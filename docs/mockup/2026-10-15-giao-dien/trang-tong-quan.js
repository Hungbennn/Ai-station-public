// Trang Tổng quan (D17) — trang mở đầu, chỉ đọc, dữ liệu giả khớp du-lieu.js.
import { BEAD, DU_AN, KHE, HE_CAN_XEM, NHAN_TRANG_THAI, DICH_VU, TRAM, VIEC_MOI_XONG, USAGE_HOM_NAY, SU_KIEN } from './du-lieu.js'
import { esc, chibi } from './chung.js'

const dem = (f) => BEAD.filter(f).length

function khoiViecCho() {
  const muc = [
    ['Cần Đại ca chốt', dem((b) => b.cot === 2), 'cột 2 · có câu hỏi', '#/cong-viec', 'tt-can_nguoi'],
    ['Chờ review để đóng', dem((b) => b.cot === 3), 'cột 3 · 1 PR không xác minh được', '#/phe-duyet', 'tt-cau_dao'],
    ['Escalation bí', KHE.filter((k) => k.hien_thi === 'can_nguoi').length, 'codex-1 hỏi ở hr-3', '#/phe-duyet', 'tt-can_nguoi'],
    ['Spec chờ duyệt', 0, 'chưa có', '#/phe-duyet', ''],
    ['Hệ cần xem', HE_CAN_XEM.length, 'cầu dao claude-4', '#/phe-duyet', 'tt-cau_dao'],
  ]
  const tong = muc.reduce((s, m) => s + (m[0] === 'Hệ cần xem' ? 0 : m[1]), 0)
  return `<section class="the tq-cho">
    <div class="tq-dau"><h2>Việc chờ Đại ca</h2><span class="tq-tong">${tong}</span><span class="nho">sắp theo độ gấp</span>
      <a class="nut chinh" href="#/phe-duyet" style="margin-left:auto;display:inline-flex;align-items:center;text-decoration:none">Mở Phê duyệt</a></div>
    <div class="tq-o-cho">${muc.map(([ten, so, phu, lk, lop]) => `<a class="tq-o ${so ? '' : 'rong'}" href="${lk}">
      <span class="so ${so ? lop : ''}">${so}</span><strong>${ten}</strong><span class="nho">${phu}</span></a>`).join('')}</div>
  </section>`
}

function khoiSucKhoe() {
  const ngat = KHE.filter((k) => k.trang_thai === 'cau_dao')
  const dong = (ten, gt, lop) => `<li><span>${ten}</span><span class="chip ${lop}">${gt}</span></li>`
  return `<section class="the">
    <h3 class="tq-h">Sức khoẻ trạm</h3>
    <ul class="tq-ds">${DICH_VU.map((d) => `<li><span class="mono">${d.ten}</span><span class="nho">${d.mo_ta}</span>
      <span class="chip ${d.chay ? 'tt-lam' : d.cai ? 'tt-can_nguoi' : 'tt-tat'}">${d.chay ? 'chạy' : d.cai ? 'dừng' : 'chưa cài'}</span></li>`).join('')}</ul>
    <ul class="tq-ds tq-ds2">
      ${dong('Quét cuối', `${TRAM.quet_cuoi} · ${TRAM.quet_cach}`, 'tt-lam')}
      ${dong('Estop', TRAM.estop ? 'đang bật' : 'tắt', TRAM.estop ? 'tt-can_nguoi' : 'tt-lam')}
      ${dong('Lỗi memory', TRAM.loi_nho ?? 'không', TRAM.loi_nho ? 'tt-can_nguoi' : 'tt-lam')}
      ${dong('Cầu dao khe', ngat.length ? `${ngat.length} ngắt · ${ngat.map((k) => k.id).join(', ')}` : 'không', ngat.length ? 'tt-cau_dao' : 'tt-lam')}
    </ul>
  </section>`
}

