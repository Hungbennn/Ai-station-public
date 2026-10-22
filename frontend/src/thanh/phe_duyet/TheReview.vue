<script setup>
import { computed } from 'vue'
import { NHAN_PR_TRAM, canhBaoPrTram, lopPrTram } from '../../giao_viec.js'
import { laLinkAnToan } from '../../luat.js'
import { linkPrReview, moTaReview, nutDongReview } from '../../luat_phe_duyet.js'
import { dungThaoTac } from './thao_tac.js'

// Thẻ "Chờ review để đóng" và "Cờ đỏ" (mockup trang.js theReview; Q7/D38: hiện trạng thái PR trạm `pr_tram`).
const props = defineProps({
  muc: { type: Object, required: true },
  khoa: { type: Boolean, default: false },
  chuKhoa: { type: String, default: '' },
})
const emit = defineEmits(['doi'])
const { gopY, loi, dangGui, moTraVe, duyet, traVe } = dungThaoTac(() => props.muc, emit)
const ct = computed(() => props.muc.chi_tiet || {})
const prt = computed(() => ct.value.pr_tram || null)
const link = computed(() => linkPrReview(props.muc))
// Link PR trạm: "PR #12 ↗"; chỉ có link bàn giao cũ: "Mở PR (bàn giao + diff)".
const nhanLink = computed(() => (prt.value && laLinkAnToan(prt.value.url)
  ? `${Number.isInteger(prt.value.so) ? `PR #${prt.value.so}` : 'PR'} ↗` : 'Mở PR (bàn giao + diff)'))
const nutDong = computed(() => nutDongReview(props.muc))
const tat = computed(() => dangGui.value || props.khoa)
</script>

<template>
  <article class="the the-duyet">
    <div>
      <div class="tren">
        <span class="ma">{{ muc.bead_id }}</span><span class="chip">{{ muc.du_an }}</span>
        <span v-if="muc.loai === 'co-do'" class="chip tt-loi">cờ đỏ</span>
        <span v-if="lopPrTram(prt)" class="chip" :class="lopPrTram(prt)">{{ NHAN_PR_TRAM[prt.trang_thai] }}</span>
        <a v-if="link" class="nho" :href="link" target="_blank" rel="noopener noreferrer">{{ nhanLink }}</a>
        <span v-else class="nho">Chưa có link PR GitHub.</span>
      </div>
      <div class="tieu-de">{{ muc.tieu_de }}</div>
      <div v-if="moTaReview(muc)" class="nho">{{ moTaReview(muc) }}</div>
      <div v-if="canhBaoPrTram(prt)" class="canh-bao">{{ canhBaoPrTram(prt) }}</div>
      <ul v-if="ct.loi && ct.loi.length" class="canh-bao"><li v-for="l in ct.loi" :key="l">{{ l }}</li></ul>
    </div>
    <div v-if="muc.loai === 'cho-review'" class="hanh-dong">
      <span v-if="nutDong === 'tu-dong'" class="nho">trạm đã xác minh — sẽ tự đóng</span>
      <button v-else-if="nutDong === 'da-merge'" class="nut" type="button" :disabled="tat" @click="duyet">
        Đã merge trên GitHub → đóng bead</button>
      <button class="nut chinh" type="button" :disabled="tat" @click="duyet">Duyệt</button>
      <button class="nut" type="button" :disabled="tat" @click="moTraVe = !moTraVe">Trả về + góp ý</button>
    </div>
    <form v-if="moTraVe" class="gop-y" @submit.prevent="traVe">
      <textarea v-model="gopY" rows="3" maxlength="4000" required aria-label="Góp ý"
                placeholder="Góp ý cho thợ (ghi vào notes, bead về hàng chưa chấm)…"></textarea>
      <button class="nut chinh" type="submit" :disabled="tat || !gopY.trim()">Gửi trả về</button>
    </form>
    <p v-if="nutDong === 'da-merge'" class="nho dong-day">
      Xác nhận "đã merge" là thao tác tay của Đại ca, không phải bằng chứng máy.</p>
    <p v-if="chuKhoa" class="nho dong-day">{{ chuKhoa }}</p>
    <p v-if="loi" class="loi dong-day" role="alert">{{ loi }}</p>
  </article>
</template>
