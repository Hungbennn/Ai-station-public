import assert from 'node:assert/strict'
import { test } from 'node:test'
import { demHong, doiCuoi, dongLichSu, dongLichSuDoi, tenTacNhan } from '../src/luat_lich_su_tu_dong.js'
import { gioTuTat } from '../src/luat_bao_tu_dong.js'

test('lịch sử gần đây: nhãn + màu theo loại như mockup, giờ VN, commit 7 ký tự, "Ai" bằng lời', () => {
  assert.deepEqual(dongLichSu({ luc: '2026-10-18T09:30:00Z', loai: 'deploy_lui', bead_id: null,
    commit: '77f0a19c3d', chi_tiet: 'kiểm còn sống: mã thoát 22 · 34 giây → lùi về 5d3e8b2: đạt', ai: 'dai_ca_bam' }),
  { gio: '16:30', nhan: 'Hỏng · đã tự lùi', lop: 'tt-cau_dao', bead: '—', commit: '77f0a19',
    chiTiet: 'kiểm còn sống: mã thoát 22 · 34 giây → lùi về 5d3e8b2: đạt', ai: 'Đại ca bấm' })
  const nhan = (loai) => { const d = dongLichSu({ luc: '', loai, ai: 'tram' }); return [d.nhan, d.lop, d.ai] }
  assert.deepEqual(nhan('tu_merge'), ['Tự merge', 'pr-da_merge', 'trạm'])
  assert.deepEqual(nhan('san_sang'), ['Sẵn sàng deploy', 'pr-mo', 'trạm'])
  assert.deepEqual(nhan('deploy_dat'), ['Deploy xong', 'tt-lam', 'trạm'])
  assert.deepEqual(nhan('lui_hong'), ['LÙI HỎNG', 'tt-loi', 'trạm'])
  assert.deepEqual(nhan('khong_ro'), ['Không rõ kết quả', 'tt-loi', 'trạm'])
  assert.deepEqual(nhan('tu_tat'), ['Tự tắt tự deploy', 'tt-can_nguoi', 'trạm'])
  assert.deepEqual(nhan('tam_dung'), ['Tạm dừng', 'tt-tat', 'trạm'])
  assert.deepEqual(nhan('huy'), ['Deploy bị huỷ', 'tt-tat', 'trạm'])   // TM-3 câu hỏi 5 (a): `deploy.huy` vào lịch sử
  assert.deepEqual(nhan('la'), ['la', '', 'trạm'])
  assert.equal(dongLichSu({ loai: 'deploy_dat', ai: 'tu_deploy' }).ai, 'tự deploy')
  assert.equal(dongLichSu({ loai: 'san_sang', ai: 'dai_ca' }).ai, 'Đại ca')
  assert.equal(dongLichSu({ loai: 'tu_merge', bead_id: 'rn-12', commit: null }).bead, 'rn-12')
})

test('bộ đếm hỏng liên tiếp: ba đèn, chữ "n / 3"; thiếu khoá → null', () => {
  assert.deepEqual(demHong(1), { den: ['thieu', 'cho', 'cho'], chu: '1 / 3' })
  assert.deepEqual(demHong(3), { den: ['thieu', 'thieu', 'thieu'], chu: '3 / 3' })
  assert.deepEqual(demHong(0), { den: ['cho', 'cho', 'cho'], chu: '0 / 3' })
  assert.equal(demHong(undefined), null)
})

test('lịch sử đổi cài đặt: ai, giờ, việc bằng lời, trước → sau (lệnh rút gọn, trống)', () => {
  assert.equal(tenTacNhan('dai-ca/dashboard'), 'Đại ca (dashboard)')
  assert.equal(tenTacNhan('tram/tu-deploy'), 'trạm')
  assert.equal(tenTacNhan('khac'), 'khac')
  assert.deepEqual(dongLichSuDoi({ luc: '2026-10-18T02:12:00Z', tac_nhan: 'dai-ca/dashboard',
    doi: [{ truong: 'tu_merge', truoc: false, sau: true }] }),
  { gio: '18/10 09:12', ai: 'Đại ca (dashboard)', viec: 'Bật tự merge', doi: 'tắt → bật' })
  assert.deepEqual(dongLichSuDoi({ luc: '2026-10-18T02:04:00Z', tac_nhan: 'dai-ca/dashboard', doi: [
    { truong: 'lenh_deploy', truoc: '', sau: '/Users/Shared/tram-deploy/repo-nhap/deploy.sh' },
    { truong: 'lenh_lui', truoc: '', sau: 'sh scripts/lui.sh' }] }),
  { gio: '18/10 09:04', ai: 'Đại ca (dashboard)', viec: 'Sửa lệnh deploy, lệnh lùi',
    doi: 'trống → …/deploy.sh, trống → …/lui.sh' })
  assert.deepEqual(dongLichSuDoi({ luc: '2026-10-17T15:40:00Z', tac_nhan: 'tram/tu-deploy', doi: [
    { truong: 'dk_cot', truoc: true, sau: false }, { truong: 'tu_deploy', truoc: true, sau: false }] }),
  { gio: '17/10 22:40', ai: 'trạm', viec: 'Tắt nút "Việc ở cột AI tự làm", Tắt tự deploy',
    doi: 'bật → tắt, bật → tắt' })
  const xoa = { luc: '', tac_nhan: 'x', doi: [{ truong: 'lenh_kiem_song', truoc: 'make kiem', sau: '' }] }
  assert.equal(dongLichSuDoi(xoa).doi, 'make kiem → trống')
})

test('đổi lần cuối và giờ trạm tự tắt tự deploy (dòng mới nhất do trạm tắt tu_deploy)', () => {
  const ds = [{ luc: '2026-10-18T19:41:00Z', tac_nhan: 'tram/tu-deploy', doi: [{ truong: 'tu_deploy', truoc: true,
    sau: false }] }, { luc: '2026-10-18T02:12:00Z', tac_nhan: 'dai-ca/dashboard', doi: [] }]
  assert.equal(doiCuoi(ds), 'Đổi lần cuối: trạm · 19/10 02:41')
  assert.equal(doiCuoi([]), 'Chưa từng đổi — đang dùng mặc định')
  assert.equal(doiCuoi(undefined), 'Chưa từng đổi — đang dùng mặc định')
  assert.equal(gioTuTat(ds), '02:41')
  assert.equal(gioTuTat(ds.slice(1)), '')
  assert.equal(gioTuTat(undefined), '')
})
