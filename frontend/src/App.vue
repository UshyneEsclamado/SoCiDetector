<script setup>
import { ref, onMounted } from 'vue'
import Header from './components/Header.vue'
import DetectionPanel from './components/DetectionPanel.vue'
import VideoPlayer from './components/VideoPlayer.vue'
import Statistics from './components/Statistics.vue'
import api from './services/api'

const backendStatus = ref({ connected: false, modelLoaded: false })
const detections = ref([])
const stats = ref({ total: 0, soldiers: 0, civilians: 0 })

async function refreshStatus() {
  try {
    const health = await api.checkHealth()
    backendStatus.value = {
      connected: health?.status === 'running',
      modelLoaded: !!health?.model_loaded
    }
  } catch (e) {
    backendStatus.value = { connected: false, modelLoaded: false }
  }
}

function onFrameDetected(newDetections) {
  // Append and recompute simple stats
  const stamped = newDetections.map((d, idx) => ({ id: Date.now() + '-' + idx, ...d }))
  detections.value = [...stamped, ...detections.value].slice(0, 50)
  const total = detections.value.length
  const soldiers = detections.value.filter(d => String(d.class).toLowerCase().includes('soldier')).length
  const civilians = detections.value.filter(d => String(d.class).toLowerCase().includes('civilian')).length
  stats.value = { total, soldiers, civilians }
}

onMounted(() => {
  refreshStatus()
})
</script>

<template>
  <div class="app">
    <Header :backend-status="backendStatus" @refresh-status="refreshStatus" />
    <main class="content">
      <section class="left">
        <VideoPlayer :backend-connected="backendStatus.connected" @frame-detected="onFrameDetected" />
      </section>
      <section class="right">
        <DetectionPanel :detections="detections" />
        <Statistics :stats="stats" />
      </section>
    </main>
  </div>
  
</template>

<style scoped>
.app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}
.content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 16px;
  padding: 16px;
}
.left, .right { 
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 8px;
  padding: 12px;
}
</style>
