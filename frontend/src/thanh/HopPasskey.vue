<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { datHoi } from '../passkey.js'
const hop = ref(null), yeuCau = ref(null)
let traLoi = null, nutCu = null
function dong(ok) {
  hop.value?.close()
  const tra = traLoi; traLoi = null; yeuCau.value = null
  nutCu?.focus(); tra?.(ok)
}
onMounted(() => datHoi(async yc => {
  if (traLoi) return false
  nutCu = document.activeElement
  yeuCau.value = yc
  const ket = new Promise(resolve => { traLoi = resolve })
  await nextTick(); hop.value.showModal()
  return ket
}))
onUnmounted(() => { dong(false); datHoi(async () => false) })
</script>
<template>
  <dialog ref="hop" class="pk-hop the" aria-labelledby="pk-tieu-de" @cancel.prevent="dong(false)">
    <h2 id="pk-tieu-de">Chạm Touch ID để xác nhận</h2>
    <p v-if="yeuCau?.loai === 'r'">Thao tác này luôn cần chạm lại, kể cả khi phiên còn hạn.</p>
    <p v-else-if="yeuCau?.loai === 'dang-ky'">Tạo passkey cho Đại ca trên thiết bị này.</p>
    <p v-else>Cho phép thao tác nguy hiểm trên trình duyệt này trong 8 giờ.</p>
    <div v-if="yeuCau" class="pk-tom-tat">
      <strong>{{ yeuCau.hienThi.hanhDong }}</strong>
      <p>{{ yeuCau.hienThi.dich }}</p>
    </div>
    <p>Trên Windows: dùng Windows Hello hoặc khoá USB có xác minh người dùng.</p>
    <p>Để dùng điện thoại, chọn “Thiết bị khác” trong hộp của trình duyệt rồi quét QR ở đó.</p>
    <div class="hang-nut">
      <button class="nut" autofocus @click="dong(false)">Huỷ</button>
      <button class="nut chinh" @click="dong(true)">Tiếp tục xác nhận</button>
    </div>
  </dialog>
</template>
<style scoped>
.pk-hop { max-width: 620px; padding: 30px; border: 1px solid var(--vien); border-radius: 16px; }
.pk-hop::backdrop { background: color-mix(in srgb, var(--chu) 40%, transparent); }
.pk-tom-tat { padding: 14px; background: var(--nen-3); border-radius: 8px; }
.hang-nut { display: flex; justify-content: end; gap: 10px; margin-top: 20px; }
</style>
