<script setup>
import { computed } from 'vue';
import { AlertCircle, ArrowRight, Check, LoaderCircle } from '@lucide/vue';
import { useStore } from '../stores/store';
import PanelIcon from './PanelIcon.vue';
const props = defineProps({
  title: { type: String, required: true }, id: { type: String, required: true },
  description: { type: String, default: '' },
  note: { type: String, default: '' }, hasParams: { type: Boolean, default: false },
  showLogs: Boolean, logsOpen: Boolean,
});
const emit = defineEmits(['execute', 'start', 'stop', 'logs-change']);
const store = useStore();
const executing = computed(() => store.service_status[props.id] === 'executing');
const feedback = computed(() => store.feedback[props.id]);
const canExecute = computed(() => store.connection === 'connected' && !executing.value && store.configValid(props.id));
const labels = { home: 'Home robot', park: 'Park robot', change_tool: 'Change tool', override_tool_location: 'Apply location', set_io: 'Set output', space_panda_link_parameters: 'Apply parameters' };
</script>
<template>
  <article class="panel" :data-status="executing ? 'executing' : 'idle'" :aria-labelledby="`${id}-title`">
    <header class="panel-header"><PanelIcon :id="id" /><h2 class="panel-title" :id="`${id}-title`">{{ title }}</h2><span class="status-badge"><span class="status-dot" />{{ executing ? 'Executing' : 'Idle' }}</span></header>
    <p v-if="description" class="panel-description">{{ description }}</p>
    <fieldset class="panel-body" :disabled="executing"><legend class="sr-only">{{ title }} parameters</legend><slot /></fieldset>
    <p v-if="note" class="panel-note">{{ note }}</p>
    <footer class="panel-footer">
      <button class="action-btn" @click="emit('execute')" :disabled="!canExecute" :aria-label="`${labels[id] ?? 'Execute'} — ${title}`"><LoaderCircle v-if="executing" :size="13" class="spin" /><ArrowRight v-else :size="13" />{{ executing ? 'Executing…' : labels[id] ?? 'Execute' }}</button>
      <div v-if="feedback" class="action-message" :class="{ error: feedback.error }" :role="feedback.error ? 'alert' : 'status'"><component :is="feedback.error ? AlertCircle : Check" :size="13" />{{ feedback.text }}</div>
    </footer>
  </article>
</template>
