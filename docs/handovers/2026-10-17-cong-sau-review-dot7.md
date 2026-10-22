# Cổng sau review đợt 7 — 17/10/2026

Đây là cập nhật trạng thái và hướng dẫn an toàn, **không cấp quyền vận hành**. Không chạy mã/tests/mạng/API trong review. Snapshot được bàn giao là `3fee383`; không có `.git` để chứng nhận ancestry/HEAD. Số 2697/101 và kết quả guard là lời bàn giao, chưa đo lại. D1–D53 và mockup giữ nguyên.

Ưu tiên phụ lục này đối với readiness/lệnh thử/cleanup trong plan 3c Task 9 và sổ tay cũ. Xem review `.handover/review-codex-dot7/REVIEW-CODEX.md` (git bỏ qua `.handover/`) và [V2](../plans/2026-10-17-lat-v2-va-sau-review-dot7.md). Không sửa các tick lịch sử thành bằng chứng mới.

| Cổng | Trạng thái hiện hành | Việc cần trước khi qua |
|---|---|---|
| G0 | Review snapshot xong; live chưa xác minh | Source digest, HEAD/dirty và mapping trên checkout đích khi triển khai |
| G1/G2 | Còn blockers | V2-0/5/6 cần hoàn thiện thiết kế; mọi thay đổi phải RED/GREEN cô lập và review |
| G3 | CHƯA CHẠY | Chỉ xin phép đo thủ công giới hạn phục vụ D7, scope/receipt/watchdog rõ; không chạy harness/lịch khi code chưa đạt |
| G4 | BỊ CHẶN | V2-0/1/3/4/5/6a/7, 3C-D7; đầy đủ matrix OS bên dưới |
| G5 | BỊ CHẶN | V2-0/6b, bs-863.14/.17; principal/env/cleanup/heartbeat đúng account thử |
| G6 | BỊ CHẶN | V2-2/7, fixture bd thật trên kho bỏ được, TLS/H5/auth/recovery; không xóa ledger |
| G7 | BỊ CHẶN | Mọi gate liên quan, .15/.16, D1/S7; Đại ca cho phép riêng |

HR `bat_ghi: false`, giao việc tắt. 1a-2/V1 có thể chuẩn bị smoke/browser riêng, không mở G4–G7. Các thao tác account/sudoers/scheduler/skill/API/Beads và tests host đều chưa được thực hiện.

## Trước phép thử OS

- Ghi OS/build, source/profile/config digest, principal UID/RUID; kiểm UID số, khác 0 và khác người vận hành. Chứng minh principal chuyên dụng, không dùng chung workload.
- Receipt nằm ngoài sandbox, mode 0600, chứa run-id, đường tuyệt đối W/W.nha/marker, danh tính launcher/con (PID cùng thời điểm sinh từ adapter đã review), các lịch/label/at job đã tạo và baseline. Không chứa token. Không đoán PID bằng pgrep mới nhất.
- Mỗi bước có hạn và watchdog ngoài đã kiểm cleanup. Không chỉ dùng đồng hồ nhắc Ctrl-C. Nếu công cụ watchdog chưa có hoặc ownership chưa chứng minh thì chưa chạy bước tạo process/lịch.
- Bằng chứng procinfo theo D52 do Đại ca tự gõ đúng PID đã xác minh. Không tự đọc lịch hay xin sudo trong phiên review. Che đường nhạy cảm/token trước chia sẻ transcript; không yêu cầu gửi nguyên mọi file home.
- Biến shell dùng hàm `TK() { /usr/bin/sudo -n -H -u tram-kiem "$@"; }`, không dùng chuỗi command qua `$TK` trong zsh. Các placeholder phải thay bằng receipt đã kiểm, không copy nguyên bảng.

## Matrix bắt buộc cho G4

