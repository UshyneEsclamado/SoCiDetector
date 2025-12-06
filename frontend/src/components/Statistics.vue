<template>
  <div class="statistics-panel">
    <h3 class="panel-title">📊 Detection Statistics</h3>
    
    <div class="stats-grid">
      <div class="stat-card total">
        <div class="stat-icon">🎯</div>
        <div class="stat-content">
          <div class="stat-label">Total Detections</div>
          <div class="stat-value">{{ stats.total }}</div>
        </div>
      </div>
      
      <div class="stat-card soldier">
        <div class="stat-icon">🪖</div>
        <div class="stat-content">
          <div class="stat-label">Soldiers</div>
          <div class="stat-value">{{ stats.soldiers }}</div>
          <div class="stat-percentage">{{ soldierPercentage }}%</div>
        </div>
      </div>
      
      <div class="stat-card civilian">
        <div class="stat-icon">👤</div>
        <div class="stat-content">
          <div class="stat-label">Civilians</div>
          <div class="stat-value">{{ stats.civilians }}</div>
          <div class="stat-percentage">{{ civilianPercentage }}%</div>
        </div>
      </div>
    </div>
    
    <div class="progress-bars">
      <div class="progress-item">
        <div class="progress-header">
          <span>Soldiers</span>
          <span>{{ stats.soldiers }}</span>
        </div>
        <div class="progress-bar">
          <div 
            class="progress-fill soldier-fill" 
            :style="{ width: soldierPercentage + '%' }"
          ></div>
        </div>
      </div>
      
      <div class="progress-item">
        <div class="progress-header">
          <span>Civilians</span>
          <span>{{ stats.civilians }}</span>
        </div>
        <div class="progress-bar">
          <div 
            class="progress-fill civilian-fill" 
            :style="{ width: civilianPercentage + '%' }"
          ></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Statistics',
  props: {
    stats: {
      type: Object,
      required: true,
      default: () => ({ total: 0, soldiers: 0, civilians: 0 }),
    },
  },
  computed: {
    soldierPercentage() {
      if (this.stats.total === 0) return 0;
      return ((this.stats.soldiers / this.stats.total) * 100).toFixed(1);
    },
    civilianPercentage() {
      if (this.stats.total === 0) return 0;
      return ((this.stats.civilians / this.stats.total) * 100).toFixed(1);
    },
  },
};
</script>

<style scoped>
.statistics-panel {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 12px;
  padding: 20px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.panel-title {
  margin: 0 0 20px;
  font-size: 1.3em;
  color: #4CAF50;
  display: flex;
  align-items: center;
  gap: 10px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
  margin-bottom: 25px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  padding: 15px;
  display: flex;
  align-items: center;
  gap: 15px;
  border: 2px solid transparent;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.3);
}

.stat-card.total {
  border-color: rgba(76, 175, 80, 0.3);
  background: linear-gradient(135deg, rgba(76, 175, 80, 0.1) 0%, rgba(76, 175, 80, 0.05) 100%);
}

.stat-card.soldier {
  border-color: rgba(244, 67, 54, 0.3);
  background: linear-gradient(135deg, rgba(244, 67, 54, 0.1) 0%, rgba(244, 67, 54, 0.05) 100%);
}

.stat-card.civilian {
  border-color: rgba(33, 150, 243, 0.3);
  background: linear-gradient(135deg, rgba(33, 150, 243, 0.1) 0%, rgba(33, 150, 243, 0.05) 100%);
}

.stat-icon {
  font-size: 2.5em;
  filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.3));
}

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 0.85em;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 5px;
}

.stat-value {
  font-size: 2em;
  font-weight: 700;
  line-height: 1;
}

.stat-percentage {
  font-size: 0.9em;
  color: rgba(255, 255, 255, 0.6);
  margin-top: 5px;
}

.progress-bars {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.progress-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  font-size: 0.9em;
  color: rgba(255, 255, 255, 0.8);
}

.progress-bar {
  height: 20px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 10px;
  overflow: hidden;
  position: relative;
}

.progress-fill {
  height: 100%;
  transition: width 0.5s ease;
  border-radius: 10px;
  position: relative;
  overflow: hidden;
}

.soldier-fill {
  background: linear-gradient(90deg, #f44336 0%, #ff5252 100%);
  box-shadow: 0 0 10px rgba(244, 67, 54, 0.5);
}

.civilian-fill {
  background: linear-gradient(90deg, #2196F3 0%, #42A5F5 100%);
  box-shadow: 0 0 10px rgba(33, 150, 243, 0.5);
}

.progress-fill::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.3),
    transparent
  );
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>