// Các trang phẳng: Công việc, Đội ngũ AI, Phê duyệt, Dự án, chỗ chờ chốt.
import { BEAD, DU_AN, KHE, NHAN_TRANG_THAI, NHAN_PR, HE_CAN_XEM, BANG_DIEM, TEN_BUOC } from './du-lieu.js'
import { esc, moNganBen, chibi, tiLe } from './chung.js'

const dauTrang = (ten, mota, congCu = '') =>
  `<div class="dau-trang"><div><h1>${ten}</h1><p>${mota}</p></div>${congCu ? `<div class="cong-cu">${congCu}</div>` : ''}</div>`

const chonDuAn = (id, chon) => `<select id="${id}" aria-label="Dự án"><option value="">Tất cả dự án</option>` +
  DU_AN.map((d) => `<option value="${d.ma}" ${d.ma === chon ? 'selected' : ''}>${d.ten}${d.tam_dong ? ' (tạm đóng)' : ''}</option>`).join('') + '</select>'

// ---------- Công việc ----------
const COT = [
  [1, 'AI tự làm', 'Trạm giao cho khe theo luật vai'],
  [2, 'Cần Đại ca chốt', 'Có câu hỏi hoặc rủi ro nghiệp vụ'],
  [3, 'Chờ review để đóng', 'Đã code + QC, chờ Duyệt'],
]

function theBead(b) {
  const khe = KHE.find((k) => k.id === b.khe)
  const pr = b.pr ? `<span class="chip pr-${b.pr.trang_thai}">${NHAN_PR[b.pr.trang_thai]}</span>` : ''
  return `<div class="the the-bead" data-id="${b.id}" tabindex="0" role="button">
    <div class="tren"><span class="ma">${b.id}</span><span class="chip">${b.du_an}</span><span class="nho" style="margin-left:auto">${b.loai} · ${b.uu_tien}</span></div>
    <div class="tieu-de">${esc(b.tieu_de)}</div>
    <div class="nhan-ds">${b.nhan.map((n) => `<span class="chip mono">${n}</span>`).join('')}${pr}${b.minh_hoa ? '<span class="chip" title="Bead thêm để minh hoạ nhãn PR">minh hoạ</span>' : ''}</div>
    ${khe ? `<div class="khe"><span class="cham" style="background:${khe.mau}"></span>${khe.ten} · ${TEN_BUOC[b.buoc]}${khe.hien_thi === 'can_nguoi' ? ' · <b style="color:var(--do)">đang hỏi Đại ca</b>' : ''}</div>` : ''}
  </div>`
}

function moBead(b) {
  const cauHoi = b.cau_hoi ? `<h4>Câu hỏi cần chốt</h4>${b.cau_hoi.map((c, i) =>
    `<div class="cau-hoi"><label for="tl-${i}"><b>${i + 1}.</b> ${esc(c)}</label><textarea id="tl-${i}" placeholder="Trả lời…"></textarea></div>`).join('')}
    <div style="display:flex;gap:8px"><button class="nut chinh" type="button">Chốt</button><button class="nut" type="button">Dẫn ADR</button></div>` : ''
  const pr = b.pr ? `<h4>PR</h4><p><span class="chip pr-${b.pr.trang_thai}">${NHAN_PR[b.pr.trang_thai]}</span> PR #${b.pr.so}${b.pr.ly_do ? ` — ${esc(b.pr.ly_do)}` : ''}</p>` : ''
  moNganBen(`<div class="nho mono">${b.du_an} · ${b.id} · cột ${b.cot}</div>
    <h2>${esc(b.tieu_de)}</h2>
    <div style="display:flex;gap:6px;flex-wrap:wrap">${b.nhan.map((n) => `<span class="chip mono">${n}</span>`).join('')}<span class="chip">${b.loai}</span><span class="chip">${b.uu_tien}</span></div>
    <h4>Lý do lần chấm gần nhất</h4><p>${esc(b.ly_do)}</p>
    ${cauHoi}${pr}
    <h4>Mô tả</h4><p>${esc(b.mo_ta)}</p>
    <h4>Tiêu chí nghiệm thu</h4><ul>${b.nghiem_thu.map((n) => `<li>${esc(n)}</li>`).join('')}</ul>
    <h4>Dòng thời gian</h4><ul class="dtg">${b.dong_thoi_gian.map(([t, s]) => `<li><span class="mono">${t}</span>${esc(s)}</li>`).join('')}</ul>`)
}

