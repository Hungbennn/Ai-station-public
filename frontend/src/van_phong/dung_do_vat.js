// Đồ đạc từng loại phòng (mockup van-phong.js dungDoVat, D20) — three thuần. Mỗi phòng một Group mang
// userData.chon = { loai: 'phong', ma } nên bấm vào đồ đạc cũng chọn phòng. Toạ độ tương đối tâm ô (bo_tri `tam`).
import { CylinderGeometry, Group } from 'three'
import { CAY_DU_AN } from './cho_nv.js'
import { MAN, banLamViec, cayXanh, coc, dat, hop, khoi, lamMo, vatLieu } from './do_vat.js'
import { doDieuPhoi, doMayChu } from './do_vat_tram.js'
import { MAU } from './hien_thi.js'

function doGiamDoc(g, tx, tz) {
  g.add(dat(hop(4.8, 1.15, 2.5, MAU.goDam), tx, 0.575, tz - 0.5))
  g.add(dat(hop(0.9, 1.4, 0.9, MAU.goTu), tx, 0.7, tz - 2.6))
  cayXanh(g, tx - 4.0, tz + 3.0, 1.1)
  cayXanh(g, tx + 3.4, tz + 3.2, 0.9)
}

// Góc cà phê (tâm ô (-1, 1)): quầy dài đất nung + máy pha + cốc, bàn tròn có cốc, hai chậu cây.
// Vị trí quầy / bàn tròn / cây trùng VAT_CA_PHE của cho_nv.js (vật cản khi xếp thêm nhân vật).
function doCaPhe(g, tx, tz) {
  g.add(dat(hop(6.0, 1.15, 1.3, MAU.quay), tx - 1.6, 0.575, tz + 2.6))
  g.add(dat(hop(1.0, 0.8, 0.8, MAU.may), tx - 4.0, 1.55, tz + 2.5))
  for (const x of [-0.6, 0.1, 0.8]) coc(g, tx + x, 1.15, tz + 2.4)
  g.add(dat(khoi(new CylinderGeometry(1.0, 1.0, 0.12, 24), vatLieu(MAU.ban)), tx + 5.7, 0.95, tz - 1.6))
  g.add(dat(khoi(new CylinderGeometry(0.12, 0.3, 0.9, 10), vatLieu(MAU.chanBan)), tx + 5.7, 0.45, tz - 1.6))
  coc(g, tx + 5.5, 1.01, tz - 1.8)
  cayXanh(g, tx - 4.2, tz - 3.8)
  cayXanh(g, tx + 14.2, tz + 4.2, 0.9)
}

function doDuAn(g, tx, tz) {
  cayXanh(g, tx + CAY_DU_AN[0], tz + CAY_DU_AN[1])
}

const DO = { giam_doc: doGiamDoc, ca_phe: doCaPhe, du_an: doDuAn, dieu_phoi: doDieuPhoi, may_chu: doMayChu }

// Trả { nhom, tu (LED đầu mỗi tủ), den (bóng đèn Điều phối), manDo: Map khe_id → mặt màn hình đỏ }.
export function dungDoVat(boTri) {
  const nhom = new Group()
  const ra = { nhom, tu: [], den: null, manDo: new Map() }
  for (const p of boTri.phong) {
    const g = new Group()
    g.userData.chon = { loai: 'phong', ma: p.ma }
    nhom.add(g)
    Object.assign(ra, DO[p.loai]?.(g, p.tam[0], p.tam[1], p))
    for (const b of boTri.ban.filter((x) => x.phong === p.ma)) {
      const ban = banLamViec(g, b.x, b.z, { mauMan: MAN[b.man], w: b.w, d: b.d })
      if (b.khe && b.man === 'do') ra.manDo.set(b.khe, ban.userData.man)
    }
    if (p.mo) lamMo(g, 0.5)                                    // dự án chỉ quét thử: mờ như ke-toan mockup
  }
  return ra
}
