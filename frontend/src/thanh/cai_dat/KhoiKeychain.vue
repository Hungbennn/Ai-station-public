<script setup>
import { LENH_KEYCHAIN, nhanKeychain } from '../../luat_cai_dat.js'
import KhoiCaiDat from './KhoiCaiDat.vue'

// Keychain (mockup trang-cai-dat.js `kc`): chỉ có / chưa có / không kiểm được — không bao giờ hiện giá trị.
defineProps({ ds: { type: Array, required: true } })
</script>

<template>
  <KhoiCaiDat tieu-de="Keychain" phu="chỉ hiện có / chưa có — không bao giờ hiện giá trị" :lenh="LENH_KEYCHAIN">
    <ul class="tq-ds">
      <li v-for="k in ds" :key="k.ten">
        <span class="mono">{{ k.ten }}</span>
        <span />
        <span class="chip" :class="nhanKeychain(k.trang_thai).lop">{{ nhanKeychain(k.trang_thai).chu }}</span>
      </li>
    </ul>
  </KhoiCaiDat>
</template>
