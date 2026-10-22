// Dữ liệu GIẢ cho mockup tự merge + tự deploy (change openspec/changes/tu-merge-tu-deploy). Không gọi API.
// Ba tình huống của repo-nhap để Đại ca xem: binh-thuong, tu-tat (hỏng 3 lần liên tiếp), lui-hong.

export const DIEU_KIEN = [
  { ma: 'qc', ten: 'QC đạt', mo_ta: 'Một agent khác agent đã code kiểm và kết luận đạt', khoa: true },
  { ma: 'kiem_lai', ten: 'Kiểm lại đạt', mo_ta: 'Trạm tự chạy lại lệnh kiểm trong vùng cách ly', khoa: true },
  { ma: 'ci', ten: 'CI GitHub xanh', mo_ta: 'Mọi kiểm tra tự động trên GitHub đã chạy xong và đạt' },
  { ma: 'cot', ten: 'Việc ở cột "AI tự làm"', mo_ta: 'Việc đi từ cột 1, Đại ca không tự gán cột' },
  { ma: 'hang_rao', ten: 'Không chạm hàng rào', mo_ta: 'Tiền/giá · quyền/bảo mật · thứ khách thấy' },
]

export const LENH = [
  { ma: 'deploy', ten: 'Lệnh deploy', goi_y: 'đưa bản mới lên' },
  { ma: 'kiem_song', ten: 'Lệnh kiểm còn sống', goi_y: 'chạy sau deploy, thoát 0 = sống' },
  { ma: 'lui', ten: 'Lệnh lùi về bản trước', goi_y: 'chạy khi deploy hỏng' },
]

const LENH_REPO_NHAP = {
  deploy: '/Users/Shared/tram-deploy/repo-nhap/deploy.sh',
  kiem_song: '/Users/Shared/tram-deploy/repo-nhap/kiem-song.sh',
  lui: '/Users/Shared/tram-deploy/repo-nhap/lui.sh',
}

const CHO_DAI_CA = [
  { bead: 'rn-14', tieu_de: 'Sửa định dạng ngày ở trang danh sách', ly_do: [['CI chưa xanh', 'tt-can_nguoi']] },
  { bead: 'rn-15', tieu_de: 'Làm tròn tổng tiền hoá đơn', ly_do: [['Chạm hàng rào: tiền/giá', 'tt-can_nguoi'], ['Cờ đỏ', 'tt-can_nguoi']] },
  { bead: 'rn-16', tieu_de: 'Thêm cột ghi chú cho bảng khách', ly_do: [['Cấu trúc DB — luôn chờ Đại ca', 'tt-loi']] },
  { bead: 'rn-17', tieu_de: 'Đổi chữ nút Lưu', ly_do: [['CI đang chạy — xét lại vòng sau', 'tt-tat']] },
]

// loai → [nhãn, lớp chip]
export const LOAI_SU_KIEN = {
  tu_merge: ['Tự merge', 'pr-da_merge'],
  san_sang: ['Sẵn sàng deploy', 'pr-mo'],
  deploy_dat: ['Deploy xong', 'tt-lam'],
  deploy_lui: ['Hỏng · đã tự lùi', 'tt-cau_dao'],
  lui_hong: ['LÙI HỎNG', 'tt-loi'],
  tu_tat: ['Tự tắt tự deploy', 'tt-can_nguoi'],
  tam_dung: ['Tạm dừng', 'tt-tat'],
}

const LS_BINH_THUONG = [
  ['21:52', 'san_sang', '—', 'a41c07e', 'gồm 2 việc: rn-11, rn-12', 'Đại ca'],
  ['21:52', 'tu_merge', 'rn-12', 'a41c07e', 'PR #31 · đủ 5 điều kiện', 'trạm'],
  ['20:07', 'tu_merge', 'rn-11', '9be2d40', 'PR #30 · đủ 5 điều kiện', 'trạm'],
  ['16:30', 'deploy_lui', '—', '77f0a19', 'kiểm còn sống: mã thoát 22 · 34 giây → lùi về 5d3e8b2: đạt', 'Đại ca bấm'],
  ['15:58', 'tu_merge', 'rn-9', '77f0a19', 'PR #28', 'trạm'],
  ['11:20', 'deploy_dat', '—', '5d3e8b2', 'deploy 48 giây · kiểm còn sống 3 giây', 'Đại ca bấm'],
]

