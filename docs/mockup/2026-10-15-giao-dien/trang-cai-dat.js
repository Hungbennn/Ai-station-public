// Trang Cài đặt (D19) — CHỈ ĐỌC: không có ô hay nút sửa; mỗi mục kèm lệnh CLI gợi ý (có nút sao chép).
// Keychain chỉ hiện "có / chưa có", không bao giờ hiện giá trị.
import { CAU_HINH_DU_AN, DICH_VU, TELEGRAM, CO, KEYCHAIN, SAN_SANG } from './du-lieu.js'
import { esc } from './chung.js'

const lenh = (cmd, ghiChu = '') => `<div class="lenh"><code>${esc(cmd)}</code>
  <button type="button" class="sao-chep" data-lenh="${esc(cmd)}" title="Sao chép lệnh">Sao chép</button>${ghiChu ? `<span class="nho">${ghiChu}</span>` : ''}</div>`

const khoi = (tieuDe, phu, than, lenhs) => `<section class="the cd-khoi">
  <div class="cd-dau"><h3>${tieuDe}</h3>${phu ? `<span class="nho">${phu}</span>` : ''}</div>${than}
  <div class="cd-lenh"><span class="nho">Sửa bằng CLI:</span>${lenhs.join('')}</div></section>`

const nhanTT = { dat: ['Đạt', 'tt-lam'], thieu: ['Thiếu', 'tt-can_nguoi'], cho: ['Chưa tới lượt', 'tt-tat'] }

function bangSanSang() {
  const dem = (t) => SAN_SANG.filter((d) => d[2] === t).length
  return `<section class="the cd-khoi">
    <div class="cd-dau"><h3>Bảng sẵn sàng chạy thật</h3>
      <span class="nho">theo sổ tay <span class="mono">docs/handovers/2026-10-15-so-tay-chay-that.md</span></span>
      <div class="tq-chip" style="margin-left:auto"><span class="chip tt-lam">${dem('dat')} đạt</span><span class="chip tt-can_nguoi">${dem('thieu')} thiếu</span><span class="chip tt-tat">${dem('cho')} chưa tới lượt</span></div></div>
    <table class="bang"><thead><tr><th style="width:28px"></th><th>Bead</th><th>Bước</th><th>Trạng thái</th><th>Ghi chú</th></tr></thead>
    <tbody>${SAN_SANG.map(([id, ten, tt, ghi]) => `<tr>
      <td><span class="den-ss ${tt}"></span></td><td class="mono" style="color:var(--nhan)">${id}</td><td>${esc(ten)}</td>
      <td><span class="chip ${nhanTT[tt][1]}">${nhanTT[tt][0]}</span></td><td class="nho">${esc(ghi)}</td></tr>`).join('')}</tbody></table>
    <div class="cd-lenh"><span class="nho">Kiểm lại:</span>${lenh('uv run tram giao kiem', 'xanh/vàng/đỏ, mã ≠ 0 nếu có đỏ')}${lenh('bd list --status open --parent bs-8eh')}</div>
  </section>`
}

