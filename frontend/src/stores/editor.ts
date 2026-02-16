import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useEditorStore = defineStore('editor', () => {
  const content = ref('');
  const currentFileName = ref<string | null>(null);
  const debounceMs = ref(300);

  function setContent(s: string) {
    content.value = s;
  }

  function setCurrentFileName(name: string | null) {
    currentFileName.value = name;
  }

  function setDebounceMs(ms: number) {
    debounceMs.value = Math.max(100, Math.min(1000, ms));
  }

  function clear() {
    content.value = '';
    currentFileName.value = null;
  }

  return {
    content,
    currentFileName,
    debounceMs,
    setContent,
    setCurrentFileName,
    setDebounceMs,
    clear,
  };
});
