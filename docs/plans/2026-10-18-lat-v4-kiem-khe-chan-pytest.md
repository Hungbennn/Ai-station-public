# Lát V4 — kiểm cách ly khe dưới tài khoản quản lý thợ (D54) và pytest từ chối chạy ngoài bộ chặn (D61) — Implementation Plan

> **Cập nhật reviewer vòng 2, 18/10/2026, HEAD `8b23e8f`:** D62–D64 đã chốt API cấp đích,
> `[CHUYỂN]` không tính lỗi và chỉ kiểm trên máy B; các câu hỏi/“giả định chờ Đại ca” bên dưới là lịch sử.
> V4-2 đã ghép, không áp lại. Chỉ triển khai V4-1. Reviewer thêm `curl -q` và assertion tương ứng
> trong mã nguyên văn để không đọc `.curlrc` của khe. Không chạy code/test trong vòng này;
> mọi số RED/GREEN dưới đây thuộc bản tác giả trước sửa vòng 2. Xem báo cáo `REVIEW-CODEX-dot9-vong2.md`.

> **For agentic workers:** REQUIRED SUB-SKILL: dùng `ai-skills:subagent-driven-development` (khuyến nghị) hoặc `ai-skills:executing-plans` để làm từng task. Step dùng checkbox (`- [ ]`). **Task V4-1 chưa được code**: chạm kill list mục 3 (thăm dò cách ly, đường `sudo` sang khe) và thêm một route API thợ — phải có Đại ca duyệt plan và review Codex trước (xem Global Constraints). Task V4-2 chỉ chạm bộ test và docs.

