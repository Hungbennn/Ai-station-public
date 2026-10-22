# Lát 2e — Đèn Điều phối: hook phiên điều phối máy A — Implementation Plan

> **Bản 15/10/2026, sửa theo D24, D33 và review Codex đợt 4.** Mã xác thực của hook là **mã điều phối riêng** (D24), không còn dùng mã Đại ca. Bản sửa F10 (gộp nguyên tử) và F11 (đọc theo hạn sống) của Codex đã gộp vào Task 1, Task 2, có mã và test nguyên văn. F14 (hạn của cả hook) đã gộp vào Task 3. Phần Vue của đèn chuyển sang **lát 2f** (làm lại giao diện theo mockup đã duyệt D20, D33). 2e chỉ giữ dữ liệu `sang`/`nhip_cuoi` và luật hiển thị JS thuần (`chuNhip`, màu đèn vàng ấm `#f2c14e` theo D38), khớp bảng đối chiếu §1.11 của khảo sát giao diện. Mốc: `main` `38a016f`, N₀ = 1994. Mọi khối mã đã chạy thử trên bản sao `main` (mục "Tự review" phần 4). **Còn chờ:** C2–C6 ở mục "Chờ Đại ca chốt"; cổng chạy thật của Task 5.

> **For agentic workers:** REQUIRED SUB-SKILL: Use ai-skills:subagent-driven-development (recommended) or ai-skills:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Đèn phòng **Điều phối** trên Văn phòng 3D (spec 2 §5.5) sáng khi máy A đang có phiên Claude Code điều phối, xám khi phiên đã đóng hoặc lâu không có nhịp. Tín hiệu lấy từ hook của phiên trên máy A, gửi về trạm qua một đường ghi riêng có xác thực (quyết định **D12**, bead `bs-urj.7`). Đường ghi dùng **mã điều phối** riêng (quyết định **D24**). Hiện API trả `sang: null` cố định (`tram/suy/van_phong.py::cac_phong`, plan 2c G4).

**Architecture:** Không thêm kho trạng thái; đèn suy lúc đọc từ nhật ký sự kiện (Q12).
- **Phía trạm — mã điều phối.** Module mới `tram/chu/ma_dieu_phoi.py`: trạm chỉ giữ sha256 của mã ở khoá `dieu_phoi_ma_sha256` trong `~/.tram/cau-hinh.yaml`. Lệnh `tram chu dat-ma-dieu-phoi` hỏi ẩn bằng `getpass` hai lần, không nhận mã qua argv, từ chối mã trùng mã Đại ca. Memory service vẫn chỉ so với `ma_dai_ca_sha256`, nên mã điều phối không đọc được memory.
- **Phía trạm — ghi.** Route mới `POST /api/dieu-phoi/nhip` (`tram/api/dieu_phoi.py`). Kiểm lần lượt: kênh ghi `cach_ly.kenh_ghi` (G29 của 3a-2) → giới hạn tần suất → **đúng bộ kiểm của API ghi dashboard** `yeu_cau_ghi` (danh tính Tailscale, `X-Tram`, `Origin`) → **mã điều phối** (`Authorization: Bearer`, so sha256 với `dieu_phoi_ma_sha256`) → thân ≤ 512 byte, đúng lược đồ. Hợp lệ thì ghi sự kiện `dieu_phoi.nhip {su_kien, phien}` vào dự án `_tram`, gộp tối đa 1 nhịp/phút/phiên. Đọc, quyết và ghi nằm trong một giao dịch `BEGIN IMMEDIATE` (F10). Route chỉ ghi đúng loại sự kiện đó.
- **Phía trạm — suy.** Module thuần `tram/suy/dieu_phoi.py`: `den_dieu_phoi(nhip, bay_gio)` → `{sang, nhip_cuoi}` với hạn sống 15 phút; `can_ghi` quyết gộp. Adapter `tram/suy/kho_nhip.py::doc_nhip` đọc **mọi** nhịp trong hạn sống, không cắt theo số dòng (F11). `GET /api/van-phong` dùng nó để truyền vào `cac_phong`. Không đụng `app.py`: router mới được gắn vào router `van_phong` có sẵn.
- **Máy A.** Script `may-a/hook-dieu-phoi/hook_dieu_phoi.py` (python3 ≥ 3.9, thư viện chuẩn, như skill `xem-spec-cho-duyet`), kèm `settings.mau.json` và `HUONG-DAN.md`. Script chỉ gửi tên sự kiện hook và 16 hex băm của `session_id`. Mã lấy từ Keychain máy A, mục `tram-dieu-phoi-ma`. Timeout mỗi thao tác 2 giây, cả hook tối đa 4 giây (F14). Lỗi gì cũng im lặng, luôn thoát 0. Đại ca tự cài.
- **Frontend.** 2e chỉ sửa luật thuần `frontend/src/van_phong/hien_thi.js`: thêm `chuNhip(p)` (dòng "nhịp cuối <giờ VN>") và đổi `MAU.den` sang vàng ấm `#f2c14e` (D38), kèm test node `dieu_phoi.test.mjs`. **Không sửa component `.vue` nào.** Giao diện hiện có (2c) đã đọc `sang` và `MAU.den`, nên đèn 3D đổi màu, chữ biển đổi theo ba trạng thái ngay khi backend 2e chạy. Dòng "nhịp cuối", biển phòng, danh sách và khung chi tiết theo mockup mới do **lát 2f** làm (mục "Ranh giới 2e / 2f").

**Tech Stack:** Python 3.12 (`uv`), FastAPI 0.143.0, pydantic 2, SQLite stdlib, `pytest`; script máy A: python3 ≥ 3.9 thư viện chuẩn (`urllib`, `hashlib`, `subprocess`, `threading`); Vue 3.5.43, Vite 8.3.4, `node:test`. **Không thêm phụ thuộc nào**, cả Python lẫn npm.

**Spec:**
- [Spec 2](../specs/2026-10-12-phan-2-dashboard.md) (ĐÃ DUYỆT): §5.5 (phòng Điều phối "sáng đèn khi có phiên điều phối"); §4 mục 1–3, 2b, 6 (chỉ nghe 127.0.0.1, danh tính Tailscale, cách ly kênh ghi, CSRF, CSP, Host 421); §7; §12.2 (sự kiện hệ dùng `_tram`); §14 (đề xuất 2c: chưa có producer → `sang: null`); "Trạng thái triển khai (15/10/2026)", dòng "§5.5 Đèn Điều phối".
- [Kiến trúc](../specs/2026-10-12-tram-dieu-phoi-kien-truc.md): §4.1 (máy A = Điều phối, Tailscale, không cài `tram-tho`), Q9 (máy thợ là thiết bị gắn tag, không mang danh tính Đại ca), Q15 (cài đặt minh bạch).
- [Spec 1b](../specs/2026-10-13-phan-1b-memory.md) §9.3: mã Đại ca (Keychain máy A, trạm giữ sha256). 2e **không** đổi phạm vi mã này (D24).
- [Quyết định 15/10 đợt 4](../quyet-dinh/2026-10-15-chot-dot-4.md): **D12** (nguồn đèn = hook phiên điều phối máy A), **D6** (Tailscale máy A chưa có), **D24** (mã riêng `tram-dieu-phoi-ma`, trạm giữ băm, không mở rộng mã Đại ca), **D20**, **D33** (mockup giao diện đã duyệt, chuẩn cho lát 2f), **D38** (ghép 2d/2e nguyên văn trước rồi 2f làm lại `.vue`; đèn Điều phối vàng ấm `#f2c14e`).
- [Khảo sát giao diện cho 2f](../handovers/2026-10-15-khao-sat-giao-dien.md): §1.11 (đối chiếu 2e ↔ 2f: T1–T3, T5 ở 2e; `chuNhip` giữ ở 2e, `.vue` do 2f làm lại; Cài đặt hiện băm mã điều phối có/chưa), §2.2 (2f giữ `hien_thi.js`, đổi `MAU` sang bảng màu mockup), §3.5 Q18.
- [Mockup đã duyệt](../mockup/2026-10-15-giao-dien/): `van-phong.js` (biển phòng Điều phối: chấm đèn + chữ trạng thái), `trang-van-phong.js` (danh sách: chip "đèn: …"; khung chi tiết), `trang-tong-quan.js` (Tổng quan: **không** có ô đèn Điều phối).
- Đọc kèm các plan: [2a](2026-10-13-lat-2a-dashboard.md) (`bao_mat.py`, Task 26 chạy thật); [2c](2026-10-13-lat-2c-van-phong-3d.md) (G4, G18, "Ghi chú triển khai"); [1b-2](2026-10-13-lat-1b-2-mcp-nho.md) (Task 3 `ma_dai_ca.py` — khuôn của lệnh đặt mã, G5, G11, Task 10); [3a-2](2026-10-13-lat-3a-2-may-tho-chay-that.md) (G29 kênh ghi, S6 + N2); [3b](2026-10-13-lat-3b-tho-tu-xa-codex.md) (token máy, ghép máy — lý do **không** dùng); [2d](2026-10-15-lat-2d-dashboard-bu-khoang-trong.md) (C1 — các phương án nguồn đèn).

## Global Constraints

- **Mốc:** plan viết trên `main` `38a016f` (đã có 3c Task 2, 4, R3 và font tự host D35). Không file nào 2e sửa bị các commit đó đụng tới; mọi bản vá đã `git apply --check` trên `38a016f`. **N₀** là số `passed` của `uv run pytest -q`, **M₀** là số test của `npm run kiem`, cả hai trên `main` lúc bắt đầu lát — **đo lại khi thực thi**. Lúc viết plan: N₀ = **1994**, M₀ = **33**. Mọi con số dưới đây viết dạng `N₀ + k`, kèm số tuyệt đối trên bản dựng thử.
- **Đã chạy thử (15/10, bản này):** dựng bản sao `main` `38a016f` trong scratchpad, không đụng repo thật. Script trích nguyên văn mọi khối "(mới)" và mọi khối `diff` **từ chính file plan này**, áp theo đúng thứ tự đợt: sau đợt 1 `uv run pytest -q` → **2010 passed** (N₀ + 16), `npm run kiem` → **34** (M₀ + 1); sau đợt 2 → **2016 passed** (N₀ + 22); `npm run build` và `npm run kiem-dist` xanh. Thông báo lỗi ghi ở Step 2 là kết quả chạy thật.
- **TDD:** mỗi task viết test trước, chạy thấy fail, viết mã, chạy thấy pass. 2e không sửa component `.vue` (D38, mục "Ranh giới 2e / 2f"). Cổng kiểm của frontend là `npm run kiem` (luật thuần + quét chèn HTML), `npm run build`, `npm run kiem-dist`.
- **Mỗi file ≤ ~120 dòng, mỗi dòng ≤ 120 ký tự.** Dòng dài có sẵn trong file cũ thì không sửa. File dài nhất sau plan: `tests/test_hook_dieu_phoi.py` 119, `tests/test_api_dieu_phoi.py` 116, `tram/api/dieu_phoi.py` 110.
- **Mỗi task một worktree, một nhánh, một commit**, tạo từ `main` sau khi đã ghép đợt trước. Task cùng đợt không sửa chung file. Không push, không merge hộ.
- **Không thêm phụ thuộc.** Không gọi mạng; frontend cài bằng `npm ci --offline --ignore-scripts`.
- **Test không được:** gọi mạng thật (hook dùng hàm mở URL giả; bài chạy tiến trình thật chỉ trỏ `https://127.0.0.1:9`, bị từ chối ngay trên loopback), đọc Keychain thật (`chay` giả cho `security`; bài chạy tiến trình thật đặt `TRAM_DIEU_PHOI_MA` nên không gọi `security`), đụng `~/.claude` thật (script chạy với `HOME` tạm; test không đọc/ghi gì dưới `~/.claude`), đụng `~/.tram` thật (`TRAM_HOME` tạm — `tests/conftest.py`), đụng dịch vụ đang chạy (`vn.tram.api`, `vn.tram.nho`, `vn.tram.bao-tin`), chạy `bd` thật.
- **Không vá các file sau** (plan song song hoặc phạm vi đã khoá):
  - plan 2d: `tram/suy/bang_diem*`, `tram/suy/diem_giao_viec.py`, `tram/suy/doi_ngu.py`, `tram/suy/pr_tram.py`, `tram/suy/giao_viec.py`, `tram/api/doi_ngu*`, `tram/api/luong.py`, `tram/bao_tin/*`, thẻ cột 3 (`frontend/src/giao_viec.js`, `thanh/TheBead.vue`, `thanh/OGiaoViec.vue`), `luat_doi_ngu.js`, `trang/DoiNgu.vue`;
  - plan 3c: `tram/cau_hinh/cach_ly.py`, `tram/chu/cai_dat_tho.py`, `tram/chu/lenh_tho.py`, `tram/chu/cai_dat.py`, `tram/chu/kiem_cach_ly.py`, `tram/giao_viec/principal_kiem.py` và các file khác của 3c;
  - plan 1b-4: `tram/nho/**` — lát này **chỉ import** `bam`, `MA_RE`, `BAM_RE`, `tep_cau_hinh`, `doc_bam`, `ghi_bam` từ `tram/nho/ma_dai_ca.py`, không sửa;
  - plan 1a-2: `tram/cham_cot/**`, `tram/du_an/**`, `tram/cli.py`, `tram/cli_du_an.py` (mới), lệnh `du-an`. **Ngoại lệ có kiểm:** Task 6 thêm 2 dòng vào `tram/cli_dich_vu.py` (đăng ký `dat-ma-dieu-phoi` ngay sau `dat-ma-dai-ca`). Đã grep 5 plan đợt 4: không plan nào sửa `tram/cli_dich_vu.py` (3c chỉ import `CONG_MAC_DINH`);
  - phạm vi refactor don-no mà 2d, 1b-4 cùng tránh: `tram/api/app.py` (route mới gắn qua router `van_phong`, G13), `tram/tho/vong_khe.py`, `tram/giao_viec/bo.py`, `tram/tho/ngu_canh.py`, `tram/giao_viec/tick_theo_plan.py`;
  - `tram/api/bao_mat.py`, `tram/api/kenh_ghi.py`, `tram/api/phu_thuoc.py`, `tram/su_kien/kho.py`: chỉ dùng, không sửa;
  - **component và bố trí của 2c** (`frontend/src/van_phong/*.vue`, `bo_tri.js`, `the_chu.js`, `frontend/src/trang/VanPhong.vue`): để nguyên cho lát 2f (G21, G24). Riêng `hien_thi.js` (luật thuần) được Task 4 sửa: thêm `chuNhip`, đổi một màu. Khảo sát §2.2 xếp file này vào nhóm 2f **giữ**, kể cả `chuNhip`.
  - Lát này **không đụng chung file nào với 2d**, nên không cần thứ tự ghép với 2d.
- **Bảo mật spec 2 §4 giữ nguyên, không ngoại lệ cho route mới:**
  - tram-api vẫn chỉ nghe `127.0.0.1`; máy A tới qua `tailscale serve` có sẵn (`/` → tram-api), không `funnel`, không thêm đường serve.
  - Host ngoài danh sách → 421; mọi phản hồi mang CSP và header an toàn (`GiuaAnToan`, áp cho cả app).
  - Danh tính Tailscale ∈ `dai_ca_logins`, đúng một header; `X-Tram: 1`; `Origin` = `https://<ten_may_b>` — dùng **chính** `yeu_cau_ghi`.
  - Chế độ `cach_ly.kenh_ghi: unix-socket`: yêu cầu qua TCP bị 403 như mọi API ghi (G29 3a-2).
  - **Thêm** mã điều phối vì header Tailscale trên TCP localhost giả được (§4 mục 2b).
  - Route mới chỉ ghi `dieu_phoi.nhip` của `_tram`; không chạm beads, phiếu, khe, memory, estop. API ghi dashboard vẫn bỏ qua `Authorization`. Mã điều phối không mở route nào khác và không đọc được memory (test ở Task 2 và Task 6).
  - Chuỗi từ server hiện bằng `{{ }}`, cấm `v-html` (`kiem-an-toan.mjs`) — áp cho lát 2f khi gắn luật vào component.
- **Lệnh kiểm:** `uv run pytest -q` từ gốc worktree; trong `frontend/` chạy `npm run kiem`, `npm run build`, `npm run kiem-dist`.

## Phụ thuộc đã có (main `38a016f`) — dùng, không sửa trừ chỗ ghi rõ

| Thứ dùng | Ở đâu (plan) | Plan 2e dùng ở |
|---|---|---|
| `yeu_cau_ghi(request)`: kênh hợp lệ → đúng một `Tailscale-User-Login` ∈ `dai_ca_logins` → `X-Tram: 1` → `ten_may_b` đã cấu hình → `Origin` = `https://<ten_may_b>`; lỗi → `HTTPException(403)` | `tram/api/bao_mat.py` (2a; 3a-2 T10) | Task 2 |
| `GiuaAnToan` (Host lạ → 421; CSP + `nosniff`, `no-referrer`, `DENY` cho mọi phản hồi, kể cả 500) | `tram/api/bao_mat.py` (2a) | Task 2 (test 421, CSP) |
| `kenh_hop_le(request)`; `KenhUnix` (gắn `scope["tram.kenh"] = "unix"`); `app.state.kenh_ghi` (`header` mặc định, `unix-socket` khi `chay_hai_cong`) | `tram/api/kenh_ghi.py` (3a-2 T10, G29) | Task 2 |
| `bam(ma)`, `MA_RE` (32–256 ký tự an toàn trong header), `BAM_RE`, `tep_cau_hinh(duong_dan=None)`, `doc_bam()` / `ghi_bam()` của **mã Đại ca** (khoá `ma_dai_ca_sha256`); `dat_ma_dai_ca` — khuôn hỏi ẩn của lệnh mới | `tram/nho/ma_dai_ca.py` (1b-2 T3) — **chỉ import** | Task 6 (khuôn + chặn trùng mã), Task 2, 6 (test tách bạch) |
| `them_lenh(sub, chu)`: nơi đăng ký lệnh `tram chu …` (**sửa** — Task 6, 2 dòng) | `tram/cli_dich_vu.py` (2a, 1b-2) | Task 6 |
| `CauHinhMcp(tra, bam_ma_dai_ca, co_du_an)`; `tao_ung_dung(dv, cfg)` (cổng xác thực MCP + `/nho-lai` nội bộ); `DichVuNho`, `KhoKyUc`, `BoDemDung` | `tram/nho/ung_dung.py`, `may_chu_mcp.py` (1b-2) — chỉ dùng trong test | Task 6 (test mã điều phối không đọc memory) |
| `KhoSuKien.ghi(du_an, loai, du_lieu, *, bead_id=None, tac_nhan=…) -> luc` (ISO UTC `…Z` đến giây, commit bằng `with self._db`); `.gan_day(du_an, loai, gioi_han)` trả mới → cũ; `._doc(sql, tham_so)`, `_CHON` (nội bộ — chỉ `kho_nhip.py` và `ghi_nhip` dùng); `.sau_id`, `.id_moi_nhat`; `SuKien(luc, du_an, bead_id, loai, tac_nhan, du_lieu, id, …)` | `tram/su_kien/kho.py` (2a) | Task 1, 2 |
| `mo_ket_noi`: WAL, `busy_timeout` 10 giây — lời gọi thứ hai chờ khoá `BEGIN IMMEDIATE` thay vì lỗi | `tram/su_kien/ket_noi.py` (2a) | Task 2 |
| `PhuThuocApi.mo_kho`, `.dong_ho` (datetime UTC có múi giờ; test thay được vì `pt` là dataclass thường) | `tram/api/phu_thuoc.py` (2a, 3a-1) | Task 1, 2 |
| `cac_phong(cac_du_an, *, so_cho, suc_khoe)` (**sửa ở Task 1**); `r_van_phong` và `router` của `/api/van-phong` (**sửa ở Task 1, 2**); `van_phong.router` đã nằm trong `CAC_TUYEN` của `app.py` | `tram/suy/van_phong.py`, `tram/api/van_phong.py` (2c T2, T5) | Task 1, 2 |
| `CAC_TUYEN` (mọi router của tram-api) | `tram/api/app.py` — chỉ import trong test | Task 2 (quét mọi route ghi) |
| Sự kiện hệ dùng `du_an = "_tram"`; `/api/luong` không đánh dấu bộ đệm cho dự án bắt đầu bằng `_` | spec 2 §12.2; `tram/api/luong.py` (2a) | Task 2 |
| Trang Văn phòng tải lại `/api/van-phong` mỗi 5 giây (`CHU_KY_MS`); `chuBien(p)`: Điều phối → "chưa có tín hiệu" / "đang có phiên" / "tắt đèn" theo `sang` null / true / false; `MAU.den` / `MAU.denTat` (**sửa** `MAU.den` ở Task 4); `Phong3D.vue`: đèn màu `MAU.den`, phát sáng khi `p.sang`, không thì `MAU.denTat` | `frontend/src/van_phong/hien_thi.js` (**sửa ở Task 4**), `Phong3D.vue`, `frontend/src/trang/VanPhong.vue` (2c) — `.vue` **không sửa** | Task 4, Task 5 (kiểm đèn) |
| `gioVN(iso)` | `frontend/src/luat.js` (2a) | Task 4 |
| Tiền lệ script cho máy A: thư mục trong repo, python3 ≥ 3.9 thư viện chuẩn, test chạy bằng `sys.executable -I` + `ast.parse(..., feature_version=(3, 9))`, Đại ca tự chép sang máy A | `ky-nang/xem-spec-cho-duyet/` (4b) | Task 3 |
| Test: `tao_app_gia(tmp_path, bds) -> (app, pt)`, `DAI_CA`, `MAY_B`, `LOGIN` (`api_gia.py`); `tao_tram(tmp_path, token_noi_bo=…, dang_ky=False)` (`tho_api_gia.py`, có kho phiếu + token máy); `goi(app, phuong_thuc, duong_dan, *, json_body, headers)` (`asgi_gia.py` — header truyền vào ghi đè `host`); `goi_mcp`, `goi_cong_cu`, `van_ban` (`mcp_gia.py`); `EmbedderGia`, `ky_uc` (`nho_gia.py`); fixture tự động `tram_home_tam` (`conftest.py`); `estop.dang_bat()` | `tests/` | Task 1, 2, 6 |

