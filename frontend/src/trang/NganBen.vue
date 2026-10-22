<script setup>
// Ngăn bên chi tiết bead (mockup trang.js moBead, anh-cong-viec-ngan-ben.png). Nút chuyển cột, trả lời decision,
// Bàn giao, Bộ giao việc giữ bố cục cũ, chỉ áp lớp mới (D36). Dự án chỉ quét thử: khoá nút ghi (D37).
import { computed, ref, watch } from 'vue'
import { doc, ghi, thanGhi } from '../api.js'
import { duocGhi } from '../quyen_passkey.js'
import { kho } from '../kho.js'
import { CHU_CHI_QUET_THU, gioVN, laLinkAnToan } from '../luat.js'
import { chipCot, uuTien, viTriThe } from '../luat_cong_viec.js'
import DongThoiGian from '../thanh/DongThoiGian.vue'
import OGiaoViec from '../thanh/OGiaoViec.vue'
import OChot from '../thanh/OChot.vue'
import OTraLoi from '../thanh/OTraLoi.vue'

const props = defineProps({ the: { type: Object, required: true }, chiQuetThu: { type: Boolean, default: false } })
const emit = defineEmits(['dong', 'chuyen', 'doi'])
const ct = ref(null)
const loi = ref('')
const duongDan = () => `${encodeURIComponent(props.the.du_an)}/${encodeURIComponent(props.the.id)}`
const laDaiCa = computed(() => duocGhi(kho.trangThai))
const cauHoi = computed(() => (ct.value && ct.value.cham_gan_nhat ? ct.value.cham_gan_nhat.cau_hoi : []))

async function tai() {
  try {
    ct.value = await doc(`/api/bead/${duongDan()}`)
    loi.value = ''
  } catch (e) {
    loi.value = e.message
  }
}
watch(() => [props.the.du_an, props.the.id, props.the.updated_at], tai, { immediate: true })
watch(() => kho.suKienCuoi, (sk) => {
  if (sk && sk.du_an === props.the.du_an && sk.bead_id === props.the.id) tai()
})

async function gui(duong, noiDung) {
  if (!laDaiCa.value || props.chiQuetThu) return false
  try {
    await ghi(duong, thanGhi(noiDung, ct.value.the.updated_at))
    loi.value = ''
    emit('doi')
    return true
  } catch (e) {
    loi.value = e.status === 409 ? 'Bead đã đổi — đã tải lại, Đại ca xem lại.' : e.message
    await tai()
    return false
  }
}
async function chot(noiDung) {
  if (!(await gui(`/api/bead/${duongDan()}/chot`, noiDung))) throw new Error(loi.value)
}
const traLoi = (vb) => gui(`/api/phe-duyet/${duongDan()}/tra-loi`, { tra_loi: vb })
</script>

<template>
  <aside class="ngan-ben" aria-label="Chi tiết bead">
    <button class="dong" type="button" aria-label="Đóng ngăn chi tiết" @click="emit('dong')">×</button>
    <p v-if="loi" class="loi" role="alert">{{ loi }}</p>
    <template v-if="ct">
      <div class="nho mono">{{ ct.the.du_an }} · {{ ct.the.id }} · {{ viTriThe(ct.the) }}</div>
      <h2>{{ ct.the.tieu_de }}</h2>
      <div class="hang-chip">
        <span v-if="chipCot(ct.the)" class="chip mono">{{ chipCot(ct.the) }}</span>
        <span class="chip">{{ ct.the.loai }}</span><span class="chip">{{ uuTien(ct.the) }}</span>
        <span v-if="chiQuetThu" class="chip tt-tat">chỉ quét thử</span>
      </div>
      <p class="nho">cập nhật {{ gioVN(ct.the.updated_at) }}</p>
      <p v-if="chiQuetThu" class="canh-bao">{{ CHU_CHI_QUET_THU }}</p>
      <div v-if="ct.the.keo_duoc" class="hang-nut">
        <button v-if="ct.the.hang !== 'ai-lam'" class="nut" type="button" :disabled="chiQuetThu || !laDaiCa"
                @click="emit('chuyen', 'ai-lam')">Chuyển sang cột 1</button>
        <button v-if="ct.the.hang !== 'can-chot'" class="nut" type="button" :disabled="chiQuetThu || !laDaiCa"
                @click="emit('chuyen', 'can-chot')">Chuyển sang cột 2</button>
      </div>
      <template v-if="ct.cham_gan_nhat">
        <h4>Lý do lần chấm gần nhất</h4>
        <p class="van-ban">{{ ct.cham_gan_nhat.ly_do }}</p>
        <p class="nho">{{ gioVN(ct.cham_gan_nhat.luc) }}</p>
      </template>
      <template v-if="ct.the.chot_duoc || cauHoi.length">
        <h4>Câu hỏi cần chốt</h4>
        <OChot v-if="ct.the.chot_duoc" :cau-hoi="cauHoi" :gui="chot" :khoa="chiQuetThu || !laDaiCa" />
        <ol v-else><li v-for="(q, i) in cauHoi" :key="i">{{ q }}</li></ol>
      </template>
      <OTraLoi v-if="ct.the.tra_loi_duoc" :gui="traLoi" :khoa="chiQuetThu || !laDaiCa" nhan="Trả lời (đóng decision)" />
      <template v-if="ct.ban_giao">
        <h4>Bàn giao</h4>
        <p class="nho">Nhánh {{ ct.ban_giao.nhanh || '—' }} · commit {{ ct.ban_giao.commit || '—' }}</p>
        <p v-if="laLinkAnToan(ct.ban_giao.pr)">
          <a :href="ct.ban_giao.pr" target="_blank" rel="noopener noreferrer">Mở PR</a></p>
        <ul v-if="ct.ban_giao.loi.length" class="canh-bao"><li v-for="l in ct.ban_giao.loi" :key="l">{{ l }}</li></ul>
      </template>
      <OGiaoViec v-if="the.giao" :giao="the.giao" />
      <h4>Mô tả</h4>
      <p class="van-ban">{{ ct.mo_ta || '(trống)' }}</p>
      <h4>Tiêu chí nghiệm thu</h4>
      <p class="van-ban">{{ ct.nghiem_thu || '(trống)' }}</p>
      <DongThoiGian :ds="ct.dong_thoi_gian" />
    </template>
  </aside>
</template>
