// Luật hiển thị thuần (test được bằng node --test). Luật nghiệp vụ thật nằm ở server (tram/suy/cot.py).
export const TEN_HANG = {
  'ai-lam': '1 · AI tự làm',
  'can-chot': '2 · Cần Đại ca chốt',
  'cho-review': '3 · Chờ review để đóng',
  'chua-cham': 'Chưa chấm',
  'theo-plan': 'Feature đang chạy plan',
  epic: 'Epic',
}
const THU_TU_PHE_DUYET = ['escalation', 'decision', 'co-do', 'he', 'cho-review', 'spec', 'feature-xong',
  'san-sang-deploy']
export const TEN_PHE_DUYET = {
  escalation: 'Bí / escalation',
  decision: 'Decision mở chờ trả lời',
  'co-do': 'Cờ đỏ',
  he: 'Hệ cần xem',
  'cho-review': 'Chờ review để đóng',
  spec: 'Spec chờ duyệt',
  'feature-xong': 'Feature xong, chờ đóng',
  'san-sang-deploy': 'Sẵn sàng deploy',          // TM-4 (D101): mục do TM-3 thêm vào GET /api/phe-duyet
}

function soThe(a, b) {
  return (a.uu_tien ?? 9) - (b.uu_tien ?? 9) || String(a.id).localeCompare(String(b.id))
}

export function nhomTheoHang(dsThe) {
  const nhom = Object.fromEntries(Object.keys(TEN_HANG).map((h) => [h, []]))
  for (const t of dsThe) (nhom[t.hang] ?? nhom['chua-cham']).push(t)
  for (const h of Object.keys(nhom)) nhom[h].sort(soThe)
  return nhom
}

export function choPhepKeo(the, hangDich) {
  return Boolean(the && the.keo_duoc) && (hangDich === 'ai-lam' || hangDich === 'can-chot') && the.hang !== hangDich
}

// Tiêu đề tab "<tên trang> · Ben Station" (mockup app.js, D20); số việc chờ Phê duyệt đứng trước khi > 0.
export function tieuDeTab(so, ten = 'Tổng quan') {
  return `${so > 0 ? `(${so}) ` : ''}${ten} · Ben Station`
}

// Dự án `bat_ghi: false` (1a-2 G26, D37): chỉ đọc + quét thử — trạm từ chối mọi thao tác ghi (422). Thiếu trường
// (API cũ) coi như đã bật ghi.
export function duAnChiQuetThu(dsDuAn) {
  return new Set((dsDuAn || []).filter((d) => d && d.bat_ghi === false).map((d) => d.ten))
}
export const CHU_CHI_QUET_THU = 'Dự án chỉ quét thử (bat_ghi: false) — trạm từ chối thao tác ghi.'

// Chỉ link PR trên GitHub (N1): server đã lọc https://, trình duyệt chặn thêm host lạ.
export function laLinkAnToan(url) {
  return typeof url === 'string' && /^https:\/\/github\.com\/[^\s"'<>]+$/.test(url)
}

// Khoá v-for duy nhất: hai mục "Hệ cần xem" không bead cùng dự án (quet.loi + nho.loi_llm) khác nhau ở su_kien.
export function khoaMucPheDuyet(m) {
  return [m.loai, m.du_an, m.bead_id || '', (m.chi_tiet && m.chi_tiet.su_kien) || ''].join('/')
}

export function nhomPheDuyet(ds) {
  return THU_TU_PHE_DUYET.map((l) => [l, ds.filter((m) => m.loai === l)]).filter(([, m]) => m.length)
}

export function gioVN(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  return Number.isNaN(d.getTime()) ? String(iso)
    : d.toLocaleString('vi-VN', { timeZone: 'Asia/Ho_Chi_Minh', hour12: false })
}
