// Trang Dự án: giữ thẻ phòng của mockup 15/10, thêm hàng tóm tắt tự merge/deploy và link sang trang của dự án.
import { esc } from '../2026-10-15-giao-dien/chung.js'
import { DU_AN } from './du-lieu.js'
import { layDuAn, trangThaiTram } from './trang-thai.js'

const DEM_COT = { 'repo-nhap': [3, 0, 5], 'hr-codex': [2, 2, 1], 'ke-toan': [0, 0, 0] }

export function chipTuDong(d, s) {
  if (!d.bat_ghi) return '<span class="chip">chỉ quét thử</span>'
  if (trangThaiTram.estop) return '<span class="chip tt-loi">estop đang bật</span>'
  if (trangThaiTram.tam_dung) return '<span class="chip tt-cau_dao">tạm dừng toàn trạm</span>'
  if (s.tam_dung) return '<span class="chip tt-cau_dao">tạm dừng</span>'
  return `<span class="chip ${s.tu_merge ? 'tt-lam' : 'tt-tat'}">tự merge: ${s.tu_merge ? 'bật' : 'tắt'}</span>` +
    `<span class="chip ${s.tu_deploy ? 'tt-lam' : 'tt-tat'}">tự deploy: ${s.tu_deploy ? 'bật' : 'tắt'}</span>` +
    `<span class="chip ${s.cap_nhat.bat ? 'tt-lam' : 'tt-tat'}">agent cập nhật việc: ${s.cap_nhat.bat ? 'bật' : 'tắt'}</span>`
}

export function veDuAn(trang) {
  trang.innerHTML = `<div class="dau-trang"><div><h1>Dự án</h1>
      <p>Các dự án đã thêm vào trạm: số bead mỗi cột, lần quét cuối, lỗi gần nhất, tự merge, tự deploy, agent cập nhật việc.</p></div></div>
    <div class="ds-phong">${DU_AN.map((d) => {
      const s = layDuAn(d.ma)
      const dem = DEM_COT[d.ma]
      return `<div class="the the-phong${d.tam_dong ? ' mo' : ''}">
        <div class="dau"><a class="ten-lk" href="#/cong-viec?du_an=${d.ma}">${esc(d.ten)}</a>
          <span class="nho">${d.tam_dong ? 'tạm đóng' : 'quét cuối 22:14'}</span></div>
        <div class="ds-nv"><span class="chip">1 · ${dem[0]}</span><span class="chip">2 · ${dem[1]}</span><span class="chip">3 · ${dem[2]}</span></div>
        <div class="nho">Lỗi gần nhất: không có</div>
        <div class="tu-dong">${chipTuDong(d, s)}
          ${s.san_sang ? '<span class="chip pr-mo">1 sẵn sàng deploy</span>' : ''}
          ${s.dem_hong >= 3 ? '<span class="chip tt-can_nguoi">tự deploy đã tự tắt</span>' : ''}
          <a href="#/du-an/${d.ma}">Tự động →</a></div>
      </div>`
    }).join('')}</div>`
}
