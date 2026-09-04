<script setup>
import { ref, onMounted } from 'vue'
import { getCSRFToken } from '../shared/csrf.js'

const props = defineProps({
  user: Object,
  is_authenticated: Boolean,
  cart_count: Number,
  urls: Object,
  messages: Array
})

const showMobileMenu = ref(false)
const showDropdown = ref(false)
const toasts = ref([])

function toggleMobile() {
  showMobileMenu.value = !showMobileMenu.value
}

function toggleDropdown() {
  showDropdown.value = !showDropdown.value
}

function isActive(href) {
  const current = window.location.pathname.replace(/\/+$/, '')
  const link = (href || '').replace(/\/+$/, '')
  return current === link
}

function onClickOutside(event) {
  const dropdown = document.querySelector('.navbar-nav .dropdown')
  if (dropdown && !dropdown.contains(event.target)) {
    showDropdown.value = false
  }
}

async function logout() {
  try {
    await fetch(props.urls.logout, {
      method: 'POST',
      headers: { 'X-CSRFToken': getCSRFToken() },
    })
  } catch (e) {}
  window.location.href = props.urls.login
}

onMounted(() => {
  document.addEventListener('click', onClickOutside)
  if (props.messages && props.messages.length) {
    props.messages.forEach((msg, i) => {
      const id = Date.now() + i
      setTimeout(() => {
        toasts.value.push({ ...msg, id, visible: true })
      }, i * 200 + 100)
      setTimeout(() => {
        const t = toasts.value.find(t => t.id === id)
        if (t) t.visible = false
        setTimeout(() => {
          toasts.value = toasts.value.filter(t => t.id !== id)
        }, 400)
      }, 6000 + i * 200)
    })
  }
})

function dismissToast(id) {
  const t = toasts.value.find(t => t.id === id)
  if (t) t.visible = false
  setTimeout(() => {
    toasts.value = toasts.value.filter(t => t.id !== id)
  }, 400)
}

function getToastTitle(tags) {
  if (tags === 'success') return 'Éxito'
  if (tags === 'danger' || tags === 'error') return 'Error'
  if (tags === 'warning') return 'Atención'
  return 'Información'
}
</script>

