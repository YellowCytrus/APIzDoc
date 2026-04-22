import { ref, watch, type Ref } from 'vue';
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

  const fieldTimers = new Map<string, ReturnType<typeof setTimeout>>();
  const fieldVersions = new Map<string, number>();
  let inflightSaves = 0;

  async function persistField(elementKey: ElementType, field: string, value: unknown, version: number) {
    const id = profileId.value;
    if (id == null) return;
    inflightSaves += 1;
    saving.value = inflightSaves > 0;
    setSaveStatus('saving');
    const key = `${elementKey}:${field}`;
    try {
      await patchElementStyles(id, elementKey, { [field]: value });
      if (fieldVersions.get(key) !== version) return;
      // Keep optimistic local state as source of truth for edited field.
      // Replacing it with server payload can re-apply legacy normalization
      // and cause visible jumps while sliders are being dragged.
      setSaveStatus('saved');
      const profilesStore = useProfilesStore();
      void profilesStore.loadProfileStyles(id);
    } catch {
      if (fieldVersions.get(key) === version) {
        setSaveStatus('error');
      }
    } finally {
      inflightSaves = Math.max(0, inflightSaves - 1);
      saving.value = inflightSaves > 0;
    }
  }

  function schedulePersist(elementKey: ElementType, field: string, value: unknown) {
    const key = `${elementKey}:${field}`;
    const version = (fieldVersions.get(key) ?? 0) + 1;
    fieldVersions.set(key, version);
    const existingTimer = fieldTimers.get(key);
    if (existingTimer) clearTimeout(existingTimer);
    const timer = setTimeout(() => {
      fieldTimers.delete(key);
      void persistField(elementKey, field, value, version);
    }, 400);
    fieldTimers.set(key, timer);
  }

  function updateField(elementKey: ElementType, field: string, value: unknown, persist = true) {
    styles.value = {
      ...styles.value,
      [elementKey]: {
        ...styles.value[elementKey],
        [field]: value,
      },
    };
    if (persist) {
      schedulePersist(elementKey, field, value);
    }
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
