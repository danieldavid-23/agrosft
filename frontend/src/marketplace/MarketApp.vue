<script setup>
import { ref, watch, onMounted } from 'vue'
import { getCSRFToken } from '../shared/csrf.js'

const props = defineProps({
  initialProducts: Array,
  categories: Array,
  urls: Object
})

const products = ref(props.initialProducts)
const search = ref('')
const selectedCategory = ref('')
const sortBy = ref('reciente')
const page = ref(1)
const loading = ref(false)
const hasNext = ref(false)
const hasPrev = ref(false)

async function fetchProducts() {
  loading.value = true
  const params = new URLSearchParams()
  if (search.value) params.append('q', search.value)
  if (selectedCategory.value) params.append('categoria', selectedCategory.value)
  if (sortBy.value) params.append('orden', sortBy.value)
  params.append('page', page.value)
  params.append('ajax', '1')

  const res = await fetch(props.urls.marketplace + '?' + params.toString(), {
    headers: { 'X-Requested-With': 'XMLHttpRequest' }
  })
  const data = await res.json()
  products.value = data.products
  hasNext.value = data.has_next
  hasPrev.value = data.has_prev
  loading.value = false
}

watch([search, selectedCategory, sortBy], () => {
  page.value = 1
  fetchProducts()
})

async function agregarCarrito(productoId) {
  const formData = new URLSearchParams()
  formData.append('cantidad', '1')
  const res = await fetch(props.urls.addToCart.replace('0', productoId), {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCSRFToken(),
      'Content-Type': 'application/x-www-form-urlencoded',
      'X-Requested-With': 'XMLHttpRequest',
    },
    body: formData
  })
  if (res.ok) {
    const item = products.value.find(p => p.id === productoId)
    if (item) item.added = true
    setTimeout(() => { if (item) item.added = false }, 2000)
  }
}

function formatearPrecio(valor) {
  return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(valor)
}
</script>