<template>
  <!-- Navbar -->
  <nav class="navbar navbar-expand-lg navbar-light navbar-premium sticky-top">
    <div class="container">
      <a class="navbar-brand d-flex align-items-center gap-2" :href="urls.home">
        <img :src="urls.logo" alt="AgroSFT" height="36">
        <span class="fw-bold fs-5" style="color: var(--primary-color)">AGROSFT</span>
      </a>
      <button class="navbar-toggler border-0 shadow-none" type="button" @click="toggleMobile">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" :class="{ show: showMobileMenu }" id="navbarNav">
        <ul class="navbar-nav ms-auto align-items-center">
          <template v-if="is_authenticated && user">
              <li class="nav-item">
                <a class="nav-link" :class="{ active: isActive(urls.marketplace) }" :href="urls.marketplace"><i class="fas fa-store me-1 d-lg-none"></i> Inicio</a>
              </li>
              <li class="nav-item">
                <a class="nav-link" :class="{ active: isActive(urls.mi_inventario) }" :href="urls.mi_inventario"><i class="fas fa-box-open me-1 d-lg-none"></i> Mi Inventario</a>
              </li>
              <li class="nav-item">
                <a class="nav-link" :class="{ active: isActive(urls.clientes) }" :href="urls.clientes"><i class="fas fa-users me-1 d-lg-none"></i> Clientes</a>
              </li>
              <li class="nav-item">
                <a class="nav-link" :class="{ active: isActive(urls.ventas) }" :href="urls.ventas"><i class="fas fa-chart-line me-1 d-lg-none"></i> Ventas</a>
              </li>
              <li class="nav-item">
                <a class="nav-link" :class="{ active: isActive(urls.solicitudes) }" :href="urls.solicitudes"><i class="fas fa-clipboard-list me-1 d-lg-none"></i> Solicitudes</a>
              </li>
              <li class="nav-item">
                <a class="nav-link" :class="{ active: isActive(urls.mis_compras) }" :href="urls.mis_compras"><i class="fas fa-shopping-bag me-1 d-lg-none"></i> Mis Compras</a>
              </li>

            <li class="nav-item ms-lg-2 mt-2 mt-lg-0 d-flex align-items-center">
                <a class="btn btn-outline-secondary border-0 rounded-circle position-relative p-2" :href="urls.carrito" title="Carrito de Compras">
                  <i class="fas fa-shopping-cart fs-5"></i>
                  <span v-if="cart_count > 0" class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger" style="font-size: 0.6rem;">
                    {{ cart_count }}
                  </span>
                </a>
              </li>

            <li class="nav-item dropdown ms-lg-2 mt-2 mt-lg-0" :class="{ show: showDropdown }">
              <a class="nav-link dropdown-toggle btn btn-light px-3 fw-bold rounded-pill" style="color: var(--text-main)" href="#" @click.prevent="toggleDropdown" role="button">
                <img v-if="user.imagen_perfil_url" :src="user.imagen_perfil_url" alt="Avatar" class="rounded-circle me-1 align-middle" style="width: 24px; height: 24px; object-fit: cover; border: 1.5px solid var(--primary-color);">
                <i v-else class="fas fa-user-circle fs-5 me-1 align-middle" style="color: var(--primary-color)"></i>
                {{ user.nombre_corto || user.correo }}
              </a>
              <ul class="dropdown-menu dropdown-menu-end shadow border-0" :class="{ show: showDropdown }" style="border-radius: var(--radius-md);">
                <li><a class="dropdown-item py-2" :href="urls.perfil"><i class="fas fa-id-card fa-fw text-muted me-2"></i> Mi Perfil</a></li>
                <li><a class="dropdown-item py-2" :href="urls.cambiar_password"><i class="fas fa-key fa-fw text-muted me-2"></i> Seguridad</a></li>
                <li><a class="dropdown-item py-2" :href="urls.facturacion_historial"><i class="fas fa-file-invoice-dollar fa-fw text-muted me-2"></i> Mis Facturas</a></li>
                <li><hr class="dropdown-divider"></li>
                <li><a class="dropdown-item py-2" href="#" @click.prevent="logout" style="color: #dc2626;"><i class="fas fa-sign-out-alt fa-fw me-2" style="color: #dc2626;"></i> Cerrar Sesión</a></li>
              </ul>
            </li>
          </template>
          <template v-else>
            <li class="nav-item">
              <a class="nav-link" :href="urls.terminos">Términos</a>
            </li>
            <li class="nav-item mt-2 mt-lg-0 ms-lg-2">
              <a class="btn btn-outline-secondary rounded-pill px-4 me-2" :href="urls.login">Iniciar Sesión</a>
            </li>
            <li class="nav-item mt-2 mt-lg-0">
              <a class="btn rounded-pill px-4 shadow-sm text-white" style="background-color: var(--primary-color)" :href="urls.registro">Registrarse</a>
            </li>
          </template>
        </ul>
      </div>
    </div>
  </nav>

  <!-- Notifications Premium -->
  <div class="notification-container" aria-live="polite" aria-atomic="true">
    <div
      v-for="toast in toasts"
      :key="toast.id"
      class="notification-toast"
      :class="{
        show: toast.visible,
        hide: !toast.visible,
        'toast-success': toast.tags === 'success',
        'toast-danger': toast.tags === 'danger' || toast.tags === 'error',
        'toast-warning': toast.tags === 'warning',
        'toast-info': toast.tags === 'info'
      }"
      role="alert"
    >
      <div class="toast-body-wrapper d-flex align-items-center gap-3 w-100">
        <div class="toast-icon-circle flex-shrink-0">
          <i v-if="toast.tags === 'success'" class="fas fa-check"></i>
          <i v-else-if="toast.tags === 'danger' || toast.tags === 'error'" class="fas fa-exclamation"></i>
          <i v-else-if="toast.tags === 'warning'" class="fas fa-exclamation-triangle"></i>
          <i v-else class="fas fa-info"></i>
        </div>
        <div class="toast-content flex-grow-1">
          <div class="toast-title">{{ getToastTitle(toast.tags) }}</div>
          <div class="toast-message">{{ toast.text }}</div>
        </div>
        <button
          type="button"
          class="toast-close-btn flex-shrink-0"
          @click="dismissToast(toast.id)"
          title="Cerrar notificación"
          aria-label="Cerrar"
        >
          <i class="fas fa-times"></i>
        </button>
      </div>
      <div class="toast-progress"></div>
    </div>
  </div>
</template>
