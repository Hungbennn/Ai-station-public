import assert from 'node:assert/strict'
import { test } from 'node:test'
import { duongVe } from '../src/bieu_tuong.js'
import { kho, moLuong, taiTuDong } from '../src/kho.js'
import { CHU_CHI_QUET_THU } from '../src/luat.js'
import { CHU_CHI_DOC, CHU_CUA_TAM, chipTuDong, laSuKienTuDong, lyDoKhoaGhi, lyDoKhoaTamDung, nutTamDungTram }
  from '../src/luat_tu_dong.js'
import { MENU, mucCua } from '../src/menu.js'

const TD = { tam_dung_tram: null, estop: false, kenh_ghi: 'unix-socket', chi_tam_dung: false, la_dai_ca: true }
const TAM = { boi: 'dai-ca/dashboard', luc: '2026-10-18T14:52:00Z', ly_do: '' }

test('sự kiện làm trạng thái tự động đổi: tu_dong.*, tu_merge.*, deploy.*, estop.*', () => {
  for (const l of ['tu_dong.cai_dat', 'tu_dong.tam_dung', 'tu_merge.xong', 'deploy.san_sang', 'estop.bat']) {
    assert.equal(laSuKienTuDong(l), true, l)
  }
  for (const l of ['quet.xong', 'pr.da_merge', 'tu_dongx', '', null, undefined]) assert.equal(laSuKienTuDong(l), false)
})

test('nút TẠM DỪNG toàn trạm: chữ theo trạng thái; khoá khi chưa đọc, không phải Đại ca, Tiếp tục qua header', () => {
  assert.deepEqual(nutTamDungTram(TD, true), { bat: false, chu: 'Tạm dừng tự động', khoa: false, lyDo: '',
    title: 'Tạm dừng tự merge và tự deploy của mọi dự án. Trạm vẫn giao việc, kiểm lại, QC, mở PR.' })
  const bat = nutTamDungTram({ ...TD, tam_dung_tram: TAM }, true)
  assert.equal(bat.bat, true)
  assert.equal(bat.chu, 'Đang tạm dừng tự động')
  assert.equal(bat.khoa, false)
  assert.equal(bat.title, 'Bấm để tiếp tục tự merge và tự deploy')
  assert.equal(nutTamDungTram(TD, false).lyDo, CHU_CHI_DOC)
  assert.equal(nutTamDungTram(null, true).khoa, true)
  assert.equal(nutTamDungTram(null, true).lyDo, 'Chưa đọc được trạng thái tự động')
  const header = { ...TD, chi_tam_dung: true }
  assert.equal(nutTamDungTram(header, true).khoa, false)                     // D87: TẠM DỪNG vẫn bấm được
  const tiepTuc = nutTamDungTram({ ...header, tam_dung_tram: TAM }, true)
  assert.equal(tiepTuc.khoa, true)
  assert.equal(tiepTuc.lyDo, 'Cửa ghi còn tạm — Tiếp tục cần cửa ghi unix-socket')
})

test('khoá nút ghi trừ TẠM DỪNG: danh tính → cửa ghi tạm → chỉ quét thử; TẠM DỪNG chỉ cần danh tính', () => {
  assert.equal(lyDoKhoaGhi({ ...TD, bat_ghi: true }, true), '')
  assert.equal(lyDoKhoaGhi({ ...TD, bat_ghi: true }, false), CHU_CHI_DOC)
  assert.equal(lyDoKhoaGhi({ ...TD, bat_ghi: false, chi_tam_dung: true }, true), CHU_CUA_TAM)
  assert.equal(lyDoKhoaGhi({ ...TD, bat_ghi: false }, true), CHU_CHI_QUET_THU)
  assert.equal(lyDoKhoaGhi(null, true), 'Chưa đọc được trạng thái tự động')
  assert.equal(CHU_CUA_TAM, 'Cửa ghi còn tạm — chỉ bấm được TẠM DỪNG')
  assert.equal(lyDoKhoaTamDung({ ...TD, bat_ghi: false, chi_tam_dung: true }, true, false), '')
  assert.equal(lyDoKhoaTamDung(TD, false, false), CHU_CHI_DOC)
  assert.equal(lyDoKhoaTamDung({ ...TD, chi_tam_dung: true }, true, true),
    'Cửa ghi còn tạm — Tiếp tục cần cửa ghi unix-socket')
})

