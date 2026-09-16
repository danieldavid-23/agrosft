<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  urls: {
    type: Object,
    default: () => ({})
  },
  isAuthenticated: {
    type: Boolean,
    default: false
  },
  user: {
    type: Object,
    default: null
  }
})

const isScrolled = ref(false)
const mobileMenuOpen = ref(false)

const handleScroll = () => {
  isScrolled.value = window.scrollY > 20
}

const toggleMobileMenu = () => {
  mobileMenuOpen.value = !mobileMenuOpen.value
}

const closeMobileMenu = () => {
  mobileMenuOpen.value = false
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<template>
  <header
    class="gh-landing-nav"
    :class="{ 'is-scrolled': isScrolled }"
  >
    <div class="gh-nav-container">
      <!-- Brand Logo -->
      <a :href="urls.home || '/'" class="gh-brand" @click="closeMobileMenu">
        <div class="gh-logo-wrap">
          <img
            :src="urls.logo || '/static/img/agrosft_o.svg'"
            alt="AgroSFT Logo"
            class="gh-logo-img"
          />
        </div>
        <span class="gh-brand-name">Agro<span class="gh-brand-accent">SFT</span></span>
      </a>

      <!-- Desktop Nav Links -->
      <nav class="gh-nav-links">
        <a href="#caracteristicas" class="gh-link">Características</a>
        <a href="#como-funciona" class="gh-link">Cómo funciona</a>
        <a href="#seguridad" class="gh-link">Seguridad</a>
      </nav>

      <!-- Action Buttons -->
      <div class="gh-nav-actions">
        <template v-if="isAuthenticated">
          <a :href="urls.marketplace || '/inventario/'" class="gh-btn gh-btn-primary">
            <i class="fas fa-th-large me-1"></i> Ir al Sistema
          </a>
        </template>
        <template v-else>
          <a :href="urls.login || '/usuarios/login/'" class="gh-btn gh-btn-ghost">
            <i class="fas fa-sign-in-alt me-1"></i> Iniciar sesión
          </a>
          <a :href="urls.registro || '/usuarios/registro/'" class="gh-btn gh-btn-primary">
            <span>Registrarse</span>
            <i class="fas fa-arrow-right ms-1"></i>
          </a>
        </template>
      </div>

      <!-- Mobile Hamburger Button -->
      <button
        class="gh-hamburger-btn"
        :class="{ 'is-active': mobileMenuOpen }"
        @click="toggleMobileMenu"
        aria-label="Toggle navigation"
      >
        <span></span>
        <span></span>
        <span></span>
      </button>
    </div>

    <!-- Mobile Drawer Menu -->
    <transition name="gh-slide-down">
      <div v-if="mobileMenuOpen" class="gh-mobile-menu">
        <div class="gh-mobile-links">
          <a href="#caracteristicas" class="gh-mobile-link" @click="closeMobileMenu">
            <i class="fas fa-layer-group me-2"></i> Características
          </a>
          <a href="#como-funciona" class="gh-mobile-link" @click="closeMobileMenu">
            <i class="fas fa-network-wired me-2"></i> Cómo funciona
          </a>
          <a href="#seguridad" class="gh-mobile-link" @click="closeMobileMenu">
            <i class="fas fa-shield-alt me-2"></i> Seguridad
          </a>
        </div>
        <div class="gh-mobile-actions">
          <template v-if="isAuthenticated">
            <a :href="urls.marketplace || '/inventario/'" class="gh-btn gh-btn-primary w-100 text-center">
              Ir al Sistema
            </a>
          </template>
          <template v-else>
            <a :href="urls.login || '/usuarios/login/'" class="gh-btn gh-btn-ghost w-100 text-center">
              Iniciar sesión
            </a>
            <a :href="urls.registro || '/usuarios/registro/'" class="gh-btn gh-btn-primary w-100 text-center">
              Registrarse
            </a>
          </template>
        </div>
      </div>
    </transition>
  </header>
</template>

<style scoped>
.gh-landing-nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background: rgba(13, 17, 23, 0.75);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid rgba(48, 54, 61, 0.4);
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  padding: 0.85rem 0;
}

