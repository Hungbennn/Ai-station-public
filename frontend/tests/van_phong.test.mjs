import assert from 'node:assert/strict'
import { test } from 'node:test'
import { O, boTriVanPhong, mauTuMay, oDuAn } from '../src/van_phong/bo_tri.js'
import { MAU, catChu, chuBien, chuBongBong, duongDanNhanVat, duongDanPhong, tuThe } from '../src/van_phong/hien_thi.js'
import { dungNhan, nhanPhu, timMucChon } from '../src/van_phong/nhan_canh.js'

// Dữ liệu kiểu mockup du-lieu.js / van-phong.js PHONG + KHE (D20), dạng API /api/van-phong + /api/du-an.
const PHONG = [{ ma: 'giam-doc', loai: 'giam_doc', so_cho: 4 }, { ma: 'dieu-phoi', loai: 'dieu_phoi', sang: null },
  { ma: 'may-chu', loai: 'may_chu', suc_khoe: { mau: 'vang', ly_do: ['claude-4'], muc: [{ mau: 'vang' }] } },
  { ma: 'ca-phe', loai: 'ca_phe' }, ...['hr-codex', 'tram', 'ke-toan'].map(duAn)]
const DU_AN = [{ ten: 'ke-toan', bat_ghi: false }, { ten: 'tram' }]
const NV = [nv('claude-1', 'lam', 'du-an:hr-codex', 'hr-1'), nv('codex-1', 'can_nguoi', 'du-an:hr-codex', 'hr-3'),
  nv('claude-2', 'ranh', 'ca-phe'), nv('claude-3', 'tat', 'ca-phe'), { ...nv('codex-2', 'tat', 'ca-phe'),
    trang_thai: 'mat_ket_noi' }, { ...nv('claude-4', 'loi', 'ca-phe'), cau_dao_ngat: true }]
function duAn(ten) { return { ma: `du-an:${ten}`, loai: 'du_an', ten, du_an: ten } }
function nv(khe, ht, phong, bead) {
  const b = bead ? { du_an: 'hr-codex', bead_id: bead, tieu_de: `Việc ${bead}`, buoc: 'code' } : null
  return { khe_id: khe, ten: khe, cli: 'claude', trang_thai: ht, hien_thi: ht, phong, bead: b }
}
const trong = (p, x, z) => x > p.x[0] && x < p.x[1] && z > p.z[0] && z < p.z[1]
const tim = (b, ma) => b.phong.find((p) => p.ma === ma)

test('bố trí ba dự án đúng ô mockup, ô 10 m, Góc cà phê hai ô, màu cố định', () => {
  const b = boTriVanPhong(PHONG, NV, DU_AN)
  const o = (ma) => [tim(b, ma).x, tim(b, ma).z]
  assert.equal(O, 10)
  assert.deepEqual(o('giam-doc'), [[-15, -5], [-15, -5]])
  assert.deepEqual(o('dieu-phoi'), [[-5, 5], [-5, 5]])
  assert.deepEqual(o('may-chu'), [[5, 15], [-5, 5]])
  assert.deepEqual(o('ca-phe'), [[-15, 5], [5, 15]])
  assert.deepEqual(o('du-an:hr-codex'), [[-15, -5], [-5, 5]])
  assert.deepEqual(o('du-an:tram'), [[-5, 5], [-15, -5]])
  assert.deepEqual(o('du-an:ke-toan'), [[5, 15], [-15, -5]])
  assert.deepEqual([tim(b, 'giam-doc').san, tim(b, 'may-chu').tuong], ['#f8e6d4', '#b2c2cc'])
  assert.deepEqual([tim(b, 'du-an:hr-codex').san, tim(b, 'du-an:tram').san], ['#f5d6d3', '#fbdcc8'])
  assert.deepEqual(tim(b, 'giam-doc').nhan, [-11.6, -12.6])                       // neo biển như mockup
  assert.deepEqual(tim(b, 'du-an:hr-codex').nhan, [-9.2, 3.9])
})

test('bat_ghi false (D37): phòng mờ xám, biển "(chỉ quét thử)"; thiếu trường = bật', () => {
  const b = boTriVanPhong(PHONG, NV, DU_AN)
  const kt = tim(b, 'du-an:ke-toan')
  assert.deepEqual([kt.mo, kt.san, kt.tenBien], [true, '#ebe5de', 'ke-toan (chỉ quét thử)'])
  assert.deepEqual([tim(b, 'du-an:tram').mo, tim(b, 'du-an:tram').tenBien], [false, 'tram'])
  assert.equal(boTriVanPhong(PHONG, NV, []).phong.filter((p) => p.mo).length, 0)
  assert.ok(b.ban.filter((x) => x.phong === 'du-an:ke-toan').every((x) => x.man === 'tat'))
})

test('hơn 3 dự án thêm hàng phía sau (D38/Q9), không chồng ô', () => {
  assert.deepEqual([0, 1, 2, 3, 5, 6].map(oDuAn), [[-1, 0], [0, -1], [1, -1], [-1, -2], [1, -2], [-1, -3]])
  const b = boTriVanPhong([...PHONG, duAn('a'), duAn('b')], NV, DU_AN)
  assert.deepEqual([tim(b, 'du-an:a').x, tim(b, 'du-an:a').z], [[-15, -5], [-25, -15]])
  assert.deepEqual([tim(b, 'du-an:b').x, tim(b, 'du-an:b').z], [[-5, 5], [-25, -15]])
  const o = b.phong.flatMap((p) => p.o.map(([x, z]) => `${x},${z}`))
  assert.equal(new Set(o).size, o.length)
  assert.equal(b.phong.length, 9)
})

