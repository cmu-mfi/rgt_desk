import { defineStore } from 'pinia';
import api from '../services/api';
import panelsConfig from '../config/panels.json';

// Fallback initial values per param type; an explicit `default` in panels.json wins.
const PARAM_DEFAULTS = {
  toggle: () => false,
  select: () => '',
  slider: (param) => param.min ?? 0,
  text: () => '',
};

// Store defaults and service status keys are derived from panels.json,
// so adding a panel never requires touching this file.
function buildInitialConfigs() {
  const configs = {};
  for (const tab of Object.values(panelsConfig.tabs)) {
    for (const panel of tab.panels) {
      configs[panel.id] = {};
      for (const param of panel.params ?? []) {
        configs[panel.id][param.key] =
          param.default !== undefined ? param.default : PARAM_DEFAULTS[param.type]?.(param);
      }
    }
  }
  return configs;
}

function buildInitialServiceStatus() {
  const status = {};
  for (const tab of Object.values(panelsConfig.tabs)) {
    for (const panel of tab.panels) {
      if (panel.type === 'service') {
        status[panel.id] = 'idle';
      }
    }
  }
  return status;
}

export const useStore = defineStore('store', {
  state: () => ({
    process_status: {
    },
    process_logs: {
    },
    service_status: buildInitialServiceStatus(),
    service_logs: {},
    serviceRevision: 0,
    configs: buildInitialConfigs(),
    connection: 'connecting',
    pending: {},
    feedback: {},
    fetchingStatus: false,
    fetchingLogs: false,
    pollingInterval: null
  }),
  actions: {
    async fetchStatus() {
      if (this.fetchingStatus) return;
      this.fetchingStatus = true;
      const serviceRevision = this.serviceRevision;
      try {
        const [processes, services] = await Promise.all([api.getStatus(), api.getServiceStatus()]);
        this.process_status = processes.data;
        // Ignore snapshots taken before a start/cancel request changed state.
        if (serviceRevision === this.serviceRevision) this.service_status = services.data;
        this.connection = 'connected';
      } catch (error) {
        this.connection = 'disconnected';
      } finally {
        this.fetchingStatus = false;
      }
    },

    async fetchLogs() {
      if (this.fetchingLogs) return;
      this.fetchingLogs = true;
      try {
        const [processes, services] = await Promise.all([api.getLogs(), api.getServiceLogs()]);
        this.process_logs = processes.data;
        this.service_logs = services.data;
      } catch (error) {
        console.error("Failed to fetch logs from backend:", error);
      } finally {
        this.fetchingLogs = false;
      }
    },

    startPolling() {
      if (!this.pollingInterval) {
        this.fetchStatus(); // Fetch immediately on start
        this.fetchLogs();
        this.pollingInterval = setInterval(() => {
          this.fetchStatus();
          this.fetchLogs();
        }, 1000);
      }
    },

    stopPolling() {
      if (this.pollingInterval) {
        clearInterval(this.pollingInterval);
        this.pollingInterval = null;
      }
    },

    configValid(id) {
      const panel = Object.values(panelsConfig.tabs).flatMap(tab => tab.panels).find(panel => panel.id === id);
      return (panel?.params ?? []).every(param => {
        if (param.type !== 'select') return true;
        const options = Array.isArray(param.options) ? param.options : panelsConfig.options[param.options] ?? [];
        return options.some(option => option.value === this.configs[id][param.key]);
      });
    },

    async startProcess(id, configData = this.configs[id] || {}) {
      if (this.pending[id] || this.connection !== 'connected' || !this.configValid(id)) return;
      this.pending[id] = 'start';
      delete this.feedback[id];
      try {
        await api.startProcess(id, configData);
        await this.fetchStatus();
      } catch (error) {
        this.setActionError(id, error);
      } finally {
        delete this.pending[id];
      }
    },

    async stopProcess(id) {
      if (this.pending[id] || this.connection !== 'connected') return;
      this.pending[id] = 'stop';
      delete this.feedback[id];
      try {
        await api.stopProcess(id);
        await this.fetchStatus();
      } catch (error) {
        this.setActionError(id, error);
      } finally {
        delete this.pending[id];
      }
    },

    async executeService(id, configData = this.configs[id] || {}) {
      if (this.pending[id] || this.service_status[id] === 'executing' || this.connection !== 'connected' || !this.configValid(id)) return;
      this.pending[id] = 'execute';
      this.serviceRevision++;
      delete this.feedback[id];
      try {
        const response = await api.executeService(id, configData);
        this.service_status[id] = response.data.status;
      } catch (error) {
        this.setActionError(id, error);
      } finally {
        this.serviceRevision++;
        delete this.pending[id];
        await this.fetchStatus();
        this.fetchLogs();
      }
    },

    async cancelService(id) {
      if (this.pending[id] || this.service_status[id] !== 'executing' || this.connection !== 'connected') return;
      this.pending[id] = 'cancel';
      this.serviceRevision++;
      delete this.feedback[id];
      try {
        const response = await api.cancelService(id);
        this.service_status[id] = response.data.status;
      } catch (error) {
        this.setActionError(id, error);
      } finally {
        this.serviceRevision++;
        delete this.pending[id];
        await this.fetchStatus();
        this.fetchLogs();
      }
    },

    setActionError(id, error) {
      const detail = error.response?.data?.detail;
      this.feedback[id] = {
        error: true,
        text: typeof detail === 'string' ? detail : error.response ? 'Request failed. Check the backend and try again.' : error.message === 'Network Error' ? 'Unable to reach the backend. Check the connection before trying again.' : error.message || 'Request failed. Please try again.',
      };
    },
  }
});
