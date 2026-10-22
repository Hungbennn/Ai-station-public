// Bố trí Văn phòng 3D theo mockup van-phong.js PHONG (D20; hơn 3 dự án thêm hàng sau — D38/Q9) — hàm thuần,
// test bằng node --test. Mặt sàn là mặt phẳng XZ, trục Y hướng lên; lưới ô O = 10 m, gốc ở giữa ô Điều phối.
// Camera nhìn từ (40, 40, 40): +x xuống phải màn hình, +z xuống trái.
import { datNhanVat } from './cho_nv.js'
import { catChu } from './hien_thi.js'

export const O = 10
// Phòng cố định: ô, màu sàn/tường, chữ biển, neo biển (tương đối tâm ô đầu) — đúng số của mockup PHONG.
const CO_DINH = {
  giam_doc: { o: [[-1, -1]], san: '#f8e6d4', tuong: '#e8c6a8', ten: 'Phòng Giám đốc', nhan: [-1.6, -2.6] },
  dieu_phoi: { o: [[0, 0]], san: '#f7eee3', tuong: '#e1cfba', ten: 'Điều phối', nhan: [1.8, -3.6] },
  may_chu: { o: [[1, 0]], san: '#dce5ea', tuong: '#b2c2cc', ten: 'Phòng máy chủ', nhan: [3.8, -4] },
  ca_phe: { o: [[-1, 1], [0, 1]], san: '#f0e4d4', tuong: '#d9c2a6', ten: 'Góc cà phê', nhan: [4.6, 4] },
}
// Phòng dự án xoay vòng màu hr-codex / tram; dự án chỉ quét thử (bat_ghi false, D37) mờ xám như ke-toan.
const MAU_DU_AN = [{ san: '#f5d6d3', tuong: '#e3a7a2' }, { san: '#fbdcc8', tuong: '#efb796' }]
const MAU_MO = { san: '#ebe5de', tuong: '#d4cac0' }
const NEO_DU_AN = [[0.8, 3.9], [-1.5, 0.5], [-2.5, -3]]          // biển hr-codex, tram, ke-toan
const MAU_TU = new Set(['xanh', 'vang', 'do'])
const tron = (v) => Math.round(v * 100) / 100

// Ô thứ i của phòng dự án: ba ô trống của lưới 3×3 trước, rồi từng hàng 3 ô phía sau (z = -2, -3, …).
export function oDuAn(i) {
  if (i < 3) return [[-1, 0], [0, -1], [1, -1]][i]
  return [((i - 3) % 3) - 1, -2 - Math.floor((i - 3) / 3)]
}

function khoang(o) {
  const xs = o.map(([x]) => x)
  const zs = o.map(([, z]) => z)
  return {
    x: [Math.min(...xs) * O - O / 2, Math.max(...xs) * O + O / 2],
    z: [Math.min(...zs) * O - O / 2, Math.max(...zs) * O + O / 2],
  }
}

function moTaPhong(p, k, chiQuet) {
  if (p.loai !== 'du_an') return { ...CO_DINH[p.loai], mo: false }
  const mo = chiQuet.has(p.du_an)
  const ten = catChu(p.ten ?? p.du_an ?? p.ma, 28)
  return { o: [oDuAn(k)], ...(mo ? MAU_MO : MAU_DU_AN[k % 2]), ten: mo ? `${ten} (chỉ quét thử)` : ten,
    nhan: NEO_DU_AN[k] ?? NEO_DU_AN[1], mo }
}

// `duAn` từ /api/du-an: thiếu `bat_ghi` coi như true. Loại phòng lạ hoặc phòng cố định lặp thì bỏ.
export function boTriPhong(phong, duAn = []) {
  const chiQuet = new Set((duAn || []).filter((d) => d?.bat_ghi === false).map((d) => d.ten))
  const daCo = new Set()
  const ra = []
  let k = 0
  for (const p of phong || []) {
    if (p.loai !== 'du_an' && (!CO_DINH[p.loai] || daCo.has(p.loai))) continue
    daCo.add(p.loai)
    const c = moTaPhong(p, p.loai === 'du_an' ? k++ : 0, chiQuet)
    const tam = [c.o[0][0] * O, c.o[0][1] * O]
    ra.push({ ...p, o: c.o, ...khoang(c.o), tam, san: c.san, tuong: c.tuong, tenBien: c.ten, mo: c.mo,
      nhan: [tron(tam[0] + c.nhan[0]), tron(tam[1] + c.nhan[1])] })
  }
  return ra
}

// Tủ thứ i của Phòng máy chủ lấy màu `suc_khoe.muc[i].mau` (T6, D38/Q10); thiếu → xanh.
export function mauTuMay(p) {
  return [0, 1, 2, 3].map((i) => {
    const m = p?.suc_khoe?.muc?.[i]?.mau
    return MAU_TU.has(m) ? m : 'xanh'
  })
}

// Toàn bộ mặt bằng: phòng, nhân vật (x, z, ngoi, phongMa), bàn làm việc (x, z, man, khe?).
export function boTriVanPhong(phong, nhanVat, duAn) {
  const ds = boTriPhong(phong, duAn)
  return { phong: ds, ...datNhanVat(ds, nhanVat || []) }
}
