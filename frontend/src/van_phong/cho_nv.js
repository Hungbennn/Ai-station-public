// Chỗ đứng/ngồi của nhân vật (mockup van-phong.js CHO + bàn của khe, D20) — hàm thuần. Phòng lấy từ
// `nhan_vat[].phong` của API (2c G7: server suy, trang không tự suy lại); phòng lạ hoặc đã gỡ → Góc cà phê.
// Toạ độ chỗ tương đối tâm ô đầu của phòng (bo_tri.js `tam`).
export const TRUOC_BAN = 1.4                                       // đứng/ngồi trước bàn (claude-1, codex-1, claude-4)
export const BAN_DU_AN = [[-3.5, -0.8], [2.5, 0.2], [0.4, -3.4]]   // ba bàn phòng hr-codex
export const CAY_DU_AN = [-4.2, 4.2]
// Góc cà phê (tâm ô (-1, 1)): chỗ đứng cho khe rảnh gần quầy, chỗ ngồi cho khe tắt/khác, bàn của khe lỗi.
const CA_PHE = {
  dung: [[-3, -1.4], [-0.8, -1.8], [1.4, -1.4]],
  ngoi: [[3, 0], [8.4, 0], [5.7, 2.2]],
  loi: [[13.5, -1.4], [10.4, -3]],
}
// Vật cản Góc cà phê [x, z, nửa rộng, nửa sâu]: quầy, bàn tròn, hai chậu cây (dung_do_vat.js cùng số).
const VAT_CA_PHE = [[-1.6, 2.6, 3, 0.65], [5.7, -1.6, 1, 1], [-4.2, -3.8, 0.4, 0.4], [14.2, 4.2, 0.4, 0.4]]
const BUOC = 2.2

const ngoi = (nv) => nv.hien_thi === 'loi' || nv.hien_thi === 'tat'
const manCua = (nv) => (nv.hien_thi === 'loi' ? 'do' : nv.hien_thi === 'tat' ? 'tat' : 'sang')

// Ô trống kế tiếp theo lưới trong phòng (khi hết chỗ định sẵn); `canBan`: chừa chỗ bàn phía sau.
function oTrong(p, dung, vat, canBan) {
  const tu = (a, b) => dung.every(([u, v]) => Math.hypot(u - a, v - b) >= 1.6) &&
    vat.every(([u, v, w, d]) => Math.abs(u - a) > w + 0.7 || Math.abs(v - b) > d + 0.7)
  for (let z = p.z[0] + 1.6; z <= p.z[1] - 1.2; z += BUOC) {
    for (let x = p.x[0] + 1.6; x <= p.x[1] - 1.2; x += BUOC) {
      if (tu(x, z) && (!canBan || tu(x, z - TRUOC_BAN))) return [x, z]
    }
  }
  return p.tam
}

function xepPhong(p, ds, nhanVat, ban) {
  const [tx, tz] = p.tam
  const dung = []
  const vat = []
  const dat = (nv, x, z) => {
    nhanVat.push({ ...nv, x, z, ngoi: ngoi(nv), phongMa: p.ma })
    dung.push([x, z])
  }
  const datBan = (x, z, man, khe, w = 2.8, d = 1.5) => {
    ban.push({ phong: p.ma, x, z, man, khe: khe ?? null, w, d })
    vat.push([x, z, w / 2, d / 2])
  }
  const thua = []
  if (p.loai === 'du_an') {
    vat.push([tx + CAY_DU_AN[0], tz + CAY_DU_AN[1], 0.4, 0.4])
    BAN_DU_AN.forEach(([bx, bz], i) => {
      const nv = ds[i]
      datBan(tx + bx, tz + bz, p.mo ? 'tat' : nv ? manCua(nv) : 'sang', nv?.khe_id)
      if (nv) dat(nv, tx + bx, tz + bz + TRUOC_BAN)
    })
    thua.push(...ds.slice(BAN_DU_AN.length))
  } else {
    for (const [x, z, w, d] of VAT_CA_PHE) vat.push([tx + x, tz + z, w, d])
    const hang = { dung: [...CA_PHE.dung], ngoi: [...CA_PHE.ngoi], loi: [...CA_PHE.loi] }
    for (const nv of ds) {
      const loai = nv.hien_thi === 'ranh' ? 'dung' : nv.hien_thi === 'loi' ? 'loi' : 'ngoi'
      const c = hang[loai].shift()
      if (!c) thua.push(nv)
      else if (loai !== 'loi') dat(nv, tx + c[0], tz + c[1])
      else {
        datBan(tx + c[0], tz + c[1], 'do', nv.khe_id, 2.2, 1.3)
        dat(nv, tx + c[0], tz + c[1] + TRUOC_BAN)
      }
    }
  }
  for (const nv of thua) {
    const loi = nv.hien_thi === 'loi'
    const [x, z] = oTrong(p, dung, vat, loi)
    if (loi) datBan(x, z - TRUOC_BAN, 'do', nv.khe_id, 2.2, 1.3)
    dat(nv, x, z)
  }
}

// Trả { nhanVat: [{...nv, x, z, ngoi, phongMa}], ban: [{phong, x, z, man: sang|do|tat, khe, w, d}] }.
export function datNhanVat(phong, nhanVat) {
  const theoMa = new Map(phong.map((p) => [p.ma, p]))
  const caPhe = phong.find((p) => p.loai === 'ca_phe')
  const nhom = new Map(phong.filter((p) => p.loai === 'du_an' || p === caPhe).map((p) => [p, []]))
  for (const nv of [...nhanVat].sort((a, b) => String(a.khe_id).localeCompare(String(b.khe_id)))) {
    const p = theoMa.get(nv.phong)
    const dich = p && nhom.has(p) ? p : caPhe
    if (dich) nhom.get(dich).push(nv)
  }
  const ra = { nhanVat: [], ban: [] }
  for (const [p, ds] of nhom) xepPhong(p, ds, ra.nhanVat, ra.ban)
  return ra
}
