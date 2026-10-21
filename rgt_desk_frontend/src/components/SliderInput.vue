<script setup>
import { computed } from 'vue';

const props = defineProps({
  modelValue: {
    type: Number,
    required: true
  },
  label: {
    type: String,
    required: true
  },
  min: {
    type: Number,
    required: true
  },
  max: {
    type: Number,
    required: true
  },
  step: {
    type: Number,
    required: true
  }
});

defineEmits(['update:modelValue']);

// Filled-track position for the fader, consumed by the scoped CSS below.
const fill = computed(() => {
  const span = props.max - props.min;
  return span === 0 ? 0 : ((props.modelValue - props.min) / span) * 100;
});
</script>

<template>
  <div class="flex flex-col gap-1.5 py-2 w-full">
    <div class="flex justify-between items-center gap-3">
      <label class="text-[13px] font-medium text-zinc-300">{{ label }}</label>
      <span class="font-mono text-[11px] text-zinc-200 bg-zinc-900 border border-hairline px-1.5 py-0.5 min-w-12 text-center">
        {{ modelValue }}
      </span>
    </div>

    <input
      type="range"
      :min="min"
      :max="max"
      :step="step"
      :value="modelValue"
      :style="{ '--fill': fill + '%' }"
      @input="$emit('update:modelValue', Number($event.target.value))"
      class="fader w-full cursor-pointer focus:outline-none"
    >
  </div>
</template>

<style scoped>
.fader {
  -webkit-appearance: none;
  appearance: none;
  height: 16px;
  background: transparent;
}
.fader::-webkit-slider-runnable-track {
  height: 2px;
  background: linear-gradient(to right, #f59e0b var(--fill, 0%), #26262b var(--fill, 0%));
}
.fader::-webkit-slider-thumb {
  -webkit-appearance: none;
  margin-top: -7px;
  width: 10px;
  height: 16px;
  background: #e4e4e7;
  border: none;
  border-radius: 0;
}
.fader:focus-visible::-webkit-slider-thumb {
  outline: 1px solid #f59e0b;
  outline-offset: 2px;
}
.fader::-moz-range-track {
  height: 2px;
  background: #26262b;
}
.fader::-moz-range-progress {
  height: 2px;
  background: #f59e0b;
}
.fader::-moz-range-thumb {
  width: 10px;
  height: 16px;
  background: #e4e4e7;
  border: none;
  border-radius: 0;
}
</style>
