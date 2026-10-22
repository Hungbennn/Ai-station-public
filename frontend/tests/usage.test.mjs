import assert from 'node:assert/strict'
import { test } from 'node:test'
import {
  chieuCot, dayNgay, giaTriNgay, khoangNgay, moiNhatTruoc, nhanLuat, nguonUsage, oTong, tiTrong, tongUsage,
  trucBieuDo, hienMocNgay,
} from '../src/luat_usage.js'

const d = (khoa, vao, ra, lan, cp, thieu = 0) =>
  ({ khoa, token_vao: vao, token_ra: ra, token_cache_doc: 10, token_cache_ghi: 1, so_lan: lan, chi_phi_usd: cp,
    thieu_gia: thieu })

test('tổng các trường từ theo_ngay; chi phí null khi mọi dòng thiếu giá', () => {
  const t = tongUsage([d('2026-10-14', 100, 20, 3, 1.5), d('2026-10-15', 50, 5, 2, null, 2)])
  assert.deepEqual(t, { token_vao: 150, token_ra: 25, token_cache_doc: 20, token_cache_ghi: 2, so_lan: 5,
    thieu_gia: 2, chi_phi_usd: 1.5 })
  assert.equal(tongUsage([d('2026-10-15', 1, 1, 1, null, 1)]).chi_phi_usd, null)
  assert.equal(tongUsage([]).so_lan, 0)
  assert.equal(tongUsage(undefined).chi_phi_usd, null)
})

test('dãy ngày tu..den (qua tháng), khoảng ngày đầu trang, mốc nhãn trục', () => {
  assert.deepEqual(dayNgay('2026-09-29', '2026-10-02'), ['2026-09-29', '2026-09-30', '2026-10-01', '2026-10-02'])
  assert.deepEqual(dayNgay('2026-10-15', '2026-10-15'), ['2026-10-15'])
  assert.deepEqual(dayNgay('x', '2026-10-15'), [])
  assert.equal(khoangNgay('2026-10-02', '2026-10-15'), 'Từ 02/10 đến 15/10/2026')
  assert.equal([...Array(14).keys()].filter((i) => hienMocNgay(i, 14, false)).length, 7)
  assert.ok(hienMocNgay(13, 14, true))
  assert.ok(hienMocNgay(5, 7, false))
})

test('trần + nhãn trục theo bước mockup, chiều cao cột', () => {
  assert.deepEqual(trucBieuDo(7.3, 'chi_phi'), { tran: 8, nhan: ['$8', '$6', '$4', '$2', '$0'] })
  assert.deepEqual(trucBieuDo(0, 'chi_phi'), { tran: 4, nhan: ['$4', '$3', '$2', '$1', '$0'] })
  assert.deepEqual(trucBieuDo(5, 'chi_phi').nhan, ['$8', '$6', '$4', '$2', '$0'])
  assert.equal(trucBieuDo(1.8e6, 'token').tran, 2e6)
  assert.deepEqual(trucBieuDo(1.8e6, 'token').nhan, ['2,00 tr', '1,50 tr', '1,00 tr', '500 n', '0'])
  assert.equal(trucBieuDo(900, 'chi_phi').tran, 2000)          // vượt bảng bước mockup → tiếp chuỗi 1-2-5
  assert.deepEqual(trucBieuDo(0, 'token').nhan, ['400 n', '300 n', '200 n', '100 n', '0'])
  assert.equal(chieuCot(2, 8), 25)
  assert.equal(chieuCot(20, 8), 100)
  assert.equal(chieuCot(null, 8), 0)
  assert.equal(giaTriNgay(d('a', 100, 20, 1, 0.5), 'chi_phi'), 0.5)
  assert.equal(giaTriNgay(d('a', 100, 20, 1, null), 'chi_phi'), 0)
  assert.equal(giaTriNgay(d('a', 100, 20, 1, 0.5), 'token'), 120)
  assert.equal(giaTriNgay(undefined, 'token'), 0)
})

test('tỉ trọng theo chi phí (tối thiểu 2%), không có giá → theo token vào + ra', () => {
  assert.deepEqual(tiTrong([d('a', 0, 0, 1, 3), d('b', 0, 0, 1, 1), d('c', 0, 0, 1, null)]), [75, 25, 2])
  assert.deepEqual(tiTrong([d('a', 30, 10, 1, null), d('b', 50, 10, 1, null)]), [40, 60])
  assert.deepEqual(tiTrong([d('a', 0, 0, 1, null)]), [2])
})

test('tên nguồn, luật nhận việc, mới nhất trước', () => {
  assert.deepEqual(nguonUsage('cham-cot'), { ten: 'Bộ chấm cột (Claude API)', mono: false, mau: 'var(--xam)' })
  const k = nguonUsage('B/claude-1')
  assert.equal(k.ten, 'B/claude-1')
  assert.equal(k.mono, true)
  assert.match(k.mau, /^#[0-9a-f]{6}$/)
  assert.deepEqual(nhanLuat('ok'), { chu: 'Nhận việc', lop: 'tt-lam' })
  assert.deepEqual(nhanLuat('ngung'), { chu: 'Ngừng — chạm ngưỡng', lop: 'tt-can_nguoi' })
  assert.deepEqual(nhanLuat('chi_p0_p1'), { chu: 'Chỉ P0–P1 — tuần cao', lop: 'tt-cau_dao' })
  assert.deepEqual(nhanLuat('chua_biet'), { chu: 'Chưa biết — vẫn nhận việc', lop: 'tt-cau_dao' })
  assert.deepEqual(nhanLuat(undefined), nhanLuat('chua_biet'))
  assert.deepEqual(moiNhatTruoc([{ khoa: '2026-W40' }, { khoa: '2026-W42' }]).map((x) => x.khoa),
    ['2026-W42', '2026-W40'])
})

test('sáu ô số tổng: gọn + title đầy đủ, phụ lần gọi và chi phí', () => {
  const dl = { co_bang_gia: true, theo_ngay: [d('2026-10-15', 1840000, 212000, 188, 52.17, 3)],
    theo_nguon: [d('B/claude-1', 1, 1, 69, 47.66), d('cham-cot', 1, 1, 119, 4.51)] }
  const o = oTong(dl)
  assert.equal(o.length, 6)
  assert.deepEqual(o[0], { gt: '1,84 tr', ten: 'token vào', phu: '', tieuDe: (1840000).toLocaleString('vi-VN') })
  assert.equal(o[4].phu, '69 khe · 119 chấm cột')
  assert.equal(o[5].gt, '$52.17')
  assert.equal(o[5].phu, 'API thật $4.51 · 3 lần thiếu giá')
  const kg = oTong({ ...dl, co_bang_gia: false })
  assert.deepEqual([kg[5].gt, kg[5].phu], ['—', 'chưa có giá'])
  assert.equal(oTong({ co_bang_gia: true, theo_ngay: [], theo_nguon: [] })[4].phu, '0 khe · 0 chấm cột')
})
