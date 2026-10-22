<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { capNhat } from '../quyen_passkey.js'
import { goiPasskey, hienPhien } from '../passkey.js'
const tt = ref(null), loi = ref(false)
let timer
async function tai() {
  capNhat(null)
  try { tt.value = await goiPasskey('trang-thai'); loi.value = false; capNhat(tt.value) }
  catch { tt.value = null; loi.value = true }
}
onMounted(() => { tai(); timer = setInterval(tai, 60000); window.addEventListener('focus', tai) })
onUnmounted(() => { clearInterval(timer); window.removeEventListener('focus', tai) })
</script>
<template>
  <router-link class="vien-tt" to="/tai-khoan/thiet-bi" role="status">
    {{ loi ? 'Chưa đọc được phiên' : hienPhien(tt) }}
  </router-link>
</template>
