<script setup lang="ts">
import 'mathlive';
import 'mathlive/static.css';
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { sanitizeLatex } from '../utils/sanitizeLatex';

const props = defineProps<{
  visible: boolean;
}>();

const emit = defineEmits<{
  close: [];
  insert: [value: string];
}>();

function useTimedState<T>(initial: T, delay = 1200) {
  const state = ref(initial);
  let timer: number | null = null;

  function set(value: T) {
    state.value = value;
    if (timer) window.clearTimeout(timer);
    timer = window.setTimeout(() => {
      state.value = initial;
      timer = null;
    }, delay);
  }

  function clear() {
    if (timer) window.clearTimeout(timer);
    timer = null;
  }

  return { state, set, clear };
}

const rawLatex = ref('');
const displayMode = ref(false);
const mathFieldRef = ref<MathfieldElement | null>(null);
const { state: feedback, set: setFeedback, clear: clearFeedback } = useTimedState('', 1200);
const shouldResetOnClose = true;
let isInternalUpdate = false;

const wrappedLatex = computed(() => {
  const value = rawLatex.value.trim();
  if (!value) return '';
  return displayMode.value ? `$$${value}$$` : `$${value}$`;
});

function close() {
  emit('close');
}

function handleMathInput(event: Event) {
  if (isInternalUpdate) return;
  const field = event.target as MathfieldElement;
  rawLatex.value = field.value;
}

function getSanitizedWrappedLatex() {
  const value = sanitizeLatex(rawLatex.value).trim();
  if (!value) return '';
  return displayMode.value ? `$$${value}$$` : `$${value}$`;
}

async function copyLatex() {
  const output = getSanitizedWrappedLatex();
  if (!output) return;
  await navigator.clipboard.writeText(output);
  setFeedback('Скопировано');
}

function insertLatex() {
  const output = getSanitizedWrappedLatex();
  if (!output) return;
  emit('insert', output);
}

function onWindowKeydown(event: KeyboardEvent) {
  if (!props.visible) return;
  if (event.key === 'Escape') close();
}

async function focusMathField() {
  await customElements.whenDefined('math-field');
  const field = mathFieldRef.value;
  if (!field) return;
  field.focus();
  requestAnimationFrame(() => {
    window.mathVirtualKeyboard?.show();
  });
}

watch(rawLatex, (value) => {
  const field = mathFieldRef.value;
  if (!field || field.value === value) return;
  isInternalUpdate = true;
  field.value = value;
  queueMicrotask(() => {
    isInternalUpdate = false;
  });
});

watch(
  () => props.visible,
  async (next) => {
    if (!next) {
      if (shouldResetOnClose) {
        rawLatex.value = '';
        displayMode.value = false;
      }
      clearFeedback();
      return;
    }
    await focusMathField();
  }
);

onMounted(() => {
  window.addEventListener('keydown', onWindowKeydown);
});

onBeforeUnmount(() => {
  window.removeEventListener('keydown', onWindowKeydown);
  window.mathVirtualKeyboard?.hide();
  clearFeedback();
});
</script>

<template>
  <Teleport to="body">
    <div
      v-if="visible"
      class="pointer-events-none fixed inset-0 z-[1200] flex items-start justify-center pt-20 p-4"
    >
      <div class="pointer-events-auto w-full max-w-2xl rounded-lg border border-zinc-700 bg-zinc-900 p-4 shadow-xl">
        <div class="mb-3 flex items-center justify-between">
          <h3 class="text-sm font-medium text-zinc-100">Конструктор формулы</h3>
          <button
            type="button"
            class="rounded px-2 py-1 text-xs text-zinc-400 hover:bg-zinc-800 hover:text-zinc-100"
            @click="close"
          >
            Закрыть
          </button>
        </div>
        <div class="space-y-3">
          <math-field
            ref="mathFieldRef"
            class="math-builder-field w-full min-h-40 rounded border border-zinc-700 bg-zinc-950 px-3 py-3 text-zinc-100"
            virtual-keyboard-mode="manual"
            @input="handleMathInput"
          />
          <div class="flex items-center justify-between gap-3">
            <label class="flex items-center gap-2 text-xs text-zinc-300">
              <input
                v-model="displayMode"
                type="checkbox"
                class="rounded border-zinc-600 bg-zinc-900 text-emerald-500"
              />
              Копировать как block ($$...$$)
            </label>
            <button
              type="button"
              class="rounded bg-emerald-600 px-3 py-1.5 text-sm text-white hover:bg-emerald-500 disabled:cursor-not-allowed disabled:opacity-60"
              :disabled="!wrappedLatex"
              @click="copyLatex"
            >
              Скопировать LaTeX
            </button>
            <button
              type="button"
              class="rounded bg-indigo-600 px-3 py-1.5 text-sm text-white hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-60"
              :disabled="!wrappedLatex"
              @click="insertLatex"
            >
              Вставить
            </button>
          </div>
          <div class="rounded border border-zinc-800 bg-zinc-950/60 px-2 py-1 text-xs text-zinc-400 font-mono break-all">
            {{ wrappedLatex || 'Формула для вставки появится здесь' }}
          </div>
          <p class="min-h-5 text-xs text-emerald-400">{{ feedback }}</p>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
:global(math-virtual-keyboard) {
  z-index: 1400 !important;
}

:global(.math-builder-field) {
  font-size: 1.75rem;
}
</style>
