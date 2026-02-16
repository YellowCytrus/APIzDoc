import { convert } from 'pandoc-wasm';

let initPromise: Promise<void> | null = null;

async function ensureReady() {
  if (!initPromise) {
    initPromise = Promise.resolve();
  }
  await initPromise;
}

export function usePandoc() {
  async function convertMdToTypst(markdown: string): Promise<string> {
    await ensureReady();
    const result = await convert(
      {
        from: 'markdown+raw_attribute',
        to: 'typst',
      },
      markdown,
      {}
    );
    return result.stdout ?? '';
  }

  return {
    convertMdToTypst,
  };
}
