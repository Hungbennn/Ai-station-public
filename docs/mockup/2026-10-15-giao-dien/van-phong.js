// Cảnh Văn phòng 3D isometric (mockup) — three.js thuần, camera trực giao đặt ở (40,40,40) rồi lookAt gốc.
// Chữ (biển phòng, tên khe, bong bóng, huy hiệu) là HTML phủ lên canvas, chiếu toạ độ mỗi khung hình.
import * as THREE from 'three'
import { KHE, NHAN_HIEN_THI, TEN_BUOC, so_viec_cho } from './du-lieu.js'
import { boTriNhan, demChong } from './bo-tri-nhan.js'

// Mặt bằng: lưới ô 10 m, gốc toạ độ ở giữa. +x xuống phải màn hình, +z xuống trái.
export const PHONG = [
  { ma: 'giam-doc', ten: 'Phòng Giám đốc', loai: 'giam_doc', x: [-15, -5], z: [-15, -5], san: '#f8e6d4', tuong: '#e8c6a8', nhan: [-11.6, -12.6] },
  { ma: 'tram', ten: 'tram', loai: 'du_an', x: [-5, 5], z: [-15, -5], san: '#fbdcc8', tuong: '#efb796', nhan: [-1.5, -9.5] },
  { ma: 'ke-toan', ten: 'ke-toan (tạm đóng)', loai: 'du_an', mo: true, x: [5, 15], z: [-15, -5], san: '#ebe5de', tuong: '#d4cac0', nhan: [7.5, -13.0] },
  { ma: 'hr-codex', ten: 'hr-codex', loai: 'du_an', x: [-15, -5], z: [-5, 5], san: '#f5d6d3', tuong: '#e3a7a2', nhan: [-9.2, 3.9] },
  { ma: 'dieu-phoi', ten: 'Điều phối', loai: 'dieu_phoi', x: [-5, 5], z: [-5, 5], san: '#f7eee3', tuong: '#e1cfba', nhan: [1.8, -3.6] },
  { ma: 'may-chu', ten: 'Phòng máy chủ', loai: 'may_chu', x: [5, 15], z: [-5, 5], san: '#dce5ea', tuong: '#b2c2cc', nhan: [13.8, -4.0] },
  { ma: 'ca-phe', ten: 'Góc cà phê', loai: 'ca_phe', x: [-15, 5], z: [5, 15], san: '#f0e4d4', tuong: '#d9c2a6', nhan: [-5.4, 14.0] },
]

const MAU = {
  go: '#c79d74', goDam: '#7a2c14', quay: '#c9805e', man: '#9fd0ee', manDo: '#e0574a', manTat: '#8d949a',
  vien: '#2f3439', da: '#f2c9a3', chan: '#2b2523', tu: '#30363c', ghe: '#8a6a50', chau: '#c4673f', la: '#5f9e57',
}

// Chỗ của từng khe (toạ độ sàn) — Làm/Cần người ở phòng dự án, còn lại ở Góc cà phê (tram/suy/nhan_vat.py).
const CHO = {
  'claude-1': { x: -13.5, z: 0.6, ngoi: false },
  'codex-1': { x: -7.5, z: 1.6, ngoi: false },
  'claude-2': { x: -13.0, z: 8.6, ngoi: false },
  'claude-3': { x: -7.0, z: 10.0, ngoi: true },
  'codex-2': { x: -1.6, z: 10.0, ngoi: true },
  'claude-4': { x: 3.5, z: 10.0, ngoi: true },
}
const PHONG_TO = 1.12
const CO_NV = 1.4                                 // phóng nhân vật cho giống tỉ lệ ảnh demo

function vatLieu(mau, them = {}) {
  return new THREE.MeshStandardMaterial({ color: mau, roughness: 0.88, metalness: 0, ...them })
}
function hop(w, h, d, mau, { bong = true, them } = {}) {
  const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), vatLieu(mau, them))
  m.castShadow = bong; m.receiveShadow = true
  return m
}
function dat(obj, x, y, z) { obj.position.set(x, y, z); return obj }

