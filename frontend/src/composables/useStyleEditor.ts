import { ref, watch, type Ref } from 'vue';
import { useDebounceFn } from '@vueuse/core';
import { API_BASE } from '../config';
import { STYLE_TAB_TREE, collectElementKeys } from '../config/styleFields';
import type { ElementType } from '../types/api';
import { useProfilesStore } from '../stores/profiles';

export type StyleDataMap = Record<ElementType, Record<string, unknown>>;

const ALL_ELEMENT_KEYS = collectElementKeys(STYLE_TAB_TREE);

function getApiPath(elementKey: ElementType): string {
  if (/^heading_\d$/.test(elementKey)) {
    const level = elementKey.replace('heading_', '');
    return `heading/${level}`;
  }
  return elementKey;
}

async function fetchElementStyles(
  profileId: number,
  elementKey: ElementType,
): Promise<Record<string, unknown>> {
  const path = getApiPath(elementKey);
  const res = await fetch(`${API_BASE}/profiles/${profileId}/${path}`);
  if (!res.ok) return {};
  return res.json();
}

async function patchElementStyles(
  profileId: number,
  elementKey: ElementType,
  patch: Record<string, unknown>,
): Promise<Record<string, unknown>> {
  const path = getApiPath(elementKey);
  const res = await fetch(`${API_BASE}/profiles/${profileId}/${path}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(patch),
  });
  if (!res.ok) {
    const res2 = await fetch(`${API_BASE}/profiles/${profileId}/${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(patch),
    });
    if (!res2.ok) throw new Error(`Failed to save ${elementKey}`);
    return res2.json();
  }
  return res.json();
}

export function useStyleEditor(profileId: Ref<number | null>) {
  const styles = ref<StyleDataMap>({} as StyleDataMap);
  const loading = ref(false);
  const saving = ref(false);
  const saveStatus = ref<'idle' | 'saving' | 'saved' | 'error'>('idle');

  let saveStatusTimeout: ReturnType<typeof setTimeout> | null = null;

  function setSaveStatus(status: 'idle' | 'saving' | 'saved' | 'error') {
    saveStatus.value = status;
    if (saveStatusTimeout) clearTimeout(saveStatusTimeout);
    if (status === 'saved' || status === 'error') {
      saveStatusTimeout = setTimeout(() => {
        saveStatus.value = 'idle';
      }, 2000);
    }
  }

  async function loadAll(id: number) {
    loading.value = true;
    try {
      const results = await Promise.all(
        ALL_ELEMENT_KEYS.map(async (key) => {
          const data = await fetchElementStyles(id, key);
          return [key, data] as const;
        }),
      );
      const map = {} as StyleDataMap;
      for (const [key, data] of results) {
        map[key] = data;
      }
      styles.value = map;
    } finally {
      loading.value = false;
    }
  }

  const debouncedPatch = useDebounceFn(
    async (elementKey: ElementType, field: string, value: unknown) => {
      const id = profileId.value;
      if (id == null) return;
      saving.value = true;
      setSaveStatus('saving');
      try {
        const updated = await patchElementStyles(id, elementKey, { [field]: value });
        styles.value = { ...styles.value, [elementKey]: updated };
        setSaveStatus('saved');
        const profilesStore = useProfilesStore();
        profilesStore.loadProfileStyles(id);
      } catch {
        setSaveStatus('error');
      } finally {
        saving.value = false;
      }
    },
    400,
  );

  function updateField(elementKey: ElementType, field: string, value: unknown) {
    styles.value = {
      ...styles.value,
      [elementKey]: {
        ...styles.value[elementKey],
        [field]: value,
      },
    };
    debouncedPatch(elementKey, field, value);
  }

  watch(
    profileId,
    (id) => {
      if (id != null) {
        loadAll(id);
      } else {
        styles.value = {} as StyleDataMap;
      }
    },
    { immediate: true },
  );

  return {
    styles,
    loading,
    saving,
    saveStatus,
    updateField,
    reload: () => {
      if (profileId.value != null) loadAll(profileId.value);
    },
  };
}
