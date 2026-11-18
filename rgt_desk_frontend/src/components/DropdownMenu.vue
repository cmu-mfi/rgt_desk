<script setup>
import { computed, useId } from 'vue';

const props = defineProps({
  modelValue: { type: [String, Number], required: true },
  label: { type: String, required: true },
  options: { type: Array, required: true },
  display: { type: String, default: 'auto' },
});
const emit = defineEmits(['update:modelValue']);
const id = useId();
const value = computed({ get: () => props.modelValue, set: value => emit('update:modelValue', value) });
const segmented = computed(() => props.options.length > 0 && (
  props.display === 'segmented' || (props.display === 'auto' && props.options.length <= 4)
));
const hasEmptyOption = computed(() => props.options.some(option => option.value === ''));
</script>

<template>
  <div class="param-row" :class="{ 'segmented-row': segmented, 'wide-options': segmented && options.length >= 4 }">
    <template v-if="segmented">
      <span :id="`${id}-label`" class="param-label">{{ label }}</span>
      <div class="segmented-control" role="radiogroup" :aria-labelledby="`${id}-label`">
        <label v-for="option in options" :key="option.value" class="segment-option">
          <input v-model="value" class="sr-only" type="radio" :name="id" :value="option.value" />
          <span>{{ option.label }}</span>
        </label>
      </div>
    </template>
    <template v-else>
      <label :for="id" class="param-label">{{ label }}</label>
      <select :id="id" v-model="value" class="field">
        <option v-if="!hasEmptyOption" disabled value="">Select {{ label.toLowerCase() }}…</option>
        <option v-for="option in options" :key="option.value" :value="option.value">{{ option.label }}</option>
      </select>
    </template>
  </div>
</template>
