<script setup>
import { ref } from 'vue'

const activeTab = ref('inventario')

const sampleProducts = [
  { id: 'PRD-01', name: 'Aguacate Hass Premium', cat: 'Frutas', stock: 450, unit: 'kg', price: '$8.500', status: 'Óptimo', statusClass: 'status-green' },
  { id: 'PRD-02', name: 'Café Especial Tostado', cat: 'Granos', stock: 120, unit: 'bolsas', price: '$24.000', status: 'En demanda', statusClass: 'status-blue' },
  { id: 'PRD-03', name: 'Plátano Hartón Verde', cat: 'Plátanos', stock: 38, unit: 'racimos', price: '$35.000', status: 'Stock Bajo', statusClass: 'status-yellow' },
  { id: 'PRD-04', name: 'Fertilizante Orgánico NPK', cat: 'Insumos', stock: 80, unit: 'bultos', price: '$95.000', status: 'Disponible', statusClass: 'status-green' }
]

const activityLogs = [
  { time: '10:42', text: 'Nueva factura #FAC-1082 generada en PDF', icon: 'fa-file-invoice' },
  { time: '09:15', text: 'Lote Aguacate sincronizado con Marketplace', icon: 'fa-sync-alt' },
  { time: '08:30', text: 'Sesión OAuth verificada desde Bogotá, COL', icon: 'fa-shield-check' }
]
</script>

<template>
  <div class="gh-mockup-wrapper">
    <!-- Ambient Glow Background -->
    <div class="gh-mockup-glow"></div>

    <!-- Window Container -->
    <div class="gh-mockup-window">
      <!-- Window Top Bar -->
      <div class="gh-mockup-header">
        <div class="gh-mockup-dots">
          <span class="dot dot-red"></span>
          <span class="dot dot-yellow"></span>
          <span class="dot dot-green"></span>
        </div>

        <div class="gh-mockup-title">
          <i class="fas fa-terminal me-2 text-muted"></i>
          <span class="text-white fw-bold">agrosft</span>
          <span class="text-muted">/</span>
          <span class="text-accent">dashboard.vue</span>
        </div>

        <div class="gh-mockup-badge">
          <span class="pulse-indicator"></span>
          <span>Sistema Activo</span>
        </div>
      </div>

      <!-- Dashboard Body -->
      <div class="gh-mockup-body">
        <!-- Top Metrics Cards -->
        <div class="mockup-metrics-grid">
          <div class="mockup-metric-card">
            <div class="metric-head">
              <span class="metric-label">Valor en Cosecha</span>
              <i class="fas fa-chart-line text-success"></i>
            </div>
            <div class="metric-val">$18.450.000 <span class="metric-inc">+12.4%</span></div>
          </div>

          <div class="mockup-metric-card">
            <div class="metric-head">
              <span class="metric-label">Lotes en Stock</span>
              <i class="fas fa-cubes text-accent"></i>
            </div>
            <div class="metric-val">142 <span class="metric-sub">ítems</span></div>
          </div>

          <div class="mockup-metric-card">
            <div class="metric-head">
              <span class="metric-label">Facturas Emitidas</span>
              <i class="fas fa-file-pdf text-danger"></i>
            </div>
            <div class="metric-val">38 <span class="metric-sub">hoy</span></div>
          </div>
        </div>

        <!-- Table View Section -->
        <div class="mockup-section-card">
          <div class="mockup-card-header">
            <div class="d-flex align-items-center gap-2">
              <i class="fas fa-seedling text-accent"></i>
              <span class="fw-semibold text-white">Monitoreo de Inventario Agrícola</span>
            </div>
            <span class="gh-mini-tag">Sincronizado</span>
          </div>

          <div class="mockup-table-container">
            <table class="mockup-table">
              <thead>
                <tr>
                  <th>Código</th>
                  <th>Producto</th>
                  <th>Categoría</th>
                  <th>Existencias</th>
                  <th>Precio Unitario</th>
                  <th>Estado</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in sampleProducts" :key="item.id">
                  <td class="text-code">{{ item.id }}</td>
                  <td class="text-white fw-medium">{{ item.name }}</td>
                  <td><span class="cat-pill">{{ item.cat }}</span></td>
                  <td><span class="text-white">{{ item.stock }}</span> <small class="text-muted">{{ item.unit }}</small></td>
                  <td class="text-success fw-bold">{{ item.price }}</td>
                  <td>
                    <span class="status-pill" :class="item.statusClass">
                      {{ item.status }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Activity Feed Mini Log -->
        <div class="mockup-activity-footer">
          <div class="activity-label">
            <i class="fas fa-bolt text-accent me-1"></i> Transacciones en vivo:
          </div>
          <div class="activity-scroll">
            <div v-for="(log, idx) in activityLogs" :key="idx" class="activity-item">
              <span class="log-time">[{{ log.time }}]</span>
              <span class="log-text">{{ log.text }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.gh-mockup-wrapper {
  position: relative;
  width: 100%;
  max-width: 620px;
  margin: 0 auto;
}

.gh-mockup-glow {
  position: absolute;
  top: 10%;
  left: 10%;
  right: 10%;
  bottom: 10%;
  background: radial-gradient(circle, rgba(46, 160, 67, 0.28) 0%, rgba(35, 134, 54, 0.1) 50%, transparent 75%);
  filter: blur(40px);
  z-index: 0;
  pointer-events: none;
}

.gh-mockup-window {
  position: relative;
  z-index: 1;
  background: #161b22;
  border: 1px solid #30363d;
  border-radius: 12px;
  box-shadow: 0 24px 48px rgba(1, 4, 9, 0.6), 0 0 1px rgba(240, 246, 252, 0.1);
  overflow: hidden;
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.3s ease;
}

.gh-mockup-window:hover {
  transform: translateY(-4px);
  box-shadow: 0 30px 60px rgba(1, 4, 9, 0.75), 0 0 25px rgba(46, 160, 67, 0.2);
  border-color: rgba(46, 160, 67, 0.4);
}

/* Header */
.gh-mockup-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #0d1117;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #30363d;
}

.gh-mockup-dots {
  display: flex;
  align-items: center;
  gap: 6px;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.dot-red { background: #ff5f56; }
.dot-yellow { background: #ffbd2e; }
.dot-green { background: #27c93f; }

.gh-mockup-title {
  font-size: 0.8rem;
  font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;
  color: #8b949e;
}

.text-accent {
  color: #3fb950;
}

.gh-mockup-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(46, 160, 67, 0.12);
  border: 1px solid rgba(46, 160, 67, 0.3);
  padding: 0.2rem 0.6rem;
  border-radius: 20px;
  font-size: 0.72rem;
  font-weight: 600;
  color: #3fb950;
}

.pulse-indicator {
  width: 6px;
  height: 6px;
  background: #2ea043;
  border-radius: 50%;
  box-shadow: 0 0 8px #2ea043;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(46, 160, 67, 0.7); }
  70% { transform: scale(1.15); box-shadow: 0 0 0 6px rgba(46, 160, 67, 0); }
  100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(46, 160, 67, 0); }
}

/* Body */
.gh-mockup-body {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* Metrics Grid */
.mockup-metrics-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
}

.mockup-metric-card {
  background: #0d1117;
  border: 1px solid #30363d;
  border-radius: 8px;
  padding: 0.75rem;
}

.metric-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.35rem;
}

.metric-label {
  font-size: 0.7rem;
  color: #8b949e;
  font-weight: 500;
}

.metric-val {
  font-size: 0.95rem;
  font-weight: 700;
  color: #f0f6fc;
}

.metric-inc {
  font-size: 0.68rem;
  color: #3fb950;
  font-weight: 600;
}

.metric-sub {
  font-size: 0.7rem;
  color: #8b949e;
  font-weight: normal;
}

/* Table Section */
.mockup-section-card {
  background: #0d1117;
  border: 1px solid #30363d;
  border-radius: 8px;
  overflow: hidden;
}

.mockup-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.65rem 0.85rem;
  background: rgba(48, 54, 61, 0.2);
  border-bottom: 1px solid #30363d;
  font-size: 0.8rem;
}

.gh-mini-tag {
  font-size: 0.68rem;
  color: #8b949e;
  background: #21262d;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
}

.mockup-table-container {
  overflow-x: auto;
}

.mockup-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.75rem;
  text-align: left;
}

