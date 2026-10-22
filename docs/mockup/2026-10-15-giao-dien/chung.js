// Tiện ích dùng chung của mockup.
export const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c])

export function moNganBen(html) {
  const n = document.getElementById('ngan-ben')
  n.innerHTML = `<button class="dong" type="button" aria-label="Đóng">×</button>${html}`
  n.hidden = false
  n.querySelector('.dong').onclick = dongNganBen
  return n
}

export function dongNganBen() {
  const n = document.getElementById('ngan-ben')
  n.hidden = true
  n.innerHTML = ''
}

// Avatar chibi nhỏ (SVG) cho thẻ khe — cùng màu thân/tóc với nhân vật 3D.
export function chibi(khe) {
  const mo = khe.hien_thi === 'tat' ? ' opacity=".4"' : ''
  return `<svg class="chibi" viewBox="0 0 46 46" aria-hidden="true"><g${mo}>
    <ellipse cx="23" cy="41" rx="10" ry="2.6" fill="#3a241822"/>
    <rect x="17.5" y="32" width="4" height="8" rx="2" fill="#2b2523"/><rect x="24.5" y="32" width="4" height="8" rx="2" fill="#2b2523"/>
    <path d="M15 34 L16.5 22 Q23 19 29.5 22 L31 34 Z" fill="${khe.mau}"/>
    <circle cx="23" cy="15" r="8" fill="#f2c9a3"/>
    <path d="M14.8 14.5 A8.3 8.3 0 0 1 31.2 14.5 Q27 9.5 23 10.5 Q18 9.8 14.8 14.5 Z" fill="${khe.toc}"/>
  </g></svg>`
}

export function tiLe(cap) {
  if (!cap) return '—'
  const [x, m] = cap
  if (!m) return 'chưa có'
  return `${Math.round((x / m) * 100)}% <span class="nho">(${x}/${m})</span>`
}
