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
const error = ref('')
const addingId = ref(null)

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

    const res = await fetch(props.urls.marketplace + '?' + params.toString(), {
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
    console.error('Error al cargar marketplace:', err)
    error.value = 'No se pudieron cargar los productos. Intenta nuevamente.'
  } finally {
    loading.value = false
  }
}

watch([search, selectedCategory, sortBy], () => {
  page.value = 1
  fetchProducts()
})

async function agregarCarrito(productoId) {
  addingId.value = productoId
  error.value = ''
  try {
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
    if (!res.ok) {
      throw new Error(`HTTP error ${res.status}`)
    }
    const data = await res.json()
    if (data && data.success) {
      const item = products.value.find(p => p.id === productoId)
      if (item) item.added = true
      setTimeout(() => { if (item) item.added = false }, 2000)
    } else {
      error.value = (data && data.error) || 'No se pudo agregar el producto al carrito.'
    }
  } catch (err) {
    console.error('Error al agregar al carrito:', err)
    error.value = 'No se pudo agregar el producto al carrito. Intenta nuevamente.'
  } finally {
    addingId.value = null
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

// Iniciales del agricultor para el avatar (p. ej. "Ana García" -> "AG")
function iniciales(nombre) {
  if (!nombre) return '?'
  const partes = String(nombre).trim().split(/\s+/)
  return partes
    .slice(0, 2)
    .map(p => p[0])
    .join('')
    .toUpperCase()
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
  <!-- ===== PANEL DE FILTROS ===== -->
  <div class="mp-filtros">
    <div class="mp-filtros-head">
      <div class="mp-filtros-title">
        <i class="fas fa-sliders me-2"></i>Filtrar productos
      </div>
      <div v-if="products.length" class="mp-filtros-count">
        {{ products.length }} producto{{ products.length !== 1 ? 's' : '' }}
      </div>
    </div>
    <div class="row g-3">
      <div class="col-md-5">
        <label class="mp-filtro-label">Buscar</label>
        <div class="input-group">
          <span class="input-group-text mp-filtro-icono border-end-0">
            <i class="fas fa-search"></i>
          </span>
          <input type="text" v-model="search" class="form-control mp-filtro-input border-start-0"
                 placeholder="Ej: Tomate, Maíz...">
        </div>
      </div>
      <div class="col-md-3">
        <label class="mp-filtro-label">Categoría</label>
        <select v-model="selectedCategory" class="form-select mp-filtro-select">
          <option value="">Todas las categorías</option>
          <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.nombre }}</option>
        </select>
      </div>
      <div class="col-md-2">
        <label class="mp-filtro-label">Ordenar por</label>
        <select v-model="sortBy" class="form-select mp-filtro-select">
          <option value="reciente">Más recientes</option>
          <option value="precio_asc">Menor Precio</option>
          <option value="precio_desc">Mayor Precio</option>
          <option value="nombre">Nombre A-Z</option>
        </select>
      </div>
      <div class="col-md-2 d-flex align-items-end">
        <button class="btn mp-filtro-boton w-100" @click="fetchProducts">
          <i class="fas fa-filter me-2"></i>Aplicar
        </button>
      </div>
    </div>
  </div>

  <!-- ===== MENSAJE DE ERROR ===== -->
  <div v-if="error" class="alert alert-danger alert-dismissible fade show rounded-4 mb-4 shadow-sm" role="alert">
    <i class="fas fa-exclamation-circle me-2"></i>{{ error }}
    <button type="button" class="btn-close" @click="error = ''" aria-label="Close"></button>
  </div>

  <!-- ===== CARGANDO ===== -->
  <div v-if="loading" class="text-center py-5">
    <div class="spinner-border text-success" role="status">
      <span class="visually-hidden">Cargando...</span>
    </div>
  </div>

  <!-- ===== REJILLA DE PRODUCTOS ===== -->
  <div v-else class="row g-4">
    <div v-for="producto in products" :key="producto.id" class="col-xl-3 col-lg-4 col-md-6">
      <div class="mp-card-vue">

        <!-- Imagen del producto -->
        <div class="mp-card-vue-img">
          <template v-if="getImages(producto).length > 0">
            <div class="image-wrapper">
              <img :src="getImages(producto)[getActiveIndex(producto.id)]" class="mp-card-vue-img-el"
                   :alt="producto.nombre" loading="lazy">
            </div>

            <!-- Controles de carrusel cuando hay más de una imagen -->
            <template v-if="getImages(producto).length > 1">
              <button type="button" class="carousel-nav-btn btn-prev shadow-sm"
                      @click.stop.prevent="prevImage(producto, $event)" title="Imagen anterior">
                <i class="fas fa-chevron-left"></i>
              </button>
              <button type="button" class="carousel-nav-btn btn-next shadow-sm"
                      @click.stop.prevent="nextImage(producto, $event)" title="Siguiente imagen">
                <i class="fas fa-chevron-right"></i>
              </button>
              <div class="carousel-dots-container" @click.stop>
                <span v-for="(img, idx) in getImages(producto)" :key="idx" class="carousel-dot"
                      :class="{ active: idx === getActiveIndex(producto.id) }"
                      @click.stop.prevent="setImage(producto, idx, $event)"></span>
              </div>
              <div class="carousel-counter badge bg-dark bg-opacity-75 rounded-pill text-white shadow-sm">
                <i class="fas fa-camera me-1"></i>{{ getActiveIndex(producto.id) + 1 }}/{{ getImages(producto).length }}
              </div>
            </template>
          </template>

          <!-- Estado sin imagen -->
          <div v-else class="d-flex justify-content-center align-items-center h-100 bg-white">
            <div class="mp-sin-imagen-ico">
              <i class="fas fa-seedling fa-2x"></i>
            </div>
          </div>

          <!-- Chip de categoría -->
          <span class="mp-card-vue-chip">
            <i class="fas fa-tag me-1"></i>{{ producto.categoria_nombre }}
          </span>

          <!-- Badges de estado del producto -->
          <div class="mp-card-vue-badges">
            <span v-if="producto.esta_agotado" class="mp-badge-stock agotado">
              <i class="fas fa-times-circle me-1"></i>Agotado
            </span>
            <span v-else-if="producto.stock < producto.stock_minimo" class="mp-badge-stock ultimas">
              <i class="fas fa-exclamation-triangle me-1"></i>Últimas unid.
            </span>
          </div>
        </div>

        <!-- Cuerpo de la tarjeta -->
        <div class="mp-card-vue-body">
          <h5 class="mp-card-vue-titulo">{{ producto.nombre }}</h5>
          <p class="mp-card-vue-desc">{{ producto.descripcion }}</p>

          <!-- Vendedor -->
          <div class="mp-card-vue-vendedor">
            <div class="mp-avatar">{{ iniciales(producto.agricultor_nombre) }}</div>
            <div class="flex-grow-1">
              <div class="mp-vendedor-label">Vendido por</div>
              <div class="mp-vendedor-nombre">{{ producto.agricultor_nombre }}</div>
            </div>
          </div>

          <!-- Precio y disponibilidad -->
          <div class="mp-card-vue-precio">
            <div>
              <div class="mp-precio-label">Precio</div>
              <div class="mp-precio-valor">{{ formatearPrecio(producto.precio) }}</div>
            </div>
            <div class="text-end">
              <div class="mp-precio-label">Disponibles</div>
              <div class="mp-card-vue-stock" :class="{ bajo: producto.stock < producto.stock_minimo }">
                <i class="fas fa-box me-1"></i>{{ producto.stock }}
              </div>
            </div>
          </div>
        </div>

        <!-- Acciones -->
        <div class="mp-card-vue-footer">
          <a :href="producto.detailUrl" class="mp-btn-detalle">
            <i class="fas fa-eye me-1"></i> Ver Detalle
          </a>
          <button v-if="!producto.esta_agotado && !producto.added" class="mp-btn-carrito"
                  :disabled="addingId === producto.id" @click="agregarCarrito(producto.id)">
            <i class="fas fa-cart-plus me-1"></i>
            {{ addingId === producto.id ? 'Añadiendo...' : 'Añadir al carrito' }}
          </button>
          <button v-else-if="producto.added" class="mp-btn-carrito anadido" disabled>
            <i class="fas fa-check me-1"></i> Añadido
          </button>
          <button v-else class="mp-btn-carrito agotado" disabled>
            <i class="fas fa-times-circle me-1"></i> Agotado
          </button>
        </div>
      </div>
    </div>

    <!-- Estado vacío -->
    <div v-if="products.length === 0" class="col-12">
      <div class="mp-vacio">
        <div class="mp-vacio-icono">
          <i class="fas fa-box-open fa-3x"></i>
        </div>
        <h4 class="mb-2 mt-4">No hay productos disponibles</h4>
        <p class="text-muted mb-4">No se encontraron productos con los filtros seleccionados.</p>
      </div>
    </div>
  </div>

  <!-- ===== PAGINACIÓN ===== -->
  <nav v-if="hasPrev || hasNext" class="mt-5 d-flex justify-content-center">
    <ul class="mp-paginacion">
      <li v-if="hasPrev">
        <button class="mp-page-btn" @click="page--; fetchProducts()">
          <i class="fas fa-chevron-left"></i>
        </button>
      </li>
      <li class="mp-page-btn active">{{ page }}</li>
      <li v-if="hasNext">
        <button class="mp-page-btn" @click="page++; fetchProducts()">
          <i class="fas fa-chevron-right"></i>
        </button>
      </li>
    </ul>
  </nav>
</template>

<style scoped>
/* ==========================================================================
   ESTILOS DEL MARKETPLACE (Inicio)
   Paleta AgroSFT: verde bosque #3C8D3C, ámbar #E8853B, fondo crema #F5F1E8.
   ========================================================================== */

/* ---------- Panel de filtros ---------- */
.mp-filtros {
  background: #ffffff;
  border-radius: 20px;
  box-shadow: 0 8px 30px rgba(18, 48, 29, 0.08);
  border: 1px solid rgba(0, 0, 0, 0.05);
  position: relative;
  margin-bottom: 2.2rem;
}
/* Línea de acento ámbar en la parte superior del panel */
.mp-filtros::before {
  content: '';
  position: absolute;
  top: -1px; left: 24px; right: 24px;
  height: 3px;
  border-radius: 0 0 8px 8px;
  background: linear-gradient(90deg, #E8853B, #3C8D3C);
}
.mp-filtros-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px 0;
}
.mp-filtros-title {
  font-weight: 800;
  font-size: 1rem;
  color: #12301D;
  letter-spacing: -0.01em;
}
.mp-filtros-count {
  background: #E8F5E8;
  color: #2E7535;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 4px 12px;
  border-radius: 100px;
}
.mp-filtro-label {
  display: block;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #7A8A7D;
  margin-bottom: 6px;
}
.mp-filtro-icono {
  background: #f8fafc;
  color: #7A8A7D;
  border-radius: 14px 0 0 14px !important;
}
.mp-filtro-input, .mp-filtro-select {
  border: 1.5px solid #D6D8CC;
  border-radius: 14px !important;
  background: #fff;
  font-size: 0.9rem;
  color: #3D5245;
}
.mp-filtro-input:focus, .mp-filtro-select:focus {
  border-color: #3C8D3C;
  box-shadow: 0 0 0 3px rgba(60, 141, 60, 0.12);
}
.mp-filtro-boton {
  background: linear-gradient(135deg, #3C8D3C, #2E7535);
  color: #ffffff;
  font-weight: 700;
  font-size: 0.88rem;
  padding: 0.7rem 1rem;
  border-radius: 14px;
  box-shadow: 0 6px 18px rgba(60, 141, 60, 0.3);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.mp-filtro-boton:hover {
  transform: translateY(-2px);
  color: #ffffff;
  box-shadow: 0 10px 24px rgba(60, 141, 60, 0.4);
}

/* ---------- Tarjeta de producto ---------- */
.mp-card-vue {
  background: #ffffff;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(18, 48, 29, 0.07);
  border: 1px solid rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  height: 100%;
  transition: transform 0.3s cubic-bezier(.22,.68,0,1.15), box-shadow 0.3s ease;
}
.mp-card-vue:hover {
  transform: translateY(-8px);
  box-shadow: 0 22px 44px rgba(60, 141, 60, 0.16);
}

/* Imagen */
.mp-card-vue-img {
  height: 220px;
  width: 100%;
  position: relative;
  overflow: hidden;
  background: #E8F5E8;
  flex-shrink: 0;
}
.image-wrapper {
  width: 100%;
  height: 100%;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}
.mp-card-vue-img-el {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
  display: block;
  transition: transform 0.5s ease;
}
.mp-card-vue:hover .mp-card-vue-img-el { transform: scale(1.07); }

/* Chip de categoría (arriba izquierda) */
.mp-card-vue-chip {
  position: absolute;
  top: 12px;
  left: 12px;
  z-index: 6;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(6px);
  border: 1px solid rgba(18, 48, 29, 0.1);
  color: #2E7535;
  font-size: 0.7rem;
  font-weight: 700;
  padding: 4px 11px;
  border-radius: 100px;
  letter-spacing: 0.02em;
}

/* Badges de estado (arriba derecha) */
.mp-card-vue-badges {
  position: absolute;
  top: 12px;
  right: 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  align-items: flex-end;
  z-index: 5;
}
.mp-badge-stock {
  font-size: 0.72rem;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 100px;
  letter-spacing: 0.02em;
  color: #fff;
}
.mp-badge-stock.agotado { background: rgba(220, 38, 38, 0.92); }
.mp-badge-stock.ultimas { background: rgba(245, 158, 11, 0.92); }

/* Sin imagen */
.mp-sin-imagen-ico {
  width: 76px;
  height: 76px;
  border-radius: 50%;
  background: #E8F5E8;
  color: #3C8D3C;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Controles de carrusel */
.carousel-nav-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(6px);
  border: 1px solid rgba(0, 0, 0, 0.08);
  color: #12301D;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  cursor: pointer;
  z-index: 5;
  opacity: 0;
  transition: opacity 0.25s ease, transform 0.2s ease, background 0.2s;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
}
.mp-card-vue:hover .carousel-nav-btn,
.mp-card-vue-img:hover .carousel-nav-btn { opacity: 1; }
.carousel-nav-btn:hover {
  background: #3C8D3C;
  transform: translateY(-50%) scale(1.1);
  color: #ffffff;
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
  z-index: 5;
  padding: 3px 8px;
  background: rgba(18, 48, 29, 0.55);
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
  background: #E8853B;
}
.carousel-counter {
  position: absolute;
  bottom: 8px;
  right: 10px;
  font-size: 0.7rem;
  padding: 3px 9px;
  backdrop-filter: blur(4px);
  z-index: 5;
  background: rgba(18, 48, 29, 0.65) !important;
}

/* ---------- Cuerpo ---------- */
.mp-card-vue-body {
  padding: 18px 18px 12px;
  display: flex;
  flex-direction: column;
  flex-grow: 1;
}
.mp-card-vue-titulo {
  font-size: 1.02rem;
  font-weight: 800;
  color: #12301D;
  margin-bottom: 6px;
  line-height: 1.3;
  letter-spacing: -0.01em;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.mp-card-vue-desc {
  font-size: 0.82rem;
  color: #7A8A7D;
  line-height: 1.55;
  margin-bottom: 12px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Vendedor */
.mp-card-vue-vendedor {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 0;
  border-top: 1px solid #f1f5f9;
  border-bottom: 1px solid #f1f5f9;
  margin-bottom: 12px;
}
.mp-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3C8D3C, #62A96B);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.78rem;
  font-weight: 800;
  flex-shrink: 0;
  letter-spacing: 0.02em;
}
.mp-vendedor-label { font-size: 0.66rem; color: #94a3b8; font-weight: 600; }
.mp-vendedor-nombre {
  font-size: 0.84rem;
  color: #1e293b;
  font-weight: 700;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Precio y stock */
.mp-card-vue-precio {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-top: auto;
}
.mp-precio-label {
  font-size: 0.66rem;
  color: #94a3b8;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 3px;
}
.mp-precio-valor {
  font-size: 1.3rem;
  font-weight: 900;
  color: #E8853B;
  line-height: 1;
  letter-spacing: -0.03em;
}
.mp-card-vue-stock {
  font-size: 0.88rem;
  font-weight: 700;
  color: #1e293b;
}
.mp-card-vue-stock.bajo { color: #d97706; }

/* ---------- Pie / Acciones ---------- */
.mp-card-vue-footer {
  padding: 12px 18px 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  background: #fafbfc;
  border-top: 1px solid #f1f5f9;
}
.mp-btn-detalle, .mp-btn-carrito {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  padding: 10px 16px;
  border-radius: 14px;
  font-size: 0.86rem;
  font-weight: 700;
  letter-spacing: 0.01em;
  border: none;
  cursor: pointer;
  transition: all 0.25s ease;
  text-decoration: none;
}
.mp-btn-detalle {
  background: transparent;
  border: 2px solid #3C8D3C;
  color: #3C8D3C;
}
.mp-btn-detalle:hover {
  background: #E8F5E8;
  color: #2E7535;
  transform: translateY(-1px);
}
.mp-btn-carrito {
  background: linear-gradient(135deg, #E8853B, #D97A30);
  color: #fff;
  box-shadow: 0 5px 16px rgba(232, 133, 59, 0.32);
}
.mp-btn-carrito:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 22px rgba(232, 133, 59, 0.45);
}
.mp-btn-carrito:disabled { opacity: 0.75; cursor: not-allowed; }
.mp-btn-carrito.anadido {
  background: linear-gradient(135deg, #3C8D3C, #2E7535);
  box-shadow: 0 5px 16px rgba(60, 141, 60, 0.3);
}
.mp-btn-carrito.agotado {
  background: #e2e8f0;
  color: #94a3b8;
  box-shadow: none;
}

/* ---------- Estado vacío ---------- */
.mp-vacio {
  background: #ffffff;
  border-radius: 20px;
  padding: 64px 30px;
  text-align: center;
  box-shadow: 0 6px 24px rgba(18, 48, 29, 0.07);
  border: 1px dashed #D6D8CC;
}
.mp-vacio-icono {
  width: 92px;
  height: 92px;
  margin: 0 auto;
  background: #E8F5E8;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #62A96B;
}

/* ---------- Paginación ---------- */
.mp-paginacion {
  list-style: none;
  padding: 6px;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  background: #ffffff;
  border-radius: 100px;
  box-shadow: 0 6px 20px rgba(18, 48, 29, 0.08);
}
.mp-page-btn {
  width: 42px;
  height: 42px;
  border-radius: 100px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  color: #475569;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}
.mp-page-btn:hover {
  border-color: #3C8D3C;
  color: #3C8D3C;
  transform: translateY(-2px);
}
.mp-page-btn.active {
  background: linear-gradient(135deg, #3C8D3C, #2E7535);
  border-color: #3C8D3C;
  color: #fff;
  box-shadow: 0 5px 14px rgba(60, 141, 60, 0.35);
}
</style>