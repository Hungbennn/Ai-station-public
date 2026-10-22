<script setup>
import { computed, ref, watch } from 'vue'
import { duocGhi } from '../quyen_passkey.js'
import { useRoute } from 'vue-router'
import { kho } from '../kho.js'
import { baoTuDong } from '../luat_bao_tu_dong.js'
import { demHong } from '../luat_lich_su_tu_dong.js'
import { CHUA_CO } from '../luat_trang_tu_dong.js'
import { chipTuDong, lyDoKhoaTamDung } from '../luat_tu_dong.js'
import BieuTuong from '../thanh/BieuTuong.vue'
import DauTrang from '../thanh/DauTrang.vue'
import KhoiCaiDat from '../thanh/tu_dong/KhoiCaiDat.vue'
import KhoiChoDaiCa from '../thanh/tu_dong/KhoiChoDaiCa.vue'
import KhoiLichSu from '../thanh/tu_dong/KhoiLichSu.vue'
import KhoiSanSang from '../thanh/tu_dong/KhoiSanSang.vue'
import NganLichSuDoi from '../thanh/tu_dong/NganLichSuDoi.vue'
import { dungGhiTuDong } from '../thanh/tu_dong/ghi_tu_dong.js'
import { dungTaiDuAn } from '../thanh/tu_dong/tai_du_an.js'
import '../kieu/tu-dong.css'

// Trang Tự động của một dự án `#/du-an/<ten>` (mockup 2026-10-18 trang-tu-dong.js, anh-tu-dong.png; spec
// dieu-khien-tu-dong "Trang tự merge/deploy của dự án"). Trái: sẵn sàng deploy, chờ Đại ca, lịch sử; phải: bộ đếm
// hỏng, cài đặt. Khối "agent tự cập nhật việc" của mockup thuộc plan TC — không vẽ. Không phải Đại ca: chỉ xem.
// Codex Q10: dữ liệu và mọi thao tác ràng với tên dự án của route (`tai_du_an.js`, `ghi_tu_dong.js`); đổi dự án thì
// bỏ dữ liệu, lỗi, ngăn lịch sử đổi của dự án cũ; khối Cài đặt / Sẵn sàng dựng lại theo `:key` (form sửa về trống).
const MO_TA = 'Tự merge và tự deploy của dự án này. Mỗi nút ở đây ghi qua cửa ghi có xác thực như các nút khác '
  + 'của dashboard.'
const route = useRoute()
const ten = computed(() => String(route.params.ten))
const { dl, loi, khongCo, tai, doiDuAn } = dungTaiDuAn(() => ten.value)
const xemLichSu = ref(false)
const laDaiCa = computed(() => Boolean(kho.trangThai && kho.trangThai.la_dai_ca))
const coQuyen = computed(() => duocGhi(kho.trangThai))
const g = dungGhiTuDong(() => dl.value, tai, () => ten.value)
watch(ten, () => { xemLichSu.value = false; g.loi.value = ''; doiDuAn() }, { immediate: true })
watch(() => kho.phienBanTuDong, tai)
const bao = computed(() => (dl.value ? baoTuDong(dl.value) : []))
const chip = computed(() => (dl.value ? chipTuDong({ ...dl.value, ...dl.value.cai_dat }, dl.value) : []))
const tamDung = computed(() => Boolean(dl.value && dl.value.tam_dung))
const lyDoTD = computed(() => tamDung.value && !coQuyen.value ? 'Cần đăng ký passkey để Tiếp tục'
  : lyDoKhoaTamDung(dl.value, laDaiCa.value, tamDung.value))
const khoaTD = computed(() => !dl.value || Boolean(lyDoTD.value) || g.dangGui.value)
const dem = computed(() => (dl.value ? demHong(dl.value.dem_hong) : null))
</script>

<template>
  <div v-if="khongCo" class="cho-chot"><strong>Không có dự án này</strong>
    Dự án "{{ ten }}" không có trong du-an/. <router-link to="/du-an">Về trang Dự án</router-link></div>
  <template v-else>
    <DauTrang :tieu-de="`${ten} · Tự động`"
              :mo-ta="MO_TA">
      <template #tren-tieu-de>
        <div class="duong-dan"><router-link to="/du-an">Dự án</router-link> / {{ ten }}</div>
      </template>
      <template #cong-cu>
        <div class="td-cong-cu">
          <div class="hang-chip"><span v-for="c in chip" :key="c.chu" class="chip" :class="c.lop"
                                       :title="c.title || null">{{ c.chu }}</span></div>
          <button type="button" class="nut-estop vang" :class="{ bat: tamDung }" :disabled="khoaTD"
                  :title="lyDoTD || null" @click="g.tamDung(!tamDung)">
            <BieuTuong ten="tam-dung" class="dac" />
            <span>{{ tamDung ? 'Dự án đang tạm dừng' : 'Tạm dừng dự án' }}</span>
          </button>
        </div>
      </template>
    </DauTrang>
    <p v-if="loi" class="loi" role="alert">{{ loi }}</p>
    <p v-if="dl?.ly_do_deploy" class="loi" role="status">{{ dl.ly_do_deploy }}</p>
    <p v-if="g.loi.value" class="loi" role="alert">{{ g.loi.value }}</p>
    <template v-if="dl">
      <div v-for="b in bao" :key="b.tieuDe" class="the td-bao" :class="b.lop">
        <strong>{{ b.tieuDe }}</strong>
        <p><span v-for="(p, i) in b.than" :key="i" :class="{ mono: p[1] }">{{ p[0] }}</span></p>
        <div v-if="b.nut" class="hang-nut">
          <button type="button" class="nut" :disabled="khoaTD" :title="lyDoTD || null"
                  @click="g.tamDung(false)">{{ b.nut }}</button></div>
      </div>
      <div class="td-luoi">
        <div class="td-cot">
          <KhoiSanSang :key="ten" :ten="ten" :dl="dl" :la-dai-ca="coQuyen" :tai-lai="tai" />
          <KhoiChoDaiCa :dl="dl" />
          <KhoiLichSu :dl="dl" />
        </div>
        <div class="td-cot">
          <section class="the"><h3 class="td-h">Deploy hỏng liên tiếp</h3>
            <div v-if="dem" class="dem-hong"><span v-for="(d, i) in dem.den" :key="i" class="den-ss" :class="d" />
              <b>{{ dem.chu }}</b></div>
            <div v-else class="ss-rong">{{ CHUA_CO }}</div>
            <p class="nho">Mỗi lần hỏng trạm tự lùi và báo Telegram. Đủ 3 lần liền thì trạm tự tắt tự deploy. Về 0 khi
              một lần deploy thành công.</p>
          </section>
          <KhoiCaiDat :key="ten" :ten="ten" :dl="dl" :la-dai-ca="coQuyen" :tai-lai="tai"
                      @xem-lich-su="xemLichSu = true" />
        </div>
      </div>
      <NganLichSuDoi v-if="xemLichSu" :du-an="dl.du_an" :ds="dl.lich_su_doi" @dong="xemLichSu = false" />
    </template>
  </template>
</template>
