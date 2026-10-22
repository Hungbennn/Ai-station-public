<script setup>
import { onMounted, onUnmounted, ref, watch } from 'vue'
import { doc } from '../api.js'
import { gioPhut } from '../dinh_dang.js'
import { kho } from '../kho.js'
import '../kieu/tong-quan.css'
import DauTrang from '../thanh/DauTrang.vue'
import KhoiDoiNgu from '../thanh/tong_quan/KhoiDoiNgu.vue'
import KhoiDuAn from '../thanh/tong_quan/KhoiDuAn.vue'
import KhoiSucKhoe from '../thanh/tong_quan/KhoiSucKhoe.vue'
import KhoiSuKien from '../thanh/tong_quan/KhoiSuKien.vue'
import KhoiUsage from '../thanh/tong_quan/KhoiUsage.vue'
import KhoiViecCho from '../thanh/tong_quan/KhoiViecCho.vue'

// Trang mở đầu (D17; mockup trang-tong-quan.js veTongQuan, anh-tong-quan.png). Một API gom `/api/tong-quan` (D38).
// Nhịp tim / hạn mức không phải sự kiện → tải lại mỗi 5 giây như Văn phòng, cộng SSE (phienBan, phienBanDoiNgu).
const CHU_KY_MS = 5000
const dl = ref(null)
const loi = ref('')
const bayGio = ref(new Date())
let hen = null
let luotTai = 0

async function tai() {
  const luot = ++luotTai
  try {
    const moi = await doc('/api/tong-quan')
    if (luot !== luotTai) return          // bỏ kết quả của lượt tải cũ
    dl.value = moi
    bayGio.value = new Date()
    loi.value = ''
  } catch (e) {
    if (luot === luotTai) loi.value = e.message
  }
}
onMounted(() => { tai(); hen = setInterval(tai, CHU_KY_MS) })
onUnmounted(() => { clearInterval(hen); luotTai += 1 })
watch(() => [kho.phienBan, kho.phienBanDoiNgu], tai)
</script>

<template>
  <DauTrang tieu-de="Tổng quan"
            mo-ta="Bức tranh chung của trạm trong một màn. Chỉ đọc; bấm vào từng mục để sang trang xử lý.">
    <template v-if="dl" #cong-cu><span class="nho">cập nhật {{ gioPhut(dl.doc_luc) }}</span></template>
  </DauTrang>
  <p v-if="loi" class="loi" role="alert">{{ loi }}</p>
  <p v-if="!dl && !loi" class="nho">Đang tải…</p>
  <template v-if="dl">
    <KhoiViecCho :dl="dl" />
    <div class="tq-luoi">
      <KhoiSucKhoe :dl="dl" :bay-gio="bayGio" />
      <KhoiDoiNgu :doi-ngu="dl.doi_ngu" :bay-gio="bayGio" />
    </div>
    <div class="tq-luoi tq-luoi-2">
      <KhoiDuAn :du-an="dl.du_an || []" />
      <KhoiUsage :usage="dl.usage" />
    </div>
    <KhoiSuKien :su-kien="dl.su_kien || []" />
  </template>
</template>
