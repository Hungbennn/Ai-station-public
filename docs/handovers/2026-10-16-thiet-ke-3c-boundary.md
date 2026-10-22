# Thiết kế 3C-A — ranh giới cưỡng chế giữa các lần kiểm lại (C01, D45)

Ngày 16/10/2026. Phụ lục của [plan 3c](../plans/2026-10-15-lat-3c-principal-kiem-trao-quyen.md). Nguồn: [D45](../quyet-dinh/2026-10-16-chot-sau-review-dot6.md), D22/D40 ([chốt đợt 4](../quyet-dinh/2026-10-15-chot-dot-4.md)), review Codex đợt 6 (C01, R7).

**Trạng thái: thiết kế khả thi có điều kiện. Chưa có bằng chứng OS. S6 vẫn đóng.** Mọi hàng "chỉ chứng minh trên OS" bên dưới phải đạt ở cổng G4 thì mới coi là đóng C01.

## 1. Invariant và phạm vi

Code của commit N chạy dưới `tram-kiem` không được để lại dữ liệu hay tác vụ mà commit N+1, hoặc môi trường kiểm của N+1 (bản chép, `.env.testing`, HOME/TMP của lượt), đọc, sửa hay chạy được.

Kẻ tấn công là mã của commit N, chạy với UID `tram-kiem`, không root. Nó có toàn quyền trong lượt của mình. Ngoài phạm vi C01:

- mã N+1 tự ý đọc kênh do N để lại (thông đồng);
- N tự gửi dữ liệu của chính N ra mạng ngoài;
- leo quyền lên root.

Hai đường làm hỏng lượt N+1 mà C01 phải chặn:

- **(T1)** tác vụ của N còn sống hoặc được lập lịch, rồi chạy trong lúc N+1 chạy;
- **(T2)** dữ liệu N cài ở chỗ mà công cụ trung thực của N+1 đọc tới.

## 2. Kết luận khả thi trong D45

**Khả thi, có điều kiện G4.** Trong macOS không cần root, chỉ có Seatbelt (`sandbox-exec`) chặn được trước việc ghi, IPC và tạo job cho cả một cây tiến trình. Tiến trình áp hồ sơ lên chính nó, và mọi tiến trình con kế thừa. Không cần root, nên D22 và D45 vẫn giữ. Thiết kế có bốn lớp:

1. **Cưỡng chế (3C-D1).** Mọi lệnh dưới `tram-kiem` trong một lượt đều chạy qua `sandbox-exec -f /usr/local/tram/tram-kiem.sb -D LUOT=<bản chép> -D NHA=<bản chép>.nha /usr/bin/env HOME=<NHA> TMPDIR=<NHA>/tmp/`, áp cho cả cơ chế `user` lẫn `sandbox`. Hồ sơ:
   - `(deny default)`;
   - chỉ ghi được `LUOT` và `NHA`, cùng `/dev/null` và `/dev/zero`;
   - **không đọc được gốc chung**, chỉ đọc lại `LUOT`/`NHA` của chính lượt;
   - `(deny job-creation)`;
   - cấm exec `crontab`, `at`, `batch`, `atq`, `atrm`, `launchctl`, `osascript`, `open`, `sudo`, `su`, `login`, `security`, `defaults`;
   - không cho IPC POSIX và SysV, kể cả semaphore có tên (review đối kháng đã tái hiện được semaphore sống qua hai lượt);
   - `mach-lookup` chỉ cho 5 dịch vụ hệ thống, không có Keychain, pasteboard hay cfprefsd;
   - **không mạng**, chỉ cho unix socket trong `LUOT`. DB/Redis dùng chung, dù trên loopback, IP LAN, VM hay máy xa, đều là trạng thái sống qua lượt vì `.env.testing` giống nhau mỗi lượt;
   - không đọc được kho của trạm.
   
   Gốc `thu_muc_kiem` chung **không** ghi được. Vì vậy một tiến trình sót của lượt N, vẫn mang tham số `LUOT` của N, cũng không ghi được vào bản chép của N+1. `NHA` (gồm `NHA/tmp`) do `chep_ban` tạo mới, 0700. `don_ban` xoá cả bản chép lẫn `NHA`.
