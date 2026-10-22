// Trang tự merge · tự deploy của một dự án (#/du-an/<ma>). Trái: trạng thái; phải: bộ đếm hỏng + cài đặt.
// Mockup: mọi nút chỉ đổi giao diện. Bản thật: mỗi nút ghi đi qua cửa ghi có xác thực + mã thao tác (spec dieu-khien-tu-dong).
import { esc, moNganBen } from '../2026-10-15-giao-dien/chung.js'
import { CAP_NHAT, DIEU_KIEN, DU_AN, LENH, LOAI_SU_KIEN } from './du-lieu.js'
import { layDuAn, trangThaiTram } from './trang-thai.js'
import { chipTuDong } from './trang-du-an.js'

const TINH_HUONG = [
  ['binh-thuong', 'Bình thường'], ['tu-tat', 'Hỏng 3 lần → tự tắt'], ['lui-hong', 'Lùi cũng hỏng'],
  ['cua-tam', 'Cửa ghi còn tạm (câu hỏi mở 1)'],
]
const O_KHOA = '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/></svg>'
const IC_TAM_DUNG = '<svg class="dac" viewBox="0 0 24 24" aria-hidden="true"><rect x="6" y="5" width="4" height="14" rx="1"/><rect x="14" y="5" width="4" height="14" rx="1"/></svg>'

const congTac = (id, bat, khoa, nhan) =>
  `<button type="button" class="cong-tac" role="switch" id="${id}" aria-checked="${bat}" aria-label="${esc(nhan)}"${khoa ? ' disabled' : ''}></button>`
const duLenh = (s) => LENH.every((l) => s.lenh[l.ma].trim())

