<script setup lang="ts">
import { watch, ref, computed, nextTick, onMounted, onUnmounted } from 'vue';
import { usePreviewStore } from '../stores/preview';
import { $typst } from '@myriaddreamin/typst.ts/contrib/snippet';
import { API_BASE } from '../config';
import Panzoom from '@panzoom/panzoom'

const previewStore = usePreviewStore();

/** Извлекает пути/URL изображений из typst: image("path_or_url") */
function extractImageRefs(typstSource: string): string[] {
  const matches = typstSource.matchAll(/image\s*\(\s*"([^"]+)"/g);
  const refs: string[] = [];
  for (const m of matches) {
    const p = m[1];
    if (p) refs.push(p);
  }
  return [...new Set(refs)];
}

/** Загружает изображения в shadow FS и возвращает typst с подставленными путями для URL нашего API. */
async function registerImagesForPreview(typstSource: string): Promise<string> {
  await $typst.resetShadow();
  const refs = extractImageRefs(typstSource);
  let modifiedSource = typstSource;
  const apiBaseNorm = API_BASE.replace(/\/$/, '');

  for (const ref of refs) {
    if (ref.startsWith('http://') || ref.startsWith('https://')) {
      if (!ref.startsWith(apiBaseNorm + '/image-assets/') || !ref.endsWith('/file')) continue;
      try {
        const res = await fetch(ref);
        if (!res.ok) continue;
        const buf = await res.arrayBuffer();
        const pathname = new URL(ref).pathname;
        const shadowPath = pathname.startsWith('/') ? pathname : '/' + pathname;
        await $typst.mapShadow(shadowPath, new Uint8Array(buf));
        modifiedSource = modifiedSource.split(ref).join(shadowPath);
      } catch {
        // пропускаем
      }
      continue;
    }
    if (!ref.startsWith('images/') || ref.includes('..')) continue;
    const filename = ref.replace(/^images\//, '');
    try {
      const res = await fetch(`${API_BASE}/images/${filename}`);
      if (!res.ok) continue;
      const buf = await res.arrayBuffer();
      await $typst.mapShadow(`/${ref}`, new Uint8Array(buf));
    } catch {
      // пропускаем
    }
  }
  return modifiedSource;
}
const canvasContainerRef = ref<HTMLElement | null>(null);
const scrollAreaRef = ref<HTMLElement | null>(null);

onMounted(() => {
  const elem = canvasContainerRef.value
  const panzoom = Panzoom(elem, {
    maxScale: 5,
    cursor: 'grab'
  })
  panzoom.pan(10, 10)
  panzoom.zoom(1, { animate: true })
  elem.parentElement.addEventListener('wheel', panzoom.zoomWithWheel)
  elem.addEventListener('panzoomstart', () => {
    panzoom.setOptions({ cursor: 'grabbing' })
  })

  elem.addEventListener('panzoomend', () => {
    panzoom.setOptions({ cursor: 'grab' })
  })
  elem.style.transform = 'scale(1)'
});
onUnmounted(() => {
  const elem = canvasContainerRef.value
  elem.parentElement.removeEventListener('wheel', panzoom.zoomWithWheel);
});

/** Compile typst source to canvas (paged rendering with native page separation) */
async function compileToCanvas(mainContent: string) {
  if (!mainContent.trim()) {
    previewStore.setError(null);
    previewStore.setCompiling(false);
    return;
  }

  previewStore.setCompiling(true);
  previewStore.setError(null);

  // Wait for container to be in DOM (shown when we have typstSource)
  await nextTick();

  const container = canvasContainerRef.value;
  if (!container) {
    previewStore.setCompiling(false);
    return;
  }

  const mainWithImages = await registerImagesForPreview(mainContent);

  try {
    await $typst.addSource('/main.typ', mainWithImages);
    await $typst.canvas(container, {
      mainFilePath: '/main.typ',
      root: '/',
      backgroundColor: '#ffffff',
      pixelPerPt: 2.5,
    });
    previewStore.setError(null);
  } catch (e) {
    previewStore.setError((e as Error).message ?? String(e));
  } finally {
    previewStore.setCompiling(false);
  }
}

watch(
  () => previewStore.typstSource,
  (source) => {
    if (!source) {
      previewStore.setError(null);
      previewStore.setCompiling(false);
      return;
    }
    compileToCanvas(source);
  },
  { immediate: true }
);

const isEmpty = computed(() => !previewStore.typstSource?.trim());
const showEmpty = computed(
  () => isEmpty.value && !previewStore.compiling && !previewStore.error
);
const showLoading = computed(() => previewStore.compiling);
const showError = computed(() => previewStore.error && !previewStore.compiling);
/** Container must be visible when canvas renders (needs offsetWidth). Hide when error. */
const showCanvasContainer = computed(
  () => !isEmpty.value && !previewStore.error
);
</script>

<template>
  <div class="typst-preview h-full flex flex-col bg-zinc-100 relative">
    <div
      ref="scrollAreaRef"
      class="flex-1 overflow-auto p-6 flex justify-center min-h-0 relative"
    >
      <!-- Empty state -->
      <div
        v-if="showEmpty"
        class="flex flex-col items-center justify-center text-zinc-400 text-sm h-full min-h-[200px]"
      >
        <span>Выберите профиль и введите текст для превью</span>
      </div>

      <!-- Error state (when we have content but compile failed) -->
      <div
        v-else-if="showError"
        class="w-full max-w-xl bg-red-50 border border-red-200 rounded-lg p-4 text-red-800 text-sm font-mono whitespace-pre-wrap"
      >
        {{ previewStore.error }}
      </div>

      <!-- Canvas container: typst.ts renders each page as separate element (typst-page) -->
      <div
        v-show="showCanvasContainer"
        ref="canvasContainerRef"
        class="typst-preview-pages"

      />

      <!-- Loading overlay (container visible underneath for correct layout) -->
      <div
        v-if="showLoading"
        class="absolute inset-0 flex flex-col items-center justify-center bg-zinc-100/80 text-zinc-500 text-sm"
      >
        <div class="animate-spin rounded-full h-8 w-8 border-2 border-zinc-400 border-t-transparent mb-3" />
        <span>Компиляция...</span>
      </div>
    </div>

    <!-- Zoom hint — вне области скролла, привязан к низу панели превью -->
    <div
      v-if="showCanvasContainer && !showLoading"
      class="absolute bottom-2 left-1/2 -translate-x-1/2 text-xs text-zinc-500 bg-zinc-200/80 px-2 py-1 rounded pointer-events-none z-10"
    >
      Ctrl + колесо — масштаб {{ Math.round(zoom * 100) }}%
    </div>
  </div>
</template>

<style scoped>
/* Container for paged document - typst.ts creates .typst-page per page */
.typst-preview-pages {
  min-width: min(100%, 595px);
  width: 100%;
  max-width: 100%;
}

/* Visual separation between pages - like typst.app */
.typst-preview-pages :deep(.typst-page) {
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 16px;
}
.typst-preview-pages :deep(.typst-page:last-child) {
  margin-bottom: 0;
}
</style>
