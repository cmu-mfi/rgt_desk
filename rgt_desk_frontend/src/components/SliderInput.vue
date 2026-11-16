<script setup>
import { computed, useId } from 'vue';
const props = defineProps({
  modelValue: { type: Number, required: true }, label: { type: String, required: true },
  min: { type: Number, required: true }, max: { type: Number, required: true }, step: { type: Number, required: true },
  format: { type: String, default: '' },
});
defineEmits(['update:modelValue']);
const id = useId();
const display = value => props.format === 'percent' ? `${Math.round(value * 100)}%` : value;
const displayValue = computed(() => display(props.modelValue));
</script>
<template>
  <div class="slider-control"><div class="slider-heading"><label :for="id" class="param-label">{{ label }}</label><output :for="id" class="slider-value">{{ displayValue }}</output></div><input :id="id" type="range" :min="min" :max="max" :step="step" :value="modelValue" :aria-valuetext="String(displayValue)" @input="$emit('update:modelValue', Number($event.target.value))" class="fader" /><div class="slider-range"><span>{{ display(min) }}</span><span>{{ display(max) }}</span></div></div>
</template>
