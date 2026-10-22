<script setup>
import { gioPhut } from '../../dinh_dang.js'
import { CHU_CHI_QUET_THU } from '../../luat.js'

// Khối "Theo dự án" (mockup trang-tong-quan.js khoiDuAn): số bead cột 1/2/3 từ `so_bead`, việc mới xong (`moi_xong`).
// Dự án `bat_ghi === false` vẽ mờ kèm chip "chỉ quét thử" (D37; mockup ghi "tạm đóng", D37 đổi chữ).
defineProps({ duAn: { type: Array, required: true } })
const COT = ['ai-lam', 'can-chot', 'cho-review']
const so = (d, cot) => (d.so_bead && d.so_bead[cot]) || 0
</script>

<template>
  <section class="the">
    <h3 class="tieu-de-khoi">Theo dự án</h3>
    <p v-if="!duAn.length" class="nho">Chưa có dự án nào.</p>
    <div v-else class="bang-cuon">
      <table class="bang">
        <thead><tr>
          <th>Dự án</th><th>1 · AI làm</th><th>2 · Cần chốt</th><th>3 · Chờ review</th><th>Mới xong</th>
        </tr></thead>
        <tbody>
          <tr v-for="d in duAn" :key="d.ten" :class="{ mo: d.bat_ghi === false }">
            <th>
              <router-link :to="{ path: '/cong-viec', query: { du_an: d.ten } }">{{ d.ten }}</router-link>
              <span v-if="d.bat_ghi === false" class="chip" :title="CHU_CHI_QUET_THU">chỉ quét thử</span>
            </th>
            <td v-for="c in COT" :key="c" class="so">
              <template v-if="so(d, c)">{{ so(d, c) }}</template><span v-else class="nho">0</span>
            </td>
            <td v-if="d.moi_xong">
              <span class="mono tq-xong">{{ d.moi_xong.id }}</span> {{ d.moi_xong.tieu_de }}
              <span class="nho">· {{ gioPhut(d.moi_xong.luc) }}</span>
            </td>
            <td v-else><span class="nho">—</span></td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>
