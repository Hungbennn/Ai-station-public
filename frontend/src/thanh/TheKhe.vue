<script setup>
import { computed, ref } from 'vue'
import '../kieu/doi-ngu.css'
import { ghi, thanGhi } from '../api.js'
import { cuaSo, tenKhe } from '../luat_han_muc.js'
import { CANH_BAO_HAN_MUC, nhanTrangThai, nutKhe } from '../luat_doi_ngu.js'
import { chuNhipTim, chuPhien, lopTrangThai, oViec } from '../luat_the_khe.js'
import Chibi from './Chibi.vue'
import HopKhe from './HopKhe.vue'
import ThanhHanMuc from './ThanhHanMuc.vue'

// Thẻ khe theo mockup trang.js theKhe (D20). Thêm cảnh báo hạn mức mockup chưa vẽ (D36); phiên không có mẫu số (Q11).
const props = defineProps({ khe: { type: Object, required: true }, laDaiCa: { type: Boolean, default: false } })
const emit = defineEmits(['doi'])
const hop = ref('')
const dangGui = ref(false)
const loi = ref('')
const duong = () => `/api/khe/${props.khe.khe_id.split('/').map(encodeURIComponent).join('/')}`
const mo = computed(() => props.khe.trang_thai === 'tat' || props.khe.trang_thai === 'mat_ket_noi')
// Thẻ vẽ lại mỗi lần trang tải lại (5 giây) → "còn x giờ", "x giây trước" tự cập nhật theo khe mới.
const viec = computed(() => oViec(props.khe))
const nut = computed(() => nutKhe(props.khe))
const canhBao = computed(() => CANH_BAO_HAN_MUC[props.khe.muc_han_muc])

async function lam(hanhDong, noiDung = {}) {
  dangGui.value = true
  loi.value = ''
  try {
    await ghi(`${duong()}/${hanhDong}`, thanGhi(noiDung, props.khe.phien_ban))
    hop.value = ''
    emit('doi')
  } catch (e) {
    loi.value = e.status === 409 ? 'Khe đã đổi — đã tải lại.' : e.message
    if (e.status === 409) emit('doi')
  } finally {
    dangGui.value = false
  }
}
function dongCauDao() {
  if (window.confirm(`Đóng cầu dao khe ${props.khe.khe_id}? Khe nhận việc lại ngay dù chưa tới giờ reset.`)) {
    lam('cau-dao-dong')
  }
}
</script>

<template>
  <article class="the the-khe" :class="{ mo }">
    <div class="dau">
      <Chibi :khe-id="khe.khe_id" :mo="mo" />
      <div>
        <strong>{{ tenKhe(khe) }}</strong>
        <span class="nho">{{ khe.khe_id.split('/').pop() }} · máy {{ khe.may }} · {{ khe.ten_goi_nho }}</span>
      </div>
      <span class="chip" :class="lopTrangThai(khe)"><span class="cham" />{{ nhanTrangThai(khe) }}</span>
    </div>
    <div v-if="viec.loai === 'phieu'" class="viec"><span class="mono">{{ viec.ma }}</span>{{ viec.chu }}</div>
    <div v-else class="viec" :class="{ nho: viec.loai === 'trong', cau_dao: viec.loai === 'cau_dao' }">
      {{ viec.chu }}</div>
    <div class="han-muc">
      <ThanhHanMuc ten="5 giờ" :cua-so="cuaSo(khe, '5h')" />
      <ThanhHanMuc ten="Tuần" :cua-so="cuaSo(khe, 'tuan')" />
    </div>
    <p v-if="canhBao" :class="canhBao[0]">{{ canhBao[1] }}</p>
    <div class="nho vai-phien">
      <span>Vai: {{ khe.vai_uu_tien.join(', ') || '—' }}</span><span>{{ chuPhien(khe.so_phien) }}</span>
    </div>
    <div class="chan">
      <span class="nho">♥ nhịp tim cuối: {{ chuNhipTim(khe.nhip_cuoi) }}</span>
      <button v-if="nut.dongCauDao" class="nut chinh" type="button" :disabled="dangGui || !laDaiCa"
              @click="dongCauDao">Đóng cầu dao</button>
      <button v-if="nut.bat" class="nut chinh" type="button" :disabled="dangGui || !laDaiCa"
              @click="hop = 'bat'">Bật khe</button>
      <button v-if="nut.tat" class="nut nguy" type="button" :disabled="dangGui || !laDaiCa"
              @click="hop = 'tat'">Tắt khe</button>
    </div>
    <p v-if="loi" class="loi" role="alert">{{ loi }}</p>
    <HopKhe v-if="hop" :khe="khe" :bat="hop === 'bat'" @huy="hop = ''" @xac-nhan="(vs) => lam(hop, { vi_sao: vs })" />
  </article>
</template>
