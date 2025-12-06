<template>
  <header class="app-header">
    <div class="header-content">
      <div class="logo-section">
        <div class="logo-icon">🛡️</div>
        <div class="title-section">
          <h1>SkyGuardian AI</h1>
          <p class="subtitle">Aerial Threat Detection & Classification System</p>
        </div>
      </div>
      
      <div class="status-section">
        <div 
          class="status-indicator" 
          :class="statusClass"
          @click="$emit('refresh-status')"
          title="Click to refresh"
        >
          <span class="status-dot"></span>
          <span class="status-text">{{ statusText }}</span>
        </div>
        
        <button 
          v-if="backendStatus.connected && backendStatus.modelLoaded"
          class="info-button"
          @click="showInfo = !showInfo"
        >
          ℹ️ Info
        </button>
      </div>
    </div>
    
    <!-- Info Modal -->
    <div v-if="showInfo" class="info-modal" @click="showInfo = false">
      <div class="info-content" @click.stop>
        <h3>System Information</h3>
        <div class="info-item">
          <strong>Status:</strong> {{ backendStatus.connected ? 'Online' : 'Offline' }}
        </div>
        <div class="info-item">
          <strong>Model:</strong> {{ backendStatus.modelLoaded ? 'Loaded' : 'Not Loaded' }}
        </div>
        <div class="info-item">
          <strong>Version:</strong> 1.0.0
        </div>
        <div class="info-item">
          <strong>Framework:</strong> YOLOv8 + Vue.js
        </div>
        <button class="close-btn" @click="showInfo = false">Close</button>
      </div>
    </div>
  </header>
</template>

<script>
export default {
  name: 'AppHeader',
  props: {
    backendStatus: {
      type: Object,
      required: true,
      default: () => ({ connected: false, modelLoaded: false }),
    },
  },
  data() {
    return {
      showInfo: false,
    };
  },
  computed: {
    statusClass() {
      if (!this.backendStatus.connected) return 'status-error';
      if (!this.backendStatus.modelLoaded) return 'status-warning';
      return 'status-success';
    },
    statusText() {
      if (!this.backendStatus.connected) return 'Backend Disconnected';
      if (!this.backendStatus.modelLoaded) return 'Model Not Loaded';
      return 'System Online';
    },
  },
};
</script>

<style scoped>
.app-header {
  background: rgba(0, 0, 0, 0.5);
  padding: 20px 30px;
  border-bottom: 2px solid rgba(76, 175, 80, 0.3);
  backdrop-filter: blur(10px);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1920px;
  margin: 0 auto;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 15px;
}

.logo-icon {
  font-size: 3em;
  filter: drop-shadow(0 0 10px rgba(76, 175, 80, 0.5));
}

.title-section h1 {
  font-size: 2em;
  font-weight: 700;
  margin: 0;
  background: linear-gradient(135deg, #4CAF50 0%, #81C784 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9em;
  margin: 5px 0 0;
}

.status-section {
  display: flex;
  align-items: center;
  gap: 15px;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 20px;
  border-radius: 25px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.status-indicator:hover {
  transform: scale(1.05);
  border-color: currentColor;
}

.status-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.status-success {
  background: rgba(76, 175, 80, 0.2);
  color: #4CAF50;
}

.status-success .status-dot {
  background: #4CAF50;
  box-shadow: 0 0 10px #4CAF50;
}

.status-warning {
  background: rgba(255, 152, 0, 0.2);
  color: #FF9800;
}

.status-warning .status-dot {
  background: #FF9800;
  box-shadow: 0 0 10px #FF9800;
}

.status-error {
  background: rgba(244, 67, 54, 0.2);
  color: #f44336;
}

.status-error .status-dot {
  background: #f44336;
  box-shadow: 0 0 10px #f44336;
}

.info-button {
  background: rgba(33, 150, 243, 0.2);
  border: 2px solid #2196F3;
  color: #2196F3;
  padding: 10px 20px;
  border-radius: 25px;
  cursor: pointer;
  font-size: 0.9em;
  font-weight: 600;
  transition: all 0.3s ease;
}

.info-button:hover {
  background: rgba(33, 150, 243, 0.3);
  transform: scale(1.05);
}

.info-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(5px);
}

.info-content {
  background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
  padding: 30px;
  border-radius: 15px;
  max-width: 500px;
  border: 2px solid rgba(76, 175, 80, 0.3);
}

.info-content h3 {
  margin-bottom: 20px;
  color: #4CAF50;
  font-size: 1.5em;
}

.info-item {
  padding: 10px;
  margin: 10px 0;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 8px;
  border-left: 3px solid #4CAF50;
}

.close-btn {
  margin-top: 20px;
  width: 100%;
  padding: 12px;
  background: #4CAF50;
  border: none;
  border-radius: 8px;
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: #45a049;
  transform: translateY(-2px);
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 15px;
  }
  
  .title-section h1 {
    font-size: 1.5em;
  }
  
  .subtitle {
    font-size: 0.8em;
  }
}
</style>