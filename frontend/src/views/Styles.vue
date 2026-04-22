<script setup lang="ts">
import { computed, ref } from 'vue';
import { useProfilesStore } from '../stores/profiles';
import { useStyleEditor } from '../composables/useStyleEditor';
import { STYLE_TAB_TREE } from '../config/styleFields';
import type { ElementType } from '../types/api';
import type { Unit } from '../utils/unitConversion';
import { ptToMm } from '../utils/unitConversion';
import ProfileSidebar from '../components/styles/ProfileSidebar.vue';
import NestedTabs from '../components/styles/NestedTabs.vue';

const profilesStore = useProfilesStore();
const profileId = computed(() => profilesStore.currentId);
const { styles, loading, saveStatus, updateField } = useStyleEditor(profileId);
const units = ref<Record<string, Unit | undefined>>({});

const conversionContext = computed(() => {
  const fontSizePt = Number(styles.value.document?.font_size) || 0;
  return {
    fontSizeMm: ptToMm(fontSizePt),
  };
});

function onFieldChange(elementKey: ElementType, field: string, value: unknown, persist = true) {
  updateField(elementKey, field, value, persist);
}

function onUnitChange(fieldPath: string, unit: Unit) {
  units.value = { ...units.value, [fieldPath]: unit };
}
</script>

<template>
  <div class="styles-page">
    <ProfileSidebar />

    <main class="main-area">
      <!-- Top bar with save status -->
      <div class="top-bar">
        <h1 class="page-title">
          {{ profilesStore.current?.name ?? 'Выберите профиль' }}
        </h1>
        <div class="status-area">
          <span v-if="loading" class="status loading">Загрузка...</span>
          <span v-else-if="saveStatus === 'saving'" class="status saving">Сохранение...</span>
          <span v-else-if="saveStatus === 'saved'" class="status saved">Сохранено</span>
          <span v-else-if="saveStatus === 'error'" class="status error">Ошибка</span>
        </div>
      </div>

      <!-- Tabs area -->
      <div v-if="profileId != null && !loading" class="tabs-area">
        <NestedTabs
          :nodes="STYLE_TAB_TREE"
          :depth="0"
          :styles="styles"
          :units="units"
          :context="conversionContext"
          @field-change="onFieldChange"
          @unit-change="onUnitChange"
        />
      </div>

      <div v-else-if="!profileId" class="empty-state">
        <p>Выберите или создайте профиль для редактирования стилей</p>
      </div>

      <div v-else class="empty-state">
        <p>Загрузка стилей...</p>
      </div>
    </main>
  </div>
</template>

<style scoped>
.styles-page {
  display: flex;
  height: 100%;
  background: #09090b;
  color: #fafafa;
}

.main-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  overflow: hidden;
}

.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1.25rem;
  border-bottom: 1px solid #27272a;
  background: #18181b;
}

.page-title {
  font-size: 1rem;
  font-weight: 600;
  margin: 0;
  color: #fafafa;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.status-area {
  flex-shrink: 0;
}

.status {
  font-size: 0.75rem;
  padding: 0.2rem 0.6rem;
  border-radius: 9999px;
}

.status.loading {
  color: #a1a1aa;
}

.status.saving {
  color: #facc15;
  background: rgba(250, 204, 21, 0.1);
}

.status.saved {
  color: #22c55e;
  background: rgba(34, 197, 94, 0.1);
}

.status.error {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.1);
}

.tabs-area {
  flex: 1;
  overflow-y: auto;
}

.empty-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-state p {
  color: #52525b;
  font-size: 0.9rem;
}
</style>
