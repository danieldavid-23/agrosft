<script setup>
defineProps({
  urls: {
    type: Object,
    default: () => ({})
  }
})
</script>

<template>
  <footer class="gh-landing-footer">
    <div class="gh-container">
      <div class="gh-footer-content">
        <!-- Brand Info -->
        <div class="gh-footer-brand">
          <div class="d-flex align-items-center gap-2 mb-2">
            <div class="footer-logo-wrap">
              <img
                :src="urls.logo || '/static/img/agrosft_o.svg'"
                alt="AgroSFT Logo"
                class="footer-logo-img"
              />
            </div>
            <span class="footer-brand-name">Agro<span class="text-accent">SFT</span></span>
          </div>
          <p class="footer-tagline">
            Plataforma integral de gestión agropecuaria, marketplace directo y facturación automatizada.
          </p>
        </div>

        <!-- Links -->
        <div class="gh-footer-links">
          <div class="link-group">
            <span class="link-group-title">Navegación</span>
            <a href="#" class="footer-link">Inicio</a>
            <a :href="urls.login || '/usuarios/login/'" class="footer-link">Iniciar Sesión</a>
            <a :href="urls.registro || '/usuarios/registro/'" class="footer-link">Registro</a>
          </div>

          <div class="link-group">
            <span class="link-group-title">Plataforma</span>
            <a href="#caracteristicas" class="footer-link">Características</a>
            <a href="#como-funciona" class="footer-link">Arquitectura</a>
          </div>

          <div class="link-group">
            <span class="link-group-title">Legal & Soporte</span>
            <a :href="urls.terminos || '/usuarios/terminos/'" class="footer-link">Términos y Condiciones</a>
            <a href="mailto:soporte@agrosft.com" class="footer-link">Contacto de Soporte</a>
          </div>
        </div>
      </div>

      <!-- Bottom Bar -->
      <div class="gh-footer-bottom">
        <p class="copyright-text">
          &copy; {{ new Date().getFullYear() }} AgroSFT. Todos los derechos reservados.
        </p>
        <div class="footer-badges">
          <span class="tech-badge"><i class="fab fa-python text-accent me-1"></i> Django</span>
          <span class="tech-badge"><i class="fab fa-vuejs text-accent me-1"></i> Vue.js 3</span>
          <span class="tech-badge"><i class="fas fa-database text-accent me-1"></i> MySQL</span>
        </div>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.gh-landing-footer {
  background: #0d1117;
  border-top: 1px solid #30363d;
  padding: 4.5rem 0 2.5rem;
  color: #8b949e;
  font-size: 0.9rem;
}

.gh-container {
  max-width: 1240px;
  margin: 0 auto;
  padding: 0 1.5rem;
}

.gh-footer-content {
  display: grid;
  grid-template-columns: 1.2fr 2fr;
  gap: 3.5rem;
  margin-bottom: 3.5rem;
}

.footer-logo-wrap {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: rgba(46, 160, 67, 0.12);
  border: 1px solid rgba(46, 160, 67, 0.3);
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.footer-logo-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.footer-brand-name {
  font-size: 1.2rem;
  font-weight: 700;
  color: #f0f6fc;
}

.text-accent {
  color: #3fb950;
}

.footer-tagline {
  font-size: 0.88rem;
  color: #8b949e;
  line-height: 1.6;
  max-width: 340px;
}

.gh-footer-links {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2rem;
}

.link-group {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.link-group-title {
  font-size: 0.82rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #c9d1d9;
  margin-bottom: 0.35rem;
}

.footer-link {
  color: #8b949e;
  text-decoration: none;
  font-size: 0.88rem;
  transition: color 0.2s ease;
}

.footer-link:hover {
  color: #3fb950;
}

/* Bottom Bar */
.gh-footer-bottom {
  border-top: 1px solid #21262d;
  padding-top: 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
}

.copyright-text {
  font-size: 0.82rem;
  color: #8b949e;
  margin: 0;
}

.footer-badges {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.tech-badge {
  font-size: 0.72rem;
  font-weight: 600;
  color: #8b949e;
  background: #161b22;
  border: 1px solid #30363d;
  padding: 0.2rem 0.6rem;
  border-radius: 6px;
}

@media (max-width: 860px) {
  .gh-footer-content {
    grid-template-columns: 1fr;
    gap: 2.5rem;
  }

  .gh-footer-links {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 540px) {
  .gh-footer-links {
    grid-template-columns: 1fr;
  }

  .gh-footer-bottom {
    flex-direction: column;
    text-align: center;
  }
}
</style>
