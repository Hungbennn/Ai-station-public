<script setup>
import { computed } from 'vue'
import '../kieu/khe.css'
import { mauKhe } from '../mau_khe.js'

// Avatar chibi SVG (mockup chung.js `chibi`), màu theo khe_id (mau_khe.js). Khe tắt / mất kết nối vẽ mờ.
const props = defineProps({ kheId: { type: String, required: true }, mo: { type: Boolean, default: false } })
const mau = computed(() => mauKhe(props.kheId))
</script>

<template>
  <svg class="chibi" viewBox="0 0 46 46" aria-hidden="true" focusable="false">
    <g :opacity="mo ? 0.4 : 1">
      <ellipse cx="23" cy="41" rx="10" ry="2.6" fill="#3a241822" />
      <rect x="17.5" y="32" width="4" height="8" rx="2" fill="#2b2523" />
      <rect x="24.5" y="32" width="4" height="8" rx="2" fill="#2b2523" />
      <path d="M15 34 L16.5 22 Q23 19 29.5 22 L31 34 Z" :fill="mau.than" />
      <circle cx="23" cy="15" r="8" fill="#f2c9a3" />
      <path d="M14.8 14.5 A8.3 8.3 0 0 1 31.2 14.5 Q27 9.5 23 10.5 Q18 9.8 14.8 14.5 Z" :fill="mau.toc" />
    </g>
  </svg>
</template>
