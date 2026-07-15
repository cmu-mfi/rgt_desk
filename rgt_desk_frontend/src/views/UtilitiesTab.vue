<script setup>
import { useStore } from '../stores/store';
import ProcessContainer from '../components/ProcessContainer.vue';
import ServiceContainer from '../components/ServiceContainer.vue';
import DropdownMenu from '../components/DropdownMenu.vue';
import SliderInput from '../components/SliderInput.vue';
const store = useStore();

const robots = [
  { label: 'UR 20', value: 'ur20' },
  { label: 'Nex 10', value: 'nex10' }
];
const tools = [
  { label: 'None', value: '' },
  { label: 'Sander', value: 'sander' },
  { label: 'Grinder', value: 'grinder' },
  { label: 'Gelsight Vision', value: 'gelsight_vision' }
];
const locations = [
  { label: 'Tray', value: 'tray' },
  { label: 'UR 20', value: 'ur20' },
  { label: 'Nex 10', value: 'nex10' }
];
const pins = [
  { label: 'Pin 0', value: 0 },
  { label: 'Pin 1', value: 1 },
  { label: 'Pin 2', value: 2 },
  { label: 'Pin 3', value: 3 },
  { label: 'Pin 4', value: 4 },
  { label: 'Pin 5', value: 5 },
  { label: 'Pin 6', value: 6 },
  { label: 'Pin 7', value: 7 },
];
const states = [
  { label: 'Low', value: 0 },
  { label: 'High', value: 1 },
];
</script>

<template>
  <div class="grid grid-cols-2 grid-rows-3 p-3 gap-3 w-full h-full">
    <!-- Spacemouse -->
    <ProcessContainer class="flex-1" title="Spacemouse" id="spacemouse" @start="() => store.startProcess('spacemouse')" @stop="() => store.stopProcess('spacemouse')">
      <DropdownMenu 
        v-model="store.configs.spacemouse.ns" 
        label="Robot" 
        :options="robots" 
      />
    </ProcessContainer>
    <!-- Home -->
    <ServiceContainer class="flex-1" title="Home" id="home" @execute="() => store.executeService('home')">
      <DropdownMenu 
        v-model="store.configs.home.ns" 
        label="Robot" 
        :options="robots" 
      />
      <SliderInput 
        v-model="store.configs.home.speed" 
        label="Speed (%)" 
        :min="0.1" 
        :max="1.0" 
        :step="0.1" 
      />
    </ServiceContainer>
    <!-- Park -->
    <ServiceContainer class="flex-1" title="Park" id="park" @execute="() => store.executeService('park')">
      <DropdownMenu 
        v-model="store.configs.park.ns" 
        label="Robot" 
        :options="robots" 
      />
      <SliderInput 
        v-model="store.configs.park.speed" 
        label="Speed (%)" 
        :min="0.1" 
        :max="1.0" 
        :step="0.1" 
      />
    </ServiceContainer>
    <!-- Change Tool -->
    <ServiceContainer class="flex-1" title="Change Tool" id="change_tool" @execute="() => store.executeService('change_tool')">
      <DropdownMenu 
        v-model="store.configs.change_tool.robot" 
        label="Robot" 
        :options="robots" 
      />
      <DropdownMenu 
        v-model="store.configs.change_tool.tool" 
        label="Tool" 
        :options="tools" 
      />
    </ServiceContainer>
    <!-- Override Tool Location -->
    <ServiceContainer class="flex-1" title="Override Tool Location" id="override_tool_location" @execute="() => store.executeService('override_tool_location')">
      <DropdownMenu 
        v-model="store.configs.override_tool_location.tool" 
        label="Tool" 
        :options="tools" 
      />
      <DropdownMenu 
        v-model="store.configs.override_tool_location.location" 
        label="Location" 
        :options="locations" 
      />
    </ServiceContainer>
    <ServiceContainer class="flex-1" title="Set IO" id="set_io" @execute="() => store.executeService('set_io')">
      <DropdownMenu 
        v-model="store.configs.set_io.robot" 
        label="Robot" 
        :options="robots" 
      />
      <DropdownMenu 
        v-model="store.configs.set_io.pin" 
        label="Pin" 
        :options="pins" 
      />
      <DropdownMenu 
        v-model="store.configs.set_io.state" 
        label="State" 
        :options="states" 
      />
    </ServiceContainer>
  </div>
</template>
