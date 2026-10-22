<script setup>
import { LENH_TELEGRAM, nhanChatId } from '../../luat_cai_dat.js'
import KhoiCaiDat from './KhoiCaiDat.vue'

// Telegram (mockup trang-cai-dat.js `tele`). chat_id chỉ hiện có / chưa có — API không trả giá trị.
defineProps({ tg: { type: Object, required: true } })
</script>

<template>
  <KhoiCaiDat tieu-de="Telegram" :lenh="LENH_TELEGRAM">
    <template #phu>
      khoá <span class="mono">telegram:</span> trong <span class="mono">~/.tram/cau-hinh.yaml</span>
    </template>
    <dl class="cd-dl">
      <dt>chat_id</dt>
      <dd><span class="chip" :class="nhanChatId(tg.co_chat_id).lop">{{ nhanChatId(tg.co_chat_id).chu }}</span></dd>
      <dt>Giờ yên lặng</dt>
      <dd v-if="tg.gio_yen_lang">{{ tg.gio_yen_lang }}</dd>
      <dd v-else class="nho">không đặt</dd>
      <dt>Loại tin</dt>
      <dd class="tq-chip"><span v-for="l in tg.loai_tin || []" :key="l" class="chip">{{ l }}</span></dd>
    </dl>
  </KhoiCaiDat>
</template>
