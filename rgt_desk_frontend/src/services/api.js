import axios from 'axios';
const dynamicBaseURL = `${window.location.protocol}//${window.location.hostname}:8000`;
const apiClient = axios.create({
  baseURL: dynamicBaseURL, 
  headers: {
    'Content-Type': 'application/json'
  }
});

export default {
  getStatus() {
    return apiClient.get('/get_status');
  },
  startProcess(name, params = {}) {
    return apiClient.post('/start_process', { name, params });
  },
  stopProcess(name) {
    return apiClient.post('/stop_process', { name });
  },
  executeService(name, params = {}) {
    return apiClient.post('/execute_service', { name, params });
  },
};
