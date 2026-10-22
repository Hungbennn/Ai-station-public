<script setup>
// Công tắc `role="switch"` (mockup them.css `.cong-tac`, design D-10). Chỉ phát `doi` với giá trị mới; khối cha hỏi
// lại và gửi. Khoá kèm câu giải thích ở `title` (máy chủ vẫn là nơi từ chối).
defineProps({ bat: { type: Boolean, default: false }, khoa: { type: Boolean, default: false },
  nhan: { type: String, required: true }, lyDo: { type: String, default: '' } })
const emit = defineEmits(['doi'])
</script>

<template>
  <button type="button" class="cong-tac" role="switch" :aria-checked="bat ? 'true' : 'false'" :aria-label="nhan"
          :disabled="khoa" :title="lyDo || null" @click="emit('doi', !bat)" />
</template>
