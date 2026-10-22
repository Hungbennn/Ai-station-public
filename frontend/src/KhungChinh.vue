<script setup>
import { computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { duocGhi, quyenPasskey } from './quyen_passkey.js'
import { dungEstop } from './estop.js'
import { kho, moLuong, taiSoPheDuyet, taiTrangThai, taiTuDong, theoDoiTab } from './kho.js'
import { tieuDeTab } from './luat.js'
import { nutTamDungTram } from './luat_tu_dong.js'
import { tenTrang } from './menu.js'
import { dungTamDungTram } from './tam_dung.js'
import HopPasskey from './thanh/HopPasskey.vue'
import BangEstop from './thanh/BangEstop.vue'
import BangTamDung from './thanh/BangTamDung.vue'
import ThanhBen from './thanh/ThanhBen.vue'
import ThanhTren from './thanh/ThanhTren.vue'

// Khung mockup (index.html): sidebar | thanh trên + băng estop + băng tạm dừng (TM-4) + trang.
// Tiêu đề tab "<trang> · Ben Station".
const route = useRoute()
const estop = dungEstop()
const khoa = computed(() => !duocGhi(kho.trangThai) || estop.dangGui.value)
const tamDung = dungTamDungTram()
const nutTD = computed(() => {
  const nut = nutTamDungTram(kho.tuDong, Boolean(kho.trangThai && kho.trangThai.la_dai_ca))
  return nut.bat && !duocGhi(kho.trangThai)
    ? { ...nut, khoa: true, lyDo: 'Cần đăng ký passkey để Tiếp tục' } : nut
})
onMounted(() => { taiTrangThai(); taiSoPheDuyet(); taiTuDong(); moLuong(); theoDoiTab() })
watch([() => route.path, () => kho.soPheDuyet],
  () => { document.title = tieuDeTab(kho.soPheDuyet, tenTrang(route.path)) }, { immediate: true })
</script>

<template>
  <HopPasskey />
  <ThanhBen />
  <div class="khung">
    <ThanhTren :estop="estop" :tam-dung="tamDung" :nut-tam-dung="nutTD" />
    <BangEstop v-if="kho.trangThai && kho.trangThai.estop" :khoa="khoa" @tiep-tuc="estop.bam(false)" />
    <BangTamDung v-if="nutTD.bat" :khoa="nutTD.khoa || tamDung.dangGui.value" :ly-do="nutTD.lyDo"
                 @tiep-tuc="tamDung.bam(false)" />
    <p v-if="estop.thongBao.value" class="loi-chung" role="alert">{{ estop.thongBao.value }}</p>
    <p v-if="tamDung.thongBao.value" class="loi-chung" role="alert">{{ tamDung.thongBao.value }}</p>
    <p v-if="kho.loi" class="loi-chung" role="alert">{{ kho.loi }}</p>
    <p v-if="kho.trangThai?.la_dai_ca && !quyenPasskey.tt?.thiet_bi.length" class="loi-chung" role="status">
      Chưa có passkey hoặc chưa đọc được trạng thái: chỉ TẠM DỪNG và Estop.
      <router-link to="/tai-khoan/thiet-bi">Đăng ký thiết bị</router-link>
    </p>
    <main class="trang"><router-view /></main>
  </div>
</template>
