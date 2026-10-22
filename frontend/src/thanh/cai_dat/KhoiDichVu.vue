<script setup>
import { LENH_DICH_VU, oDaCai, oDangChay } from '../../luat_cai_dat.js'
import KhoiCaiDat from './KhoiCaiDat.vue'

// Dịch vụ launchd (mockup trang-cai-dat.js `dichVu`). `kiem_duoc: false` → "không rõ", không đoán.
defineProps({ ds: { type: Array, required: true } })
</script>

<template>
  <KhoiCaiDat tieu-de="Dịch vụ launchd" :lenh="LENH_DICH_VU">
    <template #phu>LaunchAgent trong <span class="mono">~/Library/LaunchAgents</span></template>
    <div class="bang-cuon">
      <table class="bang">
        <thead><tr><th>Dịch vụ</th><th>Việc</th><th>Đã cài</th><th>Đang chạy</th></tr></thead>
        <tbody>
          <tr v-for="d in ds" :key="d.nhan">
            <td class="mono">{{ d.nhan }}</td>
            <td class="nho">{{ d.viec }}</td>
            <td><span class="chip" :class="oDaCai(d).lop">{{ oDaCai(d).chu }}</span></td>
            <td><span class="chip" :class="oDangChay(d).lop">{{ oDangChay(d).chu }}</span></td>
          </tr>
        </tbody>
      </table>
    </div>
  </KhoiCaiDat>
</template>
