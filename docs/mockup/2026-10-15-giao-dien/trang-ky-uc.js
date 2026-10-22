// Trang Ký ức (D36) — giữ đủ chức năng của frontend/src/trang/KyUc.vue + TheKyUc + OGhiNho + SuKienNho.
// Dữ liệu: GET /api/nho?pham_vi=&cho= (ky_uc, tong, pham_vi), GET /api/nho/su-kien; ghi: POST /api/nho/ghi, /api/nho/xoa.
// Cả trang CHỈ ĐẠI CA (GET cũng 403). Ô tìm và lọc loại sự kiện là lọc phía trình duyệt trên dữ liệu đã tải.
import { KY_UC, SU_KIEN_NHO, BAY_GIO, phamViKyUc } from './du-lieu-ky-uc-usage.js'
import { DU_AN, BEAD } from './du-lieu.js'
import { esc } from './chung.js'

const LOAI_PHAM_VI = [['du-an-cach-lam', 'Dự án · cách làm'], ['du-an-nghiep-vu', 'Dự án · nghiệp vụ'],
  ['vai', 'Vai (mọi dự án thấy)'], ['chung', 'Chung (mọi dự án thấy)']]
const TEN_SK = { 'nho.ghi': 'Ghi', 'nho.gop': 'Gộp', 'nho.xoa': 'Xoá mềm', 'nho.xoa_cung': 'Xoá cứng',
  'nho.thang_cap': 'Thăng cấp', 'nho.tu_choi': 'Từ chối', 'nho.loi_tach': 'Bỏ sự kiện', 'nho.loi_llm': 'Lỗi Claude API',
  'nho.loi_embedder': 'Lỗi embedder', 'nho.phuc_hoi': 'Phục hồi' }
const NHOM_SK = [['', 'Tất cả'], ['ghi', 'Ghi · gộp'], ['xoa', 'Xoá'], ['thang_cap', 'Thăng cấp'], ['tu_choi', 'Từ chối'], ['loi', 'Lỗi · phục hồi']]
const nhomCua = (l) => ({ 'nho.ghi': 'ghi', 'nho.gop': 'ghi', 'nho.xoa': 'xoa', 'nho.xoa_cung': 'xoa', 'nho.thang_cap': 'thang_cap',
  'nho.tu_choi': 'tu_choi' })[l] ?? 'loi'
const LOP_SK = { ghi: 'tt-lam', xoa: 'tt-tat', thang_cap: 'pv-vai', tu_choi: 'tt-cau_dao', loi: 'tt-can_nguoi' }
const TEN_NGUON = { agent: 'agent ghi', da_chot: 'Đại ca chốt', dai_ca_sua: 'Đại ca sửa cột', tra_ve: 'Đại ca trả về', dai_ca_ghi: 'Đại ca ghi tay' }
const TU_NGHIEP_VU = ['hoàn tiền', 'thuế', 'hoá đơn', 'hóa đơn', 'khách', 'sổ cái', 'bút toán', 'lương']   // minh hoạ luật nghiệp vụ

const gio = (iso) => iso ? `${iso.slice(8, 10)}/${iso.slice(5, 7)} ${iso.slice(11, 16)}` : ''
const TEN = /^[a-z0-9-]+$/
function dungPhamVi(loai, duAn, vai) {
  if (loai === 'chung') return '/chung'
  if (loai === 'vai') return TEN.test(vai || '') ? `/vai/${vai}` : null
  if (!TEN.test(duAn || '')) return null
  return loai === 'du-an-cach-lam' ? `/du-an/${duAn}/cach-lam` : `/du-an/${duAn}/nghiep-vu`
}
const ngoaiDuAn = (pv) => pv === '/chung' || String(pv).startsWith('/vai/')
function nhanPhamVi(pv) {
  if (pv === '/chung') return ['Chung', 'pv-chung']
  if (pv.startsWith('/vai/')) return [`Vai ${pv.slice(5)}`, 'pv-vai']
  return pv.endsWith('/nghiep-vu') ? ['Nghiệp vụ', 'pv-nghiep-vu'] : ['Cách làm', 'pv-cach-lam']
}
const lienKetBead = (du_an, bead) => BEAD.some((b) => b.id === bead)
  ? `<a class="mono" href="#/cong-viec?du_an=${du_an}&bead=${bead}">${du_an}/${bead}</a>` : `<span class="mono">${du_an}/${bead}</span>`
