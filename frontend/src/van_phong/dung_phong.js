// Mặt bằng (mockup van-phong.js dungPhong, D20): sàn mỗi phòng + tường. Cạnh chung hai phòng là tường có cửa
// (hai đoạn, hở giữa), cạnh sau cao 1,6 m, cạnh trước thấp 0,45 m để thấy bên trong. Hàm thuần three, không DOM.
import { BoxGeometry, Group, Mesh } from 'three'
import { O } from './bo_tri.js'
import { hop, khongBam, vatLieu } from './do_vat.js'

// Các cạnh dài O m của một phòng: [x0, z0, x1, z1, truoc] — truoc = cạnh phía camera (+x hoặc +z).
function canhCua(p) {
  const ra = []
  for (let x = p.x[0]; x < p.x[1]; x += O) ra.push([x, p.z[0], x + O, p.z[0], false], [x, p.z[1], x + O, p.z[1], true])
  for (let z = p.z[0]; z < p.z[1]; z += O) ra.push([p.x[0], z, p.x[0], z + O, false], [p.x[1], z, p.x[1], z + O, true])
  return ra
}

function tuong(c) {
  const trong = c.so > 1
  const cao = trong ? 1.3 : c.truoc ? 0.45 : 1.6
  const doc = c.x0 === c.x1
  const doan = trong ? [[0, 3.5], [6.5, O]] : [[0, O]]
  return doan.map(([a, b]) => {
    const dai = b - a + (trong ? 0 : 0.35)
    const m = new Mesh(new BoxGeometry(doc ? 0.32 : dai, cao, doc ? dai : 0.32),
      vatLieu(c.mau, { transparent: true, opacity: c.mo ? 0.35 : 0.62, depthWrite: false }))
    const giua = (a + b) / 2
    if (doc) m.position.set(c.x0, cao / 2, c.z0 + giua)
    else m.position.set(c.x0 + giua, cao / 2, c.z0)
    m.receiveShadow = true
    return khongBam(m)
  })
}

// Sàn mang userData.chon = { loai: 'phong', ma } để bấm chọn phòng (CanhVanPhong đi ngược parent tìm chon).
export function dungPhong(phong) {
  const nhom = new Group()
  const canh = new Map()
  for (const p of phong) {
    const w = p.x[1] - p.x[0]
    const d = p.z[1] - p.z[0]
    const san = hop(w, 0.3, d, p.san, { bong: false })
    san.position.set((p.x[0] + p.x[1]) / 2, -0.15, (p.z[0] + p.z[1]) / 2)
    san.userData.chon = { loai: 'phong', ma: p.ma }
    if (p.mo) Object.assign(san.material, { transparent: true, opacity: 0.75 })
    nhom.add(san)
    for (const [x0, z0, x1, z1, truoc] of canhCua(p)) {
      const k = `${x0},${z0},${x1},${z1}`
      const c = canh.get(k)
      if (c) c.so++
      else canh.set(k, { x0, z0, x1, z1, so: 1, mau: p.tuong, truoc, mo: p.mo })
    }
  }
  for (const c of canh.values()) nhom.add(...tuong(c))
  return nhom
}
