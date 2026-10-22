// Dựng dữ liệu một thẻ dự án từ phần tử /api/du-an (mockup trang.js veDuAn, D36, D37) + tóm tắt tự merge/tự deploy
// của /api/tu-dong (TM-4, mockup 2026-10-18 trang-du-an.js: hàng chip + link "Tự động →").
import { gioPhut } from './dinh_dang.js'
import { chipTuDong } from './luat_tu_dong.js'

// Ba chip cột: 1 = ai-lam, 2 = can-chot, 3 = cho-review (mockup đếm cột 1/2/3).
const COT_CHIP = ['ai-lam', 'can-chot', 'cho-review']

// `td`: GET /api/tu-dong (null khi chưa đọc được). `san_sang`, `dem_hong`: khoá TM-3 hứa thêm — thiếu thì bỏ chip.
export function theDuAn(d, td = null) {
  const sb = d.so_bead || {}
  const lg = d.loi_gan_nhat
  const da = td && (td.du_an || []).find((x) => x.ten === d.ten)
  const chipPhu = da ? [da.san_sang && { chu: '1 sẵn sàng deploy', lop: 'pr-mo' },
    da.dem_hong >= 3 && { chu: 'tự deploy đã tự tắt', lop: 'tt-can_nguoi' }].filter(Boolean) : []
  return {
    ten: d.ten,
    den: '/cong-viec?du_an=' + encodeURIComponent(d.ten),
    quet: d.quet_cuoi ? 'quét cuối ' + gioPhut(d.quet_cuoi) : 'chưa quét',
    chip: COT_CHIP.map((h, i) => ({ chu: `${i + 1} · ${sb[h] || 0}` })),
    // Bản thật có hàng chưa chấm, mockup không vẽ (D36): giữ khi > 0.
    chuaCham: sb['chua-cham'] > 0 ? `Chưa chấm · ${sb['chua-cham']}` : '',
    loiGanNhat: 'Lỗi gần nhất: ' + (lg ? `${gioPhut(lg.luc)} · ${lg.loi}` : 'không có'),
    loiDoc: d.loi_doc || '',
    chiQuetThu: d.bat_ghi === false, // D37: "chỉ quét thử", không dùng chữ "tạm đóng"
    tuDongDen: '/du-an/' + encodeURIComponent(d.ten),
    chipTuDong: da ? chipTuDong(da, td) : chipTuDong(d.bat_ghi === false ? { bat_ghi: false } : null, null),
    chipPhu,
  }
}