**Trạng thái: BẢN SỬA V4-1 sau Codex review gộp vòng 1 (`.handover/review-codex-plan/REVIEW-CODEX-dot9-vong1.md`), 18/10/2026.** V4-1 viết lại trên `main` `d340a27` (mã/test giống hệt `cc1e4a5` — từ đó `main` chỉ thêm hai file plan): giới hạn hai thăm dò mới ở quản lý thợ trên máy B (#5), từ chối đích thiếu/null (#6 — sửa của Codex, nay chạy thật), thêm 401 cho token sai/danh tính Đại ca không có Bearer (#8); RED→GREEN thật, cả bộ đo lại, áp lại + `diff -r` — mục "Phản hồi review vòng 1". Q1/Q2/Q3 CHƯA có trả lời của Đại ca: thiết kế theo ĐỀ XUẤT của Em, là GIẢ ĐỊNH chờ Đại ca. **V4-2 đã ĐẠT review, đang code ở nhánh khác — KHÔNG sửa trong bản này** (mọi số/ghi chú của V4-2 bên dưới là của bản trước). Bản trước: viết trên `main` `cc1e4a5` (đã ghép V2, V2b, V2c, V3, V3b, V3-6/7) trong worktree `plan/v4-d54-d61`. Đã chạy RED→GREEN thật cho cả hai task theo thứ tự V4-1 → V4-2, đo cả bộ ở cuối qua `tests/chan_host/chay.sh -q`, áp lại toàn bộ khối mã/docs của plan lên bản sạch và so `diff -r` với trạng thái đã chạy (khớp — mục "Kiểm chứng plan"), rồi hoàn nguyên. Nhánh chỉ có file plan. CHƯA áp vào `main`. CHƯA đo trên OS (G5 ĐÓNG).

**Goal:** (V4-1, D54, `bs-2bd.1.25`) Hai phép kiểm của khe — "gọi API Duyệt giả danh Đại ca phải bị từ chối" và "kết nối DB nghiệp vụ phải bị từ chối" — chạy trong `tram tho kiem` dưới tài khoản **quản lý thợ** (đã có sudoers `tram-tho → khe` không mật khẩu, đo ở G3 18/10), dưới CHÍNH principal khe, giữ nguyên chuẩn chấm V2b A-T6. **Lát này chỉ cho quản lý thợ trên máy B** (`tram_api` loopback); thợ ở máy khác → ĐỎ "không kết luận" (chưa có ánh xạ đích đã chứng minh). `tram chu kiem-cach-ly` ở tài khoản trạm không còn `sudo -n` sang khe (trạm không được cấp quyền đó): mục khe in `[CHUYỂN]` chỉ sang `tram tho kiem` thay vì ĐỎ khó hiểu. (V4-2, D61, `bs-2bd.1.26`) pytest **từ chối chạy** (thoát 4, hướng dẫn tiếng Việt) khi không đi qua `tests/chan_host/chay.sh`.

**Architecture:** V4-1: trạm cấp "đích" của hai thăm dò qua route mới `GET /api/tho/kiem-am` (cùng xác thực token máy như mọi `/api/tho/*`), lấy từ CHÍNH cấu hình trạm dùng để kiểm ghi — login Đại ca đầu tiên (`dai_ca_logins`), tên máy B cho `Origin` (`ten_may_b`) — và `cach_ly.db_nghiep_vu`. Thợ đọc bằng `KhachTram.kiem_am()` (kiểm dạng từng giá trị trước khi vào argv: không xuống dòng/khoảng trắng trong header, `host:cổng` đúng mẫu). `kiem_cong.cach_ly` — chỉ khi `CauHinhTho.tren_may_b` (`tram_api` là `http://127.0.0.1:`/`http://localhost:`, tức quản lý thợ chạy trên chính máy B; khác → ĐỎ "không kết luận", không lấy đích, không curl/nc) — lấy đích MỘT lần, ghép hai thăm dò (dựng bằng `tham_do_api_db` — tách từ `tham_do_day_du`, dùng chung với phía trạm) vào bộ rút gọn của từng khe rồi chạy qua đúng đường đang có: `xac_minh_uid` TRƯỚC → `chay_tham_do` (dương trước, đối chứng dưới quản lý, `chay_gioi_han` có hạn với `kill` của principal, sở hữu tiến trình qua `khoi_chay(chu=…)`) → chấm `cham_tham_do` → tàn dư. Không lấy được đích, hoặc trạm chưa khai login/máy B (client từ chối `null`/thiếu khoá) → ĐỎ "không kết luận", phần rút gọn vẫn chạy. Phía trạm, `kiem_cach_ly` chỉ còn kiểm `tram-kiem`; mỗi `--principal` của khe thành một dòng `[CHUYỂN]` không tính vào mã thoát. V4-2: runner đặt `TRAM_CHAN_CHAY_SH=1`; `tests/conftest.py` (`pytest_configure`, trước khi thu thập) đòi đủ ba dấu — biến đó, plugin `chan_host` đã nạp, `git` đầu `PATH` là `git` giả của bộ chặn — thiếu thì `pytest.exit(…, returncode=4)`.

**Tech Stack:** Python 3.12 stdlib (`re`, `shutil`), FastAPI (route có sẵn kiểu), pytest 8. Không dependency mới.

**Spec / nguồn:** quyết định [D54, D55, D61](../quyet-dinh/2026-10-18-chot-sau-dot8.md); plan V2b [`2026-10-17-lat-v2b-vong-doi-tien-trinh.md`](2026-10-17-lat-v2b-vong-doi-tien-trinh.md) mục "Thiết kế V2-6b" và Task 6 (chuẩn chấm A-T6, bảng G6); spec 3 §7.3 mục 7, §9.3; spec 2 §4 mục 2b; ADR-0003 (token máy), ADR-0004 (danh tính, kênh ghi); `docs/AGENT_RULES.md` §2, §11, §13; sổ tay chạy thật G3 (bằng chứng 18/10), G5; mã thật: `tram/chu/kiem_cach_ly.py`, `tram/tho/kiem_am.py`, `kiem_cong.py`, `cham_tham_do.py`, `kiem_may.py`, `khach.py`, `tram/api/tho.py`, `tho_them.py`, `bao_mat.py` (chỉ đọc), `tram/cau_hinh/cach_ly.py`, `tests/chan_host/{chay.sh,chan_host.py,sitecustomize.py}`, `tests/conftest.py`, `tests/test_chan_host.py`.

## Global Constraints

- **Kill list (`AGENT_RULES.md` §2 mục 3 — cách ly agent, sudo) — STOP, chờ Đại ca duyệt trước khi code V4-1.** V4-1 sửa thăm dò cách ly (`tram/tho/kiem_am.py`, `tram/tho/kiem_cong.py`, `tram/chu/kiem_cach_ly.py`) và BỎ đường `sudo -n` từ tài khoản trạm sang khe. Không đụng `tram/kiem/`, `tram/tho/principal.py`, `tram/tho/sandbox.py`, `tram/tho/cham_tham_do.py` (chuẩn chấm giữ nguyên ký tự), `tram/api/bao_mat.py`, `tram/api/kenh_ghi.py`, sudoers/installer (`tram/chu/cai_dat_tho.py`). Không đổi D45–D61.
- **Đổi hợp đồng giữa hai package (`AGENT_RULES.md` §11 — hỏi trước):** V4-1 thêm route `GET /api/tho/kiem-am` (`tram/api/tho_them.py`) và `KhachTram.kiem_am()`; trả login Đại ca đầu tiên, `ten_may_b`, `cach_ly.db_nghiep_vu` cho máy có token máy hợp lệ. Không bí mật (login và tên máy đã nằm trong header mọi yêu cầu ghi), nhưng là bề mặt mới — Câu hỏi 1.
- **Thăm dò cố định trong mã:** trạm chỉ cấp GIÁ TRỊ (login, tên máy, `host:cổng`), thợ kiểm dạng rồi mới đặt vào argv cố định; không nhận lệnh từ ngoài. Kết quả chỉ mang lý do cố định; lỗi lấy đích chỉ ghi TÊN loại lỗi (`LoiKhachTram`), không chép thông điệp/đầu ra.
- **N₀ = 3236** (`tests/chan_host/chay.sh -q` trên `cc1e4a5`, đo 18/10/2026: `3236 passed in 356.94s`, nhật ký chặn 0 dòng mới, điểm mù 48, push giả lập 629; `d340a27` cùng cây mã/test). **Sau V4-1 (bản sửa) đo thật 3253** (+17) trên `d340a27`; sau V4-1 + V4-2 đo thật **3258** (+22: V4-1 +17, V4-2 +5) trên cây dựng lại từ plan. Đo lại N₀ trước Task V4-1; lệch thì tìm nguyên nhân trước (V4-2 ghép trước thì N₀ = 3241).
- Chạy test BẮT BUỘC qua `tests/chan_host/chay.sh -q [đường test]`; "0 dòng mới" trong nhật ký chặn là điều kiện xanh. Sau V4-2, pytest trần tự thoát 4. (Khi viết plan, Em chạy pytest trần ĐÚNG MỘT LẦN có chủ đích để chứng minh RED của V4-2 — một file không spawn: `tests/test_cham_tham_do.py`; ghi ở Step 2 của V4-2.)
- **Test không bao giờ:** chạy `sudo`, `security`, mạng thật, `~/.tram` thật. tram-api chạy trong bộ nhớ (`tho_api_gia`, `khach_gia`); `chay`/`xac_minh`/`chup` giả; đối chứng Keychain/cổng DB không chạy trong test (test lọc bỏ hoặc chỉ kiểm hàm đối chứng là `mo_cong`). Subprocess pytest lồng của V4-2 luôn `--co` (chỉ thu thập — lớp chặn hỏng thì cũng không chạy test nào) và vẫn mang `PYTHONPATH` của bộ chặn.
- Mỗi file nguồn `tram/` ≤ 120 dòng, mỗi dòng ≤ 120 ký tự Unicode (`tests/test_do_dai_ma.py` canh). Sau plan: `tram/tho/kiem_cong.py` 118, `tram/tho/kiem_am.py` 110, `tram/tho/cau_hinh.py` 86, `tram/chu/lenh_tho.py` 100, `tram/tho/khach.py` 84, `tram/api/tho_them.py` 76, `tram/chu/kiem_cach_ly.py` 61. Định danh tiếng Việt không dấu.
- Hunk V4-1 viết trên `d340a27` (= `cc1e4a5` ở mọi file nó sửa); áp theo NỘI DUNG (`git apply --check` trước; không sạch thì DỪNG, báo điều phối — không chép dòng cộng theo trí nhớ). Một task một commit trên nhánh task; không push, không merge, không `bd` ghi. Giữ `bat_ghi: false`, `giao_viec.bat: false`.

## Bảng G — điều plan bảo đảm và bằng chứng

| # | Bảo đảm | Ở đâu | Bằng chứng offline | Còn chờ OS |
|---|---|---|---|---|
| G1 | `tram tho kiem` chạy "API Duyệt với header danh tính giả" và "kết nối DB nghiệp vụ <host:cổng>" dưới CHÍNH principal khe (`sudo -n -H -u <khe>` từ tài khoản quản lý thợ), sau `xac_minh_uid`, env chỉ PATH/LANG, `kill` của principal | `kiem_cong.cach_ly`, `_api_db`, `kiem_am.tham_do_api_db` | `test_tho_kiem_chay_api_va_db_duoi_principal_khe_sau_uid`, `test_kiem_cong.py` | G5.6: thăm dò chạy dưới UID khe thật |
| G1b | Chỉ quản lý thợ trên máy B (`tram_api` loopback) mới lấy đích và chạy curl/nc: đích là theo máy B (`127.0.0.1:7700`, DB `127.0.0.1:…` của trạm) và 403 qua `tailscale serve` không chứng minh kênh TCP trên B đã tách. Thợ máy khác (`https://…`, kể cả `https://127.0.0.1:…`) → ĐỎ "không kết luận: thợ không ở máy B", không gọi `dich`, phần rút gọn vẫn chạy | `CauHinhTho.tren_may_b`, `_api_db` | `test_chi_kiem_api_db_khi_tho_o_may_b` (4 ca; RED thật trên mã vòng 1: ca HTTPS vẫn lấy đích) | — |
| G2 | Đích đúng như API thật kiểm: login Đại ca đầu tiên + `Origin: https://<ten_may_b>` + `cach_ly.db_nghiep_vu` của trạm; chỉ máy có token máy lấy được | `/api/tho/kiem-am`, `KhachTram.kiem_am` | `test_tram_cap_dich_tu_cau_hinh_cua_chinh_no_qua_token_may` (401 khi thiếu token, token sai, hay chỉ có header danh tính Đại ca — không trả trường đích nào; 503 khi `cach_ly` sai) | — |
| G3 | Giá trị từ trạm sai dạng (xuống dòng/khoảng trắng trong login, tên máy lạ, DB không `host:cổng`, thân không phải bảng) hoặc login/máy B `null`/thiếu khoá → `LoiKhachTram`, không vào argv, không dùng giá trị giữ chỗ | `KhachTram.kiem_am`, `_khop` | `test_khach_tu_choi_dich_sai_dang_truoc_khi_vao_argv` (5 ca; RED thật với `_khop` cũ: `DID NOT RAISE`) | — |
| G4 | Chuẩn chấm A-T6 giữ nguyên: chỉ HTTP 401/403 là "bị chặn"; 2xx/422 "không đạt"; curl ≠ 0, 000, 404 → "không kết luận"; không chép stdout/stderr; DB có đối chứng `mo_cong` dưới quản lý | `cham_tham_do` (không sửa), `chay_tham_do` | `test_cham_api_giu_chuan_a_t6` (4 ca qua `chay_tham_do` thật), `test_cham_tham_do.py` (không sửa, xanh) | mã/stderr thật dưới khe (G5.6) |
| G5 | Không lấy được đích → mục cách ly ĐỎ "không kết luận … (LoiKhachTram)", phần rút gọn vẫn chạy, không lộ thông điệp lỗi | `_api_db` | `test_khong_lay_duoc_dich_thi_do_va_van_chay_phan_rut_gon` | trạm cũ chưa có route → 404 → ĐỎ |
| G6 | `tram chu kiem-cach-ly` không chạy gì dưới khe, không dò UID khe; in dòng [CHUYỂN] "kiểm cách ly khe bằng tram tho kiem…"; không tính vào mã thoát; chỉ có khe mà không có `tram-kiem` → mã 1 "Chưa có principal kiểm lại"; `tram-kiem` vẫn kiểm đủ, UID trước | `kiem_cach_ly` | `test_chu_kiem_cach_ly_khe_chuyen_tram_kiem_van_uid_truoc`, `test_chu_tho.py` | — |
| G7 | pytest không qua runner (thiếu `TRAM_CHAN_CHAY_SH=1`, plugin `chan_host`, hay `git` giả đầu PATH; kể cả gọi không chỉ file — `testpaths`) → thoát 4 với lệnh đúng, trước khi thu thập | `tests/conftest.py`, `tests/chan_host/chay.sh` | `test_pytest_khong_qua_chay_sh_thi_tu_choi` (4 ca); pytest trần một lần trước V4-2: `31 passed` (RED) | — |
| G8 | Runner và test lồng của chính bộ chặn vẫn chạy | `chay.sh` | `test_chay_sh_van_chay_duoc_qua_cong_d61`, `test_chay_sh_bao_so_dong_moi` và cả `tests/test_chan_host.py` xanh; cả bộ 3254 | — |

## Thiết kế V4-1 — đích của hai thăm dò khe lấy ở đâu

Thăm dò API phải mang **đúng** login Đại ca và **đúng** `Origin` máy B: sai một trong hai thì API trả 403 vì danh tính/Origin (`bao_mat.kiem_ghi`), không phải vì kênh ghi tách — thăm dò sẽ "đạt" giả. Tài khoản quản lý thợ không đọc được `~/.tram/cau-hinh.yaml` của trạm (và không được đọc — đó là một phép kiểm cách ly). Ba lựa chọn đã cân:

1. **Trạm cấp qua API thợ có token máy (chọn).** Một nguồn: đúng giá trị `bao_mat` dùng để kiểm. Đại ca không phải khai gì thêm. Bề mặt mới nhỏ: máy có token máy biết login Đại ca và danh sách `host:cổng` DB — đều không phải bí mật.
2. Đại ca khai tay `dai_ca_login`, `ten_may_b`, `db_nghiep_vu` vào `tho.yaml`. Ít mã hơn (chỉ `cau_hinh_chay.py`), nhưng hai nguồn lệch nhau được: gõ sai login → báo "bị chặn" giả, không có gì phát hiện.
3. Bỏ hẳn login thật, chỉ kiểm "API trả 403". Không chứng minh được kênh tách (403 đến từ login sai) — trái với lý do `kiem_cach_ly` dùng login thật.

Trạm chưa khai `dai_ca_logins`/`ten_may_b`: route trả `null`, client **từ chối** (review vòng 1 #6) → ĐỎ "không kết luận". Không dùng giá trị giữ chỗ: 403 vì thiếu cấu hình không phải bằng chứng cách ly với cấu hình dùng thật.

**Chỉ máy B (review vòng 1 #5, GIẢ ĐỊNH theo đề xuất Q3):** đích trạm cấp là theo máy B — API `127.0.0.1:7700` và DB khai dạng `127.0.0.1:3306` trong `cach_ly.db_nghiep_vu`. Trên máy thợ khác, `nc` tới `127.0.0.1:3306` (cả đối chứng quản lý lẫn thăm dò khe) nhắm DB của MÁY THỢ — hai phép đo đồng ý mà vẫn đo nhầm đích; và thăm dò API qua `tailscale serve` (`https://<máy B>`) nhận 403 vì danh tính bị thay, không chứng minh kênh TCP trên B đã tách. Nên `_api_db` chỉ chạy khi `tram_api` là loopback (`http://127.0.0.1:`/`http://localhost:` — `API_RE` của `tho.yaml` chỉ cho loopback dạng `http`; tram-api chỉ nghe `127.0.0.1` nên loopback nghĩa là quản lý thợ trên chính máy B). Khác → ĐỎ "không kết luận: thợ không ở máy B…", không gọi `dich`, không curl/nc. Không tự đổi loopback thành IP LAN/Tailscale (mở phạm vi kết nối mới). Hỗ trợ thợ từ xa cần ánh xạ đích theo máy + đường HTTP riêng — lát sau.

Trên máy B, thăm dò gọi thẳng cổng TCP của tram-api — kênh `header` sẽ ĐỎ "API nhận yêu cầu (HTTP 422)" (đúng rủi ro đã nhận ở D51, chưa đạt tới khi chuyển `unix-socket`); 422 đến SAU kiểm quyền vì thân `{}` thiếu trường (`tuyen_ghi` dùng `Depends(yeu_cau_ghi)` ở router), không ghi bead.

## Task ↔ file

| Task | Bead | ⛔ | File |
|---|---|---|---|
| V4-1 | `bs-2bd.1.25` (D54) | **có** — kill list mục 3; hợp đồng API thợ mới | Create `tests/test_kiem_khe_d54.py`; Modify `tram/api/tho_them.py`, `tram/tho/cau_hinh.py`, `tram/tho/khach.py`, `tram/tho/kiem_am.py`, `tram/tho/kiem_cong.py`, `tram/chu/kiem_cach_ly.py`, `tram/chu/lenh_tho.py`, `tests/test_tham_do_principal.py`, `tests/test_kiem_cong.py`, `tests/test_chu_tho.py`, `docs/handovers/2026-10-15-so-tay-chay-that.md` (G5.6) |
| V4-2 | `bs-2bd.1.26` (D61) | không (bộ test + docs) | Modify `tests/conftest.py`, `tests/chan_host/chay.sh`, `tests/test_chan_host.py`, `docs/AGENT_RULES.md` §13, `docs/MODULES.md`, `CLAUDE.md`, `docs/handovers/2026-10-15-so-tay-chay-that.md` (G6.1) |

Thứ tự: V4-1 rồi V4-2 (hunk sổ tay của V4-2 viết trên trạng thái sau V4-1). Hai task không chung file mã.

## Tasks

### Task V4-1: Kiểm API Duyệt giả danh + DB nghiệp vụ của khe trong `tram tho kiem`; trạm in `[CHUYỂN]` (D54, bs-2bd.1.25)

**Files:** như bảng trên.

**Interfaces:**
- `GET /api/tho/kiem-am` (token máy, router `tho_them`) → `200 {"dai_ca_login": str | null, "may_b": str | null, "db_nghiep_vu": [str]}`; `401` thiếu/sai token; `503 {"ly_do": "cach-ly-sai"}` khi `cach_ly` của trạm sai dạng.
- `tram.tho.khach.DichKiemAm(dai_ca_login: str, may_b: str, db_nghiep_vu: tuple[str, ...])` (frozen); `KhachTram.kiem_am() -> DichKiemAm` — mã ≠ 200, sai dạng, login/máy B `null` hay thiếu khoá → `LoiKhachTram`. Mẫu: login `[!-~]{1,320}`, máy `[A-Za-z0-9.-]{1,253}`, DB `cach_ly.DIA_CHI_RE`.
- `tram.tho.kiem_am.tham_do_api_db(*, api, dai_ca_login, may_b, db, mo=mo_cong) -> list[ThamDo]` — đúng hai loại thăm dò `http` và `nc` (argv giữ nguyên ký tự như trước); `tham_do_day_du` gọi lại hàm này.
- `tram.tho.cau_hinh.CauHinhTho.tren_may_b -> bool` (property): `tram_api` bắt đầu bằng `http://127.0.0.1:` hoặc `http://localhost:`.
- `kiem_cong.cach_ly(ch, du_an, *, goc, goc_wt, dich: Callable[[], DichKiemAm], chay_td=…, xac_minh=…, chup=…)` — `dich` **bắt buộc**; `_api_db(ch, dich) -> (list[ThamDo], list[KetQuaThamDo])` — `not ch.tren_may_b` → `([], [không kết luận])` không gọi `dich`; `dau_do_that` truyền `dich=khach.kiem_am`.
- `kiem_cach_ly(principal, *, chay_td, doc_pk, xac_minh)` — chữ ký giữ nguyên; `principal` chỉ sinh dòng `[CHUYỂN]` (hằng `CHUYEN`); `_ds_boc` thay bằng `_ds_kiem(doc_pk)`.

- [ ] **Step 0: Kiểm điều kiện vào** — Đại ca đã duyệt phần kill list + hợp đồng API (Câu hỏi 1–3; đang là giả định theo đề xuất). HEAD có `d340a27` hoặc sau đó mà `git diff d340a27 HEAD -- tram/api/tho_them.py tram/tho/cau_hinh.py tram/tho/khach.py tram/tho/kiem_am.py tram/tho/kiem_cong.py tram/chu/kiem_cach_ly.py tram/chu/lenh_tho.py tests/test_tham_do_principal.py tests/test_kiem_cong.py tests/test_chu_tho.py` rỗng; nếu không rỗng → `git apply --check` từng bản vá, hỏng thì DỪNG. Đo N₀: `tests/chan_host/chay.sh -q` → mong đợi `3236 passed`, 0 dòng chặn mới.

- [ ] **Step 1: Viết test**

Tạo mới `tests/test_kiem_khe_d54.py` (nguyên văn):

````python
"""D54 (bs-2bd.1.25): hai thăm dò "API Duyệt giả danh Đại ca" và "kết nối DB nghiệp vụ" của khe chạy trong
`tram tho kiem` dưới tài khoản QUẢN LÝ THỢ (sudoers `tram-tho → khe` có sẵn), đích lấy từ trạm qua `/api/tho/kiem-am`
(token máy). Phía trạm (`tram chu kiem-cach-ly` in [CHUYỂN]) ở `test_tham_do_principal.py`, `test_chu_tho.py`.
Không sudo, không mạng, không Keychain: tram-api trong bộ nhớ, `chay`/`xac_minh`/`chup` GIẢ."""
import json
import subprocess
from dataclasses import replace
from types import SimpleNamespace

import pytest

from api_gia import DAI_CA, LOGIN, MAY_B
from khach_gia import _TraLoi, khach_asgi
from test_kiem_cong import cau_hinh
from tho_api_gia import tao_tram
from tram.tho import kiem_cong
from tram.tho.cham_tham_do import mo_cong
from tram.tho.khach import DichKiemAm, KhachTram, LoiKhachTram
from tram.tho.kiem_am import KetQuaThamDo, chay_tham_do
from tram.tho.kiem_cong import cach_ly, dau_do_that

DICH = DichKiemAm(LOGIN, MAY_B, ("127.0.0.1:3306",))
API = "API Duyệt với header danh tính giả"


def test_tram_cap_dich_tu_cau_hinh_cua_chinh_no_qua_token_may(tmp_path, tram_home_tam):
    tram_home_tam.mkdir(parents=True, exist_ok=True)
    (tram_home_tam / "cau-hinh.yaml").write_text("cach_ly: {db_nghiep_vu: ['127.0.0.1:3306']}\n")
    t = tao_tram(tmp_path)
    assert khach_asgi(t.app, t.token["B"]).kiem_am() == DICH                     # login + Origin đúng như trạm kiểm
    assert t.goi("GET", "/api/tho/kiem-am", may=None).status == 401
    for h in ({"Authorization": "Bearer sai"}, DAI_CA):                         # token sai; danh tính Đại ca không thay
        r = t.goi("GET", "/api/tho/kiem-am", may=None, headers=h)
        assert r.status == 401 and not {"dai_ca_login", "may_b", "db_nghiep_vu"} & set(r.json())
    (tram_home_tam / "cau-hinh.yaml").write_text("cach_ly: {db_nghiep_vu: ['khong hop le']}\n")
    r = t.goi("GET", "/api/tho/kiem-am")
    assert r.status == 503 and r.json() == {"ly_do": "cach-ly-sai"}


@pytest.mark.parametrize("than", [{"dai_ca_login": "a@x\r\nX-Tram: 1", "may_b": "b", "db_nghiep_vu": []},
                                  {"dai_ca_login": "a@x", "may_b": "b/../c", "db_nghiep_vu": []},
                                  {"dai_ca_login": "a@x", "may_b": "b", "db_nghiep_vu": ["127.0.0.1"]},
                                  {"dai_ca_login": "a@x", "may_b": "b", "db_nghiep_vu": "127.0.0.1:1"}, []])
def test_khach_tu_choi_dich_sai_dang_truoc_khi_vao_argv(than):
    k = KhachTram("http://127.0.0.1:7700", "t", mo=lambda yc, timeout: _TraLoi(200, json.dumps(than).encode()))
    with pytest.raises(LoiKhachTram, match="sai dạng"):
        k.kiem_am()
    k = KhachTram("http://127.0.0.1:7700", "t", mo=lambda yc, timeout: _TraLoi(200, b'{"dai_ca_login": null, '
                                                                                 b'"may_b": null, "db_nghiep_vu": []}'))
    with pytest.raises(LoiKhachTram, match="sai dạng"):
        k.kiem_am()
    k = KhachTram("http://127.0.0.1:7700", "t", mo=lambda yc, timeout: _TraLoi(200, b'{"db_nghiep_vu": []}'))
    with pytest.raises(LoiKhachTram, match="sai dạng"):
        k.kiem_am()


def ghi(da):
    def chay_td(ds, *, boc, env, kill):
        da.append({"ds": ds, "argv": boc(["/bin/cat", "x"]), "env": env, "kill": kill})
        return [KetQuaThamDo(t.ten, True, "mã 1") for t in ds]
    return chay_td


def test_tho_kiem_chay_api_va_db_duoi_principal_khe_sau_uid(tmp_path):
    ch, da, xm = cau_hinh(tmp_path, ("user:tram-k-1",)), [], []
    ra = cach_ly(ch, [], goc=tmp_path, goc_wt=tmp_path / "wt", dich=lambda: DICH, chay_td=ghi(da),
                 xac_minh=lambda ten, boc, kill: xm.append((ten, len(da))) or 600, chup=lambda: [])
    assert [m.muc_do for m in ra] == ["xanh"] and xm == [("tram-k-1", 0)]                  # UID TRƯỚC thăm dò
    ds = {t.ten: t for t in da[0]["ds"]}
    assert da[0]["argv"][:5] == ["/usr/bin/sudo", "-n", "-H", "-u", "tram-k-1"] and set(da[0]["env"]) == {"PATH",
                                                                                                      "LANG"}
    assert da[0]["kill"].__self__.user == "tram-k-1"
    a = ds[API].argv
    assert a[:2] == ["/usr/bin/curl", "-q"]  # bỏ .curlrc của khe; env thăm dò chỉ PATH/LANG
    assert f"Tailscale-User-Login: {LOGIN}" in a and f"Origin: https://{MAY_B}" in a
    assert a[-1] == "http://127.0.0.1:7700/api/phe-duyet/kiem-am/kiem-am/duyet" and ds[API].kieu == "http"
    db = ds["kết nối DB nghiệp vụ 127.0.0.1:3306"]
    assert db.argv == ["/usr/bin/nc", "-z", "-G", "3", "127.0.0.1", "3306"] and db.doi_chung.func is mo_cong


def test_khong_lay_duoc_dich_thi_do_va_van_chay_phan_rut_gon(tmp_path):
    ch, da = cau_hinh(tmp_path, ("user:tram-k-1",)), []

    def hong():
        raise LoiKhachTram("tram-api trả 401 bi-mat")
    ra = cach_ly(ch, [], goc=tmp_path, goc_wt=tmp_path, dich=hong, chay_td=ghi(da), xac_minh=lambda *a: 600,
                 chup=lambda: [])
    assert [m.muc_do for m in ra] == ["do"] and "không lấy được đích từ tram-api (LoiKhachTram)" in ra[0].chi_tiet
    assert "bi-mat" not in ra[0].chi_tiet and API not in [t.ten for t in da[0]["ds"]] and da[0]["ds"]


@pytest.mark.parametrize("ma, out, muc, ly", [(0, "403", "xanh", "thăm dò đạt"), (0, "200", "do", "API nhận yêu cầu"),
                                             (7, "000", "do", "không kết luận: không gọi được API"),
                                             (0, "404", "do", "không chứng minh từ chối quyền")])
def test_cham_api_giu_chuan_a_t6(tmp_path, ma, out, muc, ly):
    """Chuẩn V2b A-T6 qua `chay_tham_do` THẬT (chạy GIẢ; chỉ giữ thăm dò dương + API — đối chứng Keychain/file của
    phần rút gọn không chạy trong test): chỉ 401/403 là bị chặn; lỗi hạ tầng không thành "đạt"; không chép đầu ra."""
    def chay(argv, **kw):
        kq = (ma, out, "curl: bi-mat") if "/usr/bin/curl" in argv else (0, "", "")
        return subprocess.CompletedProcess(argv, *kq)

    def chay_td(ds, **kw):
        return chay_tham_do([t for t in ds if t.kieu in ("ok", "http")], chay=chay, **kw)
    ch = cau_hinh(tmp_path, ("user:tram-k-1",))
    ra = cach_ly(ch, [], goc=tmp_path, goc_wt=tmp_path, dich=lambda: DichKiemAm(LOGIN, MAY_B, ()), chay_td=chay_td,
                 xac_minh=lambda *a: 600, chup=lambda: [])
    assert ra[0].muc_do == muc and ly in ra[0].chi_tiet and "bi-mat" not in ra[0].chi_tiet


def test_dau_do_that_lay_dich_tu_khach(monkeypatch):
    da = {}
    monkeypatch.setattr(kiem_cong, "cach_ly", lambda ch, du_an, **kw: da.update(kw) or [])
    khach = SimpleNamespace(ping=lambda: {}, du_an=lambda: [], kiem_am=lambda: DICH)
    dau_do_that(SimpleNamespace(), khach).cach_ly()
    assert da["dich"] is khach.kiem_am


@pytest.mark.parametrize("api, tren_b", [("http://127.0.0.1:7700", True), ("http://localhost:7700", True),
                                         ("https://may-b.tail.ts.net", False), ("https://127.0.0.1:7700", False)])
def test_chi_kiem_api_db_khi_tho_o_may_b(tmp_path, api, tren_b):
    """Review vòng 1 #5: đích (loopback, DB `127.0.0.1:…` của trạm) là theo máy B. Thợ ở máy khác (`tram_api` HTTPS)
    chưa có ánh xạ đích đã chứng minh, và 403 qua `tailscale serve` không chứng minh kênh ghi trên B đã tách → ĐỎ
    không kết luận, KHÔNG lấy đích, KHÔNG chạy curl/nc; phần rút gọn vẫn chạy."""
    ch, da, goi = replace(cau_hinh(tmp_path, ("user:tram-k-1",)), tram_api=api), [], []
    ra = cach_ly(ch, [], goc=tmp_path, goc_wt=tmp_path, dich=lambda: goi.append(1) or DICH, chay_td=ghi(da),
                 xac_minh=lambda *a: 600, chup=lambda: [])
    kieu = {t.kieu for t in da[0]["ds"]}
    assert (goi == [1]) is tren_b and ({"http", "nc"} <= kieu) is tren_b and "ok" in kieu
    assert [m.muc_do for m in ra] == ["xanh" if tren_b else "do"]
    assert ("không kết luận: thợ không ở máy B" in ra[0].chi_tiet) is not tren_b and ch.tren_may_b is tren_b
````

Sửa ba file test có sẵn (bản vá nguyên văn trên `cc1e4a5` = `d340a27` ở ba file này; không đổi so với bản trước; `test_tham_do_principal.py`: thêm `dich=` cho mọi lời gọi `cach_ly` và viết lại ca phía trạm theo D54; `test_kiem_cong.py`: thêm `dich=` và đòi có hai thăm dò mới; `test_chu_tho.py`: `rac` thành `[CHUYỂN]`, thêm ca chỉ có khe):

````diff
diff --git a/tests/test_chu_tho.py b/tests/test_chu_tho.py
index 81d2c55..aef5e6e 100644
--- a/tests/test_chu_tho.py
+++ b/tests/test_chu_tho.py
@@ -75,7 +75,9 @@ def test_kiem_cach_ly_du_bo_duoi_sudo_va_canh_bao_kenh_header(tram_home_tam):
         da["boc"], da["ten"] = boc(["/bin/cat", "x"]), [t.ten for t in ds]
         return [KetQuaThamDo(t.ten, "API" not in t.ten, "mã 0") for t in ds]
     van_ban, ma = kiem_cach_ly(["user:tram-k-b-claude-1", "rac"], chay_td=chay_td, xac_minh=lambda *a: 600)
-    assert ma == 1 and "header GIẢ ĐƯỢC" in van_ban and "[ĐỎ] rac:" in van_ban
+    assert ma == 1 and "header GIẢ ĐƯỢC" in van_ban and "[CHUYỂN] rac: kiểm cách ly khe bằng `tram tho kiem`" in van_ban
     assert da["boc"] == tu_cach_ly("user:tram-kiem").boc_lenh(["/bin/cat", "x"])      # đúng argv của kiểm lại (3c)
     assert "kết nối DB nghiệp vụ 127.0.0.1:3306" in da["ten"] and "[ĐỎ] user:tram-kiem — API Duyệt" in van_ban
     assert kiem_cach_ly([], doc_pk=lambda: None)[1] == 1
+    van_ban, ma = kiem_cach_ly(["user:tram-k-1"], doc_pk=lambda: None)                 # D54: chỉ khe → chưa kiểm gì
+    assert ma == 1 and "[CHUYỂN] user:tram-k-1" in van_ban and "Chưa có principal kiểm lại" in van_ban
diff --git a/tests/test_kiem_cong.py b/tests/test_kiem_cong.py
index 52b5ede..d78893e 100644
--- a/tests/test_kiem_cong.py
+++ b/tests/test_kiem_cong.py
@@ -5,6 +5,7 @@ from types import SimpleNamespace
 
 from tram.tho.cau_hinh import CauHinhTho, KheCauHinh
 from tram.tho.cau_hinh_chay import CauHinhChay
+from tram.tho.khach import DichKiemAm
 from tram.tho.kiem_am import KetQuaThamDo
 from tram.tho.kiem_cong import cach_ly, dang_nhap
 from tram.tho.kiem_may import DauDo, MucKiem, kiem_may
@@ -59,9 +60,11 @@ def test_cach_ly_xanh_khi_moi_tham_do_dat_do_khi_mot_cai_hong(tmp_path):
         da.append([t.ten for t in ds])
         return [KetQuaThamDo(t.ten, "Keychain" not in t.ten, "mã 0") for t in ds]
     ra = cach_ly(ch, ["hr-codex"], goc=tmp_path, goc_wt=tmp_path / "wt", chay_td=chay_td,
+                 dich=lambda: DichKiemAm("dai-ca@x", "b.ts.net", ("127.0.0.1:3306",)),
                  xac_minh=lambda ten, boc, kill: 600, chup=lambda: [])
     assert [m.muc_do for m in ra] == ["do", "do"] and "đọc Keychain tram-tho-token" in ra[0].chi_tiet
     assert f"sửa {tmp_path}/kho/hr-codex/.git/config" in da[0] and "chờ spike S6" in ra[1].chi_tiet
+    assert "API Duyệt với header danh tính giả" in da[0] and "kết nối DB nghiệp vụ 127.0.0.1:3306" in da[0]   # D54
 
 
 def test_kiem_may_dung_bo_kiem_that_khi_co(tmp_path):
diff --git a/tests/test_tham_do_principal.py b/tests/test_tham_do_principal.py
index e8d53bd..db01f17 100644
--- a/tests/test_tham_do_principal.py
+++ b/tests/test_tham_do_principal.py
@@ -1,14 +1,18 @@
 """bs-863.14: thăm dò cách ly của `tram tho kiem` và `tram chu kiem-cach-ly` CHỈ chạy sau khi UID thực của principal
 được chứng minh, qua `sudo -n` (không hỏi mật khẩu, không cần tty), `kill` của đúng principal, env dựng mới không HOME
-của quản lý. Không sudo/user thật: xác minh UID và chạy thăm dò đều GIẢ."""
+của quản lý. D54: khe chỉ kiểm ở `tram tho kiem`; `tram chu kiem-cach-ly` in [CHUYỂN] cho khe, kiểm `tram-kiem`.
+Không sudo/user thật: xác minh UID và chạy thăm dò đều GIẢ."""
 from test_kiem_cong import cau_hinh
 from tram.chu.kiem_cach_ly import kiem_cach_ly
 from tram.kiem.cay_tien_trinh import TienTrinh
 from tram.kiem.danh_tinh import LoiDanhTinh
 from tram.kiem.vong_doi import LoiThuHoi
+from tram.tho.khach import DichKiemAm
 from tram.tho.kiem_am import KetQuaThamDo
 from tram.tho.kiem_cong import cach_ly
 
+DICH = DichKiemAm("dai-ca@x", "b.ts.net", ())
+
 
 def ghi(da):
     def chay_td(ds, *, boc, env, kill):
@@ -20,7 +24,7 @@ def ghi(da):
 def test_tho_kiem_uid_truoc_roi_tham_do_voi_kill_va_env_cua_principal(tmp_path, monkeypatch):
     monkeypatch.setenv("HOME", "/Users/quan-ly")
     ch, da, xm = cau_hinh(tmp_path, ("user:tram-k-1",)), [], []
-    ra = cach_ly(ch, ["hr"], goc=tmp_path, goc_wt=tmp_path / "wt", chay_td=ghi(da),
+    ra = cach_ly(ch, ["hr"], goc=tmp_path, goc_wt=tmp_path / "wt", dich=lambda: DICH, chay_td=ghi(da),
                  xac_minh=lambda ten, boc, kill: xm.append(ten) or 600, chup=lambda: [])
     assert [m.muc_do for m in ra] == ["xanh"] and xm == ["tram-k-1"]
     assert da[0]["argv"][:5] == ["/usr/bin/sudo", "-n", "-H", "-u", "tram-k-1"] and da[0]["env"] == {
@@ -32,25 +36,27 @@ def test_tho_kiem_uid_chua_chung_minh_thi_do_va_khong_tham_do(tmp_path):
 
     def xm(ten, boc, kill):
         raise (LoiDanhTinh("x") if ten == "tram-k-1" else LoiThuHoi("y"))
-    ra = cach_ly(ch, [], goc=tmp_path, goc_wt=tmp_path, chay_td=ghi(da), xac_minh=xm)
+    ra = cach_ly(ch, [], goc=tmp_path, goc_wt=tmp_path, dich=lambda: DICH, chay_td=ghi(da), xac_minh=xm)
     assert [m.muc_do for m in ra] == ["do", "do"] and da == [] and "UID" in ra[0].chi_tiet
 
 
-def test_chu_kiem_cach_ly_sudo_n_kill_principal_va_uid_truoc(tram_home_tam):
+def test_chu_kiem_cach_ly_khe_chuyen_tram_kiem_van_uid_truoc(tram_home_tam):
+    """D54: tài khoản trạm KHÔNG `sudo -n` sang khe (không chạy gì dưới khe, không dò UID khe) — in [CHUYỂN], không tính
+    vào mã thoát; `tram-kiem` vẫn UID trước, `kill` của principal, env dựng mới."""
     tram_home_tam.mkdir(parents=True, exist_ok=True)
     (tram_home_tam / "cau-hinh.yaml").write_text("cach_ly: {tram_kiem: user:tram-kiem}\n")
     da, xm = [], []
+    van_ban, ma = kiem_cach_ly(["user:tram-k-b-claude-1", "sandbox:tram-exec"], chay_td=ghi(da),
+                               xac_minh=lambda ten, boc, kill: xm.append(ten))
+    assert xm == ["tram-kiem"] and len(da) == 1 and da[0]["kill"].__self__.ten == "tram-kiem" and ma == 0
+    assert "tram-k-b-claude-1" not in da[0]["argv"] and set(da[0]["env"]) == {"PATH", "LANG"}
+    assert "[CHUYỂN] user:tram-k-b-claude-1: kiểm cách ly khe bằng `tram tho kiem`" in van_ban
+    assert "[CHUYỂN] sandbox:tram-exec:" in van_ban
 
     def xac_minh(ten, boc, kill):
-        xm.append(ten)
-        if ten == "tram-exec":
-            raise LoiDanhTinh("x")
-    van_ban, ma = kiem_cach_ly(["user:tram-k-b-claude-1", "sandbox:tram-exec"], chay_td=ghi(da), xac_minh=xac_minh)
-    assert xm == ["tram-k-b-claude-1", "tram-exec", "tram-kiem"] and len(da) == 2
-    assert da[0]["argv"][:5] == ["/usr/bin/sudo", "-n", "-H", "-u", "tram-k-b-claude-1"]
-    assert da[0]["kill"].__self__.user == "tram-k-b-claude-1" and da[1]["kill"].__self__.ten == "tram-kiem"
-    assert "[ĐỎ] sandbox:tram-exec: UID" in van_ban and ma == 1
-    assert all(set(d["env"]) == {"PATH", "LANG"} for d in da)
+        raise LoiDanhTinh("x")
+    van_ban, ma = kiem_cach_ly([], chay_td=ghi(da), xac_minh=xac_minh)
+    assert "[ĐỎ] user:tram-kiem: UID" in van_ban and ma == 1 and len(da) == 1
 
 
 
@@ -58,9 +64,9 @@ def test_tho_kiem_con_tien_trinh_cua_principal_sau_tham_do_thi_do_khong_giet(tmp
     """A02: chỉ quan sát — bảng tiến trình còn tiến trình của UID principal → ĐỎ; không gửi tín hiệu nào."""
     ch, da = cau_hinh(tmp_path, ("user:tram-k-1",)), []
     con = [TienTrinh(7000, 1, 7000, 600, 600, 1)]
-    ra = cach_ly(ch, [], goc=tmp_path, goc_wt=tmp_path / "wt", chay_td=ghi(da), xac_minh=lambda *a: 600,
-                 chup=lambda: con)
+    ra = cach_ly(ch, [], goc=tmp_path, goc_wt=tmp_path / "wt", dich=lambda: DICH, chay_td=ghi(da),
+                 xac_minh=lambda *a: 600, chup=lambda: con)
     assert [m.muc_do for m in ra] == ["do"] and "còn 1 tiến trình của principal" in ra[0].chi_tiet
-    ra = cach_ly(ch, [], goc=tmp_path, goc_wt=tmp_path / "wt", chay_td=ghi(da), xac_minh=lambda *a: 600,
-                 chup=lambda: (_ for _ in ()).throw(OSError("sysctl")))
+    ra = cach_ly(ch, [], goc=tmp_path, goc_wt=tmp_path / "wt", dich=lambda: DICH, chay_td=ghi(da),
+                 xac_minh=lambda *a: 600, chup=lambda: (_ for _ in ()).throw(OSError("sysctl")))
     assert [m.muc_do for m in ra] == ["do"] and "không đọc được bảng tiến trình" in ra[0].chi_tiet
````

- [ ] **Step 2: Chạy test, thấy đỏ**

```bash
tests/chan_host/chay.sh -q tests/test_kiem_khe_d54.py tests/test_tham_do_principal.py tests/test_kiem_cong.py tests/test_chu_tho.py
```

Kết quả THẬT (18/10, đo lại trên `d340a27` + test của bản sửa):

```
E   ImportError: cannot import name 'DichKiemAm' from 'tram.tho.khach' (.../tram/tho/khach.py)
ERROR tests/test_kiem_khe_d54.py
ERROR tests/test_tham_do_principal.py
ERROR tests/test_kiem_cong.py
!!!!!!!!!!!!!!!!!!! Interrupted: 3 errors during collection !!!!!!!!!!!!!!!!!!!!
3 errors in 1.36s
=== nhật ký chặn …: 0 dòng mới; điểm mù (Python con không mang bộ chặn): 0; push giả lập (không push thật): 0
```

Riêng phía trạm (`tests/chan_host/chay.sh -q tests/test_chu_tho.py`), đỏ đúng hành vi cũ — khe còn bị chạy thăm dò qua `sudo -n` và `rac` ra ĐỎ:

```
E       AssertionError: assert (1 == 1 and 'header GIẢ ĐƯỢC' in 'Kênh ghi dashboard: header  (header GIẢ ĐƯỢC — chưa đạt §4 mục 2b)\n[XANH] user:tram-k-b-claude-1 — đọc Keychain tram...ram-kiem — tram khi xoá TRAM_GIAO_ID, trỏ kho trạm: mã 0\n[XANH] user:tram-kiem — git hook trong repo không chạy: mã 0' and '[CHUYỂN] rac: kiểm cách ly khe bằng `tram tho kiem`' in …)
1 failed, 3 passed in 0.75s
```

RED riêng của các sửa sau review vòng 1, đo trên mã V4-1 của bản vòng 1 (đã có `DichKiemAm`) + test bản sửa:
- #5 (`tests/chan_host/chay.sh -q tests/test_kiem_khe_d54.py`): `4 failed, 13 passed in 1.12s` — ca HTTPS: `assert (([1] == [1] …) is False)` (vẫn lấy đích và chạy curl/nc khi thợ không ở máy B); ca loopback: `AttributeError: 'CauHinhTho' object has no attribute 'tren_may_b'`.
- #6 (sửa `_khop` của Codex): đặt lại `_khop` cũ (`x is None or …`) → `5 failed` cùng file, `Failed: DID NOT RAISE <class 'tram.tho.khach.LoiKhachTram'>`; `_khop` mới → xanh.
- #8 (401 token sai / danh tính Đại ca không Bearer): xanh ngay trên mã vòng 1 — router `tho_them` đã kế thừa `Depends(may_cua_yeu_cau)`; assertion là lưới canh, không phải sửa lỗi.

- [ ] **Step 3: Viết mã**

Bản vá nguyên văn trên `d340a27` (7 file `tram/`):

````diff
diff --git a/tram/api/tho_them.py b/tram/api/tho_them.py
index 84731b8..2ea3a68 100644
--- a/tram/api/tho_them.py
+++ b/tram/api/tho_them.py
@@ -1,7 +1,10 @@
 """`/api/tho/*` thêm ở lát 3a-2 (spec 3 §6.4, §7.1) — cùng xác thực token máy với `tram/api/tho.py`:
 - `POST /api/tho/da-push {khe_id, giao_id, luot, commit, ref_tam, request_id}` → công bố (trả `{cong_bo, commit?, ref?,
   ly_do?}`; 503 `{ly_do: chua-chot-phuong-an | chua-co-kho-tram}`; 422 `{ly_do: ref-tam-sai}`; lỗi chung như tho.py);
-- `POST /api/tho/da-dong {bead: [{du_an, bead_id}]}` → `{dong: [...]}` các bead đã có `bead.dong` (thợ dọn worktree).
+- `POST /api/tho/da-dong {bead: [{du_an, bead_id}]}` → `{dong: [...]}` các bead đã có `bead.dong` (thợ dọn worktree);
+- `GET /api/tho/kiem-am` → `{dai_ca_login, may_b, db_nghiep_vu}` (D54): đích của hai thăm dò khe trong `tram tho kiem`,
+  lấy từ CHÍNH cấu hình trạm dùng để kiểm ghi (login Đại ca đầu tiên, `ten_may_b` cho Origin) và `cach_ly.db_nghiep_vu`;
+  503 `{ly_do: cach-ly-sai}`. Không chứa bí mật.
 Cấu hình công bố đọc mỗi yêu cầu từ `~/.tram/cau-hinh.yaml` (`app.state.cong_bo` thay được trong test)."""
 from contextlib import closing
 
@@ -10,6 +13,7 @@ from fastapi.responses import JSONResponse
 from pydantic import BaseModel, ConfigDict, Field
 
 from tram.api.tho import _chay, may_cua_yeu_cau
+from tram.cau_hinh.cach_ly import nap_cau_hinh_cach_ly
 from tram.cau_hinh.cong_bo import nap_cau_hinh_cong_bo
 from tram.cong_bo.da_push import ChuaCongBoDuoc, RefTamSai, ThanDaPush, nhan_da_push
 from tram.cong_bo.nguon import chon_nguon
@@ -59,3 +63,14 @@ def da_dong(than: ThanDaDong, request: Request) -> dict:
             "SELECT 1 FROM su_kien WHERE du_an = ? AND bead_id = ? AND loai = 'bead.dong' LIMIT 1",
             (b.du_an, b.bead_id)).fetchone()]
     return {"dong": dong}
+
+
+@router.get("/kiem-am")
+def kiem_am(request: Request):
+    ch = request.app.state.pt.cau_hinh
+    try:
+        db = list(nap_cau_hinh_cach_ly().db_nghiep_vu)
+    except ValueError:
+        return JSONResponse({"ly_do": "cach-ly-sai"}, status_code=503)
+    return {"dai_ca_login": ch.dai_ca_logins[0] if ch.dai_ca_logins else None, "may_b": ch.ten_may_b,
+            "db_nghiep_vu": db}
diff --git a/tram/chu/kiem_cach_ly.py b/tram/chu/kiem_cach_ly.py
index 0da11e1..c16bb19 100644
--- a/tram/chu/kiem_cach_ly.py
+++ b/tram/chu/kiem_cach_ly.py
@@ -1,10 +1,11 @@
 """`tram chu kiem-cach-ly` (spec 3 §7.3 mục 7, H9; spec 2 §4 mục 2b) — chạy ở TÀI KHOẢN TRẠM: bộ kiểm chứng âm ĐỦ dưới
-từng principal khe và dưới `tram-kiem` (`sudo -u`, có thể hỏi mật khẩu). Biết `dai_ca_logins` thật nên thăm dò "API
-Duyệt với header danh tính giả" mang đúng login của Đại ca: chỉ bị chặn khi kênh ghi thật sự tách (`cach_ly.kenh_ghi`).
-Mã thoát 1 nếu có thăm dò không đạt; KHÔNG có fixture nào làm nó xanh. Lát 3c: `tram-kiem` đọc từ MỘT nguồn
-(`doc_principal_kiem` — `cach_ly.tram_kiem`) và thăm dò chạy qua ĐÚNG argv lúc kiểm lại (`PrincipalKiem.boc_lenh`).
-bs-863.14: principal khe qua `Principal.boc` (`sudo -n` — KHÔNG hỏi mật khẩu, không cần tty: thiếu dòng sudoers thì
-thăm dò dương hỏng → ĐỎ, không treo), mọi thăm dò qua P1 với `kill` của principal, UID thực chứng minh TRƯỚC."""
+`tram-kiem` (principal kiểm lại, một nguồn `doc_principal_kiem` — `cach_ly.tram_kiem`; thăm dò qua ĐÚNG argv lúc kiểm
+lại `PrincipalKiem.boc_lenh`, P1 với `kill` của principal, UID thực chứng minh TRƯỚC). Biết `dai_ca_logins` thật nên
+thăm dò "API Duyệt với header danh tính giả" mang đúng login của Đại ca: chỉ bị chặn khi kênh ghi thật sự tách
+(`cach_ly.kenh_ghi`). Mã thoát 1 nếu có thăm dò không đạt; KHÔNG có fixture nào làm nó xanh.
+D54 (18/10): trạm KHÔNG được chạy thay khe (không sudoers trạm → khe). `--principal` của khe chỉ in [CHUYỂN] chỉ sang
+`tram tho kiem` — tài khoản quản lý thợ chạy kiểm chứng âm của khe, gồm API Duyệt giả danh và DB nghiệp vụ, dưới
+CHÍNH principal khe; mục [CHUYỂN] không phải kết quả kiểm nên không tính vào mã thoát."""
 import os
 import tempfile
 from pathlib import Path
@@ -18,35 +19,27 @@ from tram.cau_hinh.tram import nap_cau_hinh_tram
 from tram.duong_dan import tram_home
 from tram.tho.kiem_am import chay_tham_do, tham_do_day_du, tham_do_khe
 from tram.tho.kiem_cong import KEYCHAIN_CAM
-from tram.tho.principal import ChuaCoPrincipal, Principal, doc_principal
 
+CHUYEN = "kiểm cách ly khe bằng `tram tho kiem` dưới tài khoản quản lý thợ (D54) — lệnh này không chạy thay khe"
 
-def _ds_boc(principal: list[str], doc_pk) -> list[tuple[str, object]]:
-    """(nhãn, (tên, boc, kill) | lỗi): principal khe như user thường (không hồ sơ lượt — như trước) qua `sudo -n`;
-    `tram-kiem` qua đúng argv và kill của kiểm lại."""
-    ds: list[tuple[str, object]] = []
-    for chuoi in principal:
-        try:
-            p = Principal("user", doc_principal(chuoi).user)
-            ds.append((chuoi, (p.user, p.boc, p.kill_nhom)))
-        except ChuaCoPrincipal as e:
-            ds.append((chuoi, e))
+
+def _ds_kiem(doc_pk) -> list[tuple[str, object]]:
+    """(nhãn, (tên, boc, kill) | lỗi) của `tram-kiem` — qua đúng argv và kill của kiểm lại."""
     try:
         pk = doc_pk()
-        ds += [(f"{pk.co_che}:{pk.ten}", (pk.ten, pk.boc_lenh, pk.kill_nhom))] if pk else []
+        return [(f"{pk.co_che}:{pk.ten}", (pk.ten, pk.boc_lenh, pk.kill_nhom))] if pk else []
     except ValueError as e:
-        ds.append(("cach_ly.tram_kiem", e))
-    return ds
+        return [("cach_ly.tram_kiem", e)]
 
 
 def kiem_cach_ly(principal: list[str], *, chay_td=chay_tham_do, doc_pk=doc_principal_kiem,
                  xac_minh=xac_minh_uid) -> tuple[str, int]:
     ch, cl = nap_cau_hinh_tram(), nap_cau_hinh_cach_ly()
-    ds = _ds_boc(principal, doc_pk)
+    chuyen, ds = [f"[CHUYỂN] {chuoi}: {CHUYEN}" for chuoi in principal], _ds_kiem(doc_pk)
     if not ds:
-        return "Chưa có principal nào để kiểm (--principal / cach_ly.tram_kiem) — chờ S6.", 1
+        return "\n".join([*chuyen, "Chưa có principal kiểm lại ở tài khoản trạm (cach_ly.tram_kiem) — chờ S6."]), 1
     dong, ma = [f"Kênh ghi dashboard: {cl.kenh_ghi}" + ("  (header GIẢ ĐƯỢC — chưa đạt §4 mục 2b)"
-                                                       if cl.kenh_ghi == "header" else "")], 0
+                                                       if cl.kenh_ghi == "header" else ""), *chuyen], 0
     for chuoi, pr in ds:
         if not isinstance(pr, Exception):
             try:
diff --git a/tram/chu/lenh_tho.py b/tram/chu/lenh_tho.py
index c8f945c..60b876b 100644
--- a/tram/chu/lenh_tho.py
+++ b/tram/chu/lenh_tho.py
@@ -90,8 +90,9 @@ def them_lenh_chu_tho(chu) -> None:
     t.add_argument("may_id")
     t.add_argument("--dong-y", action="store_true")
     t.set_defaults(ham=_cap_token_may)
-    k = chu.add_parser("kiem-cach-ly", help="Kiểm chứng âm H9 dưới từng principal khe và cach_ly.tram_kiem (sudo)")
-    k.add_argument("--principal", action="append", default=[], help="user:<tên> | sandbox:<tên>, lặp lại")
+    k = chu.add_parser("kiem-cach-ly", help="Kiểm chứng âm H9 dưới cach_ly.tram_kiem; khe: `tram tho kiem` (D54)")
+    k.add_argument("--principal", action="append", default=[],
+                   help="principal khe user:<tên> | sandbox:<tên> — chỉ in hướng dẫn sang `tram tho kiem` (D54)")
     k.set_defaults(ham=_kiem_cach_ly)
     g = chu.add_parser("go-cai-dat-tho", help="Gỡ đúng thứ cai-dat-tho đã tạo theo sổ (chờ dong-y)")
     g.add_argument("--xoa-nha", action="store_true", help="Xoá luôn thư mục nhà của user (mặc định giữ)")
diff --git a/tram/tho/cau_hinh.py b/tram/tho/cau_hinh.py
index 73e9171..bc9b53c 100644
--- a/tram/tho/cau_hinh.py
+++ b/tram/tho/cau_hinh.py
@@ -38,6 +38,11 @@ class CauHinhTho:
     def khe_id(self, k: KheCauHinh) -> str:
         return f"{self.may_id}/{k.ten}"
 
+    @property
+    def tren_may_b(self) -> bool:
+        """`tram_api` loopback (đã qua `API_RE`) = quản lý thợ chạy trên CHÍNH máy B — tram-api chỉ nghe 127.0.0.1."""
+        return self.tram_api.startswith(("http://127.0.0.1:", "http://localhost:"))
+
 
 def _khe(raw: object) -> KheCauHinh:
     if not isinstance(raw, dict) or set(raw) - KHOA_KHE:
diff --git a/tram/tho/khach.py b/tram/tho/khach.py
index ca97c70..94e8715 100644
--- a/tram/tho/khach.py
+++ b/tram/tho/khach.py
@@ -2,13 +2,17 @@
 QUẢN LÝ THỢ (`tram-tho-token` — tạo ở bước cài của 3a-2, sau spike S6); không in, không ghi file, không đưa vào môi
 trường CLI của khe."""
 import json
+import re
 import urllib.error
 import urllib.request
 from dataclasses import dataclass, field
 
+from tram.cau_hinh.cach_ly import DIA_CHI_RE
 from tram.keychain import doc_muc
 
 KEYCHAIN_THO = "tram-tho-token"
+LOGIN_RE = re.compile(r"[!-~]{1,320}")                   # ASCII in được, không khoảng trắng/xuống dòng (đi vào header)
+MAY_B_RE = re.compile(r"[A-Za-z0-9.-]{1,253}")
 
 
 class LoiKhachTram(RuntimeError):
@@ -19,6 +23,18 @@ def doc_token_may(*, chay=None) -> str | None:
     return doc_muc(KEYCHAIN_THO, chay=chay)
 
 
+@dataclass(frozen=True)
+class DichKiemAm:
+    """Đích hai thăm dò khe của `tram tho kiem` do trạm cấp (D54) — đã kiểm dạng trước khi vào argv thăm dò."""
+    dai_ca_login: str
+    may_b: str
+    db_nghiep_vu: tuple[str, ...]
+
+
+def _khop(x, mau: re.Pattern) -> bool:
+    return isinstance(x, str) and mau.fullmatch(x) is not None
+
+
 @dataclass
 class KhachTram:
     url: str
@@ -56,3 +72,13 @@ class KhachTram:
         if ma != 200:
             raise LoiKhachTram(f"tram-api trả {ma}")
         return [d["ten"] for d in kq.get("du_an", [])]
+
+    def kiem_am(self) -> DichKiemAm:
+        ma, kq = self.goi("GET", "/api/tho/kiem-am")
+        if ma != 200:
+            raise LoiKhachTram(f"tram-api trả {ma}")
+        db = kq.get("db_nghiep_vu") if isinstance(kq, dict) else None
+        if not (isinstance(db, list) and all(isinstance(d, str) and DIA_CHI_RE.fullmatch(d) for d in db)
+                and _khop(kq.get("dai_ca_login"), LOGIN_RE) and _khop(kq.get("may_b"), MAY_B_RE)):
+            raise LoiKhachTram("tram-api trả đích kiểm chứng âm sai dạng")
+        return DichKiemAm(kq.get("dai_ca_login"), kq.get("may_b"), tuple(db))
diff --git a/tram/tho/kiem_am.py b/tram/tho/kiem_am.py
index ac04976..3f2327d 100644
--- a/tram/tho/kiem_am.py
+++ b/tram/tho/kiem_am.py
@@ -56,16 +56,23 @@ def tham_do_khe(*, keychain: list[str], doc_cam: list[Path], ghi_cam: list[Path]
                  ThamDo(f"ghi được {ghi_duoc}", ["/usr/bin/touch", str(ghi_duoc / ".tram-kiem-duong")], "ok")]
 
 
-def tham_do_day_du(*, rut_gon: list[ThamDo], api: str, dai_ca_login: str, may_b: str, db: list[str],
-                   tram_home_tram: Path | None, mo: Callable[[str], bool] = mo_cong) -> list[ThamDo]:
-    """Bộ đủ §7.3 mục 7: + gọi API Duyệt với header danh tính giả, kết nối DB nghiệp vụ, `tram` khi xoá
-    `TRAM_GIAO_ID` trỏ vào kho của trạm, git hook trong repo."""
-    ds = list(rut_gon) + [ThamDo("API Duyệt với header danh tính giả", [
+def tham_do_api_db(*, api: str, dai_ca_login: str, may_b: str, db: list[str],
+                   mo: Callable[[str], bool] = mo_cong) -> list[ThamDo]:
+    """Gọi API Duyệt với header danh tính giả (login THẬT của Đại ca + Origin máy B: chỉ bị chặn khi kênh ghi thật sự
+    tách) và kết nối DB nghiệp vụ — chung cho `tram chu kiem-cach-ly` (`tram-kiem`) và `tram tho kiem` (khe, D54)."""
+    ds = [ThamDo("API Duyệt với header danh tính giả", [
-        "/usr/bin/curl", "-s", "-m", "10", "-o", "/dev/null", "-w", "%{http_code}", "-X", "POST",
+        "/usr/bin/curl", "-q", "-s", "-m", "10", "-o", "/dev/null", "-w", "%{http_code}", "-X", "POST",
         "-H", "Content-Type: application/json", "-H", f"Tailscale-User-Login: {dai_ca_login}", "-H", "X-Tram: 1",
         "-H", f"Origin: https://{may_b}", "--data", "{}", f"{api}/api/phe-duyet/kiem-am/kiem-am/duyet"], "http")]
-    ds += [ThamDo(f"kết nối DB nghiệp vụ {d}", ["/usr/bin/nc", "-z", "-G", "3", *d.rsplit(":", 1)], "nc",
-                  partial(mo, d)) for d in db]
+    return ds + [ThamDo(f"kết nối DB nghiệp vụ {d}", ["/usr/bin/nc", "-z", "-G", "3", *d.rsplit(":", 1)], "nc",
+                        partial(mo, d)) for d in db]
+
+
+def tham_do_day_du(*, rut_gon: list[ThamDo], api: str, dai_ca_login: str, may_b: str, db: list[str],
+                   tram_home_tram: Path | None, mo: Callable[[str], bool] = mo_cong) -> list[ThamDo]:
+    """Bộ đủ §7.3 mục 7: + API Duyệt giả danh, DB nghiệp vụ (`tham_do_api_db`), `tram` khi xoá `TRAM_GIAO_ID` trỏ vào
+    kho của trạm, git hook trong repo."""
+    ds = list(rut_gon) + tham_do_api_db(api=api, dai_ca_login=dai_ca_login, may_b=may_b, db=db, mo=mo)
     if tram_home_tram is not None:
         ds.append(ThamDo("tram khi xoá TRAM_GIAO_ID, trỏ kho trạm", [
             "/usr/bin/env", "-u", "TRAM_GIAO_ID", f"TRAM_HOME={tram_home_tram}", "tram", "chu", "trang-thai"], "tram",
diff --git a/tram/tho/kiem_cong.py b/tram/tho/kiem_cong.py
index 8e08821..6ffad64 100644
--- a/tram/tho/kiem_cong.py
+++ b/tram/tho/kiem_cong.py
@@ -4,8 +4,11 @@ gọn §7.3 mục 7 (Keychain/token máy, thư mục tiến trình quản lý, h
 `.git/hooks` của kho) + hai thăm dò dương. Principal chưa khai/sai → đỏ. bs-863.14: UID thực của principal chứng minh
 TRƯỚC (`xac_minh_uid`); thăm dò qua P1 với `kill` của principal, env dựng mới chỉ PATH/LANG (không HOME của quản lý).
 Review vòng 1 A02: thăm dò xong mà bảng tiến trình của nhân còn tiến trình của UID principal → ĐỎ (CHỈ QUAN SÁT, không
-giết: có thể `tram tho chay` đang chạy phiếu — sổ tay: dừng nó trước khi kiểm)."""
+giết: có thể `tram tho chay` đang chạy phiếu — sổ tay: dừng nó trước khi kiểm). D54 (18/10): thêm hai thăm dò "API
+Duyệt giả danh Đại ca" và "kết nối DB nghiệp vụ" dưới CHÍNH principal khe (trạm không chạy thay khe); đích do trạm cấp
+(`KhachTram.kiem_am`); thợ không ở máy B hay không lấy được đích → ĐỎ "không kết luận", phần rút gọn vẫn chạy."""
 import subprocess
+from collections.abc import Callable
 from pathlib import Path
 
 from tram.kiem import danh_tinh
@@ -15,7 +18,8 @@ from tram.kiem.vong_doi import LoiThuHoi
 
 from tram.tho.cau_hinh import CauHinhTho, KheCauHinh
 from tram.tho.don_uid import con_lai
-from tram.tho.kiem_am import KetQuaThamDo, chay_tham_do, tham_do_khe
+from tram.tho.khach import DichKiemAm, LoiKhachTram
+from tram.tho.kiem_am import KetQuaThamDo, ThamDo, chay_tham_do, tham_do_api_db, tham_do_khe
 from tram.tho.kiem_may import DauDo, MucKiem
 from tram.tho.principal import ChuaCoPrincipal
 from tram.tho.principal_khe import principal_cua
@@ -62,9 +66,23 @@ def _tan_du(uid: int, chup) -> list[KetQuaThamDo]:
                                           "(dừng `tram tho chay` rồi kiểm lại)")] if n else []
 
 
-def cach_ly(ch: CauHinhTho, du_an: list[str], *, goc: Path, goc_wt: Path, chay_td=chay_tham_do,
-            xac_minh=danh_tinh.xac_minh_uid, chup=chup_nhan) -> list[MucKiem]:
-    ra = []
+def _api_db(ch: CauHinhTho, dich: Callable[[], DichKiemAm]) -> tuple[list[ThamDo], list[KetQuaThamDo]]:
+    """(thăm dò API Duyệt + DB nghiệp vụ, lỗi) — đích lấy MỘT lần từ trạm cho mọi khe. Đích (loopback, DB của trạm)
+    theo máy B: thợ máy khác chưa có ánh xạ đích đã chứng minh, 403 qua proxy không chứng minh kênh ghi tách → bỏ."""
+    if not ch.tren_may_b:
+        ly = "không kết luận: thợ không ở máy B (tram_api không phải loopback) — D54 lát này chỉ kiểm trên máy B"
+        return [], [KetQuaThamDo("API Duyệt + DB nghiệp vụ", False, ly)]
+    try:
+        d = dich()
+    except LoiKhachTram as e:
+        return [], [KetQuaThamDo("API Duyệt + DB nghiệp vụ", False,
+                                 f"không kết luận: không lấy được đích từ tram-api ({type(e).__name__})")]
+    return tham_do_api_db(api=ch.tram_api, dai_ca_login=d.dai_ca_login, may_b=d.may_b, db=list(d.db_nghiep_vu)), []
+
+
+def cach_ly(ch: CauHinhTho, du_an: list[str], *, goc: Path, goc_wt: Path, dich: Callable[[], DichKiemAm],
+            chay_td=chay_tham_do, xac_minh=danh_tinh.xac_minh_uid, chup=chup_nhan) -> list[MucKiem]:
+    ra, (them, loi_dich) = [], _api_db(ch, dich)
     for k in ch.khe:
         kid = ch.khe_id(k)
         try:
@@ -84,8 +102,8 @@ def cach_ly(ch: CauHinhTho, du_an: list[str], *, goc: Path, goc_wt: Path, chay_t
                          ghi_cam=[*(goc / "hang-doi" / ch.may_id / x.ten for x in khac),
                                   *(x.thu_muc_cau_hinh for x in khac), *(g / "hooks" for g in kho)],
                          ghi_duoc=goc / "hang-doi" / ch.may_id / k.ten, ghi_tep_cam=[g / "config" for g in kho])
-        kq = chay_td(ds, boc=p.boc, env={"PATH": ch.chay.path_cli, "LANG": "C.UTF-8"}, kill=p.kill_nhom)
-        hong = [x for x in kq if not x.dat] + _tan_du(uid, chup)
+        kq = chay_td(ds + them, boc=p.boc, env={"PATH": ch.chay.path_cli, "LANG": "C.UTF-8"}, kill=p.kill_nhom)
+        hong = [x for x in kq if not x.dat] + loi_dich + _tan_du(uid, chup)
         ra.append(MucKiem(f"{kid} cách ly", "do" if hong else "xanh",
                           "; ".join(f"{x.ten}: {x.chi_tiet}" for x in hong) or f"{len(kq)} thăm dò đạt"))
     return ra
@@ -97,4 +115,4 @@ def dau_do_that(ch: CauHinhTho, khach) -> DauDo:
     goc, goc_wt = tram_home(), Path.home() / "tram" / "worktrees"
     return DauDo(ping=khach.ping, du_an=khach.du_an,
                  dang_nhap=lambda k: dang_nhap(ch, k, goc=goc, goc_wt=goc_wt),
-                 cach_ly=lambda: cach_ly(ch, khach.du_an(), goc=goc, goc_wt=goc_wt))
+                 cach_ly=lambda: cach_ly(ch, khach.du_an(), goc=goc, goc_wt=goc_wt, dich=khach.kiem_am))
````

- [ ] **Step 4: Chạy test, thấy xanh**

```bash
tests/chan_host/chay.sh -q tests/test_kiem_khe_d54.py tests/test_tham_do_principal.py tests/test_kiem_cong.py \
  tests/test_chu_tho.py tests/test_kiem_am.py tests/test_cham_tham_do.py tests/test_tho_lenh_chay.py tests/test_api_tho.py \
  tests/test_api_tho_them.py tests/test_tho_lenh.py tests/test_do_dai_ma.py tests/test_vong_import.py
```

Kết quả THẬT (bản sửa, `d340a27`): `91 passed in 5.08s`; nhật ký chặn 0 dòng mới; điểm mù 0; push giả lập 9.

- [ ] **Step 5: Sổ tay — bước G5.6 (D54)**

````diff
diff --git a/docs/handovers/2026-10-15-so-tay-chay-that.md b/docs/handovers/2026-10-15-so-tay-chay-that.md
index faa1a86..225d183 100644
--- a/docs/handovers/2026-10-15-so-tay-chay-that.md
+++ b/docs/handovers/2026-10-15-so-tay-chay-that.md
@@ -157,10 +157,11 @@ Nguồn: plan bs-78r.10, mục "Gate", G5 mục 1–5. Mã: `tram/tho/han_muc_ra
 | G5.3 — đúng UID | Trong lúc G5.2 chạy, cửa sổ 2: `ps -A -o uid=,ruid=,pid=,command= \| grep '[a]pp-server'` (lặp vài lần); sau khi xong: `ps -A -o uid=,pid=,comm= \| awk -v u=$(id -u $UK) '$1==u'` | khi thấy, cột uid = `id -u $UK`; sau khi xong: rỗng | app-server chạy dưới UID quản lý; còn tiến trình của khe sau khi xong | `sudo -n -u $UK /bin/kill -KILL -1` |
 | G5.4 — không lộ token | `S=g5-sentinel-$(date +%s); OPENAI_API_KEY=$S uv run tram tho kiem > ~/.tram/g5/kiem-sentinel.txt 2>&1; grep -rl "$S" ~/.tram/g5 ~/.tram/log` | không file nào chứa sentinel | sentinel hiện ra → **dừng**, không chạy tiếp G5 | xoá file log chứa sentinel (không phải bí mật thật) |
 | G5.5 — treo/nhịp (sau S2, khi `tram tho chay` chạy được dưới `vn.tram.tho`) | Theo dõi một chu kỳ quota: `ps -U $UK` sau mỗi nhịp; xem nhịp tim ở trạm (`uv run tram chu trang-thai` hoặc dashboard) | sau thu hồi không còn tiến trình dưới `$UK`; nhịp kế tiếp tới trạm trong 90 s | khe bị dừng vì `LoiThuHoi` lặp lại; nhịp trễ > 90 s | dừng `vn.tram.tho` theo sổ tay S2 |
+| G5.6 — khe: API Duyệt giả danh + DB nghiệp vụ (D54; chỉ quản lý thợ trên máy B, `tram_api` loopback) | Dừng `tram tho chay` (D55). `uv run tram tho kiem > ~/.tram/g5/kiem-d54.txt 2>&1; echo $?`; `grep -n "cách ly" ~/.tram/g5/kiem-d54.txt` | mục "`$KHE` cách ly" có kết luận cho "API Duyệt với header danh tính giả" và mỗi DB trong `cach_ly.db_nghiep_vu` của trạm: kênh `unix-socket` → không có trong phần hỏng (HTTP 403, nc bị từ chối quyền); kênh `header` → ĐỎ "API nhận yêu cầu" là kết quả đúng (D51, chưa đạt kênh tách) | "không lấy được đích từ tram-api" (trạm chưa có `/api/tho/kiem-am`, token sai, hay trạm chưa khai `dai_ca_logins`/`ten_may_b`), "thợ không ở máy B", hoặc "không kết luận" cho API/DB → dừng, báo Em | — |
 
 Hồ sơ sandbox `han-muc.sb` (G5 mục 3 của plan) chỉ thử khi chạy cơ chế `sandbox`. Hiện chỉ cơ chế `user` (D3, D53) — bỏ qua.
 
-**Đạt G5:** G5.0–G5.4 đạt; G5.5 đạt khi có S2. Đạt mới mở S5 và S6 có Codex.
+**Đạt G5:** G5.0–G5.4 và G5.6 đạt (D54: hai thăm dò API/DB chạy được dưới đúng principal khe); G5.5 đạt khi có S2. Đạt mới mở S5 và S6 có Codex.
 
 ## G6 — 4D-4: skill máy A → API máy B thật
 
````

- [ ] **Step 6: Chạy cả bộ** — `tests/chan_host/chay.sh -q` → kết quả THẬT trên `d340a27` + V4-1 bản sửa: **`3253 passed in 347.63s`** (N₀ + 17), nhật ký chặn 0 dòng mới, điểm mù 48, push giả lập 629. (Nếu V4-2 đã ghép trước: 3258.)

- [ ] **Step 7: Commit**

```bash
git add tram/api/tho_them.py tram/tho/cau_hinh.py tram/tho/khach.py tram/tho/kiem_am.py tram/tho/kiem_cong.py tram/chu/kiem_cach_ly.py \
  tram/chu/lenh_tho.py tests/test_kiem_khe_d54.py tests/test_tham_do_principal.py tests/test_kiem_cong.py \
  tests/test_chu_tho.py docs/handovers/2026-10-15-so-tay-chay-that.md
git commit -m "fix(tho): kiểm API Duyệt giả danh + DB nghiệp vụ của khe trong tram tho kiem; trạm in [CHUYỂN] (D54, bs-2bd.1.25)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

### Task V4-2: pytest từ chối chạy khi không qua `tests/chan_host/chay.sh` (D61, bs-2bd.1.26)

**Files:** như bảng trên.

**Interfaces:**
- `tests/chan_host/chay.sh` đặt thêm `TRAM_CHAN_CHAY_SH=1` cho tiến trình pytest (và mọi con cháu — kể cả `chay.sh` lồng trong test).
- `tests/conftest.py`: `GIT_GIA`, `HUONG_DAN`, `pytest_configure(config)` — thiếu một trong: `TRAM_CHAN_CHAY_SH == "1"`, `config.pluginmanager.has_plugin("chan_host")`, `realpath(shutil.which("git")) == tests/chan_host/bin/git` → `pytest.exit(HUONG_DAN, returncode=4)`. `pytest --version` không qua `pytest_configure` (không thu thập gì) nên không bị chặn — vô hại.

- [ ] **Step 0: Kiểm điều kiện vào** — V4-1 đã commit; `git diff cc1e4a5 HEAD -- tests/conftest.py tests/chan_host/chay.sh tests/test_chan_host.py docs/AGENT_RULES.md docs/MODULES.md CLAUDE.md` rỗng (không thì `git apply --check`, hỏng thì DỪNG).

- [ ] **Step 1: Viết test** — thêm vào cuối `tests/test_chan_host.py`:

````diff
diff --git a/tests/test_chan_host.py b/tests/test_chan_host.py
index cef9a89..7917521 100644
--- a/tests/test_chan_host.py
+++ b/tests/test_chan_host.py
@@ -233,3 +233,32 @@ def test_chay_sh_bao_so_dong_moi(tmp_path):
     kq = subprocess.run([str(GOC / "chay.sh"), "--version"], env={**os.environ, "TRAM_CHAN_NHAT_KY": str(nk)},
                         capture_output=True, text=True, timeout=120)
     assert kq.returncode == 0 and "0 dòng mới" in kq.stdout
+
+
+@pytest.mark.parametrize("thieu", ["bien-runner", "plugin", "git-gia", "ca-bo"])
+def test_pytest_khong_qua_chay_sh_thi_tu_choi(tmp_path, thieu):
+    """D61 (bs-2bd.1.26): thiếu MỘT dấu của runner (biến `TRAM_CHAN_CHAY_SH`, plugin `chan_host`, `git` giả đầu PATH)
+    → pytest thoát 4 kèm lệnh đúng, trước khi thu thập — kể cả không chỉ file (`testpaths`, "ca-bo"). `--co`: lớp chặn
+    hỏng thì cũng chỉ thu thập, không chạy test."""
+    env = moi_truong(tmp_path, TRAM_CHAN_CHAY_SH="1", PATH=f"{GOC / 'bin'}{os.pathsep}{os.environ['PATH']}")
+    argv = [sys.executable, "-m", "pytest", "-p", "chan_host", "-p", "no:cacheprovider", "--co", "-q",
+            "tests/test_chan_host.py::test_chay_sh_bao_so_dong_moi"]
+    if thieu in ("bien-runner", "ca-bo"):
+        del env["TRAM_CHAN_CHAY_SH"]
+        argv = argv[:-1] if thieu == "ca-bo" else argv
+    elif thieu == "plugin":
+        argv[3:5] = []
+    else:
+        env["PATH"] = os.pathsep.join(d for d in env["PATH"].split(os.pathsep)
+                                      if d and os.path.realpath(d) != os.path.realpath(GOC / "bin"))
+    kq = subprocess.run(argv, cwd=GOC.parent.parent, env=env, capture_output=True, text=True, timeout=120)
+    assert kq.returncode == 4, kq.stdout[-500:]
+    assert "tests/chan_host/chay.sh -q" in kq.stdout + kq.stderr and "collected" not in kq.stdout
+
+
+def test_chay_sh_van_chay_duoc_qua_cong_d61(tmp_path):
+    kq = subprocess.run([str(GOC / "chay.sh"), "-p", "no:cacheprovider", "--co", "-q",
+                         "tests/test_chan_host.py::test_chay_sh_bao_so_dong_moi"], cwd=GOC.parent.parent,
+                        env={**os.environ, "TRAM_CHAN_NHAT_KY": str(tmp_path / "nk.log")}, capture_output=True,
+                        text=True, timeout=120)
+    assert kq.returncode == 0 and "1 test collected" in kq.stdout, kq.stdout[-500:]
````

- [ ] **Step 2: Chạy test, thấy đỏ**

Bằng chứng hành vi cũ (lần pytest trần DUY NHẤT, có chủ đích, khi viết plan — một file không spawn tiến trình, không push): `UV_OFFLINE=1 uv run pytest -q -p no:cacheprovider tests/test_cham_tham_do.py` → `31 passed in 0.05s` — pytest trần chạy test bình thường, không từ chối. **Người code KHÔNG lặp lại lệnh này.**

```bash
tests/chan_host/chay.sh -q tests/test_chan_host.py
```

Kết quả THẬT (18/10, sau V4-1 + test của task, trước mã):

```
E       assert 0 == 4
 +  where 0 = CompletedProcess(args=['…/.venv/bin/python', '-m', 'pytest', '-p'…returncode=0, stdout='tests/test_chan_host.py::test_chay_sh_bao_so_dong_moi\n\n1 test collected in 0.04s\n', stderr='').returncode
FAILED tests/test_chan_host.py::test_pytest_khong_qua_chay_sh_thi_tu_choi[bien-runner]
FAILED tests/test_chan_host.py::test_pytest_khong_qua_chay_sh_thi_tu_choi[plugin]
FAILED tests/test_chan_host.py::test_pytest_khong_qua_chay_sh_thi_tu_choi[git-gia]
FAILED tests/test_chan_host.py::test_pytest_khong_qua_chay_sh_thi_tu_choi[ca-bo]
4 failed, 45 passed in 12.34s
=== nhật ký chặn …: 0 dòng mới; điểm mù (Python con không mang bộ chặn): 0; push giả lập (không push thật): 0
```

(`test_chay_sh_van_chay_duoc_qua_cong_d61` xanh ngay từ đầu — nó canh để mã không làm gãy runner.)

- [ ] **Step 3: Viết mã**

````diff
diff --git a/tests/conftest.py b/tests/conftest.py
index 58f4525..f5c3357 100644
--- a/tests/conftest.py
+++ b/tests/conftest.py
@@ -1,5 +1,22 @@
+import os
+import shutil
+from pathlib import Path
+
 import pytest
 
+GIT_GIA = Path(__file__).resolve().parent / "chan_host" / "bin" / "git"
+HUONG_DAN = ("TỪ CHỐI CHẠY: pytest phải đi qua bộ chặn host (AGENT_RULES.md §13, D61) — chạy trần thì test cũ có thể "
+             "push thật vào kho tạm. Lệnh đúng: tests/chan_host/chay.sh -q [đường test]")
+
+
+def pytest_configure(config):
+    """D61: thiếu một dấu của `tests/chan_host/chay.sh` (biến runner, plugin `chan_host`, `git` giả đầu PATH) → thoát 4
+    trước khi thu thập test nào."""
+    git = shutil.which("git")
+    if (os.environ.get("TRAM_CHAN_CHAY_SH") != "1" or not config.pluginmanager.has_plugin("chan_host")
+            or git is None or os.path.realpath(git) != str(GIT_GIA)):
+        pytest.exit(HUONG_DAN, returncode=4)
+
 
 @pytest.fixture(autouse=True)
 def tram_home_tam(tmp_path, monkeypatch):
diff --git a/tests/chan_host/chay.sh b/tests/chan_host/chay.sh
index 733ee2c..0fae43d 100755
--- a/tests/chan_host/chay.sh
+++ b/tests/chan_host/chay.sh
@@ -8,6 +8,8 @@
 # đẩy/alias không đi qua git giả; git chỉ nói chuyện với kho file cục bộ (GIT_ALLOW_PROTOCOL=file). KHÔNG phải sandbox:
 # xem điểm mù ở chan_host.py. Nhật ký chặn $TRAM_CHAN_NHAT_KY (mặc định file tạm mới, xoá khi sạch): có dòng mới →
 # thoát 3 dù test xanh. Điểm mù đã gặp (Python con không mang bộ chặn) và số lần push giả lập in ở cuối.
+# D61: `TRAM_CHAN_CHAY_SH=1` là dấu của runner — `tests/conftest.py` từ chối (thoát 4) khi thiếu nó, plugin `chan_host`
+# hay `git` giả đầu PATH, nên pytest trần không chạy được test nào.
 GOC=$(cd "$(dirname "$0")" && pwd)
 NK=${TRAM_CHAN_NHAT_KY:-}
 TAM=
@@ -19,7 +21,7 @@ truoc=$(wc -l < "$NK" | tr -d ' ')
 GIT_THAT=${TRAM_CHAN_GIT:-$(command -v git)}
 GOC_TAM=$(cd "${TMPDIR:-/tmp}" && pwd -P)
 DUNG_SAN=$("$GIT_THAT" --list-cmds=builtins | tr '\n' ' ')          # lệnh con dựng sẵn của git: đọc một lần
-TRAM_CHAN_NHAT_KY="$NK" TRAM_CHAN_MU="$MU" TRAM_CHAN_GIA="$GIA" TRAM_CHAN_GIT="$GIT_THAT" \
+TRAM_CHAN_CHAY_SH=1 TRAM_CHAN_NHAT_KY="$NK" TRAM_CHAN_MU="$MU" TRAM_CHAN_GIA="$GIA" TRAM_CHAN_GIT="$GIT_THAT" \
   TRAM_CHAN_DUNG_SAN="$DUNG_SAN" TRAM_CHAN_GOC_TAM="${TRAM_CHAN_GOC_TAM:-$GOC_TAM}" \
   GIT_ALLOW_PROTOCOL=file GIT_TERMINAL_PROMPT=0 PATH="$GOC/bin:$PATH" \
   PYTHONPATH="$GOC${PYTHONPATH:+:$PYTHONPATH}" UV_OFFLINE=1 uv run pytest -p chan_host \
````

- [ ] **Step 4: Chạy test, thấy xanh**

```bash
tests/chan_host/chay.sh -q tests/test_chan_host.py
```

Kết quả THẬT: `49 passed in 6.63s`; nhật ký chặn 0 dòng mới. Thông báo pytest trần nhận được (stderr của subprocess, ca `bien-runner`, mã 4):

```
Exit: TỪ CHỐI CHẠY: pytest phải đi qua bộ chặn host (AGENT_RULES.md §13, D61) — chạy trần thì test cũ có thể push thật vào kho tạm. Lệnh đúng: tests/chan_host/chay.sh -q [đường test]
```

- [ ] **Step 5: Docs** — §13, bộ test, điểm vào, bước G6.1 của sổ tay (lệnh cũ nay thoát 4):

````diff
diff --git a/docs/AGENT_RULES.md b/docs/AGENT_RULES.md
index 6b97dcd..d1d6933 100644
--- a/docs/AGENT_RULES.md
+++ b/docs/AGENT_RULES.md
@@ -2,7 +2,7 @@
 
 Project: `ben-station`
 Status: `ACTIVE`
-Cập nhật: `2026-10-17`
+Cập nhật: `2026-10-18`
 
 ## Mục đích và sở hữu
 Sở hữu: luật vận hành agent — đọc gì, blast radius, kill list, quyền tự quyết, lệnh cấm, kiểm chứng, DoD.
@@ -161,8 +161,10 @@ không thêm dependency, tối ưu hay dịch vụ launchd mới khi chưa có n
 `sudo`, `crontab`, `at`, `batch`, `launchctl`, `security`, `dscl`, `sysadminctl`, `sandbox-exec`, `pkill`, `killall`,
 `bd`, `gh`… chỉ ghi nhật ký rồi thoát lỗi; `git` giả không bao giờ push thật (push vào kho trong thư mục tạm được giả
 lập, còn lại chặn). Audithook (pytest và Python con mang `PYTHONPATH` của bộ chặn) bắt cả đường tuyệt đối, lệnh bọc,
-chuỗi shell. Nhật ký chặn có dòng mới → thoát 3 dù test xanh. Không phải sandbox: runner in số "điểm mù" (Python con
-không mang bộ chặn). Luật §11 vẫn nguyên. Thêm lệnh cấm: sửa cả `bin/` và `CHAN` trong `tests/chan_host/chan_host.py`.
+chuỗi shell. Nhật ký chặn có dòng mới → thoát 3 dù test xanh. pytest không qua runner (thiếu `TRAM_CHAN_CHAY_SH=1`,
+plugin `chan_host` hay `git` giả đầu `PATH`) tự thoát 4 trước khi thu thập (`tests/conftest.py`, D61). Không phải
+sandbox: runner in số "điểm mù" (Python con không mang bộ chặn). Luật §11 vẫn nguyên. Thêm lệnh cấm: sửa cả `bin/` và
+`CHAN` trong `tests/chan_host/chan_host.py`.
 
 ## 14. Dữ liệu, secrets và hardcode
 - Bí mật **không bao giờ** nằm trong argv, file, log, báo cáo, bead hay docs. Tên mục Keychain thì được ghi.
diff --git a/docs/MODULES.md b/docs/MODULES.md
index 5cc0a48..89221cb 100644
--- a/docs/MODULES.md
+++ b/docs/MODULES.md
@@ -64,7 +64,7 @@ Cột "Hỏng thì" suy từ code, chưa xác nhận.
 | `brew`, `ollama pull` | cài memory | install 30 phút, services 60 giây, pull 60 phút (`tram/chu/cai_dat_nho.py`) | quá hạn: dừng kế hoạch, thoát 3; đối soát cây con ở cổng |
 
 ## Kiểm thử
-- **pytest** (`tests/`): mỗi test có `TRAM_HOME` tạm (`tests/conftest.py`); hệ ngoài thay bằng bản giả
+- **pytest** (`tests/`): mỗi test có `TRAM_HOME` tạm, chạy ngoài `tests/chan_host/chay.sh` thì thoát 4 (`tests/conftest.py`, D61); hệ ngoài thay bằng bản giả
   `tests/*_gia.py`. Không bộ nào chạm macOS thật — cách ly, launchd, Keychain chỉ chứng minh qua cổng sổ tay.
 - **Frontend:** `frontend/tests/*.test.mjs` (logic), `frontend/kiem-an-toan.mjs` (quét nguồn),
   `frontend/kiem-dist.mjs` (quét bundle cho CSP).
diff --git a/CLAUDE.md b/CLAUDE.md
index 2db72bb..f743467 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -17,7 +17,7 @@ Các tài liệu còn lại chỉ đọc khi task chạm tới — `docs/AGENTS.
 Mã nằm trong `tram/` (Python) và `frontend/` (Vue). Test:
 
 ```bash
-tests/chan_host/chay.sh -q             # bộ chặn host + git giả; KHÔNG chạy pytest trần — AGENT_RULES.md §13
+tests/chan_host/chay.sh -q             # bộ chặn host + git giả; pytest trần tự từ chối (thoát 4, D61) — AGENT_RULES.md §13
 cd frontend && npm run kiem && npm run build && npm run kiem-dist
 ```
 
--- a/docs/handovers/2026-10-15-so-tay-chay-that.md
+++ b/docs/handovers/2026-10-15-so-tay-chay-that.md
@@ -169,7 +169,7 @@
 
 | Bước | Ai | Lệnh | Đạt | Dừng khi | Lui |
 |---|---|---|---|---|---|
-| G6.1 | điều phối | `git log --oneline -1 main`; `UV_OFFLINE=1 uv run pytest -q` | 4D-1a..3c trên `main`; suite xanh (17/10: 2697) | đỏ | — |
+| G6.1 | điều phối | `git log --oneline -1 main`; `tests/chan_host/chay.sh -q` (pytest trần thoát 4 — D61) | 4D-1a..3c trên `main`; suite xanh (17/10: 2697) | đỏ | — |
 | G6.2 | điều phối | `grep -n bat_ghi tram/api/phu_thuoc.py` | `PhuThuocApi.bat_ghi` có thật. **Đạt 17/10** | — | — |
 | G6.3 | Đại ca | Tailscale máy A (A2, `bs-8eh.17`); `tailscale serve` → tram-api B (A4, `bs-6o0.11`); máy A: `/usr/bin/python3 -c "import urllib.request; print(urllib.request.urlopen('https://<máy B>/api/du-an').status)"` | 200, TLS không lỗi | lỗi chứng chỉ; Python < 3.9 | gỡ `tailscale serve` |
 | G6.4 (H5) | Đại ca + Em đọc | Từ máy A, qua `tailscale serve`: `/usr/bin/python3 -I ~/.claude/skills/phong-van-yeu-cau/yeu_cau.py xem …` (sau G6.6) → không 403. Từ máy khác trong tailnet: POST `/api/feature/yeu-cau/xem` kèm `Tailscale-User-Login: <login Đại ca>` tự gắn | máy A không 403; máy khác **403** (header client bị bỏ hoặc ghi đè) | máy khác **không** 403 → dừng, không dùng tuyến tạo | gỡ skill |
````

- [ ] **Step 6: Chạy cả bộ**

```bash
tests/chan_host/chay.sh -q
```

Kết quả THẬT (18/10, `cc1e4a5` + V4-1 + V4-2): `3254 passed in 339.65s (0:05:39); nhật ký chặn 0 dòng mới; điểm mù 48; push giả lập (không push thật) 629 — đo trên cây dựng lại từ khối mã của plan (lượt đầu trên cây đã chạy: 3254 passed in 343.68s)`.

- [ ] **Step 7: Commit**

```bash
git add tests/conftest.py tests/chan_host/chay.sh tests/test_chan_host.py docs/AGENT_RULES.md docs/MODULES.md CLAUDE.md \
  docs/handovers/2026-10-15-so-tay-chay-that.md
git commit -m "test(chan-host): pytest từ chối chạy ngoài tests/chan_host/chay.sh (D61, bs-2bd.1.26)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

## Kiểm chứng plan (khi viết, 18/10/2026)

**Bản sửa V4-1 sau review vòng 1 (trên `d340a27`):**
- RED thật: cả task (3 lỗi thu thập + 1 đỏ phía trạm, như bản trước); riêng #5 `4 failed, 13 passed`, #6 `5 failed` với `_khop` cũ (Step 2). GREEN `91 passed` (12 file liên quan). Cả bộ sau V4-1: `3253 passed in 347.63s`, 0 dòng chặn mới, điểm mù 48, push giả lập 629.
- Áp lại: hoàn nguyên worktree về `d340a27`, trích MỌI khối mã/docs từ chính file plan này (V4-1 bản sửa rồi V4-2 nguyên như bản trước), `git apply` theo thứ tự, so `diff -r` với bản sao trạng thái đã chạy: khớp (0 khác biệt sau V4-1; V4-2 áp sạch lên trên, `git apply --check` từng khối). Cả bộ trên cây dựng lại (V4-1 + V4-2): `3258 passed in 333.88s`, nhật ký chặn 0 dòng mới, điểm mù 48, push giả lập 629.

**Bản trước (trên `cc1e4a5`, lịch sử — V4-1 vòng 1, V4-2 đến nay):**

- N₀ trên `cc1e4a5`: `3236 passed in 356.94s`, 0 dòng chặn mới, điểm mù 48, push giả lập 629.
- V4-1: RED (3 lỗi thu thập + 1 đỏ hành vi phía trạm) → GREEN `87 passed` (12 file liên quan). V4-2: RED `4 failed, 45 passed` → GREEN `49 passed`. Cả bộ sau hai task: `3254 passed in 339.65s (0:05:39); nhật ký chặn 0 dòng mới; điểm mù 48; push giả lập (không push thật) 629 — đo trên cây dựng lại từ khối mã của plan (lượt đầu trên cây đã chạy: 3254 passed in 343.68s)`.
- Áp lại: hoàn nguyên worktree về `cc1e4a5`, trích MỌI khối mã/docs từ chính file plan này (file mới chép nguyên văn, bản vá `git apply` theo thứ tự task), so `diff -r` với bản sao trạng thái đã chạy (bỏ `.git`, `.venv`, `__pycache__`, `.pytest_cache`): khớp. Lượt so đầu chỉ lệch một dòng trống thừa ở cuối `tests/test_kiem_khe_d54.py` của bản đã chạy (plan không có dòng đó); cây dựng lại từ plan được chạy lại cả bộ (số ở trên) và so lại lần hai với khối trích từ CHÍNH file plan đã commit: 0 khác biệt.
- Mọi file `tram/` sửa ≤ 120 dòng, mọi dòng ≤ 120 ký tự (`tests/test_do_dai_ma.py` xanh); không vòng import mới (`tests/test_vong_import.py` xanh).

## Bước cổng trên OS thật (không tự chạy — Đại ca cho phép từng kịch bản)

Theo sổ tay G5.6 (thêm ở V4-1 Step 5), trên máy B (quản lý thợ cùng máy với trạm, `tho.yaml` `tram_api: http://127.0.0.1:<cổng>`), sau khi V4-1 đã ghép và `tram-api` chạy bản mới:
1. Dừng `tram tho chay` (D55). Dưới tài khoản quản lý thợ: `uv run tram tho kiem > ~/.tram/g5/kiem-d54.txt 2>&1; echo $?`.
2. Đạt: mục "`<khe>` cách ly" có kết luận (không phải "không kết luận") cho "API Duyệt với header danh tính giả" và mỗi DB khai ở `cach_ly.db_nghiep_vu`. Kênh `header` hiện hành → ĐỎ "API nhận yêu cầu (HTTP 422)" là kết quả ĐÚNG (D51); chỉ đạt "bị chặn" sau khi chuyển `unix-socket`.
3. Tuỳ chọn (như G5.3): trong lúc chạy, `ps -A -o uid=,pid=,command= | grep '[c]url'` → cột uid = UID khe.
4. Dừng khi: "không lấy được đích từ tram-api" (tram-api chưa có route mới, token sai, hay trạm chưa khai `dai_ca_logins`/`ten_may_b`), "thợ không ở máy B", hoặc "không kết luận" cho API/DB.
`tram chu kiem-cach-ly` ở tài khoản trạm: không cần `--principal` nữa; nếu gõ, dòng `[CHUYỂN]` là đúng.

## Rủi ro còn lại (không đóng bằng plan này)

1. **D61 là lưới chống nhầm, không chống cố ý:** ai tự đặt `TRAM_CHAN_CHAY_SH=1`, `-p chan_host` và để `git` giả đầu PATH vẫn chạy được không qua `chay.sh` (khi đó họ đã dựng lại gần đủ bộ chặn). `tests/conftest.py` chỉ nạp khi thu thập dưới `tests/` (mọi test đều ở đó; `testpaths = ["tests"]`).
2. **Bộ chặn thay thế ngoài repo sẽ bị từ chối:** lệnh `PATH="$C/bin:$PATH" PYTHONPATH="$C/plugin" … uv run pytest -p chan_host` của các agent viết plan (thư mục `chan/` trong scratchpad) thoát 4 sau V4-2 — đúng ý D61; luật chung cho agent và `.handover/qc/huong-dan-code.md` (dòng 5 còn ghi `uv run pytest -q`, git bỏ qua) phải đổi sang `tests/chan_host/chay.sh` khi ghép.
3. **Kênh `header`:** thăm dò API của khe trên máy B sẽ ĐỎ cho tới khi chuyển `unix-socket` — đúng rủi ro (b) đã nhận ở D51; G5.6 ghi nhận, không phải lỗi của plan.
4. **Cơ chế `sandbox`:** hồ sơ chặn cổng 7700 → curl không kết nối được → "không kết luận" (chuẩn A-T6), mục ĐỎ. Hiện chỉ dùng cơ chế `user` (D3, D53).
5. **Thợ ở máy khác chưa kiểm được API/DB** (review vòng 1 #5): mục cách ly của khe máy đó luôn ĐỎ "không kết luận: thợ không ở máy B" tới lát hỗ trợ ánh xạ đích theo máy. Phía trạm (`tram chu kiem-cach-ly`, dưới `tram-kiem`) vẫn còn dùng giá trị giữ chỗ `?`/`may-b` khi trạm thiếu login/máy B — như trước V4, không đổi trong lát này (trạm thiếu chúng thì mọi lệnh ghi đều bị từ chối); thợ thì nay từ chối hẳn.
6. `tram/chu/cai_dat_tho.py:93` (kill list mục 6) vẫn nhắc "chạy `tram chu kiem-cach-ly` (H9) TRƯỚC khi bật 3a" — còn đúng cho `tram-kiem`, thiếu `tram tho kiem`. Không sửa trong plan này (đề xuất một bead P4 sửa chữ khi lần tới chạm file đó).

## Thứ tự code đề xuất và file giao nhau

1. V4-2 (đã đạt review vòng 1) ghép trước sau QC, ở nhánh riêng — không phụ thuộc mã V4-1. Hunk G6.1 của V4-2 lệch vị trí (chưa có dòng G5.6), ngữ cảnh vẫn có.
2. V4-1 bản sửa: Đại ca trả lời Câu hỏi 1–3 (đang là giả định theo đề xuất) và duyệt phần kill list → review Codex vòng 2 → code. Nếu V4-2 đã ghép: N₀ = 3241, sau V4-1 mong đợi 3258; hunk G5.6 của V4-1 áp theo ngữ cảnh (`git apply --check`).
3. File giao nhau: `tram/tho/kiem_cong.py`, `kiem_am.py`, `tram/tho/cau_hinh.py`, `tram/chu/kiem_cach_ly.py` (V2b Task 6 — đã ghép, không còn plan mở nào sửa); `tram/api/tho_them.py`; `tests/conftest.py` (mọi plan sau thêm fixture phải giữ hook `pytest_configure`); `docs/handovers/2026-10-15-so-tay-chay-that.md` (điều phối hay sửa bằng chứng cổng — áp theo nội dung). Sau khi ghép: điều phối ghi lại dòng Test ở `docs/CURRENT_STATE.md` (plan không sửa file đó).

## Câu hỏi cho Đại ca

Chưa có trả lời — bản sửa V4-1 làm theo ĐỀ XUẤT của Em ở cả ba câu (GIẢ ĐỊNH, chờ Đại ca chốt trước khi code).

1. **Thông tin cho phép kiểm "giả danh Đại ca" của khe lấy ở đâu?** Phép kiểm cần đúng địa chỉ đăng nhập Tailscale của Đại ca và đúng tên máy B; sai một chữ là kiểm báo "bị chặn" giả.
   - (a) **Trạm tự đưa cho máy thợ** qua đường API thợ đã có khoá máy (đề xuất của Em): Đại ca không khai gì, luôn khớp với cái trạm thật sự kiểm. Đổi lại: máy thợ nào có khoá máy cũng đọc được địa chỉ đăng nhập Tailscale của Đại ca và danh sách địa chỉ DB (không phải mật khẩu).
   - (b) Đại ca tự gõ ba thông tin vào `tho.yaml` của tài khoản thợ: không thêm đường API, nhưng gõ sai thì kiểm "xanh" giả mà không ai biết.
   Nếu chọn sai: (a) mà Đại ca không muốn máy thợ biết địa chỉ đăng nhập → phải gỡ route (một file); (b) mà gõ sai → G5 "đạt" sai.
2. **`tram chu kiem-cach-ly` có tính mục "[CHUYỂN]" của khe là lỗi không?** Đề xuất của Em: **không tính** — lệnh trạm chỉ báo đỏ cho cái nó thật sự kiểm (`tram-kiem`); bằng chứng của khe nằm ở `tram tho kiem` (G5.6). Nếu tính là lỗi, gõ `--principal` sẽ luôn đỏ — quay lại đúng cái "đỏ khó hiểu" D54 muốn bỏ. Nếu chỉ khai khe mà chưa có `tram-kiem`, lệnh vẫn đỏ (chưa kiểm gì). (Codex vòng 1: phù hợp D54, không cần hỏi lại — giữ ở đây để Đại ca thấy.)
3. **Lát này chỉ kiểm khe trên máy B, hay phải kiểm cả thợ ở máy khác ngay?** Địa chỉ DB và API trạm đưa là theo máy B (ví dụ `127.0.0.1:3306`); đem sang máy thợ khác thì phép kiểm nhắm nhầm DB của chính máy thợ, còn API đi qua Tailscale bị đổi danh tính nên "bị chặn" không chứng minh gì.
   - (a) **Chỉ máy B ở lát này** (đề xuất của Em, Codex cũng đề xuất): thợ máy khác báo ĐỎ "không kết luận: thợ không ở máy B" — rõ ràng, không xanh giả.
   - (b) Hỗ trợ cả máy khác ngay: phải thêm bảng "máy nào thấy DB ở địa chỉ nào" và một đường API riêng — thêm cấu hình và một lần review nữa.
   Nếu chọn sai: (a) mà Đại ca sắp chạy thợ ở máy khác → máy đó ĐỎ ở mục cách ly cho tới lát sau; (b) → chậm V4-1 và thêm bề mặt mạng.

## Ghi chú triển khai

### Review Codex đợt 9 vòng 1 — 18/10/2026 (chỉ đọc, không chạy)

Ghi chú này thắng mô tả giữ chỗ ở phần thân: thiếu/null `dai_ca_login` hoặc `may_b` từ API phải làm
`KhachTram.kiem_am()` ném `LoiKhachTram`, `_api_db` trả ĐỎ không kết luận; không dùng 403 do thiếu cấu hình
làm bằng chứng cách ly. Đã sửa nguyên văn `_khop` và test ở Step 1; kiểu nullable trên dây vẫn phản ánh cấu hình
trạm chưa đầy đủ, nhưng client không chấp nhận nó làm đích thăm dò. Các số RED/GREEN phía trên là lịch sử của
tác giả, CHƯA kiểm chứng lại với sửa đổi này. Số ca test không đổi (thêm assertion vào ca đã có).

V4-1 vẫn CHƯA ĐẠT: còn phải ràng buộc đường HTTP được thăm dò, tránh 403 từ proxy/ghi đè danh tính trở thành
bằng chứng kênh ghi đã tách; xem `REVIEW-CODEX-dot9-vong1.md`. Chưa có mã TDD đầy đủ cho phần đó nên không code V4-1.
V4-2 được review độc lập, không cần chờ V4-1; khi tách thứ tự, áp hunk G6.1 theo ngữ cảnh và kiểm lại bản vá.

### Bản sửa V4-1 sau review vòng 1 — 18/10/2026 (tác giả; thắng ghi chú vòng 1 ở trên ở phần V4-1)

Hai điểm chặn V4-1 của ghi chú trên đã có mã TDD nguyên văn, chạy thật trên `d340a27`: (1) sửa `_khop` của Codex
được giữ nguyên ký tự, RED/GREEN đã chạy (Step 2), `DichKiemAm` nay không nullable và `_api_db` bỏ giá trị giữ chỗ;
(2) đường HTTP được thăm dò bị ràng buộc: chỉ `tram_api` loopback (quản lý thợ trên máy B, gọi thẳng TCP tram-api —
không proxy, không `tailscale serve`), khác → ĐỎ "không kết luận", không lấy đích. V4-1 vẫn chờ Đại ca (Câu hỏi 1–3,
kill list) và review Codex vòng 2 trước khi code. Phần V4-2 của plan KHÔNG đổi.

## Phản hồi review vòng 1

Nguồn: `.handover/review-codex-plan/REVIEW-CODEX-dot9-vong1.md`, phần A / V4-1 (B là plan 3C-D7 — không thuộc plan này; V4-2 ĐẠT, không sửa).

| # | Mức | Phát hiện | Xử lý | Bằng chứng |
|---|---|---|---|---|
| 5 | Quan trọng | Đích theo máy B (`127.0.0.1:…`) đem dùng trên máy thợ từ xa; 403 qua `tailscale serve` không chứng minh kênh TCP trên B đã tách | **Sửa:** `CauHinhTho.tren_may_b`; `_api_db` chỉ chạy khi `tram_api` loopback, khác → ĐỎ "không kết luận: thợ không ở máy B…", không gọi `dich`, không curl/nc, phần rút gọn vẫn chạy. Không đổi loopback thành IP LAN/Tailscale. Thiết kế V4-1, Bảng G (G1b), Rủi ro 5, sổ tay G5.6, Câu hỏi 3 cập nhật | `test_chi_kiem_api_db_khi_tho_o_may_b` (4 ca: `127.0.0.1`, `localhost`, `https://may-b…`, `https://127.0.0.1:…`) — RED thật trên mã vòng 1 `4 failed`, GREEN |
| 6 | Quan trọng | null/thiếu login, máy B thành giá trị giữ chỗ rồi báo đạt | **Giữ sửa của Codex** (`_khop` chỉ nhận chuỗi khớp mẫu; test null + thiếu khoá) và **chạy thật**: `_khop` cũ → `5 failed` (`DID NOT RAISE`), mới → xanh. Thêm: `DichKiemAm` đổi kiểu `str`, `_api_db` bỏ `or "?"`/`or "may-b"` (mã chết sau sửa) | Step 2, Step 4 (`91 passed`) |
| 8 | Nhỏ | Thiếu phủ định 401 cho token sai và header danh tính Đại ca không Bearer | **Thêm** vào `test_tram_cap_dich_tu_cau_hinh_cua_chinh_no_qua_token_may`: cả hai → 401, thân không có `dai_ca_login`/`may_b`/`db_nghiep_vu` | xanh ngay trên mã vòng 1 (router kế thừa `Depends(may_cua_yeu_cau)`) — lưới canh |
| Câu hỏi gộp 1–2 | — | API cấp tự động vs khai tay; chỉ máy B hay cả từ xa | Theo đề xuất (API cấp, chỉ máy B) — ghi là GIẢ ĐỊNH ở Câu hỏi 1, 3; `[CHUYỂN]` không tính lỗi (Câu hỏi 2, Codex: không cần hỏi lại) | — |

Số test V4-1: 13 → 17 (+4 ca của #5; #6, #8 thêm assertion vào ca có sẵn). Cả bộ sau V4-1 trên `d340a27`: 3253.

### Review vòng 2 — ghi chú hiện hành

V4-1 ĐẠT theo review tĩnh sau sửa trên: `-q` phải là đối số đầu của curl, ngăn cấu hình mặc định của
tài khoản khe đổi proxy/đường đo; môi trường chạy hiện chỉ PATH/LANG. Assertion mới nằm trong test
`test_tho_kiem_chay_api_va_db_duoi_principal_khe_sau_uid`: mã trước sửa không có `-q` nên đỏ, sau sửa
khớp argv. Đây là suy luận, chưa chạy. Chuẩn chấm A-T6 và token máy giữ nguyên.
Nền mã V4-1 tại HEAD không đổi so với `d340a27`; V4-2 đã ghép nên N₀ lịch sử 3236 không còn là nền hiện hành.
Không áp các bước/hunk V4-2. D62–D64 giải quyết câu hỏi thiết kế, không chứng minh G5 đã đạt và không
thay quyền duyệt từng kịch bản OS. Thứ tự ghép hiện hành ở báo cáo vòng 2 thắng thứ tự V4-1 → V4-2 cũ.

