<script setup>
import { computed } from 'vue'
import { CHUA_CO, choDaiCa } from '../../luat_trang_tu_dong.js'

// Khối "Chờ Đại ca" (mockup veCho; spec tu-merge "Thiếu điều kiện thì chờ Đại ca và nói rõ vì sao"): việc không
// được tự merge kèm từng lý do bằng lời của máy chủ (TM-2 `cho_dai_ca`). Xử lý như hôm nay ở Phê duyệt.
const props = defineProps({ dl: { type: Object, required: true } })
const ds = computed(() => choDaiCa(props.dl))
</script>

<template>
  <section class="the">
    <h3 class="td-h">Chờ Đại ca <span class="chip">{{ ds ? ds.length : '—' }}</span>
      <span class="nho">thiếu điều kiện nên không tự merge — xử lý như hôm nay ở Phê duyệt</span></h3>
    <div v-if="!ds" class="ss-rong">{{ CHUA_CO }}</div>
    <ul v-else-if="ds.length" class="ds-cho">
      <li v-for="c in ds" :key="c.bead"><span class="mono">{{ c.bead }}</span><span>{{ c.tieuDe }}</span>
        <span class="ly-do"><span v-for="l in c.lyDo" :key="l.chu" class="chip" :class="l.lop">{{ l.chu }}</span></span>
      </li>
    </ul>
    <div v-else class="ss-rong">Không có việc nào đang chờ.</div>
  </section>
</template>
