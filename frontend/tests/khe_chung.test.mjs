import assert from 'node:assert/strict'
import { test } from 'node:test'
import { cuaSo, hanMucThapNhat, oHanMuc, tenKhe } from '../src/luat_han_muc.js'
import { BANG_MAU, fnv1a, mauKhe } from '../src/mau_khe.js'

const cs = (loai, dung, reset = '2026-10-15T16:40:00Z') =>
  ({ loai, trang_thai: 'biet', phan_tram: dung, reset_luc: reset })
const BAY = '2026-10-15T15:17:00Z'

test('màu khe ổn định theo băm, nằm trong bảng mockup', () => {
  assert.equal(fnv1a('a'), 0xe40c292c)
  assert.deepEqual(mauKhe('B/claude-1'), mauKhe('B/claude-1'))
  assert.ok(BANG_MAU.some(([than, toc]) => than === mauKhe('B/codex-9').than && toc === mauKhe('B/codex-9').toc))
})

test('ô hạn mức: còn = 100 − đã dùng, lớp thấp/hết, chưa biết', () => {
  assert.deepEqual(oHanMuc(cs('5h', 38), BAY), { con: 62, lop: '', rong: 62, chu: 'còn 62% · reset 23:40' })
  assert.equal(oHanMuc(cs('5h', 75), BAY).lop, 'thap')
  assert.deepEqual(oHanMuc(cs('5h', 100), BAY), { con: 0, lop: 'het', rong: 2, chu: 'còn 0% · reset 23:40' })
  assert.equal(oHanMuc({ loai: '5h', trang_thai: 'chua_biet', phan_tram: null }, BAY).chu, 'chưa biết')
  assert.equal(oHanMuc(null).con, null)
})

test('hạn mức thấp nhất và tên khe', () => {
  const ds = [{ khe_id: 'B/claude-1', ten: 'Claude 1', han_muc: { cua_so: [cs('5h', 38), cs('tuan', 19)] } },
    { khe_id: 'B/claude-4', han_muc: { cua_so: [cs('5h', 100, '2026-10-15T17:12:00Z')] } },
    { khe_id: 'B/codex-2', han_muc: { cua_so: [] } }]
  assert.equal(cuaSo(ds[0], 'tuan').phan_tram, 19)
  const t = hanMucThapNhat(ds, BAY)
  assert.deepEqual([t.khe.khe_id, t.con, t.reset], ['B/claude-4', 0, '00:12'])
  assert.equal(hanMucThapNhat([ds[2]], BAY), null)
  assert.equal(tenKhe(ds[0]), 'Claude 1')
  assert.equal(tenKhe(ds[1]), 'Claude 4')
  assert.equal(tenKhe('B/codex-de-danh'), 'Codex de danh')
})
