import { createApp } from 'vue';
import { createPinia } from 'pinia';
import router from './router';
import App from './App.vue';
import './style.css';
import '@fontsource/roboto/400.css';
import '@fontsource/libertinus-serif/400.css';
import '@fontsource/libertinus-serif/400-italic.css';
import '@fontsource/libertinus-serif/600.css';
import '@fontsource/libertinus-serif/700.css';
import { $typst } from '@myriaddreamin/typst.ts/contrib/snippet';

// Fix WASM loading in Vite: provide explicit URLs for typst modules
import compilerWasm from '@myriaddreamin/typst-ts-web-compiler/pkg/typst_ts_web_compiler_bg.wasm?url';
import rendererWasm from '@myriaddreamin/typst-ts-renderer/pkg/typst_ts_renderer_bg.wasm?url';

$typst.setCompilerInitOptions({ getModule: () => compilerWasm });
$typst.setRendererInitOptions({ getModule: () => rendererWasm });

const app = createApp(App);
app.use(createPinia());
app.use(router);
app.mount('#app');
