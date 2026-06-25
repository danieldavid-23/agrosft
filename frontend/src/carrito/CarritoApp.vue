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
  return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(valor)
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
  <div class="cart-container mt-4 mb-5">
    <div v-if="cartItems.length > 0" class="card premium-card border-0">
      <div class="card-header bg-transparent border-bottom-0 pt-4 pb-0 px-4">
        <h4 class="mb-0 fw-bold" style="color: var(--primary-color);"><i class="fas fa-shopping-basket me-2"></i> Tu Carrito de Compras</h4>
      </div>
      <div class="card-body p-4">
        <div class="table-responsive">
          <table class="table table-hover align-middle custom-table mb-0">
            <thead>
              <tr>
                <th scope="col" class="text-uppercase fw-bold">Producto</th>
                <th scope="col" class="text-uppercase fw-bold text-center">Precio Unitario</th>
                <th scope="col" class="text-uppercase fw-bold text-center" style="width: 160px;">Cantidad</th>
                <th scope="col" class="text-uppercase fw-bold text-end">Subtotal</th>
                <th scope="col" class="text-uppercase fw-bold text-center" style="width: 80px;"></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in cartItems" :key="item.producto_id">
                <td class="fw-semibold" style="color: var(--text-main); font-size: 1.05rem;">
                  <div class="d-flex align-items-center">
                    <div class="product-icon me-3">
                      <i class="fas fa-leaf text-success opacity-75"></i>
                    </div>
                    {{ item.nombre }}
                  </div>
                </td>
                <td class="text-center text-muted fw-medium">{{ formatearPrecio(item.precio) }}</td>
                <td>
                  <div class="input-group input-group-sm quantity-control mx-auto shadow-sm">
                    <button class="btn btn-qty" @click="actualizarCantidad(item, -1)">
                      <i class="fas fa-minus"></i>
                    </button>
                    <input type="text" :value="item.cantidad" class="form-control text-center fw-bold px-0 bg-white" readonly>
                    <button class="btn btn-qty" @click="actualizarCantidad(item, 1)">
                      <i class="fas fa-plus"></i>
                    </button>
                  </div>
                </td>
                <td class="text-end fw-bold" style="color: var(--primary-dark);">{{ formatearPrecio(item.precio * item.cantidad) }}</td>
                <td class="text-center">
                  <button class="btn btn-sm btn-action-danger rounded-circle shadow-sm" @click="eliminarItem(item)" title="Eliminar producto">
                    <i class="fas fa-trash-alt"></i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <div class="d-flex flex-column flex-md-row justify-content-between align-items-center mt-4 pt-4 border-top">
          <a :href="urls.marketplace" class="btn btn-outline-secondary rounded-pill px-4 mb-3 mb-md-0 fw-semibold">
            <i class="fas fa-arrow-left me-2"></i>Seguir Explorando
          </a>
          <div class="text-end total-section p-3 rounded-4 shadow-sm">
            <span class="text-muted text-uppercase fw-bold me-3" style="letter-spacing: 0.05em; font-size: 0.85rem;">Total Estimado:</span>
            <span class="fs-2 fw-bolder" style="color: var(--primary-color);">{{ formatearPrecio(total) }}</span>
          </div>
        </div>
      </div>
      
      <div class="card-footer bg-transparent border-top-0 pb-4 px-4 d-flex justify-content-end gap-3 flex-wrap">
        <a :href="urls.checkout_venta" class="btn btn-success rounded-pill px-4 py-2 fw-bold shadow-sm d-flex align-items-center">
          <i class="fas fa-hand-holding-dollar me-2 fs-5"></i>Venta Directa
        </a>
        <a :href="urls.checkout" class="btn btn-primary rounded-pill px-4 py-2 fw-bold shadow-sm d-flex align-items-center">
          <i class="fas fa-clipboard-check me-2 fs-5"></i>Crear Solicitud de Compra
        </a>
      </div>
    </div>
    
    <div v-else class="card premium-card border-0 text-center p-5">
      <div class="empty-cart-icon mb-4">
        <div class="icon-circle mx-auto d-flex align-items-center justify-content-center bg-light rounded-circle shadow-sm" style="width: 100px; height: 100px;">
          <i class="fas fa-shopping-basket fa-3x" style="color: var(--border-color);"></i>
        </div>
      </div>
      <h3 class="fw-bold mb-3" style="color: var(--text-main);">Tu carrito está vacío</h3>
      <p class="text-muted mb-4 fs-5">Parece que aún no has agregado ningún producto agrícola.</p>
      <div>
        <a :href="urls.marketplace" class="btn btn-primary rounded-pill px-5 py-3 fw-bold shadow-sm fs-5">
          <i class="fas fa-store me-2"></i>Ir al Marketplace
        </a>
      </div>
    </div>
  </div>
</template>

<style scoped>
.premium-card {
  box-shadow: var(--shadow-lg, 0 10px 15px -3px rgba(0,0,0,0.1));
  border-radius: var(--radius-xl, 1.5rem);
  background-color: var(--surface-color, #fff);
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.custom-table th {
  border-bottom: 2px solid var(--border-color, #D6D8CC);
  color: var(--text-muted, #7A8A7D);
  font-size: 0.8rem;
  letter-spacing: 0.05em;
  padding-bottom: 1rem;
}

.custom-table td {
  padding: 1.25rem 0.5rem;
  border-bottom: 1px solid rgba(214, 216, 204, 0.4);
}

.product-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background-color: var(--primary-light, #E8F5E8);
  display: flex;
  align-items: center;
  justify-content: center;
}

.quantity-control {
  border-radius: var(--radius-md, 0.625rem);
  overflow: hidden;
  border: 1px solid var(--border-color, #D6D8CC);
}

.btn-qty {
  background-color: #f8fafc;
  color: var(--text-main, #3D5245);
  border: none;
  transition: all 0.2s;
  padding: 0.25rem 0.75rem;
}

.btn-qty:hover {
  background-color: var(--primary-light, #E8F5E8);
  color: var(--primary-color, #3C8D3C);
}

.quantity-control input {
  border: none !important;
  color: var(--text-main, #3D5245);
}

.quantity-control input:focus {
  box-shadow: none;
}

.btn-action-danger {
  background-color: #fff;
  color: var(--danger-color, #dc2626);
  border: 1px solid var(--border-color, #D6D8CC);
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  width: 36px;
  height: 36px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0;
}

.btn-action-danger:hover {
  background-color: var(--danger-color, #dc2626);
  color: #fff;
  border-color: var(--danger-color, #dc2626);
  transform: translateY(-2px);
  box-shadow: 0 4px 6px rgba(220, 38, 38, 0.2) !important;
}

.total-section {
  background-color: var(--primary-light, #E8F5E8);
  border: 1px solid rgba(60, 141, 60, 0.15);
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-width: 300px;
}

.btn-primary {
  background-color: var(--primary-color, #3C8D3C);
  border-color: var(--primary-color, #3C8D3C);
}
.btn-primary:hover {
  background-color: var(--primary-hover, #2E7535);
  border-color: var(--primary-hover, #2E7535);
  transform: translateY(-1px);
}

.btn-success {
  background-color: var(--secondary-color, #E8853B);
  border-color: var(--secondary-color, #E8853B);
}
.btn-success:hover {
  background-color: #D97A30;
  border-color: #D97A30;
  transform: translateY(-1px);
}
</style>
