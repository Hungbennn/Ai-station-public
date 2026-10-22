# Lát 3C-D7 — bộ đọc launchd của `tram-kiem` (bead bs-863.20) — Implementation Plan

> **Cập nhật reviewer vòng 2, 18/10/2026, HEAD `8b23e8f`:** D65–D68 đã chốt các câu hỏi thiết kế;
> “giả định chờ Đại ca” bên dưới là lịch sử. D66 vẫn yêu cầu trình kịch bản cụ thể trước khi chạy.
> Task 1–2 ĐẠT review tĩnh sau sửa `task-special ports` nguyên văn trong Task 1; Task 3 CHƯA ĐẠT.
> Không chạy kịch bản Task 3 này. Xem các lỗi còn mở và điều kiện vòng 3 ở ghi chú cuối và
> `REVIEW-CODEX-dot9-vong2.md`. Reviewer không chạy code/test; số đo bên dưới là lịch sử trước sửa vòng 2.

> **Cập nhật tác giả vòng 4 (D117), 18/10/2026, trên `main` `74cce8b`:** Codex vòng 3 kết luận Task 3 CHƯA ĐẠT (R3-01…R3-04); Đại ca chốt D117 — Task 3 viết lại thành MỘT kịch bản bash rút gọn kiểu `.handover/g3/g3-do.sh` (tram-kiem phải trống lúc bắt đầu, cổng dừng trước mọi lệnh ghi, dọn `kill -1` dưới tài khoản dành riêng + đếm 5 lần). Mục "Phản hồi review vòng 3" cuối plan. Task 1, Task 2 giữ NGUYÊN từng ký tự. Đã chạy RED→GREEN thật, cả bộ qua runner, áp lại từ plan lên bản sạch + `diff -r`; mã đã hoàn nguyên, nhánh chỉ có file plan. Vẫn CHƯA chạy G3.8–G3.10 thật: cần review vòng 4 rồi trình Đại ca kịch bản cụ thể (D66).

> **For agentic workers:** REQUIRED SUB-SKILL: dùng `ai-skills:subagent-driven-development` (khuyến nghị) hoặc `ai-skills:executing-plans` để làm từng task. Step dùng checkbox (`- [ ]`). **Chưa được code**: plan chạm kill list mục 3 (cách ly agent — quan sát của cổng kiểm lại `tram-kiem`) và Task 3 là kịch bản chạy thật (kill list mục 8). Phải có Đại ca duyệt plan và review Codex vòng 2 trước (xem Global Constraints). Duyệt plan KHÔNG phải cho phép chạy kịch bản G3.

**Trạng thái: bản SỬA sau Codex review đợt 9 vòng 1** (`.handover/review-codex-plan/REVIEW-CODEX-dot9-vong1.md` — B/Task 1, 2, 4 CHƯA ĐẠT; Task 3 đạt phần bản vá), 18/10/2026, trên `main` `d340a27`. Đánh số task ĐỔI so với vòng 1 (bảng ánh xạ ở "Phản hồi review vòng 1"). Đã chạy RED→GREEN thật Task 1, 2, 3 trong worktree `plan/3c-d7-launchd`, cả bộ qua runner chặn host sau từng task; áp lại toàn bộ khối của plan (trích tự động từ chính file này) lên bản sạch `d340a27` và `diff -r` khớp trạng thái đã chạy. Mã đã hoàn nguyên, nhánh chỉ có file plan. CHƯA áp vào `main`. CHƯA chạy G3.8–G3.10, G4. **Câu hỏi 1–4 cho Đại ca chưa có trả lời: bản này thiết kế theo ĐỀ XUẤT của Em, ghi rõ là giả định chờ Đại ca.**

**Goal:** Thay khung ném của `quan_sat_kiem.launchd` (3C-D6c) bằng bộ đọc `launchctl print` CHỈ cho bố cục đã đo ở G3 trên máy B (macOS 15.6.1, 24G90): miền `user/<uid>` của `tram-kiem` có job, tiến trình, trạng thái launchd hoặc THIẾU khối quan sát → cổng đóng; `gui/<uid>` chỉ sạch ở đúng dạng "không có miền" đã đo; `login/<asid>` — đo được là miền đăng nhập của NGƯỜI GỌI sudo, không quy được mục nào về `tram-kiem` — không in, chỉ cho đi tiếp khi có bằng chứng G3.9 cho ĐÚNG ngữ cảnh vận hành hiện hành (bản macOS, máy, UID kiểm, UID trạm, loại phiên) mà trạm tự đọc từ OS. Kèm kịch bản G3.8–G3.10 an toàn (hạn từng lệnh, receipt, nhãn riêng, dọn có xác nhận kể cả khi bị ngắt) để thu bằng chứng đó; kịch bản không tự kết luận "launchd từ chối".

**Architecture:** Ba module mới trong `tram/giao_viec/`: `launchd_dinh_dang.py` (47 dòng — lược đồ đóng của bố cục đã đo: mỗi khoá cấp một là KHỐI hoặc VÔ HƯỚNG có mẫu giá trị; `BAT_BUOC_USER`; `tach`), `ngu_canh_kiem.py` (55 dòng — `NguCanh` do TRẠM đọc: `ProductBuildVersion` từ plist của root, sha256 của `gethostuuid`, UID kiểm qua `pwd`, `os.getuid()`, cờ `sessionHasGraphicAccess` của `SessionGetInfo` — không env, không lời `tram-kiem`), `launchd_kiem.py` (84 dòng — `xet_user`, `doc_launchd`, `MOC_USER` theo build, `BANG_CHUNG_LOGIN: frozenset[NguCanh]` rỗng). `doc_launchd(pk)` kiểm cơ chế, ngữ cảnh, mốc, bằng chứng TRƯỚC mọi lệnh; rồi chạy hai lệnh `print` dưới `tram-kiem` qua `CongLich` (UID đã chứng minh, `chay_gioi_han` có hạn — V2b), đòi UID chứng minh = UID ngữ cảnh. `cong_that.dung_cong` cắm `partial(launchd, pk, doc=doc_launchd)`. Kịch bản G3.8–G3.10 (Task 3, bản rút gọn D117): `docs/handovers/g3-bo-sung.sh` (bash kiểu `.handover/g3/g3-do.sh`, gọi bộ đọc Task 1 qua `.venv/bin/python -I`), test bằng lệnh giả.

**Tech Stack:** Python 3.12 stdlib (`plistlib`, `re`, `ctypes`, `hashlib`, `subprocess`, `dataclasses`), bash 3.2 + perl của macOS cho kịch bản, pytest 8. Không dependency mới.

**Spec / nguồn:** plan 3c [`2026-10-15-lat-3c-principal-kiem-trao-quyen.md`](2026-10-15-lat-3c-principal-kiem-trao-quyen.md) — "Task 3C-D6c", bảng G-D4, mục G3 "Ra khỏi G3"; phụ lục thiết kế [`2026-10-16-thiet-ke-3c-boundary.md`](../handovers/2026-10-16-thiet-ke-3c-boundary.md) §2 mục 4, §3, bảng threat hàng 20–22; phụ lục cổng đợt 7 [`2026-10-17-cong-sau-review-dot7.md`](../handovers/2026-10-17-cong-sau-review-dot7.md) ("3C-D7 chỉ parse fixture đã đo, dạng lạ đóng"; "Không xanh dựa vào vắng marker"; đối chứng dương cho hàng loại A); sổ tay [`2026-10-15-so-tay-chay-that.md`](../handovers/2026-10-15-so-tay-chay-that.md) mục G3 và "Bằng chứng G3 — 18/10/2026"; mẫu kịch bản an toàn `.handover/g3/g3-do.sh`; quyết định D45, D52 (`docs/quyet-dinh/2026-10-16-chot-sau-review-dot6.md`); review Codex đợt 9 vòng 1; dữ liệu đo G3 của Đại ca (`~/.tram/g3/` máy B: `user.txt`, `gui.txt`, `login.txt`, `procinfo.txt`, `g3.log`, `darwin.txt`). Mã thật đã đọc: `tram/giao_viec/{quan_sat_kiem,cong_that,cong_luot,kiem_lai,lenh_nghiem_thu,principal_kiem,thu_muc_he,kich_ban_nghiem_thu}.py`, `tram/kiem/{cong_lich,chay_gioi_han,danh_tinh,so_huu}.py`; header `Security.framework/Headers/AuthSession.h` (SDK, chỉ đọc).

## Global Constraints

- **Kill list (`AGENT_RULES.md` §2 mục 3 — cách ly agent):** plan thêm quan sát của cổng kiểm lại `tram-kiem` (ba module mới) và sửa `tram/giao_viec/cong_that.py` (cắm bộ đọc), docstring `quan_sat_kiem.py`, `lenh_nghiem_thu.py`. **Đại ca duyệt plan + review Codex vòng 2 trước khi code.** Không sửa `tram/kiem/`, `kiem_lai.py`, `kiem_principal.py`, `principal_kiem.py`, hồ sơ Seatbelt, cấu trúc DB, `giao_viec.bat`.
- **Kill list mục 8 (chạy thật):** Task 3 thêm KỊCH BẢN + tài liệu; chạy kịch bản là bước cổng riêng: Đại ca cho phép riêng, tự gõ trong Terminal.app, gõ `dong-y`. Agent không chạy `launchctl`, `sudo`, `sandbox-exec`, `kill -1`, không chạy kịch bản ở chế độ thật.
- **Không có "Task bật bằng chứng" trong plan này** (Task 4 cũ bị bỏ — review mục 4). `BANG_CHUNG_LOGIN` rỗng → `doc_launchd` ném trước mọi lệnh → cổng kiểm lại vẫn LUÔN đóng (như khung 3C-D6c, lý do cụ thể). Thêm bằng chứng = plan nhỏ SAU khi kịch bản Task 3 cho "ỨNG VIÊN ĐẠT" và Em + Codex phân loại chữ lỗi đo được (mục "Việc sau G3 bổ sung").
- **N₀ = 3236** (`tests/chan_host/chay.sh -q` trên `d340a27`, đo 18/10/2026; nhật ký chặn 0 dòng mới; điểm mù 48 — có sẵn, không do plan). Sau Task 1: **3294 passed in 330.81s**; sau Task 2: **3294 passed in 330.55s**; sau Task 3: **3310 passed in 354.40s**. Đo lại N₀ trước Task 1; lệch thì dừng, báo người điều phối.
- Chạy test BẮT BUỘC qua runner của repo: `tests/chan_host/chay.sh -q [đường test]` (PATH chặn host + audithook + git giả, `AGENT_RULES.md` §13). Không `uv run pytest` trần. Nhật ký chặn phải 0 dòng mới.
- **Test không bao giờ** chạy `launchctl`, `sudo`, `sandbox-exec`, `kill` thật: bộ đọc đi qua `CongLich` dựng trực tiếp với `chay` giả và ngữ cảnh giả; kịch bản chạy với `G3_GIA=<tmp_path>` — `sudo` giả chỉ cho chạy lệnh trong thư mục giả, `kill` giả chỉ tới `sleep` giả do chính nó chạy, `launchctl` giả giữ trạng thái trong tệp, `ps` giả = bảng thật bỏ UID giả + dòng giả. Không có `G3_GIA` và không có Terminal → kịch bản thoát 2 trước mọi lệnh (test khoá). `test_ngu_canh_kiem.py` gọi thật `gethostuuid`/`SessionGetInfo`/đọc `SystemVersion.plist` — chỉ đọc, của chính tiến trình test.
- TDD: test trước, chạy thấy đỏ (thông báo ở bước RED là kết quả THẬT), mã, chạy thấy xanh, chạy cả bộ, commit. Mã trong plan là **nguyên văn**: file mới in toàn văn; file sửa in bằng bản vá `git diff` áp được bằng `git apply` theo đúng thứ tự task. Mỗi khối có dòng chú thích ẩn `<!-- ap: … -->` để trích tự động (mục "Kiểm chứng plan").
- Mỗi file nguồn trong `tram/` ≤ 120 dòng, dòng ≤ 120 ký tự Unicode (`tests/test_do_dai_ma.py`). Sau plan: `launchd_dinh_dang.py` 47, `ngu_canh_kiem.py` 55, `launchd_kiem.py` 84, `cong_that.py` 111, `quan_sat_kiem.py` 115, `lenh_nghiem_thu.py` 117. Định danh tiếng Việt không dấu. Thông báo lỗi không chép nhãn, đầu ra hay argv (dot6-Q06).
- **Fixture không mang thông tin cá nhân.** `login.txt` thật KHÔNG vào repo; chỉ bản rút gọn `tests/du_lieu/launchd/login-rut-gon.txt` (mục "Fixture"); ba tệp fixture kiểm bằng `shasum -a 256` trước khi commit. Mã máy chỉ lưu dạng sha256 rút gọn, không UUID thô.
- Một task một commit (`feat(giao-viec): …`, `docs(so-tay): …` + dòng `Co-Authored-By:` của model đang thực thi), trên nhánh task tạo từ `main`. Không push, không merge, không `bd` ghi.

## Phản hồi review vòng 1 (Codex đợt 9, 18/10/2026)

**Ánh xạ task:** Task 1 mới = Task 2 cũ (bộ đọc, sửa parser + thêm ngữ cảnh); Task 2 mới = Task 3 cũ (nối cổng — bản vá giữ nguyên, chỉ đổi chữ docstring); Task 3 mới = Task 1 cũ (kịch bản G3.8–G3.10 viết lại thành tệp có test, sổ tay chỉ dẫn tới nó); Task 4 cũ BỎ, thay bằng mục "Việc sau G3 bổ sung" (không mã trong plan này). Đổi thứ tự vì kịch bản gọi `xet_user` và `ngu_canh_hien_hanh` của Task 1.

| # | Mức | Phát hiện | Sửa | Bằng chứng chạy thật |
|---|---|---|---|---|
| 1 | Chặn | G3.9 có thể ghi "từ chối" khi phép thử chưa hoạt động (mã ≠ 0 bất kỳ, `print \| grep -c` không kiểm mã, submit không buộc thành công/vị trí) | Kịch bản Task 3: (a) xác minh UID (số, ≠ 0, ≠ UID vận hành) trước mọi lệnh dưới tram-kiem; (b) ASID từ `procinfo` → `audit info → session id` phải BẰNG `handle` của `gui/<uid vận hành>`, không thì dừng; (c) **đối chứng dương**: cùng loại plist nạp vào `user/<uid>` của tram-kiem phải mã 0, thấy đúng một dòng nhãn, gỡ xong không còn — không đạt thì KHÔNG thử miền của Đại ca; (d) MỌI lệnh `print` dùng để đếm đều kiểm mã 0 trước; (e) submit phải mã 0 và thấy ĐÚNG MỘT chỗ (`user/<uid>`), mọi nhãn thử khác không xuất hiện; (f) đầu ra chỉ là "ỨNG VIÊN ĐẠT" / "KHÔNG KẾT LUẬN" / "GHI ĐƯỢC … DỪNG S6" — **không kịch bản nào kết luận "launchd từ chối"**; chữ lỗi do Em + Codex phân loại từ đầu ra đo (không đoán mã/chữ trong mã); (g) bằng chứng chỉ vào mã qua plan nhỏ, gắn đúng ngữ cảnh (mục 4) | `test_g3_bo_sung.py`: `test_dieu_kien_truoc_hong_thi_khong_thu_ghi_vao_mien_nguoi_van_hanh` (đối chứng dương hỏng, ASID lệch, print lỗi → mã 1, không có `bootstrap login/`/`gui/`), `test_submit_khong_thanh_cong_la_khong_ket_luan`, `test_submit_khong_biet_o_dau_…`, `test_ghi_duoc_vao_mien_nguoi_van_hanh_thi_dung_s6_va_go_nhan` (3 ca), `test_uid_tram_kiem_sai_…` (3 ca); đột biến bỏ từng điều kiện → đỏ (Task 3 Step 5) |
| 2 | Chặn | Kịch bản thiếu sở hữu tài nguyên, hạn, receipt, xử lý ngắt, dọn có kiểm; G3.8 gọi là "chỉ đọc" dù `kill -1` | Kịch bản là TỆP (`docs/handovers/g3-bo-sung.sh`), không còn chuỗi `;` trong bảng: nhãn `vn.tram.g3b.<lần>.*` và thư mục `$GOC/g3b-<lần>` riêng mỗi lần (`<lần>` = giờ + PID), chứng minh nhãn chưa có ở cả hai miền (print mã 0) và thư mục tạo MỚI (mkdir thất bại nếu đã có → dừng, không đụng); plist ghi bằng `tee` vào thư mục 0700 vừa tạo của tram-kiem (không có symlink cũ để theo); receipt ghi TRƯỚC mỗi thao tác tạo; mỗi lệnh có hạn `perl alarm`; lệnh hỏng → `dung` (không chạy bước sau); trap EXIT/INT/TERM → dọn một lần, bỏ qua ngắt trong lúc dọn, ghi ra fd riêng (bash 3.2 chạy trap trong redirect của lệnh đang dở — test bắt được lỗi này và khoá: bằng chứng không lẫn chữ dọn); dọn gỡ đúng nhãn trong receipt rồi in lại từng miền (mã 0, không còn nhãn), xoá thư mục, `kill -1` DƯỚI tram-kiem, hai lượt không còn tiến trình uid **và** ruid tram-kiem cách `CHO` giây; job submit không biết ở đâu → "CHƯA XÁC NHẬN"; chưa xác nhận → mã 3, giữ cổng đóng. G3.8 ghi rõ "kill -1 dưới tram-kiem, không phải chỉ đọc" | `test_moi_dieu_kien_dat_chi_la_ung_vien_va_don_co_xac_nhan` (receipt, thứ tự đối chứng dương trước, không lệnh nào ngoài danh sách cho phép của `sudo` giả), `test_bi_ngat_giua_chung_van_don_va_xac_nhan` (SIGTERM giữa `bootstrap login`), `test_go_nhan_khong_xac_nhan_duoc_thi_chua_xac_nhan`, `test_con_tien_trinh_tram_kiem_sau_don_thi_chua_xac_nhan`, `test_khong_gia_va_khong_terminal_thi_khong_chay_gi` |
| 3 | Quan trọng | Parser coi mất khối quan sát là không tàn dư (`k.get(x, [])`) | `launchd_dinh_dang.py`: lược đồ `KHOA` — mỗi khoá là KHỐI hoặc VÔ HƯỚNG với mẫu giá trị đo được (sai loại/mẫu → ValueError); `BAT_BUOC_USER` = khối/khoá có trong `user.txt` mà quan sát cần (`type`, `handle`, `session`, `security context`, `services`, `unmanaged processes`, `endpoints`, `task-special ports`); khối chỉ đo ở login là tuỳ chọn nhưng có mặt vẫn đúng lược đồ; `xet_user` đòi đủ `BAT_BUOC_USER` (thiếu → "định dạng … khác bản đã đo"), bỏ mặc định `[]` | `test_thieu_khoi_hay_khoa_bat_buoc_la_khong_quan_sat_duoc` (8 ca — xoá từng khoá/khối bắt buộc khỏi fixture đo được), `test_tach_lech_bo_cuc_da_do_thi_nem` (12 đột biến, có sai loại và sai mẫu); đột biến bỏ kiểm bắt buộc → 8 đỏ |
| 4 | Quan trọng | Mốc G3.9 theo build dùng rộng hơn ngữ cảnh đo | Tách: `MOC_USER` (mốc ĐỊNH DẠNG/nhãn theo build) và `BANG_CHUNG_LOGIN: frozenset[NguCanh]` (bằng chứng VẬN HÀNH theo ngữ cảnh đầy đủ). `NguCanh(ban, may, uid_kiem, uid_tram, do_hoa)` do trạm đọc từ OS (`ngu_canh_kiem.py`), không env. Ngữ cảnh hiện hành không có trong bằng chứng (khác máy, khác UID, chạy từ phiên nền, khác build) → ném TRƯỚC mọi lệnh; đọc ngữ cảnh lỗi → ném; UID chứng minh ≠ UID ngữ cảnh → ném. Kịch bản in đúng `repr` ngữ cảnh lúc đo để plan nhỏ chép nguyên | `test_ngu_canh_khac_bang_chung_hay_ban_chua_co_moc_thi_nem_truoc_moi_lenh` (4 ca), `test_khong_doc_duoc_ngu_canh_thi_nem` (3 ca), `test_uid_da_chung_minh_khac_ngu_canh_thi_nem`, `test_moc_may_b`, `test_ngu_canh_kiem.py` (8 test) |
| 7 | Nhỏ | Nguồn bằng chứng login chưa ghi ở sổ tay hiện hành | Task 3 sửa sổ tay: đoạn "Bổ sung G3.3" ghi nguồn (tệp Đại ca gửi từ `~/.tram/g3/` máy B), giờ đo theo dấu thời gian tệp, Đại ca xác nhận khi ghép; không coi test fixture là chứng thực nguồn OS | — (docs) |

Mục 5, 6, 8 của review thuộc plan A (V4), không thuộc plan này. Câu hỏi gộp 3 của Codex ("giữ đóng tới khi có bằng chứng đúng môi trường") trùng hướng của bản này: mặc định đóng, chỉ mở theo ngữ cảnh đã đo.

**Còn mở, ghi rõ:** chữ lỗi "từ chối quyền" của launchd chưa đo → chưa có mã phân loại (đúng yêu cầu "không đoán"); kịch bản chỉ đo ngữ cảnh Terminal (phiên Aqua) — trạm chạy từ dịch vụ nền sẽ là ngữ cảnh khác và cổng đóng tới khi có kịch bản cho phiên đó (chưa có); XPC gửi thẳng tới launchd ngoài hồ sơ không thử được bằng kịch bản shell — chỉ Seatbelt (G4 điều kiện 2).

## Bảng G — điều plan bảo đảm và bằng chứng

| # | Bảo đảm | Ở đâu | Bằng chứng offline | Còn chờ OS |
|---|---|---|---|---|
| G1 | Chỉ bố cục `launchctl print` đã đo được chấp nhận: tiêu đề đúng tên miền, khoá trong lược đồ đóng (hợp `user.txt` + `login.txt`), đúng loại (khối/vô hướng) và mẫu giá trị, không lặp, khối đóng đủ, không dòng trống trong khối, dòng dịch vụ đúng ba cột; lệch → `LoiBanChep` "định dạng … khác bản đã đo" | `launchd_dinh_dang.tach`, `xet_user` | `test_tach_doc_moi_kieu_khoi_da_do`, `test_tach_lech_bo_cuc_da_do_thi_nem` (12), `test_khong_phai_mien_rieng_cua_tram_kiem_hay_lech_dang_thi_nem` | G3.8: trạng thái ổn định còn đúng bố cục (`xet_user: sạch`) |
| G2 | Thiếu khối/khoá bắt buộc của miền user = không quan sát được (đóng), không bao giờ coi là rỗng | `BAT_BUOC_USER`, `xet_user` | `test_thieu_khoi_hay_khoa_bat_buoc_la_khong_quan_sat_duoc` (8) | — |
| G3 | `user/<uid>` chỉ là của `tram-kiem` khi `type = user`, `handle` = UID đã chứng minh, `session = Background`, `security context` đúng `uid`/`asid`; trong miền đó: dịch vụ ngoài mốc hoặc khối `unmanaged processes`/`endpoints`/`externally-hosted endpoints`/`environment`/`disabled services` có dòng → đóng | `xet_user` | `test_user_503_co_job_tien_trinh_hay_trang_thai_thi_nem_khong_chep_nhan` (5), `test_cong_luot_dong_khi_user_503_co_job` | G3.10 (job thật bị bắt); G4.3 |
| G4 | `gui/<uid>` chỉ sạch khi mã 125 VÀ đúng chữ đã đo; mã 0 hay khác → đóng | `doc_launchd` | `test_ma_thoat_hay_mien_gui_khac_ban_do_thi_nem` | G3.8: kênh stdout/stderr |
| G5 | `login/<asid>` KHÔNG bao giờ được in; ngữ cảnh hiện hành không có trong `BANG_CHUNG_LOGIN` → ném TRƯỚC mọi lệnh (hiện rỗng → luôn đóng) | `doc_launchd`, `BANG_CHUNG_LOGIN` | `test_user_503_do_that_sach_va_khong_bao_gio_in_login`, `test_ngu_canh_khac_bang_chung_…` (4), `test_moc_may_b` | **G3.9** + plan nhỏ |
| G6 | Ngữ cảnh do trạm tự đọc từ OS (build, máy, UID kiểm, UID trạm, loại phiên); lỗi đọc → đóng; UID chứng minh ≠ UID ngữ cảnh → đóng | `ngu_canh_kiem`, `doc_launchd` | `test_ngu_canh_kiem.py` (8), `test_khong_doc_duoc_ngu_canh_thi_nem` (3), `test_uid_da_chung_minh_khac_ngu_canh_thi_nem` | — |
| G7 | Lệnh dưới `tram-kiem` chỉ qua `CongLich`; lỗi danh tính/thu hồi/quá hạn → thông báo cố định; cơ chế `sandbox` → ném, không chạy gì | `_ra`, `doc_launchd` | `test_loi_chay_thanh_thong_bao_co_dinh`, `test_ngu_canh_khac_…` | — |
| G8 | Thông báo chỉ mang số đếm, tên khối cố định, mã thoát — không nhãn/đầu ra do `tram-kiem` điều khiển | `xet_user` | assert `"com.apple" not in str(e)` | — |
| G9 | Cổng thật luôn dùng bộ đọc đã đo | `cong_that.dung_cong` | `test_dung_cong_du_quan_sat_va_thu_hoi_mac_dinh_khong_go_lich` | G4.0 |
| G10 | Kịch bản G3 bổ sung (bản rút gọn D117): không có Terminal/`dong-y` → không chạy; tram-kiem phải không có tiến trình lúc bắt đầu (có → in, dừng, không giết); bảng `ps` hỏng → không bao giờ đếm 0; mọi bước G3.8 + ASID đạt rõ ràng, không thì dừng trước mọi lệnh ghi; đối chứng dương có bộ đọc thật bắt đúng job và sạch sau gỡ; ghi được vào miền Đại ca ở phép nào → dừng ngay, mã 4; chỉ "ỨNG VIÊN"; dọn đếm lại 5 lần, còn sót/không đếm được/procinfo lỗi → không báo sạch; bị ngắt hay hết hạn tổng vẫn dọn | `docs/handovers/g3-bo-sung.sh` | `test_g3_bo_sung.py` (33; khoá độc quyền, lỗi đọc biên nhận/ghi bảng tổng → không sạch/dừng) | chạy thật (Đại ca cho phép) |

