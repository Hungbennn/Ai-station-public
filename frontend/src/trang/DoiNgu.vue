<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import '../kieu/doi-ngu.css'
import { doc } from '../api.js'
import { duocGhi } from '../quyen_passkey.js'
import { kho } from '../kho.js'
import { SO_NGAY_BANG_DIEM, dinhDangSo, duongDanDoiNgu, oTiLe } from '../luat_doi_ngu.js'
import DauTrang from '../thanh/DauTrang.vue'
import TheKhe from '../thanh/TheKhe.vue'

// Trang Đội ngũ AI theo mockup trang.js veDoiNgu (D20). Nhịp tim không phải sự kiện (spec 3 §10) → "mất kết nối"
// chỉ thấy khi tải lại; tải lại mỗi 5 giây (G15) và khi SSE báo đội ngũ đổi.
const CHU_KY_MS = 5000
const MO_TA = 'Mỗi khe một thẻ: trạng thái, việc đang giữ, hạn mức còn lại. Tắt khe để dành hạn mức cho việc tay.'
const dl = ref(null)
const loi = ref('')
const duAn = ref('')                      // D14: bảng điểm lọc theo dự án + số ngày; mặc định mọi dự án, 30 ngày
const soNgay = ref(30)
const dsDuAn = ref([])
const laDaiCa = computed(() => duocGhi(kho.trangThai))
let hen = null

async function tai() {
  try {
    dl.value = await doc(duongDanDoiNgu(duAn.value, soNgay.value))
    loi.value = ''
  } catch (e) {
    loi.value = e.message
  }
}
onMounted(async () => {
  tai()
  hen = setInterval(tai, CHU_KY_MS)
  try { dsDuAn.value = (await doc('/api/du-an')).du_an.map((d) => d.ten) } catch (e) { loi.value = e.message }
})
onUnmounted(() => clearInterval(hen))
watch([() => kho.phienBanDoiNgu, duAn, soNgay], tai)
</script>

<template>
  <DauTrang tieu-de="Đội ngũ AI" :mo-ta="MO_TA" />
  <p v-if="loi" class="loi" role="alert">{{ loi }}</p>
  <p v-if="dl && !dl.bat" class="cot-rong">Kho phiếu chưa bật trên trạm (phần 3) — chưa có khe, chưa có bảng điểm.</p>
  <template v-if="dl && dl.bat">
    <section class="the bang-diem">
      <div class="dau-khoi">
        <h2>Bảng điểm thợ</h2>
        <span class="nho">lọc áp cho mọi cột</span>
        <div class="loc">
          <select v-model="duAn" aria-label="Dự án"><option value="">Tất cả dự án</option>
            <option v-for="d in dsDuAn" :key="d" :value="d">{{ d }}</option></select>
          <div class="nhom-nut" role="group" aria-label="Khoảng">
            <button v-for="n in SO_NGAY_BANG_DIEM" :key="n" type="button" :class="{ chon: n === soNgay }"
                    :aria-pressed="n === soNgay" @click="soNgay = n">{{ n }} ngày</button>
          </div>
        </div>
      </div>
      <p v-if="!dl.bang_diem.length" class="nho">Không có phiếu nào được cấp trong khoảng này.</p>
      <div v-else class="bang-cuon">
        <table class="bang">
          <thead><tr>
            <th scope="col">Khe</th><th scope="col">Vai</th><th scope="col">Số phiếu</th><th scope="col">Xong</th>
            <th scope="col">Lần chạy TB / phiếu</th><th scope="col">Qua lần đầu</th><th scope="col">Bị trả về</th>
          </tr></thead>
          <tbody><tr v-for="d in dl.bang_diem" :key="d.khe_id + '/' + d.vai">
            <th scope="row" class="mono">{{ d.khe_id }}</th><td>{{ d.vai }}</td>
            <td class="so">{{ d.so_phieu }}</td><td class="so">{{ d.so_xong }}</td>
            <td class="so">{{ d.lan_chay_tb == null ? '—' : dinhDangSo(d.lan_chay_tb) }}</td>
            <td v-for="(o, i) in [oTiLe(d.qua_lan_dau, d.qua_lan_dau_mau), oTiLe(d.bi_tra_ve, d.bi_tra_ve_mau)]"
                :key="i">{{ o.chinh }} <span v-if="o.phu" class="nho">{{ o.phu }}</span></td>
          </tr></tbody>
        </table>
      </div>
      <p class="nho chu-thich">Qua lần đầu: phiếu code xong mà lần kiểm lại / QC đầu tiên qua. Bị trả về: bead vào
        cột 3 rồi bị Đại ca Trả về. Chỉ tính vai coder; vai khác “—”.</p>
    </section>
    <h2 class="muc">Khe <span class="so">{{ dl.khe.length }}</span></h2>
    <p v-if="!dl.khe.length" class="cot-rong">Chưa có khe nào đăng ký với trạm.</p>
    <div v-else class="luoi-khe">
      <TheKhe v-for="k in dl.khe" :key="k.khe_id" :khe="k" :la-dai-ca="laDaiCa" @doi="tai" />
    </div>
  </template>
  <template v-if="dl && dl.luat_vai">
    <h2 class="muc">Luật vai ↔ khe</h2>
    <div class="the nho luat-vai">Bước → vai:
      <span v-for="(vai, buoc) in dl.luat_vai.vai_cua_buoc" :key="buoc" class="chip mono">{{ buoc }} → {{ vai }}</span>
      <ul v-if="dl.luat_vai.luat && dl.luat_vai.luat.length">
        <li v-for="l in dl.luat_vai.luat" :key="l">{{ l }}</li></ul>
    </div>
  </template>
</template>
