// Dữ liệu GIẢ cho trang Ký ức và Usage & chi phí — chỉ dùng trường mà API thật trả về:
//   GET /api/nho?pham_vi=&cho=   → { ky_uc[], tong, pham_vi[] }        (tram/api/tuyen_nho.py::danh_sach, _sach)
//   GET /api/nho/su-kien         → { su_kien[{id, luc, du_an, bead_id, loai, tom_tat}] }
//   GET /api/usage?so_ngay=1–92  → { tu, den, theo_ngay, theo_tuan, theo_nguon, theo_du_an, co_bang_gia, ccusage }
//   GET /api/doi-ngu             → khe[].han_muc, khe[].muc_han_muc (khối hạn mức của trang Usage)
// Khớp các trang khác: hôm nay 15/10/2026; nho.ghi 20:58 ở hr-2 ("thêm 2 ký ức" trên Tổng quan);
// usage hôm nay = USAGE_HOM_NAY của Tổng quan (khe $3,10 · API $0,42 · 7 lượt · 1,84 tr vào · 212 n ra).

// ---------- Ký ức ----------
// nguon[].loai: agent (ghi_nho, có vai) | da_chot | dai_ca_sua | tra_ve | dai_ca_ghi | thang_cap (id_goc)
export const KY_UC = [
  { id: 'm-007bbfb13a297c6b1794334c', pham_vi: '/du-an/hr-codex/nghiep-vu', nhan: ['mau-in', 'test'],
    noi_dung: 'Mẫu in hoá đơn: sau khi đổi template, chạy bộ test mẫu in và so với 3 hoá đơn thật đã che số trước khi báo xong.',
    quan_trong: 0.55, nguon: [{ loai: 'agent', du_an: 'hr-codex', bead_id: 'hr-2', su_kien_id: '4127', vai: 'qc' }],
    nguon_dai_ca: false, tao_luc: '2026-10-15T20:58', hieu_luc_tu: '2026-10-15T20:58', dung_luc: null, so_lan_dung: 0 },
  { id: 'm-c21129e7ac09efd087ade33e', pham_vi: '/du-an/hr-codex/cach-lam', nhan: ['ruff'],
    noi_dung: 'Chạy `uv run ruff check .` trước `uv run pytest -q`; lỗi ruff làm lượt QC trượt ngay từ đầu.',
    quan_trong: 0.5, nguon: [{ loai: 'agent', du_an: 'hr-codex', bead_id: 'hr-2', su_kien_id: '4126', vai: 'coder' }],
    nguon_dai_ca: false, tao_luc: '2026-10-15T20:58', hieu_luc_tu: '2026-10-15T20:58', dung_luc: null, so_lan_dung: 0 },
  { id: 'm-f8918ddfdd6a11877681b378', pham_vi: '/vai/coder', nhan: ['lenh'],
    noi_dung: 'Trước khi báo xong, chạy đủ các lệnh được phép của dự án theo đúng thứ tự trong cấu hình; không tự thêm lệnh ngoài danh sách.',
    quan_trong: 0.55, nguon: [{ loai: 'thang_cap', du_an: 'hr-codex', id_goc: 'm-60ebb6720cb6f93486ef1009', vai: 'coder' },
      { loai: 'thang_cap', du_an: 'tram', id_goc: 'm-28b3663f97684988a564f345', vai: 'coder' }],
    nguon_dai_ca: false, tao_luc: '2026-10-15T16:05', hieu_luc_tu: '2026-10-22T16:05', dung_luc: null, so_lan_dung: 0 },
  { id: 'm-bedac1904ce616a67bcfab3e', pham_vi: '/du-an/hr-codex/nghiep-vu', nhan: ['hoa-don'],
    noi_dung: 'Hoá đơn làm tròn đến đồng ở tổng cuối; không hiện số lẻ trên mẫu in.',
    quan_trong: 0.8, nguon: [{ loai: 'da_chot', du_an: 'hr-codex', bead_id: 'hr-2', su_kien_id: '3988' }],
    nguon_dai_ca: true, tao_luc: '2026-10-14T17:10', hieu_luc_tu: '2026-10-14T17:10', dung_luc: '2026-10-15T20:12', so_lan_dung: 1 },
  { id: 'm-3d391f4b7959b29de6a81189', pham_vi: '/du-an/tram/cach-lam', nhan: ['api', 'csp'],
    noi_dung: 'Route mới trong tram/api đi qua GiuaAnToan như mọi route; không thêm middleware riêng.',
    quan_trong: 0.5, nguon: [{ loai: 'agent', du_an: 'tram', bead_id: 'bs-6o0.11', su_kien_id: '3951', vai: 'spec' }],
    nguon_dai_ca: false, tao_luc: '2026-10-14T15:30', hieu_luc_tu: '2026-10-14T15:30', dung_luc: '2026-10-15T09:40', so_lan_dung: 1 },
  { id: 'm-ad71e7c7b1eae8731f3b0da8', pham_vi: '/du-an/hr-codex/cach-lam', nhan: ['ngay'],
    noi_dung: 'Định dạng ngày đi qua hàm chung `dinh_dang_ngay`; không tự format trong template.',
    quan_trong: 0.6, nguon: [{ loai: 'tra_ve', du_an: 'hr-codex', bead_id: 'hr-5', su_kien_id: '3902' }],
    nguon_dai_ca: true, tao_luc: '2026-10-14T10:02', hieu_luc_tu: '2026-10-14T10:02', dung_luc: '2026-10-15T17:55', so_lan_dung: 2 },
  { id: 'm-230b9bbc68813c475d3d1d96', pham_vi: '/du-an/hr-codex/nghiep-vu', nhan: ['phieu-luong'],
    noi_dung: 'Phiếu lương hiển thị ngày dạng dd/mm/yyyy, không dùng dạng ISO.',
    quan_trong: 0.8, nguon: [{ loai: 'da_chot', du_an: 'hr-codex', bead_id: 'hr-5', su_kien_id: '3870' }],
    nguon_dai_ca: true, tao_luc: '2026-10-13T16:20', hieu_luc_tu: '2026-10-13T16:20', dung_luc: '2026-10-15T17:55', so_lan_dung: 3 },
  { id: 'm-42d72694a1463405c4957af0', pham_vi: '/du-an/tram/cach-lam', nhan: ['quyen'],
    noi_dung: 'Trao quyền file cho user của khe: không đi theo symlink (lstat, O_NOFOLLOW).',
    quan_trong: 0.6, nguon: [{ loai: 'tra_ve', du_an: 'tram', bead_id: 'bs-urj.15', su_kien_id: '3811' }],
    nguon_dai_ca: true, tao_luc: '2026-10-13T11:05', hieu_luc_tu: '2026-10-13T11:05', dung_luc: '2026-10-14T22:30', so_lan_dung: 4 },
  { id: 'm-2ef9100fdbb7c4d2654e9750', pham_vi: '/du-an/hr-codex/cach-lam', nhan: ['test'],
    noi_dung: 'Mỗi lỗi sửa phải có test tái hiện viết trước; tên test theo mẫu test_<module>_<hành vi>.',
    quan_trong: 0.8, nguon: [{ loai: 'dai_ca_ghi', ma_thao_tac: '9a1c…' }],
    nguon_dai_ca: true, tao_luc: '2026-10-12T09:14', hieu_luc_tu: '2026-10-12T09:14', dung_luc: '2026-10-15T22:09', so_lan_dung: 5 },
  { id: 'm-19f7d135250be9d426306b12', pham_vi: '/chung', nhan: ['chu', 'giao-dien'],
    noi_dung: 'Chữ hiện cho người dùng viết tiếng Việt có dấu; giữ nguyên thuật ngữ kỹ thuật tiếng Anh.',
    quan_trong: 0.8, nguon: [{ loai: 'dai_ca_ghi', ma_thao_tac: '51e0…' }],
    nguon_dai_ca: true, tao_luc: '2026-10-11T08:30', hieu_luc_tu: '2026-10-11T08:30', dung_luc: '2026-10-15T22:09', so_lan_dung: 14 },
  { id: 'm-1245727126cd81ea4b7db26c', pham_vi: '/vai/qc', nhan: ['nghiem-thu'],
    noi_dung: 'QC đối chiếu từng tiêu chí nghiệm thu với diff; ghi rõ tiêu chí nào chưa có test.',
    quan_trong: 0.65, nguon: [{ loai: 'thang_cap', du_an: 'hr-codex', id_goc: 'm-4f5228023a38f8c1e5905de1', vai: 'qc' },
      { loai: 'thang_cap', du_an: 'tram', id_goc: 'm-407fe9b55c1c0f1e681b693b', vai: 'qc' }],
    nguon_dai_ca: false, tao_luc: '2026-10-03T14:00', hieu_luc_tu: '2026-10-10T14:00', dung_luc: '2026-10-15T20:12', so_lan_dung: 6 },
]

