# Lát 2c — Văn phòng 3D isometric — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use ai-skills:subagent-driven-development (recommended) or ai-skills:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Thêm trang **Văn phòng** vào dashboard: cảnh 3D góc nhìn isometric, mỗi dự án đã `them` là một phòng, bốn phòng cố định (Điều phối, Phòng giám đốc, Phòng máy chủ, Góc cà phê), mỗi khe là một nhân vật dựng bằng khối hình học màu pastel với trạng thái Làm / Rảnh / Cần người / Lỗi / Tắt-mất kết nối suy từ nhịp tim + sự kiện; bấm nhân vật mở bead, bấm phòng lọc Công việc; có chế độ giảm chuyển động, bản danh sách cho bàn phím / không WebGL, và giữ nguyên CSP chặt.

**Architecture:** Không kho trạng thái mới (Q12). Server thêm `GET /api/van-phong`: nhân vật suy từ `trang_thai_khe()` của 3a-1 (spec 3 §10.1 — định nghĩa duy nhất) cộng một lớp **chỉ để hiển thị** (`hien_thi` năm hàng, phòng đặt nhân vật, `can_nguoi` khi phiếu cuối có escalation chưa đóng — sự kiện 4a-1); số việc chờ Đại ca và "Hệ cần xem" lấy bằng chính route `/api/phe-duyet` nên badge Phòng giám đốc luôn khớp trang Phê duyệt; sức khoẻ trạm (tủ máy xanh/vàng/đỏ) suy từ estop + Hệ cần xem + khe. Frontend thêm TresJS (`@tresjs/core`) + `three` đúng như spec 2 §8; luật bố trí/hiển thị thuần trong `src/van_phong/*.js` (test `node --test`), component 3D trong `src/van_phong/*.vue`, trang `/van-phong` **nạp lười** để three.js không vào gói chính (giữ D6 của 2a). Chữ trên biển/bong bóng vẽ bằng canvas 2D làm texture — không font/ảnh tải về, không HTML. Cổng CSP mới `kiem-dist.mjs` quét bundle sau build (không `eval`/`new Function`/biên dịch WebAssembly, không script/style nội tuyến, three không ở gói chính) + kiểm chạy thật trên trình duyệt với CSP của tram-api (Task 8).

**Tech Stack:** Python 3.12 (`uv`), FastAPI 0.143.0 (đã khoá ở 2a), SQLite stdlib, `pytest`; Vue 3.5.43 + vue-router 5.4.0 + Vite 8.3.4 + `@vitejs/plugin-vue` 6.0.10 (đã khoá ở 2a); **mới:** `@tresjs/core@5.9.1` (MIT, phát hành 28/09/2026) + `three@0.186.1` (MIT, 24/09/2026); `node:test`.

**Spec:** [docs/specs/2026-10-12-phan-2-dashboard.md](../specs/2026-10-12-phan-2-dashboard.md) (ĐÃ DUYỆT) — §5 "Lát 2c — cần phần 3 + 4" mục **5.5**, §4 (bảo mật — mục 4, 6: CSP chặt, cấm `v-html`), §7 (`GET /api/van-phong`), §8 (TresJS + `three`, khoá phiên bản chính xác), §9 mục 1, 4. Đọc kèm: spec 3 [§10, §10.1](../specs/2026-10-13-phan-3-may-tho-han-muc.md) (giao diện cho 2c) · spec 4 [§12](../specs/2026-10-13-phan-4-giao-viec.md) (`escalation.tao/dong`) · plan [3a-1](2026-10-13-lat-3a-1-may-tho.md) Task 13, 15, 21 · plan [2b](2026-10-13-lat-2b-doi-ngu-usage.md) Task 5, 9–12 · plan [4a-1](2026-10-13-lat-4a-1-giao-viec.md) Task 13, 19 · plan [2a](2026-10-13-lat-2a-dashboard.md) Task 10, 12, 23, 24.

## Global Constraints

**Review tĩnh đợt 3:** không chạy mã/test/build trong review; N₀ đo từ main thật1458 +1b-2T9 + toàn chuỗi trước2c, M₀ từ main18 + bổ sung trước2c. Số1059/node13 là lịch sử scratch. Assertion hồi quy mở rộng test hiện có; kỳ vọng cuối vẫn N₀+7, M₀+8. Quét regex bundle không chứng minh CSP runtime hay toàn dependency graph của chunk.


- **Điều kiện tiên quyết (thứ tự code đã chốt):** `3a-1` → `1b-3` → `2b` → `4a-1` → `1b-2` → `3a-2` → `4a-2` → `3b` → `4b` → `4c` → **`2c`** — mọi plan đứng trước đã thực thi và ghép vào `main`. **N₀** = số `passed` của `uv run pytest -q` trên `main` lúc bắt đầu lát; **M₀** = số test `node --test` (`npm run kiem`). Bản dựng thử của plan này (main 720 + 3a-1 295 + 2b 44, **chưa có** 1b-3, 4a-1, 1b-2 và năm plan đợt 3) có N₀ = **1059**, M₀ = **13**; mọi con số dưới đây viết `N₀ + k` kèm số trên bản dựng thử. N₀ test cũ luôn xanh.
- **TDD:** mỗi task viết test trước, chạy thấy fail (thông báo ở Step 2 là kết quả chạy thật trên bản dựng thử), viết mã, chạy thấy pass. Component `.vue` không có test đơn vị riêng (như 2a, 2b) — cổng kiểm là `npm run kiem` (luật thuần + quét chèn HTML) + `npm run build` (biên dịch template) + `npm run kiem-dist` (CSP của bundle) + kiểm chạy thật trên trình duyệt ở Task 8.
- **Mỗi file nguồn ≤ ~120 dòng** (cả `.vue`; dài nhất của plan: `CongViec.vue` 97 sau sửa, `nhan_vat.py` 72, `Phong3D.vue` 68, `VanPhong.vue` 68). Định danh tiếng Việt không dấu. Giờ lưu UTC `YYYY-MM-DDTHH:MM:SSZ`; hàm nghiệp vụ nhận `bay_gio` tiêm được (`PhuThuocApi.dong_ho`).
- **Mỗi task một worktree, một nhánh, một commit**, tạo từ `main` **sau khi đã ghép đợt trước** ("Chuẩn bị", "Sơ đồ đợt chạy"). Task cùng đợt không sửa chung file. Không push, không merge hộ.
- **Phụ thuộc mới — chỉ hai gói spec 2 §8 cho phép:** `npm install --save-exact @tresjs/core@5.9.1 three@0.186.1` (Task 4 — **bước duy nhất cần mạng**; phụ thuộc bắc cầu do npm giải, khoá trong `package-lock.json` — G2). Không gói Python mới. Không loader mô hình (GLTF/Draco/Meshopt/KTX2 — cần WebAssembly ⇒ `'wasm-unsafe-eval'`), không font/texture/sprite tải về, không `@tresjs/cientos` hay gói hệ sinh thái khác.
- **Test không:** gọi Claude/Codex/Ollama thật, gọi mạng, đụng Keychain, đụng `~/.tram` thật (`TRAM_HOME` tạm — `tests/conftest.py`), chạy `launchctl`, tạo user macOS, chạy `bd` trên repo thật (`BdGia`), `git push`. Script kiểm tay `tests/chay_thu_van_phong.py` (Task 8) chỉ dùng dữ liệu giả trong thư mục tạm và nghe `127.0.0.1`.
- **Bảo mật (spec 2 §4) — giữ nguyên, không nới:** CSP của tram-api **không đổi** (`script-src 'self'`, không `unsafe-eval`/`unsafe-inline`/`wasm-unsafe-eval`); `GET /api/van-phong` chỉ đọc, theo chính sách đọc chung (không danh tính), qua middleware CSP + kiểm `Host` 421 của 2a; frontend cấm `v-html`/`:innerHTML`/`innerHTML`… (`kiem-an-toan.mjs`), chuỗi từ server hiển thị bằng `{{ }}` hoặc vẽ bằng `fillText` lên canvas (không bao giờ thành HTML); server `lam_sach` tiêu đề bead; **không trả `ten_goi_nho`** (có thể là email — §5.4) và không đọc cột/trường chứa `ma_giao`; lý do sức khoẻ là câu cố định + tên dự án / mã khe, không trả nội dung lỗi.
- **Cổng chạy thật không chặn plan/code** (Đại ca chốt "code xong hết rồi mới chạy thật"): xem trên máy A / điện thoại qua tailnet chờ **#5**; dữ liệu khe thật chờ 3a-2/3b; ghi "chờ chạy thật" ở "Để sau".
- Lệnh kiểm: `uv run pytest -q` từ gốc worktree; trong `frontend/`: `npm run kiem`, `npm run build`, `npm run kiem-dist` (có từ Task 4).

## Phụ thuộc đã có (main + plan trước) — dùng, không sửa trừ chỗ ghi rõ

| Thứ dùng | Ở đâu (plan) | Plan 2c dùng ở |
|---|---|---|
| `TrangThaiKhe(khe_id, cli, ten_goi_nho, vai_uu_tien, trang_thai, phieu, han_muc, cau_dao, so_phien, nhip_cuoi)`; `trang_thai_khe(kho, *, bay_gio, ch)` — sáu giá trị `tat\|mat_ket_noi\|loi\|can_nguoi\|lam\|ranh`; `phieu = {giao_id, bead_id, du_an, buoc, tieu_de}` khi `lam`/`can_nguoi` | `tram/phieu/trang_thai.py` (3a-1 Task 21) | Task 1, 5 |
| `KhoPhieu(duong_dan)`: `.db`, `.giao_dich()`, `.ghi_su_kien(du_an, loai, du_lieu, *, luc, bead_id=None, …)`, `.close()`; bảng `phieu(giao_id, du_an, bead_id, khe_id, noi_dung JSON — GỒM ma_giao, trang_thai, …)`, bảng `su_kien(id, luc, du_an, bead_id, loai, tac_nhan, du_lieu, …)` | `tram/phieu/kho.py`, `luoc_do.py` (3a-1 Task 13); `tram/su_kien/ket_noi.py` (2a) | Task 1, 5 |
| `dang_ky_khe`, `bat_tat_khe` (`tram/phieu/khe.py`), `ngat_cau_dao` (`cau_dao.py`), `ghi_nhip` (`nhip_tim.py`), `danh_dau_ket_thuc` (`ghi.py`) | 3a-1 Task 13, 15 | test Task 1, 5, 8 |
| Sự kiện `escalation.tao {escalation_id, bead_goc, giao_id, ly_do, ma_thao_tac}`, `escalation.dong {…escalation.tao, tra_loi}` (cùng `du_an`) | `tram/giao_viec/escalation.py`, `tick_doc.py` (4a-1 Task 13, 19) | Task 1 |
| Route `phe_duyet(request) -> {"muc", "so", "loi"}` (`/api/phe-duyet`; 2b thêm mục cầu dao khe); `trang_thai_tram`; `estop.dang_bat()` (`tram/chu/estop.py`) | `tram/api/tuyen_doc.py` (2a Task 12, 2b Task 5) | Task 5 |
| `PhuThuocApi(cau_hinh, cac_du_an, …, mo_kho_phieu, dong_ho, …)`; `CAC_TUYEN` (**sửa ở Task 5** — chỉ thêm `van_phong.router`) | `tram/api/phu_thuoc.py`, `app.py` (2a, 3a-1 Task 23, 2b Task 11, 1b-3) | Task 5 |
| `lam_sach(s, n)` | `tram/suy/lam_sach.py` (2a) | Task 1 |
| Test: `kho_tam`, `dat_phieu(kho, khe_id, *, luc, **kw)`, `LUC` (`tests/kho_phieu_gia.py`); `tao_pt(tmp_path, bds, *, thu_muc_tinh=None)`, `DAI_CA` (`tests/api_gia.py`); `goi` (`tests/asgi_gia.py`); `BdGia(beads, *, ra_loi_truoc=…)` (`tests/bd_gia.py`); `bead` (`tests/bead_gia.py`); fixture `tram_home_tam` | 2a, 3a-1 | test Task 1, 5, 8 |
| Frontend: `doc` (`api.js`); `kho` với `phienBan`, `phienBanDoiNgu` (`kho.js` — 2a, 2b Task 10); `tuyen` (`tuyen.js` — **sửa ở Task 6**); menu `KhungChinh.vue` (**sửa ở Task 6**); `CongViec.vue` (**sửa ở Task 7** — đọc `?du_an=&bead=`), `NganBen.vue` (nhận `the` tối thiểu `{du_an, id}`); lớp CSS `.cong-cu`, `.muc`, `.nho`, `.loi`, `.canh-bao`, biến `--vien` (`kieu.css`) | 2a Task 23–24, 2b Task 10, 12, 1b-3 | Task 6, 7 |
| `vite.config.js` (`vue()` + `define` + proxy), `kiem-an-toan.mjs`, `package.json` (`kiem`, `build`) | 2a Task 23 | Task 4 sửa `vite.config.js`, `package.json` |

## Câu hỏi / giả định

Chỗ spec để ngỏ — Em chọn phương án an toàn nhất, không tự mở rộng phạm vi. Cột "Loại": **HỢP ĐỒNG MỚI** = giao diện/hành vi phần khác (plan khác, Đại ca khi cài) sẽ dựa vào — **Đại ca cần chốt**; **lệch chữ spec** = làm khác câu chữ spec; **giả định** = chi tiết thực thi, Đại ca gạch nếu không đồng ý.

