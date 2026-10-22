# Lát V1 — Vá sau code (bs-urj.17, bs-78r.8, bs-78r.5) — Implementation Plan

> **Review Codex đợt 6:** Task 1 giữ; Task 2 bổ sung khóa quyền ngay khi bắt đầu tải, bỏ phản hồi cũ và giữ chỉ đọc khi lỗi (Q05). Các số ở mục chạy thử cuối file là kết quả tác giả của bản trước review. Bản sửa tài liệu này chưa chạy test/build/browser. Tổng dự kiến mới: N₀+1 pytest, M₀+6 node (2243 / 101 nếu nền không đổi). Task 4 chỉ đóng bead sau kiểm lại trên mã đã ghép. Các việc chặn S6 ngoài lát được kê ở phụ lục cuối, không được coi V1 là đã xử lý chúng.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Vá ba việc còn treo sau lát 2e/2f: `dat-ma-dai-ca` chặn mã trùng mã điều phối; giao diện tải lại quyền khi SSE nối lại hoặc tab quay lại; đầu khối "Việc chờ Đại ca" xuống hàng ở màn nhỏ; đóng bead cỡ chữ văn phòng 3D.

**Architecture:** Ba thay đổi nhỏ, độc lập, mỗi cái một task có test riêng. Python: thêm một bước kiểm trong `ghi_bam` của `tram/nho/ma_dai_ca.py`, không import ngược tầng `tram/chu`. Frontend: thêm `theoDoiTab()` và nhánh "nối lại" trong `moLuong()` ở `frontend/src/kho.js`, gắn ở `KhungChinh.vue`; khóa quyền trong lúc tải/lỗi và bỏ phản hồi cũ; thêm một luật CSS trong breakpoint 900 px của mockup. Bead `bs-78r.5` đóng, không có mã.

**Tech Stack:** Python 3 + pytest (`uv`), PyYAML; Vue 3.5.43, Vite 8.3.4, `node --test`.

**Spec / nguồn:** bead `bs-urj.17`, `bs-78r.8`, `bs-78r.5`; rủi ro (h) ở `docs/plans/2026-10-15-lat-2e-den-dieu-phoi.md`; D24 ở `docs/quyet-dinh/2026-10-15-chot-dot-4.md`; mục "Ghi chú triển khai" cuối `docs/plans/2026-10-16-lat-2f-2-cac-trang.md`; mockup `docs/mockup/2026-10-15-giao-dien/style.css`.

## Global Constraints

- Mọi dòng mã thêm phải có nguyên văn trong plan này (luật QC). Khối diff dưới đây áp được bằng `git apply`.
- Mỗi file ≤ ~120 dòng; mỗi dòng **thêm** ≤ 120 ký tự. (`frontend/src/kho.js` dòng 6 dài 127 ký tự từ trước, không đụng.)
- Cổng an toàn frontend giữ nguyên: không `style="…"` tĩnh, không `v-html`/`innerHTML`, không URL ngoài, CSP `'self'`. Không thêm gói.
- UI: **không thêm thành phần mới**, chỉ CSS; breakpoint lấy từ mockup đã duyệt (mockup chỉ có 1100 px và 900 px).
- Không sửa chiều cũ của D24: `tram chu dat-ma-dieu-phoi` vẫn từ chối mã trùng mã Đại ca.
- Mã bí mật không vào argv, log, màn hình (giữ nguyên luật của 1b-2 và 2e).

## Câu hỏi / giả định

