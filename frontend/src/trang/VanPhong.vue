<script setup>
import { TresCanvas } from '@tresjs/core'
import { NoToneMapping, PCFShadowMap, SRGBColorSpace } from 'three'
import { computed, onMounted, onUnmounted, ref, shallowRef, watch } from 'vue'
import { doc } from '../api.js'
import { kho } from '../kho.js'
import '../kieu/van-phong.css'
import DauTrang from '../thanh/DauTrang.vue'
import { boTriVanPhong } from '../van_phong/bo_tri.js'
import CanhVanPhong from '../van_phong/CanhVanPhong.vue'
import DanhSachVanPhong from '../van_phong/DanhSachVanPhong.vue'
import LopNhan from '../van_phong/LopNhan.vue'
import { dungNhan, timMucChon } from '../van_phong/nhan_canh.js'
import PanelChon from '../van_phong/PanelChon.vue'

// Văn phòng 3D (mockup trang-van-phong.js, D20). Trạng thái suy ở server (`/api/van-phong`); trang chỉ vẽ.
// `/api/du-an` cho `bat_ghi` (D37). Nhịp tim không phải sự kiện → tải lại mỗi 5 giây (plan 2b G15) + SSE.
const CHU_KY_MS = 5000
const KHOA_GIAM = 'ben-station-giam-chuyen-dong'
const MO_TA = 'Ai đang làm gì, nhìn cho vui mắt. Vị trí lấy từ trạng thái nhiệm vụ thật; bấm vào nhân vật để mở việc.'
const dl = ref(null)
const duAn = ref([])
const loi = ref('')
const boTri = shallowRef(null)
const chieu = shallowRef(null)
const chon = ref(null)
const khung = ref(null)
const giam = ref(docGiam())
const coWebGL = (() => {
  try { return Boolean(document.createElement('canvas').getContext('webgl2')) } catch { return false }
})()                                                         // three bản ghim yêu cầu WebGL2
const nhan = computed(() => (boTri.value ? dungNhan(boTri.value) : []))

// "Giảm chuyển động": mặc định theo prefers-reduced-motion, nhớ lựa chọn trong localStorage (tiện ích riêng máy).
function docGiam() {
  try {
    const v = localStorage.getItem(KHOA_GIAM)
    if (v !== null) return v === '1'
  } catch { /* bỏ qua: chế độ riêng tư / bị chặn */ }
  return Boolean(window.matchMedia?.('(prefers-reduced-motion: reduce)').matches)
}
watch(giam, (b) => {
  try { localStorage.setItem(KHOA_GIAM, b ? '1' : '0') } catch { /* bỏ qua */ }
})

// Chỉ thay mặt bằng khi nội dung đổi → cảnh 3D không dựng lại mỗi 5 giây.
let khoaCu = ''
watch([dl, duAn], () => {
  if (!dl.value) return
  const b = boTriVanPhong(dl.value.phong, dl.value.nhan_vat, duAn.value)
  const k = JSON.stringify(b)
  if (k !== khoaCu) {
    khoaCu = k
    boTri.value = b
  }
})

// Panel lấy bản mới nhất của phòng / nhân vật đang chọn (D38/Q8: bấm mở panel trước).
const panel = computed(() => timMucChon(boTri.value, chon.value))
function chonTuDanhSach(c) {
  chon.value = c
  khung.value?.scrollIntoView({ behavior: giam.value ? 'auto' : 'smooth', block: 'center' })
}

let hen = null
let luotTai = 0
let luotDuAn = 0
async function tai() {
  const luot = ++luotTai
  try {
    const moi = await doc('/api/van-phong')
    if (luot !== luotTai) return
    dl.value = moi
    loi.value = ''
  } catch (e) {
    if (luot === luotTai) loi.value = e.message
  }
}
async function taiDuAn() {
  const luot = ++luotDuAn
  try {
    const r = await doc('/api/du-an')
    if (luot === luotDuAn) duAn.value = r.du_an || []
  } catch { /* không đọc được → coi mọi dự án bat_ghi = true */ }
}
onMounted(() => { tai(); taiDuAn(); hen = setInterval(tai, CHU_KY_MS) })
onUnmounted(() => { clearInterval(hen); luotTai += 1; luotDuAn += 1 })
watch(() => [kho.phienBan, kho.phienBanDoiNgu], tai)
watch(() => kho.phienBan, taiDuAn)
</script>

<template>
  <DauTrang tieu-de="Văn phòng" :mo-ta="MO_TA">
    <template #cong-cu>
      <label class="gc"><input v-model="giam" type="checkbox"> Giảm chuyển động</label>
    </template>
  </DauTrang>
  <p v-if="loi" class="loi" role="alert">{{ loi }}</p>
  <p v-if="dl && !dl.kho_phieu" class="nho">Kho phiếu (phần 3) chưa bật — chưa có nhân vật.</p>
  <div v-if="boTri" ref="khung" class="canh-khung">
    <TresCanvas v-if="coWebGL" :key="giam ? 'tinh' : 'dong'" aria-hidden="true" :alpha="true" :clear-alpha="0"
                :tone-mapping="NoToneMapping" :shadows="true" :shadow-map-type="PCFShadowMap"
                :output-color-space="SRGBColorSpace" :dpr="[1, 2]" :render-mode="giam ? 'on-demand' : 'always'">
      <CanhVanPhong :bo-tri="boTri" :nhan="nhan" :chuyen-dong="!giam" @chon="(c) => (chon = c)"
                    @chieu="(c) => (chieu = c)" />
    </TresCanvas>
    <div v-else class="loi-webgl">Trình duyệt không bật được WebGL — xem bản danh sách bên dưới.</div>
    <LopNhan v-if="coWebGL" :nhan="nhan" :chieu="chieu" @chon="(c) => (chon = c)" />
    <PanelChon v-if="panel" :key="panel.khoa" :nv="panel.nv" :phong="panel.phong" @dong="chon = null" />
  </div>
  <template v-if="boTri">
    <h2 class="muc">Bản danh sách <span class="so">{{ boTri.phong.length }} phòng</span></h2>
    <DanhSachVanPhong :bo-tri="boTri" @chon="chonTuDanhSach" />
  </template>
</template>
