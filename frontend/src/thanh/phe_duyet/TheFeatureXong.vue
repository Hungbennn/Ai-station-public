<script setup>
import { dungThaoTac } from './thao_tac.js'

// Thẻ "Feature xong, chờ đóng" — bản thật có, mockup không vẽ: giữ câu + nút cũ, áp lớp `.the-duyet` (D36).
const props = defineProps({
  muc: { type: Object, required: true },
  khoa: { type: Boolean, default: false },
  chuKhoa: { type: String, default: '' },
})
const emit = defineEmits(['doi'])
const { loi, dangGui, duyet } = dungThaoTac(() => props.muc, emit)
</script>

<template>
  <article class="the the-duyet">
    <div>
      <div class="tren"><span class="ma">{{ muc.bead_id }}</span><span class="chip">{{ muc.du_an }}</span></div>
      <div class="tieu-de">{{ muc.tieu_de }}</div>
      <div class="nho">Mọi {{ muc.chi_tiet.so_con }} bead con đã đóng. Trạm không tự đóng feature (#16).</div>
    </div>
    <div class="hanh-dong">
      <button class="nut chinh" type="button" :disabled="dangGui || khoa" @click="duyet">Đóng feature</button>
    </div>
    <p v-if="chuKhoa" class="nho dong-day">{{ chuKhoa }}</p>
    <p v-if="loi" class="loi dong-day" role="alert">{{ loi }}</p>
  </article>
</template>
