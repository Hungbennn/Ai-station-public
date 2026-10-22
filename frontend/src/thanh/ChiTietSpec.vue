<script setup>
import { computed } from 'vue'
import { lenhMayA } from '../luat_spec.js'

// "Spec chờ duyệt" (spec 2 §5.2; spec 4 §7.3): commit đang xem, file, bead đề xuất, lệnh mở trên máy A.
// Lát 2f: giữ logic, đổi sang lớp của mockup (`.bang`, `.bang-cuon`, `.canh-bao`, `.mono`; khối lệnh nền tối) — D36.
const props = defineProps({ muc: { type: Object, required: true } })
const ct = computed(() => props.muc.chi_tiet || {})
const lenh = computed(() => lenhMayA(props.muc, window.location.origin))
</script>

<template>
  <div class="chi-tiet-spec">
    <ul v-if="ct.loi && ct.loi.length" class="canh-bao"><li v-for="l in ct.loi" :key="l">{{ l }}</li></ul>
    <p v-if="ct.commit" class="nho">Nhánh <span class="mono">{{ ct.nhanh }}</span> · commit
      <span class="mono">{{ ct.commit.slice(0, 12) }}</span></p>
    <ul v-if="ct.file && ct.file.length" class="ds-file mono"><li v-for="f in ct.file" :key="f">{{ f }}</li></ul>
    <div v-if="ct.de_xuat && ct.de_xuat.length" class="bang-cuon">
      <table class="bang">
        <thead><tr><th>Khoá</th><th>Tiêu đề</th><th>Loại</th><th>P</th><th>Sau</th><th>Nhãn</th></tr></thead>
        <tbody>
          <tr v-for="b in ct.de_xuat" :key="b.khoa">
            <td class="mono">{{ b.khoa }}</td><td>{{ b.tieu_de }}</td><td>{{ b.loai }}</td><td>P{{ b.uu_tien }}</td>
            <td>{{ (b.phu_thuoc || []).join(', ') }}</td><td>{{ (b.nhan || []).join(', ') }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <p class="nho">Mở trên máy A — dán vào phiên Claude (skill chỉ đọc, không duyệt thay Đại ca):</p>
    <pre v-if="lenh" class="lenh">{{ lenh }}</pre>
    <p class="nho">Duyệt xong: Đại ca tạo PR từ nhánh trên tại đúng commit này rồi merge — bead con chỉ được giao
      khi commit đã vào nhánh chính.</p>
  </div>
</template>
