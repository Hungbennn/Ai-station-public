// Chặn chèn HTML thô vào trang (spec §4 mục 4): nội dung bead chỉ hiển thị bằng text. Quét mọi file trong src/.
// Lát 2f thêm: cấm `style="…"` tĩnh trong .vue (Vue gộp khối tĩnh thành chuỗi HTML → CSP `style-src 'self'` chặn;
// `:style` động đặt qua CSSOM thì được) và cấm URL ngoài trong mã nguồn (CSP chỉ 'self'; link PR chỉ GitHub).
import { readFileSync, readdirSync, statSync } from 'node:fs'
import { extname, join } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'

const CAM = [[/v-html/, 'v-html'], [/v-bind:innerHTML/, 'v-bind:innerHTML'], [/:innerHTML/, ':innerHTML'],
  [/innerHTML/, 'innerHTML'], [/outerHTML/, 'outerHTML'], [/insertAdjacentHTML/, 'insertAdjacentHTML'],
  [/document\.write/, 'document.write']]
const MA = new Set(['.js', '.mjs', '.vue', '.css'])
const STYLE_TINH = /<[a-zA-Z][^<>]*\sstyle=["']/
const URL_NGOAI = /\bhttps?:\/\/(?!github\.com\/)[a-z0-9]/i

export function quetNguon(ten, van) {
  const loi = []
  for (const [re, nhan] of CAM) if (re.test(van) && !loi.some((l) => nhan.includes(l))) loi.push(nhan)
  if (extname(ten) === '.vue' && STYLE_TINH.test(van)) loi.push('style="…" tĩnh')
  if (MA.has(extname(ten)) && URL_NGOAI.test(van)) loi.push('URL ngoài')
  return loi
}

function chay() {
  const goc = fileURLToPath(new URL('./src', import.meta.url))
  const duyet = (d) => readdirSync(d)
    .flatMap((t) => (statSync(join(d, t)).isDirectory() ? duyet(join(d, t)) : [join(d, t)]))
  const tep = duyet(goc)
  const viPham = tep.map((p) => [p, quetNguon(p, readFileSync(p, 'utf8'))]).filter(([, l]) => l.length)
  if (viPham.length) {
    console.error('Cấm chèn HTML thô / style tĩnh / URL ngoài trong:', viPham.map(([p, l]) => `${p}: ${l.join(', ')}`))
    process.exit(1)
  }
  console.log(`kiem-an-toan: ${tep.length} file, không có chèn HTML thô, style tĩnh hay URL ngoài`)
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) chay()
