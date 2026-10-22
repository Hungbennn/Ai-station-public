// Menu sidebar 9 mục theo mockup (app.js MENU, D20). Phân luồng đã bỏ (D18). Ký ức giữ đường /nho, /ky-uc là bí danh
// (D38) — menu trỏ /ky-uc như mockup. Đường dẫn ở đây phải khớp tuyen.js.
export const MENU = [
  { ma: 'tong-quan', ten: 'Tổng quan', duong: '/tong-quan' },
  { ma: 'du-an', ten: 'Dự án', duong: '/du-an' },
  { ma: 'van-phong', ten: 'Văn phòng', duong: '/van-phong' },
  { ma: 'cong-viec', ten: 'Công việc', duong: '/cong-viec' },
  { ma: 'doi-ngu', ten: 'Đội ngũ AI', duong: '/doi-ngu' },
  { ma: 'ky-uc', ten: 'Ký ức', duong: '/ky-uc' },
  { ma: 'usage', ten: 'Usage & chi phí', duong: '/usage' },
  { ma: 'phe-duyet', ten: 'Phê duyệt', duong: '/phe-duyet', dem: true },
  { ma: 'cai-dat', ten: 'Cài đặt', duong: '/cai-dat' },
]
const BI_DANH = { '/nho': '/ky-uc', '/': '/tong-quan' }

// Mục menu của một đường dẫn (bỏ query); đường lạ → null.
export function mucCua(duong) {
  const p = String(duong || '/').split('?')[0].replace(/\/+$/, '') || '/'
  const goc = BI_DANH[p] ?? p
  return MENU.find((m) => goc === m.duong || goc.startsWith(`${m.duong}/`)) ?? null
}

export function tenTrang(duong) {
  if (String(duong).split('?')[0].replace(/\/+$/, '') === '/tai-khoan/thiet-bi') return 'Thiết bị'
  return mucCua(duong)?.ten ?? 'Ben Station'
}
