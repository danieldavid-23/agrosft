<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
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
const error = ref('')
const deletingId = ref(null)

async function fetchProducts() {
  loading.value = true
  error.value = ''
  try {
    const params = new URLSearchParams()
    if (search.value) params.append('q', search.value)
    if (selectedCategory.value) params.append('categoria', selectedCategory.value)
    if (sortBy.value) params.append('orden', sortBy.value)
    params.append('page', page.value)
    params.append('ajax', '1')

    const res = await fetch(props.urls.listar + '?' + params.toString(), {
      headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    if (!res.ok) {
      throw new Error(`HTTP error ${res.status}`)
    }
    const data = await res.json()
    products.value = data.products || []
    hasNext.value = !!data.has_next
    hasPrev.value = !!data.has_prev
  } catch (err) {
    console.error('Error al cargar inventario:', err)
    error.value = 'No se pudieron cargar los productos. Intenta nuevamente.'
  } finally {
    loading.value = false
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

async function eliminarProducto(id, nombre) {
  if (!confirm(`¿Eliminar "${nombre}" de tu inventario?`)) return
  deletingId.value = id
  error.value = ''
  try {
    const res = await fetch(props.urls.eliminar.replace('0', id), {
      method: 'POST',
      headers: {
        'X-CSRFToken': getCSRFToken(),
        'X-Requested-With': 'XMLHttpRequest',
      },
    })
    if (!res.ok) {
      throw new Error(`HTTP error ${res.status}`)
    }
    const data = await res.json()
    if (data && data.success) {
      products.value = products.value.filter(p => p.id !== id)
    } else {
      error.value = (data && data.error) || 'No se pudo eliminar el producto. Intenta nuevamente.'
    }
  } catch (err) {
    console.error('Error al eliminar producto:', err)
    error.value = 'No se pudo eliminar el producto. Intenta nuevamente.'
  } finally {
    deletingId.value = null
  }
}

// Lógica de Carrusel de Imágenes
const activeIndexes = ref({})

function getActiveIndex(prodId) {
  return activeIndexes.value[prodId] || 0
}

function getImages(producto) {
  if (!producto) return []
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

// Lógica de Visor Lightbox para ver todas las fotos
const lightboxActive = ref(false)
const lightboxProduct = ref(null)
const lightboxIndex = ref(0)

function openLightbox(producto, initialIndex = 0, e) {
  if (e) {
    e.stopPropagation()
    e.preventDefault()
  }
  const imgs = getImages(producto)
  if (imgs.length === 0) return
  lightboxProduct.value = producto
  lightboxIndex.value = Math.max(0, Math.min(initialIndex, imgs.length - 1))
  lightboxActive.value = true
  document.body.style.overflow = 'hidden'
}

function closeLightbox() {
  lightboxActive.value = false
  lightboxProduct.value = null
  document.body.style.overflow = ''
}

function lightboxNext() {
  if (!lightboxProduct.value) return
  const imgs = getImages(lightboxProduct.value)
  if (imgs.length <= 1) return
  lightboxIndex.value = (lightboxIndex.value + 1) % imgs.length
}

function lightboxPrev() {
  if (!lightboxProduct.value) return
  const imgs = getImages(lightboxProduct.value)
  if (imgs.length <= 1) return
  lightboxIndex.value = (lightboxIndex.value - 1 + imgs.length) % imgs.length
}

function onKeydown(e) {
  if (!lightboxActive.value) return
  if (e.key === 'Escape') closeLightbox()
  else if (e.key === 'ArrowRight') lightboxNext()
  else if (e.key === 'ArrowLeft') lightboxPrev()
}

onMounted(() => {
  window.addEventListener('keydown', onKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', onKeydown)
  document.body.style.overflow = ''
})
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

  <!-- Error Alert -->
  <div v-if="error" class="alert alert-danger alert-dismissible fade show rounded-4 mb-4 shadow-sm" role="alert">
    <i class="fas fa-exclamation-circle me-2"></i>{{ error }}
    <button type="button" class="btn-close" @click="error = ''" aria-label="Close"></button>
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
            <!-- Clic en la imagen abre la galería completa / Lightbox -->
            <div
              class="image-wrapper d-block position-relative cursor-pointer"
              @click="openLightbox(producto, getActiveIndex(producto.id), $event)"
              role="button"
              :title="'Clic para ver todas las fotos (' + getImages(producto).length + ')'"
            >
              <img
                :src="getImages(producto)[getActiveIndex(producto.id)]"
                class="product-image"
                :alt="producto.nombre"
                loading="lazy"
              >
              <!-- Overlay indicador de galería al pasar el ratón -->
              <div class="ver-fotos-overlay d-flex align-items-center justify-content-center">
                <span class="badge bg-dark bg-opacity-75 rounded-pill px-3 py-2 text-white shadow-sm border border-light border-opacity-25">
                  <i class="fas fa-expand me-1"></i>Ver todas las fotos ({{ getImages(producto).length }})
                </span>
              </div>
            </div>

            <!-- Controles de Carrusel en la tarjeta (cuando hay > 1 imagen) -->
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

              <!-- Contador de fotos clickable -->
              <div
                class="carousel-counter badge bg-dark bg-opacity-75 rounded-pill text-white shadow-sm cursor-pointer"
                @click.stop.prevent="openLightbox(producto, getActiveIndex(producto.id), $event)"
                title="Ver galería completa"
              >
                <i class="fas fa-camera me-1"></i>{{ getActiveIndex(producto.id) + 1 }}/{{ getImages(producto).length }}
              </div>
            </template>
          </template>

          <div v-else class="d-flex justify-content-center align-items-center h-100 bg-white">
            <a :href="producto.detailUrl || `/inventario/producto/${producto.id}/`" class="d-flex justify-content-center align-items-center w-100 h-100 text-decoration-none">
              <div class="bg-success bg-opacity-10 p-4 rounded-circle">
                <i class="fas fa-seedling fa-3x text-success"></i>
              </div>
            </a>
          </div>

          <div class="position-absolute top-0 end-0 p-3 d-flex flex-column gap-2 align-items-end" style="z-index: 3;">
            <span v-if="producto.esta_agotado" class="badge bg-danger shadow-sm"><i class="fas fa-times-circle me-1"></i>Agotado</span>
            <span v-else-if="producto.stock < producto.stock_minimo" class="badge bg-warning shadow-sm text-dark"><i class="fas fa-exclamation-triangle me-1"></i>Últimas unid.</span>
            <span v-if="producto.estado === 'pendiente'" class="badge bg-secondary shadow-sm">Pendiente</span>
          </div>
        </div>
        <div class="card-body p-4 d-flex flex-column">
          <div class="d-flex justify-content-between align-items-start mb-2">
            <h5 class="card-title fw-bold mb-0 text-truncate" style="max-width: 70%;">
              <a :href="producto.detailUrl || `/inventario/producto/${producto.id}/`" class="text-dark text-decoration-none">
                {{ producto.nombre }}
              </a>
            </h5>
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
          <a :href="producto.detailUrl || `/inventario/producto/${producto.id}/`" class="btn btn-outline-success d-block w-100 rounded-pill fw-bold shadow-sm mb-2">
            <i class="fas fa-eye me-1"></i> Ver detalle
          </a>
          <div class="d-flex gap-2 justify-content-center">
            <a :href="producto.editUrl" class="btn btn-sm btn-outline-primary flex-grow-1 rounded-pill fw-bold">
              <i class="fas fa-edit me-1"></i> Editar
            </a>
            <button class="btn btn-sm btn-outline-danger flex-grow-1 rounded-pill fw-bold" :disabled="deletingId === producto.id" @click="eliminarProducto(producto.id, producto.nombre)">
              <i class="fas fa-trash me-1"></i> {{ deletingId === producto.id ? 'Eliminando...' : 'Eliminar' }}
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

  <!-- Modal Lightbox Galería de Fotos Interactiva -->
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="lightboxActive && lightboxProduct"
        class="custom-lightbox-backdrop"
        @click.self="closeLightbox"
      >
        <div class="custom-lightbox-dialog">
          <!-- Barra Superior -->
          <div class="lightbox-header d-flex justify-content-between align-items-center mb-3">
            <div class="d-flex align-items-center gap-2">
              <h5 class="fw-bold text-white mb-0 text-truncate" style="max-width: 55vw;">
                {{ lightboxProduct.nombre }}
              </h5>
              <span class="badge bg-success rounded-pill px-3 py-1" style="font-size: 0.75rem;">
                {{ lightboxProduct.categoria_nombre }}
              </span>
            </div>

            <div class="d-flex align-items-center gap-3">
              <span class="badge bg-dark bg-opacity-75 text-white border border-light border-opacity-25 rounded-pill px-3 py-2 fw-bold">
                <i class="fas fa-camera me-1 text-success"></i>Foto {{ lightboxIndex + 1 }} de {{ getImages(lightboxProduct).length }}
              </span>
              <button
                type="button"
                class="btn-lightbox-close"
                @click="closeLightbox"
                title="Cerrar (Esc)"
              >
                <i class="fas fa-times"></i>
              </button>
            </div>
          </div>

          <!-- Visor Central de la Imagen -->
          <div class="lightbox-body position-relative d-flex align-items-center justify-content-center">
            <!-- Flecha Anterior -->
            <button
              v-if="getImages(lightboxProduct).length > 1"
              type="button"
              class="lightbox-arrow-btn lightbox-arrow-prev"
              @click.stop="lightboxPrev"
              title="Foto anterior (←)"
            >
              <i class="fas fa-chevron-left"></i>
            </button>

            <!-- Imagen Principal -->
            <div class="lightbox-image-container">
              <img
                :src="getImages(lightboxProduct)[lightboxIndex]"
                :alt="lightboxProduct.nombre"
                class="lightbox-main-img"
              >
            </div>

            <!-- Flecha Siguiente -->
            <button
              v-if="getImages(lightboxProduct).length > 1"
              type="button"
              class="lightbox-arrow-btn lightbox-arrow-next"
              @click.stop="lightboxNext"
              title="Foto siguiente (→)"
            >
              <i class="fas fa-chevron-right"></i>
            </button>
          </div>

          <!-- Tira de Miniaturas (Filmstrip) -->
          <div
            v-if="getImages(lightboxProduct).length > 1"
            class="lightbox-thumbnails-strip mt-3"
          >
            <div
              v-for="(thumbUrl, idx) in getImages(lightboxProduct)"
              :key="idx"
              class="lightbox-thumb-item"
              :class="{ active: idx === lightboxIndex }"
              @click="lightboxIndex = idx"
              :title="'Ver foto ' + (idx + 1)"
            >
              <img :src="thumbUrl" :alt="'Miniatura ' + (idx + 1)">
            </div>
          </div>

          <!-- Barra Inferior con Acciones -->
          <div class="lightbox-footer d-flex flex-wrap justify-content-between align-items-center mt-3 pt-3 border-top border-secondary border-opacity-25">
            <div class="text-white-50 small">
              <i class="fas fa-keyboard me-1 text-light"></i>Usa <kbd class="bg-dark text-white border border-secondary px-2 py-0">←</kbd> <kbd class="bg-dark text-white border border-secondary px-2 py-0">→</kbd> para navegar o <kbd class="bg-dark text-white border border-secondary px-2 py-0">Esc</kbd> para salir
            </div>
            <div class="d-flex gap-2">
              <a
                :href="lightboxProduct.editUrl"
                class="btn btn-sm btn-outline-light rounded-pill px-3 fw-bold"
              >
                <i class="fas fa-edit me-1"></i>Editar Producto
              </a>
              <a
                :href="lightboxProduct.detailUrl || `/inventario/producto/${lightboxProduct.id}/`"
                class="btn btn-sm btn-success rounded-pill px-3 fw-bold"
              >
                <i class="fas fa-eye me-1"></i>Ver Detalle Completo
              </a>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style>
.cursor-pointer {
  cursor: pointer;
}
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
  transform: scale(1.05);
}
.ver-fotos-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.35);
  opacity: 0;
  transition: opacity 0.25s ease;
  pointer-events: none;
  z-index: 2;
}
.hover-card:hover .ver-fotos-overlay {
  opacity: 1;
}

.carousel-nav-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(6px);
  border: 1px solid rgba(0, 0, 0, 0.1);
  color: #1f2937;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  cursor: pointer;
  z-index: 4;
  opacity: 0.85;
  transition: opacity 0.25s ease, background-color 0.2s, transform 0.2s;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.18);
}
.hover-card:hover .carousel-nav-btn {
  opacity: 1;
}
.carousel-nav-btn:hover {
  background: #ffffff;
  transform: translateY(-50%) scale(1.15);
  color: #22c55e;
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
  z-index: 4;
  padding: 3px 8px;
  background: rgba(0, 0, 0, 0.4);
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
  z-index: 4;
  transition: transform 0.2s ease;
}
.carousel-counter:hover {
  transform: scale(1.05);
}
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.fw-black { font-weight: 800; }

/* Lightbox Modal Estilizado */
.custom-lightbox-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(10, 15, 29, 0.94);
  backdrop-filter: blur(12px);
  z-index: 10050;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
}

