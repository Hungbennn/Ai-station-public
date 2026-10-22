import assert from 'node:assert/strict'
import { test } from 'node:test'
import { dungPhamVi, laSuKienNho, ngoaiDuAn, tachNhan, tomTatNguon } from '../src/nho.js'

test('dungPhamVi dựng đúng bốn dạng, sai tên thì null', () => {
  assert.equal(dungPhamVi('du-an-cach-lam', 'hr-codex'), '/du-an/hr-codex/cach-lam')
  assert.equal(dungPhamVi('du-an-nghiep-vu', 'hr-codex'), '/du-an/hr-codex/nghiep-vu')
  assert.equal(dungPhamVi('vai', '', 'coder'), '/vai/coder')
  assert.equal(dungPhamVi('chung'), '/chung')
  assert.equal(dungPhamVi('vai', '', 'Coder'), null)
  assert.equal(dungPhamVi('du-an-cach-lam', '../x'), null)
  assert.equal(dungPhamVi('du-an-cach-lam', ''), null)
  assert.equal(dungPhamVi('la', 'hr'), null)
})

test('ngoaiDuAn chỉ /vai/* và /chung', () => {
  assert.equal(ngoaiDuAn('/chung'), true)
  assert.equal(ngoaiDuAn('/vai/qc'), true)
  assert.equal(ngoaiDuAn('/du-an/hr/cach-lam'), false)
})

test('tachNhan bỏ rỗng, trùng, quá dài, tối đa 5', () => {
  assert.deepEqual(tachNhan(' test, git ,test,, '), ['test', 'git'])
  assert.deepEqual(tachNhan('a,b,c,d,e,f'), ['a', 'b', 'c', 'd', 'e'])
  assert.deepEqual(tachNhan('x'.repeat(31)), [])
  assert.deepEqual(tachNhan(null), [])
})

test('tomTatNguon và laSuKienNho', () => {
  assert.equal(tomTatNguon([{ loai: 'da_chot', du_an: 'hr', bead_id: 'hr-1' }, { loai: 'dai_ca_ghi' }]),
    'da_chot · hr/hr-1; dai_ca_ghi')
  assert.equal(tomTatNguon([{ loai: 'thang_cap', du_an: 'hr', id_goc: 'm-1' }]), 'thăng cấp từ hr (m-1)')
  assert.equal(tomTatNguon(undefined), '')
  assert.equal(laSuKienNho('nho.ghi'), true)
  assert.equal(laSuKienNho('cot.da_chot'), false)
  assert.equal(laSuKienNho(null), false)
})