export function veCongViec(trang, q) {
  let duAn = q.get('du_an') || ''
  function ve() {
    const ds = BEAD.filter((b) => !duAn || b.du_an === duAn)
    trang.innerHTML = dauTrang('Công việc', 'Ba cột do trạm chấm; kéo thẻ giữa cột 1 và 2 để sửa, cột 3 do thợ và Phê duyệt quản.',
      `${chonDuAn('loc-du-an', duAn)}`) +
      `<div class="bang-cot">${COT.map(([so, ten, mota]) => {
        const the = ds.filter((b) => b.cot === so)
        return `<section class="cot"><div class="cot-dau"><span class="so-thu">${so}</span><h3>${ten}</h3><span class="so">${the.length}</span></div>
          <p class="nho" style="margin:-6px 4px 12px">${mota}</p>
          ${the.map(theBead).join('') || `<div class="cot-rong">Không có bead${duAn ? ` của ${duAn}` : ''}</div>`}</section>`
      }).join('')}</div>`
    trang.querySelector('#loc-du-an').onchange = (e) => {
      duAn = e.target.value
      history.replaceState(null, '', `#/cong-viec${duAn ? `?du_an=${duAn}` : ''}`)
      ve()
    }
    for (const el of trang.querySelectorAll('.the-bead')) {
      const mo = () => moBead(BEAD.find((b) => b.id === el.dataset.id))
      el.onclick = mo
      el.onkeydown = (e) => { if (e.key === 'Enter') mo() }
    }
  }
  ve()
  const bead = BEAD.find((b) => b.id === q.get('bead'))
  if (bead) moBead(bead)
}

// ---------- Đội ngũ AI ----------
function thanhHm(ten, phanTram, reset) {
  if (phanTram == null) return `<span>${ten}</span><div class="thanh-hm"></div><span class="nho">chưa biết</span>`
  const lop = phanTram === 0 ? 'het' : phanTram < 30 ? 'thap' : ''
  return `<span>${ten}</span><div class="thanh-hm"><i class="${lop}" style="width:${Math.max(phanTram, 2)}%"></i></div><span>còn ${phanTram}% · ${reset}</span>`
}

function theKhe(k) {
  const tt = k.trang_thai
  const mo = tt === 'tat' || tt === 'mat_ket_noi'
  const viec = k.bead ? `<div class="viec"><span class="mono">${k.bead.id}</span>${esc(k.bead.tieu_de)} · ${TEN_BUOC[k.bead.buoc]}</div>`
    : tt === 'cau_dao' ? `<div class="viec" style="background:#fcf3e2;border-color:#efd8a8">Cầu dao ngắt: ${esc(k.cau_dao.ly_do)} · tự đóng ${esc(k.cau_dao.toi)}</div>`
      : tt === 'tat' ? `<div class="viec">Đại ca tắt khe · “${esc(k.vi_sao_tat)}”</div>`
        : tt === 'mat_ket_noi' ? '<div class="viec">Không thấy nhịp tim từ máy B</div>' : '<div class="viec nho">Không giữ việc</div>'
  const hm = k.han_muc
  return `<article class="the the-khe${mo ? ' mo' : ''}">
    <div class="dau">${chibi(k)}<div><strong>${k.ten}</strong><span class="nho">${k.id} · máy ${k.may} · ${k.tai_khoan}</span></div>
      <span class="chip tt-${tt}"><span class="cham" style="background:currentColor"></span>${NHAN_TRANG_THAI[tt]}</span></div>
    ${viec}
    <div class="han-muc">${thanhHm('5 giờ', hm?.gio5, hm ? `reset ${hm.reset5}` : '')}${thanhHm('Tuần', hm?.tuan, hm ? `reset ${hm.resetTuan}` : '')}</div>
    <div class="nho" style="display:flex;gap:14px;flex-wrap:wrap"><span>Vai: ${k.vai.join(', ')}</span><span>Phiên: ${k.phien}</span></div>
    <div class="chan"><span class="nho">♥ nhịp tim cuối: ${k.nhip}</span>
      ${tt === 'cau_dao' ? '<button class="nut chinh" type="button">Đóng cầu dao</button>' : ''}
      <button class="nut ${tt === 'tat' ? 'chinh' : 'nguy'}" type="button">${tt === 'tat' ? 'Bật khe' : 'Tắt khe'}</button></div>
  </article>`
}

