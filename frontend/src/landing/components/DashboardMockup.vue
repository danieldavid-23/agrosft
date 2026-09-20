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
  background: radial-gradient(circle, rgba(98, 169, 107, 0.3) 0%, rgba(232, 133, 59, 0.15) 50%, transparent 75%);
  filter: blur(40px);
  z-index: 0;
  pointer-events: none;
}

.gh-mockup-window {
  position: relative;
  z-index: 1;
  background: rgba(10, 32, 16, 0.88);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 16px;
  box-shadow: 0 24px 50px rgba(0, 0, 0, 0.35), 0 0 25px rgba(60, 141, 60, 0.25);
  overflow: hidden;
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.3s ease;
}

.gh-mockup-window:hover {
  transform: translateY(-4px);
  box-shadow: 0 30px 60px rgba(0, 0, 0, 0.45), 0 0 30px rgba(60, 141, 60, 0.35);
  border-color: rgba(255, 255, 255, 0.3);
}

/* Header */
.gh-mockup-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(8, 22, 12, 0.95);
  padding: 0.85rem 1.15rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.12);
}

.gh-mockup-dots {
  display: flex;
  align-items: center;
  gap: 7px;
}

.dot {
  width: 11px;
  height: 11px;
  border-radius: 50%;
}

.dot-red { background: #ef4444; }
.dot-yellow { background: #f59e0b; }
.dot-green { background: #10b981; }

.gh-mockup-title {
  font-size: 0.82rem;
  font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;
  color: #cbd5e1;
}

.text-accent {
  color: #a7f3d0;
}

.gh-mockup-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(60, 141, 60, 0.25);
  border: 1px solid rgba(167, 243, 208, 0.4);
  padding: 0.25rem 0.65rem;
  border-radius: 20px;
  font-size: 0.72rem;
  font-weight: 600;
  color: #a7f3d0;
}

.pulse-indicator {
  width: 7px;
  height: 7px;
  background: #34d399;
  border-radius: 50%;
  box-shadow: 0 0 8px #34d399;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(52, 211, 153, 0.7); }
  70% { transform: scale(1.15); box-shadow: 0 0 0 6px rgba(52, 211, 153, 0); }
  100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(52, 211, 153, 0); }
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
  background: rgba(14, 42, 20, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 10px;
  padding: 0.85rem;
}

.metric-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.35rem;
}

.metric-label {
  font-size: 0.72rem;
  color: #cbd5e1;
  font-weight: 500;
}

.metric-val {
  font-size: 0.98rem;
  font-weight: 800;
  color: #ffffff;
}

.metric-inc {
  font-size: 0.7rem;
  color: #a7f3d0;
  font-weight: 700;
}

.metric-sub {
  font-size: 0.72rem;
  color: #94a3b8;
  font-weight: normal;
}

/* Table Section */
.mockup-section-card {
  background: rgba(14, 42, 20, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 10px;
  overflow: hidden;
}

.mockup-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  background: rgba(8, 22, 12, 0.75);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  font-size: 0.82rem;
}

.gh-mini-tag {
  font-size: 0.68rem;
  color: #a7f3d0;
  background: rgba(60, 141, 60, 0.25);
  border: 1px solid rgba(167, 243, 208, 0.3);
  padding: 0.18rem 0.5rem;
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
  padding: 0.6rem 0.85rem;
  color: #cbd5e1;
  font-weight: 600;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(8, 22, 12, 0.85);
}

.mockup-table td {
  padding: 0.6rem 0.85rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  color: #f1f5f9;
}

.text-code {
  font-family: ui-monospace, SFMono-Regular, monospace;
  color: #93c5fd;
  font-size: 0.72rem;
  font-weight: 600;
}

.cat-pill {
  background: rgba(255, 255, 255, 0.1);
  color: #e2e8f0;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
  font-size: 0.68rem;
}

.status-pill {
  font-size: 0.7rem;
  padding: 0.2rem 0.55rem;
  border-radius: 12px;
  font-weight: 700;
}

.status-green {
  background: rgba(46, 160, 67, 0.25);
  color: #a7f3d0;
  border: 1px solid rgba(167, 243, 208, 0.4);
}

.status-blue {
  background: rgba(58, 139, 200, 0.25);
  color: #bae6fd;
  border: 1px solid rgba(186, 230, 253, 0.4);
}

.status-yellow {
  background: rgba(232, 133, 59, 0.25);
  color: #fde047;
  border: 1px solid rgba(253, 224, 71, 0.4);
}

/* Activity Footer */
.mockup-activity-footer {
  background: rgba(8, 22, 12, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 0.6rem 0.85rem;
  font-size: 0.72rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.activity-label {
  color: #cbd5e1;
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
  color: #94a3b8;
  font-family: monospace;
}

.log-text {
  color: #e2e8f0;
}

@media (max-width: 600px) {
  .mockup-metrics-grid {
    grid-template-columns: 1fr;
  }
}
</style>
