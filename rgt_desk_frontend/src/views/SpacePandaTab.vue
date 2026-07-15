<script setup>
import { useStore } from '../stores/store';
import ProcessContainer from '../components/ProcessContainer.vue';
import ServiceContainer from '../components/ServiceContainer.vue';
import DropdownMenu from '../components/DropdownMenu.vue';
import SliderInput from '../components/SliderInput.vue';
import ToggleSwitch from '../components/ToggleSwitch.vue';
const store = useStore();
</script>

<template>
  <div class="grid grid-cols-2 p-3 gap-3 w-full h-full">
    <div class="grid grid-rows-2 p-3 gap-3 w-full h-full">
      <ProcessContainer class="flex-1" title="Panda" id="panda" @start="() => store.startProcess('panda')" @stop="() => store.stopProcess('panda')"/>
      <ProcessContainer class="flex-1" title="Space Panda Link" id="space_panda_link" @start="() => store.startProcess('space_panda_link')" @stop="() => store.stopProcess('space_panda_link')"/>
    </div>
    <div class="grid grid-rows-1 p-3 gap-3 w-full h-full">
      <ServiceContainer class="flex-1" title="Space Panda Link Parameters" id="space_panda_link_parameters" @execute="() => store.executeService('space_panda_link_parameters')">
        <SliderInput 
          v-model="store.configs.space_panda_link_parameters.mimicing_scale" 
          label="Mimicing Scale" 
          :min="0.1" 
          :max="2.0" 
          :step="0.1" 
        />
        <SliderInput 
          v-model="store.configs.space_panda_link_parameters.wrench_passthrough_force_scale" 
          label="Force Scale" 
          :min="0.0" 
          :max="1.0" 
          :step="0.1" 
        />
        <SliderInput 
          v-model="store.configs.space_panda_link_parameters.wrench_passthrough_torque_scale" 
          label="Torque Scale" 
          :min="0.0" 
          :max="1.0" 
          :step="0.1" 
        />
        <SliderInput 
          v-model="store.configs.space_panda_link_parameters.damping_value" 
          label="Damping Value" 
          :min="10" 
          :max="150" 
          :step="10" 
        />
        <ToggleSwitch 
          v-model="store.configs.space_panda_link_parameters.mimicing_enabled" 
          label="Mimicing Enabled" 
        />
        <ToggleSwitch 
          v-model="store.configs.space_panda_link_parameters.wrench_passthrough_enabled" 
          label="Wrench Passthrough Enabled" 
        />
        <ToggleSwitch 
          v-model="store.configs.space_panda_link_parameters.damping_enabled" 
          label="Damping Enabled" 
        />
      </ServiceContainer>
    </div>
  </div>
</template>
