<script setup>
import { computed, onMounted, ref } from 'vue'
import { CHU_CHI_QUET_THU } from '../luat.js'
import { mauTuMay } from './bo_tri.js'
import { chuNhip, duongDanNhanVat, duongDanPhong } from './hien_thi.js'
import { lopNhanVat, nhanPhu, trangThaiDen } from './nhan_canh.js'

// Panel khi bấm nhân vật / phòng (mockup trang-van-phong.js noiDungPanel). D38/Q8: bấm mở panel trước, nút trong
// panel mới dẫn đi (duongDanNhanVat / duongDanPhong). Panel Điều phối không có nút — chỉ trạng thái đèn + nhịp cuối.
const props = defineProps({ nv: { type: Object, default: null }, phong: { type: Object, default: null } })
const emit = defineEmits(['dong'])
const TEN_BUOC = { spec: 'spec', code: 'code', qc: 'QC' }
const NUT = { du_an: 'Lọc Công việc', giam_doc: 'Mở Phê duyệt', may_chu: 'Mở Phê duyệt', ca_phe: 'Mở Đội ngũ AI' }
const TEN_MAU = { xanh: 'xanh', vang: 'vàng', do: 'đỏ' }
const nutDong = ref(null)
onMounted(() => nutDong.value?.focus({ preventScroll: true }))

const p = computed(() => props.phong)
const moTaKhe = computed(() => {
  const nv = props.nv
  if (nv.trang_thai === 'mat_ket_noi') return 'Không thấy nhịp tim từ máy B.'
  if (nv.hien_thi === 'loi') return nv.cau_dao_ngat ? 'Cầu dao ngắt — lý do và giờ tự đóng xem ở Đội ngũ AI.'
    : 'Khe đang báo lỗi.'
  if (nv.hien_thi === 'tat') return 'Khe đang tắt.'
  return nv.hien_thi === 'ranh' ? 'Đang rảnh, chờ việc ở Góc cà phê.' : 'Không giữ việc.'
})
// Phòng máy chủ: đếm tủ theo màu `suc_khoe.muc` (T6), vd "3 tủ xanh, 1 tủ vàng".
const demTu = computed(() => {
  const dem = {}
  for (const m of mauTuMay(p.value)) dem[m] = (dem[m] ?? 0) + 1
  return Object.keys(TEN_MAU).filter((k) => dem[k]).map((k) => `${dem[k]} tủ ${TEN_MAU[k]}`).join(', ')
})
</script>

<template>
  <section class="vp-panel" :aria-label="nv ? nv.ten : phong.tenBien">
    <button ref="nutDong" class="dong" type="button" aria-label="Đóng" @click="emit('dong')">×</button>
    <template v-if="nv">
      <h3>{{ nv.ten }} <span class="chip" :class="lopNhanVat(nv)">{{ nhanPhu(nv) }}</span></h3>
      <template v-if="nv.bead">
        <p>Đang giữ <b class="mono">{{ nv.bead.bead_id }}</b> · {{ nv.bead.tieu_de }} ·
          bước {{ TEN_BUOC[nv.bead.buoc] ?? nv.bead.buoc }}.</p>
        <p class="nho">Mở bead <b>{{ nv.bead.bead_id }}</b> ở ngăn bên trang Công việc
          (lọc dự án {{ nv.bead.du_an }}).</p>
        <div class="hang-nut">
          <router-link class="nut chinh" :to="duongDanNhanVat(nv)">Mở bead {{ nv.bead.bead_id }}</router-link>
        </div>
      </template>
      <template v-else>
        <p>{{ moTaKhe }}</p>
        <p class="nho">Không giữ việc → mở thẻ khe ở trang Đội ngũ AI.</p>
        <div class="hang-nut"><router-link class="nut chinh" :to="duongDanNhanVat(nv)">Mở Đội ngũ AI</router-link></div>
      </template>
    </template>
    <template v-else>
      <h3>{{ p.tenBien }}</h3>
      <p v-if="p.loai === 'du_an'">Lọc trang Công việc theo dự án <b>{{ p.du_an }}</b>.</p>
      <p v-if="p.loai === 'du_an' && p.mo" class="nho">{{ CHU_CHI_QUET_THU }}</p>
      <p v-if="p.loai === 'giam_doc'">{{ p.so_cho ?? 0 }} việc chờ Đại ca — mở trang Phê duyệt.</p>
      <template v-if="p.loai === 'may_chu'">
        <p>Máy B: {{ demTu }}.</p>
        <ul v-if="p.suc_khoe?.ly_do?.length" class="nho">
          <li v-for="(l, i) in p.suc_khoe.ly_do" :key="i">{{ l }}</li>
        </ul>
      </template>
      <p v-if="p.loai === 'ca_phe'">Khe rảnh và khe không giữ việc đứng/ngồi ở đây — mở Đội ngũ AI.</p>
      <template v-if="p.loai === 'dieu_phoi'">
        <p>Đèn Điều phối: {{ trangThaiDen(p) }}<template v-if="p.sang == null"> (máy A chưa có nguồn báo
          phiên)</template>. Không có trang đích.</p>
        <p v-if="chuNhip(p)" class="nho">{{ chuNhip(p) }}</p>
      </template>
      <div v-if="duongDanPhong(p)" class="hang-nut">
        <router-link class="nut chinh" :to="duongDanPhong(p)">{{ NUT[p.loai] }}</router-link>
      </div>
    </template>
  </section>
</template>
