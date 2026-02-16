<script setup lang="ts">
const emit = defineEmits<{
  insert: [text: string];
}>();

function insertHeading() {
  emit('insert', '# ');
}

function insertMath() {
  emit('insert', '$ $');
}
</script>

<template>
  <div
    class="left-toolbar w-[60px] hover:w-[120px] flex flex-col items-center gap-2 py-4 bg-zinc-800 border-r border-zinc-700 transition-all duration-200 ease-out"
  >
    <button
      type="button"
      class="toolbar-btn px-3 py-2 rounded hover:bg-zinc-700 transition-colors"
      title="Вставить заголовок"
      @click="insertHeading"
    >
      <span class="font-mono text-lg">#</span>
    </button>
    <button
      type="button"
      class="toolbar-btn px-3 py-2 rounded hover:bg-zinc-700 transition-colors"
      title="Вставить формулу"
      @click="insertMath"
    >
      <span class="font-mono text-lg">$</span>
    </button>
  </div>
</template>
