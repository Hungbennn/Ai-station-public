import assert from 'node:assert/strict'
import { test } from 'node:test'
import { COT, chipCot, chipThe, dongKhe, uuTien, viTriThe } from '../src/luat_cong_viec.js'
import { mauKhe } from '../src/mau_khe.js'

const the = (x = {}) => ({ du_an: 'hr', id: 'hr-1', hang: 'ai-lam', loai: 'bug', uu_tien: 1, khoa: false, co_do: false,
  lech: false, khe_spec: false, cho: [], giao: null, ...x })

test('COT theo mockup: ba cột, số thứ tự, tên, mô tả', () => {
  assert.deepEqual(COT.map((c) => [c.hang, c.so, c.ten]),
    [['ai-lam', 1, 'AI tự làm'], ['can-chot', 2, 'Cần Đại ca chốt'], ['cho-review', 3, 'Chờ review để đóng']])
  assert.equal(COT[2].moTa, 'Đã code + QC, chờ Duyệt')
})

test('chipCot suy từ hang; hàng ngoài ba cột không có chip', () => {
  assert.equal(chipCot(the()), 'cot:ai-lam')
  assert.equal(chipCot(the({ hang: 'cho-review' })), 'cot:cho-review')
  assert.equal(chipCot(the({ hang: 'chua-cham' })), '')
  assert.equal(chipCot(null), '')
})

test('viTriThe và uuTien cho ngăn bên', () => {
  assert.equal(viTriThe(the({ hang: 'can-chot' })), 'cột 2')
  assert.equal(viTriThe(the({ hang: 'epic' })), 'Epic')
  assert.equal(uuTien(the()), 'P1')
  assert.equal(uuTien(the({ uu_tien: null })), 'P?')
})

test('chipThe: thứ tự cột → khoá → cờ đỏ → lệch → chưa giao → chờ → khe spec → chỉ quét thử → PR', () => {
  const t = the({ khoa: true, co_do: true, lech: true, khe_spec: true, cho: ['hr-2', 'hr-3'],
    giao: { khong_giao: 'thiếu tiêu chí', pr: { tram: { so: 12, trang_thai: 'da_merge', ly_do: '' } } } })
  assert.deepEqual(chipThe(t, true).map((c) => [c.chu, c.lop]), [
    ['cot:ai-lam', 'mono'], ['khoá', ''], ['cờ đỏ', 'tt-loi'], ['nhãn lệch', 'tt-cau_dao'], ['chưa giao', 'tt-cau_dao'],
    ['chờ hr-2, hr-3', ''], ['khe spec', ''], ['chỉ quét thử', 'tt-tat'], ['PR đã merge', 'pr-da_merge']])
  assert.equal(chipThe(t).find((c) => c.chu === 'chưa giao').goiY, 'thiếu tiêu chí')
  assert.deepEqual(chipThe(the({ hang: 'epic' })), [])
})

test('dongKhe ghép khe đang giữ phiếu đúng dự án + bead', () => {
  const ds = [
    { khe_id: 'B/codex-1', ten: 'Codex 1', trang_thai: 'can_nguoi',
      phieu: { du_an: 'hr', bead_id: 'hr-1', buoc: 'qc' } },
    { khe_id: 'B/claude-1', trang_thai: 'lam', phieu: { du_an: 'khac', bead_id: 'hr-1', buoc: 'code' } },
  ]
  assert.deepEqual(dongKhe(the(), ds), { ten: 'Codex 1', buoc: 'QC', canNguoi: true, mau: mauKhe('B/codex-1').than })
  assert.deepEqual(dongKhe(the({ du_an: 'khac' }), ds),
    { ten: 'Claude 1', buoc: 'code', canNguoi: false, mau: mauKhe('B/claude-1').than })
  assert.equal(dongKhe(the({ id: 'hr-9' }), ds), null)
  assert.equal(dongKhe(the(), [{ khe_id: 'x', phieu: null }]), null)
  assert.equal(dongKhe(the(), undefined), null)
})
