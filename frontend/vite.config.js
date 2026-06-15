import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  server: {
    port: 5173,
    proxy: {
      '^/(login|admin|staff|auth)': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        
        rewrite: (path) => '/api' + path,
        
        bypass(req) {
          if (req.headers.accept && req.headers.accept.includes('text/html')) {
            return req.url;
          }
        }
      } 
    } 
  } 
})