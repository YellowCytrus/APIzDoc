<script setup lang="ts">
import { computed } from 'vue';
import type { FieldDef } from '../../config/styleFields';

const props = defineProps<{
  field: FieldDef;
  modelValue: unknown;
}>();

const emit = defineEmits<{
  'update:modelValue': [value: unknown];
}>();

const numValue = computed(() => Number(props.modelValue) || 0);

const markers = computed<string[]>(() => {
  const val = props.modelValue;
  if (Array.isArray(val)) return val as string[];
  return ['', '', ''];
});

function updateMarker(index: number, value: string) {
  const updated = [...markers.value];
  updated[index] = value;
  emit('update:modelValue', updated);
}
</script>

<template>
  <div class="style-field">
    <label class="field-label">{{ field.label }}</label>

    <!-- Number: slider + input -->
    <div v-if="field.type === 'number'" class="field-number">
      <input
        type="range"
        :min="field.min ?? 0"
        :max="field.max ?? 100"
        :step="field.step ?? 1"
        :value="numValue"
        class="field-slider"
        @input="emit('update:modelValue', Number(($event.target as HTMLInputElement).value))"
      />
      <input
        type="number"
        :min="field.min"
        :max="field.max"
        :step="field.step"
        :value="numValue"
        class="field-num-input"
        @input="emit('update:modelValue', Number(($event.target as HTMLInputElement).value))"
      />
      <span v-if="field.unit" class="field-unit">{{ field.unit }}</span>
    </div>

    <!-- Boolean: toggle switch -->
    <div v-else-if="field.type === 'boolean'" class="field-toggle-wrap">
      <button
        type="button"
        class="field-toggle"
        :class="{ active: !!modelValue }"
        @click="emit('update:modelValue', !modelValue)"
      >
        <span class="toggle-thumb" />
      </button>
      <span class="toggle-label">{{ modelValue ? 'Да' : 'Нет' }}</span>
    </div>

    <!-- String: text input -->
    <div v-else-if="field.type === 'string'" class="field-string-wrap">
      <input
        type="text"
        :value="modelValue ?? ''"
        :placeholder="field.placeholder"
        class="field-text"
        @input="emit('update:modelValue', ($event.target as HTMLInputElement).value)"
      />
      <p v-if="field.hint" class="field-hint">{{ field.hint }}</p>
    </div>

    <!-- Select: pill-style selector -->
    <div v-else-if="field.type === 'select' && field.options" class="field-pills">
      <button
        v-for="opt in field.options"
        :key="opt.value"
        type="button"
        class="pill"
        :class="{ active: modelValue === opt.value }"
        @click="emit('update:modelValue', opt.value)"
      >
        {{ opt.label }}
      </button>
    </div>

    <!-- Markers: 3 text inputs -->
    <div v-else-if="field.type === 'markers'" class="field-markers">
      <div v-for="(_, i) in 3" :key="i" class="marker-row">
        <span class="marker-level">{{ i + 1 }}.</span>
        <input
          type="text"
          :value="markers[i] ?? ''"
          class="marker-input"
          :placeholder="`Уровень ${i + 1}`"
          @input="updateMarker(i, ($event.target as HTMLInputElement).value)"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.style-field {
  margin-bottom: 1rem;
}

.field-label {
  display: block;
  font-size: 0.8rem;
  color: #a1a1aa;
  margin-bottom: 0.375rem;
  font-weight: 500;
}

.field-number {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.field-slider {
  flex: 1;
  height: 6px;
  accent-color: #3b82f6;
  cursor: pointer;
}

.field-num-input {
  width: 5rem;
  background: #3f3f46;
  border: 1px solid #52525b;
  border-radius: 0.375rem;
  color: #fafafa;
  padding: 0.25rem 0.5rem;
  font-size: 0.8rem;
  text-align: right;
}

.field-num-input:focus {
  outline: none;
  border-color: #3b82f6;
}

.field-unit {
  font-size: 0.75rem;
  color: #71717a;
  min-width: 1.5rem;
}

.field-toggle-wrap {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.field-toggle {
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

.field-toggle.active {
  background: #3b82f6;
  border-color: #3b82f6;
}

.toggle-thumb {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 1rem;
  height: 1rem;
  background: #fafafa;
  border-radius: 9999px;
  transition: transform 0.2s;
}

.field-toggle.active .toggle-thumb {
  transform: translateX(1.1rem);
}

.toggle-label {
  font-size: 0.8rem;
  color: #a1a1aa;
}

.field-text {
  width: 100%;
  background: #3f3f46;
  border: 1px solid #52525b;
  border-radius: 0.375rem;
  color: #fafafa;
  padding: 0.375rem 0.625rem;
  font-size: 0.875rem;
}

.field-text:focus {
  outline: none;
  border-color: #3b82f6;
}

.field-string-wrap {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.field-hint {
  margin: 0;
  font-size: 0.75rem;
  color: #71717a;
  line-height: 1.3;
}

.field-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 0.375rem;
}

.pill {
  padding: 0.3rem 0.75rem;
  border-radius: 9999px;
  background: #3f3f46;
  border: 1px solid #52525b;
  color: #a1a1aa;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.15s;
}

.pill:hover {
  background: #52525b;
  color: #fafafa;
}

.pill.active {
  background: #3b82f6;
  border-color: #3b82f6;
  color: #fff;
}

.field-markers {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.marker-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.marker-level {
  font-size: 0.8rem;
  color: #71717a;
  min-width: 1.25rem;
}

.marker-input {
  flex: 1;
  background: #3f3f46;
  border: 1px solid #52525b;
  border-radius: 0.375rem;
  color: #fafafa;
  padding: 0.3rem 0.5rem;
  font-size: 0.8rem;
}

.marker-input:focus {
  outline: none;
  border-color: #3b82f6;
}
</style>
