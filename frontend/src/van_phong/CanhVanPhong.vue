<script setup>
import { useLoop, useTres } from '@tresjs/core'
import { nextTick, onUnmounted, shallowRef, watch } from 'vue'
import { dungCanh, huyCanh, taoAnhSang } from './dung_canh.js'
import { chieuNhan, gocSan, khit } from './khung_nhin.js'
import { chuyenDongNv } from './nhan_vat_3d.js'

// Nội dung dưới <TresCanvas> (mockup van-phong.js dungVanPhong, D20): camera trực giao ở (40, 40, 40) nhìn gốc,
// ánh sáng + phòng + đồ đạc + nhân vật dựng bằng three thuần gắn qua <primitive>. Bấm → emit('chon', chon);
// toạ độ 2D các điểm neo nhãn tính khi đổi cỡ / đổi dữ liệu (không mỗi khung hình) → emit('chieu').
const props = defineProps({
  boTri: { type: Object, required: true },
  nhan: { type: Array, required: true },
  chuyenDong: { type: Boolean, default: true },
})
const emit = defineEmits(['chon', 'chieu'])
const { sizes, invalidate, renderer } = useTres()
const cam = shallowRef(null)
const anhSang = taoAnhSang()
const canh = shallowRef(null)
let dong = []

// Dựng lại khi mặt bằng đổi (trang chỉ thay boTri khi nội dung khác); huỷ cảnh cũ sau khi Tres đã gỡ nó.
function dung() {
  const cu = canh.value
  const moi = dungCanh(props.boTri)
  dong = moi.dong
  canh.value = moi.goc
  if (cu) nextTick(() => huyCanh(cu))
  invalidate()
}
dung()
watch(() => props.boTri, dung)

// Khít khung SAU khi camera đã có position + lookAt (prop :look-at bắt buộc — bài học 2c T8); khit() tự gọi
// updateMatrixWorld(). Rồi chiếu điểm neo nhãn ra toạ độ khung.
function capNhatKhung() {
  const c = cam.value
  const w = sizes.width.value
  const h = sizes.height.value
  if (!c || !w || !h) return
  Object.assign(c, khit(c, gocSan(props.boTri.phong), w, h))
  c.updateProjectionMatrix()
  emit('chieu', chieuNhan(c, w, h, props.nhan, props.boTri.nhanVat))
  invalidate()
}
watch([cam, sizes.width, sizes.height, () => props.nhan], capNhatKhung, { immediate: true })

useLoop().onBeforeRender(({ elapsed }) => {
  if (props.chuyenDong) for (const m of dong) chuyenDongNv(m, elapsed)
})

// Sự kiện con trỏ của Tres nổi bọt lên primitive; đi ngược parent từ vật trúng tia để tìm userData.chon.
function timChon(o) {
  let x = o
  while (x && !x.userData?.chon) x = x.parent
  return x ? x.userData.chon : null
}
function bam(e) {
  const c = timChon(e.object ?? e.intersection?.object)
  if (c) emit('chon', c)
}
function troChuot(bat) {
  if (renderer?.domElement) renderer.domElement.style.cursor = bat ? 'pointer' : ''
}

onUnmounted(() => {
  huyCanh(canh.value)
  huyCanh(anhSang)
})
</script>

<template>
  <TresOrthographicCamera ref="cam" :position="[40, 40, 40]" :look-at="[0, 0, 0]" :near="0.1" :far="400" />
  <primitive :object="anhSang" />
  <primitive :object="canh" @click="bam" @pointerenter="troChuot(true)" @pointerleave="troChuot(false)" />
</template>
