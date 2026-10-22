<script setup>
import { onBeforeUnmount, ref } from 'vue'

// Một lệnh CLI gợi ý + nút "Sao chép" (mockup trang-cai-dat.js `lenh`, D19). Chỉ chép chữ — không chạy gì.
const props = defineProps({ lenh: { type: String, required: true }, ghiChu: { type: String, default: '' } })
const chu = ref('Sao chép')
let hen = null

// Dự phòng khi Clipboard API bị chặn (không HTTPS/không quyền): textarea tạm + execCommand như mockup.
function chepDuPhong(van) {
  const t = document.createElement('textarea')
  t.value = van
  document.body.appendChild(t)
  t.select()
  let ok = false
  try {
    ok = document.execCommand('copy')
  } catch {
    ok = false
  }
  t.remove()
  return ok
}

async function chep() {
  let ok = false
  try {
    await navigator.clipboard.writeText(props.lenh)
    ok = true
  } catch {
    ok = chepDuPhong(props.lenh)
  }
  chu.value = ok ? 'Đã chép' : 'Không chép được'
  clearTimeout(hen)
  hen = setTimeout(() => { chu.value = 'Sao chép' }, 1400)
}
onBeforeUnmount(() => clearTimeout(hen))
</script>

<template>
  <div class="lenh">
    <code>{{ lenh }}</code>
    <button type="button" class="sao-chep" title="Sao chép lệnh" @click="chep">{{ chu }}</button>
    <span v-if="ghiChu" class="nho">{{ ghiChu }}</span>
  </div>
</template>
