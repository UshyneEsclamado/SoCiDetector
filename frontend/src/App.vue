<script setup>
import { ref, onMounted } from 'vue'
import Header from './components/Header.vue'
import DetectionPanel from './components/DetectionPanel.vue'
import VideoPlayer from './components/VideoPlayer.vue'
import Statistics from './components/Statistics.vue'
import ResultHistory from './components/ResultHistory.vue'
import api from './services/api'

const backendStatus = ref({ connected: false, modelLoaded: false })
const detections = ref([])
const stats = ref({ total: 0, soldiers: 0, civilians: 0 })
const sessionHistory = ref([])
const selectedSessionId = ref('')

const MAX_HISTORY = 20
const MAX_DETECTIONS_PER_SESSION = 400

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

function onFrameDetected(payload) {
  if (!payload) return
  const normalizedDetections = (payload.detections || []).map((d, idx) => ({
    id: `${payload.sessionId}-${payload.frameNumber ?? 0}-${Date.now()}-${idx}`,
    frameNumber: payload.frameNumber ?? 0,
    ...d
  }))

  const existingIndex = sessionHistory.value.findIndex(s => s.id === payload.sessionId)
  let nextSession
  if (existingIndex !== -1) {
    const existing = { ...sessionHistory.value[existingIndex] }
    existing.detections = [...normalizedDetections, ...existing.detections].slice(0, MAX_DETECTIONS_PER_SESSION)
    existing.annotatedImage = payload.annotatedImage
    existing.sourceImage = payload.sourceImage
    existing.timestamp = payload.timestamp
    existing.lastFrame = payload.frameNumber ?? existing.lastFrame
    existing.totalFrames = payload.totalFrames ?? existing.totalFrames
    nextSession = existing
    sessionHistory.value.splice(existingIndex, 1)
  } else {
    nextSession = {
      id: payload.sessionId,
      fileName: payload.fileName,
      timestamp: payload.timestamp,
      sourceImage: payload.sourceImage,
      annotatedImage: payload.annotatedImage,
      detections: normalizedDetections,
      lastFrame: payload.frameNumber ?? 0,
      totalFrames: payload.totalFrames ?? 0
    }
  }
  sessionHistory.value = [nextSession, ...sessionHistory.value].slice(0, MAX_HISTORY)

  const shouldAutoSelect = !selectedSessionId.value || selectedSessionId.value === nextSession.id
  if (shouldAutoSelect) {
    selectSession(nextSession.id, nextSession)
  }
}

function selectSession(sessionId, seededSession) {
  if (!sessionId) {
    selectedSessionId.value = ''
    applyDetections([])
    return
  }
  selectedSessionId.value = sessionId
  const session = seededSession || sessionHistory.value.find(s => s.id === sessionId)
  applyDetections(session ? session.detections : [])
}

function applyDetections(list) {
  detections.value = list
  const total = list.length
  const soldiers = list.filter(d => String(d.class).toLowerCase().includes('soldier')).length
  const civilians = list.filter(d => String(d.class).toLowerCase().includes('civilian')).length
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
        <ResultHistory
          :sessions="sessionHistory"
          :selected-id="selectedSessionId"
          @select-session="selectSession"
        />
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
  background: linear-gradient(145deg, rgba(7, 24, 46, 0.85), rgba(2, 8, 16, 0.95));
}
.content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 16px;
  padding: 16px;
}
.left, .right { 
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 16px;
  padding: 18px;
  box-shadow: 0 20px 40px rgba(3, 10, 20, 0.55);
}
</style>
