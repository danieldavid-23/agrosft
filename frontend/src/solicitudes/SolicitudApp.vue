<script setup>
import { ref, computed, onMounted } from 'vue'

// Local data store - no database connection required
const solicitudes = ref([])
const selectedSolicitud = ref(null)
const filterEstado = ref('')
const searchQuery = ref('')
const sortBy = ref('reciente')
const showDetail = ref(false)
const notification = ref({ show: false, type: '', message: '' })

// Load initial data from Django template JSON or use mock data
onMounted(() => {
  const dataEl = document.getElementById('solicitudes-data')
  if (dataEl) {
    try {
      const parsed = JSON.parse(dataEl.textContent)
      if (parsed.initialSolicitudes && parsed.initialSolicitudes.length > 0) {
        solicitudes.value = parsed.initialSolicitudes.map(s => ({
          ...s,
          estado: s.estado || 'recibida',
          productos: s.productos_mios || [],
        }))
      } else {
        loadMockData()
      }
    } catch (e) {
      loadMockData()
    }
  } else {
    loadMockData()
  }
})

function loadMockData() {
  solicitudes.value = [
    {
      id: 1001,
      fecha: '2026-06-15 10:30',
      comprador_nombre: 'María García López',
      comprador_email: 'maria.garcia@email.com',
      comprador_telefono: '310 555 1234',
      total_productos_mios: 3,
      total_estimado: 45000,
      estado: 'recibida',
      productos: [
        { id_producto_usuario: { id_producto: { nombre: 'Tomate Cherry' }, precio: 8000 }, cantidad: -3 },
        { id_producto_usuario: { id_producto: { nombre: 'Cebolla Cabezona' }, precio: 5000 }, cantidad: -2 },
        { id_producto_usuario: { id_producto: { nombre: 'Pimentón Rojo' }, precio: 7000 }, cantidad: -1 },
      ]
    },
    {
      id: 1002,
      fecha: '2026-06-14 14:15',
      comprador_nombre: 'Carlos Rodríguez',
      comprador_email: 'carlos.r@email.com',
      comprador_telefono: '320 555 5678',
      total_productos_mios: 2,
      total_estimado: 120000,
      estado: 'aceptada',
      productos: [
        { id_producto_usuario: { id_producto: { nombre: 'Papa Pastusa' }, precio: 3000 }, cantidad: -20 },
        { id_producto_usuario: { id_producto: { nombre: 'Zanahoria' }, precio: 4000 }, cantidad: -15 },
      ]
    },
    {
      id: 1003,
      fecha: '2026-06-13 09:00',
      comprador_nombre: 'Ana Martínez',
      comprador_email: 'ana.martinez@email.com',
      comprador_telefono: '315 555 9012',
      total_productos_mios: 1,
      total_estimado: 75000,
      estado: 'rechazada',
      productos: [
        { id_producto_usuario: { id_producto: { nombre: 'Maíz Amarillo' }, precio: 2500 }, cantidad: -30 },
      ]
    },
    {
      id: 1004,
      fecha: '2026-06-12 16:45',
      comprador_nombre: 'Pedro Sánchez',
      comprador_email: 'pedro.s@email.com',
      comprador_telefono: '300 555 3456',
      total_productos_mios: 4,
      total_estimado: 200000,
      estado: 'vendida',
      productos: [
        { id_producto_usuario: { id_producto: { nombre: 'Plátano Dominico' }, precio: 6000 }, cantidad: -10 },
        { id_producto_usuario: { id_producto: { nombre: 'Mango Tommy' }, precio: 10000 }, cantidad: -8 },
        { id_producto_usuario: { id_producto: { nombre: 'Guayaba' }, precio: 4500 }, cantidad: -5 },
        { id_producto_usuario: { id_producto: { nombre: 'Limon' }, precio: 3500 }, cantidad: -12 },
      ]
    },
    {
      id: 1005,
      fecha: '2026-06-17 08:20',
      comprador_nombre: 'Laura Gómez',
      comprador_email: 'laura.gomez@email.com',
      comprador_telefono: '318 555 7890',
      total_productos_mios: 2,
      total_estimado: 32000,
      estado: 'recibida',
      productos: [
        { id_producto_usuario: { id_producto: { nombre: 'Lechuga Crespa' }, precio: 4000 }, cantidad: -4 },
        { id_producto_usuario: { id_producto: { nombre: 'Espinaca' }, precio: 8000 }, cantidad: -2 },
      ]
    },
  ]
}