## Câu hỏi / giả định

Ý nghĩa cột "Loại":
- **HỢP ĐỒNG MỚI**: giao diện hoặc dữ liệu mà bên khác (máy A, frontend, Đại ca, spec) sẽ dựa vào. **Đại ca cần chốt** trước khi thực thi (C5).
- **lệch chữ spec**: làm khác câu chữ spec.
- **giả định**: chi tiết thực thi; Đại ca gạch nếu không đồng ý.
- **đã chốt**: Đại ca đã quyết (số D).

| # | Chỗ mơ hồ | Chọn | Vì sao | Loại — lệch chữ spec / HỢP ĐỒNG MỚI |
|---|---|---|---|---|
| G1 | Mốc test | N₀/M₀ đo lại khi thực thi. Lúc viết plan (`main` `38a016f`): 1994 / 33 | Nhiều plan đợt 4 có thể ghép trước | giả định |
| G2 | Cơ chế xác thực của đường ghi | **Bỏ** đề xuất cũ "dùng lại mã Đại ca". Thay bằng **mã điều phối riêng** (D24): `Authorization: Bearer <mã điều phối>`, trạm so sha256 với `dieu_phoi_ma_sha256` bằng `hmac.compare_digest`, đọc băm mỗi lời gọi. Không dùng mã Đại ca, không dùng token máy (3a-1/3b). Chi tiết ở G23 | Đại ca chốt D24: mã chỉ để gửi nhịp; lộ mã thì không đọc được memory | **đã chốt** (D24) |
| G3 | Có đòi header Tailscale không | **Có.** Route gọi đúng `yeu_cau_ghi` của dashboard: kênh, đúng một `Tailscale-User-Login` ∈ `dai_ca_logins`, `X-Tram: 1`, `Origin`. Mã điều phối là lớp **thêm** | Giữ chữ spec 2 §4 mục 2–3 ("API ghi chỉ chấp nhận khi header có mặt…", "mọi `POST` phải có `X-Tram`… `Origin`"). Route này nằm trên tram-api, sau cùng một `tailscale serve /` với dashboard. Nếu Task 5 thấy `tailscale serve` không gắn header cho yêu cầu không từ trình duyệt → C4 | giả định — xem C4 |
| G4 | Đường và giao thức | `POST /api/dieu-phoi/nhip` trên tram-api (7700, hoặc Unix socket khi `kenh_ghi: unix-socket`). Máy A gọi `https://<ten_may_b>/api/dieu-phoi/nhip` qua `tailscale serve /` có sẵn. Phản hồi `200 {"ghi": true \| false}` (`false` = đã gộp) | Không mở cổng mới, không thêm đường serve | **HỢP ĐỒNG MỚI** |
| G5 | Thân yêu cầu | `{"su_kien": "SessionStart" \| "UserPromptSubmit" \| "Stop" \| "SessionEnd", "phien": "<16 hex thường>"}`, `extra="forbid"`. `phien` = 16 hex đầu của sha256(`session_id`) tính **trên máy A**. Không gửi `cwd`, `prompt`, `transcript_path` | Trạm chỉ cần phân biệt phiên. Mã phiên thô và nội dung prompt không rời máy A (§4 mục 5 tinh thần "không gửi nội dung nghiệp vụ") | **HỢP ĐỒNG MỚI** |
| G6 | `ma_thao_tac`, `expected_version` | **Không có.** Lặp lại cùng nhịp vô hại; tính bền thay bằng gộp ghi (G8) | Spec 2 §7: "Mọi `POST` ghi mang `ma_thao_tac` và `expected_version` (§12.3)". §12.3 nói về nút ghi của dashboard trên bead; nhịp không gắn bead, không có phiên bản để so | **lệch chữ spec** — xem C6 |
| G7 | Sự kiện | `dieu_phoi.nhip`, `du_an = "_tram"`, `bead_id = null`, `tac_nhan = "dai-ca/may-a"`, `du_lieu = {su_kien, phien}`. Không vào `LOAI_LAM_MOI` (SSE), không thành tin Telegram, không là nguồn ký ức | Q12: trạng thái suy từ sự kiện, không kho riêng; nhịp còn sau khi tram-api khởi động lại | **HỢP ĐỒNG MỚI** (bảng sự kiện §12.2) |
| G8 | Gộp ghi | Ghi khi: phiên chưa có nhịp; hoặc đổi giữa "kết thúc" (`SessionEnd`) và "đang chạy"; hoặc nhịp cuối của phiên cũ ≥ 60 giây. Còn lại trả `{"ghi": false}`. **Nguyên tử** (F10): `BEGIN IMMEDIATE` trước khi đọc; lời gọi song song chờ khoá rồi mới đọc; nhánh không ghi rollback | `UserPromptSubmit` + `Stop` mỗi lượt có thể vài lần/phút; gộp giữ nhật ký ≤ ~1 dòng/phút/phiên. Không khoá thì hai lời gọi cùng đọc "chưa có" rồi cùng ghi | giả định — xem C2 |
| G9 | Ý nghĩa đèn | `sang = null`: chưa từng có nhịp. `true`: có phiên mà nhịp cuối **không** là `SessionEnd` và cách đây ≤ 15 phút (đúng 15 phút vẫn sáng). `false`: mọi phiên đã `SessionEnd` hoặc quá 15 phút. Thêm khoá `nhip_cuoi` (ISO UTC của nhịp mới nhất, hoặc `null`) vào phòng Điều phối. **Cách đọc** (F11): mọi nhịp có `luc` ≥ bây giờ − 15 phút; không có thì lấy 1 nhịp mới nhất để biết "hết hạn" khác "chưa có" | "Hết hạn thì đèn xám": `false` và `null` đều xám (`MAU.denTat`), chữ khác nhau. Hai phiên song song: một phiên đóng không tắt đèn của phiên kia. Cắt 200 dòng như bản cũ thì >200 nhịp của phiên khác đẩy được phiên còn sống ra ngoài | **HỢP ĐỒNG MỚI** — xem C2 |
| G10 | Giới hạn tần suất | 30 lời gọi / 60 giây cho **cả route**, cửa sổ trượt trong bộ nhớ tiến trình tram-api (`app.state.gioi_han_dieu_phoi`). Đếm sau bước kênh, **trước** xác thực, nên lời gọi hỏng cũng tính → 429. Mất khi khởi động lại | Chặn băm/đọc file và ghi DB vô hạn. Hook thật gửi ≤ 2 lần mỗi lượt hội thoại. Đổi lại: kẻ gọi rác có thể làm đèn bỏ lỡ nhịp tối đa 1 phút (chỉ ảnh hưởng hiển thị) | giả định |
| G11 | Giới hạn kích thước | Thân ≤ 512 byte. `Content-Length` khai lớn hơn → 413 ngay; không có `Content-Length` thì đọc luồng, vượt trần → 413. Thân hợp lệ thật ~60 byte | Không đọc nguyên thân lớn vào bộ nhớ | giả định |
| G12 | Thứ tự kiểm và mã lỗi | 421 Host (middleware) → 403 kênh → 429 → 403 danh tính/CSRF (`yeu_cau_ghi`) → 401 mã điều phối (thiếu, sai, là mã Đại ca, không dạng `Bearer`, hoặc trạm chưa đặt mã) → 413 → 422 → 200. Thông báo lỗi không chứa mã | Rẻ trước; đọc thân sau khi đã xác thực | giả định |
| G13 | Đăng ký route | `tram/api/van_phong.py`: `router.include_router(dieu_phoi.router)`. **Không** sửa `tram/api/app.py` | `app.py` nằm trong danh sách mà 2d, 1b-4 cùng tránh. Đèn là một phần của Văn phòng. `van_phong.router` đã có trong `CAC_TUYEN` (2c G18) | giả định |
| G14 | Làm mới trang | Không thêm SSE. Trang Văn phòng đã tải lại mỗi 5 giây → đèn sáng/xám trễ ≤ 5 giây sau nhịp hoặc sau khi hết hạn | Hết hạn không sinh sự kiện nên SSE không giúp; tránh sửa `luong.py` (2d sửa) | giả định |
| G15 | Script máy A | `may-a/hook-dieu-phoi/hook_dieu_phoi.py`, python3 ≥ 3.9, chỉ thư viện chuẩn. Kèm `settings.mau.json` (khối `env` + bốn hook, `timeout: 5`) và `HUONG-DAN.md`. Lệnh hook là `/usr/bin/python3 "$HOME/.claude/hooks/hook_dieu_phoi.py"` | Cùng cách với skill `xem-spec-cho-duyet` (máy A không cài ben-station). Đường tuyệt đối tránh `python3` lạ trong `PATH` | giả định |
| G16 | Sự kiện hook | `SessionStart`, `UserPromptSubmit`, `Stop`, `SessionEnd`. Đọc `hook_event_name`, `session_id` từ JSON trên stdin | **Giả định cần spike** (Task 5 bước 3): chưa kiểm hành vi hook thật của bản Claude Code trên máy A | giả định — **cần spike** |
| G17 | Bí mật và cấu hình trên máy A | Mã: Keychain máy A, dịch vụ **`tram-dieu-phoi-ma`** (`/usr/bin/security find-generic-password -s tram-dieu-phoi-ma -w`; mã chỉ đi qua stdout ống, không qua argv). Biến `TRAM_DIEU_PHOI_MA` được đọc trước Keychain **chỉ để kiểm nhanh/test**, không đặt trong cấu hình. Hook **không** đọc `TRAM_DAI_CA_MA`. Địa chỉ trạm: biến `TRAM_DIEU_PHOI_URL` = `https://<ten_may_b>` trong khối `env` của `settings.json` (không bí mật). Không ghi mã vào file nào | D24 đặt tên mục Keychain. Biến kiểm nhanh giúp chạy "Kiểm nhanh" và test tiến trình thật mà không đụng Keychain | **HỢP ĐỒNG MỚI** (tên biến `TRAM_DIEU_PHOI_URL`, `TRAM_DIEU_PHOI_MA`) |
| G18 | Không chặn phiên | Timeout 2 giây cho **mỗi thao tác** (đọc Keychain, mở URL của `urllib`). **Cả hook** tối đa `HAN_TOAN_BO` = 4 giây: việc chạy trong luồng nền, luồng chính chờ tối đa 4 giây rồi `os._exit(0)` (F14). `timeout: 5` trong settings là trần của Claude Code. Lỗi gì cũng nuốt, luôn thoát 0, không in stdout/stderr | Stdout của hook `UserPromptSubmit`/`SessionStart` thoát 0 bị đưa vào ngữ cảnh phiên; thoát 2 chặn prompt. Keychain 2 giây + HTTP 2 giây + DNS tên tailnet khi Tailscale tắt có thể vượt 5 giây nếu không có hạn chung. Hạn 4 giây cần spike xác nhận khi DNS treo (Task 5 H3) | giả định — **cần spike** |
| G19 | Đường đi của mã | Chỉ nhận `TRAM_DIEU_PHOI_URL` dạng `https://host[:cổng]`, không đường dẫn/query/user. Tắt proxy (`ProxyHandler({})`, kể cả proxy hệ thống macOS) và **không theo chuyển hướng** (3xx → lỗi im lặng) | `urllib` mặc định theo 302 và mang theo `Authorization`, và đi qua `HTTPS_PROXY`. Mã chỉ được tới đúng máy B | giả định |
| G20 | "Phiên điều phối" là gì | Mặc định: **mọi** phiên Claude Code trên máy A (cài vào `~/.claude/settings.json`). Muốn hẹp hơn: cài khối `hooks` + `env` vào `<thư mục điều phối>/.claude/settings.json` — không cần đổi mã | Kiến trúc §4.1: vai của máy A là Điều phối. Code tay cũng có thể chạy trên A — xem C3 | giả định — xem C3 |
| G21 | Frontend ở 2e | Chỉ sửa luật thuần `frontend/src/van_phong/hien_thi.js`: thêm `chuNhip(p)` → `"nhịp cuối <gioVN(nhip_cuoi)>"` hoặc `null`; đổi `MAU.den` `#fff2cc` → **`#f2c14e`** (vàng ấm, D38). Thêm test `frontend/tests/dieu_phoi.test.mjs`. **Không** sửa `.vue` (bản cũ thêm một dòng vào `DanhSachVanPhong.vue` — đã bỏ) | D38: ghép 2e trước rồi 2f làm lại `.vue`; khảo sát §1.11 giữ `chuNhip` ở 2e, §2.2 giữ `hien_thi.js` ở 2f. `MAU.den` chỉ dùng cho đèn Điều phối (`Phong3D.vue`), nên đổi màu có hiệu lực ngay trên giao diện 2c mà không đụng `.vue` | giả định — xem G24 |
| G22 | Dung lượng nhật ký | Không dọn `dieu_phoi.nhip` cũ. Ước ≤ ~1 dòng/phút/phiên đang làm việc | Bảng sự kiện là nhật ký chỉ thêm; dọn là việc chung — "Để sau" | giả định |
| G23 | Mã điều phối phía trạm | Khoá **`dieu_phoi_ma_sha256`** (64 hex thường) trong `~/.tram/cau-hinh.yaml`, cạnh `ma_dai_ca_sha256`. Module `tram/chu/ma_dieu_phoi.py`: `doc_bam()` (thiếu/hỏng → `None`, route từ chối mọi lời gọi), `ghi_bam()` (giữ chú thích và khoá khác, ghi nguyên tử, **từ chối nếu trùng băm mã Đại ca**). Lệnh **`tram chu dat-ma-dieu-phoi [--dong-y]`**: hỏi ẩn bằng `getpass` hai lần, không có cờ nhận mã. Máy A tạo mã thẳng vào clipboard (`openssl rand -hex 32 \| pbcopy`), không hiện ra màn hình | D24: trạm chỉ giữ băm. Theo khuôn `tram chu dat-ma-dai-ca` (1b-2). Không sửa `tram/nho/ma_dai_ca.py` (1b-4 khoá) — module mới chỉ import `bam`, `MA_RE`, `BAM_RE`, `tep_cau_hinh`, `doc_bam` từ đó. Khoá cấp cao lạ trong `cau-hinh.yaml` không làm `nap_cau_hinh_tram` lỗi (test) | **HỢP ĐỒNG MỚI** (tên khoá, tên lệnh) |
| G24 | Ranh giới 2e / 2f | 2e giao: dữ liệu `sang`/`nhip_cuoi` của `GET /api/van-phong` (G9), `chuNhip`, `MAU.den` (G21), băm mã điều phối đọc được qua `tram.chu.ma_dieu_phoi.doc_bam()` (G23). 2f làm: chấm đèn + chữ trên biển phòng 3D, chip "đèn: …" ở danh sách, dòng "nhịp cuối" ở danh sách/khung chi tiết, ô "mã điều phối có/chưa" ở Cài đặt, theo mockup D20/D33. Chi tiết ở mục "Ranh giới 2e / 2f" | Quy tắc 15/10: việc giao diện phải theo mockup đã duyệt. Mockup chỉ vẽ trạng thái "chưa có tín hiệu"; D38 chốt màu sáng và chữ "đang có phiên" / "tắt đèn" như `chuBien`. Mockup Tổng quan **không** có ô đèn Điều phối — muốn thêm thì phải dựng mockup và duyệt lại | giả định |

**Vì sao mã điều phối riêng (D24), không phải mã Đại ca hay token máy.**
- **Mã Đại ca** (1b-2) mở MCP memory phiên tay. Hook chạy tự động ở mọi phiên trên máy A, nên mã của nó dễ lộ hơn. Dùng chung thì lộ mã hook là lộ quyền đọc memory. D24 tách: lộ mã điều phối thì kẻ có mã, đứng trong tailnet với login của Đại ca, chỉ bật/tắt được đèn giả.
- **Token máy** (3a-1, 3b) là bằng chứng của **máy thợ**: nó mở cả nhóm `/api/tho/*`. Kiến trúc §4.1 ghi máy A **không** cài `tram-tho`.
- Trạm chỉ giữ băm, đọc lại mỗi lời gọi (đổi mã có hiệu lực ngay, không khởi động lại). Test chứng minh hai chiều: mã điều phối bị memory service từ chối (MCP và `/nho-lai`), bị mọi route ghi khác từ chối; mã Đại ca bị route nhịp từ chối.

## Chờ Đại ca chốt

**Đã chốt:** C1 (mã cho hook) → **D24**: mã riêng `tram-dieu-phoi-ma`, trạm giữ băm, không mở rộng mã Đại ca. Plan đã sửa theo (G2, G17, G23).

Còn mở, mỗi câu kèm đề xuất của Em:

- **C2 — Hạn sống và gộp (G8, G9).** Đèn xám sau 15 phút không có nhịp; mỗi phiên ghi tối đa 1 nhịp/phút. **Đề xuất: giữ 15 phút và 60 giây.** Thoát phiên đã tắt đèn ngay qua `SessionEnd`, nên hạn sống chủ yếu để phòng phiên chết hay máy ngủ. Nếu Đại ca hay ngồi đọc quá 15 phút không gõ mà muốn đèn vẫn sáng thì nâng lên 30 phút. Đổi chỉ là hằng `HAN_SONG` trong `tram/suy/dieu_phoi.py` và các mốc phút trong test Task 1.
- **C3 — Phạm vi "phiên điều phối" (G20).** **Đề xuất: mọi phiên Claude Code trên máy A** (cài ở `~/.claude/settings.json`), vì vai của máy A là Điều phối. Muốn chỉ một thư mục thì cài ở mức dự án, không cần đổi mã.
- **C4 — Header Tailscale (G3).** **Đề xuất: giữ đòi `Tailscale-User-Login`** như mọi API ghi. Nếu Task 5 H5 thấy `tailscale serve` không gắn header cho yêu cầu không từ trình duyệt thì chọn **(a)**: bỏ đòi header **chỉ ở route này**, vẫn đòi kênh + `X-Tram` + `Origin` + mã điều phối (một task nhỏ, sửa `tram/api/dieu_phoi.py`). Với mã riêng, (a) chỉ mở thêm quyền bật/tắt đèn cho ai có mã. Phương án **(b)** là giữ nguyên và chờ cách khác; khi đó đèn không sáng được.
- **C5 — Duyệt các HỢP ĐỒNG MỚI.** G4 (route), G5 (thân), G7 (sự kiện), G9 (ba giá trị `sang` + `nhip_cuoi`), G17 (biến `TRAM_DIEU_PHOI_URL`, `TRAM_DIEU_PHOI_MA`), G23 (khoá `dieu_phoi_ma_sha256`, lệnh `tram chu dat-ma-dieu-phoi`). Tên mục Keychain `tram-dieu-phoi-ma` đã theo D24. **Đề xuất: duyệt cả gói như plan.**
- **C6 — Lệch chữ spec G6** (POST nhịp không có `ma_thao_tac`/`expected_version`). **Đề xuất: chấp nhận lệch**, ghi ngoại lệ vào spec 2 §7: nhịp không gắn bead, không có phiên bản để so, gửi lặp vô hại vì đã gộp.

