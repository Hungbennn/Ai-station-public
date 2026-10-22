import test from 'node:test'
import assert from 'node:assert/strict'
import { datHoi, nghiLe } from '../src/passkey.js'
import { tenTrang, MENU } from '../src/menu.js'

test('N1: tiêu đề Thiết bị giữ menu chín mục', () => {
  assert.equal(tenTrang('/tai-khoan/thiet-bi'), 'Thiết bị')
  assert.equal(MENU.length, 9)
})
test('Q6: modal chỉ nhận mô tả đích, huỷ không chạy ceremony', async () => {
  const seen = []
  datHoi(async q => { seen.push(q); return false })
  for (const id of ['usb-a', 'usb-b']) {
    await assert.rejects(nghiLe('r', {
      duong: '/api/passkey/thu-hoi', than: {id, ma_thao_tac:'secret-marker'},
      hienThi: {hanhDong:'Thu hồi thiết bị', dich:id},
    }), /huỷ/)
  }
  assert.deepEqual(seen.map(q => q.hienThi.dich), ['usb-a', 'usb-b'])
  assert.ok(!JSON.stringify(seen).includes('secret-marker'))
})

test('Q6: P hết phiên hiển thị đúng hai đích, huỷ không gửi lại', async () => {
  const { ghi } = await import('../src/api.js')
  const old = globalThis.fetch, sent = [], seen = []
  globalThis.fetch = async (path, args) => {
    sent.push([path,JSON.parse(args.body)])
    return {ok:false,status:403,json:async()=>({detail:'Cần phiên passkey'})}
  }
  datHoi(async q => { seen.push(q); return false })
  try {
    for (const id of ['hr-1','hr-2']) {
      await assert.rejects(ghi('/api/phe-duyet/hr/'+id+'/duyet', {ma_thao_tac:id}), /huỷ/)
    }
    assert.deepEqual(seen.map(q=>q.hienThi.dich), ['phe-duyet / hr / hr-1','phe-duyet / hr / hr-2'])
    assert.ok(seen.every(q=>q.hienThi.hanhDong === 'Duyệt việc'))
    assert.equal(sent.length,2)
  } finally { globalThis.fetch = old }
})