| # | Chỗ mơ hồ | Chọn | Vì sao | Loại |
|---|---|---|---|---|
| G1 | TresJS/three có cần `unsafe-eval` không (spec 2 §4 mục 6) | **Giữ CSP nguyên văn; runtime còn chờ Task 8.** Tác giả plan ghi đã quét tĩnh bản phát hành (đọc qua unpkg, không cài): `three@0.186.1` (`build/three.core.js`, `three.module.js`), `@tresjs/core@5.9.1` (`dist/tres.js`), `@vueuse/core@14.4.0`, `@vueuse/shared@14.4.0`, `radashi@12.9.6`, `@vue/devtools-kit@8.2.1`, `@vue/devtools-shared@8.2.1`: **không** có `eval(`, `new Function`, `WebAssembly.compile/instantiate`; `createObjectURL` trong three chỉ nằm trong chú thích. Phần cần `'wasm-unsafe-eval'` trong hệ three là các **loader nén** (Draco, Meshopt, Basis/KTX2) — plan **cấm** dùng loader, mọi hình tự dựng. WebGL/shader không chịu CSP `script-src`. Ba lớp chặn: (1) `kiem-dist.mjs` quét bundle sau mỗi build; (2) Task 8 chạy trang dưới CSP thật của tram-api, console không có "Refused…"; (3) nếu một ngày cần nới, **dừng và hỏi Đại ca** — không tự thêm `'wasm-unsafe-eval'`/`'unsafe-eval'` | Spec cấm `unsafe-eval`; quét thấy không cần; loader là chỗ duy nhất có WASM | giả định (review này không mạng/không chạy; chưa xác minh độc lập phiên bản hay CSP runtime) |
| G2 | Phiên bản + phụ thuộc bắc cầu | `@tresjs/core@5.9.1` (28/09/2026, 15 ngày trước 13/10) — **không** chọn 5.9.2 (29/09, mới đúng 14 ngày, đổi `@vueuse/core` lên `^15`); `three@0.186.1` (24/09/2026), peer `three >=0.133`, `vue >=3.4` khớp. TresJS kéo theo `@vueuse/core ^14.3.0`, `@vue/devtools-api ^8.1.2` (→ `@vue/devtools-kit`, `birpc`, `hookable`, `perfect-debounce`), `@pmndrs/pointer-events ^6.6.30`, `radashi ^12.9.1` — npm giải lúc cài, khoá trong `package-lock.json`; người thực thi ghi danh sách + số gói + `npm audit` vào thân commit Task 4. TresJS gọi `registerTresDevtools` cả ở production (nạp `@vue/devtools-kit`, có `innerHTML` trong overlay devtools) — chỉ chạy khi có Vue Devtools; Task 8 xác nhận không vi phạm CSP | Spec §8 chỉ nêu gói trực tiếp; gói bắc cầu là hệ quả không tránh được | **lệch chữ spec** (gói bắc cầu) — Đại ca biết |
| G3 | "Cần người: bead của khe chờ Đại ca (`--can-hoi`, bí)" | Giữ nguyên `trang_thai_khe` (3a-1 chỉ tính `bao.can_hoi` của phiếu **đang hiệu lực**). Thêm lớp **chỉ hiển thị** ở 2c: khe `ranh` hoặc `loi` (nhưng cầu dao không ngắt) mà **phiếu cuối** (đã kết thúc) có `escalation.tao` cùng `giao_id` chưa có `escalation.dong` cùng `escalation_id` → nhân vật `can_nguoi`, ngồi ở phòng dự án, bong bóng là bead đó; hết khi escalation đóng hoặc khe nhận phiếu mới. **Không** sửa `trang_thai_khe` vì 4a-1 `khe_nhan` dùng `trang_thai in ("ranh", "lam")` để chọn khe — đổi `ranh` → `can_nguoi` sẽ đổi hành vi giao việc | Spec 3 §10.1 ghi `can_nguoi` gồm "escalation liên kết chưa đóng" nhưng 3a-1 để phần đó cho 4a và 4a-1 không làm; theo 4a-1, `can_hoi`/`bi` làm phiếu kết thúc ngay nên không có lớp này thì "Cần người" gần như không bao giờ hiện | **lệch chữ spec** (trang Đội ngũ 2b vẫn hiện "Rảnh" cho khe đó — "Cần sửa spec sau") |
| G4 | "Điều phối (máy A — sáng đèn khi có phiên điều phối)" | **Không spec/plan nào có tín hiệu "phiên điều phối đang mở"** (1b-2 phiên tay MCP không ghi sự kiện; 4b `POST /api/phieu/kiem` chỉ khi tạo phiếu). Trả `sang: null` → đèn xám, biển "Điều phối · chưa có tín hiệu". Hợp đồng chừa sẵn: `sang: true\|false\|null` | Bịa nguồn (vd lấy thao tác dashboard) sẽ báo sai; đèn xám nói thật | **lệch chữ spec** — "Cần sửa spec sau" chọn nguồn |
| G5 | "Tủ máy xanh/vàng/đỏ theo sức khoẻ trạm" | `suc_khoe = {mau, ly_do[≤10]}`: **đỏ** khi estop bật, không đọc được beads của một dự án, hoặc có mục "Hệ cần xem" khác cầu dao khe (`quet.loi`, `cham_cot.bo_qua`, `nho.loi_llm`, `nho.loi_embedder`, và mọi loại `he` mới sau này); **vàng** khi cầu dao khe ngắt, hoặc khe `loi` / `mat_ket_noi`; còn lại **xanh**. Lý do là câu cố định + tên dự án / mã khe / mã bead | "Hệ cần xem" đã là định nghĩa "trạm cần người xem" của spec §5.2; cầu dao hết hạn mức là bình thường hơn lỗi trạm | giả định |
| G6 | Badge Phòng giám đốc + Hệ cần xem lấy từ đâu | `/api/van-phong` gọi **chính hàm route** `tuyen_doc.phe_duyet(request)` → `so`, `muc`, `loi`. Badge luôn bằng badge menu Phê duyệt kể cả khi 4b/4c thêm hàng mới | Một nguồn duy nhất; không chép logic `gom_phe_duyet` | **HỢP ĐỒNG MỚI** — plan khác giữ `phe_duyet(request: Request) -> {"muc": list, "so": int, "loi": dict}` gọi được như hàm thường |
| G7 | Nhân vật ngồi ở đâu | `lam`/`can_nguoi` → phòng dự án của bead; `ranh` → Góc cà phê; `loi`/`tat`/`mat_ket_noi` → phòng dự án của **phiếu cuối** của khe (bàn cũ, "ngồi yên"), chưa từng có phiếu → Góc cà phê. Dự án của bead không còn trong `du-an/` → Góc cà phê (trạng thái giữ nguyên). Trong phòng: 3 bàn một hàng, xếp theo `khe_id` | Spec chỉ định chỗ cho Làm/Rảnh | giả định |
| G8 | JSON `/api/van-phong` (spec §7 chỉ phác thảo) | Xem "Hợp đồng JSON". `hien_thi` ∈ `lam\|ranh\|can_nguoi\|loi\|tat` (năm hàng §5.5; `mat_ket_noi` → `tat`); `trang_thai` giữ giá trị gốc để phân biệt | Server suy, trình duyệt chỉ vẽ (Q12) | **HỢP ĐỒNG MỚI** |
| G9 | Bấm nhân vật / bấm phòng | Nhân vật có bead → `/cong-viec?du_an=<dự án>&bead=<id>` (trang Công việc lọc dự án + mở ngăn bên bead đó); không bead → `/doi-ngu`. Phòng dự án → `/cong-viec?du_an=<dự án>`; Phòng giám đốc, Phòng máy chủ → `/phe-duyet`; Góc cà phê → `/doi-ngu`; Điều phối không dẫn đi đâu. `CongViec.vue` đọc `?du_an=&bead=` (mới), mở ngăn bên **một lần** mỗi lần địa chỉ đổi | Spec chỉ nói "mở bead đang làm" và "lọc Công việc theo dự án"; ngăn bên của 2a đã là chỗ "mở bead" | **HỢP ĐỒNG MỚI** (địa chỉ sâu của trang Công việc) |
| G10 | "Tên theo CLI + số khe" | `"<CLI> <số cuối của tên khe>"` (`B/claude-1` → "Claude 1"; tên không có số → "Claude rieng"); trùng giữa hai máy → thêm "(<máy>)". Không dùng `ten_goi_nho` | Đúng chữ spec; tránh lộ email | giả định |
| G11 | Chế độ giảm chuyển động | Mặc định theo `prefers-reduced-motion`; ô "Giảm chuyển động" bật/tắt trong phiên. Bật: `render-mode="on-demand"` (chỉ vẽ khi dữ liệu đổi), không lắc lư/vẫy tay. Tắt: nhân vật đang làm nhún nhẹ (±4 cm), tay giơ vẫy. Đổi chế độ thì dựng lại `TresCanvas` (`:key`) vì `renderMode` không chắc phản ứng lúc chạy | Spec "có chế độ giảm chuyển động"; `kieu.css` 2a đã tắt transition theo media query | giả định |
| G12 | Biển tên, bong bóng | Vẽ chữ bằng `CanvasRenderingContext2D.fillText` (font hệ thống) lên canvas → `CanvasTexture` → `Sprite`. Bong bóng = tiêu đề bead (cắt 36 ký tự) + bước (`spec`/`code`/`QC`) | Không asset giấy phép mập mờ; không HTML nên tiêu đề từ beads không thành mã | giả định |
| G13 | "Isometric" | `TresOrthographicCamera` ở `(40, 40, 40)` nhìn gốc (TresJS tự `lookAt(0,0,0)`, tự bỏ camera mặc định khi có camera thứ hai); khung `left/right/top/bottom` tính từ `useTres().sizes.aspectRatio` và `khungNhin()` (TresJS chỉ tự cập nhật camera phối cảnh). Kiểm khi chạy (Task 8): khung hình không méo khi đổi cỡ cửa sổ | Đúng nghĩa isometric (phép chiếu trực giao) | giả định (chưa chạy với TresJS thật) |
| G14 | Kích thước gói (D6 ≤ 2 s của 2a) | Route `/van-phong` nạp lười (`() => import('./trang/VanPhong.vue')`); `kiem-dist.mjs` báo lỗi nếu gói chính chứa `WebGLRenderer`. Chunk Văn phòng ~0,7 MB (three) — Vite in cảnh báo chunk lớn, **chấp nhận** (chỉ tải khi mở trang) | three `extend(THREE)` toàn bộ trong TresCanvas, không tree-shake được | giả định |
| G15 | Cập nhật không tải lại (D2) | Không sửa SSE: trang nghe `kho.phienBan` (`cong_viec_doi`/`phe_duyet_doi`) + `kho.phienBanDoiNgu` (`doi_ngu_doi` — `khe.*`, `chay.*`, `giao.*`, `bao.*`, `tho.*`) và tải lại mỗi 5 giây (như Đội ngũ 2b — nhịp tim không là sự kiện; `escalation.*` không có trong tiền tố SSE) | Không đụng `luong.py` (nhiều plan cùng sửa) | giả định |
| G16 | Truy cập bằng bàn phím / trình đọc màn hình / máy không WebGL | Canvas `aria-hidden`; dưới canvas luôn có **bản danh sách** (`DanhSachVanPhong.vue`): mỗi phòng (link như G9, sức khoẻ + lý do), mỗi nhân vật (link, trạng thái, bong bóng). Không có WebGL → chỉ hiện danh sách | Canvas 3D không truy cập được bằng bàn phím | giả định |
| G17 | Giả định về plan cùng đợt 3 (đã đọc và đối chiếu chuỗi trước) | (a) **3a-2** không đổi chữ ký/sáu giá trị của `trang_thai_khe`, không đổi cột `phieu.noi_dung` `$.buoc`, `$.tieu_de`, `khe_id`; (b) **4a-2** nối bộ giao việc: `escalation.tao/dong` phát thật với đúng dạng 4a-1 (`giao_id`, `escalation_id`, cùng `du_an`); nếu 4a-2 tự đưa escalation vào `trang_thai_khe` thì lớp G3 trùng nhưng vô hại (chỉ áp cho `ranh`); (c) **3b** thêm khe Codex/máy từ xa với `khe_id = <may_id>/<ten>`, `cli = "codex"` — nhân vật tự có, tên "Codex 1 (C)" khi trùng; (d) **4b/4c** thêm hàng Phê duyệt ("Spec chờ duyệt" nối thật, "Feature xong, chờ đóng"…) qua route `phe_duyet` — badge tự đếm; phiếu `buoc = "spec"` → bong bóng "spec"; (e) không plan nào đổi tên/chuyển `tuyen_doc.phe_duyet`, `estop.dang_bat`, `PhuThuocApi.cac_du_an/mo_kho_phieu/dong_ho/cau_hinh`, `kho.phienBan/phienBanDoiNgu`; (f) không plan nào khác thêm gói npm hay đổi `vite.config.js`. Sai điều nào → dừng task, báo người điều phối | Plan đứng cuối chuỗi | **HỢP ĐỒNG MỚI** (giả định giao diện — Codex đối chiếu) |
| G18 | Đụng chung file với plan trước | `tram/api/app.py` (`from tram.api import …` và `CAC_TUYEN`), `frontend/src/tuyen.js`, `KhungChinh.vue`, `CongViec.vue`, `package.json`, `vite.config.js`. Bản vá đã rebase tĩnh trên main và chuỗi trước, giữ route Ký ức/ghép thợ và ganGiaoViec; nếu triển khai trên HEAD khác: `git apply --check` lỗi → áp tay đúng các dòng `+` cạnh **dòng neo** (dòng `-`/ngữ cảnh gần nhất còn nguyên), giữ phần của plan khác, chạy đủ kiểm, ghi vào mô tả commit; dòng neo đã mất → dừng, báo người điều phối | Cùng cách 2b G2 | giả định |

## Hợp đồng JSON (lát 2c)

`GET /api/van-phong` (chỉ đọc, không cần danh tính — chính sách đọc chung của spec 2 §4):

```json
{"phong": [
   {"ma": "dieu-phoi", "loai": "dieu_phoi", "ten": "Điều phối", "sang": null},
   {"ma": "giam-doc", "loai": "giam_doc", "ten": "Phòng giám đốc", "so_cho": 2},
   {"ma": "may-chu", "loai": "may_chu", "ten": "Phòng máy chủ",
    "suc_khoe": {"mau": "vang", "ly_do": ["Cầu dao khe B/claude-4 đang ngắt", "Khe B/codex-2: mất kết nối"]}},
   {"ma": "ca-phe", "loai": "ca_phe", "ten": "Góc cà phê"},
   {"ma": "du-an:hr-codex", "loai": "du_an", "ten": "hr-codex", "du_an": "hr-codex"}],
 "nhan_vat": [
   {"khe_id": "B/claude-1", "ten": "Claude 1", "cli": "claude", "trang_thai": "lam", "hien_thi": "lam",
    "phong": "du-an:hr-codex",
    "bead": {"du_an": "hr-codex", "bead_id": "hr-1", "tieu_de": "Sửa cắt UTF-8 tóm tắt hoàn tiền", "buoc": "code"}},
   {"khe_id": "B/codex-2", "ten": "Codex 2", "cli": "codex", "trang_thai": "mat_ket_noi", "hien_thi": "tat",
    "phong": "ca-phe", "bead": null}],
 "kho_phieu": true}
```

- `phong`: bốn phòng cố định theo thứ tự trên rồi mỗi dự án trong `pt.cac_du_an()` (`ma = "du-an:<tên>"`). `sang`: `true | false | null` (null = chưa có nguồn — G4). `suc_khoe.mau`: `xanh | vang | do`.
- `nhan_vat[].trang_thai`: sáu giá trị của `trang_thai_khe` hoặc `can_nguoi` của lớp G3; `hien_thi`: năm hàng §5.5; `bead` khác null khi `lam`/`can_nguoi`; `phong` luôn là một `ma` có trong `phong` (G7).
- Kho phiếu chưa bật (`mo_kho_phieu = None`): `nhan_vat: []`, `kho_phieu: false`, phòng vẫn đủ.
- Không trường nào chứa `ten_goi_nho`, `ma_giao`, nội dung lỗi thô.

Trang Công việc nhận địa chỉ `#/cong-viec?du_an=<dự án>[&bead=<id>]` (G9).

## File Structure

```
tram/
  suy/nhan_vat.py              # HIEN_THI, ten_nhan_vat, nhan_vat (lớp hiển thị trên trang_thai_khe)        — Task 1
  suy/van_phong.py             # PHONG_CO_DINH, suc_khoe, cac_phong                                         — Task 2
  api/van_phong.py             # GET /api/van-phong                                                         — Task 5
  api/app.py                   # (sửa) thêm van_phong.router                                                 — Task 5
frontend/
  src/van_phong/bo_tri.js      # CANH, boTriPhong, viTriCho, datNhanVat, khungNhin                           — Task 3
  src/van_phong/hien_thi.js    # MAU, TEN_HIEN_THI, tuThe, mauThan, catChu, chuBien, chuBongBong, duongDan* — Task 3
  tests/van_phong.test.mjs     #                                                                             — Task 3
  package.json, package-lock.json   # (sửa) @tresjs/core 5.9.1, three 0.186.1; script kiem-dist              — Task 4
  vite.config.js               # (sửa) templateCompilerOptions của TresJS                                    — Task 4
  kiem-dist.mjs                # cổng CSP của bundle: quetJs, quetHtml, kiemGoiChinh                          — Task 4
  tests/kiem_dist.test.mjs     #                                                                             — Task 4
  src/van_phong/the_chu.js     # taoTheChu (canvas 2D → CanvasTexture)                                       — Task 6
  src/van_phong/TheChu3D.vue, Phong3D.vue, NhanVat3D.vue, CanhVanPhong.vue                                   — Task 6
  src/trang/VanPhong.vue       # trang /van-phong                                                             — Task 6
  src/tuyen.js, src/KhungChinh.vue  # (sửa) route nạp lười + menu "Văn phòng"                                 — Task 6
  src/van_phong/DanhSachVanPhong.vue                                                                          — Task 7
  src/trang/VanPhong.vue, src/trang/CongViec.vue   # (sửa) gắn danh sách; đọc ?du_an=&bead=                  — Task 7
tests/
  test_suy_nhan_vat.py (1) · test_suy_van_phong.py (2) · test_api_van_phong.py (5)
  chay_thu_van_phong.py        # máy chủ dữ liệu giả để kiểm tay trên trình duyệt (không phải test pytest)   — Task 8
```

## Chuẩn bị (người điều phối)

```bash
cd "/Users/dai-ca/Developer/Ben Station"
git status --short            # chỉ được có .beads/interactions.jsonl, .DS_Store — không đụng
uv run pytest -q              # ghi N₀
(cd frontend && npm ci && npm run kiem && npm run build)   # ghi M₀; npm ci dùng phụ thuộc đã khoá, chưa có TresJS
```

**Mỗi task một worktree**, tạo từ `main` **sau khi đã ghép mọi task của đợt trước**:

```bash
N=5   # số task
git worktree add .worktrees/2c-t$N -b 2c/t$N main
cd .worktrees/2c-t$N && uv sync && uv run pytest -q    # kỳ vọng: số "sau đợt trước" trong Sơ đồ đợt chạy
(cd frontend && npm ci)                                  # task có file trong frontend/ (3, 4, 6, 7, 8)
```

Cuối mỗi task: người thực thi commit trong worktree; người điều phối kiểm (mọi dòng thêm có nguyên văn trong plan; số test đúng kỳ vọng; file ≤ ~120 dòng) rồi `git merge --no-ff 2c/t$N` vào `main` (không push). Ghép xong cả đợt → `uv run pytest -q`, `npm run kiem`, `npm run build` (+ `npm run kiem-dist` từ đợt 1) trên `main` phải khớp số "sau đợt".

Mã: file **mới** cho nguyên văn đầy đủ; file **có sẵn** cho bản vá unified diff (sinh bằng `git diff` từ bản dựng thử — G18). Áp: lưu khối `diff` ra file rồi `git apply --check <file> && git apply <file>`. Dòng ghi công trong lệnh commit: thay `<model đang thực thi>` bằng đúng tên model của người thực thi task.

---

### Task 1: Nhân vật — lớp hiển thị trên `trang_thai_khe`

**Độ khó:** `de` · **Đợt:** 1 · **Song song với:** Task 2, 3, 4 · **Phải xong trước:** —

**Files:**
- Create: `tram/suy/nhan_vat.py`
- Test: `tests/test_suy_nhan_vat.py` (mới)

**Interfaces:**
- Consumes: `TrangThaiKhe`, `trang_thai_khe` (3a-1 Task 21); `KhoPhieu` (3a-1 Task 13); `lam_sach` (2a); sự kiện `escalation.tao/dong` (4a-1); test: `kho_tam`, `dat_phieu`, `LUC`, `dang_ky_khe`, `bat_tat_khe`, `ngat_cau_dao`, `ghi_nhip`, `danh_dau_ket_thuc`.
- Produces: `HIEN_THI: dict[str, str]`; `CA_PHE = "ca-phe"`; `ma_phong_du_an(du_an) -> "du-an:<du_an>"`; `ten_nhan_vat(cac: list[tuple[khe_id, cli]]) -> dict[khe_id, ten]`; `nhan_vat(kho: KhoPhieu, ds: list[TrangThaiKhe], cac_du_an: list[str]) -> list[dict]` — mỗi phần tử đúng khoá `{khe_id, ten, cli, trang_thai, hien_thi, phong, bead}` của "Hợp đồng JSON".

- [ ] **Step 1: Viết test thất bại**

`tests/test_suy_nhan_vat.py` (mới):

