<script setup>
import { gioPhut } from '../../dinh_dang.js'

// Khối "Sự kiện gần đây" (mockup trang-tong-quan.js khoiSuKien): ≤ 18 sự kiện mới nhất, `mo_ta` dựng ở server (D39).
defineProps({ suKien: { type: Array, required: true } })
const toiBead = (s) => ({ path: '/cong-viec', query: { du_an: s.du_an, bead: s.bead_id } })
</script>

<template>
  <section class="the">
    <h3 class="tieu-de-khoi">Sự kiện gần đây <span class="nho tq-dem">{{ suKien.length }} dòng mới nhất</span></h3>
    <p v-if="!suKien.length" class="nho">Chưa có sự kiện nào.</p>
    <div v-else class="bang-cuon">
      <table class="bang tq-sk">
        <tbody>
          <tr v-for="s in suKien" :key="s.id">
            <td class="mono nho">{{ gioPhut(s.luc) }}</td>
            <td><span class="chip mono">{{ s.loai }}</span></td>
            <td>{{ s.du_an }}</td>
            <td>
              <router-link v-if="s.bead_id" class="mono" :to="toiBead(s)">{{ s.bead_id }}</router-link>
              <span v-else class="nho">—</span>
            </td>
            <td class="nho">{{ s.mo_ta }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>
