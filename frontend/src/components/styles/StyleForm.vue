<script setup lang="ts">
import type { FieldDef } from '../../config/styleFields';
import type { ElementType } from '../../types/api';
import StyleFieldInput from './StyleFieldInput.vue';

const props = defineProps<{
  elementKey: ElementType;
  fields: FieldDef[];
  values: Record<string, unknown>;
}>();

const emit = defineEmits<{
  fieldChange: [elementKey: ElementType, field: string, value: unknown];
}>();

function onFieldUpdate(fieldKey: string, value: unknown) {
  emit('fieldChange', props.elementKey, fieldKey, value);
}
</script>

<template>
  <div class="style-form">
    <StyleFieldInput
      v-for="field in fields"
      :key="field.key"
      :field="field"
      :model-value="values[field.key]"
      @update:model-value="onFieldUpdate(field.key, $event)"
    />
  </div>
</template>

<style scoped>
.style-form {
  padding: 1.25rem;
}
</style>
