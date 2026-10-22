<script setup>
import { computed, ref } from 'vue'
import { ngayGio } from '../dinh_dang.js'
import { LOP_SK, NHOM_SK, TEN_SU_KIEN_NHO, nhomCua } from '../nho.js'

// Sự kiện nho.* gần đây (mockup trang-ky-uc.js khoiSuKien, D36): lọc nhóm phía trình duyệt; D39 hiện câu `mo_ta`
// do API dựng, thiếu thì hiện `tom_tat` (JSON cũ, chữ mono).
const props = defineProps({ ds: { type: Array, required: true } })
const nhom = ref('')
const loc = computed(() => props.ds.filter((s) => !nhom.value || nhomCua(s.loai) === nhom.value))
</script>

<template>
  <section class="the ku-sk">
    <h3 class="tieu-de-khoi">Sự kiện ký ức gần đây <span class="nho">{{ ds.length }} / tối đa 50</span></h3>
    <div class="ku-loc-sk" role="group" aria-label="Lọc loại sự kiện">
      <button v-for="[m, ten] in NHOM_SK" :key="m" type="button" class="ku-pill" :class="{ chon: m === nhom }"
        :aria-pressed="m === nhom" @click="nhom = m">{{ ten }}</button>
    </div>
    <ol v-if="loc.length" class="ku-dtg">
      <li v-for="s in loc" :key="s.id">
        <div>
          <span class="mono nho">{{ ngayGio(s.luc) }}</span>
          <span class="chip" :class="LOP_SK[nhomCua(s.loai)]">{{ TEN_SU_KIEN_NHO[s.loai] || s.loai }}</span>
          <span class="nho">
            <router-link v-if="s.bead_id" class="mono"
              :to="{ path: '/cong-viec', query: { du_an: s.du_an, bead: s.bead_id } }"
            >{{ s.du_an }}/{{ s.bead_id }}</router-link>
            <span v-else class="mono">{{ s.du_an }}</span>
          </span>
        </div>
        <p class="ku-mo-ta">{{ s.mo_ta || 'Sự kiện chưa có mô tả.' }}</p>
      </li>
    </ol>
    <p v-else class="nho">Chưa có sự kiện.</p>
  </section>
</template>