| # | Chỗ mơ hồ | Chọn | Vì sao | Loại |
|---|---|---|---|---|
| G1 | Mốc test | N₀ = **2242** pytest, M₀ = **95** node (đo trên `main` `f5b1fdb`) | Đo lại khi thực thi nếu `main` đã đổi | giả định |
| G2 | `tram/nho` đọc khoá băm điều phối thế nào | Hằng `KHOA_DIEU_PHOI = "dieu_phoi_ma_sha256"` trong `ma_dai_ca.py`; test giữ khớp `ma_dieu_phoi.KHOA` | `ma_dieu_phoi` đã import `ma_dai_ca` ở đầu module; import ngược gây vòng và kéo tầng `chu` vào memory service | quyết định kỹ thuật |
| G3 | `cau-hinh.yaml` hỏng khi kiểm trùng | Coi là không trùng; bước kiểm cuối có sẵn của `ghi_bam` từ chối, không ghi | Giữ một đường báo lỗi "không đổi gì" như cũ | giả định |
| G4 | Khi nào tải lại trạng thái | SSE `onopen` từ lần thứ hai (nối lại); `visibilitychange` khi tab không `hidden`; `window` `focus` | Đúng ghi chú 2f. Focus và visibilitychange có thể cùng bắn → kiểm lượt tải để phản hồi cũ không ghi đè quyền mới | quyết định kỹ thuật |
| G5 | Breakpoint cho đầu khối Việc chờ | `@media (max-width: 900px) { .tq-dau { flex-wrap: wrap; } }` | 900 px là breakpoint nhỏ nhất của mockup; rộng hơn thì mọi phần tử vừa một hàng nên không đổi | bám mockup |
| G6 | `bs-78r.5` còn không | **Không còn → đóng bead** (xem Task 4) | Chữ 3D đã thay bằng nhãn HTML, cỡ chữ đúng công thức mockup; đo ở khung 975×536 | kết luận kiểm |

## File Structure

| File | Task | Việc |
|---|---|---|
| `tram/nho/ma_dai_ca.py` (sửa, 96 → 103 dòng) | 1 | `KHOA_DIEU_PHOI`; `_doc(van_ban, khoa=KHOA)`; `ghi_bam` từ chối băm trùng băm điều phối |
| `tests/test_nho_ma_dai_ca.py` (sửa, 70 → 88) | 1 | 1 test mới |
| `frontend/src/kho.js` (sửa, 43 → 68) | 2 | `moLuong` tải lại khi nối lại; `theoDoiTab(tai, d, w)` mới |
| `frontend/src/KhungChinh.vue` (sửa, 2 dòng) | 2 | Gọi `theoDoiTab()` trong `onMounted` |
| `frontend/tests/kho.test.mjs` (mới, 5 test) | 2 | 5 test |
| `frontend/src/kieu/tong-quan.css` (sửa, 50 → 53) | 3 | Breakpoint 900 px cho `.tq-dau` |
| `frontend/tests/tong_quan.test.mjs` (sửa, 86 → 95) | 3 | 1 test |

## Sơ đồ đợt

| Đợt | Task | Song song? | pytest sau đợt | node sau đợt |
|---|---|---|---|---|
| 1 | Task 1 (Python), Task 2 (kho.js), Task 3 (CSS) | Có — ba task không chung file | N₀ + 1 = **2243** | M₀ + 6 = **101** |
| 2 | Task 4 (đóng `bs-78r.5`, không mã) | — | 2243 | 101 |

Task 1 +1 pytest. Task 2 +5 node. Task 3 +1 node. Ghép theo thứ tự 1 → 2 → 3, không xung đột.

## Chuẩn bị

```bash
git worktree add .worktrees/v1-t$N -b va/v1-t$N main
cd .worktrees/v1-t$N && UV_OFFLINE=1 uv run pytest -q      # kỳ vọng 2242 passed
cd frontend && npm ci --offline --ignore-scripts && npm run kiem   # kỳ vọng tests 95, pass 95
```

---

### Task 1: `dat-ma-dai-ca` từ chối mã trùng mã điều phối (bs-urj.17)

**Đợt:** 1 · **Test mới:** 1 pytest

**Files:**
- Modify: `tram/nho/ma_dai_ca.py:16-17` (hằng), `:30-33` (`_doc`), `:48-50` (`ghi_bam`)
- Test: `tests/test_nho_ma_dai_ca.py` (thêm cuối file)

**Interfaces:**
- Consumes: `tram.chu.ma_dieu_phoi.KHOA`, `ghi_bam`, `doc_bam` (chỉ trong test).
- Produces: `tram.nho.ma_dai_ca.KHOA_DIEU_PHOI: str`; `ghi_bam(gia_tri, duong_dan=None)` ném `ValueError("mã Đại ca phải KHÁC mã điều phối (D24) — không đổi gì")` khi `gia_tri` bằng băm ở khoá `dieu_phoi_ma_sha256`. `doc_bam()` không đổi chữ ký.

