<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import '../kieu/usage.css'
import { doc } from '../api.js'
import { kho } from '../kho.js'
import { SO_NGAY_USAGE, khoangNgay, moiNhatTruoc, oTong } from '../luat_usage.js'
import BangUsage from '../thanh/BangUsage.vue'
import DauTrang from '../thanh/DauTrang.vue'
import BieuDoUsage from '../thanh/usage/BieuDoUsage.vue'
import KhoiCcusage from '../thanh/usage/KhoiCcusage.vue'
import KhoiHanMuc from '../thanh/usage/KhoiHanMuc.vue'

// Trang Usage & chi phí (mockup trang-usage.js veUsage, D36; D39: số gọn + title, giữ khối hạn mức, bỏ phần
// "minh hoạ"). Dữ liệu GET /api/usage?so_ngay=; tải lại khi đổi khoảng và khi có sự kiện doi_ngu_doi.
const MO_TA = 'Token và chi phí từ sự kiện của trạm: mỗi lần chạy CLI của khe và mỗi lần bộ chấm cột gọi Claude '
  + 'API. Ngày theo giờ Việt Nam, tuần theo ISO.'
const CHE = [['chi_phi', 'Chi phí'], ['token', 'Token vào + ra']]
const soNgay = ref(14)
const che = ref('chi_phi')
const dl = ref(null)
const loi = ref('')
const o = computed(() => (dl.value ? oTong(dl.value) : []))
const cheThat = computed(() => (dl.value && dl.value.co_bang_gia ? che.value : 'token'))   // không có giá → token

async function tai() {
  try {
    dl.value = await doc(`/api/usage?so_ngay=${soNgay.value}`)
    loi.value = ''
  } catch (e) {
    loi.value = e.message
  }
}
onMounted(tai)
watch(soNgay, tai)
watch(() => kho.phienBanDoiNgu, tai)
</script>

<template>
  <div class="us-trang">
    <DauTrang tieu-de="Usage & chi phí" :mo-ta="MO_TA">
      <template #cong-cu>
        <span v-if="dl" class="nho">{{ khoangNgay(dl.tu, dl.den) }}</span>
        <div class="nhom-nut" role="group" aria-label="Khoảng">
          <button v-for="n in SO_NGAY_USAGE" :key="n" type="button" :class="{ chon: n === soNgay }"
            :aria-pressed="n === soNgay" @click="soNgay = n">{{ n }} ngày</button>
        </div>
      </template>
    </DauTrang>
    <p v-if="loi" class="loi" role="alert">{{ loi }}</p>
    <template v-if="dl">
      <p class="nho us-ghi"><span>Chi phí của khe (gói thuê bao) là <b>giá tương đương</b> theo bảng giá, không phải
        tiền trả thêm; chỉ bộ chấm cột là tiền API thật.</span></p>
      <div v-if="!dl.co_bang_gia" class="canh-bao us-canh">Chưa có bảng giá
        (<span class="mono">usage.gia_usd_moi_trieu_token</span>) — chi phí để trống.</div>
      <div class="tq-so us-so">
        <div v-for="x in o" :key="x.ten" :title="x.tieuDe || null"><b>{{ x.gt }}</b><span class="nho">{{ x.ten }}</span>
          <span v-if="x.phu" class="nho us-phu">{{ x.phu }}</span></div>
      </div>
      <section class="the us-the-bd">
        <h3 class="tq-h">Theo ngày
          <span v-if="dl.co_bang_gia" class="nhom-nut us-phai" role="group" aria-label="Đại lượng">
            <button v-for="[m, ten] in CHE" :key="m" type="button" :class="{ chon: m === che }"
              :aria-pressed="m === che" @click="che = m">{{ ten }}</button>
          </span></h3>
        <BieuDoUsage :theo-ngay="dl.theo_ngay" :tu="dl.tu" :den="dl.den" :che="cheThat" />
      </section>
      <section class="the us-khoi"><h3 class="tq-h">Theo khe / nguồn</h3>
        <BangUsage ten-khoa="Khe / nguồn" :dong="dl.theo_nguon" la-nguon ti-trong /></section>
      <div class="tq-luoi us-luoi">
        <section class="the"><h3 class="tq-h">Theo dự án</h3>
          <BangUsage ten-khoa="Dự án" :dong="dl.theo_du_an" /></section>
        <section class="the"><h3 class="tq-h">Theo tuần</h3>
          <BangUsage ten-khoa="Tuần (ISO)" :dong="moiNhatTruoc(dl.theo_tuan)" /></section>
      </div>
      <section class="the us-khoi"><h3 class="tq-h">Theo ngày <span class="nho us-h-phu">{{ dl.theo_ngay.length }} ngày
        có sự kiện · mới nhất trước</span></h3>
        <BangUsage ten-khoa="Ngày" :dong="moiNhatTruoc(dl.theo_ngay)" cuon /></section>
    </template>
    <KhoiHanMuc />
    <KhoiCcusage v-if="dl" :ccusage="dl.ccusage" />
  </div>
</template>
