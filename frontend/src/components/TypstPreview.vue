<script setup lang="ts">
import { watch, ref, computed, nextTick, onMounted, onUnmounted } from 'vue';
import { usePreviewStore } from '../stores/preview';
import { $typst } from '@myriaddreamin/typst.ts/contrib/snippet';

const previewStore = usePreviewStore();
const canvasContainerRef = ref<HTMLElement | null>(null);
const scrollAreaRef = ref<HTMLElement | null>(null);

const ZOOM_MIN = 0.25;
const ZOOM_MAX = 2;
const ZOOM_STEP = 0.1;
const zoom = ref(1);

function handleWheel(e: WheelEvent) {
  if (!e.ctrlKey && !e.metaKey) return;
  e.preventDefault();
  const delta = e.deltaY > 0 ? -ZOOM_STEP : ZOOM_STEP;
  zoom.value = Math.min(ZOOM_MAX, Math.max(ZOOM_MIN, zoom.value + delta));
}

onMounted(() => {
  scrollAreaRef.value?.addEventListener('wheel', handleWheel, { passive: false });
});
onUnmounted(() => {
  scrollAreaRef.value?.removeEventListener('wheel', handleWheel);
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

  try {
    await $typst.canvas(container, {
      mainContent,
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
        :style="{ transform: `scale(${zoom})`, transformOrigin: 'top center' }"
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
