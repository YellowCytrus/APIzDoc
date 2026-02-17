<script setup lang="ts">
import { ref, onMounted, computed, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import Canvas from "../components/page-editor/Canvas.vue";
import Sidebar from "../components/page-editor/Sidebar.vue";
import Properties from "../components/page-editor/Properties.vue";
import { usePageEditorStore } from "../stores/pageEditor";
import { API_BASE } from "../config";

interface TitlePageItem {
  id: number;
  name: string;
}

const store = usePageEditorStore();
const route = useRoute();
const router = useRouter();

const pageName = ref("");
const saving = ref(false);
const error = ref<string | null>(null);
const titlePages = ref<TitlePageItem[]>([]);

const editingId = computed(() => {
  const id = route.params.id;
  return typeof id === "string" && /^\d+$/.test(id) ? parseInt(id, 10) : null;
});

async function fetchTitlePages() {
  try {
    const res = await fetch(`${API_BASE}/title-pages?limit=200`);
    if (res.ok) {
      const data = await res.json();
      titlePages.value = data.map((p: { id: number; name: string }) => ({ id: p.id, name: p.name }));
    }
  } catch {
    titlePages.value = [];
  }
}

async function loadPage(id: number) {
  try {
    const res = await fetch(`${API_BASE}/title-pages/${id}`);
    if (res.ok) {
      const data = await res.json();
      store.loadContent(data.content);
      pageName.value = data.name;
    }
  } catch {
    store.reset();
  }
}

function onTitlePageSelect(ev: Event) {
  const value = (ev.target as HTMLSelectElement).value;
  if (value === "") {
    router.push({ name: "pages" });
    store.reset();
    pageName.value = "";
  } else {
    const id = parseInt(value, 10);
    if (!isNaN(id)) {
      router.push({ name: "pages-edit", params: { id: String(id) } });
    }
  }
}

onMounted(async () => {
  await fetchTitlePages();
  if (editingId.value) {
    await loadPage(editingId.value);
  } else {
    store.reset();
  }
});

watch(editingId, (id) => {
  if (id) {
    loadPage(id);
  } else {
    store.reset();
    pageName.value = "";
  }
});

async function save() {
  const name = pageName.value.trim();
  if (!name) {
    error.value = "Введите название страницы";
    return;
  }
  error.value = null;
  saving.value = true;
  try {
    const content = {
      elements: store.elements,
      paper: store.paper,
      variables: store.variables,
      ignore_document_styles: store.ignoreDocumentStyles,
    };
    if (editingId.value) {
      const res = await fetch(`${API_BASE}/title-pages/${editingId.value}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, content }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail ?? "Ошибка сохранения");
      }
    } else {
      const res = await fetch(`${API_BASE}/title-pages`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, content }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail ?? "Ошибка сохранения");
      }
      const data = await res.json();
      titlePages.value = [...titlePages.value, { id: data.id, name: data.name }];
      await router.push({ name: "pages-edit", params: { id: String(data.id) } });
      store.loadContent(data.content);
      pageName.value = data.name;
    }
  } catch (e) {
    error.value = e instanceof Error ? e.message : "Ошибка сохранения";
  } finally {
    saving.value = false;
  }
}
</script>

<template>
  <div class="page-editor-view flex flex-col h-screen bg-zinc-900 text-zinc-100">
    <header class="flex items-center gap-4 px-4 py-2 bg-zinc-800 border-b border-zinc-700">
      <router-link to="/" class="text-sm text-zinc-400 hover:text-zinc-100">
        ← Редактор
      </router-link>
      <div class="flex-1 flex items-center gap-4">
        <div class="flex items-center gap-2">
          <label class="text-sm text-zinc-400">Титульник:</label>
          <select
            :value="editingId ?? ''"
            class="rounded bg-zinc-700 px-2 py-1.5 text-sm min-w-[160px]"
            @change="onTitlePageSelect"
          >
            <option value="">Новая страница</option>
            <option v-for="p in titlePages" :key="p.id" :value="p.id">
              {{ p.name }}
            </option>
          </select>
        </div>
        <label class="flex items-center gap-2 text-sm text-zinc-400">
          <input
            v-model="store.ignoreDocumentStyles"
            type="checkbox"
            class="rounded border-zinc-600 bg-zinc-700"
          />
          Игнорировать глобальные стили документа
        </label>
        <input
          v-model="pageName"
          type="text"
          placeholder="Название титульника"
          class="rounded bg-zinc-700 px-3 py-1.5 text-sm w-64"
        />
        <button
          type="button"
          class="px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-500 text-sm disabled:opacity-50"
          :disabled="saving"
          @click="save"
        >
          {{ saving ? "Сохранение…" : editingId ? "Сохранить" : "Создать титульник" }}
        </button>
        <span v-if="error" class="text-sm text-red-400">{{ error }}</span>
      </div>
    </header>
    <main class="flex-1 grid grid-cols-[200px_1fr_240px] min-h-0">
      <Sidebar class="border-r border-zinc-700 overflow-y-auto" />
      <div class="min-h-0 overflow-hidden">
        <Canvas />
      </div>
      <Properties class="border-l border-zinc-700 overflow-y-auto" />
    </main>
  </div>
</template>