- [ ] **Step 1: Viết test hỏng** — thêm cuối `tests/test_nho_ma_dai_ca.py`:

```python


def test_tu_choi_ma_trung_ma_dieu_phoi(tram_home_tam, capsys):      # bs-urj.17: chiều ngược của D24 / G23
    from tram.chu import ma_dieu_phoi
    from tram.nho.ma_dai_ca import KHOA_DIEU_PHOI
    assert KHOA_DIEU_PHOI == ma_dieu_phoi.KHOA                        # tầng nho không import tầng chu, test giữ khớp
    ma_dieu_phoi.ghi_bam(BAM)
    with pytest.raises(ValueError, match="KHÁC mã điều phối"):
        ghi_bam(BAM)
    nhap = iter([MA, MA])
    assert dat_ma_dai_ca(NS(dong_y=True), doc_an=lambda _: next(nhap), hoi=lambda _: "") == 1
    out = capsys.readouterr()
    assert doc_bam() is None and MA not in out.out + out.err and "KHÁC mã điều phối" in out.err
    assert ma_dieu_phoi.doc_bam() == BAM                               # băm điều phối giữ nguyên
    ghi_bam("0" * 64)                                                  # mã khác thì vẫn ghi được
    assert doc_bam() == "0" * 64 and ma_dieu_phoi.doc_bam() == BAM
    with pytest.raises(ValueError, match="KHÁC mã Đại ca"):           # chiều cũ không yếu đi
        ma_dieu_phoi.ghi_bam("0" * 64)
```

- [ ] **Step 2: Chạy, thấy hỏng**

Run: `UV_OFFLINE=1 uv run pytest -q tests/test_nho_ma_dai_ca.py`
Expected: `1 failed, 9 passed` — `ImportError: cannot import name 'KHOA_DIEU_PHOI'`.

- [ ] **Step 3: Sửa `tram/nho/ma_dai_ca.py`** (áp nguyên khối):

```diff
--- a/tram/nho/ma_dai_ca.py
+++ b/tram/nho/ma_dai_ca.py
@@ -14,6 +14,7 @@ import yaml
 from tram.duong_dan import tram_home
 
 KHOA = "ma_dai_ca_sha256"
+KHOA_DIEU_PHOI = "dieu_phoi_ma_sha256"          # = tram.chu.ma_dieu_phoi.KHOA (D24); nho không import ngược tầng chu
 MA_RE = re.compile(r"[A-Za-z0-9._~+/=-]{32,256}")       # an toàn trong header HTTP, đủ dài để không đoán được
 BAM_RE = re.compile(r"[0-9a-f]{64}")
 DONG_RE = re.compile(rf"^{KHOA}:.*$", re.M)
@@ -27,9 +28,9 @@ def bam(ma: str) -> str:
     return hashlib.sha256(ma.encode()).hexdigest()
 
 
-def _doc(van_ban: str) -> str | None:
+def _doc(van_ban: str, khoa: str = KHOA) -> str | None:
     raw = yaml.safe_load(van_ban) or {}
-    v = raw.get(KHOA) if isinstance(raw, dict) else None
+    v = raw.get(khoa) if isinstance(raw, dict) else None
     return v if isinstance(v, str) and BAM_RE.fullmatch(v) else None
 
 
@@ -47,6 +48,12 @@ def ghi_bam(gia_tri: str, duong_dan: Path | None = None) -> None:
         raise ValueError("bản băm phải là 64 ký tự hex thường")
     p = tep_cau_hinh(duong_dan)
     cu = p.read_text(encoding="utf-8") if p.exists() else ""
+    try:
+        trung = _doc(cu, KHOA_DIEU_PHOI) == gia_tri
+    except yaml.YAMLError:
+        trung = False                                   # file hỏng: bước kiểm dưới từ chối, không đổi gì
+    if trung:
+        raise ValueError("mã Đại ca phải KHÁC mã điều phối (D24) — không đổi gì")
     dong = f'{KHOA}: "{gia_tri}"'
     if DONG_RE.search(cu):
         moi = DONG_RE.sub(dong, cu)
```

