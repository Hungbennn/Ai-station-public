<script setup>
import { computed } from 'vue'
import { usageHomNay } from '../../luat_tong_quan.js'

// Khối "Usage hôm nay" (mockup trang-tong-quan.js khoiUsage): bốn ô số + thanh chi phí từng khe (bỏ dòng chấm cột).
const props = defineProps({ usage: { type: Object, default: null } })
const u = computed(() => usageHomNay(props.usage))
</script>

<template>
  <section class="the">
    <h3 class="tieu-de-khoi">Usage hôm nay <router-link class="lk-phai" to="/usage">Chi tiết →</router-link></h3>
    <div class="tq-so">
      <div><b>{{ u.vao }}</b><span class="nho">token vào</span></div>
      <div><b>{{ u.ra }}</b><span class="nho">token ra</span></div>
      <div><b>{{ u.usdKhe }}</b><span class="nho">khe · tương đương</span></div>
      <div><b>{{ u.usdApi }}</b><span class="nho">Claude API chấm cột</span></div>
    </div>
    <div class="tq-cot">
      <div v-for="c in u.cot" :key="c.ma">
        <span class="mono">{{ c.ma }}</span><i :style="{ width: c.rong + '%' }" /><span>{{ c.usd }}</span>
      </div>
    </div>
    <p class="nho tq-chu-thich">
      {{ u.luot }} lượt chạy · giá của khe thuê bao chỉ là tương đương, không phải tiền trả thêm.
    </p>
  </section>
</template>
