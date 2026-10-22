<script setup>
import { CHU_CHI_QUET_THU } from '../../luat.js'
import { cauBatGhi, chuHangRao, lenhDuAn } from '../../luat_cai_dat.js'
import KhoiCaiDat from './KhoiCaiDat.vue'

// Dự án đã thêm (mockup trang-cai-dat.js `duAn`). `ds` đã ghép `chi_quet_thu` từ /api/du-an (D37) → mờ + chip.
defineProps({ ds: { type: Array, required: true } })
</script>

<template>
  <KhoiCaiDat tieu-de="Dự án đã thêm" :lenh="lenhDuAn(ds)">
    <template #phu>{{ ds.length }} dự án · <span class="mono">du-an/*.yaml</span></template>
    <div class="cd-du-an">
      <div v-for="d in ds" :key="d.ten" class="cd-da" :class="{ mo: d.chi_quet_thu }">
        <div class="cd-da-dau">
          <strong>{{ d.ten }}</strong>
          <span v-if="d.chi_quet_thu" class="chip" :title="CHU_CHI_QUET_THU">chỉ quét thử</span>
        </div>
        <dl>
          <dt>Đường dẫn</dt><dd class="mono">{{ d.duong_dan }}</dd>
          <dt>Nhánh chính</dt><dd class="mono">{{ d.nhanh_chinh }}</dd>
          <dt>GitNexus</dt>
          <dd><span v-if="d.gitnexus" class="mono">{{ d.gitnexus }}</span><span v-else class="nho">không</span></dd>
          <dt>Lệnh được phép</dt>
          <dd class="tq-chip"><span v-for="l in d.lenh_cho_phep" :key="l" class="chip mono">{{ l }}</span></dd>
          <dt>Hàng rào</dt>
          <dd>
            <div v-for="h in d.hang_rao" :key="h.loai">
              <span class="chip mono">{{ h.loai }}</span> <span class="nho">{{ chuHangRao(h) }}</span>
            </div>
          </dd>
          <dt>Môi trường kiểm</dt><dd>{{ d.moi_truong_kiem ? 'có' : 'chưa' }}</dd>
        </dl>
        <p v-if="d.loi" class="canh-bao">{{ d.loi }}</p>
      </div>
      <p v-if="!ds.length" class="nho">Chưa thêm dự án nào.</p>
    </div>
    <template #sau-lenh>
      <span class="nho">Bật ghi (D31): {{ cauBatGhi(ds) }}</span>
    </template>
  </KhoiCaiDat>
</template>
