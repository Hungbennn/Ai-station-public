// Luật hiển thị thuần của trang Tổng quan (D17; mockup trang-tong-quan.js). Dữ liệu từ GET /api/tong-quan;
// mọi trạng thái nghiệp vụ tính ở server, ở đây chỉ đếm và đổi sang chữ. Test: tests/tong_quan.test.mjs.
import { gioPhut, gon, truocDay } from './dinh_dang.js'
import { tenKhe } from './luat_han_muc.js'
import { nhanTrangThai } from './luat_doi_ngu.js'

// Mã ngắn của khe như mockup: "B/claude-4" → "claude-4".
export const maNgan = (kheId) => String(kheId || '').split('/').pop()

const dsMuc = (dl) => (dl && dl.phe_duyet && dl.phe_duyet.muc) || []
const loc = (dl, ...loai) => dsMuc(dl).filter((m) => loai.includes(m.loai))
const ct = (m) => (m && m.chi_tiet) || {}

// Năm ô "Việc chờ Đại ca" (mockup khoiViecCho; D38/Q6: tổng là `phe_duyet.so`, mỗi ô đếm riêng).
export function oViecCho(dl) {
  const canChot = ((dl && dl.du_an) || []).reduce((s, d) => s + ((d.so_bead && d.so_bead['can-chot']) || 0), 0)
  const review = loc(dl, 'cho-review')
  const khongXm = review.filter((m) => ct(m).pr_tram && ct(m).pr_tram.trang_thai === 'khong_xac_minh').length
  const bi = loc(dl, 'escalation', 'decision')
  const hoi = bi.find((m) => m.loai === 'escalation' && ct(m).khe_id)          // T4: khe nào hỏi ở bead nào
  const spec = loc(dl, 'spec')
  const he = loc(dl, 'he')
  const heDau = ct(he[0])
  const o = (ten, so, phu, toi, lop) => ({ ten, so, phu, toi, lop })
  return [
    o('Cần Đại ca chốt', canChot, 'cột 2 · có câu hỏi', '/cong-viec', 'tt-can_nguoi'),
    o('Chờ review để đóng', review.length, `cột 3${khongXm ? ` · ${khongXm} PR không xác minh được` : ''}`,
      '/phe-duyet', 'tt-cau_dao'),
    o('Escalation bí', bi.length, hoi ? `${tenKhe(ct(hoi).khe_id)} hỏi ở ${ct(hoi).bead_goc || hoi.bead_id}`
      : 'không có', '/phe-duyet', 'tt-can_nguoi'),
    o('Spec chờ duyệt', spec.length, spec.length ? 'đọc rồi duyệt ở Phê duyệt' : 'chưa có', '/phe-duyet', ''),
    o('Hệ cần xem', he.length, !he.length ? 'không có' : heDau.khe_id ? `cầu dao ${maNgan(heDau.khe_id)}`
      : heDau.su_kien || '', '/phe-duyet', 'tt-cau_dao'),
  ]
}

// Chip một dịch vụ launchd (mockup khoiSucKhoe; `da_cai`/`dang_chay` null = không kiểm được).
export function chipDichVu(dv) {
  if (dv.dang_chay === true) return { chu: 'chạy', lop: 'tt-lam' }
  if (dv.da_cai === false) return { chu: 'chưa cài', lop: 'tt-tat' }
  if (dv.da_cai === true && dv.dang_chay === false) return { chu: 'dừng', lop: 'tt-can_nguoi' }
  return { chu: 'không rõ', lop: '' }
}

const TEN_LOI_NHO = { 'nho.loi_llm': 'LLM', 'nho.loi_embedder': 'embedder' }

// Bốn dòng dưới danh sách dịch vụ: [tên, giá trị, lớp chip].
export function dongTram(dl, bayGio = new Date()) {
  const quet = ((dl && dl.du_an) || []).map((d) => d.quet_cuoi).filter(Boolean)
    .sort((a, b) => new Date(b) - new Date(a))[0]
  const estop = Boolean(dl && dl.tram && dl.tram.estop)
  const loiNho = [...new Set(loc(dl, 'he').map((m) => TEN_LOI_NHO[ct(m).su_kien]).filter(Boolean))]
  const ngat = ((dl && dl.doi_ngu && dl.doi_ngu.khe) || []).filter((k) => k.cau_dao && k.cau_dao.ngat)
  return [
    ['Quét cuối', quet ? `${gioPhut(quet)} · ${truocDay(quet, bayGio)}` : 'chưa quét', quet ? 'tt-lam' : 'tt-tat'],
    ['Estop', estop ? 'đang bật' : 'tắt', estop ? 'tt-can_nguoi' : 'tt-lam'],
    ['Lỗi memory', loiNho.length ? `lỗi ${loiNho.join(', ')}` : 'không', loiNho.length ? 'tt-can_nguoi' : 'tt-lam'],
    ['Cầu dao khe', ngat.length ? `${ngat.length} ngắt · ${ngat.map((k) => maNgan(k.khe_id)).join(', ')}` : 'không',
      ngat.length ? 'tt-cau_dao' : 'tt-lam'],
  ]
}

// Thứ tự chip như mockup NHAN_TRANG_THAI; cầu dao ngắt đè trạng thái (nhanTrangThai, luat_doi_ngu.js).
const THU_TU = ['lam', 'ranh', 'tat', 'cau_dao', 'can_nguoi', 'loi', 'mat_ket_noi']
export const lopTrangThai = (k) => (k.cau_dao && k.cau_dao.ngat ? 'cau_dao' : k.trang_thai)

export function demTrangThai(dsKhe) {
  const dem = {}
  for (const k of dsKhe || []) dem[lopTrangThai(k)] = (dem[lopTrangThai(k)] || 0) + 1
  const ten = Object.fromEntries((dsKhe || []).map((k) => [lopTrangThai(k), nhanTrangThai(k)]))
  return THU_TU.filter((tt) => dem[tt]).map((tt) => ({ lop: `tt-${tt}`, chu: ten[tt], n: dem[tt] }))
}

// Usage hôm nay (mockup khoiUsage): giá khe thuê bao chỉ là tương đương; dòng `cham-cot` là Claude API.
const CHAM_COT = 'cham-cot'
const tien = (x) => (typeof x === 'number' ? `$${x.toFixed(2)}` : 'chưa có giá')
const tong = (ds, khoa) => ds.reduce((s, d) => s + (typeof d[khoa] === 'number' ? d[khoa] : 0), 0)
const tongGia = (ds) => (ds.some((d) => typeof d.chi_phi_usd === 'number') ? tong(ds, 'chi_phi_usd') : null)

export function usageHomNay(usage) {
  const ngay = (usage && usage.theo_ngay) || []
  const nguon = (usage && usage.theo_nguon) || []
  const khe = nguon.filter((d) => d.khoa !== CHAM_COT)
    .sort((a, b) => (b.chi_phi_usd || 0) - (a.chi_phi_usd || 0))
  const max = Math.max(0, ...khe.map((d) => d.chi_phi_usd || 0))
  return {
    vao: gon(tong(ngay, 'token_vao')),
    ra: gon(tong(ngay, 'token_ra')),
    usdKhe: tien(tongGia(khe)),
    usdApi: tien(tongGia(nguon.filter((d) => d.khoa === CHAM_COT))),
    luot: tong(ngay, 'so_lan'),
    cot: khe.map((d) => ({ ma: maNgan(d.khoa), usd: tien(d.chi_phi_usd),
      rong: max > 0 ? ((d.chi_phi_usd || 0) / max) * 100 : 0 })),
  }
}
