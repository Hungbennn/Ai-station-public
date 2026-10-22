import assert from 'node:assert/strict'
import { test } from 'node:test'
import { CANH_BAO_HAN_MUC, dinhDangSo, dinhDangUsd, khoaMuc, lyDoCauDao, moTaCuaSo, nhanTrangThai, nutKhe, tenNguon, tiLe }
  from '../src/luat_doi_ngu.js'
import { SO_NGAY_BANG_DIEM, duongDanDoiNgu, oTiLe } from '../src/luat_doi_ngu.js'

test('nhãn trạng thái: cầu dao ngắt thắng trạng thái suy', () => {
  assert.equal(nhanTrangThai({ trang_thai: 'lam', cau_dao: { ngat: false } }), 'Đang làm')
  assert.equal(nhanTrangThai({ trang_thai: 'loi', cau_dao: { ngat: true } }), 'Cầu dao ngắt')
  assert.equal(nhanTrangThai({ trang_thai: 'mat_ket_noi', cau_dao: { ngat: false } }), 'Mất kết nối')
  assert.equal(nhanTrangThai({ trang_thai: 'la', cau_dao: {} }), 'la')
})

test('mô tả cửa sổ hạn mức: còn lại, reset, chưa biết không phải 0%', () => {
  const s = moTaCuaSo({ loai: '5h', trang_thai: 'biet', phan_tram: 62, reset_luc: '2026-10-13T05:00:00Z',
    doc_luc: '2026-10-13T02:41:10Z' })
  assert.match(s, /^Cửa sổ 5 giờ: còn 38% \(đã dùng 62%\) · reset .*12:00.* · đọc lúc .*09:41/)
  assert.equal(moTaCuaSo({ loai: 'tuan', trang_thai: 'chua_biet', doc_luc: null }), 'Cửa sổ tuần: chưa biết')
  assert.match(moTaCuaSo({ loai: 'x:60m', trang_thai: 'chua_biet', doc_luc: '2026-10-13T01:00:00Z' }),
    /^x:60m: chưa biết \(số đo cũ, đọc lúc .*08:00/)
})

test('lý do cầu dao và cảnh báo hạn mức', () => {
  assert.equal(lyDoCauDao('het-han-muc'), 'hết hạn mức')
  assert.equal(lyDoCauDao('dai-ca'), 'dai-ca')
  assert.equal(lyDoCauDao(null), '')
  assert.equal(CANH_BAO_HAN_MUC.ngung[0], 'loi')
  assert.equal(CANH_BAO_HAN_MUC.ok, undefined)
})

test('nút khe theo trạng thái', () => {
  assert.deepEqual(nutKhe({ trang_thai: 'ranh', cau_dao: { ngat: false } }), { tat: true, bat: false, dongCauDao: false })
  assert.deepEqual(nutKhe({ trang_thai: 'tat', cau_dao: { ngat: true } }), { tat: false, bat: true, dongCauDao: true })
})

test('định dạng số, USD, nguồn, tỉ lệ', () => {
  assert.equal(dinhDangSo(1200), (1200).toLocaleString('vi-VN'))
  assert.equal(dinhDangSo(null), '—')
  assert.equal(dinhDangUsd(null), 'chưa có giá')
  assert.equal(dinhDangUsd(0.01234), '$0.0123')
  assert.equal(dinhDangUsd(12.5), '$12.50')
  assert.equal(tenNguon('cham-cot'), 'Bộ chấm cột (Claude API)')
  assert.equal(tenNguon('B/claude-1'), 'B/claude-1')
  assert.equal(tiLe(0.5), '50%')
  assert.equal(tiLe(null), '—')
})

test('ô tỉ lệ bảng điểm kèm (tử/mẫu) như mockup Đội ngũ AI; mẫu 0 không hiện 0% giả', () => {
  assert.equal(tiLe(0.7143, 7), '71% (5/7)')
  assert.equal(tiLe(0, 6), '0% (0/6)')
  assert.equal(tiLe(null, 0), 'chưa có')
  assert.equal(tiLe(null, null), '—')
  assert.deepEqual(oTiLe(0.5, 2), { chinh: '50%', phu: '(1/2)' })
  assert.deepEqual(oTiLe(null, 0), { chinh: 'chưa có', phu: '' })
  assert.deepEqual(oTiLe(1, undefined), { chinh: '100%', phu: '' })
})

test('khoá mục Phê duyệt không trùng giữa các mục hệ', () => {
  const a = khoaMuc({ loai: 'he', du_an: '_tram', bead_id: null, chi_tiet: { su_kien: 'khe.cau_dao_ngat', khe_id: 'B/a' } })
  const b = khoaMuc({ loai: 'he', du_an: '_tram', bead_id: null, chi_tiet: { su_kien: 'khe.cau_dao_ngat', khe_id: 'B/b' } })
  assert.notEqual(a, b)
  assert.equal(khoaMuc({ loai: 'cho-review', du_an: 'hr', bead_id: 'hr-1', chi_tiet: {} }), 'cho-review/hr/hr-1//')
})

test('đường dẫn bảng điểm: mặc định mọi dự án, 30 ngày; mã hoá tên dự án', () => {
  assert.deepEqual(SO_NGAY_BANG_DIEM, [7, 30, 92])
  assert.equal(duongDanDoiNgu('', 30), '/api/doi-ngu?du_an=&so_ngay=30')
  assert.equal(duongDanDoiNgu('hr-codex', 7), '/api/doi-ngu?du_an=hr-codex&so_ngay=7')
  assert.equal(duongDanDoiNgu('a&b', undefined), '/api/doi-ngu?du_an=a%26b&so_ngay=30')
})
