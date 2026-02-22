<script setup lang="ts">
import { MdEditor as MdEditorComponent } from 'md-editor-v3';
import 'md-editor-v3/lib/style.css';
import { computed, ref } from 'vue';
import { useEditorStore } from '../stores/editor';

const props = defineProps<{
  modelValue?: string;
}>();

const emit = defineEmits<{
  'update:modelValue': [value: string];
}>();

const editorStore = useEditorStore();
const content = computed({
  get: () => props.modelValue ?? editorStore.content,
  set: (v) => {
    emit('update:modelValue', v);
    editorStore.setContent(v);
  },
});

const editorRef = ref<{ insert: (fn: (s: string) => { targetValue: string }) => void } | null>(null);

function insertAtCursor(text: string) {
  editorRef.value?.insert(() => ({ targetValue: text }));
}

function handleDrop(e: DragEvent) {
  e.preventDefault();
  const files = e.dataTransfer?.files;
  if (!files?.length) return;
  const file = files[0];
  if (!file || !file.name.match(/\.(md|markdown|txt)$/i)) return;
  const reader = new FileReader();
  reader.onload = () => {
    const text = reader.result as string;
    content.value = text;
    editorStore.setCurrentFileName(file.name);
  };
  reader.readAsText(file);
}

function handleDragOver(e: DragEvent) {
  e.preventDefault();
  (e as any).dataTransfer.dropEffect = 'copy';
}

defineExpose({
  insertAtCursor,
});
</script>

<template>
  <div
    class="md-editor-wrapper h-full flex flex-col min-h-0 flex-1"
    @drop="handleDrop"
    @dragover="handleDragOver"
  >
    <!-- noUploadImg: только кнопка "Вставить картинку" в LeftToolbar загружает файлы; paste и toolbar md-editor не создают дубликаты -->
    <MdEditorComponent
      ref="editorRef"
      v-model="content"
      theme="dark"
      :preview="false"
      language="ru-RU"
      placeholder="Введите Markdown..."
      :no-upload-img="true"
    />
  </div>
</template>

<style scoped>
.md-editor-wrapper :deep(.md-editor) {
  flex: 1;
  min-height: 0;
  height: 100% !important;
}
</style>
