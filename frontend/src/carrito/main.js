import { createApp } from 'vue'
import CarritoApp from './CarritoApp.vue'

const el = document.getElementById('vue-carrito')
if (el) {
  const dataEl = document.getElementById('carrito-data')
  if (dataEl) {
    let data = JSON.parse(dataEl.textContent)
    if (typeof data === 'string') {
      try {
        data = JSON.parse(data)
      } catch (e) {
        console.error('Error parsing carrito data', e)
      }
    }
    createApp(CarritoApp, data).mount(el)
  }
}
