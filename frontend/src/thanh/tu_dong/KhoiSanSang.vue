<script setup>
import { computed } from 'vue'
import { CHUA_CO, sanSang } from '../../luat_trang_tu_dong.js'
import { dungGhiTuDong } from './ghi_tu_dong.js'

// Khối "Sẵn sàng deploy" (mockup veSanSang, anh-tu-dong.png): một hàng cho commit mới nhất (TM-3 gộp nhiều merge)
// + nút Deploy có hỏi lại, hoặc hàng "đang deploy". Deploy khoá khi estop / thiếu lệnh / cửa ghi; tạm dừng thì không.
const props = defineProps({ ten: { type: String, required: true }, dl: { type: Object, required: true },
  laDaiCa: { type: Boolean, default: false }, taiLai: { type: Function, required: true } })
const s = computed(() => sanSang(props.dl, props.laDaiCa))
const g = dungGhiTuDong(() => props.dl, props.taiLai, () => props.ten)
</script>

<template>
  <section class="the ss-deploy">
    <h3 class="td-h">Sẵn sàng deploy <span class="nho">{{ s.phu }}</span></h3>
    <div v-if="s.chuaCo" class="ss-rong">{{ CHUA_CO }}</div>
    <div v-else-if="s.rong" class="ss-rong">{{ s.rong }}</div>
    <div v-else-if="s.dangDeploy" class="ss-hang">
      <div><div class="tieu-de">{{ s.dangDeploy.cho ? 'Chờ trạm nhận bản' : 'Đang deploy bản' }}
        <span class="mono">{{ s.dangDeploy.commit }}</span></div>
        <div class="nho">{{ s.dangDeploy.nguon }} · {{ s.dangDeploy.cho ? 'bấm lúc' : 'bắt đầu' }}
          {{ s.dangDeploy.luc }}</div></div>
      <button type="button" class="nut chinh" disabled>{{ s.dangDeploy.cho ? 'Đã gửi…' : 'Đang deploy…' }}</button>
      <div class="chu-thich nho">Trạm chạy lệnh deploy → lệnh kiểm còn sống; hỏng thì tự lùi và báo Telegram.</div>
    </div>
    <div v-else class="ss-hang">
      <div>
        <div class="tieu-de">Bản <span class="mono">{{ s.ban.commit }}</span> — gồm {{ s.ban.soMerge }} việc đã
          merge</div>
        <div class="nho">{{ s.ban.bead ? `${s.ban.bead} · ` : '' }}merge cuối {{ s.ban.luc }}<template
          v-if="s.ban.dangChay"> · bản đang chạy <span class="mono">{{ s.ban.dangChay }}</span></template></div>
      </div>
      <button type="button" class="nut chinh" :disabled="Boolean(s.lyDo) || g.dangGui.value" :title="s.lyDo || null"
              @click="g.deploy(dl.san_sang.commit)">{{ g.dangGui.value ? 'Đang gửi…' : 'Deploy' }}</button>
      <div class="chu-thich nho">Trạm chạy lệnh deploy → lệnh kiểm còn sống; hỏng thì tự lùi<template
        v-if="s.ban.dangChay"> về <span class="mono">{{ s.ban.dangChay }}</span></template> và báo Telegram.<b
        v-if="s.lyDo">{{ ` ${s.lyDo}.` }}</b></div>
      <p v-if="g.loi.value" class="loi chu-thich" role="alert">{{ g.loi.value }}</p>
    </div>
  </section>
</template>
