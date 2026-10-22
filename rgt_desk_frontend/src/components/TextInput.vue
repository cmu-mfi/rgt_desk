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
  maxLength: {
    type: Number,
    default: 30
  }
});

defineEmits(['update:modelValue']);
</script>

<template>
  <div class="flex items-center justify-between gap-3 py-2">
    <label class="text-[16px] font-medium text-zinc-300 whitespace-nowrap">
      {{ label }}
    </label>
    <input
      type="text"
      :value="modelValue"
      :maxlength="maxLength"
      @input="$emit('update:modelValue', $event.target.value)"
      class="w-full max-w-[160px] min-w-0 bg-zinc-900 border border-hairline text-zinc-200 font-mono text-[15px] px-2 py-1.5 outline-none focus:border-accent transition-colors"
    />
  </div>
</template>
