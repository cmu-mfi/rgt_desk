<script setup>
import { computed } from 'vue';
import { useStore } from '../stores/store';

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  id: {
    type: String,
    required: true
  },
});

const emit = defineEmits(['start', 'stop']);

const store = useStore();

const STATUS_COLORS = {
  running: '#22c55e', // green-500
  started: '#eab308', // yellow-500
  error:   '#ef4444', // red-500
  stopped: '#9ca3af', // gray-400 
  unknown: '#9ca3af', // gray-400 (fallback)
};
const currentStatus = computed(() => {
  if (!props.id || !store.process_status[props.id]) return 'unknown';
  return store.process_status[props.id];
});
const statusText = computed(() => currentStatus.value);
const statusColor = computed(() => STATUS_COLORS[currentStatus.value] || STATUS_COLORS.unknown);

</script>

<template>
  <div class="flex flex-col h-full bg-gray-900/50 text-gray-200 rounded-xl overflow-hidden font-sans transition duration-200 border-t border-b" :style="{ borderColor: statusColor }">
    
    <div class="flex justify-between items-center px-4 py-1 border-b border-gray-600">
      <h3 class="m-0 text-lg font-semibold">{{ title }}</h3>
      <div class="flex items-center gap-2 bg-white px-3 py-1 rounded-full border border-gray-200 shadow-sm">
        <span 
          class="w-2 h-2 rounded-full shrink-0" 
          :style="{ backgroundColor: statusColor }"
        ></span>
        <span 
          class="text-xs font-medium uppercase tracking-wider" 
          :style="{ color: statusColor }"
        >
        {{ statusText }}
        </span>
      </div>
    </div>
    
    <div class="flex-1 px-4 py-1">
      <slot></slot> 
    </div>

    <div class="flex gap-3 w-full px-4 py-2 border-t border-gray-600">
      <button @click="emit('start')" class="flex-1 px-4 py-1.5 text-sm font-semibold text-gray-400 hover:text-green-400 active:text-green-400 border-2 border-gray-500 hover:border-green-500/40 active:border-green-500/40 rounded-md transition">
        Start
      </button>
      <button @click="emit('stop')" class="flex-1 px-4 py-1.5 text-sm font-semibold text-gray-400 hover:text-red-400 active:text-red-400 border-2 border-gray-500 hover:border-red-500/40 active:border-red-500/40 rounded-md transition">
         Stop
      </button>
    </div>
  </div>
</template>
