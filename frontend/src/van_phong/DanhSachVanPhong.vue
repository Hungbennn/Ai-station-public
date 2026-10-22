<script setup>
import { computed } from 'vue'
import { mauTuMay } from './bo_tri.js'
import { chuNhip } from './hien_thi.js'
import { lopNhanVat, nhanPhu, trangThaiDen } from './nhan_canh.js'

// Bản danh sách (mockup trang-van-phong.js "ds-phong"): thẻ phòng viền trái màu tường, chip trạng thái, chip nhân
// vật. Đường dùng bàn phím / trình đọc màn hình và chỗ xem khi không có WebGL (plan 2c G16). Bấm thẻ → emit('chon').
const props = defineProps({ boTri: { type: Object, required: true } })
const emit = defineEmits(['chon'])
const LOAI = { du_an: 'Dự án', giam_doc: 'Cố định', may_chu: 'Máy B', ca_phe: 'Khe rảnh', dieu_phoi: 'Máy A' }
const CHIP_TU = { xanh: ['tt-lam', 'xanh'], vang: ['tt-cau_dao', 'vàng'], do: ['tt-loi', 'đỏ'] }

const theoPhong = computed(() => {
  const m = {}
  for (const nv of props.boTri.nhanVat) (m[nv.phongMa] ??= []).push(nv)
  return m
})

// Chip trạng thái riêng của phòng: việc chờ / đèn Điều phối + nhịp cuối / số tủ theo màu / chỉ quét thử (D37).
function chipPhong(p) {
  if (p.loai === 'giam_doc') return [{ lop: 'tt-can_nguoi', chu: `${p.so_cho ?? 0} việc chờ` }]
  if (p.loai === 'dieu_phoi') {
    return [{ lop: '', chu: `đèn: ${trangThaiDen(p)}` }, ...(chuNhip(p) ? [{ lop: '', chu: chuNhip(p) }] : [])]
  }
  if (p.loai === 'may_chu') {
    const dem = {}
    for (const m of mauTuMay(p)) dem[m] = (dem[m] ?? 0) + 1
    const co = Object.keys(CHIP_TU).filter((k) => dem[k])
    return co.map((k) => ({ lop: CHIP_TU[k][0], chu: `${dem[k]} ${CHIP_TU[k][1]}` }))
  }
  return p.mo ? [{ lop: '', chu: 'chỉ quét thử' }] : []
}
</script>

<template>
  <div class="ds-phong">
    <button v-for="p in boTri.phong" :key="p.ma" type="button" class="the the-phong" :class="{ mo: p.mo }"
            :style="{ borderLeftColor: p.tuong }" @click="emit('chon', { loai: 'phong', ma: p.ma })">
      <span class="dau">
        <span class="cham" :style="{ background: p.san, boxShadow: `inset 0 0 0 1px ${p.tuong}` }" />
        <strong>{{ p.tenBien }}</strong><span class="nho">{{ LOAI[p.loai] }}</span>
      </span>
      <span class="ds-nv">
        <span v-for="(c, i) in chipPhong(p)" :key="i" class="chip" :class="c.lop">{{ c.chu }}</span>
        <span v-for="nv in theoPhong[p.ma] ?? []" :key="nv.khe_id"
              :class="['chip', lopNhanVat(nv)]">{{ nv.ten }} · {{ nhanPhu(nv) }}</span>
        <span v-if="!chipPhong(p).length && !theoPhong[p.ma]" class="nho">Không có ai</span>
      </span>
    </button>
  </div>
</template>