## Phân tích dữ liệu đo G3 (máy B, 18/10/2026)

### Tệp đã đọc (chỉ đọc, bản chép Đại ca gửi)

| Tệp | Lệnh (Đại ca chạy) | Mã | Nội dung chính |
|---|---|---|---|
| `user.txt` (33 dòng) | `TK /bin/launchctl print user/503` (ngoài hồ sơ) | 0 | tiêu đề `user/503 = {`; `type = user`, `handle = 503`, `creator = launchctl[85554]`, `creator euid = 503`, `session = Background`, `security context = { uid = 503, asid = 100172 }`, `in-progress bootstraps = 1`, `external activation count = 1`; khối `services`, `unmanaged processes`, `endpoints` RỖNG; `task-special ports` 2 dòng; `properties = ` (rỗng) |
| `gui.txt` (1 dòng) | `TK /bin/launchctl print gui/503` | 125 | `Could not print domain: 125: Domain does not support specified action` (ghi bằng `2>&1` — không biết kênh) |
| `procinfo.txt` | `sudo launchctl procinfo <pid sleep>` (D52) | 0 | tiến trình `uid = ruid = 503`, KHÔNG có trường `asid` (macOS 15); `audit info → session id = 100003, uid = 501`, `flags = has_graphic_access,…`; `responsible path = …/Terminal`; "not managed by launchd" |
| `login.txt` (2332 dòng) | `TK /bin/launchctl print login/100003` | 0 | tiêu đề **`gui/501 = {`**, `type = login`, `handle = 100003`, `creator = loginwindow[168]`, `session = Aqua`, `endpoint destination = com.apple.xpc.launchd.domain.user.501`, `security context = { uid = 501, asid = 100003 }`; khối `environment` (đường socket ssh-agent), 420 dòng dịch vụ, 24 khối `unmanaged processes`, 1253 dòng `externally-hosted endpoints`, 14 dòng `disabled services` (nhiều ứng dụng bên thứ ba, ứng dụng cá nhân) |
| `g3.log`, sổ tay | — | — | G3.4: một tiến trình uid 503 cha là launchd (pid 85559) xuất hiện giữa lệnh print (85554) và `sudo sleep` (85557); sau G3.6 lại thấy 1 tiến trình uid 503 — launchd sinh agent dưới `tram-kiem` khi tài khoản có hoạt động |

Dạng dòng đo được (tab là `\t`): dịch vụ `\t\t<pid canh phải> <trạng thái canh phải> \t<nhãn>` — pid `0` là không chạy; trạng thái `-`, số (`0`, `78`), số âm (`-11`) hoặc `(jt)`. Tiến trình unmanaged: khối `\t\tcom.apple.xpc.launchd.unmanaged.<tên>.<pid> = {` lồng tới 5 tab. Bật/tắt: `\t\t"<nhãn>" => enabled|disabled`. Không dòng nào mang uid của TỪNG mục. Máy của Em (cùng bản 24G90, chỉ đọc): `SessionGetInfo(callerSecuritySession)` trả session 100003, cờ `0x6030` (có `sessionHasGraphicAccess` 0x10 và `sessionHasTTY` 0x20 theo `AuthSession.h`) — cùng số phiên mà `procinfo` đọc được cho tiến trình dưới sudo.

### Mục do `tram-kiem` tạo sẽ hiện ở đâu, quy về `tram-kiem` thế nào

| Miền | Đo được | Quy về `tram-kiem` | Bộ đọc |
|---|---|---|---|
| `user/503` | Miền riêng: `handle = 503`, `security context uid = 503`, `session = Background`, asid riêng 100172. Miền do CHÍNH lệnh print tạo, đang bootstrap dở (`in-progress bootstraps = 1`) | **Theo miền**: mọi mục trong miền này là của `tram-kiem`. `launchctl bootstrap "user/$(id -u)"` của kịch bản tái sinh rơi vào đây | In, xét nghiêm (G1–G3). Trạng thái ổn định đo ở G3.8 |
| `gui/503` | Không tồn tại (mã 125) | Nếu tồn tại thì của `tram-kiem`, nhưng định dạng chưa đo và lẽ ra không có | In; chỉ dạng 125 đã đo là sạch (G4) |
| `login/<asid>` | asid của tiến trình `tram-kiem` = audit session của người gọi `sudo` (Terminal của Đại ca, 100003) = **phiên Aqua của Đại ca** (tiêu đề `gui/501`, uid 501). `tram-kiem` ĐỌC được nó | **Không quy được**: không có uid từng mục; job hẹn giờ/chưa chạy có pid 0; nhãn đặt tuỳ ý nên lọc theo nhãn là "xanh vì vắng dấu" (phụ lục đợt 7 cấm) | **Không in** (G5). Thay bằng bằng chứng G3.9 theo ngữ cảnh + Seatbelt |
| legacy `submit` | Chưa đo nơi rơi | — | Kịch bản Task 3 tìm job submit, phải thấy đúng một chỗ |

### Ba cách xử lý miền `login/<asid>` (chọn A — GIẢ ĐỊNH chờ Đại ca, Câu hỏi 1)

| Cách | Làm gì | Hệ quả |
|---|---|---|
| **A (đề xuất, đang dùng)** | Không in miền đăng nhập. Đòi bằng chứng OS cho ĐÚNG ngữ cảnh (G3.9 qua kịch bản Task 3 + phân loại chữ lỗi + plan nhỏ). Ranh giới vẫn là Seatbelt (`job-creation`, cấm exec `launchctl` — G4 điều kiện 2) | Không đọc dữ liệu riêng của Đại ca khi quan sát; cổng chỉ mở được ở ngữ cảnh đã đo |
| B | In miền đăng nhập, so danh sách nhãn với mốc | Đóng cổng giả liên tục (~420 dịch vụ đổi theo ứng dụng Đại ca mở); phải lưu danh sách ứng dụng cá nhân; vẫn không quy được |
| C | Coi miền đăng nhập là "không kết luận" vĩnh viễn | Cổng kiểm lại không bao giờ mở với cơ chế `user` → S6/G4 không chạy được; phải đổi kiến trúc |

**Rủi ro còn lại của A:**
1. Kịch bản chỉ thử `bootstrap` (hai dạng tên miền) và `submit` qua `launchctl`; XPC gửi thẳng ngoài hồ sơ không thử — chỉ Seatbelt chặn (G4 điều kiện 2).
2. Bằng chứng gắn ngữ cảnh; Apple đổi hành vi ở bản sau → khác `ban` → cổng đóng tới khi đo lại (fail-closed).
3. Kịch bản đo ngữ cảnh Terminal (Aqua). Trạm chạy thật từ dịch vụ nền là ngữ cảnh khác (`do_hoa` khác) → cổng đóng; kịch bản cho phiên nền chưa có.
4. Lệnh `print user/<uid>` tạo miền và có thể làm launchd sinh agent dưới `tram-kiem` (pid 85559 ở G3.4). Nếu vậy, lượt quan sát thứ hai của `ra()` thấy tiến trình ở `tien_trinh` → **cổng đóng giả** (fail-closed). Kịch bản G3.8 đo (`ps-sau`).
5. Mốc `user` rỗng đo lúc bootstrap dở; nếu trạng thái ổn định có dịch vụ hệ thống → cổng đóng giả tới khi ghi mốc (Câu hỏi 4).
6. `tram-kiem` (ngoài hồ sơ) đọc được danh sách dịch vụ trong phiên của Đại ca, gồm đường socket ssh-agent — rò thông tin sang tài khoản cách ly. Mã agent trong lượt bị hồ sơ cấm exec `launchctl` (G3.2); XPC đọc thẳng chưa đo. Giả định chờ Đại ca (Câu hỏi 3): chấp nhận + bead xét đổi cách chạy sau S2.

## Thiết kế bộ đọc

**Luồng `doc_launchd(pk, *, chay=None, ngu_canh=ngu_canh_hien_hanh, moc=None, bang_chung=None)`:**
1. `pk.co_che == "sandbox"` → ném (hồ sơ ghim cấm exec `launchctl`, G3.2) — không chạy gì.
2. `nc = ngu_canh(pk.ten)` — trạm đọc build, máy, UID kiểm (`pwd`), UID trạm, loại phiên; lỗi (`KeyError`/`OSError`/`ValueError`) → ném.
3. `MOC_USER[nc.ban]` không có → ném "chưa có mốc launchd cho macOS …".
4. `nc not in BANG_CHUNG_LOGIN` → ném "login/<asid>: chưa có bằng chứng G3.9 cho ngữ cảnh này …" — TRƯỚC mọi lệnh.
5. `cong = chay or mo_cong_kiem(pk)` (`CongLich`, UID thực đã chứng minh); `cong.uid != nc.uid_kiem` → ném.
6. `launchctl print user/<uid>` dưới `tram-kiem`: mã ≠ 0 → ném; `xet_user(stdout+stderr, uid, MOC_USER[ban])` — đủ `BAT_BUOC_USER`, đúng danh tính miền, không dịch vụ ngoài mốc, mọi khối trạng thái rỗng.
7. `launchctl print gui/<uid>`: mã 0 → ném; mã ≠ 125 hoặc chữ ≠ bản đo → ném.
8. KHÔNG có lệnh nào nhắm `login/`.

**Nối vào cổng:** `dung_cong` cắm `partial(launchd, pk, doc=doc_launchd)` ở cuối danh sách quan sát. `CongLuot` gọi ở `vao` (một lượt) và `ra`/`mo_lai` (hai lượt cách `cho`); harness `_don` gọi hai lượt. Mọi `LoiBanChep` → `CongDong`, `cong.json` = `dong` kèm lý do.

**Mốc và bằng chứng theo D45:** `MOC_USER: dict[build, frozenset[nhãn]]` = nhãn ĐÚNG TÊN (không tiền tố) được phép trong `services` của `user/<uid>` — chỉ hỗ trợ quan sát, thiếu = chặt nhất. `BANG_CHUNG_LOGIN: frozenset[NguCanh]` = các ngữ cảnh đã có bằng chứng G3.9 được phân loại — rỗng. Đổi cả hai chỉ qua commit có review; không có lệnh CLI chụp mốc (chụp tự động có thể hợp thức hoá job agent đã cài).

**Đọc gộp stdout + stderr:** G3 ghi `2>&1`, nên dạng đo là luồng gộp; kịch bản G3.8 tách hai kênh để ghi lại. Văn bản lạ ở kênh nào cũng làm `tach` ném.

### Fixture — rút gọn và khử thông tin cá nhân thế nào

| Tệp | Nguồn | Xử lý | sha256 |
|---|---|---|---|
| `tests/du_lieu/launchd/user-503.txt` | `user.txt` | **Nguyên văn** (33 dòng; miền của `tram-kiem`, chỉ có số pid/port của lần đo; giữ cả dấu cách cuối dòng `\tproperties = `) | `df1c1c6fbf4c43e32771482c84a7bdf1f25fea0aa5b028119025a38f168a56eb` |
| `tests/du_lieu/launchd/gui-503.txt` | `gui.txt` | **Nguyên văn** (1 dòng) | `66ad88d0b5f09a53d05c9aeba4581c40d59499cb2ac8124765b7e7db04d8567b` |
| `tests/du_lieu/launchd/login-rut-gon.txt` | `login.txt` (2332 dòng) | **Rút gọn còn 72 dòng**, giữ đúng từng byte các dòng giữ lại: dòng 1–18 (tiêu đề → `death port`); **bỏ khối `environment`** (đường socket ssh-agent); `services`: 4/420 dòng `com.apple.*` phủ mọi dạng cột trạng thái (`-`, `0`, `(jt)`, `-11`); `unmanaged processes`: 1/24 khối (Dock, `com.apple`, 23 dòng, lồng 5 tab); `endpoints` rỗng nguyên; `externally-hosted endpoints`: 2/1253 dòng `com.apple.*` (cờ `A`, `D`); `task-special ports` nguyên; `disabled services`: 2/14 dòng `com.apple.*` — **bỏ mọi nhãn bên thứ ba và ứng dụng cá nhân** (12 dòng còn lại; không liệt kê tên ở đây vì chính danh sách đó là thông tin cá nhân); `properties` nguyên. Số đếm giữ như đo, không khớp số dòng đã rút. Test `test_fixture_dung_ban_do_va_da_khu_thong_tin_ca_nhan` khoá: mọi chuỗi dạng tên miền ngược đều `com.apple.*`, không có `/` sau dòng tiêu đề, không có `environment` | `c57018cfaab6dec47ac1351b40bbaa6dfce0c4eca05f841e52f9b83300139d3e` |

Tái tạo `login-rut-gon.txt` từ tệp đo (trên máy B, chỉ đọc; cho reviewer đối chiếu):

```sh
G=~/.tram/g3/login.txt
{ sed -n '1,18p' $G; printf '\n'
  printf '\tservices = {\n'; sed -n '25p;27p;130p;298p' $G; printf '\t}\n\n'
  printf '\tunmanaged processes = {\n'; sed -n '463,485p' $G; printf '\t}\n\n'
  sed -n '1050,1053p' $G; sed -n '1054p;1065p' $G; printf '\t}\n\n'
  sed -n '2309,2313p' $G
  printf '\tdisabled services = {\n'; sed -n '2316p;2327p' $G; printf '\t}\n\n'
  sed -n '2331,2332p' $G; } > login-rut-gon.txt
```

Ca "có job/tiến trình/trạng thái" và "thiếu khối" trong `user/503` chưa có đầu ra đo riêng: test GHÉP dòng ĐO ĐƯỢC của miền login vào khối rỗng của `user-503.txt` đo được (`ghep`), hoặc XOÁ khối khỏi nó (`bo`); riêng dòng `environment` dùng `\t\tTRAM_THU => 1` theo đúng dạng `KHOÁ => giá trị` đo được. Không có fixture nào là đầu ra tự suy từ máy khác. Kịch bản Task 3 (G3.10) chạy `xet_user` trên đầu ra thật `user/<uid>` có một job.

## Task 1 — Bộ đọc: lược đồ bố cục, ngữ cảnh vận hành, `doc_launchd` + fixture đo thật (RED→GREEN thật)

**Files:**
- Create: `tests/du_lieu/launchd/user-503.txt`, `tests/du_lieu/launchd/gui-503.txt`, `tests/du_lieu/launchd/login-rut-gon.txt`
- Create: `tests/test_launchd_kiem.py`, `tests/test_ngu_canh_kiem.py`
- Create: `tram/giao_viec/launchd_dinh_dang.py`, `tram/giao_viec/ngu_canh_kiem.py`, `tram/giao_viec/launchd_kiem.py`

**Interfaces:**
- Produces: `launchd_kiem.doc_launchd(pk, *, chay: Callable | None = None, ngu_canh: Callable[[str], NguCanh] = ngu_canh_hien_hanh, moc: dict | None = None, bang_chung: frozenset | None = None) -> None` — bộ đọc cho `quan_sat_kiem.launchd(pk, doc=…)`; sạch thì trả, còn lại `LoiBanChep`. `xet_user(van_ban, uid, moc: frozenset[str]) -> None`; hằng `MOC_USER`, `BANG_CHUNG_LOGIN`, `GUI_KHONG`, `PHAI_RONG`, `LAUNCHCTL`.
- Produces: `launchd_dinh_dang.tach(van_ban, ten) -> dict[str, str | list[str]]` (ValueError khi lệch), `KHOA`, `BAT_BUOC_USER`, `DONG_DV`.
- Produces: `ngu_canh_kiem.NguCanh(ban, may, uid_kiem, uid_tram, do_hoa)`, `ngu_canh_hien_hanh(ten_kiem) -> NguCanh`, `ban_macos(tep=SYS_VER)`, `ma_may()`, `phien_do_hoa()`.
- Consumes: `quan_sat_kiem.HAN`, `quan_sat_kiem.mo_cong_kiem`, `CongLich` (`.uid`, `__call__`), `danh_tinh.uid_cua`, `LoiDanhTinh`, `LoiThuHoi`.

- [ ] **Step 1: Tạo ba fixture (nguyên văn — tab là ký tự tab, `user-503.txt` có dấu cách cuối dòng `properties = `)**

`tests/du_lieu/launchd/user-503.txt`:

<!-- ap: tao tests/du_lieu/launchd/user-503.txt -->
```text
user/503 = {
	type = user
	handle = 503
	active count = 3
	creator = launchctl[85554]
	creator euid = 503
	session = Background
	external activation count = 1
	security context = {
		uid = 503
		asid = 100172
	}

	death port = 0x0
	in-progress bootstraps = 1

	services = {
	}

	unmanaged processes = {
	}

	endpoints = {
	}

	task-special ports = {
			 0xef33f 4       bootstrap  com.apple.xpc.launchd.domain.user.503
			  0x2203 9          access  (unknown)
	}


	properties = 
}
```

`tests/du_lieu/launchd/gui-503.txt`:

<!-- ap: tao tests/du_lieu/launchd/gui-503.txt -->
```text
Could not print domain: 125: Domain does not support specified action
```

`tests/du_lieu/launchd/login-rut-gon.txt`:

<!-- ap: tao tests/du_lieu/launchd/login-rut-gon.txt -->
```text
gui/501 = {
	type = login
	handle = 100003
	active count = 421
	service count = 420
	active service count = 232
	creator = loginwindow[168]
	creator euid = 0
	session = Aqua
	endpoint destination = com.apple.xpc.launchd.domain.user.501
	auxiliary bootstrapper = com.apple.xpc.otherbsd (complete)
	security context = {
		uid = 501
		asid = 100003
	}

	bringup time = 47 ms
	death port = 0x14103

	services = {
		     462      - 	com.apple.syncdefaultsd
		       0      0 	com.apple.DataDetectorsLocalSources
		   32840   (jt) 	com.apple.knowledgeconstructiond
		   45102    -11 	com.apple.sharingd
	}

	unmanaged processes = {
		com.apple.xpc.launchd.unmanaged.com.apple.dock..37536 = {
			active count = 3
			dynamic endpoints = {
			}
			pid-local endpoints = {
				"com.apple.tsm.portname" = {
					port = 0xf0103
					active = 1
					managed = 0
					reset = 0
					hide = 0
					watching = 0
				}
				"com.apple.axserver" = {
					port = 0xd190b
					active = 1
					managed = 0
					reset = 0
					hide = 0
					watching = 0
				}
			}
		}
	}

	endpoints = {
	}

	externally-hosted endpoints = {
		 0xf652f    M   A   com.apple.BKAgentService
		       0    M   D   com.apple.FontObjectsServer
	}

	task-special ports = {
			 0x17803 4       bootstrap  com.apple.xpc.launchd.user.domain.501.100003.Aqua
			  0x2203 9          access  (unknown)
	}

	disabled services = {
		"com.apple.ManagedClientAgent.enrollagent" => disabled
		"com.apple.appleseed.seedusaged.postinstall" => disabled
	}

	properties = gui | gui login
}
```

Run: `shasum -a 256 tests/du_lieu/launchd/*.txt`
Expected: đúng ba giá trị ở bảng "Fixture". Lệch → tạo lại, KHÔNG sửa test cho khớp.

- [ ] **Step 2: Viết test**

`tests/test_launchd_kiem.py` (mới):