.mockup-table th {
  padding: 0.5rem 0.75rem;
  color: #8b949e;
  font-weight: 600;
  border-bottom: 1px solid #21262d;
  background: #0d1117;
}

.mockup-table td {
  padding: 0.55rem 0.75rem;
  border-bottom: 1px solid #21262d;
  color: #c9d1d9;
}

.text-code {
  font-family: ui-monospace, SFMono-Regular, monospace;
  color: #79c0ff;
  font-size: 0.7rem;
}

.cat-pill {
  background: #21262d;
  color: #8b949e;
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
  font-size: 0.68rem;
}

.status-pill {
  font-size: 0.68rem;
  padding: 0.15rem 0.45rem;
  border-radius: 12px;
  font-weight: 600;
}

.status-green {
  background: rgba(46, 160, 67, 0.15);
  color: #3fb950;
  border: 1px solid rgba(46, 160, 67, 0.3);
}

.status-blue {
  background: rgba(56, 139, 253, 0.15);
  color: #58a6ff;
  border: 1px solid rgba(56, 139, 253, 0.3);
}

.status-yellow {
  background: rgba(210, 153, 34, 0.15);
  color: #d29922;
  border: 1px solid rgba(210, 153, 34, 0.3);
}

/* Activity Footer */
.mockup-activity-footer {
  background: #0d1117;
  border: 1px solid #30363d;
  border-radius: 6px;
  padding: 0.5rem 0.75rem;
  font-size: 0.72rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.activity-label {
  color: #8b949e;
  font-weight: 600;
  white-space: nowrap;
}

.activity-scroll {
  display: flex;
  gap: 1rem;
  overflow-x: auto;
  scrollbar-width: none;
}

.activity-scroll::-webkit-scrollbar {
  display: none;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 4px;
  white-space: nowrap;
}

.log-time {
  color: #8b949e;
  font-family: monospace;
}

.log-text {
  color: #c9d1d9;
}

@media (max-width: 600px) {
  .mockup-metrics-grid {
    grid-template-columns: 1fr;
  }
}
</style>
