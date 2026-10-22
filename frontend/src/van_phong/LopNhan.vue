<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, shallowRef, watch } from 'vue'
import { coChu } from './khung_nhin.js'
import { xepNhan } from './nhan_canh.js'

// Lớp nhãn HTML phủ lên canvas (mockup van-phong.js "lop-phu", D20): biển phòng, tên + nhãn phụ, bong bóng việc,
// huy hiệu đỏ, huy hiệu Giám đốc, đường chỉ. Nhãn là <button> thật (thêm một đường dùng bàn phím). Vị trí đặt qua
// :style transform (CSSOM, hợp CSP); đo cỡ sau nextTick và sau document.fonts.ready rồi chạy boTriNhan.
const props = defineProps({
  nhan: { type: Array, required: true },
  chieu: { type: Object, default: null },                // chieuNhan(): { W, H, diem, than }
})
const emit = defineEmits(['chon'])
const lop = ref(null)
const kq = shallowRef({ viTri: {}, duong: [] })
const coPx = computed(() => (props.chieu ? coChu(props.chieu.W) : 16))
const LOP = { bien: 'bien-phong', ten: 'ten-nv', bb: 'bong-bong', hh: 'huy-hieu-do', gd: 'huy-hieu-do lon' }
let conSong = true

async function xep() {
  await nextTick()
  if (!conSong || !props.chieu || !lop.value) return
  const co = {}
  for (const el of lop.value.querySelectorAll('[data-id]')) {
    co[el.dataset.id] = { w: el.offsetWidth, h: el.offsetHeight }
  }
  kq.value = xepNhan(props.nhan, props.chieu, co)
}
watch(() => [props.nhan, props.chieu], xep, { immediate: true })
onMounted(() => document.fonts?.ready.then(xep))
onUnmounted(() => { conSong = false })

const lopNhan = (n) => [LOP[n.loai], { mo: n.mo, chua: !kq.value.viTri[n.id] }]
function kieu(n) {
  const v = kq.value.viTri[n.id]
  return v ? { transform: `translate(${v.x}px, ${v.y}px)` } : null
}
</script>

<template>
  <div ref="lop" class="lop-phu" :style="{ fontSize: coPx + 'px' }">
    <svg class="duong-chi" aria-hidden="true">
      <template v-for="(d, i) in kq.duong" :key="i">
        <line :x1="d[0]" :y1="d[1]" :x2="d[2]" :y2="d[3]" />
        <circle :cx="d[0]" :cy="d[1]" r="2.5" />
      </template>
    </svg>
    <button v-for="n in nhan" :key="n.id" type="button" :data-id="n.id" :class="lopNhan(n)" :style="kieu(n)"
            :aria-label="n.nhanDoc" :title="n.loai === 'hh' ? 'Cần Đại ca trả lời' : null"
            @click="emit('chon', n.chon)">
      <template v-if="n.loai === 'bien'">
        {{ n.chu }}<template v-if="n.den"><span class="den" :class="{ sang: n.den.sang }" />
          <small>{{ n.den.chu }}</small></template>
      </template>
      <template v-else-if="n.loai === 'ten'">{{ n.chu }}<small>{{ n.phu }}</small></template>
      <template v-else-if="n.loai === 'bb'"><b>{{ n.ma }}</b>{{ n.chu }}</template>
      <template v-else-if="n.loai === 'gd'">{{ n.chu }}<span class="phu">việc chờ</span></template>
      <template v-else>{{ n.chu }}</template>
    </button>
  </div>
</template>