test('chip tóm tắt của dự án theo mockup chipTuDong (không có chip agent cập nhật việc)', () => {
  const da = { ten: 'repo-nhap', bat_ghi: true, tu_merge: true, tu_deploy: false, du_lenh: true, tam_dung: null }
  assert.deepEqual(chipTuDong(da, TD), [{ chu: 'tự merge: bật', lop: 'tt-lam', title: '' },
    { chu: 'tự deploy: tắt', lop: 'tt-tat', title: '' }])
  assert.deepEqual(chipTuDong({ ...da, tam_dung: TAM }, TD), [{ chu: 'tạm dừng', lop: 'tt-cau_dao', title: '' }])
  assert.deepEqual(chipTuDong(da, { ...TD, tam_dung_tram: TAM }),
    [{ chu: 'tạm dừng toàn trạm', lop: 'tt-cau_dao', title: '' }])
  assert.deepEqual(chipTuDong(da, { ...TD, estop: true }), [{ chu: 'estop đang bật', lop: 'tt-loi', title: '' }])
  assert.deepEqual(chipTuDong({ ...da, bat_ghi: false }, { ...TD, estop: true }),
    [{ chu: 'chỉ quét thử', lop: '', title: CHU_CHI_QUET_THU }])
  assert.deepEqual(chipTuDong(null, TD), [])
})

test('đường /du-an/<ten> thuộc mục Dự án; có icon tạm dừng', () => {
  assert.equal(mucCua('/du-an/repo-nhap').ma, 'du-an')
  assert.equal(MENU.find((m) => m.ma === 'du-an').duong, '/du-an')
  assert.ok(duongVe('tam-dung').length === 2)
})

class NguonGia {
  constructor(url) { this.url = url; this.nghe = {} }
  addEventListener(ten, f) { this.nghe[ten] = f }
}
const xong = () => new Promise((r) => setImmediate(r))

test('SSE: sự kiện tự động → tải lại /api/tu-dong và số Phê duyệt, tăng phienBanTuDong; khác thì không', async () => {
  const goi = []
  globalThis.fetch = async (url) => { goi.push(url); return new Response(JSON.stringify({ ...TD, so: 1 })) }
  globalThis.EventSource = NguonGia
  const es = moLuong()
  const truoc = kho.phienBanTuDong
  const phienBanTruoc = kho.phienBan
  es.nghe.su_kien({ data: JSON.stringify({ id: 9, loai: 'quet.xong', du_an: 'a' }) })
  await xong()
  assert.deepEqual(goi, [])
  es.nghe.su_kien({ data: JSON.stringify({ id: 10, loai: 'tu_dong.tam_dung', du_an: '_tram' }) })
  await xong()
  assert.deepEqual(goi.sort(), ['/api/phe-duyet', '/api/tu-dong'])
  assert.equal(kho.phienBanTuDong, truoc + 1)
  assert.equal(kho.phienBan, phienBanTruoc + 1)       // Phê duyệt đang mở theo dõi phienBan, không chỉ số đếm
  assert.equal(kho.tuDong.chi_tam_dung, false)
  globalThis.fetch = async () => new Response('{}', { status: 500 })
  await taiTuDong()
  assert.equal(kho.tuDong, null)                       // đọc lỗi → khoá nút (nutTamDungTram(null) khoá)
})

test('tải /api/tu-dong dồn (SSE liên tiếp): phản hồi cũ về sau không ghi đè bản mới — Codex Q10', async () => {
  const tra = []
  globalThis.fetch = () => new Promise((r) => { tra.push(r) })
  const dau = taiTuDong()
  const sau = taiTuDong()
  tra[1](new Response(JSON.stringify({ ...TD, estop: true })))
  await sau
  tra[0](new Response(JSON.stringify({ ...TD, estop: false })))
  await dau
  assert.equal(kho.tuDong.estop, true)                 // nút Deploy ở Phê duyệt (D129) khoá theo bản mới nhất
})
