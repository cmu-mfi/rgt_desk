<script setup>
import { ChevronDown } from '@lucide/vue';

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
    <label class="text-[13px] font-medium text-zinc-300 whitespace-nowrap">
      {{ label }}
    </label>
    <div class="relative w-full max-w-[160px]">
      <select
        :value="modelValue"
        @change="$emit('update:modelValue', $event.target.value)"
        class="w-full appearance-none bg-zinc-900 border border-hairline text-zinc-200 font-mono text-xs px-2 py-1.5 pr-7 outline-none focus:border-accent transition-colors cursor-pointer"
      >
        <option
          v-for="option in options"
          :key="option.value"
          :value="option.value"
        >
          {{ option.label }}
        </option>
      </select>
      <ChevronDown :size="12" class="absolute right-2 top-1/2 -translate-y-1/2 text-zinc-500 pointer-events-none" />
    </div>
  </div>
</template>
