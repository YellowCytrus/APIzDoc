<script setup lang="ts">
import { Splitpanes, Pane } from 'splitpanes';
import 'splitpanes/dist/splitpanes.css';
import LeftToolbar from './LeftToolbar.vue';
import MdEditor from './MdEditor.vue';
import TypstPreview from './TypstPreview.vue';
import RightPanel from './RightPanel.vue';
import { ref } from 'vue';

const mdEditorRef = ref<InstanceType<typeof MdEditor> | null>(null);

function handleInsert(text: string) {
  mdEditorRef.value?.insertAtCursor(text);
}
</script>

<template>
  <div class="editor-layout flex h-full min-h-0 bg-zinc-900 text-zinc-100">
    <LeftToolbar @insert="handleInsert" />
    <Splitpanes class="flex-1 min-h-0 min-w-0">
      <Pane :size="50" :min-size="20">
        <div class="h-full flex flex-col min-h-0 overflow-hidden">
          <MdEditor ref="mdEditorRef" />
        </div>
      </Pane>
      <Pane :size="50" :min-size="20">
        <div class="h-full overflow-auto bg-zinc-100">
          <TypstPreview />
        </div>
      </Pane>
    </Splitpanes>
    <RightPanel />
  </div>
</template>

<style>
.editor-layout .splitpanes__splitter {
  background: rgb(63 63 70);
  width: 4px;
}
.editor-layout .splitpanes__splitter:hover {
  background: rgb(113 113 122);
}
</style>
