<script setup>
import { computed } from 'vue'
import { dongLichSuDoi } from '../../luat_lich_su_tu_dong.js'

// Ngăn bên "Lịch sử đổi cài đặt" (mockup nút "Xem lịch sử đổi" → moNganBen; spec "Xem lịch sử đổi"): ai, lúc nào,
// trước → sau. Dùng lại lớp `.ngan-ben`, `.dtg` của ngăn bên Công việc.
const props = defineProps({ duAn: { type: String, required: true }, ds: { type: Array, required: true } })
const emit = defineEmits(['dong'])
const dong = computed(() => props.ds.map(dongLichSuDoi))
</script>

<template>
  <aside class="ngan-ben" aria-label="Lịch sử đổi cài đặt" @keydown.esc="emit('dong')">
    <button class="dong" type="button" aria-label="Đóng lịch sử đổi" @click="emit('dong')">×</button>
    <h2>Lịch sử đổi cài đặt</h2>
    <p>{{ duAn }} · mỗi dòng do Đại ca (dashboard) hoặc trạm ghi; không bao giờ có giá trị bí mật.</p>
    <ul class="dtg">
      <li v-for="(r, i) in dong" :key="i"><span class="mono">{{ r.gio }}</span>{{ r.viec }} —
        <span class="nho">{{ r.doi }} · {{ r.ai }}</span></li>
    </ul>
  </aside>
</template>