## Hợp đồng (lát 2e)

`POST /api/dieu-phoi/nhip` (G4, G5, G12, G23):

```http
POST /api/dieu-phoi/nhip HTTP/1.1
Host: may-b.tail1234.ts.net
Content-Type: application/json
Authorization: Bearer <mã điều phối>
X-Tram: 1
Origin: https://may-b.tail1234.ts.net
Tailscale-User-Login: <do tailscale serve gắn>

{"su_kien": "UserPromptSubmit", "phien": "3f9c0a1b2c3d4e5f"}
```

Trả `200 {"ghi": true}` (đã ghi) hoặc `200 {"ghi": false}` (đã gộp). Lỗi: `{"detail": "<câu cố định>"}`, mã 403/429/401/413/422 theo G12; Host lạ 421 `{"loi": …}`.

`GET /api/van-phong` — phòng Điều phối (G9). Các phòng khác giữ nguyên:

```json
{"ma": "dieu-phoi", "loai": "dieu_phoi", "ten": "Điều phối", "sang": true, "nhip_cuoi": "2026-10-15T07:05:00Z"}
```

Sự kiện (G7): `dieu_phoi.nhip` · ghi bởi `POST /api/dieu-phoi/nhip` (hook máy A) · đọc bởi `GET /api/van-phong` · `du_an = "_tram"`, `tac_nhan = "dai-ca/may-a"` · `{su_kien, phien}`.

Cấu hình trạm (G23): `~/.tram/cau-hinh.yaml` thêm `dieu_phoi_ma_sha256: "<64 hex>"`, do `tram chu dat-ma-dieu-phoi` ghi. Máy A (G17): Keychain `tram-dieu-phoi-ma`; `settings.json` có `env.TRAM_DIEU_PHOI_URL`.

Luật hiển thị (G21, D38) — trong `frontend/src/van_phong/hien_thi.js`, phòng Điều phối:

| `p.sang` | `chuBien(p)` (có từ 2c, không đổi) | Màu đèn (`Phong3D.vue` của 2c) |
|---|---|---|
| `null` (hoặc không có) | Điều phối · chưa có tín hiệu | `MAU.denTat` `#b7b7b7`, không phát sáng |
| `true` | Điều phối · đang có phiên | `MAU.den` **`#f2c14e`** (vàng ấm, D38), phát sáng |
| `false` | Điều phối · tắt đèn | `MAU.denTat` `#b7b7b7`, không phát sáng |

`chuNhip(p)`: `"nhịp cuối <gioVN(nhip_cuoi)>"` nếu `p.loai === 'dieu_phoi'` và có `nhip_cuoi`; còn lại `null`.

## Ranh giới 2e / 2f

Theo D38 (Q14: ghép 2d/2e nguyên văn trước, 2f làm lại `.vue`) và bảng §1.11 của khảo sát giao diện.

| Phần | 2e (plan này) | 2f (lát làm lại giao diện, theo mockup D20/D33) |
|---|---|---|
| Dữ liệu `sang`, `nhip_cuoi` của `GET /api/van-phong` | **Làm** (Task 1) | Chỉ đọc. 2f T6 sửa cùng `tram/suy/van_phong.py` nên làm sau 2e |
| `POST /api/dieu-phoi/nhip`, hook máy A, chạy thật | **Làm** (Task 2, 3, 5) | — |
| Mã điều phối (khoá băm, lệnh) | **Làm** (Task 6) | Trang Cài đặt hiện "mã điều phối: có/chưa" bằng `tram.chu.ma_dieu_phoi.doc_bam()`, không bao giờ hiện giá trị |
| `chuNhip(p)`, `MAU.den = '#f2c14e'` trong `hien_thi.js` | **Làm** (Task 4) | Giữ; khi đổi `MAU` sang bảng màu mockup thì giữ `den` vàng ấm (D38) |
| Đèn 3D + chữ biển của giao diện 2c hiện tại | Không sửa `.vue`; đã đọc `sang` và `MAU.den` nên đổi màu, đổi chữ ngay khi backend 2e chạy | Thay bằng cảnh mới |
| Biển phòng 3D theo mockup (`van-phong.js`: chấm `.den` + `<small>` chữ trạng thái) | — | **Làm**: chấm vàng ấm phát sáng khi `sang`, xám khi không; chữ như `chuBien` |
| Danh sách phòng (`trang-van-phong.js`: chip "đèn: …") | — | **Làm**: chip theo `sang`; thêm `chuNhip(p)` nếu có |
| Khung chi tiết khi bấm phòng (mockup: "Đèn Điều phối: … Không có trang đích.") | — | **Làm**: trạng thái + `chuNhip(p)`; vẫn không có trang đích |
| Dòng "nhịp cuối" (bản cũ của 2e đặt ở `DanhSachVanPhong.vue`) | **Bỏ khỏi 2e** (chỉ còn hàm `chuNhip`) | **Làm** ở danh sách/khung chi tiết; kiểu hiển thị cần chốt khi dựng plan 2f (khảo sát §1.11) |
| Ô đèn trên Tổng quan | — | **Không làm** cho tới khi mockup Tổng quan có ô này và được duyệt lại |
| Khối "Sự kiện gần đây" ở Tổng quan | — | Nên **lọc bỏ** `dieu_phoi.nhip` (tới ~1 dòng/phút/phiên sẽ lấn hết khối) |
| Kiểm chạy thật đèn trên trình duyệt | Task 5 Step 4 trên giao diện 2c | Kiểm lại trên giao diện mới |

## File Structure

```
tram/
  suy/dieu_phoi.py          # LOAI, DU_AN_HE, TAC_NHAN, HAN_SONG, GOP, den_dieu_phoi, can_ghi (G7–G9)  — Task 1 (mới, 47)
  suy/kho_nhip.py           # doc_nhip: mọi nhịp trong HAN_SONG, fallback 1 nhịp (G9, F11)               — Task 1 (mới, 15)
  suy/van_phong.py          # (sửa) cac_phong(..., dieu_phoi=None)                                     — Task 1 (37)
  api/van_phong.py          # (sửa) đọc nhịp → dieu_phoi (Task 1); include_router(dieu_phoi) (Task 2)   — (36)
  api/dieu_phoi.py          # POST /api/dieu-phoi/nhip: GioiHan, kiem_ma_dieu_phoi, doc_than, ghi_nhip  — Task 2 (mới, 110)
  chu/ma_dieu_phoi.py       # dieu_phoi_ma_sha256: doc_bam, ghi_bam, lệnh dat-ma-dieu-phoi (G23)        — Task 6 (mới, 90)
  cli_dich_vu.py            # (sửa, 2 dòng) đăng ký dat-ma-dieu-phoi                                    — Task 6 (70)
may-a/hook-dieu-phoi/
  hook_dieu_phoi.py         # hook máy A: lay_ma, goc_tram, dung_yeu_cau, chay, chay_co_han (G15–G19)  — Task 3 (mới, 90)
  settings.mau.json         # khối env + 4 hook, timeout 5                                              — Task 3 (mới, 51)
  HUONG-DAN.md              # tạo mã / cài / kiểm nhanh / gỡ / giả định cần spike                        — Task 3 (mới, 71)
frontend/
  src/van_phong/hien_thi.js            # (sửa) chuNhip, MAU.den = '#f2c14e' (G21, D38) — không sửa .vue — Task 4 (66)
  tests/dieu_phoi.test.mjs             # (mới)                                                          — Task 4 (17)
tests/
  test_den_dieu_phoi.py (Task 1, mới, 70) · test_api_dieu_phoi.py (Task 2, mới, 116)
  test_nhip_nguyen_tu.py (Task 2, mới, 39) · test_hook_dieu_phoi.py (Task 3, mới, 119)
  test_ma_dieu_phoi.py (Task 6, mới, 88)
```

`tram/api/van_phong.py` do Task 1 và Task 2 cùng sửa, ở hai đợt khác nhau. Bản vá Task 2 sinh trên `main` sau Task 1; đã thử `git apply --check` trên cả `main` gốc lẫn `main` sau đợt 1.

## Chuẩn bị (người điều phối)

```bash
cd "/Users/dai-ca/Developer/Ben Station"
git status --short            # chỉ được có .beads/interactions.jsonl, .DS_Store — không đụng
git log --oneline -1 main     # plan viết trên 38a016f; khác thì chạy `git apply --check` mọi bản vá trước
uv run pytest -q              # ghi N₀ (lúc viết: 1994)
(cd frontend && npm ci --offline --ignore-scripts && npm run kiem && npm run build && npm run kiem-dist)  # ghi M₀ (33)
```

**Mỗi task một worktree**, tạo từ `main` sau khi đã ghép mọi task của đợt trước:

```bash
N=1   # số task
git worktree add .worktrees/2e-t$N -b 2e/t$N main
cd .worktrees/2e-t$N && uv sync && uv run pytest -q                 # kỳ vọng: số "sau đợt trước" ở Sơ đồ đợt
(cd frontend && npm ci --offline --ignore-scripts)                    # chỉ Task 4
```

**Mã:**
- File **mới**: chép nguyên văn đầy đủ.
- File **có sẵn**: bản vá unified diff, sinh bằng `git diff` trên bản dựng thử. Lưu khối `diff` ra file (vd `../t1.diff`) rồi chạy `git apply --check ../t1.diff && git apply ../t1.diff`. `--check` lỗi nghĩa là `main` đã đổi đúng chỗ đó: **dừng**, báo người điều phối; không áp tay đoán mò.

Cuối mỗi task: người thực thi commit trong worktree. Người điều phối kiểm: mọi dòng thêm có nguyên văn trong plan; số test đúng kỳ vọng; file ≤ ~120 dòng. Sau đó `git merge --no-ff 2e/t$N` vào `main` (không push). Ghép xong cả đợt thì chạy lại các lệnh kiểm trên `main`; kết quả phải khớp số "sau đợt". Dòng ghi công trong lệnh commit: thay `<model đang thực thi>` bằng đúng tên model của người thực thi task.

---

### Task 1: Suy đèn Điều phối từ nhịp, đọc theo hạn sống, `/api/van-phong` trả `sang` thật

**Độ khó:** `de` · **Đợt:** 1 · **Song song với:** Task 3, 4, 6 · **Phải xong trước:** —

**Files:**
- Create: `tram/suy/dieu_phoi.py`, `tram/suy/kho_nhip.py`
- Modify: `tram/suy/van_phong.py` (`cac_phong`), `tram/api/van_phong.py` (import, `r_van_phong`)
- Test: `tests/test_den_dieu_phoi.py` (mới)

**Interfaces:**
- Consumes: `KhoSuKien._doc`, `_CHON`, `.gan_day(du_an, loai, 1)` (mới → cũ), `SuKien.luc` (ISO `…Z` đến giây), `pt.mo_kho`, `pt.dong_ho`.
- Produces:
  - `tram/suy/dieu_phoi.py`: `LOAI = "dieu_phoi.nhip"`, `DU_AN_HE = "_tram"`, `TAC_NHAN = "dai-ca/may-a"`, `SU_KIEN_HOOK`, `KET_THUC = "SessionEnd"`, `HAN_SONG = timedelta(minutes=15)`, `GOP = timedelta(seconds=60)`; `den_dieu_phoi(nhip: list[SuKien], bay_gio: datetime) -> {"sang": bool | None, "nhip_cuoi": str | None}`; `can_ghi(nhip, phien: str, su_kien: str, bay_gio: datetime) -> bool`. Task 2 import các tên này. (Bản cũ có `DOC_TOI_DA = 200` — **đã bỏ**, F11.)
  - `tram/suy/kho_nhip.py`: `doc_nhip(kho, luc) -> list[SuKien]` — mọi nhịp có `luc` ≥ `luc − HAN_SONG`, mới → cũ; rỗng thì `gan_day(..., 1)`. Task 2 dùng trong `ghi_nhip`.
  - `cac_phong(cac_du_an, *, so_cho, suc_khoe, dieu_phoi: dict | None = None)`: phòng `dieu-phoi` mang `dieu_phoi` (mặc định `{"sang": None}` — test 2c cũ không đổi).
  - `GET /api/van-phong`: phòng Điều phối có `sang` + `nhip_cuoi` (G9). Task 4 và lát 2f dựa vào hai khoá này.

- [ ] **Step 1: Viết test thất bại**

`tests/test_den_dieu_phoi.py` (mới):

```python
"""Đèn Điều phối suy từ nhịp hook máy A (spec 2 §5.5; plan 2e Task 1, G7–G9; review đợt 4 F11)."""
from contextlib import closing
from datetime import datetime, timedelta, timezone

from api_gia import tao_app_gia
from asgi_gia import goi
from tram.su_kien.kho import KhoSuKien, SuKien
from tram.suy.dieu_phoi import DU_AN_HE, LOAI, TAC_NHAN, can_ghi, den_dieu_phoi
from tram.suy.kho_nhip import doc_nhip

T = datetime(2026, 10, 15, 7, 0, tzinfo=timezone.utc)


def nhip(phut: float, su_kien: str = "Stop", phien: str = "a" * 16) -> SuKien:
    luc = (T + timedelta(minutes=phut)).isoformat().replace("+00:00", "Z")
    return SuKien(luc, DU_AN_HE, None, LOAI, TAC_NHAN, {"su_kien": su_kien, "phien": phien})


def luc(phut: float) -> datetime:
    return T + timedelta(minutes=phut)


def test_den_theo_phien_va_han_song_15_phut():
    assert den_dieu_phoi([], luc(0)) == {"sang": None, "nhip_cuoi": None}
    mot = [nhip(0)]
    assert den_dieu_phoi(mot, luc(10)) == {"sang": True, "nhip_cuoi": "2026-10-15T07:00:00Z"}
    assert den_dieu_phoi(mot, luc(15))["sang"] is True                                # đúng 15 phút: còn sáng
    assert den_dieu_phoi(mot, luc(15.5)) == {"sang": False, "nhip_cuoi": "2026-10-15T07:00:00Z"}
    hai = [nhip(5, "SessionEnd"), nhip(0, "UserPromptSubmit", "b" * 16)]                # mới → cũ
    assert den_dieu_phoi(hai, luc(6)) == {"sang": True, "nhip_cuoi": "2026-10-15T07:05:00Z"}   # phiên b còn
    assert den_dieu_phoi(hai, luc(16))["sang"] is False
    assert den_dieu_phoi([nhip(1, "SessionEnd"), nhip(0)], luc(2))["sang"] is False     # phiên duy nhất đã đóng
    assert den_dieu_phoi([nhip(2), nhip(1, "SessionEnd")], luc(3))["sang"] is True      # mở lại (resume)


def test_can_ghi_gop_60_giay_tru_khi_doi_trang_thai():
    assert can_ghi([], "a" * 16, "SessionStart", luc(0))
    ds = [nhip(0)]
    assert not can_ghi(ds, "a" * 16, "UserPromptSubmit", luc(0.5))
    assert can_ghi(ds, "a" * 16, "UserPromptSubmit", luc(1))
    assert can_ghi(ds, "b" * 16, "Stop", luc(0.1))                                      # phiên khác
    assert can_ghi(ds, "a" * 16, "SessionEnd", luc(0.1))                                # đang chạy → kết thúc
    het = [nhip(0, "SessionEnd")]
    assert not can_ghi(het, "a" * 16, "SessionEnd", luc(0.1))
    assert can_ghi(het, "a" * 16, "SessionStart", luc(0.1))                             # kết thúc → mở lại


def test_api_van_phong_tra_sang_that_cho_phong_dieu_phoi(tmp_path):
    app, pt = tao_app_gia(tmp_path, {})
    assert {p["ma"]: p for p in goi(app, "GET", "/api/van-phong").json()["phong"]}["dieu-phoi"] == {
        "ma": "dieu-phoi", "loai": "dieu_phoi", "ten": "Điều phối", "sang": None, "nhip_cuoi": None}
    kho = KhoSuKien(tmp_path / "sk.db")
    luc_ghi = kho.ghi(DU_AN_HE, LOAI, {"su_kien": "Stop", "phien": "c" * 16}, tac_nhan=TAC_NHAN)
    kho.close()
    dp = {p["ma"]: p for p in goi(app, "GET", "/api/van-phong").json()["phong"]}["dieu-phoi"]
    assert (dp["sang"], dp["nhip_cuoi"]) == (True, luc_ghi)
    pt.dong_ho = lambda: datetime.now(timezone.utc) + timedelta(minutes=20)              # quá hạn → xám
    dp = {p["ma"]: p for p in goi(app, "GET", "/api/van-phong").json()["phong"]}["dieu-phoi"]
    assert (dp["sang"], dp["nhip_cuoi"]) == (False, luc_ghi)                             # vẫn biết nhịp cuối


def test_hon_200_nhip_khong_lam_tat_phien_con_song(tmp_path):
    with closing(KhoSuKien(tmp_path / "sk.db")) as kho:
        kho.ghi(DU_AN_HE, LOAI, {"su_kien": "Stop", "phien": "a" * 16}, tac_nhan=TAC_NHAN)
        for i in range(201):
            kho.ghi(DU_AN_HE, LOAI, {"su_kien": "SessionEnd", "phien": f"{i:016x}"}, tac_nhan=TAC_NHAN)
        luc = datetime.now(timezone.utc)
        assert den_dieu_phoi(doc_nhip(kho, luc), luc)["sang"] is True
        sau = luc + timedelta(minutes=16)
        assert den_dieu_phoi(doc_nhip(kho, sau), sau)["sang"] is False                   # hết hạn ≠ chưa từng có
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_den_dieu_phoi.py -q`
Expected: FAIL — `1 error` (`ModuleNotFoundError: No module named 'tram.suy.dieu_phoi'`)

- [ ] **Step 3: Viết mã**

`tram/suy/dieu_phoi.py` (mới):

```python
"""Đèn phòng Điều phối của Văn phòng 3D (spec 2 §5.5; plan 2e G7–G9) — suy lúc đọc từ sự kiện `dieu_phoi.nhip`.

Hook của phiên Claude Code trên máy A gửi nhịp (`POST /api/dieu-phoi/nhip`, `tram/api/dieu_phoi.py`); mỗi nhịp là
`{su_kien: <tên sự kiện hook>, phien: <16 hex = sha256(session_id)[:16], tính trên máy A>}`, dự án `_tram`.
- `sang = None`: chưa từng có nhịp ("chưa có tín hiệu" — không bịa trạng thái, như 2c G4).
- `sang = True`: có ít nhất một phiên mà nhịp cuối KHÔNG phải `SessionEnd` và cách đây ≤ `HAN_SONG`.
- `sang = False`: mọi phiên đã `SessionEnd` hoặc nhịp cuối quá hạn (đèn xám "tắt đèn").
Ghi gộp (`can_ghi`): mỗi phiên tối đa một nhịp mỗi `GOP`, trừ khi đổi giữa "đang chạy" và "kết thúc".
Danh sách nhịp vào hai hàm là MỌI nhịp trong `HAN_SONG` (`tram/suy/kho_nhip.py::doc_nhip`), không cắt theo số dòng."""
from datetime import datetime, timedelta

LOAI = "dieu_phoi.nhip"
DU_AN_HE = "_tram"
TAC_NHAN = "dai-ca/may-a"
SU_KIEN_HOOK = ("SessionStart", "UserPromptSubmit", "Stop", "SessionEnd")
KET_THUC = "SessionEnd"
HAN_SONG = timedelta(minutes=15)
GOP = timedelta(seconds=60)


def _luc(s) -> datetime:
    return datetime.fromisoformat(s.luc.replace("Z", "+00:00"))


def _cuoi_theo_phien(nhip: list) -> dict:
    """`nhip` xếp mới → cũ (như `KhoSuKien.gan_day`) → nhịp mới nhất của từng phiên."""
    ra: dict = {}
    for s in nhip:
        ra.setdefault(s.du_lieu.get("phien"), s)
    return ra


def den_dieu_phoi(nhip: list, bay_gio: datetime) -> dict:
    """`{sang: bool | None, nhip_cuoi: ISO | None}` — `nhip_cuoi` là lúc ghi nhịp mới nhất (mọi phiên)."""
    if not nhip:
        return {"sang": None, "nhip_cuoi": None}
    sang = any(s.du_lieu.get("su_kien") != KET_THUC and bay_gio - _luc(s) <= HAN_SONG
               for s in _cuoi_theo_phien(nhip).values())
    return {"sang": sang, "nhip_cuoi": nhip[0].luc}


def can_ghi(nhip: list, phien: str, su_kien: str, bay_gio: datetime) -> bool:
    """Ghi khi phiên chưa có nhịp, khi đổi giữa kết thúc / đang chạy, hoặc nhịp cuối của phiên đã cũ ≥ `GOP`."""
    cu = _cuoi_theo_phien(nhip).get(phien)
    if cu is None or (cu.du_lieu.get("su_kien") == KET_THUC) != (su_kien == KET_THUC):
        return True
    return bay_gio - _luc(cu) >= GOP
```

