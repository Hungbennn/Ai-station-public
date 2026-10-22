// Trang Công việc — CHỈ minh hoạ phần thêm của "agent tự cập nhật việc" (D81–D86, spec bs-2bd.5) trên thẻ việc:
// dòng tiến độ do agent ghi, nhãn "do agent tạo" + việc gốc, trạng thái "bị chặn — cần Đại ca" kèm lý do.
// Bố cục bảng ba cột giữ đúng mockup đã duyệt 15/10.
import { esc, moNganBen } from '../2026-10-15-giao-dien/chung.js'
import { BEAD_CV } from './du-lieu.js'

const COT = [
  [1, 'AI tự làm', 'Trạm giao cho khe theo luật vai'],
  [2, 'Cần Đại ca chốt', 'Có câu hỏi hoặc rủi ro nghiệp vụ'],
  [3, 'Chờ review để đóng', 'Đã code + QC, chờ Duyệt'],
]

function theBead(b) {
  const td = b.tien_do?.[0]
  return `<div class="the the-bead" data-id="${b.id}" tabindex="0" role="button">
    <div class="tren"><span class="ma">${b.id}</span><span class="chip">repo-nhap</span><span class="nho day-phai">${b.loai} · ${b.uu_tien}</span></div>
    <div class="tieu-de">${esc(b.tieu_de)}</div>
    ${b.bi_chan || b.goc || b.hang_rao ? `<div class="nhan-ds">
      ${b.bi_chan ? '<span class="chip tt-can_nguoi">bị chặn — cần Đại ca</span>' : ''}
      ${b.goc ? `<span class="chip pv-cach-lam">do agent tạo</span><a class="viec-goc" href="#/cong-viec?bead=${b.goc}" data-goc="${b.goc}">từ ${b.goc}</a>` : ''}
      ${b.hang_rao ? `<span class="chip mono">hàng rào: ${esc(b.hang_rao)}</span>` : ''}</div>` : ''}
    ${b.bi_chan ? `<div class="ly-do-chan"><b>Lý do:</b> ${esc(b.bi_chan[1])}</div>` : ''}
    ${td ? `<div class="tien-do"><span class="mono">${td[0]}</span> ${esc(td[1])}: ${esc(td[2])}</div>` : ''}
    ${b.khe ? `<div class="khe">${esc(b.khe[0])} · ${b.khe[2]}${b.bi_chan ? ' · <b class="chu-do">dừng chờ Đại ca</b>' : ''}</div>` : ''}
  </div>`
}

function moBead(b) {
  if (!b) return
  moNganBen(`<div class="nho mono">repo-nhap · ${b.id} · cột ${b.cot}</div><h2>${esc(b.tieu_de)}</h2>
    ${b.bi_chan ? `<h4>Bị chặn — cần Đại ca</h4><div class="ly-do-chan"><b>${b.bi_chan[0]}:</b> ${esc(b.bi_chan[1])}</div>
      <p class="nho">Agent báo qua trạm; trạm đã ghi vào việc và báo Telegram. Đại ca trả lời như câu hỏi của agent hiện nay.</p>` : ''}
    ${b.goc ? `<h4>Nguồn</h4><p><span class="chip pv-cach-lam">do agent tạo</span> từ
      <a class="viec-goc" href="#/cong-viec?bead=${b.goc}">${b.goc}</a> lúc ${b.tao_luc} — trạm ghi sau khi QC và kiểm lại của ${b.goc} đạt.
      Chưa giao: bộ chấm cột xếp như mọi việc${b.hang_rao ? ` (chạm hàng rào ${esc(b.hang_rao)} → cột "Cần Đại ca chốt")` : ''}.</p>` : ''}
    ${b.tien_do ? `<h4>Tiến độ do agent ghi</h4><ul class="dtg">${b.tien_do.map(([g, k, c]) =>
      `<li><span class="mono">${g}</span>${esc(k)}: ${esc(c)}</li>`).join('')}</ul>` : ''}
    ${!b.bi_chan && !b.goc && !b.tien_do ? '<p class="nho">Chưa có cập nhật nào từ agent.</p>' : ''}`)
}

export function veCongViec(trang, q) {
  trang.innerHTML = `<div class="dau-trang"><div><h1>Công việc</h1>
      <p>Ba cột do trạm chấm. Đợt này chỉ thêm phần agent tự cập nhật việc trên thẻ (D81–D86); còn lại giữ mockup 15/10.</p></div>
      <div class="cong-cu"><span class="chip">repo-nhap</span></div></div>
    <div class="bang-cot">${COT.map(([so, ten, mota]) => {
      const the = BEAD_CV.filter((b) => b.cot === so)
      return `<section class="cot"><div class="cot-dau"><span class="so-thu">${so}</span><h3>${ten}</h3><span class="so">${the.length}</span></div>
        <p class="nho mo-ta-cot">${mota}</p>${the.map(theBead).join('')}</section>`
    }).join('')}</div>`
  for (const el of trang.querySelectorAll('.the-bead')) {
    const mo = () => moBead(BEAD_CV.find((b) => b.id === el.dataset.id))
    el.onclick = (e) => { if (!e.target.closest('a')) mo() }
    el.onkeydown = (e) => { if (e.key === 'Enter') mo() }
  }
  moBead(BEAD_CV.find((b) => b.id === q.get('bead')))
}