`dat_ma_dai_ca` đã bắt `ValueError` và in `Lỗi: {e}` ra stderr, trả 1 — không cần sửa.

- [ ] **Step 4: Chạy, thấy qua**

Run: `UV_OFFLINE=1 uv run pytest -q tests/test_nho_ma_dai_ca.py tests/test_ma_dieu_phoi.py`
Expected: `15 passed`. Rồi cả bộ: `UV_OFFLINE=1 uv run pytest -q` → `2243 passed`.

- [ ] **Step 5: Commit**

```bash
git add tram/nho/ma_dai_ca.py tests/test_nho_ma_dai_ca.py
git commit -m "fix(nho): dat-ma-dai-ca từ chối mã trùng mã điều phối (bs-urj.17, D24)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: Tải lại quyền khi SSE nối lại và khi tab quay lại (bs-78r.8 a)

**Đợt:** 1 · **Test mới:** 5 node

**Files:**
- Modify: `frontend/src/kho.js:40-43` (`moLuong`), thêm `theoDoiTab` cuối file
- Modify: `frontend/src/KhungChinh.vue:5,16`
- Create: `frontend/tests/kho.test.mjs`

**Interfaces:**
- Consumes: `taiTrangThai()` (có sẵn, `GET /api/chu/trang-thai` → `kho.trangThai`).
- Produces: `theoDoiTab(tai = taiTrangThai, d = globalThis.document, w = globalThis.window) -> () => void` (hàm gỡ). `moLuong()` giữ chữ ký, trả `EventSource`.

- [ ] **Step 1: Viết test hỏng** — tạo `frontend/tests/kho.test.mjs`:

```js
// bs-78r.8 (a): tải lại /api/chu/trang-thai khi SSE nối lại và khi tab hiện lại / được focus, để nút ghi tắt ngay
// khi danh tính đổi giữa phiên. Máy chủ vẫn là nơi chặn ghi (403); đây chỉ là giao diện theo kịp.
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { test } from 'node:test'
import { kho, moLuong, taiTrangThai, theoDoiTab } from '../src/kho.js'

class NguonGia {
  constructor(url) { this.url = url; this.nghe = {} }
  addEventListener(ten, f) { this.nghe[ten] = f }
}
const xong = () => new Promise((r) => setImmediate(r))

test('SSE: lần mở đầu không tải lại; mỗi lần nối lại sau đó tải lại trạng thái', async () => {
  const goi = []
  globalThis.fetch = async (url) => { goi.push(url); return new Response(JSON.stringify({ la_dai_ca: false })) }
  globalThis.EventSource = NguonGia
  const es = moLuong()
  assert.equal(es.url, '/api/luong')
  es.onopen()
  await xong()
  assert.deepEqual(goi, [])
  es.onerror()
  assert.equal(kho.matKetNoi, true)
  es.onopen()
  await xong()
  assert.deepEqual(goi, ['/api/chu/trang-thai'])
  assert.equal(kho.matKetNoi, false)
  assert.deepEqual(kho.trangThai, { la_dai_ca: false })
  es.onopen()
  await xong()
  assert.equal(goi.length, 2)
})

test('tab hiện lại hoặc được focus thì tải lại; tab ẩn thì không; hàm trả về gỡ được', () => {
  let n = 0
  const d = new EventTarget()
  const w = new EventTarget()
  d.visibilityState = 'visible'
  const go = theoDoiTab(() => { n += 1 }, d, w)
  d.dispatchEvent(new Event('visibilitychange'))
  w.dispatchEvent(new Event('focus'))
  assert.equal(n, 2)
  d.visibilityState = 'hidden'
  d.dispatchEvent(new Event('visibilitychange'))
  assert.equal(n, 2)
  go()
  d.visibilityState = 'visible'
  d.dispatchEvent(new Event('visibilitychange'))
  w.dispatchEvent(new Event('focus'))
  assert.equal(n, 2)
})