2. **Thu hồi.** `kill -KILL -1` dưới `tram-kiem`, chạy ngoài hồ sơ của lượt; giết mọi tiến trình cùng UID, kể cả `setsid`.
   - Hiện tại (3C-D4): `giet_tam` chạy qua `boc_lenh`, có `timeout`.
   - Sau P1 và 3C-B (3C-D5): `thu_hoi_theo_uid` kiểm UID thật (3C-B) trước, rồi chạy qua primitive có hạn và thu hồi cây tiến trình (P1). Mã đã có trong `cong_that.py`; chỉ còn chờ dòng nối.
3. **Cổng lượt bền trên đĩa (3C-D2, 3C-D4).**
   - `vao`: cổng phải ở trạng thái `mo` và một lượt quan sát phải sạch. Sau đó ghi `dang-chay`, rồi mới chép bản chép và nhận môi trường kiểm.
   - `ra`: thu hồi, rồi quan sát hai lần cách nhau `cho` giây. Cả hai sạch mới ghi `mo`.
   - Lượt ném lỗi, quan sát thấy tàn dư hoặc quan sát lỗi thì ghi `dong`. Trạm chết giữa lượt thì trạng thái còn `dang-chay`, nghĩa là cổng vẫn đóng.
   - Chỉ Đại ca mở lại được, bằng `tram giao mo-cong-kiem`. Lệnh này cũng phải thu hồi và quan sát sạch.
   - Trong lượt, việc dọn chỉ **giết** (`kill -KILL -1`), **không gỡ lịch**. Bỏ `crontab -r` ngầm của r47 T5 vì nó xoá dấu vết trước khi quan sát.
4. **Quan sát bổ trợ (3C-D3, 3C-D4 và T11 r47).** Không phải ranh giới, chỉ là dây báo:
   - `pgrep -U` và `pgrep -u` do trạm tự chạy;
   - `find` tìm mọi độ sâu trong vùng ghi chung (sửa lỗ `-maxdepth 1` mà Codex chỉ ra);
   - gốc bản chép phải trống;
   - `crontab -l` phải báo "no crontab for", `atq` rỗng, không còn tệp của `tram-kiem` trong `/usr/lib/cron/jobs`;
   - hồ sơ đã cài: chủ root, không ai khác ghi được, có `(deny default)` và có dòng cấm đọc kho trạm hiện tại;
   - tệp môi trường kiểm của mọi dự án: 0600 và thuộc trạm;
   - launchd `user/<uid>`, `gui/<uid>`, `login/<asid>`: bộ đọc 3C-D7 (`tram/giao_viec/launchd_kiem.py`) chỉ cho định dạng đo ở G3; `login/<asid>` không in (là miền của người gọi sudo, không quy được), chỉ đi tiếp khi có bằng chứng G3.9 cho đúng ngữ cảnh vận hành (`ngu_canh_kiem.py`). Chưa có thì I1 **không** bật `giao_viec.bat`.

Đã chạy thử, không phải bằng chứng G4. Chạy dưới user hiện tại trên macOS 15.6.1 (24G90), với hồ sơ sinh ra từ mã 3C-D1, trong thư mục tạm:

- **Bị chặn:** vào thư mục 0777 ngoài `LUOT`, qua symlink, qua hardlink từ ngoài, `rename` ra ngoài, `chmod` tệp ngoài, `mkdir` lượt khác cùng gốc, đọc kho trạm.
- **Lệnh và kết nối bị chặn:** exec `crontab -l`, exec `launchctl`, `shm_open`, `connect` loopback.
- **Vẫn chạy được:** ghi `LUOT` và `NHA`, `bind` localhost, `git init`, sh, python, node, php, npm, `multiprocessing.Lock`.

