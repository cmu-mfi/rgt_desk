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
  <div class="flex items-center justify-between gap-3 py-2">
    <label class="text-[13px] font-medium text-zinc-300">{{ label }}</label>
    <label class="relative inline-flex shrink-0 cursor-pointer">
      <input
        type="checkbox"
        :checked="modelValue"
        @change="$emit('update:modelValue', $event.target.checked)"
        class="sr-only peer"
      >
      <div
        class="w-10 h-5 bg-zinc-900 border border-hairline
               after:absolute after:top-[2px] after:left-[2px] after:w-3.5 after:h-3.5
               after:bg-zinc-500 after:transition-transform after:duration-150
               peer-checked:border-accent/60 peer-checked:bg-accent/15 peer-checked:after:bg-accent
               peer-checked:after:translate-x-[22px]
               peer-focus-visible:ring-1 peer-focus-visible:ring-accent/50"
      ></div>
    </label>
  </div>
</template>
