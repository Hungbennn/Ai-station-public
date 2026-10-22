// Luật thuần của trang Cài đặt (D19 — chỉ đọc). Mockup trang-cai-dat.js, khảo sát §1.6.
// Lệnh CLI là hằng chữ phía trình duyệt: trạm KHÔNG chạy, chỉ hiện để Đại ca tự chạy; `gui/$(id -u)` giữ nguyên văn.
import { duAnChiQuetThu } from './luat.js'

const l = (lenh, ghiChu = '') => ({ lenh, ghi_chu: ghiChu })

export const LENH_SAN_SANG = [
  l('uv run tram giao kiem', 'xanh/vàng/đỏ, mã ≠ 0 nếu có đỏ'),
  l('bd list --status open --label san-sang'),
]
export const LENH_DICH_VU = [
  l('uv run tram chu trang-thai'),
  l('uv run tram chu cai-dat', 'liệt kê thay đổi, Đại ca gõ dong-y'),
  l('launchctl kickstart -k gui/$(id -u)/vn.tram.<tên>', 'chạy lại một dịch vụ đã cài'),
]
export const LENH_TELEGRAM = [
  l('$EDITOR ~/.tram/cau-hinh.yaml'),
  l('launchctl kickstart -k gui/$(id -u)/vn.tram.bao-tin'),
]
export const LENH_CO = [l('$EDITOR ~/.tram/cau-hinh.yaml', 'vd giao_viec.bat: true — chỉ sau mọi cổng')]
export const LENH_KEYCHAIN = [
  l('uv run tram chu cai-dat --nho', 'tạo tram-noi-bo-token'),
  l('security add-generic-password -U -s tram-telegram-bot-token -a tram -w', 'dán trong Terminal.app'),
]

// Dự án đầu danh sách làm ví dụ; chưa có dự án nào thì giữ chỗ `<tên>`.
const tenDau = (ds) => (ds && ds.length ? ds[0].ten : '<tên>')
export function lenhDuAn(ds) {
  return [
    l(`$EDITOR du-an/${tenDau(ds)}.yaml`, 'sửa khoá rồi chạy lệnh dưới'),
    l('uv run tram du-an them <đường dẫn repo>'),
  ]
}
// Bật ghi chỉ sửa tay file YAML (D31/G25) — không có lệnh CLI riêng.
export const cauBatGhi = (ds) => `sửa tay bat_ghi: true trong du-an/${tenDau(ds)}.yaml`

const NHAN_SAN_SANG = {
  dat: { chu: 'Đạt', lop: 'tt-lam' },
  thieu: { chu: 'Thiếu', lop: 'tt-can_nguoi' },
  cho: { chu: 'Chưa tới lượt', lop: 'tt-tat' },
}
export const nhanSanSang = (tt) => NHAN_SAN_SANG[tt] || { chu: String(tt), lop: 'tt-tat' }
// Mục tự kiểm (không phải bead, vd Ollama) hiện "—" như mockup.
export const maSanSang = (m) => (m.nguon === 'tu_kiem' ? '—' : m.ma)

export function demSanSang(ss) {
  if (ss && ss.dem) return { dat: ss.dem.dat || 0, thieu: ss.dem.thieu || 0, cho: ss.dem.cho || 0 }
  const dem = { dat: 0, thieu: 0, cho: 0 }
  for (const m of (ss && ss.muc) || []) if (m.trang_thai in dem) dem[m.trang_thai] += 1
  return dem
}

const KHONG_RO = { chu: 'không rõ', lop: 'tt-cau_dao' }
export function oDaCai(d) {
  if (typeof d.da_cai !== 'boolean') return KHONG_RO
  return d.da_cai ? { chu: 'có', lop: 'tt-lam' } : { chu: 'chưa', lop: 'tt-tat' }
}
// `kiem_duoc: false` = launchctl không trả lời được → không đoán.
export function oDangChay(d) {
  if (d.kiem_duoc === false || typeof d.dang_chay !== 'boolean') return KHONG_RO
  return d.dang_chay ? { chu: 'chạy', lop: 'tt-lam' } : { chu: '—', lop: 'tt-tat' }
}

const NHAN_KEYCHAIN = {
  co: { chu: '● có', lop: 'tt-lam' },
  chua: { chu: '○ chưa có', lop: 'tt-can_nguoi' },
}
export const nhanKeychain = (tt) => NHAN_KEYCHAIN[tt] || { chu: 'không kiểm được', lop: 'tt-cau_dao' }

// Cờ: giá trị chuỗi (vd phương án công bố) ưu tiên; null cả hai = chưa chốt.
export function nhanCo(c) {
  if (c.gia_tri != null) return { chu: String(c.gia_tri), lop: '', mono: true }
  if (c.bat === true) return { chu: 'bật', lop: 'tt-lam', mono: false }
  if (c.bat === false) return { chu: 'tắt', lop: 'tt-tat', mono: false }
  return { chu: 'chưa chốt', lop: 'tt-cau_dao', mono: false }
}
export const nhanChatId = (co) => (co ? { chu: 'có', lop: 'tt-lam' } : { chu: 'chưa có', lop: 'tt-can_nguoi' })

// /api/cai-dat không có bat_ghi → lấy từ /api/du-an (D37); thiếu coi như bật ghi.
export function ghepBatGhi(dsCaiDat, dsDuAn) {
  const chiQuet = duAnChiQuetThu(dsDuAn)
  return (dsCaiDat || []).map((d) => ({ ...d, chi_quet_thu: chiQuet.has(d.ten) }))
}
export const chuHangRao = (h) => [...(h.tu_khoa || []), ...(h.duong_dan || [])].join(', ')
