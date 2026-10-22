<script setup>
// Dòng thời gian trong ngăn bên (mockup trang.js moBead `.dtg`: giờ mono + loại + tóm tắt). Mới nhất lên trước như cũ.
import { ngayGio } from '../dinh_dang.js'
import { gioVN } from '../luat.js'

defineProps({ ds: { type: Array, required: true } })
</script>

<template>
  <section>
    <h4>Dòng thời gian</h4>
    <p v-if="!ds.length" class="nho">Chưa có sự kiện.</p>
    <ol v-else class="dtg" reversed>
      <li v-for="s in [...ds].reverse()" :key="s.id">
        <span class="mono" :title="gioVN(s.luc)">{{ ngayGio(s.luc) }}</span><strong>{{ s.loai }}</strong>
        {{ s.tom_tat }} <span class="nho">· {{ s.tac_nhan }}</span>
      </li>
    </ol>
  </section>
</template>
