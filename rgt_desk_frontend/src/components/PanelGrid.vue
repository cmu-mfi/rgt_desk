<script setup>
import ProcessContainer from './ProcessContainer.vue';
import ServiceContainer from './ServiceContainer.vue';
import ParamControl from './ParamControl.vue';
import { useStore } from '../stores/store';

const props = defineProps({
  panels: {
    type: Array,
    required: true
  },
  columns: {
    type: Number,
    default: 2
  }
});

const store = useStore();

// Desktop column counts: phones get 1 column, tablets 2 (sm:), desktop this.
const DESKTOP_COLS = {
  1: 'lg:grid-cols-1',
  2: 'lg:grid-cols-2',
  3: 'lg:grid-cols-3',
};

// A panel with span: 2 stretches across both tablet/desktop columns.
function panelClass(panel) {
  return panel.span === 2 ? 'sm:col-span-2' : '';
}
</script>

<template>
  <div
    class="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full min-h-full p-3 md:h-full"
    :class="DESKTOP_COLS[props.columns] || DESKTOP_COLS[2]"
  >
    <template v-for="panel in panels" :key="panel.id">
      <ProcessContainer
        v-if="panel.type === 'process'"
        :title="panel.title"
        :id="panel.id"
        :class="panelClass(panel)"
        @start="() => store.startProcess(panel.id)"
        @stop="() => store.stopProcess(panel.id)"
      >
        <ParamControl
          v-for="param in panel.params ?? []"
          :key="param.key"
          v-model="store.configs[panel.id][param.key]"
          :param="param"
        />
      </ProcessContainer>
      <ServiceContainer
        v-else
        :title="panel.title"
        :id="panel.id"
        :class="panelClass(panel)"
        @execute="() => store.executeService(panel.id)"
      >
        <ParamControl
          v-for="param in panel.params ?? []"
          :key="param.key"
          v-model="store.configs[panel.id][param.key]"
          :param="param"
        />
      </ServiceContainer>
    </template>
  </div>
</template>
