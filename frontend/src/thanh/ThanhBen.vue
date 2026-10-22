<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { kho } from '../kho.js'
import { MENU, mucCua } from '../menu.js'
import BieuTuong from './BieuTuong.vue'

// Sidebar 272 px (mockup index.html `.sidebar`, anh-tong-quan.png): logo, menu 9 mục, máy trạm, thẻ người dùng.
// Không có danh tính Đại ca (gọi thẳng 127.0.0.1) → thẻ "Chỉ đọc" (D38/Q15).
const may = window.location.hostname
const cucBo = ['127.0.0.1', 'localhost', '::1'].includes(may)
const laDaiCa = computed(() => Boolean(kho.trangThai && kho.trangThai.la_dai_ca))
// Mục sáng theo `mucCua` (TM-4): /du-an/<ten> (trang Tự động) vẫn sáng "Dự án" như mockup.
const route = useRoute()
const chon = computed(() => mucCua(route.path)?.ma)
</script>

<template>
  <aside class="sidebar">
    <div class="ws">
      <div class="ws-logo" aria-hidden="true">B</div>
      <div class="ws-ten"><strong>Ben Station</strong><span class="mono">Trạm điều phối</span></div>
      <span class="ws-huy-hieu">Bàn điều hành</span>
    </div>
    <nav class="menu" aria-label="Điều hướng chính">
      <router-link v-for="m in MENU" :key="m.ma" :to="m.duong" :class="{ chon: chon === m.ma }">
        <BieuTuong :ten="m.ma" />{{ m.ten }}
        <span v-if="m.dem && kho.soPheDuyet" class="dem" :aria-label="kho.soPheDuyet + ' việc chờ'">
          {{ kho.soPheDuyet }}</span>
      </router-link>
    </nav>
    <div class="sb-day">
      <div class="may-tram mono">
        <span class="cham xanh" />{{ cucBo ? 'Máy trạm cục bộ' : 'Máy trạm' }}<b>{{ may }}</b>
      </div>
      <router-link class="nguoi-dung" to="/tai-khoan/thiet-bi">
        <div class="avatar" :class="{ 'chi-doc': !laDaiCa }" aria-hidden="true">{{ laDaiCa ? 'ĐC' : '?' }}</div>
        <div v-if="laDaiCa"><strong>Đại ca</strong><span class="mono">Chủ trạm</span></div>
        <div v-else><strong>Chỉ đọc</strong><span>không có danh tính Đại ca</span></div>
      </router-link>
    </div>
  </aside>
</template>
