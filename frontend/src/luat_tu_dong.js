// Luật hiển thị chung của tự merge / tự deploy (change tu-merge-tu-deploy, mockup 2026-10-18, D78, D87, D101) —
// thuần, test bằng node --test. Trạng thái do máy chủ suy (GET /api/tu-dong, /api/du-an/<ten>/tu-dong); ở đây chỉ
// chọn chữ, màu và câu khoá. Khoá ở giao diện chỉ là tiện: máy chủ vẫn từ chối (403/422) dù nút bị mở.
import { CHU_CHI_QUET_THU } from './luat.js'

const TIEN_TO = ['tu_dong.', 'tu_merge.', 'deploy.', 'estop.']
export const CHU_CHI_DOC = 'Chỉ đọc: thiếu danh tính Đại ca'
export const CHU_CUA_TAM = 'Cửa ghi còn tạm — chỉ bấm được TẠM DỪNG'
const CHU_CHUA_DOC = 'Chưa đọc được trạng thái tự động'
const CHU_TIEP_TUC_TAM = 'Cửa ghi còn tạm — Tiếp tục cần cửa ghi unix-socket'
export const HOI_TAM_DUNG_TRAM =
  'Tạm dừng tự merge và tự deploy của MỌI dự án? Trạm vẫn giao việc, kiểm lại, QC, mở PR.'

// Sự kiện SSE (`su_kien`) làm trạng thái tự động đổi → tải lại thanh trên, trang Tự động, số đếm Phê duyệt.
export function laSuKienTuDong(loai) {
  return typeof loai === 'string' && TIEN_TO.some((t) => loai.startsWith(t))
}

// Mọi nút ghi trừ TẠM DỪNG (spec "Cửa ghi còn tạm…", "Dự án khoá ghi…", "Xem khi không phải Đại ca"): '' = mở.
export function lyDoKhoaGhi(dl, laDaiCa) {
  if (!laDaiCa) return CHU_CHI_DOC
  if (!dl) return CHU_CHUA_DOC
  if (dl.chi_tam_dung) return CHU_CUA_TAM
  return dl.bat_ghi === false ? CHU_CHI_QUET_THU : ''
}

// TẠM DỪNG: chỉ cần danh tính (kênh header vẫn nhận — D87; `bat_ghi: false` vẫn bấm được). Tiếp tục thì cần kênh thật.
export function lyDoKhoaTamDung(dl, laDaiCa, dangBat) {
  if (!laDaiCa) return CHU_CHI_DOC
  return dangBat && dl && dl.chi_tam_dung ? CHU_TIEP_TUC_TAM : ''
}

// Nút TẠM DỪNG toàn trạm trên thanh trên (mockup index.html `#nut-tam-dung-tram`, cạnh Estop, màu vàng, D101).
export function nutTamDungTram(td, laDaiCa) {
  const bat = Boolean(td && td.tam_dung_tram)
  const lyDo = td ? lyDoKhoaTamDung(td, laDaiCa, bat) : CHU_CHUA_DOC
  const title = lyDo || (bat ? 'Bấm để tiếp tục tự merge và tự deploy'
    : 'Tạm dừng tự merge và tự deploy của mọi dự án. Trạm vẫn giao việc, kiểm lại, QC, mở PR.')
  return { bat, chu: bat ? 'Đang tạm dừng tự động' : 'Tạm dừng tự động', khoa: Boolean(lyDo), lyDo, title }
}

// Chip tóm tắt một dự án (mockup trang-du-an.js `chipTuDong`; chip "agent cập nhật việc" thuộc plan TC, không vẽ).
// `da`: phần tử `du_an` của GET /api/tu-dong; `tram`: phần chung {estop, tam_dung_tram}.
export function chipTuDong(da, tram) {
  if (!da) return []
  const chip = (chu, lop = '', title = '') => ({ chu, lop, title })
  if (da.bat_ghi === false) return [chip('chỉ quét thử', '', CHU_CHI_QUET_THU)]
  if (tram && tram.estop) return [chip('estop đang bật', 'tt-loi')]
  if (tram && tram.tam_dung_tram) return [chip('tạm dừng toàn trạm', 'tt-cau_dao')]
  if (da.tam_dung) return [chip('tạm dừng', 'tt-cau_dao')]
  const cong = (ten, bat) => chip(`${ten}: ${bat ? 'bật' : 'tắt'}`, bat ? 'tt-lam' : 'tt-tat')
  return [cong('tự merge', da.tu_merge), cong('tự deploy', da.tu_deploy)]
}
