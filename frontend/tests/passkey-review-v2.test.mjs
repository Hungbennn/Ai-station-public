import test from 'node:test'
import assert from 'node:assert/strict'
import { ghi } from '../src/api.js'
import { datHoi, quanLy } from '../src/passkey.js'

test('V2-Q3: retry kết quả mời đã mất không bắt chạm R lần hai', async () => {
  const oldFetch = globalThis.fetch
  const oldNavigator = Object.getOwnPropertyDescriptor(globalThis, 'navigator')
  const b = new Uint8Array([1, 2]).buffer
  const seen = [], writes = []
  datHoi(async q => { seen.push(q); return true })
  Object.defineProperty(globalThis, 'navigator', { configurable: true, value: {
    credentials: { get: async () => ({ id: 'AQI', rawId: b, type: 'public-key',
      response: { clientDataJSON: b, authenticatorData: b, signature: b } }) },
  } })
  globalThis.fetch = async (path, args) => {
    const body = args.body ? JSON.parse(args.body) : null
    let result
    if (path.endsWith('/trang-thai')) result = {con_giay: 3600, thiet_bi: [{}]}
    else if (path.endsWith('/bat-dau')) result = {id: 'hoi', publicKey: {challenge: 'AQI'}}
    else if (path.endsWith('/ket-thuc')) result = {quyen: 'quyen-test'}
    else if (path.endsWith('/moi')) {
      writes.push(body)
      if (writes.length === 1) throw new TypeError('Mất phản hồi sau commit giả lập')
      result = {da_cap: true, ma: null}
    } else assert.fail('Tuyến ngoài kịch bản')
    return {ok: true, status: 200, json: async () => result}
  }
  try {
    const body = {ma_thao_tac: 'v2-moi-001'}
    const display = {hanhDong: 'Thêm thiết bị', dich: 'Tài khoản Đại ca'}
    await assert.rejects(quanLy('moi', body, display), /Mất phản hồi/)
    assert.deepEqual(await quanLy('moi', body, display), {da_cap: true, ma: null})
    assert.deepEqual(writes[0], writes[1])
    assert.equal(seen.filter(q => q.loai === 'r').length, 1)
  } finally {
    globalThis.fetch = oldFetch
    if (oldNavigator) Object.defineProperty(globalThis, 'navigator', oldNavigator)
    else delete globalThis.navigator
    datHoi(async () => false)
  }
})

test('V2-Q4: xoá ký ức hiển thị đúng ID, huỷ không gửi lại', async () => {
  const oldFetch = globalThis.fetch, seen = [], sent = []
  globalThis.fetch = async (path, args) => {
    sent.push(JSON.parse(args.body))
    return {ok: false, status: 403, json: async () => ({detail: 'Cần phiên passkey'})}
  }
  datHoi(async q => { seen.push(q); return false })
  try {
    for (const id of ['ky-uc-a', 'ky-uc-b']) {
      await assert.rejects(ghi('/api/nho/xoa', {
        id, ma_thao_tac: 'marker-private', expected_version: '',
      }), /huỷ/)
    }
    assert.deepEqual(seen.map(q => q.hienThi.dich), ['Ký ức ky-uc-a', 'Ký ức ky-uc-b'])
    assert.ok(seen.every(q => q.hienThi.hanhDong === 'Xoá ký ức'))
    assert.ok(!JSON.stringify(seen).includes('marker-private'))
    assert.equal(sent.length, 2)
  } finally {
    globalThis.fetch = oldFetch
    datHoi(async () => false)
  }
})

test('V2-Q3: quyền hết hạn mới xin lại; lỗi nghiệp vụ không hỏi R thêm', async () => {
  const { boQuanLy } = await import('../src/passkey.js')
  const oldFetch = globalThis.fetch, oldNav = Object.getOwnPropertyDescriptor(globalThis, 'navigator')
  const b = new Uint8Array([1,2]).buffer, seen = [], writes = []
  let round = 0
  datHoi(async q => {seen.push(q); return true})
  Object.defineProperty(globalThis,'navigator',{configurable:true,value:{credentials:{
    get:async()=>({id:'AQI',rawId:b,type:'public-key',response:{clientDataJSON:b,authenticatorData:b,signature:b}}),
  }}})
  globalThis.fetch = async(path,args) => {
    const body = args.body && JSON.parse(args.body)
    let result, status = 200
    if(path.endsWith('trang-thai')) result = {con_giay:round ? 0 : 300,thiet_bi:[{}]}
    else if(path.endsWith('bat-dau')) result = {id:'hoi',publicKey:{challenge:'AQI'}}
    else if(path.endsWith('ket-thuc')) result = {quyen:'q-' + seen.length}
    else if(path.endsWith('thu-hoi')) {
      writes.push(body); round++
      if(round===1) throw new TypeError('Mất mạng')
      if(round===2) { status=403; result={loi:'Cần phiên passkey'} }
      else if(round===3) result={da_thu_hoi:true}
      else { status=403; result={loi:'Không thể thu hồi passkey cuối cùng — khôi phục tại máy B'} }
    } else assert.fail(path)
    return {ok:status===200,status,json:async()=>result}
  }
  try {
    const body={id:'a',ma_thao_tac:'expiry-001'}, display={hanhDong:'Thu hồi',dich:'Máy A'}
    await assert.rejects(quanLy('thu-hoi',body,display),/Mất mạng/)
    assert.deepEqual(await quanLy('thu-hoi',body,display),{da_thu_hoi:true})
    assert.deepEqual(writes[0],writes[1])
    assert.deepEqual(writes[0].than,writes[2].than)
    assert.deepEqual(seen.map(q=>q.loai),['r','phien','r'])
    await assert.rejects(quanLy('thu-hoi',{id:'b',ma_thao_tac:'expiry-002'},display),/cuối cùng/)
    const count=seen.length
    await assert.rejects(quanLy('thu-hoi',{id:'b',ma_thao_tac:'expiry-002'},display),/cuối cùng/)
    assert.equal(seen.length,count)
  } finally {
    boQuanLy(); globalThis.fetch=oldFetch
    if(oldNav) Object.defineProperty(globalThis,'navigator',oldNav)
    else delete globalThis.navigator
    datHoi(async()=>false)
  }
})