`tram/suy/kho_nhip.py` (mới):

```python
"""Đọc nhịp đèn Điều phối từ kho sự kiện (plan 2e G9; review đợt 4 F11): MỌI nhịp trong `HAN_SONG`, không cắt theo
số dòng — nhiều phiên khác ghi dồn không đẩy được nhịp của phiên còn sống ra khỏi tập đọc. Không có nhịp nào trong
hạn thì trả nhịp mới nhất (nếu có) để phân biệt "đã hết hạn" (`sang: False`) với "chưa từng có" (`sang: None`).
Adapter duy nhất dùng `_CHON`/`_doc` nội bộ của `KhoSuKien`; tham số đều do mã đặt, không từ client."""
from tram.su_kien.kho import _CHON
from tram.suy.dieu_phoi import DU_AN_HE, HAN_SONG, LOAI


def doc_nhip(kho, luc):
    tu = (luc - HAN_SONG).strftime("%Y-%m-%dT%H:%M:%SZ")
    ds = kho._doc(
        f"{_CHON} WHERE du_an=? AND loai=? AND luc>=? ORDER BY id DESC",
        (DU_AN_HE, LOAI, tu),
    )
    return ds or kho.gan_day(DU_AN_HE, LOAI, 1)
```

`tram/suy/van_phong.py`, `tram/api/van_phong.py`:

```diff
diff --git a/tram/api/van_phong.py b/tram/api/van_phong.py
index 377c77a..14df6da 100644
--- a/tram/api/van_phong.py
+++ b/tram/api/van_phong.py
@@ -9,6 +9,8 @@ from fastapi import APIRouter, Request
 from tram.api.tuyen_doc import phe_duyet
 from tram.chu import estop
 from tram.phieu.trang_thai import trang_thai_khe
+from tram.suy.dieu_phoi import den_dieu_phoi
+from tram.suy.kho_nhip import doc_nhip
 from tram.suy.nhan_vat import nhan_vat
 from tram.suy.van_phong import cac_phong, suc_khoe
 
@@ -25,5 +27,8 @@ def r_van_phong(request: Request) -> dict:
         with closing(pt.mo_kho_phieu()) as kho:
             nv = nhan_vat(kho, trang_thai_khe(kho, bay_gio=pt.dong_ho(), ch=pt.cau_hinh), cac_du_an)
     sk = suc_khoe(estop_bat=estop.dang_bat(), muc=pd["muc"], loi_doc=pd["loi"], nhan_vat=nv)
-    return {"phong": cac_phong(cac_du_an, so_cho=pd["so"], suc_khoe=sk), "nhan_vat": nv,
+    with closing(pt.mo_kho()) as kho:                       # plan 2e: đèn Điều phối từ nhịp hook máy A
+        luc = pt.dong_ho()
+        dp = den_dieu_phoi(doc_nhip(kho, luc), luc)
+    return {"phong": cac_phong(cac_du_an, so_cho=pd["so"], suc_khoe=sk, dieu_phoi=dp), "nhan_vat": nv,
             "kho_phieu": pt.mo_kho_phieu is not None}
diff --git a/tram/suy/van_phong.py b/tram/suy/van_phong.py
index 88ba90b..9422b09 100644
--- a/tram/suy/van_phong.py
+++ b/tram/suy/van_phong.py
@@ -29,9 +29,9 @@ def suc_khoe(*, estop_bat: bool, muc: list[dict], loi_doc: dict[str, str], nhan_
     return {"mau": mau, "ly_do": (do + vang)[:GIU_TOI_DA]}
 
 
-def cac_phong(cac_du_an: list[str], *, so_cho: int, suc_khoe: dict) -> list[dict]:
-    """Bốn phòng cố định rồi mỗi dự án đã `them` một phòng. Điều phối: chưa có nguồn tín hiệu "phiên điều phối
-    trên máy A" ở spec/plan nào → `sang: None` (plan 2c G4, mục "Cần sửa spec sau")."""
-    them = {"dieu-phoi": {"sang": None}, "giam-doc": {"so_cho": so_cho}, "may-chu": {"suc_khoe": suc_khoe}}
+def cac_phong(cac_du_an: list[str], *, so_cho: int, suc_khoe: dict, dieu_phoi: dict | None = None) -> list[dict]:
+    """Bốn phòng cố định rồi mỗi dự án đã `them` một phòng. Điều phối: `dieu_phoi` = `{sang, nhip_cuoi}` suy từ
+    nhịp hook máy A (`tram/suy/dieu_phoi.py`, plan 2e); không truyền → `sang: None` ("chưa có tín hiệu", 2c G4)."""
+    them = {"dieu-phoi": dieu_phoi or {"sang": None}, "giam-doc": {"so_cho": so_cho}, "may-chu": {"suc_khoe": suc_khoe}}
     ra = [{"ma": ma, "loai": loai, "ten": ten, **them.get(ma, {})} for ma, loai, ten in PHONG_CO_DINH]
     return ra + [{"ma": f"du-an:{t}", "loai": "du_an", "ten": t, "du_an": t} for t in cac_du_an]
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_den_dieu_phoi.py tests/test_suy_van_phong.py tests/test_api_van_phong.py -q`
Expected: `8 passed`

Run: `uv run pytest -q`
Expected: `N₀ + 4 passed` (1998 nếu chạy riêng trên `main`)

- [ ] **Step 5: Commit**

```bash
git add tram/suy/dieu_phoi.py tram/suy/kho_nhip.py tram/suy/van_phong.py tram/api/van_phong.py tests/test_den_dieu_phoi.py
git commit -m "feat(suy): đèn Điều phối suy từ nhịp hook máy A — hạn sống 15 phút, theo phiên, đọc mọi nhịp trong hạn; /api/van-phong trả sang + nhip_cuoi (spec 2 §5.5; plan 2e G7–G9, F11; bs-urj.7)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 2: Đường ghi `POST /api/dieu-phoi/nhip` — kênh, danh tính, mã điều phối, tần suất, kích thước, gộp nguyên tử

**Độ khó:** `vua` · **Đợt:** 2 · **Song song với:** — · **Phải xong trước:** Task 1, Task 6

**Files:**
- Create: `tram/api/dieu_phoi.py`
- Modify: `tram/api/van_phong.py` (import, `router.include_router`)
- Test: `tests/test_api_dieu_phoi.py`, `tests/test_nhip_nguyen_tu.py` (mới)

**Interfaces:**
- Consumes: `yeu_cau_ghi`, `kenh_hop_le`, `KenhUnix` (bảng "Phụ thuộc đã có"); `doc_bam`, `ghi_bam` của `tram/chu/ma_dieu_phoi.py` (Task 6); `DU_AN_HE`, `LOAI`, `TAC_NHAN`, `can_ghi`, `doc_nhip` (Task 1); `KhoSuKien._db` (chỉ trong `ghi_nhip`, để mở `BEGIN IMMEDIATE`).
- Produces:
  - `tram/api/dieu_phoi.py`: `router` (`POST /api/dieu-phoi/nhip` → `{"ghi": bool}`); `TOI_DA_BYTE = 512`; `TOI_DA_LOI_GOI, CUA_SO_GIAY = 30, 60.0`; `ThanNhipDieuPhoi`; `GioiHan(toi_da=30, cua_so=60.0, dong_ho=time.monotonic).cho_phep() -> bool` (test gán `app.state.gioi_han_dieu_phoi`); `kiem_ma_dieu_phoi(request)`; `doc_than(request)`; `ghi_nhip(pt, than) -> bool` (nguyên tử). File 110 dòng nên `GioiHan` vẫn ở đây; vượt ~120 thì tách sang module riêng.
  - Hợp đồng HTTP ở mục "Hợp đồng" (G4, G5, G12). Task 3 (hook) gửi đúng thân và header này.

- [ ] **Step 1: Viết test thất bại**

`tests/test_api_dieu_phoi.py` (mới):

```python
"""`POST /api/dieu-phoi/nhip` — đường ghi riêng của hook máy A (spec 2 §4, §5.5; plan 2e Task 2, G3–G13, G23)."""
from contextlib import closing

from api_gia import DAI_CA, MAY_B, tao_app_gia
from asgi_gia import goi
from tram.api.app import CAC_TUYEN
from tram.api.dieu_phoi import GioiHan
from tram.api.kenh_ghi import KenhUnix
from tram.chu import estop
from tram.chu.ma_dieu_phoi import ghi_bam
from tram.nho import ma_dai_ca
from tho_api_gia import tao_tram
from tram.su_kien.kho import KhoSuKien

MA, MA_DAI_CA = "ma-dieu-phoi-" + "z" * 40, "ma-dai-ca-" + "y" * 40
DUONG = "/api/dieu-phoi/nhip"
H = {**DAI_CA, "Authorization": f"Bearer {MA}"}
STOP = {"su_kien": "Stop", "phien": "a" * 16}
THAN = {"/api/ghep-may": {"ma": MA[:64]}, "/api/phieu/kiem": {"du_an": "hr", "mo_ta": ""}}   # qua lược đồ → xác thực


def dung(tmp_path, *, dat_ma=True):
    ma_dai_ca.ghi_bam(ma_dai_ca.bam(MA_DAI_CA))            # ~/.tram tạm (conftest: TRAM_HOME); mã Đại ca luôn có
    if dat_ma:
        ghi_bam(ma_dai_ca.bam(MA))
    return tao_app_gia(tmp_path, {})[0]


def nhip_da_ghi(tmp_path) -> list:
    kho = KhoSuKien(tmp_path / "sk.db")
    try:
        return kho.gan_day("_tram", "dieu_phoi.nhip", 10)
    finally:
        kho.close()


def cac_tuyen_ghi(router):
    for r in router.routes:
        if getattr(r, "original_router", None) is not None:                             # router con (include_router)
            yield from cac_tuyen_ghi(r.original_router)
        elif set(getattr(r, "methods", None) or ()) - {"GET", "HEAD"}:
            yield r


def test_nhip_hop_le_ghi_gop_va_den_sang(tmp_path):
    app = dung(tmp_path)
    r = goi(app, "POST", DUONG, json_body=STOP, headers=H)
    assert (r.status, r.json()) == (200, {"ghi": True})
    assert "frame-ancestors 'none'" in r.headers["content-security-policy"]                # header an toàn §4 mục 6
    assert goi(app, "POST", DUONG, json_body={**STOP, "su_kien": "UserPromptSubmit"}, headers=H).json() == {
        "ghi": False}                                                                    # gộp trong 60 giây
    (sk,) = nhip_da_ghi(tmp_path)
    assert (sk.du_an, sk.bead_id, sk.tac_nhan, sk.du_lieu) == ("_tram", None, "dai-ca/may-a", STOP)
    dp = {p["ma"]: p for p in goi(app, "GET", "/api/van-phong").json()["phong"]}["dieu-phoi"]
    assert dp["sang"] is True and dp["nhip_cuoi"] == sk.luc
    assert goi(app, "POST", DUONG, json_body={**STOP, "su_kien": "SessionEnd"}, headers=H).json() == {"ghi": True}
    assert {p["ma"]: p for p in goi(app, "GET", "/api/van-phong").json()["phong"]}["dieu-phoi"]["sang"] is False


def test_tu_choi_khi_thieu_hoac_sai_bang_chung(tmp_path):
    app = dung(tmp_path)
    ca = {"không mã": DAI_CA, "sai mã": {**H, "Authorization": "Bearer " + "x" * 50},
          "mã Đại ca": {**H, "Authorization": f"Bearer {MA_DAI_CA}"}, "mã không Bearer": {**H, "Authorization": MA},
          "thiếu header Tailscale": {k: v for k, v in H.items() if k != "Tailscale-User-Login"},
          "login lạ": {**H, "Tailscale-User-Login": "ke-la@example.com"},
          "thiếu X-Tram": {k: v for k, v in H.items() if k != "X-Tram"},
          "Origin lạ": {**H, "Origin": "https://evil.example"}}
    ma_loi = {ten: goi(app, "POST", DUONG, json_body=STOP, headers=h) for ten, h in ca.items()}
    assert {ten: r.status for ten, r in ma_loi.items()} == {
        "không mã": 401, "sai mã": 401, "mã Đại ca": 401, "mã không Bearer": 401, "thiếu header Tailscale": 403,
        "login lạ": 403, "thiếu X-Tram": 403, "Origin lạ": 403}
    assert all(MA not in r.body.decode() and MA_DAI_CA not in r.body.decode() for r in ma_loi.values())
    assert goi(app, "POST", DUONG, json_body=STOP, headers={**H, "host": "evil.example"}).status == 421
    app.state.kenh_ghi = "unix-socket"                                                  # G29 3a-2: TCP bị chặn
    assert goi(app, "POST", DUONG, json_body=STOP, headers=H).status == 403
    assert nhip_da_ghi(tmp_path) == []
    assert goi(KenhUnix(app), "POST", DUONG, json_body=STOP, headers=H).status == 200


def test_chua_dat_ma_dieu_phoi_thi_tu_choi_moi_loi_goi(tmp_path):
    app = dung(tmp_path, dat_ma=False)
    for h in (H, {**H, "Authorization": f"Bearer {MA_DAI_CA}"}):                       # mã Đại ca không thay được
        r = goi(app, "POST", DUONG, json_body=STOP, headers=h)
        assert r.status == 401 and "dat-ma-dieu-phoi" in r.json()["detail"]
    assert nhip_da_ghi(tmp_path) == []


def test_ma_dieu_phoi_khong_mo_route_ghi_nao_khac(tmp_path):
    dung(tmp_path)
    t = tao_tram(tmp_path, token_noi_bo="tok-noi-bo", dang_ky=False)        # có kho phiếu + token máy thật
    chi_ma = {"Authorization": f"Bearer {MA}", "X-Tram": "1", "Origin": f"https://{MAY_B}"}
    tuyen = [r for rt in CAC_TUYEN for r in cac_tuyen_ghi(rt)]
    assert len(tuyen) > 20 and DUONG in {r.path for r in tuyen}
    ma = {f"{pt} {r.path}": goi(t.app, pt, r.path.replace("{", "").replace("}", ""), headers=chi_ma,
                                 json_body=THAN.get(r.path, {})).status
          for r in tuyen if r.path != DUONG for pt in sorted(r.methods - {"HEAD"})}
    assert {k: v for k, v in ma.items() if v not in (401, 403)} == {}
    with closing(KhoSuKien(tmp_path / "sk.db")) as kho:
        assert {s.loai for s in kho.sau_id(0, 100)} == {"may.ghep_sai"}                  # chỉ nhật ký từ chối
    assert not estop.dang_bat() and goi(t.app, "GET", DUONG, headers=H).status == 405


def test_gioi_han_kich_thuoc_luoc_do_va_tan_suat(tmp_path):
    app = dung(tmp_path)
    to = goi(app, "POST", DUONG, json_body={"su_kien": "Stop", "phien": "a" * 600}, headers=H)
    khai = goi(app, "POST", DUONG, json_body=STOP, headers={**H, "content-length": "10000"})
    assert (to.status, khai.status) == (413, 413)
    for than in ({"su_kien": "PreToolUse", "phien": "a" * 16}, {**STOP, "phien": "A" * 16}, {**STOP, "cwd": "/x"},
                 {"su_kien": "Stop"}):
        assert goi(app, "POST", DUONG, json_body=than, headers=H).status == 422
    t = [0.0]
    app.state.gioi_han_dieu_phoi = GioiHan(toi_da=3, dong_ho=lambda: t[0])
    assert [goi(app, "POST", DUONG, json_body=STOP, headers=h).status for h in (DAI_CA, H, H, H)] == [
        401, 200, 200, 429]                                                              # lời gọi hỏng cũng tính
    t[0] = 60.0
    assert goi(app, "POST", DUONG, json_body=STOP, headers=H).status == 200
```

`tests/test_nhip_nguyen_tu.py` (mới) — bản sửa F10 của Codex, đổi cách ép tranh chấp: lời gọi đầu dừng 0,3 giây **sau khi đọc, trước khi ghi**; lời gọi sau bắt đầu trong khoảng đó. Bản cũ của review đặt `Barrier` trong `gan_day(…, 200)`, chỉ ép được trên mã cũ; với mã mới nó không chạy tới nên không chứng minh gì. Cách mới ép được trên cả hai, nên fail khi bỏ khoá (Step 4b):

```python
"""Gộp nhịp nguyên tử giữa hai kết nối (plan 2e Task 2; review đợt 4 F10) — không gọi mạng, SQLite tạm."""
import time
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from datetime import datetime, timezone
from threading import Event
from types import SimpleNamespace

from tram.api import dieu_phoi
from tram.api.dieu_phoi import ThanNhipDieuPhoi, ghi_nhip
from tram.su_kien.kho import KhoSuKien
from tram.suy.dieu_phoi import DU_AN_HE, LOAI


def test_ghi_gop_nguyen_tu_giua_hai_ket_noi(tmp_path, monkeypatch):
    p = tmp_path / "sk.db"
    pt = SimpleNamespace(mo_kho=lambda: KhoSuKien(p), dong_ho=lambda: datetime.now(timezone.utc))
    than = ThanNhipDieuPhoi(su_kien="Stop", phien="a" * 16)
    doc_that, da_doc = dieu_phoi.doc_nhip, Event()

    def doc_roi_dung(kho, luc):
        ds = doc_that(kho, luc)
        if not da_doc.is_set():                    # lời gọi đầu: đã đọc "chưa có", dừng 0,3 s TRƯỚC khi ghi
            da_doc.set()
            time.sleep(0.3)
        return ds

    monkeypatch.setattr(dieu_phoi, "doc_nhip", doc_roi_dung)
    with ThreadPoolExecutor(max_workers=2) as ex:
        dau = ex.submit(ghi_nhip, pt, than)
        assert da_doc.wait(5)
        sau = ex.submit(ghi_nhip, pt, than)          # bản không khoá: đọc "chưa có" trong 0,3 s đó → ghi đôi
        assert sorted([dau.result(5), sau.result(15)]) == [False, True]
    with closing(KhoSuKien(p)) as kho:
        assert len(kho.gan_day(DU_AN_HE, LOAI, 10)) == 1
    assert ghi_nhip(pt, than) is False               # nhánh không ghi: rollback, đóng kết nối
    with closing(KhoSuKien(p)) as kho:
        kho._db.execute("PRAGMA busy_timeout=0")
        kho.ghi(DU_AN_HE, "thu.khoa", {})              # không còn ai giữ khoá ghi: ghi ngay, không "database is locked"
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_api_dieu_phoi.py tests/test_nhip_nguyen_tu.py -q`
Expected: FAIL — `2 errors` (`ModuleNotFoundError: No module named 'tram.api.dieu_phoi'`)

- [ ] **Step 3: Viết mã**

`tram/api/dieu_phoi.py` (mới):

```python
"""`POST /api/dieu-phoi/nhip` (spec 2 §5.5; plan 2e G3–G13, G23): hook phiên điều phối trên máy A báo nhịp → sự kiện
`dieu_phoi.nhip` của dự án `_tram`. ĐƯỜNG GHI HẸP: chỉ ghi đúng loại sự kiện này; không chạm beads, phiếu, khe, memory.

Kiểm theo thứ tự, rẻ trước: kênh ghi (`cach_ly.kenh_ghi`, 403) → tần suất (429) → danh tính Tailscale + `X-Tram` +
`Origin` (`yeu_cau_ghi` y hệt API ghi dashboard, 403) → mã điều phối (`Authorization: Bearer`, so sha256 với
`dieu_phoi_ma_sha256` — mã RIÊNG theo D24, không phải mã Đại ca; header Tailscale giả được từ TCP localhost, mã thì
không; 401) → thân ≤ 512 byte (413) đúng lược đồ (422). Mã điều phối KHÔNG mở route nào khác: API ghi dashboard bỏ
qua `Authorization`; memory service chỉ so với `ma_dai_ca_sha256`. Thông báo lỗi không chứa mã.
Gộp ghi nguyên tử (review đợt 4 F10): `BEGIN IMMEDIATE` trước khi đọc, nên hai lời gọi song song không cùng ghi."""
import hashlib
import hmac
import time
from collections import deque
from contextlib import closing
from typing import Literal