| Boundary | Proof cần, không suy ra từ việc command thất bại |
|---|---|
| Ghi ngoài lượt/liên lượt | Probe W hợp lệ thành công; ngoài W, home trạm, lượt khác bị deny; W/NHA đúng profile parameters |
| Đọc bí mật | Mọi dự án kể cả false nằm trong inventory; env mode/owner; kho trạm bị chặn, không log nội dung |
| IPC/mạng | Unix socket trong lượt dùng được nếu yêu cầu; socket ngoài lượt, TCP/UDP/loopback bị deny đúng D48; không traffic ra Internet |
| Mach/job-creation | Đo allowlist cần thiết và lookup ngoài whitelist; XPC/job-creation trực tiếp, không chỉ launchctl/crontab bị deny exec |
| Schedules | Mỗi cron/at/submit/launchd có started/completed/rc và reason OS; missing tool/127/timeout/không chạy là CHƯA ĐẠT. Positive control ngoài sandbox chỉ tài khoản thử riêng trong scope được duyệt |
| Cleanup | Detached grandchild, fast reparent, tái dùng PID/PGID, stdin producer, Ctrl-C/SIGTERM; zero wrong signal; không còn UID/RUID/tài nguyên lịch sau hai lần quan sát |
| Fail closed | Quan sát lỗi/không hiểu format/cleanup lỗi/profile drift giữ đóng, N+1 không chạy; chỉ Đại ca mở theo D49 |
| Production HR flow | Đúng archive/tree equality/repo một commit/env injection/principal như runtime; fixture testing không mạng; probe archive+tar cũ chỉ đo compatibility, không chứng minh R7 |

Không xanh dựa vào vắng marker. Chứng cứ OS trên đúng version; không tự nới profile khi EPERM. Profile cần exact expected content từ cài đặt/config tin cậy; substring không attestation. 3C-D7 chỉ parse fixture đã đo, dạng lạ đóng.

## Thu hồi và đường lui

1. Ngăn lượt mới; giữ lock/dấu/cổng đóng. Dừng launcher và con harness theo receipt đã revalidate, không chỉ nhìn tên process. Nếu identity không rõ, dừng để Đại ca đối soát; không signal bừa.
2. Dọn scheduler đúng principal/run/label/job đã ghi, tránh tái sinh. Không `crontab -r` toàn bộ nếu chưa chứng minh tài khoản dành riêng và baseline rỗng. Không sửa lịch người vận hành.
3. Thu hồi process của principal chuyên dụng trong phạm vi đã duyệt, với deadline và kiểm UID **và RUID**. Việc kill toàn UID chỉ hợp lệ sau kiểm dedicated ownership, không tái sử dụng cho worker dùng chung.
4. Quan sát lại schedules/process; lỗi quan sát không phải rỗng. Khi có tái sinh, giữ đóng và quay lại xử lý nguồn lịch, không chạy lượt kế.
5. Chỉ khi sạch mới dọn đúng W/W.nha/marker của receipt; kiểm parent, prefix, symlink và ownership. Không glob `g3-*` hay `tram-nghiem-thu-dau-*`. Không xóa evidence/gate trước cleanup.
6. Hai lần quan sát sạch theo contract, ghi kết quả và các resource còn lại. Không tự xóa dấu/mở cổng. Đại ca mở theo D49 sau đối soát. Gỡ account/sudoers là bước riêng, không thay thế dọn lịch; chưa sạch thì không tuyên bố rollback thành công.

G5 phải giữ token ngoài logs/argv, dùng sentinel giả. Lỗi quota thường giữ heartbeat; `LoiThuHoi` phải dừng khe, không che thành quota unknown. G6 giữ bản sao skill cũ nếu đã cài, rollback đúng receipt thay vì chuyển bừa thư mục dùng chung vào Trash. Không cố tạo crash ở kho thật. Nếu duplicate feature, đóng gate và bảo toàn evidence trước khi Đại ca quyết xử lý bead; xóa bead thừa không làm nghiệm thu thành đạt.

## V2c — G3.0 hồ sơ có manifest, G4 ma trận probe

#### G3.0 — sau khi cài lại bằng `tram chu cai-dat-tho` (Đại ca gõ `dong-y`, Terminal.app)

