// Luật hiển thị thuần của trang Đội ngũ AI + Usage (lát 2b). Trạng thái khe, cảnh báo hạn mức tính ở server
// (tram/phieu/trang_thai.py, tram/suy/doi_ngu.py) — ở đây chỉ đổi sang chữ.
import { gioVN } from './luat.js'

export const TEN_TRANG_THAI_KHE = {
  lam: 'Đang làm', can_nguoi: 'Cần Đại ca', ranh: 'Rảnh', tat: 'Tắt', loi: 'Lỗi lần chạy cuối',
  mat_ket_noi: 'Mất kết nối',
}
const TEN_CUA_SO = { '5h': 'Cửa sổ 5 giờ', tuan: 'Cửa sổ tuần' }
const TEN_NGUON = { 'cham-cot': 'Bộ chấm cột (Claude API)' }
const LY_DO_CAU_DAO = { 'het-han-muc': 'hết hạn mức', 'loi-lien-tiep': 'lỗi không do agent liên tiếp' }
export const CANH_BAO_HAN_MUC = {
  ngung: ['loi', 'Hạn mức chạm ngưỡng ngừng — không nhận việc mới'],
  chi_p0_p1: ['canh-bao', 'Cửa sổ tuần cao — chỉ nhận việc P0–P1'],
  chua_biet: ['canh-bao', 'Hạn mức chưa biết — vẫn nhận việc (#15)'],
}

export function nhanTrangThai(khe) {
  if (khe.cau_dao && khe.cau_dao.ngat) return 'Cầu dao ngắt'
  return TEN_TRANG_THAI_KHE[khe.trang_thai] ?? khe.trang_thai
}

// `phan_tram` là phần ĐÃ DÙNG (spec 3 §8.1–8.2: ≥ 90% thì ngừng nhận việc).
export function moTaCuaSo(cs) {
  const ten = TEN_CUA_SO[cs.loai] ?? cs.loai
  if (cs.trang_thai !== 'biet') {
    return `${ten}: chưa biết${cs.doc_luc ? ` (số đo cũ, đọc lúc ${gioVN(cs.doc_luc)})` : ''}`
  }
  const con = Math.max(0, 100 - cs.phan_tram)
  const reset = cs.reset_luc ? ` · reset ${gioVN(cs.reset_luc)}` : ''
  return `${ten}: còn ${con.toFixed(0)}% (đã dùng ${cs.phan_tram.toFixed(0)}%)${reset} · đọc lúc ${gioVN(cs.doc_luc)}`
}

export function lyDoCauDao(lyDo) {
  return LY_DO_CAU_DAO[lyDo] ?? lyDo ?? ''
}

export function nutKhe(khe) {
  return { tat: khe.trang_thai !== 'tat', bat: khe.trang_thai === 'tat', dongCauDao: Boolean(khe.cau_dao?.ngat) }
}

export function dinhDangSo(n) {
  return typeof n === 'number' ? n.toLocaleString('vi-VN') : '—'
}

export function dinhDangUsd(x) {
  if (typeof x !== 'number') return 'chưa có giá'
  return `$${x < 1 ? x.toFixed(4) : x.toFixed(2)}`
}

export function tenNguon(khoa) {
  return TEN_NGUON[khoa] ?? khoa
}

// Bảng điểm (lát 2d, D14; mockup Đội ngũ AI đã duyệt D20): lọc theo dự án ('' = mọi dự án) + số ngày, mặc định 30.
export const SO_NGAY_BANG_DIEM = [7, 30, 92]
export function duongDanDoiNgu(duAn, soNgay) {
  return `/api/doi-ngu?du_an=${encodeURIComponent(duAn || '')}&so_ngay=${Number.isInteger(soNgay) ? soNgay : 30}`
}

// Ô tỉ lệ bảng điểm, tách hai phần để giao diện (lát 2f) tô "(tử/mẫu)" nhạt như mockup mà không chèn HTML.
// `mau` = cỡ mẫu từ server: null + mẫu 0 → "chưa có"; null không có mẫu (vai khác coder) → "—".
export function oTiLe(x, mau) {
  if (typeof x !== 'number') return { chinh: mau === 0 ? 'chưa có' : '—', phu: '' }
  const phu = Number.isInteger(mau) && mau > 0 ? `(${Math.round(x * mau)}/${mau})` : ''
  return { chinh: `${Math.round(x * 100)}%`, phu }
}

export function tiLe(x, mau) {
  const o = oTiLe(x, mau)
  return o.phu ? `${o.chinh} ${o.phu}` : o.chinh
}

// Khoá v-for của mục Phê duyệt: mục "Hệ cần xem" không gắn bead có thể trùng (du_an, bead_id).
export function khoaMuc(m) {
  return [m.loai, m.du_an, m.bead_id || '', m.chi_tiet?.su_kien || '', m.chi_tiet?.khe_id || ''].join('/')
}
