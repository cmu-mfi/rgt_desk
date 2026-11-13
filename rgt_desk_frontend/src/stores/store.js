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
    service_status: buildInitialServiceStatus(),
    configs: buildInitialConfigs(),
    pollingInterval: null
  }),
  actions: {
    async fetchStatus() {
      try {
        const response = await api.getStatus();
        this.process_status = response.data;
      } catch (error) {
        console.error("Failed to fetch status from backend:", error);
      }
    },

    startPolling() {
      if (!this.pollingInterval) {
        this.fetchStatus(); // Fetch immediately on start
        this.pollingInterval = setInterval(this.fetchStatus, 1000);
      }
    },

    stopPolling() {
      if (this.pollingInterval) {
        clearInterval(this.pollingInterval);
        this.pollingInterval = null;
      }
    },

    async startProcess(id, configData = this.configs[id] || {}) {
      console.log(`Starting process: ${id}`, configData);
      try {
        await api.startProcess(id, configData);
      } catch (error) {
        console.error(`Failed to start process ${id}:`, error);
      }
    },

    async stopProcess(id) {
      console.log(`Stopping process: ${id}`);
      try {
        await api.stopProcess(id);
      } catch (error) {
        console.error(`Failed to stop process ${id}:`, error);
      }
    },

    async executeService(id, configData = this.configs[id] || {}) {
      console.log(`Executing service: ${id}`, configData);
      try {
        this.service_status[id] = "executing"
        await api.executeService(id, configData);
        this.service_status[id] = "idle"
      } catch (error) {
        console.error(`Failed to execute service ${id}:`, error);
      }
    },
  }
});
