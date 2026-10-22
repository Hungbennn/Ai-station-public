// Dữ liệu GIẢ cho mockup — bám tests/chay_thu_van_phong.py. Không gọi API.
// hr-4 là bead thêm chỉ để minh hoạ nhãn "PR đã merge" (plan 2d G14).

export const DU_AN = [
  { ma: 'hr-codex', ten: 'hr-codex', tam_dong: false },
  { ma: 'tram', ten: 'tram', tam_dong: false },
  { ma: 'ke-toan', ten: 'ke-toan', tam_dong: true },
]

export const TEN_BUOC = { spec: 'spec', code: 'code', qc: 'QC' }

// hien_thi: cách Văn phòng vẽ (spec 2 §5.5). trang_thai: nhãn trên Đội ngũ AI.
export const KHE = [
  { id: 'claude-1', ten: 'Claude 1', cli: 'claude', may: 'B', tai_khoan: 'claude-chinh', vai: ['coder'],
    hien_thi: 'lam', trang_thai: 'lam', mau: '#c8623a', toc: '#3a2620',
    bead: { id: 'hr-1', du_an: 'hr-codex', tieu_de: 'Sửa cắt UTF-8 tóm tắt hoàn tiền', buoc: 'code' },
    han_muc: { gio5: 62, reset5: '23:40', tuan: 81, resetTuan: 'T2 07:00' }, nhip: '6 giây trước', phien: '1/2' },
  { id: 'claude-2', ten: 'Claude 2', cli: 'claude', may: 'B', tai_khoan: 'claude-phu', vai: ['coder', 'qc'],
    hien_thi: 'ranh', trang_thai: 'ranh', mau: '#d39a3c', toc: '#2b2b33',
    han_muc: { gio5: 94, reset5: '01:15', tuan: 70, resetTuan: 'T2 07:00' }, nhip: '4 giây trước', phien: '0/2' },
  { id: 'codex-1', ten: 'Codex 1', cli: 'codex', may: 'B', tai_khoan: 'codex-chinh', vai: ['qc'],
    hien_thi: 'can_nguoi', trang_thai: 'can_nguoi', mau: '#4f7a99', toc: '#1f2a33',
    bead: { id: 'hr-3', du_an: 'hr-codex', tieu_de: 'Chọn cách tính thuế', buoc: 'qc' },
    han_muc: { gio5: 48, reset5: '22:55', tuan: 57, resetTuan: 'CN 19:00' }, nhip: '9 giây trước', phien: '1/1' },
  { id: 'claude-3', ten: 'Claude 3', cli: 'claude', may: 'B', tai_khoan: 'claude-de-danh', vai: ['coder'],
    hien_thi: 'tat', trang_thai: 'tat', mau: '#5f8f5a', toc: '#33261d', vi_sao_tat: 'để dành',
    han_muc: { gio5: 100, reset5: '—', tuan: 92, resetTuan: 'T2 07:00' }, nhip: '11 giây trước', phien: '0/1' },
  { id: 'codex-2', ten: 'Codex 2', cli: 'codex', may: 'B', tai_khoan: 'codex-phu', vai: ['coder'],
    hien_thi: 'tat', trang_thai: 'mat_ket_noi', mau: '#6a5bb5', toc: '#1d1b2e',
    han_muc: null, nhip: 'chưa từng có', phien: '0/1' },
  { id: 'claude-4', ten: 'Claude 4', cli: 'claude', may: 'B', tai_khoan: 'claude-thu', vai: ['spec'],
    hien_thi: 'loi', trang_thai: 'cau_dao', mau: '#b8507a', toc: '#2a1f24',
    cau_dao: { ly_do: 'hết hạn mức', toi: '00:12 (còn 2 giờ)' },
    han_muc: { gio5: 0, reset5: '00:12', tuan: 34, resetTuan: 'T2 07:00' }, nhip: '5 giây trước', phien: '0/1' },
]

export const NHAN_TRANG_THAI = {
  lam: 'Đang làm', ranh: 'Rảnh', tat: 'Tắt', cau_dao: 'Cầu dao ngắt',
  can_nguoi: 'Cần Đại ca', mat_ket_noi: 'Mất kết nối',
}
export const NHAN_HIEN_THI = { lam: 'Làm', ranh: 'Rảnh', can_nguoi: 'Cần người', loi: 'Lỗi', tat: 'Tắt / mất kết nối' }

