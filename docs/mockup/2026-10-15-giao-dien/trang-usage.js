// Trang Usage & chi phí (D36) — giữ đủ chức năng của frontend/src/trang/Usage.vue + BangUsage.vue.
// Dữ liệu: GET /api/usage?so_ngay=1–92 → tu, den, theo_ngay, theo_tuan, theo_nguon, theo_du_an (mỗi dòng
// {khoa, token_vao, token_ra, token_cache_doc, token_cache_ghi, so_lan, chi_phi_usd, thieu_gia}), co_bang_gia,
// ccusage {trang_thai, theo_ngay, loi, phien_ban}. Khối hạn mức đọc GET /api/doi-ngu (khe[].han_muc, muc_han_muc).
// Ô số tổng, biểu đồ, cột tỉ trọng: trình duyệt tự cộng từ các mảng trên, không cần API mới.
import { DONG_USAGE, HOM_NAY, congNgay, CCUSAGE, MUC_HAN_MUC } from './du-lieu-ky-uc-usage.js'
import { KHE } from './du-lieu.js'
import { esc } from './chung.js'

const SO_NGAY = [7, 14, 30, 92]
const TRUONG = ['token_vao', 'token_ra', 'token_cache_doc', 'token_cache_ghi']
const so = (n) => (typeof n === 'number' ? n.toLocaleString('vi-VN') : '—')
const usd = (x) => (typeof x !== 'number' ? 'chưa có giá' : `$${x < 1 ? x.toFixed(4) : x.toFixed(2)}`)
const gon = (n) => n >= 1e9 ? `${(n / 1e9).toFixed(2).replace('.', ',')} tỷ` : n >= 1e6 ? `${(n / 1e6).toFixed(2).replace('.', ',')} tr`
  : n >= 1e3 ? `${Math.round(n / 1e3)} n` : String(n)
const ngayNgan = (iso) => `${iso.slice(8, 10)}/${iso.slice(5, 7)}`

function isoTuan(iso) {
  const d = new Date(`${iso}T00:00:00Z`)
  const t = (d.getUTCDay() + 6) % 7
  d.setUTCDate(d.getUTCDate() - t + 3)
  const nam = d.getUTCFullYear()
  const dau = new Date(Date.UTC(nam, 0, 4))
  const tuan = 1 + Math.round(((d - dau) / 864e5 - 3 + ((dau.getUTCDay() + 6) % 7)) / 7)
  return `${nam}-W${String(tuan).padStart(2, '0')}`
}

// Bản sao tram/usage/su_kien.py::tong_hop (chỉ để dữ liệu giả có hình đúng như API trả).
function tongHop(dong, coGia) {
  const nhom = { theo_ngay: {}, theo_tuan: {}, theo_nguon: {}, theo_du_an: {} }
  for (const d of dong) {
    for (const [ten, khoa] of [['theo_ngay', d.ngay], ['theo_tuan', isoTuan(d.ngay)], ['theo_nguon', d.nguon], ['theo_du_an', d.du_an]]) {
      const x = nhom[ten][khoa] ??= { khoa, token_vao: 0, token_ra: 0, token_cache_doc: 0, token_cache_ghi: 0, so_lan: 0, chi_phi_usd: 0, thieu_gia: 0 }
      for (const t of TRUONG) x[t] += d[t]
      x.so_lan += d.so_lan
      if (d.chi_phi == null || !coGia) x.thieu_gia += d.so_lan; else x.chi_phi_usd += d.chi_phi
    }
  }
  const ra = {}
  for (const [ten, bang] of Object.entries(nhom)) {
    ra[ten] = Object.values(bang).sort((a, b) => a.khoa.localeCompare(b.khoa))
      .map((v) => ({ ...v, chi_phi_usd: v.thieu_gia === v.so_lan ? null : Math.round(v.chi_phi_usd * 1e4) / 1e4 }))
  }
  return ra
}

function ccusageTheoNgay(dong) {
  const m = {}
  for (const d of dong.filter((x) => x.nguon.includes('claude'))) {
    const x = m[d.ngay] ??= { khoa: d.ngay, token_vao: 0, token_ra: 0, token_cache_doc: 0, token_cache_ghi: 0, chi_phi_usd: 0 }
    for (const t of TRUONG) x[t] += Math.round(d[t] * CCUSAGE.he_so)
    x.chi_phi_usd += (d.chi_phi ?? 0) * CCUSAGE.he_so
  }
  return Object.values(m).sort((a, b) => b.khoa.localeCompare(a.khoa)).map((x) => ({ ...x, chi_phi_usd: Math.round(x.chi_phi_usd * 1e4) / 1e4 }))
}

