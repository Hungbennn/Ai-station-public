<script setup>
import { computed } from 'vue'
import { chiTietHe, chipHe, tieuDeHe } from '../../luat_phe_duyet.js'
import { dungThaoTac } from './thao_tac.js'

// Thẻ "Hệ cần xem" (mockup trang.js vePheDuyet, `.the-duyet.he`): chip loại + dự án, tiêu đề, chi tiết; "Mở Đội ngũ
// AI" khi là cầu dao khe; "Thử lại" (chấm lại 1a) khi mục gắn bead — bản thật có, mockup không vẽ (D36).
const props = defineProps({
  muc: { type: Object, required: true },
  khoa: { type: Boolean, default: false },
  chuKhoa: { type: String, default: '' },
})
const emit = defineEmits(['doi'])
const { loi, dangGui, thuLai } = dungThaoTac(() => props.muc, emit)
const chip = computed(() => chipHe(props.muc))
const ct = computed(() => props.muc.chi_tiet || {})
</script>

<template>
  <article class="the the-duyet he">
    <div>
      <div class="tren">
        <span class="chip" :class="chip.lop">{{ chip.chu }}</span><span class="chip">{{ muc.du_an }}</span>
        <span v-if="muc.bead_id" class="ma">{{ muc.bead_id }}</span>
      </div>
      <div class="tieu-de">{{ tieuDeHe(muc) }}</div>
      <div class="nho">{{ chiTietHe(muc) }}</div>
    </div>
    <div class="hanh-dong">
      <router-link v-if="ct.khe_id" class="nut" to="/doi-ngu">Mở Đội ngũ AI</router-link>
      <button v-if="muc.bead_id" class="nut" type="button" :disabled="dangGui || khoa" @click="thuLai">Thử lại</button>
    </div>
    <p v-if="chuKhoa" class="nho dong-day">{{ chuKhoa }}</p>
    <p v-if="loi" class="loi dong-day" role="alert">{{ loi }}</p>
  </article>
</template>