Bản sau review đối kháng chạy thử thêm:

- **Bị chặn:** đọc `.env.testing` của lượt cũ cùng gốc, liệt kê gốc, `sem_open` (`multiprocessing.Lock`), `bind` localhost, `connect` ra địa chỉ không định tuyến được (Seatbelt chặn trước khi gửi gói).
- **Vẫn chạy được:** ghi HOME/TMPDIR của lượt, `git init`/`status`. Dời tệp từ `LUOT` sang `NHA` vẫn làm được, nhưng `don_ban` xoá cả hai và `goc_rong` bắt mọi thứ còn sót.

Các điều kiện chỉ chứng minh được ở G4 (cổng 4 trong sổ tay chạy thật). Nếu G4 bác (1) hoặc (2), C01 không đóng được trong D45, xem §5.

1. Seatbelt vẫn giữ dưới `sudo -u tram-kiem`, và vẫn giữ qua exec setuid (`crontab`, `at` ghi vào spool bị chặn).
2. `job-creation` chặn được `launchctl submit` và `bootstrap`, kể cả XPC gửi thẳng tới launchd, ở mọi miền mà tiến trình dưới `sudo -u` với tới: `user/<uid>`, `gui/<uid>`, `login/<asid>` của trạm.
3. Danh sách `mach-lookup` đủ cho bộ test thật của dự án HR.
4. `kill -1` thu hồi đủ mọi tiến trình.

## 3. Đánh giá các hướng

| Hướng | Cưỡng chế được gì | Chi phí | Giới hạn | Chọn |
|---|---|---|---|---|
| Seatbelt mỗi lượt (`-D LUOT/NHA`) | Ngăn ghi ngoài allowlist, tạo job, exec công cụ lập lịch, IPC, loopback | Hồ sơ phải bảo trì; test cần dịch vụ Mach hay DB chung sẽ hỏng; công cụ Apple ghi "deprecated" nhưng vẫn có trên 15.6 | Cưỡng chế chỉ chứng minh ở G4; còn kênh dư ở §4 | **Có** (D1) |
| Thu hồi theo UID (`kill -1` dưới `tram-kiem`) | Giết mọi tiến trình cùng UID, kể cả `setsid` | Nhỏ, dùng P1 và 3C-B | Tiến trình setuid (euid root) không giết được thì bị phát hiện và cổng đóng; không gỡ được lịch | **Có** (D5) |
| Cổng bền + quan sát hai lần | Chặn N+1 khi thấy tàn dư hoặc quan sát lỗi | Nhỏ; Đại ca phải mở tay khi cổng đóng | Chỉ thấy những gì quan sát được | **Có** (D2–D4) |
| Pool UID (2 user luân phiên) | Thêm phân tách DAC cho kênh mà Seatbelt sót | Đổi hợp đồng cài đặt: 2 user, sudoers nhiều runas, sổ R2; trái G13 "một user" | Tự nó không chặn ghi vào vùng chung hay tạo job; D45 vẫn bắt chặn lượt sau khi dọn không rõ | Chưa. Phương án dự phòng A1 |
| `find / -user` có giới hạn | Không cưỡng chế, chỉ quét | Vài phút cho cả ổ, mù ở thư mục không đọc được | D45 nói rõ quét không đủ | Không. Chỉ giữ `find` sâu trên vùng ghi chung làm dây báo |
| Mốc nền launchd | Không cưỡng chế | Đại ca chụp mốc | D45: chỉ hỗ trợ quan sát | Giữ ở T11 |

## 4. Bảng threat → control

Viết tắt:

- **SB** = hồ sơ Seatbelt của lượt (D1). **Cổng** = D2/D4. **Q** = quan sát.
- **"(chạy thử)"** = đã thử với user hiện tại, chưa qua `sudo -u`.

