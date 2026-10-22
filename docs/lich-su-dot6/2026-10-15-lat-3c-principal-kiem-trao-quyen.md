# Lát 3c — Principal kiểm hợp nhất + bản chép do `tram-kiem` sở hữu (D22) + hoàn tác có sổ (R2) — Implementation Plan

> **Review Codex đợt 6 — CHƯA sẵn sàng code trọn lát / S6 ĐÓNG.** Q01/Q02 đợt 5 có sửa đúng hướng ở journal và tài nguyên nhà. C01 chưa đóng: r47 vẫn cho tồn tại dữ liệu/lịch ngoài miền được quét; hai lượt sạch không phải cách ly giữa hai lần chạy. Harness Q03 gọi đúng đường nhưng timeout daemon-thread không đảm bảo dọn và guard chưa xác minh UID thật. Xem phụ lục review cuối file. Q01 mới đợt 6 (mã lỗi dọn tệp) được sửa trực tiếp trong T11 kèm 3 regression; tổng dự kiến mới N₀+128, chưa chạy. Sáu câu hỏi r47 vẫn là câu hỏi, không có quyết định mới của Đại ca.


> **Bản sửa 16/10/2026 theo D22 (không root) và R2 (journal hoàn tác) — CHỜ CODEX REVIEW LẠI** (D22: "Plan 3c phải viết lại R1 theo hướng này và gửi Codex review lại"). Task 2, Task 4, Task R3 **đã code và ghép** (D21; `main` `d223406`, `2d21bd7`, `bedcea6`; tên `lai` đã chốt D34) — giữ nguyên văn để tham chiếu, không giao lại. Task 1, 3, 5, 6, 7, 8 viết mới: mã/test trong plan đã chạy thật trên bản sao `main 4a907cc` (xem "Ghi chú kiểm plan (16/10)"). Bản helper root cũ (R1) **bị D22 thay hẳn** — không còn trong plan. Quyết định D1–D39 giữ nguyên; hợp đồng chưa chốt không tự trở thành quyết định.

> **Bổ sung 16/10/2026 theo D40** ("3c: đồng ý mọi đề xuất … Riêng cây kiểm không có `.git` chọn (b)"): các mục 2, 3, 4, 5, 7, 8, 9, 11, 12, 13, 14 của "Chờ Đại ca chốt" **ĐÃ CHỐT D40** theo đề xuất; cây kiểm chọn (b) — thêm **Task 10** (đợt 2): sau `tar -x`, `tram-kiem` tự dựng repo git một commit trong bản chép (`env -i`, không cấu hình global/system/template, hook tắt). Mã/test Task 10 và toàn bộ T1/T3/T5–T8 đã chạy lại trên bản sao `main 66058f9` (xem "Ghi chú kiểm plan (16/10, bản D40)").

> **Review Codex đợt 5 (16/10/2026) → bản r47 (16/10/2026).** R4/R5 (Q01/Q02) đã sửa trong Task 6/8: mã + regression đầy đủ. R6/C01 có thiết kế, mã, regression ở **Task 11** (vòng đời cách ly `tram-kiem`); Q03 có harness ở **Task 12** (`tram giao nghiem-thu-kiem`, `tram giao chup-nen-lich`). R7 phần cây CRLF/encoding CHƯA làm. Toàn bộ mã/test đã chạy thử trên bản sao `main 793facb` (N₀ = 2100) — xem "Ghi chú kiểm plan (r47)". Gate S6 vẫn đóng tới khi Task 9 bước 3b, 5, 6 đạt trên máy B; kẽ hở còn lại ghi ở rủi ro (a). Mọi quyết định D1–D41 giữ nguyên (D22: không helper root lúc chạy, sudo chỉ sang `tram-kiem`; D40: user riêng, sudoers `ALL` dưới `tram-kiem`, repo một commit, khoá một lần, từ chối tài nguyên lạ). Chờ Codex review lại.

> **For agentic workers:** REQUIRED SUB-SKILL: Use ai-skills:subagent-driven-development (recommended) or ai-skills:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Gom khai báo principal kiểm lại `tram-kiem` về MỘT nguồn (`cach_ly.tram_kiem`, đọc qua một hàm); chạy kiểm lại trên **bản chép do chính `tram-kiem` sở hữu** (trạm `git archive` → `sudo -u tram-kiem tar -x`, môi trường kiểm qua stdin, `tram-kiem` tự dọn) — **không dòng sudoers nào chạy root, không helper, không ACL/chmod** (D22); `tram chu cai-dat-tho` cài có **sổ journal** (du_dinh trước lệnh, da_tao kèm định danh sau quan sát) để `tram chu go-cai-dat-tho` chỉ gỡ đúng thứ lần cài tạo ra (R2, Codex F02); `tram giao kiem` kiểm được các điều kiện mới khi chạy thật — gỡ hết các lỗ mã chặn trước spike S6 (bead `bs-urj.12`, `bs-urj.13`, `bs-urj.14`).

**Architecture:** `cach_ly.tram_kiem: user:<tên> | sandbox:<tên>` là khoá chuẩn; `doc_principal_kiem()` (`tram/cau_hinh/principal_kiem.py`) là cửa đọc duy nhất, đối chiếu khoá cũ `giao_viec.principal_kiem` của 4a-2. `PrincipalKiem.tu_cach_ly()` dựng argv từ `Principal` của 3a-2 (`sudo -n -H -u <tên> --preserve-env=… --`, cơ chế sandbox thêm `sandbox-exec -f HO_SO_KIEM`), nên argv lúc chạy và dòng sudoers (`dong_sudoers_kiem`) sinh từ cùng hằng số. Kiểm lại (`kiem_lai`) giữ khoá `~/.tram/kiem-lai.khoa` (một lần một lúc), gọi `PrincipalKiem.don_sach` (giết mọi tiến trình + crontab của `tram-kiem` DƯỚI chính `tram-kiem`, rồi trạm tự đếm bằng `pgrep -U` không qua sudo), `tram-kiem` `mkdir` thư mục MỚI `<thu_muc_kiem>/<giao_id>-<ngẫu nhiên>`, trạm `git archive` (đã vô hiệu `export-ignore`/`export-subst` bằng `info/attributes` của kho kiểm) pipe sang `tar -x` dưới `tram-kiem`; đích môi trường kiểm được xét trên **cây git của commit** rồi đi qua stdin (tar một file 0600); lệnh kiểm chạy dưới `tram-kiem`; cuối cùng `don_sach` + `tram-kiem` tự `rm -rf`, trạm `lexists` — còn sót → ném, **không trả kết quả**. Phía cài đặt: mọi user/file root/thư mục đi qua `tai_nguyen.py` + sổ `so-cai.jsonl` (chỉ ghi thêm, fsync); user mang mã id bản ghi trong RealName; định danh user = UID + GeneratedUID, file = sha256, thư mục = inode. Thứ đã có mà sổ không ghi → từ chối cài; gỡ chỉ khi còn đúng định danh.

**Tech Stack:** Python 3.12 (`uv`), PyYAML (đã có), công cụ macOS có sẵn (`git archive`, `/usr/bin/tar` = bsdtar, `pkill`, `pgrep`, `crontab`, `dscl`, `sysadminctl`, `shasum`, `sudo -n -l`). **Không thêm phụ thuộc nào.**

**Spec:** [docs/specs/2026-10-13-phan-3-may-tho-han-muc.md](../specs/2026-10-13-phan-3-may-tho-han-muc.md) — §7.3 (mục 1, 2, 5, 7), §12 S6, §13 mục 12, §14. [docs/specs/2026-10-13-phan-4-giao-viec.md](../specs/2026-10-13-phan-4-giao-viec.md) — §6.2 bước 1, 3, 4. Quyết định: [chốt đợt 4](../quyet-dinh/2026-10-15-chot-dot-4.md) D3, D4, D21, D22, D34, D40. Review: `.handover/review-codex-dot4/REVIEW-CODEX.md` F01, F02, F03, F12. Đọc kèm: [sổ tay chạy thật](../handovers/2026-10-15-so-tay-chay-that.md) §4.1 (S6); plan [3a-2](2026-10-13-lat-3a-2-may-tho-chay-that.md) Task 3, 4, 11, 15, G3, G20, G31, G32; plan [4a-2](2026-10-13-lat-4a-2-giao-viec-noi-that.md) Task 1, 5, 9, 10, G2, G7, G8.

**Không làm:** chọn cơ chế §14 thay Đại ca (D3 đã chọn **thử `user` riêng mỗi khe trước**, mã vẫn giữ hai nhánh); chạy `cai-dat-tho`/`go-cai-dat-tho`/`sudo` thật (Task 9, chờ cổng S6); quyền Git chung của khe (3a-2 G20 — S6); Keychain dưới sandbox (G34), kênh ghi Unix socket (G29); gỡ cài đặt Mac thợ từ xa (3b); lịch sử/tag/submodule/LFS trong bản chép (D40 chọn (b) — chỉ repo một commit, mục "Cây kiểm và `.git`").

> **Trạng thái:** bản r47 16/10/2026 (sau review Codex đợt 5). T2/T4/R3 đã ghép; T1, T3, T5, T7, T10 giữ nguyên văn bản D40; T6, T8 viết lại; thêm T11, T12. Chạy thử đủ trên `main 793facb` theo đợt T1,T3 → T5,T10 → T6,T7 → T8,T11 → T12. Chưa review lại.

## Global Constraints

- **Điều kiện tiên quyết:** `main` tại hoặc sau `793facb` (đã có T2 `2d21bd7`, T4 `d223406`, R3 `bedcea6`, và các lát khác ghép tới review đợt 5). **N₀ = 2100** (`uv run pytest -q` trên `main` `793facb`, đo 16/10 bản r47; số 1994 cũ là của `4a907cc`). Đo lại trước Task 1; lệch thì dừng, báo người điều phối.
- **TDD:** mỗi task viết test trước, chạy thấy fail (thông báo ở Step 2 là kết quả chạy thật trên bản sao), viết mã, chạy thấy pass. Ngoại lệ: Task 9 (chạy thật — chờ cổng, không phải task code).
- **Mỗi file nguồn ≤ ~120 dòng, mỗi dòng ≤ 120 ký tự** (file dài nhất sau plan: `tram/giao_viec/kiem_san_sang.py` 109, `tram/giao_viec/ban_chep.py` 123, `tram/chu/go_cai_dat_tho.py` 122, `tests/test_giao_kiem.py` 127, `tests/test_go_cai_dat_tho.py` 126 — các file test cũ vượt nhẹ ~120 vì thêm ca). Dòng > 120 ký tự CÓ SẴN trên `main` không sửa (`kiem_san_sang.py` dòng `_dung_duoc`, `cai_dat.py` dòng `in_ke_hoach`, `test_noi_giao_viec.py` dòng cuối, `test_tho_lenh_chay.py` dòng `monkeypatch.setattr("tram.tho.khach…`). Định danh tiếng Việt không dấu.
- **Mỗi task một worktree, một nhánh, một commit**, tạo từ `main` **sau khi đã ghép đợt trước**. Task cùng đợt không sửa chung file. Không push, không merge (người điều phối ghép).
- **Không thêm phụ thuộc mới.**
- **Test không bao giờ:** chạy `sudo`, `visudo`, `launchctl`, `sysadminctl`, `createhomedir`, `dscl`; tạo/xoá user; ghi `/etc`, `/Library`, `/usr/local`; đụng Keychain, mạng, `~/.tram` thật (`TRAM_HOME` tạm — `tests/conftest.py`). `boc` đồng nhất thay `sudo -u tram-kiem`: `git archive`, `tar`, `mkdir`, `rm` chạy THẬT dưới user đang test trong `tmp_path`; `don_sach`/`chay` giả không bao giờ gọi `pkill` thật (giết nhầm tiến trình test). Hệ thống cài/gỡ dùng `tests/he_gia.py` (`HeGia`).
- **Không chọn thay Đại ca cơ chế §14:** mọi đường đi qua chuỗi `user:<tên>` | `sandbox:<tên>` và `Principal` của 3a-2.
- **Thao tác hệ thống** (tạo user, sudoers, LaunchDaemon, hồ sơ sandbox, gỡ chúng) chỉ **in kế hoạch + chờ `dong-y`** (khuôn `tram chu cai-dat`). Agent **không gõ `dong-y`**, không nhập mật khẩu `sudo` thay Đại ca; Đại ca dán/gõ trong **Terminal.app**.
- Lệnh test: `uv run pytest -q` từ thư mục worktree của task.

## Phụ thuộc đã có (main + plan trước — plan này dùng, không sửa trừ chỗ ghi rõ)

| Thứ dùng | Ở đâu | Từ lát | Plan dùng ở |
|---|---|---|---|
| `Principal(co_che, user, ho_so)` + `.boc(argv)`, `.voi_ho_so(p)`; `doc_principal(chuoi)`, `ChuaCoPrincipal`, `SUDO`, `SANDBOX_EXEC`, `BIEN_GIU`, `USER_RE` | `tram/tho/principal.py` | 3a-2 T3 | 1, 5 |
| `ho_so_sandbox(*, cam, cam_ghi, cho_ghi, cong_cam)` | `tram/tho/sandbox.py` | 3a-2 T3 | 1 |
| `CauHinhCachLy(kenh_ghi, socket, tram_kiem, db_nghiep_vu)`, `nap_cau_hinh_cach_ly` (**sửa docstring** — Task 5) | `tram/cau_hinh/cach_ly.py` | 3a-2 T4 | 5, 6 |
| `KeHoach(tep, lenh, canh_bao, buoc)`, `in_ke_hoach`, `thuc_hien`, `bo_qua_loi` (T4 — **đã ghép**) | `tram/chu/cai_dat.py` | 2a, 3a-2 T15, 3c T4 | 6, 8 |
| `lap_ke_hoach_tho`, `noi_dung_sudoers`, `plist_tho`, `NHAN_THO`, `SUDOERS`, `DAEMON` (**sửa** — Task 6) | `tram/chu/cai_dat_tho.py` | 3a-2 T15 | 6, 8 |
| `_hoi`, `_cai_dat_tho`, `_kiem_cach_ly`, `them_lenh_chu_tho` (**sửa** — Task 6 bản vá, Task 8 chèn theo mốc) | `tram/chu/lenh_tho.py` | 3a-2 T15, T20 | 6, 8 |
| `kiem_cach_ly`, `_boc_sudo` (**sửa** — Task 6) | `tram/chu/kiem_cach_ly.py` | 3a-2 T15 | 6 |
| `PrincipalKiem(ten, boc, trao_quyen)` + `.boc_lenh`, `.kill_nhom`, `.trao` (**viết lại** — Task 5: bỏ `trao_quyen`/`trao`) | `tram/giao_viec/principal_kiem.py` | 4a-2 T1 | 5, 6, 7 |
| `CauHinhGiaoViec`, `nap_cau_hinh_giao_viec`, `KHOA`, `CHU_KY` (**sửa** — Task 5) | `tram/cau_hinh/giao_viec.py` | 4a-2 T1 | 5, 6 |
| `kiem_lai(…, trao_quyen, kill)` (**sửa** — Task 3: `trao_quyen` → `don_sach`), `KetQuaKiemLai` | `tram/giao_viec/kiem_lai.py` | 4a-1 T14, 4a-2 T5 | 3 |
| `BoGiaoViec.trao_quyen` (**đổi tên** `don_sach` — Task 3), `day_pipeline._kiem_lai` (**sửa** một dòng — Task 3), `dung_bo_that` (**sửa** một dòng — Task 3, Task 5) | `tram/giao_viec/bo.py`, `tick_pipeline.py`, `noi_that.py` | 4a-2 T4, T7, T9 | 3, 5 |
| `loi_dich`, `LoiMoiTruongKiem` (không sửa; `chep_moi_truong_kiem` vẫn dùng phía thợ) | `tram/kiem/moi_truong.py` | 4a-1 | 3 |
| `tao_worktree`, `xoa_worktree` (không sửa; kiểm lại thôi dùng, `co_do_gn.py` vẫn dùng) | `tram/giao_viec/git_kiem.py` | 4a-1 T5 | — |
| `kiem_giao_viec`, `kiem_principal`, `_ghi_duoc`, `_muc`, `_ra`, `LOI_CHAY` (**sửa** — Task 5, Task 7) | `tram/giao_viec/kiem_san_sang.py` | 4a-2 T10 | 5, 7 |
| `MucKiem(muc, muc_do, chi_tiet)` | `tram/tho/kiem_may.py` | 3a-1 T24 | 7 |
| `LOI = (LoiBd, CalledProcessError, TimeoutExpired, OSError)` của vòng tick — `LoiBanChep(OSError)` rơi vào đây: đếm lỗi, vòng sau thử lại | `tram/giao_viec/tick.py` | 4a-2 | 3 |
| Công cụ test: `tram_home_tam` (`conftest.py`), `dung_kho` (`kho_kiem_gia.py`), `m`/`chay` (`test_kiem_lai_principal.py`), `PK`/`chay_gia`/`dung_lenh`/`muc` (`test_giao_kiem.py`), `dung`/`bug`/`GIU` (`giao_viec_gia.py`, `test_tick.py`) | `tests/` | 0, 4a-1, 4a-2 | 3, 5, 7 |

## Câu hỏi / giả định

Cột "Loại": **HỢP ĐỒNG MỚI** = giao diện/khoá/lệnh/hành vi mà phần khác (hoặc Đại ca khi chạy thật) dựa vào, Đại ca cần chốt; **lệch chữ spec/plan**; **giả định** = chi tiết thực thi; **ĐÃ CHỐT Dn** = quyết định đã có; **BỎ (D22)** = hàng của bản helper root, giữ số để tra cứu.

| # | Chỗ mơ hồ | Chọn | Vì sao | Loại |
|---|---|---|---|---|
| G1 | Khai principal kiểm ở đâu | **Khoá chuẩn `cach_ly.tram_kiem: user:<tên> \| sandbox:<tên>`** | Spec 3 §7.3 mục 5 định nghĩa `tram-kiem` cùng hợp đồng principal thực thi; người dùng đầu tiên là S6; khoá 4a-2 chứa argv tự do không kiểm được với sudoers. Codex: "Giữ". | **ĐÃ CHỐT D40** (lệch 4a-2 G2, G7) |
| G2 | Khoá cũ `giao_viec.principal_kiem` | Trùng tên → cảnh báo, bỏ argv cũ; khác tên / chỉ có khoá cũ / sai dạng → `ValueError` | Lỗi sớm rẻ hơn chạy dưới principal sai. Codex: "Giữ". | **ĐÃ CHỐT D40** |
| G3 | "Mọi nơi đọc dùng chung một hàm" | `doc_principal_kiem(duong_dan=None, *, bao)`; gọi từ `nap_cau_hinh_giao_viec`, `cai-dat-tho`, `kiem-cach-ly` | Một cửa | giả định |
| G4 | Cờ `--tram-kiem` | **Bỏ cả hai cờ**; Đại ca viết cấu hình TRƯỚC `cai-dat-tho` | Cờ là nguồn thứ ba. Codex: "Giữ" (F12 đã sửa sổ tay). | **ĐÃ CHỐT D40** (CLI) |
| G5 | Hình dạng argv của `tram-kiem` | `PrincipalKiem(ten, boc, co_che)` — `boc` = `Principal.boc([])`; **không còn `trao_quyen`/`thu_quyen`** | D22 bỏ trao quyền | **HỢP ĐỒNG MỚI** (lệch 4a-2 G7) |
| G6 | Thu quyền khi xong | ~~hàm thu từ `trao`~~ → **`don_sach` + `tram-kiem` tự `rm -rf`**, trạm `lexists`; còn sót → ném, KHÔNG trả kết quả | D22; Codex G6 "không công nhận kết quả khi chưa thu quyền an toàn" | **HỢP ĐỒNG MỚI** — thay bởi G22/G25; bản r47: `don_sach` là vòng đời cách ly đầy đủ (Task 11) — `pgrep` rỗng KHÔNG còn là bằng chứng một mình
| G7, G8, G9 | Helper root `tram-trao/thu-quyen-kiem`, `find`/`chmod +a`/`chown`, dòng sudoers `(root)` | — | **BỎ (D22)**: không root, không ACL/chmod | **ĐÃ CHỐT D22** |
| G10 | `giao_viec.thu_muc_kiem` khi đã khai `tram-kiem` | Ngoài `~/.tram`, đường dẫn THẬT, chỉ `[A-Za-z0-9._/-]` (`goc_hop_le`) | Nhúng vào hồ sơ sandbox và lệnh cài | **HỢP ĐỒNG MỚI** (siết 4a-2 G8) |
| G11 | Cơ chế `tram-kiem` so với `--co-che` | Phải cùng cơ chế, khác → `ValueError` | Một máy một cơ chế (D3 giữ hai nhánh) | **HỢP ĐỒNG MỚI** |
| G12 | Cơ chế `sandbox` cho `tram-kiem` | Hồ sơ cố định `/usr/local/tram/tram-kiem.sb` (root:wheel 0644, cài lúc `cai-dat-tho`); thư mục cài `/usr/local/tram` chỉ tạo ở cơ chế sandbox | Không phải helper — file root chỉ đọc | **ĐÃ CHỐT D40** (S6: cú pháp SBPL) |
| G13 | `tram-kiem` dùng chung user với khe? | **Không** — user riêng, không trùng khe/trạm/quản lý → `ValueError` | D22 thêm lý do: `don_sach` giết MỌI tiến trình của `tram-kiem` — dùng chung là giết agent khe | **ĐÃ CHỐT D40** |
| G14 | Ghi lại thứ `cai-dat-tho` tạo | ~~`da-cai.json` planned~~ → **journal `so-cai.jsonl` v2** (G26) | Codex F02; review đợt 5 Q01 | **HỢP ĐỒNG MỚI** — thay bởi G26 (bản r47: phục hồi đuôi dở, ghi đủ bytes, khoá cài/gỡ — R4 đã sửa)
| G15 | Lệnh hoàn tác | `tram chu go-cai-dat-tho [--xoa-nha] [--dong-y]` — giữ khoá sổ; chỉ gỡ thứ có `da_tao` VÀ còn đúng định danh (G27); user luôn `-deleteUser -keepHome`; nhà là bước riêng chỉ khi `--xoa-nha`, sau khi user đã gỡ, còn đúng inode; user có thư mục kiểm chưa gỡ được thì giữ user; idempotent | Codex F02; Q01/Q02 | **HỢP ĐỒNG MỚI**; mặc định giữ nhà **ĐÃ CHỐT D40**
| G16 | `thuc_hien` với lệnh dọn có `sudo` | Bỏ qua lỗi `launchctl bootout`/`pkill` kể cả qua `sudo` | — | **ĐÃ CODE** (T4, D21) |
| G17 | `tram giao kiem` kiểm gì thêm | Mục "thư mục kiểm của tram-kiem" (chủ = `tram-kiem`, không symlink, không g/o-w, trạm đi qua được), "sudoers không NOPASSWD root" (`sudo -n -l`), "ghi bản chép kiểm" (giữ khoá; `tram-kiem` tạo thư mục con + file rồi tự dọn) | Chỉ XANH khi chạy thật | giả định |
| G18 | `kiem-cach-ly` với `tram-kiem` | H9 chạy qua đúng argv kiểm lại (`PrincipalKiem.boc_lenh`) | Kiểm chứng đúng thứ sẽ chạy | lệch 3a-2 G31 |
| G19 | Trao quyền phía thợ dùng `chmod -R ±a` | Sửa sang `find … -exec chmod ±a` | — | **ĐÃ CODE** (T2, D21) |
| G20 | Hai cơ chế §14 | Chung luồng bản chép; khác ở `boc` (thêm `sandbox-exec -f HO_SO_KIEM`), dòng sudoers (ghim tiền tố) và việc cài hồ sơ | Chạy được với cả hai | giả định |
| G21 | Kiểm lại chạy ở đâu | **Bản chép do `tram-kiem` sở hữu**: `tram-kiem` `mkdir` thư mục MỚI `<thu_muc_kiem>/<giao_id>-<8 hex>`; trạm `git archive <commit>` → `sudo … tar -x -f - -C <dir>` dưới `tram-kiem` | D22 | **HỢP ĐỒNG MỚI** (thay worktree của 4a-1/4a-2) |
| G22 | Dọn bản chép | `don_sach` → `tram-kiem` `rm -rf` (bản chép + `<bản chép>.nha`) → trạm `os.path.lexists`; lỗi ở bất kỳ bước nào → `LoiBanChep`, `kiem_lai` không trả kết quả, vòng tick đếm lỗi. `don_sach` cuối lần kiểm thấy lịch hẹn giờ (dù đã gỡ được) → cũng ném: kết quả không được công nhận | D22; C01 | **HỢP ĐỒNG MỚI** (bản r47)
| G23 | Môi trường kiểm | Xét đích trên **cây git của commit** (`loi_dich_trong_cay`: cha là thư mục thật, đích là file thường); rồi tar một file (0600) qua stdin cho `tar -x` dưới `tram-kiem` | D22 "qua stdin"; bsdtar còn tự từ chối giải nén xuyên symlink (đã đo) | **HỢP ĐỒNG MỚI** |
| G24 | Một lần kiểm lại một lúc | Khoá `flock` không chờ `~/.tram/kiem-lai.khoa`; bận → `KiemLaiDangBan`. `tram giao kiem` cũng giữ khoá: không còn giết nhầm lần kiểm lại đang chạy (mục 6 cũ) | `don_sach` giết mọi tiến trình `tram-kiem` | **ĐÃ CHỐT D40** |
| G25 | `don_sach` | Vòng đời cách ly (Task 11, mục "Vòng đời cách ly của `tram-kiem` (C01)"): mỗi lượt giết (`pkill -U/-u`), trạm `pgrep -U/-u`, launchd (nhãn + vân tay so với nền), cron (`crontab -l` phải "no crontab for"), at (file trong `/usr/lib/cron/jobs` + `atq`), nhà `/var/empty`, tệp (gốc rỗng, thư mục ghi-chung, `DARWIN_USER_*`), `pgrep` lần cuối; trả về khi HAI lượt liên tiếp sạch; thấy lịch → gỡ, xác nhận, vẫn `LoiBanChep`; không xác nhận được → `LoiBanChep` | C01: `pgrep` chỉ là ảnh chụp; không root (D22) | **HỢP ĐỒNG MỚI** — kẽ hở còn lại ghi ở rủi ro (a), chứng minh trên máy thật ở S6 bước 6
| G26 | Sổ cài đặt | `~/.tram/cai-dat-tho/so-cai.jsonl` v2: `du_dinh` (fsync TRƯỚC lệnh) → `da_tao` (+định danh) / `khong_tao` / `da_go`; chỉ ghi thêm; khoá `so-cai.jsonl.khoa` cho mọi lần ghi và cả lần cài/gỡ; dưới khoá, đuôi dở (kể cả UTF-8 dở) chép ra `.duoi-hong` rồi cắt TRƯỚC khi nối; ghi đủ bytes + `F_FULLFSYNC`; dòng hỏng/chuyển trạng thái sai ở giữa → không cài/gỡ gì | Codex F02, R2, Q01 | **HỢP ĐỒNG MỚI** (bản r47)
| G27 | Định danh | User: RealName `tram <u> <id>` khi tạo (bằng chứng do LẦN NÀY tạo), lưu UID + GeneratedUID; file: sha256; thư mục: inode (thư mục kiểm kèm `chu`) | Tên tái sử dụng / `addUser` trên user có sẵn không thành "của trạm" | **ĐÃ CHỐT D40** (đổi RealName của user dịch vụ) |
| G28 | Cài đè thứ có sẵn | Đã có mà sổ không ghi trạm tạo → **từ chối cài** (ValueError, mã 2), không backup/đè | Đơn giản hơn backup; không bao giờ nhận đồ người khác | **ĐÃ CHỐT D40** |
| G29 | Đối soát crash | Bước đầu của cài và gỡ: mọi `du_dinh` chưa khép → quan sát: đúng định danh mong đợi → `da_tao`, còn lại → `khong_tao`. Biên nhận user (UID+GUID) KHÁC hoàn tất nhà: nhà là tài nguyên riêng, chỉ nhận khi thuộc đúng UID của user trạm và mọi biên nhận cũ của nhà cùng GUID; thư mục mang UID chủ mong đợi; `dscl` lỗi khác "không có bản ghi" → dừng, không suy "không còn" | Codex F02; Q02 | **HỢP ĐỒNG MỚI** (bản r47)
| G30 | Cây kiểm không có `.git` | ~~Chấp nhận, chờ chốt~~ → **(b) repo git MỘT commit** do `tram-kiem` tự dựng sau `tar -x` (Task 10, G32, G33) | D22 bỏ `.git`; D40 chọn (b) | **ĐÃ CHỐT D40** |
| G31 | `export-ignore`/`export-subst` | `info/attributes` của kho kiểm = `* -export-ignore -export-subst` (ưu tiên cao nhất) | Commit không giấu được test khỏi bản chép (đã đo trên git 2.56) | giả định |
| G32 | Hình dạng repo của bản chép (D40 (b)) | `git init --template=` → `git add -A -f` → `git commit --allow-empty --no-verify -m kiem`, DƯỚI `tram-kiem` (`boc`), TRƯỚC khi môi trường kiểm vào cây; nhánh `kiem`, tác giả `tram-kiem <tram-kiem@localhost>`; mục tiêu cây = cây commit gốc, nhưng chưa được bảo đảm với thuộc tính chuẩn hoá CRLF/text/eol (R7), ngoài ngoại lệ LFS/submodule đã nêu; không lịch sử/remote/alternates; bản chép rỗng → vẫn một commit cây rỗng (`--allow-empty`, không nhánh riêng); git lỗi → `LoiBanChep` như `tar` | D40 "tram-kiem tạo repo git một commit … (tắt hooks)"; `-f` để file đã theo dõi mà `.gitignore` bỏ vẫn vào cây; `.env.testing` không thành đối tượng git | **HỢP ĐỒNG MỚI** (D40 chọn hướng; tên nhánh/tác giả/thông điệp là chi tiết) |
| G33 | Cấu hình git khi dựng repo | `/usr/bin/env -i PATH=/usr/bin:/bin:/usr/sbin:/sbin HOME=/var/empty LC_ALL=C GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null GIT_ATTR_NOSYSTEM=1 <git của trạm>` + `-c core.hooksPath=/dev/null -c core.attributesFile=/dev/null -c core.fsmonitor=false -c gc.auto=0 -c maintenance.auto=false -c commit.gpgSign=false …`; KHÔNG chặn riêng `filter.lfs.*` | Lệnh filter (`clean`/`process`) chỉ đến từ cấu hình; `.gitattributes` của cây chỉ gọi tên driver. Đã bỏ mọi nguồn cấu hình ngoài `.git/config` mới tạo (không template) và `-c` của trạm → không filter nào chạy — test khai filter ở global, system, `GIT_CONFIG_COUNT`, template | giả định (đã đo git 2.56) |
| G34 | Nhà của `tram-kiem` (C01, r47) | `sysadminctl -addUser … -home /var/empty`, KHÔNG `createhomedir`; lúc chạy `don_sach` đòi nhà đúng `/var/empty`, chủ root, không g/o ghi, không ACL; lệnh kiểm chạy với HOME/TMPDIR mới `<bản chép>.nha` | Nhà ghi được là chỗ cài cắm dotfile/LaunchAgents cho lần kiểm sau | **HỢP ĐỒNG MỚI** — câu hỏi r47 số 1 |
| G35 | Lần kiểm phải gỡ lịch hẹn giờ (C01, r47) | Bước dọn cuối thấy lịch → gỡ, xác nhận, `kiem_lai` trả `dat=False, loi="lich-hen-gio"` → `kiem.lai` không đạt + escalation; bước dọn đầu thấy lịch sót → ném, vòng sau thử lại | Không công nhận cây có lịch; không để commit chặn dự án mãi | **HỢP ĐỒNG MỚI** — câu hỏi r47 số 2 |
| G36 | Nền launchd của `tram-kiem` (C01, r47) | `~/.tram/kiem-lai/nen-launchd.txt` (nhãn + vân tay), `tram giao chup-nen-lich [--dong-y] [--ghi-de]`; thiếu/sai dạng → kiểm lại dừng | User khác không đọc được miền launchd; Apple nạp sẵn dịch vụ vào miền user | **HỢP ĐỒNG MỚI** — câu hỏi r47 số 4 |
| G37 | Harness S6 (Q03, r47) | `tram giao nghiem-thu-kiem [--tai-sinh] [--cho GIÂY]`: kho nháp + môi trường giả, đúng chuỗi `kiem_lai`, mỗi khẳng định một dòng, mã 1 khi có ĐỎ; `--tai-sinh` chỉ dưới principal thật | Q03: `tick --thu` không vào pha kiểm lại | **HỢP ĐỒNG MỚI** (CLI) |

## Phân tích sudoers (D22)

Dòng cho tài khoản trạm (`dong_sudoers_kiem`, `tram/tho/quyen_kiem.py`), ngoài dòng khe có sẵn của 3a-2:

| Cơ chế | Dòng | Chặn được gì |
|---|---|---|
| `user` | `<tram> ALL=(<tram-kiem>) NOPASSWD:SETENV: ALL` | runas CHỈ `tram-kiem`; không root, không user khác |
| `sandbox` | `<tram> ALL=(<tram-kiem>) NOPASSWD:SETENV: /usr/bin/sandbox-exec -f /usr/local/tram/tram-kiem.sb *` | như trên + **mọi** lệnh dưới `tram-kiem` bắt buộc đi qua hồ sơ cố định do root giữ (`test_co_che_sandbox_ghim_tien_to_ho_so_co_dinh`) |

**Sudoers có chặn được lệnh tuỳ ý dưới `tram-kiem` không? Không — và chặn cũng không thêm an toàn.**
1. Kiểm lại CHÍNH LÀ chạy mã agent viết dưới `tram-kiem`: `vendor/bin/phpunit`, `npm test`, `composer test` của commit là chương trình tuỳ ý. Argv cố định hay wrapper nhận số đối số cố định vẫn phải có một nhánh "chạy lệnh kiểm" — nhánh đó chạy được mọi thứ.
2. Kẻ dùng được dòng NOPASSWD là tiến trình chạy dưới tài khoản trạm (vd tram-api bị chiếm). Nó vốn đã giữ mọi bí mật của trạm và ghi thẳng được `su-kien.db`; chạy thêm lệnh dưới `tram-kiem` (user không credential, chỉ sở hữu bản chép) không cho nó gì mới. Cái nguy hiểm là dòng NOPASSWD **chạy root** (bản helper cũ) — D22 bỏ hẳn.
3. `SETENV` cần cho `--preserve-env=` của `Principal.boc`; biến môi trường (kể cả `DYLD_*`) chỉ ảnh hưởng tiến trình chạy dưới `tram-kiem` — yếu quyền hơn trạm.
4. Wrapper (`/usr/local/tram/tram-kiem <lệnh> <tên>`, số đối số cố định cho `tao`/`nhan`/`don`, cộng `chay <tên> -- argv…`) chỉ thêm được: env cố định do wrapper đặt (bỏ `SETENV`) và cwd do wrapper đổi (thư mục bản chép 0700). Đổi lại: thêm một file root phải cài/kiểm/gỡ, test shell. **Plan không làm** — D40 chốt theo `ALL` ("Chờ Đại ca chốt" mục 4).
5. Kiểm khi chạy thật (Task 7): `sudo -n -l` không được có dòng NOPASSWD nào runas `root`/`ALL` (`kiem_sudoers_khong_root`).

## Cây kiểm và `.git` — ĐÃ CHỐT D40: (b) repo git một commit

Trước D40 (D22, bản chép không `.git`) — hệ quả: lệnh kiểm nào gọi git đều hỏng trong bản chép — `git diff`/`git rev-parse`, test dựa `git ls-files`, `jest --changedSince/--onlyChanged`, `husky install` trong `prepare` của `npm ci` (tuỳ phiên bản: cảnh báo hoặc thoát lỗi), script composer đọc phiên bản từ tag, submodule (bản chép chỉ có thư mục rỗng), Git LFS (`git archive` có thể cho file con trỏ hoặc gọi filter smudge của trạm). Ghi chú: bản worktree cũ cũng **không** cho `tram-kiem` dùng git thật — file `.git` trỏ vào `~/.tram/kho-kiem` mà `tram-kiem` không đọc được; chỉ test (boc đồng nhất) mới thấy git. Nên D22 không làm hỏng thêm điều gì đang chạy được ở máy thật.

Ba cách đã đề xuất: (a) chấp nhận, cảnh báo khi `lenh_kiem` có chữ `git`; **(b) repo tổng hợp một commit**; (c) `git bundle` của commit qua stdin, `tram-kiem` `git clone` (có lịch sử tổ tiên, nặng nhất). **D40 chọn (b)** — Task 10.

Cách làm (Task 10, G32, G33): ngay sau `tar -x` trong `chep_ban`, ba lệnh qua `boc` (dưới `tram-kiem`): `git init -q --template=`, `git add -A -f`, `git commit -q --allow-empty --no-verify -m kiem`, cả ba chạy dưới `/usr/bin/env -i … GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null GIT_ATTR_NOSYSTEM=1` với `-c core.hooksPath=/dev/null -c core.attributesFile=/dev/null -c user.name=tram-kiem -c user.email=tram-kiem@localhost …`. Dựng repo TRƯỚC khi môi trường kiểm vào cây. Bất kỳ lệnh nào lỗi → `LoiBanChep`, không chạy lệnh kiểm (cùng khuôn `tar` lỗi).

Chứng minh bằng test (`tests/test_ban_chep_git.py`): repo một commit, cây = cây commit gốc (kể cả file đã theo dõi mà `.gitignore` bỏ), không có commit gốc hay tổ tiên, không remote/alternates; hook `.husky/*` trong cây (trỏ bằng `core.hooksPath` ở cấu hình global), hook trong template (`init.templateDir`, `GIT_TEMPLATE_DIR`), filter `x`/`lfs` khai ở global, system và `GIT_CONFIG_COUNT` — không cái nào chạy, `.git/hooks` không tồn tại; `git init/add/commit` lỗi → `LoiBanChep`, không chạy lệnh, thư mục được dọn; bản chép rỗng → một commit cây rỗng; commit chứa `.git` → `git archive` của trạm từ chối → `LoiBanChep`, không dựng repo lên đó.

**`.gitattributes` và filter khi `git add`:** cây chỉ đặt được TÊN driver (`* filter=lfs`); lệnh `clean`/`process`/`required` chỉ đọc từ cấu hình. Nguồn cấu hình còn lại: `.git/config` vừa `git init` (không template — chỉ `core.*`) và `-c` của trạm. Nên KHÔNG thêm `-c filter.lfs.clean=`: thừa, và chỉ chặn được tên đã biết. Hệ quả: dự án LFS có trong bản chép đúng như `git archive` của trạm ghi ra (con trỏ, hoặc nội dung nếu trạm có smudge LFS) và `git add` lưu nguyên — khi đó cây có thể khác cây commit gốc (chỉ ảnh hưởng `git diff` của lệnh kiểm, không ảnh hưởng an toàn).

**Vẫn không làm được (lệnh kiểm cần thì vẫn hỏng — Đại ca biết):** lịch sử/tag (`git describe`, composer đọc phiên bản từ tag, `jest --changedSince=origin/main`, `git diff origin/main`); submodule (thư mục rỗng, `git add` bỏ qua → cây khác gốc); repo lồng `sub/.git` (git archive từ chối, như trên). `git status` thấy `?? .env.testing` (file môi trường kiểm vào sau commit, cố ý). Cây lớn tốn thêm thời gian `git add` (băm mọi file) — chưa đo trên dự án thật (S6). Mức đe doạ: hook/filter nếu có chạy cũng chỉ chạy dưới `tram-kiem` — đúng principal sẽ chạy mã của commit ngay sau đó; chặn để repo xác định và không chạy gì trước khi chép môi trường kiểm, không phải để nâng ranh giới quyền.

## Ca F01/F02 của Codex — xử lý ở đâu

| Ca | Còn áp dụng? | Xử lý | Test |
|---|---|---|---|
| F01 hardlink ra ngoài, thiết bị/FIFO, `chmod`/`chown` theo pathname bằng root | **Không** — không còn thao tác root/ACL trên cây; `git archive` không sinh hardlink/thiết bị | — | — |
| F01 đổi cây sau khi kiểm | Có | Phép xét làm trên đối tượng git (bất biến theo SHA): `diff_cham_cam`, `loi_dich_trong_cay`; thư mục làm việc của kho kiểm không ảnh hưởng `git archive`; tiến trình lạ đổi cây sau khi chép → bsdtar từ chối ghi môi trường xuyên symlink → `thieu-moi-truong-kiem`, không chạy lệnh | `test_ban_chep_dung_commit_co_repo_git_khong_bi_export_ignore_giau` (tên sau Task 10), `test_cay_bi_doi_sau_khi_chep_thi_moi_truong_khong_ra_ngoai` |
| F01 symlink trong archive | Có | Mọi thao tác trên cây chạy dưới `tram-kiem` → symlink không với tới gì mới; đích môi trường là/đi qua symlink trong commit → từ chối; `rm -rf` xoá link không theo | `test_symlink_trong_archive_khong_bi_di_theo`, `test_dich_moi_truong_kiem_la_symlink_bi_tu_choi` (có sẵn) |
| F01 tiến trình `tram-kiem` tái sinh / `pkill` lỗi | Có | `don_sach` trước khi chép và trước khi dọn; trạm tự `pgrep`; còn → `LoiBanChep`, không chép/không trả kết quả. Bản r47: `pgrep` chỉ là một bước của vòng đời cách ly (C01, Task 11) | `test_con_tien_trinh_tram_kiem_thi_khong_chep_khong_chay`, `test_tien_trinh_tai_sinh_luc_don_thi_khong_tra_ket_qua`, `test_tai_sinh_hoac_pgrep_loi_thi_nem`, `test_don_sach_giet_duoi_tram_kiem_roi_tram_tu_dem` |
| F01 dọn lỗi thì fail-closed | Có | `rm` lỗi hoặc thư mục còn → `LoiBanChep` dù lệnh kiểm pass; `tar` lỗi → không chạy lệnh | `test_tar_hoac_rm_loi_thi_fail_closed[/bin/rm, /usr/bin/tar]` |
| D40 (b) repo trong bản chép: git lỗi, hook/filter/template ngoài, `.git` trong commit | Có (mới) | git lỗi → `LoiBanChep`, không chạy lệnh; `env -i` + bỏ cấu hình global/system/template + hook tắt; `.git` trong commit → `git archive` từ chối | `test_git_loi_thi_fail_closed_nhu_tar[init, add, commit]`, `test_hook_filter_template_cua_cau_hinh_ngoai_khong_chay`, `test_commit_chua_git_thi_khong_dung_repo_len_do` |
| F01 hai kiểm lại đồng thời | Có | Khoá `flock` không chờ; tên thư mục ngẫu nhiên mỗi lần; `tram giao kiem` giữ cùng khoá | `test_hai_lan_kiem_lai_dong_thoi`, `test_dang_kiem_lai_thi_muc_ghi_do_khong_giet_tram_kiem` |
| F01 quyền gốc/cha cho principal thay | Đổi dạng | Gốc thuộc `tram-kiem` là đúng thiết kế; kiểm không symlink, không g/o-w | `test_thu_muc_goc_sai_la_do` (7 ca) |
| F02 journal planned/created | Có | `du_dinh` fsync TRƯỚC lệnh, `da_tao` SAU quan sát | `test_thuc_hien_ghi_du_dinh_truoc_da_tao_kem_dinh_danh_sau`, `test_ghi_them_trang_thai_la_ban_ghi_cuoi` |
| F02 định danh UID/GeneratedUID | Có | `dscl` UniqueID/GeneratedUID/RealName; gỡ chỉ khi cùng UID+GUID | `test_dinh_danh_user_doc_dscl_va_ten_tai_su_dung`, `test_user_xoa_tao_lai_hoac_file_bi_sua_thi_khong_go` |
| F02 user có sẵn + `addUser` lỗi không bị xoá | Có | Có sẵn lúc lập kế hoạch → từ chối cài; xuất hiện giữa chừng → RealName không mang mã → `khong_tao`, dừng; gỡ bỏ qua | `test_user_co_san_khong_do_tram_tao_thi_tu_choi_cai`, `test_user_xuat_hien_giua_chung_thi_khong_nhan_la_cua_tram`, `test_user_co_san_addUser_loi_khong_bi_xoa` |
| F02 crash trước/sau lệnh tạo | Có | Đối soát | `test_doi_soat_crash_truoc_va_sau_lenh_tao`, `test_crash_quanh_lenh_tao_doi_soat_roi_moi_go[True, False]` |
| F02 sổ hỏng | Có | Không cài/gỡ gì, mã 2 | `test_dong_cuoi_ghi_do_bi_bo_dong_hong_thi_tu_choi`, `test_so_hong_thi_khong_go_gi` |
| F02 thư mục không rỗng dừng giữa chừng | Có | Thư mục root gỡ CUỐI; lỗi chỉ cảnh báo, bước khác vẫn chạy; chạy lại còn đúng mục đó | `test_thu_muc_khong_rong_chi_canh_bao_buoc_khac_van_chay` |
| F02 lặp lại gỡ | Có | Chỉ thứ còn tồn tại + `da_go` | `test_go_dung_thu_tu_het_sach_va_chay_lai_rong` |
| R4 (Q01) đuôi sổ dở + nối tiếp | Có (r47) | Dưới khoá: cắt đuôi dở (giữ bằng chứng `.duoi-hong`) trước khi nối; ghi đủ bytes; đọc bỏ đuôi theo bytes | `test_duoi_do_bi_cat_giu_bang_chung_roi_moi_noi` (3), `test_short_write_va_loi_giua_chung_khong_lam_hong_so`, `test_duoi_do_doi_soat_doc_go_doc_cai_lai` |
| R4 (Q01) cài và gỡ đồng thời | Có (r47) | Khoá `so-cai.jsonl.khoa` cả lần cài/gỡ, không chờ; bận → mã 2, không làm gì | `test_khoa_so_chan_ghi_cua_lan_cai_go_khac`, `test_khoa_giu_boi_tien_trinh_khac`, `test_dang_go_thi_cai_dat_tho_khong_lam_gi`, `test_go_khi_dang_cai_thi_khong_lam_gi`, `test_khoa_truoc_khi_xem_so` |
| R5 (Q02) lỗi/crash giữa `addUser` và `createhomedir` | Có (r47) | Nhà là tài nguyên riêng; chạy lại chỉ làm nhà, giữ UID/GUID | `test_hong_giua_addUser_va_createhomedir_chay_lai_chi_tao_nha[lenh-loi, crash]`, `test_crash_sau_addUser_tu_tao_nha_chay_lai_chi_lam_phan_thieu` |
| R5 (Q02) nhà lạ / nhà cũ / UID dùng lại | Có (r47) | Chỉ nhận nhà của user trạm hiện tại, đúng UID, biên nhận cũ cùng GUID; còn lại từ chối lúc lập kế hoạch | `test_nha_co_san_truoc_user_la_nha_la_tu_choi_cai`, `test_nha_la_xuat_hien_sau_khi_user_cua_tram_da_co_thi_khong_nhan`, `test_cai_lai_sau_khi_giu_nha_khong_nhan_nha_cu[False, True]` |
| R5 gỡ nhà / thư mục mồ côi UID | Có (r47) | User luôn `-keepHome`; nhà xoá riêng khi `--xoa-nha`; user có thư mục kiểm chưa gỡ được thì giữ user | `test_go_xoa_nha_ghi_da_go_va_chay_lai_rong`, `test_xoa_nha_khong_xoa_nha_la_va_khong_dung_var_empty`, `test_thu_muc_kiem_khong_go_duoc_thi_giu_user_va_chu_doi_thi_khong_giu` |
| C01 lịch hẹn sau `pgrep`; lỗi gỡ cron; launchd/at; chuỗi; nhãn nền bị chiếm | Có (r47) | `don_sach` (Task 11): gỡ + xác nhận, hai lượt sạch liên tiếp, thấy lịch → không công nhận | `test_pgrep_rong_nhung_con_lich_hen_tre_thi_go_va_khong_cong_nhan` (3), `test_khong_go_hoac_khong_xac_nhan_duoc_lich_thi_nem` (7), `test_job_cai_lai_nguon_khac_khi_dang_quet_van_bi_bat`, `test_nhan_nen_bi_thay_chuong_trinh_la_dich_vu_la`, `test_ngap_job_keepalive_van_bi_go_truoc_khi_dem` |
| C01 tệp cài cắm cho lần sau | Có (r47) | HOME/TMPDIR mới mỗi lần; gốc rỗng; thư mục ghi-chung, `DARWIN_USER_*` dọn | `test_moi_lan_kiem_co_nha_moi_va_nha_duoc_don`, `test_tep_cai_cam_cho_lan_kiem_sau_bi_don_goc_rong`, `test_tep_khong_xoa_duoc_thi_nem` |
| F03 nguồn công bố lai | — | **ĐÃ CODE** R3 (`bedcea6`), tên `lai` D34 | `tests/test_cong_bo_lai.py` |
| F12 sổ tay dùng CLI cũ | — | Sổ tay đã sửa ở review; Task 9 viết theo CLI mới | — |

## Chờ Đại ca chốt (không chọn thay) — D40 đã chốt hết các mục còn mở

1. ~~Cơ chế §14~~ — **ĐÃ CHỐT D3**: thử user macOS riêng mỗi khe trước; S6 hỏng G20/G34/G35 thì chuyển user chung + sandbox; mã giữ hai nhánh.
2. ~~Khoá chuẩn `cach_ly.tram_kiem` (G1, G2) và bỏ cờ `--tram-kiem` (G4)~~ — **ĐÃ CHỐT D40**: khoá chuẩn `cach_ly.tram_kiem`, bỏ cờ.
3. ~~`tram-kiem` luôn là user riêng (G13)~~ — **ĐÃ CHỐT D40**: user riêng.
4. ~~Helper chạy bằng root~~ — **ĐÃ CHỐT D22**: không root. Phần nhỏ (sudoers `ALL` dưới `tram-kiem` hay wrapper số đối số cố định) — **ĐÃ CHỐT D40**: sudoers `ALL`.
5. ~~Đường cài `/usr/local/tram/libexec`~~ — **không còn helper**. Chỗ đặt hồ sơ sandbox — **ĐÃ CHỐT D40**: `/usr/local/tram/tram-kiem.sb` (chỉ cơ chế sandbox).
6. ~~`tram giao kiem` giết lần kiểm lại đang chạy~~ — **không còn**: có khoá (G24), `tram giao kiem` báo ĐỎ "đang có lần kiểm lại" thay vì giết.
7. ~~`go-cai-dat-tho` mặc định giữ hay xoá thư mục nhà~~ — **ĐÃ CHỐT D40**: giữ (`-keepHome`; `--xoa-nha` để xoá).
8. ~~Đổi thứ tự sổ tay S6~~ — **ĐÃ CHỐT D40**: đổi thứ tự (viết cấu hình trước `cai-dat-tho`; Task 9 bước 1).
9. ~~Sửa spec~~ — **ĐÃ CHỐT D40**: sửa spec theo mục "Cần sửa spec sau" (Em sửa sau khi Codex review lại plan).
10. ~~T2/T4/R3 có code ngay~~ — **ĐÃ CHỐT D21**, đã ghép. ~~Tên `lai`~~ — **ĐÃ CHỐT D34**. ~~Chính sách lai~~ — **D4**.
11. ~~Cây kiểm không có `.git`~~ — **ĐÃ CHỐT D40: (b)** repo git một commit do `tram-kiem` tự dựng, hook tắt — Task 10.
12. ~~Từ chối cài hay backup/đè tài nguyên không do trạm tạo (G28)~~ — **ĐÃ CHỐT D40**: từ chối cài.
13. ~~RealName user dịch vụ mang mã id (G27)~~ — **ĐÃ CHỐT D40**: RealName `tram <u> <id>`.
14. ~~Khoá một lần kiểm lại một lúc trên máy (G24)~~ — **ĐÃ CHỐT D40**: khoá một lần (nhiều dự án xếp hàng — rủi ro (d)).
15. **Câu mới của bản r47** (sau review đợt 5): xem mục "Câu hỏi r47 cho Đại ca" — 6 câu, mỗi câu kèm đề xuất.

## File Structure

```
tram/
  tho/quyen_kiem.py             # (mới) goc_hop_le, dong_sudoers_kiem, ho_so_tram_kiem, HO_SO_KIEM, THU_MUC_CAI — Task 1
  tho/principal_khe.py          # (đã sửa — T2, ghép 2d21bd7)
  chu/cai_dat.py                # (đã sửa — T4, ghép d223406)
  cong_bo/nguon_lai.py …        # (đã có — R3, ghép bedcea6)
  giao_viec/cay_kiem.py         # (mới) loi_dich_trong_cay, chuan_bi_thuoc_tinh, nguon_archive, tar_mot_tep — Task 3
  giao_viec/ban_chep.py         # (mới) giu_khoa, ten_ban_chep, chep_ban, nhan_moi_truong, don_ban, LoiBanChep     — Task 3
                                # (sửa) chep_ban dựng repo git một commit sau tar -x                               — Task 10
  giao_viec/repo_ban_chep.py    # (mới) lenh_repo, MOI_TRUONG, CAU_HINH — git init/add/commit cô lập (D40 (b))      — Task 10
  giao_viec/kiem_lai.py         # (sửa) chạy trên bản chép; trao_quyen → don_sach (Task 3); docstring (Task 10)
  giao_viec/bo.py, tick_pipeline.py, noi_that.py  # (sửa một dòng mỗi file) trao_quyen → don_sach               — Task 3
  cau_hinh/principal_kiem.py    # (mới) doc_principal_kiem                                                        — Task 5
  giao_viec/principal_kiem.py   # (viết lại) PrincipalKiem(ten, boc, co_che) + don_sach, tu_cach_ly               — Task 5
  cau_hinh/giao_viec.py, cau_hinh/cach_ly.py      # (sửa) nguồn chung, goc_hop_le; docstring                     — Task 5
  giao_viec/noi_that.py         # (sửa) don_sach=pk.don_sach                                                      — Task 5
  giao_viec/kiem_san_sang.py    # (sửa) mục ghi bản chép (Task 5); thêm 2 mục D22 (Task 7)
  chu/so_cai_tho.py             # (mới) SoCai journal v2, doi_soat                                               — Task 6
  chu/dinh_danh.py              # (mới) quan sát định danh user/file/thư mục, khop, cung                          — Task 6
  chu/tai_nguyen.py             # (mới) TaiNguyen, kiem_truoc, tao, LoiCaiDat                                     — Task 6
  chu/cai_dat_kiem.py           # (mới) phan_kiem: thư mục kiểm của tram-kiem, hồ sơ sandbox, tep_root            — Task 6
  chu/cai_dat_tho.py            # (sửa) tài nguyên qua sổ, sudoers D22                                            — Task 6
  chu/kiem_cach_ly.py           # (sửa) tram-kiem từ doc_principal_kiem, boc = PrincipalKiem.boc_lenh            — Task 6
  chu/lenh_tho.py               # (sửa) bỏ --tram-kiem, bắt LoiCaiDat (Task 6); go-cai-dat-tho (Task 8, chèn theo mốc)
  giao_viec/kiem_goc.py         # (mới) kiem_thu_muc_goc, kiem_sudoers_khong_root                                 — Task 7
  chu/go_cai_dat_tho.py         # (mới) lap_ke_hoach_go, go, lenh_go, lenh_cli                                    — Task 8
  chu/nhat_ky.py                # (mới, r47) khoa, cat_duoi, ghi_het, dong_bo — journal an toàn (R4)              — Task 6
  giao_viec/lich_tram_kiem.py   # (mới, r47) don_cron, don_at, ra (C01)                                            — Task 11
  giao_viec/launchd_kiem.py     # (mới, r47) nền + vân tay launchd, don_launchd, chup, lenh_chup_nen (C01)        — Task 11
  giao_viec/don_tram_kiem.py    # (mới, r47) don_sach: vòng đời cách ly tram-kiem (C01)                           — Task 11
  giao_viec/ban_chep.py, kiem_lai.py, principal_kiem.py, noi_that.py, kiem_san_sang.py  # (sửa) C01 — Task 11
  giao_viec/nghiem_thu_kiem.py, kich_ban_nghiem_thu.py  # (mới, r47) harness S6 (Q03)                           — Task 12
  giao_viec/lenh.py             # (sửa) chup-nen-lich, nghiem-thu-kiem                                            — Task 12
tests/
  test_quyen_kiem.py (1) · test_ban_chep.py (3) · test_principal_kiem_hop_nhat.py (5) · test_ban_chep_git.py (10)
  he_gia.py (công cụ), test_cai_dat_tho_kiem.py, test_so_cai_tho.py, test_dinh_danh_cai.py, test_cai_nha_tho.py (6) · test_kiem_goc.py (7)
  test_go_cai_dat_tho.py, test_go_cai_lai.py (8) · tram_kiem_gia.py (công cụ), test_don_tram_kiem.py, test_don_tep_tram_kiem.py,
  test_ban_chep_nha.py (11) · test_nghiem_thu_kiem.py (12)
  (sửa) test_kiem_lai.py, test_kiem_lai_principal.py, test_tick_hai_pha.py, test_noi_giao_viec.py, test_luong_giao.py (3)
        test_cau_hinh_giao_viec.py, test_giao_kiem.py, test_noi_giao_viec.py (5) · test_chu_tho.py, test_tho_lenh_chay.py (6)
        test_giao_kiem.py (7) · test_ban_chep.py (10) · test_principal_kiem_hop_nhat.py, test_kiem_lai_principal.py,
        test_tick_hai_pha.py, test_noi_giao_viec.py, test_giao_kiem.py (11)
```

Ranh giới: chuỗi phía cài đặt của `tram-kiem` ở `tram/tho/quyen_kiem.py`; bản chép ở `tram/giao_viec/{cay_kiem,ban_chep,repo_ban_chep}.py` (không biết sudo — chỉ nhận `boc`); đọc cấu hình ở `tram/cau_hinh/`; cài/gỡ có sổ ở `tram/chu/`. Công cụ test là module cấp cao trong `tests/` (pytest `prepend`): `test_ban_chep.py` (và `test_ban_chep_git.py` của Task 10) import `ban_chep`, `chay`, `m` từ `test_kiem_lai_principal` (bản đã sửa ở Task 3); `test_cai_dat_tho_kiem.py`, `test_so_cai_tho.py`, `test_go_cai_dat_tho.py`, `test_chu_tho.py` import `HeGia` từ `tests/he_gia.py` (Task 6).

## Chuẩn bị (người điều phối)

```bash
cd "/Users/dai-ca/Developer/Ben Station"
git status --short            # chỉ được có .beads/interactions.jsonl, .DS_Store — không đụng
git log --oneline -1          # tại hoặc sau 793facb (đã ghép T2, T4, R3)
uv run pytest -q              # N₀ = 2100 (main 793facb)
```

**Kiểm mốc trước Task 1** — mục nào sai thì dừng, báo Em/Đại ca, không tự sửa:

```bash
grep -c '^            trao_quyen(wt)  ' tram/giao_viec/kiem_lai.py                                    # 1
grep -c 'trao_quyen=bo.trao_quyen, kill=bo.kill)' tram/giao_viec/tick_pipeline.py                   # 1
grep -c 'trao_quyen=pk.trao if pk and pk.trao_quyen else None' tram/giao_viec/noi_that.py             # 1
grep -c '^def bo_qua_loi' tram/chu/cai_dat.py                                                         # 1 (T4 đã ghép)
grep -c '^def them_lenh_chu_tho(chu) -> None:$' tram/chu/lenh_tho.py                                  # 1
ls tram/tho/quyen_kiem.py tram/cau_hinh/principal_kiem.py tram/giao_viec/ban_chep.py 2>/dev/null      # không in gì
```

**Mỗi task một worktree**, tạo từ `main` **sau khi đã ghép mọi task của đợt trước**:

```bash
N=5   # số task
git worktree add .worktrees/3c-t$N -b 3c/t$N main
cd .worktrees/3c-t$N && uv sync && uv run pytest -q    # kỳ vọng: số "sau đợt trước" trong Sơ đồ đợt chạy
```

Cuối mỗi task: người thực thi commit trong worktree của mình; người điều phối kiểm (mọi dòng thêm có nguyên văn trong plan; số test đúng kỳ vọng) rồi `git merge --no-ff 3c/t$N` vào `main` (không push).

Mã: file **mới** cho nguyên văn đầy đủ; file **có sẵn** cho bản vá `git apply` (unified diff sinh trên bản sao `main 4a907cc` sau các đợt trước — bản r47: T6, T8, T11, T12 sinh trên `main 793facb` sau các đợt trước; mọi bản vá đều `git apply --check` sạch trên `793facb`, chạy từ gốc worktree) hoặc **script chèn theo mốc** (Task 8, `tram/chu/lenh_tho.py`). Áp bản vá: lưu khối `diff` ra file rồi `git apply --check <file> && git apply <file>`; lỗi → `git apply --3way <file>`; vẫn lỗi → dừng, báo người điều phối.

Dòng ghi công trong lệnh commit: thay `<model đang thực thi>` bằng đúng tên model của người thực thi task đó.

---

### Task 1: Chuỗi phía cài đặt của `tram-kiem` — `thu_muc_kiem`, dòng sudoers D22, hồ sơ sandbox

**Độ khó:** `de` · **Đợt:** 1 · **Song song với:** Task 3 · **Phải xong trước:** — (chỉ cần `main` N₀)

**Files:**
- Create: `tram/tho/quyen_kiem.py`
- Test: `tests/test_quyen_kiem.py` (mới)

**Interfaces:**
- Consumes: `SANDBOX_EXEC`, `USER_RE`, `Principal` (`tram/tho/principal.py`), `ho_so_sandbox` (`tram/tho/sandbox.py`).
- Produces: `THU_MUC_CAI = Path("/usr/local/tram")`, `HO_SO_KIEM = THU_MUC_CAI / "tram-kiem.sb"`, `KY_TU_DUONG`, `goc_hop_le(p: Path) -> str` (ValueError), `dong_sudoers_kiem(*, tram: str, tram_kiem: str, co_che: str) -> str` (ValueError khi tên sai/trùng hoặc cơ chế lạ), `ho_so_tram_kiem(*, tram_home_tram: Path, nha_quan_ly: Path, goc: Path, cong: list[int]) -> str`.

- [ ] **Step 1: Viết test thất bại**

`tests/test_quyen_kiem.py` (mới):

```python
"""Chuỗi phía cài đặt của `tram-kiem` theo D22 (lát 3c): `thu_muc_kiem`, dòng sudoers (runas CHỈ tram-kiem, không
root), hồ sơ sandbox cố định. Chỉ kiểm chuỗi — KHÔNG sudo, không visudo."""
import fnmatch
from pathlib import Path

import pytest

from tram.tho.principal import Principal
from tram.tho.quyen_kiem import HO_SO_KIEM, dong_sudoers_kiem, goc_hop_le, ho_so_tram_kiem


def test_goc_phai_la_duong_dan_that(tmp_path):
    (tmp_path / "that").mkdir()
    (tmp_path / "lien-ket").symlink_to(tmp_path / "that")
    goc = tmp_path.resolve()
    assert goc_hop_le(goc / "that") == str(goc / "that")
    for sai in (Path("tuong/doi"), Path("/"), goc / "lien-ket", goc / "a b", Path(f"{goc}/that/../that"),
                Path(f"{goc}/x'y"), Path(f"{goc}/x,y"), Path(f'{goc}/x"y')):
        with pytest.raises(ValueError):
            goc_hop_le(sai)


def _khop(dong: str, argv: list[str]) -> bool:
    """Mô phỏng khớp lệnh sudoers: phần sau `NOPASSWD:SETENV:` so với argv SAU `--` của `sudo` (fnmatch: `*` khớp cả
    `/` và dấu cách — đúng như sudoers)."""
    mau = dong.split("NOPASSWD:SETENV: ", 1)[1]
    lenh = argv[argv.index("--") + 1:]
    return mau == "ALL" or fnmatch.fnmatchcase(" ".join(lenh), mau)


def test_co_che_user_chi_runas_tram_kiem_khong_root():
    dong = dong_sudoers_kiem(tram="hung", tram_kiem="tram-kiem", co_che="user")
    assert dong == "hung ALL=(tram-kiem) NOPASSWD:SETENV: ALL" and "root" not in dong


def test_co_che_sandbox_ghim_tien_to_ho_so_co_dinh():
    dong = dong_sudoers_kiem(tram="hung", tram_kiem="tram-kiem", co_che="sandbox")
    assert dong == f"hung ALL=(tram-kiem) NOPASSWD:SETENV: /usr/bin/sandbox-exec -f {HO_SO_KIEM} *"
    p = Principal("sandbox", "tram-kiem", HO_SO_KIEM)
    for argv in (["/usr/bin/tar", "-x", "-f", "-", "-C", "/k/g-1"], ["/bin/rm", "-rf", "/k/g-1"], ["php", "a b"]):
        assert _khop(dong, p.boc(argv))
    assert not _khop(dong, Principal("user", "tram-kiem").boc(["/bin/rm", "-rf", "/k"]))     # bỏ sandbox: từ chối
    assert not _khop(dong, Principal("sandbox", "tram-kiem", Path("/tmp/x.sb")).boc(["/bin/sh"]))  # hồ sơ khác: từ chối


@pytest.mark.parametrize("kw", [dict(tram="hung", tram_kiem="hung", co_che="user"),
                                dict(tram="hung", tram_kiem="Tram Kiem", co_che="user"),
                                dict(tram="hung", tram_kiem="tram-kiem", co_che="root")])
def test_sai_dang_la_loi(kw):
    with pytest.raises(ValueError):
        dong_sudoers_kiem(**kw)


def test_ho_so_sandbox_tram_kiem_cam_kho_tram_va_quan_ly(tmp_path):
    goc = tmp_path.resolve()
    hs = ho_so_tram_kiem(tram_home_tram=Path("/Users/dai-ca/.tram"), nha_quan_ly=Path("/Users/tram-tho"),
                         goc=goc, cong=[7700, 3306])
    assert '(deny file-read* file-write* (subpath "/Users/dai-ca/.tram"))' in hs
    assert '(deny file-read* file-write* (subpath "/Users/tram-tho/.tram"))' in hs
    assert f'(allow file-read* file-write* (subpath "{goc}"))' in hs
    assert '(remote tcp "*:7700")' in hs and '(remote tcp "*:3306")' in hs and "com.apple.securityd" in hs
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_quyen_kiem.py -q`
Expected: FAIL — `1 error` (`ModuleNotFoundError: No module named 'tram.tho.quyen_kiem'`)

- [ ] **Step 3: Viết mã**

`tram/tho/quyen_kiem.py` (mới):

```python
"""Principal kiểm lại `tram-kiem` theo D22 (lát 3c; spec 3 §7.3 mục 5, spec 4 §6.2 bước 1) — KHÔNG root lúc chạy.

`tram-kiem` tự sở hữu bản chép kiểm dưới `thu_muc_kiem` (trạm `git archive` rồi đưa qua stdin cho `tram-kiem` tự
`tar -x`, tự dọn). Tài khoản trạm chỉ được chạy lệnh DƯỚI `tram-kiem` qua sudo — không có dòng sudoers nào chạy root,
không helper, không ACL/chmod. File này giữ chuỗi phía cài đặt: kiểm `thu_muc_kiem`, dòng sudoers, hồ sơ sandbox.

Sudoers KHÔNG chặn được lệnh tuỳ ý dưới `tram-kiem`, và chặn cũng không thêm an toàn: kiểm lại CHÍNH LÀ chạy mã agent
viết dưới `tram-kiem` (`vendor/bin/phpunit` của commit là chương trình tuỳ ý). Ranh giới thật là danh tính đích:
chỉ `tram-kiem` (không root, không user khác), user không credential, không đọc kho trạm. Cơ chế `sandbox` ghim thêm
tiền tố argv cố định `sandbox-exec -f HO_SO_KIEM` — mọi lệnh dưới `tram-kiem` nằm trong hồ sơ cố định do root giữ."""
from pathlib import Path

from tram.tho.principal import SANDBOX_EXEC, USER_RE
from tram.tho.sandbox import ho_so_sandbox

THU_MUC_CAI = Path("/usr/local/tram")                 # chỉ dùng cho cơ chế sandbox: hồ sơ root:wheel 0644
HO_SO_KIEM = THU_MUC_CAI / "tram-kiem.sb"
KY_TU_DUONG = frozenset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._/-")


def goc_hop_le(p: Path) -> str:
    """`thu_muc_kiem` dùng được: tuyệt đối, đã là đường dẫn thật (không symlink, không `..`), chỉ ký tự an toàn
    (nhúng vào hồ sơ sandbox và lệnh cài)."""
    s = str(p)
    if not s.startswith("/") or s == "/" or set(s) - KY_TU_DUONG or str(Path(s).resolve()) != s:
        raise ValueError(f"thu_muc_kiem {s!r}: cần đường dẫn tuyệt đối THẬT (không symlink, không `..`), "
                         "chỉ gồm chữ, số, `._/-`")
    return s


def dong_sudoers_kiem(*, tram: str, tram_kiem: str, co_che: str) -> str:
    """MỘT dòng cho tài khoản trạm: runas CHỈ `tram_kiem`. `SETENV` cần cho `--preserve-env=` của `Principal.boc`
    (đích yếu quyền hơn trạm — biến môi trường không nâng quyền). Cơ chế `sandbox`: ghim tiền tố hồ sơ cố định."""
    if not USER_RE.fullmatch(tram) or not USER_RE.fullmatch(tram_kiem) or tram == tram_kiem:
        raise ValueError("tên user không hợp lệ (tram-kiem phải khác tài khoản trạm)")
    if co_che == "user":
        return f"{tram} ALL=({tram_kiem}) NOPASSWD:SETENV: ALL"
    if co_che == "sandbox":
        return f"{tram} ALL=({tram_kiem}) NOPASSWD:SETENV: {SANDBOX_EXEC} -f {HO_SO_KIEM} *"
    raise ValueError("co_che: user | sandbox")


def ho_so_tram_kiem(*, tram_home_tram: Path, nha_quan_ly: Path, goc: Path, cong: list[int]) -> str:
    """Hồ sơ sandbox của `tram-kiem` (cơ chế `sandbox`): cấm kho trạm, thư mục tiến trình quản lý thợ, Keychain,
    cổng tram-api/DB nghiệp vụ; mở lại `thu_muc_kiem`. Cài root:wheel 0644 tại `HO_SO_KIEM` — tram-kiem chỉ đọc."""
    return ho_so_sandbox(cam=[tram_home_tram, nha_quan_ly / ".tram"], cam_ghi=[], cho_ghi=[Path(goc_hop_le(goc))],
                         cong_cam=cong)
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_quyen_kiem.py -q`
Expected: `7 passed`

Run: `uv run pytest -q`
Expected: `N₀ + 7 passed` (2107 — r47, N₀ = 2100)

- [ ] **Step 5: Commit**

```bash
git add tram/tho/quyen_kiem.py tests/test_quyen_kiem.py
git commit -m "feat(tho): chuỗi cài đặt tram-kiem theo D22 — thu_muc_kiem, sudoers chỉ runas tram-kiem, hồ sơ sandbox (lát 3c, bs-urj.13)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

> **Task 2 — ĐÃ CODE 15/10 (D21), ghép `main` `2d21bd7`.** Nội dung dưới đây giữ nguyên văn để tham chiếu; KHÔNG giao lại.

### Task 2: Trao quyền phía thợ không đi theo symlink

**Độ khó:** `de` · **Đợt:** 1 · **Song song với:** Task 1, 3, 4 · **Phải xong trước:** —

**Files:**
- Modify: `tram/tho/principal_khe.py` (`lenh_trao_quyen`, thêm `FIND`)
- Modify: `tests/test_kiem_cong.py` (`test_lenh_trao_quyen_acl_cho_principal`), `tests/test_tho_chuan_bi.py` (`test_principal_co_user_thi_trao_quyen_ghi`) — khẳng định cũ đọc argv `chmod -R`
- Test: `tests/test_trao_quyen_symlink.py` (mới)

**Interfaces:**
- Consumes: `QUYEN_GHI`.
- Produces: `FIND = "/usr/bin/find"`; `lenh_trao_quyen(*duong, user, thu=False) -> list[list[str]]` — mỗi phần tử `[FIND, str(d), "(", "-type", "d", "-o", "-type", "f", ")", "-exec", "/bin/chmod", "+a" | "-a", f"user:{user} allow {QUYEN_GHI}", "{}", "+"]`. Chữ ký giữ nguyên; `chuan_bi`/`don_phieu` không sửa.

- [ ] **Step 1: Viết test thất bại**

`tests/test_trao_quyen_symlink.py` (mới):

```python
"""Trao quyền ghi worktree cho principal phía thợ (3a-2 G20; sửa ở lát 3c): `chmod -R +a` của macOS ĐI THEO symlink,
nên lệnh phải duyệt bằng `find` (không theo symlink). Test thật trên macOS cấp ACL cho CHÍNH user đang chạy (vô hại,
xoá cùng `tmp_path`) — không sudo, không user khác."""
import getpass
import subprocess
import sys

import pytest

from tram.tho.principal_khe import FIND, QUYEN_GHI, lenh_trao_quyen


def test_lenh_duyet_bang_find_chi_thu_muc_va_file_thuong(tmp_path):
    assert lenh_trao_quyen(tmp_path, user="tram-k-1") == [[
        FIND, str(tmp_path), "(", "-type", "d", "-o", "-type", "f", ")", "-exec", "/bin/chmod", "+a",
        f"user:tram-k-1 allow {QUYEN_GHI}", "{}", "+"]]


@pytest.mark.skipif(sys.platform != "darwin", reason="ACL macOS")
def test_that_khong_dat_acl_len_dich_cua_symlink(tmp_path):
    wt, ngoai, toi = tmp_path / "wt", tmp_path / "ngoai", getpass.getuser()
    (wt / "a").mkdir(parents=True)
    (wt / "a" / "x").write_text("x")
    ngoai.mkdir()
    (ngoai / "token").write_text("bí mật của tiến trình quản lý")
    (wt / "lk").symlink_to(ngoai / "token")
    (wt / "lkdir").symlink_to(ngoai)
    acl = lambda p: subprocess.run(["/bin/ls", "-led", str(p)], capture_output=True, text=True).stdout
    for lenh in lenh_trao_quyen(wt, user=toi):
        subprocess.run(lenh, check=True, capture_output=True)
    assert f"user:{toi} allow" in acl(wt / "a" / "x") and f"user:{toi} allow" in acl(wt)
    assert "allow" not in acl(ngoai / "token") and "allow" not in acl(ngoai)
    for lenh in lenh_trao_quyen(wt, user=toi, thu=True):
        subprocess.run(lenh, check=True, capture_output=True)
    assert "allow" not in acl(wt / "a" / "x")
```

`tests/test_kiem_cong.py`, `tests/test_tho_chuan_bi.py` (sửa — bản vá):

```diff
diff --git a/tests/test_kiem_cong.py b/tests/test_kiem_cong.py
index f4ae920..1247481 100644
--- a/tests/test_kiem_cong.py
+++ b/tests/test_kiem_cong.py
@@ -31,9 +31,10 @@ def test_principal_sandbox_co_ho_so_rieng_cua_khe(tmp_path):
 
 def test_lenh_trao_quyen_acl_cho_principal(tmp_path):
     ds = lenh_trao_quyen(tmp_path / "wt", tmp_path / "kho" / ".git" / "worktrees" / "hr-1", user="tram-k-1")
-    assert ds[0][:3] == ["/bin/chmod", "-R", "+a"] and ds[0][3].startswith("user:tram-k-1 allow list,add_file")
+    assert ds[0][:2] == ["/usr/bin/find", str(tmp_path / "wt")] and ds[0][10:12] == ["/bin/chmod", "+a"]
+    assert ds[0][12].startswith("user:tram-k-1 allow list,add_file") and "-R" not in ds[0]
     assert len(ds) == 2 and all(".git/config" not in " ".join(x) for x in ds)
-    assert lenh_trao_quyen(tmp_path, user="tram-k-1", thu=True)[0][2] == "-a"
+    assert lenh_trao_quyen(tmp_path, user="tram-k-1", thu=True)[0][11] == "-a"
 
 
 def test_dang_nhap_chay_lenh_trang_thai_duoi_principal(tmp_path):
diff --git a/tests/test_tho_chuan_bi.py b/tests/test_tho_chuan_bi.py
index 6753661..eabfd8d 100644
--- a/tests/test_tho_chuan_bi.py
+++ b/tests/test_tho_chuan_bi.py
@@ -39,8 +39,9 @@ def test_principal_co_user_thi_trao_quyen_ghi(tmp_path, monkeypatch):
     m.nc.chay_lenh = lambda argv, **kw: da.append(argv)
     k, so, hop, tt = lay_phieu(m)
     pc = chuan_bi(m.nc, k, so, hop, tt)
-    assert [a[-1] for a in da] == [str(pc.wt), git(pc.wt, "rev-parse", "--absolute-git-dir"), str(pc.thu_muc)]
-    assert all(a[:3] == ["/bin/chmod", "-R", "+a"] and "user:tram-k-b-claude-1 allow" in a[3] for a in da)
+    assert [a[1] for a in da] == [str(pc.wt), git(pc.wt, "rev-parse", "--absolute-git-dir"), str(pc.thu_muc)]
+    assert all(a[0] == "/usr/bin/find" and a[10:12] == ["/bin/chmod", "+a"] and "user:tram-k-b-claude-1 allow" in a[12]
+               for a in da)
 
 
 def test_khong_chuan_bi_duoc_tra_ly_do(tmp_path, monkeypatch):
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_trao_quyen_symlink.py -q`
Expected: FAIL — `1 error` (`ImportError: cannot import name 'FIND' from 'tram.tho.principal_khe'`)

Run: `uv run pytest tests/test_kiem_cong.py tests/test_tho_chuan_bi.py -q`
Expected: FAIL — `2 failed, 9 passed`

- [ ] **Step 3: Viết mã**

`tram/tho/principal_khe.py` (sửa — bản vá):

```diff
diff --git a/tram/tho/principal_khe.py b/tram/tho/principal_khe.py
index 7223c1d..b534368 100644
--- a/tram/tho/principal_khe.py
+++ b/tram/tho/principal_khe.py
@@ -9,6 +9,7 @@ from tram.tho.cau_hinh import CauHinhTho, KheCauHinh
 from tram.tho.principal import Principal, doc_principal
 from tram.tho.sandbox import ghi_ho_so, ho_so_sandbox
 
+FIND = "/usr/bin/find"
 QUYEN_GHI = ("list,add_file,search,delete,add_subdirectory,delete_child,readattr,writeattr,readextattr,writeextattr,"
              "readsecurity,file_inherit,directory_inherit")
 
@@ -31,5 +32,8 @@ def principal_cua(ch: CauHinhTho, k: KheCauHinh, *, goc: Path, goc_wt: Path, wt:
 def lenh_trao_quyen(*duong: Path, user: str, thu: bool = False) -> list[list[str]]:
     """Mở (`thu=True`: thu lại) quyền ghi cho principal trên từng thư mục: worktree, metadata worktree
     `.git/worktrees/<tên>` (`git rev-parse --absolute-git-dir`), thư mục hàng đợi của phiếu. KHÔNG mở `.git/config`,
-    `.git/hooks` của kho; objects/ref nhánh của kho chung — S6 chốt cách mở hẹp nhất."""
-    return [["/bin/chmod", "-R", "-a" if thu else "+a", f"user:{user} allow {QUYEN_GHI}", str(d)] for d in duong]
+    `.git/hooks` của kho; objects/ref nhánh của kho chung — S6 chốt cách mở hẹp nhất.
+    Lát 3c: duyệt bằng `find` (không đi theo symlink, chỉ thư mục/file thường) — `chmod -R +a` của macOS ĐI THEO
+    symlink kể cả với `-P`, nên symlink agent commit trỏ ra file của tiến trình quản lý sẽ nhận ACL."""
+    return [[FIND, str(d), "(", "-type", "d", "-o", "-type", "f", ")", "-exec", "/bin/chmod", "-a" if thu else "+a",
+             f"user:{user} allow {QUYEN_GHI}", "{}", "+"] for d in duong]
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_trao_quyen_symlink.py tests/test_kiem_cong.py tests/test_tho_chuan_bi.py -q`
Expected: `13 passed`

Run: `uv run pytest -q`
Expected: `N₀ + 2 passed`

- [ ] **Step 5: Commit**

```bash
git add tram/tho/principal_khe.py tests/test_trao_quyen_symlink.py tests/test_kiem_cong.py tests/test_tho_chuan_bi.py
git commit -m "fix(tho): trao quyền ghi cho principal bằng find, không đi theo symlink (chmod -R +a của macOS theo symlink) (lát 3c)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 3: Kiểm lại trên bản chép do `tram-kiem` sở hữu — `git archive` → `tar -x`, môi trường qua stdin, tự dọn

**Độ khó:** `kho` · **Đợt:** 1 · **Song song với:** Task 1 · **Phải xong trước:** — (chỉ cần `main` N₀)

**Files:**
- Create: `tram/giao_viec/cay_kiem.py`, `tram/giao_viec/ban_chep.py`
- Modify: `tram/giao_viec/kiem_lai.py` (bỏ worktree; `trao_quyen` → `don_sach`), `tram/giao_viec/bo.py` (trường `trao_quyen` → `don_sach`), `tram/giao_viec/tick_pipeline.py` (truyền `don_sach`), `tram/giao_viec/noi_that.py` (`don_sach=None` tạm — Task 5 nối)
- Modify: `tests/test_kiem_lai_principal.py` (`chay` nhận `don_sach`, `boc`; 3 test `trao_quyen` → `don_sach`; thêm `ban_chep`), `tests/test_tick_hai_pha.py`, `tests/test_noi_giao_viec.py`, `tests/test_kiem_lai.py`, `tests/test_luong_giao.py` (khẳng định cũ đọc `kiem/g-1` của worktree)
- Test: `tests/test_ban_chep.py` (mới)

**Interfaces:**
- Consumes: `loi_dich`, `LoiMoiTruongKiem` (`tram/kiem/moi_truong.py`), `tram_home`; fixture `m`, helper `chay` của `tests/test_kiem_lai_principal.py`.
- Produces:
  - `tram/giao_viec/cay_kiem.py`: `GIT`, `THUOC_TINH = "* -export-ignore -export-subst\n"`, `loi_dich_trong_cay(kho, commit, dich) -> str | None`, `chuan_bi_thuoc_tinh(kho)`, `nguon_archive(kho, commit) -> Popen`, `tar_mot_tep(dich, du_lieu) -> bytes`.
  - `tram/giao_viec/ban_chep.py`: `LoiBanChep(OSError)`, `KiemLaiDangBan(LoiBanChep)`, `giu_khoa(p=None)` (context manager, không chờ), `ten_ban_chep(giao_id) -> str`, `chep_ban(kho, commit, wt, *, boc)`, `nhan_moi_truong(kho, commit, wt, nguon, dich, *, boc)` (LoiMoiTruongKiem), `don_ban(wt, *, boc, don_sach=None)`, `TAR_NHAN`.
  - `kiem_lai(…, don_sach: Callable[[], None] | None = None, kill=…)` — thay `trao_quyen`. Chép xong mới chạy lệnh; `don_sach` trước khi chép và trong `don_ban`; `don_ban` lỗi → ném, KHÔNG trả `KetQuaKiemLai`. `BoGiaoViec.don_sach`; `day_pipeline._kiem_lai` truyền `don_sach=bo.don_sach`.
- Ghi chú đợt: từ lúc ghép Task 3 tới lúc ghép Task 5, `dung_bo_that` truyền `don_sach=None` (chưa có `PrincipalKiem.don_sach`). `giao_viec.bat` vẫn phải `false` tới sau S6 nên không có kiểm lại thật nào chạy trong khoảng này.

- [ ] **Step 1: Viết test thất bại**

`tests/test_ban_chep.py` (mới):

```python
"""Bản chép kiểm do `tram-kiem` sở hữu (D22, lát 3c) — các ca F01 còn áp dụng: đổi cây sau khi kiểm, symlink trong
archive, tiến trình tram-kiem tái sinh, dọn lỗi thì fail-closed, hai lần kiểm lại đồng thời. `git archive`, `tar`,
`rm` THẬT dưới user đang chạy test (`boc` đồng nhất thay cho `sudo -u tram-kiem`) trong `tmp_path` — không sudo."""
import os
import shutil
from pathlib import Path

import pytest

from kho_kiem_gia import dung_kho
from test_kiem_lai_principal import ban_chep, chay, m  # noqa: F401 — fixture `m` dùng chung
from tram.cau_hinh.du_an import DuAn, MoiTruongKiem
from tram.giao_viec.ban_chep import KiemLaiDangBan, LoiBanChep, chep_ban, giu_khoa, nhan_moi_truong
from tram.giao_viec.git_kiem import fetch
from tram.kiem.moi_truong import LoiMoiTruongKiem

KIEM = 'test -f tests/a.txt && test ! -e .git && grep -q "Format:" v.txt && grep -q DB_DATABASE=test .env.testing\n'


def test_ban_chep_dung_commit_khong_git_khong_bi_export_ignore_giau(m):
    (m[0].kho / "kiem.sh").write_text("exit 1\n")              # thư mục làm việc của kho kiểm bị sửa: không ảnh hưởng
    kq = chay(m, {"kiem.sh": KIEM, "tests/a.txt": "x", "v.txt": "$Format:%H$\n",
                  ".gitattributes": "/tests export-ignore\nv.txt export-subst\n"})
    assert kq.dat and ban_chep(m) == []


def test_cay_bi_doi_sau_khi_chep_thi_moi_truong_khong_ra_ngoai(tmp_path):
    k = dung_kho(tmp_path)
    sha = k.day("tram/hr-1", {"config/app.php": "x"}, tu=k.main)
    fetch(k.kho)
    wt, ngoai, env = tmp_path / "kiem" / "g-1-ab", tmp_path / "ngoai", tmp_path / "env.testing"
    ngoai.mkdir()
    env.write_text("DB_DATABASE=test\n")
    chep_ban(k.kho, sha, wt, boc=lambda a: a)
    shutil.rmtree(wt / "config")
    (wt / "config").symlink_to(ngoai)                          # tiến trình lạ đổi cây SAU khi chép
    with pytest.raises(LoiMoiTruongKiem):
        nhan_moi_truong(k.kho, sha, wt, env, "config/.env.testing", boc=lambda a: a)
    assert list(ngoai.iterdir()) == []


def test_symlink_trong_archive_khong_bi_di_theo(m):
    ngoai = m[2] / "ngoai"
    (ngoai / "thu-muc").mkdir(parents=True)
    (ngoai / "bi-mat").write_text("goc")
    (ngoai / "thu-muc" / "x").write_text("goc")
    os.symlink(ngoai / "bi-mat", m[0].dev / "lk")
    os.symlink(ngoai / "thu-muc", m[0].dev / "lkdir")
    assert chay(m, {"kiem.sh": "test -L lk && test -L lkdir\n"}).dat and ban_chep(m) == []
    assert (ngoai / "bi-mat").read_text() == "goc" and (ngoai / "thu-muc" / "x").read_text() == "goc"
    os.symlink(ngoai / "thu-muc", m[0].dev / "config")             # đích môi trường đi qua symlink trong commit
    da = DuAn("hr-codex", Path("/r"), None, {}, moi_truong_kiem=MoiTruongKiem(m[2] / "env.testing",
                                                                            "config/.env.testing"))
    kq = chay((m[0], da, m[2]), {"kiem.sh": "exit 0\n"})
    assert kq.loi == "thieu-moi-truong-kiem" and sorted(os.listdir(ngoai / "thu-muc")) == ["x"]


def test_tien_trinh_tai_sinh_luc_don_thi_khong_tra_ket_qua(m):
    lan = []

    def don_sach():
        lan.append(1)
        if len(lan) == 2:
            raise LoiBanChep("tram-kiem vẫn còn tiến trình sau 5 lần giết")
    with pytest.raises(LoiBanChep, match="vẫn còn"):
        chay(m, {"kiem.sh": "exit 0\n"}, don_sach=don_sach)
    assert ban_chep(m) == []                                       # vẫn dọn thư mục, nhưng không trả kết quả


@pytest.mark.parametrize("hong", ["/bin/rm", "/usr/bin/tar"])
def test_tar_hoac_rm_loi_thi_fail_closed(m, hong):
    boc = lambda a: ["/usr/bin/false"] if a[0] == hong else a
    with pytest.raises(LoiBanChep):
        chay(m, {"kiem.sh": f"touch {m[2]}/DA_CHAY\n"}, boc=boc)
    assert not (m[2] / "DA_CHAY").exists() or hong == "/bin/rm"
    assert (ban_chep(m) == []) == (hong == "/usr/bin/tar")


def test_hai_lan_kiem_lai_dong_thoi(m):
    with giu_khoa():
        with pytest.raises(KiemLaiDangBan):
            chay(m, {"kiem.sh": f"touch {m[2]}/DA_CHAY\n"})
    assert not (m[2] / "DA_CHAY").exists() and ban_chep(m) == []
    assert chay(m, {"kiem.sh": "exit 0\n"}).dat                       # nhả khoá → chạy được
```

`tests/test_kiem_lai_principal.py`, `tests/test_kiem_lai.py`, `tests/test_luong_giao.py`, `tests/test_noi_giao_viec.py`, `tests/test_tick_hai_pha.py` (sửa — bản vá):

```diff
diff --git a/tests/test_kiem_lai.py b/tests/test_kiem_lai.py
index f454837..b067843 100644
--- a/tests/test_kiem_lai.py
+++ b/tests/test_kiem_lai.py
@@ -33,7 +33,7 @@ def chay(m, tep, lenh, *, chay_lenh=True, da=None, cho=30):
 def test_dat_khi_moi_lenh_pass_va_co_moi_truong_kiem(m):
     kq = chay(m, {"kiem.sh": 'grep -q DB_DATABASE=test .env.testing && [ "$APP_ENV" = testing ]\n'}, ["sh kiem.sh"])
     assert kq.dat and kq.ket_qua[0]["ket_qua"] == "pass" and kq.digest_log[0].startswith("sha256:")
-    assert not (m[2] / "kiem" / "g-1").exists()                            # worktree kiểm đã dọn
+    assert list((m[2] / "kiem").iterdir()) == []                          # bản chép kiểm đã dọn (3c)
 
 
 def test_suite_bat_buoc_fail_du_lenh_khac_pass(m):
diff --git a/tests/test_kiem_lai_principal.py b/tests/test_kiem_lai_principal.py
index 1e94d90..0896674 100644
--- a/tests/test_kiem_lai_principal.py
+++ b/tests/test_kiem_lai_principal.py
@@ -1,13 +1,14 @@
-"""Kiểm lại dưới principal `tram-kiem` (spec 3 §7.3 mục 5; spec 4 §6.2 bước 1): worktree do trạm tạo, chép môi
-trường kiểm, RỒI mới trao quyền ghi, rồi mới chạy lệnh. Không chạy sudo thật — `trao_quyen` giả."""
+"""Kiểm lại dưới principal `tram-kiem` (spec 3 §7.3 mục 5; spec 4 §6.2 bước 1; lát 3c D22): `don_sach` (giết mọi
+tiến trình tram-kiem) TRƯỚC khi chép bản chép và TRƯỚC khi dọn. Không chạy sudo thật — `boc` đồng nhất, `don_sach`
+giả."""
 import os
-import subprocess
 from pathlib import Path
 
 import pytest
 
 from kho_kiem_gia import dung_kho
 from tram.cau_hinh.du_an import DuAn, MoiTruongKiem
+from tram.giao_viec.ban_chep import LoiBanChep
 from tram.giao_viec.git_kiem import fetch
 from tram.giao_viec.kiem_lai import kiem_lai
 from tram.kiem.chay_lenh import _kill_nhom
@@ -21,38 +22,42 @@ def m(tmp_path):
     return k, DuAn("hr-codex", Path("/r"), None, {}, moi_truong_kiem=MoiTruongKiem(env, ".env.testing")), tmp_path
 
 
-def chay(m, tep, *, lenh=("sh kiem.sh",), trao_quyen=None, chay_lenh=True, kill=_kill_nhom):
+def chay(m, tep, *, lenh=("sh kiem.sh",), don_sach=None, chay_lenh=True, kill=_kill_nhom, boc=lambda a: a):
     k, da, tmp = m
     sha = k.day("tram/hr-1", tep, tu=k.main)
     fetch(k.kho)
     return kiem_lai(k.kho, da, giao_id="g-1", commit=sha, lenh_kiem=list(lenh), lenh_cho_phep=["sh kiem.sh"],
-                    chay_lenh=chay_lenh, thu_muc=tmp / "kiem-ngoai", thu_muc_log=tmp / "log", boc=lambda a: a,
-                    env_goc=os.environ, trao_quyen=trao_quyen, kill=kill)
+                    chay_lenh=chay_lenh, thu_muc=tmp / "kiem-ngoai", thu_muc_log=tmp / "log", boc=boc,
+                    env_goc=os.environ, don_sach=don_sach, kill=kill)
 
 
-def test_trao_quyen_sau_moi_truong_kiem_truoc_lenh(m):
+def ban_chep(m) -> list[Path]:
+    return sorted((m[2] / "kiem-ngoai").iterdir()) if (m[2] / "kiem-ngoai").exists() else []
+
+
+def test_don_sach_truoc_khi_chep_va_truoc_khi_don(m):
     thay = []
 
-    def trao(wt: Path):
-        thay.append((wt, (wt / ".env.testing").is_file(), (wt / "DA_CHAY").exists()))
+    def don_sach():
+        thay.append([(p.name.startswith("g-1-"), (p / "DA_CHAY").exists()) for p in ban_chep(m)])
 
-    kq = chay(m, {"kiem.sh": "touch DA_CHAY\n"}, trao_quyen=trao)
-    assert kq.dat and thay == [(m[2] / "kiem-ngoai" / "g-1", True, False)]
+    kq = chay(m, {"kiem.sh": "touch DA_CHAY\n"}, don_sach=don_sach)
+    assert kq.dat and thay == [[], [(True, True)]] and ban_chep(m) == []
 
 
-def test_trao_quyen_loi_thi_nem_khong_chay_lenh_va_don_worktree(m):
-    def trao(wt: Path):
-        raise subprocess.CalledProcessError(1, ["trao"])
+def test_con_tien_trinh_tram_kiem_thi_khong_chep_khong_chay(m):
+    def don_sach():
+        raise LoiBanChep("tram-kiem còn 1 tiến trình")
 
-    with pytest.raises(subprocess.CalledProcessError):
-        chay(m, {"kiem.sh": f"touch {m[2]}/DA_CHAY\n"}, trao_quyen=trao)
-    assert not (m[2] / "DA_CHAY").exists() and not (m[2] / "kiem-ngoai" / "g-1").exists()
+    with pytest.raises(LoiBanChep):
+        chay(m, {"kiem.sh": f"touch {m[2]}/DA_CHAY\n"}, don_sach=don_sach)
+    assert not (m[2] / "DA_CHAY").exists() and ban_chep(m) == []
 
 
-def test_spike_va_cham_cam_khong_trao_quyen(m):
+def test_spike_va_cham_cam_khong_don_sach(m):
     goi = []
-    assert chay(m, {"docs/spikes/x.md": "kết luận"}, lenh=(), chay_lenh=False, trao_quyen=goi.append).dat
-    assert chay(m, {"package.json": "{}"}, trao_quyen=goi.append).loi == "dong-file-cau-hinh" and goi == []
+    assert chay(m, {"docs/spikes/x.md": "kết luận"}, lenh=(), chay_lenh=False, don_sach=lambda: goi.append(1)).dat
+    assert chay(m, {"package.json": "{}"}, don_sach=lambda: goi.append(1)).loi == "dong-file-cau-hinh" and goi == []
 
 def test_kiem_lai_truyen_kill_principal(m, monkeypatch):
     from types import SimpleNamespace
diff --git a/tests/test_luong_giao.py b/tests/test_luong_giao.py
index ae352a3..46f6340 100644
--- a/tests/test_luong_giao.py
+++ b/tests/test_luong_giao.py
@@ -112,6 +112,6 @@ def test_khoi_dong_lai_giua_kiem_lai_thi_vong_sau_kiem_lai_lai(tmp_path, tram_ho
     chuan_bi_code_xong(t, {"src/tom_tat.py": "x = 2\n", F: "x", "kiem.sh": "exit 0\n"})
     with pytest.raises(RuntimeError):
         chay_vong(KHOA_GIT, lambda: vong_git(t.bo))
-    assert loai(t, "kiem.lai") == [] and list((tram_home_tam / "kiem").iterdir()) == []
+    assert loai(t, "kiem.lai") == [] and list((tram_home_tam / "kiem").glob("*")) == []      # 3c: không còn bản chép
     assert chay_vong(KHOA_GIT, lambda: vong_git(t.bo))["kiem_lai"] == 1
     assert "kiem_lai" not in chay_vong(KHOA_GIT, lambda: vong_git(t.bo)) and len(loai(t, "kiem.lai")) == 1
diff --git a/tests/test_noi_giao_viec.py b/tests/test_noi_giao_viec.py
index 740204e..272c1b8 100644
--- a/tests/test_noi_giao_viec.py
+++ b/tests/test_noi_giao_viec.py
@@ -63,7 +63,7 @@ def test_dung_bo_that_noi_principal_va_bo_qua_du_an_hong(tmp_path, capsys):
     cg = CauHinhGiaoViec(bat=True, thu_muc_kiem=tmp_path / "k", principal_kiem=PK)
     bo = dung_bo_that(cg, tao_pt(tmp_path, {}).cau_hinh, thu_muc_du_an=tmp_path / "du-an")
     assert [d.ten for d in bo.cac_du_an()] == ["hr-x"] and "bỏ qua dự án hong" in capsys.readouterr().err
-    assert bo.boc(["sh", "kiem.sh"]) == [*PK.boc, "sh", "kiem.sh"] and bo.trao_quyen == PK.trao
+    assert bo.boc(["sh", "kiem.sh"]) == [*PK.boc, "sh", "kiem.sh"] and bo.don_sach is None      # 3c T5 nối
     assert bo.kill == PK.kill_nhom
     assert bo.thu_muc_kiem == tmp_path / "k" and bo.doc_beads is None
     assert bo.tao_bd(bo.cac_du_an()[0]).actor == "tram/giao-viec" and Path(bo.tao_bd(bo.cac_du_an()[0]).repo) == tmp_path
diff --git a/tests/test_tick_hai_pha.py b/tests/test_tick_hai_pha.py
index 03ceb69..1eebb44 100644
--- a/tests/test_tick_hai_pha.py
+++ b/tests/test_tick_hai_pha.py
@@ -59,13 +59,13 @@ def test_fetch_qua_han_chi_dem_loi_khong_chan_escalation(tmp_path, monkeypatch):
     assert (r["cong_viec"], r["loi"]) == (1, 1) and t.g.so_lan("tao") == 1
 
 
-def test_kiem_lai_dung_thu_muc_va_trao_quyen_cua_bo(tmp_path):
-    t = dung(tmp_path, bug(**GIU))
-    trao = []
-    t.bo.thu_muc_kiem, t.bo.trao_quyen = tmp_path / "kiem-ngoai", trao.append
+def test_kiem_lai_dung_thu_muc_va_don_sach_cua_bo(tmp_path):
+    t, goc = dung(tmp_path, bug(**GIU)), tmp_path / "kiem-ngoai"
+    don = []
+    t.bo.thu_muc_kiem, t.bo.don_sach = goc, lambda: don.append([p.name for p in goc.glob("*")])
     chuan_bi_code_xong(t, {"src/tom_tat.py": "x = 2\n", F: "x", "kiem.sh": "exit 0\n"})
-    assert vong_git(t.bo)["kiem_lai"] == 1 and trao == [tmp_path / "kiem-ngoai" / loai(t, "giao.nhan")[0].du_lieu[
-        "giao_id"]]
+    assert vong_git(t.bo)["kiem_lai"] == 1 and don[0] == [] and len(don[1]) == 1
+    assert don[1][0].startswith(loai(t, "giao.nhan")[0].du_lieu["giao_id"] + "-") and list(goc.iterdir()) == []
 
 
 def test_cot_3_nhanh_bi_day_ngoai_luong(tmp_path):
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_ban_chep.py tests/test_kiem_lai_principal.py tests/test_kiem_lai.py tests/test_luong_giao.py tests/test_noi_giao_viec.py tests/test_tick_hai_pha.py -q`
Expected: FAIL — `2 errors` (`ModuleNotFoundError: No module named 'tram.giao_viec.ban_chep'` khi nạp `test_ban_chep.py` và `test_kiem_lai_principal.py`)

- [ ] **Step 3: Viết mã**

`tram/giao_viec/cay_kiem.py` (mới):

```python
"""Cây của commit cho bản chép kiểm (D22, lát 3c) — mọi phép xét làm trên ĐỐI TƯỢNG GIT của kho kiểm (bất biến theo
SHA), không trên đĩa mà `tram-kiem` sửa được. `info/attributes` của kho kiểm vô hiệu `export-ignore`/`export-subst`
trong `.gitattributes` của commit (ưu tiên cao nhất theo gitattributes) — commit không giấu được file khỏi bản chép."""
import io
import subprocess
import tarfile
import time
from pathlib import Path

GIT = ("git", "-c", "core.hooksPath=/dev/null")
THUOC_TINH = "* -export-ignore -export-subst\n"


def _git(kho: Path, *args: str, **kw) -> subprocess.CompletedProcess:
    return subprocess.run([*GIT, "-C", str(kho), *args], capture_output=True, timeout=120, **kw)


def loi_dich_trong_cay(kho: Path, commit: str, dich: str) -> str | None:
    """Đích môi trường kiểm xét trên cây của commit: mọi thư mục cha là thư mục thật, đích (nếu có) là file thường —
    không symlink, thư mục hay submodule."""
    phan = dich.split("/")
    for i in range(1, len(phan) + 1):
        con, cuoi = "/".join(phan[:i]), i == len(phan)
        r = _git(kho, "ls-tree", "-z", commit, "--", con)
        if r.returncode != 0:
            return f"không đọc được cây của commit {commit[:12]}"
        dong = [x for x in r.stdout.split(b"\0") if x]
        if not dong:
            return None if cuoi else f"Thư mục đích không có trong commit: {con}"
        mode = dong[0].split(b" ", 1)[0]
        if not cuoi and mode != b"040000":
            return f"Đích {dich} đi qua {con} — không phải thư mục thật trong commit"
        if cuoi and mode not in (b"100644", b"100755"):
            return f"Đích {dich} trong commit là symlink/thư mục/submodule"
    return None


def chuan_bi_thuoc_tinh(kho: Path) -> None:
    p = Path(_git(kho, "rev-parse", "--git-path", "info/attributes", check=True, text=True).stdout.strip())
    p = p if p.is_absolute() else kho / p
    if not p.is_file() or p.read_text(encoding="utf-8") != THUOC_TINH:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(THUOC_TINH, encoding="utf-8")


def nguon_archive(kho: Path, commit: str) -> subprocess.Popen:
    """`git archive` của commit, stdout là ống — người gọi đóng ống và `wait()`."""
    chuan_bi_thuoc_tinh(kho)
    return subprocess.Popen([*GIT, "-C", str(kho), "archive", "--format=tar", commit], stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL)


def tar_mot_tep(dich: str, du_lieu: bytes) -> bytes:
    b = io.BytesIO()
    with tarfile.open(fileobj=b, mode="w") as t:
        ti = tarfile.TarInfo(dich)
        ti.size, ti.mode, ti.mtime = len(du_lieu), 0o600, int(time.time())
        t.addfile(ti, io.BytesIO(du_lieu))
    return b.getvalue()
```

`tram/giao_viec/ban_chep.py` (mới):

```python
"""Bản chép kiểm do `tram-kiem` SỞ HỮU (D22, lát 3c; spec 3 §7.3 mục 5, spec 4 §6.2 bước 1, 3) — không root, không ACL.

Trạm `git archive <commit>` từ kho kiểm, đưa qua stdin cho `tar -x` chạy DƯỚI `tram-kiem` (`boc`) vào một thư mục MỚI
dưới `thu_muc_kiem`; môi trường kiểm cũng qua stdin (tar một file); `tram-kiem` tự `rm -rf` khi xong. Mọi thao tác
trên cây đều dưới quyền `tram-kiem`, nên symlink/hardlink trong cây không với tới thứ gì `tram-kiem` vốn không với tới.
Cây kiểm KHÔNG có `.git`. Fail-closed:
- một lần kiểm lại một lúc trên máy (khoá `~/.tram/kiem-lai.khoa`, không chờ) — lần thứ hai ném `KiemLaiDangBan`;
- `don_sach` (giết mọi tiến trình `tram-kiem`, xác nhận không còn) chạy trước khi chép và trước khi dọn — lỗi → ném;
- dọn xong mà thư mục vẫn còn → ném `LoiBanChep`: kết quả kiểm lại KHÔNG được trả về."""
import fcntl
import os
import secrets
import subprocess
from collections.abc import Callable
from contextlib import contextmanager
from pathlib import Path

from tram.duong_dan import tram_home
from tram.giao_viec.cay_kiem import loi_dich_trong_cay, nguon_archive, tar_mot_tep
from tram.kiem.moi_truong import LoiMoiTruongKiem, loi_dich

TAR_NHAN = ("/usr/bin/tar", "-x", "-f", "-", "-C")
THOI_GIAN = 600
Boc = Callable[[list[str]], list[str]]


class LoiBanChep(OSError):
    """Không bảo đảm được bản chép sạch — không chạy lệnh, không công nhận kết quả (vòng tick đếm lỗi, thử lại)."""


class KiemLaiDangBan(LoiBanChep):
    """Đang có lần kiểm lại khác (hoặc `tram giao kiem`) giữ khoá."""


@contextmanager
def giu_khoa(p: Path | None = None):
    p = p or tram_home() / "kiem-lai.khoa"
    p.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(p, os.O_RDWR | os.O_CREAT, 0o600)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise KiemLaiDangBan("đang có lần kiểm lại khác chạy — thử lại vòng sau") from None
        yield
    finally:
        os.close(fd)


def ten_ban_chep(giao_id: str) -> str:
    """Tên MỚI mỗi lần (không dùng lại thư mục của lần trước)."""
    if not giao_id or "/" in giao_id or giao_id.startswith((".", "-")):
        raise ValueError(f"giao_id không dùng làm tên thư mục được: {giao_id!r}")
    return f"{giao_id}-{secrets.token_hex(4)}"


def _chay(argv: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(argv, capture_output=True, timeout=THOI_GIAN, **kw)


def chep_ban(kho: Path, commit: str, wt: Path, *, boc: Boc) -> None:
    """`tram-kiem` tạo `wt` MỚI (đã có → lỗi) rồi tự `tar -x` nội dung đúng commit từ stdin."""
    _chay(boc(["/bin/mkdir", "-p", str(wt.parent)]), check=True)
    _chay(boc(["/bin/mkdir", str(wt)]), check=True)
    nguon = nguon_archive(kho, commit)
    try:
        nhan = _chay(boc([*TAR_NHAN, str(wt)]), stdin=nguon.stdout)
    finally:
        nguon.stdout.close()
        ma = nguon.wait(timeout=THOI_GIAN)
    if ma or nhan.returncode:
        raise LoiBanChep(f"git archive (mã {ma}) | tar dưới tram-kiem (mã {nhan.returncode}) lỗi")


def nhan_moi_truong(kho: Path, commit: str, wt: Path, nguon: Path, dich: str, *, boc: Boc) -> None:
    """Môi trường kiểm vào bản chép QUA STDIN (tar một file, mode 0600) — không qua argv, trạm không ghi vào cây."""
    loi = loi_dich(dich) or loi_dich_trong_cay(kho, commit, dich)
    if loi is not None:
        raise LoiMoiTruongKiem(loi)
    if not nguon.is_file():
        raise LoiMoiTruongKiem(f"Không thấy file môi trường kiểm {nguon}")
    r = _chay(boc([*TAR_NHAN, str(wt)]), input=tar_mot_tep(dich, nguon.read_bytes()))
    if r.returncode:
        raise LoiMoiTruongKiem(f"tram-kiem không ghi được {dich} (tar mã {r.returncode})")


def don_ban(wt: Path, *, boc: Boc, don_sach: Callable[[], None] | None = None) -> None:
    """Giết mọi tiến trình `tram-kiem` rồi `tram-kiem` tự `rm -rf`. Còn sót (thư mục hoặc tiến trình) → ném."""
    loi = None
    if don_sach is not None:
        try:
            don_sach()
        except (OSError, subprocess.SubprocessError) as e:
            loi = e
    r = _chay(boc(["/bin/rm", "-rf", str(wt)]))
    if r.returncode or os.path.lexists(wt):
        raise LoiBanChep(f"không dọn được bản chép {wt} — không công nhận kết quả") from loi
    if loi is not None:
        raise loi
```

`tram/giao_viec/kiem_lai.py`, `tram/giao_viec/bo.py`, `tram/giao_viec/tick_pipeline.py`, `tram/giao_viec/noi_that.py` (sửa — bản vá):

```diff
diff --git a/tram/giao_viec/bo.py b/tram/giao_viec/bo.py
index 86ffbc0..87e3e90 100644
--- a/tram/giao_viec/bo.py
+++ b/tram/giao_viec/bo.py
@@ -44,10 +44,10 @@ class BoGiaoViec:
     boc: Callable[[list[str]], list[str]] | None = None   # principal `tram-kiem` (chờ S6); None: chưa kiểm lại
     env_goc: Mapping[str, str] = field(default_factory=lambda: dict(os.environ))
     doc_beads: DocBeads | None = None                     # 4a-2: bộ đệm beads của tram-api; None: đọc `bd` mỗi lần
-    trao_quyen: Callable[[Path], None] | None = None      # 4a-2: trao quyền ghi worktree kiểm cho `tram-kiem` (S6)
+    don_sach: Callable[[], None] | None = None            # 3c: giết mọi tiến trình `tram-kiem`, xác nhận sạch (D22)
     adr_hop_le: Callable[[DuAn, object], bool] = lambda da, b: False
     kill: Callable[[int, int], None] = _kill_nhom        # 3a-2: kill nhóm qua principal kiểm
-    thu_muc_kiem: Path | None = None                      # 4a-2: thư mục worktree kiểm lại; None: ~/.tram/kiem
+    thu_muc_kiem: Path | None = None                      # 4a-2: gốc bản chép kiểm lại; None: ~/.tram/kiem
 
     p4c: PhuThuoc4c = field(default_factory=PhuThuoc4c)
 
diff --git a/tram/giao_viec/kiem_lai.py b/tram/giao_viec/kiem_lai.py
index 721f700..7126d61 100644
--- a/tram/giao_viec/kiem_lai.py
+++ b/tram/giao_viec/kiem_lai.py
@@ -1,19 +1,22 @@
 """Kiểm lại của trạm (spec 4 §6.2 — "báo xong" khác "đã kiểm chứng"): gắn MỘT commit = SHA công bố của lượt.
 
-0. đường dẫn cấm từ gốc nhánh — TRƯỚC khi chạy bất cứ lệnh nào; 1. worktree kiểm tách rời tại commit trong kho
-kiểm; 2. spike tài liệu: dừng ở đây (không chạy lệnh); 3. chép môi trường kiểm; 4. chạy MỌI lệnh bắt buộc của phiếu
+0. đường dẫn cấm từ gốc nhánh — TRƯỚC khi chạy bất cứ lệnh nào; 1. bản chép kiểm tại commit trong kho kiểm
+(3c); 2. spike tài liệu: dừng ở đây (không chạy lệnh); 3. chép môi trường kiểm; 4. chạy MỌI lệnh bắt buộc của phiếu
 (khớp `lenh_cho_phep`, không shell, 15 phút/lệnh, kill cả nhóm); 5. đạt ⇔ mọi lệnh chạy được và pass.
-`boc` chọn principal `tram-kiem` (phần 3 §7.3 mục 5 — chờ S6); mã này không tự chạy dưới quyền trạm."""
+`boc` chọn principal `tram-kiem` (phần 3 §7.3 mục 5 — chờ S6); mã này không tự chạy dưới quyền trạm.
+Lát 3c (D22): bước 1, 3 chạy trên BẢN CHÉP do `tram-kiem` sở hữu (`ban_chep.py` — `git archive` → `tar -x` dưới
+`tram-kiem`, môi trường kiểm qua stdin, `tram-kiem` tự dọn; không `.git`, không worktree, không trao quyền). Một lần
+kiểm lại một lúc; `don_sach` trước khi chép và trước khi dọn; dọn không sạch → ném, KHÔNG trả kết quả."""
 from collections.abc import Callable, Mapping
 from dataclasses import dataclass
 from pathlib import Path
 
 from tram.cau_hinh.du_an import DuAn
 from tram.cau_hinh.lenh import khop_bat_ky
-from tram.giao_viec.git_kiem import tao_worktree, xoa_worktree
+from tram.giao_viec.ban_chep import chep_ban, don_ban, giu_khoa, nhan_moi_truong, ten_ban_chep
 from tram.kiem.chay_lenh import _kill_nhom, chay_mot_lenh, moi_truong_kiem
 from tram.kiem.diff import diff_cham_cam
-from tram.kiem.moi_truong import LoiMoiTruongKiem, chep_moi_truong_kiem
+from tram.kiem.moi_truong import LoiMoiTruongKiem
 
 THOI_GIAN_CHO = 900
 
@@ -34,7 +37,7 @@ def kiem_lai(kho_git: Path, du_an: DuAn, *, giao_id: str, commit: str, lenh_kiem
              lenh_cho_phep: list[str], chay_lenh: bool, thu_muc: Path, thu_muc_log: Path,
              boc: Callable[[list[str]], list[str]], env_goc: Mapping[str, str],
              thoi_gian_cho: float = THOI_GIAN_CHO,
-             trao_quyen: Callable[[Path], None] | None = None,
+             don_sach: Callable[[], None] | None = None,
              kill: Callable[[int, int], None] = _kill_nhom) -> KetQuaKiemLai:
     cham = diff_cham_cam(kho_git, f"origin/{du_an.nhanh_chinh}", commit, them=du_an.giao.duong_dan_cam,
                          cho_phep=du_an.giao.duong_dan_cam_cho_phep)
@@ -45,20 +48,21 @@ def kiem_lai(kho_git: Path, du_an: DuAn, *, giao_id: str, commit: str, lenh_kiem
     mt = du_an.moi_truong_kiem
     if mt is None:
         return KetQuaKiemLai(False, loi="thieu-moi-truong-kiem")
-    wt = thu_muc / giao_id
-    tao_worktree(kho_git, wt, commit)
-    try:
+    with giu_khoa():
+        if don_sach is not None:
+            don_sach()                       # tiến trình tram-kiem của lần trước không được sống sang lần này
+        wt = thu_muc / ten_ban_chep(giao_id)
         try:
-            chep_moi_truong_kiem(mt.file, wt, mt.dich)
-        except LoiMoiTruongKiem:
-            return KetQuaKiemLai(False, loi="thieu-moi-truong-kiem")      # không bao giờ chạy với .env có thể thật
-        if trao_quyen is not None:
-            trao_quyen(wt)            # 4a-2: trao quyền ghi cho `tram-kiem` SAU khi chép môi trường kiểm (spec 3 §7.3)
-        env, ket_qua = moi_truong_kiem(env_goc), []
-        for i, lenh in enumerate(lenh_kiem, 1):
-            kq = chay_mot_lenh(lenh, khop_bat_ky(lenh, lenh_cho_phep), cwd=wt, env=env, boc=boc,
-                               log=thu_muc_log / f"{giao_id}-kiem-lai-{i}.log", thoi_gian_cho=thoi_gian_cho, kill=kill)
-            ket_qua.append(kq.sang_lenh_kiem())
-    finally:
-        xoa_worktree(kho_git, wt)
+            chep_ban(kho_git, commit, wt, boc=boc)
+            try:
+                nhan_moi_truong(kho_git, commit, wt, mt.file, mt.dich, boc=boc)
+            except LoiMoiTruongKiem:
+                return KetQuaKiemLai(False, loi="thieu-moi-truong-kiem")  # không bao giờ chạy với .env có thể thật
+            env, ket_qua = moi_truong_kiem(env_goc), []
+            for i, lenh in enumerate(lenh_kiem, 1):
+                kq = chay_mot_lenh(lenh, khop_bat_ky(lenh, lenh_cho_phep), cwd=wt, env=env, boc=boc, kill=kill,
+                                   log=thu_muc_log / f"{giao_id}-kiem-lai-{i}.log", thoi_gian_cho=thoi_gian_cho)
+                ket_qua.append(kq.sang_lenh_kiem())
+        finally:
+            don_ban(wt, boc=boc, don_sach=don_sach)   # lỗi → ném: không công nhận kết quả khi chưa dọn sạch
     return KetQuaKiemLai(bool(ket_qua) and all(k["ket_qua"] == "pass" for k in ket_qua), tuple(ket_qua))
diff --git a/tram/giao_viec/noi_that.py b/tram/giao_viec/noi_that.py
index 5825ad1..9b4312c 100644
--- a/tram/giao_viec/noi_that.py
+++ b/tram/giao_viec/noi_that.py
@@ -48,7 +48,7 @@ def dung_bo_that(cg: CauHinhGiaoViec, ch: CauHinhTram, *, bo_dem=None,
     return BoGiaoViec(cac_du_an=lambda: cac_du_an_that(thu_muc_du_an),
                       tao_bd=lambda da: Bd(da.duong_dan, actor=ASSIGNEE), mo_kho=mo_kho_phieu, ch=ch,
                       dong_ho=lambda: datetime.now(timezone.utc), boc=pk.boc_lenh if pk else None,
-                      trao_quyen=pk.trao if pk and pk.trao_quyen else None,
+                      don_sach=None,                    # 3c Task 5 nối PrincipalKiem.don_sach
                       kill=pk.kill_nhom if pk else _kill_nhom,
                       doc_beads=DocBeads(bo_dem) if bo_dem is not None else None, thu_muc_kiem=cg.thu_muc_kiem,
                       p4c=nap_phu_thuoc_4c() if cg.bat else PhuThuoc4c())
diff --git a/tram/giao_viec/tick_pipeline.py b/tram/giao_viec/tick_pipeline.py
index 0909a27..7ca25e4 100644
--- a/tram/giao_viec/tick_pipeline.py
+++ b/tram/giao_viec/tick_pipeline.py
@@ -41,7 +41,7 @@ def _kiem_lai(bo, kho: KhoPhieu, da: DuAn, bd, b, ds: list[SK], kg: Path, luc: d
     kq = kiem_lai(kg, da, giao_id=p.giao_id, commit=sha, lenh_kiem=list(p.lenh_kiem), lenh_cho_phep=list(p.lenh_cho_phep),
                   chay_lenh=p.can_lenh_kiem, thu_muc=bo.thu_muc_kiem or tram_home() / "kiem",
                   thu_muc_log=tram_home() / "log" / "kiem-lai", boc=bo.boc or (lambda a: a), env_goc=bo.env_goc,
-                  trao_quyen=bo.trao_quyen, kill=bo.kill)
+                  don_sach=bo.don_sach, kill=bo.kill)
     if kq.loi is not None:
         tao_escalation(bd, kho, da.ten, b, ly_do=kq.loi, cau_hoi="", giao_id=p.giao_id, nguon=f"kl-{sha}", luc=luc)
         if kq.loi == "thieu-moi-truong-kiem":
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_ban_chep.py tests/test_kiem_lai_principal.py tests/test_kiem_lai.py tests/test_luong_giao.py tests/test_noi_giao_viec.py tests/test_tick_hai_pha.py -q`
Expected: `39 passed`

Run: `uv run pytest -q`
Expected: `N₀ + 7 passed` (2107; ghép cùng Task 1 → N₀ + 14 = 2114 — r47, đo thật)

- [ ] **Step 5: Commit**

```bash
git add tram/giao_viec/cay_kiem.py tram/giao_viec/ban_chep.py tram/giao_viec/kiem_lai.py tram/giao_viec/bo.py tram/giao_viec/tick_pipeline.py tram/giao_viec/noi_that.py tests/test_ban_chep.py tests/test_kiem_lai_principal.py tests/test_kiem_lai.py tests/test_luong_giao.py tests/test_noi_giao_viec.py tests/test_tick_hai_pha.py
git commit -m "feat(giao-viec): kiểm lại trên bản chép do tram-kiem sở hữu — git archive | tar dưới tram-kiem, môi trường qua stdin, tự dọn, fail-closed (lát 3c, D22)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

> **Task 4 — ĐÃ CODE 15/10 (D21), ghép `main` `d223406`.** Nội dung dưới đây giữ nguyên văn để tham chiếu; KHÔNG giao lại.

### Task 4: `thuc_hien` bỏ qua lỗi lệnh dọn chạy qua `sudo`

**Độ khó:** `de` · **Đợt:** 1 · **Song song với:** Task 1, 2, 3 · **Phải xong trước:** —

**Files:**
- Modify: `tram/chu/cai_dat.py` (`thuc_hien`, thêm `BO_QUA_LOI`, `bo_qua_loi`)
- Test: `tests/test_cai_dat_bo_qua_loi.py` (mới)

**Interfaces:**
- Consumes: `KeHoach`, `thuc_hien(kh, *, chay=subprocess.run)`.
- Produces: `BO_QUA_LOI = (("launchctl", "bootout"), ("pkill",))`, `bo_qua_loi(c: list[str]) -> bool` (bỏ một `sudo` đứng đầu rồi so tiền tố); `thuc_hien` gọi `chay(c, check=not bo_qua_loi(c))`. Không đổi gì cho lệnh khác (kế hoạch `tram chu cai-dat` cũ: `launchctl bootout` không `sudo` vẫn `check=False`).

- [ ] **Step 1: Viết test thất bại**

`tests/test_cai_dat_bo_qua_loi.py` (mới):

```python
"""`thuc_hien` (khuôn `tram chu cai-dat*`): lệnh dọn có `sudo` cũng được bỏ qua lỗi (lát 3c). Trước đây `sudo launchctl
bootout system/vn.tram.tho` chạy với check=True nên lần cài ĐẦU (dịch vụ chưa nạp) dừng trước `bootstrap`."""
from tram.chu.cai_dat import KeHoach, bo_qua_loi, thuc_hien


def test_bootout_va_pkill_qua_sudo_khong_check():
    lenh = [["sudo", "launchctl", "bootout", "system/vn.tram.tho"], ["launchctl", "bootout", "gui/501/vn.tram.api"],
            ["sudo", "pkill", "-KILL", "-u", "tram-kiem"], ["sudo", "launchctl", "bootstrap", "system", "/L/x.plist"],
            ["sudo", "install", "-m", "0440", "a", "b"], ["pkill", "-x", "y"], ["sudo"]]
    goi = []
    thuc_hien(KeHoach({}, lenh, []), chay=lambda c, check: goi.append(check))
    assert goi == [False, False, False, True, True, False, True]
    assert not bo_qua_loi(["sudo", "rm", "-f", "/etc/sudoers.d/tram-tho"])
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_cai_dat_bo_qua_loi.py -q`
Expected: FAIL — `1 error` (`ImportError: cannot import name 'bo_qua_loi' from 'tram.chu.cai_dat'`)

- [ ] **Step 3: Viết mã**

`tram/chu/cai_dat.py` (sửa — bản vá):

```diff
diff --git a/tram/chu/cai_dat.py b/tram/chu/cai_dat.py
index 7ef9938..63730cd 100644
--- a/tram/chu/cai_dat.py
+++ b/tram/chu/cai_dat.py
@@ -83,6 +83,15 @@ def in_ke_hoach(kh: KeHoach) -> str:
     return "\n".join(dong)
 
 
+BO_QUA_LOI = (("launchctl", "bootout"), ("pkill",))      # lệnh dọn: "không có gì để dọn" không phải lỗi
+
+
+def bo_qua_loi(c: list[str]) -> bool:
+    """`launchctl bootout` (dịch vụ chưa nạp) và `pkill` (không có tiến trình) — kể cả khi chạy qua `sudo` (lát 3c)."""
+    c = c[1:] if c[:1] == ["sudo"] else c
+    return any(tuple(c[:len(t)]) == t for t in BO_QUA_LOI)
+
+
 def thuc_hien(kh: KeHoach, *, chay=subprocess.run) -> None:
     for p, noi_dung in kh.tep.items():
         p.parent.mkdir(parents=True, exist_ok=True)
@@ -90,7 +99,7 @@ def thuc_hien(kh: KeHoach, *, chay=subprocess.run) -> None:
     for _, ham in kh.buoc:
         ham()
     for c in kh.lenh:
-        chay(c, check=c[:2] != ["launchctl", "bootout"])
+        chay(c, check=not bo_qua_loi(c))
 
 
 def trang_thai(kho) -> str:
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_cai_dat_bo_qua_loi.py tests/test_chu.py tests/test_chu_tho.py -q`
Expected: `15 passed`

Run: `uv run pytest -q`
Expected: `N₀ + 1 passed`

- [ ] **Step 5: Commit**

```bash
git add tram/chu/cai_dat.py tests/test_cai_dat_bo_qua_loi.py
git commit -m "fix(chu): thuc_hien bỏ qua lỗi launchctl bootout/pkill kể cả khi chạy qua sudo (cai-dat-tho lần đầu) (lát 3c)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 5: Một nguồn principal kiểm — `doc_principal_kiem`, `PrincipalKiem.tu_cach_ly`, `don_sach`

**Độ khó:** `kho` · **Đợt:** 2 · **Song song với:** — · **Phải xong trước:** Task 1, Task 3

**Files:**
- Create: `tram/cau_hinh/principal_kiem.py`
- Modify: `tram/giao_viec/principal_kiem.py` (viết lại: `PrincipalKiem(ten, boc, co_che)` + `don_sach`; bỏ `trao_quyen`/`trao`; thêm `tu_cach_ly`)
- Modify: `tram/cau_hinh/giao_viec.py` (bỏ `_argv`, `_principal`, `TEN_RE`; dùng `doc_principal_kiem`; `thu_muc_kiem` qua `goc_hop_le`), `tram/cau_hinh/cach_ly.py` (docstring), `tram/giao_viec/noi_that.py` (`don_sach=pk.don_sach`), `tram/giao_viec/kiem_san_sang.py` (`_ghi_duoc` theo bản chép)
- Modify: `tests/test_cau_hinh_giao_viec.py`, `tests/test_noi_giao_viec.py`, `tests/test_giao_kiem.py`
- Test: `tests/test_principal_kiem_hop_nhat.py` (mới)

**Interfaces:**
- Consumes: `doc_principal`, `BIEN_GIU` (3a-2); `HO_SO_KIEM`, `goc_hop_le`, `dong_sudoers_kiem` (Task 1); `LoiBanChep`, `KiemLaiDangBan`, `giu_khoa`, `ten_ban_chep` (Task 3); `nap_cau_hinh_cach_ly`.
- Produces: `PrincipalKiem(ten, boc, co_che="user")` + `.boc_lenh(argv)`, `.kill_nhom(pgid, sig, *, chay)`, `.don_sach(*, chay=subprocess.run, lan=5, ngu=time.sleep)` (LoiBanChep); `PGREP`; `tu_cach_ly(chuoi) -> PrincipalKiem` (`ChuaCoPrincipal` khi sai dạng). `doc_principal_kiem(duong_dan=None, *, bao=_bao) -> PrincipalKiem | None` (ValueError). `nap_cau_hinh_giao_viec` giữ chữ ký. `kiem_san_sang.THU_MUC_THU = "tram-giao-kiem-thu"`; mục `"principal: ghi worktree kiểm"` đổi tên `"principal: ghi bản chép kiểm"`.

- [ ] **Step 1: Viết test thất bại**

`tests/test_principal_kiem_hop_nhat.py` (mới):

```python
"""MỘT nguồn khai báo principal kiểm lại (lát 3c, bead bs-urj.12): `cach_ly.tram_kiem` là khoá chuẩn; khoá cũ
`giao_viec.principal_kiem` chỉ để đối chiếu. D22: không trao/thu quyền — `don_sach` giết tiến trình dưới tram-kiem, trạm
tự đếm bằng pgrep. Không sudo — chỉ kiểm argv dựng ra, `chay` giả."""
import fnmatch
from types import SimpleNamespace

import pytest

from tram.cau_hinh.giao_viec import nap_cau_hinh_giao_viec
from tram.cau_hinh.principal_kiem import doc_principal_kiem
from tram.giao_viec.ban_chep import LoiBanChep
from tram.giao_viec.principal_kiem import PrincipalKiem, tu_cach_ly
from tram.tho.principal import BIEN_GIU
from tram.tho.quyen_kiem import HO_SO_KIEM, dong_sudoers_kiem

CU = "giao_viec:\n  principal_kiem:\n    ten: {ten}\n    boc: [/bin/sh, -c]\n    trao_quyen: [/tmp/x]\n"


def ghi(tram_home, noi_dung: str):
    tram_home.mkdir(parents=True, exist_ok=True)
    (tram_home / "cau-hinh.yaml").write_text(noi_dung, encoding="utf-8")


def test_user_dung_argv_principal_3a2_khong_con_trao_quyen():
    pk = tu_cach_ly("user:tram-kiem")
    assert pk.boc == ("/usr/bin/sudo", "-n", "-H", "-u", "tram-kiem", f"--preserve-env={','.join(BIEN_GIU)}", "--")
    assert pk.co_che == "user" and list(PrincipalKiem.__dataclass_fields__) == ["ten", "boc", "co_che"]


def test_sandbox_boc_qua_ho_so_co_dinh_cua_tram_kiem():
    pk = tu_cach_ly("sandbox:tram-thuc-thi")
    assert pk.ten == "tram-thuc-thi" and pk.co_che == "sandbox"
    assert pk.boc[-4:] == ("--", "/usr/bin/sandbox-exec", "-f", str(HO_SO_KIEM))


def test_chua_khai_gi_la_none(tram_home_tam):
    assert doc_principal_kiem() is None
    ghi(tram_home_tam, "cach_ly:\n  kenh_ghi: header\n")
    assert doc_principal_kiem() is None


def test_hai_khoa_trung_ten_thi_canh_bao_va_bo_argv_cu(tram_home_tam):
    ghi(tram_home_tam, "cach_ly:\n  tram_kiem: user:tram-kiem\n" + CU.format(ten="tram-kiem"))
    bao = []
    pk = doc_principal_kiem(bao=bao.append)
    assert pk == tu_cach_ly("user:tram-kiem") and "/bin/sh" not in pk.boc
    assert len(bao) == 1 and "khoá cũ" in bao[0]


@pytest.mark.parametrize("noi_dung, loi", [
    ("cach_ly:\n  tram_kiem: user:tram-kiem\n" + CU.format(ten="tram-khac"), "khác"),
    (CU.format(ten="tram-kiem"), "cach_ly.tram_kiem"),
    ("cach_ly:\n  tram_kiem: tram-kiem\n", "sai dạng"),
    ("cach_ly:\n  tram_kiem: user:tram-kiem\ngiao_viec:\n  principal_kiem: [tram-kiem]\n", "khoá cũ")])
def test_lech_hoac_sai_dang_la_loi_cau_hinh(tram_home_tam, noi_dung, loi):
    ghi(tram_home_tam, noi_dung)
    with pytest.raises(ValueError, match=loi):
        doc_principal_kiem()


def test_giao_viec_doc_qua_nguon_chung(tram_home_tam, tmp_path):
    ghi(tram_home_tam, f"cach_ly:\n  tram_kiem: sandbox:tram-kiem\ngiao_viec:\n  thu_muc_kiem: {tmp_path}/k\n")
    assert nap_cau_hinh_giao_viec().principal_kiem == doc_principal_kiem() == tu_cach_ly("sandbox:tram-kiem")


def test_thu_muc_kiem_symlink_bi_tu_choi(tram_home_tam, tmp_path):
    (tmp_path / "that").mkdir()
    (tmp_path / "lk").symlink_to(tmp_path / "that")
    ghi(tram_home_tam, f"cach_ly:\n  tram_kiem: user:tram-kiem\ngiao_viec:\n  thu_muc_kiem: {tmp_path}/lk\n")
    with pytest.raises(ValueError, match="THẬT"):
        nap_cau_hinh_giao_viec()


def chay_gia(pgrep: list[int]):
    goi = []

    def chay(argv, **kw):
        goi.append(argv)
        return SimpleNamespace(returncode=pgrep.pop(0) if argv[0] == "/usr/bin/pgrep" else 1)
    return goi, chay


def test_don_sach_giet_duoi_tram_kiem_roi_tram_tu_dem():
    pk, (goi, chay) = tu_cach_ly("user:tram-kiem"), chay_gia([0, 1])
    pk.don_sach(chay=chay, ngu=lambda s: None)
    assert goi[:3] == [pk.boc_lenh(["/usr/bin/crontab", "-r"]), pk.boc_lenh(["/usr/bin/pkill", "-KILL", "-U",
                                                                             "tram-kiem"]),
                       ["/usr/bin/pgrep", "-U", "tram-kiem"]] and len(goi) == 6     # pgrep KHÔNG qua sudo


@pytest.mark.parametrize("pgrep, khop", [([0] * 5, "vẫn còn"), ([2], "pgrep")])
def test_tai_sinh_hoac_pgrep_loi_thi_nem(pgrep, khop):
    with pytest.raises(LoiBanChep, match=khop):
        tu_cach_ly("user:tram-kiem").don_sach(chay=chay_gia(pgrep)[1], ngu=lambda s: None)


@pytest.mark.parametrize("co_che", ["user", "sandbox"])
def test_moi_argv_duoi_tram_kiem_khop_sudoers(co_che):
    pk, (goi, chay) = tu_cach_ly(f"{co_che}:tram-kiem"), chay_gia([1])
    pk.don_sach(chay=chay)
    pk.kill_nhom(123, 9, chay=lambda argv, **kw: goi.append(argv))
    mau = dong_sudoers_kiem(tram="hung", tram_kiem="tram-kiem", co_che=co_che).split("NOPASSWD:SETENV: ", 1)[1]
    goi.append(pk.boc_lenh(["/usr/bin/tar", "-x", "-f", "-", "-C", "/k/g-1"]))
    qua_sudo = [a for a in goi if a[0] != "/usr/bin/pgrep"]
    assert all(a[:5] == ["/usr/bin/sudo", "-n", "-H", "-u", "tram-kiem"] for a in qua_sudo) and len(qua_sudo) == 4
    assert all(mau == "ALL" or fnmatch.fnmatchcase(" ".join(a[a.index("--") + 1:]), mau) for a in qua_sudo)
```

`tests/test_cau_hinh_giao_viec.py`, `tests/test_giao_kiem.py`, `tests/test_noi_giao_viec.py` (sửa — bản vá):

```diff
diff --git a/tests/test_cau_hinh_giao_viec.py b/tests/test_cau_hinh_giao_viec.py
index 26d51e3..b409a41 100644
--- a/tests/test_cau_hinh_giao_viec.py
+++ b/tests/test_cau_hinh_giao_viec.py
@@ -1,10 +1,12 @@
-"""Khoá `giao_viec:` (4a-2) và adapter principal `tram-kiem` (chờ S6) — không chạy sudo thật."""
+"""Khoá `giao_viec:` (4a-2) và adapter principal `tram-kiem` (chờ S6) — không chạy sudo thật. Lát 3c: principal
+khai ở `cach_ly.tram_kiem` (MỘT nguồn); `giao_viec.principal_kiem` chỉ còn là khoá cũ để đối chiếu."""
 import pytest
 
 from tram.cau_hinh.giao_viec import CauHinhGiaoViec, nap_cau_hinh_giao_viec
-from tram.giao_viec.principal_kiem import PrincipalKiem
+from tram.giao_viec.principal_kiem import PrincipalKiem, tu_cach_ly
 
-PK = "  principal_kiem:\n    ten: tram-kiem\n    boc: [/usr/bin/sudo, -n, -u, tram-kiem, --]\n"
+PK = "cach_ly:\n  tram_kiem: user:tram-kiem\n"
+CU = "  principal_kiem:\n    ten: tram-kiem\n    boc: [/usr/bin/sudo, -n, -u, tram-kiem, --]\n"
 
 
 def _nap(tram_home, noi_dung: str) -> CauHinhGiaoViec:
@@ -20,13 +22,11 @@ def test_thieu_file_hoac_thieu_khoa_la_tat(tram_home_tam):
 
 
 def test_doc_du_khoa(tram_home_tam, tmp_path):
-    cg = _nap(tram_home_tam, f"giao_viec:\n  bat: true\n  chu_ky_giay: 90\n  thu_muc_kiem: {tmp_path}/kiem\n" + PK
-              + "    trao_quyen: [/usr/local/libexec/trao, --ghi]\n")
+    cg = _nap(tram_home_tam, PK + f"giao_viec:\n  bat: true\n  chu_ky_giay: 90\n  thu_muc_kiem: {tmp_path}/kiem\n")
     assert (cg.bat, cg.chu_ky_giay, cg.thu_muc_kiem) == (True, 90, tmp_path / "kiem")
     pk = cg.principal_kiem
-    assert pk == PrincipalKiem("tram-kiem", ("/usr/bin/sudo", "-n", "-u", "tram-kiem", "--"),
-                               ("/usr/local/libexec/trao", "--ghi"))
-    assert pk.boc_lenh(["sh", "kiem.sh"]) == ["/usr/bin/sudo", "-n", "-u", "tram-kiem", "--", "sh", "kiem.sh"]
+    assert pk == tu_cach_ly("user:tram-kiem") and pk.ten == "tram-kiem"
+    assert pk.boc_lenh(["sh", "kiem.sh"])[:5] == ["/usr/bin/sudo", "-n", "-H", "-u", "tram-kiem"]
 
 
 @pytest.mark.parametrize("noi_dung", [
@@ -36,23 +36,22 @@ def test_doc_du_khoa(tram_home_tam, tmp_path):
     "giao_viec:\n  la: 1\n",
     "giao_viec:\n  bat: true\n",                                                     # bật mà chưa có principal
     "giao_viec:\n  thu_muc_kiem: tuong/doi\n",
-    "giao_viec:\n" + PK,                                                             # principal mà thiếu thư mục
-    "giao_viec:\n  thu_muc_kiem: {home}/kiem\n" + PK,                                # thư mục trong ~/.tram
-    "giao_viec:\n  thu_muc_kiem: /tmp/k\n  principal_kiem:\n    ten: Tram Kiem\n    boc: [/usr/bin/sudo]\n",
-    "giao_viec:\n  thu_muc_kiem: /tmp/k\n  principal_kiem:\n    ten: tram-kiem\n    boc: [sudo, -u, x]\n",
-    "giao_viec:\n  thu_muc_kiem: /tmp/k\n  principal_kiem:\n    ten: tram-kiem\n    boc: []\n",
+    PK + "giao_viec:\n  bat: false\n",                                               # principal mà thiếu thư mục
+    PK + "giao_viec:\n  thu_muc_kiem: {home}/kiem\n",                                # thư mục trong ~/.tram
+    PK + "giao_viec:\n  thu_muc_kiem: /Users/Shared/a b\n",                          # ký tự không an toàn
+    "giao_viec:\n  thu_muc_kiem: /Users/Shared/k\n" + CU,                            # chỉ có khoá cũ
+    "cach_ly:\n  tram_kiem: tram-kiem\ngiao_viec:\n  thu_muc_kiem: /Users/Shared/k\n",     # thiếu user:/sandbox:
 ])
 def test_sai_bao_loi(tram_home_tam, noi_dung):
     with pytest.raises(ValueError):
         _nap(tram_home_tam, noi_dung.replace("{home}", str(tram_home_tam)))
 
 
-def test_trao_quyen_goi_lenh_voi_thu_muc(tmp_path):
-    goi = []
-    PrincipalKiem("tram-kiem", ("/usr/bin/sudo",), ("/usr/local/libexec/trao",)).trao(
-        tmp_path, chay=lambda argv, **kw: goi.append((argv, kw["check"])))
-    PrincipalKiem("tram-kiem", ("/usr/bin/sudo",)).trao(tmp_path, chay=lambda *a, **k: goi.append("khong"))
-    assert goi == [(["/usr/local/libexec/trao", str(tmp_path)], True)]
+def test_principal_kiem_khong_con_trao_thu_quyen():
+    """D22: không helper root, không ACL — `tram-kiem` sở hữu bản chép, chỉ còn `boc`, `kill_nhom`, `don_sach`."""
+    assert not hasattr(PrincipalKiem, "trao") and not hasattr(PrincipalKiem, "thu")
+    assert PrincipalKiem("tram-kiem", ("/usr/bin/sudo",)).co_che == "user"
+
 
 def test_kill_nhom_chay_cung_principal_khong_qua_shell():
     import signal
diff --git a/tests/test_giao_kiem.py b/tests/test_giao_kiem.py
index 812228c..506aeab 100644
--- a/tests/test_giao_kiem.py
+++ b/tests/test_giao_kiem.py
@@ -9,20 +9,24 @@ from kho_kiem_gia import dung_kho
 from tram.cau_hinh.du_an import DuAn, MoiTruongKiem
 from tram.cau_hinh.giao_viec import CauHinhGiaoViec
 from tram.cli import main
+from tram.giao_viec.ban_chep import giu_khoa
 from tram.giao_viec.kho_kiem_tao import lap_ke_hoach, thuc_hien
 from tram.giao_viec.kiem_san_sang import kiem_du_an, kiem_giao_viec
 from tram.giao_viec.principal_kiem import PrincipalKiem
 from tram.kiem.chay_lenh import KetQuaLenh
 from tram.tho.kiem_may import in_ket_qua
 
-PK = PrincipalKiem("tram-kiem", ("/usr/bin/sudo", "-n", "-u", "tram-kiem", "--"), ("/usr/local/libexec/trao",))
+PK = PrincipalKiem("tram-kiem", ("/usr/bin/sudo", "-n", "-u", "tram-kiem", "--"))
 
 
-def chay_gia(ten="tram-kiem", env="APP_ENV=testing\nPATH=/usr/bin", doc_duoc=False, ghi_duoc=True):
+def chay_gia(ten="tram-kiem", env="APP_ENV=testing\nPATH=/usr/bin", doc_duoc=False, ghi_duoc=True, pgrep=1):
+    """`sudo -u tram-kiem` giả: mkdir/touch/rm chạy THẬT dưới user đang test (trong tmp_path) khi `ghi_duoc`."""
     def chay(argv, **kw):
         lenh = argv[len(PK.boc):] if argv[:len(PK.boc)] == list(PK.boc) else argv
+        if lenh[0] in ("/bin/mkdir", "/usr/bin/touch", "/bin/rm"):
+            return subprocess.run(lenh if ghi_duoc else ["/usr/bin/false"], capture_output=True, text=True)
         ra = {"/usr/bin/id": (0, ten), "/usr/bin/env": (0, env), "/bin/test": (0 if doc_duoc else 1, ""),
-              "/usr/bin/touch": (0 if ghi_duoc else 1, ""), "/usr/local/libexec/trao": (0, "")}[lenh[0]]
+              "/usr/bin/crontab": (1, ""), "/usr/bin/pkill": (1, ""), "/usr/bin/pgrep": (pgrep, "")}[lenh[0]]
         if kw.get("check") and ra[0]:
             raise subprocess.CalledProcessError(ra[0], argv)
         return subprocess.CompletedProcess(argv, ra[0], ra[1], "")
@@ -51,18 +55,29 @@ def test_principal_dat_moi_muc(tmp_path):
     cg = CauHinhGiaoViec(bat=True, thu_muc_kiem=tmp_path, principal_kiem=PK)
     ds = kiem_giao_viec(cg, [], goc_quyen=tmp_path / "quyen", chay=chay_gia(), chay_lenh=dung_lenh(), toi="hung")
     assert set(muc(ds).values()) == {"xanh"} and in_ket_qua(ds)[1] == 0
-    assert not (tmp_path / "tram-giao-kiem-thu").exists()
+    assert not list(tmp_path.glob("tram-giao-kiem-thu*"))
 
 
 @pytest.mark.parametrize("sai, muc_do", [
     ({"ten": "hung"}, "principal: danh tính"), ({"env": "PATH=/usr/bin"}, "principal: giữ APP_ENV"),
-    ({"doc_duoc": True}, "principal: không đọc kho trạm"), ({"ghi_duoc": False}, "principal: ghi worktree kiểm")])
+    ({"doc_duoc": True}, "principal: không đọc kho trạm"), ({"ghi_duoc": False}, "principal: ghi bản chép kiểm"),
+    ({"pgrep": 0}, "principal: ghi bản chép kiểm")])
 def test_principal_sai_tung_muc_la_do(tmp_path, sai, muc_do):
     m = muc(kiem_giao_viec(CauHinhGiaoViec(thu_muc_kiem=tmp_path, principal_kiem=PK), [], goc_quyen=tmp_path,
                            chay=chay_gia(**sai), chay_lenh=dung_lenh(), toi="hung"))
     assert m[muc_do] == "do" and m["principal: dừng được lệnh quá hạn"] == "xanh"
 
 
+def test_dang_kiem_lai_thi_muc_ghi_do_khong_giet_tram_kiem(tmp_path):
+    goi = []
+    goc = chay_gia()
+    with giu_khoa():
+        m = kiem_giao_viec(CauHinhGiaoViec(thu_muc_kiem=tmp_path, principal_kiem=PK), [], goc_quyen=tmp_path,
+                           chay=lambda a, **kw: goi.append(a) or goc(a, **kw), chay_lenh=dung_lenh(), toi="hung")
+    assert muc(m)["principal: ghi bản chép kiểm"] == "do" and "đang có lần kiểm lại" in str(m)
+    assert not any("/usr/bin/pkill" in a for a in goi)
+
+
 def test_khong_dung_duoc_lenh_qua_han_la_do(tmp_path):
     m = muc(kiem_giao_viec(CauHinhGiaoViec(thu_muc_kiem=tmp_path, principal_kiem=PK), [], goc_quyen=tmp_path,
                            chay=chay_gia(), chay_lenh=dung_lenh(het_gio=False), toi="hung"))
diff --git a/tests/test_noi_giao_viec.py b/tests/test_noi_giao_viec.py
index 272c1b8..adac405 100644
--- a/tests/test_noi_giao_viec.py
+++ b/tests/test_noi_giao_viec.py
@@ -11,7 +11,7 @@ from tram.cau_hinh.giao_viec import CauHinhGiaoViec
 from tram.giao_viec.noi_that import an_toan, dung_bo_that, noi_giao_viec
 from tram.giao_viec.principal_kiem import PrincipalKiem
 
-PK = PrincipalKiem("tram-kiem", ("/usr/bin/sudo", "-n", "-u", "tram-kiem", "--"), ("/usr/local/libexec/trao",))
+PK = PrincipalKiem("tram-kiem", ("/usr/bin/sudo", "-n", "-u", "tram-kiem", "--"))
 NHIP = {"khe_id": "B/claude-1", "buoc_tho": "ranh"}
 
 
@@ -63,7 +63,7 @@ def test_dung_bo_that_noi_principal_va_bo_qua_du_an_hong(tmp_path, capsys):
     cg = CauHinhGiaoViec(bat=True, thu_muc_kiem=tmp_path / "k", principal_kiem=PK)
     bo = dung_bo_that(cg, tao_pt(tmp_path, {}).cau_hinh, thu_muc_du_an=tmp_path / "du-an")
     assert [d.ten for d in bo.cac_du_an()] == ["hr-x"] and "bỏ qua dự án hong" in capsys.readouterr().err
-    assert bo.boc(["sh", "kiem.sh"]) == [*PK.boc, "sh", "kiem.sh"] and bo.don_sach is None      # 3c T5 nối
+    assert bo.boc(["sh", "kiem.sh"]) == [*PK.boc, "sh", "kiem.sh"] and bo.don_sach == PK.don_sach
     assert bo.kill == PK.kill_nhom
     assert bo.thu_muc_kiem == tmp_path / "k" and bo.doc_beads is None
     assert bo.tao_bd(bo.cac_du_an()[0]).actor == "tram/giao-viec" and Path(bo.tao_bd(bo.cac_du_an()[0]).repo) == tmp_path
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_principal_kiem_hop_nhat.py tests/test_cau_hinh_giao_viec.py tests/test_giao_kiem.py tests/test_noi_giao_viec.py -q`
Expected: FAIL — `2 errors` (`ModuleNotFoundError: No module named 'tram.cau_hinh.principal_kiem'`; `ImportError: cannot import name 'tu_cach_ly'`)

- [ ] **Step 3: Viết mã**

`tram/cau_hinh/principal_kiem.py` (mới):

```python
"""MỘT nguồn khai báo principal kiểm lại `tram-kiem` (lát 3c, bead bs-urj.12; spec 3 §7.3 mục 5, spec 4 §6.2).

Khoá chuẩn: `cach_ly.tram_kiem: user:<tên> | sandbox:<tên>` trong `~/.tram/cau-hinh.yaml`. Khoá cũ của 4a-2
`giao_viec.principal_kiem {ten, boc, trao_quyen}` chỉ còn được đọc để đối chiếu:
- có cả hai, cùng tên user → cảnh báo, bỏ `boc`/`trao_quyen` cũ (argv dựng từ khoá chuẩn);
- có cả hai, khác tên user → lỗi cấu hình;
- chỉ có khoá cũ → lỗi cấu hình (khoá cũ không nói cơ chế §14 — không chọn thay Đại ca).
Mọi nơi đọc (`nap_cau_hinh_giao_viec`, `tram chu cai-dat-tho`, `tram chu kiem-cach-ly`) đi qua `doc_principal_kiem`."""
import sys
from collections.abc import Callable
from pathlib import Path

import yaml

from tram.cau_hinh.cach_ly import nap_cau_hinh_cach_ly
from tram.duong_dan import tram_home
from tram.giao_viec.principal_kiem import PrincipalKiem, tu_cach_ly

KHOA_CU = {"ten", "boc", "trao_quyen"}


def _bao(tin: str) -> None:
    print(f"[cau-hinh] {tin}", file=sys.stderr, flush=True)


def _ten_khoa_cu(p: Path) -> str | None:
    raw = (yaml.safe_load(p.read_text(encoding="utf-8")) or {}) if p.exists() else {}
    gv = raw.get("giao_viec") if isinstance(raw, dict) else None
    cu = gv.get("principal_kiem") if isinstance(gv, dict) else None
    if cu is None:
        return None
    if not isinstance(cu, dict) or not set(cu) <= KHOA_CU or not isinstance(cu.get("ten"), str):
        raise ValueError("giao_viec.principal_kiem (khoá cũ) phải là bảng {ten, boc?, trao_quyen?}")
    return cu["ten"]


def doc_principal_kiem(duong_dan: Path | None = None, *, bao: Callable[[str], None] = _bao) -> PrincipalKiem | None:
    """None khi chưa khai (chờ S6). Sai dạng hoặc hai khoá lệch nhau → ValueError."""
    p = duong_dan or tram_home() / "cau-hinh.yaml"
    moi, cu = nap_cau_hinh_cach_ly(p).tram_kiem, _ten_khoa_cu(p)
    pk = None if moi is None else tu_cach_ly(moi)
    if cu is None:
        return pk
    if pk is None:
        raise ValueError("giao_viec.principal_kiem là khoá cũ — khai cach_ly.tram_kiem: user:<tên> | sandbox:<tên> "
                         "(lát 3c) rồi xoá khoá cũ")
    if cu != pk.ten:
        raise ValueError(f"giao_viec.principal_kiem.ten = {cu!r} khác cach_ly.tram_kiem = {moi!r} — "
                         "chỉ giữ cach_ly.tram_kiem")
    bao("giao_viec.principal_kiem là khoá cũ, trùng cach_ly.tram_kiem — bỏ qua boc/trao_quyen cũ; hãy xoá khoá này")
    return pk
```

`tram/giao_viec/principal_kiem.py`, `tram/cau_hinh/giao_viec.py`, `tram/cau_hinh/cach_ly.py`, `tram/giao_viec/noi_that.py`, `tram/giao_viec/kiem_san_sang.py` (sửa — bản vá):

```diff
diff --git a/tram/cau_hinh/cach_ly.py b/tram/cau_hinh/cach_ly.py
index d7d15d5..2ff41c9 100644
--- a/tram/cau_hinh/cach_ly.py
+++ b/tram/cau_hinh/cach_ly.py
@@ -1,7 +1,8 @@
 """Khoá `cach_ly:` trong `~/.tram/cau-hinh.yaml` (spec 3 §7.3, spec 2 §4 mục 2b). CƠ CHẾ CHƯA CHỐT — chờ spike S6:
 - `kenh_ghi`: `header` (lát 2a — header Tailscale trên TCP localhost, GIẢ ĐƯỢC: chưa đạt điều kiện trước 3a) hay
   `unix-socket` (API ghi của dashboard chỉ nhận yêu cầu qua Unix socket trong thư mục chỉ tài khoản trạm vào được);
-- `tram_kiem`: principal kiểm lại của trạm (`user:<tên>` | `sandbox:<tên>`, §7.3 mục 5);
+- `tram_kiem`: principal kiểm lại của trạm (`user:<tên>` | `sandbox:<tên>`, §7.3 mục 5) — NGUỒN DUY NHẤT từ lát 3c,
+  đọc qua `tram.cau_hinh.principal_kiem.doc_principal_kiem` (không đọc thẳng trường này);
 - `db_nghiep_vu`: `host:cổng` mà kiểm chứng âm H9 phải thấy bị chặn."""
 import re
 from dataclasses import dataclass
diff --git a/tram/cau_hinh/giao_viec.py b/tram/cau_hinh/giao_viec.py
index 4690880..8a5bd35 100644
--- a/tram/cau_hinh/giao_viec.py
+++ b/tram/cau_hinh/giao_viec.py
@@ -1,26 +1,26 @@
 """Khoá `giao_viec:` trong `~/.tram/cau-hinh.yaml` (lát 4a-2). `nap_cau_hinh_tram` bỏ qua khoá lạ nên đọc riêng ở
 đây — không sửa `tram/cau_hinh/tram.py`. Thiếu khoá → bộ giao việc TẮT: tram-api không phát phiếu, không chạy tick.
+Lát 3c: principal kiểm lại khai MỘT chỗ — `cach_ly.tram_kiem` — đọc qua `doc_principal_kiem` (khoá cũ
+`giao_viec.principal_kiem` chỉ còn để đối chiếu, xem `tram/cau_hinh/principal_kiem.py`).
 
+    cach_ly:
+      tram_kiem: user:tram-kiem      # chờ S6 — user:<tên> | sandbox:<tên>; `tram giao kiem` kiểm khi chạy thật
     giao_viec:
-      bat: false                     # true chỉ sau mọi cổng (3a-2, S6, S7) — cần principal_kiem
+      bat: false                     # true chỉ sau mọi cổng (3a-2, S6, S7) — cần cach_ly.tram_kiem
       chu_ky_giay: 120               # vòng tick (spec 4 §10); ≤ 150 để giữ G5 ≤ 3 phút
-      thu_muc_kiem: /Users/Shared/tram-kiem      # worktree kiểm lại — NGOÀI ~/.tram (tram-kiem không đọc kho trạm)
-      principal_kiem:                # chờ S6 — hình dạng lệnh chưa xác minh, `tram giao kiem` kiểm khi chạy thật
-        ten: tram-kiem
-        boc: [/usr/bin/sudo, -n, -u, tram-kiem, --]
-        trao_quyen: [/usr/bin/sudo, -n, /usr/local/libexec/tram-trao-quyen-kiem]
+      thu_muc_kiem: /Users/Shared/tram-kiem      # gốc bản chép kiểm lại — NGOÀI ~/.tram, đường dẫn THẬT, của tram-kiem
 """
-import re
 from dataclasses import dataclass
 from pathlib import Path
 
 import yaml
 
+from tram.cau_hinh.principal_kiem import doc_principal_kiem
 from tram.duong_dan import tram_home
 from tram.giao_viec.principal_kiem import PrincipalKiem
+from tram.tho.quyen_kiem import goc_hop_le
 
-KHOA = {"bat", "chu_ky_giay", "thu_muc_kiem", "principal_kiem"}
-TEN_RE = re.compile(r"[a-z_][a-z0-9_-]{0,31}")
+KHOA = {"bat", "chu_ky_giay", "thu_muc_kiem", "principal_kiem"}      # principal_kiem: khoá cũ, chỉ để đối chiếu
 CHU_KY = (30, 150)
 
 
@@ -32,32 +32,14 @@ class CauHinhGiaoViec:
     principal_kiem: PrincipalKiem | None = None
 
 
-def _argv(raw, khoa: str, *, bat_buoc: bool) -> tuple[str, ...]:
-    if raw is None and not bat_buoc:
-        return ()
-    if not isinstance(raw, list) or not raw or not all(isinstance(x, str) and x for x in raw) \
-            or not raw[0].startswith("/"):
-        raise ValueError(f"giao_viec.principal_kiem.{khoa}: danh sách argv, phần tử đầu là đường dẫn tuyệt đối")
-    return tuple(raw)
-
-
-def _principal(raw) -> PrincipalKiem | None:
-    if raw is None:
-        return None
-    if not isinstance(raw, dict) or not set(raw) <= {"ten", "boc", "trao_quyen"} or "ten" not in raw:
-        raise ValueError("giao_viec.principal_kiem phải là bảng {ten, boc, trao_quyen?}")
-    if not isinstance(raw["ten"], str) or not TEN_RE.fullmatch(raw["ten"]):
-        raise ValueError("giao_viec.principal_kiem.ten không hợp lệ")
-    return PrincipalKiem(raw["ten"], _argv(raw.get("boc"), "boc", bat_buoc=True),
-                         _argv(raw.get("trao_quyen"), "trao_quyen", bat_buoc=False))
-
-
 def _thu_muc(raw, pk: PrincipalKiem | None) -> Path | None:
     p = None if raw is None else Path(str(raw)).expanduser()
     if p is not None and not p.is_absolute():
         raise ValueError("giao_viec.thu_muc_kiem phải là đường dẫn tuyệt đối")
     if pk is not None and (p is None or p.resolve().is_relative_to(tram_home().resolve())):
-        raise ValueError("giao_viec.thu_muc_kiem phải đặt NGOÀI ~/.tram khi có principal_kiem")
+        raise ValueError("giao_viec.thu_muc_kiem phải đặt NGOÀI ~/.tram khi có cach_ly.tram_kiem")
+    if pk is not None:
+        goc_hop_le(p)                     # 3c: đường dẫn thật, ký tự an toàn (hồ sơ sandbox, lệnh cài)
     return p
 
 
@@ -74,7 +56,7 @@ def nap_cau_hinh_giao_viec(duong_dan: Path | None = None) -> CauHinhGiaoViec:
         raise ValueError("giao_viec.bat phải là true/false")
     if isinstance(chu_ky, bool) or not isinstance(chu_ky, int) or not CHU_KY[0] <= chu_ky <= CHU_KY[1]:
         raise ValueError(f"giao_viec.chu_ky_giay phải là số nguyên trong {CHU_KY} (giữ G5 ≤ 3 phút)")
-    pk = _principal(gv.get("principal_kiem"))
+    pk = doc_principal_kiem(p)
     if bat and pk is None:
-        raise ValueError("giao_viec.bat cần principal_kiem — kiểm lại không bao giờ chạy dưới quyền tram-api (G4)")
+        raise ValueError("giao_viec.bat cần cach_ly.tram_kiem — kiểm lại không bao giờ chạy dưới quyền tram-api (G4)")
     return CauHinhGiaoViec(bat, chu_ky, _thu_muc(gv.get("thu_muc_kiem"), pk), pk)
diff --git a/tram/giao_viec/kiem_san_sang.py b/tram/giao_viec/kiem_san_sang.py
index 4a5c415..bc221df 100644
--- a/tram/giao_viec/kiem_san_sang.py
+++ b/tram/giao_viec/kiem_san_sang.py
@@ -1,7 +1,9 @@
 """`tram giao kiem` — kiểm sẵn sàng của bộ giao việc trước khi bật `giao_viec.bat`: đây là BƯỚC KIỂM KHI CHẠY THẬT
 của mọi adapter chờ cổng (S6 principal `tram-kiem`, S7 kho kiểm/remote, 3a-2 file quyền). Chưa chứng minh được → ĐỎ;
-không đánh dấu sẵn sàng bằng bản giả. Mọi lần chạy thật đi qua `chay`/`chay_lenh` tiêm được (test dùng bản giả)."""
+không đánh dấu sẵn sàng bằng bản giả. Mọi lần chạy thật đi qua `chay`/`chay_lenh` tiêm được (test dùng bản giả).
+Lát 3c (D22): mục ghi bản chép — giữ khoá kiểm lại, `tram-kiem` tạo thư mục con + file rồi TỰ dọn, trạm thấy sạch."""
 import getpass
+import os
 import shutil
 import subprocess
 import threading
@@ -11,6 +13,7 @@ from pathlib import Path
 from tram.cau_hinh.du_an import DuAn
 from tram.cau_hinh.giao_viec import CauHinhGiaoViec
 from tram.duong_dan import tram_home
+from tram.giao_viec.ban_chep import KiemLaiDangBan, giu_khoa, ten_ban_chep
 from tram.giao_viec.git_kiem import kho_kiem
 from tram.giao_viec.kho_kiem_tao import url_origin
 from tram.giao_viec.principal_kiem import PrincipalKiem
@@ -19,6 +22,7 @@ from tram.kiem.chay_lenh import chay_mot_lenh, moi_truong_kiem
 from tram.tho.kiem_may import MucKiem
 
 LOI_CHAY = (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError)
+THU_MUC_THU = "tram-giao-kiem-thu"
 
 
 def _muc(ten: str, dat: bool, chi_tiet: str, *, khong_dat: str = "do") -> MucKiem:
@@ -30,18 +34,25 @@ def _ra(chay: Callable, argv: list[str], **kw):
 
 
 def _ghi_duoc(pk: PrincipalKiem, thu_muc: Path | None, chay: Callable) -> MucKiem:
+    ten = "principal: ghi bản chép kiểm"
     if thu_muc is None or not thu_muc.is_dir():
-        return _muc("principal: ghi worktree kiểm", False, f"thu_muc_kiem không có: {thu_muc}")
-    d = thu_muc / "tram-giao-kiem-thu"
-    shutil.rmtree(d, ignore_errors=True)
-    d.mkdir()
+        return _muc(ten, False, f"thu_muc_kiem không có: {thu_muc}")
+    d, ghi = thu_muc / ten_ban_chep(THU_MUC_THU), False
     try:
-        pk.trao(d, chay=chay)
-        ghi = _ra(chay, pk.boc_lenh(["/usr/bin/touch", str(d / "x")])).returncode == 0
-    except LOI_CHAY:
-        ghi = False
-    shutil.rmtree(d, ignore_errors=True)
-    return _muc("principal: ghi worktree kiểm", ghi and not d.exists(), "trao quyền → tram-kiem ghi → trạm xoá được")
+        with giu_khoa():
+            pk.don_sach(chay=chay)
+            try:
+                ghi = all(_ra(chay, pk.boc_lenh(a)).returncode == 0 for a in (
+                    ["/bin/mkdir", str(d)], ["/bin/mkdir", str(d / "con")], ["/usr/bin/touch", str(d / "con" / "x")]))
+                ghi = ghi and (d / "con" / "x").is_file()
+            finally:
+                _ra(chay, pk.boc_lenh(["/bin/rm", "-rf", str(d)]))
+                pk.don_sach(chay=chay)
+    except KiemLaiDangBan:
+        return _muc(ten, False, "đang có lần kiểm lại chạy — chạy lại `tram giao kiem` sau")
+    except LOI_CHAY as e:
+        return _muc(ten, False, f"{type(e).__name__}: {e}"[:200])
+    return _muc(ten, ghi and not os.path.lexists(d), "tram-kiem tạo thư mục con + file → tự dọn → trạm thấy sạch")
 
 
 def _dung_duoc(pk: PrincipalKiem, thu_muc: Path | None, chay_lenh: Callable) -> MucKiem:
@@ -57,7 +68,7 @@ def _dung_duoc(pk: PrincipalKiem, thu_muc: Path | None, chay_lenh: Callable) ->
 def kiem_principal(pk: PrincipalKiem | None, thu_muc: Path | None, *, chay: Callable = subprocess.run,
                    chay_lenh: Callable = chay_mot_lenh, toi: str | None = None) -> list[MucKiem]:
     if pk is None:
-        return [_muc("principal kiểm lại", False, "chưa đặt giao_viec.principal_kiem — chờ S6")]
+        return [_muc("principal kiểm lại", False, "chưa đặt cach_ly.tram_kiem — chờ S6")]
     try:
         id_ = _ra(chay, pk.boc_lenh(["/usr/bin/id", "-un"]))
         env = _ra(chay, pk.boc_lenh(["/usr/bin/env"]), env=moi_truong_kiem({}))
diff --git a/tram/giao_viec/noi_that.py b/tram/giao_viec/noi_that.py
index 9b4312c..42d216b 100644
--- a/tram/giao_viec/noi_that.py
+++ b/tram/giao_viec/noi_that.py
@@ -48,7 +48,7 @@ def dung_bo_that(cg: CauHinhGiaoViec, ch: CauHinhTram, *, bo_dem=None,
     return BoGiaoViec(cac_du_an=lambda: cac_du_an_that(thu_muc_du_an),
                       tao_bd=lambda da: Bd(da.duong_dan, actor=ASSIGNEE), mo_kho=mo_kho_phieu, ch=ch,
                       dong_ho=lambda: datetime.now(timezone.utc), boc=pk.boc_lenh if pk else None,
-                      don_sach=None,                    # 3c Task 5 nối PrincipalKiem.don_sach
+                      don_sach=pk.don_sach if pk else None,
                       kill=pk.kill_nhom if pk else _kill_nhom,
                       doc_beads=DocBeads(bo_dem) if bo_dem is not None else None, thu_muc_kiem=cg.thu_muc_kiem,
                       p4c=nap_phu_thuoc_4c() if cg.bat else PhuThuoc4c())
diff --git a/tram/giao_viec/principal_kiem.py b/tram/giao_viec/principal_kiem.py
index 5cb87e5..79106dd 100644
--- a/tram/giao_viec/principal_kiem.py
+++ b/tram/giao_viec/principal_kiem.py
@@ -1,21 +1,28 @@
-"""Principal kiểm lại của trạm `tram-kiem` (spec 3 §7.3 mục 5; spec 4 §6.2 bước 1, 4) — ADAPTER, chờ spike S6.
+"""Principal kiểm lại của trạm `tram-kiem` (spec 3 §7.3 mục 5; spec 4 §6.2 bước 1, 4) — chờ spike S6.
 
-Cơ chế cách ly (user macOS riêng, sudoers, ACL…) chốt sau S6; mã chỉ biết hai tiền tố argv Đại ca đặt trong
-`~/.tram/cau-hinh.yaml`: `boc` (chạy MỘT lệnh dưới `tram-kiem`) và `trao_quyen` (tài khoản trạm trao quyền ghi
-worktree kiểm cho `tram-kiem`; nhận thêm một đối số là thư mục). Hình dạng chưa xác minh — `tram giao kiem` chạy thật
-từng điều kiện (danh tính, giữ `APP_ENV`, không đọc kho trạm, ghi được worktree, dừng được lệnh quá hạn)."""
-import subprocess
+Lát 3c: MỘT nguồn khai báo — `cach_ly.tram_kiem: user:<tên> | sandbox:<tên>` (cùng cú pháp principal khe, 3a-2 G3;
+đọc qua `tram.cau_hinh.principal_kiem.doc_principal_kiem`). `tu_cach_ly` dựng argv từ `Principal` của 3a-2 — không
+còn argv tự do trong cấu hình: `boc` = `sudo -n -H -u <tên> --preserve-env=… --` (cơ chế sandbox thêm `sandbox-exec -f
+HO_SO_KIEM`), khớp dòng sudoers `dong_sudoers_kiem`. D22: không trao/thu quyền — `tram-kiem` sở hữu bản chép
+(`ban_chep.py`); `don_sach` giết mọi tiến trình của `tram-kiem`, rồi TRẠM tự đếm lại bằng `pgrep` (không qua sudo)."""
 import signal
+import subprocess
+import time
 from collections.abc import Callable
 from dataclasses import dataclass
-from pathlib import Path
+
+from tram.giao_viec.ban_chep import LoiBanChep
+from tram.tho.principal import doc_principal
+from tram.tho.quyen_kiem import HO_SO_KIEM
+
+PGREP = "/usr/bin/pgrep"
 
 
 @dataclass(frozen=True)
 class PrincipalKiem:
     ten: str
     boc: tuple[str, ...]
-    trao_quyen: tuple[str, ...] = ()
+    co_che: str = "user"
 
     def boc_lenh(self, argv: list[str]) -> list[str]:
         """Tham số `boc` của `chay_mot_lenh`/`kiem_lai` (3a-1): argv chạy dưới `tram-kiem`, không qua shell."""
@@ -26,7 +33,24 @@ class PrincipalKiem:
         chay(self.boc_lenh(["/bin/kill", "-s", signal.Signals(sig).name.removeprefix("SIG"),
                            "--", f"-{pgid}"]), capture_output=True, timeout=20)
 
-    def trao(self, thu_muc: Path, *, chay: Callable = subprocess.run) -> None:
-        """Trao quyền ghi `thu_muc` — gọi SAU khi trạm chép môi trường kiểm, TRƯỚC lệnh đầu tiên. Lỗi → ném."""
-        if self.trao_quyen:
-            chay([*self.trao_quyen, str(thu_muc)], check=True, capture_output=True, timeout=60)
+    def don_sach(self, *, chay: Callable = subprocess.run, lan: int = 5, ngu: Callable = time.sleep) -> None:
+        """Gỡ crontab và giết MỌI tiến trình của `tram-kiem` (chạy dưới chính `tram-kiem`), rồi trạm tự đếm bằng
+        `pgrep -U` — không tin lời `tram-kiem`. Còn tiến trình sau `lan` lần, hoặc `pgrep` lỗi → `LoiBanChep`."""
+        for _ in range(lan):
+            chay(self.boc_lenh(["/usr/bin/crontab", "-r"]), capture_output=True, timeout=30)
+            chay(self.boc_lenh(["/usr/bin/pkill", "-KILL", "-U", self.ten]), capture_output=True, timeout=30)
+            r = chay([PGREP, "-U", self.ten], capture_output=True, text=True, timeout=30)
+            if r.returncode == 1:
+                return
+            if r.returncode != 0:
+                raise LoiBanChep(f"pgrep -U {self.ten} lỗi (mã {r.returncode}) — không xác nhận được đã sạch")
+            ngu(0.5)
+        raise LoiBanChep(f"{self.ten} vẫn còn tiến trình sau {lan} lần giết (nguồn tái sinh?) — dừng kiểm lại")
+
+
+def tu_cach_ly(chuoi: str) -> PrincipalKiem:
+    """`cach_ly.tram_kiem` → PrincipalKiem. Sai dạng → `ChuaCoPrincipal` (ValueError)."""
+    p = doc_principal(chuoi)
+    if p.co_che == "sandbox":
+        p = p.voi_ho_so(HO_SO_KIEM)
+    return PrincipalKiem(p.user, tuple(p.boc([])), p.co_che)
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_principal_kiem_hop_nhat.py tests/test_cau_hinh_giao_viec.py tests/test_giao_kiem.py tests/test_noi_giao_viec.py tests/test_noi_4c.py tests/test_cau_hinh_cong_bo_cach_ly.py -q`
Expected: `62 passed`

Run: `uv run pytest -q`
Expected: `N₀ + 31 passed` (2131 — sau đợt 1 + 17; ghép cùng Task 10 → N₀ + 38 = 2138, r47 đo thật)

- [ ] **Step 5: Commit**

```bash
git add tram/cau_hinh/principal_kiem.py tram/giao_viec/principal_kiem.py tram/cau_hinh/giao_viec.py tram/cau_hinh/cach_ly.py tram/giao_viec/noi_that.py tram/giao_viec/kiem_san_sang.py tests/test_principal_kiem_hop_nhat.py tests/test_cau_hinh_giao_viec.py tests/test_giao_kiem.py tests/test_noi_giao_viec.py
git commit -m "feat(cau-hinh): một nguồn principal kiểm lại cach_ly.tram_kiem; PrincipalKiem bỏ trao quyền, thêm don_sach (lát 3c, bs-urj.12, D22)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 6: `cai-dat-tho` có sổ journal (R2, R4) + nhà là bước riêng (R5) + D22; `kiem-cach-ly` đọc nguồn chung

> **Bản r47 (16/10, sau review Codex đợt 5):** đã sửa R4 (đuôi sổ dở, ghi đủ bytes, khoá cài/gỡ) và R5 (biên nhận user tách khỏi hoàn tất nhà). Mã/test dưới đây là bản sửa đầy đủ, đã chạy thử (xem "Ghi chú kiểm plan (r47)"); thay hẳn bản bị chặn.

**Độ khó:** `kho` · **Đợt:** 3 · **Song song với:** Task 7 · **Phải xong trước:** Task 1, Task 5 (và T4 đã ghép)

**Files:**
- Create: `tram/chu/nhat_ky.py`, `tram/chu/so_cai_tho.py`, `tram/chu/dinh_danh.py`, `tram/chu/tai_nguyen.py`, `tram/chu/cai_dat_kiem.py`
- Modify: `tram/chu/cai_dat_tho.py`, `tram/chu/kiem_cach_ly.py`, `tram/chu/lenh_tho.py`
- Modify: `tests/test_chu_tho.py`, `tests/test_tho_lenh_chay.py`
- Test: `tests/he_gia.py` (công cụ, mới), `tests/test_so_cai_tho.py`, `tests/test_dinh_danh_cai.py`, `tests/test_cai_dat_tho_kiem.py`, `tests/test_cai_nha_tho.py` (mới)

**Interfaces:**
- Consumes: Task 1 (`HO_SO_KIEM`, `THU_MUC_CAI`, `goc_hop_le`, `dong_sudoers_kiem`, `ho_so_tram_kiem`); T4 (`thuc_hien` bỏ qua lỗi `sudo launchctl bootout`); Task 5 (`doc_principal_kiem`, `PrincipalKiem`, `tu_cach_ly`, `nap_cau_hinh_giao_viec`); `CONG_MAC_DINH`, `USER_RE`.
- Produces:
  - `nhat_ky.py`: `DangBan(ValueError)`, `khoa(p, thong_bao, *, loi=DangBan)` (flock không chờ), `dong_bo(fd)` (`F_FULLFSYNC`, lỗi thì `fsync`), `ghi_het(p, du)`, `dong_hoan_chinh(du) -> list[bytes]`, `cat_duoi(p) -> bytes`.
  - `so_cai_tho.py`: `PHIEN_BAN = 2`, `KIEU = (user, nha, tep, thu_muc)`, `SU`, `CHUYEN`, `SoCaiDangBan(DangBan)`, `Muc(id, kieu, ten, mong, su, dinh_danh)`, `SoCai(p=None)` + `.giu()` (khoá giao dịch, lồng được), `.muc() -> dict[str, Muc]` (ValueError khi hỏng), `.du_dinh(id, kieu, ten, mong)`, `.ket(id, su, **kw)`, `.da_tao(kieu, ten) -> list[Muc]`, `.co_ghi(kieu, ten) -> bool`; `moi_id()`; `doi_soat(so, quan_sat, khop) -> int`.
  - `dinh_danh.py`: `user(ten, *, chay)` (None chỉ khi `eDSRecordNotFound`, lỗi khác → OSError), `tep(p, *, chay, nhe)`, `thu_muc(p)`, `quan_sat_that(kieu, ten, *, nhe=False)`, `khop(kieu, mong, hien)` (thư mục/nhà: thư mục thật + đúng `mong["uid"]`), `cung(kieu, da, hien)`.
  - `tai_nguyen.py`: `LoiCaiDat(RuntimeError)`, `TaiNguyen(kieu, ten, lenh, mong, nhan=None)` + `.mo_ta()`, `cua_tram(so, kieu, ten, hien)`, `user_cua_tram(so, u, quan_sat) -> dict | None`, `nha_tram(u, so, quan_sat) -> TaiNguyen`, `kiem_truoc(so, ds, *, quan_sat) -> list[str]` (ValueError), `tao(so, tn, *, quan_sat, chay) -> "tao" | "giu" | "nhan"` (LoiCaiDat).
  - `cai_dat_kiem.py`: `NHA_KIEM = "/var/empty"`, `PhanKiem(tep, tai_nguyen, canh_bao)`, `cong_cam`, `tep_root(soan, dich, noi_dung, mode, *, truoc=())`, `phan_kiem(*, kiem, thu_muc_kiem, co_che, tram, quan_ly, soan, khe=(), db_nghiep_vu=(), quan_sat=…)`.
  - `noi_dung_sudoers(*, quan_ly, principal, tram, kiem)`; `user_tram(u, nha) -> TaiNguyen` (chỉ `addUser`); `lap_ke_hoach_tho(*, uv, repo, tram, quan_ly, khe, co_che, kiem=None, thu_muc_kiem=None, db_nghiep_vu=(), so=None, quan_sat=None, chay=subprocess.run) -> KeHoach` — tài nguyên là `buoc` (bước 0: đối soát; user → nhà (trừ `tram-kiem`) → thư mục kiểm → file root), `lenh` chỉ còn `launchctl bootout/bootstrap`; tên user sai `USER_RE` → ValueError.
  - `kiem_cach_ly(principal, *, chay_td=chay_tham_do, doc_pk=doc_principal_kiem)`.
  - CLI: `tram chu cai-dat-tho --khe … --co-che user|sandbox [--quan-ly] [--dong-y]` (không còn `--tram-kiem`; giữ khoá sổ suốt lệnh; cấu hình/sổ lỗi/đang có cài-gỡ khác → mã 2; dừng giữa chừng → mã 1 kèm hướng dẫn `go-cai-dat-tho`); `tram chu kiem-cach-ly [--principal …]`.

- [ ] **Step 1: Viết test thất bại**

`tests/he_gia.py` (mới — công cụ test, không phải test):

```python
"""Hệ thống macOS GIẢ cho test cài/gỡ máy thợ (lát 3c R2, CHỈ DÙNG TRONG TEST): user, nhà, file root, thư mục — KHÔNG
sudo, không dscl/sysadminctl thật. `sysadminctl -addUser` trên user có sẵn KHÔNG báo lỗi (như máy thật: mã thoát
không đáng tin) — chỉ quan sát định danh mới biết user là của ai. `add_tao_nha`: giả lập `addUser` tự tạo nhà (S6 đo
hành vi thật); `dung_lai_uid`: UID mới = UID trống nhỏ nhất ≥ 501 (như macOS); `-deleteUser` không `-keepHome` xoá nhà;
`createhomedir` và `sudo -u <u> mkdir` tạo thư mục thuộc UID của user đó."""
import hashlib
import itertools
import subprocess
from pathlib import Path


class HeGia:
    def __init__(self, add_tao_nha: bool = False, dung_lai_uid: bool = False):
        self.user: dict[str, dict] = {}
        self.tep: dict[str, str] = {}
        self.thu_muc: dict[str, int] = {}
        self.chu: dict[str, int] = {}             # chủ của thư mục (mặc định root = 0)
        self.lenh: list[str] = []
        self.hong: set[str] = set()               # tiền tố lệnh (không kể sudo) trả lỗi
        self.truoc: dict[str, callable] = {}      # tiền tố lệnh → việc xảy ra ngay trước lệnh (đua)
        self.add_tao_nha, self.dung_lai_uid = add_tao_nha, dung_lai_uid
        self._so = itertools.count(501)

    def them_user(self, ten: str, ten_day_du: str = "người khác") -> None:
        dung = {u["uid"] for u in self.user.values()}
        uid = min(set(range(501, 600)) - dung) if self.dung_lai_uid else next(self._so)
        self.user[ten] = {"uid": uid, "guid": f"GUID-{ten}-{uid}", "ten_day_du": ten_day_du}

    def them_nha(self, ten: str, uid: int) -> None:
        self.thu_muc[f"/Users/{ten}"], self.chu[f"/Users/{ten}"] = next(self._so), uid

    def quan_sat(self, kieu: str, ten: str, *, nhe: bool = False) -> dict | None:
        if kieu == "user":
            return dict(self.user[ten]) if ten in self.user else None
        if kieu == "tep":
            return None if ten not in self.tep else {"uid": 0, **({} if nhe else {"sha256": self.tep[ten]})}
        return {"ino": self.thu_muc[ten], "uid": self.chu.get(ten, 0)} if ten in self.thu_muc else None

    def chay(self, c: list[str], check: bool = False, **kw) -> subprocess.CompletedProcess:
        self.lenh.append(" ".join(c))
        x = c[1:] if c[0] == "sudo" else c
        ai, x = (x[1], x[2:]) if x[0] == "-u" else (None, x)
        for tien_to, viec in self.truoc.items():
            if " ".join(x).startswith(tien_to):
                viec()
        ok = not any(" ".join(x).startswith(h) for h in self.hong) and self._lam(x, ai)
        if not ok and check:
            raise subprocess.CalledProcessError(1, c)
        return subprocess.CompletedProcess(c, 0 if ok else 1, "", "")

    def _lam(self, x: list[str], ai: str | None = None) -> bool:
        if x[:2] == ["sysadminctl", "-addUser"] and x[2] not in self.user:
            self.them_user(x[2], x[x.index("-fullName") + 1])
            nha = x[x.index("-home") + 1]
            if self.add_tao_nha and nha.startswith("/Users/") and nha not in self.thu_muc:
                self.them_nha(x[2], self.user[x[2]]["uid"])
        elif x[:2] == ["sysadminctl", "-deleteUser"]:
            self.user.pop(x[2], None)
            if "-keepHome" not in x:
                self.thu_muc.pop(f"/Users/{x[2]}", None)
        elif x[0] == "createhomedir" and x[-1] in self.user:
            if f"/Users/{x[-1]}" not in self.thu_muc:
                self.them_nha(x[-1], self.user[x[-1]]["uid"])
        elif x[:2] in (["install", "-d"], ["/bin/mkdir", "-m"]):
            self.thu_muc[x[-1]], self.chu[x[-1]] = next(self._so), self.user[ai]["uid"] if ai in self.user else 0
        elif x[0] == "install":
            self.tep[x[-1]] = hashlib.sha256(Path(x[-2]).read_bytes()).hexdigest()
        elif x[:2] == ["rm", "-f"]:
            self.tep.pop(x[2], None)
        elif x[:2] in (["/bin/rm", "-rf"], ["rm", "-rf"]):
            self.thu_muc.pop(x[2], None)
        elif x[0] == "rmdir":
            if any(p.startswith(x[1] + "/") for p in [*self.tep, *self.thu_muc]):
                return False
            self.thu_muc.pop(x[1], None)
        return True
```

`tests/test_so_cai_tho.py` (mới):

```python
"""Sổ cài đặt v2 (lát 3c R2, Codex F02; R4 review đợt 5): journal chỉ ghi thêm, đuôi dở được cắt (giữ bằng chứng) TRƯỚC
khi nối, ghi đủ bytes, khoá cài/gỡ; đối soát khi crash; định danh user UID + GeneratedUID, nhà thuộc UID của user.
Không dscl/sudo thật — `HeGia`, `tmp_path`."""
import json
import os

import pytest

from he_gia import HeGia
from tram.chu import nhat_ky
from tram.chu.dinh_danh import khop
from tram.chu.so_cai_tho import SoCai, SoCaiDangBan, doi_soat

DU_DINH = '{"v": 2, "id": "a1", "su": "du_dinh", "kieu": "user", "ten": "u", "mong": {"ten_day_du": "tram u a1"}}\n'


def test_ghi_them_trang_thai_la_ban_ghi_cuoi(tmp_path):
    so = SoCai(tmp_path / "so.jsonl")
    so.du_dinh("a1", "user", "tram-kiem", {"ten_day_du": "tram tram-kiem a1"})
    so.ket("a1", "da_tao", dinh_danh={"uid": 502, "guid": "G1"})
    so.du_dinh("b2", "tep", "/etc/x", {"sha256": "h"})
    m = so.muc()
    assert (m["a1"].su, m["a1"].dinh_danh["guid"], m["b2"].su) == ("da_tao", "G1", "du_dinh")
    assert so.co_ghi("tep", "/etc/x") and not so.co_ghi("user", "khac")
    assert [x.id for x in so.da_tao("user", "tram-kiem")] == ["a1"]


def test_dong_cuoi_ghi_do_bi_bo_dong_hong_thi_tu_choi(tmp_path):
    so = SoCai(tmp_path / "so.jsonl")
    so.du_dinh("a1", "user", "u", {})
    with open(so.p, "a") as f:
        f.write('{"v": 2, "id": "a1", "su": "da_t')                   # crash giữa lúc ghi: dòng cuối không có \n
    assert so.muc()["a1"].su == "du_dinh"
    for hong in ('khong-phai-json\n', '{"v": 2, "id": "zz", "su": "da_go"}\n', '{"v": 1, "id": "a1"}\n'):
        so.p.write_text('{"v": 2, "id": "a1", "su": "du_dinh", "kieu": "user", "ten": "u", "mong": {}}\n' + hong)
        with pytest.raises(ValueError, match="hỏng"):
            so.muc()


@pytest.mark.parametrize("duoi", [b'{"v": 2, "id": "a1", "su": "da_t', b'{"v": 2, "id": "a1", "ly_do": "t\xe1\xba',
                                  b'{"v": 2, "id": "a1", "su": "khong_tao"}'])
def test_duoi_do_bi_cat_giu_bang_chung_roi_moi_noi(tmp_path, duoi):
    """R4: du_dinh hoàn chỉnh + đuôi dở (ASCII, UTF-8 dở, JSON đủ mà thiếu \\n) → đối soát nối vào DÒNG MỚI."""
    he, so = HeGia(), SoCai(tmp_path / "so.jsonl")
    so.p.write_bytes(DU_DINH.encode() + duoi)
    he.them_user("u", "tram u a1")                                     # lệnh tạo đã chạy, crash lúc ghi da_tao
    assert so.muc()["a1"].su == "du_dinh" and doi_soat(so, he.quan_sat, khop) == 1
    du = so.p.read_bytes()
    assert du.startswith(DU_DINH.encode()) and du.endswith(b"\n")
    assert [json.loads(d)["su"] for d in du.decode().splitlines()] == ["du_dinh", "da_tao"]
    assert (tmp_path / "so.jsonl.duoi-hong").read_bytes() == duoi + b"\n"
    so.ket("a1", "da_go")
    assert so.muc()["a1"].su == "da_go" and doi_soat(so, he.quan_sat, khop) == 0


def test_short_write_va_loi_giua_chung_khong_lam_hong_so(tmp_path, monkeypatch):
    so, goc, lan = SoCai(tmp_path / "so.jsonl"), os.write, []

    def ghi_ngan(fd, b):                                               # mỗi lần chỉ ghi 7 bytes
        return goc(fd, b[:7])
    monkeypatch.setattr(nhat_ky.os, "write", ghi_ngan)
    so.du_dinh("a1", "user", "u", {"ten_day_du": "tram u a1"})
    assert so.muc()["a1"].su == "du_dinh"

    def het_cho(fd, b):                                                # ghi được 10 bytes rồi hết chỗ
        lan.append(1)
        if len(lan) > 1:
            raise OSError(28, "No space left on device")
        return goc(fd, b[:10])
    monkeypatch.setattr(nhat_ky.os, "write", het_cho)
    with pytest.raises(OSError):
        so.ket("a1", "da_tao", dinh_danh={"uid": 1, "guid": "G"})
    monkeypatch.setattr(nhat_ky.os, "write", goc)
    assert so.muc()["a1"].su == "du_dinh"                              # đuôi dở bị bỏ khi đọc
    so.ket("a1", "da_tao", dinh_danh={"uid": 1, "guid": "G"})
    assert so.muc()["a1"].dinh_danh == {"uid": 1, "guid": "G"} and so.p.read_bytes().count(b"\n") == 2


def test_khoa_so_chan_ghi_cua_lan_cai_go_khac(tmp_path):
    a, b = SoCai(tmp_path / "so.jsonl"), SoCai(tmp_path / "so.jsonl")
    with a.giu():
        a.du_dinh("a1", "user", "u", {})                               # cùng đối tượng: dùng lại khoá
        with pytest.raises(SoCaiDangBan, match="đang có cài/gỡ khác"):
            b.du_dinh("b2", "user", "v", {})
    b.du_dinh("b2", "user", "v", {})
    assert list(a.muc()) == ["a1", "b2"]


def test_doi_soat_crash_truoc_va_sau_lenh_tao(tmp_path):
    he, so = HeGia(), SoCai(tmp_path / "so.jsonl")
    he.them_user("sau-tao", "tram sau-tao c3")                        # lệnh đã chạy, crash trước da_tao
    he.them_user("co-san")                                             # có sẵn, RealName không mang mã
    for id_, u in (("a1", "truoc-tao"), ("c3", "sau-tao"), ("d4", "co-san")):
        so.du_dinh(id_, "user", u, {"ten_day_du": f"tram {u} {id_}"})
    assert doi_soat(so, he.quan_sat, khop) == 3 and doi_soat(so, he.quan_sat, khop) == 0
    m = so.muc()
    assert (m["a1"].su, m["c3"].su, m["d4"].su) == ("khong_tao", "da_tao", "khong_tao")
    assert m["c3"].dinh_danh["guid"] == he.user["sau-tao"]["guid"]


def test_khoa_giu_boi_tien_trinh_khac(tmp_path):
    import subprocess
    import sys
    p = tmp_path / "so.jsonl"
    giu = subprocess.Popen([sys.executable, "-c", "import sys, time; from tram.chu.so_cai_tho import SoCai\n"
                            f"with SoCai(__import__('pathlib').Path({str(p)!r})).giu():\n"
                            "    print('giu', flush=True); time.sleep(30)"], stdout=subprocess.PIPE, text=True)
    try:
        assert giu.stdout.readline().strip() == "giu"
        with pytest.raises(SoCaiDangBan):
            SoCai(p).du_dinh("a1", "user", "u", {})
    finally:
        giu.kill()
        giu.wait()
    assert not p.exists() or p.read_bytes() == b""
```

`tests/test_dinh_danh_cai.py` (mới):

```python
"""Định danh cho sổ cài đặt (lát 3c R2; R5/Q02 review đợt 5): user UID + GeneratedUID qua `dscl`, nhà/thư mục thuộc
đúng UID; `dscl` lỗi khác "không có bản ghi" không bị hiểu là "không còn". Không dscl thật — `chay` giả."""
from types import SimpleNamespace

import pytest

from tram.chu.dinh_danh import _doc_dscl, cung, khop, user


def test_dinh_danh_user_doc_dscl_va_ten_tai_su_dung():
    hien = _doc_dscl("GeneratedUID: AB-12\nRealName:\n tram tram-kiem a1\nUniqueID: 502\n")
    assert hien == {"uid": 502, "guid": "AB-12", "ten_day_du": "tram tram-kiem a1"}
    assert khop("user", {"ten_day_du": "tram tram-kiem a1"}, hien) and cung("user", hien, dict(hien))
    assert not cung("user", hien, {**hien, "guid": "CD-34"})           # xoá rồi tạo lại cùng tên: khác GeneratedUID
    assert khop("nha", {"uid": 502}, {"ino": 9, "uid": 502}) and not khop("nha", {"uid": 502}, {"ino": 9, "uid": 7})
    assert not khop("nha", {"uid": 502}, {"loai": "khac", "uid": 502}) and not khop("nha", {"uid": None}, {"ino": 9})
    with pytest.raises(ValueError):
        _doc_dscl("RealName: x\n")


@pytest.mark.parametrize("ma, ra, mong", [(56, "DS Error: -14136 (eDSRecordNotFound)", None), (1, "lỗi", OSError)])
def test_dscl_khong_co_ban_ghi_khac_dscl_loi(ma, ra, mong):
    chay = lambda *a, **kw: SimpleNamespace(returncode=ma, stdout="", stderr=ra)   # noqa: E731
    if mong is None:
        assert user("tram-kiem", chay=chay) is None
    else:
        with pytest.raises(OSError):
            user("tram-kiem", chay=chay)
```

`tests/test_cai_dat_tho_kiem.py` (mới):

```python
"""`tram chu cai-dat-tho` (lát 3c): phần `tram-kiem` theo D22 (không dòng sudoers root, `tram-kiem` tự tạo thư mục gốc
bản chép) và cài CÓ SỔ theo R2 (du_dinh trước lệnh, da_tao kèm định danh sau quan sát; thứ có sẵn không bị nhận).
KHÔNG sudo/sysadminctl/launchctl thật — `HeGia` thay hệ thống."""
from pathlib import Path
from types import SimpleNamespace

import pytest

from he_gia import HeGia
from tram.chu import lenh_tho
from tram.chu.cai_dat import in_ke_hoach, thuc_hien
from tram.chu.cai_dat_tho import SUDOERS, lap_ke_hoach_tho
from tram.chu.so_cai_tho import SoCai
from tram.chu.tai_nguyen import LoiCaiDat
from tram.giao_viec.principal_kiem import tu_cach_ly
from tram.tho.quyen_kiem import HO_SO_KIEM, THU_MUC_CAI


def ke_hoach(tmp_path, he=None, chuoi="user:tram-kiem", co_che="user", khe=None):
    he = he or HeGia()
    return lap_ke_hoach_tho(uv="uv", repo=Path("/r"), tram="hung", quan_ly="tram-tho", co_che=co_che,
                            khe=khe or {"claude-1": "tram-k-1"}, kiem=tu_cach_ly(chuoi), thu_muc_kiem=tmp_path / "kiem",
                            db_nghiep_vu=("127.0.0.1:3306",), quan_sat=he.quan_sat, chay=he.chay)


def test_sudoers_chi_runas_tram_kiem_va_tram_kiem_tu_tao_thu_muc(tram_home_tam, tmp_path):
    kh, soan = ke_hoach(tmp_path), tram_home_tam / "cai-dat-tho"
    sud = kh.tep[soan / "tram-tho.sudoers"].decode()
    assert sud.splitlines()[-1] == "hung ALL=(tram-kiem) NOPASSWD:SETENV: ALL" and "root" not in sud
    buoc = [m for m, _ in kh.buoc]
    assert f"[tạo] thu_muc {tmp_path}/kiem: sudo -u tram-kiem /bin/mkdir -m 0755 {tmp_path}/kiem" in buoc
    assert soan / HO_SO_KIEM.name not in kh.tep and not any(str(THU_MUC_CAI) in m for m in buoc)
    assert "D22" in in_ke_hoach(kh) and "go-cai-dat-tho" in in_ke_hoach(kh) and buoc[0].startswith("Đối soát")


def test_sandbox_cai_ho_so_co_dinh_va_ghim_sudoers(tram_home_tam, tmp_path):
    kh, soan = ke_hoach(tmp_path, chuoi="sandbox:tram-kiem", co_che="sandbox"), tram_home_tam / "cai-dat-tho"
    hs = kh.tep[soan / HO_SO_KIEM.name].decode()
    assert f'(subpath "{tram_home_tam}")' in hs and '(subpath "/Users/tram-tho/.tram")' in hs and '"*:3306"' in hs
    assert kh.tep[soan / "tram-tho.sudoers"].decode().splitlines()[-1].endswith(f"sandbox-exec -f {HO_SO_KIEM} *")
    buoc = " | ".join(m for m, _ in kh.buoc)
    assert f"install -d -o root -g wheel -m 0755 {THU_MUC_CAI}" in buoc
    assert f"install -m 0644 -o root -g wheel {soan / HO_SO_KIEM.name} {HO_SO_KIEM}" in buoc


def test_lech_co_che_trung_user_khe_hoac_thieu_thu_muc_la_loi(tmp_path):
    with pytest.raises(ValueError, match="khác --co-che"):
        ke_hoach(tmp_path, chuoi="sandbox:tram-kiem")
    with pytest.raises(ValueError, match="user riêng"):
        ke_hoach(tmp_path, chuoi="sandbox:tram-k-1", co_che="sandbox")
    with pytest.raises(ValueError, match="thu_muc_kiem"):
        lap_ke_hoach_tho(uv="uv", repo=Path("/r"), tram="hung", quan_ly="q", khe={}, co_che="user",
                         kiem=tu_cach_ly("user:tram-kiem"), quan_sat=HeGia().quan_sat)


def test_thuc_hien_ghi_du_dinh_truoc_da_tao_kem_dinh_danh_sau(tram_home_tam, tmp_path):
    he = HeGia()
    thuc_hien(ke_hoach(tmp_path, he), chay=he.chay)
    muc = SoCai().muc().values()
    assert {m.su for m in muc} == {"da_tao"} and len(muc) == 8     # 3 user, 2 nhà, thư mục kiểm, sudoers, daemon
    assert sorted(m.ten for m in muc if m.kieu == "nha") == ["/Users/tram-k-1", "/Users/tram-tho"]
    assert "-home /var/empty" in next(x for x in he.lenh if "-addUser tram-kiem" in x)    # C01: không nhà ghi được
    assert not any("createhomedir -c -u tram-kiem" in x for x in he.lenh)
    u = next(m for m in muc if m.ten == "tram-kiem")
    assert u.dinh_danh == he.user["tram-kiem"] and he.user["tram-kiem"]["ten_day_du"] == f"tram tram-kiem {u.id}"
    assert he.lenh.index(f"sudo visudo -cf {tram_home_tam}/cai-dat-tho/tram-tho.sudoers") < next(
        i for i, x in enumerate(he.lenh) if x.endswith(str(SUDOERS)))


def test_user_co_san_khong_do_tram_tao_thi_tu_choi_cai(tram_home_tam, tmp_path):
    he = HeGia()
    he.them_user("tram-kiem")
    with pytest.raises(ValueError, match="không cài đè"):
        ke_hoach(tmp_path, he)
    assert not SoCai().p.exists() and he.lenh == []


def test_user_xuat_hien_giua_chung_thi_khong_nhan_la_cua_tram(tram_home_tam, tmp_path):
    he = HeGia()
    kh = ke_hoach(tmp_path, he)
    he.truoc["sysadminctl -addUser tram-kiem"] = lambda: he.them_user("tram-kiem")     # có sẵn ngay trước addUser
    with pytest.raises(LoiCaiDat):
        thuc_hien(kh, chay=he.chay)
    su = {m.ten: m.su for m in SoCai().muc().values()}
    assert su == {"tram-k-1": "da_tao", "tram-kiem": "khong_tao"} and he.user["tram-kiem"]["ten_day_du"] == "người khác"


def test_cai_lai_giu_user_cua_tram_thay_file_doi_noi_dung(tram_home_tam, tmp_path):
    he = HeGia()
    thuc_hien(ke_hoach(tmp_path, he), chay=he.chay)
    he.lenh.clear()
    thuc_hien(ke_hoach(tmp_path, he, khe={"claude-1": "tram-k-1", "claude-2": "tram-k-2"}), chay=he.chay)
    assert [x for x in he.lenh if "-addUser" in x] == [x for x in he.lenh if "-addUser tram-k-2" in x] != []
    sud = [m for m in SoCai().muc().values() if m.ten == str(SUDOERS)]
    assert [m.su for m in sud] == ["da_tao", "da_tao"] and sud[0].dinh_danh != sud[1].dinh_danh


def test_lenh_doc_cau_hinh_khong_con_co_tram_kiem(tram_home_tam, tmp_path, monkeypatch, capsys):
    tram_home_tam.mkdir(parents=True, exist_ok=True)
    (tram_home_tam / "cau-hinh.yaml").write_text(f"cach_ly:\n  tram_kiem: user:tram-kiem\n"
                                                 f"giao_viec:\n  thu_muc_kiem: {tmp_path}/kiem\n")
    monkeypatch.setattr("tram.chu.dinh_danh.quan_sat_that", HeGia().quan_sat)
    monkeypatch.setattr("builtins.input", lambda _: "khong")
    args = SimpleNamespace(khe=["claude-1=tram-k-1"], quan_ly="tram-tho", co_che="user", dong_y=False)
    assert lenh_tho._cai_dat_tho(args) == 1 and f"{tmp_path}/kiem" in capsys.readouterr().out
    assert lenh_tho._cai_dat_tho(SimpleNamespace(**{**vars(args), "co_che": "sandbox"})) == 2
    assert "khác --co-che" in capsys.readouterr().err
```

`tests/test_cai_nha_tho.py` (mới):

```python
"""R5 review đợt 5: biên nhận user (`addUser`) KHÁC hoàn tất nhà (`createhomedir`) — mỗi thứ một bản ghi sổ. Chạy lại
chỉ làm phần còn thiếu, giữ UID/GUID; nhà có sẵn mà không thuộc user của trạm là nhà lạ → từ chối, không ghi đè;
`addUser` tự tạo nhà thì nhận theo đúng UID. R4: đang có lần gỡ giữ khoá sổ thì cài không làm gì. `HeGia` — KHÔNG
sysadminctl/createhomedir/sudo thật."""
from pathlib import Path
from types import SimpleNamespace

import pytest

from he_gia import HeGia
from tram.chu import lenh_tho
from tram.chu.cai_dat import thuc_hien
from tram.chu.cai_dat_tho import lap_ke_hoach_tho
from tram.chu.so_cai_tho import SoCai
from tram.chu.tai_nguyen import LoiCaiDat
from tram.giao_viec.principal_kiem import tu_cach_ly


def ke_hoach(tmp_path, he):
    return lap_ke_hoach_tho(uv="uv", repo=Path("/r"), tram="hung", quan_ly="tram-tho", co_che="user",
                            khe={"claude-1": "tram-k-1"}, kiem=tu_cach_ly("user:tram-kiem"),
                            thu_muc_kiem=tmp_path / "kiem", quan_sat=he.quan_sat, chay=he.chay)


def su(kieu: str) -> dict[str, str]:
    return {m.ten: m.su for m in SoCai().muc().values() if m.kieu == kieu}        # bản ghi mới nhất của mỗi tên


def mat_dien():
    raise SystemExit("mất điện ngay trước createhomedir")


@pytest.mark.parametrize("hong", ["lenh-loi", "crash"])
def test_hong_giua_addUser_va_createhomedir_chay_lai_chi_tao_nha(tram_home_tam, tmp_path, hong):
    he = HeGia()
    if hong == "lenh-loi":
        he.hong.add("createhomedir -c -u tram-k-1")
    else:
        he.truoc["createhomedir -c -u tram-k-1"] = mat_dien
    with pytest.raises((LoiCaiDat, SystemExit)):
        thuc_hien(ke_hoach(tmp_path, he), chay=he.chay)
    truoc = dict(he.user["tram-k-1"])
    assert su("user")["tram-k-1"] == "da_tao" and "/Users/tram-k-1" not in he.thu_muc
    he.hong.clear(), he.truoc.clear(), he.lenh.clear()
    thuc_hien(ke_hoach(tmp_path, he), chay=he.chay)                   # chạy lại: chỉ bước còn thiếu
    assert he.user["tram-k-1"] == truoc and not any("-addUser" in x for x in he.lenh)
    assert "sudo createhomedir -c -u tram-k-1" in he.lenh and he.chu["/Users/tram-k-1"] == truoc["uid"]
    assert su("nha") == {"/Users/tram-k-1": "da_tao", "/Users/tram-tho": "da_tao"}


def test_nha_co_san_truoc_user_la_nha_la_tu_choi_cai(tram_home_tam, tmp_path):
    he = HeGia()
    he.them_nha("tram-k-1", 777)                     # nhà cũ (keepHome của user đã xoá), sổ không ghi
    with pytest.raises(ValueError, match="nha /Users/tram-k-1"):
        ke_hoach(tmp_path, he)
    assert he.lenh == [] and not SoCai().p.exists() and he.chu["/Users/tram-k-1"] == 777


def test_nha_la_xuat_hien_sau_khi_user_cua_tram_da_co_thi_khong_nhan(tram_home_tam, tmp_path):
    he = HeGia()
    he.hong.add("createhomedir -c -u tram-k-1")
    with pytest.raises(LoiCaiDat):
        thuc_hien(ke_hoach(tmp_path, he), chay=he.chay)
    he.hong.clear()
    he.them_nha("tram-k-1", 777)                     # có người khác tạo, chủ không phải UID của user trạm
    with pytest.raises(ValueError, match="nha /Users/tram-k-1"):
        ke_hoach(tmp_path, he)
    assert he.chu["/Users/tram-k-1"] == 777 and su("nha")["/Users/tram-k-1"] == "khong_tao"


def test_addUser_tu_tao_nha_thi_nhan_dung_uid(tram_home_tam, tmp_path):
    he = HeGia(add_tao_nha=True)                     # S6 đo: sysadminctl có tự tạo nhà hay không
    thuc_hien(ke_hoach(tmp_path, he), chay=he.chay)
    assert not any(x.startswith("sudo createhomedir") for x in he.lenh)
    nha = [m for m in SoCai().muc().values() if m.kieu == "nha"]
    assert {m.su for m in nha} == {"da_tao"} and all(m.dinh_danh["uid"] == m.mong["uid"] for m in nha)


def test_dang_go_thi_cai_dat_tho_khong_lam_gi(tram_home_tam, tmp_path, monkeypatch, capsys):
    tram_home_tam.mkdir(parents=True, exist_ok=True)
    (tram_home_tam / "cau-hinh.yaml").write_text(f"cach_ly:\n  tram_kiem: user:tram-kiem\n"
                                                 f"giao_viec:\n  thu_muc_kiem: {tmp_path}/kiem\n")
    monkeypatch.setattr("tram.chu.dinh_danh.quan_sat_that", HeGia().quan_sat)
    monkeypatch.setattr("tram.chu.cai_dat.thuc_hien", lambda kh: pytest.fail("không được thực hiện"))
    args = SimpleNamespace(khe=["claude-1=tram-k-1"], quan_ly="tram-tho", co_che="user", dong_y=True)
    with SoCai().giu():
        assert lenh_tho._cai_dat_tho(args) == 2
    assert "đang có cài/gỡ khác" in capsys.readouterr().err


def test_crash_sau_addUser_tu_tao_nha_chay_lai_chi_lam_phan_thieu(tram_home_tam, tmp_path):
    he = HeGia(add_tao_nha=True)

    def chay(c, check=False, **kw):
        r = he.chay(c, check=check)
        if "-addUser tram-k-1" in " ".join(c):
            raise SystemExit("mất điện sau addUser, trước da_tao")
        return r
    with pytest.raises(SystemExit):
        thuc_hien(lap_ke_hoach_tho(uv="uv", repo=Path("/r"), tram="hung", quan_ly="tram-tho", co_che="user",
                                   khe={"claude-1": "tram-k-1"}, kiem=tu_cach_ly("user:tram-kiem"),
                                   thu_muc_kiem=tmp_path / "kiem", quan_sat=he.quan_sat, chay=chay), chay=chay)
    truoc = dict(he.user["tram-k-1"])
    thuc_hien(ke_hoach(tmp_path, he), chay=he.chay)                   # du_dinh dở + nhà tự tạo: vẫn nhận đúng
    assert he.user["tram-k-1"] == truoc and su("user")["tram-k-1"] == "da_tao"
    assert su("nha")["/Users/tram-k-1"] == "da_tao"


def test_thu_muc_kiem_cua_nguoi_khac_sau_du_dinh_do_khong_bi_nhan(tram_home_tam, tmp_path):
    he = HeGia()
    he.truoc[f"/bin/mkdir -m 0755 {tmp_path}/kiem"] = mat_dien
    with pytest.raises(SystemExit):
        thuc_hien(ke_hoach(tmp_path, he), chay=he.chay)
    he.truoc.clear()
    he.thu_muc[f"{tmp_path}/kiem"], he.chu[f"{tmp_path}/kiem"] = 99, 777    # người khác tạo đúng đường dẫn đó
    with pytest.raises(LoiCaiDat):
        thuc_hien(ke_hoach(tmp_path, he), chay=he.chay)
    assert su("thu_muc")[f"{tmp_path}/kiem"] == "khong_tao" and he.chu[f"{tmp_path}/kiem"] == 777
```

`tests/test_chu_tho.py`, `tests/test_tho_lenh_chay.py` (sửa — bản vá):

```diff
diff --git a/tests/test_chu_tho.py b/tests/test_chu_tho.py
index 6e20738..2a20d4e 100644
--- a/tests/test_chu_tho.py
+++ b/tests/test_chu_tho.py
@@ -7,10 +7,12 @@ from types import SimpleNamespace
 
 import pytest
 
+from he_gia import HeGia
 from tram.chu import lenh_tho
 from tram.chu.cai_dat import in_ke_hoach
-from tram.chu.cai_dat_tho import lap_ke_hoach_tho
+from tram.chu.cai_dat_tho import DAEMON, lap_ke_hoach_tho
 from tram.chu.kiem_cach_ly import kiem_cach_ly
+from tram.giao_viec.principal_kiem import tu_cach_ly
 from tram.phieu.kho import mo_kho_phieu
 from tram.phieu.may import xac_thuc_may
 from tram.tho.kiem_am import KetQuaThamDo
@@ -19,30 +21,33 @@ from tram.tho.kiem_am import KetQuaThamDo
 def ke_hoach(**kw):
     return lap_ke_hoach_tho(uv="/opt/homebrew/bin/uv", repo=Path("/r"), tram="hung", quan_ly="tram-tho",
                             khe={"claude-1": "tram-k-b-claude-1", "claude-2": "tram-k-b-claude-2"},
-                            co_che="user", tram_kiem="tram-kiem", **kw)
+                            co_che="user", kiem=tu_cach_ly("user:tram-kiem"),
+                            thu_muc_kiem=Path("/Users/Shared/tram-kiem"), quan_sat=HeGia().quan_sat, **kw)
 
 
 def test_ke_hoach_user_moi_khe_sudoers_launchd(tram_home_tam):
     kh = ke_hoach()
     sud = kh.tep[tram_home_tam / "cai-dat-tho" / "tram-tho.sudoers"].decode()
     assert "tram-tho ALL=(tram-k-b-claude-1,tram-k-b-claude-2) NOPASSWD:SETENV: ALL" in sud
-    assert "hung ALL=(tram-kiem) NOPASSWD:SETENV: ALL" in sud
+    assert "hung ALL=(tram-kiem) NOPASSWD:SETENV: ALL" in sud and "(root)" not in sud              # D22
     pl = plistlib.loads(kh.tep[tram_home_tam / "cai-dat-tho" / "vn.tram.tho.plist"])
     assert pl["UserName"] == "tram-tho" and pl["ProgramArguments"][-3:] == ["tram", "tho", "chay"]
-    lenh = [" ".join(x) for x in kh.lenh]
-    assert sum(x.startswith("sudo sysadminctl -addUser") for x in lenh) == 4
-    assert lenh.index(f"sudo visudo -cf {tram_home_tam}/cai-dat-tho/tram-tho.sudoers") < next(
-        i for i, x in enumerate(lenh) if x.endswith("/etc/sudoers.d/tram-tho"))
+    buoc = [m for m, _ in kh.buoc]                                       # 3c R2: tài nguyên đi qua sổ
+    assert sum("sudo sysadminctl -addUser" in x for x in buoc) == 4
+    sud_b = next(x for x in buoc if x.startswith("[tạo] tep /etc/sudoers.d/tram-tho:"))
+    assert sud_b.index("sudo visudo -cf") < sud_b.index("sudo install -m 0440")
+    assert [" ".join(x) for x in kh.lenh] == ["sudo launchctl bootout system/vn.tram.tho",
+                                              f"sudo launchctl bootstrap system {DAEMON}"]
     assert "CHƯA CHỐT" in in_ke_hoach(kh) and "nhan-token" in in_ke_hoach(kh)
     with pytest.raises(ValueError):
-        lap_ke_hoach_tho(uv="uv", repo=Path("/r"), tram="h", quan_ly="q", khe={}, co_che="ca-hai", tram_kiem=None)
+        lap_ke_hoach_tho(uv="uv", repo=Path("/r"), tram="h", quan_ly="q", khe={}, co_che="ca-hai")
 
 
 def test_cai_dat_tho_khong_dong_y_thi_khong_lam_gi(monkeypatch, capsys):
     monkeypatch.setattr("builtins.input", lambda _: "khong")
     monkeypatch.setattr("tram.chu.cai_dat.thuc_hien", lambda kh: pytest.fail("không được thực hiện"))
-    args = SimpleNamespace(khe=["claude-1=tram-k-b-claude-1"], quan_ly="tram-tho", co_che="sandbox", tram_kiem=None,
-                           dong_y=False)
+    monkeypatch.setattr("tram.chu.dinh_danh.quan_sat_that", HeGia().quan_sat)
+    args = SimpleNamespace(khe=["claude-1=tram-k-b-claude-1"], quan_ly="tram-tho", co_che="sandbox", dong_y=False)
     assert lenh_tho._cai_dat_tho(args) == 1 and "Không làm gì" in capsys.readouterr().out
 
 
@@ -62,14 +67,15 @@ def test_cap_token_may_chi_vao_ong(monkeypatch, capsys):
 def test_kiem_cach_ly_du_bo_duoi_sudo_va_canh_bao_kenh_header(tram_home_tam):
     tram_home_tam.mkdir(parents=True, exist_ok=True)
     (tram_home_tam / "cau-hinh.yaml").write_text("dai_ca_logins: [dai-ca@x]\nten_may_b: b.ts.net\n"
-                                                 "cach_ly: {db_nghiep_vu: ['127.0.0.1:3306']}\n")
+                                                 "cach_ly: {db_nghiep_vu: ['127.0.0.1:3306'],\n"
+                                                 "          tram_kiem: user:tram-kiem}\n")
     da = {}
 
     def chay_td(ds, *, boc, env):
         da["boc"], da["ten"] = boc(["/bin/cat", "x"]), [t.ten for t in ds]
         return [KetQuaThamDo(t.ten, "API" not in t.ten, "mã 0") for t in ds]
-    van_ban, ma = kiem_cach_ly(["user:tram-k-b-claude-1", "rac"], tram_kiem="user:tram-kiem", chay_td=chay_td)
+    van_ban, ma = kiem_cach_ly(["user:tram-k-b-claude-1", "rac"], chay_td=chay_td)
     assert ma == 1 and "header GIẢ ĐƯỢC" in van_ban and "[ĐỎ] rac:" in van_ban
-    assert da["boc"] == ["/usr/bin/sudo", "-u", "tram-kiem", "-H", "--", "/bin/cat", "x"]
+    assert da["boc"] == tu_cach_ly("user:tram-kiem").boc_lenh(["/bin/cat", "x"])      # đúng argv của kiểm lại (3c)
     assert "kết nối DB nghiệp vụ 127.0.0.1:3306" in da["ten"] and "[ĐỎ] user:tram-kiem — API Duyệt" in van_ban
-    assert kiem_cach_ly([], tram_kiem=None)[1] == 1
+    assert kiem_cach_ly([], doc_pk=lambda: None)[1] == 1
diff --git a/tests/test_tho_lenh_chay.py b/tests/test_tho_lenh_chay.py
index b2da6ab..1e1cc9a 100644
--- a/tests/test_tho_lenh_chay.py
+++ b/tests/test_tho_lenh_chay.py
@@ -89,6 +89,8 @@ def test_dang_ky_lenh_cli():
     assert p.parse_args(["tho", "chay"]).ham.__name__ == "_chay"
     assert p.parse_args(["tho", "nhan-token"]).ham.__name__ == "_nhan_token"
     assert p.parse_args(["chu", "cai-dat-tho", "--khe", "claude-1=tram-k-1", "--co-che", "user"]).quan_ly == "tram-tho"
-    assert p.parse_args(["chu", "kiem-cach-ly", "--tram-kiem", "user:tram-kiem"]).tram_kiem == "user:tram-kiem"
+    assert p.parse_args(["chu", "kiem-cach-ly", "--principal", "user:a"]).principal == ["user:a"]
+    with pytest.raises(SystemExit):                                     # 3c: tram-kiem chỉ khai ở cach_ly.tram_kiem
+        p.parse_args(["chu", "kiem-cach-ly", "--tram-kiem", "user:tram-kiem"])
     assert p.parse_args(["tho", "them-khe", "claude-3", "--principal", "user:x", "--thu-muc-cau-hinh", "/a",
                          "--ten-goi-nho", "C3", "--vai", "coder"]).vai == ["coder"]
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_so_cai_tho.py tests/test_dinh_danh_cai.py tests/test_cai_dat_tho_kiem.py tests/test_cai_nha_tho.py tests/test_chu_tho.py tests/test_tho_lenh_chay.py -q`
Expected: FAIL — `4 errors in 1.19s` (kết quả chạy thật trên bản sao: `ModuleNotFoundError: No module named 'tram.chu.so_cai_tho'` / `'tram.chu.dinh_danh'`, `ImportError: cannot import name 'nhat_ky' from 'tram.chu'` khi nạp bốn file test mới)

- [ ] **Step 3: Viết mã**

`tram/chu/nhat_ky.py` (mới):

```python
"""Ghi thêm an toàn cho journal dạng JSONL (lát 3c, R4 review đợt 5) — dùng cho sổ cài đặt máy thợ.
- `khoa(p)`: flock KHÔNG chờ trên file khoá riêng; bận → `DangBan`.
- `cat_duoi(p)`: GỌI DƯỚI KHOÁ, trước mỗi lần nối. Bytes sau "\\n" cuối (bản ghi dở do crash hay short write, kể cả
  UTF-8 dở) được chép nguyên ra `<p>.duoi-hong` (fsync) rồi cắt khỏi `p` (fsync). Dòng hoàn chỉnh không bao giờ bị sửa.
- `ghi_het(p, du)`: ghi ĐỦ bytes (lặp `os.write` — short write không mất phần còn lại) rồi `F_FULLFSYNC` (macOS:
  `fsync` thường không ép xuống đĩa); file mới tạo thì fsync cả thư mục chứa (và thư mục cha) để tên file bền.
- `dong_hoan_chinh(du)`: các dòng kết thúc bằng "\\n" (bytes); đuôi dở bị bỏ khi đọc, chưa giải mã."""
import fcntl
import os
from contextlib import contextmanager
from pathlib import Path


class DangBan(ValueError):
    """Đã có tiến trình khác giữ khoá journal."""


@contextmanager
def khoa(p: Path, thong_bao: str, *, loi: type[DangBan] = DangBan):
    p.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(p, os.O_RDWR | os.O_CREAT, 0o600)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise loi(thong_bao) from None
        yield
    finally:
        os.close(fd)


def dong_bo(fd: int) -> None:
    try:
        fcntl.fcntl(fd, fcntl.F_FULLFSYNC)
    except (AttributeError, OSError):
        os.fsync(fd)


def _dong_bo_thu_muc(p: Path) -> None:
    for d in (p.parent, p.parent.parent, p.parent.parent.parent):
        fd = os.open(d, os.O_RDONLY)
        try:
            dong_bo(fd)
        finally:
            os.close(fd)


def ghi_het(p: Path, du: bytes) -> None:
    moi = not p.exists()
    fd = os.open(p, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
    try:
        while du:
            n = os.write(fd, du)
            if n <= 0:
                raise OSError(f"ghi {p}: os.write trả {n}")
            du = du[n:]
        dong_bo(fd)
    finally:
        os.close(fd)
    if moi:
        _dong_bo_thu_muc(p)


def dong_hoan_chinh(du: bytes) -> list[bytes]:
    return du[:du.rfind(b"\n") + 1].split(b"\n")[:-1]


def cat_duoi(p: Path) -> bytes:
    """Trả đuôi dở đã cắt (b"" nếu không có)."""
    du = p.read_bytes() if p.exists() else b""
    cat = du.rfind(b"\n") + 1
    if cat == len(du):
        return b""
    ghi_het(p.with_name(p.name + ".duoi-hong"), du[cat:] + b"\n")
    fd = os.open(p, os.O_WRONLY)
    try:
        os.ftruncate(fd, cat)
        dong_bo(fd)
    finally:
        os.close(fd)
    return du[cat:]
```

`tram/chu/so_cai_tho.py` (mới):

```python
"""Sổ cài đặt máy thợ v2 — journal (lát 3c R2, Codex F02; R4 review đợt 5). `~/.tram/cai-dat-tho/so-cai.jsonl`, mỗi
dòng một bản ghi, CHỈ ghi thêm: `du_dinh` (kieu user|nha|tep|thu_muc, ten, mong — GHI TRƯỚC lệnh tạo), `da_tao`
(+dinh_danh, sau khi QUAN SÁT đúng định danh mong đợi), `khong_tao` (+ly_do), `da_go`. Trạng thái = bản ghi cuối của id.
Mọi lần ghi — và cả lần cài/gỡ, qua `giu()` — giữ khoá `so-cai.jsonl.khoa`; dưới khoá, đuôi dở được cắt (giữ bằng
chứng ở `.duoi-hong`) TRƯỚC khi nối, rồi ghi đủ bytes + fsync (`nhat_ky.py`). Lệnh tạo chỉ chạy SAU khi `du_dinh` đã
fsync, nên bỏ đuôi dở không làm mất dấu tài nguyên nào. Dòng hỏng ở giữa → ValueError (không cài/gỡ gì theo sổ hỏng).
`doi_soat` khép `du_dinh` dở bằng quan sát: đúng định danh mong đợi → `da_tao`, còn lại → `khong_tao`."""
import json
import secrets
from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path

from tram.chu.nhat_ky import DangBan, cat_duoi, dong_hoan_chinh, ghi_het, khoa
from tram.duong_dan import tram_home

PHIEN_BAN = 2
KIEU = ("user", "nha", "tep", "thu_muc")
SU = ("du_dinh", "da_tao", "khong_tao", "da_go")
CHUYEN = {"du_dinh": ("da_tao", "khong_tao"), "da_tao": ("da_go",)}     # chuyển trạng thái hợp lệ


class SoCaiDangBan(DangBan):
    """Đang có `cai-dat-tho`/`go-cai-dat-tho` khác giữ khoá sổ."""


@dataclass(frozen=True)
class Muc:
    id: str
    kieu: str
    ten: str
    mong: dict
    su: str = "du_dinh"
    dinh_danh: dict | None = None


class SoCai:
    def __init__(self, p: Path | None = None):
        self.p = p or tram_home() / "cai-dat-tho" / "so-cai.jsonl"
        self._giu = False

    def _hong(self, ly_do: str) -> ValueError:
        return ValueError(f"Sổ cài đặt {self.p} hỏng ({ly_do}) — không cài/gỡ gì theo sổ này, Đại ca kiểm tay")

    @contextmanager
    def giu(self):
        """Khoá giao dịch cài/gỡ (không chờ); lồng trong cùng đối tượng thì dùng lại khoá đang giữ."""
        if self._giu:
            yield self
            return
        with khoa(self.p.with_name(self.p.name + ".khoa"), f"đang có cài/gỡ khác giữ sổ {self.p} — chạy lại sau",
                  loi=SoCaiDangBan):
            self._giu = True
            try:
                yield self
            finally:
                self._giu = False

    def muc(self) -> dict[str, Muc]:
        ra: dict[str, Muc] = {}
        for d in dong_hoan_chinh(self.p.read_bytes() if self.p.exists() else b""):
            try:
                x = json.loads(d.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                raise self._hong("dòng không phải JSON UTF-8") from None
            if not isinstance(x, dict) or x.get("v") != PHIEN_BAN or not isinstance(x.get("id"), str) \
                    or x.get("su") not in SU:
                raise self._hong("bản ghi sai dạng")
            if x["su"] == "du_dinh":
                if x.get("kieu") not in KIEU or not isinstance(x.get("ten"), str) \
                        or not isinstance(x.get("mong"), dict):
                    raise self._hong("du_dinh sai dạng")
                ra[x["id"]] = Muc(x["id"], x["kieu"], x["ten"], x["mong"])
            elif x["id"] not in ra or x["su"] not in CHUYEN.get(ra[x["id"]].su, ()):
                raise self._hong(f"{x['su']} không theo sau trạng thái hợp lệ")
            elif not isinstance(x.get("dinh_danh", {}), dict):
                raise self._hong("dinh_danh sai dạng")
            else:
                ra[x["id"]] = replace(ra[x["id"]], su=x["su"], dinh_danh=x.get("dinh_danh", ra[x["id"]].dinh_danh))
        return ra

    def _ghi(self, x: dict) -> None:
        with self.giu():
            cat_duoi(self.p)                     # đuôi dở (crash/short write): giữ bằng chứng rồi cắt, không nối vào
            ghi_het(self.p, (json.dumps({"v": PHIEN_BAN, **x}, ensure_ascii=False) + "\n").encode())

    def du_dinh(self, id_: str, kieu: str, ten: str, mong: dict) -> None:
        self._ghi({"id": id_, "su": "du_dinh", "kieu": kieu, "ten": ten, "mong": mong,
                   "luc": datetime.now(timezone.utc).isoformat(timespec="seconds")})

    def ket(self, id_: str, su: str, **kw) -> None:
        self._ghi({"id": id_, "su": su, **kw})

    def da_tao(self, kieu: str, ten: str) -> list[Muc]:
        return [m for m in self.muc().values() if (m.kieu, m.ten, m.su) == (kieu, ten, "da_tao")]

    def co_ghi(self, kieu: str, ten: str) -> bool:
        """Sổ có ghi trạm tạo (hoặc đang tạo dở) tài nguyên này."""
        return any((m.kieu, m.ten) == (kieu, ten) and m.su in ("du_dinh", "da_tao") for m in self.muc().values())


def moi_id() -> str:
    return secrets.token_hex(8)


def doi_soat(so: SoCai, quan_sat: Callable, khop: Callable) -> int:
    """Khép mọi `du_dinh` dở dang bằng quan sát. Trả số mục đã khép."""
    dem = 0
    for m in [m for m in so.muc().values() if m.su == "du_dinh"]:
        hien = quan_sat(m.kieu, m.ten)
        if hien is not None and khop(m.kieu, m.mong, hien):
            so.ket(m.id, "da_tao", dinh_danh=hien, doi_soat=True)
        else:
            so.ket(m.id, "khong_tao", ly_do="đối soát: không thấy tài nguyên đúng định danh mong đợi")
        dem += 1
    return dem
```

`tram/chu/dinh_danh.py` (mới):

```python
"""Định danh tài nguyên hệ thống cho sổ cài đặt (lát 3c R2): user — UniqueID, GeneratedUID, RealName qua `dscl` (không
sudo); file — sha256 nội dung (file root không đọc được như sudoers 0440 thì `sudo shasum`); thư mục, nhà — inode + chủ.
`khop`: thứ vừa thấy có đúng thứ LẦN CÀI NÀY định tạo (user mang mã id trong RealName, file đúng nội dung, thư mục
và nhà là thư mục thật thuộc đúng UID mong đợi — R5: biên nhận user KHÔNG chứng minh nhà đã tạo xong). `dscl` lỗi
khác "không có bản ghi" → OSError: không suy "không còn" từ một lần đọc hỏng.
`cung`: thứ đang có có đúng thứ sổ đã ghi `da_tao` (user cùng UID + GeneratedUID — tên tái sử dụng thì khác)."""
import hashlib
import os
import stat
import subprocess
from pathlib import Path


def _doc_dscl(s: str) -> dict:
    gia, khoa = {}, None
    for d in s.splitlines():
        if d.startswith(" ") and khoa:
            gia[khoa] = (gia[khoa] + " " + d.strip()).strip()
            continue
        khoa, _, v = d.partition(":")
        gia[khoa] = v.strip()
    if not gia.get("UniqueID", "").isdigit() or not gia.get("GeneratedUID"):
        raise ValueError("dscl không trả UniqueID/GeneratedUID")
    return {"uid": int(gia["UniqueID"]), "guid": gia["GeneratedUID"], "ten_day_du": gia.get("RealName", "")}


def user(ten: str, *, chay=subprocess.run) -> dict | None:
    r = chay(["/usr/bin/dscl", ".", "-read", f"/Users/{ten}", "UniqueID", "GeneratedUID", "RealName"],
             capture_output=True, text=True, timeout=30)
    if r.returncode == 0:
        return _doc_dscl(r.stdout)
    if "eDSRecordNotFound" in (r.stdout or "") + (r.stderr or ""):
        return None
    raise OSError(f"dscl đọc /Users/{ten} lỗi (mã {r.returncode}) — không kết luận user không có")


def tep(p: Path, *, chay=subprocess.run, nhe: bool = False) -> dict | None:
    if not os.path.lexists(p):
        return None
    st = os.lstat(p)
    if not stat.S_ISREG(st.st_mode):
        return {"loai": "khac", "uid": st.st_uid}
    if nhe:
        return {"uid": st.st_uid}
    try:
        h = hashlib.sha256(Path(p).read_bytes()).hexdigest()
    except PermissionError:
        h = chay(["sudo", "/usr/bin/shasum", "-a", "256", str(p)], capture_output=True, text=True, timeout=60,
                 check=True).stdout.split()[0]
    return {"sha256": h, "uid": st.st_uid}


def thu_muc(p: Path) -> dict | None:
    if not os.path.lexists(p):
        return None
    st = os.lstat(p)
    return {"ino": st.st_ino, "uid": st.st_uid} if stat.S_ISDIR(st.st_mode) else {"loai": "khac", "uid": st.st_uid}


def quan_sat_that(kieu: str, ten: str, *, nhe: bool = False) -> dict | None:
    """`nhe`: lúc lập kế hoạch — không gọi `sudo` (chỉ biết file có hay không)."""
    if kieu == "user":
        return user(ten)
    return tep(Path(ten), nhe=nhe) if kieu == "tep" else thu_muc(Path(ten))


def khop(kieu: str, mong: dict, hien: dict) -> bool:
    if hien.get("loai") == "khac":
        return False
    if kieu == "user":
        return hien.get("ten_day_du") == mong.get("ten_day_du")
    if kieu == "tep":
        return hien.get("sha256") == mong.get("sha256")
    return "ino" in hien and mong.get("uid") is not None and hien.get("uid") == mong.get("uid")


def cung(kieu: str, da: dict | None, hien: dict) -> bool:
    if not da or hien.get("loai") == "khac":
        return False
    if kieu == "user":
        return (hien.get("uid"), hien.get("guid")) == (da.get("uid"), da.get("guid"))
    return hien.get("sha256") == da.get("sha256") if kieu == "tep" else hien.get("ino") == da.get("ino")
```

`tram/chu/tai_nguyen.py` (mới):

```python
"""Tạo tài nguyên hệ thống CÓ SỔ (lát 3c R2; R5 review đợt 5) cho `tram chu cai-dat-tho`. Mỗi tài nguyên (user, nhà
của user, file root, thư mục) là MỘT bước riêng có bản ghi riêng — biên nhận sở hữu user không chứng minh nhà đã tạo:
1. lúc lập kế hoạch — đã có mà sổ không ghi trạm tạo → TỪ CHỐI cài (không cài đè, không nhận làm của mình). Nhà
   (`nhan`): chỉ nhận/giữ khi user cùng tên ĐANG là của trạm (`user_cua_tram`), nhà là thư mục thật của đúng UID ấy, và
   mọi biên nhận cũ của nhà này ghi cùng GeneratedUID — nhà giữ lại từ user đã gỡ (kể cả UID được dùng lại) là nhà lạ;
2. lúc chạy — quan sát lại; đã có: phải khớp định danh một bản ghi `da_tao` (user giữ nguyên; file đổi nội dung thì
   thay), không khớp → dừng; chưa có: ghi `du_dinh` (fsync) → chạy lệnh → quan sát → `da_tao` kèm định danh, hoặc
   `khong_tao` rồi dừng. Chạy lại chỉ làm bước còn thiếu; UID/GUID user giữ nguyên.
User mang mã `id` của bản ghi trong RealName: `addUser` "thành công" trên user có sẵn không biến nó thành của trạm."""
import subprocess
from collections.abc import Callable
from dataclasses import dataclass, field

from tram.chu.dinh_danh import cung, khop, quan_sat_that
from tram.chu.so_cai_tho import SoCai, moi_id


class LoiCaiDat(RuntimeError):
    """Dừng cài giữa chừng — sổ đã ghi đúng phần đã tạo; `tram chu go-cai-dat-tho` gỡ được phần đó."""


@dataclass(frozen=True)
class TaiNguyen:
    kieu: str                                            # user | nha | tep | thu_muc
    ten: str                                             # tên user | đường dẫn tuyệt đối
    lenh: Callable[[str], list[list[str]]]               # id bản ghi → lệnh tạo
    mong: Callable[[str], dict] = field(default=lambda i: {})
    nhan: Callable[[dict], bool] | None = None           # nhà: có sẵn mà nhận được là của trạm không

    def mo_ta(self) -> str:
        return " && ".join(" ".join(c) for c in self.lenh("<id>"))


def cua_tram(so: SoCai, kieu: str, ten: str, hien: dict) -> bool:
    return any(cung(kieu, m.dinh_danh, hien) for m in so.da_tao(kieu, ten))


def user_cua_tram(so: SoCai, u: str, quan_sat: Callable) -> dict | None:
    """User `u` đang có VÀ là của trạm: cùng UID + GUID một `da_tao`, hoặc RealName mang mã id của một `du_dinh` còn dở
    (crash sau `addUser`, trước `da_tao` — đối soát chưa chạy)."""
    hien = quan_sat("user", u)
    ok = hien is not None and any(m.su == "da_tao" and cung("user", m.dinh_danh, hien)
                                  or m.su == "du_dinh" and khop("user", m.mong, hien)
                                  for m in so.muc().values() if (m.kieu, m.ten) == ("user", u))
    return hien if ok else None


def nha_tram(u: str, so: SoCai, quan_sat: Callable) -> TaiNguyen:
    """`/Users/<u>` của user trạm `u` — `createhomedir`; mong: UID + GUID của user lúc tạo."""
    p = f"/Users/{u}"

    def nhan(hien: dict) -> bool:
        ch = user_cua_tram(so, u, quan_sat)
        return ch is not None and khop("nha", {"uid": ch["uid"]}, hien) and all(
            m.mong.get("guid") == ch["guid"] for m in so.da_tao("nha", p) if cung("nha", m.dinh_danh, hien))

    def mong(i: str) -> dict:
        ch = user_cua_tram(so, u, quan_sat) or {}
        return {"user": u, "uid": ch.get("uid"), "guid": ch.get("guid")}
    return TaiNguyen("nha", p, lambda i: [["sudo", "createhomedir", "-c", "-u", u]], mong, nhan)


def kiem_truoc(so: SoCai, ds: list[TaiNguyen], *, quan_sat: Callable = quan_sat_that) -> list[str]:
    """Hành động dự kiến cho từng tài nguyên (`tạo` | `giữ/thay` | `nhận`). Thứ đã có mà sổ không ghi → ValueError."""
    ra, la = [], []
    for tn in ds:
        hien, ghi = quan_sat(tn.kieu, tn.ten, nhe=True), so.co_ghi(tn.kieu, tn.ten)
        if hien is None:
            ra.append("tạo")
        elif tn.nhan is not None:
            (ra.append("giữ" if ghi else "nhận") if tn.nhan(hien) else la.append(f"{tn.kieu} {tn.ten}"))
        elif ghi:
            ra.append("giữ/thay")
        else:
            la.append(f"{tn.kieu} {tn.ten}")
    if la:
        raise ValueError("Đã có nhưng không phải của trạm (sổ không ghi, hoặc nhà cũ của user đã gỡ — `go-cai-dat-tho "
                         "--xoa-nha` nếu sổ ghi nhà đó, không thì xoá tay) — không cài đè, Đại ca kiểm tay: "
                         + ", ".join(la))
    return ra


def tao(so: SoCai, tn: TaiNguyen, *, quan_sat: Callable = quan_sat_that, chay: Callable = subprocess.run) -> str:
    hien = quan_sat(tn.kieu, tn.ten)
    if hien is not None:
        if tn.nhan is not None:
            if not tn.nhan(hien):
                raise LoiCaiDat(f"{tn.kieu} {tn.ten} có sẵn nhưng không thuộc user trạm hiện tại — dừng, không ghi đè")
            if cua_tram(so, tn.kieu, tn.ten, hien):
                return "giu"
            i = moi_id()
            so.du_dinh(i, tn.kieu, tn.ten, tn.mong(i))
            so.ket(i, "da_tao", dinh_danh=hien, nhan=True)
            return "nhan"
        if not cua_tram(so, tn.kieu, tn.ten, hien):
            raise LoiCaiDat(f"{tn.kieu} {tn.ten} đã có nhưng không khớp định danh trạm đã ghi — dừng, không đè")
        if tn.kieu == "thu_muc" and not khop("thu_muc", tn.mong(""), hien):
            raise LoiCaiDat(f"thu_muc {tn.ten} của trạm nhưng chủ không còn là UID mong đợi — dừng, không chown")
        if tn.kieu != "tep" or khop("tep", tn.mong(""), hien):
            return "giu"
    i = moi_id()
    mong = tn.mong(i)
    so.du_dinh(i, tn.kieu, tn.ten, mong)
    loi = None
    try:
        for c in tn.lenh(i):
            chay(c, check=True)
    except (subprocess.CalledProcessError, OSError) as e:
        loi = e
    sau = quan_sat(tn.kieu, tn.ten)
    if sau is not None and khop(tn.kieu, mong, sau):
        so.ket(i, "da_tao", dinh_danh=sau)
        if loi is None:
            return "tao"
    else:
        so.ket(i, "khong_tao", ly_do=f"{type(loi).__name__ if loi else 'định danh không khớp'}")
    raise LoiCaiDat(f"Không tạo được {tn.kieu} {tn.ten} đúng định danh — dừng (sổ đã ghi)") from loi
```

`tram/chu/cai_dat_kiem.py` (mới):

```python
"""Phần `tram-kiem` trong `tram chu cai-dat-tho` theo D22 (lát 3c, bead bs-urj.13) — KHÔNG helper root, không ACL.
Thêm: thư mục gốc bản chép `thu_muc_kiem` do CHÍNH `tram-kiem` tạo (nó sở hữu, trạm chỉ đi qua được), dòng sudoers
runas CHỈ `tram-kiem` (`dong_sudoers_kiem`), và — cơ chế `sandbox` — hồ sơ cố định root:wheel 0644 `HO_SO_KIEM`.
Không tự chọn cơ chế: `cach_ly.tram_kiem` phải cùng cơ chế với `--co-che` (D3: thử `user` trước, giữ hai nhánh).
`tram-kiem` luôn là user RIÊNG: `don_sach` giết MỌI tiến trình của nó — dùng chung user với khe là giết agent khe."""
import hashlib
from dataclasses import dataclass, field
from pathlib import Path

from tram.chu.tai_nguyen import TaiNguyen
from tram.cli_dich_vu import CONG_MAC_DINH
from tram.duong_dan import tram_home
from tram.giao_viec.principal_kiem import PrincipalKiem
from tram.tho.quyen_kiem import HO_SO_KIEM, THU_MUC_CAI, goc_hop_le, ho_so_tram_kiem

NHA_KIEM = "/var/empty"        # C01: tram-kiem KHÔNG có nhà ghi được (root, 0755); lệnh kiểm nhận HOME mới mỗi lần


@dataclass
class PhanKiem:
    tep: dict[Path, bytes] = field(default_factory=dict)        # file soạn trong ~/.tram/cai-dat-tho
    tai_nguyen: list[TaiNguyen] = field(default_factory=list)
    canh_bao: list[str] = field(default_factory=list)


def cong_cam(db_nghiep_vu: tuple[str, ...]) -> list[int]:
    return [CONG_MAC_DINH, *sorted({int(x.rsplit(":", 1)[1]) for x in db_nghiep_vu})]


def tep_root(soan: Path, dich: Path, noi_dung: bytes, mode: str, *, truoc: tuple = ()) -> TaiNguyen:
    """File root:wheel cài từ bản soạn; định danh = sha256 nội dung."""
    h = hashlib.sha256(noi_dung).hexdigest()
    return TaiNguyen("tep", str(dich), lambda i: [*map(list, truoc), ["sudo", "install", "-m", mode, "-o", "root",
                                                                     "-g", "wheel", str(soan), str(dich)]],
                     lambda i: {"sha256": h})


def phan_kiem(*, kiem: PrincipalKiem | None, thu_muc_kiem: Path | None, co_che: str, tram: str, quan_ly: str,
              soan: Path, khe: tuple[str, ...] = (), db_nghiep_vu: tuple[str, ...] = (),
              quan_sat=lambda kieu, ten: None) -> PhanKiem:
    if kiem is None:
        return PhanKiem()
    if kiem.co_che != co_che:
        raise ValueError(f"cach_ly.tram_kiem dùng cơ chế {kiem.co_che}, khác --co-che {co_che} — khai cùng một cơ chế")
    if kiem.ten in khe or kiem.ten in (tram, quan_ly):
        raise ValueError(f"tram-kiem ({kiem.ten}) phải là user riêng — không trùng principal khe, trạm, quản lý thợ")
    if thu_muc_kiem is None:
        raise ValueError("Có cach_ly.tram_kiem thì cần giao_viec.thu_muc_kiem (gốc bản chép của tram-kiem)")
    goc = goc_hop_le(thu_muc_kiem)
    uid_kiem = lambda i: {"chu": kiem.ten, "uid": (quan_sat("user", kiem.ten) or {}).get("uid")}  # noqa: E731
    pk = PhanKiem(tai_nguyen=[TaiNguyen("thu_muc", goc, lambda i: [["sudo", "-u", kiem.ten, "/bin/mkdir", "-m", "0755",
                                                                     goc]], uid_kiem)])
    if co_che == "sandbox":
        hs = ho_so_tram_kiem(tram_home_tram=tram_home(), nha_quan_ly=Path(f"/Users/{quan_ly}"), goc=Path(goc),
                             cong=cong_cam(db_nghiep_vu)).encode()
        pk.tep[soan / HO_SO_KIEM.name] = hs
        pk.tai_nguyen += [TaiNguyen("thu_muc", str(THU_MUC_CAI), lambda i: [
            ["sudo", "install", "-d", "-o", "root", "-g", "wheel", "-m", "0755", str(THU_MUC_CAI)]],
            lambda i: {"uid": 0}),
                          tep_root(soan / HO_SO_KIEM.name, HO_SO_KIEM, hs, "0644")]
    pk.canh_bao = [
        f"D22: KHÔNG có dòng sudoers nào chạy root — {tram} chỉ được chạy lệnh DƯỚI {kiem.ten}. {kiem.ten} tự tạo, tự "
        f"giải nén, tự dọn bản chép dưới {goc}; cây kiểm là repo git MỘT commit do {kiem.ten} tự dựng (D40).",
        f"C01: nhà của {kiem.ten} là {NHA_KIEM} (không ghi được, không createhomedir). Sau khi cài, TRƯỚC lần kiểm lại "
        "đầu tiên: `tram giao chup-nen-lich` ghi nền launchd của tram-kiem; thiếu nền thì kiểm lại dừng (fail-closed).",
        f"Principal kiểm lại đọc từ cach_ly.tram_kiem ({co_che}:{kiem.ten}), thư mục kiểm từ giao_viec.thu_muc_kiem "
        f"({goc}). Cài xong chạy `tram giao kiem`: mục thư mục kiểm, sudoers, ghi bản chép phải XANH trước khi bật "
        "giao_viec.bat."]
    return pk
```

`tram/chu/cai_dat_tho.py`, `tram/chu/kiem_cach_ly.py`, `tram/chu/lenh_tho.py` (sửa — bản vá):

```diff
diff --git a/tram/chu/cai_dat_tho.py b/tram/chu/cai_dat_tho.py
index fd57b9a..c9cf207 100644
--- a/tram/chu/cai_dat_tho.py
+++ b/tram/chu/cai_dat_tho.py
@@ -2,24 +2,35 @@
 TÀI KHOẢN TRẠM (Đại ca, quyền admin — các lệnh `sudo` hỏi mật khẩu trong Terminal). CƠ CHẾ CÁCH LY CHƯA CHỐT (§14 —
 chốt sau S6): `--co-che user` (user macOS mỗi khe) hay `sandbox` (một user thực thi chung + sandbox). Cú pháp
 `sysadminctl`, sudoers, LaunchDaemon có `UserName` và việc Keychain của user dịch vụ đọc được dưới launchd — CHỜ S2, S6.
-File cần quyền root được soạn trong `~/.tram/cai-dat-tho/` rồi `sudo install`; sudoers kiểm bằng `visudo -cf` trước."""
+File cần quyền root được soạn trong `~/.tram/cai-dat-tho/` rồi `sudo install`; sudoers kiểm bằng `visudo -cf` trước.
+Lát 3c: principal kiểm lại đọc từ MỘT nguồn (`doc_principal_kiem`, không còn cờ `--tram-kiem`); D22: không dòng
+sudoers root, không helper. R2: mọi user/file/thư mục đi qua `tai_nguyen.py` — có sổ `so-cai.jsonl` (du_dinh trước
+lệnh, da_tao kèm định danh sau quan sát), thứ đã có mà sổ không ghi thì từ chối cài."""
 import plistlib
+import subprocess
 from pathlib import Path
 
 from tram.chu.cai_dat import KeHoach
+from tram.chu.cai_dat_kiem import NHA_KIEM, phan_kiem, tep_root
+from tram.chu import dinh_danh
 from tram.chu.launchd import PATH_HE_THONG
+from tram.chu.so_cai_tho import SoCai, doi_soat
+from tram.chu.tai_nguyen import TaiNguyen, kiem_truoc, nha_tram, tao
 from tram.duong_dan import tram_home
+from tram.giao_viec.principal_kiem import PrincipalKiem
+from tram.tho.principal import USER_RE
+from tram.tho.quyen_kiem import dong_sudoers_kiem
 
 NHAN_THO = "vn.tram.tho"
 SUDOERS = Path("/etc/sudoers.d/tram-tho")
 DAEMON = Path(f"/Library/LaunchDaemons/{NHAN_THO}.plist")
 
 
-def noi_dung_sudoers(*, quan_ly: str, principal: list[str], tram: str, tram_kiem: str | None) -> bytes:
+def noi_dung_sudoers(*, quan_ly: str, principal: list[str], tram: str, kiem: PrincipalKiem | None) -> bytes:
     dong = ["# Sinh bởi `tram chu cai-dat-tho` (spec 3 §7.3) — chỉ cho chạy lệnh DƯỚI principal không credential.",
             f"{quan_ly} ALL=({','.join(sorted(set(principal)))}) NOPASSWD:SETENV: ALL"]
-    if tram_kiem:
-        dong.append(f"{tram} ALL=({tram_kiem}) NOPASSWD:SETENV: ALL")
+    if kiem:
+        dong.append(dong_sudoers_kiem(tram=tram, tram_kiem=kiem.ten, co_che=kiem.co_che))
     return ("\n".join(dong) + "\n").encode()
 
 
@@ -33,27 +44,43 @@ def plist_tho(*, uv: str, repo: Path, quan_ly: str) -> bytes:
         "EnvironmentVariables": {"PATH": f"{nha}/.local/bin:{PATH_HE_THONG}", "HOME": nha}})
 
 
+def user_tram(u: str, nha: str) -> TaiNguyen:
+    """CHỈ `addUser` — RealName mang mã id của bản ghi sổ (bằng chứng user do CHÍNH lần cài này tạo). Nhà là bước
+    riêng (`nha_tram`, R5): biên nhận user không có nghĩa nhà đã tạo xong."""
+    return TaiNguyen("user", u, lambda i: [["sudo", "sysadminctl", "-addUser", u, "-fullName", f"tram {u} {i}", "-home",
+                                            nha, "-shell", "/usr/bin/false"]],
+                     lambda i: {"ten_day_du": f"tram {u} {i}"})
+
+
 def lap_ke_hoach_tho(*, uv: str, repo: Path, tram: str, quan_ly: str, khe: dict[str, str], co_che: str,
-                     tram_kiem: str | None) -> KeHoach:
+                     kiem: PrincipalKiem | None = None, thu_muc_kiem: Path | None = None,
+                     db_nghiep_vu: tuple[str, ...] = (), so: SoCai | None = None, quan_sat=None,
+                     chay=subprocess.run) -> KeHoach:
     """`khe`: tên khe → user principal (cơ chế `sandbox`: mọi khe cùng một user). `tram`: user macOS của tài khoản
-    trạm (chủ tram-api)."""
+    trạm (chủ tram-api). `kiem`, `thu_muc_kiem`: từ `doc_principal_kiem()` và `giao_viec.thu_muc_kiem`."""
     if co_che not in ("user", "sandbox"):
         raise ValueError("--co-che user | sandbox (Đại ca chốt sau S6)")
-    nguoi = sorted(set(khe.values()) | ({tram_kiem} if tram_kiem else set()) | {quan_ly})
-    soan = tram_home() / "cai-dat-tho"
-    tep = {soan / "tram-tho.sudoers": noi_dung_sudoers(quan_ly=quan_ly, principal=list(khe.values()), tram=tram,
-                                                        tram_kiem=tram_kiem),
-           soan / f"{NHAN_THO}.plist": plist_tho(uv=uv, repo=repo, quan_ly=quan_ly)}
-    lenh = [["sudo", "sysadminctl", "-addUser", u, "-fullName", f"tram {u}", "-home", f"/Users/{u}",
-             "-shell", "/usr/bin/false"] for u in nguoi]
-    lenh += [["sudo", "createhomedir", "-c", "-u", u] for u in nguoi]
-    lenh += [["sudo", "visudo", "-cf", str(soan / "tram-tho.sudoers")],
-             ["sudo", "install", "-m", "0440", "-o", "root", "-g", "wheel", str(soan / "tram-tho.sudoers"),
-              str(SUDOERS)],
-             ["sudo", "install", "-m", "0644", "-o", "root", "-g", "wheel", str(soan / f"{NHAN_THO}.plist"),
-              str(DAEMON)],
-             ["sudo", "launchctl", "bootout", f"system/{NHAN_THO}"], ["sudo", "launchctl", "bootstrap", "system",
-                                                                     str(DAEMON)]]
+    if la := [u for u in (*khe.values(), quan_ly) if not USER_RE.fullmatch(u)]:
+        raise ValueError(f"tên user không hợp lệ (cần [a-z_][a-z0-9_-]*, gỡ được về sau): {', '.join(la)}")
+    soan, so, quan_sat = tram_home() / "cai-dat-tho", so or SoCai(), quan_sat or dinh_danh.quan_sat_that
+    pk = phan_kiem(kiem=kiem, thu_muc_kiem=thu_muc_kiem, co_che=co_che, tram=tram, quan_ly=quan_ly, soan=soan,
+                   khe=tuple(khe.values()), db_nghiep_vu=db_nghiep_vu, quan_sat=quan_sat)
+    sud = noi_dung_sudoers(quan_ly=quan_ly, principal=list(khe.values()), tram=tram, kiem=kiem)
+    pl = plist_tho(uv=uv, repo=repo, quan_ly=quan_ly)
+    tep = {soan / "tram-tho.sudoers": sud, soan / f"{NHAN_THO}.plist": pl, **pk.tep}
+    nguoi = sorted(set(khe.values()) | ({kiem.ten} if kiem else set()) | {quan_ly})
+    ds = [user_tram(u, NHA_KIEM if kiem and u == kiem.ten else f"/Users/{u}") for u in nguoi]
+    ds += [nha_tram(u, so, quan_sat) for u in nguoi if not (kiem and u == kiem.ten)]
+    ds += [*pk.tai_nguyen,
+          tep_root(soan / "tram-tho.sudoers", SUDOERS, sud, "0440",
+                   truoc=(("sudo", "visudo", "-cf", str(soan / "tram-tho.sudoers")),)),
+          tep_root(soan / f"{NHAN_THO}.plist", DAEMON, pl, "0644")]
+    viec = kiem_truoc(so, ds, quan_sat=quan_sat)
+    buoc = [("Đối soát sổ cài đặt (bản ghi dở dang của lần trước)", lambda: doi_soat(so, quan_sat, dinh_danh.khop))]
+    buoc += [(f"[{v}] {tn.kieu} {tn.ten}: {tn.mo_ta()}", lambda tn=tn: tao(so, tn, quan_sat=quan_sat, chay=chay))
+             for tn, v in zip(ds, viec)]
+    lenh = [["sudo", "launchctl", "bootout", f"system/{NHAN_THO}"], ["sudo", "launchctl", "bootstrap", "system",
+                                                                    str(DAEMON)]]
     canh_bao = [
         "Cơ chế cách ly CHƯA CHỐT (§14): chỉ gõ dong-y khi Đại ca đã chốt sau spike S6 — "
         "tạo user là thay đổi hệ thống.",
@@ -65,5 +92,7 @@ def lap_ke_hoach_tho(*, uv: str, repo: Path, tram: str, quan_ly: str, khe: dict[
         "(khớp cong_bo.phuong_an của trạm — chốt sau S7). Kiểm: tram tho kiem (mọi mục xanh) và "
         "tram chu kiem-cach-ly (H9) TRƯỚC khi bật 3a.",
         "launchd: LaunchDaemon có UserName chạy không cần đăng nhập màn hình; Keychain của user dịch vụ có mở được "
-        "dưới launchd không là việc của spike S2 — không được thì dừng, không đổi sang lưu token ra file."]
-    return KeHoach(tep=tep, lenh=lenh, canh_bao=canh_bao)
+        "dưới launchd không là việc của spike S2 — không được thì dừng, không đổi sang lưu token ra file.",
+        f"Sổ {so.p}: chỉ ghi thêm. S6 hỏng → `tram chu go-cai-dat-tho` chỉ gỡ thứ sổ ghi da_tao VÀ còn đúng định "
+        "danh (user: UID + GeneratedUID; file: sha256) — in kế hoạch, chờ dong-y."]
+    return KeHoach(tep=tep, lenh=lenh, canh_bao=canh_bao + pk.canh_bao, buoc=buoc)
diff --git a/tram/chu/kiem_cach_ly.py b/tram/chu/kiem_cach_ly.py
index 86909f8..3ce8b29 100644
--- a/tram/chu/kiem_cach_ly.py
+++ b/tram/chu/kiem_cach_ly.py
@@ -1,12 +1,14 @@
 """`tram chu kiem-cach-ly` (spec 3 §7.3 mục 7, H9; spec 2 §4 mục 2b) — chạy ở TÀI KHOẢN TRẠM: bộ kiểm chứng âm ĐỦ dưới
 từng principal khe và dưới `tram-kiem` (`sudo -u`, có thể hỏi mật khẩu). Biết `dai_ca_logins` thật nên thăm dò "API
 Duyệt với header danh tính giả" mang đúng login của Đại ca: chỉ bị chặn khi kênh ghi thật sự tách (`cach_ly.kenh_ghi`).
-Mã thoát 1 nếu có thăm dò không đạt; KHÔNG có fixture nào làm nó xanh."""
+Mã thoát 1 nếu có thăm dò không đạt; KHÔNG có fixture nào làm nó xanh. Lát 3c: `tram-kiem` đọc từ MỘT nguồn
+(`doc_principal_kiem` — `cach_ly.tram_kiem`) và thăm dò chạy qua ĐÚNG argv lúc kiểm lại (`PrincipalKiem.boc_lenh`)."""
 import os
 import tempfile
 from pathlib import Path
 
 from tram.cau_hinh.cach_ly import nap_cau_hinh_cach_ly
+from tram.cau_hinh.principal_kiem import doc_principal_kiem
 from tram.cau_hinh.tram import nap_cau_hinh_tram
 from tram.duong_dan import tram_home
 from tram.tho.kiem_am import chay_tham_do, tham_do_day_du, tham_do_khe
@@ -18,25 +20,39 @@ def _boc_sudo(user: str):
     return lambda argv: ["/usr/bin/sudo", "-u", user, "-H", "--", *argv]
 
 
-def kiem_cach_ly(principal: list[str], *, tram_kiem: str | None, chay_td=chay_tham_do) -> tuple[str, int]:
+def _ds_boc(principal: list[str], doc_pk) -> list[tuple[str, object]]:
+    """(nhãn, boc | lỗi): principal khe qua `sudo -u` (hỏi mật khẩu); `tram-kiem` qua đúng argv của kiểm lại."""
+    ds: list[tuple[str, object]] = []
+    for chuoi in principal:
+        try:
+            ds.append((chuoi, _boc_sudo(doc_principal(chuoi).user)))
+        except ChuaCoPrincipal as e:
+            ds.append((chuoi, e))
+    try:
+        pk = doc_pk()
+        ds += [(f"{pk.co_che}:{pk.ten}", pk.boc_lenh)] if pk else []
+    except ValueError as e:
+        ds.append(("cach_ly.tram_kiem", e))
+    return ds
+
+
+def kiem_cach_ly(principal: list[str], *, chay_td=chay_tham_do, doc_pk=doc_principal_kiem) -> tuple[str, int]:
     ch, cl = nap_cau_hinh_tram(), nap_cau_hinh_cach_ly()
-    ds = [*principal, *([tram_kiem] if tram_kiem else [])]
+    ds = _ds_boc(principal, doc_pk)
     if not ds:
-        return "Chưa có principal nào để kiểm (--principal / --tram-kiem) — chờ S6.", 1
+        return "Chưa có principal nào để kiểm (--principal / cach_ly.tram_kiem) — chờ S6.", 1
     dong, ma = [f"Kênh ghi dashboard: {cl.kenh_ghi}" + ("  (header GIẢ ĐƯỢC — chưa đạt §4 mục 2b)"
                                                        if cl.kenh_ghi == "header" else "")], 0
-    for chuoi in ds:
-        try:
-            p = doc_principal(chuoi)
-        except ChuaCoPrincipal as e:
-            dong.append(f"[ĐỎ] {chuoi}: {e}")
+    for chuoi, boc in ds:
+        if isinstance(boc, Exception):
+            dong.append(f"[ĐỎ] {chuoi}: {boc}")
             ma = 1
             continue
         rg = tham_do_khe(keychain=list(KEYCHAIN_CAM), doc_cam=[tram_home() / "su-kien.db"], ghi_cam=[tram_home()],
                          ghi_duoc=Path(tempfile.gettempdir()))
         td = tham_do_day_du(rut_gon=rg, api="http://127.0.0.1:7700", dai_ca_login=(ch.dai_ca_logins or ("?",))[0],
                             may_b=ch.ten_may_b or "may-b", db=list(cl.db_nghiep_vu), tram_home_tram=tram_home())
-        for kq in chay_td(td, boc=_boc_sudo(p.user), env={"PATH": os.environ.get("PATH", ""), "LANG": "C.UTF-8"}):
+        for kq in chay_td(td, boc=boc, env={"PATH": os.environ.get("PATH", ""), "LANG": "C.UTF-8"}):
             dong.append(f"[{'XANH' if kq.dat else 'ĐỎ'}] {chuoi} — {kq.ten}: {kq.chi_tiet}")
             ma |= 0 if kq.dat else 1
     return "\n".join(dong), ma
diff --git a/tram/chu/lenh_tho.py b/tram/chu/lenh_tho.py
index eb7eeb1..8d9d4dc 100644
--- a/tram/chu/lenh_tho.py
+++ b/tram/chu/lenh_tho.py
@@ -1,8 +1,10 @@
 """Lệnh phía TÀI KHOẢN TRẠM cho máy thợ (lát 3a-2): `tram chu cai-dat-tho`, `tram chu cap-token-may`,
-`tram chu kiem-cach-ly` (spec 3 §5.1, §7.3 mục 5, 7; H9). Mọi thay đổi hệ thống: liệt kê trước, chờ `dong-y`."""
+`tram chu kiem-cach-ly` (spec 3 §5.1, §7.3 mục 5, 7; H9). Mọi thay đổi hệ thống: liệt kê trước, chờ `dong-y`.
+Lát 3c: principal kiểm lại chỉ đọc từ `cach_ly.tram_kiem` (`doc_principal_kiem`) — bỏ cờ `--tram-kiem`."""
 import shutil
+import subprocess
 import sys
-from contextlib import closing
+from contextlib import ExitStack, closing
 from datetime import datetime, timezone
 
 
@@ -13,17 +15,37 @@ def _hoi(args, cau: str = "Gõ dong-y để thực hiện: ") -> bool:
 def _cai_dat_tho(args) -> int:
     import getpass
 
+    from tram.cau_hinh.cach_ly import nap_cau_hinh_cach_ly
+    from tram.cau_hinh.giao_viec import nap_cau_hinh_giao_viec
+    from tram.cau_hinh.principal_kiem import doc_principal_kiem
     from tram.chu.cai_dat import in_ke_hoach, thuc_hien
     from tram.chu.cai_dat_tho import lap_ke_hoach_tho
+    from tram.chu.so_cai_tho import SoCai
+    from tram.chu.tai_nguyen import LoiCaiDat
     from tram.duong_dan import goc_repo
     khe = dict(x.split("=", 1) for x in args.khe)
-    kh = lap_ke_hoach_tho(uv=shutil.which("uv") or "uv", repo=goc_repo(), tram=getpass.getuser(), quan_ly=args.quan_ly,
-                          khe=khe, co_che=args.co_che, tram_kiem=args.tram_kiem)
-    print(in_ke_hoach(kh))
-    if not _hoi(args):
-        print("Không làm gì.")
-        return 1
-    thuc_hien(kh)
+    so, khoa = SoCai(), ExitStack()
+    try:
+        khoa.enter_context(so.giu())          # R4: cả lần cài (kế hoạch → dong-y → chạy) giữ khoá sổ, không chờ
+        kh = lap_ke_hoach_tho(uv=shutil.which("uv") or "uv", repo=goc_repo(), tram=getpass.getuser(),
+                              quan_ly=args.quan_ly, khe=khe, co_che=args.co_che, kiem=doc_principal_kiem(),
+                              thu_muc_kiem=nap_cau_hinh_giao_viec().thu_muc_kiem,
+                              db_nghiep_vu=nap_cau_hinh_cach_ly().db_nghiep_vu, so=so)
+    except (ValueError, OSError) as e:         # cấu hình/sổ lỗi, tài nguyên lạ, SoCaiDangBan, dscl lỗi
+        khoa.close()
+        print(f"Không cài: {e}", file=sys.stderr)
+        return 2
+    with khoa:
+        print(in_ke_hoach(kh))
+        if not _hoi(args):
+            print("Không làm gì.")
+            return 1
+        try:
+            thuc_hien(kh)
+        except (LoiCaiDat, OSError, ValueError, subprocess.CalledProcessError) as e:
+            print(f"Dừng giữa chừng: {e}\nSổ cài đặt đã ghi đúng phần đã tạo — `tram chu go-cai-dat-tho` gỡ được.",
+                  file=sys.stderr)
+            return 1
     print("Đã cài. Tiếp theo: các bước trong mục Cảnh báo ở trên.")
     return 0
 
@@ -47,7 +69,7 @@ def _cap_token_may(args) -> int:
 
 def _kiem_cach_ly(args) -> int:
     from tram.chu.kiem_cach_ly import kiem_cach_ly
-    van_ban, ma = kiem_cach_ly(args.principal, tram_kiem=args.tram_kiem)
+    van_ban, ma = kiem_cach_ly(args.principal)
     print(van_ban)
     return ma
 
@@ -57,14 +79,12 @@ def them_lenh_chu_tho(chu) -> None:
     c.add_argument("--quan-ly", default="tram-tho", help="User macOS của tiến trình quản lý thợ")
     c.add_argument("--khe", action="append", required=True, help="<tên khe>=<user principal>, lặp lại mỗi khe")
     c.add_argument("--co-che", required=True, choices=("user", "sandbox"), help="Cơ chế cách ly (chốt sau S6)")
-    c.add_argument("--tram-kiem", default=None, help="User principal kiểm lại của trạm (§7.3 mục 5)")
     c.add_argument("--dong-y", action="store_true")
     c.set_defaults(ham=_cai_dat_tho)
     t = chu.add_parser("cap-token-may", help="Cấp token máy thợ, chỉ in vào ống tới `tram tho nhan-token`")
     t.add_argument("may_id")
     t.add_argument("--dong-y", action="store_true")
     t.set_defaults(ham=_cap_token_may)
-    k = chu.add_parser("kiem-cach-ly", help="Kiểm chứng âm H9 dưới từng principal (sudo hỏi mật khẩu)")
+    k = chu.add_parser("kiem-cach-ly", help="Kiểm chứng âm H9 dưới từng principal khe và cach_ly.tram_kiem (sudo)")
     k.add_argument("--principal", action="append", default=[], help="user:<tên> | sandbox:<tên>, lặp lại")
-    k.add_argument("--tram-kiem", default=None, help="principal kiểm lại của trạm, vd user:tram-kiem")
     k.set_defaults(ham=_kiem_cach_ly)
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_so_cai_tho.py tests/test_dinh_danh_cai.py tests/test_cai_dat_tho_kiem.py tests/test_cai_nha_tho.py tests/test_chu_tho.py tests/test_tho_lenh_chay.py tests/test_cai_dat_bo_qua_loi.py tests/test_chu.py -q`
Expected: `48 passed in 3.25s`

Run: `uv run pytest -q`
Expected: `N₀ + 66 passed` (2166 — sau đợt trước + 28; ghép cùng Task 7 → N₀ + 79 = 2179)

Kiểm thêm (đã làm khi viết plan): chạy `tests/test_so_cai_tho.py` với `so_cai_tho.py` bản bị chặn (nối thẳng vào đuôi dở, không khoá, một `os.write`) → 5 failed (3 ca đuôi dở, short write, khoá) — các regression R4 bắt đúng lỗi của review.

- [ ] **Step 5: Commit**

```bash
git add tram/chu/nhat_ky.py tram/chu/so_cai_tho.py tram/chu/dinh_danh.py tram/chu/tai_nguyen.py tram/chu/cai_dat_kiem.py tram/chu/cai_dat_tho.py tram/chu/kiem_cach_ly.py tram/chu/lenh_tho.py tests/he_gia.py tests/test_so_cai_tho.py tests/test_dinh_danh_cai.py tests/test_cai_dat_tho_kiem.py tests/test_cai_nha_tho.py tests/test_chu_tho.py tests/test_tho_lenh_chay.py
git commit -m "feat(chu): cai-dat-tho có sổ journal (đuôi dở cắt có bằng chứng, ghi đủ bytes, khoá cài/gỡ), user và nhà là hai bước, sudoers D22 không root; kiem-cach-ly đọc cach_ly.tram_kiem (lát 3c R2/R4/R5, bs-urj.12/13/14)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 7: `tram giao kiem` — thư mục kiểm của `tram-kiem`, sudoers không NOPASSWD root

**Độ khó:** `de` · **Đợt:** 3 · **Song song với:** Task 6 · **Phải xong trước:** Task 5

**Files:**
- Create: `tram/giao_viec/kiem_goc.py`
- Modify: `tram/giao_viec/kiem_san_sang.py` (`kiem_principal` thêm 2 mục, tham số `uid_cua`)
- Modify: `tests/test_giao_kiem.py` (`chay_gia` biết `sudo -n -l`; `uid_cua` ở ca xanh hết; thêm ca sudoers)
- Test: `tests/test_kiem_goc.py` (mới)

**Interfaces:**
- Consumes: `PrincipalKiem`, `tu_cach_ly` (Task 5); `SUDO`; `MucKiem`.
- Produces: `RUNAS_NOPASSWD`, `uid_that(ten) -> int`, `kiem_thu_muc_goc(pk, thu_muc, *, lstat, uid_cua, di_qua) -> MucKiem` ("principal: thư mục kiểm của tram-kiem"), `kiem_sudoers_khong_root(*, chay) -> MucKiem` ("principal: sudoers không NOPASSWD root"). `kiem_principal(pk, thu_muc, *, chay, chay_lenh, toi, uid_cua=uid_that)` trả 7 mục (thêm 2 mục trên trước "ghi bản chép kiểm").

- [ ] **Step 1: Viết test thất bại**

`tests/test_kiem_goc.py` (mới):

```python
"""`tram giao kiem` — thư mục gốc bản chép của `tram-kiem` và sudoers không NOPASSWD root (D22, lát 3c). `lstat`
thật trên `tmp_path`, `uid_cua`/`chay` giả — KHÔNG sudo, không đọc người dùng thật."""
import os
from types import SimpleNamespace

import pytest

from tram.giao_viec.kiem_goc import kiem_sudoers_khong_root, kiem_thu_muc_goc
from tram.giao_viec.principal_kiem import tu_cach_ly

PK = tu_cach_ly("user:tram-kiem")
TOI = lambda ten: os.getuid()                                          # noqa: E731 — "tram-kiem" = user đang test


def test_thu_muc_goc_cua_tram_kiem_la_xanh(tmp_path):
    (tmp_path / "kiem").mkdir(mode=0o755)
    assert kiem_thu_muc_goc(PK, tmp_path / "kiem", uid_cua=TOI).muc_do == "xanh"


@pytest.mark.parametrize("ca", ["symlink", "tep", "chu-khac", "nhom-ghi", "khong-di-qua", "khong-co-user", "chua-dat"])
def test_thu_muc_goc_sai_la_do(tmp_path, ca):
    d = tmp_path / "kiem"
    d.mkdir(mode=0o755)
    kw = {"uid_cua": TOI}
    if ca == "symlink":
        (tmp_path / "lk").symlink_to(d)
        d = tmp_path / "lk"
    elif ca == "tep":
        d = tmp_path / "f"
        d.write_text("x")
    elif ca == "nhom-ghi":
        d.chmod(0o775)
    kw.update({"chu-khac": {"uid_cua": lambda ten: os.getuid() + 1}, "khong-di-qua": {"di_qua": lambda p: False},
               "khong-co-user": {"uid_cua": lambda ten: pwd_loi()}}.get(ca, {}))
    assert kiem_thu_muc_goc(PK, None if ca == "chua-dat" else d, **kw).muc_do == "do"


def pwd_loi():
    raise KeyError("getpwnam(): name not found: 'tram-kiem'")


@pytest.mark.parametrize("ra, muc_do", [
    ((0, "    (ALL) ALL\n    (tram-kiem) NOPASSWD: SETENV: ALL\n"), "xanh"),
    ((0, "    (tram-kiem) NOPASSWD: SETENV: ALL\n    (root) NOPASSWD: /usr/local/tram/x /k/*\n"), "do"),
    ((0, "    (ALL : ALL) NOPASSWD: ALL\n"), "do"),
    ((1, "sudo: a password is required\n"), "do")])
def test_sudoers_nopasswd_root_la_do(ra, muc_do):
    goi = []
    m = kiem_sudoers_khong_root(chay=lambda a, **kw: goi.append(a) or SimpleNamespace(returncode=ra[0], stdout=ra[1]))
    assert m.muc_do == muc_do and goi == [["/usr/bin/sudo", "-n", "-l"]]
```

`tests/test_giao_kiem.py` (sửa — bản vá):

```diff
diff --git a/tests/test_giao_kiem.py b/tests/test_giao_kiem.py
index 506aeab..896dabf 100644
--- a/tests/test_giao_kiem.py
+++ b/tests/test_giao_kiem.py
@@ -1,5 +1,6 @@
 """`tram giao kiem|tick|kho-kiem` (4a-2). Không chạy sudo, `bd` hay mạng thật: `chay`/`chay_lenh` giả, TRAM_REPO tạm
 (du-an/ rỗng hoặc trỏ remote bare cục bộ)."""
+import os
 import subprocess
 from pathlib import Path
 
@@ -19,14 +20,16 @@ from tram.tho.kiem_may import in_ket_qua
 PK = PrincipalKiem("tram-kiem", ("/usr/bin/sudo", "-n", "-u", "tram-kiem", "--"))
 
 
-def chay_gia(ten="tram-kiem", env="APP_ENV=testing\nPATH=/usr/bin", doc_duoc=False, ghi_duoc=True, pgrep=1):
+def chay_gia(ten="tram-kiem", env="APP_ENV=testing\nPATH=/usr/bin", doc_duoc=False, ghi_duoc=True, pgrep=1,
+             sudo_l="    (ALL) ALL\n    (tram-kiem) NOPASSWD: SETENV: ALL\n"):
     """`sudo -u tram-kiem` giả: mkdir/touch/rm chạy THẬT dưới user đang test (trong tmp_path) khi `ghi_duoc`."""
     def chay(argv, **kw):
         lenh = argv[len(PK.boc):] if argv[:len(PK.boc)] == list(PK.boc) else argv
         if lenh[0] in ("/bin/mkdir", "/usr/bin/touch", "/bin/rm"):
             return subprocess.run(lenh if ghi_duoc else ["/usr/bin/false"], capture_output=True, text=True)
         ra = {"/usr/bin/id": (0, ten), "/usr/bin/env": (0, env), "/bin/test": (0 if doc_duoc else 1, ""),
-              "/usr/bin/crontab": (1, ""), "/usr/bin/pkill": (1, ""), "/usr/bin/pgrep": (pgrep, "")}[lenh[0]]
+              "/usr/bin/crontab": (1, ""), "/usr/bin/pkill": (1, ""), "/usr/bin/pgrep": (pgrep, ""),
+              "/usr/bin/sudo": (0, sudo_l)}[lenh[0]]
         if kw.get("check") and ra[0]:
             raise subprocess.CalledProcessError(ra[0], argv)
         return subprocess.CompletedProcess(argv, ra[0], ra[1], "")
@@ -53,7 +56,8 @@ def test_principal_dat_moi_muc(tmp_path):
     for v in ("coder", "qc"):
         (tmp_path / "quyen" / f"{v}.json").write_text("{}")
     cg = CauHinhGiaoViec(bat=True, thu_muc_kiem=tmp_path, principal_kiem=PK)
-    ds = kiem_giao_viec(cg, [], goc_quyen=tmp_path / "quyen", chay=chay_gia(), chay_lenh=dung_lenh(), toi="hung")
+    ds = kiem_giao_viec(cg, [], goc_quyen=tmp_path / "quyen", chay=chay_gia(), chay_lenh=dung_lenh(), toi="hung",
+                        uid_cua=lambda ten: os.getuid())
     assert set(muc(ds).values()) == {"xanh"} and in_ket_qua(ds)[1] == 0
     assert not list(tmp_path.glob("tram-giao-kiem-thu*"))
 
@@ -61,7 +65,8 @@ def test_principal_dat_moi_muc(tmp_path):
 @pytest.mark.parametrize("sai, muc_do", [
     ({"ten": "hung"}, "principal: danh tính"), ({"env": "PATH=/usr/bin"}, "principal: giữ APP_ENV"),
     ({"doc_duoc": True}, "principal: không đọc kho trạm"), ({"ghi_duoc": False}, "principal: ghi bản chép kiểm"),
-    ({"pgrep": 0}, "principal: ghi bản chép kiểm")])
+    ({"pgrep": 0}, "principal: ghi bản chép kiểm"),
+    ({"sudo_l": "    (root) NOPASSWD: /usr/local/x\n"}, "principal: sudoers không NOPASSWD root")])
 def test_principal_sai_tung_muc_la_do(tmp_path, sai, muc_do):
     m = muc(kiem_giao_viec(CauHinhGiaoViec(thu_muc_kiem=tmp_path, principal_kiem=PK), [], goc_quyen=tmp_path,
                            chay=chay_gia(**sai), chay_lenh=dung_lenh(), toi="hung"))
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_kiem_goc.py tests/test_giao_kiem.py -q`
Expected: FAIL — `1 error` (`ModuleNotFoundError: No module named 'tram.giao_viec.kiem_goc'`)

- [ ] **Step 3: Viết mã**

`tram/giao_viec/kiem_goc.py` (mới):

```python
"""`tram giao kiem` — hai mục của D22 (lát 3c, bead bs-urj.13): thư mục gốc bản chép do CHÍNH `tram-kiem` sở hữu (trạm
chỉ cần đi qua được để làm cwd), và tài khoản trạm KHÔNG có dòng sudoers NOPASSWD nào chạy dưới root/ALL — D22 bỏ
helper root, nên dòng như vậy là sót lại hoặc lỗ. Chỉ XANH khi chạy thật trên máy B; test tiêm `lstat`/`chay`."""
import os
import pwd
import re
import stat
import subprocess
from collections.abc import Callable
from pathlib import Path

from tram.giao_viec.principal_kiem import PrincipalKiem
from tram.tho.kiem_may import MucKiem
from tram.tho.principal import SUDO

RUNAS_NOPASSWD = re.compile(r"^\s*\(([^)]*)\)\s*NOPASSWD", re.M)


def uid_that(ten: str) -> int:
    return pwd.getpwnam(ten).pw_uid


def kiem_thu_muc_goc(pk: PrincipalKiem, thu_muc: Path | None, *, lstat: Callable = os.lstat,
                     uid_cua: Callable[[str], int] = uid_that,
                     di_qua: Callable[[Path], bool] = lambda p: os.access(p, os.X_OK)) -> MucKiem:
    ten = "principal: thư mục kiểm của tram-kiem"
    if thu_muc is None:
        return MucKiem(ten, "do", "chưa đặt giao_viec.thu_muc_kiem")
    try:
        s, uid = lstat(thu_muc), uid_cua(pk.ten)
    except (OSError, KeyError) as e:
        return MucKiem(ten, "do", f"{thu_muc}: {type(e).__name__}")
    loi = ("là symlink" if stat.S_ISLNK(s.st_mode) else "không phải thư mục" if not stat.S_ISDIR(s.st_mode)
           else f"chủ là uid {s.st_uid}, cần {pk.ten} (uid {uid})" if s.st_uid != uid
           else "nhóm/người khác ghi được" if s.st_mode & 0o022
           else "tài khoản trạm không đi qua được (cần quyền x)" if not di_qua(thu_muc) else None)
    return MucKiem(ten, "do" if loi else "xanh", f"{thu_muc}: {loi}" if loi else f"{thu_muc} thuộc {pk.ten}")


def kiem_sudoers_khong_root(*, chay: Callable = subprocess.run) -> MucKiem:
    ten = "principal: sudoers không NOPASSWD root"
    try:
        r = chay([SUDO, "-n", "-l"], capture_output=True, text=True, timeout=30)
    except (subprocess.TimeoutExpired, OSError) as e:
        return MucKiem(ten, "do", f"sudo -n -l: {type(e).__name__}")
    if r.returncode != 0:
        return MucKiem(ten, "do", "sudo -n -l lỗi — chưa có dòng NOPASSWD dưới tram-kiem?")
    xau = [m for m in RUNAS_NOPASSWD.findall(r.stdout) if re.search(r"\b(root|ALL)\b", m)]
    return MucKiem(ten, "do" if xau else "xanh",
                   f"NOPASSWD chạy dưới: {', '.join(xau)}" if xau else "chỉ NOPASSWD dưới user không đặc quyền")
```

`tram/giao_viec/kiem_san_sang.py` (sửa — bản vá):

```diff
diff --git a/tram/giao_viec/kiem_san_sang.py b/tram/giao_viec/kiem_san_sang.py
index bc221df..2ce8c3e 100644
--- a/tram/giao_viec/kiem_san_sang.py
+++ b/tram/giao_viec/kiem_san_sang.py
@@ -1,7 +1,8 @@
 """`tram giao kiem` — kiểm sẵn sàng của bộ giao việc trước khi bật `giao_viec.bat`: đây là BƯỚC KIỂM KHI CHẠY THẬT
 của mọi adapter chờ cổng (S6 principal `tram-kiem`, S7 kho kiểm/remote, 3a-2 file quyền). Chưa chứng minh được → ĐỎ;
 không đánh dấu sẵn sàng bằng bản giả. Mọi lần chạy thật đi qua `chay`/`chay_lenh` tiêm được (test dùng bản giả).
-Lát 3c (D22): mục ghi bản chép — giữ khoá kiểm lại, `tram-kiem` tạo thư mục con + file rồi TỰ dọn, trạm thấy sạch."""
+Lát 3c (D22): mục ghi bản chép — giữ khoá kiểm lại, `tram-kiem` tạo thư mục con + file rồi TỰ dọn, trạm thấy sạch;
+thêm thư mục gốc của `tram-kiem` và sudoers không NOPASSWD root (`kiem_goc.py`)."""
 import getpass
 import os
 import shutil
@@ -15,6 +16,7 @@ from tram.cau_hinh.giao_viec import CauHinhGiaoViec
 from tram.duong_dan import tram_home
 from tram.giao_viec.ban_chep import KiemLaiDangBan, giu_khoa, ten_ban_chep
 from tram.giao_viec.git_kiem import kho_kiem
+from tram.giao_viec.kiem_goc import uid_that, kiem_sudoers_khong_root, kiem_thu_muc_goc
 from tram.giao_viec.kho_kiem_tao import url_origin
 from tram.giao_viec.principal_kiem import PrincipalKiem
 from tram.giao_viec.quyen import KHONG_CO, phien_ban_quyen
@@ -66,7 +68,8 @@ def _dung_duoc(pk: PrincipalKiem, thu_muc: Path | None, chay_lenh: Callable) ->
 
 
 def kiem_principal(pk: PrincipalKiem | None, thu_muc: Path | None, *, chay: Callable = subprocess.run,
-                   chay_lenh: Callable = chay_mot_lenh, toi: str | None = None) -> list[MucKiem]:
+                   chay_lenh: Callable = chay_mot_lenh, toi: str | None = None,
+                   uid_cua: Callable[[str], int] = uid_that) -> list[MucKiem]:
     if pk is None:
         return [_muc("principal kiểm lại", False, "chưa đặt cach_ly.tram_kiem — chờ S6")]
     try:
@@ -79,6 +82,7 @@ def kiem_principal(pk: PrincipalKiem | None, thu_muc: Path | None, *, chay: Call
     return [_muc("principal: danh tính", id_.returncode == 0 and ten == pk.ten != (toi or getpass.getuser()), ten[:40]),
             _muc("principal: giữ APP_ENV", "APP_ENV=testing" in env.stdout.splitlines(), "lệnh kiểm phải thấy APP_ENV"),
             _muc("principal: không đọc kho trạm", doc.returncode != 0, str(tram_home() / "su-kien.db")),
+            kiem_thu_muc_goc(pk, thu_muc, uid_cua=uid_cua), kiem_sudoers_khong_root(chay=chay),
             _ghi_duoc(pk, thu_muc, chay), _dung_duoc(pk, thu_muc, chay_lenh)]
 
 
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_kiem_goc.py tests/test_giao_kiem.py -q`
Expected: `24 passed`

Run: `uv run pytest -q`
Expected: `N₀ + 51 passed` (2151 — sau đợt 2 + 13; ghép cùng Task 6 bản r47 → N₀ + 79 = 2179, đo thật).

- [ ] **Step 5: Commit**

```bash
git add tram/giao_viec/kiem_goc.py tram/giao_viec/kiem_san_sang.py tests/test_kiem_goc.py tests/test_giao_kiem.py
git commit -m "feat(giao-viec): tram giao kiem kiểm thư mục kiểm của tram-kiem và sudoers không NOPASSWD root (lát 3c, D22)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 8: `tram chu go-cai-dat-tho` — gỡ theo sổ, chỉ thứ còn đúng định danh (R2, R4, R5)

> **Bản r47 (16/10, sau review Codex đợt 5):** gỡ giữ khoá sổ suốt lệnh (R4); user luôn `-deleteUser -keepHome`, nhà là bước riêng chỉ khi `--xoa-nha`, chỉ sau khi user đã gỡ và nhà còn đúng inode (R5); thân lệnh CLI nằm trong `go_cai_dat_tho.lenh_cli`, script chèn chỉ thêm hàm gọi sang. Thay hẳn bản bị chặn.

**Độ khó:** `de` · **Đợt:** 4 · **Song song với:** Task 11 · **Phải xong trước:** Task 6

**Files:**
- Create: `tram/chu/go_cai_dat_tho.py`
- Modify: `tram/chu/lenh_tho.py` — **script chèn theo mốc** (file Task 6 vừa sửa bằng bản vá; mốc không phụ thuộc số dòng)
- Test: `tests/test_go_cai_dat_tho.py`, `tests/test_go_cai_lai.py` (mới)

**Interfaces:**
- Consumes: `SoCai`, `SoCaiDangBan`, `Muc`, `doi_soat` (Task 6), `dinh_danh.cung/khop/quan_sat_that` (Task 6), `DAEMON`, `NHAN_THO`, `lap_ke_hoach_tho` (Task 6, trong test), `KeHoach`, `in_ke_hoach`, `thuc_hien`, `_hoi`, `USER_RE`, `HeGia` (test).
- Produces: `TEN = USER_RE`, `lenh_go(m) -> list[list[str]]`, `go(so, m, *, quan_sat, chay, bao) -> bool`, `lap_ke_hoach_go(so, *, toi, quan_sat=None, chay=subprocess.run, xoa_nha=False, bao=print) -> KeHoach` (`buoc` rỗng = không còn gì để gỡ; sổ hỏng hoặc trường sổ sai dạng → ValueError), `lenh_cli(args, *, hoi) -> int`. CLI `tram chu go-cai-dat-tho [--xoa-nha] [--dong-y]` — mã 0 khi không còn gì (kể cả chưa có sổ) hoặc đã chạy, 1 khi không `dong-y` hoặc dừng giữa chừng, 2 khi sổ hỏng, `dscl` lỗi hoặc đang có cài/gỡ khác.

- [ ] **Step 1: Viết test thất bại**

`tests/test_go_cai_dat_tho.py` (mới):

```python
"""`tram chu go-cai-dat-tho` (lát 3c R2, bead bs-urj.14; Codex F02): chỉ gỡ thứ sổ ghi `da_tao` và còn đúng định danh;
user có sẵn/addUser lỗi không bị xoá; đối soát crash; thư mục không rỗng chỉ cảnh báo; chạy lại rỗng. Cài bằng chính
`cai-dat-tho` trên `HeGia` — KHÔNG sudo/sysadminctl/launchctl thật."""
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from he_gia import HeGia
from tram.chu import lenh_tho
from tram.chu.cai_dat import thuc_hien
from tram.chu.cai_dat_tho import DAEMON, SUDOERS, lap_ke_hoach_tho
from tram.chu.go_cai_dat_tho import lap_ke_hoach_go
from tram.chu.so_cai_tho import SoCai
from tram.chu.tai_nguyen import LoiCaiDat
from tram.cli import tao_parser
from tram.giao_viec.principal_kiem import tu_cach_ly
from tram.tho.quyen_kiem import HO_SO_KIEM, THU_MUC_CAI


def cai(tmp_path, he, *, co_che="sandbox", chay=None):
    kh = lap_ke_hoach_tho(uv="uv", repo=Path("/r"), tram="hung", quan_ly="tram-tho", co_che=co_che,
                          khe={"claude-1": "tram-k-1"}, kiem=tu_cach_ly(f"{co_che}:tram-kiem"),
                          thu_muc_kiem=tmp_path / "kiem", quan_sat=he.quan_sat, chay=chay or he.chay)
    thuc_hien(kh, chay=he.chay)


def ke_hoach_go(he, bao=None, **kw):
    return lap_ke_hoach_go(SoCai(), toi="hung", quan_sat=he.quan_sat, chay=he.chay,
                           bao=(bao if bao is not None else []).append, **kw)


def test_go_dung_thu_tu_het_sach_va_chay_lai_rong(tram_home_tam, tmp_path):
    he = HeGia()
    cai(tmp_path, he)
    kh = ke_hoach_go(he)
    assert [m.split(":")[0] for m, _ in kh.buoc] == [
        "Đối soát sổ cài đặt (khép bản ghi dở do crash)", f"Gỡ tep {DAEMON} nếu còn đúng định danh trong sổ",
        f"Gỡ tep {HO_SO_KIEM} nếu còn đúng định danh trong sổ", f"Gỡ tep {SUDOERS} nếu còn đúng định danh trong sổ",
        f"Gỡ thu_muc {tmp_path}/kiem nếu còn đúng định danh trong sổ",
        *(f"Gỡ user {u} nếu còn đúng định danh trong sổ" for u in ("tram-k-1", "tram-kiem", "tram-tho")),
        f"Gỡ thu_muc {THU_MUC_CAI} nếu còn đúng định danh trong sổ"]
    he.lenh.clear()
    thuc_hien(kh, chay=he.chay)
    assert (he.user, he.tep) == ({}, {}) and he.lenh[0] == "sudo launchctl bootout system/vn.tram.tho"
    assert set(he.thu_muc) == {"/Users/tram-k-1", "/Users/tram-tho"}                    # nhà giữ (-keepHome, D40)
    assert f"sudo -u tram-kiem /bin/rm -rf {tmp_path}/kiem" in he.lenh and "sudo sysadminctl -deleteUser tram-kiem " \
        "-keepHome" in he.lenh
    assert {m.su for m in SoCai().muc().values() if m.kieu != "nha"} == {"da_go"} and ke_hoach_go(he).buoc == []


def test_user_co_san_addUser_loi_khong_bi_xoa(tram_home_tam, tmp_path):
    he = HeGia()
    he.truoc["sysadminctl -addUser tram-kiem"] = lambda: he.them_user("tram-kiem")
    with pytest.raises(LoiCaiDat):
        cai(tmp_path, he, co_che="user")
    thuc_hien(ke_hoach_go(he), chay=he.chay)
    assert list(he.user) == ["tram-kiem"] and he.user["tram-kiem"]["ten_day_du"] == "người khác"


@pytest.mark.parametrize("sau", [True, False])
def test_crash_quanh_lenh_tao_doi_soat_roi_moi_go(tram_home_tam, tmp_path, sau):
    he = HeGia()

    def chay(c, check=False, **kw):
        if not sau and "-addUser" in c:
            raise SystemExit("mất điện trước lệnh")
        he.chay(c, check=check)
        if "-addUser" in c:
            raise SystemExit("mất điện sau lệnh, trước da_tao")
    with pytest.raises(SystemExit):
        cai(tmp_path, he, co_che="user", chay=chay)
    assert [m.su for m in SoCai().muc().values()] == ["du_dinh"]
    thuc_hien(ke_hoach_go(he), chay=he.chay)
    assert he.user == {} and [m.su for m in SoCai().muc().values()] == ["da_go" if sau else "khong_tao"]
    assert ke_hoach_go(he).buoc == []          # trước lệnh: chỉ đối soát khép bản ghi dở, không có gì để gỡ


def test_user_xoa_tao_lai_hoac_file_bi_sua_thi_khong_go(tram_home_tam, tmp_path):
    he, bao = HeGia(), []
    cai(tmp_path, he, co_che="user")
    he.user["tram-kiem"]["guid"] = "GUID-tao-lai"
    he.tep[str(SUDOERS)] = "da-bi-sua"
    thuc_hien(ke_hoach_go(he, bao), chay=he.chay)
    assert list(he.user) == ["tram-kiem"] and list(he.tep) == [str(SUDOERS)] and len(bao) == 2
    assert all("không khớp sổ" in b for b in bao)


def test_thu_muc_khong_rong_chi_canh_bao_buoc_khac_van_chay(tram_home_tam, tmp_path):
    he, bao = HeGia(), []
    cai(tmp_path, he)
    he.tep[f"{THU_MUC_CAI}/cua-nguoi-khac"] = "x"
    thuc_hien(ke_hoach_go(he, bao), chay=he.chay)
    assert he.user == {} and str(THU_MUC_CAI) in he.thu_muc and "không rỗng" in bao[0]
    assert [m.split(":")[0] for m, _ in ke_hoach_go(he).buoc][1:] == [
        f"Gỡ thu_muc {THU_MUC_CAI} nếu còn đúng định danh trong sổ"]


def test_khong_go_user_dang_chay_lenh_va_xoa_nha(tram_home_tam, tmp_path):
    he = HeGia()
    cai(tmp_path, he, co_che="user")
    kh = lap_ke_hoach_go(SoCai(), toi="tram-tho", quan_sat=he.quan_sat, chay=he.chay, xoa_nha=True)
    thuc_hien(kh, chay=he.chay)
    assert list(he.user) == ["tram-tho"] and "sudo sysadminctl -deleteUser tram-kiem -keepHome" in he.lenh
    assert "sudo rm -rf /Users/tram-k-1" in he.lenh and "/Users/tram-tho" in he.thu_muc        # nhà của toi: giữ
    assert any("tram-tho: là tài khoản đang chạy" in c for c in kh.canh_bao)


def test_so_hong_thi_khong_go_gi(tram_home_tam, capsys):
    SoCai().p.parent.mkdir(parents=True)
    SoCai().p.write_text(json.dumps({"v": 2, "id": "x", "su": "da_tao"}) + "\n")
    assert lenh_tho._go_cai_dat_tho(SimpleNamespace(xoa_nha=False, dong_y=True)) == 2
    assert "hỏng" in capsys.readouterr().err


def test_lenh_cli(tram_home_tam, tmp_path, monkeypatch, capsys):
    args = SimpleNamespace(xoa_nha=False, dong_y=False)
    assert lenh_tho._go_cai_dat_tho(args) == 0 and "chưa có sổ" in capsys.readouterr().out
    he = HeGia()
    cai(tmp_path, he, co_che="user")
    monkeypatch.setattr("tram.chu.dinh_danh.quan_sat_that", he.quan_sat)
    monkeypatch.setattr("builtins.input", lambda _: "khong")
    monkeypatch.setattr("tram.chu.cai_dat.thuc_hien", lambda kh: pytest.fail("không được thực hiện"))
    assert lenh_tho._go_cai_dat_tho(args) == 1 and "sysadminctl -deleteUser tram-kiem" in capsys.readouterr().out
    assert tao_parser().parse_args(["chu", "go-cai-dat-tho", "--xoa-nha"]).ham.__name__ == "_go_cai_dat_tho"
```

`tests/test_go_cai_lai.py` (mới):

```python
"""Gỡ và cài lại sau crash (lát 3c, R4/R5 review đợt 5): đuôi sổ dở → đối soát → đọc → gỡ → đọc → cài lại; nhà giữ
lại (-keepHome) không bị nhận cho user mới khác UID; `--xoa-nha`; gỡ khi đang cài thì không làm gì. `HeGia` — KHÔNG
sudo/sysadminctl/launchctl thật."""
import json
from types import SimpleNamespace

import pytest

from he_gia import HeGia
from test_go_cai_dat_tho import cai, ke_hoach_go
from tram.chu import lenh_tho
from tram.chu.cai_dat import thuc_hien
from tram.chu.so_cai_tho import SoCai
from tram.chu.tai_nguyen import LoiCaiDat


def test_duoi_do_doi_soat_doc_go_doc_cai_lai(tram_home_tam, tmp_path):
    he = HeGia()

    def chay(c, check=False, **kw):
        r = he.chay(c, check=check)
        if "-addUser tram-k-1" in " ".join(c):
            raise SystemExit("mất điện khi đang ghi da_tao")
        return r
    with pytest.raises(SystemExit):
        cai(tmp_path, he, co_che="user", chay=chay)
    so = SoCai()
    i = next(m.id for m in so.muc().values() if m.ten == "tram-k-1")
    with open(so.p, "ab") as f:                                       # da_tao ghi dở, cắt giữa ký tự UTF-8
        f.write(f'{{"v": 2, "id": "{i}", "su": "da_tao", "dinh_danh": {{"ten_day_du": "tr'.encode() + "ạ".encode()[:2])
    du = so.p.read_bytes()
    hoan_chinh = du[:du.rfind(b"\n") + 1]
    thuc_hien(ke_hoach_go(he), chay=he.chay)                          # đọc (bỏ đuôi) → đối soát → gỡ
    du = so.p.read_bytes()
    assert du.startswith(hoan_chinh) and all(json.loads(d) for d in du.decode().splitlines())
    assert he.user == {} and {m.su for m in so.muc().values()} == {"da_go"} and ke_hoach_go(he).buoc == []
    assert so.p.with_name("so-cai.jsonl.duoi-hong").read_bytes().endswith("ạ".encode()[:2] + b"\n")
    cai(tmp_path, he, co_che="user")                                  # cài lại từ đầu, sổ cũ vẫn đọc được
    assert set(he.user) == {"tram-k-1", "tram-kiem", "tram-tho"} and len(ke_hoach_go(he).buoc) > 1


@pytest.mark.parametrize("dung_lai_uid", [False, True])
def test_cai_lai_sau_khi_giu_nha_khong_nhan_nha_cu(tram_home_tam, tmp_path, dung_lai_uid):
    he = HeGia(dung_lai_uid=dung_lai_uid)              # macOS dùng lại UID trống nhỏ nhất: nhà cũ "khớp UID"
    cai(tmp_path, he, co_che="user")
    thuc_hien(ke_hoach_go(he), chay=he.chay)                          # mặc định giữ nhà
    cu, he.lenh = dict(he.chu), []
    with pytest.raises(ValueError, match="nha /Users/tram-k-1"):
        cai(tmp_path, he, co_che="user")                              # từ chối ngay lúc lập kế hoạch
    assert he.lenh == [] and he.chu == cu and he.user == {}           # không tạo user, không chown nhà cũ
    thuc_hien(ke_hoach_go(he, xoa_nha=True), chay=he.chay)
    assert not any(p.startswith("/Users/") for p in he.thu_muc) and ke_hoach_go(he, xoa_nha=True).buoc == []
    cai(tmp_path, he, co_che="user")
    assert all(he.chu[f"/Users/{u}"] == he.user[u]["uid"] for u in ("tram-k-1", "tram-tho"))


def test_xoa_nha_khong_xoa_nha_la_va_khong_dung_var_empty(tram_home_tam, tmp_path):
    he = HeGia()
    he.hong.add("createhomedir -c -u tram-k-1")
    with pytest.raises(LoiCaiDat):
        cai(tmp_path, he, co_che="user")
    he.hong.clear()
    he.them_nha("tram-k-1", 777)                                      # nhà lạ xuất hiện, sổ ghi khong_tao
    thuc_hien(ke_hoach_go(he, xoa_nha=True), chay=he.chay)
    assert he.chu["/Users/tram-k-1"] == 777 and not any("rm -rf /Users/tram-k-1" in x for x in he.lenh)
    assert not any("/var/empty" in x for x in he.lenh if "-addUser" not in x)
    assert all("-keepHome" in x for x in he.lenh if "-deleteUser" in x)


def test_go_xoa_nha_ghi_da_go_va_chay_lai_rong(tram_home_tam, tmp_path):
    he = HeGia()
    cai(tmp_path, he, co_che="user")
    kh = ke_hoach_go(he, xoa_nha=True)
    assert [m.split(":")[0] for m, _ in kh.buoc][-2:] == ["Gỡ nha /Users/tram-k-1 nếu còn đúng định danh trong sổ",
                                                          "Gỡ nha /Users/tram-tho nếu còn đúng định danh trong sổ"]
    thuc_hien(kh, chay=he.chay)
    assert {m.su for m in SoCai().muc().values()} == {"da_go"} and ke_hoach_go(he, xoa_nha=True).buoc == []


def test_go_khi_dang_cai_thi_khong_lam_gi(tram_home_tam, tmp_path, capsys):
    he = HeGia()
    cai(tmp_path, he, co_che="user")
    with SoCai().giu():
        assert lenh_tho._go_cai_dat_tho(SimpleNamespace(xoa_nha=False, dong_y=True)) == 2
    assert "đang có cài/gỡ khác" in capsys.readouterr().err and set(he.user) == {"tram-k-1", "tram-kiem", "tram-tho"}


def test_khoa_truoc_khi_xem_so(tram_home_tam, capsys):
    with SoCai().giu():                                               # lần cài đang chờ dong-y, sổ chưa có dòng nào
        assert lenh_tho._go_cai_dat_tho(SimpleNamespace(xoa_nha=False, dong_y=True)) == 2
    assert "đang có cài/gỡ khác" in capsys.readouterr().err


def test_ten_user_khong_go_duoc_thi_tu_choi_cai(tram_home_tam, tmp_path):
    from pathlib import Path

    from tram.chu.cai_dat_tho import lap_ke_hoach_tho
    he = HeGia()
    with pytest.raises(ValueError, match="tram.tho"):
        lap_ke_hoach_tho(uv="uv", repo=Path("/r"), tram="hung", quan_ly="tram.tho", co_che="user", khe={},
                         quan_sat=he.quan_sat, chay=he.chay)
    assert he.lenh == []


def test_thu_muc_kiem_khong_go_duoc_thi_giu_user_va_chu_doi_thi_khong_giu(tram_home_tam, tmp_path):
    he, bao = HeGia(), []
    cai(tmp_path, he, co_che="user")
    he.hong.add(f"/bin/rm -rf {tmp_path}/kiem")
    thuc_hien(ke_hoach_go(he, bao, xoa_nha=True), chay=he.chay)
    assert "tram-kiem" in he.user and any("thư mục của nó chưa gỡ được" in b for b in bao)   # không mồ côi UID
    he.hong.clear()
    he.chu[f"{tmp_path}/kiem"] = 999                                   # chủ đổi (UID cũ bị dùng lại…)
    with pytest.raises(LoiCaiDat, match="không chown"):
        cai(tmp_path, he, co_che="user")
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_go_cai_dat_tho.py tests/test_go_cai_lai.py -q`
Expected: FAIL — `2 errors in 0.84s` (kết quả chạy thật trên bản sao: `ModuleNotFoundError: No module named 'tram.chu.go_cai_dat_tho'` khi nạp hai file test)

- [ ] **Step 3: Viết mã**

`tram/chu/go_cai_dat_tho.py` (mới):

```python
"""`tram chu go-cai-dat-tho` — hoàn tác `cai-dat-tho` (lát 3c R2, bs-urj.14; Codex F02; R4/R5 review đợt 5). Ở TÀI
KHOẢN TRẠM, giữ khoá sổ suốt lần gỡ, in kế hoạch rồi chờ `dong-y`. CHỈ gỡ thứ sổ ghi `da_tao` VÀ còn đúng định danh
(user: UID + GeneratedUID; file: sha256; thư mục, nhà: inode); quan sát lại trước/sau mỗi bước, hết hẳn mới `da_go`;
bước lỗi chỉ cảnh báo. User luôn `-deleteUser -keepHome`; nhà là bước riêng chỉ khi `--xoa-nha` (D40), sau khi user đã
gỡ. Thứ tự: đối soát → daemon → file root → thư mục kiểm (tram-kiem tự xoá) → user → nhà → thư mục root."""
import subprocess
from collections.abc import Callable

from tram.chu import dinh_danh
from tram.chu.cai_dat import KeHoach
from tram.chu.cai_dat_tho import DAEMON, NHAN_THO
from tram.chu.so_cai_tho import Muc, SoCai, doi_soat
from tram.tho.principal import USER_RE

TEN = USER_RE                                        # cùng luật với lúc cài (`lap_ke_hoach_tho`)


def _thu_tu(m: Muc) -> int:
    if m.kieu == "tep":
        return 0 if m.ten == str(DAEMON) else 1
    return {"user": 3, "nha": 4}.get(m.kieu, 2 if m.mong.get("chu") else 5)


def _hop_le(m: Muc) -> bool:
    """Trường của sổ đi vào lệnh sudo: tên user/chủ đúng dạng, đường dẫn tuyệt đối không `..`, nhà là /Users/<user>."""
    if m.kieu == "user":
        return bool(TEN.fullmatch(m.ten))
    chu, u = m.mong.get("chu"), m.mong.get("user", "")
    ok = m.ten.startswith("/") and m.ten.count("/") >= 2 and ".." not in m.ten.split("/") and chu != "root" \
        and (not chu or TEN.fullmatch(chu))
    return bool(ok) and (m.kieu != "nha" or bool(TEN.fullmatch(u)) and m.ten == f"/Users/{u}")


def lenh_go(m: Muc) -> list[list[str]]:
    if m.kieu == "user":
        return [["sudo", "pkill", "-KILL", "-u", m.ten], ["sudo", "sysadminctl", "-deleteUser", m.ten, "-keepHome"]]
    if m.kieu == "nha":
        return [["sudo", "rm", "-rf", m.ten]]
    if m.kieu == "tep":
        dung = [["sudo", "launchctl", "bootout", f"system/{NHAN_THO}"]] if m.ten == str(DAEMON) else []
        return dung + [["sudo", "rm", "-f", m.ten]]
    chu = m.mong.get("chu")
    return [["sudo", "-u", chu, "/bin/rm", "-rf", m.ten]] if chu else [["sudo", "rmdir", m.ten]]


def go(so: SoCai, m: Muc, *, quan_sat: Callable, chay: Callable, bao: Callable[[str], None]) -> bool:
    hien = quan_sat(m.kieu, m.ten)
    if hien is None:                                 # đã không còn: khép bản ghi da_tao
        for x in so.da_tao(m.kieu, m.ten):
            so.ket(x.id, "da_go", ly_do="quan sát: không còn")
        return True
    cua_tram = [x for x in so.da_tao(m.kieu, m.ten) if dinh_danh.cung(m.kieu, x.dinh_danh, hien)]
    if not cua_tram:
        bao(f"Bỏ qua {m.kieu} {m.ten}: định danh hiện tại không khớp sổ (có sẵn, bị xoá-tạo lại hoặc bị sửa)")
        return False
    if m.kieu == "user" and (con := [x.ten for x in so.muc().values() if x.su == "da_tao" and x.kieu == "thu_muc"
                                    and x.mong.get("chu") == m.ten and quan_sat("thu_muc", x.ten) is not None]):
        bao(f"Bỏ qua user {m.ten}: thư mục của nó chưa gỡ được ({', '.join(con)}) — không để thư mục mồ côi UID")
        return False
    if m.kieu == "nha" and quan_sat("user", m.mong["user"]) is not None:
        bao(f"Bỏ qua nha {m.ten}: user {m.mong['user']} vẫn còn — chỉ xoá nhà sau khi đã gỡ user")
        return False
    for c in lenh_go(m):
        chay(c, check=False)
    if quan_sat(m.kieu, m.ten) is not None:
        bao(f"Chưa gỡ được {m.kieu} {m.ten} (vd thư mục không rỗng) — Đại ca xem tay; sổ giữ nguyên")
        return False
    for x in cua_tram:
        so.ket(x.id, "da_go")
    return True


def lap_ke_hoach_go(so: SoCai, *, toi: str, quan_sat: Callable | None = None, chay: Callable = subprocess.run,
                    xoa_nha: bool = False, bao: Callable[[str], None] = print) -> KeHoach:
    """`buoc` rỗng = không còn gì để gỡ. Sổ hỏng hoặc trường sổ sai dạng → ValueError."""
    quan_sat = quan_sat or dinh_danh.quan_sat_that
    muc = so.muc().values()
    if not all(_hop_le(m) for m in muc):
        raise ValueError(f"Sổ cài đặt {so.p} hỏng (tên/đường dẫn sai dạng) — không gỡ gì, Đại ca kiểm tay")
    nhom = {(m.kieu, m.ten): m for m in muc if m.su in ("du_dinh", "da_tao")}
    canh_bao = [f"Không gỡ user {toi}: là tài khoản đang chạy lệnh này" for k, t in nhom if (k, t) == ("user", toi)]
    ds = sorted((m for m in nhom.values() if (m.kieu, m.ten) != ("user", toi) and m.mong.get("user") != toi
                 and (xoa_nha or m.kieu != "nha") and (m.su == "da_tao" or quan_sat(m.kieu, m.ten, nhe=True))),
                key=_thu_tu)                         # da_tao đã mất: bước gỡ chỉ khép bản ghi (da_go)
    buoc = [("Đối soát sổ cài đặt (khép bản ghi dở do crash)", lambda: doi_soat(so, quan_sat, dinh_danh.khop))]
    if not ds and all(m.su != "du_dinh" for m in muc):
        return KeHoach(tep={}, lenh=[], canh_bao=canh_bao)
    buoc += [(f"Gỡ {m.kieu} {m.ten} nếu còn đúng định danh trong sổ: " + " && ".join(" ".join(c) for c in lenh_go(m)),
              lambda m=m: go(so, m, quan_sat=quan_sat, chay=chay, bao=bao)) for m in ds]
    canh_bao += [f"Thư mục nhà của user được {'XOÁ (sau khi gỡ user)' if xoa_nha else 'giữ (--xoa-nha để xoá)'} (D40).",
                 "Token máy B ở trạm vẫn hiệu lực — thu hồi bằng `tram chu go-may B` nếu không cài lại.",
                 f"Sổ {so.p} được giữ (ghi thêm da_go). Chạy lại lệnh này để xem còn gì (đối soát có thể mở thêm)."]
    return KeHoach(tep={}, lenh=[], canh_bao=canh_bao, buoc=buoc)


def lenh_cli(args, *, hoi: Callable) -> int:
    """`tram chu go-cai-dat-tho`: 0 không còn gì / đã chạy; 1 không dong-y / dừng giữa chừng; 2 sổ hỏng / đang bận."""
    import getpass
    import sys

    from tram.chu.cai_dat import in_ke_hoach, thuc_hien
    so = SoCai()
    try:
        with so.giu():                         # R4: gỡ và cài không chạy đồng thời (khoá TRƯỚC khi xem sổ)
            kh = lap_ke_hoach_go(so, toi=getpass.getuser(), xoa_nha=args.xoa_nha) if so.p.exists() else None
            if kh is None or not kh.buoc:
                print("Không còn gì để gỡ." if kh else f"Không còn gì để gỡ (chưa có sổ {so.p}).")
                return 0
            print(in_ke_hoach(kh))
            if not hoi(args):
                print("Không làm gì.")
                return 1
            try:
                thuc_hien(kh)
            except (OSError, ValueError, subprocess.CalledProcessError) as e:
                print(f"Dừng giữa chừng: {e}\nChạy lại `tram chu go-cai-dat-tho` sau khi xem lỗi.", file=sys.stderr)
                return 1
    except (ValueError, OSError) as e:         # sổ hỏng, SoCaiDangBan, dscl lỗi lúc lập kế hoạch
        print(f"Không gỡ gì: {e}", file=sys.stderr)
        return 2
    print("Đã chạy kế hoạch gỡ. Chạy lại `tram chu go-cai-dat-tho`: phải báo không còn gì để gỡ.")
    return 0
```

`tram/chu/lenh_tho.py` — lưu script dưới đây ra file tạm (ví dụ `/private/tmp/…/chen_3c_t8.py`, **không** trong repo) rồi chạy từ gốc worktree: `uv run python <file>`. Kỳ vọng in `đã chèn go-cai-dat-tho`; `AssertionError` → dừng, báo người điều phối.

```python
"""Lát 3c Task 8 — chèn `tram chu go-cai-dat-tho` vào tram/chu/lenh_tho.py theo mốc (mỗi mốc khớp đúng một chỗ). Thân
lệnh ở `tram/chu/go_cai_dat_tho.lenh_cli`; ở đây chỉ hàm gọi sang và đăng ký parser."""
from pathlib import Path

p = Path("tram/chu/lenh_tho.py")
s = p.read_text(encoding="utf-8")
MOC_HAM = "def them_lenh_chu_tho(chu) -> None:\n"
MOC_DK = "    k.set_defaults(ham=_kiem_cach_ly)\n"
assert s.count(MOC_HAM) == 1, "mốc them_lenh_chu_tho"
assert s.count(MOC_DK) == 1, "mốc k.set_defaults(ham=_kiem_cach_ly)"
assert "_go_cai_dat_tho" not in s, "đã chèn rồi"
HAM = '''def _go_cai_dat_tho(args) -> int:
    from tram.chu.go_cai_dat_tho import lenh_cli
    return lenh_cli(args, hoi=_hoi)


'''
DK = '''    g = chu.add_parser("go-cai-dat-tho", help="Gỡ đúng thứ cai-dat-tho đã tạo theo sổ (chờ dong-y)")
    g.add_argument("--xoa-nha", action="store_true", help="Xoá luôn thư mục nhà của user (mặc định giữ)")
    g.add_argument("--dong-y", action="store_true")
    g.set_defaults(ham=_go_cai_dat_tho)
'''
s = s.replace(MOC_HAM, HAM + MOC_HAM).replace(MOC_DK, MOC_DK + DK)
p.write_text(s, encoding="utf-8")
print("đã chèn go-cai-dat-tho")
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_go_cai_dat_tho.py tests/test_go_cai_lai.py tests/test_cai_dat_tho_kiem.py tests/test_cai_nha_tho.py tests/test_chu_tho.py -q`
Expected: `38 passed in 2.82s`

Run: `uv run pytest -q`
Expected: `N₀ + 97 passed` (2197 — sau đợt trước + 18; ghép cùng Task 11 sau review → N₀ + 125 (dự kiến, chưa chạy))

- [ ] **Step 5: Commit**

```bash
git add tram/chu/go_cai_dat_tho.py tram/chu/lenh_tho.py tests/test_go_cai_dat_tho.py tests/test_go_cai_lai.py
git commit -m "feat(chu): tram chu go-cai-dat-tho — giữ khoá sổ, chỉ gỡ thứ sổ ghi da_tao và còn đúng định danh, nhà là bước riêng (--xoa-nha), đối soát crash, chờ dong-y (lát 3c R2/R4/R5, bs-urj.14)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

> **Task 10 — thêm 16/10 theo D40 (cây kiểm chọn (b)).** Đánh số 10 để không đổi số Task 1–9 đã được tham chiếu; chạy ở **đợt 2** cùng Task 5.

### Task 10: Bản chép là repo git một commit — D40 chọn (b)

**Độ khó:** `de` · **Đợt:** 2 · **Song song với:** Task 5 · **Phải xong trước:** Task 3

**Files:**
- Create: `tram/giao_viec/repo_ban_chep.py`
- Modify: `tram/giao_viec/ban_chep.py` (`chep_ban` dựng repo sau `tar -x`; docstring), `tram/giao_viec/kiem_lai.py` (docstring)
- Modify: `tests/test_ban_chep.py` (lệnh kiểm của test đầu đòi repo git và `.env.testing` không bị theo dõi; đổi tên test đó)
- Test: `tests/test_ban_chep_git.py` (mới)

**Interfaces:**
- Consumes: `chep_ban`, `LoiBanChep`, `_chay` (Task 3, `tram/giao_viec/ban_chep.py`); fixture `m`, helper `chay`, `ban_chep` của `tests/test_kiem_lai_principal.py` (Task 3); `CO`, `MOI_TRUONG`, `git` của `tests/git_gia.py`; `dung_kho` của `tests/kho_kiem_gia.py`.
- Produces: `tram/giao_viec/repo_ban_chep.py`: `MOI_TRUONG`, `CAU_HINH`, `lenh_repo(wt) -> dict[str, list[str]]` (khoá `init`, `add`, `commit`, đúng thứ tự chạy). `chep_ban` giữ chữ ký: sau `tar -x` chạy ba lệnh qua `boc` (DƯỚI `tram-kiem`); lệnh nào mã ≠ 0 → `LoiBanChep("git <bước> dưới tram-kiem lỗi …")` — `kiem_lai` không chạy lệnh kiểm, `don_ban` vẫn dọn, vòng tick đếm lỗi (cùng đường với `tar` lỗi).
- Hợp đồng (G32, G33): repo một commit, nhánh `kiem`, tác giả `tram-kiem <tram-kiem@localhost>`, thông điệp `kiem`; cây của commit = cây commit gốc (`git add -A -f`); dựng TRƯỚC khi môi trường kiểm vào cây — `.env.testing` là file chưa theo dõi, không bao giờ thành đối tượng git (đối tượng git đọc được bởi user khác vì thư mục bản chép 0755, rủi ro (c)).
- Ghi chú đợt: chỉ sửa file của Task 3 và thêm file mới — rời hẳn Task 5 (Task 5 không chạm `ban_chep.py`, `kiem_lai.py`, `tests/test_ban_chep.py`).

- [ ] **Step 1: Viết test thất bại**

`tests/test_ban_chep_git.py` (mới):

```python
"""D40 (b): bản chép kiểm là repo git MỘT commit do `tram-kiem` tự dựng sau `tar -x` — cây đúng cây commit gốc, không
lịch sử/remote của kho thật; hook, filter, template ở cấu hình global/system/biến môi trường không chạy; git lỗi thì
fail-closed như tar. `git` THẬT dưới user đang test (`boc` đồng nhất thay `sudo -u tram-kiem`) trong `tmp_path`."""
import os
import subprocess

import pytest

from git_gia import CO, MOI_TRUONG, git
from kho_kiem_gia import dung_kho
from test_kiem_lai_principal import ban_chep, chay, m  # noqa: F401 — fixture `m` dùng chung
from tram.giao_viec.ban_chep import LoiBanChep, chep_ban
from tram.giao_viec.git_kiem import fetch

RONG = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"           # cây rỗng của git


def nhap(kho, *a: str, vao: str) -> str:
    return subprocess.run(["git", *CO, "-C", str(kho), *a], input=vao, capture_output=True, text=True,
                          env=MOI_TRUONG, check=True).stdout.strip()


def chep(tmp_path, k, sha):
    fetch(k.kho)
    wt = tmp_path / "kiem" / "g-1-ab"
    chep_ban(k.kho, sha, wt, boc=lambda a: a)
    return wt


def test_ban_chep_la_repo_mot_commit_cay_dung_commit_goc_khong_lich_su(tmp_path):
    k = dung_kho(tmp_path)
    k.day("tram/hr-1", {"bo-qua.log": "y", "src/a.py": "x = 1\n"}, tu=k.main)
    sha = k.day("tram/hr-1", {".gitignore": "*.log\n"})               # bo-qua.log vẫn được theo dõi dù bị ignore
    wt = chep(tmp_path, k, sha)
    assert (wt / ".git").is_dir() and git(wt, "rev-list", "--all", "--count") == "1"
    assert git(wt, "rev-parse", "HEAD^{tree}") == git(k.kho, "rev-parse", f"{sha}^{{tree}}")
    assert git(wt, "log", "-1", "--format=%s %an") == "kiem tram-kiem" and git(wt, "status", "--porcelain") == ""
    assert git(wt, "remote") == "" and not (wt / ".git" / "objects" / "info" / "alternates").exists()
    assert all(subprocess.run(["git", "-C", str(wt), "cat-file", "-e", f"{c}^{{commit}}"], env=MOI_TRUONG,
                              capture_output=True).returncode != 0 for c in (sha, k.main))


def test_hook_filter_template_cua_cau_hinh_ngoai_khong_chay(tmp_path, monkeypatch):
    dau, mau, cfg = tmp_path / "DA_CHAY", tmp_path / "mau", tmp_path / "gitconfig"
    moc = f"#!/bin/sh\ntouch {dau}\n"
    k = dung_kho(tmp_path)
    for p in (k.dev / ".husky" / "pre-commit", k.dev / ".husky" / "post-commit", mau / "hooks" / "post-commit"):
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(moc)
        p.chmod(0o755)
    sha = k.day("tram/hr-1", {".gitattributes": "* filter=x\n*.bin filter=lfs\n", "a.bin": "z", "a.txt": "a"},
                tu=k.main)
    cfg.write_text(f'[core]\n\thooksPath = .husky\n[init]\n\ttemplateDir = {mau}\n'
                   f'[filter "lfs"]\n\tclean = touch {dau}; cat\n\tsmudge = cat\n\trequired = true\n')
    for bien, gt in {"GIT_CONFIG_GLOBAL": cfg, "GIT_CONFIG_SYSTEM": cfg, "GIT_TEMPLATE_DIR": mau, "GIT_CONFIG_COUNT": 2,
                     "GIT_CONFIG_KEY_0": "filter.x.clean", "GIT_CONFIG_VALUE_0": f"touch {dau}; cat",
                     "GIT_CONFIG_KEY_1": "filter.x.smudge", "GIT_CONFIG_VALUE_1": "cat"}.items():
        monkeypatch.setenv(bien, str(gt))                    # cấu hình "của tram-kiem" mà trạm không kiểm soát
    wt = chep(tmp_path, k, sha)
    assert (wt / ".git").is_dir() and not dau.exists() and not (wt / ".git" / "hooks").exists()
    assert git(wt, "rev-parse", "HEAD^{tree}") == git(k.kho, "rev-parse", f"{sha}^{{tree}}")


@pytest.mark.parametrize("buoc", ["init", "add", "commit"])
def test_git_loi_thi_fail_closed_nhu_tar(m, buoc):
    boc = lambda a: ["/usr/bin/false"] if buoc in a else a
    with pytest.raises(LoiBanChep, match=f"git {buoc}"):
        chay(m, {"kiem.sh": f"touch {m[2]}/DA_CHAY\n"}, boc=boc)
    assert not (m[2] / "DA_CHAY").exists() and ban_chep(m) == []


def test_ban_chep_rong_van_la_repo_mot_commit_cay_rong(tmp_path):
    k = dung_kho(tmp_path)
    wt = chep(tmp_path, k, git(k.kho, "commit-tree", RONG, "-m", "rong"))
    assert os.listdir(wt) == [".git"] and git(wt, "rev-parse", "HEAD^{tree}") == RONG
    assert git(wt, "rev-list", "--all", "--count") == "1"


def test_commit_chua_git_thi_khong_dung_repo_len_do(tmp_path):
    k = dung_kho(tmp_path)
    b = nhap(k.kho, "hash-object", "-w", "--stdin", vao=f"[core]\n\tfsmonitor = touch {tmp_path}/DA_CHAY\n")
    t = nhap(k.kho, "mktree", vao=f"100644 blob {b}\tconfig\n")
    t = nhap(k.kho, "mktree", vao=f"040000 tree {t}\t.git\n100644 blob {b}\ta.txt\n")     # git không tự tạo được
    with pytest.raises(LoiBanChep, match="git archive"):
        chep(tmp_path, k, git(k.kho, "commit-tree", t, "-m", "x"))
    assert not (tmp_path / "kiem" / "g-1-ab" / ".git").exists() and not (tmp_path / "DA_CHAY").exists()
```

`tests/test_ban_chep.py` (sửa — bản vá):

```diff
diff --git a/tests/test_ban_chep.py b/tests/test_ban_chep.py
index 5584133..1e43f40 100644
--- a/tests/test_ban_chep.py
+++ b/tests/test_ban_chep.py
@@ -14,10 +14,11 @@ from tram.giao_viec.ban_chep import KiemLaiDangBan, LoiBanChep, chep_ban, giu_kh
 from tram.giao_viec.git_kiem import fetch
 from tram.kiem.moi_truong import LoiMoiTruongKiem
 
-KIEM = 'test -f tests/a.txt && test ! -e .git && grep -q "Format:" v.txt && grep -q DB_DATABASE=test .env.testing\n'
+KIEM = ('test -f tests/a.txt && grep -q "Format:" v.txt && grep -q DB_DATABASE=test .env.testing && git ls-files '
+        '--error-unmatch tests/a.txt >/dev/null && ! git ls-files --error-unmatch .env.testing 2>/dev/null\n')
 
 
-def test_ban_chep_dung_commit_khong_git_khong_bi_export_ignore_giau(m):
+def test_ban_chep_dung_commit_co_repo_git_khong_bi_export_ignore_giau(m):
     (m[0].kho / "kiem.sh").write_text("exit 1\n")              # thư mục làm việc của kho kiểm bị sửa: không ảnh hưởng
     kq = chay(m, {"kiem.sh": KIEM, "tests/a.txt": "x", "v.txt": "$Format:%H$\n",
                   ".gitattributes": "/tests export-ignore\nv.txt export-subst\n"})
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_ban_chep_git.py tests/test_ban_chep.py tests/test_kiem_lai_principal.py tests/test_kiem_lai.py tests/test_luong_giao.py tests/test_tick_hai_pha.py -q`
Expected: FAIL — `7 failed, 34 passed` (kết quả chạy thật):
- `test_ban_chep_la_repo_mot_commit_cay_dung_commit_goc_khong_lich_su`, `test_hook_filter_template_cua_cau_hinh_ngoai_khong_chay`: `AssertionError: assert (False)` — `where False = is_dir()` của `…/kiem/g-1-ab/.git`;
- `test_git_loi_thi_fail_closed_nhu_tar[init]`, `[add]`, `[commit]`: `Failed: DID NOT RAISE <class 'tram.giao_viec.ban_chep.LoiBanChep'>`;
- `test_ban_chep_rong_van_la_repo_mot_commit_cay_rong`: `AssertionError: assert ([] == ['.git']`;
- `test_ban_chep_dung_commit_co_repo_git_khong_bi_export_ignore_giau`: `AssertionError` — `KetQuaKiemLai(dat=False, …'tom_tat': 'fatal: not a git repository (o...it'…)`.

`test_commit_chua_git_thi_khong_dung_repo_len_do` đã xanh từ Step 2 — cố ý: `git archive` của trạm (git 2.56 và Apple git 2.39 đều đã đo) từ chối đường dẫn `.git`/`.GIT`/`sub/.git` ("invalid path"), nên Task 3 đã ném `LoiBanChep`. Test giữ bất biến đó cho Task 10: không bao giờ `git init` lên một `.git` do commit mang vào (cấu hình trong đó có thể đặt `core.fsmonitor`, `filter.*`).

- [ ] **Step 3: Viết mã**

`tram/giao_viec/repo_ban_chep.py` (mới):

```python
"""Bản chép kiểm là repo git MỘT commit (D40 chọn (b), lát 3c): sau `tar -x`, `tram-kiem` tự `git init`, `git add -A
-f`, `git commit` trong bản chép — đủ cho công cụ chỉ cần "là repo git" (husky, `git ls-files`, `git diff`). Cây của
commit = cây commit gốc (`-f`: cả file đã theo dõi mà `.gitignore` bỏ); KHÔNG lịch sử, remote, alternates của kho thật.

Không cấu hình nào ngoài trạm kiểm soát được chạm vào: `env -i` (bỏ `GIT_CONFIG_COUNT/PARAMETERS`, `GIT_TEMPLATE_DIR`,
`GIT_DIR`…), `GIT_CONFIG_NOSYSTEM`, `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_ATTR_NOSYSTEM`, `core.attributesFile=/dev/null`,
`--template=` (không template, không `.git/hooks`), `core.hooksPath=/dev/null` + `--no-verify`. `.gitattributes` của
cây chỉ GỌI TÊN driver (`filter=lfs`); lệnh `clean`/`process` chỉ đến từ cấu hình — không còn nguồn nào, nên `git add`
không chạy filter. `.git` trong commit: `git archive` của trạm từ chối (đường dẫn không hợp lệ) → `LoiBanChep`."""
import shutil

MOI_TRUONG = ("/usr/bin/env", "-i", "PATH=/usr/bin:/bin:/usr/sbin:/sbin", "HOME=/var/empty", "LC_ALL=C",
              "GIT_CONFIG_NOSYSTEM=1", "GIT_CONFIG_GLOBAL=/dev/null", "GIT_ATTR_NOSYSTEM=1")
CAU_HINH = ("core.hooksPath=/dev/null", "core.attributesFile=/dev/null", "core.fsmonitor=false", "gc.auto=0",
            "maintenance.auto=false", "commit.gpgSign=false", "init.defaultBranch=kiem", "user.name=tram-kiem",
            "user.email=tram-kiem@localhost")


def lenh_repo(wt) -> dict[str, list[str]]:
    """Ba lệnh (chạy theo thứ tự, DƯỚI `tram-kiem` qua `boc`) dựng repo một commit trong `wt`."""
    git = [*MOI_TRUONG, shutil.which("git") or "/usr/bin/git"]
    for c in CAU_HINH:
        git += ["-c", c]
    git += ["-C", str(wt)]
    return {"init": [*git, "init", "-q", "--template="], "add": [*git, "add", "-A", "-f"],
            "commit": [*git, "commit", "-q", "--allow-empty", "--no-verify", "-m", "kiem"]}
```

`tram/giao_viec/ban_chep.py`, `tram/giao_viec/kiem_lai.py` (sửa — bản vá):

```diff
diff --git a/tram/giao_viec/ban_chep.py b/tram/giao_viec/ban_chep.py
index f13aa53..eccbb40 100644
--- a/tram/giao_viec/ban_chep.py
+++ b/tram/giao_viec/ban_chep.py
@@ -3,9 +3,11 @@
 Trạm `git archive <commit>` từ kho kiểm, đưa qua stdin cho `tar -x` chạy DƯỚI `tram-kiem` (`boc`) vào một thư mục MỚI
 dưới `thu_muc_kiem`; môi trường kiểm cũng qua stdin (tar một file); `tram-kiem` tự `rm -rf` khi xong. Mọi thao tác
 trên cây đều dưới quyền `tram-kiem`, nên symlink/hardlink trong cây không với tới thứ gì `tram-kiem` vốn không với tới.
-Cây kiểm KHÔNG có `.git`. Fail-closed:
+Cây kiểm là repo git MỘT commit do `tram-kiem` tự dựng (D40 (b), `repo_ban_chep.py`) — không lịch sử kho thật.
+Fail-closed:
 - một lần kiểm lại một lúc trên máy (khoá `~/.tram/kiem-lai.khoa`, không chờ) — lần thứ hai ném `KiemLaiDangBan`;
 - `don_sach` (giết mọi tiến trình `tram-kiem`, xác nhận không còn) chạy trước khi chép và trước khi dọn — lỗi → ném;
+- `tar` hoặc `git init/add/commit` lỗi → ném `LoiBanChep`, không chạy lệnh kiểm;
 - dọn xong mà thư mục vẫn còn → ném `LoiBanChep`: kết quả kiểm lại KHÔNG được trả về."""
 import fcntl
 import os
@@ -17,6 +19,7 @@ from pathlib import Path
 
 from tram.duong_dan import tram_home
 from tram.giao_viec.cay_kiem import loi_dich_trong_cay, nguon_archive, tar_mot_tep
+from tram.giao_viec.repo_ban_chep import lenh_repo
 from tram.kiem.moi_truong import LoiMoiTruongKiem, loi_dich
 
 TAR_NHAN = ("/usr/bin/tar", "-x", "-f", "-", "-C")
@@ -59,7 +62,8 @@ def _chay(argv: list[str], **kw) -> subprocess.CompletedProcess:
 
 
 def chep_ban(kho: Path, commit: str, wt: Path, *, boc: Boc) -> None:
-    """`tram-kiem` tạo `wt` MỚI (đã có → lỗi) rồi tự `tar -x` nội dung đúng commit từ stdin."""
+    """`tram-kiem` tạo `wt` MỚI (đã có → lỗi), tự `tar -x` nội dung đúng commit từ stdin, rồi tự dựng repo git một
+    commit (D40) — TRƯỚC khi môi trường kiểm vào cây, nên `.env.testing` không bao giờ thành đối tượng git."""
     _chay(boc(["/bin/mkdir", "-p", str(wt.parent)]), check=True)
     _chay(boc(["/bin/mkdir", str(wt)]), check=True)
     nguon = nguon_archive(kho, commit)
@@ -70,6 +74,10 @@ def chep_ban(kho: Path, commit: str, wt: Path, *, boc: Boc) -> None:
         ma = nguon.wait(timeout=THOI_GIAN)
     if ma or nhan.returncode:
         raise LoiBanChep(f"git archive (mã {ma}) | tar dưới tram-kiem (mã {nhan.returncode}) lỗi")
+    for buoc, argv in lenh_repo(wt).items():
+        r = _chay(boc(argv))
+        if r.returncode:
+            raise LoiBanChep(f"git {buoc} dưới tram-kiem lỗi (mã {r.returncode}) — bản chép không thành repo kiểm")
 
 
 def nhan_moi_truong(kho: Path, commit: str, wt: Path, nguon: Path, dich: str, *, boc: Boc) -> None:
diff --git a/tram/giao_viec/kiem_lai.py b/tram/giao_viec/kiem_lai.py
index 7126d61..ca7a35f 100644
--- a/tram/giao_viec/kiem_lai.py
+++ b/tram/giao_viec/kiem_lai.py
@@ -5,8 +5,9 @@
 (khớp `lenh_cho_phep`, không shell, 15 phút/lệnh, kill cả nhóm); 5. đạt ⇔ mọi lệnh chạy được và pass.
 `boc` chọn principal `tram-kiem` (phần 3 §7.3 mục 5 — chờ S6); mã này không tự chạy dưới quyền trạm.
 Lát 3c (D22): bước 1, 3 chạy trên BẢN CHÉP do `tram-kiem` sở hữu (`ban_chep.py` — `git archive` → `tar -x` dưới
-`tram-kiem`, môi trường kiểm qua stdin, `tram-kiem` tự dọn; không `.git`, không worktree, không trao quyền). Một lần
-kiểm lại một lúc; `don_sach` trước khi chép và trước khi dọn; dọn không sạch → ném, KHÔNG trả kết quả."""
+`tram-kiem`, môi trường kiểm qua stdin, `tram-kiem` tự dọn; repo git MỘT commit do `tram-kiem` tự dựng — D40 (b);
+không worktree, không trao quyền). Một lần kiểm lại một lúc; `don_sach` trước khi chép và trước khi dọn; dọn không
+sạch → ném, KHÔNG trả kết quả."""
 from collections.abc import Callable, Mapping
 from dataclasses import dataclass
 from pathlib import Path
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_ban_chep_git.py tests/test_ban_chep.py tests/test_kiem_lai_principal.py tests/test_kiem_lai.py tests/test_luong_giao.py tests/test_tick_hai_pha.py -q`
Expected: `41 passed`

Run: `uv run pytest -q`
Expected: `N₀ + 21 passed` trên `main` sau đợt 1 (2121); ghép cùng Task 5 → `N₀ + 38` (2138 — r47 đo thật)

Kiểm thêm (đã làm khi viết plan — đột biến từng lớp, mỗi lần bỏ một thứ rồi chạy `tests/test_ban_chep_git.py tests/test_ban_chep.py`): bỏ `-i` của `env` → 1 failed (filter `x` khai qua `GIT_CONFIG_COUNT` chạy); bỏ `--template=` → 1 failed (template hệ thống chép `.git/hooks`); bỏ `-f` của `git add` → 1 failed (cây khác commit gốc). Bỏ riêng `GIT_CONFIG_NOSYSTEM`, `GIT_CONFIG_GLOBAL=/dev/null`, `core.hooksPath=/dev/null` hoặc `--no-verify` → vẫn 14 passed: các lớp này chồng lên nhau có chủ ý (`env -i` + `HOME=/var/empty` đã bỏ cấu hình global/biến môi trường; `--no-verify` và `core.hooksPath` cùng chặn hook) — giữ cả để một lớp hỏng không mở đường.

- [ ] **Step 5: Commit**

```bash
git add tram/giao_viec/repo_ban_chep.py tram/giao_viec/ban_chep.py tram/giao_viec/kiem_lai.py tests/test_ban_chep_git.py tests/test_ban_chep.py
git commit -m "feat(giao-viec): bản chép kiểm là repo git một commit do tram-kiem tự dựng — env -i, không cấu hình global/system/template, hook tắt, git lỗi thì fail-closed (lát 3c, D40 (b))" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

> **Task 11, 12 — thêm 16/10 (bản r47) theo review Codex đợt 5 (C01, Q03).** Đánh số tiếp để không đổi số Task 1–10.

### Task 11: Vòng đời cách ly của `tram-kiem` — gỡ và xác nhận nguồn lịch, dọn tệp cài cắm, HOME mới mỗi lần (C01)

**Độ khó:** `kho` · **Đợt:** 4 · **Song song với:** Task 8 · **Phải xong trước:** Task 3, 5, 7, 10

**Files:**
- Create: `tram/giao_viec/lich_tram_kiem.py`, `tram/giao_viec/launchd_kiem.py`, `tram/giao_viec/don_tram_kiem.py`
- Modify: `tram/giao_viec/principal_kiem.py` (`don_sach` gọi `don_tram_kiem.don_sach`, nhận `goc`), `tram/giao_viec/ban_chep.py` (`nha_cua`, `boc_nha`; `chep_ban` tạo `<bản chép>.nha`, `don_ban` dọn cả hai), `tram/giao_viec/kiem_lai.py` (lệnh kiểm qua `boc_nha`), `tram/giao_viec/noi_that.py` (`don_sach=partial(pk.don_sach, goc=cg.thu_muc_kiem)`), `tram/giao_viec/kiem_san_sang.py` (`_ghi_duoc` truyền `goc`)
- Modify: `tests/test_principal_kiem_hop_nhat.py` (3 test `don_sach` chạy trên hệ giả), `tests/test_kiem_lai_principal.py`, `tests/test_tick_hai_pha.py` (gốc có thêm `<bản chép>.nha`), `tests/test_noi_giao_viec.py` (`partial`), `tests/test_giao_kiem.py` (`chay_gia` chuyển lệnh `don_sach` cho `TramKiemGia`, gốc là thư mục riêng)
- Test: `tests/test_don_tep_loi_lenh.py` (mới, 3 ca review đợt 6), `tests/tram_kiem_gia.py` (công cụ, mới), `tests/test_don_tram_kiem.py`, `tests/test_don_tep_tram_kiem.py`, `tests/test_ban_chep_nha.py` (mới)

**Interfaces:**
- Consumes: `LoiBanChep` (T3), `PrincipalKiem`, `tu_cach_ly` (T5), `kiem_thu_muc_goc` (T7), `tram_home`.
- Produces:
  - `lich_tram_kiem.py`: `CRONTAB`, `ATQ`, `ATRM`, `FIND`, `VIEC_AT`, `ra(chay, argv)` (quá 30 s → `LoiBanChep`), `don_cron(pk, chay) -> bool`, `don_at(pk, chay, thu_muc=VIEC_AT) -> bool` (True = đã phải gỡ).
  - `launchd_kiem.py`: `LAUNCHCTL`, `nen_mac_dinh()`, `doc_nen(p=None) -> dict[nhãn, vân tay]` (thiếu → `LoiBanChep`), `nhan_launchd(van_ban) -> set[str]` (định dạng lạ → `LoiBanChep`), `in_mien(pk, chay, uid)`, `van_tay(pk, chay, uid, nhan)`, `don_launchd(pk, chay, uid, nen) -> bool`, `chup(pk, chay, uid) -> dict[nhãn, (vân tay, mô tả)]`.
  - `don_tram_kiem.py`: `PKILL`, `PGREP`, `NHA = "/var/empty"`, `GOC_CHUNG`, `THU_MUC_HE`, `uid_cua(ten, chay) -> int`, `con_tien_trinh(pk, chay) -> bool`, `kiem_nha(pk, chay)`, `don_tep(pk, goc, chay, goc_chung)`, `don_sach(pk, goc, *, chay, lan=6, ngu, nen=None, goc_chung=None, thu_muc_at=None)` — trả về khi HAI lượt liên tiếp sạch; đã phải gỡ lịch → `CoLichHenGio`; không xác nhận được → `LoiBanChep`.
  - `ban_chep.CoLichHenGio(LoiBanChep)`; `kiem_lai` bắt nó ở bước dọn cuối → `KetQuaKiemLai(dat=False, loi="lich-hen-gio")` (vòng tick tạo escalation như mọi lỗi kiểm lại).
  - `PrincipalKiem.don_sach(*, goc=None, chay, lan, ngu, **kw)`; `ban_chep.nha_cua(wt) -> Path`, `ban_chep.boc_nha(boc, wt) -> Boc`.
- Ghi chú đợt: chỉ sửa file của T3/T5/T7/T10 sau khi đã ghép đợt 3 — rời hẳn Task 8 (`tram/chu/*`, `tests/test_go*`).

- [ ] **Step 1: Viết test thất bại**

`tests/tram_kiem_gia.py` (mới — công cụ test, không phải test):

```python
"""`tram-kiem` GIẢ cho test `don_sach` (lát 3c, C01 — CHỈ DÙNG TRONG TEST): tiến trình, crontab, at, launchd và lịch tái
sinh trễ là trạng thái trong bộ nhớ — KHÔNG pkill/pgrep/crontab/atq/launchctl/sudo thật. `find`, `rm`, `stat` chạy THẬT
nhưng `find`/`rm` chỉ khi mọi đường dẫn nằm trong `tam` (tmp_path); `-user tram-kiem` đổi thành UID của user đang test.
`hen[nguon] = [n, con]`: nguồn (`cron`, `at:<id>`, `launchd:<nhãn>`, `khac`) còn tồn tại thì cứ mỗi n lần `pgrep` sinh
một tiến trình mới (tối đa `con` lần) — lịch hẹn giờ CHƯA tới lúc `pgrep` đầu tiên; `khi_chay[nguon]`: việc job làm."""
import os
import subprocess
from pathlib import Path

NEN = ("com.apple.trustd.agent", "com.apple.mdworker.shared")


def dung_tk(tmp_path: Path, tram_home: Path, monkeypatch, pk) -> "TramKiemGia":
    """`don_sach` thật trên hệ giả — gốc bản chép, thư mục ghi-chung, hàng đợi at đều trong tmp_path; có nền launchd."""
    he = TramKiemGia(tmp_path / "he", pk)
    he.ghi_nen(tram_home)
    monkeypatch.setattr("tram.giao_viec.don_tram_kiem.GOC_CHUNG", he.goc_chung)
    monkeypatch.setattr("tram.giao_viec.don_tram_kiem.VIEC_AT", he.thu_muc_at)
    return he


class TramKiemGia:
    def __init__(self, tam: Path, pk):
        self.tam, self.pk, self.uid = tam.resolve(), pk, os.getuid()
        self.song, self.cron, self.at, self.launchd, self.gui = 0, False, [], set(NEN), False
        self.nha, self.hong, self.hen, self.dem, self.goi, self.khi_chay = "/var/empty", set(), {}, 0, [], {}
        self.thu_muc_at, self.goc = self.tam / "at-jobs", self.tam / "kiem"
        self.goc_chung = (self.tam / "chung-tmp", self.tam / "chung-shared")
        self.he = {f"DARWIN_USER_{k}DIR": self.tam / "folders" / (k[:1] or "0") for k in ("TEMP_", "CACHE_", "")}
        self.chuong_trinh = {n: f"/usr/libexec/{n}" for n in NEN}       # nhãn → chương trình (vân tay)
        for d in (self.thu_muc_at, *self.goc_chung, *self.he.values()):
            d.mkdir(parents=True)
        self.goc.mkdir(mode=0o755)

    def ghi_nen(self, tram_home: Path) -> Path:
        from tram.giao_viec.launchd_kiem import chup
        p = tram_home / "kiem-lai" / "nen-launchd.txt"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("".join(f"{n}\t{v}\n" for n, (v, _) in chup(self.pk, self.chay, self.uid).items()))
        self.goi.clear()
        return p

    def _con(self, nguon: str) -> bool:
        loai, _, ten = nguon.partition(":")
        return self.hen[nguon][1] > 0 and {"cron": self.cron, "at": ten in self.at, "launchd": ten in self.launchd,
                                           "khac": True}[loai]

    def _trong(self, *p: str) -> bool:
        return all(Path(x).resolve().is_relative_to(self.tam) for x in p)

    def chay(self, argv, **kw):
        self.goi.append(list(argv))
        b = list(self.pk.boc)
        duoi, x = (True, argv[len(b):]) if argv[:len(b)] == b else (False, list(argv))
        ma, ra, loi = self._lam(x, duoi)
        return subprocess.CompletedProcess(argv, ma, ra, loi)

    def _that(self, x: list[str]):
        r = subprocess.run(x, capture_output=True, text=True, timeout=30)
        return r.returncode, r.stdout, r.stderr

    def _lam(self, x: list[str], duoi: bool):
        l, ten = x[0], self.pk.ten
        if l == "/usr/bin/pkill":
            co, self.song = self.song, (1 if "tai-sinh" in self.hong else 0)
            return (0 if co else 1), "", ""
        if l == "/usr/bin/pgrep":
            assert not duoi, "pgrep phải do trạm tự chạy, không qua sudo"
            self.dem += 1
            for nguon, (n, con) in self.hen.items():
                if self._con(nguon) and self.dem % n == 0:
                    self.song, self.hen[nguon][1] = self.song + 1, con - 1
                    self.khi_chay.get(nguon, lambda: None)()          # job chạy: có thể cài nguồn khác
            return (2, "", "") if "pgrep" in self.hong else ((0 if self.song else 1), "", "")
        if l == "/usr/bin/crontab":
            if "treo" in self.hong:                                     # hộp thoại quyền macOS chặn lệnh
                raise subprocess.TimeoutExpired(x, 30)
            if x[1] == "-r" and "crontab-r" not in self.hong:
                self.cron = False
            if "sudo" in self.hong:
                return 1, "", "sudo: a password is required"
            return (0, "* * * * * x\n", "") if self.cron else (1, "", f"crontab: no crontab for {ten}")
        if l == "/usr/bin/id":
            return (0, f"{self.uid}\n", "") if x[1] == "-u" else (
                0, f"{ten}:********:{self.uid}:20::0:0:tram:{self.nha}:/usr/bin/false\n", "")
        if l in ("/usr/bin/stat", "/bin/ls"):
            return self._that(x)
        if l == "/usr/bin/find" and x[1] == str(self.thu_muc_at):
            return 0, "".join(f"{self.thu_muc_at}/{j}\n" for j in self.at), ""
        if l == "/usr/bin/find":
            duong = x[1:next(i for i, p in enumerate(x) if p.startswith("-"))]
            assert self._trong(*duong), f"find ngoài tmp_path: {duong}"
            return self._that([str(self.uid) if p == ten else p for p in x])
        if l == "/usr/bin/atq":
            return 0, "Date\t\t\t\tOwner\t\tQueue\tJob#\n" + "".join(
                f"Thu Oct 16 12:00:00 2026\t{ten}\ta\t{j}\n" for j in self.at), ""
        if l == "/usr/bin/atrm":
            self.at = [] if "atrm" not in self.hong else self.at
            return 0, "", ""
        if l == "/bin/launchctl":
            return self._launchctl(x[1:])
        if l == "/usr/bin/getconf":
            return 0, f"{self.he[x[1]]}/\n", ""
        if l == "/bin/rm":
            assert self._trong(*[p for p in x[2:] if p != "--"]), "rm ngoài tmp_path"
            return self._that(x)
        raise AssertionError(f"lệnh lạ trong don_sach: {x}")

    def _launchctl(self, x: list[str]):
        if x[0] == "bootout":
            if "bootout" not in self.hong:
                self.launchd.discard(x[1].rsplit("/", 1)[1])
            return 0, "", ""
        if x[1].startswith("gui/"):
            return (0, "gui", "") if self.gui else (113, "", f"Could not find domain for {x[1]}")
        if x[1].count("/") == 2:                                        # print user/<uid>/<nhãn>
            n = x[1].rsplit("/", 1)[1]
            ct = self.chuong_trinh.get(n, f"/Users/Shared/{n}")
            return 0, f"{x[1]} = {{\n\tpath = /System/Library/LaunchAgents/{n}.plist\n\tprogram = {ct}\n}}\n", ""
        if "dinh-dang" in self.hong:
            return 0, f"{x[1]} = {{\n\tservices (3) = {{\n\t}}\n}}\n", ""
        dong = "".join(f"\t\t       0      - \t{n}\n" for n in sorted(self.launchd))
        return 0, f"{x[1]} = {{\n\ttype = user\n\tservices = {{\n{dong}\t}}\n}}\n", ""
```

`tests/test_don_tram_kiem.py` (mới):

```python
"""`don_sach` của `tram-kiem` (lát 3c, C01 review đợt 5): `pgrep` rỗng KHÔNG đủ — lịch cron/at/launchd hẹn sau thời
điểm đếm phải được gỡ và XÁC NHẬN, và lần kiểm có lịch thì không được công nhận; lỗi gỡ lịch, định dạng lạ, nhãn nền
bị thay, thiếu nền, phiên GUI, nhà ghi được, gốc lạ → `LoiBanChep`; tệp cài cắm cho lần sau bị dọn. `TramKiemGia` —
KHÔNG pkill/pgrep/crontab/launchctl/sudo thật."""
import pytest

from tram_kiem_gia import TramKiemGia
from tram.giao_viec.ban_chep import LoiBanChep
from tram.giao_viec.principal_kiem import tu_cach_ly

PK = tu_cach_ly("user:tram-kiem")
XAU = "vn.ke-xau.tai-sinh"


@pytest.fixture
def tk(tmp_path, tram_home_tam):
    he = TramKiemGia(tmp_path / "he", PK)
    he.ghi_nen(tram_home_tam)
    return he


def don(tk, **kw):
    PK.don_sach(goc=tk.goc, chay=tk.chay, ngu=lambda s: None, goc_chung=tk.goc_chung, thu_muc_at=tk.thu_muc_at, **kw)


def vi_tri(tk, *dau: str) -> int:
    return next(i for i, a in enumerate(tk.goi) if any(a[j:j + len(dau)] == list(dau) for j in range(len(a))))


def test_sach_thi_tra_ve_launchd_truoc_tram_tu_quan_sat(tk):
    don(tk)
    tram_tu = [a for a in tk.goi if a[0] != "/usr/bin/sudo"]
    assert {a[0] for a in tram_tu} == {"/usr/bin/pgrep", "/usr/bin/id", "/usr/bin/stat", "/usr/bin/find", "/bin/ls"}
    assert all(a[:5] == ["/usr/bin/sudo", "-n", "-H", "-u", "tram-kiem"] for a in tk.goi if a not in tram_tu)
    assert vi_tri(tk, "/bin/launchctl", "print") < vi_tri(tk, "/usr/bin/crontab", "-l")
    assert tk.goi[-1][0] == "/usr/bin/pgrep"
    assert len([a for a in tk.goi if a[-3:-1] == ["-KILL", "-U"]]) == 4         # hai lượt sạch × (trước, sau gỡ lịch)


@pytest.mark.parametrize("nguon", ["cron", "at:7", f"launchd:{XAU}"])
def test_pgrep_rong_nhung_con_lich_hen_tre_thi_go_va_khong_cong_nhan(tk, nguon):
    tk.cron, tk.at = nguon == "cron", ["7"] if nguon == "at:7" else []
    tk.launchd.add(XAU) if nguon.startswith("launchd") else None
    tk.hen[nguon] = [9, 99]                                            # chưa tới giờ lúc pgrep đầu tiên
    with pytest.raises(LoiBanChep, match="đã gỡ"):
        don(tk)
    assert not (tk.cron or tk.at or XAU in tk.launchd)
    don(tk)                                                            # vòng sau: sạch thật mới chạy
    for _ in range(30):                                                # "thời gian trôi": lịch không còn để sinh
        tk.chay(["/usr/bin/pgrep", "-U", "tram-kiem"])
    assert tk.song == 0


def test_job_cai_lai_nguon_khac_khi_dang_quet_van_bi_bat(tk):
    tk.launchd.add(XAU)
    tk.hen[f"launchd:{XAU}"], tk.khi_chay[f"launchd:{XAU}"] = [2, 1], lambda: setattr(tk, "cron", True)
    with pytest.raises(LoiBanChep, match="đã gỡ"):
        don(tk)
    assert not tk.cron and XAU not in tk.launchd


def test_nhan_nen_bi_thay_chuong_trinh_la_dich_vu_la(tk):
    tk.chuong_trinh["com.apple.trustd.agent"] = "/Users/Shared/xau"     # bootout nhãn Apple rồi submit cùng nhãn
    with pytest.raises(LoiBanChep, match="đã gỡ"):
        don(tk)
    assert "com.apple.trustd.agent" not in tk.launchd


@pytest.mark.parametrize("hong, khop", [("crontab-r", "crontab"), ("sudo", "crontab"), ("atrm", "at"),
                                        ("bootout", "launchd"), ("pgrep", "pgrep"), ("treo", "quá hạn"),
                                        ("dinh-dang", "định dạng")])
def test_khong_go_hoac_khong_xac_nhan_duoc_lich_thi_nem(tk, hong, khop):
    tk.cron, tk.at, tk.hong = True, ["7"], {hong}
    tk.launchd.add(XAU)
    with pytest.raises(LoiBanChep, match=khop):
        don(tk)


def test_tien_trinh_sinh_giua_luot_thi_lam_lai(tk):
    tk.hen["khac"] = [3, 1]                                            # sinh đúng một lần, giữa hai lần pgrep
    don(tk)
    assert len([a for a in tk.goi if a[-3:-1] == ["-KILL", "-U"]]) == 6 and tk.song == 0


def test_tai_sinh_lien_tuc_thi_nem(tk):
    tk.song, tk.hong = 1, {"tai-sinh"}
    with pytest.raises(LoiBanChep, match="chưa sạch"):
        don(tk)


@pytest.mark.parametrize("sai", ["thieu-nen", "gui", "nha-ghi-duoc", "goc-symlink"])
def test_thieu_nen_gui_nha_ghi_duoc_hoac_goc_la_thi_nem(tk, tram_home_tam, sai):
    if sai == "thieu-nen":
        (tram_home_tam / "kiem-lai" / "nen-launchd.txt").unlink()
    tk.gui = sai == "gui"
    tk.nha = str(tk.tam) if sai == "nha-ghi-duoc" else tk.nha            # thư mục của user đang test, không phải root
    if sai == "goc-symlink":
        (tk.tam / "that").mkdir()
        tk.goc.rmdir()
        tk.goc.symlink_to(tk.tam / "that")
    with pytest.raises(LoiBanChep):
        don(tk)


def test_ngap_job_keepalive_van_bi_go_truoc_khi_dem(tk):
    tk.song, tk.hong = 1, {"tai-sinh"}                                 # luôn có tiến trình sống khi đếm
    tk.launchd.add(XAU)
    with pytest.raises(LoiBanChep, match="chưa sạch"):
        don(tk)
    assert XAU not in tk.launchd                                       # bootout vẫn chạy dù pgrep không bao giờ rỗng


def test_nen_sai_dinh_dang_thi_nem(tk, tram_home_tam):
    (tram_home_tam / "kiem-lai" / "nen-launchd.txt").write_text("com.apple.trustd.agent\n")    # nền kiểu cũ
    with pytest.raises(LoiBanChep, match="sai định dạng"):
        don(tk)
```

`tests/test_don_tep_tram_kiem.py` (mới):

```python
"""`don_sach` của `tram-kiem` — phần tệp (lát 3c, C01): gốc bản chép phải rỗng, mục của `tram-kiem` trong thư mục
ghi-chung và thư mục tạm/cache riêng bị xoá (lần kiểm sau không đọc được thứ lần trước cài cắm); xoá không được → ném.
`TramKiemGia` — `find`/`rm` thật chỉ trong tmp_path, KHÔNG sudo thật."""
import os

import pytest

from test_don_tram_kiem import don, tk  # noqa: F401 — fixture `tk` dùng chung
from tram.giao_viec.ban_chep import LoiBanChep


def test_tep_cai_cam_cho_lan_kiem_sau_bi_don_goc_rong(tk):
    tk.goc = tk.goc_chung[1] / "tram-kiem"                             # gốc nằm trong thư mục ghi-chung: không bị xoá
    tk.goc.mkdir(mode=0o755)
    he = tk.he.values()
    for p in (tk.goc / "g-1-ab" / "x", tk.goc / "g-1-ab.nha" / ".npmrc", tk.goc_chung[0] / "jest_0" / "cache",
              tk.goc_chung[1] / "z", *(d / "clang" / "m" for d in he)):
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("cài cắm")
    don(tk)
    assert os.listdir(tk.goc) == [] and os.listdir(tk.goc_chung[0]) == [] and all(os.listdir(d) == [] for d in he)
    assert os.listdir(tk.goc_chung[1]) == ["tram-kiem"]


def test_tep_khong_xoa_duoc_thi_nem(tk):
    khoa = tk.goc / "khoa"
    (khoa / "x").parent.mkdir()
    (khoa / "x").write_text("x")
    khoa.chmod(0o500)
    try:
        with pytest.raises(LoiBanChep, match="không dọn được"):
            don(tk)
    finally:
        khoa.chmod(0o700)
```

`tests/test_ban_chep_nha.py` (mới):

```python
"""C01 (lát 3c): lệnh kiểm chạy với HOME + TMPDIR MỚI mỗi lần (`<bản chép>.nha`), dọn cùng bản chép — lần kiểm sau
không đọc được `~/.npmrc`, cache… mà lần trước cài cắm; dọn cuối thấy lịch hẹn giờ → phán quyết "lich-hen-gio"
(không thử lại mãi). `boc` đồng nhất, `git`/`tar`/`rm` THẬT trong `tmp_path`, `don_sach` giả."""
from test_kiem_lai_principal import ban_chep, chay, m  # noqa: F401 — fixture `m` dùng chung

KIEM = ('case "$HOME" in */kiem-ngoai/g-1-*.nha) ;; *) exit 1;; esac; test "$TMPDIR" = "$HOME/tmp/" && '
        'test -d "$TMPDIR" && test ! -e "$HOME/.npmrc" && echo "script-shell=/tmp/xau" > "$HOME/.npmrc"\n')


def test_moi_lan_kiem_co_nha_moi_va_nha_duoc_don(m):
    assert chay(m, {"kiem.sh": KIEM}).dat and ban_chep(m) == []
    assert chay(m, {"kiem.sh": KIEM, "lan2.txt": "x"}).dat and ban_chep(m) == []      # lần 2 không thấy .npmrc cũ


def test_lich_hen_gio_luc_don_cuoi_thi_co_phan_quyet_khong_thu_lai_mai(m):
    from tram.giao_viec.ban_chep import CoLichHenGio
    lan = []

    def don_sach():
        lan.append(1)
        if len(lan) == 2:                                              # commit đã cài lịch: dọn cuối gỡ được rồi ném
            raise CoLichHenGio("tram-kiem có lịch hẹn giờ (đã gỡ)")
    kq = chay(m, {"kiem.sh": "exit 0\n"}, don_sach=don_sach)
    assert (kq.dat, kq.loi) == (False, "lich-hen-gio") and ban_chep(m) == []
```

`tests/test_principal_kiem_hop_nhat.py`, `tests/test_kiem_lai_principal.py`, `tests/test_tick_hai_pha.py`, `tests/test_noi_giao_viec.py`, `tests/test_giao_kiem.py` (sửa — bản vá):

```diff
diff --git a/tests/test_giao_kiem.py b/tests/test_giao_kiem.py
index 896dabf..3211883 100644
--- a/tests/test_giao_kiem.py
+++ b/tests/test_giao_kiem.py
@@ -7,6 +7,7 @@ from pathlib import Path
 import pytest
 
 from kho_kiem_gia import dung_kho
+from tram_kiem_gia import dung_tk
 from tram.cau_hinh.du_an import DuAn, MoiTruongKiem
 from tram.cau_hinh.giao_viec import CauHinhGiaoViec
 from tram.cli import main
@@ -18,13 +19,26 @@ from tram.kiem.chay_lenh import KetQuaLenh
 from tram.tho.kiem_may import in_ket_qua
 
 PK = PrincipalKiem("tram-kiem", ("/usr/bin/sudo", "-n", "-u", "tram-kiem", "--"))
+DON = ("/usr/bin/pkill", "/usr/bin/pgrep", "/usr/bin/crontab", "/usr/bin/atq", "/bin/launchctl", "/usr/bin/getconf",
+       "/usr/bin/stat", "/usr/bin/find", "/bin/ls", "/usr/bin/atrm")
+
+
+@pytest.fixture
+def tk(tmp_path, tram_home_tam, monkeypatch):
+    return dung_tk(tmp_path, tram_home_tam, monkeypatch, PK)
 
 
 def chay_gia(ten="tram-kiem", env="APP_ENV=testing\nPATH=/usr/bin", doc_duoc=False, ghi_duoc=True, pgrep=1,
-             sudo_l="    (ALL) ALL\n    (tram-kiem) NOPASSWD: SETENV: ALL\n"):
-    """`sudo -u tram-kiem` giả: mkdir/touch/rm chạy THẬT dưới user đang test (trong tmp_path) khi `ghi_duoc`."""
+             sudo_l="    (ALL) ALL\n    (tram-kiem) NOPASSWD: SETENV: ALL\n", tk=None):
+    """`sudo -u tram-kiem` giả: mkdir/touch/rm chạy THẬT dưới user đang test (trong tmp_path) khi `ghi_duoc`; lệnh của
+    `don_sach` (C01) do `TramKiemGia` trả lời."""
+    if tk is not None and pgrep == 0:
+        tk.song, tk.hong = 1, {"tai-sinh"}
+
     def chay(argv, **kw):
         lenh = argv[len(PK.boc):] if argv[:len(PK.boc)] == list(PK.boc) else argv
+        if tk is not None and (lenh[0] in DON or lenh[:2] in (["/usr/bin/id", "-u"], ["/usr/bin/id", "-P"])):
+            return tk.chay(argv)
         if lenh[0] in ("/bin/mkdir", "/usr/bin/touch", "/bin/rm"):
             return subprocess.run(lenh if ghi_duoc else ["/usr/bin/false"], capture_output=True, text=True)
         ra = {"/usr/bin/id": (0, ten), "/usr/bin/env": (0, env), "/bin/test": (0 if doc_duoc else 1, ""),
@@ -51,15 +65,15 @@ def test_thieu_het_thi_do(tmp_path):
     assert in_ket_qua(ds)[1] == 1
 
 
-def test_principal_dat_moi_muc(tmp_path):
+def test_principal_dat_moi_muc(tmp_path, tk):
     (tmp_path / "quyen").mkdir()
     for v in ("coder", "qc"):
         (tmp_path / "quyen" / f"{v}.json").write_text("{}")
-    cg = CauHinhGiaoViec(bat=True, thu_muc_kiem=tmp_path, principal_kiem=PK)
-    ds = kiem_giao_viec(cg, [], goc_quyen=tmp_path / "quyen", chay=chay_gia(), chay_lenh=dung_lenh(), toi="hung",
+    cg = CauHinhGiaoViec(bat=True, thu_muc_kiem=tk.goc, principal_kiem=PK)
+    ds = kiem_giao_viec(cg, [], goc_quyen=tmp_path / "quyen", chay=chay_gia(tk=tk), chay_lenh=dung_lenh(), toi="hung",
                         uid_cua=lambda ten: os.getuid())
     assert set(muc(ds).values()) == {"xanh"} and in_ket_qua(ds)[1] == 0
-    assert not list(tmp_path.glob("tram-giao-kiem-thu*"))
+    assert list(tk.goc.iterdir()) == [] and tk.goi                    # don_sach thật đã chạy, gốc sạch
 
 
 @pytest.mark.parametrize("sai, muc_do", [
@@ -67,9 +81,9 @@ def test_principal_dat_moi_muc(tmp_path):
     ({"doc_duoc": True}, "principal: không đọc kho trạm"), ({"ghi_duoc": False}, "principal: ghi bản chép kiểm"),
     ({"pgrep": 0}, "principal: ghi bản chép kiểm"),
     ({"sudo_l": "    (root) NOPASSWD: /usr/local/x\n"}, "principal: sudoers không NOPASSWD root")])
-def test_principal_sai_tung_muc_la_do(tmp_path, sai, muc_do):
-    m = muc(kiem_giao_viec(CauHinhGiaoViec(thu_muc_kiem=tmp_path, principal_kiem=PK), [], goc_quyen=tmp_path,
-                           chay=chay_gia(**sai), chay_lenh=dung_lenh(), toi="hung"))
+def test_principal_sai_tung_muc_la_do(tmp_path, tk, sai, muc_do):
+    m = muc(kiem_giao_viec(CauHinhGiaoViec(thu_muc_kiem=tk.goc, principal_kiem=PK), [], goc_quyen=tmp_path,
+                           chay=chay_gia(**sai, tk=tk), chay_lenh=dung_lenh(), toi="hung"))
     assert m[muc_do] == "do" and m["principal: dừng được lệnh quá hạn"] == "xanh"
 
 
diff --git a/tests/test_kiem_lai_principal.py b/tests/test_kiem_lai_principal.py
index 0896674..385058c 100644
--- a/tests/test_kiem_lai_principal.py
+++ b/tests/test_kiem_lai_principal.py
@@ -42,7 +42,7 @@ def test_don_sach_truoc_khi_chep_va_truoc_khi_don(m):
         thay.append([(p.name.startswith("g-1-"), (p / "DA_CHAY").exists()) for p in ban_chep(m)])
 
     kq = chay(m, {"kiem.sh": "touch DA_CHAY\n"}, don_sach=don_sach)
-    assert kq.dat and thay == [[], [(True, True)]] and ban_chep(m) == []
+    assert kq.dat and thay == [[], [(True, True), (True, False)]] and ban_chep(m) == []   # bản chép + `.nha` (C01)
 
 
 def test_con_tien_trinh_tram_kiem_thi_khong_chep_khong_chay(m):
diff --git a/tests/test_noi_giao_viec.py b/tests/test_noi_giao_viec.py
index adac405..9f4898a 100644
--- a/tests/test_noi_giao_viec.py
+++ b/tests/test_noi_giao_viec.py
@@ -63,7 +63,8 @@ def test_dung_bo_that_noi_principal_va_bo_qua_du_an_hong(tmp_path, capsys):
     cg = CauHinhGiaoViec(bat=True, thu_muc_kiem=tmp_path / "k", principal_kiem=PK)
     bo = dung_bo_that(cg, tao_pt(tmp_path, {}).cau_hinh, thu_muc_du_an=tmp_path / "du-an")
     assert [d.ten for d in bo.cac_du_an()] == ["hr-x"] and "bỏ qua dự án hong" in capsys.readouterr().err
-    assert bo.boc(["sh", "kiem.sh"]) == [*PK.boc, "sh", "kiem.sh"] and bo.don_sach == PK.don_sach
+    assert bo.boc(["sh", "kiem.sh"]) == [*PK.boc, "sh", "kiem.sh"] and bo.don_sach.func == PK.don_sach
+    assert bo.don_sach.keywords == {"goc": tmp_path / "k"}                       # C01: don_sach dọn cả gốc bản chép
     assert bo.kill == PK.kill_nhom
     assert bo.thu_muc_kiem == tmp_path / "k" and bo.doc_beads is None
     assert bo.tao_bd(bo.cac_du_an()[0]).actor == "tram/giao-viec" and Path(bo.tao_bd(bo.cac_du_an()[0]).repo) == tmp_path
diff --git a/tests/test_principal_kiem_hop_nhat.py b/tests/test_principal_kiem_hop_nhat.py
index 93522a1..6cc41fe 100644
--- a/tests/test_principal_kiem_hop_nhat.py
+++ b/tests/test_principal_kiem_hop_nhat.py
@@ -2,10 +2,10 @@
 `giao_viec.principal_kiem` chỉ để đối chiếu. D22: không trao/thu quyền — `don_sach` giết tiến trình dưới tram-kiem, trạm
 tự đếm bằng pgrep. Không sudo — chỉ kiểm argv dựng ra, `chay` giả."""
 import fnmatch
-from types import SimpleNamespace
 
 import pytest
 
+from tram_kiem_gia import TramKiemGia
 from tram.cau_hinh.giao_viec import nap_cau_hinh_giao_viec
 from tram.cau_hinh.principal_kiem import doc_principal_kiem
 from tram.giao_viec.ban_chep import LoiBanChep
@@ -71,36 +71,42 @@ def test_thu_muc_kiem_symlink_bi_tu_choi(tram_home_tam, tmp_path):
         nap_cau_hinh_giao_viec()
 
 
-def chay_gia(pgrep: list[int]):
-    goi = []
+def don(pk, tk, **kw):
+    tk.ghi_nen(tk.tram_home)
+    pk.don_sach(goc=tk.goc, chay=tk.chay, ngu=lambda s: None, goc_chung=tk.goc_chung, thu_muc_at=tk.thu_muc_at, **kw)
 
-    def chay(argv, **kw):
-        goi.append(argv)
-        return SimpleNamespace(returncode=pgrep.pop(0) if argv[0] == "/usr/bin/pgrep" else 1)
-    return goi, chay
 
-
-def test_don_sach_giet_duoi_tram_kiem_roi_tram_tu_dem():
-    pk, (goi, chay) = tu_cach_ly("user:tram-kiem"), chay_gia([0, 1])
-    pk.don_sach(chay=chay, ngu=lambda s: None)
-    assert goi[:3] == [pk.boc_lenh(["/usr/bin/crontab", "-r"]), pk.boc_lenh(["/usr/bin/pkill", "-KILL", "-U",
-                                                                             "tram-kiem"]),
-                       ["/usr/bin/pgrep", "-U", "tram-kiem"]] and len(goi) == 6     # pgrep KHÔNG qua sudo
+def test_don_sach_giet_duoi_tram_kiem_roi_tram_tu_dem(tmp_path, tram_home_tam):
+    pk = tu_cach_ly("user:tram-kiem")
+    tk = TramKiemGia(tmp_path / "he", pk)
+    tk.tram_home = tram_home_tam
+    don(pk, tk)
+    assert tk.goi[1:3] == [pk.boc_lenh(["/usr/bin/pkill", "-KILL", "-U", "tram-kiem"]),
+                           pk.boc_lenh(["/usr/bin/pkill", "-KILL", "-u", "tram-kiem"])]
+    assert [a for a in tk.goi if "/usr/bin/pgrep" in a][:2] == [["/usr/bin/pgrep", "-U", "tram-kiem"],
+                                                                 ["/usr/bin/pgrep", "-u", "tram-kiem"]]   # không sudo
 
 
-@pytest.mark.parametrize("pgrep, khop", [([0] * 5, "vẫn còn"), ([2], "pgrep")])
-def test_tai_sinh_hoac_pgrep_loi_thi_nem(pgrep, khop):
+@pytest.mark.parametrize("hong, khop", [("tai-sinh", "chưa sạch"), ("pgrep", "pgrep")])
+def test_tai_sinh_hoac_pgrep_loi_thi_nem(tmp_path, tram_home_tam, hong, khop):
+    pk = tu_cach_ly("user:tram-kiem")
+    tk = TramKiemGia(tmp_path / "he", pk)
+    tk.tram_home = tram_home_tam
+    tk.song, tk.hong = 1, {hong}
     with pytest.raises(LoiBanChep, match=khop):
-        tu_cach_ly("user:tram-kiem").don_sach(chay=chay_gia(pgrep)[1], ngu=lambda s: None)
+        don(pk, tk)
 
 
 @pytest.mark.parametrize("co_che", ["user", "sandbox"])
-def test_moi_argv_duoi_tram_kiem_khop_sudoers(co_che):
-    pk, (goi, chay) = tu_cach_ly(f"{co_che}:tram-kiem"), chay_gia([1])
-    pk.don_sach(chay=chay)
+def test_moi_argv_duoi_tram_kiem_khop_sudoers(co_che, tmp_path, tram_home_tam):
+    pk = tu_cach_ly(f"{co_che}:tram-kiem")
+    tk = TramKiemGia(tmp_path / "he", pk)
+    tk.tram_home = tram_home_tam
+    don(pk, tk)
+    goi = tk.goi
     pk.kill_nhom(123, 9, chay=lambda argv, **kw: goi.append(argv))
     mau = dong_sudoers_kiem(tram="hung", tram_kiem="tram-kiem", co_che=co_che).split("NOPASSWD:SETENV: ", 1)[1]
     goi.append(pk.boc_lenh(["/usr/bin/tar", "-x", "-f", "-", "-C", "/k/g-1"]))
-    qua_sudo = [a for a in goi if a[0] != "/usr/bin/pgrep"]
-    assert all(a[:5] == ["/usr/bin/sudo", "-n", "-H", "-u", "tram-kiem"] for a in qua_sudo) and len(qua_sudo) == 4
+    qua_sudo = [a for a in goi if a[0] == "/usr/bin/sudo"]
+    assert all(a[:5] == ["/usr/bin/sudo", "-n", "-H", "-u", "tram-kiem"] for a in qua_sudo) and len(qua_sudo) > 10
     assert all(mau == "ALL" or fnmatch.fnmatchcase(" ".join(a[a.index("--") + 1:]), mau) for a in qua_sudo)
diff --git a/tests/test_tick_hai_pha.py b/tests/test_tick_hai_pha.py
index 1eebb44..81ded31 100644
--- a/tests/test_tick_hai_pha.py
+++ b/tests/test_tick_hai_pha.py
@@ -64,8 +64,9 @@ def test_kiem_lai_dung_thu_muc_va_don_sach_cua_bo(tmp_path):
     don = []
     t.bo.thu_muc_kiem, t.bo.don_sach = goc, lambda: don.append([p.name for p in goc.glob("*")])
     chuan_bi_code_xong(t, {"src/tom_tat.py": "x = 2\n", F: "x", "kiem.sh": "exit 0\n"})
-    assert vong_git(t.bo)["kiem_lai"] == 1 and don[0] == [] and len(don[1]) == 1
-    assert don[1][0].startswith(loai(t, "giao.nhan")[0].du_lieu["giao_id"] + "-") and list(goc.iterdir()) == []
+    assert vong_git(t.bo)["kiem_lai"] == 1 and don[0] == [] and len(don[1]) == 2          # bản chép + `.nha` (C01)
+    assert all(x.startswith(loai(t, "giao.nhan")[0].du_lieu["giao_id"] + "-") for x in don[1])
+    assert list(goc.iterdir()) == []
 
 
 def test_cot_3_nhanh_bi_day_ngoai_luong(tmp_path):
```


`tests/test_don_tep_loi_lenh.py` (mới — T11 review đợt 6, 3 ca; hoàn toàn runner giả):

```python
import subprocess
from types import SimpleNamespace

import pytest
from tram.giao_viec import don_tram_kiem as dtk
from tram.giao_viec.ban_chep import LoiBanChep


@pytest.mark.parametrize("hong", ["getconf", "xoa", "xac-nhan"])
def test_lenh_loi_stdout_rong_khong_duoc_coi_la_da_don(monkeypatch, hong):
    monkeypatch.setattr(dtk, "_sot", lambda *a: [])
    pk = SimpleNamespace(ten="tram-kiem", boc_lenh=lambda a: a)

    def chay(argv, **kw):
        buoc = "getconf" if argv[0] == "/usr/bin/getconf" else ("xoa" if "-exec" in argv else "xac-nhan")
        # getconf vẫn có đường dẫn hợp lệ dù mã lỗi; find lỗi có stdout rỗng.
        ra = "/private/var/folders/test/cache/" if buoc == "getconf" else ""
        return subprocess.CompletedProcess(argv, 1 if buoc == hong else 0, ra, "")

    with pytest.raises(LoiBanChep):
        dtk.don_tep(pk, None, chay, ())
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_don_tep_loi_lenh.py tests/test_don_tram_kiem.py tests/test_don_tep_tram_kiem.py tests/test_ban_chep_nha.py tests/test_principal_kiem_hop_nhat.py tests/test_kiem_lai_principal.py tests/test_tick_hai_pha.py tests/test_noi_giao_viec.py tests/test_giao_kiem.py -q`
Expected sau review: phải fail trước sửa; chưa chạy bộ +3 ca. Lịch sử r47: `10 failed, 28 passed, 30 errors in 6.25s` (kết quả tác giả trên bản sao: lỗi chủ yếu `ModuleNotFoundError: No module named 'tram.giao_viec.launchd_kiem'` trong fixture `TramKiemGia.ghi_nen`/`dung_tk`; `test_ban_chep_nha.py` fail vì HOME còn là nhà cũ và chưa có `CoLichHenGio`; `test_kiem_lai_principal`/`test_tick_hai_pha` fail vì chưa có `<bản chép>.nha`; `test_noi_giao_viec` fail vì `don_sach` chưa là `partial`)

- [ ] **Step 3: Viết mã**

`tram/giao_viec/lich_tram_kiem.py` (mới):

```python
"""Nguồn tái sinh THEO LỊCH của `tram-kiem`: cron và at (lát 3c, C01 review đợt 5; launchd ở `launchd_kiem.py`). `pgrep`
rỗng chỉ là ảnh chụp tiến trình, không chứng minh không còn tác vụ hẹn giờ. Gọi khi ĐÃ không còn tiến trình nào của
`tram-kiem` — mọi lệnh dưới `tram-kiem` ở đây là binary hệ thống, không có mã agent nào đang chạy để giả kết quả.
Không root lúc chạy (D22). Mỗi hàm trả True khi ĐÃ PHẢI GỠ thứ gì (người gọi coi đó là dấu hiệu bẩn):
- cron: `crontab -l` dưới `tram-kiem` (có thì `crontab -r` rồi đọc lại) PHẢI báo "no crontab for"; mã 0 hay lỗi khác
  (sudo hỏng, bị cấm, treo vì hộp thoại quyền…) → `LoiBanChep` — không lấy mã của lệnh gỡ làm bằng chứng đã sạch;
- at: trạm tự liệt kê `/usr/lib/cron/jobs` (đọc được, không sudo) tìm file của `tram-kiem`, và `atq` dưới `tram-kiem`;
  có → `atrm`, kiểm lại cả hai, còn → `LoiBanChep`.
Định dạng thông báo/đầu ra của `crontab`, `atq` và chủ file việc `at` là của macOS 15 — S6 đo lại trên máy B."""
import subprocess
from collections.abc import Callable
from pathlib import Path

from tram.giao_viec.ban_chep import LoiBanChep

CRONTAB, ATQ, ATRM, FIND = "/usr/bin/crontab", "/usr/bin/atq", "/usr/bin/atrm", "/usr/bin/find"
VIEC_AT = Path("/usr/lib/cron/jobs")


def ra(chay: Callable, argv: list[str]) -> subprocess.CompletedProcess:
    try:
        return chay(argv, capture_output=True, text=True, timeout=30)
    except subprocess.TimeoutExpired:
        raise LoiBanChep(f"{' '.join(argv)[-80:]} quá hạn 30 s — không xác nhận được (S6: hộp thoại quyền?)") from None


def don_cron(pk, chay: Callable) -> bool:
    """Đọc trước; chỉ `crontab -r` khi có crontab (sửa crontab trên macOS có thể bật hộp thoại quyền — S6 đo)."""
    r = ra(chay, pk.boc_lenh([CRONTAB, "-l"]))
    co = r.returncode == 0
    if co:
        ra(chay, pk.boc_lenh([CRONTAB, "-r"]))
        r = ra(chay, pk.boc_lenh([CRONTAB, "-l"]))
    if r.returncode == 0 or "no crontab for" not in (r.stdout + r.stderr):
        raise LoiBanChep(f"crontab của {pk.ten} chưa xác nhận rỗng (crontab -l mã {r.returncode}) — dừng kiểm lại")
    return co


def _viec_at(pk, chay: Callable, thu_muc: Path) -> tuple[list[str], list[str]]:
    r = ra(chay, [FIND, str(thu_muc), "-mindepth", "1", "-user", pk.ten, "-print"])
    q = ra(chay, pk.boc_lenh([ATQ]))
    if r.returncode or q.returncode:
        raise LoiBanChep(f"không liệt kê được việc at ({thu_muc} mã {r.returncode}, atq mã {q.returncode})")
    return r.stdout.split(), [c[-1] for c in map(str.split, q.stdout.splitlines()) if c and c[-1].isdigit()]


def don_at(pk, chay: Callable, thu_muc: Path = VIEC_AT) -> bool:
    tep, so = _viec_at(pk, chay, thu_muc)
    if not (tep or so):
        return False
    if so:
        ra(chay, pk.boc_lenh([ATRM, *so]))
    if any(_viec_at(pk, chay, thu_muc)):
        raise LoiBanChep(f"{pk.ten} còn việc `at` hẹn giờ sau atrm — dừng kiểm lại")
    return True
```

`tram/giao_viec/launchd_kiem.py` (mới):

```python
"""Dịch vụ launchd trong miền `user/<uid>` của `tram-kiem` (lát 3c, C01 review đợt 5). User khác không đọc được miền
này (đã đo: "Operation not permitted") → lệnh chạy DƯỚI `tram-kiem` (binary hệ thống, kết quả do launchd trả). NỀN
(`~/.tram/kiem-lai/nen-launchd.txt`, `tram giao chup-nen-lich`): dòng `nhãn<TAB>vân tay`, vân tay = sha256 các dòng
`path =`, `program =`, khối `arguments`/`environment` của `launchctl print user/<uid>/<nhãn>` — nhãn nền bị chiếm bằng
job khác là LẠ. Lạ → `bootout`, in lại; còn → `LoiBanChep`. Định dạng lệch, nền sai dạng/thiếu, miền `gui/<uid>` có
thật, lỗi khác "Could not find domain" → `LoiBanChep`: không đoán."""
import hashlib
from collections.abc import Callable
from pathlib import Path

from tram.duong_dan import tram_home
from tram.giao_viec.ban_chep import LoiBanChep
from tram.giao_viec.lich_tram_kiem import ra

LAUNCHCTL = "/bin/launchctl"
KHONG_MIEN = "could not find domain"


def nen_mac_dinh() -> Path:
    return tram_home() / "kiem-lai" / "nen-launchd.txt"


def doc_nen(p: Path | None = None) -> dict[str, str]:
    p = p or nen_mac_dinh()
    if not p.is_file():
        raise LoiBanChep(f"chưa có nền launchd của tram-kiem ({p}) — chạy `tram giao chup-nen-lich` ngay sau khi cài")
    dong = [d.split("\t") for d in p.read_text(encoding="utf-8").splitlines() if d.strip()]
    if any(len(d) != 2 or len(d[1]) != 64 for d in dong):
        raise LoiBanChep(f"nền {p} sai định dạng (cần `nhãn<TAB>vân tay`) — `tram giao chup-nen-lich --ghi-de`")
    return dict(dong)


def nhan_launchd(van_ban: str) -> set[str]:
    """Nhãn trong khối `services = { … }` (cột cuối mỗi dòng). Thiếu đầu hoặc cuối khối → `LoiBanChep`."""
    dong = [d.strip() for d in van_ban.splitlines()]
    if "services = {" not in dong:
        raise LoiBanChep("launchctl print: không thấy khối `services = {` — định dạng lạ, không đoán")
    khoi = dong[dong.index("services = {") + 1:]
    if "}" not in khoi:
        raise LoiBanChep("launchctl print: khối services không đóng — định dạng lạ, không đoán")
    return {d.split()[-1] for d in khoi[:khoi.index("}")] if d}


def in_mien(pk, chay: Callable, uid: int) -> set[str]:
    r = ra(chay, pk.boc_lenh([LAUNCHCTL, "print", f"user/{uid}"]))
    if r.returncode == 0:
        return nhan_launchd(r.stdout)
    if KHONG_MIEN in (r.stdout + r.stderr).lower():
        return set()
    raise LoiBanChep(f"launchctl print user/{uid} dưới {pk.ten} lỗi (mã {r.returncode}) — không xác nhận được lịch")


def _doc_dv(pk, chay: Callable, uid: int, nhan: str) -> tuple[str, str]:
    """(vân tay, mô tả chương trình) của một dịch vụ."""
    r = ra(chay, pk.boc_lenh([LAUNCHCTL, "print", f"user/{uid}/{nhan}"]))
    trong, ra_ = False, []
    for d in (d.strip() for d in r.stdout.splitlines()):
        trong = (trong or d in ("arguments = {", "environment = {")) and d != "}"
        if trong or d.startswith(("path = ", "program = ")):
            ra_.append(d)
    ct = [d for d in ra_ if d.startswith(("path = ", "program = "))]
    if r.returncode or not ct:
        raise LoiBanChep(f"không đọc được chương trình của dịch vụ {nhan} (mã {r.returncode}) — không đoán")
    return hashlib.sha256("\n".join(ra_).encode()).hexdigest(), "; ".join(ct)


def van_tay(pk, chay: Callable, uid: int, nhan: str) -> str:
    return _doc_dv(pk, chay, uid, nhan)[0]


def _la(pk, chay: Callable, uid: int, nen: dict[str, str]) -> list[str]:
    return sorted(n for n in in_mien(pk, chay, uid) if nen.get(n) != van_tay(pk, chay, uid, n))


def don_launchd(pk, chay: Callable, uid: int, nen: dict[str, str]) -> bool:
    la = _la(pk, chay, uid, nen)
    for nhan in la:
        ra(chay, pk.boc_lenh([LAUNCHCTL, "bootout", f"user/{uid}/{nhan}"]))
    if la and (con := _la(pk, chay, uid, nen)):
        raise LoiBanChep(f"{pk.ten} còn dịch vụ launchd lạ sau bootout: {', '.join(con)[:200]}")
    g = ra(chay, pk.boc_lenh([LAUNCHCTL, "print", f"gui/{uid}"]))
    if g.returncode == 0 or KHONG_MIEN not in (g.stdout + g.stderr).lower():
        raise LoiBanChep(f"{pk.ten}: miền gui/{uid} có thật hoặc không đọc được (mã {g.returncode}) — dừng kiểm lại")
    return bool(la)


def chup(pk, chay: Callable, uid: int) -> dict[str, tuple[str, str]]:
    return {n: _doc_dv(pk, chay, uid, n) for n in sorted(in_mien(pk, chay, uid))}
```

`tram/giao_viec/don_tram_kiem.py` (mới):

```python
"""`don_sach` của `tram-kiem` (lát 3c, C01 review đợt 5): vòng đời cách ly giữa hai lần kiểm lại, KHÔNG root lúc chạy
(D22 — sudo chỉ sang `tram-kiem`; trạm tự quan sát không qua sudo khi đọc được). Dưới khoá kiểm lại, mỗi lượt quét:
1. giết `pkill -KILL -U/-u` dưới `tram-kiem`; 2. lịch — launchd TRƯỚC (`launchd_kiem.py`), rồi cron, at
(`lich_tram_kiem.py`), làm cả khi còn tiến trình (bootout giết luôn tiến trình của job); 3. giết lại, trạm `pgrep -U/-u`
— còn → lượt sau; 4. nhà trong passwd đúng `/var/empty`, root, không g/o ghi, không ACL; 5. tệp: gốc bản chép (của
`tram-kiem`, không symlink) RỖNG, mục cấp một của `tram-kiem` trong thư mục ghi-chung và nội dung `getconf
DARWIN_USER_*` bị xoá dưới `tram-kiem` (`find … -exec rm`) rồi liệt kê lại; 6. `pgrep` lần cuối.
Chỉ trả về khi HAI lượt liên tiếp sạch (không tiến trình, không phải gỡ lịch) — thu hẹp kẽ hở job tự xoá mình rồi cài
nguồn khác đúng lúc đang quét (rủi ro (a), S6). Đã phải gỡ lịch → gỡ, xác nhận, rồi VẪN ném `CoLichHenGio` (con
`LoiBanChep`): lần kiểm không được công nhận (`kiem_lai` bắt ở bước dọn cuối → lỗi "lich-hen-gio" → escalation).
Không xác nhận được bước nào → `LoiBanChep`."""
import re
import subprocess
import time
from collections.abc import Callable
from pathlib import Path

from tram.giao_viec.ban_chep import CoLichHenGio, LoiBanChep
from tram.giao_viec.kiem_goc import kiem_thu_muc_goc
from tram.giao_viec.launchd_kiem import doc_nen, don_launchd
from tram.giao_viec.lich_tram_kiem import FIND, VIEC_AT, don_at, don_cron, ra

PKILL, PGREP, NHA = "/usr/bin/pkill", "/usr/bin/pgrep", "/var/empty"
GOC_CHUNG = (Path("/private/tmp"), Path("/private/var/tmp"), Path("/Users/Shared"), Path("/Library/Caches"))
THU_MUC_HE = ("DARWIN_USER_DIR", "DARWIN_USER_TEMP_DIR", "DARWIN_USER_CACHE_DIR")


def uid_cua(ten: str, chay: Callable) -> int:
    r = ra(chay, ["/usr/bin/id", "-u", ten])
    if r.returncode or not r.stdout.strip().isdigit():
        raise LoiBanChep(f"không có user {ten} (id -u mã {r.returncode})")
    return int(r.stdout.strip())


def con_tien_trinh(pk, chay: Callable) -> bool:
    ma = [ra(chay, [PGREP, c, pk.ten]).returncode for c in ("-U", "-u")]
    if any(m not in (0, 1) for m in ma):
        raise LoiBanChep(f"pgrep -U/-u {pk.ten} lỗi (mã {ma}) — không xác nhận được đã sạch")
    return 0 in ma


def kiem_nha(pk, chay: Callable) -> None:
    r = ra(chay, ["/usr/bin/id", "-P", pk.ten])
    nha = r.stdout.strip().split(":")[8] if r.returncode == 0 and r.stdout.count(":") >= 9 else ""
    s = ra(chay, ["/usr/bin/stat", "-f", "%u %Lp %HT", "--", NHA]).stdout.split()
    ls = ra(chay, ["/bin/ls", "-lde", "--", NHA]).stdout.splitlines()
    acl = not ls or ls[0].split()[0].endswith("+") or any(re.match(r"\s*\d+: ", d) for d in ls[1:])
    if nha != NHA or len(s) != 3 or s[0] != "0" or s[2] != "Directory" or int(s[1], 8) & 0o022 or acl:
        raise LoiBanChep(f"nhà của {pk.ten} ({nha or '?'}) phải là {NHA} của root, không ai khác ghi được — C01")


def _sot(pk, goc: Path | None, chay: Callable, goc_chung: tuple[Path, ...]) -> list[str]:
    tren = {str(p) for p in ([goc, *goc.parents] if goc else [])}
    r = ra(chay, [FIND, *map(str, goc_chung), "-mindepth", "1", "-maxdepth", "1", "-user", pk.ten, "-print0"])
    g = ra(chay, [FIND, str(goc), "-mindepth", "1", "-maxdepth", "1", "-print0"]) if goc else None
    if r.returncode or (g and g.returncode):
        raise LoiBanChep(f"không liệt kê được tệp của {pk.ten} (find mã {r.returncode})")
    ds = [x for x in r.stdout.split("\0") if x and x not in tren]
    return ds + [x for x in (g.stdout if g else "").split("\0") if x]


def _xoa(pk, chay: Callable, *tim: str) -> None:
    r = ra(chay, pk.boc_lenh([FIND, *tim, "-exec", "/bin/rm", "-rf", "{}", "+"]))
    if r.returncode:
        raise LoiBanChep(f"không dọn được tệp của {pk.ten} (mã {r.returncode})")


def don_tep(pk, goc: Path | None, chay: Callable, goc_chung: tuple[Path, ...] = GOC_CHUNG) -> None:
    if _sot(pk, goc, chay, goc_chung):
        tru = [a for p in ([goc, *goc.parents] if goc else []) for a in ("!", "-path", str(p))]
        _xoa(pk, chay, *map(str, goc_chung), "-mindepth", "1", "-maxdepth", "1", "-user", pk.ten, *tru)
        if goc:
            _xoa(pk, chay, str(goc), "-mindepth", "1", "-maxdepth", "1")
        if (con := _sot(pk, goc, chay, goc_chung)):
            raise LoiBanChep(f"không dọn được tệp của {pk.ten}: {', '.join(con)[:200]}")
    for bien in THU_MUC_HE:
        g = ra(chay, pk.boc_lenh(["/usr/bin/getconf", bien]))
        p = g.stdout.strip().rstrip("/")
        if g.returncode or not p.startswith(("/var/folders/", "/private/var/folders/")):
            raise LoiBanChep(f"không xác nhận được {bien} của {pk.ten} (mã {g.returncode})")
        _xoa(pk, chay, p, "-mindepth", "1", "-maxdepth", "1")
        kq = ra(chay, pk.boc_lenh([FIND, p, "-mindepth", "1", "-print", "-quit"]))
        if kq.returncode or kq.stdout.strip():
            raise LoiBanChep(f"không dọn được {bien} của {pk.ten} (mã {kq.returncode})")


def _luot(pk, goc: Path | None, chay: Callable, uid: int, nen: dict, goc_chung, thu_muc_at) -> tuple[bool, bool]:
    """(sạch tiến trình, đã phải gỡ lịch). Gỡ lịch TRƯỚC khi đếm: hàng trăm job KeepAlive luôn có tiến trình sống
    không được chặn việc gỡ (bootout giết luôn tiến trình của job)."""
    for c in ("-U", "-u"):
        ra(chay, pk.boc_lenh([PKILL, "-KILL", c, pk.ten]))
    go = don_launchd(pk, chay, uid, nen) | don_cron(pk, chay) | don_at(pk, chay, thu_muc_at)
    for c in ("-U", "-u"):
        ra(chay, pk.boc_lenh([PKILL, "-KILL", c, pk.ten]))
    if con_tien_trinh(pk, chay):
        return False, go
    kiem_nha(pk, chay)
    don_tep(pk, goc, chay, goc_chung)
    return not con_tien_trinh(pk, chay), go


def don_sach(pk, goc: Path | None, *, chay: Callable = subprocess.run, lan: int = 6, ngu: Callable = time.sleep,
             nen: Path | None = None, goc_chung: tuple[Path, ...] | None = None, thu_muc_at: Path | None = None
             ) -> None:
    uid, nen_ = uid_cua(pk.ten, chay), doc_nen(nen)
    goc_chung, thu_muc_at = goc_chung or GOC_CHUNG, thu_muc_at or VIEC_AT      # đọc lúc gọi (test thay được)
    if goc is not None and (m := kiem_thu_muc_goc(pk, goc, uid_cua=lambda t: uid)).muc_do != "xanh":
        raise LoiBanChep(f"gốc bản chép không an toàn để dọn: {m.chi_tiet}")
    sach_lien, da_go = 0, False
    for _ in range(lan):
        sach, go = _luot(pk, goc, chay, uid, nen_, goc_chung, thu_muc_at)
        da_go |= go
        sach_lien = sach_lien + 1 if sach and not go else 0
        if sach_lien == 2:
            if da_go:
                raise CoLichHenGio(f"{pk.ten} có lịch hẹn giờ (đã gỡ) — không công nhận lần kiểm này")
            return
        if not sach:
            ngu(0.5)
    raise LoiBanChep(f"{pk.ten} chưa sạch sau {lan} lượt (tiến trình/lịch tái sinh?) — dừng kiểm lại")
```

`tram/giao_viec/principal_kiem.py`, `tram/giao_viec/ban_chep.py`, `tram/giao_viec/kiem_lai.py`, `tram/giao_viec/noi_that.py`, `tram/giao_viec/kiem_san_sang.py` (sửa — bản vá):

```diff
diff --git a/tram/giao_viec/ban_chep.py b/tram/giao_viec/ban_chep.py
index eccbb40..4c0a94c 100644
--- a/tram/giao_viec/ban_chep.py
+++ b/tram/giao_viec/ban_chep.py
@@ -8,7 +8,8 @@ Fail-closed:
 - một lần kiểm lại một lúc trên máy (khoá `~/.tram/kiem-lai.khoa`, không chờ) — lần thứ hai ném `KiemLaiDangBan`;
 - `don_sach` (giết mọi tiến trình `tram-kiem`, xác nhận không còn) chạy trước khi chép và trước khi dọn — lỗi → ném;
 - `tar` hoặc `git init/add/commit` lỗi → ném `LoiBanChep`, không chạy lệnh kiểm;
-- dọn xong mà thư mục vẫn còn → ném `LoiBanChep`: kết quả kiểm lại KHÔNG được trả về."""
+- dọn xong mà thư mục vẫn còn → ném `LoiBanChep`: kết quả kiểm lại KHÔNG được trả về.
+Lệnh kiểm chạy với HOME/TMPDIR MỚI (`<bản chép>.nha`, C01) — không đọc được cấu hình/cache lần trước cài cắm."""
 import fcntl
 import os
 import secrets
@@ -31,6 +32,10 @@ class LoiBanChep(OSError):
     """Không bảo đảm được bản chép sạch — không chạy lệnh, không công nhận kết quả (vòng tick đếm lỗi, thử lại)."""
 
 
+class CoLichHenGio(LoiBanChep):
+    """`don_sach` đã phải gỡ lịch hẹn giờ của `tram-kiem` (C01): máy sạch lại, lần kiểm không được công nhận."""
+
+
 class KiemLaiDangBan(LoiBanChep):
     """Đang có lần kiểm lại khác (hoặc `tram giao kiem`) giữ khoá."""
 
@@ -61,11 +66,22 @@ def _chay(argv: list[str], **kw) -> subprocess.CompletedProcess:
     return subprocess.run(argv, capture_output=True, timeout=THOI_GIAN, **kw)
 
 
+def nha_cua(wt: Path) -> Path:
+    """HOME + TMPDIR MỚI của lần kiểm này (C01), cạnh bản chép, dọn cùng bản chép — không nhà dùng lại giữa các lần."""
+    return wt.with_name(wt.name + ".nha")
+
+
+def boc_nha(boc: Boc, wt: Path) -> Boc:
+    nha = nha_cua(wt)
+    return lambda a: boc(["/usr/bin/env", f"HOME={nha}", f"TMPDIR={nha}/tmp/", *a])
+
+
 def chep_ban(kho: Path, commit: str, wt: Path, *, boc: Boc) -> None:
     """`tram-kiem` tạo `wt` MỚI (đã có → lỗi), tự `tar -x` nội dung đúng commit từ stdin, rồi tự dựng repo git một
     commit (D40) — TRƯỚC khi môi trường kiểm vào cây, nên `.env.testing` không bao giờ thành đối tượng git."""
     _chay(boc(["/bin/mkdir", "-p", str(wt.parent)]), check=True)
     _chay(boc(["/bin/mkdir", str(wt)]), check=True)
+    _chay(boc(["/bin/mkdir", "-m", "0700", str(nha_cua(wt)), str(nha_cua(wt) / "tmp")]), check=True)
     nguon = nguon_archive(kho, commit)
     try:
         nhan = _chay(boc([*TAR_NHAN, str(wt)]), stdin=nguon.stdout)
@@ -100,8 +116,8 @@ def don_ban(wt: Path, *, boc: Boc, don_sach: Callable[[], None] | None = None) -
             don_sach()
         except (OSError, subprocess.SubprocessError) as e:
             loi = e
-    r = _chay(boc(["/bin/rm", "-rf", str(wt)]))
-    if r.returncode or os.path.lexists(wt):
+    r = _chay(boc(["/bin/rm", "-rf", str(wt), str(nha_cua(wt))]))
+    if r.returncode or os.path.lexists(wt) or os.path.lexists(nha_cua(wt)):
         raise LoiBanChep(f"không dọn được bản chép {wt} — không công nhận kết quả") from loi
     if loi is not None:
         raise loi
diff --git a/tram/giao_viec/kiem_lai.py b/tram/giao_viec/kiem_lai.py
index ca7a35f..e04df71 100644
--- a/tram/giao_viec/kiem_lai.py
+++ b/tram/giao_viec/kiem_lai.py
@@ -14,7 +14,7 @@ from pathlib import Path
 
 from tram.cau_hinh.du_an import DuAn
 from tram.cau_hinh.lenh import khop_bat_ky
-from tram.giao_viec.ban_chep import chep_ban, don_ban, giu_khoa, nhan_moi_truong, ten_ban_chep
+from tram.giao_viec.ban_chep import CoLichHenGio, boc_nha, chep_ban, don_ban, giu_khoa, nhan_moi_truong, ten_ban_chep
 from tram.kiem.chay_lenh import _kill_nhom, chay_mot_lenh, moi_truong_kiem
 from tram.kiem.diff import diff_cham_cam
 from tram.kiem.moi_truong import LoiMoiTruongKiem
@@ -27,7 +27,7 @@ class KetQuaKiemLai:
     dat: bool
     ket_qua: tuple[dict, ...] = ()      # dòng `lenh_kiem[]` (lenh, ket_qua, tom_tat, digest_log)
     cham_cam: tuple[str, ...] = ()
-    loi: str | None = None              # "dong-file-cau-hinh" | "thieu-moi-truong-kiem" | None
+    loi: str | None = None              # "dong-file-cau-hinh" | "thieu-moi-truong-kiem" | "lich-hen-gio" | None
 
     @property
     def digest_log(self) -> list[str]:
@@ -52,7 +52,7 @@ def kiem_lai(kho_git: Path, du_an: DuAn, *, giao_id: str, commit: str, lenh_kiem
     with giu_khoa():
         if don_sach is not None:
             don_sach()                       # tiến trình tram-kiem của lần trước không được sống sang lần này
-        wt = thu_muc / ten_ban_chep(giao_id)
+        wt, lich = thu_muc / ten_ban_chep(giao_id), False
         try:
             chep_ban(kho_git, commit, wt, boc=boc)
             try:
@@ -61,9 +61,15 @@ def kiem_lai(kho_git: Path, du_an: DuAn, *, giao_id: str, commit: str, lenh_kiem
                 return KetQuaKiemLai(False, loi="thieu-moi-truong-kiem")  # không bao giờ chạy với .env có thể thật
             env, ket_qua = moi_truong_kiem(env_goc), []
             for i, lenh in enumerate(lenh_kiem, 1):
-                kq = chay_mot_lenh(lenh, khop_bat_ky(lenh, lenh_cho_phep), cwd=wt, env=env, boc=boc, kill=kill,
+                kq = chay_mot_lenh(lenh, khop_bat_ky(lenh, lenh_cho_phep), cwd=wt, env=env, boc=boc_nha(boc, wt),
+                                   kill=kill,
                                    log=thu_muc_log / f"{giao_id}-kiem-lai-{i}.log", thoi_gian_cho=thoi_gian_cho)
                 ket_qua.append(kq.sang_lenh_kiem())
         finally:
-            don_ban(wt, boc=boc, don_sach=don_sach)   # lỗi → ném: không công nhận kết quả khi chưa dọn sạch
+            try:
+                don_ban(wt, boc=boc, don_sach=don_sach)   # lỗi → ném: không công nhận kết quả khi chưa dọn sạch
+            except CoLichHenGio:
+                lich = True                       # C01: đã gỡ sạch lịch commit cài — có phán quyết, không thử lại mãi
+    if lich:
+        return KetQuaKiemLai(False, tuple(ket_qua), loi="lich-hen-gio")
     return KetQuaKiemLai(bool(ket_qua) and all(k["ket_qua"] == "pass" for k in ket_qua), tuple(ket_qua))
diff --git a/tram/giao_viec/kiem_san_sang.py b/tram/giao_viec/kiem_san_sang.py
index 2ce8c3e..cb2e603 100644
--- a/tram/giao_viec/kiem_san_sang.py
+++ b/tram/giao_viec/kiem_san_sang.py
@@ -42,14 +42,14 @@ def _ghi_duoc(pk: PrincipalKiem, thu_muc: Path | None, chay: Callable) -> MucKie
     d, ghi = thu_muc / ten_ban_chep(THU_MUC_THU), False
     try:
         with giu_khoa():
-            pk.don_sach(chay=chay)
+            pk.don_sach(chay=chay, goc=thu_muc)
             try:
                 ghi = all(_ra(chay, pk.boc_lenh(a)).returncode == 0 for a in (
                     ["/bin/mkdir", str(d)], ["/bin/mkdir", str(d / "con")], ["/usr/bin/touch", str(d / "con" / "x")]))
                 ghi = ghi and (d / "con" / "x").is_file()
             finally:
                 _ra(chay, pk.boc_lenh(["/bin/rm", "-rf", str(d)]))
-                pk.don_sach(chay=chay)
+                pk.don_sach(chay=chay, goc=thu_muc)
     except KiemLaiDangBan:
         return _muc(ten, False, "đang có lần kiểm lại chạy — chạy lại `tram giao kiem` sau")
     except LOI_CHAY as e:
diff --git a/tram/giao_viec/noi_that.py b/tram/giao_viec/noi_that.py
index 42d216b..1fa90a6 100644
--- a/tram/giao_viec/noi_that.py
+++ b/tram/giao_viec/noi_that.py
@@ -7,6 +7,7 @@ import threading
 from collections.abc import Callable
 from dataclasses import replace
 from datetime import datetime, timezone
+from functools import partial
 from pathlib import Path
 
 import yaml
@@ -48,7 +49,7 @@ def dung_bo_that(cg: CauHinhGiaoViec, ch: CauHinhTram, *, bo_dem=None,
     return BoGiaoViec(cac_du_an=lambda: cac_du_an_that(thu_muc_du_an),
                       tao_bd=lambda da: Bd(da.duong_dan, actor=ASSIGNEE), mo_kho=mo_kho_phieu, ch=ch,
                       dong_ho=lambda: datetime.now(timezone.utc), boc=pk.boc_lenh if pk else None,
-                      don_sach=pk.don_sach if pk else None,
+                      don_sach=partial(pk.don_sach, goc=cg.thu_muc_kiem) if pk else None,     # C01: dọn cả gốc
                       kill=pk.kill_nhom if pk else _kill_nhom,
                       doc_beads=DocBeads(bo_dem) if bo_dem is not None else None, thu_muc_kiem=cg.thu_muc_kiem,
                       p4c=nap_phu_thuoc_4c() if cg.bat else PhuThuoc4c())
diff --git a/tram/giao_viec/principal_kiem.py b/tram/giao_viec/principal_kiem.py
index 79106dd..102a538 100644
--- a/tram/giao_viec/principal_kiem.py
+++ b/tram/giao_viec/principal_kiem.py
@@ -4,19 +4,18 @@ Lát 3c: MỘT nguồn khai báo — `cach_ly.tram_kiem: user:<tên> | sandbox:<
 đọc qua `tram.cau_hinh.principal_kiem.doc_principal_kiem`). `tu_cach_ly` dựng argv từ `Principal` của 3a-2 — không
 còn argv tự do trong cấu hình: `boc` = `sudo -n -H -u <tên> --preserve-env=… --` (cơ chế sandbox thêm `sandbox-exec -f
 HO_SO_KIEM`), khớp dòng sudoers `dong_sudoers_kiem`. D22: không trao/thu quyền — `tram-kiem` sở hữu bản chép
-(`ban_chep.py`); `don_sach` giết mọi tiến trình của `tram-kiem`, rồi TRẠM tự đếm lại bằng `pgrep` (không qua sudo)."""
+(`ban_chep.py`); `don_sach` giết mọi tiến trình của `tram-kiem`, gỡ và XÁC NHẬN không còn nguồn lịch (cron/at/
+launchd), dọn tệp cài cắm, rồi TRẠM tự đếm lại bằng `pgrep` (không qua sudo) — C01, `don_tram_kiem.py`."""
 import signal
 import subprocess
 import time
 from collections.abc import Callable
 from dataclasses import dataclass
+from pathlib import Path
 
-from tram.giao_viec.ban_chep import LoiBanChep
 from tram.tho.principal import doc_principal
 from tram.tho.quyen_kiem import HO_SO_KIEM
 
-PGREP = "/usr/bin/pgrep"
-
 
 @dataclass(frozen=True)
 class PrincipalKiem:
@@ -33,19 +32,12 @@ class PrincipalKiem:
         chay(self.boc_lenh(["/bin/kill", "-s", signal.Signals(sig).name.removeprefix("SIG"),
                            "--", f"-{pgid}"]), capture_output=True, timeout=20)
 
-    def don_sach(self, *, chay: Callable = subprocess.run, lan: int = 5, ngu: Callable = time.sleep) -> None:
-        """Gỡ crontab và giết MỌI tiến trình của `tram-kiem` (chạy dưới chính `tram-kiem`), rồi trạm tự đếm bằng
-        `pgrep -U` — không tin lời `tram-kiem`. Còn tiến trình sau `lan` lần, hoặc `pgrep` lỗi → `LoiBanChep`."""
-        for _ in range(lan):
-            chay(self.boc_lenh(["/usr/bin/crontab", "-r"]), capture_output=True, timeout=30)
-            chay(self.boc_lenh(["/usr/bin/pkill", "-KILL", "-U", self.ten]), capture_output=True, timeout=30)
-            r = chay([PGREP, "-U", self.ten], capture_output=True, text=True, timeout=30)
-            if r.returncode == 1:
-                return
-            if r.returncode != 0:
-                raise LoiBanChep(f"pgrep -U {self.ten} lỗi (mã {r.returncode}) — không xác nhận được đã sạch")
-            ngu(0.5)
-        raise LoiBanChep(f"{self.ten} vẫn còn tiến trình sau {lan} lần giết (nguồn tái sinh?) — dừng kiểm lại")
+    def don_sach(self, *, goc: Path | None = None, chay: Callable = subprocess.run, lan: int = 6,
+                 ngu: Callable = time.sleep, **kw) -> None:
+        """C01: vòng đời cách ly đầy đủ giữa hai lần kiểm lại — giết, lịch cron/at/launchd, nhà, tệp, đếm lại
+        (`don_tram_kiem.py`). Không xác nhận được → `LoiBanChep`."""
+        from tram.giao_viec.don_tram_kiem import don_sach
+        don_sach(self, goc, chay=chay, lan=lan, ngu=ngu, **kw)
 
 
 def tu_cach_ly(chuoi: str) -> PrincipalKiem:
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_don_tep_loi_lenh.py tests/test_don_tram_kiem.py tests/test_don_tep_tram_kiem.py tests/test_ban_chep_nha.py tests/test_principal_kiem_hop_nhat.py tests/test_kiem_lai_principal.py tests/test_tick_hai_pha.py tests/test_noi_giao_viec.py tests/test_giao_kiem.py -q`
Expected sau review (chưa chạy): `71 passed`; 68 là số tác giả của bản cũ.

Run: `uv run pytest -q`
Expected sau review (chưa chạy): `N₀ + 107 passed` (thêm 28 ở T11; ghép cùng Task 8 → N₀ + 125).

Kiểm thêm (đã làm khi viết plan — đột biến, mỗi lần bỏ một bước của lượt quét rồi chạy `tests/test_don_tram_kiem.py tests/test_don_tep_tram_kiem.py`): bỏ `don_cron` → 5 failed; bỏ `don_at` → 2 failed; bỏ `don_launchd` → 8 failed; bỏ `kiem_nha` → 2 failed; bỏ `don_tep` → 2 failed. Bỏ `boc_nha` trong `kiem_lai` → `tests/test_ban_chep_nha.py` 1 failed.

- [ ] **Step 5: Commit**

```bash
git add tests/test_don_tep_loi_lenh.py tram/giao_viec/lich_tram_kiem.py tram/giao_viec/launchd_kiem.py tram/giao_viec/don_tram_kiem.py tram/giao_viec/principal_kiem.py tram/giao_viec/ban_chep.py tram/giao_viec/kiem_lai.py tram/giao_viec/noi_that.py tram/giao_viec/kiem_san_sang.py tests/tram_kiem_gia.py tests/test_don_tram_kiem.py tests/test_don_tep_tram_kiem.py tests/test_ban_chep_nha.py tests/test_principal_kiem_hop_nhat.py tests/test_kiem_lai_principal.py tests/test_tick_hai_pha.py tests/test_noi_giao_viec.py tests/test_giao_kiem.py
git commit -m "feat(giao-viec): vòng đời cách ly tram-kiem — gỡ và xác nhận cron/at/launchd, dọn tệp cài cắm, HOME/TMPDIR mới mỗi lần kiểm (lát 3c, C01)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 12: Harness nghiệm thu S6 `tram giao nghiem-thu-kiem` + `tram giao chup-nen-lich` (Q03, C01)

**Độ khó:** `de` · **Đợt:** 5 · **Song song với:** — · **Phải xong trước:** Task 11

**Vì sao là lệnh `tram giao …`, không phải script trong `tests/` hay `ky-nang/`:** harness phải chạy dưới principal THẬT với đúng cấu hình của trạm (`doc_principal_kiem`, `thu_muc_kiem`, khoá kiểm lại, `don_sach` có nền launchd) — lệnh CLI dùng lại `nap_cau_hinh_giao_viec` và `kiem_lai` y như vòng tick, Đại ca gõ được trong Terminal.app, mã thoát rõ; script trong `tests/` dễ bị pytest thu thập hoặc chạy nhầm với `boc` đồng nhất, script `ky-nang/` không có đường cấu hình của trạm.

**Files:**
- Create: `tram/giao_viec/nghiem_thu_kiem.py`, `tram/giao_viec/kich_ban_nghiem_thu.py`, `tram/giao_viec/nen_lich.py`
- Modify: `tram/giao_viec/lenh.py` (thêm `chup-nen-lich`, `nghiem-thu-kiem`)
- Test: `tests/test_nghiem_thu_kiem.py` (mới)

**Interfaces:**
- Consumes: `kiem_lai`, `giu_khoa`, `LoiBanChep` (T3/T10/T11), `PrincipalKiem` (T5), `chup`, `nen_mac_dinh`, `don_tram_kiem`, `don_cron`, `don_at` (T11), `dung_tk` (T11, test), `MucKiem`, `in_ket_qua`.
- Produces: `kich_ban_nghiem_thu.KHANG_DINH` (tên → lệnh sh), `kich_ban_nghiem_thu.kich_ban_tai_sinh(dau) -> str`, `nghiem_thu(pk, goc, *, boc=None, don_sach=None, cho=300, thoi_gian_cho=120, tai_sinh=False, dau_goc=Path("/Users/Shared"), ngu=time.sleep, kich_ban=kich_ban_tai_sinh) -> list[MucKiem]` (từ chối `tai_sinh` với kịch bản thật khi `boc` đồng nhất hoặc principal là chính user đang chạy; `--cho` < 240 với `tai_sinh` → ValueError); `nen_lich.lenh_chup_nen(args, *, chay) -> int`. CLI: `tram giao chup-nen-lich [--dong-y] [--ghi-de]` (0 đã ghi, 1 không dong-y, 2 cấu hình/đọc lỗi, đã có nền, còn tiến trình/lịch), `tram giao nghiem-thu-kiem [--tai-sinh] [--cho GIÂY]` (0 không dòng đỏ, 1 có đỏ hoặc quá hạn tổng, 2 thiếu cấu hình / `--cho` < 240 với `--tai-sinh`).

- [ ] **Step 1: Viết test thất bại**

`tests/test_nghiem_thu_kiem.py` (mới):

```python
"""Harness nghiệm thu S6 (lát 3c, Q03): chạy đúng chuỗi `kiem_lai` → bản chép → repo một commit → môi trường kiểm →
lệnh kiểm → dọn, có khẳng định từng dòng. Test dùng `boc` đồng nhất (user đang test đóng vai `tram-kiem`) và `don_sach`
giả — KHÔNG sudo, không cài lịch thật: khẳng định cách ly ("không đọc kho trạm") phải ĐỎ ở đây, chỉ xanh dưới
principal thật (S6). Kịch bản tái sinh THẬT chỉ được kiểm nội dung — harness từ chối chạy nó khi `boc` đồng nhất."""
import getpass

import pytest

from tram.giao_viec.nghiem_thu_kiem import kich_ban_tai_sinh, nghiem_thu
from tram.giao_viec.principal_kiem import PrincipalKiem
from tram.tho.kiem_may import in_ket_qua

PK = PrincipalKiem(getpass.getuser(), ())                          # boc đồng nhất: argv chạy thẳng


def test_harness_chay_du_chuoi_va_bao_do_khi_khong_cach_ly(tmp_path, tram_home_tam):
    (goc := tmp_path / "kiem").mkdir()
    tram_home_tam.mkdir(parents=True, exist_ok=True)
    don = []
    ds = nghiem_thu(PK, goc, don_sach=lambda: don.append(sorted(p.name for p in goc.iterdir())), dau_goc=tmp_path)
    m = {x.muc: x.muc_do for x in ds}
    assert {k: v for k, v in m.items() if k != "chuỗi kiểm lại: kiem/khong-doc-kho-tram.sh"} == {
        "chuỗi kiểm lại: kiem/danh-tinh.sh": "xanh", "chuỗi kiểm lại: kiem/repo-mot-commit.sh": "xanh",
        "chuỗi kiểm lại: kiem/moi-truong-khong-thanh-git.sh": "xanh", "chuỗi kiểm lại: kiem/nha-moi.sh": "xanh",
        "dọn: gốc bản chép rỗng, don_sach lần cuối sạch": "xanh"}
    assert m["chuỗi kiểm lại: kiem/khong-doc-kho-tram.sh"] == "do" and in_ket_qua(ds)[1] == 1
    assert don[0] == [] and len(don[1]) == 2 and don[-1] == [] and list(tmp_path.glob("tram-nghiem-thu-dau-*")) == []


def test_tai_sinh_bao_nguon_cai_duoc_lich_khong_bi_phat_hien_va_lich_chay(tmp_path, tram_home_tam):
    (goc := tmp_path / "kiem").mkdir()
    kb = kich_ban_tai_sinh(tmp_path / "dau")
    assert all(x in kb for x in ("| crontab -", "| at now", "launchctl submit", "launchctl bootstrap", "setsid",
                                 "launchctl bootout", "chuoi"))
    with pytest.raises(ValueError, match="principal tram-kiem"):        # kịch bản thật không chạy dưới user test
        nghiem_thu(PK, goc, don_sach=lambda: None, dau_goc=tmp_path, tai_sinh=True)
    with pytest.raises(ValueError, match="≥ 240"):
        nghiem_thu(PK, goc, don_sach=lambda: None, dau_goc=tmp_path, tai_sinh=True, cho=1, kich_ban=lambda d: "")
    ngu = []

    def gia_lap_lich_chay(s):                                          # một lịch "lọt" trong lúc chờ → phải ĐỎ
        ngu.append(s)
        next(tmp_path.glob("tram-nghiem-thu-dau-*")).joinpath("cron").touch()
    ds = nghiem_thu(PK, goc, don_sach=lambda: None, dau_goc=tmp_path, tai_sinh=True, ngu=gia_lap_lich_chay,
                    kich_ban=lambda dau: "echo cron-da-cai\nexit 0\n")
    m = {x.muc: (x.muc_do, x.chi_tiet) for x in ds}
    assert ngu == [300] and m["tái sinh: cài được cron"][0] == "xanh" and m["tái sinh: cài được at"][0] == "vang"
    assert m["tái sinh: don_sach phát hiện lịch → gỡ, kết quả lich-hen-gio"][0] == "do"   # don_sach giả không thấy gì
    assert m["tái sinh: không lịch nào chạy sau don_sach"][0] == "do"
    assert m["tái sinh: lần kiểm sau vẫn đạt"][0] == "do"             # khong-doc-kho-tram đỏ dưới boc đồng nhất


def test_lenh_chup_nen_lich_va_nghiem_thu(tmp_path, tram_home_tam, monkeypatch, capsys):
    from types import SimpleNamespace

    from tram_kiem_gia import dung_tk
    from tram.cli import tao_parser
    from tram.giao_viec import lenh
    from tram.giao_viec.launchd_kiem import nen_mac_dinh
    from tram.giao_viec.principal_kiem import tu_cach_ly
    assert lenh._nghiem_thu_kiem(SimpleNamespace(tai_sinh=False, cho=1)) == 2      # chưa có cấu hình: không chạy gì
    tram_home_tam.mkdir(parents=True, exist_ok=True)
    (tram_home_tam / "cau-hinh.yaml").write_text(f"cach_ly:\n  tram_kiem: user:tram-kiem\n"
                                                 f"giao_viec:\n  thu_muc_kiem: {tmp_path.resolve()}/kiem\n")
    tk = dung_tk(tmp_path, tram_home_tam, monkeypatch, tu_cach_ly("user:tram-kiem"))
    tk.launchd.add("vn.la.tai-sinh")
    assert lenh._chup_nen_lich(SimpleNamespace(dong_y=True, ghi_de=False), chay=tk.chay) == 2   # đã có nền
    tk.cron = True
    assert lenh._chup_nen_lich(SimpleNamespace(dong_y=True, ghi_de=True), chay=tk.chay) == 2    # còn lịch: không chụp
    assert lenh._chup_nen_lich(SimpleNamespace(dong_y=True, ghi_de=True), chay=tk.chay) == 0
    nen = dict(d.split("\t") for d in nen_mac_dinh().read_text().splitlines())
    assert set(nen) == tk.launchd and "vn.la.tai-sinh" in capsys.readouterr().err
    p = tao_parser().parse_args(["giao", "nghiem-thu-kiem", "--tai-sinh", "--cho", "90"])
    assert (p.ham.__name__, p.tai_sinh, p.cho) == ("_nghiem_thu_kiem", True, 90.0)
    assert lenh._nghiem_thu_kiem(SimpleNamespace(tai_sinh=True, cho=10)) == 2           # --cho < 240
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_nghiem_thu_kiem.py -q`
Expected: FAIL — `1 error in 0.06s` (kết quả chạy thật trên bản sao: `ModuleNotFoundError: No module named 'tram.giao_viec.nghiem_thu_kiem'`)

- [ ] **Step 3: Viết mã**

`tram/giao_viec/kich_ban_nghiem_thu.py` (mới):

```python
"""Kịch bản của harness nghiệm thu S6 (lát 3c, Q03/C01): khẳng định chạy DƯỚI `tram-kiem` trong bản chép (mỗi khẳng
định một lệnh kiểm) và kịch bản cài lịch như mã agent sẽ làm. `kich_ban_tai_sinh` cài crontab/at/launchd THẬT — chỉ
được chạy dưới principal `tram-kiem` ở S6 (harness từ chối khi `boc` đồng nhất); test chỉ đọc nội dung."""
from pathlib import Path

KHANG_DINH = {
    "danh-tinh": 'test "$(id -un)" = "{ten}"',
    "repo-mot-commit": 'test "$(git rev-list --all --count)" = 1 && test -z "$(git remote)" && test ! -e .git/hooks '
                       '&& test ! -e .git/objects/info/alternates && test -z "$(git status --porcelain -uno)"',
    "moi-truong-khong-thanh-git": 'grep -q NGHIEM_THU=1 .env.testing && ! git ls-files --error-unmatch .env.testing',
    "nha-moi": 'case "$HOME" in *.nha) ;; *) exit 1;; esac; test -w "$HOME" && test -d "$TMPDIR" && '
               'test "$APP_ENV" = testing',
    "khong-doc-kho-tram": '! ls "{kho_tram}" >/dev/null 2>&1',
}


NGUON = ("cron", "chuoi", "at", "submit", "launchd", "gia-nhan", "setsid")


def kich_ban_tai_sinh(dau: Path) -> str:
    """Cài mọi nguồn lịch mà mã agent dưới `tram-kiem` có thể cài — kể cả cron cài tiếp launchd (chuỗi) và job giả nhãn
    nền Apple; cài được thì in `<nguồn>-da-cai`, chạy được thì tạo `dau/<nguồn>`. Mọi nguồn hẹn ≥ 120 s sau khi cài (sau
    `don_sach`), để dấu chỉ xuất hiện khi dọn THẬT SỰ lọt. Mỗi lần cài chạy nền (lệnh treo — vd hộp thoại quyền — bị
    giết khi lệnh kiểm kết thúc, không chặn nguồn khác)."""
    plist = ('<?xml version="1.0" encoding="UTF-8"?><plist version="1.0"><dict><key>Label</key><string>vn.tram.nghiem-'
             f'thu.launchd</string><key>ProgramArguments</key><array><string>/usr/bin/touch</string><string>{dau}/'
             'launchd</string></array><key>StartInterval</key><integer>150</integer></dict></plist>')
    gia = ('n=$(launchctl print "user/$(id -u)" | awk \'/services = {/{f=1;next} f&&/}/{exit} f&&/com.apple/{print $NF;'
           f'exit}}\') && launchctl bootout "user/$(id -u)/$n" && launchctl submit -l "$n" -- /bin/sh -c "sleep 150; '
           f'touch {dau}/gia-nhan" && echo gia-nhan-da-cai')
    cai = ['echo "$(date -v+3M +\'%M %H\') * * * /usr/bin/touch '
           f'{dau}/cron; launchctl submit -l vn.tram.nghiem-thu.chuoi -- /usr/bin/touch {dau}/chuoi" | crontab - '
           '&& echo cron-da-cai && echo chuoi-da-cai', gia,
           f'echo "/usr/bin/touch {dau}/at" | at now + 3 minutes && echo at-da-cai',
           f'launchctl submit -l vn.tram.nghiem-thu.submit -- /bin/sh -c "sleep 150; touch {dau}/submit" '
           '&& echo submit-da-cai',
           f"printf '%s' '{plist}' > \"$TMPDIR/nt.plist\" && "
           'launchctl bootstrap "user/$(id -u)" "$TMPDIR/nt.plist" && echo launchd-da-cai',
           f"/usr/bin/perl -MPOSIX -e 'fork and exit; POSIX::setsid(); sleep 150; system(\"touch\", \"{dau}/setsid\")' "
           "&& echo setsid-da-cai"]
    return "\n".join([*(f"( {c} ) &" for c in cai), "sleep 5", "exit 0", ""])
```

`tram/giao_viec/nghiem_thu_kiem.py` (mới):

```python
"""Harness nghiệm thu S6 cho kiểm lại dưới principal THẬT (lát 3c, Q03 review đợt 5) — `tram giao nghiem-thu-kiem`.
Gọi ĐÚNG đường production `kiem_lai` → `chep_ban` → `repo_ban_chep` → `nhan_moi_truong` → `chay_mot_lenh` → `don_ban`
với `PrincipalKiem` và `thu_muc_kiem` của cấu hình, trên kho git NHÁP + môi trường kiểm GIẢ trong thư mục tạm của trạm
(không dự án thật, không cần `giao_viec.bat`). Mỗi khẳng định là MỘT lệnh kiểm (`kich_ban_nghiem_thu.KHANG_DINH`).
`--tai-sinh`: commit thứ hai cài lịch như mã agent; khẳng định nguồn nào CÀI ĐƯỢC (dấu `-da-cai` trong log), `don_sach`
cuối lần kiểm ấy phát hiện và gỡ (ném "có lịch hẹn giờ"), sau thời gian chờ (≥ 240 s) không lịch nào chạy, lần kiểm sau
vẫn đạt. Cuối cùng, DƯỚI khoá kiểm lại, trạm `don_sach` và xem gốc rỗng; lỗi giữa chừng vẫn dọn. Mã thoát 1 khi có ĐỎ.
Test chạy với `boc` đồng nhất — kịch bản cài lịch THẬT bị từ chối dưới user đang chạy; chứng minh thật chỉ ở S6."""
import getpass
import os
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from tram.cau_hinh.du_an import DuAn, MoiTruongKiem
from tram.duong_dan import tram_home
from tram.giao_viec.ban_chep import LoiBanChep, giu_khoa
from tram.giao_viec.kich_ban_nghiem_thu import KHANG_DINH, NGUON, kich_ban_tai_sinh
from tram.giao_viec.kiem_lai import kiem_lai
from tram.tho.kiem_may import MucKiem

GIT = ("git", "-c", "core.hooksPath=/dev/null", "-c", "user.name=nghiem-thu", "-c", "user.email=nt@localhost",
       "-c", "commit.gpgSign=false")


def _git(kho: Path, *a: str) -> str:
    env = {"PATH": "/usr/bin:/bin", "HOME": str(kho), "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null"}
    return subprocess.run([*GIT, "-C", str(kho), *a], capture_output=True, text=True, env=env, check=True,
                          timeout=60).stdout.strip()


def _commit(kho: Path, tep: dict[str, str], tu: str | None) -> str:
    if tu:
        _git(kho, "checkout", "-q", "--detach", tu)
    for ten, nd in tep.items():
        (kho / ten).parent.mkdir(parents=True, exist_ok=True)
        (kho / ten).write_text(nd, encoding="utf-8")
    _git(kho, "add", "-A")
    _git(kho, "commit", "-q", "-m", "nghiem-thu")
    return _git(kho, "rev-parse", "HEAD")


def _muc(ten: str, dat: bool | None, chi_tiet: str) -> MucKiem:
    return MucKiem(ten, {True: "xanh", False: "do", None: "vang"}[dat], chi_tiet[:200])


def nghiem_thu(pk, goc: Path, *, boc=None, don_sach=None, cho: float = 300, thoi_gian_cho: float = 120,
               tai_sinh: bool = False, dau_goc: Path = Path("/Users/Shared"), ngu=time.sleep,
               kich_ban=kich_ban_tai_sinh) -> list[MucKiem]:
    boc = boc or pk.boc_lenh
    if tai_sinh and kich_ban is kich_ban_tai_sinh and (boc(["x"]) == ["x"] or pk.ten == getpass.getuser()):
        raise ValueError("--tai-sinh cài lịch THẬT: chỉ chạy dưới principal tram-kiem, không dưới user đang chạy")
    if tai_sinh and cho < 240:
        raise ValueError("--cho phải ≥ 240 giây (lịch của kịch bản hẹn 2–3 phút sau khi cài)")
    don_sach = don_sach or (lambda: pk.don_sach(goc=goc))
    tam = Path(tempfile.mkdtemp(prefix="tram-nghiem-thu-"))
    dau = Path(tempfile.mkdtemp(prefix="tram-nghiem-thu-dau-", dir=dau_goc))
    os.chmod(dau, 0o777)                          # tram-kiem ghi được dấu; quét tệp không xoá thư mục của trạm
    log, ra = tram_home() / "log" / "nghiem-thu", []
    try:
        kho = tam / "kho"
        kho.mkdir()
        _git(kho, "init", "-q", "-b", "main")
        goc_sha = _commit(kho, {"README": "nháp\n"}, None)
        _git(kho, "update-ref", "refs/remotes/origin/main", goc_sha)
        kd = {f"kiem/{k}.sh": v.format(ten=pk.ten, kho_tram=tram_home()) + "\n" for k, v in KHANG_DINH.items()}
        sha = _commit(kho, kd, goc_sha)
        (tam / "env.testing").write_text("NGHIEM_THU=1\n")
        da = DuAn("nghiem-thu", kho, None, {}, moi_truong_kiem=MoiTruongKiem(tam / "env.testing", ".env.testing"))

        def kiem(commit: str, lenh: list[str], nhan: str):
            return kiem_lai(kho, da, giao_id=f"nghiem-thu-{nhan}", commit=commit, lenh_kiem=lenh,
                            lenh_cho_phep=["sh *"], chay_lenh=True, thu_muc=goc, boc=boc, env_goc=os.environ,
                            thu_muc_log=log, thoi_gian_cho=thoi_gian_cho, don_sach=don_sach, kill=pk.kill_nhom)
        kq = kiem(sha, [f"sh {k}" for k in kd], "1")
        ra += [_muc(f"chuỗi kiểm lại: {k['lenh'][3:]}", k["ket_qua"] == "pass", k["tom_tat"][-120:])
               for k in kq.ket_qua] or [_muc("chuỗi kiểm lại", False, str(kq.loi))]
        if tai_sinh:
            loi, nk = None, log / "nghiem-thu-2-kiem-lai-1.log"
            nk.unlink(missing_ok=True)                  # không đọc nhầm log của lần nghiệm thu trước
            try:
                loi = kiem(_commit(kho, {"kiem/cai-lich.sh": kich_ban(dau)}, goc_sha), ["sh kiem/cai-lich.sh"], "2").loi
            except LoiBanChep as e:
                loi = f"{type(e).__name__}: {e}"
            cai = set(re.findall(r"([\w-]+)-da-cai", nk.read_text() if nk.exists() else ""))
            ra += [_muc(f"tái sinh: cài được {n}", n in cai or None, "đã cài" if n in cai else
                        "KHÔNG cài được — chưa chứng minh gỡ nguồn này (đọc log)") for n in NGUON]
            lich = cai - {"setsid"}
            ra.append(_muc("tái sinh: don_sach phát hiện lịch → gỡ, kết quả lich-hen-gio", loi == "lich-hen-gio"
                           if lich else None, str(loi or "không có lịch để phát hiện")))
            ngu(cho)
            chay = sorted(p.name for p in dau.iterdir())
            ra.append(_muc("tái sinh: không lịch nào chạy sau don_sach", not chay, f"đã chạy: {chay} / chờ {cho:g} s"))
            kq = kiem(sha, [f"sh {k}" for k in kd], "3")
            ra.append(_muc("tái sinh: lần kiểm sau vẫn đạt", kq.dat, str(kq.loi or "")))
    except (OSError, subprocess.SubprocessError, ValueError) as e:
        ra.append(_muc("nghiệm thu dừng vì lỗi", False, f"{type(e).__name__}: {e}"))
    finally:
        try:
            with giu_khoa():                     # không đụng lần kiểm lại thật đang chạy
                don_sach()
                con = os.listdir(goc)
            ra.append(_muc("dọn: gốc bản chép rỗng, don_sach lần cuối sạch", not con, str(con)))
        except (OSError, subprocess.SubprocessError) as e:
            ra.append(_muc("dọn: don_sach lần cuối", False, f"{type(e).__name__}: {e}"))
        shutil.rmtree(tam, ignore_errors=True)
        shutil.rmtree(dau, ignore_errors=True)
    return ra
```

`tram/giao_viec/nen_lich.py` (mới):

```python
"""`tram giao chup-nen-lich` (lát 3c, C01): chụp NỀN launchd của `tram-kiem` ngay sau khi cài, TRƯỚC lần kiểm lại
đầu tiên (S6 bước 3b). In từng dịch vụ kèm chương trình để Đại ca đọc; cảnh báo nhãn không phải `com.apple.*`,
chương trình ngoài thư mục hệ thống, hoặc nền rỗng; đã có nền thì phải `--ghi-de`. Mã: 0 đã ghi, 1 không dong-y,
2 cấu hình/đọc lỗi, đã có nền, còn tiến trình/lịch."""
import sys
from collections.abc import Callable

from tram.cau_hinh.giao_viec import nap_cau_hinh_giao_viec
from tram.giao_viec import don_tram_kiem as dtk
from tram.giao_viec.ban_chep import giu_khoa
from tram.giao_viec.launchd_kiem import chup, nen_mac_dinh
from tram.giao_viec.lich_tram_kiem import don_at, don_cron, ra


def lenh_chup_nen(args, *, chay: Callable) -> int:
    """Giữ khoá kiểm lại; `tram-kiem` không còn tiến trình, không cron/at — mới chụp; chờ `dong-y`."""
    p, pk = nen_mac_dinh(), None
    try:
        if (pk := nap_cau_hinh_giao_viec().principal_kiem) is None:
            raise ValueError("chưa có cach_ly.tram_kiem")
        if p.exists() and not args.ghi_de:
            raise ValueError(f"đã có nền {p} — chỉ chụp lại sau cập nhật macOS, thêm --ghi-de")
        with giu_khoa():
            for c in ("-U", "-u"):
                ra(chay, pk.boc_lenh([dtk.PKILL, "-KILL", c, pk.ten]))
            if dtk.con_tien_trinh(pk, chay) or don_cron(pk, chay) or don_at(pk, chay, dtk.VIEC_AT):
                raise ValueError(f"{pk.ten} còn tiến trình hoặc lịch cron/at — không chụp nền, Đại ca kiểm tay")
            nen = chup(pk, chay, dtk.uid_cua(pk.ten, chay))
    except (ValueError, OSError) as e:
        print(f"Không chụp nền: {e}", file=sys.stderr)
        return 2
    print(f"Nền launchd user/{pk.ten}: {len(nen)} dịch vụ — chụp NGAY SAU khi cài, TRƯỚC lần kiểm lại đầu tiên:")
    print("\n".join(f"  {n}: {m}" for n, (_, m) in nen.items()))                # đủ path/program để Đại ca đọc
    if la := [n for n, (_, m) in nen.items() if not n.startswith("com.apple.")
              or not m.split(" = ", 1)[-1].startswith(("/System/", "/usr/libexec/", "/usr/sbin/", "/usr/bin/"))]:
        print(f"CẢNH BÁO: dịch vụ lạ: {', '.join(la)} — Đại ca kiểm tay, KHÔNG đồng ý nếu không rõ", file=sys.stderr)
    if not nen:
        print("CẢNH BÁO: miền launchd của tram-kiem chưa có — nền RỖNG; dịch vụ Apple nạp sau này sẽ làm kiểm lại báo "
              "lịch hẹn giờ (chụp lại khi đó)", file=sys.stderr)
    if not args.dong_y and input("Gõ dong-y để ghi nền: ").strip() != "dong-y":
        print("Không làm gì.")
        return 1
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("".join(f"{n}\t{v}\n" for n, (v, _) in nen.items()), encoding="utf-8")
    print(f"Đã ghi {p}.")
    return 0
```

`tram/giao_viec/lenh.py` (sửa — bản vá):

```diff
diff --git a/tram/giao_viec/lenh.py b/tram/giao_viec/lenh.py
index b3e02b0..962ebca 100644
--- a/tram/giao_viec/lenh.py
+++ b/tram/giao_viec/lenh.py
@@ -1,6 +1,9 @@
 """Lệnh `tram giao tick [--thu]`, `tram giao kho-kiem <du_an> [--dong-y]`, `tram giao kiem` (spec 4 §10; 4a-2) —
-chạy ở TÀI KHOẢN TRẠM. `tick` chạy hai pha như các luồng của tram-api, qua cùng khoá file (không trùng vòng đang chạy).
+chạy ở TÀI KHOẢN TRẠM. Lát 3c (S6): `tram giao chup-nen-lich [--dong-y]` (nền launchd của tram-kiem, C01) và
+`tram giao nghiem-thu-kiem [--tai-sinh] [--cho GIÂY]` (harness kiểm lại dưới principal thật, Q03). `tick` chạy hai
+pha như các luồng của tram-api, qua cùng khoá file (không trùng vòng đang chạy).
 Bộ giao việc tắt (`giao_viec.bat: false`) thì chỉ cho `tick --thu` (không ghi beads, không chạy lệnh)."""
+import subprocess
 import sys
 
 
@@ -54,6 +57,46 @@ def _kiem(args) -> int:
     return ma
 
 
+def _pk_goc():
+    from tram.cau_hinh.giao_viec import nap_cau_hinh_giao_viec
+    cg = nap_cau_hinh_giao_viec()
+    if cg.principal_kiem is None or cg.thu_muc_kiem is None:
+        raise ValueError("cần cach_ly.tram_kiem và giao_viec.thu_muc_kiem trong ~/.tram/cau-hinh.yaml (S6 bước 1)")
+    return cg.principal_kiem, cg.thu_muc_kiem
+
+
+def _nghiem_thu_kiem(args, *, tong: float | None = None) -> int:
+    """Chạy harness trong luồng phụ, có hạn TỔNG (lệnh treo dưới sudo/pty không giữ Terminal mãi — S6)."""
+    import threading
+
+    from tram.giao_viec.nghiem_thu_kiem import nghiem_thu
+    from tram.tho.kiem_may import in_ket_qua
+    try:
+        pk, goc = _pk_goc()
+        if args.tai_sinh and args.cho < 240:
+            raise ValueError("--cho phải ≥ 240 giây (lịch của kịch bản hẹn 2–3 phút sau khi cài)")
+    except ValueError as e:
+        print(e, file=sys.stderr)
+        return 2
+    kq: list = []
+    luong = threading.Thread(target=lambda: kq.append(nghiem_thu(pk, goc, tai_sinh=args.tai_sinh, cho=args.cho)),
+                             daemon=True)
+    luong.start()
+    luong.join(tong or args.cho + 900)
+    if not kq:
+        print("[ĐỎ] nghiệm thu quá hạn tổng hoặc dừng vì lỗi — xem ~/.tram/log/nghiem-thu, chạy `tram giao kiem`",
+              file=sys.stderr)
+        return 1
+    van_ban, ma = in_ket_qua(kq[0])
+    print(van_ban)
+    return ma
+
+
+def _chup_nen_lich(args, *, chay=subprocess.run) -> int:
+    from tram.giao_viec.nen_lich import lenh_chup_nen
+    return lenh_chup_nen(args, chay=chay)
+
+
 def them_lenh_giao(sub) -> None:
     g = sub.add_parser("giao", help="Bộ giao việc (phần 4)").add_subparsers(dest="lenh_giao", required=True)
     t = g.add_parser("tick", help="Chạy một vòng tick (pha nhanh rồi pha Git)")
@@ -64,3 +107,11 @@ def them_lenh_giao(sub) -> None:
     k.add_argument("--dong-y", action="store_true", help="Bỏ bước hỏi (chỉ khi Đại ca đã đọc kế hoạch)")
     k.set_defaults(ham=_kho_kiem)
     g.add_parser("kiem", help="Kiểm sẵn sàng: xanh/vàng/đỏ, mã ≠ 0 nếu có đỏ").set_defaults(ham=_kiem)
+    n = g.add_parser("chup-nen-lich", help="Chụp nền launchd của tram-kiem ngay sau khi cài (C01, chờ dong-y)")
+    n.add_argument("--dong-y", action="store_true")
+    n.add_argument("--ghi-de", action="store_true", help="Chụp lại nền đã có (sau cập nhật macOS)")
+    n.set_defaults(ham=_chup_nen_lich)
+    h = g.add_parser("nghiem-thu-kiem", help="S6: harness kiểm lại trên kho nháp dưới principal thật (mã ≠ 0 nếu đỏ)")
+    h.add_argument("--tai-sinh", action="store_true", help="Cài lịch cron/at/launchd như mã agent rồi chờ (S6 bước 6)")
+    h.add_argument("--cho", type=float, default=300, help="Giây chờ quá giờ hẹn của lịch (mặc định 300)")
+    h.set_defaults(ham=_nghiem_thu_kiem)
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_nghiem_thu_kiem.py tests/test_giao_kiem.py -q`
Expected: `15 passed in 5.14s`

Run: `uv run pytest -q`
Expected sau review (chưa chạy): `N₀ + 128 passed` (sau đợt trước +3; chỉ cho bản sửa Q01, C01/C02 vẫn chặn).

**An toàn khi viết test:** test KHÔNG BAO GIỜ chạy `kich_ban_tai_sinh` (cài crontab/at/launchd thật dưới user đang chạy) — harness tự từ chối khi `boc` đồng nhất; test chỉ kiểm nội dung kịch bản và dùng `kich_ban=lambda dau: "exit 0\n"`.

- [ ] **Step 5: Commit**

```bash
git add tram/giao_viec/nghiem_thu_kiem.py tram/giao_viec/kich_ban_nghiem_thu.py tram/giao_viec/nen_lich.py tram/giao_viec/lenh.py tests/test_nghiem_thu_kiem.py
git commit -m "feat(giao-viec): tram giao nghiem-thu-kiem (harness S6 trên đường kiểm lại thật) và chup-nen-lich (lát 3c, Q03, C01)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 9: Chạy thật trên máy B (S6) — **CHỜ CỔNG, KHÔNG PHẢI TASK CODE**

**Không thực thi** cho tới khi: Task 1–8, Task 10, 11, 12 đã ghép, `uv run pytest -q` xanh trên `main`; Codex review lại bản r47 này (D22 + D40 + R4–R7); điều kiện trước Đợt 4 của sổ tay đã xong. (Các mục "Chờ Đại ca chốt" đã chốt hết ở D40.) Cơ chế: theo D3 — **`user` trước**. Người làm: Đại ca (bước có `sudo`/`dong-y`, trong **Terminal.app**) và Em (lệnh kiểm, ghi kết quả). Dừng ngay khi một bước sai.

- [ ] **Bước 1 — cấu hình (Đại ca sửa tay `~/.tram/cau-hinh.yaml` của tài khoản trạm, TRƯỚC `cai-dat-tho`):**
  ```yaml
  cach_ly:
    tram_kiem: user:tram-kiem        # D3: user trước; CÙNG cơ chế với --co-che; user riêng, không trùng khe
    db_nghiep_vu: ['127.0.0.1:3306']
  giao_viec:
    bat: false
    thu_muc_kiem: /Users/Shared/tram-kiem      # CHƯA được tồn tại — cai-dat-tho cho tram-kiem tự tạo
  ```
  Không có khoá `giao_viec.principal_kiem`. Kiểm: `uv run tram giao kiem` không báo lỗi cấu hình (các mục principal còn ĐỎ là đúng).
- [ ] **Bước 2 — kế hoạch cài:** `uv run tram chu cai-dat-tho --khe claude-1=<user> --khe claude-2=<user> --co-che user`. Đọc: bước 0 "Đối soát sổ", mỗi user `[tạo] user …: sudo sysadminctl -addUser … -fullName tram <u> <id> …`, `[tạo] thu_muc /Users/Shared/tram-kiem: sudo -u tram-kiem /bin/mkdir -m 0755 …`, `[tạo] tep /etc/sudoers.d/tram-tho: sudo visudo -cf … && sudo install -m 0440 …`, cảnh báo "D22". Mở `~/.tram/cai-dat-tho/tram-tho.sudoers`: **không có dòng nào chứa `(root)`**; dòng cuối `<tram> ALL=(tram-kiem) NOPASSWD:SETENV: ALL`. Có tài nguyên "đã có nhưng sổ không ghi" → lệnh dừng mã 2: Đại ca kiểm tay, KHÔNG xoá theo đoán. Đúng → **Đại ca gõ `dong-y`**.
- [ ] **Bước 3 — sổ:** `cat ~/.tram/cai-dat-tho/so-cai.jsonl` — mỗi tài nguyên có `du_dinh` rồi `da_tao` kèm `uid`/`guid` (user), `ino`/`uid` (nhà, thư mục) hoặc `sha256` (file); ghi lại `addUser` có tự tạo `/Users/<u>` không (sổ có `"nhan": true` cho nhà) và `ls -ld /var/empty` vẫn `root … drwxr-xr-x` (R5, C01); `dscl . -read /Users/tram-kiem UniqueID GeneratedUID RealName` khớp sổ.
- [ ] **Bước 3b — nền launchd (C01, NGAY sau cài, TRƯỚC bước 4 và mọi lần kiểm lại):** `uv run tram giao chup-nen-lich`. Lệnh giữ khoá kiểm lại, giết và xác nhận `tram-kiem` không còn tiến trình, không có crontab/việc `at` (có → từ chối, mã 2), rồi in từng dịch vụ trong `user/<uid tram-kiem>` kèm dòng chương trình. Đọc: mọi nhãn phải `com.apple.*` và chương trình dưới `/System/`, `/usr/libexec/`, `/usr/sbin/`, `/usr/bin/` (có CẢNH BÁO → dừng, ghi lại). Miền chưa có → nền rỗng (lệnh cảnh báo; dịch vụ Apple nạp sau này sẽ làm kiểm lại báo `lich-hen-gio` — khi đó chụp lại). **Đại ca gõ `dong-y`** → `~/.tram/kiem-lai/nen-launchd.txt`. Ghi transcript (số dịch vụ, phiên bản macOS). Sau cập nhật macOS: `chup-nen-lich --ghi-de`, đọc kỹ rồi mới `dong-y`.
- [ ] **Bước 4 — `uv run tram giao kiem`:** (sau bước 3b — mục "ghi bản chép kiểm" cần nền launchd) 7 mục `principal: …` XANH (danh tính, giữ `APP_ENV`, không đọc kho trạm, thư mục kiểm của tram-kiem, sudoers không NOPASSWD root, ghi bản chép kiểm, dừng được lệnh quá hạn). Còn ĐỎ → dừng, ghi lại.
- [ ] **Bước 5 — bản chép thật (Q03):** `uv run tram giao nghiem-thu-kiem` (không `--tai-sinh`). Harness dựng kho git nháp + môi trường kiểm giả trong thư mục tạm của trạm, gọi `kiem_lai` đúng đường production (`don_sach` thật → `chep_ban` → repo một commit → `nhan_moi_truong` → `chay_mot_lenh` qua HOME mới → `don_ban`) với `PrincipalKiem` và `thu_muc_kiem` của cấu hình; mỗi khẳng định là một lệnh kiểm. Kỳ vọng mọi dòng XANH: `danh-tinh` (`id -un` = tram-kiem), `repo-mot-commit` (một commit, không remote/hooks/alternates, sạch), `moi-truong-khong-thanh-git`, `nha-moi` (HOME/TMPDIR là `<bản chép>.nha`, `APP_ENV=testing`), `khong-doc-kho-tram`, `dọn: gốc bản chép rỗng, don_sach lần cuối sạch`. Mã thoát ≠ 0 → dừng, ghi log `~/.tram/log/nghiem-thu/`. Ghi thời gian chạy (chi phí `git add` + hai lượt `don_sach` ×2 mỗi lần kiểm). Lệnh treo quá hạn tổng (`--cho` + 900 s) → ĐỎ: xem rủi ro "p.wait" ở "Để sau".
- [ ] **Bước 6 — nguồn tái sinh (C01/R6):** `uv run tram giao nghiem-thu-kiem --tai-sinh` (chờ mặc định 300 s, tối thiểu 240). Commit nháp thứ hai cài dưới `tram-kiem`, mỗi nguồn chạy nền: crontab hẹn phút +3 (job cron còn `launchctl submit` một job "chuỗi"), job giả nhãn (bootout một nhãn `com.apple.*` của nền rồi `submit -l` cùng nhãn), `at now + 3 minutes`, `launchctl submit` (sleep 150), `launchctl bootstrap user/<uid>` job `StartInterval 150` (plist trong TMPDIR, bị xoá sau đó), tiến trình `setsid` (sleep 150). Cài được → log `<nguồn>-da-cai`; chạy được → file dấu trong `/Users/Shared/tram-nghiem-thu-dau-*` (thư mục của trạm). Kỳ vọng: dòng `tái sinh: cài được <nguồn>` XANH cho từng nguồn (VÀNG = macOS không cho cài nguồn đó — ghi nguyên văn lỗi trong `~/.tram/log/nghiem-thu/nghiem-thu-2-kiem-lai-1.log`; nguồn không cài được thì an toàn nhưng chưa chứng minh gỡ), `don_sach phát hiện lịch → gỡ, kết quả lich-hen-gio` XANH, `không lịch nào chạy sau don_sach` XANH, `lần kiểm sau vẫn đạt` XANH. Thêm: (a) `sudo -u tram-kiem crontab -l` trả đúng chữ "no crontab for tram-kiem"; (b) `sudo -u tram-kiem launchctl print user/<uid>` có khối `services = {` và `…/<nhãn>` có dòng `program =`/`path =`; (c) `ls -ld /var/empty` vẫn `root sys … drwxr-xr-x`; (d) `sudo find / -xdev -type d -perm -0002 2>/dev/null` — danh sách thư mục ghi-chung trên máy B, Đại ca quyết có thêm vào `GOC_CHUNG`; (e) `ls -ln /usr/lib/cron/jobs` khi còn việc `at` (chủ file = UID tram-kiem?); (f) `crontab -`/`-r` dưới `sudo -u tram-kiem` có bật hộp thoại quyền hay treo không (trên máy dev, khi chạy thử plan, `crontab -` không TTY treo tới hết hạn); (g) `launchctl print login/…` / `gui/<uid>` của `tram-kiem` không tồn tại. Bất kỳ dấu nào xuất hiện, hay một dòng ĐỎ → dừng S6, không bật `giao_viec.bat`, báo Em sửa thiết kế. Transcript ghi thời điểm cài, thời điểm hẹn, thời điểm `don_sach`, kết quả, giới hạn của phép đo.
- [ ] **Bước 7 — H9:** `uv run tram chu kiem-cach-ly --principal user:<khe-1> --principal user:<khe-2>` → dòng `user:tram-kiem — …` mọi thăm dò XANH.
- [ ] **Bước 8 — symlink phía thợ (G19, T2 đã ghép):** trong một worktree khe, commit symlink trỏ ra `~/.tram/tho.yaml` của tài khoản quản lý; chạy một phiếu thử; `ls -le` trên `tho.yaml` không có ACL của principal.
- [ ] **Bước 9 — hoàn tác (khi S6 hỏng, hoặc để thử):** `uv run tram chu go-cai-dat-tho` → đọc kế hoạch (đối soát → daemon → sudoers → thư mục kiểm `sudo -u tram-kiem /bin/rm -rf` → user `-keepHome`; nhà chỉ khi `--xoa-nha`) → **Đại ca gõ `dong-y`**. Chạy lại → `Không còn gì để gỡ.`; `ls /etc/sudoers.d/tram-tho` không còn; `dscl . -list /Users | grep tram-` rỗng; sổ có `da_go`. Nhắc `tram chu go-may B` nếu không cài lại.
- [ ] **Bước 10 — ghi kết quả** `docs/spikes/<ngày>-s6-principal-kiem.md` (phiên bản macOS, lệnh, mã thoát, transcript đã che bí mật), thêm "Ghi chú triển khai" vào cuối plan này, cập nhật bead `bs-urj.12/13/14`, `bs-8eh.4`.

---

## Sơ đồ đợt chạy

Số dưới đây sau review là DỰ KIẾN, chưa chạy; mốc gốc tác giả trên bản sao `main 793facb` (N₀ = 2100, đã gồm T2/T4/R3 và các lát khác ghép tới review đợt 5), bản r47. N₀ đo lại khi thực thi.

```
Đã ghép (D21): T2, T4, R3  → N₀ = 2100
Đợt 1: T1, T3          → N₀ + 14 (2114)
Đợt 2: T5, T10         → N₀ + 38 (2138)
Đợt 3: T6, T7          → N₀ + 79 (2179)
Đợt 4: T8, T11         → N₀ + 125 (2225)
Đợt 5: T12             → N₀ + 128 (2228)
(T9: chờ Codex review r47 + cổng S6 — Task 9 bước 3b, 5, 6 trên máy B)
```

| Task | Độ khó | Đợt | Phải xong trước | File chạm (ngoài test) | Test mới | Toàn bộ sau task (trên main đợt trước) |
|---|---|---|---|---|---|---|
| 1 | de | 1 | — | `tram/tho/quyen_kiem.py` | 7 | N₀ + 7 |
| 2 | — | đã ghép | — | `tram/tho/principal_khe.py` | (2, đã tính trong N₀) | — |
| 3 | kho | 1 | — | `tram/giao_viec/cay_kiem.py`, `ban_chep.py`, `kiem_lai.py`, `bo.py`, `tick_pipeline.py`, `noi_that.py` | 7 | N₀ + 7 |
| 4 | — | đã ghép | — | `tram/chu/cai_dat.py` | (1, đã tính trong N₀) | — |
| 5 | kho | 2 | 1, 3 | `tram/cau_hinh/principal_kiem.py`, `tram/giao_viec/principal_kiem.py`, `tram/cau_hinh/giao_viec.py`, `tram/cau_hinh/cach_ly.py`, `tram/giao_viec/noi_that.py`, `tram/giao_viec/kiem_san_sang.py` | 17 | N₀ + 31 |
| 10 | de | 2 | 3 | `tram/giao_viec/repo_ban_chep.py`, `tram/giao_viec/ban_chep.py`, `tram/giao_viec/kiem_lai.py` (docstring) | 7 | N₀ + 21 |
| 6 | kho | 3 | 1, 5 | `tram/chu/nhat_ky.py`, `so_cai_tho.py`, `dinh_danh.py`, `tai_nguyen.py`, `cai_dat_kiem.py`, `cai_dat_tho.py`, `kiem_cach_ly.py`, `lenh_tho.py` | 28 | N₀ + 66 |
| 7 | de | 3 | 5 | `tram/giao_viec/kiem_goc.py`, `tram/giao_viec/kiem_san_sang.py` | 13 | N₀ + 51 |
| 8 | de | 4 | 6 | `tram/chu/go_cai_dat_tho.py`, `tram/chu/lenh_tho.py` (chèn theo mốc) | 18 | N₀ + 97 |
| 11 | kho | 4 | 3, 5, 7, 10 | `tram/giao_viec/lich_tram_kiem.py`, `launchd_kiem.py`, `don_tram_kiem.py`, `principal_kiem.py`, `ban_chep.py`, `kiem_lai.py`, `noi_that.py`, `kiem_san_sang.py` | 28 | N₀ + 107 |
| 12 | de | 5 | 11 | `tram/giao_viec/nghiem_thu_kiem.py`, `kich_ban_nghiem_thu.py`, `lenh.py` | 3 | N₀ + 128 |
| R3 | — | đã ghép | — | `tram/cong_bo/nguon_lai.py` … | (4, đã tính trong N₀) | — |
| 9 | — | chờ cổng | mọi task (cả T10, T11, T12) + review | (không mã) | — | — |

"Test mới" đếm ca pytest (kể cả ca tham số hoá) — tăng của cả bộ sau task: T1 = 7; T3 = 7; T5 = 17; T10 = 7; T6 = 28 (`test_so_cai_tho.py`, `test_dinh_danh_cai.py`, `test_cai_dat_tho_kiem.py`, `test_cai_nha_tho.py`); T7 = 13; T8 = 18 (`test_go_cai_dat_tho.py`, `test_go_cai_lai.py`); T11 = 28 (`test_don_tram_kiem.py`, `test_don_tep_tram_kiem.py`, `test_ban_chep_nha.py`; test cũ sửa giữ số ca); T12 = 3. T11 thêm 3 ca `test_don_tep_loi_lenh.py`; tổng N₀+128 (2370 nếu đo lại N₀=2242), không phải kết quả chạy. Cột "Toàn bộ sau task" tính trên `main` của đợt trước, chưa ghép task cùng đợt.

File dùng chung giữa các đợt (đúng một task sở hữu mỗi lần sửa): `tram/giao_viec/noi_that.py`, `tests/test_noi_giao_viec.py` (T3 → T5 → T11); `tram/giao_viec/kiem_san_sang.py`, `tests/test_giao_kiem.py` (T5 → T7 → T11); `tram/chu/lenh_tho.py` (T6 bản vá → T8 chèn theo mốc); `tram/giao_viec/ban_chep.py`, `tram/giao_viec/kiem_lai.py` (T3 → T10 → T11); `tests/test_ban_chep.py` (T3 → T10); `tram/giao_viec/principal_kiem.py`, `tests/test_principal_kiem_hop_nhat.py` (T5 → T11); `tests/test_kiem_lai_principal.py`, `tests/test_tick_hai_pha.py` (T3 → T11). Không file nào bị hai task cùng đợt sửa (T1↔T3, T5↔T10, T6↔T7, T8↔T11 rời nhau).

## Để sau (chờ cổng / lát khác) — không lập task code ở plan này

| Phần | Spec | Chờ | Plan này chừa sẵn |
|---|---|---|---|
| Chạy thật `cai-dat-tho`, bản chép, `go-cai-dat-tho` | spec 3 §12 S6 | Codex review lại bản D22 + D40, Đại ca `dong-y` | Task 9 |
| Lịch sử/tag/submodule/LFS trong bản chép (ngoài repo một commit của D40 (b)) | spec 4 §6.2 | dự án thật cần — đo ở S6 | mục "Cây kiểm và `.git`" |
| Wrapper số đối số cố định thay `ALL` dưới `tram-kiem` | spec 3 §7.3 mục 5 | D40 chọn `ALL` — chỉ xét lại nếu cần thư mục bản chép 0700 (rủi ro (c)) | "Phân tích sudoers" |
| Kẽ hở còn lại của vòng đời cách ly (rủi ro (a)): job tự xoá rồi cài nguồn khác đúng lúc quét, nhãn nền không nạp bị chiếm, thư mục ghi-chung bên thứ ba, `login/<asid>` | spec 3 §7.3 mục 5 | S6 (Task 9 bước 6) + Đại ca chốt câu hỏi r47 | Task 11 thu hẹp; `cron.deny`/`at.deny` hoặc `bootout` cả miền nếu S6 cho phép |
| `chay_mot_lenh`: `p.wait()` sau SIGKILL không có hạn; dưới `sudo` có `use_pty` thì kill nhóm qua principal không tới lệnh (review C01 vòng 2, mã 3a-1) | spec 3 §7.5 | S6 bước 5 đo; lát sửa riêng | CLI harness có hạn tổng; kiểm lại trong tick chưa |
| Regression cây CRLF/`text`/`eol`/`working-tree-encoding` cho G32 (R7) | spec 4 §6.2 | lát sau / Đại ca giao | rủi ro (h) |
| Quyền Git chung của khe (objects/ref, cấm config/hooks) | spec 3 §7.3, 3a-2 G20 | S6 | — |
| Gỡ cài đặt Mac thợ từ xa (`tram tho dang-ky`) | spec 3 §9.2 | 3b chạy thật | sổ `so-cai.jsonl` là khuôn |
| Kênh ghi Unix socket (G29 3a-2), Keychain dưới sandbox (G34), credential dưới daemon (G35) | spec 2 §4 mục 2b, spec 3 §12 S2 | S2, S6, N2 | — |

## Tự review

**1. Độ phủ yêu cầu**

| Yêu cầu (bead / spec / quyết định) | Task | Kiểm bằng |
|---|---|---|
| Một nguồn khai principal kiểm (bs-urj.12) | 5, 6 | `test_giao_viec_doc_qua_nguon_chung`, `test_lech_hoac_sai_dang_la_loi_cau_hinh` (4), `test_lenh_doc_cau_hinh_khong_con_co_tram_kiem`, `test_kiem_cach_ly_du_bo_duoi_sudo_va_canh_bao_kenh_header` |
| D22: không root, không helper, không ACL/chmod | 1, 5, 6, 7 | `test_co_che_user_chi_runas_tram_kiem_khong_root`, `test_sudoers_chi_runas_tram_kiem_va_tram_kiem_tu_tao_thu_muc`, `test_principal_kiem_khong_con_trao_thu_quyen`, `test_sudoers_nopasswd_root_la_do` |
| D22: `git archive` → `tar -x` dưới `tram-kiem`; môi trường qua stdin; `tram-kiem` tự dọn | 3 | `test_ban_chep_dung_commit_co_repo_git_khong_bi_export_ignore_giau`, `test_dat_khi_moi_lenh_pass_va_co_moi_truong_kiem`, `test_don_sach_truoc_khi_chep_va_truoc_khi_don` |
| D40 (b): bản chép là repo git một commit, hook tắt; git lỗi fail-closed; bản chép rỗng | 10 | `test_ban_chep_la_repo_mot_commit_cay_dung_commit_goc_khong_lich_su`, `test_hook_filter_template_cua_cau_hinh_ngoai_khong_chay`, `test_git_loi_thi_fail_closed_nhu_tar` (3), `test_ban_chep_rong_van_la_repo_mot_commit_cay_rong`, `test_commit_chua_git_thi_khong_dung_repo_len_do` |
| Sudoers chặn được gì / argv lúc chạy khớp sudoers | 1, 5 | `test_co_che_sandbox_ghim_tien_to_ho_so_co_dinh`, `test_moi_argv_duoi_tram_kiem_khop_sudoers[user, sandbox]` |
| Ca F01 còn áp dụng | 3, 5, 7, 10 | bảng "Ca F01/F02" |
| R2 (F02): journal, định danh, chỉ gỡ thứ lần cài tạo, đối soát crash, user có sẵn không bị xoá | 6, 8 | bảng "Ca F01/F02" |
| `tram giao kiem` kiểm điều kiện mới khi chạy thật | 5, 7 | `test_principal_dat_moi_muc`, `test_principal_sai_tung_muc_la_do` (7), `test_dang_kiem_lai_thi_muc_ghi_do_khong_giet_tram_kiem`, `test_thu_muc_goc_sai_la_do` (7) |
| Chạy được với cả hai cơ chế §14 (D3 giữ hai nhánh) | 1, 5, 6 | `test_sandbox_boc_qua_ho_so_co_dinh_cua_tram_kiem`, `test_sandbox_cai_ho_so_co_dinh_va_ghim_sudoers`, `test_go_dung_thu_tu_het_sach_va_chay_lai_rong` (sandbox) |
| Lần cài đầu không dừng ở `bootout` | T4 (đã ghép) | `test_bootout_va_pkill_qua_sudo_khong_check` |
| R4 (Q01): đuôi sổ dở, short write, UTF-8 dở, khoá cài/gỡ | 6, 8 | `test_duoi_do_bi_cat_giu_bang_chung_roi_moi_noi` (3), `test_short_write_va_loi_giua_chung_khong_lam_hong_so`, `test_khoa_giu_boi_tien_trinh_khac`, `test_duoi_do_doi_soat_doc_go_doc_cai_lai`, `test_go_khi_dang_cai_thi_khong_lam_gi` |
| R5 (Q02): biên nhận user ≠ hoàn tất nhà; nhà lạ không bị nhận; gỡ nhà riêng | 6, 8 | `tests/test_cai_nha_tho.py`, `test_cai_lai_sau_khi_giu_nha_khong_nhan_nha_cu` (2), `test_xoa_nha_khong_xoa_nha_la_va_khong_dung_var_empty` |
| C01 (R6): lịch hẹn trễ, lỗi gỡ cron, launchd/at, nhãn nền bị chiếm, chuỗi nguồn, tệp cài cắm, HOME mới | 11 | `tests/test_don_tram_kiem.py`, `tests/test_don_tep_tram_kiem.py`, `tests/test_ban_chep_nha.py` |
| Q03: harness S6 đi đúng chuỗi kiểm lại | 12 | `tests/test_nghiem_thu_kiem.py` (boc đồng nhất); thật ở Task 9 bước 5, 6 |
| Chạy thật S6 | 9 | chờ cổng |

**2. Quét placeholder:** không có "TBD/TODO/tương tự Task N"; mọi bước mã có khối mã đầy đủ (file mới nguyên văn; file có sẵn bằng bản vá sinh từ bản sao đã chạy, hoặc script chèn theo mốc đã chạy); mọi lệnh có kết quả mong đợi. `<model đang thực thi>` trong lệnh commit là cố ý.

**3. Khớp chữ ký:** `goc_hop_le`, `dong_sudoers_kiem`, `ho_so_tram_kiem`, `HO_SO_KIEM`, `THU_MUC_CAI` (1) ↔ 5, 6; `LoiBanChep`, `KiemLaiDangBan`, `giu_khoa`, `ten_ban_chep` (3) ↔ 5 (`don_sach`, `_ghi_duoc`); `chep_ban`, `LoiBanChep`, `_chay` (3) ↔ 10 (`lenh_repo`); `kiem_lai(don_sach=…)` (3) ↔ `BoGiaoViec.don_sach` (3) ↔ `dung_bo_that` (5: `pk.don_sach`); `PrincipalKiem(ten, boc, co_che)`, `tu_cach_ly`, `doc_principal_kiem` (5) ↔ 6, 7; `SoCai`, `Muc`, `doi_soat`, `dinh_danh.*` (6) ↔ 8; `HeGia` (6) ↔ 8; `bo_qua_loi`/`thuc_hien` (T4 đã ghép) ↔ 6 (`lenh` bootout). Bản r47: `SoCai.giu`, `SoCaiDangBan`, `nha_tram`, `user_cua_tram` (6) ↔ 8 (`lenh_cli`); `CoLichHenGio`, `boc_nha`, `nha_cua` (11) ↔ `kiem_lai` (11) ↔ 12; `don_tram_kiem.don_sach` (11) ↔ `PrincipalKiem.don_sach` ↔ `dung_bo_that` (`partial(…, goc=)`) ↔ `_ghi_duoc`; `chup`, `nen_mac_dinh`, `uid_cua`, `con_tien_trinh`, `don_cron`, `don_at` (11) ↔ `nen_lich` (12); `kiem_thu_muc_goc` (7) ↔ `don_sach` (11). Với mã có sẵn: `Principal.boc([])`, `doc_principal`, `BIEN_GIU`, `ho_so_sandbox`, `KeHoach(tep, lenh, canh_bao, buoc)`, `MucKiem`, `chay_mot_lenh(…, cwd, boc, kill)`, `loi_dich` — đúng mã `main 4a907cc`.

**4. Đã chạy thử (16/10):** xem "Ghi chú kiểm plan (16/10)"; bản r47: "Ghi chú kiểm plan (16/10/2026, bản r47)". Phát hiện khi chạy thử: bsdtar 3.5.3 (macOS 15.6) **thay** symlink ở thành phần cuối bằng file thường khi giải nén (đích symlink không bị ghi) và **từ chối** giải nén xuyên symlink ở thư mục cha ("Cannot extract through symlink", mã 1); `git archive` (git 2.56) bỏ file theo `export-ignore` của commit trừ khi `info/attributes` có `* -export-ignore -export-subst`; bỏ kiểm `loi_dich_trong_cay` thì `test_dich_moi_truong_kiem_la_symlink_bi_tu_choi` đỏ (bsdtar đè symlink và kiểm lại chạy tiếp) — hai lớp đều cần.

**5. Rủi ro còn lại (Đại ca biết):**
- (a) Vòng đời cách ly (C01, Task 11) thay "pgrep rỗng". ĐÃ chặn bằng test hệ giả: lịch hẹn trễ cron/at/launchd, lỗi gỡ crontab, chuỗi nguồn, nhãn nền bị chiếm, ngập job KeepAlive, tệp cài cắm. CHƯA chứng minh (không tuyên bố): (1) job tự xoá mình rồi cài nguồn khác đúng giữa hai lần đọc trong cùng lượt, lặp lại ở hai lượt liên tiếp — không có thao tác nguyên tử "không tiến trình + không lịch" khi không root; (2) nhãn nền KHÔNG nạp lúc quét bị job lạ chiếm sau đó, hoặc job chiếm nhãn nền với cùng chương trình/đối số/biến môi trường nhưng khác MachServices; (3) thư mục ghi-chung khác do phần mềm bên thứ ba tạo, mục sâu hơn cấp một trong thư mục người khác ghi được, bộ nhớ chia sẻ POSIX tên đoán được, anh em của gốc khi cha của gốc thuộc `tram-kiem` (cấu hình Task 9 đặt gốc dưới `/Users/Shared` — cha là root); (4) miền `login/<asid>`; (5) mục trong `DARWIN_USER_DIR` mà `tram-kiem` không xoá được làm mọi lần kiểm dừng (liveness); (6) định dạng thật của `crontab -l`, `atq`, `launchctl print`, chủ file `at` — S6 đo. S6 bước 6 (harness `--tai-sinh`) là bằng chứng thật; chưa đạt thì không bật `giao_viec.bat`.
- (b) Trong lúc một lần kiểm lại chạy, mã của chính commit đó có thể sửa bản chép (vd sửa test trước khi chạy test) — là mã đang kiểm, QC đọc diff; ngoài phạm vi cách ly.
- (c) Thư mục bản chép 0755 (trạm cần đi qua để làm cwd): user khác trên máy đọc được mã dự án (không đọc được `.env.testing` 0600). Wrapper (mục 4) cho phép 0700.
- (d) Khoá một lần một lúc: nhiều dự án xếp hàng kiểm lại; lần bận ném `KiemLaiDangBan` → vòng tick đếm "lỗi" (không phải escalation).
- (e) Đối soát thư mục: thư mục có mặt sau `du_dinh` chỉ được nhận khi chủ là UID mong đợi (`tram-kiem` cho thư mục kiểm, root cho `/usr/local/tram`) — không có mã id như user; root tạo đúng đường dẫn đó sau crash vẫn bị nhận (chỉ `rmdir` khi gỡ). Lần cài thấy thư mục lạ sau `du_dinh` dở chỉ dừng lúc CHẠY (sau các user đã tạo — vẫn gỡ được theo sổ). Gỡ thư mục root chỉ `rmdir` (rỗng mới xoá); thư mục kiểm gỡ bằng `rm -rf` DƯỚI `tram-kiem` — không bao giờ root.
- (f) `sysadminctl` có thể "thành công" mà không tạo: không tin mã thoát, chỉ tin quan sát `dscl` (RealName mang mã id).
- (g) Sổ: dòng hỏng ở giữa → không cài/gỡ gì cho tới khi Đại ca sửa tay (cố ý: không đoán). Đuôi dở thì tự cắt (bằng chứng ở `so-cai.jsonl.duoi-hong`, có thể lặp nếu crash giữa ghi bằng chứng và cắt). Mỗi lần ghi đọc lại cả sổ (sổ nhỏ). `F_FULLFSYNC` không đo được bằng test (cần mất điện thật).
- (k) Nhà `/var/empty` của `tram-kiem`: nếu `sysadminctl -addUser -home /var/empty` đổi chủ thư mục ấy (chưa biết), mọi lần kiểm lại dừng ở bước "nhà" (fail-closed) — S6 bước 3 kiểm, khi đó Đại ca trả chủ về root:sys.
- (l) Nhà giữ lại sau gỡ (D40 mặc định) chặn lần cài lại cùng tên user (UID mới hoặc UID dùng lại đều không nhận nhà cũ) — `go-cai-dat-tho --xoa-nha` nếu sổ ghi nhà đó, không thì xoá tay.
- (m) Kết quả "lich-hen-gio" (C01): commit có test hợp lệ dùng `crontab`/`launchctl`/`at` sẽ bị coi là không đạt và tạo escalation; dịch vụ Apple mới xuất hiện sau khi chụp nền (vd nền chụp lúc miền chưa có) cũng gây kết quả này cho tới khi Đại ca chụp lại nền (`chup-nen-lich --ghi-de`).
- (h) Cây kiểm là repo git MỘT commit (D40 (b)): lệnh kiểm cần lịch sử/tag/remote/submodule vẫn hỏng; `git status` thấy `?? .env.testing`; LFS/submodule làm cây khác cây gốc; `.gitattributes` text/eol/working-tree-encoding cũng cần ca giữ nguyên tree (ví dụ blob CRLF đã track, commit sau chỉ thêm `*.txt text` không renormalize: `git add -A -f` có thể chuẩn hoá lại thành LF). Đây là khoảng trống của lời hứa G32, không phải bằng chứng leo quyền; `git add` cây lớn tốn thời gian (chưa đo — S6 bước 5). Hook/filter bị chặn bằng cấu hình cô lập (G33) — nếu lọt cũng chỉ chạy dưới `tram-kiem`, như lệnh kiểm.
- (i) Đổi khoá/CLI (G1, G4 — ĐÃ CHỐT D40) làm sổ tay §4.1, §5.1 lỗi thời tới khi Em cập nhật.
- (j) `lenh_repo` dùng git mà trạm tìm thấy trong PATH (`shutil.which`) với `PATH=/usr/bin:/bin:…` cho tiến trình con; nếu daemon trạm chỉ thấy `/usr/bin/git` (Apple, cần Command Line Tools) thì `git` chạy dưới `tram-kiem` cũng là bản đó — S6 bước 5 kiểm.

## Cần sửa spec sau (Codex/Đại ca đối chiếu khi review)

- **Spec 3 §7.3 mục 5:** khai `tram-kiem` ở `cach_ly.tram_kiem`; user riêng; D22 — bản chép do `tram-kiem` sở hữu (`git archive` → `tar -x` dưới `tram-kiem`, môi trường qua stdin, tự dọn), D40 — bản chép là repo git một commit do `tram-kiem` tự dựng (hook tắt, cấu hình git cô lập), không helper root/ACL; `don_sach`; khoá một lần một lúc; hồ sơ sandbox cố định (G1, G5, G12, G13, G21–G25, G32, G33).
- **Spec 3 §9.1:** `tram chu cai-dat-tho` không còn `--tram-kiem`; sổ journal `so-cai.jsonl` v2 (du_dinh/da_tao/khong_tao/da_go, định danh, đối soát, từ chối cài đè); `tram chu go-cai-dat-tho` (G4, G15, G26–G29).
- **Spec 3 §7.3 mục 7 / plan 3a-2 G31:** `kiem-cach-ly` chạy H9 cho `tram-kiem` qua argv kiểm lại thật (G18).
- **Spec 4 §6.2 bước 1, 3, §13 / plan 4a-2 G2, G7, G8:** "worktree kiểm" → "bản chép kiểm" (repo git một commit, không lịch sử — D40); `giao_viec.principal_kiem` thành khoá cũ; `thu_muc_kiem` là đường dẫn thật thuộc `tram-kiem`; `trao_quyen` → `don_sach` (G2, G6, G10, G21–G23, G30).
- **Spec 2 §12.5 (khoá `cau-hinh.yaml`):** `cach_ly.tram_kiem` là nguồn duy nhất; `giao_viec.bat: true` cần `cach_ly.tram_kiem`.
- **Sổ tay chạy thật §4.1, §5.1, §6 mục 6:** thứ tự S6 mới (Task 9, gồm bước 3b nền launchd, bước 5–6 harness); bỏ mọi bước helper root/ACL; thêm bước sổ và tái sinh.
- **Spec 3 §7.3 mục 5 (bản r47):** vòng đời cách ly `tram-kiem` giữa hai lần kiểm (C01): nhà `/var/empty`, HOME/TMPDIR mới mỗi lần, `don_sach` gỡ và xác nhận cron/at/launchd so với nền, dọn tệp, lần kiểm có lịch → kết quả `lich-hen-gio`; `tram giao chup-nen-lich`, `tram giao nghiem-thu-kiem`.
- **Spec 3 §9.1 (bản r47):** user và nhà là hai bước có sổ; `tram-kiem` không `createhomedir`; gỡ luôn `-keepHome`, nhà xoá riêng khi `--xoa-nha`; khoá sổ cho cài/gỡ.
- **Spec 4 §6.2 bước 4 (bản r47):** thêm lỗi kiểm lại `lich-hen-gio` (escalation như các lỗi kiểm lại khác).

## Review đợt 5 — R4–R7: thiết kế đã chọn và trạng thái (bản r47, 16/10/2026)

**R4 (Q01) — ĐÃ GIẢI QUYẾT ở mức plan (mã + regression, Task 6/8).** Thiết kế: `tram/chu/nhat_ky.py` (mới) giữ ba thao tác journal dùng chung: `khoa` (flock không chờ trên `so-cai.jsonl.khoa`, bận → `SoCaiDangBan`), `cat_duoi` (GỌI DƯỚI KHOÁ, trước mỗi lần nối: bytes sau `\n` cuối — bản ghi dở do crash/short write, kể cả UTF-8 dở, kể cả JSON đủ mà thiếu `\n` — được chép nguyên ra `so-cai.jsonl.duoi-hong` rồi cắt khỏi sổ; mọi dòng hoàn chỉnh giữ nguyên), `ghi_het` (lặp `os.write` tới đủ bytes, rồi `F_FULLFSYNC`; file mới thì fsync cả thư mục chứa và thư mục cha). Đọc (`SoCai.muc`) tách theo bytes, bỏ đuôi dở trước khi giải mã; dòng hỏng ở giữa, chuyển trạng thái sai (`CHUYEN`), `dinh_danh` sai dạng → `ValueError` (không cài/gỡ gì). Cả lần `cai-dat-tho` và `go-cai-dat-tho` (lập kế hoạch → `dong-y` → chạy) giữ khoá sổ; lần thứ hai (cùng hay khác tiến trình) báo "đang có cài/gỡ khác", mã 2, không làm gì. Regression: `test_duoi_do_bi_cat_giu_bang_chung_roi_moi_noi` (3 kiểu đuôi), `test_short_write_va_loi_giua_chung_khong_lam_hong_so`, `test_khoa_so_chan_ghi_cua_lan_cai_go_khac`, `test_khoa_giu_boi_tien_trinh_khac` (hai tiến trình), `test_duoi_do_doi_soat_doc_go_doc_cai_lai` (đúng chuỗi review yêu cầu: intention + đuôi → đối soát → đọc → gỡ → đọc → cài lại), `test_dang_go_thi_cai_dat_tho_khong_lam_gi`, `test_go_khi_dang_cai_thi_khong_lam_gi`, `test_khoa_truoc_khi_xem_so`. Còn lại cho S6: `F_FULLFSYNC` trên APFS máy B (chỉ đo được bằng mất điện thật — không làm); ghi nhận là giới hạn.

**R5 (Q02) — ĐÃ GIẢI QUYẾT ở mức plan (Task 6/8).** Thiết kế: user và nhà là HAI tài nguyên, hai bản ghi: `user_tram` chỉ `sysadminctl -addUser` (RealName mang mã id); `nha_tram` (`tai_nguyen.py`) là `createhomedir`, mong đợi = UID + GUID của user lúc tạo. "User của trạm" (`user_cua_tram`) = cùng UID + GUID một `da_tao`, hoặc RealName mang mã id của một `du_dinh` còn dở (crash sau `addUser`, trước `da_tao`). Nhà có sẵn chỉ được nhận/giữ (`nhan`) khi: user cùng tên đang là của trạm, nhà là thư mục thật thuộc đúng UID ấy, và mọi biên nhận cũ của nhà (cùng inode) ghi cùng GUID. Nhà có sẵn mà user chưa có, nhà thuộc UID khác, nhà giữ lại từ user đã gỡ (kể cả khi macOS dùng lại UID) → từ chối NGAY lúc lập kế hoạch, không tạo user nào, không chown/ghi đè. `addUser` tự tạo nhà hay không (chưa biết — S6 đo) đều đi được: nhà vừa xuất hiện thuộc đúng UID thì ghi `da_tao` (`nhan`). Chạy lại chỉ làm bước còn thiếu; UID/GUID giữ nguyên. Thư mục kiểm và `/usr/local/tram` cũng mang UID chủ mong đợi (`tram-kiem`/root) — thư mục người khác tạo sau `du_dinh` dở không bị nhận. Gỡ: user luôn `-deleteUser -keepHome` (cả `tram-kiem`, nhà `/var/empty` không bao giờ bị đụng); nhà là bước riêng, chỉ khi `--xoa-nha`, chỉ khi user đã gỡ và nhà còn đúng inode đã ghi → `sudo rm -rf /Users/<u>`; trường sổ đi vào lệnh sudo được kiểm dạng (`_hop_le`). `dscl` lỗi khác "không có bản ghi" (`eDSRecordNotFound`) → `OSError`, không suy "không còn". Tên user ngoài `USER_RE` bị từ chối ngay lúc lập kế hoạch cài (gỡ được về sau). Thư mục kiểm của trạm mà chủ không còn là UID mong đợi → dừng, không chown; user có thư mục kiểm chưa gỡ được thì giữ user (không để thư mục mồ côi UID). Regression: `tests/test_cai_nha_tho.py` (8 ca), `tests/test_go_cai_lai.py` (9 ca), `tests/test_dinh_danh_cai.py` (3 ca). Còn lại cho S6: hành vi `sysadminctl -addUser` với nhà (tự tạo hay không, có đụng `-home /var/empty` không), thông báo `dscl` khi không có user, `-keepHome` giữ nguyên tại chỗ.

**R6 (C01) — THIẾT KẾ + MÃ + REGRESSION ĐÃ CÓ (Task 11, harness Task 12); gate S6 vẫn đóng tới khi Task 9 bước 3b, 5, 6 đạt; kẽ hở còn lại ở rủi ro (a).** Xem mục "Vòng đời cách ly của `tram-kiem` (C01)". Không root lúc chạy, sudo chỉ sang `tram-kiem` (D22), user riêng, sudoers `ALL` dưới `tram-kiem`, khoá một lần (D40) — giữ nguyên.

**R7 — phần harness ĐÃ CÓ (Task 12, Q03); phần cây tổng hợp CRLF/encoding CHƯA đổi.** `tram giao nghiem-thu-kiem` chạy đúng chuỗi production (`kiem_lai` → `chep_ban` → `repo_ban_chep` → `nhan_moi_truong` → `chay_mot_lenh` → `don_ban`) dưới principal thật, mỗi khẳng định một lệnh kiểm, hạn từng lệnh + hạn tổng, dọn dưới khoá kể cả khi lỗi, mã thoát 1 khi có ĐỎ; S6 bước 5, 6 dùng nó. Vì sao là lệnh `tram giao`: xem Task 12. Regression CRLF/`text`/`eol`/`working-tree-encoding` cho G32 chưa viết trong bản này (ngoài phạm vi Đại ca giao đợt r47) — G32 vẫn ghi giới hạn, rủi ro (h).

## Vòng đời cách ly của `tram-kiem` (C01)

Mối đe doạ: mã của commit N (chạy dưới `tram-kiem`) để lại thứ gì đó chạy/được đọc trong lần kiểm N+1 (commit khác, có thể dự án khác) — sửa cây hay kết quả của N+1, đọc `.env.testing` của N+1. `pgrep` rỗng chỉ là ảnh chụp: lịch hẹn giờ chưa tới lúc đếm.

**Lúc cài (`cai-dat-tho`, sudo một lần, có sổ R2):** `tram-kiem` tạo với `-home /var/empty` (root, 0755 — không ghi được), KHÔNG `createhomedir`. Lý do: user domain launchd tự nạp `~/Library/LaunchAgents` và công cụ đọc dotfile trong HOME; nhà không ghi được thì không cài cắm được ở đó. Không sửa `cron.deny`/`at.deny`: hai file có sẵn của Apple (máy dev: `cron.deny` = `Guest`, `at.deny` rỗng) — sửa file hệ thống không do trạm tạo trái mô hình sổ "tạo hoặc từ chối" (D40) và bản cập nhật macOS có thể ghi đè; thay vào đó kiểm lúc chạy (dưới). Không tạo `~/Library/LaunchAgents` root (nhà đã là `/var/empty`).

**Trước khi chép và khi dọn mỗi lần kiểm (`PrincipalKiem.don_sach(goc=…)` → `don_tram_kiem.don_sach`), dưới khoá kiểm lại.** Mỗi LƯỢT quét:

| Bước | Ai chạy | Bằng chứng chấp nhận | Sai → |
|---|---|---|---|
| giết | `pkill -KILL -U` và `-u` dưới `tram-kiem` | — (mã lệnh không dùng làm bằng chứng) | — |
| đếm | trạm `pgrep -U`, `pgrep -u` (không sudo) | cả hai mã 1 | mã 0: lượt sau; mã khác: `LoiBanChep` |
| launchd (TRƯỚC) | `launchctl print user/<uid>` và `…/<nhãn>` dưới `tram-kiem` (user khác không đọc được — đã đo: "Operation not permitted") | khối `services = {…}` đọc được; mọi nhãn có trong nền VÀ cùng vân tay (sha256 dòng `path`/`program`/`arguments`); dịch vụ lạ → `bootout user/<uid>/<nhãn>`, in lại | định dạng lạ, còn dịch vụ lạ, thiếu nền → `LoiBanChep` |
| phiên GUI | `launchctl print gui/<uid>` dưới `tram-kiem` | mã ≠ 0 VÀ "Could not find domain" | miền có thật hoặc lỗi khác → `LoiBanChep` |
| cron | `crontab -l` dưới `tram-kiem` (có thì `-r` rồi đọc lại) | mã ≠ 0 VÀ chữ "no crontab for" | `LoiBanChep` (sudo hỏng, bị cấm, còn crontab, treo 30 s) |
| at | trạm `find /usr/lib/cron/jobs -user tram-kiem` + `atq` dưới `tram-kiem` | cả hai rỗng; có → `atrm`, kiểm lại cả hai | còn → `LoiBanChep` |
| nhà | trạm `id -P`, `stat`, `ls -lde` | đúng `/var/empty`, chủ root, không g/o ghi, không ACL | `LoiBanChep` |
| gốc bản chép | trạm `kiem_thu_muc_goc` + `find <goc> -maxdepth 1` | của `tram-kiem`, không symlink; rỗng sau khi xoá (`find … -exec rm`) dưới `tram-kiem` | `LoiBanChep` |
| thư mục ghi-chung | trạm `find /private/tmp /private/var/tmp /Users/Shared /Library/Caches -maxdepth 1 -user tram-kiem` | không mục nào (trừ gốc và cha của gốc) sau khi xoá dưới `tram-kiem` | `LoiBanChep` |
| thư mục riêng | `getconf DARWIN_USER_DIR/TEMP_DIR/CACHE_DIR` dưới `tram-kiem` | dưới `/var/folders/`; rỗng sau khi xoá | `LoiBanChep` |
| đếm lần cuối | trạm `pgrep` | cả hai mã 1 | còn → lượt sau |

`don_sach` chỉ trả về khi HAI lượt LIÊN TIẾP sạch (không tiến trình, không phải gỡ lịch nào); tối đa 6 lượt rồi `LoiBanChep`. Lịch được gỡ TRƯỚC khi đếm tiến trình trong mỗi lượt (hàng trăm job KeepAlive luôn có tiến trình sống không chặn được việc gỡ; `bootout` giết luôn tiến trình của job). Lượt nào phải gỡ lịch → sau khi đã gỡ và xác nhận vẫn ném `CoLichHenGio` (con `LoiBanChep`): ở bước dọn CUỐI lần kiểm, `kiem_lai` bắt lỗi này và trả `KetQuaKiemLai(dat=False, loi="lich-hen-gio")` — vòng tick ghi `kiem.lai` không đạt và tạo escalation như các lỗi kiểm lại khác (không thử lại mãi, không chặn dự án); ở bước dọn ĐẦU (sót từ trước) thì ném ra vòng tick, đếm lỗi, vòng sau chạy trên máy đã sạch. Mọi lệnh dưới `tram-kiem` sau bước "đếm" chạy khi KHÔNG còn tiến trình nào của nó — binary hệ thống, đường dẫn tuyệt đối, môi trường sudo chỉ giữ `BIEN_GIU`. Lệnh quá 30 s (vd hộp thoại quyền) → `LoiBanChep`.

**Nền launchd** (`tram giao chup-nen-lich`, S6 bước 3b): giữ khoá kiểm lại; giết và xác nhận không còn tiến trình; không có crontab/việc `at` (có → từ chối chụp); in từng nhãn kèm dòng chương trình, cảnh báo nhãn không phải `com.apple.*` hay chương trình ngoài `/System/`, `/usr/libexec/`, `/usr/sbin/`, `/usr/bin/`; nền rỗng (miền chưa có) cũng cảnh báo; đã có nền thì phải `--ghi-de`; chờ `dong-y`.

**Trong lần kiểm:** lệnh kiểm chạy qua `ban_chep.boc_nha` = `/usr/bin/env HOME=<bản chép>.nha TMPDIR=<bản chép>.nha/tmp/ <lệnh>` — HOME/TMPDIR mới (0700, của `tram-kiem`), dọn cùng bản chép. `~/.npmrc`, cache jest/composer, XDG… của lần trước không còn để công cụ tự đọc.

**`tram-kiem` còn tự hẹn được gì, và vì sao không lọt:**
- cron, at: cài được (allow/deny mặc định của Apple) — bị phát hiện, gỡ, lần kiểm không được công nhận; không gỡ được thì dừng;
- `launchctl bootstrap user/<uid>`, `launchctl submit`: cài được vào miền user của chính nó (chưa đo được ở đây) — phát hiện bằng nền nhãn + vân tay chương trình; job giả nhãn Apple (bootout nhãn thật rồi `submit -l` cùng nhãn) khác vân tay → lạ;
- chuỗi (cron cài lại launchd, launchd cài lại cron): launchd quét trước; mọi lượt phải gỡ đều làm lại cả vòng; cần hai lượt sạch liên tiếp;
- LaunchAgents trong nhà: nhà `/var/empty` không ghi được, không ACL;
- `nohup`, double-fork, `setsid`: là tiến trình — `pkill -U/-u` + `pgrep`; tiến trình setuid-`tram-kiem` do user khác chạy có euid `tram-kiem` → `-u`;
- tệp cho lần sau tự đọc: HOME/TMPDIR mới mỗi lần; gốc bản chép phải rỗng; mục của `tram-kiem` trong thư mục ghi-chung và thư mục riêng bị xoá;
- `periodic`: chỉ chạy script root trong `/etc/periodic`, `/etc/*.local` — user không thêm được; login hook, `~/.ssh/authorized_keys` (shell `/usr/bin/false`, nhà không ghi được): không áp dụng.

**Kẽ hở còn lại — KHÔNG tuyên bố đã chứng minh (rủi ro (a)):** (1) một job tự xoá mình rồi cài nguồn khác đúng trong khoảng giữa hai lần đọc của cùng lượt, lặp lại được ở hai lượt liên tiếp — cần tính giờ chính xác, chỉ thu hẹp chứ không loại trừ được khi không có thao tác nguyên tử "không tiến trình + không lịch" mà không cần root; (2) nhãn nền KHÔNG nạp lúc quét bị job lạ chiếm sau đó — vân tay chỉ so với dịch vụ đang nạp; (3) thư mục ghi-chung KHÁC do phần mềm bên thứ ba tạo, mục sâu hơn cấp một trong thư mục người khác ghi được, bộ nhớ chia sẻ POSIX đặt tên đoán được, anh em của gốc khi cha của gốc thuộc `tram-kiem` (cấu hình Task 9 đặt gốc dưới `/Users/Shared`, cha của root); (4) miền `login/<asid>`. Phương án giảm thêm cần Đại ca chốt (xem "Câu hỏi r47"): thêm `tram-kiem` vào `cron.deny`/`at.deny` lúc cài (bỏ hẳn hai nguồn, nhưng sửa file có sẵn của Apple), và nếu S6 cho thấy `tram-kiem` được `launchctl bootout user/<uid>` cả miền thì dùng làm bước xoá nguyên tử.

**Chỉ chứng minh được trên macOS thật (S6 bước 6, harness `--tai-sinh`):** user domain của user không đăng nhập có tồn tại/nạp gì; `launchctl print user/<uid>` dưới `sudo -u tram-kiem` đọc được và định dạng khối `services`; `launchctl bootout` của chính nó được phép; `submit`/`bootstrap` từ `sudo -u` rơi vào miền nào; thông báo đúng của `crontab -l` khi không có crontab và việc `crontab -`/`-r` có bật hộp thoại quyền (trên máy dev, khi chạy thử plan, `crontab -` không TTY bị treo tới hết hạn 120 s — xem "Ghi chú kiểm plan (r47)"); `atq` định dạng; chủ file trong `/usr/lib/cron/jobs`; `sysadminctl -addUser -home /var/empty` không đổi chủ `/var/empty`; thư mục ghi-chung trên máy B.

## Câu hỏi r47 cho Đại ca (không chọn thay — mỗi câu kèm đề xuất)

1. **Nhà của `tram-kiem` là `/var/empty`** (root, không ghi được, không `createhomedir`; lệnh kiểm nhận HOME/TMPDIR mới mỗi lần) — HỢP ĐỒNG MỚI của C01. *Đề xuất:* đồng ý; S6 bước 3 kiểm `/var/empty` không đổi chủ.
2. **Lần kiểm mà `don_sach` cuối phải gỡ lịch hẹn giờ → kết quả "không đạt", lỗi `lich-hen-gio`, tạo escalation** (thay vì thử lại mãi hoặc công nhận). Commit có test hợp lệ dùng `crontab`/`launchctl`/`at` cũng rơi vào đây. *Đề xuất:* đồng ý — Đại ca/QC đọc escalation; dự án cần test như vậy thì sửa test chạy giả.
3. **Có thêm `tram-kiem` vào `/usr/lib/cron/cron.deny` và `at.deny` lúc cài không** (bỏ hẳn hai nguồn; nhưng là sửa file có sẵn của Apple — cần thêm loại tài nguyên "dòng trong file" vào sổ, bản cập nhật macOS có thể ghi đè). *Đề xuất:* chưa làm; quyết sau S6 bước 6 — nếu cron/at cài được dưới `tram-kiem` thì thêm (một task nhỏ).
4. **Nền launchd do Đại ca chụp bằng lệnh riêng (`tram giao chup-nen-lich`, chờ `dong-y`)**, chụp lại sau cập nhật macOS. *Đề xuất:* đồng ý.
5. **`chay_mot_lenh` (mã 3a-1) có thể treo vô hạn sau SIGKILL khi lệnh chạy dưới `sudo` có pty** (review C01 vòng 2) — ngoài phạm vi 3c. *Đề xuất:* tách một lát nhỏ sửa trước S6 (hạn chờ cuối, trạm tự `killpg` tiến trình `sudo` con của mình), Em lập bead.
6. **R7 — regression cây CRLF/`text`/`eol`/`working-tree-encoding` cho G32** chưa làm trong r47. *Đề xuất:* giao cùng lát ở câu 5, trước S6 bước 5.

## Ghi chú kiểm plan (16/10/2026, bản r47)

Bản sao: `git clone` cục bộ của repo, `checkout 793facb` (`main` sau review Codex đợt 5), `UV_OFFLINE=1 uv sync` (không mạng). **N₀ = 2100** (`uv run pytest -q`, 159 s). Script trích **từ chính file plan này** (`kiem_plan.py` của bản D40: file mới theo dòng "`đường dẫn` (mới…):", khối `diff` qua `git apply --check` rồi `git apply`, script chèn theo mốc của Task 8), áp theo đợt `T1, T3` → `T5, T10` → `T6, T7` → `T8, T11` → `T12`; mỗi task: áp test → lệnh Run của Step 2 → áp mã → lệnh Run đầu của Step 4; cuối đợt chạy cả bộ. Mọi bản vá cũ (T1, T3, T5, T7, T10) vẫn `git apply --check` sạch trên `793facb`. Máy: macOS 15.6.1 (Darwin 24.6), Python 3.12.15, git 2.56.0, bsdtar 3.5.3. Không `sudo`/`dscl`/`sysadminctl`/`launchctl` ghi/`crontab`, không tạo user.

| Task | Step 2 (thật) | Step 4 (thật) |
|---|---|---|
| 1 | `1 error in 0.06s` | `7 passed in 0.03s` |
| 3 | `2 errors in 1.63s` | `39 passed in 12.37s` |
| 5 | `2 errors in 1.13s` | `62 passed in 4.41s` |
| 10 | `7 failed, 34 passed in 13.83s` | `41 passed in 14.55s` |
| 6 | `4 errors in 1.19s` | `48 passed in 3.25s` |
| 7 | `1 error in 0.11s` | `24 passed in 3.16s` |
| 8 | `2 errors in 0.84s` | `38 passed in 2.82s` |
| 11 | `10 failed, 28 passed, 30 errors in 6.25s` | `68 passed in 11.37s` |
| 12 | `1 error in 0.06s` | `15 passed in 5.14s` |

Cả bộ: N₀ = **2100** → **2114** (đợt 1, N₀ + 14) → **2138** (đợt 2, N₀ + 38) → **2179** (đợt 3, N₀ + 79) → **2222** (đợt 4, N₀ + 122) → **2225** (đợt 5, N₀ + 125).

Kiểm thêm khi viết bản r47:
- Q01: chạy `tests/test_so_cai_tho.py` với `so_cai_tho.py` bản bị chặn (nối thẳng, không khoá, một `os.write`) → 5 failed — regression bắt đúng lỗi review.
- C01 (đột biến, mỗi lần bỏ một bước của lượt quét rồi chạy `tests/test_don_tram_kiem.py tests/test_don_tep_tram_kiem.py`): bỏ `don_cron` → 5 failed; bỏ `don_at` → 2 failed; bỏ `don_launchd` → 8 failed; bỏ `kiem_nha` → 2 failed; bỏ `don_tep` → 2 failed. Bỏ `boc_nha` trong `kiem_lai` → `tests/test_ban_chep_nha.py` 1 failed.
- Review đối kháng (doubt-driven, ngữ cảnh mới, chỉ đọc + test hệ giả) hai vòng cho Q01/Q02 và hai vòng cho C01/Q03; mọi phát hiện Chặn/Quan trọng đã sửa hoặc ghi thành rủi ro có tên (a), (e), (g), (k)–(m) và "Để sau". Không chạy review khác mô hình (ngữ cảnh không tương tác).
- **Sự cố khi viết plan (Đại ca cần biết):** một bản nháp đầu của test harness chạy kịch bản cài lịch dưới CHÍNH user `hungle` (`boc` đồng nhất) — lệnh `crontab -` bị treo (không TTY; có thể đã bật hộp thoại quyền trên màn hình) tới hết hạn 120 s rồi bị giết cả nhóm; các lệnh `at`/`launchctl` sau nó không chạy. Đã kiểm ngay sau đó: `crontab -l` → "no crontab for hungle", `atq` rỗng, `launchctl print user/501` và `gui/501` không có nhãn `nghiem-thu`, không còn tiến trình liên quan. Đã sửa: harness từ chối `--tai-sinh` với kịch bản thật khi `boc` đồng nhất hoặc principal là user đang chạy; test chỉ đọc nội dung kịch bản.

## Ghi chú kiểm plan (16/10/2026, bản D40)

Chạy lại toàn bộ sau khi thêm Task 10. Bản sao: `git clone` cục bộ của repo, `checkout 66058f9` (mã `tram/`, `tests/` giống hệt `4a907cc`), `UV_OFFLINE=1 uv sync` (không mạng). Script trích **từ chính file plan này** (file mới theo dòng "`đường dẫn` (mới…):", khối `diff` qua `git apply --check` rồi `git apply`, script chèn theo mốc của Task 8), áp theo đợt `T1, T3` → `T5, T10` → `T6, T7` → `T8`; mỗi task: áp test → lệnh Run của Step 2 → áp mã → lệnh Run đầu của Step 4; cuối đợt chạy cả bộ. Máy: macOS Darwin 24.6, Python 3.12.15, git 2.56.0 (Homebrew; Apple git 2.39.5 ở `/usr/bin/git`), bsdtar 3.5.3. Không `sudo`/`dscl`/`sysadminctl`, không tạo user.

| Task | Step 2 (thật) | Step 4 (thật) |
|---|---|---|
| 1 | `1 error` | `7 passed` |
| 3 | `2 errors` | `39 passed` |
| 5 | `2 errors` | `62 passed` |
| 10 | `7 failed, 34 passed` | `41 passed` |
| 6 | `2 errors` | `33 passed` |
| 7 | `1 error` | `24 passed` |
| 8 | `1 error` | `21 passed` |

Cả bộ: N₀ = **1994** → **2008** (đợt 1) → **2032** (đợt 2) → **2058** (đợt 3) → **2067** (đợt 4) — đúng `N₀ + 14`, `N₀ + 38`, `N₀ + 64`, `N₀ + 73`. Riêng Task 10 trên `main` sau đợt 1 (chưa có T5): **2015** = `N₀ + 21`. Task 10 không làm đỏ test nào của T5–T8 (kiểm lại giờ chạy thêm ba lệnh git mỗi lần; cả bộ ~134 giây như trước).

## Ghi chú kiểm plan (16/10/2026, bản D22 — số trước D40)

Script `kiem_plan.py` trích ngược **từ chính văn bản plan này** (file mới theo dòng "`đường dẫn` (mới)", khối `diff`, script chèn theo mốc), áp lên bản `git archive 4a907cc` sạch (N₀ = 1994) theo đúng thứ tự đợt; mỗi task: áp test → chạy lệnh Step 2 → áp mã → chạy lệnh Step 4; cuối đợt chạy cả bộ. Mọi bản vá qua `git apply`; script mốc in `đã chèn go-cai-dat-tho`. Máy: macOS Darwin 24.6, Python 3.12.15, git 2.56, bsdtar 3.5.3. Test không chạy `sudo`/`dscl`/`sysadminctl` thật, không tạo user.

| Task | Step 2 (thật) | Step 4 (thật) |
|---|---|---|
| 1 | `1 error` | `7 passed` |
| 3 | `2 errors` | `39 passed` |
| 5 | `2 errors` | `62 passed` |
| 6 | `2 errors` | `33 passed` |
| 7 | `1 error` | `24 passed` |
| 8 | `1 error` | `21 passed` |

Cả bộ: 1994 → **2008** (đợt 1) → **2025** (đợt 2) → **2051** (đợt 3) → **2060** (đợt 4). Bản soạn riêng (code tuần tự T1→T8 trước khi viết plan) cũng ra 2060. Bản D40 thay các số này (thêm 7 test của Task 10).

Ghi chú kiểm plan bản cũ (15/10, helper root, 1987 → 2055) là lịch sử của thiết kế đã bị D22 thay — không còn hiệu lực.

## Bổ sung review đợt 4 — R1/R2 (đã xử lý ở bản 16/10)

**R1 (helper root, Codex F01) — THAY bởi D22.** Đại ca chốt không dùng root: không còn helper, ACL/chmod, `trao_quyen`/`thu_quyen`, dòng sudoers `(root)`. Các ca F01 còn áp dụng (đổi cây sau khi kiểm, symlink trong archive, tiến trình `tram-kiem` tái sinh, dọn lỗi thì fail-closed, hai lần kiểm lại đồng thời) đã thành test ở Task 3, 5, 7 — bảng "Ca F01/F02". Ca hardlink/thiết bị/FIFO và chmod/chown bằng root không còn áp dụng.

**R2 (hoàn tác an toàn, Codex F02) — đã viết đủ ở Task 6 (journal, định danh, cài có sổ) và Task 8 (gỡ).** Thiết kế: sổ `so-cai.jsonl` chỉ ghi thêm + fsync; `du_dinh` trước lệnh; `da_tao` chỉ khi quan sát thấy đúng định danh mong đợi (user mang mã id trong RealName → lưu UID + GeneratedUID; file → sha256; thư mục → inode); thứ có sẵn mà sổ không ghi → từ chối cài; gỡ chỉ khi còn đúng định danh `da_tao`; đối soát mọi `du_dinh` dở ở đầu cài và gỡ; thư mục root gỡ cuối, lỗi chỉ cảnh báo; lặp lại gỡ ra kế hoạch rỗng. Sổ v1 `da-cai.json` của bản cũ chưa từng được cài nên không có đường đọc.

> **Task R3 — ĐÃ CODE 15/10 (D21), ghép `main` `bedcea6`; tên `lai` ĐÃ CHỐT D34.** Nội dung dưới đây giữ nguyên văn để tham chiếu; KHÔNG giao lại.

## Bổ sung review đợt 4 — Task R3: công bố lai theo D4

Mã snapshot chỉ có `cong_bo.phuong_an` toàn cục. Sổ tay không thể thực hiện D4 chỉ bằng cấu hình hai máy khác nhau. Task này bổ sung vào 3c để có chủ sở hữu, **không đổi D4**, không thực thi S7. Tên giá trị cấu hình `lai` là hợp đồng kỹ thuật mới đề xuất; cần chốt tên trước ghép, chính sách lai đã chốt.

**Files:** sửa `tram/cau_hinh/cong_bo.py`, `tram/cong_bo/nguon.py`; thêm `tram/cong_bo/nguon_lai.py`, `tests/test_cong_bo_lai.py`. Không sửa `da_push`, CAS hay fencing. `may_id` tới `lay` đã qua `kiem_thuoc_may`, không lấy lựa chọn từ payload thợ. Map `kho_tho` chỉ liệt kê máy cục bộ B; các máy từ xa đã xác thực dùng ref tạm. Không fallback từ kho B sang origin nếu fetch B lỗi.

Bước RED — test đầy đủ (4 ca) vào `tests/test_cong_bo_lai.py`:

```python
from pathlib import Path

import pytest

from tram.cau_hinh.cong_bo import nap_cau_hinh_cong_bo
from tram.cong_bo.nguon import NguonKhoTho, NguonRefTam, chon_nguon


def test_nap_lai_can_map_kho(tmp_path):
    p = tmp_path / "cau-hinh.yaml"
    p.write_text("cong_bo:\n  phuong_an: lai\n  kho_tho: {B: /Users/tram-tho/tram/kho}\n")
    cb = nap_cau_hinh_cong_bo(p)
    assert cb.phuong_an == "lai"
    p.write_text("cong_bo: {phuong_an: lai}\n")
    with pytest.raises(ValueError):
        nap_cau_hinh_cong_bo(p)


def test_lai_chon_theo_may_khong_giu_trang_thai_request(tmp_path, monkeypatch):
    p = tmp_path / "cau-hinh.yaml"
    p.write_text("cong_bo:\n  phuong_an: lai\n  kho_tho: {B: /Users/tram-tho/tram/kho}\n")
    n = chon_nguon(nap_cau_hinh_cong_bo(p))
    monkeypatch.setattr(NguonKhoTho, "lay", lambda self, kho, **kw: "local-" + kw["may_id"])
    monkeypatch.setattr(NguonRefTam, "lay", lambda self, kho, **kw: "remote-" + kw["may_id"])
    kw = dict(du_an="hr", ref_tam="tram/luot/hr-1/1", giao_id="g-1", timeout=1)
    assert n.lay(Path("/k"), may_id="B", **kw) == "local-B"
    assert n.lay(Path("/k"), may_id="C", **kw) == "remote-C"
    assert n.lay(Path("/k"), may_id="B", **kw) == "local-B"


def test_local_loi_khong_fallback_remote(tmp_path, monkeypatch):
    from tram.cong_bo.nguon_lai import NguonLai
    monkeypatch.setattr(NguonKhoTho, "lay", lambda *a, **kw: None)
    monkeypatch.setattr(NguonRefTam, "lay", lambda *a, **kw: pytest.fail("không fallback"))
    n = NguonLai({"B": tmp_path})
    assert n.lay(tmp_path, may_id="B", du_an="hr", ref_tam="r", giao_id="g", timeout=1) is None


def test_don_remote_van_qua_cas(tmp_path, monkeypatch):
    from tram.cong_bo.nguon_lai import NguonLai
    goi = []
    def don(self, kho, **kw):
        goi.append((kho, kw))
        return ["tram/luot/hr-1/1"]
    monkeypatch.setattr(NguonRefTam, "don_cu", don)
    assert NguonLai({"B": tmp_path}).don_cu(tmp_path, bead_id="hr-1", luot=2, timeout=1) == ["tram/luot/hr-1/1"]
    assert goi == [(tmp_path, {"bead_id": "hr-1", "luot": 2, "timeout": 1})]
```

Bước GREEN — file `tram/cong_bo/nguon_lai.py` đầy đủ:

```python
"""D4: nguồn theo máy đã xác thực; không fallback nguồn hoặc đổi trạng thái giữa request."""
from tram.cong_bo.nguon import NguonKhoTho, NguonRefTam


class NguonLai:
    ten = "lai"

    def __init__(self, kho_tho):
        self.kho_tho = dict(kho_tho)
        self.local = NguonKhoTho(self.kho_tho)
        self.remote = NguonRefTam()

    def lay(self, kho, *, may_id, du_an, ref_tam, giao_id, timeout):
        nguon = self.local if may_id in self.kho_tho else self.remote
        return nguon.lay(kho, may_id=may_id, du_an=du_an, ref_tam=ref_tam, giao_id=giao_id, timeout=timeout)

    def don_cu(self, kho, *, bead_id, luot, timeout):
        # Dọn ref remote cũ cả khi lượt mới chạy B; don_cu chỉ xoá ref cũ bằng CAS.
        return self.remote.don_cu(kho, bead_id=bead_id, luot=luot, timeout=timeout)
```

Hai thay đổi chính xác trong `tram/cau_hinh/cong_bo.py`: `PHUONG_AN = ("ref-tam", "kho-tho", "lai")`; đổi điều kiện `if pa == "kho-tho" and not kho:` thành `if pa in ("kho-tho", "lai") and not kho:` và thông báo thành `phương án kho-tho/lai cần cong_bo.kho_tho`. Thay toàn bộ `chon_nguon` trong `tram/cong_bo/nguon.py` bằng:

```python
def chon_nguon(cb: CauHinhCongBo):
    if cb.phuong_an == "lai":
        from tram.cong_bo.nguon_lai import NguonLai
        return NguonLai(cb.kho_tho)
    if cb.phuong_an == "ref-tam":
        return NguonRefTam()
    if cb.phuong_an == "kho-tho":
        return NguonKhoTho(cb.kho_tho)
    return None
```

Khi triển khai: test mới + toàn bộ `tests/test_cong_bo*.py`, test `da_push`/thu hồi/CAS và suite gốc; kiểm hai request B/C cùng trạm, cùng dự án theo hai lượt. Test adapter không thay S7: quyền remote, push treo và thu hồi giữa CAS vẫn phải chứng minh trên repo nháp. Cập nhật docstring hai phương án cũ để ghi D4; không đổi default None hay tự bật nguồn.

**Sơ đồ/số test:** R3 độc lập T1–T8, ghép trước S7; thêm 4 ca, dự kiến phần có mã đầy đủ N₀+72 thay N₀+68. R1/R2 còn thiếu thiết kế/mã, **không có tổng cuối toàn lát được chốt**; không cộng test giả cho chúng. T9 chỉ sau R1/R2, T1–T8 và quyền chạy thật; S7 còn cần R3. Không nghiệm thu root bằng fixture giả.


## Phụ lục review Codex đợt 6 — cổng kỹ thuật còn đóng

Các neo trong `REVIEW-CODEX.md` thuộc ZIP đầu vào; phần này ưu tiên hơn chữ “đầy đủ/đã giải quyết” về C01 và Q03 ở bản r47. Không thay D1–D44; không thực hiện lệnh trong tài liệu.

### C01 — vòng quét chưa tạo ranh giới cách ly giữa các lần kiểm

Bằng chứng chính là thuật toán `_sot`: chỉ nhìn mục cấp một có owner `tram-kiem` trong bốn thư mục chung. Một thư mục cha do trạm/người khác sở hữu nhưng cho `tram-kiem` ghi (ví dụ thư mục dấu 0777 mà chính harness tạo) chứa tệp của lần kiểm trước thì không bị quét; HOME mới không xóa dữ liệu đó. `login/<asid>`, POSIX shared memory và lịch tự chuyển nguồn cũng chưa được đóng. Đây là khoảng trống của invariant G6/G22/G25, không được đổi tên thành “đã chứng minh” bằng số test. Không có kết luận khai thác trên máy thật.

Cần thiết kế ranh giới cưỡng chế: chặn mọi nơi ghi/nguồn thực thi ngoài phạm vi có thể thu hồi, hoặc vòng đời principal/miền cô lập mới cho từng lượt; phương án phải giữ D22/D40 hoặc xin Đại ca đổi quyết định rõ ràng. Chưa tự chọn deny-file/root helper/VM. Sáu câu r47 không tự trở thành chấp thuận. C01 **chưa có mã sửa đầy đủ**, không cộng test giả. S6 chỉ là bước kiểm một thiết kế đã có ranh giới; không dùng thử tác vụ thật trên máy chủ để thay thiết kế.

### C02 — harness timeout chưa bảo đảm dọn; sự cố cron chưa được ngăn bằng UID

`_nghiem_thu_kiem` dùng daemon thread rồi `join(timeout)`. Hết hạn chỉ return 1: không hủy thread, không giết/chờ process tree, không bảo đảm `finally` của `nghiem_thu` chạy trước CLI thoát. `chay_mot_lenh._ket_thuc` vẫn `p.wait()` vô hạn. Guard `pk.ten == getpass.getuser()` dựa tên môi trường, không so UID từ cơ sở user với UID tiến trình thực; `boc(["x"]) != ["x"]` chỉ chứng minh argv khác, không chứng minh đã đổi principal. Test không được chạy script cài lịch thật chỉ vì guard này có trong mã.

Trước T12/T9: cần runner ở tiến trình con quản lý được; hạn thời gian cho kill/wait cuối; xác minh UID thực dưới đúng wrapper trước bất kỳ thao tác lịch; lỗi/timeout phải thu hồi lịch/process và báo cleanup không xác nhận được, không giải phóng gate. Tests dùng runner giả có spy chứng minh mọi ca sai UID/timeout không gọi cron/at/launchctl thật; một test tiến trình con treo trong sandbox không được dùng tài khoản người vận hành. Chưa có thiết kế/mã TDD đầy đủ cho tất cả phần này, T12/T9 giữ khóa.

Không sửa lịch máy của Đại ca trong review. “Đã dọn sạch” trong ghi chú r47 là lời bàn giao lịch sử, chưa được reviewer xác minh hiện trạng.

### Q01 — lỗi lệnh dọn bị coi là rỗng (đã sửa văn bản T11)

Bản cũ bỏ returncode của getconf, lệnh find/rm và find xác nhận `DARWIN_USER_*`: stdout rỗng với mã lỗi có thể đi qua. T11 nay kiểm cả returncode, có 3 test runner giả; lỗi nào cũng dừng. Sửa này không đóng C01.

### Ghi chú vận hành và Q01/Q02 cũ

- Q01 cũ: tách bytes trước decode, lưu/cắt tail dưới khóa rồi write-all; Q02 cũ: user/home là hai receipt và retry riêng. Đã có mã/regression ở plan; chưa xác minh crash/APFS/sysadminctl thật. Không thấy lỗi cũ còn nguyên sau sửa.
- Số baseline 2100 thuộc `793facb`, không phải `54af13d`. 2242 là lời bàn giao snapshot mới; đo lại khi triển khai, cộng delta 128 dự kiến, không copy mốc 2225 cũ thành mục tiêu mới.
- R7 CRLF/encoding còn chưa có regression; không công nhận “cây đúng commit” cho trường hợp ngoài phạm vi đã kiểm. Giữ gate.
- Sơ đồ: T1/T3 → T5/T10 → T6/T7 → T8/T11 (+3 ca sửa ở đây) → **T12 sau C02** → **T9 sau C01/C02, Q02 hạn mức, R7 và quyết định r47**. Không chạy đồng thời các task cùng ghi `noi_that.py`; 1a-2 T4–T6 áp sau chuỗi 3c.
