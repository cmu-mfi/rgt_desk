<script setup>
import { computed, ref } from 'vue';
import { useRoute } from 'vue-router';
import { Terminal } from '@lucide/vue';
import ProcessContainer from './ProcessContainer.vue';
import ServiceContainer from './ServiceContainer.vue';
import ParamControl from './ParamControl.vue';
import { useStore } from '../stores/store';

const props = defineProps({
  panels: { type: Array, required: true },
  columns: { type: Number, default: 2 },
  showLogs: { type: Boolean, default: false },
});
const store = useStore();
const route = useRoute();
const titles = { '/main': 'Main', '/sensors': 'Sensors & Tools', '/utilities': 'Utilities', '/space_panda': 'Space Panda' };
const logState = ref({});
const anyLogsOpen = computed(() => props.panels.some(panel => logState.value[panel.id]));

function toggleAllLogs() {
  const open = !anyLogsOpen.value;
  logState.value = Object.fromEntries(props.panels.filter(panel => panel.type === 'process').map(panel => [panel.id, open]));
}
</script>

<template>
  <section>
    <div class="panel-toolbar">
      <h1>{{ titles[route.path] }}</h1>
      <button v-if="showLogs" class="quiet-btn" @click="toggleAllLogs" :aria-pressed="anyLogsOpen">
        <Terminal :size="14" />{{ anyLogsOpen ? 'Collapse all logs' : 'Expand all logs' }}
      </button>
    </div>
    <div class="panel-grid" :class="{ 'three-columns': columns === 3, 'one-column': columns === 1 }">
      <template v-for="panel in panels" :key="panel.id">
        <component :is="panel.type === 'process' ? ProcessContainer : ServiceContainer"
          :title="panel.title" :description="panel.description" :note="panel.note" :id="panel.id"
          :show-logs="showLogs" :logs-open="!!logState[panel.id]" :has-params="!!panel.params?.length"
          :class="{ 'panel-span': panel.span === 2 }"
          @logs-change="logState[panel.id] = $event"
          @start="store.startProcess(panel.id)" @stop="store.stopProcess(panel.id)" @execute="store.executeService(panel.id)">
          <ParamControl v-for="param in panel.params ?? []" :key="param.key" v-model="store.configs[panel.id][param.key]" :param="param" />
        </component>
      </template>
    </div>
  </section>
</template>
