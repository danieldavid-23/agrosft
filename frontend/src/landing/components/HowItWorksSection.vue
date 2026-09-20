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
  padding: 6.5rem 0;
  background: #ffffff;
  position: relative;
  border-top: 1px solid #D6D8CC;
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
  font-size: 0.82rem;
  font-weight: 700;
  color: #2E7535;
  background: #E8F5E8;
  border: 1px solid rgba(60, 141, 60, 0.25);
  padding: 0.3rem 0.95rem;
  border-radius: 20px;
  margin-bottom: 1.1rem;
}

.gh-section-title {
  font-size: clamp(2rem, 3.2vw, 2.6rem);
  font-weight: 800;
  letter-spacing: -0.03em;
  color: #27402d;
  margin-bottom: 1rem;
  line-height: 1.2;
}

.gh-section-sub {
  font-size: 1.05rem;
  color: #52635a;
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
  background: #F5F1E8;
  border: 1px solid #D6D8CC;
  border-radius: 16px;
  padding: 2rem 1.35rem;
  text-align: center;
  position: relative;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  min-height: 290px;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 4px 12px rgba(39, 64, 45, 0.04);
}

.gh-flow-card:hover {
  transform: translateY(-5px);
  border-color: #3C8D3C;
  box-shadow: 0 16px 32px rgba(39, 64, 45, 0.1);
  background: #faf7f0;
}

.flow-card-num {
  position: absolute;
  top: 12px;
  left: 14px;
  font-size: 0.74rem;
  font-weight: 700;
  color: #7A8A7D;
  font-family: ui-monospace, monospace;
}

.flow-card-icon {
  width: 54px;
  height: 54px;
  border-radius: 14px;
  background: #E8F5E8;
  border: 1px solid rgba(60, 141, 60, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: #3C8D3C;
  margin: 0.5rem auto 1rem;
  transition: transform 0.25s ease;
}

.gh-flow-card:hover .flow-card-icon {
  transform: scale(1.1);
  background: #3C8D3C;
  color: #ffffff;
}

.flow-badge-pill {
  font-size: 0.7rem;
  font-weight: 700;
  color: #25632C;
  background: #E8F5E8;
  border: 1px solid rgba(60, 141, 60, 0.25);
  padding: 0.2rem 0.65rem;
  border-radius: 12px;
  margin-bottom: 0.75rem;
}

.flow-role {
  font-size: 1.15rem;
  font-weight: 800;
  color: #27402d;
  margin-bottom: 0.25rem;
}

.flow-tech {
  font-size: 0.84rem;
  font-weight: 700;
  color: #3C8D3C;
  font-family: ui-monospace, monospace;
  margin-bottom: 0.75rem;
}

.flow-desc {
  font-size: 0.85rem;
  color: #52635a;
  line-height: 1.55;
  margin: 0;
}

/* Connectors */
.gh-flow-connector {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 0 0.5rem;
  color: #3C8D3C;
  position: relative;
}

.connector-line {
  display: none;
}

.connector-arrow {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: #ffffff;
  border: 1.5px solid #D6D8CC;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  color: #3C8D3C;
  box-shadow: 0 2px 8px rgba(39, 64, 45, 0.08);
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
