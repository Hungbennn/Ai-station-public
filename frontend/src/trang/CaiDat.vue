<script setup>
import { computed, onMounted, ref } from 'vue'
import { doc } from '../api.js'
import { ghepBatGhi } from '../luat_cai_dat.js'
import DauTrang from '../thanh/DauTrang.vue'
import BangSanSang from '../thanh/cai_dat/BangSanSang.vue'
import KhoiCo from '../thanh/cai_dat/KhoiCo.vue'
import KhoiDichVu from '../thanh/cai_dat/KhoiDichVu.vue'
import KhoiDuAn from '../thanh/cai_dat/KhoiDuAn.vue'
import KhoiKeychain from '../thanh/cai_dat/KhoiKeychain.vue'
import KhoiTelegram from '../thanh/cai_dat/KhoiTelegram.vue'
import '../kieu/cai-dat.css'

// Trang Cài đặt — CHỈ ĐỌC (D19; mockup trang-cai-dat.js, ảnh anh-cai-dat.png).
// Chỉ Đại ca xem (D38/Q13): 403 → thẻ chặn.
// Không SSE: "Kiểm lại" tải lại hai API. bat_ghi lấy từ /api/du-an (D37); lỗi đọc thì coi như bật ghi.
const caiDat = ref(null)
const sanSang = ref(null)
const duAn = ref(null)
const cam = ref(false)
const loi = ref('')
const dangTai = ref(false)
const dsDuAn = computed(() => ghepBatGhi(caiDat.value && caiDat.value.du_an, duAn.value))

async function tai() {
  dangTai.value = true
  try {
    const [c, s, d] = await Promise.all([
      doc('/api/cai-dat'), doc('/api/san-sang'), doc('/api/du-an').catch(() => null),
    ])
    caiDat.value = c
    sanSang.value = s
    duAn.value = d && d.du_an
    cam.value = false
    loi.value = ''
  } catch (e) {
    cam.value = e.status === 403
    loi.value = cam.value ? '' : e.message
  } finally {
    dangTai.value = false
  }
}
onMounted(tai)
</script>

<template>
  <DauTrang
    tieu-de="Cài đặt"
    mo-ta="Chỉ đọc. Không sửa được qua web; mỗi mục kèm lệnh CLI gợi ý để Đại ca tự chạy trên máy B."
  >
    <template #cong-cu>
      <span class="chip">chỉ đọc</span>
      <button type="button" class="nut" :disabled="dangTai" @click="tai">Kiểm lại</button>
    </template>
  </DauTrang>
  <section v-if="cam" class="the the-chan" role="alert">
    <strong>403 · Chỉ Đại ca xem được Cài đặt</strong>
    <p>Trang này cần danh tính Tailscale của Đại ca. Máy hoặc tài khoản khác không đọc được cấu hình trạm.</p>
  </section>
  <template v-else>
    <p v-if="loi" class="loi" role="alert">{{ loi }}</p>
    <p v-if="!caiDat && !loi" class="nho">Đang đọc cấu hình…</p>
    <BangSanSang v-if="sanSang" :ss="sanSang" />
    <template v-if="caiDat">
      <div class="cd-luoi">
        <KhoiDuAn :ds="dsDuAn" />
        <KhoiDichVu :ds="caiDat.dich_vu || []" />
        <KhoiTelegram :tg="caiDat.telegram || {}" />
        <KhoiCo :ds="caiDat.co || []" />
        <KhoiKeychain :ds="caiDat.keychain || []" />
      </div>
      <p v-for="(l, i) in caiDat.loi_cau_hinh || []" :key="i" class="canh-bao">{{ l }}</p>
    </template>
  </template>
</template>
