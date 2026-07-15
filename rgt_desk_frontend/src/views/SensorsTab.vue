<script setup>
import { useStore } from '../stores/store';
import ProcessContainer from '../components/ProcessContainer.vue';
const store = useStore();
</script>

<template>
  <div class="grid grid-cols-3 p-3 gap-3 w-full h-full">
    <ProcessContainer class="flex-1" title="Bed Side Camera" id="bed_side_cam" @start="() => store.startProcess('bed_side_cam')" @stop="() => store.stopProcess('bed_side_cam')"/>
    <ProcessContainer class="flex-1" title="Bed Side Thermal" id="bed_side_thermal" @start="() => store.startProcess('bed_side_thermal')" @stop="() => store.stopProcess('bed_side_thermal')"/>
    <ProcessContainer class="flex-1" title="Bed Side Audio" id="bed_side_audio" @start="() => store.startProcess('bed_side_audio')" @stop="() => store.stopProcess('bed_side_audio')"/>
  </div>
</template>
