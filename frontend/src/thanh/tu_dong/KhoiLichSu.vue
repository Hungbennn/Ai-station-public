<script setup>
import { computed } from 'vue'
import { dongLichSu } from '../../luat_lich_su_tu_dong.js'
import { CHUA_CO } from '../../luat_trang_tu_dong.js'

// Khối "Lịch sử gần đây" (mockup veLichSu): tự merge, sẵn sàng, deploy, lùi — chỉ mã thoát và thời gian, không log
// (spec tu-deploy "Không lọt bí mật qua kết quả deploy"). Dữ liệu TM-2/TM-3 dựng trong `lich_su`.
const props = defineProps({ dl: { type: Object, required: true } })
const ds = computed(() => (Array.isArray(props.dl.lich_su) ? props.dl.lich_su.map(dongLichSu) : null))
</script>

<template>
  <section class="the">
    <h3 class="td-h">Lịch sử gần đây
      <span class="nho">tự merge, deploy, lùi — chỉ mã thoát và thời gian, không có log</span></h3>
    <div v-if="!ds" class="ss-rong">{{ CHUA_CO }}</div>
    <div v-else-if="ds.length" class="bang-cuon">
      <table class="bang bang-ls">
        <thead><tr><th>Giờ</th><th>Việc</th><th>Bead</th><th>Commit</th><th>Chi tiết</th><th>Ai</th></tr></thead>
        <tbody>
          <tr v-for="(r, i) in ds" :key="i">
            <td class="mono">{{ r.gio }}</td><td><span class="chip" :class="r.lop">{{ r.nhan }}</span></td>
            <td class="mono ma">{{ r.bead }}</td><td class="mono">{{ r.commit }}</td>
            <td class="nho">{{ r.chiTiet }}</td><td class="nho">{{ r.ai }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-else class="ss-rong">Chưa có lần tự merge hay deploy nào.</div>
  </section>
</template>
