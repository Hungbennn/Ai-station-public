<script setup>
// Đầu trang chung của mockup (`.dau-trang`): tiêu đề, một câu mô tả, công cụ bên phải (slot `cong-cu`).
// Slot `tren-tieu-de` (TM-4): đường dẫn "Dự án / <tên>" trên tiêu đề như mockup trang Tự động.
defineProps({ tieuDe: { type: String, required: true }, moTa: { type: String, default: '' } })
</script>

<template>
  <div class="dau-trang">
    <div>
      <slot name="tren-tieu-de" />
      <h1>{{ tieuDe }}<slot name="sau-tieu-de" /></h1>
      <p v-if="moTa">{{ moTa }}</p>
    </div>
    <div v-if="$slots['cong-cu']" class="cong-cu"><slot name="cong-cu" /></div>
  </div>
</template>
