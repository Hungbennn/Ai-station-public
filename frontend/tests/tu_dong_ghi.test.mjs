import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { test } from 'node:test'
import { dungGhiTuDong } from '../src/thanh/tu_dong/ghi_tu_dong.js'

const CD = { tu_merge: true, tu_deploy: false, dieu_kien: { ci: true, cot: true, hang_rao: true },
  lenh: { deploy: 'make deploy', kiem_song: 'sh kiem.sh', lui: 'sh lui.sh' } }
const DL = { du_an: 'repo nhap', phien_ban: '41', cai_dat: CD }
const TEN = () => 'repo nhap'                              // tên dự án của route
const XUNG_DOT = 'Cài đặt đã đổi — tải lại'

function gia(phanHoi) {
  const goi = []
  globalThis.fetch = async (url, o) => {
    goi.push({ url, than: JSON.parse(o.body), xTram: o.headers['X-Tram'] })
    return phanHoi()
  }
  return goi
}
const boMa = ({ ma_thao_tac: ma, ...r }) => { assert.ok(ma.length >= 8); return r }

test('lưu cài đặt: thân đủ khoá + expected_version đang xem, X-Tram; huỷ hộp xác nhận thì không gửi gì', async () => {
  const hoi = []
  globalThis.window = { confirm: (c) => { hoi.push(c); return hoi.length > 1 } }
  let tai = 0
  const g = dungGhiTuDong(() => DL, async () => { tai += 1 }, TEN)
  const goi = gia(() => new Response('{"ket_qua": {}, "lap_lai": false}'))
  assert.equal(await g.luu({ tu_merge: false }, 'Tắt tự merge?'), false)
  assert.deepEqual(goi, [])
  assert.equal(await g.luu({ tu_merge: false }, 'Tắt tự merge?'), true)
  assert.deepEqual(hoi, ['Tắt tự merge?', 'Tắt tự merge?'])
  assert.equal(goi[0].url, '/api/du-an/repo%20nhap/tu-dong/cai-dat')
  assert.equal(goi[0].xTram, '1')
  assert.deepEqual(boMa(goi[0].than), { expected_version: '41', cai_dat: { ...CD, tu_merge: false } })
  assert.equal(tai, 1)
  assert.equal(await g.luu({ dieu_kien: { ci: true } }, ''), true)          // không hỏi khi câu hỏi rỗng
  assert.equal(hoi.length, 2)
})

test('409 / 422 / 403: báo tại chỗ, không tải lại, nút mở lại; 409 cài đặt → "Cài đặt đã đổi — tải lại"', async () => {
  globalThis.window = { confirm: () => true }
  let tai = 0
  const g = dungGhiTuDong(() => DL, async () => { tai += 1 }, TEN)
  const loi409 = 'Cài đặt tự động của repo nhap đã đổi (hiện 42, đang xem 41) — tải lại'
  gia(() => new Response(JSON.stringify({ loi: loi409 }), { status: 409 }))
  assert.equal(await g.luu({ lenh: { deploy: 'x' } }, 'Lưu?'), false)
  assert.equal(g.loi.value, XUNG_DOT)
  assert.equal(g.xungDot.value, true)                                       // khối hiện nút "Tải lại"
  assert.equal(g.dangGui.value, false)
  gia(() => new Response(JSON.stringify({ detail: 'cần kênh ghi unix-socket — cửa ghi còn tạm' }), { status: 403 }))
  assert.equal(await g.luu({ tu_merge: false }, ''), false)
  assert.match(g.loi.value, /^cần kênh ghi unix-socket/)
  assert.equal(g.xungDot.value, false)
  const cu = 'Có bản mới hơn — tải lại (bản chờ deploy của repo nhap đã đổi: hiện b2, đang xem a41c07e)'   // TM-3
  gia(() => new Response(JSON.stringify({ loi: cu }), { status: 409 }))
  assert.equal(await g.deploy('a41c07e9d2b8'), false)
  assert.equal(g.loi.value, cu)
  assert.equal(tai, 0)
})

