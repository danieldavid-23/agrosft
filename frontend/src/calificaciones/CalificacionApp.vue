<script setup>
import { ref, computed } from 'vue'
import { getCSRFToken } from '../shared/csrf.js'

const props = defineProps({
  movimientoDetalle: Object,
  urls: Object
})

const rating = ref(props.movimientoDetalle.calificacion || 0)
const hoverRating = ref(0)
const submitting = ref(false)
const submitted = ref(!!props.movimientoDetalle.calificacion)
const error = ref('')

const displayRating = computed(() => hoverRating.value || rating.value)

async function submitRating() {
  if (rating.value === 0) {
    error.value = 'Selecciona una calificación'
    return
  }
  submitting.value = true
  error.value = ''

  const formData = new URLSearchParams()
  formData.append('calificacion', rating.value)

  const res = await fetch(props.urls.calificar, {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCSRFToken(),
      'Content-Type': 'application/x-www-form-urlencoded',
      'X-Requested-With': 'XMLHttpRequest',
    },
    body: formData
  })
  const data = await res.json()
  if (data.success) {
    submitted.value = true
  } else {
    error.value = data.error || 'Error al enviar calificación'
  }
  submitting.value = false
}

function estrellaClase(estrella) {
  if (displayRating.value >= estrella) return 'fas fa-star text-warning'
  if (displayRating.value >= estrella - 0.5) return 'fas fa-star-half-alt text-warning'
  return 'far fa-star text-warning'
}
</script>

<template>
  <div class="row justify-content-center">
    <div class="col-md-8">
      <div class="card">
        <div class="card-header">
          <h3 class="mb-0">Calificar Transacción</h3>
        </div>
        <div class="card-body">
          <div class="alert alert-info">
            <h5>Detalles de la Transacción</h5>
            <p><strong>Producto:</strong> {{ movimientoDetalle.producto_nombre }}</p>
            <p><strong>Cantidad:</strong> {{ movimientoDetalle.cantidad }}</p>
            <p><strong>Fecha:</strong> {{ movimientoDetalle.fecha }}</p>
            <p><strong>Tipo:</strong> {{ movimientoDetalle.tipo }}</p>
          </div>

          <template v-if="!submitted">
            <div class="text-center mb-4">
              <label class="form-label fw-bold fs-5">Tu calificación</label>
              <div class="rating-stars fs-1">
                <span v-for="i in [1,2,3,4,5]" :key="i"
                  class="cursor-pointer"
                  @click="rating = i"
                  @mouseenter="hoverRating = i"
                  @mouseleave="hoverRating = 0">
                  <i :class="estrellaClase(i)"></i>
                </span>
              </div>
              <small class="text-muted">Selecciona de 1 a 5 estrellas</small>
              <div v-if="error" class="alert alert-danger mt-2">{{ error }}</div>
            </div>

            <div class="mt-3 text-center">
              <button class="btn btn-primary" :disabled="submitting" @click="submitRating">
                <i class="fas fa-star"></i> {{ submitting ? 'Enviando...' : 'Enviar Calificación' }}
              </button>
              <a :href="urls.historial" class="btn btn-secondary ms-2">Cancelar</a>
            </div>
          </template>

          <div v-else class="text-center py-4">
            <i class="fas fa-check-circle text-success fs-1 mb-3"></i>
            <h4>¡Calificación enviada!</h4>
            <p class="text-muted">Tu calificación de {{ rating }} estrellas ha sido registrada.</p>
            <a :href="urls.historial" class="btn btn-primary">Volver al historial</a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.cursor-pointer { cursor: pointer; }
.rating-stars span {
  transition: transform 0.15s ease;
  display: inline-block;
}
.rating-stars span:hover {
  transform: scale(1.2);
}
</style>
