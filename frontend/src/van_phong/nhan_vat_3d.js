// Nhân vật chibi (mockup van-phong.js nhanVat, D20): bóng tròn, ghế khi ngồi, chân, thân, đầu, tóc, hai tay.
// Màu thân/tóc theo khe (mau_khe.js, chung với Đội ngũ AI). Giơ tay khi can_nguoi, mờ khi tat. Three thuần.
import { CircleGeometry, CylinderGeometry, Group, Mesh, MeshBasicMaterial, SphereGeometry } from 'three'
import { fnv1a, mauKhe } from '../mau_khe.js'
import { MAU } from './hien_thi.js'
import { dat, ghe, khoi, khongBam, lamMo, vatLieu } from './do_vat.js'

export const CO_NV = 1.4                                  // phóng nhân vật cho giống tỉ lệ ảnh demo
const yThan = (nv) => (nv.ngoi ? 0.55 : 0.52)
// Chiều cao đỉnh đầu (m, đã nhân CO_NV) — neo bong bóng / huy hiệu và khung thân cho bo_tri_nhan.
export const caoNv = (nv) => (yThan(nv) + 1.95) * CO_NV

function chan(than, ngoi, mau) {
  for (const s of [-1, 1]) {
    const c = khoi(new CylinderGeometry(0.13, 0.12, 0.56, 12), mau)
    if (ngoi) {
      c.rotation.x = Math.PI / 2
      dat(c, s * 0.17, 0.62, 0.3)
    } else dat(c, s * 0.17, 0.28, 0)
    than.add(c)
  }
}

function tay(than, y0, mau) {
  return [-1, 1].map((s) => {
    const truc = dat(new Group(), s * 0.42, y0 + 0.82, 0)
    truc.add(dat(khoi(new CylinderGeometry(0.1, 0.09, 0.62, 10), mau), 0, -0.28, 0))
    truc.rotation.z = s * 0.12
    than.add(truc)
    return truc
  })
}

// nv: phần tử nhanVat của bo_tri (x, z, ngoi, hien_thi, khe_id). userData: chon, than, tay.
export function taoNhanVat(nv) {
  const mau = mauKhe(nv.khe_id)
  const g = new Group()
  const bong = new Mesh(new CircleGeometry(0.66, 28),
    new MeshBasicMaterial({ color: MAU.bong, transparent: true, opacity: 0.18, depthWrite: false }))
  bong.rotation.x = -Math.PI / 2
  g.add(khongBam(dat(bong, 0, 0.03, 0)))
  const than = new Group()
  g.add(than)
  if (nv.ngoi) ghe(than, 0, -0.05)
  chan(than, nv.ngoi, vatLieu(MAU.chan))
  const y0 = yThan(nv)
  const mauThan = vatLieu(mau.than)
  than.add(dat(khoi(new CylinderGeometry(0.34, 0.42, 0.92, 22), mauThan), 0, y0 + 0.46, 0))
  than.add(dat(khoi(new SphereGeometry(0.5, 28, 20), vatLieu(MAU.da)), 0, y0 + 1.36, 0))
  const toc = khoi(new SphereGeometry(0.53, 28, 14, 0, Math.PI * 2, 0, Math.PI * 0.52), vatLieu(mau.toc))
  toc.rotation.x = -0.42
  than.add(dat(toc, 0, y0 + 1.4, -0.02))
  const hai = tay(than, y0, mauThan)
  if (nv.hien_thi === 'can_nguoi') hai[1].rotation.z = Math.PI - 0.35          // giơ tay phải
  g.rotation.y = Math.PI / 4                                                 // quay mặt về phía camera
  if (nv.hien_thi === 'tat') lamMo(g, 0.36)
  g.position.set(nv.x, 0, nv.z)
  g.scale.setScalar(CO_NV)
  g.userData = { chon: { loai: 'khe', khe_id: nv.khe_id }, than, tay: hai }
  return g
}

export const phaNv = (kheId) => (fnv1a(kheId) % 628) / 100

// Một khung hình chuyển động (mockup ve()): nhún khi lam, vẫy tay khi can_nguoi, xoay nhẹ khi ranh,
// màn đỏ nhấp nháy khi loi. Chỉ gọi khi KHÔNG bật "Giảm chuyển động" (dựng lại cảnh trả về tư thế tĩnh).
export function chuyenDongNv(muc, t) {
  const { than, tay: hai } = muc.g.userData
  const ht = muc.nv.hien_thi
  than.position.y = ht === 'lam' ? Math.abs(Math.sin(t * 3.4 + muc.pha)) * 0.12 : 0
  if (ht === 'can_nguoi') hai[1].rotation.z = Math.PI - 0.35 + Math.sin(t * 5) * 0.22
  if (ht === 'ranh') than.rotation.y = Math.sin(t * 0.9 + muc.pha) * 0.25
  if (muc.man) muc.man.material.emissiveIntensity = 0.35 + Math.abs(Math.sin(t * 2.2)) * 0.5
}
