// Codex vòng 1 Q9, Q10: form sửa lệnh giữ bản chụp lúc mở; trang Tự động bỏ phản hồi cũ, xoá dữ liệu khi đổi dự án.
import assert from 'node:assert/strict'
import { test } from 'node:test'
import { dungGhiTuDong } from '../src/thanh/tu_dong/ghi_tu_dong.js'
import { dungSuaLenh } from '../src/thanh/tu_dong/sua_lenh.js'
import { dungTaiDuAn } from '../src/thanh/tu_dong/tai_du_an.js'

const LENH = { deploy: 'make deploy', kiem_song: 'sh kiem.sh', lui: 'sh lui.sh' }
const ban = (du_an, phien_ban, deploy = 'make deploy') => ({ du_an, phien_ban, cai_dat: { tu_merge: true,
  tu_deploy: false, dieu_kien: { ci: true, cot: true, hang_rao: true }, lenh: { ...LENH, deploy } } })
const json = (o, status = 200) => new Response(JSON.stringify(o), { status })
const XUNG_DOT = 'Cài đặt đã đổi — tải lại'

test('Q9: SSE chen giữa mở form và lưu → 409 giữ nháp; "Tải lại" lấy bản mới làm gốc, nháp còn, lưu lại', async () => {
  globalThis.window = { confirm: () => true }
  let dl = ban('a', '41')
  const g = dungGhiTuDong(() => dl, async () => {}, () => 'a')
  const s = dungSuaLenh(() => dl, g, async () => { dl = ban('a', '42', 'make deploy-moi'); return true })
  s.mo()
  s.o.deploy = 'make deploy-cua-a'
  dl = ban('a', '42', 'make deploy-moi')                     // tab khác lưu → SSE → trang tải lại `dl`
  const goi = []
  globalThis.fetch = async (url, o) => {
    goi.push(JSON.parse(o.body))
    return goi.length === 1 ? json({ loi: 'Cài đặt tự động của a đã đổi (hiện 42, đang xem 41) — tải lại' }, 409)
      : json({ ket_qua: {}, lap_lai: false })
  }
  await s.luu()
  assert.deepEqual([goi[0].expected_version, goi[0].cai_dat.lenh.deploy], ['41', 'make deploy-cua-a'])
  assert.deepEqual([s.dangSua.value, s.o.deploy, g.loi.value, g.xungDot.value],
    [true, 'make deploy-cua-a', XUNG_DOT, true])
  await s.taiLaiGoc()
  assert.equal(s.o.deploy, 'make deploy-cua-a')                // nháp giữ nguyên
  assert.equal(s.doiChieu.value.deploy, 'make deploy-moi')      // lệnh đang lưu ở trạm để đối chiếu
  assert.deepEqual([g.loi.value, g.xungDot.value], ['', false])
  await s.luu()
  assert.deepEqual([goi[1].expected_version, goi[1].cai_dat.lenh.deploy], ['42', 'make deploy-cua-a'])
  assert.deepEqual([s.dangSua.value, s.doiChieu.value], [false, null])
})

for (const status of [500, 404]) {
  test(`V2-N1: tải lại lỗi ${status} giữ xung đột và bản gốc của form`, async () => {
    globalThis.window = { confirm: () => true }
    const t = dungTaiDuAn(() => 'a')
    globalThis.fetch = async () => json(ban('a', '41'))
    assert.equal(await t.tai(), true)
    const g = dungGhiTuDong(() => t.dl.value, t.tai, () => 'a')
    const s = dungSuaLenh(() => t.dl.value, g, t.tai)
    s.mo()
    s.o.deploy = 'make nhap'
    g.loi.value = XUNG_DOT
    g.xungDot.value = true
    globalThis.fetch = async () => json({ loi: 'tải lỗi' }, status)
    await s.taiLaiGoc()
    assert.deepEqual([g.loi.value, g.xungDot.value, s.doiChieu.value], [XUNG_DOT, true, null])
    assert.deepEqual([s.dangSua.value, s.o.deploy], [true, 'make nhap'])
    globalThis.fetch = async () => json(ban('a', '42', 'make moi'))
    await t.tai()                                // SSE thành công không tự thay bản gốc đang sửa
    let than
    globalThis.fetch = async (url, o) => { than = JSON.parse(o.body); return json({ loi: XUNG_DOT }, 409) }
    await s.luu()
    assert.equal(than.expected_version, '41')
  })
}

test('Q10: chuyển route khi đang sửa A — không gửi nháp của A sang B', async () => {
  globalThis.window = { confirm: () => true }
  let ten = 'a'
  let dl = ban('a', '41')
  const g = dungGhiTuDong(() => dl, async () => {}, () => ten)
  const s = dungSuaLenh(() => dl, g, async () => {})
  s.mo()
  s.o.deploy = 'make deploy-cua-a'
  ten = 'b'
  dl = ban('b', '7')
  const goi = []
  globalThis.fetch = async (url) => { goi.push(url); return json({}) }
  await s.luu()
  assert.deepEqual(goi, [])
  assert.equal(g.loi.value, XUNG_DOT)
})

test('Q10: phản hồi về đảo thứ tự — chỉ giữ dữ liệu của dự án đang xem', async () => {
  let ten = 'a'
  const t = dungTaiDuAn(() => ten)
  const cho = {}
  globalThis.fetch = (url) => new Promise((r) => { cho[url] = r })
  const ta = t.doiDuAn()
  ten = 'b'
  const tb = t.doiDuAn()
  cho['/api/du-an/b/tu-dong'](json(ban('b', '7')))
  await tb
  cho['/api/du-an/a/tu-dong'](json(ban('a', '41')))
  await ta
  assert.equal(t.dl.value.du_an, 'b')
})

test('Q10: đổi sang B thì xoá dữ liệu A ngay; tải B lỗi → không còn dữ liệu A; 404 → không có dự án', async () => {
  let ten = 'a'
  const t = dungTaiDuAn(() => ten)
  globalThis.fetch = async (url) => (url.includes('/a/') ? json(ban('a', '41')) : json({ loi: 'trạm lỗi' }, 500))
  await t.doiDuAn()
  assert.equal(t.dl.value.du_an, 'a')
  globalThis.fetch = async () => json({ loi: 'mất kết nối' }, 502)
  await t.tai()                                                // tải lại CÙNG dự án lỗi: giữ dữ liệu A, báo lỗi
  assert.deepEqual([t.dl.value.du_an, t.loi.value], ['a', 'mất kết nối'])
  globalThis.fetch = async () => json({ loi: 'trạm lỗi' }, 500)
  ten = 'b'
  const viec = t.doiDuAn()
  assert.deepEqual([t.dl.value, t.loi.value], [null, ''])      // khoá ngay, không chờ B
  await viec
  assert.deepEqual([t.dl.value, t.loi.value, t.khongCo.value], [null, 'trạm lỗi', false])
  globalThis.fetch = async () => json({ detail: 'không có' }, 404)
  ten = 'c'
  await t.doiDuAn()
  assert.deepEqual([t.dl.value, t.khongCo.value, t.loi.value], [null, true, ''])
})

test('Q10: route đổi trước watcher tải mới — phản hồi A không được nhận vào B', async () => {
  let ten = 'a'
  const t = dungTaiDuAn(() => ten)
  let tra
  globalThis.fetch = () => new Promise((r) => { tra = r })
  const viec = t.tai()
  ten = 'b'
  tra(json(ban('a', '41')))
  await viec
  assert.equal(t.dl.value, null)
})
