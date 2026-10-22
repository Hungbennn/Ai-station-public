<script setup>
import { computed } from 'vue'
import { doiCuoi } from '../../luat_lich_su_tu_dong.js'
import { DIEU_KIEN, LENH, doiCongTac, hoiCongTac } from '../../luat_trang_tu_dong.js'
import { lyDoKhoaGhi } from '../../luat_tu_dong.js'
import BieuTuong from '../BieuTuong.vue'
import CongTac from './CongTac.vue'
import { dungGhiTuDong } from './ghi_tu_dong.js'
import { dungSuaLenh } from './sua_lenh.js'

// Khối "Cài đặt" (mockup veCaiDat, anh-tu-dong.png, anh-tu-dong-sua-lenh.png, anh-hr-codex-khoa.png): công tắc tự
// merge, 2 điều kiện "luôn bật" không có nút (D71), 3 nút điều kiện, dòng "cấu trúc DB — luôn chờ Đại ca" (D76),
// 3 lệnh (xem / sửa, Lưu hỏi lại), tự deploy (khoá khi chưa đủ 3 lệnh, D73). Lỗi của máy chủ hiện tại chỗ; 409 →
// "Cài đặt đã đổi — tải lại" + nút Tải lại, form sửa lệnh giữ bản chụp lúc mở và giữ nháp (Codex Q9, `sua_lenh.js`).
const props = defineProps({ ten: { type: String, required: true }, dl: { type: Object, required: true },
  laDaiCa: { type: Boolean, default: false }, taiLai: { type: Function, required: true } })
const emit = defineEmits(['xem-lich-su'])
const g = dungGhiTuDong(() => props.dl, props.taiLai, () => props.ten)
const s = dungSuaLenh(() => props.dl, g, props.taiLai)
const cd = computed(() => props.dl.cai_dat)
const lyDo = computed(() => lyDoKhoaGhi(props.dl, props.laDaiCa))
const khoa = computed(() => Boolean(lyDo.value) || g.dangGui.value)
const thieuLenh = computed(() => !props.dl.du_lenh && !cd.value.tu_deploy)
const doi = (ma, bat) => g.luu(doiCongTac(ma, bat), hoiCongTac(ma, bat, props.ten))
async function taiLaiXungDot() {
  if (s.dangSua.value) return s.taiLaiGoc()
  if (await props.taiLai() !== true) return
  g.loi.value = ''
  g.xungDot.value = false
}
const conTram = (ma) => (s.doiChieu.value && s.doiChieu.value[ma] !== s.o[ma] ? s.doiChieu.value[ma] || 'trống' : '')
</script>

<template>
  <section class="the">
    <h3 class="td-h">Cài đặt</h3>
    <p v-if="lyDo" class="nho">{{ lyDo }}</p>
    <p v-if="g.loi.value && !s.dangSua.value" class="loi" role="alert">{{ g.loi.value }}
      <button v-if="g.xungDot.value" type="button" class="nut" @click="taiLaiXungDot">Tải lại</button></p>
    <div class="cd-hang chinh"><span class="ten">Tự merge</span>
      <span class="mo-ta">Mặc định tắt. Bật: trạm tự gộp PR của chính nó khi đủ mọi điều kiện dưới đây.</span>
      <span class="ben-phai"><CongTac :bat="cd.tu_merge" :khoa="khoa" nhan="Tự merge" :ly-do="lyDo"
                                       @doi="doi('tu_merge', $event)" /></span></div>
    <div class="cd-nhom">Điều kiện — thiếu một thì chờ Đại ca</div>
    <div v-for="d in DIEU_KIEN" :key="d.ma" class="cd-hang" :class="{ khoa: d.khoa }">
      <span class="ten">{{ d.ten }}</span><span class="mo-ta">{{ d.mo_ta }}</span>
      <span v-if="d.khoa" class="ben-phai chip khoa"><BieuTuong ten="khoa" />luôn bật</span>
      <span v-else class="ben-phai"><CongTac :bat="cd.dieu_kien[d.ma]" :khoa="khoa" :nhan="d.ten" :ly-do="lyDo"
                                             @doi="doi(d.ma, $event)" /></span>
    </div>
    <div class="cd-hang khoa"><span class="ten">Cấu trúc DB, xoá dữ liệu</span>
      <span class="mo-ta">Luôn chờ Đại ca, kể cả khi tắt nút hàng rào</span>
      <span class="ben-phai chip tt-loi khoa"><BieuTuong ten="khoa" />luôn chờ Đại ca</span></div>
    <div class="cd-nhom">Deploy — 3 lệnh của dự án</div>
    <div v-if="s.dangSua.value" class="lenh-ds">
      <label v-for="l in LENH" :key="l.ma" class="lenh-o">
        <span class="nhan">{{ l.ten }}<span class="nho">{{ l.goi_y }}</span></span>
        <input v-model="s.o[l.ma]" class="o" spellcheck="false" autocomplete="off" maxlength="500">
        <span v-if="conTram(l.ma)" class="nho">Đang lưu ở trạm: <code>{{ conTram(l.ma) }}</code></span></label>
      <p class="nho">Mỗi lệnh chạy trên máy B dưới tài khoản trạm, trong bản sạch của nhánh chính, không qua shell.
        Không dán mật khẩu hay token vào lệnh.</p>
      <div class="lenh-nut">
        <button type="button" class="nut chinh" :disabled="khoa" @click="s.luu">Lưu 3 lệnh</button>
        <button type="button" class="nut" @click="s.dong">Huỷ</button>
        <span v-if="g.loi.value" class="loi-tai-cho" role="alert">{{ g.loi.value }}</span>
        <button v-if="g.xungDot.value" type="button" class="nut" @click="taiLaiXungDot">Tải lại</button></div>
    </div>
    <div v-else class="lenh-ds">
      <div v-for="l in LENH" :key="l.ma" class="lenh-o">
        <span class="nhan">{{ l.ten }}<span class="nho">{{ l.goi_y }}</span></span>
        <code v-if="cd.lenh[l.ma]">{{ cd.lenh[l.ma] }}</code><code v-else class="trong">chưa khai</code></div>
      <div class="lenh-nut"><button type="button" class="nut" :disabled="khoa" :title="lyDo || null"
                                    @click="s.mo">Sửa 3 lệnh</button></div>
    </div>
    <div class="cd-hang chinh"><span class="ten">Tự deploy</span>
      <span class="mo-ta">Mặc định tắt: trạm merge xong thì báo "sẵn sàng deploy" và chờ Đại ca bấm. Bật: trạm tự
        deploy ngay sau khi merge.<b v-if="!dl.du_lenh"> Chưa khai đủ 3 lệnh.</b></span>
      <span class="ben-phai"><CongTac :bat="cd.tu_deploy" :khoa="khoa || thieuLenh" nhan="Tự deploy"
                                       :ly-do="lyDo || (thieuLenh ? 'Chưa khai đủ 3 lệnh' : '')"
                                       @doi="doi('tu_deploy', $event)" /></span></div>
    <div class="cd-chan">{{ doiCuoi(dl.lich_su_doi) }}
      <button v-if="dl.lich_su_doi.length" type="button" @click="emit('xem-lich-su')">Xem lịch sử đổi</button></div>
  </section>
</template>
