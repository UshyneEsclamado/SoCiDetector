from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from ultralytics import YOLO
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
MODEL_PATH = 'model/best.pt'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Global variables
model = None
detection_history = []

def load_model():
    """Load YOLO model on startup"""
    global model
    try:
        if os.path.exists(MODEL_PATH):
            model = YOLO(MODEL_PATH)
            print(f"✅ Model loaded successfully from {MODEL_PATH}")
            return True
        else:
            print(f"❌ Model file not found at {MODEL_PATH}")
            return False
    except Exception as e:
        print(f"❌ Error loading model: {str(e)}")
        return False

@app.route('/api/health', methods=['GET'])
def health_check():
    """Check if backend is running and model is loaded"""
    model_status = model is not None
    return jsonify({
        'status': 'running',
        'model_loaded': model_status,
        'timestamp': datetime.now().isoformat()
    })

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

        # Run inference
        results = model(image_np, conf=0.25)  # 25% confidence threshold
        
        # Parse detections
        detections = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                class_id = int(box.cls)
                class_name = result.names[class_id]
                confidence = float(box.conf)
                bbox = box.xyxy[0].tolist()  # [x1, y1, x2, y2]
                
                detection = {
                    'class': class_name,
                    'confidence': confidence,
                    'bbox': bbox,
                    'timestamp': datetime.now().isoformat()
                }
                detections.append(detection)
                
                # Add to history
                detection_history.append(detection)

        # Draw boxes on image
        annotated_frame = results[0].plot()
        annotated_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
        
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
    
    return jsonify({
        'success': True,
        'model_type': str(type(model).__name__),
        'classes': model.names if hasattr(model, 'names') else [],
        'model_path': MODEL_PATH
    })

# Initialize model on startup
with app.app_context():
    load_model()

if __name__ == '__main__':
    print("🚀 Starting SkyGuardian AI Backend...")
    print(f"📁 Upload folder: {os.path.abspath(UPLOAD_FOLDER)}")
    print(f"🤖 Model path: {os.path.abspath(MODEL_PATH)}")
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)