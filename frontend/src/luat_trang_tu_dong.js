// Luật trang Tự động của một dự án `#/du-an/<ten>` (mockup 2026-10-18 trang-tu-dong.js, anh-tu-dong*.png; spec
// dieu-khien-tu-dong "Trang tự merge/deploy của dự án", "Bật công tắc cần xác nhận"; tu-deploy) — thuần. Khoá TM-2/TM-3
// (`cho_dai_ca`, `san_sang`, `dang_deploy`, `lich_su`, `dem_hong`) thiếu → "chưa có dữ liệu", không đoán.
import { gioPhut } from './dinh_dang.js'
import { CHU_CUA_TAM, lyDoKhoaGhi } from './luat_tu_dong.js'

export const DIEU_KIEN = [
  { ma: 'qc', ten: 'QC đạt', mo_ta: 'Một agent khác agent đã code kiểm và kết luận đạt', khoa: true },
  { ma: 'kiem_lai', ten: 'Kiểm lại đạt', mo_ta: 'Trạm tự chạy lại lệnh kiểm trong vùng cách ly', khoa: true },
  { ma: 'ci', ten: 'CI GitHub xanh', ngan: 'CI GitHub xanh',
    mo_ta: 'GitHub bắt kiểm đã chọn, nguồn tin cậy và nhánh cập nhật', khoa: true },
  { ma: 'cot', ten: 'Việc ở cột "AI tự làm"', ngan: 'Việc ở cột AI tự làm',
    mo_ta: 'Việc đi từ cột 1, Đại ca không tự gán cột' },
  { ma: 'hang_rao', ten: 'Không chạm hàng rào', ngan: 'Không chạm hàng rào',
    mo_ta: 'Tiền/giá · quyền/bảo mật · thứ khách thấy' },
]
export const LENH = [
  { ma: 'deploy', ten: 'Lệnh deploy', ngan: 'lệnh deploy', goi_y: 'đưa bản mới lên' },
  { ma: 'kiem_song', ten: 'Lệnh kiểm còn sống', ngan: 'lệnh kiểm còn sống', goi_y: 'xác nhận đúng bản và chức năng cốt lõi' },
  { ma: 'lui', ten: 'Lệnh lùi về bản trước', ngan: 'lệnh lùi', goi_y: 'chạy khi deploy hỏng' },
]
export const CHUA_CO = 'Chưa có dữ liệu — phần này của trạm chưa chạy.'
export const ma7 = (c) => (c ? String(c).slice(0, 7) : '—')
const dk = (ma) => DIEU_KIEN.find((d) => d.ma === ma)

// Hỏi lại trước khi gửi: bật tự merge/tự deploy, lưu ba lệnh (spec "Bật công tắc cần xác nhận"); tắt công tắc, tắt
// điều kiện, TẠM DỪNG — một lần bấm + xác nhận như estop. Bật lại điều kiện (chiều chặt hơn) không hỏi ('').
export function hoiCongTac(ma, bat, ten) {
  if (ma === 'tu_merge') {
    return bat ? `Bật tự merge cho ${ten}? Trạm sẽ tự gộp PR vào nhánh chính khi đủ mọi điều kiện, `
      + 'không chờ Đại ca.'
      : `Tắt tự merge của ${ten}? Việc xong sẽ chờ Đại ca merge như trước.`
  }
  if (ma === 'tu_deploy') {
    return bat ? 'Trạm sẽ tự đưa bản mới lên cho khách dùng, không chờ Đại ca. Bật?'
      : `Tắt tự deploy của ${ten}? Bản mới sẽ chờ ở "Sẵn sàng deploy" cho Đại ca bấm.`
  }
  return bat ? '' : `Tắt điều kiện "${dk(ma).ngan}"? Trạm sẽ tự merge cả việc không đạt điều kiện này.`
}
export const hoiTamDung = (ten) =>
  `Tạm dừng tự merge và tự deploy của ${ten}? Cài đặt giữ nguyên; bấm Tiếp tục để chạy lại.`
export const hoiDeploy = (ten, commit) => `Deploy bản ${ma7(commit)} của ${ten} lên cho khách dùng?\n`
   + 'Đại ca xác nhận phạm vi toàn bộ bản này, kể cả mã ngoài luồng. Trạm kiểm bản, deploy và lùi khi cần.'