test('KhungChinh gắn theoDoiTab() lúc mở trang', () => {
  const vue = readFileSync(new URL('../src/KhungChinh.vue', import.meta.url), 'utf8')
  assert.match(vue, /onMounted\(\(\) => \{[^}]*theoDoiTab\(\)/)
})


// Q05 review đợt 6: lỗi tải quyền và phản hồi về đảo thứ tự không được mở lại nút ghi.
test('đang tải và tải lỗi đều khóa quyền cũ', async (t) => {
  const cu = globalThis.fetch
  t.after(() => { globalThis.fetch = cu })
  let huy
  globalThis.fetch = () => new Promise((resolve, reject) => { huy = reject })
  kho.trangThai = { la_dai_ca: true }
  const viec = taiTrangThai()
  assert.equal(kho.trangThai, null)
  huy(new Error('mất kết nối'))
  await viec
  assert.equal(kho.trangThai, null)
})

test('phản hồi owner cũ về sau không ghi đè danh tính mới', async (t) => {
  const cu = globalThis.fetch
  t.after(() => { globalThis.fetch = cu })
  const tra = []
  globalThis.fetch = () => new Promise((resolve) => { tra.push(resolve) })
  const dau = taiTrangThai()
  const sau = taiTrangThai()
  tra[1](new Response(JSON.stringify({ la_dai_ca: false })))
  await sau
  tra[0](new Response(JSON.stringify({ la_dai_ca: true })))
  await dau
  assert.deepEqual(kho.trangThai, { la_dai_ca: false })
})
```

- [ ] **Step 2: Chạy, thấy hỏng**

Run (trong `frontend/`): `node --test tests/kho.test.mjs`
Expected: `fail 1` — `SyntaxError: The requested module '../src/kho.js' does not provide an export named 'theoDoiTab'`.

- [ ] **Step 3: Sửa `frontend/src/kho.js` và `frontend/src/KhungChinh.vue`** (áp nguyên khối):

```diff
--- a/frontend/src/kho.js
+++ b/frontend/src/kho.js
@@ -6,10 +6,18 @@
 export const kho = reactive({ trangThai: null, soPheDuyet: 0, phienBan: 0, phienBanNho: 0, phienBanDoiNgu: 0, suKienCuoi: null,
   matKetNoi: false, loi: '' })
 
+let lanTaiTrangThai = 0
 export async function taiTrangThai() {
+  const lan = ++lanTaiTrangThai
+  kho.trangThai = null                         // đang xác minh lại: khóa thao tác ghi
   try {
-    kho.trangThai = await doc('/api/chu/trang-thai')
+    const trangThai = await doc('/api/chu/trang-thai')
+    if (lan !== lanTaiTrangThai) return         // phản hồi cũ không khôi phục quyền
+    kho.trangThai = trangThai
+    kho.loi = ''
   } catch (e) {
+    if (lan !== lanTaiTrangThai) return
+    kho.trangThai = null
     kho.loi = e.message
   }
 }
```

```diff
--- a/frontend/src/kho.js
+++ b/frontend/src/kho.js
@@ -37,7 +37,23 @@ export function moLuong() {
       kho.suKienCuoi = null
     }
   })
+  let daMo = false
   es.onerror = () => { kho.matKetNoi = true }
-  es.onopen = () => { kho.matKetNoi = false }
+  es.onopen = () => {
+    if (daMo) taiTrangThai()                  // bs-78r.8: nối lại sau khi rớt → quyền có thể đã đổi
+    daMo = true
+    kho.matKetNoi = false
+  }
   return es
 }
+
+// bs-78r.8: tab ở nền lâu thì danh tính có thể đã đổi → tải lại khi tab hiện lại hoặc được focus. Trả hàm gỡ.
+export function theoDoiTab(tai = taiTrangThai, d = globalThis.document, w = globalThis.window) {
+  const lai = () => { if (d.visibilityState !== 'hidden') tai() }
+  d.addEventListener('visibilitychange', lai)
+  w.addEventListener('focus', lai)
+  return () => {
+    d.removeEventListener('visibilitychange', lai)
+    w.removeEventListener('focus', lai)
+  }
+}
--- a/frontend/src/KhungChinh.vue
+++ b/frontend/src/KhungChinh.vue
@@ -2,7 +2,7 @@
 import { computed, onMounted, watch } from 'vue'
 import { useRoute } from 'vue-router'
 import { dungEstop } from './estop.js'