export function veTuDong(trang, ma, q, veLai) {
  const d = DU_AN.find((x) => x.ma === ma)
  if (!d) { trang.innerHTML = '<div class="cho-chot"><strong>Không có dự án này</strong></div>'; return }
  const th = ma === 'repo-nhap' ? (q.get('th') || 'binh-thuong') : 'binh-thuong'
  const s = layDuAn(ma, th === 'cua-tam' ? 'binh-thuong' : th)
  const khoaGhi = !d.bat_ghi || th === 'cua-tam'          // khoá mọi nút ghi trừ TẠM DỪNG
  const dangSua = trang.dataset.suaLenh === ma || q.get('sua') === '1'      // ?sua=1: mở sẵn ô sửa (ảnh chụp)

  const thanhTH = ma !== 'repo-nhap' ? '' : `<div class="th-mockup"><span class="nho">Tình huống (chỉ có trong mockup):</span>
    <div class="nhom-nut">${TINH_HUONG.map(([k, t]) =>
      `<button type="button" data-th="${k}" class="${k === th ? 'chon' : ''}">${t}</button>`).join('')}</div></div>`

  trang.innerHTML = `<div class="dau-trang"><div>
      <div class="duong-dan"><a href="#/du-an">Dự án</a> / ${esc(d.ten)}</div>
      <h1>${esc(d.ten)} · Tự động</h1>
      <p>Tự merge, tự deploy và agent tự cập nhật việc của dự án này. Mỗi nút ở đây ghi qua cửa ghi có xác thực như các nút khác của dashboard.</p></div>
      <div class="cong-cu">${chipTuDong(d, s)}
        <button type="button" class="nut-estop vang${s.tam_dung ? ' bat' : ''}" id="nut-tam-dung-da">${IC_TAM_DUNG}
          <span>${s.tam_dung ? 'Dự án đang tạm dừng' : 'Tạm dừng dự án'}</span></button></div></div>
    ${thanhTH}${veBao(d, s, th)}
    <div class="td-luoi">
      <div class="td-cot">${veSanSang(s, khoaGhi)}${veCho(s)}${veLichSu(s)}</div>
      <div class="td-cot">${veDemHong(s)}${veCaiDat(d, s, khoaGhi, dangSua)}${veCapNhat(s, khoaGhi)}</div>
    </div>`

  // ---- Sự kiện ----
  for (const b of trang.querySelectorAll('[data-th]')) {
    b.onclick = () => { location.hash = `#/du-an/${ma}?th=${b.dataset.th}` }
  }
  const tamDung = () => {
    if (s.tam_dung) { s.tam_dung = null; s.lui_hong = false; return veLai() }
    if (confirm(`Tạm dừng tự merge và tự deploy của ${d.ten}? Cài đặt giữ nguyên; bấm Tiếp tục để chạy lại.`)) {
      s.tam_dung = { boi: 'Đại ca', luc: 'bây giờ' }; veLai()
    }
  }
  trang.querySelector('#nut-tam-dung-da').onclick = tamDung
  trang.querySelector('#nut-tiep-tuc-da')?.addEventListener('click', tamDung)
  trang.querySelector('#nut-deploy')?.addEventListener('click', () => {
    if (!confirm(`Deploy bản ${s.san_sang.commit} của ${d.ten} lên cho khách dùng?\nTrạm chạy lệnh deploy rồi lệnh kiểm còn sống; hỏng thì tự lùi.`)) return
    const btn = trang.querySelector('#nut-deploy')
    btn.disabled = true; btn.textContent = 'Đang deploy…'
    setTimeout(() => {
      s.lich_su.unshift(['22:20', 'deploy_dat', '—', s.san_sang.commit, 'deploy 51 giây · kiểm còn sống 2 giây', 'Đại ca bấm'])
      s.san_sang = null; s.dem_hong = 0; veLai()
    }, 1600)
  })
  const ganCongTac = (id, lam) => trang.querySelector(`#${id}`)?.addEventListener('click', lam)
  ganCongTac('ct-tu-merge', () => {
    if (!s.tu_merge && !confirm(`Bật tự merge cho ${d.ten}? Trạm sẽ tự gộp PR vào nhánh chính khi đủ mọi điều kiện, không chờ Đại ca.`)) return
    s.tu_merge = !s.tu_merge; veLai()
  })
  ganCongTac('ct-tu-deploy', () => {
    if (!s.tu_deploy && !confirm('Trạm sẽ tự đưa bản mới lên cho khách dùng, không chờ Đại ca. Bật?')) return
    s.tu_deploy = !s.tu_deploy
    if (s.tu_deploy) { s.dem_hong = 0; s.tu_tat = null }
    veLai()
  })
  for (const dk of DIEU_KIEN.filter((x) => !x.khoa)) {
    ganCongTac(`ct-${dk.ma}`, () => {
      if (s.dieu_kien[dk.ma] && !confirm(`Tắt điều kiện "${dk.ten}"? Trạm sẽ tự merge cả việc không đạt điều kiện này.`)) return
      s.dieu_kien[dk.ma] = !s.dieu_kien[dk.ma]; veLai()
    })
  }
  ganCongTac('ct-cap-nhat', () => {
    if (!s.cap_nhat.bat && !confirm(`Cho agent tự cập nhật việc của ${d.ten}? Agent chỉ gửi đề nghị; trạm kiểm rồi mới ghi.`)) return
    s.cap_nhat.bat = !s.cap_nhat.bat; veLai()
  })
  for (const c of CAP_NHAT) ganCongTac(`ct-cn-${c.ma}`, () => { s.cap_nhat[c.ma] = !s.cap_nhat[c.ma]; veLai() })
  trang.querySelector('#nut-sua-lenh')?.addEventListener('click', () => { trang.dataset.suaLenh = ma; veLai() })
  trang.querySelector('#nut-huy-lenh')?.addEventListener('click', () => { delete trang.dataset.suaLenh; veLai() })
  trang.querySelector('#nut-luu-lenh')?.addEventListener('click', () => {
    const moi = Object.fromEntries(LENH.map((l) => [l.ma, trang.querySelector(`#o-${l.ma}`).value.trim()]))
    const loi = trang.querySelector('#loi-lenh')
    if (Object.values(moi).some((v) => /token|ghp_|sk-|password|mat-khau/i.test(v))) {
      loi.textContent = 'Lệnh có vẻ chứa bí mật — để bí mật ngoài lệnh (máy chủ trả 422, chưa lưu gì).'
      return
    }
    if (!confirm('Lưu 3 lệnh? Lệnh sẽ chạy trên máy B dưới tài khoản trạm.')) return
    s.lenh = moi
    if (!duLenh(s)) s.tu_deploy = false
    s.lich_su_doi.unshift(['bây giờ', 'Sửa 3 lệnh deploy', 'đã lưu'])
    delete trang.dataset.suaLenh; veLai()
  })
  trang.querySelector('#nut-ls-doi')?.addEventListener('click', () => moNganBen(`<h2>Lịch sử đổi cài đặt</h2>
    <p>${esc(d.ten)} · mỗi dòng do Đại ca (dashboard) hoặc trạm ghi; không bao giờ có giá trị bí mật.</p>
    <ul class="dtg">${s.lich_su_doi.map(([gio, viec, doi]) =>
      `<li><span class="mono">${esc(gio)}</span>${esc(viec)} — <span class="nho">${esc(doi)}</span></li>`).join('')}</ul>`))
}

