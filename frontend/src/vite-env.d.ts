/// <reference types="vite/client" />

declare module '*.wasm?url' {
  const src: string;
  export default src;
}

declare module 'splitpanes' {
  import type { DefineComponent } from 'vue';
  export const Splitpanes: DefineComponent<any>;
  export const Pane: DefineComponent<any>;
}

declare module 'pandoc-wasm' {
  export function convert(
    options: { from: string; to: string },
    stdin: string | null,
    files: Record<string, string | Blob>
  ): Promise<{ stdout: string; stderr: string; warnings: unknown[] }>;
}
