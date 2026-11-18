<script setup>
import { computed } from 'vue';
import { AlertCircle, ArrowRight, LoaderCircle, Square } from '@lucide/vue';
import { useStore } from '../stores/store';
import PanelIcon from './PanelIcon.vue';
import TerminalLogs from './TerminalLogs.vue';
const props = defineProps({
  title: { type: String, required: true }, id: { type: String, required: true },
  description: { type: String, default: '' },
  note: { type: String, default: '' }, hasParams: { type: Boolean, default: false },
  showLogs: Boolean, logsOpen: Boolean,
});
const emit = defineEmits(['execute', 'cancel', 'logs-change']);
const store = useStore();
const executing = computed(() => store.service_status[props.id] === 'executing');
const currentStatus = computed(() => executing.value ? 'executing' : 'idle');
const statusText = computed(() => executing.value ? 'Executing' : 'Idle');
const pending = computed(() => store.pending[props.id]);
const feedback = computed(() => store.feedback[props.id]);
const canExecute = computed(() => store.connection === 'connected' && !executing.value && !pending.value && store.configValid(props.id));
const logLines = computed(() => store.service_logs[props.id] ?? []);
const labels = { gripper_command: 'Command gripper', home: 'Home robot', park: 'Park robot', change_tool: 'Change tool', override_tool_location: 'Apply location', set_io: 'Set output', space_panda_link_parameters: 'Apply parameters' };
</script>
<template>
  <article class="panel" :data-status="currentStatus" :aria-labelledby="`${id}-title`">
    <header class="panel-header"><PanelIcon :id="id" /><h2 class="panel-title" :id="`${id}-title`">{{ title }}</h2><span class="status-badge"><span class="status-dot" />{{ statusText }}</span></header>
    <p v-if="description" class="panel-description">{{ description }}</p>
    <fieldset class="panel-body" :disabled="executing || !!pending"><legend class="sr-only">{{ title }} parameters</legend><slot /></fieldset>
    <p v-if="note" class="panel-note">{{ note }}</p>
    <footer class="panel-footer">
      <button class="action-btn" @click="emit('execute')" :disabled="!canExecute" :aria-label="`${labels[id] ?? 'Execute'} — ${title}`"><LoaderCircle v-if="executing || pending === 'execute'" :size="13" class="spin" /><ArrowRight v-else :size="13" />{{ pending === 'execute' ? 'Starting…' : executing ? 'Executing…' : labels[id] ?? 'Execute' }}</button>
      <button class="action-btn secondary" @click="emit('cancel')" :disabled="!executing || !!pending || store.connection !== 'connected'" :aria-label="`Cancel ${title} call`" title="Stops the local call; the ROS server may continue work already accepted."><LoaderCircle v-if="pending === 'cancel'" :size="12" class="spin" /><Square v-else :size="11" />{{ pending === 'cancel' ? 'Cancelling…' : 'Cancel call' }}</button>
      <div v-if="feedback?.error" class="action-message" role="alert"><AlertCircle :size="13" />{{ feedback.text }}</div>
    </footer>
    <TerminalLogs v-if="showLogs" :title="title" :lines="logLines" :open="logsOpen" :connected="store.connection === 'connected'" @logs-change="emit('logs-change', $event)" />
  </article>
</template>