export const hoiLuuLenh = (tatTuDeploy) => 'Lưu 3 lệnh? Dùng đường deploy đã cấp quyền riêng cho dự án.'
  + (tatTuDeploy ? '\nThiếu lệnh nên tự deploy sẽ tắt.' : '')

// Thân POST …/tu-dong/cai-dat luôn mang ĐỦ cài đặt (TM-1 `ThanCaiDat`): bản đang xem + phần đổi.
export const doiCongTac = (ma, bat) => (ma === 'tu_merge' || ma === 'tu_deploy' ? { [ma]: bat }
  : { dieu_kien: { [ma]: bat } })
export function doiLenh(cd, moi) {
  const lenh = Object.fromEntries(LENH.map((l) => [l.ma, String(moi[l.ma] ?? '').trim()]))
  return cd.tu_deploy && LENH.some((l) => !lenh[l.ma]) ? { lenh, tu_deploy: false } : { lenh }
}
export const thanCaiDat = (cd, doi) => ({ ...cd, ...doi, dieu_kien: { ...cd.dieu_kien, ...doi.dieu_kien },
  lenh: { ...cd.lenh, ...doi.lenh } })

// Khoá nút Deploy (mockup: estop → thiếu lệnh → cửa ghi). Tạm dừng KHÔNG khoá (D97: Deploy tay vẫn dùng được).
export function lyDoKhoaDeploy(dl, laDaiCa) {
  if (dl.estop) return 'Estop đang bật'
  if (!dl.du_lenh) return 'Chưa khai đủ 3 lệnh'
  if (dl.dang_deploy) return 'Đang có một lần deploy chạy'
  const k = lyDoKhoaGhi(dl, laDaiCa)
  return k === CHU_CUA_TAM ? 'Cửa ghi đang khoá' : k
}

// Khối "Sẵn sàng deploy": một hàng cho commit mới nhất (TM-3 gộp nhiều merge), hoặc hàng "đang deploy" (`cho`: Đại ca
// vừa bấm, pha deploy của trạm chưa nhận — TM-3 `dang_deploy.trang_thai`).
export function sanSang(dl, laDaiCa) {
  const phu = dl.cai_dat.tu_deploy ? 'tự deploy đang bật — trạm tự chạy sau mỗi lần merge'
    : 'tự deploy đang tắt — trạm chờ Đại ca bấm'
  if (dl.san_sang === undefined) return { phu, chuaCo: true }
  const ss = dl.san_sang
  const dd = dl.dang_deploy
  return { phu, lyDo: lyDoKhoaDeploy(dl, laDaiCa), rong: !ss && !dd ? 'Không có bản nào chờ deploy.' : '',
    ban: ss ? { commit: ma7(ss.commit), soMerge: ss.so_merge, bead: (ss.bead_ids || []).join(', '),
      luc: gioPhut(ss.luc), dangChay: ss.commit_dang_chay ? ma7(ss.commit_dang_chay) : '' } : null,
    dangDeploy: dd ? { commit: ma7(dd.commit), nguon: dd.nguon === 'dai_ca' ? 'Đại ca bấm' : 'tự deploy',
      luc: gioPhut(dd.luc), cho: dd.trang_thai === 'cho' } : null }
}

// "Chờ Đại ca" (TM-2 `cho_dai_ca`: {bead_id, tieu_de, luc, ly_do: [{ma, nhan, muc}]}): lý do là câu của máy chủ;
// màu theo `muc` của máy chủ (`tu_merge_xet.MUC`) — loi đỏ (luôn chờ: cấu trúc DB, không đọc được diff, tự merge
// lỗi), tat xám (CI đang chạy), còn lại "cần người". Thiếu khoá → null ("chưa có dữ liệu").
const LOP_MUC = { loi: 'tt-loi', tat: 'tt-tat' }
export function choDaiCa(dl) {
  if (!Array.isArray(dl.cho_dai_ca)) return null
  return dl.cho_dai_ca.map((c) => ({ bead: c.bead_id, tieuDe: c.tieu_de || '',
    lyDo: (c.ly_do || []).map((l) => ({ chu: l.nhan, lop: LOP_MUC[l.muc] ?? 'tt-can_nguoi' })) }))
}
