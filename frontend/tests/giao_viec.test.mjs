import assert from 'node:assert/strict'
import { test } from 'node:test'
import { canhBaoPr, ganGiaoViec, nhanChuaGiao } from '../src/giao_viec.js'
import { canhBaoPrTram, lopPrTram, moTaPrTram, nhanPrTram, prTram } from '../src/giao_viec.js'

test('ganGiaoViec gắn theo khoá du_an/id, thiếu thì null', () => {
  const ds = ganGiaoViec([{ du_an: 'hr', id: 'a' }, { du_an: 'hr', id: 'b' }],
    { 'hr/a': { khong_giao: 'thiếu tiêu chí', pr: null } })
  assert.deepEqual(ds.map((t) => t.giao), [{ khong_giao: 'thiếu tiêu chí', pr: null }, null])
  assert.deepEqual(ganGiaoViec([{ du_an: 'hr', id: 'a' }], undefined)[0].giao, null)
})

test('nhanChuaGiao chỉ khi có lý do', () => {
  assert.equal(nhanChuaGiao({ giao: { khong_giao: 'chờ merge spec' } }), 'chờ merge spec')
  assert.equal(nhanChuaGiao({ giao: null }), '')
  assert.equal(nhanChuaGiao(null), '')
})

test('canhBaoPr: lệch nhánh, chưa kiểm được, khớp', () => {
  const pr = { nhanh: 'tram/hr-1', commit: 'a'.repeat(40), tu_xa: 'a'.repeat(40), lech: false }
  assert.equal(canhBaoPr(pr), '')
  assert.match(canhBaoPr({ ...pr, tu_xa: 'b'.repeat(40), lech: true }), /KHÁC commit/)
  assert.match(canhBaoPr({ ...pr, tu_xa: null }), /Chưa kiểm được/)
  assert.equal(canhBaoPr(null), '')
})

test('nhanPrTram, lopPrTram: nhãn và lớp chip theo mockup; trạng thái lạ thì không có', () => {
  const the = (tram) => ({ giao: { khong_giao: null, pr: { nhanh: 'tram/hr-1', tram } } })
  assert.equal(nhanPrTram(the({ so: 7, trang_thai: 'khong_xac_minh', ly_do: 'x' })), 'PR không xác minh được')
  assert.equal(nhanPrTram(the({ so: 7, trang_thai: 'mo', ly_do: null })), 'PR đã mở')
  assert.equal(nhanPrTram(the({ so: 7, trang_thai: 'da_merge', ly_do: null })), 'PR đã merge')
  assert.equal(nhanPrTram(the({ so: 7, trang_thai: 'constructor', ly_do: null })), '')
  assert.equal(nhanPrTram(the(null)), '')
  assert.equal(nhanPrTram({ giao: null }), '')
  assert.equal(prTram(null), null)
  assert.equal(lopPrTram({ trang_thai: 'khong_xac_minh' }), 'pr-khong_xac_minh')
  assert.equal(lopPrTram({ trang_thai: 'x" onclick="' }), '')
  assert.equal(lopPrTram(null), '')
})

test('moTaPrTram, canhBaoPrTram: số PR chỉ khi là số nguyên; cảnh báo chỉ khi không xác minh được', () => {
  const t = { so: 12, url: null, trang_thai: 'khong_xac_minh', ly_do: 'không phải merge commit (squash / rebase)' }
  assert.equal(moTaPrTram(t), 'PR #12 — không phải merge commit (squash / rebase)')
  assert.equal(moTaPrTram({ ...t, so: '12<b>', trang_thai: 'da_merge', ly_do: null }), 'PR')
  assert.equal(moTaPrTram(null), '')
  assert.equal(canhBaoPrTram(t), 'PR đã merge nhưng trạm không xác minh được: không phải merge commit'
    + ' (squash / rebase). Bead ở lại cột 3 — Đại ca tự kiểm rồi bấm Duyệt.')
  assert.equal(canhBaoPrTram({ ...t, trang_thai: 'mo' }), '')
  assert.equal(canhBaoPrTram(null), '')
})
