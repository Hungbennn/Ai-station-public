import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { test } from 'node:test'
import { CHU_CHI_QUET_THU } from '../src/luat.js'
import { TEN_PHE_DUYET, nhomPheDuyet } from '../src/luat.js'
import { chiTietHe, chipHe, chipNguoiHoi, duongDanTraLoi, khoaDeploy, khoaThaoTac, linkPrReview, moTaReview,
  nutDongReview, sanSangDeploy, tieuDeHe } from '../src/luat_phe_duyet.js'
import { CHU_CHI_DOC } from '../src/luat_tu_dong.js'

const LUC = '2026-10-15T17:12:00Z'   // 00:12 giờ VN
const CAU_DAO = {
  loai: 'he', du_an: '_tram', bead_id: null, tieu_de: 'Khe a/claude-4',
  chi_tiet: {
    su_kien: 'khe.cau_dao_ngat', luc: LUC, khe_id: 'a/claude-4', loi: 'Cầu dao ngắt — hết hạn mức',
  },
}
const QUET = {
  loai: 'he', du_an: 'hr', bead_id: null, tieu_de: '', chi_tiet: { su_kien: 'quet.loi', luc: LUC, loi: 'x' },
}
const PR = 'https://github.com/a/b/pull/12'

test('mục hệ: cầu dao có chip "cầu dao" + tiêu đề theo khe; sự kiện khác có chip tên dễ đọc', () => {
  assert.deepEqual(chipHe(CAU_DAO), { lop: 'tt-cau_dao', chu: 'cầu dao' })
  assert.equal(tieuDeHe(CAU_DAO), 'Cầu dao khe a/claude-4 ngắt')
  assert.deepEqual(chipHe(QUET), { lop: 'tt-can_nguoi', chu: 'lỗi quét' })
  assert.equal(tieuDeHe(QUET), 'Quét dự án lỗi')
  assert.equal(tieuDeHe({ ...QUET, tieu_de: 'Bead A', chi_tiet: { su_kien: 'cham_cot.bo_qua' } }), 'Bead A')
  const la = { ...QUET, chi_tiet: { su_kien: 'x.y' } }
  assert.deepEqual(chipHe(la), { lop: 'tt-can_nguoi', chu: 'x.y' })
  assert.equal(tieuDeHe(la), 'x.y')
  assert.equal(chiTietHe(CAU_DAO), '16/10 00:12 · Cầu dao ngắt — hết hạn mức')
  assert.equal(chiTietHe({ chi_tiet: {} }), '')
  assert.equal(chiTietHe({ chi_tiet: { ...CAU_DAO.chi_tiet, toi_luc: '2026-10-15T17:12:00Z' } }),
    'Lý do: hết hạn mức · tự đóng lúc 00:12')
})

test('mục bí: chip "<tên khe> hỏi · <bước>"; thiếu khe thì bỏ chip; link trả lời sang ngăn bên', () => {
  const m = { loai: 'escalation', du_an: 'hr-codex', bead_id: 'hr-3', chi_tiet: { khe_id: 'b/codex-1', buoc: 'qc' } }
  assert.equal(chipNguoiHoi(m), 'Codex 1 hỏi · QC')
  assert.equal(chipNguoiHoi({ ...m, chi_tiet: { khe_id: 'b/codex-1' } }), 'Codex 1 hỏi')
  assert.equal(chipNguoiHoi({ ...m, chi_tiet: {} }), '')
  assert.equal(chipNguoiHoi({ ...m, loai: 'decision' }), '')
  assert.deepEqual(duongDanTraLoi(m), { path: '/cong-viec', query: { du_an: 'hr-codex', bead: 'hr-3' } })
})

test('mục review: câu mô tả + nút đóng theo pr_tram; link PR an toàn', () => {
  const mo = { loai: 'cho-review', chi_tiet: { pr: null, pr_tram: { so: 12, url: PR, trang_thai: 'mo' } } }
  const merge = { loai: 'cho-review', chi_tiet: { pr_tram: { so: 11, url: PR, trang_thai: 'da_merge' } } }
  const cu = { loai: 'cho-review', chi_tiet: { pr: PR, pr_tram: null } }
  const khong = { loai: 'cho-review', chi_tiet: { pr: 'javascript:x', pr_tram: null } }
  assert.equal(moTaReview(mo), 'Đã code + QC qua; chờ Đại ca review để đóng.')
  assert.equal(moTaReview(merge), 'PR đã merge đúng commit đã kiểm.')
  assert.equal(nutDongReview(merge), 'tu-dong')
  assert.equal(nutDongReview(mo), 'da-merge')
  assert.equal(nutDongReview(cu), 'da-merge')
  assert.equal(nutDongReview(khong), '')
  assert.equal(nutDongReview({ ...mo, loai: 'co-do' }), '')
  assert.equal(moTaReview({ ...mo, loai: 'co-do' }), '')
  assert.equal(linkPrReview(mo), PR)
  assert.equal(linkPrReview(cu), PR)
  assert.equal(linkPrReview({ chi_tiet: { pr_tram: { url: 'https://evil.com/x' } } }), '')
})

