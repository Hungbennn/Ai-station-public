<script setup>
// Hộp "Vì sao?" khi kéo thẻ giữa cột 1–2 (mockup không vẽ, giữ bố cục cũ; lớp mockup .nen-mo .hop .truong — D36).
import { ref } from 'vue'
import { TEN_HANG } from '../luat.js'

defineProps({ the: { type: Object, required: true }, cot: { type: String, required: true } })
const emit = defineEmits(['huy', 'xac-nhan'])
const viSao = ref('')
</script>

<template>
  <div class="nen-mo" role="dialog" aria-modal="true" aria-labelledby="hop-vi-sao-td" @keydown.esc="emit('huy')">
    <form class="hop" @submit.prevent="emit('xac-nhan', viSao.trim())">
      <h2 id="hop-vi-sao-td">Chuyển {{ the.id }} sang "{{ TEN_HANG[cot] }}"</h2>
      <label class="truong">Vì sao? (tuỳ chọn)
        <textarea v-model="viSao" rows="3" maxlength="2000" autofocus></textarea></label>
      <p class="nho">Bead sẽ được khoá cột (cot-khoa); bộ chấm không lật lại cho tới khi Đại ca gỡ khoá.</p>
      <div class="hang-nut">
        <button class="nut" type="button" @click="emit('huy')">Huỷ</button>
        <button class="nut chinh" type="submit">Chuyển cột</button>
      </div>
    </form>
  </div>
</template>
