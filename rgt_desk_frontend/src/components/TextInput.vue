<script setup>
import { useId } from 'vue';
defineProps({ modelValue: { type: [String, Number], required: true }, label: { type: String, required: true }, maxLength: { type: Number, default: 30 } });
defineEmits(['update:modelValue']);
const id = useId();
</script>
<template><div class="param-row"><label :for="id" class="param-label">{{ label }}</label><input :id="id" type="text" :value="modelValue" :maxlength="maxLength" @input="$emit('update:modelValue', $event.target.value)" class="field" placeholder="Optional name" /></div></template>
