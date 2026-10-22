<script setup>
import { computed } from 'vue'
import { gioPhut } from '../dinh_dang.js'
import { duocGhi } from '../quyen_passkey.js'
import { kho } from '../kho.js'
import BieuTuong from './BieuTuong.vue'
import ChipPasskey from './ChipPasskey.vue'
import OTim from './OTim.vue'

// Thanh trên (mockup index.html `.thanh-tren`): ô tìm ⌘K, viên đồng bộ (quét cuối mới nhất của mọi dự án; mất luồng
// SSE thì báo "Mất kết nối"), nút TẠM DỪNG toàn trạm màu vàng (TM-4, D101), nút Estop. Chỉ Đại ca bấm được.
const props = defineProps({ estop: { type: Object, required: true }, tamDung: { type: Object, required: true },
  nutTamDung: { type: Object, required: true } })
const tt = computed(() => kho.trangThai)
const quetCuoi = computed(() => {
  const ds = (tt.value ? tt.value.du_an : []).map((d) => d.quet_cuoi).filter(Boolean).sort()
  return ds.length ? gioPhut(ds[ds.length - 1]) : 'chưa quét'
})
const khoa = computed(() => !tt.value || !tt.value.la_dai_ca || (tt.value.estop && !duocGhi(tt.value)) || props.estop.dangGui.value)
</script>

<template>
  <header class="thanh-tren">
    <OTim />
    <div class="tt-phai">
      <ChipPasskey v-if="tt?.la_dai_ca" />
      <span class="vien-tt mono" role="status">
        <span class="cham" :class="kho.matKetNoi ? 'do' : 'xanh'" />
        {{ kho.matKetNoi ? 'Mất kết nối · đang thử lại' : `Đồng bộ · quét cuối ${quetCuoi}` }}</span>
      <button type="button" class="nut-estop vang" :class="{ bat: nutTamDung.bat }" :title="nutTamDung.title"
              :disabled="nutTamDung.khoa || tamDung.dangGui.value" @click="tamDung.bam(!nutTamDung.bat)">
        <BieuTuong ten="tam-dung" class="dac" /><span>{{ nutTamDung.chu }}</span>
      </button>
      <button type="button" class="nut-estop" :class="{ bat: tt && tt.estop }" :disabled="khoa"
              :title="tt && !tt.la_dai_ca ? 'Chỉ đọc: thiếu danh tính Đại ca' : 'Dừng khẩn: trạm ngừng giao việc mới'"
              @click="estop.bam(!(tt && tt.estop))">
        <BieuTuong ten="estop" /><span>{{ tt && tt.estop ? 'Estop đang bật' : 'Estop' }}</span>
      </button>
    </div>
  </header>
</template>
