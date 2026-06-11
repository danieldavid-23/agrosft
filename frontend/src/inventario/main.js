import { createApp } from 'vue'
import InventarioApp from './InventarioApp.vue'

const el = document.getElementById('vue-inventario')
if (el) {
  const data = JSON.parse(document.getElementById('inventario-data').textContent)
  createApp(InventarioApp, data).mount(el)
}
