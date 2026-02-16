export function useFileSave() {
  async function saveFile(blob: Blob, suggestedName: string): Promise<void> {
    if ('showSaveFilePicker' in window) {
      try {
        const handle = await (window as any).showSaveFilePicker({
          suggestedName,
          types: [
            {
              description: suggestedName.endsWith('.pdf') ? 'PDF document' : 'Markdown file',
              accept: suggestedName.endsWith('.pdf')
                ? { 'application/pdf': ['.pdf'] }
                : { 'text/markdown': ['.md'] },
            },
          ],
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
