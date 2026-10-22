import assert from 'node:assert/strict'
import { test } from 'node:test'
import { CHU_CHI_QUET_THU } from '../src/luat.js'
import { CHU_CHI_DOC } from '../src/luat_tu_dong.js'
import { baoTuDong } from '../src/luat_bao_tu_dong.js'
import { DIEU_KIEN, LENH, choDaiCa, doiCongTac, doiLenh, hoiCongTac, hoiDeploy, hoiLuuLenh, hoiTamDung,
  lyDoKhoaDeploy, ma7, sanSang, thanCaiDat } from '../src/luat_trang_tu_dong.js'

const LENH_DU = { deploy: '/Users/Shared/tram-deploy/repo-nhap/deploy.sh',
  kiem_song: '/Users/Shared/tram-deploy/repo-nhap/kiem-song.sh', lui: '/Users/Shared/tram-deploy/repo-nhap/lui.sh' }
const CD = { tu_merge: true, tu_deploy: false, dieu_kien: { ci: true, cot: true, hang_rao: true }, lenh: LENH_DU }
// GET /api/du-an/repo-nhap/tu-dong: khoá TM-1 + khoá TM-2/TM-3 hứa thêm (cho_dai_ca, san_sang, dang_deploy, dem_hong).
const DL = { du_an: 'repo-nhap', bat_ghi: true, estop: false, chi_tam_dung: false, tam_dung_tram: null, tam_dung: null,
  cai_dat: CD, du_lenh: true, phien_ban: '41', lich_su_doi: [], dem_hong: 1, dang_deploy: null,
  san_sang: { commit: 'a41c07e9d2b8c0ffee', so_merge: 2, bead_ids: ['rn-11', 'rn-12'], luc: '2026-10-18T14:52:00Z',
    commit_dang_chay: '5d3e8b2aa' },
  // TM-2 (`tram/suy/tu_merge.py`): {bead_id, tieu_de, luc, ly_do: [{ma, nhan, muc}]}, muc ∈ loi | tat | can_nguoi.
  cho_dai_ca: [{ bead_id: 'rn-15', tieu_de: 'Làm tròn tổng tiền hoá đơn', luc: '2026-10-18T14:00:00Z',
    ly_do: [{ ma: 'hang_rao_tien', nhan: 'Chạm hàng rào: tiền/giá', muc: 'can_nguoi' },
      { ma: 'schema_duong_dan', nhan: 'Cấu trúc DB — luôn chờ Đại ca', muc: 'loi' },
      { ma: 'ci_dang_chay', nhan: 'CI đang chạy — xét lại vòng sau', muc: 'tat' },
      { ma: 'ma_moi', nhan: 'Mã lạ', muc: 'khac' }] }] }

test('hằng theo mockup: 5 điều kiện (2 luôn bật), 3 lệnh; mã commit 7 ký tự', () => {
  assert.deepEqual(DIEU_KIEN.map((d) => [d.ma, Boolean(d.khoa)]),
    [['qc', true], ['kiem_lai', true], ['ci', true], ['cot', false], ['hang_rao', false]])
  assert.equal(DIEU_KIEN[3].ten, 'Việc ở cột "AI tự làm"')
  assert.deepEqual(LENH.map((l) => l.ma), ['deploy', 'kiem_song', 'lui'])
  assert.equal(ma7('a41c07e9d2b8'), 'a41c07e')
  assert.equal(ma7(null), '—')
})

