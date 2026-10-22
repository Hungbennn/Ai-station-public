// Hạn mức khe theo mockup Đội ngũ AI (trang.js thanhHm): thanh "còn x% · reset hh:mm", lớp thấp (< 30%) / hết (0%).
// `phan_tram` của server là phần ĐÃ DÙNG (spec 3 §8.1) — ở đây đổi sang phần CÒN LẠI như mockup. Hàm thuần.
import { gioReset } from './dinh_dang.js'

export function cuaSo(khe, loai) {
  return ((khe && khe.han_muc && khe.han_muc.cua_so) || []).find((c) => c.loai === loai) ?? null
}

export function oHanMuc(cs, bayGio = new Date()) {
  if (!cs || cs.trang_thai !== 'biet' || typeof cs.phan_tram !== 'number') {
    return { con: null, lop: '', rong: 0, chu: 'chưa biết' }
  }
  const con = Math.max(0, Math.min(100, Math.round(100 - cs.phan_tram)))
  const lop = con === 0 ? 'het' : con < 30 ? 'thap' : ''
  return { con, lop, rong: Math.max(con, 2), chu: `còn ${con}% · reset ${gioReset(cs.reset_luc, bayGio)}` }
}

// Khe có cửa sổ 5 giờ còn ít nhất (mockup Tổng quan "Hạn mức thấp nhất"); không khe nào biết → null.
export function hanMucThapNhat(dsKhe, bayGio = new Date()) {
  let tot = null
  for (const k of dsKhe || []) {
    const o = oHanMuc(cuaSo(k, '5h'), bayGio)
    if (o.con !== null && (!tot || o.con < tot.con)) tot = { khe: k, con: o.con, reset: o.chu.split(' · reset ')[1] }
  }
  return tot
}

// Tên hiển thị của khe: `ten` từ server (lát 2f T1, "Claude 1"); thiếu thì dựng từ khe_id "B/codex-1" → "Codex 1".
export function tenKhe(khe) {
  if (khe && khe.ten) return khe.ten
  const rieng = String((khe && khe.khe_id) || khe || '').split('/').pop()
  return rieng.split('-').map((x, i) => (i === 0 ? x.charAt(0).toUpperCase() + x.slice(1) : x)).join(' ')
}