from fastapi import APIRouter, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from tram.api.bao_mat import yeu_cau_ghi
from tram.api.kenh_ghi import kenh_hop_le
from tram.chu.ma_dieu_phoi import doc_bam
from tram.suy.dieu_phoi import DU_AN_HE, LOAI, TAC_NHAN, can_ghi
from tram.suy.kho_nhip import doc_nhip

router = APIRouter()
TOI_DA_BYTE = 512
TOI_DA_LOI_GOI, CUA_SO_GIAY = 30, 60.0


class ThanNhipDieuPhoi(BaseModel):
    model_config = ConfigDict(extra="forbid")
    su_kien: Literal["SessionStart", "UserPromptSubmit", "Stop", "SessionEnd"]
    phien: str = Field(pattern=r"^[0-9a-f]{16}$")


class GioiHan:
    """Cửa sổ trượt trong bộ nhớ tiến trình tram-api (mất khi khởi động lại — chấp nhận, G10)."""

    def __init__(self, toi_da: int = TOI_DA_LOI_GOI, cua_so: float = CUA_SO_GIAY, dong_ho=time.monotonic):
        self.toi_da, self.cua_so, self.dong_ho, self.moc = toi_da, cua_so, dong_ho, deque()

    def cho_phep(self) -> bool:
        bay_gio = self.dong_ho()
        while self.moc and bay_gio - self.moc[0] >= self.cua_so:
            self.moc.popleft()
        if len(self.moc) >= self.toi_da:
            return False
        self.moc.append(bay_gio)
        return True


def gioi_han(request: Request) -> GioiHan:
    gh = getattr(request.app.state, "gioi_han_dieu_phoi", None)
    if gh is None:
        gh = request.app.state.gioi_han_dieu_phoi = GioiHan()
    return gh


def kiem_ma_dieu_phoi(request: Request) -> None:
    gt = request.headers.getlist("authorization")
    ma = gt[0].removeprefix("Bearer ") if len(gt) == 1 and gt[0].startswith("Bearer ") else ""
    bam = doc_bam()                                  # đọc mỗi lời gọi: `tram chu dat-ma-dieu-phoi` có hiệu lực ngay
    gui = hashlib.sha256(ma.encode()).hexdigest()
    if not ma or not bam or not hmac.compare_digest(gui.encode(), bam.encode()):
        raise HTTPException(401, "Thiếu hoặc sai mã điều phối (hoặc trạm chưa đặt mã — tram chu dat-ma-dieu-phoi)")


async def doc_than(request: Request) -> ThanNhipDieuPhoi:
    cl = request.headers.get("content-length")
    if cl is not None and (not cl.isdigit() or int(cl) > TOI_DA_BYTE):
        raise HTTPException(413, f"Thân quá {TOI_DA_BYTE} byte")
    than = b""
    async for phan in request.stream():
        than += phan
        if len(than) > TOI_DA_BYTE:
            raise HTTPException(413, f"Thân quá {TOI_DA_BYTE} byte")
    try:
        return ThanNhipDieuPhoi.model_validate_json(than)
    except ValidationError:
        raise HTTPException(422, "Thân phải là {su_kien, phien} đúng dạng") from None


def ghi_nhip(pt, than: ThanNhipDieuPhoi) -> bool:
    """Đọc + quyết + ghi trong MỘT giao dịch ghi (`BEGIN IMMEDIATE`): lời gọi thứ hai chờ khoá (busy_timeout của
    `mo_ket_noi`) rồi mới đọc, nên thấy nhịp vừa ghi. `KhoSuKien.ghi` commit giao dịch này; nhánh không ghi rollback."""
    with closing(pt.mo_kho()) as kho:
        kho._db.execute("BEGIN IMMEDIATE")
        try:
            luc = pt.dong_ho()
            if not can_ghi(doc_nhip(kho, luc), than.phien, than.su_kien, luc):
                return False
            kho.ghi(DU_AN_HE, LOAI, {"su_kien": than.su_kien, "phien": than.phien}, tac_nhan=TAC_NHAN)
            return True
        finally:
            if kho._db.in_transaction:
                kho._db.rollback()


@router.post("/api/dieu-phoi/nhip")
async def nhip_dieu_phoi(request: Request) -> dict:
    if not kenh_hop_le(request):
        raise HTTPException(403, "API ghi chỉ nhận qua kênh đã xác thực (cach_ly.kenh_ghi)")
    if not gioi_han(request).cho_phep():
        raise HTTPException(429, "Quá nhiều nhịp — thử lại sau")
    yeu_cau_ghi(request)
    await run_in_threadpool(kiem_ma_dieu_phoi, request)
    than = await doc_than(request)
    return {"ghi": await run_in_threadpool(ghi_nhip, request.app.state.pt, than)}
```

`tram/api/van_phong.py` (gắn router — không sửa `app.py`, G13):

```diff
diff --git a/tram/api/van_phong.py b/tram/api/van_phong.py
index 14df6da..fb7d3fd 100644
--- a/tram/api/van_phong.py
+++ b/tram/api/van_phong.py
@@ -6,6 +6,7 @@ from contextlib import closing
 
 from fastapi import APIRouter, Request
 
+from tram.api import dieu_phoi
 from tram.api.tuyen_doc import phe_duyet
 from tram.chu import estop
 from tram.phieu.trang_thai import trang_thai_khe
@@ -15,6 +16,7 @@ from tram.suy.nhan_vat import nhan_vat
 from tram.suy.van_phong import cac_phong, suc_khoe
 
 router = APIRouter()
+router.include_router(dieu_phoi.router)          # plan 2e: POST /api/dieu-phoi/nhip — đăng ký qua đây, không sửa app.py
 
 
 @router.get("/api/van-phong")
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_api_dieu_phoi.py tests/test_nhip_nguyen_tu.py tests/test_kenh_ghi.py tests/test_bao_mat.py tests/test_api_van_phong.py -q`
Expected: `19 passed`

Run: `uv run pytest -q`
Expected: `N₀ + 22 passed` (2016 trên bản dựng thử, sau đợt 1)

- [ ] **Step 4b: Chứng minh khoá có tác dụng (không commit)** — `cp tram/api/dieu_phoi.py ../dieu_phoi.bak`, rồi tạm đổi dòng `kho._db.execute("BEGIN IMMEDIATE")` trong `ghi_nhip` thành `pass`. Run: `uv run pytest tests/test_nhip_nguyen_tu.py -q`. Expected: `1 failed` với `assert [True, True] == [False, True]` (hai lời gọi cùng ghi). Trả lại: `cp ../dieu_phoi.bak tram/api/dieu_phoi.py`, chạy lại thấy `1 passed`.

- [ ] **Step 5: Commit**

```bash
git add tram/api/dieu_phoi.py tram/api/van_phong.py tests/test_api_dieu_phoi.py tests/test_nhip_nguyen_tu.py
git commit -m "feat(api): POST /api/dieu-phoi/nhip — đường ghi riêng cho hook máy A: kênh ghi + danh tính/CSRF dashboard + mã điều phối riêng, 30 lời gọi/phút, thân ≤ 512 byte, gộp nguyên tử, chỉ ghi dieu_phoi.nhip (spec 2 §4, §5.5; plan 2e G3–G13, D24, F10; bs-urj.7)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 3: Hook máy A — script, `settings.mau.json`, hướng dẫn cài

**Độ khó:** `vua` · **Đợt:** 1 · **Song song với:** Task 1, 4, 6 · **Phải xong trước:** —

**Files:**
- Create: `may-a/hook-dieu-phoi/hook_dieu_phoi.py`, `may-a/hook-dieu-phoi/settings.mau.json`, `may-a/hook-dieu-phoi/HUONG-DAN.md`
- Test: `tests/test_hook_dieu_phoi.py` (mới)

**Interfaces:**
- Consumes: hợp đồng HTTP của Task 2 (mục "Hợp đồng"); lệnh `tram chu dat-ma-dieu-phoi` của Task 6 (chỉ nhắc trong HUONG-DAN). Không import gì từ `tram/` — script chạy trên máy A không có ben-station.
- Produces: `SU_KIEN`, `KEYCHAIN = "tram-dieu-phoi-ma"`, `DUONG`, `TIMEOUT_GIAY = 2`, `HAN_TOAN_BO = 4`; `KhongChuyenHuong`; `mo_mac_dinh()`; `lay_ma(env, chay=subprocess.run) -> str | None`; `goc_tram(url) -> str | None`; `dung_yeu_cau(goc, ma, su_kien, session_id) -> urllib.request.Request`; `chay(stdin, env, mo=None, lay=lay_ma) -> 0`; `chay_co_han(stdin, env, han=HAN_TOAN_BO, viec=None) -> 0`.

- [ ] **Step 1: Viết test thất bại**

`tests/test_hook_dieu_phoi.py` (mới):

```python
"""Hook đèn Điều phối trên máy A (plan 2e Task 3, G15–G19, G23): không mạng thật, không Keychain thật, không đụng
~/.claude thật."""
import ast
import hashlib
import importlib.util
import io
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request

from tram.duong_dan import goc_repo

THU_MUC = goc_repo() / "may-a" / "hook-dieu-phoi"
KICH_BAN = THU_MUC / "hook_dieu_phoi.py"
MA, URL = "ma-dieu-phoi-" + "z" * 40, "https://may-b.tail.ts.net"
_spec = importlib.util.spec_from_file_location("hook_dieu_phoi", KICH_BAN)
hook = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hook)


class MoGia:
    def __init__(self, loi=None):
        self.goi, self.loi = [], loi

    def __call__(self, req, timeout):
        self.goi.append((req, timeout))
        if self.loi:
            raise self.loi
        return io.BytesIO(b'{"ghi": true}')


def vao(su_kien="UserPromptSubmit", **them):
    return io.StringIO(json.dumps({"hook_event_name": su_kien, "session_id": "phien-1", "cwd": "/Users/x/hr",
                                   "prompt": "lương tháng 10 của khách", **them}))


def test_gui_dung_yeu_cau_va_khong_lo_noi_dung_phien():
    mo = MoGia()
    assert hook.chay(vao(), {"TRAM_DIEU_PHOI_URL": URL + "/"}, mo=mo, lay=lambda _: MA) == 0
    ((req, timeout),) = mo.goi
    assert (req.full_url, req.get_method(), timeout) == (URL + "/api/dieu-phoi/nhip", "POST", 2)
    h = {k.lower(): v for k, v in req.header_items()}
    assert (h["authorization"], h["x-tram"], h["origin"]) == (f"Bearer {MA}", "1", URL)
    assert json.loads(req.data) == {"su_kien": "UserPromptSubmit",
                                    "phien": hashlib.sha256(b"phien-1").hexdigest()[:16]}
    assert b"luong" not in req.data and "lương".encode() not in req.data and b"/Users" not in req.data


def test_im_lang_khi_loi_mang_dau_vao_la_hoac_thieu_cau_hinh():
    env = {"TRAM_DIEU_PHOI_URL": URL}
    for loi in (urllib.error.URLError("tắt Tailscale"), TimeoutError(), urllib.error.HTTPError(URL, 401, "x", {},
                                                                                                None)):
        assert hook.chay(vao("Stop"), env, mo=MoGia(loi), lay=lambda _: MA) == 0
    mo = MoGia()
    for stdin, e in ((io.StringIO("không phải json"), env), (io.StringIO("[1]"), env), (vao("PreToolUse"), env),
                     (vao(session_id=7), env), (vao(), {"TRAM_DIEU_PHOI_URL": "http://may-b"}),
                     (vao(), {"TRAM_DIEU_PHOI_URL": URL + "/api"}),
                     (vao(), {"TRAM_DIEU_PHOI_URL": "https://u@may-b"}), (vao(), {})):
        assert hook.chay(stdin, e, mo=mo, lay=lambda _: MA) == 0
    assert hook.chay(vao(), env, mo=mo, lay=lambda _: None) == 0
    assert mo.goi == []


def test_lay_ma_tu_keychain_rieng_khong_qua_argv():
    goi = []

    def chay(argv, **kw):
        goi.append(argv)
        return subprocess.CompletedProcess(argv, 0, MA + "\n", "")
    assert hook.lay_ma({"TRAM_DIEU_PHOI_MA": " " + MA + " "}, chay=chay) == MA and goi == []
    assert hook.lay_ma({"TRAM_DAI_CA_MA": "ma-dai-ca-" + "y" * 40}, chay=chay) == MA      # không dùng mã Đại ca
    assert goi == [["/usr/bin/security", "find-generic-password", "-s", "tram-dieu-phoi-ma", "-w"]]
    assert hook.lay_ma({}, chay=lambda a, **k: subprocess.CompletedProcess(a, 44, "", "khong co")) is None

    def hong(argv, **kw):
        raise FileNotFoundError(argv[0])
    assert hook.lay_ma({}, chay=hong) is None


def test_khong_proxy_khong_theo_chuyen_huong(monkeypatch):
    monkeypatch.setenv("HTTPS_PROXY", "http://proxy.example:3128")
    assert any(isinstance(x, urllib.request.ProxyHandler) for x in urllib.request.build_opener().handlers)
    xu_ly = hook.mo_mac_dinh().__self__.handlers
    assert not any(isinstance(x, urllib.request.ProxyHandler) for x in xu_ly)               # bỏ proxy của môi trường
    assert [type(x) for x in xu_ly if isinstance(x, urllib.request.HTTPRedirectHandler)] == [
        hook.KhongChuyenHuong]
    assert hook.KhongChuyenHuong().redirect_request(None, None, 302, "x", {}, "https://khac/") is None


def test_han_toan_bo_khi_mot_buoc_treo():
    bat_dau = time.monotonic()
    assert hook.chay_co_han(vao(), {}, han=0.2, viec=lambda *_: time.sleep(5)) == 0
    assert time.monotonic() - bat_dau < 1
    assert hook.HAN_TOAN_BO < 5                                                            # dưới `timeout: 5`


def test_chay_that_thoat_0_khong_in_gi_khi_tram_khong_voi_toi(tmp_path):
    env = {"PATH": "/usr/bin:/bin", "HOME": str(tmp_path), "TRAM_DIEU_PHOI_URL": "https://127.0.0.1:9",
           "TRAM_DIEU_PHOI_MA": MA}                  # cổng 9 cục bộ: bị từ chối ngay, không ra mạng; không Keychain
    bat_dau = time.monotonic()
    kq = subprocess.run([sys.executable, "-I", str(KICH_BAN)], input=vao().getvalue(), capture_output=True,
                        text=True, env=env, timeout=10)
    assert (kq.returncode, kq.stdout, kq.stderr) == (0, "", "") and time.monotonic() - bat_dau < 5


def test_python_3_9_va_mau_settings():
    ast.parse(KICH_BAN.read_text(encoding="utf-8"), feature_version=(3, 9))
    mau = json.loads((THU_MUC / "settings.mau.json").read_text(encoding="utf-8"))
    assert set(mau["hooks"]) == {"SessionStart", "UserPromptSubmit", "Stop", "SessionEnd"}
    for nhom in mau["hooks"].values():
        ((lenh,),) = [x["hooks"] for x in nhom]
        assert "hook_dieu_phoi.py" in lenh["command"] and 0 < lenh["timeout"] <= 5
    assert set(mau["env"]) == {"TRAM_DIEU_PHOI_URL"} and mau["env"]["TRAM_DIEU_PHOI_URL"].startswith("https://")
    huong_dan = (THU_MUC / "HUONG-DAN.md").read_text(encoding="utf-8")
    assert "tram-dieu-phoi-ma" in huong_dan and "dat-ma-dieu-phoi" in huong_dan and "Terminal.app" in huong_dan
    assert "tram-dai-ca-ma" not in huong_dan and "Gộp" in huong_dan
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_hook_dieu_phoi.py -q`
Expected: FAIL — `1 error` (`FileNotFoundError: … may-a/hook-dieu-phoi/hook_dieu_phoi.py`)

- [ ] **Step 3: Viết mã**

`may-a/hook-dieu-phoi/hook_dieu_phoi.py` (mới):

```python
#!/usr/bin/env python3
"""Hook Claude Code trên MÁY A: báo nhịp phiên điều phối về trạm (spec 2 §5.5; plan 2e Task 3, G15–G19, G23).

Đọc JSON sự kiện hook từ stdin, chỉ lấy `hook_event_name` và `session_id`; gửi `POST <TRAM_DIEU_PHOI_URL>/api/
dieu-phoi/nhip` thân `{su_kien, phien}` với `phien` = 16 hex đầu của sha256(session_id). KHÔNG gửi prompt, cwd,
đường transcript. Mã: MÃ ĐIỀU PHỐI riêng (D24) trong Keychain máy A, dịch vụ `tram-dieu-phoi-ma` — không phải mã Đại
ca, không bao giờ nằm trong file, argv hay log; biến `TRAM_DIEU_PHOI_MA` chỉ để kiểm nhanh. Không bao giờ chặn phiên:
timeout mỗi thao tác (Keychain, HTTP) 2 giây, cả hook tối đa `HAN_TOAN_BO` = 4 giây rồi thoát (dưới `timeout: 5` của
settings); mọi lỗi im lặng, luôn thoát 0, không in gì (stdout của hook UserPromptSubmit/SessionStart bị đưa vào ngữ
cảnh phiên). Không dùng proxy, không theo chuyển hướng: `Authorization` chỉ tới đúng máy B. python3 ≥ 3.9 của macOS,
chỉ thư viện chuẩn."""
import hashlib
import json
import os
import subprocess
import sys
import threading
import urllib.parse
import urllib.request

SU_KIEN = ("SessionStart", "UserPromptSubmit", "Stop", "SessionEnd")
KEYCHAIN = "tram-dieu-phoi-ma"
DUONG = "/api/dieu-phoi/nhip"
TIMEOUT_GIAY = 2
HAN_TOAN_BO = 4


class KhongChuyenHuong(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None                                   # 3xx → lỗi (im lặng), không mang mã sang chỗ khác


def mo_mac_dinh():
    return urllib.request.build_opener(urllib.request.ProxyHandler({}), KhongChuyenHuong()).open


def lay_ma(env, chay=subprocess.run):
    ma = env.get("TRAM_DIEU_PHOI_MA", "").strip()
    if ma:
        return ma
    try:
        kq = chay(["/usr/bin/security", "find-generic-password", "-s", KEYCHAIN, "-w"], capture_output=True,
                  text=True, timeout=TIMEOUT_GIAY)
    except (OSError, subprocess.SubprocessError):
        return None
    return (kq.stdout.strip() or None) if kq.returncode == 0 else None


def goc_tram(url):
    """`https://<máy B>[:cổng]` không đường dẫn, query, user → gốc; còn lại None (không gửi)."""
    u = urllib.parse.urlsplit(url.strip())
    if u.scheme != "https" or not u.hostname or u.path not in ("", "/") or u.query or u.fragment or "@" in u.netloc:
        return None
    return "https://" + u.netloc


def dung_yeu_cau(goc, ma, su_kien, session_id):
    than = json.dumps({"su_kien": su_kien, "phien": hashlib.sha256(session_id.encode()).hexdigest()[:16]})
    return urllib.request.Request(goc + DUONG, data=than.encode(), method="POST", headers={
        "Content-Type": "application/json", "Authorization": "Bearer " + ma, "X-Tram": "1", "Origin": goc})


def chay(stdin, env, mo=None, lay=lay_ma):
    try:
        vao = json.loads(stdin.read() or "{}")
        su_kien, phien = vao.get("hook_event_name"), vao.get("session_id")
        goc = goc_tram(env.get("TRAM_DIEU_PHOI_URL", ""))
        if su_kien not in SU_KIEN or not isinstance(phien, str) or not phien or goc is None:
            return 0
        ma = lay(env)
        if not ma:
            return 0
        with (mo or mo_mac_dinh())(dung_yeu_cau(goc, ma, su_kien, phien), timeout=TIMEOUT_GIAY) as r:
            r.read(1024)
    except Exception:                                 # noqa: BLE001 — trạm không với tới / lỗi gì cũng im lặng
        pass
    return 0


