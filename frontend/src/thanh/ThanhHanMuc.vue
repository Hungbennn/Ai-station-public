<script setup>
import { computed } from 'vue'
import '../kieu/khe.css'
import { oHanMuc } from '../luat_han_muc.js'

// Một dòng của lưới `.han-muc` (mockup trang.js thanhHm): tên cửa sổ | thanh | "còn x% · reset hh:mm".
const props = defineProps({ ten: { type: String, required: true }, cuaSo: { type: Object, default: null } })
const o = computed(() => oHanMuc(props.cuaSo))
</script>

<template>
  <span>{{ ten }}</span>
  <div class="thanh-hm" role="img" :aria-label="`${ten}: ${o.chu}`"><i v-if="o.con !== null" :class="o.lop"
    :style="{ width: `${o.rong}%` }" /></div>
  <span :class="{ nho: o.con === null }">{{ o.chu }}</span>
</template>
