import { createApp } from 'vue'
import NavbarApp from './NavbarApp.vue'
import FooterApp from './FooterApp.vue'

const dataEl = document.getElementById('layout-data')
if (dataEl) {
  const data = JSON.parse(dataEl.textContent)

  const navbarEl = document.getElementById('vue-navbar')
  if (navbarEl) {
    createApp(NavbarApp, data).mount(navbarEl)
  }

  const footerEl = document.getElementById('vue-footer')
  if (footerEl) {
    createApp(FooterApp, { urls: data.urls }).mount(footerEl)
  }
}
