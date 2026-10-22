// Trạng thái dùng chung của mockup (thay cho dữ liệu máy chủ). Bản thật: máy chủ suy từ sự kiện, trang chỉ vẽ.
import { trangThai } from './du-lieu.js'

export const trangThaiTram = { estop: false, tam_dung: false }
const daSua = {}            // ma dự án → trạng thái đã sửa trong phiên mockup
let thHienTai = null

export function datEstop(bat) {
  trangThaiTram.estop = bat
  document.getElementById('bang-estop').hidden = !bat
  const n = document.getElementById('nut-estop')
  n.classList.toggle('bat', bat)
  n.querySelector('span').textContent = bat ? 'Estop đang bật' : 'Estop'
}

export function datTamDungTram(bat) {
  trangThaiTram.tam_dung = bat
  document.getElementById('bang-tam-dung').hidden = !bat
  const n = document.getElementById('nut-tam-dung-tram')
  n.classList.toggle('bat', bat)
  n.querySelector('span').textContent = bat ? 'Đang tạm dừng tự động' : 'Tạm dừng tự động'
}

// Trạng thái một dự án theo tình huống; đổi tình huống thì bỏ phần đã sửa.
export function layDuAn(ma, th = 'binh-thuong') {
  if (th !== thHienTai) { for (const k of Object.keys(daSua)) delete daSua[k]; thHienTai = th }
  daSua[ma] ??= structuredClone(trangThai(ma, th))
  return daSua[ma]
}
