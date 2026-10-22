// Trạng thái dùng chung giữa các trang; mọi trạng thái nghiệp vụ tính ở server (Q12).
import { reactive } from 'vue'
import { doc } from './api.js'
import { laSuKienTuDong } from './luat_tu_dong.js'
import { laSuKienNho } from './nho.js'

export const kho = reactive({ trangThai: null, soPheDuyet: 0, phienBan: 0, phienBanNho: 0, phienBanDoiNgu: 0, suKienCuoi: null,
  matKetNoi: false, loi: '', tuDong: null, phienBanTuDong: 0 })

let lanTaiTrangThai = 0
export async function taiTrangThai() {
  const lan = ++lanTaiTrangThai
  kho.trangThai = null                         // đang xác minh lại: khóa thao tác ghi
  try {
    const trangThai = await doc('/api/chu/trang-thai')
    if (lan !== lanTaiTrangThai) return         // phản hồi cũ không khôi phục quyền
    kho.trangThai = trangThai
    kho.loi = ''
  } catch (e) {
    if (lan !== lanTaiTrangThai) return
    kho.trangThai = null
    kho.loi = e.message
  }
}

export async function taiSoPheDuyet() {
  try {
    const r = await doc('/api/phe-duyet')
    kho.soPheDuyet = r.so
  } catch (e) {
    kho.loi = e.message
  }
}

// TM-4: GET /api/tu-dong — TẠM DỪNG toàn trạm, cửa ghi tạm (`chi_tam_dung`), tóm tắt từng dự án. Lỗi → null (khoá nút).
// Phản hồi của lần tải cũ về sau (SSE tải dồn) bị bỏ — như taiTrangThai (Codex Q10).
let lanTaiTuDong = 0
export async function taiTuDong() {
  const lan = ++lanTaiTuDong
  try {
    const td = await doc('/api/tu-dong')
    if (lan === lanTaiTuDong) kho.tuDong = td
  } catch {
    if (lan === lanTaiTuDong) kho.tuDong = null
  }
}

export function moLuong() {
  const es = new EventSource('/api/luong')
  const doi = () => { kho.phienBan += 1 }
  es.addEventListener('cong_viec_doi', doi)
  es.addEventListener('phe_duyet_doi', () => { doi(); taiSoPheDuyet(); taiTrangThai() })
  es.addEventListener('doi_ngu_doi', () => { kho.phienBanDoiNgu += 1 })     // lát 2b: sự kiện khe.*, chay.*, …
  es.addEventListener('su_kien', (e) => {
    try {
      kho.suKienCuoi = JSON.parse(e.data)
      if (laSuKienNho(kho.suKienCuoi.loai)) kho.phienBanNho += 1     // màn Ký ức tải lại (1b-3)
      if (laSuKienTuDong(kho.suKienCuoi.loai)) {                       // TM-4: thanh trên, trang Tự động, Phê duyệt
        kho.phienBanTuDong += 1
        doi()                                                       // tải lại danh sách Phê duyệt đang mở
        taiTuDong()
        taiSoPheDuyet()
      }
    } catch {
      kho.suKienCuoi = null
    }
  })
  let daMo = false
  es.onerror = () => { kho.matKetNoi = true }
  es.onopen = () => {
    if (daMo) taiTrangThai()                  // bs-78r.8: nối lại sau khi rớt → quyền có thể đã đổi
    daMo = true
    kho.matKetNoi = false
  }
  return es
}

// bs-78r.8: tab ở nền lâu thì danh tính có thể đã đổi → tải lại khi tab hiện lại hoặc được focus. Trả hàm gỡ.
export function theoDoiTab(tai = taiTrangThai, d = globalThis.document, w = globalThis.window) {
  const lai = () => { if (d.visibilityState !== 'hidden') tai() }
  d.addEventListener('visibilitychange', lai)
  w.addEventListener('focus', lai)
  return () => {
    d.removeEventListener('visibilitychange', lai)
    w.removeEventListener('focus', lai)
  }
}
