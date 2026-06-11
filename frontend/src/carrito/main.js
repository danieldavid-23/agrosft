import { createApp } from 'vue'
import CarritoApp from './CarritoApp.vue'

const el = document.getElementById('vue-carrito')
if (el) {
  const data = JSON.parse(document.getElementById('carrito-data').textContent)
  createApp(CarritoApp, data).mount(el)
}
