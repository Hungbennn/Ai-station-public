import assert from 'node:assert/strict'
import { test } from 'node:test'
import * as luat from '../src/luat.js'
import * as hienThi from '../src/van_phong/hien_thi.js'

// bs-2bd.1.9: hai export không nơi nào dùng (src/, tests/) — bỏ để không ai tưởng là luật đang chạy.
test('không còn export chết HANG_COT, TEN_HIEN_THI', () => {
  assert.equal('HANG_COT' in luat, false)
  assert.equal('TEN_HIEN_THI' in hienThi, false)
  assert.equal(typeof luat.TEN_HANG, 'object')
  assert.equal(typeof hienThi.tuThe, 'function')
})
