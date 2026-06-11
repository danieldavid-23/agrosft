import { createApp } from 'vue'
import MarketApp from './MarketApp.vue'

const el = document.getElementById('vue-marketplace')
if (el) {
  const data = JSON.parse(document.getElementById('marketplace-data').textContent)
  createApp(MarketApp, data).mount(el)
}