```python
from datetime import timedelta

from kho_phieu_gia import LUC, dat_phieu, kho_tam
from tram.cau_hinh.tram import CauHinhTram
from tram.phieu.cau_dao import ngat_cau_dao
from tram.phieu.ghi import danh_dau_ket_thuc
from tram.phieu.khe import bat_tat_khe, dang_ky_khe
from tram.phieu.nhip_tim import ghi_nhip
from tram.phieu.trang_thai import trang_thai_khe
from tram.suy.nhan_vat import nhan_vat, ten_nhan_vat

CH = CauHinhTram()
DA = ["hr-codex", "tram"]


def _khe(kho, may, *ten, cli="claude", ten_goi_nho="Claude"):
    with kho.giao_dich():
        dang_ky_khe(kho, may, [{"ten": t, "cli": cli, "ten_goi_nho": ten_goi_nho, "vai_uu_tien": ["coder"]}
                               for t in ten], luc=LUC)
        for t in ten:
            ghi_nhip(kho, f"{may}/{t}", luc=LUC, giao_id=None, luot=None, buoc_tho="ranh", han_muc=None)


def _nv(kho, cac_du_an=DA):
    return {x["khe_id"]: x for x in nhan_vat(kho, trang_thai_khe(kho, bay_gio=LUC, ch=CH), cac_du_an)}


def test_ten_nhan_vat_theo_cli_va_so_khe_trung_thi_them_may():
    assert ten_nhan_vat([("B/claude-1", "claude"), ("B/codex-2", "codex"), ("B/rieng", "gemini")]) == {
        "B/claude-1": "Claude 1", "B/codex-2": "Codex 2", "B/rieng": "Gemini rieng"}
    assert ten_nhan_vat([("B/claude-1", "claude"), ("C/claude-1", "claude")]) == {
        "B/claude-1": "Claude 1 (B)", "C/claude-1": "Claude 1 (C)"}


def test_phong_va_hien_thi_theo_trang_thai(tmp_path):
    kho = kho_tam(tmp_path)
    _khe(kho, "B", "lam", "ranh", "tat", "dao", "la", ten_goi_nho="dai-ca@vi-du.vn")
    with kho.giao_dich():
        dang_ky_khe(kho, "B", [{"ten": "mat", "cli": "codex", "ten_goi_nho": "x", "vai_uu_tien": ["qc"]}], luc=LUC)
        ngat_cau_dao(kho, "B/dao", ly_do="het-han-muc", toi_luc=LUC + timedelta(hours=1), luc=LUC)
    dat_phieu(kho, "B/lam", bead_id="hr-1", tieu_de="Sửa \u202egiá", buoc="qc")
    cu = dat_phieu(kho, "B/tat", bead_id="hr-2")
    with kho.giao_dich() as db:
        danh_dau_ket_thuc(db, cu.giao_id, "xong", LUC)
        bat_tat_khe(kho, "B/tat", bat=False, vi_sao="", tac_nhan="dai-ca", luc=LUC)
    dat_phieu(kho, "B/la", bead_id="x-1", du_an="da-go")
    nv = _nv(kho)
    assert nv["B/lam"] == {"khe_id": "B/lam", "ten": "Claude lam", "cli": "claude", "trang_thai": "lam",
                           "hien_thi": "lam", "phong": "du-an:hr-codex",
                           "bead": {"du_an": "hr-codex", "bead_id": "hr-1", "tieu_de": "Sửa giá", "buoc": "qc"}}
    assert (nv["B/ranh"]["phong"], nv["B/ranh"]["hien_thi"], nv["B/ranh"]["bead"]) == ("ca-phe", "ranh", None)
    assert (nv["B/tat"]["phong"], nv["B/tat"]["hien_thi"], nv["B/tat"]["bead"]) == ("du-an:hr-codex", "tat", None)
    assert (nv["B/mat"]["trang_thai"], nv["B/mat"]["hien_thi"], nv["B/mat"]["phong"]) == (
        "mat_ket_noi", "tat", "ca-phe")
    assert (nv["B/dao"]["hien_thi"], nv["B/dao"]["phong"]) == ("loi", "ca-phe")
    assert nv["B/la"]["phong"] == "ca-phe" and nv["B/la"]["hien_thi"] == "lam"      # dự án đã gỡ khỏi trạm
    assert "@" not in str(nv) and "ma_giao" not in str(nv)


def test_escalation_mo_cua_phieu_cuoi_thanh_can_nguoi_toi_khi_dong(tmp_path):
    kho = kho_tam(tmp_path)
    _khe(kho, "B", "claude-1")
    p = dat_phieu(kho, "B/claude-1", bead_id="hr-7", tieu_de="Bí chỗ thuế")
    with kho.giao_dich() as db:
        danh_dau_ket_thuc(db, p.giao_id, "bi", LUC)
        kho.ghi_su_kien("hr-codex", "chay.xong", {"khe_id": "B/claude-1", "ket_thuc": "bi"}, luc=LUC)
        kho.ghi_su_kien("hr-codex", "escalation.tao", {"escalation_id": "hr-e1", "bead_goc": "hr-7",
                                                       "giao_id": p.giao_id, "ly_do": "agent-bi"},
                        luc=LUC, bead_id="hr-7")
    x = _nv(kho)["B/claude-1"]
    assert (x["trang_thai"], x["hien_thi"], x["phong"]) == ("can_nguoi", "can_nguoi", "du-an:hr-codex")
    assert x["bead"]["bead_id"] == "hr-7" and x["bead"]["tieu_de"] == "Bí chỗ thuế"
    with kho.giao_dich():
        kho.ghi_su_kien("hr-codex", "escalation.dong", {"escalation_id": "hr-e1", "bead_goc": "hr-7",
                                                        "tra_loi": "ok"}, luc=LUC, bead_id="hr-7")
    x = _nv(kho)["B/claude-1"]
    assert (x["trang_thai"], x["phong"], x["bead"]) == ("loi", "du-an:hr-codex", None)
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_suy_nhan_vat.py -q`
Expected: FAIL — `1 error` (`ModuleNotFoundError: No module named 'tram.suy.nhan_vat'`)

- [ ] **Step 3: Viết mã**

`tram/suy/nhan_vat.py` (mới):

```python
"""Nhân vật của Văn phòng 3D (spec 2 §5.5): mỗi khe một nhân vật, trạng thái lấy từ `trang_thai_khe` của phần 3
(spec 3 §10.1) — KHÔNG có định nghĩa trạng thái thứ hai. Thêm hai việc chỉ để hiển thị:
- `hien_thi`: sáu giá trị gộp thành năm hàng của bảng §5.5 (`mat_ket_noi` → hàng "Tắt / mất kết nối");
- khe `ranh` mà phiếu cuối có escalation chưa đóng (`escalation.tao` cùng `giao_id`, chưa `escalation.dong` — sự
  kiện của 4a-1) → `can_nguoi` (spec 3 §10.1 "escalation liên kết chưa đóng"; plan 2c G3).
Không trả `ten_goi_nho` (có thể là email — §5.4) và không đọc cột nào chứa `ma_giao`."""
import re

from tram.phieu.kho import KhoPhieu
from tram.phieu.trang_thai import TrangThaiKhe
from tram.suy.lam_sach import lam_sach

HIEN_THI = {"lam": "lam", "ranh": "ranh", "can_nguoi": "can_nguoi", "loi": "loi", "tat": "tat", "mat_ket_noi": "tat"}
TEN_CLI = {"claude": "Claude", "codex": "Codex"}
CA_PHE = "ca-phe"


def ma_phong_du_an(du_an: str) -> str:
    return f"du-an:{du_an}"


def ten_nhan_vat(cac: list[tuple[str, str]]) -> dict[str, str]:
    """`[(khe_id, cli)]` → tên "<CLI> <số khe>"; trùng tên giữa các máy thì thêm "(<máy>)"."""
    ten = {}
    for khe_id, cli in cac:
        may, _, rieng = khe_id.partition("/")
        so = re.search(r"(\d+)$", rieng)
        ten[khe_id] = f"{TEN_CLI.get(cli, lam_sach(cli, 32).capitalize())} {so.group(1) if so else rieng}"
    dem: dict[str, int] = {}
    for t in ten.values():
        dem[t] = dem.get(t, 0) + 1
    return {k: (f"{t} ({k.split('/')[0]})" if dem[t] > 1 else t) for k, t in ten.items()}


def _phieu_cuoi(kho: KhoPhieu, khe_id: str) -> dict | None:
    h = kho.db.execute("SELECT giao_id, du_an, bead_id, json_extract(noi_dung, '$.buoc'),"
                       " json_extract(noi_dung, '$.tieu_de'), trang_thai FROM phieu WHERE khe_id = ?"
                       " ORDER BY rowid DESC LIMIT 1", (khe_id,)).fetchone()
    return None if h is None else dict(zip(("giao_id", "du_an", "bead_id", "buoc", "tieu_de", "trang_thai"), h))


def _escalation_mo(kho: KhoPhieu, du_an: str, giao_id: str) -> bool:
    return kho.db.execute(
        "SELECT 1 FROM su_kien t WHERE t.du_an = ? AND t.loai = 'escalation.tao'"
        " AND json_extract(t.du_lieu, '$.giao_id') = ? AND NOT EXISTS (SELECT 1 FROM su_kien d WHERE d.du_an = t.du_an"
        " AND d.loai = 'escalation.dong' AND json_extract(d.du_lieu, '$.escalation_id') ="
        " json_extract(t.du_lieu, '$.escalation_id')) LIMIT 1", (du_an, giao_id)).fetchone() is not None


def _bead(p: dict) -> dict:
    return {"du_an": p["du_an"], "bead_id": p["bead_id"], "tieu_de": lam_sach(p["tieu_de"] or "", 120),
            "buoc": p["buoc"]}


def _mot(kho: KhoPhieu, tt: TrangThaiKhe, ten: str, cac_du_an: list[str]) -> dict:
    trang_thai, bead, cuoi = tt.trang_thai, None, None
    if tt.phieu is not None:
        bead = _bead(tt.phieu)
    elif trang_thai != "lam":
        cuoi = _phieu_cuoi(kho, tt.khe_id)
        if (trang_thai in ("ranh", "loi") and not tt.cau_dao.get("ngat") and cuoi is not None and cuoi["trang_thai"] == "ket_thuc"
                and _escalation_mo(kho, cuoi["du_an"], cuoi["giao_id"])):
            trang_thai, bead = "can_nguoi", _bead(cuoi)
    noi = bead or (cuoi if trang_thai != "ranh" else None)
    phong = ma_phong_du_an(noi["du_an"]) if noi and noi["du_an"] in cac_du_an else CA_PHE
    return {"khe_id": tt.khe_id, "ten": ten, "cli": lam_sach(tt.cli, 32), "trang_thai": trang_thai,
            "hien_thi": HIEN_THI.get(trang_thai, "tat"), "phong": phong, "bead": bead}


def nhan_vat(kho: KhoPhieu, ds: list[TrangThaiKhe], cac_du_an: list[str]) -> list[dict]:
    ten = ten_nhan_vat([(t.khe_id, t.cli) for t in ds])
    return [_mot(kho, t, ten[t.khe_id], cac_du_an) for t in ds]
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_suy_nhan_vat.py -q`
Expected: `3 passed`

Run: `uv run pytest -q`
Expected: `N₀ + 3 passed` (1062 trên bản dựng thử)

- [ ] **Step 5: Commit**

```bash
git add tram/suy/nhan_vat.py tests/test_suy_nhan_vat.py
git commit -m "feat(suy): nhân vật Văn phòng từ trang_thai_khe — năm hàng hiển thị, phòng, escalation mở thành Cần người (spec 2 §5.5; plan 2c G3, G7, G10)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 2: Phòng + sức khoẻ trạm

**Độ khó:** `de` · **Đợt:** 1 · **Song song với:** Task 1, 3, 4 · **Phải xong trước:** —

**Files:**
- Create: `tram/suy/van_phong.py`
- Test: `tests/test_suy_van_phong.py` (mới)

**Interfaces:**
- Consumes: dạng mục Phê duyệt của 2a/2b (`{loai, du_an, bead_id, chi_tiet: {su_kien, khe_id?}}`); dạng nhân vật của Task 1 (chỉ đọc `khe_id`, `trang_thai` — không import Task 1).
- Produces: `PHONG_CO_DINH`; `suc_khoe(*, estop_bat: bool, muc: list[dict], loi_doc: dict[str, str], nhan_vat: list[dict]) -> {"mau": "xanh"|"vang"|"do", "ly_do": list[str]}` (G5); `cac_phong(cac_du_an: list[str], *, so_cho: int, suc_khoe: dict) -> list[dict]` (G4, G8).

- [ ] **Step 1: Viết test thất bại**

`tests/test_suy_van_phong.py` (mới):

```python
from tram.suy.van_phong import cac_phong, suc_khoe

HE_QUET = {"loai": "he", "du_an": "hr-codex", "bead_id": None, "chi_tiet": {"su_kien": "quet.loi"}}
HE_DAO = {"loai": "he", "du_an": "_tram", "bead_id": None,
          "chi_tiet": {"su_kien": "khe.cau_dao_ngat", "khe_id": "B/claude-2"}}
REVIEW = {"loai": "cho-review", "du_an": "hr-codex", "bead_id": "hr-1", "chi_tiet": {}}


def test_suc_khoe_xanh_vang_do():
    assert suc_khoe(estop_bat=False, muc=[REVIEW], loi_doc={}, nhan_vat=[]) == {"mau": "xanh", "ly_do": []}
    nv = [{"khe_id": "B/claude-1", "trang_thai": "mat_ket_noi"}, {"khe_id": "B/claude-3", "trang_thai": "lam"}]
    assert suc_khoe(estop_bat=False, muc=[HE_DAO], loi_doc={}, nhan_vat=nv) == {
        "mau": "vang", "ly_do": ["Cầu dao khe B/claude-2 đang ngắt", "Khe B/claude-1: mất kết nối"]}
    r = suc_khoe(estop_bat=True, muc=[HE_QUET, HE_DAO], loi_doc={"tram": "bd lỗi <bí mật>"}, nhan_vat=[])
    assert r["mau"] == "do"
    assert r["ly_do"] == ["Estop đang bật", "Không đọc được beads của dự án tram", "hr-codex: lỗi quét beads",
                          "Cầu dao khe B/claude-2 đang ngắt"]
    assert "bí mật" not in str(r)


def test_cac_phong_co_dinh_truoc_roi_du_an():
    sk = {"mau": "xanh", "ly_do": []}
    ds = cac_phong(["hr-codex", "tram"], so_cho=3, suc_khoe=sk)
    assert [p["ma"] for p in ds] == ["dieu-phoi", "giam-doc", "may-chu", "ca-phe", "du-an:hr-codex", "du-an:tram"]
    assert ds[0] == {"ma": "dieu-phoi", "loai": "dieu_phoi", "ten": "Điều phối", "sang": None}
    assert ds[1]["so_cho"] == 3 and ds[2]["suc_khoe"] == sk
    assert ds[4] == {"ma": "du-an:hr-codex", "loai": "du_an", "ten": "hr-codex", "du_an": "hr-codex"}
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_suy_van_phong.py -q`
Expected: FAIL — `1 error` (`ModuleNotFoundError: No module named 'tram.suy.van_phong'`)

- [ ] **Step 3: Viết mã**

`tram/suy/van_phong.py` (mới):

```python
"""Phòng của Văn phòng 3D (spec 2 §5.5) và sức khoẻ trạm cho tủ máy ở Phòng máy chủ — suy lúc đọc (Q12).

Sức khoẻ (plan 2c G5): `do` khi estop bật, không đọc được beads của một dự án, hoặc có mục "Hệ cần xem" khác cầu dao
khe; `vang` khi cầu dao khe ngắt hoặc khe `loi` / `mat_ket_noi`; còn lại `xanh`. Chỉ trả câu cố định + tên dự án /
mã khe — không trả nội dung lỗi (có thể chứa đường dẫn, argv)."""
PHONG_CO_DINH = (("dieu-phoi", "dieu_phoi", "Điều phối"), ("giam-doc", "giam_doc", "Phòng giám đốc"),
                 ("may-chu", "may_chu", "Phòng máy chủ"), ("ca-phe", "ca_phe", "Góc cà phê"))
TEN_HE = {"quet.loi": "lỗi quét beads", "cham_cot.bo_qua": "bộ chấm bỏ qua bead lỗi liên tiếp",
          "nho.loi_llm": "memory lỗi LLM", "nho.loi_embedder": "memory lỗi embedder"}
TEN_KHE = {"loi": "lỗi lần chạy cuối", "mat_ket_noi": "mất kết nối"}
GIU_TOI_DA = 10


def suc_khoe(*, estop_bat: bool, muc: list[dict], loi_doc: dict[str, str], nhan_vat: list[dict]) -> dict:
    do, vang = [], []
    if estop_bat:
        do.append("Estop đang bật")
    do += [f"Không đọc được beads của dự án {t}" for t in sorted(loi_doc)]
    for m in muc:
        if m["loai"] != "he":
            continue
        sk = m["chi_tiet"].get("su_kien")
        if sk == "khe.cau_dao_ngat":
            vang.append(f"Cầu dao khe {m['chi_tiet'].get('khe_id')} đang ngắt")
        else:
            do.append(f"{m['du_an']}: {TEN_HE.get(sk, sk)}" + (f" ({m['bead_id']})" if m.get("bead_id") else ""))
    vang += [f"Khe {x['khe_id']}: {TEN_KHE[x['trang_thai']]}" for x in nhan_vat if x["trang_thai"] in TEN_KHE]
    mau = "do" if do else "vang" if vang else "xanh"
    return {"mau": mau, "ly_do": (do + vang)[:GIU_TOI_DA]}


def cac_phong(cac_du_an: list[str], *, so_cho: int, suc_khoe: dict) -> list[dict]:
    """Bốn phòng cố định rồi mỗi dự án đã `them` một phòng. Điều phối: chưa có nguồn tín hiệu "phiên điều phối
    trên máy A" ở spec/plan nào → `sang: None` (plan 2c G4, mục "Cần sửa spec sau")."""
    them = {"dieu-phoi": {"sang": None}, "giam-doc": {"so_cho": so_cho}, "may-chu": {"suc_khoe": suc_khoe}}
    ra = [{"ma": ma, "loai": loai, "ten": ten, **them.get(ma, {})} for ma, loai, ten in PHONG_CO_DINH]
    return ra + [{"ma": f"du-an:{t}", "loai": "du_an", "ten": t, "du_an": t} for t in cac_du_an]
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_suy_van_phong.py -q`
Expected: `2 passed`

Run: `uv run pytest -q`
Expected: `N₀ + 2 passed` (1061)

- [ ] **Step 5: Commit**

```bash
git add tram/suy/van_phong.py tests/test_suy_van_phong.py
git commit -m "feat(suy): phòng Văn phòng 3D và sức khoẻ trạm xanh/vàng/đỏ (spec 2 §5.5; plan 2c G4, G5)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 3: Frontend — luật bố trí và hiển thị thuần (`bo_tri.js`, `hien_thi.js`)

