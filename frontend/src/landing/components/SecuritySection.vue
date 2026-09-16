<script setup>
const securityFeatures = [
  {
    id: 'oauth',
    title: 'Google OAuth 2.0',
    icon: 'fab fa-google',
    tag: 'Autenticación',
    desc: 'Inicio de sesión ágil y confiable integrado con cuentas de Google, verificación en dos pasos y control de identidades.',
    points: ['Integración social-auth', 'Flujo de autenticación seguro', 'Sincronización de avatar y perfil']
  },
  {
    id: 'csrf',
    title: 'Protección CSRF',
    icon: 'fas fa-shield-virus',
    tag: 'Criptografía Web',
    desc: 'Tokens CSRF dinámicos en cada petición POST/PUT que blindan todas las operaciones de inventario y compras contra falsificaciones.',
    points: ['Cabeceras X-CSRFToken estrictas', 'Validación por middleware Django', 'Sanitización contra XSS']
  },
  {
    id: 'sesiones',
    title: 'Sesiones Seguras',
    icon: 'fas fa-user-lock',
    tag: 'Privacidad',
    desc: 'Gestión de sesiones blindadas con cookies HttpOnly y SameSite, expiración programada y algoritmos de hashing modernos.',
    points: ['Cookies con flags de seguridad', 'Almacenamiento cifrado en servidor', 'Cierre de sesión multi-dispositivo']
  }
]
</script>

<template>
  <section id="seguridad" class="gh-section">
    <div class="gh-container">
      <!-- Section Header -->
      <div class="gh-section-header text-center">
        <div class="gh-section-badge">
          <i class="fas fa-shield-alt me-1"></i> Blindaje y Confianza
        </div>
        <h2 class="gh-section-title">
          Seguridad de grado empresarial
        </h2>
        <p class="gh-section-sub">
          Protegemos tu información productiva y comercial con las mejores prácticas y estándares de la industria del software.
        </p>
      </div>

      <!-- Security Cards Grid -->
      <div class="gh-security-grid">
        <div
          v-for="sec in securityFeatures"
          :key="sec.id"
          class="gh-security-card"
        >
          <div class="security-card-header">
            <div class="security-icon-wrap">
              <i :class="sec.icon"></i>
            </div>
            <span class="security-badge">{{ sec.tag }}</span>
          </div>

          <h3 class="security-title">{{ sec.title }}</h3>
          <p class="security-desc">{{ sec.desc }}</p>

          <ul class="security-points">
            <li v-for="(p, pIdx) in sec.points" :key="pIdx">
              <i class="fas fa-lock text-accent me-2"></i>
              <span>{{ p }}</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.gh-section {
  padding: 6rem 0;
  background: #0d1117;
  position: relative;
  border-top: 1px solid rgba(48, 54, 61, 0.5);
}

.gh-container {
  max-width: 1240px;
  margin: 0 auto;
  padding: 0 1.5rem;
}

.gh-section-header {
  max-width: 680px;
  margin: 0 auto 4rem;
}

.gh-section-badge {
  display: inline-flex;
  align-items: center;
  font-size: 0.8rem;
  font-weight: 600;
  color: #3fb950;
  background: rgba(46, 160, 67, 0.12);
  border: 1px solid rgba(46, 160, 67, 0.3);
  padding: 0.25rem 0.85rem;
  border-radius: 20px;
  margin-bottom: 1rem;
}

.gh-section-title {
  font-size: clamp(2rem, 3.2vw, 2.6rem);
  font-weight: 800;
  letter-spacing: -0.03em;
  color: #f0f6fc;
  margin-bottom: 1rem;
  line-height: 1.2;
}

.gh-section-sub {
  font-size: 1.05rem;
  color: #8b949e;
  line-height: 1.6;
}

/* Security Grid */
.gh-security-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

/* Security Card */
.gh-security-card {
  background: #161b22;
  border: 1px solid #30363d;
  border-radius: 12px;
  padding: 2.25rem 2rem;
  display: flex;
  flex-direction: column;
  transition: all 0.28s cubic-bezier(0.16, 1, 0.3, 1);
}

.gh-security-card:hover {
  transform: translateY(-6px);
  border-color: rgba(46, 160, 67, 0.6);
  box-shadow: 0 20px 40px rgba(1, 4, 9, 0.6), 0 0 22px rgba(46, 160, 67, 0.16);
  background: #1c2128;
}

.security-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}

.security-icon-wrap {
  width: 50px;
  height: 50px;
  border-radius: 10px;
  background: rgba(46, 160, 67, 0.12);
  border: 1px solid rgba(46, 160, 67, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.4rem;
  color: #3fb950;
  transition: all 0.25s ease;
}

.gh-security-card:hover .security-icon-wrap {
  background: #238636;
  color: #ffffff;
  transform: scale(1.08);
}

.security-badge {
  font-size: 0.72rem;
  font-weight: 600;
  color: #8b949e;
  background: #21262d;
  border: 1px solid #30363d;
  padding: 0.2rem 0.6rem;
  border-radius: 20px;
}

.security-title {
  font-size: 1.35rem;
  font-weight: 700;
  color: #f0f6fc;
  margin-bottom: 0.75rem;
  letter-spacing: -0.02em;
}

.security-desc {
  font-size: 0.92rem;
  color: #8b949e;
  line-height: 1.6;
  margin-bottom: 1.5rem;
  flex-grow: 1;
}

.security-points {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  border-top: 1px solid rgba(48, 54, 61, 0.5);
  padding-top: 1.25rem;
}

.security-points li {
  font-size: 0.85rem;
  color: #c9d1d9;
  display: flex;
  align-items: center;
}

.text-accent {
  color: #3fb950;
  font-size: 0.75rem;
}
</style>
