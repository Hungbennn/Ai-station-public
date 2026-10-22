import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { ghi } from '../src/api.js'
import { datHoi } from '../src/passkey.js'

test('ghi P chỉ xin xác nhận khi cửa phiên từ chối, huỷ không retry', async () => {
  const old = globalThis.fetch
  let calls = 0
  globalThis.fetch = async () => { calls++; return {ok:false,status:403,
    json: async () => ({detail:'Cần phiên passkey'})} }
  datHoi(async () => false)
  try { await assert.rejects(ghi('/api/chu/tiep-tuc',{ma_thao_tac:'m'}), /huỷ/); assert.equal(calls,1) }
  finally { globalThis.fetch = old }
})
test('thiết bị đi từ thẻ chủ và chip, không thêm menu chính', () => {
  const read = p => readFileSync(new URL('../src/'+p, import.meta.url),'utf8')
  assert.match(read('tuyen.js'), /tai-khoan\/thiet-bi/)
  assert.match(read('thanh/ThanhBen.vue'), /tai-khoan\/thiet-bi/)
  assert.match(read('thanh/ThanhTren.vue'), /ChipPasskey/)
  assert.match(read('KhungChinh.vue'), /HopPasskey/)
  assert.match(read('trang/ThietBi.vue'), /tram chu passkey khoi-phuc/)
  assert.match(read('trang/ThietBi.vue'), /length <= 1/)
})