**Độ khó:** `de` · **Đợt:** 1 · **Song song với:** Task 1, 2, 4 (chỉ đụng file mới trong `frontend/`; làm theo "Hợp đồng JSON") · **Phải xong trước:** —

**Files:**
- Create: `frontend/src/van_phong/bo_tri.js`, `frontend/src/van_phong/hien_thi.js`
- Test: `frontend/tests/van_phong.test.mjs` (mới — `npm run kiem` tự chạy mọi `tests/*.test.mjs`)

**Interfaces:**
- Consumes: "Hợp đồng JSON".
- Produces (Task 6, 7 dùng): `bo_tri.js`: `CANH = {phong: 6, buoc: 8, cho: 1.8, cotCho: 3}`, `boTriPhong(phong) -> phong[] có thêm {x, z}`, `viTriCho(i) -> [dx, dz]`, `datNhanVat(phongDaBoTri, nhanVat) -> nhanVat[] có thêm {x, z}`, `khungNhin(phongDaBoTri) -> number`. `hien_thi.js`: `MAU`, `TEN_HIEN_THI`, `tuThe(hienThi) -> {ngoi, giaTay, chamDo, manHinh: 'sang'|'do'|'tat'|null, doMo}`, `mauThan(cli)`, `catChu(s, n)`, `chuBien(phong)`, `chuBongBong(nv) -> string|null`, `duongDanNhanVat(nv) -> {path, query?}`, `duongDanPhong(phong) -> {path, query?}|null`.

- [ ] **Step 1: Viết test thất bại**

`frontend/tests/van_phong.test.mjs` (mới):

```js
import assert from 'node:assert/strict'
import { test } from 'node:test'
import { CANH, boTriPhong, datNhanVat, khungNhin } from '../src/van_phong/bo_tri.js'
import { MAU, catChu, chuBien, chuBongBong, duongDanNhanVat, duongDanPhong, mauThan, tuThe }
  from '../src/van_phong/hien_thi.js'

const PHONG = [{ ma: 'dieu-phoi', loai: 'dieu_phoi', sang: null }, { ma: 'giam-doc', loai: 'giam_doc', so_cho: 2 },
  { ma: 'may-chu', loai: 'may_chu' }, { ma: 'ca-phe', loai: 'ca_phe' },
  { ma: 'du-an:hr', loai: 'du_an', ten: 'hr', du_an: 'hr' }]

test('bố trí phòng thành lưới quanh gốc toạ độ, không chồng nhau', () => {
  const ds = boTriPhong(PHONG)
  assert.equal(ds.length, 5)
  const o = new Set(ds.map((p) => `${p.x},${p.z}`))
  assert.equal(o.size, 5)
  const xs = ds.map((p) => p.x)
  assert.equal(Math.min(...xs) + Math.max(...xs), 0)
  assert.ok(ds.every((p) => Math.abs(p.x) % CANH.buoc === 0 || Math.abs(p.x) % CANH.buoc === CANH.buoc / 2))
  assert.ok(khungNhin(ds) >= Math.max(...xs) + CANH.phong / 2)
  assert.deepEqual(boTriPhong([]), [])
})

test('đặt nhân vật vào chỗ trong phòng; phòng lạ về góc cà phê', () => {
  const ds = boTriPhong(PHONG)
  const nv = datNhanVat(ds, [{ khe_id: 'B/b', phong: 'du-an:hr' }, { khe_id: 'B/a', phong: 'du-an:hr' },
    { khe_id: 'B/c', phong: 'du-an:la' }])
  const hr = ds.find((p) => p.ma === 'du-an:hr')
  const cp = ds.find((p) => p.ma === 'ca-phe')
  const [a, b, c] = ['B/a', 'B/b', 'B/c'].map((k) => nv.find((x) => x.khe_id === k))
  assert.notDeepEqual([a.x, a.z], [b.x, b.z])
  assert.ok(Math.abs(a.x - hr.x) < CANH.phong / 2 && Math.abs(a.z - hr.z) < CANH.phong / 2)
  assert.ok(Math.abs(c.x - cp.x) < CANH.phong / 2)
})

test('tư thế theo năm hàng của bảng §5.5', () => {
  assert.deepEqual(tuThe('lam'), { ngoi: true, giaTay: false, chamDo: false, manHinh: 'sang', doMo: 1 })
  assert.deepEqual(tuThe('ranh'), { ngoi: false, giaTay: false, chamDo: false, manHinh: null, doMo: 1 })
  assert.deepEqual(tuThe('can_nguoi'), { ngoi: true, giaTay: true, chamDo: true, manHinh: 'sang', doMo: 1 })
  assert.equal(tuThe('loi').manHinh, 'do')
  assert.deepEqual(tuThe('tat'), { ngoi: true, giaTay: false, chamDo: false, manHinh: 'tat', doMo: 0.35 })
  assert.deepEqual(tuThe('la'), tuThe('tat'))
})

test('chữ biển, bong bóng, cắt chữ theo ký tự', () => {
  assert.equal(chuBien(PHONG[1]), 'Phòng giám đốc · 2 việc chờ')
  assert.equal(chuBien(PHONG[0]), 'Điều phối · chưa có tín hiệu')
  assert.equal(chuBien({ ...PHONG[0], sang: true }), 'Điều phối · đang có phiên')
  assert.equal(chuBien(PHONG[4]), 'hr')
  assert.equal(catChu('Sửa cắt tóm tắt', 8), 'Sửa cắt…')
  assert.equal(catChu('ngắn', 8), 'ngắn')
  assert.equal(chuBongBong({ hien_thi: 'lam', bead: { tieu_de: 'Sửa thuế', buoc: 'qc' } }), 'Sửa thuế · QC')
  assert.equal(chuBongBong({ hien_thi: 'ranh', bead: null }), null)
})

test('đường dẫn khi bấm và màu pastel', () => {
  assert.deepEqual(duongDanNhanVat({ bead: { du_an: 'hr', bead_id: 'hr-1' } }),
    { path: '/cong-viec', query: { du_an: 'hr', bead: 'hr-1' } })
  assert.deepEqual(duongDanNhanVat({ bead: null }), { path: '/doi-ngu' })
  assert.deepEqual(duongDanPhong(PHONG[4]), { path: '/cong-viec', query: { du_an: 'hr' } })
  assert.deepEqual(duongDanPhong(PHONG[1]), { path: '/phe-duyet' })
  assert.equal(duongDanPhong(PHONG[0]), null)
  assert.equal(mauThan('claude'), MAU.than.claude)
  assert.equal(mauThan('gemini'), MAU.than.khac)
  assert.ok(Object.values(MAU.suc_khoe).every((m) => /^#[0-9a-f]{6}$/.test(m)))
})
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `cd frontend && node --test tests/van_phong.test.mjs`
Expected: FAIL — `Error [ERR_MODULE_NOT_FOUND]: Cannot find module '…/frontend/src/van_phong/bo_tri.js'`

- [ ] **Step 3: Viết mã**

```bash
mkdir -p frontend/src/van_phong
```

`frontend/src/van_phong/bo_tri.js` (mới):

```js
// Bố trí Văn phòng 3D (spec 2 §5.5) — hàm thuần, test bằng node --test. Đơn vị: mét của cảnh three.js;
// mặt sàn là mặt phẳng XZ, trục Y hướng lên. Phòng xếp lưới quanh gốc toạ độ (camera nhìn vào gốc).
export const CANH = { phong: 6, buoc: 8, cho: 1.8, cotCho: 3 }

export function boTriPhong(phong) {
  const n = phong.length
  if (!n) return []
  const cot = Math.max(2, Math.ceil(Math.sqrt(n)))
  const hang = Math.ceil(n / cot)
  return phong.map((p, i) => ({
    ...p,
    x: ((i % cot) - (cot - 1) / 2) * CANH.buoc,
    z: (Math.floor(i / cot) - (hang - 1) / 2) * CANH.buoc,
  }))
}

// Chỗ thứ i trong phòng: 3 bàn một hàng, hàng đầu sát tường sau.
export function viTriCho(i) {
  return [((i % CANH.cotCho) - 1) * CANH.cho, Math.floor(i / CANH.cotCho) * CANH.cho - CANH.cho]
}

// Nhân vật có `phong` không có trong danh sách (dự án vừa gỡ) về Góc cà phê; trong phòng xếp theo khe_id.
export function datNhanVat(phongDaBoTri, nhanVat) {
  const theoMa = new Map(phongDaBoTri.map((p) => [p.ma, p]))
  const nhom = new Map()
  for (const nv of [...nhanVat].sort((a, b) => a.khe_id.localeCompare(b.khe_id))) {
    const ma = theoMa.has(nv.phong) ? nv.phong : 'ca-phe'
    if (!nhom.has(ma)) nhom.set(ma, [])
    nhom.get(ma).push(nv)
  }
  const ra = []
  for (const [ma, ds] of nhom) {
    const p = theoMa.get(ma)
    if (!p) continue
    ds.forEach((nv, i) => {
      const [dx, dz] = viTriCho(i)
      ra.push({ ...nv, x: p.x + dx, z: p.z + dz })
    })
  }
  return ra
}

// Nửa chiều cao khung nhìn của camera trực giao: đủ chứa phòng xa nhất (cộng lề 1 m), tối thiểu 8.
export function khungNhin(phongDaBoTri) {
  const xa = phongDaBoTri.reduce((m, p) => Math.max(m, Math.abs(p.x), Math.abs(p.z)), 0)
  return Math.max(8, xa + CANH.phong / 2 + 1)
}
```

`frontend/src/van_phong/hien_thi.js` (mới):

```js
// Hình thức nhân vật / phòng của Văn phòng 3D (spec 2 §5.5) — hàm thuần. Trạng thái do server suy
// (`hien_thi` ∈ lam | ranh | can_nguoi | loi | tat — tram/suy/nhan_vat.py); ở đây chỉ đổi sang tư thế, màu, chữ.
export const MAU = {
  phong: { du_an: '#cfe2f3', dieu_phoi: '#d9d2e9', giam_doc: '#fce5cd', may_chu: '#d0e0e3', ca_phe: '#ead1dc' },
  tuong: '#f3f3f3', ban: '#e6d5c3', dau: '#ffe0bd', chamDo: '#cc0000', den: '#fff2cc', denTat: '#b7b7b7',
  than: { claude: '#f6b26b', codex: '#9fc5e8', khac: '#b6d7a8' },
  manHinh: { sang: '#a4c2f4', do: '#e06666', tat: '#999999' },
  suc_khoe: { xanh: '#93c47d', vang: '#ffd966', do: '#e06666' },
}
export const TEN_HIEN_THI = { lam: 'Làm', ranh: 'Rảnh', can_nguoi: 'Cần người', loi: 'Lỗi', tat: 'Tắt / mất kết nối' }
const TEN_BUOC = { spec: 'spec', code: 'code', qc: 'QC' }
const TU_THE = {
  lam: { ngoi: true, giaTay: false, chamDo: false, manHinh: 'sang', doMo: 1 },
  ranh: { ngoi: false, giaTay: false, chamDo: false, manHinh: null, doMo: 1 },
  can_nguoi: { ngoi: true, giaTay: true, chamDo: true, manHinh: 'sang', doMo: 1 },
  loi: { ngoi: true, giaTay: false, chamDo: false, manHinh: 'do', doMo: 1 },
  tat: { ngoi: true, giaTay: false, chamDo: false, manHinh: 'tat', doMo: 0.35 },
}

export function tuThe(hienThi) {
  return { ...(TU_THE[hienThi] ?? TU_THE.tat) }
}

export function mauThan(cli) {
  return MAU.than[cli] ?? MAU.than.khac
}

// Cắt theo ký tự (không cắt đôi chữ có dấu tổ hợp sẵn).
export function catChu(s, n) {
  const kt = Array.from(String(s ?? ''))
  return kt.length > n ? `${kt.slice(0, n - 1).join('')}…` : kt.join('')
}

export function chuBien(p) {
  if (p.loai === 'giam_doc') return `Phòng giám đốc · ${p.so_cho} việc chờ`
  if (p.loai === 'dieu_phoi') {
    return `Điều phối · ${p.sang === null || p.sang === undefined ? 'chưa có tín hiệu' : p.sang ? 'đang có phiên' : 'tắt đèn'}`
  }
  return catChu(p.ten ?? p.ma, 28)
}

export function chuBongBong(nv) {
  if (!nv.bead || (nv.hien_thi !== 'lam' && nv.hien_thi !== 'can_nguoi')) return null
  return `${catChu(nv.bead.tieu_de, 36)} · ${TEN_BUOC[nv.bead.buoc] ?? nv.bead.buoc}`
}

// Bấm nhân vật → mở bead đang làm (ngăn bên trang Công việc); không có bead → Đội ngũ AI.
export function duongDanNhanVat(nv) {
  return nv.bead ? { path: '/cong-viec', query: { du_an: nv.bead.du_an, bead: nv.bead.bead_id } } : { path: '/doi-ngu' }
}

// Bấm phòng dự án → lọc Công việc theo dự án; phòng cố định dẫn tới trang tương ứng (plan 2c G9).
export function duongDanPhong(p) {
  if (p.loai === 'du_an') return { path: '/cong-viec', query: { du_an: p.du_an } }
  if (p.loai === 'giam_doc' || p.loai === 'may_chu') return { path: '/phe-duyet' }
  if (p.loai === 'ca_phe') return { path: '/doi-ngu' }
  return null
}
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `cd frontend && npm run kiem`
Expected: `ℹ tests M₀ + 5` (18) · `ℹ fail 0`; `kiem-an-toan: … không có chèn HTML thô`

Run: `cd frontend && npm run build` → `✓ built in …` (hai file chưa được trang nào import — build không đổi)

Run: `uv run pytest -q` → `N₀ passed` (task này không đụng Python)

- [ ] **Step 5: Commit**

```bash
git add frontend/src/van_phong/bo_tri.js frontend/src/van_phong/hien_thi.js frontend/tests/van_phong.test.mjs
git commit -m "feat(frontend): luật bố trí + hiển thị Văn phòng 3D — lưới phòng, chỗ ngồi, tư thế năm hàng, chữ biển, đường dẫn (spec 2 §5.5; plan 2c G7, G9, G12)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 4: Phụ thuộc TresJS + three, cấu hình Vite, cổng CSP của bundle (`kiem-dist.mjs`)

**Độ khó:** `de` · **Đợt:** 1 · **Song song với:** Task 1, 2, 3 · **Phải xong trước:** —

**Files:**
- Modify: `frontend/package.json`, `frontend/package-lock.json` (npm sinh), `frontend/vite.config.js` (2a)
- Create: `frontend/kiem-dist.mjs`
- Test: `frontend/tests/kiem_dist.test.mjs` (mới)

**Interfaces:**
- Consumes: `vite.config.js`, `package.json` của 2a.
- Produces: gói `@tresjs/core` 5.9.1 (`TresCanvas`, `useTres`, `useLoop`, `@tresjs/core/template-compiler-options`), `three` 0.186.1 (`CanvasTexture`, `SRGBColorSpace`); plugin-vue nhận thẻ `Tres*` là phần tử của renderer TresJS; script `npm run kiem-dist`; `kiem-dist.mjs`: `quetJs(van) -> string[]`, `quetHtml(van) -> string[]`, `kiemGoiChinh(van) -> string[]`.

- [ ] **Step 1: Viết test thất bại**

`frontend/tests/kiem_dist.test.mjs` (mới):

```js
import assert from 'node:assert/strict'
import { test } from 'node:test'
import { kiemGoiChinh, quetHtml, quetJs } from '../kiem-dist.mjs'

test('quetJs bắt eval, new Function, biên dịch WebAssembly', () => {
  assert.deepEqual(quetJs('const a = 1; retrieval(x); obj.evaluate()'), [])
  assert.deepEqual(quetJs('eval("1")'), ['eval('])
  assert.deepEqual(quetJs('const f = new Function("a", "return a")'), ['new Function'])
  assert.deepEqual(quetJs('await WebAssembly.instantiate(buf)'), ['WebAssembly.instantiate'])
})

test('quetHtml bắt script/style nội tuyến và thuộc tính sự kiện', () => {
  const sach = '<script type="module" crossorigin src="/assets/index-a.js"></script><link rel="stylesheet" href="/x.css">'
  assert.deepEqual(quetHtml(sach), [])
  assert.deepEqual(quetHtml('<script>alert(1)</script>'), ['<script> nội tuyến'])
  assert.deepEqual(quetHtml('<style>a{}</style><div style="color:red" onclick="x()">'),
    ['<style> nội tuyến', 'thuộc tính style', 'thuộc tính onclick'])
})

test('kiemGoiChinh: three không nằm trong gói chính', () => {
  assert.deepEqual(kiemGoiChinh('import("./VanPhong-x.js")'), [])
  assert.deepEqual(kiemGoiChinh('class WebGLRenderer {}'), ['three nằm trong gói chính — trang Văn phòng phải nạp lười'])
})
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `cd frontend && node --test tests/kiem_dist.test.mjs`
Expected: FAIL — `Error [ERR_MODULE_NOT_FOUND]: Cannot find module '…/frontend/kiem-dist.mjs'`

- [ ] **Step 3: Viết mã**

`frontend/kiem-dist.mjs` (mới):

