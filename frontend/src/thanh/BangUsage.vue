<script setup>
import { computed } from 'vue'
import '../kieu/khe.css'
import '../kieu/usage.css'
import { gon, soDayDu, usd } from '../dinh_dang.js'
import { TRUONG_TOKEN, nguonUsage, tiTrong as tinhTiTrong } from '../luat_usage.js'

// Bảng usage (mockup trang-usage.js bang()): số gọn "4,20 tr", rê chuột ra số đầy đủ (D39); "x thiếu giá";
// cột Tỉ trọng tuỳ chọn; `cuon` = khung cuộn dọc, đầu bảng dính.
const props = defineProps({
  tenKhoa: { type: String, required: true },
  dong: { type: Array, required: true },   // [{khoa, token_*, so_lan?, chi_phi_usd, thieu_gia?}]
  laNguon: { type: Boolean, default: false },
  coSoLan: { type: Boolean, default: true },
  tiTrong: { type: Boolean, default: false },
  cuon: { type: Boolean, default: false },
})
const tt = computed(() => (props.tiTrong ? tinhTiTrong(props.dong) : []))
const nguon = computed(() => props.dong.map((d) => nguonUsage(d.khoa)))
const TEN_COT = ['Token vào', 'Token ra', 'Cache đọc', 'Cache ghi']
</script>

<template>
  <p v-if="!dong.length" class="nho">Không có số liệu trong khoảng này.</p>
  <div v-else class="us-bang" :class="{ cuon }">
    <table class="bang">
      <thead><tr>
        <th scope="col">{{ tenKhoa }}</th><th v-for="t in TEN_COT" :key="t" scope="col">{{ t }}</th>
        <th v-if="coSoLan" scope="col">Lần gọi</th><th scope="col">Chi phí</th>
        <th v-if="tiTrong" scope="col" class="us-cot-tt">Tỉ trọng</th>
      </tr></thead>
      <tbody><tr v-for="(d, i) in dong" :key="d.khoa">
        <th v-if="laNguon" scope="row"><span class="cham" :style="{ background: nguon[i].mau }" /><span
          :class="{ mono: nguon[i].mono }">{{ nguon[i].ten }}</span></th>
        <th v-else scope="row"><span class="mono">{{ d.khoa }}</span></th>
        <td v-for="t in TRUONG_TOKEN" :key="t" class="so" :title="soDayDu(d[t])">{{ gon(d[t]) }}</td>
        <td v-if="coSoLan" class="so">{{ soDayDu(d.so_lan) }}</td>
        <td class="so">{{ usd(d.chi_phi_usd) }}<span v-if="d.thieu_gia && d.chi_phi_usd != null" class="us-thieu"
          :title="`${d.thieu_gia} lần gọi chưa có giá — không tính vào chi phí`">{{ d.thieu_gia }} thiếu giá</span></td>
        <td v-if="tiTrong"><div class="thanh-hm us-tt" role="img" :aria-label="`Tỉ trọng ${Math.round(tt[i])}%`">
          <i :style="{ width: `${tt[i]}%` }" /></div></td>
      </tr></tbody>
    </table>
  </div>
</template>
