import assert from 'node:assert/strict'
import { test } from 'node:test'
import { TEN_PHE_DUYET, nhomPheDuyet } from '../src/luat.js'
import { coTheDuyetSpec, lenhMayA, thanDuyet } from '../src/luat_spec.js'

const C = 'a'.repeat(40)
const D = `sha256:${'b'.repeat(64)}`
const SPEC = { loai: 'spec', du_an: 'hr-codex', bead_id: 'hr-f', chi_tiet: { commit: C, digest_bead: D } }

test('Duyệt spec gửi đúng commit + digest đang xem; mục khác không gửi gì thêm', () => {
  assert.deepEqual(thanDuyet(SPEC), { expected_commit: C, digest_bead: D })
  assert.deepEqual(thanDuyet({ loai: 'spec', chi_tiet: {} }), { expected_commit: null, digest_bead: null })
  assert.deepEqual(thanDuyet({ loai: 'cho-review', chi_tiet: { commit: C } }), {})
})

test('chỉ cho Duyệt spec khi có commit và digest hợp lệ', () => {
  assert.equal(coTheDuyetSpec(SPEC), true)
  assert.equal(coTheDuyetSpec({ ...SPEC, chi_tiet: { commit: null, digest_bead: D } }), false)
  assert.equal(coTheDuyetSpec({ ...SPEC, chi_tiet: { commit: C, digest_bead: 'sha256:x' } }), false)
})

test('lệnh máy A mang dự án, feature, commit, digest, link dashboard; dữ liệu lạ thì không có lệnh', () => {
  assert.equal(lenhMayA(SPEC, 'https://may-b.ts.net'),
    `/xem-spec-cho-duyet hr-codex hr-f ${C} ${D} https://may-b.ts.net/#/phe-duyet`)
  assert.equal(lenhMayA({ ...SPEC, bead_id: 'hr-f; rm -rf ~' }, 'https://x'), '')
  assert.equal(lenhMayA({ ...SPEC, chi_tiet: {} }, 'https://x'), '')
})

test('hàng "Feature xong, chờ đóng" đứng sau "Spec chờ duyệt"', () => {
  const n = nhomPheDuyet([{ loai: 'feature-xong', bead_id: 'f' }, { loai: 'spec', bead_id: 's' }])
  assert.deepEqual(n.map(([l]) => l), ['spec', 'feature-xong'])
  assert.equal(TEN_PHE_DUYET['feature-xong'], 'Feature xong, chờ đóng')
})
