// Luật hiển thị thuần của màn Ký ức (spec 1b §4, §5, §8; spec 2 §7 `/api/nho/*`). Server vẫn tự kiểm mọi thứ.
const TEN = /^[a-z0-9-]+$/
export const LOAI_PHAM_VI = [
  ['du-an-cach-lam', 'Dự án · cách làm'],
  ['du-an-nghiep-vu', 'Dự án · nghiệp vụ'],
  ['vai', 'Vai (mọi dự án thấy)'],
  ['chung', 'Chung (mọi dự án thấy)'],
]
export const TEN_SU_KIEN_NHO = {
  'nho.ghi': 'Ghi', 'nho.gop': 'Gộp', 'nho.xoa': 'Xoá mềm', 'nho.xoa_cung': 'Xoá cứng',
  'nho.thang_cap': 'Thăng cấp', 'nho.tu_choi': 'Từ chối', 'nho.loi_tach': 'Bỏ sự kiện',
  'nho.loi_llm': 'Lỗi Claude API', 'nho.loi_embedder': 'Lỗi embedder', 'nho.phuc_hoi': 'Phục hồi',
  'nho.bo_bi_mat': 'Bỏ vì bí mật',   // lát 1b-4 (quét bí mật)
}

// Phạm vi đầy đủ từ lựa chọn trên form; null khi thiếu/sai tên — nút Ghi tắt.
export function dungPhamVi(loai, duAn, vai) {
  if (loai === 'chung') return '/chung'
  if (loai === 'vai') return TEN.test(vai || '') ? `/vai/${vai}` : null
  if (!TEN.test(duAn || '')) return null
  if (loai === 'du-an-cach-lam') return `/du-an/${duAn}/cach-lam`
  if (loai === 'du-an-nghiep-vu') return `/du-an/${duAn}/nghiep-vu`
  return null
}

export function ngoaiDuAn(phamVi) {
  return phamVi === '/chung' || String(phamVi).startsWith('/vai/')
}

// "test, git ,test" → ['test', 'git']: tối đa 5 nhãn, mỗi nhãn 1–30 ký tự, bỏ trùng.
export function tachNhan(s) {
  const ds = String(s || '').split(',').map((x) => x.trim()).filter((x) => x && x.length <= 30)
  return [...new Set(ds)].slice(0, 5)
}

export function tomTatNguon(nguon) {
  return (nguon || []).map((n) => {
    const noi = [n.du_an, n.bead_id].filter(Boolean).join('/')
    return n.loai === 'thang_cap' ? `thăng cấp từ ${n.du_an || '?'} (${n.id_goc || '?'})`
      : `${n.loai}${noi ? ' · ' + noi : ''}`
  }).join('; ')
}

export function laSuKienNho(loai) {
  return typeof loai === 'string' && loai.startsWith('nho.')
}

// ---- Trang Ký ức theo mockup (trang-ky-uc.js, D36/D39) ----
// Nhãn + lớp chip loại phạm vi.
export function nhanPhamVi(pv) {
  const s = String(pv || '')
  if (s === '/chung') return ['Chung', 'pv-chung']
  if (s.startsWith('/vai/')) return [`Vai ${s.slice(5)}`, 'pv-vai']
  return s.endsWith('/nghiep-vu') ? ['Nghiệp vụ', 'pv-nghiep-vu'] : ['Cách làm', 'pv-cach-lam']
}

export const TEN_NGUON = { agent: 'agent ghi', da_chot: 'Đại ca chốt', dai_ca_sua: 'Đại ca sửa cột',
  tra_ve: 'Đại ca trả về', dai_ca_ghi: 'Đại ca ghi tay' }

// nguon[] → đoạn để template dựng "Nguồn: …" (thăng cấp: dự án đậm + mã gốc cắt 9 ký tự; khác: nhãn · vai · bead).
export function moTaNguon(nguon) {
  return (nguon || []).map((n) => {
    const thangCap = n.loai === 'thang_cap'
    return { thangCap, chu: thangCap ? '' : `${TEN_NGUON[n.loai] ?? n.loai}${n.vai ? ` · vai ${n.vai}` : ''}`,
      duAn: n.du_an || '', bead: thangCap ? '' : n.bead_id || '',
      idGoc: thangCap && n.id_goc ? `${String(n.id_goc).slice(0, 9)}…` : '' }
  })
}

// Nhóm lọc sự kiện nho.* (pill) và lớp chip của từng nhóm; loại lạ / lỗi / phục hồi / bỏ vì bí mật → 'loi'.
export const NHOM_SK = [['', 'Tất cả'], ['ghi', 'Ghi · gộp'], ['xoa', 'Xoá'], ['thang_cap', 'Thăng cấp'],
  ['tu_choi', 'Từ chối'], ['loi', 'Lỗi · phục hồi']]
const NHOM_LOAI = { 'nho.ghi': 'ghi', 'nho.gop': 'ghi', 'nho.xoa': 'xoa', 'nho.xoa_cung': 'xoa',
  'nho.thang_cap': 'thang_cap', 'nho.tu_choi': 'tu_choi' }
export const nhomCua = (loai) => NHOM_LOAI[loai] ?? 'loi'
export const LOP_SK = { ghi: 'tt-lam', xoa: 'tt-tat', thang_cap: 'pv-vai', tu_choi: 'tt-cau_dao', loi: 'tt-can_nguoi' }

// Ô tìm lọc phía trình duyệt trên ký ức đã tải: nội dung, nhãn, mã, phạm vi.
export function locKyUc(ds, tim) {
  const q = String(tim || '').trim().toLowerCase()
  if (!q) return ds || []
  return (ds || []).filter((k) => [k.noi_dung, k.id, k.pham_vi, ...(k.nhan || [])]
    .some((x) => String(x || '').toLowerCase().includes(q)))
}

// Pill "Tất cả n": cộng `so` của mọi phạm vi server trả (không phụ thuộc bộ lọc đang chọn).
export const tongPhamVi = (dsPv) => (dsPv || []).reduce((t, p) => t + (p.so || 0), 0)