test('hỏi lại: bật tự merge/tự deploy, tắt công tắc, tắt điều kiện; bật lại điều kiện không hỏi', () => {
  assert.equal(hoiCongTac('tu_deploy', true, 'repo-nhap'),
    'Trạm sẽ tự đưa bản mới lên cho khách dùng, không chờ Đại ca. Bật?')
  assert.match(hoiCongTac('tu_merge', true, 'repo-nhap'), /^Bật tự merge cho repo-nhap\? Trạm sẽ tự gộp PR/)
  assert.match(hoiCongTac('tu_merge', false, 'repo-nhap'), /^Tắt tự merge của repo-nhap\?/)
  assert.match(hoiCongTac('tu_deploy', false, 'repo-nhap'), /^Tắt tự deploy của repo-nhap\?/)
  assert.equal(hoiCongTac('ci', false, 'repo-nhap'),
    'Tắt điều kiện "CI GitHub xanh"? Trạm sẽ tự merge cả việc không đạt điều kiện này.')
  assert.equal(hoiCongTac('ci', true, 'repo-nhap'), '')
  assert.equal(hoiTamDung('repo-nhap'),
    'Tạm dừng tự merge và tự deploy của repo-nhap? Cài đặt giữ nguyên; bấm Tiếp tục để chạy lại.')
  assert.equal(hoiDeploy('repo-nhap', 'a41c07e9d2'), 'Deploy bản a41c07e của repo-nhap lên cho khách dùng?\n'
    + 'Đại ca xác nhận phạm vi toàn bộ bản này, kể cả mã ngoài luồng. Trạm kiểm bản, deploy và lùi khi cần.')
  assert.equal(hoiLuuLenh(false), 'Lưu 3 lệnh? Dùng đường deploy đã cấp quyền riêng cho dự án.')
  assert.match(hoiLuuLenh(true), /\nThiếu lệnh nên tự deploy sẽ tắt\.$/)
})

test('thân POST cài đặt luôn đủ khoá: đổi một công tắc / điều kiện / ba lệnh trên bản đang xem', () => {
  assert.deepEqual(thanCaiDat(CD, doiCongTac('tu_deploy', true)), { ...CD, tu_deploy: true })
  assert.deepEqual(thanCaiDat(CD, doiCongTac('cot', false)),
    { ...CD, dieu_kien: { ci: true, cot: false, hang_rao: true } })
  const moi = { deploy: ' make deploy ', kiem_song: 'sh kiem.sh', lui: 'sh lui.sh' }
  assert.deepEqual(doiLenh(CD, moi), { lenh: { deploy: 'make deploy', kiem_song: 'sh kiem.sh', lui: 'sh lui.sh' } })
  const bat = { ...CD, tu_deploy: true }
  assert.deepEqual(doiLenh(bat, { ...moi, lui: '  ' }),
    { lenh: { deploy: 'make deploy', kiem_song: 'sh kiem.sh', lui: '' }, tu_deploy: false })   // thiếu lệnh → tắt
  assert.deepEqual(thanCaiDat(bat, doiLenh(bat, { ...moi, lui: '' })).tu_deploy, false)
})

test('khối báo: chỉ quét thử, cửa tạm, estop, tạm dừng (Đại ca / lùi hỏng / không rõ), trạm tự tắt', () => {
  assert.deepEqual(baoTuDong(DL), [])
  const qt = baoTuDong({ ...DL, bat_ghi: false })
  assert.equal(qt[0].tieuDe, 'Dự án đang chỉ quét thử')
  assert.deepEqual(qt[0].than.filter((p) => p[1]).map((p) => p[0]), ['bat_ghi: false', 'du-an/repo-nhap.yaml'])
  assert.equal(baoTuDong({ ...DL, chi_tam_dung: true })[0].tieuDe, 'Cửa ghi còn tạm — chỉ bấm được TẠM DỪNG')
  assert.deepEqual(baoTuDong({ ...DL, estop: true }).map((b) => [b.lop, b.tieuDe]), [['do', 'Estop đang bật']])
  const td = (boi, ly_do) => baoTuDong({ ...DL, tam_dung: { boi, luc: '2026-10-18T20:12:00Z', ly_do } })[0]
  const daiCa = td('dai-ca/dashboard', '')
  assert.deepEqual([daiCa.lop, daiCa.tieuDe, daiCa.nut], ['', 'Dự án đang tạm dừng', 'Tiếp tục'])
  assert.match(daiCa.than[0][0], /^Đại ca bấm lúc 03:12\. Trạm vẫn giao việc và mở PR/)
  const lui = td('tram/tu-deploy', 'lui-hong')
  assert.deepEqual([lui.lop, lui.tieuDe, lui.nut],
    ['do', 'LÙI HỎNG lúc 03:12 — trang của khách có thể đang chết', 'Tiếp tục dự án'])
  assert.deepEqual([td('tram/tu-deploy', 'khong-ro').lop, td('tram/tu-deploy', 'khong-ro').tieuDe],
    ['do', 'Deploy không rõ kết quả lúc 03:12 — cần Đại ca kiểm'])
  const tat = baoTuDong({ ...DL, dem_hong: 3, lich_su_doi: [
    { luc: '2026-10-18T19:41:00Z', tac_nhan: 'tram/tu-deploy',
      doi: [{ truong: 'tu_deploy', truoc: true, sau: false }] }] })
  assert.equal(tat[0].tieuDe, 'Trạm đã tự tắt tự deploy lúc 02:41')
  assert.equal(baoTuDong({ ...DL, dem_hong: 3 })[0].tieuDe, 'Trạm đã tự tắt tự deploy')
  assert.deepEqual(baoTuDong({ ...DL, dem_hong: 3, cai_dat: { ...CD, tu_deploy: true } }), [])
})

