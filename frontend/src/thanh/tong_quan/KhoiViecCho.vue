<script setup>
import { computed } from 'vue'
import { oViecCho } from '../../luat_tong_quan.js'

// Khối "Việc chờ Đại ca" (mockup trang-tong-quan.js khoiViecCho). Tổng = `phe_duyet.so`, đúng số badge menu
// (D38/Q6); năm ô đếm riêng nên tổng không nhất thiết bằng tổng các ô.
const props = defineProps({ dl: { type: Object, required: true } })
const o = computed(() => oViecCho(props.dl))
const tong = computed(() => (props.dl.phe_duyet && props.dl.phe_duyet.so) || 0)
</script>

<template>
  <section class="the tq-cho">
    <div class="tq-dau">
      <h2>Việc chờ Đại ca</h2><span class="tq-tong">{{ tong }}</span>
      <span class="nho">chờ ở Phê duyệt · sắp theo độ gấp</span>
      <router-link class="nut chinh" to="/phe-duyet">Mở Phê duyệt</router-link>
    </div>
    <div class="tq-o-cho">
      <router-link v-for="x in o" :key="x.ten" class="tq-o" :class="{ rong: !x.so }" :to="x.toi">
        <span class="so" :class="x.so ? x.lop : ''">{{ x.so }}</span>
        <strong>{{ x.ten }}</strong><span class="nho">{{ x.phu }}</span>
      </router-link>
    </div>
    <p v-for="(l, t) in (dl.phe_duyet && dl.phe_duyet.loi) || {}" :key="t" class="loi">{{ t }}: {{ l }}</p>
  </section>
</template>
