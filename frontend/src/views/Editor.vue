<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { useFileDialog } from '@vueuse/core';
import EditorLayout from '../components/EditorLayout.vue';
import { useProfilesStore } from '../stores/profiles';
import { useEditorStore } from '../stores/editor';
import { usePreviewStore } from '../stores/preview';
import { usePandoc } from '../composables/usePandoc';
import { useFileSave } from '../composables/useFileSave';
import { API_BASE } from '../config';

interface TitlePageItem {
  id: number;
  name: string;
}

// TEMPORARY: built-in SFU STU title; remove this constant and the option below to disable
const SFU_STU_TITLE_PAGE_ID = -1;

const profilesStore = useProfilesStore();
const editorStore = useEditorStore();
const titlePages = ref<TitlePageItem[]>([]);
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

  const preamble = profilesStore.getCachedPreamble(profileId);
  const fullTypst = (preamble ?? '') + '\n' + typstBody;
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

  const content = editorStore.content?.trim() ?? '';
  if (!content) {
    alert('Документ пуст. Добавьте текст перед генерацией PDF.');
    return;
  }

  const formData = new FormData();
  const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' });
  const fileName = editorStore.currentFileName ?? 'document.md';
  formData.append('file', blob, fileName);

  const url = new URL(`${API_BASE}/profiles/${profileId}/generate-pdf`);
  if (editorStore.titlePageId != null) {
    url.searchParams.set('title_page_id', String(editorStore.titlePageId));
  }
  if (editorStore.titlePageId != null) {
    url.searchParams.set('title_page_id', String(editorStore.titlePageId));
  }

  try {
    const res = await fetch(url.toString(), {
      method: 'POST',
      body: formData,
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      const detail = typeof err.detail === 'string' ? err.detail : 'Не удалось сгенерировать PDF';
      alert(detail);
      return;
    }

    const pdfBlob = await res.blob();
    const pdfName = fileName.replace(/\.(md|markdown|txt)$/i, '.pdf');
    await saveFile(pdfBlob, pdfName);
  } catch (e) {
    alert((e as Error).message ?? 'Ошибка при генерации PDF');
  }
}

async function downloadTyp() {
  const profileId = profilesStore.currentId;
  if (!profileId) return;

  const content = editorStore.content?.trim() ?? '';
  if (!content) {
    alert('Документ пуст. Добавьте текст перед экспортом .typ.');
    return;
  }

  const formData = new FormData();
  const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' });
  const fileName = editorStore.currentFileName ?? 'document.md';
  formData.append('file', blob, fileName);

  const url = new URL(`${API_BASE}/profiles/${profileId}/export-typ`);
  if (editorStore.titlePageId != null) {
    url.searchParams.set('title_page_id', String(editorStore.titlePageId));
  }

  try {
    const res = await fetch(url.toString(), {
      method: 'POST',
      body: formData,
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      const detail = typeof err.detail === 'string' ? err.detail : 'Не удалось экспортировать .typ';
      alert(detail);
      return;
    }

    const text = await res.text();
    const typName = fileName.match(/\.(md|markdown|txt)$/i)
      ? fileName.replace(/\.(md|markdown|txt)$/i, '.typ')
      : (fileName || 'document') + '.typ';
    await saveFile(new Blob([text], { type: 'text/plain;charset=utf-8' }), typName);
  } catch (e) {
    alert((e as Error).message ?? 'Ошибка при экспорте .typ');
  }
}

onMounted(async () => {
  await profilesStore.fetchProfiles();
  if (profilesStore.currentId) {
    await profilesStore.loadProfileStyles(profilesStore.currentId);
  }
  try {
    const res = await fetch(`${API_BASE}/title-pages?limit=200`);
    if (res.ok) {
      const data = await res.json();
      titlePages.value = data.map((p: { id: number; name: string }) => ({ id: p.id, name: p.name }));
    }
  } catch {
    // ignore
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
      <div class="flex items-center gap-2">
        <label class="text-sm text-zinc-400">Титульник:</label>
        <select
          :value="editorStore.titlePageId ?? ''"
          class="rounded bg-zinc-700 px-2 py-1.5 text-sm min-w-[140px]"
          @change="editorStore.setTitlePageId(($event.target as HTMLSelectElement).value ? +(($event.target as HTMLSelectElement).value) : null)"
        >
          <option value="">Без титульника</option>
          <!-- TEMPORARY: SFU STU title; remove option and SFU_STU_TITLE_PAGE_ID to disable -->
          <option :value="SFU_STU_TITLE_PAGE_ID">СФУ СТУ</option>
          <option v-for="p in titlePages" :key="p.id" :value="p.id">
            {{ p.name }}
          </option>
        </select>
      </div>
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
      <button
        type="button"
        class="px-3 py-1.5 rounded bg-zinc-700 hover:bg-zinc-600 text-sm"
        :disabled="!profilesStore.currentId"
        @click="downloadTyp"
      >
        Экспортировать как .typ
      </button>
    </header>
    <main class="flex-1 min-h-0 overflow-hidden flex flex-col">
      <EditorLayout class="flex-1 min-h-0" />
    </main>
  </div>
</template>
