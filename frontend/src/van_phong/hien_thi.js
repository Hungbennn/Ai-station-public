// Hình thức nhân vật / phòng của Văn phòng 3D (spec 2 §5.5) — hàm thuần. Trạng thái do server suy
// (`hien_thi` ∈ lam | ranh | can_nguoi | loi | tat — tram/suy/nhan_vat.py); ở đây chỉ đổi sang tư thế, màu, chữ.
import { gioVN } from '../luat.js'

// Bảng màu đồ vật của mockup van-phong.js MAU (D20). `den`: đèn Điều phối khi sáng — vàng ấm (D38, plan 2e G21);
// `denTat`: xám khi tắt hoặc chưa có tín hiệu. `suc_khoe`: đèn LED tủ máy chủ theo `suc_khoe.muc[i].mau` (T6).
export const MAU = {
  go: '#c79d74', goDam: '#7a2c14', goTu: '#5d2412', quay: '#c9805e', may: '#3b3330', man: '#9fd0ee',
  manDo: '#e0574a', manTat: '#8d949a', vien: '#2f3439', da: '#f2c9a3', chan: '#2b2523', tu: '#30363c',
  ledTat: '#4b5a52', ghe: '#8a6a50', chau: '#c4673f', la: '#5f9e57', la2: '#7cb36d', dat: '#5a3d2b',
  su: '#ece7f2', cafe: '#5b3426', ban: '#efe6da', chanBan: '#8d7a6a', cot: '#6b6058', bong: '#3a2418',
  den: '#f2c14e', denTat: '#b7b7b7',
  suc_khoe: { xanh: '#5fd38a', vang: '#f2c14e', do: '#e0574a' },
}
const TEN_BUOC = { spec: 'spec', code: 'code', qc: 'QC' }
const TU_THE = {
  lam: { ngoi: true, giaTay: false, chamDo: false, manHinh: 'sang', doMo: 1 },
  ranh: { ngoi: false, giaTay: false, chamDo: false, manHinh: null, doMo: 1 },
  can_nguoi: { ngoi: true, giaTay: true, chamDo: true, manHinh: 'sang', doMo: 1 },
  loi: { ngoi: true, giaTay: false, chamDo: false, manHinh: 'do', doMo: 1 },
  tat: { ngoi: true, giaTay: false, chamDo: false, manHinh: 'tat', doMo: 0.35 },
}

export function tuThe(hienThi) {
  return { ...(TU_THE[hienThi] ?? TU_THE.tat) }
}

// Cắt theo ký tự (không cắt đôi chữ có dấu tổ hợp sẵn).
export function catChu(s, n) {
  const kt = Array.from(String(s ?? ''))
  return kt.length > n ? `${kt.slice(0, n - 1).join('')}…` : kt.join('')
}

export function chuBien(p) {
  if (p.loai === 'giam_doc') return `Phòng giám đốc · ${p.so_cho} việc chờ`
  if (p.loai === 'dieu_phoi') {
    const den = p.sang === null || p.sang === undefined ? 'chưa có tín hiệu' : p.sang ? 'đang có phiên' : 'tắt đèn'
    return `Điều phối · ${den}`
  }
  return catChu(p.ten ?? p.ma, 28)
}

// Phòng Điều phối: lúc nhận nhịp cuối từ hook máy A (plan 2e G21). Component hiển thị dòng này thuộc lát 2f.
export function chuNhip(p) {
  return p.loai === 'dieu_phoi' && p.nhip_cuoi ? `nhịp cuối ${gioVN(p.nhip_cuoi)}` : null
}

export function chuBongBong(nv) {
  if (!nv.bead || (nv.hien_thi !== 'lam' && nv.hien_thi !== 'can_nguoi')) return null
  return `${catChu(nv.bead.tieu_de, 36)} · ${TEN_BUOC[nv.bead.buoc] ?? nv.bead.buoc}`
}

// Bấm nhân vật → mở bead đang làm (ngăn bên trang Công việc); không có bead → Đội ngũ AI.
export function duongDanNhanVat(nv) {
  return nv.bead ? { path: '/cong-viec', query: { du_an: nv.bead.du_an, bead: nv.bead.bead_id } } : { path: '/doi-ngu' }
}

// Bấm phòng dự án → lọc Công việc theo dự án; phòng cố định dẫn tới trang tương ứng (plan 2c G9).
export function duongDanPhong(p) {
  if (p.loai === 'du_an') return { path: '/cong-viec', query: { du_an: p.du_an } }
  if (p.loai === 'giam_doc' || p.loai === 'may_chu') return { path: '/phe-duyet' }
  if (p.loai === 'ca_phe') return { path: '/doi-ngu' }
  return null
}
