import { createApp } from 'vue'
import SolicitudApp from './SolicitudApp.vue'

const el = document.getElementById('vue-solicitudes')
if (el) {
  const data = JSON.parse(document.getElementById('solicitudes-data').textContent)
  createApp(SolicitudApp, data).mount(el)
}
