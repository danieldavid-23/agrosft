<script setup>
import DashboardMockup from './DashboardMockup.vue'

defineProps({
  urls: {
    type: Object,
    default: () => ({})
  },
  isAuthenticated: {
    type: Boolean,
    default: false
  }
})
</script>

<template>
  <section class="gh-hero-section">
    <!-- Ambient Lighting & Grid Elements -->
    <div class="gh-hero-bg-glow"></div>
    <div class="gh-hero-grid-pattern"></div>

    <div class="gh-hero-container">
      <div class="gh-hero-grid">
        <!-- Left Content Column -->
        <div class="gh-hero-content">
          <!-- Announcement Pill -->
          <div class="gh-announcement-pill">
            <span class="pill-spark"><i class="fas fa-sparkles"></i></span>
            <span class="pill-text">Plataforma Agrícola Integral</span>
            <span class="pill-arrow"><i class="fas fa-chevron-right"></i></span>
          </div>

          <!-- Main Hero Title -->
          <h1 class="gh-hero-title">
            Gestiona tu producción <span class="gh-title-gradient">agrícola</span> de forma inteligente.
          </h1>

          <!-- Subtitle -->
          <p class="gh-hero-subtitle">
            AgroSFT integra inventario, marketplace, compras y facturación en una sola plataforma moderna y segura diseñada para potenciar el campo.
          </p>

          <!-- Action Buttons -->
          <div class="gh-hero-actions">
            <template v-if="isAuthenticated">
              <a :href="urls.marketplace || '/inventario/'" class="gh-btn-hero gh-btn-hero-primary">
                <i class="fas fa-arrow-right me-2"></i> Ir al Marketplace
              </a>
              <a :href="urls.mi_inventario || '/inventario/mis-productos/'" class="gh-btn-hero gh-btn-hero-secondary">
                <i class="fas fa-boxes me-2"></i> Mi Inventario
              </a>
            </template>
            <template v-else>
              <a :href="urls.registro || '/usuarios/registro/'" class="gh-btn-hero gh-btn-hero-primary">
                <span>Crear cuenta gratis</span>
                <i class="fas fa-arrow-right ms-2"></i>
              </a>
              <a :href="urls.login || '/usuarios/login/'" class="gh-btn-hero gh-btn-hero-secondary">
                <i class="fas fa-sign-in-alt me-2"></i> Iniciar sesión
              </a>
            </template>
          </div>

          <!-- Mini Feature Tags -->
          <div class="gh-hero-tags">
            <div class="tag-item">
              <i class="fas fa-check-circle text-accent"></i>
              <span>Sin costos ocultos</span>
            </div>
            <div class="tag-item">
              <i class="fas fa-check-circle text-accent"></i>
              <span>Facturación PDF instantánea</span>
            </div>
            <div class="tag-item">
              <i class="fas fa-check-circle text-accent"></i>
              <span>Acceso multidispositivo</span>
            </div>
          </div>
        </div>

        <!-- Right Visual Column (Mockup) -->
        <div class="gh-hero-visual">
          <DashboardMockup />
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.gh-hero-section {
  position: relative;
  min-height: calc(100vh - 70px);
  padding: 8.5rem 0 5rem;
  display: flex;
  align-items: center;
  background: #0d1117;
  overflow: hidden;
}

/* Background Effects */
.gh-hero-bg-glow {
  position: absolute;
  top: -150px;
  left: 50%;
  transform: translateX(-50%);
  width: 900px;
  height: 600px;
  background: radial-gradient(circle, rgba(46, 160, 67, 0.18) 0%, rgba(35, 134, 54, 0.06) 45%, transparent 70%);
  filter: blur(80px);
  pointer-events: none;
  z-index: 0;
}

.gh-hero-grid-pattern {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    linear-gradient(to right, rgba(48, 54, 61, 0.15) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(48, 54, 61, 0.15) 1px, transparent 1px);
  background-size: 40px 40px;
  mask-image: radial-gradient(ellipse at center, black 40%, transparent 80%);
  -webkit-mask-image: radial-gradient(ellipse at center, black 40%, transparent 80%);
  pointer-events: none;
  z-index: 0;
}

.gh-hero-container {
  position: relative;
  z-index: 1;
  max-width: 1240px;
  margin: 0 auto;
  padding: 0 1.5rem;
  width: 100%;
}

.gh-hero-grid {
  display: grid;
  grid-template-columns: 1.15fr 1fr;
  align-items: center;
  gap: 3.5rem;
}

/* Announcement Pill */
.gh-announcement-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(46, 160, 67, 0.1);
  border: 1px solid rgba(46, 160, 67, 0.35);
  border-radius: 30px;
  padding: 0.35rem 0.9rem;
  margin-bottom: 1.5rem;
  font-size: 0.8rem;
  color: #3fb950;
  transition: all 0.2s ease;
}

.gh-announcement-pill:hover {
  background: rgba(46, 160, 67, 0.18);
  border-color: rgba(46, 160, 67, 0.55);
}

.pill-spark {
  color: #2ea043;
}

.pill-text {
  font-weight: 600;
}

.pill-arrow {
  font-size: 0.65rem;
  opacity: 0.8;
}

/* Main Title */
.gh-hero-title {
  font-size: clamp(2.4rem, 4vw, 3.6rem);
  font-weight: 800;
  line-height: 1.12;
  letter-spacing: -0.035em;
  color: #f0f6fc;
  margin-bottom: 1.25rem;
}

.gh-title-gradient {
  background: linear-gradient(135deg, #3fb950 0%, #2ea043 50%, #56d364 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* Subtitle */
.gh-hero-subtitle {
  font-size: clamp(1rem, 1.3vw, 1.2rem);
  line-height: 1.6;
  color: #8b949e;
  margin-bottom: 2.25rem;
  max-width: 580px;
}

/* Actions */
.gh-hero-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2.5rem;
  flex-wrap: wrap;
}

.gh-btn-hero {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  font-weight: 600;
  padding: 0.85rem 1.75rem;
  border-radius: 8px;
  text-decoration: none;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  cursor: pointer;
}

.gh-btn-hero-primary {
  color: #ffffff;
  background-color: #238636;
  border: 1px solid rgba(240, 246, 252, 0.15);
  box-shadow: 0 4px 14px rgba(35, 134, 54, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.08);
}

.gh-btn-hero-primary:hover {
  background-color: #2ea043;
  box-shadow: 0 6px 20px rgba(46, 160, 67, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.12);
  transform: translateY(-2px);
}

.gh-btn-hero-secondary {
  color: #c9d1d9;
  background-color: #21262d;
  border: 1px solid #30363d;
}

.gh-btn-hero-secondary:hover {
  color: #f0f6fc;
  background-color: #30363d;
  border-color: #8b949e;
  transform: translateY(-2px);
}

/* Tags */
.gh-hero-tags {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.tag-item {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  font-size: 0.82rem;
  color: #8b949e;
  font-weight: 500;
}

.text-accent {
  color: #3fb950;
}

/* Responsive */
@media (max-width: 992px) {
  .gh-hero-grid {
    grid-template-columns: 1fr;
    gap: 3rem;
  }

  .gh-hero-content {
    text-align: center;
  }

  .gh-hero-subtitle {
    margin-left: auto;
    margin-right: auto;
  }

  .gh-hero-actions {
    justify-content: center;
  }

  .gh-hero-tags {
    justify-content: center;
  }
}
</style>