| # | Nơi ghi hoặc nguồn thực thi | Cưỡng chế (ngăn ghi hoặc ngăn chạy) | Kiểm offline | Phát hiện thất bại | Chỉ chứng minh trên OS (G4) |
|---|---|---|---|---|---|
| 1 | Bản chép `LUOT` của lượt | Cho ghi; tên mới mỗi lượt; lượt khác không ghi được vì `LUOT` khác | `test_cam_mac_dinh_chi_ghi_va_doc_lai_ban_chep_va_nha_cua_luot` | `don_ban` + `lexists` (T3); lỗi thì cổng đóng | Tham số `-D` có hiệu lực dưới `sudo -u` |
| 2 | Gốc `thu_muc_kiem` (anh em của bản chép) | SB không cho ghi (gốc không có trong hồ sơ) | Test D1: gốc không có trong hồ sơ; chạy thử `mkdir` lượt khác bị chặn | T11 kiểm gốc rỗng | Như hàng 1 |
| 3 | `/private/tmp`, `/private/var/tmp`, `/Users/Shared`, `/Library/Caches` (1777) | SB cấm ghi (deny default) | Hồ sơ D1; chạy thử | Q `tep_ngoai` mọi độ sâu | SB dưới `sudo -u` |
| 4 | Tệp con trong thư mục cha 0777 hoặc ACL ghi của user khác, ở bất kỳ đâu (ca Codex) | SB cấm ghi theo đường dẫn, không phụ thuộc chủ; chặn cả hardlink, symlink, `rename` ra ngoài | `test_tep_ngoai_thay_tep_sau_trong_thu_muc_cha_khac_owner_hoac_find_loi`, `test_luot_n_de_tan_du_thi_luot_n1_khong_chep_khong_nhan_moi_truong`; chạy thử | Q sâu chỉ trong vùng ghi chung; ngoài vùng đó chỉ có cưỡng chế | SB dưới `sudo -u` |
| 5 | Thư mục ghi được qua nhóm `staff` hoặc ACL `everyone` (Homebrew, phần mềm khác) | SB cấm ghi | Hồ sơ D1 | Không có Q (ghi rõ) | G3: một lần liệt kê `find` các thư mục `staff`/`everyone` ghi được, làm bằng chứng phạm vi |
| 6 | `DARWIN_USER_DIR/TEMP/CACHE` (`/var/folders`, 0700 của `tram-kiem`) | SB cấm ghi; không cho `mach-lookup` dirhelper | Hồ sơ D1 | T11: `getconf` + xoá dưới `tram-kiem` (đã có sửa Q01 mã lỗi) | SB; dirhelper |
| 7 | Nhà tài khoản `/var/empty` | DAC root + SB | — | T11: `id -P`, `stat`, ACL | `sysadminctl -home /var/empty` không đổi chủ |
| 8 | HOME/TMP của lượt (`NHA`) | Cho ghi; xoá cùng bản chép | T11 `boc_nha` | T11 | — |
| 9 | `~/Library`, `defaults`, cfprefsd | HOME `/var/empty`; `user-preference-write` bị deny default; không `mach-lookup` cfprefsd; cấm exec `defaults` | Test D1 | Bộ đệm cfprefsd theo user là tiến trình, bị thu hồi | SB, cfprefsd |
| 10 | Keychain của user | Không có `SecurityServer` trong `MACH_CHO`; cấm exec `security` | Test D1 | — | SB |
| 11 | Pasteboard, Apple Events, `open`, `lsopen`, `osascript` | `mach-lookup`, `appleevent-send`, `lsopen` bị deny default; cấm exec | Test D1 | — | SB |
| 12 | POSIX shm | Không cho `ipc-posix-shm` | Test D1; chạy thử `shm_open` EPERM | — | SB dưới `sudo -u` |
| 13 | SysV IPC (`shmget`/`semget`/`msgget`) | Deny default | Hồ sơ D1 | Chưa có Q. Bổ sung `ipcs -a` của trạm sau G3 | Chưa chạy thử. G4 |
| 14 | POSIX semaphore có tên (review tái hiện được kênh sống qua hai lượt) | **Cấm** (deny default; hồ sơ không có `ipc-`) | `test_khong_tao_job_khong_chay_cong_cu_lap_lich_khong_ipc`; chạy thử `multiprocessing.Lock` EPERM | — | SB. **Hệ quả:** test Python dùng `multiprocessing` sẽ fail |
| 15 | notifyd state (`notify_set_state`) | `notification_center` được cho (libSystem cần) | — | — | **Kênh dư** 64 bit dùng chung toàn máy (thông đồng). G4 đo phạm vi |
| 16 | Unix socket | `bind` chỉ trong `LUOT` (file-write); `connect` chỉ socket trong `LUOT` | Test D1 | Tiến trình giữ socket bị thu hồi | SB |
| 17 | Dịch vụ dùng chung qua mạng: MySQL/Redis/tram-api trên loopback, IP LAN, VM (Docker/OrbStack) hay máy xa; MySQL EVENT/trigger là nguồn thực thi | **Không mạng** (chỉ unix socket trong `LUOT`) | `test_khong_mang_chi_unix_socket_trong_luot`; chạy thử `bind`/`connect` EPERM | — | SB. **Hệ quả:** test cần DB/mạng không chạy được, xem Q-A |
| 18 | cron (`crontab` setuid → `/usr/lib/cron/tabs`) | Cấm exec + cấm ghi; SB kế thừa qua setuid | Test D1; chạy thử exec bị chặn | T11 `crontab -l`; lỗi thì cổng đóng | Kế thừa SB qua setuid |
| 19 | at/batch (`/usr/lib/cron/jobs`) | Như hàng 18 | Như hàng 18 | T11 `find` + `atq` | Như hàng 18 |
| 20 | launchd `user/<uid>` (bootstrap, submit, XPC trực tiếp) | `(deny job-creation)` + cấm exec `launchctl` | Test D1; chạy thử exec bị chặn; `test_launchd_kiem.py` | 3C-D7: miền riêng của tram-kiem — dịch vụ ngoài mốc (theo bản macOS), khối trạng thái có dòng, thiếu khối bắt buộc → cổng đóng | **`job-creation` với XPC trực tiếp. Điều kiện chính** |
| 21 | launchd `gui/<uid>` | Như hàng 20 | Như hàng 20 | 3C-D7: chỉ mã 125 "Domain does not support specified action" (đo G3) là sạch; miền tồn tại → cổng đóng | Như hàng 20 |
| 22 | launchd `login/<asid>` (sudo giữ asid của trạm) | Như hàng 20 | Như hàng 20 | **Không có Q (không quy được):** G3 đo asid là phiên Aqua của người vận hành (uid 501), miền không ghi uid từng mục; 3C-D7 không in, chỉ đi tiếp khi `BANG_CHUNG_LOGIN` có đúng ngữ cảnh hiện hành (bản macOS, máy, UID kiểm, UID trạm, loại phiên) | Như hàng 20 + G3.9 (đối chứng dương ngoài hồ sơ, `docs/handovers/g3-bo-sung.sh`). Điều kiện chính |
| 23 | Tiến trình nền (nohup, double-fork, setsid, daemon) | Thu hồi `kill -1` theo UID (D5) | `test_thu_hoi_theo_uid_*` | Q `tien_trinh` (UID thực và hiệu lực) ở `ra` hai lần và ở `vao` lượt sau | `kill -1` đủ |
| 24 | Tiến trình setuid (ruid `tram-kiem`, euid khác) không giết được | Cấm exec `sudo`, `su`, `login`; setuid khác (vd `traceroute`) chưa cấm | — | `pgrep -U` thấy, cổng đóng (fail-closed, mất khả năng chạy tiếp) | G4: danh sách setuid trên máy B |
| 25 | Tái sinh trễ | Như hàng 20 và 23 | `test_tai_sinh_tre_giua_hai_lan_quan_sat`, `test_tai_sinh_sau_khi_mo_bi_bat_luc_vao_luot_sau` | Quan sát hai lần + quan sát ở `vao` | Thời gian `cho` thật |
| 26 | ACL, chmod, chown, xattr, flock trên tệp ngoài | `file-write*` (mode, owner, xattr) bị cấm; flock giữ trên tệp đọc được chỉ sống cùng tiến trình | Chạy thử chmod EPERM | Thu hồi giải phóng | SB |
| 27 | Hardlink hoặc rename ra ngoài | Không cho `file-link`; rename bị chặn | Chạy thử | — | SB |
| 28 | `launchctl setenv`, biến môi trường cho lượt sau | Cấm exec `launchctl`; env của N+1 do trạm dựng từ `env_goc` | Test D1 | — | Như hàng 20 |
| 29 | Lượt lỗi giữa chừng, trạm chết | Cổng `dang-chay`/`dong` bền, ghi bằng fsync + `replace` | `test_luot_loi_giua_chung_thi_dong_cong_va_chan_luot_sau`, `test_crash_giua_luot_thi_lan_khoi_dong_sau_van_dong` | — | — |
| 30 | Quan sát lỗi (pgrep/find mã lạ, hết hạn, định dạng lạ) | Cổng đóng | `test_quan_sat_thay_hoac_loi_khi_ra_thi_dong_va_chan_luot_sau` (4 ca) | — | Mức ồn `find` trong `/private/tmp` (mất khả năng chạy tiếp, không lọt) |
| 31 | `periodic`, emond, login hook, kext, nvram | Cần root; `nvram-set` bị deny default | — | — | — |
| 32 | `NHA` và bản chép bị dời trong gốc (review: `mv LUOT NHA/saved`) | `don_ban` xoá cả `wt` lẫn `wt.nha`; SB cấm đọc gốc ngoài lượt mình | `test_goc_rong_thay_ban_chep_hoac_nha_con_sot`; `test_cam_mac_dinh_chi_ghi_va_doc_lai_ban_chep_va_nha_cua_luot` | `goc_rong` ở `vao`, `ra`, `mo_lai` | SB |
| 33 | Tệp nguồn môi trường kiểm của dự án khác (đường dẫn tuyệt đối ngoài `~/.tram`) | DAC: phải 0600 và thuộc trạm | `test_env_kin_doi_0600_cua_tram` | `env_kin`, sai thì cổng đóng | — |
| 34 | Hồ sơ cài sai hoặc bị thay, `TRAM_HOME` đổi | Hồ sơ root 0644 | `test_ho_so_cai_*` | `ho_so_cai`, sai thì cổng đóng | Cài cho cả hai cơ chế: sửa r47 T6 (task 3C-D6, chưa có mã) |
| 35 | `tram giao kiem` chạy probe dưới `tram-kiem` ngoài khoá và ngoài cổng | — | — | Probe để lại tiến trình làm cổng đóng (không lọt, nhưng cổng đóng giả) | 3C-D6: chạy dưới `giu_khoa`, qua `boc_luot` của một lượt tạm, thêm probe "ghi ngoài LUOT phải bị từ chối". Sửa r47 T5/T7, chưa có mã |
| 36 | `tom_tat` (stdout của N) đi vào sự kiện và beads, rồi vào ngữ cảnh tác tử sau | Ngoài ranh giới OS | — | — | **Ngoài C01:** là kênh prompt injection; QC đọc. Ghi để review |