// Bộ đếm phạm vi do memory service trả (`pham_vi[] {pham_vi, so, so_cho}`) — mọi phạm vi có ký ức.
export function phamViKyUc(ds = KY_UC) {
  const m = new Map()
  for (const k of ds) {
    const x = m.get(k.pham_vi) ?? { pham_vi: k.pham_vi, so: 0, so_cho: 0 }
    x.so++
    if (k.hieu_luc_tu > BAY_GIO) x.so_cho++
    m.set(k.pham_vi, x)
  }
  return [...m.values()].sort((a, b) => a.pham_vi.localeCompare(b.pham_vi))
}

export const BAY_GIO = '2026-10-15T22:17'

// Sự kiện nho.* (tối đa 50, mới nhất trước). `tom_tat` = JSON của du_lieu, cắt 300 ký tự (như API thật).
const sk = (id, luc, du_an, bead_id, loai, du_lieu) => ({ id, luc, du_an, bead_id, loai,
  tom_tat: JSON.stringify(du_lieu).slice(0, 300) })
export const SU_KIEN_NHO = [
  sk(4131, '2026-10-15T20:58', 'hr-codex', 'hr-2', 'nho.ghi', { id: KY_UC[0].id, pham_vi: KY_UC[0].pham_vi, nguon: KY_UC[0].nguon }),
  sk(4130, '2026-10-15T20:58', 'hr-codex', 'hr-2', 'nho.ghi', { id: KY_UC[1].id, pham_vi: KY_UC[1].pham_vi, nguon: KY_UC[1].nguon }),
  sk(4088, '2026-10-15T16:05', '_tram', null, 'nho.thang_cap', { id: KY_UC[2].id, pham_vi: '/vai/coder',
    id_goc: KY_UC[2].nguon.map((n) => n.id_goc), du_an: ['hr-codex', 'tram'], hieu_luc_tu: KY_UC[2].hieu_luc_tu }),
  sk(4062, '2026-10-15T14:20', 'hr-codex', 'hr-1', 'nho.phuc_hoi', { loai: 'embedder' }),
  sk(4058, '2026-10-15T14:02', 'hr-codex', 'hr-1', 'nho.loi_embedder', { su_kien_id: 4051, loi: 'Ollama không phản hồi ở 127.0.0.1:11434' }),
  sk(4021, '2026-10-15T11:47', '_tram', null, 'nho.tu_choi', { ly_do: 'chạm luật nghiệp vụ: hoàn tiền', nguon: 'dai_ca_ghi', pham_vi: '/chung' }),
  sk(3990, '2026-10-14T17:10', 'hr-codex', 'hr-2', 'nho.gop', { cu: ['m-66e6b76fa6b8266677a9e7e0'], moi: KY_UC[3].id }),
  sk(3989, '2026-10-14T17:10', 'hr-codex', 'hr-2', 'nho.ghi', { id: KY_UC[3].id, pham_vi: KY_UC[3].pham_vi, nguon: KY_UC[3].nguon }),
  sk(3953, '2026-10-14T15:30', 'tram', 'bs-6o0.11', 'nho.ghi', { id: KY_UC[4].id, pham_vi: KY_UC[4].pham_vi, nguon: KY_UC[4].nguon }),
  sk(3904, '2026-10-14T10:02', 'hr-codex', 'hr-5', 'nho.ghi', { id: KY_UC[5].id, pham_vi: KY_UC[5].pham_vi, nguon: KY_UC[5].nguon }),
  sk(3872, '2026-10-13T16:20', 'hr-codex', 'hr-5', 'nho.ghi', { id: KY_UC[6].id, pham_vi: KY_UC[6].pham_vi, nguon: KY_UC[6].nguon }),
  sk(3813, '2026-10-13T11:05', 'tram', 'bs-urj.15', 'nho.ghi', { id: KY_UC[7].id, pham_vi: KY_UC[7].pham_vi, nguon: KY_UC[7].nguon }),
  sk(3705, '2026-10-13T09:40', 'hr-codex', 'hr-4', 'nho.loi_tach', { su_kien_id: 3702, loi: 'ValueError: nho.agent_ghi: nhan sai dạng' }),
  sk(3650, '2026-10-12T21:00', 'hr-codex', null, 'nho.xoa', { id: 'm-60ebb6720cb6f93486ef1009', pham_vi: '/du-an/hr-codex/cach-lam' }),
  sk(3598, '2026-10-12T09:14', 'hr-codex', null, 'nho.ghi', { id: KY_UC[8].id, pham_vi: KY_UC[8].pham_vi, nguon: KY_UC[8].nguon }),
  sk(3541, '2026-10-11T08:30', '_tram', null, 'nho.ghi', { id: KY_UC[9].id, pham_vi: '/chung', nguon: KY_UC[9].nguon }),
  sk(3330, '2026-10-09T18:12', 'ke-toan', null, 'nho.xoa_cung', { id: 'm-0d4c2a9e51b7f3a8c6e21d90', pham_vi: '/du-an/ke-toan/cach-lam' }),
  sk(3102, '2026-10-03T14:00', '_tram', null, 'nho.thang_cap', { id: KY_UC[10].id, pham_vi: '/vai/qc',
    id_goc: KY_UC[10].nguon.map((n) => n.id_goc), du_an: ['hr-codex', 'tram'], hieu_luc_tu: KY_UC[10].hieu_luc_tu }),
]