export const BEAD = [
  { id: 'hr-1', du_an: 'hr-codex', cot: 1, tieu_de: 'Sửa cắt UTF-8 tóm tắt hoàn tiền', loai: 'bug', uu_tien: 'P1',
    nhan: ['cot:ai-lam'], khe: 'claude-1', buoc: 'code',
    ly_do: 'Lỗi rõ, có test tái hiện; không đổi hành vi nghiệp vụ → AI tự làm.',
    mo_ta: 'Tóm tắt hoàn tiền cắt chuỗi theo byte nên vỡ chữ có dấu ở ký tự thứ 120.',
    nghiem_thu: ['Cắt theo ký tự, không theo byte', 'Có test với chuỗi tiếng Việt dài 200 ký tự'],
    dong_thoi_gian: [['21:58', 'cham_cot.ket_qua → cột 1'], ['22:01', 'giao.cap → claude-1 · code'], ['22:09', 'chay.bat_dau lượt 1']] },
  { id: 'hr-3', du_an: 'hr-codex', cot: 2, tieu_de: 'Chọn cách tính thuế', loai: 'task', uu_tien: 'P2',
    nhan: ['cot:can-chot'], khe: 'codex-1', buoc: 'qc',
    ly_do: 'Có hai cách tính hợp lệ, chọn sai ảnh hưởng số liệu kế toán → cần Đại ca chốt.',
    cau_hoi: ['Tính thuế trên giá trước hay sau chiết khấu?', 'Làm tròn theo từng dòng hay theo tổng hoá đơn?'],
    mo_ta: 'QC phát hiện hai đường tính cho kết quả lệch 1–3 đồng mỗi hoá đơn.',
    nghiem_thu: ['Một cách tính duy nhất, ghi trong ADR', 'Test so khớp 50 hoá đơn mẫu'],
    dong_thoi_gian: [['21:40', 'giao.cap → codex-1 · QC'], ['22:05', 'bao.can_hoi (escalation mở)']] },
  { id: 'hr-2', du_an: 'hr-codex', cot: 3, tieu_de: 'Xem lại hoá đơn', loai: 'task', uu_tien: 'P2',
    nhan: ['cot:cho-review'], pr: { so: 12, trang_thai: 'khong_xac_minh', ly_do: 'không phải merge commit (squash / rebase)' },
    ly_do: 'Đã code + QC qua; chờ Đại ca review để đóng.',
    mo_ta: 'Rà các trường hoá đơn sau khi đổi mẫu in.', nghiem_thu: ['Mẫu in mới khớp 3 hoá đơn thật đã che số'],
    dong_thoi_gian: [['20:12', 'qc.ket_qua qua'], ['20:14', 'bead.vao_cot_3'], ['21:30', 'pr.khong_xac_minh']] },
  { id: 'hr-4', du_an: 'hr-codex', cot: 3, tieu_de: 'Kiểm định dạng mã số thuế', loai: 'feature', uu_tien: 'P3',
    nhan: ['cot:cho-review'], minh_hoa: true, pr: { so: 11, trang_thai: 'da_merge' },
    ly_do: 'Đã code + QC qua; PR đã merge đúng commit đã kiểm.',
    mo_ta: 'Kiểm 10/13 chữ số và gạch nối.', nghiem_thu: ['Từ chối mã sai độ dài'],
    dong_thoi_gian: [['19:02', 'bead.vao_cot_3'], ['19:40', 'pr.da_merge']] },
]

export const NHAN_PR = { mo: 'PR đã mở', khong_xac_minh: 'PR không xác minh được', da_merge: 'PR đã merge' }

export const HE_CAN_XEM = [
  { tieu_de: 'Cầu dao khe claude-4 ngắt', chi_tiet: 'Lý do: hết hạn mức · tự đóng lúc 00:12', lien_ket: '#/doi-ngu', nhan_lk: 'Mở Đội ngũ AI' },
]

