<script setup>
// Trang Công việc (mockup trang.js veCongViec, anh-cong-viec.png). Phần mockup không vẽ (hàng Chưa chấm / theo plan /
// Epic, kéo thẻ + hộp Vì sao?, lỗi từng dự án) giữ bố cục cũ, chỉ áp lớp mới (D36).
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { doc, ghi, thanGhi } from '../api.js'
import { ganGiaoViec } from '../giao_viec.js'
import { duocGhi } from '../quyen_passkey.js'
import { kho } from '../kho.js'
import { TEN_HANG, choPhepKeo, duAnChiQuetThu, nhomTheoHang } from '../luat.js'
import { COT, MO_TA_TRANG, dongKhe } from '../luat_cong_viec.js'
import DauTrang from '../thanh/DauTrang.vue'
import HopViSao from '../thanh/HopViSao.vue'
import TheBead from '../thanh/TheBead.vue'
import NganBen from './NganBen.vue'
import '../kieu/cong-viec.css'

const route = useRoute()
const tuDiaChi = (x) => (typeof x === 'string' ? x : '')
const duAn = ref(tuDiaChi(route.query.du_an))       // lát 2c: /cong-viec?du_an=<dự án>[&bead=<id>] từ Văn phòng
const dsDuAn = ref([])
const dsThe = ref([])
const dsKhe = ref([])
const loiDoc = ref({})
const thongBao = ref('')
const dangKeo = ref(null)
const keoCho = ref(null)
const chon = ref(null)
const nhom = computed(() => nhomTheoHang(dsThe.value))
const chiQuetThu = computed(() => duAnChiQuetThu(dsDuAn.value))     // D37: bat_ghi false → chỉ quét thử
const laDaiCa = computed(() => duocGhi(kho.trangThai))
const rong = computed(() => `Không có bead${duAn.value ? ` của ${duAn.value}` : ''}`)
const tenChon = (d) => `${d.ten}${d.bat_ghi === false ? ' (chỉ quét thử)' : ''}`
const thuocTinh = (t) => ({ the: t, khe: dongKhe(t, dsKhe.value), chiQuetThu: chiQuetThu.value.has(t.du_an) })

async function tai() {
  try {
    const q = encodeURIComponent(duAn.value)
    const [r, g] = await Promise.all([doc(`/api/cong-viec?du_an=${q}`),
      doc(`/api/giao-viec?du_an=${q}`).catch(() => ({ giao: {} }))])     // bộ giao việc là phần thêm, lỗi thì bỏ qua
    dsThe.value = ganGiaoViec(r.the, g.giao)
    loiDoc.value = r.loi
    if (chon.value) chon.value = dsThe.value.find((t) => t.du_an === chon.value.du_an && t.id === chon.value.id) ?? null
  } catch (e) {
    thongBao.value = e.message
  }
}
// Dòng khe đang giữ trên thẻ: ghép với /api/doi-ngu phía trình duyệt (khảo sát T7); lỗi thì bỏ dòng khe, không báo.
async function taiKhe() {
  dsKhe.value = await doc('/api/doi-ngu').then((r) => r.khe || [], () => [])
}
onMounted(async () => {
  taiKhe()
  try {
    dsDuAn.value = (await doc('/api/du-an')).du_an
  } catch (e) {
    thongBao.value = e.message
  }
  await tai()
  moTheoDiaChi()
})
watch([duAn, () => kho.phienBan], tai)
watch(() => kho.phienBanDoiNgu, taiKhe)
watch(() => route.fullPath, async () => { duAn.value = tuDiaChi(route.query.du_an); await tai(); moTheoDiaChi() })

// Mở ngăn bên đúng một lần mỗi lần địa chỉ đổi (Đại ca đóng ngăn thì lượt tải lại sau không mở lại).
function moTheoDiaChi() {
  const id = tuDiaChi(route.query.bead)
  if (!id || !duAn.value) return
  chon.value = dsThe.value.find((t) => t.du_an === duAn.value && t.id === id) ?? { du_an: duAn.value, id }
}