// ---------- Usage ----------
export const HOM_NAY = '2026-10-15'
export const NGAY_DAU_SU_KIEN = '2026-08-24'     // trước ngày này trạm chưa ghi sự kiện chạy nào

// Dòng usage thô (một dòng = một nhóm sự kiện chay.xong / cham_cot.ket_qua cùng ngày, nguồn, dự án) — mockup tự
// cộng giống tram/usage/su_kien.py::tong_hop. `gia: false` = mô hình chưa có trong bảng giá (thiếu giá).
const HOM_NAY_DONG = [
  ['B/claude-1', 'hr-codex', 2, 520000, 61000, 2900000, 180000, 1.35],
  ['B/codex-1', 'hr-codex', 2, 410000, 48000, 1200000, 0, 0.96],
  ['B/claude-2', 'hr-codex', 2, 230000, 27000, 1100000, 90000, 0.52],
  ['B/claude-4', 'tram', 1, 160000, 21000, 300000, 60000, 0.27],
  ['cham-cot', 'hr-codex', 9, 330000, 30000, 0, 0, 0.27],
  ['cham-cot', 'tram', 4, 120000, 15000, 0, 0, 0.10],
  ['cham-cot', 'ke-toan', 2, 70000, 10000, 0, 0, 0.05],
]