```js
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

export function kiemGoiChinh(van) {
  return /\bWebGLRenderer\b/.test(van) ? ['three nằm trong gói chính — trang Văn phòng phải nạp lười'] : []
}

function chay() {
  const dist = fileURLToPath(new URL('./dist', import.meta.url))
  const html = readFileSync(join(dist, 'index.html'), 'utf8')
  const loi = quetHtml(html).map((l) => `index.html: ${l}`)
  const chinh = [...html.matchAll(/<script[^>]*\bsrc="\/?([^"]+)"/g)].map((m) => m[1])
  for (const f of chinh) loi.push(...kiemGoiChinh(readFileSync(join(dist, f), 'utf8')).map((l) => `${f}: ${l}`))
  const tep = readdirSync(join(dist, 'assets')).filter((t) => t.endsWith('.js'))
  for (const t of tep) loi.push(...quetJs(readFileSync(join(dist, 'assets', t), 'utf8')).map((l) => `assets/${t}: ${l}`))
  if (loi.length) {
    console.error('kiem-dist: vi phạm CSP chặt:\n' + loi.join('\n'))
    process.exit(1)
  }
  console.log(`kiem-dist: ${tep.length} file JS, không thấy mẫu eval/inline trong quét tĩnh; cần kiểm CSP runtime ở Task 8`)
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) chay()
```

Chạy thử cổng trên bundle hiện tại (chưa có TresJS):

```bash
cd frontend && npm run build && node kiem-dist.mjs
```

Expected: `kiem-dist: 1 file JS, không thấy mẫu eval/inline trong quét tĩnh; cần kiểm CSP runtime ở Task 8` (số file JS tuỳ `main`).

- [ ] **Step 4: Thêm script, cài hai gói, ghim chính xác (cần mạng — chỉ bước này của plan)**

Thêm script vào `frontend/package.json` **trước** khi cài (npm sắp xếp lại `dependencies`, làm lệch ngữ cảnh bản vá):

```diff
--- a/frontend/package.json
+++ b/frontend/package.json
@@ -6,7 +6,8 @@
   "scripts": {
     "dev": "vite",
     "build": "vite build",
-    "kiem": "node --test tests/*.test.mjs && node kiem-an-toan.mjs"
+    "kiem": "node --test tests/*.test.mjs && node kiem-an-toan.mjs",
+    "kiem-dist": "node kiem-dist.mjs"
   },
   "dependencies": {
     "vue": "3.5.43",
```

```bash
cd frontend
npm install --save-exact @tresjs/core@5.9.1 three@0.186.1
node -e "const p=require('./package.json'); console.log(p.dependencies, p.scripts['kiem-dist'])"   # đúng 5.9.1 và 0.186.1, không ^ hay ~
npm ls @tresjs/core three @vueuse/core @vue/devtools-api @pmndrs/pointer-events radashi
npm audit --omit=dev
cd ..
```

Expected: `dependencies` có `"@tresjs/core": "5.9.1"`, `"three": "0.186.1"` (cạnh `vue`, `vue-router` cũ), script `kiem-dist` còn nguyên. Ghi vào thân commit: số gói thêm vào `node_modules`, phiên bản bắc cầu `npm ls` in ra, kết quả `npm audit` (G2). Có lỗ hổng mức `high`/`critical` → **dừng**, báo người điều phối (không tự nâng/hạ phiên bản). Registry không còn đúng hai phiên bản này → dừng, báo (không tự chọn số khác).

`frontend/vite.config.js` (bản vá):

```diff
--- a/frontend/vite.config.js
+++ b/frontend/vite.config.js
@@ -1,9 +1,11 @@
+import templateCompilerOptions from '@tresjs/core/template-compiler-options'
 import vue from '@vitejs/plugin-vue'
 import { defineConfig } from 'vite'
 
 // Component `.vue` dịch sẵn lúc build (G13, spec §8): bản Vue chỉ-runtime, không `new Function` → bật được CSP chặt.
+// Lát 2c: thẻ `Tres*` là phần tử của renderer TresJS, không phải component Vue (templateCompilerOptions của TresJS).
 export default defineConfig({
-  plugins: [vue()],
+  plugins: [vue({ ...templateCompilerOptions })],
   define: {
     __VUE_OPTIONS_API__: 'true',
     __VUE_PROD_DEVTOOLS__: 'false',
```

- [ ] **Step 5: Chạy, thấy pass**

Run: `cd frontend && npm run kiem`
Expected: `ℹ tests M₀ + 3` (16 nếu Task 3 chưa ghép) · `ℹ fail 0`

Run: `cd frontend && npm run build && npm run kiem-dist`
Expected: `✓ built in …`; `kiem-dist: … không thấy mẫu eval/inline trong quét tĩnh; cần kiểm CSP runtime ở Task 8` (chưa trang nào import TresJS)

Run: `uv run pytest -q` → `N₀ passed`

- [ ] **Step 6: Commit**

```bash
git add frontend/package.json frontend/package-lock.json frontend/vite.config.js frontend/kiem-dist.mjs frontend/tests/kiem_dist.test.mjs
git commit -m "build(frontend): thêm @tresjs/core 5.9.1 + three 0.186.1 (spec 2 §8), templateCompilerOptions, cổng CSP kiem-dist (plan 2c G1, G2, G14)" -m "<danh sách gói bắc cầu + npm audit — Step 4>" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 5: tram-api — `GET /api/van-phong`

**Độ khó:** `de` · **Đợt:** 2 · **Song song với:** Task 6 · **Phải xong (đã ghép vào `main`) trước khi bắt đầu:** Task 1, 2

**Files:**
- Create: `tram/api/van_phong.py`
- Modify: `tram/api/app.py` (2a + 3a-1 + 2b + 1b-3 + plan đợt 3)
- Test: `tests/test_api_van_phong.py` (mới)

**Interfaces:**
- Consumes: `nhan_vat` (Task 1); `cac_phong`, `suc_khoe` (Task 2); `trang_thai_khe` (3a-1); `phe_duyet` (`tram/api/tuyen_doc.py` — G6); `estop.dang_bat`; `PhuThuocApi.cac_du_an`, `.mo_kho_phieu`, `.dong_ho`, `.cau_hinh`.
- Produces: `GET /api/van-phong` đúng "Hợp đồng JSON"; `van_phong.router` trong `CAC_TUYEN`.

- [ ] **Step 1: Viết test thất bại**

`tests/test_api_van_phong.py` (mới):

```python
from dataclasses import replace

from api_gia import tao_pt
from asgi_gia import goi
from bd_gia import BdGia
from bead_gia import bead
from kho_phieu_gia import LUC, dat_phieu
from tram.api.app import tao_app
from tram.chu import estop
from tram.phieu.khe import dang_ky_khe
from tram.phieu.kho import KhoPhieu
from tram.phieu.nhip_tim import ghi_nhip

BDS = {"hr-codex": BdGia([bead("hr-1", labels=["cot:cho-review"]), bead("hr-2", labels=["cot:ai-lam"])])}


def _app(tmp_path, bds=BDS, *, kho_phieu=True):
    db = tmp_path / "sk.db"
    kho = KhoPhieu(db)
    with kho.giao_dich():
        dang_ky_khe(kho, "B", [{"ten": "claude-1", "cli": "claude", "ten_goi_nho": "a@b.vn", "vai_uu_tien": ["coder"]}],
                    luc=LUC)
        ghi_nhip(kho, "B/claude-1", luc=LUC, giao_id=None, luot=None, buoc_tho="chay", han_muc=None)
    dat_phieu(kho, "B/claude-1", bead_id="hr-2", tieu_de="Sửa thuế")
    kho.close()
    pt = replace(tao_pt(tmp_path, bds), mo_kho_phieu=(lambda: KhoPhieu(db)) if kho_phieu else None,
                 dong_ho=lambda: LUC)
    return tao_app(pt)


def test_van_phong_phong_nhan_vat_va_badge(tmp_path):
    r = goi(_app(tmp_path), "GET", "/api/van-phong")
    assert r.status == 200 and "unsafe-eval" not in r.headers["content-security-policy"]
    d = r.json()
    phong = {p["ma"]: p for p in d["phong"]}
    assert phong["giam-doc"]["so_cho"] == 1 and phong["may-chu"]["suc_khoe"] == {"mau": "xanh", "ly_do": []}
    assert phong["dieu-phoi"]["sang"] is None and "du-an:hr-codex" in phong
    (nv,) = d["nhan_vat"]
    assert (nv["ten"], nv["hien_thi"], nv["phong"], nv["bead"]["bead_id"]) == ("Claude 1", "lam", "du-an:hr-codex", "hr-2")
    assert d["kho_phieu"] is True and "a@b.vn" not in r.body.decode() and "ma_giao" not in r.body.decode()


def test_van_phong_khi_kho_phieu_tat_va_tram_loi(tmp_path, tram_home_tam):
    tram_home_tam.mkdir(parents=True, exist_ok=True)
    estop.bat("thử")
    bds = {**BDS, "tram": BdGia([], ra_loi_truoc={"tat_ca": 1})}
    d = goi(_app(tmp_path, bds, kho_phieu=False), "GET", "/api/van-phong").json()
    assert d["kho_phieu"] is False and d["nhan_vat"] == []
    sk = {p["ma"]: p for p in d["phong"]}["may-chu"]["suc_khoe"]
    assert sk == {"mau": "do", "ly_do": ["Estop đang bật", "Không đọc được beads của dự án tram"]}
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_api_van_phong.py -q`
Expected: FAIL — `2 failed` (`assert (404 == 200)` — chưa có route; `KeyError: 'kho_phieu'`)

- [ ] **Step 3: Viết mã**

`tram/api/van_phong.py` (mới):

```python
"""`GET /api/van-phong` (spec 2 §5.5, §7 lát 2c): phòng + nhân vật + trạng thái đã suy, chỉ đọc.

Số việc chờ Đại ca và "Hệ cần xem" lấy bằng CHÍNH route `/api/phe-duyet` (`tuyen_doc.phe_duyet`) — badge Phòng giám
đốc luôn khớp trang Phê duyệt, kể cả khi phần 4 thêm hàng mới (plan 2c G6). Nhân vật suy từ `trang_thai_khe`."""
from contextlib import closing

from fastapi import APIRouter, Request

from tram.api.tuyen_doc import phe_duyet
from tram.chu import estop
from tram.phieu.trang_thai import trang_thai_khe
from tram.suy.nhan_vat import nhan_vat
from tram.suy.van_phong import cac_phong, suc_khoe

router = APIRouter()


@router.get("/api/van-phong")
def r_van_phong(request: Request) -> dict:
    pt = request.app.state.pt
    cac_du_an = pt.cac_du_an()
    pd = phe_duyet(request)
    nv = []
    if pt.mo_kho_phieu is not None:
        with closing(pt.mo_kho_phieu()) as kho:
            nv = nhan_vat(kho, trang_thai_khe(kho, bay_gio=pt.dong_ho(), ch=pt.cau_hinh), cac_du_an)
    sk = suc_khoe(estop_bat=estop.dang_bat(), muc=pd["muc"], loi_doc=pd["loi"], nhan_vat=nv)
    return {"phong": cac_phong(cac_du_an, so_cho=pd["so"], suc_khoe=sk), "nhan_vat": nv,
            "kho_phieu": pt.mo_kho_phieu is not None}
```

`tram/api/app.py` (bản vá — G18: nếu ngữ cảnh lệch vì 1b-3 / plan đợt 3 đã thêm router, chỉ thêm `van_phong` vào dòng `from tram.api import …` và `van_phong.router` vào cuối `CAC_TUYEN`, giữ mọi router khác):

```diff
diff --git a/tram/api/app.py b/tram/api/app.py
--- a/tram/api/app.py
+++ b/tram/api/app.py
@@ -3,7 +3,7 @@ from fastapi import FastAPI, Request
 from fastapi.responses import JSONResponse
 from fastapi.staticfiles import StaticFiles
 
-from tram.api import doi_ngu, ghep, luong, noi_bo, tho, tho_them, tuyen_chu, tuyen_doc, tuyen_ghi, tuyen_nho, usage
+from tram.api import doi_ngu, ghep, luong, noi_bo, tho, tho_them, tuyen_chu, tuyen_doc, tuyen_ghi, tuyen_nho, usage, van_phong
 from tram.api.bao_mat import them_header_an_toan
 from tram.api.phu_thuoc import PhuThuocApi
 from tram.beads.bd import KhongThayBead, LoiBd
@@ -12,5 +12,5 @@ from tram.thao_tac.loi import ChuaHoTro, KhongHopLe, KhongThay, XungDot
 
 MA_LOI = {XungDot: 409, KhongHopLe: 422, ChuaHoTro: 501, KhongThay: 404, KhongThayBead: 404, LoiBd: 502,
           LoiNhoKhach: 503}
 CAC_TUYEN = (tuyen_doc.router, tuyen_ghi.router, tuyen_chu.router, tuyen_nho.router, luong.router, tho.router, noi_bo.router,
-             doi_ngu.router, usage.router, tho_them.router, ghep.router)
+             doi_ngu.router, usage.router, tho_them.router, ghep.router, van_phong.router)
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_api_van_phong.py tests/test_api_doc.py tests/test_api_doi_ngu.py -q`
Expected: tất cả pass (`test_api_van_phong.py`: `2 passed`)

Run: `uv run pytest -q`
Expected: `N₀ + 7 passed` (1066 — trên `main` sau đợt 1 + riêng task này)

- [ ] **Step 5: Commit**

```bash
git add tram/api/van_phong.py tram/api/app.py tests/test_api_van_phong.py
git commit -m "feat(api): GET /api/van-phong — phòng, nhân vật, sức khoẻ trạm, badge từ route Phê duyệt (spec 2 §5.5, §7; plan 2c G6, G8)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 6: Frontend — cảnh 3D (phòng, nhân vật, biển chữ) + trang `/van-phong`

**Độ khó:** `kho` (TresJS lần đầu trong repo; chưa chạy với TresJS thật khi viết plan) · **Đợt:** 2 · **Song song với:** Task 5 (chỉ đụng `frontend/`) · **Phải xong trước:** Task 3, 4

**Files:**
- Create: `frontend/src/van_phong/the_chu.js`, `frontend/src/van_phong/TheChu3D.vue`, `frontend/src/van_phong/Phong3D.vue`, `frontend/src/van_phong/NhanVat3D.vue`, `frontend/src/van_phong/CanhVanPhong.vue`, `frontend/src/trang/VanPhong.vue`
- Modify: `frontend/src/tuyen.js`, `frontend/src/KhungChinh.vue`

**Interfaces:**
- Consumes: "Hợp đồng JSON"; `doc` (`api.js`); `kho.phienBan`, `kho.phienBanDoiNgu` (`kho.js`); mọi hàm của Task 3; `TresCanvas`, `useTres`, `useLoop` (`@tresjs/core`), `CanvasTexture`, `SRGBColorSpace` (`three`) — Task 4.
- Produces: route `/van-phong` (nạp lười), mục menu "Văn phòng"; `CanhVanPhong` (props `phong`, `nhanVat`, `chuyenDong`; emit `bam-phong`, `bam-nhan-vat`), `Phong3D` (props `phong`; emit `bam`), `NhanVat3D` (props `nv`, `chuyenDong`; emit `bam`), `TheChu3D` (props `chu`, `viTri`, `cao`, `nen`, `mauChu`), `taoTheChu(chu, {nen, mauChu, cao}) -> {tex, tiLe}`.

Giao diện theo skill `frontend-ui-engineering` như 2a/2b (spec §12.5 — không có bản vẽ, Đại ca xem lại ở Task 8 và khi kiểm tay §9 mục 4). Hình chỉ là hộp, trụ, cầu + màu pastel trong `MAU` (spec §5.5). Thẻ `Tres*` là phần tử của renderer TresJS (nhờ `templateCompilerOptions` — Task 4); sự kiện `@click` đặt trên `TresMesh` (TresJS 5 dùng `@pmndrs/pointer-events`: chỉ vật thể bị trúng đầu tiên nhận sự kiện). `useTres`/`useLoop` chỉ gọi trong component con của `TresCanvas` (`CanhVanPhong`, `NhanVat3D`).

- [ ] **Step 1: Chạy kiểm hiện tại (mốc)**

Run: `cd frontend && npm run kiem && npm run build && npm run kiem-dist`
Expected: `ℹ fail 0`; `✓ built`; `kiem-dist: …` xanh

- [ ] **Step 2: Viết mã mới**

`frontend/src/van_phong/the_chu.js` (mới):

```js
// Biển tên và bong bóng của Văn phòng 3D: vẽ chữ lên canvas 2D rồi dùng làm texture của sprite (plan 2c G12).
// Không tải font hay ảnh nào (không asset giấy phép mập mờ — spec 2 §5.5); không chèn HTML (fillText chỉ vẽ
// chữ) nên tiêu đề bead từ server không thể thành mã; hợp CSP chặt (không cần img-src blob:).
import { CanvasTexture, SRGBColorSpace } from 'three'

const PHONG_CHU = 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif'

export function taoTheChu(chu, { nen = '#ffffff', mauChu = '#333333', cao = 64 } = {}) {
  const c = document.createElement('canvas')
  const g = c.getContext('2d')
  const font = `${Math.round(cao * 0.5)}px ${PHONG_CHU}`
  g.font = font
  const rong = Math.ceil(g.measureText(chu).width + cao * 0.6)
  c.width = rong
  c.height = cao
  g.font = font                          // đổi kích thước canvas làm mất trạng thái vẽ
  g.fillStyle = nen
  g.beginPath()
  g.roundRect(0, 0, rong, cao, cao * 0.25)
  g.fill()
  g.fillStyle = mauChu
  g.textBaseline = 'middle'
  g.fillText(chu, cao * 0.3, cao / 2)
  const tex = new CanvasTexture(c)
  tex.colorSpace = SRGBColorSpace
  return { tex, tiLe: rong / cao }
}
```

`frontend/src/van_phong/TheChu3D.vue` (mới):

```vue
<script setup>
import { computed, onUnmounted, watch } from 'vue'
import { taoTheChu } from './the_chu.js'

const props = defineProps({
  chu: { type: String, required: true },
  viTri: { type: Array, required: true },
  cao: { type: Number, default: 0.5 },
  nen: { type: String, default: '#ffffff' },
  mauChu: { type: String, default: '#333333' },
})
const the = computed(() => taoTheChu(props.chu, { nen: props.nen, mauChu: props.mauChu }))
watch(the, (_, cu) => cu.tex.dispose())
onUnmounted(() => the.value.tex.dispose())
</script>

<template>
  <TresSprite :position="viTri" :scale="[the.tiLe * cao, cao, 1]" :render-order="10">
    <TresSpriteMaterial :map="the.tex" :transparent="true" :depth-test="false" />
  </TresSprite>
</template>
```