const khe = (khoa) => KHE.find((k) => `${k.may}/${k.id}` === khoa)
const tenNguon = (khoa) => khoa === 'cham-cot' ? '<span class="cham" style="background:var(--xam)"></span>Bộ chấm cột (Claude API)'
  : `<span class="cham" style="background:${khe(khoa)?.mau ?? 'var(--xam)'}"></span><span class="mono">${esc(khoa)}</span>`

function bang(tenKhoa, dong, { laNguon = false, coSoLan = true, tiTrong = false, cuon = false } = {}) {
  if (!dong.length) return '<p class="nho">Không có số liệu trong khoảng này.</p>'
  const tong = dong.reduce((s, d) => s + (d.chi_phi_usd ?? 0), 0) || 1
  return `<div class="us-bang${cuon ? ' cuon' : ''}"><table class="bang"><thead><tr><th>${tenKhoa}</th><th>Token vào</th><th>Token ra</th>
    <th>Cache đọc</th><th>Cache ghi</th>${coSoLan ? '<th>Lần gọi</th>' : ''}<th>Chi phí</th>${tiTrong ? '<th style="width:90px">Tỉ trọng</th>' : ''}</tr></thead>
    <tbody>${dong.map((d) => `<tr><th>${laNguon ? tenNguon(d.khoa) : `<span class="mono">${esc(d.khoa)}</span>`}</th>
      ${TRUONG.map((t) => `<td class="so" title="${so(d[t])}">${gon(d[t])}</td>`).join('')}${coSoLan ? `<td class="so">${so(d.so_lan)}</td>` : ''}
      <td class="so">${usd(d.chi_phi_usd)}${d.thieu_gia && d.chi_phi_usd != null ? `<span class="us-thieu" title="${d.thieu_gia} lần gọi chưa có giá — không tính vào chi phí">${d.thieu_gia} thiếu giá</span>` : ''}</td>
      ${tiTrong ? `<td><div class="thanh-hm us-tt"><i style="width:${Math.max(2, ((d.chi_phi_usd ?? 0) / tong) * 100)}%"></i></div></td>` : ''}</tr>`).join('')}</tbody></table></div>`
}

function bieuDo(theoNgay, tu, che) {
  const m = Object.fromEntries(theoNgay.map((d) => [d.khoa, d]))
  const ngay = []
  for (let n = tu; n <= HOM_NAY; n = congNgay(n, 1)) ngay.push(n)
  const gt = (d) => (!d ? 0 : che === 'chi_phi' ? d.chi_phi_usd ?? 0 : d.token_vao + d.token_ra)
  const buoc = che === 'chi_phi' ? [1, 2, 5, 10, 20, 50] : [1e5, 2e5, 5e5, 1e6, 2e6, 5e6]
  const lon = Math.max(...ngay.map((n) => gt(m[n])), 0.01)
  const tran = (buoc.find((b) => b * 4 >= lon) ?? buoc.at(-1)) * 4
  const nhan = (v) => che === 'chi_phi' ? `$${v % 1 ? v.toFixed(1) : v}` : gon(v)
  const moc = Math.max(1, Math.ceil(ngay.length / 10))
  return `<div class="us-bd" style="--so-cot:${ngay.length}">
    <div class="us-truc">${[4, 3, 2, 1, 0].map((i) => `<span>${nhan((tran * i) / 4)}</span>`).join('')}</div>
    <div class="us-vung">${[1, 2, 3, 4].map((i) => `<i class="us-ke" style="bottom:${i * 25}%"></i>`).join('')}
      ${ngay.map((n, i) => { const d = m[n]; const v = gt(d)
        return `<div class="us-cot${n === HOM_NAY ? ' nay' : ''}" tabindex="0"><b style="height:${(v / tran) * 100}%"></b>
          <span class="us-tip"><strong>${ngayNgan(n)}${n === HOM_NAY ? ' · hôm nay' : ''}</strong>${d ? `${usd(d.chi_phi_usd)} · ${so(d.so_lan)} lần<br>${gon(d.token_vao)} vào · ${gon(d.token_ra)} ra` : 'không có sự kiện'}</span>
          ${i % moc === 0 || n === HOM_NAY ? `<em>${ngayNgan(n)}</em>` : ''}</div>` }).join('')}</div></div>`
}

