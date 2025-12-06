import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default {
  async checkHealth() {
    try {
      const response = await api.get('/health');
      return response.data;
    } catch (error) {
      console.error('Health check failed:', error);
      return { status: 'error', model_loaded: false };
    }
  },

  async detectImage(imageBase64) {
    const response = await api.post('/detect/image', {
      image: imageBase64,
    });
    return response.data;
  },

  async detectVideoFrame(frameBase64) {
    const response = await api.post('/detect/video-frame', {
      image: frameBase64,
    });
    return response.data;
  },

  async uploadVideo(videoFile) {
    const formData = new FormData();
    formData.append('video', videoFile);

    const response = await api.post('/upload-video', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async getStatistics() {
    const response = await api.get('/statistics');
    return response.data;
  },

  async clearHistory() {
    const response = await api.post('/clear-history');
    return response.data;
  },

  async getModelInfo() {
    const response = await api.get('/model-info');
    return response.data;
  },
};