function lamMo(obj, doMo) {
  obj.traverse((o) => {
    if (!o.material) return
    o.material = o.material.clone()
    o.material.transparent = true
    o.material.opacity = Math.min(o.material.opacity ?? 1, doMo)
    o.castShadow = false
  })
}

// ---------- Đồ vật ----------
function manHinh(mau = MAU.man) {
  const g = new THREE.Group()
  g.add(dat(hop(0.14, 0.4, 0.14, MAU.vien), 0, 0.2, 0))
  g.add(dat(hop(1.25, 0.82, 0.12, MAU.vien), 0, 0.72, 0))
  const sang = mau !== MAU.manTat
  const man = new THREE.Mesh(new THREE.BoxGeometry(1.08, 0.66, 0.02),
    vatLieu(mau, sang ? { emissive: mau, emissiveIntensity: 0.45 } : {}))
  g.add(dat(man, 0, 0.72, 0.07))
  g.userData.man = man
  return g
}
function banLamViec(nhom, x, z, { mauMan = MAU.man, w = 2.8, d = 1.5 } = {}) {
  const g = new THREE.Group()
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
function cayXanh(nhom, x, z, cao = 1) {
  const g = new THREE.Group()
  g.add(dat(new THREE.Mesh(new THREE.CylinderGeometry(0.36, 0.28, 0.55, 16), vatLieu(MAU.chau)), 0, 0.275, 0))
  g.add(dat(new THREE.Mesh(new THREE.CylinderGeometry(0.33, 0.33, 0.05, 16), vatLieu('#5a3d2b')), 0, 0.55, 0))
  for (let i = 0; i < 7; i++) {
    const la = new THREE.Mesh(new THREE.ConeGeometry(0.1, 0.9 * cao, 6), vatLieu(i % 2 ? MAU.la : '#7cb36d'))
    const a = (i / 7) * Math.PI * 2
    la.position.set(Math.cos(a) * 0.12, 0.55 + 0.42 * cao, Math.sin(a) * 0.12)
    la.rotation.set(Math.sin(a) * 0.45, 0, -Math.cos(a) * 0.45)
    g.add(la)
  }
  g.traverse((o) => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true } })
  nhom.add(dat(g, x, 0, z))
}
function coc(nhom, x, y, z) {
  const g = new THREE.Group()
  g.add(dat(new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.16, 0.34, 16), vatLieu('#ece7f2')), 0, 0.17, 0))
  g.add(dat(new THREE.Mesh(new THREE.CylinderGeometry(0.17, 0.17, 0.02, 16), vatLieu('#5b3426')), 0, 0.33, 0))
  const tai = new THREE.Mesh(new THREE.TorusGeometry(0.09, 0.03, 6, 12), vatLieu('#ece7f2'))
  g.add(dat(tai, 0.21, 0.17, 0))
  g.traverse((o) => { if (o.isMesh) o.castShadow = true })
  nhom.add(dat(g, x, y, z))
}
function ghe(nhom, x, z) {
  const m = new THREE.Mesh(new THREE.CylinderGeometry(0.36, 0.32, 0.55, 14), vatLieu(MAU.ghe))
  m.castShadow = true; m.receiveShadow = true
  nhom.add(dat(m, x, 0.275, z))
}

