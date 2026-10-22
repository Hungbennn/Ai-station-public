<script setup>
import { duongVe } from '../bieu_tuong.js'

defineProps({ ten: { type: String, required: true } })
</script>

<template>
  <svg class="bieu-tuong" viewBox="0 0 24 24" aria-hidden="true" focusable="false">
    <path v-for="(d, i) in duongVe(ten)" :key="i" :d="d" />
  </svg>
</template>
