<script setup>
// Băng vàng dưới thanh trên khi TẠM DỪNG toàn trạm bật (mockup index.html `.bang-tam-dung`, D101) — có trên mọi trang.
// "Tiếp tục" gọi lại hàm của thanh trên; khoá khi không phải Đại ca hoặc cửa ghi còn tạm (D87), câu giải thích ở title.
defineProps({ khoa: { type: Boolean, default: false }, lyDo: { type: String, default: '' } })
const emit = defineEmits(['tiep-tuc'])
</script>

<template>
  <div class="bang-tam-dung" role="status">
    <span><b>Tự merge · tự deploy đang tạm dừng toàn trạm</b> — trạm vẫn giao việc, kiểm lại, QC và mở PR; chỉ không
      tự merge, không tự deploy. Việc đang deploy dở được làm nốt.</span>
    <button type="button" :disabled="khoa" :title="lyDo" @click="emit('tiep-tuc')">Tiếp tục</button>
  </div>
</template>
