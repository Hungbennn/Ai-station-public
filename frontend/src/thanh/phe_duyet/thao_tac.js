// Thao tác ghi của một mục Phê duyệt (tách từ MucPheDuyet cũ, giữ nguyên hành vi): gửi kèm `updated_at` đang xem;
// 409 = bản đã đổi → báo + tải lại; 501 = trạm chưa sẵn sàng. Thành công → emit('doi') để trang tải lại.
import { ref } from 'vue'
import { ghi, thanGhi } from '../../api.js'
import { thanDuyet } from '../../luat_spec.js'

export function dungThaoTac(layMuc, emit) {
  const gopY = ref('')
  const loi = ref('')
  const dangGui = ref(false)
  const moTraVe = ref(false)
  const ma = () => `${encodeURIComponent(layMuc().du_an)}/${encodeURIComponent(layMuc().bead_id)}`

  async function lam(duongDan, noiDung) {
    dangGui.value = true
    loi.value = ''
    try {
      await ghi(duongDan, thanGhi(noiDung, layMuc().updated_at))
      gopY.value = ''
      moTraVe.value = false
      emit('doi')
      return true
    } catch (e) {
      loi.value = e.status === 501 ? `Trạm chưa sẵn sàng: ${e.message}`
        : e.status === 409 ? `${e.message} — đã tải lại.` : e.message
      if (e.status === 409) emit('doi')
      return false
    } finally {
      dangGui.value = false
    }
  }
  const duyet = () => lam(`/api/phe-duyet/${ma()}/duyet`, thanDuyet(layMuc()))
  const traVe = () => lam(`/api/phe-duyet/${ma()}/tra-ve`, { gop_y: gopY.value.trim() })
  const traLoi = (vb) => lam(`/api/phe-duyet/${ma()}/tra-loi`, { tra_loi: vb })
  const thuLai = () => lam(`/api/bead/${ma()}/thu-lai`, {})
  return { gopY, loi, dangGui, moTraVe, duyet, traVe, traLoi, thuLai }
}
