import { guiPasskey } from './api.js'
// Không ghi mã, cookie hay ceremony vào storage, URL hoặc console.
let hoi = async () => { throw new Error('Chưa mở được hộp xác nhận') }
export function datHoi(fn) { hoi = fn }
export function doc64(s) {
  return Uint8Array.from(atob(s.replace(/-/g, '+').replace(/_/g, '/')), c => c.charCodeAt(0)).buffer
}
export function ghi64(b) {
  return btoa(String.fromCharCode(...new Uint8Array(b))).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')
}
export function tuyChon(o) {
  const r = { ...o, challenge: doc64(o.challenge) }
  if (o.user) r.user = { ...o.user, id: doc64(o.user.id) }
  for (const k of ['allowCredentials', 'excludeCredentials']) {
    if (o[k]) r[k] = o[k].map(c => ({ ...c, id: doc64(c.id) }))
  }
  return r
}
export function phanHoi(c) {
  const response = {}
  for (const k of ['clientDataJSON', 'attestationObject', 'authenticatorData', 'signature', 'userHandle']) {
    if (c.response[k] !== undefined) response[k] = c.response[k] === null ? null : ghi64(c.response[k])
  }
  return { id: c.id, rawId: ghi64(c.rawId), type: c.type, response }
}
export const goiPasskey = guiPasskey
export async function nghiLe(loai, them = {}, deps = {}) {
  them = structuredClone(them)
  const hienThi = Object.freeze({
    hanhDong: String(them.hienThi?.hanhDong || 'Xác nhận thao tác').slice(0, 100),
    dich: String(them.hienThi?.dich || them.duong || 'Phiên trình duyệt này').slice(0, 300),
  })
  if (!await hoi({ loai, hienThi })) throw new Error('Đã huỷ xác nhận')
  const goi = deps.goi || goiPasskey
  const credentials = deps.credentials || globalThis.navigator?.credentials
  if (!credentials) throw new Error('Trình duyệt chưa hỗ trợ passkey; dùng browser hoặc thiết bị khác')
  const o = await goi('bat-dau', { loai, ...them })
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), 120000)
  try {
    const method = loai === 'dang-ky' ? 'create' : 'get'
    const c = await credentials[method]({ publicKey: tuyChon(o.publicKey), signal: controller.signal })
    if (!c) throw new Error('Đã huỷ')
    return await goi('ket-thuc', { id: o.id, credential: phanHoi(c), ten: them.ten })
  } catch {
    throw new Error('Chưa xác nhận — thử lại. Đại ca có thể chọn thiết bị khác trong hộp trình duyệt.')
  } finally { clearTimeout(timer) }
}
let dangCho = null
export function boQuanLy() { dangCho = null }
export async function quanLy(viec, than, hienThi) {
  const key = JSON.stringify([viec, than])
  if (!dangCho || dangCho.key !== key) {
    dangCho = { key, than: structuredClone(than), hienThi: structuredClone(hienThi), quyen: null }
  }
  const cho = dangCho
  const gui = () => goiPasskey(viec, { than: cho.than, quyen: cho.quyen })
  if (cho.quyen) {
    try {
      const out = await gui()
      if (dangCho === cho) boQuanLy()
      return out
    } catch (e) {
      if (e.status !== 403 || !['Cần phiên passkey', 'Cần chạm lại cho thao tác này'].includes(e.message)) throw e
      cho.quyen = null
    }
  }
  const tt = await goiPasskey('trang-thai')
  if (!tt.con_giay) await nghiLe('phien', { hienThi: cho.hienThi })
  const { quyen } = await nghiLe('r', { duong: '/api/passkey/' + viec, than: cho.than, hienThi: cho.hienThi })
  cho.quyen = quyen
  const out = await gui()
  if (dangCho === cho) boQuanLy()
  return out
}
export function hienPhien(tt) {
  if (!tt?.thiet_bi.length) return 'Chưa có passkey'
  return tt.con_giay > 0 ? `Đã xác nhận, còn ${Math.ceil(tt.con_giay / 60)} phút` : 'Cần xác nhận passkey'
}
