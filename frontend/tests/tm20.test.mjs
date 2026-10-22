import assert from 'node:assert/strict'
import { test } from 'node:test'
import { DIEU_KIEN, hoiLuuLenh, hoiDeploy } from '../src/luat_trang_tu_dong.js'

test('CI là khoá cứng; câu xác nhận không cấp quyền trạm cho mã dự án', () => {
  assert.equal(DIEU_KIEN.find(x => x.ma === 'ci').khoa, true)
  assert.match(hoiLuuLenh(false), /quyền riêng/)
  assert.match(hoiDeploy('a', 'a'.repeat(40)), /phạm vi/)
})
