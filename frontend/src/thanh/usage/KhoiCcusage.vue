<script setup>
import { computed } from 'vue'
import '../../kieu/usage.css'
import { dongCcusage } from '../../luat_usage.js'
import BangUsage from '../BangUsage.vue'

// Khối ccusage (mockup trang-usage.js khoiCcusage): chua_cau_hinh / loi / bảng theo ngày (không cột lần gọi).
// Bỏ nhóm nút "minh hoạ" trạng thái của mockup — trạng thái thật lấy từ /api/usage `ccusage.trang_thai` (D39).
const props = defineProps({ ccusage: { type: Object, required: true } })  // {trang_thai, theo_ngay, loi, phien_ban}
const dong = computed(() => dongCcusage(props.ccusage))
</script>

<template>
  <section class="the us-khoi">
    <h3 class="tq-h">ccusage — toàn bộ Claude Code của tài khoản trạm trên máy B</h3>
    <p v-if="ccusage.trang_thai === 'chua_cau_hinh'" class="nho">Chưa cấu hình ccusage
      (<span class="mono">usage.ccusage</span> trong <span class="mono">~/.tram/cau-hinh.yaml</span>).</p>
    <div v-else-if="ccusage.trang_thai === 'loi'" class="canh-bao" role="alert">{{ ccusage.loi || 'ccusage lỗi' }}</div>
    <template v-else>
      <p class="nho">ccusage {{ ccusage.phien_ban }} — số liệu giữ tối đa 10 phút. Gồm cả phiên Claude Code không do
        khe chạy, nên lớn hơn dòng khe ở trên.</p>
      <BangUsage ten-khoa="Ngày" :dong="dong" :co-so-lan="false" cuon />
    </template>
  </section>
</template>