-import { kho, moLuong, taiSoPheDuyet, taiTrangThai } from './kho.js'
+import { kho, moLuong, taiSoPheDuyet, taiTrangThai, theoDoiTab } from './kho.js'
 import { tieuDeTab } from './luat.js'
 import { tenTrang } from './menu.js'
 import BangEstop from './thanh/BangEstop.vue'
@@ -13,7 +13,7 @@ import ThanhTren from './thanh/ThanhTren.vue'
 const route = useRoute()
 const estop = dungEstop()
 const khoa = computed(() => !(kho.trangThai && kho.trangThai.la_dai_ca) || estop.dangGui.value)
-onMounted(() => { taiTrangThai(); taiSoPheDuyet(); moLuong() })
+onMounted(() => { taiTrangThai(); taiSoPheDuyet(); moLuong(); theoDoiTab() })
 watch([() => route.path, () => kho.soPheDuyet],
   () => { document.title = tieuDeTab(kho.soPheDuyet, tenTrang(route.path)) }, { immediate: true })
 </script>
```

- [ ] **Step 4: Chạy, thấy qua**

Run: `node --test tests/kho.test.mjs` → dự kiến `pass 5`. Rồi `npm run kiem` → dự kiến `tests 100, pass 100` + dòng `kiem-an-toan: 135 file, …`; `npm run build` xanh; `npm run kiem-dist` xanh.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/kho.js frontend/src/KhungChinh.vue frontend/tests/kho.test.mjs
git commit -m "fix(dashboard): tải lại quyền khi SSE nối lại và khi tab quay lại (bs-78r.8 a)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: Đầu khối "Việc chờ Đại ca" xuống hàng ở màn nhỏ (bs-78r.8 b)

**Đợt:** 1 · **Test mới:** 1 node · **Mockup bám:** `style.css` dòng 466 (`@media (max-width: 900px)`), dòng 303 (`.tq-dau`); ảnh `anh-tong-quan.png`.

**Files:**
- Modify: `frontend/src/kieu/tong-quan.css` (thêm cuối file)
- Test: `frontend/tests/tong_quan.test.mjs` (thêm import + 1 test cuối file)

**Interfaces:** không đổi template `KhoiViecCho.vue`; chỉ CSS.

- [ ] **Step 1: Viết test hỏng** — trong `frontend/tests/tong_quan.test.mjs`:

```diff
--- a/frontend/tests/tong_quan.test.mjs
+++ b/frontend/tests/tong_quan.test.mjs
@@ -1,4 +1,5 @@
 import assert from 'node:assert/strict'
+import { readFileSync } from 'node:fs'
 import { test } from 'node:test'
 import { chipDichVu, demTrangThai, dongTram, oViecCho, usageHomNay } from '../src/luat_tong_quan.js'
 
@@ -84,3 +85,11 @@ test('usage hôm nay: tách khe / chấm cột, thanh theo tỉ lệ giảm dầ
   assert.deepEqual([trong.vao, trong.usdKhe, trong.usdApi, trong.luot, trong.cot],
     ['0', 'chưa có giá', 'chưa có giá', 0, []])
 })
