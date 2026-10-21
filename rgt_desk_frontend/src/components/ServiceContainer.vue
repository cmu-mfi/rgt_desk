<script setup>
import { computed, useSlots } from 'vue';
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

const slots = useSlots();
// Cards without params drop the body entirely, so the action key owns the module.
const hasBody = computed(() => {
  if (!slots.default) return false;
  const vnodes = slots.default();
  return Array.isArray(vnodes) ? vnodes.length > 0 : !!vnodes;
});
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
      <h3 class="m-0 text-[14px] font-semibold uppercase tracking-wider text-zinc-100">{{ title }}</h3>
      <div class="flex items-center gap-1.5">
        <span
          class="led"
          :class="{ 'animate-pulse': isBlinking }"
          :style="{ backgroundColor: statusColor, boxShadow: ledGlow }"
        ></span>
        <span class="micro-label" :style="{ color: statusColor }">{{ statusText }}</span>
      </div>
    </header>

    <div v-if="hasBody" class="panel-body">
      <slot></slot>
    </div>

    <footer class="panel-footer" :class="{ 'flex-1': !hasBody }">
      <button @click="emit('execute')" class="key-btn bg-accent hover:bg-amber-400 active:bg-amber-300">
        Execute
      </button>
    </footer>
  </div>
</template>
