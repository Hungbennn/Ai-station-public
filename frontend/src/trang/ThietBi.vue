<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { capNhat } from '../quyen_passkey.js'
import { goiPasskey, nghiLe, quanLy, boQuanLy, hienPhien } from '../passkey.js'
const tt = ref(null), ma = ref(''), ten = ref(''), moi = ref(''), loi = ref(''), ban = ref(false)
let hanMa, yeuCauMoi = null, yeuCauThu = null
const gio = t => t ? new Date(t * 1000).toLocaleString('vi-VN', { timeZone: 'Asia/Ho_Chi_Minh' }) : 'Chưa dùng'
async function tai() { tt.value = await goiPasskey('trang-thai'); capNhat(tt.value) }
async function lam(fn) {
  if (ban.value) return
  ban.value = true; loi.value = ''
  try { await fn(); await tai() } catch (e) { loi.value = e.message }
  finally { ban.value = false }
}
async function dangKy() {
  const code = ma.value; ma.value = ''
  await lam(() => nghiLe('dang-ky', { ma: code, ten: ten.value }))
}
async function them() {
  await lam(async () => {
    moi.value = ''
    yeuCauMoi ||= { ma_thao_tac: crypto.randomUUID() }
    const r = await quanLy('moi', yeuCauMoi, { hanhDong: 'Thêm thiết bị', dich: 'Tài khoản Đại ca' })
    yeuCauMoi = null
    if (!r.ma) throw new Error('Yêu cầu đã cấp mã. Nếu mất mã, bấm Thêm thiết bị để tạo yêu cầu mới.')
    moi.value = r.ma
    clearTimeout(hanMa); hanMa = setTimeout(() => { moi.value = '' }, 600000)
  })
}
async function thu(k) {
  await lam(async () => {
    if (yeuCauThu?.id !== k.id) yeuCauThu = { id: k.id, ma_thao_tac: crypto.randomUUID() }
    await quanLy('thu-hoi', yeuCauThu,
      { hanhDong: 'Thu hồi thiết bị và các phiên của nó', dich: `${k.ten} (${k.id})` })
    yeuCauThu = null
  })
}
onMounted(() => lam(async () => {}))
onUnmounted(() => { boQuanLy(); yeuCauMoi = null; yeuCauThu = null; ma.value = ''; moi.value = ''; clearTimeout(hanMa) })
</script>
<template>
  <div class="dau-trang"><div><div class="duong-dan">Đại ca / Thiết bị đã đăng ký</div>
    <h1>Thiết bị</h1><p>Cửa ghi dashboard bằng passkey</p></div></div>
  <p v-if="loi" role="alert" class="loi-chung">{{ loi }}</p>
  <section class="the pk-bao">
    <strong>{{ hienPhien(tt) }}</strong>
    <p v-if="tt && !tt.thiet_bi.length">Chưa có passkey: chỉ TẠM DỪNG và Estop. Đăng ký bên dưới để mở cửa ghi.</p>
    <p>Thêm hoặc thu hồi luôn cần chạm lại. Tin ban đêm được gom gửi buổi sáng.</p>
    <p v-if="tt?.cho_gui">Cảnh báo đang chờ gửi: {{ tt.cho_gui }}</p>
    <button v-if="tt?.thiet_bi.length && !tt.con_giay" class="nut" :disabled="ban"
      @click="lam(() => nghiLe('phien'))">Xác nhận phiên 8 giờ</button>
  </section>
  <section v-if="tt?.thiet_bi.length" class="the">
    <div class="pk-hang"><h2>Thiết bị đã đăng ký <span class="chip">{{ tt.thiet_bi.length }}</span></h2>
      <button class="nut chinh" :disabled="ban" @click="them">Thêm thiết bị</button></div>
    <div class="bang-cuon"><table class="bang"><thead><tr><th>Tên gợi nhớ</th><th>Đăng ký</th>
      <th>Dùng gần nhất</th><th>Thao tác</th></tr></thead><tbody>
      <tr v-for="k in tt.thiet_bi" :key="k.id"><td>{{ k.ten }}</td><td>{{ gio(k.tao) }}</td><td>{{ gio(k.dung) }}</td>
        <td><button class="nut nguy" :disabled="ban || tt.thiet_bi.length <= 1" @click="thu(k)">Thu hồi</button></td>
      </tr></tbody></table></div>
    <p>Một passkey đồng bộ có thể dùng trên nhiều máy; thu hồi sẽ mất quyền trên mọi bản sao cùng passkey.</p>
    <p v-if="tt.thiet_bi.length <= 1">Không thể thu hồi passkey cuối ở đây; dùng khôi phục trên máy B.</p>
  </section>
  <section v-if="moi" class="the pk-bao" aria-live="polite"><h2>Mã mời thiết bị</h2>
    <code class="pk-lenh">{{ moi }}</code><p>Dùng một lần, hết hạn 10 phút. Nhập ở trang Thiết bị trên máy mới.</p>
    <p>Không gửi vào chat, chụp ảnh hay lưu mã. QR xác thực bằng điện thoại do trình duyệt cung cấp.</p>
    <button class="nut" @click="moi = ''">Ẩn mã</button></section>
  <div class="pk-luoi">
    <section class="the"><span class="pk-buoc">BƯỚC 1 · TẠI MÁY B</span><h2>Lấy mã đăng ký</h2>
      <p>Đại ca mở Terminal trên máy B, chạy lệnh rồi làm theo hướng dẫn.</p>
      <code class="pk-lenh">tram chu passkey cap-ma</code><p>Mã dùng một lần, hết hạn 10 phút.</p></section>
    <form class="the" @submit.prevent="dangKy"><span class="pk-buoc">BƯỚC 2 · TRÊN THIẾT BỊ NÀY</span>
      <h2>Đăng ký cho Đại ca</h2><p>Thiết bị cần dùng đúng tài khoản Tailscale của Đại ca.</p>
      <label class="pk-truong">Mã từ máy B hoặc thiết bị cũ<input v-model="ma" type="password"
        autocomplete="off" required :disabled="ban"></label>
      <label class="pk-truong">Tên gợi nhớ<input v-model="ten" maxlength="80" required :disabled="ban"></label>
      <button class="nut chinh" :disabled="ban">Tạo passkey</button></form>
  </div>
  <section class="the"><h2>Mất hết thiết bị hoặc nghi bị lộ?</h2>
    <p>Đại ca mở Terminal trên máy B. Gõ dong-y sẽ thu hồi mọi passkey, phiên, mã cũ.</p>
    <code class="pk-lenh">tram chu passkey khoi-phuc</code></section>
</template>
<style scoped>
.the { padding: 26px; margin-bottom: 18px; }
.pk-luoi { display: grid; grid-template-columns: 1fr 1.1fr; gap: 18px; }
.pk-truong { display: flex; flex-direction: column; gap: 7px; margin: 16px 0; }
.pk-truong input { padding: 12px; border: 1px solid var(--vien); border-radius: 8px; font: inherit; }
.pk-lenh { display: block; padding: 14px; background: var(--nen-lenh); color: var(--chu-lenh); border-radius: 8px; overflow-wrap: anywhere; }
.pk-hang { display: flex; justify-content: space-between; gap: 16px; align-items: center; }
.pk-bao { background: var(--nen-canh-bao); }
.bang-cuon { overflow-x: auto; }
@media (max-width: 1100px) { .pk-luoi { grid-template-columns: 1fr; } }
</style>
