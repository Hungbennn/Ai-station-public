import templateCompilerOptions from '@tresjs/core/template-compiler-options'
import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'

// Component `.vue` dịch sẵn lúc build (G13, spec §8): bản Vue chỉ-runtime, không `new Function` → bật được CSP chặt.
// Lát 2c: thẻ `Tres*` là phần tử của renderer TresJS, không phải component Vue (templateCompilerOptions của TresJS).
export default defineConfig({
  plugins: [vue({ ...templateCompilerOptions })],
  define: {
    __VUE_OPTIONS_API__: 'true',
    __VUE_PROD_DEVTOOLS__: 'false',
    __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: 'false',
  },
  // changeOrigin: tram-api chỉ nhận Host 127.0.0.1:<cổng> / localhost:<cổng> / tên máy B (421 nếu khác).
  server: { proxy: { '/api': { target: 'http://127.0.0.1:7700', changeOrigin: true } } },
  // Lát 2f: không nhúng tài nguyên nhỏ thành `data:` (mặc định < 4 kB) — font JetBrains Mono tiếng Việt ~3,9 kB sẽ
  // thành `data:font/woff2` và bị CSP `font-src 'self'` chặn (phát hiện khi kiểm trình duyệt).
  build: { outDir: 'dist', emptyOutDir: true, assetsInlineLimit: 0 },
})
