import test from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { createSSRApp } from 'vue'
import { renderToString } from '@vue/server-renderer'
import { parse, compileScript } from '@vue/compiler-sfc'

// Chạy computed và template Vue thật; chỉ thay IO và component con bằng fixture.
async function render(source) {
  source = source.replace("const ds = ref([])", "const ds = ref([{loai:'decision',du_an:'hr',id:'hr-1'}])")
  source = source.replace(/import ([A-Za-z]+) from '[^']+\.vue'/g,
    "const $1 = { template: '<span>Thẻ phê duyệt</span>' }")
  source = source.replace(/import '[^']+\.css'\n/g, '')
  source = source.replace("import { kho, taiSoPheDuyet } from '../kho.js'",
    "const kho = {trangThai:{la_dai_ca:true,passkey:{thiet_bi:[{}]}}}; const taiSoPheDuyet = () => {}")
  const { descriptor } = parse(source)
  let code = compileScript(descriptor, {id:'runtime-test',inlineTemplate:true}).content
  code = code.replace(/from (['"])(.*?)\1/g, (all, q, name) => {
    const url = name.startsWith('.') ? new URL('../src/trang/' + name, import.meta.url).href : import.meta.resolve(name)
    return `from '${url}'`
  })
  const { default: component } = await import('data:text/javascript;base64,' + Buffer.from(code).toString('base64'))
  return renderToString(createSSRApp(component))
}
test('Q1: template danh sách không rỗng đánh giá khoaCua', async () => {
  const src = await readFile(new URL('../src/trang/PheDuyet.vue', import.meta.url),'utf8')
  await assert.rejects(render(src.replace("import { duocGhi } from '../quyen_passkey.js'",'')), /duocGhi/)
  assert.match(await render(src), /Thẻ phê duyệt/)
})
