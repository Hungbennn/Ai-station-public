// Đồ vật phản ánh trạng thái trạm (mockup van-phong.js dungDoVat, D20): đèn Điều phối (2e, D38 vàng ấm) và bốn tủ
// máy chủ có đèn LED theo `suc_khoe.muc` (T6, D38/Q10). Toạ độ tương đối tâm ô của phòng.
import { CylinderGeometry, Mesh, MeshBasicMaterial, SphereGeometry } from 'three'
import { mauTuMay } from './bo_tri.js'
import { MAU } from './hien_thi.js'
import { banLamViec, dat, hop, khoi, vatLieu } from './do_vat.js'

// Phòng Điều phối: hai bàn + cột đèn. `sang === true` → bóng vàng ấm phát sáng; còn lại (false / null) → xám.
export function doDieuPhoi(g, tx, tz, p) {
  banLamViec(g, tx - 2.5, tz + 2.0)
  banLamViec(g, tx + 2.0, tz + 3.0)
  const [x, z] = [tx - 3.5, tz + 4.2]
  g.add(dat(khoi(new CylinderGeometry(0.07, 0.07, 2.3, 8), vatLieu(MAU.cot)), x, 1.15, z))
  g.add(dat(khoi(new CylinderGeometry(0.4, 0.4, 0.08, 16), vatLieu(MAU.cot)), x, 0.04, z))
  const sang = p.sang === true
  const den = new Mesh(new SphereGeometry(0.36, 20, 14), vatLieu(sang ? MAU.den : MAU.denTat,
    sang ? { emissive: MAU.den, emissiveIntensity: 0.9 } : { emissive: '#000000' }))
  den.castShadow = !sang
  g.add(dat(den, x, 2.45, z))
  return { den }
}

// Phòng máy chủ: 4 tủ đen xếp chéo, 3 đèn LED ở mặt +z. Tủ xanh tắt đèn giữa (như mockup); vàng/đỏ sáng cả ba.
export function doMayChu(g, tx, tz, p) {
  const tu = []
  mauTuMay(p).forEach((mau, i) => {
    const x = tx - 3.2 + i * 2.1
    const z = tz - 1.2 + i * 1.3
    g.add(dat(hop(1.6, 2.7, 1.6, MAU.tu), x, 1.35, z))
    for (let k = 0; k < 3; k++) {
      const m = k === 1 && mau === 'xanh' ? MAU.ledTat : MAU.suc_khoe[mau]
      const led = new Mesh(new SphereGeometry(0.1, 10, 8), new MeshBasicMaterial({ color: m }))
      g.add(dat(led, x - 0.35, 2.2 - k * 0.45, z + 0.81))
      if (k === 0) tu.push(led)
    }
  })
  return { tu }
}
