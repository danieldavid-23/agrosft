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
  padding: 8.5rem 0 5.5rem;
  display: flex;
  align-items: center;
  background: linear-gradient(165deg, #133f18 0%, #1f6326 45%, #2e7d33 100%);
  overflow: hidden;
}

/* Background Effects */
.gh-hero-bg-glow {
  position: absolute;
  top: -150px;
  left: 50%;
  transform: translateX(-50%);
  width: 950px;
  height: 650px;
  background: radial-gradient(circle, rgba(98, 169, 107, 0.22) 0%, rgba(232, 133, 59, 0.12) 40%, transparent 70%);
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
  background-image: radial-gradient(rgba(255, 255, 255, 0.12) 1.2px, transparent 1.2px);
  background-size: 28px 28px;
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
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.28);
  backdrop-filter: blur(8px);
  border-radius: 30px;
  padding: 0.4rem 1rem;
  margin-bottom: 1.5rem;
  font-size: 0.82rem;
  color: #ffffff;
  transition: all 0.2s ease;
}

.gh-announcement-pill:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.45);
}

.pill-spark {
  color: #E8853B;
}

.pill-text {
  font-weight: 600;
  letter-spacing: 0.02em;
}

.pill-arrow {
  font-size: 0.65rem;
  opacity: 0.85;
}

/* Main Title */
.gh-hero-title {
  font-size: clamp(2.4rem, 4vw, 3.6rem);
  font-weight: 900;
  line-height: 1.12;
  letter-spacing: -0.035em;
  color: #ffffff;
  text-shadow: 0 2px 20px rgba(0, 0, 0, 0.25);
  margin-bottom: 1.25rem;
}

.gh-title-gradient {
  background: linear-gradient(135deg, #a7f3d0 0%, #6ee7b7 50%, #fde047 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* Subtitle */
.gh-hero-subtitle {
  font-size: clamp(1rem, 1.3vw, 1.2rem);
  line-height: 1.65;
  color: rgba(255, 255, 255, 0.88);
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
  font-weight: 700;
  padding: 0.85rem 1.85rem;
  border-radius: 10px;
  text-decoration: none;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  cursor: pointer;
}

.gh-btn-hero-primary {
  color: #ffffff;
  background: linear-gradient(135deg, #E8853B 0%, #D97A30 100%);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 24px rgba(232, 133, 59, 0.45);
}

.gh-btn-hero-primary:hover {
  background: linear-gradient(135deg, #f09247 0%, #e08337 100%);
  box-shadow: 0 12px 30px rgba(232, 133, 59, 0.6);
  transform: translateY(-2px);
  color: #ffffff;
}

.gh-btn-hero-secondary {
  color: #ffffff;
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(8px);
  border: 1.5px solid rgba(255, 255, 255, 0.35);
}

.gh-btn-hero-secondary:hover {
  color: #ffffff;
  background: rgba(255, 255, 255, 0.22);
  border-color: rgba(255, 255, 255, 0.6);
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
  gap: 0.5rem;
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.92);
  font-weight: 600;
}

.text-accent {
  color: #a7f3d0;
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
