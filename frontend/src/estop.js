// Bật estop / tiếp tục từ thanh trên và băng estop (logic giữ nguyên ThanhTrangThai.vue cũ của lát 2a).
import { ref } from 'vue'
import { ghi, thanGhi } from './api.js'
import { kho, taiTrangThai } from './kho.js'

export function dungEstop() {
  const dangGui = ref(false)
  const thongBao = ref('')
  async function bam(laEstop) {
    const tt = kho.trangThai
    if (!tt || (laEstop && !window.confirm('Bật estop: dừng mọi lượt quét ngay?'))) return
    dangGui.value = true
    try {
      await ghi(laEstop ? '/api/chu/estop' : '/api/chu/tiep-tuc', thanGhi({}, tt.estop ? 'bat' : 'tat'))
      thongBao.value = ''
      await taiTrangThai()
    } catch (e) {
      thongBao.value = e.message
    } finally {
      dangGui.value = false
    }
  }
  return { dangGui, thongBao, bam }
}