// Computed: filtered and sorted solicitudes
const solicitudesFiltradas = computed(() => {
  let result = [...solicitudes.value]

  // Filter by status
  if (filterEstado.value) {
    result = result.filter(s => s.estado === filterEstado.value)
  }

  // Filter by search query
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(s =>
      s.comprador_nombre.toLowerCase().includes(q) ||
      s.comprador_email.toLowerCase().includes(q) ||
      String(s.id).includes(q)
    )
  }

  // Sort
  if (sortBy.value === 'reciente') {
    result.sort((a, b) => new Date(b.fecha) - new Date(a.fecha))
  } else if (sortBy.value === 'mayor_total') {
    result.sort((a, b) => b.total_estimado - a.total_estimado)
  } else if (sortBy.value === 'menor_total') {
    result.sort((a, b) => a.total_estimado - b.total_estimado)
  }

  return result
})

// Stats
const stats = computed(() => ({
  total: solicitudes.value.length,
  recibidas: solicitudes.value.filter(s => s.estado === 'recibida').length,
  aceptadas: solicitudes.value.filter(s => s.estado === 'aceptada').length,
  rechazadas: solicitudes.value.filter(s => s.estado === 'rechazada').length,
  vendidas: solicitudes.value.filter(s => s.estado === 'vendida').length,
}))

function formatearPrecio(valor) {
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    minimumFractionDigits: 0,
  }).format(valor)
}

function formatearFecha(fecha) {
  if (!fecha) return 'N/A'
  try {
    const d = new Date(fecha)
    return d.toLocaleDateString('es-CO', {
      day: '2-digit', month: 'short', year: 'numeric',
      hour: '2-digit', minute: '2-digit'
    })
  } catch {
    return fecha
  }
}

function estadoBadge(estado) {
  const map = {
    recibida: { class: 'bg-warning text-dark', icon: 'fa-inbox', label: 'Recibida' },
    aceptada: { class: 'bg-success', icon: 'fa-check-circle', label: 'Aceptada' },
    rechazada: { class: 'bg-danger', icon: 'fa-times-circle', label: 'Rechazada' },
    vendida: { class: 'bg-primary', icon: 'fa-truck', label: 'Vendida' },
  }
  return map[estado] || { class: 'bg-secondary', icon: 'fa-question', label: estado }
}

function showNotification(type, message) {
  notification.value = { show: true, type, message }
  setTimeout(() => { notification.value.show = false }, 4000)
}

// Actions - all operate on local state only
function aceptarSolicitud(solicitud) {
  if (!confirm(`¿Aceptar la solicitud #${solicitud.id} de ${solicitud.comprador_nombre}?`)) return
  solicitud.estado = 'aceptada'
  showNotification('success', `Solicitud #${solicitud.id} aceptada. El comprador será notificado.`)
}

function rechazarSolicitud(solicitud) {
  if (!confirm(`¿Rechazar la solicitud #${solicitud.id} de ${solicitud.comprador_nombre}?`)) return
  solicitud.estado = 'rechazada'
  showNotification('danger', `Solicitud #${solicitud.id} rechazada.`)
}

function marcarVendida(solicitud) {
  if (!confirm(`¿Marcar solicitud #${solicitud.id} como vendida?`)) return
  solicitud.estado = 'vendida'
  showNotification('success', `Solicitud #${solicitud.id} marcada como vendida.`)
}

function verDetalle(solicitud) {
  selectedSolicitud.value = solicitud
  showDetail.value = true
}

function cerrarDetalle() {
  showDetail.value = false
  selectedSolicitud.value = null
}
</script>