test('nhân vật nằm trong phòng theo nhan_vat[].phong; phòng lạ về cà phê; không trùng chỗ', () => {
  const ranh = ['a', 'b', 'c', 'd'].map((k) => nv(k, 'ranh', 'ca-phe'))
  const ds = [...NV, nv('codex-9', 'lam', 'du-an:da-go', 'x-1'), ranh[0], ranh[1], ranh[2], ranh[3]]
  const b = boTriVanPhong(PHONG, ds, DU_AN)
  for (const n of b.nhanVat) assert.ok(trong(tim(b, n.phongMa), n.x, n.z), n.khe_id)
  assert.equal(b.nhanVat.find((n) => n.khe_id === 'codex-9').phongMa, 'ca-phe')
  assert.equal(b.nhanVat.find((n) => n.khe_id === 'claude-1').phongMa, 'du-an:hr-codex')
  const cho = b.nhanVat.map((n) => `${n.x},${n.z}`)
  assert.equal(new Set(cho).size, cho.length)
  const c1 = b.nhanVat.find((n) => n.khe_id === 'claude-1')
  assert.ok(b.ban.some((x) => x.x === c1.x && Math.abs(c1.z - x.z - 1.4) < 1e-9))     // đứng trước bàn
  const c4 = b.nhanVat.find((n) => n.khe_id === 'claude-4')
  assert.deepEqual([c4.ngoi, b.ban.find((x) => x.khe === 'claude-4').man], [true, 'do'])   // lỗi: màn đỏ
  assert.equal(b.nhanVat.find((n) => n.khe_id === 'claude-2').ngoi, false)
})

test('tủ máy chủ theo suc_khoe.muc, thiếu → xanh', () => {
  assert.deepEqual(mauTuMay(PHONG[2]), ['vang', 'xanh', 'xanh', 'xanh'])
  assert.deepEqual(mauTuMay({ suc_khoe: { mau: 'do', ly_do: [] } }), ['xanh', 'xanh', 'xanh', 'xanh'])
})

test('nhãn: biển, tên + nhãn phụ, bong bóng, huy hiệu đỏ, huy hiệu Giám đốc', () => {
  assert.deepEqual(NV.map(nhanPhu), ['Làm', 'Cần người', 'Rảnh', 'Tắt', 'Mất kết nối', 'Lỗi · cầu dao ngắt'])
  assert.equal(nhanPhu({ hien_thi: 'loi', trang_thai: 'loi' }), 'Lỗi')
  const ds = dungNhan(boTriVanPhong(PHONG, NV, DU_AN))
  const dem = (l) => ds.filter((n) => n.loai === l).length
  assert.deepEqual(['bien', 'ten', 'bb', 'hh', 'gd'].map(dem), [7, 6, 2, 1, 1])
  assert.equal(ds.find((n) => n.id === 'gd').chu, '4')
  assert.deepEqual(ds.find((n) => n.id === 'bien:dieu-phoi').den, { sang: false, chu: 'chưa có tín hiệu' })
  const bb = ds.find((n) => n.id === 'bb:codex-1')
  assert.deepEqual([bb.ma, bb.chu, bb.chon], ['hr-3', 'Việc hr-3 · code', { loai: 'khe', khe_id: 'codex-1' }])
  assert.ok(ds.every((n) => n.nhanDoc && n.neo.length === 3))
  const b = boTriVanPhong(PHONG, NV, DU_AN)                                  // panel lấy bản mới nhất (D38/Q8)
  assert.equal(timMucChon(b, bb.chon).nv.bead.bead_id, 'hr-3')
  assert.deepEqual([timMucChon(b, { loai: 'phong', ma: 'may-chu' }).khoa, timMucChon(b, null)], ['phong:may-chu', null])
  assert.equal(timMucChon(b, { loai: 'khe', khe_id: 'da-go' }), null)
})

test('hiển thị giữ từ 2c/2e: tư thế, chữ biển, bong bóng, đường dẫn, bảng màu mockup', () => {
  assert.deepEqual(tuThe('can_nguoi'), { ngoi: true, giaTay: true, chamDo: true, manHinh: 'sang', doMo: 1 })
  assert.deepEqual(tuThe('la'), tuThe('tat'))
  assert.equal(chuBien(PHONG[0]), 'Phòng giám đốc · 4 việc chờ')
  assert.equal(catChu('Sửa cắt tóm tắt', 8), 'Sửa cắt…')
  assert.equal(chuBongBong({ hien_thi: 'lam', bead: { tieu_de: 'Sửa thuế', buoc: 'qc' } }), 'Sửa thuế · QC')
  assert.equal(chuBongBong({ hien_thi: 'ranh', bead: null }), null)
  assert.deepEqual(duongDanNhanVat({ bead: { du_an: 'hr', bead_id: 'hr-1' } }),
    { path: '/cong-viec', query: { du_an: 'hr', bead: 'hr-1' } })
  assert.deepEqual(duongDanPhong(duAn('hr')), { path: '/cong-viec', query: { du_an: 'hr' } })
  assert.equal(duongDanPhong(PHONG[1]), null)
  assert.deepEqual([MAU.go, MAU.man, MAU.manDo, MAU.tu, MAU.den],
    ['#c79d74', '#9fd0ee', '#e0574a', '#30363c', '#f2c14e'])
  assert.ok(Object.values(MAU.suc_khoe).every((m) => /^#[0-9a-f]{6}$/.test(m)))
})
