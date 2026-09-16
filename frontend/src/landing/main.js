import { createApp } from 'vue'
import LandingPage from './LandingPage.vue'

const mountEl = document.getElementById('vue-landing')
if (mountEl) {
  let props = {
    urls: {},
    user: null,
    is_authenticated: false
  }

  const dataEl = document.getElementById('layout-data') || document.getElementById('landing-data')
  if (dataEl) {
    try {
      const parsed = JSON.parse(dataEl.textContent)
      props = { ...props, ...parsed }
    } catch (e) {
      console.error('Error parsing layout-data for landing:', e)
    }
  }

  createApp(LandingPage, props).mount(mountEl)
}