def chay_co_han(stdin, env, han=HAN_TOAN_BO, viec=None):
    """Hạn cho CẢ hook (review đợt 4 F14): DNS hay Keychain treo cũng không giữ phiên quá `han` giây."""
    t = threading.Thread(target=viec or chay, args=(stdin, env), daemon=True)
    t.start()
    t.join(han)
    return 0


if __name__ == "__main__":
    chay_co_han(sys.stdin, os.environ)
    os._exit(0)                                       # không chờ luồng còn treo; không có gì cần flush
```

`may-a/hook-dieu-phoi/settings.mau.json` (mới):

```json
{
  "env": {
    "TRAM_DIEU_PHOI_URL": "https://<may-b>.<tailnet>.ts.net"
  },
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "/usr/bin/python3 \"$HOME/.claude/hooks/hook_dieu_phoi.py\"",
            "timeout": 5
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "/usr/bin/python3 \"$HOME/.claude/hooks/hook_dieu_phoi.py\"",
            "timeout": 5
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "/usr/bin/python3 \"$HOME/.claude/hooks/hook_dieu_phoi.py\"",
            "timeout": 5
          }
        ]
      }
    ],
    "SessionEnd": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "/usr/bin/python3 \"$HOME/.claude/hooks/hook_dieu_phoi.py\"",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

`may-a/hook-dieu-phoi/HUONG-DAN.md` (mới):

````markdown
# Hook đèn Điều phối — cài trên máy A (Đại ca làm tay)

Hook này báo cho trạm (máy B) biết máy A đang có phiên Claude Code điều phối. Đèn phòng **Điều phối** trên trang Văn
phòng sẽ sáng khi có phiên, và xám khi phiên đã đóng hoặc 15 phút không có nhịp (spec 2 §5.5, plan 2e).

Hook chỉ gửi tên sự kiện và 16 ký tự băm của mã phiên. Nó **không** gửi prompt, thư mục hay transcript. Trạm không
với tới thì hook im lặng, không in gì và không chặn phiên. Mỗi bước (đọc Keychain, gửi HTTP) chờ tối đa 2 giây; cả
hook tối đa 4 giây rồi tự thoát (Claude Code còn tự dừng hook ở 5 giây).

Hook dùng **mã điều phối**, một mã riêng chỉ để gửi nhịp (D24). Mã này **khác** mã Đại ca của MCP phiên tay. Lộ mã
điều phối thì kẻ có mã chỉ bật/tắt được đèn giả, không đọc được memory, không mở được việc ghi nào khác.

## Điều kiện trước

1. Tailscale đã cài và đăng nhập trên máy A bằng tài khoản của Đại ca (D6, `bs-8eh.17`).
2. Dashboard đã chạy qua `tailscale serve` trên máy B (2a Task 26). Trang `https://<máy B>.<tailnet>.ts.net/` mở
   được từ máy A.
3. `/usr/bin/python3 --version` trên máy A in ra 3.9 trở lên. Nếu macOS hỏi cài Command Line Tools thì cài xong rồi
   mới làm tiếp. Không thì mỗi lần hook chạy sẽ bật hộp thoại cài đặt.

## Tạo mã điều phối (làm một lần)

Mở **Terminal.app** trên máy A, không dùng khung terminal của app Claude vì nó làm hỏng chuỗi dán vào ô ẩn.

1. Tạo mã vào clipboard, không hiện ra màn hình: `openssl rand -hex 32 | tr -d '\n' | pbcopy`
2. Lưu vào Keychain máy A. Chạy lệnh sau, dán mã khi được hỏi (hai lần):
   `security add-generic-password -s tram-dieu-phoi-ma -a "$USER" -w`
3. Đặt bản băm trên máy B: mở phiên Terminal.app tới máy B (ví dụ `ssh`), chạy `tram chu dat-ma-dieu-phoi`, gõ
   `dong-y`, dán mã hai lần. Trạm chỉ lưu sha256 ở khoá `dieu_phoi_ma_sha256` trong `~/.tram/cau-hinh.yaml`.
   Lệnh từ chối nếu mã trùng mã Đại ca.
4. Xoá clipboard: `pbcopy < /dev/null`

**Không** ghi mã vào `settings.json`, biến môi trường cố định hay bất kỳ file nào. Biến `TRAM_DIEU_PHOI_MA` chỉ dùng
cho lệnh kiểm nhanh bên dưới, không đặt trong cấu hình.

## Cài

1. Chép script: `mkdir -p ~/.claude/hooks && cp may-a/hook-dieu-phoi/hook_dieu_phoi.py ~/.claude/hooks/`
2. Gộp `settings.mau.json` vào `~/.claude/settings.json`: thêm khoá `env.TRAM_DIEU_PHOI_URL` với địa chỉ thật của
   máy B (chỉ `https://<tên máy>`, không có đường dẫn), rồi thêm bốn mục trong `hooks`. **Gộp**, không chép đè, vì
   file có thể đã có cấu hình khác.
3. Mở một phiên Claude Code **mới**. Gõ `/hooks` để xem bốn hook đã nhận, duyệt nếu Claude Code hỏi.

Muốn chỉ phiên mở trong một thư mục điều phối mới làm sáng đèn (C3 của plan 2e)? Đặt khối `hooks` và `env` vào
`<thư mục>/.claude/settings.json` thay cho `~/.claude/settings.json`.

## Kiểm nhanh không cần Claude

```bash
echo '{"hook_event_name":"Stop","session_id":"thu-tay"}' \
  | TRAM_DIEU_PHOI_URL=https://<máy B>.<tailnet>.ts.net /usr/bin/python3 ~/.claude/hooks/hook_dieu_phoi.py; echo $?
```

Kết quả mong đợi: in `0`, không in gì khác. Trong 5 giây, trang Văn phòng hiện "Điều phối · đang có phiên". Tắt
Tailscale rồi chạy lại: vẫn in `0` sau tối đa khoảng 4 giây.

## Gỡ

Xoá bốn mục hook và khoá `env.TRAM_DIEU_PHOI_URL` khỏi `settings.json`, xoá `~/.claude/hooks/hook_dieu_phoi.py`,
xoá Keychain: `security delete-generic-password -s tram-dieu-phoi-ma`. Trên máy B, xoá dòng `dieu_phoi_ma_sha256`
trong `~/.tram/cau-hinh.yaml`: route nhịp sẽ từ chối mọi lời gọi.

## Giả định chưa kiểm (spike ở plan 2e Task 5)

- Claude Code chạy hook `SessionStart`, `UserPromptSubmit`, `Stop`, `SessionEnd`. JSON trên stdin có
  `hook_event_name`, `session_id`. Hook được kế thừa khối `env`. Lệnh vượt `timeout` thì bị dừng và phiên đi tiếp.
- Phiên Claude Code trong app Claude desktop cũng đọc `~/.claude/settings.json`.
- `tailscale serve` gắn `Tailscale-User-Login` cho yêu cầu không đến từ trình duyệt, và giữ nguyên `Host`,
  `Origin`, `Authorization`.
- `python3` của macOS xác minh được chứng chỉ HTTPS của `tailscale serve`.
- Hạn 4 giây của cả hook giữ đúng khi DNS tên tailnet treo (Tailscale tắt).
````

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_hook_dieu_phoi.py -q`
Expected: `7 passed`

Run: `uv run pytest -q`
Expected: `N₀ + 7 passed` (2001 nếu chạy riêng trên `main`)

- [ ] **Step 5: Commit**

```bash
git add may-a/hook-dieu-phoi tests/test_hook_dieu_phoi.py
git commit -m "feat(may-a): hook Claude Code báo nhịp phiên điều phối — chỉ tên sự kiện + băm phiên, mã điều phối từ Keychain riêng, timeout 2 s mỗi bước, cả hook ≤ 4 s, im lặng, không proxy/chuyển hướng; mẫu settings + hướng dẫn (spec 2 §5.5; plan 2e G15–G20, D24, F14; bs-urj.7)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 4: Frontend — luật hiển thị thuần của đèn Điều phối: `chuNhip`, màu vàng ấm (D38)

**Độ khó:** `de` · **Đợt:** 1 · **Song song với:** Task 1, 3, 6 · **Phải xong trước:** —

Phần gắn vào component (biển phòng, chip danh sách, dòng "nhịp cuối", khung chi tiết) thuộc **lát 2f** — xem "Ranh giới 2e / 2f". Task này không sửa file `.vue` nào.

**Files:**
- Modify: `frontend/src/van_phong/hien_thi.js` (import `gioVN`, `MAU.den`, hàm `chuNhip`)
- Test: `frontend/tests/dieu_phoi.test.mjs` (mới)

**Interfaces:**
- Consumes: phòng `dieu-phoi` của `/api/van-phong` có `sang`, `nhip_cuoi` (Task 1, G9). Task này không cần Task 1 để chạy test: dữ liệu test dựng tay đúng hợp đồng. `gioVN` (`luat.js`); `chuBien` (có từ 2c, không đổi).
- Produces: `chuNhip(p) -> string | null`; `MAU.den === '#f2c14e'` (đèn Điều phối khi sáng, D38). `Phong3D.vue` của 2c đọc `MAU.den` nên đổi màu ngay; lát 2f dùng cả hai.

- [ ] **Step 1: Viết test thất bại**

`frontend/tests/dieu_phoi.test.mjs` (mới):

```js
import assert from 'node:assert/strict'
import { test } from 'node:test'
import { gioVN } from '../src/luat.js'
import { MAU, chuBien, chuNhip } from '../src/van_phong/hien_thi.js'

// Đèn Điều phối từ nhịp hook máy A (plan 2e Task 4, G9, G21; D38): server suy `sang`; trang chỉ đổi sang chữ, màu.
test('phòng Điều phối: chữ biển ba trạng thái, dòng nhịp cuối, màu đèn', () => {
  const p = { ma: 'dieu-phoi', loai: 'dieu_phoi', sang: false, nhip_cuoi: '2026-10-15T07:05:00Z' }
  assert.equal(chuBien(p), 'Điều phối · tắt đèn')
  assert.equal(chuBien({ ...p, sang: true }), 'Điều phối · đang có phiên')
  assert.equal(chuBien({ ...p, sang: null, nhip_cuoi: null }), 'Điều phối · chưa có tín hiệu')
  assert.equal(chuNhip(p), `nhịp cuối ${gioVN('2026-10-15T07:05:00Z')}`)
  assert.equal(chuNhip({ ...p, nhip_cuoi: null }), null)
  assert.equal(chuNhip({ ma: 'dieu-phoi', loai: 'dieu_phoi', sang: null }), null)                 // API 2c cũ
  assert.equal(chuNhip({ ma: 'giam-doc', loai: 'giam_doc', nhip_cuoi: '2026-10-15T07:05:00Z' }), null)
  assert.deepEqual([MAU.den, MAU.denTat], ['#f2c14e', '#b7b7b7'])                               // vàng ấm D38
})
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `cd frontend && npm run kiem`
Expected: FAIL — `ℹ tests 34`, `ℹ fail 1` (`SyntaxError: The requested module '../src/van_phong/hien_thi.js' does not provide an export named 'chuNhip'`)

- [ ] **Step 3: Viết mã**

```diff
diff --git a/frontend/src/van_phong/hien_thi.js b/frontend/src/van_phong/hien_thi.js
index 9ea7f69..fc90590 100644
--- a/frontend/src/van_phong/hien_thi.js
+++ b/frontend/src/van_phong/hien_thi.js
@@ -1,8 +1,11 @@
 // Hình thức nhân vật / phòng của Văn phòng 3D (spec 2 §5.5) — hàm thuần. Trạng thái do server suy
 // (`hien_thi` ∈ lam | ranh | can_nguoi | loi | tat — tram/suy/nhan_vat.py); ở đây chỉ đổi sang tư thế, màu, chữ.
