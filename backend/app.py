from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from ultralytics import YOLO
import torch
import sys
import pathlib
from pathlib import Path
import subprocess
import cv2
import numpy as np
import base64
from io import BytesIO
from PIL import Image
import os
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for Vue.js frontend

# Configuration
UPLOAD_FOLDER = 'uploads'
MODEL_PATH = os.environ.get('MODEL_PATH', 'model/best.pt')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Global variables
model = None
model_type = None  # 'v8' or 'v5' or 'v5_local'
last_model_error = None
v5_ctx = {}

def ensure_yolov5_repo():
    repo_dir = Path(__file__).parent / 'yolov5'
    if not repo_dir.exists():
        try:
            print('⬇️  Cloning YOLOv5 repository...')
            subprocess.check_call(['git', 'clone', '--depth', '1', 'https://github.com/ultralytics/yolov5', str(repo_dir)])
        except Exception as e:
            print(f'❌ Failed to clone YOLOv5 repo: {e}')
            return None
    sys.path.insert(0, str(repo_dir))
    return repo_dir
detection_history = []

def load_model():
    """Load YOLO model on startup"""
    global model, model_type, last_model_error
    try:
        if os.path.exists(MODEL_PATH):
            try:
                model = YOLO(MODEL_PATH)
                model_type = 'v8'
                print(f"✅ YOLOv8 model loaded from {MODEL_PATH}")
                last_model_error = None
                return True
            except Exception as e_v8:
                print(f"⚠️ YOLOv8 load failed: {str(e_v8)}. Trying YOLOv5 loader...")
                try:
                    # Fix for loading Linux-trained checkpoints on Windows
                    try:
                        pathlib.PosixPath = pathlib.WindowsPath  # type: ignore
                    except Exception:
                        pass
                    model = torch.hub.load('ultralytics/yolov5', 'custom', path=MODEL_PATH, trust_repo=True, force_reload=True)
                    model_type = 'v5'
                    print(f"✅ YOLOv5 model loaded from hub: {MODEL_PATH}")
                    last_model_error = None
                    return True
                except Exception as e_v5:
                    print(f"⚠️ Hub YOLOv5 load failed: {str(e_v5)}. Trying local YOLOv5 repo...")
                    repo = ensure_yolov5_repo()
                    if repo is None:
                        last_model_error = f"Failed to prepare YOLOv5 repo; original errors: v8={e_v8}; hub={e_v5}"
                        return False
                    try:
                        try:
                            pathlib.PosixPath = pathlib.WindowsPath  # type: ignore
                        except Exception:
                            pass
                        from models.common import DetectMultiBackend  # type: ignore
                        from utils.torch_utils import select_device  # type: ignore
                        device = select_device('cpu')
                        local_model = DetectMultiBackend(MODEL_PATH, device=device, dnn=False, data=None, fp16=False)
                        v5_ctx['model'] = local_model
                        v5_ctx['device'] = device
                        v5_ctx['stride'] = getattr(local_model, 'stride', 32)
                        v5_ctx['names'] = local_model.names
                        model = local_model
                        model_type = 'v5_local'
                        print(f"✅ YOLOv5 model loaded from local repo: {MODEL_PATH}")
                        last_model_error = None
                        return True
                    except Exception as e_local:
                        print(f"❌ Error loading YOLOv5 local repo model: {e_local}")
                        last_model_error = f"YOLOv8 error: {e_v8}; YOLOv5 hub error: {e_v5}; YOLOv5 local error: {e_local}"
                        return False
        else:
            print(f"❌ Model file not found at {MODEL_PATH}")
            last_model_error = f"Model file not found at {MODEL_PATH}"
            return False
    except Exception as e:
        print(f"❌ Error loading model: {str(e)}")
        last_model_error = str(e)
        return False

