<script setup>
defineProps({
  modelValue: {
    type: Boolean,
    required: true
  },
  label: {
    type: String,
    required: true
  }
});

defineEmits(['update:modelValue']);
</script>

<template>
  <div class="flex items-center gap-3 py-2">
    <label class="relative inline-flex items-center cursor-pointer">
      <input 
        type="checkbox" 
        :checked="modelValue"
        @change="$emit('update:modelValue', $event.target.checked)"
        class="sr-only peer"
      >
      <div class="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-violet-500"></div>
      <span class="ml-3 text-sm font-medium text-gray-300">{{ label }}</span>
    </label>
  </div>
</template>
