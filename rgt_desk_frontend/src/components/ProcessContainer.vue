<script setup>
import { computed } from 'vue';
import { AlertCircle, LoaderCircle, Play, Square } from '@lucide/vue';
import { useStore } from '../stores/store';
import PanelIcon from './PanelIcon.vue';
import TerminalLogs from './TerminalLogs.vue';
const props = defineProps({
  title: { type: String, required: true }, id: { type: String, required: true },
  description: { type: String, default: '' },
  note: { type: String, default: '' }, showLogs: { type: Boolean, default: false },
  logsOpen: { type: Boolean, default: false }, hasParams: { type: Boolean, default: false },
});
const emit = defineEmits(['start', 'stop', 'logs-change']);
const store = useStore();
const currentStatus = computed(() => store.connection === 'connected' ? store.process_status[props.id] ?? 'unknown' : 'unknown');
const statusText = computed(() => ({ running: 'Running', started: 'Started', error: 'Error', stopped: 'Stopped', unknown: 'Unknown' })[currentStatus.value] ?? 'Unknown');
const pending = computed(() => store.pending[props.id]);
const feedback = computed(() => store.feedback[props.id]);
const active = computed(() => ['running', 'started', 'error'].includes(currentStatus.value));
const canStart = computed(() => store.connection === 'connected' && currentStatus.value === 'stopped' && !pending.value && store.configValid(props.id));
const logLines = computed(() => store.process_logs[props.id] ?? []);
</script>

<template>
  <article class="panel" :data-status="currentStatus" :aria-labelledby="`${id}-title`">
    <header class="panel-header"><PanelIcon :id="id" /><h2 class="panel-title" :id="`${id}-title`">{{ title }}</h2><span class="status-badge" :title="currentStatus === 'started' ? 'Process started; waiting for a matching ROS node.' : undefined"><span class="status-dot" />{{ statusText }}</span></header>
    <p v-if="description" class="panel-description">{{ description }}</p>
    <div v-if="hasParams || note" class="panel-body" :class="{ 'launch-parameters': hasParams }">
      <h3 v-if="hasParams" class="settings-label">Parameters for next launch</h3><slot />
      <p v-if="note" class="panel-note">{{ note }}</p>
    </div>
    <footer class="panel-footer">
      <button class="action-btn" @click="emit('start')" :disabled="!canStart" :aria-label="`Start ${title}`"><LoaderCircle v-if="pending === 'start'" :size="12" class="spin" /><Play v-else :size="12" />{{ pending === 'start' ? 'Starting…' : 'Start' }}</button>
      <button class="action-btn secondary" @click="emit('stop')" :disabled="!active || !!pending || store.connection !== 'connected'" :aria-label="`Stop ${title}`"><LoaderCircle v-if="pending === 'stop'" :size="12" class="spin" /><Square v-else :size="11" />{{ pending === 'stop' ? 'Stopping…' : 'Stop' }}</button>
      <div v-if="feedback?.error" class="action-message" role="alert"><AlertCircle :size="13" />{{ feedback.text }}</div>
    </footer>
    <TerminalLogs v-if="showLogs" :title="title" :lines="logLines" :open="logsOpen" :connected="store.connection === 'connected'" @logs-change="emit('logs-change', $event)" />
  </article>
</template>
