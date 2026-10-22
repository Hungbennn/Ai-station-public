// Luật hiển thị trang Công việc + ngăn bên (mockup trang.js COT, theBead, moBead) — thuần, test bằng node --test.
import { lopPrTram, nhanPrTram, prTram } from './giao_viec.js'
import { TEN_HANG } from './luat.js'
import { tenKhe } from './luat_han_muc.js'
import { mauKhe } from './mau_khe.js'

export const MO_TA_TRANG = 'Ba cột do trạm chấm; kéo thẻ giữa cột 1 và 2 để sửa, cột 3 do thợ và Phê duyệt quản.'

// Ba cột chính (mockup trang.js COT): hàng của API → số thứ tự, tên, mô tả dưới đầu cột.
export const COT = [
  { hang: 'ai-lam', so: 1, ten: 'AI tự làm', moTa: 'Trạm giao cho khe theo luật vai' },
  { hang: 'can-chot', so: 2, ten: 'Cần Đại ca chốt', moTa: 'Có câu hỏi hoặc rủi ro nghiệp vụ' },
  { hang: 'cho-review', so: 3, ten: 'Chờ review để đóng', moTa: 'Đã code + QC, chờ Duyệt' },
]
const SO_COT = Object.fromEntries(COT.map((c) => [c.hang, c.so]))
const TEN_BUOC = { spec: 'spec', code: 'code', qc: 'QC' }     // mockup du-lieu.js TEN_BUOC

// API không trả danh sách nhãn — suy chip `cot:<hang>` từ hang (khảo sát §1.3); hàng ngoài ba cột không có nhãn cột.
export function chipCot(the) {
  return the && SO_COT[the.hang] ? `cot:${the.hang}` : ''
}

// Dòng đầu ngăn bên "du_an · id · cột n" (mockup moBead); hàng phụ (Chưa chấm, Epic…) ghi tên hàng.
export function viTriThe(the) {
  return SO_COT[the.hang] ? `cột ${SO_COT[the.hang]}` : TEN_HANG[the.hang] ?? TEN_HANG['chua-cham']
}

export function uuTien(the) {
  return `P${the.uu_tien ?? '?'}`
}

// Chip trên thẻ (mockup theBead `.nhan-ds`) + chip của bản cũ phải giữ (khảo sát §1.3, D36, D37). {chu, lop, goiY}.
export function chipThe(the, chiQuetThu = false) {
  const ds = []
  const them = (chu, lop = '', goiY = '') => ds.push({ chu, lop, goiY })
  if (chipCot(the)) them(chipCot(the), 'mono')
  if (the.khoa) them('khoá', '', 'Đại ca đã khoá cột')
  if (the.co_do) them('cờ đỏ', 'tt-loi')
  if (the.lech) them('nhãn lệch', 'tt-cau_dao', 'Nhiều nhãn cột')
  if (the.giao && the.giao.khong_giao) them('chưa giao', 'tt-cau_dao', the.giao.khong_giao)
  if (the.cho && the.cho.length) them(`chờ ${the.cho.join(', ')}`)
  if (the.khe_spec) them('khe spec')
  if (chiQuetThu) them('chỉ quét thử', 'tt-tat', 'bat_ghi: false — trạm từ chối thao tác ghi')
  if (nhanPrTram(the)) them(nhanPrTram(the), lopPrTram(prTram(the)))
  return ds
}

// Dòng "Claude 1 · code · đang hỏi Đại ca" (mockup theBead `.khe`): ghép phía trình duyệt với /api/doi-ngu
// theo khe.phieu {du_an, bead_id} (khảo sát T7). Không khe nào giữ bead → null.
export function dongKhe(the, dsKhe) {
  const khe = (dsKhe || []).find((k) => k.phieu && k.phieu.du_an === the.du_an && k.phieu.bead_id === the.id)
  if (!khe) return null
  const buoc = khe.phieu.buoc
  return { ten: tenKhe(khe), buoc: TEN_BUOC[buoc] ?? buoc ?? '', canNguoi: khe.trang_thai === 'can_nguoi',
    mau: mauKhe(khe.khe_id).than }
}
