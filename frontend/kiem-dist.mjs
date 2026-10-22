// Cổng CSP sau `vite build` (spec 2 §4 mục 6; plan 2c G1): bundle không được cần 'unsafe-eval' / 'unsafe-inline'
// / 'wasm-unsafe-eval', và three.js (TresJS) chỉ nằm trong chunk nạp lười của trang Văn phòng (giữ D6 cho 2a).
// Chạy: `npm run build && npm run kiem-dist`. Không thay kiểm chạy thật trên trình duyệt (Task 8).
import { readFileSync, readdirSync } from 'node:fs'
import { join } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'

// Worker/blob không cần liệt kê: CSP `default-src 'none'` + `script-src 'self'` đã chặn worker từ blob:.
const CAM_JS = [[/new Function\s*\(/, 'new Function'], [/(^|[^\w$.])eval\s*\(/, 'eval('],
  [/WebAssembly\.(compile|instantiate)/, 'WebAssembly.instantiate']]

export function quetJs(van) {
  return CAM_JS.filter(([re]) => re.test(van)).map(([, ten]) => ten)
}

export function quetHtml(van) {
  const loi = []
  if (/<script(?![^>]*\bsrc=)[^>]*>/i.test(van)) loi.push('<script> nội tuyến')
  if (/<style[\s>]/i.test(van)) loi.push('<style> nội tuyến')
  if (/\sstyle=/i.test(van)) loi.push('thuộc tính style')
  for (const m of van.matchAll(/\s(on[a-z]+)=/gi)) loi.push(`thuộc tính ${m[1].toLowerCase()}`)
  return loi
}

// Lát 2f: font tự host (D35) — không được còn font / CDN ngoài; CSS không `url(http…)`.
const HOST_NGOAI = ['fonts.googleapis.com', 'fonts.gstatic.com', 'cdn.jsdelivr.net', 'unpkg.com']
export function quetNgoai(van) {
  const loi = HOST_NGOAI.filter((h) => van.includes(h))
  if (/url\(\s*["']?https?:/i.test(van)) loi.push('url(http…) trong CSS')
  if (/url\(\s*["']?data:font/i.test(van)) loi.push('font nhúng data: (CSP font-src)')
  return loi
}

// Lát 2f: Vue gộp khối tĩnh thành chuỗi HTML chèn bằng innerHTML — `style=` trong chuỗi đó bị CSP chặn.
export function quetKhoiTinh(van) {
  return /<[a-zA-Z][^<>]*?\sstyle=\\?["']/.test(van) ? ['style= trong khối tĩnh'] : []
}

export function kiemGoiChinh(van) {
  return /\bWebGLRenderer\b/.test(van) ? ['three nằm trong gói chính — trang Văn phòng phải nạp lười'] : []
}

function chay() {
  const dist = fileURLToPath(new URL('./dist', import.meta.url))
  const html = readFileSync(join(dist, 'index.html'), 'utf8')
  const loi = [...quetHtml(html), ...quetNgoai(html)].map((l) => `index.html: ${l}`)
  const chinh = [...html.matchAll(/<script[^>]*\bsrc="\/?([^"]+)"/g)].map((m) => m[1])
  for (const f of chinh) loi.push(...kiemGoiChinh(readFileSync(join(dist, f), 'utf8')).map((l) => `${f}: ${l}`))
  const tep = readdirSync(join(dist, 'assets')).filter((t) => t.endsWith('.js'))
  for (const t of tep) {
    const van = readFileSync(join(dist, 'assets', t), 'utf8')
    loi.push(...[...quetJs(van), ...quetNgoai(van), ...quetKhoiTinh(van)].map((l) => `assets/${t}: ${l}`))
  }
  const css = readdirSync(join(dist, 'assets')).filter((t) => t.endsWith('.css'))
  for (const t of css) {
    loi.push(...quetNgoai(readFileSync(join(dist, 'assets', t), 'utf8')).map((l) => `assets/${t}: ${l}`))
  }
  if (loi.length) {
    console.error('kiem-dist: vi phạm CSP chặt:\n' + loi.join('\n'))
    process.exit(1)
  }
  console.log(`kiem-dist: ${tep.length} file JS, ${css.length} file CSS, không thấy eval/inline/style tĩnh/font ngoài; `
    + 'cần kiểm CSP runtime trên trình duyệt (task K)')
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) chay()
