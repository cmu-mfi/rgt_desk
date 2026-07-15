<script setup>
defineProps({
  modelValue: {
    type: [String, Number],
    required: true
  },
  label: {
    type: String,
    required: true
  },
  options: {
    type: Array,
    required: true
    // Expected format: [{ label: 'Option 1', value: 'opt1' }, ...]
  }
});

defineEmits(['update:modelValue']);
</script>

<template>
  <div class="flex items-center justify-between gap-3 py-2">
    <label class="text-sm font-medium text-gray-300 whitespace-nowrap">
      {{ label }}
    </label>
    <select
      :value="modelValue"
      @change="$emit('update:modelValue', $event.target.value)"
      class="bg-gray-800 border border-gray-600 text-gray-200 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block p-1.5 w-full max-w-[150px] outline-none transition-colors cursor-pointer"
    >
      <option 
        v-for="option in options" 
        :key="option.value" 
        :value="option.value"
      >
        {{ option.label }}
      </option>
    </select>
  </div>
</template>
