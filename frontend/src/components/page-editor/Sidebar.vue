<template>
  <div class="sidebar">
    <section class="section">
      <h3>Страница</h3>
      <div class="paper-buttons">
        <button :class="{ active: paper.name === 'a4' }" @click="setPaperPreset('a4')">A4</button>
        <button :class="{ active: paper.name === 'a3' }" @click="setPaperPreset('a3')">A3</button>
      </div>
      <label class="margin-row">
        <span>Отступ (мм)</span>
        <input v-model.number="marginInput" type="number" min="0" step="1" @change="applyMargin" />
      </label>
    </section>
    <section class="section">
      <h3>Добавить элемент</h3>
      <button class="add-btn" @click="addText">Текст</button>
      <button class="add-btn" @click="addVariable">Переменная</button>
      <button class="add-btn" @click="addLine">Линия</button>
    </section>
    <section class="section">
      <label class="grid-row">
        <input :checked="showGrid" type="checkbox" @change="toggleGrid" />
        <span>Сетка</span>
      </label>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import { storeToRefs } from "pinia";
import { usePageEditorStore } from "../../stores/pageEditor";
import { PAPER_PRESETS } from "../../types/pageEditor";

const store = usePageEditorStore();
const { paper, showGrid } = storeToRefs(store);
const marginInput = ref(paper.value.margin);

watch(paper, (p) => { marginInput.value = p.margin; }, { deep: true });

function setPaperPreset(name: "a4" | "a3") {
  const p = PAPER_PRESETS[name];
  if (!p) return;
  store.setPaper(p);
  marginInput.value = p.margin;
}

function applyMargin() {
  const m = Math.max(0, marginInput.value ?? 0);
  store.setPaper({ ...paper.value, margin: m });
}

function addText() {
  store.addText(50, 50);
}

function addVariable() {
  store.addVariable(50, 50);
}

function addLine() {
  store.addLine(50, 50, 100, 80);
}

function toggleGrid() {
  store.toggleGrid();
}
</script>

<style scoped>
.sidebar {
  padding: 0.75rem;
  background: #18181b;
  color: #e4e4e7;
}
.section {
  margin-bottom: 1rem;
}
.section h3 {
  margin: 0 0 0.5rem 0;
  font-size: 0.9rem;
  color: #a1a1aa;
}
.paper-buttons {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}
.paper-buttons button {
  flex: 1;
  padding: 0.4rem 0.6rem;
  border: 1px solid #3f3f46;
  background: #27272a;
  color: #e4e4e7;
  cursor: pointer;
  border-radius: 4px;
}
.paper-buttons button:hover {
  background: #3f3f46;
}
.paper-buttons button.active {
  background: #3b82f6;
  border-color: #3b82f6;
  color: #fff;
}
.margin-row,
.grid-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
}
.margin-row input {
  width: 4rem;
  padding: 0.25rem;
  background: #27272a;
  border: 1px solid #3f3f46;
  color: #e4e4e7;
  border-radius: 4px;
}
.add-btn {
  display: block;
  width: 100%;
  padding: 0.5rem;
  margin-bottom: 0.4rem;
  border: 1px solid #3f3f46;
  background: #27272a;
  color: #e4e4e7;
  cursor: pointer;
  border-radius: 4px;
}
.add-btn:hover {
  background: #3f3f46;
}
</style>