+
+test('bs-78r.8 (b): đầu khối Việc chờ xuống hàng ở breakpoint 900 px của mockup, không đổi bản rộng', () => {
+  const css = readFileSync(new URL('../src/kieu/tong-quan.css', import.meta.url), 'utf8')
+  const i = css.indexOf('@media (max-width: 900px)')
+  assert.ok(i > 0)
+  assert.match(css.slice(i), /\.tq-dau \{ flex-wrap: wrap; \}/)
+  assert.match(css.slice(0, i), /\.tq-dau \{ display: flex; align-items: center; gap: 10px; margin-bottom: 14px; \}/)
+})
```

- [ ] **Step 2: Chạy, thấy hỏng** — `node --test tests/tong_quan.test.mjs` → `fail 1` (`assert.ok(i > 0)`).

- [ ] **Step 3: Thêm cuối `frontend/src/kieu/tong-quan.css`**:

```css
@media (max-width: 900px) {          /* bs-78r.8: breakpoint nhỏ nhất của mockup; 375 px đầu khối xuống hàng */
  .tq-dau { flex-wrap: wrap; }
}
```

- [ ] **Step 4: Chạy, thấy qua** — `node --test tests/tong_quan.test.mjs` qua; `npm run kiem` → `tests 96` nếu chạy riêng trên `main` (101 khi đã ghép Task 2); `npm run build`, `npm run kiem-dist` xanh.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/kieu/tong-quan.css frontend/tests/tong_quan.test.mjs
git commit -m "fix(dashboard): Tổng quan 375 px đầu khối Việc chờ xuống hàng (bs-78r.8 b)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4: Đóng `bs-78r.5` (không có mã)

Bead cũ: "biển chữ/bong bóng văn phòng 3D quá nhỏ ở khung ~975x536" (plan 2c dòng 1769, thời còn `TheChu3D.vue` vẽ chữ bằng texture canvas). Kiểm lại trên `main` `f5b1fdb`:

- `frontend/src/van_phong/` không còn sprite chữ (không có `TheChu3D.vue`, `CanvasTexture`, `Sprite`). Biển phòng, tên, bong bóng, huy hiệu là `<button>` HTML trong `LopNhan.vue`.
- Cỡ chữ gốc của lớp nhãn: `coChu(W) = 16 * max(0.7, min(1.05, W / 1100))` (`khung_nhin.js`) — **đúng công thức `boTriLai()` của mockup đã duyệt** (`van-phong.js` dòng 362); các cỡ `em` trong `kieu/van-phong.css` chép từ mockup `style.css` dòng 175–196.
- Đo trên trình duyệt (máy chủ dữ liệu giả `tests/chay_thu_giao_dien.py`, khung cảnh đúng **975×536**): cỡ gốc 14,15 px; biển phòng 16,8 px; tên nhân vật 15,0 px; bong bóng 12,4 px; nhãn phụ dưới tên 9,3 px (`.62em` như mockup). 17 nhãn, **0 cặp chồng**, 0 nhãn ra ngoài khung.

Kết luận: lỗi không còn. Không lập task sửa.

- [ ] **Step 1:** Trong repo chính: `bd close bs-78r.5 --reason "2f thay chữ 3D bằng nhãn HTML; cỡ chữ theo coChu() của mockup; đo 975x536: biển 16.8px, tên 15px, bong bóng 12.4px, 0 chồng (plan V1 Task 4)"`.
- [ ] **Step 2:** Đóng `bs-urj.17` và `bs-78r.8` sau khi Task 1–3 ghép vào `main` và chạy đủ bộ test.

---

## Chạy thử khi viết plan (16/10, bản sao `main` `f5b1fdb`, thư mục scratchpad riêng)

- Trước: `UV_OFFLINE=1 uv run pytest -q` → **2242 passed**; `npm ci --offline --ignore-scripts` + `npm run kiem` → **95/95**.
- Áp Task 1–3 như trên (từng bước hỏng → qua đúng như "Expected"):
  - pytest → **2243 passed** (158 s).
  - `npm run kiem` → **tests 99, pass 99**, `kiem-an-toan: 135 file, …`.
  - `npm run build` xanh (chỉ cảnh báo chunk > 500 kB có sẵn từ three).
  - `npm run kiem-dist` → `2 file JS, 2 file CSS, không thấy eval/inline/style tĩnh/font ngoài`.
- Trình duyệt (`tests/chay_thu_giao_dien.py 7811 --dai-ca`, khung Browser):
  - 375 px Tổng quan: tiêu đề "Việc chờ Đại ca" **một dòng** (cao 24 px) cạnh số 4; dòng phụ hàng 2; nút "Mở Phê duyệt" hàng 3 sát phải; không cuộn ngang.
  - 1240 px: bốn phần tử đầu khối vẫn một hàng như mockup.
  - Phát `focus` và `visibilitychange`: hai GET `/api/chu/trang-thai` mới.
  - Văn phòng 975×536: số đo ở Task 4.

## Tự review

- Phủ bead: `bs-urj.17` → Task 1; `bs-78r.8` (a) → Task 2, (b) → Task 3; `bs-78r.5` → Task 4.
- Không placeholder; tên `KHOA_DIEU_PHOI`, `theoDoiTab`, `taiTrangThai` khớp giữa task và test.
- Chiều cũ D24 có assert riêng trong test Task 1 (`KHÁC mã Đại ca`); `tests/test_ma_dieu_phoi.py` vẫn qua nguyên.
- Rủi ro (h) của plan 2e hết hiệu lực sau Task 1; sửa chữ ở plan 2e và HUONG-DAN để đợt đồng bộ tài liệu.


## Review đợt 6 — phạm vi và cổng bổ sung

- Q05 được sửa đầy đủ trong Task 2 (hai test mới, chỉ ở văn bản). Sơ đồ mới: Task 1 (+1 pytest), Task 2 (+5 node), Task 3 (+1 node), rồi kiểm tích hợp và Task 4. Không lấy các số chạy thử 2243/99 cũ làm chứng cứ bản 101.
- Chiều token Task 1 đúng cho setter chạy tuần tự; `os.replace` không phải khóa giao dịch giữa hai setter hoặc mọi trình sửa YAML. Không tuyên bố giải quyết cập nhật cấu hình đồng thời. Vận hành một người đặt mã một lần; nếu cần nhiều writer phải thiết kế khóa chung cho tất cả writer trước.
- `bs-78r.10` (Q02): chưa được vá bởi V1. Cần task riêng cho toàn chuỗi `VongKhe.nhip → BoCodex → doc_han_muc_ranh → hoi_app_server`: principal lấy qua `nc.principal(k, None, ...)`, bọc lệnh, môi trường khe, callback kill dưới principal kèm hạn chờ wrapper. Chưa thể chỉ thêm `sudo` mà giữ `_giet` killpg dưới quản lý. Regression cần user/sandbox/thiếu principal, hai khe khác danh tính, không lộ credential, timeout và heartbeat tiếp tục. **Chưa có mã TDD đầy đủ cho chuỗi này; không giao code từ mô tả này, không tính test và không đóng bead.** Chặn trước S6 có Codex và nghiệm thu S5/D5.
- C02 của 3c: sửa `_ket_thuc` có hạn cuối là cần nhưng chưa đủ; harness phải quản lý tiến trình con, chờ dọn hoàn tất sau timeout và xác minh UID thực trước kịch bản cài lịch. Cần thiết kế cùng 3c, không coi daemon-thread timeout là cleanup. **Chưa có phương án đầy đủ để giao code; S6 vẫn đóng.**
- 375px: CSS test chỉ kiểm văn bản; nghiệm thu browser 375/900/1100/1440, bàn phím, no-WebGL, reduced-motion chưa được chạy trong review này. Không tự đóng `bs-78r.5` bằng số đo lịch sử.

## Ghi chú triển khai (17/10/2026, I1)

Đối chiếu với `main` `59f8281`. Em không chạy lại test (I1 chỉ sửa tài liệu).

- **Ghép:** `9a0c0ff` (`merge: V1 Task 1–3`), ngay trên `5da881e`. Commit: Task 1 `66a3553`, Task 2 `2176230`, Task 3 `013a7fe`.
- **Số test:** pytest 2242 → **2243** (+1; số 2243 ghi ở ghi chú plan 1a-2). Node 95 → **101** (+6). Số node em đếm bằng `git grep` các dòng `test(`/`it(` trong `frontend/tests` tại `5da881e` và `9a0c0ff`, không chạy `node --test`. Đúng bảng "Sơ đồ đợt" sau review đợt 6 (không phải mốc 99 cũ).
- **Chỗ lệch khi code:** không ghi nhận. Em không so lại từng dòng với plan.
- **Task 4:** `bs-78r.5` đã đóng; `bs-urj.17` và `bs-78r.8` đã đóng sau khi ghép.
- **Còn lại:** nghiệm thu trên trình duyệt thật (375/900/1100/1440 px, bàn phím, không WebGL, giảm chuyển động) chưa chạy — vẫn ở sổ tay A4 (lịch sử) và mục "Review đợt 6" ở trên. Hai mục "`bs-78r.10`" và "C02 của 3c" trong mục đó nay **đã có mã** (plan bs-78r.10, plan P1, plan 3c đợt 8); phần OS vẫn chờ G3/G4/G5.
