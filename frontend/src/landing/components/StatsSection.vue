<script setup>
const stats = [
  {
    value: '+5,400',
    label: 'Productos registrados',
    icon: 'fas fa-seedling',
    subtext: 'En catálogo e inventario'
  },
  {
    value: '+1,250',
    label: 'Usuarios activos',
    icon: 'fas fa-users',
    subtext: 'Productores y compradores'
  },
  {
    value: '+8,900',
    label: 'Compras realizadas',
    icon: 'fas fa-shopping-bag',
    subtext: 'Órdenes despachadas con éxito'
  },
  {
    value: '100%',
    label: 'Facturas generadas',
    icon: 'fas fa-file-invoice',
    subtext: 'En tiempo real con firma PDF'
  }
]
</script>

<template>
  <section id="metricas" class="gh-section">
    <div class="gh-container">
      <div class="gh-stats-banner">
        <div class="gh-stats-grid">
          <div
            v-for="(stat, idx) in stats"
            :key="idx"
            class="gh-stat-item"
          >
            <div class="stat-icon-wrapper">
              <i :class="stat.icon"></i>
            </div>
            <div class="stat-number">{{ stat.value }}</div>
            <div class="stat-label">{{ stat.label }}</div>
            <div class="stat-sub">{{ stat.subtext }}</div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.gh-section {
  padding: 5rem 0;
  background: #0d1117;
  position: relative;
  border-top: 1px solid rgba(48, 54, 61, 0.5);
}

.gh-container {
  max-width: 1240px;
  margin: 0 auto;
  padding: 0 1.5rem;
}

.gh-stats-banner {
  background: linear-gradient(180deg, #161b22 0%, #0d1117 100%);
  border: 1px solid #30363d;
  border-radius: 16px;
  padding: 3rem 2rem;
  box-shadow: 0 16px 36px rgba(1, 4, 9, 0.5);
}

.gh-stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 2.5rem;
  text-align: center;
}

.gh-stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}

.stat-icon-wrapper {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: rgba(46, 160, 67, 0.12);
  border: 1px solid rgba(46, 160, 67, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  color: #3fb950;
  margin-bottom: 1rem;
}

.stat-number {
  font-size: clamp(2.4rem, 3.5vw, 3.2rem);
  font-weight: 800;
  color: #f0f6fc;
  letter-spacing: -0.03em;
  line-height: 1.1;
  margin-bottom: 0.4rem;
  background: linear-gradient(180deg, #ffffff 30%, #3fb950 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-label {
  font-size: 1rem;
  font-weight: 600;
  color: #c9d1d9;
  margin-bottom: 0.25rem;
}

.stat-sub {
  font-size: 0.8rem;
  color: #8b949e;
}
</style>