+import { gioVN } from '../luat.js'
+
+// `den`: đèn Điều phối khi sáng — vàng ấm (D38, plan 2e G21); `denTat`: xám khi tắt hoặc chưa có tín hiệu.
 export const MAU = {
   phong: { du_an: '#cfe2f3', dieu_phoi: '#d9d2e9', giam_doc: '#fce5cd', may_chu: '#d0e0e3', ca_phe: '#ead1dc' },
-  tuong: '#f3f3f3', ban: '#e6d5c3', dau: '#ffe0bd', chamDo: '#cc0000', den: '#fff2cc', denTat: '#b7b7b7',
+  tuong: '#f3f3f3', ban: '#e6d5c3', dau: '#ffe0bd', chamDo: '#cc0000', den: '#f2c14e', denTat: '#b7b7b7',
   than: { claude: '#f6b26b', codex: '#9fc5e8', khac: '#b6d7a8' },
   manHinh: { sang: '#a4c2f4', do: '#e06666', tat: '#999999' },
   suc_khoe: { xanh: '#93c47d', vang: '#ffd966', do: '#e06666' },
@@ -39,6 +42,11 @@ export function chuBien(p) {
   return catChu(p.ten ?? p.ma, 28)
 }
 
+// Phòng Điều phối: lúc nhận nhịp cuối từ hook máy A (plan 2e G21). Component hiển thị dòng này thuộc lát 2f.
+export function chuNhip(p) {
+  return p.loai === 'dieu_phoi' && p.nhip_cuoi ? `nhịp cuối ${gioVN(p.nhip_cuoi)}` : null
+}
+
 export function chuBongBong(nv) {
   if (!nv.bead || (nv.hien_thi !== 'lam' && nv.hien_thi !== 'can_nguoi')) return null
   return `${catChu(nv.bead.tieu_de, 36)} · ${TEN_BUOC[nv.bead.buoc] ?? nv.bead.buoc}`
```

Dòng 127 ký tự trong `chuBien` (dòng 40 sau vá) là dòng có sẵn, không sửa.

- [ ] **Step 4: Chạy, thấy pass**

Run: `cd frontend && npm run kiem && npm run build && npm run kiem-dist`
Expected: `ℹ tests 34`, `ℹ pass 34`; `kiem-an-toan: 68 file, không có chèn HTML thô`; build xanh (cảnh báo cỡ chunk của 2c G14 là đã biết); `kiem-dist: 2 file JS, không thấy mẫu eval/inline…`.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/van_phong/hien_thi.js frontend/tests/dieu_phoi.test.mjs
git commit -m "feat(van-phong): chuNhip cho phòng Điều phối, đèn sáng vàng ấm #f2c14e; component để lát 2f (spec 2 §5.5; plan 2e G21, G24; D38; bs-urj.7)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 5: Kiểm chứng chạy thật trên máy B và máy A — **CHỜ CỔNG**

**Độ khó:** `vua` · **Đợt:** 3 · **Phải xong trước:** Task 1–4, 6 đã ghép; **cổng:** #5 / 2a Task 26 (`bs-6o0.11`: `vn.tram.api` cài, `tailscale serve /` → tram-api); D6 Tailscale máy A (`bs-8eh.17`); S6 + N2 cho chế độ `unix-socket` (`bs-8eh.4`) — bước 2b chỉ làm khi đã bật.

**Files:** không mã. Cuối task: thêm mục "Ghi chú triển khai" vào cuối plan này (kết quả, chỗ khác plan).

Mọi bước có **(Đại ca)** do Đại ca tự làm. Agent không nhập, không đọc, không in mã điều phối hay mã Đại ca; không cài gì trên máy A; không đăng nhập Tailscale; không sửa `~/.claude`.

- [ ] **Step 1 (Đại ca cho phép): Nạp mã mới cho tram-api trên máy B** — sau khi ghép Task 1–4, 6 và build frontend (`cd frontend && npm ci && npm run build`): `launchctl kickstart -k gui/$(id -u)/vn.tram.api`. Nếu `vn.tram.api` chưa cài thì task này còn chờ 2a Task 26.

- [ ] **Step 2: Kiểm âm cục bộ trên máy B (agent, không cần mã)**

```bash
B=https://<ten_may_b>                                         # từ ~/.tram/cau-hinh.yaml
NHIP='{"su_kien":"Stop","phien":"0123456789abcdef"}'
curl -s -o /dev/null -w '%{http_code}\n' -X POST -H 'Content-Type: application/json' -d "$NHIP" \
  http://127.0.0.1:7700/api/dieu-phoi/nhip                                              # 403 (không danh tính)
curl -s -o /dev/null -w '%{http_code}\n' -X POST -H 'Content-Type: application/json' -H 'X-Tram: 1' \
  -H "Origin: $B" -H 'Tailscale-User-Login: <login Đại ca>' -d "$NHIP" \
  http://127.0.0.1:7700/api/dieu-phoi/nhip                     # 401: header giả đúng nhưng không có mã
curl -s -o /dev/null -w '%{http_code}\n' -X POST -H 'Host: evil.example' -d "$NHIP" \
  http://127.0.0.1:7700/api/dieu-phoi/nhip                                              # 421
sqlite3 ~/.tram/su-kien.db "select count(*) from su_kien where loai='dieu_phoi.nhip'"   # 0
```

Expected: 403, 401, 421, 0 dòng. Lệnh thứ hai là đúng lỗ §4 mục 2b (header giả trên TCP localhost). Ở route này, mã điều phối chặn được lỗ đó.

- [ ] **Step 2b (chỉ khi đã bật `cach_ly.kenh_ghi: unix-socket` sau S6): Kiểm âm từ principal thực thi** — chạy lệnh thứ hai ở Step 2 dưới principal thực thi (cách chạy theo plan 3a-2/3c): kỳ vọng **403** (kênh). Qua socket với header giả mà không có mã: **401**.

- [ ] **Step 3 (Đại ca, máy A và máy B): Tạo mã, cài hook và spike hành vi hook** — làm theo `may-a/hook-dieu-phoi/HUONG-DAN.md` (mục "Tạo mã điều phối" có bước `tram chu dat-ma-dieu-phoi` trên máy B), rồi kiểm từng giả định, ghi đạt / không đạt:
  - **H1 — sự kiện, stdin:** mở phiên mới, gõ một câu, chờ trả lời, thoát phiên. Trên máy B: `sqlite3 ~/.tram/su-kien.db "select luc, du_lieu from su_kien where loai='dieu_phoi.nhip' order by id desc limit 5"`. Kỳ vọng có `SessionStart` (hoặc `UserPromptSubmit`), rồi `SessionEnd`, cùng một `phien`. Không thấy dòng nào → chạy "Kiểm nhanh" trong HUONG-DAN. Kiểm nhanh đạt thì lỗi nằm ở cấu hình hook (tên sự kiện, `env`), không ở mạng.
  - **H2 — `env` tới hook:** H1 đạt là `TRAM_DIEU_PHOI_URL` trong khối `env` đã tới hook.
  - **H3 — không chặn phiên, hạn cả hook:** tắt Tailscale trên máy A, gõ một câu. Phiên vẫn trả lời; độ trễ thêm ≤ 4 giây (hạn `HAN_TOAN_BO`), không bao giờ tới 5 giây; không có dòng lạ nào trong hội thoại (stdout rỗng). Đo thêm: `time (echo '{"hook_event_name":"Stop","session_id":"x"}' | TRAM_DIEU_PHOI_URL=https://<ten_may_b> /usr/bin/python3 ~/.claude/hooks/hook_dieu_phoi.py)` khi Tailscale tắt → `real` ≤ 4,5 giây.
  - **H4 — app Claude desktop:** nếu Đại ca điều phối bằng app desktop, lặp H1 trong app.
  - **H5 — `tailscale serve`:** có `Tailscale-User-Login` cho yêu cầu không từ trình duyệt; giữ `Host`, `Origin`, `Authorization`, `Content-Length`. Nếu H1 không có dòng, Đại ca tự chạy ở Terminal.app trên máy A (mã đi qua ống vào `curl -K -`, không nằm trong argv, không hiện ra màn hình):

    ```bash
    B=https://<ten_may_b>
    security find-generic-password -s tram-dieu-phoi-ma -w | sed 's/.*/header = "Authorization: Bearer &"/' \
      | curl -sS -K - -X POST -H 'Content-Type: application/json' -H 'X-Tram: 1' -H "Origin: $B" \
          -d '{"su_kien":"Stop","phien":"0123456789abcdef"}' -w ' %{http_code}\n' "$B/api/dieu-phoi/nhip"
    ```

    Kỳ vọng `{"ghi":true} 200` (hoặc `false`). Nhận **403** kèm "Chỉ đọc…" nghĩa là `tailscale serve` không gắn header danh tính → **C4**. Nhận **401** nghĩa là mã ở máy A khác mã đã đặt trên máy B.
  - **H6 — TLS của `python3`:** `/usr/bin/python3 -c "import urllib.request as u; print(u.urlopen('https://<ten_may_b>/api/du-an', timeout=5).status)"` in `200` (đường chỉ đọc, không cần mã). Lỗi `CERTIFICATE_VERIFY_FAILED` → ghi vào "Ghi chú triển khai"; cách sửa (gửi bằng `curl` của macOS, hoặc chỉ định bộ chứng chỉ) thành một task riêng.

- [ ] **Step 4 (Đại ca): Đèn trên dashboard (giao diện 2c hiện có)** — mở trang Văn phòng (máy A hoặc điện thoại):
  - gõ một câu trong phiên điều phối → trong ≤ 5 giây, biển "Điều phối · đang có phiên", đèn vàng ấm `#f2c14e` phát sáng (D38);
  - thoát phiên → ≤ 5 giây "tắt đèn" (H1 đạt) hoặc sau 15 phút (nếu `SessionEnd` không tới);
  - để phiên mở mà không gõ 16 phút → "tắt đèn".
  - Dòng "nhịp cuối" chưa có trên giao diện 2c; kiểm bằng `curl -s https://<ten_may_b>/api/van-phong` (khoá `nhip_cuoi` của phòng `dieu-phoi`). Lát 2f kiểm lại đèn trên giao diện mới.

- [ ] **Step 5: Đếm dung lượng** — sau một ngày làm việc: `sqlite3 ~/.tram/su-kien.db "select count(*) from su_kien where loai='dieu_phoi.nhip' and luc > strftime('%Y-%m-%dT%H:%M:%SZ','now','-1 day')"`. Ghi số vào "Ghi chú triển khai" (G22).

- [ ] **Step 6: Ghi chú triển khai** vào cuối plan: H1–H6, số đếm Step 5, Host thật mà `tailscale serve` chuyển tới, chỗ khác plan. Commit riêng `docs: ghi chú triển khai lát 2e`. Đạt Step 4 thì đóng `bs-urj.7`.

---

### Task 6: Mã điều phối riêng — khoá băm, lệnh `tram chu dat-ma-dieu-phoi` (D24)

**Độ khó:** `de` · **Đợt:** 1 · **Song song với:** Task 1, 3, 4 · **Phải xong trước:** — (Task 2 cần task này)

**Files:**
- Create: `tram/chu/ma_dieu_phoi.py`
- Modify: `tram/cli_dich_vu.py` (2 dòng trong `them_lenh`)
- Test: `tests/test_ma_dieu_phoi.py` (mới)

**Interfaces:**
- Consumes: `bam`, `MA_RE`, `BAM_RE`, `tep_cau_hinh`, `doc_bam` (mã Đại ca) từ `tram/nho/ma_dai_ca.py` — chỉ import. Trong test: `ma_dai_ca.ghi_bam`, `CauHinhMcp`, `tao_ung_dung`, `DichVuNho`, `KhoKyUc`, `BoDemDung`, `EmbedderGia`, `ky_uc`, `goi_mcp`.
- Produces: `KHOA = "dieu_phoi_ma_sha256"`; `doc_bam(duong_dan=None) -> str | None`; `ghi_bam(gia_tri, duong_dan=None)` (`ValueError` nếu sai dạng, file hỏng, hoặc trùng băm mã Đại ca); `dat_ma_dieu_phoi(args, *, doc_an=None, hoi=None) -> int`; `them_lenh_ma_dieu_phoi(chu)`; lệnh `tram chu dat-ma-dieu-phoi [--dong-y]`. Task 2 import `doc_bam` (route) và `ghi_bam` (test).

- [ ] **Step 1: Viết test thất bại**

`tests/test_ma_dieu_phoi.py` (mới):

```python
"""Mã điều phối riêng của hook máy A (D24; plan 2e Task 6, G2, G23): khoá băm riêng, lệnh hỏi ẩn, khác mã Đại ca,
KHÔNG đọc được memory (MCP phiên tay lẫn HTTP nội bộ của memory service)."""
from types import SimpleNamespace as NS

import pytest

from asgi_gia import goi
from mcp_gia import goi_cong_cu, goi_mcp, van_ban
from nho_gia import EmbedderGia, ky_uc
from tram.cau_hinh.tram import nap_cau_hinh_tram
from tram.chu.ma_dieu_phoi import dat_ma_dieu_phoi, doc_bam, ghi_bam
from tram.nho import ma_dai_ca
from tram.nho.dich_vu import DichVuNho
from tram.nho.kho import KhoKyUc
from tram.nho.may_chu_mcp import tao_ung_dung
from tram.nho.nho_lai import BoDemDung
from tram.nho.ung_dung import CauHinhMcp
from tram.su_kien.kho import KhoSuKien

MA_DP, MA_DC = "d1" * 32, "c2" * 32                     # mã điều phối, mã Đại ca
CU = "# cấu hình trạm — Đại ca sửa tay\ndai_ca_logins: [dai-ca@example.com]\nten_may_b: may-b.tail.ts.net\n"


def test_khoa_rieng_giu_chu_thich_va_ma_dai_ca(tram_home_tam):
    p = tram_home_tam / "cau-hinh.yaml"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(CU, encoding="utf-8")
    assert doc_bam() is None
    ma_dai_ca.ghi_bam(ma_dai_ca.bam(MA_DC))
    ghi_bam(ma_dai_ca.bam(MA_DP))
    assert doc_bam() == ma_dai_ca.bam(MA_DP) and ma_dai_ca.doc_bam() == ma_dai_ca.bam(MA_DC)
    ghi_bam("0" * 64)
    van_ban_moi = p.read_text(encoding="utf-8")
    assert van_ban_moi.startswith(CU) and van_ban_moi.count("dieu_phoi_ma_sha256") == 1 and doc_bam() == "0" * 64
    assert nap_cau_hinh_tram(p).ten_may_b == "may-b.tail.ts.net" and not list(p.parent.glob(".cau-hinh-*"))
    for hong in ("dieu_phoi_ma_sha256: 123\n", ": : :\n  - ["):
        p.write_text(hong, encoding="utf-8")
        assert doc_bam() is None
    with pytest.raises(ValueError):
        ghi_bam("khong-phai-hex")


def test_tu_choi_ma_trung_ma_dai_ca(tram_home_tam, capsys):
    ma_dai_ca.ghi_bam(ma_dai_ca.bam(MA_DC))
    with pytest.raises(ValueError, match="KHÁC mã Đại ca"):
        ghi_bam(ma_dai_ca.bam(MA_DC))
    nhap = iter([MA_DC, MA_DC])
    assert dat_ma_dieu_phoi(NS(dong_y=True), doc_an=lambda _: next(nhap), hoi=lambda _: "") == 1
    assert doc_bam() is None and MA_DC not in capsys.readouterr().out


def test_lenh_hoi_an_hai_lan_khong_in_ma_va_tu_choi_dau_vao_sai(tram_home_tam, capsys):
    for nhap, hoi in (([MA_DP, MA_DP], "khong"), ([MA_DP, MA_DP[:-1] + "x"], "dong-y"), (["ngan", "ngan"], "dong-y")):
        it = iter(nhap)
        assert dat_ma_dieu_phoi(NS(dong_y=False), doc_an=lambda _: next(it), hoi=lambda _: hoi) == 1
    assert doc_bam() is None and not (tram_home_tam / "cau-hinh.yaml").exists()
    nhap = iter([MA_DP, MA_DP])
    assert dat_ma_dieu_phoi(NS(dong_y=False), doc_an=lambda _: next(nhap), hoi=lambda _: "dong-y") == 0
    out = capsys.readouterr()
    assert doc_bam() == ma_dai_ca.bam(MA_DP) and MA_DP not in out.out + out.err and "Terminal.app" in out.out


def test_cli_chu_dat_ma_dieu_phoi_khong_nhan_ma_qua_argv(monkeypatch, tram_home_tam):
    from tram.cli import main, tao_parser
    nhap = iter([MA_DP, MA_DP])
    monkeypatch.setattr("getpass.getpass", lambda _: next(nhap))
    assert main(["chu", "dat-ma-dieu-phoi", "--dong-y"]) == 0 and doc_bam() == ma_dai_ca.bam(MA_DP)
    with pytest.raises(SystemExit):
        tao_parser().parse_args(["chu", "dat-ma-dieu-phoi", "--ma", MA_DP])


def test_ma_dieu_phoi_khong_doc_duoc_memory(tmp_path, tram_home_tam):
    ma_dai_ca.ghi_bam(ma_dai_ca.bam(MA_DC))
    ghi_bam(ma_dai_ca.bam(MA_DP))                       # cả hai băm cùng nằm trong ~/.tram/cau-hinh.yaml tạm
    e = EmbedderGia()
    kho = KhoKyUc(tmp_path / "l", so_chieu=e.so_chieu)
    kho.them(ky_uc("m-y", "/du-an/erp/nghiep-vu", vector=e.embed(["m-y"])[0], noi_dung="Nội dung m-y"))
    e.goi.clear()
    dv = DichVuNho(kho, e, lambda: KhoSuKien(tmp_path / "sk.db"), BoDemDung(), "tok-nho")
    app = tao_ung_dung(dv, CauHinhMcp(lambda g: None, ma_dai_ca.doc_bam, lambda t: t == "erp"))   # bộ đọc băm THẬT
    hoi = goi_cong_cu("nho_lai", {"truy_van": "nội dung"})
    dp, dc = goi_mcp(app, ("POST", "/mcp", hoi, {"Authorization": f"Bearer {MA_DP}", "X-Tram-Du-An": "erp"}),
                     ("POST", "/mcp", hoi, {"Authorization": f"Bearer {MA_DC}", "X-Tram-Du-An": "erp"}))
    assert dp.status == 401 and MA_DP not in dp.body.decode()
    assert van_ban(dc)[0] is False and "m-y" in van_ban(dc)[1]          # đối chứng: mã Đại ca vẫn đọc được
    than = {"truy_van": "nội dung", "vung_cap": ["/du-an/erp"]}
    assert goi(app, "POST", "/nho-lai", json_body=than, headers={"Authorization": f"Bearer {MA_DP}"}).status == 401
    assert e.goi == [["nội dung"]]                       # chỉ lời gọi của mã Đại ca chạm tới embedder
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_ma_dieu_phoi.py -q`
Expected: FAIL — `1 error` (`ModuleNotFoundError: No module named 'tram.chu.ma_dieu_phoi'`)

- [ ] **Step 3: Viết mã**

`tram/chu/ma_dieu_phoi.py` (mới):

```python
"""Mã điều phối (quyết định D24; plan 2e G2, G23): bí mật RIÊNG của hook phiên điều phối trên máy A, chỉ mở đúng
`POST /api/dieu-phoi/nhip`. Máy A giữ mã trong Keychain (mục `tram-dieu-phoi-ma`); trạm chỉ giữ sha256 ở khoá
`dieu_phoi_ma_sha256` của `~/.tram/cau-hinh.yaml`. Mã này không đọc được memory (memory service chỉ so với
`ma_dai_ca_sha256`), không mở route ghi nào khác, và phải KHÁC mã Đại ca. Mã không bao giờ đi qua argv, log hay màn
hình: `tram chu dat-ma-dieu-phoi` hỏi ẩn (getpass) hai lần, chờ `dong-y`. Chỉ import từ `tram/nho/ma_dai_ca.py`."""
import getpass
import os
import re
import sys
import tempfile
from pathlib import Path

import yaml

from tram.nho.ma_dai_ca import BAM_RE, MA_RE, bam, tep_cau_hinh
from tram.nho.ma_dai_ca import doc_bam as doc_bam_dai_ca

KHOA = "dieu_phoi_ma_sha256"
DONG_RE = re.compile(rf"^{KHOA}:.*$", re.M)


def _doc(van_ban: str) -> str | None:
    raw = yaml.safe_load(van_ban) or {}
    v = raw.get(KHOA) if isinstance(raw, dict) else None
    return v if isinstance(v, str) and BAM_RE.fullmatch(v) else None


def doc_bam(duong_dan: Path | None = None) -> str | None:
    """Bản băm đã đặt. Thiếu file, yaml hỏng, giá trị sai dạng → None: route nhịp từ chối mọi lời gọi (fail closed)."""
    try:
        return _doc(tep_cau_hinh(duong_dan).read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return None


def ghi_bam(gia_tri: str, duong_dan: Path | None = None) -> None:
    """Thay dòng `dieu_phoi_ma_sha256:` (hoặc thêm cuối file), giữ chú thích và khoá khác; kiểm trước, ghi nguyên tử."""
    if not BAM_RE.fullmatch(gia_tri):
        raise ValueError("bản băm phải là 64 ký tự hex thường")
    if gia_tri == doc_bam_dai_ca(duong_dan):
        raise ValueError("mã điều phối phải KHÁC mã Đại ca (D24) — không đổi gì")
    p = tep_cau_hinh(duong_dan)
    cu = p.read_text(encoding="utf-8") if p.exists() else ""
    dong = f'{KHOA}: "{gia_tri}"'
    if DONG_RE.search(cu):
        moi = DONG_RE.sub(dong, cu)
    else:
        moi = (cu if not cu or cu.endswith("\n") else cu + "\n") + dong + "\n"
    try:
        dung = _doc(moi) == gia_tri
    except yaml.YAMLError:
        dung = False
    if not dung:
        raise ValueError(f"{p} không phải bảng khoá → giá trị hợp lệ — sửa tay rồi chạy lại; không đổi gì")
    p.parent.mkdir(parents=True, exist_ok=True)
    fd, tam = tempfile.mkstemp(dir=p.parent, prefix=".cau-hinh-")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(moi)
    os.replace(tam, p)


def dat_ma_dieu_phoi(args, *, doc_an=None, hoi=None) -> int:
    doc_an, hoi, p = doc_an or getpass.getpass, hoi or input, tep_cau_hinh()
    print(f"Sẽ ghi sha256 của mã điều phối vào {p} (khoá {KHOA}; thay bản cũ nếu có). Mã không được lưu, không in.\n"
          "Mã: chuỗi ngẫu nhiên ≥ 32 ký tự, đúng mã trong Keychain máy A (mục tram-dieu-phoi-ma), KHÁC mã Đại ca. "
          "Mã này chỉ mở POST /api/dieu-phoi/nhip.\nDán trong Terminal.app — khung terminal của app Claude làm hỏng "
          "chuỗi dán vào ô ẩn.")
    if not args.dong_y and hoi("Gõ dong-y để tiếp tục: ").strip() != "dong-y":
        print("Không đổi gì.")
        return 1
    ma = doc_an("Mã điều phối (ẩn): ")
    if not MA_RE.fullmatch(ma):
        print("Lỗi: mã phải 32–256 ký tự trong [A-Za-z0-9._~+/=-] — không đổi gì.", file=sys.stderr)
        return 1
    if doc_an("Nhập lại (ẩn): ") != ma:
        print("Lỗi: hai lần nhập không khớp — không đổi gì.", file=sys.stderr)
        return 1
    try:
        ghi_bam(bam(ma), p)
    except ValueError as e:
        print(f"Lỗi: {e}", file=sys.stderr)
        return 1
    print(f"Đã lưu bản băm vào {p}. tram-api dùng ngay từ nhịp kế tiếp, không cần khởi động lại.")
    return 0


def them_lenh_ma_dieu_phoi(chu) -> None:
    d = chu.add_parser("dat-ma-dieu-phoi", help="Đặt mã điều phối cho hook máy A (lưu sha256, hỏi ẩn; D24)")
    d.add_argument("--dong-y", action="store_true", help="Bỏ bước gõ dong-y (vẫn hỏi mã ẩn)")
    d.set_defaults(ham=dat_ma_dieu_phoi)
```

`tram/cli_dich_vu.py`:

```diff
diff --git a/tram/cli_dich_vu.py b/tram/cli_dich_vu.py
index 6c72c76..5a1f7c8 100644
--- a/tram/cli_dich_vu.py
+++ b/tram/cli_dich_vu.py
@@ -60,6 +60,8 @@ def them_lenh(sub, chu) -> None:
     them_lenh_nho(sub)
     from tram.nho.ma_dai_ca import them_lenh_ma_dai_ca
     them_lenh_ma_dai_ca(chu)
+    from tram.chu.ma_dieu_phoi import them_lenh_ma_dieu_phoi     # plan 2e (D24): mã riêng của hook máy A
+    them_lenh_ma_dieu_phoi(chu)
     from tram.tho.bao_lenh import them_lenh_bao
     them_lenh_bao(sub)
     from tram.tho.lenh import them_lenh_tho
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_ma_dieu_phoi.py tests/test_nho_ma_dai_ca.py tests/test_nho_mcp.py -q`
Expected: `25 passed`

Run: `uv run pytest -q`
Expected: `N₀ + 5 passed` (1999 nếu chạy riêng trên `main`)

- [ ] **Step 5: Commit**

```bash
git add tram/chu/ma_dieu_phoi.py tram/cli_dich_vu.py tests/test_ma_dieu_phoi.py
git commit -m "feat(chu): mã điều phối riêng cho hook máy A — trạm giữ sha256 ở dieu_phoi_ma_sha256, lệnh tram chu dat-ma-dieu-phoi hỏi ẩn, chặn trùng mã Đại ca, không đọc được memory (plan 2e G23; D24; bs-urj.7)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

## Sơ đồ đợt chạy

Số test là kết quả chạy thật trên bản dựng thử (`main` `38a016f`: N₀ = 1994, M₀ = 33), áp nguyên văn từ plan này. Ngoặc sau tên task là task phải ghép trước.

```
Đợt 0 — main 38a016f (hoặc main lúc thực thi) → N₀ passed · node M₀ · build + kiem-dist xanh

Đợt 1 — song song, 4 worktree từ main
  T1 suy đèn + đọc theo hạn sống + /api/van-phong (py) · T3 hook máy A (py)
  T4 chuNhip + màu đèn D38 (frontend, không .vue) · T6 mã điều phối + lệnh (py)
  → N₀ + 16 = 2010 passed · node M₀ + 1 = 34 · build + kiem-dist xanh

Đợt 2 — 1 worktree từ main sau đợt 1
  T2 POST /api/dieu-phoi/nhip, gộp nguyên tử (1, 6)
  → N₀ + 22 = 2016 passed · node 34

Đợt 3 — CHỜ CỔNG (#5 / 2a T26, D6 máy A; S6 + N2 cho bước 2b) và C2–C6
  T5 kiểm chứng chạy thật (1–4, 6)

Sau 2e — lát 2f làm lại .vue: biển phòng / danh sách / khung chi tiết dùng sang, chuNhip, MAU.den theo mockup D20, D33, D38
```

| Task | Độ khó | Đợt | Phải xong trước | File chạm (ngoài test) | Test mới | Toàn bộ sau task (trên main đợt trước) |
|---|---|---|---|---|---|---|
| 1 | de | 1 | — | `tram/suy/dieu_phoi.py`, `tram/suy/kho_nhip.py` (mới), `tram/suy/van_phong.py`, `tram/api/van_phong.py` | 4 (py) | N₀ + 4 (1998) |
| 3 | vua | 1 | — | `may-a/hook-dieu-phoi/` (3 file mới) | 7 (py) | N₀ + 7 (2001) |
| 4 | de | 1 | — | `frontend/src/van_phong/hien_thi.js` | 1 (node) | node M₀ + 1 (34) |
| 6 | de | 1 | — | `tram/chu/ma_dieu_phoi.py` (mới), `tram/cli_dich_vu.py` | 5 (py) | N₀ + 5 (1999) |
| 2 | vua | 2 | 1, 6 | `tram/api/dieu_phoi.py` (mới), `tram/api/van_phong.py` | 6 (py: 5 API + 1 race) | N₀ + 22 (2016) |
| 5 | vua | 3 | 1–4, 6 + cổng | — (tài liệu) | — | — |

**Tổng cuối (Task 1–4, 6):** `uv run pytest -q` = **N₀ + 22** (2016); `npm run kiem` = **M₀ + 1** (34); `npm run build` và `npm run kiem-dist` xanh. Số "riêng trên `main`" của từng task đợt 1 là phép cộng từ số test mới; số sau đợt 1 và sau đợt 2 là số chạy thật.

Không file nào bị hai task cùng đợt sửa. **Đụng chung với nơi khác:** `tram/cli_dich_vu.py` (Task 6, 2 dòng) — không plan đợt 4 nào khác sửa file này. Không file nào thuộc danh sách tránh (2d, 3c, 1b-4, 1a-2, `app.py`). `tram/api/van_phong.py`, `tram/suy/van_phong.py` (2c) hiện không plan nào khác đang sửa. Thư mục `may-a/` là mới. Component `.vue` của 2c để nguyên cho 2f; `hien_thi.js` chỉ thêm `chuNhip` và đổi một màu (2f giữ file này, khảo sát §2.2).

## Để sau (chờ cổng / chờ chốt) — không lập task code ở plan này

| Phần | Spec | Chờ | Đã chừa sẵn |
|---|---|---|---|
| Chạy thật: hook trên máy A, đèn sáng qua tailnet | 2 §5.5 | Task 5: #5 (`bs-6o0.11`), D6 (`bs-8eh.17`) | HUONG-DAN, "Kiểm nhanh" |
| Kiểm âm từ principal thực thi khi bật `unix-socket` | 2 §4 mục 2b | S6 + N2 (`bs-8eh.4`) | Route dùng `kenh_hop_le` như mọi API ghi |
| Bỏ đòi header Tailscale ở route này | 2 §4 mục 2 | **C4**, nếu H5 không đạt | Chỉ sửa một dòng `yeu_cau_ghi(request)` trong `tram/api/dieu_phoi.py` |
| Đổi hạn sống / gộp | — | **C2** | Hằng `HAN_SONG`, `GOP` |
| Gắn đèn vào giao diện mới (biển, danh sách, khung chi tiết) | 2 §5.5, mockup D20/D33 | **Lát 2f** | `sang`, `nhip_cuoi`, `chuNhip`, `MAU.den` (Task 1, 4), mục "Ranh giới 2e / 2f" |
| Ô đèn Điều phối trên Tổng quan | D17 | Mockup Tổng quan bổ sung ô này và được duyệt | — |
| `tram chu dat-ma-dai-ca` chặn trùng mã điều phối (chiều ngược của G23) | 1b §9.3 | 1b-4 mở lại `tram/nho/ma_dai_ca.py` | `tram.chu.ma_dieu_phoi.doc_bam` |
| Hook gửi bằng `curl` của macOS nếu `python3` không xác minh được TLS | — | H6 | `dung_yeu_cau` tách riêng khỏi bước gửi |
| Dọn nhịp cũ khỏi `su_kien` | — | số đo Step 5 (G22) | `doc_nhip` chỉ đọc nhịp trong 15 phút |
| Cài hook bằng lệnh (thay chép tay) | kiến trúc Q15 | Đại ca muốn | `settings.mau.json` |

## Tự review

**1. Độ phủ yêu cầu**

| Yêu cầu | Task | Kiểm bằng |
|---|---|---|
| D12: đèn Điều phối lấy tín hiệu từ hook phiên điều phối trên máy A | 1, 2, 3 | chuỗi hook → `POST` → `dieu_phoi.nhip` → `/api/van-phong`: `test_nhip_hop_le_ghi_gop_va_den_sang` |
| D24: mã riêng `tram-dieu-phoi-ma`, trạm chỉ giữ băm | 6, 2, 3 | `test_khoa_rieng_giu_chu_thich_va_ma_dai_ca`; `test_lenh_hoi_an_hai_lan_khong_in_ma_va_tu_choi_dau_vao_sai`; `test_cli_chu_dat_ma_dieu_phoi_khong_nhan_ma_qua_argv`; `test_lay_ma_tu_keychain_rieng_khong_qua_argv` |
| D24: mã điều phối **không** đọc được memory | 6 | `test_ma_dieu_phoi_khong_doc_duoc_memory` (MCP phiên tay 401, `/nho-lai` 401, embedder không bị gọi; đối chứng mã Đại ca đọc được) |
| D24: mã điều phối **không** mở route ghi nào khác | 2 | `test_ma_dieu_phoi_khong_mo_route_ghi_nao_khac` (quét **mọi** route POST của `CAC_TUYEN`, kể cả `/api/tho/*` có kho phiếu + token máy thật: chỉ 401/403; không sự kiện nào ngoài nhật ký từ chối `may.ghep_sai`; estop tắt) |
| D24: không mở rộng mã Đại ca | 2, 6 | `test_tu_choi_khi_thieu_hoac_sai_bang_chung` ("mã Đại ca" → 401); `test_chua_dat_ma_dieu_phoi_thi_tu_choi_moi_loi_goi`; `test_tu_choi_ma_trung_ma_dai_ca` |
| Đường ghi riêng **có xác thực** | 2 | `test_tu_choi_khi_thieu_hoac_sai_bang_chung` (không mã, sai mã, mã Đại ca, không `Bearer`, thiếu/lạ header Tailscale, thiếu `X-Tram`, `Origin` lạ, Host lạ 421, `unix-socket` qua TCP 403, qua socket 200) |
| Giới hạn tần suất và kích thước | 2 | `test_gioi_han_kich_thuoc_luoc_do_va_tan_suat` (413 thân lớn, 413 `Content-Length` khai lớn, 422 bốn dạng sai, 429 kể cả lời gọi hỏng, mở lại sau 60 s) |
| F10: gộp nguyên tử | 2 | `test_ghi_gop_nguyen_tu_giua_hai_ket_noi` (hai kết nối, ép đan xen → `[False, True]`, 1 dòng); Step 4b: bỏ khoá thì fail |
| F11: không cắt mất phiên còn sống | 1 | `test_hon_200_nhip_khong_lam_tat_phien_con_song` (201 phiên đóng sau phiên còn sống → vẫn sáng; quá hạn → `false`, không `null`) |
| Nhịp có hạn sống; hết hạn → đèn xám | 1 | `test_den_theo_phien_va_han_song_15_phut`; `test_api_van_phong_tra_sang_that_cho_phong_dieu_phoi` (dời `dong_ho` 20 phút → `false`, vẫn có `nhip_cuoi`) |
| `/api/van-phong` trả `sang` thật; luật hiển thị cho 2f; màu D38 | 1, 4 | test API Task 1; node `phòng Điều phối: chữ biển ba trạng thái, dòng nhịp cuối, màu đèn` |
| F14 + hook không chặn phiên | 3 | `test_han_toan_bo_khi_mot_buoc_treo`; `test_im_lang_khi_loi_mang_dau_vao_la_hoac_thieu_cau_hinh`; `test_chay_that_thoat_0_khong_in_gi_khi_tram_khong_voi_toi` (tiến trình thật: thoát 0, stdout/stderr rỗng, < 5 s) |
| Mã chỉ tới đúng máy B | 3 | `test_khong_proxy_khong_theo_chuyen_huong`; URL `http://`, có đường dẫn, có user → không gửi |
| Không lộ nội dung phiên | 3 | `test_gui_dung_yeu_cau_va_khong_lo_noi_dung_phien` (prompt, `cwd` không có trong thân; `phien` là băm) |
| Giả định hook cần spike; chạy thật chờ cổng | 5 | H1–H6 |
| Test không gọi mạng, không Keychain, không `~/.claude` thật | 3 | `MoGia`; `chay` giả; tiến trình thật chạy `HOME` tạm, `TRAM_DIEU_PHOI_MA` đặt sẵn, trỏ `127.0.0.1:9` |

**2. Quét placeholder:** không có "TBD/TODO/tương tự Task N". Mọi file mới có nguyên văn đầy đủ; mọi file có sẵn có bản vá đã `git apply --check` trên `38a016f`; mọi lệnh có kết quả mong đợi. Các chỗ cố ý để người thực hiện điền: `<model đang thực thi>` trong lệnh commit, `<ten_may_b>` / `<login Đại ca>` trong Task 5, `<may-b>.<tailnet>` trong `settings.mau.json` (test kiểm nó vẫn là `https://`).

**3. Khớp chữ ký:**
- `LOAI`, `DU_AN_HE`, `TAC_NHAN`, `HAN_SONG`, `can_ghi(nhip, phien, su_kien, bay_gio)` (Task 1) ↔ `doc_nhip(kho, luc)` (Task 1) ↔ `ghi_nhip` trong `tram/api/dieu_phoi.py` (Task 2) ↔ `den_dieu_phoi(doc_nhip(kho, luc), luc)` trong `r_van_phong` (Task 1).
- `{"sang", "nhip_cuoi"}` (Task 1) ↔ `cac_phong(..., dieu_phoi=dp)` ↔ `chuNhip(p)` đọc `p.nhip_cuoi`, `chuBien(p)` của 2c và `Phong3D.vue` (`MAU.den`) đọc `p.sang` (Task 4).
- Thân `{"su_kien", "phien"}` + header `Authorization: Bearer`, `X-Tram: 1`, `Origin` (`dung_yeu_cau`, Task 3) ↔ `ThanNhipDieuPhoi` (bốn giá trị `su_kien` khớp `SU_KIEN` của script và `SU_KIEN_HOOK` của Task 1; `phien` 16 hex thường = `hexdigest()[:16]`) ↔ `yeu_cau_ghi` + `kiem_ma_dieu_phoi` (Task 2).
- `dieu_phoi_ma_sha256` (Task 6 `KHOA`) ↔ `doc_bam()` trong `kiem_ma_dieu_phoi` (Task 2) ↔ thông báo 401 nhắc `tram chu dat-ma-dieu-phoi` (Task 2 test) ↔ HUONG-DAN (Task 3 test).
- Tên mục Keychain `tram-dieu-phoi-ma` giống nhau ở script, HUONG-DAN, lời nhắc của lệnh Task 6 và test Task 3 (test còn kiểm HUONG-DAN không nhắc `tram-dai-ca-ma`).

**4. Đã chạy thử (15/10, bản D24 + D38, trên `main` `38a016f`):**
- Bản sao `main` `38a016f` trong scratchpad (thư mục riêng `p2e-d24/tu-plan`); không đụng repo thật, không mạng, không Keychain, không `~/.tram`, không `~/.claude` thật. Mốc: **1994 passed**, node **33**.
- Script trích **từ chính file plan** mọi khối "(mới)" và mọi khối `diff`, áp lên bản sao sạch theo thứ tự đợt. Mỗi task: chép test trước, chạy thấy đúng thông báo fail ở Step 2, rồi chép mã. Đợt 1 (T1 +4, T3 +7, T6 +5, T4 node +1) → **2010 passed**, node **34**, `kiem-an-toan` 68 file, `npm run build` và `npm run kiem-dist` xanh. Đợt 2 (T2 +6) → **2016 passed**.
- Step 4b (bỏ `BEGIN IMMEDIATE`) → `test_ghi_gop_nguyen_tu_giua_hai_ket_noi` fail `[True, True] == [False, True]`; trả lại → pass.
- Bản vá Task 2 cho `tram/api/van_phong.py` qua `git apply --check` trên cả `main` gốc lẫn `main` sau đợt 1. Mọi bản vá khác qua `git apply --check` trên `38a016f`.
- Bản trước của plan này (trên `60bc562`, N₀ = 1987) cũng đã chạy thử: 2003 / 2009 passed; mã Python không đổi giữa hai bản, chỉ Task 4 đổi.
- **Chưa** kiểm: hook thật của Claude Code, `tailscale serve` thật, TLS từ `python3` máy A, hạn 4 giây khi DNS treo thật, giao diện trên trình duyệt (chỉ build + luật thuần; màu `#f2c14e` chưa nhìn bằng mắt).

**5. Rủi ro còn lại (Đại ca biết):**
- (a) **Lộ mã điều phối.** Kẻ có mã, đứng trong tailnet với login của Đại ca (hoặc là tiến trình cục bộ trên B khi còn chế độ `header`), bật/tắt được đèn giả. Không đọc được memory, không mở route ghi nào khác (test). Đổi mã: chạy lại `tram chu dat-ma-dieu-phoi` và cập nhật Keychain máy A.
- (b) **Mã nằm trong tầm đọc của agent trên máy A.** Mục Keychain do `security` tạo mà không giới hạn ứng dụng đọc được từ Bash của phiên Claude trên máy A. Nhờ D24, thứ đọc được chỉ là mã bật đèn, không phải mã memory.
- (c) **Từ chối dịch vụ đèn (G10).** Ở chế độ `header`, một tiến trình cục bộ trên B gọi rác 30 lần/phút sẽ làm nhịp thật bị 429 → đèn có thể xám sai. Không ảnh hưởng gì ngoài đèn. Chế độ `unix-socket` (S6) đóng được lỗ này vì lời gọi qua TCP bị chặn ở bước kênh, trước bộ đếm.
- (d) **Hook chưa kiểm thật (G16, H1–H6).** Nếu `SessionEnd` không chạy (phiên bị giết, máy ngủ), đèn sáng thêm tối đa 15 phút. Nếu tên trường stdin khác, hook im lặng và đèn mãi `null`/`false`. Task 5 phát hiện được.
- (e) **Độ trễ prompt khi trạm không với tới** (G18): mỗi thao tác tối đa 2 giây, cả hook tối đa 4 giây, mỗi lần gửi prompt và mỗi lần trả lời xong. Hạn 4 giây dựa trên luồng nền + `os._exit`; cần H3 xác nhận khi DNS treo thật.
- (f) **Header Tailscale cho yêu cầu không từ trình duyệt** chưa kiểm (H5). Nếu không có thì mọi nhịp bị 403 và đèn không bao giờ sáng → C4.
- (g) **Giao dịch ghi giữ khoá DB trong lúc đọc nhịp** (F10). Đọc ≤ vài trăm dòng `_tram` trong 15 phút, vài mili giây; người ghi khác chờ qua `busy_timeout` 10 giây. Chấp nhận.
- (h) **`dat-ma-dai-ca` chưa chặn trùng mã điều phối** (chiều ngược G23) vì `tram/nho/ma_dai_ca.py` thuộc 1b-4. Đặt mã Đại ca trùng mã điều phối thì mã hook đọc được memory. HUONG-DAN dặn tạo mã bằng `openssl rand` riêng; ghi ở "Để sau".

## Cần sửa spec sau (không sửa spec đã duyệt trong plan này)

- **Spec 2 §5.5, §14:** nguồn đèn Điều phối = hook phiên Claude Code máy A (D12); ba giá trị `sang`, hạn sống 15 phút, khoá `nhip_cuoi` (G9). Đổi đề xuất 2c "chưa có producer" thành "producer: hook máy A".
- **Spec 2 §7:** thêm `POST /api/dieu-phoi/nhip` (G4, G5); ghi ngoại lệ của câu "Mọi `POST` ghi mang `ma_thao_tac` và `expected_version`" (G6, C6).
- **Spec 2 §4:** route này đòi **thêm** mã điều phối (D24) ngoài danh tính Tailscale + CSRF; giới hạn tần suất và kích thước (G3, G10, G11, G23).
- **Spec 2 §12.2:** thêm dòng sự kiện `dieu_phoi.nhip` (G7). **§12.5:** khoá `dieu_phoi_ma_sha256` trong `cau-hinh.yaml` (G23).
- **Spec 1b §9.3:** không đổi phạm vi mã Đại ca; thêm một câu: mã điều phối (D24) là bí mật khác, memory service không nhận nó.
- **Kiến trúc §4.1** hàng máy A: thêm "hook Claude Code báo nhịp điều phối (Đại ca tự cài), mã riêng trong Keychain `tram-dieu-phoi-ma`".
- **Spec 2 "Trạng thái triển khai":** sau khi ghép, chuyển dòng "§5.5 Đèn Điều phối" sang "đã có mã + test phía trạm; giao diện mới ở 2f; chờ cổng chạy thật (Task 5)"; bỏ dòng tương ứng trong "Cổng còn treo" khi Task 5 đạt.

## Lịch sử review đợt 4 (15/10) — đã gộp vào task

Codex review đợt 4 (`REVIEW-CODEX.md`, mục F10, F11, F14 và bảng hợp đồng 2e) đề xuất "Task 2-R" dạng bổ sung ở cuối plan. Bản này gộp thẳng vào các task, có mã và test nguyên văn, đã chạy:

| Phát hiện | Bản sửa của Codex | Ở bản này |
|---|---|---|
| **F10** — gộp nhịp không nguyên tử giữa hai request | `ghi_nhip` mở `BEGIN IMMEDIATE` trước khi đọc, nhánh không ghi rollback; test hai kết nối | Giữ nguyên `ghi_nhip` (Task 2, thêm docstring). Test đổi cách ép tranh chấp (Task 2 Step 1 giải thích); thêm Step 4b chứng minh RED khi bỏ khoá |
| **F11** — đọc 200 nhịp không đủ cho TTL 15 phút | `tram/suy/kho_nhip.py::doc_nhip`: mọi nhịp trong TTL, fallback 1 nhịp; dùng cho GET và POST; test 201 phiên | Giữ nguyên `doc_nhip` (Task 1, thêm docstring). Bỏ `DOC_TOI_DA`. Test 201 phiên ở Task 1, thêm ca quá hạn → `false` |
| **F14** — timeout mỗi thao tác không phải hạn của cả hook | Sửa lời hứa thành "mỗi thao tác 2 giây; hook 5 giây; cần spike" | Giữ lời hứa đã sửa, **thêm** hạn cả hook 4 giây (`chay_co_han`, luồng nền + `os._exit`) và test; vẫn cần spike H3 |
| Bảng hợp đồng: G2 chờ chốt mở rộng mã Đại ca | — | **D24** thay G2: mã riêng (G23, Task 6) |

Các con số "N₀ + 14 / 2001" và "N₀ + 16 dự kiến" của bản trước là lịch sử; số có hiệu lực ở mục "Sơ đồ đợt chạy".

## Ghi chú triển khai (16/10/2026) — phần code; Task 5 chưa làm

**Code:** Task 1, 2, 3, 4, 6 đã ghép vào `main`. **Task 5 (kiểm chứng chạy thật) chưa làm**, nên chưa có H1–H6, chưa có số đếm Step 5 và chưa đóng gói "Ghi chú triển khai" cuối cùng của Task 5. Mục này sẽ được bổ sung khi Task 5 xong.

| Lần ghép | Task | Commit chính | `pytest` trước → sau | node |
|---|---|---|---|---|
| `b9138a9` `merge: 2e/t1t4` | T1 đèn suy từ nhịp + `/api/van-phong`; T4 `chuNhip`, màu `#f2c14e` | `a377ec0`, `4109d01` | 2054 → 2058 (+4) | 33 → 34 (+1) |
| `85cf15c` `merge: 2e Task 6, 3, 2` | T6 mã điều phối + lệnh; T3 hook máy A; T2 `POST /api/dieu-phoi/nhip` | `bfcc53e`, `4e185b5`, `6edcf46` | 2112 → 2130 (+18) | 34 → 34 |

Số test thật theo từng task: T1 +4, T6 +5, T3 +7, T2 +6 (Python); T4 +1 (node). Tổng **+22 Python, +1 node**, đúng bảng "Sơ đồ đợt chạy" (N₀ + 22, M₀ + 1). Số tuyệt đối thay đổi vì các lát khác ghép xen kẽ. Sau khi bốn lát đã ghép, `main` có 2212 passed, node 38.

**Chỗ lệch plan khi code:** không có. Em đối chiếu từng dòng thêm của 5 commit với văn bản plan (16/10): mọi dòng thêm đều có nguyên văn trong plan. Không sửa `.vue` nào (G21, đúng ý plan). Lát 2f sau đó làm biển phòng, danh sách và khung chi tiết của đèn (Task 12) và ô mã điều phối ở Cài đặt.

**Các quyết định đã áp dụng:** D24 (mã riêng `tram-dieu-phoi-ma`, trạm giữ băm `dieu_phoi_ma_sha256`), D38 (màu đèn `#f2c14e`), D40 (C2–C6: 15 phút và 60 giây; mọi phiên Claude Code trên máy A; giữ đòi header Tailscale; duyệt cả gói hợp đồng mới; chấp nhận lệch G6 — nhịp không có `ma_thao_tac`, đã ghi ngoại lệ vào spec 2 §7).

**Còn lại:**
- **Task 5** (chờ #5 / 2a Task 26 và D6 — Tailscale máy A): H1–H6, số đếm nhịp một ngày (G22), Host thật mà `tailscale serve` chuyển tới. Bead `bs-urj.7` đã đóng ngày 16/10 cho phần code; phần chạy thật ghi vào Task 5.
- Rủi ro (f): nếu `tailscale serve` không gắn header cho yêu cầu không từ trình duyệt thì mọi nhịp bị 403 và đèn không sáng. Khi đó áp dụng C4 (bỏ đòi header ở route nhịp, vẫn đòi mã điều phối).
- Rủi ro (h): `tram chu dat-ma-dai-ca` chưa chặn trùng mã điều phối (chiều ngược của G23). Việc này thuộc lát sau mở lại `tram/nho/ma_dai_ca.py`.
