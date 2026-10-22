# Lát 3b — Mac thợ từ xa qua Tailscale + khe Codex — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use ai-skills:subagent-driven-development (recommended) or ai-skills:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ghép một Mac thợ từ xa vào trạm chủ qua tailnet (`tram chu cap-ma` → `tram tho dang-ky` liệt kê thay đổi rồi chờ `dong-y` → token máy trong Keychain, `tho.yaml`, cấu hình memory MCP, LaunchAgent `tram tho chay`), kiểm máy từ xa (`tram tho kiem`: tag Tailscale, đăng nhập và hạn mức khe Codex), và dựng khe Codex (bộ đọc hạn mức `codex app-server`, bộ đọc stream `codex exec --json`, `ChayCLI` cho Codex, bộ CLI cắm vào vòng `tram tho chay` của 3a-2) — mọi phần phụ thuộc hình dạng dữ liệu Codex cô lập trong adapter, test bằng fixture, **chờ spike S5**.

**Architecture:** Phía trạm thêm bảng `ma_ghep`/`ghep_sai` (cùng `~/.tram/su-kien.db`, tạo lười) và `POST /api/ghep-may` (ngoài nhóm `/api/tho/*` vì máy chưa có token) — đổi mã dùng một lần lấy token máy vào đúng bảng `may_tho` của 3a-1. Phía Mac thợ: `tram/tho/` thêm bước dò chỉ đọc (`do_may`), sinh thay đổi (`mcp_tho`, `launchd_tho`, `khai_khe`), kế hoạch + in (`ke_hoach_dk`), thực hiện sau `dong-y` (`thuc_hien_dk`, `token_may`), và mục kiểm 3b nối vào cuối `kiem_may`. Khe Codex nằm trọn trong `tram/chay_cli/codex/` (`han_muc`, `app_server`, `luong`, `chay`, `bo`) và Task 13 tạo registry rồi nối vòng thợ của 3a-2 (G3).

**Tech Stack:** Python 3.12 (`uv`); FastAPI 0.143.0 (đã có); pydantic ≥ 2.14 (đã có); PyYAML (đã có); `tomllib`, `plistlib`, `difflib`, `urllib`, `subprocess` (stdlib); `pytest`. **Không thêm phụ thuộc nào.**

