// Luật hiển thị thuần của thẻ khe trang Đội ngũ AI theo mockup (lát 2f; trang.js veDoiNgu / theKhe, D20). Tách khỏi
// luat_doi_ngu.js (2b/2d) để file đó giữ nguyên. Hàng bảng điểm (cả khe 0 phiếu) do API 2d trả sẵn (D41).
import { conLai, gioPhut, truocDay } from './dinh_dang.js'
import { lyDoCauDao } from './luat_doi_ngu.js'

// Lớp chip trạng thái (chung.css `.tt-*`), cùng thứ tự ưu tiên với nhanTrangThai.
export function lopTrangThai(khe) {
  return khe.cau_dao && khe.cau_dao.ngat ? 'tt-cau_dao' : `tt-${khe.trang_thai}`
}

const TEN_BUOC = { spec: 'spec', code: 'code', qc: 'QC' }

// Ô `.viec` của thẻ khe: {loai: phieu|cau_dao|tat|mat_ket_noi|trong, ma (bead_id, chỉ khi giữ phiếu), chu}.
export function oViec(khe, bayGio = new Date()) {
  const p = khe.phieu
  if (p) return { loai: 'phieu', ma: p.bead_id, chu: `${p.tieu_de} · ${TEN_BUOC[p.buoc] ?? p.buoc}` }
  const cd = khe.cau_dao || {}
  if (cd.ngat) {
    const con = conLai(cd.toi_luc, bayGio)
    const toi = cd.toi_luc ? ` · tự đóng ${gioPhut(cd.toi_luc)}${con ? ` (${con})` : ''}` : ''
    return { loai: 'cau_dao', ma: '', chu: `Cầu dao ngắt: ${lyDoCauDao(cd.ly_do)}${toi}` }
  }
  if (khe.trang_thai === 'tat') {
    const vs = (khe.vi_sao_tat || '').trim()
    return { loai: 'tat', ma: '', chu: `Đại ca tắt khe${vs ? ` · “${vs}”` : ''}` }
  }
  if (khe.trang_thai === 'mat_ket_noi') {
    return { loai: 'mat_ket_noi', ma: '', chu: `Không thấy nhịp tim từ máy ${khe.may}` }
  }
  return { loai: 'trong', ma: '', chu: 'Không giữ việc' }
}

// Spec 3 không có số phiên tối đa (D38/Q11) → chỉ đếm phiên đang chạy, bỏ mẫu số "1/2" của mockup.
export function chuPhien(soPhien) {
  return soPhien > 0 ? `${soPhien} phiên đang chạy` : 'Không có phiên'
}

// "♥ nhịp tim cuối: …"; giờ máy lệch làm nhịp nằm ở tương lai → "vừa xong".
export function chuNhipTim(nhip, bayGio = new Date()) {
  return nhip ? truocDay(nhip, bayGio) || 'vừa xong' : 'chưa từng có'
}