function tha(hang) {
  const t = dangKeo.value
  if (laDaiCa.value && choPhepKeo(t, hang) && !chiQuetThu.value.has(t.du_an)) keoCho.value = { the: t, cot: hang }
  dangKeo.value = null
}
async function xacNhanKeo(viSao) {
  if (!keoCho.value || !laDaiCa.value || chiQuetThu.value.has(keoCho.value.the.du_an)) {
    keoCho.value = null
    return
  }
  const { the, cot } = keoCho.value
  keoCho.value = null
  try {
    await ghi(`/api/bead/${encodeURIComponent(the.du_an)}/${encodeURIComponent(the.id)}/cot`,
      thanGhi({ cot, vi_sao: viSao || null }, the.updated_at))
    thongBao.value = ''
  } catch (e) {
    thongBao.value = e.status === 409 ? 'Bead đã đổi trên beads — đã tải lại, Đại ca kéo lại nếu vẫn muốn.' : e.message
  }
  await tai()
}
</script>

<template>
  <DauTrang tieu-de="Công việc" :mo-ta="MO_TA_TRANG">
    <template #cong-cu>
      <select v-model="duAn" aria-label="Dự án"><option value="">Tất cả dự án</option>
        <option v-for="d in dsDuAn" :key="d.ten" :value="d.ten">{{ tenChon(d) }}</option></select>
    </template>
  </DauTrang>
  <p v-for="(l, t) in loiDoc" :key="t" class="loi">{{ t }}: {{ l }}</p>
  <p v-if="thongBao" class="loi" role="alert">{{ thongBao }}</p>
  <section v-if="nhom['chua-cham'].length" class="hang-phu" :aria-label="TEN_HANG['chua-cham']">
    <h2 class="muc">{{ TEN_HANG['chua-cham'] }} <span class="so">{{ nhom['chua-cham'].length }}</span></h2>
    <div class="day-the"><TheBead v-for="t in nhom['chua-cham']" :key="t.du_an + '/' + t.id" v-bind="thuocTinh(t)"
                                  @mo="chon = t" /></div>
  </section>
  <div class="bang-cot">
    <section v-for="c in COT" :key="c.hang" class="cot" :aria-label="c.ten" @dragover.prevent
             @drop.prevent="tha(c.hang)">
      <div class="cot-dau"><span class="so-thu">{{ c.so }}</span><h3>{{ c.ten }}</h3>
        <span class="so">{{ nhom[c.hang].length }}</span></div>
      <p class="nho mo-ta-cot">{{ c.moTa }}</p>
      <TheBead v-for="t in nhom[c.hang]" :key="t.du_an + '/' + t.id" v-bind="thuocTinh(t)" @mo="chon = t"
               @keo="dangKeo = t" />
      <div v-if="!nhom[c.hang].length" class="cot-rong">{{ rong }}</div>
    </section>
  </div>
  <section v-for="h in ['theo-plan', 'epic']" v-show="nhom[h].length" :key="h" class="hang-phu"
           :aria-label="TEN_HANG[h]">
    <h2 class="muc">{{ TEN_HANG[h] }} <span class="so">{{ nhom[h].length }}</span></h2>
    <div class="day-the"><TheBead v-for="t in nhom[h]" :key="t.du_an + '/' + t.id" v-bind="thuocTinh(t)"
                                  @mo="chon = t" /></div>
  </section>
  <NganBen v-if="chon" :the="chon" :chi-quet-thu="chiQuetThu.has(chon.du_an)" @dong="chon = null"
           @chuyen="(cot) => (keoCho = { the: chon, cot })" @doi="tai" />
  <HopViSao v-if="keoCho && laDaiCa && !chiQuetThu.has(keoCho.the.du_an)" :the="keoCho.the" :cot="keoCho.cot" @huy="keoCho = null" @xac-nhan="xacNhanKeo" />
</template>
