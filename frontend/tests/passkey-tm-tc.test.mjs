import test from 'node:test'
import assert from 'node:assert/strict'
import { ghi } from '../src/api.js'
import { datHoi } from '../src/passkey.js'
import { dungGhiTuDong } from '../src/thanh/tu_dong/ghi_tu_dong.js'

test('TM: xin P rồi R với đúng snapshot; retry mất phản hồi giữ UUID/quyền và đích', async () => {
  const oldFetch = globalThis.fetch, oldNav = Object.getOwnPropertyDescriptor(globalThis, 'navigator')
  const oldWindow = globalThis.window
  const bytes = new Uint8Array([1,2]).buffer, writes = [], ceremonies = [], seen = []
  datHoi(async yc => { seen.push(yc); return true })
  globalThis.window = { confirm: () => true }
  Object.defineProperty(globalThis, 'navigator', {configurable:true,value:{credentials:{
    get:async()=>({id:'AQI',rawId:bytes,type:'public-key',response:{clientDataJSON:bytes,signature:bytes}}),
  }}})
  let session = false, authorized = false, lost = false
  globalThis.fetch = async (path,args) => {
    const b = JSON.parse(args.body)
    let status = 200, out = {}
    if (path.endsWith('bat-dau')) { ceremonies.push(b); out={id:b.loai,publicKey:{challenge:'AQI'}} }
    else if (path.endsWith('ket-thuc')) {
      if(b.id==='phien') session = true
      else authorized = true
      out={quyen:'quyen-r'}
    } else {
      writes.push({path,body:b,quyen:args.headers['X-Tram-Xac-Nhan']})
      if(!session) { status=403;out={detail:'Cần phiên passkey'} }
      else if(!authorized || args.headers['X-Tram-Xac-Nhan']!=='quyen-r') {
        status=403;out={detail:'Cần chạm lại cho thao tác này'}
      } else if(!lost) {lost=true;throw new TypeError('Mất phản hồi')}
    }
    return {ok:status===200,status,json:async()=>out}
  }
  const cd = {tu_merge:false,tu_deploy:false,dieu_kien:{ci:true,cot:true,hang_rao:true},
    lenh:{deploy:'d.sh',kiem_song:'k.sh',lui:'l.sh'}}
  let ten='dự án A'
  const dl = {du_an:ten,cai_dat:cd,phien_ban:'4'}
  const g = dungGhiTuDong(()=>dl,async()=>{},()=>ten)
  try {
    assert.equal(await g.luu({tu_deploy:true},''),false)
    assert.equal(await g.luu({tu_deploy:true},''),true)
    assert.deepEqual(writes.at(-1),writes.at(-2))
    assert.deepEqual(ceremonies.map(x=>x.loai),['phien','r'])
    assert.equal(ceremonies[1].duong,writes.at(-1).path)
    assert.deepEqual(ceremonies[1].than,writes.at(-1).body)
    assert.ok(seen.every(x=>x.hienThi.dich.includes('dự án A')))
    assert.ok(seen.every(x=>x.hienThi.hanhDong === 'Bật tự deploy'))
    assert.ok(!JSON.stringify(seen).includes('ma_thao_tac'))
  } finally {
    globalThis.fetch=oldFetch;globalThis.window=oldWindow
    if(oldNav) Object.defineProperty(globalThis,'navigator',oldNav); else delete globalThis.navigator
    datHoi(async()=>false)
  }
})

test('TM: huỷ R và lỗi 403 nghiệp vụ không gửi lại ghi', async () => {
  const old = globalThis.fetch, sent=[]
  datHoi(async()=>false)
  globalThis.fetch=async(path,args)=>{
    sent.push(path)
    return {ok:false,status:403,json:async()=>({detail:'Cần chạm lại cho thao tác này'})}
  }
  try {
    await assert.rejects(ghi('/api/du-an/hr/tu-dong/cai-dat',{ma_thao_tac:'cancel-tm-001'}),/huỷ/)
    assert.equal(sent.length,1)
    globalThis.fetch=async()=>({ok:false,status:403,json:async()=>({detail:'Bị khoá nghiệp vụ'})})
    await assert.rejects(ghi('/api/du-an/hr/tu-cap-nhat',{ma_thao_tac:'tc-001'}),/Bị khoá/)
  } finally {globalThis.fetch=old;datHoi(async()=>false)}
})

test('TM: khoá cài đặt/Deploy/Tiếp tục trước đăng ký, giữ đường TẠM DỪNG', async () => {
  const { readFile } = await import('node:fs/promises')
  const page = await readFile(new URL('../src/trang/TuDong.vue',import.meta.url),'utf8')
  assert.match(page,/duocGhi/)
  assert.match(page,/:la-dai-ca="coQuyen"/)
  assert.match(page,/tamDung\.value && !coQuyen\.value/)
  const frame = await readFile(new URL('../src/KhungChinh.vue',import.meta.url),'utf8')
  assert.match(frame,/nut\.bat && !duocGhi/)
  const card = await readFile(new URL('../src/thanh/phe_duyet/TheSanSang.vue',import.meta.url),'utf8')
  assert.match(card,/duocGhi/)
})
