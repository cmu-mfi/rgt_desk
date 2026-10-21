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

const emit = defineEmits(['execute']);
const store = useStore();
const STATUS_COLORS = {
  executing: '#1490de',
  idle:      '#52525b', // zinc-600
  unknown:   '#52525b', // zinc-600 (fallback)
};
const currentStatus = computed(() => {
  if (!props.id || !store.service_status[props.id]) return 'unknown';
  return store.service_status[props.id];
});
const statusText = computed(() => currentStatus.value);
const statusColor = computed(() => STATUS_COLORS[currentStatus.value] || STATUS_COLORS.unknown);
const isBlinking = computed(() => currentStatus.value === 'executing');
const ledGlow = computed(() =>
  currentStatus.value === 'executing' ? `0 0 6px ${statusColor.value}` : 'none'
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

    <p v-if="description" class="pl-4 pr-3 mt-1 mb-3 text-[11px] leading-snug text-zinc-500">{{ description }}</p>

    <div class="panel-body">
      <slot></slot>
    </div>

    <footer class="panel-footer">
      <button @click="emit('execute')" class="key-btn hover:text-blue-400 hover:bg-blue-500/10 active:text-blue-300 active:bg-blue-500/15">
        Execute
      </button>
    </footer>
  </div>
</template>
