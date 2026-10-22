# Lát V2b — vòng đời tiến trình: định danh, phạm vi gửi, sở hữu từ PID, dọn theo UID khe, thăm dò đúng principal, theo dõi dừng hữu hạn — Implementation Plan

> **Review cuối 18/10/2026, HEAD `3c2b46c`:** đã sửa nguyên văn Task 2 để lỗi đọc/đóng kqueue không cắt ngang sở hữu và thu hồi (R3-01). Hai ca test bổ sung CHƯA CHẠY. Mọi số RED/GREEN và `diff -r` bên dưới là bằng chứng tác giả của bản TRƯỚC sửa này, không phải bằng chứng cho bản cuối. V3-11 đã ghép, chỉ thêm `tests/test_vong_import.py`; không áp lại task đó. Kết luận và thứ tự ghép cuối: `REVIEW-CODEX-dot8-vong3.md`.

> **For agentic workers:** REQUIRED SUB-SKILL: dùng `ai-skills:subagent-driven-development` (khuyến nghị) hoặc `ai-skills:executing-plans` để làm từng task. Step dùng checkbox (`- [ ]`). **Chưa được code**: plan chạm kill list (cách ly — `tram/kiem/`, thăm dò cách ly, vòng khe thợ), phải qua Đại ca duyệt và review Codex trước (xem Global Constraints).

**Trạng thái: bản SỬA sau Codex review gộp vòng 2 (`.handover/review-codex-plan/REVIEW-CODEX-dot8-vong2.md` — R2-01…R2-04 và phần A của §4.1), 18/10/2026; vòng 1 (A01…A06) giữ như đã đóng.** Task 2–4 viết lại thành MỘT hợp đồng sở hữu (`tram/kiem/so_huu.py`) và MỘT bản thân hàm cuối cho `khoi_chay`/`Nhom`/`chay_gioi_han`/`chay_han_tong` mà plan B (V2c) áp TRÊN đó — không còn hai bản thay thân hàm cạnh tranh. Đã chạy RED→GREEN thật theo thứ tự ghép cuối (A-T1→T8 rồi B-T1→T9) trên `main` `f4fa3a8` (đã có V2-1/2/3/7, V3-1/5/8/9/10/16/17) trong worktree `plan/ab-tich-hop`, đo cả bộ sau các mốc; áp lại toàn bộ khối mã của hai plan lên bản sạch và `diff -r` khớp trạng thái đã chạy (mục "Phản hồi review vòng 2"). Mã đã hoàn nguyên, nhánh chỉ có file plan. CHƯA áp vào `main`. CHƯA đo trên OS (G3/G4/G5/G7 ĐÓNG).

**Goal:** Đóng thiết kế còn chặn của plan V2 cho vòng đời tiến trình: **V2-0** (dot7-C01 — `bs-2bd.1.11`, `bs-863.15`) thu hồi không bao giờ gửi tín hiệu ra ngoài phạm vi đã chứng minh **tại chính lúc gửi**, sở hữu tiến trình từ lúc có PID, và khe thợ chỉ sang lượt sau khi chứng minh sạch theo UID của khe; **V2-6b** (`bs-863.14`, `bs-863.17`) thăm dò âm và dò đăng nhập chạy đúng principal, có hạn, mỗi loại thăm dò một bằng chứng riêng, lỗi hạ tầng không bao giờ thành "đạt"; **V2-6c** (`bs-863.16`) luồng đọc hàng đợi của phiếu dừng trong MỘT hạn tổng.

**Architecture:** Nguồn ảnh chụp `tram/kiem/bang_tien_trinh.py` đọc bảng tiến trình của nhân bằng `sysctl(KERN_PROC)` (định danh sinh µs, không cần quyền). `giu_xac.Goc` biết gốc thoát mà **không gặt** (kqueue `NOTE_EXIT`) để xác giữ số nhóm gốc; chỉ `Nhom.thu_hoi` (khi đã xác nhận) mới gặt — kể cả trong `chay_gioi_han` (bỏ `communicate`). `khoi_chay` **sở hữu tiến trình từ lúc có PID** (`so_huu`: hoãn SIGINT/SIGTERM trong lúc spawn, lỗi/ngắt → giết nhóm gốc, `LoiThuHoi`; danh sách sở hữu `chu` cho người gọi). **Phạm vi gửi do chính lệnh gửi giới hạn** (`gui_tin`): nhóm gốc chưa gặt (số không thể cấp lại) qua mọi kênh; nhóm khác CHỈ qua `kill_nhom` của principal cơ chế `user` — chạy dưới UID dành riêng, nhân macOS chỉ cho trúng tiến trình của UID đó — không bao giờ qua kênh cục bộ hay principal `sandbox` dùng chung. `Nhom.thu_hoi` True chỉ nghĩa "cây QUAN SÁT ĐƯỢC đã hết"; khe thợ chỉ sang lượt/phiếu sau khi **dọn theo UID của khe** (`tho/don_uid.py`: `kill -KILL -1` dưới chính principal rồi chứng minh bằng bảng của nhân không còn tiến trình nào của UID đó) — lúc khởi động khe (thay dọn mồ côi theo số pid), đầu mỗi phiếu, sau mỗi lần chạy CLI; không chứng minh được → khe dừng. Thăm dò cách ly/đăng nhập đi qua `chay_gioi_han` với `kill` của principal sau `xac_minh_uid`; mỗi loại thăm dò có bằng chứng từ chối quyền riêng + đối chứng mục tiêu dưới quản lý. `TheoDoi` dừng trong MỘT hạn bao trùm cả lần đọc cuối.

**Tech Stack:** Python 3.12 stdlib (`ctypes`, `select.kqueue`, `selectors`, `signal`, `struct`, `subprocess`, `threading`), pytest 8. Không dependency mới.

**Spec / nguồn:** plan V2 [`2026-10-17-lat-v2-va-sau-review-dot7.md`](2026-10-17-lat-v2-va-sau-review-dot7.md) mục V2-0, V2-6b, V2-6c; review Codex đợt 7 (`.handover/review-codex-dot7/REVIEW-CODEX.md` — dot7-C01, bảng bead §6); **review Codex gộp vòng 1** (`.handover/review-codex-plan/REVIEW-CODEX-dot8-vong1.md` — A01…A06, §4 thứ tự ghép, §5 cổng OS, §6 câu hỏi gộp); phụ lục cổng [`2026-10-17-cong-sau-review-dot7.md`](../handovers/2026-10-17-cong-sau-review-dot7.md); plan P1 [`2026-10-16-lat-p1-vong-doi-tien-trinh.md`](2026-10-16-lat-p1-vong-doi-tien-trinh.md) (Rủi ro 1, 4, 8); spec 3 §7.2, §7.3 mục 2/5/7, §9.3; quyết định [D45–D53](../quyet-dinh/2026-10-16-chot-sau-review-dot6.md) (giữ nguyên, không mở lại — D53 là nền của lựa chọn A01/A02 bên dưới).

## Global Constraints

- **Kill list (`AGENT_RULES.md` §2 mục 3 — cách ly agent):** plan sửa `tram/kiem/` (`bang_tien_trinh`, `giu_xac`, `so_huu`, `gui_tin`, `cay_tien_trinh`, `vong_doi`, `chay_gioi_han`, `han_tong`, `danh_tinh`), vòng khe thợ (`tram/tho/don_uid.py`, `mo_coi`, `mo_coi_khe`, `vong_khe`, `ngu_canh`, `phieu_chay`, `mot_lan`, `cau_hinh`) và thăm dò cách ly (`tram/tho/kiem_am.py`, `cham_tham_do.py`, `kiem_cong.py`, `tram/chu/kiem_cach_ly.py`). **Phải có Đại ca duyệt plan và review Codex vòng sau trước khi code.** Không đụng `tram/giao_viec/principal_kiem.py`, `kiem_lai.py`, `kiem_principal.py`, `cong_that.py`, `tram/tho/sandbox.py`, `tram/tho/principal.py`; không đổi sudoers/installer; không đổi D45–D53.
- **`kill -KILL -1` chỉ được chạy DƯỚI principal của khe, sau khi UID đã chứng minh khác root/khác tài khoản đang chạy** (`don_uid` kiểm hai lần: `xac_minh_uid` + so `os.getuid()/geteuid()`). Test KHÔNG BAO GIỜ chạy `kill -1` thật: mọi test của `don_uid` truyền `chay`/`xac_minh`/`chup` giả; máy thợ giả (`tests/tho_chay_gia.py`) đặt `don_uid=lambda pr: None`.
- **N₀ = 2809** (`UV_OFFLINE=1 uv run pytest -q` trên `f4fa3a8`, đo 18/10/2026 với PATH chặn host + plugin `chan_host`; nhật ký chặn: 0 dòng mới). Sau plan đo thật **2947** (+138). Đo lại N₀ trước Task 1; lệch thì dừng, báo người điều phối.
- TDD: test trước, chạy thấy đỏ (thông báo ở bước RED là kết quả THẬT: mã của task trước + test của task này), mã, chạy thấy xanh, chạy cả bộ, commit. Mã trong plan là **nguyên văn** file mới / bản vá đã chạy — áp đúng như in, theo đúng thứ tự task (bản vá task sau dựa trên kết quả task trước).
- Mỗi file nguồn ≤ ~120 dòng, mỗi dòng ≤ 120 ký tự Unicode (sau plan: `tram/kiem/vong_doi.py` 120, `tram/chay_cli/codex/app_server.py` 120, `tram/tho/vong_khe.py` 120, `tram/tho/theo_doi.py` 116; test mới lớn nhất `tests/test_so_huu_ong.py` 115). Định danh tiếng Việt không dấu. Thông báo lỗi/kết quả không chép argv, đường dẫn của người khác, stdout/stderr (dot6-Q06, INV-001).
- **Test không bao giờ:** chạy `sudo`, `crontab`, `at`, `batch`, `launchctl`, `dscl`/`sysadminctl`, `security`, `pkill`, `killall`, `kill -1`; đụng Keychain, mạng, `~/.tram` thật. Tiến trình thật chỉ là `python -c` của chính user đang test, nhóm riêng, tự thu hồi đúng PID mình tạo (test ghi PID cháu ra file trong `tmp_path` và giết đúng PID đó trong `finally`). Đọc bảng tiến trình của nhân (`sysctl`, như `ps`) là chỉ đọc. kqueue chỉ gắn lên **con của chính test**. Tín hiệu ngắt trong test chỉ phát vào CHÍNH tiến trình test (`signal.raise_signal`) với handler của test.
- Chạy test bắt buộc với PATH chặn host (`AGENT_RULES.md` §13): `PATH="$C/bin:$PATH" PYTHONPATH="$C/plugin" UV_OFFLINE=1 uv run pytest -p chan_host -q …`; nhật ký chặn của worktree phải rỗng.
- Một task một commit (`fix(kiem): …` / `fix(tho): …` + dòng ghi công), trên nhánh tạo từ `main` sau lần ghép gần nhất. Không push, không merge, không `bd` ghi.
- **Giao nhau với plan khác (review §4, R2-03):** plan này là chủ của primitive VÀ của bản thân hàm cuối `chay_gioi_han`/`chay_han_tong` (Task 1–4): hợp đồng sở hữu `tram/kiem/so_huu.py` (thay "H-A03"), cơ chế hoãn ngắt DUY NHẤT `tram/kiem/ngat.hoan`. B-T6 chỉ thêm `stdin=` + `term_thanh_ngat`, B-T7 dùng `khoi_chay(chu=)`, B-T8 không sửa `han_tong.py`; xem mục "Thứ tự code đề xuất và file giao nhau" cuối file. Task 2 sửa thêm người gọi `khoi_chay` ngoài kill list mục 3 (`tram/kiem/chay_lenh.py`, `tram/chay_cli/claude.py`, `tram/chay_cli/codex/chay.py`, `tram/chay_cli/codex/app_server.py`) — chỉ đặt spawn vào khối sở hữu, hành vi thường giữ nguyên.

## Bảng G — điều plan bảo đảm và bằng chứng

| # | Bảo đảm | Ở đâu | Bằng chứng offline | Còn chờ OS |
|---|---|---|---|---|
| G1 | Nhóm ngoài gốc CHỈ được gửi qua kênh chạy dưới UID dành riêng (principal `user`); kênh cục bộ/`sandbox` chỉ gửi nhóm gốc chưa gặt. Thay nhóm sau lần kiểm cuối hay giữa hai kênh của `gop_kill` không trúng tiến trình ngoài UID khe | `gui_tin.kill_uid`, `GopKill`, `Nhom._gui` | `test_pham_vi_gui.py` (nhân GIẢ có UID; so TOÀN BỘ tín hiệu đã trúng), đột biến về thiết kế vòng trước → 4 đỏ | kiểm quyền gửi thật của nhân: `kill` dưới tài khoản khe tới tiến trình tài khoản khác bị EPERM (G3 V0.5) |
| G2 | Nhóm gốc chỉ được coi là "của cây" khi gốc là con chưa gặt (còn sống hoặc còn xác); chỉ `thu_hoi` đã xác nhận mới gặt — không `communicate`, không `poll` gặt sớm | `giu_xac.Goc`, `chay_gioi_han._ong`, `danh_tinh.quan_sat` | `test_giu_xac.py`, `test_so_huu_bo_chay.py` (gốc thoát nhanh, cháu ở nhóm gốc vẫn thu hồi qua nhóm gốc; dò danh tính không gọi `poll`) | — |
| G3 | Sở hữu từ lúc có PID (hợp đồng `so_huu`, R2-02): `khoi_chay(chu=)` bắt buộc; sau Popen `Nhom` vào `chu` TRONG `hoan()` trước mọi lối ra; nhánh lỗi đăng ký kqueue KHÔNG gặt (R2-01) — không tín hiệu nào tới số đã có thể cấp lại; SIGINT/SIGTERM lúc spawn/thu hồi được hoãn rồi phát lại khi `Nhom` đã có chủ; MỌI người gọi (`quan_sat`, lệnh kiểm, CLI Claude/Codex, app-server, bộ chạy, hạn tổng; B: `nguon_archive`) thu hồi trong khối sở hữu; `LoiThuHoi` = KHÔNG xác nhận (con có thể còn, `Nhom` còn trong `chu`, cổng/khe đóng) — không phải "không còn con"; lỗi đóng ống/selector không chặn thu hồi (R2-04); ngắt vẫn là ngắt | `ngat`, `so_huu`, `giu_xac`, `khoi_chay`, `chay_gioi_han`, `han_tong`, người gọi | `test_so_huu*.py` (6 file), `test_giu_xac.py`; tái hiện R2-01/R2-04 trên mã vòng 2 | lỗi nội bộ của `Popen` sau fork (không phải lỗi exec) — xem Rủi ro 1 |
| G4 | Định danh sinh µs của MỌI tiến trình, bố cục tự kiểm; mơ hồ (số nhóm cũ có người không chứng minh được) → không gửi, không xác nhận | `bang_tien_trinh`, `cay_tien_trinh.mo_ho` | `test_bang_tien_trinh.py`, `test_vong_doi_tai_su_dung.py` | bảng thấy tiến trình của principal (G3 V0.1–V0.2) |
| G5 | Khe thợ chỉ sang lần chạy/phiếu sau khi dọn theo UID khe chứng minh sạch (kill -1 dưới principal + bảng của nhân không còn uid/uid thực của khe); không chứng minh được (sandbox, UID chưa chứng minh/trùng, kill lỗi, còn tàn dư, không đọc được bảng) → khe dừng, giữ bản ghi + phiếu. Mồ côi KHÔNG còn bị giết theo số pid/pgid đọc từ file | `tho.don_uid`, `ngu_canh.don_khe`, `mo_coi`, `mo_coi_khe`, `phieu_chay`, `mot_lan`, `vong_khe` | `test_don_uid.py`, `test_mo_coi_uid.py`, `test_khe_tan_du.py` (vòng `tram tho chay` thật, CLI giả) | `kill -1` thật dưới khe thử, tàn dư setsid/TERM bị bỏ qua (G4, G7) |
| G6 | Thăm dò cách ly: dương trước; mỗi loại một bằng chứng từ chối quyền riêng + đối chứng mục tiêu dưới quản lý; lỗi hạ tầng (curl 7/28 + `000`, 127/126, 404/500, mục tiêu thiếu, mã chưa phân loại) → "không kết luận"; kết quả chỉ mang lý do cố định; còn tiến trình của principal sau thăm dò → ĐỎ (chỉ quan sát) | `cham_tham_do`, `kiem_am`, `kiem_cong.cach_ly`, `kiem_cach_ly` | `test_cham_tham_do.py` (đột biến về cách chấm vòng trước → 18 đỏ), `test_kiem_am_p1.py`, `test_tham_do_principal.py` | mã thoát/stderr thật từng loại dưới principal (G5) |
| G7 | Đăng nhập dò dưới principal (env mới); `LoiThuHoi` của lệnh đăng nhập nổi lên → không dò hạn mức dưới principal đó | `do_may.dang_nhap_codex`, `kiem_3b`, `kiem_cong.dang_nhap` | `test_dang_nhap_principal.py` | `codex login status` dưới principal thật (G5) |
| G8 | `TheoDoi`: MỘT hạn cho dừng luồng nền + lần đọc cuối; hết hạn → `LoiThuHoi` trong hạn, lần đọc cuối thôi ở ranh giới dòng kế tiếp; không hẹn `xong` nào được tạo sau khi đã bắt đầu dừng; không đọc song song | `theo_doi`, `trong_han`, `day`, `phieu_chay` | `test_theo_doi_dung.py`, `test_theo_doi_noi.py` | worker thật (G7) |

## Thiết kế V2-0 — định danh, phạm vi gửi, sở hữu, dọn theo UID

### Nền tảng đã đo (17/10/2026, lệnh chỉ đọc + tiến trình `python -c` của chính Em) — giữ nguyên, không đo lại

| Mục | Kết quả |
|---|---|
| Máy | `uname -a`: Darwin 24.6.0, `xnu-11417.140.69~1/RELEASE_ARM64_T8132`, arm64. `sw_vers`: macOS 15.6.1 (24G90). `sysctl`: `kern.maxproc` 4000, `kern.maxprocperuid` 2666, `kern.bootsessionuuid` có |
| Python | 3.12.15 (uv): `select.kqueue` có; `KQ_NOTE_EXIT/FORK/EXEC/TRACK` có; KHÔNG có hằng `EV_RECEIPT`, `NOTE_EXITSTATUS` (dùng số 0x40, 0x04000000 từ `<sys/event.h>`); `os.waitid` KHÔNG có; `os.waitpid(pid, WNOHANG\|WNOWAIT)` → `EINVAL` |
| Bố cục `struct kinfo_proc` | chương trình C 10 dòng in `offsetof` trên `MacOSX.sdk`: sizeof 648; `p_starttime` @0 (`tv_sec` 8 byte, `tv_usec` @8, 4 byte); `p_stat` @36; `p_pid` @40; `e_pcred.p_ruid` @392; `e_ucred.cr_uid` @420; `e_ppid` @560; `e_pgid` @564; `SZOMB` = 5 |
| `sysctl(KERN_PROC_ALL)` qua ctypes | 795–799 tiến trình mọi user, 0,6–1,2 ms một lần; so với `ps -A -o pid,ppid,pgid,uid,ruid` cùng lúc: 793/795 dòng trùng. `KERN_PROC_PID` 17–20 µs; pid không tồn tại → độ dài 0 |
| Xác và mồ côi (con của Em) | con thoát chưa gặt: vẫn trong bảng, `p_stat` = 5, giữ `pgid`; gặt xong: biến mất. Cháu mồ côi: `ppid` → 1, `pgid` và `sinh` không đổi |
| kqueue `EVFILT_PROC` (con của Em) | `NOTE_EXIT\|NOTE_EXITSTATUS`: sự kiện mang mã chờ, xác còn tới khi `poll()`; đăng ký trên xác → `EV_ERROR` data `ESRCH`; `NOTE_TRACK` → `ENOTSUP`; `NOTE_FORK` không cho pid con |
| `PROC_PIDUNIQIDENTIFIERINFO` | KHÔNG có trong SDK công khai → không dùng |
| CPython 3.12 `subprocess` (đọc mã nguồn thư viện chuẩn, 18/10) | `Popen.communicate()` kết thúc bằng `self.wait()` → GẶT gốc; `Popen.__init__` lỗi sau fork không giết con. Handler tín hiệu Python chỉ chạy ở luồng chính |

Định danh một lần sống = **(phiên khởi động, pid, sinh µs)**; bố cục 648 byte tự kiểm ở MỌI lần đọc (dòng của chính tiến trình phải khớp `getppid/getpgrp/geteuid/getuid`; lệch → `OSError` → không chứng minh gì). Lựa chọn nguồn (`ps -o lstart` 1 s, `proc_pidinfo` cần cùng user, API riêng) giữ như bản trước.

### Lựa chọn cho A01/A02 (đã kiểm D53, D45–D52, spec 3 §7)

- **D53:** S6 chỉ cơ chế `user` — mỗi khe MỘT tài khoản macOS riêng; nhánh `sandbox` giữ mã, cổng đóng. **D45:** không root lúc chạy, cách ly cưỡng chế; "quét/dọn đơn thuần không đủ" — áp cho CÁCH LY (nơi ghi, nguồn thực thi). **Spec 3 §7.3 mục 2:** khe tách khe bằng quyền thật của OS. **Spec 3 §7.2:** khởi động `tram tho chay` thì CLI mồ côi bị dừng và có `chay.xong {mo-coi}`.
- **Chọn (A01):** an toàn không đặt ở bước kiểm (kiểm → gửi không nguyên tử: thành viên cuối chết, số được cấp lại, kể cả giữa hai kênh của `gop_kill`) mà ở **chính lệnh gửi**: nhóm ngoài gốc chỉ được gửi qua `kill_nhom` của principal `user` — chạy dưới UID dành riêng, nhân macOS kiểm quyền gửi trong chính lời gọi `kill(2)` (user thường chỉ gửi được tới tiến trình có UID thực/UID lưu = UID mình). Số nhóm có bị cấp lại cho tài khoản khác thì lệnh gửi không trúng; trúng tiến trình khác CÙNG UID thì đó vẫn là việc của khe/`tram-kiem`. Nhóm gốc chưa gặt: số không thể cấp lại → mọi kênh. Kênh cục bộ (quản lý/trạm chạy nhiều việc khác) và `sandbox` (user dùng chung) không bao giờ gửi nhóm ngoài gốc — nhóm đó còn sống thì thu hồi KHÔNG xác nhận. `tho.yaml` cấm hai khe trùng `user:<tên>` (UID "dành riêng" phải đúng là riêng). `van_o_nhom` vẫn chạy ngay trước khi gửi nhưng chỉ để bớt tín hiệu thừa — KHÔNG còn là cơ sở an toàn.
- **Chọn (A02):** `Nhom` (polling) không thể thấy tiến trình fork + setsid + cha thoát giữa hai ảnh; `thu_hoi` True vì thế chỉ nghĩa "cây quan sát được đã hết". Chứng cứ dừng của khe thợ đặt ở tầng khe: **dọn theo UID khe** (như `tram-kiem` đã có `cong_that.thu_hoi_theo_uid`): `xac_minh_uid` → `kill -KILL -1` DƯỚI chính principal → bảng của nhân không còn tiến trình có uid/uid thực của khe. Chạy lúc khởi động khe (thay việc giết theo số pgid trong bản ghi — bs-863.15), đầu mỗi phiếu (trước khi dựng worktree/trao quyền), sau mỗi lần chạy CLI. Không chứng minh được → `LoiThuHoi` → khe dừng, giữ bản ghi + phiếu (INV-003, INV-004: không nhận việc mới khi chứng cứ dừng chưa đủ). **Principal `sandbox:`** (dùng chung tài khoản) KHÔNG có cách dọn theo phạm vi an toàn → `don_uid` từ chối ngay → khe dừng (đúng D53: cổng sandbox đóng). Không áp `kill -1` lên tài khoản dùng chung.
- **Không mâu thuẫn D45:** dọn theo UID là bằng chứng DỪNG (không còn tiến trình của khe giữa hai lượt), không thay cưỡng chế nơi ghi/nguồn thực thi của S6.
- **Hệ quả vận hành** (ghi sổ tay G7): mọi tiến trình dưới tài khoản khe đều bị giết ở các mốc trên — Đại ca đăng nhập tay dưới tài khoản khe hay chạy `tram tho kiem` chỉ khi đã dừng `tram tho chay` (câu hỏi 2). Khe chưa khai principal hợp lệ thì dừng ngay lúc khởi động (trước đây: chạy nhịp, phiếu lỗi).

### Mô hình sở hữu

1. **Sở hữu từ PID (A03, R2-01, R2-02) — hợp đồng `tram/kiem/so_huu.py`.** `khoi_chay(argv, *, kill, chu, …)` là nơi DUY NHẤT spawn, `chu` bắt buộc. Popen + dựng `Nhom` + `chu.append` trong `ngat.hoan()` (bộ ghi SIGINT/SIGTERM ở luồng chính; ra khỏi: khôi phục mọi handler rồi phát lại). `khoi_chay` KHÔNG tự giết/gặt: lỗi theo dõi gốc → `Goc.hong` (không gặt, không bao giờ xác nhận) → `LoiThuHoi` khi `Nhom` đã ở `chu`; ngắt phát lại khi `Nhom` đã ở `chu`. Người gọi: một khối sở hữu (`so_huu(...)` hoặc `chu` + `thu_hoi_con_lai` trong `finally`) bao spawn và mọi bước sau. `LoiThuHoi` = không xác nhận, KHÔNG phải "không để lại con": cổng/khe đóng, tầng trên dọn theo UID (Task 5 cho khe; `cong_that.thu_hoi_theo_uid` cho `tram-kiem`).
2. **Gốc là con, chưa gặt.** `cho()` biết gốc thoát qua kqueue mà không gặt; chỉ `thu_hoi` gặt sau khi xác nhận. `chay_gioi_han` đọc/ghi ống bằng `selectors` (thay `communicate`, vốn gặt gốc) — hợp đồng gặt thống nhất cho mọi người gọi, kể cả B-T6/T7.
3. **Thành viên khác:** con theo `ppid` trong cùng ảnh; khoá (pid, sinh) đã thấy ở ảnh trước; cùng nhóm với thành viên đã chứng minh **trong chính ảnh đó**. Số nhóm của ảnh cũ không còn là bằng chứng.
4. **Mơ hồ:** mang số nhóm cây từng có mà không chứng minh được → không gửi, `thu_hoi` False.
5. **Phạm vi gửi (A01):** mục "Lựa chọn" ở trên.
6. **Dọn theo UID khe (A02):** mục "Lựa chọn" ở trên. Với `tram-kiem`, lưới UID là `cong_that.thu_hoi_theo_uid` (không đổi).
7. **Bản ghi `dang-chay.pid`** giữ định dạng cũ `{pid, pgid, giao_id, luot, lan}` — chỉ còn để gửi `chay.xong {mo-coi}`; không bao giờ gửi tín hiệu theo số trong file. Bản ghi cũ/hỏng không cản việc dọn; dọn không chứng minh được → giữ bản ghi.

### Ma trận test (assert trên TOÀN BỘ tín hiệu đã gửi/đã trúng)

| Ca | Test |
|---|---|
| Cùng UID, birth khác | `test_cung_so_cung_uid_sinh_khac_khong_nhan`, `test_nhom_tai_su_dung_khong_duoc_kill` (nguyên văn plan V2) |
| PGID đổi / neo đổi giữa ảnh và lúc gửi | `test_mo_coi_da_thay_doi_nhom…`, `test_neo_doi_giua_anh_va_luc_gui_thi_khong_gui` |
| **Nhóm cấp lại SAU lần kiểm cuối** (A01) | `test_nhom_cap_lai_sau_lan_kiem_cuoi_khong_trung_ai_ngoai_uid_khe` |
| **Nhóm cấp lại GIỮA hai kênh `gop_kill`** (A01) | `test_nhom_cap_lai_giua_hai_kenh_gui_khong_trung_ai_ngoai_uid_khe` |
| **Kênh cục bộ / sandbox** (A01) | `test_khong_co_kenh_theo_uid_rieng…[cuc-bo, sandbox]`, `test_kenh_cuc_bo_khong_gui_nhom_ngoai_goc…` (thật) |
| ps/sysctl lỗi | `test_khong_chup_duoc_luc_gui_chi_nhom_goc_chua_gat`, `test_vong_doi_ps.py`, `test_tu_kiem_bo_cuc_hong_thi_nem`, `test_khong_doc_duoc_bang_thi_loi_thu_hoi` (don_uid) |
| Root đã gặt / chưa gặt / gặt sớm bởi người khác (A03) | `test_goc_da_gat_*`, `test_cho_tra_ma_nhung_giu_xac…`, `test_goc_thoat_nhanh_chau_o_nhom_goc…` (chay_gioi_han thật), `test_do_danh_tinh_khong_tu_gat_goc` |
| Lỗi/ngắt lúc spawn (A03, R2-01, R2-02) | `test_dang_ky_loi_khac_esrch_khong_gat_goc_va_khong_tin_hieu_nao_trung_nhom_thay_the` (nhân giả, số cấp lại), `test_dang_ky_loi_voi_con_that…`, `test_ngat_luc_spawn_duoc_hoan…`, `test_tin_hieu_toi_dung_luc_khoi_phuc_handler…`, `test_moi_nguoi_goi_so_huu_tu_pid…[5 người gọi]`, `test_kill_bi_tu_choi_hay_goc_treo…`, `test_han_tong_*`, `test_ngat_hay_loi_giua_chung…` |
| Lỗi ống/selector/đọc (R2-04) | `test_dong_ong_loi_khong_chan_ong_sau…[stdin/stdout/stderr × sach]`, `test_doc_hay_bo_chon_loi…[doc, chon, dong_bo_chon]` |
| Nhóm của manager, nhóm 0/1 | `test_khong_bao_gio_gui_nhom_0_1_va_nhom_cua_quan_ly` |
| Fork/setsid trước ảnh đầu (A02) | `test_fork_setsid_truoc_anh_dau_nhom_khong_thay_duoc_khong_gui` (giới hạn của MỘT Nhom) + `test_tan_du_*` (tầng khe: không sang lần sau) |
| Legacy pid receipt | `test_don_theo_uid_roi_moi_xoa_ban_ghi` (4 dạng), `test_khoi_dong_khe_khong_chung_minh_duoc…` |

## Thiết kế V2-6b — thăm dò âm và đăng nhập đúng principal

- **Một đường chạy:** mọi thăm dò và lệnh trạng thái đăng nhập đi qua `chay_gioi_han` (hạn tuyệt đối, thu hồi bằng `kill` CỦA PRINCIPAL, không gặt sớm). `kill` là tham số bắt buộc của `chay_tham_do`.
- **UID trước:** `tram tho kiem` (`cach_ly`, `dang_nhap`), `tram chu kiem-cach-ly`, khe Codex trong `kiem_3b` chạy `xac_minh_uid` TRƯỚC; chưa chứng minh/chưa thu hồi được → ĐỎ, không spawn thăm dò/đăng nhập.
- **Chấm (A04, `cham_tham_do`):** dương chạy trước; một dương hỏng → mọi âm "không kết luận". Âm chỉ "đạt" khi có dấu hiệu TỪ CHỐI QUYỀN của đúng loại (bảng trong docstring của `cham_tham_do`): `doc/ghi/sua/nc/tram` cần stderr "Permission denied"/"Operation not permitted"; `keychain` cần mã 44 + "could not be found" (keychain của principal không thấy mục) VÀ đối chứng mục có trong keychain của quản lý (không `-w`); `http` cần curl mã 0 + HTTP 401/403 (đúng 3 chữ số). Lỗi hạ tầng, 126/127, chết vì tín hiệu, mục tiêu không có (đối chứng dưới quản lý), mã chưa phân loại → "không kết luận". Đọc thư mục bằng `ls` (cat thư mục luôn lỗi — trước đây bị tính là "bị chặn"). Kết quả chỉ mang lý do cố định (+ mã HTTP 3 chữ số đã kiểm), không chép stdout/stderr.
- **Tàn dư sau thăm dò (A02 cho `tram tho kiem`):** thăm dò xong, bảng của nhân còn tiến trình của UID principal → mục cách ly ĐỎ. Chỉ quan sát, không giết (có thể `tram tho chay` đang chạy).
- **Env:** dựng mới — thăm dò `PATH`/`LANG`; đăng nhập Codex `PATH`/`LANG`/`CODEX_HOME`; Claude `CLAUDE_CONFIG_DIR`/`PATH`/`LANG`. Không `HOME`, token hay env của quản lý.
- **`LoiThuHoi` (A05):** `dang_nhap_codex` để `LoiThuHoi` nổi lên; `bo_sung_3b` ghi ĐỎ cho cả đăng nhập lẫn hạn mức và KHÔNG gọi app-server dưới principal đó.
- **`tram chu kiem-cach-ly`:** principal khe qua `Principal("user", …).boc` = `sudo -n -H -u …` (không hỏi mật khẩu, không treo). Câu hỏi 1.
- **`do_cli`** chỉ còn đọc `--version`; đăng nhập dò dưới principal (`tram tho kiem`).

## Thiết kế V2-6c — `TheoDoi` dừng trong MỘT hạn

- `mot_luot` giữ khoá ⇒ luồng nền và lần đọc cuối không chạy cùng lúc. Luồng nền nhận `ngung`: kiểm giữa các dòng (dòng chưa xử lý giữ vị trí) và trong `day_va_cong_bo(dung=…)`.
- `ket_thuc(han)` (A06): `het = now + han` (mặc định `HAN_DUNG` 150 s); dừng luồng nền tới `het` (chưa dừng → `LoiThuHoi`), rồi đọc lần cuối trong luồng riêng (`trong_han.chay_trong_han`) cũng tới `het`; quá hạn → đặt `_ngung_cuoi` (lần đọc cuối thôi ở ranh giới dòng/đẩy mốc kế tiếp) và `LoiThuHoi` — người gọi không bao giờ bị giữ quá `het` (cộng vài ms). Dòng chưa xử lý giữ vị trí; khởi động lại gửi lại với request_id tất định.
- Hẹn `xong` (A06): tạo/hủy dưới khoá riêng; `_dung_den` đặt cờ `_het_hen` + hủy hẹn đang chờ TRƯỚC khi dừng luồng; sau đó `_dat_hen` không tạo hẹn nào nữa (kể cả lần đọc cuối gặp dòng `xong`).
- `_mot_vong`: CLI ném ⇒ `dung_lai()` (không đọc cuối) rồi ném lại; luồng chưa dừng ⇒ `LoiThuHoi` thắng lỗi gốc.
- Giới hạn còn lại: một thao tác I/O đang dở trong luồng đọc cuối bị bỏ lại (daemon) khi quá hạn — nó có thể hoàn tất SAU `LoiThuHoi` và ghi vị trí; khe đã dừng, gửi lại sau khởi động là idempotent (request_id tất định).

## File Structure

```
tram/kiem/
  bang_tien_trinh.py  (mới, T1; T3 van_o_nhom)  sysctl KERN_PROC: chup_nhan, mot_nhan, phien_khoi_dong
  cay_tien_trinh.py   (sửa, T1, T3)  TienTrinh.sinh/khoa; cay theo định danh; mo_ho
  giu_xac.py          (mới, T2)  Goc: biết thoát không gặt (kqueue), gặt khi thu hồi xong
  ngat.py             (mới, T2)  hoan() — MỘT cơ chế hoãn ngắt (B-T6 thêm NgatTerm, term_thanh_ngat)
  so_huu.py           (mới, T2)  HỢP ĐỒNG sở hữu; thu_hoi_con_lai, so_huu(...)
  gui_tin.py          (mới, T2; T3 GopKill/kill_uid)  kill_cuc_bo, phạm vi gửi theo UID
  vong_doi.py         (sửa, T2, T3)  Nhom giữ xác + ket_thu_hoi, khoi_chay(chu) bắt buộc, gửi theo phạm vi, mơ hồ → False
  chay_gioi_han.py    (sửa T2; thay T4)  thân hàm CUỐI: hạn trước spawn, _ong (selector), _don (đóng từng ống → luôn thu hồi)
  han_tong.py         (sửa, T2, T3, T4)  thân hàm CUỐI: dấu + spawn trong try/hoan, thu hồi chu trong hoan; gop_kill
  danh_tinh.py        (sửa, T2, T3, T4)  khối sở hữu; ảnh qua sysctl; không poll gặt gốc
  chay_lenh.py        (sửa, T2)  khối sở hữu
tram/chay_cli/
  claude.py, codex/chay.py, codex/app_server.py  (sửa, T2)  khối sở hữu (spawn → thu hồi), hành vi thường giữ nguyên
tram/tho/
  cau_hinh.py         (sửa, T3)  cấm hai khe trùng user:<tên>
  don_uid.py          (mới, T5)  dọn theo UID khe: kill -1 dưới principal + chứng minh không còn ai
  ngu_canh.py         (sửa, T5)  don_uid (tiêm), don_khe(k)
  mo_coi.py           (sửa, T5)  don_mo_coi(p, *, don) — không gửi theo số
  mo_coi_khe.py       (sửa, T5)  (phiếu, dừng khe)
  vong_khe.py         (sửa, T5)  khoi_dong nhận cờ dừng khe
  phieu_chay.py       (sửa, T5, T8)  dọn UID đầu phiếu; CLI lỗi → dung_lai
  mot_lan.py          (sửa, T5)  dọn UID sau mỗi lần chạy CLI
  cham_tham_do.py     (mới, T6)  cham + đối chứng (co_muc_keychain, mo_cong)
  kiem_am.py          (sửa, T6)  ThamDo(kieu, doi_chung); chay_tham_do qua P1
  kiem_cong.py        (sửa, T6, T7)  UID trước; tàn dư sau thăm dò; dang_nhap qua P1
  do_may.py           (sửa, T7)  do_cli chỉ phiên bản; dang_nhap_codex (LoiThuHoi nổi lên)
  kiem_3b.py          (sửa, T7)  một lần xác minh UID; LoiThuHoi đăng nhập → không đọc hạn mức
  day.py              (sửa, T8)  day_va_cong_bo(dung=…)
  trong_han.py        (mới, T8)  chay_trong_han — việc không hủy được, hạn tuyệt đối
  theo_doi.py         (sửa, T8)  khoá, hủy giữa dòng, MỘT hạn cho dừng + đọc cuối, hẹn có khoá
tram/chu/
  kiem_cach_ly.py     (sửa, T6)  sudo -n qua Principal, kill, UID trước
tests/  (mới) test_bang_tien_trinh (T1) · test_giu_xac, test_so_huu, test_so_huu_ngat, test_so_huu_nguoi_goi (T2) ·
        test_vong_doi_tai_su_dung, test_pham_vi_gui (T3) · test_so_huu_bo_chay, test_so_huu_ong, test_so_huu_han_tong (T4) · test_don_uid, test_mo_coi_uid, test_khe_tan_du (T5) · test_cham_tham_do,
        test_kiem_am_p1, test_tham_do_principal (T6) · test_dang_nhap_principal (T7) · test_theo_doi_dung,
        test_theo_doi_noi (T8); (sửa) test_cay_tien_trinh, test_vong_doi, test_vong_doi_ps, test_han_tong,
        test_chay_gioi_han (T3) · tho_chay_gia, test_phieu_chay_thu_hoi, test_so_khe_hop_thu (T5) · test_kiem_am,
        test_kiem_cong, test_chu_tho (T6) · test_do_may, test_kiem_3b, test_kiem_cong, test_han_muc_principal (T7)
```

Trong các bước dưới, **`PT`** là viết tắt của lệnh test qua PATH chặn host (`AGENT_RULES.md` §13), chạy từ gốc worktree:
`PATH="$C/bin:$PATH" PYTHONPATH="$C/plugin" UV_OFFLINE=1 uv run pytest -p chan_host -q` (`C` = thư mục bin giả + plugin
`chan_host` của người điều phối). Sau mỗi lần chạy, đếm dòng mới của nhật ký chặn thuộc worktree này — phải bằng 0 (mọi lần chạy khi sửa plan: 32 → 32 dòng, 0 dòng mới).

## Task 1 — Bảng tiến trình của nhân có định danh sinh (V2-0)

**Files:** tạo `tram/kiem/bang_tien_trinh.py`, `tests/test_bang_tien_trinh.py`; sửa `tram/kiem/cay_tien_trinh.py` (thêm trường `sinh`, thuộc tính `khoa`).

**Interfaces:**
- `TienTrinh(pid, ppid, pgid, uid, ruid, sinh=None)`; `TienTrinh.khoa -> (pid, sinh) | None` — dựng 5 đối số như cũ vẫn chạy (`sinh=None` = nguồn không có định danh, ví dụ `ps`).
- `bang_tien_trinh.doc_kinfo(raw: bytes) -> list[TienTrinh]` (thuần, test được bằng byte dựng tay); `chup_nhan(*, doc=_sysctl) -> list[TienTrinh]`; `mot_nhan(pid, *, doc=_sysctl) -> TienTrinh | None`; `phien_khoi_dong() -> str`. Lỗi đọc/bố cục lệch → `OSError`; `pid <= 0` → `ValueError`.
- Task này không đổi so với bản trước review (review vòng 1 không nêu phát hiện ở đây).

- [ ] **Step 1: Viết test**

Tạo mới `tests/test_bang_tien_trinh.py` (nguyên văn):

```python
"""Bảng tiến trình của nhân qua sysctl (V2-0, dot7-C01): định danh sinh (pid, sinh µs), tự kiểm bố cục. Ca giả dùng byte
dựng tay; ca thật CHỈ ĐỌC bảng (như `ps`) và chỉ tạo/giết `python -c` của chính user đang test."""
import os
import struct
import subprocess
import sys

import pytest

from tram.kiem.bang_tien_trinh import CO, chup_nhan, doc_kinfo, mot_nhan, phien_khoi_dong
from tram.kiem.cay_tien_trinh import TienTrinh


def dong(pid, ppid, pgid, uid, ruid, giay=1_700_000_000, micro=5) -> bytes:
    b = bytearray(CO)
    struct.pack_into("<qi", b, 0, giay, micro)
    struct.pack_into("<i", b, 40, pid)
    struct.pack_into("<ii", b, 560, ppid, pgid)
    struct.pack_into("<I", b, 392, ruid)
    struct.pack_into("<I", b, 420, uid)
    return bytes(b)


TOI = dong(os.getpid(), os.getppid(), os.getpgrp(), os.geteuid(), os.getuid())


def test_doc_kinfo_lay_dung_cot_va_sinh_micro_giay():
    ds = doc_kinfo(dong(5000, 4242, 5000, 502, 501, giay=10, micro=7) + TOI)
    assert ds[0] == TienTrinh(5000, 4242, 5000, 502, 501, 10_000_007) and ds[0].khoa == (5000, 10_000_007)
    with pytest.raises(OSError):
        doc_kinfo(TOI + b"\0")


@pytest.mark.parametrize("bang", [dong(5000, 1, 5000, 0, 0),                      # thiếu dòng của chính mình
                                  dong(os.getpid(), 1, 1, 0, 0),                  # bố cục lệch: cột không khớp
                                  TOI + TOI])                                     # hai dòng cùng pid
def test_tu_kiem_bo_cuc_hong_thi_nem(bang):
    with pytest.raises(OSError):
        chup_nhan(doc=lambda mib: bang)
    with pytest.raises(OSError):
        mot_nhan(5000, doc=lambda mib: bang if mib[-1] == os.getpid() else dong(5000, 1, 5000, 0, 0))


def test_mot_nhan_khong_con_thi_none_pid_khong_hop_le_thi_nem():
    assert mot_nhan(5000, doc=lambda mib: TOI if mib[-1] == os.getpid() else b"") is None
    with pytest.raises(ValueError):
        mot_nhan(0)


def test_bang_that_thay_con_cua_minh_voi_sinh_on_dinh():
    p = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"], start_new_session=True)
    try:
        con = mot_nhan(p.pid)
        assert con is not None and (con.ppid, con.pgid, con.uid) == (os.getpid(), p.pid, os.geteuid())
        assert next(t for t in chup_nhan() if t.pid == p.pid).sinh == con.sinh
    finally:
        p.kill()
        p.wait(5)
    assert mot_nhan(p.pid) is None or mot_nhan(p.pid).sinh != con.sinh


def test_phien_khoi_dong_on_dinh_va_khong_rong():
    assert phien_khoi_dong() == phien_khoi_dong() and len(phien_khoi_dong()) >= 8
```

- [ ] **Step 2: Chạy, thấy đỏ** — `PT tests/test_bang_tien_trinh.py` (kết quả thật 18/10, mã ở `7921f26`):

```
E   ModuleNotFoundError: No module named 'tram.kiem.bang_tien_trinh'
ERROR tests/test_bang_tien_trinh.py
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
1 error in 0.05s
```

- [ ] **Step 3: Mã**

Tạo mới `tram/kiem/bang_tien_trinh.py` (nguyên văn):

```python
"""Bảng tiến trình của NHÂN qua `sysctl(KERN_PROC)` (V2-0, dot7-C01) — nguồn ảnh chụp có ĐỊNH DANH SINH cho P1.
`kinfo_proc.kp_proc.p_starttime` (giây + micro giây) do nhân ghi lúc fork; số pid chỉ được cấp lại sau khi tiến trình
cũ đã chết VÀ đã được gặt, nên khoá (pid, sinh) phân biệt hai lần sống của cùng một số. CHỈ so BẰNG: `p_starttime` là
giờ tường (đổi giờ hệ thống làm lệch thứ tự) — không dùng để so trước/sau. Không tiến trình con, không phân tích chữ;
người dùng thường đọc được bảng của mọi tiến trình (`ps` dùng cùng nguồn), không gửi tín hiệu.
Bố cục `struct kinfo_proc` lấy từ SDK macOS 15.6.1 arm64 (offsetof; sizeof 648) và TỰ KIỂM ở mỗi lần đọc: dòng của chính
tiến trình này phải khớp `os.getppid/getpgrp/geteuid/getuid`. Lệch, sysctl lỗi → `OSError` — người gọi coi như KHÔNG
chụp được, không chứng minh gì."""
import ctypes
import ctypes.util
import errno
import os
import struct
from collections.abc import Callable

from tram.kiem.cay_tien_trinh import TienTrinh

CO = 648                                        # sizeof(struct kinfo_proc)
TAT_CA, MOT_PID = (1, 14, 0), (1, 14, 1)        # CTL_KERN, KERN_PROC, KERN_PROC_ALL | KERN_PROC_PID
_libc = ctypes.CDLL(ctypes.util.find_library("c"), use_errno=True)


def doc_kinfo(raw: bytes) -> list[TienTrinh]:
    if len(raw) % CO:
        raise OSError("bảng kinfo_proc sai kích thước")
    ds = []
    for i in range(0, len(raw), CO):
        giay, micro = struct.unpack_from("<qi", raw, i)                  # p_starttime: timeval ở đầu kp_proc
        (pid,) = struct.unpack_from("<i", raw, i + 40)                   # kp_proc.p_pid
        ppid, pgid = struct.unpack_from("<ii", raw, i + 560)             # kp_eproc.e_ppid, e_pgid
        (ruid,) = struct.unpack_from("<I", raw, i + 392)                 # kp_eproc.e_pcred.p_ruid
        (uid,) = struct.unpack_from("<I", raw, i + 420)                  # kp_eproc.e_ucred.cr_uid
        ds.append(TienTrinh(pid, ppid, pgid, uid, ruid, giay * 1_000_000 + micro))
    return ds


def _sysctl(mib: tuple[int, ...]) -> bytes:
    m = (ctypes.c_int * len(mib))(*mib)
    for _ in range(5):
        n = ctypes.c_size_t(0)
        if _libc.sysctl(m, len(mib), None, ctypes.byref(n), None, 0) != 0:
            raise OSError(ctypes.get_errno(), "sysctl: không đọc được kích thước bảng")
        n.value += 32 * CO                                               # bảng có thể lớn thêm giữa hai lần gọi
        buf = ctypes.create_string_buffer(n.value)
        if _libc.sysctl(m, len(mib), buf, ctypes.byref(n), None, 0) == 0:
            return buf.raw[: n.value]
        if ctypes.get_errno() != errno.ENOMEM:
            raise OSError(ctypes.get_errno(), "sysctl: không đọc được bảng tiến trình")
    raise OSError(errno.ENOMEM, "sysctl: bảng tiến trình đổi liên tục")


def _tu_kiem(ds: list[TienTrinh]) -> None:
    toi = [t for t in ds if t.pid == os.getpid()]
    if len(toi) != 1 or (toi[0].ppid, toi[0].pgid, toi[0].uid, toi[0].ruid) != (
            os.getppid(), os.getpgrp(), os.geteuid(), os.getuid()):
        raise OSError("bố cục kinfo_proc không khớp tiến trình này — không tin ảnh chụp")


def chup_nhan(*, doc: Callable[[tuple[int, ...]], bytes] = _sysctl) -> list[TienTrinh]:
    """Toàn bộ bảng tiến trình trong MỘT lần gọi sysctl, đã tự kiểm bố cục."""
    ds = doc_kinfo(doc(TAT_CA))
    _tu_kiem(ds)
    return ds


def mot_nhan(pid: int, *, doc: Callable[[tuple[int, ...]], bytes] = _sysctl) -> TienTrinh | None:
    """Dòng của MỘT pid ngay lúc gọi (đọc pid đích TRƯỚC, tự kiểm sau); None khi không còn tiến trình mang số đó."""
    if pid <= 0:
        raise ValueError("pid phải dương")
    ds = doc_kinfo(doc((*MOT_PID, pid)))
    _tu_kiem(doc_kinfo(doc((*MOT_PID, os.getpid()))))
    if len(ds) > 1 or (ds and ds[0].pid != pid):
        raise OSError("sysctl trả dòng lạ cho một pid")
    return ds[0] if ds else None


def phien_khoi_dong() -> str:
    """`kern.bootsessionuuid` — đổi sau mỗi lần khởi động máy; pid/sinh của phiên khác không còn tiến trình nào."""
    n = ctypes.c_size_t(64)
    buf = ctypes.create_string_buffer(n.value)
    if _libc.sysctlbyname(b"kern.bootsessionuuid", buf, ctypes.byref(n), None, 0) != 0 or not buf.value:
        raise OSError(ctypes.get_errno(), "sysctl: không đọc được phiên khởi động")
    return buf.value.decode("ascii")
```

Bản vá `tram/kiem/cay_tien_trinh.py`:

```diff
--- a/tram/kiem/cay_tien_trinh.py
+++ b/tram/kiem/cay_tien_trinh.py
@@ -20,6 +20,12 @@
     pgid: int
     uid: int
     ruid: int
+    sinh: int | None = None         # thời điểm sinh (µs) nhân ghi lúc fork — None: nguồn không có định danh sinh (`ps`)
+
+    @property
+    def khoa(self) -> tuple[int, int] | None:
+        """Định danh MỘT lần sống: (pid, sinh). None → không chứng minh được là cùng tiến trình đã thấy."""
+        return None if self.sinh is None else (self.pid, self.sinh)
 
 
 def doc_ps(van_ban: bytes) -> list[TienTrinh]:
```

- [ ] **Step 4: Chạy, thấy xanh** — `PT tests/test_bang_tien_trinh.py tests/test_cay_tien_trinh.py` → `17 passed`.

- [ ] **Step 5: Cả bộ** — `PT` → 2809 + 7 = `2816` (thu thập; đo cả bộ gộp với Task 2: `2833 passed`), nhật ký chặn 0 dòng mới.

- [ ] **Step 6: Commit** — `git add tram/kiem/bang_tien_trinh.py tram/kiem/cay_tien_trinh.py tests/test_bang_tien_trinh.py && git commit -m "fix(kiem): bảng tiến trình của nhân có định danh sinh (V2-0, dot7-C01)"`

## Task 2 — Biết gốc thoát mà không gặt; MỘT hợp đồng sở hữu từ lúc có PID cho mọi người gọi (V2-0; review vòng 1 A03, vòng 2 R2-01, R2-02)

**Files:** tạo `tram/kiem/giu_xac.py`, `tram/kiem/gui_tin.py`, `tram/kiem/ngat.py`, `tram/kiem/so_huu.py`, `tests/test_giu_xac.py`, `tests/test_so_huu.py`, `tests/test_so_huu_ngat.py`, `tests/test_so_huu_nguoi_goi.py`; sửa `tram/kiem/vong_doi.py`, `tram/kiem/danh_tinh.py`, `tram/kiem/chay_lenh.py`, `tram/chay_cli/claude.py`, `tram/chay_cli/codex/chay.py`, `tram/chay_cli/codex/app_server.py`, `tram/kiem/chay_gioi_han.py` và `tram/kiem/han_tong.py` (Task này chỉ truyền `chu` — Task 4 viết vùng sở hữu đầy đủ của hai bộ chạy), `tests/test_vong_doi.py`.

**Interfaces (HỢP ĐỒNG SỞ HỮU — thay "H-A03" mà plan B dựa vào; nguyên văn ở docstring `tram/kiem/so_huu.py`):**
- `giu_xac.Goc(p)`: `chua_gat()`, `thoat(giay=0.0)` (chờ tối đa `giay`, KHÔNG gặt), `ma()`, `gat()`, thuộc tính `hong`. Popen thật → kqueue `NOTE_EXIT|NOTE_EXITSTATUS`; đăng ký trả ESRCH (gốc đã là xác) → gặt ngay lấy mã, TRƯỚC mọi lần gửi; lỗi KHÁC (receipt lỗi, không tạo được kqueue) → **không gặt**, `hong = True`: `thoat()` luôn False, nên `thu_hoi` không bao giờ True; gốc vẫn là con chưa gặt nên gửi nhóm gốc vẫn an toàn. `giu_xac._kqueue` là điểm tiêm lỗi của test.
- `ngat.hoan()` — MỘT cơ chế hoãn ngắt cho cả A lẫn B (B-T6 thêm `NgatTerm`, `term_thanh_ngat` vào cùng file): khối ngoài cùng ở luồng chính cài bộ GHI cho SIGINT/SIGTERM; ra khỏi khối thì khôi phục MỌI handler cũ — kể cả khi tín hiệu tới giữa lúc khôi phục — rồi PHÁT LẠI theo thứ tự nhận (`raise_signal`), tín hiệu đầu ném thì dừng. Không hoãn ở luồng phụ. `ngat._dat` là điểm tiêm của test.
- `vong_doi.khoi_chay(argv, *, kill, chu: list, popen=…, chup=…, **kw) -> Nhom`: `chu` **BẮT BUỘC** (không phải list → `TypeError` trước khi spawn). Popen + dựng `Nhom` + `chu.append(n)` trong `hoan()`. Ném `OSError` ⇒ `chu` không đổi (Popen chưa tạo được tiến trình). Mọi lối ra khác sau Popen — trả `Nhom`; `LoiThuHoi` khi `Goc.hong`; ngắt phát lại khi rời `hoan()` — đều khi `Nhom` ĐÃ ở `chu`. `khoi_chay` không tự giết/gặt gì: không còn `bo_khan`.
- `Nhom.ket_thu_hoi: bool | None` — None tới khi `thu_hoi` chạy xong lần đầu, rồi là kết quả của nó.
- `so_huu.thu_hoi_con_lai(chu, **kw) -> bool` (thu hồi mọi `Nhom` có `ket_thu_hoi` None, trong `hoan()`; rỗng → True) và `so_huu.so_huu(loi, **kw)` (context manager → `chu`; ra khỏi khối: `thu_hoi_con_lai`; chưa xác nhận → `LoiThuHoi(loi)` THAY lỗi thường, `from None`; KeyboardInterrupt vẫn là KeyboardInterrupt).
- **Mọi người gọi `khoi_chay` trên HEAD** đặt spawn trong khối sở hữu: `danh_tinh.quan_sat`, `chay_lenh.chay_mot_lenh`, `ChayClaude.chay`, `ChayCodex.chay`, `hoi_app_server` dùng `so_huu(...)`; `chay_gioi_han`, `chay_han_tong` (bộ chạy một chủ) dùng `chu` + `thu_hoi_con_lai` ở Task 4. Hành vi thường giữ nguyên (cùng thông báo lỗi, `ChayClaude`/`ChayCodex` vẫn ném `LoiThuHoi` khi không dọn được nhóm CLI, `hoi_app_server` vẫn thu hồi `thu_hoi(1, 3, 2)`); `hoi_app_server` nay tính hạn TRƯỚC spawn.
- `gui_tin`: `Kill`, `LOI_GUI`, `kill_cuc_bo` (chuyển từ `vong_doi`; `vong_doi` vẫn xuất lại tên cũ).

**Vì sao đổi so với bản vòng 2 (review R2-01, R2-02):** bản trước, nhánh lỗi của `Goc` GẶT gốc rồi mới ném, và `bo_khan` gửi SIGKILL tới số pid đó qua cả kênh cục bộ — số đã có thể được cấp lại cho việc khác của tài khoản quản lý (tái hiện thật ở Step 2: tín hiệu trúng tiến trình 7000 của "nhân giả"). Bản trước cũng ném `LoiThuHoi` sau `bo_khan` dù không chứng minh được gì (kill bị từ chối, `wait(2)` quá hạn, hậu duệ tách phiên) và để `chu` tuỳ chọn — `quan_sat`, `hoi_app_server`, CLI của phiếu, `nguon_archive` của B không có danh sách nhận `Nhom` trước khi tín hiệu được phát lại. Nay: nhánh lỗi không bao giờ gặt; `khoi_chay` không giết thay ai mà BÀN GIAO cho người gọi; mọi người gọi có khối sở hữu; `LoiThuHoi` được định nghĩa đúng nghĩa "không xác nhận" (con có thể còn sống, `Nhom` còn trong `chu`, cổng/khe đóng, tầng trên dọn theo UID — Task 5 cho khe, `cong_that.thu_hoi_theo_uid` cho `tram-kiem`), không còn hứa "không để lại con".

- [ ] **Step 1: Viết test**

Tạo mới `tests/test_giu_xac.py` (nguyên văn):

```python
"""V2-0: `Nhom` biết gốc đã thoát mà KHÔNG gặt — xác giữ số nhóm gốc tới khi thu hồi xác nhận xong; đăng ký kqueue lỗi
khác ESRCH thì KHÔNG gặt (R2-01). Tiến trình thật chỉ là `python -c` của chính user đang test, nhóm riêng, tự thu hồi
đúng PID mình tạo."""
import errno
import os
import signal
import subprocess
import sys
import time

import pytest

from test_vong_doi import _chau, _song
from tram.kiem import giu_xac
from tram.kiem.bang_tien_trinh import mot_nhan
from tram.kiem.giu_xac import Goc
from tram.kiem.vong_doi import khoi_chay, kill_cuc_bo


def test_cho_tra_ma_nhung_giu_xac_toi_khi_thu_hoi_xong():
    n = khoi_chay([sys.executable, "-c", "import sys; sys.exit(7)"], kill=kill_cuc_bo, chu=[])
    try:
        assert n.cho(10) == 7
        xac = mot_nhan(n.p.pid)
        assert n.p.returncode is None and xac is not None and xac.pgid == n.p.pid       # còn xác, giữ số nhóm
        assert n.thu_hoi(cho_term=0.3, cho_cuoi=1) is True
        assert n.p.returncode == 7 and mot_nhan(n.p.pid) is None
    finally:
        if n.p.returncode is None:
            n.p.kill()
            n.p.wait(5)


def test_mo_coi_o_nhom_goc_sau_khi_goc_thoat_van_bi_thu_hoi(tmp_path):
    n, chau = _chau(tmp_path, moi=False, ngu=0)                 # cha thoát ngay, cháu cùng nhóm gốc bỏ qua SIGTERM
    try:
        assert n.cho(10) == 0 and n.p.returncode is None and mot_nhan(chau).pgid == n.p.pid
        assert n.thu_hoi(cho_term=0.3, cho_cuoi=3) is True and not _song(chau)
    finally:
        if n.p.returncode is None:
            kill_cuc_bo(n.p.pid, signal.SIGKILL)
        if _song(chau):
            os.kill(chau, signal.SIGKILL)


def test_goc_thoat_truoc_khi_dang_ky_van_lay_dung_ma():
    p = subprocess.Popen([sys.executable, "-c", "import sys; sys.exit(3)"], start_new_session=True)
    time.sleep(1.0)                                             # thường đã là xác → kqueue trả ESRCH → gặt ngay
    g = Goc(p)
    assert g.thoat(10) is True and g.ma() == 3
    g.gat()
    assert p.returncode == 3 and mot_nhan(p.pid) is None


class KqLoi:
    def control(self, ds, n, t):
        import select
        return [select.kevent(ds[0].ident, select.KQ_FILTER_PROC, select.KQ_EV_ERROR, 0, errno.EINVAL)]

    def close(self):
        pass


def kq_khong_tao_duoc():
    raise OSError(errno.EMFILE, "quá nhiều fd")


class KqDongLoi(KqLoi):
    def close(self):
        raise OSError(errno.EBADF, "đóng kqueue lỗi")


@pytest.mark.parametrize("kq", [KqLoi, kq_khong_tao_duoc, KqDongLoi])
def test_dang_ky_loi_khac_esrch_tren_xac_thi_khong_gat_va_khong_bao_gio_xac_nhan_thoat(monkeypatch, kq):
    p = subprocess.Popen([sys.executable, "-c", "pass"], start_new_session=True)
    try:
        time.sleep(0.5)                                         # gốc đã là xác
        monkeypatch.setattr(giu_xac, "_kqueue", kq)
        g = Goc(p)
        assert g.hong and p.returncode is None and mot_nhan(p.pid) is not None          # xác còn giữ số nhóm
        assert g.thoat(0.1) is False and g.chua_gat() and g.ma() is None
    finally:
        p.wait(5)


def test_kqueue_loi_khi_doc_van_thu_hoi_va_bao_loi_thu_hoi(monkeypatch):
    from types import SimpleNamespace
    from tram.kiem.so_huu import so_huu
    from tram.kiem.vong_doi import LoiThuHoi

    class KqDocLoi(KqDongLoi):
        def control(self, ds, n, t):
            if ds is not None:
                return [SimpleNamespace(flags=0, data=0)]
            raise OSError(errno.EBADF, "đọc kqueue lỗi")

    monkeypatch.setattr(giu_xac, "_kqueue", KqDocLoi)
    chu = []
    try:
        with pytest.raises(LoiThuHoi, match="chưa xác nhận"):
            with so_huu("chưa xác nhận", cho_term=0.0, cho_cuoi=0.0) as chu:
                n = khoi_chay([sys.executable, "-c", "import time; time.sleep(30)"],
                             kill=kill_cuc_bo, chu=chu)
                assert n.cho(0.0) is None and n.goc.hong
        assert len(chu) == 1 and n.ket_thu_hoi is False and n.p.returncode is None
    finally:
        for n in chu:
            n.p.kill()
            n.p.wait(5)
```

Tạo mới `tests/test_so_huu.py` (nguyên văn):

```python
"""Hợp đồng sở hữu (`tram/kiem/so_huu.py`; review vòng 1 A03, vòng 2 R2-01/R2-02): sau Popen, `Nhom` LUÔN vào danh sách
sở hữu của người gọi trước mọi lối ra; nhánh lỗi đăng ký kqueue KHÔNG gặt gốc (xác giữ số nhóm) nên không tín hiệu nào
trúng nhóm được cấp lại; kill bị từ chối/gốc treo → `LoiThuHoi`, `Nhom` vẫn trong `chu`. Ngắt lúc spawn:
`test_so_huu_ngat.py`; mọi người gọi: `test_so_huu_nguoi_goi.py`. Nhân/Popen GIẢ cho ca tái dùng số — `os.killpg` thật
bị thay bằng bản ghi để không tín hiệu nào rời test; tiến trình thật chỉ là `python -c` của chính user đang test."""
import errno
import os
import select
import signal
import subprocess
import sys

import pytest

from test_vong_doi import PopenGia
from tram.kiem import giu_xac
from tram.kiem.cay_tien_trinh import TienTrinh
from tram.kiem.so_huu import so_huu, thu_hoi_con_lai
from tram.kiem.vong_doi import LoiThuHoi, khoi_chay, kill_cuc_bo

NGU = [sys.executable, "-c", "import time; time.sleep(60)"]
QUAN_LY = os.getuid()
GOC = TienTrinh(4242, 1, 4242, QUAN_LY, QUAN_LY, 42)
LA = TienTrinh(7000, 1, 4242, QUAN_LY, QUAN_LY, 70)      # việc khác của tài khoản quản lý nhận lại số nhóm 4242


class KqLoi:
    """kqueue đăng ký trả receipt lỗi KHÁC ESRCH (vd. EINVAL)."""
    def control(self, ds, n, t):
        return [select.kevent(ds[0].ident, select.KQ_FILTER_PROC, select.KQ_EV_ERROR, 0, errno.EINVAL)]

    def close(self):
        pass


class Nhan:
    """Nhân GIẢ: gửi tới nhóm g trúng mọi tiến trình mang nhóm g lúc gửi."""
    def __init__(self):
        self.bang, self.trung = [GOC], []

    def chup(self):
        return list(self.bang)

    def kill(self, g, sig):
        self.trung += [(t.pid, sig) for t in self.bang if t.pgid == g]


class PopenTaiCap(subprocess.Popen):
    """Gốc đã là xác; GẶT nó thì số 4242 về nhân và được cấp ngay cho `LA`. Không fork (không gọi `Popen.__init__`)."""
    def __init__(self, nhan):
        self.pid, self.returncode, self.nhan = 4242, None, nhan
        self.stdin = self.stdout = self.stderr = None

    def poll(self):
        if self.returncode is None:
            self.returncode, self.nhan.bang = 0, [LA]
        return self.returncode

    def wait(self, timeout=None):
        return self.poll()


def test_dang_ky_loi_khac_esrch_khong_gat_goc_va_khong_tin_hieu_nao_trung_nhom_thay_the(monkeypatch):
    nh, that, chu = Nhan(), [], []
    monkeypatch.setattr(giu_xac, "_kqueue", KqLoi)
    monkeypatch.setattr(os, "killpg", lambda g, s: that.append((g, s)))
    with pytest.raises(LoiThuHoi):
        khoi_chay(["gia"], kill=nh.kill, chu=chu, popen=lambda a, **kw: PopenTaiCap(nh), chup=nh.chup)
    assert thu_hoi_con_lai(chu, cho_term=0.1, cho_cuoi=0.1, han_gui=1) is False      # không bao giờ xác nhận
    assert 7000 not in {pid for pid, _ in nh.trung} and that == []
    assert len(chu) == 1 and chu[0].p.returncode is None and nh.trung                 # xác giữ số; gốc vẫn được gửi


def test_dang_ky_loi_voi_con_that_van_giu_xac_va_giet_duoc_nhom_goc(monkeypatch):
    monkeypatch.setattr(giu_xac, "_kqueue", KqLoi)
    chu = []
    try:
        with pytest.raises(LoiThuHoi, match="chưa xác nhận"):
            khoi_chay(NGU, kill=kill_cuc_bo, chu=chu)
        assert thu_hoi_con_lai(chu, cho_term=0.2, cho_cuoi=0.5) is False and chu[0].p.returncode is None
        assert chu[0].p.wait(5) in (-signal.SIGTERM, -signal.SIGKILL)                 # nhóm gốc (chưa gặt) bị giết
    finally:
        for n in chu:
            if n.p.poll() is None:
                n.p.kill()
                n.p.wait(5)


@pytest.mark.parametrize("loi_than", [None, RuntimeError("BI-MAT")])
def test_kill_bi_tu_choi_hay_goc_treo_thi_loi_thu_hoi_nhom_van_trong_chu(loi_than):
    def tu_choi(g, s):
        raise PermissionError
    with pytest.raises(LoiThuHoi, match="KHÔNG xác nhận") as e:
        with so_huu("KHÔNG xác nhận — cổng đóng", cho_term=0.1, cho_cuoi=0.1, han_gui=0.2) as chu:
            khoi_chay(["x"], kill=tu_choi, chu=chu, popen=lambda a, **kw: PopenGia(), chup=lambda: [])
            if loi_than:
                raise loi_than
    assert chu[0].ket_thu_hoi is False and chu[0].p.returncode is None              # còn chủ, không gặt
    assert "BI-MAT" not in str(e.value) and (loi_than is None or e.value.__suppress_context__)


def test_khoi_chay_bat_buoc_danh_sach_so_huu_truoc_khi_spawn():
    goi = []
    with pytest.raises(TypeError):
        khoi_chay(["x"], kill=kill_cuc_bo, chu=None, popen=lambda a, **kw: goi.append(1))
    assert goi == []
```

Tạo mới `tests/test_so_huu_ngat.py` (nguyên văn):

```python
"""Hoãn ngắt ở ranh giới sở hữu (`tram/kiem/ngat.py`; review vòng 1 A03, vòng 2 R2-02): Ctrl-C tới NGAY sau Popen được
hoãn, `Nhom` vào `chu` rồi tín hiệu mới phát lại qua handler cũ; tín hiệu tới đúng lúc khôi phục handler không để
handler nào kẹt ở bộ ghi. Tiến trình thật chỉ là `python -c` của chính user đang test; tín hiệu chỉ phát vào CHÍNH tiến
trình test (`raise_signal`) với handler của test."""
import signal
import subprocess
import sys

import pytest

from test_vong_doi import _song
from tram.kiem import ngat as ngat_mod
from tram.kiem.so_huu import thu_hoi_con_lai
from tram.kiem.vong_doi import khoi_chay, kill_cuc_bo

NGU = [sys.executable, "-c", "import time; time.sleep(60)"]


class Ngat(Exception):
    pass


def ngat(so, khung):
    raise Ngat(so)


def popen_ngat(goi):
    def popen(argv, **kw):
        p = subprocess.Popen(argv, **kw)
        goi.append(p)
        signal.raise_signal(signal.SIGINT)                  # Ctrl-C tới khi Popen đã có PID mà chưa trả
        return p
    return popen


def don(goi):
    for p in goi:
        if p.poll() is None:
            p.kill()
            p.wait(5)


def test_ngat_luc_spawn_duoc_hoan_nhom_da_trong_chu_roi_moi_phat_lai():
    goi, chu, cu = [], [], signal.signal(signal.SIGINT, ngat)          # handler của người gọi (vd. `tram tho chay`)
    try:
        with pytest.raises(Ngat):
            khoi_chay(NGU, kill=kill_cuc_bo, chu=chu, popen=popen_ngat(goi))
        assert [n.p for n in chu] == goi and _song(goi[0].pid)          # khoi_chay không tự giết: đã bàn giao
        assert signal.getsignal(signal.SIGINT) is ngat                    # handler cũ khôi phục rồi mới phát lại
        assert thu_hoi_con_lai(chu) is True and not _song(goi[0].pid)
    finally:
        signal.signal(signal.SIGINT, cu)
        don(goi)


def test_tin_hieu_toi_dung_luc_khoi_phuc_handler_van_khoi_phuc_het(monkeypatch):
    goi, chu, da = [], [], []
    cu = {s: signal.signal(s, ngat) for s in (signal.SIGINT, signal.SIGTERM)}

    def dat(so, h):
        r = signal.signal(so, h)
        if h is ngat and not da:                          # tín hiệu tới NGAY khi handler đầu tiên vừa khôi phục
            da.append(so)
            signal.raise_signal(so)
        return r
    monkeypatch.setattr(ngat_mod, "_dat", dat)
    try:
        with pytest.raises(Ngat):
            khoi_chay(NGU, kill=kill_cuc_bo, chu=chu, popen=lambda a, **kw: goi.append(subprocess.Popen(a, **kw))
                      or goi[-1])
        assert signal.getsignal(signal.SIGINT) is ngat and signal.getsignal(signal.SIGTERM) is ngat
        assert [n.p for n in chu] == goi and thu_hoi_con_lai(chu) is True and not _song(goi[0].pid)
    finally:
        for s, h in cu.items():
            signal.signal(s, h)
        don(goi)
```

Tạo mới `tests/test_so_huu_nguoi_goi.py` (nguyên văn):

```python
"""Hợp đồng sở hữu (`so_huu`, review vòng 2 R2-02): MỌI người gọi `khoi_chay` trên HEAD — lệnh kiểm, CLI Claude/Codex,
app-server, dò danh tính — đặt spawn trong khối sở hữu: Ctrl-C tới NGAY sau Popen (hoãn trong `khoi_chay`, phát lại
khi `Nhom` đã ở `chu`) thì con vẫn bị thu hồi rồi ngắt mới nổi lên. Tiến trình thật chỉ là `python -c` của chính user
đang test; tín hiệu chỉ phát vào CHÍNH tiến trình test (`raise_signal`) với handler của test."""
import os
import signal
import threading

import pytest

from test_so_huu_ngat import NGU, Ngat, don, ngat, popen_ngat
from test_vong_doi import _song
from tram.chay_cli.claude import ChayClaude
from tram.chay_cli.codex.app_server import hoi_app_server
from tram.chay_cli.codex.chay import ChayCodex
from tram.chay_cli.codex.han_muc import NguonHanMucCodex
from tram.han_muc.claude import NguonHanMucClaude
from tram.kiem.chay_lenh import chay_mot_lenh
from tram.kiem.danh_tinh import quan_sat
from tram.kiem.vong_doi import khoi_chay, kill_cuc_bo


def _chay_lenh(tmp_path, khoi, popen):
    chay_mot_lenh("x", NGU, cwd=tmp_path, env=dict(os.environ), log=tmp_path / "l.log", thoi_gian_cho=5,
                  boc=lambda a: a, kill=kill_cuc_bo, khoi=khoi)


def _claude(tmp_path, khoi, popen):
    (tmp_path / "goi.md").write_text("x")
    ChayClaude(lambda a: a, khe_id="k", khoi=khoi, cho_kill=1).chay(
        NGU, cwd=tmp_path, env=dict(os.environ), stdin=tmp_path / "goi.md", log=tmp_path / "c.log",
        dung=threading.Event(), nguon=NguonHanMucClaude())


def _codex(tmp_path, khoi, popen):
    (tmp_path / "goi.md").write_text("x")
    ChayCodex(lambda a: a, popen=popen, cho_dung_giay=1).chay(
        NGU, cwd=tmp_path, env=dict(os.environ), stdin=tmp_path / "goi.md", log=tmp_path / "c.log",
        dung=threading.Event(), nguon=NguonHanMucCodex())


def _app_server(tmp_path, khoi, popen):
    hoi_app_server(NGU, env=dict(os.environ), thoi_gian_cho=5, kill=kill_cuc_bo, khoi=khoi)


def _quan_sat(tmp_path, khoi, popen):
    quan_sat(lambda a: NGU, kill_cuc_bo, khoi=khoi, han=5)


@pytest.mark.parametrize("nguoi_goi", [_chay_lenh, _claude, _codex, _app_server, _quan_sat])
def test_moi_nguoi_goi_so_huu_tu_pid_ngat_luc_spawn_van_thu_hoi(tmp_path, nguoi_goi):
    goi, cu = [], signal.signal(signal.SIGINT, ngat)
    p = popen_ngat(goi)
    try:
        with pytest.raises(Ngat):
            nguoi_goi(tmp_path, lambda a, **kw: khoi_chay(a, popen=p, **kw), p)
        assert len(goi) == 1 and not _song(goi[0].pid)
    finally:
        signal.signal(signal.SIGINT, cu)
        don(goi)
```

Bản vá `tests/test_vong_doi.py`:

```diff
--- a/tests/test_vong_doi.py
+++ b/tests/test_vong_doi.py
@@ -40,7 +40,7 @@
 
 
 def _chau(tmp_path, *, moi: bool, ngu: float):
-    n = khoi_chay([PY, "-c", CHAU.format(moi=moi, ngu=ngu)], kill=kill_cuc_bo, cwd=tmp_path)
+    n = khoi_chay([PY, "-c", CHAU.format(moi=moi, ngu=ngu)], kill=kill_cuc_bo, chu=[], cwd=tmp_path)
     het = time.monotonic() + 10
     while not (tmp_path / "chau.pid").exists() and time.monotonic() < het:
         time.sleep(0.02)
@@ -100,5 +100,5 @@
     def popen(argv, **kw):
         goi.append(kw)
         return PopenGia()
-    khoi_chay(["x"], kill=kill_cuc_bo, popen=popen, start_new_session=False, cwd="/")
+    khoi_chay(["x"], kill=kill_cuc_bo, chu=[], popen=popen, start_new_session=False, cwd="/")
     assert goi == [{"start_new_session": True, "cwd": "/"}]
```

- [ ] **Step 2: Chạy, thấy đỏ** — `PT tests/test_giu_xac.py tests/test_so_huu.py tests/test_so_huu_ngat.py tests/test_so_huu_nguoi_goi.py tests/test_vong_doi.py`. Kết quả thật trên `f4fa3a8` + Task 1 (18/10):

```
E   ImportError: cannot import name 'giu_xac' from 'tram.kiem'     (test_giu_xac.py, test_so_huu.py)
E   ImportError: cannot import name 'ngat' from 'tram.kiem'        (test_so_huu_ngat.py, test_so_huu_nguoi_goi.py)
!!!!!!!!!!!!!!!!!!!! Interrupted: 4 errors during collection !!!!!!!!!!!!!!!!!!!!
4 errors in 0.16s
```

Đỏ ở mức hành vi — thêm bốn module mới (`giu_xac`, `gui_tin`, `ngat`, `so_huu`) nhưng giữ `vong_doi.py` và mọi người gọi của HEAD:

```
E       TypeError: Popen.__init__() got an unexpected keyword argument 'chu'        (8 ca — khoi_chay cũ không nhận chu)
E           AssertionError: assert (1 == 1 and not True)
E            +  and   True = _song(46003)                ← ×5: _chay_lenh, _claude, _codex, _app_server, _quan_sat —
                                                            Ctrl-C ngay sau Popen: con THẬT còn sống, không ai thu hồi
E       Failed: DID NOT RAISE <class 'tram.kiem.vong_doi.LoiThuHoi'>   (×2 — khoi_chay cũ không có hợp đồng)
FAILED tests/test_so_huu_nguoi_goi.py::test_moi_nguoi_goi_so_huu_tu_pid_ngat_luc_spawn_van_thu_hoi[_chay_lenh]
FAILED tests/test_so_huu_nguoi_goi.py::test_moi_nguoi_goi_so_huu_tu_pid_ngat_luc_spawn_van_thu_hoi[_claude]
FAILED tests/test_so_huu_nguoi_goi.py::test_moi_nguoi_goi_so_huu_tu_pid_ngat_luc_spawn_van_thu_hoi[_codex]
FAILED tests/test_so_huu_nguoi_goi.py::test_moi_nguoi_goi_so_huu_tu_pid_ngat_luc_spawn_van_thu_hoi[_app_server]
FAILED tests/test_so_huu_nguoi_goi.py::test_moi_nguoi_goi_so_huu_tu_pid_ngat_luc_spawn_van_thu_hoi[_quan_sat]
FAILED tests/test_so_huu_ngat.py::… (2) · tests/test_so_huu.py::… (5) · tests/test_giu_xac.py::… (2) · tests/test_vong_doi.py::… (4)
18 failed, 6 passed in 3.95s
```

Test để sót con khi đỏ tự thu hồi trong `finally` (`ps` sau lần chạy: không còn `time.sleep(60)` của test).

**Đối chứng R2-01 trên mã Task 2 của bản plan vòng 2 (`Goc` gặt trên nhánh lỗi + `bo_khan`), kịch bản của `test_dang_ky_loi_khac_esrch_khong_gat_goc_va_khong_tin_hieu_nao_trung_nhom_thay_the` (nhân giả, `os.killpg` thay bằng bản ghi):**

```
E       assert (7000 not in {7000})            ← gặt gốc rồi gửi SIGKILL tới số 4242 đã cấp lại: trúng việc khác
1 failed in 0.04s
```

- [ ] **Step 3: Mã**

Tạo mới `tram/kiem/giu_xac.py` (nguyên văn):

```python
"""Gốc của một `Nhom` (V2-0, dot7-C01): biết gốc đã THOÁT mà KHÔNG GẶT. Popen thật → kqueue `EVFILT_PROC` +
`NOTE_EXIT|NOTE_EXITSTATUS` trên con của CHÍNH tiến trình này (đo trên macOS 15.6.1: sự kiện mang mã chờ, tiến trình
còn là xác tới khi `waitpid`). Còn xác thì số pid — cũng là số NHÓM và PHIÊN của gốc, vì gốc luôn `start_new_session`
— không thể được cấp lại: mọi tiến trình mang nhóm đó là hậu duệ của gốc, tín hiệu gửi nhóm gốc không trúng ai khác.
Chỉ gặt ở `gat()`, sau khi thu hồi đã xác nhận. Đăng ký trên xác (gốc thoát trước khi kịp đăng ký) trả ESRCH → gặt
ngay để lấy mã, TRƯỚC mọi lần gửi; nhóm gốc khi đó mất bảo vệ, ai còn mang số đó thành "mơ hồ" (không gửi, không xác
nhận). Review vòng 2 R2-01: lỗi khác ESRCH (hay không tạo được kqueue) → KHÔNG gặt — gốc vẫn là con chưa gặt nên số
nhóm vẫn được giữ (gửi nhóm gốc vẫn an toàn); `hong` = không bao giờ xác nhận gốc đã thoát → `thu_hoi` không bao giờ
True, người gọi giữ `Nhom` trong danh sách sở hữu, cổng đóng. Popen GIẢ của test (không phải `subprocess.Popen`) → chờ
bằng `wait`/`poll` của chính nó."""
import errno
import os
import select
import subprocess
import time

EV_RECEIPT = 0x0040                                 # <sys/event.h>; Python không xuất hằng này
NOTE_EXITSTATUS = 0x04000000
_kqueue = select.kqueue                             # test thay để tiêm lỗi đăng ký


class Goc:
    def __init__(self, p):
        self.p, self._kq, self._ma, self.hong = p, None, None, False
        if not isinstance(p, subprocess.Popen) or p.returncode is not None:
            return
        try:
            self._kq = _kqueue()
            (r,) = self._kq.control([select.kevent(p.pid, select.KQ_FILTER_PROC, select.KQ_EV_ADD | EV_RECEIPT,
                                                   select.KQ_NOTE_EXIT | NOTE_EXITSTATUS)], 1, 0)
            loi = r.data if r.flags & select.KQ_EV_ERROR else 0
        except Exception:                           # noqa: BLE001 — không theo dõi được gốc: như đăng ký lỗi
            loi = -1
        if loi == errno.ESRCH:
            self.gat()
        elif loi:
            self._dong()
            self.hong = True

    @property
    def pid(self) -> int:
        return self.p.pid

    def chua_gat(self) -> bool:
        """Số pid/nhóm gốc còn được giữ (gốc còn sống hoặc còn là xác)."""
        return self.p.returncode is None

    def thoat(self, giay: float = 0.0) -> bool:
        """True khi gốc đã thoát (còn xác hoặc đã gặt). Chờ tối đa `giay`; KHÔNG gặt. `hong` → luôn False."""
        if self.p.returncode is not None or self._ma is not None:
            return True
        if self.hong:
            time.sleep(max(0.0, giay))
            return False
        if self._kq is None:
            try:
                self.p.wait(timeout=max(0.0, giay))
                return True
            except subprocess.TimeoutExpired:
                return False
        try:
            su_kien = self._kq.control(None, 1, max(0.0, giay))
        except OSError:
            self.hong = True
            self._dong()
            return False
        for e in su_kien:
            if e.fflags & select.KQ_NOTE_EXIT:
                self._ma = os.waitstatus_to_exitcode(e.data)
        return self._ma is not None

    def ma(self) -> int | None:
        return self.p.returncode if self.p.returncode is not None else self._ma

    def _dong(self) -> None:
        if self._kq is not None:
            kq, self._kq = self._kq, None
            try:
                kq.close()
            except OSError:
                pass                            # lỗi đóng không được cắt ngang bàn giao/thu hồi tiến trình

    def gat(self) -> None:
        self._dong()
        self.p.poll()
```

Tạo mới `tram/kiem/gui_tin.py` (nguyên văn):

```python
"""Gửi tín hiệu cho nhóm tiến trình (P1; V2-0). `kill_cuc_bo` gửi DƯỚI user của chính tiến trình này — chỉ dùng cho
nhóm gốc CHƯA GẶT (số không thể cấp lại) hoặc khi mọi tiến trình là của chính user (test)."""
import os
import subprocess
from collections.abc import Callable

Kill = Callable[[int, int], None]
LOI_GUI = (OSError, subprocess.SubprocessError)


def kill_cuc_bo(pgid: int, sig: int) -> None:
    try:
        os.killpg(pgid, sig)
    except (ProcessLookupError, PermissionError):
        pass
```

Tạo mới `tram/kiem/ngat.py` (nguyên văn):

```python
"""Hoãn ngắt ở RANH GIỚI SỞ HỮU (V2-0 — review A03, R2-02): MỘT cơ chế cho mọi chỗ spawn/thu hồi (`vong_doi`,
`so_huu`, bộ chạy) và cho CLI cha (plan B thêm `term_thanh_ngat` vào file này). Trong khối `hoan()` ngoài cùng, SIGINT/
SIGTERM tới LUỒNG CHÍNH chỉ được GHI; ra khỏi khối: khôi phục MỌI handler cũ — kể cả khi một tín hiệu tới ngay giữa lúc
khôi phục — rồi PHÁT LẠI theo thứ tự nhận (`raise_signal`, handler cũ chạy đồng bộ: KeyboardInterrupt, handler của
người gọi, hay mặc định). Tín hiệu đầu ném thì các tín hiệu sau không phát lại; ngắt đang chờ thắng lỗi của thân khối.
Khối lồng nhau dùng chung một lần ghi. Không hoãn ngoài luồng chính (handler Python chỉ chạy ở luồng chính) và với tín
hiệu có handler đặt từ C (`getsignal` None). Không hứa gì với SIGKILL."""
import signal
import threading
from contextlib import contextmanager

TIN_HIEU = (signal.SIGINT, signal.SIGTERM)
_dat = signal.signal                        # test thay để mô phỏng tín hiệu tới đúng lúc khôi phục handler
_muc, _cu, _nhan = 0, {}, []


def _ghi(so, khung):
    _nhan.append(so)


def _khoi_phuc() -> None:
    loi = None
    for s, h in list(_cu.items()):
        try:
            _dat(s, h)
        except BaseException as e:          # noqa: BLE001 — tín hiệu tới ngay khi handler cũ vừa về: khôi phục nốt
            loi = loi or e
    _cu.clear()
    nhan, _nhan[:] = list(_nhan), []
    if loi is not None:
        raise loi
    for s in nhan:
        signal.raise_signal(s)


@contextmanager
def hoan():
    global _muc
    if threading.current_thread() is not threading.main_thread():
        yield
        return
    if _muc == 0:
        _nhan.clear()
        _cu.update({s: h for s in TIN_HIEU if (h := signal.getsignal(s)) is not None})
    _muc += 1
    try:
        if _muc == 1:                       # cài bộ ghi TRONG try: tín hiệu tới giữa lúc cài vẫn được khôi phục
            for s in _cu:
                _dat(s, _ghi)
        yield
    finally:
        _muc -= 1
        if _muc == 0:
            _khoi_phuc()
```

Tạo mới `tram/kiem/so_huu.py` (nguyên văn):

```python
"""HỢP ĐỒNG SỞ HỮU tiến trình con (V2-0 — review vòng 1 A03, vòng 2 R2-01/R2-02; plan B dựa vào, thay "H-A03"):

1. `vong_doi.khoi_chay(argv, *, kill, chu, …)` là nơi DUY NHẤT spawn; `chu` (list) BẮT BUỘC. Popen + dựng `Nhom` +
   `chu.append` nằm trong `ngat.hoan()`. Ném `OSError` ⇒ `chu` không đổi: Popen chưa tạo được tiến trình (lỗi exec thì
   Popen tự gặt con). MỌI lối ra khác sau khi Popen trả — trả `Nhom`, `LoiThuHoi` vì không theo dõi được gốc, ngắt
   được phát lại khi ra khỏi `hoan()` — đều xảy ra khi `Nhom` ĐÃ ở `chu`.
2. Người gọi: MỘT khối sở hữu bao lời gọi `khoi_chay` và mọi bước sau — `with so_huu(...) as chu:`, hoặc `chu = []` +
   `try/finally` với `thu_hoi_con_lai(chu)` (bộ chạy một chủ: `chay_gioi_han`, `chay_han_tong`). Mỗi `Nhom` chưa thu
   hồi lần nào được thu hồi trong `hoan()` (ngắt lần hai ném SAU khi xong).
3. `LoiThuHoi` KHÔNG có nghĩa "không còn con": con/hậu duệ có thể còn sống (kill bị từ chối, treo sau SIGKILL, hậu duệ
   tách phiên, không theo dõi được gốc). Nó nghĩa là KHÔNG XÁC NHẬN: `Nhom` vẫn trong `chu` (gốc chưa gặt giữ số nhóm),
   kết quả không công nhận, cổng/khe giữ đóng; tầng trên dọn theo UID dành riêng (khe: `tho.don_uid`; `tram-kiem`:
   `cong_that.thu_hoi_theo_uid`). Lệnh dưới chính tài khoản quản lý không có lưới UID: chỉ cổng đóng + Đại ca kiểm.
4. Chỉ `Nhom.thu_hoi` đã xác nhận mới gặt gốc; nhánh lỗi không bao giờ gặt (`giu_xac`, R2-01)."""
from contextlib import contextmanager

from tram.kiem.ngat import hoan
from tram.kiem.vong_doi import LoiThuHoi


def thu_hoi_con_lai(chu: list, **kw) -> bool:
    """Thu hồi mọi `Nhom` trong `chu` CHƯA thu hồi lần nào (`ket_thu_hoi` None), trong `hoan()`. True khi mọi `Nhom`
    vừa thu hồi đều xác nhận (không còn gì → True); người gọi đã tự thu hồi, tự xử lý kết quả thì không thu hồi lại."""
    with hoan():
        return all([n.thu_hoi(**kw) for n in chu if getattr(n, "ket_thu_hoi", None) is None])


@contextmanager
def so_huu(loi: str, **kw):
    """`with so_huu("…") as chu:` — ra khỏi khối (xong, lỗi, ngắt) thì `thu_hoi_con_lai(chu, **kw)`. Chưa xác nhận →
    `LoiThuHoi(loi)` THAY lỗi thường (`from None` — không nối chuỗi có thể mang byte đầu ra); ngắt vẫn là ngắt."""
    chu: list = []
    try:
        yield chu
    except KeyboardInterrupt:
        thu_hoi_con_lai(chu, **kw)
        raise
    except BaseException:
        if not thu_hoi_con_lai(chu, **kw):
            raise LoiThuHoi(loi) from None
        raise
    if not thu_hoi_con_lai(chu, **kw):
        raise LoiThuHoi(loi)
```

Bản vá `tram/kiem/vong_doi.py`:

```diff
--- a/tram/kiem/vong_doi.py
+++ b/tram/kiem/vong_doi.py
@@ -1,19 +1,10 @@
-"""Vòng đời MỘT tiến trình con có hạn hữu hạn (lát P1, dot6-C02/Q02) — primitive DUY NHẤT cho mọi chỗ spawn rồi
-chờ/giết: lệnh kiểm (`chay_lenh`), quota app-server, CLI của phiếu, dò danh tính và hạn tổng harness (3C-B).
-
-- `khoi_chay` LUÔN đặt `start_new_session`: nhóm riêng, KHÔNG terminal điều khiển → `sudo` không có tty để cấp pty
-  (theo man sudoers, `use_pty` chỉ áp khi sudo chạy trong terminal — G3 đo trên macOS thật).
-- `cho` chụp cây mỗi `CHU_KY_CHUP` giây khi gốc còn sống: con/cháu (kể cả nhóm/phiên mới do sudo/pty hay do lệnh tự
-  setsid) được ghi nhận TRƯỚC khi cha thoát và mất liên kết ppid. Nhóm đã biết chỉ giữ nhóm còn thành viên trong ảnh
-  chụp thành công gần nhất — số nhóm đã chết không bị dùng lại khi PID quay vòng.
-- `thu_hoi` không bao giờ chờ vô hạn: SIGTERM mọi nhóm còn sống của cây, chờ `cho_term`, SIGKILL nhóm còn sống, chờ
-  `cho_cuoi`; mỗi pha gửi qua `kill(pgid, sig)` của người gọi (principal khác user → `sudo -n … /bin/kill`, có hạn
-  tuyệt đối `lenh_ngan`) và thôi gửi khi pha đó quá `han_gui`. True CHỈ khi gốc đã được gặt VÀ ảnh chụp sau cùng không
-  còn ai trong cây. Ca "treo sau SIGKILL" (gốc là `sudo` root không nhận tín hiệu của ta, tiến trình kẹt trong nhân):
-  hết `cho_cuoi` → False, người gọi giữ cổng đóng — không `wait()` trần ở bất kỳ đâu.
-- Chỉ gửi cho nhóm THẤY CÒN SỐNG trong ảnh chụp thành công ≤ 2 s trước (cũ hơn → chỉ nhóm gốc) và nhóm của gốc khi
-  gốc chưa gặt (PID chưa gặt không bị tái dùng). Không nhóm 0/1, nhóm của tiến trình quản lý, không theo username.
-Cận trên của `thu_hoi`: cho_term + cho_cuoi + 2 × (han_gui + một lần `kill`) + 3 lần `ps` (mỗi lần ≤ 5 s)."""
+"""Vòng đời MỘT tiến trình con có hạn hữu hạn (P1, dot6-C02/Q02) — primitive DUY NHẤT cho mọi chỗ spawn rồi chờ/giết.
+`khoi_chay` LUÔN `start_new_session` (không terminal điều khiển); hợp đồng sở hữu từ lúc có PID ở `so_huu` (A03,
+R2-02). `cho` chụp cây mỗi `CHU_KY_CHUP` giây và biết gốc thoát mà KHÔNG gặt (`giu_xac.Goc`, V2-0) — xác giữ số
+nhóm gốc. `thu_hoi` có hạn: SIGTERM → `cho_term` → SIGKILL → `cho_cuoi`, mỗi pha qua `kill(pgid, sig)` của người gọi,
+thôi gửi khi pha quá `han_gui`; chỉ nhóm THẤY CÒN SỐNG trong ảnh ≤ 2 s trước và nhóm gốc chưa gặt (không nhóm 0/1/của
+quản lý). True CHỈ khi gốc đã thoát, cây chỉ còn xác gốc — rồi mới gặt. Treo sau SIGKILL → False, cổng giữ đóng.
+Cận trên: cho_term + cho_cuoi + 2 × (han_gui + một lần `kill`) + 3 lần chụp bảng tiến trình."""
 import math
 import os
 import signal
@@ -22,9 +13,10 @@
 from collections.abc import Callable
 
 from tram.kiem.cay_tien_trinh import TienTrinh, cay, chup_he
+from tram.kiem.giu_xac import Goc
+from tram.kiem.gui_tin import LOI_GUI, Kill, kill_cuc_bo  # noqa: F401 — tên cũ, người gọi import từ đây
+from tram.kiem.ngat import hoan
 
-Kill = Callable[[int, int], None]
-LOI_GUI = (OSError, subprocess.SubprocessError)
 CHU_KY_CHUP = 1.0
 
 
@@ -32,16 +24,10 @@
     """Không xác nhận được cây tiến trình đã hết — kết quả không được công nhận, cổng giữ đóng."""
 
 
-def kill_cuc_bo(pgid: int, sig: int) -> None:
-    try:
-        os.killpg(pgid, sig)
-    except (ProcessLookupError, PermissionError):
-        pass
-
-
 class Nhom:
     def __init__(self, p: subprocess.Popen, *, kill: Kill, chup: Callable[[], list[TienTrinh]] = chup_he):
-        self.p, self.kill, self.chup = p, kill, chup
+        self.p, self.kill, self.chup, self.goc = p, kill, chup, Goc(p)
+        self.ket_thu_hoi: bool | None = None                            # None: chưa thu hồi lần nào (`so_huu`)
         self.nhom_biet: set[int] = {p.pid}
         self.lan_dung = time.monotonic()                                # lần chụp thành công gần nhất
         self.lan_chup = time.monotonic() - CHU_KY_CHUP + 0.2          # lần chụp đầu sau 0,2 s
@@ -51,13 +37,12 @@
             raise ValueError("hạn chờ phải hữu hạn")
         het = time.monotonic() + max(0.0, giay)
         while True:
-            try:
-                return self.p.wait(timeout=max(0.0, min(het, self.lan_chup + CHU_KY_CHUP) - time.monotonic()))
-            except subprocess.TimeoutExpired:
-                if time.monotonic() >= self.lan_chup + CHU_KY_CHUP:
-                    self.cay()
-                if time.monotonic() >= het:
-                    return None
+            if self.goc.thoat(max(0.0, min(het, self.lan_chup + CHU_KY_CHUP) - time.monotonic())):
+                return self.goc.ma()
+            if time.monotonic() >= self.lan_chup + CHU_KY_CHUP:
+                self.cay()
+            if time.monotonic() >= het:
+                return None
 
     def cay(self) -> list[TienTrinh] | None:
         """Cây hiện tại; None khi `ps` lỗi (không xác nhận được gì, giữ nhóm đã biết)."""
@@ -66,14 +51,14 @@
             ds = self.chup()
         except (OSError, subprocess.SubprocessError, ValueError):
             return None
-        song, self.lan_dung = self.p.poll() is None, time.monotonic()
+        song, self.lan_dung = self.goc.chua_gat(), time.monotonic()
         con = cay(ds, self.p.pid if song else None, self.nhom_biet)
         self.nhom_biet = {t.pgid for t in con} | ({self.p.pid} if song else set())
         return con
 
     def _gui(self, sig: int, han: float) -> None:
         moi = time.monotonic() - self.lan_dung <= 2 * CHU_KY_CHUP
-        nhom = (self.nhom_biet if moi else set()) | ({self.p.pid} if self.p.poll() is None else set())
+        nhom = (self.nhom_biet if moi else set()) | ({self.p.pid} if self.goc.chua_gat() else set())
         for g in sorted(nhom - {0, 1, os.getpgrp()}):
             if time.monotonic() >= han:
                 return
@@ -84,30 +69,43 @@
 
     def _cho_het(self, giay: float) -> list[TienTrinh] | None:
         het = time.monotonic() + giay
-        try:
-            self.p.wait(timeout=giay)
-        except subprocess.TimeoutExpired:
-            pass
+        self.goc.thoat(giay)
         while True:
             con = self.cay()
-            if (con == [] and self.p.poll() is not None) or time.monotonic() >= het:
+            if self._sach(con) or time.monotonic() >= het:
                 return con
             time.sleep(0.05)
 
+    def _sach(self, con: list[TienTrinh] | None) -> bool:
+        """Gốc đã thoát và cây chỉ còn (nhiều nhất) xác của gốc."""
+        return con is not None and self.goc.thoat() and all(t.pid == self.p.pid for t in con)
+
     def thu_hoi(self, *, cho_term: float = 2.0, cho_cuoi: float = 2.0, han_gui: float = 10.0) -> bool:
         con = self.cay()
         for sig, cho in ((signal.SIGTERM, cho_term), (signal.SIGKILL, cho_cuoi)):
-            if con == [] and self.p.poll() is not None:
-                return True
+            if self._sach(con):
+                break
             self._gui(sig, time.monotonic() + han_gui)
             con = self._cho_het(cho)
-        return con == [] and self.p.poll() is not None
+        self.ket_thu_hoi = self._sach(con)
+        if self.ket_thu_hoi:
+            self.goc.gat()
+        return self.ket_thu_hoi
 
 
-def khoi_chay(argv: list[str], *, kill: Kill, popen: Callable = subprocess.Popen,
+def khoi_chay(argv: list[str], *, kill: Kill, chu: list, popen: Callable = subprocess.Popen,
               chup: Callable[[], list[TienTrinh]] = chup_he, **kw) -> Nhom:
+    """Hợp đồng `so_huu` mục 1: `Nhom` vào `chu` TRONG `hoan()`, trước mọi lối ra sau Popen; gốc không theo dõi được
+    (`Goc.hong`) → `LoiThuHoi`, `Nhom` vẫn ở `chu` — người gọi thu hồi (không bao giờ xác nhận), cổng đóng."""
+    if not isinstance(chu, list):
+        raise TypeError("chu phải là list sở hữu của người gọi")
     kw["start_new_session"] = True
-    return Nhom(popen(argv, **kw), kill=kill, chup=chup)
+    with hoan():
+        n = Nhom(popen(argv, **kw), kill=kill, chup=chup)
+        chu.append(n)
+    if n.goc.hong:
+        raise LoiThuHoi("không theo dõi được gốc — tiến trình ở danh sách sở hữu của người gọi, chưa xác nhận thu hồi")
+    return n
 
 
 def cho_den_dung(n: Nhom, dung, *, cho_term: float) -> tuple[int | None, bool]:
```

Bản vá `tram/kiem/danh_tinh.py`:

```diff
--- a/tram/kiem/danh_tinh.py
+++ b/tram/kiem/danh_tinh.py
@@ -12,7 +12,8 @@
 from collections.abc import Callable
 
 from tram.kiem.cay_tien_trinh import TienTrinh, chup_he
-from tram.kiem.vong_doi import Kill, LoiThuHoi, khoi_chay
+from tram.kiem.so_huu import so_huu
+from tram.kiem.vong_doi import Kill, khoi_chay
 
 SLEEP = "/bin/sleep"
 
@@ -28,23 +29,20 @@
 
 def quan_sat(boc: Callable[[list[str]], list[str]], kill: Kill, *, khoi: Callable = khoi_chay,
              chup: Callable[[], list[TienTrinh]] = chup_he, han: float = 10.0) -> list[TienTrinh]:
-    """Cây của tiến trình dò lúc mọi lá đã rời UID root."""
-    try:
-        n = khoi(boc([SLEEP, "30"]), kill=kill, chup=chup, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
-                 stderr=subprocess.DEVNULL, env={"PATH": "/usr/bin:/bin"})
-    except (OSError, ValueError) as e:
-        raise LoiDanhTinh(f"không khởi chạy được tiến trình dò: {type(e).__name__}") from None
-    het = time.monotonic() + han
-    try:
+    """Cây của tiến trình dò lúc mọi lá đã rời UID root. Sở hữu theo `so_huu` (R2-02): spawn trong khối sở hữu."""
+    with so_huu("không xác nhận thu hồi tiến trình dò", cho_term=1.0, cho_cuoi=1.0, han_gui=2.0) as chu:
+        try:
+            n = khoi(boc([SLEEP, "30"]), kill=kill, chup=chup, chu=chu, stdin=subprocess.DEVNULL,
+                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env={"PATH": "/usr/bin:/bin"})
+        except (OSError, ValueError) as e:
+            raise LoiDanhTinh(f"không khởi chạy được tiến trình dò: {type(e).__name__}") from None
+        het = time.monotonic() + han
         while time.monotonic() < het and n.p.poll() is None:
             con = n.cay()
             if con and all(t.uid != 0 for t in la_cua(con)):
                 return con
             time.sleep(0.05)
         raise LoiDanhTinh("không thấy tiến trình dò dưới boc (wrapper lỗi, bị từ chối hoặc quá hạn)")
-    finally:
-        if not n.thu_hoi(cho_term=1.0, cho_cuoi=1.0, han_gui=2.0):
-            raise LoiThuHoi("không xác nhận thu hồi tiến trình dò")
 
 
 def uid_cua(ten: str) -> int:
```

Bản vá `tram/kiem/chay_lenh.py`:

```diff
--- a/tram/kiem/chay_lenh.py
+++ b/tram/kiem/chay_lenh.py
@@ -11,6 +11,7 @@
 from dataclasses import dataclass
 from pathlib import Path
 
+from tram.kiem.so_huu import so_huu
 from tram.kiem.vong_doi import khoi_chay
 from tram.kiem.vong_doi import kill_cuc_bo as _kill_nhom          # tên cũ — 3c/4a import, một định nghĩa ở P1
 
@@ -56,13 +57,13 @@
     if not math.isfinite(thoi_gian_cho):
         raise ValueError("thoi_gian_cho phải hữu hạn")
     log.parent.mkdir(parents=True, exist_ok=True)
-    with open(log, "wb") as f:
+    with open(log, "wb") as f, so_huu("lệnh kiểm: không xác nhận thu hồi cây tiến trình", cho_term=cho_kill) as chu:
         if argv is None:
             f.write(f"[tram] lệnh không khớp lenh_cho_phep — không chạy: {lenh}\n".encode())
             f.flush()
             return _ket_qua(lenh, log, None, False)
-        try:
-            n = khoi(boc(argv), kill=kill, cwd=cwd, env=dict(env), stdin=subprocess.DEVNULL, stdout=f,
+        try:                                        # sở hữu từ PID (`so_huu`): lỗi/ngắt trước bước thu hồi → thu hồi
+            n = khoi(boc(argv), kill=kill, chu=chu, cwd=cwd, env=dict(env), stdin=subprocess.DEVNULL, stdout=f,
                      stderr=subprocess.STDOUT)
         except OSError as e:
             f.write(f"[tram] lỗi khởi chạy: {type(e).__name__}\n".encode())     # không chép argv/đường dẫn
```

Bản vá `tram/chay_cli/claude.py`:

```diff
--- a/tram/chay_cli/claude.py
+++ b/tram/chay_cli/claude.py
@@ -16,10 +16,13 @@
 from tram.phieu.mo_hinh import che_ma_giao
 from tram.han_muc.mo_hinh import HanMuc
 from tram.han_muc.nguon import NguonHanMuc
+from tram.kiem.so_huu import so_huu
 from tram.kiem.vong_doi import LoiThuHoi, cho_den_dung, khoi_chay
 from tram.tho.mo_coi import Kill, kill_cuc_bo
 
+LOI_DON = "Không dọn được nhóm CLI; dừng khe để kiểm principal"
 
+
 class ChayClaude:
     def __init__(self, boc: Callable[[list[str]], list[str]], *, khe_id: str, kill: Kill = kill_cuc_bo,
                  khi_bat_dau: Callable[[int], None] | None = None,
@@ -42,27 +45,21 @@
                         khi_vuot=dung.set)
         log.parent.mkdir(parents=True, exist_ok=True)
         bat_dau, ma = time.monotonic(), None
-        with open(stdin, "rb") as vao, open(log, "wb") as f:
-            try:
-                n = self.khoi(self.boc(argv), kill=self.kill, cwd=cwd, env=env, stdin=vao, stdout=subprocess.PIPE,
-                              stderr=subprocess.STDOUT)
+        with open(stdin, "rb") as vao, open(log, "wb") as f, so_huu(LOI_DON, cho_term=self.cho_kill) as chu:
+            try:                                            # sở hữu từ PID (`so_huu`): lỗi/ngắt trước khi thu hồi
+                n = self.khoi(self.boc(argv), kill=self.kill, chu=chu, cwd=cwd, env=env, stdin=vao,
+                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
             except OSError as e:
                 f.write(f"[tram] lỗi khởi chạy CLI: {type(e).__name__}\n".encode())
             else:
-                try:
-                    if self.khi_bat_dau:
-                        self.khi_bat_dau(n.p.pid)
-                    doc_t = threading.Thread(target=self._doc, args=(n.p, f, doc, env.get("TRAM_MA_GIAO")),
-                                             daemon=True)
-                    doc_t.start()
-                except BaseException:                       # lỗi giữa spawn và chờ: không để CLI sống ngoài quản lý
-                    if not n.thu_hoi(cho_term=self.cho_kill):
-                        raise LoiThuHoi("Không dọn được nhóm CLI; dừng khe để kiểm principal") from None
-                    raise
+                if self.khi_bat_dau:
+                    self.khi_bat_dau(n.p.pid)
+                doc_t = threading.Thread(target=self._doc, args=(n.p, f, doc, env.get("TRAM_MA_GIAO")), daemon=True)
+                doc_t.start()
                 ma, sach = cho_den_dung(n, dung, cho_term=self.cho_kill)   # kể cả con cháu giữ stdout sau khi CLI thoát
                 doc_t.join(timeout=self.cho_kill)
                 if not sach or doc_t.is_alive():
-                    raise LoiThuHoi("Không dọn được nhóm CLI; dừng khe để kiểm principal")
+                    raise LoiThuHoi(LOI_DON)
         digest = "sha256:" + hashlib.sha256(log.read_bytes()).hexdigest()
         return doc.ket_qua(ma_thoat=ma, bi_dung=dung.is_set(), thoi_gian_ms=int((time.monotonic() - bat_dau) * 1000),
                            digest_log=digest)
```

Bản vá `tram/chay_cli/codex/chay.py`:

```diff
--- a/tram/chay_cli/codex/chay.py
+++ b/tram/chay_cli/codex/chay.py
@@ -11,10 +11,13 @@
 from tram.chay_cli.giao_dien import KetQuaChay
 from tram.han_muc.nguon import NguonHanMuc
 from tram.phieu.mo_hinh import che_ma_giao
+from tram.kiem.so_huu import so_huu
 from tram.kiem.vong_doi import LoiThuHoi, cho_den_dung, khoi_chay
 from tram.tho.mo_coi import kill_cuc_bo
 
+LOI_DON = "Không dọn được nhóm CLI; dừng khe để kiểm principal"
 
+
 class ChayCodex:
     def __init__(self, boc=lambda a: a, *, khe_id="", kill=kill_cuc_bo, khi_bat_dau=None,
                  khi_han_muc=None, tran_token_ra=None, popen=subprocess.Popen, cho_dung_giay=10.0):
@@ -44,27 +47,22 @@
              dung: threading.Event, nguon: NguonHanMuc) -> KetQuaChay:
         doc, t0, ma = DocLuongCodex(nguon), time.monotonic(), None
         log.parent.mkdir(parents=True, exist_ok=True)
-        with open(stdin, "rb") as vao, open(log, "wb") as ghi:
-            try:
-                n = khoi_chay(self.boc(argv), kill=self.kill, popen=self.popen, cwd=cwd, env=env, stdin=vao,
+        with open(stdin, "rb") as vao, open(log, "wb") as ghi, so_huu(LOI_DON, cho_term=self.cho_dung_giay) as chu:
+            try:                                            # sở hữu từ PID (`so_huu`): lỗi/ngắt trước khi thu hồi
+                n = khoi_chay(self.boc(argv), kill=self.kill, chu=chu, popen=self.popen, cwd=cwd, env=env, stdin=vao,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
             except OSError as e:
                 ghi.write(f"[tram] lỗi khởi chạy CLI: {type(e).__name__}\n".encode())
             else:
-                try:
-                    if self.khi_bat_dau:
-                        self.khi_bat_dau(n.p.pid)
-                    doc_t = threading.Thread(target=self._doc,
-                        args=(n.p, ghi, doc, dung, nguon, env.get("TRAM_MA_GIAO")), daemon=True)
-                    doc_t.start()
-                except BaseException:
-                    if not n.thu_hoi(cho_term=self.cho_dung_giay):
-                        raise LoiThuHoi("Không dọn được nhóm CLI; dừng khe để kiểm principal") from None
-                    raise
+                if self.khi_bat_dau:
+                    self.khi_bat_dau(n.p.pid)
+                doc_t = threading.Thread(target=self._doc,
+                                         args=(n.p, ghi, doc, dung, nguon, env.get("TRAM_MA_GIAO")), daemon=True)
+                doc_t.start()
                 ma, sach = cho_den_dung(n, dung, cho_term=self.cho_dung_giay)
                 doc_t.join(timeout=self.cho_dung_giay)
                 if not sach or doc_t.is_alive():
-                    raise LoiThuHoi("Không dọn được nhóm CLI; dừng khe để kiểm principal")
+                    raise LoiThuHoi(LOI_DON)
         digest = "sha256:" + hashlib.sha256(log.read_bytes()).hexdigest()
         return doc.ket_qua(ma_thoat=ma, bi_dung=dung.is_set(), thoi_gian_ms=int((time.monotonic() - t0) * 1000),
                            digest_log=digest)
```

Bản vá `tram/chay_cli/codex/app_server.py`:

```diff
--- a/tram/chay_cli/codex/app_server.py
+++ b/tram/chay_cli/codex/app_server.py
@@ -20,7 +20,8 @@
 
 from tram.chay_cli.codex.han_muc import han_muc_app_server
 from tram.han_muc.mo_hinh import HanMuc
-from tram.kiem.vong_doi import CHU_KY_CHUP, Kill, LoiThuHoi, khoi_chay, kill_cuc_bo
+from tram.kiem.so_huu import so_huu
+from tram.kiem.vong_doi import CHU_KY_CHUP, Kill, khoi_chay, kill_cuc_bo
 
 PHUONG_THUC = "account/rateLimits/read"
 CHU_KY_RANH_GIAY = 300
@@ -82,27 +83,27 @@
 
 def hoi_app_server(argv: list[str], *, env: dict[str, str], thoi_gian_cho: float = THOI_GIAN_CHO,
                    kill: Kill = kill_cuc_bo, khoi=khoi_chay) -> dict:
-    n = khoi(argv, kill=kill, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, env=env)
     han, dem = time.monotonic() + thoi_gian_cho, bytearray()
-    try:
-        _gui(n.p, {"method": "initialize", "id": 0, "params": {"clientInfo": {"name": "tram", "title": "Tram dieu phoi",
-                                                                               "version": "3b"}}})
-        _cho(n, 0, han, dem)
-        _gui(n.p, {"method": "initialized"})
-        _gui(n.p, {"method": PHUONG_THUC, "id": 1})
-        return _cho(n, 1, han, dem)
-    except _HetGio:
-        raise LoiAppServer(f"app-server không trả lời trong {thoi_gian_cho:g} giây") from None
-    except OSError as e:
-        raise LoiAppServer(f"app-server lỗi: {type(e).__name__}") from None
-    finally:
-        for f in (n.p.stdin, n.p.stdout):
-            try:
-                f.close()
-            except OSError:
-                pass
-        if not n.thu_hoi(cho_term=1.0, cho_cuoi=3.0, han_gui=2.0):
-            raise LoiThuHoi("không xác nhận thu hồi tiến trình app-server")
+    with so_huu("không xác nhận thu hồi tiến trình app-server", cho_term=1.0, cho_cuoi=3.0, han_gui=2.0) as chu:
+        n = khoi(argv, kill=kill, chu=chu, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
+                 env=env)                        # sở hữu từ PID (`so_huu`): mọi lối ra thu hồi cả cây, kể cả ngắt
+        try:
+            _gui(n.p, {"method": "initialize", "id": 0,
+                       "params": {"clientInfo": {"name": "tram", "title": "Tram dieu phoi", "version": "3b"}}})
+            _cho(n, 0, han, dem)
+            _gui(n.p, {"method": "initialized"})
+            _gui(n.p, {"method": PHUONG_THUC, "id": 1})
+            return _cho(n, 1, han, dem)
+        except _HetGio:
+            raise LoiAppServer(f"app-server không trả lời trong {thoi_gian_cho:g} giây") from None
+        except OSError as e:
+            raise LoiAppServer(f"app-server lỗi: {type(e).__name__}") from None
+        finally:
+            for f in (n.p.stdin, n.p.stdout):
+                try:
+                    f.close()
+                except OSError:
+                    pass
 
 
 def doc_han_muc_ranh(khe_id: str, thu_muc_cau_hinh: Path, *, bay_gio: datetime, principal, path: str,
```

Bản vá `tram/kiem/chay_gioi_han.py`:

```diff
--- a/tram/kiem/chay_gioi_han.py
+++ b/tram/kiem/chay_gioi_han.py
@@ -23,7 +23,7 @@
         input = input.encode()
     try:
         n = khoi(list(argv), kill=kill, stdin=subprocess.PIPE if input is not None else subprocess.DEVNULL,
-                 stdout=ong, stderr=ong, env=env, cwd=cwd)
+                 stdout=ong, stderr=ong, env=env, cwd=cwd, chu=[])     # Task 4: vùng sở hữu đầy đủ
     except OSError as e:
         raise OSError(f"{ten}: không khởi chạy được ({type(e).__name__})") from None
     het = time.monotonic() + timeout
```

Bản vá `tram/kiem/han_tong.py`:

```diff
--- a/tram/kiem/han_tong.py
+++ b/tram/kiem/han_tong.py
@@ -50,7 +50,7 @@
     except FileExistsError:
         raise LoiThuHoi(f"cổng đang đóng ({dau.name}): lượt trước chưa xác nhận dọn — không chạy") from None
     try:
-        n = khoi(argv, kill=kill, stdin=subprocess.DEVNULL, **kw)
+        n = khoi(argv, kill=kill, stdin=subprocess.DEVNULL, chu=[], **kw)     # Task 4: vùng sở hữu đầy đủ
     except OSError:
         n = None
     ma, sach, xong = None, False, False
```

- [ ] **Step 4: Chạy, thấy xanh** — `PT tests/test_giu_xac.py tests/test_so_huu.py tests/test_so_huu_ngat.py tests/test_so_huu_nguoi_goi.py` → `17 passed`; người gọi: `PT tests/test_vong_doi.py tests/test_vong_doi_ps.py tests/test_chay_lenh_p1.py tests/test_chay_lenh.py tests/test_chay_cli_vong_doi.py tests/test_han_tong.py tests/test_han_tong_ngat.py tests/test_danh_tinh.py tests/test_codex_app_server.py tests/test_chay_gioi_han.py tests/test_chay_claude.py tests/test_codex_chay.py tests/test_nhip_han_muc.py tests/test_han_muc_principal.py tests/test_lenh_nghiem_thu.py` → `101 passed`.

- [ ] **Step 5: Cả bộ** — `PT` → `2833 passed` (2809 + 7 của Task 1 + 17), nhật ký chặn 0 dòng mới.

- [ ] **Step 6: Commit** — `fix(kiem): giữ xác gốc, nhánh lỗi không gặt; một hợp đồng sở hữu từ PID cho mọi người gọi (V2-0, A03, R2-01, R2-02)`

## Task 3 — Cây theo định danh, mơ hồ đóng cổng, phạm vi gửi do chính lệnh gửi giới hạn (V2-0, dot7-C01; review vòng 1 A01)

**Files:** sửa `tram/kiem/cay_tien_trinh.py`, `tram/kiem/bang_tien_trinh.py` (thêm `van_o_nhom`), `tram/kiem/danh_tinh.py` (ảnh mặc định qua sysctl), `tram/kiem/gui_tin.py` (`GopKill`, `gop_kill`, `kill_uid`), `tram/kiem/han_tong.py` (`gop_kill` lấy từ `gui_tin`), `tram/kiem/vong_doi.py`, `tram/tho/cau_hinh.py` (cấm trùng `user:<tên>`); test mới `tests/test_vong_doi_tai_su_dung.py`, `tests/test_pham_vi_gui.py`; sửa `tests/test_cay_tien_trinh.py`, `tests/test_vong_doi.py`, `tests/test_vong_doi_ps.py`, `tests/test_han_tong.py`, `tests/test_chay_gioi_han.py`.

**Interfaces:**
- `cay(ds, goc: int | None, biet: set[(pid, sinh)])` — tham số thứ ba là **khoá định danh**; `mo_ho(ds, con, nhom_cu) -> list[TienTrinh]`; `van_o_nhom(ds, g, *, mot=mot_nhan) -> bool`.
- `Nhom(p, *, kill, chup=chup_nhan, mot=mot_nhan)`; thuộc tính `kill_uid`, `biet`, `nhom_biet` (chỉ để nhận ra mơ hồ), `mo_ho`. `CHU_KY_CHUP` 1,0 → 0,25 s (câu hỏi 3).
- **Phạm vi gửi (A01):** `Nhom._gui` gửi nhóm gốc chưa gặt qua `kill`; nhóm khác CHỈ qua `gui_tin.kill_uid(kill)` — `kill_nhom` (bound) của đối tượng có `co_che == "user"` (`tho.principal.Principal`, `giao_viec.principal_kiem.PrincipalKiem`), với `GopKill` là phần như vậy đầu tiên; None → nhóm ngoài gốc không bao giờ được gửi, còn sống thì `thu_hoi` False. `van_o_nhom` vẫn kiểm ngay trước khi gửi (bớt tín hiệu thừa), không còn là cơ sở an toàn.
- `gop_kill(*ds) -> GopKill` (dataclass gọi được, `.ds`); `han_tong.gop_kill` là cùng đối tượng (tên cũ cho `cong_lich`, `kiem_principal`, `lenh_nghiem_thu`).
- `nap_cau_hinh_tho`: hai khe cùng `user:<tên>` → `ValueError` (UID "dành riêng" phải riêng); `sandbox:` dùng chung là thiết kế, không chặn.
- **Đổi kỳ vọng test cũ (có chủ đích):** `test_vong_doi_ps.py` — ps lỗi KHÔNG còn gửi nhóm thấy ở ảnh trước; `test_cay_theo_ppid_va_nhom_da_biet` tách theo hợp đồng mới; các ca THẬT có cháu tách phiên (`test_vong_doi._chau`, `test_han_tong`, `test_chay_gioi_han`) gửi qua `KILL_UID` — principal `user` GIẢ mà "UID riêng" là chính user test; thêm ca thật ngược lại: kênh cục bộ không gửi nhóm ngoài gốc, cây không xác nhận. `test_vong_doi_tai_su_dung.thu` gửi qua kênh `user` giả. `test_kill_cham_nhieu_nhom…` dùng kênh `user` chậm (50 nhóm vẫn có hạn).

- [ ] **Step 1: Viết test**

Bản vá `tests/test_cay_tien_trinh.py`:

```diff
--- a/tests/test_cay_tien_trinh.py
+++ b/tests/test_cay_tien_trinh.py
@@ -5,7 +5,7 @@
 
 import pytest
 
-from tram.kiem.cay_tien_trinh import TienTrinh, cay, chup_he, doc_ps
+from tram.kiem.cay_tien_trinh import TienTrinh, cay, chup_he, doc_ps, mo_ho
 from tram.kiem.lenh_ngan import chay_ngan
 
 PS = (b"    0     0     0     0     0\n"
@@ -30,20 +30,28 @@
         doc_ps(PS + hong)
 
 
-def test_cay_theo_ppid_va_nhom_da_biet():
+def test_cay_theo_ppid_va_nhom_co_thanh_vien_da_chung_minh():
     ds = doc_ps(PS)
-    # gốc 600 còn sống: con 601 (nhóm mới, như pty của sudo), cháu 602 (phiên mới), 603 mồ côi nhưng cùng nhóm 601
-    assert [t.pid for t in cay(ds, 600, {600})] == [600, 601, 602, 603]
-    # gốc đã được gặt: chỉ còn đi theo nhóm đã biết (và con của chúng); 700 không thuộc cây
-    assert [t.pid for t in cay(ds, None, {601})] == [601, 602, 603]
-    assert cay(ds, None, set()) == []
-    assert 500 not in {t.pid for t in cay(ds, 600, {600})}
+    # gốc 600 còn sống: con 601 (nhóm mới, như pty của sudo), cháu 602 (phiên mới), 603 mồ côi nhưng cùng nhóm với 601
+    assert [t.pid for t in cay(ds, 600, set())] == [600, 601, 602, 603]
+    assert cay(ds, None, set()) == [] and 500 not in {t.pid for t in cay(ds, 600, set())}
+
+
+def test_cay_sau_khi_goc_gat_chi_theo_dinh_danh_da_thay():
+    ds = [TienTrinh(601, 1, 601, 502, 502, 11), TienTrinh(602, 601, 602, 502, 502, 12),
+          TienTrinh(603, 1, 601, 502, 502, 13), TienTrinh(700, 1, 700, 502, 502, 14)]
+    # 601 đã thấy (cùng sinh) → nó, con 602 và 603 cùng nhóm với nó; 700 không thuộc cây
+    assert [t.pid for t in cay(ds, None, {(601, 11)})] == [601, 602, 603]
+    # cùng số 601 nhưng sinh khác: lần sống khác — không nhận, kể cả 603 mang số nhóm đó
+    assert cay(ds, None, {(601, 99)}) == []
+    assert [t.pid for t in mo_ho(ds, [], {601})] == [601, 603]
+    assert mo_ho(ds, cay(ds, None, {(601, 11)}), {601, 0, 1}) == []
 
 
 def test_chup_he_doc_ps_that_thay_tien_trinh_con_cua_minh():
     p = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"], start_new_session=True)
     try:
-        con = cay(chup_he(), p.pid, {p.pid})
+        con = cay(chup_he(), p.pid, set())
         assert [t.pid for t in con] == [p.pid] and con[0].pgid == p.pid
     finally:
         p.kill()
```

Bản vá `tests/test_chay_gioi_han.py`:

```diff
--- a/tests/test_chay_gioi_han.py
+++ b/tests/test_chay_gioi_han.py
@@ -5,7 +5,7 @@
 
 import pytest
 
-from test_vong_doi import CHAU, SUDO, PopenGia, _song
+from test_vong_doi import CHAU, KILL_UID, SUDO, PopenGia, _song
 from tram.kiem.chay_gioi_han import chay_gioi_han
 from tram.kiem.vong_doi import LoiThuHoi, khoi_chay, kill_cuc_bo
 
@@ -40,7 +40,7 @@
 
 
 def test_chau_tu_tach_phien_khi_dang_chay_van_bi_thu_hoi(tmp_path):
-    chay_gioi_han([PY, "-c", CHAU.format(moi=True, ngu=1.5)], kill=kill_cuc_bo, timeout=20, cwd=tmp_path)
+    chay_gioi_han([PY, "-c", CHAU.format(moi=True, ngu=1.5)], kill=KILL_UID, timeout=20, cwd=tmp_path)
     assert not _song(int((tmp_path / "chau.pid").read_text()))
 
 
```

Bản vá `tests/test_han_tong.py`:

```diff
--- a/tests/test_han_tong.py
+++ b/tests/test_han_tong.py
@@ -7,6 +7,7 @@
 
 import pytest
 
+from test_vong_doi import KILL_UID
 from tram.kiem.han_tong import HetHanTong, chay_han_tong, cong_dong
 from tram.kiem.vong_doi import LoiThuHoi, khoi_chay, kill_cuc_bo
 
@@ -28,7 +29,7 @@
 def test_qua_han_thu_hoi_ca_chau_roi_don_va_mo_cong(tmp_path):
     don, dau, t0 = [], tmp_path / "cong" / "kiem.dong", time.monotonic()
     with pytest.raises(HetHanTong, match="đã thu hồi và dọn"):
-        chay_han_tong([PY, "-c", TREO], han=1.0, kill=kill_cuc_bo, dau=dau, don=lambda: don.append(1) or True,
+        chay_han_tong([PY, "-c", TREO], han=1.0, kill=KILL_UID, dau=dau, don=lambda: don.append(1) or True,
                       cwd=tmp_path)
     chau = int((tmp_path / "chau.pid").read_text())
     assert time.monotonic() - t0 < 10 and not _song(chau) and don == [1] and not cong_dong(dau)
```

Tạo mới `tests/test_pham_vi_gui.py` (nguyên văn):

```python
"""Review vòng 1 A01 (dot7-C01): kiểm rồi gửi KHÔNG nguyên tử, nên an toàn phải nằm Ở CHÍNH LỆNH GỬI. Nhóm gốc chưa gặt
(số không thể cấp lại) → mọi kênh; nhóm khác → CHỈ kênh chạy dưới UID dành riêng của principal `user` (nhân chỉ cho
trúng tiến trình của UID đó). `Nhan` là nhân GIẢ có UID: thay nhóm SAU lần kiểm cuối và GIỮA hai kênh gửi, rồi so toàn
bộ tín hiệu đã TRÚNG tiến trình. Không sudo/kill thật."""
import pytest

from test_vong_doi import PopenGia
from tram.giao_viec.principal_kiem import PrincipalKiem
from tram.kiem.cay_tien_trinh import TienTrinh
from tram.kiem.gui_tin import gop_kill, kill_cuc_bo, kill_uid
from tram.kiem.han_tong import gop_kill as gop_kill_cu
from tram.kiem.vong_doi import Nhom
from tram.tho.cau_hinh import nap_cau_hinh_tho
from tram.tho.principal import Principal

QUAN_LY, KHE = 501, 502
SUDO = TienTrinh(4242, 1, 4242, 0, QUAN_LY, 1)                       # gốc: sudo root, uid thực = quản lý
LA = TienTrinh(7000, 1, 5001, QUAN_LY, QUAN_LY, 70)                  # tiến trình của quản lý mang số nhóm vừa cấp lại


class Nhan:
    """`kill(uid)(g, sig)` chỉ TRÚNG tiến trình nhóm g có uid thực = uid gửi (cansignal của macOS, không root)."""
    def __init__(self, *bang, sau_kiem=None):
        self.bang, self.sau_kiem, self.trung, self.goi = list(bang), sau_kiem, [], []

    def chup(self):
        return list(self.bang)

    def mot(self, pid):
        t = next((t for t in self.bang if t.pid == pid), None)
        if self.sau_kiem is not None:                                 # thay nhóm NGAY SAU lần kiểm cuối
            f, self.sau_kiem = self.sau_kiem, None
            f(self)
        return t

    def kill(self, uid):
        def gui(g, sig):
            self.goi.append((uid, g, sig))
            self.trung += [(t.pid, sig) for t in self.bang if t.pgid == g and t.ruid == uid]
        return gui


class PrGia:
    """Principal GIẢ: `kill_nhom` chạy dưới UID của nó (như `sudo -n -u … /bin/kill`)."""
    def __init__(self, nhan, uid, co_che="user", sau_gui=None):
        self.nhan, self.uid, self.co_che, self.sau_gui = nhan, uid, co_che, sau_gui

    def kill_nhom(self, g, sig):
        self.nhan.kill(self.uid)(g, sig)
        if self.sau_gui is not None:
            self.sau_gui(g)


def thu_hoi(nh, kill):
    n = Nhom(PopenGia(), kill=kill, chup=nh.chup, mot=nh.mot)
    n.cay()
    return n.thu_hoi(cho_term=0, cho_cuoi=0, han_gui=1)


def cap_lai(nh):
    nh.bang = [t for t in nh.bang if t.pid != 5001] + [LA]


def test_nhom_cap_lai_sau_lan_kiem_cuoi_khong_trung_ai_ngoai_uid_khe():
    nh = Nhan(SUDO, TienTrinh(5001, 4242, 5001, KHE, KHE, 11), sau_kiem=cap_lai)
    thu_hoi(nh, gop_kill(PrGia(nh, KHE).kill_nhom, nh.kill(QUAN_LY)))
    assert 7000 not in {pid for pid, _ in nh.trung}
    assert {g for uid, g, _ in nh.goi if uid == QUAN_LY} == {4242}             # cục bộ: chỉ nhóm gốc chưa gặt


def test_nhom_cap_lai_giua_hai_kenh_gui_khong_trung_ai_ngoai_uid_khe():
    nh = Nhan(SUDO, TienTrinh(5001, 4242, 5001, KHE, KHE, 11))
    pr = PrGia(nh, KHE, sau_gui=lambda g: cap_lai(nh) if g == 5001 else None)
    thu_hoi(nh, gop_kill(pr.kill_nhom, nh.kill(QUAN_LY)))
    assert (5001, 15) in nh.trung and 7000 not in {pid for pid, _ in nh.trung}
    assert {g for uid, g, _ in nh.goi if uid == QUAN_LY} == {4242}


@pytest.mark.parametrize("kenh", ["cuc-bo", "sandbox"])
def test_khong_co_kenh_theo_uid_rieng_thi_chi_gui_nhom_goc_va_khong_xac_nhan(kenh):
    nh = Nhan(SUDO, TienTrinh(5001, 4242, 5001, KHE, KHE, 11))
    kill = nh.kill(QUAN_LY) if kenh == "cuc-bo" else PrGia(nh, KHE, co_che="sandbox").kill_nhom
    assert thu_hoi(nh, kill) is False and {g for _, g, _ in nh.goi} == {4242}


def test_nhan_ra_kenh_theo_uid_rieng():
    u, s = Principal("user", "tram-k-1"), Principal("sandbox", "tram-exec")
    pk = PrincipalKiem("tram-kiem", ("/usr/bin/sudo",))
    assert kill_uid(u.kill_nhom) == u.kill_nhom and kill_uid(pk.kill_nhom) == pk.kill_nhom
    assert kill_uid(gop_kill(u.kill_nhom, kill_cuc_bo)) == u.kill_nhom and gop_kill_cu is gop_kill
    assert kill_uid(s.kill_nhom) is None and kill_uid(kill_cuc_bo) is None and kill_uid(u.boc) is None
    assert kill_uid(PrincipalKiem("tram-exec", (), "sandbox").kill_nhom) is None


def test_principal_user_phai_rieng_tung_khe(tmp_path):
    khe = ("  - {{ten: k{i}, cli: claude, principal: '{p}', thu_muc_cau_hinh: /x/{i}, ten_goi_nho: K{i}, "
           "vai_uu_tien: [coder]}}\n")
    yaml = "may_id: B\ntram_api: http://127.0.0.1:7700\nkhe:\n"
    (tmp_path / "a.yaml").write_text(yaml + khe.format(i=1, p="user:tram-k") + khe.format(i=2, p="user:tram-k"))
    with pytest.raises(ValueError, match="riêng"):
        nap_cau_hinh_tho(tmp_path / "a.yaml")
    sb = "sandbox:tram-exec"                                         # cơ chế sandbox: user dùng chung là thiết kế
    (tmp_path / "b.yaml").write_text(yaml + khe.format(i=1, p=sb) + khe.format(i=2, p=sb))
    assert len(nap_cau_hinh_tho(tmp_path / "b.yaml").khe) == 2
```

Bản vá `tests/test_vong_doi.py`:

```diff
--- a/tests/test_vong_doi.py
+++ b/tests/test_vong_doi.py
@@ -1,5 +1,6 @@
 """Primitive vòng đời tiến trình (lát P1): hạn hữu hạn, thu hồi cả cây. Tiến trình thật chỉ là `python -c` của chính
-user đang test, trong tmp_path, tự thu hồi; ca sudo/root/kill bị từ chối dùng Popen/ps/kill GIẢ."""
+user đang test, trong tmp_path, tự thu hồi; ca sudo/root/kill bị từ chối dùng Popen/ps/kill GIẢ. Nhóm ngoài gốc chỉ được
+gửi qua kênh theo UID dành riêng (A01): ca thật dùng `KILL_UID` — principal `user` GIẢ, UID riêng = chính user test."""
 import os
 import signal
 import subprocess
@@ -19,6 +20,17 @@
         "open('chau.pid', 'w').write(str(c.pid)); time.sleep({ngu})\n")
 
 
+class PrCungUser:
+    """Principal cơ chế `user` GIẢ: trong test "UID dành riêng" là chính user đang test (`gui_tin.kill_uid` nhận nó)."""
+    co_che = "user"
+
+    def kill_nhom(self, pgid, sig):
+        kill_cuc_bo(pgid, sig)
+
+
+KILL_UID = PrCungUser().kill_nhom
+
+
 class PopenGia:
     """Gốc không bao giờ thoát (vd. `sudo` root không nhận tín hiệu của tiến trình quản lý)."""
     pid, returncode = 4242, None
@@ -39,8 +51,8 @@
     return True
 
 
-def _chau(tmp_path, *, moi: bool, ngu: float):
-    n = khoi_chay([PY, "-c", CHAU.format(moi=moi, ngu=ngu)], kill=kill_cuc_bo, chu=[], cwd=tmp_path)
+def _chau(tmp_path, *, moi: bool, ngu: float, kill=KILL_UID):
+    n = khoi_chay([PY, "-c", CHAU.format(moi=moi, ngu=ngu)], kill=kill, chu=[], cwd=tmp_path)
     het = time.monotonic() + 10
     while not (tmp_path / "chau.pid").exists() and time.monotonic() < het:
         time.sleep(0.02)
@@ -61,16 +73,18 @@
 
 
 def test_kill_cham_nhieu_nhom_moi_pha_van_gui_va_co_han():
-    cay = [SUDO, *(TienTrinh(5000 + i, 4242, 5000 + i, 502, 502) for i in range(50))]
+    cay = [SUDO, *(TienTrinh(5000 + i, 4242, 5000 + i, 502, 502, 7 + i) for i in range(50))]
     gui = []
 
-    def kill(g, sig):
-        gui.append(sig)
-        time.sleep(0.1)
-        raise subprocess.TimeoutExpired(["kill"], 0.1)
-    t0 = time.monotonic()
-    assert Nhom(PopenGia(), kill=kill, chup=lambda: cay).thu_hoi(cho_term=0.1, cho_cuoi=0.1, han_gui=0.3) is False
-    assert time.monotonic() - t0 < 2 and signal.SIGKILL in gui and len(gui) < 20
+    class Cham(PrCungUser):
+        def kill_nhom(self, g, sig):
+            gui.append(sig)
+            time.sleep(0.1)
+            raise subprocess.TimeoutExpired(["kill"], 0.1)
+    t0, mot = time.monotonic(), lambda pid: next((t for t in cay if t.pid == pid), None)
+    assert Nhom(PopenGia(), kill=Cham().kill_nhom, chup=lambda: cay, mot=mot).thu_hoi(cho_term=0.1, cho_cuoi=0.1,
+                                                                                       han_gui=0.3) is False
+    assert time.monotonic() - t0 < 2 and signal.SIGKILL in gui and 2 < len(gui) < 20
 
 
 def test_da_thoat_cay_rong_khong_gui_gi():
@@ -94,6 +108,17 @@
             os.kill(chau, signal.SIGKILL)
 
 
+def test_kenh_cuc_bo_khong_gui_nhom_ngoai_goc_chau_tach_phien_thi_khong_xac_nhan(tmp_path):
+    """A01: kênh cục bộ (tài khoản quản lý/trạm chạy nhiều việc khác) không bao giờ gửi nhóm ngoài gốc."""
+    n, chau = _chau(tmp_path, moi=True, ngu=60, kill=kill_cuc_bo)
+    try:
+        assert n.cho(0.3) is None and n.thu_hoi(cho_term=0.2, cho_cuoi=0.5) is False and _song(chau)
+    finally:
+        kill_cuc_bo(n.p.pid, signal.SIGKILL)
+        if _song(chau):
+            os.kill(chau, signal.SIGKILL)
+
+
 def test_khoi_chay_luon_nhom_rieng():
     goi = []
 
```

Bản vá `tests/test_vong_doi_ps.py`:

```diff
--- a/tests/test_vong_doi_ps.py
+++ b/tests/test_vong_doi_ps.py
@@ -1,5 +1,5 @@
-"""Primitive P1 khi `ps` lỗi: vẫn gửi nhóm thấy trong ảnh chụp thành công GẦN (≤ 2 s); ảnh chụp cũ hơn → chỉ nhóm gốc
-chưa gặt (số nhóm đã chết có thể bị tái dùng). Popen/ps/kill GIẢ."""
+"""Primitive P1 khi không chụp được bảng tiến trình LÚC GỬI (V2-0): không dùng ảnh cũ làm bằng chứng — chỉ nhóm gốc
+chưa gặt (số chưa thể cấp lại) được gửi, kết quả không xác nhận. Popen/bảng/kill GIẢ."""
 import signal
 
 from test_vong_doi import SUDO, PopenGia
@@ -7,28 +7,27 @@
 from tram.kiem.vong_doi import Nhom
 
 
-def test_ps_loi_van_gui_nhom_thay_lan_truoc_va_khong_xac_nhan():
-    gui, lan = [], []
+def _chup_hong_tu_lan(k):
+    lan = []
 
     def chup():
         lan.append(1)
-        if len(lan) > 1:
+        if len(lan) >= k:
             raise OSError("ps")
-        return [SUDO, TienTrinh(5000, 4242, 5000, 502, 502)]
-    n = Nhom(PopenGia(), kill=lambda g, s: gui.append((g, s)), chup=chup)
-    assert n.thu_hoi(cho_term=0.1, cho_cuoi=0.1, han_gui=0.1) is False
-    assert (5000, signal.SIGKILL) in gui and (4242, signal.SIGKILL) in gui
+        return [SUDO, TienTrinh(5000, 4242, 5000, 502, 502, 11)]
+    return chup
 
 
-def test_ps_loi_lau_thi_chi_gui_nhom_goc():
-    gui, lan = [], []
+def test_khong_chup_duoc_luc_gui_chi_gui_nhom_goc_va_khong_xac_nhan():
+    gui = []
+    n = Nhom(PopenGia(), kill=lambda g, s: gui.append((g, s)), chup=_chup_hong_tu_lan(2), mot=lambda pid: None)
+    n.cay()
+    assert n.thu_hoi(cho_term=0.1, cho_cuoi=0.1, han_gui=0.1) is False
+    assert gui == [(4242, signal.SIGTERM), (4242, signal.SIGKILL)]
 
-    def chup():
-        lan.append(1)
-        if len(lan) > 1:
-            raise OSError("ps")
-        return [SUDO, TienTrinh(5000, 4242, 5000, 502, 502)]
-    n = Nhom(PopenGia(), kill=lambda g, s: gui.append(g), chup=chup)
+
+def test_anh_cu_khong_con_la_bang_chung_du_vua_chup():
+    gui = []
+    n = Nhom(PopenGia(), kill=lambda g, s: gui.append(g), chup=_chup_hong_tu_lan(3), mot=lambda pid: None)
     n.cay()
-    n.lan_dung -= 10                                     # ảnh chụp thành công gần nhất đã cũ: nhóm 5000 có thể tái dùng
     assert n.thu_hoi(cho_term=0.1, cho_cuoi=0.1, han_gui=0.1) is False and set(gui) == {4242}
```

Tạo mới `tests/test_vong_doi_tai_su_dung.py` (nguyên văn):

```python
"""V2-0 (dot7-C01): thu hồi KHÔNG BAO GIỜ gửi tín hiệu cho nhóm không chứng minh được thuộc cây — số nhóm/PID có thể
được cấp lại giữa hai ảnh chụp. Popen/bảng tiến trình/kill GIẢ; mỗi ca so ĐÚNG tập nhóm đã nhận tín hiệu."""
import os

from test_vong_doi import SUDO, PopenGia
from tram.kiem.cay_tien_trinh import TienTrinh
from tram.kiem.vong_doi import Nhom


class PopenXong(PopenGia):
    """Gốc đã được gặt (mã 0) — số 4242 có thể đã được cấp lại."""
    returncode = 0

    def poll(self):
        return 0


def con(pid, ppid=4242, pgid=None, sinh=None):
    return TienTrinh(pid, ppid, pid if pgid is None else pgid, 502, 502, sinh)


class May:
    """`chup` trả lần lượt các ảnh (ảnh cuối lặp lại; Exception thì ném); `mot` đọc ảnh vừa trả, hoặc `doi` — mô phỏng
    thay đổi GIỮA ảnh chụp và lúc gửi."""
    def __init__(self, *anh, doi=None):
        self.anh, self.i, self.doi, self.hien = list(anh), 0, doi, []

    def chup(self):
        a = self.anh[min(self.i, len(self.anh) - 1)]
        self.i += 1
        if isinstance(a, Exception):
            raise a
        self.hien = a
        return list(a)

    def mot(self, pid):
        if isinstance(self.doi, Exception):
            raise self.doi
        return next((t for t in (self.hien if self.doi is None else self.doi) if t.pid == pid), None)


class Gui:
    """Kênh gửi GIẢ chạy dưới UID dành riêng (principal `user`) — ghi lại mọi nhóm được gửi."""
    co_che = "user"

    def __init__(self):
        self.da = []

    def kill_nhom(self, g, s):
        self.da.append(g)


def thu(may, goc=None):
    gui = Gui()
    n = Nhom(goc or PopenGia(), kill=gui.kill_nhom, chup=may.chup, mot=may.mot)
    n.cay()
    return n.thu_hoi(cho_term=0, cho_cuoi=0, han_gui=1), set(gui.da)


def test_nhom_tai_su_dung_khong_duoc_kill():
    gui = []
    cu = [SUDO, TienTrinh(5000, 4242, 5000, 502, 502)]
    moi = [SUDO, TienTrinh(5000, 1, 5000, 502, 502)]
    anh = iter([cu, moi])
    n = Nhom(PopenGia(), kill=lambda g, s: gui.append(g),
             chup=lambda: next(anh, moi))
    n.cay()
    assert n.thu_hoi(cho_term=0, cho_cuoi=0, han_gui=1) is False
    assert 5000 not in gui


def test_cung_so_cung_uid_sinh_khac_khong_nhan():
    assert thu(May([SUDO, con(5000, sinh=11)], [SUDO, con(5000, ppid=1, sinh=22)])) == (False, {4242})


def test_mo_coi_da_thay_doi_nhom_van_theo_no_so_nhom_cu_thi_mo_ho():
    # 5001 đã thấy; cha chết (ppid=1), nó sang nhóm 6000. Nhóm cũ 5001 giờ có 5002 lạ → mơ hồ: không gửi, không xác nhận
    may = May([SUDO, con(5001, sinh=11)],
              [SUDO, con(5001, ppid=1, pgid=6000, sinh=11), con(5002, ppid=1, pgid=5001, sinh=12), con(5000, ppid=1)])
    assert thu(may) == (False, {4242, 6000})


def test_mo_coi_hop_le_cung_sinh_van_bi_gui():
    assert thu(May([SUDO, con(5001, sinh=11)], [SUDO, con(5001, ppid=1, sinh=11)])) == (False, {4242, 5001})


def test_khong_chup_duoc_luc_gui_chi_nhom_goc_chua_gat():
    assert thu(May([SUDO, con(5001, sinh=11)], OSError("sysctl"))) == (False, {4242})
    assert thu(May([con(5001, ppid=1, sinh=11)], OSError("sysctl")), PopenXong()) == (False, set())


def test_goc_da_gat_cay_rong_thi_xac_nhan_khong_gui_gi():
    assert thu(May([]), PopenXong()) == (True, set())


def test_goc_da_gat_tien_trinh_mang_so_nhom_goc_la_mo_ho():
    # fork rồi cha thoát TRƯỚC ảnh đầu, người khác đã gặt gốc: số 4242 có thể đã cấp lại → không gửi, không xác nhận
    assert thu(May([con(7000, ppid=1, pgid=4242, sinh=5)]), PopenXong()) == (False, set())


def test_fork_setsid_truoc_anh_dau_nhom_khong_thay_duoc_khong_gui():
    # GIỚI HẠN của MỘT `Nhom` (polling): tách phiên + cha thoát trước ảnh đầu → không thấy, không gửi gì; True ở đây chỉ
    # nghĩa "cây QUAN SÁT ĐƯỢC đã hết". Khe thợ không dừng ở đây: `tho.don_uid` quét toàn UID của khe trước khi sang
    # lượt sau (test_don_uid.py, test_khe_tan_du.py); `tram-kiem` có `cong_that.thu_hoi_theo_uid`.
    assert thu(May([con(8000, ppid=1, sinh=7)]), PopenXong()) == (True, set())


def test_khong_bao_gio_gui_nhom_0_1_va_nhom_cua_quan_ly():
    ql = os.getpgrp()
    may = May([SUDO, con(5001, pgid=0, sinh=1), con(5002, pgid=1, sinh=2), con(5003, pgid=ql, sinh=3)])
    assert thu(may) == (False, {4242})


def test_neo_doi_giua_anh_va_luc_gui_thi_khong_gui():
    truoc = [SUDO, con(5001, sinh=11)]
    assert thu(May(truoc, doi=[SUDO, con(5001, ppid=1, sinh=99)])) == (False, {4242})      # số 5001 đã cấp lại
    assert thu(May(truoc, doi=[SUDO, con(5001, pgid=6000, sinh=11)])) == (False, {4242})   # neo rời nhóm 5001
    assert thu(May(truoc, doi=OSError("sysctl"))) == (False, {4242})                      # không kiểm lại được


def test_neo_dau_da_chet_thanh_vien_khac_con_thi_van_gui():
    may = May([SUDO, con(5001, sinh=11), con(5002, pgid=5001, sinh=12)], doi=[SUDO, con(5002, pgid=5001, sinh=12)])
    assert thu(may) == (False, {4242, 5001})
```

- [ ] **Step 2: Chạy, thấy đỏ** — `PT tests/test_cay_tien_trinh.py`, `PT tests/test_pham_vi_gui.py`, rồi `PT tests/test_vong_doi_tai_su_dung.py tests/test_vong_doi_ps.py tests/test_vong_doi.py tests/test_han_tong.py tests/test_chay_gioi_han.py`. Kết quả thật (mã của Task 2; chạy lại trên `f4fa3a8`, khớp bản trước):

```
E   ImportError: cannot import name 'mo_ho' from 'tram.kiem.cay_tien_trinh'
1 error in 0.06s
---
E   ImportError: cannot import name 'gop_kill' from 'tram.kiem.gui_tin'
1 error in 0.07s
---
E       assert 5000 not in [4242, 5000, 4242, 5000]
E       TypeError: Nhom.__init__() got an unexpected keyword argument 'mot'      (13 lần)
E           assert (None is None and True is False)        ← kênh cục bộ vẫn gửi nhóm của cháu tách phiên
FAILED tests/test_vong_doi_tai_su_dung.py::…   (11 ca)
FAILED tests/test_vong_doi_ps.py::…            (2 ca)
FAILED tests/test_vong_doi.py::test_kill_cham_nhieu_nhom_moi_pha_van_gui_va_co_han
FAILED tests/test_vong_doi.py::test_kenh_cuc_bo_khong_gui_nhom_ngoai_goc_chau_tach_phien_thi_khong_xac_nhan
15 failed, 21 passed in 20.25s
```

**Đối chứng thiết kế vòng trước (đột biến thật, 18/10):** ở mã sau Task 3, đổi `Nhom._gui` về cách của bản trước (kiểm `van_o_nhom` rồi gửi MỌI nhóm qua `kill` gộp) và chạy `PT tests/test_pham_vi_gui.py`:

```
E       assert 7000 not in {4242, 7000}                                   ← cấp lại SAU lần kiểm cuối: trúng 7000
E       assert ((5001, 15) in [(4242, …15), (5001, …15), (7000, …15), (4242, …9)] and 7000 not in {4242, 5001, 7000})
                                                                          ← cấp lại GIỮA hai kênh: kênh cục bộ trúng 7000
E       assert (False is False and {4242, 5001} == {4242}                 (cuc-bo, sandbox: gửi nhóm ngoài gốc)
4 failed, 2 passed in 0.06s
```

- [ ] **Step 3: Mã**

Bản vá `tram/kiem/bang_tien_trinh.py`:

```diff
--- a/tram/kiem/bang_tien_trinh.py
+++ b/tram/kiem/bang_tien_trinh.py
@@ -74,6 +74,19 @@
     return ds[0] if ds else None
 
 
+def van_o_nhom(ds: list[TienTrinh], g: int, *, mot: Callable[[int], TienTrinh | None] = mot_nhan) -> bool:
+    """Một thành viên đã thấy vẫn là ĐÚNG lần sống đó và vẫn ở `g` tại lúc đọc. Đây chỉ là kiểm tra để giảm tín hiệu
+    thừa, không nguyên tử với lúc gửi; phạm vi gửi do `kill_uid` giới hạn (A01). Lỗi đọc → False."""
+    for t in ds:
+        try:
+            moi = mot(t.pid)
+        except (OSError, ValueError):
+            return False
+        if t.khoa is not None and moi is not None and moi.khoa == t.khoa and moi.pgid == g:
+            return True
+    return False
+
+
 def phien_khoi_dong() -> str:
     """`kern.bootsessionuuid` — đổi sau mỗi lần khởi động máy; pid/sinh của phiên khác không còn tiến trình nào."""
     n = ctypes.c_size_t(64)
```

Bản vá `tram/kiem/cay_tien_trinh.py`:

```diff
--- a/tram/kiem/cay_tien_trinh.py
+++ b/tram/kiem/cay_tien_trinh.py
@@ -2,9 +2,11 @@
 của MỌI tiến trình trên macOS, không cần sudo, không gửi tín hiệu. `uid` là UID HIỆU LỰC nhân ghi cho tiến trình,
 không phải tên trong env. CHỈ lấy cột số (không `comm`): tên chương trình do agent đặt được, có thể chứa xuống dòng để
 giả một dòng `ps` — dòng nào không đúng 5 số nguyên không âm làm cả ảnh chụp hỏng (người gọi coi như không xác nhận).
-Cây của một lần chạy = gốc (khi chưa gặt) + mọi tiến trình có cha trong cây hoặc thuộc một nhóm đã biết của cây — gồm
-cả con mà `sudo` đặt vào nhóm/phiên mới (pty). Tiến trình đã rời cả cây lẫn mọi nhóm đã biết GIỮA hai lần chụp (fork +
-setsid rồi cha thoát trong < 1 s) không thấy được: đó là ranh giới cách ly C01/3C-A, không phải lời hứa của P1."""
+Cây của một lần chạy (V2-0, dot7-C01): gốc chưa gặt + con theo ppid + tiến trình ĐÃ THẤY là thành viên (cùng khoá
+(pid, sinh)) + mọi tiến trình cùng NHÓM với một thành viên đã chứng minh trong CHÍNH ảnh đó. Số nhóm của ảnh cũ KHÔNG
+còn là bằng chứng: nhóm có thể đã chết và số được cấp lại. Ai mang số nhóm cũ mà không chứng minh được → `mo_ho`.
+Tiến trình rời cây (fork + setsid rồi cha thoát) GIỮA hai lần chụp không thấy được: ranh giới C01/3C-A, không phải lời
+hứa của P1 — chỉ quét theo UID dành riêng (`tram-kiem`) bắt được."""
 from collections.abc import Callable, Iterable
 from dataclasses import dataclass
 
@@ -47,14 +49,23 @@
     return doc_ps(ra)
 
 
-def cay(ds: Iterable[TienTrinh], goc: int | None, nhom: set[int]) -> list[TienTrinh]:
-    ds, pids, nhom = list(ds), set(), set(nhom)
+def cay(ds: Iterable[TienTrinh], goc: int | None, biet: set[tuple[int, int]]) -> list[TienTrinh]:
+    """Cây trong MỘT ảnh chụp. Cùng nhóm với thành viên đã chứng minh ⇒ cùng phiên; phiên chỉ thừa kế qua fork, mà
+    phiên của thành viên do chính cây tạo (gốc luôn `start_new_session`) — nên ai cùng nhóm cũng là hậu duệ."""
+    ds, pids, nhom = list(ds), set(), set()
     doi = True
     while doi:
         doi = False
         for t in ds:
-            if t.pid not in pids and (t.pid == goc or t.ppid in pids or t.pgid in nhom):
+            if t.pid not in pids and (t.pid == goc or t.ppid in pids or t.khoa in biet or t.pgid in nhom):
                 pids.add(t.pid)
-                nhom.add(t.pgid)
+                nhom |= {t.pgid} - {0, 1}
                 doi = True
     return [t for t in ds if t.pid in pids]
+
+
+def mo_ho(ds: Iterable[TienTrinh], con: list[TienTrinh], nhom_cu: set[int]) -> list[TienTrinh]:
+    """Mang số nhóm cây từng có nhưng KHÔNG chứng minh được thuộc cây: mồ côi chưa từng thấy, hoặc nhóm khác được cấp
+    lại cùng số. Không đoán — không gửi tín hiệu, thu hồi coi là chưa xác nhận."""
+    trong = {t.pid for t in con}
+    return [t for t in ds if t.pid not in trong and t.pgid in nhom_cu - {0, 1}]
```

Bản vá `tram/kiem/danh_tinh.py`:

```diff
--- a/tram/kiem/danh_tinh.py
+++ b/tram/kiem/danh_tinh.py
@@ -11,7 +11,8 @@
 import time
 from collections.abc import Callable
 
-from tram.kiem.cay_tien_trinh import TienTrinh, chup_he
+from tram.kiem.bang_tien_trinh import chup_nhan
+from tram.kiem.cay_tien_trinh import TienTrinh
 from tram.kiem.so_huu import so_huu
 from tram.kiem.vong_doi import Kill, khoi_chay
 
@@ -28,7 +29,7 @@
 
 
 def quan_sat(boc: Callable[[list[str]], list[str]], kill: Kill, *, khoi: Callable = khoi_chay,
-             chup: Callable[[], list[TienTrinh]] = chup_he, han: float = 10.0) -> list[TienTrinh]:
+             chup: Callable[[], list[TienTrinh]] = chup_nhan, han: float = 10.0) -> list[TienTrinh]:
     """Cây của tiến trình dò lúc mọi lá đã rời UID root. Sở hữu theo `so_huu` (R2-02): spawn trong khối sở hữu."""
     with so_huu("không xác nhận thu hồi tiến trình dò", cho_term=1.0, cho_cuoi=1.0, han_gui=2.0) as chu:
         try:
```

Thay TOÀN BỘ `tram/kiem/gui_tin.py` bằng (nguyên văn):

```python
"""Gửi tín hiệu cho nhóm tiến trình (P1; V2-0 — review vòng 1 A01). Kiểm "nhóm còn là của cây" rồi mới gửi KHÔNG
nguyên tử (thành viên cuối chết, số được cấp lại giữa hai bước — kể cả giữa hai kênh của `gop_kill`), nên phạm vi phải
do CHÍNH lệnh gửi giới hạn:
- `kill_cuc_bo` gửi dưới user của chính tiến trình này (quản lý/trạm chạy nhiều việc khác) → chỉ hợp lệ cho nhóm gốc
  CHƯA GẶT (số không thể cấp lại) hoặc khi mọi tiến trình là của chính user (test).
- `kill_uid(kill)`: phần của `kill` chạy DƯỚI UID DÀNH RIÊNG — `kill_nhom` của principal cơ chế `user`: `Principal` của
  khe (D53: mỗi khe một tài khoản macOS, `tho.yaml` cấm trùng) hay `PrincipalKiem` (`tram-kiem`). Nhân macOS chỉ cho
  user thường gửi tới tiến trình có UID thực/UID lưu = UID của mình, nên số nhóm có bị cấp lại cho tài khoản khác thì
  lệnh gửi cũng không trúng; trúng tiến trình khác CÙNG UID thì đó vẫn là việc của khe/`tram-kiem`. Cơ chế `sandbox`
  (một user dùng chung nhiều khe) và kênh cục bộ KHÔNG phải kênh theo UID.
- `gop_kill(*ds)` → `GopKill`: gửi lần lượt từng kênh (cây harness có tiến trình của quản lý lẫn principal); `Nhom` chỉ
  dùng nó cho nhóm gốc chưa gặt, nhóm khác đi qua `kill_uid(GopKill)` = phần theo UID đầu tiên."""
import os
import subprocess
from collections.abc import Callable
from dataclasses import dataclass

Kill = Callable[[int, int], None]
LOI_GUI = (OSError, subprocess.SubprocessError)


def kill_cuc_bo(pgid: int, sig: int) -> None:
    try:
        os.killpg(pgid, sig)
    except (ProcessLookupError, PermissionError):
        pass


@dataclass(frozen=True)
class GopKill:
    ds: tuple[Kill, ...]

    def __call__(self, pgid: int, sig: int) -> None:
        for k in self.ds:
            try:
                k(pgid, sig)
            except LOI_GUI:
                pass


def gop_kill(*ds: Kill) -> GopKill:
    return GopKill(ds)


def kill_uid(kill: Kill) -> Kill | None:
    if isinstance(kill, GopKill):
        return next((k for k in map(kill_uid, kill.ds) if k is not None), None)
    chu, ham = getattr(kill, "__self__", None), getattr(kill, "__func__", None)
    return kill if getattr(ham, "__name__", None) == "kill_nhom" and getattr(chu, "co_che", None) == "user" else None
```

Bản vá `tram/kiem/han_tong.py`:

```diff
--- a/tram/kiem/han_tong.py
+++ b/tram/kiem/han_tong.py
@@ -9,18 +9,8 @@
 from collections.abc import Callable
 from pathlib import Path
 
-from tram.kiem.vong_doi import LOI_GUI, Kill, LoiThuHoi, khoi_chay
-
-
-def gop_kill(*ds: Kill) -> Kill:
-    """Gửi lần lượt qua từng cách (principal rồi cục bộ) — cây harness có cả tiến trình của quản lý lẫn principal."""
-    def kill(pgid: int, sig: int) -> None:
-        for k in ds:
-            try:
-                k(pgid, sig)
-            except LOI_GUI:
-                pass
-    return kill
+from tram.kiem.gui_tin import gop_kill  # noqa: F401 — tên cũ; định nghĩa và phạm vi gửi ở `gui_tin` (A01)
+from tram.kiem.vong_doi import Kill, LoiThuHoi, khoi_chay
 
 
 class HetHanTong(LoiThuHoi):
```

Bản vá `tram/kiem/vong_doi.py`:

```diff
--- a/tram/kiem/vong_doi.py
+++ b/tram/kiem/vong_doi.py
@@ -1,10 +1,8 @@
-"""Vòng đời MỘT tiến trình con có hạn hữu hạn (P1, dot6-C02/Q02) — primitive DUY NHẤT cho mọi chỗ spawn rồi chờ/giết.
-`khoi_chay` LUÔN `start_new_session` (không terminal điều khiển); hợp đồng sở hữu từ lúc có PID ở `so_huu` (A03,
-R2-02). `cho` chụp cây mỗi `CHU_KY_CHUP` giây và biết gốc thoát mà KHÔNG gặt (`giu_xac.Goc`, V2-0) — xác giữ số
-nhóm gốc. `thu_hoi` có hạn: SIGTERM → `cho_term` → SIGKILL → `cho_cuoi`, mỗi pha qua `kill(pgid, sig)` của người gọi,
-thôi gửi khi pha quá `han_gui`; chỉ nhóm THẤY CÒN SỐNG trong ảnh ≤ 2 s trước và nhóm gốc chưa gặt (không nhóm 0/1/của
-quản lý). True CHỈ khi gốc đã thoát, cây chỉ còn xác gốc — rồi mới gặt. Treo sau SIGKILL → False, cổng giữ đóng.
-Cận trên: cho_term + cho_cuoi + 2 × (han_gui + một lần `kill`) + 3 lần chụp bảng tiến trình."""
+"""Vòng đời MỘT tiến trình con có hạn (P1): primitive DUY NHẤT spawn rồi chờ/giết; `khoi_chay` LUÔN `start_new_session`,
+sở hữu từ PID theo `so_huu` (A03, R2-02). `cho` chụp cây theo định danh (pid, sinh) mỗi `CHU_KY_CHUP` giây, biết gốc
+thoát mà KHÔNG gặt (`giu_xac`). `thu_hoi`: SIGTERM → `cho_term` → SIGKILL → `cho_cuoi`, mỗi pha chụp mới; nhóm gốc
+chưa gặt qua `kill`, nhóm khác CHỈ qua `kill_uid(kill)` sau `van_o_nhom` (`gui_tin`, A01). True = cây QUAN SÁT ĐƯỢC
+đã hết, không mơ hồ — rồi mới gặt; KHÔNG chứng minh hết tàn dư lẩn khỏi tầm chụp (khe thợ: `tho.don_uid`, A02)."""
 import math
 import os
 import signal
@@ -12,12 +10,13 @@
 import time
 from collections.abc import Callable
 
-from tram.kiem.cay_tien_trinh import TienTrinh, cay, chup_he
+from tram.kiem.bang_tien_trinh import chup_nhan, mot_nhan, van_o_nhom
+from tram.kiem.cay_tien_trinh import TienTrinh, cay, mo_ho
 from tram.kiem.giu_xac import Goc
-from tram.kiem.gui_tin import LOI_GUI, Kill, kill_cuc_bo  # noqa: F401 — tên cũ, người gọi import từ đây
+from tram.kiem.gui_tin import LOI_GUI, Kill, kill_cuc_bo, kill_uid  # noqa: F401 — tên cũ, người gọi import từ đây
 from tram.kiem.ngat import hoan
 
-CHU_KY_CHUP = 1.0
+CHU_KY_CHUP = 0.25
 
 
 class LoiThuHoi(RuntimeError):
@@ -25,12 +24,13 @@
 
 
 class Nhom:
-    def __init__(self, p: subprocess.Popen, *, kill: Kill, chup: Callable[[], list[TienTrinh]] = chup_he):
-        self.p, self.kill, self.chup, self.goc = p, kill, chup, Goc(p)
-        self.ket_thu_hoi: bool | None = None                            # None: chưa thu hồi lần nào (`so_huu`)
-        self.nhom_biet: set[int] = {p.pid}
-        self.lan_dung = time.monotonic()                                # lần chụp thành công gần nhất
-        self.lan_chup = time.monotonic() - CHU_KY_CHUP + 0.2          # lần chụp đầu sau 0,2 s
+    def __init__(self, p: subprocess.Popen, *, kill: Kill, chup: Callable[[], list[TienTrinh]] = chup_nhan,
+                 mot: Callable[[int], TienTrinh | None] = mot_nhan):
+        self.p, self.kill, self.chup, self.mot, self.goc = p, kill, chup, mot, Goc(p)
+        self.kill_uid, self.ket_thu_hoi = kill_uid(kill), None          # kênh theo UID | None; None: chưa thu hồi
+        # khoá (pid, sinh) của cây ở ảnh gần nhất; số nhóm cây từng có — CHỈ để nhận ra "mơ hồ", không để gửi
+        self.biet, self.nhom_biet, self.mo_ho = set(), {p.pid}, False
+        self.lan_chup = time.monotonic() - CHU_KY_CHUP + 0.05         # lần chụp đầu sau 0,05 s
 
     def cho(self, giay: float) -> int | None:
         if not math.isfinite(giay):
@@ -45,25 +45,29 @@
                 return None
 
     def cay(self) -> list[TienTrinh] | None:
-        """Cây hiện tại; None khi `ps` lỗi (không xác nhận được gì, giữ nhóm đã biết)."""
+        """Cây hiện tại; None khi không chụp được (không xác nhận được gì, giữ những gì đã biết)."""
         self.lan_chup = time.monotonic()
         try:
             ds = self.chup()
         except (OSError, subprocess.SubprocessError, ValueError):
             return None
-        song, self.lan_dung = self.goc.chua_gat(), time.monotonic()
-        con = cay(ds, self.p.pid if song else None, self.nhom_biet)
-        self.nhom_biet = {t.pgid for t in con} | ({self.p.pid} if song else set())
+        goc = self.p.pid if self.goc.chua_gat() else None
+        con = cay(ds, goc, self.biet)
+        self.mo_ho |= bool(mo_ho(ds, con, self.nhom_biet))
+        self.biet = {t.khoa for t in con if t.khoa is not None}
+        self.nhom_biet = {t.pgid for t in con} | ({goc} if goc else set())
         return con
 
     def _gui(self, sig: int, han: float) -> None:
-        moi = time.monotonic() - self.lan_dung <= 2 * CHU_KY_CHUP
-        nhom = (self.nhom_biet if moi else set()) | ({self.p.pid} if self.goc.chua_gat() else set())
-        for g in sorted(nhom - {0, 1, os.getpgrp()}):
+        con, goc = self.cay() or [], self.p.pid if self.goc.chua_gat() else None
+        for g in sorted(({t.pgid for t in con} | ({goc} if goc else set())) - {0, 1, os.getpgrp()}):
             if time.monotonic() >= han:
                 return
+            gui = self.kill if g == goc else self.kill_uid
+            if gui is None or (g != goc and not van_o_nhom([t for t in con if t.pgid == g], g, mot=self.mot)):
+                continue
             try:
-                self.kill(g, sig)
+                gui(g, sig)
             except LOI_GUI:
                 pass
 
@@ -76,9 +80,8 @@
                 return con
             time.sleep(0.05)
 
-    def _sach(self, con: list[TienTrinh] | None) -> bool:
-        """Gốc đã thoát và cây chỉ còn (nhiều nhất) xác của gốc."""
-        return con is not None and self.goc.thoat() and all(t.pid == self.p.pid for t in con)
+    def _sach(self, con: list[TienTrinh] | None) -> bool:       # gốc đã thoát, chỉ còn xác gốc, chưa gặp mơ hồ
+        return con is not None and not self.mo_ho and self.goc.thoat() and all(t.pid == self.p.pid for t in con)
 
     def thu_hoi(self, *, cho_term: float = 2.0, cho_cuoi: float = 2.0, han_gui: float = 10.0) -> bool:
         con = self.cay()
@@ -94,7 +97,7 @@
 
 
 def khoi_chay(argv: list[str], *, kill: Kill, chu: list, popen: Callable = subprocess.Popen,
-              chup: Callable[[], list[TienTrinh]] = chup_he, **kw) -> Nhom:
+              chup: Callable[[], list[TienTrinh]] = chup_nhan, **kw) -> Nhom:
     """Hợp đồng `so_huu` mục 1: `Nhom` vào `chu` TRONG `hoan()`, trước mọi lối ra sau Popen; gốc không theo dõi được
     (`Goc.hong`) → `LoiThuHoi`, `Nhom` vẫn ở `chu` — người gọi thu hồi (không bao giờ xác nhận), cổng đóng."""
     if not isinstance(chu, list):
```

Bản vá `tram/tho/cau_hinh.py`:

```diff
--- a/tram/tho/cau_hinh.py
+++ b/tram/tho/cau_hinh.py
@@ -75,4 +75,7 @@
     khe = tuple(_khe(k) for k in (raw.get("khe") or []))
     if not khe or len({k.ten for k in khe}) != len(khe):
         raise ValueError("khe: cần ít nhất một khe, tên không trùng")
+    rieng = [k.principal for k in khe if (k.principal or "").startswith("user:")]
+    if len(set(rieng)) != len(rieng):
+        raise ValueError("khe: principal user:<tên> phải riêng từng khe (D53 — gửi tín hiệu/dọn theo UID của khe)")
     return CauHinhTho(may_id, api.rstrip("/"), khe, doc_cau_hinh_chay(raw.get("chay")))
```

- [ ] **Step 4: Chạy, thấy xanh** — `PT tests/test_pham_vi_gui.py tests/test_vong_doi_tai_su_dung.py tests/test_vong_doi_ps.py tests/test_vong_doi.py tests/test_cay_tien_trinh.py tests/test_giu_xac.py tests/test_bang_tien_trinh.py tests/test_so_huu.py tests/test_so_huu_ngat.py tests/test_so_huu_nguoi_goi.py tests/test_han_tong.py tests/test_han_tong_ngat.py tests/test_chay_gioi_han.py tests/test_cau_hinh_tho.py` → `96 passed`; người gọi: `PT tests/test_chay_lenh_p1.py tests/test_chay_lenh.py tests/test_chay_cli_vong_doi.py tests/test_danh_tinh.py tests/test_codex_app_server.py tests/test_thu_hoi_uid.py tests/test_lenh_nghiem_thu.py tests/test_kiem_3b.py tests/test_han_muc_principal.py tests/test_chay_claude.py tests/test_codex_chay.py` → `81 passed`.

- [ ] **Step 5: Cả bộ** — `PT` → `2852 passed` (2833 + 19), nhật ký chặn 0 dòng mới.

- [ ] **Step 6: Commit** — `fix(kiem): cây theo định danh; nhóm ngoài gốc chỉ gửi dưới UID dành riêng (V2-0, dot7-C01, A01)`

## Task 4 — Bộ chạy không gặt gốc; hạn trước spawn; spawn, đóng ống và thu hồi trong vùng sở hữu (V2-0; review vòng 1 A03, vòng 2 R2-02, R2-03, R2-04)

**Files:** thay toàn bộ `tram/kiem/chay_gioi_han.py`; sửa `tram/kiem/han_tong.py`, `tram/kiem/danh_tinh.py`; test mới `tests/test_so_huu_bo_chay.py`, `tests/test_so_huu_ong.py`, `tests/test_so_huu_han_tong.py` (file riêng — B-T8 thêm test vào cuối `tests/test_han_tong_ngat.py`, tránh xung đột).

**Interfaces — MỘT bản thân hàm cuối cùng cho `chay_gioi_han`/`chay_han_tong` (review §4.1, R2-03):** plan B KHÔNG viết thân hàm cạnh tranh; B-T6 chỉ thêm tham số `stdin=` vào đúng bản này (hunk chữ ký + chọn `vao`), B-T8 không sửa `han_tong.py` (chỉ thêm test trên bản này).
- `chay_gioi_han(argv, *, kill, timeout, capture_output=False, text=False, input=None, env=None, cwd=None, check=False, khoi=khoi_chay)` — chữ ký và hình dạng kết quả giữ nguyên. Hạn tuyệt đối `het` tính TRƯỚC spawn. `khoi(..., chu=chu)`; `khoi` giả không tự ghi `chu` thì nhận `Nhom` nó trả. `_ong(n, input, het) -> (stdout, stderr, xong)`: đọc/ghi ống bằng selector (`with` — đóng ở mọi lối ra), chờ gốc bằng `n.cho` (KHÔNG gặt). `_don(chu, ten, loi)`: trong `hoan()`, đóng TỪNG ống (OSError khi đóng bị nuốt — không chặn ống sau) rồi trong `finally` LUÔN `thu_hoi_con_lai(chu)`; chưa xác nhận → `LoiThuHoi` THAY `loi` và mọi lỗi đóng ống/selector (`from None`); `loi` là KeyboardInterrupt (kể cả `NgatTerm` của B) thì ngắt vẫn thắng. Điểm tiêm của test: `_doc` (= `os.read`), `_ghi` (= `os.write`), `_bo_chon` (= `selectors.DefaultSelector`).
- `chay_han_tong`: tạo dấu + spawn trong `try` VÀ trong `hoan()` (ngắt tới lúc đó chỉ ném khi `Nhom` đã ở `chu`); `khoi` ném `OSError` với `chu` rỗng = Popen chưa tạo tiến trình (sạch); ném gì khác (vd. `LoiThuHoi` khi gốc không theo dõi được — `Nhom` đã ở `chu`) → `finally` thu hồi `chu` (trong `hoan()`), `don()` vẫn chạy, dấu GIỮ. Dấu chỉ xoá khi thu hồi VÀ `don()` cùng xác nhận.
- `danh_tinh.quan_sat`: chờ bằng `n.goc.thoat()` thay `n.p.poll()` (không gặt gốc trước `thu_hoi`).
- **Hợp đồng gặt:** chỉ `Nhom.thu_hoi` (khi đã xác nhận) gặt gốc; không ai gọi `communicate`/`wait`/`poll` trên `n.p` của một `Nhom` (`Goc` của Popen giả trong test là ngoại lệ có chủ đích).

- [ ] **Step 1: Viết test**

Tạo mới `tests/test_so_huu_bo_chay.py` (nguyên văn):

```python
"""Review vòng 1 A03, vòng 2 R2-02/R2-03/R2-04: bộ chạy `chay_gioi_han` KHÔNG gặt gốc bằng `communicate` (gặt sớm làm
nhóm gốc mất bảo vệ), hạn tính TRƯỚC spawn, mọi bước sau spawn trong vùng sở hữu; lỗi đóng ống/selector/đọc không chặn
thu hồi và không che "chưa xác nhận" (`test_so_huu_ong.py`); `chay_han_tong`: `test_so_huu_han_tong.py`. Tiến
trình thật chỉ là `python -c` của chính user đang test; kênh gửi là bản ghi lại rồi gửi cục bộ."""
import os
import signal
import subprocess
import time

import pytest

from test_vong_doi import CHAU, PY, _song
from tram.kiem import chay_gioi_han as cgh
from tram.kiem.chay_gioi_han import chay_gioi_han
from tram.kiem.vong_doi import khoi_chay, kill_cuc_bo


def test_goc_thoat_nhanh_chau_o_nhom_goc_van_thu_hoi_qua_nhom_goc(tmp_path):
    gui, goc = [], []

    def kill(g, s):
        gui.append(g)
        kill_cuc_bo(g, s)

    def khoi(argv, **kw):
        n = khoi_chay(argv, **kw)
        goc.append(n.p.pid)
        return n
    try:
        r = chay_gioi_han([PY, "-c", CHAU.format(moi=False, ngu=0)], kill=kill, timeout=20, cwd=tmp_path, khoi=khoi)
        chau = int((tmp_path / "chau.pid").read_text())
        assert r.returncode == 0 and not _song(chau) and set(gui) == set(goc)       # chỉ nhóm gốc, số còn giữ bởi xác
    finally:
        if (tmp_path / "chau.pid").exists() and _song(chau := int((tmp_path / "chau.pid").read_text())):
            os.kill(chau, signal.SIGKILL)                   # đúng PID test vừa tạo


def test_han_tinh_truoc_spawn_spawn_cham_thi_het_han_va_van_thu_hoi(monkeypatch):
    goi, con, that = [], [], cgh._ong

    def khoi(a, **kw):
        time.sleep(0.4)                                     # spawn tiêu hết hạn 0,2 s
        goi.append(khoi_chay(a, **kw))
        return goi[-1]

    def ong(n, vao, het):
        con.append(het - time.monotonic())                  # phần hạn còn lại khi bắt đầu đọc
        return that(n, vao, het)
    monkeypatch.setattr(cgh, "_ong", ong)
    with pytest.raises(subprocess.TimeoutExpired):
        chay_gioi_han([PY, "-c", "import time; time.sleep(60)"], kill=kill_cuc_bo, timeout=0.2, khoi=khoi)
    assert con[0] <= 0 and not _song(goi[0].p.pid)
```

Tạo mới `tests/test_so_huu_ong.py` (nguyên văn):

```python
"""Review vòng 2 R2-04: lỗi ở ống của `chay_gioi_han` — đóng stdin/stdout/stderr ném, selector `select`/`close` ném, đọc
ném — không chặn ống sau, LUÔN tới thu hồi; chưa xác nhận → `LoiThuHoi` thắng lỗi ống/lỗi thường (`from None`); ngắt
vẫn là ngắt. Lỗi tiêm ĐÚNG điểm đọc/selector thật (`_doc`, `_bo_chon`); tiến trình thật chỉ là `python -c` của chính
user đang test."""
import errno
import selectors
from types import SimpleNamespace

import pytest

from test_vong_doi import PY, _song
from tram.kiem import chay_gioi_han as cgh
from tram.kiem.chay_gioi_han import chay_gioi_han
from tram.kiem.vong_doi import LoiThuHoi, khoi_chay, kill_cuc_bo

IN_RA = "print('x' * 10, flush=True); import time; time.sleep(60)"


class Ong:
    """Ống của ta; `close` có thể ném (lỗi đóng ống mang chữ lạ)."""
    def __init__(self, ten, ghi, loi):
        self.ten, self.ghi, self.loi = ten, ghi, loi

    def close(self):
        self.ghi.append(self.ten)
        if self.loi:
            raise OSError("đóng ống: BI-MAT")


class NhomGia:
    def __init__(self, sach, ong_loi=None):
        self.sach, self.da = sach, []
        ong = {t: Ong(t, self.da, t == ong_loi) for t in ("stdin", "stdout", "stderr")}
        self.p = SimpleNamespace(returncode=0, **ong)

    def thu_hoi(self):
        self.da.append("thu")
        return self.sach


@pytest.mark.parametrize("sach, loi, mong", [(True, KeyboardInterrupt, KeyboardInterrupt),
                                              (False, KeyboardInterrupt, KeyboardInterrupt),
                                              (True, OSError, OSError), (False, OSError, LoiThuHoi)])
def test_ngat_hay_loi_giua_chung_van_thu_hoi_chua_xac_nhan_thi_loi_thu_hoi_tru_ngat(monkeypatch, sach, loi, mong):
    n = NhomGia(sach)

    def hong(*a):
        raise loi("BI-MAT")
    monkeypatch.setattr(cgh, "_ong", hong)
    with pytest.raises(mong) as e:
        chay_gioi_han(["x"], kill=kill_cuc_bo, timeout=5, khoi=lambda a, **kw: n)
    assert n.da == ["stdin", "stdout", "stderr", "thu"]
    assert mong is not LoiThuHoi or ("BI-MAT" not in str(e.value) and e.value.__suppress_context__)


@pytest.mark.parametrize("sach", [True, False])
@pytest.mark.parametrize("ong_loi", ["stdin", "stdout", "stderr"])
def test_dong_ong_loi_khong_chan_ong_sau_va_thu_hoi_khong_che_chua_xac_nhan(monkeypatch, ong_loi, sach):
    n = NhomGia(sach, ong_loi)
    monkeypatch.setattr(cgh, "_ong", lambda *a: (b"", b"", True))
    if sach:
        assert chay_gioi_han(["x"], kill=kill_cuc_bo, timeout=5, khoi=lambda a, **kw: n).returncode == 0
    else:
        with pytest.raises(LoiThuHoi) as e:
            chay_gioi_han(["x"], kill=kill_cuc_bo, timeout=5, khoi=lambda a, **kw: n)
        assert "BI-MAT" not in str(e.value) and e.value.__cause__ is None
    assert n.da == ["stdin", "stdout", "stderr", "thu"]


class ChonHong:
    """Selector thật, nhưng `select` hoặc `close` ném."""
    def __init__(self, diem):
        self.s, self.diem = selectors.DefaultSelector(), diem

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()

    def __getattr__(self, ten):
        return getattr(self.s, ten)

    def select(self, t):
        if self.diem == "chon":
            raise OSError(errno.EBADF, "select: BI-MAT")
        return self.s.select(t)

    def close(self):
        self.s.close()
        if self.diem == "dong_bo_chon":
            raise OSError(errno.EIO, "close: BI-MAT")


@pytest.mark.parametrize("diem", ["doc", "chon", "dong_bo_chon"])
def test_doc_hay_bo_chon_loi_van_dong_ong_va_thu_hoi_con_that(monkeypatch, diem):
    goi = []

    def doc_hong(fd, n):
        raise OSError(errno.EIO, "read: BI-MAT")
    if diem == "doc":
        monkeypatch.setattr(cgh, "_doc", doc_hong)
    else:
        monkeypatch.setattr(cgh, "_bo_chon", lambda: ChonHong(diem))
    argv = [PY, "-c", "print('x')" if diem == "dong_bo_chon" else IN_RA]
    try:
        with pytest.raises(OSError, match="BI-MAT"):
            chay_gioi_han(argv, kill=kill_cuc_bo, timeout=20, capture_output=True,
                          khoi=lambda a, **kw: goi.append(khoi_chay(a, **kw)) or goi[-1])
        assert goi[0].ket_thu_hoi is True and goi[0].p.stdout.closed and not _song(goi[0].p.pid)
    finally:
        for n in goi:
            if n.p.returncode is None:
                n.p.kill()
                n.p.wait(5)
```

Tạo mới `tests/test_so_huu_han_tong.py` (nguyên văn):

```python
"""Review vòng 1 A03, vòng 2 R2-02/R2-03: `chay_han_tong` spawn TRONG try/finally thu hồi + dọn — `khoi` hỏng sau khi có
PID, gốc không theo dõi được, ngắt khi `Nhom` đã ở `chu`: thu hồi vẫn chạy, `don()` vẫn chạy, dấu chỉ xoá khi cả hai xác
nhận; dò danh tính không tự gặt gốc. Tiến trình thật chỉ là `python -c` của chính user đang test."""
import signal

import pytest

from test_so_huu import KqLoi
from test_so_huu_ngat import Ngat, ngat
from test_so_huu_ong import NhomGia
from test_vong_doi import PY, SUDO, PopenGia
from tram.kiem import giu_xac
from tram.kiem.danh_tinh import LoiDanhTinh, quan_sat
from tram.kiem.han_tong import chay_han_tong
from tram.kiem.vong_doi import LoiThuHoi, khoi_chay, kill_cuc_bo


def test_han_tong_khoi_chay_hong_sau_khi_co_pid_van_don_va_giu_dau(tmp_path):
    goi = []

    def khoi(*a, **kw):
        raise LoiThuHoi("khởi chạy hỏng sau khi đã có tiến trình")
    with pytest.raises(LoiThuHoi):
        chay_han_tong(["gia"], han=1, kill=kill_cuc_bo, dau=tmp_path / "dau", don=lambda: goi.append(1) or True,
                      khoi=khoi)
    assert goi == [1] and (tmp_path / "dau").exists()


def test_han_tong_goc_khong_theo_doi_duoc_nhom_trong_chu_van_bi_giet_dau_giu(tmp_path, monkeypatch):
    goi, chu = [], []
    monkeypatch.setattr(giu_xac, "_kqueue", KqLoi)

    def khoi(a, **kw):
        chu.append(kw["chu"])
        return khoi_chay(a, **kw)
    try:
        with pytest.raises(LoiThuHoi, match="chưa xác nhận"):
            chay_han_tong([PY, "-c", "import time; time.sleep(60)"], han=5, kill=kill_cuc_bo, dau=tmp_path / "dau",
                          don=lambda: goi.append(1) or True, khoi=khoi)
        n, = chu[0]
        assert goi == [1] and (tmp_path / "dau").exists() and n.ket_thu_hoi is False and n.p.returncode is None
        assert n.p.wait(5) in (-signal.SIGTERM, -signal.SIGKILL)                  # nhóm gốc (chưa gặt) đã bị giết
    finally:
        for n in (chu[0] if chu else []):
            if n.p.poll() is None:
                n.p.kill()
                n.p.wait(5)


def test_han_tong_ngat_sau_khi_nhan_nhom_van_thu_hoi_nhom_trong_danh_sach(tmp_path):
    n, goi = NhomGia(True), []

    def khoi(*a, chu, **kw):
        chu.append(n)                                       # `khoi_chay` đã đưa Nhom vào danh sách sở hữu
        raise KeyboardInterrupt                             # ngắt được phát lại khi rời `hoan()`, trước khi trả
    with pytest.raises(KeyboardInterrupt):
        chay_han_tong(["gia"], han=1, kill=kill_cuc_bo, dau=tmp_path / "dau", don=lambda: goi.append(1) or True,
                      khoi=khoi)
    assert n.da == ["thu"] and goi == [1] and not (tmp_path / "dau").exists()


def test_han_tong_ngat_lan_hai_luc_thu_hoi_ghi_ket_qua_roi_moi_nem(tmp_path):
    goi, cu = [], signal.signal(signal.SIGINT, ngat)                # handler của người gọi

    class N:
        def cho(self, han):
            raise Ngat("lần một")

        def thu_hoi(self):
            signal.raise_signal(signal.SIGINT)                      # lần hai, giữa lúc thu hồi: được hoãn
            goi.append("thu")
            return True
    try:
        with pytest.raises(Ngat):
            chay_han_tong(["gia"], han=1, kill=kill_cuc_bo, dau=tmp_path / "dau",
                          don=lambda: goi.append("don") or True, khoi=lambda a, **kw: N())
        assert goi == ["thu", "don"] and not (tmp_path / "dau").exists()
    finally:
        signal.signal(signal.SIGINT, cu)


class PopenDem(PopenGia):
    """Gốc không bao giờ thoát; đếm số lần `poll` (gặt) bị gọi."""
    def __init__(self):
        self.dem = 0

    def poll(self):
        self.dem += 1
        return None


def test_do_danh_tinh_khong_tu_gat_goc():
    p = PopenDem()
    with pytest.raises((LoiDanhTinh, LoiThuHoi)):
        quan_sat(lambda a: a, lambda g, s: None, khoi=lambda argv, **kw: khoi_chay(argv, popen=lambda a, **k: p, **kw),
                 chup=lambda: [SUDO], han=0.2)
    assert p.dem == 0                                       # chỉ `Nhom.thu_hoi` (khi đã xác nhận) mới gặt
```

- [ ] **Step 2: Chạy, thấy đỏ** — `PT tests/test_so_huu_bo_chay.py tests/test_so_huu_ong.py tests/test_so_huu_han_tong.py`. Kết quả thật (mã của Task 3 — `chay_gioi_han` còn `communicate`, `han_tong` spawn ngoài `try`):

```
E           tram.kiem.vong_doi.LoiThuHoi: ['python']: không xác nhận thu hồi cây tiến trình
                       ← communicate gặt gốc sớm: cháu còn ở nhóm gốc thành "mơ hồ", không thu hồi được
E       AttributeError: <module 'tram.kiem.chay_gioi_han' …> has no attribute '_ong'      (×11)
E       AttributeError: <module 'tram.kiem.chay_gioi_han' …> has no attribute '_bo_chon'  (×2) / '_doc' (×1)
E       assert ([] == [1]                     ← han_tong: khoi_chay hỏng sau khi có PID / gốc không theo dõi được →
                                                dọn KHÔNG chạy (×2)
E       AssertionError: assert ([] == ['thu'] ← ngắt khi Nhom đã ở `chu`: không thu hồi
E           AssertionError: assert (['don'] == ['thu', 'don']  ← ngắt lần hai lúc thu hồi cắt ngang thu hồi
E       assert 4 == 0                         ← dò danh tính gọi `poll` (gặt) 4 lần
20 failed in 6.52s
```

**Đối chứng R2-04 trên `chay_gioi_han.py` của bản plan vòng 2 (`_don` đóng ống rồi mới thu hồi, không `finally`):**

```
E           OSError: đóng ống: BI-MAT            ← ×6: lỗi đóng stdin/stdout/stderr chặn thu hồi, che "chưa xác nhận"
E               tram.kiem.vong_doi.LoiThuHoi: ['x']: bị ngắt và không xác nhận thu hồi cây tiến trình
                                                 ← ngắt bị đổi thành LoiThuHoi (khác hợp đồng "ngắt vẫn là ngắt")
```

**Đột biến `han_tong` (bỏ `hoan()` quanh lời thu hồi trong `finally`, giữ `thu_hoi_con_lai`):** `test_han_tong_ngat_lan_hai_luc_thu_hoi_ghi_ket_qua_roi_moi_nem` đỏ — `assert (['thu', 'don'] == ['thu', 'don'] … and not True)`: ngắt lần hai phát lại NGAY trong lời thu hồi nên kết quả "đã thu hồi" không kịp ghi, dấu bị giữ dù thu hồi và dọn đều xác nhận (bản sửa: ghi kết quả trong `hoan()` rồi mới phát lại).

- [ ] **Step 3: Mã**

Thay TOÀN BỘ `tram/kiem/chay_gioi_han.py` bằng (nguyên văn):

```python
"""`subprocess.run` có hạn và sở hữu cây (lát 3C-B, dot6-C02) — cùng hình dạng gọi `chay(argv, capture_output=…,
text=…, timeout=…)` mà mã dọn lịch/tiến trình của 3c đã dùng, nhưng đi qua `vong_doi`: trong lúc chờ vẫn chụp cây mỗi
`CHU_KY_CHUP` giây; quá hạn → thu hồi cả cây qua `kill` của principal rồi ném `TimeoutExpired`; không xác nhận thu hồi
→ `LoiThuHoi`. Ngoại lệ chỉ mang TÊN chương trình, không argv/đường dẫn/stdout/stderr (dot6-Q06). Luôn đọc bytes rồi
giải mã `errors="replace"` khi `text=True` — đầu ra không phải UTF-8 không làm bỏ qua bước thu hồi.
Review A03, R2-02, R2-04: KHÔNG gặt gốc bằng `communicate` — `_ong` đọc/ghi ống bằng `selectors` (selector đóng bằng
`with` ở mọi lối ra) và chờ gốc bằng `Nhom.cho` (xác giữ số nhóm gốc tới `thu_hoi`). Hạn tuyệt đối tính TRƯỚC spawn;
spawn và mọi bước sau trong vùng sở hữu (`so_huu`): lỗi/ngắt ở đâu cũng `_don` — đóng TỪNG ống (lỗi đóng không chặn
ống sau) rồi LUÔN thu hồi, cả hai trong `ngat.hoan()`. Chưa xác nhận → `LoiThuHoi` THAY lỗi thường/lỗi ống (`from
None`); ngắt (KeyboardInterrupt) vẫn là ngắt — mọi ngắt đều là "chưa công nhận" ở người gọi."""
import contextlib
import math
import os
import selectors
import subprocess
import time
from collections.abc import Callable
from pathlib import Path

from tram.kiem.ngat import hoan
from tram.kiem.so_huu import thu_hoi_con_lai
from tram.kiem.vong_doi import CHU_KY_CHUP, Kill, LoiThuHoi, khoi_chay

_doc, _ghi, _bo_chon = os.read, os.write, selectors.DefaultSelector       # test thay để tiêm lỗi đúng điểm đọc/ghi


def _ong(n, input: bytes | None, het: float) -> tuple[bytes | None, bytes | None, bool]:
    """(stdout, stderr, xong) — xong: mọi ống đã EOF VÀ gốc đã thoát trước `het`. Không gặt gốc."""
    p, ra, ma = n.p, {}, None
    with _bo_chon() as sel:
        for f in (p.stdout, p.stderr):
            if f is not None:
                sel.register(f, selectors.EVENT_READ)
                ra[f] = bytearray()
        vao = memoryview(input or b"")
        if p.stdin is not None:
            sel.register(p.stdin, selectors.EVENT_WRITE) if vao else p.stdin.close()
        while (con := het - time.monotonic()) > 0:
            for k, _ in sel.select(min(CHU_KY_CHUP, con)) if sel.get_map() else ():
                if k.fileobj is p.stdin:
                    try:
                        vao = vao[_ghi(k.fd, vao[:512]):]               # ≤ PIPE_BUF: select báo ghi được thì không chặn
                    except BrokenPipeError:
                        vao = vao[:0]
                    if not vao:
                        sel.unregister(p.stdin)
                        p.stdin.close()
                elif d := _doc(k.fd, 65536):
                    ra[k.fileobj] += d
                else:
                    sel.unregister(k.fileobj)
            if ma is None:
                ma = n.cho(0.0 if sel.get_map() else min(CHU_KY_CHUP, max(0.0, het - time.monotonic())))
            elif time.monotonic() >= n.lan_chup + CHU_KY_CHUP:
                n.cay()                                                   # gốc đã thoát, ống còn mở: vẫn theo dõi cây
            if ma is not None and not sel.get_map():
                return (bytes(ra[p.stdout]) if p.stdout else None), (bytes(ra[p.stderr]) if p.stderr else None), True
    return None, None, False


def _don(chu: list, ten: list[str], loi: BaseException | None) -> None:
    """Đóng TỪNG ống của ta rồi LUÔN thu hồi mọi `Nhom` trong `chu`, cả hai trong `hoan()` (ngắt lần hai ném SAU khi
    xong). Chưa xác nhận → `LoiThuHoi` THAY `loi` và mọi lỗi đóng ống; `loi` là ngắt thì ngắt vẫn thắng."""
    with hoan():
        try:
            for n in chu:
                for f in (n.p.stdin, n.p.stdout, n.p.stderr):
                    if f is not None:
                        with contextlib.suppress(OSError):
                            f.close()
        finally:
            if not thu_hoi_con_lai(chu) and not isinstance(loi, KeyboardInterrupt):
                qua = " quá hạn và" if isinstance(loi, subprocess.TimeoutExpired) else ":"
                raise LoiThuHoi(f"{ten}{qua} không xác nhận thu hồi cây tiến trình") from None


def chay_gioi_han(argv: list[str], *, kill: Kill, timeout: float, capture_output: bool = False, text: bool = False,
                  input=None, env=None, cwd=None, check: bool = False,
                  khoi: Callable = khoi_chay) -> subprocess.CompletedProcess:
    if not math.isfinite(timeout):
        raise ValueError("timeout phải hữu hạn")
    ten = [Path(str(argv[0])).name] if argv else []
    ong = subprocess.PIPE if capture_output else subprocess.DEVNULL
    if text and isinstance(input, str):
        input = input.encode()
    het, chu = time.monotonic() + timeout, []                            # hạn tuyệt đối tính TRƯỚC spawn
    try:
        try:
            n = khoi(list(argv), kill=kill, stdin=subprocess.PIPE if input is not None else subprocess.DEVNULL,
                     stdout=ong, stderr=ong, env=env, cwd=cwd, chu=chu)
        except OSError as e:                    # `khoi_chay`: OSError chỉ khi Popen chưa tạo được tiến trình
            raise OSError(f"{ten}: không khởi chạy được ({type(e).__name__})") from None
        chu[:] = chu or [n]                     # `khoi` giả không tự ghi `chu`: nhận Nhom nó trả
        ra, loi, xong = _ong(n, input, het)
    except BaseException as e:
        _don(chu, ten, e)
        raise
    _don(chu, ten, None if xong else subprocess.TimeoutExpired(ten, timeout))
    if not xong:
        raise subprocess.TimeoutExpired(ten, timeout)
    if check and n.p.returncode:
        raise subprocess.CalledProcessError(n.p.returncode, ten)
    if text:
        ra, loi = (None if x is None else x.decode("utf-8", "replace") for x in (ra, loi))
    return subprocess.CompletedProcess(list(argv), n.p.returncode, ra, loi)
```

Bản vá `tram/kiem/han_tong.py`:

```diff
--- a/tram/kiem/han_tong.py
+++ b/tram/kiem/han_tong.py
@@ -2,7 +2,11 @@
 hồi). Harness chạy trong TIẾN TRÌNH CON nhóm riêng (`vong_doi`); quá hạn → thu hồi cả cây qua `kill` gộp (quản lý +
 principal); sau đó, kể cả khi harness tự xong, `don()` (gỡ lịch + tiến trình của principal qua `CongLich` — mã 3c)
 phải trả đúng True. Cổng = file dấu `dau`, tạo O_EXCL TRƯỚC khi spawn, chỉ xoá khi cả thu hồi cây lẫn `don()` xác
-nhận. Còn dấu → lượt sau bị từ chối không spawn (`cong_dong`), chờ Đại ca dọn và kiểm tay."""
+nhận. Còn dấu → lượt sau bị từ chối không spawn (`cong_dong`), chờ Đại ca dọn và kiểm tay. Review A03/R2-02/R2-03
+(hợp đồng `so_huu`): tạo dấu + spawn nằm trong `try` VÀ trong `ngat.hoan()` — ngắt tới lúc đó chỉ ném khi `Nhom` đã ở
+`chu`; thu hồi trong `hoan()` (ngắt lần hai không cắt ngang, ném sau khi xong); `don()` luôn chạy sau thu hồi, vẫn ngắt
+được → dấu GIỮ. `khoi` ném lỗi khác OSError (vd. `LoiThuHoi` — `Nhom` đã ở `chu` — hay `khoi` giả hỏng) → không xác
+nhận: dấu giữ, cổng đóng."""
 import math
 import os
 import subprocess
@@ -10,6 +14,8 @@
 from pathlib import Path
 
 from tram.kiem.gui_tin import gop_kill  # noqa: F401 — tên cũ; định nghĩa và phạm vi gửi ở `gui_tin` (A01)
+from tram.kiem.ngat import hoan
+from tram.kiem.so_huu import thu_hoi_con_lai
 from tram.kiem.vong_doi import Kill, LoiThuHoi, khoi_chay
 
 
@@ -35,25 +41,33 @@
     if not (math.isfinite(han) and han > 0):
         raise ValueError("hạn tổng phải hữu hạn, dương")
     dau.parent.mkdir(parents=True, exist_ok=True)
+    chu, co_dau, ma, sach, xong = [], False, None, False, False
     try:
-        os.close(os.open(dau, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600))
-    except FileExistsError:
-        raise LoiThuHoi(f"cổng đang đóng ({dau.name}): lượt trước chưa xác nhận dọn — không chạy") from None
-    try:
-        n = khoi(argv, kill=kill, stdin=subprocess.DEVNULL, chu=[], **kw)     # Task 4: vùng sở hữu đầy đủ
-    except OSError:
-        n = None
-    ma, sach, xong = None, False, False
-    try:
-        ma = n.cho(han) if n else None
+        with hoan():                            # tạo dấu + spawn: ngắt chỉ ném khi Nhom đã ở `chu` (finally thu hồi)
+            try:
+                os.close(os.open(dau, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600))
+            except FileExistsError:
+                raise LoiThuHoi(f"cổng đang đóng ({dau.name}): lượt trước chưa xác nhận dọn — không chạy") from None
+            co_dau = True
+            try:
+                n = khoi(argv, kill=kill, stdin=subprocess.DEVNULL, chu=chu, **kw)
+                chu[:] = chu or [n]             # `khoi` giả không tự ghi `chu`: nhận Nhom nó trả
+            except OSError:
+                if chu:
+                    raise
+                sach = True                     # Popen chưa tạo được tiến trình: không có gì để thu hồi
+        ma = chu[0].cho(han) if chu else None
     finally:
-        try:
-            sach = n.thu_hoi() if n else True
-        finally:
-            xong = _don(don) and sach
-            if xong:
-                dau.unlink()
-    if n is None:
+        if co_dau:
+            try:
+                with hoan():                    # ngắt lần hai ném SAU khi thu hồi xong VÀ đã ghi kết quả
+                    if chu:
+                        sach = thu_hoi_con_lai(chu)
+            finally:
+                xong = _don(don) and sach
+                if xong:
+                    dau.unlink()
+    if not chu:
         raise LoiThuHoi("không khởi chạy được harness")
     if ma is None:
         raise HetHanTong(f"harness quá hạn tổng {han:g} s — " + ("đã thu hồi và dọn" if xong else "CỔNG GIỮ ĐÓNG"))
```

Bản vá `tram/kiem/danh_tinh.py`:

```diff
--- a/tram/kiem/danh_tinh.py
+++ b/tram/kiem/danh_tinh.py
@@ -38,7 +38,7 @@
         except (OSError, ValueError) as e:
             raise LoiDanhTinh(f"không khởi chạy được tiến trình dò: {type(e).__name__}") from None
         het = time.monotonic() + han
-        while time.monotonic() < het and n.p.poll() is None:
+        while time.monotonic() < het and not n.goc.thoat():          # A03: chỉ `Nhom.thu_hoi` gặt gốc
             con = n.cay()
             if con and all(t.uid != 0 for t in la_cua(con)):
                 return con
```

- [ ] **Step 4: Chạy, thấy xanh** — `PT tests/test_so_huu_bo_chay.py tests/test_so_huu_ong.py tests/test_so_huu_han_tong.py tests/test_chay_gioi_han.py tests/test_han_tong.py tests/test_han_tong_ngat.py tests/test_danh_tinh.py tests/test_thu_hoi_uid.py tests/test_lenh_nghiem_thu.py tests/test_cong_lich.py tests/test_so_huu.py tests/test_so_huu_ngat.py tests/test_so_huu_nguoi_goi.py` → `96 passed`.

- [ ] **Step 5: Cả bộ** — `PT` → `2872 passed` (2852 + 20), nhật ký chặn 0 dòng mới.

- [ ] **Step 6: Commit** — `fix(kiem): chay_gioi_han không gặt gốc, hạn trước spawn, đóng ống luôn tới thu hồi; han_tong dọn cả khi spawn hỏng (V2-0, A03, R2-02..04)`

## Task 5 — Dọn theo UID của khe: khởi động, đầu phiếu, sau mỗi lần chạy CLI; mồ côi không còn giết theo số (V2-0, bs-863.15; review vòng 1 A01, A02)

**Files:** tạo `tram/tho/don_uid.py`; sửa `tram/tho/ngu_canh.py`, `tram/tho/mo_coi.py`, `tram/tho/mo_coi_khe.py`, `tram/tho/vong_khe.py`, `tram/tho/phieu_chay.py`, `tram/tho/mot_lan.py`; test mới `tests/test_don_uid.py`, `tests/test_mo_coi_uid.py`, `tests/test_khe_tan_du.py`; sửa `tests/tho_chay_gia.py` (máy thợ giả: `don_uid` giả), `tests/test_phieu_chay_thu_hoi.py` (`nc` giả có `don_khe`), `tests/test_so_khe_hop_thu.py` (bỏ ca cũ giết mồ côi theo pgid).

**Interfaces:**
- `don_uid.don_uid(pr, *, xac_minh=xac_minh_uid, chay=chay_gioi_han, chup=chup_nhan, han=5.0, ngu=time.sleep) -> None`; ném `LoiThuHoi` khi: `pr.co_che != "user"`; `LoiDanhTinh`; UID ∈ {0, `os.getuid()`, `os.geteuid()`} (phòng thủ thêm — kill -1 không bao giờ ngoài khe); `kill -1` không chạy được/không xác nhận thu hồi; không đọc được bảng; còn tiến trình có uid/uid thực của khe sau `han`. Lệnh: `pr.boc(["/bin/kill", "-KILL", "-1"])`, `kill=pr.kill_nhom`, `env={"PATH": "/usr/bin:/bin"}`, `timeout=10`. `con_lai(uid, chup) -> int`.
- `NguCanhTho.don_uid: Callable | None` (tiêm; None → `don_uid.don_uid`); `NguCanhTho.don_khe(k)` — principal của khe (`ChuaCoPrincipal` → `LoiThuHoi`) rồi dọn.
- `mo_coi.don_mo_coi(p, *, don) -> dict | None`: đọc bản ghi, `don()` (ném → GIỮ file), xoá file, trả bản ghi hợp lệ (`giao_id` str, `lan` int) hoặc None. Bỏ `dung_nhom` (giết theo số pgid — chính lỗi .15). `ghi_pid` giữ định dạng cũ.
- `mo_coi_khe.don_mo_coi_khe(...) -> (TrangThaiPhieu | None, dung_khe: bool)`; `VongKhe.khoi_dong` gán `self.hong`.
- `chay_phieu`: `nc.don_khe(vk.k)` TRƯỚC `chuan_bi` (trước khi dựng worktree/trao quyền). `chay_mot_lan`: `nc.don_khe(pc.k)` sau khi CLI trả bình thường, TRƯỚC khi xoá bản ghi pid và gửi `chay.xong` — `LoiThuHoi` giữ pid, không có lần sau.
- **Hệ quả có chủ đích:** khe chưa khai principal hợp lệ, hay principal `sandbox:`, dừng ngay lúc khởi động (D53). Đọc hạn mức lúc rảnh không chạy song song với dọn (chỉ chạy khi khe không giữ phiếu, trong luồng nhịp — phiếu mới cũng chỉ được nhận trong luồng đó).

- [ ] **Step 1: Viết test**

Tạo mới `tests/test_don_uid.py` (nguyên văn):

```python
"""Review vòng 1 A01/A02 (V2-0, D53): dọn theo PHẠM VI UID của khe — `kill -KILL -1` CHẠY DƯỚI chính principal (nhân
chỉ gửi tới tiến trình cùng UID: không thể trúng tài khoản khác dù số PID/nhóm đã cấp lại), rồi chứng minh bằng bảng
tiến trình của nhân không còn tiến trình nào có uid/uid thực của khe. Bước nào không chứng minh được → `LoiThuHoi`.
Xác minh UID, lệnh chạy và bảng tiến trình đều GIẢ — test KHÔNG BAO GIỜ chạy kill -1 thật."""
import os
import subprocess

import pytest

from tram.kiem.cay_tien_trinh import TienTrinh
from tram.kiem.danh_tinh import LoiDanhTinh
from tram.kiem.vong_doi import LoiThuHoi
from tram.tho.don_uid import GIET, don_uid
from tram.tho.principal import Principal

PR = Principal("user", "tram-k-c-codex-1")
UID = 600 if os.getuid() != 600 else 601


class May:
    """`chay` ghi lại lệnh (không spawn); `chup` trả lần lượt các ảnh (ảnh cuối lặp lại)."""
    def __init__(self, *anh, loi=None):
        self.goi, self.anh, self.loi = [], list(anh) or [[]], loi

    def chay(self, argv, **kw):
        self.goi.append((argv, kw))
        if self.loi is not None:
            raise self.loi
        return subprocess.CompletedProcess(argv, 1, b"", b"")         # mã thoát không là bằng chứng

    def chup(self):
        return self.anh.pop(0) if len(self.anh) > 1 else self.anh[0]


def don(may, pr=PR, xac_minh=lambda *a: UID, **kw):
    return don_uid(pr, xac_minh=xac_minh, chay=may.chay, chup=may.chup, ngu=lambda s: None, **kw)


def test_kill_1_duoi_principal_roi_bang_khong_con_ai_cua_uid():
    may = May([TienTrinh(7000, 1, 7000, UID, UID, 1), TienTrinh(7001, 1, 7001, 501, 501, 2)],
              [TienTrinh(7001, 1, 7001, 501, 501, 2)])                # tiến trình của tài khoản khác không tính
    don(may)
    ((argv, kw),) = may.goi
    assert GIET == ["/bin/kill", "-KILL", "-1"] and argv == PR.boc(GIET) and argv[:5] == ["/usr/bin/sudo", "-n", "-H",
                                                                                            "-u", PR.user]
    assert kw["kill"] == PR.kill_nhom and kw["env"] == {"PATH": "/usr/bin:/bin"} and kw["timeout"] == 10


def test_con_tien_trinh_cua_uid_sau_han_thi_loi_thu_hoi():
    may = May([TienTrinh(7000, 1, 7000, 0, UID, 1)])                   # setuid root, uid thực của khe: vẫn tính
    with pytest.raises(LoiThuHoi, match="còn 1"):
        don(may, han=0.05)


def _loi_danh_tinh(*a):
    raise LoiDanhTinh("x")


@pytest.mark.parametrize("pr, xm", [(Principal("sandbox", "tram-exec"), lambda *a: UID), (PR, _loi_danh_tinh),
                                    (PR, lambda *a: os.getuid()), (PR, lambda *a: 0)])
def test_khong_chung_minh_duoc_uid_rieng_thi_khong_kill_va_loi_thu_hoi(pr, xm):
    may = May()
    with pytest.raises(LoiThuHoi):
        don(may, pr=pr, xac_minh=xm)
    assert may.goi == []


@pytest.mark.parametrize("loi", [OSError("spawn"), subprocess.TimeoutExpired("kill", 10), LoiThuHoi("x")])
def test_kill_khong_xac_nhan_thi_loi_thu_hoi(loi):
    with pytest.raises(LoiThuHoi):
        don(May(loi=loi))


def test_khong_doc_duoc_bang_thi_loi_thu_hoi():
    may = May()
    may.chup = lambda: (_ for _ in ()).throw(OSError("sysctl"))
    with pytest.raises(LoiThuHoi):
        don(may)
```

Tạo mới `tests/test_khe_tan_du.py` (nguyên văn):

```python
"""Review vòng 1 A02: cây không quan sát được KHÔNG được coi là sạch ở tầng khe. Vòng `tram tho chay` THẬT (CLI giả,
trạm trong bộ nhớ, cùng user) chỉ sang lần chạy/phiếu sau khi dọn theo UID của khe xác nhận; còn tàn dư → khe dừng,
không spawn lần sau, giữ bản ghi pid + phiếu. Dọn UID là bản GIẢ (ghi lại; ném khi "còn tàn dư"), không kill -1
thật."""
import threading

from test_kich_ban_3a2 import su_kien
from tho_chay_gia import dung_may
from tram.kiem.vong_doi import LoiThuHoi
from tram.tho.vong_khe import VongKhe


def chay_khe(m, hong_tu: int):
    """Chạy vòng khe tới khi nó TỰ dừng; lần dọn thứ `hong_tu` báo còn tàn dư."""
    goi = []

    def don(pr):
        goi.append(pr)
        if len(goi) >= hong_tu:
            raise LoiThuHoi("còn 1 tiến trình của UID khe sau kill -1")
    m.nc.don_uid = don
    tat, vk = threading.Event(), VongKhe(m.nc, m.nc.ch.khe[0])
    th = threading.Thread(target=vk.chay, args=(tat,), daemon=True)
    th.start()
    th.join(40)
    tat.set()
    return vk, goi, not th.is_alive()


def test_tan_du_sau_lan_chay_thi_khong_sang_lan_sau_va_khe_dung(tmp_path, monkeypatch):
    m = dung_may(tmp_path, monkeypatch, {"1": [{"thoat": 1}], "2": [{"thoat": 0}]})
    vk, goi, tu_dung = chay_khe(m, 3)                   # 1: khởi động khe, 2: đầu phiếu, 3: sau lần chạy 1
    wt = m.nc.goc_wt / "hr-codex" / "hr-1"
    assert tu_dung and vk.hong and len(goi) == 3 and [s["lan"] for s in su_kien(m, "chay.bat_dau")] == [1]
    assert not (wt / ".tram" / "stdin-2.md").exists() and su_kien(m, "chay.xong") == []
    assert vk.so.pid.exists() and vk.so.doc_phieu() is not None             # khởi động lại: dọn UID rồi `mo-coi`


def test_tan_du_luc_khoi_dong_thi_khe_dung_khong_nhan_phieu(tmp_path, monkeypatch):
    m = dung_may(tmp_path, monkeypatch, [{"thoat": 0}])
    vk, goi, tu_dung = chay_khe(m, 1)
    assert tu_dung and vk.hong and len(goi) == 1 and vk.so.doc_phieu() is None and su_kien(m, "chay.bat_dau") == []


def test_tan_du_dau_phieu_thi_khong_dung_worktree_khe_dung_giu_phieu(tmp_path, monkeypatch):
    m = dung_may(tmp_path, monkeypatch, [{"thoat": 0}])
    vk, goi, tu_dung = chay_khe(m, 2)
    assert tu_dung and vk.hong and len(goi) == 2 and su_kien(m, "chay.bat_dau") == []
    assert not (m.nc.goc_wt / "hr-codex" / "hr-1").exists() and vk.so.doc_phieu() is not None
```

Tạo mới `tests/test_mo_coi_uid.py` (nguyên văn):

```python
"""V2-0 / bs-863.15, review vòng 1 A01: CLI mồ côi được dọn theo UID của khe, KHÔNG theo số pid/pgid đọc từ file (số có
thể đã cấp lại). Bản ghi chỉ còn để gửi `chay.xong mo-coi`; dọn không chứng minh được → giữ bản ghi + phiếu, khe dừng.
Dọn UID là bản GIẢ."""
import json
from types import SimpleNamespace

import pytest

from tram.kiem.vong_doi import LoiThuHoi
from tram.tho import mo_coi_khe
from tram.tho.mo_coi import don_mo_coi

BAN_GHI = {"pid": 4242, "pgid": 4242, "giao_id": "g-1", "luot": 2, "lan": 1}


@pytest.mark.parametrize("noi_dung, ra", [(json.dumps(BAN_GHI), BAN_GHI), ("không phải json", None),
                                          (json.dumps({"pid": 4242}), None), (None, None)])
def test_don_theo_uid_roi_moi_xoa_ban_ghi(tmp_path, noi_dung, ra):
    p, goi = tmp_path / "pid", []
    if noi_dung is not None:
        p.write_text(noi_dung)
    assert don_mo_coi(p, don=lambda: goi.append(1)) == ra and goi == [1] and not p.exists()


def _hong(*a):
    raise LoiThuHoi("còn tàn dư của UID khe")


def test_don_khong_chung_minh_duoc_thi_giu_ban_ghi(tmp_path):
    (p := tmp_path / "pid").write_text(json.dumps(BAN_GHI))
    with pytest.raises(LoiThuHoi):
        don_mo_coi(p, don=_hong)
    assert json.loads(p.read_text()) == BAN_GHI


def test_khoi_dong_khe_khong_chung_minh_duoc_khe_sach_thi_dung_va_giu_phieu(tmp_path):
    (p := tmp_path / "pid").write_text(json.dumps(BAN_GHI))
    so = SimpleNamespace(pid=p, doc_phieu=lambda: 1 / 0)
    assert mo_coi_khe.don_mo_coi_khe(SimpleNamespace(don_khe=_hong), None, so, SimpleNamespace()) == (None, True)
    assert p.exists()
```

Bản vá `tests/test_phieu_chay_thu_hoi.py`:

```diff
--- a/tests/test_phieu_chay_thu_hoi.py
+++ b/tests/test_phieu_chay_thu_hoi.py
@@ -23,7 +23,7 @@
     monkeypatch.setattr(pcm, "go_khoa", khoa.append)
     monkeypatch.setattr(pcm, "don_phieu", lambda *a: don.append(1))
     with pytest.raises(LoiThuHoi):
-        pcm.chay_phieu(None, SimpleNamespace(k=None, so=None, hop=None), None)
+        pcm.chay_phieu(SimpleNamespace(don_khe=lambda k: None), SimpleNamespace(k=None, so=None, hop=None), None)
     assert lan == [1, 1] and don == [] and khoa == ["/khong-dung"]
 
 
```

Bản vá `tests/test_so_khe_hop_thu.py`:

```diff
--- a/tests/test_so_khe_hop_thu.py
+++ b/tests/test_so_khe_hop_thu.py
@@ -8,7 +8,7 @@
 from tram.tho.cau_hinh_chay import CauHinhChay
 from tram.tho.hop_thu import HopThu
 from tram.tho.khach import LoiKhachTram
-from tram.tho.mo_coi import con_song, dat_khoa, don_mo_coi, ghi_pid, go_khoa, kill_cuc_bo
+from tram.tho.mo_coi import con_song, dat_khoa, go_khoa
 from tram.tho.so_khe import SoKhe, TrangThaiPhieu
 
 LUC = datetime(2026, 10, 13, 3, 0, tzinfo=timezone.utc)
@@ -71,22 +71,6 @@
     assert h.gui_mot(KhachGia(401), "/api/tho/bao", {"request_id": "r-1"}) is None and not h.don()
 
 
-def test_mo_coi_bi_kill_ca_nhom_va_tra_ban_ghi(tmp_path):
-    p = subprocess.Popen([sys.executable, "-c", "import subprocess,sys,time; subprocess.Popen([sys.executable,'-c',"
-                          "'import time; time.sleep(60)']); time.sleep(60)"], start_new_session=True)
-    ghi_pid(tmp_path / "pid", pid=p.pid, giao_id="g-1", luot=2, lan=1)
-    x = don_mo_coi(tmp_path / "pid", kill=kill_cuc_bo, cho=2)
-    p.wait(timeout=5)
-    assert x["giao_id"] == "g-1" and x["lan"] == 1 and not (tmp_path / "pid").exists()
-    try:
-        os.killpg(p.pid, 0)
-        con = True
-    except ProcessLookupError:
-        con = False
-    assert not con                                                            # cả cháu cũng đã chết
-    assert don_mo_coi(tmp_path / "pid", kill=kill_cuc_bo) is None
-
-
 def test_khoa_worktree_h1(tmp_path):
     song = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
     try:
```

Bản vá `tests/tho_chay_gia.py`:

```diff
--- a/tests/tho_chay_gia.py
+++ b/tests/tho_chay_gia.py
@@ -97,6 +97,7 @@
     nc = NguCanhTho(ch, khach_asgi(t.app, t.token["B"]), goc=tmp_path / "tho-home", goc_kho=b.tho.parent,
                     goc_wt=tmp_path / "worktrees", principal_cua=lambda k, wt, ten: PrincipalGia(kb),
                     tao_cli=ChayClaude, chu_ky_nhip=0.2, cho_doc=0.05, cho_xong=5, cho_thu_lai=0.05,
+                    don_uid=lambda pr: None,     # dọn theo UID của khe: GIẢ, không kill -1 thật (test_don_uid)
                     dong_ho=lambda: t.gio[0])    # đồng hồ thợ = đồng hồ trạm giả (han_giu do trạm cấp)
     return MayGia(t, b, nc, kb)
 
```

- [ ] **Step 2: Chạy, thấy đỏ** — `PT tests/test_don_uid.py` rồi `PT tests/test_mo_coi_uid.py tests/test_khe_tan_du.py`. Kết quả thật (mã của Task 4):

```
E   ModuleNotFoundError: No module named 'tram.tho.don_uid'
1 error in 0.06s
---
E       TypeError: don_mo_coi() got an unexpected keyword argument 'don'        (5 ca)
E           AttributeError: 'types.SimpleNamespace' object has no attribute 'principal'
E       TypeError: NguCanhTho.__init__() got an unexpected keyword argument 'don_uid'   (3 ca khe)
9 failed in 1.58s
```

Đối chứng hành vi (cùng mã Task 4, 3 ca `test_khe_tan_du` với `don_uid` gán thẳng vào `nc` thay vì qua máy giả): khe KHÔNG tự dừng — `assert (False)` ×3 (`tu_dung` False sau `join(40)`), lần chạy 2 vẫn spawn sau khi "dọn" báo còn tàn dư; `9 failed in 121.71s`.

- [ ] **Step 3: Mã**

Tạo mới `tram/tho/don_uid.py` (nguyên văn):

```python
"""Dọn theo PHẠM VI UID của khe (V2-0; review vòng 1 A01/A02, bs-863.15) — lưới cuối cho MỌI tiến trình dưới principal
của khe, kể cả tiến trình đã lẩn khỏi tầm chụp của `Nhom` (fork + setsid + cha thoát giữa hai ảnh) và CLI mồ côi của lần
chạy trước. D53: chỉ cơ chế `user` — mỗi khe MỘT tài khoản macOS riêng (`tho.yaml` cấm trùng). Các bước: chứng minh UID
thực của principal (`xac_minh_uid`; không root, không người vận hành) → `kill -KILL -1` CHẠY DƯỚI chính UID đó (nhân chỉ
gửi tới tiến trình cùng UID: không thể trúng tài khoản khác dù số PID/nhóm đã cấp lại) → chụp bảng tiến trình của nhân
tới khi KHÔNG còn tiến trình nào có uid hoặc uid thực = UID đó. Mã thoát của `kill` không là bằng chứng. Bước nào không
chứng minh được → `LoiThuHoi`: khe dừng, không nhận lượt/phiếu mới. Cơ chế `sandbox` (một user dùng chung nhiều khe)
chưa có cách dọn theo phạm vi → `LoiThuHoi` ngay (D53: cổng sandbox đóng).
Chỉ gọi khi khe KHÔNG có việc nào khác đang chạy dưới principal: khởi động khe, đầu mỗi phiếu, sau mỗi lần chạy CLI
(đọc hạn mức lúc rảnh chỉ chạy khi khe không giữ phiếu — `vong_khe.nhip`). `tram tho kiem` chạy song song sẽ bị cắt
(kết quả "không kết luận") — sổ tay: dừng `tram tho chay` trước khi kiểm."""
import os
import subprocess
import time
from collections.abc import Callable

from tram.kiem import danh_tinh
from tram.kiem.bang_tien_trinh import chup_nhan
from tram.kiem.chay_gioi_han import chay_gioi_han
from tram.kiem.vong_doi import LoiThuHoi

GIET = ["/bin/kill", "-KILL", "-1"]
HAN_HET = 5.0


def con_lai(uid: int, chup: Callable = chup_nhan) -> int:
    """Số tiến trình có uid hoặc uid thực = `uid` trong bảng của nhân. Lỗi đọc → OSError."""
    return sum(uid in (t.uid, t.ruid) for t in chup())


def don_uid(pr, *, xac_minh: Callable = danh_tinh.xac_minh_uid, chay: Callable = chay_gioi_han,
            chup: Callable = chup_nhan, han: float = HAN_HET, ngu: Callable = time.sleep) -> None:
    if getattr(pr, "co_che", None) != "user":
        raise LoiThuHoi("principal không phải tài khoản riêng của khe (D53) — không dọn được theo UID, khe dừng")
    try:
        uid = xac_minh(pr.user, pr.boc, pr.kill_nhom)
    except danh_tinh.LoiDanhTinh:
        raise LoiThuHoi("UID thực của principal chưa chứng minh — không dọn theo UID, khe dừng") from None
    if uid in (0, os.getuid(), os.geteuid()):                     # phòng thủ thêm: kill -1 không bao giờ ngoài khe
        raise LoiThuHoi("UID principal trùng root/tài khoản đang chạy — không dọn, khe dừng")
    try:
        chay(pr.boc(GIET), kill=pr.kill_nhom, capture_output=True, timeout=10, env={"PATH": "/usr/bin:/bin"})
    except (OSError, subprocess.SubprocessError):
        raise LoiThuHoi("kill -1 dưới principal không chạy được — khe dừng") from None
    het = time.monotonic() + han
    while True:
        try:
            n = con_lai(uid, chup)
        except (OSError, ValueError):
            raise LoiThuHoi("không đọc được bảng tiến trình sau kill -1 — khe dừng") from None
        if n == 0:
            return
        if time.monotonic() >= het:
            raise LoiThuHoi(f"còn {n} tiến trình của UID khe sau kill -1 (setuid hay kẹt trong nhân) — khe dừng")
        ngu(0.2)
```

Bản vá `tram/tho/mo_coi.py`:

```diff
--- a/tram/tho/mo_coi.py
+++ b/tram/tho/mo_coi.py
@@ -1,18 +1,17 @@
-"""CLI mồ côi và khoá worktree (spec 3 §7.2, H1). `dang-chay.pid` = {pid, pgid, giao_id, luot, lan} của lần chạy
-đang sống — ghi NGAY sau khi spawn, xoá khi lần chạy kết thúc. `tram tho chay` khởi động: pid còn sống → kill cả nhóm
-(qua principal — `kill`), rồi bảo đảm có `chay.xong {ket_thuc: "mo-coi"}` sau `chay.bat_dau` đã ghi bền (G35).
+"""CLI mồ côi và khoá worktree (spec 3 §7.2, H1; V2-0 bs-863.15, review vòng 1 A01/A02). `dang-chay.pid` = {pid, pgid,
+giao_id, luot, lan} của lần chạy đang sống — ghi NGAY sau khi spawn, xoá khi lần chạy kết thúc VÀ khe đã dọn theo UID.
+`tram tho chay` khởi động: dọn TOÀN UID của khe (`don` — `tho.don_uid`: kill -1 dưới chính principal rồi chứng minh
+không còn tiến trình nào của UID đó) rồi mới xoá bản ghi; KHÔNG BAO GIỜ gửi tín hiệu theo số pid/pgid đọc từ file (số có
+thể đã cấp lại — lỗi .15). Bản ghi chỉ còn để gửi `chay.xong {ket_thuc: "mo-coi"}` sau `chay.bat_dau` đã ghi bền (G35);
+bản ghi cũ/hỏng không cản việc dọn. Dọn không chứng minh được → `LoiThuHoi`, GIỮ bản ghi, khe dừng.
 Khoá `.tram/khoa` trong worktree (pid + giao_id): còn pid sống → không chạy lần mới (lớp bổ sung — agent ghi được
 `.tram/`; hàng rào thật là kho phiếu của trạm + pid của tiến trình quản lý)."""
 import json
 import os
-import signal
-import time
 from collections.abc import Callable
 from pathlib import Path
 
-from tram.kiem.vong_doi import kill_cuc_bo  # noqa: F401 — tên cũ; một định nghĩa ở primitive P1
-
-Kill = Callable[[int, int], None]
+from tram.kiem.vong_doi import Kill, kill_cuc_bo  # noqa: F401 — tên cũ; một định nghĩa ở primitive P1
 
 
 def con_song(pid: int) -> bool:
@@ -23,15 +22,6 @@
     except PermissionError:
         return True                                     # tiến trình của user khác (principal) vẫn đang sống
     return True
-
-
-def dung_nhom(pgid: int, *, kill: Kill, cho: float = 10.0) -> None:
-    """SIGTERM cả nhóm, chờ tối đa `cho` giây, rồi SIGKILL (§6.3 dừng cứng / §7.2)."""
-    kill(pgid, signal.SIGTERM)
-    het = time.monotonic() + cho
-    while con_song(pgid) and time.monotonic() < het:
-        time.sleep(0.05)
-    kill(pgid, signal.SIGKILL)
 
 
 def ghi_pid(p: Path, *, pid: int, giao_id: str, luot: int, lan: int) -> None:
@@ -45,16 +35,13 @@
         return None
 
 
-def don_mo_coi(p: Path, *, kill: Kill, cho: float = 10.0) -> dict | None:
-    """Trả bản ghi pid của lần chạy dở (để người gọi gửi `chay.xong mo-coi`), đã kill nếu còn sống; xoá file."""
+def don_mo_coi(p: Path, *, don: Callable[[], None]) -> dict | None:
+    """Bản ghi của lần chạy dở (dict có `giao_id`, `lan`; hỏng → None) SAU KHI `don()` đã chứng minh khe sạch; xoá file.
+    `don` ném (`LoiThuHoi`) → file giữ nguyên, lỗi nổi lên."""
     x = doc_pid(p)
-    if x is None:
-        p.unlink(missing_ok=True)
-        return None
-    if con_song(x["pid"]):
-        dung_nhom(x["pgid"], kill=kill, cho=cho)
+    don()
     p.unlink(missing_ok=True)
-    return x
+    return x if isinstance(x, dict) and isinstance(x.get("giao_id"), str) and isinstance(x.get("lan"), int) else None
 
 
 def dat_khoa(wt: Path, *, pid: int, giao_id: str) -> bool:
```

Bản vá `tram/tho/mo_coi_khe.py`:

```diff
--- a/tram/tho/mo_coi_khe.py
+++ b/tram/tho/mo_coi_khe.py
@@ -1,25 +1,29 @@
-"""Khởi động một khe trong `tram tho chay` (spec 3 §7.2; 3a-1 G12): kill CLI mồ côi của lần chạy trước qua principal
-của khe, bảo đảm đã gửi `chay.xong {mo-coi}` cho phiếu đang giữ, trả lại phiếu đó (đọc `phieu.json`) để chạy tiếp."""
+"""Khởi động một khe trong `tram tho chay` (spec 3 §7.2; 3a-1 G12; V2-0, review vòng 1 A02): dọn TOÀN UID của khe
+(`nc.don_khe` — gồm cả CLI mồ côi của lần chạy trước), bảo đảm đã gửi `chay.xong {mo-coi}` cho phiếu đang giữ, trả lại
+phiếu đó (đọc `phieu.json`) để chạy tiếp. Không chứng minh được khe sạch → (None, True): khe DỪNG, giữ bản ghi và
+phiếu."""
+from tram.kiem.vong_doi import LoiThuHoi
 from tram.phieu.mo_hinh import Phieu
 from tram.tho.cau_hinh import KheCauHinh
 from tram.tho.chuan_bi import gui_su_kien
 from tram.tho.hop_thu import HopThu
 from tram.tho.mo_coi import don_mo_coi
 from tram.tho.ngu_canh import NguCanhTho
-from tram.tho.principal import ChuaCoPrincipal
 from tram.tho.so_khe import SoKhe, TrangThaiPhieu
 
 
-def don_mo_coi_khe(nc: NguCanhTho, k: KheCauHinh, so: SoKhe, hop: HopThu) -> TrangThaiPhieu | None:
+def don_mo_coi_khe(nc: NguCanhTho, k: KheCauHinh, so: SoKhe, hop: HopThu) -> tuple[TrangThaiPhieu | None, bool]:
+    """(phiếu đang giữ, khe phải dừng)."""
     try:
-        kill = nc.principal(k, None, "mo-coi").kill_nhom
-    except ChuaCoPrincipal:
-        kill = None
-    x = don_mo_coi(so.pid, kill=kill) if kill else None
+        x = don_mo_coi(so.pid, don=lambda: nc.don_khe(k))
+    except LoiThuHoi:
+        print("Chưa chứng minh được khe sạch (dọn theo UID của principal) — giữ bản ghi và phiếu, dừng khe; "
+              "Đại ca kiểm theo sổ tay G7")
+        return None, True
     tt = so.doc_phieu()
     if x and tt and Phieu.model_validate(tt.phieu).giao_id == x["giao_id"]:
         p = Phieu.model_validate(tt.phieu)
         if not hop.co(lambda d, t: t.get("loai") == "chay.xong" and t.get("du_lieu", {}).get("lan") == x["lan"]
                       and t.get("giao_id") == p.giao_id):
             gui_su_kien(nc, hop, p, "chay.xong", {"lan": x["lan"], "ket_thuc": "mo-coi"}, x["lan"])
-    return tt
+    return tt, False
```

Bản vá `tram/tho/mot_lan.py`:

```diff
--- a/tram/tho/mot_lan.py
+++ b/tram/tho/mot_lan.py
@@ -74,6 +74,7 @@
         raise
     finally:
         hen.cancel()
+    nc.don_khe(pc.k)                    # A02: còn tàn dư (lẩn khỏi tầm chụp) → LoiThuHoi, GIỮ pid, không lần sau
     so.pid.unlink(missing_ok=True)
     tt.token_ra += kq.token_ra
     pc.luu()
```

Bản vá `tram/tho/ngu_canh.py`:

```diff
--- a/tram/tho/ngu_canh.py
+++ b/tram/tho/ngu_canh.py
@@ -10,8 +10,11 @@
 
 from tram.chay_cli.bo_cli import BO_CLI
 from tram.duong_dan import tram_home
+from tram.kiem.vong_doi import LoiThuHoi
 from tram.tho.cau_hinh import CauHinhTho, KheCauHinh
+from tram.tho.don_uid import don_uid
 from tram.tho.khach import KhachTram
+from tram.tho.principal import ChuaCoPrincipal
 from tram.tho.principal_khe import principal_cua
 
 
@@ -35,11 +38,20 @@
     cho_doc: float = 1.0                       # đọc hàng đợi `tram bao`
     cho_xong: float = 60.0                     # §7.4: chờ CLI thoát sau `xong`
     cho_thu_lai: float = 5.0                   # gửi lại da-push tạm
+    don_uid: Callable | None = None             # (principal) -> None | ném LoiThuHoi; None → tho.don_uid.don_uid (A02)
 
     def principal(self, k: KheCauHinh, wt: Path | None, ten: str):
         if self.principal_cua is not None:
             return self.principal_cua(k, wt, ten)
         return principal_cua(self.ch, k, goc=self.goc, goc_wt=self.goc_wt, wt=wt, ten=ten)
 
+    def don_khe(self, k: KheCauHinh) -> None:
+        """Dọn theo UID của khe (A02); không chứng minh được khe sạch → `LoiThuHoi` (khe dừng, không nhận việc)."""
+        try:
+            pr = self.principal(k, None, "don-uid")
+        except ChuaCoPrincipal:
+            raise LoiThuHoi("khe chưa có principal hợp lệ — không chứng minh được khe sạch") from None
+        (self.don_uid or don_uid)(pr)
+
     def nguon_han_muc(self, cli="claude"):
         return self.nguon or BO_CLI[cli].tao_nguon(thang=self.ch.chay.thang_utilization)
```

Bản vá `tram/tho/phieu_chay.py`:

```diff
--- a/tram/tho/phieu_chay.py
+++ b/tram/tho/phieu_chay.py
@@ -76,6 +76,7 @@
 
 
 def chay_phieu(nc: NguCanhTho, vk, tt: TrangThaiPhieu) -> str:
+    nc.don_khe(vk.k)                            # A02: khe sạch theo UID TRƯỚC mọi việc của phiếu (không → LoiThuHoi)
     vk.buoc = "chuan_bi"
     pc = chuan_bi(nc, vk.k, vk.so, vk.hop, tt)
     if isinstance(pc, str):
```

Bản vá `tram/tho/vong_khe.py`:

```diff
--- a/tram/tho/vong_khe.py
+++ b/tram/tho/vong_khe.py
@@ -1,8 +1,8 @@
 """Vòng của MỘT khe trong `tram tho chay` (spec 3 §6.2, §7.2): nhịp tim 30 giây kiêm xin việc (luồng nền, kể cả khi
 đang chạy phiếu — mang `giao_id`/`luot`/`buoc_tho`/`han_muc`; `tiep_tuc: false` → `lenh` + dừng lần chạy), và vòng
-chính nhận phiếu → `chay_phieu`. Khởi động: CLI mồ côi bị kill + bảo đảm `chay.xong {mo-coi}`; phiếu đang giữ (đọc
-lại `phieu.json`) được chạy tiếp từ lần kế — trạm không trao lại phiếu (3a-1 G12). Hạn mức lúc rảnh đọc SAU khi gửi
-nhịp, dưới principal của khe (`han_muc_ranh`, bs-78r.10)."""
+chính nhận phiếu → `chay_phieu`. Khởi động: dọn theo UID của khe (gồm CLI mồ côi), bảo đảm `chay.xong {mo-coi}`;
+chưa chứng minh được khe sạch → khe dừng ngay; phiếu đang giữ (`phieu.json`) chạy tiếp từ lần kế (3a-1 G12). Hạn
+mức lúc rảnh đọc SAU khi gửi nhịp, dưới principal của khe (`han_muc_ranh`, bs-78r.10)."""
 import threading
 import time
 
@@ -36,7 +36,7 @@
         self.han_muc = DocHanMucRanh(nc, k, self.khe_id, self.so)
 
     def khoi_dong(self) -> None:
-        tt = don_mo_coi_khe(self.nc, self.k, self.so, self.hop)
+        tt, self.hong = don_mo_coi_khe(self.nc, self.k, self.so, self.hop)
         self.hop.gui(self.nc.khach)
         self.phieu_moi = tt
 
```

- [ ] **Step 4: Chạy, thấy xanh** — `PT tests/test_don_uid.py tests/test_mo_coi_uid.py tests/test_khe_tan_du.py tests/test_so_khe_hop_thu.py tests/test_phieu_chay_thu_hoi.py tests/test_kich_ban_3a2.py tests/test_chay_cli_vong_doi.py tests/test_nhip_han_muc.py tests/test_tho_chuan_bi.py tests/test_tho_lenh_chay.py tests/test_tho_theo_doi_ket_thuc.py tests/test_bo_codex.py tests/test_codex_chay.py` → `73 passed`.

- [ ] **Step 5: Cả bộ** — `PT` → `2890` (+19, −1 ca cũ bỏ; thu thập trên cây A-T1…T5), nhật ký chặn 0 dòng mới.

- [ ] **Step 6: Commit** — `fix(tho): khe chỉ sang lượt sau khi dọn theo UID của khe chứng minh sạch; mồ côi không giết theo số (V2-0, bs-863.15, A01/A02)`

## Task 6 — Thăm dò cách ly có hạn, đúng principal, mỗi loại một bằng chứng; tàn dư sau thăm dò là ĐỎ (V2-6b, bs-863.14; review vòng 1 A04, A02)

**Files:** tạo `tram/tho/cham_tham_do.py`; sửa `tram/tho/kiem_am.py`, `tram/tho/kiem_cong.py` (`cach_ly`), `tram/chu/kiem_cach_ly.py`; test mới `tests/test_cham_tham_do.py`, `tests/test_kiem_am_p1.py`, `tests/test_tham_do_principal.py`; sửa `tests/test_kiem_am.py`, `tests/test_kiem_cong.py`, `tests/test_chu_tho.py`.

**Interfaces:**
- `ThamDo(ten, argv, kieu, doi_chung=None)` — `kieu` BẮT BUỘC ∈ `doc | ghi | sua | keychain | http | nc | tram | ok` (bỏ `loi` chung); `doi_chung: () -> bool` chạy dưới tài khoản quản lý TRƯỚC thăm dò (đích có thật).
- `cham_tham_do.cham(kieu, ma, out, err) -> (dat | khong-dat | khong-ket-luan, lý do cố định)`; `co_muc_keychain(k, *, chay=subprocess.run) -> bool` (không `-w`); `mo_cong("host:port", *, noi=socket.create_connection) -> bool`.
- `tham_do_khe(..., co_muc=co_muc_keychain)`; `tham_do_day_du(..., mo=mo_cong)`; đọc thư mục → `/bin/ls`, đọc file → `/bin/cat`.
- `chay_tham_do(ds, *, boc, env, kill, timeout=30, chay=chay_gioi_han) -> list[KetQuaThamDo]` — `kill` BẮT BUỘC; dương trước; đối chứng hỏng/ném → "không kết luận: đối chứng hỏng…", không chạy thăm dò; `LoiThuHoi` → dừng phần còn lại.
- `kiem_cong.cach_ly(..., chay_td=chay_tham_do, xac_minh=xac_minh_uid, chup=chup_nhan)`; `_uid(p, xac_minh) -> (uid | None, lý do | None)`; sau thăm dò `con_lai(uid, chup) > 0` → thêm "tàn dư" ĐỎ (chỉ quan sát), không đọc được bảng → "không kết luận".
- `kiem_cach_ly(principal, *, chay_td, doc_pk, xac_minh=xac_minh_uid)`; principal khe dựng `Principal("user", tên)` (`sudo -n -H -u …`), bỏ `_boc_sudo`.

- [ ] **Step 1: Viết test**

Tạo mới `tests/test_cham_tham_do.py` (nguyên văn):

```python
"""Review vòng 1 A04: mỗi loại thăm dò một bằng chứng riêng; lỗi hạ tầng (curl 7/28 + `000`, thiếu công cụ 127, 404/500,
mục tiêu không tồn tại, mã chưa phân loại) KHÔNG BAO GIỜ là "bị chặn"; kết quả chỉ mang lý do cố định — không chép
stdout/stderr (có thể chứa bí mật). Chạy và đối chứng GIẢ (CompletedProcess dựng tay) — không spawn, không Keychain."""
import subprocess

import pytest

from tram.kiem.vong_doi import kill_cuc_bo
from tram.tho.cham_tham_do import co_muc_keychain, mo_cong
from tram.tho.kiem_am import ThamDo, chay_tham_do, tham_do_day_du, tham_do_khe

BI_MAT = "tok-BI-MAT-123"
DUONG = ThamDo("hợp lệ", ["/usr/bin/true"], "ok")


def mot(t, ma, out="", err="", goi=None):
    """Chạy [dương, t] với kết quả GIẢ cho t; trả kết quả của t."""
    def chay(argv, **kw):
        (goi if goi is not None else []).append(argv)
        return subprocess.CompletedProcess(argv, *((0, "", "") if argv == DUONG.argv else (ma, out, err)))
    return chay_tham_do([DUONG, t], boc=lambda a: a, env={}, kill=kill_cuc_bo, chay=chay)[1]


@pytest.mark.parametrize("ma, out, dat, ly", [
    (7, "000", False, "không kết luận"), (28, "000", False, "không kết luận"), (0, "000", False, "không kết luận"),
    (0, "404", False, "không kết luận"), (0, "500", False, "không kết luận"), (0, BI_MAT, False, "không kết luận"),
    (0, "403", True, "HTTP 403"), (0, "401", True, "HTTP 401"), (0, "200", False, "nhận"), (0, "422", False, "nhận")])
def test_http_chi_dat_khi_api_tu_choi(ma, out, dat, ly):
    k = mot(ThamDo("api", ["/usr/bin/curl"], "http"), ma, out, f"curl: lỗi {BI_MAT}")
    assert k.dat is dat and ly in k.chi_tiet and BI_MAT not in k.chi_tiet


@pytest.mark.parametrize("kieu, ma, err, dat", [
    ("doc", 1, "cat: x: Permission denied", True), ("doc", 1, "cat: x: No such file or directory", None),
    ("doc", 1, "cat: x: Is a directory", None), ("doc", 127, "env: cat: No such file", None), ("doc", 126, "", None),
    ("doc", -9, "", None), ("doc", 0, "", False), ("ghi", 1, "touch: x: Operation not permitted", True),
    ("sua", 1, "touch: x: Read-only file system", None),
    ("keychain", 44, "SecKeychainSearchCopyNext: The specified item could not be found in the keychain.", True),
    ("keychain", 44, "", None), ("keychain", 36, "User interaction is not allowed.", None), ("keychain", 0, "", False),
    ("nc", 1, "nc: connectx to 127.0.0.1 port 3306 (tcp) failed: Operation not permitted", True),
    ("nc", 1, "nc: connectx to 127.0.0.1 port 3306 (tcp) failed: Connection refused", None),
    ("tram", 1, "PermissionError: [Errno 13] Permission denied: '/x/su-kien.db'", True),
    ("tram", 127, "env: tram: No such file or directory", None)])
def test_am_chi_dat_khi_co_dau_hieu_tu_choi_quyen(kieu, ma, err, dat):
    k = mot(ThamDo("x", ["/bin/x"], kieu), ma, BI_MAT, f"{err} {BI_MAT}")
    assert k.dat is bool(dat) and BI_MAT not in k.chi_tiet
    assert ("không kết luận" in k.chi_tiet) is (dat is None)


@pytest.mark.parametrize("doi_chung", [lambda: False, lambda: 1 / 0])
def test_doi_chung_hong_thi_khong_chay_va_khong_ket_luan(doi_chung):
    goi = []
    k = mot(ThamDo("đọc", ["/bin/cat", "/x"], "doc", doi_chung), 1, "", "Permission denied", goi)
    assert k.dat is False and "đối chứng" in k.chi_tiet and goi == [DUONG.argv]


def test_bo_tham_do_doi_chung_dung_dich(tmp_path):
    (tep := tmp_path / "phieu.json").write_text("{}")
    rg = tham_do_khe(keychain=["tram-tho-token", "khong-co"], doc_cam=[tep, tmp_path / "khong-co", tmp_path],
                     ghi_cam=[tmp_path, tmp_path / "khong-co"], ghi_duoc=tmp_path, ghi_tep_cam=[tep],
                     co_muc=lambda k: k == "tram-tho-token")
    assert [(t.kieu, t.doi_chung()) for t in rg if t.kieu != "ok"] == [
        ("keychain", True), ("keychain", False), ("doc", True), ("doc", False), ("doc", True), ("ghi", True),
        ("ghi", False), ("sua", True)]
    assert rg[4].argv == ["/bin/ls", str(tmp_path)] and rg[2].argv == ["/bin/cat", str(tep)]   # thư mục: ls, không cat
    dd = tham_do_day_du(rut_gon=[], api="http://x", dai_ca_login="a", may_b="b", db=["127.0.0.1:3306", "h:1"],
                        tram_home_tram=tmp_path, mo=lambda d: d == "127.0.0.1:3306")
    assert [(t.kieu, t.doi_chung and t.doi_chung()) for t in dd if t.kieu != "ok"] == [
        ("http", None), ("nc", True), ("nc", False), ("tram", True)]


def test_doi_chung_keychain_khong_lay_mat_khau_va_cong_db():
    goi = []

    def chay(argv, **kw):
        goi.append(argv)
        return subprocess.CompletedProcess(argv, 0 if argv[-1] == "co" else 44, b"", b"")
    assert co_muc_keychain("co", chay=chay) and not co_muc_keychain("khong", chay=chay) and "-w" not in goi[0]
    assert not co_muc_keychain("x", chay=lambda *a, **k: (_ for _ in ()).throw(OSError("security")))

    class Noi:
        def close(self):
            pass
    assert mo_cong("127.0.0.1:3306", noi=lambda dich, timeout: Noi())
    assert not mo_cong("127.0.0.1:3306", noi=lambda dich, timeout: (_ for _ in ()).throw(ConnectionRefusedError()))
```

Bản vá `tests/test_chu_tho.py`:

```diff
--- a/tests/test_chu_tho.py
+++ b/tests/test_chu_tho.py
@@ -71,10 +71,10 @@
                                                  "          tram_kiem: user:tram-kiem}\n")
     da = {}
 
-    def chay_td(ds, *, boc, env):
+    def chay_td(ds, *, boc, env, kill):
         da["boc"], da["ten"] = boc(["/bin/cat", "x"]), [t.ten for t in ds]
         return [KetQuaThamDo(t.ten, "API" not in t.ten, "mã 0") for t in ds]
-    van_ban, ma = kiem_cach_ly(["user:tram-k-b-claude-1", "rac"], chay_td=chay_td)
+    van_ban, ma = kiem_cach_ly(["user:tram-k-b-claude-1", "rac"], chay_td=chay_td, xac_minh=lambda *a: 600)
     assert ma == 1 and "header GIẢ ĐƯỢC" in van_ban and "[ĐỎ] rac:" in van_ban
     assert da["boc"] == tu_cach_ly("user:tram-kiem").boc_lenh(["/bin/cat", "x"])      # đúng argv của kiểm lại (3c)
     assert "kết nối DB nghiệp vụ 127.0.0.1:3306" in da["ten"] and "[ĐỎ] user:tram-kiem — API Duyệt" in van_ban
```

Bản vá `tests/test_kiem_am.py`:

```diff
--- a/tests/test_kiem_am.py
+++ b/tests/test_kiem_am.py
@@ -2,14 +2,16 @@
 import os
 import sys
 
+from tram.kiem.vong_doi import kill_cuc_bo
 from tram.tho.kiem_am import ThamDo, chay_tham_do, tham_do_day_du, tham_do_khe
 
 
 def boc_gia(dich: dict):
-    """Thay mỗi argv bằng lệnh python trả mã/xuất đã định (CHỈ DÙNG TRONG TEST)."""
+    """Thay mỗi argv bằng lệnh python trả mã/stdout/stderr đã định (CHỈ DÙNG TRONG TEST)."""
     def boc(argv):
-        ma, out = dich.get(argv[0], (0, ""))
-        return [sys.executable, "-c", f"import sys; print({out!r}); sys.exit({ma})"]
+        ma, out, *loi = dich.get(argv[0], (0, ""))
+        return [sys.executable, "-c", f"import sys; print({out!r}); print({''.join(loi)!r}, file=sys.stderr); "
+                f"sys.exit({ma})"]
     return boc
 
 
@@ -29,18 +31,19 @@
 
 
 def test_cham_bi_chan_va_duong():
-    ds = [ThamDo("keychain", ["/usr/bin/security"]), ThamDo("đọc", ["/bin/cat"]),
+    ds = [ThamDo("keychain", ["/usr/bin/security"], "keychain"), ThamDo("đọc", ["/bin/cat"], "doc"),
           ThamDo("api 403", ["/usr/bin/curl"], "http"), ThamDo("api 422", ["/usr/bin/curl2"], "http"),
           ThamDo("hợp lệ", ["/usr/bin/true"], "ok")]
-    kq = chay_tham_do(ds, boc=boc_gia({"/usr/bin/security": (44, ""), "/bin/cat": (0, "token!"),
-                                       "/usr/bin/curl": (0, "403"), "/usr/bin/curl2": (0, "422"),
-                                       "/usr/bin/true": (0, "")}), env=dict(os.environ))
+    kq = chay_tham_do(ds, boc=boc_gia({"/usr/bin/security": (44, "", "The specified item could not be found"),
+                                       "/bin/cat": (0, "token!"), "/usr/bin/curl": (0, "403"),
+                                       "/usr/bin/curl2": (0, "422"), "/usr/bin/true": (0, "")}), env=dict(os.environ),
+                      kill=kill_cuc_bo)
     assert [k.dat for k in kq] == [True, False, True, False, True]
-    assert kq[2].chi_tiet == "mã 0, HTTP 403"
+    assert kq[2].chi_tiet == "API từ chối (HTTP 403)" and "token!" not in kq[1].chi_tiet
 
 
 def test_git_hook_that_khong_chay_voi_hook_tat(tmp_path):
     ds = [t for t in tham_do_day_du(rut_gon=[], api="http://x", dai_ca_login="a", may_b="b", db=[],
                                     tram_home_tram=None) if t.ten.startswith("git hook")]
     env = {**os.environ, "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1", "TMPDIR": str(tmp_path)}
-    assert chay_tham_do(ds, boc=lambda a: a, env=env)[0].dat
+    assert chay_tham_do(ds, boc=lambda a: a, env=env, kill=kill_cuc_bo)[0].dat
```

Tạo mới `tests/test_kiem_am_p1.py` (nguyên văn):

```python
"""bs-863.14: thăm dò cách ly qua primitive P1 — hạn tuyệt đối, thu hồi cả cây bằng `kill` của principal; lỗi hạ tầng
(quá hạn, không khởi chạy, chưa thu hồi) KHÔNG BAO GIỜ thành "bị chặn"; dương hỏng → âm không kết luận. Chạy/kill GIẢ,
trừ một ca dùng `python -c` của chính user đang test (tự thu hồi đúng PID mình tạo)."""
import os
import signal
import subprocess
import sys
import time

from tram.kiem.vong_doi import LoiThuHoi, kill_cuc_bo
from tram.tho.kiem_am import ThamDo, chay_tham_do

DS = [ThamDo("keychain", ["/usr/bin/security"], "keychain"), ThamDo("đọc", ["/bin/cat"], "doc"),
      ThamDo("hợp lệ", ["/usr/bin/true"], "ok")]
LOI = {44: "The specified item could not be found in the keychain.", 1: "cat: x: Permission denied"}


def chay_gia(ket: dict, goi: list):
    def chay(argv, **kw):
        goi.append((argv, kw))
        r = ket[argv[-1]]
        if isinstance(r, BaseException):
            raise r
        return subprocess.CompletedProcess(argv, r, "", LOI.get(r, ""))
    return chay


def test_qua_p1_voi_kill_cua_principal_duong_chay_truoc():
    goi, kill = [], lambda g, s: None
    kq = chay_tham_do(DS, boc=lambda a: ["/usr/bin/sudo", "-n", *a], env={"PATH": "/x"}, kill=kill,
                      chay=chay_gia({"/usr/bin/security": 44, "/bin/cat": 1, "/usr/bin/true": 0}, goi))
    assert [k.dat for k in kq] == [True, True, True] and [k.ten for k in kq] == ["keychain", "đọc", "hợp lệ"]
    assert [a[-1] for a, _ in goi] == ["/usr/bin/true", "/usr/bin/security", "/bin/cat"]
    assert all(a[:2] == ["/usr/bin/sudo", "-n"] and kw["kill"] is kill and kw["timeout"] == 30
               and kw["env"] == {"PATH": "/x"} for a, kw in goi)


def test_loi_ha_tang_khong_bao_gio_la_bi_chan():
    kq = chay_tham_do(DS, boc=lambda a: a, env={}, kill=kill_cuc_bo, chay=chay_gia(
        {"/usr/bin/security": subprocess.TimeoutExpired("x", 30), "/bin/cat": OSError("spawn"),
         "/usr/bin/true": 0}, []))
    assert [k.dat for k in kq] == [False, False, True] and all("không kết luận" in k.chi_tiet for k in kq[:2])


def test_duong_hong_thi_am_khong_chay_khong_xanh():
    goi = []
    kq = chay_tham_do(DS, boc=lambda a: a, env={}, kill=kill_cuc_bo, chay=chay_gia({"/usr/bin/true": 1}, goi))
    assert [k.dat for k in kq] == [False, False, False] and len(goi) == 1 and "dương" in kq[0].chi_tiet


def test_chua_thu_hoi_duoc_thi_dung_khong_chay_tiep():
    goi = []
    kq = chay_tham_do(DS, boc=lambda a: a, env={}, kill=kill_cuc_bo, chay=chay_gia(
        {"/usr/bin/true": 0, "/usr/bin/security": LoiThuHoi("x"), "/bin/cat": 1}, goi))
    assert [k.dat for k in kq] == [False, False, True] and [a[-1] for a, _ in goi] == ["/usr/bin/true",
                                                                                          "/usr/bin/security"]


def test_that_qua_han_va_kill_bi_tu_choi_van_tra_trong_han(tmp_path):
    pid = tmp_path / "pid"
    treo = ("import os, signal, sys, time; signal.signal(signal.SIGTERM, signal.SIG_IGN); "
            f"open({str(pid)!r}, 'w').write(str(os.getpid())); time.sleep(30)")

    def tu_choi(g, s):
        raise PermissionError
    t0 = time.monotonic()
    try:
        kq = chay_tham_do([ThamDo("treo", ["x"], "doc")], boc=lambda a: [sys.executable, "-c", treo],
                          env=dict(os.environ), kill=tu_choi, timeout=0.5)
        assert time.monotonic() - t0 < 10 and kq[0].dat is False and "không kết luận" in kq[0].chi_tiet
    finally:
        if pid.exists():
            try:
                os.kill(int(pid.read_text()), signal.SIGKILL)
            except ProcessLookupError:
                pass
```

Bản vá `tests/test_kiem_cong.py`:

```diff
--- a/tests/test_kiem_cong.py
+++ b/tests/test_kiem_cong.py
@@ -55,10 +55,11 @@
 def test_cach_ly_xanh_khi_moi_tham_do_dat_do_khi_mot_cai_hong(tmp_path):
     ch, da = cau_hinh(tmp_path, ("user:tram-k-1", None)), []
 
-    def chay_td(ds, *, boc, env):
+    def chay_td(ds, *, boc, env, kill):
         da.append([t.ten for t in ds])
         return [KetQuaThamDo(t.ten, "Keychain" not in t.ten, "mã 0") for t in ds]
-    ra = cach_ly(ch, ["hr-codex"], goc=tmp_path, goc_wt=tmp_path / "wt", chay_td=chay_td)
+    ra = cach_ly(ch, ["hr-codex"], goc=tmp_path, goc_wt=tmp_path / "wt", chay_td=chay_td,
+                 xac_minh=lambda ten, boc, kill: 600, chup=lambda: [])
     assert [m.muc_do for m in ra] == ["do", "do"] and "đọc Keychain tram-tho-token" in ra[0].chi_tiet
     assert f"sửa {tmp_path}/kho/hr-codex/.git/config" in da[0] and "chờ spike S6" in ra[1].chi_tiet
 
```

Tạo mới `tests/test_tham_do_principal.py` (nguyên văn):

```python
"""bs-863.14: thăm dò cách ly của `tram tho kiem` và `tram chu kiem-cach-ly` CHỈ chạy sau khi UID thực của principal
được chứng minh, qua `sudo -n` (không hỏi mật khẩu, không cần tty), `kill` của đúng principal, env dựng mới không HOME
của quản lý. Không sudo/user thật: xác minh UID và chạy thăm dò đều GIẢ."""
from test_kiem_cong import cau_hinh
from tram.chu.kiem_cach_ly import kiem_cach_ly
from tram.kiem.cay_tien_trinh import TienTrinh
from tram.kiem.danh_tinh import LoiDanhTinh
from tram.kiem.vong_doi import LoiThuHoi
from tram.tho.kiem_am import KetQuaThamDo
from tram.tho.kiem_cong import cach_ly


def ghi(da):
    def chay_td(ds, *, boc, env, kill):
        da.append({"argv": boc(["/bin/cat", "x"]), "env": env, "kill": kill})
        return [KetQuaThamDo(t.ten, True, "mã 1") for t in ds]
    return chay_td


def test_tho_kiem_uid_truoc_roi_tham_do_voi_kill_va_env_cua_principal(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", "/Users/quan-ly")
    ch, da, xm = cau_hinh(tmp_path, ("user:tram-k-1",)), [], []
    ra = cach_ly(ch, ["hr"], goc=tmp_path, goc_wt=tmp_path / "wt", chay_td=ghi(da),
                 xac_minh=lambda ten, boc, kill: xm.append(ten) or 600, chup=lambda: [])
    assert [m.muc_do for m in ra] == ["xanh"] and xm == ["tram-k-1"]
    assert da[0]["argv"][:5] == ["/usr/bin/sudo", "-n", "-H", "-u", "tram-k-1"] and da[0]["env"] == {
        "PATH": "/x/bin", "LANG": "C.UTF-8"} and da[0]["kill"].__self__.user == "tram-k-1"


def test_tho_kiem_uid_chua_chung_minh_thi_do_va_khong_tham_do(tmp_path):
    ch, da = cau_hinh(tmp_path, ("user:tram-k-1", "user:tram-k-2")), []

    def xm(ten, boc, kill):
        raise (LoiDanhTinh("x") if ten == "tram-k-1" else LoiThuHoi("y"))
    ra = cach_ly(ch, [], goc=tmp_path, goc_wt=tmp_path, chay_td=ghi(da), xac_minh=xm)
    assert [m.muc_do for m in ra] == ["do", "do"] and da == [] and "UID" in ra[0].chi_tiet


def test_chu_kiem_cach_ly_sudo_n_kill_principal_va_uid_truoc(tram_home_tam):
    tram_home_tam.mkdir(parents=True, exist_ok=True)
    (tram_home_tam / "cau-hinh.yaml").write_text("cach_ly: {tram_kiem: user:tram-kiem}\n")
    da, xm = [], []

    def xac_minh(ten, boc, kill):
        xm.append(ten)
        if ten == "tram-exec":
            raise LoiDanhTinh("x")
    van_ban, ma = kiem_cach_ly(["user:tram-k-b-claude-1", "sandbox:tram-exec"], chay_td=ghi(da), xac_minh=xac_minh)
    assert xm == ["tram-k-b-claude-1", "tram-exec", "tram-kiem"] and len(da) == 2
    assert da[0]["argv"][:5] == ["/usr/bin/sudo", "-n", "-H", "-u", "tram-k-b-claude-1"]
    assert da[0]["kill"].__self__.user == "tram-k-b-claude-1" and da[1]["kill"].__self__.ten == "tram-kiem"
    assert "[ĐỎ] sandbox:tram-exec: UID" in van_ban and ma == 1
    assert all(set(d["env"]) == {"PATH", "LANG"} for d in da)



def test_tho_kiem_con_tien_trinh_cua_principal_sau_tham_do_thi_do_khong_giet(tmp_path):
    """A02: chỉ quan sát — bảng tiến trình còn tiến trình của UID principal → ĐỎ; không gửi tín hiệu nào."""
    ch, da = cau_hinh(tmp_path, ("user:tram-k-1",)), []
    con = [TienTrinh(7000, 1, 7000, 600, 600, 1)]
    ra = cach_ly(ch, [], goc=tmp_path, goc_wt=tmp_path / "wt", chay_td=ghi(da), xac_minh=lambda *a: 600,
                 chup=lambda: con)
    assert [m.muc_do for m in ra] == ["do"] and "còn 1 tiến trình của principal" in ra[0].chi_tiet
    ra = cach_ly(ch, [], goc=tmp_path, goc_wt=tmp_path / "wt", chay_td=ghi(da), xac_minh=lambda *a: 600,
                 chup=lambda: (_ for _ in ()).throw(OSError("sysctl")))
    assert [m.muc_do for m in ra] == ["do"] and "không đọc được bảng tiến trình" in ra[0].chi_tiet
```

- [ ] **Step 2: Chạy, thấy đỏ** — `PT tests/test_cham_tham_do.py` rồi `PT tests/test_kiem_am_p1.py tests/test_tham_do_principal.py tests/test_kiem_am.py`. Kết quả thật (mã của Task 5):

```
E   ModuleNotFoundError: No module named 'tram.tho.cham_tham_do'
1 error in 0.06s
---
E       TypeError: chay_tham_do() got an unexpected keyword argument 'kill'        (7 ca)
E       TypeError: cach_ly() got an unexpected keyword argument 'xac_minh'         (3 ca)
E       TypeError: kiem_cach_ly() got an unexpected keyword argument 'xac_minh'
11 failed, 1 passed in 0.11s
```

**Đối chứng cách chấm vòng trước (đột biến thật):** ở mã sau Task 6, thay `cham(...)` trong `chay_tham_do` bằng cách chấm của bản trước (`ma != 0` là bị chặn; HTTP không 2xx/422 là bị chặn; chép `out`) và chạy `PT tests/test_cham_tham_do.py` → `18 failed, 13 passed`: curl 7/28 + `000`, `000`, 404, 500, stdout chứa bí mật đều "đạt" (và chuỗi bí mật vào `chi_tiet`), 200/422 lộ đầu ra; `cat` thiếu file / thư mục, 127, 126, chết vì tín hiệu, `Read-only file system`, Keychain 44 không có thông điệp, Keychain 36, `nc` bị `Connection refused`, `tram` 127 đều thành "bị chặn".

- [ ] **Step 3: Mã**

Bản vá `tram/chu/kiem_cach_ly.py`:

```diff
--- a/tram/chu/kiem_cach_ly.py
+++ b/tram/chu/kiem_cach_ly.py
@@ -2,10 +2,15 @@
 từng principal khe và dưới `tram-kiem` (`sudo -u`, có thể hỏi mật khẩu). Biết `dai_ca_logins` thật nên thăm dò "API
 Duyệt với header danh tính giả" mang đúng login của Đại ca: chỉ bị chặn khi kênh ghi thật sự tách (`cach_ly.kenh_ghi`).
 Mã thoát 1 nếu có thăm dò không đạt; KHÔNG có fixture nào làm nó xanh. Lát 3c: `tram-kiem` đọc từ MỘT nguồn
-(`doc_principal_kiem` — `cach_ly.tram_kiem`) và thăm dò chạy qua ĐÚNG argv lúc kiểm lại (`PrincipalKiem.boc_lenh`)."""
+(`doc_principal_kiem` — `cach_ly.tram_kiem`) và thăm dò chạy qua ĐÚNG argv lúc kiểm lại (`PrincipalKiem.boc_lenh`).
+bs-863.14: principal khe qua `Principal.boc` (`sudo -n` — KHÔNG hỏi mật khẩu, không cần tty: thiếu dòng sudoers thì
+thăm dò dương hỏng → ĐỎ, không treo), mọi thăm dò qua P1 với `kill` của principal, UID thực chứng minh TRƯỚC."""
 import os
 import tempfile
 from pathlib import Path
+
+from tram.kiem.danh_tinh import LoiDanhTinh, xac_minh_uid
+from tram.kiem.vong_doi import LoiThuHoi
 
 from tram.cau_hinh.cach_ly import nap_cau_hinh_cach_ly
 from tram.cau_hinh.principal_kiem import doc_principal_kiem
@@ -13,46 +18,51 @@
 from tram.duong_dan import tram_home
 from tram.tho.kiem_am import chay_tham_do, tham_do_day_du, tham_do_khe
 from tram.tho.kiem_cong import KEYCHAIN_CAM
-from tram.tho.principal import ChuaCoPrincipal, doc_principal
-
-
-def _boc_sudo(user: str):
-    return lambda argv: ["/usr/bin/sudo", "-u", user, "-H", "--", *argv]
+from tram.tho.principal import ChuaCoPrincipal, Principal, doc_principal
 
 
 def _ds_boc(principal: list[str], doc_pk) -> list[tuple[str, object]]:
-    """(nhãn, boc | lỗi): principal khe qua `sudo -u` (hỏi mật khẩu); `tram-kiem` qua đúng argv của kiểm lại."""
+    """(nhãn, (tên, boc, kill) | lỗi): principal khe như user thường (không hồ sơ lượt — như trước) qua `sudo -n`;
+    `tram-kiem` qua đúng argv và kill của kiểm lại."""
     ds: list[tuple[str, object]] = []
     for chuoi in principal:
         try:
-            ds.append((chuoi, _boc_sudo(doc_principal(chuoi).user)))
+            p = Principal("user", doc_principal(chuoi).user)
+            ds.append((chuoi, (p.user, p.boc, p.kill_nhom)))
         except ChuaCoPrincipal as e:
             ds.append((chuoi, e))
     try:
         pk = doc_pk()
-        ds += [(f"{pk.co_che}:{pk.ten}", pk.boc_lenh)] if pk else []
+        ds += [(f"{pk.co_che}:{pk.ten}", (pk.ten, pk.boc_lenh, pk.kill_nhom))] if pk else []
     except ValueError as e:
         ds.append(("cach_ly.tram_kiem", e))
     return ds
 
 
-def kiem_cach_ly(principal: list[str], *, chay_td=chay_tham_do, doc_pk=doc_principal_kiem) -> tuple[str, int]:
+def kiem_cach_ly(principal: list[str], *, chay_td=chay_tham_do, doc_pk=doc_principal_kiem,
+                 xac_minh=xac_minh_uid) -> tuple[str, int]:
     ch, cl = nap_cau_hinh_tram(), nap_cau_hinh_cach_ly()
     ds = _ds_boc(principal, doc_pk)
     if not ds:
         return "Chưa có principal nào để kiểm (--principal / cach_ly.tram_kiem) — chờ S6.", 1
     dong, ma = [f"Kênh ghi dashboard: {cl.kenh_ghi}" + ("  (header GIẢ ĐƯỢC — chưa đạt §4 mục 2b)"
                                                        if cl.kenh_ghi == "header" else "")], 0
-    for chuoi, boc in ds:
-        if isinstance(boc, Exception):
-            dong.append(f"[ĐỎ] {chuoi}: {boc}")
+    for chuoi, pr in ds:
+        if not isinstance(pr, Exception):
+            try:
+                xac_minh(*pr)
+            except (LoiDanhTinh, LoiThuHoi) as e:
+                pr = ValueError(f"UID thực chưa chứng minh ({type(e).__name__}) — không chạy thăm dò")
+        if isinstance(pr, Exception):
+            dong.append(f"[ĐỎ] {chuoi}: {pr}")
             ma = 1
             continue
+        _, boc, kill = pr
         rg = tham_do_khe(keychain=list(KEYCHAIN_CAM), doc_cam=[tram_home() / "su-kien.db"], ghi_cam=[tram_home()],
                          ghi_duoc=Path(tempfile.gettempdir()))
         td = tham_do_day_du(rut_gon=rg, api="http://127.0.0.1:7700", dai_ca_login=(ch.dai_ca_logins or ("?",))[0],
                             may_b=ch.ten_may_b or "may-b", db=list(cl.db_nghiep_vu), tram_home_tram=tram_home())
-        for kq in chay_td(td, boc=boc, env={"PATH": os.environ.get("PATH", ""), "LANG": "C.UTF-8"}):
+        for kq in chay_td(td, boc=boc, env={"PATH": os.environ.get("PATH", ""), "LANG": "C.UTF-8"}, kill=kill):
             dong.append(f"[{'XANH' if kq.dat else 'ĐỎ'}] {chuoi} — {kq.ten}: {kq.chi_tiet}")
             ma |= 0 if kq.dat else 1
     return "\n".join(dong), ma
```

Tạo mới `tram/tho/cham_tham_do.py` (nguyên văn):

```python
"""Chấm MỘT thăm dò cách ly (V2-6b; review vòng 1 A04) — mỗi loại một bằng chứng riêng; kết luận chỉ là LÝ DO CỐ ĐỊNH,
không bao giờ chép stdout/stderr (có thể chứa token đọc được, email…). "Đạt" (bị chặn) CHỈ khi có dấu hiệu TỪ CHỐI QUYỀN
của chính đích; lỗi hạ tầng (không khởi chạy, thiếu công cụ 126/127, chết vì tín hiệu, mục tiêu không có, API không trả
lời/404/500, mã chưa phân loại) → "không kết luận", KHÔNG BAO GIỜ "bị chặn".
| loại | đạt (bị chặn) | không đạt | còn lại → không kết luận |
| doc, ghi, sua, nc, tram | mã ≠ 0, stderr "Permission denied"/"Operation not permitted" | mã 0 | |
| keychain | mã 44, stderr "could not be found" (keychain của principal không thấy mục) | mã 0 | mã khác — đo G4 |
| http | curl mã 0, HTTP 401/403 | HTTP 2xx/422 (đã qua kiểm quyền) | curl ≠ 0, 000, 404, 500… |
| ok (dương) | mã 0 | mã ≠ 0 | |
Đối chứng mục tiêu (`ThamDo.doi_chung`, chạy dưới tài khoản QUẢN LÝ trước thăm dò): đích phải tồn tại — file/thư mục
có thật, mục Keychain có trong keychain của quản lý (KHÔNG lấy mật khẩu: không `-w`), cổng DB mở được."""
import re
import socket
from collections.abc import Callable

from tram.keychain import LoiKeychain, co_muc

TU_CHOI = re.compile(r"Permission denied|Operation not permitted")
KHONG_THAY_MUC = re.compile(r"could not be found")
MA_HTTP = re.compile(r"[1-5]\d\d")


def cham(kieu: str, ma: int | None, out: str, err: str) -> tuple[str, str]:
    """(kết luận `dat` | `khong-dat` | `khong-ket-luan`, lý do cố định)."""
    if ma is None or ma < 0:
        return "khong-ket-luan", "không khởi chạy được hoặc bị tín hiệu dừng"
    if ma in (126, 127):
        return "khong-ket-luan", f"thiếu công cụ hoặc không thực thi được (mã {ma})"
    if kieu == "ok":
        return ("dat", "mã 0") if ma == 0 else ("khong-dat", f"thăm dò dương hỏng (mã {ma})")
    if kieu == "http":
        if ma != 0 or not MA_HTTP.fullmatch(out):
            return "khong-ket-luan", f"không gọi được API (curl mã {ma})"
        if out in ("401", "403"):
            return "dat", f"API từ chối (HTTP {out})"
        if out.startswith("2") or out == "422":
            return "khong-dat", f"API nhận yêu cầu (HTTP {out})"
        return "khong-ket-luan", f"API trả HTTP {out} — không chứng minh từ chối quyền"
    if ma == 0:
        return "khong-dat", "lệnh chạy được — không bị chặn"
    if kieu == "keychain":
        if ma == 44 and KHONG_THAY_MUC.search(err):
            return "dat", "keychain của principal không thấy mục (mã 44)"
        return "khong-ket-luan", f"mã {ma} chưa phân loại — đo ở G4"
    if kieu in ("doc", "ghi", "sua", "nc", "tram") and TU_CHOI.search(err):
        return "dat", f"bị từ chối quyền (mã {ma})"
    return "khong-ket-luan", f"mã {ma} không phải từ chối quyền"


def co_muc_keychain(k: str, *, chay: Callable | None = None) -> bool:
    """Đối chứng: mục `k` có trong keychain của QUẢN LÝ — qua `keychain.co_muc` (V3-1: không `-w`, có hạn, chỉ 0/44 là
    biết); không kiểm được → False ("không kết luận" ở người gọi)."""
    try:
        return co_muc(k, chay=chay)
    except LoiKeychain:
        return False


def mo_cong(dich: str, *, noi: Callable = socket.create_connection) -> bool:
    """Đối chứng: cổng `host:port` mở được từ tài khoản quản lý/trạm (hạn 3 s); lỗi → False."""
    host, _, cong = dich.rpartition(":")
    try:
        noi((host, int(cong)), timeout=3).close()
        return True
    except (OSError, ValueError):
        return False
```

Bản vá `tram/tho/kiem_am.py`:

```diff
--- a/tram/tho/kiem_am.py
+++ b/tram/tho/kiem_am.py
@@ -1,12 +1,20 @@
 """Kiểm chứng âm H9 (spec 3 §7.3 mục 7, §9.3): chạy từng thăm dò DƯỚI principal (`boc`) và đòi nó BỊ CHẶN; hai thăm
 dò dương (lệnh hợp lệ chạy được, ghi được thư mục của chính nó) để "chặn hết" không do principal hỏng. Chạy thật cần
 cổng S6 (user/sandbox đã tạo); test chỉ chạy với `boc` giả. Thăm dò ghi cố định trong mã — không nhận lệnh từ ngoài.
-`kieu`: `loi` — bị chặn khi mã thoát ≠ 0; `http` — bị chặn khi mã HTTP không phải 2xx/422 (422 = đã qua kiểm quyền);
-`ok` — thăm dò dương, phải thành công."""
+Review vòng 1 A04: mỗi `kieu` một bằng chứng riêng + đối chứng mục tiêu dưới quản lý (`cham_tham_do`); kết quả chỉ mang
+lý do cố định, không chép đầu ra. Đọc thư mục bằng `ls` (cat thư mục luôn lỗi — không phải bằng chứng bị chặn).
+bs-863.14: mọi thăm dò qua primitive P1 (`chay_gioi_han`: hạn tuyệt đối, thu hồi cả cây bằng `kill` CỦA PRINCIPAL —
+không `wait()` trần). Dương chạy TRƯỚC; một dương hỏng → mọi âm "không kết luận" (không chạy). Lỗi hạ tầng (quá hạn,
+không khởi chạy) không bao giờ thành "bị chặn"; chưa thu hồi được (`LoiThuHoi`) → dừng, phần còn lại không chạy."""
 import subprocess
 from collections.abc import Callable
-from dataclasses import dataclass
+from dataclasses import dataclass, field
+from functools import partial
 from pathlib import Path
+
+from tram.kiem.chay_gioi_han import chay_gioi_han
+from tram.kiem.vong_doi import Kill, LoiThuHoi
+from tram.tho.cham_tham_do import cham, co_muc_keychain, mo_cong
 
 HOOK = ("set -e; d=$(mktemp -d); cd \"$d\"; git init -q; mkdir -p .git/hooks; "
         "printf '#!/bin/sh\\ntouch \"$0.da-chay\"\\n' > .git/hooks/pre-commit; chmod +x .git/hooks/pre-commit; "
@@ -18,7 +26,8 @@
 class ThamDo:
     ten: str
     argv: list[str]
-    kieu: str = "loi"
+    kieu: str                                   # doc | ghi | sua | keychain | http | nc | tram | ok (cham_tham_do)
+    doi_chung: Callable[[], bool] | None = field(default=None, compare=False)      # dưới quản lý: đích CÓ thật
 
 
 @dataclass(frozen=True)
@@ -28,48 +37,67 @@
     chi_tiet: str
 
 
+def _doc(p: Path) -> ThamDo:
+    argv = ["/bin/ls", str(p)] if p.is_dir() else ["/bin/cat", str(p)]
+    return ThamDo(f"đọc {p}", argv, "doc", partial(p.exists))
+
+
 def tham_do_khe(*, keychain: list[str], doc_cam: list[Path], ghi_cam: list[Path], ghi_duoc: Path,
-                ghi_tep_cam: list[Path] = ()) -> list[ThamDo]:
+                ghi_tep_cam: list[Path] = (), co_muc: Callable[[str], bool] = co_muc_keychain) -> list[ThamDo]:
     """Bản rút gọn cho `tram tho kiem`: Keychain, file/thư mục của tiến trình quản lý và khe khác, file cấu hình của
     kho (`ghi_tep_cam` — `touch -c` không tạo file mới), + hai dương."""
-    ds = [ThamDo(f"đọc Keychain {k}", ["/usr/bin/security", "find-generic-password", "-s", k, "-w"]) for k in keychain]
-    ds += [ThamDo(f"đọc {p}", ["/bin/cat", str(p)]) for p in doc_cam]
-    ds += [ThamDo(f"ghi vào {p}", ["/usr/bin/touch", str(p / ".tram-kiem-am")]) for p in ghi_cam]
-    ds += [ThamDo(f"sửa {p}", ["/usr/bin/touch", "-c", str(p)]) for p in ghi_tep_cam]
+    ds = [ThamDo(f"đọc Keychain {k}", ["/usr/bin/security", "find-generic-password", "-s", k, "-w"], "keychain",
+                 partial(co_muc, k)) for k in keychain]
+    ds += [_doc(p) for p in doc_cam]
+    ds += [ThamDo(f"ghi vào {p}", ["/usr/bin/touch", str(p / ".tram-kiem-am")], "ghi", partial(p.is_dir))
+           for p in ghi_cam]
+    ds += [ThamDo(f"sửa {p}", ["/usr/bin/touch", "-c", str(p)], "sua", partial(p.is_file)) for p in ghi_tep_cam]
     return ds + [ThamDo("lệnh hợp lệ chạy được", ["/usr/bin/true"], "ok"),
                  ThamDo(f"ghi được {ghi_duoc}", ["/usr/bin/touch", str(ghi_duoc / ".tram-kiem-duong")], "ok")]
 
 
 def tham_do_day_du(*, rut_gon: list[ThamDo], api: str, dai_ca_login: str, may_b: str, db: list[str],
-                   tram_home_tram: Path | None) -> list[ThamDo]:
+                   tram_home_tram: Path | None, mo: Callable[[str], bool] = mo_cong) -> list[ThamDo]:
     """Bộ đủ §7.3 mục 7: + gọi API Duyệt với header danh tính giả, kết nối DB nghiệp vụ, `tram` khi xoá
     `TRAM_GIAO_ID` trỏ vào kho của trạm, git hook trong repo."""
     ds = list(rut_gon) + [ThamDo("API Duyệt với header danh tính giả", [
         "/usr/bin/curl", "-s", "-m", "10", "-o", "/dev/null", "-w", "%{http_code}", "-X", "POST",
         "-H", "Content-Type: application/json", "-H", f"Tailscale-User-Login: {dai_ca_login}", "-H", "X-Tram: 1",
         "-H", f"Origin: https://{may_b}", "--data", "{}", f"{api}/api/phe-duyet/kiem-am/kiem-am/duyet"], "http")]
-    ds += [ThamDo(f"kết nối DB nghiệp vụ {d}", ["/usr/bin/nc", "-z", "-G", "3", *d.rsplit(":", 1)]) for d in db]
+    ds += [ThamDo(f"kết nối DB nghiệp vụ {d}", ["/usr/bin/nc", "-z", "-G", "3", *d.rsplit(":", 1)], "nc",
+                  partial(mo, d)) for d in db]
     if tram_home_tram is not None:
         ds.append(ThamDo("tram khi xoá TRAM_GIAO_ID, trỏ kho trạm", [
-            "/usr/bin/env", "-u", "TRAM_GIAO_ID", f"TRAM_HOME={tram_home_tram}", "tram", "chu", "trang-thai"]))
+            "/usr/bin/env", "-u", "TRAM_GIAO_ID", f"TRAM_HOME={tram_home_tram}", "tram", "chu", "trang-thai"], "tram",
+            partial(tram_home_tram.exists)))
     return ds + [ThamDo("git hook trong repo không chạy", ["/bin/sh", "-c", HOOK], "ok")]
 
 
-def chay_tham_do(ds: list[ThamDo], *, boc: Callable[[list[str]], list[str]], env: dict[str, str],
-                 timeout: float = 30) -> list[KetQuaThamDo]:
-    ra = []
-    for t in ds:
+def _doi_chung(t: ThamDo) -> bool:
+    try:
+        return t.doi_chung is None or t.doi_chung() is True
+    except Exception:                                   # noqa: BLE001 — đối chứng hỏng = không chứng minh được đích
+        return False
+
+
+def chay_tham_do(ds: list[ThamDo], *, boc: Callable[[list[str]], list[str]], env: dict[str, str], kill: Kill,
+                 timeout: float = 30, chay: Callable = chay_gioi_han) -> list[KetQuaThamDo]:
+    ra: dict[int, KetQuaThamDo] = {}
+    dung = None
+    for i in sorted(range(len(ds)), key=lambda i: ds[i].kieu != "ok"):          # dương trước, giữ thứ tự trong nhóm
+        t = ds[i]
+        if dung is None and t.kieu != "ok" and not all(ra[j].dat for j in ra if ds[j].kieu == "ok"):
+            dung = "không kết luận: thăm dò dương hỏng — principal/sandbox không chạy được lệnh hợp lệ"
+        if dung is not None or not _doi_chung(t):
+            ra[i] = KetQuaThamDo(t.ten, False, dung or "không kết luận: đối chứng hỏng — đích không có/không kiểm được")
+            continue
         try:
-            kq = subprocess.run(boc(t.argv), capture_output=True, text=True, timeout=timeout, env=env,
-                                stdin=subprocess.DEVNULL)
-            ma, out = kq.returncode, kq.stdout.strip()
-        except (OSError, subprocess.TimeoutExpired) as e:
-            ma, out = None, type(e).__name__
-        if t.kieu == "ok":
-            dat = ma == 0
-        elif t.kieu == "http":
-            dat = not (out.startswith("2") or out == "422")
-        else:
-            dat = ma != 0
-        ra.append(KetQuaThamDo(t.ten, dat, f"mã {ma}" + (f", HTTP {out}" if t.kieu == "http" else "")))
-    return ra
+            kq = chay(boc(t.argv), kill=kill, capture_output=True, text=True, timeout=timeout, env=env)
+            kl, ly = cham(t.kieu, kq.returncode, (kq.stdout or "").strip(), kq.stderr or "")
+        except LoiThuHoi:
+            kl, ly = "khong-ket-luan", "không xác nhận thu hồi tiến trình thăm dò"
+            dung = "không chạy: thăm dò trước chưa thu hồi được — kiểm principal"
+        except (OSError, subprocess.SubprocessError, ValueError) as e:
+            kl, ly = "khong-ket-luan", f"lỗi hạ tầng ({type(e).__name__})"
+        ra[i] = KetQuaThamDo(t.ten, kl == "dat", ly if kl != "khong-ket-luan" else f"không kết luận: {ly}")
+    return [ra[i] for i in range(len(ds))]
```

Bản vá `tram/tho/kiem_cong.py`:

```diff
--- a/tram/tho/kiem_cong.py
+++ b/tram/tho/kiem_cong.py
@@ -1,13 +1,20 @@
 """Các mục chờ cổng của `tram tho kiem` (spec 3 §9.3, H7) — chạy THẬT dưới principal của khe, không đánh dấu xanh bằng
 fixture: đăng nhập CLI qua lệnh trạng thái (không đọc file đăng nhập — lệnh chính xác CHỜ S2), và kiểm chứng âm rút
 gọn §7.3 mục 7 (Keychain/token máy, thư mục tiến trình quản lý, hàng đợi + cấu hình khe khác, `.git/config` và
-`.git/hooks` của kho) + hai thăm dò dương. Principal chưa khai/sai → đỏ."""
-import os
+`.git/hooks` của kho) + hai thăm dò dương. Principal chưa khai/sai → đỏ. bs-863.14: UID thực của principal chứng minh
+TRƯỚC (`xac_minh_uid`); thăm dò qua P1 với `kill` của principal, env dựng mới chỉ PATH/LANG (không HOME của quản lý).
+Review vòng 1 A02: thăm dò xong mà bảng tiến trình của nhân còn tiến trình của UID principal → ĐỎ (CHỈ QUAN SÁT, không
+giết: có thể `tram tho chay` đang chạy phiếu — sổ tay: dừng nó trước khi kiểm)."""
 import subprocess
 from pathlib import Path
 
+from tram.kiem import danh_tinh
+from tram.kiem.bang_tien_trinh import chup_nhan
+from tram.kiem.vong_doi import LoiThuHoi
+
 from tram.tho.cau_hinh import CauHinhTho, KheCauHinh
-from tram.tho.kiem_am import chay_tham_do, tham_do_khe
+from tram.tho.don_uid import con_lai
+from tram.tho.kiem_am import KetQuaThamDo, chay_tham_do, tham_do_khe
 from tram.tho.kiem_may import DauDo, MucKiem
 from tram.tho.principal import ChuaCoPrincipal
 from tram.tho.principal_khe import principal_cua
@@ -29,7 +36,27 @@
     return ("xanh", "đã đăng nhập (lệnh chờ S2 xác nhận)") if kq.returncode == 0 else ("do", "chưa đăng nhập / lỗi")
 
 
-def cach_ly(ch: CauHinhTho, du_an: list[str], *, goc: Path, goc_wt: Path, chay_td=chay_tham_do) -> list[MucKiem]:
+def _uid(p, xac_minh) -> tuple[int | None, str | None]:
+    """(UID thực đã chứng minh, None) hoặc (None, lý do) — lỗi thì không chạy gì thêm dưới principal này."""
+    try:
+        return xac_minh(p.user, p.boc, p.kill_nhom), None
+    except danh_tinh.LoiDanhTinh:
+        return None, "UID thực của principal chưa chứng minh — không chạy thăm dò"
+    except LoiThuHoi:
+        return None, "UID: không xác nhận thu hồi tiến trình dò — kiểm principal"
+
+
+def _tan_du(uid: int, chup) -> list[KetQuaThamDo]:
+    try:
+        n = con_lai(uid, chup)
+    except (OSError, ValueError):
+        return [KetQuaThamDo("tàn dư", False, "không kết luận: không đọc được bảng tiến trình sau thăm dò")]
+    return [KetQuaThamDo("tàn dư", False, f"còn {n} tiến trình của principal sau thăm dò — chưa chứng minh thu hồi "
+                                          "(dừng `tram tho chay` rồi kiểm lại)")] if n else []
+
+
+def cach_ly(ch: CauHinhTho, du_an: list[str], *, goc: Path, goc_wt: Path, chay_td=chay_tham_do,
+            xac_minh=danh_tinh.xac_minh_uid, chup=chup_nhan) -> list[MucKiem]:
     ra = []
     for k in ch.khe:
         kid = ch.khe_id(k)
@@ -37,6 +64,10 @@
             p = principal_cua(ch, k, goc=goc, goc_wt=goc_wt, wt=None, ten="kiem")
         except ChuaCoPrincipal as e:
             ra.append(MucKiem(f"{kid} cách ly", "do", str(e)))
+            continue
+        uid, ly_do = _uid(p, xac_minh)
+        if ly_do is not None:
+            ra.append(MucKiem(f"{kid} cách ly", "do", ly_do))
             continue
         khac = [x for x in ch.khe if x.ten != k.ten]
         kho = [goc_wt.parent / "kho" / d / ".git" for d in du_an]
@@ -46,8 +77,8 @@
                          ghi_cam=[*(goc / "hang-doi" / ch.may_id / x.ten for x in khac),
                                   *(x.thu_muc_cau_hinh for x in khac), *(g / "hooks" for g in kho)],
                          ghi_duoc=goc / "hang-doi" / ch.may_id / k.ten, ghi_tep_cam=[g / "config" for g in kho])
-        kq = chay_td(ds, boc=p.boc, env={"PATH": ch.chay.path_cli, "LANG": "C.UTF-8", "HOME": os.environ.get("HOME", "")})
-        hong = [x for x in kq if not x.dat]
+        kq = chay_td(ds, boc=p.boc, env={"PATH": ch.chay.path_cli, "LANG": "C.UTF-8"}, kill=p.kill_nhom)
+        hong = [x for x in kq if not x.dat] + _tan_du(uid, chup)
         ra.append(MucKiem(f"{kid} cách ly", "do" if hong else "xanh",
                           "; ".join(f"{x.ten}: {x.chi_tiet}" for x in hong) or f"{len(kq)} thăm dò đạt"))
     return ra
```

- [ ] **Step 4: Chạy, thấy xanh** — `PT tests/test_cham_tham_do.py tests/test_kiem_am_p1.py tests/test_tham_do_principal.py tests/test_kiem_am.py tests/test_kiem_cong.py tests/test_chu_tho.py` → `52 passed`.

- [ ] **Step 5: Cả bộ** — `PT` → `2930` (thu thập), nhật ký chặn 0 dòng mới.

- [ ] **Step 6: Commit** — `fix(tho): thăm dò cách ly qua P1, UID trước, mỗi loại một bằng chứng, tàn dư là đỏ (V2-6b, bs-863.14, A04)`

## Task 7 — Dò đăng nhập dưới principal của khe; thu hồi lỗi thì thôi mọi thăm dò dưới principal đó (V2-6b, bs-863.17; review vòng 1 A05)

**Files:** sửa `tram/tho/do_may.py`, `tram/tho/kiem_3b.py`, `tram/tho/kiem_cong.py` (`dang_nhap`); test mới `tests/test_dang_nhap_principal.py`; sửa `tests/test_do_may.py`, `tests/test_kiem_3b.py`, `tests/test_kiem_cong.py`, `tests/test_han_muc_principal.py`.

**Interfaces:**
- `do_cli(cli, thu_muc, *, which, chay)` chỉ đọc `--version`, `dang_nhap` luôn None (bỏ `LENH_DANG_NHAP`).
- `dang_nhap_codex(pr, codex, thu_muc, *, path, chay=chay_gioi_han) -> (True | False | None, chi_tiết)` — `pr` đã xác minh UID; lỗi hạ tầng → None "không kết luận"; **`LoiThuHoi` NỔI LÊN** (A05).
- `bo_sung_3b(..., principal_cua_=_principal, dang_nhap_=dang_nhap_codex)` — `principal_cua_` MỘT lần cho đăng nhập + quota; `LoiThuHoi` ở xác minh HAY ở đăng nhập → đăng nhập ĐỎ, hạn mức ĐỎ, KHÔNG gọi `doc_han_muc`.
- `kiem_cong.dang_nhap(..., chay=chay_gioi_han, xac_minh=xac_minh_uid)` (Claude).
- **Đổi kỳ vọng test cũ (có chủ đích):** `test_kiem_may_goi_bo_sung_3b` — khe chưa có principal nay đăng nhập ĐỎ; `test_do_may` — không còn chạy `login status`; `test_kiem_3b`/`test_han_muc_principal` truyền `principal_cua_`/`dang_nhap_` giả.

- [ ] **Step 1: Viết test**

Tạo mới `tests/test_dang_nhap_principal.py` (nguyên văn):

```python
"""bs-863.17: trạng thái đăng nhập CLI dò DƯỚI principal của khe — argv qua `boc`, `kill` của principal, env dựng mới
chỉ PATH/LANG/<thư mục cấu hình> (không HOME/token của quản lý); chưa có principal hay UID chưa chứng minh → không spawn
lệnh đăng nhập nào. Lỗi hạ tầng không thành "đã đăng nhập". Không sudo/CLI thật: chạy và xác minh UID đều GIẢ."""
import subprocess
from datetime import datetime, timezone

import pytest

from test_kiem_3b import _ch, _dd, _hm
from test_kiem_cong import cau_hinh
from tram.kiem.danh_tinh import LoiDanhTinh
from tram.kiem.vong_doi import LoiThuHoi
from tram.tho.do_may import dang_nhap_codex, do_cli
from tram.tho.kiem_3b import bo_sung_3b
from tram.tho.kiem_cong import dang_nhap
from tram.tho.principal import Principal

LUC = datetime(2026, 10, 13, 3, 0, tzinfo=timezone.utc)
PR = Principal("user", "tram-k-c-codex-1")


def chay_gia(goi, ket=0):
    def chay(argv, **kw):
        goi.append((argv, kw))
        if isinstance(ket, BaseException):
            raise ket
        return subprocess.CompletedProcess(argv, ket, "Logged in as ai@x\n", "")
    return chay


def test_do_cli_chi_doc_phien_ban_khong_do_dang_nhap_duoi_quan_ly(tmp_path):
    goi = []
    kq = do_cli("codex", tmp_path, which=lambda c: "/opt/bin/codex", chay=chay_gia(goi))
    assert [a for a, _ in goi] == [["/opt/bin/codex", "--version"]] and kq.dang_nhap is None
    assert "principal" in kq.chi_tiet


def test_dang_nhap_codex_duoi_principal_env_moi_kill_cua_principal(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", "/Users/quan-ly")
    monkeypatch.setenv("TRAM_THO_TOKEN", "BI-MAT")
    goi = []
    assert dang_nhap_codex(PR, "/opt/bin/codex", tmp_path / "k1", path="/x/bin", chay=chay_gia(goi))[0] is True
    argv, kw = goi[0]
    assert argv == PR.boc(["/opt/bin/codex", "login", "status"]) and kw["kill"] == PR.kill_nhom
    assert kw["env"] == {"PATH": "/x/bin", "LANG": "C.UTF-8", "CODEX_HOME": str(tmp_path / "k1")}
    assert kw["timeout"] == 20
    co, ct = dang_nhap_codex(PR, "codex", tmp_path, path="/x", chay=chay_gia([], 1))
    assert co is False and "ai@x" not in ct


def test_dang_nhap_codex_loi_ha_tang_khong_ket_luan_thu_hoi_loi_thi_noi_len(tmp_path):
    for loi in (subprocess.TimeoutExpired("x", 20), OSError("spawn")):
        co, ct = dang_nhap_codex(PR, "codex", tmp_path, path="/x", chay=chay_gia([], loi))
        assert co is None and "không kết luận" in ct
    with pytest.raises(LoiThuHoi):                      # A05: người gọi phải biết để thôi mọi thăm dò dưới principal
        dang_nhap_codex(PR, "codex", tmp_path, path="/x", chay=chay_gia([], LoiThuHoi("x")))


def test_tho_kiem_dang_nhap_thu_hoi_loi_thi_khong_do_han_muc(tmp_path):
    hm = []

    def dn(*a, **kw):
        raise LoiThuHoi("không xác nhận thu hồi `codex login status`")
    ds = bo_sung_3b(_ch(tmp_path), _dd(tmp_path), [], doc_han_muc=lambda *a, **k: hm.append(1), bay_gio=LUC,
                    principal_cua_=lambda ch, k: PR, dang_nhap_=dn)
    m = {x.muc: x for x in ds}
    assert hm == [] and m["C/codex-1 hạn mức"].muc_do == "do" and m["C/codex-1 đăng nhập"].muc_do == "do"
    assert "thu hồi" in m["C/codex-1 đăng nhập"].chi_tiet


def test_tho_kiem_khong_principal_thi_khong_spawn_dang_nhap(tmp_path):
    goi, hm = [], []
    ds = bo_sung_3b(_ch(tmp_path), _dd(tmp_path), [], doc_han_muc=lambda *a, **k: hm.append(k["principal"]),
                    bay_gio=LUC, principal_cua_=lambda ch, k: None,
                    dang_nhap_=lambda *a, **k: goi.append(a) or (True, "x"))
    m = {x.muc: x for x in ds}
    assert goi == [] and hm == [None] and m["C/codex-1 đăng nhập"].muc_do == "do"
    assert "principal" in m["C/codex-1 đăng nhập"].chi_tiet


def test_tho_kiem_mot_lan_xac_minh_uid_cho_ca_dang_nhap_va_han_muc(tmp_path):
    goi, xm = [], []

    def dn(pr, codex, thu_muc, *, path):
        goi.append((pr, codex, thu_muc, path))
        return True, "ok"
    ds = bo_sung_3b(_ch(tmp_path), _dd(tmp_path), [], doc_han_muc=_hm, bay_gio=LUC,
                    principal_cua_=lambda ch, k: xm.append(k.ten) or PR, dang_nhap_=dn)
    assert xm == ["codex-1"] and goi == [(PR, "/opt/bin/codex", tmp_path / "codex-1", _ch(tmp_path).chay.path_cli)]
    assert {x.muc: x.muc_do for x in ds}["C/codex-1 đăng nhập"] == "xanh"


def test_tho_kiem_thu_hoi_loi_khi_xac_minh_uid_thi_do(tmp_path):
    def loi(ch, k):
        raise LoiThuHoi("x")
    ds = bo_sung_3b(_ch(tmp_path), _dd(tmp_path), [], doc_han_muc=_hm, bay_gio=LUC, principal_cua_=loi,
                    dang_nhap_=lambda *a, **k: 1 / 0)
    assert {x.muc: x.muc_do for x in ds}["C/codex-1 hạn mức"] == "do"


def test_claude_auth_status_uid_truoc_qua_p1(tmp_path):
    ch, goi = cau_hinh(tmp_path), []
    assert dang_nhap(ch, ch.khe[0], goc=tmp_path, goc_wt=tmp_path, chay=chay_gia(goi),
                     xac_minh=lambda *a: (_ for _ in ()).throw(LoiDanhTinh("x")))[0] == "do" and goi == []
    assert dang_nhap(ch, ch.khe[0], goc=tmp_path, goc_wt=tmp_path, chay=chay_gia(goi), xac_minh=lambda *a: 600)[0] \
        == "xanh"
    assert goi[0][1]["kill"].__self__.user == "tram-k-1" and goi[0][1]["timeout"] == 30
    assert dang_nhap(ch, ch.khe[0], goc=tmp_path, goc_wt=tmp_path, chay=chay_gia([], LoiThuHoi("x")),
                     xac_minh=lambda *a: 600)[0] == "do"
```

Bản vá `tests/test_do_may.py`:

```diff
--- a/tests/test_do_may.py
+++ b/tests/test_do_may.py
@@ -12,22 +12,18 @@
     return chay
 
 
-def test_codex_dang_nhap_qua_lenh_trang_thai_voi_codex_home_cua_khe(tmp_path):
+def test_codex_chi_doc_phien_ban_dang_nhap_do_duoi_principal(tmp_path):
     goi = []
-    chay = _chay({("--version",): (0, "codex-cli 0.170.0\n"), ("login", "status"): (0, "Logged in using ChatGPT\n")},
-                 goi)
+    chay = _chay({("--version",): (0, "codex-cli 0.170.0\n")}, goi)
     kq = do_cli("codex", tmp_path / "khe", which=lambda c: f"/opt/bin/{c}", chay=chay)
-    assert (kq.duong_dan, kq.phien_ban, kq.dang_nhap) == ("/opt/bin/codex", "codex-cli 0.170.0", True)
-    assert goi[1] == (["/opt/bin/codex", "login", "status"], str(tmp_path / "khe"))
-    assert "@" not in kq.chi_tiet and "ChatGPT" not in kq.chi_tiet          # không chép đầu ra (có thể có email)
-    chay = _chay({("--version",): (0, "x\n"), ("login", "status"): (1, "Not logged in\n")}, [])
-    assert do_cli("codex", tmp_path, which=lambda c: c, chay=chay).dang_nhap is False
+    assert (kq.duong_dan, kq.phien_ban, kq.dang_nhap) == ("/opt/bin/codex", "codex-cli 0.170.0", None)
+    assert goi == [(["/opt/bin/codex", "--version"], None)] and "principal" in kq.chi_tiet    # bs-863.17
 
 
 def test_claude_chua_kiem_dang_nhap_va_cli_thieu(tmp_path):
     goi = []
     kq = do_cli("claude", tmp_path, which=lambda c: "/b/claude", chay=_chay({("--version",): (0, "2.1.227\n")}, goi))
-    assert kq.dang_nhap is None and "S2" in kq.chi_tiet and len(goi) == 1
+    assert kq.dang_nhap is None and "principal" in kq.chi_tiet and len(goi) == 1
     kq = do_cli("codex", tmp_path, which=lambda c: None, chay=None)
     assert kq.duong_dan is None and kq.dang_nhap is None and "PATH" in kq.chi_tiet
 
```

Bản vá `tests/test_han_muc_principal.py`:

```diff
--- a/tests/test_han_muc_principal.py
+++ b/tests/test_han_muc_principal.py
@@ -72,7 +72,8 @@
             raise LoiThuHoi("x")
         return None
     ds = {m.muc: m.muc_do for m in bo_sung_3b(nc.ch, dd, [], doc_han_muc=doc, bay_gio=datetime.now(timezone.utc),
-                                              principal_cua_=lambda ch, x: None if x.principal is None else x.ten)}
+                                              principal_cua_=lambda ch, x: None if x.principal is None else x.ten,
+                                              dang_nhap_=lambda *a, **kw: (None, "không kết luận"))}
     assert goi == [("C/codex-1", "codex-1"), ("C/codex-2", "codex-2"), ("C/codex-3", None)]
     assert [ds[f"C/codex-{i} hạn mức"] for i in (1, 2, 3)] == ["vang", "do", "vang"]
 
```

Bản vá `tests/test_kiem_3b.py`:

```diff
--- a/tests/test_kiem_3b.py
+++ b/tests/test_kiem_3b.py
@@ -7,6 +7,7 @@
 from tram.tho.do_may import TAG_THO
 from tram.tho.kiem_3b import bo_sung_3b
 from tram.tho.kiem_may import DauDo, MucKiem, in_ket_qua, kiem_may
+from tram.tho.principal import Principal
 
 LUC = datetime(2026, 10, 13, 3, 0, tzinfo=timezone.utc)
 
@@ -40,7 +41,9 @@
 
 def test_khe_codex_thay_muc_dang_nhap_them_han_muc_va_tag(tmp_path):
     goc = [MucKiem("C/codex-1 đăng nhập", "do", "chờ S2"), MucKiem("C/claude-3 đăng nhập", "do", "chờ S2")]
-    ds = bo_sung_3b(_ch(tmp_path), _dd(tmp_path), goc, doc_han_muc=_hm, bay_gio=LUC)
+    ds = bo_sung_3b(_ch(tmp_path), _dd(tmp_path), goc, doc_han_muc=_hm, bay_gio=LUC,
+                    principal_cua_=lambda ch, k: Principal("user", "tram-k-c-codex-1"),
+                    dang_nhap_=lambda *a, **kw: (True, "đã đăng nhập"))
     m = _muc(ds)
     assert m["C/codex-1 đăng nhập"][0] == "xanh" and m["C/claude-3 đăng nhập"] == ("do", "chờ S2")
     assert [x.muc for x in ds].count("C/codex-1 đăng nhập") == 1
@@ -60,7 +63,7 @@
 
 def test_kiem_may_goi_bo_sung_3b(tmp_path):
     m = _muc(kiem_may(_ch(tmp_path), _dd(tmp_path, goc=str(tmp_path / "khong-co"))))
-    assert m["C/codex-1 đăng nhập"][0] == "xanh" and m["tailscale tag"][0] == "xanh"
+    assert m["C/codex-1 đăng nhập"][0] == "do" and m["tailscale tag"][0] == "xanh"     # khe chưa principal: không dò
     assert m["C/codex-1 hạn mức"][0] == "vang"                      # không có `codex` thật → không đọc được
 
 
```

Bản vá `tests/test_kiem_cong.py`:

```diff
--- a/tests/test_kiem_cong.py
+++ b/tests/test_kiem_cong.py
@@ -44,7 +44,7 @@
         goi.append((argv, kw["env"]))
         return SimpleNamespace(returncode=0)
     ch = cau_hinh(tmp_path)
-    assert dang_nhap(ch, ch.khe[0], goc=tmp_path, goc_wt=tmp_path, chay=chay)[0] == "xanh"
+    assert dang_nhap(ch, ch.khe[0], goc=tmp_path, goc_wt=tmp_path, chay=chay, xac_minh=lambda *a: 600)[0] == "xanh"
     argv, env = goi[0]
     assert argv[:5] == ["/usr/bin/sudo", "-n", "-H", "-u", "tram-k-1"] and argv[-3:] == ["claude", "auth", "status"]
     assert env["CLAUDE_CONFIG_DIR"] == str(tmp_path / "cfg1") and "TRAM_THO_TOKEN" not in env
```

- [ ] **Step 2: Chạy, thấy đỏ** — `PT tests/test_dang_nhap_principal.py`. Kết quả thật (mã của Task 6):

```
E   ImportError: cannot import name 'dang_nhap_codex' from 'tram.tho.do_may'
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
1 error in 0.11s
```

Đối chứng bản trước (có `dang_nhap_codex` nhưng đổi `LoiThuHoi` thành `(None, …)`), chạy cùng file test:

```
E       Failed: DID NOT RAISE <class 'tram.kiem.vong_doi.LoiThuHoi'>
E       tram.kiem.vong_doi.LoiThuHoi: không xác nhận thu hồi `codex login status`
FAILED …::test_dang_nhap_codex_loi_ha_tang_khong_ket_luan_thu_hoi_loi_thi_noi_len
FAILED …::test_tho_kiem_dang_nhap_thu_hoi_loi_thi_khong_do_han_muc
2 failed, 6 passed in 0.10s
```

- [ ] **Step 3: Mã**

Bản vá `tram/tho/do_may.py`:

```diff
--- a/tram/tho/do_may.py
+++ b/tram/tho/do_may.py
@@ -1,21 +1,23 @@
 """Dò máy thợ — CHỈ ĐỌC, không đổi gì (spec 3 §9.2, §9.3; kiến trúc §7 "Mac thợ").
 
-- CLI: đường dẫn + `--version`; đăng nhập qua LỆNH TRẠNG THÁI của CLI, dưới thư mục cấu hình của khe — không bao giờ mở
-  file đăng nhập. Codex: `codex login status` (mã 0 = đã đăng nhập — chờ spike S5 xác nhận). Claude: lệnh trạng thái
-  chốt ở spike S2 (3a-2) — ở đây báo "chưa kiểm". Không chép đầu ra lệnh trạng thái (có thể chứa email tài khoản).
+- CLI: đường dẫn + `--version` (không đụng credential). Đăng nhập CHỈ dò DƯỚI principal của khe (bs-863.17):
+  `dang_nhap_codex` — `codex login status` qua `boc`/`kill` của principal, env dựng mới PATH/LANG/CODEX_HOME (không
+  HOME/token của quản lý; mã 0 = đã đăng nhập — chờ spike S5). Claude: lệnh trạng thái chốt ở S2 (`kiem_cong`). Không
+  bao giờ mở file đăng nhập, không chép đầu ra lệnh trạng thái (có thể chứa email tài khoản).
 - Tailscale: Mac thợ phải là thiết bị GẮN TAG (#3) — đọc `tailscale status --json` → `Self.Tags`. Trạm không tự gắn tag,
   không chạy `tailscale up`; chưa gắn thì Đại ca làm trong trang quản trị Tailscale."""
 import json
-import os
 import shutil
 import subprocess
+from collections.abc import Callable
 from dataclasses import dataclass
 from pathlib import Path
+
+from tram.kiem.chay_gioi_han import chay_gioi_han
 
 TAG_THO = "tag:tram-tho"
 DUONG_TAILSCALE_APP = "/Applications/Tailscale.app/Contents/MacOS/Tailscale"
 BIEN_THU_MUC = {"claude": "CLAUDE_CONFIG_DIR", "codex": "CODEX_HOME"}
-LENH_DANG_NHAP = {"codex": ["login", "status"]}          # claude: chờ S2 (3a-2)
 
 
 @dataclass(frozen=True)
@@ -33,15 +35,24 @@
         return KetQuaDo(cli, None, "", None, f"không thấy `{cli}` trong PATH")
     v = chay([duong, "--version"], capture_output=True, text=True, timeout=20)
     phien = ((v.stdout or v.stderr or "").strip().splitlines() or [""])[0][:80]
-    if cli not in LENH_DANG_NHAP:
-        return KetQuaDo(cli, duong, phien, None, "đăng nhập chưa kiểm được — chờ spike S2 (không đọc file đăng nhập)")
-    env = {**os.environ, BIEN_THU_MUC[cli]: str(thu_muc)}
-    s = chay([duong, *LENH_DANG_NHAP[cli]], capture_output=True, text=True, timeout=20, env=env)
-    lenh = " ".join([cli, *LENH_DANG_NHAP[cli]])
+    return KetQuaDo(cli, duong, phien, None, "đăng nhập chỉ dò dưới principal của khe (`tram tho kiem`) — không dò "
+                    f"dưới tài khoản quản lý; thư mục đăng nhập của khe: {BIEN_THU_MUC[cli]}={thu_muc}")
+
+
+def dang_nhap_codex(pr, codex: str, thu_muc: Path, *, path: str, chay: Callable = chay_gioi_han
+                    ) -> tuple[bool | None, str]:
+    """(True | False | None = không kết luận, chi tiết) — `pr` là principal ĐÃ xác minh UID (người gọi). `LoiThuHoi`
+    NỔI LÊN (review vòng 1 A05): người gọi phải thôi mọi thăm dò khác dưới principal này."""
+    env = {"PATH": path, "LANG": "C.UTF-8", "CODEX_HOME": str(thu_muc)}
+    try:
+        s = chay(pr.boc([codex, "login", "status"]), kill=pr.kill_nhom, capture_output=True, text=True, timeout=20,
+                 env=env)
+    except (OSError, subprocess.SubprocessError, ValueError) as e:
+        return None, f"không kết luận: không chạy được `codex login status` dưới principal ({type(e).__name__})"
     if s.returncode == 0:
-        return KetQuaDo(cli, duong, phien, True, f"đã đăng nhập (`{lenh}` mã 0)")
-    return KetQuaDo(cli, duong, phien, False, f"chưa đăng nhập (`{lenh}` mã {s.returncode}) — Đại ca đăng nhập tay: "
-                    f"{BIEN_THU_MUC[cli]}={thu_muc} {cli} login")
+        return True, "đã đăng nhập (`codex login status` mã 0, dưới principal của khe)"
+    return False, (f"chưa đăng nhập (`codex login status` mã {s.returncode}) — Đại ca đăng nhập tay dưới principal "
+                   f"của khe với CODEX_HOME={thu_muc}")
 
 
 def kiem_tag(*, which=shutil.which, chay=subprocess.run, tag: str = TAG_THO) -> tuple[bool, str]:
```

Bản vá `tram/tho/kiem_3b.py`:

```diff
--- a/tram/tho/kiem_3b.py
+++ b/tram/tho/kiem_3b.py
@@ -1,9 +1,9 @@
 """Mục `tram tho kiem` của lát 3b (spec 3 §9.2, §9.3, H7) — nối vào cuối `kiem_may` (3a-1):
 
-- Khe Codex: đăng nhập qua `codex login status` với `CODEX_HOME` của khe (thay mục "chờ S2" chung); hạn mức đọc một lần
-  qua `codex app-server` DƯỚI PRINCIPAL CỦA KHE (bs-78r.10), sau khi xác minh UID thực của principal — chưa có
-  principal, UID chưa chứng minh hay không đọc được thì VÀNG (#15: vẫn nhận việc, cảnh báo), không đỏ; không xác nhận
-  thu hồi tiến trình (dò UID hay app-server) → ĐỎ.
+- Khe Codex: xác minh UID thực của principal MỘT lần, rồi cả đăng nhập (`codex login status`, bs-863.17) lẫn hạn mức
+  (`codex app-server`, bs-78r.10) đều chạy DƯỚI PRINCIPAL ĐÓ. Chưa có principal / UID chưa chứng minh → đăng nhập ĐỎ
+  (không dò dưới quản lý, không spawn), hạn mức VÀNG (#15); không xác nhận thu hồi tiến trình (dò UID, đăng nhập hay
+  app-server) → ĐỎ và KHÔNG spawn gì thêm dưới principal đó (review vòng 1 A05).
 - Máy từ xa (`tram_api` là https): Mac thợ phải gắn tag Tailscale (#3) — chỉ kiểm, không đổi.
 Mục cách ly, quyền ghi worktree của principal giữ nguyên như 3a-1/3a-2 (S6)."""
 from datetime import datetime, timezone
@@ -14,7 +14,7 @@
 from tram.kiem import danh_tinh
 from tram.kiem.vong_doi import LoiThuHoi
 from tram.tho.cau_hinh import CauHinhTho, KheCauHinh
-from tram.tho.do_may import do_cli, kiem_tag
+from tram.tho.do_may import dang_nhap_codex, do_cli, kiem_tag
 from tram.tho.kiem_may import DauDo, MucKiem
 from tram.tho.principal_khe import principal_cua
 
@@ -39,17 +39,27 @@
 
 
 def bo_sung_3b(ch: CauHinhTho, dd: DauDo, ra: list[MucKiem], *, doc_han_muc=doc_han_muc_ranh,
-               bay_gio: datetime | None = None, principal_cua_=_principal) -> list[MucKiem]:
+               bay_gio: datetime | None = None, principal_cua_=_principal, dang_nhap_=dang_nhap_codex) -> list[MucKiem]:
     ra = list(ra)
     for k in (k for k in ch.khe if k.cli == "codex"):
         kid = ch.khe_id(k)
         d = do_cli("codex", k.thu_muc_cau_hinh, which=dd.which, chay=dd.chay)
-        muc = MucKiem(f"{kid} đăng nhập", "xanh" if d.dang_nhap else "do", d.chi_tiet)
-        ra = [muc if m.muc == muc.muc else m for m in ra] if any(m.muc == muc.muc for m in ra) else [*ra, muc]
         hm, loi = None, False
         try:
-            hm = doc_han_muc(kid, k.thu_muc_cau_hinh, bay_gio=bay_gio or datetime.now(timezone.utc),
-                             principal=principal_cua_(ch, k), path=ch.chay.path_cli, codex=d.duong_dan or "codex")
+            pr = principal_cua_(ch, k)
+        except LoiThuHoi:
+            pr, loi = None, True
+        co, chi_tiet = None, "chưa có principal hoặc UID thực chưa chứng minh — không dò đăng nhập (bs-863.17)"
+        if pr is not None:
+            try:
+                co, chi_tiet = dang_nhap_(pr, d.duong_dan or "codex", k.thu_muc_cau_hinh, path=ch.chay.path_cli)
+            except LoiThuHoi:                   # A05: không spawn thêm gì (app-server) dưới principal này
+                loi, chi_tiet = True, "không xác nhận thu hồi tiến trình `codex login status` — kiểm principal"
+        muc = MucKiem(f"{kid} đăng nhập", "xanh" if co else "do", chi_tiet)
+        ra = [muc if m.muc == muc.muc else m for m in ra] if any(m.muc == muc.muc for m in ra) else [*ra, muc]
+        try:
+            hm = None if loi else doc_han_muc(kid, k.thu_muc_cau_hinh, bay_gio=bay_gio or datetime.now(timezone.utc),
+                                              principal=pr, path=ch.chay.path_cli, codex=d.duong_dan or "codex")
         except LoiThuHoi:
             loi = True
         except Exception:                                # noqa: BLE001 — dữ liệu app-server hỏng: vàng, không sập lệnh
```

Bản vá `tram/tho/kiem_cong.py`:

```diff
--- a/tram/tho/kiem_cong.py
+++ b/tram/tho/kiem_cong.py
@@ -10,6 +10,7 @@
 
 from tram.kiem import danh_tinh
 from tram.kiem.bang_tien_trinh import chup_nhan
+from tram.kiem.chay_gioi_han import chay_gioi_han
 from tram.kiem.vong_doi import LoiThuHoi
 
 from tram.tho.cau_hinh import CauHinhTho, KheCauHinh
@@ -23,19 +24,6 @@
 KEYCHAIN_CAM = ("tram-tho-token", "tram-noi-bo-token", "tram-anthropic-api-key")
 
 
-def dang_nhap(ch: CauHinhTho, k: KheCauHinh, *, goc: Path, goc_wt: Path, chay=subprocess.run) -> tuple[str, str]:
-    try:
-        p = principal_cua(ch, k, goc=goc, goc_wt=goc_wt, wt=None, ten="kiem")
-    except ChuaCoPrincipal as e:
-        return "do", str(e)
-    env = {"CLAUDE_CONFIG_DIR": str(k.thu_muc_cau_hinh), "PATH": ch.chay.path_cli, "LANG": "C.UTF-8"}
-    try:
-        kq = chay(p.boc([k.cli, *LENH_DANG_NHAP]), capture_output=True, text=True, timeout=30, env=env)
-    except (OSError, subprocess.TimeoutExpired) as e:
-        return "do", f"không chạy được lệnh trạng thái: {type(e).__name__}"
-    return ("xanh", "đã đăng nhập (lệnh chờ S2 xác nhận)") if kq.returncode == 0 else ("do", "chưa đăng nhập / lỗi")
-
-
 def _uid(p, xac_minh) -> tuple[int | None, str | None]:
     """(UID thực đã chứng minh, None) hoặc (None, lý do) — lỗi thì không chạy gì thêm dưới principal này."""
     try:
@@ -44,6 +32,25 @@
         return None, "UID thực của principal chưa chứng minh — không chạy thăm dò"
     except LoiThuHoi:
         return None, "UID: không xác nhận thu hồi tiến trình dò — kiểm principal"
+
+
+def dang_nhap(ch: CauHinhTho, k: KheCauHinh, *, goc: Path, goc_wt: Path, chay=chay_gioi_han,
+              xac_minh=danh_tinh.xac_minh_uid) -> tuple[str, str]:
+    try:
+        p = principal_cua(ch, k, goc=goc, goc_wt=goc_wt, wt=None, ten="kiem")
+    except ChuaCoPrincipal as e:
+        return "do", str(e)
+    if (ly_do := _uid(p, xac_minh)[1]) is not None:
+        return "do", ly_do
+    env = {"CLAUDE_CONFIG_DIR": str(k.thu_muc_cau_hinh), "PATH": ch.chay.path_cli, "LANG": "C.UTF-8"}
+    try:
+        kq = chay(p.boc([k.cli, *LENH_DANG_NHAP]), kill=p.kill_nhom, capture_output=True, text=True, timeout=30,
+                  env=env)
+    except LoiThuHoi:
+        return "do", "không xác nhận thu hồi tiến trình lệnh trạng thái — kiểm principal"
+    except (OSError, subprocess.SubprocessError, ValueError) as e:
+        return "do", f"không chạy được lệnh trạng thái: {type(e).__name__}"
+    return ("xanh", "đã đăng nhập (lệnh chờ S2 xác nhận)") if kq.returncode == 0 else ("do", "chưa đăng nhập / lỗi")
 
 
 def _tan_du(uid: int, chup) -> list[KetQuaThamDo]:
```

- [ ] **Step 4: Chạy, thấy xanh** — `PT tests/test_dang_nhap_principal.py tests/test_kiem_3b.py tests/test_do_may.py tests/test_kiem_cong.py tests/test_ke_hoach_dk.py tests/test_thuc_hien_dk.py tests/test_kich_ban_3b.py tests/test_han_muc_principal.py tests/test_tham_do_principal.py` → `48 passed`.

- [ ] **Step 5: Cả bộ** — `PT` → `2938` (thu thập), nhật ký chặn 0 dòng mới.

- [ ] **Step 6: Commit** — `fix(tho): dò đăng nhập dưới principal; thu hồi lỗi thì không dò hạn mức dưới principal đó (V2-6b, bs-863.17, A05)`

## Task 8 — `TheoDoi` dừng trong MỘT hạn, gồm cả lần đọc cuối; hẹn `xong` không tạo sau khi dừng (V2-6c, bs-863.16; review vòng 1 A06)

**Files:** tạo `tram/tho/trong_han.py`; sửa `tram/tho/theo_doi.py`, `tram/tho/day.py`, `tram/tho/phieu_chay.py`; test mới `tests/test_theo_doi_dung.py`, `tests/test_theo_doi_noi.py`.

**Interfaces:**
- `TheoDoi(pc, nc, dung, lenh_nhip=…, han_dung=HAN_DUNG)`; `mot_luot(ngung=None)`; `dung_lai(han=None)` (không đọc cuối; chưa dừng → `LoiThuHoi`); `ket_thuc(han=None)` — MỘT hạn tuyệt đối cho dừng luồng nền + đọc lần cuối; thuộc tính `loi_nen: str | None`, `_luong_cuoi: list[Thread]`. `HAN_DUNG = 150.0`.
- `trong_han.chay_trong_han(ham, het, *, ngung, ten, luong) -> None` — chạy `ham` ở luồng riêng; quá `het` → đặt `ngung`, `LoiThuHoi`; lỗi của `ham` ném lại ở luồng gọi.
- Hẹn `xong`: `_dat_hen()` dưới `_khoa_hen`, không tạo khi `_het_hen`; `_dung_den(het)` đặt `_het_hen`, hủy hẹn, rồi mới dừng luồng.
- `day_va_cong_bo(..., dung: threading.Event | None = None)`; `phieu_chay._mot_vong`: CLI ném → `td.dung_lai()` rồi ném lại.
- Người gọi khác không đổi (`test_tho_theo_doi_ket_thuc.py`, `test_kich_ban_3a2.py` xanh nguyên).

- [ ] **Step 1: Viết test**

Tạo mới `tests/test_theo_doi_dung.py` (nguyên văn):

```python
"""bs-863.16 (V2-6c): luồng đọc hàng đợi DỪNG HỮU HẠN — hủy giữa các dòng và trong lúc chờ đẩy mốc, `ket_thuc` có hạn,
chưa dừng → `LoiThuHoi` (khe dừng, giữ phiếu) và KHÔNG đọc lần cuối song song; dòng cuối giao đúng một lần. Hàng đợi,
hộp thư, đẩy ref đều GIẢ; không push/API thật."""
import threading
import time
from types import SimpleNamespace

import pytest

from tram.kiem.vong_doi import LoiThuHoi
from tram.tho import theo_doi
from tram.tho.hang_doi import DongHangDoi
from tram.tho.theo_doi import TheoDoi


class Hop:
    """`gui_mot` GIẢ: lần gọi đầu có thể chặn (handshake `vao`/`tha`) hoặc ném."""
    def __init__(self, chan=False, nem=False):
        self.da, self.chan, self.nem = [], chan, nem
        self.vao, self.tha = threading.Event(), threading.Event()

    def gui_mot(self, khach, duong, than):
        if self.chan and not self.vao.is_set():
            self.vao.set()
            self.tha.wait(10)
        if self.nem:
            self.nem = False
            raise RuntimeError("mất mạng")
        self.da.append(than["request_id"])


def dung(monkeypatch, dong, hop, *, cho_xong=0.2, lenh_nhip=lambda: None):
    def xu_ly(p, *, khe_id, giao_id, luot, tu_dong=0):
        return [DongHangDoi(i, {**t, "request_id": f"r-{i}"}) for i, t in enumerate(dong) if i >= tu_dong], len(dong)
    monkeypatch.setattr(theo_doi, "xu_ly_hang_doi", xu_ly)
    pc = SimpleNamespace(hang_doi=None, hop=hop, wt=None, luu=lambda: None,
                         p=SimpleNamespace(khe_id="B/claude-1", giao_id="g-1", luot=1),
                         tt=SimpleNamespace(vi_tri_hang_doi=0, ban_giao_tam=None))
    nc = SimpleNamespace(khach=None, cho_doc=0.01, cho_xong=cho_xong, cho_thu_lai=0.01,
                         ch=SimpleNamespace(chay=SimpleNamespace(day="kho-tho")))
    return TheoDoi(pc, nc, threading.Event(), lenh_nhip=lenh_nhip), pc


def test_luong_ket_io_thi_ket_thuc_tra_loi_trong_han_khong_doc_song_song(monkeypatch):
    hop = Hop(chan=True)
    td, pc = dung(monkeypatch, [{"loai": "moc"}], hop)
    td.bat_dau()
    assert hop.vao.wait(5)
    t0 = time.monotonic()
    try:
        with pytest.raises(LoiThuHoi):
            td.ket_thuc(han=0.2)
        assert time.monotonic() - t0 < 2 and hop.da == [] and pc.tt.vi_tri_hang_doi == 0
    finally:
        hop.tha.set()
        td._luong.join(5)
    assert hop.da == ["r-0"]                                            # chỉ luồng nền giao, không lần đọc thứ hai


def test_huy_giua_cac_dong_dong_con_lai_giao_dung_mot_lan(monkeypatch):
    hop = Hop(chan=True)
    td, pc = dung(monkeypatch, [{"loai": "moc"}, {"loai": "moc"}, {"loai": "moc"}], hop)
    td.bat_dau()
    assert hop.vao.wait(5)
    kt = threading.Thread(target=td.ket_thuc, kwargs={"han": 5})
    kt.start()
    time.sleep(0.1)
    hop.tha.set()
    kt.join(10)
    assert not kt.is_alive() and hop.da == ["r-0", "r-1", "r-2"] and pc.tt.vi_tri_hang_doi == 3


def test_xong_dat_dung_dung_han_khi_luong_ket_va_ket_thuc_huy_hen(monkeypatch):
    ket = threading.Event()
    td, _ = dung(monkeypatch, [{"loai": "xong"}], Hop(), lenh_nhip=lambda: ket.wait(10) and None)
    td.bat_dau()
    try:
        assert td.dung.wait(3) and td.xong is not None                 # hẹn 0,2 s chạy dù luồng đang kẹt
    finally:
        ket.set()
        td.ket_thuc(han=5)
    td2, _ = dung(monkeypatch, [{"loai": "xong"}], Hop(), cho_xong=5)
    td2.mot_luot()
    td2.ket_thuc(han=5)
    time.sleep(0.1)
    assert not td2.dung.is_set() and not td2._hen.is_alive()


def test_loi_o_luong_nen_thi_doc_cuoi_thu_lai_dung_mot_lan(monkeypatch):
    hop = Hop(nem=True)
    td, pc = dung(monkeypatch, [{"loai": "moc"}], hop)
    td.bat_dau()
    het = time.monotonic() + 5
    while td.loi_nen is None and time.monotonic() < het:
        time.sleep(0.01)
    td.ket_thuc(han=5)
    assert td.loi_nen == "RuntimeError" and hop.da == ["r-0"] and pc.tt.vi_tri_hang_doi == 1


def test_doc_cuoi_ket_io_thi_ket_thuc_tra_loi_trong_mot_han(monkeypatch):
    """A06: hạn của `ket_thuc` bao trùm cả lần đọc cuối — chặn RIÊNG lần đọc cuối (luồng nền không có gì kẹt)."""
    hop = Hop(chan=True)
    td, pc = dung(monkeypatch, [{"loai": "moc"}], hop)              # không bat_dau: dòng chỉ được đọc ở lần cuối
    t0 = time.monotonic()
    try:
        with pytest.raises(LoiThuHoi):
            td.ket_thuc(han=0.3)
        assert time.monotonic() - t0 < 2 and hop.vao.is_set() and pc.tt.vi_tri_hang_doi == 0
    finally:
        hop.tha.set()


class HopCham(Hop):
    def gui_mot(self, khach, duong, than):
        time.sleep(0.05)
        self.da.append(than["request_id"])


def test_backlog_nhieu_dong_doc_cuoi_thoi_o_ranh_gioi_dong_trong_han(monkeypatch):
    hop = HopCham()
    td, pc = dung(monkeypatch, [{"loai": "moc"}] * 50, hop)
    t0 = time.monotonic()
    with pytest.raises(LoiThuHoi):
        td.ket_thuc(han=0.5)
    assert time.monotonic() - t0 < 1.5
    td._luong_cuoi[0].join(5)                                       # luồng đọc cuối thôi ở ranh giới dòng kế tiếp
    assert 0 < len(hop.da) < 50 and len(set(hop.da)) == len(hop.da) and pc.tt.vi_tri_hang_doi == len(hop.da)


def test_xong_gap_o_lan_doc_cuoi_khong_tao_hen_sau_khi_dung(monkeypatch):
    td, _ = dung(monkeypatch, [{"loai": "xong"}], Hop(), cho_xong=0.1)
    td.ket_thuc(han=5)
    time.sleep(0.3)
    assert td.xong is not None and not td.dung.is_set() and td._hen is None
    td._dat_hen()                                                   # đã bắt đầu dừng: không bao giờ tạo hẹn mới
    assert td._hen is None
```

Tạo mới `tests/test_theo_doi_noi.py` (nguyên văn):

```python
"""bs-863.16 (V2-6c): nối dừng hữu hạn vào đẩy mốc và vòng phiếu — đẩy mốc thôi thử lại ngay khi bị hủy; CLI lỗi thì
dừng luồng đọc (có hạn, không đọc lần cuối), luồng chưa dừng thì `LoiThuHoi` thắng lỗi gốc. Mọi thứ GIẢ."""
import threading
import time
from types import SimpleNamespace

import pytest

import tram.tho.phieu_chay as phieu_chay
from tram.kiem.vong_doi import LoiThuHoi
from tram.tho import day


def test_day_mot_dung_thi_thoi_thu_lai_ngay(monkeypatch):
    monkeypatch.setattr(day, "dua_len_ref_tam", lambda *a, **k: False)
    p = SimpleNamespace(giao_id="g-1", luot=1, khe_id="B/claude-1", bead_id="hr-1")
    huy = threading.Event()
    threading.Timer(0.1, huy.set).start()
    t0 = time.monotonic()
    kq = day.day_va_cong_bo(None, p, "a" * 40, khach=None, phuong_an="ref-tam", han=time.monotonic() + 60, cho=5,
                            dung=huy)
    assert kq == "chua-cong-bo" and time.monotonic() - t0 < 2


def test_cli_loi_thi_dung_luong_khong_doc_cuoi_va_thu_hoi_loi_thang(monkeypatch):
    goi = []

    class TD:
        def __init__(self, *a, **kw):
            pass

        def bat_dau(self):
            return self

        def dung_lai(self):
            goi.append("dung_lai")
            raise LoiThuHoi("luồng chưa dừng")

        def ket_thuc(self):
            goi.append("ket_thuc")
    monkeypatch.setattr(phieu_chay, "TheoDoi", TD)
    monkeypatch.setattr(phieu_chay, "ly_do_khong_chay", lambda *a: None)
    monkeypatch.setattr(phieu_chay, "chay_mot_lan", lambda *a: (_ for _ in ()).throw(OSError("log")))
    with pytest.raises(LoiThuHoi):
        phieu_chay._mot_vong(object(), SimpleNamespace(dong_ho=lambda: None), SimpleNamespace(lenh=None))
    assert goi == ["dung_lai"]
```

- [ ] **Step 2: Chạy, thấy đỏ** — `PT tests/test_theo_doi_dung.py tests/test_theo_doi_noi.py`. Kết quả thật (mã của Task 7):

```
E               TypeError: TheoDoi.ket_thuc() got an unexpected keyword argument 'han'      (6 lần)
E       AssertionError: assert (not False and [] == ['r-0', 'r-1', 'r-2']
E       AttributeError: 'TheoDoi' object has no attribute 'loi_nen'
E       TypeError: day_va_cong_bo() got an unexpected keyword argument 'dung'
E   OSError: log
9 failed, 4 warnings in 5.56s
```

**Đối chứng bản trước (đã có `dung_lai`/`ket_thuc(han)` nhưng đọc cuối không có hạn, hẹn không khoá)**, chạy cùng file test → `3 failed, 4 passed in 14.00s`:

```
E           Failed: DID NOT RAISE <class 'tram.kiem.vong_doi.LoiThuHoi'>   ← đọc cuối kẹt I/O: ket_thuc(han=0,3) giữ ~10 s
E       Failed: DID NOT RAISE <class 'tram.kiem.vong_doi.LoiThuHoi'>       ← backlog 50 dòng: đọc hết 2,5 s, quá hạn 0,5 s
E       AssertionError: assert ({'loai': 'xong', …} is not None and not True)  ← đọc cuối tạo hẹn mới SAU khi dừng
```

- [ ] **Step 3: Mã**

Bản vá `tram/tho/day.py`:

```diff
--- a/tram/tho/day.py
+++ b/tram/tho/day.py
@@ -5,6 +5,7 @@
 request_id tới hạn chót."""
 import hashlib
 import subprocess
+import threading
 import time
 from collections.abc import Callable
 from pathlib import Path
@@ -58,11 +59,15 @@
 
 
 def day_va_cong_bo(wt: Path, phieu: Phieu, commit: str, *, khach: KhachTram, phuong_an: str, han: float,
-                   cho: float = 5.0, ngu: Callable[[float], None] = time.sleep) -> str:
+                   cho: float = 5.0, ngu: Callable[[float], None] = time.sleep,
+                   dung: threading.Event | None = None) -> str:
     """Trả `cong_bo` | `khong-cong-bo` | `ngoai-luong` | `luot-cu` | `chua-cong-bo` (tới `han` — giờ monotonic —
-    vẫn chưa xác nhận: trạm giữ snapshot cũ, thợ KHÔNG ghi "đã lưu toàn bộ")."""
+    vẫn chưa xác nhận: trạm giữ snapshot cũ, thợ KHÔNG ghi "đã lưu toàn bộ"). `dung` đặt (luồng đọc hàng đợi đang
+    dừng, bs-863.16) → thôi thử lại ngay sau lần đang dở, trả `chua-cong-bo`."""
     than = than_da_push(phieu, commit)
     while True:
+        if dung is not None and dung.is_set():
+            return "chua-cong-bo"
         if dua_len_ref_tam(wt, phieu, commit, phuong_an=phuong_an, timeout=max(1.0, min(60.0, han - time.monotonic()))):
             try:
                 ma, kq = khach.goi("POST", "/api/tho/da-push", than)
@@ -76,4 +81,7 @@
                 return "luot-cu"
         if time.monotonic() + cho >= han:
             return "chua-cong-bo"
-        ngu(cho)
+        if dung is None:
+            ngu(cho)
+        else:
+            dung.wait(cho)
```

Bản vá `tram/tho/phieu_chay.py`:

```diff
--- a/tram/tho/phieu_chay.py
+++ b/tram/tho/phieu_chay.py
@@ -52,7 +52,11 @@
         return ly
     vk.dung, vk.buoc = threading.Event(), "chay"
     td = TheoDoi(pc, nc, vk.dung, lenh_nhip=lambda: vk.lenh).bat_dau()
-    kq = chay_mot_lan(pc, nc, vk.dung)
+    try:
+        kq = chay_mot_lan(pc, nc, vk.dung)
+    except BaseException:
+        td.dung_lai()                           # bs-863.16: có hạn; chưa dừng → LoiThuHoi thắng lỗi gốc
+        raise
     td.ket_thuc()
     if vk.lenh in (*DUNG_CUNG, "tat-tho"):
         return "cung" if vk.lenh in DUNG_CUNG else "tat-tho"
```

Bản vá `tram/tho/theo_doi.py`:

```diff
--- a/tram/tho/theo_doi.py
+++ b/tram/tho/theo_doi.py
@@ -1,48 +1,67 @@
 """Đọc hàng đợi `tram bao` của phiếu trong lúc CLI chạy (spec 3 §7.4) — luồng nền, mỗi `cho_doc` giây. Mỗi dòng đã
 được kiểm lại + gắn phiếu bởi `xu_ly_hang_doi` (3a-1): `moc` → đưa lên ref tạm + `da-push` rồi `bao.moc` (giữ bàn
 giao tạm cho lần sau); `can_hoi` → `bao.can_hoi` rồi DỪNG MỀM NGAY (4a: chưa có `pham_vi_doc_lap`); `bi` → dừng;
-`xong` → cho CLI tối đa `cho_xong` giây để thoát rồi dừng. Lệnh dừng từ nhịp tim cũng được chuyển thành `dung`."""
+`xong` → cho CLI tối đa `cho_xong` giây để thoát rồi dừng. Lệnh dừng từ nhịp tim cũng được chuyển thành `dung`.
+bs-863.16 + review vòng 1 A06: MỘT hạn (`han_dung`) bao trùm chờ luồng nền VÀ lần đọc cuối (chạy ở luồng riêng); hết hạn
+→ báo thôi ở ranh giới dòng/đẩy mốc kế tiếp, `LoiThuHoi` (khe dừng, giữ phiếu; dòng chưa xử lý giữ vị trí — request_id
+tất định). Một lượt đọc giữ khoá: không đọc song song. Đã bắt đầu dừng thì không hẹn `xong` nào được tạo nữa."""
 import threading
 import time
 
+from tram.kiem.vong_doi import LoiThuHoi
 from tram.tho.chuan_bi import PhieuDangChay
 from tram.tho.day import day_va_cong_bo
 from tram.tho.hang_doi import xu_ly_hang_doi
 from tram.tho.ngu_canh import NguCanhTho
+from tram.tho.trong_han import chay_trong_han
 
 DUNG_CUNG = ("luot-cu", "thu-hoi")
+HAN_DUNG = 150.0        # > một dòng mốc: git update-ref ≤ 60 s + push ≤ 60 s + gửi HTTP (`KhachTram.thoi_gian_cho`)
 
 
 class TheoDoi:
-    def __init__(self, pc: PhieuDangChay, nc: NguCanhTho, dung: threading.Event, lenh_nhip=lambda: None):
-        self.pc, self.nc, self.dung, self.lenh_nhip = pc, nc, dung, lenh_nhip
+    def __init__(self, pc: PhieuDangChay, nc: NguCanhTho, dung: threading.Event, lenh_nhip=lambda: None,
+                 han_dung: float = HAN_DUNG):
+        self.pc, self.nc, self.dung, self.lenh_nhip, self.han_dung = pc, nc, dung, lenh_nhip, han_dung
         self.xong: dict | None = None
         self.bi: dict | None = None
-        self.can_hoi = False
-        self.loi: list[str] = []
-        self._ngung = threading.Event()
+        self.can_hoi, self.loi = False, []
+        self._ngung, self._ngung_cuoi = threading.Event(), threading.Event()
         self._luong: threading.Thread | None = None
+        self._luong_cuoi: list[threading.Thread] = []
+        self._khoa, self._khoa_hen = threading.Lock(), threading.Lock()
+        self._hen, self._het_hen = None, False          # hẹn `xong`; đã bắt đầu dừng → không tạo hẹn mới
+        self.loi_nen: str | None = None                 # tên lỗi ở luồng nền — lần đọc cuối thử lại các dòng chưa ghi
 
-    def _moc(self, than: dict) -> None:
+    def _moc(self, than: dict, ngung: threading.Event | None) -> None:
         pc, nc = self.pc, self.nc
         if than.get("ban_giao"):
             pc.tt.ban_giao_tam = than["ban_giao"]
         if than.get("commit") and len(than["commit"]) == 40:
             day_va_cong_bo(pc.wt, pc.p, than["commit"], khach=nc.khach, phuong_an=nc.ch.chay.day,
-                           han=time.monotonic() + 60, cho=nc.cho_thu_lai)
+                           han=time.monotonic() + 60, cho=nc.cho_thu_lai, dung=ngung)
         pc.hop.gui_mot(nc.khach, "/api/tho/bao", than)
 
-    def mot_luot(self) -> None:
+    def mot_luot(self, ngung: threading.Event | None = None) -> None:
+        with self._khoa:
+            self._doc(ngung)
+        if self.lenh_nhip() and not self.dung.is_set():
+            self.dung.set()
+
+    def _doc(self, ngung: threading.Event | None) -> None:
         pc = self.pc
         ds, ke = xu_ly_hang_doi(pc.hang_doi, khe_id=pc.p.khe_id, giao_id=pc.p.giao_id, luot=pc.p.luot,
                                 tu_dong=pc.tt.vi_tri_hang_doi)
         for d in ds:
+            if ngung is not None and ngung.is_set():
+                ke = d.so                                       # chưa xử lý: lần đọc cuối làm tiếp, đúng một lần
+                break
             if d.than is None:
                 self.loi.append(f"dòng {d.so}: {d.loi}")
             elif self.xong or self.bi or self.can_hoi:
                 continue                                        # sau dòng kết thúc: bỏ
             elif d.than["loai"] == "moc":
-                self._moc(d.than)
+                self._moc(d.than, ngung)
             elif d.than["loai"] == "can_hoi":
                 pc.hop.gui_mot(self.nc.khach, "/api/tho/bao", d.than)
                 self.can_hoi = True
@@ -52,26 +71,46 @@
                 self.dung.set()
             elif d.than["loai"] == "xong":
                 self.xong = d.than
-                hen = threading.Timer(self.nc.cho_xong, self.dung.set)
-                hen.daemon = True
-                hen.start()
+                self._dat_hen()
         pc.tt.vi_tri_hang_doi = ke
         pc.luu()
-        if self.lenh_nhip() and not self.dung.is_set():
-            self.dung.set()
 
     def _vong(self) -> None:
-        while not self._ngung.wait(self.nc.cho_doc):
-            self.mot_luot()
+        try:
+            while not self._ngung.wait(self.nc.cho_doc):
+                self.mot_luot(self._ngung)
+        except Exception as e:                          # noqa: BLE001 — vị trí chưa ghi: lần đọc cuối thử lại
+            self.loi_nen = type(e).__name__
 
     def bat_dau(self) -> "TheoDoi":
         self._luong = threading.Thread(target=self._vong, daemon=True, name=f"theo-doi-{self.pc.p.giao_id}")
         self._luong.start()
         return self
 
-    def ket_thuc(self) -> None:
-        """Dừng luồng nền rồi đọc lần cuối (dòng ghi ngay trước khi CLI thoát)."""
+    def _dat_hen(self) -> None:
+        with self._khoa_hen:
+            if not self._het_hen:
+                self._hen = threading.Timer(self.nc.cho_xong, self.dung.set)
+                self._hen.daemon = True
+                self._hen.start()
+
+    def _dung_den(self, het: float) -> None:
+        with self._khoa_hen:
+            self._het_hen = True
+            if self._hen is not None:
+                self._hen.cancel()
         self._ngung.set()
-        if self._luong:
-            self._luong.join()
-        self.mot_luot()
+        if self._luong is not None:
+            self._luong.join(max(0.0, het - time.monotonic()))
+            if self._luong.is_alive():
+                raise LoiThuHoi("luồng đọc hàng đợi chưa dừng trong hạn — dừng khe, giữ phiếu")
+
+    def dung_lai(self, han: float | None = None) -> None:     # KHÔNG đọc lần cuối; chưa dừng → `LoiThuHoi`
+        self._dung_den(time.monotonic() + (self.han_dung if han is None else han))
+
+    def ket_thuc(self, han: float | None = None) -> None:
+        """Dừng luồng nền rồi đọc lần cuối (dòng ghi ngay trước khi CLI thoát) — cả hai trong MỘT hạn."""
+        het = time.monotonic() + (self.han_dung if han is None else han)
+        self._dung_den(het)
+        chay_trong_han(lambda: self.mot_luot(self._ngung_cuoi), het, ngung=self._ngung_cuoi,
+                       ten=f"đọc hàng đợi lần cuối {self.pc.p.giao_id}", luong=self._luong_cuoi)
```

Tạo mới `tram/tho/trong_han.py` (nguyên văn):

```python
"""Chạy MỘT việc không hủy được giữa chừng (I/O mạng, đẩy mốc) trong luồng riêng với hạn TUYỆT ĐỐI `het` (V2-6c, review
vòng 1 A06): xong trong hạn → trả (lỗi của việc ném lại ở luồng gọi); quá hạn → đặt `ngung` (việc tự thôi ở ranh giới
an toàn kế tiếp) rồi ném `LoiThuHoi` — người gọi không bao giờ bị giữ quá hạn. Luồng vào `luong` để người gọi
chờ/kiểm."""
import threading
import time
from collections.abc import Callable

from tram.kiem.vong_doi import LoiThuHoi


def chay_trong_han(ham: Callable[[], None], het: float, *, ngung: threading.Event, ten: str, luong: list) -> None:
    loi: list[BaseException] = []

    def chay() -> None:
        try:
            ham()
        except BaseException as e:                      # noqa: BLE001 — chuyển về luồng gọi
            loi.append(e)
    t = threading.Thread(target=chay, daemon=True, name=ten)
    luong.append(t)
    t.start()
    t.join(max(0.0, het - time.monotonic()))
    if t.is_alive():
        ngung.set()
        raise LoiThuHoi(f"{ten}: chưa xong trong hạn — dừng khe, giữ phiếu")
    if loi:
        raise loi[0]
```

- [ ] **Step 4: Chạy, thấy xanh** — `PT tests/test_theo_doi_dung.py tests/test_theo_doi_noi.py tests/test_tho_theo_doi_ket_thuc.py tests/test_kich_ban_3a2.py tests/test_phieu_chay_thu_hoi.py tests/test_tho_day.py tests/test_khe_tan_du.py` → `31 passed`.

- [ ] **Step 5: Cả bộ** — `PT` → `2947 passed` (đo cả bộ), nhật ký chặn 0 dòng mới.

- [ ] **Step 6: Commit** — `fix(tho): luồng đọc hàng đợi dừng trong một hạn gồm cả lần đọc cuối (V2-6c, bs-863.16, A06)`

## Bước cổng trên OS thật (không tự chạy — Đại ca cho phép từng kịch bản)

Đưa vào sổ tay theo phụ lục cổng đợt 7. Mỗi bước ghi lệnh, giờ, kết quả, người cho phép vào mục "Ghi bằng chứng". Các bước dưới là bằng chứng OS — KHÔNG thay cho các sửa logic ở trên (review §5).

| Cổng | Bước | Cách đo | Đạt khi |
|---|---|---|---|
| G3 | V0.1 nền tảng + bố cục | Trên máy B, tài khoản trạm và tài khoản quản lý thợ: `sw_vers`, `uname -a`; `uv run python -c "from tram.kiem.bang_tien_trinh import chup_nhan as c; print(len(c()))"` cạnh `ps -A \| wc -l` | không `OSError` (tự kiểm bố cục đạt), số dòng lệch ≤ vài tiến trình. macOS khác 15.6.1 → đo lại `offsetof` bằng chương trình C ở mục "Nền tảng đã đo" TRƯỚC khi dùng |
| G3 | V0.2 thấy tiến trình của principal | Sau khi có `tram-kiem`/tài khoản khe (S6): trong lúc `xac_minh_uid` chạy `/bin/sleep` dưới principal, `chup_nhan()` từ tài khoản trạm/quản lý thấy dòng uid = ruid = UID principal, `sinh` khác None | đúng; không thấy → dừng, không dùng V2-0 cho principal |
| G3 | V0.5 phạm vi gửi của nhân (A01) | Tài khoản quản lý tạo một `sleep 300` của CHÍNH nó ở nhóm riêng (canh), ghi pgid; chạy `sudo -n -u <tài khoản khe thử> /bin/kill -s TERM -- -<pgid canh>` | lệnh báo `Operation not permitted`, `sleep` canh còn sống. Ngược lại → DỪNG, A01 không đứng được trên máy này |
| G3 | V0.3 độ trễ `sudo -n … /bin/kill` | 20 lần `sudo -n -u <khe thử> /usr/bin/true` | ghi p50/p99 — CHỈ là số hiệu năng (cận trên `thu_hoi`); an toàn không còn phụ thuộc độ trễ (A01) |
| G4 | Thu hồi + dọn theo UID (A02) | Harness dưới tài khoản khe thử: cháu tách phiên TRƯỚC ảnh đầu + cha thoát ngay; cháu cùng nhóm bỏ qua SIGTERM; cha thoát sớm; ngắt lần hai. Một `sleep` canh của tài khoản quản lý chạy suốt. Sau lượt: `don_uid` thật | `don_uid` xác nhận 0 tiến trình uid/ruid của khe (hoặc khe dừng với `LoiThuHoi`); `sleep` canh còn sống; không có tín hiệu nào tới tài khoản khác. Giới hạn bằng chứng: tái dùng số PID/PGID không ép được an toàn trên máy thật — offline chỉ chứng minh LOGIC chọn kênh gửi (`test_pham_vi_gui`), an toàn thật dựa vào kiểm quyền của nhân (V0.5); số test pass không phải chứng minh tuyệt đối |
| G5 | Thăm dò + đăng nhập dưới principal khe (A04) | `tram tho kiem` trên khe thử khi `tram tho chay` ĐÃ DỪNG: UID xác minh; ghi lại mã thoát + câu stderr THẬT của từng loại (`security` không thấy mục, `cat`/`ls`/`touch` bị từ chối, `nc` bị chặn, `tram` bị từ chối, curl 401/403) vào sổ tay — KHÔNG ghi stdout | mỗi âm "đạt" có đúng dấu hiệu của bảng `cham_tham_do`; loại nào ra "không kết luận" thì sửa bảng chấm bằng bead riêng (không nới thành "mã ≠ 0"); thiếu sudoers → ĐỎ ≤ 30 s mỗi thăm dò; log không có token/email |
| G5 | Đăng nhập | `codex login status`/`claude auth status` dưới principal; thử principal không thu hồi được (ví dụ chặn `/bin/kill` trong sudoers khe thử) | `LoiThuHoi` → đăng nhập + hạn mức ĐỎ, không app-server nào được spawn |
| G7 | Khởi động lại thợ khi CLI đang chạy | Dừng `tram tho chay` giữa phiếu (khe thử), chạy lại | dọn UID xác nhận 0 tiến trình của khe, `chay.xong mo-coi` gửi đúng một lần, phiếu chạy tiếp; với bản ghi `dang-chay.pid` định dạng cũ cũng vậy |
| G7 | Tàn dư không giết được | Khe thử chạy một tiến trình setuid-root mà uid thực là khe (ví dụ `login` treo) rồi dừng phiếu | khe dừng với "còn N tiến trình của UID khe", giữ bản ghi + phiếu, không nhận phiếu mới |
| G7 | `TheoDoi` kẹt mạng | Cắt mạng tới trạm khi agent đang `tram bao --moc` ngay trước khi CLI thoát | khe dừng với `LoiThuHoi` trong ≤ `HAN_DUNG` (150 s) TÍNH CẢ lần đọc cuối, phiếu/hộp thư còn, không lượt mới |

## Rủi ro còn lại (không đóng bằng plan này)

1. **Khe sở hữu ĐÃ ĐÓNG ở mức mã (R2-02):** mọi người gọi `khoi_chay` dùng khối sở hữu, `chu` bắt buộc. Còn lại, ghi rõ không tuyên bố quá: (a) `subprocess.Popen` hỏng NỘI BỘ sau fork mà không phải lỗi exec (vd. `MemoryError` giữa chừng) thì Popen không trả đối tượng nào — con có thể sống không chủ trong phiên; ngắt không gây được ca này vì đã hoãn; (b) SIGTERM với handler MẶC ĐỊNH được phát lại vẫn giết tiến trình như trước (chỉ CLI có `term_thanh_ngat` — plan B — mới dọn); (c) `LoiThuHoi` dưới chính tài khoản quản lý (lệnh cục bộ) không có lưới dọn theo UID: chỉ cổng/khe đóng + Đại ca kiểm tay.
2. **SIGKILL vào tiến trình quản lý** không hoãn được: con/cháu mồ côi tới lần khởi động sau (dọn UID lúc khởi động khe bắt được).
3. **Dọn theo UID giết MỌI tiến trình của tài khoản khe** ở các mốc (khởi động, đầu phiếu, sau mỗi lần chạy) — kể cả phiên Đại ca tự mở dưới tài khoản đó hay `tram tho kiem` chạy song song. Câu hỏi 2.
4. **Bảng chấm thăm dò dựa vào thông điệp tiếng Anh** (`LANG=C.UTF-8` đặt trong env thăm dò): khác đi thì ra "không kết luận" (phía an toàn) — đo ở G5.
5. **Lần đọc cuối quá hạn** để lại một thao tác I/O đang dở trong luồng daemon; nó có thể xong SAU `LoiThuHoi` và ghi vị trí — khe đã dừng, gửi lại sau khởi động là idempotent.
6. **`p_starttime` là giờ tường; bố cục `kinfo_proc` theo phiên bản macOS** — như bản trước (G3 V0.1 bắt buộc khi đổi macOS).
7. **Chế độ cùng user (không principal — test/dev):** nhóm ngoài gốc không bao giờ được gửi → nhiều `LoiThuHoi` hơn (phía an toàn).
8. **`tram chu kiem-cach-ly` (trạm) chưa có quan sát tàn dư cho principal khe** — chỉ `tram tho kiem` có; `tram-kiem` đã có dọn UID mỗi lượt (`cong_that`). Gắn với câu hỏi 1.
9. **Khoá worktree `.tram/khoa` và `don_dep`** vẫn theo pid (`con_song`) — chỉ chặn chạy, không gửi tín hiệu (như bản trước).
10. **`cong_that.cho_het_uid`** vẫn chụp bằng `ps` (không đổi file đó).

## Thứ tự code đề xuất và file giao nhau

1. Đại ca duyệt plan → review Codex vòng 2 (gộp với B, C) → nhận review.
2. **Primitive trước (review §4 mục 1):** Task 1 → 2 → 3 → 4, MỘT subagent, tuần tự (chung `vong_doi.py`, `ngat.py`, `so_huu.py`, `gui_tin.py`, `chay_gioi_han.py`, `han_tong.py`, người gọi). Đây là hợp đồng sở hữu và bản thân hàm cuối mà B-T6/T7/T8 áp lên.
3. Thứ tự ghép CUỐI (đã chạy thật): A-T1 → … → A-T8, rồi B-T1 → … → B-T9; B-T6/T7/T8 là các hunk viết TRÊN cây đã có A-T1…T8.
4. Task 5 (vòng khe) sau Task 4. Task 6 → 7 (chung `kiem_cong.py`) song song với Task 8 (`theo_doi.py`, `day.py`, `trong_han.py`; `phieu_chay.py` chung với Task 5 → Task 8 sau Task 5).
5. C18 (dọn của plan C) sau A + B, vì chung `tram/tho/kiem_cong.py`, `kiem_may.py`.
6. QC (`.handover/qc/qc.py`), cả bộ với PATH chặn host, ghép; rồi mới tới các bước cổng ở trên.

| File | Plan này | Plan khác |
|---|---|---|
| `tram/kiem/chay_gioi_han.py` | T2 (`chu`), T4 thân hàm CUỐI (hạn trước spawn, `_ong`, `_don`) | B-T6 chỉ thêm `stdin=` (chữ ký, loại trừ `input`, chọn `vao`) trên đúng bản T4; B-T7 dùng làm runner của đích |
| `tram/kiem/han_tong.py` | T2 (`chu`), T3 (`gop_kill` từ `gui_tin`), T4 thân hàm CUỐI | B KHÔNG sửa; B-T8 thêm test cuối `test_han_tong_ngat.py` + `test_ngat_ab.py` (plan này không đụng hai file đó) |
| `tram/kiem/ngat.py` | T2 tạo (`hoan`) | B-T6 thêm `NgatTerm`, `term_thanh_ngat` cuối file |
| `tram/kiem/vong_doi.py`, `so_huu.py` | T2, T3 (`khoi_chay(chu)` bắt buộc, phạm vi gửi) | B-T7 `cay_kiem.nguon_archive(chu=)`, `ong_chep` thu hồi `chu`; nhóm ngoài gốc của nguồn chạy cục bộ không được gửi (kênh cục bộ chỉ cho gốc) |
| `tram/tho/kiem_cong.py` | T6, T7 | C18 dọn sau |
| `tram/giao_viec/cong_that.py`, `principal_kiem.py`, `tram/tho/principal.py` | không sửa (nhận diện kênh theo UID qua `co_che == "user"` + tên `kill_nhom`) | V2-3/V2-5 sửa `cong_that` |
| `main` sau `7921f26` (`b358532`: V3-1/8/9/10/17) | không trùng file mã của plan; `test_ke_hoach_dk.py`/`test_thuc_hien_dk.py` (đổi ở V3-8) nằm trong lệnh xanh T7 — chạy lại khi rebase | — |

## Câu hỏi cho Đại ca

1. **Kiểm cách ly khe từ tài khoản trạm (`tram chu kiem-cach-ly --principal …`).** Lệnh này nay "không bao giờ hỏi mật khẩu" (trước đây có thể treo mãi). Khi tài khoản trạm chưa được phép chạy thay tài khoản khe mà không mật khẩu, mục kiểm khe luôn ĐỎ. Lựa chọn: (A) cấp thêm quyền đó lúc cài máy (tài khoản trạm mạnh thêm); (B) không kiểm khe từ tài khoản trạm nữa, chỉ kiểm bằng `tram tho kiem` ở tài khoản quản lý thợ (đã có quyền); hai phép kiểm "gọi API Duyệt giả danh Đại ca" và "kết nối DB" cho khe được chuyển sang `tram tho kiem` bằng bead riêng, và **cổng G5 chưa đạt cho tới khi hai phép đó chạy được** dưới đúng principal; (C) để ĐỎ, quyết sau. **Em đề xuất B** — không mở thêm quyền, không bỏ bằng chứng. Nếu chọn A: tài khoản trạm rộng quyền hơn; C: G5 thiếu bằng chứng.
2. **Dọn sạch tài khoản khe ở mỗi mốc.** Để chắc không còn tiến trình nào của agent sót sang việc sau, mỗi lần khởi động khe, đầu mỗi phiếu và sau mỗi lần chạy, hệ thống giết hết mọi tiến trình đang chạy dưới tài khoản của khe đó (chỉ tài khoản đó, không đụng tài khoản khác). Hệ quả: Đại ca muốn đăng nhập tay dưới tài khoản khe (ví dụ `codex login`) hay chạy `tram tho kiem` thì phải dừng `tram tho chay` trước, không thì có thể bị cắt giữa chừng. **Em đề xuất đồng ý và ghi luật này vào sổ tay.** Nếu không đồng ý: cần thêm công tắc "khe tạm nghỉ" (việc mới, bead riêng) — trong lúc chờ, khe vẫn dọn như trên vì an toàn ưu tiên.
3. **Chụp bảng tiến trình 4 lần mỗi giây** (trước là 1 lần) trong lúc một lệnh đang chạy: khoảng 0,4% CPU mỗi lệnh. Nay việc này chỉ giúp thu hồi gọn hơn, không còn là điều kiện an toàn (an toàn đã nhờ phạm vi gửi + dọn theo tài khoản). **Em đề xuất đồng ý tạm, đo lại ở G3** và chỉnh nếu tốn.
4. **`tram tho dang-ky` thôi kiểm đăng nhập CLI** (chỉ còn kiểm phiên bản) vì lúc đăng ký chưa có tài khoản khe; kiểm đăng nhập chuyển hẳn sang `tram tho kiem`. **Em đề xuất đồng ý.** Hệ quả: bảng kế hoạch đăng ký luôn có dòng nhắc "đăng nhập kiểm sau bằng `tram tho kiem`".

(Các câu hỏi 2 và 3 của bản trước — "lưới an toàn cho khe thợ", "bản ghi cũ không chứng minh được" — đã được giải bằng thiết kế ở Task 5: khe tài khoản riêng được dọn theo tài khoản, khe dùng chung tài khoản không được chạy (đúng D53), bản ghi cũ không còn cần đối soát tay vì việc dọn không dựa vào số trong bản ghi.)

## Phản hồi review vòng 1

Nguồn: `.handover/review-codex-plan/REVIEW-CODEX-dot8-vong1.md` §1 (Plan A). "Đỏ → xanh thật" = chạy trong worktree `plan/v2-vong-doi` ở `7921f26`, 18/10/2026, PATH chặn host, nhật ký chặn 0 dòng mới; "đột biến" = đổi riêng phần sửa về cách của bản trước rồi chạy lại test mới.

| Mã | Mức | Đã sửa ở đâu | Bằng chứng |
|---|---|---|---|
| A01 | Chặn | Task 3 (dòng 828): `gui_tin.kill_uid`/`GopKill` (dòng 1463), `Nhom._gui` (bản vá dòng 1563 — nhóm ngoài gốc chỉ qua kênh dưới UID dành riêng), `cau_hinh` cấm trùng `user:` (dòng 1682); Task 5: mồ côi dọn theo UID, bỏ `dung_nhom` theo số pgid (dòng 2341) | `test_pham_vi_gui.py`: thay nhóm SAU lần kiểm cuối và GIỮA hai kênh, so toàn bộ tín hiệu đã trúng; đột biến về thiết kế vòng trước → `4 failed, 2 passed` (trúng tiến trình 7000 của tài khoản khác); sau sửa xanh. `test_kenh_cuc_bo_khong_gui_nhom_ngoai_goc…` (tiến trình thật) đỏ ở Task 2 → xanh. Cổng G3 V0.5 đo kiểm quyền của nhân |
| A02 | Chặn | Task 5 (dòng 1999): `tho/don_uid.py` (dòng 2281), `NguCanhTho.don_khe` (dòng 2473), gọi ở `khoi_dong`/`chay_phieu`/`chay_mot_lan` (dòng 2412, 2513, 2458); sandbox từ chối → khe dừng; Task 6: tàn dư sau thăm dò → ĐỎ (dòng 3221); docstring `vong_doi`: True = cây quan sát được | `test_khe_tan_du.py` (vòng `tram tho chay` thật): đỏ hành vi ở Task 4 (`assert (False)` ×3 — khe không dừng, lần 2 vẫn spawn) → xanh; `test_don_uid.py` (10 ca, gồm sandbox/UID trùng/không đọc được bảng); `test_tho_kiem_con_tien_trinh_cua_principal…` |
| A03 | Quan trọng | Task 2 (dòng 358): `so_huu` (dòng 609), `khoi_chay(chu=)` (dòng 662); Task 4 (dòng 1703): `chay_gioi_han` bỏ `communicate` (dòng 1831), `han_tong` spawn trong try/finally (dòng 1943), `danh_tinh` không `poll` (dòng 1927) | `test_so_huu.py` (lỗi kqueue/`KeyboardInterrupt` sau Popen, SIGINT lúc spawn): đỏ (bản trước để `OSError`/`KeyboardInterrupt` lọt, con không ai thu hồi) → xanh; `test_so_huu_bo_chay.py`: đỏ ở Task 3 (`LoiThuHoi` vì `communicate` gặt sớm; `han_tong` không dọn; `poll` 4 lần) → xanh |
| A04 | Quan trọng | Task 6 (dòng 2562): `cham_tham_do` (dòng 3017 — bảng bằng chứng theo loại, đối chứng mục tiêu, lý do cố định), `kiem_am` (dòng 3087 — `kieu` bắt buộc, `ls` cho thư mục) | `test_cham_tham_do.py` (31 ca: curl 7/28 + `000`, 404/500, 127/126, tín hiệu, thiếu đích, Keychain 44/36, chuỗi bí mật ở stdout/stderr): đột biến về cách chấm vòng trước → `18 failed, 13 passed` → xanh |
| A05 | Quan trọng | Task 7 (dòng 3309): `dang_nhap_codex` để `LoiThuHoi` nổi lên (dòng 3559); `bo_sung_3b` → đăng nhập + hạn mức ĐỎ, không gọi `doc_han_muc` (dòng 3628) | `test_dang_nhap_principal.py`: bản trước `2 failed` (`DID NOT RAISE`; `LoiThuHoi` lọt) → xanh; số lần gọi quota = 0 |
| A06 | Quan trọng | Task 8 (dòng 3758): `ket_thuc` một hạn tuyệt đối (`_dung_den` + `chay_trong_han` — dòng 4046, 4190), hẹn `xong` dưới khoá + cờ `_het_hen` | `test_theo_doi_dung.py` (chặn RIÊNG lần đọc cuối; backlog 50 dòng; `xong` gặp ở lần đọc cuối): bản trước `3 failed` → xanh |
| Nhỏ | Nhỏ | Cổng G4 (bảng trên): "tái dùng PID/PGID chỉ chứng minh offline" → ghi là GIỚI HẠN BẰNG CHỨNG; thêm G3 V0.5 | — |

Câu hỏi gộp của review §6 liên quan Plan A: mục 1 → câu hỏi 1 (giữ B, G5 chưa đạt tới khi hai phép kiểm chạy đúng principal); mục 2 → giải bằng thiết kế (khe `sandbox:` không chạy tới khi có cơ chế — D53), không còn là câu hỏi; mục 3 → giải bằng thiết kế (dọn không dựa vào bản ghi; dọn không chứng minh được thì giữ bản ghi, khe dừng); mục 4 → câu hỏi 3 (chỉ là thông số hiệu năng).

## Phản hồi review vòng 2

Nguồn: `.handover/review-codex-plan/REVIEW-CODEX-dot8-vong2.md` §1 (A01, A03 còn mở), §2 (R2-01…R2-04), §3 (mặt ghép), §4.1 (thống nhất A-T1…T4 với B-T6/T8). "Đỏ → xanh thật" = chạy trong worktree `plan/ab-tich-hop` trên `main` `f4fa3a8`, 18/10/2026, PATH chặn host, nhật ký chặn 0 dòng mới; "tái hiện" = đặt mã của bản plan vòng 2 vào cây rồi chạy test mới. Thứ tự đã chạy: A-T1→T8 (`2947 passed`) rồi B-T1→T8 (`3062 passed`); áp lại toàn bộ khối mã hai plan lên bản sạch → `diff -r` khớp từng byte, cả bộ `3062 passed in 266.06s`.

| Mã | Mức | Đã sửa ở đâu | Bằng chứng |
|---|---|---|---|
| R2-01 | Chặn | Task 2: `giu_xac.Goc` — lỗi đăng ký khác ESRCH / không tạo được kqueue → KHÔNG gặt, `hong` (không bao giờ xác nhận thoát); `khoi_chay` không còn `bo_khan`, không tự gửi gì; chỉ ESRCH (gốc đã là xác lúc đăng ký) mới gặt và gặt TRƯỚC mọi lần gửi | `test_dang_ky_loi_khac_esrch_khong_gat_goc_va_khong_tin_hieu_nao_trung_nhom_thay_the` (nhân giả: gặt gốc thì số 4242 cấp NGAY cho việc khác 7000 của tài khoản quản lý; so toàn bộ tín hiệu đã trúng; `os.killpg` thật thay bằng bản ghi): tái hiện trên mã vòng 2 → `assert (7000 not in {7000})`; mã mới xanh, 7000 không bị trúng, `p.returncode` vẫn None. Ca con thật đã là xác + receipt EINVAL / EMFILE: xác còn giữ số, nhóm gốc vẫn bị giết, không xác nhận |
| R2-02 | Chặn | Task 2: hợp đồng sở hữu `tram/kiem/so_huu.py` (thay "H-A03"): `khoi_chay(chu)` bắt buộc, `Nhom` vào `chu` trong `hoan()` trước mọi lối ra; `LoiThuHoi` định nghĩa lại = KHÔNG xác nhận (con có thể còn, `Nhom` còn trong `chu`, cổng/khe đóng, tầng trên dọn theo UID) — không còn hứa "không để lại con"; MỌI người gọi trên HEAD (`quan_sat`, `chay_mot_lenh`, `ChayClaude`, `ChayCodex`, `hoi_app_server`) có khối sở hữu; `ngat.hoan` khôi phục MỌI handler kể cả khi tín hiệu tới giữa lúc khôi phục. Task 4: `chay_gioi_han`, `chay_han_tong` thu hồi `chu` trong `hoan()`, ghi kết quả rồi mới phát lại ngắt lần hai. Plan B: `nguon_archive(chu=)`, `term_thanh_ngat` trên `hoan` này | Đỏ hành vi (thêm module mới, giữ `vong_doi`/người gọi của HEAD): `18 failed, 6 passed` — cả 5 người gọi để con THẬT sống sau Ctrl-C ngay sau Popen (`_song(…) = True`) → `17 passed` + người gọi `101 passed`. Ca: lỗi sau Popen (kqueue), kill bị từ chối, gốc treo (`wait` quá hạn), hậu duệ tách phiên (kênh cục bộ → không xác nhận), ngắt khi khôi phục handler, ngắt lần hai lúc thu hồi (`test_han_tong_ngat_lan_hai…`: đột biến bỏ `hoan()` → dấu bị giữ sai). Trên đường A+B thật: `test_ngat_ab.py` (plan B, SIGTERM THẬT qua hai lớp) |
| R2-03 (phần A) | Quan trọng | Task 4 là bản thân hàm CUỐI duy nhất của `chay_gioi_han`/`chay_han_tong`: hạn trước spawn, `_ong` selector, `_don`, `chu`, `GopKill`, `_don` của V2-1; điểm tiêm `_doc`/`_ghi`/`_bo_chon` cho fault injection tại điểm đọc thật. B-T6 chỉ thêm `stdin=`, B-T8 không sửa `han_tong.py` | `test_han_tinh_truoc_spawn…` (phần hạn còn lại khi bắt đầu đọc ≤ 0 khi spawn chậm); B-T6/T8 áp nguyên văn lên cây A, bản sạch khớp `diff -r` |
| R2-04 | Quan trọng | Task 4: `_don` đóng TỪNG ống (OSError nuốt, không chặn ống sau), thu hồi trong `finally` của cùng khối `hoan()`; chưa xác nhận → `LoiThuHoi` thay lỗi đóng ống/selector/đọc (`from None`); selector `with` ở mọi lối ra | `test_dong_ong_loi…` (×6), `test_doc_hay_bo_chon_loi…` (đọc/`select`/`close` của selector ném, con thật vẫn được thu hồi): tái hiện trên `chay_gioi_han.py` vòng 2 → `OSError: đóng ống: BI-MAT` ×6 (thu hồi bị chặn, "chưa xác nhận" bị che); mã mới xanh |
| A01 | Chặn (vòng 1) | Phần còn mở (gửi sau khi đã gặt gốc) đóng bằng R2-01; phạm vi gửi theo UID (Task 3) không đổi | Task 3 chạy lại trên cây mới: đỏ `15 failed, 21 passed` như bản trước → `96 passed` |
| A03 | Quan trọng (vòng 1) | Đóng bằng R2-02/R2-03/R2-04 | như trên |
| Mới — xung đột với V3-1 đã ghép | Quan trọng | Task 6: `cham_tham_do.co_muc_keychain` gọi `security find-generic-password` riêng → vi phạm test HEAD `test_khong_con_loi_goi_security_khong_han_ngoai_keychain` (V3-1). Nay dùng `tram.keychain.co_muc` (không `-w`, có hạn, chỉ 0/44 là biết; không kiểm được → False = "không kết luận") | Cả bộ ở cây A-T1…T8 trước sửa: `1 failed, 2945 passed` (đúng test đó); sau sửa `2947 passed` |
| A02, A04, A05, A06, A-Nhỏ | — | Không đổi (docstring `van_o_nhom` theo bản sửa của reviewer giữ nguyên) | Task 5–8 chạy lại trên cây mới: đỏ `1 error`/`9 failed`; `1 error`/`11 failed, 1 passed`; `1 error`; `9 failed` — khớp bản trước; xanh `177 passed` (nhóm test của T5–T8) |

Câu hỏi gộp §5 của review: mục 1 → câu hỏi 2 (quy ước dừng thợ trước khi đăng nhập tay — giữ đề xuất); mục 2 → câu hỏi 4 (giữ); mục 3, 4 thuộc plan C/B. Không có câu hỏi mới: các lỗi đúng/sai ở vòng này đều sửa bằng mã + test.

## Ghi chú triển khai

Chưa có — viết sau khi ghép (commit, số test thật trên `main`, chỗ lệch so với plan). Phần này thắng phần thân khi đã có. Spec 3 §7.2 ("pid còn sống → kill cả nhóm") cần cập nhật theo Task 5 (dọn theo UID của khe) khi ghép — việc docs, không thuộc mã của plan.
