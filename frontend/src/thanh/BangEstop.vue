<script setup>
// Băng đỏ dưới thanh trên khi estop bật (mockup index.html `.bang-estop`). Nút "Tiếp tục" gọi lại hàm của ThanhTren.
defineProps({ khoa: { type: Boolean, default: false } })
const emit = defineEmits(['tiep-tuc'])
</script>

<template>
  <div class="bang-estop" role="status">
    <b>Estop đang bật</b> — trạm không giao việc mới, không tự merge, không deploy; khe đang chạy dừng mềm sau lượt
    hiện tại.
    <button type="button" :disabled="khoa" @click="emit('tiep-tuc')">Tiếp tục</button>
  </div>
</template>
