<script setup>
const props = defineProps({
  urls: Object
})
</script>

<template>
  <footer class="footer">
    <div class="container text-center">
      <div class="d-flex align-items-center justify-content-center gap-2 mb-3">
        <img :src="urls.logo" alt="AgroSFT" height="24">
        <h5 class="mb-0 fw-bold">AgroSFT</h5>
      </div>
      <p class="mb-2 text-muted small">&copy; 2026 Sistema de Gestión Agrícola</p>
      <div class="d-flex justify-content-center gap-3 small">
        <a :href="urls.terminos">Términos y Condiciones</a>
        <span class="text-muted"> &bull; </span>
        <a href="#">Política de Privacidad</a>
      </div>
    </div>
  </footer>
</template>