export function veDoiNgu(trang) {
  let duAn = ''
  let soNgay = 30
  function ve() {
    trang.innerHTML = dauTrang('Đội ngũ AI', 'Mỗi khe một thẻ: trạng thái, việc đang giữ, hạn mức còn lại. Tắt khe để dành hạn mức cho việc tay.') +
      `<section class="the" style="padding:14px 16px 6px">
        <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:6px">
          <h2 style="margin:0;font-size:17px">Bảng điểm thợ</h2>
          <span class="nho">lọc áp cho mọi cột</span>
          <div style="margin-left:auto;display:flex;gap:8px;align-items:center">${chonDuAn('bd-du-an', duAn)}
            <div class="nhom-nut" role="group" aria-label="Khoảng">${[7, 30, 92].map((n) => `<button type="button" data-n="${n}" class="${n === soNgay ? 'chon' : ''}">${n} ngày</button>`).join('')}</div></div>
        </div>
        <div style="overflow-x:auto"><table class="bang"><thead><tr><th>Khe</th><th>Vai</th><th>Số phiếu</th><th>Xong</th><th>Lần chạy TB / phiếu</th><th>Qua lần đầu</th><th>Bị trả về</th></tr></thead>
        <tbody>${BANG_DIEM.map((d) => `<tr><th class="mono" style="font-weight:500">${d.khe}</th><td>${d.vai}</td><td class="so">${d.so_phieu}</td><td class="so">${d.xong}</td>
          <td class="so">${d.tb ?? '—'}</td><td>${tiLe(d.qua)}</td><td>${tiLe(d.tra)}</td></tr>`).join('')}</tbody></table></div>
        <p class="nho" style="margin:8px 0">Qua lần đầu: phiếu code xong mà lần kiểm lại / QC đầu tiên qua. Bị trả về: bead vào cột 3 rồi bị Đại ca Trả về. Chỉ tính vai coder; vai khác “—”. Số liệu giả ${duAn ? `(${duAn}, ` : '('}${soNgay} ngày).</p>
      </section>
      <h2 class="muc">Khe <span class="so">${KHE.length}</span></h2>
      <div class="luoi-khe">${KHE.map(theKhe).join('')}</div>
      <h2 class="muc">Luật vai ↔ khe</h2>
      <div class="the nho" style="font-size:13.5px">Bước → vai: <span class="chip mono">spec → spec</span> <span class="chip mono">code → coder</span> <span class="chip mono">qc → qc</span>
        &nbsp;· Khe QC phải khác CLI với khe code của cùng bead.</div>`
    trang.querySelector('#bd-du-an').onchange = (e) => { duAn = e.target.value; ve() }
    for (const b of trang.querySelectorAll('.nhom-nut button')) b.onclick = () => { soNgay = +b.dataset.n; ve() }
  }
  ve()
}

// ---------- Phê duyệt ----------
function theReview(b) {
  const pr = b.pr
  const nutDong = pr?.trang_thai === 'da_merge'
    ? '<span class="nho">trạm đã xác minh — sẽ tự đóng</span>'
    : pr ? '<button class="nut" type="button">Đã merge trên GitHub → đóng bead</button>' : ''
  return `<article class="the the-duyet">
    <div>
      <div class="tren"><span class="ma">${b.id}</span><span class="chip">${b.du_an}</span>
        ${pr ? `<span class="chip pr-${pr.trang_thai}">${NHAN_PR[pr.trang_thai]}</span><a href="#/phe-duyet" class="nho">PR #${pr.so} ↗</a>` : ''}
        ${b.minh_hoa ? '<span class="chip" title="Bead thêm để minh hoạ nhãn PR">minh hoạ</span>' : ''}</div>
      <div class="tieu-de">${esc(b.tieu_de)}</div>
      <div class="nho">${esc(b.ly_do)}</div>
      ${pr?.trang_thai === 'khong_xac_minh' ? `<div class="canh-bao">PR đã merge nhưng trạm không xác minh được: ${esc(pr.ly_do)}. Bead ở lại cột 3 — Đại ca tự kiểm rồi bấm Duyệt.</div>` : ''}
    </div>
    <div class="hanh-dong">${nutDong}<button class="nut chinh" type="button">Duyệt</button><button class="nut" type="button" data-tra-ve>Trả về + góp ý</button></div>
    <div class="gop-y" hidden><textarea placeholder="Góp ý cho thợ (ghi vào notes, bead về hàng chưa chấm)…"></textarea><button class="nut chinh" type="button">Gửi trả về</button></div>
  </article>`
}

export function vePheDuyet(trang) {
  const review = BEAD.filter((b) => b.cot === 3)
  const bi = KHE.filter((k) => k.hien_thi === 'can_nguoi')
  trang.innerHTML = dauTrang('Phê duyệt', 'Việc chờ Đại ca, sắp theo độ gấp. Duyệt / Trả về ghi thẳng vào beads với tác nhân dai-ca/dashboard.') +
    `<h2 class="muc">Hệ cần xem <span class="so">${HE_CAN_XEM.length}</span></h2>
    <div class="ds-duyet">${HE_CAN_XEM.map((h) => `<article class="the the-duyet he"><div>
      <div class="tren"><span class="chip tt-cau_dao">cầu dao</span><span class="chip">_tram</span></div>
      <div class="tieu-de">${esc(h.tieu_de)}</div><div class="nho">${esc(h.chi_tiet)}</div></div>
      <div class="hanh-dong"><a class="nut" href="${h.lien_ket}" style="display:inline-flex;align-items:center;text-decoration:none">${h.nhan_lk}</a></div></article>`).join('')}</div>
    <h2 class="muc">Bí / escalation <span class="so">${bi.length}</span></h2>
    <div class="ds-duyet">${bi.map((k) => `<article class="the the-duyet"><div>
      <div class="tren"><span class="ma">${k.bead.id}</span><span class="chip">${k.bead.du_an}</span><span class="chip tt-can_nguoi">${k.ten} hỏi · ${TEN_BUOC[k.bead.buoc]}</span></div>
      <div class="tieu-de">${esc(k.bead.tieu_de)}</div><div class="nho">Tính thuế trên giá trước hay sau chiết khấu? Làm tròn theo dòng hay theo tổng?</div></div>
      <div class="hanh-dong"><a class="nut chinh" href="#/cong-viec?du_an=${k.bead.du_an}&bead=${k.bead.id}" style="display:inline-flex;align-items:center;text-decoration:none">Trả lời</a></div></article>`).join('')}</div>
    <h2 class="muc">Chờ review để đóng <span class="so">${review.length}</span></h2>
    <div class="ds-duyet">${review.map(theReview).join('')}</div>`
  for (const b of trang.querySelectorAll('[data-tra-ve]')) {
    b.onclick = () => { const g = b.closest('.the-duyet').querySelector('.gop-y'); g.hidden = !g.hidden; if (!g.hidden) g.querySelector('textarea').focus() }
  }
}

// ---------- Dự án ----------
export function veDuAn(trang) {
  trang.innerHTML = dauTrang('Dự án', 'Các dự án đã thêm vào trạm: số bead mỗi cột, lần quét cuối, lỗi gần nhất.') +
    `<div class="ds-phong">${DU_AN.map((d) => {
      const ds = BEAD.filter((b) => b.du_an === d.ma)
      const dem = [1, 2, 3].map((c) => ds.filter((b) => b.cot === c).length)
      return `<a class="the the-phong${d.tam_dong ? ' mo' : ''}" href="#/cong-viec?du_an=${d.ma}" style="text-decoration:none;color:inherit;border-left-color:var(--nhan)">
        <div class="dau"><strong>${d.ten}</strong><span class="nho">${d.tam_dong ? 'tạm đóng' : 'quét cuối 22:14'}</span></div>
        <div class="ds-nv"><span class="chip">1 · ${dem[0]}</span><span class="chip">2 · ${dem[1]}</span><span class="chip">3 · ${dem[2]}</span></div>
        <div class="nho">Lỗi gần nhất: không có</div></a>`
    }).join('')}</div>`
}

// ---------- Chỗ chờ chốt ----------
export function veChoChot(ten, mota, chuaCoSpec) {
  return (trang) => {
    trang.innerHTML = dauTrang(ten, mota) + `<div class="cho-chot"><strong>${ten}</strong>
      ${chuaCoSpec ? '(chưa có trong spec — chờ Đại ca chốt)' : 'Đã có trong spec; mockup đợt này chưa vẽ chi tiết trang này.'}</div>`
  }
}
