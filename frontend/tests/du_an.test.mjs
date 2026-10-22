import assert from 'node:assert/strict'
import { test } from 'node:test'
import { theDuAn } from '../src/luat_du_an.js'

const goc = { ten: 'ben-web', quet_cuoi: '2026-10-15T15:14:00Z', loi_gan_nhat: null, loi_doc: '',
  so_bead: { 'ai-lam': 2, 'can-chot': 1, 'cho-review': 0, 'chua-cham': 3 } }

test('theDuAn dựng link, giờ quét, chip 1·2·3 và chip chưa chấm', () => {
  const t = theDuAn(goc)
  assert.equal(t.den, '/cong-viec?du_an=ben-web')
  assert.match(t.quet, /^quét cuối \d\d:\d\d$/)
  assert.deepEqual(t.chip.map((c) => c.chu), ['1 · 2', '2 · 1', '3 · 0'])
  assert.equal(t.chuaCham, 'Chưa chấm · 3')
  assert.equal(t.loiGanNhat, 'Lỗi gần nhất: không có')
  assert.equal(t.chiQuetThu, false)
})

test('theDuAn: chưa quét, hết chưa chấm, lỗi gần nhất + loi_doc, chỉ quét thử', () => {
  const t = theDuAn({ ten: 'a b', quet_cuoi: null, bat_ghi: false, loi_doc: 'không đọc được bead',
    loi_gan_nhat: { luc: '2026-10-15T15:20:00Z', loai: 'quet', loi: 'bd lỗi' }, so_bead: {} })
  assert.equal(t.den, '/cong-viec?du_an=a%20b')
  assert.equal(t.quet, 'chưa quét')
  assert.equal(t.chuaCham, '')
  assert.deepEqual(t.chip.map((c) => c.chu), ['1 · 0', '2 · 0', '3 · 0'])
  assert.match(t.loiGanNhat, /^Lỗi gần nhất: \d\d:\d\d · bd lỗi$/)
  assert.equal(t.loiDoc, 'không đọc được bead')
  assert.equal(t.chiQuetThu, true)
})

test('TM-4: thẻ dự án có link tên → Công việc, "Tự động →" → /du-an/<ten>, chip tự động và chip phụ', () => {
  const td = { estop: false, tam_dung_tram: null, du_an: [
    { ten: 'ben-web', bat_ghi: true, tu_merge: true, tu_deploy: false, du_lenh: true, tam_dung: null,
      san_sang: true, dem_hong: 3 }] }
  const t = theDuAn(goc, td)
  assert.equal(t.tuDongDen, '/du-an/ben-web')
  assert.deepEqual(t.chipTuDong.map((c) => c.chu), ['tự merge: bật', 'tự deploy: tắt'])
  assert.deepEqual(t.chipPhu, [{ chu: '1 sẵn sàng deploy', lop: 'pr-mo' },
    { chu: 'tự deploy đã tự tắt', lop: 'tt-can_nguoi' }])
  // Chưa đọc được /api/tu-dong hoặc dự án không có trong đó: chỉ còn chip "chỉ quét thử" từ /api/du-an (D37).
  assert.deepEqual(theDuAn(goc, null).chipTuDong, [])
  assert.deepEqual(theDuAn(goc, null).chipPhu, [])
  assert.deepEqual(theDuAn({ ...goc, bat_ghi: false }, null).chipTuDong.map((c) => c.chu), ['chỉ quét thử'])
  assert.equal(theDuAn({ ...goc, ten: 'a b' }, td).tuDongDen, '/du-an/a%20b')
  const khongKhoa = { ...td, du_an: [{ ...td.du_an[0], san_sang: false, dem_hong: 0 }] }
  assert.deepEqual(theDuAn(goc, khongKhoa).chipPhu, [])
})