`frontend/src/van_phong/Phong3D.vue` (mới):

```vue
<script setup>
import { computed } from 'vue'
import { CANH } from './bo_tri.js'
import { MAU, chuBien } from './hien_thi.js'
import TheChu3D from './TheChu3D.vue'

// Một phòng: sàn + hai tường sau (camera nhìn từ góc +x +y +z) + biển tên + đồ riêng của phòng cố định.
const props = defineProps({ phong: { type: Object, required: true } })
const emit = defineEmits(['bam'])
const S = CANH.phong
const p = computed(() => props.phong)
const mauTu = computed(() => MAU.suc_khoe[p.value.suc_khoe?.mau] ?? MAU.suc_khoe.vang)
const den = computed(() => (p.value.sang ? MAU.den : MAU.denTat))
</script>

<template>
  <TresGroup :position="[p.x, 0, p.z]">
    <TresMesh :position="[0, -0.05, 0]" @click="emit('bam', phong)">
      <TresBoxGeometry :args="[S, 0.1, S]" />
      <TresMeshStandardMaterial :color="MAU.phong[p.loai] ?? MAU.phong.du_an" />
    </TresMesh>
    <TresMesh :position="[0, 0.6, -S / 2]">
      <TresBoxGeometry :args="[S, 1.2, 0.1]" />
      <TresMeshStandardMaterial :color="MAU.tuong" />
    </TresMesh>
    <TresMesh :position="[-S / 2, 0.6, 0]">
      <TresBoxGeometry :args="[0.1, 1.2, S]" />
      <TresMeshStandardMaterial :color="MAU.tuong" />
    </TresMesh>
    <TheChu3D :chu="chuBien(p)" :vi-tri="[0, 1.7, -S / 2]" :cao="0.55" />
    <template v-if="p.loai === 'may_chu'">
      <TresMesh v-for="i in 3" :key="i" :position="[(i - 2) * 1.4, 0.8, -S / 2 + 0.8]">
        <TresBoxGeometry :args="[0.9, 1.6, 0.7]" />
        <TresMeshStandardMaterial :color="mauTu" :emissive="mauTu" :emissive-intensity="0.25" />
      </TresMesh>
    </template>
    <template v-if="p.loai === 'dieu_phoi'">
      <TresMesh :position="[0, 0.8, 0]">
        <TresCylinderGeometry :args="[0.05, 0.05, 1.6, 8]" />
        <TresMeshStandardMaterial :color="MAU.tuong" />
      </TresMesh>
      <TresMesh :position="[0, 1.7, 0]">
        <TresSphereGeometry :args="[0.3, 16, 16]" />
        <TresMeshStandardMaterial :color="den" :emissive="den" :emissive-intensity="p.sang ? 0.8 : 0" />
      </TresMesh>
    </template>
    <template v-if="p.loai === 'giam_doc'">
      <TresMesh :position="[0, 0.4, -1]">
        <TresBoxGeometry :args="[2.2, 0.8, 1]" />
        <TresMeshStandardMaterial :color="MAU.ban" />
      </TresMesh>
      <TresMesh v-if="p.so_cho > 0" :position="[0, 1.3, -1]">
        <TresSphereGeometry :args="[0.25, 16, 16]" />
        <TresMeshStandardMaterial :color="MAU.chamDo" />
      </TresMesh>
    </template>
    <template v-if="p.loai === 'ca_phe'">
      <TresMesh :position="[2.2, 0.45, 2.2]">
        <TresCylinderGeometry :args="[0.5, 0.5, 0.9, 24]" />
        <TresMeshStandardMaterial :color="MAU.ban" />
      </TresMesh>
      <TresMesh :position="[-2.4, 0.5, -2.4]">
        <TresBoxGeometry :args="[0.7, 1, 0.6]" />
        <TresMeshStandardMaterial :color="MAU.than.khac" />
      </TresMesh>
    </template>
  </TresGroup>
</template>
```

`frontend/src/van_phong/NhanVat3D.vue` (mới):

```vue
<script setup>
import { useLoop } from '@tresjs/core'
import { computed, shallowRef } from 'vue'
import { MAU, chuBongBong, mauThan, tuThe } from './hien_thi.js'
import TheChu3D from './TheChu3D.vue'

// Nhân vật = khe (spec 2 §5.5): thân trụ + đầu cầu; ngồi bàn khi làm / cần người / lỗi / tắt, đứng khi rảnh.
const props = defineProps({ nv: { type: Object, required: true }, chuyenDong: { type: Boolean, default: true } })
const emit = defineEmits(['bam'])
const tu = computed(() => tuThe(props.nv.hien_thi))
const yThan = computed(() => (tu.value.ngoi ? 0.55 : 0.75))
const yDau = computed(() => yThan.value + 0.55)
const bongBong = computed(() => chuBongBong(props.nv))
const mo = computed(() => ({ transparent: tu.value.doMo < 1, opacity: tu.value.doMo }))
const nhom = shallowRef(null)
const tay = shallowRef(null)
const pha = [...props.nv.khe_id].reduce((s, c) => s + c.charCodeAt(0), 0) % 7

// Chuyển động nhẹ chỉ khi không bật "giảm chuyển động" (vòng lặp on-demand không gọi callback liên tục).
useLoop().onBeforeRender(({ elapsed }) => {
  if (nhom.value) nhom.value.position.y = props.chuyenDong && props.nv.hien_thi === 'lam'
    ? Math.abs(Math.sin(elapsed * 3 + pha)) * 0.04 : 0
  if (tay.value) tay.value.rotation.z = props.chuyenDong ? Math.sin(elapsed * 4 + pha) * 0.35 : 0
})
const bam = () => emit('bam', props.nv)
</script>

<template>
  <TresGroup :position="[nv.x, 0, nv.z]">
    <template v-if="tu.ngoi">
      <TresMesh :position="[0, 0.35, -0.55]">
        <TresBoxGeometry :args="[1.2, 0.7, 0.6]" />
        <TresMeshStandardMaterial :color="MAU.ban" v-bind="mo" />
      </TresMesh>
      <TresMesh :position="[0, 0.95, -0.7]">
        <TresBoxGeometry :args="[0.6, 0.4, 0.05]" />
        <TresMeshStandardMaterial :color="MAU.manHinh[tu.manHinh]" :emissive="MAU.manHinh[tu.manHinh]"
                                  :emissive-intensity="tu.manHinh === 'do' ? 0.8 : 0.2" v-bind="mo" />
      </TresMesh>
    </template>
    <TresGroup ref="nhom">
      <TresMesh :position="[0, yThan, 0]" @click="bam">
        <TresCylinderGeometry :args="[0.25, 0.3, 0.7, 16]" />
        <TresMeshStandardMaterial :color="mauThan(nv.cli)" v-bind="mo" />
      </TresMesh>
      <TresMesh :position="[0, yDau, 0]" @click="bam">
        <TresSphereGeometry :args="[0.22, 16, 16]" />
        <TresMeshStandardMaterial :color="MAU.dau" v-bind="mo" />
      </TresMesh>
      <TresMesh v-if="tu.giaTay" ref="tay" :position="[0.32, yDau + 0.1, 0]">
        <TresBoxGeometry :args="[0.1, 0.5, 0.1]" />
        <TresMeshStandardMaterial :color="mauThan(nv.cli)" />
      </TresMesh>
      <TresMesh v-if="tu.chamDo" :position="[0, yDau + 0.4, 0]">
        <TresSphereGeometry :args="[0.1, 12, 12]" />
        <TresMeshStandardMaterial :color="MAU.chamDo" :emissive="MAU.chamDo" :emissive-intensity="0.6" />
      </TresMesh>
    </TresGroup>
    <TheChu3D :chu="nv.ten" :vi-tri="[0, yDau + 0.65, 0]" :cao="0.28" />
    <TheChu3D v-if="bongBong" :chu="bongBong" :vi-tri="[0, yDau + 1.05, 0]" :cao="0.34" nen="#fffbe6" />
  </TresGroup>
</template>
```

`frontend/src/van_phong/CanhVanPhong.vue` (mới):

```vue
<script setup>
import { useTres } from '@tresjs/core'
import { computed } from 'vue'
import { khungNhin } from './bo_tri.js'
import NhanVat3D from './NhanVat3D.vue'
import Phong3D from './Phong3D.vue'

// Nội dung bên trong <TresCanvas>: camera trực giao góc isometric (nhìn từ +x +y +z về gốc), ánh sáng, phòng,
// nhân vật. Camera đặt ở component con để đọc được kích thước canvas (useTres chỉ chạy dưới TresCanvas).
const props = defineProps({
  phong: { type: Array, required: true },
  nhanVat: { type: Array, required: true },
  chuyenDong: { type: Boolean, default: true },
})
const emit = defineEmits(['bam-phong', 'bam-nhan-vat'])
const { sizes } = useTres()
const v = computed(() => khungNhin(props.phong))
const a = computed(() => sizes.aspectRatio.value || 1)
</script>

<template>
  <TresOrthographicCamera :position="[40, 40, 40]" :left="-v * a" :right="v * a" :top="v" :bottom="-v"
                          :near="0.1" :far="200" />
  <TresAmbientLight :intensity="1.4" />
  <TresDirectionalLight :position="[10, 25, 15]" :intensity="1.6" />
  <Phong3D v-for="p in phong" :key="p.ma" :phong="p" @bam="(x) => emit('bam-phong', x)" />
  <NhanVat3D v-for="n in nhanVat" :key="n.khe_id" :nv="n" :chuyen-dong="chuyenDong"
             @bam="(x) => emit('bam-nhan-vat', x)" />
</template>
```

`frontend/src/trang/VanPhong.vue` (mới):

```vue
<script setup>
import { TresCanvas } from '@tresjs/core'
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { doc } from '../api.js'
import { kho } from '../kho.js'
import { boTriPhong, datNhanVat } from '../van_phong/bo_tri.js'
import CanhVanPhong from '../van_phong/CanhVanPhong.vue'
import { duongDanNhanVat, duongDanPhong } from '../van_phong/hien_thi.js'

// Văn phòng 3D (spec 2 §5.5). Trạng thái suy ở server (`/api/van-phong`); trang chỉ vẽ. Nhịp tim không phải sự
// kiện → tải lại mỗi 5 giây như trang Đội ngũ AI (plan 2b G15), cộng SSE `doi_ngu_doi` / thay đổi bảng.
const CHU_KY_MS = 5000
const router = useRouter()
const dl = ref(null)
const loi = ref('')
const giamChuyenDong = ref(Boolean(window.matchMedia?.('(prefers-reduced-motion: reduce)').matches))
const coWebGL = (() => {
  try {
    const c = document.createElement('canvas')
    return Boolean(c.getContext('webgl2'))  // three bản ghim yêu cầu WebGL2
  } catch {
    return false
  }
})()
const phong = computed(() => boTriPhong(dl.value ? dl.value.phong : []))
const nhanVat = computed(() => datNhanVat(phong.value, dl.value ? dl.value.nhan_vat : []))
let hen = null
let luotTai = 0

async function tai() {
  const luot = ++luotTai
  try {
    const moi = await doc('/api/van-phong')
    if (luot !== luotTai) return
    dl.value = moi
    loi.value = ''
  } catch (e) {
    if (luot === luotTai) loi.value = e.message
  }
}
onMounted(() => { tai(); hen = setInterval(tai, CHU_KY_MS) })
onUnmounted(() => { clearInterval(hen); luotTai += 1 })
watch(() => [kho.phienBan, kho.phienBanDoiNgu], tai)
const di = (dich) => { if (dich) router.push(dich) }
</script>

<template>
  <section class="van-phong">
    <div class="cong-cu">
      <h1>Văn phòng</h1>
      <label class="chon-giam"><input v-model="giamChuyenDong" type="checkbox">Giảm chuyển động</label>
    </div>
    <p v-if="loi" class="loi" role="alert">{{ loi }}</p>
    <p v-if="dl && !dl.kho_phieu" class="nho">Kho phiếu (phần 3) chưa bật — chưa có nhân vật.</p>
    <div v-if="dl && coWebGL" class="khung-3d" aria-hidden="true">
      <TresCanvas :key="giamChuyenDong ? 'tinh' : 'dong'" clear-color="#f6f5f2" :dpr="[1, 2]"
                  :render-mode="giamChuyenDong ? 'on-demand' : 'always'">
        <CanhVanPhong :phong="phong" :nhan-vat="nhanVat" :chuyen-dong="!giamChuyenDong"
                      @bam-phong="(p) => di(duongDanPhong(p))" @bam-nhan-vat="(n) => di(duongDanNhanVat(n))" />
      </TresCanvas>
    </div>
    <p v-else-if="dl" class="nho">Trình duyệt không bật WebGL — chỉ xem được dạng danh sách.</p>
  </section>
</template>

<style scoped>
.khung-3d { height: min(70vh, 40rem); border: 1px solid var(--vien); border-radius: 8px; overflow: hidden; }
.chon-giam { display: flex; align-items: center; min-width: auto; }
</style>
```

- [ ] **Step 3: Nối route + menu (bản vá — G18)**

`frontend/src/tuyen.js` (route nạp lười — G14; nếu ngữ cảnh lệch, thêm đúng dòng `+` vào cuối mảng `tuyen`):

```diff
diff --git a/frontend/src/tuyen.js b/frontend/src/tuyen.js
--- a/frontend/src/tuyen.js
+++ b/frontend/src/tuyen.js
@@ -11,5 +11,6 @@ export const tuyen = [
   { path: '/phe-duyet', component: PheDuyet },
   { path: '/nho', component: KyUc },
   { path: '/doi-ngu', component: DoiNgu },
   { path: '/usage', component: Usage },
+  { path: '/van-phong', component: () => import('./trang/VanPhong.vue') },   // lát 2c: nạp lười (three.js)
 ]
```

`frontend/src/KhungChinh.vue` (thêm đúng dòng `+` vào cuối `<nav class="menu">`):

```diff
diff --git a/frontend/src/KhungChinh.vue b/frontend/src/KhungChinh.vue
--- a/frontend/src/KhungChinh.vue
+++ b/frontend/src/KhungChinh.vue
@@ -16,7 +16,8 @@ onMounted(() => { taiTrangThai(); taiSoPheDuyet(); moLuong() })
       </router-link>
       <router-link to="/nho">Ký ức</router-link>
       <router-link to="/doi-ngu">Đội ngũ AI</router-link>
       <router-link to="/usage">Usage</router-link>
+      <router-link to="/van-phong">Văn phòng</router-link>
     </nav>
     <ThanhTrangThai />
   </header>
```

- [ ] **Step 4: Chạy kiểm**

Run: `cd frontend && npm run kiem`
Expected: `ℹ tests M₀ + 8` (21) · `ℹ fail 0`; `kiem-an-toan: … không có chèn HTML thô`

Run: `cd frontend && npm run build && npm run kiem-dist`
Expected: `✓ built in …` — có chunk riêng `dist/assets/VanPhong-*.js` (Vite có thể cảnh báo chunk > 500 kB — chấp nhận, G14); `kiem-dist: … không thấy mẫu eval/inline trong quét tĩnh; cần kiểm CSP runtime ở Task 8`. Build đỏ vì template (thẻ `Tres*` bị coi là component lạ, thuộc tính sai) → sửa theo thông báo, không đổi CSP. `kiem-dist` báo `eval(`/`new Function`/`WebAssembly.instantiate` trong chunk Văn phòng → **dừng**, ghi file + đoạn mã vi phạm, báo người điều phối (G1).

Run: `wc -l frontend/src/van_phong/*.vue frontend/src/trang/VanPhong.vue` → mỗi file ≤ 120.

Run: `uv run pytest -q` → `N₀ + 5` hoặc `N₀ + 7` tuỳ Task 5 đã ghép (task này không đụng Python)

- [ ] **Step 5: Commit**

```bash
git add frontend/src/van_phong/the_chu.js frontend/src/van_phong/TheChu3D.vue frontend/src/van_phong/Phong3D.vue frontend/src/van_phong/NhanVat3D.vue frontend/src/van_phong/CanhVanPhong.vue frontend/src/trang/VanPhong.vue frontend/src/tuyen.js frontend/src/KhungChinh.vue
git commit -m "feat(frontend): trang Văn phòng 3D isometric — phòng, nhân vật khối hình học pastel, biển chữ canvas, giảm chuyển động (spec 2 §5.5; plan 2c G11–G14)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 7: Frontend — bản danh sách (bàn phím / không WebGL) + địa chỉ sâu trang Công việc

**Độ khó:** `de` · **Đợt:** 3 · **Song song với:** — · **Phải xong trước:** Task 6

**Files:**
- Create: `frontend/src/van_phong/DanhSachVanPhong.vue`
- Modify: `frontend/src/trang/VanPhong.vue` (Task 6), `frontend/src/trang/CongViec.vue` (2a)

**Interfaces:**
- Consumes: `TEN_HIEN_THI`, `chuBien`, `chuBongBong`, `duongDanNhanVat`, `duongDanPhong` (Task 3); `useRoute` (vue-router).
- Produces: `DanhSachVanPhong` (props `phong`, `nhanVat`); trang Công việc nhận `?du_an=<dự án>&bead=<id>` (G9): chọn dự án theo địa chỉ, mở ngăn bên bead đó **một lần** mỗi lần địa chỉ đổi (thẻ trên bảng nếu có, ngược lại `{du_an, id}` tối thiểu — `NganBen` tự tải `/api/bead/…`).

- [ ] **Step 1: Chạy kiểm hiện tại (mốc)**

Run: `cd frontend && npm run kiem && npm run build && npm run kiem-dist` → xanh như cuối Task 6

- [ ] **Step 2: Viết component mới**

`frontend/src/van_phong/DanhSachVanPhong.vue` (mới):

```vue
<script setup>
import { computed } from 'vue'
import { TEN_HIEN_THI, chuBien, chuBongBong, duongDanNhanVat, duongDanPhong } from './hien_thi.js'