// ---------- Nhân vật chibi ----------
function nhanVat(khe, cho) {
  const g = new THREE.Group()
  const bong = new THREE.Mesh(new THREE.CircleGeometry(0.66, 28),
    new THREE.MeshBasicMaterial({ color: '#3a2418', transparent: true, opacity: 0.18, depthWrite: false }))
  bong.rotation.x = -Math.PI / 2
  g.add(dat(bong, 0, 0.03, 0))
  const than = new THREE.Group()
  g.add(than)
  if (cho.ngoi) ghe(than, 0, -0.05)
  const mauChan = vatLieu(MAU.chan)
  for (const s of [-1, 1]) {
    const chan = new THREE.Mesh(new THREE.CylinderGeometry(0.13, 0.12, 0.56, 12), mauChan)
    chan.castShadow = true
    if (cho.ngoi) { chan.rotation.x = Math.PI / 2; dat(chan, s * 0.17, 0.62, 0.3) } else dat(chan, s * 0.17, 0.28, 0)
    than.add(chan)
  }
  const y0 = cho.ngoi ? 0.55 : 0.52
  const mauThan = vatLieu(khe.mau)
  const minh = new THREE.Mesh(new THREE.CylinderGeometry(0.34, 0.42, 0.92, 22), mauThan)
  minh.castShadow = true
  than.add(dat(minh, 0, y0 + 0.46, 0))
  const dau = new THREE.Mesh(new THREE.SphereGeometry(0.5, 28, 20), vatLieu(MAU.da))
  dau.castShadow = true
  than.add(dat(dau, 0, y0 + 1.36, 0))
  const toc = new THREE.Mesh(new THREE.SphereGeometry(0.53, 28, 14, 0, Math.PI * 2, 0, Math.PI * 0.52), vatLieu(khe.toc))
  toc.rotation.x = -0.42
  toc.castShadow = true
  than.add(dat(toc, 0, y0 + 1.4, -0.02))
  const tay = []
  for (const s of [-1, 1]) {
    const truc = new THREE.Group()
    dat(truc, s * 0.42, y0 + 0.82, 0)
    const canh = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.09, 0.62, 10), mauThan)
    canh.castShadow = true
    dat(canh, 0, -0.28, 0)
    truc.add(canh)
    truc.rotation.z = s * 0.12
    than.add(truc)
    tay.push(truc)
  }
  if (khe.hien_thi === 'can_nguoi') {             // giơ tay phải
    tay[1].rotation.z = Math.PI - 0.35
  }
  g.rotation.y = Math.PI / 4                      // quay mặt về phía camera
  if (khe.hien_thi === 'tat') lamMo(g, 0.36)
  g.userData = { chon: { loai: 'khe', khe }, than, tay, cao: y0 + 1.95 }
  return g
}

// ---------- Mặt bằng ----------
function dungPhong(canh) {
  const nhom = new THREE.Group()
  canh.add(nhom)
  const canh2 = new Map()
  for (const p of PHONG) {
    const w = p.x[1] - p.x[0], d = p.z[1] - p.z[0]
    const san = hop(w, 0.3, d, p.san, { bong: false })
    san.position.set((p.x[0] + p.x[1]) / 2, -0.15, (p.z[0] + p.z[1]) / 2)
    san.userData.chon = { loai: 'phong', phong: p }
    if (p.mo) { san.material.transparent = true; san.material.opacity = 0.75 }
    nhom.add(san)
    // cạnh 10 m: khoá theo toạ độ; cạnh chung hai phòng → tường có cửa
    const canhPhong = []
    for (let x = p.x[0]; x < p.x[1]; x += 10) canhPhong.push([x, p.z[0], x + 10, p.z[0], false], [x, p.z[1], x + 10, p.z[1], true])
    for (let z = p.z[0]; z < p.z[1]; z += 10) canhPhong.push([p.x[0], z, p.x[0], z + 10, false], [p.x[1], z, p.x[1], z + 10, true])
    for (const [x0, z0, x1, z1, truoc] of canhPhong) {
      const k = `${x0},${z0},${x1},${z1}`
      const c = canh2.get(k)
      if (c) c.so++
      else canh2.set(k, { x0, z0, x1, z1, so: 1, mau: p.tuong, truoc, mo: p.mo })
    }
  }
  for (const c of canh2.values()) {
    const trong = c.so > 1
    const cao = trong ? 1.3 : c.truoc ? 0.45 : 1.6
    const doc = c.x0 === c.x1
    const doan = trong ? [[0, 3.5], [6.5, 10]] : [[0, 10]]
    for (const [a, b] of doan) {
      const dai = b - a + (trong ? 0 : 0.35)
      const m = new THREE.Mesh(new THREE.BoxGeometry(doc ? 0.32 : dai, cao, doc ? dai : 0.32),
        vatLieu(c.mau, { transparent: true, opacity: c.mo ? 0.35 : 0.62, depthWrite: false }))
      const giua = (a + b) / 2
      if (doc) m.position.set(c.x0, cao / 2, c.z0 + giua)
      else m.position.set(c.x0 + giua, cao / 2, c.z0)
      m.receiveShadow = true
      nhom.add(m)
    }
  }
  return nhom
}

