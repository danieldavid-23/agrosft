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
  if (valor == null) return '$0';
  const num = Number(valor);
  const formatted = new Intl.NumberFormat('es-CO', { 
    style: 'currency', 
    currency: 'COP', 
    minimumFractionDigits: 0, 
    maximumFractionDigits: Number.isInteger(num) ? 0 : 2 
  }).format(num);
  return formatted.replace(/\s+/g, '');
}

// Lógica de Carrusel de Imágenes
const activeIndexes = ref({})

function getActiveIndex(prodId) {
  return activeIndexes.value[prodId] || 0
}

function getImages(producto) {
  if (producto.imagenes && producto.imagenes.length > 0) {
    return producto.imagenes
  }
  return producto.imagen ? [producto.imagen] : []
}

function nextImage(producto, e) {
  if (e) {
    e.stopPropagation()
    e.preventDefault()
  }
  const imgs = getImages(producto)
  if (imgs.length <= 1) return
  const current = getActiveIndex(producto.id)
  const next = (current + 1) % imgs.length
  activeIndexes.value = { ...activeIndexes.value, [producto.id]: next }
}

function prevImage(producto, e) {
  if (e) {
    e.stopPropagation()
    e.preventDefault()
  }
  const imgs = getImages(producto)
  if (imgs.length <= 1) return
  const current = getActiveIndex(producto.id)
  const prev = (current - 1 + imgs.length) % imgs.length
  activeIndexes.value = { ...activeIndexes.value, [producto.id]: prev }
}

function setImage(producto, index, e) {
  if (e) {
    e.stopPropagation()
    e.preventDefault()
  }
  activeIndexes.value = { ...activeIndexes.value, [producto.id]: index }
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
          <template v-if="getImages(producto).length > 0">
            <div class="image-wrapper">
              <img
                :src="getImages(producto)[getActiveIndex(producto.id)]"
                class="product-image"
                :alt="producto.nombre"
                loading="lazy"
              >
            </div>

            <!-- Controles de Carrusel (cuando hay > 1 imagen) -->
            <template v-if="getImages(producto).length > 1">
              <button
                type="button"
                class="carousel-nav-btn btn-prev shadow-sm"
                @click.stop.prevent="prevImage(producto, $event)"
                title="Imagen anterior"
              >
                <i class="fas fa-chevron-left"></i>
              </button>
              <button
                type="button"
                class="carousel-nav-btn btn-next shadow-sm"
                @click.stop.prevent="nextImage(producto, $event)"
                title="Siguiente imagen"
              >
                <i class="fas fa-chevron-right"></i>
              </button>

              <!-- Indicadores Dots -->
              <div class="carousel-dots-container" @click.stop>
                <span
                  v-for="(img, idx) in getImages(producto)"
                  :key="idx"
                  class="carousel-dot"
                  :class="{ active: idx === getActiveIndex(producto.id) }"
                  @click.stop.prevent="setImage(producto, idx, $event)"
                ></span>
              </div>

              <!-- Contador de fotos -->
              <div class="carousel-counter badge bg-dark bg-opacity-75 rounded-pill text-white shadow-sm">
                <i class="fas fa-camera me-1"></i>{{ getActiveIndex(producto.id) + 1 }}/{{ getImages(producto).length }}
              </div>
            </template>
          </template>

          <div v-else class="d-flex justify-content-center align-items-center h-100 bg-white">
            <div class="bg-success bg-opacity-10 p-4 rounded-circle">
              <i class="fas fa-seedling fa-3x text-success"></i>
            </div>
          </div>

          <div class="position-absolute top-0 end-0 p-3 d-flex flex-column gap-2 align-items-end" style="z-index: 3;">
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
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  top: 0;
}
.hover-card:hover {
  top: -8px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04) !important;
}
.product-image-container {
  height: 220px;
  width: 100%;
  position: relative;
  overflow: hidden;
  background-color: #f8fafc;
}
.image-wrapper {
  width: 100%;
  height: 100%;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}
.product-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
  display: block;
  transition: transform 0.4s ease;
}
.hover-card:hover .product-image {
  transform: scale(1.04);
}
.carousel-nav-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.88);
  backdrop-filter: blur(6px);
  border: 1px solid rgba(0, 0, 0, 0.08);
  color: #1f2937;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  cursor: pointer;
  z-index: 2;
  opacity: 0;
  transition: opacity 0.25s ease, background-color 0.2s, transform 0.2s;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
}
.hover-card:hover .carousel-nav-btn {
  opacity: 1;
}
.carousel-nav-btn:hover {
  background: #ffffff;
  transform: translateY(-50%) scale(1.1);
  color: var(--primary-color, #3C8D3C);
}
.btn-prev { left: 8px; }
.btn-next { right: 8px; }

.carousel-dots-container {
  position: absolute;
  bottom: 8px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 5px;
  z-index: 2;
  padding: 3px 8px;
  background: rgba(0, 0, 0, 0.35);
  backdrop-filter: blur(4px);
  border-radius: 20px;
}
.carousel-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  transition: all 0.2s ease;
}
.carousel-dot.active {
  width: 16px;
  border-radius: 10px;
  background: #ffffff;
}
.carousel-counter {
  position: absolute;
  bottom: 8px;
  left: 8px;
  font-size: 0.7rem;
  padding: 0.25rem 0.5rem;
  backdrop-filter: blur(4px);
  z-index: 2;
}
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.fw-black { font-weight: 800; }
</style>
