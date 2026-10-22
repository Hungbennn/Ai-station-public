// Ô tìm ⌘K phía trình duyệt (D38/Q5): tìm trên dữ liệu đã tải — dự án, bead, khe. Không API mới. Hàm thuần.
const TOI_DA = 8
const thuong = (s) => String(s ?? '').normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/đ/g, 'd')
  .replace(/Đ/g, 'D').toLowerCase()

// Kết quả: [{loai: 'du-an'|'bead'|'khe', nhan, phu, den}] — `den` là đích router (object path/query).
export function timKiem(q, { duAn = [], the = [], khe = [] } = {}) {
  const k = thuong(q).trim()
  if (!k) return []
  const khop = (...s) => s.some((x) => thuong(x).includes(k))
  const ra = []
  for (const d of duAn) {
    if (khop(d)) ra.push({ loai: 'du-an', nhan: d, phu: 'dự án', den: { path: '/cong-viec', query: { du_an: d } } })
  }
  for (const t of the) {
    if (khop(t.id, t.tieu_de)) {
      ra.push({ loai: 'bead', nhan: `${t.id} · ${t.tieu_de}`, phu: t.du_an,
        den: { path: '/cong-viec', query: { du_an: t.du_an, bead: t.id } } })
    }
  }
  for (const x of khe) {
    if (khop(x.khe_id, x.ten, x.ten_goi_nho)) {
      ra.push({ loai: 'khe', nhan: x.ten || x.khe_id, phu: x.khe_id, den: { path: '/doi-ngu' } })
    }
  }
  return ra.slice(0, TOI_DA)
}

export function laPhimTim(e) {
  return Boolean(e.metaKey || e.ctrlKey) && String(e.key).toLowerCase() === 'k'
}