const NHAN_MUC = { ok: ['Nhận việc', 'tt-lam'], ngung: ['Ngừng — chạm ngưỡng', 'tt-can_nguoi'],
  chi_p0_p1: ['Chỉ P0–P1 — tuần cao', 'tt-cau_dao'], chua_biet: ['Chưa biết — vẫn nhận việc', 'tt-cau_dao'] }
function thanh(con, reset) {
  if (con == null) return '<div class="thanh-hm"></div><span class="nho">chưa biết</span>'
  const lop = con === 0 ? 'het' : con < 30 ? 'thap' : ''
  return `<div class="thanh-hm"><i class="${lop}" style="width:${Math.max(con, 2)}%"></i></div><span>còn ${con}% · ${reset}</span>`
}
function khoiHanMuc() {
  return `<section class="the"><h3 class="tq-h">Hạn mức thuê bao của khe <span class="nho" style="font-weight:400">từ <span class="mono">/api/doi-ngu</span> · đọc mỗi 5 giây</span>
      <a class="nho" href="#/doi-ngu" style="margin-left:auto">Mở Đội ngũ AI →</a></h3>
    <table class="bang us-hm"><thead><tr><th>Khe</th><th>Cửa sổ 5 giờ</th><th>Cửa sổ tuần</th><th>Luật nhận việc</th></tr></thead><tbody>
    ${KHE.map((k) => { const hm = k.han_muc; const [ten, lop] = NHAN_MUC[MUC_HAN_MUC[k.id]]
      return `<tr><th>${tenNguon(`${k.may}/${k.id}`)}</th><td><div class="us-o-hm">${thanh(hm?.gio5, hm ? `reset ${hm.reset5}` : '')}</div></td>
        <td><div class="us-o-hm">${thanh(hm?.tuan, hm ? `reset ${hm.resetTuan}` : '')}</div></td><td><span class="chip ${lop}">${ten}</span></td></tr>` }).join('')}
    </tbody></table>
    <p class="nho" style="margin:8px 0 0">Đã dùng ≥ 90% một cửa sổ thì khe ngừng nhận việc; tuần cao chỉ nhận P0–P1; chưa biết vẫn nhận việc kèm cảnh báo vàng. Giá trên trang này là tương đương — hạn mức mới là giới hạn thật của khe thuê bao.</p>
  </section>`
}

function khoiCcusage(tt, dong) {
  const than = tt === 'chua_cau_hinh'
    ? '<p class="nho">Chưa cấu hình ccusage (<span class="mono">usage.ccusage</span> trong <span class="mono">~/.tram/cau-hinh.yaml</span>).</p>'
    : tt === 'loi' ? `<div class="canh-bao">Phiên bản ccusage lệch (cần ${CCUSAGE.phien_ban}, thấy 16.3.1) — không chạy</div>`
      : `<p class="nho">ccusage ${CCUSAGE.phien_ban} — số liệu giữ tối đa 10 phút. Gồm cả phiên Claude Code không do khe chạy, nên lớn hơn dòng khe ở trên.</p>
        ${bang('Ngày', dong, { coSoLan: false, cuon: true })}`
  return `<section class="the"><h3 class="tq-h">ccusage — toàn bộ Claude Code của tài khoản trạm trên máy B
      <div class="nhom-nut" role="group" aria-label="Minh hoạ trạng thái ccusage" style="margin-left:auto">${[['ok', 'có số liệu'], ['chua_cau_hinh', 'chưa cấu hình'], ['loi', 'lỗi']].map(([m, t]) =>
        `<button type="button" data-cc="${m}" class="${m === tt ? 'chon' : ''}">${t}</button>`).join('')}</div></h3>${than}</section>`
}