test('sẵn sàng deploy: một hàng cho commit mới nhất, khoá Deploy theo thứ tự estop → thiếu lệnh → khoá ghi', () => {
  const s = sanSang(DL, true)
  assert.equal(s.phu, 'tự deploy đang tắt — trạm chờ Đại ca bấm')
  assert.deepEqual(s.ban, { commit: 'a41c07e', soMerge: 2, bead: 'rn-11, rn-12', luc: '21:52', dangChay: '5d3e8b2' })
  assert.equal(s.lyDo, '')
  assert.equal(sanSang({ ...DL, cai_dat: { ...CD, tu_deploy: true } }, true).phu,
    'tự deploy đang bật — trạm tự chạy sau mỗi lần merge')
  assert.equal(sanSang({ ...DL, san_sang: null }, true).rong, 'Không có bản nào chờ deploy.')
  assert.equal(sanSang({ ...DL, san_sang: undefined }, true).chuaCo, true)
  // TM-3 (`tram/deploy/hien_thi.dang_deploy`): trang_thai "cho" = Đại ca vừa bấm, pha deploy chưa nhận; "chay".
  const dd = (trang_thai, nguon = 'dai_ca') => sanSang({ ...DL, san_sang: null,
    dang_deploy: { trang_thai, commit: 'a41c07e9', nguon, luc: '2026-10-18T15:20:00Z' } }, true).dangDeploy
  assert.deepEqual(dd('chay'), { commit: 'a41c07e', nguon: 'Đại ca bấm', luc: '22:20', cho: false })
  assert.deepEqual(dd('cho'), { commit: 'a41c07e', nguon: 'Đại ca bấm', luc: '22:20', cho: true })
  assert.equal(dd('chay', 'tu_dong').nguon, 'tự deploy')
  assert.equal(lyDoKhoaDeploy({ ...DL, estop: true, du_lenh: false }, false), 'Estop đang bật')
  assert.equal(lyDoKhoaDeploy({ ...DL, du_lenh: false }, false), 'Chưa khai đủ 3 lệnh')
  assert.equal(lyDoKhoaDeploy({ ...DL, chi_tam_dung: true }, true), 'Cửa ghi đang khoá')
  assert.equal(lyDoKhoaDeploy(DL, false), CHU_CHI_DOC)
  assert.equal(lyDoKhoaDeploy({ ...DL, bat_ghi: false }, true), CHU_CHI_QUET_THU)
  assert.equal(lyDoKhoaDeploy({ ...DL, tam_dung: { boi: 'x', luc: '', ly_do: '' } }, true), '')   // D97: vẫn bấm được
})

test('chờ Đại ca: câu của máy chủ, màu theo `muc` (loi đỏ, tat xám, còn lại cần người); thiếu khoá → null', () => {
  assert.deepEqual(choDaiCa(DL), [{ bead: 'rn-15', tieuDe: 'Làm tròn tổng tiền hoá đơn', lyDo: [
    { chu: 'Chạm hàng rào: tiền/giá', lop: 'tt-can_nguoi' }, { chu: 'Cấu trúc DB — luôn chờ Đại ca', lop: 'tt-loi' },
    { chu: 'CI đang chạy — xét lại vòng sau', lop: 'tt-tat' }, { chu: 'Mã lạ', lop: 'tt-can_nguoi' }] }])
  assert.equal(choDaiCa({ ...DL, cho_dai_ca: undefined }), null)
  assert.deepEqual(choDaiCa({ ...DL, cho_dai_ca: [] }), [])
})