function dungDoVat(canh, khe) {
  const nhom = new THREE.Group()
  canh.add(nhom)
  const banCuaKhe = {}
  // Phòng Giám đốc
  nhom.add(dat(hop(4.8, 1.15, 2.5, MAU.goDam), -10, 0.575, -10.5))
  nhom.add(dat(hop(0.9, 1.4, 0.9, '#5d2412'), -10, 0.7, -12.6))
  cayXanh(nhom, -14.0, -7.0, 1.1)
  cayXanh(nhom, -6.6, -6.8, 0.9)
  // hr-codex: 4 bàn, khe đang làm đứng phía trước bàn
  banLamViec(nhom, -9.6, -3.4)
  banCuaKhe['claude-1'] = banLamViec(nhom, -13.5, -0.8)
  banCuaKhe['codex-1'] = banLamViec(nhom, -7.5, 0.2)
  cayXanh(nhom, -14.2, 4.2)
  // tram: bàn trống
  banLamViec(nhom, 0.5, -13.0)
  banLamViec(nhom, 2.2, -8.0)
  cayXanh(nhom, 4.0, -13.8, 1.1)
  // ke-toan (tạm đóng): mờ
  const dong = new THREE.Group()
  nhom.add(dong)
  banLamViec(dong, 12.5, -12.2, { mauMan: MAU.manTat })
  banLamViec(dong, 12.5, -8.0, { mauMan: MAU.manTat })
  lamMo(dong, 0.5)
  // Điều phối: 2 bàn + đèn trạng thái (chưa có tín hiệu → xám)
  banLamViec(nhom, -2.5, 2.0)
  banLamViec(nhom, 2.0, 3.0)
  nhom.add(dat(new THREE.Mesh(new THREE.CylinderGeometry(0.07, 0.07, 2.3, 8), vatLieu('#6b6058')), -3.5, 1.15, 4.2))
  nhom.add(dat(new THREE.Mesh(new THREE.CylinderGeometry(0.4, 0.4, 0.08, 16), vatLieu('#6b6058')), -3.5, 0.04, 4.2))
  const bongDen = new THREE.Mesh(new THREE.SphereGeometry(0.36, 20, 14), vatLieu('#bdb6ae', { emissive: '#000000' }))
  nhom.add(dat(bongDen, -3.5, 2.45, 4.2))
  // Phòng máy chủ: 4 tủ đen, đèn LED ở mặt +z (mặt trái-trước)
  // mỗi tủ một màu sức khoẻ (xanh/vàng/đỏ); tủ 3 vàng vì claude-4 cầu dao ngắt
  const SUC_KHOE = ['#5fd38a', '#5fd38a', '#f2c14e', '#5fd38a']
  for (let i = 0; i < 4; i++) {
    const x = 6.8 + i * 2.1, z = -1.2 + i * 1.3
    nhom.add(dat(hop(1.6, 2.7, 1.6, MAU.tu), x, 1.35, z))
    for (let k = 0; k < 3; k++) {
      const m = k === 1 && SUC_KHOE[i] !== '#f2c14e' ? '#4b5a52' : SUC_KHOE[i]
      const l = new THREE.Mesh(new THREE.SphereGeometry(0.1, 10, 8), new THREE.MeshBasicMaterial({ color: m }))
      nhom.add(dat(l, x - 0.35, 2.2 - k * 0.45, z + 0.81))
    }
  }
  // Góc cà phê: quầy dài đất nung + cốc, bàn tròn, bàn chờ của khe lỗi
  nhom.add(dat(hop(6.0, 1.15, 1.3, MAU.quay), -11.6, 0.575, 12.6))
  nhom.add(dat(hop(1.0, 0.8, 0.8, '#3b3330'), -14.0, 1.55, 12.5))
  for (const x of [-10.6, -9.9, -9.2]) coc(nhom, x, 1.15, 12.4)
  nhom.add(dat(new THREE.Mesh(new THREE.CylinderGeometry(1.0, 1.0, 0.12, 24), vatLieu('#efe6da')), -4.3, 0.95, 8.4))
  nhom.add(dat(new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.3, 0.9, 10), vatLieu('#8d7a6a')), -4.3, 0.45, 8.4))
  coc(nhom, -4.5, 1.01, 8.2)
  banCuaKhe['claude-4'] = banLamViec(nhom, 3.5, 8.6, { mauMan: MAU.manDo, w: 2.2, d: 1.3 })
  cayXanh(nhom, -14.2, 6.2)
  cayXanh(nhom, 4.2, 14.2, 0.9)
  nhom.traverse((o) => { if (o.isMesh && !o.userData.chon) o.userData.vatThe = true })
  return { nhom, banCuaKhe, bongDen }
}

