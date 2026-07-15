import { defineStore } from 'pinia';
import api from '../services/api';

export const useStore = defineStore('store', {
  state: () => ({
    process_status: {
    },
    service_status: {
      "home": "idle",
      "park": "idle",
      "change_tool": "idle",
      "override_tool_location": "idle",
      "space_panda_link_parameters": "idle",
      "set_io": "idle",
    },
    configs: {
      ur20: {
        use_mock_hardware: false,
      },
      nex10: {
        use_mock_hardware: false,
        use_ft_sensor: true,
      },
      spacemouse: {
        ns: "",
      },
      home: {
        ns: "",
        speed: 0.1,
      },
      park: {
        ns: "",
        speed: 0.1,
      },
      change_tool: {
        robot: "",
        tool: "",
      },
      override_tool_location: {
        tool: "",
        location: "",
      },
      space_panda_link_parameters: {
        mimicing_scale: 1.0,
        wrench_passthrough_force_scale: 0.3,
        wrench_passthrough_torque_scale: 0.3,
        damping_value: 100.0,
        mimicing_enabled: false,
        wrench_passthrough_enabled: false,
        damping_enabled: false,
      },
      set_io: {
        robot: "",
        pin: 0,
        state: 0,
      },
    },
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
