<template>
  <div class="video-player">
    <div class="video-container">
      <canvas ref="canvas" class="video-canvas"></canvas>
      
      <div v-if="!videoLoaded" class="placeholder">
        <div class="placeholder-icon">🎥</div>
        <p>Upload a video or image to begin detection</p>
      </div>
      
      <div v-if="isProcessing" class="processing-overlay">
        <div class="spinner"></div>
        <p>Processing... {{ fps.toFixed(1) }} FPS</p>
      </div>
    </div>
    
    <div class="controls">
      <div class="control-group">
        <input 
          type="file" 
          ref="videoInput" 
          accept="video/*,image/*" 
          @change="handleFileUpload"
          style="display: none"
        >
        <button 
          class="btn btn-primary" 
          @click="$refs.videoInput.click()"
          :disabled="isProcessing"
        >
          📁 Upload Video/Image
        </button>
        
        <button 
          v-if="videoLoaded && !isProcessing" 
          class="btn btn-success" 
          @click="startDetection"
          :disabled="!backendConnected"
        >
          ▶️ Start Detection
        </button>
        
        <button 
          v-if="isProcessing" 
          class="btn btn-danger" 
          @click="stopDetection"
        >
          ⏸️ Stop
        </button>
        
        <button 
          class="btn btn-secondary" 
          @click="captureFrame"
          :disabled="!videoLoaded"
        >
          📸 Capture Frame
        </button>
      </div>
      
      <div v-if="videoInfo" class="video-info">
        <span>{{ videoInfo.width }}x{{ videoInfo.height }}</span>
        <span v-if="videoInfo.duration">{{ videoInfo.duration.toFixed(1) }}s</span>
        <span>{{ currentFrame }} / {{ totalFrames }} frames</span>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../services/api';

