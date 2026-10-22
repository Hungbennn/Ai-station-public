<script setup>
import { LENH_CO, nhanCo } from '../../luat_cai_dat.js'
import KhoiCaiDat from './KhoiCaiDat.vue'

// Cờ (mockup trang-cai-dat.js `co`): khoá mono, ghi chú, chip bật/tắt hoặc giá trị chuỗi; null → "chưa chốt".
defineProps({ ds: { type: Array, required: true } })
</script>

<template>
  <KhoiCaiDat tieu-de="Cờ" :lenh="LENH_CO">
    <ul class="tq-ds">
      <li v-for="c in ds" :key="c.khoa">
        <span class="mono">{{ c.khoa }}</span>
        <span class="nho">{{ c.ghi_chu }}</span>
        <span class="chip" :class="[nhanCo(c).lop, { mono: nhanCo(c).mono }]">{{ nhanCo(c).chu }}</span>
      </li>
    </ul>
  </KhoiCaiDat>
</template>
