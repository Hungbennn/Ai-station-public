<script setup>
import { ref } from 'vue'
import { tenKhe } from '../luat_han_muc.js'

// Hộp xác nhận Bật / Tắt khe (lớp chung.css `.nen-mo .hop .truong .hang-nut .nut`, lát 2f F3). Logic giữ như 2b.
defineProps({ khe: { type: Object, required: true }, bat: { type: Boolean, default: false } })
const emit = defineEmits(['huy', 'xac-nhan'])
const viSao = ref('')
</script>

<template>
  <div class="nen-mo" role="dialog" aria-modal="true" aria-labelledby="hop-khe-td" @keydown.esc="emit('huy')">
    <form class="hop" @submit.prevent="emit('xac-nhan', viSao.trim())">
      <h2 id="hop-khe-td">{{ bat ? 'Bật' : 'Tắt' }} khe {{ tenKhe(khe) }} ({{ khe.khe_id }})</h2>
      <p v-if="!bat && khe.phieu" class="canh-bao">Khe đang làm {{ khe.phieu.du_an }}/{{ khe.phieu.bead_id }} — phiếu
        sẽ dừng mềm (lưu phần đã làm, bộ giao việc giao lại cho khe khác).</p>
      <p v-if="!bat" class="nho">Không giao việc mới cho khe này tới khi Đại ca bật lại.</p>
      <label class="truong">Vì sao? (tuỳ chọn)
        <textarea v-model="viSao" rows="2" maxlength="500" autofocus></textarea></label>
      <div class="hang-nut">
        <button class="nut" type="button" @click="emit('huy')">Huỷ</button>
        <button class="nut" :class="bat ? 'chinh' : 'nguy'" type="submit">{{ bat ? 'Bật khe' : 'Tắt khe' }}</button>
      </div>
    </form>
  </div>
</template>