export default {
  name: 'VideoPlayer',
  props: {
    backendConnected: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      video: null,
      canvas: null,
      ctx: null,
      videoLoaded: false,
      isProcessing: false,
      videoInfo: null,
      currentFrame: 0,
      totalFrames: 0,
      fps: 0,
      lastFrameTime: 0,
      isImage: false,
      currentSessionId: null,
      currentFileName: '',
      lastSourceFrame: null,
      targetFps: 3,
      detectionIntervalMs: 333,
      lastDetectionTimestamp: 0,
      estimatedVideoFps: 30,
    };
  },
  mounted() {
    this.canvas = this.$refs.canvas;
    this.ctx = this.canvas.getContext('2d');
    this.video = document.createElement('video');
    this.video.muted = true;
    this.video.addEventListener('ended', this.handleVideoEnded);
  },
  beforeUnmount() {
    if (this.video) {
      this.video.removeEventListener('ended', this.handleVideoEnded);
    }
  },
  methods: {
    handleFileUpload(event) {
      const file = event.target.files[0];
      if (!file) return;

      const fileType = file.type;
      this.isImage = fileType.startsWith('image/');
      this.currentSessionId = this.generateSessionId();
      this.currentFileName = file.name || (this.isImage ? 'Image Upload' : 'Video Upload');
      this.currentFrame = 0;
      this.totalFrames = this.isImage ? 1 : 0;
      this.lastDetectionTimestamp = 0;

      const url = URL.createObjectURL(file);

      if (this.isImage) {
        const img = new Image();
        img.onload = () => {
          this.canvas.width = img.width;
          this.canvas.height = img.height;
          this.ctx.drawImage(img, 0, 0);
          
          this.videoLoaded = true;
          this.videoInfo = {
            width: img.width,
            height: img.height,
          };
          this.lastSourceFrame = this.canvas.toDataURL('image/jpeg', 0.85);
          
          URL.revokeObjectURL(url);
        };
        img.src = url;
      } else {
        this.stopDetection();
        this.video.pause();
        this.video.src = url;
        this.video.load();
        this.video.onloadedmetadata = () => {
          this.canvas.width = this.video.videoWidth || this.canvas.width;
          this.canvas.height = this.video.videoHeight || this.canvas.height;
          this.ctx.drawImage(this.video, 0, 0);

          this.videoLoaded = true;
          const fallbackFps = 30;
          this.estimatedVideoFps = fallbackFps;
          this.totalFrames = Math.max(1, Math.floor(this.video.duration * this.estimatedVideoFps));
          this.videoInfo = {
            width: this.video.videoWidth,
            height: this.video.videoHeight,
            duration: this.video.duration,
          };
          this.lastSourceFrame = this.canvas.toDataURL('image/jpeg', 0.85);
        };
      }
    },
    
    async startDetection() {
      if (!this.backendConnected) {
        alert('Backend is not connected. Please start the Python server.');
        return;
      }

      this.isProcessing = true;
      this.lastFrameTime = performance.now();
      this.lastDetectionTimestamp = 0;

      if (this.isImage) {
        await this.processFrame();
        this.currentFrame = 1;
        this.isProcessing = false;
      } else {
        this.currentFrame = 0;
        this.video.currentTime = 0;
        this.video.play();
        requestAnimationFrame(() => this.processVideoFrames());
      }
    },
    
    stopDetection(resetPosition = false) {
      this.isProcessing = false;
      if (this.video) {
        this.video.pause();
        if (resetPosition) {
          this.video.currentTime = 0;
        }
      }
    },
    
    async processVideoFrames() {
      if (!this.isProcessing || !this.video) return;
      if (this.video.ended) {
        this.finishVideoProcessing();
        return;
      }

      const now = performance.now();
      if (now - this.lastDetectionTimestamp < this.detectionIntervalMs) {
        requestAnimationFrame(() => this.processVideoFrames());
        return;
      }
      this.lastDetectionTimestamp = now;

      await this.processFrame();
      
      // Calculate FPS
      const elapsed = now - this.lastFrameTime;
      if (elapsed > 0) {
        this.fps = 1000 / elapsed;
      }
      this.lastFrameTime = performance.now();

      this.currentFrame = Math.min(
        this.totalFrames || 0,
        Math.max(1, Math.floor(this.video.currentTime * this.estimatedVideoFps))
      );

      if (this.video.ended) {
        this.finishVideoProcessing();
        return;
      }

      if (this.isProcessing) {
        requestAnimationFrame(() => this.processVideoFrames());
      }
    },
    
    async processFrame() {
      try {
        // Draw current frame
        if (!this.isImage) {
          this.ctx.drawImage(this.video, 0, 0, this.canvas.width, this.canvas.height);
        }
        
        // Get frame as base64
        const frameData = this.canvas.toDataURL('image/jpeg', 0.8);
        this.lastSourceFrame = frameData;
        
        // Send to backend
        const result = await api.detectImage(frameData);
        
        if (result.success) {
          // Draw annotated frame
          const img = new Image();
          img.onload = () => {
            this.ctx.drawImage(img, 0, 0, this.canvas.width, this.canvas.height);
          };
          img.src = result.annotated_image;
          
          this.emitSessionPayload(result, frameData);
        }
      } catch (error) {
        console.error('Detection error:', error);
        this.stopDetection();
        alert('Detection failed. Please check if the backend is running.');
      }
    },
    handleVideoEnded() {
      if (!this.isProcessing) return;
      this.finishVideoProcessing();
    },
    finishVideoProcessing() {
      this.stopDetection();
      this.currentFrame = this.totalFrames;
    },
    generateSessionId() {
      if (typeof crypto !== 'undefined' && crypto.randomUUID) {
        return crypto.randomUUID();
      }
      return `session-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
    },
    emitSessionPayload(result, frameData) {
      const payload = {
        sessionId: this.currentSessionId || this.generateSessionId(),
        fileName: this.currentFileName || (this.isImage ? 'Image Upload' : 'Video Frame'),
        timestamp: new Date().toISOString(),
        sourceImage: frameData || this.lastSourceFrame,
        annotatedImage: result.annotated_image,
        detections: result.detections || [],
        frameNumber: this.currentFrame,
        totalFrames: this.totalFrames,
        isImage: this.isImage,
        finished: !this.isProcessing && (!!this.isImage || this.video?.ended)
      };
      this.$emit('frame-detected', payload);
    },
    
    captureFrame() {
      const link = document.createElement('a');
      link.download = `skyguardian_${Date.now()}.jpg`;
      link.href = this.canvas.toDataURL('image/jpeg');
      link.click();
    },
  },
};
</script>

<style scoped>
.video-player {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 20px;
}

.video-container {
  flex: 1;
  position: relative;
  background: #000;
  border-radius: 12px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

.video-canvas {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  border-radius: 8px;
}

.placeholder {
  text-align: center;
  color: rgba(255, 255, 255, 0.5);
}

.placeholder-icon {
  font-size: 5em;
  margin-bottom: 20px;
  opacity: 0.3;
}

.processing-overlay {
  position: absolute;
  top: 20px;
  right: 20px;
  background: rgba(76, 175, 80, 0.9);
  padding: 15px 25px;
  border-radius: 25px;
  display: flex;
  align-items: center;
  gap: 15px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
}

.spinner {
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.controls {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.control-group {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 1em;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.btn-success {
  background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
  color: white;
}

.btn-success:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(76, 175, 80, 0.4);
}

.btn-danger {
  background: linear-gradient(135deg, #f44336 0%, #da190b 100%);
  color: white;
}

.btn-danger:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(244, 67, 54, 0.4);
}

.btn-secondary {
  background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(33, 150, 243, 0.4);
}

.video-info {
  display: flex;
  gap: 20px;
  padding: 10px 15px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 8px;
  font-size: 0.9em;
  color: rgba(255, 255, 255, 0.7);
}

.video-info span {
  display: flex;
  align-items: center;
}

@media (max-width: 768px) {
  .control-group {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
    justify-content: center;
  }
}
</style>