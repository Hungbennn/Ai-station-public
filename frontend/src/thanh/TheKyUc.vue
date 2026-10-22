<script setup>
import { computed, ref } from 'vue'
import { ghi, thanGhi } from '../api.js'
import { ngayGio } from '../dinh_dang.js'
import { moTaNguon, nhanPhamVi } from '../nho.js'

// Một ký ức (mockup trang-ky-uc.js theKyUc, D36; spec 1b §5): nội dung chỉ hiện bằng text; Xoá = xoá mềm (`nho.xoa`).
const props = defineProps({ ky: { type: Object, required: true }, laDaiCa: { type: Boolean, default: false } })
const emit = defineEmits(['doi'])
const dangGui = ref(false)
const loi = ref('')
const pv = computed(() => nhanPhamVi(props.ky.pham_vi))
const nguon = computed(() => moTaNguon(props.ky.nguon))
const qt = computed(() => Math.min(1, Math.max(0, Number(props.ky.quan_trong) || 0)))

async function xoa() {
  if (!window.confirm('Xoá mềm ký ức này? Recall sẽ không trả nó nữa.')) return
  dangGui.value = true
  loi.value = ''
  try {
    await ghi('/api/nho/xoa', thanGhi({ id: props.ky.id }, props.ky.tao_luc))
    emit('doi', props.ky.id)
  } catch (e) {
    loi.value = e.message
  } finally {
    dangGui.value = false
  }
}
</script>

<template>
  <article class="the ku-the" :class="{ cho: ky.dang_cho }">
    <div class="ku-tren">
      <span class="chip" :class="pv[1]">{{ pv[0] }}</span>
      <span class="chip mono">{{ ky.pham_vi }}</span>
      <span v-if="ky.dang_cho" class="chip tt-cau_dao">chờ tự có hiệu lực {{ ngayGio(ky.hieu_luc_tu) }}</span>
      <span v-if="ky.nguon_dai_ca" class="chip ku-dai-ca">của Đại ca</span>
      <span v-for="n in ky.nhan" :key="n" class="ku-nhan mono">#{{ n }}</span>
      <button class="nut nguy ku-xoa" type="button" title="Xoá mềm — recall không trả nữa"
        :disabled="dangGui || !laDaiCa" @click="xoa">Xoá</button>
    </div>
    <p class="ku-noi-dung">{{ ky.noi_dung }}</p>
    <div class="ku-meta">
      <span>Nguồn:
        <template v-for="(n, i) in nguon" :key="i"><template v-if="i">; </template>
          <template v-if="n.thangCap">thăng cấp từ <b>{{ n.duAn }}</b> <span
            class="mono nho">{{ n.idGoc }}</span></template>
          <template v-else>{{ n.chu }}<template v-if="n.bead"> · <router-link class="mono"
            :to="{ path: '/cong-viec', query: { du_an: n.duAn, bead: n.bead } }">{{ n.duAn }}/{{ n.bead }}</router-link>
          </template><template v-else-if="n.duAn"> · {{ n.duAn }}</template></template>
        </template>
      </span>
      <span>Tạo {{ ngayGio(ky.tao_luc) }}</span>
      <span class="ku-qt" title="Độ quan trọng 0–1">Quan trọng <i><b :style="{ width: qt * 100 + '%' }"></b></i>
        {{ qt.toFixed(2) }}</span>
      <span>Dùng {{ ky.so_lan_dung }} lần<template v-if="ky.dung_luc"> · gần nhất
        {{ ngayGio(ky.dung_luc) }}</template></span>
      <span class="mono ku-id">{{ ky.id }}</span>
    </div>
    <p v-if="loi" class="ku-loi" role="alert">{{ loi }}</p>
  </article>
</template>
