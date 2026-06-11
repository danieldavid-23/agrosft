<script setup>
import { ref } from 'vue'
import { getCSRFToken } from '../shared/csrf.js'

const props = defineProps({
  initialSolicitudes: Array,
  urls: Object
})

const solicitudes = ref(props.initialSolicitudes)

function formatearPrecio(valor) {
  return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', minimumFractionDigits: 0 }).format(valor)
}

async function cambiarEstado(solicitud, accion) {
  if (accion === 'aceptar' && !confirm('¿Aceptar esta solicitud?')) return
  if (accion === 'rechazar' && !confirm('¿Rechazar esta solicitud?')) return

  const url = accion === 'aceptar'
    ? solicitud.urls.aceptar
    : solicitud.urls.rechazar

  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCSRFToken(),
      'X-Requested-With': 'XMLHttpRequest',
    },
  })
  const data = await res.json()
  if (data.success) {
    solicitud.estado = accion === 'aceptar' ? 'aceptada' : 'rechazada'
  }
}
</script>

<template>
  <div class="d-flex justify-content-between align-items-center mb-4">
    <div>
      <h2 class="mb-1"><i class="fas fa-clipboard-list text-success me-2"></i>{{ urls.titulo || 'Solicitudes Recibidas' }}</h2>
      <p class="text-muted mb-0">{{ urls.subtitulo || 'Usuarios que quieren comprar tus productos' }}</p>
    </div>
  </div>

  <div class="card border-0 shadow-sm rounded-lg">
    <div class="card-body p-0">
      <div class="table-responsive">
        <table class="table table-hover mb-0">
          <thead class="table-light">
            <tr>
              <th class="px-4 py-3">ID</th>
              <th class="px-4 py-3">Comprador</th>
              <th class="px-4 py-3">Fecha</th>
              <th class="px-4 py-3">Mis Productos</th>
              <th class="px-4 py-3">Total Est.</th>
              <th class="px-4 py-3">Estado</th>
              <th class="px-4 py-3 text-end">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="solicitud in solicitudes" :key="solicitud.id">
              <td class="px-4 py-3 align-middle fw-bold text-muted">#{{ solicitud.id }}</td>
              <td class="px-4 py-3 align-middle">
                <div class="fw-bold">{{ solicitud.comprador_nombre }}</div>
                <small class="text-muted">{{ solicitud.comprador_email }}</small>
                <br><small class="text-success"><i class="fab fa-whatsapp"></i> {{ solicitud.comprador_telefono }}</small>
              </td>
              <td class="px-4 py-3 align-middle">{{ solicitud.fecha }}</td>
              <td class="px-4 py-3 align-middle">
                <span class="badge bg-primary">{{ solicitud.total_productos_mios }} producto(s) tuyos</span>
              </td>
              <td class="px-4 py-3 align-middle fw-semibold">{{ formatearPrecio(solicitud.total_estimado) }}</td>
              <td class="px-4 py-3 align-middle">
                <span class="badge bg-warning text-dark"><i class="fas fa-inbox me-1"></i>{{ solicitud.estado }}</span>
              </td>
              <td class="px-4 py-3 align-middle text-end">
                <div class="d-flex justify-content-end gap-2">
                  <template v-if="solicitud.estado === 'recibida'">
                    <button class="btn btn-sm btn-success rounded-pill" @click="cambiarEstado(solicitud, 'aceptar')">
                      <i class="fas fa-check me-1"></i> Aceptar
                    </button>
                    <button class="btn btn-sm btn-danger rounded-pill" @click="cambiarEstado(solicitud, 'rechazar')">
                      <i class="fas fa-times me-1"></i> Rechazar
                    </button>
                  </template>
                  <a :href="solicitud.urls.detalle" class="btn btn-sm btn-outline-primary rounded-pill">
                    <i class="fas fa-eye"></i>
                  </a>
                </div>
              </td>
            </tr>
            <tr v-if="solicitudes.length === 0">
              <td colspan="7" class="text-center py-5 text-muted">
                <i class="fas fa-inbox fa-3x mb-3 text-light"></i>
                <p class="mb-0">No has recibido solicitudes de compra aún.</p>
                <p class="small">Cuando otros usuarios compren tus productos, aparecerán aquí.</p>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
