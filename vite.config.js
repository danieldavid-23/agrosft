import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  root: 'frontend',
  base: '/static/dist/',
  build: {
    outDir: '../static/dist',
    emptyOutDir: true,
    rollupOptions: {
      input: {
        carrito: 'frontend/src/carrito/main.js',
        marketplace: 'frontend/src/marketplace/main.js',
        inventario: 'frontend/src/inventario/main.js',
        solicitudes: 'frontend/src/solicitudes/main.js',
        calificaciones: 'frontend/src/calificaciones/main.js',
      },
      output: {
        entryFileNames: '[name].js',
        chunkFileNames: 'chunks/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash][extname]',
      },
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'frontend/src'),
    },
  },
})
