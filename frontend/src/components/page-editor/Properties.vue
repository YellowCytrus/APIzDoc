<template>
  <div class="properties-panel">
    <h3>Свойства</h3>
    <template v-if="selected">
      <div v-if="selected.type === 'text'" class="form">
        <label>Текст</label>
        <input v-model="textContent" @input="updateTextContent" />
      </div>
      <div v-else-if="selected.type === 'variable'" class="form">
        <label>Имя переменной</label>
        <input v-model="varName" @input="updateVarName" />
        <label>Значение</label>
        <input v-model="varValue" @input="updateVarValue" />
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
import { ref, watch } from "vue";
import { storeToRefs } from "pinia";
import { usePageEditorStore } from "../../stores/pageEditor";

const store = usePageEditorStore();
const { selected, variables } = storeToRefs(store);

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
.form input {
  padding: 0.35rem;
  background: #27272a;
  border: 1px solid #3f3f46;
  color: #e4e4e7;
  border-radius: 4px;
}
.hint {
  font-size: 0.85rem;
  color: #71717a;
  margin: 0 0 1rem 0;
}
</style>
