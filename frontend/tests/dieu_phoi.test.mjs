import assert from 'node:assert/strict'
import { test } from 'node:test'
import { gioVN } from '../src/luat.js'
import { MAU, chuBien, chuNhip } from '../src/van_phong/hien_thi.js'

// Đèn Điều phối từ nhịp hook máy A (plan 2e Task 4, G9, G21; D38): server suy `sang`; trang chỉ đổi sang chữ, màu.
test('phòng Điều phối: chữ biển ba trạng thái, dòng nhịp cuối, màu đèn', () => {
  const p = { ma: 'dieu-phoi', loai: 'dieu_phoi', sang: false, nhip_cuoi: '2026-10-15T07:05:00Z' }
  assert.equal(chuBien(p), 'Điều phối · tắt đèn')
  assert.equal(chuBien({ ...p, sang: true }), 'Điều phối · đang có phiên')
  assert.equal(chuBien({ ...p, sang: null, nhip_cuoi: null }), 'Điều phối · chưa có tín hiệu')
  assert.equal(chuNhip(p), `nhịp cuối ${gioVN('2026-10-15T07:05:00Z')}`)
  assert.equal(chuNhip({ ...p, nhip_cuoi: null }), null)
  assert.equal(chuNhip({ ma: 'dieu-phoi', loai: 'dieu_phoi', sang: null }), null)                 // API 2c cũ
  assert.equal(chuNhip({ ma: 'giam-doc', loai: 'giam_doc', nhip_cuoi: '2026-10-15T07:05:00Z' }), null)
  assert.deepEqual([MAU.den, MAU.denTat], ['#f2c14e', '#b7b7b7'])                               // vàng ấm D38
})
