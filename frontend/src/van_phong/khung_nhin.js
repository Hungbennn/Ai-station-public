// Khít khung camera trực giao và chiếu điểm 3D ra toạ độ màn hình (mockup van-phong.js khit(), manHinhXY()).
// Thuần three (Vector3, ma trận camera), không DOM. Gọi SAU khi camera đã đặt position + lookAt (bài học 2c T8).
import { Vector3 } from 'three'
import { caoNv } from './nhan_vat_3d.js'

export const PHONG_TO = 1.12                       // phóng thêm, cắt nhẹ hai góc xa như ảnh demo

// Các góc sàn (đáy -0,3 m, đỉnh tường 2,6 m) của mọi phòng.
export function gocSan(phong) {
  const goc = []
  for (const p of phong) {
    for (const x of p.x) for (const z of p.z) for (const y of [-0.3, 2.6]) goc.push(new Vector3(x, y, z))
  }
  return goc
}

// Trả { left, right, top, bottom } để mọi góc nằm trong khung w×h (giữ tỉ lệ), chừa chỗ biển phía trên,
// rồi chia cho phongTo. Camera phải cập nhật ma trận thế giới trước (gọi ở đây).
export function khit(camera, goc, w, h, phongTo = PHONG_TO) {
  camera.updateMatrixWorld()
  let [x0, x1, y0, y1] = [Infinity, -Infinity, Infinity, -Infinity]
  const c = new Vector3()
  for (const v of goc) {
    c.copy(v).applyMatrix4(camera.matrixWorldInverse)
    x0 = Math.min(x0, c.x)
    x1 = Math.max(x1, c.x)
    y0 = Math.min(y0, c.y)
    y1 = Math.max(y1, c.y)
  }
  const le = 0.5
  x0 -= le
  x1 += le
  y0 -= le
  y1 += le + 1.2                                   // chừa chỗ biển tên phòng phía trên
  let cw = x1 - x0
  let ch = y1 - y0
  const cx = (x0 + x1) / 2
  const cy = (y0 + y1) / 2
  if (cw / ch > w / h) ch = (cw * h) / w
  else cw = (ch * w) / h
  cw /= phongTo
  ch /= phongTo
  return { left: cx - cw / 2, right: cx + cw / 2, top: cy + ch / 2, bottom: cy - ch / 2 }
}

// Cỡ chữ (px) của lớp nhãn co theo bề rộng khung như mockup boTriLai().
export function coChu(w) {
  return 16 * Math.max(0.7, Math.min(1.05, w / 1100))
}

const tam = new Vector3()
export function chieu(camera, w, h, [x, y, z]) {
  tam.set(x, y, z).project(camera)
  return { x: ((tam.x + 1) / 2) * w, y: ((1 - tam.y) / 2) * h }
}

// Toạ độ 2D của điểm neo mỗi nhãn + khung thân từng nhân vật (vật cản cho boTriNhan).
export function chieuNhan(camera, w, h, nhan, nhanVat) {
  const diem = Object.fromEntries(nhan.map((n) => [n.id, chieu(camera, w, h, n.neo)]))
  const than = nhanVat.map((nv) => {
    const a = chieu(camera, w, h, [nv.x, 0, nv.z])
    const b = chieu(camera, w, h, [nv.x, caoNv(nv), nv.z])
    const cao = a.y - b.y
    return { x: a.x - cao * 0.3, y: b.y - 2, w: cao * 0.6, h: cao + 6, khe: nv.khe_id }
  })
  return { W: w, H: h, diem, than }
}