const LS_TU_TAT = [
  ['02:41', 'tu_tat', '—', 'c0d9e11', 'hỏng 3 lần liên tiếp — chờ Đại ca bật lại', 'trạm'],
  ['02:41', 'deploy_lui', '—', 'c0d9e11', 'deploy: mã thoát 1 · 12 giây → lùi về 5d3e8b2: đạt', 'tự deploy'],
  ['02:38', 'tu_merge', 'rn-13', 'c0d9e11', 'PR #32', 'trạm'],
  ['01:15', 'deploy_lui', '—', 'a41c07e', 'kiểm còn sống: quá hạn 2 phút → lùi về 5d3e8b2: đạt', 'tự deploy'],
  ['23:30', 'deploy_lui', '—', '9be2d40', 'deploy: quá hạn 15 phút → lùi về 5d3e8b2: đạt', 'tự deploy'],
  ['11:20', 'deploy_dat', '—', '5d3e8b2', 'deploy 48 giây · kiểm còn sống 3 giây', 'Đại ca bấm'],
]

const LS_LUI_HONG = [
  ['03:12', 'tam_dung', '—', '—', 'trạm tạm dừng dự án sau khi lùi hỏng', 'trạm'],
  ['03:12', 'lui_hong', '—', 'c0d9e11', 'lùi: mã thoát 0 · kiểm còn sống sau lùi: mã thoát 7', 'tự deploy'],
  ['03:10', 'tu_merge', 'rn-13', 'c0d9e11', 'PR #32', 'trạm'],
  ['11:20', 'deploy_dat', '—', '5d3e8b2', 'deploy 48 giây · kiểm còn sống 3 giây', 'Đại ca bấm'],
]

const LICH_SU_DOI = [
  ['18/10 09:12', 'Bật tự merge', 'tắt → bật'],
  ['18/10 09:05', 'Sửa lệnh kiểm còn sống', 'trống → …/kiem-song.sh'],
  ['18/10 09:04', 'Sửa lệnh deploy, lệnh lùi', 'trống → …/deploy.sh, …/lui.sh'],
  ['17/10 22:40', 'Tắt nút "Việc ở cột AI tự làm"', 'bật → tắt'],
  ['17/10 22:41', 'Bật lại nút "Việc ở cột AI tự làm"', 'tắt → bật'],
]

export const DU_AN = [
  { ma: 'repo-nhap', ten: 'repo-nhap', ghi_chu: 'repo nháp GitHub (cũng là repo của S7)', bat_ghi: true },
  { ma: 'hr-codex', ten: 'hr-codex', ghi_chu: 'ERP du lịch', bat_ghi: false },
  { ma: 'ke-toan', ten: 'ke-toan', ghi_chu: 'tạm đóng', bat_ghi: false, tam_dong: true },
]

