<script setup>
// Trang Dự án — mockup trang.js veDuAn: lưới thẻ, tên dẫn tới /cong-viec?du_an=<ten>. TM-4 (mockup 2026-10-18
// trang-du-an.js, anh-du-an.png): hàng chip tự merge / tự deploy (từ kho.tuDong) + link "Tự động →" sang /du-an/<ten>.
import { computed, onMounted, ref, watch } from 'vue'
import { doc } from '../api.js'
import { kho } from '../kho.js'
import { theDuAn } from '../luat_du_an.js'
import DauTrang from '../thanh/DauTrang.vue'
import '../kieu/du-an.css'

const ds = ref([])
const loi = ref('')
const the = computed(() => ds.value.map((d) => theDuAn(d, kho.tuDong)))

async function tai() {
  try {
    ds.value = (await doc('/api/du-an')).du_an
    loi.value = ''
  } catch (e) {
    loi.value = e.message
  }
}
onMounted(tai)
watch(() => kho.phienBan, tai)
</script>

<template>
  <DauTrang
    tieu-de="Dự án"
    mo-ta="Các dự án đã thêm vào trạm: số bead mỗi cột, lần quét cuối, lỗi gần nhất, tự merge, tự deploy."
  />
  <p v-if="loi" class="loi" role="alert">{{ loi }}</p>
  <p v-if="!the.length && !loi" class="nho">Chưa có dự án nào trong du-an/.</p>
  <div v-if="the.length" class="ds-du-an">
    <div v-for="t in the" :key="t.ten" class="the the-du-an" :class="{ mo: t.chiQuetThu }">
      <div class="dau"><router-link class="ten-lk" :to="t.den">{{ t.ten }}</router-link>
        <span class="nho">{{ t.quet }}</span></div>
      <div class="ds-chip">
        <span v-for="c in t.chip" :key="c.chu" class="chip">{{ c.chu }}</span>
        <span v-if="t.chuaCham" class="chip">{{ t.chuaCham }}</span>
      </div>
      <div class="nho">{{ t.loiGanNhat }}</div>
      <div v-if="t.loiDoc" class="loi">{{ t.loiDoc }}</div>
      <div class="tu-dong">
        <span v-for="c in [...t.chipTuDong, ...t.chipPhu]" :key="c.chu" class="chip" :class="c.lop"
              :title="c.title || null">{{ c.chu }}</span>
        <router-link :to="t.tuDongDen">Tự động →</router-link>
      </div>
    </div>
  </div>
</template>
