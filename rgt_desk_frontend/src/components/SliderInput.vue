<script setup>
defineProps({
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
</script>

<template>
  <div class="flex flex-col gap-2 py-2 w-full">
    <div class="flex justify-between items-center text-sm font-medium text-gray-300">
      <span>{{ label }}</span>
      <span class="text-gray-400 bg-gray-800 px-2 py-0.5 rounded text-xs border border-gray-700">
        {{ modelValue }}
      </span>
    </div>
    
    <input 
      type="range" 
      :min="min" 
      :max="max" 
      :step="step"
      :value="modelValue"
      @input="$emit('update:modelValue', Number($event.target.value))"
      class="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-500 focus:outline-none"
    >
  </div>
</template>
