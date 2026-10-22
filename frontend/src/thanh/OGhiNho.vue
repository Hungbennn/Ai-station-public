<script setup>
import { computed, ref } from 'vue'
import { ghi, taoMaThaoTac, thanGhi } from '../api.js'
import { LOAI_PHAM_VI, dungPhamVi, ngoaiDuAn, tachNhan } from '../nho.js'

// Đại ca ghi tay (mockup trang-ky-uc.js formGhi, D36; spec 1b §6.1): mọi phạm vi. Server ép /du-an/X/cach-lam chạm
// luật về nghiep-vu; /vai/*, /chung chạm luật của bất kỳ dự án nào thì từ chối (nho.tu_choi) — trình duyệt không kiểm.
const props = defineProps({ duAn: { type: Array, default: () => [] }, laDaiCa: { type: Boolean, default: false } })
const emit = defineEmits(['doi'])
const noiDung = ref('')
const loai = ref('du-an-cach-lam')
const duAnChon = ref('')
const vai = ref('')
const nhan = ref('')
const dangGui = ref(false)
const thongBao = ref('')
const loi = ref('')
let ma = taoMaThaoTac()            // giữ mã khi gửi lại sau lỗi mạng; đổi mã khi đã ghi xong
const phamVi = computed(() => dungPhamVi(loai.value, duAnChon.value, vai.value))

async function gui() {
  if (!phamVi.value || !noiDung.value.trim() || dangGui.value) return
  dangGui.value = true
  loi.value = ''
  thongBao.value = ''
  try {
    const r = await ghi('/api/nho/ghi', thanGhi({ noi_dung: noiDung.value.trim(), pham_vi: phamVi.value,
      nhan: tachNhan(nhan.value) }, '', ma))
    const kq = r.ket_qua.ghi
    thongBao.value = kq.pham_vi === phamVi.value ? `Đã ghi ${kq.id} vào ${kq.pham_vi}.`
      : `Đã ghi ${kq.id} — chạm luật nghiệp vụ nên chuyển vào ${kq.pham_vi}.`
    noiDung.value = ''
    nhan.value = ''
    ma = taoMaThaoTac()
    emit('doi')
  } catch (e) {
    loi.value = e.message
    if (e.status === 422 || e.status === 409 || e.status === 404) ma = taoMaThaoTac()
  } finally {
    dangGui.value = false
  }
}
</script>

<template>
  <form class="the ku-ghi" @submit.prevent="gui">
    <h3 class="tieu-de-khoi">Ghi tay một ký ức</h3>
    <label class="ku-o"><span>Nội dung <span class="nho">{{ noiDung.length }}/600</span></span>
      <textarea v-model="noiDung" maxlength="600" rows="3" required
        placeholder="Một bài học ngắn, tự đứng được…"></textarea></label>
    <div class="ku-hang">
      <label class="ku-o"><span>Phạm vi</span><select v-model="loai">
        <option v-for="[k, ten] in LOAI_PHAM_VI" :key="k" :value="k">{{ ten }}</option>
      </select></label>
      <label v-if="loai.startsWith('du-an')" class="ku-o"><span>Dự án</span><select v-model="duAnChon">
        <option value="" disabled>— chọn —</option>
        <option v-for="d in props.duAn" :key="d" :value="d">{{ d }}</option>
      </select></label>
      <label v-if="loai === 'vai'" class="ku-o"><span>Vai</span>
        <input v-model.trim="vai" class="o" maxlength="40" placeholder="coder, qc, cham-cot…"></label>
    </div>
    <label class="ku-o"><span>Nhãn <span class="nho">tối đa 5, cách nhau dấu phẩy</span></span>
      <input v-model="nhan" class="o" maxlength="200" placeholder="test, git"></label>
    <p class="nho ku-dich">Ghi vào: <span class="chip mono">{{ phamVi || '(chưa đủ)' }}</span></p>
    <div v-if="phamVi && ngoaiDuAn(phamVi)" class="canh-bao">Agent của MỌI dự án sẽ thấy ký ức này. Có tên khách,
      số tiền hay tên module của bất kỳ dự án nào thì bị từ chối.</div>
    <p v-if="phamVi && phamVi.endsWith('/cach-lam')" class="nho">Chạm luật nghiệp vụ của dự án thì trạm tự chuyển vào
      <span class="mono">nghiep-vu</span>.</p>
    <div class="ku-gui">
      <button class="nut chinh" type="submit" :disabled="!laDaiCa || dangGui || !phamVi || !noiDung.trim()">Ghi</button>
      <span v-if="thongBao" class="nho" role="status">{{ thongBao }}</span>
      <span v-if="loi" class="ku-loi" role="alert">{{ loi }}</span>
    </div>
  </form>
</template>
