// Gọi tram-api. POST ghi gắn X-Tram (chống CSRF — spec §4 mục 3) và ma_thao_tac + expected_version (§12.3).
export function taoMaThaoTac() {
  return crypto.randomUUID()
}

export function thanGhi(noiDung, version, ma = taoMaThaoTac()) {
  return { ...noiDung, ma_thao_tac: ma, expected_version: version ?? '' }
}

async function xuLy(r) {
  let than = {}
  try {
    than = await r.json()
  } catch {
    than = {}
  }
  if (!r.ok) {
    const loi = new Error(than.loi || (typeof than.detail === 'string' ? than.detail : `Lỗi HTTP ${r.status}`))
    loi.status = r.status
    throw loi
  }
  return than
}

export async function doc(duongDan) {
  return xuLy(await fetch(duongDan, { headers: { Accept: 'application/json' } }))
}

const quyenGhi = new Map() // Chỉ RAM; giữ quyền của cùng snapshot khi mất phản hồi.
export async function ghi(duongDan, than, hienThi) {
  than = structuredClone(than)
  hienThi = structuredClone(hienThi || moTaGhi(duongDan, than))
  const key = JSON.stringify([duongDan, than])
  const gui = async () => xuLy(await fetch(duongDan, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-Tram': '1',
      ...(quyenGhi.has(key) ? { 'X-Tram-Xac-Nhan': quyenGhi.get(key) } : {}) },
    body: JSON.stringify(than),
  }))
  for (let lan = 0; ; lan++) {
    try {
      const out = await gui()
      quyenGhi.delete(key)
      return out
    } catch (e) {
      if (lan >= 2 || e.status !== 403) throw e
      const { nghiLe } = await import('./passkey.js')
      if (e.message === 'Cần phiên passkey') {
        quyenGhi.delete(key)
        await nghiLe('phien', { hienThi })
      } else if (e.message === 'Cần chạm lại cho thao tác này') {
        const { quyen } = await nghiLe('r', { duong: duongDan, than, hienThi })
        quyenGhi.set(key, quyen)
      } else throw e
    }
  }
}

export function boQuyenGhi(duong, than) { quyenGhi.delete(JSON.stringify([duong, than])) }

export async function guiPasskey(path, body) {
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), 15000)
  try {
    const r = await fetch('/api/passkey/' + path, { method: body ? 'POST' : 'GET',
      credentials: 'same-origin', cache: 'no-store', signal: controller.signal,
      headers: { 'Content-Type': 'application/json', 'X-Tram': '1' },
      body: body ? JSON.stringify(body) : undefined })
    const b = await r.json()
    if (!r.ok) {
      const e = new Error(b.loi || b.detail || 'Chưa xác nhận — thử lại')
      e.status = r.status
      throw e
    }
    return b
  } finally { clearTimeout(timer) }
}

export function moTaGhi(duong, than = {}) {
  const ten = { chot: 'Chốt việc', duyet: 'Duyệt việc', 'tra-loi': 'Trả lời quyết định',
    'tiep-tuc': 'Tiếp tục trạm', bat: 'Bật khe', 'cau-dao-dong': 'Đóng cầu dao',
    xoa: 'Xoá ký ức', deploy: 'Deploy', 'tu-deploy': 'Bật tự deploy',
    'lenh-deploy': 'Sửa lệnh deploy' }
  const parts = String(duong).split('/').filter(Boolean)
  if (duong === '/api/nho/xoa') {
    return { hanhDong: 'Xoá ký ức', dich: `Ký ức ${String(than.id || '').slice(0, 64)}` }
  }
  return { hanhDong: ten[parts.at(-1)] || 'Xác nhận thay đổi', dich: parts.slice(1, -1).join(' / ') || 'Trạm' }
}