function veBao(d, s, th) {
  const ra = []
  if (!d.bat_ghi) {
    ra.push(`<div class="the td-bao"><strong>Dự án đang chỉ quét thử</strong>
      <p>Khoá ghi <span class="mono">bat_ghi: false</span> — không bật được tự merge hay tự deploy. Đại ca bật ghi bằng tay trong
      <span class="mono">du-an/${esc(d.ma)}.yaml</span> sau các cổng chạy thật. Nút tạm dừng vẫn bấm được.</p></div>`)
  }
  if (th === 'cua-tam') {
    ra.push(`<div class="the td-bao"><strong>Cửa ghi còn tạm — chỉ bấm được TẠM DỪNG</strong>
      <p>Trạm chưa chuyển cửa ghi sang loại chắc chắn (<span class="mono">unix-socket</span>). Lúc này một chương trình trên máy B có thể
      giả là Đại ca, nên mọi nút bật và ô sửa ở đây bị khoá (đề xuất ở câu hỏi mở 1).</p></div>`)
  }
  if (trangThaiTram.estop) {
    ra.push('<div class="the td-bao do"><strong>Estop đang bật</strong><p>Không tự merge, không tự deploy, nút Deploy cũng bị khoá.</p></div>')
  }
  if (s.lui_hong && s.tam_dung) {
    ra.push(`<div class="the td-bao do"><strong>LÙI HỎNG lúc ${esc(s.tam_dung.luc)} — trang của khách có thể đang chết</strong>
      <p>Deploy hỏng, trạm đã chạy lệnh lùi nhưng kiểm còn sống vẫn không đạt. Trạm đã tắt tự deploy và tạm dừng dự án này.
      Telegram đã báo khẩn. Đại ca kiểm trang, sửa tay, rồi bấm Tiếp tục.</p>
      <div class="hang-nut"><button type="button" class="nut" id="nut-tiep-tuc-da">Tiếp tục dự án</button></div></div>`)
  } else if (s.tam_dung) {
    ra.push(`<div class="the td-bao"><strong>Dự án đang tạm dừng</strong>
      <p>${esc(s.tam_dung.boi)} bấm lúc ${esc(s.tam_dung.luc)}. Trạm vẫn giao việc và mở PR, nhưng không tự merge, không tự deploy.
      Cài đặt bên dưới giữ nguyên. Nút Deploy của Đại ca vẫn dùng được.</p>
      <div class="hang-nut"><button type="button" class="nut" id="nut-tiep-tuc-da">Tiếp tục</button></div></div>`)
  }
  if (s.tu_tat) {
    ra.push(`<div class="the td-bao"><strong>Trạm đã tự tắt tự deploy lúc ${esc(s.tu_tat)}</strong>
      <p>Hỏng 3 lần liên tiếp, lần nào cũng đã tự lùi thành công. Tự merge vẫn chạy; bản mới sẽ chờ ở "Sẵn sàng deploy".
      Bật lại tự deploy khi Đại ca đã kiểm — bộ đếm về 0.</p></div>`)
  }
  return ra.join('')
}

