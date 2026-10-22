// Luật hiển thị trang Phê duyệt (mockup trang.js vePheDuyet + theReview, anh-phe-duyet.png; D36–D38) — thuần,
// test bằng node --test. Server dựng mọi chuỗi trong `chi_tiet`; ở đây chỉ chọn nhãn và ghép câu.
import { gioPhut, ngayGio } from './dinh_dang.js'
import { CHU_CHI_QUET_THU, laLinkAnToan } from './luat.js'
import { tenKhe } from './luat_han_muc.js'
import { lyDoKhoaDeploy } from './luat_trang_tu_dong.js'
import { lyDoKhoaGhi } from './luat_tu_dong.js'

// Sự kiện của mục "Hệ cần xem" (tram/suy/phe_duyet.py, phe_duyet_khe.py): [chữ chip, tiêu đề khi mục không gắn bead].
const SU_KIEN_HE = {
  'cham_cot.bo_qua': ['chấm cột bỏ qua', 'Chấm cột bỏ qua bead'],
  'quet.loi': ['lỗi quét', 'Quét dự án lỗi'],
  'nho.loi_llm': ['ký ức · LLM', 'Nạp ký ức đứng (LLM lỗi)'],
  'nho.loi_embedder': ['ký ức · embedder', 'Nạp ký ức đứng (embedder lỗi)'],
}
const TEN_BUOC = { spec: 'spec', code: 'code', qc: 'QC' }
const CAU_DAO = 'khe.cau_dao_ngat'
const ct = (m) => (m && m.chi_tiet) || {}

// Chip loại của mục hệ: cầu dao → `tt-cau_dao` "cầu dao" (mockup); sự kiện khác → `tt-can_nguoi` + tên dễ đọc.
export function chipHe(m) {
  const sk = ct(m).su_kien || ''
  if (sk === CAU_DAO) return { lop: 'tt-cau_dao', chu: 'cầu dao' }
  return { lop: 'tt-can_nguoi', chu: SU_KIEN_HE[sk] ? SU_KIEN_HE[sk][0] : sk }
}

export function tieuDeHe(m) {
  const c = ct(m)
  if (c.su_kien === CAU_DAO) return `Cầu dao khe ${c.khe_id} ngắt`
  if (m.tieu_de) return m.tieu_de
  return SU_KIEN_HE[c.su_kien] ? SU_KIEN_HE[c.su_kien][1] : c.su_kien || ''
}

// Dòng `.nho` dưới tiêu đề: giờ sự kiện · lỗi server gửi.
// Cầu dao (mockup "Lý do: hết hạn mức · tự đóng lúc 00:12"): lý do là phần sau " — " của câu hằng server
// (tram/suy/phe_duyet_khe.py `LY_DO`), giờ tự đóng lấy từ `toi_luc`. Mục hệ khác: giờ + câu lỗi.
export function chiTietHe(m) {
  const c = ct(m)
  if (c.su_kien === 'khe.cau_dao_ngat' && c.toi_luc) {
    const lyDo = String(c.loi || '').split(' — ').slice(1).join(' — ')
    return `Lý do: ${lyDo || '?'} · tự đóng lúc ${gioPhut(c.toi_luc)}`
  }
  return [ngayGio(c.luc), c.loi].filter(Boolean).join(' · ')
}

// Chip người hỏi của mục bí (mockup "Codex 1 hỏi · QC"): chỉ escalation có `khe_id` (T4); thiếu thì bỏ chip.
export function chipNguoiHoi(m) {
  const c = ct(m)
  if (m.loai !== 'escalation' || !c.khe_id) return ''
  const buoc = c.buoc ? ` · ${TEN_BUOC[c.buoc] ?? c.buoc}` : ''
  return `${tenKhe(c.khe_id)} hỏi${buoc}`
}

// "Trả lời" dẫn sang ngăn bên trang Công việc (mockup), nơi có ô trả lời.
export function duongDanTraLoi(m) {
  return { path: '/cong-viec', query: { du_an: m.du_an, bead: m.bead_id } }
}

// Link PR của mục review: PR trạm (2d) trước, rồi link PR trong khối bàn giao; chỉ link GitHub (N1).
export function linkPrReview(m) {
  const c = ct(m)
  if (c.pr_tram && laLinkAnToan(c.pr_tram.url)) return c.pr_tram.url
  return laLinkAnToan(c.pr) ? c.pr : ''
}

const daMerge = (m) => Boolean(ct(m).pr_tram) && ct(m).pr_tram.trang_thai === 'da_merge'

// Câu mô tả dưới tiêu đề (mockup theReview `b.ly_do`); mục cờ đỏ không có câu này.
export function moTaReview(m) {
  if (m.loai !== 'cho-review') return ''
  return daMerge(m) ? 'PR đã merge đúng commit đã kiểm.' : 'Đã code + QC qua; chờ Đại ca review để đóng.'
}

// Ô đóng của mục review (mockup theReview): 'tu-dong' = "trạm đã xác minh — sẽ tự đóng"; 'da-merge' = nút
// "Đã merge trên GitHub → đóng bead"; '' = không có gì. Cờ đỏ không có nút đóng.
export function nutDongReview(m) {
  if (m.loai !== 'cho-review') return ''
  if (daMerge(m)) return 'tu-dong'
  return linkPrReview(m) ? 'da-merge' : ''
}

// Khoá nút ghi: không phải Đại ca → khoá (như cũ); dự án `bat_ghi: false` → khoá + câu D37.
export function khoaThaoTac(laDaiCa, chiQuetThu) {
  return { khoa: !laDaiCa || Boolean(chiQuetThu), chu: chiQuetThu ? CHU_CHI_QUET_THU : '' }
}

// Dòng "sẵn sàng deploy" (spec tu-deploy "Hiện ở trang Phê duyệt", D101, D129): một dòng mỗi dự án, có nút Deploy và
// link sang trang Tự động. `chi_tiet` {commit, so_merge} do TM-3 dựng.
export function sanSangDeploy(m) {
  const c = ct(m)
  const moTa = c.commit ? [`Bản ${String(c.commit).slice(0, 7)} — gồm ${c.so_merge} việc đã merge`,
    m.updated_at ? `merge cuối ${gioPhut(m.updated_at)}` : ''].filter(Boolean).join(' · ') : ''
  return { tieuDe: `${m.du_an} · sẵn sàng deploy`, moTa, den: '/du-an/' + encodeURIComponent(m.du_an) }
}

// Khoá nút Deploy ở dòng đó (D129): cùng thứ tự với nút trang Tự động (`lyDoKhoaDeploy`: estop → thiếu lệnh → danh
// tính / cửa ghi `header` / chỉ quét thử), trạng thái lấy từ GET /api/tu-dong (`kho.tuDong`). Chưa đọc được → khoá.
export function khoaDeploy(m, td, laDaiCa) {
  const da = td && (td.du_an || []).find((x) => x.ten === m.du_an)
  if (!da) return lyDoKhoaGhi(null, laDaiCa)
  if (!ct(m).commit) return 'Không có bản mới nào chờ deploy'
  return lyDoKhoaDeploy({ estop: td.estop, chi_tam_dung: td.chi_tam_dung, bat_ghi: da.bat_ghi, du_lenh: da.du_lenh,
    dang_deploy: null }, laDaiCa)
}