.custom-lightbox-dialog {
  width: 100%;
  max-width: 950px;
  max-height: 94vh;
  display: flex;
  flex-direction: column;
}

.btn-lightbox-close {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.25);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-lightbox-close:hover {
  background: #ef4444;
  border-color: #ef4444;
  transform: rotate(90deg);
}

.lightbox-body {
  width: 100%;
  min-height: 360px;
  max-height: 64vh;
}

.lightbox-image-container {
  max-width: 100%;
  max-height: 64vh;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.lightbox-main-img {
  max-width: 100%;
  max-height: 64vh;
  object-fit: contain;
  border-radius: 12px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5);
  transition: opacity 0.2s ease;
}

.lightbox-arrow-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(6px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 10;
  transition: all 0.2s ease;
}

.lightbox-arrow-btn:hover {
  background: rgba(255, 255, 255, 0.95);
  color: #111827;
  transform: translateY(-50%) scale(1.12);
}

.lightbox-arrow-prev {
  left: -20px;
}

.lightbox-arrow-next {
  right: -20px;
}

@media (max-width: 768px) {
  .lightbox-arrow-prev { left: 5px; }
  .lightbox-arrow-next { right: 5px; }
}

.lightbox-thumbnails-strip {
  display: flex;
  gap: 8px;
  justify-content: center;
  overflow-x: auto;
  padding: 8px 4px;
}

.lightbox-thumb-item {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  overflow: hidden;
  border: 2px solid transparent;
  cursor: pointer;
  opacity: 0.55;
  flex-shrink: 0;
  transition: all 0.2s ease;
}

.lightbox-thumb-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.lightbox-thumb-item:hover {
  opacity: 0.9;
  transform: translateY(-2px);
}

.lightbox-thumb-item.active {
  opacity: 1;
  border-color: #22c55e;
  box-shadow: 0 0 10px rgba(34, 197, 94, 0.6);
  transform: scale(1.06);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>

