import { createApp } from 'vue'
import CalificacionApp from './CalificacionApp.vue'

const el = document.getElementById('vue-calificaciones')
if (el) {
  const data = JSON.parse(document.getElementById('calificaciones-data').textContent)
  createApp(CalificacionApp, data).mount(el)
}