// ---------- Khung cảnh + overlay ----------
export function dungVanPhong(khung, { giamChuyenDong = false, khiChon } = {}) {
  const lop = document.createElement('div')
  lop.className = 'lop-phu'
  let renderer
  try {
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
  } catch {
    khung.insertAdjacentHTML('beforeend', '<div class="loi-webgl">Trình duyệt không bật được WebGL — xem bản danh sách bên dưới.</div>')
    return { huy() {}, datGiamChuyenDong() {} }
  }
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  renderer.shadowMap.enabled = true
  renderer.shadowMap.type = THREE.PCFSoftShadowMap
  renderer.outputColorSpace = THREE.SRGBColorSpace
  khung.appendChild(renderer.domElement)
  khung.appendChild(lop)

  const canh = new THREE.Scene()
  const camera = new THREE.OrthographicCamera(-10, 10, 10, -10, 0.1, 400)
  camera.position.set(40, 40, 40)
  camera.lookAt(0, 0, 0)                          // sau khi đặt vị trí

  canh.add(new THREE.AmbientLight('#fff3e4', 1.15))
  canh.add(new THREE.HemisphereLight('#fff8ef', '#d8bfa2', 0.75))
  const mat = new THREE.DirectionalLight('#ffe9d2', 1.55)
  mat.position.set(-8, 34, 22)
  mat.castShadow = true
  mat.shadow.mapSize.set(2048, 2048)
  Object.assign(mat.shadow.camera, { left: -26, right: 26, top: 26, bottom: -26, near: 1, far: 90 })
  mat.shadow.bias = -0.0006
  mat.shadow.normalBias = 0.03
  canh.add(mat)

  dungPhong(canh)
  const { banCuaKhe } = dungDoVat(canh, KHE)

  // nhân vật + nhãn (vị trí nhãn do boTriNhan quyết định khi đổi cỡ khung)
  const ds = []
  const nhan = []
  const them = (el, loai, neo, ax, ay, dx, dy, khe) => { lop.appendChild(el); nhan.push({ el, loai, neo, ax, ay, dx, dy, khe }) }
  for (const k of KHE) {
    const cho = CHO[k.id]
    const g = nhanVat(k, cho)
    g.position.set(cho.x, 0, cho.z)
    g.scale.setScalar(CO_NV)
    g.userData.cao *= CO_NV
    canh.add(g)
    const mo = k.hien_thi === 'tat'
    const ten = document.createElement('div')
    ten.className = 'ten-nv' + (mo ? ' mo' : '')
    const nhanPhu = k.trang_thai === 'mat_ket_noi' ? 'Mất kết nối' : k.trang_thai === 'tat' ? 'Tắt' : k.hien_thi === 'loi' ? 'Lỗi · cầu dao ngắt' : NHAN_HIEN_THI[k.hien_thi]
    ten.innerHTML = `${k.ten}<small>${nhanPhu}</small>`
    ten.onclick = () => khiChon?.({ loai: 'khe', khe: k })
    them(ten, 'ten', new THREE.Vector3(cho.x, 0, cho.z), -0.5, 0, 0, 8, k.id)
    const muc = { k, g, cho, pha: Math.random() * 6 }
    if (k.bead && (k.hien_thi === 'lam' || k.hien_thi === 'can_nguoi')) {
      const bb = document.createElement('div')
      bb.className = 'bong-bong'
      bb.innerHTML = `<b>${k.bead.id}</b>${k.bead.tieu_de} · ${TEN_BUOC[k.bead.buoc]}`
      bb.onclick = ten.onclick
      them(bb, 'bb', new THREE.Vector3(cho.x, g.userData.cao + 0.3, cho.z), -0.5, -1, 0, -10, k.id)
      muc.bb = nhan[nhan.length - 1]
    }
    if (k.hien_thi === 'can_nguoi') {
      const hh = document.createElement('div')
      hh.className = 'huy-hieu-do'
      hh.textContent = '1'
      hh.title = 'Cần Đại ca trả lời'
      hh.onclick = ten.onclick
      them(hh, 'hh', new THREE.Vector3(cho.x, g.userData.cao - 0.5, cho.z), 0, -0.5, 16, 0, k.id)
    }
    if (k.hien_thi === 'loi' && banCuaKhe[k.id]) muc.man = banCuaKhe[k.id].userData.man   // màn hình đỏ nhấp nháy
    ds.push(muc)
  }

  // biển tên phòng: neo ở góc sàn trống của phòng
  for (const p of PHONG) {
    const el = document.createElement('div')
    el.className = 'bien-phong' + (p.mo ? ' mo' : '')
    let phu = ''
    if (p.loai === 'dieu_phoi') phu = '<span class="den" title="Đèn Điều phối"></span><small>chưa có tín hiệu</small>'
    el.innerHTML = `${p.ten}${phu}`
    el.onclick = () => khiChon?.({ loai: 'phong', phong: p })
    them(el, 'bien', new THREE.Vector3(p.nhan[0], 0.5, p.nhan[1]), -0.5, -0.5, 0, 0)
  }
  const hhGd = document.createElement('div')
  hhGd.className = 'huy-hieu-do lon'
  hhGd.innerHTML = `${so_viec_cho()}<span class="phu">việc chờ</span>`
  hhGd.onclick = () => khiChon?.({ loai: 'phong', phong: PHONG[0] })
  them(hhGd, 'gd', new THREE.Vector3(-9.6, 1.2, -10.0), -0.5, -1, 0, -2)

  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg')
  svg.setAttribute('class', 'duong-chi')
  lop.prepend(svg)

  const tam = new THREE.Vector3()
  function manHinhXY(v) {
    tam.copy(v).project(camera)
    return { x: (tam.x + 1) / 2 * khung.clientWidth, y: (1 - tam.y) / 2 * khung.clientHeight }
  }
  let pxMoiMet = 1
  function boTriLai() {
    const W = khung.clientWidth, H = khung.clientHeight
    if (!W || !H) return
    lop.style.fontSize = `${16 * Math.max(0.7, Math.min(1.05, W / 1100))}px`   // chữ co theo khung
    pxMoiMet = manHinhXY(new THREE.Vector3(0, 0, 0)).y - manHinhXY(new THREE.Vector3(0, 1, 0)).y
    for (const n of nhan) {
      n.w = n.el.offsetWidth; n.h = n.el.offsetHeight
      n.neoXY = manHinhXY(n.neo)
      n.x0 = n.neoXY.x + n.ax * n.w + n.dx
      n.y0 = n.neoXY.y + n.ay * n.h + n.dy
      n.diemNeo = n.neoXY
    }
    const than = ds.map(({ g, k }) => {
      const a = manHinhXY(new THREE.Vector3(g.position.x, 0, g.position.z))
      const b = manHinhXY(new THREE.Vector3(g.position.x, g.userData.cao, g.position.z))
      const cao = a.y - b.y
      return { x: a.x - cao * 0.3, y: b.y - 2, w: cao * 0.6, h: cao + 6, khe: k.id }
    })
    const duong = boTriNhan(nhan, than, W, H)
    svg.innerHTML = duong.map(([x1, y1, x2, y2]) => `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}"/><circle cx="${x1}" cy="${y1}" r="2.5"/>`).join('')
    lop.dataset.chong = String(demChong(nhan))
  }

  // camera: khít khung theo hình chiếu các góc sàn
  const goc = []
  for (const p of PHONG) for (const x of p.x) for (const z of p.z) for (const y of [-0.3, 2.6]) goc.push(new THREE.Vector3(x, y, z))
  function khit() {
    const w = khung.clientWidth, h = khung.clientHeight
    if (!w || !h) return
    renderer.setSize(w, h, false)
    camera.updateMatrixWorld()
    let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity
    for (const v of goc) {
      const c = v.clone().applyMatrix4(camera.matrixWorldInverse)
      x0 = Math.min(x0, c.x); x1 = Math.max(x1, c.x); y0 = Math.min(y0, c.y); y1 = Math.max(y1, c.y)
    }
    const le = 0.5
    x0 -= le; x1 += le; y0 -= le; y1 += le + 1.2   // chừa chỗ biển tên phòng phía trên
    let cw = x1 - x0, ch = y1 - y0
    const cx = (x0 + x1) / 2, cy = (y0 + y1) / 2
    if (cw / ch > w / h) ch = cw * h / w; else cw = ch * w / h
    cw /= PHONG_TO; ch /= PHONG_TO                 // phóng thêm, cắt nhẹ hai góc xa như ảnh demo
    Object.assign(camera, { left: cx - cw / 2, right: cx + cw / 2, top: cy + ch / 2, bottom: cy - ch / 2 })
    camera.updateProjectionMatrix()
  }
  const ro = new ResizeObserver(() => { khit(); boTriLai() })
  ro.observe(khung)
  khit()
  boTriLai()
  document.fonts?.ready.then(() => { khit(); boTriLai() })

  // bấm chọn
  const tia = new THREE.Raycaster()
  const chuot = new THREE.Vector2()
  function timChon(ev) {
    const r = renderer.domElement.getBoundingClientRect()
    chuot.set(((ev.clientX - r.left) / r.width) * 2 - 1, -((ev.clientY - r.top) / r.height) * 2 + 1)
    tia.setFromCamera(chuot, camera)
    for (const t of tia.intersectObjects(canh.children, true)) {
      let o = t.object
      while (o && !o.userData?.chon) o = o.parent
      if (o) return o.userData.chon
    }
    return null
  }
  renderer.domElement.addEventListener('click', (ev) => { const c = timChon(ev); if (c) khiChon?.(c) })
  renderer.domElement.addEventListener('pointermove', (ev) => {
    renderer.domElement.style.cursor = timChon(ev) ? 'pointer' : 'default'
  })

  // vòng vẽ
  let giam = giamChuyenDong
  let raf = 0
  const dongHo = new THREE.Clock()
  function ve() {
    raf = requestAnimationFrame(ve)
    const t = dongHo.getElapsedTime()
    for (const m of ds) {
      const { g, k } = m
      const than = g.userData.than
      let nhun = 0
      if (!giam) {
        if (k.hien_thi === 'lam') nhun = Math.abs(Math.sin(t * 3.4 + m.pha)) * 0.12
        if (k.hien_thi === 'can_nguoi') g.userData.tay[1].rotation.z = Math.PI - 0.35 + Math.sin(t * 5) * 0.22
        if (k.hien_thi === 'ranh') than.rotation.y = Math.sin(t * 0.9 + m.pha) * 0.25
        if (m.man) m.man.material.emissiveIntensity = 0.35 + Math.abs(Math.sin(t * 2.2)) * 0.5
      } else {
        than.rotation.y = 0
        if (k.hien_thi === 'can_nguoi') g.userData.tay[1].rotation.z = Math.PI - 0.35
      }
      than.position.y = nhun
      if (m.bb) m.bb.nhun = nhun * CO_NV * pxMoiMet
    }
    for (const n of nhan) {
      if (n.x === undefined) continue
      n.el.style.transform = `translate(${n.x}px, ${n.y - (n.nhun || 0)}px)`
    }
    renderer.render(canh, camera)
  }
  ve()

  return {
    datGiamChuyenDong(b) { giam = b },
    huy() {
      cancelAnimationFrame(raf)
      ro.disconnect()
      canh.traverse((o) => { o.geometry?.dispose(); if (o.material) [].concat(o.material).forEach((m) => m.dispose()) })
      renderer.dispose()
      renderer.forceContextLoss()
    },
  }
}