// Văn phòng dạng danh sách: đường dùng bàn phím / trình đọc màn hình, và chỗ xem khi không có WebGL (plan 2c G16).
const props = defineProps({ phong: { type: Array, required: true }, nhanVat: { type: Array, required: true } })
const TEN_SUC_KHOE = { xanh: 'Trạm ổn', vang: 'Cần để ý', do: 'Trạm lỗi' }
const LOP_SUC_KHOE = { xanh: 'nho', vang: 'canh-bao', do: 'loi' }
const theoPhong = computed(() => {
  const co = new Set(props.phong.map((p) => p.ma))
  const m = {}
  for (const n of props.nhanVat) (m[co.has(n.phong) ? n.phong : 'ca-phe'] ??= []).push(n)
  return m
})
</script>

<template>
  <section class="ds-van-phong" aria-label="Văn phòng dạng danh sách">
    <h2>Các phòng</h2>
    <div class="luoi-phong">
      <article v-for="p in phong" :key="p.ma" class="muc">
        <h3>
          <router-link v-if="duongDanPhong(p)" :to="duongDanPhong(p)">{{ chuBien(p) }}</router-link>
          <template v-else>{{ chuBien(p) }}</template>
        </h3>
        <template v-if="p.suc_khoe">
          <p :class="LOP_SUC_KHOE[p.suc_khoe.mau]">{{ TEN_SUC_KHOE[p.suc_khoe.mau] }}</p>
          <ul v-if="p.suc_khoe.ly_do.length" class="nho"><li v-for="(l, i) in p.suc_khoe.ly_do" :key="i">{{ l }}</li></ul>
        </template>
        <ul v-if="theoPhong[p.ma]">
          <li v-for="n in theoPhong[p.ma]" :key="n.khe_id">
            <router-link :to="duongDanNhanVat(n)">{{ n.ten }}</router-link> — {{ TEN_HIEN_THI[n.hien_thi] }}
            <span v-if="chuBongBong(n)" class="nho"> · {{ chuBongBong(n) }}</span>
          </li>
        </ul>
        <p v-else class="nho">Không có ai.</p>
      </article>
    </div>
  </section>
</template>

<style scoped>
.luoi-phong { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(16rem, 100%), 1fr)); gap: .75rem; }
.luoi-phong h3 { margin-top: 0; }
</style>
```

- [ ] **Step 3: Sửa trang (bản vá)**

`frontend/src/trang/VanPhong.vue`:

```diff
diff --git a/frontend/src/trang/VanPhong.vue b/frontend/src/trang/VanPhong.vue
--- a/frontend/src/trang/VanPhong.vue
+++ b/frontend/src/trang/VanPhong.vue
@@ -6,6 +6,7 @@ import { doc } from '../api.js'
 import { kho } from '../kho.js'
 import { boTriPhong, datNhanVat } from '../van_phong/bo_tri.js'
 import CanhVanPhong from '../van_phong/CanhVanPhong.vue'
+import DanhSachVanPhong from '../van_phong/DanhSachVanPhong.vue'
 import { duongDanNhanVat, duongDanPhong } from '../van_phong/hien_thi.js'
 
 // Văn phòng 3D (spec 2 §5.5). Trạng thái suy ở server (`/api/van-phong`); trang chỉ vẽ. Nhịp tim không phải sự
@@ -57,6 +58,7 @@ const di = (dich) => { if (dich) router.push(dich) }
       </TresCanvas>
     </div>
     <p v-else-if="dl" class="nho">Trình duyệt không bật WebGL — chỉ xem được dạng danh sách.</p>
+    <DanhSachVanPhong v-if="dl" :phong="dl.phong" :nhan-vat="dl.nhan_vat" />
   </section>
 </template>
 
```

`frontend/src/trang/CongViec.vue` (G18: nếu plan khác đã sửa trang này, áp tay đúng các dòng `+` cạnh dòng neo `const duAn = ref('')`, `await tai()` cuối `onMounted`, `watch([duAn, () => kho.phienBan], tai)`):

```diff
diff --git a/frontend/src/trang/CongViec.vue b/frontend/src/trang/CongViec.vue
--- a/frontend/src/trang/CongViec.vue
+++ b/frontend/src/trang/CongViec.vue
@@ -1,6 +1,7 @@
 <script setup>
 import { computed, onMounted, ref, watch } from 'vue'
+import { useRoute } from 'vue-router'
 import { doc, ghi, thanGhi } from '../api.js'
 import { ganGiaoViec } from '../giao_viec.js'
 import { kho } from '../kho.js'
 import { HANG_COT, TEN_HANG, choPhepKeo, nhomTheoHang } from '../luat.js'
@@ -7,7 +8,9 @@ import HopViSao from '../thanh/HopViSao.vue'
 import TheBead from '../thanh/TheBead.vue'
 import NganBen from './NganBen.vue'
 
-const duAn = ref('')
+const route = useRoute()
+const tuDiaChi = (x) => (typeof x === 'string' ? x : '')
+const duAn = ref(tuDiaChi(route.query.du_an))       // lát 2c: /cong-viec?du_an=<dự án>[&bead=<id>] từ Văn phòng
 const dsDuAn = ref([])
 const dsThe = ref([])
 const loiDoc = ref({})
@@ -34,8 +37,17 @@ onMounted(async () => {
     thongBao.value = e.message
   }
   await tai()
+  moTheoDiaChi()
 })
 watch([duAn, () => kho.phienBan], tai)