@app.route('/api/health', methods=['GET'])
def health_check():
    """Check if backend is running and model is loaded"""
    model_status = model is not None
    return jsonify({
        'status': 'running',
        'model_loaded': model_status,
        'timestamp': datetime.now().isoformat(),
        'model_backend': model_type,
        'model_path': MODEL_PATH,
        'error': None if model_status else last_model_error
    })

@app.route('/api/reload-model', methods=['POST'])
def reload_model_endpoint():
    """Reload model, optionally with a new path.
    Body: { "model_path": "c:/path/to/best.pt" }
    """
    global MODEL_PATH
    try:
        data = request.get_json(silent=True) or {}
        new_path = data.get('model_path')
        if new_path:
            MODEL_PATH = new_path
        ok = load_model()
        return jsonify({
            'success': ok,
            'model_loaded': model is not None,
            'model_backend': model_type,
            'model_path': MODEL_PATH,
            'error': None if model is not None else last_model_error
        }), (200 if ok else 500)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/detect/image', methods=['POST'])
def detect_image():
    """Detect objects in a single image"""
    try:
        if model is None:
            return jsonify({
                'success': False, 
                'error': 'Model not loaded'
            }), 500

        # Get image from request
        data = request.json
        image_data = data.get('image')
        
        if not image_data:
            return jsonify({
                'success': False,
                'error': 'No image data provided'
            }), 400

        # Decode base64 image
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        image = Image.open(BytesIO(image_bytes))
        image_np = np.array(image)
        image_np = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)

        detections = []

        if model_type == 'v8':
            # Run inference (YOLOv8)
            results = model(image_np, conf=0.25)
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    class_id = int(box.cls)
                    class_name = result.names[class_id]
                    confidence = float(box.conf)
                    bbox = box.xyxy[0].tolist()

                    detection = {
                        'class': class_name,
                        'confidence': confidence,
                        'bbox': bbox,
                        'timestamp': datetime.now().isoformat()
                    }
                    detections.append(detection)
                    detection_history.append(detection)

            annotated_frame = results[0].plot()
            annotated_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
        else:
            # Run inference (YOLOv5 via torch.hub)
            # Set confidence if supported
            try:
                model.conf = 0.25
            except Exception:
                pass
            if model_type == 'v5_local':
                # Minimal YOLOv5 local inference
                try:
                    from utils.augmentations import letterbox  # type: ignore
                    from utils.general import non_max_suppression, scale_boxes  # type: ignore
                    import torch as _torch
                    stride = int(v5_ctx.get('stride', 32))
                    img = letterbox(image_np, new_shape=640, stride=stride, auto=True)[0]
                    img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, HWC to CHW
                    img = _torch.from_numpy(img).to(v5_ctx['device'])
                    img = img.float()
                    img /= 255.0
                    if img.ndimension() == 3:
                        img = img.unsqueeze(0)
                    pred = v5_ctx['model'](img, augment=False, visualize=False)
                    pred = non_max_suppression(pred, 0.25, 0.45, None, False, max_det=1000)
                    names = v5_ctx['names']
                    for det in pred:
                        if len(det):
                            det[:, :4] = scale_boxes(img.shape[2:], det[:, :4], image_np.shape).round()
                            for *xyxy, conf, cls in det:
                                x1, y1, x2, y2 = [float(x) for x in xyxy]
                                cls_id = int(cls.item()) if hasattr(cls, 'item') else int(cls)
                                class_name = names[cls_id] if isinstance(names, list) else names.get(cls_id, str(cls_id))
                                detection = {
                                    'class': class_name,
                                    'confidence': float(conf.item()) if hasattr(conf, 'item') else float(conf),
                                    'bbox': [x1, y1, x2, y2],
                                    'timestamp': datetime.now().isoformat()
                                }
                                detections.append(detection)
                                detection_history.append(detection)

                    # For annotation, draw simple boxes
                    annotated_frame = image_np.copy()
                    for det in detections:
                        x1, y1, x2, y2 = map(int, det['bbox'])
                        cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(annotated_frame, f"{det['class']} {det['confidence']:.2f}", (x1, max(y1-5, 0)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
                    annotated_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
                except Exception as e_inf:
                    print(f"❌ YOLOv5 local inference error: {e_inf}")
                    annotated_frame = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
            else:
                # Hub model path
                res = model(image_np)
            # Parse detections from tensors
            if hasattr(res, 'xyxy') and len(res.xyxy) > 0:
                det_tensor = res.xyxy[0].cpu().numpy()
                names = model.names if hasattr(model, 'names') else {}
                for row in det_tensor:
                    x1, y1, x2, y2, conf, cls_id = row[:6]
                    cls_id = int(cls_id)
                    class_name = names.get(cls_id, str(cls_id)) if isinstance(names, dict) else names[cls_id]
                    detection = {
                        'class': class_name,
                        'confidence': float(conf),
                        'bbox': [float(x1), float(y1), float(x2), float(y2)],
                        'timestamp': datetime.now().isoformat()
                    }
                    detections.append(detection)
                    detection_history.append(detection)

            # Render annotated frame
            if model_type != 'v5_local':
                try:
                    res.render()
                    annotated_frame = res.imgs[0]
                    annotated_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
                except Exception:
                    annotated_frame = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
        
        # Convert back to base64
        pil_img = Image.fromarray(annotated_frame)
        buffered = BytesIO()
        pil_img.save(buffered, format="JPEG", quality=85)
        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

        return jsonify({
            'success': True,
            'detections': detections,
            'count': len(detections),
            'annotated_image': f'data:image/jpeg;base64,{img_base64}'
        })

    except Exception as e:
        print(f"Error in detect_image: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/detect/video-frame', methods=['POST'])
def detect_video_frame():
    """Detect objects in video frame (same as image detection)"""
    return detect_image()

@app.route('/api/upload-video', methods=['POST'])
def upload_video():
    """Upload video file for processing"""
    try:
        if 'video' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No video file provided'
            }), 400

        video_file = request.files['video']
        if video_file.filename == '':
            return jsonify({
                'success': False,
                'error': 'Empty filename'
            }), 400

        # Save video file
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{video_file.filename}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        video_file.save(filepath)

        # Get video info
        cap = cv2.VideoCapture(filepath)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = frame_count / fps if fps > 0 else 0
        cap.release()

        return jsonify({
            'success': True,
            'filename': filename,
            'filepath': filepath,
            'info': {
                'fps': fps,
                'frame_count': frame_count,
                'width': width,
                'height': height,
                'duration': duration
            }
        })

    except Exception as e:
        print(f"Error in upload_video: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get detection statistics"""
    soldier_count = sum(1 for d in detection_history if 'soldier' in d['class'].lower())
    civilian_count = sum(1 for d in detection_history if 'civilian' in d['class'].lower())
    
    return jsonify({
        'total': len(detection_history),
        'soldiers': soldier_count,
        'civilians': civilian_count,
        'recent': detection_history[-10:]  # Last 10 detections
    })

@app.route('/api/clear-history', methods=['POST'])
def clear_history():
    """Clear detection history"""
    global detection_history
    detection_history = []
    return jsonify({'success': True, 'message': 'History cleared'})

@app.route('/api/model-info', methods=['GET'])
def model_info():
    """Get model information"""
    if model is None:
        return jsonify({
            'success': False,
            'error': 'Model not loaded'
        }), 500
    
    info = {
        'success': True,
        'model_backend': model_type or 'unknown',
        'model_type': str(type(model).__name__),
        'model_path': MODEL_PATH
    }
    if hasattr(model, 'names'):
        info['classes'] = model.names
    return jsonify(info)

# Initialize model on startup
with app.app_context():
    load_model()

if __name__ == '__main__':
    print("🚀 Starting SkyGuardian AI Backend...")
    print(f"📁 Upload folder: {os.path.abspath(UPLOAD_FOLDER)}")
    print(f"🤖 Model path: {os.path.abspath(MODEL_PATH)}")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)