<template>
  <!-- Filtros -->
  <div class="card shadow-sm mb-5 border-0 rounded-4">
    <div class="card-body p-4">
      <div class="row g-3">
        <div class="col-md-5">
          <label class="form-label text-muted small fw-bold text-uppercase mb-1">Buscar</label>
          <div class="input-group">
            <span class="input-group-text bg-light border-end-0">
              <i class="fas fa-search text-muted"></i>
            </span>
            <input type="text" v-model="search" class="form-control border-start-0 bg-light ps-0" placeholder="Ej: Tomate, Maíz...">
          </div>
        </div>
        <div class="col-md-3">
          <label class="form-label text-muted small fw-bold text-uppercase mb-1">Categoría</label>
          <select v-model="selectedCategory" class="form-select bg-light">
            <option value="">Todas las categorías</option>
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.nombre }}</option>
          </select>
        </div>
        <div class="col-md-2">
          <label class="form-label text-muted small fw-bold text-uppercase mb-1">Ordenar por</label>
          <select v-model="sortBy" class="form-select bg-light">
            <option value="reciente">Más recientes</option>
            <option value="precio_asc">Menor Precio</option>
            <option value="precio_desc">Mayor Precio</option>
            <option value="nombre">Nombre A-Z</option>
          </select>
        </div>
        <div class="col-md-2 d-flex align-items-end">
          <button class="btn btn-outline-success w-100 fw-bold" @click="fetchProducts">
            <i class="fas fa-filter me-2"></i>Aplicar
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- Loading -->
  <div v-if="loading" class="text-center py-5">
    <div class="spinner-border text-success" role="status">
      <span class="visually-hidden">Cargando...</span>
    </div>
  </div>

  <!-- Grid -->
  <div v-else class="row g-4">
    <div v-for="producto in products" :key="producto.id" class="col-xl-3 col-lg-4 col-md-6">
      <div class="card h-100 hover-card border-0 rounded-4 position-relative">
        <div class="product-image-container bg-light rounded-top-4 overflow-hidden position-relative">
          <div v-if="producto.imagen" class="d-flex justify-content-center align-items-center h-100 bg-white" style="min-height: 220px;">
            <img :src="producto.imagen" class="product-image" :alt="producto.nombre">
          </div>
          <div v-else class="d-flex justify-content-center align-items-center h-100 bg-white" style="min-height: 220px;">
            <div class="bg-success bg-opacity-10 p-4 rounded-circle">
              <i class="fas fa-seedling fa-3x text-success"></i>
            </div>
          </div>
          <div class="position-absolute top-0 end-0 p-3 d-flex flex-column gap-2 align-items-end">
            <span v-if="producto.esta_agotado" class="badge bg-danger shadow-sm"><i class="fas fa-times-circle me-1"></i>Agotado</span>
            <span v-else-if="producto.stock < producto.stock_minimo" class="badge bg-warning shadow-sm text-dark"><i class="fas fa-exclamation-triangle me-1"></i>Últimas unid.</span>
          </div>
        </div>
        <div class="card-body p-4 d-flex flex-column">
          <div class="d-flex justify-content-between align-items-start mb-2">
            <h5 class="card-title fw-bold mb-0 text-truncate" style="max-width: 70%;">{{ producto.nombre }}</h5>
            <span class="badge bg-light text-secondary border px-2 py-1"><i class="fas fa-tag me-1"></i>{{ producto.categoria_nombre }}</span>
          </div>
          <p class="card-text text-muted small mb-2 flex-grow-1 line-clamp-2">{{ producto.descripcion }}</p>
          <div class="mb-3 pb-2 border-bottom border-light">
            <small class="text-muted"><i class="fas fa-user me-1"></i>Vendido por:</small>
            <div class="fw-bold text-dark">{{ producto.agricultor_nombre }}</div>
          </div>
          <div class="d-flex justify-content-between align-items-end mt-auto pt-2 border-top border-light">
            <div>
              <span class="small text-muted d-block mb-1">Precio</span>
              <span class="fs-4 fw-black text-success lh-1">{{ formatearPrecio(producto.precio) }}</span>
            </div>
            <div class="text-end">
              <span class="small text-muted d-block mb-1">Disponibles</span>
              <span class="fw-bold" :class="producto.stock < producto.stock_minimo ? 'text-warning' : 'text-dark'">
                <i class="fas fa-box me-1"></i>{{ producto.stock }}
              </span>
            </div>
          </div>
        </div>
        <div class="card-footer bg-white border-0 p-3 pt-0 rounded-bottom-4 text-center">
          <a :href="producto.detailUrl" class="btn btn-outline-primary d-block w-100 rounded-pill fw-bold shadow-sm mb-2">
            <i class="fas fa-eye me-1"></i> Ver Detalle
          </a>
          <button v-if="!producto.esta_agotado && !producto.added" class="btn btn-success d-block w-100 rounded-pill fw-bold shadow-sm" @click="agregarCarrito(producto.id)">
            <i class="fas fa-cart-plus me-1"></i> Añadir al carrito
          </button>
          <button v-else-if="producto.added" class="btn btn-outline-success d-block w-100 rounded-pill fw-bold shadow-sm" disabled>
            <i class="fas fa-check me-1"></i> Añadido
          </button>
          <button v-else class="btn btn-secondary d-block w-100 rounded-pill fw-bold shadow-sm" disabled>
            <i class="fas fa-times-circle me-1"></i> Agotado
          </button>
        </div>
      </div>
    </div>
    <div v-if="products.length === 0" class="col-12">
      <div class="card border-0 shadow-sm rounded-4 text-center py-5 my-4 bg-white">
        <div class="card-body">
          <div class="mb-4">
            <i class="fas fa-box-open fa-4x text-muted opacity-50"></i>
          </div>
          <h4 class="text-muted mb-2">No hay productos disponibles</h4>
          <p class="text-muted mb-4">No se encontraron productos con los filtros seleccionados.</p>
        </div>
      </div>
    </div>
  </div>

  <!-- Paginación -->
  <nav v-if="hasPrev || hasNext" class="mt-5 d-flex justify-content-center">
    <ul class="pagination shadow-sm rounded-pill bg-white p-2">
      <li v-if="hasPrev" class="page-item">
        <button class="page-link rounded-pill me-1" @click="page--; fetchProducts()">
          <i class="fas fa-chevron-left"></i>
        </button>
      </li>
      <li class="page-item active">
        <span class="page-link rounded-pill">{{ page }}</span>
      </li>
      <li v-if="hasNext" class="page-item">
        <button class="page-link rounded-pill ms-1" @click="page++; fetchProducts()">
          <i class="fas fa-chevron-right"></i>
        </button>
      </li>
    </ul>
  </nav>
</template>

<style scoped>
.hover-card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.hover-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 1rem 3rem rgba(0, 0, 0, 0.15) !important;
}
.product-image {
  width: 100%;
  height: 220px;
  object-fit: cover;
  transition: transform 0.4s ease;
}
.hover-card:hover .product-image {
  transform: scale(1.05);
}
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.fw-black { font-weight: 800; }
</style>
