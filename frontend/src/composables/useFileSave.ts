export function useFileSave() {
  async function saveFile(blob: Blob, suggestedName: string): Promise<void> {
    if ('showSaveFilePicker' in window) {
      try {
        const types: { description: string; accept: Record<string, string[]> }[] = [];
        if (suggestedName.endsWith('.pdf')) {
          types.push({ description: 'PDF document', accept: { 'application/pdf': ['.pdf'] } });
        } else if (suggestedName.endsWith('.typ')) {
          types.push({ description: 'Typst source', accept: { 'text/plain': ['.typ'] } });
        } else {
          types.push({ description: 'Markdown file', accept: { 'text/markdown': ['.md'] } });
        }
        const handle = await (window as any).showSaveFilePicker({
          suggestedName,
          types,
        });
        const writable = await handle.createWritable();
        await writable.write(blob);
        await writable.close();
        return;
      } catch (e) {
        if ((e as Error).name === 'AbortError') return;
      }
    }
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = suggestedName;
    a.click();
    URL.revokeObjectURL(url);
  }

  return {
    saveFile,
  };
}
