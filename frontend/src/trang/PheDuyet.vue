<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { doc } from '../api.js'
import { duocGhi } from '../quyen_passkey.js'
import { kho, taiSoPheDuyet } from '../kho.js'
import { TEN_PHE_DUYET, duAnChiQuetThu, nhomPheDuyet } from '../luat.js'
import { khoaMuc } from '../luat_doi_ngu.js'
import { khoaThaoTac } from '../luat_phe_duyet.js'
import DauTrang from '../thanh/DauTrang.vue'
import TheBi from '../thanh/phe_duyet/TheBi.vue'
import TheFeatureXong from '../thanh/phe_duyet/TheFeatureXong.vue'
import TheHe from '../thanh/phe_duyet/TheHe.vue'
import TheReview from '../thanh/phe_duyet/TheReview.vue'
import TheSanSang from '../thanh/phe_duyet/TheSanSang.vue'
import TheSpec from '../thanh/phe_duyet/TheSpec.vue'
import '../kieu/phe-duyet.css'

// Trang Phê duyệt (mockup trang.js vePheDuyet, anh-phe-duyet.png): nhóm theo độ gấp, mỗi mục một thẻ `.the-duyet`.
const THE = { he: TheHe, escalation: TheBi, decision: TheBi, 'cho-review': TheReview, 'co-do': TheReview,
  spec: TheSpec, 'feature-xong': TheFeatureXong, 'san-sang-deploy': TheSanSang }      // TM-4: D101
const MO_TA = 'Việc chờ Đại ca, sắp theo độ gấp. Duyệt / Trả về ghi thẳng vào beads với tác nhân dai-ca/dashboard.'
const ds = ref([])
const loi = ref('')
const loiDoc = ref({})
const chiQuetThu = ref(new Set())          // dự án `bat_ghi: false` (D37)
const nhom = computed(() => nhomPheDuyet(ds.value))
const laDaiCa = computed(() => duocGhi(kho.trangThai))
const khoaCua = (m) => khoaThaoTac(laDaiCa.value, chiQuetThu.value.has(m.du_an))

async function tai() {
  try {
    // /api/du-an lỗi → không biết dự án nào chỉ quét thử; server vẫn từ chối ghi (422) nên coi như không khoá thêm.
    const [r, da] = await Promise.all([doc('/api/phe-duyet'), doc('/api/du-an').catch(() => ({ du_an: [] }))])
    ds.value = r.muc
    loiDoc.value = r.loi || {}
    chiQuetThu.value = duAnChiQuetThu(da.du_an)
    loi.value = ''
  } catch (e) {
    loi.value = e.message
  }
}
async function doi() {
  await tai()
  await taiSoPheDuyet()
}
onMounted(tai)
watch(() => kho.phienBan, tai)
</script>

<template>
  <section class="phe-duyet">
    <DauTrang tieu-de="Phê duyệt" :mo-ta="MO_TA" />
    <p v-if="loi" class="loi" role="alert">{{ loi }}</p>
    <p v-for="(l, t) in loiDoc" :key="t" class="loi">{{ t }}: {{ l }}</p>
    <p v-if="!nhom.length && !loi" class="nho">Không có việc nào chờ Đại ca.</p>
    <template v-for="[loai, muc] in nhom" :key="loai">
      <h2 class="muc">{{ TEN_PHE_DUYET[loai] }} <span class="so">{{ muc.length }}</span></h2>
      <div class="ds-duyet">
        <component :is="THE[loai]" v-for="m in muc" :key="khoaMuc(m)" :muc="m" :khoa="khoaCua(m).khoa"
                   :chu-khoa="khoaCua(m).chu" @doi="doi" />
      </div>
    </template>
  </section>
</template>
