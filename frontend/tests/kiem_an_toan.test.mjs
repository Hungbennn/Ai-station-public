import assert from 'node:assert/strict'
import { test } from 'node:test'
import { quetNguon } from '../kiem-an-toan.mjs'

test('kiem-an-toan: giữ luật cũ (chèn HTML thô)', () => {
  assert.deepEqual(quetNguon('a.vue', '<div v-html="x" />'), ['v-html'])
  assert.deepEqual(quetNguon('a.js', 'el.innerHTML = s'), ['innerHTML'])
  assert.deepEqual(quetNguon('a.js', 'const a = 1'), [])
})

test('kiem-an-toan: cấm style="…" tĩnh trong .vue, cho :style động (lát 2f)', () => {
  assert.deepEqual(quetNguon('a.vue', '<template><i class="a" style="width:3px" /></template>'), ['style="…" tĩnh'])
  assert.deepEqual(quetNguon('a.vue', '<template><i :style="{ width: w + \'%\' }" /></template>'), [])
  assert.deepEqual(quetNguon('a.js', "el.setAttribute('x', 'style=\"a\"')"), [])
})

test('kiem-an-toan: cấm URL ngoài trong mã nguồn, trừ GitHub', () => {
  assert.deepEqual(quetNguon('a.css', '@import url(https://fonts.googleapis.com/css2)'), ['URL ngoài'])
  assert.deepEqual(quetNguon('a.js', "import x from 'http://cdn.example/x.js'"), ['URL ngoài'])
  assert.deepEqual(quetNguon('a.js', "const m = 'https://github.com/o/r/pull/1'"), [])
  assert.deepEqual(quetNguon('OFL.txt', 'http://scripts.sil.org/OFL'), [])
})
