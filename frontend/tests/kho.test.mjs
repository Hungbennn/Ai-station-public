// bs-78r.8 (a): tải lại /api/chu/trang-thai khi SSE nối lại và khi tab hiện lại / được focus, để nút ghi tắt ngay
// khi danh tính đổi giữa phiên. Máy chủ vẫn là nơi chặn ghi (403); đây chỉ là giao diện theo kịp.
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { test } from 'node:test'
import { kho, moLuong, taiTrangThai, theoDoiTab } from '../src/kho.js'

class NguonGia {
  constructor(url) { this.url = url; this.nghe = {} }
  addEventListener(ten, f) { this.nghe[ten] = f }
}
const xong = () => new Promise((r) => setImmediate(r))

test('SSE: lần mở đầu không tải lại; mỗi lần nối lại sau đó tải lại trạng thái', async () => {
  const goi = []
  globalThis.fetch = async (url) => { goi.push(url); return new Response(JSON.stringify({ la_dai_ca: false })) }
  globalThis.EventSource = NguonGia
  const es = moLuong()
  assert.equal(es.url, '/api/luong')
  es.onopen()
  await xong()
  assert.deepEqual(goi, [])
  es.onerror()
  assert.equal(kho.matKetNoi, true)
  es.onopen()
  await xong()
  assert.deepEqual(goi, ['/api/chu/trang-thai'])
  assert.equal(kho.matKetNoi, false)
  assert.deepEqual(kho.trangThai, { la_dai_ca: false })
  es.onopen()
  await xong()
  assert.equal(goi.length, 2)
})

test('tab hiện lại hoặc được focus thì tải lại; tab ẩn thì không; hàm trả về gỡ được', () => {
  let n = 0
  const d = new EventTarget()
  const w = new EventTarget()
  d.visibilityState = 'visible'
  const go = theoDoiTab(() => { n += 1 }, d, w)
  d.dispatchEvent(new Event('visibilitychange'))
  w.dispatchEvent(new Event('focus'))
  assert.equal(n, 2)
  d.visibilityState = 'hidden'
  d.dispatchEvent(new Event('visibilitychange'))
  assert.equal(n, 2)
  go()
  d.visibilityState = 'visible'
  d.dispatchEvent(new Event('visibilitychange'))
  w.dispatchEvent(new Event('focus'))
  assert.equal(n, 2)
})

test('KhungChinh gắn theoDoiTab() lúc mở trang', () => {
  const vue = readFileSync(new URL('../src/KhungChinh.vue', import.meta.url), 'utf8')
  assert.match(vue, /onMounted\(\(\) => \{[^}]*theoDoiTab\(\)/)
})


// Q05 review đợt 6: lỗi tải quyền và phản hồi về đảo thứ tự không được mở lại nút ghi.
test('đang tải và tải lỗi đều khóa quyền cũ', async (t) => {
  const cu = globalThis.fetch
  t.after(() => { globalThis.fetch = cu })
  let huy
  globalThis.fetch = () => new Promise((resolve, reject) => { huy = reject })
  kho.trangThai = { la_dai_ca: true }
  const viec = taiTrangThai()
  assert.equal(kho.trangThai, null)
  huy(new Error('mất kết nối'))
  await viec
  assert.equal(kho.trangThai, null)
})

test('phản hồi owner cũ về sau không ghi đè danh tính mới', async (t) => {
  const cu = globalThis.fetch
  t.after(() => { globalThis.fetch = cu })
  const tra = []
  globalThis.fetch = () => new Promise((resolve) => { tra.push(resolve) })
  const dau = taiTrangThai()
  const sau = taiTrangThai()
  tra[1](new Response(JSON.stringify({ la_dai_ca: false })))
  await sau
  tra[0](new Response(JSON.stringify({ la_dai_ca: true })))
  await dau
  assert.deepEqual(kho.trangThai, { la_dai_ca: false })
})
