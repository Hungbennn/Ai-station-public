import assert from 'node:assert/strict'
import { test } from 'node:test'
import { kiemGoiChinh, quetHtml, quetJs, quetKhoiTinh, quetNgoai } from '../kiem-dist.mjs'

test('quetJs bắt eval, new Function, biên dịch WebAssembly', () => {
  assert.deepEqual(quetJs('const a = 1; retrieval(x); obj.evaluate()'), [])
  assert.deepEqual(quetJs('eval("1")'), ['eval('])
  assert.deepEqual(quetJs('const f = new Function("a", "return a")'), ['new Function'])
  assert.deepEqual(quetJs('await WebAssembly.instantiate(buf)'), ['WebAssembly.instantiate'])
})

test('quetHtml bắt script/style nội tuyến và thuộc tính sự kiện', () => {
  const sach = '<script type="module" crossorigin src="/assets/index-a.js"></script><link rel="stylesheet" href="/x.css">'
  assert.deepEqual(quetHtml(sach), [])
  assert.deepEqual(quetHtml('<script>alert(1)</script>'), ['<script> nội tuyến'])
  assert.deepEqual(quetHtml('<style>a{}</style><div style="color:red" onclick="x()">'),
    ['<style> nội tuyến', 'thuộc tính style', 'thuộc tính onclick'])
})

test('kiemGoiChinh: three không nằm trong gói chính', () => {
  assert.deepEqual(kiemGoiChinh('import("./VanPhong-x.js")'), [])
  assert.deepEqual(kiemGoiChinh('class WebGLRenderer {}'), ['three nằm trong gói chính — trang Văn phòng phải nạp lười'])
})

test('quetNgoai bắt font / CDN ngoài (CSP font-src, script-src chỉ self — lát 2f)', () => {
  assert.deepEqual(quetNgoai('url(./be-vietnam-pro-latin-400-normal-x.woff2)'), [])
  assert.deepEqual(quetNgoai('@import url(https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro)'),
    ['fonts.googleapis.com', 'url(http…) trong CSS'])
  assert.deepEqual(quetNgoai('import "https://cdn.jsdelivr.net/npm/three@0.160.0"; src: url(http://x.io/a.woff2)'),
    ['cdn.jsdelivr.net', 'url(http…) trong CSS'])
  assert.deepEqual(quetNgoai('src:url(data:font/woff2;base64,d09GMg) format("woff2")'),
    ['font nhúng data: (CSP font-src)'])
})

test('quetKhoiTinh bắt style= trong chuỗi khối tĩnh Vue gộp (CSP style-src chặn)', () => {
  assert.deepEqual(quetKhoiTinh('sa(`<li style="color:red;">x</li><li class="a">`,26)'),
    ['style= trong khối tĩnh'])
  assert.deepEqual(quetKhoiTinh('sa("<div class=\\"a\\" style=\\"b\\">",3)'), ['style= trong khối tĩnh'])
  assert.deepEqual(quetKhoiTinh('t.style=fe(n);el.style.transform=`translate(${x}px)`;e===`style`'), [])
})