function veSanSang(s, khoaGhi) {
  const thieu = !duLenh(s)
  const khoa = khoaGhi || thieu || trangThaiTram.estop
  const lyDo = trangThaiTram.estop ? 'Estop đang bật' : thieu ? 'Chưa khai đủ 3 lệnh' : khoaGhi ? 'Cửa ghi đang khoá' : ''
  const than = s.san_sang
    ? `<div class="ss-hang"><div><div class="tieu-de">Bản <span class="mono">${esc(s.san_sang.commit)}</span> — gồm ${s.san_sang.so} việc đã merge</div>
        <div class="nho">${esc(s.san_sang.viec)} · merge cuối ${esc(s.san_sang.luc)} · bản đang chạy <span class="mono">5d3e8b2</span></div></div>
        <button type="button" class="nut chinh" id="nut-deploy"${khoa ? ' disabled' : ''}>Deploy</button>
        <div class="chu-thich nho">Trạm chạy lệnh deploy → lệnh kiểm còn sống; hỏng thì tự lùi về <span class="mono">5d3e8b2</span> và báo Telegram.${lyDo ? ` <b>${lyDo}.</b>` : ''}</div></div>`
    : '<div class="ss-rong">Không có bản nào chờ deploy.</div>'
  return `<section class="the ss-deploy"><h3 class="td-h">Sẵn sàng deploy
      <span class="nho">${s.tu_deploy ? 'tự deploy đang bật — trạm tự chạy sau mỗi lần merge' : 'tự deploy đang tắt — trạm chờ Đại ca bấm'}</span></h3>${than}</section>`
}

function veCho(s) {
  return `<section class="the"><h3 class="td-h">Chờ Đại ca <span class="chip">${s.cho_dai_ca.length}</span>
      <span class="nho">thiếu điều kiện nên không tự merge — xử lý như hôm nay ở Phê duyệt</span></h3>
    ${s.cho_dai_ca.length ? `<ul class="ds-cho">${s.cho_dai_ca.map((c) => `<li><span class="mono">${esc(c.bead)}</span><span>${esc(c.tieu_de)}</span>
      <span class="ly-do">${c.ly_do.map(([t, lop]) => `<span class="chip ${lop}">${esc(t)}</span>`).join('')}</span></li>`).join('')}</ul>`
      : '<div class="ss-rong">Không có việc nào đang chờ.</div>'}</section>`
}

function veLichSu(s) {
  return `<section class="the"><h3 class="td-h">Lịch sử gần đây <span class="nho">tự merge, deploy, lùi — chỉ mã thoát và thời gian, không có log</span></h3>
    ${s.lich_su.length ? `<div class="bang-cuon"><table class="bang bang-ls"><thead><tr><th>Giờ</th><th>Việc</th><th>Bead</th><th>Commit</th><th>Chi tiết</th><th>Ai</th></tr></thead>
    <tbody>${s.lich_su.map(([gio, loai, bead, commit, chiTiet, ai]) => `<tr><td class="mono">${esc(gio)}</td>
      <td><span class="chip ${LOAI_SU_KIEN[loai][1]}">${LOAI_SU_KIEN[loai][0]}</span></td>
      <td class="mono ma">${esc(bead)}</td><td class="mono">${esc(commit)}</td><td class="nho">${esc(chiTiet)}</td><td class="nho">${esc(ai)}</td></tr>`).join('')}</tbody></table></div>`
      : '<div class="ss-rong">Chưa có lần tự merge hay deploy nào.</div>'}</section>`
}

function veDemHong(s) {
  const den = [0, 1, 2].map((i) => `<span class="den-ss ${i < s.dem_hong ? 'thieu' : 'cho'}"></span>`).join('')
  return `<section class="the"><h3 class="td-h">Deploy hỏng liên tiếp</h3>
    <div class="dem-hong">${den}<b>${s.dem_hong} / 3</b></div>
    <p class="nho">Mỗi lần hỏng trạm tự lùi và báo Telegram. Đủ 3 lần liền thì trạm tự tắt tự deploy. Về 0 khi một lần deploy thành công.</p></section>`
}

