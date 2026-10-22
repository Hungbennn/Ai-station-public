# Lát 2f — Giao diện theo mockup: phần 2 — các trang — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ] **Step N: …**`) syntax for tracking. Hướng dẫn chung: `.handover/qc/huong-dan-code.md`. **Mọi dòng mã thêm vào phải có nguyên văn trong plan.**

> **Sửa 16/10 theo D41** (G19 của phần 1): bảng điểm trang Đội ngũ AI đọc thẳng `bang_diem` của `/api/doi-ngu` — API 2d (Task 6, bản D41) đã trả hàng cho mọi khe đã khai, kể cả khe 0 phiếu. Task 10 bỏ `hangBangDiem` và test của nó (còn 4 test node); `DoiNgu.vue` đọc `dl.bang_diem`. Các task khác không đổi. Tổng sau đợt 3: node **M₀ + 57** (trước M₀ + 58).

**Goal:** Dựng lại chín trang dashboard đúng mockup đã duyệt (D20, D33, D39) trên nền của phần 1, rồi kiểm trên trình duyệt dưới CSP thật của tram-api.

**Architecture:** Mỗi trang một task, file riêng (trang, thành phần con trong `thanh/<trang>/`, luật thuần `luat_<trang>.js` có test node, CSS `kieu/<trang>.css` import trong trang). Logic ghi (`thanGhi`, 409/501, khoá khi không phải Đại ca) giữ nguyên của 2a–2e; chỉ đổi giao diện. Văn phòng dựng cảnh bằng module three thuần gắn qua `<primitive>`, nhãn là lớp HTML phủ chống chồng bằng thuật toán `boTriNhan` của mockup.

**Tech Stack:** Vue 3.5.43, vue-router 5.4.0, Vite 8.3.4, `@tresjs/core` 5.9.1, `three` 0.186.1, node `--test`; tram-api FastAPI cho task 18.

**Phần 1 (bắt buộc đọc trước):** `docs/plans/2026-10-16-lat-2f-1-nen-va-api.md` — Global Constraints, Phụ thuộc, bảng "Câu hỏi / giả định" G1–G30, "Chờ Đại ca chốt", **"Hợp đồng (lát 2f)"** (JSON của API mới + tên lớp CSS, hàm, component nền), "Chuẩn bị", "Sơ đồ đợt". Mọi ràng buộc ở đó áp cho file này.

## Hợp đồng giữa hai file

- Phần 2 **chỉ dùng** những gì phần 1 công bố ở mục "Hợp đồng (lát 2f)": tên API/trường JSON, lớp CSS ở `kieu/nen.css`, `kieu/khung.css`, `kieu/chung.css`, `kieu/khe.css`, hàm ở `dinh_dang.js`, `luat.js`, `mau_khe.js`, `luat_han_muc.js`, component `DauTrang`, `BieuTuong`, `Chibi`, `ThanhHanMuc`. Đổi tên ở phần 1 thì phải sửa phần 2.
- Phần 2 **không sửa** file nào của phần 1, trừ hai trang giữ chỗ `trang/TongQuan.vue` (Task 13) và `trang/CaiDat.vue` (Task 14) — thay toàn bộ.
- Task 9–17 build và test được ngay sau Task 1–2 (đợt 2); dữ liệu thật của Tổng quan / Cài đặt / Ký ức (mô tả) / Phê duyệt (T4) / Đội ngũ (T1) cần Task 5–8 đã ghép — Task 18 kiểm sau khi mọi task đã ghép.
- Mỗi trang tạo `kieu/<trang>.css` riêng; không trang nào sửa `main.js`, `tuyen.js`, CSS chung.

## Global Constraints (nhắc lại — đầy đủ ở phần 1)

- Bám mockup: mỗi task ghi file + ảnh mockup; QC so ảnh `docs/mockup/2026-10-15-giao-dien/anh-*.png`.
- Không `style="…"` tĩnh trong template; không `v-html`/`innerHTML`; không URL ngoài; link PR qua `laLinkAnToan` + `rel="noopener noreferrer"`.
- Chỉ nền sáng; font tự host; không thêm gói; mỗi file ≤ ~120 dòng, dòng ≤ 120 ký tự.
- Trang không import `three` hay `van_phong/*` (trừ trang Văn phòng nạp lười).
- Dự án `bat_ghi === false` (1a-2): chip "chỉ quét thử", nút ghi của dự án đó khoá + `CHU_CHI_QUET_THU` (G4).

### Task 9: Trang Công việc + ngăn bên

**Đợt:** 3 · **Độ khó:** vừa · **Phải xong trước:** Task 1, 2 · **Test mới:** 5 node

**Mockup bám:** `trang.js` (`COT`, `theBead`, `moBead`, `veCongViec`), `style.css` mục "Công việc", `.ngan-ben`, `.dtg`; ảnh `anh-cong-viec.png`, `anh-cong-viec-ngan-ben.png`. Khảo sát §1.3 (danh sách "Bản thật có, mockup không vẽ" — giữ theo D36).

**Files:**
- Create: `frontend/src/luat_cong_viec.js` (`COT`, `MO_TA_TRANG`, `chipCot`, `viTriThe`, `uuTien`, `chipThe`, `dongKhe`), `frontend/src/kieu/cong-viec.css`
- Modify (viết lại — khối diff): `frontend/src/trang/CongViec.vue`, `frontend/src/trang/NganBen.vue`, `frontend/src/thanh/TheBead.vue`; (đổi lớp, giữ logic): `frontend/src/thanh/OChot.vue` (hai nút "Chốt" / "Dẫn ADR" thay ô đánh dấu; thêm prop `khoa`), `OTraLoi.vue`, `OGiaoViec.vue`, `DongThoiGian.vue`, `HopViSao.vue`
- Test: `frontend/tests/cong_viec.test.mjs` (mới)

**Interfaces:**
- Consumes: `/api/cong-viec`, `/api/giao-viec`, `/api/du-an` (`bat_ghi`), `/api/doi-ngu` (dòng khe trên thẻ — ghép phía trình duyệt, T7), `/api/bead/{du_an}/{id}`; `nhanPrTram`, `lopPrTram`, `moTaPrTram` (2d), `mauKhe`, `tenKhe`, `duAnChiQuetThu`, `CHU_CHI_QUET_THU`.
- Produces: `dongKhe(the, dsKhe) -> {ten, buoc, canNguoi, mau} | null`.

Giữ (D36, bố cục cũ + lớp mới): hàng "Chưa chấm" / "Feature đang chạy plan" / "Epic", kéo thẻ cột 1↔2 + hộp "Vì sao?", nút "Chuyển sang cột 1/2", trả lời decision, khối Bàn giao, Bộ giao việc, mở ngăn bên theo `?du_an=&bead=` đúng một lần, xử lý 409. Dự án `bat_ghi === false`: thẻ không kéo được, nút ghi ở ngăn bên khoá kèm `CHU_CHI_QUET_THU`. Tiêu chí nghiệm thu hiện cả văn bản (`pre-wrap`) vì API trả chuỗi tự do. `CongViec.vue` dài 124 dòng (nhỉnh hơn ~120, chấp nhận vì phải giữ đủ năm hàng).

- [ ] **Step 1: Viết test (chép nguyên văn)**

`frontend/tests/cong_viec.test.mjs` (mới):

```js
import assert from 'node:assert/strict'
import { test } from 'node:test'
import { COT, chipCot, chipThe, dongKhe, uuTien, viTriThe } from '../src/luat_cong_viec.js'
import { mauKhe } from '../src/mau_khe.js'

const the = (x = {}) => ({ du_an: 'hr', id: 'hr-1', hang: 'ai-lam', loai: 'bug', uu_tien: 1, khoa: false, co_do: false,
  lech: false, khe_spec: false, cho: [], giao: null, ...x })

test('COT theo mockup: ba cột, số thứ tự, tên, mô tả', () => {
  assert.deepEqual(COT.map((c) => [c.hang, c.so, c.ten]),
    [['ai-lam', 1, 'AI tự làm'], ['can-chot', 2, 'Cần Đại ca chốt'], ['cho-review', 3, 'Chờ review để đóng']])
  assert.equal(COT[2].moTa, 'Đã code + QC, chờ Duyệt')
})

test('chipCot suy từ hang; hàng ngoài ba cột không có chip', () => {
  assert.equal(chipCot(the()), 'cot:ai-lam')
  assert.equal(chipCot(the({ hang: 'cho-review' })), 'cot:cho-review')
  assert.equal(chipCot(the({ hang: 'chua-cham' })), '')
  assert.equal(chipCot(null), '')
})

test('viTriThe và uuTien cho ngăn bên', () => {
  assert.equal(viTriThe(the({ hang: 'can-chot' })), 'cột 2')
  assert.equal(viTriThe(the({ hang: 'epic' })), 'Epic')
  assert.equal(uuTien(the()), 'P1')
  assert.equal(uuTien(the({ uu_tien: null })), 'P?')
})

test('chipThe: thứ tự cột → khoá → cờ đỏ → lệch → chưa giao → chờ → khe spec → chỉ quét thử → PR', () => {
  const t = the({ khoa: true, co_do: true, lech: true, khe_spec: true, cho: ['hr-2', 'hr-3'],
    giao: { khong_giao: 'thiếu tiêu chí', pr: { tram: { so: 12, trang_thai: 'da_merge', ly_do: '' } } } })
  assert.deepEqual(chipThe(t, true).map((c) => [c.chu, c.lop]), [
    ['cot:ai-lam', 'mono'], ['khoá', ''], ['cờ đỏ', 'tt-loi'], ['nhãn lệch', 'tt-cau_dao'], ['chưa giao', 'tt-cau_dao'],
    ['chờ hr-2, hr-3', ''], ['khe spec', ''], ['chỉ quét thử', 'tt-tat'], ['PR đã merge', 'pr-da_merge']])
  assert.equal(chipThe(t).find((c) => c.chu === 'chưa giao').goiY, 'thiếu tiêu chí')
  assert.deepEqual(chipThe(the({ hang: 'epic' })), [])
})

test('dongKhe ghép khe đang giữ phiếu đúng dự án + bead', () => {
  const ds = [
    { khe_id: 'B/codex-1', ten: 'Codex 1', trang_thai: 'can_nguoi',
      phieu: { du_an: 'hr', bead_id: 'hr-1', buoc: 'qc' } },
    { khe_id: 'B/claude-1', trang_thai: 'lam', phieu: { du_an: 'khac', bead_id: 'hr-1', buoc: 'code' } },
  ]
  assert.deepEqual(dongKhe(the(), ds), { ten: 'Codex 1', buoc: 'QC', canNguoi: true, mau: mauKhe('B/codex-1').than })
  assert.deepEqual(dongKhe(the({ du_an: 'khac' }), ds),
    { ten: 'Claude 1', buoc: 'code', canNguoi: false, mau: mauKhe('B/claude-1').than })
  assert.equal(dongKhe(the({ id: 'hr-9' }), ds), null)
  assert.equal(dongKhe(the(), [{ khe_id: 'x', phieu: null }]), null)
  assert.equal(dongKhe(the(), undefined), null)
})
```

- [ ] **Step 2: Chạy thấy FAIL**

```bash
cd frontend && node --test tests/cong_viec.test.mjs
```

Kỳ vọng: FAIL — `Error [ERR_MODULE_NOT_FOUND]: Cannot find module '…/frontend/src/luat_cong_viec.js' imported from …/frontend/tests/cong_viec.test.mjs`

- [ ] **Step 3: Viết mã (chép nguyên văn; file sửa: chép khối diff ra file tạm, `git apply --check` rồi `git apply`)**

`frontend/src/kieu/cong-viec.css` (mới):

```css
/* Trang Công việc + ngăn bên (mockup style.css mục "Công việc", `.ngan-ben`, `.dtg`). Độ đậm 650 → 600 (luật 4). */
.bang-cot { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; align-items: start; }
.cot {
  background: var(--nen-3); border: 1px solid var(--vien); border-radius: 14px; padding: 12px; min-height: 340px;
}
.cot-dau { display: flex; align-items: center; gap: 8px; padding: 2px 4px 12px; }
.cot-dau h3 { margin: 0; font-size: 15px; }
.cot-dau .so {
  margin-left: auto; font-size: 12px; font-weight: 700; color: var(--chu-2); background: var(--the);
  border: 1px solid var(--vien); border-radius: 999px; padding: 1px 9px;
}
.cot-dau .so-thu {
  width: 22px; height: 22px; border-radius: 6px; background: var(--nhan); color: #fff; display: grid;
  place-items: center; font-size: 12px; font-weight: 800;
}
.cot .mo-ta-cot { margin: -6px 4px 12px; }
.the-bead { cursor: pointer; display: flex; flex-direction: column; gap: 8px; margin-bottom: 10px; }
.the-bead:hover { border-color: var(--nhan); }
.the-bead .tren { display: flex; gap: 8px; align-items: center; font-size: 12.5px; }
.the-bead .tren .phai { margin-left: auto; white-space: nowrap; }
.the-bead .ma { font-family: var(--mono); color: var(--nhan); font-weight: 500; white-space: nowrap; }
.the-bead .tieu-de { font-weight: 600; font-size: 15px; line-height: 1.35; }
.the-bead .nhan-ds { display: flex; gap: 6px; flex-wrap: wrap; }
.the-bead .khe { font-size: 12.5px; color: var(--chu-2); display: flex; align-items: center; gap: 6px; }
.the-bead .khe .cham { margin: 0; }

/* Hàng Chưa chấm / Feature đang chạy plan / Epic — mockup không vẽ, giữ bố cục cũ (hàng thẻ ngang, D36). */
.hang-phu { margin-bottom: 18px; }
.hang-phu h2.muc { margin-top: 8px; }
.day-the { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 10px; }
.day-the .the-bead { margin-bottom: 0; }

.ngan-ben {
  position: fixed; right: 0; top: 0; bottom: 0; width: min(460px, 100vw); background: var(--the);
  border-left: 1px solid var(--vien-dam); box-shadow: -14px 0 40px #5a3a2222; z-index: 50; overflow-y: auto;
  padding: 20px 22px 30px;
}
.ngan-ben .dong {
  position: absolute; right: 14px; top: 12px; border: 0; background: none; font-size: 22px; color: var(--chu-phu);
}
.ngan-ben h2 { margin: 6px 0 6px; font-size: 21px; letter-spacing: -.3px; }
.ngan-ben h4 {
  margin: 18px 0 6px; font-size: 13px; text-transform: uppercase; letter-spacing: .6px; color: var(--chu-phu);
}
/* :where → độ ưu tiên 0, để .nho / .loi / .canh-bao của chung.css vẫn thắng. */
:where(.ngan-ben p, .ngan-ben li) { font-size: 14px; color: var(--chu-2); line-height: 1.5; }
.ngan-ben ul, .ngan-ben ol { margin: 0; padding-left: 18px; }
.ngan-ben a { color: var(--nhan); font-weight: 600; }
.ngan-ben .hang-chip { display: flex; gap: 6px; flex-wrap: wrap; }
.ngan-ben .cau-hoi { display: flex; flex-direction: column; gap: 6px; margin-bottom: 10px; font-size: 14px; }
.ngan-ben .lenh {
  font-family: var(--mono); font-size: 12.5px; background: var(--nen-lenh); color: var(--chu-lenh);
  border-radius: 8px; padding: 8px 10px; margin: 6px 0 0;
}
.ngan-ben .dtg { list-style: none; padding: 0; border-left: 2px solid var(--vien); margin-left: 4px; }
.dtg li { padding: 3px 0 3px 12px; position: relative; overflow-wrap: anywhere; }
.dtg li::before {
  content: ''; position: absolute; left: -5px; top: 10px; width: 8px; height: 8px; border-radius: 50%;
  background: var(--nhan);
}
.dtg .mono { font-size: 12px; color: var(--chu-phu); margin-right: 8px; }
.dtg strong { font-weight: 500; color: var(--chu); }

@media (max-width: 900px) { .bang-cot { grid-template-columns: 1fr; } }
.ngan-ben .truong textarea, .hop .truong textarea { font-weight: 400; }
```

`frontend/src/luat_cong_viec.js` (mới):

```js
// Luật hiển thị trang Công việc + ngăn bên (mockup trang.js COT, theBead, moBead) — thuần, test bằng node --test.
import { lopPrTram, nhanPrTram, prTram } from './giao_viec.js'
import { TEN_HANG } from './luat.js'
import { tenKhe } from './luat_han_muc.js'
import { mauKhe } from './mau_khe.js'

export const MO_TA_TRANG = 'Ba cột do trạm chấm; kéo thẻ giữa cột 1 và 2 để sửa, cột 3 do thợ và Phê duyệt quản.'

// Ba cột chính (mockup trang.js COT): hàng của API → số thứ tự, tên, mô tả dưới đầu cột.
export const COT = [
  { hang: 'ai-lam', so: 1, ten: 'AI tự làm', moTa: 'Trạm giao cho khe theo luật vai' },
  { hang: 'can-chot', so: 2, ten: 'Cần Đại ca chốt', moTa: 'Có câu hỏi hoặc rủi ro nghiệp vụ' },
  { hang: 'cho-review', so: 3, ten: 'Chờ review để đóng', moTa: 'Đã code + QC, chờ Duyệt' },
]
const SO_COT = Object.fromEntries(COT.map((c) => [c.hang, c.so]))
const TEN_BUOC = { spec: 'spec', code: 'code', qc: 'QC' }     // mockup du-lieu.js TEN_BUOC

// API không trả danh sách nhãn — suy chip `cot:<hang>` từ hang (khảo sát §1.3); hàng ngoài ba cột không có nhãn cột.
export function chipCot(the) {
  return the && SO_COT[the.hang] ? `cot:${the.hang}` : ''
}

// Dòng đầu ngăn bên "du_an · id · cột n" (mockup moBead); hàng phụ (Chưa chấm, Epic…) ghi tên hàng.
export function viTriThe(the) {
  return SO_COT[the.hang] ? `cột ${SO_COT[the.hang]}` : TEN_HANG[the.hang] ?? TEN_HANG['chua-cham']
}

export function uuTien(the) {
  return `P${the.uu_tien ?? '?'}`
}

// Chip trên thẻ (mockup theBead `.nhan-ds`) + chip của bản cũ phải giữ (khảo sát §1.3, D36, D37). {chu, lop, goiY}.
export function chipThe(the, chiQuetThu = false) {
  const ds = []
  const them = (chu, lop = '', goiY = '') => ds.push({ chu, lop, goiY })
  if (chipCot(the)) them(chipCot(the), 'mono')
  if (the.khoa) them('khoá', '', 'Đại ca đã khoá cột')
  if (the.co_do) them('cờ đỏ', 'tt-loi')
  if (the.lech) them('nhãn lệch', 'tt-cau_dao', 'Nhiều nhãn cột')
  if (the.giao && the.giao.khong_giao) them('chưa giao', 'tt-cau_dao', the.giao.khong_giao)
  if (the.cho && the.cho.length) them(`chờ ${the.cho.join(', ')}`)
  if (the.khe_spec) them('khe spec')
  if (chiQuetThu) them('chỉ quét thử', 'tt-tat', 'bat_ghi: false — trạm từ chối thao tác ghi')
  if (nhanPrTram(the)) them(nhanPrTram(the), lopPrTram(prTram(the)))
  return ds
}

// Dòng "Claude 1 · code · đang hỏi Đại ca" (mockup theBead `.khe`): ghép phía trình duyệt với /api/doi-ngu
// theo khe.phieu {du_an, bead_id} (khảo sát T7). Không khe nào giữ bead → null.
export function dongKhe(the, dsKhe) {
  const khe = (dsKhe || []).find((k) => k.phieu && k.phieu.du_an === the.du_an && k.phieu.bead_id === the.id)
  if (!khe) return null
  const buoc = khe.phieu.buoc
  return { ten: tenKhe(khe), buoc: TEN_BUOC[buoc] ?? buoc ?? '', canNguoi: khe.trang_thai === 'can_nguoi',
    mau: mauKhe(khe.khe_id).than }
}
```

`frontend/src/thanh/DongThoiGian.vue` (sửa):

```diff
diff --git a/frontend/src/thanh/DongThoiGian.vue b/frontend/src/thanh/DongThoiGian.vue
index 6d7d102..7a1698f 100644
--- a/frontend/src/thanh/DongThoiGian.vue
+++ b/frontend/src/thanh/DongThoiGian.vue
@@ -1,4 +1,6 @@
 <script setup>
+// Dòng thời gian trong ngăn bên (mockup trang.js moBead `.dtg`: giờ mono + loại + tóm tắt). Mới nhất lên trước như cũ.
+import { ngayGio } from '../dinh_dang.js'
 import { gioVN } from '../luat.js'
 
 defineProps({ ds: { type: Array, required: true } })
@@ -6,12 +8,12 @@ defineProps({ ds: { type: Array, required: true } })
 
 <template>
   <section>
-    <h3>Dòng thời gian</h3>
+    <h4>Dòng thời gian</h4>
     <p v-if="!ds.length" class="nho">Chưa có sự kiện.</p>
-    <ol v-else class="dong-thoi-gian" reversed>
+    <ol v-else class="dtg" reversed>
       <li v-for="s in [...ds].reverse()" :key="s.id">
-        <span class="nho">{{ gioVN(s.luc) }} · {{ s.tac_nhan }}</span> <strong>{{ s.loai }}</strong>
-        <span class="van-ban">{{ s.tom_tat }}</span>
+        <span class="mono" :title="gioVN(s.luc)">{{ ngayGio(s.luc) }}</span><strong>{{ s.loai }}</strong>
+        {{ s.tom_tat }} <span class="nho">· {{ s.tac_nhan }}</span>
       </li>
     </ol>
   </section>
```

`frontend/src/thanh/HopViSao.vue` (sửa):

```diff
diff --git a/frontend/src/thanh/HopViSao.vue b/frontend/src/thanh/HopViSao.vue
index 40f051b..02b1f14 100644
--- a/frontend/src/thanh/HopViSao.vue
+++ b/frontend/src/thanh/HopViSao.vue
@@ -1,4 +1,5 @@
 <script setup>
+// Hộp "Vì sao?" khi kéo thẻ giữa cột 1–2 (mockup không vẽ, giữ bố cục cũ; lớp mockup .nen-mo .hop .truong — D36).
 import { ref } from 'vue'
 import { TEN_HANG } from '../luat.js'
 
@@ -11,11 +12,12 @@ const viSao = ref('')
   <div class="nen-mo" role="dialog" aria-modal="true" aria-labelledby="hop-vi-sao-td" @keydown.esc="emit('huy')">
     <form class="hop" @submit.prevent="emit('xac-nhan', viSao.trim())">
       <h2 id="hop-vi-sao-td">Chuyển {{ the.id }} sang "{{ TEN_HANG[cot] }}"</h2>
-      <label>Vì sao? (tuỳ chọn)<textarea v-model="viSao" rows="3" maxlength="2000" autofocus></textarea></label>
+      <label class="truong">Vì sao? (tuỳ chọn)
+        <textarea v-model="viSao" rows="3" maxlength="2000" autofocus></textarea></label>
       <p class="nho">Bead sẽ được khoá cột (cot-khoa); bộ chấm không lật lại cho tới khi Đại ca gỡ khoá.</p>
-      <div class="nut">
-        <button type="button" @click="emit('huy')">Huỷ</button>
-        <button type="submit">Chuyển cột</button>
+      <div class="hang-nut">
+        <button class="nut" type="button" @click="emit('huy')">Huỷ</button>
+        <button class="nut chinh" type="submit">Chuyển cột</button>
       </div>
     </form>
   </div>
```

`frontend/src/thanh/OChot.vue` (sửa):

```diff
diff --git a/frontend/src/thanh/OChot.vue b/frontend/src/thanh/OChot.vue
index b33bdd9..8e21803 100644
--- a/frontend/src/thanh/OChot.vue
+++ b/frontend/src/thanh/OChot.vue
@@ -1,8 +1,14 @@
 <script setup>
+// Ô chốt câu hỏi (mockup trang.js moBead, anh-cong-viec-ngan-ben.png): mỗi câu một nhãn "1. …" + ô "Trả lời…",
+// nút "Chốt" và "Dẫn ADR" (chuyển sang ô mã ADR). Gửi {tra_loi[]} hoặc {adr} như cũ.
 import { ref, watch } from 'vue'
 
 const CAU_CHUNG = 'Chốt chung cho bead (lần chấm không có câu hỏi cụ thể)'
-const props = defineProps({ cauHoi: { type: Array, required: true }, gui: { type: Function, required: true } })
+const props = defineProps({
+  cauHoi: { type: Array, required: true },
+  gui: { type: Function, required: true },
+  khoa: { type: Boolean, default: false },      // dự án chỉ quét thử (D37)
+})
 const traLoi = ref([])
 const adr = ref('')
 const dungAdr = ref(false)
@@ -12,7 +18,7 @@ watch(() => props.cauHoi, () => { traLoi.value = cau().map(() => '') }, { immedi
 const du = () => (dungAdr.value ? /^ADR-\d{4}$/.test(adr.value.trim()) : traLoi.value.every((t) => t.trim()))
 
 async function chot() {
-  if (!du() || dangGui.value) return
+  if (!du() || dangGui.value || props.khoa) return
   dangGui.value = true
   try {
     await props.gui(dungAdr.value ? { adr: adr.value.trim() } : { tra_loi: traLoi.value.map((t) => t.trim()) })
@@ -26,14 +32,17 @@ async function chot() {
 
 <template>
   <form class="o-chot" @submit.prevent="chot">
-    <h3>Trả lời câu hỏi cần chốt</h3>
-    <label><input type="checkbox" v-model="dungAdr">Dẫn ADR thay cho trả lời (câu trả lời dài / kiến trúc)</label>
-    <label v-if="dungAdr">Mã ADR<input v-model="adr" placeholder="ADR-0000" maxlength="8" required></label>
+    <label v-if="dungAdr" class="cau-hoi"><span>Mã ADR <span class="nho">— dẫn ADR thay cho trả lời (câu trả lời dài /
+      kiến trúc)</span></span><input v-model="adr" class="o" placeholder="ADR-0000" maxlength="8" required></label>
     <template v-else>
-      <label v-for="(q, i) in cau()" :key="i">{{ q }}
-        <textarea v-model="traLoi[i]" rows="2" maxlength="4000" required></textarea></label>
+      <label v-for="(q, i) in cau()" :key="i" class="cau-hoi"><span><b>{{ i + 1 }}.</b> {{ q }}</span>
+        <textarea v-model="traLoi[i]" rows="2" maxlength="4000" placeholder="Trả lời…" required></textarea></label>
     </template>
-    <button type="submit" :disabled="dangGui || !du()">Chốt</button>
+    <div class="hang-nut">
+      <button class="nut chinh" type="submit" :disabled="khoa || dangGui || !du()">Chốt</button>
+      <button class="nut" type="button" :aria-pressed="dungAdr ? 'true' : 'false'" @click="dungAdr = !dungAdr">
+        {{ dungAdr ? 'Trả lời từng câu' : 'Dẫn ADR' }}</button>
+    </div>
     <p class="nho">Tạo bead decision đã đóng, nối vào bead này, gỡ nhãn cột; lượt quét sau chấm lại.</p>
   </form>
 </template>
```

`frontend/src/thanh/OGiaoViec.vue` (sửa):

```diff
diff --git a/frontend/src/thanh/OGiaoViec.vue b/frontend/src/thanh/OGiaoViec.vue
index eb8c1be..4b09cb2 100644
--- a/frontend/src/thanh/OGiaoViec.vue
+++ b/frontend/src/thanh/OGiaoViec.vue
@@ -1,6 +1,8 @@
 <script setup>
+// Bộ giao việc trong ngăn bên. PR trạm mở vẽ theo khối "PR" của mockup trang.js moBead (chip + "PR #12 — lý do");
+// phần còn lại (chưa giao, lệnh gh pr create) giữ bố cục cũ, chỉ áp lớp mới (D36).
 import { computed } from 'vue'
-import { canhBaoPr, canhBaoPrTram, moTaPrTram, nhanPrTram } from '../giao_viec.js'
+import { canhBaoPr, canhBaoPrTram, lopPrTram, moTaPrTram, nhanPrTram } from '../giao_viec.js'
 import { laLinkAnToan } from '../luat.js'
 
 const props = defineProps({ giao: { type: Object, required: true } })
@@ -11,22 +13,25 @@ const nhanTram = computed(() => nhanPrTram({ giao: props.giao }))
 
 <template>
   <section aria-label="Bộ giao việc">
-    <h3>Bộ giao việc</h3>
-    <p v-if="giao.khong_giao" class="canh-bao">Chưa giao: {{ giao.khong_giao }}</p>
     <template v-if="tram">
-      <p class="nho">{{ nhanTram }} · {{ moTaPrTram(tram) }}</p>
+      <h4>PR</h4>
+      <p><span v-if="nhanTram" class="chip" :class="lopPrTram(tram)">{{ nhanTram }}</span> {{ moTaPrTram(tram) }}</p>
       <p v-if="canhBaoPrTram(tram)" class="canh-bao" role="alert">{{ canhBaoPrTram(tram) }}</p>
       <p v-if="laLinkAnToan(tram.url)">
         <a :href="tram.url" target="_blank" rel="noopener noreferrer">Mở PR trên GitHub</a>
       </p>
     </template>
-    <template v-else-if="giao.pr">
-      <p class="nho">Tạo PR từ nhánh {{ giao.pr.nhanh }} tại commit {{ giao.pr.commit }} (trạm đã kiểm lại và QC).</p>
-      <p v-if="canhBao" class="canh-bao" role="alert">{{ canhBao }}</p>
-      <p v-else-if="laLinkAnToan(giao.pr.link)">
-        <a :href="giao.pr.link" target="_blank" rel="noopener noreferrer">Mở trang tạo PR trên GitHub</a>
-      </p>
-      <pre class="van-ban">{{ giao.pr.lenh }}</pre>
+    <template v-if="giao.khong_giao || (!tram && giao.pr)">
+      <h4>Bộ giao việc</h4>
+      <p v-if="giao.khong_giao" class="canh-bao">Chưa giao: {{ giao.khong_giao }}</p>
+      <template v-if="!tram && giao.pr">
+        <p class="nho">Tạo PR từ nhánh {{ giao.pr.nhanh }} tại commit {{ giao.pr.commit }} (trạm đã kiểm lại và QC).</p>
+        <p v-if="canhBao" class="canh-bao" role="alert">{{ canhBao }}</p>
+        <p v-else-if="laLinkAnToan(giao.pr.link)">
+          <a :href="giao.pr.link" target="_blank" rel="noopener noreferrer">Mở trang tạo PR trên GitHub</a>
+        </p>
+        <pre class="van-ban lenh">{{ giao.pr.lenh }}</pre>
+      </template>
     </template>
   </section>
 </template>
```

`frontend/src/thanh/OTraLoi.vue` (sửa):

```diff
diff --git a/frontend/src/thanh/OTraLoi.vue b/frontend/src/thanh/OTraLoi.vue
index 240352a..ec530da 100644
--- a/frontend/src/thanh/OTraLoi.vue
+++ b/frontend/src/thanh/OTraLoi.vue
@@ -1,7 +1,7 @@
 <script setup>
 import { ref } from 'vue'
 
-// Nút Trả lời escalation / decision mở (spec 2 §5.2) — dùng ở ngăn bên và trang Phê duyệt.
+// Nút Trả lời escalation / decision mở (spec 2 §5.2) — dùng ở ngăn bên và trang Phê duyệt. Lớp mockup: .truong .nut.
 const props = defineProps({
   gui: { type: Function, required: true },          // (traLoi) => Promise<boolean>; false = lỗi, giữ nội dung
   khoa: { type: Boolean, default: false },
@@ -24,8 +24,10 @@ async function guiTraLoi() {
 
 <template>
   <form class="o-tra-loi" @submit.prevent="guiTraLoi">
-    <label>Trả lời<textarea v-model="traLoi" rows="3" maxlength="4000" required></textarea></label>
-    <button type="submit" :disabled="khoa || dangGui || !traLoi.trim()">{{ nhan }}</button>
+    <label class="truong">Trả lời<textarea v-model="traLoi" rows="3" maxlength="4000" required></textarea></label>
+    <div class="hang-nut">
+      <button class="nut chinh" type="submit" :disabled="khoa || dangGui || !traLoi.trim()">{{ nhan }}</button>
+    </div>
     <p class="nho">Đóng chính bead quyết định, câu trả lời thành lý do đóng. Câu trả lời không cấp quyền làm thao tác
       nguy hiểm (deploy, migrate DB thật, xoá dữ liệu, gửi khách).</p>
   </form>
```

`frontend/src/thanh/TheBead.vue` (sửa):

```diff
diff --git a/frontend/src/thanh/TheBead.vue b/frontend/src/thanh/TheBead.vue
index 80fd1fb..97cfa10 100644
--- a/frontend/src/thanh/TheBead.vue
+++ b/frontend/src/thanh/TheBead.vue
@@ -1,11 +1,18 @@
 <script setup>
+// Thẻ bead (mockup trang.js theBead, anh-cong-viec.png); chip của bản cũ giữ theo khảo sát §1.3 + D37.
 import { computed } from 'vue'
-import { nhanPrTram, prTram } from '../giao_viec.js'
+import { chipThe, uuTien } from '../luat_cong_viec.js'
+import { kho } from '../kho.js'
 
-const props = defineProps({ the: { type: Object, required: true } })
+const props = defineProps({
+  the: { type: Object, required: true },
+  khe: { type: Object, default: null },          // dongKhe(): {ten, buoc, canNguoi, mau} | null
+  chiQuetThu: { type: Boolean, default: false },  // dự án bat_ghi: false — không kéo được
+})
 const emit = defineEmits(['mo', 'keo'])
-const nhanPr = computed(() => nhanPrTram(props.the))
-const prVang = computed(() => prTram(props.the)?.trang_thai === 'khong_xac_minh')
+const chip = computed(() => chipThe(props.the, props.chiQuetThu))
+const keoDuoc = computed(() => props.the.keo_duoc && !props.chiQuetThu && Boolean(kho.trangThai?.la_dai_ca))
 
 function batDauKeo(e) {
+  if (!keoDuoc.value) { e.preventDefault(); return }
   e.dataTransfer.setData('text/plain', props.the.id)   // Firefox chỉ bắt đầu kéo khi có dữ liệu (N2)
@@ -15,19 +22,20 @@ function batDauKeo(e) {
 </script>
 
 <template>
-  <article class="the" :class="{ mo: the.mo, lech: the.lech }" tabindex="0" :draggable="the.keo_duoc ? 'true' : 'false'"
+  <article class="the the-bead" :class="{ mo: the.mo }" tabindex="0" :draggable="keoDuoc ? 'true' : 'false'"
            :aria-label="the.id + ': ' + the.tieu_de" @click="emit('mo')" @keydown.enter="emit('mo')"
            @dragstart="batDauKeo">
-    <header>
-      <span class="ma">{{ the.id }}</span> <span class="nho">{{ the.du_an }}</span>
-      <span v-if="the.khoa" class="nhan-nho" title="Đại ca đã khoá cột">khoá</span>
-      <span v-if="the.co_do" class="nhan-nho do">cờ đỏ</span>
-      <span v-if="the.lech" class="nhan-nho vang" title="Nhiều nhãn cột">nhãn lệch</span>
-      <span v-if="the.giao && the.giao.khong_giao" class="nhan-nho vang" :title="the.giao.khong_giao">chưa giao</span>
-      <span v-if="nhanPr" class="nhan-nho" :class="{ vang: prVang }">{{ nhanPr }}</span>
-    </header>
-    <p class="tieu-de">{{ the.tieu_de }}</p>
-    <footer class="nho">{{ the.loai }} · P{{ the.uu_tien ?? '?' }}<span v-if="the.khe_spec"> · khe spec</span><span
-      v-if="the.cho.length"> · chờ {{ the.cho.join(', ') }}</span></footer>
+    <div class="tren">
+      <span class="ma">{{ the.id }}</span><span class="chip">{{ the.du_an }}</span>
+      <span class="nho phai">{{ the.loai }} · {{ uuTien(the) }}</span>
+    </div>
+    <div class="tieu-de">{{ the.tieu_de }}</div>
+    <div v-if="chip.length" class="nhan-ds">
+      <span v-for="c in chip" :key="c.chu" class="chip" :class="c.lop" :title="c.goiY || null">{{ c.chu }}</span>
+    </div>
+    <div v-if="khe" class="khe">
+      <span class="cham" :style="{ background: khe.mau }"></span>{{ khe.buoc ? `${khe.ten} · ${khe.buoc}` : khe.ten }}
+      <template v-if="khe.canNguoi"> · <b class="chu-do">đang hỏi Đại ca</b></template>
+    </div>
   </article>
 </template>
```

`frontend/src/trang/CongViec.vue` (sửa):

```diff
diff --git a/frontend/src/trang/CongViec.vue b/frontend/src/trang/CongViec.vue
index e1cf8f4..752bb39 100644
--- a/frontend/src/trang/CongViec.vue
+++ b/frontend/src/trang/CongViec.vue
@@ -1,25 +1,36 @@
 <script setup>
+// Trang Công việc (mockup trang.js veCongViec, anh-cong-viec.png). Phần mockup không vẽ (hàng Chưa chấm / theo plan /
+// Epic, kéo thẻ + hộp Vì sao?, lỗi từng dự án) giữ bố cục cũ, chỉ áp lớp mới (D36).
 import { computed, onMounted, ref, watch } from 'vue'
 import { useRoute } from 'vue-router'
 import { doc, ghi, thanGhi } from '../api.js'
 import { ganGiaoViec } from '../giao_viec.js'
 import { kho } from '../kho.js'
-import { HANG_COT, TEN_HANG, choPhepKeo, nhomTheoHang } from '../luat.js'
+import { TEN_HANG, choPhepKeo, duAnChiQuetThu, nhomTheoHang } from '../luat.js'
+import { COT, MO_TA_TRANG, dongKhe } from '../luat_cong_viec.js'
+import DauTrang from '../thanh/DauTrang.vue'
 import HopViSao from '../thanh/HopViSao.vue'
 import TheBead from '../thanh/TheBead.vue'
 import NganBen from './NganBen.vue'
+import '../kieu/cong-viec.css'
 
 const route = useRoute()
 const tuDiaChi = (x) => (typeof x === 'string' ? x : '')
 const duAn = ref(tuDiaChi(route.query.du_an))       // lát 2c: /cong-viec?du_an=<dự án>[&bead=<id>] từ Văn phòng
 const dsDuAn = ref([])
 const dsThe = ref([])
+const dsKhe = ref([])
 const loiDoc = ref({})
 const thongBao = ref('')
 const dangKeo = ref(null)
 const keoCho = ref(null)
 const chon = ref(null)
 const nhom = computed(() => nhomTheoHang(dsThe.value))
+const chiQuetThu = computed(() => duAnChiQuetThu(dsDuAn.value))     // D37: bat_ghi false → chỉ quét thử
+const laDaiCa = computed(() => Boolean(kho.trangThai?.la_dai_ca))
+const rong = computed(() => `Không có bead${duAn.value ? ` của ${duAn.value}` : ''}`)
+const tenChon = (d) => `${d.ten}${d.bat_ghi === false ? ' (chỉ quét thử)' : ''}`
+const thuocTinh = (t) => ({ the: t, khe: dongKhe(t, dsKhe.value), chiQuetThu: chiQuetThu.value.has(t.du_an) })
 
 async function tai() {
   try {
@@ -33,9 +44,14 @@ async function tai() {
     thongBao.value = e.message
   }
 }
+// Dòng khe đang giữ trên thẻ: ghép với /api/doi-ngu phía trình duyệt (khảo sát T7); lỗi thì bỏ dòng khe, không báo.
+async function taiKhe() {
+  dsKhe.value = await doc('/api/doi-ngu').then((r) => r.khe || [], () => [])
+}
 onMounted(async () => {
+  taiKhe()
   try {
-    dsDuAn.value = (await doc('/api/du-an')).du_an.map((d) => d.ten)
+    dsDuAn.value = (await doc('/api/du-an')).du_an
   } catch (e) {
     thongBao.value = e.message
   }
@@ -43,6 +59,7 @@ onMounted(async () => {
   moTheoDiaChi()
 })
 watch([duAn, () => kho.phienBan], tai)
+watch(() => kho.phienBanDoiNgu, taiKhe)
 watch(() => route.fullPath, async () => { duAn.value = tuDiaChi(route.query.du_an); await tai(); moTheoDiaChi() })
 
 // Mở ngăn bên đúng một lần mỗi lần địa chỉ đổi (Đại ca đóng ngăn thì lượt tải lại sau không mở lại).
@@ -53,7 +70,12 @@ function moTheoDiaChi() {
 }
 
 function tha(hang) {
-  if (choPhepKeo(dangKeo.value, hang)) keoCho.value = { the: dangKeo.value, cot: hang }
+  const t = dangKeo.value
+  if (laDaiCa.value && choPhepKeo(t, hang) && !chiQuetThu.value.has(t.du_an)) keoCho.value = { the: t, cot: hang }
   dangKeo.value = null
 }
 async function xacNhanKeo(viSao) {
+  if (!keoCho.value || !laDaiCa.value || chiQuetThu.value.has(keoCho.value.the.du_an)) {
+    keoCho.value = null
+    return
+  }
@@ -71,30 +93,37 @@ async function xacNhanKeo(viSao) {
 </script>
 
 <template>
-  <section class="cong-viec">
-    <div class="cong-cu">
-      <label>Dự án
-        <select v-model="duAn"><option value="">Tất cả</option>
-          <option v-for="d in dsDuAn" :key="d" :value="d">{{ d }}</option></select>
-      </label>
-      <span v-for="(l, t) in loiDoc" :key="t" class="loi">{{ t }}: {{ l }}</span>
-      <span v-if="thongBao" class="loi" role="alert">{{ thongBao }}</span>
-    </div>
-    <section v-if="nhom['chua-cham'].length" class="hang-ngang" :aria-label="TEN_HANG['chua-cham']">
-      <h2>{{ TEN_HANG['chua-cham'] }} <span class="dem-nho">{{ nhom['chua-cham'].length }}</span></h2>
-      <div class="day"><TheBead v-for="t in nhom['chua-cham']" :key="t.du_an + '/' + t.id" :the="t" @mo="chon = t" /></div>
-    </section>
-    <div class="ba-cot">
-      <section v-for="h in HANG_COT" :key="h" class="cot" :aria-label="TEN_HANG[h]" @dragover.prevent @drop.prevent="tha(h)">
-        <h2>{{ TEN_HANG[h] }} <span class="dem-nho">{{ nhom[h].length }}</span></h2>
-        <TheBead v-for="t in nhom[h]" :key="t.du_an + '/' + t.id" :the="t" @mo="chon = t" @keo="dangKeo = t" />
-      </section>
-    </div>
-    <section v-for="h in ['theo-plan', 'epic']" :key="h" v-show="nhom[h].length" class="hang-ngang" :aria-label="TEN_HANG[h]">
-      <h2>{{ TEN_HANG[h] }} <span class="dem-nho">{{ nhom[h].length }}</span></h2>
-      <div class="day"><TheBead v-for="t in nhom[h]" :key="t.du_an + '/' + t.id" :the="t" @mo="chon = t" /></div>
+  <DauTrang tieu-de="Công việc" :mo-ta="MO_TA_TRANG">
+    <template #cong-cu>
+      <select v-model="duAn" aria-label="Dự án"><option value="">Tất cả dự án</option>
+        <option v-for="d in dsDuAn" :key="d.ten" :value="d.ten">{{ tenChon(d) }}</option></select>
+    </template>
+  </DauTrang>
+  <p v-for="(l, t) in loiDoc" :key="t" class="loi">{{ t }}: {{ l }}</p>
+  <p v-if="thongBao" class="loi" role="alert">{{ thongBao }}</p>
+  <section v-if="nhom['chua-cham'].length" class="hang-phu" :aria-label="TEN_HANG['chua-cham']">
+    <h2 class="muc">{{ TEN_HANG['chua-cham'] }} <span class="so">{{ nhom['chua-cham'].length }}</span></h2>
+    <div class="day-the"><TheBead v-for="t in nhom['chua-cham']" :key="t.du_an + '/' + t.id" v-bind="thuocTinh(t)"
+                                  @mo="chon = t" /></div>
+  </section>
+  <div class="bang-cot">
+    <section v-for="c in COT" :key="c.hang" class="cot" :aria-label="c.ten" @dragover.prevent
+             @drop.prevent="tha(c.hang)">
+      <div class="cot-dau"><span class="so-thu">{{ c.so }}</span><h3>{{ c.ten }}</h3>
+        <span class="so">{{ nhom[c.hang].length }}</span></div>
+      <p class="nho mo-ta-cot">{{ c.moTa }}</p>
+      <TheBead v-for="t in nhom[c.hang]" :key="t.du_an + '/' + t.id" v-bind="thuocTinh(t)" @mo="chon = t"
+               @keo="dangKeo = t" />
+      <div v-if="!nhom[c.hang].length" class="cot-rong">{{ rong }}</div>
     </section>
-    <NganBen v-if="chon" :the="chon" @dong="chon = null" @chuyen="(cot) => (keoCho = { the: chon, cot })" @doi="tai" />
-    <HopViSao v-if="keoCho" :the="keoCho.the" :cot="keoCho.cot" @huy="keoCho = null" @xac-nhan="xacNhanKeo" />
+  </div>
+  <section v-for="h in ['theo-plan', 'epic']" v-show="nhom[h].length" :key="h" class="hang-phu"
+           :aria-label="TEN_HANG[h]">
+    <h2 class="muc">{{ TEN_HANG[h] }} <span class="so">{{ nhom[h].length }}</span></h2>
+    <div class="day-the"><TheBead v-for="t in nhom[h]" :key="t.du_an + '/' + t.id" v-bind="thuocTinh(t)"
+                                  @mo="chon = t" /></div>
   </section>
+  <NganBen v-if="chon" :the="chon" :chi-quet-thu="chiQuetThu.has(chon.du_an)" @dong="chon = null"
+           @chuyen="(cot) => (keoCho = { the: chon, cot })" @doi="tai" />
+  <HopViSao v-if="keoCho && laDaiCa && !chiQuetThu.has(keoCho.the.du_an)" :the="keoCho.the" :cot="keoCho.cot" @huy="keoCho = null" @xac-nhan="xacNhanKeo" />
 </template>
```

`frontend/src/trang/NganBen.vue` (sửa):

```diff
diff --git a/frontend/src/trang/NganBen.vue b/frontend/src/trang/NganBen.vue
index c42aebb..fe993cc 100644
--- a/frontend/src/trang/NganBen.vue
+++ b/frontend/src/trang/NganBen.vue
@@ -1,18 +1,23 @@
 <script setup>
-import { ref, watch } from 'vue'
+// Ngăn bên chi tiết bead (mockup trang.js moBead, anh-cong-viec-ngan-ben.png). Nút chuyển cột, trả lời decision,
+// Bàn giao, Bộ giao việc giữ bố cục cũ, chỉ áp lớp mới (D36). Dự án chỉ quét thử: khoá nút ghi (D37).
+import { computed, ref, watch } from 'vue'
 import { doc, ghi, thanGhi } from '../api.js'
 import { kho } from '../kho.js'
-import { gioVN, laLinkAnToan } from '../luat.js'
+import { CHU_CHI_QUET_THU, gioVN, laLinkAnToan } from '../luat.js'
+import { chipCot, uuTien, viTriThe } from '../luat_cong_viec.js'
 import DongThoiGian from '../thanh/DongThoiGian.vue'
 import OGiaoViec from '../thanh/OGiaoViec.vue'
 import OChot from '../thanh/OChot.vue'
 import OTraLoi from '../thanh/OTraLoi.vue'
 
-const props = defineProps({ the: { type: Object, required: true } })
+const props = defineProps({ the: { type: Object, required: true }, chiQuetThu: { type: Boolean, default: false } })
 const emit = defineEmits(['dong', 'chuyen', 'doi'])
 const ct = ref(null)
 const loi = ref('')
 const duongDan = () => `${encodeURIComponent(props.the.du_an)}/${encodeURIComponent(props.the.id)}`
+const laDaiCa = computed(() => Boolean(kho.trangThai && kho.trangThai.la_dai_ca))
+const cauHoi = computed(() => (ct.value && ct.value.cham_gan_nhat ? ct.value.cham_gan_nhat.cau_hoi : []))
 
 async function tai() {
   try {
@@ -30,3 +35,4 @@
 async function gui(duong, noiDung) {
+  if (!laDaiCa.value || props.chiQuetThu) return false
   try {
     await ghi(duong, thanGhi(noiDung, ct.value.the.updated_at))
@@ -50,29 +56,44 @@ const traLoi = (vb) => gui(`/api/phe-duyet/${duongDan()}/tra-loi`, { tra_loi: vb
     <button class="dong" type="button" aria-label="Đóng ngăn chi tiết" @click="emit('dong')">×</button>
     <p v-if="loi" class="loi" role="alert">{{ loi }}</p>
     <template v-if="ct">
-      <h2>{{ ct.the.id }} · {{ ct.the.tieu_de }}</h2>
-      <p class="nho">{{ ct.the.du_an }} · {{ ct.the.loai }} · P{{ ct.the.uu_tien ?? '?' }} · cập nhật {{ gioVN(ct.the.updated_at) }}</p>
-      <div v-if="ct.the.keo_duoc" class="nut">
-        <button v-if="ct.the.hang !== 'ai-lam'" type="button" @click="emit('chuyen', 'ai-lam')">Chuyển sang cột 1</button>
-        <button v-if="ct.the.hang !== 'can-chot'" type="button" @click="emit('chuyen', 'can-chot')">Chuyển sang cột 2</button>
+      <div class="nho mono">{{ ct.the.du_an }} · {{ ct.the.id }} · {{ viTriThe(ct.the) }}</div>
+      <h2>{{ ct.the.tieu_de }}</h2>
+      <div class="hang-chip">
+        <span v-if="chipCot(ct.the)" class="chip mono">{{ chipCot(ct.the) }}</span>
+        <span class="chip">{{ ct.the.loai }}</span><span class="chip">{{ uuTien(ct.the) }}</span>
+        <span v-if="chiQuetThu" class="chip tt-tat">chỉ quét thử</span>
       </div>
-      <section v-if="ct.cham_gan_nhat">
-        <h3>Lần chấm gần nhất · {{ gioVN(ct.cham_gan_nhat.luc) }}</h3>
+      <p class="nho">cập nhật {{ gioVN(ct.the.updated_at) }}</p>
+      <p v-if="chiQuetThu" class="canh-bao">{{ CHU_CHI_QUET_THU }}</p>
+      <div v-if="ct.the.keo_duoc" class="hang-nut">
+        <button v-if="ct.the.hang !== 'ai-lam'" class="nut" type="button" :disabled="chiQuetThu || !laDaiCa"
+                @click="emit('chuyen', 'ai-lam')">Chuyển sang cột 1</button>
+        <button v-if="ct.the.hang !== 'can-chot'" class="nut" type="button" :disabled="chiQuetThu || !laDaiCa"
+                @click="emit('chuyen', 'can-chot')">Chuyển sang cột 2</button>
+      </div>
+      <template v-if="ct.cham_gan_nhat">
+        <h4>Lý do lần chấm gần nhất</h4>
         <p class="van-ban">{{ ct.cham_gan_nhat.ly_do }}</p>
-        <ol v-if="ct.cham_gan_nhat.cau_hoi.length"><li v-for="(q, i) in ct.cham_gan_nhat.cau_hoi" :key="i">{{ q }}</li></ol>
-      </section>
-      <OChot v-if="ct.the.chot_duoc" :cau-hoi="ct.cham_gan_nhat ? ct.cham_gan_nhat.cau_hoi : []" :gui="chot" />
-      <OTraLoi v-if="ct.the.tra_loi_duoc" :gui="traLoi" :khoa="!(kho.trangThai && kho.trangThai.la_dai_ca)"
-               nhan="Trả lời (đóng decision)" />
-      <section v-if="ct.ban_giao">
-        <h3>Bàn giao</h3>
-        <p v-if="laLinkAnToan(ct.ban_giao.pr)"><a :href="ct.ban_giao.pr" target="_blank" rel="noopener noreferrer">Mở PR</a></p>
+        <p class="nho">{{ gioVN(ct.cham_gan_nhat.luc) }}</p>
+      </template>
+      <template v-if="ct.the.chot_duoc || cauHoi.length">
+        <h4>Câu hỏi cần chốt</h4>
+        <OChot v-if="ct.the.chot_duoc" :cau-hoi="cauHoi" :gui="chot" :khoa="chiQuetThu || !laDaiCa" />
+        <ol v-else><li v-for="(q, i) in cauHoi" :key="i">{{ q }}</li></ol>
+      </template>
+      <OTraLoi v-if="ct.the.tra_loi_duoc" :gui="traLoi" :khoa="chiQuetThu || !laDaiCa" nhan="Trả lời (đóng decision)" />
+      <template v-if="ct.ban_giao">
+        <h4>Bàn giao</h4>
         <p class="nho">Nhánh {{ ct.ban_giao.nhanh || '—' }} · commit {{ ct.ban_giao.commit || '—' }}</p>
+        <p v-if="laLinkAnToan(ct.ban_giao.pr)">
+          <a :href="ct.ban_giao.pr" target="_blank" rel="noopener noreferrer">Mở PR</a></p>
         <ul v-if="ct.ban_giao.loi.length" class="canh-bao"><li v-for="l in ct.ban_giao.loi" :key="l">{{ l }}</li></ul>
-      </section>
+      </template>
       <OGiaoViec v-if="the.giao" :giao="the.giao" />
-      <section><h3>Mô tả</h3><pre class="van-ban">{{ ct.mo_ta || '(trống)' }}</pre></section>
-      <section><h3>Tiêu chí nghiệm thu</h3><pre class="van-ban">{{ ct.nghiem_thu || '(trống)' }}</pre></section>
+      <h4>Mô tả</h4>
+      <p class="van-ban">{{ ct.mo_ta || '(trống)' }}</p>
+      <h4>Tiêu chí nghiệm thu</h4>
+      <p class="van-ban">{{ ct.nghiem_thu || '(trống)' }}</p>
       <DongThoiGian :ds="ct.dong_thoi_gian" />
     </template>
   </aside>
```

- [ ] **Step 4: Chạy thấy PASS**

```bash
cd frontend && node --test tests/cong_viec.test.mjs
npm run kiem && npm run build && npm run kiem-dist && cd ..
```

Kỳ vọng: PASS — lệnh test của task: pass 5 · fail 0; toàn bộ tăng đúng 5 node test so với main trước task (bảng "Sơ đồ đợt chạy"); `npm run build`, `npm run kiem-dist` xanh. Số đo trên bản chạy thử.

- [ ] **Step 5: Commit**

```bash
git add frontend/tests/cong_viec.test.mjs frontend/src/kieu/cong-viec.css frontend/src/luat_cong_viec.js frontend/src/thanh/DongThoiGian.vue frontend/src/thanh/HopViSao.vue frontend/src/thanh/OChot.vue frontend/src/thanh/OGiaoViec.vue frontend/src/thanh/OTraLoi.vue frontend/src/thanh/TheBead.vue frontend/src/trang/CongViec.vue frontend/src/trang/NganBen.vue
git commit -m "feat(dashboard): 2f trang Công việc + ngăn bên theo mockup"
```

### Task 10: Trang Đội ngũ AI

**Đợt:** 3 · **Độ khó:** vừa · **Phải xong trước:** Task 1, 2 · **Test mới:** 4 node

**Mockup bám:** `trang.js` (`veDoiNgu`, `theKhe`, `thanhHm`), `chung.js` (`chibi`, `tiLe`), `style.css` mục "Đội ngũ AI"; ảnh `anh-doi-ngu.png`. Plan 2d mục "Ranh giới 2d ↔ 2f" (`oTiLe` in nhạt phần ngoặc, nhóm nút 7/30/92). Hàng khe 0 phiếu do API 2d trả sẵn (G19, **D41**: 2d Task 6 `du_hang_khe`) — trang đọc thẳng `bang_diem`, không ghép phía trình duyệt.

**Files:**
- Create: `frontend/src/luat_the_khe.js` (`lopTrangThai`, `oViec`, `chuPhien`, `chuNhipTim` — tách khỏi `luat_doi_ngu.js` để file 2b/2d giữ nguyên), `frontend/src/kieu/doi-ngu.css`
- Modify (viết lại): `frontend/src/trang/DoiNgu.vue`, `frontend/src/thanh/TheKhe.vue`; (đổi lớp): `frontend/src/thanh/HopKhe.vue`
- Test: `frontend/tests/doi_ngu_2f.test.mjs` (mới)

**Interfaces:**
- Consumes: `/api/doi-ngu?du_an=&so_ngay=` (2d T6: `bang_diem` đã có hàng mọi khe đã khai — D41; `ten`, `vi_sao_tat` của Task 7), `/api/du-an`; `SO_NGAY_BANG_DIEM`, `duongDanDoiNgu`, `oTiLe`, `nhanTrangThai`, `nutKhe`, `CANH_BAO_HAN_MUC`, `lyDoCauDao` (`luat_doi_ngu.js`), `Chibi`, `ThanhHanMuc`, `cuaSo`, `tenKhe`, `conLai`, `gioPhut`, `truocDay`.
- Produces: `lopTrangThai`, `oViec`, `chuPhien`, `chuNhipTim` (chỉ trang này dùng).

Giữ (D36): cảnh báo `CANH_BAO_HAN_MUC`, danh sách luật vai, hộp bật/tắt khe, xác nhận đóng cầu dao, 409, polling 5 giây. "Phiên: 1/2" → "1 phiên đang chạy" (G11). Phụ đề thẻ "claude-1 · máy B · <tên gợi nhớ>" như mockup.

- [ ] **Step 1: Viết test (chép nguyên văn)**

`frontend/tests/doi_ngu_2f.test.mjs` (mới):

```js
// Luật thuần trang Đội ngũ AI theo mockup (lát 2f F3): chip trạng thái, ô việc, chữ phiên / nhịp tim. Hàng bảng điểm
// (kể cả khe 0 phiếu) do API 2d trả sẵn (D41) — không có luật ghép hàng ở đây.
import assert from 'node:assert/strict'
import { test } from 'node:test'
import { chuNhipTim, chuPhien, lopTrangThai, oViec } from '../src/luat_the_khe.js'

const KHONG_NGAT = { ngat: false, ly_do: null, toi_luc: null }
const khe = (them) => ({ khe_id: 'B/claude-1', may: 'B', trang_thai: 'ranh', phieu: null, cau_dao: KHONG_NGAT,
  ...them })

test('lớp chip trạng thái: cầu dao ngắt thắng trạng thái suy', () => {
  assert.equal(lopTrangThai(khe({ trang_thai: 'lam' })), 'tt-lam')
  assert.equal(lopTrangThai(khe({ trang_thai: 'mat_ket_noi' })), 'tt-mat_ket_noi')
  assert.equal(lopTrangThai(khe({ trang_thai: 'loi', cau_dao: { ngat: true } })), 'tt-cau_dao')
  assert.equal(lopTrangThai({ trang_thai: 'tat' }), 'tt-tat')
})

test('ô việc: đang giữ phiếu đứng trước mọi trạng thái', () => {
  const phieu = { du_an: 'hr', bead_id: 'hr-1', buoc: 'qc', tieu_de: 'Chọn cách tính thuế' }
  assert.deepEqual(oViec(khe({ trang_thai: 'can_nguoi', phieu })),
    { loai: 'phieu', ma: 'hr-1', chu: 'Chọn cách tính thuế · QC' })
  assert.equal(oViec(khe({ phieu: { ...phieu, buoc: 'code' } })).chu, 'Chọn cách tính thuế · code')
  assert.deepEqual(oViec(khe({})), { loai: 'trong', ma: '', chu: 'Không giữ việc' })
})

test('ô việc: cầu dao ngắt, tắt, mất kết nối', () => {
  const bayGio = new Date('2026-10-15T15:12:00Z')
  const ngat = { ngat: true, ly_do: 'het-han-muc', toi_luc: '2026-10-15T17:12:00Z' }
  assert.deepEqual(oViec(khe({ trang_thai: 'loi', cau_dao: ngat }), bayGio),
    { loai: 'cau_dao', ma: '', chu: 'Cầu dao ngắt: hết hạn mức · tự đóng 00:12 (còn 2 giờ)' })
  assert.equal(oViec(khe({ cau_dao: { ...ngat, toi_luc: '2026-10-15T15:00:00Z' } }), bayGio).chu,
    'Cầu dao ngắt: hết hạn mức · tự đóng 22:00')
  assert.equal(oViec(khe({ cau_dao: { ngat: true, ly_do: 'loi-lien-tiep', toi_luc: null } }), bayGio).chu,
    'Cầu dao ngắt: lỗi không do agent liên tiếp')
  assert.deepEqual(oViec(khe({ trang_thai: 'tat', vi_sao_tat: 'để dành' })),
    { loai: 'tat', ma: '', chu: 'Đại ca tắt khe · “để dành”' })
  assert.equal(oViec(khe({ trang_thai: 'tat', vi_sao_tat: '  ' })).chu, 'Đại ca tắt khe')
  assert.equal(oViec(khe({ trang_thai: 'tat' })).chu, 'Đại ca tắt khe')
  assert.deepEqual(oViec(khe({ trang_thai: 'mat_ket_noi', may: 'C' })),
    { loai: 'mat_ket_noi', ma: '', chu: 'Không thấy nhịp tim từ máy C' })
})

test('chữ phiên (D38/Q11: không có số phiên tối đa) và nhịp tim cuối', () => {
  assert.equal(chuPhien(1), '1 phiên đang chạy')
  assert.equal(chuPhien(2), '2 phiên đang chạy')
  assert.equal(chuPhien(0), 'Không có phiên')
  assert.equal(chuPhien(undefined), 'Không có phiên')
  const bayGio = new Date('2026-10-15T15:12:06Z')
  assert.equal(chuNhipTim('2026-10-15T15:12:00Z', bayGio), '6 giây trước')
  assert.equal(chuNhipTim(null, bayGio), 'chưa từng có')
  assert.equal(chuNhipTim('2026-10-15T15:12:09Z', bayGio), 'vừa xong')
})
```

- [ ] **Step 2: Chạy thấy FAIL**

```bash
cd frontend && node --test tests/doi_ngu_2f.test.mjs
```

Kỳ vọng: FAIL — `Error [ERR_MODULE_NOT_FOUND]: Cannot find module '…/frontend/src/luat_the_khe.js' imported from …/frontend/tests/doi_ngu_2f.test.mjs`

- [ ] **Step 3: Viết mã (chép nguyên văn; file sửa: chép khối diff ra file tạm, `git apply --check` rồi `git apply`)**

`frontend/src/kieu/doi-ngu.css` (mới):

```css
/* Trang Đội ngũ AI (mockup style.css "Đội ngũ AI" + style="" nội tuyến của trang.js veDoiNgu / theKhe, D20).
   .chibi .han-muc .thanh-hm ở khe.css; .bang .chip .tt-* .nhom-nut ở chung.css. */
.bang-diem { padding: 14px 16px 6px; }
.bang-diem .dau-khoi { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; margin-bottom: 6px; }
.bang-diem h2 { margin: 0; font-size: 17px; }
.bang-diem .loc { margin-left: auto; display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
.bang-diem .bang tbody th { font-weight: 500; white-space: nowrap; }
.bang-diem .chu-thich { margin: 8px 0; }
.luoi-khe { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(300px, 100%), 1fr)); gap: 14px; }
.the-khe { display: flex; flex-direction: column; gap: 11px; }
/* chung.css làm mờ mọi `.mo`; mockup chỉ đổi nền thẻ khe tắt / mất kết nối (chibi mờ riêng). */
.the.the-khe.mo { opacity: 1; background: #fbf9f6; }
.the-khe p { margin: 0; }
.the-khe .dau { display: flex; gap: 12px; align-items: center; }
.the-khe .dau > div { min-width: 0; }
.the-khe .dau strong { font-size: 16px; display: block; }
.the-khe .dau .nho { font-family: var(--mono); font-size: 11.5px; overflow-wrap: anywhere; }
.the-khe .dau .chip { margin-left: auto; align-self: flex-start; }
.the-khe .viec {
  font-size: 13.5px; background: var(--nen-3); border: 1px solid var(--vien); border-radius: 8px; padding: 7px 10px;
}
.the-khe .viec .mono { color: var(--nhan); font-size: 12px; margin-right: 6px; }
.the-khe .viec.cau_dao { background: var(--nen-canh-bao); border-color: var(--vien-canh-bao); }
.the-khe .vai-phien { display: flex; gap: 14px; flex-wrap: wrap; }
.the-khe .chan {
  display: flex; flex-wrap: wrap; gap: 8px; align-items: center; border-top: 1px solid var(--vien); padding-top: 10px;
}
.the-khe .chan .nho { margin-right: auto; font-size: 12px; }
.luat-vai { font-size: 13.5px; }
.luat-vai .chip { margin-right: 4px; }
.luat-vai ul { margin: 8px 0 0; padding-left: 1.2rem; }
```

`frontend/src/luat_the_khe.js` (mới):

```js
// Luật hiển thị thuần của thẻ khe trang Đội ngũ AI theo mockup (lát 2f; trang.js veDoiNgu / theKhe, D20). Tách khỏi
// luat_doi_ngu.js (2b/2d) để file đó giữ nguyên. Hàng bảng điểm (cả khe 0 phiếu) do API 2d trả sẵn (D41).
import { conLai, gioPhut, truocDay } from './dinh_dang.js'
import { lyDoCauDao } from './luat_doi_ngu.js'

// Lớp chip trạng thái (chung.css `.tt-*`), cùng thứ tự ưu tiên với nhanTrangThai.
export function lopTrangThai(khe) {
  return khe.cau_dao && khe.cau_dao.ngat ? 'tt-cau_dao' : `tt-${khe.trang_thai}`
}

const TEN_BUOC = { spec: 'spec', code: 'code', qc: 'QC' }

// Ô `.viec` của thẻ khe: {loai: phieu|cau_dao|tat|mat_ket_noi|trong, ma (bead_id, chỉ khi giữ phiếu), chu}.
export function oViec(khe, bayGio = new Date()) {
  const p = khe.phieu
  if (p) return { loai: 'phieu', ma: p.bead_id, chu: `${p.tieu_de} · ${TEN_BUOC[p.buoc] ?? p.buoc}` }
  const cd = khe.cau_dao || {}
  if (cd.ngat) {
    const con = conLai(cd.toi_luc, bayGio)
    const toi = cd.toi_luc ? ` · tự đóng ${gioPhut(cd.toi_luc)}${con ? ` (${con})` : ''}` : ''
    return { loai: 'cau_dao', ma: '', chu: `Cầu dao ngắt: ${lyDoCauDao(cd.ly_do)}${toi}` }
  }
  if (khe.trang_thai === 'tat') {
    const vs = (khe.vi_sao_tat || '').trim()
    return { loai: 'tat', ma: '', chu: `Đại ca tắt khe${vs ? ` · “${vs}”` : ''}` }
  }
  if (khe.trang_thai === 'mat_ket_noi') {
    return { loai: 'mat_ket_noi', ma: '', chu: `Không thấy nhịp tim từ máy ${khe.may}` }
  }
  return { loai: 'trong', ma: '', chu: 'Không giữ việc' }
}

// Spec 3 không có số phiên tối đa (D38/Q11) → chỉ đếm phiên đang chạy, bỏ mẫu số "1/2" của mockup.
export function chuPhien(soPhien) {
  return soPhien > 0 ? `${soPhien} phiên đang chạy` : 'Không có phiên'
}

// "♥ nhịp tim cuối: …"; giờ máy lệch làm nhịp nằm ở tương lai → "vừa xong".
export function chuNhipTim(nhip, bayGio = new Date()) {
  return nhip ? truocDay(nhip, bayGio) || 'vừa xong' : 'chưa từng có'
}
```

`frontend/src/thanh/HopKhe.vue` (sửa):

```diff
diff --git a/frontend/src/thanh/HopKhe.vue b/frontend/src/thanh/HopKhe.vue
index bb811f0..cb6adb0 100644
--- a/frontend/src/thanh/HopKhe.vue
+++ b/frontend/src/thanh/HopKhe.vue
@@ -1,6 +1,8 @@
 <script setup>
 import { ref } from 'vue'
+import { tenKhe } from '../luat_han_muc.js'
 
+// Hộp xác nhận Bật / Tắt khe (lớp chung.css `.nen-mo .hop .truong .hang-nut .nut`, lát 2f F3). Logic giữ như 2b.
 defineProps({ khe: { type: Object, required: true }, bat: { type: Boolean, default: false } })
 const emit = defineEmits(['huy', 'xac-nhan'])
 const viSao = ref('')
@@ -9,14 +11,15 @@ const viSao = ref('')
 <template>
   <div class="nen-mo" role="dialog" aria-modal="true" aria-labelledby="hop-khe-td" @keydown.esc="emit('huy')">
     <form class="hop" @submit.prevent="emit('xac-nhan', viSao.trim())">
-      <h2 id="hop-khe-td">{{ bat ? 'Bật' : 'Tắt' }} khe {{ khe.ten_goi_nho }} ({{ khe.khe_id }})</h2>
+      <h2 id="hop-khe-td">{{ bat ? 'Bật' : 'Tắt' }} khe {{ tenKhe(khe) }} ({{ khe.khe_id }})</h2>
       <p v-if="!bat && khe.phieu" class="canh-bao">Khe đang làm {{ khe.phieu.du_an }}/{{ khe.phieu.bead_id }} — phiếu
         sẽ dừng mềm (lưu phần đã làm, bộ giao việc giao lại cho khe khác).</p>
       <p v-if="!bat" class="nho">Không giao việc mới cho khe này tới khi Đại ca bật lại.</p>
-      <label>Vì sao? (tuỳ chọn)<textarea v-model="viSao" rows="2" maxlength="500" autofocus></textarea></label>
-      <div class="nut">
-        <button type="button" @click="emit('huy')">Huỷ</button>
-        <button type="submit">{{ bat ? 'Bật khe' : 'Tắt khe' }}</button>
+      <label class="truong">Vì sao? (tuỳ chọn)
+        <textarea v-model="viSao" rows="2" maxlength="500" autofocus></textarea></label>
+      <div class="hang-nut">
+        <button class="nut" type="button" @click="emit('huy')">Huỷ</button>
+        <button class="nut" :class="bat ? 'chinh' : 'nguy'" type="submit">{{ bat ? 'Bật khe' : 'Tắt khe' }}</button>
       </div>
     </form>
   </div>
```

`frontend/src/thanh/TheKhe.vue` (sửa):

```diff
diff --git a/frontend/src/thanh/TheKhe.vue b/frontend/src/thanh/TheKhe.vue
index c53e8b4..5cbd64e 100644
--- a/frontend/src/thanh/TheKhe.vue
+++ b/frontend/src/thanh/TheKhe.vue
@@ -1,16 +1,26 @@
 <script setup>
-import { ref } from 'vue'
+import { computed, ref } from 'vue'
+import '../kieu/doi-ngu.css'
 import { ghi, thanGhi } from '../api.js'
-import { gioVN } from '../luat.js'
-import { CANH_BAO_HAN_MUC, lyDoCauDao, moTaCuaSo, nhanTrangThai, nutKhe } from '../luat_doi_ngu.js'
+import { cuaSo, tenKhe } from '../luat_han_muc.js'
+import { CANH_BAO_HAN_MUC, nhanTrangThai, nutKhe } from '../luat_doi_ngu.js'
+import { chuNhipTim, chuPhien, lopTrangThai, oViec } from '../luat_the_khe.js'
+import Chibi from './Chibi.vue'
 import HopKhe from './HopKhe.vue'
+import ThanhHanMuc from './ThanhHanMuc.vue'
 
+// Thẻ khe theo mockup trang.js theKhe (D20). Thêm cảnh báo hạn mức mockup chưa vẽ (D36); phiên không có mẫu số (Q11).
 const props = defineProps({ khe: { type: Object, required: true }, laDaiCa: { type: Boolean, default: false } })
 const emit = defineEmits(['doi'])
 const hop = ref('')
 const dangGui = ref(false)
 const loi = ref('')
 const duong = () => `/api/khe/${props.khe.khe_id.split('/').map(encodeURIComponent).join('/')}`
+const mo = computed(() => props.khe.trang_thai === 'tat' || props.khe.trang_thai === 'mat_ket_noi')
+// Thẻ vẽ lại mỗi lần trang tải lại (5 giây) → "còn x giờ", "x giây trước" tự cập nhật theo khe mới.
+const viec = computed(() => oViec(props.khe))
+const nut = computed(() => nutKhe(props.khe))
+const canhBao = computed(() => CANH_BAO_HAN_MUC[props.khe.muc_han_muc])
 
 async function lam(hanhDong, noiDung = {}) {
   dangGui.value = true
@@ -34,37 +44,36 @@ function dongCauDao() {
 </script>
 
 <template>
-  <article class="the-khe" :class="{ mo: khe.trang_thai === 'tat' || khe.trang_thai === 'mat_ket_noi' }">
-    <header>
-      <strong>{{ khe.ten_goi_nho }}</strong> <span class="ma">{{ khe.khe_id }}</span>
-      <span class="chip" :class="{ bat: khe.cau_dao.ngat || khe.trang_thai === 'loi' }">{{ nhanTrangThai(khe) }}</span>
-    </header>
-    <p class="nho">Máy {{ khe.may }} · CLI {{ khe.cli }} · vai ưu tiên {{ khe.vai_uu_tien.join(', ') }} ·
-      {{ khe.so_phien }} phiên đồng thời</p>
-    <p v-if="khe.phieu" class="tieu-de">Đang làm <span class="ma">{{ khe.phieu.du_an }}/{{ khe.phieu.bead_id }}</span>
-      ({{ khe.phieu.buoc }}) — {{ khe.phieu.tieu_de }}</p>
-    <ul class="han-muc">
-      <li v-for="cs in khe.han_muc.cua_so" :key="cs.loai">{{ moTaCuaSo(cs) }}</li>
-    </ul>
-    <p v-if="CANH_BAO_HAN_MUC[khe.muc_han_muc]" :class="CANH_BAO_HAN_MUC[khe.muc_han_muc][0]">
-      {{ CANH_BAO_HAN_MUC[khe.muc_han_muc][1] }}</p>
-    <p v-if="khe.cau_dao.ngat" class="loi">Cầu dao ngắt tới {{ gioVN(khe.cau_dao.toi_luc) }} —
-      {{ lyDoCauDao(khe.cau_dao.ly_do) }}</p>
-    <p class="nho">Nhịp tim cuối: {{ khe.nhip_cuoi ? gioVN(khe.nhip_cuoi) : 'chưa có' }}</p>
-    <div class="nut">
-      <button v-if="nutKhe(khe).tat" type="button" :disabled="dangGui || !laDaiCa" @click="hop = 'tat'">Tắt khe</button>
-      <button v-if="nutKhe(khe).bat" type="button" :disabled="dangGui || !laDaiCa" @click="hop = 'bat'">Bật khe</button>
-      <button v-if="nutKhe(khe).dongCauDao" type="button" :disabled="dangGui || !laDaiCa" @click="dongCauDao">
-        Đóng cầu dao</button>
+  <article class="the the-khe" :class="{ mo }">
+    <div class="dau">
+      <Chibi :khe-id="khe.khe_id" :mo="mo" />
+      <div>
+        <strong>{{ tenKhe(khe) }}</strong>
+        <span class="nho">{{ khe.khe_id.split('/').pop() }} · máy {{ khe.may }} · {{ khe.ten_goi_nho }}</span>
+      </div>
+      <span class="chip" :class="lopTrangThai(khe)"><span class="cham" />{{ nhanTrangThai(khe) }}</span>
+    </div>
+    <div v-if="viec.loai === 'phieu'" class="viec"><span class="mono">{{ viec.ma }}</span>{{ viec.chu }}</div>
+    <div v-else class="viec" :class="{ nho: viec.loai === 'trong', cau_dao: viec.loai === 'cau_dao' }">
+      {{ viec.chu }}</div>
+    <div class="han-muc">
+      <ThanhHanMuc ten="5 giờ" :cua-so="cuaSo(khe, '5h')" />
+      <ThanhHanMuc ten="Tuần" :cua-so="cuaSo(khe, 'tuan')" />
+    </div>
+    <p v-if="canhBao" :class="canhBao[0]">{{ canhBao[1] }}</p>
+    <div class="nho vai-phien">
+      <span>Vai: {{ khe.vai_uu_tien.join(', ') || '—' }}</span><span>{{ chuPhien(khe.so_phien) }}</span>
+    </div>
+    <div class="chan">
+      <span class="nho">♥ nhịp tim cuối: {{ chuNhipTim(khe.nhip_cuoi) }}</span>
+      <button v-if="nut.dongCauDao" class="nut chinh" type="button" :disabled="dangGui || !laDaiCa"
+              @click="dongCauDao">Đóng cầu dao</button>
+      <button v-if="nut.bat" class="nut chinh" type="button" :disabled="dangGui || !laDaiCa"
+              @click="hop = 'bat'">Bật khe</button>
+      <button v-if="nut.tat" class="nut nguy" type="button" :disabled="dangGui || !laDaiCa"
+              @click="hop = 'tat'">Tắt khe</button>
     </div>
-    <HopKhe v-if="hop" :khe="khe" :bat="hop === 'bat'" @huy="hop = ''" @xac-nhan="(vs) => lam(hop, { vi_sao: vs })" />
     <p v-if="loi" class="loi" role="alert">{{ loi }}</p>
+    <HopKhe v-if="hop" :khe="khe" :bat="hop === 'bat'" @huy="hop = ''" @xac-nhan="(vs) => lam(hop, { vi_sao: vs })" />
   </article>
 </template>
-
-<style scoped>
-.the-khe { background: var(--mat); border: 1px solid var(--vien); border-radius: 8px; padding: .75rem; }
-.the-khe.mo { opacity: .6; }
-.the-khe header { display: flex; flex-wrap: wrap; gap: .25rem .5rem; align-items: baseline; }
-.han-muc { margin: .25rem 0; padding-left: 1.1rem; font-size: .85rem; }
-</style>
```

`frontend/src/trang/DoiNgu.vue` (sửa):

```diff
diff --git a/frontend/src/trang/DoiNgu.vue b/frontend/src/trang/DoiNgu.vue
index 0fc0134..26e7dad 100644
--- a/frontend/src/trang/DoiNgu.vue
+++ b/frontend/src/trang/DoiNgu.vue
@@ -1,17 +1,22 @@
 <script setup>
-import { onMounted, onUnmounted, ref, watch } from 'vue'
+import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
+import '../kieu/doi-ngu.css'
 import { doc } from '../api.js'
 import { kho } from '../kho.js'
-import { SO_NGAY_BANG_DIEM, dinhDangSo, duongDanDoiNgu, tiLe } from '../luat_doi_ngu.js'
+import { SO_NGAY_BANG_DIEM, dinhDangSo, duongDanDoiNgu, oTiLe } from '../luat_doi_ngu.js'
+import DauTrang from '../thanh/DauTrang.vue'
 import TheKhe from '../thanh/TheKhe.vue'
 
-// Nhịp tim không phải sự kiện (spec 3 §10) → "mất kết nối" chỉ thấy khi tải lại; tải lại mỗi 5 giây (G15).
+// Trang Đội ngũ AI theo mockup trang.js veDoiNgu (D20). Nhịp tim không phải sự kiện (spec 3 §10) → "mất kết nối"
+// chỉ thấy khi tải lại; tải lại mỗi 5 giây (G15) và khi SSE báo đội ngũ đổi.
 const CHU_KY_MS = 5000
+const MO_TA = 'Mỗi khe một thẻ: trạng thái, việc đang giữ, hạn mức còn lại. Tắt khe để dành hạn mức cho việc tay.'
 const dl = ref(null)
 const loi = ref('')
 const duAn = ref('')                      // D14: bảng điểm lọc theo dự án + số ngày; mặc định mọi dự án, 30 ngày
 const soNgay = ref(30)
 const dsDuAn = ref([])
+const laDaiCa = computed(() => Boolean(kho.trangThai && kho.trangThai.la_dai_ca))
 let hen = null
 
 async function tai() {
@@ -32,55 +37,54 @@ watch([() => kho.phienBanDoiNgu, duAn, soNgay], tai)
 </script>
 
 <template>
-  <section>
-    <h1>Đội ngũ AI</h1>
-    <p v-if="loi" class="loi" role="alert">{{ loi }}</p>
-    <p v-if="dl && !dl.bat" class="nho">Kho phiếu (phần 3) chưa bật trên trạm.</p>
-    <p v-else-if="dl && !dl.khe.length" class="nho">Chưa có khe nào đăng ký với trạm.</p>
-    <div v-if="dl && dl.khe.length" class="luoi-khe">
-      <TheKhe v-for="k in dl.khe" :key="k.khe_id" :khe="k"
-              :la-dai-ca="Boolean(kho.trangThai && kho.trangThai.la_dai_ca)" @doi="tai" />
-    </div>
-    <template v-if="dl && dl.luat_vai">
-      <h2>Luật vai ↔ khe</h2>
-      <p class="nho">Bước → vai:
-        <span v-for="(vai, buoc) in dl.luat_vai.vai_cua_buoc" :key="buoc" class="nhan-nho">{{ buoc }} → {{ vai }}</span></p>
-      <ul class="nho"><li v-for="l in dl.luat_vai.luat" :key="l">{{ l }}</li></ul>
-    </template>
-    <template v-if="dl && dl.bat">
-      <h2>Bảng điểm thợ</h2>
-      <div class="cong-cu">
-        <label>Dự án
-          <select v-model="duAn"><option value="">Tất cả</option>
+  <DauTrang tieu-de="Đội ngũ AI" :mo-ta="MO_TA" />
+  <p v-if="loi" class="loi" role="alert">{{ loi }}</p>
+  <p v-if="dl && !dl.bat" class="cot-rong">Kho phiếu chưa bật trên trạm (phần 3) — chưa có khe, chưa có bảng điểm.</p>
+  <template v-if="dl && dl.bat">
+    <section class="the bang-diem">
+      <div class="dau-khoi">
+        <h2>Bảng điểm thợ</h2>
+        <span class="nho">lọc áp cho mọi cột</span>
+        <div class="loc">
+          <select v-model="duAn" aria-label="Dự án"><option value="">Tất cả dự án</option>
             <option v-for="d in dsDuAn" :key="d" :value="d">{{ d }}</option></select>
-        </label>
-        <label>Khoảng
-          <select v-model.number="soNgay">
-            <option v-for="n in SO_NGAY_BANG_DIEM" :key="n" :value="n">{{ n }} ngày gần nhất</option></select>
-        </label>
+          <div class="nhom-nut" role="group" aria-label="Khoảng">
+            <button v-for="n in SO_NGAY_BANG_DIEM" :key="n" type="button" :class="{ chon: n === soNgay }"
+                    :aria-pressed="n === soNgay" @click="soNgay = n">{{ n }} ngày</button>
+          </div>
+        </div>
       </div>
       <p v-if="!dl.bang_diem.length" class="nho">Không có phiếu nào được cấp trong khoảng này.</p>
       <div v-else class="bang-cuon">
-        <table>
+        <table class="bang">
           <thead><tr>
             <th scope="col">Khe</th><th scope="col">Vai</th><th scope="col">Số phiếu</th><th scope="col">Xong</th>
             <th scope="col">Lần chạy TB / phiếu</th><th scope="col">Qua lần đầu</th><th scope="col">Bị trả về</th>
           </tr></thead>
           <tbody><tr v-for="d in dl.bang_diem" :key="d.khe_id + '/' + d.vai">
-            <th scope="row">{{ d.khe_id }}</th><td>{{ d.vai }}</td><td>{{ d.so_phieu }}</td><td>{{ d.so_xong }}</td>
-            <td>{{ d.lan_chay_tb == null ? '—' : dinhDangSo(d.lan_chay_tb) }}</td>
-            <td>{{ tiLe(d.qua_lan_dau, d.qua_lan_dau_mau) }}</td><td>{{ tiLe(d.bi_tra_ve, d.bi_tra_ve_mau) }}</td>
+            <th scope="row" class="mono">{{ d.khe_id }}</th><td>{{ d.vai }}</td>
+            <td class="so">{{ d.so_phieu }}</td><td class="so">{{ d.so_xong }}</td>
+            <td class="so">{{ d.lan_chay_tb == null ? '—' : dinhDangSo(d.lan_chay_tb) }}</td>
+            <td v-for="(o, i) in [oTiLe(d.qua_lan_dau, d.qua_lan_dau_mau), oTiLe(d.bi_tra_ve, d.bi_tra_ve_mau)]"
+                :key="i">{{ o.chinh }} <span v-if="o.phu" class="nho">{{ o.phu }}</span></td>
           </tr></tbody>
         </table>
       </div>
-      <p class="nho">Tính theo phiếu được cấp trong khoảng đã chọn. Hai cột cuối chỉ cho vai coder (spec 4 §12,
-        D25–D29). "Qua lần đầu": lần kiểm lại đầu cho SHA của phiếu đạt và lần QC đầu sau đó đạt, chia cho số phiếu
-        code xong (phiếu còn chờ QC vẫn ở mẫu). "Bị trả về": mỗi lần bead vào cột 3 bằng phiếu của khe là một mẫu;
-        bị Đại ca trả về trước lần vào cột 3 kế tiếp thì tính. Ngoặc: (số đếm / cỡ mẫu).</p>
-    </template>
-  </section>
+      <p class="nho chu-thich">Qua lần đầu: phiếu code xong mà lần kiểm lại / QC đầu tiên qua. Bị trả về: bead vào
+        cột 3 rồi bị Đại ca Trả về. Chỉ tính vai coder; vai khác “—”.</p>
+    </section>
+    <h2 class="muc">Khe <span class="so">{{ dl.khe.length }}</span></h2>
+    <p v-if="!dl.khe.length" class="cot-rong">Chưa có khe nào đăng ký với trạm.</p>
+    <div v-else class="luoi-khe">
+      <TheKhe v-for="k in dl.khe" :key="k.khe_id" :khe="k" :la-dai-ca="laDaiCa" @doi="tai" />
+    </div>
+  </template>
+  <template v-if="dl && dl.luat_vai">
+    <h2 class="muc">Luật vai ↔ khe</h2>
+    <div class="the nho luat-vai">Bước → vai:
+      <span v-for="(vai, buoc) in dl.luat_vai.vai_cua_buoc" :key="buoc" class="chip mono">{{ buoc }} → {{ vai }}</span>
+      <ul v-if="dl.luat_vai.luat && dl.luat_vai.luat.length">
+        <li v-for="l in dl.luat_vai.luat" :key="l">{{ l }}</li></ul>
+    </div>
+  </template>
 </template>
-
-<style scoped>
-.luoi-khe { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(22rem, 100%), 1fr)); gap: 1rem; }
-</style>
```

- [ ] **Step 4: Chạy thấy PASS**

```bash
cd frontend && node --test tests/doi_ngu_2f.test.mjs
npm run kiem && npm run build && npm run kiem-dist && cd ..
```

Kỳ vọng: PASS — lệnh test của task: pass 4 · fail 0; toàn bộ tăng đúng 4 node test so với main trước task (bảng "Sơ đồ đợt chạy"); `npm run build`, `npm run kiem-dist` xanh. Số đo trên bản chạy thử.

- [ ] **Step 5: Commit**

```bash
git add frontend/tests/doi_ngu_2f.test.mjs frontend/src/kieu/doi-ngu.css frontend/src/luat_the_khe.js frontend/src/thanh/HopKhe.vue frontend/src/thanh/TheKhe.vue frontend/src/trang/DoiNgu.vue
git commit -m "feat(dashboard): 2f trang Đội ngũ AI theo mockup"
```

### Task 11: Trang Phê duyệt

**Đợt:** 3 · **Độ khó:** vừa · **Phải xong trước:** Task 1, 2 · **Test mới:** 4 node

**Mockup bám:** `trang.js` (`vePheDuyet`, `theReview`), `style.css` mục "Phê duyệt"; ảnh `anh-phe-duyet.png`. Khảo sát §1.5. G7 (PR trạm), G27 (Trả lời dẫn sang ngăn bên).

**Files:**
- Create: `frontend/src/thanh/phe_duyet/TheHe.vue`, `TheBi.vue`, `TheReview.vue`, `TheSpec.vue`, `TheFeatureXong.vue`, `frontend/src/thanh/phe_duyet/thao_tac.js` (`dungThaoTac` — logic `lam/duyet/traVe/traLoi/thuLai`, 409/501 giữ nguyên của `MucPheDuyet.vue`), `frontend/src/luat_phe_duyet.js`, `frontend/src/kieu/phe-duyet.css`
- Modify: `frontend/src/trang/PheDuyet.vue` (viết lại), `frontend/src/thanh/ChiTietSpec.vue` (đổi lớp, giữ logic)
- Delete: `frontend/src/thanh/MucPheDuyet.vue`
- Test: `frontend/tests/phe_duyet.test.mjs` (mới)

**Interfaces:**
- Consumes: `/api/phe-duyet` (`chi_tiet.pr_tram` của 2d T7; `cau_hoi`, `khe_id`, `buoc`, `bead_goc` của Task 7), `/api/du-an` (`bat_ghi`); `nhomPheDuyet`, `TEN_PHE_DUYET`, `khoaMuc`, `NHAN_PR_TRAM`, `lopPrTram`, `canhBaoPrTram`, `thanDuyet`, `coTheDuyetSpec`, `laLinkAnToan`, `tenKhe`, `taiSoPheDuyet`.
- Produces: `chipHe`, `tieuDeHe`, `chiTietHe`, `chipNguoiHoi`, `duongDanTraLoi`, `linkPrReview`, `moTaReview`, `nutDongReview`, `khoaThaoTac` (`luat_phe_duyet.js`).

Giữ (D36): nhóm "Decision mở", "Cờ đỏ", "Spec chờ duyệt" (ChiTietSpec), "Feature xong", dòng "Xác nhận đã merge là thao tác tay…", nút "Thử lại" mục hệ có bead, khoá nút khi không phải Đại ca hoặc dự án chỉ quét thử, lỗi đọc từng dự án. Hai nút "Đã merge trên GitHub → đóng bead" và "Duyệt" cùng gọi `…/duyet` như mockup.

- [ ] **Step 1: Viết test (chép nguyên văn)**

`frontend/tests/phe_duyet.test.mjs` (mới):

```js
import assert from 'node:assert/strict'
import { test } from 'node:test'
import { CHU_CHI_QUET_THU } from '../src/luat.js'
import { chiTietHe, chipHe, chipNguoiHoi, duongDanTraLoi, khoaThaoTac, linkPrReview, moTaReview, nutDongReview,
  tieuDeHe } from '../src/luat_phe_duyet.js'

const LUC = '2026-10-15T17:12:00Z'   // 00:12 giờ VN
const CAU_DAO = {
  loai: 'he', du_an: '_tram', bead_id: null, tieu_de: 'Khe a/claude-4',
  chi_tiet: {
    su_kien: 'khe.cau_dao_ngat', luc: LUC, khe_id: 'a/claude-4', loi: 'Cầu dao ngắt — hết hạn mức',
  },
}
const QUET = {
  loai: 'he', du_an: 'hr', bead_id: null, tieu_de: '', chi_tiet: { su_kien: 'quet.loi', luc: LUC, loi: 'x' },
}
const PR = 'https://github.com/a/b/pull/12'

test('mục hệ: cầu dao có chip "cầu dao" + tiêu đề theo khe; sự kiện khác có chip tên dễ đọc', () => {
  assert.deepEqual(chipHe(CAU_DAO), { lop: 'tt-cau_dao', chu: 'cầu dao' })
  assert.equal(tieuDeHe(CAU_DAO), 'Cầu dao khe a/claude-4 ngắt')
  assert.deepEqual(chipHe(QUET), { lop: 'tt-can_nguoi', chu: 'lỗi quét' })
  assert.equal(tieuDeHe(QUET), 'Quét dự án lỗi')
  assert.equal(tieuDeHe({ ...QUET, tieu_de: 'Bead A', chi_tiet: { su_kien: 'cham_cot.bo_qua' } }), 'Bead A')
  const la = { ...QUET, chi_tiet: { su_kien: 'x.y' } }
  assert.deepEqual(chipHe(la), { lop: 'tt-can_nguoi', chu: 'x.y' })
  assert.equal(tieuDeHe(la), 'x.y')
  assert.equal(chiTietHe(CAU_DAO), '16/10 00:12 · Cầu dao ngắt — hết hạn mức')
  assert.equal(chiTietHe({ chi_tiet: {} }), '')
  assert.equal(chiTietHe({ chi_tiet: { ...CAU_DAO.chi_tiet, toi_luc: '2026-10-15T17:12:00Z' } }),
    'Lý do: hết hạn mức · tự đóng lúc 00:12')
})

test('mục bí: chip "<tên khe> hỏi · <bước>"; thiếu khe thì bỏ chip; link trả lời sang ngăn bên', () => {
  const m = { loai: 'escalation', du_an: 'hr-codex', bead_id: 'hr-3', chi_tiet: { khe_id: 'b/codex-1', buoc: 'qc' } }
  assert.equal(chipNguoiHoi(m), 'Codex 1 hỏi · QC')
  assert.equal(chipNguoiHoi({ ...m, chi_tiet: { khe_id: 'b/codex-1' } }), 'Codex 1 hỏi')
  assert.equal(chipNguoiHoi({ ...m, chi_tiet: {} }), '')
  assert.equal(chipNguoiHoi({ ...m, loai: 'decision' }), '')
  assert.deepEqual(duongDanTraLoi(m), { path: '/cong-viec', query: { du_an: 'hr-codex', bead: 'hr-3' } })
})

test('mục review: câu mô tả + nút đóng theo pr_tram; link PR an toàn', () => {
  const mo = { loai: 'cho-review', chi_tiet: { pr: null, pr_tram: { so: 12, url: PR, trang_thai: 'mo' } } }
  const merge = { loai: 'cho-review', chi_tiet: { pr_tram: { so: 11, url: PR, trang_thai: 'da_merge' } } }
  const cu = { loai: 'cho-review', chi_tiet: { pr: PR, pr_tram: null } }
  const khong = { loai: 'cho-review', chi_tiet: { pr: 'javascript:x', pr_tram: null } }
  assert.equal(moTaReview(mo), 'Đã code + QC qua; chờ Đại ca review để đóng.')
  assert.equal(moTaReview(merge), 'PR đã merge đúng commit đã kiểm.')
  assert.equal(nutDongReview(merge), 'tu-dong')
  assert.equal(nutDongReview(mo), 'da-merge')
  assert.equal(nutDongReview(cu), 'da-merge')
  assert.equal(nutDongReview(khong), '')
  assert.equal(nutDongReview({ ...mo, loai: 'co-do' }), '')
  assert.equal(moTaReview({ ...mo, loai: 'co-do' }), '')
  assert.equal(linkPrReview(mo), PR)
  assert.equal(linkPrReview(cu), PR)
  assert.equal(linkPrReview({ chi_tiet: { pr_tram: { url: 'https://evil.com/x' } } }), '')
})

test('khoá nút: không phải Đại ca khoá không chữ; dự án chỉ quét thử khoá + chữ D37', () => {
  assert.deepEqual(khoaThaoTac(true, false), { khoa: false, chu: '' })
  assert.deepEqual(khoaThaoTac(false, false), { khoa: true, chu: '' })
  assert.deepEqual(khoaThaoTac(true, true), { khoa: true, chu: CHU_CHI_QUET_THU })
  assert.deepEqual(khoaThaoTac(false, true), { khoa: true, chu: CHU_CHI_QUET_THU })
})
```

- [ ] **Step 2: Chạy thấy FAIL**

```bash
cd frontend && node --test tests/phe_duyet.test.mjs
```

Kỳ vọng: FAIL — `Error [ERR_MODULE_NOT_FOUND]: Cannot find module '…/frontend/src/luat_phe_duyet.js' imported from …/frontend/tests/phe_duyet.test.mjs`

- [ ] **Step 3: Viết mã (chép nguyên văn; file sửa: chép khối diff ra file tạm, `git apply --check` rồi `git apply`)**

`frontend/src/kieu/phe-duyet.css` (mới):

```css
/* Trang Phê duyệt — mockup style.css "Phê duyệt" (650 → 600 theo luật độ đậm), cộng phần bản thật có (D36). */
.ds-duyet { display: flex; flex-direction: column; gap: 10px; }
.the-duyet { display: grid; grid-template-columns: 1fr auto; gap: 8px 16px; align-items: start; }
.the-duyet .tren { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; font-size: 12.5px; }
.the-duyet .ma { font-family: var(--mono); color: var(--nhan); }
.the-duyet .tieu-de { font-weight: 600; font-size: 15.5px; margin: 4px 0 2px; }
.the-duyet .hanh-dong { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; justify-content: flex-end;
  max-width: 380px; }
.the-duyet .gop-y { grid-column: 1 / -1; display: flex; gap: 8px; align-items: flex-start; }
.the-duyet.he { border-left: 5px solid var(--vang); }
.the-duyet .nho { overflow-wrap: anywhere; }
.the-duyet ul.canh-bao { padding-left: 26px; }
/* Dòng phụ trải hết hai cột: câu khoá, lỗi thao tác, câu "đã merge là thao tác tay", chi tiết spec. */
.the-duyet > .dong-day, .the-duyet > .chi-tiet-spec { grid-column: 1 / -1; margin: 0; }
.chi-tiet-spec { display: flex; flex-direction: column; gap: 6px; }
.chi-tiet-spec p { margin: 0; }
.chi-tiet-spec .ds-file { margin: 0; padding-left: 18px; font-size: 12.5px; color: var(--chu-2); }
.chi-tiet-spec .lenh {
  font-family: var(--mono); font-size: 12.5px; background: var(--nen-lenh); color: var(--chu-lenh);
  border-radius: 8px; padding: 8px 10px; margin: 0; white-space: pre-wrap; overflow-wrap: anywhere;
}
@media (max-width: 720px) {
  .the-duyet { grid-template-columns: 1fr; }
  .the-duyet .hanh-dong { justify-content: flex-start; }
}
```

`frontend/src/luat_phe_duyet.js` (mới):

```js
// Luật hiển thị trang Phê duyệt (mockup trang.js vePheDuyet + theReview, anh-phe-duyet.png; D36–D38) — thuần,
// test bằng node --test. Server dựng mọi chuỗi trong `chi_tiet`; ở đây chỉ chọn nhãn và ghép câu.
import { gioPhut, ngayGio } from './dinh_dang.js'
import { CHU_CHI_QUET_THU, laLinkAnToan } from './luat.js'
import { tenKhe } from './luat_han_muc.js'

// Sự kiện của mục "Hệ cần xem" (tram/suy/phe_duyet.py, phe_duyet_khe.py): [chữ chip, tiêu đề khi mục không gắn bead].
const SU_KIEN_HE = {
  'cham_cot.bo_qua': ['chấm cột bỏ qua', 'Chấm cột bỏ qua bead'],
  'quet.loi': ['lỗi quét', 'Quét dự án lỗi'],
  'nho.loi_llm': ['ký ức · LLM', 'Nạp ký ức đứng (LLM lỗi)'],
  'nho.loi_embedder': ['ký ức · embedder', 'Nạp ký ức đứng (embedder lỗi)'],
}
const TEN_BUOC = { spec: 'spec', code: 'code', qc: 'QC' }
const CAU_DAO = 'khe.cau_dao_ngat'
const ct = (m) => (m && m.chi_tiet) || {}

// Chip loại của mục hệ: cầu dao → `tt-cau_dao` "cầu dao" (mockup); sự kiện khác → `tt-can_nguoi` + tên dễ đọc.
export function chipHe(m) {
  const sk = ct(m).su_kien || ''
  if (sk === CAU_DAO) return { lop: 'tt-cau_dao', chu: 'cầu dao' }
  return { lop: 'tt-can_nguoi', chu: SU_KIEN_HE[sk] ? SU_KIEN_HE[sk][0] : sk }
}

export function tieuDeHe(m) {
  const c = ct(m)
  if (c.su_kien === CAU_DAO) return `Cầu dao khe ${c.khe_id} ngắt`
  if (m.tieu_de) return m.tieu_de
  return SU_KIEN_HE[c.su_kien] ? SU_KIEN_HE[c.su_kien][1] : c.su_kien || ''
}

// Dòng `.nho` dưới tiêu đề: giờ sự kiện · lỗi server gửi.
// Cầu dao (mockup "Lý do: hết hạn mức · tự đóng lúc 00:12"): lý do là phần sau " — " của câu hằng server
// (tram/suy/phe_duyet_khe.py `LY_DO`), giờ tự đóng lấy từ `toi_luc`. Mục hệ khác: giờ + câu lỗi.
export function chiTietHe(m) {
  const c = ct(m)
  if (c.su_kien === 'khe.cau_dao_ngat' && c.toi_luc) {
    const lyDo = String(c.loi || '').split(' — ').slice(1).join(' — ')
    return `Lý do: ${lyDo || '?'} · tự đóng lúc ${gioPhut(c.toi_luc)}`
  }
  return [ngayGio(c.luc), c.loi].filter(Boolean).join(' · ')
}

// Chip người hỏi của mục bí (mockup "Codex 1 hỏi · QC"): chỉ escalation có `khe_id` (T4); thiếu thì bỏ chip.
export function chipNguoiHoi(m) {
  const c = ct(m)
  if (m.loai !== 'escalation' || !c.khe_id) return ''
  const buoc = c.buoc ? ` · ${TEN_BUOC[c.buoc] ?? c.buoc}` : ''
  return `${tenKhe(c.khe_id)} hỏi${buoc}`
}

// "Trả lời" dẫn sang ngăn bên trang Công việc (mockup), nơi có ô trả lời.
export function duongDanTraLoi(m) {
  return { path: '/cong-viec', query: { du_an: m.du_an, bead: m.bead_id } }
}

// Link PR của mục review: PR trạm (2d) trước, rồi link PR trong khối bàn giao; chỉ link GitHub (N1).
export function linkPrReview(m) {
  const c = ct(m)
  if (c.pr_tram && laLinkAnToan(c.pr_tram.url)) return c.pr_tram.url
  return laLinkAnToan(c.pr) ? c.pr : ''
}

const daMerge = (m) => Boolean(ct(m).pr_tram) && ct(m).pr_tram.trang_thai === 'da_merge'

// Câu mô tả dưới tiêu đề (mockup theReview `b.ly_do`); mục cờ đỏ không có câu này.
export function moTaReview(m) {
  if (m.loai !== 'cho-review') return ''
  return daMerge(m) ? 'PR đã merge đúng commit đã kiểm.' : 'Đã code + QC qua; chờ Đại ca review để đóng.'
}

// Ô đóng của mục review (mockup theReview): 'tu-dong' = "trạm đã xác minh — sẽ tự đóng"; 'da-merge' = nút
// "Đã merge trên GitHub → đóng bead"; '' = không có gì. Cờ đỏ không có nút đóng.
export function nutDongReview(m) {
  if (m.loai !== 'cho-review') return ''
  if (daMerge(m)) return 'tu-dong'
  return linkPrReview(m) ? 'da-merge' : ''
}

// Khoá nút ghi: không phải Đại ca → khoá (như cũ); dự án `bat_ghi: false` → khoá + câu D37.
export function khoaThaoTac(laDaiCa, chiQuetThu) {
  return { khoa: !laDaiCa || Boolean(chiQuetThu), chu: chiQuetThu ? CHU_CHI_QUET_THU : '' }
}
```

`frontend/src/thanh/ChiTietSpec.vue` (sửa):

```diff
diff --git a/frontend/src/thanh/ChiTietSpec.vue b/frontend/src/thanh/ChiTietSpec.vue
index 2417293..60e2852 100644
--- a/frontend/src/thanh/ChiTietSpec.vue
+++ b/frontend/src/thanh/ChiTietSpec.vue
@@ -3,6 +3,7 @@ import { computed } from 'vue'
 import { lenhMayA } from '../luat_spec.js'
 
 // "Spec chờ duyệt" (spec 2 §5.2; spec 4 §7.3): commit đang xem, file, bead đề xuất, lệnh mở trên máy A.
+// Lát 2f: giữ logic, đổi sang lớp của mockup (`.bang`, `.bang-cuon`, `.canh-bao`, `.mono`; khối lệnh nền tối) — D36.
 const props = defineProps({ muc: { type: Object, required: true } })
 const ct = computed(() => props.muc.chi_tiet || {})
 const lenh = computed(() => lenhMayA(props.muc, window.location.origin))
@@ -11,20 +12,22 @@ const lenh = computed(() => lenhMayA(props.muc, window.location.origin))
 <template>
   <div class="chi-tiet-spec">
     <ul v-if="ct.loi && ct.loi.length" class="canh-bao"><li v-for="l in ct.loi" :key="l">{{ l }}</li></ul>
-    <p v-if="ct.commit" class="nho">Nhánh <span class="ma">{{ ct.nhanh }}</span> · commit
-      <span class="ma">{{ ct.commit.slice(0, 12) }}</span></p>
-    <ul v-if="ct.file && ct.file.length" class="nho"><li v-for="f in ct.file" :key="f">{{ f }}</li></ul>
-    <table v-if="ct.de_xuat && ct.de_xuat.length" class="bang-cuon">
-      <thead><tr><th>Khoá</th><th>Tiêu đề</th><th>Loại</th><th>P</th><th>Sau</th><th>Nhãn</th></tr></thead>
-      <tbody>
-        <tr v-for="b in ct.de_xuat" :key="b.khoa">
-          <td class="ma">{{ b.khoa }}</td><td>{{ b.tieu_de }}</td><td>{{ b.loai }}</td><td>P{{ b.uu_tien }}</td>
-          <td>{{ (b.phu_thuoc || []).join(', ') }}</td><td>{{ (b.nhan || []).join(', ') }}</td>
-        </tr>
-      </tbody>
-    </table>
+    <p v-if="ct.commit" class="nho">Nhánh <span class="mono">{{ ct.nhanh }}</span> · commit
+      <span class="mono">{{ ct.commit.slice(0, 12) }}</span></p>
+    <ul v-if="ct.file && ct.file.length" class="ds-file mono"><li v-for="f in ct.file" :key="f">{{ f }}</li></ul>
+    <div v-if="ct.de_xuat && ct.de_xuat.length" class="bang-cuon">
+      <table class="bang">
+        <thead><tr><th>Khoá</th><th>Tiêu đề</th><th>Loại</th><th>P</th><th>Sau</th><th>Nhãn</th></tr></thead>
+        <tbody>
+          <tr v-for="b in ct.de_xuat" :key="b.khoa">
+            <td class="mono">{{ b.khoa }}</td><td>{{ b.tieu_de }}</td><td>{{ b.loai }}</td><td>P{{ b.uu_tien }}</td>
+            <td>{{ (b.phu_thuoc || []).join(', ') }}</td><td>{{ (b.nhan || []).join(', ') }}</td>
+          </tr>
+        </tbody>
+      </table>
+    </div>
     <p class="nho">Mở trên máy A — dán vào phiên Claude (skill chỉ đọc, không duyệt thay Đại ca):</p>
-    <pre v-if="lenh" class="van-ban">{{ lenh }}</pre>
+    <pre v-if="lenh" class="lenh">{{ lenh }}</pre>
     <p class="nho">Duyệt xong: Đại ca tạo PR từ nhánh trên tại đúng commit này rồi merge — bead con chỉ được giao
       khi commit đã vào nhánh chính.</p>
   </div>
```

`frontend/src/thanh/phe_duyet/TheBi.vue` (mới):

```vue
<script setup>
import { computed } from 'vue'
import { chipNguoiHoi, duongDanTraLoi } from '../../luat_phe_duyet.js'

// Thẻ "Bí / escalation" và "Decision mở" (mockup trang.js vePheDuyet): mã, dự án, chip "<khe> hỏi · <bước>" (T4),
// tiêu đề, câu hỏi; "Trả lời" dẫn sang ngăn bên trang Công việc, nơi có ô trả lời (OTraLoi). `khoa` nhận chung từ
// trang nhưng link chỉ dẫn đường nên không khoá; câu "chỉ quét thử" vẫn hiện (D37).
const props = defineProps({
  muc: { type: Object, required: true },
  khoa: { type: Boolean, default: false },
  chuKhoa: { type: String, default: '' },
})
const nguoiHoi = computed(() => chipNguoiHoi(props.muc))
const cauHoi = computed(() => (props.muc.chi_tiet && props.muc.chi_tiet.cau_hoi) || '')
</script>

<template>
  <article class="the the-duyet">
    <div>
      <div class="tren">
        <span class="ma">{{ muc.bead_id }}</span><span class="chip">{{ muc.du_an }}</span>
        <span v-if="nguoiHoi" class="chip tt-can_nguoi">{{ nguoiHoi }}</span>
      </div>
      <div class="tieu-de">{{ muc.tieu_de }}</div>
      <div v-if="cauHoi" class="nho">{{ cauHoi }}</div>
    </div>
    <div class="hanh-dong">
      <router-link class="nut chinh" :to="duongDanTraLoi(muc)">Trả lời</router-link>
    </div>
    <p v-if="chuKhoa" class="nho dong-day">{{ chuKhoa }}</p>
  </article>
</template>
```

`frontend/src/thanh/phe_duyet/TheFeatureXong.vue` (mới):

```vue
<script setup>
import { dungThaoTac } from './thao_tac.js'

// Thẻ "Feature xong, chờ đóng" — bản thật có, mockup không vẽ: giữ câu + nút cũ, áp lớp `.the-duyet` (D36).
const props = defineProps({
  muc: { type: Object, required: true },
  khoa: { type: Boolean, default: false },
  chuKhoa: { type: String, default: '' },
})
const emit = defineEmits(['doi'])
const { loi, dangGui, duyet } = dungThaoTac(() => props.muc, emit)
</script>

<template>
  <article class="the the-duyet">
    <div>
      <div class="tren"><span class="ma">{{ muc.bead_id }}</span><span class="chip">{{ muc.du_an }}</span></div>
      <div class="tieu-de">{{ muc.tieu_de }}</div>
      <div class="nho">Mọi {{ muc.chi_tiet.so_con }} bead con đã đóng. Trạm không tự đóng feature (#16).</div>
    </div>
    <div class="hanh-dong">
      <button class="nut chinh" type="button" :disabled="dangGui || khoa" @click="duyet">Đóng feature</button>
    </div>
    <p v-if="chuKhoa" class="nho dong-day">{{ chuKhoa }}</p>
    <p v-if="loi" class="loi dong-day" role="alert">{{ loi }}</p>
  </article>
</template>
```

`frontend/src/thanh/phe_duyet/TheHe.vue` (mới):

```vue
<script setup>
import { computed } from 'vue'
import { chiTietHe, chipHe, tieuDeHe } from '../../luat_phe_duyet.js'
import { dungThaoTac } from './thao_tac.js'

// Thẻ "Hệ cần xem" (mockup trang.js vePheDuyet, `.the-duyet.he`): chip loại + dự án, tiêu đề, chi tiết; "Mở Đội ngũ
// AI" khi là cầu dao khe; "Thử lại" (chấm lại 1a) khi mục gắn bead — bản thật có, mockup không vẽ (D36).
const props = defineProps({
  muc: { type: Object, required: true },
  khoa: { type: Boolean, default: false },
  chuKhoa: { type: String, default: '' },
})
const emit = defineEmits(['doi'])
const { loi, dangGui, thuLai } = dungThaoTac(() => props.muc, emit)
const chip = computed(() => chipHe(props.muc))
const ct = computed(() => props.muc.chi_tiet || {})
</script>

<template>
  <article class="the the-duyet he">
    <div>
      <div class="tren">
        <span class="chip" :class="chip.lop">{{ chip.chu }}</span><span class="chip">{{ muc.du_an }}</span>
        <span v-if="muc.bead_id" class="ma">{{ muc.bead_id }}</span>
      </div>
      <div class="tieu-de">{{ tieuDeHe(muc) }}</div>
      <div class="nho">{{ chiTietHe(muc) }}</div>
    </div>
    <div class="hanh-dong">
      <router-link v-if="ct.khe_id" class="nut" to="/doi-ngu">Mở Đội ngũ AI</router-link>
      <button v-if="muc.bead_id" class="nut" type="button" :disabled="dangGui || khoa" @click="thuLai">Thử lại</button>
    </div>
    <p v-if="chuKhoa" class="nho dong-day">{{ chuKhoa }}</p>
    <p v-if="loi" class="loi dong-day" role="alert">{{ loi }}</p>
  </article>
</template>
```

`frontend/src/thanh/phe_duyet/TheReview.vue` (mới):

```vue
<script setup>
import { computed } from 'vue'
import { NHAN_PR_TRAM, canhBaoPrTram, lopPrTram } from '../../giao_viec.js'
import { laLinkAnToan } from '../../luat.js'
import { linkPrReview, moTaReview, nutDongReview } from '../../luat_phe_duyet.js'
import { dungThaoTac } from './thao_tac.js'

// Thẻ "Chờ review để đóng" và "Cờ đỏ" (mockup trang.js theReview; Q7/D38: hiện trạng thái PR trạm `pr_tram`).
const props = defineProps({
  muc: { type: Object, required: true },
  khoa: { type: Boolean, default: false },
  chuKhoa: { type: String, default: '' },
})
const emit = defineEmits(['doi'])
const { gopY, loi, dangGui, moTraVe, duyet, traVe } = dungThaoTac(() => props.muc, emit)
const ct = computed(() => props.muc.chi_tiet || {})
const prt = computed(() => ct.value.pr_tram || null)
const link = computed(() => linkPrReview(props.muc))
// Link PR trạm: "PR #12 ↗"; chỉ có link bàn giao cũ: "Mở PR (bàn giao + diff)".
const nhanLink = computed(() => (prt.value && laLinkAnToan(prt.value.url)
  ? `${Number.isInteger(prt.value.so) ? `PR #${prt.value.so}` : 'PR'} ↗` : 'Mở PR (bàn giao + diff)'))
const nutDong = computed(() => nutDongReview(props.muc))
const tat = computed(() => dangGui.value || props.khoa)
</script>

<template>
  <article class="the the-duyet">
    <div>
      <div class="tren">
        <span class="ma">{{ muc.bead_id }}</span><span class="chip">{{ muc.du_an }}</span>
        <span v-if="muc.loai === 'co-do'" class="chip tt-loi">cờ đỏ</span>
        <span v-if="lopPrTram(prt)" class="chip" :class="lopPrTram(prt)">{{ NHAN_PR_TRAM[prt.trang_thai] }}</span>
        <a v-if="link" class="nho" :href="link" target="_blank" rel="noopener noreferrer">{{ nhanLink }}</a>
        <span v-else class="nho">Chưa có link PR GitHub.</span>
      </div>
      <div class="tieu-de">{{ muc.tieu_de }}</div>
      <div v-if="moTaReview(muc)" class="nho">{{ moTaReview(muc) }}</div>
      <div v-if="canhBaoPrTram(prt)" class="canh-bao">{{ canhBaoPrTram(prt) }}</div>
      <ul v-if="ct.loi && ct.loi.length" class="canh-bao"><li v-for="l in ct.loi" :key="l">{{ l }}</li></ul>
    </div>
    <div v-if="muc.loai === 'cho-review'" class="hanh-dong">
      <span v-if="nutDong === 'tu-dong'" class="nho">trạm đã xác minh — sẽ tự đóng</span>
      <button v-else-if="nutDong === 'da-merge'" class="nut" type="button" :disabled="tat" @click="duyet">
        Đã merge trên GitHub → đóng bead</button>
      <button class="nut chinh" type="button" :disabled="tat" @click="duyet">Duyệt</button>
      <button class="nut" type="button" :disabled="tat" @click="moTraVe = !moTraVe">Trả về + góp ý</button>
    </div>
    <form v-if="moTraVe" class="gop-y" @submit.prevent="traVe">
      <textarea v-model="gopY" rows="3" maxlength="4000" required aria-label="Góp ý"
                placeholder="Góp ý cho thợ (ghi vào notes, bead về hàng chưa chấm)…"></textarea>
      <button class="nut chinh" type="submit" :disabled="tat || !gopY.trim()">Gửi trả về</button>
    </form>
    <p v-if="nutDong === 'da-merge'" class="nho dong-day">
      Xác nhận "đã merge" là thao tác tay của Đại ca, không phải bằng chứng máy.</p>
    <p v-if="chuKhoa" class="nho dong-day">{{ chuKhoa }}</p>
    <p v-if="loi" class="loi dong-day" role="alert">{{ loi }}</p>
  </article>
</template>
```

`frontend/src/thanh/phe_duyet/TheSpec.vue` (mới):

```vue
<script setup>
import { coTheDuyetSpec } from '../../luat_spec.js'
import ChiTietSpec from '../ChiTietSpec.vue'
import { dungThaoTac } from './thao_tac.js'

// Thẻ "Spec chờ duyệt" — bản thật có, mockup không vẽ: giữ bố cục cũ, áp lớp `.the-duyet` (D36). "Duyệt spec" gửi
// kèm commit + digest đang xem (thanDuyet, trong thao_tac.js).
const props = defineProps({
  muc: { type: Object, required: true },
  khoa: { type: Boolean, default: false },
  chuKhoa: { type: String, default: '' },
})
const emit = defineEmits(['doi'])
const { gopY, loi, dangGui, moTraVe, duyet, traVe } = dungThaoTac(() => props.muc, emit)
</script>

<template>
  <article class="the the-duyet">
    <div>
      <div class="tren"><span class="ma">{{ muc.bead_id }}</span><span class="chip">{{ muc.du_an }}</span></div>
      <div class="tieu-de">{{ muc.tieu_de }}</div>
    </div>
    <div class="hanh-dong">
      <button class="nut chinh" type="button" :disabled="dangGui || khoa || !coTheDuyetSpec(muc)"
              @click="duyet">Duyệt spec</button>
      <button class="nut" type="button" :disabled="dangGui || khoa" @click="moTraVe = !moTraVe">Trả về + góp ý</button>
    </div>
    <form v-if="moTraVe" class="gop-y" @submit.prevent="traVe">
      <textarea v-model="gopY" rows="3" maxlength="4000" required aria-label="Góp ý"
                placeholder="Góp ý cho thợ (ghi vào notes, bead về hàng chưa chấm)…"></textarea>
      <button class="nut chinh" type="submit" :disabled="dangGui || khoa || !gopY.trim()">Gửi trả về</button>
    </form>
    <ChiTietSpec :muc="muc" />
    <p v-if="chuKhoa" class="nho dong-day">{{ chuKhoa }}</p>
    <p v-if="loi" class="loi dong-day" role="alert">{{ loi }}</p>
  </article>
</template>
```

`frontend/src/thanh/phe_duyet/thao_tac.js` (mới):

```js
// Thao tác ghi của một mục Phê duyệt (tách từ MucPheDuyet cũ, giữ nguyên hành vi): gửi kèm `updated_at` đang xem;
// 409 = bản đã đổi → báo + tải lại; 501 = trạm chưa sẵn sàng. Thành công → emit('doi') để trang tải lại.
import { ref } from 'vue'
import { ghi, thanGhi } from '../../api.js'
import { thanDuyet } from '../../luat_spec.js'

export function dungThaoTac(layMuc, emit) {
  const gopY = ref('')
  const loi = ref('')
  const dangGui = ref(false)
  const moTraVe = ref(false)
  const ma = () => `${encodeURIComponent(layMuc().du_an)}/${encodeURIComponent(layMuc().bead_id)}`

  async function lam(duongDan, noiDung) {
    dangGui.value = true
    loi.value = ''
    try {
      await ghi(duongDan, thanGhi(noiDung, layMuc().updated_at))
      gopY.value = ''
      moTraVe.value = false
      emit('doi')
      return true
    } catch (e) {
      loi.value = e.status === 501 ? `Trạm chưa sẵn sàng: ${e.message}`
        : e.status === 409 ? `${e.message} — đã tải lại.` : e.message
      if (e.status === 409) emit('doi')
      return false
    } finally {
      dangGui.value = false
    }
  }
  const duyet = () => lam(`/api/phe-duyet/${ma()}/duyet`, thanDuyet(layMuc()))
  const traVe = () => lam(`/api/phe-duyet/${ma()}/tra-ve`, { gop_y: gopY.value.trim() })
  const traLoi = (vb) => lam(`/api/phe-duyet/${ma()}/tra-loi`, { tra_loi: vb })
  const thuLai = () => lam(`/api/bead/${ma()}/thu-lai`, {})
  return { gopY, loi, dangGui, moTraVe, duyet, traVe, traLoi, thuLai }
}
```

`frontend/src/trang/PheDuyet.vue` (sửa):

```diff
diff --git a/frontend/src/trang/PheDuyet.vue b/frontend/src/trang/PheDuyet.vue
index f9cffa0..f68cc2b 100644
--- a/frontend/src/trang/PheDuyet.vue
+++ b/frontend/src/trang/PheDuyet.vue
@@ -2,20 +2,36 @@
 import { computed, onMounted, ref, watch } from 'vue'
 import { doc } from '../api.js'
 import { kho, taiSoPheDuyet } from '../kho.js'
-import { TEN_PHE_DUYET, nhomPheDuyet } from '../luat.js'
+import { TEN_PHE_DUYET, duAnChiQuetThu, nhomPheDuyet } from '../luat.js'
 import { khoaMuc } from '../luat_doi_ngu.js'
-import MucPheDuyet from '../thanh/MucPheDuyet.vue'
+import { khoaThaoTac } from '../luat_phe_duyet.js'
+import DauTrang from '../thanh/DauTrang.vue'
+import TheBi from '../thanh/phe_duyet/TheBi.vue'
+import TheFeatureXong from '../thanh/phe_duyet/TheFeatureXong.vue'
+import TheHe from '../thanh/phe_duyet/TheHe.vue'
+import TheReview from '../thanh/phe_duyet/TheReview.vue'
+import TheSpec from '../thanh/phe_duyet/TheSpec.vue'
+import '../kieu/phe-duyet.css'
 
+// Trang Phê duyệt (mockup trang.js vePheDuyet, anh-phe-duyet.png): nhóm theo độ gấp, mỗi mục một thẻ `.the-duyet`.
+const THE = { he: TheHe, escalation: TheBi, decision: TheBi, 'cho-review': TheReview, 'co-do': TheReview,
+  spec: TheSpec, 'feature-xong': TheFeatureXong }
+const MO_TA = 'Việc chờ Đại ca, sắp theo độ gấp. Duyệt / Trả về ghi thẳng vào beads với tác nhân dai-ca/dashboard.'
 const ds = ref([])
 const loi = ref('')
 const loiDoc = ref({})
+const chiQuetThu = ref(new Set())          // dự án `bat_ghi: false` (D37)
 const nhom = computed(() => nhomPheDuyet(ds.value))
+const laDaiCa = computed(() => Boolean(kho.trangThai && kho.trangThai.la_dai_ca))
+const khoaCua = (m) => khoaThaoTac(laDaiCa.value, chiQuetThu.value.has(m.du_an))
 
 async function tai() {
   try {
-    const r = await doc('/api/phe-duyet')
+    // /api/du-an lỗi → không biết dự án nào chỉ quét thử; server vẫn từ chối ghi (422) nên coi như không khoá thêm.
+    const [r, da] = await Promise.all([doc('/api/phe-duyet'), doc('/api/du-an').catch(() => ({ du_an: [] }))])
     ds.value = r.muc
-    loiDoc.value = r.loi
+    loiDoc.value = r.loi || {}
+    chiQuetThu.value = duAnChiQuetThu(da.du_an)
     loi.value = ''
   } catch (e) {
     loi.value = e.message
@@ -30,15 +46,17 @@ watch(() => kho.phienBan, tai)
 </script>
 
 <template>
-  <section>
-    <h1>Phê duyệt <span class="dem-nho">{{ kho.soPheDuyet }}</span></h1>
+  <section class="phe-duyet">
+    <DauTrang tieu-de="Phê duyệt" :mo-ta="MO_TA" />
     <p v-if="loi" class="loi" role="alert">{{ loi }}</p>
     <p v-for="(l, t) in loiDoc" :key="t" class="loi">{{ t }}: {{ l }}</p>
     <p v-if="!nhom.length && !loi" class="nho">Không có việc nào chờ Đại ca.</p>
-    <section v-for="[loai, muc] in nhom" :key="loai">
-      <h2>{{ TEN_PHE_DUYET[loai] }} <span class="dem-nho">{{ muc.length }}</span></h2>
-      <MucPheDuyet v-for="m in muc" :key="khoaMuc(m)" :muc="m"
-                   :la-dai-ca="Boolean(kho.trangThai && kho.trangThai.la_dai_ca)" @doi="doi" />
-    </section>
+    <template v-for="[loai, muc] in nhom" :key="loai">
+      <h2 class="muc">{{ TEN_PHE_DUYET[loai] }} <span class="so">{{ muc.length }}</span></h2>
+      <div class="ds-duyet">
+        <component :is="THE[loai]" v-for="m in muc" :key="khoaMuc(m)" :muc="m" :khoa="khoaCua(m).khoa"
+                   :chu-khoa="khoaCua(m).chu" @doi="doi" />
+      </div>
+    </template>
   </section>
 </template>
```

Xoá file thay thế:

```bash
git rm -q frontend/src/thanh/MucPheDuyet.vue
```

- [ ] **Step 4: Chạy thấy PASS**

```bash
cd frontend && node --test tests/phe_duyet.test.mjs
npm run kiem && npm run build && npm run kiem-dist && cd ..
```

Kỳ vọng: PASS — lệnh test của task: pass 4 · fail 0; toàn bộ tăng đúng 4 node test so với main trước task (bảng "Sơ đồ đợt chạy"); `npm run build`, `npm run kiem-dist` xanh. Số đo trên bản chạy thử.

- [ ] **Step 5: Commit**

```bash
git add frontend/tests/phe_duyet.test.mjs frontend/src/kieu/phe-duyet.css frontend/src/luat_phe_duyet.js frontend/src/thanh/ChiTietSpec.vue frontend/src/thanh/phe_duyet/TheBi.vue frontend/src/thanh/phe_duyet/TheFeatureXong.vue frontend/src/thanh/phe_duyet/TheHe.vue frontend/src/thanh/phe_duyet/TheReview.vue frontend/src/thanh/phe_duyet/TheSpec.vue frontend/src/thanh/phe_duyet/thao_tac.js frontend/src/trang/PheDuyet.vue && git rm -q --cached --ignore-unmatch frontend/src/thanh/MucPheDuyet.vue
git commit -m "feat(dashboard): 2f trang Phê duyệt theo mockup"
```

### Task 12: Văn phòng 3D theo mockup — cảnh, nhãn phủ, panel, bản danh sách

**Đợt:** 3 · **Độ khó:** khó · **Phải xong trước:** Task 1, 2 (Task 7 cho `cau_dao_ngat`, `suc_khoe.muc`) · **Test mới:** 6 node (bố trí/nhãn/hiển thị 7 + cảnh 4 thay 5 test bố trí cũ)

**Mockup bám:** `van-phong.js` (PHONG, MAU, CHO, đồ vật, nhân vật chibi, ánh sáng, camera `khit()`, lớp phủ, bấm chọn, vòng vẽ), `bo-tri-nhan.js` (port nguyên `boTriNhan`, `demChong`), `trang-van-phong.js` (panel `noiDungPanel`, bản danh sách, giảm chuyển động nhớ `localStorage`), `style.css` mục "Văn phòng"; ảnh `anh-van-phong.png`, `anh-van-phong-1280.png`, `anh-van-phong-1024.png`, `anh-van-phong-ca-trang.png`, `anh-van-phong-bam-nhan-vat.png` (ảnh thiết kế gốc không đăng ở bản public). Khảo sát §1.2, §2.3 mục 6–8. G8, G9, G10, G17, G18.

**Files:**
- Create: `frontend/src/van_phong/bo_tri_nhan.js`, `khung_nhin.js` (khít khung thuần), `cho_nv.js` (chỗ nhân vật mỗi phòng), `do_vat.js` (vật liệu + bàn/màn hình/cây/cốc/ghế), `do_vat_tram.js` (tủ máy theo `suc_khoe.muc`, đèn Điều phối), `dung_phong.js` (sàn, tường chung có cửa, tường trước thấp), `dung_do_vat.js` (đồ từng loại phòng), `nhan_vat_3d.js` (chibi), `dung_canh.js` (ghép cảnh + `huy`), `nhan_canh.js` (dữ liệu nhãn phủ), `LopNhan.vue`, `PanelChon.vue`, `frontend/src/kieu/van-phong.css`
- Modify (viết lại): `frontend/src/trang/VanPhong.vue`, `frontend/src/van_phong/CanhVanPhong.vue`, `DanhSachVanPhong.vue`, `bo_tri.js`; (sửa): `hien_thi.js` (`MAU` theo mockup, giữ `den '#f2c14e'`, `denTat`, các hàm `tuThe catChu chuBien chuNhip chuBongBong duongDanNhanVat duongDanPhong`; bỏ `mauThan` — màu thân lấy `mauKhe`)
- Delete: `van_phong/NhanVat3D.vue`, `Phong3D.vue`, `TheChu3D.vue`, `the_chu.js` (chữ canvas → nhãn HTML phủ: nét, đúng font, có `aria`)
- Test: `frontend/tests/van_phong.test.mjs` (sửa), `frontend/tests/van_phong_canh.test.mjs` (mới); `dieu_phoi.test.mjs` (2e) vẫn xanh

**Interfaces:**
- Consumes: `/api/van-phong` (`sang`, `nhip_cuoi` 2e; `cau_dao_ngat`, `suc_khoe.muc` Task 7), `/api/du-an` (`bat_ghi`), `mauKhe`, `kho.phienBan`, `kho.phienBanDoiNgu`.
- TresJS 5.9.1 / three 0.186.1 (khảo sát §2.3 mục 8): `TresOrthographicCamera :look-at="[0, 0, 0]"` (bắt buộc — bài học 2c T8), khít khung tính sau khi đặt vị trí + `lookAt` rồi `updateMatrixWorld()`; `TresCanvas :tone-mapping="NoToneMapping" :alpha="true" :clear-alpha="0" :shadows="true" :shadow-map-type="PCFShadowMap"` (`alpha` cần vì renderer Tres mặc định `alpha: false` — chỉ `clear-alpha 0` thì nền đen); `shadow.radius`; đồ đạc/nhân vật dựng bằng module three thuần gắn `<primitive>`, `dispose` khi unmount; sự kiện con trỏ viết `@pointerenter`/`@pointerleave` (Tres chỉ nhận `onPointerenter`).

Lệch mockup có chủ ý: bỏ dòng chú thích góc `.vp-goc` (chỉ của mockup); bong bóng không nhún theo nhân vật (vị trí nhãn chỉ tính khi đổi cỡ/dữ liệu — không cập nhật DOM mỗi khung); mọi phòng dự án dùng bố trí 3 bàn + 1 cây như hr-codex; huy hiệu Giám đốc chỉ khi `so_cho > 0`; panel dùng dữ liệu thật (API không có lý do cầu dao/lý do tắt ở `/api/van-phong`). Không có WebGL2: khung vẫn có dòng `.loi-webgl` để panel mở từ bản danh sách vẫn hiện.

- [ ] **Step 1: Viết test (chép nguyên văn)**

`frontend/tests/van_phong.test.mjs` (sửa):

```diff
diff --git a/frontend/tests/van_phong.test.mjs b/frontend/tests/van_phong.test.mjs
index 02f41b4..8c80a51 100644
--- a/frontend/tests/van_phong.test.mjs
+++ b/frontend/tests/van_phong.test.mjs
@@ -1,65 +1,111 @@
 import assert from 'node:assert/strict'
 import { test } from 'node:test'
-import { CANH, boTriPhong, datNhanVat, khungNhin } from '../src/van_phong/bo_tri.js'
-import { MAU, catChu, chuBien, chuBongBong, duongDanNhanVat, duongDanPhong, mauThan, tuThe }
-  from '../src/van_phong/hien_thi.js'
+import { O, boTriVanPhong, mauTuMay, oDuAn } from '../src/van_phong/bo_tri.js'
+import { MAU, catChu, chuBien, chuBongBong, duongDanNhanVat, duongDanPhong, tuThe } from '../src/van_phong/hien_thi.js'
+import { dungNhan, nhanPhu, timMucChon } from '../src/van_phong/nhan_canh.js'
 
-const PHONG = [{ ma: 'dieu-phoi', loai: 'dieu_phoi', sang: null }, { ma: 'giam-doc', loai: 'giam_doc', so_cho: 2 },
-  { ma: 'may-chu', loai: 'may_chu' }, { ma: 'ca-phe', loai: 'ca_phe' },
-  { ma: 'du-an:hr', loai: 'du_an', ten: 'hr', du_an: 'hr' }]
+// Dữ liệu kiểu mockup du-lieu.js / van-phong.js PHONG + KHE (D20), dạng API /api/van-phong + /api/du-an.
+const PHONG = [{ ma: 'giam-doc', loai: 'giam_doc', so_cho: 4 }, { ma: 'dieu-phoi', loai: 'dieu_phoi', sang: null },
+  { ma: 'may-chu', loai: 'may_chu', suc_khoe: { mau: 'vang', ly_do: ['claude-4'], muc: [{ mau: 'vang' }] } },
+  { ma: 'ca-phe', loai: 'ca_phe' }, ...['hr-codex', 'tram', 'ke-toan'].map(duAn)]
+const DU_AN = [{ ten: 'ke-toan', bat_ghi: false }, { ten: 'tram' }]
+const NV = [nv('claude-1', 'lam', 'du-an:hr-codex', 'hr-1'), nv('codex-1', 'can_nguoi', 'du-an:hr-codex', 'hr-3'),
+  nv('claude-2', 'ranh', 'ca-phe'), nv('claude-3', 'tat', 'ca-phe'), { ...nv('codex-2', 'tat', 'ca-phe'),
+    trang_thai: 'mat_ket_noi' }, { ...nv('claude-4', 'loi', 'ca-phe'), cau_dao_ngat: true }]
+function duAn(ten) { return { ma: `du-an:${ten}`, loai: 'du_an', ten, du_an: ten } }
+function nv(khe, ht, phong, bead) {
+  const b = bead ? { du_an: 'hr-codex', bead_id: bead, tieu_de: `Việc ${bead}`, buoc: 'code' } : null
+  return { khe_id: khe, ten: khe, cli: 'claude', trang_thai: ht, hien_thi: ht, phong, bead: b }
+}
+const trong = (p, x, z) => x > p.x[0] && x < p.x[1] && z > p.z[0] && z < p.z[1]
+const tim = (b, ma) => b.phong.find((p) => p.ma === ma)
 
-test('bố trí phòng thành lưới quanh gốc toạ độ, không chồng nhau', () => {
-  const ds = boTriPhong(PHONG)
-  assert.equal(ds.length, 5)
-  const o = new Set(ds.map((p) => `${p.x},${p.z}`))
-  assert.equal(o.size, 5)
-  const xs = ds.map((p) => p.x)
-  assert.equal(Math.min(...xs) + Math.max(...xs), 0)
-  assert.ok(ds.every((p) => Math.abs(p.x) % CANH.buoc === 0 || Math.abs(p.x) % CANH.buoc === CANH.buoc / 2))
-  assert.ok(khungNhin(ds) >= Math.max(...xs) + CANH.phong / 2)
-  assert.deepEqual(boTriPhong([]), [])
+test('bố trí ba dự án đúng ô mockup, ô 10 m, Góc cà phê hai ô, màu cố định', () => {
+  const b = boTriVanPhong(PHONG, NV, DU_AN)
+  const o = (ma) => [tim(b, ma).x, tim(b, ma).z]
+  assert.equal(O, 10)
+  assert.deepEqual(o('giam-doc'), [[-15, -5], [-15, -5]])
+  assert.deepEqual(o('dieu-phoi'), [[-5, 5], [-5, 5]])
+  assert.deepEqual(o('may-chu'), [[5, 15], [-5, 5]])
+  assert.deepEqual(o('ca-phe'), [[-15, 5], [5, 15]])
+  assert.deepEqual(o('du-an:hr-codex'), [[-15, -5], [-5, 5]])
+  assert.deepEqual(o('du-an:tram'), [[-5, 5], [-15, -5]])
+  assert.deepEqual(o('du-an:ke-toan'), [[5, 15], [-15, -5]])
+  assert.deepEqual([tim(b, 'giam-doc').san, tim(b, 'may-chu').tuong], ['#f8e6d4', '#b2c2cc'])
+  assert.deepEqual([tim(b, 'du-an:hr-codex').san, tim(b, 'du-an:tram').san], ['#f5d6d3', '#fbdcc8'])
+  assert.deepEqual(tim(b, 'giam-doc').nhan, [-11.6, -12.6])                       // neo biển như mockup
+  assert.deepEqual(tim(b, 'du-an:hr-codex').nhan, [-9.2, 3.9])
 })
 
-test('đặt nhân vật vào chỗ trong phòng; phòng lạ về góc cà phê', () => {
-  const ds = boTriPhong(PHONG)
-  const nv = datNhanVat(ds, [{ khe_id: 'B/b', phong: 'du-an:hr' }, { khe_id: 'B/a', phong: 'du-an:hr' },
-    { khe_id: 'B/c', phong: 'du-an:la' }])
-  const hr = ds.find((p) => p.ma === 'du-an:hr')
-  const cp = ds.find((p) => p.ma === 'ca-phe')
-  const [a, b, c] = ['B/a', 'B/b', 'B/c'].map((k) => nv.find((x) => x.khe_id === k))
-  assert.notDeepEqual([a.x, a.z], [b.x, b.z])
-  assert.ok(Math.abs(a.x - hr.x) < CANH.phong / 2 && Math.abs(a.z - hr.z) < CANH.phong / 2)
-  assert.ok(Math.abs(c.x - cp.x) < CANH.phong / 2)
+test('bat_ghi false (D37): phòng mờ xám, biển "(chỉ quét thử)"; thiếu trường = bật', () => {
+  const b = boTriVanPhong(PHONG, NV, DU_AN)
+  const kt = tim(b, 'du-an:ke-toan')
+  assert.deepEqual([kt.mo, kt.san, kt.tenBien], [true, '#ebe5de', 'ke-toan (chỉ quét thử)'])
+  assert.deepEqual([tim(b, 'du-an:tram').mo, tim(b, 'du-an:tram').tenBien], [false, 'tram'])
+  assert.equal(boTriVanPhong(PHONG, NV, []).phong.filter((p) => p.mo).length, 0)
+  assert.ok(b.ban.filter((x) => x.phong === 'du-an:ke-toan').every((x) => x.man === 'tat'))
 })
 
-test('tư thế theo năm hàng của bảng §5.5', () => {
-  assert.deepEqual(tuThe('lam'), { ngoi: true, giaTay: false, chamDo: false, manHinh: 'sang', doMo: 1 })
-  assert.deepEqual(tuThe('ranh'), { ngoi: false, giaTay: false, chamDo: false, manHinh: null, doMo: 1 })
-  assert.deepEqual(tuThe('can_nguoi'), { ngoi: true, giaTay: true, chamDo: true, manHinh: 'sang', doMo: 1 })
-  assert.equal(tuThe('loi').manHinh, 'do')
-  assert.deepEqual(tuThe('tat'), { ngoi: true, giaTay: false, chamDo: false, manHinh: 'tat', doMo: 0.35 })
-  assert.deepEqual(tuThe('la'), tuThe('tat'))
+test('hơn 3 dự án thêm hàng phía sau (D38/Q9), không chồng ô', () => {
+  assert.deepEqual([0, 1, 2, 3, 5, 6].map(oDuAn), [[-1, 0], [0, -1], [1, -1], [-1, -2], [1, -2], [-1, -3]])
+  const b = boTriVanPhong([...PHONG, duAn('a'), duAn('b')], NV, DU_AN)
+  assert.deepEqual([tim(b, 'du-an:a').x, tim(b, 'du-an:a').z], [[-15, -5], [-25, -15]])
+  assert.deepEqual([tim(b, 'du-an:b').x, tim(b, 'du-an:b').z], [[-5, 5], [-25, -15]])
+  const o = b.phong.flatMap((p) => p.o.map(([x, z]) => `${x},${z}`))
+  assert.equal(new Set(o).size, o.length)
+  assert.equal(b.phong.length, 9)
+})
+
+test('nhân vật nằm trong phòng theo nhan_vat[].phong; phòng lạ về cà phê; không trùng chỗ', () => {
+  const ranh = ['a', 'b', 'c', 'd'].map((k) => nv(k, 'ranh', 'ca-phe'))
+  const ds = [...NV, nv('codex-9', 'lam', 'du-an:da-go', 'x-1'), ranh[0], ranh[1], ranh[2], ranh[3]]
+  const b = boTriVanPhong(PHONG, ds, DU_AN)
+  for (const n of b.nhanVat) assert.ok(trong(tim(b, n.phongMa), n.x, n.z), n.khe_id)
+  assert.equal(b.nhanVat.find((n) => n.khe_id === 'codex-9').phongMa, 'ca-phe')
+  assert.equal(b.nhanVat.find((n) => n.khe_id === 'claude-1').phongMa, 'du-an:hr-codex')
+  const cho = b.nhanVat.map((n) => `${n.x},${n.z}`)
+  assert.equal(new Set(cho).size, cho.length)
+  const c1 = b.nhanVat.find((n) => n.khe_id === 'claude-1')
+  assert.ok(b.ban.some((x) => x.x === c1.x && Math.abs(c1.z - x.z - 1.4) < 1e-9))     // đứng trước bàn
+  const c4 = b.nhanVat.find((n) => n.khe_id === 'claude-4')
+  assert.deepEqual([c4.ngoi, b.ban.find((x) => x.khe === 'claude-4').man], [true, 'do'])   // lỗi: màn đỏ
+  assert.equal(b.nhanVat.find((n) => n.khe_id === 'claude-2').ngoi, false)
+})
+
+test('tủ máy chủ theo suc_khoe.muc, thiếu → xanh', () => {
+  assert.deepEqual(mauTuMay(PHONG[2]), ['vang', 'xanh', 'xanh', 'xanh'])
+  assert.deepEqual(mauTuMay({ suc_khoe: { mau: 'do', ly_do: [] } }), ['xanh', 'xanh', 'xanh', 'xanh'])
 })
 
-test('chữ biển, bong bóng, cắt chữ theo ký tự', () => {
-  assert.equal(chuBien(PHONG[1]), 'Phòng giám đốc · 2 việc chờ')
-  assert.equal(chuBien(PHONG[0]), 'Điều phối · chưa có tín hiệu')
-  assert.equal(chuBien({ ...PHONG[0], sang: true }), 'Điều phối · đang có phiên')
-  assert.equal(chuBien(PHONG[4]), 'hr')
+test('nhãn: biển, tên + nhãn phụ, bong bóng, huy hiệu đỏ, huy hiệu Giám đốc', () => {
+  assert.deepEqual(NV.map(nhanPhu), ['Làm', 'Cần người', 'Rảnh', 'Tắt', 'Mất kết nối', 'Lỗi · cầu dao ngắt'])
+  assert.equal(nhanPhu({ hien_thi: 'loi', trang_thai: 'loi' }), 'Lỗi')
+  const ds = dungNhan(boTriVanPhong(PHONG, NV, DU_AN))
+  const dem = (l) => ds.filter((n) => n.loai === l).length
+  assert.deepEqual(['bien', 'ten', 'bb', 'hh', 'gd'].map(dem), [7, 6, 2, 1, 1])
+  assert.equal(ds.find((n) => n.id === 'gd').chu, '4')
+  assert.deepEqual(ds.find((n) => n.id === 'bien:dieu-phoi').den, { sang: false, chu: 'chưa có tín hiệu' })
+  const bb = ds.find((n) => n.id === 'bb:codex-1')
+  assert.deepEqual([bb.ma, bb.chu, bb.chon], ['hr-3', 'Việc hr-3 · code', { loai: 'khe', khe_id: 'codex-1' }])
+  assert.ok(ds.every((n) => n.nhanDoc && n.neo.length === 3))
+  const b = boTriVanPhong(PHONG, NV, DU_AN)                                  // panel lấy bản mới nhất (D38/Q8)
+  assert.equal(timMucChon(b, bb.chon).nv.bead.bead_id, 'hr-3')
+  assert.deepEqual([timMucChon(b, { loai: 'phong', ma: 'may-chu' }).khoa, timMucChon(b, null)], ['phong:may-chu', null])
+  assert.equal(timMucChon(b, { loai: 'khe', khe_id: 'da-go' }), null)
+})
+
+test('hiển thị giữ từ 2c/2e: tư thế, chữ biển, bong bóng, đường dẫn, bảng màu mockup', () => {
+  assert.deepEqual(tuThe('can_nguoi'), { ngoi: true, giaTay: true, chamDo: true, manHinh: 'sang', doMo: 1 })
+  assert.deepEqual(tuThe('la'), tuThe('tat'))
+  assert.equal(chuBien(PHONG[0]), 'Phòng giám đốc · 4 việc chờ')
   assert.equal(catChu('Sửa cắt tóm tắt', 8), 'Sửa cắt…')
-  assert.equal(catChu('ngắn', 8), 'ngắn')
   assert.equal(chuBongBong({ hien_thi: 'lam', bead: { tieu_de: 'Sửa thuế', buoc: 'qc' } }), 'Sửa thuế · QC')
   assert.equal(chuBongBong({ hien_thi: 'ranh', bead: null }), null)
-})
-
-test('đường dẫn khi bấm và màu pastel', () => {
   assert.deepEqual(duongDanNhanVat({ bead: { du_an: 'hr', bead_id: 'hr-1' } }),
     { path: '/cong-viec', query: { du_an: 'hr', bead: 'hr-1' } })
-  assert.deepEqual(duongDanNhanVat({ bead: null }), { path: '/doi-ngu' })
-  assert.deepEqual(duongDanPhong(PHONG[4]), { path: '/cong-viec', query: { du_an: 'hr' } })
-  assert.deepEqual(duongDanPhong(PHONG[1]), { path: '/phe-duyet' })
-  assert.equal(duongDanPhong(PHONG[0]), null)
-  assert.equal(mauThan('claude'), MAU.than.claude)
-  assert.equal(mauThan('gemini'), MAU.than.khac)
+  assert.deepEqual(duongDanPhong(duAn('hr')), { path: '/cong-viec', query: { du_an: 'hr' } })
+  assert.equal(duongDanPhong(PHONG[1]), null)
+  assert.deepEqual([MAU.go, MAU.man, MAU.manDo, MAU.tu, MAU.den],
+    ['#c79d74', '#9fd0ee', '#e0574a', '#30363c', '#f2c14e'])
   assert.ok(Object.values(MAU.suc_khoe).every((m) => /^#[0-9a-f]{6}$/.test(m)))
 })
```

`frontend/tests/van_phong_canh.test.mjs` (mới):

```js
import assert from 'node:assert/strict'
import { test } from 'node:test'
import { OrthographicCamera } from 'three'
import { boTriVanPhong } from '../src/van_phong/bo_tri.js'
import { boTriNhan, demChong } from '../src/van_phong/bo_tri_nhan.js'
import { dungCanh, huyCanh } from '../src/van_phong/dung_canh.js'
import { PHONG_TO, chieuNhan, coChu, gocSan, khit } from '../src/van_phong/khung_nhin.js'
import { dungNhan, xepNhan } from '../src/van_phong/nhan_canh.js'

// Cảnh three chạy trong node (không WebGL). Dữ liệu kiểu mockup van-phong.js (D20).
const PHONG = [{ ma: 'giam-doc', loai: 'giam_doc', so_cho: 4 }, { ma: 'dieu-phoi', loai: 'dieu_phoi', sang: null },
  { ma: 'may-chu', loai: 'may_chu', suc_khoe: { mau: 'vang', ly_do: ['a', 'b'], muc: [{ mau: 'vang' },
    { mau: 'do' }] } },
  { ma: 'ca-phe', loai: 'ca_phe' }, ...['hr-codex', 'tram', 'ke-toan'].map((t) => ({ ma: `du-an:${t}`, loai: 'du_an',
    ten: t, du_an: t }))]
const BEAD = (id, t) => ({ du_an: 'hr-codex', bead_id: id, tieu_de: t, buoc: 'code' })
const NV = [['claude-1', 'lam', 'du-an:hr-codex', BEAD('hr-1', 'Sửa cắt UTF-8 tóm tắt hoàn tiền')],
  ['codex-1', 'can_nguoi', 'du-an:hr-codex', BEAD('hr-3', 'Chọn cách tính thuế')], ['claude-2', 'ranh', 'ca-phe'],
  ['claude-3', 'tat', 'ca-phe'], ['codex-2', 'tat', 'ca-phe'], ['claude-4', 'loi', 'ca-phe']]
  .map(([k, h, p, b]) => ({ khe_id: k, ten: k.replace('-', ' '), trang_thai: h, hien_thi: h, phong: p,
    bead: b ?? null }))
const BO_TRI = boTriVanPhong(PHONG, NV, [{ ten: 'ke-toan', bat_ghi: false }])

function camera() {
  const c = new OrthographicCamera(-1, 1, 1, -1, 0.1, 400)
  c.position.set(40, 40, 40)
  c.lookAt(0, 0, 0)
  return c
}
function datKhung(c, w, h, to) {
  Object.assign(c, khit(c, gocSan(BO_TRI.phong), w, h, to))
  c.updateProjectionMatrix()
}
// Ước cỡ nhãn như CSS mục Văn phòng (chữ đậm ~0,62 em mỗi ký tự): đủ để kiểm thuật toán, trình duyệt đo thật.
function uocCo(n, f) {
  const dai = (s, k) => [...String(s ?? '')].length * 0.62 * f * k
  if (n.loai === 'bien') return { w: dai(n.chu, 1.19) + (n.den ? 7 * f : 0) + 2 * f + 3, h: 2.1 * f }
  if (n.loai === 'ten') return { w: Math.max(dai(n.chu, 1.06), dai(n.phu, 0.66)), h: 1.9 * f }
  if (n.loai === 'bb') return { w: dai(`${n.ma} ${n.chu}`, 0.875) + 1.5 * f + 3, h: 1.9 * f }
  if (n.loai === 'hh') return { w: 2.2 * f + 5, h: 2.2 * f + 5 }
  return { w: dai(`${n.chu} việc chờ`, 0.875) + 1.7 * f, h: 2 * f + 5 }
}

test('khít khung: mọi góc sàn nằm trong khung khi không phóng; PHONG_TO phóng 1,12 lần quanh tâm', () => {
  for (const [w, h] of [[1100, 640], [343, 460], [1280, 400]]) {
    const c = camera()
    datKhung(c, w, h, 1)
    for (const v of gocSan(BO_TRI.phong)) {
      const p = v.clone().project(c)
      assert.ok(Math.abs(p.x) <= 1 && Math.abs(p.y) <= 1, `${w}x${h} ${v.toArray()}`)
    }
    const r = (k) => (k.right - k.left) / (k.top - k.bottom)
    const a = khit(c, gocSan(BO_TRI.phong), w, h, 1)
    const b = khit(c, gocSan(BO_TRI.phong), w, h)
    assert.ok(Math.abs(r(a) - w / h) < 1e-9 && Math.abs((a.right - a.left) / (b.right - b.left) - PHONG_TO) < 1e-9)
  }
})

test('boTriNhan: không chồng nhãn với dữ liệu kiểu mockup ở 1280, 1024, 375 px', () => {
  for (const [w, h] of [[1280, 700], [1108, 646], [1024, 600], [740, 540], [343, 460]]) {
    const c = camera()
    datKhung(c, w, h)
    const nhan = dungNhan(BO_TRI)
    const f = coChu(w)
    const co = Object.fromEntries(nhan.map((n) => [n.id, uocCo(n, f)]))
    const kq = xepNhan(nhan, chieuNhan(c, w, h, nhan, BO_TRI.nhanVat), co)
    assert.equal(kq.chong, 0, `${w}x${h}`)
    assert.equal(Object.keys(kq.viTri).length, nhan.length)
    for (const n of nhan) {
      const v = kq.viTri[n.id]
      assert.ok(v.x >= 2 && v.y >= 2 && v.x + co[n.id].w <= w - 2 + 1e-9, `${n.id} trong khung ${w}`)
    }
  }
})

test('boTriNhan: thứ tự ưu tiên bong bóng trước biển; đường chỉ khi dời > 10 px', () => {
  const o = (loai, x0, y0) => ({ loai, w: 100, h: 20, x0, y0, diemNeo: { x: x0 + 50, y: y0 + 40 } })
  const bien = o('bien', 100, 100)
  const bb = o('bb', 100, 100)
  const duong = boTriNhan([bien, bb], [], 800, 600)
  assert.deepEqual([bb.x, bb.y], [100, 100])                                   // bong bóng giữ chỗ
  assert.ok(Math.hypot(bien.x - 100, bien.y - 100) > 10)
  assert.equal(duong.length, 1)
  assert.deepEqual(duong[0].slice(0, 2), [150, 140])
  assert.equal(demChong([bien, bb]), 0)
  const mot = o('ten', 10, 10)
  assert.deepEqual(boTriNhan([mot], [], 800, 600), [])
  assert.equal(demChong([{ x: 0, y: 0, w: 10, h: 10 }, { x: 5, y: 5, w: 10, h: 10 }]), 1)
})

test('khói dựng cảnh: phòng, sàn bấm được, tủ máy theo muc, đèn Điều phối', () => {
  const canh = dungCanh(BO_TRI)
  const san = []
  canh.goc.traverse((o) => { if (o.userData.chon?.loai === 'phong' && o.isMesh) san.push(o.userData.chon.ma) })
  assert.deepEqual(san.sort(), PHONG.map((p) => p.ma).sort())
  const khe = []
  canh.goc.traverse((o) => { if (o.userData.chon?.loai === 'khe') khe.push(o.userData.chon.khe_id) })
  assert.deepEqual(khe.sort(), NV.map((n) => n.khe_id).sort())
  const tu = canh.goc.userData.tu.map((m) => m.material.color.getHexString())
  assert.deepEqual(tu, ['f2c14e', 'e0574a', '5fd38a', '5fd38a'])
  const den = (sang) => dungCanh(boTriVanPhong(PHONG.map((p) => ({ ...p, sang })), NV, [])).goc.userData.den.material
  assert.deepEqual([den(true).emissive.getHexString(), den(true).color.getHexString()], ['f2c14e', 'f2c14e'])
  assert.deepEqual([den(false).emissive.getHexString(), den(false).color.getHexString()], ['000000', 'b7b7b7'])
  assert.equal(canh.dong.filter((d) => d.man).length, 1)                       // màn đỏ của khe lỗi nhấp nháy
  huyCanh(canh.goc)
})
```

- [ ] **Step 2: Chạy thấy FAIL**

```bash
cd frontend && node --test tests/van_phong.test.mjs tests/van_phong_canh.test.mjs
```

Kỳ vọng: FAIL — `Error [ERR_MODULE_NOT_FOUND]: Cannot find module '…/frontend/src/van_phong/nhan_canh.js' imported from …/frontend/tests/van_phong.test.mjs`

- [ ] **Step 3: Viết mã (chép nguyên văn; file sửa: chép khối diff ra file tạm, `git apply --check` rồi `git apply`)**

`frontend/src/kieu/van-phong.css` (mới):

```css
/* Trang Văn phòng — mockup style.css mục "Văn phòng" (D20). Nhãn phủ là <button> thật nên thêm phần đặt lại nút. */
.gc {
  white-space: nowrap; display: inline-flex; align-items: center; gap: 6px; font-size: 13px; color: var(--chu-2);
  background: var(--the); border: 1px solid var(--vien-dam); border-radius: 8px; padding: 0 10px; height: 32px;
  cursor: pointer;
}
.gc input { accent-color: var(--nhan); }
.canh-khung {
  position: relative; height: 72vh; min-height: 460px; border: 1px solid var(--vien); border-radius: 16px;
  background: radial-gradient(ellipse at 50% 40%, #fdf9f3 0%, #f7efe4 75%); overflow: hidden;
}
.canh-khung canvas { display: block; width: 100%; height: 100%; }
.lop-phu { position: absolute; inset: 0; pointer-events: none; }
.lop-phu > * { position: absolute; left: 0; top: 0; will-change: transform; }
:where(.lop-phu) button { margin: 0; text-align: inherit; }
.lop-phu .chua { visibility: hidden; }
.bien-phong {
  pointer-events: auto; cursor: pointer; background: #fffdfa; border: 1.5px solid #e2d4c4; border-radius: 999px;
  padding: .26em .84em .32em; font-weight: 700; font-size: 1.19em; letter-spacing: -.2px; white-space: nowrap;
  color: #3a2a21; box-shadow: 0 2px 6px #6b4a3014; display: flex; align-items: center; gap: .42em;
}
.bien-phong:hover { border-color: var(--nhan); }
.bien-phong small { font-size: .6em; font-weight: 500; color: var(--chu-phu); }
.bien-phong.mo { opacity: .7; }
.bien-phong .den {
  width: .47em; height: .47em; border-radius: 50%; background: #b9b2aa; box-shadow: inset 0 0 0 1px #0002;
}
.bien-phong .den.sang { background: #f2c14e; box-shadow: 0 0 0 .2em #f2c14e44; }   /* vàng ấm D38 = MAU.den */
.ten-nv {
  font-weight: 800; font-size: 1.06em; color: #2b1f19; white-space: nowrap; text-align: center; line-height: 1.1;
  text-shadow: 0 0 3px #fffaf3, 0 0 6px #fffaf3; pointer-events: auto; cursor: pointer;
  background: none; border: 0; padding: 0;
}
.ten-nv small { display: block; font-size: .62em; font-weight: 600; color: var(--chu-phu); letter-spacing: .1px; }
.ten-nv.mo { opacity: .5; }
.bong-bong {
  pointer-events: auto; cursor: pointer; background: #fff; border: 1.5px solid #e2d4c4; border-radius: .85em;
  padding: .43em .85em; font-size: .875em; white-space: nowrap; color: #3a2a21; box-shadow: 0 3px 10px #6b4a301c;
}
.bong-bong::after {
  content: ''; position: absolute; left: 50%; bottom: -7px; width: 11px; height: 11px; background: #fff;
  border-right: 1.5px solid #e2d4c4; border-bottom: 1.5px solid #e2d4c4; transform: translateX(-50%) rotate(45deg);
}
.bong-bong b { font-family: var(--mono); font-weight: 500; font-size: .86em; color: var(--nhan); margin-right: 6px; }
.huy-hieu-do {
  width: 2.1em; height: 2.1em; border-radius: 50%; background: #8f2f19; color: #fff; display: grid;
  place-items: center; font-weight: 800; font-size: 1.06em; border: 2.5px solid #fff4ec; padding: 0;
  box-shadow: 0 3px 8px #7f321a55; pointer-events: auto; cursor: pointer;
}
.huy-hieu-do.lon {
  width: auto; min-width: 2.4em; height: 2.3em; padding: 0 .85em; border-radius: 999px; font-size: .875em; gap: .4em;
  display: flex; align-items: center;
}
.huy-hieu-do .phu { font-weight: 600; font-size: .86em; }
.lop-phu svg.duong-chi { width: 100%; height: 100%; overflow: visible; }
.duong-chi line { stroke: #8a6a55; stroke-width: 1.2; stroke-dasharray: 3 3; opacity: .75; }
.duong-chi circle { fill: #8a6a55; opacity: .8; }
.vp-panel {
  position: absolute; right: 16px; bottom: 16px; width: 320px; max-width: calc(100% - 32px); background: #fff;
  border: 1px solid var(--vien-dam); border-radius: 14px; box-shadow: 0 10px 30px #5a3a2230; padding: 14px 16px;
  font-size: 14px;
}
.vp-panel h3 { margin: 0 0 4px; font-size: 16px; display: flex; gap: 8px; align-items: center; padding-right: 18px; }
.vp-panel p { margin: 6px 0; color: var(--chu-2); }
.vp-panel ul { margin: 4px 0; padding-left: 18px; }
.vp-panel .hang-nut { display: flex; gap: 8px; margin-top: 10px; }
.vp-panel .dong {
  position: absolute; right: 10px; top: 8px; border: 0; background: none; font-size: 18px; color: var(--chu-phu);
}
.loi-webgl { position: absolute; inset: 0; display: grid; place-items: center; color: var(--chu-2); padding: 16px; }

.ds-phong { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(250px, 100%), 1fr)); gap: 12px; }
.the-phong {
  cursor: pointer; display: flex; flex-direction: column; gap: 8px; border-left-width: 6px; text-align: left;
  font: inherit; color: inherit;
}
.the-phong:hover { border-color: var(--vien-dam); box-shadow: 0 4px 14px #6b4a3014; }
.the-phong .dau { display: flex; align-items: center; gap: 8px; width: 100%; }
.the-phong .dau .cham { width: 12px; height: 12px; margin: 0; }
.the-phong .dau strong { font-size: 15.5px; }
.the-phong .dau .nho { margin-left: auto; }
.the-phong .ds-nv { display: flex; flex-wrap: wrap; gap: 6px; }
.the-phong.mo { opacity: .6; }
@media (max-width: 600px) {
  .vp-panel { left: 12px; right: 12px; bottom: 12px; width: auto; max-width: none; }
}
```

`frontend/src/trang/VanPhong.vue` (sửa):

```diff
diff --git a/frontend/src/trang/VanPhong.vue b/frontend/src/trang/VanPhong.vue
index 5d5e536..772071e 100644
--- a/frontend/src/trang/VanPhong.vue
+++ b/frontend/src/trang/VanPhong.vue
@@ -1,34 +1,70 @@
 <script setup>
 import { TresCanvas } from '@tresjs/core'
-import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
-import { useRouter } from 'vue-router'
+import { NoToneMapping, PCFShadowMap, SRGBColorSpace } from 'three'
+import { computed, onMounted, onUnmounted, ref, shallowRef, watch } from 'vue'
 import { doc } from '../api.js'
 import { kho } from '../kho.js'
-import { boTriPhong, datNhanVat } from '../van_phong/bo_tri.js'
+import '../kieu/van-phong.css'
+import DauTrang from '../thanh/DauTrang.vue'
+import { boTriVanPhong } from '../van_phong/bo_tri.js'
 import CanhVanPhong from '../van_phong/CanhVanPhong.vue'
 import DanhSachVanPhong from '../van_phong/DanhSachVanPhong.vue'
-import { duongDanNhanVat, duongDanPhong } from '../van_phong/hien_thi.js'
+import LopNhan from '../van_phong/LopNhan.vue'
+import { dungNhan, timMucChon } from '../van_phong/nhan_canh.js'
+import PanelChon from '../van_phong/PanelChon.vue'
 
-// Văn phòng 3D (spec 2 §5.5). Trạng thái suy ở server (`/api/van-phong`); trang chỉ vẽ. Nhịp tim không phải sự
-// kiện → tải lại mỗi 5 giây như trang Đội ngũ AI (plan 2b G15), cộng SSE `doi_ngu_doi` / thay đổi bảng.
+// Văn phòng 3D (mockup trang-van-phong.js, D20). Trạng thái suy ở server (`/api/van-phong`); trang chỉ vẽ.
+// `/api/du-an` cho `bat_ghi` (D37). Nhịp tim không phải sự kiện → tải lại mỗi 5 giây (plan 2b G15) + SSE.
 const CHU_KY_MS = 5000
-const router = useRouter()
+const KHOA_GIAM = 'ben-station-giam-chuyen-dong'
+const MO_TA = 'Ai đang làm gì, nhìn cho vui mắt. Vị trí lấy từ trạng thái nhiệm vụ thật; bấm vào nhân vật để mở việc.'
 const dl = ref(null)
+const duAn = ref([])
 const loi = ref('')
-const giamChuyenDong = ref(Boolean(window.matchMedia?.('(prefers-reduced-motion: reduce)').matches))
+const boTri = shallowRef(null)
+const chieu = shallowRef(null)
+const chon = ref(null)
+const khung = ref(null)
+const giam = ref(docGiam())
 const coWebGL = (() => {
+  try { return Boolean(document.createElement('canvas').getContext('webgl2')) } catch { return false }
+})()                                                         // three bản ghim yêu cầu WebGL2
+const nhan = computed(() => (boTri.value ? dungNhan(boTri.value) : []))
+
+// "Giảm chuyển động": mặc định theo prefers-reduced-motion, nhớ lựa chọn trong localStorage (tiện ích riêng máy).
+function docGiam() {
   try {
-    const c = document.createElement('canvas')
-    return Boolean(c.getContext('webgl2'))  // three bản ghim yêu cầu WebGL2
-  } catch {
-    return false
+    const v = localStorage.getItem(KHOA_GIAM)
+    if (v !== null) return v === '1'
+  } catch { /* bỏ qua: chế độ riêng tư / bị chặn */ }
+  return Boolean(window.matchMedia?.('(prefers-reduced-motion: reduce)').matches)
+}
+watch(giam, (b) => {
+  try { localStorage.setItem(KHOA_GIAM, b ? '1' : '0') } catch { /* bỏ qua */ }
+})
+
+// Chỉ thay mặt bằng khi nội dung đổi → cảnh 3D không dựng lại mỗi 5 giây.
+let khoaCu = ''
+watch([dl, duAn], () => {
+  if (!dl.value) return
+  const b = boTriVanPhong(dl.value.phong, dl.value.nhan_vat, duAn.value)
+  const k = JSON.stringify(b)
+  if (k !== khoaCu) {
+    khoaCu = k
+    boTri.value = b
   }
-})()
-const phong = computed(() => boTriPhong(dl.value ? dl.value.phong : []))
-const nhanVat = computed(() => datNhanVat(phong.value, dl.value ? dl.value.nhan_vat : []))
+})
+
+// Panel lấy bản mới nhất của phòng / nhân vật đang chọn (D38/Q8: bấm mở panel trước).
+const panel = computed(() => timMucChon(boTri.value, chon.value))
+function chonTuDanhSach(c) {
+  chon.value = c
+  khung.value?.scrollIntoView({ behavior: giam.value ? 'auto' : 'smooth', block: 'center' })
+}
+
 let hen = null
 let luotTai = 0
-
+let luotDuAn = 0
 async function tai() {
   const luot = ++luotTai
   try {
@@ -40,33 +76,40 @@ async function tai() {
     if (luot === luotTai) loi.value = e.message
   }
 }
-onMounted(() => { tai(); hen = setInterval(tai, CHU_KY_MS) })
-onUnmounted(() => { clearInterval(hen); luotTai += 1 })
+async function taiDuAn() {
+  const luot = ++luotDuAn
+  try {
+    const r = await doc('/api/du-an')
+    if (luot === luotDuAn) duAn.value = r.du_an || []
+  } catch { /* không đọc được → coi mọi dự án bat_ghi = true */ }
+}
+onMounted(() => { tai(); taiDuAn(); hen = setInterval(tai, CHU_KY_MS) })
+onUnmounted(() => { clearInterval(hen); luotTai += 1; luotDuAn += 1 })
 watch(() => [kho.phienBan, kho.phienBanDoiNgu], tai)
-const di = (dich) => { if (dich) router.push(dich) }
+watch(() => kho.phienBan, taiDuAn)
 </script>
 
 <template>
-  <section class="van-phong">
-    <div class="cong-cu">
-      <h1>Văn phòng</h1>
-      <label class="chon-giam"><input v-model="giamChuyenDong" type="checkbox">Giảm chuyển động</label>
-    </div>
-    <p v-if="loi" class="loi" role="alert">{{ loi }}</p>
-    <p v-if="dl && !dl.kho_phieu" class="nho">Kho phiếu (phần 3) chưa bật — chưa có nhân vật.</p>
-    <div v-if="dl && coWebGL" class="khung-3d" aria-hidden="true">
-      <TresCanvas :key="giamChuyenDong ? 'tinh' : 'dong'" clear-color="#f6f5f2" :dpr="[1, 2]"
-                  :render-mode="giamChuyenDong ? 'on-demand' : 'always'">
-        <CanhVanPhong :phong="phong" :nhan-vat="nhanVat" :chuyen-dong="!giamChuyenDong"
-                      @bam-phong="(p) => di(duongDanPhong(p))" @bam-nhan-vat="(n) => di(duongDanNhanVat(n))" />
-      </TresCanvas>
-    </div>
-    <p v-else-if="dl" class="nho">Trình duyệt không bật WebGL — chỉ xem được dạng danh sách.</p>
-    <DanhSachVanPhong v-if="dl" :phong="dl.phong" :nhan-vat="dl.nhan_vat" />
-  </section>
+  <DauTrang tieu-de="Văn phòng" :mo-ta="MO_TA">
+    <template #cong-cu>
+      <label class="gc"><input v-model="giam" type="checkbox"> Giảm chuyển động</label>
+    </template>
+  </DauTrang>
+  <p v-if="loi" class="loi" role="alert">{{ loi }}</p>
+  <p v-if="dl && !dl.kho_phieu" class="nho">Kho phiếu (phần 3) chưa bật — chưa có nhân vật.</p>
+  <div v-if="boTri" ref="khung" class="canh-khung">
+    <TresCanvas v-if="coWebGL" :key="giam ? 'tinh' : 'dong'" aria-hidden="true" :alpha="true" :clear-alpha="0"
+                :tone-mapping="NoToneMapping" :shadows="true" :shadow-map-type="PCFShadowMap"
+                :output-color-space="SRGBColorSpace" :dpr="[1, 2]" :render-mode="giam ? 'on-demand' : 'always'">
+      <CanhVanPhong :bo-tri="boTri" :nhan="nhan" :chuyen-dong="!giam" @chon="(c) => (chon = c)"
+                    @chieu="(c) => (chieu = c)" />
+    </TresCanvas>
+    <div v-else class="loi-webgl">Trình duyệt không bật được WebGL — xem bản danh sách bên dưới.</div>
+    <LopNhan v-if="coWebGL" :nhan="nhan" :chieu="chieu" @chon="(c) => (chon = c)" />
+    <PanelChon v-if="panel" :key="panel.khoa" :nv="panel.nv" :phong="panel.phong" @dong="chon = null" />
+  </div>
+  <template v-if="boTri">
+    <h2 class="muc">Bản danh sách <span class="so">{{ boTri.phong.length }} phòng</span></h2>
+    <DanhSachVanPhong :bo-tri="boTri" @chon="chonTuDanhSach" />
+  </template>
 </template>
-
-<style scoped>
-.khung-3d { height: min(70vh, 40rem); border: 1px solid var(--vien); border-radius: 8px; overflow: hidden; }
-.chon-giam { display: flex; align-items: center; min-width: auto; }
-</style>
```

`frontend/src/van_phong/CanhVanPhong.vue` (sửa):

```diff
diff --git a/frontend/src/van_phong/CanhVanPhong.vue b/frontend/src/van_phong/CanhVanPhong.vue
index 0f5de11..762eeb5 100644
--- a/frontend/src/van_phong/CanhVanPhong.vue
+++ b/frontend/src/van_phong/CanhVanPhong.vue
@@ -1,29 +1,77 @@
 <script setup>
-import { useTres } from '@tresjs/core'
-import { computed } from 'vue'
-import { khungNhin } from './bo_tri.js'
-import NhanVat3D from './NhanVat3D.vue'
-import Phong3D from './Phong3D.vue'
+import { useLoop, useTres } from '@tresjs/core'
+import { nextTick, onUnmounted, shallowRef, watch } from 'vue'
+import { dungCanh, huyCanh, taoAnhSang } from './dung_canh.js'
+import { chieuNhan, gocSan, khit } from './khung_nhin.js'
+import { chuyenDongNv } from './nhan_vat_3d.js'
 
-// Nội dung bên trong <TresCanvas>: camera trực giao góc isometric (nhìn từ +x +y +z về gốc), ánh sáng, phòng,
-// nhân vật. Camera đặt ở component con để đọc được kích thước canvas (useTres chỉ chạy dưới TresCanvas).
+// Nội dung dưới <TresCanvas> (mockup van-phong.js dungVanPhong, D20): camera trực giao ở (40, 40, 40) nhìn gốc,
+// ánh sáng + phòng + đồ đạc + nhân vật dựng bằng three thuần gắn qua <primitive>. Bấm → emit('chon', chon);
+// toạ độ 2D các điểm neo nhãn tính khi đổi cỡ / đổi dữ liệu (không mỗi khung hình) → emit('chieu').
 const props = defineProps({
-  phong: { type: Array, required: true },
-  nhanVat: { type: Array, required: true },
+  boTri: { type: Object, required: true },
+  nhan: { type: Array, required: true },
   chuyenDong: { type: Boolean, default: true },
 })
-const emit = defineEmits(['bam-phong', 'bam-nhan-vat'])
-const { sizes } = useTres()
-const v = computed(() => khungNhin(props.phong))
-const a = computed(() => sizes.aspectRatio.value || 1)
+const emit = defineEmits(['chon', 'chieu'])
+const { sizes, invalidate, renderer } = useTres()
+const cam = shallowRef(null)
+const anhSang = taoAnhSang()
+const canh = shallowRef(null)
+let dong = []
+
+// Dựng lại khi mặt bằng đổi (trang chỉ thay boTri khi nội dung khác); huỷ cảnh cũ sau khi Tres đã gỡ nó.
+function dung() {
+  const cu = canh.value
+  const moi = dungCanh(props.boTri)
+  dong = moi.dong
+  canh.value = moi.goc
+  if (cu) nextTick(() => huyCanh(cu))
+  invalidate()
+}
+dung()
+watch(() => props.boTri, dung)
+
+// Khít khung SAU khi camera đã có position + lookAt (prop :look-at bắt buộc — bài học 2c T8); khit() tự gọi
+// updateMatrixWorld(). Rồi chiếu điểm neo nhãn ra toạ độ khung.
+function capNhatKhung() {
+  const c = cam.value
+  const w = sizes.width.value
+  const h = sizes.height.value
+  if (!c || !w || !h) return
+  Object.assign(c, khit(c, gocSan(props.boTri.phong), w, h))
+  c.updateProjectionMatrix()
+  emit('chieu', chieuNhan(c, w, h, props.nhan, props.boTri.nhanVat))
+  invalidate()
+}
+watch([cam, sizes.width, sizes.height, () => props.nhan], capNhatKhung, { immediate: true })
+
+useLoop().onBeforeRender(({ elapsed }) => {
+  if (props.chuyenDong) for (const m of dong) chuyenDongNv(m, elapsed)
+})
+
+// Sự kiện con trỏ của Tres nổi bọt lên primitive; đi ngược parent từ vật trúng tia để tìm userData.chon.
+function timChon(o) {
+  let x = o
+  while (x && !x.userData?.chon) x = x.parent
+  return x ? x.userData.chon : null
+}
+function bam(e) {
+  const c = timChon(e.object ?? e.intersection?.object)
+  if (c) emit('chon', c)
+}
+function troChuot(bat) {
+  if (renderer?.domElement) renderer.domElement.style.cursor = bat ? 'pointer' : ''
+}
+
+onUnmounted(() => {
+  huyCanh(canh.value)
+  huyCanh(anhSang)
+})
 </script>
 
 <template>
-  <TresOrthographicCamera :position="[40, 40, 40]" :look-at="[0, 0, 0]" :left="-v * a" :right="v * a" :top="v"
-                          :bottom="-v" :near="0.1" :far="200" />
-  <TresAmbientLight :intensity="1.4" />
-  <TresDirectionalLight :position="[10, 25, 15]" :intensity="1.6" />
-  <Phong3D v-for="p in phong" :key="p.ma" :phong="p" @bam="(x) => emit('bam-phong', x)" />
-  <NhanVat3D v-for="n in nhanVat" :key="n.khe_id" :nv="n" :chuyen-dong="chuyenDong"
-             @bam="(x) => emit('bam-nhan-vat', x)" />
+  <TresOrthographicCamera ref="cam" :position="[40, 40, 40]" :look-at="[0, 0, 0]" :near="0.1" :far="400" />
+  <primitive :object="anhSang" />
+  <primitive :object="canh" @click="bam" @pointerenter="troChuot(true)" @pointerleave="troChuot(false)" />
 </template>
```

`frontend/src/van_phong/DanhSachVanPhong.vue` (sửa):

```diff
diff --git a/frontend/src/van_phong/DanhSachVanPhong.vue b/frontend/src/van_phong/DanhSachVanPhong.vue
index 32c333e..b77518b 100644
--- a/frontend/src/van_phong/DanhSachVanPhong.vue
+++ b/frontend/src/van_phong/DanhSachVanPhong.vue
@@ -1,45 +1,52 @@
 <script setup>
 import { computed } from 'vue'
-import { TEN_HIEN_THI, chuBien, chuBongBong, duongDanNhanVat, duongDanPhong } from './hien_thi.js'
+import { mauTuMay } from './bo_tri.js'
+import { chuNhip } from './hien_thi.js'
+import { lopNhanVat, nhanPhu, trangThaiDen } from './nhan_canh.js'
+
+// Bản danh sách (mockup trang-van-phong.js "ds-phong"): thẻ phòng viền trái màu tường, chip trạng thái, chip nhân
+// vật. Đường dùng bàn phím / trình đọc màn hình và chỗ xem khi không có WebGL (plan 2c G16). Bấm thẻ → emit('chon').
+const props = defineProps({ boTri: { type: Object, required: true } })
+const emit = defineEmits(['chon'])
+const LOAI = { du_an: 'Dự án', giam_doc: 'Cố định', may_chu: 'Máy B', ca_phe: 'Khe rảnh', dieu_phoi: 'Máy A' }
+const CHIP_TU = { xanh: ['tt-lam', 'xanh'], vang: ['tt-cau_dao', 'vàng'], do: ['tt-loi', 'đỏ'] }
 
-// Văn phòng dạng danh sách: đường dùng bàn phím / trình đọc màn hình, và chỗ xem khi không có WebGL (plan 2c G16).
-const props = defineProps({ phong: { type: Array, required: true }, nhanVat: { type: Array, required: true } })
-const TEN_SUC_KHOE = { xanh: 'Trạm ổn', vang: 'Cần để ý', do: 'Trạm lỗi' }
-const LOP_SUC_KHOE = { xanh: 'nho', vang: 'canh-bao', do: 'loi' }
 const theoPhong = computed(() => {
-  const co = new Set(props.phong.map((p) => p.ma))
   const m = {}
-  for (const n of props.nhanVat) (m[co.has(n.phong) ? n.phong : 'ca-phe'] ??= []).push(n)
+  for (const nv of props.boTri.nhanVat) (m[nv.phongMa] ??= []).push(nv)
   return m
 })
+
+// Chip trạng thái riêng của phòng: việc chờ / đèn Điều phối + nhịp cuối / số tủ theo màu / chỉ quét thử (D37).
+function chipPhong(p) {
+  if (p.loai === 'giam_doc') return [{ lop: 'tt-can_nguoi', chu: `${p.so_cho ?? 0} việc chờ` }]
+  if (p.loai === 'dieu_phoi') {
+    return [{ lop: '', chu: `đèn: ${trangThaiDen(p)}` }, ...(chuNhip(p) ? [{ lop: '', chu: chuNhip(p) }] : [])]
+  }
+  if (p.loai === 'may_chu') {
+    const dem = {}
+    for (const m of mauTuMay(p)) dem[m] = (dem[m] ?? 0) + 1
+    const co = Object.keys(CHIP_TU).filter((k) => dem[k])
+    return co.map((k) => ({ lop: CHIP_TU[k][0], chu: `${dem[k]} ${CHIP_TU[k][1]}` }))
+  }
+  return p.mo ? [{ lop: '', chu: 'chỉ quét thử' }] : []
+}
 </script>
 
 <template>
-  <section class="ds-van-phong" aria-label="Văn phòng dạng danh sách">
-    <h2>Các phòng</h2>
-    <div class="luoi-phong">
-      <article v-for="p in phong" :key="p.ma" class="muc">
-        <h3>
-          <router-link v-if="duongDanPhong(p)" :to="duongDanPhong(p)">{{ chuBien(p) }}</router-link>
-          <template v-else>{{ chuBien(p) }}</template>
-        </h3>
-        <template v-if="p.suc_khoe">
-          <p :class="LOP_SUC_KHOE[p.suc_khoe.mau]">{{ TEN_SUC_KHOE[p.suc_khoe.mau] }}</p>
-          <ul v-if="p.suc_khoe.ly_do.length" class="nho"><li v-for="(l, i) in p.suc_khoe.ly_do" :key="i">{{ l }}</li></ul>
-        </template>
-        <ul v-if="theoPhong[p.ma]">
-          <li v-for="n in theoPhong[p.ma]" :key="n.khe_id">
-            <router-link :to="duongDanNhanVat(n)">{{ n.ten }}</router-link> — {{ TEN_HIEN_THI[n.hien_thi] }}
-            <span v-if="chuBongBong(n)" class="nho"> · {{ chuBongBong(n) }}</span>
-          </li>
-        </ul>
-        <p v-else class="nho">Không có ai.</p>
-      </article>
-    </div>
-  </section>
+  <div class="ds-phong">
+    <button v-for="p in boTri.phong" :key="p.ma" type="button" class="the the-phong" :class="{ mo: p.mo }"
+            :style="{ borderLeftColor: p.tuong }" @click="emit('chon', { loai: 'phong', ma: p.ma })">
+      <span class="dau">
+        <span class="cham" :style="{ background: p.san, boxShadow: `inset 0 0 0 1px ${p.tuong}` }" />
+        <strong>{{ p.tenBien }}</strong><span class="nho">{{ LOAI[p.loai] }}</span>
+      </span>
+      <span class="ds-nv">
+        <span v-for="(c, i) in chipPhong(p)" :key="i" class="chip" :class="c.lop">{{ c.chu }}</span>
+        <span v-for="nv in theoPhong[p.ma] ?? []" :key="nv.khe_id"
+              :class="['chip', lopNhanVat(nv)]">{{ nv.ten }} · {{ nhanPhu(nv) }}</span>
+        <span v-if="!chipPhong(p).length && !theoPhong[p.ma]" class="nho">Không có ai</span>
+      </span>
+    </button>
+  </div>
 </template>
-
-<style scoped>
-.luoi-phong { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(16rem, 100%), 1fr)); gap: .75rem; }
-.luoi-phong h3 { margin-top: 0; }
-</style>
```

`frontend/src/van_phong/LopNhan.vue` (mới):

```vue
<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, shallowRef, watch } from 'vue'
import { coChu } from './khung_nhin.js'
import { xepNhan } from './nhan_canh.js'

// Lớp nhãn HTML phủ lên canvas (mockup van-phong.js "lop-phu", D20): biển phòng, tên + nhãn phụ, bong bóng việc,
// huy hiệu đỏ, huy hiệu Giám đốc, đường chỉ. Nhãn là <button> thật (thêm một đường dùng bàn phím). Vị trí đặt qua
// :style transform (CSSOM, hợp CSP); đo cỡ sau nextTick và sau document.fonts.ready rồi chạy boTriNhan.
const props = defineProps({
  nhan: { type: Array, required: true },
  chieu: { type: Object, default: null },                // chieuNhan(): { W, H, diem, than }
})
const emit = defineEmits(['chon'])
const lop = ref(null)
const kq = shallowRef({ viTri: {}, duong: [] })
const coPx = computed(() => (props.chieu ? coChu(props.chieu.W) : 16))
const LOP = { bien: 'bien-phong', ten: 'ten-nv', bb: 'bong-bong', hh: 'huy-hieu-do', gd: 'huy-hieu-do lon' }
let conSong = true

async function xep() {
  await nextTick()
  if (!conSong || !props.chieu || !lop.value) return
  const co = {}
  for (const el of lop.value.querySelectorAll('[data-id]')) {
    co[el.dataset.id] = { w: el.offsetWidth, h: el.offsetHeight }
  }
  kq.value = xepNhan(props.nhan, props.chieu, co)
}
watch(() => [props.nhan, props.chieu], xep, { immediate: true })
onMounted(() => document.fonts?.ready.then(xep))
onUnmounted(() => { conSong = false })

const lopNhan = (n) => [LOP[n.loai], { mo: n.mo, chua: !kq.value.viTri[n.id] }]
function kieu(n) {
  const v = kq.value.viTri[n.id]
  return v ? { transform: `translate(${v.x}px, ${v.y}px)` } : null
}
</script>

<template>
  <div ref="lop" class="lop-phu" :style="{ fontSize: coPx + 'px' }">
    <svg class="duong-chi" aria-hidden="true">
      <template v-for="(d, i) in kq.duong" :key="i">
        <line :x1="d[0]" :y1="d[1]" :x2="d[2]" :y2="d[3]" />
        <circle :cx="d[0]" :cy="d[1]" r="2.5" />
      </template>
    </svg>
    <button v-for="n in nhan" :key="n.id" type="button" :data-id="n.id" :class="lopNhan(n)" :style="kieu(n)"
            :aria-label="n.nhanDoc" :title="n.loai === 'hh' ? 'Cần Đại ca trả lời' : null"
            @click="emit('chon', n.chon)">
      <template v-if="n.loai === 'bien'">
        {{ n.chu }}<template v-if="n.den"><span class="den" :class="{ sang: n.den.sang }" />
          <small>{{ n.den.chu }}</small></template>
      </template>
      <template v-else-if="n.loai === 'ten'">{{ n.chu }}<small>{{ n.phu }}</small></template>
      <template v-else-if="n.loai === 'bb'"><b>{{ n.ma }}</b>{{ n.chu }}</template>
      <template v-else-if="n.loai === 'gd'">{{ n.chu }}<span class="phu">việc chờ</span></template>
      <template v-else>{{ n.chu }}</template>
    </button>
  </div>
</template>
```

`frontend/src/van_phong/PanelChon.vue` (mới):

```vue
<script setup>
import { computed, onMounted, ref } from 'vue'
import { CHU_CHI_QUET_THU } from '../luat.js'
import { mauTuMay } from './bo_tri.js'
import { chuNhip, duongDanNhanVat, duongDanPhong } from './hien_thi.js'
import { lopNhanVat, nhanPhu, trangThaiDen } from './nhan_canh.js'

// Panel khi bấm nhân vật / phòng (mockup trang-van-phong.js noiDungPanel). D38/Q8: bấm mở panel trước, nút trong
// panel mới dẫn đi (duongDanNhanVat / duongDanPhong). Panel Điều phối không có nút — chỉ trạng thái đèn + nhịp cuối.
const props = defineProps({ nv: { type: Object, default: null }, phong: { type: Object, default: null } })
const emit = defineEmits(['dong'])
const TEN_BUOC = { spec: 'spec', code: 'code', qc: 'QC' }
const NUT = { du_an: 'Lọc Công việc', giam_doc: 'Mở Phê duyệt', may_chu: 'Mở Phê duyệt', ca_phe: 'Mở Đội ngũ AI' }
const TEN_MAU = { xanh: 'xanh', vang: 'vàng', do: 'đỏ' }
const nutDong = ref(null)
onMounted(() => nutDong.value?.focus({ preventScroll: true }))

const p = computed(() => props.phong)
const moTaKhe = computed(() => {
  const nv = props.nv
  if (nv.trang_thai === 'mat_ket_noi') return 'Không thấy nhịp tim từ máy B.'
  if (nv.hien_thi === 'loi') return nv.cau_dao_ngat ? 'Cầu dao ngắt — lý do và giờ tự đóng xem ở Đội ngũ AI.'
    : 'Khe đang báo lỗi.'
  if (nv.hien_thi === 'tat') return 'Khe đang tắt.'
  return nv.hien_thi === 'ranh' ? 'Đang rảnh, chờ việc ở Góc cà phê.' : 'Không giữ việc.'
})
// Phòng máy chủ: đếm tủ theo màu `suc_khoe.muc` (T6), vd "3 tủ xanh, 1 tủ vàng".
const demTu = computed(() => {
  const dem = {}
  for (const m of mauTuMay(p.value)) dem[m] = (dem[m] ?? 0) + 1
  return Object.keys(TEN_MAU).filter((k) => dem[k]).map((k) => `${dem[k]} tủ ${TEN_MAU[k]}`).join(', ')
})
</script>

<template>
  <section class="vp-panel" :aria-label="nv ? nv.ten : phong.tenBien">
    <button ref="nutDong" class="dong" type="button" aria-label="Đóng" @click="emit('dong')">×</button>
    <template v-if="nv">
      <h3>{{ nv.ten }} <span class="chip" :class="lopNhanVat(nv)">{{ nhanPhu(nv) }}</span></h3>
      <template v-if="nv.bead">
        <p>Đang giữ <b class="mono">{{ nv.bead.bead_id }}</b> · {{ nv.bead.tieu_de }} ·
          bước {{ TEN_BUOC[nv.bead.buoc] ?? nv.bead.buoc }}.</p>
        <p class="nho">Mở bead <b>{{ nv.bead.bead_id }}</b> ở ngăn bên trang Công việc
          (lọc dự án {{ nv.bead.du_an }}).</p>
        <div class="hang-nut">
          <router-link class="nut chinh" :to="duongDanNhanVat(nv)">Mở bead {{ nv.bead.bead_id }}</router-link>
        </div>
      </template>
      <template v-else>
        <p>{{ moTaKhe }}</p>
        <p class="nho">Không giữ việc → mở thẻ khe ở trang Đội ngũ AI.</p>
        <div class="hang-nut"><router-link class="nut chinh" :to="duongDanNhanVat(nv)">Mở Đội ngũ AI</router-link></div>
      </template>
    </template>
    <template v-else>
      <h3>{{ p.tenBien }}</h3>
      <p v-if="p.loai === 'du_an'">Lọc trang Công việc theo dự án <b>{{ p.du_an }}</b>.</p>
      <p v-if="p.loai === 'du_an' && p.mo" class="nho">{{ CHU_CHI_QUET_THU }}</p>
      <p v-if="p.loai === 'giam_doc'">{{ p.so_cho ?? 0 }} việc chờ Đại ca — mở trang Phê duyệt.</p>
      <template v-if="p.loai === 'may_chu'">
        <p>Máy B: {{ demTu }}.</p>
        <ul v-if="p.suc_khoe?.ly_do?.length" class="nho">
          <li v-for="(l, i) in p.suc_khoe.ly_do" :key="i">{{ l }}</li>
        </ul>
      </template>
      <p v-if="p.loai === 'ca_phe'">Khe rảnh và khe không giữ việc đứng/ngồi ở đây — mở Đội ngũ AI.</p>
      <template v-if="p.loai === 'dieu_phoi'">
        <p>Đèn Điều phối: {{ trangThaiDen(p) }}<template v-if="p.sang == null"> (máy A chưa có nguồn báo
          phiên)</template>. Không có trang đích.</p>
        <p v-if="chuNhip(p)" class="nho">{{ chuNhip(p) }}</p>
      </template>
      <div v-if="duongDanPhong(p)" class="hang-nut">
        <router-link class="nut chinh" :to="duongDanPhong(p)">{{ NUT[p.loai] }}</router-link>
      </div>
    </template>
  </section>
</template>
```

`frontend/src/van_phong/bo_tri.js` (sửa):

```diff
diff --git a/frontend/src/van_phong/bo_tri.js b/frontend/src/van_phong/bo_tri.js
index c27e8ab..9e1bcf3 100644
--- a/frontend/src/van_phong/bo_tri.js
+++ b/frontend/src/van_phong/bo_tri.js
@@ -1,47 +1,74 @@
-// Bố trí Văn phòng 3D (spec 2 §5.5) — hàm thuần, test bằng node --test. Đơn vị: mét của cảnh three.js;
-// mặt sàn là mặt phẳng XZ, trục Y hướng lên. Phòng xếp lưới quanh gốc toạ độ (camera nhìn vào gốc).
-export const CANH = { phong: 6, buoc: 8, cho: 1.8, cotCho: 3 }
+// Bố trí Văn phòng 3D theo mockup van-phong.js PHONG (D20; hơn 3 dự án thêm hàng sau — D38/Q9) — hàm thuần,
+// test bằng node --test. Mặt sàn là mặt phẳng XZ, trục Y hướng lên; lưới ô O = 10 m, gốc ở giữa ô Điều phối.
+// Camera nhìn từ (40, 40, 40): +x xuống phải màn hình, +z xuống trái.
+import { datNhanVat } from './cho_nv.js'
+import { catChu } from './hien_thi.js'
 
-export function boTriPhong(phong) {
-  const n = phong.length
-  if (!n) return []
-  const cot = Math.max(2, Math.ceil(Math.sqrt(n)))
-  const hang = Math.ceil(n / cot)
-  return phong.map((p, i) => ({
-    ...p,
-    x: ((i % cot) - (cot - 1) / 2) * CANH.buoc,
-    z: (Math.floor(i / cot) - (hang - 1) / 2) * CANH.buoc,
-  }))
+export const O = 10
+// Phòng cố định: ô, màu sàn/tường, chữ biển, neo biển (tương đối tâm ô đầu) — đúng số của mockup PHONG.
+const CO_DINH = {
+  giam_doc: { o: [[-1, -1]], san: '#f8e6d4', tuong: '#e8c6a8', ten: 'Phòng Giám đốc', nhan: [-1.6, -2.6] },
+  dieu_phoi: { o: [[0, 0]], san: '#f7eee3', tuong: '#e1cfba', ten: 'Điều phối', nhan: [1.8, -3.6] },
+  may_chu: { o: [[1, 0]], san: '#dce5ea', tuong: '#b2c2cc', ten: 'Phòng máy chủ', nhan: [3.8, -4] },
+  ca_phe: { o: [[-1, 1], [0, 1]], san: '#f0e4d4', tuong: '#d9c2a6', ten: 'Góc cà phê', nhan: [4.6, 4] },
 }
+// Phòng dự án xoay vòng màu hr-codex / tram; dự án chỉ quét thử (bat_ghi false, D37) mờ xám như ke-toan.
+const MAU_DU_AN = [{ san: '#f5d6d3', tuong: '#e3a7a2' }, { san: '#fbdcc8', tuong: '#efb796' }]
+const MAU_MO = { san: '#ebe5de', tuong: '#d4cac0' }
+const NEO_DU_AN = [[0.8, 3.9], [-1.5, 0.5], [-2.5, -3]]          // biển hr-codex, tram, ke-toan
+const MAU_TU = new Set(['xanh', 'vang', 'do'])
+const tron = (v) => Math.round(v * 100) / 100
 
-// Chỗ thứ i trong phòng: 3 bàn một hàng, hàng đầu sát tường sau.
-export function viTriCho(i) {
-  return [((i % CANH.cotCho) - 1) * CANH.cho, Math.floor(i / CANH.cotCho) * CANH.cho - CANH.cho]
+// Ô thứ i của phòng dự án: ba ô trống của lưới 3×3 trước, rồi từng hàng 3 ô phía sau (z = -2, -3, …).
+export function oDuAn(i) {
+  if (i < 3) return [[-1, 0], [0, -1], [1, -1]][i]
+  return [((i - 3) % 3) - 1, -2 - Math.floor((i - 3) / 3)]
 }
 
-// Nhân vật có `phong` không có trong danh sách (dự án vừa gỡ) về Góc cà phê; trong phòng xếp theo khe_id.
-export function datNhanVat(phongDaBoTri, nhanVat) {
-  const theoMa = new Map(phongDaBoTri.map((p) => [p.ma, p]))
-  const nhom = new Map()
-  for (const nv of [...nhanVat].sort((a, b) => a.khe_id.localeCompare(b.khe_id))) {
-    const ma = theoMa.has(nv.phong) ? nv.phong : 'ca-phe'
-    if (!nhom.has(ma)) nhom.set(ma, [])
-    nhom.get(ma).push(nv)
+function khoang(o) {
+  const xs = o.map(([x]) => x)
+  const zs = o.map(([, z]) => z)
+  return {
+    x: [Math.min(...xs) * O - O / 2, Math.max(...xs) * O + O / 2],
+    z: [Math.min(...zs) * O - O / 2, Math.max(...zs) * O + O / 2],
   }
+}
+
+function moTaPhong(p, k, chiQuet) {
+  if (p.loai !== 'du_an') return { ...CO_DINH[p.loai], mo: false }
+  const mo = chiQuet.has(p.du_an)
+  const ten = catChu(p.ten ?? p.du_an ?? p.ma, 28)
+  return { o: [oDuAn(k)], ...(mo ? MAU_MO : MAU_DU_AN[k % 2]), ten: mo ? `${ten} (chỉ quét thử)` : ten,
+    nhan: NEO_DU_AN[k] ?? NEO_DU_AN[1], mo }
+}
+
+// `duAn` từ /api/du-an: thiếu `bat_ghi` coi như true. Loại phòng lạ hoặc phòng cố định lặp thì bỏ.
+export function boTriPhong(phong, duAn = []) {
+  const chiQuet = new Set((duAn || []).filter((d) => d?.bat_ghi === false).map((d) => d.ten))
+  const daCo = new Set()
   const ra = []
-  for (const [ma, ds] of nhom) {
-    const p = theoMa.get(ma)
-    if (!p) continue
-    ds.forEach((nv, i) => {
-      const [dx, dz] = viTriCho(i)
-      ra.push({ ...nv, x: p.x + dx, z: p.z + dz })
-    })
+  let k = 0
+  for (const p of phong || []) {
+    if (p.loai !== 'du_an' && (!CO_DINH[p.loai] || daCo.has(p.loai))) continue
+    daCo.add(p.loai)
+    const c = moTaPhong(p, p.loai === 'du_an' ? k++ : 0, chiQuet)
+    const tam = [c.o[0][0] * O, c.o[0][1] * O]
+    ra.push({ ...p, o: c.o, ...khoang(c.o), tam, san: c.san, tuong: c.tuong, tenBien: c.ten, mo: c.mo,
+      nhan: [tron(tam[0] + c.nhan[0]), tron(tam[1] + c.nhan[1])] })
   }
   return ra
 }
 
-// Nửa chiều cao khung nhìn của camera trực giao: đủ chứa phòng xa nhất (cộng lề 1 m), tối thiểu 8.
-export function khungNhin(phongDaBoTri) {
-  const xa = phongDaBoTri.reduce((m, p) => Math.max(m, Math.abs(p.x), Math.abs(p.z)), 0)
-  return Math.max(8, xa + CANH.phong / 2 + 1)
+// Tủ thứ i của Phòng máy chủ lấy màu `suc_khoe.muc[i].mau` (T6, D38/Q10); thiếu → xanh.
+export function mauTuMay(p) {
+  return [0, 1, 2, 3].map((i) => {
+    const m = p?.suc_khoe?.muc?.[i]?.mau
+    return MAU_TU.has(m) ? m : 'xanh'
+  })
+}
+
+// Toàn bộ mặt bằng: phòng, nhân vật (x, z, ngoi, phongMa), bàn làm việc (x, z, man, khe?).
+export function boTriVanPhong(phong, nhanVat, duAn) {
+  const ds = boTriPhong(phong, duAn)
+  return { phong: ds, ...datNhanVat(ds, nhanVat || []) }
 }
```

`frontend/src/van_phong/bo_tri_nhan.js` (mới):

```js
// Tránh va chạm cho nhãn HTML phủ trên cảnh Văn phòng — port nguyên thuật toán mockup bo-tri-nhan.js (D20, D33).
// Hàm thuần, chạy khi đổi cỡ khung hoặc đổi dữ liệu (không chạy mỗi khung hình).
// Mỗi nhãn: { loai, w, h, x0, y0 (vị trí mong muốn, góc trên-trái), diemNeo: {x, y} (điểm gốc trên màn hình), khe? }.
// Thứ tự đặt (ưu tiên giữ chỗ): bong bóng → huy hiệu → tên nhân vật → huy hiệu Giám đốc → biển phòng.
// Vật cản thêm: hình chữ nhật thân nhân vật (biển phòng tránh mọi nhân vật; nhãn của một khe tránh thân khe khác).

const UU_TIEN = { bb: 0, hh: 1, ten: 2, gd: 3, bien: 4 }
const DEM = 4                                  // khoảng hở tối thiểu giữa hai nhãn (px)

function day(tu, den, buoc) {
  const r = []
  for (let v = tu; v <= den; v += buoc) r.push(v)
  return r
}
const MIEN = {
  bb: { dy: day(-140, 0, 4), dx: day(-120, 120, 8), wx: 1.6, wy: 1 },
  hh: { dy: day(-30, 30, 4), dx: day(-10, 40, 5), wx: 1, wy: 1 },
  ten: { dy: day(-30, 60, 3), dx: day(-48, 48, 6), wx: 1.4, wy: 1 },
  gd: { dy: day(-90, 90, 4), dx: day(-120, 120, 8), wx: 1, wy: 1 },
  bien: { dy: day(-170, 170, 4), dx: day(-200, 200, 8), wx: 1, wy: 1 },
}
// Ứng viên dời (dx, dy) sắp theo giá tăng dần — tính một lần cho mỗi loại.
const UNG = Object.fromEntries(Object.entries(MIEN).map(([loai, m]) => {
  const ung = []
  for (const dy of m.dy) for (const dx of m.dx) ung.push([Math.abs(dx) * m.wx + Math.abs(dy) * m.wy, dx, dy])
  return [loai, ung.sort((a, b) => a[0] - b[0])]
}))

const giao = (a, b) => Math.max(0, Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x)) *
  Math.max(0, Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y))

// Ghi n.x, n.y vào từng nhãn; trả danh sách đường chỉ [x1, y1, x2, y2] (từ điểm neo tới mép nhãn bị dời xa).
export function boTriNhan(nhan, thanNv, W, H) {
  const daDat = []
  const duongChi = []
  const thuTu = [...nhan].sort((a, b) => UU_TIEN[a.loai] - UU_TIEN[b.loai])
  for (const n of thuTu) {
    const vatCan = [...daDat]
    for (const t of thanNv) if (n.loai === 'bien' || n.loai === 'gd' || t.khe !== n.khe) vatCan.push(t)
    let tot = null
    let totPhat = Infinity
    for (const [gia, dx, dy] of UNG[n.loai]) {
      const x = Math.min(Math.max(n.x0 + dx, 2), W - n.w - 2)
      const y = Math.min(Math.max(n.y0 + dy, 2), H - n.h - 2)
      const r = { x: x - DEM / 2, y: y - DEM / 2, w: n.w + DEM, h: n.h + DEM }
      let chong = 0
      for (const v of vatCan) chong += giao(r, v)
      if (chong === 0) {
        tot = [x, y]
        break
      }
      const phat = chong * 50 + gia
      if (phat < totPhat) {
        totPhat = phat
        tot = [x, y]
      }
    }
    ;[n.x, n.y] = tot
    daDat.push({ x: n.x - DEM / 2, y: n.y - DEM / 2, w: n.w + DEM, h: n.h + DEM })
    // đường chỉ mảnh khi nhãn bị dời xa chỗ mong muốn
    if (Math.hypot(n.x - n.x0, n.y - n.y0) > 10 && n.diemNeo) {
      const neo = n.diemNeo
      const cx = Math.min(Math.max(neo.x, n.x + 6), n.x + n.w - 6)
      const cy = Math.min(Math.max(neo.y, n.y), n.y + n.h)
      if (Math.hypot(cx - neo.x, cy - neo.y) > 6) duongChi.push([neo.x, neo.y, cx, cy])
    }
  }
  return duongChi
}

// Số cặp nhãn chồng nhau sau khi bố trí (mockup ghi vào data-chong để kiểm).
export function demChong(nhan) {
  let so = 0
  for (let i = 0; i < nhan.length; i++) {
    for (let j = i + 1; j < nhan.length; j++) if (giao(nhan[i], nhan[j]) > 0) so++
  }
  return so
}
```

`frontend/src/van_phong/cho_nv.js` (mới):

```js
// Chỗ đứng/ngồi của nhân vật (mockup van-phong.js CHO + bàn của khe, D20) — hàm thuần. Phòng lấy từ
// `nhan_vat[].phong` của API (2c G7: server suy, trang không tự suy lại); phòng lạ hoặc đã gỡ → Góc cà phê.
// Toạ độ chỗ tương đối tâm ô đầu của phòng (bo_tri.js `tam`).
export const TRUOC_BAN = 1.4                                       // đứng/ngồi trước bàn (claude-1, codex-1, claude-4)
export const BAN_DU_AN = [[-3.5, -0.8], [2.5, 0.2], [0.4, -3.4]]   // ba bàn phòng hr-codex
export const CAY_DU_AN = [-4.2, 4.2]
// Góc cà phê (tâm ô (-1, 1)): chỗ đứng cho khe rảnh gần quầy, chỗ ngồi cho khe tắt/khác, bàn của khe lỗi.
const CA_PHE = {
  dung: [[-3, -1.4], [-0.8, -1.8], [1.4, -1.4]],
  ngoi: [[3, 0], [8.4, 0], [5.7, 2.2]],
  loi: [[13.5, -1.4], [10.4, -3]],
}
// Vật cản Góc cà phê [x, z, nửa rộng, nửa sâu]: quầy, bàn tròn, hai chậu cây (dung_do_vat.js cùng số).
const VAT_CA_PHE = [[-1.6, 2.6, 3, 0.65], [5.7, -1.6, 1, 1], [-4.2, -3.8, 0.4, 0.4], [14.2, 4.2, 0.4, 0.4]]
const BUOC = 2.2

const ngoi = (nv) => nv.hien_thi === 'loi' || nv.hien_thi === 'tat'
const manCua = (nv) => (nv.hien_thi === 'loi' ? 'do' : nv.hien_thi === 'tat' ? 'tat' : 'sang')

// Ô trống kế tiếp theo lưới trong phòng (khi hết chỗ định sẵn); `canBan`: chừa chỗ bàn phía sau.
function oTrong(p, dung, vat, canBan) {
  const tu = (a, b) => dung.every(([u, v]) => Math.hypot(u - a, v - b) >= 1.6) &&
    vat.every(([u, v, w, d]) => Math.abs(u - a) > w + 0.7 || Math.abs(v - b) > d + 0.7)
  for (let z = p.z[0] + 1.6; z <= p.z[1] - 1.2; z += BUOC) {
    for (let x = p.x[0] + 1.6; x <= p.x[1] - 1.2; x += BUOC) {
      if (tu(x, z) && (!canBan || tu(x, z - TRUOC_BAN))) return [x, z]
    }
  }
  return p.tam
}

function xepPhong(p, ds, nhanVat, ban) {
  const [tx, tz] = p.tam
  const dung = []
  const vat = []
  const dat = (nv, x, z) => {
    nhanVat.push({ ...nv, x, z, ngoi: ngoi(nv), phongMa: p.ma })
    dung.push([x, z])
  }
  const datBan = (x, z, man, khe, w = 2.8, d = 1.5) => {
    ban.push({ phong: p.ma, x, z, man, khe: khe ?? null, w, d })
    vat.push([x, z, w / 2, d / 2])
  }
  const thua = []
  if (p.loai === 'du_an') {
    vat.push([tx + CAY_DU_AN[0], tz + CAY_DU_AN[1], 0.4, 0.4])
    BAN_DU_AN.forEach(([bx, bz], i) => {
      const nv = ds[i]
      datBan(tx + bx, tz + bz, p.mo ? 'tat' : nv ? manCua(nv) : 'sang', nv?.khe_id)
      if (nv) dat(nv, tx + bx, tz + bz + TRUOC_BAN)
    })
    thua.push(...ds.slice(BAN_DU_AN.length))
  } else {
    for (const [x, z, w, d] of VAT_CA_PHE) vat.push([tx + x, tz + z, w, d])
    const hang = { dung: [...CA_PHE.dung], ngoi: [...CA_PHE.ngoi], loi: [...CA_PHE.loi] }
    for (const nv of ds) {
      const loai = nv.hien_thi === 'ranh' ? 'dung' : nv.hien_thi === 'loi' ? 'loi' : 'ngoi'
      const c = hang[loai].shift()
      if (!c) thua.push(nv)
      else if (loai !== 'loi') dat(nv, tx + c[0], tz + c[1])
      else {
        datBan(tx + c[0], tz + c[1], 'do', nv.khe_id, 2.2, 1.3)
        dat(nv, tx + c[0], tz + c[1] + TRUOC_BAN)
      }
    }
  }
  for (const nv of thua) {
    const loi = nv.hien_thi === 'loi'
    const [x, z] = oTrong(p, dung, vat, loi)
    if (loi) datBan(x, z - TRUOC_BAN, 'do', nv.khe_id, 2.2, 1.3)
    dat(nv, x, z)
  }
}

// Trả { nhanVat: [{...nv, x, z, ngoi, phongMa}], ban: [{phong, x, z, man: sang|do|tat, khe, w, d}] }.
export function datNhanVat(phong, nhanVat) {
  const theoMa = new Map(phong.map((p) => [p.ma, p]))
  const caPhe = phong.find((p) => p.loai === 'ca_phe')
  const nhom = new Map(phong.filter((p) => p.loai === 'du_an' || p === caPhe).map((p) => [p, []]))
  for (const nv of [...nhanVat].sort((a, b) => String(a.khe_id).localeCompare(String(b.khe_id)))) {
    const p = theoMa.get(nv.phong)
    const dich = p && nhom.has(p) ? p : caPhe
    if (dich) nhom.get(dich).push(nv)
  }
  const ra = { nhanVat: [], ban: [] }
  for (const [p, ds] of nhom) xepPhong(p, ds, ra.nhanVat, ra.ban)
  return ra
}
```

`frontend/src/van_phong/do_vat.js` (mới):

```js
// Đồ vật dựng bằng three thuần (mockup van-phong.js "Đồ vật", D20): vật liệu, hộp, màn hình, bàn, cây, cốc, ghế.
// Không DOM, không WebGL — chạy được trong node --test.
import { BoxGeometry, ConeGeometry, CylinderGeometry, Group, Mesh, MeshStandardMaterial, TorusGeometry } from 'three'
import { MAU } from './hien_thi.js'

export const MAN = { sang: MAU.man, do: MAU.manDo, tat: MAU.manTat }

export function vatLieu(mau, them = {}) {
  return new MeshStandardMaterial({ color: mau, roughness: 0.88, metalness: 0, ...them })
}

export function dat(obj, x, y, z) {
  obj.position.set(x, y, z)
  return obj
}

// Mesh có bóng đổ + nhận bóng (mặc định của mọi đồ đạc mockup).
export function khoi(geo, mat, bong = true) {
  const m = new Mesh(geo, mat)
  m.castShadow = bong
  m.receiveShadow = true
  return m
}

export function hop(w, h, d, mau, { bong = true, them } = {}) {
  return khoi(new BoxGeometry(w, h, d), vatLieu(mau, them), bong)
}

// Vật không nhận bấm (tường, bóng tròn dưới chân): tia dò bỏ qua để bấm xuyên tới sàn / nhân vật phía sau.
export function khongBam(o) {
  o.raycast = () => {}
  return o
}

export function lamMo(obj, doMo) {
  obj.traverse((o) => {
    if (!o.material) return
    o.material = o.material.clone()
    o.material.transparent = true
    o.material.opacity = Math.min(o.material.opacity ?? 1, doMo)
    o.castShadow = false
  })
}

function manHinh(mau) {
  const g = new Group()
  g.add(dat(hop(0.14, 0.4, 0.14, MAU.vien), 0, 0.2, 0))
  g.add(dat(hop(1.25, 0.82, 0.12, MAU.vien), 0, 0.72, 0))
  const sang = mau !== MAU.manTat
  const man = new Mesh(new BoxGeometry(1.08, 0.66, 0.02),
    vatLieu(mau, sang ? { emissive: mau, emissiveIntensity: 0.45 } : {}))
  g.add(dat(man, 0, 0.72, 0.07))
  g.userData.man = man
  return g
}

// Bàn làm việc; `mauMan` null = bàn không màn hình. userData.man = mặt màn hình (để nhấp nháy khi lỗi).
export function banLamViec(nhom, x, z, { mauMan = MAU.man, w = 2.8, d = 1.5 } = {}) {
  const g = new Group()
  g.add(dat(hop(w, 1.0, d, MAU.go), 0, 0.5, 0))
  if (mauMan) {
    const mh = manHinh(mauMan)
    mh.rotation.y = Math.PI / 4                 // màn hình quay mặt về phía camera (+x+z)
    g.add(dat(mh, 0.3, 1.0, -0.25))
    g.userData.man = mh.userData.man
  }
  nhom.add(dat(g, x, 0, z))
  return g
}

export function cayXanh(nhom, x, z, cao = 1) {
  const g = new Group()
  g.add(dat(khoi(new CylinderGeometry(0.36, 0.28, 0.55, 16), vatLieu(MAU.chau)), 0, 0.275, 0))
  g.add(dat(khoi(new CylinderGeometry(0.33, 0.33, 0.05, 16), vatLieu(MAU.dat)), 0, 0.55, 0))
  for (let i = 0; i < 7; i++) {
    const la = khoi(new ConeGeometry(0.1, 0.9 * cao, 6), vatLieu(i % 2 ? MAU.la : MAU.la2))
    const a = (i / 7) * Math.PI * 2
    la.position.set(Math.cos(a) * 0.12, 0.55 + 0.42 * cao, Math.sin(a) * 0.12)
    la.rotation.set(Math.sin(a) * 0.45, 0, -Math.cos(a) * 0.45)
    g.add(la)
  }
  nhom.add(dat(g, x, 0, z))
}

export function coc(nhom, x, y, z) {
  const g = new Group()
  g.add(dat(khoi(new CylinderGeometry(0.2, 0.16, 0.34, 16), vatLieu(MAU.su)), 0, 0.17, 0))
  g.add(dat(khoi(new CylinderGeometry(0.17, 0.17, 0.02, 16), vatLieu(MAU.cafe)), 0, 0.33, 0))
  g.add(dat(khoi(new TorusGeometry(0.09, 0.03, 6, 12), vatLieu(MAU.su)), 0.21, 0.17, 0))
  nhom.add(dat(g, x, y, z))
}

export function ghe(nhom, x, z) {
  nhom.add(dat(khoi(new CylinderGeometry(0.36, 0.32, 0.55, 14), vatLieu(MAU.ghe)), x, 0.275, z))
}
```

`frontend/src/van_phong/do_vat_tram.js` (mới):

```js
// Đồ vật phản ánh trạng thái trạm (mockup van-phong.js dungDoVat, D20): đèn Điều phối (2e, D38 vàng ấm) và bốn tủ
// máy chủ có đèn LED theo `suc_khoe.muc` (T6, D38/Q10). Toạ độ tương đối tâm ô của phòng.
import { CylinderGeometry, Mesh, MeshBasicMaterial, SphereGeometry } from 'three'
import { mauTuMay } from './bo_tri.js'
import { MAU } from './hien_thi.js'
import { banLamViec, dat, hop, khoi, vatLieu } from './do_vat.js'

// Phòng Điều phối: hai bàn + cột đèn. `sang === true` → bóng vàng ấm phát sáng; còn lại (false / null) → xám.
export function doDieuPhoi(g, tx, tz, p) {
  banLamViec(g, tx - 2.5, tz + 2.0)
  banLamViec(g, tx + 2.0, tz + 3.0)
  const [x, z] = [tx - 3.5, tz + 4.2]
  g.add(dat(khoi(new CylinderGeometry(0.07, 0.07, 2.3, 8), vatLieu(MAU.cot)), x, 1.15, z))
  g.add(dat(khoi(new CylinderGeometry(0.4, 0.4, 0.08, 16), vatLieu(MAU.cot)), x, 0.04, z))
  const sang = p.sang === true
  const den = new Mesh(new SphereGeometry(0.36, 20, 14), vatLieu(sang ? MAU.den : MAU.denTat,
    sang ? { emissive: MAU.den, emissiveIntensity: 0.9 } : { emissive: '#000000' }))
  den.castShadow = !sang
  g.add(dat(den, x, 2.45, z))
  return { den }
}

// Phòng máy chủ: 4 tủ đen xếp chéo, 3 đèn LED ở mặt +z. Tủ xanh tắt đèn giữa (như mockup); vàng/đỏ sáng cả ba.
export function doMayChu(g, tx, tz, p) {
  const tu = []
  mauTuMay(p).forEach((mau, i) => {
    const x = tx - 3.2 + i * 2.1
    const z = tz - 1.2 + i * 1.3
    g.add(dat(hop(1.6, 2.7, 1.6, MAU.tu), x, 1.35, z))
    for (let k = 0; k < 3; k++) {
      const m = k === 1 && mau === 'xanh' ? MAU.ledTat : MAU.suc_khoe[mau]
      const led = new Mesh(new SphereGeometry(0.1, 10, 8), new MeshBasicMaterial({ color: m }))
      g.add(dat(led, x - 0.35, 2.2 - k * 0.45, z + 0.81))
      if (k === 0) tu.push(led)
    }
  })
  return { tu }
}
```

`frontend/src/van_phong/dung_canh.js` (mới):

```js
// Ghép cảnh Văn phòng từ mặt bằng bo_tri (mockup van-phong.js dungVanPhong, D20): phòng + đồ đạc + nhân vật,
// cộng ánh sáng như mockup. CanhVanPhong gắn bằng <primitive :object> và tự gọi huyCanh (Tres không tự huỷ
// primitive — nodeOps.remove bỏ qua dispose khi là primitive).
import { AmbientLight, DirectionalLight, Group, HemisphereLight } from 'three'
import { dungDoVat } from './dung_do_vat.js'
import { dungPhong } from './dung_phong.js'
import { phaNv, taoNhanVat } from './nhan_vat_3d.js'

// Ánh sáng mockup: Ambient + Hemisphere + Directional đổ bóng (map 2048, khung ±26). three 0.186 bỏ
// PCFSoftShadowMap → TresCanvas dùng PCFShadowMap, làm mềm bằng shadow.radius (D38/Q17).
export function taoAnhSang() {
  const g = new Group()
  g.add(new AmbientLight('#fff3e4', 1.15))
  g.add(new HemisphereLight('#fff8ef', '#d8bfa2', 0.75))
  const mat = new DirectionalLight('#ffe9d2', 1.55)
  mat.position.set(-8, 34, 22)
  mat.castShadow = true
  mat.shadow.mapSize.set(2048, 2048)
  Object.assign(mat.shadow.camera, { left: -26, right: 26, top: 26, bottom: -26, near: 1, far: 90 })
  mat.shadow.camera.updateProjectionMatrix()
  mat.shadow.bias = -0.0006
  mat.shadow.normalBias = 0.03
  mat.shadow.radius = 3
  g.add(mat)
  return g
}

// Trả { goc: Group, dong: [{ g, nv, man, pha }] } — `dong` cho chuyenDongNv mỗi khung hình.
// goc.userData: tu (LED đầu mỗi tủ máy), den (bóng đèn Điều phối) — để test và kiểm.
export function dungCanh(boTri) {
  const goc = new Group()
  goc.add(dungPhong(boTri.phong))
  const dv = dungDoVat(boTri)
  goc.add(dv.nhom)
  const dong = boTri.nhanVat.map((nv) => {
    const g = taoNhanVat(nv)
    goc.add(g)
    return { g, nv, man: nv.hien_thi === 'loi' ? dv.manDo.get(nv.khe_id) ?? null : null, pha: phaNv(nv.khe_id) }
  })
  goc.userData.tu = dv.tu
  goc.userData.den = dv.den
  return { goc, dong }
}

// Giải phóng geometry, material, bóng đổ của đèn (mockup huy()).
export function huyCanh(obj) {
  if (!obj) return
  obj.traverse((o) => {
    o.geometry?.dispose()
    for (const m of [].concat(o.material ?? [])) m.dispose()
    if (o.isLight) o.dispose()
  })
}
```

`frontend/src/van_phong/dung_do_vat.js` (mới):

```js
// Đồ đạc từng loại phòng (mockup van-phong.js dungDoVat, D20) — three thuần. Mỗi phòng một Group mang
// userData.chon = { loai: 'phong', ma } nên bấm vào đồ đạc cũng chọn phòng. Toạ độ tương đối tâm ô (bo_tri `tam`).
import { CylinderGeometry, Group } from 'three'
import { CAY_DU_AN } from './cho_nv.js'
import { MAN, banLamViec, cayXanh, coc, dat, hop, khoi, lamMo, vatLieu } from './do_vat.js'
import { doDieuPhoi, doMayChu } from './do_vat_tram.js'
import { MAU } from './hien_thi.js'

function doGiamDoc(g, tx, tz) {
  g.add(dat(hop(4.8, 1.15, 2.5, MAU.goDam), tx, 0.575, tz - 0.5))
  g.add(dat(hop(0.9, 1.4, 0.9, MAU.goTu), tx, 0.7, tz - 2.6))
  cayXanh(g, tx - 4.0, tz + 3.0, 1.1)
  cayXanh(g, tx + 3.4, tz + 3.2, 0.9)
}

// Góc cà phê (tâm ô (-1, 1)): quầy dài đất nung + máy pha + cốc, bàn tròn có cốc, hai chậu cây.
// Vị trí quầy / bàn tròn / cây trùng VAT_CA_PHE của cho_nv.js (vật cản khi xếp thêm nhân vật).
function doCaPhe(g, tx, tz) {
  g.add(dat(hop(6.0, 1.15, 1.3, MAU.quay), tx - 1.6, 0.575, tz + 2.6))
  g.add(dat(hop(1.0, 0.8, 0.8, MAU.may), tx - 4.0, 1.55, tz + 2.5))
  for (const x of [-0.6, 0.1, 0.8]) coc(g, tx + x, 1.15, tz + 2.4)
  g.add(dat(khoi(new CylinderGeometry(1.0, 1.0, 0.12, 24), vatLieu(MAU.ban)), tx + 5.7, 0.95, tz - 1.6))
  g.add(dat(khoi(new CylinderGeometry(0.12, 0.3, 0.9, 10), vatLieu(MAU.chanBan)), tx + 5.7, 0.45, tz - 1.6))
  coc(g, tx + 5.5, 1.01, tz - 1.8)
  cayXanh(g, tx - 4.2, tz - 3.8)
  cayXanh(g, tx + 14.2, tz + 4.2, 0.9)
}

function doDuAn(g, tx, tz) {
  cayXanh(g, tx + CAY_DU_AN[0], tz + CAY_DU_AN[1])
}

const DO = { giam_doc: doGiamDoc, ca_phe: doCaPhe, du_an: doDuAn, dieu_phoi: doDieuPhoi, may_chu: doMayChu }

// Trả { nhom, tu (LED đầu mỗi tủ), den (bóng đèn Điều phối), manDo: Map khe_id → mặt màn hình đỏ }.
export function dungDoVat(boTri) {
  const nhom = new Group()
  const ra = { nhom, tu: [], den: null, manDo: new Map() }
  for (const p of boTri.phong) {
    const g = new Group()
    g.userData.chon = { loai: 'phong', ma: p.ma }
    nhom.add(g)
    Object.assign(ra, DO[p.loai]?.(g, p.tam[0], p.tam[1], p))
    for (const b of boTri.ban.filter((x) => x.phong === p.ma)) {
      const ban = banLamViec(g, b.x, b.z, { mauMan: MAN[b.man], w: b.w, d: b.d })
      if (b.khe && b.man === 'do') ra.manDo.set(b.khe, ban.userData.man)
    }
    if (p.mo) lamMo(g, 0.5)                                    // dự án chỉ quét thử: mờ như ke-toan mockup
  }
  return ra
}
```

`frontend/src/van_phong/dung_phong.js` (mới):

```js
// Mặt bằng (mockup van-phong.js dungPhong, D20): sàn mỗi phòng + tường. Cạnh chung hai phòng là tường có cửa
// (hai đoạn, hở giữa), cạnh sau cao 1,6 m, cạnh trước thấp 0,45 m để thấy bên trong. Hàm thuần three, không DOM.
import { BoxGeometry, Group, Mesh } from 'three'
import { O } from './bo_tri.js'
import { hop, khongBam, vatLieu } from './do_vat.js'

// Các cạnh dài O m của một phòng: [x0, z0, x1, z1, truoc] — truoc = cạnh phía camera (+x hoặc +z).
function canhCua(p) {
  const ra = []
  for (let x = p.x[0]; x < p.x[1]; x += O) ra.push([x, p.z[0], x + O, p.z[0], false], [x, p.z[1], x + O, p.z[1], true])
  for (let z = p.z[0]; z < p.z[1]; z += O) ra.push([p.x[0], z, p.x[0], z + O, false], [p.x[1], z, p.x[1], z + O, true])
  return ra
}

function tuong(c) {
  const trong = c.so > 1
  const cao = trong ? 1.3 : c.truoc ? 0.45 : 1.6
  const doc = c.x0 === c.x1
  const doan = trong ? [[0, 3.5], [6.5, O]] : [[0, O]]
  return doan.map(([a, b]) => {
    const dai = b - a + (trong ? 0 : 0.35)
    const m = new Mesh(new BoxGeometry(doc ? 0.32 : dai, cao, doc ? dai : 0.32),
      vatLieu(c.mau, { transparent: true, opacity: c.mo ? 0.35 : 0.62, depthWrite: false }))
    const giua = (a + b) / 2
    if (doc) m.position.set(c.x0, cao / 2, c.z0 + giua)
    else m.position.set(c.x0 + giua, cao / 2, c.z0)
    m.receiveShadow = true
    return khongBam(m)
  })
}

// Sàn mang userData.chon = { loai: 'phong', ma } để bấm chọn phòng (CanhVanPhong đi ngược parent tìm chon).
export function dungPhong(phong) {
  const nhom = new Group()
  const canh = new Map()
  for (const p of phong) {
    const w = p.x[1] - p.x[0]
    const d = p.z[1] - p.z[0]
    const san = hop(w, 0.3, d, p.san, { bong: false })
    san.position.set((p.x[0] + p.x[1]) / 2, -0.15, (p.z[0] + p.z[1]) / 2)
    san.userData.chon = { loai: 'phong', ma: p.ma }
    if (p.mo) Object.assign(san.material, { transparent: true, opacity: 0.75 })
    nhom.add(san)
    for (const [x0, z0, x1, z1, truoc] of canhCua(p)) {
      const k = `${x0},${z0},${x1},${z1}`
      const c = canh.get(k)
      if (c) c.so++
      else canh.set(k, { x0, z0, x1, z1, so: 1, mau: p.tuong, truoc, mo: p.mo })
    }
  }
  for (const c of canh.values()) nhom.add(...tuong(c))
  return nhom
}
```

`frontend/src/van_phong/hien_thi.js` (sửa):

```diff
diff --git a/frontend/src/van_phong/hien_thi.js b/frontend/src/van_phong/hien_thi.js
index fc90590..8706d0d 100644
--- a/frontend/src/van_phong/hien_thi.js
+++ b/frontend/src/van_phong/hien_thi.js
@@ -2,13 +2,15 @@
 // (`hien_thi` ∈ lam | ranh | can_nguoi | loi | tat — tram/suy/nhan_vat.py); ở đây chỉ đổi sang tư thế, màu, chữ.
 import { gioVN } from '../luat.js'
 
-// `den`: đèn Điều phối khi sáng — vàng ấm (D38, plan 2e G21); `denTat`: xám khi tắt hoặc chưa có tín hiệu.
+// Bảng màu đồ vật của mockup van-phong.js MAU (D20). `den`: đèn Điều phối khi sáng — vàng ấm (D38, plan 2e G21);
+// `denTat`: xám khi tắt hoặc chưa có tín hiệu. `suc_khoe`: đèn LED tủ máy chủ theo `suc_khoe.muc[i].mau` (T6).
 export const MAU = {
-  phong: { du_an: '#cfe2f3', dieu_phoi: '#d9d2e9', giam_doc: '#fce5cd', may_chu: '#d0e0e3', ca_phe: '#ead1dc' },
-  tuong: '#f3f3f3', ban: '#e6d5c3', dau: '#ffe0bd', chamDo: '#cc0000', den: '#f2c14e', denTat: '#b7b7b7',
-  than: { claude: '#f6b26b', codex: '#9fc5e8', khac: '#b6d7a8' },
-  manHinh: { sang: '#a4c2f4', do: '#e06666', tat: '#999999' },
-  suc_khoe: { xanh: '#93c47d', vang: '#ffd966', do: '#e06666' },
+  go: '#c79d74', goDam: '#7a2c14', goTu: '#5d2412', quay: '#c9805e', may: '#3b3330', man: '#9fd0ee',
+  manDo: '#e0574a', manTat: '#8d949a', vien: '#2f3439', da: '#f2c9a3', chan: '#2b2523', tu: '#30363c',
+  ledTat: '#4b5a52', ghe: '#8a6a50', chau: '#c4673f', la: '#5f9e57', la2: '#7cb36d', dat: '#5a3d2b',
+  su: '#ece7f2', cafe: '#5b3426', ban: '#efe6da', chanBan: '#8d7a6a', cot: '#6b6058', bong: '#3a2418',
+  den: '#f2c14e', denTat: '#b7b7b7',
+  suc_khoe: { xanh: '#5fd38a', vang: '#f2c14e', do: '#e0574a' },
 }
 export const TEN_HIEN_THI = { lam: 'Làm', ranh: 'Rảnh', can_nguoi: 'Cần người', loi: 'Lỗi', tat: 'Tắt / mất kết nối' }
 const TEN_BUOC = { spec: 'spec', code: 'code', qc: 'QC' }
@@ -24,10 +26,6 @@ export function tuThe(hienThi) {
   return { ...(TU_THE[hienThi] ?? TU_THE.tat) }
 }
 
-export function mauThan(cli) {
-  return MAU.than[cli] ?? MAU.than.khac
-}
-
 // Cắt theo ký tự (không cắt đôi chữ có dấu tổ hợp sẵn).
 export function catChu(s, n) {
   const kt = Array.from(String(s ?? ''))
@@ -37,7 +35,8 @@ export function catChu(s, n) {
 export function chuBien(p) {
   if (p.loai === 'giam_doc') return `Phòng giám đốc · ${p.so_cho} việc chờ`
   if (p.loai === 'dieu_phoi') {
-    return `Điều phối · ${p.sang === null || p.sang === undefined ? 'chưa có tín hiệu' : p.sang ? 'đang có phiên' : 'tắt đèn'}`
+    const den = p.sang === null || p.sang === undefined ? 'chưa có tín hiệu' : p.sang ? 'đang có phiên' : 'tắt đèn'
+    return `Điều phối · ${den}`
   }
   return catChu(p.ten ?? p.ma, 28)
 }
```

`frontend/src/van_phong/khung_nhin.js` (mới):

```js
// Khít khung camera trực giao và chiếu điểm 3D ra toạ độ màn hình (mockup van-phong.js khit(), manHinhXY()).
// Thuần three (Vector3, ma trận camera), không DOM. Gọi SAU khi camera đã đặt position + lookAt (bài học 2c T8).
import { Vector3 } from 'three'
import { caoNv } from './nhan_vat_3d.js'

export const PHONG_TO = 1.12                       // phóng thêm, cắt nhẹ hai góc xa như ảnh demo

// Các góc sàn (đáy -0,3 m, đỉnh tường 2,6 m) của mọi phòng.
export function gocSan(phong) {
  const goc = []
  for (const p of phong) {
    for (const x of p.x) for (const z of p.z) for (const y of [-0.3, 2.6]) goc.push(new Vector3(x, y, z))
  }
  return goc
}

// Trả { left, right, top, bottom } để mọi góc nằm trong khung w×h (giữ tỉ lệ), chừa chỗ biển phía trên,
// rồi chia cho phongTo. Camera phải cập nhật ma trận thế giới trước (gọi ở đây).
export function khit(camera, goc, w, h, phongTo = PHONG_TO) {
  camera.updateMatrixWorld()
  let [x0, x1, y0, y1] = [Infinity, -Infinity, Infinity, -Infinity]
  const c = new Vector3()
  for (const v of goc) {
    c.copy(v).applyMatrix4(camera.matrixWorldInverse)
    x0 = Math.min(x0, c.x)
    x1 = Math.max(x1, c.x)
    y0 = Math.min(y0, c.y)
    y1 = Math.max(y1, c.y)
  }
  const le = 0.5
  x0 -= le
  x1 += le
  y0 -= le
  y1 += le + 1.2                                   // chừa chỗ biển tên phòng phía trên
  let cw = x1 - x0
  let ch = y1 - y0
  const cx = (x0 + x1) / 2
  const cy = (y0 + y1) / 2
  if (cw / ch > w / h) ch = (cw * h) / w
  else cw = (ch * w) / h
  cw /= phongTo
  ch /= phongTo
  return { left: cx - cw / 2, right: cx + cw / 2, top: cy + ch / 2, bottom: cy - ch / 2 }
}

// Cỡ chữ (px) của lớp nhãn co theo bề rộng khung như mockup boTriLai().
export function coChu(w) {
  return 16 * Math.max(0.7, Math.min(1.05, w / 1100))
}

const tam = new Vector3()
export function chieu(camera, w, h, [x, y, z]) {
  tam.set(x, y, z).project(camera)
  return { x: ((tam.x + 1) / 2) * w, y: ((1 - tam.y) / 2) * h }
}

// Toạ độ 2D của điểm neo mỗi nhãn + khung thân từng nhân vật (vật cản cho boTriNhan).
export function chieuNhan(camera, w, h, nhan, nhanVat) {
  const diem = Object.fromEntries(nhan.map((n) => [n.id, chieu(camera, w, h, n.neo)]))
  const than = nhanVat.map((nv) => {
    const a = chieu(camera, w, h, [nv.x, 0, nv.z])
    const b = chieu(camera, w, h, [nv.x, caoNv(nv), nv.z])
    const cao = a.y - b.y
    return { x: a.x - cao * 0.3, y: b.y - 2, w: cao * 0.6, h: cao + 6, khe: nv.khe_id }
  })
  return { W: w, H: h, diem, than }
}
```

`frontend/src/van_phong/nhan_canh.js` (mới):

```js
// Danh sách nhãn HTML phủ trên cảnh (mockup van-phong.js "nhân vật + nhãn", "biển tên phòng", D20) — hàm thuần.
// Mỗi nhãn: { id, loai (bien|ten|bb|hh|gd), neo [x, y, z], ax, ay, dx, dy, khe?, chon, chu, nhanDoc, … }.
import { boTriNhan, demChong } from './bo_tri_nhan.js'
import { chuBongBong } from './hien_thi.js'
import { caoNv } from './nhan_vat_3d.js'

const TEN_PHU = { lam: 'Làm', ranh: 'Rảnh', can_nguoi: 'Cần người', loi: 'Lỗi', tat: 'Tắt' }

// Nhãn phụ dưới tên nhân vật; `cau_dao_ngat` (T2) thiếu → "Lỗi".
export function nhanPhu(nv) {
  if (nv.trang_thai === 'mat_ket_noi') return 'Mất kết nối'
  if (nv.hien_thi === 'loi') return nv.cau_dao_ngat ? 'Lỗi · cầu dao ngắt' : 'Lỗi'
  return TEN_PHU[nv.hien_thi] ?? 'Tắt'
}

// Lớp chip trạng thái (chung.css): mất kết nối có màu riêng, cầu dao ngắt màu vàng, còn lại theo hien_thi.
export function lopNhanVat(nv) {
  if (nv.trang_thai === 'mat_ket_noi') return 'tt-mat_ket_noi'
  if (nv.hien_thi === 'loi' && nv.cau_dao_ngat) return 'tt-cau_dao'
  return `tt-${TEN_PHU[nv.hien_thi] ? nv.hien_thi : 'tat'}`
}

// Đèn Điều phối (2e G21): sang true / false / null.
export function trangThaiDen(p) {
  return p.sang === true ? 'đang có phiên' : p.sang === false ? 'tắt đèn' : 'chưa có tín hiệu'
}

function nhanNhanVat(nv) {
  const chon = { loai: 'khe', khe_id: nv.khe_id }
  const goc = { khe: nv.khe_id, chon }
  const cao = caoNv(nv)
  const phu = nhanPhu(nv)
  const ra = [{ ...goc, id: `ten:${nv.khe_id}`, loai: 'ten', neo: [nv.x, 0, nv.z], ax: -0.5, ay: 0, dx: 0, dy: 8,
    chu: nv.ten, phu, mo: nv.hien_thi === 'tat', nhanDoc: `${nv.ten}: ${phu}` }]
  const bb = chuBongBong(nv)
  if (bb) {
    ra.push({ ...goc, id: `bb:${nv.khe_id}`, loai: 'bb', neo: [nv.x, cao + 0.3, nv.z], ax: -0.5, ay: -1, dx: 0,
      dy: -10, ma: nv.bead.bead_id, chu: bb, nhanDoc: `${nv.ten} đang giữ ${nv.bead.bead_id}: ${bb}` })
  }
  if (nv.hien_thi === 'can_nguoi') {
    ra.push({ ...goc, id: `hh:${nv.khe_id}`, loai: 'hh', neo: [nv.x, cao - 0.5, nv.z], ax: 0, ay: -0.5, dx: 16,
      dy: 0, chu: '1', nhanDoc: `${nv.ten} cần Đại ca trả lời` })
  }
  return ra
}

function nhanPhong(p) {
  const chon = { loai: 'phong', ma: p.ma }
  const den = p.loai === 'dieu_phoi' ? { sang: p.sang === true, chu: trangThaiDen(p) } : null
  const ra = [{ id: `bien:${p.ma}`, loai: 'bien', neo: [p.nhan[0], 0.5, p.nhan[1]], ax: -0.5, ay: -0.5, dx: 0, dy: 0,
    chon, chu: p.tenBien, mo: p.mo, den, nhanDoc: den ? `${p.tenBien}, đèn ${den.chu}` : p.tenBien }]
  if (p.loai === 'giam_doc' && p.so_cho > 0) {
    ra.push({ id: 'gd', loai: 'gd', neo: [p.tam[0] + 0.4, 1.2, p.tam[1]], ax: -0.5, ay: -1, dx: 0, dy: -2, chon,
      chu: String(p.so_cho), nhanDoc: `${p.so_cho} việc chờ Đại ca` })
  }
  return ra
}

export function dungNhan(boTri) {
  return [...boTri.nhanVat.flatMap(nhanNhanVat), ...boTri.phong.flatMap(nhanPhong)]
}

// Phòng / nhân vật đang chọn ({loai, ma | khe_id}) trong mặt bằng mới nhất → props cho PanelChon (khoa = :key).
export function timMucChon(boTri, c) {
  if (!c || !boTri) return null
  if (c.loai === 'khe') {
    const nv = boTri.nhanVat.find((n) => n.khe_id === c.khe_id)
    return nv ? { khoa: `khe:${nv.khe_id}`, nv } : null
  }
  const p = boTri.phong.find((x) => x.ma === c.ma)
  return p ? { khoa: `phong:${p.ma}`, phong: p } : null
}

// Từ toạ độ neo (chieuNhan) + cỡ đo được {id: {w, h}} → vị trí từng nhãn, đường chỉ, số cặp chồng.
export function xepNhan(nhan, chieu, co) {
  const ds = nhan.filter((n) => chieu.diem[n.id] && co[n.id]).map((n) => {
    const d = chieu.diem[n.id]
    const { w, h } = co[n.id]
    const x0 = d.x + n.ax * w + n.dx
    return { id: n.id, loai: n.loai, khe: n.khe, w, h, x0, y0: d.y + n.ay * h + n.dy, diemNeo: d }
  })
  const duong = boTriNhan(ds, chieu.than, chieu.W, chieu.H)
  return { viTri: Object.fromEntries(ds.map((n) => [n.id, { x: n.x, y: n.y }])), duong, chong: demChong(ds) }
}
```

`frontend/src/van_phong/nhan_vat_3d.js` (mới):

```js
// Nhân vật chibi (mockup van-phong.js nhanVat, D20): bóng tròn, ghế khi ngồi, chân, thân, đầu, tóc, hai tay.
// Màu thân/tóc theo khe (mau_khe.js, chung với Đội ngũ AI). Giơ tay khi can_nguoi, mờ khi tat. Three thuần.
import { CircleGeometry, CylinderGeometry, Group, Mesh, MeshBasicMaterial, SphereGeometry } from 'three'
import { fnv1a, mauKhe } from '../mau_khe.js'
import { MAU } from './hien_thi.js'
import { dat, ghe, khoi, khongBam, lamMo, vatLieu } from './do_vat.js'

export const CO_NV = 1.4                                  // phóng nhân vật cho giống tỉ lệ ảnh demo
const yThan = (nv) => (nv.ngoi ? 0.55 : 0.52)
// Chiều cao đỉnh đầu (m, đã nhân CO_NV) — neo bong bóng / huy hiệu và khung thân cho bo_tri_nhan.
export const caoNv = (nv) => (yThan(nv) + 1.95) * CO_NV

function chan(than, ngoi, mau) {
  for (const s of [-1, 1]) {
    const c = khoi(new CylinderGeometry(0.13, 0.12, 0.56, 12), mau)
    if (ngoi) {
      c.rotation.x = Math.PI / 2
      dat(c, s * 0.17, 0.62, 0.3)
    } else dat(c, s * 0.17, 0.28, 0)
    than.add(c)
  }
}

function tay(than, y0, mau) {
  return [-1, 1].map((s) => {
    const truc = dat(new Group(), s * 0.42, y0 + 0.82, 0)
    truc.add(dat(khoi(new CylinderGeometry(0.1, 0.09, 0.62, 10), mau), 0, -0.28, 0))
    truc.rotation.z = s * 0.12
    than.add(truc)
    return truc
  })
}

// nv: phần tử nhanVat của bo_tri (x, z, ngoi, hien_thi, khe_id). userData: chon, than, tay.
export function taoNhanVat(nv) {
  const mau = mauKhe(nv.khe_id)
  const g = new Group()
  const bong = new Mesh(new CircleGeometry(0.66, 28),
    new MeshBasicMaterial({ color: MAU.bong, transparent: true, opacity: 0.18, depthWrite: false }))
  bong.rotation.x = -Math.PI / 2
  g.add(khongBam(dat(bong, 0, 0.03, 0)))
  const than = new Group()
  g.add(than)
  if (nv.ngoi) ghe(than, 0, -0.05)
  chan(than, nv.ngoi, vatLieu(MAU.chan))
  const y0 = yThan(nv)
  const mauThan = vatLieu(mau.than)
  than.add(dat(khoi(new CylinderGeometry(0.34, 0.42, 0.92, 22), mauThan), 0, y0 + 0.46, 0))
  than.add(dat(khoi(new SphereGeometry(0.5, 28, 20), vatLieu(MAU.da)), 0, y0 + 1.36, 0))
  const toc = khoi(new SphereGeometry(0.53, 28, 14, 0, Math.PI * 2, 0, Math.PI * 0.52), vatLieu(mau.toc))
  toc.rotation.x = -0.42
  than.add(dat(toc, 0, y0 + 1.4, -0.02))
  const hai = tay(than, y0, mauThan)
  if (nv.hien_thi === 'can_nguoi') hai[1].rotation.z = Math.PI - 0.35          // giơ tay phải
  g.rotation.y = Math.PI / 4                                                 // quay mặt về phía camera
  if (nv.hien_thi === 'tat') lamMo(g, 0.36)
  g.position.set(nv.x, 0, nv.z)
  g.scale.setScalar(CO_NV)
  g.userData = { chon: { loai: 'khe', khe_id: nv.khe_id }, than, tay: hai }
  return g
}

export const phaNv = (kheId) => (fnv1a(kheId) % 628) / 100

// Một khung hình chuyển động (mockup ve()): nhún khi lam, vẫy tay khi can_nguoi, xoay nhẹ khi ranh,
// màn đỏ nhấp nháy khi loi. Chỉ gọi khi KHÔNG bật "Giảm chuyển động" (dựng lại cảnh trả về tư thế tĩnh).
export function chuyenDongNv(muc, t) {
  const { than, tay: hai } = muc.g.userData
  const ht = muc.nv.hien_thi
  than.position.y = ht === 'lam' ? Math.abs(Math.sin(t * 3.4 + muc.pha)) * 0.12 : 0
  if (ht === 'can_nguoi') hai[1].rotation.z = Math.PI - 0.35 + Math.sin(t * 5) * 0.22
  if (ht === 'ranh') than.rotation.y = Math.sin(t * 0.9 + muc.pha) * 0.25
  if (muc.man) muc.man.material.emissiveIntensity = 0.35 + Math.abs(Math.sin(t * 2.2)) * 0.5
}
```

Xoá file thay thế:

```bash
git rm -q frontend/src/van_phong/NhanVat3D.vue frontend/src/van_phong/Phong3D.vue frontend/src/van_phong/TheChu3D.vue frontend/src/van_phong/the_chu.js
```

- [ ] **Step 4: Chạy thấy PASS**

```bash
cd frontend && node --test tests/van_phong.test.mjs tests/van_phong_canh.test.mjs
npm run kiem && npm run build && npm run kiem-dist && cd ..
```

Kỳ vọng: PASS — lệnh test của task: pass 11 · fail 0; toàn bộ tăng đúng 6 node (net) test so với main trước task (bảng "Sơ đồ đợt chạy"); `npm run build`, `npm run kiem-dist` xanh. Số đo trên bản chạy thử.

- [ ] **Step 5: Commit**

```bash
git add frontend/tests/van_phong.test.mjs frontend/tests/van_phong_canh.test.mjs frontend/src/kieu/van-phong.css frontend/src/trang/VanPhong.vue frontend/src/van_phong/CanhVanPhong.vue frontend/src/van_phong/DanhSachVanPhong.vue frontend/src/van_phong/LopNhan.vue frontend/src/van_phong/PanelChon.vue frontend/src/van_phong/bo_tri.js frontend/src/van_phong/bo_tri_nhan.js frontend/src/van_phong/cho_nv.js frontend/src/van_phong/do_vat.js frontend/src/van_phong/do_vat_tram.js frontend/src/van_phong/dung_canh.js frontend/src/van_phong/dung_do_vat.js frontend/src/van_phong/dung_phong.js frontend/src/van_phong/hien_thi.js frontend/src/van_phong/khung_nhin.js frontend/src/van_phong/nhan_canh.js frontend/src/van_phong/nhan_vat_3d.js && git rm -q --cached --ignore-unmatch frontend/src/van_phong/NhanVat3D.vue frontend/src/van_phong/Phong3D.vue frontend/src/van_phong/TheChu3D.vue frontend/src/van_phong/the_chu.js
git commit -m "feat(dashboard): 2f Văn phòng 3D theo mockup"
```

### Task 13: Trang Tổng quan (trang mở đầu, D17)

**Đợt:** 3 · **Độ khó:** vừa · **Phải xong trước:** Task 1, 2 (Task 8 cho dữ liệu thật — không cần cho build/test) · **Test mới:** 4 node

**Mockup bám:** `trang-tong-quan.js` (sáu khối `khoiViecCho`, `khoiSucKhoe`, `khoiDoiNgu`, `khoiDuAn`, `khoiUsage`, `khoiSuKien`), `du-lieu.js`, `style.css` mục "Tổng quan"; ảnh `anh-tong-quan.png`. G6 (số tổng = `so` của Phê duyệt), G12.

**Files:**
- Create: `frontend/src/thanh/tong_quan/KhoiViecCho.vue`, `KhoiSucKhoe.vue`, `KhoiDoiNgu.vue`, `KhoiDuAn.vue`, `KhoiUsage.vue`, `KhoiSuKien.vue`, `frontend/src/luat_tong_quan.js` (`oViecCho`, `chipDichVu`, `dongTram`, `demTrangThai`, `usageHomNay`, `maNgan`), `frontend/src/kieu/tong-quan.css`
- Modify: `frontend/src/trang/TongQuan.vue` (thay toàn bộ trang giữ chỗ của Task 1)
- Test: `frontend/tests/tong_quan.test.mjs` (mới)

**Interfaces:**
- Consumes: `GET /api/tong-quan` (Task 8); `Chibi`, `hanMucThapNhat`, `tenKhe`, `nhanTrangThai`, `gon`, `gioPhut`, `truocDay`. Không import gì từ `van_phong/` hay `three`.

Polling 5 giây + tải lại theo `kho.phienBan`, `kho.phienBanDoiNgu`; bỏ kết quả tải cũ. Dự án `bat_ghi === false`: dòng mờ + chip "chỉ quét thử" (không dùng chữ "tạm đóng" của mockup — D37). Ô đèn Điều phối không làm (ranh giới 2e/2f).

- [ ] **Step 1: Viết test (chép nguyên văn)**

`frontend/tests/tong_quan.test.mjs` (mới):

```js
import assert from 'node:assert/strict'
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
```

- [ ] **Step 2: Chạy thấy FAIL**

```bash
cd frontend && node --test tests/tong_quan.test.mjs
```

Kỳ vọng: FAIL — `Error [ERR_MODULE_NOT_FOUND]: Cannot find module '…/frontend/src/luat_tong_quan.js' imported from …/frontend/tests/tong_quan.test.mjs`

- [ ] **Step 3: Viết mã (chép nguyên văn; file sửa: chép khối diff ra file tạm, `git apply --check` rồi `git apply`)**

`frontend/src/kieu/tong-quan.css` (mới):

```css
/* Trang Tổng quan (D17) — chép từ mockup style.css mục "Tổng quan"; tiêu đề khối dùng .tieu-de-khoi (chung.css).
   Các style="..." nội tuyến của mockup đổi thành lớp ở đây (CSP chặt, spec 2 §4). */
.tq-cho { border-color: #e6c8b9; background: linear-gradient(180deg, #fffaf6, #fff); padding: 16px 18px 18px;
  margin-bottom: 16px; }
.tq-dau { display: flex; align-items: center; gap: 10px; margin-bottom: 14px; }
.tq-dau h2 { margin: 0; font-size: 19px; }
.tq-dau .nut.chinh { margin-left: auto; }
.tq-tong { background: var(--nhan); color: #fff; font-weight: 800; border-radius: 999px; min-width: 28px; height: 28px;
  display: grid; place-items: center; padding: 0 9px; }
.tq-o-cho { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 10px; }
.tq-o { display: flex; flex-direction: column; gap: 3px; padding: 12px 14px; border: 1px solid var(--vien);
  border-radius: 12px; background: #fff; text-decoration: none; color: inherit; }
.tq-o:hover { border-color: var(--nhan); box-shadow: 0 4px 12px #6b4a3014; }
.tq-o .so { font-size: 30px; font-weight: 800; line-height: 1.1; align-self: flex-start; padding: 0 10px;
  border-radius: 10px; background: none; border: 0; }
.tq-o.rong { background: var(--nen-3); }
.tq-o.rong .so { color: var(--chu-phu); }
.tq-o strong { font-size: 14.5px; }
.tq-luoi { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; margin-bottom: 16px;
  align-items: start; }
.tq-luoi-2 { grid-template-columns: minmax(0, 1.4fr) minmax(0, 1fr); }
.tq-ds { list-style: none; margin: 0; padding: 0; }
.tq-ds li { display: grid; grid-template-columns: minmax(0, auto) 1fr auto; gap: 10px; align-items: center;
  padding: 7px 0; border-bottom: 1px solid var(--vien); font-size: 13.5px; }
.tq-ds li:last-child { border-bottom: 0; }
.tq-ds .mono { font-size: 12.5px; }
.tq-ds2 { margin-top: 8px; border-top: 1px dashed var(--vien-dam); }
.tq-ds2 li { grid-template-columns: 1fr auto; }
.tq-chibi { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 12px; }
.tq-chibi a { display: flex; flex-direction: column; align-items: center; gap: 3px; font-size: 11.5px;
  color: var(--chu-2); text-decoration: none; }
.tq-chip { display: flex; gap: 6px; flex-wrap: wrap; }
.tq-thap { margin: 12px 0 0; font-size: 13.5px; color: var(--chu-2); background: #fcf3e2; border: 1px solid #efd8a8;
  border-radius: 8px; padding: 7px 10px; }
.tq-so { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-bottom: 12px; }
.tq-so div { display: flex; flex-direction: column; background: var(--nen-3); border: 1px solid var(--vien);
  border-radius: 10px; padding: 8px 10px; }
.tq-so b { font-size: 18px; }
.tq-so .nho { font-size: 11.5px; }
.tq-cot div { display: grid; grid-template-columns: 74px 1fr 48px; gap: 8px; align-items: center; font-size: 12.5px;
  margin: 5px 0; }
.tq-cot i { display: block; height: 8px; border-radius: 99px; background: var(--nhan); opacity: .75; }
.tq-chu-thich { margin: 8px 0 0; }
.tq-xong { color: var(--nhan); }
.tq-dem { font-weight: 400; }
.tq-sk td { padding: 6px 10px; font-size: 13px; }
@media (max-width: 1100px) {
  .tq-luoi, .tq-luoi-2 { grid-template-columns: 1fr; }
  .tq-so { grid-template-columns: repeat(2, 1fr); }
}
```

`frontend/src/luat_tong_quan.js` (mới):

```js
// Luật hiển thị thuần của trang Tổng quan (D17; mockup trang-tong-quan.js). Dữ liệu từ GET /api/tong-quan;
// mọi trạng thái nghiệp vụ tính ở server, ở đây chỉ đếm và đổi sang chữ. Test: tests/tong_quan.test.mjs.
import { gioPhut, gon, truocDay } from './dinh_dang.js'
import { tenKhe } from './luat_han_muc.js'
import { nhanTrangThai } from './luat_doi_ngu.js'

// Mã ngắn của khe như mockup: "B/claude-4" → "claude-4".
export const maNgan = (kheId) => String(kheId || '').split('/').pop()

const dsMuc = (dl) => (dl && dl.phe_duyet && dl.phe_duyet.muc) || []
const loc = (dl, ...loai) => dsMuc(dl).filter((m) => loai.includes(m.loai))
const ct = (m) => (m && m.chi_tiet) || {}

// Năm ô "Việc chờ Đại ca" (mockup khoiViecCho; D38/Q6: tổng là `phe_duyet.so`, mỗi ô đếm riêng).
export function oViecCho(dl) {
  const canChot = ((dl && dl.du_an) || []).reduce((s, d) => s + ((d.so_bead && d.so_bead['can-chot']) || 0), 0)
  const review = loc(dl, 'cho-review')
  const khongXm = review.filter((m) => ct(m).pr_tram && ct(m).pr_tram.trang_thai === 'khong_xac_minh').length
  const bi = loc(dl, 'escalation', 'decision')
  const hoi = bi.find((m) => m.loai === 'escalation' && ct(m).khe_id)          // T4: khe nào hỏi ở bead nào
  const spec = loc(dl, 'spec')
  const he = loc(dl, 'he')
  const heDau = ct(he[0])
  const o = (ten, so, phu, toi, lop) => ({ ten, so, phu, toi, lop })
  return [
    o('Cần Đại ca chốt', canChot, 'cột 2 · có câu hỏi', '/cong-viec', 'tt-can_nguoi'),
    o('Chờ review để đóng', review.length, `cột 3${khongXm ? ` · ${khongXm} PR không xác minh được` : ''}`,
      '/phe-duyet', 'tt-cau_dao'),
    o('Escalation bí', bi.length, hoi ? `${tenKhe(ct(hoi).khe_id)} hỏi ở ${ct(hoi).bead_goc || hoi.bead_id}`
      : 'không có', '/phe-duyet', 'tt-can_nguoi'),
    o('Spec chờ duyệt', spec.length, spec.length ? 'đọc rồi duyệt ở Phê duyệt' : 'chưa có', '/phe-duyet', ''),
    o('Hệ cần xem', he.length, !he.length ? 'không có' : heDau.khe_id ? `cầu dao ${maNgan(heDau.khe_id)}`
      : heDau.su_kien || '', '/phe-duyet', 'tt-cau_dao'),
  ]
}

// Chip một dịch vụ launchd (mockup khoiSucKhoe; `da_cai`/`dang_chay` null = không kiểm được).
export function chipDichVu(dv) {
  if (dv.dang_chay === true) return { chu: 'chạy', lop: 'tt-lam' }
  if (dv.da_cai === false) return { chu: 'chưa cài', lop: 'tt-tat' }
  if (dv.da_cai === true && dv.dang_chay === false) return { chu: 'dừng', lop: 'tt-can_nguoi' }
  return { chu: 'không rõ', lop: '' }
}

const TEN_LOI_NHO = { 'nho.loi_llm': 'LLM', 'nho.loi_embedder': 'embedder' }

// Bốn dòng dưới danh sách dịch vụ: [tên, giá trị, lớp chip].
export function dongTram(dl, bayGio = new Date()) {
  const quet = ((dl && dl.du_an) || []).map((d) => d.quet_cuoi).filter(Boolean)
    .sort((a, b) => new Date(b) - new Date(a))[0]
  const estop = Boolean(dl && dl.tram && dl.tram.estop)
  const loiNho = [...new Set(loc(dl, 'he').map((m) => TEN_LOI_NHO[ct(m).su_kien]).filter(Boolean))]
  const ngat = ((dl && dl.doi_ngu && dl.doi_ngu.khe) || []).filter((k) => k.cau_dao && k.cau_dao.ngat)
  return [
    ['Quét cuối', quet ? `${gioPhut(quet)} · ${truocDay(quet, bayGio)}` : 'chưa quét', quet ? 'tt-lam' : 'tt-tat'],
    ['Estop', estop ? 'đang bật' : 'tắt', estop ? 'tt-can_nguoi' : 'tt-lam'],
    ['Lỗi memory', loiNho.length ? `lỗi ${loiNho.join(', ')}` : 'không', loiNho.length ? 'tt-can_nguoi' : 'tt-lam'],
    ['Cầu dao khe', ngat.length ? `${ngat.length} ngắt · ${ngat.map((k) => maNgan(k.khe_id)).join(', ')}` : 'không',
      ngat.length ? 'tt-cau_dao' : 'tt-lam'],
  ]
}

// Thứ tự chip như mockup NHAN_TRANG_THAI; cầu dao ngắt đè trạng thái (nhanTrangThai, luat_doi_ngu.js).
const THU_TU = ['lam', 'ranh', 'tat', 'cau_dao', 'can_nguoi', 'loi', 'mat_ket_noi']
export const lopTrangThai = (k) => (k.cau_dao && k.cau_dao.ngat ? 'cau_dao' : k.trang_thai)

export function demTrangThai(dsKhe) {
  const dem = {}
  for (const k of dsKhe || []) dem[lopTrangThai(k)] = (dem[lopTrangThai(k)] || 0) + 1
  const ten = Object.fromEntries((dsKhe || []).map((k) => [lopTrangThai(k), nhanTrangThai(k)]))
  return THU_TU.filter((tt) => dem[tt]).map((tt) => ({ lop: `tt-${tt}`, chu: ten[tt], n: dem[tt] }))
}

// Usage hôm nay (mockup khoiUsage): giá khe thuê bao chỉ là tương đương; dòng `cham-cot` là Claude API.
const CHAM_COT = 'cham-cot'
const tien = (x) => (typeof x === 'number' ? `$${x.toFixed(2)}` : 'chưa có giá')
const tong = (ds, khoa) => ds.reduce((s, d) => s + (typeof d[khoa] === 'number' ? d[khoa] : 0), 0)
const tongGia = (ds) => (ds.some((d) => typeof d.chi_phi_usd === 'number') ? tong(ds, 'chi_phi_usd') : null)

export function usageHomNay(usage) {
  const ngay = (usage && usage.theo_ngay) || []
  const nguon = (usage && usage.theo_nguon) || []
  const khe = nguon.filter((d) => d.khoa !== CHAM_COT)
    .sort((a, b) => (b.chi_phi_usd || 0) - (a.chi_phi_usd || 0))
  const max = Math.max(0, ...khe.map((d) => d.chi_phi_usd || 0))
  return {
    vao: gon(tong(ngay, 'token_vao')),
    ra: gon(tong(ngay, 'token_ra')),
    usdKhe: tien(tongGia(khe)),
    usdApi: tien(tongGia(nguon.filter((d) => d.khoa === CHAM_COT))),
    luot: tong(ngay, 'so_lan'),
    cot: khe.map((d) => ({ ma: maNgan(d.khoa), usd: tien(d.chi_phi_usd),
      rong: max > 0 ? ((d.chi_phi_usd || 0) / max) * 100 : 0 })),
  }
}
```

`frontend/src/thanh/tong_quan/KhoiDoiNgu.vue` (mới):

```vue
<script setup>
import { computed } from 'vue'
import { nhanTrangThai } from '../../luat_doi_ngu.js'
import { hanMucThapNhat, tenKhe } from '../../luat_han_muc.js'
import { demTrangThai } from '../../luat_tong_quan.js'
import Chibi from '../Chibi.vue'

// Khối "Đội ngũ" (mockup trang-tong-quan.js khoiDoiNgu): chibi từng khe, chip đếm trạng thái, hạn mức 5 giờ thấp nhất.
const props = defineProps({ doiNgu: { type: Object, default: null }, bayGio: { type: Date, required: true } })
const khe = computed(() => (props.doiNgu && props.doiNgu.khe) || [])
const dem = computed(() => demTrangThai(khe.value))
const thap = computed(() => hanMucThapNhat(khe.value, props.bayGio))
const mo = (k) => k.trang_thai === 'tat' || k.trang_thai === 'mat_ket_noi'
</script>

<template>
  <section class="the">
    <h3 class="tieu-de-khoi">Đội ngũ <router-link class="lk-phai" to="/doi-ngu">Mở Đội ngũ AI →</router-link></h3>
    <p v-if="doiNgu && doiNgu.bat === false" class="nho">Kho phiếu chưa bật</p>
    <template v-else>
      <div class="tq-chibi">
        <router-link v-for="k in khe" :key="k.khe_id" to="/doi-ngu" :title="`${tenKhe(k)} · ${nhanTrangThai(k)}`">
          <Chibi :khe-id="k.khe_id" :mo="mo(k)" /><span>{{ tenKhe(k) }}</span>
        </router-link>
      </div>
      <div class="tq-chip">
        <span v-for="c in dem" :key="c.lop" class="chip" :class="c.lop">{{ c.chu }} · {{ c.n }}</span>
      </div>
      <p v-if="thap" class="tq-thap">
        Hạn mức thấp nhất: <b>{{ tenKhe(thap.khe) }}</b> — 5 giờ còn <b>{{ thap.con }}%</b>, reset {{ thap.reset }}
      </p>
    </template>
  </section>
</template>
```

`frontend/src/thanh/tong_quan/KhoiDuAn.vue` (mới):

```vue
<script setup>
import { gioPhut } from '../../dinh_dang.js'
import { CHU_CHI_QUET_THU } from '../../luat.js'

// Khối "Theo dự án" (mockup trang-tong-quan.js khoiDuAn): số bead cột 1/2/3 từ `so_bead`, việc mới xong (`moi_xong`).
// Dự án `bat_ghi === false` vẽ mờ kèm chip "chỉ quét thử" (D37; mockup ghi "tạm đóng", D37 đổi chữ).
defineProps({ duAn: { type: Array, required: true } })
const COT = ['ai-lam', 'can-chot', 'cho-review']
const so = (d, cot) => (d.so_bead && d.so_bead[cot]) || 0
</script>

<template>
  <section class="the">
    <h3 class="tieu-de-khoi">Theo dự án</h3>
    <p v-if="!duAn.length" class="nho">Chưa có dự án nào.</p>
    <div v-else class="bang-cuon">
      <table class="bang">
        <thead><tr>
          <th>Dự án</th><th>1 · AI làm</th><th>2 · Cần chốt</th><th>3 · Chờ review</th><th>Mới xong</th>
        </tr></thead>
        <tbody>
          <tr v-for="d in duAn" :key="d.ten" :class="{ mo: d.bat_ghi === false }">
            <th>
              <router-link :to="{ path: '/cong-viec', query: { du_an: d.ten } }">{{ d.ten }}</router-link>
              <span v-if="d.bat_ghi === false" class="chip" :title="CHU_CHI_QUET_THU">chỉ quét thử</span>
            </th>
            <td v-for="c in COT" :key="c" class="so">
              <template v-if="so(d, c)">{{ so(d, c) }}</template><span v-else class="nho">0</span>
            </td>
            <td v-if="d.moi_xong">
              <span class="mono tq-xong">{{ d.moi_xong.id }}</span> {{ d.moi_xong.tieu_de }}
              <span class="nho">· {{ gioPhut(d.moi_xong.luc) }}</span>
            </td>
            <td v-else><span class="nho">—</span></td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>
```

`frontend/src/thanh/tong_quan/KhoiSuKien.vue` (mới):

```vue
<script setup>
import { gioPhut } from '../../dinh_dang.js'

// Khối "Sự kiện gần đây" (mockup trang-tong-quan.js khoiSuKien): ≤ 18 sự kiện mới nhất, `mo_ta` dựng ở server (D39).
defineProps({ suKien: { type: Array, required: true } })
const toiBead = (s) => ({ path: '/cong-viec', query: { du_an: s.du_an, bead: s.bead_id } })
</script>

<template>
  <section class="the">
    <h3 class="tieu-de-khoi">Sự kiện gần đây <span class="nho tq-dem">{{ suKien.length }} dòng mới nhất</span></h3>
    <p v-if="!suKien.length" class="nho">Chưa có sự kiện nào.</p>
    <div v-else class="bang-cuon">
      <table class="bang tq-sk">
        <tbody>
          <tr v-for="s in suKien" :key="s.id">
            <td class="mono nho">{{ gioPhut(s.luc) }}</td>
            <td><span class="chip mono">{{ s.loai }}</span></td>
            <td>{{ s.du_an }}</td>
            <td>
              <router-link v-if="s.bead_id" class="mono" :to="toiBead(s)">{{ s.bead_id }}</router-link>
              <span v-else class="nho">—</span>
            </td>
            <td class="nho">{{ s.mo_ta }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>
```

`frontend/src/thanh/tong_quan/KhoiSucKhoe.vue` (mới):

```vue
<script setup>
import { computed } from 'vue'
import { chipDichVu, dongTram } from '../../luat_tong_quan.js'

// Khối "Sức khoẻ trạm" (mockup trang-tong-quan.js khoiSucKhoe): dịch vụ launchd vn.tram.* rồi bốn dòng trạm.
const props = defineProps({ dl: { type: Object, required: true }, bayGio: { type: Date, required: true } })
const dichVu = computed(() => (props.dl.dich_vu || []).map((d) => ({ ...d, chip: chipDichVu(d) })))
const dong = computed(() => dongTram(props.dl, props.bayGio))
</script>

<template>
  <section class="the">
    <h3 class="tieu-de-khoi">Sức khoẻ trạm</h3>
    <ul class="tq-ds">
      <li v-for="d in dichVu" :key="d.nhan">
        <span class="mono">{{ d.nhan }}</span><span class="nho">{{ d.viec }}</span>
        <span class="chip" :class="d.chip.lop">{{ d.chip.chu }}</span>
      </li>
    </ul>
    <ul class="tq-ds tq-ds2">
      <li v-for="[ten, gt, lop] in dong" :key="ten">
        <span>{{ ten }}</span><span class="chip" :class="lop">{{ gt }}</span>
      </li>
    </ul>
  </section>
</template>
```

`frontend/src/thanh/tong_quan/KhoiUsage.vue` (mới):

```vue
<script setup>
import { computed } from 'vue'
import { usageHomNay } from '../../luat_tong_quan.js'

// Khối "Usage hôm nay" (mockup trang-tong-quan.js khoiUsage): bốn ô số + thanh chi phí từng khe (bỏ dòng chấm cột).
const props = defineProps({ usage: { type: Object, default: null } })
const u = computed(() => usageHomNay(props.usage))
</script>

<template>
  <section class="the">
    <h3 class="tieu-de-khoi">Usage hôm nay <router-link class="lk-phai" to="/usage">Chi tiết →</router-link></h3>
    <div class="tq-so">
      <div><b>{{ u.vao }}</b><span class="nho">token vào</span></div>
      <div><b>{{ u.ra }}</b><span class="nho">token ra</span></div>
      <div><b>{{ u.usdKhe }}</b><span class="nho">khe · tương đương</span></div>
      <div><b>{{ u.usdApi }}</b><span class="nho">Claude API chấm cột</span></div>
    </div>
    <div class="tq-cot">
      <div v-for="c in u.cot" :key="c.ma">
        <span class="mono">{{ c.ma }}</span><i :style="{ width: c.rong + '%' }" /><span>{{ c.usd }}</span>
      </div>
    </div>
    <p class="nho tq-chu-thich">
      {{ u.luot }} lượt chạy · giá của khe thuê bao chỉ là tương đương, không phải tiền trả thêm.
    </p>
  </section>
</template>
```

`frontend/src/thanh/tong_quan/KhoiViecCho.vue` (mới):

```vue
<script setup>
import { computed } from 'vue'
import { oViecCho } from '../../luat_tong_quan.js'

// Khối "Việc chờ Đại ca" (mockup trang-tong-quan.js khoiViecCho). Tổng = `phe_duyet.so`, đúng số badge menu
// (D38/Q6); năm ô đếm riêng nên tổng không nhất thiết bằng tổng các ô.
const props = defineProps({ dl: { type: Object, required: true } })
const o = computed(() => oViecCho(props.dl))
const tong = computed(() => (props.dl.phe_duyet && props.dl.phe_duyet.so) || 0)
</script>

<template>
  <section class="the tq-cho">
    <div class="tq-dau">
      <h2>Việc chờ Đại ca</h2><span class="tq-tong">{{ tong }}</span>
      <span class="nho">chờ ở Phê duyệt · sắp theo độ gấp</span>
      <router-link class="nut chinh" to="/phe-duyet">Mở Phê duyệt</router-link>
    </div>
    <div class="tq-o-cho">
      <router-link v-for="x in o" :key="x.ten" class="tq-o" :class="{ rong: !x.so }" :to="x.toi">
        <span class="so" :class="x.so ? x.lop : ''">{{ x.so }}</span>
        <strong>{{ x.ten }}</strong><span class="nho">{{ x.phu }}</span>
      </router-link>
    </div>
    <p v-for="(l, t) in (dl.phe_duyet && dl.phe_duyet.loi) || {}" :key="t" class="loi">{{ t }}: {{ l }}</p>
  </section>
</template>
```

`frontend/src/trang/TongQuan.vue` (thay toàn bộ):

```vue
<script setup>
import { onMounted, onUnmounted, ref, watch } from 'vue'
import { doc } from '../api.js'
import { gioPhut } from '../dinh_dang.js'
import { kho } from '../kho.js'
import '../kieu/tong-quan.css'
import DauTrang from '../thanh/DauTrang.vue'
import KhoiDoiNgu from '../thanh/tong_quan/KhoiDoiNgu.vue'
import KhoiDuAn from '../thanh/tong_quan/KhoiDuAn.vue'
import KhoiSucKhoe from '../thanh/tong_quan/KhoiSucKhoe.vue'
import KhoiSuKien from '../thanh/tong_quan/KhoiSuKien.vue'
import KhoiUsage from '../thanh/tong_quan/KhoiUsage.vue'
import KhoiViecCho from '../thanh/tong_quan/KhoiViecCho.vue'

// Trang mở đầu (D17; mockup trang-tong-quan.js veTongQuan, anh-tong-quan.png). Một API gom `/api/tong-quan` (D38).
// Nhịp tim / hạn mức không phải sự kiện → tải lại mỗi 5 giây như Văn phòng, cộng SSE (phienBan, phienBanDoiNgu).
const CHU_KY_MS = 5000
const dl = ref(null)
const loi = ref('')
const bayGio = ref(new Date())
let hen = null
let luotTai = 0

async function tai() {
  const luot = ++luotTai
  try {
    const moi = await doc('/api/tong-quan')
    if (luot !== luotTai) return          // bỏ kết quả của lượt tải cũ
    dl.value = moi
    bayGio.value = new Date()
    loi.value = ''
  } catch (e) {
    if (luot === luotTai) loi.value = e.message
  }
}
onMounted(() => { tai(); hen = setInterval(tai, CHU_KY_MS) })
onUnmounted(() => { clearInterval(hen); luotTai += 1 })
watch(() => [kho.phienBan, kho.phienBanDoiNgu], tai)
</script>

<template>
  <DauTrang tieu-de="Tổng quan"
            mo-ta="Bức tranh chung của trạm trong một màn. Chỉ đọc; bấm vào từng mục để sang trang xử lý.">
    <template v-if="dl" #cong-cu><span class="nho">cập nhật {{ gioPhut(dl.doc_luc) }}</span></template>
  </DauTrang>
  <p v-if="loi" class="loi" role="alert">{{ loi }}</p>
  <p v-if="!dl && !loi" class="nho">Đang tải…</p>
  <template v-if="dl">
    <KhoiViecCho :dl="dl" />
    <div class="tq-luoi">
      <KhoiSucKhoe :dl="dl" :bay-gio="bayGio" />
      <KhoiDoiNgu :doi-ngu="dl.doi_ngu" :bay-gio="bayGio" />
    </div>
    <div class="tq-luoi tq-luoi-2">
      <KhoiDuAn :du-an="dl.du_an || []" />
      <KhoiUsage :usage="dl.usage" />
    </div>
    <KhoiSuKien :su-kien="dl.su_kien || []" />
  </template>
</template>
```

- [ ] **Step 4: Chạy thấy PASS**

```bash
cd frontend && node --test tests/tong_quan.test.mjs
npm run kiem && npm run build && npm run kiem-dist && cd ..
```

Kỳ vọng: PASS — lệnh test của task: pass 4 · fail 0; toàn bộ tăng đúng 4 node test so với main trước task (bảng "Sơ đồ đợt chạy"); `npm run build`, `npm run kiem-dist` xanh. Số đo trên bản chạy thử.

- [ ] **Step 5: Commit**

```bash
git add frontend/tests/tong_quan.test.mjs frontend/src/kieu/tong-quan.css frontend/src/luat_tong_quan.js frontend/src/thanh/tong_quan/KhoiDoiNgu.vue frontend/src/thanh/tong_quan/KhoiDuAn.vue frontend/src/thanh/tong_quan/KhoiSuKien.vue frontend/src/thanh/tong_quan/KhoiSucKhoe.vue frontend/src/thanh/tong_quan/KhoiUsage.vue frontend/src/thanh/tong_quan/KhoiViecCho.vue frontend/src/trang/TongQuan.vue
git commit -m "feat(dashboard): 2f trang Tổng quan"
```

### Task 14: Trang Cài đặt (chỉ đọc, D19)

**Đợt:** 3 · **Độ khó:** vừa · **Phải xong trước:** Task 1 (Task 6 cho dữ liệu thật) · **Test mới:** 6 node

**Mockup bám:** `trang-cai-dat.js` (bảng sẵn sàng, Dự án đã thêm, Dịch vụ launchd, Telegram, Cờ, Keychain; nút Sao chép có dự phòng `execCommand`), `du-lieu.js` (khối Cài đặt), `style.css` mục "Cài đặt"; ảnh `anh-cai-dat.png`. G13, G29.

**Files:**
- Create: `frontend/src/thanh/LenhCli.vue`, `frontend/src/thanh/cai_dat/KhoiCaiDat.vue`, `BangSanSang.vue`, `KhoiDuAn.vue`, `KhoiDichVu.vue`, `KhoiTelegram.vue`, `KhoiCo.vue`, `KhoiKeychain.vue`, `frontend/src/luat_cai_dat.js`, `frontend/src/kieu/cai-dat.css`
- Modify: `frontend/src/trang/CaiDat.vue` (thay toàn bộ trang giữ chỗ của Task 1)
- Test: `frontend/tests/cai_dat.test.mjs` (mới)

**Interfaces:**
- Consumes: `GET /api/cai-dat`, `GET /api/san-sang` (Task 6), `GET /api/du-an` (`bat_ghi`).
- Lệnh gợi ý là chuỗi hằng (`gui/$(id -u)/…` nguyên văn — không gửi uid thật); API không bao giờ chạy chúng.

403 → thẻ chặn "Chỉ Đại ca xem được Cài đặt". Không có nút sửa nào (chỉ đọc). Keychain chỉ "● có / ○ chưa có / không kiểm được" — không bao giờ hiện giá trị.

- [ ] **Step 1: Viết test (chép nguyên văn)**

`frontend/tests/cai_dat.test.mjs` (mới):

```js
import assert from 'node:assert/strict'
import { test } from 'node:test'
import {
  LENH_CO, LENH_DICH_VU, LENH_KEYCHAIN, LENH_SAN_SANG, LENH_TELEGRAM, cauBatGhi, chuHangRao, demSanSang, ghepBatGhi,
  lenhDuAn, maSanSang, nhanChatId, nhanCo, nhanKeychain, nhanSanSang, oDaCai, oDangChay,
} from '../src/luat_cai_dat.js'

test('lệnh gợi ý: hằng chữ đúng mockup, không chèn uid thật', () => {
  assert.deepEqual(LENH_SAN_SANG.map((l) => l.lenh),
    ['uv run tram giao kiem', 'bd list --status open --label san-sang'])
  assert.equal(LENH_SAN_SANG[0].ghi_chu, 'xanh/vàng/đỏ, mã ≠ 0 nếu có đỏ')
  assert.equal(LENH_DICH_VU[2].lenh, 'launchctl kickstart -k gui/$(id -u)/vn.tram.<tên>')
  assert.equal(LENH_DICH_VU[1].ghi_chu, 'liệt kê thay đổi, Đại ca gõ dong-y')
  assert.equal(LENH_TELEGRAM[1].lenh, 'launchctl kickstart -k gui/$(id -u)/vn.tram.bao-tin')
  assert.equal(LENH_CO[0].ghi_chu, 'vd giao_viec.bat: true — chỉ sau mọi cổng')
  assert.deepEqual(LENH_KEYCHAIN.map((l) => l.ghi_chu), ['tạo tram-noi-bo-token', 'dán trong Terminal.app'])
  assert.equal(LENH_KEYCHAIN[1].lenh, 'security add-generic-password -U -s tram-telegram-bot-token -a tram -w')
})

test('lệnh dự án theo dự án đầu, không có thì <tên>; câu bật ghi D31', () => {
  const ds = [{ ten: 'hr-codex' }, { ten: 'tram' }]
  assert.deepEqual(lenhDuAn(ds), [
    { lenh: '$EDITOR du-an/hr-codex.yaml', ghi_chu: 'sửa khoá rồi chạy lệnh dưới' },
    { lenh: 'uv run tram du-an them <đường dẫn repo>', ghi_chu: '' },
  ])
  assert.equal(lenhDuAn([])[0].lenh, '$EDITOR du-an/<tên>.yaml')
  assert.equal(cauBatGhi(ds), 'sửa tay bat_ghi: true trong du-an/hr-codex.yaml')
  assert.equal(cauBatGhi(undefined), 'sửa tay bat_ghi: true trong du-an/<tên>.yaml')
})

test('sẵn sàng: nhãn + lớp, mã tự kiểm thành —, đếm từ dem hoặc đếm lại', () => {
  assert.deepEqual(nhanSanSang('dat'), { chu: 'Đạt', lop: 'tt-lam' })
  assert.deepEqual(nhanSanSang('thieu'), { chu: 'Thiếu', lop: 'tt-can_nguoi' })
  assert.deepEqual(nhanSanSang('cho'), { chu: 'Chưa tới lượt', lop: 'tt-tat' })
  assert.equal(maSanSang({ ma: 'bs-g28.9', nguon: 'bead' }), 'bs-g28.9')
  assert.equal(maSanSang({ ma: 'ollama', nguon: 'tu_kiem' }), '—')
  assert.deepEqual(demSanSang({ dem: { dat: 3, thieu: 2, cho: 10 } }), { dat: 3, thieu: 2, cho: 10 })
  const muc = [{ trang_thai: 'dat' }, { trang_thai: 'cho' }, { trang_thai: 'cho' }]
  assert.deepEqual(demSanSang({ muc }), { dat: 1, thieu: 0, cho: 2 })
  assert.deepEqual(demSanSang(null), { dat: 0, thieu: 0, cho: 0 })
})

test('dịch vụ: đã cài có/chưa, đang chạy chạy/—/không rõ', () => {
  assert.deepEqual(oDaCai({ da_cai: true }), { chu: 'có', lop: 'tt-lam' })
  assert.deepEqual(oDaCai({ da_cai: false }), { chu: 'chưa', lop: 'tt-tat' })
  assert.deepEqual(oDangChay({ dang_chay: true, kiem_duoc: true }), { chu: 'chạy', lop: 'tt-lam' })
  assert.deepEqual(oDangChay({ dang_chay: false, kiem_duoc: true }), { chu: '—', lop: 'tt-tat' })
  assert.deepEqual(oDangChay({ dang_chay: true, kiem_duoc: false }), { chu: 'không rõ', lop: 'tt-cau_dao' })
  assert.deepEqual(oDangChay({ dang_chay: null, kiem_duoc: true }), { chu: 'không rõ', lop: 'tt-cau_dao' })
})

test('keychain, cờ, chat_id: chỉ nhãn, không bao giờ giá trị bí mật', () => {
  assert.deepEqual(nhanKeychain('co'), { chu: '● có', lop: 'tt-lam' })
  assert.deepEqual(nhanKeychain('chua'), { chu: '○ chưa có', lop: 'tt-can_nguoi' })
  assert.deepEqual(nhanKeychain('khong_ro'), { chu: 'không kiểm được', lop: 'tt-cau_dao' })
  assert.deepEqual(nhanCo({ bat: true, gia_tri: null }), { chu: 'bật', lop: 'tt-lam', mono: false })
  assert.deepEqual(nhanCo({ bat: false, gia_tri: null }), { chu: 'tắt', lop: 'tt-tat', mono: false })
  assert.deepEqual(nhanCo({ bat: null, gia_tri: 'nhanh_rieng' }), { chu: 'nhanh_rieng', lop: '', mono: true })
  assert.deepEqual(nhanCo({ bat: null, gia_tri: null }), { chu: 'chưa chốt', lop: 'tt-cau_dao', mono: false })
  assert.deepEqual(nhanChatId(true), { chu: 'có', lop: 'tt-lam' })
  assert.deepEqual(nhanChatId(false), { chu: 'chưa có', lop: 'tt-can_nguoi' })
})

test('ghép bat_ghi từ /api/du-an: false → chỉ quét thử, thiếu → coi như bật ghi; hàng rào nối phẩy', () => {
  const caiDat = [{ ten: 'hr-codex' }, { ten: 'tram' }, { ten: 'moi' }]
  const duAn = [{ ten: 'hr-codex', bat_ghi: false }, { ten: 'tram', bat_ghi: true }]
  assert.deepEqual(ghepBatGhi(caiDat, duAn).map((d) => d.chi_quet_thu), [true, false, false])
  assert.deepEqual(ghepBatGhi(caiDat, null).map((d) => d.chi_quet_thu), [false, false, false])
  assert.deepEqual(ghepBatGhi(undefined, duAn), [])
  assert.equal(chuHangRao({ loai: 'tien', tu_khoa: ['hoàn tiền', 'thuế'], duong_dan: ['billing/'] }),
    'hoàn tiền, thuế, billing/')
  assert.equal(chuHangRao({ loai: 'schema', tu_khoa: [], duong_dan: [] }), '')
})
```

- [ ] **Step 2: Chạy thấy FAIL**

```bash
cd frontend && node --test tests/cai_dat.test.mjs
```

Kỳ vọng: FAIL — `Error [ERR_MODULE_NOT_FOUND]: Cannot find module '…/frontend/src/luat_cai_dat.js' imported from …/frontend/tests/cai_dat.test.mjs`

- [ ] **Step 3: Viết mã (chép nguyên văn; file sửa: chép khối diff ra file tạm, `git apply --check` rồi `git apply`)**

`frontend/src/kieu/cai-dat.css` (mới):

```css
/* Trang Cài đặt (D19) — chép từ mockup style.css mục "Cài đặt"; .tq-ds/.tq-chip bó trong .cd-khoi. */
.cd-luoi {
  display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; align-items: start; margin-top: 16px;
}
.cd-luoi > .cd-khoi:first-child { grid-column: 1 / -1; }
.cd-dau { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin-bottom: 10px; }
.cd-dau h3 { margin: 0; font-size: 16px; }
.cd-dem { margin-left: auto; }
.cd-lenh {
  margin-top: 12px; padding-top: 10px; border-top: 1px dashed var(--vien-dam);
  display: flex; flex-direction: column; gap: 6px;
}
.lenh { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.lenh code {
  font-family: var(--mono); font-size: 12.5px; background: var(--nen-lenh); color: var(--chu-lenh);
  padding: 5px 10px; border-radius: 7px; overflow-wrap: anywhere;
}
.sao-chep {
  border: 1px solid var(--vien-dam); background: var(--the); border-radius: 6px; font-size: 12px; padding: 3px 8px;
  color: var(--chu-2);
}
.sao-chep:hover { border-color: var(--nhan); color: var(--nhan); }
.cd-du-an { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 12px; }
.cd-da { border: 1px solid var(--vien); border-radius: 10px; padding: 10px 12px; background: var(--nen-3); }
.cd-da.mo { opacity: .6; }
.cd-da-dau { display: flex; gap: 8px; align-items: center; margin-bottom: 6px; }
.cd-da dl, .cd-dl { display: grid; grid-template-columns: 110px 1fr; gap: 6px 10px; margin: 0; font-size: 13px; }
.cd-da dt, .cd-dl dt { color: var(--chu-phu); }
.cd-da dd, .cd-dl dd { margin: 0; }
.cd-da dd .mono, .cd-da dd.mono { font-size: 12.5px; }
.cd-khoi .tq-chip { display: flex; gap: 6px; flex-wrap: wrap; }
.cd-khoi .tq-ds { list-style: none; margin: 0; padding: 0; }
.cd-khoi .tq-ds li {
  display: grid; grid-template-columns: minmax(0, auto) 1fr auto; gap: 10px; align-items: center; padding: 7px 0;
  border-bottom: 1px solid var(--vien); font-size: 13.5px;
}
.cd-khoi .tq-ds li:last-child { border-bottom: 0; }
.cd-khoi .tq-ds .mono { font-size: 12.5px; }
.cot-den { width: 28px; }
.ma-ss { color: var(--nhan); white-space: nowrap; }
.den-ss { display: inline-block; width: 12px; height: 12px; border-radius: 50%; }
.den-ss.dat { background: var(--xanh); box-shadow: 0 0 0 3px #4f9a6a22; }
.den-ss.thieu { background: var(--do); box-shadow: 0 0 0 3px #b8392b22; }
.den-ss.cho { background: #c9c2ba; }
@media (max-width: 1100px) { .cd-luoi { grid-template-columns: 1fr; } }
```

`frontend/src/luat_cai_dat.js` (mới):

```js
// Luật thuần của trang Cài đặt (D19 — chỉ đọc). Mockup trang-cai-dat.js, khảo sát §1.6.
// Lệnh CLI là hằng chữ phía trình duyệt: trạm KHÔNG chạy, chỉ hiện để Đại ca tự chạy; `gui/$(id -u)` giữ nguyên văn.
import { duAnChiQuetThu } from './luat.js'

const l = (lenh, ghiChu = '') => ({ lenh, ghi_chu: ghiChu })

export const LENH_SAN_SANG = [
  l('uv run tram giao kiem', 'xanh/vàng/đỏ, mã ≠ 0 nếu có đỏ'),
  l('bd list --status open --label san-sang'),
]
export const LENH_DICH_VU = [
  l('uv run tram chu trang-thai'),
  l('uv run tram chu cai-dat', 'liệt kê thay đổi, Đại ca gõ dong-y'),
  l('launchctl kickstart -k gui/$(id -u)/vn.tram.<tên>', 'chạy lại một dịch vụ đã cài'),
]
export const LENH_TELEGRAM = [
  l('$EDITOR ~/.tram/cau-hinh.yaml'),
  l('launchctl kickstart -k gui/$(id -u)/vn.tram.bao-tin'),
]
export const LENH_CO = [l('$EDITOR ~/.tram/cau-hinh.yaml', 'vd giao_viec.bat: true — chỉ sau mọi cổng')]
export const LENH_KEYCHAIN = [
  l('uv run tram chu cai-dat --nho', 'tạo tram-noi-bo-token'),
  l('security add-generic-password -U -s tram-telegram-bot-token -a tram -w', 'dán trong Terminal.app'),
]

// Dự án đầu danh sách làm ví dụ; chưa có dự án nào thì giữ chỗ `<tên>`.
const tenDau = (ds) => (ds && ds.length ? ds[0].ten : '<tên>')
export function lenhDuAn(ds) {
  return [
    l(`$EDITOR du-an/${tenDau(ds)}.yaml`, 'sửa khoá rồi chạy lệnh dưới'),
    l('uv run tram du-an them <đường dẫn repo>'),
  ]
}
// Bật ghi chỉ sửa tay file YAML (D31/G25) — không có lệnh CLI riêng.
export const cauBatGhi = (ds) => `sửa tay bat_ghi: true trong du-an/${tenDau(ds)}.yaml`

const NHAN_SAN_SANG = {
  dat: { chu: 'Đạt', lop: 'tt-lam' },
  thieu: { chu: 'Thiếu', lop: 'tt-can_nguoi' },
  cho: { chu: 'Chưa tới lượt', lop: 'tt-tat' },
}
export const nhanSanSang = (tt) => NHAN_SAN_SANG[tt] || { chu: String(tt), lop: 'tt-tat' }
// Mục tự kiểm (không phải bead, vd Ollama) hiện "—" như mockup.
export const maSanSang = (m) => (m.nguon === 'tu_kiem' ? '—' : m.ma)

export function demSanSang(ss) {
  if (ss && ss.dem) return { dat: ss.dem.dat || 0, thieu: ss.dem.thieu || 0, cho: ss.dem.cho || 0 }
  const dem = { dat: 0, thieu: 0, cho: 0 }
  for (const m of (ss && ss.muc) || []) if (m.trang_thai in dem) dem[m.trang_thai] += 1
  return dem
}

const KHONG_RO = { chu: 'không rõ', lop: 'tt-cau_dao' }
export function oDaCai(d) {
  if (typeof d.da_cai !== 'boolean') return KHONG_RO
  return d.da_cai ? { chu: 'có', lop: 'tt-lam' } : { chu: 'chưa', lop: 'tt-tat' }
}
// `kiem_duoc: false` = launchctl không trả lời được → không đoán.
export function oDangChay(d) {
  if (d.kiem_duoc === false || typeof d.dang_chay !== 'boolean') return KHONG_RO
  return d.dang_chay ? { chu: 'chạy', lop: 'tt-lam' } : { chu: '—', lop: 'tt-tat' }
}

const NHAN_KEYCHAIN = {
  co: { chu: '● có', lop: 'tt-lam' },
  chua: { chu: '○ chưa có', lop: 'tt-can_nguoi' },
}
export const nhanKeychain = (tt) => NHAN_KEYCHAIN[tt] || { chu: 'không kiểm được', lop: 'tt-cau_dao' }

// Cờ: giá trị chuỗi (vd phương án công bố) ưu tiên; null cả hai = chưa chốt.
export function nhanCo(c) {
  if (c.gia_tri != null) return { chu: String(c.gia_tri), lop: '', mono: true }
  if (c.bat === true) return { chu: 'bật', lop: 'tt-lam', mono: false }
  if (c.bat === false) return { chu: 'tắt', lop: 'tt-tat', mono: false }
  return { chu: 'chưa chốt', lop: 'tt-cau_dao', mono: false }
}
export const nhanChatId = (co) => (co ? { chu: 'có', lop: 'tt-lam' } : { chu: 'chưa có', lop: 'tt-can_nguoi' })

// /api/cai-dat không có bat_ghi → lấy từ /api/du-an (D37); thiếu coi như bật ghi.
export function ghepBatGhi(dsCaiDat, dsDuAn) {
  const chiQuet = duAnChiQuetThu(dsDuAn)
  return (dsCaiDat || []).map((d) => ({ ...d, chi_quet_thu: chiQuet.has(d.ten) }))
}
export const chuHangRao = (h) => [...(h.tu_khoa || []), ...(h.duong_dan || [])].join(', ')
```

`frontend/src/thanh/LenhCli.vue` (mới):

```vue
<script setup>
import { onBeforeUnmount, ref } from 'vue'

// Một lệnh CLI gợi ý + nút "Sao chép" (mockup trang-cai-dat.js `lenh`, D19). Chỉ chép chữ — không chạy gì.
const props = defineProps({ lenh: { type: String, required: true }, ghiChu: { type: String, default: '' } })
const chu = ref('Sao chép')
let hen = null

// Dự phòng khi Clipboard API bị chặn (không HTTPS/không quyền): textarea tạm + execCommand như mockup.
function chepDuPhong(van) {
  const t = document.createElement('textarea')
  t.value = van
  document.body.appendChild(t)
  t.select()
  let ok = false
  try {
    ok = document.execCommand('copy')
  } catch {
    ok = false
  }
  t.remove()
  return ok
}

async function chep() {
  let ok = false
  try {
    await navigator.clipboard.writeText(props.lenh)
    ok = true
  } catch {
    ok = chepDuPhong(props.lenh)
  }
  chu.value = ok ? 'Đã chép' : 'Không chép được'
  clearTimeout(hen)
  hen = setTimeout(() => { chu.value = 'Sao chép' }, 1400)
}
onBeforeUnmount(() => clearTimeout(hen))
</script>

<template>
  <div class="lenh">
    <code>{{ lenh }}</code>
    <button type="button" class="sao-chep" title="Sao chép lệnh" @click="chep">{{ chu }}</button>
    <span v-if="ghiChu" class="nho">{{ ghiChu }}</span>
  </div>
</template>
```

`frontend/src/thanh/cai_dat/BangSanSang.vue` (mới):

```vue
<script setup>
import { computed } from 'vue'
import { LENH_SAN_SANG, demSanSang, maSanSang, nhanSanSang } from '../../luat_cai_dat.js'
import KhoiCaiDat from './KhoiCaiDat.vue'

// Bảng sẵn sàng chạy thật (mockup trang-cai-dat.js `bangSanSang`, ảnh anh-cai-dat.png). Dữ liệu GET /api/san-sang.
// Hai lệnh "Kiểm lại" chỉ hiện để Đại ca tự chạy — API không bao giờ chạy chúng.
const props = defineProps({ ss: { type: Object, required: true } })
const dem = computed(() => demSanSang(props.ss))
</script>

<template>
  <KhoiCaiDat tieu-de="Bảng sẵn sàng chạy thật" :lenh="LENH_SAN_SANG" nhan-lenh="Kiểm lại:">
    <template #phu>theo sổ tay <span class="mono">docs/handovers/2026-10-15-so-tay-chay-that.md</span></template>
    <template #dau>
      <div class="tq-chip cd-dem">
        <span class="chip tt-lam">{{ dem.dat }} đạt</span>
        <span class="chip tt-can_nguoi">{{ dem.thieu }} thiếu</span>
        <span class="chip tt-tat">{{ dem.cho }} chưa tới lượt</span>
      </div>
    </template>
    <p v-if="ss.loi" class="canh-bao">{{ ss.loi }}</p>
    <div class="bang-cuon">
      <table class="bang">
        <thead><tr><th class="cot-den" /><th>Bead</th><th>Bước</th><th>Trạng thái</th><th>Ghi chú</th></tr></thead>
        <tbody>
          <tr v-for="(m, i) in ss.muc || []" :key="m.ma + i">
            <td><span class="den-ss" :class="m.trang_thai" /></td>
            <td class="mono ma-ss">{{ maSanSang(m) }}</td>
            <td>{{ m.ten }}</td>
            <td>
              <span class="chip" :class="nhanSanSang(m.trang_thai).lop">{{ nhanSanSang(m.trang_thai).chu }}</span>
            </td>
            <td class="nho">{{ m.ghi_chu }}</td>
          </tr>
          <tr v-if="!(ss.muc || []).length"><td colspan="5" class="nho">Chưa có mục nào.</td></tr>
        </tbody>
      </table>
    </div>
  </KhoiCaiDat>
</template>
```

`frontend/src/thanh/cai_dat/KhoiCaiDat.vue` (mới):

```vue
<script setup>
import LenhCli from '../LenhCli.vue'
import '../../kieu/cai-dat.css'

// Khung một khối Cài đặt (mockup trang-cai-dat.js `khoi`): tiêu đề + phụ + thân + danh sách lệnh CLI gợi ý.
// Slot `phu` thay chữ phụ khi cần đoạn mono; slot `dau` thêm đồ bên phải tiêu đề; slot `sau-lenh` thêm ghi chú.
defineProps({
  tieuDe: { type: String, required: true },
  phu: { type: String, default: '' },
  lenh: { type: Array, default: () => [] },
  nhanLenh: { type: String, default: 'Sửa bằng CLI:' },
})
</script>

<template>
  <section class="the cd-khoi">
    <div class="cd-dau">
      <h3>{{ tieuDe }}</h3>
      <span v-if="phu || $slots.phu" class="nho"><slot name="phu">{{ phu }}</slot></span>
      <slot name="dau" />
    </div>
    <slot />
    <div v-if="lenh.length" class="cd-lenh">
      <span class="nho">{{ nhanLenh }}</span>
      <LenhCli v-for="l in lenh" :key="l.lenh" :lenh="l.lenh" :ghi-chu="l.ghi_chu" />
      <slot name="sau-lenh" />
    </div>
  </section>
</template>
```

`frontend/src/thanh/cai_dat/KhoiCo.vue` (mới):

```vue
<script setup>
import { LENH_CO, nhanCo } from '../../luat_cai_dat.js'
import KhoiCaiDat from './KhoiCaiDat.vue'

// Cờ (mockup trang-cai-dat.js `co`): khoá mono, ghi chú, chip bật/tắt hoặc giá trị chuỗi; null → "chưa chốt".
defineProps({ ds: { type: Array, required: true } })
</script>

<template>
  <KhoiCaiDat tieu-de="Cờ" :lenh="LENH_CO">
    <ul class="tq-ds">
      <li v-for="c in ds" :key="c.khoa">
        <span class="mono">{{ c.khoa }}</span>
        <span class="nho">{{ c.ghi_chu }}</span>
        <span class="chip" :class="[nhanCo(c).lop, { mono: nhanCo(c).mono }]">{{ nhanCo(c).chu }}</span>
      </li>
    </ul>
  </KhoiCaiDat>
</template>
```

`frontend/src/thanh/cai_dat/KhoiDichVu.vue` (mới):

```vue
<script setup>
import { LENH_DICH_VU, oDaCai, oDangChay } from '../../luat_cai_dat.js'
import KhoiCaiDat from './KhoiCaiDat.vue'

// Dịch vụ launchd (mockup trang-cai-dat.js `dichVu`). `kiem_duoc: false` → "không rõ", không đoán.
defineProps({ ds: { type: Array, required: true } })
</script>

<template>
  <KhoiCaiDat tieu-de="Dịch vụ launchd" :lenh="LENH_DICH_VU">
    <template #phu>LaunchAgent trong <span class="mono">~/Library/LaunchAgents</span></template>
    <div class="bang-cuon">
      <table class="bang">
        <thead><tr><th>Dịch vụ</th><th>Việc</th><th>Đã cài</th><th>Đang chạy</th></tr></thead>
        <tbody>
          <tr v-for="d in ds" :key="d.nhan">
            <td class="mono">{{ d.nhan }}</td>
            <td class="nho">{{ d.viec }}</td>
            <td><span class="chip" :class="oDaCai(d).lop">{{ oDaCai(d).chu }}</span></td>
            <td><span class="chip" :class="oDangChay(d).lop">{{ oDangChay(d).chu }}</span></td>
          </tr>
        </tbody>
      </table>
    </div>
  </KhoiCaiDat>
</template>
```

`frontend/src/thanh/cai_dat/KhoiDuAn.vue` (mới):

```vue
<script setup>
import { CHU_CHI_QUET_THU } from '../../luat.js'
import { cauBatGhi, chuHangRao, lenhDuAn } from '../../luat_cai_dat.js'
import KhoiCaiDat from './KhoiCaiDat.vue'

// Dự án đã thêm (mockup trang-cai-dat.js `duAn`). `ds` đã ghép `chi_quet_thu` từ /api/du-an (D37) → mờ + chip.
defineProps({ ds: { type: Array, required: true } })
</script>

<template>
  <KhoiCaiDat tieu-de="Dự án đã thêm" :lenh="lenhDuAn(ds)">
    <template #phu>{{ ds.length }} dự án · <span class="mono">du-an/*.yaml</span></template>
    <div class="cd-du-an">
      <div v-for="d in ds" :key="d.ten" class="cd-da" :class="{ mo: d.chi_quet_thu }">
        <div class="cd-da-dau">
          <strong>{{ d.ten }}</strong>
          <span v-if="d.chi_quet_thu" class="chip" :title="CHU_CHI_QUET_THU">chỉ quét thử</span>
        </div>
        <dl>
          <dt>Đường dẫn</dt><dd class="mono">{{ d.duong_dan }}</dd>
          <dt>Nhánh chính</dt><dd class="mono">{{ d.nhanh_chinh }}</dd>
          <dt>GitNexus</dt>
          <dd><span v-if="d.gitnexus" class="mono">{{ d.gitnexus }}</span><span v-else class="nho">không</span></dd>
          <dt>Lệnh được phép</dt>
          <dd class="tq-chip"><span v-for="l in d.lenh_cho_phep" :key="l" class="chip mono">{{ l }}</span></dd>
          <dt>Hàng rào</dt>
          <dd>
            <div v-for="h in d.hang_rao" :key="h.loai">
              <span class="chip mono">{{ h.loai }}</span> <span class="nho">{{ chuHangRao(h) }}</span>
            </div>
          </dd>
          <dt>Môi trường kiểm</dt><dd>{{ d.moi_truong_kiem ? 'có' : 'chưa' }}</dd>
        </dl>
        <p v-if="d.loi" class="canh-bao">{{ d.loi }}</p>
      </div>
      <p v-if="!ds.length" class="nho">Chưa thêm dự án nào.</p>
    </div>
    <template #sau-lenh>
      <span class="nho">Bật ghi (D31): {{ cauBatGhi(ds) }}</span>
    </template>
  </KhoiCaiDat>
</template>
```

`frontend/src/thanh/cai_dat/KhoiKeychain.vue` (mới):

```vue
<script setup>
import { LENH_KEYCHAIN, nhanKeychain } from '../../luat_cai_dat.js'
import KhoiCaiDat from './KhoiCaiDat.vue'

// Keychain (mockup trang-cai-dat.js `kc`): chỉ có / chưa có / không kiểm được — không bao giờ hiện giá trị.
defineProps({ ds: { type: Array, required: true } })
</script>

<template>
  <KhoiCaiDat tieu-de="Keychain" phu="chỉ hiện có / chưa có — không bao giờ hiện giá trị" :lenh="LENH_KEYCHAIN">
    <ul class="tq-ds">
      <li v-for="k in ds" :key="k.ten">
        <span class="mono">{{ k.ten }}</span>
        <span />
        <span class="chip" :class="nhanKeychain(k.trang_thai).lop">{{ nhanKeychain(k.trang_thai).chu }}</span>
      </li>
    </ul>
  </KhoiCaiDat>
</template>
```

`frontend/src/thanh/cai_dat/KhoiTelegram.vue` (mới):

```vue
<script setup>
import { LENH_TELEGRAM, nhanChatId } from '../../luat_cai_dat.js'
import KhoiCaiDat from './KhoiCaiDat.vue'

// Telegram (mockup trang-cai-dat.js `tele`). chat_id chỉ hiện có / chưa có — API không trả giá trị.
defineProps({ tg: { type: Object, required: true } })
</script>

<template>
  <KhoiCaiDat tieu-de="Telegram" :lenh="LENH_TELEGRAM">
    <template #phu>
      khoá <span class="mono">telegram:</span> trong <span class="mono">~/.tram/cau-hinh.yaml</span>
    </template>
    <dl class="cd-dl">
      <dt>chat_id</dt>
      <dd><span class="chip" :class="nhanChatId(tg.co_chat_id).lop">{{ nhanChatId(tg.co_chat_id).chu }}</span></dd>
      <dt>Giờ yên lặng</dt>
      <dd v-if="tg.gio_yen_lang">{{ tg.gio_yen_lang }}</dd>
      <dd v-else class="nho">không đặt</dd>
      <dt>Loại tin</dt>
      <dd class="tq-chip"><span v-for="l in tg.loai_tin || []" :key="l" class="chip">{{ l }}</span></dd>
    </dl>
  </KhoiCaiDat>
</template>
```

`frontend/src/trang/CaiDat.vue` (thay toàn bộ):

```vue
<script setup>
import { computed, onMounted, ref } from 'vue'
import { doc } from '../api.js'
import { ghepBatGhi } from '../luat_cai_dat.js'
import DauTrang from '../thanh/DauTrang.vue'
import BangSanSang from '../thanh/cai_dat/BangSanSang.vue'
import KhoiCo from '../thanh/cai_dat/KhoiCo.vue'
import KhoiDichVu from '../thanh/cai_dat/KhoiDichVu.vue'
import KhoiDuAn from '../thanh/cai_dat/KhoiDuAn.vue'
import KhoiKeychain from '../thanh/cai_dat/KhoiKeychain.vue'
import KhoiTelegram from '../thanh/cai_dat/KhoiTelegram.vue'
import '../kieu/cai-dat.css'

// Trang Cài đặt — CHỈ ĐỌC (D19; mockup trang-cai-dat.js, ảnh anh-cai-dat.png).
// Chỉ Đại ca xem (D38/Q13): 403 → thẻ chặn.
// Không SSE: "Kiểm lại" tải lại hai API. bat_ghi lấy từ /api/du-an (D37); lỗi đọc thì coi như bật ghi.
const caiDat = ref(null)
const sanSang = ref(null)
const duAn = ref(null)
const cam = ref(false)
const loi = ref('')
const dangTai = ref(false)
const dsDuAn = computed(() => ghepBatGhi(caiDat.value && caiDat.value.du_an, duAn.value))

async function tai() {
  dangTai.value = true
  try {
    const [c, s, d] = await Promise.all([
      doc('/api/cai-dat'), doc('/api/san-sang'), doc('/api/du-an').catch(() => null),
    ])
    caiDat.value = c
    sanSang.value = s
    duAn.value = d && d.du_an
    cam.value = false
    loi.value = ''
  } catch (e) {
    cam.value = e.status === 403
    loi.value = cam.value ? '' : e.message
  } finally {
    dangTai.value = false
  }
}
onMounted(tai)
</script>

<template>
  <DauTrang
    tieu-de="Cài đặt"
    mo-ta="Chỉ đọc. Không sửa được qua web; mỗi mục kèm lệnh CLI gợi ý để Đại ca tự chạy trên máy B."
  >
    <template #cong-cu>
      <span class="chip">chỉ đọc</span>
      <button type="button" class="nut" :disabled="dangTai" @click="tai">Kiểm lại</button>
    </template>
  </DauTrang>
  <section v-if="cam" class="the the-chan" role="alert">
    <strong>403 · Chỉ Đại ca xem được Cài đặt</strong>
    <p>Trang này cần danh tính Tailscale của Đại ca. Máy hoặc tài khoản khác không đọc được cấu hình trạm.</p>
  </section>
  <template v-else>
    <p v-if="loi" class="loi" role="alert">{{ loi }}</p>
    <p v-if="!caiDat && !loi" class="nho">Đang đọc cấu hình…</p>
    <BangSanSang v-if="sanSang" :ss="sanSang" />
    <template v-if="caiDat">
      <div class="cd-luoi">
        <KhoiDuAn :ds="dsDuAn" />
        <KhoiDichVu :ds="caiDat.dich_vu || []" />
        <KhoiTelegram :tg="caiDat.telegram || {}" />
        <KhoiCo :ds="caiDat.co || []" />
        <KhoiKeychain :ds="caiDat.keychain || []" />
      </div>
      <p v-for="(l, i) in caiDat.loi_cau_hinh || []" :key="i" class="canh-bao">{{ l }}</p>
    </template>
  </template>
</template>
```

- [ ] **Step 4: Chạy thấy PASS**

```bash
cd frontend && node --test tests/cai_dat.test.mjs
npm run kiem && npm run build && npm run kiem-dist && cd ..
```

Kỳ vọng: PASS — lệnh test của task: pass 6 · fail 0; toàn bộ tăng đúng 6 node test so với main trước task (bảng "Sơ đồ đợt chạy"); `npm run build`, `npm run kiem-dist` xanh. Số đo trên bản chạy thử.

- [ ] **Step 5: Commit**

```bash
git add frontend/tests/cai_dat.test.mjs frontend/src/kieu/cai-dat.css frontend/src/luat_cai_dat.js frontend/src/thanh/LenhCli.vue frontend/src/thanh/cai_dat/BangSanSang.vue frontend/src/thanh/cai_dat/KhoiCaiDat.vue frontend/src/thanh/cai_dat/KhoiCo.vue frontend/src/thanh/cai_dat/KhoiDichVu.vue frontend/src/thanh/cai_dat/KhoiDuAn.vue frontend/src/thanh/cai_dat/KhoiKeychain.vue frontend/src/thanh/cai_dat/KhoiTelegram.vue frontend/src/trang/CaiDat.vue
git commit -m "feat(dashboard): 2f trang Cài đặt chỉ đọc"
```

### Task 15: Trang Dự án

**Đợt:** 3 · **Độ khó:** dễ · **Phải xong trước:** Task 1 · **Test mới:** 2 node

**Mockup bám:** `trang.js` (`veDuAn`), `style.css` `.ds-phong`, `.the-phong`. Khảo sát §1.7.

**Files:**
- Create: `frontend/src/luat_du_an.js` (`theDuAn(d)`), `frontend/src/kieu/du-an.css`
- Modify: `frontend/src/trang/DuAn.vue` (viết lại: bảng → lưới thẻ)
- Test: `frontend/tests/du_an.test.mjs` (mới)

**Interfaces:** Consumes `/api/du-an` (`bat_ghi`), `gioPhut`. Giữ chip "Chưa chấm · n" khi > 0 (D36) và `loi_doc`; dự án chỉ quét thử → `.mo` + chip "chỉ quét thử".

- [ ] **Step 1: Viết test (chép nguyên văn)**

`frontend/tests/du_an.test.mjs` (mới):

```js
import assert from 'node:assert/strict'
import { test } from 'node:test'
import { theDuAn } from '../src/luat_du_an.js'

const goc = { ten: 'ben-web', quet_cuoi: '2026-10-15T15:14:00Z', loi_gan_nhat: null, loi_doc: '',
  so_bead: { 'ai-lam': 2, 'can-chot': 1, 'cho-review': 0, 'chua-cham': 3 } }

test('theDuAn dựng link, giờ quét, chip 1·2·3 và chip chưa chấm', () => {
  const t = theDuAn(goc)
  assert.equal(t.den, '/cong-viec?du_an=ben-web')
  assert.match(t.quet, /^quét cuối \d\d:\d\d$/)
  assert.deepEqual(t.chip.map((c) => c.chu), ['1 · 2', '2 · 1', '3 · 0'])
  assert.equal(t.chuaCham, 'Chưa chấm · 3')
  assert.equal(t.loiGanNhat, 'Lỗi gần nhất: không có')
  assert.equal(t.chiQuetThu, false)
})

test('theDuAn: chưa quét, hết chưa chấm, lỗi gần nhất + loi_doc, chỉ quét thử', () => {
  const t = theDuAn({ ten: 'a b', quet_cuoi: null, bat_ghi: false, loi_doc: 'không đọc được bead',
    loi_gan_nhat: { luc: '2026-10-15T15:20:00Z', loai: 'quet', loi: 'bd lỗi' }, so_bead: {} })
  assert.equal(t.den, '/cong-viec?du_an=a%20b')
  assert.equal(t.quet, 'chưa quét')
  assert.equal(t.chuaCham, '')
  assert.deepEqual(t.chip.map((c) => c.chu), ['1 · 0', '2 · 0', '3 · 0'])
  assert.match(t.loiGanNhat, /^Lỗi gần nhất: \d\d:\d\d · bd lỗi$/)
  assert.equal(t.loiDoc, 'không đọc được bead')
  assert.equal(t.chiQuetThu, true)
})
```

- [ ] **Step 2: Chạy thấy FAIL**

```bash
cd frontend && node --test tests/du_an.test.mjs
```

Kỳ vọng: FAIL — `Error [ERR_MODULE_NOT_FOUND]: Cannot find module '…/frontend/src/luat_du_an.js' imported from …/frontend/tests/du_an.test.mjs`

- [ ] **Step 3: Viết mã (chép nguyên văn; file sửa: chép khối diff ra file tạm, `git apply --check` rồi `git apply`)**

`frontend/src/kieu/du-an.css` (mới):

```css
/* Trang Dự án — chép .ds-phong / .the-phong của mockup style.css (mục Văn phòng). */
.ds-du-an { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 12px; }
.the-du-an {
  cursor: pointer; display: flex; flex-direction: column; gap: 8px; border-left: 6px solid var(--nhan);
  text-decoration: none; color: inherit;
}
.the-du-an:hover { border-color: var(--vien-dam); border-left-color: var(--nhan); box-shadow: 0 4px 14px #6b4a3014; }
.the-du-an .dau { display: flex; align-items: center; gap: 8px; }
.the-du-an .dau strong { font-size: 15.5px; }
.the-du-an .dau .nho { margin-left: auto; }
.the-du-an .ds-chip { display: flex; flex-wrap: wrap; gap: 6px; }
```

`frontend/src/luat_du_an.js` (mới):

```js
// Dựng dữ liệu một thẻ dự án từ phần tử /api/du-an (mockup trang.js veDuAn, D36, D37).
import { gioPhut } from './dinh_dang.js'

// Ba chip cột: 1 = ai-lam, 2 = can-chot, 3 = cho-review (mockup đếm cột 1/2/3).
const COT_CHIP = ['ai-lam', 'can-chot', 'cho-review']

export function theDuAn(d) {
  const sb = d.so_bead || {}
  const lg = d.loi_gan_nhat
  return {
    ten: d.ten,
    den: '/cong-viec?du_an=' + encodeURIComponent(d.ten),
    quet: d.quet_cuoi ? 'quét cuối ' + gioPhut(d.quet_cuoi) : 'chưa quét',
    chip: COT_CHIP.map((h, i) => ({ chu: `${i + 1} · ${sb[h] || 0}` })),
    // Bản thật có hàng chưa chấm, mockup không vẽ (D36): giữ khi > 0.
    chuaCham: sb['chua-cham'] > 0 ? `Chưa chấm · ${sb['chua-cham']}` : '',
    loiGanNhat: 'Lỗi gần nhất: ' + (lg ? `${gioPhut(lg.luc)} · ${lg.loi}` : 'không có'),
    loiDoc: d.loi_doc || '',
    chiQuetThu: d.bat_ghi === false, // D37: "chỉ quét thử", không dùng chữ "tạm đóng"
  }
}
```

`frontend/src/trang/DuAn.vue` (sửa):

```diff
diff --git a/frontend/src/trang/DuAn.vue b/frontend/src/trang/DuAn.vue
index ff7bb3e..5c00d9b 100644
--- a/frontend/src/trang/DuAn.vue
+++ b/frontend/src/trang/DuAn.vue
@@ -1,12 +1,16 @@
 <script setup>
-import { onMounted, ref, watch } from 'vue'
+// Trang Dự án — mockup trang.js veDuAn: lưới thẻ, mỗi thẻ dẫn tới /cong-viec?du_an=<ten>.
+import { computed, onMounted, ref, watch } from 'vue'
 import { doc } from '../api.js'
 import { kho } from '../kho.js'
-import { TEN_HANG, gioVN } from '../luat.js'
+import { theDuAn } from '../luat_du_an.js'
+import { CHU_CHI_QUET_THU } from '../luat.js'
+import DauTrang from '../thanh/DauTrang.vue'
+import '../kieu/du-an.css'
 
-const COT_HIEN = ['ai-lam', 'can-chot', 'cho-review', 'chua-cham']
 const ds = ref([])
 const loi = ref('')
+const the = computed(() => ds.value.map(theDuAn))
 
 async function tai() {
   try {
@@ -21,23 +25,24 @@ watch(() => kho.phienBan, tai)
 </script>
 
 <template>
-  <section>
-    <h1>Dự án</h1>
-    <p v-if="loi" class="loi" role="alert">{{ loi }}</p>
-    <p v-if="!ds.length && !loi" class="nho">Chưa có dự án nào trong du-an/.</p>
-    <div v-if="ds.length" class="bang-cuon">
-      <table>
-        <thead><tr>
-          <th scope="col">Dự án</th><th v-for="h in COT_HIEN" :key="h" scope="col">{{ TEN_HANG[h] }}</th>
-          <th scope="col">Quét cuối</th><th scope="col">Lỗi gần nhất</th>
-        </tr></thead>
-        <tbody><tr v-for="d in ds" :key="d.ten">
-          <th scope="row">{{ d.ten }}</th>
-          <td v-for="h in COT_HIEN" :key="h">{{ d.so_bead[h] }}</td>
-          <td>{{ d.quet_cuoi ? gioVN(d.quet_cuoi) : 'chưa' }}</td>
-          <td>{{ d.loi_doc || (d.loi_gan_nhat ? gioVN(d.loi_gan_nhat.luc) + ' · ' + d.loi_gan_nhat.loi : 'không') }}</td>
-        </tr></tbody>
-      </table>
-    </div>
-  </section>
+  <DauTrang
+    tieu-de="Dự án"
+    mo-ta="Các dự án đã thêm vào trạm: số bead mỗi cột, lần quét cuối, lỗi gần nhất."
+  />
+  <p v-if="loi" class="loi" role="alert">{{ loi }}</p>
+  <p v-if="!the.length && !loi" class="nho">Chưa có dự án nào trong du-an/.</p>
+  <div v-if="the.length" class="ds-du-an">
+    <router-link
+      v-for="t in the" :key="t.ten" :to="t.den" class="the the-du-an" :class="{ mo: t.chiQuetThu }"
+    >
+      <div class="dau"><strong>{{ t.ten }}</strong><span class="nho">{{ t.quet }}</span></div>
+      <div class="ds-chip">
+        <span v-for="c in t.chip" :key="c.chu" class="chip">{{ c.chu }}</span>
+        <span v-if="t.chuaCham" class="chip">{{ t.chuaCham }}</span>
+        <span v-if="t.chiQuetThu" class="chip" :title="CHU_CHI_QUET_THU">chỉ quét thử</span>
+      </div>
+      <div class="nho">{{ t.loiGanNhat }}</div>
+      <div v-if="t.loiDoc" class="loi">{{ t.loiDoc }}</div>
+    </router-link>
+  </div>
 </template>
```

- [ ] **Step 4: Chạy thấy PASS**

```bash
cd frontend && node --test tests/du_an.test.mjs
npm run kiem && npm run build && npm run kiem-dist && cd ..
```

Kỳ vọng: PASS — lệnh test của task: pass 2 · fail 0; toàn bộ tăng đúng 2 node test so với main trước task (bảng "Sơ đồ đợt chạy"); `npm run build`, `npm run kiem-dist` xanh. Số đo trên bản chạy thử.

- [ ] **Step 5: Commit**

```bash
git add frontend/tests/du_an.test.mjs frontend/src/kieu/du-an.css frontend/src/luat_du_an.js frontend/src/trang/DuAn.vue
git commit -m "feat(dashboard): 2f trang Dự án"
```

### Task 16: Trang Ký ức (mockup D39)

**Đợt:** 3 · **Độ khó:** vừa · **Phải xong trước:** Task 1 (Task 5 cho `mo_ta`) · **Test mới:** 5 node

**Mockup bám:** `trang-ky-uc.js`, `du-lieu-ky-uc-usage.js`, `style.css` mục "Ký ức (D36)"; ảnh `anh-ky-uc.png`. D39: khối sự kiện hiện `mo_ta` thay khối JSON `tom_tat`. Bỏ hết phần "Minh hoạ" của mockup (nút minh hoạ quyền, kiểm nghiệp vụ phía trình duyệt — server quyết định).

**Files:**
- Modify (viết lại): `frontend/src/trang/KyUc.vue`, `frontend/src/thanh/TheKyUc.vue`, `frontend/src/thanh/OGhiNho.vue`, `frontend/src/thanh/SuKienNho.vue`; (chỉ thêm): `frontend/src/nho.js` (`nhanPhamVi`, `TEN_NGUON`, `moTaNguon`, `NHOM_SK`, `nhomCua`, `LOP_SK`, `locKyUc`, `tongPhamVi`, nhãn `nho.bo_bi_mat` "Bỏ vì bí mật")
- Create: `frontend/src/kieu/ky-uc.css`
- Test: `frontend/tests/ky_uc.test.mjs` (mới)

**Interfaces:** Consumes `/api/nho`, `/api/nho/su-kien` (`mo_ta` — Task 5), `POST /api/nho/ghi`, `/api/nho/xoa`, `kho.phienBanNho`. 403 → thẻ chặn "403 · Chỉ Đại ca xem được ký ức"; 503 → "Không đọc được memory service" + nút "Mở Tổng quan". Ô tìm lọc phía trình duyệt trên danh sách đã tải; phạm vi và "chỉ chờ" vẫn gửi lên server như cũ. Đường dẫn `/nho` và `/ky-uc` cùng trang (G16).

- [ ] **Step 1: Viết test (chép nguyên văn)**

`frontend/tests/ky_uc.test.mjs` (mới):

```js
import assert from 'node:assert/strict'
import { test } from 'node:test'
import { LOP_SK, NHOM_SK, TEN_NGUON, TEN_SU_KIEN_NHO, locKyUc, moTaNguon, nhanPhamVi, nhomCua, tongPhamVi }
  from '../src/nho.js'

test('nhanPhamVi: bốn loại phạm vi ra nhãn + lớp chip', () => {
  assert.deepEqual(nhanPhamVi('/chung'), ['Chung', 'pv-chung'])
  assert.deepEqual(nhanPhamVi('/vai/coder'), ['Vai coder', 'pv-vai'])
  assert.deepEqual(nhanPhamVi('/du-an/hr-codex/nghiep-vu'), ['Nghiệp vụ', 'pv-nghiep-vu'])
  assert.deepEqual(nhanPhamVi('/du-an/tram/cach-lam'), ['Cách làm', 'pv-cach-lam'])
  assert.deepEqual(nhanPhamVi(undefined), ['Cách làm', 'pv-cach-lam'])
})

test('moTaNguon: nhãn tiếng Việt, vai, bead, thăng cấp cắt mã gốc', () => {
  assert.equal(TEN_NGUON.dai_ca_ghi, 'Đại ca ghi tay')
  assert.deepEqual(moTaNguon([{ loai: 'agent', du_an: 'hr-codex', bead_id: 'hr-2', vai: 'qc' }]),
    [{ thangCap: false, chu: 'agent ghi · vai qc', duAn: 'hr-codex', bead: 'hr-2', idGoc: '' }])
  assert.deepEqual(moTaNguon([{ loai: 'thang_cap', du_an: 'tram', id_goc: 'm-28b3663f97684988' }]),
    [{ thangCap: true, chu: '', duAn: 'tram', bead: '', idGoc: 'm-28b3663…' }])
  assert.deepEqual(moTaNguon([{ loai: 'la', du_an: 'hr' }]),
    [{ thangCap: false, chu: 'la', duAn: 'hr', bead: '', idGoc: '' }])
  assert.deepEqual(moTaNguon(null), [])
})

test('nhomCua + LOP_SK: nhóm lọc sự kiện, nho.bo_bi_mat vào nhóm lỗi', () => {
  assert.equal(nhomCua('nho.ghi'), 'ghi')
  assert.equal(nhomCua('nho.gop'), 'ghi')
  assert.equal(nhomCua('nho.xoa_cung'), 'xoa')
  assert.equal(nhomCua('nho.thang_cap'), 'thang_cap')
  assert.equal(nhomCua('nho.tu_choi'), 'tu_choi')
  assert.equal(nhomCua('nho.phuc_hoi'), 'loi')
  assert.equal(nhomCua('nho.bo_bi_mat'), 'loi')
  assert.equal(TEN_SU_KIEN_NHO['nho.bo_bi_mat'], 'Bỏ vì bí mật')
  assert.deepEqual(NHOM_SK.map(([m]) => m), ['', 'ghi', 'xoa', 'thang_cap', 'tu_choi', 'loi'])
  for (const [m] of NHOM_SK.slice(1)) assert.ok(LOP_SK[m], m)
})

test('locKyUc: tìm theo nội dung, nhãn, mã, phạm vi; không phân biệt hoa thường', () => {
  const ds = [
    { id: 'm-1', noi_dung: 'Chạy Ruff trước', pham_vi: '/du-an/hr/cach-lam', nhan: ['test'] },
    { id: 'm-2', noi_dung: 'Hoá đơn làm tròn', pham_vi: '/chung', nhan: ['hoa-don'] },
  ]
  assert.deepEqual(locKyUc(ds, '  ').map((k) => k.id), ['m-1', 'm-2'])
  assert.deepEqual(locKyUc(ds, 'ruff').map((k) => k.id), ['m-1'])
  assert.deepEqual(locKyUc(ds, 'HOA-DON').map((k) => k.id), ['m-2'])
  assert.deepEqual(locKyUc(ds, 'm-2').map((k) => k.id), ['m-2'])
  assert.deepEqual(locKyUc(ds, '/chung').map((k) => k.id), ['m-2'])
  assert.deepEqual(locKyUc(ds, 'khong-co'), [])
})

test('tongPhamVi cộng số ký ức mọi phạm vi (pill "Tất cả")', () => {
  assert.equal(tongPhamVi([{ pham_vi: '/chung', so: 1 }, { pham_vi: '/vai/qc', so: 3 }]), 4)
  assert.equal(tongPhamVi(undefined), 0)
})
```

- [ ] **Step 2: Chạy thấy FAIL**

```bash
cd frontend && node --test tests/ky_uc.test.mjs
```

Kỳ vọng: FAIL — `SyntaxError: The requested module '../src/nho.js' does not provide an export named 'LOP_SK'`

- [ ] **Step 3: Viết mã (chép nguyên văn; file sửa: chép khối diff ra file tạm, `git apply --check` rồi `git apply`)**

`frontend/src/kieu/ky-uc.css` (mới):

```css
/* Trang Ký ức — mockup style.css "Ký ức (D36)". Bỏ .ku-chan (dùng .the-chan chung);
   .ku-tom-tat thay bằng .ku-mo-ta (D39); .tq-h → .tieu-de-khoi chung; .gc chỉ trong .ku-loc. */
.ku-tong {
  font-size: 15px; font-weight: 700; background: var(--nhan-nhat); color: var(--nhan); border-radius: 999px;
  padding: 2px 10px; vertical-align: 6px; margin-left: 8px; letter-spacing: 0;
}
.ku-khoa-chip .bieu-tuong { width: 12px; height: 12px; stroke-width: 2; }
.ku-luoi { display: grid; grid-template-columns: minmax(0, 1fr) 380px; gap: 16px; align-items: start; }
.ku-chinh { display: flex; flex-direction: column; gap: 10px; min-width: 0; }
.ku-ray { display: flex; flex-direction: column; gap: 16px; position: sticky; top: 72px; }
.ku-ray .tieu-de-khoi { margin: 0; }
.ku-loc { display: flex; flex-direction: column; gap: 10px; }
.ku-hang { display: flex; gap: 10px; flex-wrap: wrap; align-items: flex-end; }
.ku-tim { flex: 1 1 340px; height: 32px; }
.ku-loc .gc {
  white-space: nowrap; display: inline-flex; align-items: center; gap: 6px; font-size: 13px; color: var(--chu-2);
  background: var(--the); border: 1px solid var(--vien-dam); border-radius: 8px; padding: 0 10px; height: 32px;
  cursor: pointer;
}
.ku-loc .gc input { accent-color: var(--nhan); }
.ku-pv, .ku-loc-sk { display: flex; gap: 6px; flex-wrap: wrap; align-items: center; }
.ku-pv > .nho { margin-right: 4px; }
.ku-pill {
  display: inline-flex; align-items: center; gap: 6px; height: 28px; padding: 0 10px; border: 1px solid var(--vien-dam);
  background: var(--the); color: var(--chu-2); border-radius: 999px; font-size: 12.5px;
}
.ku-pill.mono { font-family: var(--mono); font-size: 12px; }
.ku-pill b { font-family: var(--sans); font-weight: 700; color: var(--chu); }
.ku-pill em {
  font-style: normal; font-family: var(--sans); font-size: 11px; font-weight: 600; color: #9a6510;
  background: #fbefd9; border-radius: 999px; padding: 0 6px;
}
.ku-pill:hover { border-color: var(--nhan); }
.ku-pill.chon { background: var(--nhan); border-color: var(--nhan); color: #fff; }
.ku-pill.chon b { color: #fff; }
.ku-dem { margin: 0 2px; font-size: 12.5px; }
.ku-bao {
  margin: 0; font-size: 13px; color: #2f6f45; background: #e5f2e8; border: 1px solid #c4e0cc; border-radius: 8px;
  padding: 6px 10px;
}
.ku-ds { display: flex; flex-direction: column; gap: 10px; }
.ku-the { display: flex; flex-direction: column; gap: 8px; }
.ku-the.cho { border-style: dashed; border-color: #efd8a8; background: #fffdf8; }
.ku-tren { display: flex; gap: 6px; flex-wrap: wrap; align-items: center; }
.ku-nhan { font-size: 12px; color: var(--chu-phu); }
.ku-xoa { margin-left: auto; height: 28px; padding: 0 11px; font-size: 12.5px; }
.ku-noi-dung { margin: 0; font-size: 15px; line-height: 1.5; white-space: pre-wrap; overflow-wrap: anywhere; }
.ku-meta {
  display: flex; flex-wrap: wrap; gap: 4px 16px; font-size: 12.5px; color: var(--chu-2);
  border-top: 1px dashed var(--vien); padding-top: 8px;
}
.ku-meta a { color: var(--nhan); text-decoration: none; }
.ku-meta .ku-id { color: var(--chu-phu); font-size: 11.5px; margin-left: auto; }
.ku-qt { display: inline-flex; align-items: center; gap: 6px; }
.ku-qt i {
  display: inline-block; width: 46px; height: 6px; border-radius: 99px; background: #efe7dc; overflow: hidden;
}
.ku-qt i b { display: block; height: 100%; background: var(--nhan); opacity: .7; }
.pv-cach-lam { background: #e6eef6; color: #3b6187; border-color: #cfdcea; }
.pv-nghiep-vu { background: var(--nhan-nhat); color: var(--nhan); border-color: #ecc9b8; }
.pv-vai, .pv-chung { background: #ece8f6; color: #5a4b97; border-color: #d7d0ee; }
.ku-dai-ca { background: #2f2622; color: #f6e9dc; border-color: #2f2622; }
.ku-ghi { display: flex; flex-direction: column; gap: 10px; }
.ku-ghi > .ku-o { flex: none; }
.ku-ghi textarea { min-height: 76px; }
.ku-o { display: flex; flex-direction: column; gap: 4px; font-size: 13px; font-weight: 600; color: var(--chu-2);
  flex: 1 1 140px; }
.ku-o > span { display: flex; justify-content: space-between; gap: 8px; }
.ku-o .nho { font-weight: 400; font-size: 12px; }
.ku-o select, .ku-o .o { width: 100%; font-weight: 400; }
.ku-dich { margin: 0; display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.ku-ghi .canh-bao { margin: 0; }
.ku-ghi > p.nho { margin: 0; font-size: 12.5px; }
.ku-gui { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.ku-gui .nho { font-size: 12.5px; }
.ku-loi { color: var(--do); font-size: 12.5px; }
.ku-sk .tieu-de-khoi { margin-bottom: 8px; }
.ku-sk .tieu-de-khoi .nho { font-weight: 400; }
.ku-loc-sk { margin-bottom: 8px; }
.ku-loc-sk .ku-pill { height: 24px; font-size: 12px; padding: 0 9px; }
.ku-dtg {
  list-style: none; margin: 0; padding: 0 0 0 2px; border-left: 2px solid var(--vien); max-height: 640px;
  overflow-y: auto;
}
.ku-dtg li { position: relative; padding: 6px 0 8px 12px; border-bottom: 1px dashed var(--vien); }
.ku-dtg li:last-child { border-bottom: 0; }
.ku-dtg li::before {
  content: ''; position: absolute; left: -6px; top: 13px; width: 8px; height: 8px; border-radius: 50%;
  background: var(--nhan);
}
.ku-dtg li > div { display: flex; gap: 6px; align-items: center; flex-wrap: wrap; font-size: 12.5px; }
.ku-dtg a { color: var(--nhan); text-decoration: none; }
/* D39: câu mo_ta dễ đọc (chữ thường); thiếu mo_ta thì tom_tat JSON (thêm .mono, cắt từ) */
.ku-mo-ta { margin: 4px 0 0; font-size: 13px; line-height: 1.45; color: var(--chu-2); overflow-wrap: anywhere; }
.ku-mo-ta.mono { font-size: 11px; word-break: break-all; }
@media (max-width: 1100px) { .ku-luoi { grid-template-columns: 1fr; } .ku-ray { position: static; } }
```

`frontend/src/nho.js` (sửa):

```diff
diff --git a/frontend/src/nho.js b/frontend/src/nho.js
index 7837899..c2a2898 100644
--- a/frontend/src/nho.js
+++ b/frontend/src/nho.js
@@ -10,6 +10,7 @@ export const TEN_SU_KIEN_NHO = {
   'nho.ghi': 'Ghi', 'nho.gop': 'Gộp', 'nho.xoa': 'Xoá mềm', 'nho.xoa_cung': 'Xoá cứng',
   'nho.thang_cap': 'Thăng cấp', 'nho.tu_choi': 'Từ chối', 'nho.loi_tach': 'Bỏ sự kiện',
   'nho.loi_llm': 'Lỗi Claude API', 'nho.loi_embedder': 'Lỗi embedder', 'nho.phuc_hoi': 'Phục hồi',
+  'nho.bo_bi_mat': 'Bỏ vì bí mật',   // lát 1b-4 (quét bí mật)
 }
 
 // Phạm vi đầy đủ từ lựa chọn trên form; null khi thiếu/sai tên — nút Ghi tắt.
@@ -43,3 +44,44 @@ export function tomTatNguon(nguon) {
 export function laSuKienNho(loai) {
   return typeof loai === 'string' && loai.startsWith('nho.')
 }
+
+// ---- Trang Ký ức theo mockup (trang-ky-uc.js, D36/D39) ----
+// Nhãn + lớp chip loại phạm vi.
+export function nhanPhamVi(pv) {
+  const s = String(pv || '')
+  if (s === '/chung') return ['Chung', 'pv-chung']
+  if (s.startsWith('/vai/')) return [`Vai ${s.slice(5)}`, 'pv-vai']
+  return s.endsWith('/nghiep-vu') ? ['Nghiệp vụ', 'pv-nghiep-vu'] : ['Cách làm', 'pv-cach-lam']
+}
+
+export const TEN_NGUON = { agent: 'agent ghi', da_chot: 'Đại ca chốt', dai_ca_sua: 'Đại ca sửa cột',
+  tra_ve: 'Đại ca trả về', dai_ca_ghi: 'Đại ca ghi tay' }
+
+// nguon[] → đoạn để template dựng "Nguồn: …" (thăng cấp: dự án đậm + mã gốc cắt 9 ký tự; khác: nhãn · vai · bead).
+export function moTaNguon(nguon) {
+  return (nguon || []).map((n) => {
+    const thangCap = n.loai === 'thang_cap'
+    return { thangCap, chu: thangCap ? '' : `${TEN_NGUON[n.loai] ?? n.loai}${n.vai ? ` · vai ${n.vai}` : ''}`,
+      duAn: n.du_an || '', bead: thangCap ? '' : n.bead_id || '',
+      idGoc: thangCap && n.id_goc ? `${String(n.id_goc).slice(0, 9)}…` : '' }
+  })
+}
+
+// Nhóm lọc sự kiện nho.* (pill) và lớp chip của từng nhóm; loại lạ / lỗi / phục hồi / bỏ vì bí mật → 'loi'.
+export const NHOM_SK = [['', 'Tất cả'], ['ghi', 'Ghi · gộp'], ['xoa', 'Xoá'], ['thang_cap', 'Thăng cấp'],
+  ['tu_choi', 'Từ chối'], ['loi', 'Lỗi · phục hồi']]
+const NHOM_LOAI = { 'nho.ghi': 'ghi', 'nho.gop': 'ghi', 'nho.xoa': 'xoa', 'nho.xoa_cung': 'xoa',
+  'nho.thang_cap': 'thang_cap', 'nho.tu_choi': 'tu_choi' }
+export const nhomCua = (loai) => NHOM_LOAI[loai] ?? 'loi'
+export const LOP_SK = { ghi: 'tt-lam', xoa: 'tt-tat', thang_cap: 'pv-vai', tu_choi: 'tt-cau_dao', loi: 'tt-can_nguoi' }
+
+// Ô tìm lọc phía trình duyệt trên ký ức đã tải: nội dung, nhãn, mã, phạm vi.
+export function locKyUc(ds, tim) {
+  const q = String(tim || '').trim().toLowerCase()
+  if (!q) return ds || []
+  return (ds || []).filter((k) => [k.noi_dung, k.id, k.pham_vi, ...(k.nhan || [])]
+    .some((x) => String(x || '').toLowerCase().includes(q)))
+}
+
+// Pill "Tất cả n": cộng `so` của mọi phạm vi server trả (không phụ thuộc bộ lọc đang chọn).
+export const tongPhamVi = (dsPv) => (dsPv || []).reduce((t, p) => t + (p.so || 0), 0)
```

`frontend/src/thanh/OGhiNho.vue` (sửa):

```diff
diff --git a/frontend/src/thanh/OGhiNho.vue b/frontend/src/thanh/OGhiNho.vue
index 616b849..f670aa2 100644
--- a/frontend/src/thanh/OGhiNho.vue
+++ b/frontend/src/thanh/OGhiNho.vue
@@ -3,8 +3,8 @@ import { computed, ref } from 'vue'
 import { ghi, taoMaThaoTac, thanGhi } from '../api.js'
 import { LOAI_PHAM_VI, dungPhamVi, ngoaiDuAn, tachNhan } from '../nho.js'
 
-// Đại ca ghi tay (spec 1b §6.1): mọi phạm vi. Server ép /du-an/X/cach-lam chạm luật về nghiep-vu;
-// /vai/*, /chung chạm luật của bất kỳ dự án nào thì từ chối (nho.tu_choi).
+// Đại ca ghi tay (mockup trang-ky-uc.js formGhi, D36; spec 1b §6.1): mọi phạm vi. Server ép /du-an/X/cach-lam chạm
+// luật về nghiep-vu; /vai/*, /chung chạm luật của bất kỳ dự án nào thì từ chối (nho.tu_choi) — trình duyệt không kiểm.
 const props = defineProps({ duAn: { type: Array, default: () => [] }, laDaiCa: { type: Boolean, default: false } })
 const emit = defineEmits(['doi'])
 const noiDung = ref('')
@@ -43,25 +43,33 @@ async function gui() {
 </script>
 
 <template>
-  <form class="muc" @submit.prevent="gui">
-    <h2>Ghi tay một ký ức</h2>
-    <label>Nội dung<textarea v-model="noiDung" rows="3" maxlength="600" required></textarea></label>
-    <div class="cong-cu">
-      <label>Phạm vi<select v-model="loai">
+  <form class="the ku-ghi" @submit.prevent="gui">
+    <h3 class="tieu-de-khoi">Ghi tay một ký ức</h3>
+    <label class="ku-o"><span>Nội dung <span class="nho">{{ noiDung.length }}/600</span></span>
+      <textarea v-model="noiDung" maxlength="600" rows="3" required
+        placeholder="Một bài học ngắn, tự đứng được…"></textarea></label>
+    <div class="ku-hang">
+      <label class="ku-o"><span>Phạm vi</span><select v-model="loai">
         <option v-for="[k, ten] in LOAI_PHAM_VI" :key="k" :value="k">{{ ten }}</option>
       </select></label>
-      <label v-if="loai.startsWith('du-an')">Dự án<select v-model="duAnChon">
+      <label v-if="loai.startsWith('du-an')" class="ku-o"><span>Dự án</span><select v-model="duAnChon">
         <option value="" disabled>— chọn —</option>
         <option v-for="d in props.duAn" :key="d" :value="d">{{ d }}</option>
       </select></label>
-      <label v-if="loai === 'vai'">Vai<input v-model.trim="vai" placeholder="coder, qc, cham-cot…" maxlength="40"></label>
-      <label>Nhãn<input v-model="nhan" placeholder="test, git" maxlength="200"></label>
+      <label v-if="loai === 'vai'" class="ku-o"><span>Vai</span>
+        <input v-model.trim="vai" class="o" maxlength="40" placeholder="coder, qc, cham-cot…"></label>
+    </div>
+    <label class="ku-o"><span>Nhãn <span class="nho">tối đa 5, cách nhau dấu phẩy</span></span>
+      <input v-model="nhan" class="o" maxlength="200" placeholder="test, git"></label>
+    <p class="nho ku-dich">Ghi vào: <span class="chip mono">{{ phamVi || '(chưa đủ)' }}</span></p>
+    <div v-if="phamVi && ngoaiDuAn(phamVi)" class="canh-bao">Agent của MỌI dự án sẽ thấy ký ức này. Có tên khách,
+      số tiền hay tên module của bất kỳ dự án nào thì bị từ chối.</div>
+    <p v-if="phamVi && phamVi.endsWith('/cach-lam')" class="nho">Chạm luật nghiệp vụ của dự án thì trạm tự chuyển vào
+      <span class="mono">nghiep-vu</span>.</p>
+    <div class="ku-gui">
+      <button class="nut chinh" type="submit" :disabled="!laDaiCa || dangGui || !phamVi || !noiDung.trim()">Ghi</button>
+      <span v-if="thongBao" class="nho" role="status">{{ thongBao }}</span>
+      <span v-if="loi" class="ku-loi" role="alert">{{ loi }}</span>
     </div>
-    <p class="nho">Ghi vào: <span class="ma">{{ phamVi || '(chưa đủ)' }}</span></p>
-    <p v-if="phamVi && ngoaiDuAn(phamVi)" class="canh-bao">Agent của MỌI dự án sẽ thấy ký ức này. Có tên khách, số tiền
-      hay tên module của bất kỳ dự án nào thì bị từ chối.</p>
-    <button type="submit" :disabled="!laDaiCa || dangGui || !phamVi || !noiDung.trim()">Ghi</button>
-    <p v-if="thongBao" class="nho" role="status">{{ thongBao }}</p>
-    <p v-if="loi" class="loi" role="alert">{{ loi }}</p>
   </form>
 </template>
```

`frontend/src/thanh/SuKienNho.vue` (sửa):

```diff
diff --git a/frontend/src/thanh/SuKienNho.vue b/frontend/src/thanh/SuKienNho.vue
index 1c1c854..44cfdb8 100644
--- a/frontend/src/thanh/SuKienNho.vue
+++ b/frontend/src/thanh/SuKienNho.vue
@@ -1,20 +1,37 @@
 <script setup>
-import { gioVN } from '../luat.js'
-import { TEN_SU_KIEN_NHO } from '../nho.js'
+import { computed, ref } from 'vue'
+import { ngayGio } from '../dinh_dang.js'
+import { LOP_SK, NHOM_SK, TEN_SU_KIEN_NHO, nhomCua } from '../nho.js'
 
-defineProps({ ds: { type: Array, required: true } })
+// Sự kiện nho.* gần đây (mockup trang-ky-uc.js khoiSuKien, D36): lọc nhóm phía trình duyệt; D39 hiện câu `mo_ta`
+// do API dựng, thiếu thì hiện `tom_tat` (JSON cũ, chữ mono).
+const props = defineProps({ ds: { type: Array, required: true } })
+const nhom = ref('')
+const loc = computed(() => props.ds.filter((s) => !nhom.value || nhomCua(s.loai) === nhom.value))
 </script>
 
 <template>
-  <section>
-    <h2>Sự kiện ký ức gần đây</h2>
-    <p v-if="!ds.length" class="nho">Chưa có sự kiện.</p>
-    <ol v-else class="dong-thoi-gian">
-      <li v-for="s in ds" :key="s.id">
-        <span class="nho">{{ gioVN(s.luc) }} · {{ s.du_an }}<template v-if="s.bead_id">/{{ s.bead_id }}</template></span>
-        <strong>{{ TEN_SU_KIEN_NHO[s.loai] || s.loai }}</strong>
-        <span class="van-ban">{{ s.tom_tat }}</span>
+  <section class="the ku-sk">
+    <h3 class="tieu-de-khoi">Sự kiện ký ức gần đây <span class="nho">{{ ds.length }} / tối đa 50</span></h3>
+    <div class="ku-loc-sk" role="group" aria-label="Lọc loại sự kiện">
+      <button v-for="[m, ten] in NHOM_SK" :key="m" type="button" class="ku-pill" :class="{ chon: m === nhom }"
+        :aria-pressed="m === nhom" @click="nhom = m">{{ ten }}</button>
+    </div>
+    <ol v-if="loc.length" class="ku-dtg">
+      <li v-for="s in loc" :key="s.id">
+        <div>
+          <span class="mono nho">{{ ngayGio(s.luc) }}</span>
+          <span class="chip" :class="LOP_SK[nhomCua(s.loai)]">{{ TEN_SU_KIEN_NHO[s.loai] || s.loai }}</span>
+          <span class="nho">
+            <router-link v-if="s.bead_id" class="mono"
+              :to="{ path: '/cong-viec', query: { du_an: s.du_an, bead: s.bead_id } }"
+            >{{ s.du_an }}/{{ s.bead_id }}</router-link>
+            <span v-else class="mono">{{ s.du_an }}</span>
+          </span>
+        </div>
+        <p class="ku-mo-ta">{{ s.mo_ta || 'Sự kiện chưa có mô tả.' }}</p>
       </li>
     </ol>
+    <p v-else class="nho">Chưa có sự kiện.</p>
   </section>
 </template>
```

`frontend/src/thanh/TheKyUc.vue` (sửa):

```diff
diff --git a/frontend/src/thanh/TheKyUc.vue b/frontend/src/thanh/TheKyUc.vue
index 18413da..0f9db47 100644
--- a/frontend/src/thanh/TheKyUc.vue
+++ b/frontend/src/thanh/TheKyUc.vue
@@ -1,14 +1,17 @@
 <script setup>
-import { ref } from 'vue'
+import { computed, ref } from 'vue'
 import { ghi, thanGhi } from '../api.js'
-import { gioVN } from '../luat.js'
-import { tomTatNguon } from '../nho.js'
+import { ngayGio } from '../dinh_dang.js'
+import { moTaNguon, nhanPhamVi } from '../nho.js'
 
-// Một ký ức trên màn Ký ức (spec 1b §5): nội dung chỉ hiện bằng text; Xoá = xoá mềm (`nho.xoa`).
+// Một ký ức (mockup trang-ky-uc.js theKyUc, D36; spec 1b §5): nội dung chỉ hiện bằng text; Xoá = xoá mềm (`nho.xoa`).
 const props = defineProps({ ky: { type: Object, required: true }, laDaiCa: { type: Boolean, default: false } })
 const emit = defineEmits(['doi'])
 const dangGui = ref(false)
 const loi = ref('')
+const pv = computed(() => nhanPhamVi(props.ky.pham_vi))
+const nguon = computed(() => moTaNguon(props.ky.nguon))
+const qt = computed(() => Math.min(1, Math.max(0, Number(props.ky.quan_trong) || 0)))
 
 async function xoa() {
   if (!window.confirm('Xoá mềm ký ức này? Recall sẽ không trả nó nữa.')) return
@@ -16,7 +19,7 @@ async function xoa() {
   loi.value = ''
   try {
     await ghi('/api/nho/xoa', thanGhi({ id: props.ky.id }, props.ky.tao_luc))
-    emit('doi')
+    emit('doi', props.ky.id)
   } catch (e) {
     loi.value = e.message
   } finally {
@@ -26,18 +29,34 @@ async function xoa() {
 </script>
 
 <template>
-  <article class="muc">
-    <header>
-      <span class="ma">{{ ky.pham_vi }}</span>
-      <span v-if="ky.dang_cho" class="nhan-nho vang">chờ tự có hiệu lực {{ gioVN(ky.hieu_luc_tu) }}</span>
-      <span v-if="ky.nguon_dai_ca" class="nhan-nho">của Đại ca</span>
-      <span v-for="n in ky.nhan" :key="n" class="nhan-nho">{{ n }}</span>
-    </header>
-    <p class="van-ban">{{ ky.noi_dung }}</p>
-    <p class="nho">{{ tomTatNguon(ky.nguon) }} · tạo {{ gioVN(ky.tao_luc) }} · quan trọng {{ ky.quan_trong.toFixed(2) }}
-      · dùng {{ ky.so_lan_dung }} lần<template v-if="ky.dung_luc"> (gần nhất {{ gioVN(ky.dung_luc) }})</template>
-      · <span class="ma">{{ ky.id }}</span></p>
-    <button type="button" :disabled="dangGui || !laDaiCa" @click="xoa">Xoá</button>
-    <p v-if="loi" class="loi" role="alert">{{ loi }}</p>
+  <article class="the ku-the" :class="{ cho: ky.dang_cho }">
+    <div class="ku-tren">
+      <span class="chip" :class="pv[1]">{{ pv[0] }}</span>
+      <span class="chip mono">{{ ky.pham_vi }}</span>
+      <span v-if="ky.dang_cho" class="chip tt-cau_dao">chờ tự có hiệu lực {{ ngayGio(ky.hieu_luc_tu) }}</span>
+      <span v-if="ky.nguon_dai_ca" class="chip ku-dai-ca">của Đại ca</span>
+      <span v-for="n in ky.nhan" :key="n" class="ku-nhan mono">#{{ n }}</span>
+      <button class="nut nguy ku-xoa" type="button" title="Xoá mềm — recall không trả nữa"
+        :disabled="dangGui || !laDaiCa" @click="xoa">Xoá</button>
+    </div>
+    <p class="ku-noi-dung">{{ ky.noi_dung }}</p>
+    <div class="ku-meta">
+      <span>Nguồn:
+        <template v-for="(n, i) in nguon" :key="i"><template v-if="i">; </template>
+          <template v-if="n.thangCap">thăng cấp từ <b>{{ n.duAn }}</b> <span
+            class="mono nho">{{ n.idGoc }}</span></template>
+          <template v-else>{{ n.chu }}<template v-if="n.bead"> · <router-link class="mono"
+            :to="{ path: '/cong-viec', query: { du_an: n.duAn, bead: n.bead } }">{{ n.duAn }}/{{ n.bead }}</router-link>
+          </template><template v-else-if="n.duAn"> · {{ n.duAn }}</template></template>
+        </template>
+      </span>
+      <span>Tạo {{ ngayGio(ky.tao_luc) }}</span>
+      <span class="ku-qt" title="Độ quan trọng 0–1">Quan trọng <i><b :style="{ width: qt * 100 + '%' }"></b></i>
+        {{ qt.toFixed(2) }}</span>
+      <span>Dùng {{ ky.so_lan_dung }} lần<template v-if="ky.dung_luc"> · gần nhất
+        {{ ngayGio(ky.dung_luc) }}</template></span>
+      <span class="mono ku-id">{{ ky.id }}</span>
+    </div>
+    <p v-if="loi" class="ku-loi" role="alert">{{ loi }}</p>
   </article>
 </template>
```

`frontend/src/trang/KyUc.vue` (sửa):

```diff
diff --git a/frontend/src/trang/KyUc.vue b/frontend/src/trang/KyUc.vue
index e377dba..e249f0a 100644
--- a/frontend/src/trang/KyUc.vue
+++ b/frontend/src/trang/KyUc.vue
@@ -2,20 +2,32 @@
 import { computed, onMounted, ref, watch } from 'vue'
 import { doc } from '../api.js'
 import { kho } from '../kho.js'
+import { locKyUc, tongPhamVi } from '../nho.js'
+import BieuTuong from '../thanh/BieuTuong.vue'
+import DauTrang from '../thanh/DauTrang.vue'
 import OGhiNho from '../thanh/OGhiNho.vue'
 import SuKienNho from '../thanh/SuKienNho.vue'
 import TheKyUc from '../thanh/TheKyUc.vue'
+import '../kieu/ky-uc.css'
 
-// Màn Ký ức (spec 1b lát 1b-3, spec 2 §7 `/api/nho/*`): xem / xoá / ghi tay; lọc ký ức thăng cấp đang chờ (#19).
+// Màn Ký ức (mockup trang-ky-uc.js veKyUc, D36/D39; spec 1b lát 1b-3, spec 2 §7 `/api/nho/*`): xem / tìm / xoá /
+// ghi tay; lọc phạm vi + ký ức thăng cấp đang chờ (#19) gửi lên server; ô tìm lọc phía trình duyệt. Quyền: server.
 const ds = ref([])
 const cacPhamVi = ref([])
 const tong = ref(0)
 const suKien = ref([])
 const phamVi = ref('')
 const chiCho = ref(false)
+const tim = ref('')
+const bao = ref('')
+const chan = ref(0)                // 403 | 503 → thẻ chặn thay cả lưới
 const loi = ref('')
 const laDaiCa = computed(() => Boolean(kho.trangThai && kho.trangThai.la_dai_ca))
 const duAn = computed(() => (kho.trangThai ? kho.trangThai.du_an.map((d) => d.ten) : []))
+const hien = computed(() => locKyUc(ds.value, tim.value))
+const tatCa = computed(() => tongPhamVi(cacPhamVi.value))
+const MO_TA = 'Bài học agent và Đại ca để lại cho các lượt sau. Xem, lọc, xoá mềm, ghi tay; '
+  + 'ký ức thăng cấp chờ 7 ngày rồi mới có hiệu lực.'
 
 async function tai() {
   const q = new URLSearchParams({ pham_vi: phamVi.value, cho: chiCho.value ? '1' : '0' })
@@ -25,31 +37,64 @@ async function tai() {
     cacPhamVi.value = r.pham_vi
     tong.value = r.tong
     suKien.value = s.su_kien
+    chan.value = 0
     loi.value = ''
   } catch (e) {
-    loi.value = e.status === 403 ? 'Chỉ Đại ca xem được ký ức (cần danh tính Tailscale của Đại ca).' : e.message
+    chan.value = e.status === 403 || e.status === 503 ? e.status : 0
+    loi.value = chan.value ? '' : e.message
   }
 }
+function daXoa(id) {
+  bao.value = `Đã xoá mềm ${id}.`
+  tai()
+}
 onMounted(tai)
 watch([phamVi, chiCho, () => kho.phienBanNho], tai)
 </script>
 
 <template>
-  <section>
-    <h1>Ký ức <span class="dem-nho">{{ tong }}</span></h1>
-    <p v-if="loi" class="loi" role="alert">{{ loi }}</p>
-    <div class="cong-cu">
-      <label>Phạm vi<select v-model="phamVi">
-        <option value="">Tất cả</option>
-        <option v-for="p in cacPhamVi" :key="p.pham_vi" :value="p.pham_vi">
-          {{ p.pham_vi }} ({{ p.so }}<template v-if="p.so_cho">, {{ p.so_cho }} chờ</template>)</option>
-      </select></label>
-      <label><input v-model="chiCho" type="checkbox">Chỉ ký ức thăng cấp đang chờ tự có hiệu lực (7 ngày)</label>
+  <DauTrang tieu-de="Ký ức" :mo-ta="MO_TA">
+    <template #sau-tieu-de><span class="ku-tong">{{ chan ? '—' : tong }}</span></template>
+    <template #cong-cu><span class="chip ku-khoa-chip"><BieuTuong ten="khoa" />chỉ Đại ca xem</span></template>
+  </DauTrang>
+  <div v-if="chan === 403" class="the the-chan" role="alert"><strong>403 · Chỉ Đại ca xem được ký ức</strong>
+    <p>Cần danh tính Tailscale của Đại ca. Ký ức của mọi dự án (cả nghiệp vụ và nguồn) không hiện cho ai khác, kể cả
+      danh sách phạm vi và sự kiện.</p></div>
+  <div v-else-if="chan === 503" class="the the-chan" role="alert"><strong>Không đọc được memory service</strong>
+    <p>tram-api chưa nối memory service (vn.tram.nho, 127.0.0.1:7710). Xem Sức khoẻ trạm ở Tổng quan; trang tự tải lại
+      khi có sự kiện nho.*.</p>
+    <router-link class="nut" to="/tong-quan">Mở Tổng quan</router-link></div>
+  <div v-else class="ku-luoi">
+    <div class="ku-chinh">
+      <section class="the ku-loc">
+        <div class="ku-hang">
+          <label class="tim ku-tim"><BieuTuong ten="tim" />
+            <input v-model="tim" type="search" placeholder="Tìm nội dung, nhãn, mã…" aria-label="Tìm ký ức"></label>
+          <label class="gc"><input v-model="chiCho" type="checkbox">Chỉ ký ức thăng cấp đang chờ tự có hiệu lực
+            (7 ngày)</label>
+        </div>
+        <div class="ku-pv" role="group" aria-label="Lọc phạm vi"><span class="nho">Phạm vi</span>
+          <button type="button" class="ku-pill" :class="{ chon: !phamVi }" :aria-pressed="!phamVi"
+            @click="phamVi = ''">Tất cả <b>{{ tatCa }}</b></button>
+          <button v-for="p in cacPhamVi" :key="p.pham_vi" type="button" class="ku-pill mono"
+            :class="{ chon: p.pham_vi === phamVi }" :aria-pressed="p.pham_vi === phamVi" @click="phamVi = p.pham_vi"
+          >{{ p.pham_vi }} <b>{{ p.so }}</b><em v-if="p.so_cho">{{ p.so_cho }} chờ</em></button>
+        </div>
+      </section>
+      <p v-if="loi" class="loi" role="alert">{{ loi }}</p>
+      <p v-if="bao" class="ku-bao" role="status">{{ bao }}</p>
+      <p class="nho ku-dem">Đang hiện {{ hien.length }} / {{ tong }} ký ức<template v-if="tim.trim()"> khớp
+        “{{ tim.trim() }}”</template> · mới nhất trước · tự tải lại khi có sự kiện <span class="mono">nho.*</span>
+        <template v-if="tong > ds.length"> · server chỉ trả 200 ký ức mới nhất, lọc theo phạm vi để xem
+          thêm</template></p>
+      <div class="ku-ds">
+        <TheKyUc v-for="k in hien" :key="k.id" :ky="k" :la-dai-ca="laDaiCa" @doi="daXoa" />
+        <div v-if="!hien.length" class="cot-rong">Không có ký ức nào.</div>
+      </div>
     </div>
-    <p v-if="tong > ds.length" class="nho">Đang hiện {{ ds.length }} ký ức mới nhất trên {{ tong }} — lọc theo phạm vi để xem thêm.</p>
-    <p v-if="!ds.length && !loi" class="nho">Không có ký ức nào.</p>
-    <TheKyUc v-for="k in ds" :key="k.id" :ky="k" :la-dai-ca="laDaiCa" @doi="tai" />
-    <OGhiNho :du-an="duAn" :la-dai-ca="laDaiCa" @doi="tai" />
-    <SuKienNho :ds="suKien" />
-  </section>
+    <aside class="ku-ray">
+      <OGhiNho :du-an="duAn" :la-dai-ca="laDaiCa" @doi="tai" />
+      <SuKienNho :ds="suKien" />
+    </aside>
+  </div>
 </template>
```

- [ ] **Step 4: Chạy thấy PASS**

```bash
cd frontend && node --test tests/ky_uc.test.mjs
npm run kiem && npm run build && npm run kiem-dist && cd ..
```

Kỳ vọng: PASS — lệnh test của task: pass 5 · fail 0; toàn bộ tăng đúng 5 node test so với main trước task (bảng "Sơ đồ đợt chạy"); `npm run build`, `npm run kiem-dist` xanh. Số đo trên bản chạy thử.

- [ ] **Step 5: Commit**

```bash
git add frontend/tests/ky_uc.test.mjs frontend/src/kieu/ky-uc.css frontend/src/nho.js frontend/src/thanh/OGhiNho.vue frontend/src/thanh/SuKienNho.vue frontend/src/thanh/TheKyUc.vue frontend/src/trang/KyUc.vue
git commit -m "feat(dashboard): 2f trang Ký ức (D39)"
```

### Task 17: Trang Usage & chi phí (mockup D39)

**Đợt:** 3 · **Độ khó:** vừa · **Phải xong trước:** Task 1, 2 · **Test mới:** 6 node

**Mockup bám:** `trang-usage.js`, `du-lieu-ky-uc-usage.js`, `style.css` mục "Usage & chi phí (D36)"; ảnh `anh-usage.png`. D39: giữ khối "Hạn mức thuê bao của khe" (đọc `/api/doi-ngu` mỗi 5 giây), số gọn ("4,20 tr") + rê chuột hiện số đầy đủ (`title`). Bỏ phần minh hoạ (ô "chưa có bảng giá", nhóm nút trạng thái ccusage).

**Files:**
- Create: `frontend/src/thanh/usage/BieuDoUsage.vue`, `KhoiHanMuc.vue`, `KhoiCcusage.vue`, `frontend/src/luat_usage.js`, `frontend/src/kieu/usage.css`
- Modify (viết lại): `frontend/src/trang/Usage.vue`, `frontend/src/thanh/BangUsage.vue`
- Test: `frontend/tests/usage.test.mjs` (mới)

**Interfaces:** Consumes `/api/usage?so_ngay=` (7/14/30/92, mặc định 14), `/api/doi-ngu` (`han_muc`, `muc_han_muc`), `mauKhe`, `oHanMuc`, `cuaSo`, `tenKhe`, `gon`, `soDayDu`, `usd`, `ngayNgan`. Không có bảng giá: ẩn nhóm nút Chi phí/Token, biểu đồ vẽ token.

- [ ] **Step 1: Viết test (chép nguyên văn)**

`frontend/tests/usage.test.mjs` (mới):

```js
import assert from 'node:assert/strict'
import { test } from 'node:test'
import {
  chieuCot, dayNgay, giaTriNgay, khoangNgay, moiNhatTruoc, nhanLuat, nguonUsage, oTong, tiTrong, tongUsage,
  trucBieuDo, hienMocNgay,
} from '../src/luat_usage.js'

const d = (khoa, vao, ra, lan, cp, thieu = 0) =>
  ({ khoa, token_vao: vao, token_ra: ra, token_cache_doc: 10, token_cache_ghi: 1, so_lan: lan, chi_phi_usd: cp,
    thieu_gia: thieu })

test('tổng các trường từ theo_ngay; chi phí null khi mọi dòng thiếu giá', () => {
  const t = tongUsage([d('2026-10-14', 100, 20, 3, 1.5), d('2026-10-15', 50, 5, 2, null, 2)])
  assert.deepEqual(t, { token_vao: 150, token_ra: 25, token_cache_doc: 20, token_cache_ghi: 2, so_lan: 5,
    thieu_gia: 2, chi_phi_usd: 1.5 })
  assert.equal(tongUsage([d('2026-10-15', 1, 1, 1, null, 1)]).chi_phi_usd, null)
  assert.equal(tongUsage([]).so_lan, 0)
  assert.equal(tongUsage(undefined).chi_phi_usd, null)
})

test('dãy ngày tu..den (qua tháng), khoảng ngày đầu trang, mốc nhãn trục', () => {
  assert.deepEqual(dayNgay('2026-09-29', '2026-10-02'), ['2026-09-29', '2026-09-30', '2026-10-01', '2026-10-02'])
  assert.deepEqual(dayNgay('2026-10-15', '2026-10-15'), ['2026-10-15'])
  assert.deepEqual(dayNgay('x', '2026-10-15'), [])
  assert.equal(khoangNgay('2026-10-02', '2026-10-15'), 'Từ 02/10 đến 15/10/2026')
  assert.equal([...Array(14).keys()].filter((i) => hienMocNgay(i, 14, false)).length, 7)
  assert.ok(hienMocNgay(13, 14, true))
  assert.ok(hienMocNgay(5, 7, false))
})

test('trần + nhãn trục theo bước mockup, chiều cao cột', () => {
  assert.deepEqual(trucBieuDo(7.3, 'chi_phi'), { tran: 8, nhan: ['$8', '$6', '$4', '$2', '$0'] })
  assert.deepEqual(trucBieuDo(0, 'chi_phi'), { tran: 4, nhan: ['$4', '$3', '$2', '$1', '$0'] })
  assert.deepEqual(trucBieuDo(5, 'chi_phi').nhan, ['$8', '$6', '$4', '$2', '$0'])
  assert.equal(trucBieuDo(1.8e6, 'token').tran, 2e6)
  assert.deepEqual(trucBieuDo(1.8e6, 'token').nhan, ['2,00 tr', '1,50 tr', '1,00 tr', '500 n', '0'])
  assert.equal(trucBieuDo(900, 'chi_phi').tran, 2000)          // vượt bảng bước mockup → tiếp chuỗi 1-2-5
  assert.deepEqual(trucBieuDo(0, 'token').nhan, ['400 n', '300 n', '200 n', '100 n', '0'])
  assert.equal(chieuCot(2, 8), 25)
  assert.equal(chieuCot(20, 8), 100)
  assert.equal(chieuCot(null, 8), 0)
  assert.equal(giaTriNgay(d('a', 100, 20, 1, 0.5), 'chi_phi'), 0.5)
  assert.equal(giaTriNgay(d('a', 100, 20, 1, null), 'chi_phi'), 0)
  assert.equal(giaTriNgay(d('a', 100, 20, 1, 0.5), 'token'), 120)
  assert.equal(giaTriNgay(undefined, 'token'), 0)
})

test('tỉ trọng theo chi phí (tối thiểu 2%), không có giá → theo token vào + ra', () => {
  assert.deepEqual(tiTrong([d('a', 0, 0, 1, 3), d('b', 0, 0, 1, 1), d('c', 0, 0, 1, null)]), [75, 25, 2])
  assert.deepEqual(tiTrong([d('a', 30, 10, 1, null), d('b', 50, 10, 1, null)]), [40, 60])
  assert.deepEqual(tiTrong([d('a', 0, 0, 1, null)]), [2])
})

test('tên nguồn, luật nhận việc, mới nhất trước', () => {
  assert.deepEqual(nguonUsage('cham-cot'), { ten: 'Bộ chấm cột (Claude API)', mono: false, mau: 'var(--xam)' })
  const k = nguonUsage('B/claude-1')
  assert.equal(k.ten, 'B/claude-1')
  assert.equal(k.mono, true)
  assert.match(k.mau, /^#[0-9a-f]{6}$/)
  assert.deepEqual(nhanLuat('ok'), { chu: 'Nhận việc', lop: 'tt-lam' })
  assert.deepEqual(nhanLuat('ngung'), { chu: 'Ngừng — chạm ngưỡng', lop: 'tt-can_nguoi' })
  assert.deepEqual(nhanLuat('chi_p0_p1'), { chu: 'Chỉ P0–P1 — tuần cao', lop: 'tt-cau_dao' })
  assert.deepEqual(nhanLuat('chua_biet'), { chu: 'Chưa biết — vẫn nhận việc', lop: 'tt-cau_dao' })
  assert.deepEqual(nhanLuat(undefined), nhanLuat('chua_biet'))
  assert.deepEqual(moiNhatTruoc([{ khoa: '2026-W40' }, { khoa: '2026-W42' }]).map((x) => x.khoa),
    ['2026-W42', '2026-W40'])
})

test('sáu ô số tổng: gọn + title đầy đủ, phụ lần gọi và chi phí', () => {
  const dl = { co_bang_gia: true, theo_ngay: [d('2026-10-15', 1840000, 212000, 188, 52.17, 3)],
    theo_nguon: [d('B/claude-1', 1, 1, 69, 47.66), d('cham-cot', 1, 1, 119, 4.51)] }
  const o = oTong(dl)
  assert.equal(o.length, 6)
  assert.deepEqual(o[0], { gt: '1,84 tr', ten: 'token vào', phu: '', tieuDe: (1840000).toLocaleString('vi-VN') })
  assert.equal(o[4].phu, '69 khe · 119 chấm cột')
  assert.equal(o[5].gt, '$52.17')
  assert.equal(o[5].phu, 'API thật $4.51 · 3 lần thiếu giá')
  const kg = oTong({ ...dl, co_bang_gia: false })
  assert.deepEqual([kg[5].gt, kg[5].phu], ['—', 'chưa có giá'])
  assert.equal(oTong({ co_bang_gia: true, theo_ngay: [], theo_nguon: [] })[4].phu, '0 khe · 0 chấm cột')
})
```

- [ ] **Step 2: Chạy thấy FAIL**

```bash
cd frontend && node --test tests/usage.test.mjs
```

Kỳ vọng: FAIL — `Error [ERR_MODULE_NOT_FOUND]: Cannot find module '…/frontend/src/luat_usage.js' imported from …/frontend/tests/usage.test.mjs`

- [ ] **Step 3: Viết mã (chép nguyên văn; file sửa: chép khối diff ra file tạm, `git apply --check` rồi `git apply`)**

`frontend/src/kieu/usage.css` (mới):

```css
/* Trang Usage & chi phí (mockup style.css "Usage & chi phí (D36)" + phần .tq-* trang dùng, gói trong .us-trang). */
.us-trang .tq-h { margin: 0 0 10px; font-size: 16px; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.us-trang .tq-h a { text-decoration: none; }
.us-h-phu { font-weight: 400; }
.us-lk { margin-left: auto; color: var(--chu-phu); }
.us-phai { margin-left: auto; }
.us-ghi { margin: -4px 0 14px; display: flex; gap: 6px 14px; flex-wrap: wrap; align-items: center; }
.us-canh { margin: -6px 0 14px; }
.tq-so.us-so { display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 8px; margin-bottom: 16px; }
.us-so div { display: flex; flex-direction: column; background: var(--the); border: 1px solid var(--vien);
  border-radius: 10px; padding: 10px 12px; }
.us-so b { font-size: 22px; letter-spacing: -.3px; }
.us-so .nho { font-size: 11.5px; }
.us-so .us-phu { margin-top: 2px; color: var(--chu-2); }
.us-the-bd, .us-khoi { margin-bottom: 16px; }
.us-bd { display: grid; grid-template-columns: 52px 1fr; gap: 8px; height: 230px; padding: 4px 0 22px; }
.us-truc { display: flex; flex-direction: column; justify-content: space-between; align-items: flex-end;
  font-size: 11px; color: var(--chu-phu); font-family: var(--mono); transform: translateY(-6px);
  height: calc(100% + 12px); }
.us-vung { position: relative; display: flex; align-items: flex-end; gap: 2px;
  border-bottom: 1px solid var(--vien-dam); }
.us-ke { position: absolute; left: 0; right: 0; height: 0; border-top: 1px dashed var(--vien); pointer-events: none; }
.us-cot { position: relative; flex: 1 1 0; height: 100%; display: flex; align-items: flex-end; justify-content: center;
  outline: none; }
.us-cot b { display: block; width: 100%; max-width: 30px; min-height: 0; background: var(--nhan); opacity: .55;
  border-radius: 4px 4px 0 0; }
.us-cot.nay b { opacity: 1; }
.us-cot:hover b, .us-cot:focus b { opacity: .9; }
.us-cot:focus-visible b { outline: 2px solid var(--nhan-dam); outline-offset: 1px; }
.us-cot em { position: absolute; top: 100%; margin-top: 5px; font-style: normal; font-size: 10.5px;
  color: var(--chu-phu); font-family: var(--mono); white-space: nowrap; }
.us-tip { display: none; position: absolute; left: 50%; z-index: 5; background: #2f2622; color: #f6e9dc;
  font-size: 12px; line-height: 1.45; padding: 6px 9px; border-radius: 8px; white-space: nowrap; pointer-events: none; }
.us-tip strong { display: block; color: #fff; }
.us-cot:hover .us-tip, .us-cot:focus .us-tip { display: block; top: -8px; transform: translate(-50%, -100%); }
.tq-luoi.us-luoi { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; margin-bottom: 16px;
  align-items: start; }
.us-luoi .us-bang .bang th, .us-luoi .us-bang .bang td { padding: 6px 5px; font-size: 12.5px; }
.us-luoi .us-bang .bang thead th { font-size: 11px; letter-spacing: 0; }
.us-bang { overflow-x: auto; }
.us-bang.cuon { max-height: 380px; overflow-y: auto; }
.us-bang.cuon thead th { position: sticky; top: 0; background: var(--the); z-index: 1; }
.us-bang th .cham { margin-right: 6px; }
.us-bang td.so { text-align: right; white-space: nowrap; }
.us-bang thead th:not(:first-child) { text-align: right; }
.us-bang thead th:last-child { text-align: left; }
.us-bang .bang th, .us-bang .bang td { padding: 7px 8px; white-space: nowrap; }
.us-cot-tt { width: 90px; }
.us-thieu { display: block; font-size: 11px; color: #9a6510; }
.us-tt { width: 100%; }
.us-tt.thanh-hm i { background: var(--nhan); opacity: .7; }
.us-hm td { vertical-align: middle; }
.us-hm th .cham { margin-right: 6px; }
.us-o-hm { display: grid; grid-template-columns: minmax(80px, 1fr) auto; gap: 10px; align-items: center;
  font-size: 12.5px; color: var(--chu-2); }
.us-giai { margin: 8px 0 0; }
@media (max-width: 1100px) {
  .tq-so.us-so { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  .tq-luoi.us-luoi { grid-template-columns: 1fr; }
}
```

`frontend/src/luat_usage.js` (mới):

```js
// Luật hiển thị thuần của trang Usage & chi phí (mockup trang-usage.js, D36/D39). Server chỉ trả các mảng của
// GET /api/usage; ô số tổng, biểu đồ theo ngày, tỉ trọng do trình duyệt tự cộng ở đây. Test: tests/usage.test.mjs.
import { gon, ngayNgan, soDayDu, usd } from './dinh_dang.js'
import { mauKhe } from './mau_khe.js'

export const SO_NGAY_USAGE = [7, 14, 30, 92]
export const TRUONG_TOKEN = ['token_vao', 'token_ra', 'token_cache_doc', 'token_cache_ghi']
const NGUON_CHAM = 'cham-cot'
// Bước trục biểu đồ như mockup bieuDo(): trần = bước × 4; vượt bảng thì tiếp chuỗi 1-2-5 (cột không tràn khung).
const BUOC = { chi_phi: [1, 2, 5, 10, 20, 50], token: [1e5, 2e5, 5e5, 1e6, 2e6, 5e6] }
const LUAT = {
  ok: { chu: 'Nhận việc', lop: 'tt-lam' },
  ngung: { chu: 'Ngừng — chạm ngưỡng', lop: 'tt-can_nguoi' },
  chi_p0_p1: { chu: 'Chỉ P0–P1 — tuần cao', lop: 'tt-cau_dao' },
  chua_biet: { chu: 'Chưa biết — vẫn nhận việc', lop: 'tt-cau_dao' },
}

const so = (x) => (typeof x === 'number' && Number.isFinite(x) ? x : 0)

// Tổng từ `theo_ngay`; `chi_phi_usd` = null khi không dòng nào có giá (như tram/usage/su_kien.py::tong_hop).
export function tongUsage(theoNgay) {
  const t = { token_vao: 0, token_ra: 0, token_cache_doc: 0, token_cache_ghi: 0, so_lan: 0, thieu_gia: 0 }
  let cp = null
  for (const d of theoNgay || []) {
    for (const k of Object.keys(t)) t[k] += so(d[k])
    if (typeof d.chi_phi_usd === 'number') cp = (cp ?? 0) + d.chi_phi_usd
  }
  return { ...t, chi_phi_usd: cp === null ? null : Math.round(cp * 1e4) / 1e4 }
}

// Sáu ô `.tq-so.us-so`: số gọn, rê chuột (`tieuDe`) ra số đầy đủ (D39).
export function oTong(dl) {
  const t = tongUsage(dl.theo_ngay)
  const cham = (dl.theo_nguon || []).find((d) => d.khoa === NGUON_CHAM)
  const lanCham = so(cham && cham.so_lan)
  const o = (gt, ten, phu = '', tieuDe = '') => ({ gt, ten, phu, tieuDe })
  const coGia = dl.co_bang_gia && t.chi_phi_usd !== null
  const thieu = t.thieu_gia ? ` · ${soDayDu(t.thieu_gia)} lần thiếu giá` : ''
  return [
    o(gon(t.token_vao), 'token vào', '', soDayDu(t.token_vao)),
    o(gon(t.token_ra), 'token ra', '', soDayDu(t.token_ra)),
    o(gon(t.token_cache_doc), 'cache đọc', '', soDayDu(t.token_cache_doc)),
    o(gon(t.token_cache_ghi), 'cache ghi', '', soDayDu(t.token_cache_ghi)),
    o(soDayDu(t.so_lan), 'lần gọi', `${soDayDu(t.so_lan - lanCham)} khe · ${soDayDu(lanCham)} chấm cột`),
    coGia ? o(usd(t.chi_phi_usd), 'chi phí ước tính', `API thật ${usd(cham ? cham.chi_phi_usd : 0)}${thieu}`)
      : o('—', 'chi phí ước tính', 'chưa có giá'),
  ]
}

// Mọi ngày từ `tu` đến `den` (YYYY-MM-DD, kể cả hai đầu) — biểu đồ có cột cả ngày không có sự kiện.
export function dayNgay(tu, den) {
  const re = /^\d{4}-\d{2}-\d{2}$/
  if (!re.test(String(tu)) || !re.test(String(den))) return []
  const ra = []
  for (let n = new Date(`${tu}T00:00:00Z`); ra.length < 400; n.setUTCDate(n.getUTCDate() + 1)) {
    const iso = n.toISOString().slice(0, 10)
    if (iso > den) break
    ra.push(iso)
  }
  return ra
}

export function khoangNgay(tu, den) {
  return `Từ ${ngayNgan(tu)} đến ${ngayNgan(den)}/${String(den).slice(0, 4)}`
}

// Nhãn ngày dưới cột: khoảng 10 mốc + luôn có hôm nay (mockup `moc`).
export function hienMocNgay(i, soCot, laNay) {
  return laNay || i % Math.max(1, Math.ceil(soCot / 10)) === 0
}

export function giaTriNgay(d, che) {
  if (!d) return 0
  return che === 'chi_phi' ? so(d.chi_phi_usd) : so(d.token_vao) + so(d.token_ra)
}

// Trần trục + 5 nhãn từ trên xuống ("$8" … "$0", "2,00 tr" … "0").
export function trucBieuDo(lon, che) {
  const buoc = [...(BUOC[che] || BUOC.token)]
  const can = Math.max(so(lon), 0.01)
  while (buoc.at(-1) * 4 < can) buoc.push(buoc.at(-3) * 10)
  const tran = buoc.find((b) => b * 4 >= can) * 4
  const nhan = (v) => (che === 'chi_phi' ? `$${v % 1 ? v.toFixed(1) : v}` : gon(v))
  return { tran, nhan: [4, 3, 2, 1, 0].map((i) => nhan((tran * i) / 4)) }
}

export function chieuCot(v, tran) {
  return tran > 0 ? Math.min(100, Math.max(0, (so(v) / tran) * 100)) : 0
}

// Cột Tỉ trọng (mockup bang tiTrong): theo chi phí, tối thiểu 2%; chưa có giá thì theo token vào + ra.
export function tiTrong(dong) {
  const ds = dong || []
  const cp = ds.map((d) => so(d.chi_phi_usd))
  const gt = cp.some((x) => x > 0) ? cp : ds.map((d) => so(d.token_vao) + so(d.token_ra))
  const tong = gt.reduce((a, x) => a + x, 0) || 1
  return gt.map((x) => Math.max(2, (x / tong) * 100))
}

// Tên + chấm màu của nguồn: khe → khe_id mono, màu thân khe (mau_khe.js); cham-cot → chấm xám.
export function nguonUsage(khoa) {
  if (khoa === NGUON_CHAM) return { ten: 'Bộ chấm cột (Claude API)', mono: false, mau: 'var(--xam)' }
  return { ten: String(khoa), mono: true, mau: mauKhe(khoa).than }
}

export function nhanLuat(muc) {
  return LUAT[muc] ?? LUAT.chua_biet
}

export function moiNhatTruoc(ds) {
  return [...(ds || [])].sort((a, b) => String(b.khoa).localeCompare(String(a.khoa)))
}

// ccusage trả {ngay, ...} → dòng bảng {khoa, ...}, mới nhất trước.
export function dongCcusage(cc) {
  return moiNhatTruoc(((cc && cc.theo_ngay) || []).map((d) => ({ ...d, khoa: d.ngay })))
}
```

`frontend/src/thanh/BangUsage.vue` (sửa):

```diff
diff --git a/frontend/src/thanh/BangUsage.vue b/frontend/src/thanh/BangUsage.vue
index 53f6182..aeb9667 100644
--- a/frontend/src/thanh/BangUsage.vue
+++ b/frontend/src/thanh/BangUsage.vue
@@ -1,39 +1,45 @@
 <script setup>
-import { dinhDangSo, dinhDangUsd, tenNguon } from '../luat_doi_ngu.js'
+import { computed } from 'vue'
+import '../kieu/khe.css'
+import '../kieu/usage.css'
+import { gon, soDayDu, usd } from '../dinh_dang.js'
+import { TRUONG_TOKEN, nguonUsage, tiTrong as tinhTiTrong } from '../luat_usage.js'
 
-defineProps({
-  tieuDe: { type: String, default: '' },
+// Bảng usage (mockup trang-usage.js bang()): số gọn "4,20 tr", rê chuột ra số đầy đủ (D39); "x thiếu giá";
+// cột Tỉ trọng tuỳ chọn; `cuon` = khung cuộn dọc, đầu bảng dính.
+const props = defineProps({
   tenKhoa: { type: String, required: true },
-  dong: { type: Array, required: true },          // [{khoa, token_vao, token_ra, token_cache_doc, token_cache_ghi, so_lan?, chi_phi_usd, thieu_gia?}]
+  dong: { type: Array, required: true },   // [{khoa, token_*, so_lan?, chi_phi_usd, thieu_gia?}]
   laNguon: { type: Boolean, default: false },
   coSoLan: { type: Boolean, default: true },
+  tiTrong: { type: Boolean, default: false },
+  cuon: { type: Boolean, default: false },
 })
+const tt = computed(() => (props.tiTrong ? tinhTiTrong(props.dong) : []))
+const nguon = computed(() => props.dong.map((d) => nguonUsage(d.khoa)))
+const TEN_COT = ['Token vào', 'Token ra', 'Cache đọc', 'Cache ghi']
 </script>
 
 <template>
-  <section class="bang-usage">
-    <h2 v-if="tieuDe">{{ tieuDe }}</h2>
-    <p v-if="!dong.length" class="nho">Không có số liệu trong khoảng này.</p>
-    <div v-else class="bang-cuon">
-      <table>
-        <thead><tr>
-          <th scope="col">{{ tenKhoa }}</th><th scope="col">Token vào</th><th scope="col">Token ra</th>
-          <th scope="col">Cache đọc</th><th scope="col">Cache ghi</th><th v-if="coSoLan" scope="col">Số lần gọi</th>
-          <th scope="col">Chi phí</th>
-        </tr></thead>
-        <tbody><tr v-for="d in dong" :key="d.khoa">
-          <th scope="row">{{ laNguon ? tenNguon(d.khoa) : d.khoa }}</th>
-          <td>{{ dinhDangSo(d.token_vao) }}</td><td>{{ dinhDangSo(d.token_ra) }}</td>
-          <td>{{ dinhDangSo(d.token_cache_doc) }}</td><td>{{ dinhDangSo(d.token_cache_ghi) }}</td>
-          <td v-if="coSoLan">{{ dinhDangSo(d.so_lan) }}</td>
-          <td>{{ dinhDangUsd(d.chi_phi_usd) }}<span v-if="d.thieu_gia && d.chi_phi_usd != null" class="nho">
-            · {{ d.thieu_gia }} lần thiếu giá</span></td>
-        </tr></tbody>
-      </table>
-    </div>
-  </section>
+  <p v-if="!dong.length" class="nho">Không có số liệu trong khoảng này.</p>
+  <div v-else class="us-bang" :class="{ cuon }">
+    <table class="bang">
+      <thead><tr>
+        <th scope="col">{{ tenKhoa }}</th><th v-for="t in TEN_COT" :key="t" scope="col">{{ t }}</th>
+        <th v-if="coSoLan" scope="col">Lần gọi</th><th scope="col">Chi phí</th>
+        <th v-if="tiTrong" scope="col" class="us-cot-tt">Tỉ trọng</th>
+      </tr></thead>
+      <tbody><tr v-for="(d, i) in dong" :key="d.khoa">
+        <th v-if="laNguon" scope="row"><span class="cham" :style="{ background: nguon[i].mau }" /><span
+          :class="{ mono: nguon[i].mono }">{{ nguon[i].ten }}</span></th>
+        <th v-else scope="row"><span class="mono">{{ d.khoa }}</span></th>
+        <td v-for="t in TRUONG_TOKEN" :key="t" class="so" :title="soDayDu(d[t])">{{ gon(d[t]) }}</td>
+        <td v-if="coSoLan" class="so">{{ soDayDu(d.so_lan) }}</td>
+        <td class="so">{{ usd(d.chi_phi_usd) }}<span v-if="d.thieu_gia && d.chi_phi_usd != null" class="us-thieu"
+          :title="`${d.thieu_gia} lần gọi chưa có giá — không tính vào chi phí`">{{ d.thieu_gia }} thiếu giá</span></td>
+        <td v-if="tiTrong"><div class="thanh-hm us-tt" role="img" :aria-label="`Tỉ trọng ${Math.round(tt[i])}%`">
+          <i :style="{ width: `${tt[i]}%` }" /></div></td>
+      </tr></tbody>
+    </table>
+  </div>
 </template>
-
-<style scoped>
-.bang-usage { margin-bottom: 1.25rem; }
-</style>
```

`frontend/src/thanh/usage/BieuDoUsage.vue` (mới):

```vue
<script setup>
import { computed } from 'vue'
import '../../kieu/usage.css'
import { gon, ngayNgan, soDayDu, usd } from '../../dinh_dang.js'
import { chieuCot, dayNgay, giaTriNgay, hienMocNgay, trucBieuDo } from '../../luat_usage.js'

// Biểu đồ cột theo ngày (mockup trang-usage.js bieuDo): mỗi ngày tu..den một cột, cột hôm nay (`den`) đậm;
// rê chuột hoặc Tab tới cột (tabindex=0) hiện tooltip `.us-tip`. `che`: 'chi_phi' | 'token' (vào + ra).
const props = defineProps({
  theoNgay: { type: Array, required: true },
  tu: { type: String, required: true },
  den: { type: String, required: true },
  che: { type: String, default: 'chi_phi' },
})
const KE = [1, 2, 3, 4]

const cot = computed(() => {
  const m = Object.fromEntries(props.theoNgay.map((d) => [d.khoa, d]))
  return dayNgay(props.tu, props.den).map((ngay) => {
    const c = { ngay, d: m[ngay], nay: ngay === props.den }
    return { ...c, tip: tip(c) }
  })
})
const truc = computed(() => trucBieuDo(Math.max(0, ...cot.value.map((c) => giaTriNgay(c.d, props.che))), props.che))

function tip(c) {
  const dau = `${ngayNgan(c.ngay)}${c.nay ? ' · hôm nay' : ''}`
  if (!c.d) return [dau, 'không có sự kiện', '']
  return [dau, `${usd(c.d.chi_phi_usd)} · ${soDayDu(c.d.so_lan)} lần`,
    `${gon(c.d.token_vao)} vào · ${gon(c.d.token_ra)} ra`]
}
</script>

<template>
  <div class="us-bd">
    <div class="us-truc" aria-hidden="true"><span v-for="(n, i) in truc.nhan" :key="i">{{ n }}</span></div>
    <div class="us-vung">
      <i v-for="k in KE" :key="k" class="us-ke" :style="{ bottom: `${k * 25}%` }" />
      <div v-for="(c, i) in cot" :key="c.ngay" class="us-cot" :class="{ nay: c.nay }" tabindex="0" role="img"
        :aria-label="c.tip.filter(Boolean).join(' · ')">
        <b :style="{ height: `${chieuCot(giaTriNgay(c.d, che), truc.tran)}%` }" />
        <span class="us-tip" aria-hidden="true"><strong>{{ c.tip[0] }}</strong>{{ c.tip[1] }}<template
          v-if="c.tip[2]"><br>{{ c.tip[2] }}</template></span>
        <em v-if="hienMocNgay(i, cot.length, c.nay)" aria-hidden="true">{{ ngayNgan(c.ngay) }}</em>
      </div>
    </div>
  </div>
</template>
```

`frontend/src/thanh/usage/KhoiCcusage.vue` (mới):

```vue
<script setup>
import { computed } from 'vue'
import '../../kieu/usage.css'
import { dongCcusage } from '../../luat_usage.js'
import BangUsage from '../BangUsage.vue'

// Khối ccusage (mockup trang-usage.js khoiCcusage): chua_cau_hinh / loi / bảng theo ngày (không cột lần gọi).
// Bỏ nhóm nút "minh hoạ" trạng thái của mockup — trạng thái thật lấy từ /api/usage `ccusage.trang_thai` (D39).
const props = defineProps({ ccusage: { type: Object, required: true } })  // {trang_thai, theo_ngay, loi, phien_ban}
const dong = computed(() => dongCcusage(props.ccusage))
</script>

<template>
  <section class="the us-khoi">
    <h3 class="tq-h">ccusage — toàn bộ Claude Code của tài khoản trạm trên máy B</h3>
    <p v-if="ccusage.trang_thai === 'chua_cau_hinh'" class="nho">Chưa cấu hình ccusage
      (<span class="mono">usage.ccusage</span> trong <span class="mono">~/.tram/cau-hinh.yaml</span>).</p>
    <div v-else-if="ccusage.trang_thai === 'loi'" class="canh-bao" role="alert">{{ ccusage.loi || 'ccusage lỗi' }}</div>
    <template v-else>
      <p class="nho">ccusage {{ ccusage.phien_ban }} — số liệu giữ tối đa 10 phút. Gồm cả phiên Claude Code không do
        khe chạy, nên lớn hơn dòng khe ở trên.</p>
      <BangUsage ten-khoa="Ngày" :dong="dong" :co-so-lan="false" cuon />
    </template>
  </section>
</template>
```

`frontend/src/thanh/usage/KhoiHanMuc.vue` (mới):

```vue
<script setup>
import { onMounted, onUnmounted, ref, watch } from 'vue'
import '../../kieu/khe.css'
import '../../kieu/usage.css'
import { doc } from '../../api.js'
import { kho } from '../../kho.js'
import { cuaSo, oHanMuc, tenKhe } from '../../luat_han_muc.js'
import { nguonUsage, nhanLuat } from '../../luat_usage.js'

// Khối "Hạn mức thuê bao của khe" (mockup trang-usage.js khoiHanMuc, D39): đọc /api/doi-ngu mỗi 5 giây như trang
// Đội ngũ AI, và ngay khi có sự kiện doi_ngu_doi. Cột luật nhận việc theo `muc_han_muc` server đã tính.
const CHU_KY_MS = 5000
const ds = ref(null)
const loi = ref('')
let hen = null

async function tai() {
  try {
    ds.value = ((await doc('/api/doi-ngu')).khe || []).map((k) => ({
      k, nguon: nguonUsage(k.khe_id), luat: nhanLuat(k.muc_han_muc),
      o: [oHanMuc(cuaSo(k, '5h')), oHanMuc(cuaSo(k, 'tuan'))],
    }))
    loi.value = ''
  } catch (e) {
    loi.value = e.message
  }
}
onMounted(() => { tai(); hen = setInterval(tai, CHU_KY_MS) })
onUnmounted(() => clearInterval(hen))
watch(() => kho.phienBanDoiNgu, tai)
</script>

<template>
  <section class="the us-khoi">
    <h3 class="tq-h">Hạn mức thuê bao của khe <span class="nho us-h-phu">từ <span class="mono">/api/doi-ngu</span> ·
      đọc mỗi 5 giây</span><router-link class="nho us-lk" to="/doi-ngu">Mở Đội ngũ AI →</router-link></h3>
    <p v-if="loi" class="loi" role="alert">{{ loi }}</p>
    <p v-if="ds && !ds.length" class="nho">Chưa có khe nào đăng ký với trạm.</p>
    <div v-if="ds && ds.length" class="bang-cuon">
      <table class="bang us-hm">
        <thead><tr><th scope="col">Khe</th><th scope="col">Cửa sổ 5 giờ</th><th scope="col">Cửa sổ tuần</th>
          <th scope="col">Luật nhận việc</th></tr></thead>
        <tbody><tr v-for="x in ds" :key="x.k.khe_id">
          <th scope="row" :title="tenKhe(x.k)"><span class="cham" :style="{ background: x.nguon.mau }" /><span
            class="mono">{{ x.k.khe_id }}</span></th>
          <td v-for="(o, i) in x.o" :key="i"><div class="us-o-hm">
            <div class="thanh-hm" role="img" :aria-label="o.chu"><i v-if="o.con !== null" :class="o.lop"
              :style="{ width: `${o.rong}%` }" /></div>
            <span :class="{ nho: o.con === null }">{{ o.chu }}</span>
          </div></td>
          <td><span class="chip" :class="x.luat.lop">{{ x.luat.chu }}</span></td>
        </tr></tbody>
      </table>
    </div>
    <p class="nho us-giai">Đã dùng ≥ 90% một cửa sổ thì khe ngừng nhận việc; tuần cao chỉ nhận P0–P1; chưa biết vẫn
      nhận việc kèm cảnh báo vàng. Giá trên trang này là tương đương — hạn mức mới là giới hạn thật của khe thuê
      bao.</p>
  </section>
</template>
```

`frontend/src/trang/Usage.vue` (sửa):

```diff
diff --git a/frontend/src/trang/Usage.vue b/frontend/src/trang/Usage.vue
index ae4b0fd..49dd8a6 100644
--- a/frontend/src/trang/Usage.vue
+++ b/frontend/src/trang/Usage.vue
@@ -1,14 +1,26 @@
 <script setup>
 import { computed, onMounted, ref, watch } from 'vue'
+import '../kieu/usage.css'
 import { doc } from '../api.js'
 import { kho } from '../kho.js'
+import { SO_NGAY_USAGE, khoangNgay, moiNhatTruoc, oTong } from '../luat_usage.js'
 import BangUsage from '../thanh/BangUsage.vue'
+import DauTrang from '../thanh/DauTrang.vue'
+import BieuDoUsage from '../thanh/usage/BieuDoUsage.vue'
+import KhoiCcusage from '../thanh/usage/KhoiCcusage.vue'
+import KhoiHanMuc from '../thanh/usage/KhoiHanMuc.vue'
 
-const SO_NGAY = [7, 14, 30, 92]
+// Trang Usage & chi phí (mockup trang-usage.js veUsage, D36; D39: số gọn + title, giữ khối hạn mức, bỏ phần
+// "minh hoạ"). Dữ liệu GET /api/usage?so_ngay=; tải lại khi đổi khoảng và khi có sự kiện doi_ngu_doi.
+const MO_TA = 'Token và chi phí từ sự kiện của trạm: mỗi lần chạy CLI của khe và mỗi lần bộ chấm cột gọi Claude '
+  + 'API. Ngày theo giờ Việt Nam, tuần theo ISO.'
+const CHE = [['chi_phi', 'Chi phí'], ['token', 'Token vào + ra']]
 const soNgay = ref(14)
+const che = ref('chi_phi')
 const dl = ref(null)
 const loi = ref('')
-const ccusage = computed(() => (dl.value ? dl.value.ccusage.theo_ngay.map((d) => ({ ...d, khoa: d.ngay })) : []))
+const o = computed(() => (dl.value ? oTong(dl.value) : []))
+const cheThat = computed(() => (dl.value && dl.value.co_bang_gia ? che.value : 'token'))   // không có giá → token
 
 async function tai() {
   try {
@@ -24,34 +36,47 @@ watch(() => kho.phienBanDoiNgu, tai)
 </script>
 
 <template>
-  <section>
-    <h1>Usage</h1>
-    <div class="cong-cu">
-      <label>Khoảng
-        <select v-model.number="soNgay">
-          <option v-for="n in SO_NGAY" :key="n" :value="n">{{ n }} ngày gần nhất</option>
-        </select>
-      </label>
-    </div>
+  <div class="us-trang">
+    <DauTrang tieu-de="Usage & chi phí" :mo-ta="MO_TA">
+      <template #cong-cu>
+        <span v-if="dl" class="nho">{{ khoangNgay(dl.tu, dl.den) }}</span>
+        <div class="nhom-nut" role="group" aria-label="Khoảng">
+          <button v-for="n in SO_NGAY_USAGE" :key="n" type="button" :class="{ chon: n === soNgay }"
+            :aria-pressed="n === soNgay" @click="soNgay = n">{{ n }} ngày</button>
+        </div>
+      </template>
+    </DauTrang>
     <p v-if="loi" class="loi" role="alert">{{ loi }}</p>
     <template v-if="dl">
-      <p class="nho">Từ {{ dl.tu }} đến {{ dl.den }} (ngày theo giờ Việt Nam). Nguồn: sự kiện của trạm — mỗi lần
-        chạy CLI của khe và mỗi lần bộ chấm cột gọi Claude API. Chi phí của khe (gói thuê bao) là giá tương đương theo
-        bảng giá, không phải tiền trả thêm.
-        <template v-if="!dl.co_bang_gia"> Chưa có bảng giá (<code>usage.gia_usd_moi_trieu_token</code>) — chi phí để
-          trống.</template></p>
-      <BangUsage tieu-de="Theo ngày" ten-khoa="Ngày" :dong="dl.theo_ngay" />
-      <BangUsage tieu-de="Theo tuần" ten-khoa="Tuần (ISO)" :dong="dl.theo_tuan" />
-      <BangUsage tieu-de="Theo khe" ten-khoa="Khe / nguồn" :dong="dl.theo_nguon" la-nguon />
-      <BangUsage tieu-de="Theo dự án" ten-khoa="Dự án" :dong="dl.theo_du_an" />
-      <h2>ccusage — toàn bộ Claude Code của tài khoản trạm trên máy B</h2>
-      <p v-if="dl.ccusage.trang_thai === 'chua_cau_hinh'" class="nho">Chưa cấu hình ccusage
-        (<code>usage.ccusage</code> trong <code>~/.tram/cau-hinh.yaml</code>).</p>
-      <p v-else-if="dl.ccusage.trang_thai === 'loi'" class="loi">{{ dl.ccusage.loi }}</p>
-      <template v-else>
-        <p class="nho">ccusage {{ dl.ccusage.phien_ban }} — số liệu giữ tối đa 10 phút.</p>
-        <BangUsage ten-khoa="Ngày" :dong="ccusage" :co-so-lan="false" />
-      </template>
+      <p class="nho us-ghi"><span>Chi phí của khe (gói thuê bao) là <b>giá tương đương</b> theo bảng giá, không phải
+        tiền trả thêm; chỉ bộ chấm cột là tiền API thật.</span></p>
+      <div v-if="!dl.co_bang_gia" class="canh-bao us-canh">Chưa có bảng giá
+        (<span class="mono">usage.gia_usd_moi_trieu_token</span>) — chi phí để trống.</div>
+      <div class="tq-so us-so">
+        <div v-for="x in o" :key="x.ten" :title="x.tieuDe || null"><b>{{ x.gt }}</b><span class="nho">{{ x.ten }}</span>
+          <span v-if="x.phu" class="nho us-phu">{{ x.phu }}</span></div>
+      </div>
+      <section class="the us-the-bd">
+        <h3 class="tq-h">Theo ngày
+          <span v-if="dl.co_bang_gia" class="nhom-nut us-phai" role="group" aria-label="Đại lượng">
+            <button v-for="[m, ten] in CHE" :key="m" type="button" :class="{ chon: m === che }"
+              :aria-pressed="m === che" @click="che = m">{{ ten }}</button>
+          </span></h3>
+        <BieuDoUsage :theo-ngay="dl.theo_ngay" :tu="dl.tu" :den="dl.den" :che="cheThat" />
+      </section>
+      <section class="the us-khoi"><h3 class="tq-h">Theo khe / nguồn</h3>
+        <BangUsage ten-khoa="Khe / nguồn" :dong="dl.theo_nguon" la-nguon ti-trong /></section>
+      <div class="tq-luoi us-luoi">
+        <section class="the"><h3 class="tq-h">Theo dự án</h3>
+          <BangUsage ten-khoa="Dự án" :dong="dl.theo_du_an" /></section>
+        <section class="the"><h3 class="tq-h">Theo tuần</h3>
+          <BangUsage ten-khoa="Tuần (ISO)" :dong="moiNhatTruoc(dl.theo_tuan)" /></section>
+      </div>
+      <section class="the us-khoi"><h3 class="tq-h">Theo ngày <span class="nho us-h-phu">{{ dl.theo_ngay.length }} ngày
+        có sự kiện · mới nhất trước</span></h3>
+        <BangUsage ten-khoa="Ngày" :dong="moiNhatTruoc(dl.theo_ngay)" cuon /></section>
     </template>
-  </section>
+    <KhoiHanMuc />
+    <KhoiCcusage v-if="dl" :ccusage="dl.ccusage" />
+  </div>
 </template>
```

- [ ] **Step 4: Chạy thấy PASS**

```bash
cd frontend && node --test tests/usage.test.mjs
npm run kiem && npm run build && npm run kiem-dist && cd ..
```

Kỳ vọng: PASS — lệnh test của task: pass 6 · fail 0; toàn bộ tăng đúng 6 node test so với main trước task (bảng "Sơ đồ đợt chạy"); `npm run build`, `npm run kiem-dist` xanh. Số đo trên bản chạy thử.

- [ ] **Step 5: Commit**

```bash
git add frontend/tests/usage.test.mjs frontend/src/kieu/usage.css frontend/src/luat_usage.js frontend/src/thanh/BangUsage.vue frontend/src/thanh/usage/BieuDoUsage.vue frontend/src/thanh/usage/KhoiCcusage.vue frontend/src/thanh/usage/KhoiHanMuc.vue frontend/src/trang/Usage.vue
git commit -m "feat(dashboard): 2f trang Usage & chi phí (D39)"
```

### Task 18: Kiểm trên trình duyệt dưới CSP thật, so với ảnh mockup + ghi chú triển khai

**Đợt:** 4 · **Độ khó:** vừa · **Phải xong trước:** Task 1–17 · **Test mới:** — (cổng là trình duyệt; như 2c T8)

**Mockup bám:** mọi ảnh `docs/mockup/2026-10-15-giao-dien/anh-*.png`.

**Files:**
- Create: `tests/du_lieu_giao_dien.py` (gieo dữ liệu giả giống `du-lieu.js`, `du-lieu-ky-uc-usage.js`), `tests/chay_thu_giao_dien.py` (tram-api thật — `GiuaAnToan`, CSP thật — trên `127.0.0.1:7798` với `BdGia`, kho sự kiện tạm, memory giả, `DocHeThong` với bộ chạy giả; `--dai-ca` gắn header danh tính Đại ca giả CHỈ để kiểm tay). Không phải test pytest (tên không bắt đầu `test_`); không mạng, không `~/.tram`, Keychain, launchctl, beads thật.
- Modify: `docs/plans/2026-10-16-lat-2f-2-cac-trang.md` — thêm mục "Ghi chú triển khai" cuối file (kết quả từng bước dưới đây, ảnh chụp lưu ở `docs/mockup/2026-10-15-giao-dien/that-*.png` nếu Đại ca muốn so).

- [ ] **Step 1: Viết máy chủ dữ liệu giả (chép nguyên văn)**

`tests/du_lieu_giao_dien.py` (mới):

```python
"""Dữ liệu GIẢ cho máy chủ kiểm giao diện lát 2f (`tests/chay_thu_giao_dien.py`) — CHỈ DÙNG KHI KIỂM TAY, không phải
test pytest. Bám mockup `docs/mockup/2026-10-15-giao-dien/du-lieu.js`, `du-lieu-ky-uc-usage.js`; giờ lùi từ `LUC`."""
import random
from datetime import datetime, timedelta, timezone

from bead_gia import bead, notes_ban_giao
from kho_phieu_gia import dat_phieu
from tram.han_muc.mo_hinh import CuaSo, HanMuc
from tram.phieu.cau_dao import ngat_cau_dao
from tram.phieu.khe import bat_tat_khe, dang_ky_khe
from tram.phieu.kho import chuoi_gio as iso
from tram.phieu.nhip_tim import ghi_nhip

LUC = datetime.now(timezone.utc).replace(microsecond=0)
P, NGAY = timedelta(minutes=1), timedelta(days=1)
C2, C4, URL = "2" * 40, "4" * 40, "https://github.com/dai-ca/hr-codex/pull/"     # commit_ban_giao hr-2, hr-4
# khe, cli, tên gợi nhớ, vai, hạn mức ĐÃ dùng (5h %, phút tới reset 5h, tuần %) — mockup ghi phần "còn"
KHE = [("claude-1", "claude", "claude-chinh", ["coder"], (38, 83, 19)),
       ("claude-2", "claude", "claude-phu", ["coder", "qc"], (6, 178, 30)),
       ("codex-1", "codex", "codex-chinh", ["qc"], (52, 38, 43)),
       ("claude-3", "claude", "claude-de-danh", ["coder"], (0, None, 8)),
       ("codex-2", "codex", "codex-phu", ["coder"], None),                     # không nhịp tim → mất kết nối
       ("claude-4", "claude", "claude-thu", ["spec"], (100, 115, 66))]
SONNET, CODEX, HAIKU = "claude-sonnet-4-5", "gpt-5-codex", "claude-haiku-4-5"   # "o3-cu": mô hình thiếu giá
GIA = {SONNET: {"vao": 3, "ra": 15, "cache_doc": 0.3, "cache_ghi": 3.75},
       CODEX: {"vao": 1.25, "ra": 10, "cache_doc": 0.125, "cache_ghi": 0},
       HAIKU: {"vao": 1, "ra": 5, "cache_doc": 0.1, "cache_ghi": 1.25}}
CAU_HOI = "Tính thuế trên giá trước hay sau chiết khấu? Làm tròn theo từng dòng hay theo tổng hoá đơn?"
KY_UC = [  # (phạm vi, nhãn, nội dung, quan trọng, loại nguồn, bead nguồn, số ngày trước — âm: chờ hiệu lực, lần dùng)
    ("/du-an/hr-codex/nghiep-vu", "mau-in", "Đổi template hoá đơn thì chạy test mẫu in.", .55, "agent", "hr-2", 0, 0),
    ("/du-an/hr-codex/cach-lam", "ruff", "Chạy `ruff check .` trước `uv run pytest`.", .5, "agent", "hr-2", 0, 0),
    ("/vai/coder", "lenh", "Trước khi báo xong, chạy đủ lệnh được phép theo thứ tự.", .55, "thang_cap", None, -7, 0),
    ("/du-an/hr-codex/nghiep-vu", "hoa-don", "Hoá đơn làm tròn đến đồng ở tổng cuối.", .8, "da_chot", "hr-2", 1, 1),
    ("/du-an/tram/cach-lam", "csp", "Route mới trong tram/api đi qua GiuaAnToan.", .5, "agent", "bs-1", 1, 1),
    ("/du-an/hr-codex/nghiep-vu", "ngay", "Phiếu lương hiện ngày dạng dd/mm/yyyy.", .8, "da_chot", "hr-5", 2, 3),
    ("/chung", "chu", "Chữ hiện cho người dùng viết tiếng Việt có dấu.", .8, "dai_ca_ghi", None, 4, 14),
    ("/vai/qc", "nghiem-thu", "QC đối chiếu từng tiêu chí nghiệm thu với diff.", .65, "thang_cap", None, 12, 6)]


def ky_uc() -> list[dict]:
    return [{"id": f"m-{i:024x}", "noi_dung": nd, "pham_vi": pv, "nhan": [nh], "quan_trong": qt,
             "nguon": [{"loai": lo, "du_an": "tram" if "tram" in pv else "hr-codex", **({"bead_id": b} if b else {})}],
             "nguon_dai_ca": lo in ("da_chot", "dai_ca_ghi"), "tao_luc": iso(LUC - max(n, 0) * NGAY - i * 60 * P),
             "hieu_luc_tu": iso(LUC - n * NGAY - i * 60 * P), "dung_luc": iso(LUC - i * 30 * P) if d else None,
             "so_lan_dung": d} for i, (pv, nh, nd, qt, lo, b, n, d) in enumerate(KY_UC)]


def cac_bead(g3: str) -> dict[str, list]:
    esc = f"ly_do: agent-can-hoi\nbead_goc: hr-3\ngiao_id: {g3}\n\n{CAU_HOI}"          # mẫu 4a-1
    return {"hr-codex": [
        bead("hr-1", title="Sửa cắt UTF-8 tóm tắt hoàn tiền", issue_type="bug", priority=1, labels=["cot:ai-lam"],
             status="in_progress", assignee="tram/giao-viec", acceptance_criteria="- Cắt theo ký tự, không theo byte"),
        bead("hr-3", title="Chọn cách tính thuế", priority=2, labels=["cot:can-chot"]),
        bead("hr-2", title="Xem lại hoá đơn", priority=2, labels=["cot:cho-review"],
             notes=notes_ban_giao(nhanh="tram/hr-2", commit=C2, pr=URL + "12")),
        bead("hr-4", title="Kiểm định dạng mã số thuế", issue_type="feature", priority=3, labels=["cot:cho-review"],
             notes=notes_ban_giao(nhanh="tram/hr-4", commit=C4, pr=URL + "11")),
        bead("hr-5", title="Sửa định dạng ngày trên phiếu lương", status="closed", closed_at=iso(LUC - 95 * P)),
        bead("hr-6", title="Hỏi: cách tính thuế cho hr-3", priority=1, issue_type="decision",
             labels=["tram:escalation"], description=esc),
        bead("hr-7", title="Thêm bộ lọc phòng ban cho báo cáo lương", priority=3)],             # chưa chấm
        "tram": [bead("bs-1", title="Đèn điều phối theo nhịp hook", labels=["cot:ai-lam"], priority=2)],
        "ke-toan": [bead("kt-1", title="Đối chiếu sổ cái tháng 9", priority=2)]}


def _usage_cu(kho, r: random.Random) -> None:
    """20 ngày `chay.xong` (khe) + `cham_cot.ket_qua` (cham-cot) có token cho trang Usage (tram/usage/su_kien.py)."""
    for n in range(20, 0, -1):
        for khe, mh in (("claude-1", SONNET), ("claude-2", SONNET), ("codex-1", CODEX), ("claude-3", SONNET),
                        ("claude-4", "o3-cu" if n > 15 else SONNET), *[(None, HAIKU)] * 3):
            for _ in range(r.randint(0, 2) if khe else 1):
                v = r.randint(110_000, 230_000) if khe else r.randint(30_000, 90_000)
                dl = {"khe_id": f"B/{khe}", "luot": 1, "ket_thuc": "xong", "token_cache_doc": v * 3} if khe else {}
                kho.ghi_su_kien(r.choice(["hr-codex", "tram", "ke-toan"]), "chay.xong" if khe else "cham_cot.ket_qua",
                                dl, luc=LUC - n * NGAY, token_vao=v, token_ra=v // 9, mo_hinh=mh)


def gieo(kho) -> str:
    """Khe + nhịp tim + phiếu + sự kiện (cũ → mới, đúng thứ tự id). Trả `giao_id` phiếu QC của codex-1 (hr-3)."""
    with kho.giao_dich():
        dang_ky_khe(kho, "B", [{"ten": t, "cli": c, "ten_goi_nho": g, "vai_uu_tien": v} for t, c, g, v, _ in KHE],
                    luc=LUC - 30 * NGAY)
        _usage_cu(kho, random.Random(20261015))
    g1 = dat_phieu(kho, "B/claude-1", luc=LUC, bead_id="hr-1", tieu_de="Sửa cắt UTF-8 tóm tắt hoàn tiền").giao_id
    g3 = dat_phieu(kho, "B/codex-1", luc=LUC, bead_id="hr-3", tieu_de="Chọn cách tính thuế", buoc="qc").giao_id
    hr, he, k1, tok = "hr-codex", "_tram", {"khe_id": "B/claude-1"}, {"token_vao": 520_000, "token_ra": 61_000}
    su_kien = [  # (phút trước LUC, dự án, loại, bead, dữ liệu[, cột riêng]) — cũ → mới
        (100, "tram", "quet.loi", None, {"loi": "bd timeout"}), (95, hr, "bead.dong", "hr-5", {}),
        (90, hr, "bead.vao_cot_3", "hr-4", {"commit_ban_giao": C4}),
        (85, hr, "pr.mo", "hr-4", {"loai": "bead", "pr": 11, "url": URL + "11", "commit": C4}),
        (80, hr, "pr.da_merge", "hr-4", {"pr": 11, "commit": C4}), (70, hr, "qc.ket_qua", "hr-2", {"ket_luan": "dat"}),
        (69, hr, "bead.vao_cot_3", "hr-2", {"commit_ban_giao": C2}),
        (68, hr, "pr.mo", "hr-2", {"loai": "bead", "pr": 12, "url": URL + "12", "commit": C2}),
        *[(60, hr, "nho.ghi", "hr-2", {"id": f"m-{i:024x}", "pham_vi": KY_UC[i][0]}) for i in (0, 1)],
        (55, hr, "pr.khong_xac_minh", "hr-2", {"pr": 12, "commit": C2, "ly_do": "khong-phai-merge-commit"}),
        (50, he, "khe.tat", None, {}), (48, hr, "nho.loi_embedder", "hr-1", {"su_kien_id": 4051}),
        (45, hr, "giao.nhan", "hr-3", {"giao_id": g3, "khe_id": "B/codex-1", "buoc": "qc"}),
        (44, hr, "nho.phuc_hoi", "hr-1", {"loai": "embedder"}),
        (40, hr, "cham_cot.ket_qua", "hr-1", {"cot": "ai-lam", "ly_do": "Lỗi rõ, có test tái hiện."}),
        (39, hr, "cham_cot.ket_qua", "hr-3", {"cot": "can-chot", "ly_do": "Hai cách tính hợp lệ.",
                                              "cau_hoi": CAU_HOI.split("? ")}, {"token_vao": 41_000, "mo_hinh": HAIKU}),
        (38, hr, "giao.nhan", "hr-1", {"giao_id": g1, **k1, "buoc": "code"}), (30, he, "khe.cau_dao_ngat", None, {}),
        (28, hr, "escalation.tao", "hr-6", {"escalation_id": "hr-6", "bead_goc": "hr-3", "giao_id": g3,
                                            "ly_do": "agent-can-hoi"}),
        (28, hr, "bao.can_hoi", "hr-3", {"giao_id": g3, "loai_hoi": "can_quyet_dinh"}, {"tac_nhan": "tho/B/codex-1"}),
        (25, hr, "chay.bat_dau", "hr-1", {**k1, "luot": 1}),
        *[(20, hr, "chay.xong", b, {"khe_id": f"B/{k}", "luot": 1, "ket_thuc": kt}, {**tok, "mo_hinh": m})
          for k, b, m, kt in (("claude-1", "hr-1", SONNET, "loi"), ("codex-1", "hr-3", CODEX, "xong"),
                              ("claude-2", "hr-2", SONNET, "xong"), ("claude-4", None, SONNET, "xong"))],
        (10, hr, "chay.bat_dau", "hr-1", {**k1, "luot": 2}),
        *[(3, d, "quet.xong", None, {"da_cham": n}) for d, n in ((hr, 4), ("tram", 1), ("ke-toan", 1))],
        (1, he, "dieu_phoi.nhip", None, {"su_kien": "Stop", "phien": "0" * 16}, {"tac_nhan": "dai-ca/may-a"})]
    with kho.giao_dich():
        for phut, du_an, loai, b, dl, *kw in su_kien:
            luc = LUC - phut * P
            if loai == "khe.tat":
                bat_tat_khe(kho, "B/claude-3", bat=False, vi_sao="để dành", tac_nhan="dai-ca", luc=luc)
            elif loai == "khe.cau_dao_ngat":
                ngat_cau_dao(kho, "B/claude-4", ly_do="het-han-muc", toi_luc=LUC + 115 * P, luc=luc)
            else:
                kho.ghi_su_kien(du_an, loai, dl, luc=luc, bead_id=b, **(kw[0] if kw else {}))
        for t, *_, hm in (k for k in KHE if k[4]):                              # nhịp tim kèm hạn mức 5h / tuần
            cs = [CuaSo(loai=ten, trang_thai="biet", phan_tram=x, doc_luc=iso(LUC), reset_luc=r and iso(LUC + r * P))
                  for ten, x, r in (("5h", hm[0], hm[1]), ("tuan", hm[2], 4 * 24 * 60))]
            ghi_nhip(kho, f"B/{t}", luc=LUC, giao_id=None, luot=None, buoc_tho="ranh",
                     han_muc=HanMuc(khe_id=f"B/{t}", cua_so=cs, nguon="stream"))
    return g3
```

`tests/chay_thu_giao_dien.py` (mới):

```python
"""Chạy tram-api với dữ liệu GIẢ (`tests/du_lieu_giao_dien.py`) để kiểm tay giao diện lát 2f — CHỈ DÙNG KHI KIỂM.

`uv run python tests/chay_thu_giao_dien.py [cong] [--dai-ca]` (mặc định 7798) sau `npm run build`. Mọi thứ trong thư mục
tạm (TRAM_HOME, su-kien.db, TRAM_REPO/du-an, HOME giả có plist); bd, launchctl, security, memory service đều giả — không
mạng, không ~/.tram, Keychain, launchctl, beads thật. `--dai-ca`: lớp ASGI CHỈ ĐỂ KIỂM TAY, gắn `Tailscale-User-Login`
của Đại ca giả + đổi Origin cục bộ thành máy B giả (xem Cài đặt, Ký ức, nút ghi). Không phải test pytest."""
import os
import sys
import tempfile
from collections import Counter
from dataclasses import dataclass, replace
from pathlib import Path
from types import SimpleNamespace

TAM = Path(tempfile.mkdtemp(prefix="tram-giao-dien-"))
os.environ["TRAM_HOME"] = str(TAM / "tram-home")
os.environ["TRAM_REPO"] = str(TAM / "repo")                   # nap_du_an đọc TRAM_REPO/du-an/<ten>.yaml

import uvicorn  # noqa: E402
import yaml  # noqa: E402

from api_gia import LOGIN, MAY_B, tao_pt  # noqa: E402
from bd_gia import BdGia  # noqa: E402
from bead_gia import bead  # noqa: E402
from du_lieu_giao_dien import GIA, LUC, cac_bead, gieo, iso, ky_uc  # noqa: E402
from tram.api.app import tao_app  # noqa: E402
from tram.cau_hinh.du_an import nap_du_an  # noqa: E402
from tram.phieu.kho import KhoPhieu  # noqa: E402
from tram.suy import he_thong, san_sang  # noqa: E402

# tên → (đường dẫn dưới ~, gitnexus, lệnh cho phép, hàng rào {loại: từ khoá}) — mockup CAU_HINH_DU_AN
DU_AN = {"hr-codex": ("Developer/hr-codex", "hr-codex", ["uv run pytest -q", "uv run ruff check ."],
                      {"tien": ["hoàn tiền", "thuế", "hoá đơn"], "quyen": ["phân quyền", "vai trò"]}),
         "tram": ("Developer/Ben Station", "ben-station", ["uv run pytest -q", "npm --prefix frontend test"],
                  {"quyen": ["CSP", "danh tính", "token"]}),
         "ke-toan": ("Developer/ke-toan", None, ["uv run pytest -q"], {"tien": ["sổ cái", "bút toán"]})}
SAN_SANG = [("bs-g28.9", "Tailscale máy B đã đăng nhập", "closed", ()),          # mockup SAN_SANG (bead repo trạm)
            ("bs-8eh.17", "Tailscale máy A (Đại ca cài, D6)", "open", ()),
            ("bs-urj.4", "Kickstart vn.tram.nho sau ghép 1b-4 T4 (D11)", "open", ("bs-8eh.1",)),
            ("bs-8eh.1", "1b-2 T10 — /nho, mã Đại ca, tram-noi-bo-token", "open", ()),
            ("bs-hpc.5", "1b-1 memory: dịch vụ, Keychain, M1/M2, recall", "closed", ())]
DANG_CHAY = ("vn.tram.api", "vn.tram.quet", "vn.tram.nho", "vn.tram.bao-tin")      # vn.tram.sao-luu: chưa cài


def chay_gia(argv: list[str]) -> tuple[int, str]:
    """Bộ chạy giả cho `DocHeThong`: launchctl (4 dịch vụ chạy), security (thiếu `tram-noi-bo-token`)."""
    if argv[0] == "launchctl":
        return (0, "state = running\n") if argv[-1].rsplit("/", 1)[-1] in DANG_CHAY else (113, "")
    return (44, "") if argv[-1] == "tram-noi-bo-token" else (0, "")


@dataclass
class NhoGia:
    """Memory service giả (như `KhachGia` của tests/test_api_nho.py) — `/danh-sach`, `/ghi`, `/xoa` trong bộ nhớ."""
    ds: list[dict]

    def goi(self, duong: str, than: dict, *, thoi_gian_cho: float) -> dict:
        bay = iso(LUC)
        if duong == "/ghi":
            k = {"id": f"m-tay{len(self.ds):020x}", "noi_dung": than["noi_dung"], "pham_vi": than["pham_vi"],
                 "nhan": than.get("nhan") or [], "quan_trong": 0.8, "nguon": [{"loai": "dai_ca_ghi"}],
                 "nguon_dai_ca": True, "tao_luc": bay, "hieu_luc_tu": bay, "dung_luc": None, "so_lan_dung": 0}
            self.ds.insert(0, k)
            return {"id": k["id"], "pham_vi": k["pham_vi"], "xoa": [], "lap_lai": False}
        if duong == "/xoa":
            self.ds = [k for k in self.ds if k["id"] != than["id"]]
            return {"da_xoa": True}
        so = Counter(k["pham_vi"] for k in self.ds)
        cho = Counter(k["pham_vi"] for k in self.ds if k["hieu_luc_tu"] > bay)
        ds = [k for k in self.ds if (not than.get("pham_vi") or k["pham_vi"] == than["pham_vi"])
              and (not than.get("cho_hieu_luc") or k["hieu_luc_tu"] > bay)]
        return {"ky_uc": ds, "tong": len(ds),
                "pham_vi": [{"pham_vi": p, "so": n, "so_cho": cho[p]} for p, n in sorted(so.items())]}


class DaiCaGia:
    """CHỈ ĐỂ KIỂM TAY: mọi yêu cầu mang danh tính Đại ca giả; Origin cục bộ → `https://<máy B giả>`."""

    def __init__(self, app, cong: int):
        self.app, self.cuc_bo = app, {f"http://127.0.0.1:{cong}".encode(), f"http://localhost:{cong}".encode()}

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            h = [(k, f"https://{MAY_B}".encode() if k == b"origin" and v in self.cuc_bo else v)
                 for k, v in scope["headers"] if k != b"tailscale-user-login"]
            scope = {**scope, "headers": [*h, (b"tailscale-user-login", LOGIN.encode())]}
        await self.app(scope, receive, send)


def moi_truong() -> None:
    """`du-an/*.yaml` trong TRAM_REPO tạm; plist giả trong HOME giả; thay bộ đọc launchd/Keychain và bảng sẵn sàng."""
    (TAM / "repo" / "du-an").mkdir(parents=True)
    for ten, (dd, gn, lenh, rao) in DU_AN.items():
        raw = {"ten": ten, "duong_dan": str(Path.home() / dd), "gitnexus_repo": gn, "lenh_cho_phep": lenh,
               "hang_rao": {k: {"tu_khoa": v} for k, v in rao.items()},
               "moi_truong_kiem": {"file": str(TAM / "env"), "dich": ".env.testing"} if ten == "hr-codex" else None}
        (TAM / "repo" / "du-an" / f"{ten}.yaml").write_text(yaml.safe_dump(raw, allow_unicode=True), encoding="utf-8")
    (la := TAM / "home" / "Library" / "LaunchAgents").mkdir(parents=True)
    for nhan in DANG_CHAY:
        (la / f"{nhan}.plist").write_text("<plist/>\n", encoding="utf-8")
    he_thong._CHUNG = he_thong.DocHeThong(chay=chay_gia, home=TAM / "home", uid=501)
    ds = [bead(i, title=t, status=st, labels=["san-sang"], chan_boi=cb) for i, t, st, cb in SAN_SANG]
    san_sang.CHUNG = san_sang.BangSanSang(doc_bead=lambda: ds, which=lambda lenh: f"/gia/bin/{lenh}")


def main() -> None:
    cong = int(next((a for a in sys.argv[1:] if a != "--dai-ca"), 7798))
    dist = Path(__file__).resolve().parents[1] / "frontend" / "dist"
    moi_truong()
    kho = KhoPhieu(TAM / "sk.db")
    g3 = gieo(kho)
    kho.close()
    pt = tao_pt(TAM, {t: BdGia(ds) for t, ds in cac_bead(g3).items()}, thu_muc_tinh=dist)
    ch = replace(pt.cau_hinh, telegram=replace(pt.cau_hinh.telegram, chat_id="1", gio_yen_lang="23:00–07:00"))
    pt = replace(pt, mo_kho_phieu=lambda: KhoPhieu(TAM / "sk.db"), dong_ho=lambda: LUC, nho=NhoGia(ky_uc()),
                 usage=replace(pt.usage, gia=GIA), cau_hinh=ch,
                 bo_giao=SimpleNamespace(cac_du_an=lambda: [nap_du_an(t) for t in DU_AN], kho_git=lambda da: None))
    app = tao_app(pt, cong=cong)
    print(f"Dữ liệu giả ở {TAM} — mở http://127.0.0.1:{cong}/ (Ctrl+C để dừng)", flush=True)
    uvicorn.run(DaiCaGia(app, cong) if "--dai-ca" in sys.argv else app, host="127.0.0.1", port=cong,
                server_header=False, log_level="warning")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Build và chạy máy chủ thử**

```bash
cd frontend && npm ci --offline --ignore-scripts && npm run build && npm run kiem-dist && cd ..
uv run --offline python tests/chay_thu_giao_dien.py 7798 --dai-ca &   # ghi lại PID; dừng bằng kill <PID>
curl -sI -H 'Host: 127.0.0.1:7798' http://127.0.0.1:7798/ | grep -i content-security-policy
```

Kỳ vọng: header `content-security-policy: default-src 'none'; script-src 'self'; style-src 'self'; …; font-src 'self'; …`. Không dùng cổng 7801 (người điều phối), 7700 (tram-api thật), 7710 (memory).

- [ ] **Step 3: Kiểm CSP và tải tài nguyên**

Mở `http://127.0.0.1:7798/#/tong-quan` trong trình duyệt (Chrome). Lần lượt mở chín trang qua menu. Với mỗi trang:
1. Console: **không** có dòng "Refused to apply inline style", "Refused to load the font", "Refused to execute", "Content Security Policy" (lỗi CSP do Vue gộp khối tĩnh chỉ lộ ở đây — khảo sát §2.3 mục 1).
2. Network: font `be-vietnam-pro-*.woff2`, `jetbrains-mono-*.woff2` tải từ `/assets/` (cùng nguồn), không request nào ra ngoài.
3. `document.fonts.check('600 16px "Be Vietnam Pro"')` = `true`.

- [ ] **Hồi quy D39:** gieo sự kiện ký ức loại lạ có `mo_ta: ""`, `tom_tat` chứa JSON/sentinel giả; giao diện chỉ hiện “Sự kiện chưa có mô tả.”, không hiện JSON/sentinel. Kiểm giao diện danh sách Văn phòng bằng bàn phím và khi không có WebGL; ghi rõ nếu không mở được panel từng nhân vật như G8 để sửa trước nghiệm thu.
- [ ] **Hồi quy quyền G15 và breakpoint Tổng quan:** dữ liệu giả có bead cột 1/2; khi không danh tính hoặc trạng thái danh tính chưa tải, không kéo thẻ, hai nút chuyển cột và Chốt bị khoá, không phát POST. Khi có danh tính thì hoạt động; `bat_ghi: false` vẫn khoá. Mở hộp Vì sao rồi cho trạng thái danh tính chuyển sang không có quyền: hộp biến mất, không gửi POST kể cả submit đã được xếp hàng. Kiểm ngăn Chốt tương tự. Trên Tổng quan ở 375/900/1100 px, hai lưới xuống một cột, số Usage hai cột; ở 1440 px giữ bố cục mockup. Không cuộn ngang toàn trang (bảng có thể cuộn trong khối).

- [ ] **Step 4: So từng trang với ảnh mockup (1440 px)**

| Trang | Ảnh mockup | Kiểm |
|---|---|---|
| Tổng quan | `anh-tong-quan.png` | 5 ô việc chờ, số tổng = badge menu; sức khoẻ 5 dịch vụ; hàng chibi + chip; bảng dự án có "Mới xong"; usage 4 ô + thanh; sự kiện có câu mô tả (không JSON) |
| Văn phòng | `anh-van-phong.png`, `-1280`, `-1024`, `-ca-trang`, `-bam-nhan-vat` | xem Step 5 |
| Công việc + ngăn bên | `anh-cong-viec.png`, `anh-cong-viec-ngan-ben.png` | 3 cột có số thứ tự, thẻ có chip `cot:*`, chip PR, dòng khe "· đang hỏi Đại ca"; ngăn bên h4 viết hoa, nút Chốt / Dẫn ADR |
| Đội ngũ AI | `anh-doi-ngu.png` | bảng điểm + nhóm nút 7/30/92, "chưa có" / "—", phần ngoặc nhạt; thẻ khe chibi, thanh hạn mức, nút |
| Ký ức | `anh-ky-uc.png` | pill phạm vi, ô tìm lọc ngay, form ghi tay bên phải, sự kiện là câu dễ đọc |
| Usage | `anh-usage.png` | 6 ô số gọn (rê chuột ra số đầy đủ), biểu đồ cột, bảng khe có tỉ trọng, khối hạn mức |
| Phê duyệt | `anh-phe-duyet.png` | Hệ cần xem viền vàng; Bí có chip "Codex 1 hỏi · QC" + câu hỏi; review có chip PR, "PR #12 ↗", cảnh báo, nút theo trạng thái |
| Cài đặt | `anh-cai-dat.png` | bảng sẵn sàng có đèn + chip đếm; Keychain chỉ có/chưa; nút Sao chép đổi chữ "Đã chép" |
| Dự án | (trang.js `veDuAn`) | lưới thẻ, chip 1·2·3, "Lỗi gần nhất" |

Chạy lại không có `--dai-ca`: thẻ người dùng "Chỉ đọc · không có danh tính Đại ca", nút ghi khoá, Cài đặt và Ký ức hiện thẻ 403.

- [ ] **Step 5: Văn phòng 3D (bài học 2c T8)**

1. Cảnh hiện đủ 7 phòng, khít khung (không lệch về một góc) ở 1440, 1280, 1024 px; ở 375 px (DevTools thiết bị) cảnh vẫn khít, nhãn không chồng. Đếm chồng nhãn: `document.querySelector('.lop-phu')` — các nút nhãn không giao nhau (tính bằng `getBoundingClientRect`).
2. Màu pastel giống ảnh (NoToneMapping), nền gradient CSS thấy được (`alpha` + `clear-alpha 0`), có bóng đổ mềm (PCF + radius; three không in cảnh báo "PCFSoftShadowMap has been removed" trong Console).
3. Bấm nhân vật / phòng / nhãn → panel mở (công cụ tự động phải `hover` trước `click` — pointer-events dò theo lần di chuột trước); nút trong panel dẫn đúng trang.
4. Đèn Điều phối vàng ấm khi có nhịp, chữ "đang có phiên"; tủ máy chủ có tủ vàng theo `suc_khoe.muc`.
5. Bật "Giảm chuyển động": nhân vật đứng yên, màn đỏ không nhấp nháy; tải lại trang vẫn nhớ (localStorage). (`prefers-reduced-motion` không giả lập được trong khung Browser.)
6. Gói chính không có three: `npm run kiem-dist` xanh; Network khi mở Tổng quan không tải `VanPhong-*.js`.

- [ ] **Step 6: Bàn phím và 375 px**

Tab qua menu, ô tìm (⌘K/Ctrl+K focus; mũi tên + Enter chọn), thẻ bead (Enter mở ngăn bên), nhãn Văn phòng, bản danh sách phòng. Ở 375 px: sidebar thành khối trên, không cuộn ngang trang (trừ bảng có `.bang-cuon`).

- [ ] **Step 7: Dừng máy chủ, ghi "Ghi chú triển khai", commit**

```bash
kill <PID máy chủ thử>
git add tests/du_lieu_giao_dien.py tests/chay_thu_giao_dien.py docs/plans/2026-10-16-lat-2f-2-cac-trang.md
git commit -m "test(dashboard): 2f kiểm trên trình duyệt dưới CSP thật + ghi chú triển khai"
```

## Sơ đồ đợt chạy

Xem "Sơ đồ đợt chạy" ở cuối phần 1 (`docs/plans/2026-10-16-lat-2f-1-nen-va-api.md`). Tóm tắt phần 2: Task 9–17 cùng **đợt 3** (song song, 9 worktree, sau Task 1 và 2), Task 18 **đợt 4** sau mọi task. Sau đợt 3: pytest **N₀ + 30**, node **M₀ + 57**, build + kiem-dist xanh (chạy thử bản D41: 2061 / 95).

## Tự review (đối chiếu yêu cầu với task)

| Yêu cầu | Task |
|---|---|
| Khung chung: sidebar, thanh trên, Estop + băng estop, ô tìm ⌘K phía trình duyệt, thẻ "Chỉ đọc" | 1 |
| Tổng quan (D17) | 8 (API), 13 (trang) |
| Dự án (lưới thẻ, chip "chỉ quét thử") | 15 |
| Văn phòng 3D (TresCanvas `NoToneMapping`, `clear-alpha 0`, PCF + radius, `:look-at`, nhãn phủ chống chồng, panel, danh sách, đèn Điều phối, tủ máy theo mức) | 7 (T2, T6), 12, 18 |
| Công việc + ngăn bên (chip, PR trạm, dòng khe, giữ phần D36) | 9 |
| Đội ngũ AI (bảng điểm 2d — hàng 0 phiếu do API 2d trả, D41; thẻ khe chibi + hạn mức) | 7 (T1), 10 |
| Ký ức (mockup D39, `/nho` + `/ky-uc`, sự kiện có mô tả) | 1 (tuyến), 5 (`mo_ta`), 16 |
| Usage & chi phí (D39: hạn mức, số gọn + tooltip) | 17 |
| Phê duyệt (PR trạm, escalation có khe/bước/câu hỏi) | 7 (T4), 11 |
| Cài đặt (chỉ đọc, chỉ Đại ca, bảng sẵn sàng, Keychain có/chưa) | 4, 6, 14 |
| API mới `/api/cai-dat`, `/api/san-sang`, `/api/su-kien/gan-day`, `/api/tong-quan`, mô tả sự kiện ký ức (D39), T1–T7 | 4–8 |
| launchd/Keychain chỉ có/chưa, không trả giá trị/đầu ra thô; không gọi `tram tho kiem`/`tram giao kiem` | 4, 6 (test bảo mật) |
| Luật cấm inline style trong `kiem-an-toan`, `kiem-dist` | 3 |
| Bỏ chế độ tối (D38) | 1 |
| Kiểm trình duyệt dưới CSP thật, so ảnh mockup (như 2c T8) | 18 |
| Font tự host (D35) | 1 |
| Chip "chỉ quét thử" theo `bat_ghi` (D37) | 1 (`duAnChiQuetThu`), 9, 11, 12, 13, 14, 15 |

Đã rà: không còn chỗ "tương tự Task N" hay mã giữ chỗ; mọi file mã đều có nguyên văn (file mới: toàn văn; file sửa: khối diff áp được bằng `git apply` lên `main` sau các task trước — đã kiểm bằng chạy thử); tên hàm/trường giữa hai file khớp mục "Hợp đồng (lát 2f)".

## Cần sửa spec sau (không sửa spec đã duyệt trong plan này)

- Spec 2 §7: thêm `GET /api/tong-quan`, `GET /api/su-kien/gan-day`, `GET /api/cai-dat`, `GET /api/san-sang`; trường `mo_ta` của `/api/nho/su-kien`; T1/T2/T4/T6.
- Spec 2 §5: trang mở đầu là Tổng quan (D17); trang Cài đặt (D19); bỏ chế độ tối (D38); đường `/ky-uc`.
- Spec 1b §9.4: `nho.bo_bi_mat` có mẫu mô tả (theo 1b-4 G22, đã dùng ở Task 5).

## Ghi chú triển khai (16/10/2026)

**Code:** Task 1–17 ghép vào `main` theo đúng ba đợt; mỗi nhánh QC "mọi dòng thêm có nguyên văn trong plan" đạt 100%. Sau đợt 3: `uv run pytest -q` = **2242** (N₀ 2212 + 30), `npm run kiem` = **95** (M₀ 38 + 57), `npm run build` và `npm run kiem-dist` xanh. Mốc N₀ đo sau khi đã ghép 2d, 2e, 1b-4 (T0–T4), 1a-2 (T1–T3); 1a-2 T4/T5 và 3c chưa ghép, nên chip "chỉ quét thử" chỉ kiểm bằng test node.

**Chỗ lệch khi code:**
- Task 9: khối diff `CongViec.vue` thiếu một dòng ngữ cảnh ở hunk thứ 3 (sau bản sửa Q07 của Codex), `git apply` từ chối. Đã thêm đúng dòng ngữ cảnh `   const { the, cot } = keoCho.value` rồi áp bằng `--recount`; không đổi dòng thêm hay xoá nào.
- Task 6: mục File Structure ghi sửa `tuyen_chu.py`, phần riêng của Task 6 ghi sửa `app.py` (G28 sau N05). Làm theo phần riêng của task.

**Task 18 — kiểm trên trình duyệt dưới CSP thật** (máy chủ `tests/chay_thu_giao_dien.py` cổng 7798, khung Browser của app Claude, 16/10):
- Header CSP đúng: `default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; font-src 'self'; …`.
- Mở đủ chín trang ở 1440 px: Console **không có dòng nào** (không lỗi CSP, không cảnh báo three). `document.fonts.check` đúng cho Be Vietnam Pro và JetBrains Mono; 18 file woff2 tải từ cùng nguồn; không request nào ra ngoài; không cuộn ngang.
- So với ảnh mockup: chín trang khớp bố cục và khối chính (Tổng quan 5 ô việc chờ + sức khoẻ + đội ngũ + dự án + usage; Văn phòng; Công việc ba cột có chip PR và dòng khe; Đội ngũ AI có hàng 0 phiếu "chưa có"/"—"; Ký ức; Usage; Phê duyệt có cảnh báo PR không xác minh; Cài đặt có bảng sẵn sàng; Dự án lưới thẻ).
- Văn phòng: 17 nhãn phủ, **0 cặp chồng** ở 1440 và 375 px; cảnh khít khung ở cả hai cỡ; bấm nhân vật "Claude 1" (hover rồi click) mở panel có nút "Mở bead hr-1"; đèn Điều phối "đang có phiên".
- 375 px: sidebar thành khối trên, không cuộn ngang ở Tổng quan và Văn phòng.
- Không có danh tính Đại ca (máy chủ chạy không `--dai-ca`, tải lại trang): thẻ "Chỉ đọc · không có danh tính Đại ca", không thẻ nào kéo được, Estop khoá, Cài đặt hiện thẻ 403.

**Còn lại / theo dõi:**
- Khi danh tính đổi giữa phiên mà không tải lại trang, giao diện giữ quyền cũ cho tới khi `taiTrangThai()` chạy lại (chỉ lúc mở trang và khi có SSE `phe_duyet_doi`). Máy chủ vẫn từ chối mọi ghi (403), nên không vượt quyền; chỉ là nút còn bật. Ghi bead để tải lại trạng thái khi SSE nối lại hoặc khi tab được focus.
- 375 px Tổng quan: tiêu đề "Việc chờ Đại ca" bẻ thành bốn dòng cạnh số và nút "Mở Phê duyệt"; nên cho đầu khối xuống hàng ở breakpoint nhỏ.
- Chưa kiểm: bàn phím đầy đủ (Tab qua nhãn Văn phòng, ⌘K), chế độ không WebGL, `prefers-reduced-motion` (khung Browser không giả lập được). Làm ở đợt chạy thật cùng 2a T26.