// Trạng thái tự động của từng dự án theo tình huống.
export function trangThai(ma, tinhHuong) {
  if (ma !== 'repo-nhap') {
    return {
      tu_merge: false, tu_deploy: false, dieu_kien: { ci: true, cot: true, hang_rao: true },
      lenh: { deploy: '', kiem_song: '', lui: '' }, tam_dung: null, san_sang: null, dem_hong: 0,
      cho_dai_ca: [], lich_su: [], lich_su_doi: [], doi_cuoi: null,
      cap_nhat: { bat: false, tien_do: false, viec_moi: false, bi_chan: false },
    }
  }
  const chung = {
    tu_merge: true, dieu_kien: { ci: true, cot: true, hang_rao: true }, lenh: { ...LENH_REPO_NHAP },
    cho_dai_ca: CHO_DAI_CA, lich_su_doi: LICH_SU_DOI, doi_cuoi: ['Đại ca (dashboard)', '18/10 09:12'],
    cap_nhat: { bat: true, tien_do: true, viec_moi: true, bi_chan: true },     // D85: mặc định tắt; ở đây Đại ca đã bật
  }
  if (tinhHuong === 'tu-tat') {
    return { ...chung, tu_deploy: false, tu_tat: '02:41', tam_dung: null, dem_hong: 3, lich_su: LS_TU_TAT,
      san_sang: { commit: 'c0d9e11', so: 1, viec: 'rn-13', luc: '02:41' } }
  }
  if (tinhHuong === 'lui-hong') {
    return { ...chung, tu_deploy: false, tam_dung: { boi: 'trạm', luc: '03:12', ly_do: 'lùi hỏng' }, lui_hong: true,
      dem_hong: 1, lich_su: LS_LUI_HONG, san_sang: null }
  }
  return { ...chung, tu_deploy: false, tam_dung: null, dem_hong: 1, lich_su: LS_BINH_THUONG,
    san_sang: { commit: 'a41c07e', so: 2, viec: 'rn-11, rn-12', luc: '21:52' } }
}

// ---- Agent tự cập nhật việc (D81–D86, spec riêng của bs-2bd.5) ----
export const CAP_NHAT = [
  { ma: 'tien_do', ten: 'Ghi tiến độ', mo_ta: 'Agent ghi tiến độ vào đúng việc của phiếu mình; chỉ hiện trên dashboard' },
  { ma: 'viec_moi', ten: 'Tạo việc mới', mo_ta: 'Tối đa 5 việc mỗi phiếu, nhãn "do agent tạo", liên kết việc gốc; ghi sau khi QC + kiểm lại đạt; không tự giao — bộ chấm cột xếp như mọi việc' },
  { ma: 'bi_chan', ten: 'Báo bị chặn', mo_ta: 'Agent báo "bị chặn — cần Đại ca" kèm lý do; ghi ngay, báo Telegram' },
]

// Thẻ việc minh hoạ trên trang Công việc. tien_do: [giờ, khe, câu]; goc: việc gốc khi do agent tạo.
export const BEAD_CV = [
  { id: 'rn-21', cot: 1, loai: 'task', uu_tien: 'P2', tieu_de: 'Chuyển trang danh sách khách sang bảng phân trang',
    khe: ['Claude 1', '#c8623a', 'code'],
    tien_do: [['22:05', 'Claude 1', 'Đã đổi 3/5 màn, còn trang báo cáo và trang xuất file'],
      ['21:40', 'Claude 1', 'Đọc xong mã cũ, bắt đầu từ màn danh sách']] },
  { id: 'rn-25', cot: 1, loai: 'bug', uu_tien: 'P3', tieu_de: 'Nút "Trang sau" không tắt ở trang cuối', goc: 'rn-21',
    tao_luc: '22:31' },
  { id: 'rn-22', cot: 2, loai: 'task', uu_tien: 'P2', tieu_de: 'Hiện giá tour trên phiếu đặt chỗ',
    khe: ['Codex 1', '#4f7a99', 'code'],
    bi_chan: ['21:58', 'Có hai bảng giá tour khác nhau (bảng cũ và bảng 2026); không biết phiếu đặt chỗ phải lấy bảng nào.'],
    tien_do: [['21:50', 'Codex 1', 'Tìm thấy hai nguồn giá, dừng lại hỏi']] },
  { id: 'rn-24', cot: 2, loai: 'task', uu_tien: 'P2', tieu_de: 'Làm tròn tổng tiền khi xuất hoá đơn', goc: 'rn-21',
    tao_luc: '22:31', hang_rao: 'tiền/giá' },
  { id: 'rn-12', cot: 3, loai: 'task', uu_tien: 'P2', tieu_de: 'Thêm ô tìm theo số điện thoại',
    tien_do: [['20:44', 'Claude 2', 'Xong, đã chạy bộ test']] },
]
