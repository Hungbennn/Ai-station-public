<script setup>
// Thẻ bead (mockup trang.js theBead, anh-cong-viec.png); chip của bản cũ giữ theo khảo sát §1.3 + D37.
import { computed } from 'vue'
import { chipThe, uuTien } from '../luat_cong_viec.js'
import { duocGhi } from '../quyen_passkey.js'
import { kho } from '../kho.js'

const props = defineProps({
  the: { type: Object, required: true },
  khe: { type: Object, default: null },          // dongKhe(): {ten, buoc, canNguoi, mau} | null
  chiQuetThu: { type: Boolean, default: false },  // dự án bat_ghi: false — không kéo được
})
const emit = defineEmits(['mo', 'keo'])
const chip = computed(() => chipThe(props.the, props.chiQuetThu))
const keoDuoc = computed(() => props.the.keo_duoc && !props.chiQuetThu && duocGhi(kho.trangThai))

function batDauKeo(e) {
  if (!keoDuoc.value) { e.preventDefault(); return }
  e.dataTransfer.setData('text/plain', props.the.id)   // Firefox chỉ bắt đầu kéo khi có dữ liệu (N2)
  e.dataTransfer.effectAllowed = 'move'
  emit('keo')
}
</script>

<template>
  <article class="the the-bead" :class="{ mo: the.mo }" tabindex="0" :draggable="keoDuoc ? 'true' : 'false'"
           :aria-label="the.id + ': ' + the.tieu_de" @click="emit('mo')" @keydown.enter="emit('mo')"
           @dragstart="batDauKeo">
    <div class="tren">
      <span class="ma">{{ the.id }}</span><span class="chip">{{ the.du_an }}</span>
      <span class="nho phai">{{ the.loai }} · {{ uuTien(the) }}</span>
    </div>
    <div class="tieu-de">{{ the.tieu_de }}</div>
    <div v-if="chip.length" class="nhan-ds">
      <span v-for="c in chip" :key="c.chu" class="chip" :class="c.lop" :title="c.goiY || null">{{ c.chu }}</span>
    </div>
    <div v-if="khe" class="khe">
      <span class="cham" :style="{ background: khe.mau }"></span>{{ khe.buoc ? `${khe.ten} · ${khe.buoc}` : khe.ten }}
      <template v-if="khe.canNguoi"> · <b class="chu-do">đang hỏi Đại ca</b></template>
    </div>
  </article>
</template>
