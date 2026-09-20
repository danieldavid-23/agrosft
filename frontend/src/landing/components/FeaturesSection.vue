<script setup>
const features = [
  {
    id: 'inventario',
    title: 'Inventario Inteligente',
    tag: 'Control Total',
    icon: 'fas fa-boxes-stacked',
    description: 'Gestiona insumos, semillas, fertilizantes y lotes cosechados con control de stock mínimo en tiempo real y alertas de vencimiento.',
    bullets: [
      'Trazabilidad por lote y fecha de corte',
      'Alertas de reabastecimiento crítico',
      'Categorización agrícola personalizada'
    ],
    accentColor: '#3fb950'
  },
  {
    id: 'marketplace',
    title: 'Marketplace Agrícola',
    tag: 'Comercio Directo',
    icon: 'fas fa-store-alt',
    description: 'Publica y comercializa productos del campo directamente con compradores y empresas eliminando la intermediación innecesaria.',
    bullets: [
      'Vitrina digital para productores',
      'Carrito de compras ágil y flexible',
      'Filtros por categoría y precios'
    ],
    accentColor: '#2ea043'
  },
  {
    id: 'compras',
    title: 'Compras y Pedidos',
    tag: 'Flujo Comercial',
    icon: 'fas fa-clipboard-check',
    description: 'Administra tus solicitudes de abastecimiento, seguimiento de estados de órdenes de compra y control de proveedores en un solo lugar.',
    bullets: [
      'Gestión de órdenes de compra y venta',
      'Seguimiento en vivo de estados',
      'Historial detallado por cliente'
    ],
    accentColor: '#56d364'
  },
  {
    id: 'facturacion',
    title: 'Facturación PDF',
    tag: 'Automatización',
    icon: 'fas fa-file-invoice-dollar',
    description: 'Genera comprobantes oficiales, liquidaciones de cosecha y facturas comerciales con exportación instantánea a formato PDF imprimible.',
    bullets: [
      'Plantillas de factura profesional',
      'Cálculo de impuestos y subtotales',
      'Descarga e historial de documentos'
    ],
    accentColor: '#39d353'
  }
]
</script>

<template>
  <section id="caracteristicas" class="gh-section">
    <div class="gh-container">
      <!-- Section Header -->
      <div class="gh-section-header text-center">
        <div class="gh-section-badge">
          <i class="fas fa-layer-group me-1"></i> Módulos Especializados
        </div>
        <h2 class="gh-section-title">
          Todo lo que tu operación agrícola necesita
        </h2>
        <p class="gh-section-sub">
          Módulos diseñados para optimizar cada etapa del ciclo productivo y comercial del campo.
        </p>
      </div>

      <!-- Feature Cards Grid -->
      <div class="gh-features-grid">
        <div
          v-for="feature in features"
          :key="feature.id"
          class="gh-feature-card"
        >
          <!-- Card Header & Icon -->
          <div class="feature-card-top">
            <div class="feature-icon-wrapper">
              <i :class="feature.icon"></i>
            </div>
            <span class="feature-tag">{{ feature.tag }}</span>
          </div>

          <!-- Title & Description -->
          <h3 class="feature-title">{{ feature.title }}</h3>
          <p class="feature-desc">{{ feature.description }}</p>

          <!-- Bullet Points -->
          <ul class="feature-bullets">
            <li v-for="(bullet, bIdx) in feature.bullets" :key="bIdx">
              <i class="fas fa-check text-accent me-2"></i>
              <span>{{ bullet }}</span>
            </li>
          </ul>

          <!-- Card Bottom Glow Line -->
          <div class="feature-hover-indicator"></div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.gh-section {
  padding: 6.5rem 0;
  background: #F5F1E8;
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

/* Features Grid */
.gh-features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(270px, 1fr));
  gap: 1.75rem;
}

/* Feature Card */
.gh-feature-card {
  position: relative;
  background: #ffffff;
  border: 1px solid #D6D8CC;
  border-radius: 16px;
  padding: 2.25rem 1.85rem;
  display: flex;
  flex-direction: column;
  transition: all 0.28s cubic-bezier(0.16, 1, 0.3, 1);
  overflow: hidden;
  box-shadow: 0 4px 14px rgba(39, 64, 45, 0.04);
}

.gh-feature-card:hover {
  transform: translateY(-6px);
  border-color: #3C8D3C;
  box-shadow: 0 20px 40px rgba(39, 64, 45, 0.1), 0 0 16px rgba(60, 141, 60, 0.12);
}

.feature-card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}

.feature-icon-wrapper {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  background: #E8F5E8;
  border: 1px solid rgba(60, 141, 60, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.35rem;
  color: #3C8D3C;
  transition: all 0.25s ease;
}

.gh-feature-card:hover .feature-icon-wrapper {
  background: #3C8D3C;
  color: #ffffff;
  border-color: #2E7535;
  transform: scale(1.06);
}

.feature-tag {
  font-size: 0.74rem;
  font-weight: 700;
  color: #2E7535;
  background: #E8F5E8;
  border: 1px solid rgba(60, 141, 60, 0.2);
  padding: 0.25rem 0.7rem;
  border-radius: 20px;
}

.feature-title {
  font-size: 1.35rem;
  font-weight: 800;
  color: #27402d;
  margin-bottom: 0.75rem;
  letter-spacing: -0.02em;
}

.feature-desc {
  font-size: 0.92rem;
  color: #52635a;
  line-height: 1.6;
  margin-bottom: 1.5rem;
  flex-grow: 1;
}

.feature-bullets {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  border-top: 1px solid #EAECE4;
  padding-top: 1.25rem;
}

.feature-bullets li {
  font-size: 0.88rem;
  color: #3D5245;
  display: flex;
  align-items: flex-start;
}

.text-accent {
  color: #3C8D3C;
  font-size: 0.82rem;
  margin-top: 3px;
}

.feature-hover-indicator {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, transparent, #3C8D3C, transparent);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.gh-feature-card:hover .feature-hover-indicator {
  opacity: 1;
}
</style>