1. Đại ca ghi (chỉ đọc, không sudo): `ls -ld / /usr /usr/local /usr/local/tram`, `stat -f '%Su:%Sg %Lp %HT' /usr/local/tram/tram-kiem.sb /usr/local/tram/tram-kiem.sb.json`, `shasum -a 256 /usr/local/tram/tram-kiem.sb /usr/local/tram/tram-kiem.sb.json`. Đạt: mọi dòng `root:wheel`, thư mục 755, file 644 `Regular File`. Máy viết plan (macOS 15.6.1, 24G90) đo 17/10: `/`, `/usr`, `/usr/local` đều `root wheel drwxr-xr-x`; **máy B chưa đo** — nếu `/usr/local` không phải root (ví dụ Homebrew cũ trên Intel đổi chủ) thì `doc_tep_root` đóng cổng: dừng, hỏi Đại ca (xem Câu hỏi 2), không tự nới.
2. Ghi vào biên bản: `phien_ban` trong manifest (= `PHIEN_BAN_HO_SO` của mã đã ghép), hai digest, commit của mã. Không ghi nội dung hồ sơ hay đường dẫn có tên người ngoài phạm vi.
3. `tram giao kiem` (Đại ca chạy): mục cổng không báo `LoiBanChep` về hồ sơ/manifest. Đổi `TRAM_HOME`/`giao_viec.thu_muc_kiem` sau đó → phải đỏ cho tới khi cài lại (kiểm một lần, ghi kết quả).

#### G4 — ma trận chứng cứ OS (V2-4 phần OS; phụ lục đợt 7 mục "Matrix bắt buộc")

Điều kiện trước: T1–T8 đã ghép, G3 đạt, V2-0/V2-1/V2-3 xong theo phụ lục; receipt + watchdog như phụ lục. Harness OS là **một script riêng phải soạn thành plan TDD và Codex review SAU G3** (cần định dạng launchd đo ở G3) — plan này chỉ chốt yêu cầu, không giao thực thi từ bảng dưới. Mọi probe chạy dưới `tram-kiem` trong một lượt thật (`boc_luot`, `-D LUOT/NHA`), mỗi probe có: dấu `probe:<n>:bat-dau/ket` và MỘT mã `ly-do` hữu hạn (giao thức `boc_probe` của Task 1 — không thêm kênh in đầu ra), hạn ≤ 20 s, receipt dọn đúng tài nguyên vừa tạo; hàng loại A/C thêm **đối chứng dương** (cùng probe, cùng tài khoản thử, KHÔNG có hồ sơ — chứng minh probe thật sự làm được việc đó).

**Ba loại tiêu chí — KHÔNG gộp trong một hàng (B04):**

- **A — phải bị chặn** (lịch cron/at/submit/launchd, job-creation, IPC, mạng loopback, Mach): ĐẠT khi probe dưới hồ sơ có `ket` ≠ 0 **và** Đại ca xác nhận từ chối của sandbox trong log Sandbox (mã `ly-do` `eperm` chỉ là gợi ý) **và** đối chứng dương có `ket` = 0; riêng lịch thêm: không có dấu `dau/<nguồn>` sau `cho` ≥ 240 s ở hai lần quan sát. Thiếu một điều = CHƯA ĐẠT; thiếu công cụ (127), quá hạn, không có dấu = CHƯA ĐẠT.
- **B — được phép nhưng phải thu hồi** (tách phiên: fork + `setsid`, cha thoát sớm; Unix socket trong `LUOT`): probe ĐƯỢC thành công — `ket` = 0 là bình thường, không phải "lọt". ĐẠT khi `ra()` xác nhận thu hồi (cổng không đóng vì `LoiThuHoi`), sau hai lần quan sát không còn tiến trình nào có UID **hoặc** RUID `tram-kiem`, và không có dấu `dau/setsid` sau ≥ 240 s. `ket` ≠ 0 (không fork được) = **CHƯA ĐO** — chưa chứng minh được thu hồi, không phải đạt. Biến thể bắt buộc: con/cháu tách phiên; cha thoát sớm; TERM bị bỏ qua (`SIG_IGN` — phải tới SIGKILL); ngắt lần hai lúc dọn (cổng giữ đóng, Task 8). Thu hồi toàn UID chỉ áp cho `tram-kiem` dành riêng, không bao giờ cho tài khoản dùng chung.
- **C — mạng ra ngoài máy:** chỉ thử tới **endpoint do Đại ca chỉ định và cho phép riêng** (một máy của Đại ca trong mạng nội bộ/Tailscale, có listener ghi nhận kết nối; một cổng, một lần, ghi giờ bắt đầu/kết thúc). Không dùng địa chỉ Internet tuỳ ý (phụ lục cổng: không traffic ra Internet). ĐẠT theo tiêu chí A với đối chứng dương tới đúng endpoint đó. Chưa có endpoint được duyệt → hàng ghi **CHƯA ĐO** và G4 chưa đạt hàng này; không thay bằng loopback (Câu hỏi 4).

