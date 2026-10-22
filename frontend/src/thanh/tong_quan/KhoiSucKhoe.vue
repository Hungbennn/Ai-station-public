<script setup>
import { computed } from 'vue'
import { chipDichVu, dongTram } from '../../luat_tong_quan.js'

// Khối "Sức khoẻ trạm" (mockup trang-tong-quan.js khoiSucKhoe): dịch vụ launchd vn.tram.* rồi bốn dòng trạm.
const props = defineProps({ dl: { type: Object, required: true }, bayGio: { type: Date, required: true } })
const dichVu = computed(() => (props.dl.dich_vu || []).map((d) => ({ ...d, chip: chipDichVu(d) })))
const dong = computed(() => dongTram(props.dl, props.bayGio))
</script>

<template>
  <section class="the">
    <h3 class="tieu-de-khoi">Sức khoẻ trạm</h3>
    <ul class="tq-ds">
      <li v-for="d in dichVu" :key="d.nhan">
        <span class="mono">{{ d.nhan }}</span><span class="nho">{{ d.viec }}</span>
        <span class="chip" :class="d.chip.lop">{{ d.chip.chu }}</span>
      </li>
    </ul>
    <ul class="tq-ds tq-ds2">
      <li v-for="[ten, gt, lop] in dong" :key="ten">
        <span>{{ ten }}</span><span class="chip" :class="lop">{{ gt }}</span>
      </li>
    </ul>
  </section>
</template>