export const BANG_DIEM = [
  // khe, vai, so_phieu, xong, lan_chay_tb, qua [x, mau], tra_ve [x, mau]
  { khe: 'claude-1', vai: 'coder', so_phieu: 9, xong: 7, tb: 1.4, qua: [5, 7], tra: [1, 7] },
  { khe: 'claude-2', vai: 'coder', so_phieu: 6, xong: 6, tb: 1.2, qua: [5, 6], tra: [0, 6] },
  { khe: 'claude-2', vai: 'qc', so_phieu: 4, xong: 4, tb: 1.0, qua: null, tra: null },
  { khe: 'codex-1', vai: 'qc', so_phieu: 8, xong: 7, tb: 1.1, qua: null, tra: null },
  { khe: 'claude-3', vai: 'coder', so_phieu: 2, xong: 2, tb: 2.0, qua: [1, 2], tra: [1, 2] },
  { khe: 'codex-2', vai: 'coder', so_phieu: 0, xong: 0, tb: null, qua: [0, 0], tra: [0, 0] },
  { khe: 'claude-4', vai: 'spec', so_phieu: 3, xong: 2, tb: 1.5, qua: null, tra: null },
]

export const so_viec_cho = () => HE_CAN_XEM.length + BEAD.filter((b) => b.cot === 3).length +
  BEAD.filter((b) => b.cot === 2).length

// ---------- Tổng quan (D17) ----------
export const DICH_VU = [
  { ten: 'vn.tram.api', mo_ta: 'dashboard + API', cai: true, chay: true },
  { ten: 'vn.tram.quet', mo_ta: 'quét + chấm cột', cai: true, chay: true },
  { ten: 'vn.tram.nho', mo_ta: 'memory 127.0.0.1:7710', cai: true, chay: true },
  { ten: 'vn.tram.bao-tin', mo_ta: 'Telegram', cai: true, chay: true },
  { ten: 'vn.tram.sao-luu', mo_ta: 'sao lưu su-kien.db', cai: false, chay: false },
]
export const TRAM = { quet_cuoi: '22:14', quet_cach: '3 phút trước', estop: false, loi_nho: null, loi_gan_nhat: null }

export const VIEC_MOI_XONG = { 'hr-codex': { id: 'hr-5', tieu_de: 'Sửa định dạng ngày trên phiếu lương', luc: '18:40' } }

export const USAGE_HOM_NAY = {
  token_vao: '1,84 tr', token_ra: '212 n', usd_khe: 3.1, usd_api: 0.42, luot: 7,
  theo_khe: [['claude-1', 1.35], ['codex-1', 0.96], ['claude-2', 0.52], ['claude-4', 0.27]],
}

export const SU_KIEN = [
  ['22:14', 'quet.xong', '_tram', null, '3 dự án, 4 bead đổi'],
  ['22:12', 'chay.bat_dau', 'hr-codex', 'hr-1', 'claude-1 · lượt 2'],
  ['22:09', 'chay.xong', 'hr-codex', 'hr-1', 'claude-1 · lượt 1 · test đỏ'],
  ['22:05', 'bao.can_hoi', 'hr-codex', 'hr-3', 'codex-1 hỏi Đại ca (escalation)'],
  ['22:03', 'khe.cau_dao_ngat', '_tram', null, 'claude-4 · hết hạn mức'],
  ['22:01', 'giao.cap', 'hr-codex', 'hr-1', '→ claude-1 · code'],
  ['21:58', 'cham_cot.ket_qua', 'hr-codex', 'hr-1', '→ cột 1'],
  ['21:52', 'tho.mat_nhip', '_tram', null, 'codex-2 mất nhịp tim'],
  ['21:40', 'giao.cap', 'hr-codex', 'hr-3', '→ codex-1 · QC'],
  ['21:30', 'pr.khong_xac_minh', 'hr-codex', 'hr-2', 'PR #12 — không phải merge commit'],
  ['21:12', 'khe.tat', '_tram', null, 'claude-3 · Đại ca tắt (để dành)'],
  ['20:58', 'nho.ghi', 'hr-codex', 'hr-2', 'thêm 2 ký ức'],
  ['20:14', 'bead.vao_cot_3', 'hr-codex', 'hr-2', 'chờ review'],
  ['20:12', 'qc.ket_qua', 'hr-codex', 'hr-2', 'qua'],
  ['19:40', 'pr.da_merge', 'hr-codex', 'hr-4', 'PR #11 đúng commit đã kiểm'],
  ['19:02', 'bead.vao_cot_3', 'hr-codex', 'hr-4', 'chờ review'],
  ['18:40', 'bead.dong', 'hr-codex', 'hr-5', 'Đại ca Duyệt'],
  ['18:05', 'quet.loi', 'tram', null, 'bd timeout — đã tự hết ở lượt sau'],
]

