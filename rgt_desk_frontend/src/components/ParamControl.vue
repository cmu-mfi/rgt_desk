<script setup>
import ToggleSwitch from './ToggleSwitch.vue';
import SliderInput from './SliderInput.vue';
import DropdownMenu from './DropdownMenu.vue';
import panelsConfig from '../config/panels.json';

defineProps({
  param: {
    type: Object,
    required: true
  },
  modelValue: {
    required: true
  }
});

defineEmits(['update:modelValue']);

const OPTION_SETS = panelsConfig.options ?? {};

// A param's `options` is either the name of a shared option set in
// panels.json (e.g. "robots") or an inline array of { label, value }.
function resolveOptions(param) {
  return Array.isArray(param.options) ? param.options : OPTION_SETS[param.options] ?? [];
}
</script>

<template>
  <ToggleSwitch
    v-if="param.type === 'toggle'"
    :model-value="modelValue"
    :label="param.label"
    @update:modelValue="$emit('update:modelValue', $event)"
  />
  <SliderInput
    v-else-if="param.type === 'slider'"
    :model-value="modelValue"
    :label="param.label"
    :min="param.min"
    :max="param.max"
    :step="param.step"
    @update:modelValue="$emit('update:modelValue', $event)"
  />
  <DropdownMenu
    v-else-if="param.type === 'select'"
    :model-value="modelValue"
    :label="param.label"
    :options="resolveOptions(param)"
    @update:modelValue="$emit('update:modelValue', $event)"
  />
</template>
