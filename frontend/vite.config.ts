import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import topLevelAwait from 'vite-plugin-top-level-await'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue(), topLevelAwait()],
  assetsInclude: ['**/*.wasm'],
  optimizeDeps: {
    exclude: ['@myriaddreamin/typst-ts-web-compiler', '@myriaddreamin/typst-ts-renderer'],
  },
  test: {
    environment: 'jsdom',
    globals: true,
  },
})
