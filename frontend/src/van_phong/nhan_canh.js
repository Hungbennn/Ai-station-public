// Danh sách nhãn HTML phủ trên cảnh (mockup van-phong.js "nhân vật + nhãn", "biển tên phòng", D20) — hàm thuần.
// Mỗi nhãn: { id, loai (bien|ten|bb|hh|gd), neo [x, y, z], ax, ay, dx, dy, khe?, chon, chu, nhanDoc, … }.
import { boTriNhan, demChong } from './bo_tri_nhan.js'
import { chuBongBong } from './hien_thi.js'
import { caoNv } from './nhan_vat_3d.js'

const TEN_PHU = { lam: 'Làm', ranh: 'Rảnh', can_nguoi: 'Cần người', loi: 'Lỗi', tat: 'Tắt' }

// Nhãn phụ dưới tên nhân vật; `cau_dao_ngat` (T2) thiếu → "Lỗi".
export function nhanPhu(nv) {
  if (nv.trang_thai === 'mat_ket_noi') return 'Mất kết nối'
  if (nv.hien_thi === 'loi') return nv.cau_dao_ngat ? 'Lỗi · cầu dao ngắt' : 'Lỗi'
  return TEN_PHU[nv.hien_thi] ?? 'Tắt'
}

// Lớp chip trạng thái (chung.css): mất kết nối có màu riêng, cầu dao ngắt màu vàng, còn lại theo hien_thi.
export function lopNhanVat(nv) {
  if (nv.trang_thai === 'mat_ket_noi') return 'tt-mat_ket_noi'
  if (nv.hien_thi === 'loi' && nv.cau_dao_ngat) return 'tt-cau_dao'
  return `tt-${TEN_PHU[nv.hien_thi] ? nv.hien_thi : 'tat'}`
}

// Đèn Điều phối (2e G21): sang true / false / null.
export function trangThaiDen(p) {
  return p.sang === true ? 'đang có phiên' : p.sang === false ? 'tắt đèn' : 'chưa có tín hiệu'
}

function nhanNhanVat(nv) {
  const chon = { loai: 'khe', khe_id: nv.khe_id }
  const goc = { khe: nv.khe_id, chon }
  const cao = caoNv(nv)
  const phu = nhanPhu(nv)
  const ra = [{ ...goc, id: `ten:${nv.khe_id}`, loai: 'ten', neo: [nv.x, 0, nv.z], ax: -0.5, ay: 0, dx: 0, dy: 8,
    chu: nv.ten, phu, mo: nv.hien_thi === 'tat', nhanDoc: `${nv.ten}: ${phu}` }]
  const bb = chuBongBong(nv)
  if (bb) {
    ra.push({ ...goc, id: `bb:${nv.khe_id}`, loai: 'bb', neo: [nv.x, cao + 0.3, nv.z], ax: -0.5, ay: -1, dx: 0,
      dy: -10, ma: nv.bead.bead_id, chu: bb, nhanDoc: `${nv.ten} đang giữ ${nv.bead.bead_id}: ${bb}` })
  }
  if (nv.hien_thi === 'can_nguoi') {
    ra.push({ ...goc, id: `hh:${nv.khe_id}`, loai: 'hh', neo: [nv.x, cao - 0.5, nv.z], ax: 0, ay: -0.5, dx: 16,
      dy: 0, chu: '1', nhanDoc: `${nv.ten} cần Đại ca trả lời` })
  }
  return ra
}

function nhanPhong(p) {
  const chon = { loai: 'phong', ma: p.ma }
  const den = p.loai === 'dieu_phoi' ? { sang: p.sang === true, chu: trangThaiDen(p) } : null
  const ra = [{ id: `bien:${p.ma}`, loai: 'bien', neo: [p.nhan[0], 0.5, p.nhan[1]], ax: -0.5, ay: -0.5, dx: 0, dy: 0,
    chon, chu: p.tenBien, mo: p.mo, den, nhanDoc: den ? `${p.tenBien}, đèn ${den.chu}` : p.tenBien }]
  if (p.loai === 'giam_doc' && p.so_cho > 0) {
    ra.push({ id: 'gd', loai: 'gd', neo: [p.tam[0] + 0.4, 1.2, p.tam[1]], ax: -0.5, ay: -1, dx: 0, dy: -2, chon,
      chu: String(p.so_cho), nhanDoc: `${p.so_cho} việc chờ Đại ca` })
  }
  return ra
}

export function dungNhan(boTri) {
  return [...boTri.nhanVat.flatMap(nhanNhanVat), ...boTri.phong.flatMap(nhanPhong)]
}

// Phòng / nhân vật đang chọn ({loai, ma | khe_id}) trong mặt bằng mới nhất → props cho PanelChon (khoa = :key).
export function timMucChon(boTri, c) {
  if (!c || !boTri) return null
  if (c.loai === 'khe') {
    const nv = boTri.nhanVat.find((n) => n.khe_id === c.khe_id)
    return nv ? { khoa: `khe:${nv.khe_id}`, nv } : null
  }
  const p = boTri.phong.find((x) => x.ma === c.ma)
  return p ? { khoa: `phong:${p.ma}`, phong: p } : null
}

// Từ toạ độ neo (chieuNhan) + cỡ đo được {id: {w, h}} → vị trí từng nhãn, đường chỉ, số cặp chồng.
export function xepNhan(nhan, chieu, co) {
  const ds = nhan.filter((n) => chieu.diem[n.id] && co[n.id]).map((n) => {
    const d = chieu.diem[n.id]
    const { w, h } = co[n.id]
    const x0 = d.x + n.ax * w + n.dx
    return { id: n.id, loai: n.loai, khe: n.khe, w, h, x0, y0: d.y + n.ay * h + n.dy, diemNeo: d }
  })
  const duong = boTriNhan(ds, chieu.than, chieu.W, chieu.H)
  return { viTri: Object.fromEntries(ds.map((n) => [n.id, { x: n.x, y: n.y }])), duong, chong: demChong(ds) }
}
