<script setup>
import { computed } from 'vue'
import { duocGhi } from '../../quyen_passkey.js'
import { kho } from '../../kho.js'
import { khoaDeploy, sanSangDeploy } from '../../luat_phe_duyet.js'
import { dungGhiTuDong } from '../tu_dong/ghi_tu_dong.js'

// Thẻ "sẵn sàng deploy" ở Phê duyệt (spec tu-deploy "Hiện ở trang Phê duyệt", D101, D129). Mockup 2026-10-18 không vẽ
// trang này → khung `.the-duyet` sẵn có (D36). Nút Deploy dùng đúng hàm ghi của trang Tự động (`ghi_tu_dong.js`: cùng
// hộp hỏi, cùng thân {ma_thao_tac, expected_version: "", expected_commit}, 409/422 hiện câu máy chủ tại chỗ) và cùng
// khoá (`khoaDeploy`); thành công → emit('doi') để trang tải lại. Link sang trang Tự động để xem đủ chi tiết.
const props = defineProps({
  muc: { type: Object, required: true },
  khoa: { type: Boolean, default: false },
  chuKhoa: { type: String, default: '' },
})
const emit = defineEmits(['doi'])
const t = computed(() => sanSangDeploy(props.muc))
const laDaiCa = computed(() => duocGhi(kho.trangThai))
const lyDo = computed(() => khoaDeploy(props.muc, kho.tuDong, laDaiCa.value))
const g = dungGhiTuDong(() => props.muc.chi_tiet, async () => emit('doi'), () => props.muc.du_an)
</script>

<template>
  <article class="the the-duyet">
    <div>
      <div class="tren"><span class="chip">{{ muc.du_an }}</span><span class="chip pr-mo">sẵn sàng deploy</span></div>
      <div class="tieu-de">{{ t.tieuDe }}</div>
      <div v-if="t.moTa" class="nho">{{ t.moTa }}</div>
    </div>
    <div class="hanh-dong">
      <button type="button" class="nut chinh" :disabled="Boolean(lyDo) || g.dangGui.value" :title="lyDo || null"
              @click="g.deploy(muc.chi_tiet.commit)">{{ g.dangGui.value ? 'Đang gửi…' : 'Deploy' }}</button>
      <router-link class="nut" :to="t.den">Mở trang Tự động</router-link>
    </div>
    <p v-if="lyDo" class="nho dong-day">{{ lyDo }}</p>
    <p v-if="g.loi.value" class="loi dong-day" role="alert">{{ g.loi.value }}</p>
  </article>
</template>
