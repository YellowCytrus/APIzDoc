<script setup lang="ts">
import { ref } from 'vue';
import { API_BASE } from '../config';

const emit = defineEmits<{
  insert: [text: string];
}>();

const fileInputRef = ref<HTMLInputElement | null>(null);

function insertHeading() {
  emit('insert', '# ');
}

function insertMath() {
  emit('insert', '$ $');
}

function triggerImageInput() {
  fileInputRef.value?.click();
}

async function onImageSelected(e: Event) {
  const input = e.target as HTMLInputElement;
  const file = input.files?.[0];
  input.value = '';
  if (!file) return;
  try {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/upload-image`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(typeof err.detail === 'string' ? err.detail : 'Upload failed');
    }
    const { path } = await res.json();
    emit('insert', `![подпись к рисунку](${path})`);
  } catch (err) {
    console.error('Image upload failed:', err);
  }
}
</script>

<template>
  <div
    class="left-toolbar w-[60px] hover:w-[120px] flex flex-col items-center gap-2 py-4 bg-zinc-800 border-r border-zinc-700 transition-all duration-200 ease-out"
  >
    <input
      ref="fileInputRef"
      type="file"
      accept="image/png,image/jpeg,image/gif,image/webp,image/svg+xml"
      class="hidden"
      @change="onImageSelected"
    />
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
    <button
      type="button"
      class="toolbar-btn px-3 py-2 rounded hover:bg-zinc-700 transition-colors"
      title="Вставить картинку"
      @click="triggerImageInput"
    >
      <span class="text-lg">🖼</span>
    </button>
  </div>
</template>