## 5. Lựa chọn thay kiến trúc cần Đại ca chốt (chỉ khi G4 bác điều kiện 1 hoặc 2)

| Phương án | Làm gì | Tác động | Đánh giá |
|---|---|---|---|
| **A1 — pool user dùng một lần, bảo trì root do Đại ca** | Lúc cài, tạo K user kiểm (vd 8), cùng `/var/empty` và sudoers runas từng user. Mỗi lượt lấy một user **chưa dùng**; user đã dùng bị cách ly vĩnh viễn. Hết user thì cổng đóng; Đại ca chạy lệnh bảo trì có `sudo` (xoá user cũ + tạo lại, có sổ R2) | Vẫn không root lúc chạy (D45). Lượt N+1 luôn khác UID với mọi lượt trước, nên kênh của UID cũ không chạm được N+1 nhờ DAC. Đổi G13 (một user) và hợp đồng cài đặt | **Khuyến nghị nếu G4 bác.** Hợp D22/D45; chi phí là thao tác định kỳ của Đại ca |
| A2 — helper root giữa các lượt | Daemon root chỉ làm `launchctl bootout` cả miền, xoá spool cron/at và giết theo UID | Trái D22/D45 (root lúc chạy); thêm bề mặt root | Không khuyến nghị |
| A3 — VM mỗi lượt (Virtualization.framework, Tart/UTM) | Lượt kiểm chạy trong VM khôi phục từ snapshot | Cách ly mạnh nhất; tốn RAM, ổ đĩa, thời gian dựng; giấy phép macOS cho 2 VM; đổi cả kiến trúc D22 | Chỉ khi Đại ca muốn mức cách ly cao nhất |

