import assert from 'node:assert/strict'
import { test } from 'node:test'
import { OrthographicCamera } from 'three'
import { boTriVanPhong } from '../src/van_phong/bo_tri.js'
import { boTriNhan, demChong } from '../src/van_phong/bo_tri_nhan.js'
import { dungCanh, huyCanh } from '../src/van_phong/dung_canh.js'
import { PHONG_TO, chieuNhan, coChu, gocSan, khit } from '../src/van_phong/khung_nhin.js'
import { dungNhan, xepNhan } from '../src/van_phong/nhan_canh.js'

// Cảnh three chạy trong node (không WebGL). Dữ liệu kiểu mockup van-phong.js (D20).
const PHONG = [{ ma: 'giam-doc', loai: 'giam_doc', so_cho: 4 }, { ma: 'dieu-phoi', loai: 'dieu_phoi', sang: null },
  { ma: 'may-chu', loai: 'may_chu', suc_khoe: { mau: 'vang', ly_do: ['a', 'b'], muc: [{ mau: 'vang' },
    { mau: 'do' }] } },
  { ma: 'ca-phe', loai: 'ca_phe' }, ...['hr-codex', 'tram', 'ke-toan'].map((t) => ({ ma: `du-an:${t}`, loai: 'du_an',
    ten: t, du_an: t }))]
const BEAD = (id, t) => ({ du_an: 'hr-codex', bead_id: id, tieu_de: t, buoc: 'code' })
const NV = [['claude-1', 'lam', 'du-an:hr-codex', BEAD('hr-1', 'Sửa cắt UTF-8 tóm tắt hoàn tiền')],
  ['codex-1', 'can_nguoi', 'du-an:hr-codex', BEAD('hr-3', 'Chọn cách tính thuế')], ['claude-2', 'ranh', 'ca-phe'],
  ['claude-3', 'tat', 'ca-phe'], ['codex-2', 'tat', 'ca-phe'], ['claude-4', 'loi', 'ca-phe']]
  .map(([k, h, p, b]) => ({ khe_id: k, ten: k.replace('-', ' '), trang_thai: h, hien_thi: h, phong: p,
    bead: b ?? null }))
const BO_TRI = boTriVanPhong(PHONG, NV, [{ ten: 'ke-toan', bat_ghi: false }])

function camera() {
  const c = new OrthographicCamera(-1, 1, 1, -1, 0.1, 400)
  c.position.set(40, 40, 40)
  c.lookAt(0, 0, 0)
  return c
}
function datKhung(c, w, h, to) {
  Object.assign(c, khit(c, gocSan(BO_TRI.phong), w, h, to))
  c.updateProjectionMatrix()
}
// Ước cỡ nhãn như CSS mục Văn phòng (chữ đậm ~0,62 em mỗi ký tự): đủ để kiểm thuật toán, trình duyệt đo thật.
function uocCo(n, f) {
  const dai = (s, k) => [...String(s ?? '')].length * 0.62 * f * k
  if (n.loai === 'bien') return { w: dai(n.chu, 1.19) + (n.den ? 7 * f : 0) + 2 * f + 3, h: 2.1 * f }
  if (n.loai === 'ten') return { w: Math.max(dai(n.chu, 1.06), dai(n.phu, 0.66)), h: 1.9 * f }
  if (n.loai === 'bb') return { w: dai(`${n.ma} ${n.chu}`, 0.875) + 1.5 * f + 3, h: 1.9 * f }
  if (n.loai === 'hh') return { w: 2.2 * f + 5, h: 2.2 * f + 5 }
  return { w: dai(`${n.chu} việc chờ`, 0.875) + 1.7 * f, h: 2 * f + 5 }
}

