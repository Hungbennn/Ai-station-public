<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { doc } from '../api.js'
import { kho } from '../kho.js'
import { laPhimTim, timKiem } from '../tim.js'
import BieuTuong from './BieuTuong.vue'

// Ô tìm ⌘K (mockup index.html `.tim`; D38/Q5: tìm phía trình duyệt). Tải bead + khe một lần khi focus, giữ 30 giây.
const GIU_MS = 30000
const router = useRouter()
const o = ref(null)
const q = ref('')
const mo = ref(false)
const chon = ref(0)
const dl = ref({ the: [], khe: [] })
let taiLuc = 0
const duAn = computed(() => (kho.trangThai ? kho.trangThai.du_an.map((d) => d.ten) : []))
const ketQua = computed(() => timKiem(q.value, { duAn: duAn.value, ...dl.value }))

async function tai() {
  if (Date.now() - taiLuc < GIU_MS) return
  taiLuc = Date.now()
  const [cv, dn] = await Promise.all([doc('/api/cong-viec').catch(() => ({ the: [] })),
    doc('/api/doi-ngu').catch(() => ({ khe: [] }))])
  dl.value = { the: cv.the || [], khe: dn.khe || [] }
}
function di(kq) {
  if (!kq) return
  router.push(kq.den)
  q.value = ''
  mo.value = false
}
function phim(e) {
  const n = ketQua.value.length
  if (e.key === 'ArrowDown' && n) { e.preventDefault(); chon.value = (chon.value + 1) % n }
  else if (e.key === 'ArrowUp' && n) { e.preventDefault(); chon.value = (chon.value + n - 1) % n }
  else if (e.key === 'Enter') di(ketQua.value[chon.value])
  else if (e.key === 'Escape') { mo.value = false; o.value?.blur() }
}
const toanCuc = (e) => { if (laPhimTim(e)) { e.preventDefault(); o.value?.focus() } }
onMounted(() => window.addEventListener('keydown', toanCuc))
onUnmounted(() => window.removeEventListener('keydown', toanCuc))
</script>

<template>
  <label class="tim">
    <BieuTuong ten="tim" />
    <span class="an-chu">Tìm nhiệm vụ, dự án, agent phụ trách</span>
    <input ref="o" v-model="q" type="search" placeholder="Tìm nhiệm vụ, dự án, agent phụ trách… (⌘K)"
           role="combobox" aria-controls="ket-qua-tim" :aria-expanded="mo && ketQua.length > 0"
           @focus="mo = true; tai()" @input="mo = true; chon = 0" @keydown="phim" @blur="mo = false">
    <ul v-if="mo && ketQua.length" id="ket-qua-tim" class="ket-qua-tim" role="listbox">
      <li v-for="(k, i) in ketQua" :key="k.loai + k.nhan" role="option" :aria-selected="i === chon"
          :class="{ chon: i === chon }" @mousedown.prevent="di(k)">
        <span class="loai">{{ k.loai === 'bead' ? 'bead' : k.loai === 'khe' ? 'khe' : 'dự án' }}</span>
        <span>{{ k.nhan }}</span><span class="phu mono">{{ k.phu }}</span>
      </li>
    </ul>
  </label>
</template>
