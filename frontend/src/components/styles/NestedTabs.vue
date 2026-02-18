<script setup lang="ts">
import { ref, watch } from 'vue';
import type { TabLeaf, TabGroup, TabNode } from '../../config/styleFields';
import type { ElementType } from '../../types/api';
import type { StyleDataMap } from '../../composables/useStyleEditor';
import StyleForm from './StyleForm.vue';

const props = defineProps<{
  nodes: TabNode[];
  depth?: number;
  styles: StyleDataMap;
}>();

const emit = defineEmits<{
  fieldChange: [elementKey: ElementType, field: string, value: unknown];
}>();

const currentDepth = props.depth ?? 0;
const activeIndex = ref(0);

watch(
  () => props.nodes,
  () => {
    if (activeIndex.value >= props.nodes.length) {
      activeIndex.value = 0;
    }
  },
);

function forwardFieldChange(elementKey: ElementType, field: string, value: unknown) {
  emit('fieldChange', elementKey, field, value);
}
</script>

<template>
  <div class="nested-tabs" :class="`depth-${currentDepth}`">
    <div class="tab-bar" :class="`tab-bar-depth-${currentDepth}`">
      <button
        v-for="(node, idx) in nodes"
        :key="idx"
        type="button"
        class="tab-btn"
        :class="{ active: activeIndex === idx }"
        @click="activeIndex = idx"
      >
        {{ node.label }}
      </button>
    </div>

    <div class="tab-content">
      <template v-if="nodes[activeIndex]">
        <!-- Leaf: render style form -->
        <StyleForm
          v-if="nodes[activeIndex]?.kind === 'leaf'"
          :element-key="(nodes[activeIndex] as TabLeaf).elementKey"
          :fields="(nodes[activeIndex] as TabLeaf).fields"
          :values="styles[(nodes[activeIndex] as TabLeaf).elementKey] ?? {}"
          :has-text-override="(nodes[activeIndex] as TabLeaf).hasTextOverride"
          @field-change="forwardFieldChange"
        />

        <!-- Group: recurse -->
        <NestedTabs
          v-else
          :nodes="(nodes[activeIndex] as TabGroup).children ?? []"
          :depth="currentDepth + 1"
          :styles="styles"
          @field-change="forwardFieldChange"
        />
      </template>
    </div>
  </div>
</template>

<style scoped>
.tab-bar {
  display: flex;
  gap: 0.25rem;
  padding: 0.5rem 1rem 0;
  border-bottom: 1px solid #3f3f46;
  overflow-x: auto;
  scrollbar-width: thin;
}

/* Level 0: pill-style tabs */
.tab-bar-depth-0 {
  gap: 0.375rem;
  padding: 0.75rem 1.25rem 0.75rem;
  border-bottom: 1px solid #3f3f46;
  background: #27272a;
}

.tab-bar-depth-0 .tab-btn {
  padding: 0.4rem 1rem;
  border-radius: 9999px;
  background: transparent;
  border: 1px solid #3f3f46;
  color: #a1a1aa;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.15s;
  white-space: nowrap;
}

.tab-bar-depth-0 .tab-btn:hover {
  background: #3f3f46;
  color: #fafafa;
}

.tab-bar-depth-0 .tab-btn.active {
  background: #3b82f6;
  border-color: #3b82f6;
  color: #fff;
}

/* Level 1+: underline-style tabs */
.tab-bar:not(.tab-bar-depth-0) {
  background: transparent;
  padding: 0.375rem 1.25rem 0;
}

.tab-bar:not(.tab-bar-depth-0) .tab-btn {
  padding: 0.375rem 0.75rem;
  border: none;
  border-bottom: 2px solid transparent;
  border-radius: 0;
  background: transparent;
  color: #a1a1aa;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.15s;
  white-space: nowrap;
}

.tab-bar:not(.tab-bar-depth-0) .tab-btn:hover {
  color: #fafafa;
}

.tab-bar:not(.tab-bar-depth-0) .tab-btn.active {
  color: #3b82f6;
  border-bottom-color: #3b82f6;
}

.tab-content {
  min-height: 0;
}
</style>