function veCaiDat(d, s, khoaGhi, dangSua) {
  const thieu = !duLenh(s)
  const dk = DIEU_KIEN.map((x) => x.khoa
    ? `<div class="cd-hang khoa"><span class="ten">${x.ten}</span><span class="mo-ta">${x.mo_ta}</span>
        <span class="ben-phai chip khoa">${O_KHOA}luôn bật</span></div>`
    : `<div class="cd-hang"><span class="ten">${x.ten}</span><span class="mo-ta">${x.mo_ta}</span>
        <span class="ben-phai">${congTac(`ct-${x.ma}`, s.dieu_kien[x.ma], khoaGhi, x.ten)}</span></div>`).join('')
  const lenh = dangSua
    ? `<div class="lenh-ds">${LENH.map((l) => `<label class="lenh-o"><span class="nhan">${l.ten}<span class="nho">${l.goi_y}</span></span>
        <input class="o" id="o-${l.ma}" value="${esc(s.lenh[l.ma])}" spellcheck="false" autocomplete="off"></label>`).join('')}
        <p class="nho">Mỗi lệnh chạy trên máy B dưới tài khoản trạm, trong bản sạch của nhánh chính, không qua shell. Không dán mật khẩu hay token vào lệnh.</p>
        <div class="lenh-nut"><button type="button" class="nut chinh" id="nut-luu-lenh">Lưu 3 lệnh</button>
          <button type="button" class="nut" id="nut-huy-lenh">Huỷ</button><span class="loi-tai-cho" id="loi-lenh" role="alert"></span></div></div>`
    : `<div class="lenh-ds">${LENH.map((l) => `<div class="lenh-o"><span class="nhan">${l.ten}<span class="nho">${l.goi_y}</span></span>
        ${s.lenh[l.ma] ? `<code>${esc(s.lenh[l.ma])}</code>` : '<code class="trong">chưa khai</code>'}</div>`).join('')}
        <div class="lenh-nut"><button type="button" class="nut" id="nut-sua-lenh"${khoaGhi ? ' disabled' : ''}>Sửa 3 lệnh</button></div></div>`
  return `<section class="the"><h3 class="td-h">Cài đặt</h3>
    <div class="cd-hang chinh"><span class="ten">Tự merge</span>
      <span class="mo-ta">Mặc định tắt. Bật: trạm tự gộp PR của chính nó khi đủ mọi điều kiện dưới đây.</span>
      <span class="ben-phai">${congTac('ct-tu-merge', s.tu_merge, khoaGhi, 'Tự merge')}</span></div>
    <div class="cd-nhom">Điều kiện — thiếu một thì chờ Đại ca</div>${dk}
    <div class="cd-hang khoa"><span class="ten">Cấu trúc DB, xoá dữ liệu</span>
      <span class="mo-ta">Luôn chờ Đại ca, kể cả khi tắt nút hàng rào</span>
      <span class="ben-phai chip tt-loi khoa">${O_KHOA}luôn chờ Đại ca</span></div>
    <div class="cd-nhom">Deploy — 3 lệnh của dự án</div>${lenh}
    <div class="cd-hang chinh"><span class="ten">Tự deploy</span>
      <span class="mo-ta">Mặc định tắt: trạm merge xong thì báo "sẵn sàng deploy" và chờ Đại ca bấm. Bật: trạm tự deploy ngay sau khi merge.${thieu ? ' <b>Chưa khai đủ 3 lệnh.</b>' : ''}</span>
      <span class="ben-phai">${congTac('ct-tu-deploy', s.tu_deploy, khoaGhi || thieu, 'Tự deploy')}</span></div>
    <div class="cd-chan">${s.doi_cuoi ? `Đổi lần cuối: ${esc(s.doi_cuoi[0])} · ${esc(s.doi_cuoi[1])}` : 'Chưa từng đổi — đang dùng mặc định'}
      ${s.lich_su_doi.length ? '<button type="button" id="nut-ls-doi">Xem lịch sử đổi</button>' : ''}</div>
  </section>`
}

function veCapNhat(s, khoaGhi) {
  const cn = s.cap_nhat
  return `<section class="the"><h3 class="td-h">Agent tự cập nhật việc <span class="nho">spec riêng · D81–D86</span></h3>
    <div class="cd-hang chinh"><span class="ten">Cho agent cập nhật việc</span>
      <span class="mo-ta">Mặc định tắt. Agent chỉ gửi đề nghị qua trạm; trạm kiểm đúng việc của phiếu, đúng loại, không có bí mật rồi mới ghi. Agent không đóng việc, không sửa mô tả hay ưu tiên, không đụng việc khác.</span>
      <span class="ben-phai">${congTac('ct-cap-nhat', cn.bat, khoaGhi, 'Cho agent cập nhật việc')}</span></div>
    ${CAP_NHAT.map((c) => `<div class="cd-hang con"><span class="ten">${c.ten}</span><span class="mo-ta">${c.mo_ta}</span>
      <span class="ben-phai">${congTac(`ct-cn-${c.ma}`, cn[c.ma], khoaGhi || !cn.bat, c.ten)}</span></div>`).join('')}
    <div class="cd-chan">Xem trên thẻ việc: <a class="viec-goc" href="#/cong-viec">trang Công việc →</a></div>
  </section>`
}
