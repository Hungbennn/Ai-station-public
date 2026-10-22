import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { test } from 'node:test'
import { chipDichVu, demTrangThai, dongTram, oViecCho, usageHomNay } from '../src/luat_tong_quan.js'

const muc = (loai, chi_tiet = {}) => ({ loai, du_an: 'hr-codex', bead_id: 'hr-1', chi_tiet })
const BAY = '2026-10-15T15:17:00Z'

test('ô việc chờ: đếm theo loại, phụ đề theo T4 / pr_tram / cầu dao, ô rỗng', () => {
  const dl = {
    du_an: [{ ten: 'hr-codex', so_bead: { 'can-chot': 1 } }, { ten: 'tram', so_bead: { 'can-chot': 0 } }],
    phe_duyet: { so: 4, muc: [
      muc('escalation', { khe_id: 'B/codex-1', bead_goc: 'hr-3' }), muc('decision'),
      muc('cho-review', { pr_tram: { trang_thai: 'khong_xac_minh' } }), muc('cho-review', { pr_tram: null }),
      muc('he', { su_kien: 'khe.cau_dao_ngat', khe_id: 'B/claude-4' }),
    ] },
  }
  const o = oViecCho(dl)
  assert.deepEqual(o.map((x) => [x.ten, x.so, x.phu]), [
    ['Cần Đại ca chốt', 1, 'cột 2 · có câu hỏi'],
    ['Chờ review để đóng', 2, 'cột 3 · 1 PR không xác minh được'],
    ['Escalation bí', 2, 'Codex 1 hỏi ở hr-3'],
    ['Spec chờ duyệt', 0, 'chưa có'],
    ['Hệ cần xem', 1, 'cầu dao claude-4'],
  ])
  assert.equal(o[0].toi, '/cong-viec')
  assert.equal(o[1].toi, '/phe-duyet')
  assert.deepEqual(o.map((x) => x.lop), ['tt-can_nguoi', 'tt-cau_dao', 'tt-can_nguoi', '', 'tt-cau_dao'])
  const rong = oViecCho({ du_an: [], phe_duyet: { muc: [muc('he', { su_kien: 'quet.loi' }), muc('cho-review')] } })
  assert.equal(rong[1].phu, 'cột 3')
  assert.equal(rong[2].phu, 'không có')
  assert.equal(rong[4].phu, 'quet.loi')
})

test('dòng sức khoẻ: chip dịch vụ + quét cuối, estop, lỗi memory, cầu dao khe', () => {
  assert.deepEqual(chipDichVu({ da_cai: true, dang_chay: true }), { chu: 'chạy', lop: 'tt-lam' })
  assert.deepEqual(chipDichVu({ da_cai: true, dang_chay: false }), { chu: 'dừng', lop: 'tt-can_nguoi' })
  assert.deepEqual(chipDichVu({ da_cai: false, dang_chay: false }), { chu: 'chưa cài', lop: 'tt-tat' })
  assert.deepEqual(chipDichVu({ da_cai: null, dang_chay: null }), { chu: 'không rõ', lop: '' })
  const dl = {
    du_an: [{ quet_cuoi: '2026-10-15T15:10:00Z' }, { quet_cuoi: '2026-10-15T15:14:00Z' }, { quet_cuoi: null }],
    tram: { estop: false },
    phe_duyet: { muc: [muc('he', { su_kien: 'nho.loi_llm' })] },
    doi_ngu: { khe: [{ khe_id: 'B/claude-4', cau_dao: { ngat: true } },
      { khe_id: 'B/claude-1', cau_dao: { ngat: false } }] },
  }
  assert.deepEqual(dongTram(dl, BAY), [
    ['Quét cuối', '22:14 · 3 phút trước', 'tt-lam'],
    ['Estop', 'tắt', 'tt-lam'],
    ['Lỗi memory', 'lỗi LLM', 'tt-can_nguoi'],
    ['Cầu dao khe', '1 ngắt · claude-4', 'tt-cau_dao'],
  ])
  const yen = dongTram({ du_an: [], tram: { estop: true }, phe_duyet: { muc: [] }, doi_ngu: { khe: [] } }, BAY)
  assert.deepEqual(yen.map((d) => d.slice(1)), [['chưa quét', 'tt-tat'], ['đang bật', 'tt-can_nguoi'],
    ['không', 'tt-lam'], ['không', 'tt-lam']])
})

test('đếm trạng thái đội ngũ: cầu dao ngắt tính riêng, thứ tự cố định, bỏ trạng thái 0', () => {
  const khe = [
    { trang_thai: 'lam' }, { trang_thai: 'ranh' }, { trang_thai: 'ranh', cau_dao: { ngat: true } },
    { trang_thai: 'can_nguoi' }, { trang_thai: 'mat_ket_noi' }, { trang_thai: 'lam' },
  ]
  assert.deepEqual(demTrangThai(khe), [
    { lop: 'tt-lam', chu: 'Đang làm', n: 2 }, { lop: 'tt-ranh', chu: 'Rảnh', n: 1 },
    { lop: 'tt-cau_dao', chu: 'Cầu dao ngắt', n: 1 }, { lop: 'tt-can_nguoi', chu: 'Cần Đại ca', n: 1 },
    { lop: 'tt-mat_ket_noi', chu: 'Mất kết nối', n: 1 },
  ])
  assert.deepEqual(demTrangThai([]), [])
})

test('usage hôm nay: tách khe / chấm cột, thanh theo tỉ lệ giảm dần, chưa có giá', () => {
  const dong = (khoa, usd, so_lan = 1) => ({ khoa, token_vao: 0, token_ra: 0, so_lan, chi_phi_usd: usd })
  const u = usageHomNay({
    theo_ngay: [{ khoa: '2026-10-15', token_vao: 1840000, token_ra: 212000, so_lan: 7, chi_phi_usd: 3.52 }],
    theo_nguon: [dong('B/codex-1', 0.96), dong('cham-cot', 0.42), dong('B/claude-1', 1.35), dong('B/claude-4', null)],
  })
  assert.equal(u.vao, '1,84 tr')
  assert.equal(u.ra, '212 n')
  assert.equal(u.usdKhe, '$2.31')
  assert.equal(u.usdApi, '$0.42')
  assert.equal(u.luot, 7)
  assert.deepEqual(u.cot.map((c) => [c.ma, c.usd, Math.round(c.rong)]),
    [['claude-1', '$1.35', 100], ['codex-1', '$0.96', 71], ['claude-4', 'chưa có giá', 0]])
  const trong = usageHomNay({ theo_ngay: [], theo_nguon: [] })
  assert.deepEqual([trong.vao, trong.usdKhe, trong.usdApi, trong.luot, trong.cot],
    ['0', 'chưa có giá', 'chưa có giá', 0, []])
})

test('bs-78r.8 (b): đầu khối Việc chờ xuống hàng ở breakpoint 900 px của mockup, không đổi bản rộng', () => {
  const css = readFileSync(new URL('../src/kieu/tong-quan.css', import.meta.url), 'utf8')
  const i = css.indexOf('@media (max-width: 900px)')
  assert.ok(i > 0)
  assert.match(css.slice(i), /\.tq-dau \{ flex-wrap: wrap; \}/)
  assert.match(css.slice(0, i), /\.tq-dau \{ display: flex; align-items: center; gap: 10px; margin-bottom: 14px; \}/)
})