**Spec:** [docs/specs/2026-10-13-phan-3-may-tho-han-muc.md](../specs/2026-10-13-phan-3-may-tho-han-muc.md) (ĐÃ DUYỆT 13/10) — phần lát **3b**: §3 hàng 3b, §5.1 (token máy), §7.2 (lệnh Codex), §8.1 (nguồn Codex: app-server + rollout), §9.1, §9.2, §9.3, §12 S5, §16 (không Gemini). Đọc kèm: kiến trúc [§7 "Mac thợ"](../specs/2026-10-12-tram-dieu-phoi-kien-truc.md) · spec 1b [§9.2](../specs/2026-10-13-phan-1b-memory.md) (MCP theo phiếu) · [spike hạn mức 12/10](../spikes/2026-10-12-han-muc-cli.md) · [quyết định 13/10](../quyet-dinh/2026-10-13-tra-loi-cau-hoi-gop.md) (#3 Mac thợ gắn tag, #5 chưa duyệt, #15) · plan 3a-1 (G20, G29, G30, G31, "Để 3a-2") · plan 1b-2 (G1, G16, Task 6 `cau_hinh_tho`).

**Không làm:** Gemini CLI (§16); tự cài/cập nhật CLI, tự đăng nhập tài khoản CLI (Đại ca làm tay); tạo user macOS / principal thực thi (S6); push ref tạm từ Mac thợ (S7); trỏ Beads về trạm chủ (G6); tự gắn tag hay đổi cài đặt Tailscale (chỉ kiểm, hướng dẫn); chạy `codex`/`claude` thật, `launchctl`, `security` thật trong test.

> **Đứng sau 3a-2 và 4a-2** (đang viết song song, chưa đọc được). Mọi chỗ plan này dựa vào 3a-2 ghi ở bảng giả định, loại **HỢP ĐỒNG MỚI** (G3, G4, G5) để Codex đối chiếu khi gom review. 4a-2 không có điểm nối trực tiếp — chỉ có thể đụng `tram/api/app.py` (`CAC_TUYEN`, xem "Chuẩn bị").

## Global Constraints

- **Điều kiện tiên quyết:** `main` đã ghép xong `3a-1 → 1b-3 → 2b → 4a-1 → 1b-2 → 3a-2 → 4a-2`; `uv run pytest -q` xanh, số test = **N₀** (đo ở "Chuẩn bị"). N₀ test cũ phải xanh suốt plan; chỉ đổi **hai dòng** trong test cũ của 3a-1 (`"codex"` → `"gemini"` ở `tests/test_api_tho.py`, `tests/test_cau_hinh_tho.py` — Task 3), số test cũ giữ nguyên.
- **TDD:** mỗi task viết test trước, chạy thấy fail (thông báo ở Step 2 là kết quả chạy thật trên bản sao), viết mã, chạy thấy pass. Ngoại lệ duy nhất: Task 14 (chỉ test tích hợp). **Mỗi file nguồn ≤ ~120 dòng** (dài nhất: `tram/phieu/ma_ghep.py` 102, `tram/tho/ke_hoach_dk.py` 97); mọi dòng ≤ 120 ký tự. Định danh tiếng Việt không dấu như mã hiện có. Giờ lưu UTC `YYYY-MM-DDTHH:MM:SSZ`; hàm nghiệp vụ nhận `luc`/`bay_gio` tiêm được.
- **Mỗi task một worktree, một nhánh, một commit**, tạo từ `main` **sau khi đã ghép đợt trước** (xem "Sơ đồ đợt chạy"). Task cùng đợt không sửa chung file. Không push.
- **Không thêm phụ thuộc mới.** HTTP phía thợ bằng `urllib` (`KhachTram` của 3a-1); TOML chỉ đọc bằng `tomllib`, ghi bằng văn bản có dấu mốc.
- **Test không:** gọi `codex`/`claude` thật (kể cả `--version`, `login status`, `app-server` — test dùng script giả chạy bằng `sys.executable` hoặc `chay` tiêm), gọi mạng (HTTP đi qua `mo` tiêm hoặc app ASGI trong bộ nhớ), đọc/ghi Keychain thật (`security` qua `chay` tiêm), chạy `launchctl`, `tailscale` thật, đụng `~/.tram` thật (`TRAM_HOME` tạm — `tests/conftest.py`), tạo user macOS, đọc file đăng nhập CLI. Test Git đặt `GIT_CONFIG_GLOBAL=/dev/null` (`tests/git_gia.py`).
- **Bản giả và fixture chỉ ở `tests/`** (`tests/du_lieu/codex/*`, `tests/tho_dk_gia.py`), ghi rõ "CHỈ DÙNG TRONG TEST" và "chờ spike S5 — hình dạng chưa xác minh"; mã `tram/` không import chúng. **Không đánh dấu khe Codex sẵn sàng bằng fixture** — S5 là cổng chạy thật (mục "Để sau").
- **Bí mật:** mã ghép và token máy không vào sự kiện, log, file, argv (`ps`), thông báo lỗi; trạm chỉ lưu sha256 của cả hai; token qua stdin của `security -i`; phản hồi ghép `Cache-Control: no-store`. Log CLI Codex che `ma_giao` (`che_ma_giao` của 3a-1).
- **Thao tác chạm hệ thống** (Keychain, `~/Library/LaunchAgents`, cấu hình CLI của khe) chỉ sau khi in **kế hoạch liệt kê** và Đại ca gõ `dong-y` (Q15, khuôn `tram chu cai-dat`).
- Lệnh test: `uv run pytest -q` từ thư mục worktree của task.

## Phụ thuộc đã có (main + plan trước)

| Thứ dùng | Ở đâu | Plan dùng ở |
|---|---|---|
| `KhoPhieu(duong_dan)`: `.db`, `.giao_dich()`, `.ghi_su_kien(du_an, loai, du_lieu, *, luc, …)`; `DU_AN_TRAM`, `chuoi_gio`, `mo_kho_phieu()`; bảng `may_tho(may_id, bam_token, tao_luc, go_luc)` | `tram/phieu/kho.py`, `luoc_do.py` (3a-1 Task 13) | Task 1, 9 |
| `MAY_RE`, `cap_token_may`, `xac_thuc_may`, `go_may` (token = `secrets.token_urlsafe(32)`, lưu sha256 hex) | `tram/phieu/may.py` (3a-1 Task 20) | Task 1, 9, 14 |
| `cac_khe(kho)` | `tram/phieu/khe.py` (3a-1 Task 15) | Task 3 (test) |
| `router` `/api/tho/*` + `KheDangKy`, `ThanDangKy` (**sửa** Task 3); `ThanNhip(han_muc: HanMuc)` | `tram/api/tho.py` (3a-1 Task 23), `tram/phieu/nhip.py` (Task 22) | Task 3, 14 |
| `CAC_TUYEN`, dòng `from tram.api import …` (**sửa** Task 9) — bản sau 1b-3 Task 9 + 2b Task 11 | `tram/api/app.py` | Task 9 |
| `PhuThuocApi.mo_kho_phieu`, `.dong_ho` | `tram/api/phu_thuoc.py` (3a-1 Task 23) | Task 9 |
| `KheCauHinh`, `CauHinhTho(.khe_id)`, `nap_cau_hinh_tho`, `TEN_KHE_RE`, `VAI`, `API_RE` (**sửa** Task 3: thêm `CLI`) | `tram/tho/cau_hinh.py` (3a-1 Task 9) | Task 3, 10, 11, 12 |
| `KEYCHAIN_THO`, `doc_token_may(*, chay)`, `KhachTram(url, token, mo, thoi_gian_cho).goi(method, duong, than, *, xac_thuc)`, `LoiKhachTram` | `tram/tho/khach.py` (3a-1 Task 24) | Task 6, 11 |
| `MucKiem`, `DauDo(ping, du_an, which, chay, con_trong, thu_muc_kho)`, `kiem_may` (**sửa** Task 12), `in_ket_qua` | `tram/tho/kiem_may.py` (3a-1 Task 24) | Task 12 |
| `them_lenh_tho(sub, chu)` (**sửa** Task 9, 11) | `tram/tho/lenh.py` (3a-1 Task 24) | Task 9, 11 |
| `CuaSo`, `HanMuc` (`nguon` ∈ `stream|app-server|log|regex|chua_co`), `ten_cua_so`, `lam_moi`; `duoc_nhan`; Protocol `NguonHanMuc`; `KetQuaChay`, `ket_thuc_tu`, Protocol `ChayCLI` | `tram/han_muc/*.py`, `tram/chay_cli/giao_dien.py` (3a-1 Task 4) | Task 2, 7, 8, 13 |
| `che_ma_giao(van_ban, ma_giao)` | `tram/phieu/mo_hinh.py` (3a-1 Task 11) | Task 8 |
| `PATH_HE_THONG` | `tram/chu/launchd.py` (2a) | Task 6 |
| `CauHinhTram.ten_may_b`, `nap_cau_hinh_tram()` | `tram/cau_hinh/tram.py` (2a) | Task 9 |
| `TEN_MAY_CHU = "tram-nho"`, `cau_hinh_tho()` (header `X-Tram-Giao-Id: ${TRAM_GIAO_ID}`, `X-Tram-Ma-Giao: ${TRAM_MA_GIAO}`, url `${TRAM_NHO_URL}`) | `tram/nho/cau_hinh_mcp.py` (1b-2 Task 6) | Task 5 |
| `BO_CLI`, Protocol `BoCLI` (**3b tạo ở Task 13**, nối nền 3a-2); `tram tho chay`, cài token/launchd máy B (**3a-2 — G4, G5**) | `tram/chay_cli/bo_cli.py`, vòng thợ (3a-2) | Task 13 |
| `tao_tram(tmp_path, *, chon, token_noi_bo, dang_ky)` → `TramGia(.goi, .toi, .kho, .token, .gio, .app)`; `de_xuat()`; `kho_tam`, `LUC`; `goi(app, …)`; `git`, `ghi`, `tao_repo`, `MOI_TRUONG`; fixture `tram_home_tam` | `tests/tho_api_gia.py`, `phieu_gia.py`, `kho_phieu_gia.py`, `asgi_gia.py`, `git_gia.py`, `conftest.py` | mọi task |

## Câu hỏi / giả định

Chỗ spec để ngỏ — Em chọn phương án an toàn nhất, không tự mở rộng phạm vi. Cột "Loại": **HỢP ĐỒNG MỚI** = giao diện/hành vi phần khác (3a-2, 2b, 2c, phần 4) dựa vào hoặc plan này dựa vào plan cùng đợt chưa đọc được — **Đại ca/Codex chốt** trước khi thực thi; **lệch chữ spec** = làm khác câu chữ spec; **giả định** = chi tiết thực thi, Đại ca gạch nếu không đồng ý.

| # | Chỗ mơ hồ | Chọn | Vì sao | Loại |
|---|---|---|---|---|
| G1 | Đổi mã ghép lấy token ở đâu | `POST /api/ghep-may {ma}` (ngoài nhóm `/api/tho/*` — máy chưa có token máy để gửi; 3a-1 G31 nói mọi `/api/tho/*` mang Bearer). 200 `{may_id, token}` + `Cache-Control: no-store`; 403 `{loi}` mã sai/đã dùng/hết hạn (không nói mã thuộc máy nào); 429 khi bị khoá; 422 thân sai. Không dùng danh tính Tailscale | Giữ nguyên luật "mọi `/api/tho/*` có Bearer" của 3a-1 | **HỢP ĐỒNG MỚI** |
| G2 | Dạng và vòng đời mã ghép (§9.2 chỉ nói "dùng một lần, 10 phút") | `tram chu cap-ma <may_id>` — mã **gắn với `may_id`** do Đại ca đặt lúc cấp; 12 ký tự Crockford base32 (60 bit) in `XXXX-XXXX-XXXX`, nhập không phân biệt hoa thường/khoảng trắng/gạch; trạm chỉ lưu sha256. Cấp mã mới huỷ mã cũ chưa dùng của máy đó. Máy đang có token còn hiệu lực → từ chối cấp (`tram chu go-may` trước). Sai 5 lần trong 10 phút → khoá đổi mã 10 phút và huỷ mọi mã đang chờ. Bảng `ma_ghep`, `ghep_sai` trong `su-kien.db`, tạo lười (`CREATE TABLE IF NOT EXISTS`). Sự kiện `_tram` mới: `may.cap_ma {may_id, het_luc}`, `may.ghep {may_id}`, `may.ghep_sai {so_lan}` — không chứa mã/token | Mã qua tailnet có thể bị dò: entropy + khoá + một lần. Đặt `may_id` ở trạm thì Mac thợ không tự xưng tên máy khác | **HỢP ĐỒNG MỚI** (sự kiện mới §10) |
| G3 | Nối khe Codex vào vòng thợ | 3b Task 13 **tạo** BoCLI/BO_CLI và vá ngu_canh/mot_lan/principal/vong_khe trên mã mẫu 3a-2. Factory nhận boc, kill, khe_id, callback pid/hạn mức, tran_token_ra; lenh nhận settings/mcp của Claude. CODEX_HOME qua whitelist sudo; parser chọn theo k.cli; app-server đọc lúc rảnh mỗi 300 giây. | 3a-2 thực chưa có registry; hai dòng nối cũ không đủ. Không dùng module thế chỗ làm bằng chứng tích hợp. | **HỢP ĐỒNG MỚI — đổi** |
| G4 | Service quản lý thợ | B dùng LaunchDaemon 3a-2; Mac từ xa mới dùng LaunchAgent vn.tram.tho. Đăng ký từ chối khi đã có daemon/tho.yaml, chỉ staging plist khi principal còn trống; kích hoạt sau cấu hình và S2/S6/S7. | Tránh hai manager và vòng restart do cấu hình chưa đủ; không đổi lựa chọn §14. | **HỢP ĐỒNG MỚI — đổi** |
| G5 | Biến môi trường memory MCP cho CLI trên Mac thợ | Task 3 mở schema URL HTTPS `/nho/mcp`; Task 10/11 ghi chay.nho_url khi bật memory, `--khong-nho` ghi null; vòng 3a-2 đặt `TRAM_GIAO_ID`, `TRAM_MA_GIAO` và `TRAM_NHO_URL` cho CLI khi memory bật (spec 3 §7.2); với `tram_api` https thì `TRAM_NHO_URL = <tram_api>/nho/mcp` (`tailscale serve` đưa `/nho` → 7710 — N2). Khe Codex: URL ghi thẳng trong `config.toml` (Codex không mở rộng biến trong `url` — chờ S5), header lấy từ `TRAM_GIAO_ID`/`TRAM_MA_GIAO` qua `env_http_headers` | 1b-2 G16 để `${TRAM_NHO_URL}` cho Claude; Codex cần URL tĩnh | **HỢP ĐỒNG MỚI — đổi** (nối thật vào 3a-2) |
| G6 | Kiến trúc §7: `dang-ky` "trỏ beads host về trạm chủ" | **Không làm.** Kiến trúc §7 cùng đoạn nói "máy thợ không được cấp quyền ghi Beads"; spec 3 §9.2 (đã duyệt, cụ thể hơn) không liệt kê; vai thợ cấm `bd` (§7.2). Kế hoạch in rõ dòng "không trỏ Beads" | An toàn hơn và đúng spec đã duyệt | **lệch chữ spec** (kiến trúc nháp) |
| G7 | "Khai vai cho từng CLI" — cú pháp | `--khe <ten>:<cli>:<vai,…>:<tên gợi nhớ>` (lặp được, bắt buộc ≥ 1); `--thu-muc-khe` (mặc định `~/tram/khe`, thư mục cấu hình của khe = `<đó>/<ten>`); `--khong-nho` (bỏ cấu hình MCP); `--dong-y` (bỏ bước hỏi). `principal` để trống (S6). Cùng luật kiểm với `nap_cau_hinh_tho` (tên, `cli`, vai, tên gợi nhớ không phải email) | Spec chỉ ghi `--tram-chu`, `--ma`; khai không tương tác thì test được và lặp lại được | giả định |
| G8 | Khi nào `dang-ky` từ chối | Từ chối (mã 2, chưa đổi gì): `--tram-chu` không phải `https://<tên>.<miền>`; máy **chưa gắn `tag:tram-tho`** (đọc `tailscale status --json` → `Self.Tags`; không thấy Tailscale cũng là chưa gắn); thiếu `tram` hoặc CLI của một khe; khai khe sai. Chưa đăng nhập CLI hay chưa có thư mục khe → **chỉ cảnh báo** (Đại ca đăng nhập sau) | #3: Mac thợ từ xa là thiết bị gắn tag, nếu không `tailscale serve` gắn danh tính Đại ca cho mọi yêu cầu từ máy thợ | giả định |
| G9 | "Dò trạng thái đăng nhập không đọc file đăng nhập" | Codex: `codex login status` với `CODEX_HOME` của khe — mã 0 = đã đăng nhập (**chờ S5** xác nhận mã/chữ). Claude: lệnh trạng thái chốt ở S2 (3a-2) → 3b báo "chưa kiểm được"; `tram tho kiem` giữ mục đăng nhập Claude như 3a-1/3a-2. Không chép đầu ra lệnh trạng thái (có thể chứa email) | §9.3: trạng thái qua lệnh của CLI | giả định |
| G10 | Ghi cấu hình MCP vào claude/codex của khe | Claude: `claude mcp remove --scope user tram-nho` (được lỗi) rồi `claude mcp add-json --scope user tram-nho '<cau_hinh_tho()>'` với `CLAUDE_CONFIG_DIR` của khe — trạm không mở `.claude.json` (có thông tin tài khoản). Codex: khối có dấu mốc ở **cuối** `$CODEX_HOME/config.toml` (`[mcp_servers.tram-nho]`, `url`, `env_http_headers`), kế hoạch in diff; chạy lại thay khối cũ; trùng tên ngoài khối hoặc TOML hỏng → từ chối. Mặc định ghi; `--khong-nho` bỏ. **Chờ N2 + S5** | 1b-2 "Để sau": "ghi cấu hình MCP vào claude/codex của máy thợ, có diff + dong-y" | giả định |
| G11 | Thứ tự thực hiện, lỗi giữa chừng | Ghép (tiêu mã) → Keychain → `tho.yaml` (kiểm bằng `nap_cau_hinh_tho` trước khi thay; bản cũ → `tho.yaml.bak`) → file (`config.toml` 0600, plist 0644; ghi nguyên tử) → lệnh MCP Claude → `POST /api/tho/dang-ky` → nạp launchd (cuối). Lỗi → dừng, in hướng dẫn: xin mã mới (`tram chu cap-ma`), nếu máy đã nhận token thì `tram chu go-may` trước. Không tự lùi | Launchd cuối cùng: thợ không chạy với cấu hình nửa vời | giả định |
| G12 | Ghi token máy vào Keychain | `security -i` qua **stdin**: `add-generic-password -U -s tram-tho-token -a <may_id> -w "<token>"`; ghi xong đọc lại bằng `doc_token_may` và so hằng thời gian. Kiểm dạng giá trị trạm trả về trước khi ghép dòng lệnh: `may_id` `[A-Za-z0-9][A-Za-z0-9-]{0,31}`, token `[A-Za-z0-9_-]{32,128}`. Chạy thật **chờ S6** (Keychain của tài khoản quản lý thợ khi không có phiên GUI) | Như `tao_token_nho` của 1b-1; token không vào argv | giả định |
| G13 | Chuẩn hoá hạn mức Codex | Tên cửa sổ theo thời lượng (`ten_cua_so`: 300 → `5h`, 10080 → `tuan`, khác → `<tên gốc>:<n>m`), không theo primary/secondary. `resets_at`/`resetsAt`: giây epoch (> 10¹² coi là mili giây) hoặc chuỗi ISO. Trường thiếu/sai (phần trăm ngoài 0–100, thời lượng ≤ 0 hoặc lẻ) → bỏ cửa sổ đó (thành chưa biết ở `lam_moi`), không giả 0%. App-server → `nguon="app-server"`, `doc_luc` = lúc hỏi; rollout → `nguon="log"`, `doc_luc` = `timestamp` của dòng. `codex exec --json` **không mang hạn mức** (theo hiểu biết hiện tại) → `NguonHanMucCodex.doc_dong` chỉ đọc dòng rollout; hết hạn mức = thông điệp `error`/`turn.failed` khớp `usage limit|rate limit|too many requests|429|quota`; chưa đăng nhập: `not logged in|log in again|unauthorized|401`. **Chờ S5** | Spec §8.1; spike hạn mức 12/10 | giả định |
| G14 | Giao thức `codex app-server` | JSON mỗi dòng, không trường `jsonrpc`: `initialize` (id 0, `clientInfo.name = "tram"`) → chờ trả lời → `initialized` → `account/rateLimits/read` (id 1); bỏ qua thông báo/dòng rác; quá 20 giây giết cả nhóm tiến trình. Môi trường tối thiểu: `PATH, HOME, LANG, USER, TMPDIR` + `CODEX_HOME` — không biến `TRAM_*`. Chu kỳ khi rảnh 300 giây (§8.1). Đọc lỗi → `None` → cửa sổ chưa biết, vẫn nhận việc (#15). **Chờ S5** | Tài liệu app-server theo spike 12/10 | giả định |
| G15 | Lệnh `codex exec` (§7.2 "sandbox ghi trong worktree") | `codex exec --json --cd <worktree> --sandbox workspace-write -c approval_policy="never" -c sandbox_workspace_write.network_access=false --add-dir <thư mục phiếu> -` (prompt qua stdin). **Không bao giờ** cờ bỏ qua sandbox/quyền (Q6). `vai`, `lenh_cho_phep` không vào lệnh: Codex không có file quyền theo vai như Claude — lớp bổ sung là prompt vai + kiểm diff của phần 4; hàng rào thật là sandbox + principal (S6). Không mở common-dir; S6 phải chốt quyền commit đủ dùng mà không cho sửa config/hooks/ref khe khác. **Chờ S5** (cờ, `.git` có bị sandbox khoá không, mạng tắt thật không) | Đường đi ít quyền nhất mà `tram bao` vẫn commit và ghi hàng đợi được | **lệch chữ spec** (không có lớp quyền theo vai cho Codex) |
| G16 | Token của Codex | `input_tokens` của Codex **gồm** phần cache → `token_vao = input − cached`, `token_cache_doc = cached`, `token_ra = output_tokens`, `token_cache_ghi = 0`, `mo_hinh = None`; cộng qua mọi `turn.completed`. **Chờ S5** | Cùng nghĩa với cột của Claude để Usage (2b) cộng được | giả định |
| G17 | `tram tho kiem` cho máy từ xa | Nối vào cuối `kiem_may` (3a-1): khe Codex — **thay** mục `<khe> đăng nhập` bằng kết quả `codex login status`; thêm `<khe> hạn mức` (xanh kèm số đo, **vàng** khi không đọc được — #15 vẫn nhận việc); `tram_api` https → thêm `tailscale tag` (đỏ nếu chưa gắn). Mục cách ly/quyền ghi worktree giữ như 3a-1/3a-2 | §9.3 + #3 | giả định |
| G18 | Log của lần chạy Codex | stdout + stderr gộp, che `ma_giao` (lấy từ `env["TRAM_MA_GIAO"]`) từng dòng **trước** khi ghi và băm; `digest_log = "sha256:<hex>"` trên log đã che | §7.3 mục 6, §7.8 | giả định |
| G19 | `cli` của khe | `claude` \| `codex` ở `tho.yaml` (hằng `CLI` mới trong `tram/tho/cau_hinh.py`) và `KheDangKy.cli` của `/api/tho/dang-ky`; Gemini → lỗi. 2b/2c/phần 4 sẽ thấy `cli: "codex"` trong `khe.dang_ky`/`trang_thai_khe` | §3 hàng 3b, §16 | **HỢP ĐỒNG MỚI** (đổi 3a-1) |
| G20 | File đụng chung với plan khác | `tram/api/app.py` (bản vá trên nền 1b-3 + 2b; 4a-2 có thể thêm tuyến), `tram/tho/lenh.py`, `tram/tho/kiem_may.py`, `tram/tho/cau_hinh.py`, `tram/api/tho.py` (3a-1; 3a-2 có thể sửa), `tram/chay_cli/bo_cli.py` (3a-2). Mỗi bản vá có **dòng neo**; `git apply --check` lỗi vì plan trước đã sửa cạnh đó → áp tay đúng các dòng `+` cạnh dòng neo, giữ phần của plan trước, chạy đủ kiểm, ghi vào mô tả commit; dòng neo mất → **dừng**, báo người điều phối | Cùng cách 2b G2 | giả định |

## File Structure

```
tram/
  phieu/ma_ghep.py            # mã ghép: cấp, đổi lấy token máy, khoá khi dò                       — Task 1
  api/ghep.py                 # POST /api/ghep-may                                                — Task 9
  api/app.py                  # (sửa) thêm ghep.router vào CAC_TUYEN                              — Task 9
  api/tho.py                  # (sửa) KheDangKy.cli nhận "codex"                                  — Task 3
  chu/cap_ma.py               # tram chu cap-ma <may_id>                                          — Task 9
  chay_cli/codex/__init__.py  # (rỗng)                                                            — Task 2
  chay_cli/codex/han_muc.py   # chuẩn hoá app-server + rollout, NguonHanMucCodex, thong_diep_loi  — Task 2
  chay_cli/codex/app_server.py# hoi_app_server (JSON-RPC stdio), doc_han_muc_ranh                 — Task 7
  chay_cli/codex/luong.py     # DocLuongCodex: stream exec --json → KetQuaChay                    — Task 8
  chay_cli/codex/chay.py      # ChayCodex (ChayCLI): nhóm tiến trình, dừng, log che ma_giao        — Task 8
  chay_cli/codex/bo.py        # lenh_codex, BoCodex (bộ CLI của khe Codex)                        — Task 13
  chay_cli/bo_cli.py          # (3b tạo) registry Claude/Codex + patches vòng thợ                                   — Task 13
  tho/cau_hinh.py             # (sửa) CLI = ("claude", "codex")                                   — Task 3
  tho/do_may.py               # dò CLI + đăng nhập (lệnh trạng thái), tag Tailscale — chỉ đọc     — Task 4
  tho/mcp_tho.py              # cấu hình memory MCP cho Claude (lệnh) / Codex (khối config.toml)  — Task 5
  tho/launchd_tho.py          # plist vn.tram.tho + lệnh nạp                                      — Task 6
  tho/token_may.py            # ghi token máy vào Keychain qua stdin, đọc lại                     — Task 6
  tho/khai_khe.py             # --khe <ten>:<cli>:<vai>:<tên>, nội dung tho.yaml                  — Task 10
  tho/ke_hoach_dk.py          # DauDoDK, KeHoachDangKy, lap_ke_hoach_dk, in_ke_hoach_dk           — Task 10
  tho/thuc_hien_dk.py         # HieuUng, ghep_that, dang_ky_that, thuc_hien_dk                    — Task 11
  tho/lenh_dang_ky.py         # tram tho dang-ky                                                  — Task 11
  tho/lenh.py                 # (sửa) đăng ký cap-ma (Task 9), dang-ky (Task 11)
  tho/kiem_3b.py              # bo_sung_3b: mục kiem của khe Codex + tag Tailscale                — Task 12
  tho/kiem_may.py             # (sửa) cuối kiem_may gọi bo_sung_3b                                — Task 12
tests/
  du_lieu/codex/  app_server_rate_limits.json, rollout.jsonl (2) · app_server_gia.py (7)
                  exec_xong.jsonl, exec_het_han_muc.jsonl, exec_chua_dang_nhap.jsonl, exec_gia.py (8)
  tho_dk_gia.py (10)
  test_ma_ghep.py (1) · test_codex_han_muc.py (2) · test_khe_codex.py + test_api_tho.py, test_cau_hinh_tho.py sửa (3)
  test_do_may.py (4) · test_mcp_tho.py (5) · test_launchd_token_tho.py (6) · test_codex_app_server.py (7)
  test_codex_chay.py (8) · test_ghep_may.py (9) · test_ke_hoach_dk.py (10) · test_thuc_hien_dk.py (11)
  test_kiem_3b.py (12) · test_bo_codex.py (13) · test_kich_ban_3b.py (14)
```

Fixture và script giả (`tests/du_lieu/codex/*`) **CHỈ DÙNG TRONG TEST**, dựng theo hiểu biết hiện tại về Codex — **chờ spike S5**; script giả chạy bằng `sys.executable`, không bao giờ là `codex` thật.

## Chuẩn bị (người điều phối)

```bash
cd "/Users/dai-ca/Developer/Ben Station"
git status --short                     # chỉ được có .beads/interactions.jsonl, .DS_Store — không đụng
uv run pytest -q                       # ghi lại số passed = N₀ (main sau 3a-2, 4a-2)
test -f tram/tho/mot_lan.py                    # nền 3a-2 thật; registry do Task 13 tạo
test -f tram/tho/ngu_canh.py                   # đối chiếu bản vá Task 13 với 3a-2
grep -n "them_lenh_tho(sub, chu)" tram/cli_dich_vu.py tram/tho/lenh.py   # dòng neo Task 9, 11
grep -n "def kiem_may" tram/tho/kiem_may.py                              # dòng neo Task 12
grep -n "^CAC_TUYEN" tram/api/app.py                                     # dòng neo Task 9
```

**Mỗi task một worktree**, tạo từ `main` **sau khi đã ghép mọi task của đợt trước**:

```bash
N=1   # số task
git worktree add .worktrees/3b-t$N -b 3b/t$N main
cd .worktrees/3b-t$N && uv sync && uv run pytest -q    # kỳ vọng: số "sau đợt trước" trong Sơ đồ đợt chạy
```

Cuối mỗi task: người thực thi commit trong worktree của mình; người điều phối kiểm (mọi dòng thêm có nguyên văn trong plan; số test đúng kỳ vọng) rồi `git merge --no-ff 3b/t$N` vào `main` (không push). Ghép xong cả đợt → `uv run pytest -q` trên `main` phải bằng số "sau đợt" trong bảng.

Mã: file **mới** cho nguyên văn đầy đủ; file **có sẵn** cho bản vá `git apply` (unified diff, chạy từ gốc worktree: lưu khối `diff` ra file rồi `git apply --check <file> && git apply <file>`). Bản vá không áp được → làm theo G20 (áp tay cạnh dòng neo, hoặc dừng). File rỗng (`__init__.py`) tạo bằng `mkdir -p … && touch …`.

Dòng ghi công trong lệnh commit: thay `<model đang thực thi>` bằng đúng tên model của người thực thi task đó.

---

### Task 1: Mã ghép phía trạm — cấp, đổi lấy token máy, khoá khi dò

**Độ khó:** `kho` · **Đợt:** 1 · **Song song với:** Task 2, 3, 4, 5, 6 · **Phải xong (đã ghép vào `main`) trước khi bắt đầu:** — (chỉ cần `main` N₀)

**Files:**
- Create: `tram/phieu/ma_ghep.py`
- Test: `tests/test_ma_ghep.py` (mới)

**Interfaces:**
- Consumes: `KhoPhieu` (`.db`, `.giao_dich()`, `.ghi_su_kien`), `DU_AN_TRAM`, `chuoi_gio` (`tram/phieu/kho.py`); `MAY_RE` (`tram/phieu/may.py`); bảng `may_tho` (3a-1). Test: `kho_tam`, `LUC` (`tests/kho_phieu_gia.py`), `cap_token_may`, `xac_thuc_may`.
- Produces: `tram/phieu/ma_ghep.py`: `MaGhep(ma, may_id, het_luc)`, `MaGhepSai`, `GhepBiKhoa`, `LUOC_DO_GHEP`, `cap_ma_ghep(kho, may_id, *, luc) -> MaGhep` (ValueError khi `may_id` sai hoặc máy đang có token), `doi_ma_ghep(kho, ma, *, luc) -> tuple[str, str]` (`(may_id, token)`; token cùng dạng/cách băm với `cap_token_may`).

- [ ] **Step 1: Viết test thất bại**

`tests/test_ma_ghep.py` (mới):

```python
from datetime import timedelta

import pytest

from kho_phieu_gia import LUC, kho_tam
from tram.phieu.ma_ghep import GhepBiKhoa, MaGhepSai, cap_ma_ghep, doi_ma_ghep
from tram.phieu.may import cap_token_may, xac_thuc_may


def _loai(kho):
    return [r[0] for r in kho.db.execute("SELECT loai FROM su_kien WHERE du_an = '_tram' ORDER BY id")]


def test_cap_roi_doi_mot_lan_ra_token_may(tmp_path):
    kho = kho_tam(tmp_path)
    mg = cap_ma_ghep(kho, "C", luc=LUC)
    assert mg.may_id == "C" and mg.het_luc == "2026-10-13T03:10:00Z"
    assert len(mg.ma) == 14 and mg.ma[4] == mg.ma[9] == "-"
    may_id, token = doi_ma_ghep(kho, mg.ma.lower().replace("-", " "), luc=LUC + timedelta(minutes=9))
    assert may_id == "C" and xac_thuc_may(kho, token) == "C"
    with pytest.raises(MaGhepSai):
        doi_ma_ghep(kho, mg.ma, luc=LUC + timedelta(minutes=9))                 # dùng một lần
    bang = str(kho.db.execute("SELECT * FROM ma_ghep").fetchall()) + str(kho.db.execute(
        "SELECT du_lieu FROM su_kien").fetchall())
    assert mg.ma not in bang and mg.ma.replace("-", "") not in bang and token not in bang
    assert _loai(kho) == ["may.cap_ma", "may.ghep", "may.ghep_sai"]


def test_het_han_sau_10_phut_va_ma_moi_huy_ma_cu(tmp_path):
    kho = kho_tam(tmp_path)
    cu = cap_ma_ghep(kho, "C", luc=LUC)
    with pytest.raises(MaGhepSai):
        doi_ma_ghep(kho, cu.ma, luc=LUC + timedelta(minutes=10))
    cu = cap_ma_ghep(kho, "C", luc=LUC)
    moi = cap_ma_ghep(kho, "C", luc=LUC)
    with pytest.raises(MaGhepSai):
        doi_ma_ghep(kho, cu.ma, luc=LUC)
    assert doi_ma_ghep(kho, moi.ma, luc=LUC)[0] == "C"


def test_may_dang_co_token_khong_cap_ma(tmp_path):
    kho = kho_tam(tmp_path)
    cap_token_may(kho, "B", luc=LUC)
    with pytest.raises(ValueError, match="go-may"):
        cap_ma_ghep(kho, "B", luc=LUC)
    with pytest.raises(ValueError):
        cap_ma_ghep(kho, "C/x", luc=LUC)
    mg = cap_ma_ghep(kho, "C", luc=LUC)
    cap_token_may(kho, "C", luc=LUC)                                              # máy C được ghép đường khác
    with pytest.raises(MaGhepSai):
        doi_ma_ghep(kho, mg.ma, luc=LUC)


def test_sai_5_lan_trong_10_phut_khoa_va_huy_moi_ma_dang_cho(tmp_path):
    kho = kho_tam(tmp_path)
    mg = cap_ma_ghep(kho, "C", luc=LUC)
    for i in range(5):
        with pytest.raises(MaGhepSai):
            doi_ma_ghep(kho, "AAAA-AAAA-AAA" + str(i), luc=LUC + timedelta(seconds=i))
    with pytest.raises(GhepBiKhoa):
        doi_ma_ghep(kho, mg.ma, luc=LUC + timedelta(minutes=1))
    with pytest.raises(MaGhepSai):                                                # hết khoá nhưng mã đã bị huỷ
        doi_ma_ghep(kho, mg.ma, luc=LUC + timedelta(minutes=11))
    assert doi_ma_ghep(kho, cap_ma_ghep(kho, "C", luc=LUC + timedelta(minutes=11)).ma,
                       luc=LUC + timedelta(minutes=11))[0] == "C"
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_ma_ghep.py -q`
Expected: FAIL — `1 error` (`ModuleNotFoundError: No module named 'tram.phieu.ma_ghep'`)

- [ ] **Step 3: Viết mã**

`tram/phieu/ma_ghep.py` (mới):

```python
"""Mã ghép Mac thợ từ xa (spec 3 §9.2) — phía trạm. `tram chu cap-ma <may_id>` cấp mã dùng MỘT lần, hết hạn sau
10 phút; `POST /api/ghep-may {ma}` đổi mã lấy token máy (cùng bảng `may_tho` của 3a-1, trạm chỉ giữ sha256).

Mã = 12 ký tự Crockford base32 (60 bit), in dạng `XXXX-XXXX-XXXX`; trạm chỉ lưu sha256 của mã đã chuẩn hoá. Sai 5 lần
trong 10 phút → khoá đổi mã 10 phút và huỷ mọi mã đang chờ (chặn dò mã qua tailnet). Sự kiện `_tram`: `may.cap_ma`,
`may.ghep`, `may.ghep_sai` — không chứa mã hay token."""
import hashlib
import re
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta

from tram.phieu.kho import DU_AN_TRAM, KhoPhieu, chuoi_gio
from tram.phieu.may import MAY_RE

BANG_CHU = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
DO_DAI, PHUT_HIEU_LUC, SAI_TOI_DA, PHUT_KHOA = 12, 10, 5, 10
LUOC_DO_GHEP = """
CREATE TABLE IF NOT EXISTS ma_ghep (
  bam_ma TEXT PRIMARY KEY, may_id TEXT NOT NULL, tao_luc TEXT NOT NULL, het_luc TEXT NOT NULL,
  dung_luc TEXT, huy_luc TEXT);
CREATE TABLE IF NOT EXISTS ghep_sai (id INTEGER PRIMARY KEY, luc TEXT NOT NULL);
"""


class MaGhepSai(Exception):
    pass


class GhepBiKhoa(Exception):
    pass


@dataclass(frozen=True)
class MaGhep:
    ma: str
    may_id: str
    het_luc: str


def _bam(ma: str) -> str:
    return hashlib.sha256(re.sub(r"[\s-]", "", ma).upper().encode()).hexdigest()


def _co_token(db, may_id: str) -> bool:
    return db.execute("SELECT 1 FROM may_tho WHERE may_id = ? AND go_luc IS NULL", (may_id,)).fetchone() is not None


def cap_ma_ghep(kho: KhoPhieu, may_id: str, *, luc: datetime) -> MaGhep:
    """Mã mới cho `may_id` (huỷ mã cũ chưa dùng của máy đó). Máy đang có token → ValueError (gỡ trước)."""
    if not MAY_RE.fullmatch(may_id):
        raise ValueError(f"may_id không hợp lệ: {may_id!r}")
    kho.db.executescript(LUOC_DO_GHEP)
    ma = "".join(secrets.choice(BANG_CHU) for _ in range(DO_DAI))
    het = chuoi_gio(luc + timedelta(minutes=PHUT_HIEU_LUC))
    with kho.giao_dich() as db:
        if _co_token(db, may_id):
            raise ValueError(f"Máy {may_id} đang có token — chạy `tram chu go-may {may_id}` trước nếu muốn ghép lại")
        db.execute("UPDATE ma_ghep SET huy_luc = ? WHERE may_id = ? AND dung_luc IS NULL AND huy_luc IS NULL",
                   (chuoi_gio(luc), may_id))
        db.execute("INSERT INTO ma_ghep (bam_ma, may_id, tao_luc, het_luc) VALUES (?,?,?,?)",
                   (_bam(ma), may_id, chuoi_gio(luc), het))
        kho.ghi_su_kien(DU_AN_TRAM, "may.cap_ma", {"may_id": may_id, "het_luc": het}, luc=luc)
    return MaGhep(f"{ma[:4]}-{ma[4:8]}-{ma[8:]}", may_id, het)


def _doi(kho: KhoPhieu, db, ma: str, luc: datetime) -> tuple[str, str] | str:
    """Trong giao dịch. Trả (may_id, token), hoặc chuỗi lý do thất bại — người gọi raise SAU khi commit."""
    tu = chuoi_gio(luc - timedelta(minutes=PHUT_KHOA))
    if db.execute("SELECT COUNT(*) FROM ghep_sai WHERE luc > ?", (tu,)).fetchone()[0] >= SAI_TOI_DA:
        return "khoa"
    h = db.execute("SELECT may_id FROM ma_ghep WHERE bam_ma = ? AND dung_luc IS NULL AND huy_luc IS NULL"
                   " AND het_luc > ?", (_bam(ma), chuoi_gio(luc))).fetchone()
    if h is None:
        db.execute("INSERT INTO ghep_sai (luc) VALUES (?)", (chuoi_gio(luc),))
        so = db.execute("SELECT COUNT(*) FROM ghep_sai WHERE luc > ?", (tu,)).fetchone()[0]
        if so >= SAI_TOI_DA:
            db.execute("UPDATE ma_ghep SET huy_luc = ? WHERE dung_luc IS NULL AND huy_luc IS NULL", (chuoi_gio(luc),))
        kho.ghi_su_kien(DU_AN_TRAM, "may.ghep_sai", {"so_lan": so}, luc=luc)
        return "sai"
    may_id = h[0]
    db.execute("UPDATE ma_ghep SET dung_luc = ? WHERE bam_ma = ?", (chuoi_gio(luc), _bam(ma)))
    if _co_token(db, may_id):
        return "sai"
    token = secrets.token_urlsafe(32)                 # cùng dạng và cách băm với `cap_token_may` (3a-1)
    db.execute("INSERT INTO may_tho (may_id, bam_token, tao_luc) VALUES (?,?,?) ON CONFLICT(may_id) DO UPDATE"
               " SET bam_token = excluded.bam_token, tao_luc = excluded.tao_luc, go_luc = NULL",
               (may_id, hashlib.sha256(token.encode()).hexdigest(), chuoi_gio(luc)))
    kho.ghi_su_kien(DU_AN_TRAM, "may.ghep", {"may_id": may_id}, luc=luc)
    return may_id, token


def doi_ma_ghep(kho: KhoPhieu, ma: str, *, luc: datetime) -> tuple[str, str]:
    """(may_id, token máy). Token chỉ trả MỘT lần — người gọi không log, không in."""
    kho.db.executescript(LUOC_DO_GHEP)
    with kho.giao_dich() as db:
        kq = _doi(kho, db, ma, luc)
    if kq == "khoa":
        raise GhepBiKhoa(f"Sai mã quá {SAI_TOI_DA} lần — chờ {PHUT_KHOA} phút rồi xin mã mới")
    if isinstance(kq, str):
        raise MaGhepSai("Mã ghép sai, đã dùng hoặc hết hạn")
    return kq
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_ma_ghep.py -q`
Expected: `4 passed`

Run: `uv run pytest -q`
Expected: `N₀+4 passed` (trên `main` đợt 0 + riêng task này)

- [ ] **Step 5: Commit**

```bash
git add tram/phieu/ma_ghep.py tests/test_ma_ghep.py
git commit -m "feat(phieu): mã ghép Mac thợ dùng một lần, 10 phút, khoá khi dò; đổi lấy token máy (spec 3 §9.2)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 2: Hạn mức Codex — chuẩn hoá `account/rateLimits/read` và rollout, phát hiện hết hạn mức (chờ S5)

**Độ khó:** `de` · **Đợt:** 1 · **Song song với:** Task 1, 3, 4, 5, 6 · **Phải xong trước:** —

**Files:**
- Create: `tram/chay_cli/codex/__init__.py` (rỗng)
- Create: `tram/chay_cli/codex/han_muc.py`
- Test: `tests/du_lieu/codex/app_server_rate_limits.json` (mới — fixture, chờ S5)
- Test: `tests/du_lieu/codex/rollout.jsonl` (mới — fixture, chờ S5)
- Test: `tests/test_codex_han_muc.py` (mới)

**Interfaces:**
- Consumes: `CuaSo`, `HanMuc`, `ten_cua_so`, `lam_moi` (`tram/han_muc/mo_hinh.py`); `duoc_nhan`; Protocol `NguonHanMuc`.
- Produces: `tram/chay_cli/codex/han_muc.py`: `MAU_HET`, `MAU_CHUA_DANG_NHAP` (regex), `han_muc_app_server(ket_qua, *, khe_id, bay_gio) -> HanMuc | None` (`nguon="app-server"`), `han_muc_rollout(dong, *, khe_id, bay_gio) -> HanMuc | None` (`nguon="log"`), `thong_diep_loi(dong) -> str | None` (≤ 300 ký tự), `NguonHanMucCodex` (`.doc_dong(dong, *, khe_id, bay_gio)`, `.het_han_muc(dong)`). Fixture: khoá `plus`, `prolite`, `la` trong `app_server_rate_limits.json` (Task 7, 14 dùng `plus`/`prolite`).

- [ ] **Step 1: Viết test thất bại**

```bash
mkdir -p tests/du_lieu/codex
```

`tests/du_lieu/codex/app_server_rate_limits.json` (mới):

```json
{"_ghi_chu": "CHỈ DÙNG TRONG TEST — dựng theo tài liệu app-server và spike hạn mức 12/10 (usedPercent, windowDurationMins, resetsAt); CHƯA xác minh bằng chạy thật, chờ spike S5",
 "plus": {"rateLimits": {"primary": {"usedPercent": 62, "windowDurationMins": 300, "resetsAt": 1791867600},
                         "secondary": {"usedPercent": 12.5, "windowDurationMins": 10080, "resetsAt": 1792281600}}},
 "prolite": {"rateLimits": {"primary": {"usedPercent": 91, "windowDurationMins": 10080, "resetsAt": "2026-10-18T00:00:00Z"},
                            "secondary": null}},
 "la": {"rateLimits": {"primary": {"usedPercent": 40, "windowDurationMins": 60, "resetsAt": 1791867600},
                       "x": {"usedPercent": "nhieu", "windowDurationMins": 300},
                       "y": {"usedPercent": 150, "windowDurationMins": 300},
                       "z": {"usedPercent": 5, "windowDurationMins": 0}}}}
```

`tests/du_lieu/codex/rollout.jsonl` (mới):

```text
{"_ghi_chu": "CHỈ DÙNG TRONG TEST — dòng token_count của rollout-*.jsonl theo spike hạn mức 12/10 (used_percent, window_minutes, resets_at); chờ spike S5"}
{"timestamp": "2026-10-13T02:40:00.000Z", "type": "session_meta", "payload": {"cwd": "/tmp/x"}}
{"timestamp": "2026-10-13T02:41:10.512Z", "type": "event_msg", "payload": {"type": "token_count", "info": null, "rate_limits": {"primary": {"used_percent": 62.0, "window_minutes": 300, "resets_at": 1791867600}, "secondary": {"used_percent": 12.5, "window_minutes": 10080, "resets_at": 1792281600}}}}
{"timestamp": "khong-phai-gio", "type": "event_msg", "payload": {"type": "token_count", "rate_limits": {"primary": {"used_percent": 5, "window_minutes": 10080, "resets_at": 1792281600}, "secondary": null}}}
```

`tests/test_codex_han_muc.py` (mới):

```python
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from tram.chay_cli.codex.han_muc import (NguonHanMucCodex, han_muc_app_server, han_muc_rollout,
                                         thong_diep_loi)
from tram.han_muc.luat import duoc_nhan
from tram.han_muc.mo_hinh import lam_moi
from tram.han_muc.nguon import NguonHanMuc

DL = Path(__file__).parent / "du_lieu" / "codex"
KHE = "C/codex-1"
LUC = datetime(2026, 10, 13, 3, 0, tzinfo=timezone.utc)
MAU = json.loads((DL / "app_server_rate_limits.json").read_text(encoding="utf-8"))


def _cs(hm):
    return {c.loai: (c.phan_tram, c.reset_luc) for c in hm.cua_so}


def test_app_server_theo_thoi_luong_khong_theo_primary():
    hm = han_muc_app_server(MAU["plus"], khe_id=KHE, bay_gio=LUC)
    assert hm.nguon == "app-server" and all(c.doc_luc == "2026-10-13T03:00:00Z" for c in hm.cua_so)
    assert _cs(hm) == {"5h": (62.0, "2026-10-13T05:00:00Z"), "tuan": (12.5, "2026-10-18T00:00:00Z")}
    pro = han_muc_app_server(MAU["prolite"], khe_id=KHE, bay_gio=LUC)
    assert _cs(pro) == {"tuan": (91.0, "2026-10-18T00:00:00Z")}                  # primary là cửa sổ tuần
    assert not duoc_nhan(lam_moi(pro, KHE, LUC), 0)
    assert [c.trang_thai for c in lam_moi(pro, KHE, LUC).cua_so] == ["biet", "chua_biet"]   # thiếu 5h → chưa biết


def test_cua_so_la_giu_ten_goc_truong_sai_bi_bo_khong_gia_0():
    hm = han_muc_app_server(MAU["la"], khe_id=KHE, bay_gio=LUC)
    assert _cs(hm) == {"primary:60m": (40.0, "2026-10-13T05:00:00Z")}
    for sai in ({}, {"rateLimits": None}, {"rateLimits": {"primary": None}}, {"rateLimits": []}):
        assert han_muc_app_server(sai, khe_id=KHE, bay_gio=LUC) is None


def test_rollout_dung_truong_snake_case_va_gio_cua_dong():
    dong = [json.loads(x) for x in (DL / "rollout.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [han_muc_rollout(d, khe_id=KHE, bay_gio=LUC) for d in dong[:2]] == [None, None]
    hm = han_muc_rollout(dong[2], khe_id=KHE, bay_gio=LUC)
    assert hm.nguon == "log" and _cs(hm)["5h"] == (62.0, "2026-10-13T05:00:00Z")
    assert hm.cua_so[0].doc_luc == "2026-10-13T02:41:10Z"
    assert han_muc_rollout(dong[3], khe_id=KHE, bay_gio=LUC).cua_so[0].doc_luc == "2026-10-13T03:00:00Z"


@pytest.mark.parametrize("dong, het", [
    ({"type": "error", "message": "You've hit your usage limit. Try again in 2 hours."}, True),
    ({"type": "turn.failed", "error": {"message": "unexpected status 429 Too Many Requests"}}, True),
    ({"type": "turn.failed", "error": {"message": "stream disconnected"}}, False),
    ({"type": "item.completed", "item": {"type": "agent_message", "text": "usage limit của API là gì?"}}, False),
    ({"type": "error"}, False),
])
def test_het_han_muc_chi_tu_thong_diep_loi(dong, het):
    assert NguonHanMucCodex().het_han_muc(dong) is het


def test_nguon_dung_giao_dien_va_thong_diep_loi():
    n = NguonHanMucCodex()
    assert isinstance(n, NguonHanMuc)
    assert n.doc_dong({"type": "turn.completed", "usage": {}}, khe_id=KHE, bay_gio=LUC) is None
    assert thong_diep_loi({"type": "turn.failed", "error": "x"}) is None
    assert thong_diep_loi({"type": "error", "message": "a" * 500}) == "a" * 300
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_codex_han_muc.py -q`
Expected: FAIL — `1 error` (`ModuleNotFoundError: No module named 'tram.chay_cli.codex'`)

- [ ] **Step 3: Viết mã**

```bash
mkdir -p tram/chay_cli/codex && touch tram/chay_cli/codex/__init__.py
```

`tram/chay_cli/codex/han_muc.py` (mới):

```python
"""Bộ đọc hạn mức Codex (spec 3 §8.1, lát 3b) — HÌNH DẠNG CHƯA XÁC MINH, chờ spike S5.

Nguồn chính: `codex app-server` → `account/rateLimits/read`, kết quả `{"rateLimits": {"<tên>": {usedPercent,
windowDurationMins, resetsAt}}}` (spike hạn mức 12/10). Nguồn lùi: dòng `token_count` của
`$CODEX_HOME/sessions/**/rollout-*.jsonl`, `rate_limits.<tên>.{used_percent, window_minutes, resets_at}`.
Tên cửa sổ theo THỜI LƯỢNG (`ten_cua_so`: 300 → 5h, 10080 → tuan), không theo primary/secondary. `resets_at` nhận giây
epoch hoặc chuỗi ISO. Trường thiếu/sai → bỏ cửa sổ đó (thành chưa biết ở `lam_moi`), KHÔNG giả 0%.
`codex exec --json` không mang hạn mức (theo hiểu biết hiện tại) — chỉ dùng thông điệp lỗi để phát hiện hết hạn mức."""
import re
from datetime import datetime, timezone

from tram.han_muc.mo_hinh import CuaSo, HanMuc, ten_cua_so

MAU_HET = re.compile(r"usage limit|rate limit|too many requests|\b429\b|quota", re.I)
MAU_CHUA_DANG_NHAP = re.compile(r"not logged in|log ?in again|unauthorized|\b401\b", re.I)


def _chuoi(d: datetime) -> str:
    return d.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _gio(x) -> str | None:
    try:
        if isinstance(x, (int, float)) and not isinstance(x, bool):
            return _chuoi(datetime.fromtimestamp(x / 1000 if x > 1e12 else x, timezone.utc))
        if isinstance(x, str):
            d = datetime.fromisoformat(x.replace("Z", "+00:00"))
            return _chuoi(d if d.tzinfo else d.replace(tzinfo=timezone.utc))
    except (ValueError, OverflowError, OSError):
        pass
    return None


def _so(x) -> float | None:
    return float(x) if isinstance(x, (int, float)) and not isinstance(x, bool) else None


def _cac_cua_so(bang, k_pt: str, k_phut: str, k_reset: str, doc_luc: str) -> list[CuaSo]:
    ra: dict[str, CuaSo] = {}
    for ten, d in (bang.items() if isinstance(bang, dict) else []):
        if not isinstance(d, dict):
            continue
        pt, phut = _so(d.get(k_pt)), _so(d.get(k_phut))
        if pt is None or not 0 <= pt <= 100 or phut is None or phut < 1 or phut != int(phut):
            continue
        loai = ten_cua_so(int(phut), str(ten)[:32])
        ra.setdefault(loai, CuaSo(loai=loai, trang_thai="biet", phan_tram=pt, reset_luc=_gio(d.get(k_reset)),
                                  doc_luc=doc_luc))
    return list(ra.values())


def han_muc_app_server(ket_qua: dict, *, khe_id: str, bay_gio: datetime) -> HanMuc | None:
    cs = _cac_cua_so(ket_qua.get("rateLimits"), "usedPercent", "windowDurationMins", "resetsAt", _chuoi(bay_gio))
    return HanMuc(khe_id=khe_id, cua_so=cs, nguon="app-server") if cs else None


def han_muc_rollout(dong: dict, *, khe_id: str, bay_gio: datetime) -> HanMuc | None:
    p = dong.get("payload")
    if not isinstance(p, dict) or p.get("type") != "token_count":
        return None
    luc = _gio(dong.get("timestamp")) or _chuoi(bay_gio)
    cs = _cac_cua_so(p.get("rate_limits"), "used_percent", "window_minutes", "resets_at", luc)
    return HanMuc(khe_id=khe_id, cua_so=cs, nguon="log") if cs else None


def thong_diep_loi(dong: dict) -> str | None:
    """Thông điệp của sự kiện lỗi `codex exec --json` (`error`, `turn.failed`), cắt 300 ký tự; không phải lỗi → None."""
    if dong.get("type") == "error":
        m = dong.get("message")
    elif dong.get("type") == "turn.failed" and isinstance(dong.get("error"), dict):
        m = dong["error"].get("message")
    else:
        return None
    return m[:300] if isinstance(m, str) and m else None


class NguonHanMucCodex:
    """`NguonHanMuc` cho khe Codex: đọc dòng rollout (nguồn lùi); dòng exec chỉ dùng để phát hiện hết hạn mức."""

    def doc_dong(self, dong: dict, *, khe_id: str, bay_gio: datetime) -> HanMuc | None:
        return han_muc_rollout(dong, khe_id=khe_id, bay_gio=bay_gio)

    def het_han_muc(self, dong: dict) -> bool:
        m = thong_diep_loi(dong)
        return bool(m and MAU_HET.search(m))
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_codex_han_muc.py -q`
Expected: `9 passed`

Run: `uv run pytest -q`
Expected: `N₀+9 passed` (trên `main` đợt 0 + riêng task này)

- [ ] **Step 5: Commit**

```bash
git add tram/chay_cli/codex/__init__.py tram/chay_cli/codex/han_muc.py tests/du_lieu/codex/app_server_rate_limits.json tests/du_lieu/codex/rollout.jsonl tests/test_codex_han_muc.py
git commit -m "feat(codex): chuẩn hoá hạn mức Codex theo thời lượng cửa sổ, phát hiện hết hạn mức — chờ spike S5 (spec 3 §8.1)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 3: Cho phép khe `codex` ở `tho.yaml` và `/api/tho/dang-ky`

**Độ khó:** `de` · **Đợt:** 1 · **Song song với:** Task 1, 2, 4, 5, 6 · **Phải xong trước:** —

**Files:**
- Modify: `tram/tho/cau_hinh.py` (thêm `CLI`, đổi kiểm `cli`)
- Modify: `tram/api/tho.py` (`KheDangKy.cli`)
- Modify: `tests/test_cau_hinh_tho.py`, `tests/test_api_tho.py` (ca "cli lạ" đổi `codex` → `gemini`; số test giữ nguyên)
- Test: `tests/test_khe_codex.py` (mới)

**Interfaces:**
- Consumes: `nap_cau_hinh_tho`; `tao_tram(..., dang_ky=False)` (`tests/tho_api_gia.py` — có sẵn token máy B, C); `cac_khe`.
- Produces: `tram/tho/cau_hinh.py`: `CLI = ("claude", "codex")` (Task 10 dùng). `/api/tho/dang-ky` nhận `cli: "codex"`; mọi `cli` khác `claude`/`codex` → 422 (G19).

- [ ] **Step 1: Viết test thất bại**

`tests/test_khe_codex.py` (mới):

```python
from contextlib import closing

import pytest

from tho_api_gia import tao_tram
from tram.phieu.khe import cac_khe
from tram.tho.cau_hinh import nap_cau_hinh_tho

YAML = """may_id: C
tram_api: https://may-b.tail1234.ts.net
khe:
  - ten: codex-1
    cli: codex
    thu_muc_cau_hinh: /Users/tho/khe/codex-1
    ten_goi_nho: "Codex tài khoản 1"
    vai_uu_tien: [coder, qc]
"""
CODEX = {"ten": "codex-1", "cli": "codex", "ten_goi_nho": "Codex tài khoản 1", "vai_uu_tien": ["coder", "qc"]}


def test_tho_yaml_nhan_khe_codex_tu_xa(tmp_path):
    (tmp_path / "tho.yaml").write_text(YAML, encoding="utf-8")
    ch = nap_cau_hinh_tho(tmp_path / "tho.yaml")
    assert ch.tram_api == "https://may-b.tail1234.ts.net" and ch.khe_id(ch.khe[0]) == "C/codex-1"
    assert ch.khe[0].cli == "codex" and ch.khe[0].vai_uu_tien == ("coder", "qc")
    (tmp_path / "tho.yaml").write_text(YAML.replace("cli: codex", "cli: gemini"), encoding="utf-8")
    with pytest.raises(ValueError, match="gemini"):
        nap_cau_hinh_tho(tmp_path / "tho.yaml")


def test_api_dang_ky_khe_codex_cua_may_c(tmp_path):
    t = tao_tram(tmp_path, dang_ky=False)
    r = t.goi("POST", "/api/tho/dang-ky", "C", json_body={"may_id": "C", "khe": [CODEX]})
    assert r.status == 200 and r.json() == {"khe_id": ["C/codex-1"]}
    with closing(t.kho()) as kho:
        assert cac_khe(kho)["C/codex-1"]["cli"] == "codex"
    sai = {**CODEX, "cli": "gemini"}
    assert t.goi("POST", "/api/tho/dang-ky", "C", json_body={"may_id": "C", "khe": [sai]}).status == 422
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_khe_codex.py -q`
Expected: FAIL — `2 failed` (`ValueError: khe codex-1: lát 3a chỉ có cli claude (khe Codex thuộc lát 3b)`; `assert (422 == 200)` — `Input should be 'claude'`)

- [ ] **Step 3: Viết mã** — bản vá bốn file (nền: 3a-1 Task 9, 23 trên `main`):

```diff
diff --git a/tests/test_api_tho.py b/tests/test_api_tho.py
index d769769..179b980 100644
--- a/tests/test_api_tho.py
+++ b/tests/test_api_tho.py
@@ -34,7 +34,7 @@ def test_dang_ky_va_khe_cua_may_khac_403(tmp_path):
         {"ten": "x", "cli": "claude", "ten_goi_nho": "x", "vai_uu_tien": ["qc"]}]}).status == 403
     assert t.goi("POST", "/api/tho/nhip", "C", json_body=NHIP).status == 403
     assert t.goi("POST", "/api/tho/nhip", json_body={**NHIP, "khe_id": "B/claude-9"}).status == 403
-    for khe in ({"ten": "x", "cli": "codex", "ten_goi_nho": "x", "vai_uu_tien": ["qc"]},
+    for khe in ({"ten": "x", "cli": "gemini", "ten_goi_nho": "x", "vai_uu_tien": ["qc"]},
                 {"ten": "x", "cli": "claude", "ten_goi_nho": "a@b.c", "vai_uu_tien": ["qc"]}):
         assert t.goi("POST", "/api/tho/dang-ky", json_body={"may_id": "B", "khe": [khe]}).status == 422
 
diff --git a/tests/test_cau_hinh_tho.py b/tests/test_cau_hinh_tho.py
index 426ab9e..5994c59 100644
--- a/tests/test_cau_hinh_tho.py
+++ b/tests/test_cau_hinh_tho.py
@@ -43,7 +43,7 @@ def test_mac_dinh_doc_tu_tram_home(tram_home_tam):
 
 @pytest.mark.parametrize("cu, moi", [
     ("may_id: B", "may_id: 'B/x'"), ("tram_api: http://127.0.0.1:7700", "tram_api: http://10.0.0.2:7700"),
-    ("cli: claude\n    principal", "cli: codex\n    principal"), ("ten: claude-1", "ten: Claude_1"),
+    ("cli: claude\n    principal", "cli: gemini\n    principal"), ("ten: claude-1", "ten: Claude_1"),
     ("ten: claude-2", "ten: claude-1"), ("[coder]", "[admin]"), ("[coder]", "[]"),
     ('"Claude tài khoản 1"', '"hung@example.com"'), ("/Users/tho/khe/claude-1", "khe/claude-1"),
     ("    vai_uu_tien: [coder]", "    vai_uu_tien: [coder]\n    token: x"), ("may_id: B", "may_id: B\nla: 1"),
diff --git a/tram/api/tho.py b/tram/api/tho.py
index b40f6da..edebc43 100644
--- a/tram/api/tho.py
+++ b/tram/api/tho.py
@@ -39,7 +39,7 @@ router = APIRouter(prefix="/api/tho", dependencies=[Depends(may_cua_yeu_cau)])
 class KheDangKy(BaseModel):
     model_config = ConfigDict(extra="forbid")
     ten: str = Field(pattern=r"^[a-z0-9-]{1,32}$")
-    cli: Literal["claude"]                                  # khe Codex: lát 3b
+    cli: Literal["claude", "codex"]                         # Gemini: ngoài phạm vi (spec 3 §16)
     ten_goi_nho: str = Field(min_length=1, max_length=64, pattern=r"^[^@]*$")
     vai_uu_tien: list[Literal["spec", "coder", "qc"]] = Field(min_length=1, max_length=3)
 
diff --git a/tram/tho/cau_hinh.py b/tram/tho/cau_hinh.py
index f0c64f8..1724d55 100644
--- a/tram/tho/cau_hinh.py
+++ b/tram/tho/cau_hinh.py
@@ -13,6 +14,7 @@ MAY_RE = re.compile(r"[A-Za-z0-9-]{1,32}")
 TEN_KHE_RE = re.compile(r"[a-z0-9-]{1,32}")
 API_RE = re.compile(r"(http://(127\.0\.0\.1|localhost):\d{2,5}|https://[A-Za-z0-9.-]+(:\d{2,5})?)/?")
 VAI = ("spec", "coder", "qc")
+CLI = ("claude", "codex")
 KHOA_KHE = {"ten", "cli", "principal", "thu_muc_cau_hinh", "ten_goi_nho", "vai_uu_tien"}
 
 
@@ -42,8 +44,8 @@ def _khe(raw: object) -> KheCauHinh:
     ten, cli = str(raw.get("ten", "")), raw.get("cli")
     if not TEN_KHE_RE.fullmatch(ten):
         raise ValueError(f"tên khe {ten!r} chỉ gồm chữ thường, số, '-'")
-    if cli != "claude":
-        raise ValueError(f"khe {ten}: lát 3a chỉ có cli claude (khe Codex thuộc lát 3b)")
+    if cli not in CLI:
+        raise ValueError(f"khe {ten}: cli {cli!r} không hỗ trợ — chỉ {CLI}")
     thu_muc = Path(str(raw.get("thu_muc_cau_hinh") or "")).expanduser()
     if not thu_muc.is_absolute():
         raise ValueError(f"khe {ten}: thu_muc_cau_hinh phải là đường dẫn tuyệt đối")
diff --git a/tram/tho/cau_hinh_chay.py b/tram/tho/cau_hinh_chay.py
--- a/tram/tho/cau_hinh_chay.py
+++ b/tram/tho/cau_hinh_chay.py
@@ -7,7 +7,7 @@
 from pathlib import Path
 
 PATH_HE_THONG = "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
-NHO_RE = re.compile(r"http://(127\.0\.0\.1|localhost):\d{2,5}/mcp")
+NHO_RE = re.compile(r"(?:http://(127\.0\.0\.1|localhost):\d{2,5}/mcp|https://[A-Za-z0-9.-]+(?::\d{2,5})?/nho/mcp)")
 SO = {"han_chot_dung_mem_phut": (3, 1, 30), "lan_chay_moi_gio": (6, 1, 60), "lan_chay_moi_ngay": (60, 1, 1440),
       "thoi_gian_cho_kiem_giay": (900, 10, 7200)}
 
@@ -42,7 +42,7 @@
     if raw.get("day") not in (None, "ref-tam", "kho-tho"):
         raise ValueError("chay.day là ref-tam hoặc kho-tho (phải khớp cong_bo.phuong_an của trạm)")
     if raw.get("nho_url") is not None and not NHO_RE.fullmatch(str(raw["nho_url"])):
-        raise ValueError("chay.nho_url phải dạng http://127.0.0.1:<cổng>/mcp")
+        raise ValueError("chay.nho_url phải là loopback /mcp hoặc HTTPS trạm từ xa /nho/mcp")
     if raw.get("thang_utilization") not in (None, "ti_le", "phan_tram"):
         raise ValueError("chay.thang_utilization là ti_le hoặc phan_tram (chốt ở S1)")
     so = {}

```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_khe_codex.py tests/test_api_tho.py tests/test_cau_hinh_tho.py -q`
Expected: `22 passed` nếu `test_api_tho.py` vẫn 6 test như 3a-1 (3a-2 thêm test vào file này thì cộng thêm đúng số đó)

Run: `uv run pytest -q`
Expected: `N₀+2 passed` (trên `main` đợt 0 + riêng task này)

- [ ] **Step 5: Commit**

```bash
git add tram/tho/cau_hinh.py tram/tho/cau_hinh_chay.py tram/api/tho.py tests/test_cau_hinh_tho.py tests/test_api_tho.py tests/test_khe_codex.py
git commit -m "feat(tho): khe cli codex ở tho.yaml và /api/tho/dang-ky (spec 3 §3 lát 3b); Gemini ngoài phạm vi" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 4: Dò máy thợ — CLI, đăng nhập qua lệnh trạng thái, tag Tailscale (chỉ đọc)

**Độ khó:** `de` · **Đợt:** 1 · **Song song với:** Task 1, 2, 3, 5, 6 · **Phải xong trước:** —

**Files:**
- Create: `tram/tho/do_may.py`
- Test: `tests/test_do_may.py` (mới)

**Interfaces:**
- Consumes: — (stdlib; `which`, `chay` tiêm được).
- Produces: `tram/tho/do_may.py`: `TAG_THO = "tag:tram-tho"`, `DUONG_TAILSCALE_APP`, `BIEN_THU_MUC = {"claude": "CLAUDE_CONFIG_DIR", "codex": "CODEX_HOME"}`, `LENH_DANG_NHAP`, `KetQuaDo(cli, duong_dan, phien_ban, dang_nhap: bool | None, chi_tiet)`, `do_cli(cli, thu_muc, *, which, chay) -> KetQuaDo`, `kiem_tag(*, which, chay, tag=TAG_THO) -> tuple[bool, str]`.

- [ ] **Step 1: Viết test thất bại**

`tests/test_do_may.py` (mới):

```python
import json
import subprocess

from tram.tho.do_may import DUONG_TAILSCALE_APP, TAG_THO, do_cli, kiem_tag


def _chay(bang: dict, goi: list):
    def chay(argv, **kw):
        goi.append((argv, kw.get("env", {}).get("CODEX_HOME")))
        ma, ra = bang[tuple(argv[1:])]
        return subprocess.CompletedProcess(argv, ma, ra, "")
    return chay


def test_codex_dang_nhap_qua_lenh_trang_thai_voi_codex_home_cua_khe(tmp_path):
    goi = []
    chay = _chay({("--version",): (0, "codex-cli 0.170.0\n"), ("login", "status"): (0, "Logged in using ChatGPT\n")},
                 goi)
    kq = do_cli("codex", tmp_path / "khe", which=lambda c: f"/opt/bin/{c}", chay=chay)
    assert (kq.duong_dan, kq.phien_ban, kq.dang_nhap) == ("/opt/bin/codex", "codex-cli 0.170.0", True)
    assert goi[1] == (["/opt/bin/codex", "login", "status"], str(tmp_path / "khe"))
    assert "@" not in kq.chi_tiet and "ChatGPT" not in kq.chi_tiet          # không chép đầu ra (có thể có email)
    chay = _chay({("--version",): (0, "x\n"), ("login", "status"): (1, "Not logged in\n")}, [])
    assert do_cli("codex", tmp_path, which=lambda c: c, chay=chay).dang_nhap is False


def test_claude_chua_kiem_dang_nhap_va_cli_thieu(tmp_path):
    goi = []
    kq = do_cli("claude", tmp_path, which=lambda c: "/b/claude", chay=_chay({("--version",): (0, "2.1.227\n")}, goi))
    assert kq.dang_nhap is None and "S2" in kq.chi_tiet and len(goi) == 1
    kq = do_cli("codex", tmp_path, which=lambda c: None, chay=None)
    assert kq.duong_dan is None and kq.dang_nhap is None and "PATH" in kq.chi_tiet


def _ts(du_lieu, goi=None, ma=0):
    def chay(argv, **kw):
        (goi if goi is not None else []).append(argv)
        return subprocess.CompletedProcess(argv, ma, json.dumps(du_lieu) if isinstance(du_lieu, dict) else du_lieu, "")
    return chay


def test_tag_tailscale_chi_doc_khong_doi():
    goi = []
    ok, ct = kiem_tag(which=lambda c: "/usr/local/bin/tailscale" if c == "tailscale" else None,
                      chay=_ts({"Self": {"Tags": ["tag:khac", TAG_THO], "HostName": "mac-c"}}, goi))
    assert ok and TAG_THO in ct and goi == [["/usr/local/bin/tailscale", "status", "--json"]]
    ok, ct = kiem_tag(which=lambda c: None, chay=None)
    assert not ok and "Tailscale" in ct
    app = {DUONG_TAILSCALE_APP: DUONG_TAILSCALE_APP}
    ok, ct = kiem_tag(which=app.get, chay=_ts({"Self": {"UserID": 1}}))
    assert not ok and "chưa gắn" in ct and "không tự đổi" in ct
    for hong in ("không phải json", {"Self": None}, {"Self": {"Tags": "tag:tram-tho"}}):
        assert kiem_tag(which=app.get, chay=_ts(hong))[0] is False
    assert kiem_tag(which=app.get, chay=_ts({"Self": {"Tags": [TAG_THO]}}, ma=1))[0] is False
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_do_may.py -q`
Expected: FAIL — `1 error` (`ModuleNotFoundError: No module named 'tram.tho.do_may'`)

- [ ] **Step 3: Viết mã**

`tram/tho/do_may.py` (mới):

```python
"""Dò máy thợ — CHỈ ĐỌC, không đổi gì (spec 3 §9.2, §9.3; kiến trúc §7 "Mac thợ").

- CLI: đường dẫn + `--version`; đăng nhập qua LỆNH TRẠNG THÁI của CLI, dưới thư mục cấu hình của khe — không bao giờ mở
  file đăng nhập. Codex: `codex login status` (mã 0 = đã đăng nhập — chờ spike S5 xác nhận). Claude: lệnh trạng thái
  chốt ở spike S2 (3a-2) — ở đây báo "chưa kiểm". Không chép đầu ra lệnh trạng thái (có thể chứa email tài khoản).
- Tailscale: Mac thợ phải là thiết bị GẮN TAG (#3) — đọc `tailscale status --json` → `Self.Tags`. Trạm không tự gắn tag,
  không chạy `tailscale up`; chưa gắn thì Đại ca làm trong trang quản trị Tailscale."""
import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

TAG_THO = "tag:tram-tho"
DUONG_TAILSCALE_APP = "/Applications/Tailscale.app/Contents/MacOS/Tailscale"
BIEN_THU_MUC = {"claude": "CLAUDE_CONFIG_DIR", "codex": "CODEX_HOME"}
LENH_DANG_NHAP = {"codex": ["login", "status"]}          # claude: chờ S2 (3a-2)


@dataclass(frozen=True)
class KetQuaDo:
    cli: str
    duong_dan: str | None
    phien_ban: str
    dang_nhap: bool | None          # None = chưa kiểm được
    chi_tiet: str


def do_cli(cli: str, thu_muc: Path, *, which=shutil.which, chay=subprocess.run) -> KetQuaDo:
    duong = which(cli)
    if duong is None:
        return KetQuaDo(cli, None, "", None, f"không thấy `{cli}` trong PATH")
    v = chay([duong, "--version"], capture_output=True, text=True, timeout=20)
    phien = ((v.stdout or v.stderr or "").strip().splitlines() or [""])[0][:80]
    if cli not in LENH_DANG_NHAP:
        return KetQuaDo(cli, duong, phien, None, "đăng nhập chưa kiểm được — chờ spike S2 (không đọc file đăng nhập)")
    env = {**os.environ, BIEN_THU_MUC[cli]: str(thu_muc)}
    s = chay([duong, *LENH_DANG_NHAP[cli]], capture_output=True, text=True, timeout=20, env=env)
    lenh = " ".join([cli, *LENH_DANG_NHAP[cli]])
    if s.returncode == 0:
        return KetQuaDo(cli, duong, phien, True, f"đã đăng nhập (`{lenh}` mã 0)")
    return KetQuaDo(cli, duong, phien, False, f"chưa đăng nhập (`{lenh}` mã {s.returncode}) — Đại ca đăng nhập tay: "
                    f"{BIEN_THU_MUC[cli]}={thu_muc} {cli} login")


def kiem_tag(*, which=shutil.which, chay=subprocess.run, tag: str = TAG_THO) -> tuple[bool, str]:
    duong = which("tailscale") or which(DUONG_TAILSCALE_APP)
    if duong is None:
        return False, "không thấy Tailscale — Đại ca cài, rồi đưa máy vào tailnet như thiết bị gắn tag"
    kq = chay([duong, "status", "--json"], capture_output=True, text=True, timeout=20)
    try:
        tu = json.loads(kq.stdout) if kq.returncode == 0 else {}
        tags = ((tu.get("Self") or {}).get("Tags") or []) if isinstance(tu, dict) else []
    except (ValueError, AttributeError):
        tags = []
    if isinstance(tags, list) and tag in tags:
        return True, f"máy gắn {tag}"
    return False, (f"máy chưa gắn {tag} (hoặc không đọc được `tailscale status`) — Đại ca gắn tag trong trang quản "
                   "trị Tailscale (máy không đăng nhập bằng tài khoản Đại ca); trạm không tự đổi cài đặt")
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_do_may.py -q`
Expected: `3 passed`

Run: `uv run pytest -q`
Expected: `N₀+3 passed` (trên `main` đợt 0 + riêng task này)

- [ ] **Step 5: Commit**

```bash
git add tram/tho/do_may.py tests/test_do_may.py
git commit -m "feat(tho): dò CLI, đăng nhập qua lệnh trạng thái, tag Tailscale của Mac thợ — chỉ đọc (spec 3 §9.2, §9.3)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 5: Cấu hình memory MCP cho khe — Claude qua lệnh CLI, Codex qua khối `config.toml`

**Độ khó:** `de` · **Đợt:** 1 · **Song song với:** Task 1, 2, 3, 4, 6 · **Phải xong trước:** —

**Files:**
- Create: `tram/tho/mcp_tho.py`
- Test: `tests/test_mcp_tho.py` (mới)

**Interfaces:**
- Consumes: `TEN_MAY_CHU`, `cau_hinh_tho()` (`tram/nho/cau_hinh_mcp.py`, 1b-2 Task 6).
- Produces: `tram/tho/mcp_tho.py`: `DAU`, `CUOI` (dấu mốc), `url_nho(tram_chu) -> str` (ValueError khi không phải `https://<tên>.<miền>`), `khoi_codex(url) -> str`, `ghep_codex_toml(cu, url) -> str` (ValueError khi TOML hỏng/dấu mốc hỏng/trùng tên ngoài khối), `lenh_claude_mcp(claude, thu_muc) -> list[tuple[list[str], dict[str, str]]]`.

- [ ] **Step 1: Viết test thất bại**

`tests/test_mcp_tho.py` (mới):

```python
import json
import tomllib
from pathlib import Path

import pytest

from tram.nho.cau_hinh_mcp import TEN_MAY_CHU, cau_hinh_tho
from tram.tho.mcp_tho import DAU, CUOI, ghep_codex_toml, lenh_claude_mcp, url_nho

URL = "https://may-b.tail1234.ts.net/nho/mcp"
CU = 'model = "gpt-5"\n\n[profiles.nhanh]\nmodel = "gpt-5-mini"\n'


def test_url_nho_chi_https_tailnet():
    assert url_nho("https://may-b.tail1234.ts.net/") == URL
    for sai in ("http://may-b.tail1234.ts.net", "https://may-b/x", 'https://a"b'):
        with pytest.raises(ValueError):
            url_nho(sai)


def test_codex_them_khoi_cuoi_file_giu_noi_dung_cu_header_tu_bien_moi_truong():
    moi = ghep_codex_toml(CU, URL)
    assert moi.startswith(CU) and moi.count(DAU) == moi.count(CUOI) == 1
    t = tomllib.loads(moi)
    assert t["profiles"]["nhanh"]["model"] == "gpt-5-mini"
    may_chu = t["mcp_servers"][TEN_MAY_CHU]
    assert may_chu["url"] == URL and "http_headers" not in may_chu
    assert {h: f"${{{b}}}" for h, b in may_chu["env_http_headers"].items()} == cau_hinh_tho()["headers"]
    assert ghep_codex_toml("", URL).startswith(DAU)


def test_codex_chay_lai_thay_khoi_cu_khong_nhan_doi():
    lan1 = ghep_codex_toml(CU, URL)
    lan2 = ghep_codex_toml(lan1 + "\n[khac]\nx = 1\n", URL.replace("may-b", "may-b2"))
    assert lan2.count(DAU) == 1 and "may-b2" in lan2 and "may-b.tail" not in lan2
    assert tomllib.loads(lan2)["khac"]["x"] == 1


@pytest.mark.parametrize("cu", ['[mcp_servers.tram-nho]\nurl = "http://khac"\n', "model = \n", f"{DAU}\nx = 1\n"])
def test_codex_tu_choi_cau_hinh_hong_hoac_trung_ten_ngoai_khoi(cu):
    with pytest.raises(ValueError):
        ghep_codex_toml(cu, URL)


def test_claude_qua_lenh_cua_cli_voi_thu_muc_cua_khe(tmp_path):
    (xoa, env1), (them, env2) = lenh_claude_mcp("/b/claude", tmp_path / "khe")
    assert xoa == ["/b/claude", "mcp", "remove", "--scope", "user", TEN_MAY_CHU]
    assert them[:6] == ["/b/claude", "mcp", "add-json", "--scope", "user", TEN_MAY_CHU]
    assert json.loads(them[6]) == cau_hinh_tho() and "${TRAM_MA_GIAO}" in them[6]
    assert env1 == env2 == {"CLAUDE_CONFIG_DIR": str(tmp_path / "khe")}
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_mcp_tho.py -q`
Expected: FAIL — `1 error` (`ModuleNotFoundError: No module named 'tram.tho.mcp_tho'`)

- [ ] **Step 3: Viết mã**

`tram/tho/mcp_tho.py` (mới):

```python
"""Cấu hình memory MCP (spec 1b §9.2) cho CLI của khe trên máy thợ — `tram tho dang-ky` (3b). Chỉ SINH nội dung/lệnh;
ghi thật ở bước thực hiện sau khi Đại ca gõ `dong-y`. Hình dạng cấu hình của CLI chưa kiểm bằng chạy thật
(spike N2, S5).

- Claude: qua lệnh của CLI (`claude mcp add-json --scope user`, `CLAUDE_CONFIG_DIR` của khe) với `cau_hinh_tho()` của
  1b-2 — trạm không mở file cấu hình/đăng nhập của Claude. Biến `${TRAM_NHO_URL}`… do vòng `tram tho chay` đặt (3a-2).
- Codex: khối có dấu mốc ở CUỐI `$CODEX_HOME/config.toml`: `url` ghi thẳng (Codex không mở rộng biến trong url — chờ
  S5), header lấy từ biến môi trường qua `env_http_headers`. Chạy lại thay khối cũ; trùng tên ngoài khối → từ chối."""
import json
import re
import tomllib
from pathlib import Path

from tram.nho.cau_hinh_mcp import TEN_MAY_CHU, cau_hinh_tho

DAU = f"# >>> {TEN_MAY_CHU} (tram tho dang-ky — đừng sửa tay) >>>"
CUOI = f"# <<< {TEN_MAY_CHU} <<<"
URL_RE = re.compile(r"https://[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)+(:\d{2,5})?")


def url_nho(tram_chu: str) -> str:
    """`tailscale serve` đưa đường `/nho` → memory 7710 (spec 1b §9; kiểm ở N2)."""
    goc = tram_chu.rstrip("/")
    if not URL_RE.fullmatch(goc):
        raise ValueError("tram chủ phải dạng https://<máy B>.<tailnet>.ts.net")
    return goc + "/nho/mcp"


def _bien_header() -> dict[str, str]:
    """{header: TÊN_BIẾN} từ `cau_hinh_tho()` (`${TÊN}`) — một nguồn với bên kiểm của memory 1b-2."""
    return {h: re.fullmatch(r"\$\{([A-Z_]+)\}", v).group(1) for h, v in cau_hinh_tho()["headers"].items()}


def khoi_codex(url: str) -> str:
    hdr = ", ".join(f'"{h}" = "{b}"' for h, b in _bien_header().items())
    return f'{DAU}\n[mcp_servers.{TEN_MAY_CHU}]\nurl = "{url}"\nenv_http_headers = {{ {hdr} }}\n{CUOI}\n'


def _bo_khoi(cu: str) -> str:
    if cu.count(DAU) != cu.count(CUOI) or cu.count(DAU) > 1:
        raise ValueError("config.toml có dấu mốc tram-nho hỏng — Đại ca sửa tay trước")
    if DAU not in cu:
        return cu
    dau, cuoi = cu.index(DAU), cu.index(CUOI) + len(CUOI)
    return cu[:dau] + cu[cuoi:].lstrip("\n")


def ghep_codex_toml(cu: str, url: str) -> str:
    goc = _bo_khoi(cu)
    try:
        if TEN_MAY_CHU in tomllib.loads(goc).get("mcp_servers", {}):
            raise ValueError(f"config.toml đã có mcp_servers.{TEN_MAY_CHU} ngoài khối của trạm — Đại ca gỡ tay trước")
    except tomllib.TOMLDecodeError as e:
        raise ValueError(f"config.toml hiện tại không đọc được: {e}") from None
    moi = (goc if not goc or goc.endswith("\n") else goc + "\n") + ("\n" if goc.strip() else "") + khoi_codex(url)
    tomllib.loads(moi)
    return moi


def lenh_claude_mcp(claude: str, thu_muc: Path) -> list[tuple[list[str], dict[str, str]]]:
    """(argv, biến môi trường thêm). Lệnh xoá được phép lỗi (chưa có); lệnh thêm phải thành công."""
    env = {"CLAUDE_CONFIG_DIR": str(thu_muc)}
    goc = [claude, "mcp"]
    return [([*goc, "remove", "--scope", "user", TEN_MAY_CHU], env),
            ([*goc, "add-json", "--scope", "user", TEN_MAY_CHU, json.dumps(cau_hinh_tho(), ensure_ascii=False)], env)]
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_mcp_tho.py -q`
Expected: `7 passed`

Run: `uv run pytest -q`
Expected: `N₀+7 passed` (trên `main` đợt 0 + riêng task này)

- [ ] **Step 5: Commit**

```bash
git add tram/tho/mcp_tho.py tests/test_mcp_tho.py
git commit -m "feat(tho): sinh cấu hình memory MCP cho khe Claude (lệnh CLI) và Codex (khối config.toml) — chờ N2, S5 (spec 1b §9.2)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 6: LaunchAgent `vn.tram.tho` và ghi token máy vào Keychain qua stdin

**Độ khó:** `de` · **Đợt:** 1 · **Song song với:** Task 1, 2, 3, 4, 5 · **Phải xong trước:** —

**Files:**
- Create: `tram/tho/launchd_tho.py`
- Create: `tram/tho/token_may.py`
- Test: `tests/test_launchd_token_tho.py` (mới)

**Interfaces:**
- Consumes: `PATH_HE_THONG` (`tram/chu/launchd.py`); `KEYCHAIN_THO`, `doc_token_may(*, chay)` (`tram/tho/khach.py`).
- Produces: `tram/tho/launchd_tho.py`: `NHAN_THO = "vn.tram.tho"` (G4), `tao_plist_tho(*, tram, log, home) -> bytes`, `lenh_nap_launchd(plist, *, uid) -> list[list[str]]`. `tram/tho/token_may.py`: `MAY_RE`, `TOKEN_RE`, `ghi_token_may(may_id, token, *, chay) -> None` (ValueError giá trị sai dạng — không gọi `security`; RuntimeError đọc lại không khớp).

- [ ] **Step 1: Viết test thất bại**

`tests/test_launchd_token_tho.py` (mới):

```python
import plistlib
import shlex
import subprocess
from pathlib import Path

import pytest

from tram.tho.khach import KEYCHAIN_THO
from tram.tho.launchd_tho import NHAN_THO, lenh_nap_launchd, tao_plist_tho
from tram.tho.token_may import ghi_token_may

TOKEN = "AbC_d-" + "x" * 40


class KeychainGia:
    def __init__(self, hong=False):
        self.kho, self.argv, self.hong = {}, [], hong

    def __call__(self, argv, **kw):
        self.argv.append(argv)
        if argv == ["security", "-i"]:
            t = shlex.split(kw["input"])
            if not self.hong:
                self.kho[t[t.index("-s") + 1]] = t[t.index("-w") + 1]
            return subprocess.CompletedProcess(argv, 0, "", "")
        gt = self.kho.get(argv[argv.index("-s") + 1])
        return subprocess.CompletedProcess(argv, 0 if gt else 44, (gt or "") + "\n", "")


def test_plist_chay_tram_tho_chay_khong_mang_bi_mat(tmp_path):
    p = plistlib.loads(tao_plist_tho(tram="/Users/tho/.local/bin/tram", log=tmp_path / "tho.log", home=tmp_path))
    assert p["Label"] == NHAN_THO == "vn.tram.tho"
    assert p["ProgramArguments"] == ["/Users/tho/.local/bin/tram", "tho", "chay"]
    assert p["RunAtLoad"] is True and p["KeepAlive"] == {"SuccessfulExit": False}
    assert p["StandardOutPath"] == p["StandardErrorPath"] == str(tmp_path / "tho.log")
    env = p["EnvironmentVariables"]
    assert set(env) == {"PATH"} and str(tmp_path / ".local/bin") in env["PATH"]
    with pytest.raises(ValueError):
        tao_plist_tho(tram="tram", log=tmp_path / "x.log", home=tmp_path)
    pl = tmp_path / f"{NHAN_THO}.plist"
    assert lenh_nap_launchd(pl, uid=501) == [["launchctl", "bootout", f"gui/501/{NHAN_THO}"],
                                             ["launchctl", "bootstrap", "gui/501", str(pl)]]


def test_ghi_token_qua_stdin_roi_doc_lai_khop():
    kc = KeychainGia()
    ghi_token_may("C", TOKEN, chay=kc)
    assert kc.kho == {KEYCHAIN_THO: TOKEN}
    assert all(TOKEN not in " ".join(a) for a in kc.argv)                     # không bao giờ nằm trong argv
    with pytest.raises(RuntimeError, match="Keychain"):
        ghi_token_may("C", TOKEN, chay=KeychainGia(hong=True))


@pytest.mark.parametrize("may_id, token", [("C", "ngan"), ("C", 'x" -A ' + "y" * 40), ("C/x", TOKEN), ("-U", TOKEN)])
def test_tu_choi_gia_tri_la_tu_tram_tra_ve(may_id, token):
    kc = KeychainGia()
    with pytest.raises(ValueError):
        ghi_token_may(may_id, token, chay=kc)
    assert kc.argv == []
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_launchd_token_tho.py -q`
Expected: FAIL — `1 error` (`ModuleNotFoundError: No module named 'tram.tho.launchd_tho'`)

- [ ] **Step 3: Viết mã**

`tram/tho/launchd_tho.py` (mới):

```python
"""LaunchAgent của tiến trình quản lý thợ trên Mac thợ từ xa (spec 3 §9.2; kiến trúc §7): `vn.tram.tho` chạy
`tram tho chay` (vòng của 3a-2) dưới tài khoản quản lý thợ. Mac thợ cài trạm bằng `uv tool install` nên chạy thẳng
file `tram` (đường dẫn tuyệt đối), không `uv run --project`. Chỉ SINH plist/lệnh — nạp thật sau `dong-y`."""
import plistlib
from pathlib import Path

from tram.chu.launchd import PATH_HE_THONG

NHAN_THO = "vn.tram.tho"


def tao_plist_tho(*, tram: str, log: Path, home: Path) -> bytes:
    if not Path(tram).is_absolute():
        raise ValueError("cần đường dẫn tuyệt đối tới `tram` (vd ~/.local/bin/tram của uv tool)")
    return plistlib.dumps({
        "Label": NHAN_THO,
        "ProgramArguments": [tram, "tho", "chay"],
        "WorkingDirectory": str(home),
        "StandardOutPath": str(log),
        "StandardErrorPath": str(log),
        "EnvironmentVariables": {"PATH": f"{home / '.local/bin'}:{PATH_HE_THONG}"},
        "RunAtLoad": True,
        "KeepAlive": {"SuccessfulExit": False},
    })


def lenh_nap_launchd(plist: Path, *, uid: int) -> list[list[str]]:
    """`bootout` được phép lỗi (chưa nạp lần nào); `bootstrap` phải thành công."""
    mien = f"gui/{uid}"
    return [["launchctl", "bootout", f"{mien}/{NHAN_THO}"], ["launchctl", "bootstrap", mien, str(plist)]]
```

`tram/tho/token_may.py` (mới):

```python
"""Ghi token máy vào Keychain `tram-tho-token` của TÀI KHOẢN QUẢN LÝ THỢ (spec 3 §5.1, §9.2) — bước của
`tram tho dang-ky` sau khi ghép. Token đi qua STDIN của `security -i` (không nằm trong argv — `ps` thấy được), không
in, không ghi file; ghi xong đọc lại và so hằng thời gian (`security -i` có thể trả 0 dù lệnh con lỗi).

Giá trị đến từ phản hồi của trạm → kiểm dạng trước khi ghép vào dòng lệnh của `security -i`. Chạy thật chờ S6 (Keychain
của tài khoản quản lý thợ khi không có phiên GUI)."""
import hmac
import re
import subprocess

from tram.tho.khach import KEYCHAIN_THO, doc_token_may

MAY_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9-]{0,31}")
TOKEN_RE = re.compile(r"[A-Za-z0-9_-]{32,128}")


def ghi_token_may(may_id: str, token: str, *, chay=subprocess.run) -> None:
    if not MAY_RE.fullmatch(may_id or "") or not TOKEN_RE.fullmatch(token or ""):
        raise ValueError("may_id hoặc token trạm trả về sai dạng — không ghi Keychain")
    chay(["security", "-i"], input=f'add-generic-password -U -s {KEYCHAIN_THO} -a {may_id} -w "{token}"\n',
         text=True, check=True, capture_output=True)
    doc = doc_token_may(chay=chay)
    if doc is None or not hmac.compare_digest(doc, token):
        raise RuntimeError(f"Không ghi được Keychain {KEYCHAIN_THO} — kiểm Keychain của tài khoản quản lý thợ")
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_launchd_token_tho.py -q`
Expected: `6 passed`

Run: `uv run pytest -q`
Expected: `N₀+6 passed` (trên `main` đợt 0 + riêng task này)

- [ ] **Step 5: Commit**

```bash
git add tram/tho/launchd_tho.py tram/tho/token_may.py tests/test_launchd_token_tho.py
git commit -m "feat(tho): plist vn.tram.tho cho Mac thợ; ghi token máy vào Keychain qua stdin rồi đọc lại (spec 3 §5.1, §9.2)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 7: Hỏi hạn mức qua `codex app-server` lúc khe rảnh (chờ S5)

**Độ khó:** `kho` · **Đợt:** 2 · **Song song với:** Task 8, 9, 10 · **Phải xong (đã ghép vào `main`) trước khi bắt đầu:** Task 2

**Files:**
- Create: `tram/chay_cli/codex/app_server.py`
- Test: `tests/du_lieu/codex/app_server_gia.py` (mới — script giả, CHỈ DÙNG TRONG TEST)
- Test: `tests/test_codex_app_server.py` (mới)

**Interfaces:**
- Consumes: `han_muc_app_server` (Task 2); fixture `app_server_rate_limits.json` (Task 2).
- Produces: `tram/chay_cli/codex/app_server.py`: `PHUONG_THUC = "account/rateLimits/read"`, `CHU_KY_RANH_GIAY = 300`, `LoiAppServer`, `hoi_app_server(argv, *, env, thoi_gian_cho=20.0, popen) -> dict` (kết quả của id 1), `doc_han_muc_ranh(khe_id, thu_muc_cau_hinh, *, bay_gio, codex="codex", hoi=hoi_app_server) -> HanMuc | None`.

- [ ] **Step 1: Viết test thất bại**

`tests/du_lieu/codex/app_server_gia.py` (mới):

```python
"""`codex app-server` GIẢ — CHỈ DÙNG TRONG TEST (chạy bằng sys.executable). Mỗi dòng stdin một JSON; ghi lại mọi
tin nhận được + CODEX_HOME vào file $GHI. CHE_DO: ok | loi | treo | dong.
Hình dạng tin theo hiểu biết hiện tại — chờ spike S5."""
import json
import os
import sys
import time
from pathlib import Path

MAU = json.loads((Path(__file__).parent / "app_server_rate_limits.json").read_text(encoding="utf-8"))
che_do, ghi = os.environ.get("CHE_DO", "ok"), Path(os.environ["GHI"])
nhan = [{"CODEX_HOME": os.environ.get("CODEX_HOME")}]


def tra(tin):
    print(json.dumps(tin), flush=True)


for dong in sys.stdin:
    tin = json.loads(dong)
    nhan.append(tin)
    ghi.write_text(json.dumps(nhan))
    if tin.get("method") == "initialize":
        if che_do == "dong":
            sys.exit(0)
        tra({"method": "thong-bao/khac", "params": {}})
        print("dòng rác không phải json", flush=True)
        tra({"id": 0, "result": {"userAgent": "gia/0"}})
        if che_do == "treo":
            time.sleep(60)
    elif tin.get("method") == "account/rateLimits/read":
        tra({"id": 1, "error": {"code": -32600, "message": "chưa đăng nhập"}} if che_do == "loi"
            else {"id": 1, "result": MAU["plus"]})
```

`tests/test_codex_app_server.py` (mới):

```python
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pytest

from tram.chay_cli.codex.app_server import LoiAppServer, doc_han_muc_ranh, hoi_app_server

GIA = Path(__file__).parent / "du_lieu" / "codex" / "app_server_gia.py"
LUC = datetime(2026, 10, 13, 3, 0, tzinfo=timezone.utc)


def _hoi(tmp_path, che_do, **kw):
    env = {"CHE_DO": che_do, "GHI": str(tmp_path / "nhan.json"), "CODEX_HOME": str(tmp_path / "khe")}
    return hoi_app_server([sys.executable, str(GIA)], env=env, **kw)


def test_bat_tay_roi_hoi_rate_limits(tmp_path):
    kq = _hoi(tmp_path, "ok")
    assert kq["rateLimits"]["primary"]["windowDurationMins"] == 300
    nhan = json.loads((tmp_path / "nhan.json").read_text())
    assert nhan[0] == {"CODEX_HOME": str(tmp_path / "khe")}
    assert [(t.get("method"), t.get("id")) for t in nhan[1:]] == [
        ("initialize", 0), ("initialized", None), ("account/rateLimits/read", 1)]
    assert nhan[1]["params"]["clientInfo"]["name"] == "tram"


@pytest.mark.parametrize("che_do, mau", [("loi", "chưa đăng nhập"), ("dong", "đóng trước")])
def test_loi_hoac_dong_som(tmp_path, che_do, mau):
    with pytest.raises(LoiAppServer, match=mau):
        _hoi(tmp_path, che_do)


def test_treo_thi_het_gio_va_giet(tmp_path):
    t0 = time.monotonic()
    with pytest.raises(LoiAppServer, match="không trả lời trong 1 giây"):
        _hoi(tmp_path, "treo", thoi_gian_cho=1)
    assert time.monotonic() - t0 < 10


def test_doc_han_muc_ranh_chuan_hoa_va_moi_truong_toi_thieu(tmp_path, monkeypatch):
    monkeypatch.setenv("TRAM_TOKEN_BAT_KY", "bi-mat")
    goi = []
    mau = json.loads((GIA.parent / "app_server_rate_limits.json").read_text(encoding="utf-8"))["plus"]
    hm = doc_han_muc_ranh("C/codex-1", tmp_path / "khe", bay_gio=LUC,
                          hoi=lambda argv, env: goi.append((argv, env)) or mau)
    assert hm.nguon == "app-server" and {c.loai for c in hm.cua_so} == {"5h", "tuan"}
    argv, env = goi[0]
    assert argv == ["codex", "app-server"] and env["CODEX_HOME"] == str(tmp_path / "khe")
    assert not any(k.startswith("TRAM_") for k in env)

    def hong(argv, env):
        raise LoiAppServer("x")
    assert doc_han_muc_ranh("C/codex-1", tmp_path, bay_gio=LUC, hoi=hong) is None
    assert doc_han_muc_ranh("C/codex-1", tmp_path, bay_gio=LUC, hoi=lambda a, env: {}) is None
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_codex_app_server.py -q`
Expected: FAIL — `1 error` (`ModuleNotFoundError: No module named 'tram.chay_cli.codex.app_server'`)

- [ ] **Step 3: Viết mã**

`tram/chay_cli/codex/app_server.py` (mới):

```python
"""Hỏi hạn mức Codex qua `codex app-server` lúc khe RẢNH (spec 3 §8.1: mỗi 5 phút, không cần gửi tin cho model).

Giao thức theo tài liệu app-server (JSON-RPC qua stdio, mỗi dòng một JSON, không trường `jsonrpc`): `initialize` (id 0)
→ chờ trả lời → thông báo `initialized` → `account/rateLimits/read` (id 1). CHƯA chạy thật — chờ spike S5 (dưới launchd,
`CODEX_HOME` riêng của khe). Tiến trình chạy trong nhóm riêng, quá hạn thì giết cả nhóm. Môi trường tối thiểu: không
mang token máy hay biến `TRAM_*`."""
import json
import os
import signal
import subprocess
import threading
from datetime import datetime
from pathlib import Path

from tram.chay_cli.codex.han_muc import han_muc_app_server
from tram.han_muc.mo_hinh import HanMuc

PHUONG_THUC = "account/rateLimits/read"
CHU_KY_RANH_GIAY = 300
BIEN_GIU = ("PATH", "HOME", "LANG", "USER", "TMPDIR")


class LoiAppServer(RuntimeError):
    pass


def _gui(p, tin: dict) -> None:
    p.stdin.write(json.dumps(tin) + "\n")
    p.stdin.flush()


def _cho(p, ma: int) -> dict:
    for dong in p.stdout:
        try:
            tin = json.loads(dong)
        except ValueError:
            continue
        if isinstance(tin, dict) and tin.get("id") == ma:
            if "error" in tin:
                loi = tin["error"] if isinstance(tin["error"], dict) else {}
                raise LoiAppServer(f"app-server trả lỗi: {str(loi.get('message', ''))[:120]}")
            return tin["result"] if isinstance(tin.get("result"), dict) else {}
    raise LoiAppServer("app-server đóng trước khi trả lời")


def _giet(p) -> None:
    if p.poll() is not None:
        return
    try:
        os.killpg(p.pid, signal.SIGTERM)
        p.wait(2)
    except subprocess.TimeoutExpired:
        os.killpg(p.pid, signal.SIGKILL)
        p.wait()
    except ProcessLookupError:
        pass


def hoi_app_server(argv: list[str], *, env: dict[str, str], thoi_gian_cho: float = 20.0,
                   popen=subprocess.Popen) -> dict:
    p = popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, env=env, text=True,
              start_new_session=True)
    qua_gio = threading.Event()
    hen = threading.Timer(thoi_gian_cho, lambda: (qua_gio.set(), _giet(p)))
    hen.start()
    try:
        _gui(p, {"method": "initialize", "id": 0, "params": {"clientInfo": {"name": "tram", "title": "Tram dieu phoi",
                                                                             "version": "3b"}}})
        _cho(p, 0)
        _gui(p, {"method": "initialized"})
        _gui(p, {"method": PHUONG_THUC, "id": 1})
        return _cho(p, 1)
    except (LoiAppServer, OSError) as e:
        if qua_gio.is_set():
            raise LoiAppServer(f"app-server không trả lời trong {thoi_gian_cho:g} giây") from None
        raise e if isinstance(e, LoiAppServer) else LoiAppServer(f"app-server lỗi: {type(e).__name__}") from None
    finally:
        hen.cancel()
        _giet(p)


def doc_han_muc_ranh(khe_id: str, thu_muc_cau_hinh: Path, *, bay_gio: datetime, codex: str = "codex",
                     hoi=hoi_app_server) -> HanMuc | None:
    """Số đo của khe, hoặc None khi không đọc được (vòng 3a-2 gửi nhịp không có số đo → cửa sổ chưa biết, #15)."""
    env = {k: os.environ[k] for k in BIEN_GIU if k in os.environ}
    env["CODEX_HOME"] = str(thu_muc_cau_hinh)
    try:
        kq = hoi([codex, "app-server"], env=env)
    except (LoiAppServer, OSError):
        return None
    return han_muc_app_server(kq, khe_id=khe_id, bay_gio=bay_gio)
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_codex_app_server.py -q`
Expected: `5 passed` (ca "treo" mất ~1 giây)

Run: `uv run pytest -q`
Expected: `N₀+36 passed` (trên `main` sau đợt 1 + riêng task này)

- [ ] **Step 5: Commit**

```bash
git add tram/chay_cli/codex/app_server.py tests/du_lieu/codex/app_server_gia.py tests/test_codex_app_server.py
git commit -m "feat(codex): hỏi account/rateLimits/read qua codex app-server, quá hạn giết nhóm — chờ spike S5 (spec 3 §8.1)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 8: `ChayCLI` cho Codex — đọc stream `codex exec --json`, dừng cả nhóm, log che `ma_giao` (chờ S5)

**Độ khó:** `kho` · **Đợt:** 2 · **Song song với:** Task 7, 9, 10 · **Phải xong trước:** Task 2

**Files:**
- Create: `tram/chay_cli/codex/luong.py`
- Create: `tram/chay_cli/codex/chay.py`
- Test: `tests/du_lieu/codex/exec_xong.jsonl`, `exec_het_han_muc.jsonl`, `exec_chua_dang_nhap.jsonl` (mới — fixture, chờ S5)
- Test: `tests/du_lieu/codex/exec_gia.py` (mới — script giả, CHỈ DÙNG TRONG TEST)
- Test: `tests/test_codex_chay.py` (mới)

**Interfaces:**
- Consumes: `MAU_CHUA_DANG_NHAP`, `thong_diep_loi`, `NguonHanMucCodex` (Task 2); `KetQuaChay`, `ket_thuc_tu`, `ChayCLI` (`tram/chay_cli/giao_dien.py`); `che_ma_giao` (`tram/phieu/mo_hinh.py`).
- Produces: `tram/chay_cli/codex/luong.py`: `DocLuongCodex(nguon)` + `.nap(dong)`, `.ket_qua(*, ma_thoat, bi_dung, thoi_gian_ms, digest_log) -> KetQuaChay`. `tram/chay_cli/codex/chay.py`: `ChayCodex(*, popen, cho_dung_giay=10.0)` + `.chay(argv, *, cwd, env, stdin, log, dung, nguon) -> KetQuaChay` (thoả Protocol `ChayCLI`).

- [ ] **Step 1: Viết test thất bại**

`tests/du_lieu/codex/exec_xong.jsonl` (mới):

```text
{"_ghi_chu": "CHỈ DÙNG TRONG TEST — sự kiện codex exec --json theo hiểu biết hiện tại, CHƯA xác minh bằng chạy thật (chờ spike S5)"}
{"type": "thread.started", "thread_id": "0199-gia"}
{"type": "turn.started"}
{"type": "item.completed", "item": {"id": "item_0", "type": "reasoning", "text": "Đọc .tram/goi.md"}}
{"type": "item.started", "item": {"id": "item_1", "type": "command_execution", "command": "bash -lc 'php artisan test'", "aggregated_output": "", "exit_code": null, "status": "in_progress"}}
cảnh báo: dòng stderr không phải json
{"type": "item.completed", "item": {"id": "item_1", "type": "command_execution", "command": "bash -lc 'php artisan test'", "aggregated_output": "OK (3 tests)", "exit_code": 0, "status": "completed"}}
{"type": "item.completed", "item": {"id": "item_2", "type": "agent_message", "text": "Đã sửa, mã MA-GIAO-BI-MAT không được lộ"}}
{"type": "turn.completed", "usage": {"input_tokens": 24763, "cached_input_tokens": 24448, "output_tokens": 1122}}
```

`tests/du_lieu/codex/exec_het_han_muc.jsonl` (mới):

```text
{"type": "thread.started", "thread_id": "0199-gia"}
{"type": "turn.started"}
{"type": "error", "message": "You've hit your usage limit. Upgrade or try again in 2 hours."}
{"type": "turn.failed", "error": {"message": "You've hit your usage limit."}}
```

`tests/du_lieu/codex/exec_chua_dang_nhap.jsonl` (mới):

```text
{"type": "thread.started", "thread_id": "0199-gia"}
{"type": "turn.failed", "error": {"message": "unexpected status 401 Unauthorized: not logged in"}}
```

`tests/du_lieu/codex/exec_gia.py` (mới):

```python
"""`codex exec --json` GIẢ — CHỈ DÙNG TRONG TEST (chạy bằng sys.executable). In từng dòng của $FIXTURE, chép stdin
vào $GHI, thoát mã $MA. CHE_DO=treo: in dòng đầu rồi bỏ qua SIGTERM và ngủ (thử leo thang SIGKILL)."""
import os
import signal
import sys
import time
from pathlib import Path

Path(os.environ["GHI"]).write_text(sys.stdin.read(), encoding="utf-8")
dong = Path(os.environ["FIXTURE"]).read_text(encoding="utf-8").splitlines()
if os.environ.get("CHE_DO") == "treo":
    print(dong[0], flush=True)
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    time.sleep(30)
for d in dong:
    print(d, flush=True)
sys.exit(int(os.environ.get("MA", "0")))
```

`tests/test_codex_chay.py` (mới):

```python
import hashlib
import sys
import threading
import time
from pathlib import Path

from tram.chay_cli.codex.chay import ChayCodex
from tram.chay_cli.codex.han_muc import NguonHanMucCodex
from tram.chay_cli.codex.luong import DocLuongCodex
from tram.chay_cli.giao_dien import ChayCLI, ket_thuc_tu

DL = Path(__file__).parent / "du_lieu" / "codex"


def _chay(tmp_path, fixture, *, ma=0, che_do="", dung=None, **kw):
    (tmp_path / "goi.md").write_text("# Gói ngữ cảnh\n", encoding="utf-8")
    env = {"FIXTURE": str(DL / fixture), "GHI": str(tmp_path / "stdin.txt"), "MA": str(ma), "CHE_DO": che_do,
           "TRAM_MA_GIAO": "MA-GIAO-BI-MAT"}
    return ChayCodex(**kw).chay([sys.executable, str(DL / "exec_gia.py")], cwd=tmp_path, env=env,
                                stdin=tmp_path / "goi.md", log=tmp_path / "log" / "lan-1.jsonl",
                                dung=dung or threading.Event(), nguon=NguonHanMucCodex())


def test_xong_dem_token_va_log_che_ma_giao(tmp_path):
    boc, pid, kills = [], [], []
    from tram.tho.mo_coi import kill_cuc_bo
    def kill(p, sig):
        kills.append((p, sig))
        kill_cuc_bo(p, sig)
    kq = _chay(tmp_path, "exec_xong.jsonl", boc=lambda a: (boc.append(a) or a),
               khe_id="C/codex-1", khi_bat_dau=pid.append, kill=kill)
    assert len(boc) == len(pid) == 1 and kills[-1][0] == pid[0]
    assert isinstance(ChayCodex(), ChayCLI) and ket_thuc_tu(kq) == "xong"
    assert (kq.ma_thoat, kq.co_assistant, kq.het_han_muc, kq.chua_dang_nhap) == (0, True, False, False)
    assert (kq.token_vao, kq.token_cache_doc, kq.token_ra) == (315, 24448, 1122)
    assert (tmp_path / "stdin.txt").read_text(encoding="utf-8") == "# Gói ngữ cảnh\n"
    log = (tmp_path / "log" / "lan-1.jsonl").read_bytes()
    assert b"MA-GIAO-BI-MAT" not in log and "mã *** không".encode() in log and b"stderr" in log
    assert kq.digest_log == "sha256:" + hashlib.sha256(log).hexdigest() and kq.thoi_gian_ms >= 0


def test_het_han_muc_va_chua_dang_nhap(tmp_path):
    kq = _chay(tmp_path, "exec_het_han_muc.jsonl", ma=1)
    assert kq.het_han_muc and ket_thuc_tu(kq) == "het_han_muc"
    kq = _chay(tmp_path, "exec_chua_dang_nhap.jsonl", ma=1)
    assert kq.chua_dang_nhap and not kq.co_assistant and ket_thuc_tu(kq) == "loi_he"


def test_dung_giet_ca_nhom_ke_ca_khi_bo_qua_sigterm(tmp_path):
    dung = threading.Event()
    threading.Timer(0.5, dung.set).start()
    t0 = time.monotonic()
    kq = _chay(tmp_path, "exec_xong.jsonl", che_do="treo", dung=dung, cho_dung_giay=0.5)
    assert ket_thuc_tu(kq) == "dung" and kq.bi_dung and time.monotonic() - t0 < 10
    kq = _chay(tmp_path, "exec_xong.jsonl", tran_token_ra=100)
    assert kq.bi_dung and kq.token_ra == 1122


def test_doc_luong_bo_qua_dong_la_va_usage_thieu():
    d = DocLuongCodex(NguonHanMucCodex())
    for dong in ({"type": "turn.completed"}, {"type": "turn.completed", "usage": {"input_tokens": "x"}},
                 {"type": "item.completed", "item": "x"}, {"type": "item.completed", "item": {"type": "reasoning"}},
                 {"type": "turn.completed", "usage": {"input_tokens": 10, "cached_input_tokens": 30}}):
        d.nap(dong)
    kq = d.ket_qua(ma_thoat=1, bi_dung=False, thoi_gian_ms=5, digest_log="sha256:x")
    assert (kq.token_vao, kq.token_cache_doc, kq.token_ra, kq.co_assistant) == (0, 30, 0, False)
    assert ket_thuc_tu(kq) == "loi_he"
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_codex_chay.py -q`
Expected: FAIL — `1 error` (`ModuleNotFoundError: No module named 'tram.chay_cli.codex.chay'`)

- [ ] **Step 3: Viết mã**

`tram/chay_cli/codex/luong.py` (mới):

```python
"""Đọc stream `codex exec --json` của một lần chạy (spec 3 §7.2, §7.8) — bộ chuẩn hoá riêng của Codex, không dùng
parser của Claude. HÌNH DẠNG CHƯA XÁC MINH (chờ spike S5); theo hiểu biết hiện tại các sự kiện là: `thread.started`,
`turn.started`, `item.started|updated|completed {item: {type: agent_message | reasoning | command_execution | …}}`,
`turn.completed {usage: {input_tokens, cached_input_tokens, output_tokens}}`, `turn.failed {error: {message}}`,
`error {message}`. Trường thiếu/sai → bỏ qua (đếm 0), không đoán."""
from tram.chay_cli.codex.han_muc import MAU_CHUA_DANG_NHAP, thong_diep_loi
from tram.chay_cli.giao_dien import KetQuaChay
from tram.han_muc.nguon import NguonHanMuc


def _so(usage: dict, khoa: str) -> int:
    x = usage.get(khoa)
    return x if isinstance(x, int) and not isinstance(x, bool) and x > 0 else 0


class DocLuongCodex:
    def __init__(self, nguon: NguonHanMuc):
        self.nguon = nguon
        self.co_assistant = self.het_han_muc = self.chua_dang_nhap = False
        self.token_vao = self.token_cache_doc = self.token_ra = 0

    def nap(self, dong: dict) -> None:
        loai, item = dong.get("type"), dong.get("item")
        if loai == "item.completed" and isinstance(item, dict) and item.get("type") == "agent_message":
            self.co_assistant = True
        elif loai == "turn.completed" and isinstance(dong.get("usage"), dict):
            u = dong["usage"]
            cache = _so(u, "cached_input_tokens")
            self.token_vao += max(_so(u, "input_tokens") - cache, 0)   # input_tokens của Codex GỒM phần cache
            self.token_cache_doc += cache
            self.token_ra += _so(u, "output_tokens")
        loi = thong_diep_loi(dong)
        if loi and MAU_CHUA_DANG_NHAP.search(loi):
            self.chua_dang_nhap = True
        if self.nguon.het_han_muc(dong):
            self.het_han_muc = True

    def ket_qua(self, *, ma_thoat: int | None, bi_dung: bool, thoi_gian_ms: int, digest_log: str) -> KetQuaChay:
        return KetQuaChay(ma_thoat=ma_thoat, co_assistant=self.co_assistant, het_han_muc=self.het_han_muc,
                          chua_dang_nhap=self.chua_dang_nhap, bi_dung=bi_dung, token_vao=self.token_vao,
                          token_ra=self.token_ra, token_cache_doc=self.token_cache_doc, thoi_gian_ms=thoi_gian_ms,
                          digest_log=digest_log)
```

`tram/chay_cli/codex/chay.py` (mới):

```python
"""Codex dưới principal, callback pid, budget và dọn nhóm con (S5/S6 chưa kiểm thật)."""
import hashlib
import json
import signal
import subprocess
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

from tram.chay_cli.codex.luong import DocLuongCodex
from tram.chay_cli.giao_dien import KetQuaChay
from tram.han_muc.nguon import NguonHanMuc
from tram.phieu.mo_hinh import che_ma_giao
from tram.tho.mo_coi import dung_nhom, kill_cuc_bo


class ChayCodex:
    def __init__(self, boc=lambda a: a, *, khe_id="", kill=kill_cuc_bo, khi_bat_dau=None,
                 khi_han_muc=None, tran_token_ra=None, popen=subprocess.Popen, cho_dung_giay=10.0):
        self.boc, self.khe_id, self.kill = boc, khe_id, kill
        self.khi_bat_dau, self.khi_han_muc = khi_bat_dau, khi_han_muc
        self.tran_token_ra, self.popen, self.cho_dung_giay = tran_token_ra, popen, cho_dung_giay

    def _canh(self, pid, dung, xong):
        while not xong.wait(0.05):
            if dung.is_set():
                dung_nhom(pid, kill=self.kill, cho=self.cho_dung_giay)
                return

    def _doc(self, p, ghi, doc, dung, nguon, ma_giao):
        for tho in p.stdout:
            dong = che_ma_giao(tho.decode("utf-8", errors="replace"), ma_giao)
            ghi.write(dong.encode())
            ghi.flush()
            try:
                obj = json.loads(dong)
            except ValueError:
                continue
            if not isinstance(obj, dict):
                continue
            doc.nap(obj)
            hm = nguon.doc_dong(obj, khe_id=self.khe_id, bay_gio=datetime.now(timezone.utc))
            if hm is not None and self.khi_han_muc:
                self.khi_han_muc(hm)
            if self.tran_token_ra is not None and doc.token_ra >= self.tran_token_ra:
                dung.set()

    def chay(self, argv: list[str], *, cwd: Path, env: dict[str, str], stdin: Path, log: Path,
             dung: threading.Event, nguon: NguonHanMuc) -> KetQuaChay:
        doc, t0, ma = DocLuongCodex(nguon), time.monotonic(), None
        log.parent.mkdir(parents=True, exist_ok=True)
        with open(stdin, "rb") as vao, open(log, "wb") as ghi:
            try:
                p = self.popen(self.boc(argv), cwd=cwd, env=env, stdin=vao, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, start_new_session=True)
            except OSError as e:
                ghi.write(f"[tram] lỗi khởi chạy CLI: {type(e).__name__}\n".encode())
            else:
                if self.khi_bat_dau:
                    self.khi_bat_dau(p.pid)
                xong = threading.Event()
                canh = threading.Thread(target=self._canh, args=(p.pid, dung, xong), daemon=True)
                doc_t = threading.Thread(target=self._doc,
                    args=(p, ghi, doc, dung, nguon, env.get("TRAM_MA_GIAO")), daemon=True)
                canh.start()
                doc_t.start()
                ma = p.wait()
                xong.set()
                canh.join()
                self.kill(p.pid, signal.SIGKILL)
                doc_t.join(timeout=self.cho_dung_giay)
                if doc_t.is_alive():
                    raise RuntimeError("Không dọn được nhóm CLI; dừng khe để kiểm principal")
        digest = "sha256:" + hashlib.sha256(log.read_bytes()).hexdigest()
        return doc.ket_qua(ma_thoat=ma, bi_dung=dung.is_set(), thoi_gian_ms=int((time.monotonic() - t0) * 1000),
                           digest_log=digest)
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_codex_chay.py -q`
Expected: `4 passed`

Run: `uv run pytest -q`
Expected: `N₀+35 passed` (trên `main` sau đợt 1 + riêng task này)

- [ ] **Step 5: Commit**

```bash
git add tram/chay_cli/codex/luong.py tram/chay_cli/codex/chay.py tests/du_lieu/codex/exec_xong.jsonl tests/du_lieu/codex/exec_het_han_muc.jsonl tests/du_lieu/codex/exec_chua_dang_nhap.jsonl tests/du_lieu/codex/exec_gia.py tests/test_codex_chay.py
git commit -m "feat(codex): ChayCLI cho codex exec --json — token, hết hạn mức, chưa đăng nhập, dừng cả nhóm — chờ spike S5 (spec 3 §7.2, §7.8)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 9: `POST /api/ghep-may` và lệnh `tram chu cap-ma`

**Độ khó:** `de` · **Đợt:** 2 · **Song song với:** Task 7, 8, 10 · **Phải xong trước:** Task 1, Task 4

**Files:**
- Create: `tram/api/ghep.py`
- Create: `tram/chu/cap_ma.py`
- Modify: `tram/api/app.py` (dòng neo: `from tram.api import …`, `CAC_TUYEN = (…`)
- Modify: `tram/tho/lenh.py` (dòng neo: `    g.set_defaults(ham=_go_may)` trong `them_lenh_tho`)
- Test: `tests/test_ghep_may.py` (mới)

**Interfaces:**
- Consumes: `doi_ma_ghep`, `cap_ma_ghep`, `MaGhepSai`, `GhepBiKhoa` (Task 1); `TAG_THO` (Task 4); `PhuThuocApi.mo_kho_phieu`, `.dong_ho`; `nap_cau_hinh_tram().ten_may_b`; `mo_kho_phieu`. Test: `tao_tram`, `main`.
- Produces: `tram/api/ghep.py`: `router` (`POST /api/ghep-may` — G1), `ThanGhep(ma)`. `tram/chu/cap_ma.py`: `them_lenh_cap_ma(chu)` → `tram chu cap-ma <may_id>` (mã 0 in mã; mã 2 khi máy đang có token / `may_id` sai).

- [ ] **Step 1: Viết test thất bại**

`tests/test_ghep_may.py` (mới):

```python
import re
from datetime import datetime, timezone

from tho_api_gia import tao_tram
from tram.cli import main
from tram.phieu.kho import mo_kho_phieu
from tram.phieu.ma_ghep import cap_ma_ghep
from tram.phieu.may import cap_token_may, xac_thuc_may


def test_doi_ma_qua_http_khong_can_bearer_token_dung_duoc_ngay(tmp_path):
    t = tao_tram(tmp_path, dang_ky=False)
    kho = t.kho()
    ma = cap_ma_ghep(kho, "C2", luc=t.gio[0]).ma
    r = t.goi("POST", "/api/ghep-may", None, json_body={"ma": ma})
    assert r.status == 200 and r.headers["cache-control"] == "no-store" and r.json()["may_id"] == "C2"
    tok = r.json()["token"]
    assert xac_thuc_may(kho, tok) == "C2"
    t.token["C2"] = tok
    assert t.goi("GET", "/api/tho/ping", "C2").json() == {"may_id": "C2", "khe": []}
    lai = t.goi("POST", "/api/ghep-may", None, json_body={"ma": ma})
    assert lai.status == 403 and tok not in lai.body.decode() and "token" not in lai.json()


def test_sai_nhieu_lan_bi_khoa_429_than_sai_422(tmp_path):
    t = tao_tram(tmp_path, dang_ky=False)
    ma = cap_ma_ghep(t.kho(), "C2", luc=t.gio[0]).ma
    for _ in range(5):
        assert t.goi("POST", "/api/ghep-may", None, json_body={"ma": "0000-0000-0000"}).status == 403
    assert t.goi("POST", "/api/ghep-may", None, json_body={"ma": ma}).status == 429
    for than in ({}, {"ma": ma, "may_id": "X"}, {"ma": "x" * 65}):
        assert t.goi("POST", "/api/ghep-may", None, json_body=than).status == 422


def test_cli_chu_cap_ma(tram_home_tam, capsys):
    assert main(["chu", "cap-ma", "C"]) == 0
    ra = capsys.readouterr().out
    assert re.search(r"Mã ghép máy C: [0-9A-Z]{4}-[0-9A-Z]{4}-[0-9A-Z]{4}", ra) and "tram tho dang-ky" in ra
    kho = mo_kho_phieu()
    cap_token_may(kho, "D", luc=datetime.now(timezone.utc))
    assert main(["chu", "cap-ma", "D"]) == 2 and "go-may" in capsys.readouterr().err
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_ghep_may.py -q`
Expected: FAIL — `3 failed` (`assert (404 == 200)` — chưa có `/api/ghep-may`; `SystemExit: 2` — chưa có lệnh `cap-ma`)

- [ ] **Step 3: Viết mã**

`tram/api/ghep.py` (mới):

```python
"""`POST /api/ghep-may {ma}` (spec 3 §9.2): Mac thợ từ xa đổi mã ghép dùng một lần lấy token máy. KHÔNG nằm trong
nhóm `/api/tho/*` (chưa có token máy để gửi) — bằng chứng duy nhất là mã ghép. Phản hồi `Cache-Control: no-store`;
lỗi không bao giờ nói mã thuộc máy nào. Không dùng danh tính Tailscale (Mac thợ là thiết bị gắn tag)."""
from contextlib import closing

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from tram.phieu.ma_ghep import GhepBiKhoa, MaGhepSai, doi_ma_ghep

router = APIRouter()


class ThanGhep(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ma: str = Field(min_length=1, max_length=64)


@router.post("/api/ghep-may")
def ghep_may(than: ThanGhep, request: Request):
    pt = request.app.state.pt
    if pt.mo_kho_phieu is None:
        return JSONResponse({"loi": "Kho phiếu chưa bật"}, status_code=503)
    with closing(pt.mo_kho_phieu()) as kho:
        try:
            may_id, token = doi_ma_ghep(kho, than.ma, luc=pt.dong_ho())
        except GhepBiKhoa as e:
            return JSONResponse({"loi": str(e)}, status_code=429)
        except MaGhepSai as e:
            return JSONResponse({"loi": str(e)}, status_code=403)
    return JSONResponse({"may_id": may_id, "token": token}, headers={"Cache-Control": "no-store"})
```

`tram/chu/cap_ma.py` (mới):

```python
"""`tram chu cap-ma <may_id>` (spec 3 §9.2) — chạy ở TÀI KHOẢN TRẠM: in mã ghép dùng một lần, hết hạn sau 10 phút,
cho Mac thợ từ xa `tram tho dang-ky`. Mã là bí mật ngắn hạn: chỉ in ra màn hình, không ghi file/log."""
import sys
from contextlib import closing
from datetime import datetime, timezone


def _cap_ma(args) -> int:
    from tram.cau_hinh.tram import nap_cau_hinh_tram
    from tram.phieu.kho import mo_kho_phieu
    from tram.phieu.ma_ghep import cap_ma_ghep
    from tram.tho.do_may import TAG_THO
    try:
        with closing(mo_kho_phieu()) as kho:
            mg = cap_ma_ghep(kho, args.may_id, luc=datetime.now(timezone.utc))
    except ValueError as e:
        print(e, file=sys.stderr)
        return 2
    try:
        may_b = nap_cau_hinh_tram().ten_may_b or "<máy B>.<tailnet>.ts.net"
    except ValueError:
        may_b = "<máy B>.<tailnet>.ts.net"
    print(f"Mã ghép máy {mg.may_id}: {mg.ma} — dùng một lần, hết hạn {mg.het_luc} (UTC).")
    print(f"Trên Mac thợ (thiết bị Tailscale gắn {TAG_THO}, tài khoản quản lý thợ):")
    print(f"  tram tho dang-ky --tram-chu https://{may_b} --khe <ten>:<cli>:<vai,…>:<tên gợi nhớ>")
    return 0


def them_lenh_cap_ma(chu) -> None:
    c = chu.add_parser("cap-ma", help="In mã ghép dùng một lần (10 phút) cho Mac thợ từ xa")
    c.add_argument("may_id", help="Tên máy thợ mới, vd C")
    c.set_defaults(ham=_cap_ma)
```

`tram/api/app.py` (sửa — bản vá trên nền sau 1b-3 Task 9 + 2b Task 11; G20 nếu 4a-2 đã đổi dòng neo):

```diff
diff --git a/tram/api/app.py b/tram/api/app.py
index 68b7e72..e9cd149 100644
--- a/tram/api/app.py
+++ b/tram/api/app.py
@@ -3,7 +3,7 @@ from fastapi import FastAPI, Request
 from fastapi.responses import JSONResponse
 from fastapi.staticfiles import StaticFiles
 
-from tram.api import doi_ngu, luong, noi_bo, tho, tho_them, tuyen_chu, tuyen_doc, tuyen_ghi, tuyen_nho, usage
+from tram.api import doi_ngu, ghep, luong, noi_bo, tho, tho_them, tuyen_chu, tuyen_doc, tuyen_ghi, tuyen_nho, usage
 from tram.api.bao_mat import them_header_an_toan
 from tram.api.phu_thuoc import PhuThuocApi
 from tram.beads.bd import KhongThayBead, LoiBd
@@ -14,7 +14,7 @@ from tram.thao_tac.loi import ChuaHoTro, KhongHopLe, KhongThay, XungDot
 MA_LOI = {XungDot: 409, KhongHopLe: 422, ChuaHoTro: 501, KhongThay: 404, KhongThayBead: 404, LoiBd: 502,
           LoiNhoKhach: 503}
 CAC_TUYEN = (tuyen_doc.router, tuyen_ghi.router, tuyen_chu.router, tuyen_nho.router, luong.router, tho.router, noi_bo.router,
-             doi_ngu.router, usage.router, tho_them.router)
+             doi_ngu.router, usage.router, tho_them.router, ghep.router)
 
 
 def _xu_ly(ma: int):
```

`tram/tho/lenh.py` (sửa — bản vá; dòng neo `    g.set_defaults(ham=_go_may)` — nếu 3a-2 đã thêm dòng sau mốc thì chèn tay hai dòng `+` ngay sau dòng neo, G20):

```diff
diff --git a/tram/tho/lenh.py b/tram/tho/lenh.py
index fdb497f..d49ec44 100644
--- a/tram/tho/lenh.py
+++ b/tram/tho/lenh.py
@@ -64,3 +64,5 @@ def them_lenh_tho(sub, chu) -> None:
     g.add_argument("may_id")
     g.add_argument("--dong-y", action="store_true", help="Bỏ bước hỏi")
     g.set_defaults(ham=_go_may)
+    from tram.chu.cap_ma import them_lenh_cap_ma
+    them_lenh_cap_ma(chu)
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_ghep_may.py tests/test_api_tho.py tests/test_tho_lenh.py -q`
Expected: `3 passed` cho file mới; mọi test của hai file 3a-1 vẫn pass

Run: `uv run pytest -q`
Expected: `N₀+34 passed` (trên `main` sau đợt 1 + riêng task này)

- [ ] **Step 5: Commit**

```bash
git add tram/api/ghep.py tram/chu/cap_ma.py tram/api/app.py tram/tho/lenh.py tests/test_ghep_may.py
git commit -m "feat(api): POST /api/ghep-may đổi mã ghép lấy token máy; tram chu cap-ma (spec 3 §9.2)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 10: Kế hoạch `tram tho dang-ky` — dò, khai khe, liệt kê thay đổi (chưa ghi gì)

**Độ khó:** `kho` · **Đợt:** 2 · **Song song với:** Task 7, 8, 9 · **Phải xong trước:** Task 3, 4, 5, 6

**Files:**
- Create: `tram/tho/khai_khe.py`
- Create: `tram/tho/ke_hoach_dk.py`
- Test: `tests/tho_dk_gia.py` (mới — đầu dò giả, CHỈ DÙNG TRONG TEST)
- Test: `tests/test_ke_hoach_dk.py` (mới)

**Interfaces:**
- Consumes: `CLI`, `TEN_KHE_RE`, `VAI`, `nap_cau_hinh_tho` (Task 3 / 3a-1); `KetQuaDo`, `TAG_THO`, `do_cli`, `kiem_tag` (Task 4); `ghep_codex_toml`, `lenh_claude_mcp`, `url_nho` (Task 5); `NHAN_THO`, `lenh_nap_launchd`, `tao_plist_tho` (Task 6).
- Produces: `tram/tho/khai_khe.py`: `KheKhai(ten, cli, vai_uu_tien, ten_goi_nho)`, `doc_khe(chuoi) -> KheKhai`, `noi_dung_tho_yaml(may_id, tram_api, khe) -> str`. `tram/tho/ke_hoach_dk.py`: `DauDoDK(which, chay, home, uid, tram_home)`, `KeHoachDangKy(tram_chu, khe, do, tep, so_sanh, lenh_mcp, lenh_launchd, canh_bao, tho_yaml)`, `lap_ke_hoach_dk(tram_chu, khe, *, thu_muc_khe, nho, dd) -> KeHoachDangKy` (ValueError theo G8), `in_ke_hoach_dk(kh) -> str`. `tests/tho_dk_gia.py`: `URL`, `dau_do(tmp_path, *, tags, co, dang_nhap, goi) -> DauDoDK`. `kh.khe` là list dict `{ten, cli, thu_muc_cau_hinh, ten_goi_nho, vai_uu_tien}`.

- [ ] **Step 1: Viết test thất bại**

`tests/tho_dk_gia.py` (mới):

```python
"""Đầu dò giả cho `tram tho dang-ky` (CHỈ DÙNG TRONG TEST): Mac thợ có `tram`, `codex`, `claude`, Tailscale gắn tag."""
import json
import subprocess
from pathlib import Path

from tram.tho.do_may import TAG_THO
from tram.tho.ke_hoach_dk import DauDoDK

URL = "https://may-b.tail1234.ts.net"


def dau_do(tmp_path: Path, *, tags=(TAG_THO,), co=("tram", "codex", "claude", "tailscale"), dang_nhap=0,
           goi: list | None = None) -> DauDoDK:
    goi = [] if goi is None else goi

    def chay(argv, **kw):
        goi.append(argv)
        if argv[1:] == ["status", "--json"]:
            return subprocess.CompletedProcess(argv, 0, json.dumps({"Self": {"Tags": list(tags)}}), "")
        if argv[1:] == ["login", "status"]:
            return subprocess.CompletedProcess(argv, dang_nhap, "", "")
        return subprocess.CompletedProcess(argv, 0, f"{Path(argv[0]).name} 1.0\n", "")
    return DauDoDK(which=lambda c: f"/opt/bin/{c}" if c in co else None, chay=chay, home=tmp_path / "home",
                   uid=501, tram_home=tmp_path / "home" / ".tram", daemon=tmp_path / "daemon.plist")
```

`tests/test_ke_hoach_dk.py` (mới):

```python
import plistlib
import tomllib

import pytest

from tho_dk_gia import URL, dau_do
from tram.tho.ke_hoach_dk import in_ke_hoach_dk, lap_ke_hoach_dk
from tram.tho.khai_khe import doc_khe, noi_dung_tho_yaml

CODEX = doc_khe("codex-1:codex:coder,qc:Codex tài khoản 1")
CLAUDE = doc_khe("claude-3:claude:spec:Claude tài khoản 3")


def _kh(tmp_path, khe=(CODEX, CLAUDE), nho=True, **kw):
    goi = []
    kh = lap_ke_hoach_dk(URL + "/", list(khe), thu_muc_khe=tmp_path / "khe", nho=nho,
                         dd=dau_do(tmp_path, goi=goi, **kw))
    return kh, goi


@pytest.mark.parametrize("sai", ["codex-1:codex:coder", "Codex:codex:coder:x", "g:gemini:coder:x",
                                 "c:codex:admin:x", "c:codex::x", "c:codex:qc:a@b.c", "c:codex:qc: "])
def test_doc_khe_sai(sai):
    with pytest.raises(ValueError):
        doc_khe(sai)


def test_ke_hoach_chi_do_khong_ghi_gi(tmp_path):
    kh, goi = _kh(tmp_path)
    assert not (tmp_path / "home").exists() and not (tmp_path / "khe").exists()
    assert all(a[1:] in (["--version"], ["login", "status"], ["status", "--json"]) for a in goi)
    assert kh.tram_chu == URL and [k["ten"] for k in kh.khe] == ["codex-1", "claude-3"]
    assert kh.khe[0]["thu_muc_cau_hinh"] == str(tmp_path / "khe" / "codex-1")
    toml = kh.tep[tmp_path / "khe" / "codex-1" / "config.toml"].decode()
    assert tomllib.loads(toml)["mcp_servers"]["tram-nho"]["url"] == URL + "/nho/mcp"
    plist = plistlib.loads(kh.tep[tmp_path / "home/Library/LaunchAgents/vn.tram.tho.plist"])
    assert plist["ProgramArguments"] == ["/opt/bin/tram", "tho", "chay"]
    assert kh.lenh_mcp[1][0][:4] == ["/opt/bin/claude", "mcp", "add-json", "--scope"]
    pl = str(tmp_path / "home/Library/LaunchAgents/vn.tram.tho.plist")
    assert kh.lenh_launchd[-1] == ["launchctl", "bootstrap", "gui/501", pl]
    van_ban = in_ke_hoach_dk(kh)
    for y in ("Đổi mã ghép", "Keychain tram-tho-token", "tho.yaml", "config.toml", "+[mcp_servers.tram-nho]",
              "launchctl bootstrap", "/api/tho/dang-ky", "Beads", "S6", "tag:tram-tho"):
        assert y in van_ban, y


def test_khong_nho_thi_khong_cham_cau_hinh_cli(tmp_path):
    kh, _ = _kh(tmp_path, nho=False)
    assert kh.lenh_mcp == [] and all(p.suffix == ".plist" for p in kh.tep)


@pytest.mark.parametrize("kw, mau", [({"tags": ()}, "chưa gắn"), ({"co": ("tram", "claude", "tailscale")}, "codex"),
                                     ({"co": ("codex", "claude", "tailscale")}, "tram")])
def test_tu_choi_khi_chua_gan_tag_hoac_thieu_cli(tmp_path, kw, mau):
    with pytest.raises(ValueError, match=mau):
        _kh(tmp_path, **kw)


def test_tu_choi_url_va_khe_trung(tmp_path):
    with pytest.raises(ValueError):
        lap_ke_hoach_dk("http://may-b.tail1234.ts.net", [CODEX], thu_muc_khe=tmp_path, nho=True, dd=dau_do(tmp_path))
    with pytest.raises(ValueError):
        lap_ke_hoach_dk(URL, [CODEX, CODEX], thu_muc_khe=tmp_path, nho=True, dd=dau_do(tmp_path))


def test_chua_dang_nhap_chi_canh_bao_va_tho_yaml_hop_le(tmp_path):
    kh, _ = _kh(tmp_path, dang_nhap=1)
    assert any("codex-1" in c and "đăng nhập" in c for c in kh.canh_bao)
    from tram.tho.cau_hinh import nap_cau_hinh_tho
    p = tmp_path / "tho.yaml"
    p.write_text(noi_dung_tho_yaml("C", kh.tram_chu, kh.khe), encoding="utf-8")
    ch = nap_cau_hinh_tho(p)
    assert ch.may_id == "C" and [ch.khe_id(k) for k in ch.khe] == ["C/codex-1", "C/claude-3"]
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_ke_hoach_dk.py -q`
Expected: FAIL — `1 error` (`ModuleNotFoundError: No module named 'tram.tho.ke_hoach_dk'`)

- [ ] **Step 3: Viết mã**

`tram/tho/khai_khe.py` (mới):

```python
"""Khai khe cho `tram tho dang-ky --khe <ten>:<cli>:<vai,…>:<tên gợi nhớ>` (spec 3 §9.1, §9.2) và nội dung
`~/.tram/tho.yaml` sinh ra — cùng luật với `nap_cau_hinh_tho` (3a-1). `principal` để trống: chốt sau spike S6."""
from dataclasses import dataclass

import yaml

from tram.tho.cau_hinh import CLI, TEN_KHE_RE, VAI


@dataclass(frozen=True)
class KheKhai:
    ten: str
    cli: str
    vai_uu_tien: tuple[str, ...]
    ten_goi_nho: str


def doc_khe(chuoi: str) -> KheKhai:
    phan = chuoi.split(":", 3)
    if len(phan) != 4:
        raise ValueError(f"--khe {chuoi!r}: dạng <ten>:<cli>:<vai,…>:<tên gợi nhớ>")
    ten, cli, vai, goi_nho = phan[0], phan[1], tuple(v for v in phan[2].split(",") if v), phan[3].strip()
    if not TEN_KHE_RE.fullmatch(ten):
        raise ValueError(f"--khe: tên khe {ten!r} chỉ gồm chữ thường, số, '-'")
    if cli not in CLI:
        raise ValueError(f"--khe {ten}: cli {cli!r} không hỗ trợ — chỉ {CLI}")
    if not vai or not set(vai) <= set(VAI):
        raise ValueError(f"--khe {ten}: vai ưu tiên là danh sách con của {VAI}")
    if not goi_nho or len(goi_nho) > 64 or "@" in goi_nho:
        raise ValueError(f"--khe {ten}: tên gợi nhớ bắt buộc, ≤ 64 ký tự, không phải email")
    return KheKhai(ten, cli, vai, goi_nho)


def noi_dung_tho_yaml(may_id: str, tram_api: str, khe: list[dict], *, nho_url: str | None = None) -> str:
    """`khe`: các dict `{ten, cli, thu_muc_cau_hinh, ten_goi_nho, vai_uu_tien}` của kế hoạch. Không chứa bí mật."""
    du_lieu = {"may_id": may_id, "tram_api": tram_api, "khe": [
        {"ten": k["ten"], "cli": k["cli"], "thu_muc_cau_hinh": k["thu_muc_cau_hinh"], "ten_goi_nho": k["ten_goi_nho"],
         "vai_uu_tien": list(k["vai_uu_tien"])} for k in khe]}
    du_lieu["chay"] = {"nho_url": nho_url}
    return ("# Sinh bởi `tram tho dang-ky` (spec 3 §9.1). principal: chốt sau spike S6.\n"
            + yaml.safe_dump(du_lieu, allow_unicode=True, sort_keys=False))
```

`tram/tho/ke_hoach_dk.py` (mới):

```python
"""Kế hoạch `tram tho dang-ky` (spec 3 §9.2, Q15; kiến trúc §7 "Mac thợ"): DÒ máy (chỉ đọc) rồi LIỆT KÊ mọi thay đổi
— chưa ghi gì. Ghi thật ở `thuc_hien_dk` sau khi Đại ca gõ `dong-y`. Từ chối khi máy chưa gắn tag Tailscale (#3),
thiếu `tram` hoặc CLI của một khe. KHÔNG trỏ Beads về trạm chủ (máy thợ không có quyền ghi Beads — kiến trúc §7)."""
import difflib
import os
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from tram.tho.do_may import KetQuaDo, TAG_THO, do_cli, kiem_tag
from tram.tho.khai_khe import KheKhai, noi_dung_tho_yaml
from tram.tho.launchd_tho import NHAN_THO, lenh_nap_launchd, tao_plist_tho
from tram.tho.mcp_tho import ghep_codex_toml, lenh_claude_mcp, url_nho


@dataclass
class DauDoDK:
    which: object = shutil.which
    chay: object = subprocess.run
    home: Path = field(default_factory=Path.home)
    uid: int = field(default_factory=os.getuid)
    tram_home: Path = field(default_factory=lambda: Path(os.environ.get("TRAM_HOME") or Path.home() / ".tram"))
    daemon: Path = Path("/Library/LaunchDaemons/vn.tram.tho.plist")


@dataclass
class KeHoachDangKy:
    tram_chu: str
    khe: list[dict]
    do: list[KetQuaDo]
    tep: dict[Path, bytes]
    so_sanh: list[str]
    lenh_mcp: list[tuple[list[str], dict[str, str]]]
    lenh_launchd: list[list[str]]
    canh_bao: list[str]
    tho_yaml: Path
    nho_url: str | None = None
    daemon: Path = Path("/Library/LaunchDaemons/vn.tram.tho.plist")


def lap_ke_hoach_dk(tram_chu: str, khe: list[KheKhai], *, thu_muc_khe: Path, nho: bool, dd: DauDoDK) -> KeHoachDangKy:
    url = url_nho(tram_chu)[: -len("/nho/mcp")]
    if dd.daemon.exists() or (dd.tram_home / "tho.yaml").exists():
        raise ValueError("Máy đã có cấu hình/service thợ; dừng để không ghi đè principal hay chạy hai manager")
    if not khe or len({k.ten for k in khe}) != len(khe):
        raise ValueError("cần ít nhất một --khe, tên không trùng")
    co_tag, ly_do = kiem_tag(which=dd.which, chay=dd.chay)
    if not co_tag:
        raise ValueError(ly_do)
    tram = dd.which("tram")
    if not tram or not Path(tram).is_absolute():
        raise ValueError("không thấy `tram` trong PATH — cài bằng `uv tool install` trước")
    ds, do, tep, so_sanh, lenh_mcp = [], [], {}, [], []
    canh_bao = ["Tài khoản/principal thực thi của khe chưa tạo — chờ spike S6; dang-ky không tạo user macOS.",
                "Push ref tạm từ Mac thợ chờ spike S7 (credential GitHub); kho ~/tram/kho/<du-an> Đại ca clone tay."]
    for k in khe:
        thu_muc = thu_muc_khe.expanduser() / k.ten
        d = do_cli(k.cli, thu_muc, which=dd.which, chay=dd.chay)
        if d.duong_dan is None:
            raise ValueError(f"khe {k.ten}: {d.chi_tiet}")
        if d.dang_nhap is not True:
            canh_bao.append(f"khe {k.ten}: {d.chi_tiet}")
        if not thu_muc.exists():
            canh_bao.append(f"khe {k.ten}: chưa có {thu_muc} — Đại ca đăng nhập CLI vào đúng thư mục này")
        do.append(d)
        ds.append({"ten": k.ten, "cli": k.cli, "thu_muc_cau_hinh": str(thu_muc), "ten_goi_nho": k.ten_goi_nho,
                   "vai_uu_tien": list(k.vai_uu_tien)})
        if nho and k.cli == "codex":
            p = thu_muc / "config.toml"
            cu = p.read_text(encoding="utf-8") if p.exists() else ""
            moi = ghep_codex_toml(cu, url + "/nho/mcp")
            tep[p] = moi.encode()
            so_sanh += difflib.unified_diff(cu.splitlines(keepends=True), moi.splitlines(keepends=True), str(p), str(p))
        elif nho:
            lenh_mcp += lenh_claude_mcp(d.duong_dan, thu_muc)
    if nho:
        canh_bao.append("Memory MCP: cấu hình CLI chưa kiểm bằng chạy thật (spike N2, S5); --khong-nho để bỏ qua.")
    plist = dd.home / "Library/LaunchAgents" / f"{NHAN_THO}.plist"
    log = dd.tram_home / "log"
    tep[plist] = tao_plist_tho(tram=tram, log=log / "tho.log", home=dd.home)
    return KeHoachDangKy(url, ds, do, tep, so_sanh, lenh_mcp, [["mkdir", "-p", str(log)], *lenh_nap_launchd(
        plist, uid=dd.uid)], canh_bao, dd.tram_home / "tho.yaml", url + "/nho/mcp" if nho else None, dd.daemon)


def in_ke_hoach_dk(kh: KeHoachDangKy) -> str:
    d = [f"Đăng ký máy thợ với trạm chủ {kh.tram_chu}", "Dò (chỉ đọc):", f"  - tailscale: máy gắn {TAG_THO}"]
    d += [f"  - khe {k['ten']} ({x.cli} {x.phien_ban}, {x.duong_dan}): {x.chi_tiet}" for k, x in zip(kh.khe, kh.do)]
    d += ["Sẽ làm, theo thứ tự:", f"  1. Đổi mã ghép (dùng một lần) lấy token máy: POST {kh.tram_chu}/api/ghep-may",
          "  2. Ghi token máy vào Keychain tram-tho-token của tài khoản đang chạy (không in, không ghi file)",
          f"  3. Ghi {kh.tho_yaml} (bản cũ, nếu có, giữ ở tho.yaml.bak):"]
    d += ["       " + x for x in noi_dung_tho_yaml("<theo mã ghép>", kh.tram_chu, kh.khe).splitlines()]
    d += ["  4. Ghi file:"] + [f"       - {p}" for p in kh.tep]
    d += ["  5. Cấu hình memory MCP cho Claude:"] + [
        f"       - {' '.join(f'{x}={y}' for x, y in e.items())} {' '.join(a)}" for a, e in kh.lenh_mcp]
    d += [f"  6. Gửi đăng ký khe: POST {kh.tram_chu}/api/tho/dang-ky ({', '.join(k['ten'] for k in kh.khe)})",
          "  7. Chỉ ghi plist; CHƯA nạp. Sau khai principal/chay.day và đạt S2/S6/S7, mới dùng lệnh kích hoạt:"] + [f"       - {' '.join(c)}" for c in kh.lenh_launchd]
    d += ["Thay đổi config.toml của khe Codex:"] + ["    " + x.rstrip("\n") for x in kh.so_sanh or ["(không có)"]]
    d += ["Không làm: không trỏ Beads về trạm chủ (máy thợ không có quyền ghi Beads); không tạo tài khoản macOS (S6); "
          "không đổi cài đặt Tailscale.", "Cảnh báo:"] + [f"  - {c}" for c in kh.canh_bao]
    d += ["Lúc chạy, máy này chỉ gọi trạm chủ qua tailnet; CLI của khe tự gọi API nhà cung cấp của nó."]
    return "\n".join(d)
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_ke_hoach_dk.py -q`
Expected: `14 passed`

Run: `uv run pytest -q`
Expected: `N₀+45 passed` (trên `main` sau đợt 1 + riêng task này)

- [ ] **Step 5: Commit**

```bash
git add tram/tho/khai_khe.py tram/tho/ke_hoach_dk.py tests/tho_dk_gia.py tests/test_ke_hoach_dk.py
git commit -m "feat(tho): kế hoạch tram tho dang-ky — dò chỉ đọc, từ chối máy chưa gắn tag, liệt kê mọi thay đổi (spec 3 §9.2, Q15)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 11: Thực hiện `tram tho dang-ky` sau `dong-y` + lệnh CLI

**Độ khó:** `kho` · **Đợt:** 3 · **Song song với:** Task 12, 13 · **Phải xong trước:** Task 10 (và Task 9 đã sửa `tram/tho/lenh.py` ở đợt 2)

**Files:**
- Create: `tram/tho/thuc_hien_dk.py`
- Create: `tram/tho/lenh_dang_ky.py`
- Modify: `tram/tho/lenh.py` (dòng neo: dòng `tho.add_parser("kiem", …).set_defaults(ham=_kiem)` trong `them_lenh_tho`)
- Test: `tests/test_thuc_hien_dk.py` (mới)

**Interfaces:**
- Consumes: `KeHoachDangKy`, `lap_ke_hoach_dk`, `in_ke_hoach_dk`, `DauDoDK`, `doc_khe`, `noi_dung_tho_yaml` (Task 10); `ghi_token_may` (Task 6); `nap_cau_hinh_tho`; `KhachTram`, `LoiKhachTram` (3a-1). Test: `dau_do`, `URL` (Task 10), `main`.
- Produces: `tram/tho/thuc_hien_dk.py`: `HieuUng(ghep, ghi_token, dang_ky, chay)`, `ghep_that(tram_chu, ma, *, mo) -> (may_id, token)`, `dang_ky_that(tram_chu, may_id, token, khe, *, mo)`, `hieu_ung_that() -> HieuUng`, `thuc_hien_dk(kh, ma, hu) -> str` (may_id). `tram/tho/lenh_dang_ky.py`: `them_lenh_dang_ky(tho)` → `tram tho dang-ky --tram-chu URL --khe … [--thu-muc-khe] [--khong-nho] [--dong-y]` (mã 0 xong; 1 không gõ `dong-y`; 2 từ chối/dừng giữa chừng).

- [ ] **Step 1: Viết test thất bại**

`tests/test_thuc_hien_dk.py` (mới):

```python
import io
import json
import urllib.error
from pathlib import Path

import pytest

from tho_dk_gia import URL, dau_do
from tram.cli import main
from tram.tho.cau_hinh import nap_cau_hinh_tho
from tram.tho.khach import LoiKhachTram
from tram.tho.ke_hoach_dk import lap_ke_hoach_dk
from tram.tho.khai_khe import doc_khe
from tram.tho.thuc_hien_dk import HieuUng, dang_ky_that, ghep_that, thuc_hien_dk

TOKEN = "tok_" + "z" * 40
KHE = ["codex-1:codex:coder,qc:Codex 1", "claude-3:claude:spec:Claude 3"]


def _hu(nhat_ky, *, ghep_loi=False):
    def ghep(url, ma):
        if ghep_loi:
            raise LoiKhachTram("trạm từ chối mã ghép (403)")
        nhat_ky.append(("ghep", url, ma))
        return "C", TOKEN
    return HieuUng(ghep=ghep, ghi_token=lambda m, t: nhat_ky.append(("token", m)),
                   dang_ky=lambda url, m, t, khe: nhat_ky.append(("dang_ky", m, t == TOKEN, [k["ten"] for k in khe])),
                   chay=lambda argv, **kw: nhat_ky.append(("chay", argv[:3], kw.get("check"),
                                                           (kw.get("env") or {}).get("CLAUDE_CONFIG_DIR"))))


def _kh(tmp_path):
    return lap_ke_hoach_dk(URL, [doc_khe(k) for k in KHE], thu_muc_khe=tmp_path / "khe", nho=True,
                           dd=dau_do(tmp_path))


def test_thu_tu_ghep_token_yaml_tep_mcp_dang_ky_launchd(tmp_path):
    kh, nk = _kh(tmp_path), []
    assert thuc_hien_dk(kh, "ABCD-EFGH-JKMN", _hu(nk)) == "C"
    assert [x[0] for x in nk] == ["ghep", "token", "chay", "chay", "dang_ky"]
    assert nk[0] == ("ghep", URL, "ABCD-EFGH-JKMN") and nk[4] == ("dang_ky", "C", True, ["codex-1", "claude-3"])
    assert nk[2][1:] == (["/opt/bin/claude", "mcp", "remove"], False, str(tmp_path / "khe/claude-3"))
    assert nk[3][1:] == (["/opt/bin/claude", "mcp", "add-json"], True, str(tmp_path / "khe/claude-3"))
    assert not any(x[0] == "chay" and x[1][0] == "launchctl" for x in nk)
    ch = nap_cau_hinh_tho(kh.tho_yaml)
    assert ch.chay.nho_url == URL + "/nho/mcp"
    assert ch.may_id == "C" and ch.tram_api == URL and not (kh.tho_yaml.parent / "tho.yaml.bak").exists()
    toml = tmp_path / "khe/codex-1/config.toml"
    assert "tram-nho" in toml.read_text() and toml.stat().st_mode & 0o777 == 0o600
    assert (tmp_path / "home/Library/LaunchAgents/vn.tram.tho.plist").exists()
    assert not any(TOKEN in p.read_text(errors="ignore") for p in tmp_path.rglob("*") if p.is_file())
    before = list(nk)
    with pytest.raises(ValueError, match="service"):
        thuc_hien_dk(kh, "MA-MOI", _hu(nk))
    assert nk == before


def test_ghep_loi_thi_khong_ghi_gi(tmp_path):
    kh, nk = _kh(tmp_path), []
    with pytest.raises(LoiKhachTram):
        thuc_hien_dk(kh, "x", _hu(nk, ghep_loi=True))
    assert nk == [] and not kh.tho_yaml.exists() and not any(p.exists() for p in kh.tep)


class _Ph(io.BytesIO):
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def test_ghep_va_dang_ky_qua_http():
    goi = []

    def mo(yc, timeout):
        goi.append((yc.full_url, yc.get_header("Authorization"), json.loads(yc.data)))
        if yc.data and b"SAI" in yc.data:
            raise urllib.error.HTTPError(yc.full_url, 403, "x", {}, io.BytesIO(b'{"loi": "M\xc3\xa3 sai"}'))
        return _Ph(json.dumps({"may_id": "C", "token": TOKEN, "khe_id": ["C/codex-1"]}).encode())

    assert ghep_that(URL, "ABCD", mo=mo) == ("C", TOKEN)
    assert goi[0] == (URL + "/api/ghep-may", None, {"ma": "ABCD"})
    with pytest.raises(LoiKhachTram, match="403"):
        ghep_that(URL, "SAI", mo=mo)
    dang_ky_that(URL, "C", TOKEN, [{"ten": "codex-1", "cli": "codex", "thu_muc_cau_hinh": "/x", "ten_goi_nho": "C1",
                                     "vai_uu_tien": ["qc"]}], mo=mo)
    assert goi[2] == (URL + "/api/tho/dang-ky", f"Bearer {TOKEN}", {"may_id": "C", "khe": [
        {"ten": "codex-1", "cli": "codex", "ten_goi_nho": "C1", "vai_uu_tien": ["qc"]}]})


def test_cli_liet_ke_roi_cho_dong_y(tmp_path, monkeypatch, capsys):
    import tram.tho.ke_hoach_dk as khdk
    import tram.tho.thuc_hien_dk as thdk
    nk = []
    monkeypatch.setattr("getpass.getpass", lambda *_: "ABCD-EFGH-JKMN")
    monkeypatch.setattr(khdk, "DauDoDK", lambda: dau_do(tmp_path))
    monkeypatch.setattr(thdk, "hieu_ung_that", lambda: _hu(nk))
    lenh = ["tho", "dang-ky", "--tram-chu", URL, "--thu-muc-khe", str(tmp_path / "khe"),
            *[x for k in KHE for x in ("--khe", k)]]
    monkeypatch.setattr("builtins.input", lambda *_: "không")
    assert main(lenh) == 1 and nk == [] and "Sẽ làm" in capsys.readouterr().out
    assert main([*lenh, "--dong-y"]) == 0 and nk[0][0] == "ghep" and "Đã đăng ký máy C" in capsys.readouterr().out
    assert main([*lenh[:-4], "--khe", "x:gemini:qc:X", "--dong-y"]) == 2
    monkeypatch.setattr(khdk, "DauDoDK", lambda: dau_do(tmp_path / "may-moi", tags=()))
    assert main([*lenh, "--dong-y"]) == 2 and "chưa gắn" in capsys.readouterr().err
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_thuc_hien_dk.py -q`
Expected: FAIL — `1 error` (`ModuleNotFoundError: No module named 'tram.tho.thuc_hien_dk'`)

- [ ] **Step 3: Viết mã**

`tram/tho/thuc_hien_dk.py` (mới):

```python
"""Thực hiện kế hoạch `tram tho dang-ky` (spec 3 §9.2) — CHỈ gọi sau khi Đại ca gõ `dong-y`.

Thứ tự: đổi mã ghép (dùng một lần) → Keychain → `tho.yaml` → file (config.toml của khe Codex, plist) → lệnh MCP của
Claude → đăng ký khe với trạm → nạp launchd (cuối cùng). Lỗi giữa chừng thì dừng; chạy lại cần mã ghép MỚI, và nếu
máy đã nhận token thì `tram chu go-may <máy>` ở trạm trước. Token chỉ nằm trong bộ nhớ và Keychain."""
import os
import shutil
import subprocess
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from tram.tho.cau_hinh import nap_cau_hinh_tho
from tram.tho.ke_hoach_dk import KeHoachDangKy
from tram.tho.khach import KhachTram, LoiKhachTram
from tram.tho.khai_khe import noi_dung_tho_yaml
from tram.tho.token_may import ghi_token_may


@dataclass
class HieuUng:
    ghep: Callable[[str, str], tuple[str, str]]               # (tram_chu, ma) -> (may_id, token)
    ghi_token: Callable[[str, str], None]                     # (may_id, token)
    dang_ky: Callable[[str, str, str, list[dict]], None]      # (tram_chu, may_id, token, khe)
    chay: Callable = subprocess.run


def ghep_that(tram_chu: str, ma: str, *, mo=urllib.request.urlopen) -> tuple[str, str]:
    ma_http, kq = KhachTram(tram_chu, "", mo=mo).goi("POST", "/api/ghep-may", {"ma": ma}, xac_thuc=False)
    if ma_http != 200:
        raise LoiKhachTram(f"trạm từ chối mã ghép ({ma_http}): {str(kq.get('loi', ''))[:120]}")
    return str(kq.get("may_id", "")), str(kq.get("token", ""))


def dang_ky_that(tram_chu: str, may_id: str, token: str, khe: list[dict], *, mo=urllib.request.urlopen) -> None:
    than = {"may_id": may_id, "khe": [{k: x[k] for k in ("ten", "cli", "ten_goi_nho", "vai_uu_tien")} for x in khe]}
    ma_http, kq = KhachTram(tram_chu, token, mo=mo).goi("POST", "/api/tho/dang-ky", than)
    if ma_http != 200:
        raise LoiKhachTram(f"trạm từ chối đăng ký khe ({ma_http}): {str(kq.get('loi', ''))[:120]}")


def hieu_ung_that() -> HieuUng:
    return HieuUng(ghep=ghep_that, ghi_token=ghi_token_may, dang_ky=dang_ky_that)


def _ghi(p: Path, noi_dung: bytes) -> None:
    p.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    tam = p.with_name(p.name + ".moi")
    tam.write_bytes(noi_dung)
    tam.chmod(0o644 if p.suffix == ".plist" else 0o600)
    os.replace(tam, p)


def thuc_hien_dk(kh: KeHoachDangKy, ma: str, hu: HieuUng) -> str:
    if kh.daemon.exists() or kh.tho_yaml.exists():
        raise ValueError("Máy đã có cấu hình/service thợ; chưa đổi mã ghép")
    may_id, token = hu.ghep(kh.tram_chu, ma)
    hu.ghi_token(may_id, token)
    tam = kh.tho_yaml.with_name("tho.yaml.moi")
    tam.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    tam.write_text(noi_dung_tho_yaml(may_id, kh.tram_chu, kh.khe, nho_url=kh.nho_url), encoding="utf-8")
    nap_cau_hinh_tho(tam)                                   # đúng luật đọc của `tram tho chay` trước khi thay
    if kh.tho_yaml.exists():
        shutil.copy2(kh.tho_yaml, kh.tho_yaml.with_name("tho.yaml.bak"))
    os.replace(tam, kh.tho_yaml)
    for p, noi_dung in kh.tep.items():
        _ghi(p, noi_dung)
    for argv, env in kh.lenh_mcp:
        hu.chay(argv, env={**os.environ, **env}, check=argv[2] != "remove", capture_output=True, text=True)
    hu.dang_ky(kh.tram_chu, may_id, token, kh.khe)
    # Chỉ staging: tho.yaml mới chưa có principal/chay.day và các cổng S2/S6/S7 chưa được duyệt.
    # Không bootstrap service lặp exit 2; lệnh kh.lenh_launchd được giữ để kích hoạt sau kiểm.
    return may_id
```

`tram/tho/lenh_dang_ky.py` (mới):

```python
"""Lệnh `tram tho dang-ky` (spec 3 §9.2; kiến trúc §7 "Mac thợ") — chạy ở TÀI KHOẢN QUẢN LÝ THỢ của Mac thợ từ xa:
dò, in danh sách thay đổi, chờ gõ `dong-y` (Q15), rồi mới làm."""
import subprocess
import sys
from pathlib import Path


def _dang_ky(args) -> int:
    from tram.tho import ke_hoach_dk, thuc_hien_dk
    from tram.tho.khach import LoiKhachTram
    from tram.tho.khai_khe import doc_khe
    try:
        khe = [doc_khe(s) for s in args.khe]
        kh = ke_hoach_dk.lap_ke_hoach_dk(args.tram_chu, khe, thu_muc_khe=Path(args.thu_muc_khe),
                                         nho=not args.khong_nho, dd=ke_hoach_dk.DauDoDK())
    except ValueError as e:
        print(f"Không đăng ký: {e}", file=sys.stderr)
        return 2
    print(ke_hoach_dk.in_ke_hoach_dk(kh))
    if not args.dong_y and input("Gõ dong-y để thực hiện: ").strip() != "dong-y":
        print("Không làm gì.")
        return 1
    try:
        import getpass
        ma = getpass.getpass("Mã ghép (ẩn): ").strip()
        may_id = thuc_hien_dk.thuc_hien_dk(kh, ma, thuc_hien_dk.hieu_ung_that())
    except (LoiKhachTram, ValueError, RuntimeError, OSError, subprocess.CalledProcessError) as e:
        print(f"Dừng giữa chừng: {e}. Xin mã ghép mới (`tram chu cap-ma`; nếu máy đã nhận token thì "
              "`tram chu go-may <máy>` trước) rồi chạy lại.", file=sys.stderr)
        return 2
    print(f"Đã đăng ký máy {may_id}. Kiểm: tram tho kiem")
    return 0


def them_lenh_dang_ky(tho) -> None:
    d = tho.add_parser("dang-ky", help="Ghép Mac thợ từ xa với trạm chủ (liệt kê thay đổi, chờ dong-y)")
    d.add_argument("--tram-chu", required=True, help="https://<máy B>.<tailnet>.ts.net")
    d.add_argument("--khe", action="append", required=True, help="<ten>:<cli>:<vai,…>:<tên gợi nhớ> — lặp được")
    d.add_argument("--thu-muc-khe", default="~/tram/khe", help="Thư mục cha của CLAUDE_CONFIG_DIR/CODEX_HOME các khe")
    d.add_argument("--khong-nho", action="store_true", help="Không ghi cấu hình memory MCP")
    d.add_argument("--dong-y", action="store_true", help="Bỏ bước hỏi")
    d.set_defaults(ham=_dang_ky)
```

`tram/tho/lenh.py` (sửa — bản vá trên nền sau Task 9; dòng neo là dòng `kiem` — nếu 3a-2 đã thêm dòng ngay sau mốc thì chèn tay hai dòng `+` ngay sau dòng neo, G20):

```diff
diff --git a/tram/tho/lenh.py b/tram/tho/lenh.py
index d49ec44..d2e0694 100644
--- a/tram/tho/lenh.py
+++ b/tram/tho/lenh.py
@@ -55,6 +55,8 @@ def _go_may(args) -> int:
 def them_lenh_tho(sub, chu) -> None:
     tho = sub.add_parser("tho", help="Máy thợ (phần 3)").add_subparsers(dest="lenh_tho", required=True)
     tho.add_parser("kiem", help="Kiểm máy thợ: xanh/vàng/đỏ, mã ≠ 0 nếu có đỏ").set_defaults(ham=_kiem)
+    from tram.tho.lenh_dang_ky import them_lenh_dang_ky
+    them_lenh_dang_ky(tho)
     for ten, mo_ta in (("tat-khe", "Tắt khe (phiếu đang chạy dừng mềm)"), ("bat-khe", "Bật lại khe")):
         x = tho.add_parser(ten, help=mo_ta)
         x.add_argument("khe", help="khe_id, vd B/claude-1")
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_thuc_hien_dk.py tests/test_tho_lenh.py tests/test_ghep_may.py -q`
Expected: `4 passed` cho file mới; mọi test của hai file kia vẫn pass

Run: `uv run pytest -q`
Expected: `N₀+61 passed` (trên `main` sau đợt 2 + riêng task này)

- [ ] **Step 5: Commit**

```bash
git add tram/tho/thuc_hien_dk.py tram/tho/lenh_dang_ky.py tram/tho/lenh.py tests/test_thuc_hien_dk.py
git commit -m "feat(tho): tram tho dang-ky — in kế hoạch, chờ dong-y, ghép → Keychain → tho.yaml → MCP → đăng ký khe → launchd (spec 3 §9.2)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 12: `tram tho kiem` cho máy từ xa — khe Codex và tag Tailscale

**Độ khó:** `de` · **Đợt:** 3 · **Song song với:** Task 11, 13 · **Phải xong trước:** Task 4, Task 7

**Files:**
- Create: `tram/tho/kiem_3b.py`
- Modify: `tram/tho/kiem_may.py` (dòng neo: `return ra` cuối `kiem_may`, ngay sau mục "dung lượng")
- Test: `tests/test_kiem_3b.py` (mới)

**Interfaces:**
- Consumes: `doc_han_muc_ranh` (Task 7); `do_cli`, `kiem_tag`, `TAG_THO` (Task 4); `CauHinhTho`, `KheCauHinh`; `DauDo`, `MucKiem`, `kiem_may`, `in_ket_qua` (3a-1).
- Produces: `tram/tho/kiem_3b.py`: `bo_sung_3b(ch, dd, ra, *, doc_han_muc=doc_han_muc_ranh, bay_gio=None) -> list[MucKiem]` (G17). `kiem_may` trả `bo_sung_3b(ch, dd, ra)`.

- [ ] **Step 1: Viết test thất bại**

`tests/test_kiem_3b.py` (mới):

```python
import json
import subprocess
from datetime import datetime, timezone

from tram.han_muc.mo_hinh import CuaSo, HanMuc
from tram.tho.cau_hinh import CauHinhTho, KheCauHinh
from tram.tho.do_may import TAG_THO
from tram.tho.kiem_3b import bo_sung_3b
from tram.tho.kiem_may import DauDo, MucKiem, in_ket_qua, kiem_may

LUC = datetime(2026, 10, 13, 3, 0, tzinfo=timezone.utc)


def _ch(tmp_path, api="https://may-b.tail1234.ts.net"):
    return CauHinhTho("C", api, (
        KheCauHinh("codex-1", "codex", None, tmp_path / "codex-1", "Codex 1", ("coder",)),
        KheCauHinh("claude-3", "claude", None, tmp_path / "claude-3", "Claude 3", ("qc",))))


def _dd(tmp_path, *, dang_nhap=0, tags=(TAG_THO,), goc="/opt/bin"):
    def chay(argv, **kw):
        if argv[1:] == ["login", "status"]:
            assert kw["env"]["CODEX_HOME"] == str(tmp_path / "codex-1")
            return subprocess.CompletedProcess(argv, dang_nhap, "", "")
        if argv[1:] == ["status", "--json"]:
            return subprocess.CompletedProcess(argv, 0, json.dumps({"Self": {"Tags": list(tags)}}), "")
        return subprocess.CompletedProcess(argv, 0, "x 1.0\n" if "--version" in argv else "", "")
    return DauDo(ping=lambda: {"may_id": "C", "khe": []}, du_an=lambda: [], which=lambda c: f"{goc}/{c}",
                 chay=chay, con_trong=lambda p: 50 * 1024 ** 3, thu_muc_kho=tmp_path / "kho")


def _hm(kid, thu_muc, *, bay_gio, codex):
    return HanMuc(khe_id=kid, nguon="app-server", cua_so=[
        CuaSo(loai="5h", trang_thai="biet", phan_tram=62.0, doc_luc="2026-10-13T03:00:00Z")])


def _muc(ds):
    return {m.muc: (m.muc_do, m.chi_tiet) for m in ds}


def test_khe_codex_thay_muc_dang_nhap_them_han_muc_va_tag(tmp_path):
    goc = [MucKiem("C/codex-1 đăng nhập", "do", "chờ S2"), MucKiem("C/claude-3 đăng nhập", "do", "chờ S2")]
    ds = bo_sung_3b(_ch(tmp_path), _dd(tmp_path), goc, doc_han_muc=_hm, bay_gio=LUC)
    m = _muc(ds)
    assert m["C/codex-1 đăng nhập"][0] == "xanh" and m["C/claude-3 đăng nhập"] == ("do", "chờ S2")
    assert [x.muc for x in ds].count("C/codex-1 đăng nhập") == 1
    assert m["C/codex-1 hạn mức"] == ("xanh", "5h 62%") and m["tailscale tag"][0] == "xanh"
    assert "C/claude-3 hạn mức" not in m


def test_chua_dang_nhap_chua_doc_han_muc_chua_gan_tag(tmp_path):
    ds = bo_sung_3b(_ch(tmp_path), _dd(tmp_path, dang_nhap=1, tags=()), [],
                    doc_han_muc=lambda *a, **k: None, bay_gio=LUC)
    m = _muc(ds)
    assert m["C/codex-1 đăng nhập"][0] == "do" and m["C/codex-1 hạn mức"][0] == "vang"
    assert m["tailscale tag"][0] == "do" and in_ket_qua(ds)[1] == 1
    assert "tailscale tag" not in _muc(bo_sung_3b(_ch(tmp_path, "http://127.0.0.1:7700"), _dd(tmp_path), [],
                                                  doc_han_muc=_hm, bay_gio=LUC))


def test_kiem_may_goi_bo_sung_3b(tmp_path):
    m = _muc(kiem_may(_ch(tmp_path), _dd(tmp_path, goc=str(tmp_path / "khong-co"))))
    assert m["C/codex-1 đăng nhập"][0] == "xanh" and m["tailscale tag"][0] == "xanh"
    assert m["C/codex-1 hạn mức"][0] == "vang"                      # không có `codex` thật → không đọc được
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_kiem_3b.py -q`
Expected: FAIL — `1 error` (`ModuleNotFoundError: No module named 'tram.tho.kiem_3b'`)

- [ ] **Step 3: Viết mã**

`tram/tho/kiem_3b.py` (mới):

```python
"""Mục `tram tho kiem` của lát 3b (spec 3 §9.2, §9.3, H7) — nối vào cuối `kiem_may` (3a-1):

- Khe Codex: đăng nhập qua `codex login status` với `CODEX_HOME` của khe (thay mục "chờ S2" chung); hạn mức đọc một lần
  qua `codex app-server` — không đọc được thì VÀNG (#15: vẫn nhận việc, cảnh báo), không đỏ.
- Máy từ xa (`tram_api` là https): Mac thợ phải gắn tag Tailscale (#3) — chỉ kiểm, không đổi.
Mục cách ly, quyền ghi worktree của principal giữ nguyên như 3a-1/3a-2 (S6)."""
from datetime import datetime, timezone

from tram.chay_cli.codex.app_server import doc_han_muc_ranh
from tram.tho.cau_hinh import CauHinhTho
from tram.tho.do_may import do_cli, kiem_tag
from tram.tho.kiem_may import DauDo, MucKiem


def bo_sung_3b(ch: CauHinhTho, dd: DauDo, ra: list[MucKiem], *, doc_han_muc=doc_han_muc_ranh,
               bay_gio: datetime | None = None) -> list[MucKiem]:
    ra = list(ra)
    for k in (k for k in ch.khe if k.cli == "codex"):
        kid = ch.khe_id(k)
        d = do_cli("codex", k.thu_muc_cau_hinh, which=dd.which, chay=dd.chay)
        muc = MucKiem(f"{kid} đăng nhập", "xanh" if d.dang_nhap else "do", d.chi_tiet)
        ra = [muc if m.muc == muc.muc else m for m in ra] if any(m.muc == muc.muc for m in ra) else [*ra, muc]
        hm = doc_han_muc(kid, k.thu_muc_cau_hinh, bay_gio=bay_gio or datetime.now(timezone.utc),
                         codex=d.duong_dan or "codex")
        ra.append(MucKiem(f"{kid} hạn mức", "xanh", ", ".join(f"{c.loai} {c.phan_tram:g}%" for c in hm.cua_so))
                  if hm else MucKiem(f"{kid} hạn mức", "vang", "chưa đọc được qua `codex app-server` (chờ spike S5) "
                                     "— vẫn nhận việc, cảnh báo vàng (#15)"))
    if ch.tram_api.startswith("https://"):
        co, chi_tiet = kiem_tag(which=dd.which, chay=dd.chay)
        ra.append(MucKiem("tailscale tag", "xanh" if co else "do", chi_tiet))
    return ra
```

`tram/tho/kiem_may.py` (sửa — bản vá; nếu 3a-2 đã thêm mục sau "dung lượng" thì thay đúng dòng `return ra` cuối `kiem_may` bằng hai dòng `+`, G20):

```diff
diff --git a/tram/tho/kiem_may.py b/tram/tho/kiem_may.py
index 6dcb6c7..044a07a 100644
--- a/tram/tho/kiem_may.py
+++ b/tram/tho/kiem_may.py
@@ -79,7 +79,8 @@ def kiem_may(ch: CauHinhTho, dd: DauDo) -> list[MucKiem]:
     ra.append(MucKiem("máy ngủ", "vang" if bat_ngu else "xanh", "đang bật chế độ ngủ" if bat_ngu else "tắt"))
     trong = dd.con_trong(Path.home())
     ra.append(MucKiem("dung lượng", "vang" if trong < 10 * GB else "xanh", f"còn {trong / GB:.1f} GB"))
-    return ra
+    from tram.tho.kiem_3b import bo_sung_3b          # lát 3b: khe Codex, tag Tailscale của máy từ xa
+    return bo_sung_3b(ch, dd, ra)
 
 
 def in_ket_qua(ds: list[MucKiem]) -> tuple[str, int]:
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_kiem_3b.py tests/test_tho_lenh.py -q`
Expected: `3 passed` cho file mới; test 3a-1 (`test_kiem_may_*`) vẫn pass — khe Claude + `tram_api` cục bộ không có mục 3b nào

Run: `uv run pytest -q`
Expected: `N₀+60 passed` (trên `main` sau đợt 2 + riêng task này)

- [ ] **Step 5: Commit**

```bash
git add tram/tho/kiem_3b.py tram/tho/kiem_may.py tests/test_kiem_3b.py
git commit -m "feat(tho): tram tho kiem — đăng nhập + hạn mức khe Codex, tag Tailscale của Mac thợ từ xa (spec 3 §9.3, H7)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 13: Bộ CLI `BoCodex` và đăng ký vào `BO_CLI` của vòng thợ (3a-2)

**Độ khó:** `de` · **Đợt:** 3 · **Song song với:** Task 11, 12 · **Phải xong trước:** Task 2, 7, 8 (nền 3a-2 và 4a-2 đã ghép; Task 13 tạo registry)

**Files:**
- Create: `tram/chay_cli/codex/bo.py`
- Create: `tram/chay_cli/bo_cli.py`
- Modify: `tram/tho/ngu_canh.py`, `tram/tho/mot_lan.py`, `tram/tho/principal.py`, `tram/tho/vong_khe.py` (nền 3a-2; các file chỉ Task 13 của đợt 3 sửa)
- Test: `tests/test_bo_codex.py` (mới)

**Interfaces:**
- Consumes: `CHU_KY_RANH_GIAY`, `doc_han_muc_ranh` (Task 7); `ChayCodex` (Task 8); `NguonHanMucCodex` (Task 2); `BO_CLI`, `BoCLI` (3a-2, G3); `git`, `ghi`, `tao_repo`, `MOI_TRUONG` (`tests/git_gia.py`).
- Produces: `tram/chay_cli/codex/bo.py`: `lenh_codex(*, worktree, ghi_them, codex="codex") -> list[str]` (G15), `BoCodex(*, codex="codex", chay)` với `cli="codex"`, `bien_thu_muc="CODEX_HOME"`, `chu_ky_han_muc_ranh_giay=300`, `.lenh(*, worktree, thu_muc_phieu, vai, lenh_cho_phep)`, `.tao_chay()`, `.tao_nguon()`, `.doc_han_muc_ranh(khe_id, thu_muc_cau_hinh, *, bay_gio)`. `BO_CLI["codex"]` là một `BoCodex`.

- [ ] **Step 1: Viết test thất bại**

`tests/test_bo_codex.py` (mới):

```python
import subprocess
from datetime import datetime, timezone

import pytest

from git_gia import MOI_TRUONG, git, ghi, tao_repo
from tram.chay_cli.bo_cli import BO_CLI, BoCLI
from tram.chay_cli.codex.bo import BoCodex, lenh_codex
from tram.chay_cli.giao_dien import ChayCLI
from tram.han_muc.nguon import NguonHanMuc


def test_lenh_codex_sandbox_ghi_worktree_khong_mang_khong_hoi(tmp_path):
    argv = lenh_codex(worktree=tmp_path / "wt", ghi_them=[tmp_path / "phieu"], codex="/opt/bin/codex")
    assert argv == ["/opt/bin/codex", "exec", "--json", "--cd", str(tmp_path / "wt"), "--sandbox", "workspace-write",
                    "-c", 'approval_policy="never"', "-c", "sandbox_workspace_write.network_access=false",
                    "--add-dir", str(tmp_path / "phieu"), "-"]
    assert not any("danger" in a or "bypass" in a or "full-auto" in a for a in argv)
    for sai in ({"worktree": "wt", "ghi_them": []}, {"worktree": tmp_path, "ghi_them": ["/"]},
                {"worktree": tmp_path, "ghi_them": [tmp_path / ".." / "x"]}):
        with pytest.raises(ValueError):
            lenh_codex(**sai)


def test_bo_codex_khong_mo_git_chung(tmp_path):
    kho = tao_repo(tmp_path / "kho")
    ghi(kho, {"a.txt": "1"})
    git(kho, "worktree", "add", "-q", "-b", "tram/hr-1", str(tmp_path / "wt"))
    bo = BoCodex(codex="/opt/bin/codex", chay=lambda a, **k: subprocess.run(a, **k, env=MOI_TRUONG))
    argv = bo.lenh(worktree=tmp_path / "wt", thu_muc_phieu=tmp_path / "phieu", vai="coder", lenh_cho_phep=["x *"])
    them = [argv[i + 1] for i, a in enumerate(argv) if a == "--add-dir"]
    assert them == [str(tmp_path / "phieu")]
    assert str((kho / ".git").resolve()) not in them


def test_dang_ky_vao_bo_cli_cua_vong_tho(tmp_path, monkeypatch):
    bo = BO_CLI["codex"]
    assert isinstance(bo, BoCLI) and isinstance(bo, BoCodex) and bo.cli == "codex" and bo.bien_thu_muc == "CODEX_HOME"
    assert bo.chu_ky_han_muc_ranh_giay == 300
    assert isinstance(bo.tao_chay(), ChayCLI) and isinstance(bo.tao_nguon(), NguonHanMuc)
    khong = BoCodex(codex=str(tmp_path / "khong-co-codex"))
    assert khong.doc_han_muc_ranh("C/codex-1", tmp_path, bay_gio=datetime.now(timezone.utc)) is None
    from dataclasses import replace
    from types import SimpleNamespace
    import threading
    from tho_chay_gia import dung_may, lay_phieu
    from tram.tho.chuan_bi import chuan_bi
    from tram.tho.mot_lan import chay_mot_lan
    from tram.chay_cli.giao_dien import KetQuaChay
    from tram.tho.principal import BIEN_GIU
    from tram.tho.cau_hinh_chay import doc_cau_hinh_chay
    assert "CODEX_HOME" in BIEN_GIU
    assert doc_cau_hinh_chay({"nho_url": "https://may-b.tail.ts.net/nho/mcp"}).nho_url.endswith("/nho/mcp")
    m = dung_may(tmp_path / "worker", monkeypatch, [])
    k, so, hop, tt = lay_phieu(m)
    pc = chuan_bi(m.nc, k, so, hop, tt)
    pc.k = replace(pc.k, cli="codex")
    m.nc.tao_cli = None
    captured = {}
    def chay(argv, **kw):
        captured.update(argv=argv, **kw)
        return KetQuaChay(0, True, False, False, False, token_ra=11)
    def factory(boc, **kw):
        captured["factory"] = (boc, kw)
        return SimpleNamespace(chay=chay)
    monkeypatch.setattr(bo, "tao_chay", factory)
    result = chay_mot_lan(pc, m.nc, threading.Event())
    assert result.token_ra == 11 and captured["argv"][0] == "codex"
    assert "CODEX_HOME" in captured["env"] and "CLAUDE_CONFIG_DIR" not in captured["env"]
    assert captured["factory"][0] == pc.principal.boc
    assert captured["factory"][1]["kill"] == pc.principal.kill_nhom
    assert captured["factory"][1]["tran_token_ra"] == pc.p.ngan_sach.token_ra
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_bo_codex.py -q`
Expected: FAIL — `1 error` (`ModuleNotFoundError: No module named 'tram.chay_cli.codex.bo'`)

- [ ] **Step 3: Viết mã**

`tram/chay_cli/codex/bo.py` (mới):

```python
"""Bộ CLI của khe Codex (spec 3 §7.2, lát 3b) cho vòng `tram tho chay` (3a-2) — đăng ký `BO_CLI["codex"]`.

Lệnh (cờ theo hiểu biết hiện tại — chờ spike S5): `codex exec --json --cd <worktree> --sandbox workspace-write`,
`approval_policy="never"` (không hỏi — thao tác ngoài sandbox bị từ chối, agent phải `tram bao --can-hoi`), mạng tắt
(`sandbox_workspace_write.network_access=false`), thêm chỗ ghi: thư mục phiếu (hàng đợi `tram bao`) — chưa mở git common-dir (chờ giải pháp S6). Prompt qua stdin (`-`). KHÔNG BAO GIỜ dùng chế độ bỏ qua sandbox/quyền (Q6).
Codex không có file quyền theo vai như Claude: `vai`, `lenh_cho_phep` không vào lệnh — lớp bổ sung là prompt vai và kiểm
diff của phần 4; hàng rào thật là sandbox + principal của khe (S6)."""
import subprocess
from datetime import datetime
from pathlib import Path

from tram.chay_cli.codex.app_server import CHU_KY_RANH_GIAY, doc_han_muc_ranh
from tram.chay_cli.codex.chay import ChayCodex
from tram.chay_cli.codex.han_muc import NguonHanMucCodex
from tram.han_muc.mo_hinh import HanMuc


def _kiem(p: Path) -> Path:
    p = Path(p)
    if not p.is_absolute() or ".." in p.parts or p == Path("/") or p == Path.home():
        raise ValueError(f"đường dẫn ghi của sandbox phải tuyệt đối, cụ thể: {p}")
    return p


def lenh_codex(*, worktree: Path, ghi_them: list[Path], codex: str = "codex") -> list[str]:
    argv = [codex, "exec", "--json", "--cd", str(_kiem(worktree)), "--sandbox", "workspace-write",
            "-c", 'approval_policy="never"', "-c", "sandbox_workspace_write.network_access=false"]
    for d in ghi_them:
        argv += ["--add-dir", str(_kiem(d))]
    return [*argv, "-"]


class BoCodex:
    cli = "codex"
    bien_thu_muc = "CODEX_HOME"
    chu_ky_han_muc_ranh_giay = CHU_KY_RANH_GIAY

    def __init__(self, *, codex: str = "codex", chay=subprocess.run):
        self.codex, self.chay = codex, chay

    def lenh(self, *, worktree: Path, thu_muc_phieu: Path, vai: str, lenh_cho_phep: list[str],
             settings: Path | None = None, mcp: Path | None = None) -> list[str]:
        # S6 chưa giải quyết quyền Git: không mở cả common-dir để làm commit chạy được.
        return lenh_codex(worktree=worktree, ghi_them=[thu_muc_phieu], codex=self.codex)

    def tao_chay(self, boc=lambda a: a, **kw) -> ChayCodex:
        return ChayCodex(boc, **kw)

    def tao_nguon(self, **kw) -> NguonHanMucCodex:
        return NguonHanMucCodex()

    def doc_han_muc_ranh(self, khe_id: str, thu_muc_cau_hinh: Path, *, bay_gio: datetime) -> HanMuc | None:
        return doc_han_muc_ranh(khe_id, thu_muc_cau_hinh, bay_gio=bay_gio, codex=self.codex)
```

`tram/chay_cli/bo_cli.py` (mới, **3b tạo**):

```python
"""Registry được tạo tại 3b; 3a-2 chỉ có ChayClaude, chưa có BoCLI."""
from pathlib import Path
from typing import Protocol, runtime_checkable

from tram.chay_cli.claude import ChayClaude
from tram.chay_cli.lenh_claude import argv_claude
from tram.chay_cli.codex.bo import BoCodex
from tram.han_muc.claude import NguonHanMucClaude


@runtime_checkable
class BoCLI(Protocol):
    cli: str
    bien_thu_muc: str
    chu_ky_han_muc_ranh_giay: int | None
    def lenh(self, *, worktree: Path, thu_muc_phieu: Path, vai: str, lenh_cho_phep: list[str],
             settings: Path | None = None, mcp: Path | None = None) -> list[str]: ...
    def tao_chay(self, boc, **kw): ...
    def tao_nguon(self, **kw): ...
    def doc_han_muc_ranh(self, khe_id, thu_muc_cau_hinh, *, bay_gio): ...


class BoClaude:
    cli, bien_thu_muc, chu_ky_han_muc_ranh_giay = "claude", "CLAUDE_CONFIG_DIR", None

    def lenh(self, *, worktree, thu_muc_phieu, vai, lenh_cho_phep, settings=None, mcp=None):
        if settings is None:
            raise ValueError("Claude cần settings của phiếu")
        return argv_claude(settings=settings, mcp=mcp)

    def tao_chay(self, boc, **kw):
        return ChayClaude(boc, **kw)

    def tao_nguon(self, **kw):
        return NguonHanMucClaude(**kw)

    def doc_han_muc_ranh(self, khe_id, thu_muc_cau_hinh, *, bay_gio):
        return None


BO_CLI: dict[str, BoCLI] = {"claude": BoClaude(), "codex": BoCodex()}
```

Nối thật vào các file do 3a-2 tạo (áp sau 4a-2; không dùng module thế chỗ):

```diff
diff --git a/tram/tho/ngu_canh.py b/tram/tho/ngu_canh.py
--- a/tram/tho/ngu_canh.py
+++ b/tram/tho/ngu_canh.py
@@ -8,7 +8,7 @@
 from datetime import datetime, timezone
 from pathlib import Path
 
-from tram.chay_cli.claude import ChayClaude
+from tram.chay_cli.bo_cli import BO_CLI
 from tram.duong_dan import tram_home
 from tram.han_muc.claude import NguonHanMucClaude
 from tram.tho.cau_hinh import CauHinhTho, KheCauHinh
@@ -28,7 +28,7 @@
     goc_kho: Path = field(default_factory=lambda: Path.home() / "tram" / "kho")
     goc_wt: Path = field(default_factory=lambda: Path.home() / "tram" / "worktrees")
     principal_cua: Callable | None = None      # (khe, wt, tên hồ sơ) -> Principal; None → principal_khe.principal_cua
-    tao_cli: Callable = ChayClaude             # (boc, *, khe_id, kill, khi_bat_dau, khi_han_muc, tran_token_ra)
+    tao_cli: Callable | None = None             # (boc, *, khe_id, kill, khi_bat_dau, khi_han_muc, tran_token_ra)
     nguon: object | None = None                # NguonHanMuc; None → NguonHanMucClaude(thang=chay.thang_utilization)
     dong_ho: Callable[[], datetime] = lambda: datetime.now(timezone.utc)
     chay_lenh: Callable = subprocess.run       # lệnh hệ thống của tiến trình quản lý (chmod +a)
@@ -42,5 +42,5 @@
             return self.principal_cua(k, wt, ten)
         return principal_cua(self.ch, k, goc=self.goc, goc_wt=self.goc_wt, wt=wt, ten=ten)
 
-    def nguon_han_muc(self):
-        return self.nguon or NguonHanMucClaude(thang=self.ch.chay.thang_utilization)
+    def nguon_han_muc(self, cli="claude"):
+        return self.nguon or BO_CLI[cli].tao_nguon(thang=self.ch.chay.thang_utilization)
diff --git a/tram/tho/mot_lan.py b/tram/tho/mot_lan.py
--- a/tram/tho/mot_lan.py
+++ b/tram/tho/mot_lan.py
@@ -5,7 +5,8 @@
 from datetime import datetime, timedelta
 
 from tram.chay_cli.giao_dien import KetQuaChay, ket_thuc_tu
-from tram.chay_cli.lenh_claude import argv_claude, env_cli
+from tram.chay_cli.lenh_claude import env_cli
+from tram.chay_cli.bo_cli import BO_CLI
 from tram.duong_dan import doc_luc
 from tram.han_muc.log_claude import doc_log_claude, gop_han_muc
 from tram.han_muc.luat import cham_nguong_ngung
@@ -53,15 +54,18 @@
     so.ghi_lan_chay(nc.dong_ho())
     env = env_cli(thu_muc_cau_hinh=pc.k.thu_muc_cau_hinh, giao_id=p.giao_id, hang_doi=pc.hang_doi, wt=pc.wt,
                   path=ch.path_cli, ma_giao=p.ma_giao if ch.nho_url else None, nho_url=ch.nho_url)
-    cli = nc.tao_cli(pc.principal.boc, khe_id=p.khe_id, kill=pc.principal.kill_nhom,
+    bo = BO_CLI[pc.k.cli]
+    env[bo.bien_thu_muc] = env.pop("CLAUDE_CONFIG_DIR")
+    cli = (nc.tao_cli or bo.tao_chay)(pc.principal.boc, khe_id=p.khe_id, kill=pc.principal.kill_nhom,
                      khi_bat_dau=lambda pid: ghi_pid(so.pid, pid=pid, giao_id=p.giao_id, luot=p.luot, lan=lan),
                      khi_han_muc=so.luu_han_muc, tran_token_ra=p.ngan_sach.token_ra - tt.token_ra)
     hen = threading.Timer(max(0.0, giay_con_lai(pc, nc.dong_ho())), dung.set)
     hen.start()
     try:
-        kq = cli.chay(argv_claude(settings=pc.settings, mcp=pc.mcp, cli=pc.k.cli), cwd=pc.wt, env=env,
+        kq = cli.chay(bo.lenh(worktree=pc.wt, thu_muc_phieu=pc.thu_muc, vai=p.vai,
+                              lenh_cho_phep=p.lenh_cho_phep, settings=pc.settings, mcp=pc.mcp), cwd=pc.wt, env=env,
                       stdin=_goi(pc, lan), log=nc.goc / "log" / "chay" / f"{p.giao_id}-{p.luot}-{lan}.jsonl",
-                      dung=dung, nguon=nc.nguon_han_muc())
+                      dung=dung, nguon=nc.nguon_han_muc(pc.k.cli))
     finally:
         hen.cancel()
         so.pid.unlink(missing_ok=True)
@@ -73,8 +77,8 @@
         "token_ra": kq.token_ra, "token_cache_doc": kq.token_cache_doc, "token_cache_ghi": kq.token_cache_ghi,
         "thoi_gian_ms": kq.thoi_gian_ms, "digest_log": kq.digest_log, "reset_luc": kq.reset_luc}, lan)
     bay = nc.dong_ho()
-    if kt in ("loi", "loi_he"):              # nguồn lùi §8.1: log của CLI chỉ có rate_limit_info khi đã bị chặn
-        hm = doc_log_claude(pc.k.thu_muc_cau_hinh, khe_id=p.khe_id, bay_gio=bay, nguon=nc.nguon_han_muc())
+    if pc.k.cli == "claude" and kt in ("loi", "loi_he"):              # nguồn lùi §8.1: log của CLI chỉ có rate_limit_info khi đã bị chặn
+        hm = doc_log_claude(pc.k.thu_muc_cau_hinh, khe_id=p.khe_id, bay_gio=bay, nguon=nc.nguon_han_muc(pc.k.cli))
         if hm is not None:
             so.luu_han_muc(gop_han_muc(so.doc_han_muc(), hm))
     if kt == "het_han_muc":
diff --git a/tram/tho/principal.py b/tram/tho/principal.py
--- a/tram/tho/principal.py
+++ b/tram/tho/principal.py
@@ -13,7 +13,7 @@
 
 SUDO = "/usr/bin/sudo"
 SANDBOX_EXEC = "/usr/bin/sandbox-exec"
-BIEN_GIU = ("CLAUDE_CONFIG_DIR", "TRAM_GIAO_ID", "TRAM_HANG_DOI", "TRAM_MA_GIAO", "TRAM_NHO_URL", "PATH", "LANG",
+BIEN_GIU = ("CLAUDE_CONFIG_DIR", "CODEX_HOME", "TRAM_GIAO_ID", "TRAM_HANG_DOI", "TRAM_MA_GIAO", "TRAM_NHO_URL", "PATH", "LANG",
             "APP_ENV", "TMPDIR", "GIT_CONFIG_COUNT", "GIT_CONFIG_KEY_0", "GIT_CONFIG_VALUE_0", "GIT_CONFIG_KEY_1",
             "GIT_CONFIG_VALUE_1")
 USER_RE = re.compile(r"[a-z_][a-z0-9_-]{0,30}")
diff --git a/tram/tho/vong_khe.py b/tram/tho/vong_khe.py
--- a/tram/tho/vong_khe.py
+++ b/tram/tho/vong_khe.py
@@ -6,5 +6,6 @@
 import time
 from tram.duong_dan import doc_luc
+from tram.chay_cli.bo_cli import BO_CLI
 
 from tram.phieu.mo_hinh import Phieu
 from tram.tho.cau_hinh import KheCauHinh
@@ -32,6 +33,7 @@
         self.phieu_moi: TrangThaiPhieu | None = None
         self.da_xac_nhan = False
         self.han_giu = None
+        self.han_muc_doc_lai = 0.0
 
     def khoi_dong(self) -> None:
         try:
@@ -49,6 +51,13 @@
         self.phieu_moi = tt
 
     def nhip(self) -> dict | None:
+        bo = BO_CLI[self.k.cli]
+        if self.pc is None and self.phieu_moi is None and bo.chu_ky_han_muc_ranh_giay is not None \
+                and time.monotonic() >= self.han_muc_doc_lai:
+            self.han_muc_doc_lai = time.monotonic() + bo.chu_ky_han_muc_ranh_giay
+            hm = bo.doc_han_muc_ranh(self.khe_id, self.k.thu_muc_cau_hinh, bay_gio=self.nc.dong_ho())
+            if hm is not None:
+                self.so.luu_han_muc(hm)
         than = {"khe_id": self.khe_id, "buoc_tho": self.buoc}
         p = self.pc.p if self.pc else (Phieu.model_validate(self.phieu_moi.phieu) if self.phieu_moi else None)
         if p is not None:
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_bo_codex.py -q`
Expected: `3 passed`

Run: `uv run pytest -q`
Expected: `N₀+60 passed` (trên `main` sau đợt 2 + riêng task này)

- [ ] **Step 5: Commit**

```bash
git add tram/chay_cli/codex/bo.py tram/chay_cli/bo_cli.py tram/tho/ngu_canh.py tram/tho/mot_lan.py tram/tho/principal.py tram/tho/vong_khe.py tests/test_bo_codex.py
git commit -m "feat(codex): BoCodex — lệnh codex exec sandbox ghi worktree, không mạng, không hỏi; đăng ký BO_CLI['codex'] — chờ S5 (spec 3 §7.2)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 14: Kịch bản giả lập lát 3b qua HTTP (ghép → đăng ký → nhịp Codex → gỡ máy)

**Độ khó:** `de` · **Đợt:** 4 · **Song song với:** — · **Phải xong trước:** Task 1–13

**Files:**
- Test: `tests/test_kich_ban_3b.py` (mới — chỉ test tích hợp, ngoại lệ TDD như 3a-1 Task 25)

**Interfaces:**
- Consumes: `cap_ma_ghep` (1); `han_muc_app_server`, fixture (2); `/api/tho/dang-ky` nhận codex (3); `/api/ghep-may` (9); `lap_ke_hoach_dk`, `doc_khe`, `dau_do`, `URL` (10); `HieuUng`, `ghep_that`, `dang_ky_that`, `thuc_hien_dk` (11); `tao_tram`, `de_xuat`, `goi`, `go_may` (3a-1).
- Produces: — (H4 cho khe Codex với số đo app-server; G1, G2, G11 đầu–cuối qua app ASGI trong bộ nhớ).

- [ ] **Step 1: Viết test**

`tests/test_kich_ban_3b.py` (mới):

```python
"""Kịch bản giả lập lát 3b (spec 3 §9.2, §15 mục 2 phần 3b): trạm cấp mã → Mac thợ D dang-ky qua HTTP thật của app
(trong bộ nhớ) → khe Codex gửi nhịp có hạn mức app-server → luật nhận việc áp cho Codex → gỡ máy."""
import io
import json
import urllib.error
from contextlib import closing
from datetime import timedelta
from pathlib import Path

import pytest

from asgi_gia import goi
from phieu_gia import de_xuat
from tho_api_gia import tao_tram
from tho_dk_gia import URL, dau_do
from tram.chay_cli.codex.han_muc import han_muc_app_server
from tram.phieu.ma_ghep import cap_ma_ghep
from tram.phieu.may import go_may
from tram.tho.cau_hinh import nap_cau_hinh_tho
from tram.tho.khach import LoiKhachTram
from tram.tho.ke_hoach_dk import lap_ke_hoach_dk
from tram.tho.khai_khe import doc_khe
from tram.tho.thuc_hien_dk import HieuUng, dang_ky_that, ghep_that, thuc_hien_dk

MAU = json.loads((Path(__file__).parent / "du_lieu/codex/app_server_rate_limits.json").read_text(encoding="utf-8"))


class _Ph(io.BytesIO):
    def __init__(self, status, body):
        super().__init__(body)
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _mo(app):
    def mo(yc, timeout):
        r = goi(app, yc.get_method(), yc.full_url.removeprefix(URL), json_body=json.loads(yc.data),
                headers={k: v for k, v in yc.header_items() if k.lower() == "authorization"})
        if r.status >= 400:
            raise urllib.error.HTTPError(yc.full_url, r.status, "x", {}, io.BytesIO(r.body))
        return _Ph(r.status, r.body)
    return mo


def test_ghep_dang_ky_nhip_codex_roi_go_may(tmp_path):
    hm_hien = [MAU["prolite"]]
    t = tao_tram(tmp_path, chon=lambda khe, hm: de_xuat() if khe == "D/codex-1" else None, dang_ky=False)
    ma = cap_ma_ghep(t.kho(), "D", luc=t.gio[0]).ma
    kh = lap_ke_hoach_dk(URL, [doc_khe("codex-1:codex:coder:Codex 1")], thu_muc_khe=tmp_path / "khe", nho=True,
                         dd=dau_do(tmp_path))
    keychain, mo = {}, _mo(t.app)
    hu = HieuUng(ghep=lambda u, m: ghep_that(u, m, mo=mo), ghi_token=lambda m, tok: keychain.update({m: tok}),
                 dang_ky=lambda u, m, tok, khe: dang_ky_that(u, m, tok, khe, mo=mo), chay=lambda *a, **k: None)
    assert thuc_hien_dk(kh, ma, hu) == "D"
    ch = nap_cau_hinh_tho(kh.tho_yaml)
    assert ch.tram_api == URL and ch.khe_id(ch.khe[0]) == "D/codex-1"
    t.token["D"] = keychain["D"]
    assert [k["khe_id"] for k in t.goi("GET", "/api/tho/ping", "D").json()["khe"]] == ["D/codex-1"]
    with pytest.raises(LoiKhachTram, match="403"):
        thuc_hien_dk(kh, ma, hu)                                               # mã đã dùng

    def nhip():
        hm = han_muc_app_server(hm_hien[0], khe_id="D/codex-1", bay_gio=t.gio[0])
        return t.goi("POST", "/api/tho/nhip", "D", json_body={"khe_id": "D/codex-1", "buoc_tho": "ranh",
                                                              "han_muc": hm.model_dump()}).json()
    assert nhip() == {"tiep_tuc": True, "phieu": None}                          # tuần đã biết 91% → không nhận (H4)
    hm_hien[0] = MAU["plus"]
    t.toi(seconds=30)
    assert nhip()["phieu"]["khe_id"] == "D/codex-1"                             # 62% / 12,5% → nhận phiếu
    with closing(t.kho()) as kho:
        ghi = kho.db.execute("SELECT du_lieu FROM su_kien WHERE loai = 'khe.han_muc' ORDER BY id").fetchall()
        assert [json.loads(x[0])["nguon"] for x in ghi] == ["app-server", "app-server"]
        assert go_may(kho, "D", luc=t.gio[0] + timedelta(minutes=1)) == 1
    assert t.goi("GET", "/api/tho/ping", "D").status == 401
```

- [ ] **Step 2: Chạy, thấy pass**

Run: `uv run pytest tests/test_kich_ban_3b.py -q`
Expected: `1 passed`

Run: `uv run pytest -q`
Expected: `N₀+68 passed` (trên `main` sau đợt 3 + riêng task này)

- [ ] **Step 3: Commit**

```bash
git add tests/test_kich_ban_3b.py
git commit -m "test(3b): kịch bản ghép Mac thợ, đăng ký khe Codex, nhịp với hạn mức app-server, gỡ máy (spec 3 §9.2, §15 mục 2)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

## Sơ đồ đợt chạy

N₀ = số test trên `main` sau 3a-2 và 4a-2 (đo ở "Chuẩn bị"). Ngoặc sau tên task: task phải ghép trước.

```
Đợt 0 — main (sau 3a-2, 4a-2) → N₀ passed

Đợt 1 — song song, 6 worktree từ main
  T1 mã ghép phía trạm · T2 hạn mức Codex · T3 cho phép cli codex
  T4 dò máy · T5 cấu hình MCP · T6 launchd + Keychain
  → N₀+31 passed (+4 +9 +2 +3 +7 +6)

Đợt 2 — song song, 4 worktree từ main sau đợt 1
  T7 app-server (2) · T8 ChayCodex (2) · T9 /api/ghep-may + cap-ma (1, 4) · T10 kế hoạch dang-ky (3, 4, 5, 6)
  → N₀+57 passed (+5 +4 +3 +14)

Đợt 3 — song song, 3 worktree từ main sau đợt 2
  T11 thực hiện + lệnh dang-ky (10; lenh.py sau T9) · T12 tram tho kiem 3b (4, 7) · T13 BoCodex + BO_CLI (2, 7, 8; 3a-2)
  → N₀+67 passed (+4 +3 +3)

Đợt 4 — 1 worktree từ main sau đợt 3
  T14 kịch bản giả lập (1–13)
  → N₀+68 passed (+1)
```

| Task | Độ khó | Đợt | Phải xong trước | File chạm (ngoài test) | Test mới | Toàn bộ sau task (trên main đợt trước) |
|---|---|---|---|---|---|---|
| 1 | kho | 1 | — | `tram/phieu/ma_ghep.py` | 4 | N₀+4 |
| 2 | de | 1 | — | `tram/chay_cli/codex/__init__.py`, `tram/chay_cli/codex/han_muc.py` | 9 | N₀+9 |
| 3 | de | 1 | — | `tram/tho/cau_hinh.py`, `tram/tho/cau_hinh_chay.py`, `tram/api/tho.py` | 2 | N₀+2 |
| 4 | de | 1 | — | `tram/tho/do_may.py` | 3 | N₀+3 |
| 5 | de | 1 | — | `tram/tho/mcp_tho.py` | 7 | N₀+7 |
| 6 | de | 1 | — | `tram/tho/launchd_tho.py`, `tram/tho/token_may.py` | 6 | N₀+6 |
| 7 | kho | 2 | 2 | `tram/chay_cli/codex/app_server.py` | 5 | N₀+36 |
| 8 | kho | 2 | 2 | `tram/chay_cli/codex/luong.py`, `tram/chay_cli/codex/chay.py` | 4 | N₀+35 |
| 9 | de | 2 | 1, 4 | `tram/api/ghep.py`, `tram/chu/cap_ma.py`, `tram/api/app.py`, `tram/tho/lenh.py` | 3 | N₀+34 |
| 10 | kho | 2 | 3, 4, 5, 6 | `tram/tho/khai_khe.py`, `tram/tho/ke_hoach_dk.py` | 14 | N₀+45 |
| 11 | kho | 3 | 10 | `tram/tho/thuc_hien_dk.py`, `tram/tho/lenh_dang_ky.py`, `tram/tho/lenh.py` | 4 | N₀+61 |
| 12 | de | 3 | 4, 7 | `tram/tho/kiem_3b.py`, `tram/tho/kiem_may.py` | 3 | N₀+60 |
| 13 | de | 3 | 2, 7, 8 | `tram/chay_cli/codex/bo.py`, `tram/chay_cli/bo_cli.py`, `tram/tho/{ngu_canh,mot_lan,principal,vong_khe}.py` | 3 | N₀+60 |
| 14 | de | 4 | 1–13 | (chỉ test) | 1 | N₀+68 |

Không file nào bị hai task cùng đợt sửa. File dùng chung giữa các đợt: `tram/tho/lenh.py` — Task 9 (đợt 2) rồi Task 11 (đợt 3), hai chỗ khác nhau. Thư mục `tests/du_lieu/codex/` có file của Task 2 (đợt 1), Task 7, 8 (đợt 2, khác tên file). Sau plan: **68 test mới**, tổng **N₀+68**; hai dòng test cũ đổi (Task 3).

**Đụng chung file với plan khác** (G20): `tram/api/app.py` (1b-3, 2b; có thể 4a-2), `tram/tho/lenh.py`, `tram/tho/kiem_may.py`, `tram/tho/cau_hinh.py`, `tram/api/tho.py`, `tests/test_api_tho.py`, `tests/test_cau_hinh_tho.py` (3a-1; có thể 3a-2), `tram/chay_cli/bo_cli.py` (3a-2 — G3).

## Để sau (chờ cổng) — không lập task code ở plan này

Phần dưới **không** được đánh dấu sẵn sàng bằng fixture. Mỗi dòng ghi cổng và chỗ plan đã chừa.

| Phần | Spec | Cổng | Đã chừa sẵn |
|---|---|---|---|
| Xác minh Codex thật: (1) `codex app-server` dưới launchd + `CODEX_HOME` riêng — bắt tay `initialize`/`initialized`, tên `account/rateLimits/read`, hình dạng `rateLimits.*.{usedPercent, windowDurationMins, resetsAt}` (đơn vị `resetsAt`), có cần gửi tin cho model không; (2) `codex exec --json`: tên sự kiện, `turn.completed.usage` (cache có nằm trong `input_tokens` không — G16), thông điệp hết hạn mức / chưa đăng nhập (G13), có mang hạn mức không; (3) cờ G15: `--add-dir`, `-c approval_policy="never"`, `sandbox_workspace_write.network_access=false` có chặn mạng thật; `.git` trong vùng ghi có bị sandbox khoá không (nếu khoá: `tram bao` không commit được → cần phương án — thợ commit thay agent); lệnh ngoài sandbox bị từ chối trong thời gian hữu hạn, không treo; hook; (4) `codex login status` mã 0/≠0 (G9); (5) MCP: `env_http_headers` trong `config.toml` (G10). Ghi fixture thật thay fixture hiện có, chạy lại test Task 2, 7, 8 | §8.1, §7.2, §12 S5 | **S5** (cần cho phép) | adapter `tram/chay_cli/codex/*`; fixture `tests/du_lieu/codex/*` ghi "chờ S5" |
| `claude mcp add-json --scope user` với `CLAUDE_CONFIG_DIR` của khe có ghi đúng chỗ khe đọc; Claude mở rộng `${TRAM_*}` trong `url`/`headers`; `tailscale serve` đường `/nho` → 7710 | spec 1b §9.2, N2 | **N2** + #5 | `lenh_claude_mcp`, `url_nho`, `--khong-nho` |
| Mac thợ chạy dưới tài khoản quản lý thợ: Keychain `tram-tho-token` khi không có phiên GUI (đăng nhập trước/sau reboot), `security -i` với token có `-`/`_` trong ngoặc kép (G12); LaunchAgent của user đó; principal thực thi của khe, quyền đọc `CODEX_HOME` cho `login status`/`app-server` (chạy dưới principal nào); git chạy với hook/fsmonitor tắt khi agent ghi được `.git/config` (G15) | §7.3, §9.2 | **S6** | `ghi_token_may` (đọc lại, so khớp), `tao_plist_tho`, mục cảnh báo "chờ S6" trong kế hoạch |
| Push ref tạm từ Mac thợ từ xa: credential GitHub của tài khoản quản lý thợ chỉ push `tram/luot/*`, hoặc "cơ chế khác" khi S7 chọn phương án lùi (trạm fetch từ kho thợ — không áp được cho máy từ xa) | §6.4 | **S7** + Đại ca chốt §14 | — (dang-ky in cảnh báo; `tram tho kiem` không kiểm push) |
| Tailscale thật: máy B đăng nhập, `tailscale serve`; Đại ca tạo ACL `tagOwners` cho `tag:tram-tho` và gắn tag cho Mac thợ; Host thật qua `tailscale serve` cho `/api/ghep-may` (`host_hop_le` của 2a) | §9.2, #3 | **#5** (chưa duyệt) | `kiem_tag` (chỉ đọc), `TAG_THO`, `tram chu cap-ma` in lệnh mẫu |
| Kiểm chứng trên máy thật: một Mac thợ gắn tag, `tram chu cap-ma C` → `tram tho dang-ky … --khe codex-1:codex:coder:…` → `tram tho kiem` xanh (trừ mục chờ S6) → một bead nháp chạy bước `code` trên `C/codex-1` | §15 mục 3 | mọi cổng trên + phần 4 phát phiếu | Task 14 là bản giả lập của chính luồng này |
| `tram tho them-khe`/`bot-khe` cho Mac thợ (sửa `tho.yaml` + `POST /api/tho/dang-ky`) | §9.1 | 3a-2 | `dang-ky` chạy lại được (thay khối MCP, `tho.yaml.bak`) — nhưng cần mã ghép mới |

## Tự review

**1. Độ phủ spec (phần lát 3b)**

| Yêu cầu spec | Task | Kiểm bằng |
|---|---|---|
| §3 hàng 3b / §9.2: `tram chu cap-ma` in mã dùng một lần, hết hạn 10 phút | 1, 9 | `test_cap_roi_doi_mot_lan_ra_token_may`, `test_het_han_sau_10_phut_va_ma_moi_huy_ma_cu`, `test_cli_chu_cap_ma` |
| §9.2 `tram tho dang-ky --tram-chu --ma` → token máy 32 byte, Keychain `tram-tho-token` của tài khoản quản lý thợ | 1, 6, 9, 11, 14 | `test_doi_ma_qua_http_khong_can_bearer_token_dung_duoc_ngay`, `test_ghi_token_qua_stdin_roi_doc_lai_khop`, `test_tu_choi_gia_tri_la_tu_tram_tra_ve`, `test_ghep_dang_ky_nhip_codex_roi_go_may` |
| §9.2 thu hồi `tram chu go-may` (3a-1) áp cho máy ghép qua mã | 14 | `go_may` → ping 401 trong kịch bản |
| §9.2 Mac thợ là thiết bị **gắn tag** (#3) | 4, 10, 12 | `test_tag_tailscale_chi_doc_khong_doi`, `test_tu_choi_khi_chua_gan_tag_hoac_thieu_cli`, `test_chua_dang_nhap_chua_doc_han_muc_chua_gan_tag` |
| §9.2 minh bạch Q15: in danh sách thay đổi (tài khoản, file cấu hình, launchd, cấu hình memory MCP) và chờ `dong-y` | 10, 11 | `test_ke_hoach_chi_do_khong_ghi_gi` (chưa ghi gì, đủ mục), `test_cli_liet_ke_roi_cho_dong_y` |
| Kiến trúc §7: dò CLI + trạng thái đăng nhập (không đọc file đăng nhập), khai vai từng CLI, ghi cấu hình memory MCP vào claude/codex, cài launchd | 4, 5, 6, 10, 11 | `test_codex_dang_nhap_qua_lenh_trang_thai_voi_codex_home_cua_khe`, `test_doc_khe_sai` (7 ca), `test_codex_*` / `test_claude_qua_lenh_cua_cli_voi_thu_muc_cua_khe`, `test_plist_chay_tram_tho_chay_khong_mang_bi_mat`, `test_thu_tu_ghep_token_yaml_tep_mcp_dang_ky_launchd` |
| Kiến trúc §7: "trỏ beads host về trạm chủ" | — | **không làm** (G6); kế hoạch in "không trỏ Beads" — `test_ke_hoach_chi_do_khong_ghi_gi` kiểm chữ "Beads" |
| §9.1 `tho.yaml` có khe `cli: codex` | 3, 10, 11 | `test_tho_yaml_nhan_khe_codex_tu_xa`, `test_chua_dang_nhap_chi_canh_bao_va_tho_yaml_hop_le` |
| §9.3 `tram tho kiem` cho máy từ xa (tram-api qua https, CLI, đăng nhập, cầu dao, tag; H7) | 12 | `test_khe_codex_thay_muc_dang_nhap_them_han_muc_va_tag`, `test_kiem_may_goi_bo_sung_3b` |
| §8.1 Codex: app-server `usedPercent`/`windowDurationMins`/`resetsAt`, hỏi lúc rảnh mỗi 5 phút; nguồn lùi rollout `used_percent`/`window_minutes`/`resets_at`; chuẩn hoá theo thời lượng, không primary/secondary; thiếu → chưa biết, không 0% | 2, 7, 13 | `test_app_server_theo_thoi_luong_khong_theo_primary` (prolite: primary là tuần), `test_cua_so_la_giu_ten_goc_truong_sai_bi_bo_khong_gia_0`, `test_rollout_dung_truong_snake_case_va_gio_cua_dong`, `test_bat_tay_roi_hoi_rate_limits`, `chu_ky_han_muc_ranh_giay == 300` |
| §8.2 H4 áp cho khe Codex | 14 | nhịp có tuần 91% → không phiếu; 62%/12,5% → nhận phiếu |
| §8.3 / H5: hết hạn mức → cầu dao (thợ phân loại `ket_thuc`) | 2, 8 | `test_het_han_muc_chi_tu_thong_diep_loi` (5 ca), `test_het_han_muc_va_chua_dang_nhap` (`ket_thuc_tu` → `het_han_muc`, `loi_he`) |
| §7.2 Codex: `codex exec --json`, sandbox ghi trong worktree, mạng, approval; bộ chuẩn hoá riêng | 8, 13 | `test_lenh_codex_sandbox_ghi_worktree_khong_mang_khong_hoi` (không cờ bỏ qua sandbox), `test_bo_codex_them_git_chung_va_thu_muc_phieu`, `test_xong_dem_token_va_log_che_ma_giao` |
| §7.2 chạy trong nhóm tiến trình riêng, dừng: SIGTERM 10 s rồi SIGKILL; §7.3 mục 6 log che `ma_giao` | 7, 8 | `test_dung_giet_ca_nhom_ke_ca_khi_bo_qua_sigterm`, `test_treo_thi_het_gio_va_giet`, `b"MA-GIAO-BI-MAT" not in log` |
| §7.2 môi trường CLI không có token máy | 7 | `test_doc_han_muc_ranh_chuan_hoa_va_moi_truong_toi_thieu` (không biến `TRAM_*` cho app-server); môi trường lần chạy do vòng 3a-2 dựng (G3) |
| §12 S5: "hình dạng chưa xác minh → adapter + fixture" | 2, 7, 8 | mọi fixture/script giả ghi "chờ S5"; "Để sau" có bước kiểm khi chạy thật |
| §16 không Gemini | 3, 10 | `cli: gemini` → lỗi ở `tho.yaml`, API, `--khe` |

**2. Quét placeholder:** không có "TBD/TODO/tương tự Task N"; mọi bước mã có khối mã đầy đủ (file mới nguyên văn; file có sẵn bằng bản vá sinh từ bản đã chạy, Task 13 tạo registry và có bản vá đủ cho vòng thợ); mọi lệnh có kết quả mong đợi. `N₀` và `<model đang thực thi>` là cố ý.

**3. Đối chiếu chữ ký (phải kiểm lại khi triển khai bản sửa):** `cap_ma_ghep → MaGhep(ma, may_id, het_luc)`, `doi_ma_ghep → (may_id, token)` (1) ↔ `ghep.py`, `cap_ma.py` (9), kịch bản (14); `han_muc_app_server(ket_qua, *, khe_id, bay_gio)` (2) ↔ `doc_han_muc_ranh` (7), kịch bản (14); `MAU_CHUA_DANG_NHAP`, `thong_diep_loi`, `NguonHanMucCodex` (2) ↔ `DocLuongCodex` (8), `BoCodex.tao_nguon` (13); `CLI` (3) ↔ `doc_khe` (10); `KetQuaDo`, `do_cli(cli, thu_muc, *, which, chay)`, `kiem_tag(*, which, chay)`, `TAG_THO` (4) ↔ 9, 10, 12; `url_nho`, `ghep_codex_toml(cu, url)`, `lenh_claude_mcp(claude, thu_muc)` (5) ↔ 10; `tao_plist_tho(*, tram, log, home)`, `lenh_nap_launchd(plist, *, uid)`, `ghi_token_may(may_id, token, *, chay)` (6) ↔ 10, 11; `CHU_KY_RANH_GIAY`, `doc_han_muc_ranh(khe_id, thu_muc_cau_hinh, *, bay_gio, codex, hoi)` (7) ↔ 12, 13; `ChayCodex().chay(argv, *, cwd, env, stdin, log, dung, nguon)` khớp Protocol `ChayCLI` của 3a-1 (8) ↔ 13; `KeHoachDangKy`, `DauDoDK`, `noi_dung_tho_yaml(may_id, tram_api, khe)` (10) ↔ 11; `HieuUng(ghep, ghi_token, dang_ky, chay)` (11) ↔ 14; `bo_sung_3b(ch, dd, ra, *, doc_han_muc, bay_gio)` (12) ↔ `kiem_may`; `BoCodex` thành viên đúng G3 (13).

**4. Đã chạy thử (13/10):** dựng bản sao ở scratchpad (không đụng repo thật, không gọi Codex/Claude/Tailscale/`security`/`launchctl` thật, không mạng, không `~/.tram` thật): nền = bản sao `main` `891ae04` + mã 3a-1 và 4a-1 dựng lại từ văn bản plan (bản `r4b` của đợt 2: **1213 passed**) + `tram/nho/cau_hinh_mcp.py` chép nguyên văn plan 1b-2 Task 6 + **bản thế chỗ** `tram/chay_cli/bo_cli.py` đúng G3 (Protocol `BoCLI`, `BO_CLI = {}` — CHỈ cho lần chạy thử, không thuộc plan). Mỗi task: viết test → chạy thấy fail (thông báo ở Step 2 là kết quả thật) → viết mã → pass; toàn bộ 1213 → **1281 passed** (+68), chạy lại các test có tiến trình con (Task 7, 8) 3–5 lần không chập chờn. Bản vá Task 3, 9 (`lenh.py`), 11, 12 sinh bằng `git diff` từ chính bản đã chạy. Bản vá `tram/api/app.py` Task 9 viết trên nền **1b-3 + 2b** (bản sao chỉ có 3a-1): đã dựng lại `app.py` sau hai bản vá đó từ văn bản plan 1b-3/2b, áp bản vá Task 9 bằng `git apply` — khớp; trên bản sao chạy thử đã áp biến thể tương đương trên nền 3a-1. **Chưa chạy thử được:** trên nền có 1b-3, 2b, 1b-2 thật, 3a-2 và 4a-2 (chưa có mã/plan đọc được) — số tuyệt đối là N₀ + k; Task 13 phụ thuộc hình dạng `bo_cli.py` của 3a-2 (G3). Kiểm lại văn bản plan: tách mọi file mới + bản vá từ chính văn bản plan, áp lên nền bản sao → khớp từng byte, 1281 passed. Các số dòng ở bản scratchpad không phải kiểm chứng của bản đã sửa; giữ module quanh120dòng và tách helper nếu vượt khi triển khai.

**5. Rủi ro còn lại (Đại ca biết):** (a) Toàn bộ hình dạng dữ liệu Codex là hiểu biết tốt nhất, chưa chạy thật — S5 có thể đổi tên sự kiện/trường; sửa chỉ trong `tram/chay_cli/codex/*` + fixture. (b) Nếu sandbox Codex khoá `.git` trong vùng ghi, `tram bao` không commit được trong khe Codex → cần đổi luồng (thợ commit thay) — phát hiện ở S5, chưa có phương án trong plan. (c) S6 chưa chứng minh commit an toàn dưới principal; không mở common-dir để vượt cổng. (d) G3 đã nối bằng bản vá nền 3a-2; chạy kiểm tích hợp khi triển khai, không dùng stub registry. (e) mã ghép nhập kín bằng getpass sau bước đồng ý, không nằm trong argv/lịch sử shell; thay cú pháp triển khai, giữ hạn 10 phút/dùng một lần của spec. (f) Lỗi giữa chừng của `dang-ky` không tự lùi (G11) — cần mã mới và có thể `go-may`. (g) `tram tho kiem` trên máy từ xa gọi `codex app-server` thật (tốn vài giây; không gửi tin cho model theo spike 12/10 — xác nhận ở S5).

## Cần sửa spec sau (chờ Đại ca chốt cùng plan)

- **Spec 3 §9.2:** mã ghép gắn `may_id` ở `tram chu cap-ma <may_id>`, 60 bit, lưu băm, cấp lại huỷ mã cũ, máy có token thì từ chối, khoá sau 5 lần sai/10 phút (G2); endpoint `POST /api/ghep-may` ngoài nhóm `/api/tho/*` (G1); cú pháp `--khe`, `--thu-muc-khe`, `--khong-nho`, `--dong-y` (G7); điều kiện từ chối (G8); thứ tự thực hiện (G11).
- **Spec 3 §10:** thêm sự kiện `_tram` `may.cap_ma {may_id, het_luc}`, `may.ghep {may_id}`, `may.ghep_sai {so_lan}` (G2).
- **Spec 3 §9.3:** mục `tailscale tag` cho máy có `tram_api` https; khe Codex: đăng nhập qua `codex login status`, mục hạn mức vàng khi không đọc được (G17).
- **Spec 3 §8.1:** `codex exec --json` không là nguồn hạn mức (chỉ phát hiện hết hạn mức); quy ước đơn vị `resets_at` (G13).
- **Spec 3 §7.2:** lệnh Codex cụ thể và việc không có lớp quyền theo vai cho Codex (G15); token Codex (G16).
- **Kiến trúc §7 "Mac thợ":** bỏ "trỏ beads host về trạm chủ" (G6) — mâu thuẫn với "máy thợ không được cấp quyền ghi Beads".
- **Plan/spec 3a-2:** giao diện `BoCLI`/`BO_CLI` (G3), `tram tho chay` với `tram_api` https + nhãn `vn.tram.tho` (G4), biến `TRAM_NHO_URL` cho máy từ xa (G5) — Codex đối chiếu khi gom review.
- **Spec 2 (2b, 2c):** khe có `cli: "codex"` (G19) — Đội ngũ AI/Văn phòng 3D hiện được nhãn CLI này.


## Review tĩnh đợt 3 — giới hạn readiness

- S5 và **Q15**: whitelist đã duyệt chưa có endpoint OpenAI. Trước chạy Codex thật cần spike nêu endpoint thực và Đại ca duyệt bổ sung; không tự mở mạng. `network_access=false` của sandbox không phải bằng chứng mọi lớp CLI bị chặn mạng.
- G15 bỏ `--add-dir <git chung>` trong mã mẫu: cho phép ghi config/hooks chung là leo quyền qua Git của manager. S6 cần lời giải commit an toàn cho cả Claude/Codex trước dùng thật; chưa tự chọn hai phương án §14.
- G4 phân vai: máy B do 3a-2 quản lý LaunchDaemon; máy từ xa mới dùng LaunchAgent 3b. Task 10/11 từ chối nếu đã có daemon hoặc tho.yaml, trước đổi mã/token; không migrate/ghi đè cấu hình cũ. Đăng ký chỉ staging plist, chưa bootstrap trước khai principal/chay.day và đạt S2/S6/S7. Regression từ chối lần đăng ký hai không thêm hiệu ứng.
- G34/G35 của 3a-2 vẫn áp dụng: principal sandbox/Keychain và token riêng khe chưa kiểm dưới service thật.
- Task 13 tạo registry và các bản vá worker thật; Task 8 nhận đầy đủ callback/kill như ChayClaude, không chạy Codex dưới user manager. Coverage factory/kill/token/log mở rộng trong 4 test hiện hữu; Task 13 vẫn 3 test. Tổng vẫn **68 test mới dự kiến**, chưa chạy trong review.
- Bản thử lịch sử dùng stub `BO_CLI = {}` trên nền 1213 không chứng minh tích hợp trên eb97f87 (1458 + Task 9 1b-2 + 3a-2 + 4a-2).

## Ghi chú triển khai (code 14/10/2026)

- **Kết quả:** code xong 14 task trong 4 đợt. Plan thêm **68 test**, đúng kỳ vọng: 1692 trước khi bắt đầu (đã gồm 4a-2 Task 13), 1760 sau Task 14.
- **Chạy song song:** đợt 1 chạy cùng 4a-2 Task 13. Task 14 chạy cùng đợt 1 của 4b. Các task chạy song song không sửa chung file nào.
- **Lệch plan:**
  1. **Task 9:** cả hai bản vá `app.py` và `tho/lenh.py` không áp được nguyên văn, vì 3a-2 và 4a-2 đã đổi ngữ cảnh. Đã áp tay đúng các dòng `+`, giữ nguyên `tho_them`, `tuyen_giao` và các lệnh của 3a-2.
  2. **Task 10, 13:** ngắt lại các dòng dài hơn 120 ký tự (kế hoạch đăng ký, docstring `bo.py`, `mot_lan.py`, tuple `BIEN_GIU`), giá trị không đổi. Sau Task 13, `vong_khe.py` dài 125 dòng; giữ nguyên, không tách file. `ngu_canh.py` còn một import `NguonHanMucClaude` không dùng, giữ lại vì nó là ngữ cảnh của bản vá.
  3. **Task 14:** plan tự mâu thuẫn. Theo G4 của review đợt 3, `thuc_hien_dk` phải từ chối ngay khi máy đã có `tho.yaml`, nên lần gọi thứ hai báo `ValueError` thay vì 403. Phần kiểm "mã đã dùng" vì vậy gọi thẳng `ghep_that(URL, ma, mo=mo)`. Ý kiểm giữ nguyên: mã dùng một lần, lần thứ hai nhận 403.
- **Sự cố khi chạy:** một subagent (Task 4) chạy `pkill -f "pytest -q"`, làm ngắt pytest của các agent khác. Đã chạy lại, kết quả không đổi. Hướng dẫn chung cho subagent đã thêm luật cấm `pkill`/`killall`.
- **Còn chờ cổng:** S5 (Codex thật), allowlist mạng OpenAI (Q15), S6/S7, chạy `dang-ky` thật trên Mac từ xa. Plist mới chỉ dựng sẵn, chưa bootstrap.
