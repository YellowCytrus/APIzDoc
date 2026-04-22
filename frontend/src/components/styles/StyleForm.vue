<script setup lang="ts">
import { computed } from 'vue';
import type { FieldDef } from '../../config/styleFields';
import { TEXT_OVERRIDE_FIELDS } from '../../config/styleFields';
import type { ElementType } from '../../types/api';
import StyleFieldInput from './StyleFieldInput.vue';
import type { Context, Unit } from '../../utils/unitConversion';

const props = defineProps<{
  elementKey: ElementType;
  fields: FieldDef[];
  values: Record<string, unknown>;
  hasTextOverride?: boolean;
  units: Record<string, Unit | undefined>;
  context?: Context;
}>();

const emit = defineEmits<{
  fieldChange: [elementKey: ElementType, field: string, value: unknown, persist?: boolean];
  unitChange: [fieldPath: string, unit: Unit];
}>();

const textOverrideEnabled = computed({
  get: () => props.values.text_override != null && typeof props.values.text_override === 'object',
  set: (enabled: boolean) => {
    emit('fieldChange', props.elementKey, 'text_override', enabled ? {} : null);
  },
});

const textOverrideValues = computed(() => {
  const to = props.values.text_override;
  if (to != null && typeof to === 'object') return to as Record<string, unknown>;
  return {};
});

function onFieldUpdate(fieldKey: string, value: unknown, persist = true) {
  emit('fieldChange', props.elementKey, fieldKey, value, persist);
}

function onTextOverrideFieldUpdate(fieldKey: string, value: unknown, persist = true) {
  const merged = { ...textOverrideValues.value, [fieldKey]: value };
  emit('fieldChange', props.elementKey, 'text_override', merged, persist);
}

function onUnitChange(fieldPath: string, unit: Unit) {
  emit('unitChange', fieldPath, unit);
}

function fieldUnitPath(fieldKey: string): string {
  return `${props.elementKey}.${fieldKey}`;
}

function textOverrideUnitPath(fieldKey: string): string {
  return `${props.elementKey}.text_override.${fieldKey}`;
}
</script>

<template>
  <div class="style-form">
    <StyleFieldInput
      v-for="field in fields"
      :key="field.key"
      :field="field"
      :model-value="values[field.key]"
      :display-unit="units[fieldUnitPath(field.key)]"
      :context="context"
      @update:model-value="(value, persist) => onFieldUpdate(field.key, value, persist)"
      @update:unit="onUnitChange(fieldUnitPath(field.key), $event)"
    />

    <!-- Кнопка/переключатель "Задать свой стиль для текста" -->
    <div v-if="hasTextOverride" class="text-override-section">
      <div class="text-override-toggle">
        <label class="field-label">Задать свой стиль для текста</label>
        <button
          type="button"
          class="field-toggle"
          :class="{ active: textOverrideEnabled }"
          @click="textOverrideEnabled = !textOverrideEnabled"
        >
          <span class="toggle-thumb" />
        </button>
      </div>

      <div v-if="textOverrideEnabled" class="text-override-fields">
        <StyleFieldInput
          v-for="field in TEXT_OVERRIDE_FIELDS"
          :key="field.key"
          :field="field"
          :model-value="textOverrideValues[field.key]"
          :display-unit="units[textOverrideUnitPath(field.key)]"
          :context="context"
          @update:model-value="(value, persist) => onTextOverrideFieldUpdate(field.key, value, persist)"
          @update:unit="onUnitChange(textOverrideUnitPath(field.key), $event)"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.style-form {
  padding: 1.25rem;
}

.text-override-section {
  margin-top: 1.5rem;
  padding-top: 1.25rem;
  border-top: 1px solid #3f3f46;
}

.text-override-toggle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.75rem;
}

.text-override-toggle .field-label {
  margin-bottom: 0;
}

.text-override-toggle .field-toggle {
  position: relative;
  width: 2.5rem;
  height: 1.375rem;
  background: #3f3f46;
  border: 1px solid #52525b;
  border-radius: 9999px;
  cursor: pointer;
  transition: background 0.2s, border-color 0.2s;
  padding: 0;
}

.text-override-toggle .field-toggle.active {
  background: #3b82f6;
  border-color: #3b82f6;
}

.text-override-toggle .toggle-thumb {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 1rem;
  height: 1rem;
  background: #fafafa;
  border-radius: 9999px;
  transition: transform 0.2s;
}

.text-override-toggle .field-toggle.active .toggle-thumb {
  transform: translateX(1.1rem);
}

.text-override-fields {
  margin-top: 0.75rem;
  padding-left: 0.5rem;
  border-left: 2px solid #3f3f46;
}
</style>