<template>
  <!-- Notification Toast -->
  <Transition name="toast">
    <div v-if="notification.show"
      class="position-fixed top-0 end-0 m-3 px-4 py-3 rounded-3 shadow-lg text-white fw-semibold"
      :class="notification.type === 'success' ? 'bg-success' : 'bg-danger'"
      style="z-index: 9999; min-width: 280px;">
      <i :class="notification.type === 'success' ? 'fas fa-check-circle' : 'fas fa-exclamation-circle'" class="me-2"></i>
      {{ notification.message }}
    </div>
  </Transition>

  <!-- Header -->
  <div class="d-flex flex-wrap justify-content-between align-items-center mb-4">
    <div>
      <h2 class="mb-1 fw-bold">
        <i class="fas fa-clipboard-list text-success me-2"></i>Solicitudes de Compra
      </h2>
      <p class="text-muted mb-0">Gestiona las solicitudes que recibes de los compradores</p>
    </div>
  </div>

  <!-- Stats Cards -->
  <div class="row g-3 mb-4">
    <div class="col-6 col-md">
      <div class="card border-0 shadow-sm rounded-4 text-center py-3">
        <div class="fs-3 fw-bold text-dark">{{ stats.total }}</div>
        <small class="text-muted">Total</small>
      </div>
    </div>
    <div class="col-6 col-md">
      <div class="card border-0 shadow-sm rounded-4 text-center py-3 border-start border-warning border-3">
        <div class="fs-3 fw-bold text-warning">{{ stats.recibidas }}</div>
        <small class="text-muted">Recibidas</small>
      </div>
    </div>
    <div class="col-6 col-md">
      <div class="card border-0 shadow-sm rounded-4 text-center py-3 border-start border-success border-3">
        <div class="fs-3 fw-bold text-success">{{ stats.aceptadas }}</div>
        <small class="text-muted">Aceptadas</small>
      </div>
    </div>
    <div class="col-6 col-md">
      <div class="card border-0 shadow-sm rounded-4 text-center py-3 border-start border-danger border-3">
        <div class="fs-3 fw-bold text-danger">{{ stats.rechazadas }}</div>
        <small class="text-muted">Rechazadas</small>
      </div>
    </div>
    <div class="col-6 col-md">
      <div class="card border-0 shadow-sm rounded-4 text-center py-3 border-start border-primary border-3">
        <div class="fs-3 fw-bold text-primary">{{ stats.vendidas }}</div>
        <small class="text-muted">Vendidas</small>
      </div>
    </div>
  </div>

  <!-- Filters -->
  <div class="card border-0 shadow-sm rounded-4 mb-4">
    <div class="card-body p-3">
      <div class="row g-3 align-items-end">
        <div class="col-md-5">
          <label class="form-label small fw-bold text-muted text-uppercase">Buscar</label>
          <div class="input-group">
            <span class="input-group-text bg-light border-end-0"><i class="fas fa-search text-muted"></i></span>
            <input v-model="searchQuery" type="text" class="form-control border-start-0 bg-light ps-0"
              placeholder="Nombre, email o ID del comprador...">
          </div>
        </div>
        <div class="col-md-3">
          <label class="form-label small fw-bold text-muted text-uppercase">Estado</label>
          <select v-model="filterEstado" class="form-select">
            <option value="">Todos los estados</option>
            <option value="recibida">Recibidas</option>
            <option value="aceptada">Aceptadas</option>
            <option value="rechazada">Rechazadas</option>
            <option value="vendida">Vendidas</option>
          </select>
        </div>
        <div class="col-md-2">
          <label class="form-label small fw-bold text-muted text-uppercase">Ordenar</label>
          <select v-model="sortBy" class="form-select">
            <option value="reciente">Más recientes</option>
            <option value="mayor_total">Mayor total</option>
            <option value="menor_total">Menor total</option>
          </select>
        </div>
        <div class="col-md-2">
          <button class="btn btn-outline-secondary w-100" @click="filterEstado = ''; searchQuery = ''; sortBy = 'reciente'">
            <i class="fas fa-undo me-1"></i>Limpiar
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- Solicitations Table -->
  <div class="card border-0 shadow-sm rounded-4">
    <div class="card-body p-0">
      <div class="table-responsive">
        <table class="table table-hover mb-0 align-middle">
          <thead class="table-light">
            <tr>
              <th class="px-4 py-3 small text-uppercase text-muted">ID</th>
              <th class="px-4 py-3 small text-uppercase text-muted">Comprador</th>
              <th class="px-4 py-3 small text-uppercase text-muted">Fecha</th>
              <th class="px-4 py-3 small text-uppercase text-muted">Productos</th>
              <th class="px-4 py-3 small text-uppercase text-muted">Total Est.</th>
              <th class="px-4 py-3 small text-uppercase text-muted">Estado</th>
              <th class="px-4 py-3 small text-uppercase text-muted text-end">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="sol in solicitudesFiltradas" :key="sol.id" class="transition-row">
              <td class="px-4 fw-bold text-muted">#{{ sol.id }}</td>
              <td class="px-4">
                <div class="fw-semibold">{{ sol.comprador_nombre }}</div>
                <small class="text-muted d-block">{{ sol.comprador_email }}</small>
                <small class="text-success"><i class="fab fa-whatsapp me-1"></i>{{ sol.comprador_telefono }}</small>
              </td>
              <td class="px-4 text-muted small">{{ formatearFecha(sol.fecha) }}</td>
              <td class="px-4">
                <span class="badge bg-light text-dark border">{{ sol.total_productos_mios }} producto(s)</span>
              </td>
              <td class="px-4 fw-semibold text-success">{{ formatearPrecio(sol.total_estimado) }}</td>
              <td class="px-4">
                <span class="badge rounded-pill px-3 py-2" :class="estadoBadge(sol.estado).class">
                  <i class="fas me-1" :class="estadoBadge(sol.estado).icon"></i>{{ estadoBadge(sol.estado).label }}
                </span>
              </td>
              <td class="px-4 text-end">
                <div class="d-flex justify-content-end gap-1 flex-wrap">
                  <template v-if="sol.estado === 'recibida'">
                    <button class="btn btn-sm btn-success rounded-pill px-3" @click="aceptarSolicitud(sol)">
                      <i class="fas fa-check me-1"></i>Aceptar
                    </button>
                    <button class="btn btn-sm btn-outline-danger rounded-pill px-3" @click="rechazarSolicitud(sol)">
                      <i class="fas fa-times me-1"></i>Rechazar
                    </button>
                  </template>
                  <template v-if="sol.estado === 'aceptada'">
                    <button class="btn btn-sm btn-primary rounded-pill px-3" @click="marcarVendida(sol)">
                      <i class="fas fa-truck me-1"></i>Vendida
                    </button>
                  </template>
                  <button class="btn btn-sm btn-outline-secondary rounded-pill px-2" @click="verDetalle(sol)" title="Ver detalle">
                    <i class="fas fa-eye"></i>
                  </button>
                </div>
              </td>
            </tr>

            <!-- Empty State -->
            <tr v-if="solicitudesFiltradas.length === 0">
              <td colspan="7" class="text-center py-5">
                <i class="fas fa-inbox fa-3x text-muted opacity-25 mb-3"></i>
                <p class="text-muted mb-1 fw-semibold">No hay solicitudes</p>
                <p class="text-muted small mb-0">
                  {{ solicitudes.length === 0
                    ? 'Cuando otros usuarios compren tus productos, aparecerán aquí.'
                    : 'No se encontraron solicitudes con los filtros seleccionados.' }}
                </p>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- Detail Modal -->
  <Transition name="fade">
    <div v-if="showDetail && selectedSolicitud" class="modal d-block" tabindex="-1"
      style="background: rgba(0,0,0,0.5);" @click.self="cerrarDetalle">
      <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content border-0 shadow-lg rounded-4 overflow-hidden">
          <div class="modal-header bg-light border-0 px-4 py-3">
            <div>
              <h5 class="modal-title fw-bold mb-0">
                <i class="fas fa-file-invoice text-success me-2"></i>
                Solicitud #{{ selectedSolicitud.id }}
              </h5>
              <small class="text-muted">{{ formatearFecha(selectedSolicitud.fecha) }}</small>
            </div>
            <button class="btn-close" @click="cerrarDetalle"></button>
          </div>
          <div class="modal-body px-4 py-3">
            <!-- Buyer Info -->
            <div class="row g-3 mb-4">
              <div class="col-md-6">
                <div class="card bg-light border-0 rounded-3 p-3">
                  <small class="text-muted text-uppercase fw-bold">Comprador</small>
                  <div class="fw-semibold fs-5">{{ selectedSolicitud.comprador_nombre }}</div>
                  <div class="text-muted small">{{ selectedSolicitud.comprador_email }}</div>
                  <div class="text-success small"><i class="fab fa-whatsapp me-1"></i>{{ selectedSolicitud.comprador_telefono }}</div>
                </div>
              </div>
              <div class="col-md-6">
                <div class="card bg-light border-0 rounded-3 p-3">
                  <small class="text-muted text-uppercase fw-bold">Estado</small>
                  <div class="mt-1">
                    <span class="badge rounded-pill px-3 py-2 fs-6" :class="estadoBadge(selectedSolicitud.estado).class">
                      <i class="fas me-1" :class="estadoBadge(selectedSolicitud.estado).icon"></i>
                      {{ estadoBadge(selectedSolicitud.estado).label }}
                    </span>
                  </div>
                  <small class="text-muted mt-1">Total: <strong class="text-success">{{ formatearPrecio(selectedSolicitud.total_estimado) }}</strong></small>
                </div>
              </div>
            </div>

            <!-- Products -->
            <h6 class="fw-bold text-muted text-uppercase small mb-3">Productos solicitados</h6>
            <div class="table-responsive">
              <table class="table table-sm">
                <thead class="table-light">
                  <tr>
                    <th>Producto</th>
                    <th class="text-end">Precio Unit.</th>
                    <th class="text-center">Cantidad</th>
                    <th class="text-end">Subtotal</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(prod, idx) in selectedSolicitud.productos" :key="idx">
                    <td class="fw-semibold">{{ prod.id_producto_usuario?.id_producto?.nombre || 'Producto' }}</td>
                    <td class="text-end">{{ formatearPrecio(prod.id_producto_usuario?.precio || 0) }}</td>
                    <td class="text-center">
                      <span class="badge bg-light text-dark border">{{ Math.abs(prod.cantidad || 0) }}</span>
                    </td>
                    <td class="text-end fw-semibold">
                      {{ formatearPrecio(Math.abs(prod.cantidad || 0) * (prod.id_producto_usuario?.precio || 0)) }}
                    </td>
                  </tr>
                </tbody>
                <tfoot>
                  <tr class="table-light">
                    <th colspan="3" class="text-end">Total:</th>
                    <th class="text-end text-success fs-5">{{ formatearPrecio(selectedSolicitud.total_estimado) }}</th>
                  </tr>
                </tfoot>
              </table>
            </div>
          </div>
          <div class="modal-footer border-0 px-4 pb-4">
            <template v-if="selectedSolicitud.estado === 'recibida'">
              <button class="btn btn-success rounded-pill px-4" @click="aceptarSolicitud(selectedSolicitud); cerrarDetalle()">
                <i class="fas fa-check me-1"></i>Aceptar Solicitud
              </button>
              <button class="btn btn-outline-danger rounded-pill px-4" @click="rechazarSolicitud(selectedSolicitud); cerrarDetalle()">
                <i class="fas fa-times me-1"></i>Rechazar
              </button>
            </template>
            <template v-if="selectedSolicitud.estado === 'aceptada'">
              <button class="btn btn-primary rounded-pill px-4" @click="marcarVendida(selectedSolicitud); cerrarDetalle()">
                <i class="fas fa-truck me-1"></i>Marcar como Vendida
              </button>
            </template>
            <button class="btn btn-outline-secondary rounded-pill px-4" @click="cerrarDetalle">Cerrar</button>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.toast-enter-active { transition: all 0.3s ease-out; }
.toast-leave-active { transition: all 0.3s ease-in; }
.toast-enter-from { transform: translateX(100%); opacity: 0; }
.toast-leave-to { transform: translateY(-20px); opacity: 0; }

.fade-enter-active { transition: opacity 0.2s ease; }
.fade-leave-active { transition: opacity 0.15s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.transition-row { transition: background-color 0.15s ease; }
.transition-row:hover { background-color: rgba(5, 150, 105, 0.04) !important; }
</style>