// ---------- Cài đặt (D19) — chỉ đọc ----------
export const CAU_HINH_DU_AN = [
  { ten: 'hr-codex', duong_dan: '~/Developer/hr-codex', nhanh: 'main', gitnexus: 'hr-codex',
    lenh: ['uv run pytest -q', 'uv run ruff check .'],
    hang_rao: [['tien', 'hoàn tiền, thuế, hoá đơn'], ['schema', 'migrations/'], ['quyen', 'phân quyền, vai trò'], ['khach_thay', 'mẫu in, email khách']] },
  { ten: 'tram', duong_dan: '~/Developer/Ben Station', nhanh: 'main', gitnexus: 'ben-station',
    lenh: ['uv run pytest -q', 'npm --prefix frontend test'], hang_rao: [['quyen', 'CSP, danh tính, token'], ['schema', 'su_kien/*.sql']] },
  { ten: 'ke-toan', duong_dan: '~/Developer/ke-toan', nhanh: 'main', gitnexus: null, tam_dong: true,
    lenh: ['uv run pytest -q'], hang_rao: [['tien', 'sổ cái, bút toán']] },
]
export const TELEGRAM = {
  chat_id: 'có', gio_yen_lang: '23:00–07:00 (chỉ gửi "trạm lỗi")',
  loai: ['cột 3 mới', 'spec chờ duyệt', 'escalation bí', 'cờ đỏ', 'cầu dao khe', 'khe hết hạn mức', 'trạm lỗi', 'estop', 'PR đã merge', 'PR không xác minh được'],
}
export const CO = [
  ['giao_viec.bat', false, 'chỉ bật sau 3a-2, S6, S7'],
  ['github (gh, công bố)', false, 'chờ S7'],
  ['gitnexus', true, 'đọc đồ thị khi chấm cột'],
  ['memory (vn.tram.nho)', true, '1b-1 đang chạy'],
]
export const KEYCHAIN = [
  ['tram-telegram-bot-token', true], ['tram-anthropic-api-key', true], ['tram-nho-token', true], ['tram-noi-bo-token', false],
]
// trang_thai: dat (xanh) | thieu (đỏ) | cho (xám) — theo docs/handovers/2026-10-15-so-tay-chay-that.md
export const SAN_SANG = [
  ['bs-g28.9', 'Tailscale máy B đã đăng nhập', 'dat', ''],
  ['bs-8eh.17', 'Tailscale máy A (Đại ca cài, D6)', 'thieu', 'chặn dashboard từ A, N2, Task 0'],
  ['bs-urj.4', 'Kickstart vn.tram.nho sau ghép 1b-4 T4 (D11)', 'cho', 'trước khi cài vn.tram.api'],
  ['bs-6o0.11', '2a T26 — tailscale serve, Telegram, D1–D6', 'cho', 'cần bs-8eh.17 cho bước 7'],
  ['bs-8eh.1', '1b-2 T10 — /nho, mã Đại ca, tram-noi-bo-token', 'thieu', 'chưa có tram-noi-bo-token'],
  ['bs-g28.4', 'Task 0 — beads từ xa (Dolt qua Tailscale)', 'cho', 'cần bs-8eh.17'],
  ['bs-g28.5', 'T13 — bộ 20 bead mẫu HR Codex', 'cho', 'cần Task 0'],
  ['bs-g28.6', 'T14 — chấm thử (API < 5 USD)', 'cho', 'cần T13'],
  ['bs-g28.7', 'T15 — bật ghi HR Codex trên B', 'cho', 'cần T14 + Đại ca duyệt'],
  ['bs-hpc.5', '1b-1 memory: dịch vụ, Keychain, M1/M2, recall', 'dat', 'M4/M5 chờ sự kiện thật'],
  ['bs-8eh.3', 'S1 — hạn mức/stream (sơ bộ, user hiện tại)', 'cho', 'chưa duyệt chạy CLI thật'],
  ['bs-8eh.4', 'S6 — principal, user riêng mỗi khe', 'cho', 'chưa duyệt tạo user/sudoers'],
  ['bs-8eh.5', 'S7 — repo GitHub nháp, gh', 'cho', 'chưa duyệt'],
  ['bs-8eh.6', 'S5 — Codex, allowlist Q15', 'cho', 'chờ chốt Q15'],
  ['—', 'Ollama + bge-m3', 'dat', ''],
]
