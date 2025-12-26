<template>
  <div class="detection-panel">
    <div class="panel-header">
      <h3 class="panel-title">🔍 Recent Detections</h3>
      <span class="detection-count">{{ detections.length }}</span>
    </div>
    
    <div v-if="detections.length === 0" class="empty-state">
      <div class="empty-icon">📭</div>
      <p>No detections yet</p>
      <p class="empty-subtitle">Start processing to see detections</p>
    </div>
    
    <div v-else class="detection-list">
      <TransitionGroup name="detection">
        <div
          v-for="detection in detections"
          :key="detection.id"
          class="detection-item"
          :class="getDetectionClass(detection.class)"
        >
          <div class="detection-icon">
            {{ getDetectionIcon(detection.class) }}
          </div>
          
          <div class="detection-content">
            <div class="detection-header">
              <span class="detection-class">{{ detection.class }}</span>
              <span class="detection-confidence">
                {{ (detection.confidence * 100).toFixed(1) }}%
              </span>
            </div>
            
            <div class="detection-meta">
              <span class="detection-time">
                {{ formatTime(detection.timestamp) }}
              </span>
              <span 
                class="confidence-badge" 
                :class="getConfidenceBadge(detection.confidence)"
              >
                {{ getConfidenceLabel(detection.confidence) }}
              </span>
            </div>
            
            <div class="confidence-bar">
              <div 
                class="confidence-fill"
                :style="{ width: (detection.confidence * 100) + '%' }"
              ></div>
            </div>
          </div>
        </div>
      </TransitionGroup>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DetectionPanel',
  props: {
    detections: {
      type: Array,
      default: () => [],
    },
  },
  methods: {
    getDetectionClass(className) {
      const lower = className.toLowerCase();
      if (lower.includes('soldier')) return 'soldier';
      if (lower.includes('civilian')) return 'civilian';
      return 'unknown';
    },
    
    getDetectionIcon(className) {
      const lower = className.toLowerCase();
      if (lower.includes('soldier')) return '🪖';
      if (lower.includes('civilian')) return '👤';
      return '❓';
    },
    
    formatTime(timestamp) {
      if (!timestamp) return 'Just now';
      const date = new Date(timestamp);
      return date.toLocaleTimeString();
    },
    
    getConfidenceBadge(confidence) {
      if (confidence >= 0.8) return 'high';
      if (confidence >= 0.5) return 'medium';
      return 'low';
    },
    
    getConfidenceLabel(confidence) {
      if (confidence >= 0.8) return 'High';
      if (confidence >= 0.5) return 'Medium';
      return 'Low';
    },
  },
};
</script>

<style scoped>
.detection-panel {
  background: linear-gradient(135deg, rgba(16, 36, 66, 0.95), rgba(13, 29, 54, 0.92));
  border-radius: 18px;
  padding: 20px;
  border: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  max-height: 600px;
  box-shadow: 0 16px 30px rgba(3, 10, 20, 0.45);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.panel-title {
  margin: 0;
  font-size: 1.2em;
  color: var(--accent-primary);
  display: flex;
  align-items: center;
  gap: 10px;
}

.detection-count {
  background: rgba(62, 213, 152, 0.15);
  color: var(--accent-primary);
  padding: 5px 15px;
  border-radius: 999px;
  font-weight: 600;
  font-size: 0.9em;
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  text-align: center;
  color: rgba(255, 255, 255, 0.5);
}

.empty-icon {
  font-size: 4em;
  margin-bottom: 15px;
  opacity: 0.3;
}

.empty-subtitle {
  font-size: 0.9em;
  margin-top: 5px;
}

.detection-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.detection-item {
  background: rgba(21, 48, 84, 0.85);
  border-radius: 12px;
  padding: 15px;
  display: flex;
  gap: 15px;
  border-left: 4px solid;
  transition: all 0.3s ease;
  cursor: pointer;
  border: 1px solid rgba(255, 255, 255, 0.04);
}

.detection-item:hover {
  background: rgba(255, 255, 255, 0.08);
  transform: translateX(5px);
}

.detection-item.soldier {
  border-left-color: #ff7c6b;
}

.detection-item.civilian {
  border-left-color: #6fc3ff;
}

.detection-item.unknown {
  border-left-color: #b497ff;
}

.detection-icon {
  font-size: 2.5em;
  filter: drop-shadow(0 2px 5px rgba(0, 0, 0, 0.3));
}

.detection-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detection-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detection-class {
  font-weight: 700;
  font-size: 1.1em;
  text-transform: capitalize;
}

.detection-confidence {
  background: rgba(62, 213, 152, 0.18);
  color: var(--accent-primary);
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 0.9em;
  font-weight: 600;
}

.detection-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85em;
  color: rgba(255, 255, 255, 0.6);
}

.confidence-badge {
  padding: 2px 8px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 0.85em;
}

.confidence-badge.high {
  background: rgba(62, 213, 152, 0.2);
  color: var(--accent-primary);
}

.confidence-badge.medium {
  background: rgba(255, 200, 111, 0.25);
  color: #ffbd63;
}

.confidence-badge.low {
  background: rgba(255, 120, 120, 0.2);
  color: #ff8080;
}


.confidence-bar {
  height: 4px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 2px;
  overflow: hidden;
  margin-top: 5px;
}

.confidence-fill {
  height: 100%;
  background: linear-gradient(90deg, #3ed598 0%, #6fc3ff 100%);
  border-radius: 2px;
  transition: width 0.5s ease;
}

/* Transition animations */
.detection-enter-active {
  animation: slideIn 0.4s ease-out;
}

.detection-leave-active {
  animation: slideOut 0.3s ease-in;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes slideOut {
  from {
    opacity: 1;
    transform: translateX(0);
  }
  to {
    opacity: 0;
    transform: translateX(100px);
  }
}

/* Scrollbar */
.detection-list::-webkit-scrollbar {
  width: 6px;
}

.detection-list::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 3px;
}

.detection-list::-webkit-scrollbar-thumb {
  background: rgba(76, 175, 80, 0.5);
  border-radius: 3px;
}

.detection-list::-webkit-scrollbar-thumb:hover {
  background: rgba(76, 175, 80, 0.7);
}
</style>