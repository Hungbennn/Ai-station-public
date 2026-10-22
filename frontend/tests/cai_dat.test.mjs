import assert from 'node:assert/strict'
import { test } from 'node:test'
import {
  LENH_CO, LENH_DICH_VU, LENH_KEYCHAIN, LENH_SAN_SANG, LENH_TELEGRAM, cauBatGhi, chuHangRao, demSanSang, ghepBatGhi,
  lenhDuAn, maSanSang, nhanChatId, nhanCo, nhanKeychain, nhanSanSang, oDaCai, oDangChay,
} from '../src/luat_cai_dat.js'

test('lệnh gợi ý: hằng chữ đúng mockup, không chèn uid thật', () => {
  assert.deepEqual(LENH_SAN_SANG.map((l) => l.lenh),
    ['uv run tram giao kiem', 'bd list --status open --label san-sang'])
  assert.equal(LENH_SAN_SANG[0].ghi_chu, 'xanh/vàng/đỏ, mã ≠ 0 nếu có đỏ')
  assert.equal(LENH_DICH_VU[2].lenh, 'launchctl kickstart -k gui/$(id -u)/vn.tram.<tên>')
  assert.equal(LENH_DICH_VU[1].ghi_chu, 'liệt kê thay đổi, Đại ca gõ dong-y')
  assert.equal(LENH_TELEGRAM[1].lenh, 'launchctl kickstart -k gui/$(id -u)/vn.tram.bao-tin')
  assert.equal(LENH_CO[0].ghi_chu, 'vd giao_viec.bat: true — chỉ sau mọi cổng')
  assert.deepEqual(LENH_KEYCHAIN.map((l) => l.ghi_chu), ['tạo tram-noi-bo-token', 'dán trong Terminal.app'])
  assert.equal(LENH_KEYCHAIN[1].lenh, 'security add-generic-password -U -s tram-telegram-bot-token -a tram -w')
})

test('lệnh dự án theo dự án đầu, không có thì <tên>; câu bật ghi D31', () => {
  const ds = [{ ten: 'hr-codex' }, { ten: 'tram' }]
  assert.deepEqual(lenhDuAn(ds), [
    { lenh: '$EDITOR du-an/hr-codex.yaml', ghi_chu: 'sửa khoá rồi chạy lệnh dưới' },
    { lenh: 'uv run tram du-an them <đường dẫn repo>', ghi_chu: '' },
  ])
  assert.equal(lenhDuAn([])[0].lenh, '$EDITOR du-an/<tên>.yaml')
  assert.equal(cauBatGhi(ds), 'sửa tay bat_ghi: true trong du-an/hr-codex.yaml')
  assert.equal(cauBatGhi(undefined), 'sửa tay bat_ghi: true trong du-an/<tên>.yaml')
})

test('sẵn sàng: nhãn + lớp, mã tự kiểm thành —, đếm từ dem hoặc đếm lại', () => {
  assert.deepEqual(nhanSanSang('dat'), { chu: 'Đạt', lop: 'tt-lam' })
  assert.deepEqual(nhanSanSang('thieu'), { chu: 'Thiếu', lop: 'tt-can_nguoi' })
  assert.deepEqual(nhanSanSang('cho'), { chu: 'Chưa tới lượt', lop: 'tt-tat' })
  assert.equal(maSanSang({ ma: 'bs-g28.9', nguon: 'bead' }), 'bs-g28.9')
  assert.equal(maSanSang({ ma: 'ollama', nguon: 'tu_kiem' }), '—')
  assert.deepEqual(demSanSang({ dem: { dat: 3, thieu: 2, cho: 10 } }), { dat: 3, thieu: 2, cho: 10 })
  const muc = [{ trang_thai: 'dat' }, { trang_thai: 'cho' }, { trang_thai: 'cho' }]
  assert.deepEqual(demSanSang({ muc }), { dat: 1, thieu: 0, cho: 2 })
  assert.deepEqual(demSanSang(null), { dat: 0, thieu: 0, cho: 0 })
})

test('dịch vụ: đã cài có/chưa, đang chạy chạy/—/không rõ', () => {
  assert.deepEqual(oDaCai({ da_cai: true }), { chu: 'có', lop: 'tt-lam' })
  assert.deepEqual(oDaCai({ da_cai: false }), { chu: 'chưa', lop: 'tt-tat' })
  assert.deepEqual(oDangChay({ dang_chay: true, kiem_duoc: true }), { chu: 'chạy', lop: 'tt-lam' })
  assert.deepEqual(oDangChay({ dang_chay: false, kiem_duoc: true }), { chu: '—', lop: 'tt-tat' })
  assert.deepEqual(oDangChay({ dang_chay: true, kiem_duoc: false }), { chu: 'không rõ', lop: 'tt-cau_dao' })
  assert.deepEqual(oDangChay({ dang_chay: null, kiem_duoc: true }), { chu: 'không rõ', lop: 'tt-cau_dao' })
})

test('keychain, cờ, chat_id: chỉ nhãn, không bao giờ giá trị bí mật', () => {
  assert.deepEqual(nhanKeychain('co'), { chu: '● có', lop: 'tt-lam' })
  assert.deepEqual(nhanKeychain('chua'), { chu: '○ chưa có', lop: 'tt-can_nguoi' })
  assert.deepEqual(nhanKeychain('khong_ro'), { chu: 'không kiểm được', lop: 'tt-cau_dao' })
  assert.deepEqual(nhanCo({ bat: true, gia_tri: null }), { chu: 'bật', lop: 'tt-lam', mono: false })
  assert.deepEqual(nhanCo({ bat: false, gia_tri: null }), { chu: 'tắt', lop: 'tt-tat', mono: false })
  assert.deepEqual(nhanCo({ bat: null, gia_tri: 'nhanh_rieng' }), { chu: 'nhanh_rieng', lop: '', mono: true })
  assert.deepEqual(nhanCo({ bat: null, gia_tri: null }), { chu: 'chưa chốt', lop: 'tt-cau_dao', mono: false })
  assert.deepEqual(nhanChatId(true), { chu: 'có', lop: 'tt-lam' })
  assert.deepEqual(nhanChatId(false), { chu: 'chưa có', lop: 'tt-can_nguoi' })
})

test('ghép bat_ghi từ /api/du-an: false → chỉ quét thử, thiếu → coi như bật ghi; hàng rào nối phẩy', () => {
  const caiDat = [{ ten: 'hr-codex' }, { ten: 'tram' }, { ten: 'moi' }]
  const duAn = [{ ten: 'hr-codex', bat_ghi: false }, { ten: 'tram', bat_ghi: true }]
  assert.deepEqual(ghepBatGhi(caiDat, duAn).map((d) => d.chi_quet_thu), [true, false, false])
  assert.deepEqual(ghepBatGhi(caiDat, null).map((d) => d.chi_quet_thu), [false, false, false])
  assert.deepEqual(ghepBatGhi(undefined, duAn), [])
  assert.equal(chuHangRao({ loai: 'tien', tu_khoa: ['hoàn tiền', 'thuế'], duong_dan: ['billing/'] }),
    'hoàn tiền, thuế, billing/')
  assert.equal(chuHangRao({ loai: 'schema', tu_khoa: [], duong_dan: [] }), '')
})
