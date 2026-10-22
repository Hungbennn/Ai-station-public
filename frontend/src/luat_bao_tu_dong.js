// Khối báo đầu trang Tự động (mockup 2026-10-18 trang-tu-dong.js `veBao`; ảnh anh-hr-codex-khoa.png,
// anh-tu-dong-cua-tam.png, anh-tu-dong-lui-hong.png, anh-tu-dong-tu-tat.png) — thuần.
// `than`: danh sách [chữ, mono?] để trang vẽ bằng {{ }} (không chèn HTML).
import { gioPhut } from './dinh_dang.js'
import { CHU_CUA_TAM } from './luat_tu_dong.js'

// Giờ trạm tự tắt tự deploy: dòng `lich_su_doi` mới nhất do trạm (`tram/…`) đổi tu_deploy sang tắt; không có → ''.
export function gioTuTat(ds) {
  const r = (ds || []).find((x) => String(x.tac_nhan).startsWith('tram/')
    && x.doi.some((d) => d.truong === 'tu_deploy' && d.sau === false))
  return r ? gioPhut(r.luc) : ''
}

const doan = (...p) => p.map((x, i) => [x, i % 2 === 1])      // đoạn lẻ hiện chữ mono
const bao = (lop, tieuDe, than, nut = '') => ({ lop, tieuDe, than, nut })

function baoTamDung(td) {
  const gio = gioPhut(td.luc)
  if (td.ly_do === 'lui-hong') {
    return bao('do', `LÙI HỎNG lúc ${gio} — trang của khách có thể đang chết`, doan('Deploy hỏng, trạm đã chạy '
      + 'lệnh lùi nhưng kiểm còn sống vẫn không đạt. Trạm đã tắt tự deploy và tạm dừng dự án này. Telegram đã báo '
      + 'khẩn. Đại ca kiểm trang, sửa tay, rồi bấm Tiếp tục.'), 'Tiếp tục dự án')
  }
  if (td.ly_do === 'khong-ro') {
    return bao('do', `Deploy không rõ kết quả lúc ${gio} — cần Đại ca kiểm`, doan('Trạm tắt hay máy khởi động lại giữa '
      + 'lúc deploy. Trạm không tự chạy lại lệnh deploy hay lệnh lùi và đã tạm dừng dự án này. Đại ca kiểm trang của '
      + 'khách, rồi bấm Tiếp tục.'), 'Tiếp tục dự án')
  }
  const ai = String(td.boi).startsWith('tram/') ? 'Trạm' : String(td.boi).startsWith('dai-ca') ? 'Đại ca' : td.boi
  return bao('', 'Dự án đang tạm dừng', doan(`${ai} bấm lúc ${gio}. Trạm vẫn giao việc và mở PR, nhưng không tự merge, `
    + 'không tự deploy. Cài đặt bên dưới giữ nguyên. Nút Deploy của Đại ca vẫn dùng được.'), 'Tiếp tục')
}

// Khối báo đầu trang (mockup veBao), theo thứ tự: chỉ quét thử, cửa tạm, estop, tạm dừng dự án, trạm tự tắt.
export function baoTuDong(dl) {
  const ra = []
  if (dl.bat_ghi === false) {
    ra.push(bao('', 'Dự án đang chỉ quét thử', doan('Khoá ghi ', 'bat_ghi: false', ' — không bật được tự merge hay tự '
      + 'deploy. Đại ca bật ghi bằng tay trong ', `du-an/${dl.du_an}.yaml`, ' sau các cổng chạy thật. Nút tạm dừng vẫn '
      + 'bấm được.')))
  }
  if (dl.chi_tam_dung) {
    ra.push(bao('', CHU_CUA_TAM, doan('Trạm chưa chuyển cửa ghi sang loại chắc chắn (', 'unix-socket', '). Lúc này một '
      + 'chương trình trên máy B có thể giả là Đại ca, nên mọi nút bật và ô sửa ở đây bị khoá.')))
  }
  if (dl.estop) ra.push(bao('do', 'Estop đang bật', doan('Không tự merge, không tự deploy, nút Deploy cũng bị khoá.')))
  if (dl.tam_dung) ra.push(baoTamDung(dl.tam_dung))
  if (!dl.cai_dat.tu_deploy && dl.dem_hong >= 3) {
    const gio = gioTuTat(dl.lich_su_doi)
    ra.push(bao('', `Trạm đã tự tắt tự deploy${gio ? ` lúc ${gio}` : ''}`, doan('Hỏng 3 lần liên tiếp, lần nào cũng đã '
      + 'tự lùi thành công. Tự merge vẫn chạy; bản mới sẽ chờ ở "Sẵn sàng deploy". Bật lại tự deploy khi Đại ca đã '
      + 'kiểm — bộ đếm về 0.')))
  }
  return ra
}
