import { createApp } from 'vue'
import InventarioApp from './InventarioApp.vue'

const el = document.getElementById('vue-inventario')
if (el) {
  const dataEl = document.getElementById('inventario-data')
  if (dataEl) {
    let data = JSON.parse(dataEl.textContent)
    if (typeof data === 'string') {
      try {
        data = JSON.parse(data)
      } catch (e) {
        console.error('Error parsing inventario data', e)
      }
    }
    createApp(InventarioApp, data).mount(el)
    const fallback = document.getElementById('django-inventario-fallback')
    if (fallback) fallback.remove()
  }
}
