<script setup>
import { computed } from 'vue'
import { chipNguoiHoi, duongDanTraLoi } from '../../luat_phe_duyet.js'

// Thẻ "Bí / escalation" và "Decision mở" (mockup trang.js vePheDuyet): mã, dự án, chip "<khe> hỏi · <bước>" (T4),
// tiêu đề, câu hỏi; "Trả lời" dẫn sang ngăn bên trang Công việc, nơi có ô trả lời (OTraLoi). `khoa` nhận chung từ
// trang nhưng link chỉ dẫn đường nên không khoá; câu "chỉ quét thử" vẫn hiện (D37).
const props = defineProps({
  muc: { type: Object, required: true },
  khoa: { type: Boolean, default: false },
  chuKhoa: { type: String, default: '' },
})
const nguoiHoi = computed(() => chipNguoiHoi(props.muc))
const cauHoi = computed(() => (props.muc.chi_tiet && props.muc.chi_tiet.cau_hoi) || '')
</script>

<template>
  <article class="the the-duyet">
    <div>
      <div class="tren">
        <span class="ma">{{ muc.bead_id }}</span><span class="chip">{{ muc.du_an }}</span>
        <span v-if="nguoiHoi" class="chip tt-can_nguoi">{{ nguoiHoi }}</span>
      </div>
      <div class="tieu-de">{{ muc.tieu_de }}</div>
      <div v-if="cauHoi" class="nho">{{ cauHoi }}</div>
    </div>
    <div class="hanh-dong">
      <router-link class="nut chinh" :to="duongDanTraLoi(muc)">Trả lời</router-link>
    </div>
    <p v-if="chuKhoa" class="nho dong-day">{{ chuKhoa }}</p>
  </article>
</template>
