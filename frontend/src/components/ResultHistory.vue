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
        <div
          class="preview-card"
          role="button"
          tabindex="0"
          title="Click to view larger preview"
          @click="openModal"
          @keydown.enter.prevent="openModal"
          @keydown.space.prevent="openModal"
        >
          <h4>Uploaded Frame</h4>
          <img :src="selectedSession.sourceImage" alt="Uploaded frame" />
        </div>
        <div
          class="preview-card"
          role="button"
          tabindex="0"
          title="Click to view larger preview"
          @click="openModal"
          @keydown.enter.prevent="openModal"
          @keydown.space.prevent="openModal"
        >
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

    <div
      v-if="isModalOpen && selectedSession"
      class="modal-overlay"
      @click.self="closeModal"
    >
      <div class="modal-window" tabindex="-1">
        <button class="modal-close" type="button" aria-label="Close enlarged preview" @click="closeModal">
          ×
        </button>
        <div class="modal-header">
          <div>
            <h4>{{ selectedSession.fileName }}</h4>
            <p>{{ formatDate(selectedSession.timestamp) }}</p>
          </div>
          <span class="modal-badge">{{ selectedSession.detections.length }} detections</span>
        </div>
        <div class="modal-image-grid">
          <div class="modal-card">
            <h5>Uploaded Frame</h5>
            <img :src="selectedSession.sourceImage" alt="Uploaded frame enlarged" />
          </div>
          <div class="modal-card">
            <h5>Annotated Result</h5>
            <img :src="selectedSession.annotatedImage" alt="Annotated frame enlarged" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch, onBeforeUnmount } from 'vue'

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
const isModalOpen = ref(false)

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

function openModal() {
  if (!selectedSession.value) return
  isModalOpen.value = true
}

function closeModal() {
  isModalOpen.value = false
}

function formatLabel(session) {
  return `${session.fileName || 'Session'} • ${formatDate(session.timestamp)}`
}

function formatDate(value) {
  if (!value) return 'Unknown'
  const date = new Date(value)
  return `${date.toLocaleDateString()} ${date.toLocaleTimeString()}`
}

watch(isModalOpen, (val) => {
  document.body.style.overflow = val ? 'hidden' : ''
})

onBeforeUnmount(() => {
  document.body.style.overflow = ''
})
</script>

<style scoped>
.history-panel {
  background: linear-gradient(135deg, rgba(19, 38, 69, 0.96), rgba(31, 59, 104, 0.95));
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
  background: rgba(11, 40, 74, 0.85);
  border: 1px solid rgba(190, 227, 255, 0.7);
  border-radius: 12px;
  padding: 11px 16px;
  color: #f7fbff;
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
  background: #152c4c;
  color: #f7fbff;
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
  background: rgba(17, 45, 84, 0.85);
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
  border: 1px solid rgba(247, 250, 255, 0.5);
}

.meta {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 12px;
  background: rgba(17, 37, 66, 0.9);
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

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(2, 8, 18, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(6px);
  z-index: 1000;
  padding: 24px;
}

.modal-window {
  position: relative;
  width: min(1100px, 100%);
  background: linear-gradient(145deg, rgba(15, 40, 74, 0.98), rgba(9, 24, 45, 0.98));
  border-radius: 20px;
  border: 1px solid rgba(111, 195, 255, 0.25);
  padding: 28px;
  box-shadow: 0 35px 80px rgba(0, 0, 0, 0.55);
}

.modal-close {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.08);
  color: #f7fbff;
  font-size: 1.6rem;
  cursor: pointer;
  line-height: 1;
}

.modal-close:hover {
  background: rgba(255, 255, 255, 0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 22px;
}

.modal-header h4 {
  margin: 0;
  font-size: 1.3rem;
}

.modal-header p {
  margin: 4px 0 0;
  color: var(--color-text-muted);
}

.modal-badge {
  background: rgba(62, 213, 152, 0.15);
  color: var(--accent-primary);
  padding: 6px 14px;
  border-radius: 999px;
  font-weight: 600;
}

.modal-image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 18px;
}

.modal-card {
  background: rgba(10, 26, 48, 0.7);
  border-radius: 16px;
  padding: 16px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.modal-card h5 {
  margin: 0 0 10px;
  font-size: 1rem;
  color: var(--color-text-muted);
}

.modal-card img {
  width: 100%;
  max-height: 70vh;
  object-fit: contain;
  border-radius: 12px;
  border: 1px solid rgba(247, 250, 255, 0.4);
}
</style>
