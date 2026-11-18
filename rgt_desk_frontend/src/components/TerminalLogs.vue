<script setup>
import { nextTick, ref, watch } from 'vue';
import { ChevronDown, Terminal } from '@lucide/vue';

const props = defineProps({
  title: { type: String, required: true },
  lines: { type: Array, default: () => [] },
  open: Boolean,
  connected: Boolean,
});
const emit = defineEmits(['logs-change']);
const logBox = ref(null);
const followLog = ref(true);
function onLogToggle(event) {
  emit('logs-change', event.target.open);
  if (event.target.open && followLog.value) jumpToLatest();
}
function onLogScroll() {
  const el = logBox.value;
  if (el) followLog.value = el.scrollTop + el.clientHeight >= el.scrollHeight - 5;
}
async function jumpToLatest() {
  followLog.value = true;
  await nextTick();
  logBox.value?.scrollTo({ top: logBox.value.scrollHeight });
}
watch(() => props.lines, () => { if (followLog.value) jumpToLatest(); });
watch(() => props.open, async () => {
  await nextTick();
  if (props.open) jumpToLatest();
});
</script>

<template>
  <details class="log-details" :open="open" @toggle="onLogToggle">
    <summary><Terminal :size="13" />Logs<ChevronDown :size="13" class="chevron" /></summary>
    <div ref="logBox" class="log-view" tabindex="0" :aria-label="`${title} terminal output`" @scroll="onLogScroll">
      <div v-if="!lines.length" class="log-empty"><Terminal :size="14" />No output</div>
      <div v-for="(line, i) in lines" :key="i" class="log-line">{{ line }}</div>
    </div>
    <div class="log-tools"><span>{{ !connected ? 'Disconnected · output may be out of date' : followLog ? 'Following latest output' : 'Auto-scroll paused' }}</span><button @click="jumpToLatest" :aria-label="`Jump to latest ${title} output`">Latest ↓</button></div>
  </details>
</template>