function khoiDoiNgu() {
  const nhom = Object.keys(NHAN_TRANG_THAI).map((tt) => [tt, KHE.filter((k) => k.trang_thai === tt).length]).filter(([, n]) => n)
  const coHm = KHE.filter((k) => k.han_muc)
  const thap = coHm.reduce((a, k) => (k.han_muc.gio5 < a.han_muc.gio5 ? k : a), coHm[0])
  return `<section class="the">
    <h3 class="tq-h">Đội ngũ <a class="nho" href="#/doi-ngu" style="margin-left:auto">Mở Đội ngũ AI →</a></h3>
    <div class="tq-chibi">${KHE.map((k) => `<a href="#/doi-ngu" title="${k.ten} · ${NHAN_TRANG_THAI[k.trang_thai]}">${chibi(k)}<span>${k.ten}</span></a>`).join('')}</div>
    <div class="tq-chip">${nhom.map(([tt, n]) => `<span class="chip tt-${tt}">${NHAN_TRANG_THAI[tt]} · ${n}</span>`).join('')}</div>
    <p class="tq-thap">Hạn mức thấp nhất: <b>${thap.ten}</b> — 5 giờ còn <b>${thap.han_muc.gio5}%</b>, reset ${thap.han_muc.reset5}</p>
  </section>`
}

function khoiDuAn() {
  return `<section class="the">
    <h3 class="tq-h">Theo dự án</h3>
    <table class="bang"><thead><tr><th>Dự án</th><th>1 · AI làm</th><th>2 · Cần chốt</th><th>3 · Chờ review</th><th>Mới xong</th></tr></thead>
    <tbody>${DU_AN.map((d) => {
      const c = [1, 2, 3].map((n) => dem((b) => b.du_an === d.ma && b.cot === n))
      const xong = VIEC_MOI_XONG[d.ma]
      return `<tr${d.tam_dong ? ' style="opacity:.55"' : ''}><th><a href="#/cong-viec?du_an=${d.ma}">${d.ten}</a>${d.tam_dong ? ' <span class="chip">tạm đóng</span>' : ''}</th>
        ${c.map((n) => `<td class="so">${n || '<span class="nho">0</span>'}</td>`).join('')}
        <td>${xong ? `<span class="mono" style="color:var(--nhan)">${xong.id}</span> ${esc(xong.tieu_de)} <span class="nho">· ${xong.luc}</span>` : '<span class="nho">—</span>'}</td></tr>`
    }).join('')}</tbody></table>
  </section>`
}

function khoiUsage() {
  const u = USAGE_HOM_NAY
  const max = Math.max(...u.theo_khe.map(([, v]) => v))
  return `<section class="the">
    <h3 class="tq-h">Usage hôm nay <a class="nho" href="#/usage" style="margin-left:auto">Chi tiết →</a></h3>
    <div class="tq-so">
      <div><b>${u.token_vao}</b><span class="nho">token vào</span></div>
      <div><b>${u.token_ra}</b><span class="nho">token ra</span></div>
      <div><b>$${u.usd_khe.toFixed(2)}</b><span class="nho">khe · tương đương</span></div>
      <div><b>$${u.usd_api.toFixed(2)}</b><span class="nho">Claude API chấm cột</span></div>
    </div>
    <div class="tq-cot">${u.theo_khe.map(([k, v]) => `<div><span class="mono">${k}</span><i style="width:${(v / max) * 100}%"></i><span>$${v.toFixed(2)}</span></div>`).join('')}</div>
    <p class="nho" style="margin:8px 0 0">${u.luot} lượt chạy · giá của khe thuê bao chỉ là tương đương, không phải tiền trả thêm.</p>
  </section>`
}

function khoiSuKien() {
  return `<section class="the">
    <h3 class="tq-h">Sự kiện gần đây <span class="nho" style="font-weight:400">${SU_KIEN.length} dòng mới nhất</span></h3>
    <table class="bang tq-sk"><tbody>${SU_KIEN.map(([gio, loai, du_an, bead, mo_ta]) => `<tr>
      <td class="mono nho">${gio}</td><td><span class="chip mono">${loai}</span></td><td>${du_an}</td>
      <td>${bead ? `<a class="mono" href="#/cong-viec?du_an=${du_an}&bead=${bead}">${bead}</a>` : '<span class="nho">—</span>'}</td>
      <td class="nho">${esc(mo_ta)}</td></tr>`).join('')}</tbody></table>
  </section>`
}

export function veTongQuan(trang) {
  trang.innerHTML = `<div class="dau-trang"><div><h1>Tổng quan</h1>
      <p>Bức tranh chung của trạm trong một màn. Chỉ đọc; bấm vào từng mục để sang trang xử lý.</p></div>
      <div class="cong-cu"><span class="nho">cập nhật 22:17</span></div></div>
    ${khoiViecCho()}
    <div class="tq-luoi">${khoiSucKhoe()}${khoiDoiNgu()}</div>
    <div class="tq-luoi tq-luoi-2">${khoiDuAn()}${khoiUsage()}</div>
    ${khoiSuKien()}`
}
