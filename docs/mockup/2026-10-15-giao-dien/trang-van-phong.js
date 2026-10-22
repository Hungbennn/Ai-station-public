// Trang Văn phòng: cảnh 3D + panel bấm chọn + bản danh sách phòng.
import { dungVanPhong, PHONG } from './van-phong.js'
import { KHE, NHAN_HIEN_THI, TEN_BUOC, so_viec_cho } from './du-lieu.js'
import { esc } from './chung.js'

const KHOA_GIAM = 'ben-station-mockup-giam-chuyen-dong'
function docGiam() {
  try {
    const v = localStorage.getItem(KHOA_GIAM)
    if (v !== null) return v === '1'
  } catch { /* bỏ qua */ }
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches
}

function phongCuaKhe(k) {
  return k.bead && (k.hien_thi === 'lam' || k.hien_thi === 'can_nguoi') ? k.bead.du_an : 'ca-phe'
}

function noiDungPanel(c) {
  if (c.loai === 'khe') {
    const k = c.khe
    const tt = k.trang_thai === 'mat_ket_noi' ? 'Mất kết nối' : NHAN_HIEN_THI[k.hien_thi]
    if (k.bead) {
      return `<h3>${esc(k.ten)} <span class="chip tt-${k.hien_thi}">${tt}</span></h3>
        <p>Đang giữ <b class="mono">${k.bead.id}</b> · ${esc(k.bead.tieu_de)} · bước ${TEN_BUOC[k.bead.buoc]}.</p>
        <p class="nho">Sẽ mở bead <b>${k.bead.id}</b> ở ngăn bên trang Công việc (lọc dự án ${k.bead.du_an}).</p>
        <div class="hang-nut"><a class="nut chinh" href="#/cong-viec?du_an=${k.bead.du_an}&bead=${k.bead.id}" style="display:inline-flex;align-items:center;text-decoration:none">Mở bead ${k.bead.id}</a></div>`
    }
    const them = k.trang_thai === 'cau_dao' ? `Cầu dao ngắt (${esc(k.cau_dao.ly_do)}), tự đóng lúc ${esc(k.cau_dao.toi)}.`
      : k.trang_thai === 'mat_ket_noi' ? 'Không thấy nhịp tim từ máy B.' : k.trang_thai === 'tat' ? `Đại ca tắt khe (${esc(k.vi_sao_tat)}).` : 'Đang rảnh, chờ việc ở Góc cà phê.'
    return `<h3>${esc(k.ten)} <span class="chip tt-${k.trang_thai === 'cau_dao' ? 'cau_dao' : k.trang_thai}">${tt}</span></h3>
      <p>${them}</p><p class="nho">Không giữ việc → sẽ mở thẻ khe ở trang Đội ngũ AI.</p>
      <div class="hang-nut"><a class="nut chinh" href="#/doi-ngu" style="display:inline-flex;align-items:center;text-decoration:none">Mở Đội ngũ AI</a></div>`
  }
  const p = c.phong
  const dich = {
    du_an: [`Sẽ lọc trang Công việc theo dự án <b>${esc(p.ma)}</b>.`, `#/cong-viec?du_an=${p.ma}`, 'Lọc Công việc'],
    giam_doc: [`${so_viec_cho()} việc chờ Đại ca — sẽ mở Phê duyệt.`, '#/phe-duyet', 'Mở Phê duyệt'],
    may_chu: ['Máy B: 3 tủ xanh, 1 tủ vàng (khe claude-4 cầu dao ngắt). Sẽ mở Phê duyệt › Hệ cần xem.', '#/phe-duyet', 'Mở Phê duyệt'],
    ca_phe: ['Khe rảnh và khe không giữ việc đứng/ngồi ở đây — sẽ mở Đội ngũ AI.', '#/doi-ngu', 'Mở Đội ngũ AI'],
    dieu_phoi: ['Đèn Điều phối: chưa có tín hiệu (máy A chưa có nguồn báo phiên). Không có trang đích.', null, null],
  }[p.loai]
  const mo = p.mo ? '<p class="nho">Dự án tạm đóng: không nhận việc mới.</p>' : ''
  return `<h3>${esc(p.ten)}</h3><p>${dich[0]}</p>${mo}` +
    (dich[1] ? `<div class="hang-nut"><a class="nut chinh" href="${dich[1]}" style="display:inline-flex;align-items:center;text-decoration:none">${dich[2]}</a></div>` : '')
}

