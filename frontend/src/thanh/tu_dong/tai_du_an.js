// Tải GET /api/du-an/<ten>/tu-dong cho trang Tự động, ràng với tên dự án của route (Codex Q10): mỗi lần tải mang một
// thế hệ, phản hồi của lần cũ (kể cả của dự án trước) bị bỏ. Đổi dự án → xoá dữ liệu cũ NGAY (khối và nút biến mất)
// rồi mới tải dự án mới, nên tải lỗi không để lại dữ liệu của dự án khác. Tải lại cùng dự án lỗi: giữ dữ liệu, báo lỗi.
import { ref } from 'vue'
import { doc } from '../../api.js'

export function dungTaiDuAn(layTen) {
  const dl = ref(null)
  const loi = ref('')
  const khongCo = ref(false)
  let theHe = 0

  async function tai() {
    const lan = ++theHe
    const ten = layTen()
    try {
      const r = await doc(`/api/du-an/${encodeURIComponent(ten)}/tu-dong`)
      if (lan !== theHe || ten !== layTen()) return false
      dl.value = r
      loi.value = ''
      khongCo.value = false
      return true
    } catch (e) {
      if (lan !== theHe || ten !== layTen()) return false
      khongCo.value = e.status === 404
      if (khongCo.value) dl.value = null
      loi.value = khongCo.value ? '' : e.message
      return false
    }
  }
  function doiDuAn() {
    dl.value = null
    loi.value = ''
    khongCo.value = false
    return tai()
  }
  return { dl, loi, khongCo, tai, doiDuAn }
}
