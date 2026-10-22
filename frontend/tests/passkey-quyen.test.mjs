import test from 'node:test'
import assert from 'node:assert/strict'
import { quyenPasskey, duocGhi, capNhat } from '../src/quyen_passkey.js'

test('chưa có passkey khóa ghi, lỗi đọc cũng khóa, hết phiên vẫn cho N', () => {
  capNhat(null)
  assert.equal(duocGhi({la_dai_ca:true}), false)
  capNhat({thiet_bi:[],con_giay:0})
  assert.equal(duocGhi({la_dai_ca:true}), false)
  capNhat({thiet_bi:[{}],con_giay:0})
  assert.equal(duocGhi({la_dai_ca:true}), true)
  assert.equal(duocGhi({la_dai_ca:false}), false)
  assert.equal(duocGhi(null), false)
  capNhat(null)
})
