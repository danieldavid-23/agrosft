<script setup>
import { ref, onMounted } from 'vue'
import NavbarLanding from './components/NavbarLanding.vue'
import HeroSection from './components/HeroSection.vue'
import FeaturesSection from './components/FeaturesSection.vue'
import HowItWorksSection from './components/HowItWorksSection.vue'
import CtaSection from './components/CtaSection.vue'
import FooterLanding from './components/FooterLanding.vue'

const props = defineProps({
  urls: {
    type: Object,
    default: () => ({})
  },
  user: {
    type: Object,
    default: null
  },
  is_authenticated: {
    type: Boolean,
    default: false
  }
})

const isLoading = ref(true)
const currentTipIndex = ref(0)

const tips = [
  { icon: 'fas fa-lightbulb', title: 'Tip Agrícola', text: 'Mantener un inventario digitalizado reduce hasta un 25% las mermas y productos vencidos.' },
  { icon: 'fas fa-seedling', title: 'Buenas Prácticas', text: 'Registra tus lotes con fecha de corte para garantizar trazabilidad y mejor precio de venta.' },
  { icon: 'fas fa-file-invoice-dollar', title: 'Automatización', text: 'Genera facturas y comprobantes PDF al instante para agilizar tus cobros comerciales.' },
  { icon: 'fas fa-shield-alt', title: 'Seguridad AgroSFT', text: 'Tus datos agrícolas están blindados con cifrado de grado empresarial y protección CSRF.' },
  { icon: 'fas fa-store', title: 'Comercio Directo', text: 'Conecta en el Marketplace directamente con compradores eliminando intermediarios innecesarios.' }
]

onMounted(() => {
  // Select a random tip to display
  currentTipIndex.value = Math.floor(Math.random() * tips.length)

  // Setup smooth hide for loader
  setTimeout(() => {
    isLoading.value = false
  }, 950)

  // Setup Intersection Observer for smooth reveal animations on scroll
  const observerCallback = (entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('gh-revealed')
        observer.unobserve(entry.target)
      }
    })
  }

  const observer = new IntersectionObserver(observerCallback, {
    threshold: 0.1,
    rootMargin: '0px 0px -40px 0px'
  })

  document.querySelectorAll('.gh-reveal-on-scroll').forEach(el => {
    observer.observe(el)
  })
})
</script>

<template>
  <div class="gh-landing-root">
    <!-- Preloader Overlay with Spinner Wheel & Agricultural Tip -->
    <transition name="gh-loader-fade">
      <div v-if="isLoading" class="gh-preloader-overlay">
        <div class="gh-preloader-card">
          <!-- Spinner Wheel Container -->
          <div class="gh-spinner-wrapper">
            <svg class="gh-spinner-svg" viewBox="0 0 50 50">
              <circle class="gh-spinner-track" cx="25" cy="25" r="20" fill="none" stroke-width="3"></circle>
              <circle class="gh-spinner-circle" cx="25" cy="25" r="20" fill="none" stroke-width="3.5"></circle>
            </svg>
            <div class="gh-spinner-center">
              <img
                :src="urls.logo || '/static/img/agrosft_o.svg'"
                alt="AgroSFT"
                class="gh-spinner-logo"
              />
            </div>
          </div>

          <!-- Brand text -->
          <div class="gh-preloader-brand">
            Agro<span class="text-accent">SFT</span>
          </div>

          <!-- Loading Tip Box -->
          <div class="gh-tip-box">
            <div class="gh-tip-header">
              <i :class="tips[currentTipIndex].icon" class="text-accent me-2"></i>
              <span class="gh-tip-title">{{ tips[currentTipIndex].title }}</span>
            </div>
            <p class="gh-tip-text">{{ tips[currentTipIndex].text }}</p>
          </div>

          <!-- Subtle Progress dots -->
          <div class="gh-loading-dots">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    </transition>

    <!-- Navbar (Fixed Top) -->
    <NavbarLanding
      :urls="urls"
      :is-authenticated="is_authenticated"
      :user="user"
    />

    <!-- Hero Section -->
    <HeroSection
      :urls="urls"
      :is-authenticated="is_authenticated"
    />

    <!-- Features Section -->
    <div class="gh-reveal-on-scroll">
      <FeaturesSection />
    </div>

    <!-- How It Works Section -->
    <div class="gh-reveal-on-scroll">
      <HowItWorksSection />
    </div>

    <!-- Call to Action Banner -->
    <div class="gh-reveal-on-scroll">
      <CtaSection
        :urls="urls"
        :is-authenticated="is_authenticated"
      />
    </div>

    <!-- Footer -->
    <FooterLanding :urls="urls" />
  </div>
</template>

