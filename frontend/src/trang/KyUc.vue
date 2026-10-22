<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { doc } from '../api.js'
import { duocGhi } from '../quyen_passkey.js'
import { kho } from '../kho.js'
import { locKyUc, tongPhamVi } from '../nho.js'
import BieuTuong from '../thanh/BieuTuong.vue'
import DauTrang from '../thanh/DauTrang.vue'
import OGhiNho from '../thanh/OGhiNho.vue'
import SuKienNho from '../thanh/SuKienNho.vue'
import TheKyUc from '../thanh/TheKyUc.vue'
import '../kieu/ky-uc.css'

// Màn Ký ức (mockup trang-ky-uc.js veKyUc, D36/D39; spec 1b lát 1b-3, spec 2 §7 `/api/nho/*`): xem / tìm / xoá /
// ghi tay; lọc phạm vi + ký ức thăng cấp đang chờ (#19) gửi lên server; ô tìm lọc phía trình duyệt. Quyền: server.
const ds = ref([])
const cacPhamVi = ref([])
const tong = ref(0)
const suKien = ref([])
const phamVi = ref('')
const chiCho = ref(false)
const tim = ref('')
const bao = ref('')
const chan = ref(0)                // 403 | 503 → thẻ chặn thay cả lưới
const loi = ref('')
const laDaiCa = computed(() => duocGhi(kho.trangThai))
const duAn = computed(() => (kho.trangThai ? kho.trangThai.du_an.map((d) => d.ten) : []))
const hien = computed(() => locKyUc(ds.value, tim.value))
const tatCa = computed(() => tongPhamVi(cacPhamVi.value))
const MO_TA = 'Bài học agent và Đại ca để lại cho các lượt sau. Xem, lọc, xoá mềm, ghi tay; '
  + 'ký ức thăng cấp chờ 7 ngày rồi mới có hiệu lực.'

async function tai() {
  const q = new URLSearchParams({ pham_vi: phamVi.value, cho: chiCho.value ? '1' : '0' })
  try {
    const [r, s] = await Promise.all([doc(`/api/nho?${q}`), doc('/api/nho/su-kien')])
    ds.value = r.ky_uc
    cacPhamVi.value = r.pham_vi
    tong.value = r.tong
    suKien.value = s.su_kien
    chan.value = 0
    loi.value = ''
  } catch (e) {
    chan.value = e.status === 403 || e.status === 503 ? e.status : 0
    loi.value = chan.value ? '' : e.message
  }
}
function daXoa(id) {
  bao.value = `Đã xoá mềm ${id}.`
  tai()
}
onMounted(tai)
watch([phamVi, chiCho, () => kho.phienBanNho], tai)
</script>

<template>
  <DauTrang tieu-de="Ký ức" :mo-ta="MO_TA">
    <template #sau-tieu-de><span class="ku-tong">{{ chan ? '—' : tong }}</span></template>
    <template #cong-cu><span class="chip ku-khoa-chip"><BieuTuong ten="khoa" />chỉ Đại ca xem</span></template>
  </DauTrang>
  <div v-if="chan === 403" class="the the-chan" role="alert"><strong>403 · Chỉ Đại ca xem được ký ức</strong>
    <p>Cần danh tính Tailscale của Đại ca. Ký ức của mọi dự án (cả nghiệp vụ và nguồn) không hiện cho ai khác, kể cả
      danh sách phạm vi và sự kiện.</p></div>
  <div v-else-if="chan === 503" class="the the-chan" role="alert"><strong>Không đọc được memory service</strong>
    <p>tram-api chưa nối memory service (vn.tram.nho, 127.0.0.1:7710). Xem Sức khoẻ trạm ở Tổng quan; trang tự tải lại
      khi có sự kiện nho.*.</p>
    <router-link class="nut" to="/tong-quan">Mở Tổng quan</router-link></div>
  <div v-else class="ku-luoi">
    <div class="ku-chinh">
      <section class="the ku-loc">
        <div class="ku-hang">
          <label class="tim ku-tim"><BieuTuong ten="tim" />
            <input v-model="tim" type="search" placeholder="Tìm nội dung, nhãn, mã…" aria-label="Tìm ký ức"></label>
          <label class="gc"><input v-model="chiCho" type="checkbox">Chỉ ký ức thăng cấp đang chờ tự có hiệu lực
            (7 ngày)</label>
        </div>
        <div class="ku-pv" role="group" aria-label="Lọc phạm vi"><span class="nho">Phạm vi</span>
          <button type="button" class="ku-pill" :class="{ chon: !phamVi }" :aria-pressed="!phamVi"
            @click="phamVi = ''">Tất cả <b>{{ tatCa }}</b></button>
          <button v-for="p in cacPhamVi" :key="p.pham_vi" type="button" class="ku-pill mono"
            :class="{ chon: p.pham_vi === phamVi }" :aria-pressed="p.pham_vi === phamVi" @click="phamVi = p.pham_vi"
          >{{ p.pham_vi }} <b>{{ p.so }}</b><em v-if="p.so_cho">{{ p.so_cho }} chờ</em></button>
        </div>
      </section>
      <p v-if="loi" class="loi" role="alert">{{ loi }}</p>
      <p v-if="bao" class="ku-bao" role="status">{{ bao }}</p>
      <p class="nho ku-dem">Đang hiện {{ hien.length }} / {{ tong }} ký ức<template v-if="tim.trim()"> khớp
        “{{ tim.trim() }}”</template> · mới nhất trước · tự tải lại khi có sự kiện <span class="mono">nho.*</span>
        <template v-if="tong > ds.length"> · server chỉ trả 200 ký ức mới nhất, lọc theo phạm vi để xem
          thêm</template></p>
      <div class="ku-ds">
        <TheKyUc v-for="k in hien" :key="k.id" :ky="k" :la-dai-ca="laDaiCa" @doi="daXoa" />
        <div v-if="!hien.length" class="cot-rong">Không có ký ức nào.</div>
      </div>
    </div>
    <aside class="ku-ray">
      <OGhiNho :du-an="duAn" :la-dai-ca="laDaiCa" @doi="tai" />
      <SuKienNho :ds="suKien" />
    </aside>
  </div>
</template>