function nguon(k) {
  return k.nguon.map((n) => n.loai === 'thang_cap'
    ? `thăng cấp từ <b>${esc(n.du_an)}</b> <span class="mono nho">${esc(n.id_goc.slice(0, 9))}…</span>`
    : `${TEN_NGUON[n.loai] ?? esc(n.loai)}${n.vai ? ` · vai ${esc(n.vai)}` : ''}${n.bead_id ? ` · ${lienKetBead(n.du_an, n.bead_id)}` : n.du_an ? ` · ${esc(n.du_an)}` : ''}`).join('; ')
}

function theKyUc(k) {
  const [ten, lop] = nhanPhamVi(k.pham_vi)
  const cho = k.hieu_luc_tu > BAY_GIO
  return `<article class="the ku-the${cho ? ' cho' : ''}">
    <div class="ku-tren"><span class="chip ${lop}">${ten}</span><span class="chip mono">${esc(k.pham_vi)}</span>
      ${cho ? `<span class="chip tt-cau_dao">chờ tự có hiệu lực ${gio(k.hieu_luc_tu)}</span>` : ''}
      ${k.nguon_dai_ca ? '<span class="chip ku-dai-ca">của Đại ca</span>' : ''}
      ${k.nhan.map((n) => `<span class="ku-nhan mono">#${esc(n)}</span>`).join('')}
      <button class="nut nguy ku-xoa" type="button" data-xoa="${k.id}" title="Xoá mềm — recall không trả nữa">Xoá</button></div>
    <p class="ku-noi-dung">${esc(k.noi_dung)}</p>
    <div class="ku-meta"><span>Nguồn: ${nguon(k)}</span><span>Tạo ${gio(k.tao_luc)}</span>
      <span class="ku-qt" title="Độ quan trọng 0–1">Quan trọng <i><b style="width:${k.quan_trong * 100}%"></b></i> ${k.quan_trong.toFixed(2)}</span>
      <span>Dùng ${k.so_lan_dung} lần${k.dung_luc ? ` · gần nhất ${gio(k.dung_luc)}` : ''}</span>
      <span class="mono ku-id">${k.id}</span></div>
  </article>`
}

function formGhi(f) {
  const pv = dungPhamVi(f.loai, f.duAn, f.vai)
  const duAn = DU_AN.map((d) => `<option value="${d.ma}" ${d.ma === f.duAn ? 'selected' : ''}>${d.ten}</option>`).join('')
  return `<section class="the ku-ghi"><h3 class="tq-h">Ghi tay một ký ức</h3>
    <label class="ku-o"><span>Nội dung <span class="nho" id="ku-dem">${f.noiDung.length}/600</span></span>
      <textarea id="ku-noi-dung" maxlength="600" rows="3" placeholder="Một bài học ngắn, tự đứng được…">${esc(f.noiDung)}</textarea></label>
    <div class="ku-hang">
      <label class="ku-o"><span>Phạm vi</span><select id="ku-loai">${LOAI_PHAM_VI.map(([k, t]) => `<option value="${k}" ${k === f.loai ? 'selected' : ''}>${t}</option>`).join('')}</select></label>
      ${f.loai.startsWith('du-an') ? `<label class="ku-o"><span>Dự án</span><select id="ku-du-an"><option value="" disabled ${f.duAn ? '' : 'selected'}>— chọn —</option>${duAn}</select></label>` : ''}
      ${f.loai === 'vai' ? `<label class="ku-o"><span>Vai</span><input class="o" id="ku-vai" value="${esc(f.vai)}" maxlength="40" placeholder="coder, qc, cham-cot…"></label>` : ''}
    </div>
    <label class="ku-o"><span>Nhãn <span class="nho">tối đa 5, cách nhau dấu phẩy</span></span><input class="o" id="ku-nhan" value="${esc(f.nhan)}" maxlength="200" placeholder="test, git"></label>
    <p class="nho ku-dich">Ghi vào: <span class="chip mono">${pv ?? '(chưa đủ)'}</span></p>
    ${pv && ngoaiDuAn(pv) ? '<div class="canh-bao">Agent của MỌI dự án sẽ thấy ký ức này. Có tên khách, số tiền hay tên module của bất kỳ dự án nào thì bị từ chối.</div>' : ''}
    ${pv && pv.endsWith('/cach-lam') ? '<p class="nho">Chạm luật nghiệp vụ của dự án thì trạm tự chuyển vào <span class="mono">nghiep-vu</span>.</p>' : ''}
    <div class="ku-gui"><button class="nut chinh" id="ku-ghi" type="button" ${pv && f.noiDung.trim() ? '' : 'disabled'}>Ghi</button>
      ${f.bao ? `<span class="${f.bao.loi ? 'ku-loi' : 'nho'}" role="${f.bao.loi ? 'alert' : 'status'}">${esc(f.bao.chu)}</span>` : ''}</div>
  </section>`
}

function khoiSuKien(ds, nhom) {
  const loc = ds.filter((s) => !nhom || nhomCua(s.loai) === nhom)
  return `<section class="the ku-sk"><h3 class="tq-h">Sự kiện ký ức gần đây <span class="nho" style="font-weight:400">${ds.length} / tối đa 50</span></h3>
    <div class="ku-loc-sk">${NHOM_SK.map(([m, t]) => `<button type="button" class="ku-pill${m === nhom ? ' chon' : ''}" data-nhom="${m}">${t}</button>`).join('')}</div>
    ${loc.length ? `<ol class="ku-dtg">${loc.map((s) => `<li><div><span class="mono nho">${gio(s.luc)}</span>
      <span class="chip ${LOP_SK[nhomCua(s.loai)]}">${TEN_SK[s.loai] ?? esc(s.loai)}</span>
      <span class="nho">${s.bead_id ? lienKetBead(s.du_an, s.bead_id) : `<span class="mono">${esc(s.du_an)}</span>`}</span></div>
      <code class="ku-tom-tat">${esc(s.tom_tat)}</code></li>`).join('')}</ol>` : '<p class="nho">Chưa có sự kiện.</p>'}
  </section>`
}

const MINH_HOA = [['dai_ca', 'Đại ca'], ['khong_danh_tinh', 'Không có danh tính'], ['loi_nho', 'Memory lỗi']]

export function veKyUc(trang) {
  const s = { quyen: 'dai_ca', phamVi: '', chiCho: false, tim: '', nhomSk: '', ds: [...KY_UC], suKien: [...SU_KIEN_NHO], bao: '',
    f: { noiDung: '', loai: 'du-an-cach-lam', duAn: '', vai: '', nhan: '', bao: null } }

  function ve() {
    const dsPv = phamViKyUc(s.ds)
    const theoPv = s.ds.filter((k) => (!s.phamVi || k.pham_vi === s.phamVi) && (!s.chiCho || k.hieu_luc_tu > BAY_GIO))
    const q = s.tim.trim().toLowerCase()
    const hien = theoPv.filter((k) => !q || [k.noi_dung, k.id, k.pham_vi, ...k.nhan].some((x) => x.toLowerCase().includes(q)))
    const dau = `<div class="dau-trang"><div><h1>Ký ức <span class="ku-tong">${s.quyen === 'dai_ca' ? theoPv.length : '—'}</span></h1>
        <p>Bài học agent và Đại ca để lại cho các lượt sau. Xem, lọc, xoá mềm, ghi tay; ký ức thăng cấp chờ 7 ngày rồi mới có hiệu lực.</p></div>
      <div class="cong-cu"><span class="chip ku-khoa-chip"><svg viewBox="0 0 24 24" aria-hidden="true"><rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/></svg>chỉ Đại ca xem</span>
        <span class="nho">Minh hoạ:</span><div class="nhom-nut" role="group" aria-label="Minh hoạ quyền">${MINH_HOA.map(([m, t]) =>
          `<button type="button" data-quyen="${m}" class="${m === s.quyen ? 'chon' : ''}">${t}</button>`).join('')}</div></div></div>`
    if (s.quyen !== 'dai_ca') {
      const loi = s.quyen === 'khong_danh_tinh'
        ? ['403 · Chỉ Đại ca xem được ký ức', 'Cần danh tính Tailscale của Đại ca. Ký ức của mọi dự án (cả nghiệp vụ và nguồn) không hiện cho ai khác, kể cả danh sách phạm vi và sự kiện.']
        : ['Không đọc được memory service', 'tram-api chưa nối memory service (vn.tram.nho, 127.0.0.1:7710). Xem Sức khoẻ trạm ở Tổng quan; trang tự tải lại khi có sự kiện nho.*.']
      trang.innerHTML = dau + `<div class="the ku-chan" role="alert"><strong>${loi[0]}</strong><p>${loi[1]}</p>
        ${s.quyen === 'loi_nho' ? '<a class="nut" href="#/tong-quan" style="display:inline-flex;align-items:center;text-decoration:none">Mở Tổng quan</a>' : ''}</div>`
      return gan()
    }
    trang.innerHTML = dau + `<div class="ku-luoi"><div class="ku-chinh">
      <section class="the ku-loc">
        <div class="ku-hang"><label class="tim ku-tim"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
          <input id="ku-tim" type="search" placeholder="Tìm nội dung, nhãn, mã…" value="${esc(s.tim)}"></label>
          <label class="gc"><input type="checkbox" id="ku-cho" ${s.chiCho ? 'checked' : ''}>Chỉ ký ức thăng cấp đang chờ tự có hiệu lực (7 ngày)</label></div>
        <div class="ku-pv"><span class="nho">Phạm vi</span>
          <button type="button" class="ku-pill${s.phamVi ? '' : ' chon'}" data-pv="">Tất cả <b>${s.ds.length}</b></button>
          ${dsPv.map((p) => `<button type="button" class="ku-pill mono${p.pham_vi === s.phamVi ? ' chon' : ''}" data-pv="${esc(p.pham_vi)}">${esc(p.pham_vi)} <b>${p.so}</b>${p.so_cho ? `<em>${p.so_cho} chờ</em>` : ''}</button>`).join('')}</div>
      </section>
      ${s.bao ? `<p class="ku-bao" role="status">${esc(s.bao)}</p>` : ''}
      <p class="nho ku-dem">Đang hiện ${hien.length} / ${theoPv.length} ký ức${q ? ` khớp “${esc(s.tim)}”` : ''} · mới nhất trước · tự tải lại khi có sự kiện <span class="mono">nho.*</span>
        ${theoPv.length > 200 ? ' · server chỉ trả 200 ký ức mới nhất, lọc theo phạm vi để xem thêm' : ''}</p>
      <div class="ku-ds">${hien.map(theKyUc).join('') || '<div class="cot-rong">Không có ký ức nào.</div>'}</div>
    </div>
    <aside class="ku-ray">${formGhi(s.f)}${khoiSuKien(s.suKien, s.nhomSk)}</aside></div>`
    gan()
  }

  function gan() {
    const $ = (sel) => trang.querySelector(sel)
    for (const b of trang.querySelectorAll('[data-quyen]')) b.onclick = () => { s.quyen = b.dataset.quyen; ve() }
    if (s.quyen !== 'dai_ca') return
    $('#ku-tim').oninput = (e) => { s.tim = e.target.value; ve(); const o = $('#ku-tim'); o.focus(); o.setSelectionRange(o.value.length, o.value.length) }
    $('#ku-cho').onchange = (e) => { s.chiCho = e.target.checked; ve() }
    for (const b of trang.querySelectorAll('[data-pv]')) b.onclick = () => { s.phamVi = b.dataset.pv; ve() }
    for (const b of trang.querySelectorAll('[data-nhom]')) b.onclick = () => { s.nhomSk = b.dataset.nhom; ve() }
    for (const b of trang.querySelectorAll('[data-xoa]')) {
      b.onclick = () => {
        if (!window.confirm('Xoá mềm ký ức này? Recall sẽ không trả nó nữa.')) return
        const k = s.ds.find((x) => x.id === b.dataset.xoa)
        s.ds = s.ds.filter((x) => x !== k)
        s.suKien.unshift({ id: 0, luc: BAY_GIO, du_an: k.pham_vi.split('/')[2] && k.pham_vi.startsWith('/du-an/') ? k.pham_vi.split('/')[2] : '_tram',
          bead_id: null, loai: 'nho.xoa', tom_tat: JSON.stringify({ id: k.id, pham_vi: k.pham_vi }) })
        s.bao = `Đã xoá mềm ${k.id}.`
        ve()
      }
    }
    const f = s.f
    const giu = (id, khoa) => { const o = $(id); if (o) o.oninput = o.onchange = (e) => { f[khoa] = e.target.value; f.bao = null; ve(); const n = $(id); if (n && n.tagName !== 'SELECT') { n.focus(); n.setSelectionRange?.(n.value.length, n.value.length) } } }
    giu('#ku-noi-dung', 'noiDung'); giu('#ku-loai', 'loai'); giu('#ku-du-an', 'duAn'); giu('#ku-vai', 'vai'); giu('#ku-nhan', 'nhan')
    $('#ku-ghi').onclick = () => {
      let pv = dungPhamVi(f.loai, f.duAn, f.vai)
      const cham = TU_NGHIEP_VU.filter((t) => f.noiDung.toLowerCase().includes(t))
      if (cham.length && ngoaiDuAn(pv)) {
        s.suKien.unshift({ id: 0, luc: BAY_GIO, du_an: '_tram', bead_id: null, loai: 'nho.tu_choi',
          tom_tat: JSON.stringify({ ly_do: `chạm luật nghiệp vụ: ${cham.join(', ')}`, nguon: 'dai_ca_ghi', pham_vi: pv }) })
        f.bao = { loi: true, chu: `Từ chối: chạm luật nghiệp vụ — ${cham.join(', ')}.` }
        return ve()
      }
      const chuyen = cham.length && pv.endsWith('/cach-lam')
      if (chuyen) pv = pv.replace('/cach-lam', '/nghiep-vu')
      const id = `m-${[...crypto.getRandomValues(new Uint8Array(12))].map((x) => x.toString(16).padStart(2, '0')).join('')}`
      const nhan = [...new Set(f.nhan.split(',').map((x) => x.trim()).filter((x) => x && x.length <= 30))].slice(0, 5)
      const k = { id, pham_vi: pv, nhan, noi_dung: f.noiDung.trim(), quan_trong: 0.8, nguon: [{ loai: 'dai_ca_ghi' }], nguon_dai_ca: true,
        tao_luc: BAY_GIO, hieu_luc_tu: BAY_GIO, dung_luc: null, so_lan_dung: 0 }
      s.ds.unshift(k)
      s.suKien.unshift({ id: 0, luc: BAY_GIO, du_an: pv.startsWith('/du-an/') ? f.duAn : '_tram', bead_id: null, loai: 'nho.ghi',
        tom_tat: JSON.stringify({ id, pham_vi: pv, nguon: k.nguon }) })
      s.f = { ...f, noiDung: '', nhan: '', bao: { loi: false, chu: chuyen ? `Đã ghi ${id} — chạm luật nghiệp vụ nên chuyển vào ${pv}.` : `Đã ghi ${id} vào ${pv}.` } }
      ve()
    }
  }
  ve()
}
