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

const emit = defineEmits(['execute']);
const store = useStore();
const STATUS_COLORS = {
  executing: '#1490de',
  idle:      '#9ca3af',
  unknown:   '#9ca3af',
};
const currentStatus = computed(() => {
  if (!props.id || !store.service_status[props.id]) return 'unknown';
  return store.service_status[props.id];
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
      <button @click="emit('execute')" class="flex-1 px-4 py-1.5 text-sm font-semibold text-gray-400 hover:text-blue-400 active:text-blue-400 border-2 border-gray-500 hover:border-blue-500/40 active:border-blue-500/40 rounded-md transition">
        Execute
      </button>
    </div>
  </div>
</template>
