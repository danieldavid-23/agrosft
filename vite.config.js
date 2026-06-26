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
        style: 'frontend/src/style.css',
        layout: 'frontend/src/layout/main.js',
        carrito: 'frontend/src/carrito/main.js',
        marketplace: 'frontend/src/marketplace/main.js',
        inventario: 'frontend/src/inventario/main.js',
        calificaciones: 'frontend/src/calificaciones/main.js',
      },
      output: {
        entryFileNames: '[name].js',
        chunkFileNames: 'chunks/[name]-[hash].js',
        assetFileNames: (assetInfo) => {
          if (assetInfo.name && assetInfo.name.endsWith('.css')) {
            return 'css/[name].[ext]';
          }
          return 'assets/[name]-[hash][extname]';
        },
      },
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'frontend/src'),
    },
  },
})
