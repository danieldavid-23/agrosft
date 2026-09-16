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
  padding: 5rem 0 6rem;
  background: #0d1117;
  position: relative;
}

.gh-container {
  max-width: 1240px;
  margin: 0 auto;
  padding: 0 1.5rem;
}

.gh-cta-card {
  position: relative;
  background: linear-gradient(135deg, #161b22 0%, #0d1117 100%);
  border: 1px solid rgba(46, 160, 67, 0.4);
  border-radius: 20px;
  padding: 4.5rem 2rem;
  overflow: hidden;
  box-shadow: 0 24px 60px rgba(1, 4, 9, 0.8), 0 0 35px rgba(46, 160, 67, 0.15);
}

.cta-glow {
  position: absolute;
  top: -80px;
  left: 50%;
  transform: translateX(-50%);
  width: 500px;
  height: 250px;
  background: radial-gradient(circle, rgba(46, 160, 67, 0.3) 0%, transparent 70%);
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
  font-weight: 600;
  color: #3fb950;
  background: rgba(46, 160, 67, 0.15);
  border: 1px solid rgba(46, 160, 67, 0.4);
  padding: 0.3rem 0.95rem;
  border-radius: 20px;
  margin-bottom: 1.5rem;
}

.cta-title {
  font-size: clamp(2.2rem, 3.8vw, 3rem);
  font-weight: 800;
  color: #f0f6fc;
  letter-spacing: -0.03em;
  line-height: 1.15;
  margin-bottom: 1.25rem;
}

.cta-subtitle {
  font-size: 1.1rem;
  color: #8b949e;
  line-height: 1.6;
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
  font-weight: 600;
  padding: 0.85rem 2rem;
  border-radius: 8px;
  color: #ffffff;
  background-color: #238636;
  border: 1px solid rgba(240, 246, 252, 0.15);
  text-decoration: none;
  box-shadow: 0 4px 14px rgba(35, 134, 54, 0.4);
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  cursor: pointer;
}

.btn-cta-primary:hover {
  background-color: #2ea043;
  box-shadow: 0 6px 22px rgba(46, 160, 67, 0.55);
  transform: translateY(-2px);
}

.btn-cta-secondary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  font-weight: 600;
  padding: 0.85rem 1.85rem;
  border-radius: 8px;
  color: #c9d1d9;
  background-color: #21262d;
  border: 1px solid #30363d;
  text-decoration: none;
  transition: all 0.25s ease;
  cursor: pointer;
}

.btn-cta-secondary:hover {
  color: #f0f6fc;
  background-color: #30363d;
  border-color: #8b949e;
  transform: translateY(-2px);
}
</style>
