<template>
  <div class="history-panel">
    <div class="panel-header">
      <div>
        <h3>🗂 Detection Sessions</h3>
        <p class="subtitle">Review each upload with its annotated result.</p>
      </div>
      <select
        class="session-select"
        :disabled="sessions.length === 0"
        v-model="localSelected"
        @change="handleSelect"
      >
        <option value="" disabled>Select a session</option>
        <option v-for="session in sessions" :key="session.id" :value="session.id">
          {{ formatLabel(session) }}
        </option>
      </select>
    </div>

    <div v-if="sessions.length === 0" class="empty-state">
      <span>Upload an image or video to see saved results.</span>
    </div>

    <div v-else-if="selectedSession" class="preview-section">
      <div class="image-grid">
        <div class="preview-card">
          <h4>Uploaded Frame</h4>
          <img :src="selectedSession.sourceImage" alt="Uploaded frame" />
        </div>
        <div class="preview-card">
          <h4>Annotated Result</h4>
          <img :src="selectedSession.annotatedImage" alt="Annotated frame" />
        </div>
      </div>

      <div class="meta">
        <div>
          <span class="meta-label">File</span>
          <p>{{ selectedSession.fileName }}</p>
        </div>
        <div>
          <span class="meta-label">Captured</span>
          <p>{{ formatDate(selectedSession.timestamp) }}</p>
        </div>
        <div>
          <span class="meta-label">Detections</span>
          <p>{{ selectedSession.detections.length }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  sessions: {
    type: Array,
    default: () => []
  },
  selectedId: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['select-session'])
const localSelected = ref(props.selectedId || '')

watch(() => props.selectedId, (val) => {
  localSelected.value = val || ''
})

const selectedSession = computed(() => {
  return props.sessions.find(session => session.id === localSelected.value)
})

function handleSelect() {
  if (!localSelected.value) return
  emit('select-session', localSelected.value)
}

function formatLabel(session) {
  return `${session.fileName || 'Session'} • ${formatDate(session.timestamp)}`
}

function formatDate(value) {
  if (!value) return 'Unknown'
  const date = new Date(value)
  return `${date.toLocaleDateString()} ${date.toLocaleTimeString()}`
}
</script>

<style scoped>
.history-panel {
  background: var(--color-surface);
  border-radius: 18px;
  padding: 20px 22px;
  border: 1px solid var(--color-border);
  margin-bottom: 16px;
  color: var(--color-text);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.panel-header h3 {
  margin: 0;
  font-size: 1.2rem;
}

.subtitle {
  margin: 6px 0 0;
  font-size: 0.85rem;
  color: var(--color-text-muted);
}

.session-select {
  background: var(--color-surface-soft);
  border: 1px solid rgba(111, 195, 255, 0.5);
  border-radius: 10px;
  padding: 10px 14px;
  color: var(--color-text);
  min-width: 240px;
  font-family: var(--font-base);
  font-size: 0.95rem;
  box-shadow: 0 10px 25px rgba(5, 13, 30, 0.6);
}

.session-select:focus {
  outline: 2px solid var(--focus-ring);
  outline-offset: 2px;
}

.session-select option {
  background: var(--color-surface);
  color: var(--color-text);
}

.empty-state {
  margin-top: 16px;
  padding: 16px;
  border-radius: 12px;
  background: rgba(62, 213, 152, 0.08);
  text-align: center;
  color: var(--color-text-muted);
}

.preview-section {
  margin-top: 18px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
}

.preview-card {
  background: var(--color-surface-soft);
  border-radius: 14px;
  padding: 12px;
  border: 1px solid rgba(111, 195, 255, 0.25);
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.03);
}

.preview-card h4 {
  margin: 0 0 8px;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--color-text-muted);
}

.preview-card img {
  width: 100%;
  border-radius: 10px;
  border: 1px solid rgba(226, 239, 255, 0.35);
}

.meta {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 12px;
  background: var(--color-surface-soft);
  border-radius: 12px;
  padding: 12px;
}

.meta-label {
  font-size: 0.7rem;
  text-transform: uppercase;
  color: var(--color-text-muted);
  letter-spacing: 1px;
}

.meta p {
  margin: 4px 0 0;
  font-weight: 600;
  color: var(--color-text);
}
</style>