export function veUsage(trang) {
  const s = { soNgay: 14, che: 'chi_phi', cc: 'ok', coGia: true }
  function ve() {
    const tu = congNgay(HOM_NAY, -(s.soNgay - 1))
    const dong = DONG_USAGE.filter((d) => d.ngay >= tu)
    const dl = tongHop(dong, s.coGia)
    const t = Object.fromEntries([...TRUONG, 'so_lan', 'thieu_gia'].map((k) => [k, dl.theo_ngay.reduce((a, d) => a + d[k], 0)]))
    const cp = dl.theo_ngay.reduce((a, d) => a + (d.chi_phi_usd ?? 0), 0)
    const cham = dl.theo_nguon.find((d) => d.khoa === 'cham-cot')
    const o = (gt, ten, phu, tieuDe = '') => `<div title="${tieuDe}"><b>${gt}</b><span class="nho">${ten}</span>${phu ? `<span class="nho us-phu">${phu}</span>` : ''}</div>`
    trang.innerHTML = `<div class="dau-trang"><div><h1>Usage & chi phí</h1>
        <p>Token và chi phí từ sự kiện của trạm: mỗi lần chạy CLI của khe và mỗi lần bộ chấm cột gọi Claude API. Ngày theo giờ Việt Nam, tuần theo ISO.</p></div>
      <div class="cong-cu"><span class="nho">Từ ${ngayNgan(tu)} đến ${ngayNgan(HOM_NAY)}/2026</span>
        <div class="nhom-nut" role="group" aria-label="Khoảng">${SO_NGAY.map((n) => `<button type="button" data-n="${n}" class="${n === s.soNgay ? 'chon' : ''}">${n} ngày</button>`).join('')}</div></div></div>
      <p class="nho us-ghi"><span>Chi phí của khe (gói thuê bao) là <b>giá tương đương</b> theo bảng giá, không phải tiền trả thêm; chỉ bộ chấm cột là tiền API thật.</span>
        <label class="us-mh"><input type="checkbox" id="us-gia" ${s.coGia ? '' : 'checked'}> minh hoạ: chưa có bảng giá</label></p>
      ${s.coGia ? '' : '<div class="canh-bao" style="margin-bottom:14px">Chưa có bảng giá (<span class="mono">usage.gia_usd_moi_trieu_token</span>) — chi phí để trống.</div>'}
      <div class="tq-so us-so">
        ${o(gon(t.token_vao), 'token vào', '', so(t.token_vao))}${o(gon(t.token_ra), 'token ra', '', so(t.token_ra))}
        ${o(gon(t.token_cache_doc), 'cache đọc', '', so(t.token_cache_doc))}${o(gon(t.token_cache_ghi), 'cache ghi', '', so(t.token_cache_ghi))}
        ${o(so(t.so_lan), 'lần gọi', `${so(t.so_lan - (cham?.so_lan ?? 0))} khe · ${so(cham?.so_lan ?? 0)} chấm cột`)}
        ${o(s.coGia ? `$${cp.toFixed(2)}` : '—', 'chi phí ước tính', s.coGia ? `API thật ${usd(cham?.chi_phi_usd)}${t.thieu_gia ? ` · ${t.thieu_gia} lần thiếu giá` : ''}` : 'chưa có giá')}
      </div>
      <section class="the us-the-bd"><h3 class="tq-h">Theo ngày
        <div class="nhom-nut" role="group" aria-label="Đại lượng" style="margin-left:auto">${[['chi_phi', 'Chi phí'], ['token', 'Token vào + ra']].map(([m, ten]) =>
          `<button type="button" data-che="${m}" class="${m === s.che ? 'chon' : ''}">${ten}</button>`).join('')}</div></h3>
        ${bieuDo(dl.theo_ngay, tu, s.coGia ? s.che : 'token')}</section>
      <section class="the us-khoi"><h3 class="tq-h">Theo khe / nguồn</h3>${bang('Khe / nguồn', dl.theo_nguon, { laNguon: true, tiTrong: true })}</section>
      <div class="tq-luoi us-luoi">
        <section class="the"><h3 class="tq-h">Theo dự án</h3>${bang('Dự án', dl.theo_du_an)}</section>
        <section class="the"><h3 class="tq-h">Theo tuần</h3>${bang('Tuần (ISO)', [...dl.theo_tuan].reverse())}</section>
      </div>
      <section class="the us-khoi"><h3 class="tq-h">Theo ngày <span class="nho" style="font-weight:400">${dl.theo_ngay.length} ngày có sự kiện · mới nhất trước</span></h3>${bang('Ngày', [...dl.theo_ngay].reverse(), { cuon: true })}</section>
      ${khoiHanMuc()}
      <div style="height:16px"></div>
      ${khoiCcusage(s.cc, ccusageTheoNgay(dong))}`
    for (const b of trang.querySelectorAll('[data-n]')) b.onclick = () => { s.soNgay = +b.dataset.n; ve() }
    for (const b of trang.querySelectorAll('[data-che]')) b.onclick = () => { s.che = b.dataset.che; ve() }
    for (const b of trang.querySelectorAll('[data-cc]')) b.onclick = () => { s.cc = b.dataset.cc; ve() }
    trang.querySelector('#us-gia').onchange = (e) => { s.coGia = !e.target.checked; ve() }
  }
  ve()
}