test('TẠM DỪNG hỏi lại, Tiếp tục không hỏi; cả hai không kiểm phiên bản; Deploy mang expected_commit', async () => {
  const hoi = []
  globalThis.window = { confirm: (c) => { hoi.push(c); return true } }
  const g = dungGhiTuDong(() => DL, async () => {}, TEN)
  const goi = gia(() => new Response('{}'))
  await g.tamDung(true)
  await g.tamDung(false)
  await g.deploy('a41c07e9d2b8')
  assert.deepEqual(goi.map((x) => x.url), ['/api/du-an/repo%20nhap/tu-dong/tam-dung',
    '/api/du-an/repo%20nhap/tu-dong/tiep-tuc', '/api/du-an/repo%20nhap/tu-dong/deploy'])
  assert.deepEqual(goi.map((x) => boMa(x.than)), [{ expected_version: '' }, { expected_version: '' },
    { expected_version: '41', expected_commit: 'a41c07e9d2b8' }])
  assert.equal(hoi.length, 2)
  assert.match(hoi[0], /^Tạm dừng tự merge và tự deploy của repo nhap\?/)
  assert.match(hoi[1], /^Deploy bản a41c07e của repo nhap/)
})

test('Q9: lưu theo bản chụp lúc mở form — SSE đổi `dl` giữa chừng không đổi phiên bản gửi đi', async () => {
  globalThis.window = { confirm: () => true }
  let dl = DL
  const g = dungGhiTuDong(() => dl, async () => {}, TEN)
  const ban = JSON.parse(JSON.stringify(DL))                                 // chụp lúc mở form (phiên bản 41)
  dl = { ...DL, phien_ban: '42', cai_dat: { ...CD, lenh: { ...CD.lenh, deploy: 'make deploy-moi' } } }  // tab khác lưu
  const goi = gia(() => new Response(JSON.stringify({ loi: 'đã đổi — tải lại' }), { status: 409 }))
  assert.equal(await g.luu({ lenh: { deploy: 'make deploy-cu' } }, '', ban), false)
  assert.deepEqual(boMa(goi[0].than), { expected_version: '41',
    cai_dat: { ...CD, lenh: { ...CD.lenh, deploy: 'make deploy-cu' } } })
  assert.equal(g.loi.value, XUNG_DOT)
})

test('Q10: thao tác theo tên dự án của route; dữ liệu dự án khác thì không gửi; kết quả về muộn thì bỏ', async () => {
  globalThis.window = { confirm: () => true }
  let ten = 'a'
  let tai = 0
  const g = dungGhiTuDong(() => ({ ...DL, du_an: 'a' }), async () => { tai += 1 }, () => ten)
  const goi = gia(() => new Response('{}'))
  ten = 'b'                                                                  // route đã sang b, `dl` còn của a
  assert.equal(await g.luu({ tu_merge: false }, ''), false)
  assert.deepEqual(goi, [])
  assert.equal(g.loi.value, XUNG_DOT)
  await g.tamDung(true)
  await g.deploy('a41c07e9d2b8')
  assert.deepEqual(goi.map((x) => x.url), ['/api/du-an/b/tu-dong/tam-dung', '/api/du-an/b/tu-dong/deploy'])
  assert.equal(tai, 2)
  let tra
  globalThis.fetch = () => new Promise((r) => { tra = r })
  const viec = g.tamDung(false)
  ten = 'c'                                                                  // chuyển trang khi đang gửi
  tra(new Response(JSON.stringify({ loi: 'Estop đang bật' }), { status: 422 }))
  assert.equal(await viec, false)
  assert.deepEqual([g.loi.value, tai], ['', 2])                              // không ghi lỗi của b lên trang c
})

test('tuyến /du-an/:ten tới trang Tự động (mục "Dự án" sáng theo mucCua)', () => {
  const tuyen = readFileSync(new URL('../src/tuyen.js', import.meta.url), 'utf8')
  assert.match(tuyen, /\{ path: '\/du-an\/:ten', component: TuDong \}/)
  assert.match(tuyen, /^import TuDong from '\.\/trang\/TuDong\.vue'$/m)
})
