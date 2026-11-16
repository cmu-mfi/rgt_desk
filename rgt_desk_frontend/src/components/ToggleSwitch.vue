<script setup>
defineProps({ modelValue: { type: Boolean, required: true }, label: { type: String, required: true } });
defineEmits(['update:modelValue']);
</script>
<template>
  <label class="param-row toggle-row"><span class="param-label">{{ label }}</span><span class="relative inline-flex"><input class="sr-only" type="checkbox" role="switch" :checked="modelValue" @change="$emit('update:modelValue', $event.target.checked)" /><span class="switch" aria-hidden="true" /></span></label>
</template>
