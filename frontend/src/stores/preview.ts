import { defineStore } from 'pinia';
import { ref } from 'vue';

export const usePreviewStore = defineStore('preview', () => {
  const typstSource = ref('');
  const error = ref<string | null>(null);
  const compiling = ref(false);

  function setTypstSource(s: string) {
    typstSource.value = s;
  }

  function setError(e: string | null) {
    error.value = e;
  }

  function setCompiling(b: boolean) {
    compiling.value = b;
  }

  function clear() {
    typstSource.value = '';
    error.value = null;
    compiling.value = false;
  }

  return {
    typstSource,
    error,
    compiling,
    setTypstSource,
    setError,
    setCompiling,
    clear,
  };
});
