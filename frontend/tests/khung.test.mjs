import assert from 'node:assert/strict'
import { test } from 'node:test'
import { BIEU_TUONG, duongVe } from '../src/bieu_tuong.js'
import { MENU, mucCua, tenTrang } from '../src/menu.js'
import { laPhimTim, timKiem } from '../src/tim.js'

test('menu 9 mục đúng thứ tự mockup, bí danh /nho và / ', () => {
  assert.deepEqual(MENU.map((m) => m.ten), ['Tổng quan', 'Dự án', 'Văn phòng', 'Công việc', 'Đội ngũ AI', 'Ký ức',
    'Usage & chi phí', 'Phê duyệt', 'Cài đặt'])
  assert.equal(mucCua('/nho').ma, 'ky-uc')
  assert.equal(mucCua('/').ma, 'tong-quan')
  assert.equal(mucCua('/cong-viec?du_an=hr&bead=hr-1').ma, 'cong-viec')
  assert.equal(mucCua('/phan-luong'), null)
  assert.equal(tenTrang('/doi-ngu'), 'Đội ngũ AI')
  assert.equal(tenTrang('/la'), 'Ben Station')
})

test('mỗi mục menu có icon; icon chỉ gồm lệnh path hợp lệ', () => {
  for (const m of MENU) assert.ok(duongVe(m.ma).length > 0, m.ma)
  for (const [ten, ds] of Object.entries(BIEU_TUONG)) {
    for (const d of ds) assert.match(d, /^[MmLlHhVvCcSsQqTtAaZz0-9 .,-]+$/, ten)
  }
  assert.deepEqual(duongVe('khong-co'), [])
})

test('tìm ⌘K: không dấu, dự án → bead → khe, tối đa 8', () => {
  const dl = { duAn: ['hr-codex', 'tram'], the: [{ id: 'hr-3', du_an: 'hr-codex', tieu_de: 'Chọn cách tính thuế' }],
    khe: [{ khe_id: 'B/codex-1', ten: 'Codex 1', ten_goi_nho: 'codex-chinh' }] }
  assert.deepEqual(timKiem('thue', dl).map((k) => k.den),
    [{ path: '/cong-viec', query: { du_an: 'hr-codex', bead: 'hr-3' } }])
  assert.deepEqual(timKiem('hr', dl).map((k) => k.loai), ['du-an', 'bead'])
  assert.deepEqual(timKiem('codex 1', dl)[0],
    { loai: 'khe', nhan: 'Codex 1', phu: 'B/codex-1', den: { path: '/doi-ngu' } })
  assert.deepEqual(timKiem('  ', dl), [])
  const nhieu = { the: Array.from({ length: 12 }, (_, i) => ({ id: `x-${i}`, du_an: 'x', tieu_de: 'việc' })) }
  assert.equal(timKiem('viec', nhieu).length, 8)
  assert.equal(laPhimTim({ metaKey: true, key: 'k' }), true)
  assert.equal(laPhimTim({ ctrlKey: true, key: 'K' }), true)
  assert.equal(laPhimTim({ key: 'k' }), false)
})
