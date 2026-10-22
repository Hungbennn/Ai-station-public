// Luật hiển thị thuần của trang Usage & chi phí (mockup trang-usage.js, D36/D39). Server chỉ trả các mảng của
// GET /api/usage; ô số tổng, biểu đồ theo ngày, tỉ trọng do trình duyệt tự cộng ở đây. Test: tests/usage.test.mjs.
import { gon, ngayNgan, soDayDu, usd } from './dinh_dang.js'
import { mauKhe } from './mau_khe.js'

export const SO_NGAY_USAGE = [7, 14, 30, 92]
export const TRUONG_TOKEN = ['token_vao', 'token_ra', 'token_cache_doc', 'token_cache_ghi']
const NGUON_CHAM = 'cham-cot'
// Bước trục biểu đồ như mockup bieuDo(): trần = bước × 4; vượt bảng thì tiếp chuỗi 1-2-5 (cột không tràn khung).
const BUOC = { chi_phi: [1, 2, 5, 10, 20, 50], token: [1e5, 2e5, 5e5, 1e6, 2e6, 5e6] }
const LUAT = {
  ok: { chu: 'Nhận việc', lop: 'tt-lam' },
  ngung: { chu: 'Ngừng — chạm ngưỡng', lop: 'tt-can_nguoi' },
  chi_p0_p1: { chu: 'Chỉ P0–P1 — tuần cao', lop: 'tt-cau_dao' },
  chua_biet: { chu: 'Chưa biết — vẫn nhận việc', lop: 'tt-cau_dao' },
}

const so = (x) => (typeof x === 'number' && Number.isFinite(x) ? x : 0)

// Tổng từ `theo_ngay`; `chi_phi_usd` = null khi không dòng nào có giá (như tram/usage/su_kien.py::tong_hop).
export function tongUsage(theoNgay) {
  const t = { token_vao: 0, token_ra: 0, token_cache_doc: 0, token_cache_ghi: 0, so_lan: 0, thieu_gia: 0 }
  let cp = null
  for (const d of theoNgay || []) {
    for (const k of Object.keys(t)) t[k] += so(d[k])
    if (typeof d.chi_phi_usd === 'number') cp = (cp ?? 0) + d.chi_phi_usd
  }
  return { ...t, chi_phi_usd: cp === null ? null : Math.round(cp * 1e4) / 1e4 }
}

// Sáu ô `.tq-so.us-so`: số gọn, rê chuột (`tieuDe`) ra số đầy đủ (D39).
export function oTong(dl) {
  const t = tongUsage(dl.theo_ngay)
  const cham = (dl.theo_nguon || []).find((d) => d.khoa === NGUON_CHAM)
  const lanCham = so(cham && cham.so_lan)
  const o = (gt, ten, phu = '', tieuDe = '') => ({ gt, ten, phu, tieuDe })
  const coGia = dl.co_bang_gia && t.chi_phi_usd !== null
  const thieu = t.thieu_gia ? ` · ${soDayDu(t.thieu_gia)} lần thiếu giá` : ''
  return [
    o(gon(t.token_vao), 'token vào', '', soDayDu(t.token_vao)),
    o(gon(t.token_ra), 'token ra', '', soDayDu(t.token_ra)),
    o(gon(t.token_cache_doc), 'cache đọc', '', soDayDu(t.token_cache_doc)),
    o(gon(t.token_cache_ghi), 'cache ghi', '', soDayDu(t.token_cache_ghi)),
    o(soDayDu(t.so_lan), 'lần gọi', `${soDayDu(t.so_lan - lanCham)} khe · ${soDayDu(lanCham)} chấm cột`),
    coGia ? o(usd(t.chi_phi_usd), 'chi phí ước tính', `API thật ${usd(cham ? cham.chi_phi_usd : 0)}${thieu}`)
      : o('—', 'chi phí ước tính', 'chưa có giá'),
  ]
}

// Mọi ngày từ `tu` đến `den` (YYYY-MM-DD, kể cả hai đầu) — biểu đồ có cột cả ngày không có sự kiện.
export function dayNgay(tu, den) {
  const re = /^\d{4}-\d{2}-\d{2}$/
  if (!re.test(String(tu)) || !re.test(String(den))) return []
  const ra = []
  for (let n = new Date(`${tu}T00:00:00Z`); ra.length < 400; n.setUTCDate(n.getUTCDate() + 1)) {
    const iso = n.toISOString().slice(0, 10)
    if (iso > den) break
    ra.push(iso)
  }
  return ra
}

export function khoangNgay(tu, den) {
  return `Từ ${ngayNgan(tu)} đến ${ngayNgan(den)}/${String(den).slice(0, 4)}`
}

// Nhãn ngày dưới cột: khoảng 10 mốc + luôn có hôm nay (mockup `moc`).
export function hienMocNgay(i, soCot, laNay) {
  return laNay || i % Math.max(1, Math.ceil(soCot / 10)) === 0
}

export function giaTriNgay(d, che) {
  if (!d) return 0
  return che === 'chi_phi' ? so(d.chi_phi_usd) : so(d.token_vao) + so(d.token_ra)
}

// Trần trục + 5 nhãn từ trên xuống ("$8" … "$0", "2,00 tr" … "0").
export function trucBieuDo(lon, che) {
  const buoc = [...(BUOC[che] || BUOC.token)]
  const can = Math.max(so(lon), 0.01)
  while (buoc.at(-1) * 4 < can) buoc.push(buoc.at(-3) * 10)
  const tran = buoc.find((b) => b * 4 >= can) * 4
  const nhan = (v) => (che === 'chi_phi' ? `$${v % 1 ? v.toFixed(1) : v}` : gon(v))
  return { tran, nhan: [4, 3, 2, 1, 0].map((i) => nhan((tran * i) / 4)) }
}

export function chieuCot(v, tran) {
  return tran > 0 ? Math.min(100, Math.max(0, (so(v) / tran) * 100)) : 0
}

// Cột Tỉ trọng (mockup bang tiTrong): theo chi phí, tối thiểu 2%; chưa có giá thì theo token vào + ra.
export function tiTrong(dong) {
  const ds = dong || []
  const cp = ds.map((d) => so(d.chi_phi_usd))
  const gt = cp.some((x) => x > 0) ? cp : ds.map((d) => so(d.token_vao) + so(d.token_ra))
  const tong = gt.reduce((a, x) => a + x, 0) || 1
  return gt.map((x) => Math.max(2, (x / tong) * 100))
}

// Tên + chấm màu của nguồn: khe → khe_id mono, màu thân khe (mau_khe.js); cham-cot → chấm xám.
export function nguonUsage(khoa) {
  if (khoa === NGUON_CHAM) return { ten: 'Bộ chấm cột (Claude API)', mono: false, mau: 'var(--xam)' }
  return { ten: String(khoa), mono: true, mau: mauKhe(khoa).than }
}

export function nhanLuat(muc) {
  return LUAT[muc] ?? LUAT.chua_biet
}

export function moiNhatTruoc(ds) {
  return [...(ds || [])].sort((a, b) => String(b.khoa).localeCompare(String(a.khoa)))
}

// ccusage trả {ngay, ...} → dòng bảng {khoa, ...}, mới nhất trước.
export function dongCcusage(cc) {
  return moiNhatTruoc(((cc && cc.theo_ngay) || []).map((d) => ({ ...d, khoa: d.ngay })))
}
