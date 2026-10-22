// Bộ giao việc trên bảng (lát 4a-2): gắn lý do chưa giao / thông tin PR vào thẻ; chuỗi hiển thị thuần (node --test).
// Server dựng mọi chuỗi từ hằng số + id/SHA đã kiểm dạng; ở đây chỉ hiển thị bằng text, link qua laLinkAnToan.
export function ganGiaoViec(dsThe, giao) {
  const g = giao || {}
  return dsThe.map((t) => ({ ...t, giao: g[`${t.du_an}/${t.id}`] ?? null }))
}

export function nhanChuaGiao(the) {
  return the && the.giao && the.giao.khong_giao ? the.giao.khong_giao : ''
}

export function canhBaoPr(pr) {
  if (!pr) return ''
  if (pr.tu_xa == null) return 'Chưa kiểm được nhánh trên remote — kiểm trước khi tạo PR.'
  if (pr.lech) return `Nhánh ${pr.nhanh} trên remote đang ở ${pr.tu_xa}, KHÁC commit trạm đã kiểm — đừng tạo PR.`
  return ''
}

// Lát 2d: PR do trạm mở (4c). Server gửi `giao.pr.tram = {so, url, trang_thai, ly_do}`; `ly_do` là câu hằng của server.
// Nhãn và câu theo mockup đã duyệt (D20, D33 — docs/mockup/2026-10-15-giao-dien); giao diện Vue làm ở lát 2f.
export const NHAN_PR_TRAM = { mo: 'PR đã mở', khong_xac_minh: 'PR không xác minh được', da_merge: 'PR đã merge' }
const biet = (t) => Boolean(t) && Object.hasOwn(NHAN_PR_TRAM, t.trang_thai)

export function prTram(the) {
  return (the && the.giao && the.giao.pr && the.giao.pr.tram) || null
}

export function nhanPrTram(the) {
  const t = prTram(the)
  return biet(t) ? NHAN_PR_TRAM[t.trang_thai] : ''
}

// Lớp chip `pr-<trạng thái>` của mockup (style.css) — chỉ cho trạng thái đã biết.
export function lopPrTram(t) {
  return biet(t) ? `pr-${t.trang_thai}` : ''
}

// Dòng PR trong ngăn bên (mockup Công việc): "PR #12 — <lý do>"; số chỉ khi là số nguyên.
export function moTaPrTram(t) {
  if (!t) return ''
  const so = Number.isInteger(t.so) ? `PR #${t.so}` : 'PR'
  return t.ly_do ? `${so} — ${t.ly_do}` : so
}

// Cảnh báo trên thẻ "Chờ review để đóng" (mockup Phê duyệt) — chỉ khi PR đã merge mà trạm không xác minh được.
export function canhBaoPrTram(t) {
  if (!t || t.trang_thai !== 'khong_xac_minh') return ''
  return `PR đã merge nhưng trạm không xác minh được: ${t.ly_do}. Bead ở lại cột 3 — Đại ca tự kiểm rồi bấm Duyệt.`
}
