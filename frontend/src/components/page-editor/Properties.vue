<template>
  <div class="properties-panel">
    <h3>Свойства</h3>
    <template v-if="selected">
      <div v-if="selected.type === 'text'" class="form">
        <label>Текст</label>
        <input v-model="textContent" @input="updateTextContent" />
        <div class="text-style-section">
          <h4>Стиль текста</h4>
          <StyleFieldInput
            v-for="field in TEXT_OVERRIDE_FIELDS"
            :key="field.key"
            :field="field"
            :model-value="textStyleValues[field.key]"
            @update:model-value="(v) => updateTextStyle(field.key, v)"
          />
        </div>
      </div>
      <div v-else-if="selected.type === 'variable'" class="form">
        <label>Имя переменной</label>
        <input v-model="varName" @input="updateVarName" />
        <label>Значение</label>
        <input v-model="varValue" @input="updateVarValue" />
        <label>Выравнивание</label>
        <select
          :value="varAlign"
          @change="updateVarAlign(($event.target as HTMLSelectElement).value)"
        >
          <option v-for="opt in VARIABLE_ALIGN_OPTIONS" :key="opt.value" :value="opt.value">
            {{ opt.label }}
          </option>
        </select>
        <div class="text-style-section">
          <h4>Стиль текста</h4>
          <StyleFieldInput
            v-for="field in TEXT_OVERRIDE_FIELDS"
            :key="field.key"
            :field="field"
            :model-value="textStyleValues[field.key]"
            @update:model-value="(v) => updateTextStyle(field.key, v)"
          />
        </div>
      </div>
      <div v-else-if="selected.type === 'line'" class="form">
        <label>X1 (мм)</label>
        <input v-model.number="lineX1" type="number" step="0.1" @change="updateLine" />
        <label>Y1 (мм)</label>
        <input v-model.number="lineY1" type="number" step="0.1" @change="updateLine" />
        <label>X2 (мм)</label>
        <input v-model.number="lineX2" type="number" step="0.1" @change="updateLine" />
        <label>Y2 (мм)</label>
        <input v-model.number="lineY2" type="number" step="0.1" @change="updateLine" />
      </div>
    </template>
    <p v-else class="hint">Выберите элемент</p>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from "vue";
import { storeToRefs } from "pinia";
import { usePageEditorStore } from "../../stores/pageEditor";
import { TEXT_OVERRIDE_FIELDS, TITLE_TEXT_DEFAULTS, VARIABLE_ALIGN_OPTIONS } from "../../config/styleFields";
import StyleFieldInput from "../styles/StyleFieldInput.vue";

const store = usePageEditorStore();
const { selected, variables } = storeToRefs(store);

const textStyleValues = computed(() => {
  const el = selected.value;
  if (!el || (el.type !== "text" && el.type !== "variable")) return {};
  const ts = (el.text_style ?? {}) as Record<string, unknown>;
  return { ...TITLE_TEXT_DEFAULTS, ...ts };
});

const varAlign = computed(() => {
  const el = selected.value;
  if (el?.type !== "variable") return "left";
  return ((el.text_style as Record<string, unknown> | undefined)?.align as string) || "left";
});

const textContent = ref("");
const varName = ref("");
const varValue = ref("");
const lineX1 = ref(0);
const lineY1 = ref(0);
const lineX2 = ref(0);
const lineY2 = ref(0);

watch(
  selected,
  (el) => {
    if (!el) return;
    if (el.type === "text") {
      textContent.value = el.content;
    } else if (el.type === "variable") {
      varName.value = el.var_name;
      varValue.value = variables.value[el.var_name] ?? "";
    } else if (el.type === "line") {
      lineX1.value = el.x1_mm;
      lineY1.value = el.y1_mm;
      lineX2.value = el.x2_mm;
      lineY2.value = el.y2_mm;
    }
  },
  { immediate: true }
);

function updateTextContent() {
  if (selected.value?.type === "text")
    store.updateTextContent(selected.value.id, textContent.value);
}

function updateVarName() {
  if (selected.value?.type === "variable")
    store.updateVariableName(selected.value.id, varName.value);
}

function updateVarValue() {
  if (selected.value?.type === "variable")
    store.setVariableValue(selected.value.var_name, varValue.value);
}

function updateLine() {
  if (selected.value?.type === "line") {
    store.updateLineEndpoints(
      selected.value.id,
      lineX1.value,
      lineY1.value,
      lineX2.value,
      lineY2.value
    );
  }
}

function updateTextStyle(fieldKey: string, value: unknown) {
  const el = selected.value;
  if (!el || (el.type !== "text" && el.type !== "variable")) return;
  store.updateTextStyle(el.id, fieldKey, value);
}

function updateVarAlign(value: string) {
  const el = selected.value;
  if (el?.type === "variable") {
    store.updateTextStyle(el.id, "align", value);
  }
}
</script>

<style scoped>
.properties-panel {
  padding: 0.75rem;
  background: #18181b;
  color: #e4e4e7;
}
.properties-panel h3 {
  margin: 0 0 0.75rem 0;
  font-size: 0.9rem;
  color: #a1a1aa;
}
.form {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  margin-bottom: 1rem;
}
.form label {
  font-size: 0.8rem;
  color: #a1a1aa;
}
.form input,
.form select {
  padding: 0.35rem;
  background: #27272a;
  border: 1px solid #3f3f46;
  color: #e4e4e7;
  border-radius: 4px;
}
.text-style-section {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #3f3f46;
}
.text-style-section h4 {
  font-size: 0.85rem;
  color: #a1a1aa;
  margin: 0 0 0.75rem 0;
}
.hint {
  font-size: 0.85rem;
  color: #71717a;
  margin: 0 0 1rem 0;
}
</style>
