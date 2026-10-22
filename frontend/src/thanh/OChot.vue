<script setup>
// Ô chốt câu hỏi (mockup trang.js moBead, anh-cong-viec-ngan-ben.png): mỗi câu một nhãn "1. …" + ô "Trả lời…",
// nút "Chốt" và "Dẫn ADR" (chuyển sang ô mã ADR). Gửi {tra_loi[]} hoặc {adr} như cũ.
import { ref, watch } from 'vue'

const CAU_CHUNG = 'Chốt chung cho bead (lần chấm không có câu hỏi cụ thể)'
const props = defineProps({
  cauHoi: { type: Array, required: true },
  gui: { type: Function, required: true },
  khoa: { type: Boolean, default: false },      // dự án chỉ quét thử (D37)
})
const traLoi = ref([])
const adr = ref('')
const dungAdr = ref(false)
const dangGui = ref(false)
const cau = () => (props.cauHoi.length ? props.cauHoi : [CAU_CHUNG])
watch(() => props.cauHoi, () => { traLoi.value = cau().map(() => '') }, { immediate: true })
const du = () => (dungAdr.value ? /^ADR-\d{4}$/.test(adr.value.trim()) : traLoi.value.every((t) => t.trim()))

async function chot() {
  if (!du() || dangGui.value || props.khoa) return
  dangGui.value = true
  try {
    await props.gui(dungAdr.value ? { adr: adr.value.trim() } : { tra_loi: traLoi.value.map((t) => t.trim()) })
  } catch {
    // NganBen đã hiện lỗi; mở lại nút để Đại ca sửa và gửi lại
  } finally {
    dangGui.value = false
  }
}
</script>

<template>
  <form class="o-chot" @submit.prevent="chot">
    <label v-if="dungAdr" class="cau-hoi"><span>Mã ADR <span class="nho">— dẫn ADR thay cho trả lời (câu trả lời dài /
      kiến trúc)</span></span><input v-model="adr" class="o" placeholder="ADR-0000" maxlength="8" required></label>
    <template v-else>
      <label v-for="(q, i) in cau()" :key="i" class="cau-hoi"><span><b>{{ i + 1 }}.</b> {{ q }}</span>
        <textarea v-model="traLoi[i]" rows="2" maxlength="4000" placeholder="Trả lời…" required></textarea></label>
    </template>
    <div class="hang-nut">
      <button class="nut chinh" type="submit" :disabled="khoa || dangGui || !du()">Chốt</button>
      <button class="nut" type="button" :aria-pressed="dungAdr ? 'true' : 'false'" @click="dungAdr = !dungAdr">
        {{ dungAdr ? 'Trả lời từng câu' : 'Dẫn ADR' }}</button>
    </div>
    <p class="nho">Tạo bead decision đã đóng, nối vào bead này, gỡ nhãn cột; lượt quét sau chấm lại.</p>
  </form>
</template>
