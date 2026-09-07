import { createApp } from 'vue'
import CalificacionApp from './CalificacionApp.vue'

const el = document.getElementById('vue-calificaciones')
if (el) {
  const dataEl = document.getElementById('calificaciones-data')
  if (dataEl) {
    let data = JSON.parse(dataEl.textContent)
    if (typeof data === 'string') {
      try {
        data = JSON.parse(data)
      } catch (e) {
        console.error('Error parsing calificaciones data', e)
      }
    }
    createApp(CalificacionApp, data).mount(el)
  }
}
