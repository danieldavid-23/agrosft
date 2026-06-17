import { createApp } from 'vue'
import SolicitudApp from './SolicitudApp.vue'

const el = document.getElementById('vue-solicitudes')
if (el) {
  createApp(SolicitudApp).mount(el)
}