<style>
/* Global resets and typography for the landing root */
.gh-landing-root {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
  background-color: #0d1117;
  color: #c9d1d9;
  min-height: 100vh;
  overflow-x: hidden;
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  position: relative;
}

.gh-landing-root *,
.gh-landing-root *::before,
.gh-landing-root *::after {
  box-sizing: border-box;
}

.text-accent {
  color: #2ea043;
}

/* ============================================================
   PRELOADER & TIP WHEEL
   ============================================================ */
.gh-preloader-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 9999;
  background: #0d1117;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
}

.gh-preloader-card {
  background: #161b22;
  border: 1px solid #30363d;
  border-radius: 16px;
  padding: 2.5rem 2rem;
  max-width: 440px;
  width: 100%;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 24px 48px rgba(1, 4, 9, 0.75), 0 0 25px rgba(46, 160, 67, 0.15);
}

.gh-spinner-wrapper {
  position: relative;
  width: 72px;
  height: 72px;
  margin-bottom: 1.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.gh-spinner-svg {
  width: 100%;
  height: 100%;
  animation: rotateSpinner 1.4s linear infinite;
}

.gh-spinner-track {
  stroke: #21262d;
}

.gh-spinner-circle {
  stroke: #2ea043;
  stroke-linecap: round;
  stroke-dasharray: 90, 150;
  stroke-dashoffset: 0;
  animation: dashSpinner 1.4s ease-in-out infinite;
}

@keyframes rotateSpinner {
  100% {
    transform: rotate(360deg);
  }
}

@keyframes dashSpinner {
  0% {
    stroke-dasharray: 1, 150;
    stroke-dashoffset: 0;
  }
  50% {
    stroke-dasharray: 90, 150;
    stroke-dashoffset: -35;
  }
  100% {
    stroke-dasharray: 90, 150;
    stroke-dashoffset: -124;
  }
}

.gh-spinner-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.gh-spinner-logo {
  width: 100%;
  height: 100%;
  object-fit: contain;
  animation: pulseLogo 2s infinite ease-in-out;
}

@keyframes pulseLogo {
  0%, 100% { transform: scale(0.92); opacity: 0.85; }
  50% { transform: scale(1.08); opacity: 1; filter: drop-shadow(0 0 6px rgba(46, 160, 67, 0.6)); }
}

.gh-preloader-brand {
  font-size: 1.3rem;
  font-weight: 800;
  color: #f0f6fc;
  letter-spacing: -0.02em;
  margin-bottom: 1.5rem;
}

.gh-tip-box {
  background: #0d1117;
  border: 1px solid #30363d;
  border-radius: 10px;
  padding: 1rem 1.25rem;
  width: 100%;
  text-align: left;
  margin-bottom: 1.25rem;
}

.gh-tip-header {
  display: flex;
  align-items: center;
  margin-bottom: 0.4rem;
}

.gh-tip-title {
  font-size: 0.78rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: #c9d1d9;
}

.gh-tip-text {
  font-size: 0.85rem;
  color: #8b949e;
  line-height: 1.5;
  margin: 0;
}

.gh-loading-dots {
  display: flex;
  align-items: center;
  gap: 6px;
}

.gh-loading-dots span {
  width: 6px;
  height: 6px;
  background-color: #2ea043;
  border-radius: 50%;
  animation: loadingDot 1.2s infinite ease-in-out;
}

.gh-loading-dots span:nth-child(1) { animation-delay: -0.32s; }
.gh-loading-dots span:nth-child(2) { animation-delay: -0.16s; }
.gh-loading-dots span:nth-child(3) { animation-delay: 0s; }

@keyframes loadingDot {
  0%, 80%, 100% { transform: scale(0); opacity: 0.3; }
  40% { transform: scale(1); opacity: 1; }
}

/* Loader fade transition */
.gh-loader-fade-leave-active {
  transition: opacity 0.4s ease, transform 0.4s ease;
}

.gh-loader-fade-leave-to {
  opacity: 0;
  transform: scale(0.98);
}

/* Smooth Scroll Reveal Animations */
.gh-reveal-on-scroll {
  opacity: 0;
  transform: translateY(28px);
  transition: opacity 0.6s cubic-bezier(0.16, 1, 0.3, 1), transform 0.6s cubic-bezier(0.16, 1, 0.3, 1);
  will-change: opacity, transform;
}

.gh-reveal-on-scroll.gh-revealed {
  opacity: 1;
  transform: translateY(0);
}

/* Custom Scrollbar for Landing */
.gh-landing-root::-webkit-scrollbar {
  width: 10px;
}

.gh-landing-root::-webkit-scrollbar-track {
  background: #0d1117;
}

.gh-landing-root::-webkit-scrollbar-thumb {
  background: #30363d;
  border-radius: 5px;
}

.gh-landing-root::-webkit-scrollbar-thumb:hover {
  background: #2ea043;
}
</style>
