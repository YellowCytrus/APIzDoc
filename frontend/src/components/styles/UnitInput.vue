<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import type { Context, Unit } from '../../utils/unitConversion';
import { fromMm, toMm } from '../../utils/unitConversion';

const props = defineProps<{
  valueMm: number;
  unit: Unit;
  allowedUnits: Unit[];
  minMm?: number;
  maxMm?: number;
  stepMm?: number;
  context?: Context;
}>();

const emit = defineEmits<{
  preview: [valueMm: number];
  commit: [valueMm: number];
  unitChange: [unit: Unit];
}>();

const hasContextError = computed(() => {
  if (props.unit !== 'em') return false;
  return !props.context || !Number.isFinite(props.context.fontSizeMm) || props.context.fontSizeMm <= 0;
});

function safeFromMm(valueMm: number): number | null {
  try {
    return fromMm(valueMm, props.unit, props.context);
  } catch {
    return null;
  }
}

const lastValidDisplayValue = ref(0);

watch(
  () => [props.valueMm, props.unit, props.context] as const,
  () => {
    const converted = safeFromMm(props.valueMm);
    if (converted != null) {
      lastValidDisplayValue.value = converted;
    }
  },
  { immediate: true }
);

const displayValue = computed(() => {
  const converted = safeFromMm(props.valueMm);
  return converted ?? lastValidDisplayValue.value;
});

const displayMin = computed(() => {
  if (props.minMm == null) return undefined;
  try {
    return fromMm(props.minMm, props.unit, props.context);
  } catch {
    return undefined;
  }
});

const displayMax = computed(() => {
  if (props.maxMm == null) return undefined;
  try {
    return fromMm(props.maxMm, props.unit, props.context);
  } catch {
    return undefined;
  }
});

const displayStep = computed(() => {
  if (props.stepMm == null) return undefined;
  try {
    return fromMm(props.stepMm, props.unit, props.context);
  } catch {
    return undefined;
  }
});

function parseMm(rawValue: string): number | null {
  if (hasContextError.value) return null;
  const parsed = Number(rawValue);
  if (!Number.isFinite(parsed)) return null;
  try {
    return toMm(parsed, props.unit, props.context);
  } catch {
    // Keep current value when em context is missing.
    return null;
  }
}

function emitPreview(rawValue: string) {
  const valueMm = parseMm(rawValue);
  if (valueMm == null) return;
  emit('preview', valueMm);
}

function emitCommit(rawValue: string) {
  const valueMm = parseMm(rawValue);
  if (valueMm == null) return;
  emit('commit', valueMm);
}
</script>

<template>
  <div class="unit-input">
    <input
      type="range"
      :min="displayMin ?? 0"
      :max="displayMax ?? 100"
      :step="displayStep ?? 1"
      :value="displayValue"
      class="field-slider"
      :disabled="hasContextError"
      :title="hasContextError ? 'Для em нужен корректный размер шрифта. Выберите другую единицу или задайте контекст.' : undefined"
      @input="emitPreview(($event.target as HTMLInputElement).value)"
      @change="emitCommit(($event.target as HTMLInputElement).value)"
    />
    <input
      type="number"
      :min="displayMin"
      :max="displayMax"
      :step="displayStep"
      :value="displayValue"
      class="field-num-input"
      :disabled="hasContextError"
      :title="hasContextError ? 'Для em нужен корректный размер шрифта. Выберите другую единицу или задайте контекст.' : undefined"
      @input="emitPreview(($event.target as HTMLInputElement).value)"
      @change="emitCommit(($event.target as HTMLInputElement).value)"
      @blur="emitCommit(($event.target as HTMLInputElement).value)"
    />
    <select
      class="unit-select"
      :value="unit"
      @change="emit('unitChange', ($event.target as HTMLSelectElement).value as Unit)"
    >
      <option v-for="opt in allowedUnits" :key="opt" :value="opt">{{ opt }}</option>
    </select>
  </div>
  <p v-if="hasContextError" class="unit-error">Для единицы em нужен корректный размер шрифта.</p>
</template>

<style scoped>
.unit-input {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.unit-select {
  background: #3f3f46;
  border: 1px solid #52525b;
  border-radius: 0.375rem;
  color: #fafafa;
  padding: 0.25rem 0.4rem;
  font-size: 0.8rem;
}

.unit-error {
  margin: 0.25rem 0 0;
  color: #f87171;
  font-size: 0.75rem;
}
</style>
