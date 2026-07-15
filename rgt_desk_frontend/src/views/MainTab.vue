<script setup>
import { useStore } from '../stores/store';
import ProcessContainer from '../components/ProcessContainer.vue';
import ToggleSwitch from '../components/ToggleSwitch.vue';

const store = useStore();
</script>

<template>
  <div class="grid grid-cols-2 grid-rows-2 p-3 gap-3 w-full h-full">
    <ProcessContainer class="flex-1" title="UR 20" id="ur20" @start="() => store.startProcess('ur20')" @stop="() => store.stopProcess('ur20')">
      <ToggleSwitch 
        v-model="store.configs.ur20.use_mock_hardware" 
        label="Use Mock Hardware" 
      />
    </ProcessContainer>

    <ProcessContainer class="flex-1" title="Nex 10" id="nex10" @start="() => store.startProcess('nex10')" @stop="() => store.stopProcess('nex10')">
      <ToggleSwitch 
        v-model="store.configs.nex10.use_mock_hardware" 
        label="Use Mock Hardware" 
      />
      <ToggleSwitch 
        v-model="store.configs.nex10.use_ft_sensor" 
        label="Use FT Sensor" 
      />
    </ProcessContainer>

    <ProcessContainer class="flex-1" title="RGT Manager" id="rgt_manager" @start="() => store.startProcess('rgt_manager')" @stop="() => store.stopProcess('rgt_manager')"/>
    <ProcessContainer class="flex-1" title="Foxglove Bridge" id="foxglove_bridge" @start="() => store.startProcess('foxglove_bridge')" @stop="() => store.stopProcess('foxglove_bridge')"/>
    
  </div>
</template>