test('khoá nút: không phải Đại ca khoá không chữ; dự án chỉ quét thử khoá + chữ D37', () => {
  assert.deepEqual(khoaThaoTac(true, false), { khoa: false, chu: '' })
  assert.deepEqual(khoaThaoTac(false, false), { khoa: true, chu: '' })
  assert.deepEqual(khoaThaoTac(true, true), { khoa: true, chu: CHU_CHI_QUET_THU })
  assert.deepEqual(khoaThaoTac(false, true), { khoa: true, chu: CHU_CHI_QUET_THU })
})

test('TM-4: dòng "sẵn sàng deploy" (D101) — nhóm cuối, một dòng mỗi dự án, dẫn sang trang Tự động', () => {
  const m = { loai: 'san-sang-deploy', du_an: 'repo-nhap', bead_id: null, tieu_de: '', uu_tien: null,
    updated_at: '2026-10-18T14:52:00Z', chi_tiet: { commit: 'a41c07e9d2b8', so_merge: 3 } }
  assert.equal(TEN_PHE_DUYET['san-sang-deploy'], 'Sẵn sàng deploy')
  assert.deepEqual(nhomPheDuyet([m, { loai: 'feature-xong', bead_id: 'f' }]).map(([l]) => l),
    ['feature-xong', 'san-sang-deploy'])
  assert.deepEqual(sanSangDeploy(m), { tieuDe: 'repo-nhap · sẵn sàng deploy',
    moTa: 'Bản a41c07e — gồm 3 việc đã merge · merge cuối 21:52', den: '/du-an/repo-nhap' })
  assert.deepEqual(sanSangDeploy({ ...m, du_an: 'a b', updated_at: null, chi_tiet: {} }),
    { tieuDe: 'a b · sẵn sàng deploy', moTa: '', den: '/du-an/a%20b' })
})

test('TM-4 D129: nút Deploy ở dòng "sẵn sàng deploy" — cùng khoá, hộp hỏi, thân như nút trang Tự động', () => {
  const da = { ten: 'repo-nhap', bat_ghi: true, du_lenh: true }
  const td = { estop: false, chi_tam_dung: false, tam_dung_tram: null, du_an: [da] }
  const m = { loai: 'san-sang-deploy', du_an: 'repo-nhap', chi_tiet: { commit: 'a41c07e9d2b8', so_merge: 3 } }
  assert.equal(khoaDeploy(m, td, true), '')
  assert.equal(khoaDeploy(m, { ...td, estop: true }, true), 'Estop đang bật')
  assert.equal(khoaDeploy(m, { ...td, chi_tam_dung: true }, true), 'Cửa ghi đang khoá')        // kênh header
  assert.equal(khoaDeploy(m, td, false), CHU_CHI_DOC)
  assert.equal(khoaDeploy(m, { ...td, du_an: [{ ...da, bat_ghi: false }] }, true), CHU_CHI_QUET_THU)
  assert.equal(khoaDeploy(m, { ...td, du_an: [{ ...da, du_lenh: false }] }, true), 'Chưa khai đủ 3 lệnh')
  assert.equal(khoaDeploy(m, { ...td, tam_dung_tram: { boi: 'x', luc: '', ly_do: '' } }, true), '')   // D97
  assert.equal(khoaDeploy(m, null, true), 'Chưa đọc được trạng thái tự động')
  assert.equal(khoaDeploy(m, null, false), CHU_CHI_DOC)
  assert.equal(khoaDeploy({ ...m, chi_tiet: {} }, td, true), 'Không có bản mới nào chờ deploy')
  // Thẻ dùng đúng hàm ghi của trang Tự động (hộp hỏi hoiDeploy, thân {ma_thao_tac, expected_version: "",
  // expected_commit}, 409/422 hiện câu máy chủ — test ở tu_dong_ghi.test.mjs) + link sang trang Tự động.
  const vue = readFileSync(new URL('../src/thanh/phe_duyet/TheSanSang.vue', import.meta.url), 'utf8')
  assert.match(vue, /dungGhiTuDong\(\(\) => props\.muc\.chi_tiet, /)
  assert.match(vue, /@click="g\.deploy\(muc\.chi_tiet\.commit\)"/)
  assert.match(vue, /khoaDeploy\(props\.muc, kho\.tuDong, laDaiCa\.value\)/)
  assert.match(vue, />Mở trang Tự động</)
})
