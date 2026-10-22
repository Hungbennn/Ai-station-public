import test from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { parse, compileScript } from '@vue/compiler-sfc'
import { createRenderer } from 'vue'
import { datHoi } from '../src/passkey.js'

test('V2-Q3: thu(k) hai lần sau mất phản hồi giữ UUID và R; đổi đích tạo mới', async () => {
  const source = await readFile(new URL('../src/trang/ThietBi.vue', import.meta.url), 'utf8')
  const { descriptor } = parse(source)
  let code = compileScript(descriptor, { id: 'thu-runtime' }).content
  code = code.replace(/from (['"])(.*?)\1/g, (all, q, name) =>
    `from '${name.startsWith('.') ? new URL('../src/trang/' + name, import.meta.url).href : import.meta.resolve(name)}'`)
  const { default: component } = await import('data:text/javascript;base64,' + Buffer.from(code).toString('base64'))
  const oldFetch = globalThis.fetch, oldNav = Object.getOwnPropertyDescriptor(globalThis, 'navigator')
  const b = new Uint8Array([1, 2]).buffer, writes = [], seen = []
  datHoi(async q => { seen.push(q); return true })
  Object.defineProperty(globalThis, 'navigator', { configurable: true, value: { credentials: {
    get: async () => ({id:'AQI',rawId:b,type:'public-key',response:{clientDataJSON:b,authenticatorData:b,signature:b}}),
  } } })
  globalThis.fetch = async (path, args) => {
    const body = args.body && JSON.parse(args.body)
    let result
    if (path.endsWith('trang-thai')) result = {con_giay:3600,thiet_bi:[{id:'a'},{id:'b'}]}
    else if (path.endsWith('bat-dau')) result = {id:'hoi',publicKey:{challenge:'AQI'}}
    else if (path.endsWith('ket-thuc')) result = {quyen:'q-' + seen.length}
    else if (path.endsWith('thu-hoi')) {
      writes.push(body)
      if (writes.length === 1) throw new TypeError('Mất phản hồi sau commit')
      result = {da_thu_hoi:true}
    } else assert.fail(path)
    return {ok:true,status:200,json:async()=>result}
  }
  let vm
  const setup = component.setup
  component.setup = (props, ctx) => { vm = setup(props, ctx); return vm }
  component.render = () => null
  const renderer = createRenderer({ createComment:()=>({}), insert:()=>{}, remove:()=>{}, parentNode:()=>null,
    nextSibling:()=>null })
  const app = renderer.createApp(component)
  try {
    app.mount({})
    await new Promise(resolve => setImmediate(resolve))
    await vm.thu({id:'a',ten:'Máy A'})
    await vm.thu({id:'a',ten:'Máy A'})
    assert.deepEqual(writes[0], writes[1])
    assert.equal(seen.filter(q=>q.loai==='r').length, 1)
    await vm.thu({id:'b',ten:'Máy B'})
    assert.notEqual(writes[2].than.ma_thao_tac, writes[0].than.ma_thao_tac)
    assert.equal(writes[2].than.id, 'b')
  } finally {
    app.unmount(); globalThis.fetch = oldFetch
    if (oldNav) Object.defineProperty(globalThis,'navigator',oldNav)
    else delete globalThis.navigator
    datHoi(async()=>false)
  }
})
