<script setup>
import { computed } from 'vue'
import '../../kieu/usage.css'
import { gon, ngayNgan, soDayDu, usd } from '../../dinh_dang.js'
import { chieuCot, dayNgay, giaTriNgay, hienMocNgay, trucBieuDo } from '../../luat_usage.js'

// Biểu đồ cột theo ngày (mockup trang-usage.js bieuDo): mỗi ngày tu..den một cột, cột hôm nay (`den`) đậm;
// rê chuột hoặc Tab tới cột (tabindex=0) hiện tooltip `.us-tip`. `che`: 'chi_phi' | 'token' (vào + ra).
const props = defineProps({
  theoNgay: { type: Array, required: true },
  tu: { type: String, required: true },
  den: { type: String, required: true },
  che: { type: String, default: 'chi_phi' },
})
const KE = [1, 2, 3, 4]

const cot = computed(() => {
  const m = Object.fromEntries(props.theoNgay.map((d) => [d.khoa, d]))
  return dayNgay(props.tu, props.den).map((ngay) => {
    const c = { ngay, d: m[ngay], nay: ngay === props.den }
    return { ...c, tip: tip(c) }
  })
})
const truc = computed(() => trucBieuDo(Math.max(0, ...cot.value.map((c) => giaTriNgay(c.d, props.che))), props.che))

function tip(c) {
  const dau = `${ngayNgan(c.ngay)}${c.nay ? ' · hôm nay' : ''}`
  if (!c.d) return [dau, 'không có sự kiện', '']
  return [dau, `${usd(c.d.chi_phi_usd)} · ${soDayDu(c.d.so_lan)} lần`,
    `${gon(c.d.token_vao)} vào · ${gon(c.d.token_ra)} ra`]
}
</script>

<template>
  <div class="us-bd">
    <div class="us-truc" aria-hidden="true"><span v-for="(n, i) in truc.nhan" :key="i">{{ n }}</span></div>
    <div class="us-vung">
      <i v-for="k in KE" :key="k" class="us-ke" :style="{ bottom: `${k * 25}%` }" />
      <div v-for="(c, i) in cot" :key="c.ngay" class="us-cot" :class="{ nay: c.nay }" tabindex="0" role="img"
        :aria-label="c.tip.filter(Boolean).join(' · ')">
        <b :style="{ height: `${chieuCot(giaTriNgay(c.d, che), truc.tran)}%` }" />
        <span class="us-tip" aria-hidden="true"><strong>{{ c.tip[0] }}</strong>{{ c.tip[1] }}<template
          v-if="c.tip[2]"><br>{{ c.tip[2] }}</template></span>
        <em v-if="hienMocNgay(i, cot.length, c.nay)" aria-hidden="true">{{ ngayNgan(c.ngay) }}</em>
      </div>
    </div>
  </div>
</template>
