// Đồ vật dựng bằng three thuần (mockup van-phong.js "Đồ vật", D20): vật liệu, hộp, màn hình, bàn, cây, cốc, ghế.
// Không DOM, không WebGL — chạy được trong node --test.
import { BoxGeometry, ConeGeometry, CylinderGeometry, Group, Mesh, MeshStandardMaterial, TorusGeometry } from 'three'
import { MAU } from './hien_thi.js'

export const MAN = { sang: MAU.man, do: MAU.manDo, tat: MAU.manTat }

export function vatLieu(mau, them = {}) {
  return new MeshStandardMaterial({ color: mau, roughness: 0.88, metalness: 0, ...them })
}

export function dat(obj, x, y, z) {
  obj.position.set(x, y, z)
  return obj
}

// Mesh có bóng đổ + nhận bóng (mặc định của mọi đồ đạc mockup).
export function khoi(geo, mat, bong = true) {
  const m = new Mesh(geo, mat)
  m.castShadow = bong
  m.receiveShadow = true
  return m
}

export function hop(w, h, d, mau, { bong = true, them } = {}) {
  return khoi(new BoxGeometry(w, h, d), vatLieu(mau, them), bong)
}

// Vật không nhận bấm (tường, bóng tròn dưới chân): tia dò bỏ qua để bấm xuyên tới sàn / nhân vật phía sau.
export function khongBam(o) {
  o.raycast = () => {}
  return o
}

export function lamMo(obj, doMo) {
  obj.traverse((o) => {
    if (!o.material) return
    o.material = o.material.clone()
    o.material.transparent = true
    o.material.opacity = Math.min(o.material.opacity ?? 1, doMo)
    o.castShadow = false
  })
}

function manHinh(mau) {
  const g = new Group()
  g.add(dat(hop(0.14, 0.4, 0.14, MAU.vien), 0, 0.2, 0))
  g.add(dat(hop(1.25, 0.82, 0.12, MAU.vien), 0, 0.72, 0))
  const sang = mau !== MAU.manTat
  const man = new Mesh(new BoxGeometry(1.08, 0.66, 0.02),
    vatLieu(mau, sang ? { emissive: mau, emissiveIntensity: 0.45 } : {}))
  g.add(dat(man, 0, 0.72, 0.07))
  g.userData.man = man
  return g
}

// Bàn làm việc; `mauMan` null = bàn không màn hình. userData.man = mặt màn hình (để nhấp nháy khi lỗi).
export function banLamViec(nhom, x, z, { mauMan = MAU.man, w = 2.8, d = 1.5 } = {}) {
  const g = new Group()
  g.add(dat(hop(w, 1.0, d, MAU.go), 0, 0.5, 0))
  if (mauMan) {
    const mh = manHinh(mauMan)
    mh.rotation.y = Math.PI / 4                 // màn hình quay mặt về phía camera (+x+z)
    g.add(dat(mh, 0.3, 1.0, -0.25))
    g.userData.man = mh.userData.man
  }
  nhom.add(dat(g, x, 0, z))
  return g
}

export function cayXanh(nhom, x, z, cao = 1) {
  const g = new Group()
  g.add(dat(khoi(new CylinderGeometry(0.36, 0.28, 0.55, 16), vatLieu(MAU.chau)), 0, 0.275, 0))
  g.add(dat(khoi(new CylinderGeometry(0.33, 0.33, 0.05, 16), vatLieu(MAU.dat)), 0, 0.55, 0))
  for (let i = 0; i < 7; i++) {
    const la = khoi(new ConeGeometry(0.1, 0.9 * cao, 6), vatLieu(i % 2 ? MAU.la : MAU.la2))
    const a = (i / 7) * Math.PI * 2
    la.position.set(Math.cos(a) * 0.12, 0.55 + 0.42 * cao, Math.sin(a) * 0.12)
    la.rotation.set(Math.sin(a) * 0.45, 0, -Math.cos(a) * 0.45)
    g.add(la)
  }
  nhom.add(dat(g, x, 0, z))
}

export function coc(nhom, x, y, z) {
  const g = new Group()
  g.add(dat(khoi(new CylinderGeometry(0.2, 0.16, 0.34, 16), vatLieu(MAU.su)), 0, 0.17, 0))
  g.add(dat(khoi(new CylinderGeometry(0.17, 0.17, 0.02, 16), vatLieu(MAU.cafe)), 0, 0.33, 0))
  g.add(dat(khoi(new TorusGeometry(0.09, 0.03, 6, 12), vatLieu(MAU.su)), 0.21, 0.17, 0))
  nhom.add(dat(g, x, y, z))
}

export function ghe(nhom, x, z) {
  nhom.add(dat(khoi(new CylinderGeometry(0.36, 0.32, 0.55, 14), vatLieu(MAU.ghe)), x, 0.275, z))
}