test('khít khung: mọi góc sàn nằm trong khung khi không phóng; PHONG_TO phóng 1,12 lần quanh tâm', () => {
  for (const [w, h] of [[1100, 640], [343, 460], [1280, 400]]) {
    const c = camera()
    datKhung(c, w, h, 1)
    for (const v of gocSan(BO_TRI.phong)) {
      const p = v.clone().project(c)
      assert.ok(Math.abs(p.x) <= 1 && Math.abs(p.y) <= 1, `${w}x${h} ${v.toArray()}`)
    }
    const r = (k) => (k.right - k.left) / (k.top - k.bottom)
    const a = khit(c, gocSan(BO_TRI.phong), w, h, 1)
    const b = khit(c, gocSan(BO_TRI.phong), w, h)
    assert.ok(Math.abs(r(a) - w / h) < 1e-9 && Math.abs((a.right - a.left) / (b.right - b.left) - PHONG_TO) < 1e-9)
  }
})

test('boTriNhan: không chồng nhãn với dữ liệu kiểu mockup ở 1280, 1024, 375 px', () => {
  for (const [w, h] of [[1280, 700], [1108, 646], [1024, 600], [740, 540], [343, 460]]) {
    const c = camera()
    datKhung(c, w, h)
    const nhan = dungNhan(BO_TRI)
    const f = coChu(w)
    const co = Object.fromEntries(nhan.map((n) => [n.id, uocCo(n, f)]))
    const kq = xepNhan(nhan, chieuNhan(c, w, h, nhan, BO_TRI.nhanVat), co)
    assert.equal(kq.chong, 0, `${w}x${h}`)
    assert.equal(Object.keys(kq.viTri).length, nhan.length)
    for (const n of nhan) {
      const v = kq.viTri[n.id]
      assert.ok(v.x >= 2 && v.y >= 2 && v.x + co[n.id].w <= w - 2 + 1e-9, `${n.id} trong khung ${w}`)
    }
  }
})

test('boTriNhan: thứ tự ưu tiên bong bóng trước biển; đường chỉ khi dời > 10 px', () => {
  const o = (loai, x0, y0) => ({ loai, w: 100, h: 20, x0, y0, diemNeo: { x: x0 + 50, y: y0 + 40 } })
  const bien = o('bien', 100, 100)
  const bb = o('bb', 100, 100)
  const duong = boTriNhan([bien, bb], [], 800, 600)
  assert.deepEqual([bb.x, bb.y], [100, 100])                                   // bong bóng giữ chỗ
  assert.ok(Math.hypot(bien.x - 100, bien.y - 100) > 10)
  assert.equal(duong.length, 1)
  assert.deepEqual(duong[0].slice(0, 2), [150, 140])
  assert.equal(demChong([bien, bb]), 0)
  const mot = o('ten', 10, 10)
  assert.deepEqual(boTriNhan([mot], [], 800, 600), [])
  assert.equal(demChong([{ x: 0, y: 0, w: 10, h: 10 }, { x: 5, y: 5, w: 10, h: 10 }]), 1)
})

test('khói dựng cảnh: phòng, sàn bấm được, tủ máy theo muc, đèn Điều phối', () => {
  const canh = dungCanh(BO_TRI)
  const san = []
  canh.goc.traverse((o) => { if (o.userData.chon?.loai === 'phong' && o.isMesh) san.push(o.userData.chon.ma) })
  assert.deepEqual(san.sort(), PHONG.map((p) => p.ma).sort())
  const khe = []
  canh.goc.traverse((o) => { if (o.userData.chon?.loai === 'khe') khe.push(o.userData.chon.khe_id) })
  assert.deepEqual(khe.sort(), NV.map((n) => n.khe_id).sort())
  const tu = canh.goc.userData.tu.map((m) => m.material.color.getHexString())
  assert.deepEqual(tu, ['f2c14e', 'e0574a', '5fd38a', '5fd38a'])
  const den = (sang) => dungCanh(boTriVanPhong(PHONG.map((p) => ({ ...p, sang })), NV, [])).goc.userData.den.material
  assert.deepEqual([den(true).emissive.getHexString(), den(true).color.getHexString()], ['f2c14e', 'f2c14e'])
  assert.deepEqual([den(false).emissive.getHexString(), den(false).color.getHexString()], ['000000', 'b7b7b7'])
  assert.equal(canh.dong.filter((d) => d.man).length, 1)                       // màn đỏ của khe lỗi nhấp nháy
  huyCanh(canh.goc)
})
