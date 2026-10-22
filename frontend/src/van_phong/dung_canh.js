// Ghép cảnh Văn phòng từ mặt bằng bo_tri (mockup van-phong.js dungVanPhong, D20): phòng + đồ đạc + nhân vật,
// cộng ánh sáng như mockup. CanhVanPhong gắn bằng <primitive :object> và tự gọi huyCanh (Tres không tự huỷ
// primitive — nodeOps.remove bỏ qua dispose khi là primitive).
import { AmbientLight, DirectionalLight, Group, HemisphereLight } from 'three'
import { dungDoVat } from './dung_do_vat.js'
import { dungPhong } from './dung_phong.js'
import { phaNv, taoNhanVat } from './nhan_vat_3d.js'

// Ánh sáng mockup: Ambient + Hemisphere + Directional đổ bóng (map 2048, khung ±26). three 0.186 bỏ
// PCFSoftShadowMap → TresCanvas dùng PCFShadowMap, làm mềm bằng shadow.radius (D38/Q17).
export function taoAnhSang() {
  const g = new Group()
  g.add(new AmbientLight('#fff3e4', 1.15))
  g.add(new HemisphereLight('#fff8ef', '#d8bfa2', 0.75))
  const mat = new DirectionalLight('#ffe9d2', 1.55)
  mat.position.set(-8, 34, 22)
  mat.castShadow = true
  mat.shadow.mapSize.set(2048, 2048)
  Object.assign(mat.shadow.camera, { left: -26, right: 26, top: 26, bottom: -26, near: 1, far: 90 })
  mat.shadow.camera.updateProjectionMatrix()
  mat.shadow.bias = -0.0006
  mat.shadow.normalBias = 0.03
  mat.shadow.radius = 3
  g.add(mat)
  return g
}

// Trả { goc: Group, dong: [{ g, nv, man, pha }] } — `dong` cho chuyenDongNv mỗi khung hình.
// goc.userData: tu (LED đầu mỗi tủ máy), den (bóng đèn Điều phối) — để test và kiểm.
export function dungCanh(boTri) {
  const goc = new Group()
  goc.add(dungPhong(boTri.phong))
  const dv = dungDoVat(boTri)
  goc.add(dv.nhom)
  const dong = boTri.nhanVat.map((nv) => {
    const g = taoNhanVat(nv)
    goc.add(g)
    return { g, nv, man: nv.hien_thi === 'loi' ? dv.manDo.get(nv.khe_id) ?? null : null, pha: phaNv(nv.khe_id) }
  })
  goc.userData.tu = dv.tu
  goc.userData.den = dv.den
  return { goc, dong }
}

// Giải phóng geometry, material, bóng đổ của đèn (mockup huy()).
export function huyCanh(obj) {
  if (!obj) return
  obj.traverse((o) => {
    o.geometry?.dispose()
    for (const m of [].concat(o.material ?? [])) m.dispose()
    if (o.isLight) o.dispose()
  })
}