| Nguồn | Loại | Probe dưới hồ sơ | Đối chứng dương (ngoài hồ sơ, tài khoản thử) | Dọn theo receipt |
|---|---|---|---|---|
| cron / at / submit / launchd | A | `kich_ban_tai_sinh` (Task 2) — mỗi nguồn một khối `boc_probe` | Không chạy cron/at thật dưới tài khoản người vận hành; đối chứng chỉ dưới `tram-kiem` khi Đại ca cho phép riêng | nhãn `vn.tram.nghiem-thu.*`, đúng UID |
| setsid / fork, cha thoát sớm, TERM bị bỏ qua | B | khối `setsid` của `kich_ban_tai_sinh` + biến thể `SIG_IGN` | — (được phép; bằng chứng là thu hồi + quan sát) | theo phụ lục mục "Thu hồi và đường lui"; kill toàn UID chỉ với `tram-kiem` dành riêng |
| job-creation trực tiếp (không qua đường dẫn `/bin/launchctl` bị cấm exec) | A | chép `/bin/launchctl` vào `LUOT` rồi `submit -l vn.tram.nghiem-thu.chep` — chỉ `(deny job-creation)` chặn được | cùng bản chép, ngoài hồ sơ | `launchctl remove vn.tram.nghiem-thu.chep` đúng domain |
| POSIX semaphore / shared memory | A | `python3 -c` `multiprocessing.shared_memory.SharedMemory(create=True, size=1, name=…)` và `sem_open` (qua `multiprocessing.synchronize`) | cùng lệnh ngoài hồ sơ | `unlink()` đúng tên ghi trong receipt |
| SysV IPC | A | `perl -MIPC::SysV` `msgget/shmget/semget(IPC_PRIVATE)` | cùng lệnh ngoài hồ sơ | `ipcrm` đúng id ghi trong receipt |
| TCP/UDP loopback | A | kết nối `127.0.0.1:<cổng listener Đại ca mở riêng>`, gửi UDP loopback | cùng lệnh ngoài hồ sơ | tắt listener |
| Mạng ra ngoài máy | C | TCP connect (không gửi dữ liệu) tới endpoint Đại ca chỉ định | cùng lệnh ngoài hồ sơ, cùng endpoint | tắt listener; ghi endpoint + giờ vào biên bản |
| Unix socket | B trong `LUOT` / A ngoài `LUOT` | trong `LUOT`: phải được; ngoài `LUOT`: phải bị chặn | ngoài `LUOT`: cùng lệnh ngoài hồ sơ | xoá socket |
| Mach lookup ngoài allowlist | A | chương trình gọi dịch vụ ngoài `MACH_CHO` (ví dụ `pbpaste` — pasteboard) | cùng lệnh ngoài hồ sơ | — |
| Nguồn chạy sau cleanup | (điều kiện của A lịch và B) | dấu `dau/<nguồn>` sau `cho` ≥ 240 s, hai lần quan sát | — | theo phụ lục mục "Thu hồi và đường lui" |

**Biên bản sạch (B01, INV-001).** Mỗi hàng ghi: nguồn, loại (A/B/C), `ket`, mã `ly-do` (một khoá của `LY_DO`), TÊN thao tác sandbox bị từ chối mà Đại ca đọc thấy trong log (ví dụ `job-creation`, `network-outbound` — chỉ tên thao tác), `ket` của đối chứng dương, kết luận ĐẠT / CHƯA ĐẠT / CHƯA ĐO do Đại ca viết. KHÔNG dán stdout/stderr thô, nguyên dòng log, argv, biến môi trường hay đường dẫn ngoài phạm vi vào biên bản/transcript. Thấy dữ liệu nhạy cảm khi xem log thì ghi "đã thấy dữ liệu nhạy cảm — không chép" và dừng hàng đó. Không tự nới hồ sơ khi gặp EPERM.
