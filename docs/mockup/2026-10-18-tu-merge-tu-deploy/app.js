// Mockup tự merge + tự deploy (+ agent tự cập nhật việc) — khung giống mockup 15/10; vẽ Dự án, trang Tự động của dự án, Công việc.
// Các mục menu khác trỏ về mockup đã duyệt (không vẽ lại). Dữ liệu giả, không gọi API.
import { dongNganBen } from '../2026-10-15-giao-dien/chung.js'
import { veDuAn } from './trang-du-an.js'
import { veTuDong } from './trang-tu-dong.js'
import { veCongViec } from './trang-cong-viec.js'
import { trangThaiTram, datTamDungTram, datEstop } from './trang-thai.js'

// Icon menu: chép từ app.js của mockup 15/10 (file đó không export).
const I = {
  'tong-quan': '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M9 21V9"/>',
  'du-an': '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v3"/><path d="M3 7v11a2 2 0 0 0 2 2h7"/><circle cx="17.5" cy="17.5" r="2.5"/><path d="M17.5 13.5v1.5M17.5 20v1.5M13.5 17.5H15M20 17.5h1.5"/>',
  'van-phong': '<path d="M4 21V5a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v16"/><path d="M16 9h3a1 1 0 0 1 1 1v11"/><path d="M2 21h20M8 7h1M11 7h1M8 11h1M11 11h1M8 15h1M11 15h1"/>',
  'cong-viec': '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M8 7v7M12 7v4M16 7v9"/>',
  'doi-ngu': '<rect x="5" y="8" width="14" height="11" rx="3"/><path d="M12 8V5M10 4h4"/><circle cx="9.5" cy="13" r="1"/><circle cx="14.5" cy="13" r="1"/><path d="M3 12v3M21 12v3"/>',
  'ky-uc': '<path d="M12 5a3 3 0 0 0-5.8-1A3 3 0 0 0 4 8a3 3 0 0 0 .5 5.5A3.5 3.5 0 0 0 9 19a3 3 0 0 0 3-1"/><path d="M12 5a3 3 0 0 1 5.8-1A3 3 0 0 1 20 8a3 3 0 0 1-.5 5.5A3.5 3.5 0 0 1 15 19a3 3 0 0 1-3-1V5"/>',
  'usage': '<path d="M3 3v18h18"/><path d="M7 16v-3M11 16V9M15 16v-5M19 16V6"/>',
  'phe-duyet': '<path d="M12 2.5l2.3 1.7 2.8-.2.9 2.7 2.3 1.6-.9 2.7.9 2.7-2.3 1.6-.9 2.7-2.8-.2L12 21.5l-2.3-1.7-2.8.2-.9-2.7L3.7 15.7l.9-2.7-.9-2.7 2.3-1.6.9-2.7 2.8.2z"/><path d="m8.5 12 2.5 2.5 4.5-5"/>',
  'cai-dat': '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/>',
}
const MENU = [
  ['tong-quan', 'Tổng quan'], ['du-an', 'Dự án'], ['van-phong', 'Văn phòng'], ['cong-viec', 'Công việc'],
  ['doi-ngu', 'Đội ngũ AI'], ['ky-uc', 'Ký ức'], ['usage', 'Usage & chi phí'], ['phe-duyet', 'Phê duyệt'], ['cai-dat', 'Cài đặt'],
]

const menu = document.getElementById('menu')
menu.innerHTML = MENU.map(([ma, ten]) =>
  `<a href="#/${ma}" data-ma="${ma}"><svg viewBox="0 0 24 24" aria-hidden="true">${I[ma]}</svg>${ten}` +
  (ma === 'phe-duyet' ? '<span class="dem">4</span>' : '') + '</a>').join('')

const trang = document.getElementById('trang')

function veMockupCu(ma, ten) {
  trang.innerHTML = `<div class="dau-trang"><div><h1>${ten}</h1>
    <p>Trang này không đổi trong đợt tự merge/deploy — xem bản đã duyệt.</p></div></div>
    <div class="cho-chot"><strong>${ten}</strong>Giữ nguyên mockup đã duyệt ngày 15/10:
    <a href="../2026-10-15-giao-dien/index.html#/${ma}">mở ${ten} trong mockup 15/10</a>.</div>`
}

function dieuHuong() {
  const [duong, chuoi] = location.hash.replace(/^#\/?/, '').split('?')
  const phan = (duong || 'du-an').split('/')
  const q = new URLSearchParams(chuoi || '')
  dongNganBen()
  for (const a of menu.querySelectorAll('a')) a.classList.toggle('chon', a.dataset.ma === phan[0])
  trang.innerHTML = ''
  if (phan[0] === 'du-an' && phan[1]) {
    document.title = `${phan[1]} · Dự án · Ben Station (mockup)`
    veTuDong(trang, phan[1], q, dieuHuong)
  } else if (phan[0] === 'cong-viec') {
    document.title = 'Công việc · Ben Station (mockup)'
    veCongViec(trang, q)
  } else if (phan[0] === 'du-an') {
    document.title = 'Dự án · Ben Station (mockup)'
    veDuAn(trang, dieuHuong)
  } else {
    const ten = MENU.find(([m]) => m === phan[0])?.[1] ?? 'Dự án'
    document.title = `${ten} · Ben Station (mockup)`
    veMockupCu(phan[0], ten)
  }
  window.scrollTo(0, 0)
}

// Thanh trên: Estop (như mockup cũ) + TẠM DỪNG toàn trạm (mới). Mockup: chỉ đổi giao diện; bản thật đi qua cửa ghi.
document.getElementById('nut-estop').onclick = () => {
  if (trangThaiTram.estop || confirm('Bật Estop? Trạm ngừng giao việc mới, không tự merge, không deploy.')) {
    datEstop(!trangThaiTram.estop); dieuHuong()
  }
}
document.getElementById('nut-tiep-tuc').onclick = () => { datEstop(false); dieuHuong() }
document.getElementById('nut-tam-dung-tram').onclick = () => {
  if (trangThaiTram.tam_dung) { datTamDungTram(false); dieuHuong(); return }
  if (confirm('Tạm dừng tự merge và tự deploy của MỌI dự án? Trạm vẫn giao việc, kiểm lại, QC, mở PR.')) {
    datTamDungTram(true); dieuHuong()
  }
}
document.getElementById('nut-tiep-tuc-tram').onclick = () => { datTamDungTram(false); dieuHuong() }

// Tham số ảnh chụp: ?tram=tam-dung bật sẵn băng tạm dừng toàn trạm.
if (new URLSearchParams(location.hash.split('?')[1] || '').get('tram') === 'tam-dung') datTamDungTram(true)

const oTim = document.getElementById('o-tim')
window.addEventListener('keydown', (e) => {
  if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); oTim.focus() }
  if (e.key === 'Escape') dongNganBen()
})
window.addEventListener('hashchange', dieuHuong)
dieuHuong()