export function veVanPhong(trang, q) {
  const giam = docGiam()
  trang.innerHTML = `
    <div class="dau-trang">
      <div>
        <h1>Văn phòng</h1>
        <p>Ai đang làm gì, nhìn cho vui mắt. Vị trí lấy từ trạng thái nhiệm vụ thật; bấm vào nhân vật để mở việc.</p>
      </div>
      <div class="cong-cu vp-cong-cu">
        <label class="gc"><input type="checkbox" id="giam-cd" ${giam ? 'checked' : ''}> Giảm chuyển động</label>
      </div>
    </div>
    <div class="canh-khung" id="canh-khung">
      <div class="vp-goc">mockup · dữ liệu giả · camera trực giao (40,40,40)</div>
    </div>
    <h2 class="muc">Bản danh sách <span class="so">${PHONG.length} phòng</span></h2>
    <div class="ds-phong" id="ds-phong"></div>`

  const khung = trang.querySelector('#canh-khung')
  let panel = null
  function chon(c) {
    panel?.remove()
    panel = document.createElement('div')
    panel.className = 'vp-panel'
    panel.innerHTML = `<button class="dong" type="button" aria-label="Đóng">×</button>${noiDungPanel(c)}`
    panel.querySelector('.dong').onclick = () => { panel.remove(); panel = null }
    khung.appendChild(panel)
  }
  const canh = dungVanPhong(khung, { giamChuyenDong: giam, khiChon: chon })
  trang.querySelector('#giam-cd').onchange = (e) => {
    canh.datGiamChuyenDong(e.target.checked)
    try { localStorage.setItem(KHOA_GIAM, e.target.checked ? '1' : '0') } catch { /* bỏ qua */ }
  }

  // ?chon=<khe hoặc mã phòng> mở sẵn panel (để chụp ảnh / gửi link duyệt)
  const maChon = q?.get('chon')
  const khe = KHE.find((k) => k.id === maChon)
  const phong = PHONG.find((p) => p.ma === maChon)
  if (khe) chon({ loai: 'khe', khe })
  else if (phong) chon({ loai: 'phong', phong })

  const ds = trang.querySelector('#ds-phong')
  ds.innerHTML = PHONG.map((p, i) => {
    const nv = KHE.filter((k) => phongCuaKhe(k) === p.ma)
    const loai = { du_an: 'Dự án', giam_doc: 'Cố định', may_chu: 'Máy B', ca_phe: 'Khe rảnh', dieu_phoi: 'Máy A' }[p.loai]
    let phu = ''
    if (p.loai === 'giam_doc') phu = `<span class="chip tt-can_nguoi">${so_viec_cho()} việc chờ</span>`
    if (p.loai === 'dieu_phoi') phu = '<span class="chip">đèn: chưa có tín hiệu</span>'
    if (p.loai === 'may_chu') phu = '<span class="chip tt-lam">3 xanh</span><span class="chip tt-cau_dao">1 vàng</span>'
    if (p.mo) phu = '<span class="chip">tạm đóng</span>'
    const nvHtml = nv.map((k) => {
      const tt = k.trang_thai === 'mat_ket_noi' ? 'mat_ket_noi' : k.hien_thi
      const ten = k.trang_thai === 'mat_ket_noi' ? 'Mất kết nối' : NHAN_HIEN_THI[k.hien_thi]
      return `<span class="chip tt-${tt}">${esc(k.ten)} · ${ten}</span>`
    }).join('')
    return `<button class="the the-phong${p.mo ? ' mo' : ''}" data-i="${i}" type="button" style="border-left-color:${p.tuong};text-align:left;font:inherit;color:inherit">
      <div class="dau"><span class="cham" style="background:${p.san};box-shadow:inset 0 0 0 1px ${p.tuong};width:12px;height:12px"></span>
        <strong>${esc(p.ten)}</strong><span class="nho">${loai}</span></div>
      <div class="ds-nv">${phu}${nvHtml || (phu ? '' : '<span class="nho">Không có ai</span>')}</div>
    </button>`
  }).join('')
  for (const b of ds.querySelectorAll('.the-phong')) {
    b.onclick = () => { chon({ loai: 'phong', phong: PHONG[+b.dataset.i] }); khung.scrollIntoView({ behavior: 'smooth', block: 'center' }) }
  }
  return () => canh.huy()
}