.gh-landing-nav.is-scrolled {
  background: rgba(13, 17, 23, 0.94);
  border-bottom-color: rgba(48, 54, 61, 0.85);
  box-shadow: 0 8px 24px rgba(1, 4, 9, 0.4);
  padding: 0.65rem 0;
}

.gh-nav-container {
  max-width: 1240px;
  margin: 0 auto;
  padding: 0 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* Brand */
.gh-brand {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  text-decoration: none;
  color: #f0f6fc;
}

.gh-logo-wrap {
  width: 34px;
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background: rgba(46, 160, 67, 0.12);
  border: 1px solid rgba(46, 160, 67, 0.3);
  padding: 4px;
}

.gh-logo-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.gh-brand-name {
  font-size: 1.2rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: #f0f6fc;
}

.gh-brand-accent {
  color: #2ea043;
}

.gh-badge-pill {
  font-size: 0.7rem;
  font-weight: 600;
  color: #3fb950;
  background: rgba(46, 160, 67, 0.15);
  border: 1px solid rgba(46, 160, 67, 0.3);
  padding: 0.15rem 0.45rem;
  border-radius: 20px;
}

/* Nav Links */
.gh-nav-links {
  display: flex;
  align-items: center;
  gap: 1.75rem;
}

.gh-link {
  color: #8b949e;
  font-size: 0.92rem;
  font-weight: 500;
  text-decoration: none;
  transition: color 0.2s ease;
  position: relative;
}

.gh-link:hover {
  color: #f0f6fc;
}

/* Action Buttons */
.gh-nav-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.gh-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 0.88rem;
  font-weight: 600;
  padding: 0.5rem 1.1rem;
  border-radius: 6px;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  white-space: nowrap;
}

.gh-btn-ghost {
  color: #c9d1d9;
  background: transparent;
  border: 1px solid transparent;
}

.gh-btn-ghost:hover {
  color: #f0f6fc;
  background: rgba(177, 186, 196, 0.12);
  border-color: rgba(240, 246, 252, 0.1);
}

.gh-btn-primary {
  color: #ffffff;
  background-color: #238636;
  border: 1px solid rgba(240, 246, 252, 0.1);
  box-shadow: 0 1px 0 rgba(1, 4, 9, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.03);
}

.gh-btn-primary:hover {
  background-color: #2ea043;
  border-color: rgba(240, 246, 252, 0.15);
  box-shadow: 0 0 14px rgba(46, 160, 67, 0.4);
  transform: translateY(-1px);
}

/* Hamburger */
.gh-hamburger-btn {
  display: none;
  flex-direction: column;
  justify-content: space-between;
  width: 28px;
  height: 20px;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0;
  z-index: 1001;
}

.gh-hamburger-btn span {
  display: block;
  height: 2px;
  width: 100%;
  background: #c9d1d9;
  border-radius: 2px;
  transition: all 0.3s ease;
}

.gh-hamburger-btn.is-active span:nth-child(1) {
  transform: translateY(9px) rotate(45deg);
}

.gh-hamburger-btn.is-active span:nth-child(2) {
  opacity: 0;
}

.gh-hamburger-btn.is-active span:nth-child(3) {
  transform: translateY(-9px) rotate(-45deg);
}

/* Mobile Menu */
.gh-mobile-menu {
  display: none;
  background: #161b22;
  border-bottom: 1px solid #30363d;
  padding: 1.25rem 1.5rem 1.75rem;
  box-shadow: 0 16px 32px rgba(1, 4, 9, 0.6);
}

.gh-mobile-links {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  margin-bottom: 1.25rem;
}

.gh-mobile-link {
  color: #c9d1d9;
  font-size: 1rem;
  font-weight: 500;
  text-decoration: none;
  padding: 0.5rem 0;
  border-bottom: 1px solid rgba(48, 54, 61, 0.3);
}

.gh-mobile-link:hover {
  color: #2ea043;
}

.gh-mobile-actions {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

/* Responsive */
@media (max-width: 860px) {
  .gh-nav-links,
  .gh-nav-actions {
    display: none;
  }

  .gh-hamburger-btn {
    display: flex;
  }

  .gh-mobile-menu {
    display: block;
  }
}
</style>
