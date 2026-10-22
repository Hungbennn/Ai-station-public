<script setup>
// Bộ giao việc trong ngăn bên. PR trạm mở vẽ theo khối "PR" của mockup trang.js moBead (chip + "PR #12 — lý do");
// phần còn lại (chưa giao, lệnh gh pr create) giữ bố cục cũ, chỉ áp lớp mới (D36).
import { computed } from 'vue'
import { canhBaoPr, canhBaoPrTram, lopPrTram, moTaPrTram, nhanPrTram } from '../giao_viec.js'
import { laLinkAnToan } from '../luat.js'

const props = defineProps({ giao: { type: Object, required: true } })
const canhBao = computed(() => canhBaoPr(props.giao.pr))
const tram = computed(() => (props.giao.pr && props.giao.pr.tram) || null)
const nhanTram = computed(() => nhanPrTram({ giao: props.giao }))
</script>

<template>
  <section aria-label="Bộ giao việc">
    <template v-if="tram">
      <h4>PR</h4>
      <p><span v-if="nhanTram" class="chip" :class="lopPrTram(tram)">{{ nhanTram }}</span> {{ moTaPrTram(tram) }}</p>
      <p v-if="canhBaoPrTram(tram)" class="canh-bao" role="alert">{{ canhBaoPrTram(tram) }}</p>
      <p v-if="laLinkAnToan(tram.url)">
        <a :href="tram.url" target="_blank" rel="noopener noreferrer">Mở PR trên GitHub</a>
      </p>
    </template>
    <template v-if="giao.khong_giao || (!tram && giao.pr)">
      <h4>Bộ giao việc</h4>
      <p v-if="giao.khong_giao" class="canh-bao">Chưa giao: {{ giao.khong_giao }}</p>
      <template v-if="!tram && giao.pr">
        <p class="nho">Tạo PR từ nhánh {{ giao.pr.nhanh }} tại commit {{ giao.pr.commit }} (trạm đã kiểm lại và QC).</p>
        <p v-if="canhBao" class="canh-bao" role="alert">{{ canhBao }}</p>
        <p v-else-if="laLinkAnToan(giao.pr.link)">
          <a :href="giao.pr.link" target="_blank" rel="noopener noreferrer">Mở trang tạo PR trên GitHub</a>
        </p>
        <pre class="van-ban lenh">{{ giao.pr.lenh }}</pre>
      </template>
    </template>
  </section>
</template>
