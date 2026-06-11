<script setup>
import { ref } from 'vue'
import { getCSRFToken } from '../shared/csrf.js'

const props = defineProps({
  initialProducts: Array,
  categories: Array,
  estados: Array,
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

  const res = await fetch(props.urls.listar + '?' + params.toString(), {
    headers: { 'X-Requested-With': 'XMLHttpRequest' }
  })
  const data = await res.json()
  products.value = data.products
  hasNext.value = data.has_next
  hasPrev.value = data.has_prev
  loading.value = false
}

function formatearPrecio(valor) {
  return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', minimumFractionDigits: 0 }).format(valor)
}

async function eliminarProducto(id, nombre) {
  if (!confirm(`¿Eliminar "${nombre}" de tu inventario?`)) return
  const res = await fetch(props.urls.eliminar.replace('0', id), {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCSRFToken(),
      'X-Requested-With': 'XMLHttpRequest',
    },
  })
  if (res.ok) {
    products.value = products.value.filter(p => p.id !== id)
  }
}
</script>

<template>
  <div class="row align-items-center mb-5">
    <div class="col-md-8">
      <h1 class="display-6 fw-bold mb-2">
        <i class="fas fa-boxes text-success me-2"></i>{{ urls.titulo || 'Mi Inventario' }}
      </h1>
      <p class="text-muted fs-5 mb-0">{{ urls.subtitulo || 'Gestiona tus productos registrados' }}</p>
    </div>
    <div class="col-md-4 text-md-end mt-4 mt-md-0">
      <a :href="urls.crear" class="btn btn-success btn-lg shadow-sm">
        <i class="fas fa-plus-circle me-2"></i>Nuevo Producto
      </a>
    </div>
  </div>

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
            <span v-if="producto.estado === 'pendiente'" class="badge bg-secondary shadow-sm">Pendiente</span>
          </div>
        </div>
        <div class="card-body p-4 d-flex flex-column">
          <div class="d-flex justify-content-between align-items-start mb-2">
            <h5 class="card-title fw-bold mb-0 text-truncate" style="max-width: 70%;">{{ producto.nombre }}</h5>
            <span class="badge bg-light text-secondary border px-2 py-1"><i class="fas fa-tag me-1"></i>{{ producto.categoria_nombre }}</span>
          </div>
          <p class="card-text text-muted small mb-4 flex-grow-1 line-clamp-2">{{ producto.descripcion }}</p>
          <div class="d-flex justify-content-between align-items-end mt-auto pt-3 border-top border-light">
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
          <div class="d-flex gap-2 justify-content-center">
            <a :href="producto.editUrl" class="btn btn-sm btn-outline-primary flex-grow-1 rounded-pill fw-bold">
              <i class="fas fa-edit me-1"></i> Editar
            </a>
            <button class="btn btn-sm btn-outline-danger flex-grow-1 rounded-pill fw-bold" @click="eliminarProducto(producto.id, producto.nombre)">
              <i class="fas fa-trash me-1"></i> Eliminar
            </button>
          </div>
        </div>
      </div>
    </div>
    <div v-if="products.length === 0" class="col-12">
      <div class="card border-0 shadow-sm rounded-4 text-center py-5 my-4 bg-white">
        <div class="card-body py-5">
          <div class="bg-light rounded-circle d-inline-flex align-items-center justify-content-center mb-4" style="width: 100px; height: 100px;">
            <i class="fas fa-box-open fa-3x text-secondary"></i>
          </div>
          <h3 class="fw-bold h4">No se encontraron productos</h3>
          <p class="text-muted mx-auto" style="max-width: 400px;">Aún no hay productos disponibles o los filtros no arrojaron resultados.</p>
          <a :href="urls.crear" class="btn btn-success btn-lg mt-3 rounded-pill px-4 shadow-sm">
            <i class="fas fa-plus-circle me-2"></i>Registrar Primer Producto
          </a>
        </div>
      </div>
    </div>
  </div>

  <!-- Paginación -->
  <nav v-if="hasPrev || hasNext" class="mt-5 mb-3">
    <ul class="pagination justify-content-center gap-2">
      <li v-if="hasPrev" class="page-item">
        <button class="page-link rounded-pill px-3 border-0 bg-white shadow-sm text-dark fw-bold" @click="page--; fetchProducts()">
          <i class="fas fa-chevron-left me-1 small"></i> Anterior
        </button>
      </li>
      <li class="page-item active">
        <span class="page-link rounded-pill px-4 border-0 bg-success shadow-sm text-white fw-bold">Página {{ page }}</span>
      </li>
      <li v-if="hasNext" class="page-item">
        <button class="page-link rounded-pill px-3 border-0 bg-white shadow-sm text-dark fw-bold" @click="page++; fetchProducts()">
          Siguiente <i class="fas fa-chevron-right ms-1 small"></i>
        </button>
      </li>
    </ul>
  </nav>
</template>

<style scoped>
.hover-card {
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  top: 0;
}
.hover-card:hover {
  top: -8px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04) !important;
}
.product-image-container {
  height: 220px;
}
.product-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
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