<!-- ap: tao tests/test_launchd_kiem.py -->
```python
"""3C-D7: bộ đọc launchd của `tram-kiem` CHỈ cho định dạng đo ở G3 (máy B 18/10, 24G90). Fixture `du_lieu/launchd/`:
`user-503.txt`, `gui-503.txt` nguyên văn; `login-rut-gon.txt` = `print login/100003` (phiên GUI của người vận hành) RÚT
GỌN + khử thông tin cá nhân (bỏ khối environment, dịch vụ/tiến trình/endpoint ngoài `com.apple.*`). Ca "có job" ghép
dòng ĐO ĐƯỢC của miền login vào khung user đo được. `CongLich` dựng trực tiếp, `chay` giả, ngữ cảnh giả: không chạy
launchctl/sudo, không đọc OS."""
import re
import subprocess
from functools import partial
from pathlib import Path

import pytest

from tram.giao_viec.ban_chep import LoiBanChep
from tram.giao_viec.cong_luot import CongDong, CongLuot
from tram.giao_viec.launchd_dinh_dang import BAT_BUOC_USER, DONG_DV, tach
from tram.giao_viec.launchd_kiem import BANG_CHUNG_LOGIN, MOC_USER, doc_launchd
from tram.giao_viec.ngu_canh_kiem import NguCanh
from tram.giao_viec.principal_kiem import tu_cach_ly
from tram.giao_viec.quan_sat_kiem import launchd
from tram.kiem.cong_lich import CongLich

DL = Path(__file__).parent / "du_lieu" / "launchd"
USER, GUI, LOGIN = ((DL / t).read_text(encoding="utf-8") for t in ("user-503.txt", "gui-503.txt", "login-rut-gon.txt"))
PK = tu_cach_ly("user:tram-kiem")
NC = NguCanh("24G90", "0123456789abcdef", 503, 501, True)          # ngữ cảnh giả "đã đạt G3.9"
DV = [d for d in LOGIN.split("\n") if DONG_DV.fullmatch(d)]       # 4 dòng dịch vụ đo được (-, 0, (jt), -11)


def cong(*kq, uid=503):
    goi, con = [], list(kq)

    def chay(argv, **kw):
        goi.append(argv)
        return subprocess.CompletedProcess(argv, *con.pop(0))
    return CongLich(tuple(PK.boc_lenh([])), uid, chay), goi


def doc(c, *, nc=NC, moc=None, bang_chung=frozenset({NC}), pk=PK):
    return doc_launchd(pk, chay=c, ngu_canh=lambda ten: nc, moc=moc, bang_chung=bang_chung)


def ghep(khoa, dong, van_ban=USER):
    """Đổ dòng đo được vào khối rỗng `khoa` của `user-503.txt` (khối chưa có thì thêm trước `endpoints`)."""
    rong = f"\t{khoa} = {{\n\t}}\n"
    van_ban = van_ban if rong in van_ban else van_ban.replace("\tendpoints = {", rong + "\n\tendpoints = {")
    return van_ban.replace(rong, f"\t{khoa} = {{\n" + "".join(d + "\n" for d in dong) + "\t}\n")


def bo(khoa, van_ban=USER):
    """Xoá nguyên khoá `khoa` (dòng vô hướng, hoặc cả khối tới `\\t}` đầu tiên) khỏi `user-503.txt`."""
    i = van_ban.index(f"\n\t{khoa} = ") + 1
    j = van_ban.index("\n\t}\n", i) + 4 if van_ban[i:].split("\n", 1)[0].endswith("{") else van_ban.index("\n", i) + 1
    return van_ban[:i] + van_ban[j:]


def test_fixture_dung_ban_do_va_da_khu_thong_tin_ca_nhan():
    assert USER.startswith("user/503 = {\n\ttype = user\n\thandle = 503\n") and "\tservices = {\n\t}\n" in USER
    assert GUI == "Could not print domain: 125: Domain does not support specified action\n"
    assert "environment" not in LOGIN and "/" not in LOGIN.partition("\n")[2] and len(DV) == 4
    assert all(t.startswith("com.apple.") for t in re.findall(r"[A-Za-z]+\.[A-Za-z]+\.[\w.-]+", LOGIN))


def test_tach_doc_moi_kieu_khoi_da_do():
    k = tach(LOGIN, "gui/501")
    assert (k["type"], k["handle"], k["session"], k["properties"]) == ("login", "100003", "Aqua", "gui | gui login")
    assert len(k["services"]) == 4 and len(k["unmanaged processes"]) == 23 and k["endpoints"] == []
    u = tach(USER, "user/503")
    assert u["properties"] == "" and u["security context"] == ["\t\tuid = 503", "\t\tasid = 100172"]
    assert all(x in u for x in BAT_BUOC_USER)


@pytest.mark.parametrize("sua", [lambda s: s.replace("user/503 = {", "user/504 = {"),
                                 lambda s: s.replace("\tendpoints = {", "\tpending jobs = {\n\t}\n\tendpoints = {"),
                                 lambda s: s.replace("\tsession = Background\n", "\tsession = Background\n" * 2),
                                 lambda s: s.replace("\tservices = {\n\t}", "\tservices = {\n\n\t}"),
                                 lambda s: s.rstrip("\n").removesuffix("}"), lambda s: s.replace("\t}\n", "", 1),
                                 lambda s: s.replace("\ttype = user", "type = user"),
                                 lambda s: s.replace("\tservices = {\n\t}", "\tservices = 0"),
                                 lambda s: s.replace("\ttype = user", "\ttype = {\n\t}"),
                                 lambda s: s.replace("\thandle = 503", "\thandle = 503x"),
                                 lambda s: s.replace("\tdeath port = 0x0", "\tdeath port = 0"),
                                 lambda s: s.replace("\tcreator = launchctl[85554]", "\tcreator = launchctl")])
def test_tach_lech_bo_cuc_da_do_thi_nem(sua):
    with pytest.raises(ValueError):
        tach(sua(USER), "user/503")


def test_user_503_do_that_sach_va_khong_bao_gio_in_login():
    c, goi = cong((0, USER, ""), (125, "", GUI))
    doc(c)
    assert goi == [PK.boc_lenh(["/bin/launchctl", "print", "user/503"]), PK.boc_lenh(["/bin/launchctl", "print",
                                                                                      "gui/503"])]
    assert not any("login" in a for argv in goi for a in argv)


@pytest.mark.parametrize("khoa", BAT_BUOC_USER)
def test_thieu_khoi_hay_khoa_bat_buoc_la_khong_quan_sat_duoc(khoa):
    assert khoa not in tach(bo(khoa), "user/503")                  # tach vẫn đọc được — xet_user phải từ chối
    with pytest.raises(LoiBanChep, match="định dạng launchctl print khác bản đã đo"):
        doc(cong((0, bo(khoa), ""))[0])


@pytest.mark.parametrize("van_ban, khop", [
    (ghep("services", DV[:2]), "2 dịch vụ launchd ngoài mốc"),
    (ghep("unmanaged processes", tach(LOGIN, "gui/501")["unmanaged processes"]), "'unmanaged processes' có 23 dòng"),
    (ghep("endpoints", ['\t\t"com.apple.tsm.portname" = {', "\t\t}"]), "'endpoints' có 2"),
    (ghep("disabled services", tach(LOGIN, "gui/501")["disabled services"]), "'disabled services' có 2"),
    (ghep("environment", ["\t\tTRAM_THU => 1"]), "'environment' có 1")])
def test_user_503_co_job_tien_trinh_hay_trang_thai_thi_nem_khong_chep_nhan(van_ban, khop):
    with pytest.raises(LoiBanChep, match=khop) as e:
        doc(cong((0, van_ban, ""))[0])
    assert "com.apple" not in str(e.value) and "TRAM_THU" not in str(e.value)


def test_moc_chi_tha_nhan_da_ghi_nhan():
    moc = {"24G90": frozenset({"com.apple.syncdefaultsd"})}
    doc(cong((0, ghep("services", DV[:1]), ""), (125, GUI, ""))[0], moc=moc)
    with pytest.raises(LoiBanChep, match="1 dịch vụ"):
        doc(cong((0, ghep("services", DV[:2]), ""))[0], moc=moc)


@pytest.mark.parametrize("sua", [lambda s: s.replace("domain.user.503", "domain.user.504"),
                                 lambda s: s.replace("bootstrap", "khac"),
                                 lambda s: s.replace("(unknown)", "khac"),
                                 lambda s: "\t\trac", lambda s: ""])
def test_task_special_ports_lech_mau_da_do_thi_dong(sua):
    cu = "\n".join(tach(USER, "user/503")["task-special ports"])
    with pytest.raises(LoiBanChep, match="định dạng launchctl print khác bản đã đo"):
        doc(cong((0, USER.replace(cu, sua(cu)), ""))[0])


@pytest.mark.parametrize("van_ban", [LOGIN, USER.replace("handle = 503", "handle = 504"), USER.replace(
    "Background", "Aqua"), USER.replace("uid = 503", "uid = 501"), ghep("services", ["\t\t0 - com.apple.x"]), ""])
def test_khong_phai_mien_rieng_cua_tram_kiem_hay_lech_dang_thi_nem(van_ban):
    with pytest.raises(LoiBanChep, match="định dạng launchctl print khác bản đã đo"):
        doc(cong((0, van_ban, ""))[0])


@pytest.mark.parametrize("kq, khop", [([(1, "", "")], "user/503: launchctl print mã 1"),
                                      ([(0, USER, ""), (0, LOGIN, "")], "có miền GUI"),
                                      ([(0, USER, ""), (125, "", "Could not print domain: 125\n")], "mã 125"),
                                      ([(0, USER, ""), (113, "", GUI)], "mã 113")])
def test_ma_thoat_hay_mien_gui_khac_ban_do_thi_nem(kq, khop):
    with pytest.raises(LoiBanChep, match=khop):
        doc(cong(*kq)[0])


def test_loi_chay_thanh_thong_bao_co_dinh():
    def treo(argv, **kw):
        raise subprocess.TimeoutExpired(["launchctl"], 120)
    with pytest.raises(LoiBanChep, match=r"không xác nhận được \(TimeoutExpired\)"):
        doc(CongLich(tuple(PK.boc_lenh([])), 503, treo))


def test_moc_may_b():
    assert MOC_USER == {"24G90": frozenset()}                      # máy B 18/10: user/503 không dịch vụ (G3.3)
    assert BANG_CHUNG_LOGIN == frozenset()                         # G3.9 chưa đo: mọi ngữ cảnh đều đóng


@pytest.mark.parametrize("nc, khop", [(NguCanh("24G90", "0123456789abcdef", 503, 501, False), "G3.9"),
                                      (NguCanh("24G90", "fedcba9876543210", 503, 501, True), "G3.9"),
                                      (NguCanh("24G90", "0123456789abcdef", 503, 504, True), "G3.9"),
                                      (NguCanh("25A354", "0123456789abcdef", 503, 501, True), "chưa có mốc")])
def test_ngu_canh_khac_bang_chung_hay_ban_chua_co_moc_thi_nem_truoc_moi_lenh(nc, khop):
    c, goi = cong()
    with pytest.raises(LoiBanChep, match=khop):
        doc(c, nc=nc)
    with pytest.raises(LoiBanChep, match="G3.9"):
        doc(c, bang_chung=frozenset())
    with pytest.raises(LoiBanChep, match="sandbox"):
        doc(c, pk=tu_cach_ly("sandbox:tram-kiem"))
    assert goi == []


@pytest.mark.parametrize("loi", [KeyError("tram-kiem"), OSError("gethostuuid lỗi"), ValueError("plist")])
def test_khong_doc_duoc_ngu_canh_thi_nem(loi):
    def hong(ten):
        raise loi
    c, goi = cong()
    with pytest.raises(LoiBanChep, match="không xác định được ngữ cảnh"):
        doc_launchd(PK, chay=c, ngu_canh=hong, bang_chung=frozenset({NC}))
    assert goi == []


def test_uid_da_chung_minh_khac_ngu_canh_thi_nem():
    c, goi = cong(uid=504)
    with pytest.raises(LoiBanChep, match="UID đã chứng minh khác"):
        doc(c)
    assert goi == []


def test_cong_luot_dong_khi_user_503_co_job(tmp_path):
    d = partial(doc, cong((0, ghep("services", DV[:1]), ""))[0])
    c = CongLuot(tmp_path / "cong.json", thu_hoi=lambda: None, quan_sat=[partial(launchd, PK, doc=lambda pk: d())],
                 ngu=lambda s: None)
    with pytest.raises(CongDong):
        c.mo_lai()
    assert c.trang_thai()["trang_thai"] == "dong" and "1 dịch vụ launchd" in c.trang_thai()["ly_do"]
```

`tests/test_ngu_canh_kiem.py` (mới):

<!-- ap: tao tests/test_ngu_canh_kiem.py -->
```python
"""3C-D7 (review đợt 9 vòng 1 mục 4): ngữ cảnh vận hành do TRẠM tự đọc từ OS — chỉ đọc (plist của root, `gethostuuid`,
`SessionGetInfo` của chính tiến trình test); không env, không lệnh hệ thống, không sudo."""
import ctypes
import os
import plistlib
import re

import pytest

from tram.giao_viec.ngu_canh_kiem import NguCanh, ban_macos, ma_may, ngu_canh_hien_hanh, phien_do_hoa


def test_ban_macos_chi_nhan_build_hop_le(tmp_path):
    p = tmp_path / "SystemVersion.plist"
    p.write_bytes(plistlib.dumps({"ProductBuildVersion": "24G90", "ProductVersion": "15.6.1"}))
    assert ban_macos(p) == "24G90"
    for nd in (plistlib.dumps({"ProductBuildVersion": "24G90/../x"}), plistlib.dumps({"ProductVersion": "15"}),
               plistlib.dumps({"ProductBuildVersion": 24})):
        p.write_bytes(nd)
        with pytest.raises(ValueError):
            ban_macos(p)
    p.write_bytes(b"rac")
    with pytest.raises(ValueError):
        ban_macos(p)
    with pytest.raises(OSError):
        ban_macos(tmp_path / "khong-co")


def test_doc_that_tu_os_chi_doc():
    assert re.fullmatch(r"[0-9a-f]{16}", ma_may()) and ma_may() == ma_may()
    assert isinstance(phien_do_hoa(), bool) and ban_macos().isalnum()


def test_ngu_canh_hien_hanh_gan_uid_tram_va_tai_khoan_kiem():
    nc = ngu_canh_hien_hanh("root")
    assert isinstance(nc, NguCanh) and nc.uid_tram == os.getuid() and nc.uid_kiem == 0
    assert nc == NguCanh(ban_macos(), ma_may(), 0, os.getuid(), phien_do_hoa())
    with pytest.raises(KeyError):
        ngu_canh_hien_hanh("khong-co-tai-khoan-nay-3c-d7")


class ThuVienGia:
    """Thay `ctypes.CDLL` trong một test: `SessionGetInfo` ghi cờ phiên, `gethostuuid` trả mã."""
    def __init__(self, cot=0, ma=0):
        self.cot, self.ma = cot, ma

    def SessionGetInfo(self, phien, sid, cot):
        cot._obj.value = self.cot
        return self.ma

    def gethostuuid(self, buf, han):
        return self.ma


@pytest.mark.parametrize("cot, mong", [(0x6030, True), (0x0010, True), (0x6020, False), (0, False)])
def test_phien_do_hoa_chi_doc_co_sessionHasGraphicAccess(monkeypatch, cot, mong):
    monkeypatch.setattr(ctypes, "CDLL", lambda ten: ThuVienGia(cot))
    assert phien_do_hoa() is mong


def test_api_os_bao_loi_thi_nem(monkeypatch):
    monkeypatch.setattr(ctypes, "CDLL", lambda ten: ThuVienGia(0x10, ma=-1))
    with pytest.raises(OSError):
        phien_do_hoa()
    with pytest.raises(OSError):
        ma_may()
```

- [ ] **Step 3: Chạy — đỏ**

Run: `tests/chan_host/chay.sh -q tests/test_launchd_kiem.py tests/test_ngu_canh_kiem.py`
Expected (thật):
```
E   ModuleNotFoundError: No module named 'tram.giao_viec.launchd_dinh_dang'
E   ModuleNotFoundError: No module named 'tram.giao_viec.ngu_canh_kiem'
!!!!!!!!!!!!!!!!!!! Interrupted: 2 errors during collection !!!!!!!!!!!!!!!!!!!!
2 errors in 0.10s
=== nhật ký chặn …: 0 dòng mới; …
```

- [ ] **Step 4: Viết mã**

`tram/giao_viec/launchd_dinh_dang.py` (mới):

<!-- ap: tao tram/giao_viec/launchd_dinh_dang.py -->
```python
"""Bố cục `launchctl print` ĐÃ ĐO ở G3 (máy B 18/10, macOS 15.6.1 24G90; `tests/du_lieu/launchd/`) — 3C-D7.
Lược đồ đóng: mỗi khoá cấp một (hợp của `user.txt` và `login.txt`) là KHỐI (`= {` … `\t}`) hoặc VÔ HƯỚNG với mẫu giá
trị đo được; sai loại, sai mẫu, khoá lạ, lặp, khối chưa đóng, dòng trống trong khối → ValueError. `BAT_BUOC_USER`:
khối/khoá có trong `user.txt` mà quan sát cần (thiếu = không quan sát được, KHÔNG coi là rỗng); khoá chỉ đo ở miền
login là tuỳ chọn nhưng có mặt thì vẫn đúng lược đồ."""
import re

KHOI = None
SO = r"\d+"
KHOA = {"type": r"user|login", "handle": SO, "active count": SO, "service count": SO, "active service count": SO,
        "creator": r"[\w.-]+\[\d+\]", "creator euid": SO, "session": r"[A-Za-z]+", "endpoint destination": r"[\w.]+",
        "auxiliary bootstrapper": r"[\w.]+ \(\w+\)", "bringup time": r"\d+ ms", "death port": r"0x[0-9a-f]+",
        "in-progress bootstraps": SO, "external activation count": SO, "properties": r"[a-z |]*",
        "security context": KHOI, "environment": KHOI, "services": KHOI, "unmanaged processes": KHOI,
        "endpoints": KHOI, "externally-hosted endpoints": KHOI, "task-special ports": KHOI, "disabled services": KHOI}
BAT_BUOC_USER = ("type", "handle", "session", "security context", "services", "unmanaged processes", "endpoints",
                 "task-special ports")
DONG_KHOA = re.compile(r"\t([a-z][a-z -]*[a-z]) = (.*)")
DONG_DV = re.compile(r"\t\t +\d+ +(?:-|-?\d+|\(\w+\)) \t([^\t]+)")   # pid, trạng thái thoát (-, số, (jt)), nhãn


def tach(van_ban: str, ten: str) -> dict[str, str | list[str]]:
    """`launchctl print <ten>` → {khoá: giá trị vô hướng | các dòng của khối}. Lệch bố cục đã đo → ValueError."""
    dong = van_ban.split("\n")
    if dong[0] != f"{ten} = {{" or dong[-2:] != ["}", ""]:
        raise ValueError("đầu/cuối")
    kq, khoi = {}, None
    for d in dong[1:-2]:
        if khoi is not None:
            if d == "\t}":
                khoi = None
            elif d.startswith("\t\t"):
                kq[khoi].append(d)
            else:
                raise ValueError("dòng lạ trong khối")
        elif d:
            m = DONG_KHOA.fullmatch(d)
            if not m or m[1] not in KHOA or m[1] in kq:
                raise ValueError("khoá lạ hoặc lặp")
            mau = KHOA[m[1]]
            if (mau is KHOI) != (m[2] == "{") or (mau is not KHOI and not re.fullmatch(mau, m[2])):
                raise ValueError("sai loại hoặc sai mẫu giá trị")
            khoi = m[1] if mau is KHOI else None
            kq[m[1]] = [] if khoi else m[2]
    if khoi is not None:
        raise ValueError("khối chưa đóng")
    return kq
```

`tram/giao_viec/ngu_canh_kiem.py` (mới):

<!-- ap: tao tram/giao_viec/ngu_canh_kiem.py -->
```python
"""Ngữ cảnh vận hành của quan sát launchd (3C-D7, review đợt 9 vòng 1 mục 4): bằng chứng G3.9 ("launchd từ chối
tram-kiem ghi vào miền đăng nhập của người gọi sudo") chỉ có giá trị đúng ngữ cảnh đã đo — bản macOS, máy, UID
`tram-kiem`, UID trạm, và loại phiên của người gọi (tiến trình dưới sudo kế thừa audit session của trạm, G3:
`procinfo` → `audit info → session id`). TRẠM tự đọc từ OS, không qua env hay lời `tram-kiem`: build từ
`SystemVersion.plist` (của root), máy = sha256 của `gethostuuid` (16 ký tự đầu — không ghi UUID thô vào mã), loại
phiên = cờ `sessionHasGraphicAccess` của `SessionGetInfo(callerSecuritySession)` (Security.framework). Đọc lỗi →
`OSError`/`ValueError`; người gọi đóng cổng. Không dùng số asid (đổi mỗi lần đăng nhập)."""
import ctypes
import hashlib
import os
import plistlib
from dataclasses import dataclass
from pathlib import Path

from tram.kiem.danh_tinh import uid_cua

SYS_VER = Path("/System/Library/CoreServices/SystemVersion.plist")
SECURITY = "/System/Library/Frameworks/Security.framework/Security"
CO_DO_HOA = 0x0010                                   # sessionHasGraphicAccess (AuthSession.h)


@dataclass(frozen=True)
class NguCanh:
    ban: str            # ProductBuildVersion
    may: str            # sha256(gethostuuid)[:16]
    uid_kiem: int
    uid_tram: int
    do_hoa: bool        # người gọi sudo ở phiên có đồ hoạ (Aqua) hay phiên nền


def ban_macos(tep: Path = SYS_VER) -> str:
    with open(tep, "rb") as f:
        ban = plistlib.load(f).get("ProductBuildVersion")
    if not isinstance(ban, str) or not ban.isalnum():
        raise ValueError("ProductBuildVersion không hợp lệ")
    return ban


def ma_may() -> str:
    buf, han = (ctypes.c_ubyte * 16)(), (ctypes.c_long * 2)(1, 0)
    if ctypes.CDLL(None).gethostuuid(buf, han) != 0:
        raise OSError("gethostuuid lỗi")
    return hashlib.sha256(bytes(buf)).hexdigest()[:16]


def phien_do_hoa() -> bool:
    sid, cot = ctypes.c_uint32(), ctypes.c_uint32()
    if ctypes.CDLL(SECURITY).SessionGetInfo(ctypes.c_int32(-1), ctypes.byref(sid), ctypes.byref(cot)) != 0:
        raise OSError("SessionGetInfo lỗi")
    return bool(cot.value & CO_DO_HOA)


def ngu_canh_hien_hanh(ten_kiem: str) -> NguCanh:
    """Ngữ cảnh lúc này; `KeyError` khi không có tài khoản `ten_kiem`."""
    return NguCanh(ban_macos(), ma_may(), uid_cua(ten_kiem), os.getuid(), phien_do_hoa())
```

`tram/giao_viec/launchd_kiem.py` (mới):

<!-- ap: tao tram/giao_viec/launchd_kiem.py -->
```python
"""Bộ đọc launchd của `tram-kiem` (3C-D7; C01 hàng 20–22) CHỈ cho bố cục đo ở G3 (`launchd_dinh_dang`); lệch bố cục,
mã lạ, thiếu mốc hay thiếu bằng chứng cho ngữ cảnh hiện hành → ném, cổng đóng. Dây báo, không phải ranh giới
(Seatbelt, G4). `user/<uid>`: miền RIÊNG của tram-kiem — dịch vụ ngoài mốc, khối trạng thái có dòng → ném; thiếu
khối bắt buộc = không quan sát được. `gui/<uid>`: chỉ mã 125 đã đo là sạch. `login/<asid>` là phiên của NGƯỜI GỌI
sudo (G3: phiên Aqua của người vận hành, uid 501), không ghi uid từng mục → không quy được → KHÔNG in; chỉ đi tiếp
khi `BANG_CHUNG_LOGIN` có ĐÚNG ngữ cảnh hiện hành (`ngu_canh_kiem`, G3.9 — launchd từ chối tram-kiem ghi vào đó),
kiểm TRƯỚC mọi lệnh. Mốc (D45: chỉ hỗ trợ, không là bằng chứng) theo build. G3 ghi `2>&1` → đọc gộp stdout+stderr."""
import re
import subprocess
from collections.abc import Callable

from tram.giao_viec.ban_chep import LoiBanChep
from tram.giao_viec.launchd_dinh_dang import BAT_BUOC_USER, DONG_DV, tach
from tram.giao_viec.ngu_canh_kiem import NguCanh, ngu_canh_hien_hanh
from tram.giao_viec.quan_sat_kiem import HAN, mo_cong_kiem
from tram.kiem.danh_tinh import LoiDanhTinh
from tram.kiem.vong_doi import LoiThuHoi

LAUNCHCTL = "/bin/launchctl"
GUI_KHONG = "Could not print domain: 125: Domain does not support specified action"
PHAI_RONG = ("unmanaged processes", "endpoints", "externally-hosted endpoints", "environment", "disabled services")
MOC_USER: dict[str, frozenset[str]] = {"24G90": frozenset()}   # build → nhãn được phép trong user/<uid> (G3.3)
BANG_CHUNG_LOGIN: frozenset[NguCanh] = frozenset()             # ngữ cảnh đã đạt G3.9 — chưa đo


def xet_user(van_ban: str, uid: int, moc: frozenset[str]) -> None:
    ten = f"user/{uid}"
    try:
        k = tach(van_ban, ten)
        if any(x not in k for x in BAT_BUOC_USER):
            raise ValueError("thiếu khối/khoá bắt buộc")
        ports = (rf"\t\t\t +0x[0-9a-f]+ 4 +bootstrap  com\.apple\.xpc\.launchd\.domain\.user\.{uid}\n"
                 r"\t\t\t +0x[0-9a-f]+ 9 +access  \(unknown\)")
        if not re.fullmatch(ports, "\n".join(k["task-special ports"])):
            raise ValueError("task-special ports khác bản đã đo")
        dv = [DONG_DV.fullmatch(d) for d in k["services"]]
        if (k["type"], k["handle"], k["session"]) != ("user", str(uid), "Background") or not all(dv) or \
                not re.fullmatch(rf"\t\tuid = {uid}\n\t\tasid = \d+", "\n".join(k["security context"])):
            raise ValueError("danh tính miền")
    except ValueError:
        raise LoiBanChep(f"{ten}: định dạng launchctl print khác bản đã đo — không quan sát được, cổng đóng") from None
    la = [m[1] for m in dv if m[1] not in moc]
    if la:
        raise LoiBanChep(f"{ten}: {len(la)} dịch vụ launchd ngoài mốc — tram-kiem có job (C01 hàng 20)")
    for x in PHAI_RONG:
        if k.get(x):
            raise LoiBanChep(f"{ten}: khối '{x}' có {len(k[x])} dòng — tram-kiem để lại trạng thái launchd")


def _ra(cong: Callable, argv: list[str]) -> tuple[int, str]:
    try:
        r = cong(argv, capture_output=True, text=True, timeout=HAN)
    except (LoiDanhTinh, LoiThuHoi, subprocess.SubprocessError) as e:          # P1 H4: thông báo cố định
        raise LoiBanChep(f"launchctl print dưới tram-kiem không xác nhận được ({type(e).__name__})") from None
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def _ngu_canh(pk, ngu_canh: Callable[[str], NguCanh]) -> NguCanh:
    try:
        return ngu_canh(pk.ten)
    except (KeyError, OSError, ValueError, AttributeError):
        raise LoiBanChep("không xác định được ngữ cảnh vận hành (bản macOS, máy, UID, phiên) — cổng đóng") from None


def doc_launchd(pk, *, chay: Callable | None = None, ngu_canh: Callable[[str], NguCanh] = ngu_canh_hien_hanh,
                moc: dict | None = None, bang_chung: frozenset | None = None) -> None:
    """Bộ đọc cho `quan_sat_kiem.launchd(pk, doc=…)`: sạch thì trả; thấy, lệch hay không chắc → `LoiBanChep`."""
    if pk.co_che == "sandbox":
        raise LoiBanChep(f"{pk.ten}: cơ chế sandbox cấm exec launchctl (G3.2) — không quan sát được launchd, cổng đóng")
    nc = _ngu_canh(pk, ngu_canh)
    moc_user = (MOC_USER if moc is None else moc).get(nc.ban)
    if moc_user is None:
        raise LoiBanChep(f"chưa có mốc launchd cho macOS {nc.ban} — đo lại (G3.3, G3.8) rồi ghi mốc")
    if nc not in (BANG_CHUNG_LOGIN if bang_chung is None else bang_chung):
        raise LoiBanChep("login/<asid>: chưa có bằng chứng G3.9 cho ngữ cảnh này (bản macOS, máy, UID, phiên) — không "
                         "quy được mục nào về tram-kiem, cổng đóng")
    cong = chay or mo_cong_kiem(pk)
    if cong.uid != nc.uid_kiem:
        raise LoiBanChep(f"{pk.ten}: UID đã chứng minh khác UID của ngữ cảnh — cổng đóng")
    ma, ra = _ra(cong, pk.boc_lenh([LAUNCHCTL, "print", f"user/{cong.uid}"]))
    if ma:
        raise LoiBanChep(f"user/{cong.uid}: launchctl print mã {ma} — không quan sát được")
    xet_user(ra, cong.uid, moc_user)
    ma, ra = _ra(cong, pk.boc_lenh([LAUNCHCTL, "print", f"gui/{cong.uid}"]))
    if ma == 0:
        raise LoiBanChep(f"gui/{cong.uid}: tram-kiem có miền GUI — chưa đo, không được có (cổng đóng)")
    if ma != 125 or ra.strip() != GUI_KHONG:                          # chỉ dạng "không có miền" đã đo là sạch
        raise LoiBanChep(f"gui/{cong.uid}: launchctl print mã {ma} — không quan sát được")
```

- [ ] **Step 5: Chạy — xanh**

Run: `tests/chan_host/chay.sh -q tests/test_launchd_kiem.py tests/test_ngu_canh_kiem.py tests/test_do_dai_ma.py`
Expected (thật): `61 passed in 0.15s`, nhật ký chặn 0 dòng mới.

Đột biến đã thử (mỗi lần một chỗ, rồi hoàn nguyên; số đỏ/tổng của hai file test): bỏ kiểm `BAT_BUOC_USER` → 8 đỏ; bỏ kiểm mẫu giá trị vô hướng → 3; bỏ `m[1] not in KHOA` → 1; bỏ kiểm `BANG_CHUNG_LOGIN` → 4; bỏ so `cong.uid` với ngữ cảnh → 1; chỉ bắt `KeyError` khi đọc ngữ cảnh → 2; bỏ vòng `PHAI_RONG` → 4; bỏ đòi `session = Background` → 1; `gui` mã 125 không so chữ → 1; bỏ `isalnum` của build → 1; `phien_do_hoa` luôn True → 2; bỏ kiểm mã `gethostuuid` → 1. **Đột biến tương đương (không bắt, có ghi):** bỏ riêng điều kiện "đúng loại khối/vô hướng" — mọi ca sai loại vẫn bị mẫu giá trị hoặc kiểm khối đóng bắt (`services = 0` làm các dòng sau thành "dòng lạ trong khối"; `type = {` sai mẫu); giữ điều kiện cho rõ nghĩa.

