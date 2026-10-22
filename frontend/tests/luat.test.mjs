import assert from 'node:assert/strict'
import { test } from 'node:test'
import { ghi, thanGhi } from '../src/api.js'
import { choPhepKeo, duAnChiQuetThu, gioVN, khoaMucPheDuyet, laLinkAnToan, nhomPheDuyet, nhomTheoHang, tieuDeTab }
  from '../src/luat.js'

test('nhomTheoHang xếp thẻ theo hàng và ưu tiên; hàng lạ về chưa chấm', () => {
  const n = nhomTheoHang([{ id: 'b', hang: 'ai-lam', uu_tien: 2 }, { id: 'a', hang: 'ai-lam', uu_tien: 1 },
    { id: 'c', hang: 'la' }])
  assert.deepEqual(n['ai-lam'].map((t) => t.id), ['a', 'b'])
  assert.deepEqual(n['chua-cham'].map((t) => t.id), ['c'])
  assert.deepEqual(n.epic, [])
})

test('choPhepKeo chỉ giữa cột 1 và cột 2', () => {
  const t = { keo_duoc: true, hang: 'ai-lam' }
  assert.equal(choPhepKeo(t, 'can-chot'), true)
  assert.equal(choPhepKeo(t, 'ai-lam'), false)
  assert.equal(choPhepKeo(t, 'cho-review'), false)
  assert.equal(choPhepKeo({ ...t, keo_duoc: false }, 'can-chot'), false)
  assert.equal(choPhepKeo(null, 'can-chot'), false)
})

test('tiêu đề tab và link an toàn', () => {
  assert.equal(tieuDeTab(0), 'Tổng quan · Ben Station')
  assert.equal(tieuDeTab(3, 'Phê duyệt'), '(3) Phê duyệt · Ben Station')
  assert.equal(laLinkAnToan('https://github.com/o/r/pull/7'), true)
  assert.equal(laLinkAnToan('javascript:alert(1)'), false)
  assert.equal(laLinkAnToan('http://github.com/o/r/pull/7'), false)
  assert.equal(laLinkAnToan('https://evil.example/o/r/pull/7'), false)
  assert.equal(laLinkAnToan('https://github.com.evil.example/x'), false)
  assert.equal(laLinkAnToan(null), false)
})

test('nhomPheDuyet giữ thứ tự độ gấp, bỏ nhóm rỗng', () => {
  const n = nhomPheDuyet([{ loai: 'cho-review', bead_id: '1' }, { loai: 'decision', bead_id: '3' },
    { loai: 'escalation', bead_id: '2' }])
  assert.deepEqual(n.map(([loai]) => loai), ['escalation', 'decision', 'cho-review'])
})

test('khoaMucPheDuyet phân biệt hai mục hệ không bead cùng dự án', () => {
  const a = { loai: 'he', du_an: 'hr', bead_id: null, chi_tiet: { su_kien: 'quet.loi' } }
  const b = { loai: 'he', du_an: 'hr', bead_id: null, chi_tiet: { su_kien: 'nho.loi_llm' } }
  assert.notEqual(khoaMucPheDuyet(a), khoaMucPheDuyet(b))
  assert.equal(khoaMucPheDuyet({ loai: 'cho-review', du_an: 'hr', bead_id: 'hr-1', chi_tiet: {} }), 'cho-review/hr/hr-1/')
})

test('gioVN đổi sang giờ Việt Nam', () => {
  assert.match(gioVN('2026-10-13T01:00:00Z'), /08:00/)
  assert.equal(gioVN(null), '')
})

test('thanGhi gắn ma_thao_tac và expected_version', () => {
  assert.deepEqual(thanGhi({ cot: 'ai-lam' }, 'v1', 'ma-co-dinh-01'),
    { cot: 'ai-lam', ma_thao_tac: 'ma-co-dinh-01', expected_version: 'v1' })
  assert.match(thanGhi({}, 'v').ma_thao_tac, /^[0-9a-f-]{36}$/)
})

test('ghi gửi X-Tram và ném lỗi kèm status', async () => {
  let goi
  globalThis.fetch = async (url, opt) => {
    goi = { url, opt }
    return new Response(JSON.stringify({ loi: 'Bead đã đổi' }), { status: 409 })
  }
  await assert.rejects(ghi('/api/x', { a: 1 }), (e) => e.status === 409 && e.message === 'Bead đã đổi')
  assert.equal(goi.opt.method, 'POST')
  assert.equal(goi.opt.headers['X-Tram'], '1')
  assert.equal(goi.opt.body, '{"a":1}')
})

test('duAnChiQuetThu chỉ lấy dự án bat_ghi === false', () => {
  const ds = [{ ten: 'hr', bat_ghi: true }, { ten: 'kt', bat_ghi: false }, { ten: 'cu' }]
  assert.deepEqual([...duAnChiQuetThu(ds)], ['kt'])
  assert.deepEqual([...duAnChiQuetThu(null)], [])
})
