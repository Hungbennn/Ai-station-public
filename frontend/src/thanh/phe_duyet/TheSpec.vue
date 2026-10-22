<script setup>
import { coTheDuyetSpec } from '../../luat_spec.js'
import ChiTietSpec from '../ChiTietSpec.vue'
import { dungThaoTac } from './thao_tac.js'

// Thẻ "Spec chờ duyệt" — bản thật có, mockup không vẽ: giữ bố cục cũ, áp lớp `.the-duyet` (D36). "Duyệt spec" gửi
// kèm commit + digest đang xem (thanDuyet, trong thao_tac.js).
const props = defineProps({
  muc: { type: Object, required: true },
  khoa: { type: Boolean, default: false },
  chuKhoa: { type: String, default: '' },
})
const emit = defineEmits(['doi'])
const { gopY, loi, dangGui, moTraVe, duyet, traVe } = dungThaoTac(() => props.muc, emit)
</script>

<template>
  <article class="the the-duyet">
    <div>
      <div class="tren"><span class="ma">{{ muc.bead_id }}</span><span class="chip">{{ muc.du_an }}</span></div>
      <div class="tieu-de">{{ muc.tieu_de }}</div>
    </div>
    <div class="hanh-dong">
      <button class="nut chinh" type="button" :disabled="dangGui || khoa || !coTheDuyetSpec(muc)"
              @click="duyet">Duyệt spec</button>
      <button class="nut" type="button" :disabled="dangGui || khoa" @click="moTraVe = !moTraVe">Trả về + góp ý</button>
    </div>
    <form v-if="moTraVe" class="gop-y" @submit.prevent="traVe">
      <textarea v-model="gopY" rows="3" maxlength="4000" required aria-label="Góp ý"
                placeholder="Góp ý cho thợ (ghi vào notes, bead về hàng chưa chấm)…"></textarea>
      <button class="nut chinh" type="submit" :disabled="dangGui || khoa || !gopY.trim()">Gửi trả về</button>
    </form>
    <ChiTietSpec :muc="muc" />
    <p v-if="chuKhoa" class="nho dong-day">{{ chuKhoa }}</p>
    <p v-if="loi" class="loi dong-day" role="alert">{{ loi }}</p>
  </article>
</template>