+watch(() => route.fullPath, async () => { duAn.value = tuDiaChi(route.query.du_an); await tai(); moTheoDiaChi() })
+
+// Mở ngăn bên đúng một lần mỗi lần địa chỉ đổi (Đại ca đóng ngăn thì lượt tải lại sau không mở lại).
+function moTheoDiaChi() {
+  const id = tuDiaChi(route.query.bead)
+  if (!id || !duAn.value) return
+  chon.value = dsThe.value.find((t) => t.du_an === duAn.value && t.id === id) ?? { du_an: duAn.value, id }
+}
 
 function tha(hang) {
   if (choPhepKeo(dangKeo.value, hang)) keoCho.value = { the: dangKeo.value, cot: hang }
```

- [ ] **Step 4: Chạy kiểm**

Run: `cd frontend && npm run kiem && npm run build && npm run kiem-dist`
Expected: `ℹ tests M₀ + 8` (21) · `ℹ fail 0`; `✓ built`; `kiem-dist` xanh. `wc -l frontend/src/trang/CongViec.vue` ≤ 120 (bản dựng thử: 97).

Run: `uv run pytest -q` → `N₀ + 7 passed` (1066)

- [ ] **Step 5: Commit**

```bash
git add frontend/src/van_phong/DanhSachVanPhong.vue frontend/src/trang/VanPhong.vue frontend/src/trang/CongViec.vue
git commit -m "feat(frontend): Văn phòng dạng danh sách cho bàn phím/không WebGL; Công việc nhận ?du_an=&bead= (spec 2 §5.5; plan 2c G9, G16)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 8: Kiểm chạy thật trên trình duyệt cục bộ — CSP thật của tram-api, bấm, giảm chuyển động

**Độ khó:** `de` · **Đợt:** 4 · **Phải xong trước:** Task 5, 6, 7 · **Người làm:** người điều phối (cần trình duyệt — khung Browser của Claude hoặc Chrome trên máy B), trên worktree của task, chỉ `127.0.0.1`.

**Files:**
- Create: `tests/chay_thu_van_phong.py` (máy chủ dữ liệu giả — CHỈ DÙNG KHI KIỂM; không phải test pytest)

**Interfaces:**
- Consumes: `tao_app` (2a), `tao_pt`, `BdGia`, `bead`, `dat_phieu`, `dang_ky_khe`, `bat_tat_khe`, `ngat_cau_dao`, `ghi_nhip`, `KhoPhieu`.
- Produces: `uv run python tests/chay_thu_van_phong.py [cong]` — tram-api thật (CSP + Host 421 của 2a) phục vụ `frontend/dist` với sáu khe giả đủ năm hàng §5.5 (Làm, Rảnh, Cần người, Lỗi — cầu dao, Tắt, Mất kết nối), hai dự án, một bead chờ review.

- [ ] **Step 1: Viết script**

`tests/chay_thu_van_phong.py` (mới):

```python
"""Chạy tram-api với dữ liệu GIẢ để kiểm tay trang Văn phòng trên trình duyệt (plan 2c Task 8) — CHỈ DÙNG KHI KIỂM.

`uv run python tests/chay_thu_van_phong.py [cong]` (mặc định 7799) sau `cd frontend && npm run build`. Mọi dữ liệu nằm
trong thư mục tạm (TRAM_HOME, su-kien.db); `bd` là `BdGia`; không gọi mạng, không đụng ~/.tram hay beads thật.
Không phải test pytest (tên file không bắt đầu bằng `test_`)."""
import os
import sys
import tempfile
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

TAM = Path(tempfile.mkdtemp(prefix="tram-van-phong-"))
os.environ["TRAM_HOME"] = str(TAM / "tram-home")

import uvicorn  # noqa: E402

from api_gia import tao_pt  # noqa: E402
from bd_gia import BdGia  # noqa: E402
from bead_gia import bead  # noqa: E402
from kho_phieu_gia import dat_phieu  # noqa: E402
from tram.api.app import tao_app  # noqa: E402
from tram.phieu.cau_dao import ngat_cau_dao  # noqa: E402
from tram.phieu.khe import bat_tat_khe, dang_ky_khe  # noqa: E402
from tram.phieu.kho import KhoPhieu  # noqa: E402
from tram.phieu.nhip_tim import ghi_nhip  # noqa: E402

LUC = datetime.now(timezone.utc).replace(microsecond=0)
KHE = [("claude-1", "claude"), ("claude-2", "claude"), ("codex-1", "codex"), ("claude-3", "claude"),
       ("codex-2", "codex"), ("claude-4", "claude")]


def gieo(db: Path) -> None:
    kho = KhoPhieu(db)
    with kho.giao_dich():
        dang_ky_khe(kho, "B", [{"ten": t, "cli": c, "ten_goi_nho": t, "vai_uu_tien": ["coder"]} for t, c in KHE], luc=LUC)
        for t, _ in KHE:
            if t != "codex-2":                                            # codex-2: mất kết nối
                ghi_nhip(kho, f"B/{t}", luc=LUC, giao_id=None, luot=None, buoc_tho="ranh", han_muc=None)
        bat_tat_khe(kho, "B/claude-3", bat=False, vi_sao="để dành", tac_nhan="dai-ca", luc=LUC)
        ngat_cau_dao(kho, "B/claude-4", ly_do="het-han-muc", toi_luc=LUC + timedelta(hours=2), luc=LUC)
    dat_phieu(kho, "B/claude-1", luc=LUC, bead_id="hr-1", tieu_de="Sửa cắt UTF-8 tóm tắt hoàn tiền")
    p = dat_phieu(kho, "B/codex-1", luc=LUC, bead_id="hr-3", tieu_de="Chọn cách tính thuế", buoc="qc")
    with kho.giao_dich():
        kho.ghi_su_kien("hr-codex", "bao.can_hoi", {"giao_id": p.giao_id}, luc=LUC, bead_id="hr-3")
    kho.close()


def main() -> None:
    cong = int(sys.argv[1]) if len(sys.argv) > 1 else 7799
    dist = Path(__file__).resolve().parents[1] / "frontend" / "dist"
    bds = {"hr-codex": BdGia([bead("hr-1", title="Sửa cắt UTF-8", labels=["cot:ai-lam"]),
                              bead("hr-2", title="Xem lại hoá đơn", labels=["cot:cho-review"]),
                              bead("hr-3", title="Chọn cách tính thuế", labels=["cot:can-chot"])]),
           "tram": BdGia([])}
    gieo(TAM / "sk.db")
    pt = replace(tao_pt(TAM, bds, thu_muc_tinh=dist), mo_kho_phieu=lambda: KhoPhieu(TAM / "sk.db"),
                 dong_ho=lambda: LUC)
    print(f"Dữ liệu giả ở {TAM} — mở http://127.0.0.1:{cong}/#/van-phong (Ctrl+C để dừng)")
    uvicorn.run(tao_app(pt, cong=cong), host="127.0.0.1", port=cong, server_header=False, log_level="warning")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Build và chạy**

```bash
(cd frontend && npm run build && npm run kiem-dist)
uv run pytest -q                                         # N₀ + 7 — script không bị pytest thu (tên không bắt đầu bằng test_)
uv run python tests/chay_thu_van_phong.py 7799           # chạy nền; dừng bằng Ctrl+C (hoặc kill tiến trình) ở Step 5
curl -s -D - -o /dev/null http://127.0.0.1:7799/ | grep -i content-security-policy   # đúng chuỗi CSP của spec §4 mục 6
```

- [ ] **Step 3: Kiểm trên trình duyệt** (mở `http://127.0.0.1:7799/#/van-phong`; ghi kết quả từng dòng vào mô tả commit)

1. Console **không** có dòng nào chứa `Content Security Policy`, `Refused to`, `unsafe-eval`, `WebAssembly`; không lỗi JS.
2. Tab mạng: mọi yêu cầu chỉ tới `http://127.0.0.1:7799` (không CDN, không font, không `raw.githubusercontent.com`); `VanPhong-*.js` chỉ tải khi mở trang Văn phòng (mở `#/cong-viec` trước, xem mạng, rồi mới vào Văn phòng).
3. Cảnh 3D: thấy 6 phòng góc isometric (camera trực giao — đường song song không hội tụ); biển tên đọc được; Claude 1 ngồi bàn ở phòng `hr-codex` có bong bóng "Sửa cắt UTF-8 tóm tắt h… · code"; Codex 1 giơ tay + chấm đỏ, bong bóng "… · QC"; Claude 4 màn hình đỏ; Claude 3 và Codex 2 mờ, ngồi yên; Claude 2 đứng ở Góc cà phê; tủ máy ở Phòng máy chủ màu **vàng**; Phòng giám đốc có chấm đỏ, biển "2 việc chờ"; đèn Điều phối xám. Kéo đổi cỡ cửa sổ → hình không méo (G13).
4. Bấm nhân vật Claude 1 → địa chỉ thành `#/cong-viec?du_an=hr-codex&bead=hr-1`, ô Dự án = `hr-codex`, ngăn bên mở `hr-1`; đóng ngăn → không tự mở lại. Bấm sàn phòng `tram` → `#/cong-viec?du_an=tram`. Bấm Phòng giám đốc → `#/phe-duyet`.
5. Bật ô "Giảm chuyển động" → cảnh đứng yên (không nhún/vẫy); tắt → chuyển động lại. Giả lập `prefers-reduced-motion: reduce` (DevTools → Rendering) rồi tải lại → ô được tích sẵn.
6. Bản danh sách dưới canvas: Tab đi qua được mọi link; link "Codex 1" mở `#/cong-viec?du_an=hr-codex&bead=hr-3`.
7. `document.querySelectorAll('style').length` trong console = 0 (CSS chỉ từ file `.css`).

Bất kỳ mục 1–2 nào hỏng → **dừng**, không nới CSP; ghi lỗi + file gây ra, báo người điều phối/Đại ca (G1). Mục 3 lệch (camera, vị trí, màu) → sửa trong file của Task 6 bằng một commit riêng của task này, chạy lại Step 2–3.

- [ ] **Step 4: Dừng máy chủ, dọn**

```bash
pkill -f "tests/chay_thu_van_phong.py" || true; sleep 1; pgrep -fl chay_thu_van_phong || echo "đã dừng"
```

(Máy chủ giữ được SIGTERM vài giây; còn chạy thì `pkill -9 -f …`.) Thư mục tạm `tram-van-phong-*` in ra ở dòng đầu có thể xoá.

- [ ] **Step 5: Commit**

```bash
git add tests/chay_thu_van_phong.py
git commit -m "test(van-phong): máy chủ dữ liệu giả + kiểm chạy trang Văn phòng dưới CSP thật (spec 2 §4 mục 6, §9 mục 4; plan 2c G1, G13)" -m "<kết quả 7 mục Step 3>" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

## Sơ đồ đợt chạy

Số test là kết quả chạy thật trên bản dựng thử (Tự review mục 4), N₀ = 1059, M₀ = 13. Ngoặc sau tên task: task phải ghép trước.

```
Đợt 0 — main (sau mọi plan trước) → N₀ passed · node M₀

Đợt 1 — song song, 4 worktree từ main
  T1 nhân vật (py) · T2 phòng + sức khoẻ (py) · T3 luật bố trí/hiển thị (js) · T4 TresJS + three + kiem-dist (js, cần mạng)
  → N₀ + 5 = 1064 passed · node M₀ + 8 = 21 · build + kiem-dist xanh

Đợt 2 — song song, 2 worktree từ main sau đợt 1
  T5 API /api/van-phong (1, 2) · T6 cảnh 3D + trang (3, 4)
  → N₀ + 7 = 1066 passed · node 21 · build + kiem-dist xanh (có chunk VanPhong)

Đợt 3 — 1 worktree
  T7 danh sách + địa chỉ sâu Công việc (6) → N₀ + 7 · node 21

Đợt 4 — người điều phối
  T8 kiểm chạy trên trình duyệt dưới CSP thật (5, 6, 7) → N₀ + 7 · node 21
```

| Task | Độ khó | Đợt | Phải xong trước | File chạm (ngoài test) | Test mới | Toàn bộ sau task (trên main đợt trước) |
|---|---|---|---|---|---|---|
| 1 | de | 1 | — | `tram/suy/nhan_vat.py` | 3 | N₀ + 3 (1062) |
| 2 | de | 1 | — | `tram/suy/van_phong.py` | 2 | N₀ + 2 (1061) |
| 3 | de | 1 | — | `frontend/src/van_phong/bo_tri.js`, `hien_thi.js` | 5 (node) | node M₀ + 5 (18) |
| 4 | de | 1 | — | `frontend/package.json`, `package-lock.json`, `vite.config.js`, `kiem-dist.mjs` | 3 (node) | node M₀ + 3 (16) |
| 5 | de | 2 | 1, 2 | `tram/api/van_phong.py`, `tram/api/app.py` | 2 | N₀ + 7 (1066) |
| 6 | kho | 2 | 3, 4 | `frontend/src/van_phong/the_chu.js`, `TheChu3D.vue`, `Phong3D.vue`, `NhanVat3D.vue`, `CanhVanPhong.vue`, `src/trang/VanPhong.vue`; sửa `tuyen.js`, `KhungChinh.vue` | — (build) | node 21 |
| 7 | de | 3 | 6 | `frontend/src/van_phong/DanhSachVanPhong.vue`; sửa `trang/VanPhong.vue`, `trang/CongViec.vue` | — (build) | node 21 |
| 8 | de | 4 | 5, 6, 7 | `tests/chay_thu_van_phong.py` | — (kiểm tay) | N₀ + 7 · node 21 |

**Tổng cuối:** `uv run pytest -q` = **N₀ + 7**; `npm run kiem` = **M₀ + 8**; `npm run build` + `npm run kiem-dist` xanh; Task 8 bảy mục đạt.

Không file nào bị hai task cùng đợt sửa. **Đụng chung với plan khác (G18):** `tram/api/app.py` (2a, 3a-1, 2b, 1b-3 và có thể 3a-2/4a-2/4b — chỉ thêm một import + một router); `frontend/src/tuyen.js`, `KhungChinh.vue` (2a, 1b-3, 2b — thêm một route + một link); `frontend/src/trang/CongViec.vue` (2a; plan đợt 3 có thể sửa — 4a-1 "Để sau" ghi "lý do không giao ở cột 1" cho lát dashboard sau); `frontend/package.json`, `package-lock.json`, `vite.config.js` (2a — 2c là plan duy nhất thêm gói npm). Đọc (không sửa): `tram/api/tuyen_doc.py` (`phe_duyet` — G6), `tram/phieu/trang_thai.py`, `tram/chu/estop.py`, `frontend/src/kho.js`, `NganBen.vue`.

## Để sau (chờ cổng / chờ chạy thật) — không lập task code ở plan này

Không đánh dấu lát 2c sẵn sàng triển khai cho tới khi các mục "chờ chạy thật" dưới đây đã làm.

| Phần | Spec | Chờ | Đã chừa sẵn |
|---|---|---|---|
| Nguồn tín hiệu "phiên điều phối trên máy A" để đèn Điều phối sáng | §5.5 | **Đại ca chọn nguồn** ("Cần sửa spec sau") — rồi một task nhỏ: sinh sự kiện ở bên chọn + đọc trong `cac_phong` | `sang: true\|false\|null`; `chuBien`, đèn `Phong3D` đã xử lý cả ba giá trị |
| Kiểm tay trên máy A (trình duyệt) và điện thoại qua tailnet: tốc độ khung hình, cảm ứng bấm nhân vật, chữ đọc được trên màn nhỏ, pin | §9 mục 3–4 | **#5** (Tailscale chưa duyệt) | Task 8 đã kiểm trên `127.0.0.1`; danh sách thay thế cho màn nhỏ |
| Dữ liệu khe thật (nhịp tim, phiếu, escalation thật) trong văn phòng | §5.5 | 3a-2 (thợ thật, S1–S6), 4a-2 (giao việc thật), 3b (máy từ xa) | đọc đúng `trang_thai_khe`, `escalation.*` như các plan đó định nghĩa (G17) |
| Trang Đội ngũ AI (2b) hiện "Cần Đại ca" cho khe có escalation mở như Văn phòng | spec 3 §10.1 | Đại ca chốt ("Cần sửa spec sau") | `tram/suy/nhan_vat.py::_escalation_mo` dùng lại được |
| Hiệu năng khi nhiều dự án/khe (> 12 phòng, > 20 nhân vật): `InstancedMesh`, giảm `dpr` | — | có số liệu thật | `CANH`, `boTriPhong` gom bố trí một chỗ |

> **Ghi chú 15/10/2026** (không đổi bảng trên): Tailscale máy B đã đăng nhập, và gói `@tresjs/core@5.9.1`, `three@0.186.1` đã được cho tải. Hàng "Kiểm tay ... qua tailnet" giờ chờ 2a Task 26 (`vn.tram.api` chưa cài, `tailscale serve` chưa làm), không chờ #5 nữa; bead `bs-8eh.16`. Hàng "Dữ liệu khe thật" vẫn chờ S1–S6, các spike này **chưa duyệt**. Xem [quyết định 13/10, mục "Ghi chú 15/10"](../quyet-dinh/2026-10-13-tra-loi-cau-hoi-gop.md).

## Tự review

**1. Độ phủ spec (phần của lát 2c)**

| Yêu cầu | Task | Kiểm bằng |
|---|---|---|
| §5.5 mỗi dự án đã `them` là một phòng, tên dự án trên biển | 2, 3, 6 | `test_cac_phong_co_dinh_truoc_roi_du_an`; node `bố trí phòng…`, `chữ biển…`; Task 8 mục 3 |
| §5.5 phòng cố định Điều phối / Góc cà phê / Phòng máy chủ (xanh/vàng/đỏ) / Phòng giám đốc (badge) | 2, 5, 6 | `test_suc_khoe_xanh_vang_do`, `test_van_phong_phong_nhan_vat_va_badge` (badge = route Phê duyệt), `test_van_phong_khi_kho_phieu_tat_va_tram_loi` (đỏ); Điều phối: lệch chữ G4 |
| §5.5 nhân vật = khe, tên theo CLI + số khe | 1, 6 | `test_ten_nhan_vat_theo_cli_va_so_khe_trung_thi_them_may` |
| §5.5 bảng năm trạng thái từ nhịp tim + sự kiện (Làm / Rảnh / Cần người / Lỗi / Tắt-mất kết nối) + cách hiển thị | 1, 3, 6 | `test_phong_va_hien_thi_theo_trang_thai`, `test_escalation_mo_cua_phieu_cuoi_thanh_can_nguoi_toi_khi_dong`; node `tư thế theo năm hàng`; Task 8 mục 3 |
| §5.5 bong bóng = tiêu đề bead + bước (spec/code/QC) | 1, 3, 6 | `bead.tieu_de` đã `lam_sach` (bidi bị lọc) trong test Task 1; node `chuBongBong` |
| §5.5 bấm nhân vật → mở bead; bấm phòng → lọc Công việc | 3, 6, 7 | node `đường dẫn khi bấm`; Task 8 mục 4, 6 (đã thử trên bản dựng thử với link danh sách) |
| §5.5 hình tự dựng bằng khối hình học + pastel, không asset giấy phép mập mờ | 6 | chỉ `Box/Cylinder/SphereGeometry`, `MAU`; chữ vẽ canvas, font hệ thống; Global Constraints cấm loader/asset |
| §5.5 chế độ giảm chuyển động | 6 | `prefers-reduced-motion` + ô bật/tắt; Task 8 mục 5 |
| §4 mục 4, 6: CSP chặt, không `unsafe-eval`, không chèn HTML | 4, 6, 8 | G1 quét tĩnh upstream; `kiem-dist` (3 test node); `kiem-an-toan`; Task 8 mục 1, 2, 7; CSP header trong `test_van_phong_phong_nhan_vat_va_badge` |
| §5.4 không hiện email | 1, 5 | `"@" not in str(nv)`, `"a@b.vn" not in r.body` |
| §7 `GET /api/van-phong` | 5 | `test_api_van_phong.py` (2) |
| §8 TresJS + three, khoá phiên bản chính xác | 4 | `npm install --save-exact …@5.9.1 …@0.186.1`; G2 |
| §2 D2 (≤ 10 s không tải lại), D6 (2a ≤ 2 s) | 6 | SSE `phienBan`/`phienBanDoiNgu` + tải lại 5 s (G15); route nạp lười + `kiemGoiChinh` (G14) |
| §9 mục 1 unit test trạng thái nhân vật từ sự kiện giả | 1 | test Task 1 |

**2. Quét placeholder:** không "TBD/TODO/tương tự Task N"; mọi file mới có nguyên văn; file có sẵn có bản vá; mọi lệnh có kết quả mong đợi. `<model đang thực thi>`, `<danh sách gói bắc cầu…>`, `<kết quả 7 mục…>` trong lệnh commit là chỗ người thực thi điền số liệu thật — cố ý. "Chờ #5 / chờ 3a-2 / Đại ca chọn nguồn" là cổng có chủ đích, có mục "Để sau".

**3. Khớp chữ ký:** `nhan_vat(kho, ds, cac_du_an)`, `HIEN_THI`, khoá `{khe_id, ten, cli, trang_thai, hien_thi, phong, bead}` (1) ↔ `suc_khoe(nhan_vat=…)` chỉ đọc `khe_id`, `trang_thai` (2) ↔ route (5) ↔ "Hợp đồng JSON" ↔ `datNhanVat` (`khe_id`, `phong`), `tuThe(hien_thi)`, `chuBongBong` (`bead.tieu_de`, `bead.buoc`), `duongDanNhanVat` (`bead.du_an`, `bead.bead_id`) (3) ↔ `NhanVat3D`, `DanhSachVanPhong` (6, 7). Mã phòng `"du-an:<t>"` sinh ở hai nơi — `ma_phong_du_an` (1) và `cac_phong` (2) — test API Task 5 khẳng định `nv["phong"] == "du-an:hr-codex"` có trong `phong`. `cac_phong(…, so_cho, suc_khoe)` (2) ↔ `chuBien` (`so_cho`, `sang`), `Phong3D` (`suc_khoe.mau`, `sang`, `so_cho`) ↔ `MAU.suc_khoe` (3). `boTriPhong` → `{x, z}` ↔ `Phong3D` (`p.x`, `p.z`), `khungNhin` ↔ `CanhVanPhong`. `taoTheChu → {tex, tiLe}` ↔ `TheChu3D`. Địa chỉ `?du_an=&bead=` (`duongDanNhanVat`, 3) ↔ `CongViec.vue` (7).

**4. Đã chạy thử (13/10):** dựng bản sao trong scratchpad (không đụng repo thật, không gọi Claude/Codex/mạng ngoài, không Keychain, không `~/.tram` thật): bản dựng thử của plan 2b = main `891ae04` (720) + mã 3a-1 dựng lại nguyên văn từ plan (295) + mã 2b (44) → **1059 passed**, node **13**. Chạy nguyên văn mã + test của plan này: Task 1, 2, 5 → **1066 passed** (+3, +2, +2; thông báo fail ở Step 2 là kết quả thật); Task 3, 4 → node **21** (+5, +3); `kiem-an-toan` xanh; `kiem-dist` chạy trên bundle 2b và trên bundle có trang Văn phòng → xanh, Văn phòng tách chunk riêng. **Chưa chạy với TresJS/three thật** — quy ước đợt 3 không cho cài gói: (a) mọi `.vue` của Task 6–7 đã biên dịch thử bằng `@vue/compiler-sfc` của repo với đúng `isCustomElement` của `@tresjs/core@5.9.1` (`dist/template-compiler-options.mjs`): không lỗi, không thẻ `Tres*` nào bị coi là component; (b) `vite build` thử với **bản giả** `@tresjs/core`/`three` (alias, chỉ trong scratchpad) → build xanh, chunk `VanPhong-*.js` riêng, `kiem-dist` xanh; (c) chạy `tests/chay_thu_van_phong.py` (tram-api thật, CSP thật) + khung Browser: `/api/van-phong` đúng hợp đồng, bản danh sách đủ 6 phòng / 6 nhân vật / năm hàng, link "Codex 1" mở `#/cong-viec?du_an=hr-codex&bead=hr-3` với ô Dự án đúng và ngăn bên `hr-3` mở; console không lỗi, mọi yêu cầu chỉ tới `127.0.0.1`. Phần cảnh 3D thật (camera trực giao, sự kiện bấm của TresJS, `useLoop`, texture chữ) **chỉ kiểm được ở Task 8**. API TresJS dùng trong plan đối chiếu với mã nguồn `dist/tres.js` 5.9.1: `TresCanvas` (props `clearColor`, `renderMode`, `dpr`), `useTres().sizes.aspectRatio`, `useLoop().onBeforeRender` (tự gỡ khi component huỷ — `tryOnScopeDispose`), camera đầu tiên trong cảnh thay camera mặc định, patch prop gọi `updateProjectionMatrix` cho camera và `invalidate` ở chế độ on-demand.

**5. Rủi ro còn lại (Đại ca biết):** (a) Task 6 có thể phải chỉnh nhỏ khi gặp TresJS thật (tên sự kiện, camera trực giao) — gói gọn trong `src/van_phong/*.vue`, có Task 8 bắt; (b) chunk Văn phòng ~0,7 MB — chậm lần đầu mở trang trên điện thoại (không ảnh hưởng các trang khác); (c) đèn Điều phối luôn xám tới khi có nguồn (G4); (d) Văn phòng hiện "Cần người" cho khe có escalation mở trong khi Đội ngũ AI hiện "Rảnh" (G3); (e) TresJS kéo `@vue/devtools-kit` vào bundle (G2) — không chạy khi không mở Vue Devtools; (f) bản vá có thể không áp thẳng vì 1b-3 và plan đợt 3 sửa cùng file (G18).

## Cần sửa spec sau

- **Spec 2 §7** (bảng API): `GET /api/van-phong` — dạng JSON như "Hợp đồng JSON" (G8); trang Công việc nhận `#/cong-viec?du_an=&bead=` (G9).
- **Spec 2 §5.5:** (1) "Điều phối sáng đèn khi có phiên điều phối" chưa có nguồn — Đại ca chọn: sự kiện do skill/hook phiên điều phối trên máy A gửi (cần đường ghi riêng có xác thực — không dùng Bearer thợ, không dùng header Tailscale giả được), hay coi lời gọi MCP phiên tay (1b-2) là tín hiệu (memory ghi `nho.phien_tay {du_an}` tối đa 1 lần/phút); tới lúc đó đèn xám "chưa có tín hiệu" (G4). (2) Ghi rõ hàng "Tắt / mất kết nối" gộp `tat` + `mat_ket_noi`; "Lỗi" gồm cầu dao ngắt (theo spec 3 §10.1). (3) Ghi chỗ ngồi của nhân vật Lỗi/Tắt (bàn của phiếu cuối — G7) và đích của phòng cố định khi bấm (G9). (4) Thêm "bản danh sách cho bàn phím / không WebGL" (G16).
- **Spec 2 §8:** ghi phiên bản đã chốt `@tresjs/core 5.9.1`, `three 0.186.1` và danh sách gói bắc cầu (G2); cấm loader nén cần WebAssembly (G1).
- **Spec 3 §10.1:** "escalation liên kết chưa đóng" → `can_nguoi` hiện chỉ có ở lớp hiển thị của 2c; `trang_thai_khe` (3a-1) không tính vì bộ giao việc 4a-1 dựa vào `ranh`. Đại ca chọn: giữ như vậy (ghi rõ), hay thêm trường riêng `can_nguoi_hien_thi` vào `TrangThaiKhe` để 2b dùng chung (G3).
- **Spec 2 §4 mục 6:** thêm "cổng `kiem-dist` sau mỗi build" vào danh sách kiểm CSP (G1).

## Ghi chú triển khai (code 14–15/10/2026)

- **Kết quả:** code xong Task 1–7, Task 8 do Em kiểm trực tiếp trên khung Browser.
  - Python thêm **7 test**, khớp kỳ vọng (N₀ + 7). Node thêm **8 test**: Task 3 thêm 5, Task 4 thêm 3, frontend lên 33/33. Build, `kiem-dist` đều xanh.
  - Trang Văn phòng tách thành chunk riêng `VanPhong-*.js`, khoảng 864 kB (gzip 231 kB). Cảnh báo chunk lớn đã được chấp nhận theo G14.
- **Gói npm:** Đại ca cho tải ngày 15/10 `@tresjs/core` 5.9.1 và `three` 0.186.1, cài bằng `--save-exact --ignore-scripts`. Có thêm 8 gói, khớp G2: `@vueuse/core|shared|metadata` 14.4.0, `@pmndrs/pointer-events` 6.6.32, `radashi` 12.9.6, `@types/web-bluetooth` 0.0.21. `npm audit` báo 0 lỗ hổng.
  - `npm audit --omit=dev` không chạy riêng vì cần mạng. Thay vào đó dùng kết quả audit đi kèm lệnh cài, đã quét đủ 87 gói.
- **Lệch plan:**
  1. **Task 8 tìm ra lỗi camera** (sửa trong file Task 6 bằng commit riêng, đúng như Step 3 cho phép). TresJS 5.9.1 chỉ gọi `lookAt(0,0,0)` một lần lúc tạo camera, khi vị trí chưa được đặt. Vì vậy camera ở `[40,40,40]` nhìn theo trục −z và canvas trống. Đã thêm `:look-at="[0, 0, 0]"`. Quét tĩnh và test node không bắt được lỗi này, chỉ lộ ra khi chạy trên trình duyệt.
  2. **Task 5:** áp tay `app.py` theo G18. Dùng `CAC_TUYEN += (van_phong.router,)` thay cho sửa tuple, kết quả vẫn là router nằm cuối danh sách.
- **Kết quả kiểm Task 8:** 7 mục đều đạt. Chi tiết nằm trong thân commit `test(van-phong): …`.
  - Còn một điểm tinh chỉnh chưa xử lý: ở cỡ khung khoảng 975×536, biển chữ và bong bóng rất nhỏ, khó đọc. Có thể thu nhỏ khung nhìn (`khungNhin`) hoặc phóng to biển chữ.
  - `prefers-reduced-motion` chưa giả lập được trong khung Browser, mới đối chiếu qua mã.
- **Ghi chú cho kiểm tay sau này:** pointer-events dò điểm bấm theo vị trí của lần di chuột trước. Người dùng thật luôn rê chuột tới trước khi bấm nên không bị ảnh hưởng. Công cụ tự động thì phải `hover` trước rồi mới `click`.