- [ ] **Step 6: Chạy cả bộ**

Run: `tests/chan_host/chay.sh -q`
Expected (thật): `3294 passed in 330.81s`, nhật ký chặn 0 dòng mới.

- [ ] **Step 7: Commit**

```bash
git add tests/du_lieu/launchd tests/test_launchd_kiem.py tests/test_ngu_canh_kiem.py tram/giao_viec/launchd_dinh_dang.py tram/giao_viec/ngu_canh_kiem.py tram/giao_viec/launchd_kiem.py
git commit -m "feat(giao-viec): bộ đọc launchd của tram-kiem chỉ cho bố cục đo ở G3; thiếu khối = đóng; login/<asid> không in, bằng chứng G3.9 gắn ngữ cảnh (lát 3c 3C-D7, C01)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

## Task 2 — Nối bộ đọc vào cổng thật + cập nhật bảng threat (RED→GREEN thật)

**Files:**
- Modify: `tests/test_cong_that.py` (khẳng định `dung_cong` cắm `doc_launchd`)
- Modify: `tram/giao_viec/cong_that.py` (import + `partial(launchd, pk, doc=doc_launchd)` + docstring), `tram/giao_viec/quan_sat_kiem.py` (docstring `launchd`), `tram/giao_viec/lenh_nghiem_thu.py` (docstring)
- Modify: `docs/handovers/2026-10-16-thiet-ke-3c-boundary.md` (§2 mục 4, bảng threat hàng 20–22)

**Interfaces:** Consumes `launchd_kiem.doc_launchd` (Task 1). `quan_sat_kiem.launchd(pk, *, doc=None)` giữ nguyên chữ ký và hành vi (`test_quan_sat_launchd.py` không đổi).

- [ ] **Step 1: Sửa test**

<!-- ap: va t2a -->
```diff
diff --git a/tests/test_cong_that.py b/tests/test_cong_that.py
index 8333200..3aba18a 100644
--- a/tests/test_cong_that.py
+++ b/tests/test_cong_that.py
@@ -8,6 +8,7 @@ import pytest
 
 from tram.giao_viec.ban_chep import LoiBanChep
 from tram.giao_viec.cong_that import dung_cong, env_kin, ho_so_cai, thu_hoi_theo_uid
+from tram.giao_viec.launchd_kiem import doc_launchd
 from tram.giao_viec.principal_kiem import tu_cach_ly
 from tram.giao_viec.quan_sat_kiem import cron_at, goc_rong, launchd, tep_ngoai, tien_trinh
 
