import assert from 'node:assert/strict'
import { test } from 'node:test'
import { LOP_SK, NHOM_SK, TEN_NGUON, TEN_SU_KIEN_NHO, locKyUc, moTaNguon, nhanPhamVi, nhomCua, tongPhamVi }
  from '../src/nho.js'

test('nhanPhamVi: bốn loại phạm vi ra nhãn + lớp chip', () => {
  assert.deepEqual(nhanPhamVi('/chung'), ['Chung', 'pv-chung'])
  assert.deepEqual(nhanPhamVi('/vai/coder'), ['Vai coder', 'pv-vai'])
  assert.deepEqual(nhanPhamVi('/du-an/hr-codex/nghiep-vu'), ['Nghiệp vụ', 'pv-nghiep-vu'])
  assert.deepEqual(nhanPhamVi('/du-an/tram/cach-lam'), ['Cách làm', 'pv-cach-lam'])
  assert.deepEqual(nhanPhamVi(undefined), ['Cách làm', 'pv-cach-lam'])
})

test('moTaNguon: nhãn tiếng Việt, vai, bead, thăng cấp cắt mã gốc', () => {
  assert.equal(TEN_NGUON.dai_ca_ghi, 'Đại ca ghi tay')
  assert.deepEqual(moTaNguon([{ loai: 'agent', du_an: 'hr-codex', bead_id: 'hr-2', vai: 'qc' }]),
    [{ thangCap: false, chu: 'agent ghi · vai qc', duAn: 'hr-codex', bead: 'hr-2', idGoc: '' }])
  assert.deepEqual(moTaNguon([{ loai: 'thang_cap', du_an: 'tram', id_goc: 'm-28b3663f97684988' }]),
    [{ thangCap: true, chu: '', duAn: 'tram', bead: '', idGoc: 'm-28b3663…' }])
  assert.deepEqual(moTaNguon([{ loai: 'la', du_an: 'hr' }]),
    [{ thangCap: false, chu: 'la', duAn: 'hr', bead: '', idGoc: '' }])
  assert.deepEqual(moTaNguon(null), [])
})

test('nhomCua + LOP_SK: nhóm lọc sự kiện, nho.bo_bi_mat vào nhóm lỗi', () => {
  assert.equal(nhomCua('nho.ghi'), 'ghi')
  assert.equal(nhomCua('nho.gop'), 'ghi')
  assert.equal(nhomCua('nho.xoa_cung'), 'xoa')
  assert.equal(nhomCua('nho.thang_cap'), 'thang_cap')
  assert.equal(nhomCua('nho.tu_choi'), 'tu_choi')
  assert.equal(nhomCua('nho.phuc_hoi'), 'loi')
  assert.equal(nhomCua('nho.bo_bi_mat'), 'loi')
  assert.equal(TEN_SU_KIEN_NHO['nho.bo_bi_mat'], 'Bỏ vì bí mật')
  assert.deepEqual(NHOM_SK.map(([m]) => m), ['', 'ghi', 'xoa', 'thang_cap', 'tu_choi', 'loi'])
  for (const [m] of NHOM_SK.slice(1)) assert.ok(LOP_SK[m], m)
})

test('locKyUc: tìm theo nội dung, nhãn, mã, phạm vi; không phân biệt hoa thường', () => {
  const ds = [
    { id: 'm-1', noi_dung: 'Chạy Ruff trước', pham_vi: '/du-an/hr/cach-lam', nhan: ['test'] },
    { id: 'm-2', noi_dung: 'Hoá đơn làm tròn', pham_vi: '/chung', nhan: ['hoa-don'] },
  ]
  assert.deepEqual(locKyUc(ds, '  ').map((k) => k.id), ['m-1', 'm-2'])
  assert.deepEqual(locKyUc(ds, 'ruff').map((k) => k.id), ['m-1'])
  assert.deepEqual(locKyUc(ds, 'HOA-DON').map((k) => k.id), ['m-2'])
  assert.deepEqual(locKyUc(ds, 'm-2').map((k) => k.id), ['m-2'])
  assert.deepEqual(locKyUc(ds, '/chung').map((k) => k.id), ['m-2'])
  assert.deepEqual(locKyUc(ds, 'khong-co'), [])
})

test('tongPhamVi cộng số ký ức mọi phạm vi (pill "Tất cả")', () => {
  assert.equal(tongPhamVi([{ pham_vi: '/chung', so: 1 }, { pham_vi: '/vai/qc', so: 3 }]), 4)
  assert.equal(tongPhamVi(undefined), 0)
})
