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
  description: {
    type: String,
    default: ''
  },
});

const emit = defineEmits(['start', 'stop']);

const store = useStore();

const STATUS_COLORS = {
  running: '#22c55e', // green-500
  started: '#eab308', // yellow-500
  error:   '#ef4444', // red-500
  stopped: '#52525b', // zinc-600
  unknown: '#52525b', // zinc-600 (fallback)
};
// Pending/transient states get a blinking LED, like an instrument annunciator.
const BLINKING = new Set(['started', 'error']);
const currentStatus = computed(() => {
  if (!props.id || !store.process_status[props.id]) return 'unknown';
  return store.process_status[props.id];
});
const statusText = computed(() => currentStatus.value);
const statusColor = computed(() => STATUS_COLORS[currentStatus.value] || STATUS_COLORS.unknown);
const isBlinking = computed(() => BLINKING.has(currentStatus.value));
const ledGlow = computed(() =>
  currentStatus.value === 'running' ? `0 0 6px ${statusColor.value}` : 'none'
);

</script>

<template>
  <div class="panel">
    <span
      class="absolute left-0 top-0 bottom-0 w-0.5"
      :style="{ backgroundColor: statusColor }"
    ></span>

    <header class="panel-header">
      <h3 class="m-0 text-[18px] font-semibold uppercase tracking-wider text-zinc-100">{{ title }}</h3>
      <div class="flex items-center gap-1.5">
        <span
          class="led"
          :class="{ 'animate-pulse': isBlinking }"
          :style="{ backgroundColor: statusColor, boxShadow: ledGlow }"
        ></span>
        <span class="micro-label" :style="{ color: statusColor }">{{ statusText }}</span>
      </div>
    </header>

    <p v-if="description" class="pl-4 pr-3 mt-1 mb-3 text-[13px] leading-snug text-zinc-500">{{ description }}</p>

    <div class="panel-body">
      <slot></slot>
    </div>

    <footer class="panel-footer">
      <button @click="emit('start')" class="key-btn hover:text-green-400 hover:bg-green-500/10 active:text-green-300 active:bg-green-500/15">
        Start
      </button>
      <button @click="emit('stop')" class="key-btn border-l border-hairline hover:text-red-400 hover:bg-red-500/10 active:text-red-300 active:bg-red-500/15">
        Stop
      </button>
    </footer>
  </div>
</template>
