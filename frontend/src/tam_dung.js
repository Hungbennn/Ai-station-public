// TẠM DỪNG toàn trạm từ thanh trên và băng vàng (spec dieu-khien-tu-dong "TẠM DỪNG toàn trạm", D78, D101).
// Như estop.js: bật có hộp xác nhận, Tiếp tục một lần bấm; không kiểm phiên bản (máy chủ bỏ qua `expected_version`).
import { ref } from 'vue'
import { ghi, thanGhi } from './api.js'
import { kho, taiTuDong } from './kho.js'
import { HOI_TAM_DUNG_TRAM } from './luat_tu_dong.js'

export function dungTamDungTram() {
  const dangGui = ref(false)
  const thongBao = ref('')
  async function bam(bat) {
    if (!kho.tuDong || (bat && !window.confirm(HOI_TAM_DUNG_TRAM))) return
    dangGui.value = true
    try {
      await ghi(bat ? '/api/tu-dong/tam-dung' : '/api/tu-dong/tiep-tuc', thanGhi({}, ''))
      thongBao.value = ''
      await taiTuDong()
    } catch (e) {
      thongBao.value = e.message
    } finally {
      dangGui.value = false
    }
  }
  return { dangGui, thongBao, bam }
}
