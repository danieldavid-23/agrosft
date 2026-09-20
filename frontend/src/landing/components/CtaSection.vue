<script setup>
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
  <section class="gh-cta-section">
    <div class="gh-container">
      <div class="gh-cta-card">
        <!-- Glow accents -->
        <div class="cta-glow"></div>

        <div class="cta-content text-center">
          <div class="cta-badge">
            <i class="fas fa-rocket me-1"></i> Transformación Digital
          </div>

          <h2 class="cta-title">
            Empieza hoy a digitalizar tu gestión agrícola.
          </h2>

          <p class="cta-subtitle">
            Únete a la red moderna de productores y distribuidores del campo. Optimiza tu inventario, expande tus ventas y automatiza tus facturas en minutos.
          </p>

          <div class="cta-actions">
            <template v-if="isAuthenticated">
              <a :href="urls.marketplace || '/inventario/'" class="btn-cta-primary">
                <i class="fas fa-store me-2"></i> Ir al Marketplace
              </a>
            </template>
            <template v-else>
              <a :href="urls.registro || '/usuarios/registro/'" class="btn-cta-primary">
                <span>Registrarse gratis</span>
                <i class="fas fa-arrow-right ms-2"></i>
              </a>
              <a :href="urls.login || '/usuarios/login/'" class="btn-cta-secondary">
                <i class="fas fa-sign-in-alt me-2"></i> Iniciar sesión
              </a>
            </template>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.gh-cta-section {
  padding: 5rem 0 6.5rem;
  background: #F5F1E8;
  position: relative;
}

.gh-container {
  max-width: 1240px;
  margin: 0 auto;
  padding: 0 1.5rem;
}

.gh-cta-card {
  position: relative;
  background: linear-gradient(135deg, #133f18 0%, #1f6326 50%, #2e7d33 100%);
  border: 1px solid rgba(255, 255, 255, 0.22);
  border-radius: 24px;
  padding: 4.5rem 2rem;
  overflow: hidden;
  box-shadow: 0 24px 50px rgba(19, 63, 24, 0.25), 0 8px 24px rgba(0, 0, 0, 0.08);
}

.cta-glow {
  position: absolute;
  top: -80px;
  left: 50%;
  transform: translateX(-50%);
  width: 550px;
  height: 280px;
  background: radial-gradient(circle, rgba(98, 169, 107, 0.25) 0%, rgba(232, 133, 59, 0.15) 50%, transparent 70%);
  filter: blur(50px);
  pointer-events: none;
}

.cta-content {
  position: relative;
  z-index: 1;
  max-width: 720px;
  margin: 0 auto;
}

.cta-badge {
  display: inline-flex;
  align-items: center;
  font-size: 0.82rem;
  font-weight: 700;
  color: #ffffff;
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 0.35rem 1rem;
  border-radius: 20px;
  margin-bottom: 1.5rem;
}

.cta-title {
  font-size: clamp(2.2rem, 3.8vw, 3rem);
  font-weight: 900;
  color: #ffffff;
  letter-spacing: -0.03em;
  line-height: 1.15;
  margin-bottom: 1.25rem;
  text-shadow: 0 2px 20px rgba(0, 0, 0, 0.25);
}

.cta-subtitle {
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.88);
  line-height: 1.65;
  margin-bottom: 2.5rem;
}

.cta-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.btn-cta-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  font-weight: 700;
  padding: 0.85rem 2rem;
  border-radius: 10px;
  color: #ffffff;
  background: linear-gradient(135deg, #E8853B 0%, #D97A30 100%);
  border: 1px solid rgba(255, 255, 255, 0.2);
  text-decoration: none;
  box-shadow: 0 8px 24px rgba(232, 133, 59, 0.45);
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  cursor: pointer;
}

.btn-cta-primary:hover {
  background: linear-gradient(135deg, #f09247 0%, #e08337 100%);
  box-shadow: 0 12px 30px rgba(232, 133, 59, 0.6);
  transform: translateY(-2px);
  color: #ffffff;
}

.btn-cta-secondary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  font-weight: 600;
  padding: 0.85rem 1.85rem;
  border-radius: 10px;
  color: #ffffff;
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(8px);
  border: 1.5px solid rgba(255, 255, 255, 0.35);
  text-decoration: none;
  transition: all 0.25s ease;
  cursor: pointer;
}

.btn-cta-secondary:hover {
  color: #ffffff;
  background: rgba(255, 255, 255, 0.22);
  border-color: rgba(255, 255, 255, 0.6);
  transform: translateY(-2px);
}
</style>
