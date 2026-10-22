<script setup>
import { computed } from 'vue'
import { LENH_SAN_SANG, demSanSang, maSanSang, nhanSanSang } from '../../luat_cai_dat.js'
import KhoiCaiDat from './KhoiCaiDat.vue'

// Bảng sẵn sàng chạy thật (mockup trang-cai-dat.js `bangSanSang`, ảnh anh-cai-dat.png). Dữ liệu GET /api/san-sang.
// Hai lệnh "Kiểm lại" chỉ hiện để Đại ca tự chạy — API không bao giờ chạy chúng.
const props = defineProps({ ss: { type: Object, required: true } })
const dem = computed(() => demSanSang(props.ss))
</script>

<template>
  <KhoiCaiDat tieu-de="Bảng sẵn sàng chạy thật" :lenh="LENH_SAN_SANG" nhan-lenh="Kiểm lại:">
    <template #phu>theo sổ tay <span class="mono">docs/handovers/2026-10-15-so-tay-chay-that.md</span></template>
    <template #dau>
      <div class="tq-chip cd-dem">
        <span class="chip tt-lam">{{ dem.dat }} đạt</span>
        <span class="chip tt-can_nguoi">{{ dem.thieu }} thiếu</span>
        <span class="chip tt-tat">{{ dem.cho }} chưa tới lượt</span>
      </div>
    </template>
    <p v-if="ss.loi" class="canh-bao">{{ ss.loi }}</p>
    <div class="bang-cuon">
      <table class="bang">
        <thead><tr><th class="cot-den" /><th>Bead</th><th>Bước</th><th>Trạng thái</th><th>Ghi chú</th></tr></thead>
        <tbody>
          <tr v-for="(m, i) in ss.muc || []" :key="m.ma + i">
            <td><span class="den-ss" :class="m.trang_thai" /></td>
            <td class="mono ma-ss">{{ maSanSang(m) }}</td>
            <td>{{ m.ten }}</td>
            <td>
              <span class="chip" :class="nhanSanSang(m.trang_thai).lop">{{ nhanSanSang(m.trang_thai).chu }}</span>
            </td>
            <td class="nho">{{ m.ghi_chu }}</td>
          </tr>
          <tr v-if="!(ss.muc || []).length"><td colspan="5" class="nho">Chưa có mục nào.</td></tr>
        </tbody>
      </table>
    </div>
  </KhoiCaiDat>
</template>
