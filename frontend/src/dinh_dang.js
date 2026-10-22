// Định dạng số / giờ dùng chung các trang mới (mockup: "1,84 tr", "212 n", "22:14", "3 phút trước", "T2 07:00").
// Giờ luôn theo Asia/Ho_Chi_Minh như gioVN (luat.js). Hàm thuần, test bằng node --test.
const VN = 'Asia/Ho_Chi_Minh'
const THU = ['CN', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7']

const phan = (iso) => {
  const d = new Date(iso)
  if (!iso || Number.isNaN(d.getTime())) return null
  const p = Object.fromEntries(new Intl.DateTimeFormat('en-GB', { timeZone: VN, hour12: false, weekday: 'short',
    year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
    .formatToParts(d).map((x) => [x.type, x.value]))
  const thu = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].indexOf(p.weekday)
  return { ...p, hour: p.hour === '24' ? '00' : p.hour, thu }
}

// Số gọn của mockup Usage (D39): ≥ 1 tỷ "x,xx tỷ"; ≥ 1 triệu "x,xx tr"; ≥ 1 nghìn "n n"; không phải số → "—".
export function gon(n) {
  if (typeof n !== 'number' || Number.isNaN(n)) return '—'
  const a = Math.abs(n)
  if (a >= 1e9) return `${(n / 1e9).toFixed(2).replace('.', ',')} tỷ`
  if (a >= 1e6) return `${(n / 1e6).toFixed(2).replace('.', ',')} tr`
  if (a >= 1e3) return `${Math.round(n / 1e3)} n`
  return String(n)
}

export function soDayDu(n) {
  return typeof n === 'number' ? n.toLocaleString('vi-VN') : '—'
}

export function usd(x) {
  if (typeof x !== 'number') return 'chưa có giá'
  return `$${x < 1 && x > 0 ? x.toFixed(4) : x.toFixed(2)}`
}

export function gioPhut(iso) {
  const p = phan(iso)
  return p ? `${p.hour}:${p.minute}` : ''
}

export function ngayGio(iso) {
  const p = phan(iso)
  return p ? `${p.day}/${p.month} ${p.hour}:${p.minute}` : ''
}

export function ngayNgan(isoNgay) {
  const m = /^(\d{4})-(\d{2})-(\d{2})/.exec(String(isoNgay || ''))
  return m ? `${m[3]}/${m[2]}` : ''
}

// "6 giây trước", "3 phút trước", "2 giờ trước", "4 ngày trước"; tương lai hoặc lỗi → "".
export function truocDay(iso, bayGio = new Date()) {
  const giay = Math.floor((new Date(bayGio).getTime() - new Date(iso).getTime()) / 1000)
  if (!iso || Number.isNaN(giay) || giay < 0) return ''
  if (giay < 60) return `${giay} giây trước`
  if (giay < 3600) return `${Math.floor(giay / 60)} phút trước`
  if (giay < 86400) return `${Math.floor(giay / 3600)} giờ trước`
  return `${Math.floor(giay / 86400)} ngày trước`
}

// "còn 2 giờ", "còn 15 phút" tới mốc; đã qua → "".
export function conLai(iso, bayGio = new Date()) {
  const phut = Math.ceil((new Date(iso).getTime() - new Date(bayGio).getTime()) / 60000)
  if (!iso || Number.isNaN(phut) || phut <= 0) return ''
  return phut < 60 ? `còn ${phut} phút` : `còn ${Math.round(phut / 60)} giờ`
}

// Giờ reset hạn mức: trong 24 giờ tới → "23:40", xa hơn → "T2 07:00" (mockup Đội ngũ AI).
export function gioReset(iso, bayGio = new Date()) {
  const p = phan(iso)
  if (!p) return '—'
  const xa = new Date(iso).getTime() - new Date(bayGio).getTime() > 86400000
  return xa ? `${THU[p.thu]} ${p.hour}:${p.minute}` : `${p.hour}:${p.minute}`
}
