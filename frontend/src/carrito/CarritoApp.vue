<script setup>
import { ref, computed } from 'vue'
import { getCSRFToken } from '../shared/csrf.js'

const props = defineProps({
  items: Array,
  urls: Object
})

const cartItems = ref(props.items)

const total = computed(() =>
  cartItems.value.reduce((sum, item) => sum + item.precio * item.cantidad, 0)
)

function formatearPrecio(valor) {
  return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', minimumFractionDigits: 0 }).format(valor)
}

async function actualizarCantidad(item, delta) {
  const nueva = item.cantidad + delta
  if (nueva < 1) return
  const formData = new URLSearchParams()
  formData.append('cantidad', nueva)
  const res = await fetch(item.urls.actualizar, {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCSRFToken(),
      'Content-Type': 'application/x-www-form-urlencoded',
      'X-Requested-With': 'XMLHttpRequest',
    },
    body: formData
  })
  const data = await res.json()
  if (data.success) item.cantidad = nueva
}

async function eliminarItem(item) {
  if (!confirm('¿Eliminar este producto del carrito?')) return
  const res = await fetch(item.urls.eliminar, {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCSRFToken(),
      'X-Requested-With': 'XMLHttpRequest',
    },
  })
  const data = await res.json()
  if (data.success) {
    cartItems.value = cartItems.value.filter(i => i.producto_id !== item.producto_id)
  }
}
</script>

<template>
  <template v-if="cartItems.length > 0">
    <div class="table-responsive">
      <table class="table table-bordered table-striped mt-4">
        <thead class="table-dark">
          <tr>
            <th>Producto</th>
            <th>Precio Unitario</th>
            <th>Cantidad</th>
            <th>Subtotal</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in cartItems" :key="item.producto_id">
            <td>{{ item.nombre }}</td>
            <td>{{ formatearPrecio(item.precio) }}</td>
            <td style="width: 200px;">
              <div class="input-group input-group-sm">
                <button class="btn btn-outline-secondary" @click="actualizarCantidad(item, -1)">
                  <i class="fas fa-minus"></i>
                </button>
                <input type="number" :value="item.cantidad" min="1" class="form-control text-center fw-bold px-0" readonly>
                <button class="btn btn-outline-secondary" @click="actualizarCantidad(item, 1)">
                  <i class="fas fa-plus"></i>
                </button>
              </div>
            </td>
            <td>{{ formatearPrecio(item.precio * item.cantidad) }}</td>
            <td>
              <button class="btn btn-sm btn-danger" @click="eliminarItem(item)">
                <i class="fas fa-trash"></i>
              </button>
            </td>
          </tr>
        </tbody>
        <tfoot>
          <tr>
            <th colspan="3" class="text-end">Total:</th>
            <th colspan="2" class="fs-4 text-success">{{ formatearPrecio(total) }}</th>
          </tr>
        </tfoot>
      </table>
    </div>
    <div class="d-flex justify-content-between mt-3">
      <a :href="urls.marketplace" class="btn btn-secondary">Seguir Comprando</a>
      <div>
        <a :href="urls.checkout" class="btn btn-primary btn-lg me-2">Crear Solicitud de Compra</a>
        <a :href="urls.checkout_venta" class="btn btn-success btn-lg">Realizar Venta Directa</a>
      </div>
    </div>
  </template>
  <div v-else class="alert alert-info mt-4">
    Tu carrito está vacío. <a :href="urls.marketplace" class="alert-link">Vuelve al marketplace para agregar productos</a>.
  </div>
</template>
