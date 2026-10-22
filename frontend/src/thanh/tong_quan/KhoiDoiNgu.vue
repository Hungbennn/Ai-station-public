<script setup>
import { computed } from 'vue'
import { nhanTrangThai } from '../../luat_doi_ngu.js'
import { hanMucThapNhat, tenKhe } from '../../luat_han_muc.js'
import { demTrangThai } from '../../luat_tong_quan.js'
import Chibi from '../Chibi.vue'

// Khối "Đội ngũ" (mockup trang-tong-quan.js khoiDoiNgu): chibi từng khe, chip đếm trạng thái, hạn mức 5 giờ thấp nhất.
const props = defineProps({ doiNgu: { type: Object, default: null }, bayGio: { type: Date, required: true } })
const khe = computed(() => (props.doiNgu && props.doiNgu.khe) || [])
const dem = computed(() => demTrangThai(khe.value))
const thap = computed(() => hanMucThapNhat(khe.value, props.bayGio))
const mo = (k) => k.trang_thai === 'tat' || k.trang_thai === 'mat_ket_noi'
</script>

<template>
  <section class="the">
    <h3 class="tieu-de-khoi">Đội ngũ <router-link class="lk-phai" to="/doi-ngu">Mở Đội ngũ AI →</router-link></h3>
    <p v-if="doiNgu && doiNgu.bat === false" class="nho">Kho phiếu chưa bật</p>
    <template v-else>
      <div class="tq-chibi">
        <router-link v-for="k in khe" :key="k.khe_id" to="/doi-ngu" :title="`${tenKhe(k)} · ${nhanTrangThai(k)}`">
          <Chibi :khe-id="k.khe_id" :mo="mo(k)" /><span>{{ tenKhe(k) }}</span>
        </router-link>
      </div>
      <div class="tq-chip">
        <span v-for="c in dem" :key="c.lop" class="chip" :class="c.lop">{{ c.chu }} · {{ c.n }}</span>
      </div>
      <p v-if="thap" class="tq-thap">
        Hạn mức thấp nhất: <b>{{ tenKhe(thap.khe) }}</b> — 5 giờ còn <b>{{ thap.con }}%</b>, reset {{ thap.reset }}
      </p>
    </template>
  </section>
</template>
