<script setup>
const steps = [
  {
    step: '01',
    role: 'Navegador Web',
    tech: 'Cliente & PWA',
    icon: 'fas fa-globe',
    desc: 'El usuario accede desde cualquier dispositivo móvil o escritorio con interfaz responsiva y rápida.',
    badge: 'Frontend Client'
  },
  {
    step: '02',
    role: 'Interfaz Reactiva',
    tech: 'Vue.js 3 + Vite',
    icon: 'fab fa-vuejs',
    desc: 'Componentes reactivos modulares, renderizado dinámico, validaciones instantáneas y feedback visual.',
    badge: 'Single Page Layer'
  },
  {
    step: '03',
    role: 'Backend Robusto',
    tech: 'Django 4.2 / Python',
    icon: 'fab fa-python',
    desc: 'Arquitectura limpia por capas (Controllers, Services, Repositories, DTOs) con seguridad empresarial.',
    badge: 'Business Core'
  },
  {
    step: '04',
    role: 'Base de Datos',
    tech: 'MySQL / MariaDB',
    icon: 'fas fa-database',
    desc: 'Persistencia relacional con transacciones ACID, índices optimizados y respaldos de integridad agrícola.',
    badge: 'Persistent Storage'
  }
]
</script>

<template>
  <section id="como-funciona" class="gh-section">
    <div class="gh-container">
      <!-- Section Header -->
      <div class="gh-section-header text-center">
        <div class="gh-section-badge">
          <i class="fas fa-network-wired me-1"></i> Arquitectura Técnica
        </div>
        <h2 class="gh-section-title">
          Cómo funciona AgroSFT
        </h2>
        <p class="gh-section-sub">
          Un flujo arquitectónico desacoplado, seguro y de alto rendimiento que conecta al usuario con sus datos en milisegundos.
        </p>
      </div>

      <!-- Flow Container -->
      <div class="gh-flow-wrapper">
        <div class="gh-flow-grid">
          <template v-for="(item, idx) in steps" :key="item.step">
            <!-- Step Card -->
            <div class="gh-flow-card">
              <div class="flow-card-num">{{ item.step }}</div>
              
              <div class="flow-card-icon">
                <i :class="item.icon"></i>
              </div>

              <div class="flow-badge-pill">{{ item.badge }}</div>

              <h4 class="flow-role">{{ item.role }}</h4>
              <div class="flow-tech">{{ item.tech }}</div>
              <p class="flow-desc">{{ item.desc }}</p>
            </div>

            <!-- Connector (Arrows / Animated Flow Line) -->
            <div v-if="idx < steps.length - 1" class="gh-flow-connector">
              <div class="connector-line">
                <span class="connector-pulse"></span>
              </div>
              <div class="connector-arrow">
                <i class="fas fa-chevron-right d-none d-lg-block"></i>
                <i class="fas fa-chevron-down d-lg-none"></i>
              </div>
            </div>
          </template>
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

/* Flow Wrapper */
.gh-flow-wrapper {
  position: relative;
  margin-top: 2rem;
}

.gh-flow-grid {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

/* Flow Card */
.gh-flow-card {
  flex: 1;
  background: #161b22;
  border: 1px solid #30363d;
  border-radius: 12px;
  padding: 1.75rem 1.25rem;
  text-align: center;
  position: relative;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  min-height: 290px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.gh-flow-card:hover {
  transform: translateY(-5px);
  border-color: #2ea043;
  box-shadow: 0 16px 32px rgba(1, 4, 9, 0.6), 0 0 18px rgba(46, 160, 67, 0.18);
  background: #1c2128;
}

.flow-card-num {
  position: absolute;
  top: 12px;
  left: 14px;
  font-size: 0.72rem;
  font-weight: 700;
  color: #8b949e;
  font-family: ui-monospace, monospace;
}

.flow-card-icon {
  width: 52px;
  height: 52px;
  border-radius: 12px;
  background: rgba(46, 160, 67, 0.12);
  border: 1px solid rgba(46, 160, 67, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: #3fb950;
  margin: 0.5rem auto 1rem;
  transition: transform 0.25s ease;
}

.gh-flow-card:hover .flow-card-icon {
  transform: scale(1.1);
  background: #238636;
  color: #ffffff;
}

.flow-badge-pill {
  font-size: 0.68rem;
  font-weight: 600;
  color: #79c0ff;
  background: rgba(56, 139, 253, 0.12);
  border: 1px solid rgba(56, 139, 253, 0.3);
  padding: 0.15rem 0.55rem;
  border-radius: 12px;
  margin-bottom: 0.75rem;
}

.flow-role {
  font-size: 1.1rem;
  font-weight: 700;
  color: #f0f6fc;
  margin-bottom: 0.25rem;
}

.flow-tech {
  font-size: 0.82rem;
  font-weight: 600;
  color: #3fb950;
  font-family: ui-monospace, monospace;
  margin-bottom: 0.75rem;
}

.flow-desc {
  font-size: 0.82rem;
  color: #8b949e;
  line-height: 1.5;
  margin: 0;
}

/* Connectors */
.gh-flow-connector {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 0 0.5rem;
  color: #3fb950;
  position: relative;
}

.connector-line {
  display: none;
}

.connector-arrow {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #21262d;
  border: 1px solid #30363d;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  color: #3fb950;
}

/* Responsive */
@media (max-width: 992px) {
  .gh-flow-grid {
    flex-direction: column;
    gap: 1.25rem;
  }

  .gh-flow-card {
    width: 100%;
    max-width: 460px;
    min-height: auto;
  }

  .gh-flow-connector {
    padding: 0.25rem 0;
  }
}
</style>
