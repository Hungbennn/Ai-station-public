<script setup>
import LenhCli from '../LenhCli.vue'
import '../../kieu/cai-dat.css'

// Khung một khối Cài đặt (mockup trang-cai-dat.js `khoi`): tiêu đề + phụ + thân + danh sách lệnh CLI gợi ý.
// Slot `phu` thay chữ phụ khi cần đoạn mono; slot `dau` thêm đồ bên phải tiêu đề; slot `sau-lenh` thêm ghi chú.
defineProps({
  tieuDe: { type: String, required: true },
  phu: { type: String, default: '' },
  lenh: { type: Array, default: () => [] },
  nhanLenh: { type: String, default: 'Sửa bằng CLI:' },
})
</script>

<template>
  <section class="the cd-khoi">
    <div class="cd-dau">
      <h3>{{ tieuDe }}</h3>
      <span v-if="phu || $slots.phu" class="nho"><slot name="phu">{{ phu }}</slot></span>
      <slot name="dau" />
    </div>
    <slot />
    <div v-if="lenh.length" class="cd-lenh">
      <span class="nho">{{ nhanLenh }}</span>
      <LenhCli v-for="l in lenh" :key="l.lenh" :lenh="l.lenh" :ghi-chu="l.ghi_chu" />
      <slot name="sau-lenh" />
    </div>
  </section>
</template>
