// Luật thuần trang Đội ngũ AI theo mockup (lát 2f F3): chip trạng thái, ô việc, chữ phiên / nhịp tim. Hàng bảng điểm
// (kể cả khe 0 phiếu) do API 2d trả sẵn (D41) — không có luật ghép hàng ở đây.
import assert from 'node:assert/strict'
import { test } from 'node:test'
import { chuNhipTim, chuPhien, lopTrangThai, oViec } from '../src/luat_the_khe.js'

const KHONG_NGAT = { ngat: false, ly_do: null, toi_luc: null }
const khe = (them) => ({ khe_id: 'B/claude-1', may: 'B', trang_thai: 'ranh', phieu: null, cau_dao: KHONG_NGAT,
  ...them })

test('lớp chip trạng thái: cầu dao ngắt thắng trạng thái suy', () => {
  assert.equal(lopTrangThai(khe({ trang_thai: 'lam' })), 'tt-lam')
  assert.equal(lopTrangThai(khe({ trang_thai: 'mat_ket_noi' })), 'tt-mat_ket_noi')
  assert.equal(lopTrangThai(khe({ trang_thai: 'loi', cau_dao: { ngat: true } })), 'tt-cau_dao')
  assert.equal(lopTrangThai({ trang_thai: 'tat' }), 'tt-tat')
})

test('ô việc: đang giữ phiếu đứng trước mọi trạng thái', () => {
  const phieu = { du_an: 'hr', bead_id: 'hr-1', buoc: 'qc', tieu_de: 'Chọn cách tính thuế' }
  assert.deepEqual(oViec(khe({ trang_thai: 'can_nguoi', phieu })),
    { loai: 'phieu', ma: 'hr-1', chu: 'Chọn cách tính thuế · QC' })
  assert.equal(oViec(khe({ phieu: { ...phieu, buoc: 'code' } })).chu, 'Chọn cách tính thuế · code')
  assert.deepEqual(oViec(khe({})), { loai: 'trong', ma: '', chu: 'Không giữ việc' })
})

test('ô việc: cầu dao ngắt, tắt, mất kết nối', () => {
  const bayGio = new Date('2026-10-15T15:12:00Z')
  const ngat = { ngat: true, ly_do: 'het-han-muc', toi_luc: '2026-10-15T17:12:00Z' }
  assert.deepEqual(oViec(khe({ trang_thai: 'loi', cau_dao: ngat }), bayGio),
    { loai: 'cau_dao', ma: '', chu: 'Cầu dao ngắt: hết hạn mức · tự đóng 00:12 (còn 2 giờ)' })
  assert.equal(oViec(khe({ cau_dao: { ...ngat, toi_luc: '2026-10-15T15:00:00Z' } }), bayGio).chu,
    'Cầu dao ngắt: hết hạn mức · tự đóng 22:00')
  assert.equal(oViec(khe({ cau_dao: { ngat: true, ly_do: 'loi-lien-tiep', toi_luc: null } }), bayGio).chu,
    'Cầu dao ngắt: lỗi không do agent liên tiếp')
  assert.deepEqual(oViec(khe({ trang_thai: 'tat', vi_sao_tat: 'để dành' })),
    { loai: 'tat', ma: '', chu: 'Đại ca tắt khe · “để dành”' })
  assert.equal(oViec(khe({ trang_thai: 'tat', vi_sao_tat: '  ' })).chu, 'Đại ca tắt khe')
  assert.equal(oViec(khe({ trang_thai: 'tat' })).chu, 'Đại ca tắt khe')
  assert.deepEqual(oViec(khe({ trang_thai: 'mat_ket_noi', may: 'C' })),
    { loai: 'mat_ket_noi', ma: '', chu: 'Không thấy nhịp tim từ máy C' })
})

test('chữ phiên (D38/Q11: không có số phiên tối đa) và nhịp tim cuối', () => {
  assert.equal(chuPhien(1), '1 phiên đang chạy')
  assert.equal(chuPhien(2), '2 phiên đang chạy')
  assert.equal(chuPhien(0), 'Không có phiên')
  assert.equal(chuPhien(undefined), 'Không có phiên')
  const bayGio = new Date('2026-10-15T15:12:06Z')
  assert.equal(chuNhipTim('2026-10-15T15:12:00Z', bayGio), '6 giây trước')
  assert.equal(chuNhipTim(null, bayGio), 'chưa từng có')
  assert.equal(chuNhipTim('2026-10-15T15:12:09Z', bayGio), 'vừa xong')
})