@@ -32,4 +33,5 @@ def test_dung_cong_du_quan_sat_va_thu_hoi_mac_dinh_khong_go_lich(tram_home_tam,
     ham = [q.func if isinstance(q, partial) else q for q in c.quan_sat]
     assert ham == [tien_trinh, tep_ngoai, goc_rong, cron_at, ho_so_cai, env_kin, launchd]
     assert c.quan_sat[4].args == (tmp_path,)                       # V2-5: hồ sơ so với gốc bản chép HIỆN HÀNH
+    assert c.quan_sat[6].args == (pk,) and c.quan_sat[6].keywords == {"doc": doc_launchd}     # 3C-D7: bộ đọc đã đo
     assert dung_cong(pk, tmp_path, cac_du_an=list, thu_hoi=print).thu_hoi is print
```

- [ ] **Step 2: Chạy — đỏ**

Run: `tests/chan_host/chay.sh -q tests/test_cong_that.py`
Expected (thật):
```
E       AssertionError: assert ((PrincipalKie..._che='user'),) == (PrincipalKie..._che='user'),)
E         Use -v to get more diff and {} == {'doc': <func... 0x10657f4c0>}
E         Right contains 1 more item:
E         {'doc': <function doc_launchd at 0x10657f4c0>}
1 failed, 1 passed in 0.06s
```

- [ ] **Step 3: Sửa mã**

<!-- ap: va t2b -->
```diff
diff --git a/tram/giao_viec/cong_that.py b/tram/giao_viec/cong_that.py
index 4ccf96d..1b50cf7 100644
--- a/tram/giao_viec/cong_that.py
+++ b/tram/giao_viec/cong_that.py
@@ -6,8 +6,8 @@ Thu hồi (3C-D5, hợp đồng P1/3C-B): mở `CongLich` (UID THỰC của `tra
 rồi dọn + xác nhận rỗng `DARWIN_USER_*` của `tram-kiem` (`thu_muc_he`, phần còn giữ của r47 T11).
 KHÔNG gỡ lịch — lịch để `cron_at` thấy và đóng cổng. Quan sát: tiến trình, tệp ngoài, gốc rỗng, cron/at, hồ sơ
 Seatbelt đúng TỪNG BYTE bản sinh từ manifest root (V2-5), tệp môi trường kiểm của mọi dự án kín (0600, của trạm),
-launchd (`user/<uid>`, `gui/<uid>`, `login/<asid>` — 3C-D6: khung, chưa có bộ đọc đã đo ở G3 thì ném, cổng giữ đóng;
-I1 KHÔNG bật `giao_viec.bat`)."""
+launchd (`user/<uid>`, `gui/<uid>`, `login/<asid>` — 3C-D7: bộ đọc CHỈ cho định dạng đo ở G3, `launchd_kiem`; lệch
+hay thiếu bằng chứng G3.9 đúng ngữ cảnh thì ném, cổng giữ đóng; I1 KHÔNG bật `giao_viec.bat`)."""
 import os
 import stat
 import subprocess
@@ -19,6 +19,7 @@ from pathlib import Path
 from tram.duong_dan import tram_home
 from tram.giao_viec.ban_chep import LoiBanChep
 from tram.giao_viec.cong_luot import CongLuot
+from tram.giao_viec.launchd_kiem import doc_launchd
 from tram.giao_viec.quan_sat_kiem import (HAN, cron_at, env_kin, goc_rong, launchd, mo_cong_kiem, tep_ngoai,
                                          tien_trinh)
 from tram.giao_viec.thu_muc_he import don_thu_muc_he
@@ -107,4 +108,4 @@ def dung_cong(pk, goc: Path | None, *, cac_du_an: Callable[[], list],
     return CongLuot(tram_home() / "kiem-lai" / "cong.json", thu_hoi=thu_hoi or partial(thu_hoi_theo_uid, pk),
                     quan_sat=[partial(tien_trinh, pk.ten), partial(tep_ngoai, pk.ten, goc), partial(goc_rong, goc),
                               partial(cron_at, pk), partial(ho_so_cai, goc), partial(env_kin, cac_du_an),
-                              partial(launchd, pk)])
+                              partial(launchd, pk, doc=doc_launchd)])
diff --git a/tram/giao_viec/lenh_nghiem_thu.py b/tram/giao_viec/lenh_nghiem_thu.py
index a28f113..c7b094e 100644
--- a/tram/giao_viec/lenh_nghiem_thu.py
+++ b/tram/giao_viec/lenh_nghiem_thu.py
@@ -5,7 +5,7 @@ tại) với `--trong --dau-ino <inode dấu> --cha <pid cha>` làm TIẾN TRÌN
 900`, quá hạn thu hồi cả cây (kill gộp principal + cục bộ). Con chỉ chạy khi cha của nó đúng là pid đó VÀ dấu
 `~/.tram/kiem-lai.dong` còn, đúng inode cha vừa tạo (gọi `--trong` tay, dấu cũ → mã 2). Cổng và quan sát của harness
 là cổng THẬT với mọi dự án thật (`env_kin` đủ). Sau đó `_don` dưới khoá kiểm lại: thu hồi theo UID + HAI lượt mọi quan
-sát cách `cho` của cổng (kể cả launchd — chưa đo ở G3 thì ném); lỗi hay ngắt → `cong.dong` rồi ném. Chỉ khi xác nhận
+sát cách `cho` của cổng (kể cả launchd — thiếu G3.9 thì ném); lỗi hay ngắt → `cong.dong` rồi ném. Chỉ khi xác nhận
 mới xoá dấu; còn dấu thì kiểm lại, `tram giao kiem`, `mo-cong-kiem` từ chối. Ctrl-C/SIGTERM ở cha (bs-863.19, B03):
 `term_thanh_ngat` cài TỪ ĐẦU lệnh cha — phủ preflight (tiến trình dò UID, bọc `hoan()`: ngắt chờ nó thu hồi xong) lẫn
 tạo dấu + spawn harness (`chay_han_tong` tự hoãn tới khi con có chủ) — rồi thu hồi + dọn trong `finally` mới trả. Con
diff --git a/tram/giao_viec/quan_sat_kiem.py b/tram/giao_viec/quan_sat_kiem.py
index e6c790c..5d1acb8 100644
--- a/tram/giao_viec/quan_sat_kiem.py
+++ b/tram/giao_viec/quan_sat_kiem.py
@@ -95,8 +95,8 @@ def cron_at(pk, *, chay: Callable | None = None) -> None:
 
 def launchd(pk, *, doc: Callable | None = None) -> None:
     """Khung quan sát launchd của `tram-kiem` (3C-D6; C01 hàng 20–22: `user/<uid>`, `gui/<uid>`, `login/<asid>`).
-    Định dạng `launchctl print` CHƯA đo (G3): không có bộ đọc `doc(pk)` đã đo thì ném — cổng giữ đóng, I1 không bật
-    `giao_viec.bat`. Bộ đọc là task sau G3, kèm đầu ra thật làm fixture; không viết parser đoán."""
+    Không có bộ đọc `doc(pk)` thì ném — cổng giữ đóng. Bộ đọc đã đo: `launchd_kiem.doc_launchd` (3C-D7, fixture là đầu
+    ra thật G3.3), `cong_that.dung_cong` truyền vào; không viết parser đoán."""
     if doc is None:
         raise LoiBanChep("quan sát launchd user/gui/login của tram-kiem chưa có — G3 chưa đo định dạng launchctl print")
     doc(pk)
```

- [ ] **Step 4: Chạy — xanh**

Run: `tests/chan_host/chay.sh -q tests/test_cong_that.py tests/test_launchd_kiem.py tests/test_ngu_canh_kiem.py tests/test_quan_sat_launchd.py tests/test_do_dai_ma.py`
Expected (thật): `65 passed in 0.20s`, nhật ký chặn 0 dòng mới.

- [ ] **Step 5: Cập nhật bảng threat (docs)**

<!-- ap: va t2c -->
```diff
diff --git a/docs/handovers/2026-10-16-thiet-ke-3c-boundary.md b/docs/handovers/2026-10-16-thiet-ke-3c-boundary.md
index 719f1b4..481164b 100644
--- a/docs/handovers/2026-10-16-thiet-ke-3c-boundary.md
+++ b/docs/handovers/2026-10-16-thiet-ke-3c-boundary.md
@@ -51,7 +51,7 @@ Hai đường làm hỏng lượt N+1 mà C01 phải chặn:
    - `crontab -l` phải báo "no crontab for", `atq` rỗng, không còn tệp của `tram-kiem` trong `/usr/lib/cron/jobs`;
    - hồ sơ đã cài: chủ root, không ai khác ghi được, có `(deny default)` và có dòng cấm đọc kho trạm hiện tại;
    - tệp môi trường kiểm của mọi dự án: 0600 và thuộc trạm;
-   - launchd `user/<uid>`, `gui/<uid>`, `login/<asid>`: dùng T11 khi ghép, sau khi G3 đo định dạng. Chưa có thì I1 **không** bật `giao_viec.bat`.
+   - launchd `user/<uid>`, `gui/<uid>`, `login/<asid>`: bộ đọc 3C-D7 (`tram/giao_viec/launchd_kiem.py`) chỉ cho định dạng đo ở G3; `login/<asid>` không in (là miền của người gọi sudo, không quy được), chỉ đi tiếp khi có bằng chứng G3.9 cho đúng ngữ cảnh vận hành (`ngu_canh_kiem.py`). Chưa có thì I1 **không** bật `giao_viec.bat`.
 
 Đã chạy thử, không phải bằng chứng G4. Chạy dưới user hiện tại trên macOS 15.6.1 (24G90), với hồ sơ sinh ra từ mã 3C-D1, trong thư mục tạm:
 
@@ -110,9 +110,9 @@ Viết tắt:
 | 17 | Dịch vụ dùng chung qua mạng: MySQL/Redis/tram-api trên loopback, IP LAN, VM (Docker/OrbStack) hay máy xa; MySQL EVENT/trigger là nguồn thực thi | **Không mạng** (chỉ unix socket trong `LUOT`) | `test_khong_mang_chi_unix_socket_trong_luot`; chạy thử `bind`/`connect` EPERM | — | SB. **Hệ quả:** test cần DB/mạng không chạy được, xem Q-A |
 | 18 | cron (`crontab` setuid → `/usr/lib/cron/tabs`) | Cấm exec + cấm ghi; SB kế thừa qua setuid | Test D1; chạy thử exec bị chặn | T11 `crontab -l`; lỗi thì cổng đóng | Kế thừa SB qua setuid |
 | 19 | at/batch (`/usr/lib/cron/jobs`) | Như hàng 18 | Như hàng 18 | T11 `find` + `atq` | Như hàng 18 |
-| 20 | launchd `user/<uid>` (bootstrap, submit, XPC trực tiếp) | `(deny job-creation)` + cấm exec `launchctl` | Test D1; chạy thử exec bị chặn | T11 mốc nền + vân tay | **`job-creation` với XPC trực tiếp. Điều kiện chính** |
-| 21 | launchd `gui/<uid>` | Như hàng 20 | Như hàng 20 | T11 "Could not find domain" | Như hàng 20 |
-| 22 | launchd `login/<asid>` (sudo giữ asid của trạm) | Như hàng 20 | Như hàng 20 | **Chưa có Q:** chờ G3 đo định dạng, không viết parser đoán | Như hàng 20. Điều kiện chính |
+| 20 | launchd `user/<uid>` (bootstrap, submit, XPC trực tiếp) | `(deny job-creation)` + cấm exec `launchctl` | Test D1; chạy thử exec bị chặn; `test_launchd_kiem.py` | 3C-D7: miền riêng của tram-kiem — dịch vụ ngoài mốc (theo bản macOS), khối trạng thái có dòng, thiếu khối bắt buộc → cổng đóng | **`job-creation` với XPC trực tiếp. Điều kiện chính** |
+| 21 | launchd `gui/<uid>` | Như hàng 20 | Như hàng 20 | 3C-D7: chỉ mã 125 "Domain does not support specified action" (đo G3) là sạch; miền tồn tại → cổng đóng | Như hàng 20 |
+| 22 | launchd `login/<asid>` (sudo giữ asid của trạm) | Như hàng 20 | Như hàng 20 | **Không có Q (không quy được):** G3 đo asid là phiên Aqua của người vận hành (uid 501), miền không ghi uid từng mục; 3C-D7 không in, chỉ đi tiếp khi `BANG_CHUNG_LOGIN` có đúng ngữ cảnh hiện hành (bản macOS, máy, UID kiểm, UID trạm, loại phiên) | Như hàng 20 + G3.9 (đối chứng dương ngoài hồ sơ, `docs/handovers/g3-bo-sung.sh`). Điều kiện chính |
 | 23 | Tiến trình nền (nohup, double-fork, setsid, daemon) | Thu hồi `kill -1` theo UID (D5) | `test_thu_hoi_theo_uid_*` | Q `tien_trinh` (UID thực và hiệu lực) ở `ra` hai lần và ở `vao` lượt sau | `kill -1` đủ |
 | 24 | Tiến trình setuid (ruid `tram-kiem`, euid khác) không giết được | Cấm exec `sudo`, `su`, `login`; setuid khác (vd `traceroute`) chưa cấm | — | `pgrep -U` thấy, cổng đóng (fail-closed, mất khả năng chạy tiếp) | G4: danh sách setuid trên máy B |
 | 25 | Tái sinh trễ | Như hàng 20 và 23 | `test_tai_sinh_tre_giua_hai_lan_quan_sat`, `test_tai_sinh_sau_khi_mo_bi_bat_luc_vao_luot_sau` | Quan sát hai lần + quan sát ở `vao` | Thời gian `cho` thật |
```

Run: `ls tram/giao_viec/launchd_kiem.py tram/giao_viec/ngu_canh_kiem.py tests/test_launchd_kiem.py`
Expected: cả ba tồn tại. (Hàng 22 nhắc `docs/handovers/g3-bo-sung.sh` — có sau Task 3.)

- [ ] **Step 6: Chạy cả bộ**

Run: `tests/chan_host/chay.sh -q`
Expected (thật): `3294 passed in 330.55s`, nhật ký chặn 0 dòng mới.

- [ ] **Step 7: Commit**

```bash
git add tests/test_cong_that.py tram/giao_viec/cong_that.py tram/giao_viec/quan_sat_kiem.py tram/giao_viec/lenh_nghiem_thu.py docs/handovers/2026-10-16-thiet-ke-3c-boundary.md
git commit -m "feat(giao-viec): cổng kiểm lại thật dùng bộ đọc launchd đã đo; bảng threat hàng 20–22 theo G3 (lát 3c 3C-D7, C01)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

Sau Task 2: `tram giao mo-cong-kiem`/`kiem`/`nghiem-thu-kiem` vẫn báo cổng đóng với lý do "login/<asid>: chưa có bằng chứng G3.9 cho ngữ cảnh này …" — đúng thiết kế.

## Task 3 — Kịch bản G3 bổ sung (G3.8–G3.10), bản rút gọn D117 (RED→GREEN thật)

Thay Task 3 vòng 3 (lớp ngoài bash + thân Python ~600 dòng — Codex vòng 3 CHƯA ĐẠT R3-01…R3-04). Đại ca chốt **D117**:
một kịch bản bash ngắn kiểu `.handover/g3/g3-do.sh` (Đại ca đã chạy đạt sáng 18/10), đọc được bằng mắt. Cần Task 1 đã
ghép (kịch bản gọi `xet_user`, `MOC_USER`, `ngu_canh_hien_hanh`). Task 3 không sửa `tram/`, không đụng Task 1–2.

**Lập luận an toàn (đóng R3-01…R3-04 theo D117):**

| Review vòng 3 | Cách bản rút gọn xử lý |
|---|---|
| R3-01 — `kill -1` dưới tram-kiem rộng hơn "tiến trình kịch bản tạo" | **Tài khoản dành riêng cho lần đo.** Tiền điều kiện: bảng tiến trình đọc được (ps mã 0, stderr rỗng, mọi dòng đúng dạng số, có dòng của chính kịch bản) và KHÔNG có tiến trình nào uid hoặc ruid = tram-kiem → có thì in danh sách, DỪNG, không giết, không chạy lệnh nào dưới tram-kiem. Từ lúc đó tiến trình tram-kiem chỉ có thể do lần đo tạo — ngoại lệ đã biết: dịch vụ macOS tự bật dưới UID đó khi tài khoản có hoạt động (`distnoted`, ghi nhận G3.6), cũng là hệ quả của lần đo. `kill -KILL -1` chạy DƯỚI tram-kiem (nhân chỉ cho trúng tiến trình cùng UID — đo V0.5, G3.5) nên không thể trúng tiến trình của Đại ca hay của ai khác; dọn chỉ chạy `kill -1` khi tiền điều kiện đã đạt (`DA_TK=1`). Không còn bảng sở hữu/kênh nhóm nào cần chứng minh. |
| R3-02 — nhánh `procinfo` mất dấu hậu duệ rồi báo sạch | Giữ như g3-do.sh: MỘT lệnh tiền cảnh có hạn `han 60 sudo launchctl procinfo`. Mã ≠ 0 (lỗi, quá hạn, Ctrl-C lúc hỏi mật khẩu) → không dùng ASID, DỪNG, và dọn LUÔN in "CHƯA XÁC NHẬN: procinfo lỗi/quá hạn" + mã 3 (không biết hậu duệ root của sudo đã hết). Giới hạn ghi rõ: kịch bản không gửi tín hiệu tới tiến trình root; procinfo mã 0 là lệnh đọc đã xong. |
| R3-03 — quan sát hỏng vẫn đi tới phép ghi | Mỗi bước G3.8 là cổng `|| dung`: bảng trước đọc được; `print user` hai lần mã 0; `print gui/<uid>` mã 125 VÀ đúng chữ đã đo; 10 lượt bảng đều đọc được và tổng 0 dòng; bộ đọc thật xác nhận sạch cả hai ảnh. ASID: procinfo mã 0, sleep đã dừng và bảng xác nhận không còn tiến trình tram-kiem, ASID = `handle`. Không đạt → DỪNG TRƯỚC mọi lệnh ghi launchd (test: không có `bootstrap`/`submit` nào trong nhật ký). |
| R3-04 — tìm Python ngoài hạn tổng | Không `uv run`: đường cố định `"$REPO/.venv/bin/python" -I` (không có → DỪNG trước mọi thao tác). Hạn tổng: kịch bản tự chạy lại dưới `perl alarm` (alarm còn hiệu lực qua `exec`), SIGALRM → trap → dọn (mỗi lệnh dọn có hạn riêng). Bỏ ông canh riêng. |
| Ghi được vào miền Đại ca (D66) | Sau mỗi phép ghi: mã 0 → DỪNG ngay mã 4; không thì `print gui/<uid vận hành>` ngay — thấy nhãn → mã 4, print lỗi → không kết luận; chỉ khi sạch mới sang phép kế (login → gui → submit). |

**Bổ sung sau review vòng bổ sung R4 (điều phối chốt, không thêm vòng Codex):** (R4-01) `PROC_LOI=1` đặt TRƯỚC `procinfo`, chỉ về 0 sau khi xét mã 0 — ngắt TERM/HUP/ALRM lúc procinfo đang chạy vẫn để dọn báo chưa xác nhận (sửa của Codex, đã chạy thật). (R4-03) Khoá độc quyền `$OUT/g3b.khoa` bằng `mkdir` nguyên tử, lấy TRƯỚC ảnh tram-kiem ban đầu, giữ tới hết dọn; đã có → mã 2, không sudo/kill gì; gỡ khi `DỌN: XONG`, GIỮ khi chưa xác nhận (lần sau tự dừng tới khi Em kiểm). Phạm vi: trạm thật cũng dùng tram-kiem để kiểm lại → điều kiện chạy là `giao_viec.bat: false`; tiền điều kiện "tram-kiem trống" chặn thêm trường hợp trạm đang kiểm lại. (R4-04) Biên nhận đọc MỘT lần vào bộ nhớ, đọc lỗi → dọn chưa xác nhận, xét dòng bằng so chuỗi (không `grep`); `ps-sau` đếm từ từng lượt đã đọc được, ghi bảng tổng lỗi → DỪNG trước mọi lệnh ghi launchd. (R4-02) **Giới hạn đã biết**, ghi ở đầu kịch bản và sổ tay: bash chỉ chạy trap ALRM/INT/TERM khi lệnh đang chờ kết thúc, lệnh bỏ qua SIGALRM không bị cắt, dọn không có trần riêng — Đại ca ngồi trước Terminal, quá ~20 phút thì đóng cửa sổ Terminal và báo Em; test hạn tổng đo thời gian thật và ghi đúng hành vi đó.

Biên nhận giữ từ vòng 3 (đã ĐẠT R2-03): `y-dinh thumuc` trước `mkdir`, `co thumuc` sau khi `mkdir` thành công (ngắt INT/TERM giữa hai bước chỉ được ghi lại rồi phát lại sau); dọn chỉ xoá thư mục có `co`, luôn kiểm lại bằng `/bin/test -e … -o -L …` dưới tram-kiem. Dòng `nap <nhãn> <miền> <tk|toi>` ghi trước mỗi `bootstrap`/`submit` (nhãn duy nhất của lần chạy, đã chứng minh chưa có ở cả hai miền).

**Files:**
- Create: `tests/test_g3_bo_sung.py`
- Create: `docs/handovers/g3-bo-sung.sh`
- Modify: `docs/handovers/2026-10-15-so-tay-chay-that.md` (dòng trạng thái G3; hàng G3.3; mục mới "G3 bổ sung cho 3C-D7 — bản rút gọn (D117)" sau "Ra khỏi G3"; đoạn "Bổ sung G3.3")

**Interfaces:** Đại ca chạy `bash "/Users/dai-ca/Developer/Ben Station/docs/handovers/g3-bo-sung.sh"` trong Terminal.app, gõ `dong-y`. Mã thoát: 0 ứng viên đạt; 1 dừng/không kết luận; 2 không chạy (kể cả khoá `g3b.khoa` có sẵn); 3 dọn chưa xác nhận; 4 ghi được vào miền Đại ca; 129/130/142/143 mất Terminal/bị ngắt/hết hạn tổng (đã dọn). Bằng chứng `~/.tram/g3/g3b-<lần>.{log,receipt}` và đầu ra từng bước (`-tk-dau`, `-ngu-canh`, `-truoc-{user,gui}`, `-ps-truoc`, `-user-{2,3}.{out,err}`, `-gui.{out,err}`, `-ps-sau`, `-procinfo`, `-user-co-viec`, `-user-sau-don`, `-g39-*`, `-don*`). CHỈ test: `G3_GIA=<thư mục>` (lệnh giả `sudo`, `launchctl`, `ps`, `id` trong thư mục đó; `CHO=DEM=0`), `G3_PY`, `G3_BAN`, `G3_HAN_TONG`.

- [ ] **Step 1: Viết test**

`tests/test_g3_bo_sung.py` (mới):

<!-- ap: tao tests/test_g3_bo_sung.py -->
```python
"""3C-D7 Task 3 bản rút gọn (D117): kịch bản `docs/handovers/g3-bo-sung.sh` chạy với LỆNH GIẢ trong `tmp_path`
(`G3_GIA`): `sudo` giả chỉ cho chạy lệnh trong thư mục giả; `kill` giả chỉ tới `sleep` giả mà chính nó đã chạy "dưới
tram-kiem" (mô phỏng kill theo UID, không bao giờ tới tiến trình khác); `launchctl` giả giữ trạng thái miền trong tệp;
`ps` giả = bảng THẬT bỏ UID 503 + dòng giả của tram-kiem. Chỉ kiểm cái đáng kiểm: tiền điều kiện, cổng dừng trước mọi
lệnh ghi, ghi lọt miền Đại ca → mã 4, dọn còn sót → không báo sạch, bị ngắt vẫn dọn."""
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest

GOC = Path(__file__).resolve().parents[1]
KB = GOC / "docs" / "handovers" / "g3-bo-sung.sh"
USER = (GOC / "tests" / "du_lieu" / "launchd" / "user-503.txt").read_text(encoding="utf-8")
TOI = str(os.getuid())
GIA = {
    "id": '[ "$1 $2" = "-u tram-kiem" ] && echo "${G3_UID_KIEM:-503}"\n',
    "sudo": r'''D=$(dirname "$0"); echo "sudo $*" >> "$D/nhat-ky"
if [ "$1" = -n ]; then shift 4
  case "$1" in
    "$D/launchctl") exec "$@";;
    /usr/bin/true) exit 0;;
    /bin/sleep) echo "$$ $PPID" > "$D/tk-sleep"; exec "$@";;
    /bin/kill) [ -f "$D/tk-sleep" ] && read p pp < "$D/tk-sleep" && { [ "$3" = -1 ] || [ "$3" = "$p" ]; } \
      && /bin/kill -KILL "$p" 2>/dev/null; exit 0;;
    /bin/mkdir|/usr/bin/tee|/bin/rm|/bin/test) case "$*" in *"$D"/goc/*) exec "$@";; esac;;
  esac; echo "TU-CHOI $*" >> "$D/nhat-ky"; exit 98
fi
if [ "$1 $2" = "$D/launchctl procinfo" ]; then
  /bin/sleep "${G3_TRE_PROCINFO:-0}"
  printf 'audit info\n\tsession id = %s\n' "${G3_ASID:-100003}"; exit "${G3_RC_PROCINFO:-0}"; fi
echo "TU-CHOI $*" >> "$D/nhat-ky"; exit 99
''',
    "ps": r'''D=$(dirname "$0"); che=$(cat "$D/ps-che-do" 2>/dev/null)
case "$che" in *1) rm -f "$D/ps-che-do";; esac
case "$che" in loi*) exit 1;; rac*) echo "khong phai bang"; exit 0;; rong*) exit 0;; esac
/bin/ps -A -o pid=,ppid=,uid=,ruid=,comm= | awk '$3 != 503 && $4 != 503'
[ -f "$D/tk-them" ] && { cat "$D/tk-them"; case "$(cat "$D/tk-them-mot" 2>/dev/null)" in 1) rm -f "$D/tk-them";; esac; }
[ -f "$D/tk-sleep" ] && read p pp < "$D/tk-sleep" && /bin/kill -0 "$p" 2>/dev/null && echo "$p $pp 503 503 /bin/sleep"
exit 0
''',
    "launchctl": r'''D=$(dirname "$0"); S="$D/lc"; mkdir -p "$S"; echo "launchctl $*" >> "$D/nhat-ky"
f() { echo "$S/$(echo "$1" | tr / _)"; }
su_kien() { [ "${G3_PS#*@}" = "$1" ] && echo "${G3_PS%@*}" > "$D/ps-che-do"
  [ "${G3_TK_THEM#*@}" = "$1" ] && { echo "${G3_TK_DONG:-999999 1 503 503 /usr/libexec/la}" > "$D/tk-them"
    echo "${G3_TK_THEM%@*}" > "$D/tk-them-mot"; }; :; }
case "$1" in
print) case "$2" in
  user/503) n=$(($(cat "$D/dem-user" 2>/dev/null || echo 0) + 1)); echo "$n" > "$D/dem-user"
    [ "$n" = "${G3_PRINT_LOI_LAN:-}" ] && exit 5
    awk -v t="$(f user/503)" -v lech="${G3_CO_VIEC_LECH:-}" '{print}
      /^\tservices = \{$/ {while ((getline l < t) > 0) {printf "\t\t       0      - \t%s\n", l; co = 1}}
      END {if (co && lech) print "\tthu lech = 1"}' "$D/user-503.txt"; exit 0;;
  gui/503) su_kien print-gui-tk
    [ -n "${G3_HONG_PS_SAU:-}" ] && for l in "$D"/out/g3b-*.log; do mkdir "${l%.log}-ps-sau.txt"; done
    echo "Could not print domain: 125: Domain does not support ${G3_GUI_LECH:+other }specified action" >&2; exit 125;;
  gui/"$G3_TOI") printf 'gui/%s = {\n\ttype = login\n\thandle = 100003\n\tservices = {\n' "$G3_TOI"
    [ -f "$(f "$2")" ] && sed 's/^/\t\t       0      - \t/' "$(f "$2")"; printf '\t}\n}\n'; exit 0;;
  esac; exit 113;;
bootstrap) n=$(sed -n 's/.*<string>\(vn[^<]*\)<\/string>.*/\1/p' "$3"); m=$2
  case "$m" in user/503) rc=${G3_RC_USER:-0};;
    login/*) /bin/sleep "${G3_TRE_LOGIN:-0}"; rc=${G3_RC_LOGIN:-5}; m=gui/$G3_TOI; an=${G3_AN:-}
      [ -n "${G3_LOGIN_LOT:-}" ] && echo "$n" >> "$(f "$m")";;
    gui/"$G3_TOI") rc=${G3_RC_GUI:-5};; *) rc=113;; esac
  if [ "$rc" = 0 ]; then [ -n "${an:-}" ] || echo "$n" >> "$(f "$m")"
  else echo "Bootstrap failed: $rc: lỗi giả" >&2; fi; exit "$rc";;
bootout) su_kien bootout; [ -n "${G3_BOOTOUT_HONG:-}" ] && exit 0
  t=$(f "${2%/*}"); [ -f "$t" ] && { grep -vxF "${2##*/}" "$t" > "$t.x"; mv "$t.x" "$t"; }; exit 0;;
submit) echo "$3" >> "$(f "${G3_SUBMIT:-user/503}")"; [ -n "${G3_KHOA_BN:-}" ] && chmod 000 "$D"/out/*.receipt
  exit 0;;
remove) for t in "$S"/*; do [ -f "$t" ] && { grep -vxF "$2" "$t" > "$t.x"; mv "$t.x" "$t"; }; done; exit 0;;
esac; exit 64
''',
}


def dung(tmp_path: Path) -> Path:
    for ten, than in GIA.items():
        p = tmp_path / ten
        p.write_text("#!/bin/sh\n" + than, encoding="utf-8")
        p.chmod(0o755)
    (tmp_path / "user-503.txt").write_text(USER, encoding="utf-8")
    (tmp_path / "goc").mkdir()
    return tmp_path


def moi_truong(d: Path, **env) -> dict:
    return {**os.environ, "G3_GIA": str(d), "G3_PY": sys.executable, "G3_TOI": TOI, "G3_BAN": "24G90", "G3_PS": "",
            "G3_TK_THEM": "", **env}


def nhat_ky(d: Path) -> str:
    return (d / "nhat-ky").read_text(encoding="utf-8") if (d / "nhat-ky").exists() else ""


def chay(tmp_path, **env):
    d = dung(tmp_path)
    r = subprocess.run(["/bin/bash", str(KB)], env=moi_truong(d, **env), stdin=subprocess.DEVNULL,
                       capture_output=True, text=True, timeout=120)
    return r, nhat_ky(d)


def sach(d: Path) -> bool:
    lc = d / "lc"
    return all(not f.read_text().strip() for f in (lc.iterdir() if lc.exists() else ())) and \
        not any((d / "goc").iterdir())


def test_khong_gia_va_khong_terminal_thi_khong_chay_gi():
    e = {k: v for k, v in os.environ.items() if not k.startswith("G3_")}
    r = subprocess.run(["/bin/bash", str(KB)], env=e, stdin=subprocess.DEVNULL, capture_output=True, text=True,
                       timeout=30)
    assert r.returncode == 2 and "Không chạy" in r.stdout


def test_moi_dieu_kien_dat_chi_la_ung_vien_va_don_co_xac_nhan(tmp_path):
    r, nk = chay(tmp_path)
    assert r.returncode == 0, r.stdout
    for chu in ("ps-sau: 0 dòng", "xet_user user-3: sạch", "asid(procinfo)=100003 handle(gui/",
                "bộ đọc ảnh có job: user/503: 1 dịch vụ launchd ngoài mốc", "bộ đọc sau gỡ: sạch",
                "đối chứng dương: ĐẠT", "G3.9: ỨNG VIÊN ĐẠT", "lần 5: 0 tiến trình", "DỌN: XONG"):
        assert chu in r.stdout, chu
    assert sach(tmp_path) and "TU-CHOI" not in nk and "sudo -n -H -u tram-kiem /bin/kill -KILL -1" in nk
    assert nk.index("bootstrap user/503") < nk.index("bootstrap login/100003") < nk.index("bootstrap gui/")


def test_tram_kiem_dang_co_tien_trinh_thi_dung_khong_giet_khong_lam_gi(tmp_path):
    d = dung(tmp_path)
    (d / "tk-them").write_text("999999 1 503 503 /usr/libexec/la\n")
    r = subprocess.run(["/bin/bash", str(KB)], env=moi_truong(d), stdin=subprocess.DEVNULL, capture_output=True,
                       text=True, timeout=120)
    assert r.returncode == 1 and "999999 1 503 503 /usr/libexec/la" in r.stdout and "không giết" in r.stdout
    assert nhat_ky(d) == "" and "DỌN: XONG" in r.stdout        # không một lệnh sudo/launchctl nào


@pytest.mark.parametrize("env, chu", [
    ({"G3_UID_KIEM": TOI}, "UID tram-kiem = 0 hoặc = UID vận hành"),
    ({"G3_PS": "rac1@print-gui-tk"}, "G3.8: không đọc được bảng tiến trình (lượt 1)"),
    ({"G3_PS": "loi1@print-gui-tk"}, "G3.8: không đọc được bảng tiến trình (lượt 1)"),
    ({"G3_PRINT_LOI_LAN": "3"}, "G3.8: print user-3 lỗi"),
    ({"G3_GUI_LECH": "1"}, "G3.8: print gui/503 khác dạng đã đo"),
    ({"G3_TK_THEM": "1@print-gui-tk"}, "G3.8: print sinh tiến trình dưới tram-kiem"),
    ({"G3_ASID": "1"}, "ASID không xác minh được"),
    ({"G3_CO_VIEC_LECH": "1"}, "đối chứng dương không đạt")])
def test_buoc_do_khong_dat_thi_dung_truoc_moi_lenh_ghi_vao_mien_dai_ca(tmp_path, env, chu):
    r, nk = chay(tmp_path, **env)               # lỗi thoáng qua (…1): dọn sau đó sạch, không che lỗi đo
    assert r.returncode == 1 and "DỪNG: " + chu in r.stdout and "DỌN: XONG" in r.stdout, r.stdout
    assert "bootstrap login/" not in nk and "bootstrap gui/" not in nk and "submit" not in nk
    assert "ỨNG VIÊN" not in r.stdout and sach(tmp_path)
    if "CO_VIEC" not in str(env):
        assert "bootstrap" not in nk


def test_procinfo_loi_thi_khong_dung_asid_va_khong_bao_xong(tmp_path):
    r, nk = chay(tmp_path, G3_RC_PROCINFO="1")
    assert r.returncode == 3 and "procinfo mã 1 — không dùng ASID" in r.stdout and "bootstrap" not in nk
    assert "CHƯA XÁC NHẬN: procinfo" in r.stdout and "DỌN: XONG" not in r.stdout


@pytest.mark.parametrize("tin", [signal.SIGTERM, signal.SIGHUP, signal.SIGALRM])
def test_ngat_khi_procinfo_chua_xac_nhan_thi_khong_bao_xong(tmp_path, tin):
    d = dung(tmp_path)
    p = subprocess.Popen(["/bin/bash", str(KB)],
                         env=moi_truong(d, G3_TRE_PROCINFO="3", G3_RC_PROCINFO="1"),
                         stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    try:
        het = time.monotonic() + 60
        while " procinfo " not in nhat_ky(d):
            assert time.monotonic() < het and p.poll() is None
            time.sleep(0.05)
        p.send_signal(tin)                   # chỉ PID kịch bản do test tạo; procinfo giả sắp trả lỗi
        ra, _ = p.communicate(timeout=60)
    finally:
        if p.poll() is None:
            p.kill()
            p.wait(timeout=5)
    assert p.returncode == 3 and "CHƯA XÁC NHẬN: procinfo" in ra, ra
    assert "DỌN: XONG" not in ra and "ỨNG VIÊN" not in ra
    assert "bootstrap" not in nhat_ky(d) and "submit" not in nhat_ky(d)
    assert sach(d)


@pytest.mark.parametrize("env, sau, cam", [
    ({"G3_RC_LOGIN": "0"}, "bootstrap login/", ("bootstrap gui/", "submit")),
    ({"G3_RC_LOGIN": "0", "G3_AN": "1"}, "bootstrap login/", ("bootstrap gui/", "submit")),   # thành công không nhãn
    ({"G3_LOGIN_LOT": "1"}, "bootstrap login/", ("bootstrap gui/", "submit")),
    ({"G3_RC_GUI": "0"}, "bootstrap gui/", ("submit",)),
    ({"G3_SUBMIT": f"gui/{TOI}"}, "submit", ())])
def test_ghi_lot_mien_dai_ca_thi_dung_ngay_ma_4_va_go(tmp_path, env, sau, cam):
    r, nk = chay(tmp_path, **env)
    assert r.returncode == 4 and "DỪNG S6" in r.stdout and "DỌN: XONG" in r.stdout and sach(tmp_path), r.stdout
    for chu in cam:
        assert chu not in nk[nk.index(sau):], nk


@pytest.mark.parametrize("env, chu", [({"G3_TK_THEM": "0@bootout"}, "lần 1: 1 tiến trình"),
                                      ({"G3_TK_THEM": "0@bootout", "G3_TK_DONG": f"999999 1 503 {TOI} x"},
                                       "lần 1: 1 tiến trình"),
                                      ({"G3_TK_THEM": "0@bootout", "G3_TK_DONG": f"999999 1 {TOI} 503 x"},
                                       "lần 1: 1 tiến trình"),
                                      ({"G3_PS": "rac@bootout"}, "lần 1: KHÔNG ĐỌC ĐƯỢC"),
                                      ({"G3_PS": "loi@bootout"}, "lần 5: KHÔNG ĐỌC ĐƯỢC"),
                                      ({"G3_PS": "rong@bootout"}, "lần 1: KHÔNG ĐỌC ĐƯỢC"),
                                      ({"G3_BOOTOUT_HONG": "1"}, "CHƯA XÁC NHẬN gỡ")])
def test_don_con_sot_hay_khong_dem_duoc_thi_khong_bao_sach(tmp_path, env, chu):
    r, _ = chay(tmp_path, **env)
    assert r.returncode == 3 and chu in r.stdout and "DỌN: CHƯA XÁC NHẬN" in r.stdout, r.stdout
    assert "DỌN: XONG" not in r.stdout


def test_bi_ngat_giua_chung_van_don_va_xac_nhan(tmp_path):
    d = dung(tmp_path)
    p = subprocess.Popen(["/bin/bash", str(KB)], env=moi_truong(d, G3_TRE_LOGIN="3"), stdin=subprocess.DEVNULL,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    try:
        het = time.monotonic() + 60
        while "bootstrap login/" not in nhat_ky(d):
            assert time.monotonic() < het and p.poll() is None
            time.sleep(0.05)
        p.send_signal(signal.SIGTERM)          # chính tiến trình kịch bản do test tạo
        ra, _ = p.communicate(timeout=60)
    finally:
        if p.poll() is None:
            p.kill()
            p.wait()
    assert p.returncode == 143 and "bị ngắt (TERM)" in ra and "DỌN: XONG" in ra and sach(d), ra
    assert "bootstrap gui/" not in nhat_ky(d)


def test_het_han_tong_thi_dung_va_don(tmp_path):
    """Đo thời gian THẬT. Sự thật của bash (R4-02, giới hạn đã biết): trap ALRM chỉ chạy khi lệnh đang chờ kết thúc —
    bootstrap giả trễ 12 s nên kịch bản dừng SAU ~12 s, không phải ở giây 6; vẫn trong độ trễ lệnh giả + biên độ."""
    t = time.monotonic()
    r, nk = chay(tmp_path, G3_TRE_LOGIN="12", G3_HAN_TONG="6")
    tg = time.monotonic() - t
    assert r.returncode == 142 and "HẠN TỔNG 6s hết" in r.stdout and "DỌN: XONG" in r.stdout and sach(tmp_path)
    assert "bootstrap gui/" not in nk and 12 <= tg < 12 + 10, tg


def test_khoa_co_san_thi_khong_chay_gi(tmp_path):
    d = dung(tmp_path)
    (d / "out" / "g3b.khoa").mkdir(parents=True)
    r = subprocess.run(["/bin/bash", str(KB)], env=moi_truong(d), stdin=subprocess.DEVNULL, capture_output=True,
                       text=True, timeout=60)
    assert r.returncode == 2 and "đang có lần đo khác hoặc khoá sót" in r.stdout and nhat_ky(d) == "", r.stdout
    assert (d / "out" / "g3b.khoa").is_dir()                  # khoá không phải của lần này: không gỡ


def test_hai_lan_chong_nhau_lan_sau_khong_sudo(tmp_path):
    d = dung(tmp_path)
    p = subprocess.Popen(["/bin/bash", str(KB)], env=moi_truong(d, G3_TRE_LOGIN="5"), stdin=subprocess.DEVNULL,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    try:
        het = time.monotonic() + 60
        while "bootstrap login/" not in nhat_ky(d):
            assert time.monotonic() < het and p.poll() is None
            time.sleep(0.05)
        truoc = nhat_ky(d)
        r = subprocess.run(["/bin/bash", str(KB)], env=moi_truong(d), stdin=subprocess.DEVNULL, capture_output=True,
                           text=True, timeout=60)
        sau = nhat_ky(d)[len(truoc):]
        ra, _ = p.communicate(timeout=60)
    finally:
        if p.poll() is None:
            p.kill()
            p.wait()
    assert r.returncode == 2 and "đang có lần đo khác" in r.stdout and sau == "", sau
    assert p.returncode == 0 and "DỌN: XONG" in ra and not (d / "out" / "g3b.khoa").exists()


def test_khong_doc_duoc_bien_nhan_khi_don_thi_chua_xac_nhan(tmp_path):
    r, _ = chay(tmp_path, G3_KHOA_BN="1")
    assert r.returncode == 3 and "CHƯA XÁC NHẬN: không đọc được biên nhận" in r.stdout and "DỌN: XONG" not in r.stdout
    assert (tmp_path / "out" / "g3b.khoa").is_dir()           # dọn chưa xác nhận: giữ khoá


def test_khong_ghi_duoc_bang_tong_g38_thi_dung_truoc_moi_lenh_ghi(tmp_path):
    r, nk = chay(tmp_path, G3_HONG_PS_SAU="1")
    assert r.returncode == 1 and "G3.8: không ghi được bảng tổng ps-sau" in r.stdout and "bootstrap" not in nk
    assert "DỌN: XONG" in r.stdout and not (tmp_path / "out" / "g3b.khoa").exists()
```

- [ ] **Step 2: Chạy — đỏ**

Run: `tests/chan_host/chay.sh -q tests/test_g3_bo_sung.py`
Expected (thật): `33 failed in 0.55s` — mọi ca mã 127 vì `… docs/handovers/g3-bo-sung.sh: No such file or directory` (ca chờ dòng nhật ký thì kịch bản đã thoát); nhật ký chặn 0 dòng mới.

- [ ] **Step 3: Viết kịch bản**

`docs/handovers/g3-bo-sung.sh` (mới):

<!-- ap: tao docs/handovers/g3-bo-sung.sh -->
```bash
#!/bin/bash
# G3 bổ sung cho 3C-D7 (G3.8–G3.10), bản RÚT GỌN (D117). Đại ca chạy trong Terminal.app, gõ `dong-y` khi được hỏi:
#   bash "/Users/dai-ca/Developer/Ben Station/docs/handovers/g3-bo-sung.sh"
# Theo mẫu `.handover/g3/g3-do.sh` (đã chạy đạt 18/10): mỗi lệnh có hạn (perl alarm), lệnh dưới tram-kiem qua mảng
# TKC; cả lần chạy dưới HẠN TỔNG (perl alarm trên chính tiến trình này → SIGALRM → dọn). Tiền điều kiện: tram-kiem
# KHÔNG có tiến trình nào → mọi tiến trình tram-kiem về sau là của lần đo (trừ dịch vụ macOS tự bật như distnoted), nên
# dọn bằng `kill -KILL -1` DƯỚI tram-kiem (G3.5) chỉ trúng tài khoản dành riêng cho lần đo; có tiến trình → in, DỪNG,
# không giết. Mỗi bước đo phải đạt rõ ràng, không thì DỪNG trước mọi lệnh ghi launchd. Ghi được vào miền của Đại ca →
# dừng ngay, mã 4 (D66). Không kết luận "launchd từ chối": chỉ ỨNG VIÊN; chữ lỗi do Em + Codex phân loại sau.
# Mã: 0 ứng viên; 1 dừng/không kết luận; 2 không chạy; 3 dọn chưa xác nhận; 4 ghi được vào miền Đại ca; 130/142/143
# bị ngắt/hết hạn tổng (đã dọn). G3_GIA=<thư mục>: CHỈ cho test (lệnh giả trong thư mục đó).
# Độc quyền (R4-03): khoá `$OUT/g3b.khoa` (mkdir nguyên tử) lấy TRƯỚC ảnh tram-kiem ban đầu, giữ tới hết dọn; đã có →
# mã 2, không sudo/kill gì. Chỉ chạy khi trạm chưa bật giao việc (`giao_viec.bat: false`) — trạm cũng dùng tram-kiem.
# GIỚI HẠN ĐÃ BIẾT (R4-02): bash chỉ chạy trap ALRM/INT/TERM khi lệnh đang chờ kết thúc; lệnh tự bỏ qua SIGALRM thì
# không hạn nào cắt được nó, và phần dọn không có trần riêng. Đại ca ngồi trước Terminal: quá ~20 phút chưa xong thì
# ĐÓNG cửa sổ Terminal và báo Em (HUP → dọn; dọn treo thì khoá còn → lần sau tự dừng, Em kiểm tay).
set -u
D=$(cd "$(dirname "$0")" && pwd); REPO=$(cd "$D/../.." && pwd)
if [ -n "${G3_GIA:-}" ]; then
  B=$G3_GIA; SUDO=$B/sudo; LCTL=$B/launchctl; PS=$B/ps; ID=$B/id; PY=$G3_PY; GOC=$B/goc; OUT=$B/out
  CHO=0; DEM=0; HAN_TONG=${G3_HAN_TONG:-120}; NC_TEN=root; BAN_GIA=${G3_BAN:-}
else
  [ -t 0 ] || { echo "Không chạy: cần Terminal tương tác (Đại ca gõ dong-y)"; exit 2; }
  if [ "${1:-}" != --trong-han ]; then
    read -r -p "G3.8–G3.10: kill -1 + launchctl ghi dưới tram-kiem (nhãn thử). Gõ dong-y để chạy: " OK
    [ "$OK" = dong-y ] || { echo "Không chạy."; exit 2; }
    export G3_DONG_Y=dong-y
  fi
  [ "${G3_DONG_Y:-}" = dong-y ] || { echo "Không chạy."; exit 2; }
  SUDO=/usr/bin/sudo; LCTL=/bin/launchctl; PS=/bin/ps; ID=/usr/bin/id; PY="$REPO/.venv/bin/python"
  GOC=/Users/Shared/tram-kiem; OUT=$HOME/.tram/g3; CHO=10; DEM=1; HAN_TONG=900; NC_TEN=tram-kiem; BAN_GIA=
fi
# Hạn tổng: chạy lại chính kịch bản dưới perl alarm (alarm còn hiệu lực qua exec; SIGALRM → trap → dọn có hạn).
[ "${1:-}" = --trong-han ] || exec /usr/bin/perl -e 'alarm shift; exec @ARGV or die "exec: $!"' "$HAN_TONG" \
  /bin/bash "$0" --trong-han
LAN=$(date +%Y%m%d%H%M%S)-$$
mkdir -p "$OUT" && chmod 700 "$OUT" || exit 2
P="$OUT/g3b-$LAN"; RC="$P.receipt"; : > "$RC"
exec > >(tee "$P.log") 2>&1
exec 4>&1      # bash 3.2 chạy trap trong redirect của lệnh đang dở: dọn ghi thẳng fd 4
han() { local s=$1; shift; /usr/bin/perl -e 'alarm shift; exec @ARGV or die "exec: $!"' "$s" "$@"; }
TKC=("$SUDO" -n -H -u tram-kiem)
W="$GOC/g3b-$LAN"; NHAN="vn.tram.g3b.$LAN"; TOI=$(/usr/bin/id -u)
GUI_KHONG="Could not print domain: 125: Domain does not support specified action"
muc() { echo; echo "=== $* ==="; }
ghi() { echo "$*" >> "$RC" || { echo "DỪNG: không ghi được biên nhận"; exit 1; }; }
dem() { awk -v n="$2" 'index($0, n) {c++} END {print c+0}' "$1"; }
inmien() { # inmien <tk|toi> <miền> <tệp>: mã của print, tệp = stdout+stderr
  if [ "$1" = tk ]; then han 30 "${TKC[@]}" "$LCTL" print "$2" > "$3" 2>&1
  else han 30 "$LCTL" print "$2" > "$3" 2>&1; fi
}
# bang <tệp>: dòng pid ppid uid ruid comm của tram-kiem vào <tệp>. Mã 0 CHỈ khi ps mã 0, stderr rỗng, MỌI dòng đúng
# dạng số và có dòng của chính kịch bản (uid=ruid=người vận hành) — bảng thật sự đọc được, không bao giờ "0" giả.
bang() {
  han 10 "$PS" -A -o pid=,ppid=,uid=,ruid=,comm= > "$1.bang" 2> "$1.err" || return 1
  [ -s "$1.err" ] && return 1
  awk -v u="$UIDK" -v me="$$" -v toi="$TOI" '!/^ *[0-9]+ +[0-9]+ +[0-9]+ +[0-9]+ +[^ ]/ {hong=1}
    $1 == me && $3 == toi && $4 == toi {thay=1}  $3 == u || $4 == u {print}
    END {exit (hong || !thay)}' "$1.bang" > "$1"
}
XET='import sys
from tram.giao_viec.ban_chep import LoiBanChep
from tram.giao_viec.launchd_kiem import MOC_USER, xet_user
moc = MOC_USER.get(sys.argv[2])
if moc is None:
    sys.exit(f"chưa có mốc launchd cho macOS {sys.argv[2]}")
try:
    xet_user("".join(open(p, encoding="utf-8", errors="replace").read() for p in sys.argv[3:]), int(sys.argv[1]), moc)
except LoiBanChep as e:
    print(e)
    sys.exit(1)
print("sạch")'
xet() { han 60 "$PY" -I -c "$XET" "$UIDK" "$BAN" "$@"; }

UIDK=; DA_TK=0; SP=; PROC_LOI=0; KQ=1; NGAT=; CO_KHOA=0; KHOA="$OUT/g3b.khoa"; NL='
'
mkdir "$KHOA" 2>/dev/null || { echo "Không chạy: đang có lần đo khác hoặc khoá sót từ lần trước ($KHOA — xoá tay nếu chắc"\
  "không còn lần nào chạy)"; exit 2; }
CO_KHOA=1      # khoá của CHÍNH lần này: lấy trước ảnh tram-kiem ban đầu, gỡ ở cuối dọn khi DỌN: XONG
_don() {
  trap '' INT TERM ALRM HUP; local ok=1 loai nhan mien ai i n bn
  muc "Dọn (biên nhận $RC)"
  if [ "$DA_TK" != 1 ]; then echo "chưa chạy gì dưới tram-kiem — không có gì để dọn"; echo "DỌN: XONG"; go_khoa; return; fi
  # Đọc biên nhận MỘT lần; đọc lỗi = không biết đã tạo gì → chưa xác nhận (R4-04). Xét dòng trong bộ nhớ, không grep.
  if bn=$(cat "$RC"); then :; else echo "CHƯA XÁC NHẬN: không đọc được biên nhận $RC"; ok=0; bn=; fi
  while read -r loai nhan mien ai; do
    [ "$loai" = huy ] && han 30 "${TKC[@]}" "$LCTL" remove "$nhan" > /dev/null 2>&1
    [ "$loai" = khongro ] && { echo "CHƯA XÁC NHẬN: không biết job $nhan ở miền nào"; ok=0; }
    [ "$loai" = nap ] || continue
    if [ "$ai" = tk ]; then han 30 "${TKC[@]}" "$LCTL" bootout "$mien/$nhan" > /dev/null 2>&1
    else han 30 "$LCTL" bootout "$mien/$nhan" > /dev/null 2>&1; fi
    if inmien "$ai" "$mien" "$P-don.txt" && [ "$(dem "$P-don.txt" "$nhan")" = 0 ]; then echo "đã gỡ $nhan khỏi $mien"
    else echo "CHƯA XÁC NHẬN gỡ $nhan khỏi $mien"; ok=0; fi
  done <<< "$bn"
  case "$NL$bn$NL" in *"${NL}co thumuc$NL"*) han 30 "${TKC[@]}" /bin/rm -rf "$W";; esac
  case "$NL$bn$NL" in *"${NL}y-dinh thumuc$NL"*)   # chỉ xoá khi biên nhận chứng minh của lần này; luôn kiểm lại
    han 20 "${TKC[@]}" /bin/test -e "$W" -o -L "$W"; i=$?
    if [ "$i" = 1 ]; then echo "thư mục $W: không còn"
    else echo "CHƯA XÁC NHẬN: thư mục $W còn/không kiểm được"; ok=0; fi;;
  esac
  [ "$ok" = 1 ] || [ -n "$bn" ] || { han 20 "${TKC[@]}" /bin/test -e "$W" -o -L "$W"; [ $? = 1 ] || \
    echo "(thư mục $W còn — không xoá vì không đọc được biên nhận)"; }
  han 20 "${TKC[@]}" /bin/kill -KILL -1 2>/dev/null       # tài khoản dành riêng, đã chứng minh trống lúc bắt đầu
  [ -n "$SP" ] && wait "$SP" 2>/dev/null
  for i in 1 2 3 4 5; do sleep "$DEM"
    if bang "$P-don-ps.txt"; then n=$(wc -l < "$P-don-ps.txt" | tr -d ' ')
      echo "lần $i: $n tiến trình uid/ruid tram-kiem"
      [ "$n" = 0 ] || ok=0
    else echo "lần $i: KHÔNG ĐỌC ĐƯỢC bảng tiến trình"; ok=0; fi
  done
  [ "$PROC_LOI" = 1 ] && { echo "CHƯA XÁC NHẬN: procinfo lỗi/quá hạn — không biết hậu duệ root của sudo đã hết"; ok=0; }
  if [ "$ok" = 1 ]; then echo "DỌN: XONG"; go_khoa
  else echo "DỌN: CHƯA XÁC NHẬN — giữ cổng đóng, báo Em, không chạy lại (giữ khoá $KHOA tới khi Em kiểm tay)"
    exit 3; fi
}
go_khoa() { [ "$CO_KHOA" = 1 ] && { rmdir "$KHOA" || echo "không gỡ được khoá $KHOA — xoá tay"; }; CO_KHOA=0; }
trap '_don >&4 2>&4' EXIT
trap 'echo "bị ngắt (INT)" >&4; exit 130' INT
trap 'echo "bị ngắt (TERM)" >&4; exit 143' TERM
trap 'echo "HẠN TỔNG ${HAN_TONG}s hết" >&4; exit 142' ALRM
trap 'echo "mất Terminal (HUP)" >&4; exit 129' HUP
dung() { echo "DỪNG: $*"; exit 1; }

muc "Chuẩn bị"
date; echo "lần $LAN"
[ -x "$PY" ] || dung "không có python của repo ($PY)"
UIDK=$(han 10 "$ID" -u tram-kiem)
case "$UIDK" in ''|*[!0-9]*) dung "UID tram-kiem không phải số";; esac
{ [ "$UIDK" -ne 0 ] && [ "$UIDK" -ne "$TOI" ]; } || dung "UID tram-kiem = 0 hoặc = UID vận hành"
bang "$P-tk-dau.txt" || dung "không đọc được bảng tiến trình"
if [ -s "$P-tk-dau.txt" ]; then cat "$P-tk-dau.txt"
  dung "tram-kiem đang có tiến trình (danh sách trên) — không giết; Đại ca dừng chúng hoặc báo Em rồi chạy lại"; fi
DA_TK=1
han 10 "${TKC[@]}" /usr/bin/true || dung "sudo -n -u tram-kiem không chạy được"
han 60 "$PY" -I -c "import sys; from tram.giao_viec.ngu_canh_kiem import ngu_canh_hien_hanh as n
c = n(sys.argv[1]); print(repr(c)); print(c.ban)" "$NC_TEN" > "$P-ngu-canh.txt" 2>&1 || dung "không đọc được ngữ cảnh"
cat "$P-ngu-canh.txt"; BAN=${BAN_GIA:-$(tail -n 1 "$P-ngu-canh.txt")}
inmien tk "user/$UIDK" "$P-truoc-user.txt" || dung "print user/$UIDK lỗi trước khi ghi"
inmien toi "gui/$TOI" "$P-truoc-gui.txt" || dung "print gui/$TOI lỗi trước khi ghi"
[ "$(dem "$P-truoc-user.txt" "$NHAN")$(dem "$P-truoc-gui.txt" "$NHAN")" = 00 ] || dung "nhãn $NHAN đã tồn tại"
ghi "y-dinh thumuc"
trap 'NGAT=${NGAT:-INT}' INT; trap 'NGAT=${NGAT:-TERM}' TERM   # mkdir + ghi kết quả không bị cắt giữa chừng
han 20 "${TKC[@]}" /bin/mkdir -m 700 "$W"; M=$?; [ "$M" = 0 ] && ghi "co thumuc"
trap 'echo "bị ngắt (INT)" >&4; exit 130' INT; trap 'echo "bị ngắt (TERM)" >&4; exit 143' TERM
[ -n "$NGAT" ] && kill -s "$NGAT" $$
[ "$M" = 0 ] || dung "không tạo được thư mục MỚI $W (đã có, symlink có sẵn, hoặc lỗi) — không đụng"
for k in user login gui; do
  printf '%s\n' '<?xml version="1.0" encoding="UTF-8"?>' \
    "<plist version=\"1.0\"><dict><key>Label</key><string>$NHAN.$k</string>" \
    '<key>ProgramArguments</key><array><string>/usr/bin/true</string></array></dict></plist>' \
    | han 20 "${TKC[@]}" /usr/bin/tee "$W/$k.plist" > /dev/null || dung "không ghi được $W/$k.plist"
done

muc "G3.8 — trạng thái ổn định của user/$UIDK (kill -1 dưới tram-kiem rồi print; KHÔNG chỉ đọc). Mọi bước phải đạt."
han 20 "${TKC[@]}" /bin/kill -KILL -1 2>/dev/null; sleep "$CHO"
bang "$P-ps-truoc.txt" || dung "G3.8: không đọc được bảng tiến trình (trước)"
for n in 2 3; do
  han 30 "${TKC[@]}" "$LCTL" print "user/$UIDK" > "$P-user-$n.out" 2> "$P-user-$n.err" || dung "G3.8: print user-$n lỗi"
  echo "user-$n → 0"; sleep "$CHO"
done
han 30 "${TKC[@]}" "$LCTL" print "gui/$UIDK" > "$P-gui.out" 2> "$P-gui.err"; M=$?; echo "gui → $M"
[ "$M" = 125 ] && [ "$(cat "$P-gui.out" "$P-gui.err")" = "$GUI_KHONG" ] || dung "G3.8: print gui/$UIDK khác dạng đã đo"
: > "$P-ps-sau.txt" || dung "G3.8: không ghi được bảng tổng ps-sau"; N=0
for i in 1 2 3 4 5 6 7 8 9 10; do sleep "$DEM"
  bang "$P-ps-lan.txt" || dung "G3.8: không đọc được bảng tiến trình (lượt $i)"
  n=$(wc -l < "$P-ps-lan.txt" | tr -d ' '); case "$n" in ''|*[!0-9]*) dung "G3.8: không đếm được lượt $i";; esac
  N=$((N + n)); cat "$P-ps-lan.txt" >> "$P-ps-sau.txt" || dung "G3.8: không ghi được bảng tổng ps-sau"
done
echo "ps-sau: $N dòng"     # đếm từ từng lượt đã đọc được, không từ tệp tổng (R4-04)
[ "$N" = 0 ] || dung "G3.8: print sinh tiến trình dưới tram-kiem (rủi ro 4 — cổng đóng giả), ghi nhận rồi dừng"
for n in 2 3; do
  R=$(xet "$P-user-$n.out" "$P-user-$n.err"); M=$?; echo "xet_user user-$n: $R"
  [ "$M" = 0 ] || dung "G3.8: bộ đọc không xác nhận sạch user-$n"
done

muc "G3.9 — ASID (D52: hỏi MẬT KHẨU cho sudo launchctl procinfo, chỉ đọc)"
han 90 "${TKC[@]}" /bin/sleep 60 & SP=$!; sleep 1
bang "$P-ps-sleep.txt" || dung "không đọc được bảng tiến trình"
LA=$(awk -v p="$SP" -v u="$UIDK" '{cha[$1]=$2} $3 == u && $4 == u && $5 ~ /sleep$/ {la[$1]=1}
  END {for (i in la) if (i == p || cha[i] == p || cha[cha[i]] == p) print i}' "$P-ps-sleep.txt.bang")
case "$LA" in ''|*[!0-9]*) dung "không thấy đúng một sleep của tram-kiem dưới sudo $SP";; esac
PROC_LOI=1     # đặt TRƯỚC lệnh: trap có thể thoát trước khi shell nhận/xét mã trả về
han 60 "$SUDO" "$LCTL" procinfo "$LA" > "$P-procinfo.txt" 2>&1; M=$?; echo "procinfo → $M"
[ "$M" = 0 ] || dung "procinfo mã $M — không dùng ASID"
PROC_LOI=0     # chỉ xoá dấu chưa xác nhận sau khi đã xét mã 0; ngắt trước đây giữ mã dọn 3
han 10 "${TKC[@]}" /bin/kill -KILL "$LA"; wait "$SP" 2>/dev/null; SP=
bang "$P-ps-sleep.txt" || dung "không đọc được bảng tiến trình sau khi dừng sleep"
[ -s "$P-ps-sleep.txt" ] && dung "còn tiến trình tram-kiem sau khi dừng sleep"
ASID=$(awk '/^audit info$/ {a=1; next} a && /^\tsession id = [0-9]+$/ {print $4; exit}' "$P-procinfo.txt")
HANDLE=$(awk '/^\thandle = [0-9]+$/ {print $3; exit}' "$P-truoc-gui.txt")
echo "asid(procinfo)=${ASID:-?} handle(gui/$TOI)=${HANDLE:-?}"
{ [ -n "$ASID" ] && [ "$ASID" = "$HANDLE" ]; } || dung "ASID không xác minh được (procinfo ≠ handle gui/$TOI)"

muc "G3.10 — đối chứng dương: plist cùng loại nạp vào user/$UIDK, bộ đọc thật trên ảnh có job / sau gỡ"
ghi "nap $NHAN.user user/$UIDK tk"
han 30 "${TKC[@]}" "$LCTL" bootstrap "user/$UIDK" "$W/user.plist" > "$P-nap-user.txt" 2>&1; MU=$?
inmien tk "user/$UIDK" "$P-user-co-viec.txt"; IU=$?
han 30 "${TKC[@]}" "$LCTL" bootout "user/$UIDK/$NHAN.user" > /dev/null 2>&1
inmien tk "user/$UIDK" "$P-user-sau-don.txt"; IS=$?
XC=$(xet "$P-user-co-viec.txt"); MC=$?; XS=$(xet "$P-user-sau-don.txt"); MS=$?
echo "bootstrap → $MU; print → $IU, $IS; bộ đọc ảnh có job: $XC; bộ đọc sau gỡ: $XS"
MONG="user/$UIDK: 1 dịch vụ launchd ngoài mốc — tram-kiem có job (C01 hàng 20)"
[ "$MU$IU$IS$MC$MS" = 00010 ] && [ "$XC" = "$MONG" ] \
  && [ "$XS" = sạch ] && [ "$(dem "$P-user-co-viec.txt" "$NHAN.user")$(dem "$P-user-sau-don.txt" "$NHAN.user")" = 10 ] \
  || dung "đối chứng dương không đạt — G3.9 KHÔNG KẾT LUẬN"
echo "đối chứng dương: ĐẠT"

muc "G3.9 — tram-kiem thử ghi vào miền của Đại ca (login/$ASID, gui/$TOI); ghi được ở bước nào thì DỪNG ngay"
thu() { # thu <tên> <miền đích>: nạp rồi quan sát gui/$TOI ngay
  ghi "nap $NHAN.$1 gui/$TOI toi"
  han 30 "${TKC[@]}" "$LCTL" bootstrap "$2" "$W/$1.plist" > "$P-g39-$1.txt" 2>&1; M=$?; echo "$1 → $M"
  [ "$M" = 0 ] && { echo "G3.9: GHI ĐƯỢC VÀO MIỀN CỦA ĐẠI CA ($1) — DỪNG S6, báo Em"; KQ=4; exit 4; }
  inmien toi "gui/$TOI" "$P-g39-sau-$1.txt" || dung "G3.9: KHÔNG KẾT LUẬN (print gui/$TOI lỗi)"
  [ "$(dem "$P-g39-sau-$1.txt" "$NHAN")" = 0 ] || { echo "G3.9: GHI ĐƯỢC VÀO MIỀN CỦA ĐẠI CA (thấy nhãn) — DỪNG S6"
    KQ=4; exit 4; }
}
thu login "login/$ASID"; thu gui "gui/$TOI"
ghi "nap $NHAN.submit user/$UIDK tk"; ghi "nap $NHAN.submit gui/$TOI toi"; ghi "huy $NHAN.submit"
han 30 "${TKC[@]}" "$LCTL" submit -l "$NHAN.submit" -- /usr/bin/true > "$P-g39-submit.txt" 2>&1; MS=$?
inmien toi "gui/$TOI" "$P-g39-mien-toi.txt"; IT=$?; inmien tk "user/$UIDK" "$P-g39-mien-tk.txt"; IK=$?
OT=$(dem "$P-g39-mien-toi.txt" "$NHAN"); SK=$(dem "$P-g39-mien-tk.txt" "$NHAN.submit")
LK=$(dem "$P-g39-mien-tk.txt" "$NHAN.")
echo "submit → $MS; print gui/$TOI → $IT (nhãn: $OT); print user/$UIDK → $IK (submit: $SK, mọi nhãn: $LK)"
[ "$IT" = 0 ] && [ "$OT" != 0 ] && { echo "G3.9: GHI ĐƯỢC VÀO MIỀN CỦA ĐẠI CA (submit) — DỪNG S6"; KQ=4; exit 4; }
[ "$MS" = 0 ] && [ "$IK$SK" != 01 ] && ghi "khongro $NHAN.submit"
if [ "$IT$IK$MS" = 000 ] && [ "$SK$LK" = 11 ]; then
  echo "G3.9: ỨNG VIÊN ĐẠT — Em + Codex phân loại chữ lỗi trong $P-g39-login.txt, $P-g39-gui.txt"; KQ=0
else echo "G3.9: KHÔNG KẾT LUẬN (print lỗi, submit không thành công hoặc không thấy đúng một chỗ)"; fi
exit "$KQ"
```

- [ ] **Step 4: Chạy — xanh**

Run: `tests/chan_host/chay.sh -q tests/test_g3_bo_sung.py`
Expected (thật): `33 passed in 97.30s` (lần chạy kế: `33 passed in 95.53s`), nhật ký chặn 0 dòng mới.

- [ ] **Step 5: Đột biến đã thử** (mỗi lần MỘT chỗ trong kịch bản, chạy `-k` qua runner, hoàn nguyên, `cmp` với bản giữ; số đỏ/số ca được chọn)

D1 bỏ dừng khi tram-kiem có tiến trình → 1/1; D2 bảng G3.8 hỏng vẫn đi tiếp → 2/8; D3 bỏ so chữ `gui` → 1/8; D4 bỏ đòi `ps-sau` = 0 → 1/8; D5 login thành công vẫn đi tiếp → 1/5 (thành công không để lại nhãn); D6 bỏ quan sát nhãn sau mỗi phép ghi → 1/5; D7 dọn: bảng không đọc được không làm hỏng xác nhận → 3/7; D8 bỏ đòi dòng của chính kịch bản trong bảng → 1/7 (bảng rỗng mã 0); D9 procinfo lỗi vẫn báo XONG → 4/4; D10 bỏ phán quyết bộ đọc trên ảnh có job → 1/8; D11 chỉ đếm khi uid VÀ ruid đều là tram-kiem → 2/8 (uid-only, ruid-only); D12 (R4-03) bỏ khoá độc quyền → 2/2 (khoá có sẵn, hai lần chồng nhau); D13 (R4-04) đọc biên nhận lỗi vẫn coi là xác nhận → 1/1; D14 (R4-04) bỏ cả hai chặn khi ghi bảng tổng `ps-sau` lỗi → 1/1 (bỏ riêng chặn `: >` thì chặn `cat >>` vẫn bắt — không đỏ, đúng thiết kế hai lớp); D15 (R4-01) đặt cờ procinfo SAU lệnh như bản trước → 3/3 (TERM, HUP, ALRM). **Không có test (ghi rõ):** hoãn ngắt quanh `mkdir` + `co thumuc` (giữ nguyên cơ chế đã đạt R2-03; D117 bỏ test thư mục có sẵn/ngắt sau mkdir để giữ bộ test gọn).

- [ ] **Step 6: Sửa sổ tay**

<!-- ap: va t3c -->
```diff
diff --git a/docs/handovers/2026-10-15-so-tay-chay-that.md b/docs/handovers/2026-10-15-so-tay-chay-that.md
index 8463f73..e0e6e48 100644
--- a/docs/handovers/2026-10-15-so-tay-chay-that.md
+++ b/docs/handovers/2026-10-15-so-tay-chay-that.md
@@ -42,7 +42,7 @@ Trong bàn giao này Claude được hoàn thiện thiết kế, sửa code và
 | G0 | **ĐẠT** | B0: nền `5da881e` 2242 pytest / 95 node, môi trường thử chặn `sudo`/cron/at/launchctl/security (`bs-863.1`). |
 | G1 | **ĐẠT** (thiết kế) | 3C-A: phụ lục [thiết kế 3c](2026-10-16-thiet-ke-3c-boundary.md), khả thi trong D45 **có điều kiện G4**. 4D-0: plan 4d. P1: hợp đồng H1–H8. D48–D53 chốt các câu hỏi còn lại. Review Codex cho đợt 7–8 **chưa có**. |
 | G2 | **ĐẠT (offline)** cho 3c, 4d, P1/3C-B, quota | `main`: 2242 → 2243 (V1) → 2269 (1a-2) → 2398 (4d) → 2566 (3c đợt 7) → 2650 (P1 + 3C-B + Q1/Q2) → **2697** (3c đợt 8). Mỗi task RED → GREEN trên bản thử, nhật ký chặn host rỗng (xem "Ghi chú triển khai" cuối từng plan). Còn mở: 3C-D7 (chờ G3), `bs-863.14`–`.19`. Không lấy 2697 làm bằng chứng OS. |
-| G3 | **GẦN XONG 18/10** (xem "Bằng chứng G3 — 18/10" cuối file; còn `login/<session id>`) | Cần Đại ca cho phép từng bước. Máy B 17/10: chưa có user `tram-kiem`, chưa có `/Users/Shared/tram-kiem`, `/usr/local/tram` (I1 kiểm bằng `id`, `ls`). Kịch bản ở mục G3 dưới. |
+| G3 | **GẦN XONG 18/10** (xem "Bằng chứng G3 — 18/10" cuối file; `login/<session id>` đã đo; còn G3.8–G3.10 cho 3C-D7) | Cần Đại ca cho phép từng bước. Máy B 17/10: chưa có user `tram-kiem`, chưa có `/Users/Shared/tram-kiem`, `/usr/local/tram` (I1 kiểm bằng `id`, `ls`). Kịch bản ở mục G3 dưới. |
 | G4 | **BỊ CHẶN** | Cần G3 rồi **3C-D7** (bộ đọc launchd). Trước 3C-D7, cổng kiểm lại luôn đóng — đúng thiết kế. |
 | G5 | **CHƯA CHẠY** | Mã Q1/Q2 đã có. Cần S2 (user khe), S5 (Codex của khe đăng nhập), tài khoản thử riêng. Kịch bản ở mục G5 dưới. |
 | G6 | **CHƯA CHẠY** | G6.1 đạt (4D-1a..3c trên `main`, +129). G6.2 đạt ở mức mã (1a-2 T5 ghép trước 4d). G6.3–G6.8 chưa. Kịch bản ở mục G6 dưới. |
@@ -110,6 +110,29 @@ Không dùng glob hoặc tìm PID theo tên để dọn. Thực hiện theo rece
 
 **Ra khỏi G3:** Đại ca gửi `~/.tram/g3/*` và transcript. Em viết plan **3C-D7** (parser chỉ cho định dạng đã đo, fixture là chính các tệp G3.3, định dạng khác → ném), qua review, ghép. Rồi mới vào G4.
 
+### G3 bổ sung cho 3C-D7 (G3.8–G3.10) — bản rút gọn (D117)
+
+Nguồn: [plan 3C-D7](../plans/2026-10-18-lat-3c-d7-bo-doc-launchd.md), Task 3. Một kịch bản bash [`g3-bo-sung.sh`](g3-bo-sung.sh) theo mẫu `.handover/g3/g3-do.sh`: mỗi lệnh có hạn (perl alarm), cả lần chạy dưới hạn tổng 900 s; lệnh dưới tram-kiem qua mảng `sudo -n -H -u tram-kiem`. **Tiền điều kiện:** tram-kiem không có tiến trình nào lúc bắt đầu (bảng `ps` đọc được, có dòng của chính kịch bản) — có thì in danh sách và DỪNG, không giết. Nhờ vậy tiến trình tram-kiem trong lúc chạy là của lần đo (trừ dịch vụ macOS tự bật như `distnoted`), và dọn bằng `kill -KILL -1` dưới tram-kiem (G3.5) chỉ trúng tài khoản dành riêng cho lần đo. Nhãn/đường riêng mỗi lần (`vn.tram.g3b.<lần>.*`, thư mục MỚI `$GOC/g3b-<lần>`), biên nhận ghi trước mỗi thao tác; dọn (kể cả khi Ctrl-C/SIGTERM/hết hạn tổng) gỡ đúng các nhãn trong biên nhận, kiểm lại miền và thư mục, `kill -1` dưới tram-kiem, đếm lại 5 lần — còn tiến trình hay không đếm được → "DỌN: CHƯA XÁC NHẬN". Kịch bản **không** kết luận "launchd từ chối" — chỉ ghi "ỨNG VIÊN" khi mọi điều kiện kiểm được đều đạt.
+
+**Điều kiện vào:** Task 1–2 của plan 3C-D7 đã ghép (kịch bản gọi `xet_user`, `MOC_USER`, `ngu_canh_hien_hanh` bằng `"$REPO/.venv/bin/python" -I`). Trạm CHƯA bật giao việc (`giao_viec.bat: false`) — trạm cũng dùng tram-kiem để kiểm lại; tiền điều kiện "tram-kiem trống" chặn thêm trường hợp trạm đang kiểm lại. Chỉ một lần đo một lúc: khoá `~/.tram/g3/g3b.khoa` (lấy trước ảnh tram-kiem ban đầu, gỡ khi `DỌN: XONG`); khoá có sẵn → "Không chạy: đang có lần đo khác hoặc khoá sót…", mã 2, không sudo/kill gì — chỉ xoá tay khi chắc không còn lần nào chạy; `DỌN: CHƯA XÁC NHẬN` thì khoá được GIỮ để lần sau tự dừng tới khi Em kiểm. **Đại ca cho phép riêng** (kill list mục 8): `kill -1` dưới tram-kiem; `launchctl` ghi dưới tram-kiem NGOÀI hồ sơ (chương trình `/usr/bin/true`, không lịch); một lần `sudo launchctl procinfo` hỏi mật khẩu (D52, chỉ đọc).
+
+**Chạy** (Terminal.app, gõ `dong-y` khi được hỏi): `bash "/Users/dai-ca/Developer/Ben Station/docs/handovers/g3-bo-sung.sh"`. **Đại ca ngồi trước Terminal suốt lần chạy.** Giới hạn đã biết: bash chỉ xử lý hạn tổng/Ctrl-C sau khi lệnh đang chờ kết thúc, phần dọn không có trần riêng — quá ~20 phút chưa xong thì ĐÓNG cửa sổ Terminal và báo Em (mất Terminal → dọn; dọn treo thì khoá còn → lần sau tự dừng, Em kiểm tay). Bằng chứng: `~/.tram/g3/g3b-<lần>.*` (log, biên nhận, đầu ra từng lệnh).
+
+| Phần | Kịch bản làm | Dòng kết quả cần đọc |
+|---|---|---|
+| Chuẩn bị | UID tram-kiem là số, khác 0, khác UID vận hành; tram-kiem không có tiến trình; `sudo -n` chạy được; in ngữ cảnh; in `user/<uid>` và `gui/<uid vận hành>` mã 0, chưa có nhãn của lần này; tạo thư mục mới, ba plist | `DỪNG: …` → không ghi launchd |
+| G3.8 | `kill -1` dưới tram-kiem (KHÔNG phải chỉ đọc), bảng trước; hai lần `print user/<uid>`, `print gui/<uid>`; 10 lần bảng; bộ đọc trên hai lần in — MỌI bước phải đạt, không thì DỪNG | `user-2 → 0`, `user-3 → 0`, `gui → 125`, `ps-sau: 0 dòng`, hai dòng `xet_user user-N: sạch` |
+| G3.9 (ASID) | `sleep` dưới tram-kiem → `sudo launchctl procinfo` (mã phải 0) → `audit info → session id`; dừng sleep và kiểm không còn; so với `handle` của `gui/<uid vận hành>` | `procinfo → 0`, `asid(procinfo)=N handle(…)=N`; procinfo lỗi → DỪNG và dọn báo CHƯA XÁC NHẬN |
+| G3.10 (đối chứng dương) | plist cùng loại nạp vào `user/<uid>` của tram-kiem, in, gỡ, in lại; bộ đọc thật trên hai ảnh | `bộ đọc ảnh có job: user/<uid>: 1 dịch vụ launchd ngoài mốc …`, `bộ đọc sau gỡ: sạch`, `đối chứng dương: ĐẠT` |
+| G3.9 (thử ghi) | `bootstrap login/<asid>` → quan sát `gui/<uid vận hành>` → `bootstrap gui/<uid vận hành>` → quan sát → `submit`; ghi được ở bước nào thì DỪNG ngay | `G3.9: ỨNG VIÊN ĐẠT` / `G3.9: KHÔNG KẾT LUẬN` / `G3.9: GHI ĐƯỢC VÀO MIỀN CỦA ĐẠI CA … DỪNG S6` |
+| Dọn | như trên | `DỌN: XONG`; `DỌN: CHƯA XÁC NHẬN` → giữ cổng đóng, báo Em, không chạy lại |
+
+Mã thoát: 0 ứng viên đạt; 1 dừng/không kết luận; 2 không chạy; 3 dọn chưa xác nhận; 4 ghi được vào miền của Đại ca; 129/130/142/143 mất Terminal/bị ngắt/hết hạn tổng (đã dọn). Test bằng lệnh giả: `tests/test_g3_bo_sung.py`. Lưu ý đã biết: launchd có thể tự bật lại `distnoted` dưới tram-kiem — khi đó dọn báo CHƯA XÁC NHẬN (an toàn), Đại ca gửi log cho Em.
+
+**Ra khỏi G3 bổ sung:** Đại ca gửi `~/.tram/g3/g3b-<lần>.*`. Em + Codex phân loại chữ lỗi của `g39-login.txt`/`g39-gui.txt` (chỉ coi là từ chối quyền khi chữ đo được nói vậy). Chỉ khi "ỨNG VIÊN ĐẠT", `DỌN: XONG` và phân loại xong mới viết plan nhỏ thêm ĐÚNG bộ ngữ cảnh in ở `g3b-<lần>-ngu-canh.txt` vào `BANG_CHUNG_LOGIN` (và nhãn `com.apple.*` thấy ở cả hai lần in `user`, nếu có và Đại ca duyệt, vào `MOC_USER` — D68), kèm `user-co-viec`/`user-sau-don` đã khử thông tin cá nhân làm fixture. Khác → cổng giữ đóng, Em trình phương án.
+
+**3C-D7 ở G4:** G4.0 chạy bộ đọc thật — "Vẫn đóng: … launchd …" thì ghi nguyên văn, dừng, gửi Em `print user/<uid tram-kiem>` (không gửi miền của Đại ca). G4.3: nguồn `submit`/`launchd` "CÀI ĐƯỢC" thì lý do cổng `dong` phải có "dịch vụ launchd ngoài mốc"; không có → báo Em. Bằng chứng G3.9 gắn ngữ cảnh (bản macOS, máy, UID kiểm, UID trạm, loại phiên): trạm chạy từ dịch vụ nền hay sau cập nhật macOS là ngữ cảnh khác → cổng tự đóng tới khi có bằng chứng cho ngữ cảnh đó.
+
 ## G4 — S6 cách ly (sau 3C-D7 ghép và review)
 
 **Chưa được vào G4:** hoàn tất V2 và `.18/.19` theo phụ lục trước. Không dùng “tránh Ctrl-C” làm biện pháp khắc phục. Kịch bản sau khi sửa phải có watchdog ngoài, receipt và đường ngắt đã kiểm; Ctrl-C/SIGTERM phải thử trong môi trường cô lập trước. Khi cleanup chưa rõ, giữ dấu/cổng đóng.
@@ -203,7 +226,7 @@ kèm và lặp thoát mã 1 (chưa có `tho.yaml`/token) → Đại ca `bootout`
 | V0.1 | **ĐẠT** | `chup_nhan()` 779 dòng, `ps -A` 779 dòng (gồm tiêu đề); không lỗi bố cục |
 | G3.1 | **ĐẠT** | trong hồ sơ: ghi `$W/x` → 0; `$GOC/ngoai`, `/Users/Shared/…`, `/private/tmp/…` → 1 "Operation not permitted" |
 | G3.2 | **ĐẠT** | trong hồ sơ: `crontab -l`, `launchctl print user/503`, `at -l` → 126 "Operation not permitted" |
-| G3.3 | **MỘT PHẦN** | `print user/503` → 0 (`user.txt`; domain do chính lệnh print tạo, `asid = 100172`); `print gui/503` → 125 "Domain does not support specified action"; procinfo (D52) không có trường `asid` — macOS 15 ghi `audit info → session id = 100003`; `print login/100003` CHƯA chạy |
+| G3.3 | **ĐẠT** (bổ sung 18/10) | `print user/503` → 0 (`user.txt`; domain do chính lệnh print tạo, `asid = 100172`); `print gui/503` → 125 "Domain does not support specified action"; procinfo (D52) không có trường `asid` — macOS 15 ghi `audit info → session id = 100003`; `print login/100003` → 0 (xem "Bổ sung G3.3" dưới) |
 | G3.4 | **ĐÃ GHI** | cây `sudo(uid 0, ruid 501) → sleep(uid=ruid=503)`, không có tiến trình giám sát pty chen giữa; cùng lúc thấy một tiến trình uid 503 cha là launchd (agent hệ thống, vd. `distnoted`) |
 | V0.2 | **ĐẠT** | `chup_nhan()` từ tài khoản trạm thấy 2 tiến trình uid=ruid=503, đều có thời điểm sinh |
 | G3.5 | **ĐẠT** | `kill -KILL -1` dưới tram-kiem → mã 137 (lệnh tự trúng; sudo tự phát lại tín hiệu); 0 tiến trình uid 503 cả 5 lần quan sát |
@@ -214,4 +237,12 @@ kèm và lặp thoát mã 1 (chưa có `tho.yaml`/token) → Đại ca `bootout`
 
 Ghi nhận cho thiết kế: launchd tự sinh lại agent hệ thống (`distnoted`) dưới UID dành riêng khi tài khoản đó có hoạt động
 (thấy lại 1 tiến trình sau G3.6). `don_uid` đếm cả tiến trình này — G3.5 cho thấy ngay sau `kill -1` không bị sinh lại trong 5 s;
-G5/G7 phải theo dõi khe báo "còn tiến trình" giả do agent hệ thống. Còn thiếu: `login/<session id>` cho fixture 3C-D7.
+G5/G7 phải theo dõi khe báo "còn tiến trình" giả do agent hệ thống.
+
+**Bổ sung G3.3 (18/10, sau commit trên):** nguồn: Đại ca chạy
+`sudo -n -H -u tram-kiem /bin/launchctl print login/100003 > ~/.tram/g3/login.txt` lúc 08:47 ngày 18/10/2026 trên máy B,
+mã 0 (mtime tệp 08:47). Đầu ra (`login.txt`, 2332 dòng) mang tiêu đề `gui/501`, `type = login`, `session = Aqua`,
+`security context` uid **501**: asid 100003 là phiên GUI của **Đại ca** (tiến trình tram-kiem chạy qua sudo từ Terminal
+mang audit session của Đại ca), không phải miền của tram-kiem. Tệp chứa danh sách ứng dụng cá nhân → KHÔNG đưa nguyên
+vào repo; 3C-D7 dùng bản rút gọn, khử thông tin cá nhân, và KHÔNG in miền này khi quan sát (xem plan 3C-D7). Còn thiếu
+cho 3C-D7: G3.8–G3.10 ở mục "G3 bổ sung" trên.
```

Run: `ls docs/handovers/g3-bo-sung.sh && grep -n "G3 bổ sung cho 3C-D7\|Bổ sung G3.3\|3C-D7 ở G4" docs/handovers/2026-10-15-so-tay-chay-that.md`
Expected: tệp tồn tại; ba dòng khớp.

- [ ] **Step 7: Chạy cả bộ**

Run: `tests/chan_host/chay.sh -q`
Expected (thật): `3337 passed in 424.55s` (Task 1 + 2 + 3 trên `main` `74cce8b`; cùng nền chỉ Task 1 + 2: `3304 passed in 342.62s` — chênh 33 = số test của tệp này), nhật ký chặn 0 dòng mới.

- [ ] **Step 8: Commit**

```bash
git add tests/test_g3_bo_sung.py docs/handovers/g3-bo-sung.sh docs/handovers/2026-10-15-so-tay-chay-that.md
git commit -m "docs(so-tay): kịch bản G3.8–G3.10 rút gọn cho 3C-D7 — tram-kiem phải trống lúc đầu, cổng dừng trước mọi lệnh ghi, ghi lọt miền Đại ca → mã 4, dọn đếm lại 5 lần (D117, lát 3c 3C-D7)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

## Việc sau G3 bổ sung (không có mã trong plan này — thay Task 4 vòng 1)

Chỉ khi Đại ca đã cho phép và chạy kịch bản Task 3, kết quả "G3.9: ỨNG VIÊN ĐẠT", "DỌN: XONG", G3.8 hai dòng `xet_user user-N: sạch` và `ps-sau: 0 dòng` (bảng đọc được cả 10 lượt), G3.10 hai dòng bộ đọc như mong đợi:
1. Em + Codex đọc `g39-login.txt`, `g39-gui.txt`: chỉ coi là "launchd từ chối quyền" khi chữ đo được nói rõ điều đó; chữ khác (thiếu tệp, miền sai, lỗi I/O…) → không kết luận, không viết tiếp.
2. Plan nhỏ (review riêng) thêm ĐÚNG bộ `NguCanh(...)` in ở `g3b-<lần>-ngu-canh.txt` vào `BANG_CHUNG_LOGIN` (test: ngữ cảnh đó đi tiếp, mọi ngữ cảnh khác lệch một trường vẫn đóng), kèm đường dẫn bằng chứng và chữ lỗi đã phân loại trong chú thích; `g3b-<lần>-user-co-viec.txt` / `-user-sau-don.txt` (miền của tram-kiem) đã khử thông tin cá nhân thành fixture có job / sau gỡ cho `xet_user` — lấy từ đầu ra đo, không tự đoán trước.
3. Nếu G3.8 thấy nhãn ổn định ở CẢ hai lần in `user` và Đại ca duyệt danh sách (Câu hỏi 4) → thêm đúng các nhãn đó (không tiền tố) vào `MOC_USER["24G90"]` trong cùng plan nhỏ.
4. Kết quả khác → không viết, cổng giữ đóng, Em trình phương án (A1 phụ lục §5, hoặc trạm gọi `sudo` từ phiên không phải Aqua).

## Cổng OS cần đo (mỗi bước Đại ca cho phép riêng, tự gõ)

| Bước | Loại | Đo gì | Quyết định gì |
|---|---|---|---|
| G3.8 (kịch bản) | `kill -1` + `print` dưới `tram-kiem` (KHÔNG phải chỉ đọc) | trạng thái ỔN ĐỊNH của `user/<uid>` (hai lần), kênh chữ của `gui/<uid>`, lệnh print có sinh tiến trình dưới `tram-kiem` không | mốc `user` (Câu hỏi 4); rủi ro 4 (cổng đóng giả) |
| G3.9 (kịch bản) | `procinfo` (D52, mật khẩu) + **`launchctl` ghi dưới `tram-kiem`, ngoài hồ sơ** (đối chứng dương, nhãn thử, `/usr/bin/true`) | ASID; launchd có cho `tram-kiem` `bootstrap` vào `login/<asid>`, `gui/<uid vận hành>` không; job `submit` rơi vào đâu; ngữ cảnh lúc đo | "ỨNG VIÊN" → việc sau G3; "GHI ĐƯỢC" → **dừng S6**, hàng 22 không đóng được bằng quan sát, trình A1 |
| G3.10 (kịch bản) | **`launchctl` ghi dưới `tram-kiem`** — chỉ miền của chính nó | đầu ra THẬT của `user/<uid>` có một job, và sau `bootout`; `xet_user` thật trên cả hai | đối chứng dương của G3.9; bộ đọc bắt job thật (đúng lỗi "1 dịch vụ launchd ngoài mốc") và sạch sau gỡ — khác thì không thử miền người vận hành |
| G4.0 (sau việc sau G3) | có sẵn trong sổ tay | `mo-cong-kiem` chạy bộ đọc thật | "Vẫn đóng: … launchd …" → ghi, dừng, gửi Em `print user/<uid>` |
| G4.3 | có sẵn | nguồn `submit`/`launchd` "CÀI ĐƯỢC" | lý do `cong.json` phải có "dịch vụ launchd ngoài mốc" |
| Phiên chạy thật khác / cập nhật macOS | — | ngữ cảnh khác | cổng tự đóng; cần bằng chứng cho ngữ cảnh đó |

## Kiểm chứng plan (số đo thật, 18/10/2026)

- N₀: `tests/chan_host/chay.sh -q -p no:cacheprovider` trên `d340a27` → **3236 passed** (347,84 s), nhật ký chặn 0 dòng mới, điểm mù 48 (có sẵn).
- RED/GREEN ở các bước trên là đầu ra thật trong worktree.
- Đột biến: Task 1 Step 5, Task 3 Step 5.
- **Áp lại từ chính file plan:** script trích mọi khối `<!-- ap: tao … -->` (ghi tệp) và `<!-- ap: va … -->` (`git apply`) theo thứ tự, áp lên worktree sạch `d340a27`: sha256 ba fixture khớp bảng; RED Task 1 (2 lỗi thu thập), Task 2 (`1 failed, 1 passed`), Task 3 (`16 failed`) lặp lại đúng như trên; xanh `61 passed` / `65 passed` / `16 passed`; cả bộ **3294** sau Task 1 (330,81 s), **3294** sau Task 2 (330,55 s), **3310** sau Task 3 (354,40 s), nhật ký chặn 0 dòng mới mỗi lần, điểm mù 48 (bằng N₀). `diff -r` `tram/`, `tests/`, `docs/` của bản áp lại với trạng thái đã chạy RED→GREEN (dựng lại thành chuỗi commit trong một bản sao tạm): **khớp**.
- Hoàn nguyên: `git checkout -- tram tests docs` + xoá các tệp mới; nhánh chỉ còn file plan.
- Bản vòng 1 (trên `306c5d9`) đo N₀ 3236 → 3268; bản này thay toàn bộ khối mã của vòng 1.
- **Vòng 4 — bản rút gọn D117 (18/10/2026, `main` `74cce8b` = sau V4-2):** áp Task 1 + Task 2 từ chính plan (sha256 ba fixture khớp bảng; ba tệp test Task 1–2 → 65 passed), rồi Task 3 rút gọn: RED `26 failed`, xanh `26 passed` (2 lần liên tiếp), 11 đột biến đều đỏ, cả bộ **3304** (T1+T2, 342.62s) → **3330** (T1+T2+T3, 449.26s), nhật ký chặn 0 dòng mới mỗi lần. Áp lại TOÀN BỘ khối `ap` (Task 1–3) từ plan lên bản sạch `git archive 74cce8b` rồi `diff -r` `tram/`, `tests/`, `docs/handovers/` với worktree đã chạy: **khớp**. Bản vòng 3 (41 test, thân Python) đã bị thay; số N₀/Task 1–2 cũ ở trên là của nền `d340a27`, giữ làm lịch sử.
- **Vòng bổ sung R4 (18/10/2026, cùng nền):** áp TOÀN BỘ khối `ap` của plan sau commit Codex `a435570` (R4-01) lên worktree; 3 ca R4-01 chạy thật: xanh với sửa của Codex, đỏ 3/3 khi đặt cờ như bản trước. Thêm R4-03/R4-04 + 4 test: RED `33 failed`, xanh `33 passed` (2 lần), 15 đột biến đều đỏ, cả bộ **3337** (424.55s), nhật ký chặn 0 dòng mới. Áp lại từ plan lên bản sạch `git archive 74cce8b` + `diff -r` `tram/`, `tests/`, `docs/handovers/`: **khớp**.

## Câu hỏi cho Đại ca (chưa trả lời — bản này dùng ĐỀ XUẤT làm giả định)

1. **Miền đăng nhập (`login`) — quan sát thế nào?** Tài khoản kiểm `tram-kiem` với tới "miền đăng nhập" của **phiên màn hình của chính Đại ca**, và trong đó không biết mục nào do `tram-kiem` tạo. (A) Không đọc; chỉ mở khi đo được trên đúng máy, đúng cách chạy rằng macOS từ chối `tram-kiem` cài job vào phiên của Đại ca. (B) Đọc và so ảnh chụp — đóng nhầm liên tục, phải lưu danh sách ứng dụng của Đại ca. (C) Không bao giờ mở — S6 không chạy được. **Đề xuất A (đang dùng).** Chọn sai: A chỉ mở khi có bằng chứng đúng ngữ cảnh; không có trường hợp "mở mà không biết".
2. **Cho phép chạy kịch bản G3.8–G3.10?** Kịch bản giết mọi tiến trình của `tram-kiem` (`kill -1` dưới tài khoản đó), cho `tram-kiem` thử cài job vô hại (`/usr/bin/true`, nhãn thử, không hẹn giờ) NGOÀI hồ sơ chặn rồi tự gỡ và kiểm lại, hỏi mật khẩu một lần cho lệnh chỉ đọc `procinfo`. Khoảng 2–3 phút. **Đề xuất cho phép sau khi plan qua review vòng 2** — đây là lần cho phép riêng, không nằm trong việc duyệt plan.
3. **`tram-kiem` đọc được danh sách dịch vụ trong phiên của Đại ca** khi chạy ngoài hồ sơ chặn. (a) Chấp nhận, ghi rủi ro (mã agent trong lượt bị hồ sơ cấm chạy `launchctl`); (b) về sau cho trạm gọi `sudo` từ dịch vụ nền không gắn phiên màn hình. **Đề xuất (a) bây giờ + tạo bead xét (b) sau S2** (giả định đang dùng; bead chưa tạo — chờ Đại ca).
4. **Nếu G3.8 thấy macOS tự nạp dịch vụ hệ thống vào miền của `tram-kiem`**, có cho ghi ĐÚNG các nhãn đó (thấy ở cả hai lần đo, Đại ca duyệt danh sách; không cho theo tiền tố `com.apple.*`) vào mốc không? **Đề xuất có**, qua plan nhỏ có review.

## Thứ tự code đề xuất và file giao nhau

1. Task 1 → Task 2 — sau Đại ca duyệt + review Codex vòng 2 (cổng vẫn đóng, lý do G3.9).
2. Task 3 — sau Task 1 (kịch bản gọi mã Task 1) và sau review vòng 4; chạy kịch bản là lần cho phép riêng (D66: trình Đại ca kịch bản cụ thể trước).
3. Việc sau G3 bổ sung — plan nhỏ, chỉ khi kết quả đủ điều kiện.

File giao nhau: `tram/giao_viec/cong_that.py` (1 import, 1 dòng `dung_cong`, docstring), `quan_sat_kiem.py` và `lenh_nghiem_thu.py` (chỉ docstring), `tests/test_cong_that.py` (1 import, 1 assert), `docs/handovers/2026-10-15-so-tay-chay-that.md` (plan V4 cũng sửa: thêm G5.6/sửa G6.1 — khác câu, giữ cả hai), `docs/handovers/2026-10-16-thiet-ke-3c-boundary.md` (hàng 20–22, §2 mục 4). Bản vá dùng `git apply --3way` khi ngữ cảnh lệch, không sửa tay nội dung. Ba module mới và `g3-bo-sung.sh` không giao với plan nào (kịch bản chỉ gọi module Task 1 qua python của repo).

## Ghi chú review Codex đợt 9 vòng 1 — 18/10/2026

**CHƯA ĐẠT toàn plan.** Ghi chú này thắng các bước cho phép áp/chạy ở trên: chưa đưa kịch bản Task 1 vào chạy thật,
chưa áp Task 4. Review này chỉ đối chiếu tĩnh, không chạy mã/test/OS. Các số đo phía trên là lịch sử của tác giả.

- Task 1: G3.8 có `kill -KILL -1`, không phải chỉ đọc. G3.9 cần phân biệt từ chối quyền với lỗi hạ tầng và kiểm
  thành công từng lệnh quan sát; `grep -c = 0` không đủ. G3.8–G3.10 còn thiếu receipt riêng từng lần, hạn cưỡng chế,
  đường ngắt và xác nhận cleanup hữu hạn; không dùng các chuỗi shell hiện tại làm kịch bản đã được review đạt.
- Task 2: `xet_user` đang chấp nhận thiếu cả khối `unmanaged processes`/`endpoints` như rỗng. Cần sửa mã nguyên văn
  và test đột biến xoá khối bắt buộc trước vòng 2; chưa thay parser bằng một định dạng tự suy từ máy khác.
- Task 3: phần nối chữ ký khớp mã thật, nhưng chỉ ghép sau Task 2 đã sửa và đạt review.
- Task 4: chưa có bằng chứng G3.8–G3.10; cờ theo build không chứng thực đúng máy/principal/ngữ cảnh chạy.
  Giữ `False` tới khi hợp đồng bằng chứng được sửa và đo đủ. Không cho phép theo tên `com.apple.*` đơn thuần.

Chi tiết, mức độ và câu hỏi gộp: `REVIEW-CODEX-dot9-vong1.md` ở gốc worktree. Đây là danh sách lỗi của bản review,
không phải mã thay thế: các task bị chặn vẫn chưa có bản TDD hoàn chỉnh đạt yêu cầu.

Phản hồi cho ghi chú trên (số task trong ghi chú là đánh số vòng 1 — xem bảng ánh xạ): mục "Phản hồi review vòng 1" ở đầu plan (bản này thay các task bị chặn bằng mã + test đã chạy; vẫn cần review vòng 2).

## Review vòng 2 — ghi chú hiện hành (thắng ghi chú vòng 1)

- Task 1: đã thêm kiểm hai dòng `task-special ports` theo đúng fixture user (số cổng hex được thay đổi,
  số loại 4/9, bootstrap/access và miền UID phải khớp); 5 ca phủ định trong test nguyên văn. Trước sửa
  khối này chỉ cần tồn tại, nội dung bất kỳ vẫn được bỏ qua. Không mở rộng định dạng ngoài mẫu đã đo.
  `launchd_kiem.py` tăng 4 dòng; thêm 5 ca test. Các tổng test và số dòng cũ chỉ là lịch sử, chưa chạy lại.
- Task 2: nối `doc=doc_launchd` khớp mã thật; chỉ ghép sau Task 1, giữ `BANG_CHUNG_LOGIN` rỗng.
- Task 3 vẫn CHƯA ĐẠT, không dùng làm kịch bản được duyệt chạy: (1) `uidcon`/các pipeline `ps` nuốt lỗi,
  chưa kiểm cấu trúc bảng nên có thể báo 0 giả; (2) `han` chỉ đặt alarm rồi exec, chưa có chủ giám sát
  cây lệnh và cleanup có hạn; `wait "$SP"`, `ps` còn ngoài hạn; (3) tạo thư mục trước ghi receipt,
  ngắt ở giữa làm sót thư mục nhưng vẫn báo dọn xong; (4) `bootstrap login` thành công vẫn tiếp tục
  `bootstrap gui`/`submit`, trái D66; (5) G3.10 chưa gọi bộ đọc trên mẫu có job/sau gỡ như lời mô tả.
  Cần mã + test lỗi/ngắt/quá hạn cho từng điểm, không chỉ sửa lời dặn. Chi tiết và mức độ ở báo cáo vòng 2.
- Bằng chứng G3.9 vẫn chưa có, không thêm ngữ cảnh vào danh sách tin. Ghi nhận login ở sổ tay còn là
  hunk dự kiến, thiếu giờ đo cụ thể/xác nhận nguồn; không coi fixture hoặc lời tác giả là chứng thực OS.
- D65–D68 đã chốt hướng A, rủi ro đọc phiên và nhãn hệ thống đúng tên. Không hỏi lại; sửa kỹ thuật
  không cần một quyết định sản phẩm mới. Sau Task 3 đạt review mới trình kịch bản cụ thể theo D66.

## Phản hồi review vòng 2 (Codex đợt 9, `REVIEW-CODEX-dot9-vong2.md`) — tác giả, 18/10/2026

> Lịch sử: bản Task 3 nói trong mục này (lớp ngoài + thân Python) đã bị THAY bởi bản rút gọn D117 — xem "Phản hồi review vòng 3".

Phạm vi sửa: CHỈ Task 3 (và các dòng tham chiếu tới Task 3 ở đầu plan, Bảng G hàng G10, "Việc sau G3 bổ sung", "Cổng OS",
"Kiểm chứng plan", "Thứ tự code"). Task 1, Task 2 giữ nguyên từng ký tự bản đã đạt (gồm sửa R2-07 của reviewer). R2-06
thuộc plan A (V4-1), không thuộc plan này. Mọi bằng chứng dưới đây là chạy THẬT trong worktree `plan/3c-d7-launchd`
(nền `main` `74cce8b`, Task 1–2 áp từ chính plan) qua `tests/chan_host/chay.sh`, nhật ký chặn 0 dòng mới; không chạy
`launchctl`/`sudo`/`kill -1` thật, không chạy kịch bản ở chế độ thật.

| Mã | Mức | Đã sửa ở đâu | Bằng chứng (đỏ → xanh, đột biến) |
|---|---|---|---|
| R2-01 | Chặn | Task 3 Step 4 — thân `g3_bo_sung.py`: `bang()` (= `chup_nhan`, sysctl một lần, tự kiểm bố cục với dòng của chính tiến trình; lỗi/rỗng/rác/sai bố cục → None, không bao giờ `[]`), `cua_tk` (uid HOẶC ruid), G3.8 `ps-truoc`/`ps-sau` (bảng hỏng ở lượt nào → "KHÔNG ĐỌC ĐƯỢC BẢNG (lượt i)", không ra "0 dòng"), `_don_tien_trinh` (không đọc được → "KHÔNG ĐỌC ĐƯỢC", mã 3). Không còn pipeline `ps | awk | wc` nào | `test_bang_tien_trinh_hong_hay_con_tien_trinh_khi_don_thi_khong_bao_xong` (6 ca: lỗi sysctl, rỗng, rác, sai bố cục — tiêm qua CHÍNH đường kiểm của `chup_nhan`; uid-only; ruid-only), `test_g38_bang_hong_khong_bao_gio_thanh_0_dong`; RED 41/41 khi chưa có kịch bản; đột biến M1 (5 đỏ), M2, M19 |
| R2-02 | Chặn | Task 3 — cơ chế chạy thay toàn bộ: lệnh dưới tram-kiem qua `CongLich` (UID thực từ `xac_minh_uid`) → `chay_gioi_han`; lệnh của người vận hành qua `chay_gioi_han` + `kill_cuc_bo`; sleep cho procinfo qua `khoi_chay` vào danh sách sở hữu + `Nhom.thu_hoi`; lệnh hỏi mật khẩu `mat_khau` (nhóm tiền cảnh vì sudo đọc /dev/tty và vé gắn phiên; tín hiệu CHỈ tới pid con chưa gặt, `Goc` giữ xác; hậu duệ theo (pid, sinh); còn sót → `hong`); tín hiệu: handler chỉ ghi, cắt lệnh đang chờ (bộ chạy thu hồi cây) hoặc dừng ở điểm kiểm; trong dọn chỉ ghi, dọn chạy hết (mỗi lệnh có hạn). Lớp ngoài `g3-bo-sung.sh`: ông canh hạn tổng 900 s + hạn dọn 300 s, chỉ gửi tín hiệu cho chính con chưa gặt (gặt trong lúc chặn TERM/HUP). Không mở rộng tín hiệu sang PID/nhóm chưa chứng minh sở hữu | `test_lenh_va_con_treo_bo_qua_term_bi_thu_hoi_ca_cay` (lệnh + con bỏ qua TERM → cả hai chết), `test_bi_ngat_roi_qua_han_va_ngat_tiep_trong_luc_don_van_don_xong` (TERM giữa lệnh, lệnh dọn treo quá hạn, TERM lần hai lúc dọn → mã 143, DỌN: XONG, tiến trình treo đã hết), `test_lenh_hoi_mat_khau_treo_con_sot_thi_khong_xac_nhan`, `test_han_tong_gui_term_cho_than_va_than_tu_don`, `test_het_han_don_thi_kill_than_va_bao_chua_xac_nhan`; đột biến M3, M4, M5, M6 |
| R2-03 | Quan trọng | Task 3 — `BienNhan` (O_EXCL; mỗi dòng mở-ghi-fsync-đóng; lỗi → `Dung` trước thao tác), `tao_thu_muc` (`y-dinh` → mkdir với `cat=False` → `co`/`khong`/`chua-ro`), `don_thu_muc` (chỉ xoá khi `co`; mọi trạng thái trừ `khong` kiểm lại `/bin/test -e … -o -L …` dưới tram-kiem; còn mà chưa chứng minh → KHÔNG xoá, mã 3). Nhãn launchd: dòng `nap` là ý định (nhãn duy nhất, đã chứng minh chưa có ở hai miền → gỡ khi chưa chắc đã nạp vô hại), mỗi dòng ghi trước thao tác, lỗi ghi → dừng | `test_ngat_ngay_sau_mkdir_van_ghi_so_huu_va_xoa` (TERM tới thân ngay sau mkdir → biên nhận `y-dinh`+`co`, thư mục bị xoá, mã 143), `test_mkdir_qua_han_thi_khong_chung_minh_so_huu_va_khong_xoa`, `test_loi_ghi_bien_nhan_thi_khong_tao_gi`, `test_thu_muc_hay_symlink_co_san_thi_khong_dung_toi` (2), `test_nhan_cua_lan_nay_da_co_thi_khong_tao_gi`; đột biến M7–M10, M21 |
| R2-04 | Quan trọng | Task 3 — `thu_mien_toi` + `g39_ghi`: login → (mã 0 → 4 ngay; không thì print `gui/<uid vận hành>` ngay: thấy nhãn → 4, print lỗi/quá hạn hay phép thử quá hạn → 1) → gui (như vậy) → submit (thấy nhãn ở miền người vận hành → 4) | `test_ghi_duoc_vao_mien_nguoi_van_hanh_thi_dung_ngay_va_go` (5 ca, assert nhật ký không có `bootstrap gui/`/`submit` sau login thành công — kể cả thành công không để lại nhãn — hay nhãn lọt dù mã ≠ 0; không có `submit` sau gui thành công; submit rơi vào miền người vận hành); đột biến M11, M12 |
| R2-05 | Quan trọng | Task 3 — `g310`: `xet_user` thật (mốc `MOC_USER[bản]` của ngữ cảnh; bản chưa có mốc → dừng trước khi ghi) trên `user-co-viec` phải ĐÚNG `user/<uid>: 1 dịch vụ launchd ngoài mốc — tram-kiem có job (C01 hàng 20)`, trên `user-sau-don` phải `sạch`; cộng mã print và đếm nhãn. Đầu ra hai ảnh giữ trong `~/.tram/g3/` để làm fixture SAU cổng (mục "Việc sau G3 bổ sung") — không tự đoán dạng trước | `test_bo_doc_phai_bat_dung_job_va_sach_sau_go` (4 ca: ảnh có job lệch định dạng → lỗi định dạng ≠ đạt; ảnh sau gỡ còn khối trạng thái; bộ đọc giả không bắt job; bộ đọc giả luôn lỗi định dạng — chồng module qua `PYTHONPATH`, phần còn lại của `tram` là thật), `test_dieu_kien_truoc_hong_…[G3_BAN=99Z99]`, ca chính in đúng hai dòng bộ đọc; đột biến M13, M14, M15, M20 |
| #2 vòng 1 | Chặn | Đóng qua R2-01…R2-03 bằng mã + test ở trên (sở hữu tài nguyên, hạn, cleanup có kiểm) | như trên |
| #7 vòng 1 | Nhỏ | Task 3 Step 7 (hunk sổ tay): hàng G3.3 → ĐẠT, đoạn "Bổ sung G3.3" ghi đúng nguồn Đại ca xác nhận: lệnh `sudo -n -H -u tram-kiem /bin/launchctl print login/100003 > ~/.tram/g3/login.txt`, 08:47 ngày 18/10/2026, máy B, mã 0 (mtime tệp 08:47); bỏ câu "giờ đo theo dấu thời gian tệp, Đại ca xác nhận khi ghép" | — (docs); `git apply --check` hunk trên `74cce8b` sạch |

**Giới hạn còn lại, ghi rõ (an toàn chọn phía đóng):**
- Thân và bộ chạy là Python của repo; nếu chính tiến trình thân bị KILL (hết hạn dọn), cây con có thể còn — ông canh in "DỌN: CHƯA XÁC NHẬN" + đường biên nhận, mã 3; Đại ca báo Em, không chạy lại. Không có lớp nào "tự dọn sau khi bị KILL".
- Lệnh hỏi mật khẩu (D52) không có nhóm riêng: hậu duệ root của sudo không nhận tín hiệu của kịch bản (đúng ràng buộc "chỉ PID tự tạo"); còn sót → chưa xác nhận, mã 3.
- launchd có thể tự sinh lại agent hệ thống dưới UID tram-kiem (`distnoted`, ghi nhận G3.6) → dọn báo CHƯA XÁC NHẬN giả (an toàn); Em phân loại từ log, không nới điều kiện trong kịch bản.
- `sudo -n -H -u tram-kiem` cho `/usr/bin/tee`, `/bin/test` chưa được dùng ở G3 trước (sudoers đo ở G3.0 là `(tram-kiem) NOPASSWD`); nếu bị từ chối → dừng trước khi ghi launchd (tee) hoặc dọn chưa xác nhận (test) — không bao giờ báo sạch.
- Kịch bản vẫn chỉ đo ngữ cảnh Terminal (phiên Aqua); XPC thẳng ngoài hồ sơ không thử được bằng `launchctl` (như vòng 1).

**Câu hỏi cho Đại ca:** không có câu mới — D62–D68 đã đủ; nguồn `login.txt` đã ghi đúng như Đại ca xác nhận. Việc còn
lại theo D66: sau review vòng 3 ĐẠT, Em trình Đại ca kịch bản cụ thể (lệnh chạy, những gì nó làm trên máy B, mã thoát)
trước khi Đại ca tự gõ trong Terminal.app.

## Phản hồi review vòng 3 (Codex đợt 9, `REVIEW-CODEX-dot9-vong3.md`) — tác giả, 18/10/2026

> **Bổ sung reviewer vòng 4, 18/10/2026:** đã sửa cờ `PROC_LOI` để đặt trước `procinfo`, chỉ xoá sau khi xét mã 0;
> thêm 3 ca TERM/HUP/ALRM ngay khi procinfo đang chạy. Chưa chạy code/test theo yêu cầu review tĩnh. Các số 26 test,
> RED/GREEN và 11 đột biến bên dưới là số tác giả ghi TRƯỚC sửa này; bản hiện tại có 29 ca dự kiến, chưa đo lại.
> Chưa đóng R3-04 (hạn tổng/dọn); còn lỗ chạy đồng thời trong lập luận R3-01 và bỏ qua lỗi I/O khi xét sạch/dọn.
> Kết luận vòng 4: CHƯA ĐẠT;
> xem `REVIEW-CODEX-dot9-vong4.md` ở gốc worktree. Không dùng bảng phản hồi lịch sử dưới đây làm chứng nhận đã đóng lỗi.

Sau vòng 3 (Task 3 CHƯA ĐẠT), Đại ca chốt **D117**: bỏ bản lớp ngoài + thân Python, viết lại Task 3 thành MỘT kịch bản
bash ngắn kiểu `.handover/g3/g3-do.sh`. Mục "Phản hồi review vòng 2" ở trên là lịch sử của bản đã bị thay. Task 1, Task 2
giữ nguyên từng ký tự (so bằng máy đoạn "## Task 1" … "## Task 3" trước/sau sửa: trùng). Mọi số dưới đây chạy THẬT trong
worktree `plan/3c-d7-launchd` (nền `main` `74cce8b`, Task 1–2 áp từ chính plan) qua `tests/chan_host/chay.sh`, nhật ký
chặn 0 dòng mới; không chạy `sudo`/`launchctl`/`kill` thật, không chạy kịch bản ở chế độ thật.

| Mã | Mức | Xử lý trong bản rút gọn (Task 3) | Bằng chứng |
|---|---|---|---|
| R3-01 | Chặn | Không còn kênh tín hiệu "theo sở hữu cây": tiền điều kiện tram-kiem KHÔNG có tiến trình (bảng đọc được, có dòng của chính kịch bản; có tiến trình → in, DỪNG, không giết, không chạy gì dưới tram-kiem). Từ đó tài khoản là của riêng lần đo; `kill -KILL -1` chạy DƯỚI tram-kiem (nhân chặn tới UID khác — V0.5) chỉ khi tiền điều kiện đã đạt. Ngoại lệ ghi rõ: dịch vụ macOS tự bật dưới UID đó (`distnoted`) — sinh ra do chính hoạt động của lần đo. Tín hiệu khác duy nhất: `kill -KILL <pid sleep>` dưới tram-kiem cho sleep do kịch bản tạo | `test_tram_kiem_dang_co_tien_trinh_thi_dung_khong_giet_khong_lam_gi` (nhật ký lệnh giả RỖNG — không một `sudo`/`launchctl` nào); đột biến D1 |
| R3-02 | Chặn | `procinfo` là một lệnh tiền cảnh có hạn như g3-do.sh. Mã ≠ 0 → không dùng ASID, DỪNG trước mọi lệnh ghi, và dọn luôn báo "CHƯA XÁC NHẬN: procinfo lỗi/quá hạn", mã 3 — không bao giờ XONG khi không biết hậu duệ root của sudo. Giới hạn còn lại (ghi rõ): procinfo mã 0 thì coi lệnh đọc đã xong; kịch bản không theo dõi/không gửi tín hiệu tới tiến trình root | `test_procinfo_loi_thi_khong_dung_asid_va_khong_bao_xong`; đột biến D9 |
| R3-03 | Quan trọng | Mọi bước G3.8 và ASID là cổng `|| dung` TRƯỚC mọi lệnh ghi launchd: bảng trước/10 lượt sau đọc được, `ps-sau` 0 dòng, `print user` ×2 mã 0, `print gui/<uid>` mã 125 + đúng chữ đã đo, bộ đọc thật sạch cả hai ảnh, procinfo mã 0, sleep đã dừng và bảng xác nhận không còn, ASID = handle. Lỗi thoáng qua (chỉ một lần đọc hỏng) cũng dừng; dọn sau đó sạch nên không che lỗi đo | `test_buoc_do_khong_dat_thi_dung_truoc_moi_lenh_ghi_vao_mien_dai_ca` (8 ca: UID, bảng rác/lỗi một lần, print user lỗi, gui khác chữ, `ps-sau` có tiến trình, ASID lệch, ảnh có job lệch định dạng — assert không có `bootstrap login/`, `bootstrap gui/`, `submit`, không "ỨNG VIÊN"); đột biến D2, D3, D4, D10 |
| R3-04 | Quan trọng | Bỏ `uv run` và ông canh: Python cố định `"$REPO/.venv/bin/python" -I` (thiếu → DỪNG trước mọi thao tác); hạn tổng = kịch bản tự chạy lại dưới `perl alarm` (alarm qua `exec`), SIGALRM → trap → dọn. Giới hạn ghi rõ (chưa đo): `alarm` có bị ảnh hưởng khi chỉnh giờ hệ thống không; như g3-do.sh, mỗi lệnh `han` là alarm + exec — chương trình tự đổi xử lý SIGALRM thì chỉ hạn tổng của kịch bản còn hiệu lực (bash chạy trap sau khi lệnh đang dở kết thúc) | `test_het_han_tong_thi_dung_va_don` (mã 142, DỌN: XONG, không `bootstrap gui/`) |
| R3-N01 | Nhỏ | Hunk sổ tay giữ nguyên nguồn #7 đúng lời Đại ca xác nhận (lệnh, 08:47 ngày 18/10/2026, máy B, mã 0, mtime 08:47). Người ghép đối chiếu bản xác nhận của Đại ca trước khi ghép; không có thì giữ "chưa đối chiếu nguồn" | — (docs) |

Thêm theo D117 (D66): ghi lọt miền Đại ca → dừng ngay mã 4 — `test_ghi_lot_mien_dai_ca_thi_dung_ngay_ma_4_va_go` (5 ca, kể cả thành công không để lại nhãn); dọn còn sót/không đếm được → không báo sạch — `test_don_con_sot_hay_khong_dem_duoc_thi_khong_bao_sach` (7 ca: còn tiến trình uid+ruid, uid-only, ruid-only, bảng rác, lỗi, rỗng mã 0, gỡ nhãn không xác nhận); bị ngắt vẫn dọn — `test_bi_ngat_giua_chung_van_don_va_xac_nhan`. Tổng 26 test (thay 41), 11 đột biến đều đỏ.

**Câu hỏi cho Đại ca:** không có câu mới. Sau review vòng 4 ĐẠT, theo D66 Em trình Đại ca kịch bản cụ thể trước khi Đại ca
tự gõ trong Terminal.app.

## Phản hồi review vòng bổ sung (R4) (Codex đợt 9, `REVIEW-CODEX-dot9-vong4.md`) — tác giả, 18/10/2026

Điều phối chốt cách xử lý từng mục; làm xong là chốt, không thêm vòng Codex. Task 1, Task 2 giữ nguyên từng ký tự.
Mọi số chạy THẬT qua `tests/chan_host/chay.sh` trong worktree `plan/3c-d7-launchd` (nền `main` `74cce8b`, khối `ap` áp
từ chính plan), nhật ký chặn 0 dòng mới; không chạy `sudo`/`launchctl`/`kill` thật.

| Mã | Mức | Xử lý | Bằng chứng |
|---|---|---|---|
| R4-01 | Chặn | Giữ sửa của Codex (`a435570`): `PROC_LOI=1` trước `procinfo`, về 0 chỉ sau khi xét mã 0; sudo giả có `G3_TRE_PROCINFO` | `test_ngat_khi_procinfo_chua_xac_nhan_thi_khong_bao_xong` (TERM/HUP/ALRM) xanh; đặt cờ như bản trước → 3/3 đỏ (D15) |
| R4-02 | Quan trọng | Theo điều phối: KHÔNG thêm giám sát độc lập. Ghi **giới hạn đã biết** ở chú thích đầu kịch bản, Task 3 và sổ tay: trap của bash chỉ chạy khi lệnh đang chờ kết thúc; lệnh bỏ qua SIGALRM không bị cắt; dọn không có trần riêng. Biện pháp vận hành: Đại ca ngồi trước Terminal, quá ~20 phút chưa xong thì đóng cửa sổ Terminal và báo Em (HUP → dọn; dọn treo thì khoá còn → lần sau tự dừng, Em kiểm tay). Test hạn tổng nay đo thời gian thật: hạn 6 s, bootstrap giả trễ 12 s → kịch bản kết thúc trong [12 s, 22 s) — đúng sự thật là trap chờ lệnh đang dở, không phải dừng ở giây 6 | `test_het_han_tong_thi_dung_va_don` (mã 142, DỌN: XONG, `12 <= tg < 22`) |
| R4-03 | Quan trọng | Khoá `$OUT/g3b.khoa` (`mkdir` nguyên tử) lấy TRƯỚC ảnh tram-kiem ban đầu, giữ tới hết dọn; đã có → "Không chạy: đang có lần đo khác hoặc khoá sót từ lần trước (… xoá tay nếu chắc không còn lần nào chạy)", mã 2, không sudo/kill; chỉ gỡ khoá do chính lần này tạo, khi `DỌN: XONG` (chưa xác nhận → giữ khoá, chặn chạy lại tới khi Em kiểm — chặt hơn mức điều phối nêu, cùng hướng "không chạy lại"). Phạm vi: trạm thật cũng dùng tram-kiem → chỉ chạy khi `giao_viec.bat: false`; tiền điều kiện "tram-kiem trống" chặn trường hợp trạm đang kiểm lại | `test_khoa_co_san_thi_khong_chay_gi` (nhật ký lệnh giả rỗng, khoá lạ không bị gỡ), `test_hai_lan_chong_nhau_lan_sau_khong_sudo` (lần sau mã 2, không một dòng nhật ký mới; lần đầu vẫn ỨNG VIÊN + DỌN: XONG, khoá được gỡ); D12 2/2 |
| R4-04 | Quan trọng | Dọn đọc biên nhận MỘT lần (`bn=$(cat "$RC")`); đọc lỗi → "CHƯA XÁC NHẬN: không đọc được biên nhận", không xoá thư mục chưa chứng minh; xét `co thumuc`/`y-dinh thumuc` bằng so chuỗi trong bộ nhớ (không còn `grep` có thể lỗi mã 2). G3.8: `ps-sau` = tổng số dòng của TỪNG lượt đã đọc được (đếm không ra số → dừng); ghi bảng tổng (`: >`, `cat >>`) lỗi → DỪNG trước mọi lệnh ghi launchd | `test_khong_doc_duoc_bien_nhan_khi_don_thi_chua_xac_nhan` (biên nhận `chmod 000` sau submit → mã 3, không XONG, giữ khoá), `test_khong_ghi_duoc_bang_tong_g38_thi_dung_truoc_moi_lenh_ghi` (tệp tổng bị thay bằng thư mục → dừng, không `bootstrap`); D13, D14 |

**Còn lại, ghi rõ:** R4-02 là giới hạn đã chấp nhận theo điều phối (không phải đã đóng bằng mã); kịch bản vẫn phải đo
trên OS thật theo cổng sổ tay sau khi Đại ca cho phép (D66). Ghi chú của reviewer ở đầu "Phản hồi review vòng 3" (29 ca
dự kiến, chưa đo) được thay bằng số đo ở đây: 33 ca.

**Ghi nhận trung thực về cả bộ:** lần chạy cả bộ đầu tiên sau sửa ra `1 failed, 3336 passed` — ca
`tests/test_ban_chep_pipeline_han.py::test_ctrl_c_ngay_sau_khi_nguon_spawn_nguon_da_co_chu_va_bi_thu_hoi` (`DID NOT RAISE
KeyboardInterrupt`), tệp nền Task 3 không chạm; chạy riêng 5/5 xanh, lần cả bộ kế `3337 passed`. Ghi là test nền phụ
thuộc thời gian, không sửa trong plan này.
