<script setup lang="ts">
import { onMounted, watch } from 'vue';
import { useFileDialog } from '@vueuse/core';
import EditorLayout from '../components/EditorLayout.vue';
import { useProfilesStore } from '../stores/profiles';
import { useEditorStore } from '../stores/editor';
import { usePreviewStore } from '../stores/preview';
import { usePandoc } from '../composables/usePandoc';
import { useFileSave } from '../composables/useFileSave';
import { API_BASE } from '../config';

const profilesStore = useProfilesStore();
const editorStore = useEditorStore();
const previewStore = usePreviewStore();
const { convertMdToTypst } = usePandoc();
const { saveFile } = useFileSave();

const { open: openFileDialog, onChange: onFileChange } = useFileDialog({
  accept: '.md,.markdown,.txt',
  multiple: false,
});

onFileChange((files) => {
  const file = files?.item(0);
  if (!file) return;
  const reader = new FileReader();
  reader.onload = () => {
    editorStore.setContent(reader.result as string);
    editorStore.setCurrentFileName(file.name);
  };
  reader.readAsText(file);
});

async function compileMdToPreview() {
  const content = editorStore.content;
  const profileId = profilesStore.currentId;
  if (!profileId) {
    previewStore.setTypstSource('');
    previewStore.setError(null);
    return;
  }

  let typstBody = '';
  try {
    typstBody = await convertMdToTypst(content || '\n');
  } catch (e) {
    previewStore.setError((e as Error).message);
    return;
  }

  const PAGE_SETUP = '#set page(paper: "a4", margin: (x: 1in, y: 1in))\n';
  const preamble = profilesStore.getCachedPreamble(profileId);
  const fullTypst = PAGE_SETUP + (preamble ?? '') + '\n' + typstBody;
  previewStore.setTypstSource(fullTypst);
  previewStore.setError(null);
}

let debounceTimer: ReturnType<typeof setTimeout> | null = null;

function debouncedCompile() {
  if (debounceTimer) clearTimeout(debounceTimer);
  debounceTimer = setTimeout(compileMdToPreview, editorStore.debounceMs);
}

watch(
  () => editorStore.content,
  debouncedCompile,
  { immediate: true }
);

watch(
  () => [profilesStore.currentId, profilesStore.styleCache],
  debouncedCompile,
  { deep: true }
);

async function saveMarkdown() {
  const blob = new Blob([editorStore.content], { type: 'text/markdown;charset=utf-8' });
  const name = editorStore.currentFileName ?? 'document.md';
  await saveFile(blob, name);
}

async function downloadPdf() {
  const profileId = profilesStore.currentId;
  if (!profileId) return;

  const formData = new FormData();
  const blob = new Blob([editorStore.content], { type: 'text/markdown;charset=utf-8' });
  const fileName = editorStore.currentFileName ?? 'document.md';
  formData.append('file', blob, fileName);

  const res = await fetch(`${API_BASE}/profiles/${profileId}/generate-pdf`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail ?? 'Failed to generate PDF');
  }

  const pdfBlob = await res.blob();
  const pdfName = fileName.replace(/\.(md|markdown|txt)$/i, '.pdf');
  await saveFile(pdfBlob, pdfName);
}

onMounted(async () => {
  await profilesStore.fetchProfiles();
  if (profilesStore.currentId) {
    await profilesStore.loadProfileStyles(profilesStore.currentId);
  }
  debouncedCompile();
});
</script>

<template>
  <div class="editor-view h-screen flex flex-col">
    <header class="flex items-center gap-4 px-4 py-2 bg-zinc-800 border-b border-zinc-700">
      <button
        type="button"
        class="px-3 py-1.5 rounded bg-zinc-700 hover:bg-zinc-600 text-sm"
        @click="openFileDialog()"
      >
        Открыть
      </button>
      <button
        type="button"
        class="px-3 py-1.5 rounded bg-zinc-700 hover:bg-zinc-600 text-sm"
        @click="saveMarkdown"
      >
        Сохранить MD
      </button>
      <button
        type="button"
        class="px-3 py-1.5 rounded bg-zinc-700 hover:bg-zinc-600 text-sm"
        :disabled="!profilesStore.currentId"
        @click="downloadPdf"
      >
        Скачать PDF
      </button>
    </header>
    <main class="flex-1 min-h-0 overflow-hidden flex flex-col">
      <EditorLayout class="flex-1 min-h-0" />
    </main>
  </div>
</template>
