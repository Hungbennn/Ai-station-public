// Luật hiển thị lịch sử của trang Tự động (mockup 2026-10-18 du-lieu.js LOAI_SU_KIEN, trang-tu-dong.js veLichSu,
// veDemHong, ngăn "Lịch sử đổi cài đặt") — thuần. Máy chủ dựng `chi_tiet` (chỉ mã thoát, thời gian — không có log);
// ở đây chỉ chọn nhãn, màu, giờ VN và ghép câu.
import { gioPhut, ngayGio } from './dinh_dang.js'
import { DIEU_KIEN, LENH, ma7 } from './luat_trang_tu_dong.js'

// loai (TM-3 `tram/deploy/hien_thi.LOAI_LICH_SU`) → [nhãn, lớp chip]; loại lạ hiện nguyên mã, không màu.
const LOAI = {
  tu_merge: ['Tự merge', 'pr-da_merge'], san_sang: ['Sẵn sàng deploy', 'pr-mo'], deploy_dat: ['Deploy xong', 'tt-lam'],
  deploy_lui: ['Hỏng · đã tự lùi', 'tt-cau_dao'], lui_hong: ['LÙI HỎNG', 'tt-loi'],
  khong_ro: ['Không rõ kết quả', 'tt-loi'], tu_tat: ['Tự tắt tự deploy', 'tt-can_nguoi'],
  tam_dung: ['Tạm dừng', 'tt-tat'], huy: ['Deploy bị huỷ', 'tt-tat'],     // huy: TM-3 câu hỏi 5 (a), `deploy.huy`
}
const AI = { dai_ca: 'Đại ca', dai_ca_bam: 'Đại ca bấm', tu_deploy: 'tự deploy', tram: 'trạm' }

export function dongLichSu(r) {
  const [nhan, lop] = LOAI[r.loai] ?? [r.loai, '']
  return { gio: gioPhut(r.luc), nhan, lop, bead: r.bead_id || '—', commit: ma7(r.commit), chiTiet: r.chi_tiet || '',
    ai: AI[r.ai] ?? r.ai ?? '' }
}

export function demHong(n) {
  if (typeof n !== 'number') return null
  return { den: [0, 1, 2].map((i) => (i < n ? 'thieu' : 'cho')), chu: `${n} / 3` }
}

export function tenTacNhan(t) {
  if (t === 'dai-ca/dashboard') return 'Đại ca (dashboard)'
  if (String(t).startsWith('dai-ca')) return 'Đại ca'
  return String(t).startsWith('tram/') ? 'trạm' : t
}

const TEN_BAT = { tu_merge: 'tự merge', tu_deploy: 'tự deploy',
  ...Object.fromEntries(DIEU_KIEN.filter((d) => !d.khoa).map((d) => [`dk_${d.ma}`, `nút "${d.ngan}"`])) }
const TEN_LENH = Object.fromEntries(LENH.map((l) => [`lenh_${l.ma}`, l.ngan]))
const giaTri = (v) => (typeof v === 'boolean' ? (v ? 'bật' : 'tắt')
  : !v ? 'trống' : v.includes('/') ? `…/${v.split('/').pop()}` : v)

// Một dòng của `lich_su_doi` (TM-1: {luc, tac_nhan, doi: [{truong, truoc, sau}]}) → {gio, ai, viec, doi}.
export function dongLichSuDoi(r) {
  const bat = r.doi.filter((d) => TEN_BAT[d.truong]).map((d) => `${d.sau ? 'Bật' : 'Tắt'} ${TEN_BAT[d.truong]}`)
  const lenh = r.doi.filter((d) => TEN_LENH[d.truong]).map((d) => TEN_LENH[d.truong])
  const viec = [...bat, ...(lenh.length ? [`Sửa ${lenh.join(', ')}`] : [])].join(', ')
  return { gio: ngayGio(r.luc), ai: tenTacNhan(r.tac_nhan), viec,
    doi: r.doi.map((d) => `${giaTri(d.truoc)} → ${giaTri(d.sau)}`).join(', ') }
}

export function doiCuoi(ds) {
  if (!ds || !ds.length) return 'Chưa từng đổi — đang dùng mặc định'
  return `Đổi lần cuối: ${tenTacNhan(ds[0].tac_nhan)} · ${ngayGio(ds[0].luc)}`
}