## 6. Câu hỏi cần Đại ca biết hoặc chốt (không chọn thay)

- **Q-A, không mạng, không semaphore.** Lệnh kiểm không có mạng (kể cả loopback) và không có POSIX semaphore. Test cần MySQL/Redis dùng chung, cần tải gói, hoặc dùng `multiprocessing` của Python sẽ không chạy được trong kiểm lại. Đề xuất:
  - dự án dùng SQLite (tệp trong `LUOT` hoặc `:memory:`) cho `.env.testing`;
  - phụ thuộc đã có sẵn trong commit hoặc bước chuẩn bị riêng.
  
  Mở mạng tới DB dùng chung là trái invariant (dữ liệu, trigger, EVENT sống qua lượt), nên Em không đề xuất. Nếu cần DB thật thì phương án là dựng DB riêng trong `LUOT` mỗi lượt; đó là task mới, cần Đại ca chốt.
- **Q-B, cổng đóng thì dừng hẳn.** Mỗi lần cổng đóng, toàn bộ kiểm lại dừng tới khi Đại ca chạy `tram giao mo-cong-kiem`. Đây là đúng D45, nhưng có thể làm nhịp việc chậm.
- **Q-C, chính sách R7 chặt hơn.** Các loại repo sau trước đây chạy với "cây khác nguồn"; nay bị từ chối kèm escalation `cay-khac-nguon`: blob CRLF dưới thuộc tính text, `ident` đã mở, submodule, trùng tên hoa-thường, tệp `._*`, kho sha256, kho kiểm có `filter.*`. Muốn hỗ trợ lại thì phải trình phương án riêng.

## 7. Giả định hợp đồng của nhánh khác

- **P1** cung cấp `chay(argv, *, principal, han, ...)`: chạy argv dưới principal, có hạn cuối, thu hồi cây tiến trình, quá hạn thì ném.
- **3C-B** cung cấp `kiem_uid(ten)`: probe không tác dụng phụ dưới đúng wrapper, sai UID hoặc không đọc được thì ném.
- 3C-D5 chỉ nhận hai hàm này qua tham số. Khi ghép P1 và 3C-B, `noi_that.dung_bo_that` truyền `thu_hoi=partial(thu_hoi_theo_uid, pk.ten, kiem_uid=<3C-B>, chay=<P1>)` vào `dung_cong`. Dòng này viết sau khi biết tên module thật; không đoán trước.
- C02 vẫn mở trong `chay_mot_lenh`: `kill_nhom` bỏ qua mã thoát, `_ket_thuc` gọi `p.wait()` không có hạn. Hậu quả: treo, giữ khoá, cổng kẹt ở `dang-chay`. Đây là fail-closed, không lọt; phần sửa thuộc P1 và 3C-B.