export function veCaiDat(trang) {
  const duAn = khoi('Dự án đã thêm', `${CAU_HINH_DU_AN.length} dự án · <span class="mono">du-an/*.yaml</span>`,
    `<div class="cd-du-an">${CAU_HINH_DU_AN.map((d) => `<div class="cd-da${d.tam_dong ? ' mo' : ''}">
      <div class="cd-da-dau"><strong>${d.ten}</strong>${d.tam_dong ? '<span class="chip">tạm đóng</span>' : ''}</div>
      <dl>
        <dt>Đường dẫn</dt><dd class="mono">${esc(d.duong_dan)}</dd>
        <dt>Nhánh chính</dt><dd class="mono">${d.nhanh}</dd>
        <dt>GitNexus</dt><dd class="mono">${d.gitnexus ?? '<span class="nho">không</span>'}</dd>
        <dt>Lệnh được phép</dt><dd>${d.lenh.map((l) => `<span class="chip mono">${esc(l)}</span>`).join(' ')}</dd>
        <dt>Hàng rào</dt><dd>${d.hang_rao.map(([loai, tk]) => `<div><span class="chip mono">${loai}</span> <span class="nho">${esc(tk)}</span></div>`).join('')}</dd>
      </dl></div>`).join('')}</div>`,
    [lenh('$EDITOR du-an/hr-codex.yaml', 'sửa khoá rồi chạy lệnh dưới'), lenh('uv run tram du-an them ~/Developer/hr-codex')])

  const dichVu = khoi('Dịch vụ launchd', 'LaunchAgent trong <span class="mono">~/Library/LaunchAgents</span>',
    `<table class="bang"><thead><tr><th>Dịch vụ</th><th>Việc</th><th>Đã cài</th><th>Đang chạy</th></tr></thead><tbody>${DICH_VU.map((d) => `<tr>
      <td class="mono">${d.ten}</td><td class="nho">${d.mo_ta}</td>
      <td><span class="chip ${d.cai ? 'tt-lam' : 'tt-tat'}">${d.cai ? 'có' : 'chưa'}</span></td>
      <td><span class="chip ${d.chay ? 'tt-lam' : 'tt-tat'}">${d.chay ? 'chạy' : '—'}</span></td></tr>`).join('')}</tbody></table>`,
    [lenh('uv run tram chu trang-thai'), lenh('uv run tram chu cai-dat', 'liệt kê thay đổi, Đại ca gõ dong-y'), lenh('launchctl kickstart -k gui/$(id -u)/vn.tram.<tên>', 'chạy lại một dịch vụ đã cài')])

  const tele = khoi('Telegram', 'khoá <span class="mono">telegram:</span> trong <span class="mono">~/.tram/cau-hinh.yaml</span>',
    `<dl class="cd-dl"><dt>chat_id</dt><dd><span class="chip tt-lam">${TELEGRAM.chat_id}</span></dd>
      <dt>Giờ yên lặng</dt><dd>${TELEGRAM.gio_yen_lang}</dd>
      <dt>Loại tin</dt><dd class="tq-chip">${TELEGRAM.loai.map((l) => `<span class="chip">${l}</span>`).join('')}</dd></dl>`,
    [lenh('$EDITOR ~/.tram/cau-hinh.yaml'), lenh('launchctl kickstart -k gui/$(id -u)/vn.tram.bao-tin')])

  const co = khoi('Cờ', '',
    `<ul class="tq-ds">${CO.map(([ten, bat, ghi]) => `<li><span class="mono">${ten}</span><span class="nho">${ghi}</span>
      <span class="chip ${bat ? 'tt-lam' : 'tt-tat'}">${bat ? 'bật' : 'tắt'}</span></li>`).join('')}</ul>`,
    [lenh('$EDITOR ~/.tram/cau-hinh.yaml', 'vd giao_viec.bat: true — chỉ sau mọi cổng')])

  const kc = khoi('Keychain', 'chỉ hiện có / chưa có — không bao giờ hiện giá trị',
    `<ul class="tq-ds">${KEYCHAIN.map(([ten, co]) => `<li><span class="mono">${ten}</span><span></span>
      <span class="chip ${co ? 'tt-lam' : 'tt-can_nguoi'}">${co ? '● có' : '○ chưa có'}</span></li>`).join('')}</ul>`,
    [lenh('uv run tram chu cai-dat --nho', 'tạo tram-noi-bo-token'),
      lenh('security add-generic-password -U -s tram-telegram-bot-token -a tram -w', 'dán trong Terminal.app')])

  trang.innerHTML = `<div class="dau-trang"><div><h1>Cài đặt</h1>
      <p>Chỉ đọc. Không sửa được qua web; mỗi mục kèm lệnh CLI gợi ý để Đại ca tự chạy trên máy B.</p></div>
      <div class="cong-cu"><span class="chip">chỉ đọc</span></div></div>
    ${bangSanSang()}
    <div class="cd-luoi">${duAn}${dichVu}${tele}${co}${kc}</div>`

  for (const b of trang.querySelectorAll('.sao-chep')) {
    b.onclick = async () => {
      let ok = false
      try { await navigator.clipboard.writeText(b.dataset.lenh); ok = true } catch {
        const t = document.createElement('textarea')                    // dự phòng khi Clipboard API bị chặn
        t.value = b.dataset.lenh; document.body.appendChild(t); t.select()
        try { ok = document.execCommand('copy') } catch { ok = false }
        t.remove()
      }
      b.textContent = ok ? 'Đã chép' : 'Không chép được'
      setTimeout(() => { b.textContent = 'Sao chép' }, 1400)
    }
  }
}