function rng(seed) {
  return () => { seed |= 0; seed = (seed + 0x6D2B79F5) | 0; let t = Math.imul(seed ^ (seed >>> 15), 1 | seed)
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296 }
}
const isoNgay = (d) => d.toISOString().slice(0, 10)
export function congNgay(iso, n) { const d = new Date(`${iso}T00:00:00Z`); d.setUTCDate(d.getUTCDate() + n); return isoNgay(d) }

function sinhDongUsage() {
  const r = rng(20261015)
  const ra = []
  const gia = (v, o, cd, cg) => (v * 3 + o * 15 + cd * 0.3 + cg * 3.75) / 1e6
  for (let ngay = NGAY_DAU_SU_KIEN; ngay < HOM_NAY; ngay = congNgay(ngay, 1)) {
    const thu = new Date(`${ngay}T00:00:00Z`).getUTCDay()
    const nghi = thu === 0 || thu === 6 ? 0.35 : 1
    const khe = [['B/claude-1', 1], ['B/claude-2', 0.8], ['B/codex-1', 0.7], ['B/claude-4', 0.5]]
    if (ngay < '2026-10-15') khe.push(['B/claude-3', 0.6])      // claude-3 để dành từ 15/10
    for (const [nguon, he] of khe) {
      const lan = Math.round(r() * 3.4 * he * nghi)
      if (!lan) continue
      const du_an = nguon === 'B/claude-4' || r() < 0.28 ? 'tram' : 'hr-codex'
      const v = Math.round(lan * (110000 + r() * 120000)), o = Math.round(v * (0.09 + r() * 0.05))
      const cd = Math.round(v * (2.5 + r() * 3)), cg = nguon.includes('codex') ? 0 : Math.round(v * (0.15 + r() * 0.2))
      const coGia = !(nguon === 'B/codex-1' && ngay < '2026-09-10')   // bảng giá thêm mô hình Codex từ 10/09
      ra.push({ ngay, nguon, du_an, so_lan: lan, token_vao: v, token_ra: o, token_cache_doc: cd, token_cache_ghi: cg,
        chi_phi: coGia ? gia(v, o, cd, cg) * 0.62 : null })
    }
    for (const du_an of ['hr-codex', 'tram', 'ke-toan']) {
      if (du_an === 'ke-toan' && ngay < '2026-10-01') continue
      const lan = Math.round(r() * (du_an === 'hr-codex' ? 10 : 5) * nghi)
      if (!lan) continue
      const v = Math.round(lan * (30000 + r() * 12000)), o = Math.round(lan * (2500 + r() * 1500))
      ra.push({ ngay, nguon: 'cham-cot', du_an, so_lan: lan, token_vao: v, token_ra: o, token_cache_doc: 0,
        token_cache_ghi: 0, chi_phi: gia(v, o, 0, 0) * 0.25 })
    }
  }
  for (const [nguon, du_an, so_lan, v, o, cd, cg, cp] of HOM_NAY_DONG) {
    ra.push({ ngay: HOM_NAY, nguon, du_an, so_lan, token_vao: v, token_ra: o, token_cache_doc: cd, token_cache_ghi: cg, chi_phi: cp })
  }
  return ra
}
export const DONG_USAGE = sinhDongUsage()

// ccusage `daily --json --offline` (toàn bộ Claude Code của tài khoản trạm trên máy B, gồm cả phiên không do khe chạy).
export const CCUSAGE = { phien_ban: '16.2.0', he_so: 1.18 }

// Hạn mức: lấy từ /api/doi-ngu (khe[].han_muc.cua_so, khe[].muc_han_muc). Phần trăm "còn" như Đội ngũ AI.
export const MUC_HAN_MUC = { 'claude-1': 'ok', 'claude-2': 'ok', 'codex-1': 'ok', 'claude-3': 'ok', 'codex-2': 'chua_biet', 'claude-4': 'ngung' }
