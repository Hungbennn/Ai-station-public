<script setup>
import { onMounted, onUnmounted, ref, watch } from 'vue'
import '../../kieu/khe.css'
import '../../kieu/usage.css'
import { doc } from '../../api.js'
import { kho } from '../../kho.js'
import { cuaSo, oHanMuc, tenKhe } from '../../luat_han_muc.js'
import { nguonUsage, nhanLuat } from '../../luat_usage.js'

// Khối "Hạn mức thuê bao của khe" (mockup trang-usage.js khoiHanMuc, D39): đọc /api/doi-ngu mỗi 5 giây như trang
// Đội ngũ AI, và ngay khi có sự kiện doi_ngu_doi. Cột luật nhận việc theo `muc_han_muc` server đã tính.
const CHU_KY_MS = 5000
const ds = ref(null)
const loi = ref('')
let hen = null

async function tai() {
  try {
    ds.value = ((await doc('/api/doi-ngu')).khe || []).map((k) => ({
      k, nguon: nguonUsage(k.khe_id), luat: nhanLuat(k.muc_han_muc),
      o: [oHanMuc(cuaSo(k, '5h')), oHanMuc(cuaSo(k, 'tuan'))],
    }))
    loi.value = ''
  } catch (e) {
    loi.value = e.message
  }
}
onMounted(() => { tai(); hen = setInterval(tai, CHU_KY_MS) })
onUnmounted(() => clearInterval(hen))
watch(() => kho.phienBanDoiNgu, tai)
</script>

<template>
  <section class="the us-khoi">
    <h3 class="tq-h">Hạn mức thuê bao của khe <span class="nho us-h-phu">từ <span class="mono">/api/doi-ngu</span> ·
      đọc mỗi 5 giây</span><router-link class="nho us-lk" to="/doi-ngu">Mở Đội ngũ AI →</router-link></h3>
    <p v-if="loi" class="loi" role="alert">{{ loi }}</p>
    <p v-if="ds && !ds.length" class="nho">Chưa có khe nào đăng ký với trạm.</p>
    <div v-if="ds && ds.length" class="bang-cuon">
      <table class="bang us-hm">
        <thead><tr><th scope="col">Khe</th><th scope="col">Cửa sổ 5 giờ</th><th scope="col">Cửa sổ tuần</th>
          <th scope="col">Luật nhận việc</th></tr></thead>
        <tbody><tr v-for="x in ds" :key="x.k.khe_id">
          <th scope="row" :title="tenKhe(x.k)"><span class="cham" :style="{ background: x.nguon.mau }" /><span
            class="mono">{{ x.k.khe_id }}</span></th>
          <td v-for="(o, i) in x.o" :key="i"><div class="us-o-hm">
            <div class="thanh-hm" role="img" :aria-label="o.chu"><i v-if="o.con !== null" :class="o.lop"
              :style="{ width: `${o.rong}%` }" /></div>
            <span :class="{ nho: o.con === null }">{{ o.chu }}</span>
          </div></td>
          <td><span class="chip" :class="x.luat.lop">{{ x.luat.chu }}</span></td>
        </tr></tbody>
      </table>
    </div>
    <p class="nho us-giai">Đã dùng ≥ 90% một cửa sổ thì khe ngừng nhận việc; tuần cao chỉ nhận P0–P1; chưa biết vẫn
      nhận việc kèm cảnh báo vàng. Giá trên trang này là tương đương — hạn mức mới là giới hạn thật của khe thuê
      bao.</p>
  </section>
</template>
