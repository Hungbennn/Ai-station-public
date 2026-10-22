import test from 'node:test'
import assert from 'node:assert/strict'
import { doc64, ghi64, tuyChon, phanHoi, hienPhien, nghiLe, datHoi } from '../src/passkey.js'

test('base64url và options chuyển đúng BufferSource, giữ UV', () => {
  const v = new Uint8Array([0, 127, 255])
  assert.deepEqual(new Uint8Array(doc64(ghi64(v))), v)
  const r = tuyChon({ challenge: ghi64(v), user: { id: ghi64(v) },
    allowCredentials: [{ id: ghi64(v) }], authenticatorSelection: { userVerification: 'required' } })
  assert.ok(r.challenge instanceof ArrayBuffer)
  assert.ok(r.user.id instanceof ArrayBuffer)
  assert.equal(r.authenticatorSelection.userVerification, 'required')
})
test('serialize cả assertion và registration, không private key', () => {
  const b = new Uint8Array([1, 2]).buffer
  const r = phanHoi({id:'AQI',rawId:b,type:'public-key',response:{clientDataJSON:b,signature:b,
    authenticatorData:b,userHandle:null}})
  assert.equal(r.response.signature,'AQI')
  assert.equal(r.response.userHandle,null)
  assert.equal(phanHoi({id:'AQI',rawId:b,type:'public-key',response:{clientDataJSON:b,
    attestationObject:b}}).response.attestationObject,'AQI')
})
test('thời gian từ server và trước đăng ký', () => {
  assert.equal(hienPhien({thiet_bi:[],con_giay:0}), 'Chưa có passkey')
  assert.equal(hienPhien({thiet_bi:[{}],con_giay:3600}), 'Đã xác nhận, còn 60 phút')
})
test('hủy trước ceremony không gọi fetch/authenticator', async () => {
  datHoi(async () => false)
  await assert.rejects(nghiLe('phien', {}, {goi: () => assert.fail('không gọi mạng')}), /huỷ/)
})
test('ceremony dùng API có sẵn, không tự ghi nghiệp vụ', async () => {
  datHoi(async () => true)
  const calls = []
  const b = new Uint8Array([1, 2]).buffer
  const goi = async (p, body) => {
    calls.push([p,body]); return calls.length === 1 ? {id:'hoi',publicKey:{challenge:'AQI'}} : {han:100}
  }
  const credentials = {get: async o => {
    assert.ok(o.publicKey.challenge instanceof ArrayBuffer)
    return {id:'AQI',rawId:b,type:'public-key',response:{clientDataJSON:b,signature:b,authenticatorData:b}}
  }}
  assert.deepEqual(await nghiLe('phien',{}, {goi,credentials}),{han:100})
  assert.equal(calls.length,2)
})
