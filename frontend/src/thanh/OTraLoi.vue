<script setup>
import { ref } from 'vue'

// Nút Trả lời escalation / decision mở (spec 2 §5.2) — dùng ở ngăn bên và trang Phê duyệt. Lớp mockup: .truong .nut.
const props = defineProps({
  gui: { type: Function, required: true },          // (traLoi) => Promise<boolean>; false = lỗi, giữ nội dung
  khoa: { type: Boolean, default: false },
  nhan: { type: String, default: 'Trả lời' },
})
const traLoi = ref('')
const dangGui = ref(false)

async function guiTraLoi() {
  const vb = traLoi.value.trim()
  if (!vb || dangGui.value) return
  dangGui.value = true
  try {
    if ((await props.gui(vb)) !== false) traLoi.value = ''
  } finally {
    dangGui.value = false
  }
}
</script>

<template>
  <form class="o-tra-loi" @submit.prevent="guiTraLoi">
    <label class="truong">Trả lời<textarea v-model="traLoi" rows="3" maxlength="4000" required></textarea></label>
    <div class="hang-nut">
      <button class="nut chinh" type="submit" :disabled="khoa || dangGui || !traLoi.trim()">{{ nhan }}</button>
    </div>
    <p class="nho">Đóng chính bead quyết định, câu trả lời thành lý do đóng. Câu trả lời không cấp quyền làm thao tác
      nguy hiểm (deploy, migrate DB thật, xoá dữ liệu, gửi khách).</p>
  </form>
</template>
