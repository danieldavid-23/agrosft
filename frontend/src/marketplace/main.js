import { createApp } from 'vue'
import MarketApp from './MarketApp.vue'

const el = document.getElementById('vue-marketplace')
if (el) {
  const dataEl = document.getElementById('marketplace-data')
  if (dataEl) {
    let data = JSON.parse(dataEl.textContent)
    if (typeof data === 'string') {
      try {
        data = JSON.parse(data)
      } catch (e) {
        console.error('Error parsing marketplace data', e)
      }
    }
    createApp(MarketApp, data).mount(el)
    const fallback = document.getElementById('django-marketplace-fallback')
    if (fallback) fallback.remove()
  }
}
