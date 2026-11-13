<script setup>
import { computed, nextTick, ref, watch } from 'vue';
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
  showLogs: {
    type: Boolean,
    default: false
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

// Terminal log viewer: the process's tmux pane history in a 5-line scrollable
// strip, pinned to the bottom as new output arrives. Following pauses when the
// user scrolls up and resumes once they scroll back to the bottom.
const logLines = computed(() => store.process_logs[props.id] ?? []);
const logBox = ref(null);
const followLog = ref(true);

function onLogScroll() {
  const el = logBox.value;
  if (!el) return;
  followLog.value = el.scrollTop + el.clientHeight >= el.scrollHeight - 2;
}

watch(logLines, async () => {
  if (!followLog.value) return;
  await nextTick();
  logBox.value?.scrollTo({ top: logBox.value.scrollHeight });
});

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

    <div
      v-if="showLogs"
      ref="logBox"
      class="log-view shrink-0 overflow-y-auto bg-console border-t border-hairline px-3 py-1.5 font-mono text-[12px] leading-4 text-zinc-400"
      @scroll="onLogScroll"
    >
      <div v-if="!logLines.length" class="select-none text-zinc-600">— no terminal output —</div>
      <div v-for="(line, i) in logLines" :key="i" class="whitespace-pre">{{ line }}</div>
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

<style scoped>
/* 5 visible lines (leading-4 = 16px each) plus py-1.5 vertical padding */
.log-view {
  height: calc(5 * 1rem + 0.75rem);
}
</style>
