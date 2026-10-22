# Lát V2c — cách ly và chứng cứ: probe từng nguồn, attestation hồ sơ, ống bản chép, SIGTERM — Implementation Plan

> **Review cuối 18/10/2026, HEAD `3c2b46c`:** đã sửa nguyên văn B-T6 để ngắt giữa lúc cài/trả handler vẫn trả đủ cả hai handler (R3-02); giữ nguyên `hoan()` của A. Hai ca test bổ sung CHƯA CHẠY. Số RED/GREEN và `diff -r` bên dưới là bằng chứng tác giả của bản TRƯỚC sửa này. B vẫn áp sau toàn bộ A, gồm sửa vòng cuối; không thay lại `chay_han_tong`. Kết luận và thứ tự ghép: `REVIEW-CODEX-dot8-vong3.md`.

> **For agentic workers:** REQUIRED SUB-SKILL: Use ai-skills:subagent-driven-development (recommended) or ai-skills:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Trạng thái: PLAN, bản sửa theo Codex review gộp vòng 2 (18/10/2026: R2-02, R2-03 — phần B của §4.1; xem mục "Phản hồi review vòng 2" cuối plan); vòng 1 (B01, B02, B04) giữ như đã đóng, B03 đóng hẳn ở vòng này.** B-T6/T7/T8 viết lại TRÊN cây đã có plan A T1–T8 (`plan/ab-tich-hop`, `main` `f4fa3a8`): một cơ chế hoãn ngắt (`ngat.hoan` của A), một hợp đồng sở hữu (`so_huu` của A, thay "H-A03"), một bản thân hàm `chay_gioi_han`/`chay_han_tong` (của A-T4) — B chỉ thêm `stdin=`, `term_thanh_ngat`, ống bản chép, CLI nghiệm thu. Đã chạy RED→GREEN THẬT theo thứ tự ghép cuối (A-T1→T8, B-T1→T9) rồi hoàn nguyên; áp lại toàn bộ khối mã hai plan lên bản sạch và `diff -r` khớp. CHƯA áp vào `main`; vùng kill list → chờ Đại ca duyệt + Codex review. KHÔNG có bước OS nào được chạy (G3/G4 ĐÓNG).

**Goal:** Hoàn thiện các task plan V2 còn thiếu implementation về cách ly/chứng cứ: V2-4 (dot7-Q03, `bs-2bd.1.14`) chứng cứ TỪNG nguồn lịch, thiếu dấu/quá hạn = không đạt; V2-5 (dot7-Q04, `bs-2bd.1.15`) hồ sơ Seatbelt khớp TOÀN BỘ byte bản đã duyệt qua manifest của installer; V2-6a (`bs-863.18`) H1 `stdin=` + ống `git archive | tar` có chủ hai đầu; phần còn lại của `bs-863.19` (SIGTERM ở CLI cha, ngắt lần hai giữ dấu).

**Architecture:** (1) `chung_cu_probe.py` là parser + producer thuần (không OS): mỗi nguồn in `probe:<n>:bat-dau` / `ly-do:<n>:<mã hữu hạn>` / `probe:<n>:ket:<mã>` — bộ phân loại chạy trong chính khối shell, chỉ in một mã thuộc `LY_DO`, đầu ra thô bị xoá, không bao giờ ra log/kết quả (INV-001); consumer harness đổi màu theo bằng chứng, mục tổng "đủ bằng chứng S6" luôn đỏ cho tới biên bản OS G4. (2) `quyen_kiem.manifest_ho_so` sinh hồ sơ + manifest từ CÙNG input; installer cài manifest SAU hồ sơ qua cùng sổ; runtime `ho_so_cai(goc)` đọc manifest root (O_NOFOLLOW, fstat trên fd, cha của root), sinh lại hồ sơ, so từng byte, đối chiếu TRAM_HOME/gốc hiện hành. (3) `ngat.py` (plan A tạo `hoan()` — MỘT cơ chế hoãn ngắt): B thêm `term_thanh_ngat` (SIGTERM → `NgatTerm(KeyboardInterrupt)`, SIGINT → `KeyboardInterrupt`, chỉ CLI cha); trong ranh giới SỞ HỮU (spawn, preflight có spawn, thu hồi) tín hiệu chỉ được ghi rồi phát lại QUA handler này khi ra khỏi khối, tức sau khi con đã ở danh sách sở hữu (`chu`) / sau khi thu hồi xong. `chay_gioi_han` là thân hàm của A-T4 (selector, hạn trước spawn, `_don` đóng từng ống rồi luôn thu hồi); B thêm `stdin=`. (4) `ong_chep.chay_ong`: nguồn `git archive` qua primitive P1, đích `tar` qua `chay_gioi_han` với `timeout=` là phần còn lại của MỘT hạn tính trước khi chuẩn bị nguồn; nguồn luôn thu hồi trong `finally`; nguồn chưa xác nhận thu hồi thắng mọi lỗi khác, không nối chuỗi lỗi. (5) `lenh_nghiem_thu` cài `term_thanh_ngat` từ đầu (phủ preflight `xac_minh_uid`); `chay_han_tong` là thân hàm của A-T4 (tạo dấu + spawn trong `try` và `hoan()`, thu hồi trong `hoan()`) — B không sửa. Primitive `vong_doi`/`so_huu`/`ngat.hoan` thuộc plan A — B dùng qua **hợp đồng sở hữu** (`tram/kiem/so_huu.py`, thay "H-A03" của bản trước).

**Tech Stack:** Python 3.12 stdlib (`json`, `hashlib`, `os`, `stat`, `signal`, `subprocess`), pytest 8. Không phụ thuộc mới.

**Spec / nguồn:** [plan V2](2026-10-17-lat-v2-va-sau-review-dot7.md) V2-4, V2-5, V2-6a, V2-1 (acceptance SIGTERM); review Codex đợt 7 (`.handover/review-codex-dot7/REVIEW-CODEX.md`) dot7-Q03, dot7-Q04, dot7-C02, bảng bead §6 (.18/.19); [phụ lục cổng đợt 7](../handovers/2026-10-17-cong-sau-review-dot7.md) (ma trận G4); [D45–D53](../quyet-dinh/2026-10-16-chot-sau-review-dot6.md) (D45, D48, D49, D53); spec 3 §7.3; [plan P1](2026-10-16-lat-p1-vong-doi-tien-trinh.md) (primitive `vong_doi`, `chay_gioi_han`).

## Global Constraints

- **Kill list (`docs/AGENT_RULES.md` §2) — STOP:** plan chạm mục 3 *Cách ly agent* (`tram/kiem/chay_gioi_han.py`, `tram/kiem/han_tong.py`, `tram/kiem/ngat.py` mới, `tram/giao_viec/kiem_lai.py`, `tram/tho/quyen_kiem.py` — hồ sơ Seatbelt, `tram/giao_viec/cong_that.py`/`ban_chep.py`/`ong_chep.py`/`nghiem_thu_kiem.py`/`lenh_nghiem_thu.py` — cổng và harness kiểm lại) và mục 6 *Cài dịch vụ, sửa hệ thống* (`tram/chu/cai_dat_kiem.py` — installer thêm một file root). **Không code khi Đại ca chưa duyệt plan này VÀ Codex chưa review** (gom zip một lần cùng các plan V2 khác — `DEVELOPMENT_PLAYBOOK.md`). Duyệt plan không phải quyền chạy installer, sudo hay kịch bản lịch.
- **N₀ = 2809** (`pytest --collect-only` trên `main` `f4fa3a8`, đo 18/10 với PATH chặn host); plan B áp SAU plan A (A-T1…T8: **2947**). Plan B **+115 → 3062** (đã đo: áp đủ A-T1…T8 rồi B-T1…T8 thì `3062 passed`); trong đó xoá 2 hàm test cũ (4 ca) của `ho_so_cai` tìm chuỗi, thay bằng 19 ca attestation. Đo lại trước Task 1; lệch thì tìm nguyên nhân.
- TDD: test trước, chạy thấy đỏ (thông báo ở bước RED là kết quả THẬT trong worktree), viết mã, chạy thấy xanh. Mã trong plan là nguyên văn file/bản vá đã chạy — áp đúng như in; bản vá áp theo NỘI DUNG (`git apply --3way` hoặc tay), không mù số dòng, vì các plan V2 khác có thể ghép trước.
- File nguồn ≤ ~120 dòng, dòng ≤ 120 ký tự Unicode. Sau plan: `tram/giao_viec/cong_that.py` 122, `tram/giao_viec/ban_chep.py` 122 (bằng trước plan), `tram/giao_viec/lenh_nghiem_thu.py` 122, `tram/giao_viec/nghiem_thu_kiem.py` 120, `tram/tho/quyen_kiem.py` 112, `tram/kiem/chay_gioi_han.py` 110 (bản A-T4 + `stdin=`), `tram/kiem/ngat.py` 75 (bản A-T2 + `term_thanh_ngat`), `tram/giao_viec/ong_chep.py` 43; test lớn nhất mới `tests/test_ban_chep_pipeline_han.py` 123, `tests/test_ho_so_cai_attest.py` 122, `tests/test_han_tong_ngat.py` 121, `tests/test_ong_chep_uu_tien.py` 112.
- Thông báo lỗi và chứng cứ không chép nội dung hồ sơ/manifest, argv, stdout/stderr, byte môi trường (dot6-Q06, INV-001): lý do probe là mã hữu hạn (`LY_DO`), lỗi thay thế dùng `from None`. Test có sentinel `BIMAT`/`BI_MAT_ENV` ở cả stdout lẫn stderr.
- **Phụ thuộc plan A (V2-0) — áp SAU A-T1…T8:** B không sửa `vong_doi.py`, `so_huu.py`, `cay_tien_trinh.py`, `danh_tinh.py`, `han_tong.py`; sửa `ngat.py` (thêm cuối file) và `chay_gioi_han.py` (chỉ `stdin=`) của A. Mọi spawn của B theo **hợp đồng sở hữu** của A: `khoi_chay(..., chu=)` bắt buộc, `Nhom` vào `chu` trước mọi lối ra, người gọi thu hồi `chu` trong `finally`; `LoiThuHoi` = KHÔNG xác nhận (con có thể còn) → dấu/cổng giữ đóng — B không còn dựa vào lời hứa "ném = không để lại con".
- **Test không bao giờ:** chạy `sudo`, `crontab`, `at`, `batch`, `launchctl`, `sandbox-exec`, `kill`/`pkill` theo tên, `chmod`/`chown` file hệ thống; đọc `/usr/local/tram`; gửi tín hiệu ra ngoài tiến trình test. Tín hiệu "thật" chỉ là `signal.raise_signal` vào CHÍNH tiến trình test khi handler đang cài là của `hoan`/`term_thanh_ngat`/handler canh của test (`chan_sigterm_mac_dinh` — không bao giờ để SIGTERM mặc định giết pytest); còn lại gọi thẳng handler đang cài. Chủ/quyền root do `lstat`/`fstat` GIẢ trả. Tiến trình thật chỉ là `git archive`, `/bin/sh` chạy `echo`/`exit N`, `python -c` của chính user test trong `tmp_path`, tự thu hồi.
- Chạy test luôn với PATH chặn host (`AGENT_RULES.md` §13): `PATH="$C/bin:$PATH" PYTHONPATH="$C/plugin" UV_OFFLINE=1 uv run pytest -p chan_host -q …`; nhật ký chặn phải không thêm dòng.
- Giữ `bat_ghi: false` (HR), `giao_viec.bat: false`. Không đổi D45–D53, mockup, quyết định. Không push/merge; một task một commit trên nhánh task.

## Bảng G — điều plan bảo đảm và bằng chứng

| # | Bảo đảm | Ở đâu | Bằng chứng offline | Còn chờ OS |
|---|---|---|---|---|
| G1 | Mỗi nguồn lịch có dấu bắt đầu + mã thoát của riêng nó; thiếu/trùng/sai thứ tự/không số/ngoài 0–255 = chưa chứng minh (đỏ) | `chung_cu_probe.doc_probe`, `muc_lich` | `test_thieu_hong_trung_khong_phai_bi_chan[*]` (9 ca) | — |
| G2 | Mã ≠ 0 chỉ là "thất bại" (vàng), không tự là "Seatbelt chặn"; mục tổng "đủ bằng chứng S6" luôn đỏ → harness `--tai-sinh` mã thoát 1 | `nghiem_thu_kiem._tai_sinh` | `test_thieu_dau_ma_127_hay_qua_han_khong_cho_harness_dat[*]`, `test_tai_sinh_lot_thi_do_…` | biên bản G4: lý do OS + đối chứng dương |
| G3 | Đầu ra của lệnh cài không giả được dòng dấu và KHÔNG ra log/kết quả: lý do chỉ là mã thuộc `LY_DO` do bộ phân loại trong khối sinh, tệp đầu ra bị xoá; dòng `ly-do:` lạ/trùng/thiếu → `khong-ro`; không tạo được tệp đầu ra → không có `ket` (đỏ), không giả mã thất bại (B01) | `boc_probe`, `ly_do`, `_tai_sinh` | `test_khoi_probe_khong_chep_stdout_stderr_tho`, `test_phan_loai_ly_do_huu_han[*]` (5), `test_dong_ly_do_la_hay_trung_…[*]` (5), `test_dong_ly_do_mang_byte_la_khong_vao_ket_qua_harness`, `test_khong_co_tmpdir_thi_khong_co_ket` | `/bin/sh` thật dưới hồ sơ; biên bản sạch G4 |
| G4 | Hồ sơ đã cài = từng byte bản sinh lại từ manifest root; không tìm chuỗi; comment giả, CRLF, thêm/bớt một dòng đều đóng cổng | `cong_that.ho_so_cai`, `quyen_kiem.ho_so_tu_manifest` | `test_ho_so_lech_mot_byte_…[*]` (6), `test_ba_dong_hai_chuoi_cu_khong_con_du` | — |
| G5 | Mẫu mong đợi KHÔNG lấy từ chính hồ sơ đang kiểm; manifest chặt (khoá, kiểu, phiên bản mã, digest); bộ sinh đổi mà quên tăng phiên bản → đóng | `ho_so_tu_manifest` | `test_manifest_sai_thi_tu_choi_…[*]` (15), `test_bo_sinh_doi_ma_quen_tang_phien_ban_thi_dong` | — |
| G6 | Không dùng `Path.home()`: `nha_quan_ly` chỉ từ manifest root do installer ghi; TRAM_HOME/gốc so với cấu hình HIỆN HÀNH | `ho_so_cai(goc)`, `dung_cong` | `test_goc_hoac_tram_home_doi_thi_phai_cai_lai`, `test_dung_cong_…` | — |
| G7 | File root: cha thật của root không ai khác ghi, O_NOFOLLOW, fstat trên fd đã mở, file thường root 0644, ≤ 64 KiB | `doc_tep_root` | `test_symlink_…`, `test_chu_hoac_quyen_root_sai[*]`, `test_thu_muc_cha_…[*]` | `ls -ld /usr/local` trên máy B |
| G8 | Installer cài manifest SAU hồ sơ, cùng sổ; hỏng giữa hai file → sổ đúng, runtime đóng | `phan_kiem` | `test_manifest_cai_sau_ho_so_…`, `test_cai_hong_giua_ho_so_va_manifest_…`, `test_manifest_thieu_hong_hoac_cu_hon_ho_so` | cài thật G3.0 |
| G9 | `stdin=` truyền thẳng Popen, loại trừ `input` trước spawn; quá hạn không kèm dữ liệu; thân hàm của A-T4: từ lúc có `Nhom`, MỌI lối ra (xong/quá hạn/lỗi đọc/lỗi selector/đóng ống lỗi/ngắt) đóng TỪNG ống rồi LUÔN thu hồi; không xác nhận → `LoiThuHoi` thay lỗi thường, ngắt vẫn là ngắt (B03, R2-03) | `chay_gioi_han` (A-T4 + B-T6) | `test_stdin_…`, `test_input_va_stdin_loai_tru_…`, `test_stdin_ong_nguon_qua_han_…`, `test_chay_gioi_han_ngat.py` (6: SIGTERM THẬT ngay sau Popen qua hai lớp, `_doc` ném ×4, SIGTERM lần hai lúc thu hồi); của A: `test_so_huu_ong.py` | — |
| G10 | Ống `git archive \| tar`: nguồn có chủ (nhóm riêng, spawn trong `hoan()`), đích quá hạn/lỗi/thoát sớm/không chạy/không thu hồi → nguồn vẫn thu hồi; MỘT hạn tính trước khi chuẩn bị nguồn — đích nhận phần còn lại, hết hạn thì không chạy đích; nguồn CHƯA xác nhận thu hồi thắng mọi lỗi khác (`from None`), cổng đóng vì bản chép (B02); không `wait()` trần | `ong_chep.chay_ong`, `ban_chep`, `kiem_lai` | `test_dich_qua_han_loi_hoac_khong_chay_…[*]`, `test_nguon_treo_khi_dich_xong_…`, `test_nguon_khong_xac_nhan_thu_hoi_thang_moi_loi_khac[*]` (4), `test_dich_loi_va_nguon_chua_thu_hoi_thi_cong_dong_vi_nguon`, `test_dich_nhan_phan_han_con_lai_…`, `test_dich_khong_xac_nhan_…` | `tar` dưới `sudo -u tram-kiem` thật |
| G11 | `LoiThuHoi` của lệnh bản chép thành `LoiBanChep` (tick chỉ bắt OSError — không sập vòng tick); kill của principal tới mọi lệnh bản chép | `ban_chep._chay`, `kiem_lai` | `test_dich_khong_xac_nhan_…`, `test_kiem_lai_truyen_kill_…` | — |
| G12 | SIGTERM/Ctrl-C ở CLI cha ở MỌI đoạn đã/đang sở hữu con (preflight dò UID, tạo dấu + spawn, chờ, thu hồi, dọn) → con có chủ, thu hồi + dọn trong `finally` rồi mới trả (143/130); tín hiệu ở ranh giới sở hữu được ghi rồi phát lại qua `term_thanh_ngat` khi `Nhom` đã ở `chu`/thu hồi xong; `khoi` ném lỗi khác OSError → dấu giữ; ngắt lần hai giữa lúc dọn → dấu giữ, cổng đóng; kill bị từ chối/gốc treo + SIGTERM → dấu giữ, `Nhom` còn trong `chu`; handler cũ (SIGTERM + SIGINT) khôi phục (B03, R2-02) | `ngat` (A + B), `han_tong` (A-T4), `lenh_nghiem_thu` | `test_ngat.py` (6), `test_lenh_nghiem_thu_ngat.py` (4), `test_ngat_ab.py` (4, SIGTERM THẬT qua hai lớp), `test_han_tong_ngat.py` (+5) | SIGKILL không hứa gì; Popen hỏng nội bộ sau fork (không phải lỗi exec) — plan A Rủi ro 1 |

## Ranh giới phần offline và phần OS

| Phần | Ở plan này | Ở đâu chứng minh |
|---|---|---|
| Parser/producer probe, màu và mã thoát harness | Code + test (Task 1–2) | offline |
| Seatbelt THẬT chặn từng nguồn, IPC/mạng/Mach/XPC | **Không code, không chạy** | Cổng G4, mục "Bước cổng" cuối plan — harness OS riêng phải soạn + review sau G3 |
| Attestation byte hồ sơ, manifest, installer | Code + test (Task 3–5) | offline; cài thật ở G3.0 |
| Ống `git archive \| tar` có chủ, `stdin=`, một ngân sách hạn | Code + test (Task 6–7) | offline; `tar` dưới principal thật ở G4 |
| SIGTERM/Ctrl-C ở CLI cha, hoãn ngắt ở ranh giới sở hữu | Code + test (Task 6, 8; cơ chế `hoan` + hợp đồng của plan A) | offline (`raise_signal` vào chính tiến trình test, có handler canh; hoặc gọi thẳng handler đang cài); G4 chỉ quan sát lại (TERM bị bỏ qua, ngắt lần hai) |
| Lỗi sau Popen (theo dõi gốc hỏng, kill bị từ chối, gốc treo) | Plan A sửa (R2-01/R2-02: không gặt nhánh lỗi, `Nhom` luôn vào `chu`, `LoiThuHoi` = không xác nhận); B chỉ giữ phía an toàn (dấu giữ) | test của A (`test_so_huu*.py`); test phía an toàn của B: `test_ngat_ab.py`, `test_han_tong_ngat.py` |

## File Structure

```
tram/giao_viec/
  chung_cu_probe.py     (mới, T1)  boc_probe, doc_probe, ly_do, muc_lich, LY_DO — chứng cứ từng nguồn, lý do mã hữu hạn
  kich_ban_nghiem_thu.py (sửa, T2) kich_ban_tai_sinh: mỗi nguồn một khối boc_probe, bỏ `-da-cai`
  nghiem_thu_kiem.py    (sửa, T2)  _tai_sinh: màu theo chứng cứ + mục tổng "đủ bằng chứng S6"
  cong_that.py          (sửa, T5)  doc_tep_root, ho_so_cai(goc) so từng byte; dung_cong truyền goc
  ong_chep.py           (mới, T7)  chay_ong: git archive | tar có chủ hai đầu, một ngân sách hạn, ưu tiên chưa thu hồi
  cay_kiem.py           (sửa, T7)  nguon_archive → Nhom qua khoi_chay (kill cục bộ)
  ban_chep.py           (sửa, T7)  _chay qua chay_gioi_han (kill, timeout), chep_ban dùng chay_ong(loi=LoiBanChep)
  kiem_lai.py           (sửa, T7)  truyền kill cho chep_ban/nhan_moi_truong/don_ban
  lenh_nghiem_thu.py    (sửa, T8)  term_thanh_ngat TỪ ĐẦU lệnh cha; preflight trong hoan(); _don bắt BaseException
tram/tho/quyen_kiem.py  (sửa, T3)  MANIFEST_KIEM, PHIEN_BAN_HO_SO, manifest_ho_so, ho_so_tu_manifest
tram/chu/cai_dat_kiem.py (sửa, T4) cài manifest root:wheel 0644 sau hồ sơ, cùng sổ
tram/kiem/
  ngat.py               (sửa, T6)  của A-T2 (`hoan`); B thêm NgatTerm, term_thanh_ngat (SIGTERM + SIGINT)
  chay_gioi_han.py      (sửa, T6)  của A-T4; B chỉ thêm stdin= (loại trừ input, chọn vao)
  han_tong.py           (KHÔNG sửa)  thân hàm cuối của A-T4; B-T8 chỉ thêm test
tests/
  test_chung_cu_probe.py (mới, T1) · test_nghiem_thu_kiem.py (sửa, T2) · test_manifest_ho_so.py (mới, T3) ·
  test_cai_dat_tho_kiem.py, test_go_cai_dat_tho.py (sửa, T4) · test_ho_so_cai_attest.py (mới), test_cong_that.py
  (sửa, T5) · test_ngat.py, test_chay_gioi_han_ngat.py (mới), test_chay_gioi_han.py (sửa, T6) ·
  test_ban_chep_pipeline_han.py, test_ong_chep_uu_tien.py (mới, T7) · test_lenh_nghiem_thu_ngat.py, test_ngat_ab.py
  (mới), test_han_tong_ngat.py (sửa, T8)
```

## Sơ đồ đợt, số test, giao nhau với plan khác

Task cùng đợt không sửa chung file. Cột "tổng" là số thu thập THẬT khi áp theo thứ tự T1…T8 trên `f4fa3a8` + plan A T1–T8 (2947).

| Đợt | Task | File chính | Test + | Tổng sau task |
|---|---|---|---|---|
| 1 | T1 | `chung_cu_probe` | +27 | 2974 |
| 2 | T2 | `kich_ban_nghiem_thu`, `nghiem_thu_kiem` | +5 | 2979 |
| 1 | T3 | `quyen_kiem` | +23 | 3002 |
| 2 | T4 | `cai_dat_kiem` (+ test gỡ) | +2 | 3004 |
| 2 | T5 | `cong_that` | +15 (19 mới − 4 cũ) | 3019 |
| 1 | T6 | `ngat`, `chay_gioi_han` (trên bản A) | +15 | 3034 |
| 2 | T7 | `ong_chep`, `cay_kiem`, `ban_chep`, `kiem_lai` | +15 | 3049 |
| 2 | T8 | `lenh_nghiem_thu` (+ test `han_tong` trên bản A) | +13 | 3062 |
| 3 | T9 | phụ lục cổng (docs) | 0 | 3062 |

**Giao nhau và thứ tự ghép với plan khác:**

| Plan / agent | File chung | Cách ghép |
|---|---|---|
| V2-1 (`han_tong.py`, đã ghép `a06eefb`) | `tram/kiem/han_tong.py`, `tests/test_han_tong_ngat.py` (T8) | `han_tong.py` có MỘT bản thân hàm cuối do plan A-T4 viết (R2-03) — B KHÔNG sửa; T8 chỉ thêm test cuối `tests/test_han_tong_ngat.py` (A không đụng file test này). |
| V2-0 / plan A (`ngat.py`, `so_huu.py`, `vong_doi.py`, `chay_gioi_han.py`, `han_tong.py`, `danh_tinh.py`, người gọi `khoi_chay`) | B áp SAU A-T1…T8. T6 sửa `ngat.py` (thêm cuối file) và `chay_gioi_han.py` (chỉ `stdin=`) — hunk viết trên đúng bản của A; T7 dùng `khoi_chay(chu=)`, `thu_hoi_con_lai`; T8 dùng `chay_han_tong` của A-T4. | Thứ tự ghép cuối (đã chạy thật): A-T1→T8, rồi B-T1→T9. Không còn "rebase/bỏ hunk trùng": bản vòng 2 của B-T6/T7 không ghép được với hợp đồng A (`TypeError … 'chu'`), đã thay hoàn toàn. |
| V2-6b/V2-6c (`tram/tho/*`, `kiem_am`, `theo_doi`) | Không. Có thể dùng `chay_gioi_han(stdin=)` — thêm tham số tương thích ngược | Thứ tự tuỳ ý. |
| V2-3 (inventory env, đã ghép trên `7921f26`) | `tram/giao_viec/lenh_nghiem_thu.py`: bản vá T8 tạo TRÊN mã đã có V2-3 — giữ nguyên import + callback `cac_du_an_quan_sat` ở `_don`/`_trong` (không quay về chỉ dự án bật ghi); T8 chỉ đổi `except` trong `_don` và tách thân `lenh_nghiem_thu` thành `_chay`. `tram/giao_viec/kiem_principal.py`: T5 đổi `dung_cong` bên trong (thêm `partial(ho_so_cai, goc)`) — không chạm chữ ký | Áp theo nội dung; chạy lại `tests/test_lenh_nghiem_thu*.py`, `tests/test_cong_that.py` (đã chạy: xanh trong lần đo cả bộ). |
| V2-2, V2-7 | Không | — |

## Tasks

### Task 1: Parser + producer chứng cứ từng probe, lý do là mã hữu hạn (V2-4 phần offline, dot7-Q03; B01 vòng 1)

**Đợt:** 1 · **Phải xong trước:** Task 2 · **Bead:** bs-2bd.1.14. Harness cũ coi nguồn nào không in `<nguồn>-da-cai` là XANH: lệnh thiếu, sai cú pháp, treo quá 20 s hay shell chết đều thành "bị chặn". Mỗi nguồn cần dấu bắt đầu + mã thoát riêng; thiếu = đỏ; mã ≠ 0 chỉ là vàng chờ proof OS. **B01 (vòng 1):** bản trước lấy 200 byte đầu ra làm `ly-do` — cắt ngắn/thay newline không lọc bí mật. Nay bộ phân loại chạy NGAY trong khối shell (dưới principal), chỉ in một mã thuộc tập hữu hạn `LY_DO` (`eperm`/`eacces`/`khong-thay`/`khac`/`trong`) rồi xoá tệp đầu ra; bên đọc chỉ nhận mã trong `LY_DO`, dòng lạ/trùng/thiếu → `khong-ro`. Byte stdout/stderr của lệnh không bao giờ ra log, kết quả hay biên bản. Mã lý do chỉ là gợi ý — kết luận "Seatbelt chặn" vẫn chỉ ở biên bản G4 (quy tắc biên bản sạch ở mục "Bước cổng").

**Files:**
- Create: `tests/test_chung_cu_probe.py`
- Create: `tram/giao_viec/chung_cu_probe.py`

**Interfaces:**
- Consumes: —
- Produces: `chung_cu_probe.boc_probe(nguon, lenh) -> str` (khối shell nền; `nguon` khớp `[a-z]{1,16}`, sai → ValueError), `doc_probe(log, nguon) -> int | None`, `ly_do(log, nguon) -> str` (luôn là một khoá của `LY_DO`), `muc_lich(log, nguon) -> tuple[bool | None, str]` (False đỏ, None vàng, không bao giờ True; chuỗi chỉ ghép từ `LY_DO`), `LY_DO: dict[str, str]`, `NGUON_RE`.

- [ ] **Step 1: Viết test thất bại**

`tests/test_chung_cu_probe.py` (mới, nguyên văn):

```python
"""V2-4 (dot7-Q03) + B01 (vòng 1): chứng cứ TỪNG probe — thiếu/trùng/hỏng dấu là chưa chứng minh, mã ≠ 0 không tự là
"bị chặn"; lý do chỉ là mã HỮU HẠN do bộ phân loại sinh, byte stdout/stderr của lệnh không bao giờ ra log/kết quả.
Khối shell chỉ chạy lệnh GIẢ (`exit N`, `echo`) bằng `/bin/sh` của user test trong tmp_path — không lệnh lịch nào."""
import subprocess

import pytest

from tram.giao_viec.chung_cu_probe import LY_DO, boc_probe, doc_probe, ly_do, muc_lich


@pytest.mark.parametrize("s", ["kich-ban-bat-dau\n", "probe:cron:bat-dau\n",
    "probe:cron:ket:126\n", "probe:cron:bat-dau\nprobe:cron:ket:x\n",
    "probe:cron:bat-dau\nprobe:cron:ket:1\nprobe:cron:ket:1\n",
    "probe:cron:ket:1\nprobe:cron:bat-dau\n", "probe:cron:bat-dau\nprobe:cron:ket:256\n",
    "probe:cron:bat-dau\nprobe:cron:ket:-1\n", "probe:cron:bat-dau\nprobe:cron:ket:1 \n"])
def test_thieu_hong_trung_khong_phai_bi_chan(s):
    assert doc_probe(s, "cron") is None
    assert muc_lich(s, "cron")[0] is False


def test_co_ma_nhung_khong_tu_ket_luan_seatbelt():
    assert doc_probe("probe:cron:bat-dau\nprobe:cron:ket:126\n", "cron") == 126
    assert doc_probe("probe:cron:bat-dau\nprobe:cron:ket:0\n", "cron") == 0
    assert muc_lich("probe:at:bat-dau\nly-do:at:eperm\nprobe:at:ket:126\n", "at") == (
        None, "lệnh thất bại (mã 126, lý do eperm — Operation not permitted) — chờ biên bản OS + đối chứng dương ở G4")
    assert muc_lich("probe:at:bat-dau\nprobe:at:ket:0\n", "at") == (False, "CÀI ĐƯỢC — hồ sơ không chặn")


@pytest.mark.parametrize("dong", ["ly-do:at:Operation not permitted BIMAT\n", "ly-do:at:eperm\nly-do:at:eperm\n", "",
                                  "ly-do:at:eperm BIMAT\n", "ly-do:at:\n"])
def test_dong_ly_do_la_hay_trung_thanh_khong_ro_khong_chep(dong):
    log = f"probe:at:bat-dau\n{dong}probe:at:ket:1\n"
    assert ly_do(log, "at") == "khong-ro" and "BIMAT" not in muc_lich(log, "at")[1]


def _chay(tmp_path, kb: str, tmpdir=True) -> str:
    env = {"PATH": "/usr/bin:/bin", **({"TMPDIR": str(tmp_path)} if tmpdir else {})}
    return subprocess.run(["/bin/sh", "-c", kb + "\nwait\n"], capture_output=True, text=True, env=env, timeout=10,
                          cwd=tmp_path).stdout


def test_khoi_probe_khong_chep_stdout_stderr_tho(tmp_path):
    log = _chay(tmp_path, boc_probe("cron", "echo BIMAT_OUT; echo BIMAT_ERR >&2; echo probe:cron:ket:0 >&2; exit 7"))
    assert doc_probe(log, "cron") == 7                          # đầu ra của lệnh không giả được dòng dấu
    assert "BIMAT" not in log and ly_do(log, "cron") == "khac" and "BIMAT" not in muc_lich(log, "cron")[1]
    assert not (tmp_path / "probe-cron").exists()               # tệp đầu ra thô bị xoá ngay trong khối
    assert doc_probe(_chay(tmp_path, boc_probe("at", "true")), "at") == 0


@pytest.mark.parametrize("lenh, ma", [("echo 'crontab: tmp: Operation not permitted' >&2; exit 1", "eperm"),
                                      ("echo 'at: Permission denied' >&2; exit 1", "eacces"),
                                      ("/khong/co/lenh-nay", "khong-thay"), ("exit 1", "trong"),
                                      ("echo 'Permission denied; Operation not permitted'; exit 1", "eperm")])
def test_phan_loai_ly_do_huu_han(tmp_path, lenh, ma):
    log = _chay(tmp_path, boc_probe("at", lenh))
    assert ly_do(log, "at") == ma and ma in LY_DO and doc_probe(log, "at") != 0


def test_khong_co_tmpdir_thi_khong_co_ket(tmp_path):
    log = _chay(tmp_path, boc_probe("submit", "exit 1"), tmpdir=False)
    assert "probe:submit:bat-dau" in log and doc_probe(log, "submit") is None


@pytest.mark.parametrize("ten", ["", "Cron", "cr on", "cron;rm", "a" * 17])
def test_ten_nguon_sai_dang(ten):
    with pytest.raises(ValueError):
        boc_probe(ten, "true")
```

- [ ] **Step 2: Chạy, thấy ĐỎ**

```bash
C=<thư mục PATH chặn host>; PATH="$C/bin:$PATH" PYTHONPATH="$C/plugin" UV_OFFLINE=1 uv run pytest -p chan_host -q tests/test_chung_cu_probe.py
```

Kết quả THẬT trên `main` `7921f26` (trước khi có mã của task):

```
ERROR tests/test_chung_cu_probe.py
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
1 error in 0.06s
```

(`ModuleNotFoundError: No module named 'tram.giao_viec.chung_cu_probe'`.) Đỏ ở mức hành vi — tái hiện B01 bằng mã `chung_cu_probe.py` của bản plan TRƯỚC (lấy 200 byte đầu ra), chỉ thêm bảng `LY_DO` để test import được:

```
E       AssertionError: assert ('BIMAT' not in 'probe:cron:...cron:ket:7\n'
E           ly-do:cron:BIMAT_OUT BIMAT_ERR probe:cron:ket:0          ← stdout + stderr thô vào log
E       AssertionError: assert ('Operation no...rmitted BIMAT' == 'khong-ro'   ← dòng lý do lạ được chép nguyên
E       AssertionError: assert ('crontab: tmp...not permitted' == 'eperm'
FAILED tests/test_chung_cu_probe.py::test_co_ma_nhung_khong_tu_ket_luan_seatbelt
FAILED tests/test_chung_cu_probe.py::test_dong_ly_do_la_hay_trung_thanh_khong_ro_khong_chep[…]   (×5)
FAILED tests/test_chung_cu_probe.py::test_khoi_probe_khong_chep_stdout_stderr_tho
FAILED tests/test_chung_cu_probe.py::test_phan_loai_ly_do_huu_han[…]                             (×5)
12 failed, 15 passed in 0.10s
```

- [ ] **Step 3: Viết mã**

`tram/giao_viec/chung_cu_probe.py` (mới, nguyên văn):

```python
"""Chứng cứ TỪNG nguồn lịch của kịch bản tái sinh S6 (V2-4, dot7-Q03; B01 vòng 1). Mỗi nguồn chạy trong một khối
riêng in đúng `probe:<nguồn>:bat-dau` rồi — SAU khi lệnh cài trả — `probe:<nguồn>:ket:<mã>`. Đầu ra của lệnh vào tệp
riêng trong `$TMPDIR` (không lẫn vào dòng dấu); bộ phân loại trong CHÍNH khối đó chỉ in MỘT mã lý do HỮU HẠN
`ly-do:<nguồn>:<mã>` (`LY_DO`) rồi xoá tệp — byte đầu ra không bao giờ ra stdout, vào kết quả hay bản ghi (INV-001).
Bên đọc chỉ nhận mã thuộc `LY_DO`; dòng lạ/thiếu/trùng → `khong-ro`, không chép. Mã lý do chỉ là GỢI Ý: Seatbelt chặn
hay thiếu công cụ/sai cú pháp chỉ phân biệt được bằng biên bản G4 (Đại ca xem log Sandbox + đối chứng dương; biên bản
ghi mã + kết luận, không dán đầu ra thô). Thiếu/trùng/sai thứ tự/không phải số/ngoài 0–255 = probe CHƯA HOÀN TẤT (đỏ)
— vắng dấu không bao giờ là "bị chặn"; mã khác 0 chỉ là "lệnh thất bại" (vàng)."""
import re

NGUON_RE = re.compile(r"[a-z]{1,16}")
LY_DO = {"eperm": "Operation not permitted", "eacces": "Permission denied", "khong-thay": "không thấy lệnh/tệp",
         "khac": "có đầu ra khác (không chép)", "trong": "không có đầu ra",
         "khong-ro": "dòng lý do thiếu/trùng/lạ (không chép)"}


def boc_probe(nguon: str, lenh: str) -> str:
    """Một khối nền cho MỘT nguồn. Không tạo được tệp đầu ra → khối dừng trước `ket` (đỏ), không giả mã thất bại.
    Phân loại theo thứ tự ưu tiên tăng dần (mẫu sau thắng): trong < khac < khong-thay < eacces < eperm."""
    if not NGUON_RE.fullmatch(nguon):
        raise ValueError(f"tên nguồn probe sai dạng: {nguon!r}")
    return (f'( echo probe:{nguon}:bat-dau; ra="${{TMPDIR:?}}/probe-{nguon}"; : >"$ra" || exit 0; '
            f'( {lenh} ) >"$ra" 2>&1; ma=$?; ld=trong; [ -s "$ra" ] && ld=khac; '
            "grep -qiE 'not found|no such file' \"$ra\" && ld=khong-thay; "
            "grep -qi 'permission denied' \"$ra\" && ld=eacces; "
            "grep -qi 'operation not permitted' \"$ra\" && ld=eperm; "
            f'rm -f "$ra"; echo ly-do:{nguon}:$ld; echo probe:{nguon}:ket:$ma ) &')


def doc_probe(log: str, nguon: str) -> int | None:
    dong = [s for s in log.splitlines() if s.startswith(f"probe:{nguon}:")]
    if len(dong) != 2 or dong[0] != f"probe:{nguon}:bat-dau":
        return None
    m = re.fullmatch(rf"probe:{re.escape(nguon)}:ket:([0-9]+)", dong[1])
    if m is None:
        return None
    ma = int(m.group(1))
    return ma if 0 <= ma <= 255 else None


def ly_do(log: str, nguon: str) -> str:
    """Mã lý do thuộc `LY_DO` — không bao giờ là chuỗi lấy từ log ngoài tập đó."""
    dong = [s[len(f"ly-do:{nguon}:"):] for s in log.splitlines() if s.startswith(f"ly-do:{nguon}:")]
    return dong[0] if len(dong) == 1 and dong[0] in LY_DO else "khong-ro"


def muc_lich(log: str, nguon: str) -> tuple[bool | None, str]:
    """(False, …) đỏ: chưa hoàn tất hoặc CÀI ĐƯỢC · (None, …) vàng: thất bại, chờ proof OS. Không bao giờ True."""
    ma = doc_probe(log, nguon)
    if ma is None:
        return False, "probe chưa hoàn tất (thiếu/trùng/hỏng dấu hoặc quá 20 s) — không chứng minh gì"
    if ma == 0:
        return False, "CÀI ĐƯỢC — hồ sơ không chặn"
    ld = ly_do(log, nguon)
    return None, f"lệnh thất bại (mã {ma}, lý do {ld} — {LY_DO[ld]}) — chờ biên bản OS + đối chứng dương ở G4"
```

- [ ] **Step 4: Chạy, thấy XANH**

```bash
C=<thư mục PATH chặn host>; PATH="$C/bin:$PATH" PYTHONPATH="$C/plugin" UV_OFFLINE=1 uv run pytest -p chan_host -q tests/test_chung_cu_probe.py
```

Kết quả THẬT: `27 passed in 0.12s`; nhật ký chặn host không thêm dòng.

- [ ] **Step 5: Commit**

```bash
git add tests/test_chung_cu_probe.py tram/giao_viec/chung_cu_probe.py
git commit -m "feat(v2-4): chứng cứ từng probe lịch, lý do là mã hữu hạn — không chép đầu ra (bs-2bd.1.14, dot7-Q03, B01)"
```

### Task 2: Producer/consumer harness dùng chứng cứ từng nguồn (V2-4; B01 vòng 1)

**Đợt:** 2 · **Phải xong trước:** — (cần Task 1) · **Bead:** bs-2bd.1.14. `kich_ban_tai_sinh` giữ nguyên các lệnh cài, bỏ `&& echo …-da-cai`, bọc mỗi nguồn bằng `boc_probe`. `_tai_sinh` tô màu theo `muc_lich`; setsid: thiếu dấu đỏ, mã 0 xanh khi `ra()` sạch, mã ≠ 0 vàng; thêm mục tổng "đủ bằng chứng S6" LUÔN đỏ (in_ket_qua coi vàng là mã 0 — không được để harness thoát 0 khi chưa có biên bản OS). **B01 (vòng 1):** mã của task không đổi so với bản trước — chi tiết mục chỉ ghép từ `muc_lich` (Task 1, chuỗi thuộc `LY_DO`); thêm một test khoá: kịch bản (hay mã agent) tự in `ly-do:` mang byte lạ và ghi stderr thì kết quả harness chỉ có `khong-ro`, không có byte đó.

**Files:**
- Modify: `tests/test_nghiem_thu_kiem.py`
- Modify: `tram/giao_viec/kich_ban_nghiem_thu.py`
- Modify: `tram/giao_viec/nghiem_thu_kiem.py`

**Interfaces:**
- Consumes: Task 1: `boc_probe`, `doc_probe`, `muc_lich`.
- Produces: `kich_ban_tai_sinh(dau) -> str` (mỗi nguồn của `NGUON` đúng một khối probe); `nghiem_thu(..., tai_sinh=True)` thêm mục `tái sinh: đủ bằng chứng S6` (đỏ); mục `tái sinh: hồ sơ chặn cài <n>` có thể VÀNG.

- [ ] **Step 1: Viết test thất bại**

`tests/test_nghiem_thu_kiem.py` (sửa — bản vá):

```diff
diff --git a/tests/test_nghiem_thu_kiem.py b/tests/test_nghiem_thu_kiem.py
index 1e5035f..c133a4b 100644
--- a/tests/test_nghiem_thu_kiem.py
+++ b/tests/test_nghiem_thu_kiem.py
@@ -51,19 +51,55 @@ def test_kich_ban_that_bi_tu_choi_duoi_nguoi_van_hanh_truoc_khi_spawn(tmp_path,
     assert not list(tmp_path.glob("tram-nghiem-thu-*")) and not list((tmp_path / "kiem").iterdir())
 
 
+def kb_gia(**ma) -> str:
+    """Kịch bản GIẢ chỉ `echo`: dấu probe từng nguồn theo `ma` (None = có bắt đầu, không có kết — treo/quá hạn)."""
+    dong = ["echo kich-ban-bat-dau"]
+    for n, m in ma.items():
+        dong += [f"echo probe:{n}:bat-dau", *([] if m is None else [f"echo probe:{n}:ket:{m}"])]
+    return "\n".join([*dong, "exit 0", ""])
+
+
 def test_tai_sinh_lot_thi_do_tung_nguon_va_dau_chay_sau_thu_hoi(tmp_path):
     ngu = []
 
     def lich_chay_trong_luc_cho(s):                                # một lịch "lọt" chạy trong lúc chờ → phải ĐỎ
         ngu.append(s)
         next(tmp_path.glob("tram-nghiem-thu-dau-*")).joinpath("cron").touch()
-    m, *_ = chay(tmp_path, tai_sinh=True, ngu=lich_chay_trong_luc_cho,
-                 kich_ban=lambda dau: "echo kich-ban-bat-dau\necho cron-da-cai\necho setsid-da-cai\nexit 0\n")
+    m, ds, *_ = chay(tmp_path, tai_sinh=True, ngu=lich_chay_trong_luc_cho,
+                     kich_ban=lambda dau: kb_gia(cron=0, at=126, submit=126, launchd=126, setsid=0))
     assert ngu == [300] and m["tái sinh: hồ sơ chặn cài cron"] == "do"
-    assert m["tái sinh: hồ sơ chặn cài at"] == m["tái sinh: hồ sơ chặn cài launchd"] == "xanh"
+    assert m["tái sinh: hồ sơ chặn cài at"] == m["tái sinh: hồ sơ chặn cài launchd"] == "vang"   # thất bại ≠ bị chặn
     assert m["tái sinh: quan sát đóng cổng khi lịch lọt"] == "do"     # cổng giả không đóng
     assert m["tái sinh: tiến trình setsid bị thu hồi ở ra()"] == "xanh"  # ra() của cổng giả không ném
     assert m["tái sinh: không gì chạy sau thu hồi"] == "do" and m["tái sinh: lần kiểm sau đạt"] == "do"
+    assert m["tái sinh: đủ bằng chứng S6"] == "do"
+
+
+@pytest.mark.parametrize("ma, mong, ss", [
+    ({}, ["do"] * 4, "do"),                                         # chỉ `kich-ban-bat-dau`: cũ là bốn nguồn XANH
+    (dict(cron=127, at=127, submit=127, launchd=127, setsid=127), ["vang"] * 4, "vang"),    # không có lệnh
+    (dict(cron=None, at=126, submit=126, launchd=126, setsid=0), ["do", "vang", "vang", "vang"], "xanh")])  # treo
+def test_thieu_dau_ma_127_hay_qua_han_khong_cho_harness_dat(tmp_path, ma, mong, ss):
+    m, ds, *_ = chay(tmp_path, tai_sinh=True, ngu=lambda s: None, kich_ban=lambda dau: kb_gia(**ma))
+    assert [m[f"tái sinh: hồ sơ chặn cài {n}"] for n in ("cron", "at", "submit", "launchd")] == mong
+    assert m["tái sinh: tiến trình setsid bị thu hồi ở ra()"] == ss
+    assert m["tái sinh: đủ bằng chứng S6"] == "do" and in_ket_qua(ds)[1] == 1
+
+
+def test_kich_ban_that_moi_nguon_mot_khoi_probe(tmp_path):
+    kb = kich_ban_tai_sinh(tmp_path / "dau")
+    for n in ("cron", "at", "submit", "launchd", "setsid"):
+        assert kb.count(f"echo probe:{n}:bat-dau;") == kb.count(f"echo probe:{n}:ket:$ma )") == 1
+    assert "-da-cai" not in kb and kb.startswith("echo kich-ban-bat-dau\n") and kb.endswith("sleep 20\nexit 0\n")
+
+
+def test_dong_ly_do_mang_byte_la_khong_vao_ket_qua_harness(tmp_path):
+    """B01: kịch bản (hay mã agent) tự in `ly-do:` mang byte lạ + stderr — kết quả chỉ có mã thuộc `LY_DO`."""
+    kb = kb_gia(cron=126, at=126, submit=126, launchd=126, setsid=0).replace(
+        "echo probe:at:ket:126", "echo 'ly-do:at:BIMAT_OUT'\necho BIMAT_ERR >&2\necho probe:at:ket:126")
+    m, ds, *_ = chay(tmp_path, tai_sinh=True, ngu=lambda s: None, kich_ban=lambda dau: kb)
+    assert m["tái sinh: hồ sơ chặn cài at"] == "vang" and "BIMAT" not in in_ket_qua(ds)[0]
+    assert "lý do khong-ro" in next(x.chi_tiet for x in ds if x.muc == "tái sinh: hồ sơ chặn cài at")
 
 
 def test_tai_sinh_khong_thay_dau_bat_dau_thi_khong_xanh_gi(tmp_path):
```

- [ ] **Step 2: Chạy, thấy ĐỎ**

```bash
C=<thư mục PATH chặn host>; PATH="$C/bin:$PATH" PYTHONPATH="$C/plugin" UV_OFFLINE=1 uv run pytest -p chan_host -q tests/test_nghiem_thu_kiem.py
```

Kết quả THẬT trên `main` `7921f26` + Task 1 (trước khi có mã của task):

```
E       AssertionError: assert ([300] == [300] ... 'xanh' == 'do'          ← cron thiếu `-da-cai` (vì probe mới) bị coi là XANH
E       AssertionError: assert ['xanh', 'xan...xanh', 'xanh'] == ['do', 'do', 'do', 'do']   ← chỉ `kich-ban-bat-dau`: bốn nguồn XANH
E       AssertionError: assert ['xanh', 'xan...xanh', 'xanh'] == ['vang', 'van...vang', 'vang']  ← mã 127
E       AssertionError: assert ['xanh', 'xan...xanh', 'xanh'] == ['do', 'vang', 'vang', 'vang']  ← cron treo
E           assert 0 == 1   (count 'echo probe:cron:ket:$ma )' trong kịch bản cũ)
FAILED tests/test_nghiem_thu_kiem.py::test_tai_sinh_lot_thi_do_tung_nguon_va_dau_chay_sau_thu_hoi
FAILED tests/test_nghiem_thu_kiem.py::test_thieu_dau_ma_127_hay_qua_han_khong_cho_harness_dat[ma0-mong0-do]
FAILED tests/test_nghiem_thu_kiem.py::test_thieu_dau_ma_127_hay_qua_han_khong_cho_harness_dat[ma1-mong1-vang]
FAILED tests/test_nghiem_thu_kiem.py::test_thieu_dau_ma_127_hay_qua_han_khong_cho_harness_dat[ma2-mong2-xanh]
E       AssertionError: assert ('xanh' == 'vang'                        ← dòng `ly-do:` lạ: nguồn `at` vẫn XANH ở mã cũ
FAILED tests/test_nghiem_thu_kiem.py::test_kich_ban_that_moi_nguon_mot_khoi_probe
FAILED tests/test_nghiem_thu_kiem.py::test_dong_ly_do_mang_byte_la_khong_vao_ket_qua_harness
6 failed, 3 passed in 4.78s
```

Ca `ma0` tái hiện đúng dot7-Q03: mã cũ cho bốn nguồn lịch XANH khi log chỉ có `kich-ban-bat-dau`. Test B01 mới xanh ngay với mã Task 2 của bản trước khi Task 1 đã sửa (consumer chỉ dùng `muc_lich`) — là regression khoá INV-001 ở mức harness.

- [ ] **Step 3: Viết mã**

`tram/giao_viec/kich_ban_nghiem_thu.py` (sửa — bản vá):

```diff
diff --git a/tram/giao_viec/kich_ban_nghiem_thu.py b/tram/giao_viec/kich_ban_nghiem_thu.py
index 628b45a..051bda4 100644
--- a/tram/giao_viec/kich_ban_nghiem_thu.py
+++ b/tram/giao_viec/kich_ban_nghiem_thu.py
@@ -6,6 +6,8 @@ của harness dựng bằng `git_nhap`/`commit_nhap` (không hook, không cấu
 import subprocess
 from pathlib import Path
 
+from tram.giao_viec.chung_cu_probe import boc_probe
+
 GIT = ("git", "-c", "core.hooksPath=/dev/null", "-c", "user.name=nghiem-thu", "-c", "user.email=nt@localhost",
        "-c", "commit.gpgSign=false")
 
@@ -24,22 +26,21 @@ NGUON = ("cron", "at", "submit", "launchd", "setsid")
 
 
 def kich_ban_tai_sinh(dau: Path) -> str:
-    """Thử cài mọi nguồn lịch mà mã agent dưới `tram-kiem` có thể cài; cài được thì in `<nguồn>-da-cai`, chạy được thì
-    tạo `dau/<nguồn>`. Mọi nguồn hẹn 121–180 s sau khi cài (cron/at theo ranh giới phút; submit/launchd/setsid 150 s) —
-    sau thu hồi của `ra()` — để dấu chỉ xuất hiện khi lọt THẬT. Dòng đầu in `kich-ban-bat-dau` (bằng chứng kịch bản đã
-    chạy). Mỗi lần cài chạy nền, chờ 20 s cho lệnh cài chậm in kết quả; còn treo thì bị thu hồi cùng lệnh kiểm."""
+    """Thử cài mọi nguồn lịch mà mã agent dưới `tram-kiem` có thể cài — mỗi nguồn một khối `boc_probe` (V2-4: dấu bắt
+    đầu + mã thoát + lý do OS của TỪNG nguồn); chạy được thì tạo `dau/<nguồn>`. Mọi nguồn hẹn 121–180 s sau khi cài
+    (cron/at theo ranh giới phút; submit/launchd/setsid 150 s) — sau thu hồi của `ra()` — để dấu chỉ xuất hiện khi lọt
+    THẬT. Dòng đầu in `kich-ban-bat-dau`. Các khối chạy nền, chờ 20 s; khối còn treo thì không có `ket` (đỏ) và bị thu
+    hồi cùng lệnh kiểm."""
     plist = ('<?xml version="1.0" encoding="UTF-8"?><plist version="1.0"><dict><key>Label</key><string>vn.tram.nghiem-'
              f'thu.launchd</string><key>ProgramArguments</key><array><string>/usr/bin/touch</string><string>{dau}/'
              'launchd</string></array><key>StartInterval</key><integer>150</integer></dict></plist>')
-    cai = [f'echo "$(date -v+3M +\'%M %H\') * * * /usr/bin/touch {dau}/cron" | crontab - && echo cron-da-cai',
-           f'echo "/usr/bin/touch {dau}/at" | at now + 3 minutes && echo at-da-cai',
-           f'launchctl submit -l vn.tram.nghiem-thu.submit -- /bin/sh -c "sleep 150; touch {dau}/submit" '
-           '&& echo submit-da-cai',
+    cai = [f'echo "$(date -v+3M +\'%M %H\') * * * /usr/bin/touch {dau}/cron" | crontab -',
+           f'echo "/usr/bin/touch {dau}/at" | at now + 3 minutes',
+           f'launchctl submit -l vn.tram.nghiem-thu.submit -- /bin/sh -c "sleep 150; touch {dau}/submit"',
            f"printf '%s' '{plist}' > \"$TMPDIR/nt.plist\" && "
-           'launchctl bootstrap "user/$(id -u)" "$TMPDIR/nt.plist" && echo launchd-da-cai',
-           f"/usr/bin/perl -MPOSIX -e 'fork and exit; POSIX::setsid(); sleep 150; system(\"touch\", \"{dau}/setsid\")' "
-           "&& echo setsid-da-cai"]
-    return "\n".join(["echo kich-ban-bat-dau", *(f"( {c} ) &" for c in cai), "sleep 20", "exit 0", ""])
+           'launchctl bootstrap "user/$(id -u)" "$TMPDIR/nt.plist"',
+           f"/usr/bin/perl -MPOSIX -e 'fork and exit; POSIX::setsid(); sleep 150; system(\"touch\", \"{dau}/setsid\")'"]
+    return "\n".join(["echo kich-ban-bat-dau", *map(boc_probe, NGUON, cai), "sleep 20", "exit 0", ""])
 
 
 def git_nhap(kho: Path, *a: str) -> str:
```

`tram/giao_viec/nghiem_thu_kiem.py` (sửa — bản vá):

```diff
diff --git a/tram/giao_viec/nghiem_thu_kiem.py b/tram/giao_viec/nghiem_thu_kiem.py
index ef39ea7..d776332 100644
--- a/tram/giao_viec/nghiem_thu_kiem.py
+++ b/tram/giao_viec/nghiem_thu_kiem.py
@@ -3,13 +3,12 @@ của `tram giao nghiem-thu-kiem` (CLI cha giữ hạn tổng — `lenh_nghiem_t
 qua `cong` (cổng lượt) và `boc_luot` (hồ sơ Seatbelt của lượt), `don_sach` = thu hồi theo UID, trên kho git NHÁP + môi
 trường kiểm GIẢ trong thư mục tạm của trạm (không dự án thật, không cần `giao_viec.bat`). Harness là chủ dấu hạn tổng
 `kiem-lai.dong` (`chu_dau=True`). Mỗi khẳng định là MỘT lệnh kiểm (`KHANG_DINH`). `--tai-sinh`: commit thứ hai thử cài
-lịch như mã agent; chỉ khi log có dấu `kich-ban-bat-dau` (kịch bản THẬT SỰ chạy — cổng đóng thì không xanh gì) mới
-khẳng định từng nguồn BỊ CHẶN, lọt thì quan sát đóng cổng, sau `cho` (≥ 240 s) không dấu nào chạy, lần kiểm sau vẫn
-đạt. Kịch bản lịch thật hay khẳng định exec `crontab` chỉ chạy khi `xac_minh_uid` chứng minh UID thực không phải người
-vận hành/root — kiểm TRƯỚC mọi spawn. Cuối cùng, dưới khoá, thu hồi theo UID rồi xem gốc rỗng; lỗi giữa chừng
-vẫn dọn."""
+lịch như mã agent; chỉ khi log có dấu `kich-ban-bat-dau` mới xét TỪNG nguồn qua `chung_cu_probe` (V2-4: thiếu dấu =
+đỏ, cài được = đỏ, thất bại = vàng chờ biên bản OS G4 — mục tổng "đủ bằng chứng S6" luôn đỏ, harness không tự đóng
+C01), lọt thì quan sát đóng cổng, sau `cho` (≥ 240 s) không dấu nào chạy, lần kiểm sau vẫn đạt. Kịch bản lịch
+thật hay khẳng định exec `crontab` chỉ chạy khi `xac_minh_uid` chứng minh UID thực không phải người vận hành/root —
+kiểm TRƯỚC mọi spawn. Cuối cùng, dưới khoá, thu hồi theo UID rồi xem gốc rỗng; lỗi giữa chừng vẫn dọn."""
 import os
-import re
 import shlex
 import shutil
 import subprocess
@@ -20,6 +19,7 @@ from pathlib import Path
 from tram.cau_hinh.du_an import DuAn, MoiTruongKiem
 from tram.duong_dan import tram_home
 from tram.giao_viec.ban_chep import LoiBanChep, giu_khoa
+from tram.giao_viec.chung_cu_probe import doc_probe, muc_lich
 from tram.giao_viec.kich_ban_nghiem_thu import KHANG_DINH, NGUON, commit_nhap, git_nhap, kich_ban_tai_sinh
 from tram.giao_viec.kiem_lai import kiem_lai
 from tram.kiem.danh_tinh import LoiDanhTinh, xac_minh_uid
@@ -102,14 +102,17 @@ def _tai_sinh(kiem, kho: Path, goc_sha: str, sha: str, kd: dict, dau: Path, kich
     log = nk.read_text(errors="replace") if nk.exists() else ""
     if "kich-ban-bat-dau" not in log:                # cổng đóng/lỗi trước khi chạy: không có gì được chứng minh
         return [_muc("tái sinh: lượt cài lịch đã chạy", False, str(loi or "log không có dấu bắt đầu"))]
-    cai = set(re.findall(r"([\w-]+)-da-cai", log))
-    lot = cai - {"setsid"}                          # fork + setsid được phép; bằng chứng là `ra()` thu hồi sạch
-    ra = [_muc(f"tái sinh: hồ sơ chặn cài {n}", n not in cai, "CÀI ĐƯỢC — hồ sơ không chặn" if n in cai else "bị chặn")
-          for n in NGUON if n != "setsid"]
-    ra.append(_muc("tái sinh: tiến trình setsid bị thu hồi ở ra()", loi is None if "setsid" in cai else None,
-                   str(loi or ("ra() sạch" if "setsid" in cai else "không fork được"))))
+    lich = {n: muc_lich(log, n) for n in NGUON if n != "setsid"}          # V2-4: chứng cứ TỪNG nguồn, không suy từ vắng
+    lot = [n for n in lich if doc_probe(log, n) == 0]  # fork + setsid được phép; bằng chứng là `ra()` thu hồi sạch
+    ra = [_muc(f"tái sinh: hồ sơ chặn cài {n}", *lich[n]) for n in lich]
+    ss = doc_probe(log, "setsid")
+    ra.append(_muc("tái sinh: tiến trình setsid bị thu hồi ở ra()", {None: False, 0: loi is None}.get(ss),
+                   str(loi or {None: "probe chưa hoàn tất", 0: "ra() sạch"}.get(ss, f"không fork được (mã {ss})"))))
     ra.append(_muc("tái sinh: quan sát đóng cổng khi lịch lọt", "CongDong" in str(loi) if lot else None,
                    str(loi or "không có lịch lọt để quan sát")))
+    vang = sum(v[0] is None for v in lich.values())
+    ra.append(_muc("tái sinh: đủ bằng chứng S6", False, f"{vang}/{len(lich)} nguồn chỉ 'thất bại' — chưa nguồn nào có "
+                   "biên bản OS G4 (lý do + đối chứng dương); harness không tự đóng C01"))
     ngu(cho)
     chay = sorted(p.name for p in dau.iterdir())
     ra.append(_muc("tái sinh: không gì chạy sau thu hồi", not chay, f"đã chạy: {chay} / chờ {cho:g} s"))
```

- [ ] **Step 4: Chạy, thấy XANH**

```bash
C=<thư mục PATH chặn host>; PATH="$C/bin:$PATH" PYTHONPATH="$C/plugin" UV_OFFLINE=1 uv run pytest -p chan_host -q tests/test_nghiem_thu_kiem.py tests/test_chung_cu_probe.py
```

Kết quả THẬT: `36 passed in 4.83s`; nhật ký chặn host không thêm dòng.

- [ ] **Step 5: Commit**

```bash
git add tests/test_nghiem_thu_kiem.py tram/giao_viec/kich_ban_nghiem_thu.py tram/giao_viec/nghiem_thu_kiem.py
git commit -m "fix(v2-4): harness tái sinh tô màu theo chứng cứ từng nguồn, mục tổng chờ biên bản OS (bs-2bd.1.14)"
```

### Task 3: Manifest hồ sơ Seatbelt: sinh và đọc chặt (V2-5 hợp đồng, dot7-Q04)

**Đợt:** 1 · **Phải xong trước:** Task 4, Task 5 · **Bead:** bs-2bd.1.15. Hợp đồng Codex yêu cầu khoá trước code: mẫu mong đợi sinh bằng đúng `ho_so_tram_kiem(tram_home_tram, nha_quan_ly, goc, cong)` của mã đã review, input lấy từ manifest root của installer (runtime không có `nha_quan_ly` chính tắc — KHÔNG dùng `Path.home()`), có phiên bản + digest; không bao giờ hash chính file đang kiểm để làm mẫu.

**Files:**
- Create: `tests/test_manifest_ho_so.py`
- Modify: `tram/tho/quyen_kiem.py`

**Interfaces:**
- Consumes: `ho_so_tram_kiem`, `goc_hop_le`, `USER_RE` (có sẵn).
- Produces: `MANIFEST_KIEM = /usr/local/tram/tram-kiem.sb.json`, `PHIEN_BAN_HO_SO = 1`, `KHOA_MANIFEST`; `manifest_ho_so(*, tram_home_tram, nha_quan_ly, goc, cong) -> (ho_so: bytes, manifest: bytes)` (JSON `sort_keys`, `indent=1`, kết thúc `\n` — tất định); `ho_so_tu_manifest(bytes) -> (dict, ho_so_mong_doi: bytes)` — ValueError thông báo cố định khi: không phải object JSON, khoá trùng/thiếu/thừa, kiểu sai (bool không là int), `phien_ban` khác mã, `nha_quan_ly` không phải `/Users/<user hợp lệ>`, đường dẫn bộ sinh từ chối, digest ≠ digest bản vừa sinh.

- [ ] **Step 1: Viết test thất bại**

`tests/test_manifest_ho_so.py` (mới, nguyên văn):

```python
"""V2-5 (dot7-Q04): manifest của hồ sơ Seatbelt — input bộ sinh + phiên bản + digest. Runtime sinh lại hồ sơ từ
manifest, không lấy hồ sơ đang kiểm làm mẫu của chính nó. Chỉ xử lý byte trong bộ nhớ — không đọc /usr/local."""
import json
from pathlib import Path

import pytest

from tram.tho import quyen_kiem
from tram.tho.quyen_kiem import KHOA_MANIFEST, PHIEN_BAN_HO_SO, ho_so_tram_kiem, ho_so_tu_manifest, manifest_ho_so


def dung(tmp_path):
    return manifest_ho_so(tram_home_tram=Path("/Users/dai-ca/.tram"), nha_quan_ly=Path("/Users/tram-tho"),
                          goc=tmp_path.resolve(), cong=[7700, 3306])


def test_manifest_sinh_lai_dung_tung_byte_va_tat_dinh(tmp_path):
    hs, mf = dung(tmp_path)
    assert (hs, mf) == dung(tmp_path)
    m, lai = ho_so_tu_manifest(mf)
    assert lai == hs == ho_so_tram_kiem(tram_home_tram=Path("/Users/dai-ca/.tram"), nha_quan_ly=Path("/Users/tram-tho"),
                                        goc=tmp_path.resolve(), cong=[7700, 3306]).encode()
    assert tuple(sorted(m)) == KHOA_MANIFEST and m["phien_ban"] == PHIEN_BAN_HO_SO
    assert m["goc"] == str(tmp_path.resolve()) and m["nha_quan_ly"] == "/Users/tram-tho"
    assert mf.endswith(b"}\n") and b"\n \"cong\"" in mf


def _sua(mf: bytes, **sua) -> bytes:
    m = json.loads(mf)
    for k, v in sua.items():
        if v is KeyError:
            m.pop(k)
        else:
            m[k] = v
    return json.dumps(m).encode()


@pytest.mark.parametrize("sua", [dict(phien_ban=PHIEN_BAN_HO_SO + 1), dict(phien_ban=True), dict(phien_ban="1"),
                                 dict(cong=[True]), dict(cong=[0]), dict(cong="7700"), dict(nha_quan_ly="/etc/BIMAT"),
                                 dict(nha_quan_ly='/Users/a"b'), dict(goc="BIMAT/tuong-doi"), dict(tram_home="BIMAT"),
                                 dict(tram_home='/Users/"BIMAT'), dict(sha256="0" * 64), dict(goc=KeyError),
                                 dict(them="BIMAT"), dict(sha256=None)])
def test_manifest_sai_thi_tu_choi_khong_lo_noi_dung(tmp_path, sua):
    with pytest.raises(ValueError, match="cài lại") as e:
        ho_so_tu_manifest(_sua(dung(tmp_path)[1], **sua))
    assert "BIMAT" not in str(e.value)


@pytest.mark.parametrize("du_lieu", [b"", b"[]", b"\xff\xfe", b'{"goc": "a", "goc": "b"}', b"BIMAT"])
def test_khong_phai_json_object_hoac_khoa_trung(du_lieu):
    with pytest.raises(ValueError, match="sai dạng") as e:
        ho_so_tu_manifest(du_lieu)
    assert "BIMAT" not in str(e.value)


def test_khoa_trung_trong_manifest_that_bi_tu_choi(tmp_path):
    mf = dung(tmp_path)[1]
    with pytest.raises(ValueError, match="sai dạng"):
        ho_so_tu_manifest(mf.replace(b'"cong": [', b'"cong": [7700], "cong": [', 1))


def test_bo_sinh_doi_ma_quen_tang_phien_ban_thi_dong(tmp_path, monkeypatch):
    mf = dung(tmp_path)[1]
    goc = quyen_kiem.ho_so_tram_kiem
    monkeypatch.setattr(quyen_kiem, "ho_so_tram_kiem", lambda **kw: goc(**kw) + "(allow network*)\n")
    with pytest.raises(ValueError, match="digest"):
        ho_so_tu_manifest(mf)
```

- [ ] **Step 2: Chạy, thấy ĐỎ**

```bash
C=<thư mục PATH chặn host>; PATH="$C/bin:$PATH" PYTHONPATH="$C/plugin" UV_OFFLINE=1 uv run pytest -p chan_host -q tests/test_manifest_ho_so.py
```

Kết quả THẬT (trước khi có mã của task):

```
E   ImportError: cannot import name 'KHOA_MANIFEST' from 'tram.tho.quyen_kiem' (…/tram/tho/quyen_kiem.py)
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
1 error in 0.06s
```

- [ ] **Step 3: Viết mã**

`tram/tho/quyen_kiem.py` (sửa — bản vá):

```diff
diff --git a/tram/tho/quyen_kiem.py b/tram/tho/quyen_kiem.py
index ea0adc7..f0fd9e0 100644
--- a/tram/tho/quyen_kiem.py
+++ b/tram/tho/quyen_kiem.py
@@ -11,7 +11,12 @@ tiền tố argv cố định `sandbox-exec -f HO_SO_KIEM` — mọi lệnh dư
 3C-D1 (C01, D45): CẢ HAI cơ chế chạy lệnh của lượt trong `HO_SO_KIEM` (`PrincipalKiem.boc_luot`) — hồ sơ cấm mặc
 định, chỉ cho ghi `-D LUOT` (bản chép) và `-D NHA` (nhà của lượt): lượt N không để lại tệp ngoài hai chỗ đó, không tạo
 job launchd, không chạy crontab/at/launchctl, không IPC POSIX/SysV, không mạng (DB/Redis dùng chung, cục bộ hay xa).
-Cưỡng chế thật của Seatbelt dưới `sudo -u` (setuid, XPC tới launchd) chỉ chứng minh được ở G4."""
+Cưỡng chế thật của Seatbelt dưới `sudo -u` (setuid, XPC tới launchd) chỉ chứng minh được ở G4.
+V2-5 (dot7-Q04): installer ghi kèm hồ sơ một MANIFEST (input của bộ sinh + phiên bản + digest); runtime sinh lại hồ sơ
+từ manifest rồi so TOÀN BỘ byte — không tìm chuỗi, không lấy hồ sơ đang kiểm làm mẫu của chính nó."""
+import hashlib
+import json
+import re
 from pathlib import Path
 
 from tram.tho.principal import SANDBOX_EXEC, USER_RE
@@ -19,6 +24,9 @@ from tram.tho.sandbox import _p
 
 THU_MUC_CAI = Path("/usr/local/tram")                 # hồ sơ root:wheel 0644 (cả hai cơ chế — 3C-D5)
 HO_SO_KIEM = THU_MUC_CAI / "tram-kiem.sb"
+MANIFEST_KIEM = THU_MUC_CAI / "tram-kiem.sb.json"      # root:wheel 0644, cùng sổ cài với hồ sơ (V2-5)
+PHIEN_BAN_HO_SO = 1                                   # TĂNG khi chữ của `ho_so_tram_kiem` đổi → bản cài cũ đóng cổng
+KHOA_MANIFEST = ("cong", "goc", "nha_quan_ly", "phien_ban", "sha256", "tram_home")
 LICH = ("/usr/bin/crontab", "/usr/bin/at", "/usr/bin/batch", "/usr/bin/atq", "/usr/bin/atrm", "/bin/launchctl",
         "/usr/bin/osascript", "/usr/bin/open", "/usr/bin/sudo", "/usr/bin/su", "/usr/bin/login", "/usr/bin/security",
         "/usr/bin/defaults")
@@ -66,3 +74,39 @@ def ho_so_tram_kiem(*, tram_home_tram: Path, nha_quan_ly: Path, goc: Path, cong:
             "(allow mach-lookup " + " ".join(f'(global-name "{m}")' for m in MACH_CHO) + ")",
             '(allow network-outbound (remote unix-socket (subpath (param "LUOT"))))']
     return "\n".join(dong) + "\n"
+
+
+def manifest_ho_so(*, tram_home_tram: Path, nha_quan_ly: Path, goc: Path, cong: list[int]) -> tuple[bytes, bytes]:
+    """(hồ sơ, manifest) sinh từ CÙNG một bộ input — installer cài cả hai qua sổ; runtime chỉ tin manifest root."""
+    hs = ho_so_tram_kiem(tram_home_tram=tram_home_tram, nha_quan_ly=nha_quan_ly, goc=goc, cong=cong).encode()
+    m = {"cong": [int(c) for c in cong], "goc": goc_hop_le(goc), "nha_quan_ly": str(nha_quan_ly),
+         "phien_ban": PHIEN_BAN_HO_SO, "sha256": hashlib.sha256(hs).hexdigest(), "tram_home": str(tram_home_tram)}
+    return hs, (json.dumps(m, ensure_ascii=False, sort_keys=True, indent=1) + "\n").encode()
+
+
+def _khong_trung(cap: list) -> dict:
+    if len({k for k, _ in cap}) != len(cap):
+        raise ValueError("khoá trùng")
+    return dict(cap)
+
+
+def ho_so_tu_manifest(du_lieu: bytes) -> tuple[dict, bytes]:
+    """Đọc manifest CHẶT (khoá, kiểu, phiên bản mã hiện tại) rồi sinh lại hồ sơ mong đợi; digest ghi trong manifest
+    phải bằng digest của bản vừa sinh (bộ sinh đổi mà quên tăng phiên bản cũng bị bắt). Sai → ValueError cố định."""
+    try:
+        m = json.loads(du_lieu.decode("utf-8"), object_pairs_hook=_khong_trung)
+        if not isinstance(m, dict) or tuple(sorted(m)) != KHOA_MANIFEST or type(m["phien_ban"]) is not int:
+            raise ValueError
+        if not all(isinstance(m[k], str) for k in ("goc", "nha_quan_ly", "sha256", "tram_home")):
+            raise ValueError
+        if not isinstance(m["cong"], list) or not all(type(c) is int and 0 < c < 65536 for c in m["cong"]):
+            raise ValueError
+        if m["phien_ban"] != PHIEN_BAN_HO_SO or not re.fullmatch(rf"/Users/{USER_RE.pattern}", m["nha_quan_ly"]):
+            raise ValueError
+        hs = ho_so_tram_kiem(tram_home_tram=Path(m["tram_home"]), nha_quan_ly=Path(m["nha_quan_ly"]),
+                             goc=Path(m["goc"]), cong=m["cong"]).encode()
+    except (ValueError, TypeError, UnicodeDecodeError):
+        raise ValueError("manifest hồ sơ sai dạng hoặc khác phiên bản mã — cài lại (`tram chu cai-dat-tho`)") from None
+    if hashlib.sha256(hs).hexdigest() != m["sha256"]:
+        raise ValueError("manifest hồ sơ ghi digest khác bản sinh từ mã hiện tại — cài lại (`tram chu cai-dat-tho`)")
+    return m, hs
```

- [ ] **Step 4: Chạy, thấy XANH**

```bash
C=<thư mục PATH chặn host>; PATH="$C/bin:$PATH" PYTHONPATH="$C/plugin" UV_OFFLINE=1 uv run pytest -p chan_host -q tests/test_manifest_ho_so.py tests/test_ho_so_kiem_lai.py tests/test_quyen_kiem.py
```

Kết quả THẬT: `34 passed in 0.12s (riêng test_manifest_ho_so.py: 23 passed)`; nhật ký chặn host không thêm dòng.

- [ ] **Step 5: Commit**

```bash
git add tests/test_manifest_ho_so.py tram/tho/quyen_kiem.py
git commit -m "feat(v2-5): manifest hồ sơ Seatbelt — input bộ sinh, phiên bản, digest (bs-2bd.1.15, dot7-Q04)"
```

### Task 4: Installer cài manifest sau hồ sơ, cùng sổ cài (V2-5)

**Đợt:** 2 · **Phải xong trước:** — (cần Task 3) · **Bead:** bs-2bd.1.15. Manifest phải root:wheel 0644, cùng receipt/journal (`so-cai.jsonl`) với hồ sơ. Thứ tự hồ sơ → manifest: cài dừng giữa hai file thì manifest thiếu (hoặc của lần cài trước) → runtime đóng cổng; gỡ (`go-cai-dat-tho`) tự gỡ manifest theo sổ như mọi file root.

**Files:**
- Modify: `tests/test_cai_dat_tho_kiem.py`
- Modify: `tests/test_go_cai_dat_tho.py`
- Modify: `tram/chu/cai_dat_kiem.py`

**Interfaces:**
- Consumes: Task 3: `manifest_ho_so`, `MANIFEST_KIEM`, `ho_so_tu_manifest` (test).
- Produces: `phan_kiem(...)` thêm `pk.tep[soan/'tram-kiem.sb.json']` và `tep_root(…, MANIFEST_KIEM, mf, "0644")` ngay sau hồ sơ.

- [ ] **Step 1: Viết test thất bại**

`tests/test_cai_dat_tho_kiem.py` (sửa — bản vá):

```diff
diff --git a/tests/test_cai_dat_tho_kiem.py b/tests/test_cai_dat_tho_kiem.py
index e00d403..4855699 100644
--- a/tests/test_cai_dat_tho_kiem.py
+++ b/tests/test_cai_dat_tho_kiem.py
@@ -13,7 +13,7 @@ from tram.chu.cai_dat_tho import SUDOERS, lap_ke_hoach_tho
 from tram.chu.so_cai_tho import SoCai
 from tram.chu.tai_nguyen import LoiCaiDat
 from tram.giao_viec.principal_kiem import tu_cach_ly
-from tram.tho.quyen_kiem import HO_SO_KIEM, THU_MUC_CAI
+from tram.tho.quyen_kiem import HO_SO_KIEM, MANIFEST_KIEM, THU_MUC_CAI, ho_so_tu_manifest
 
 
 def ke_hoach(tmp_path, he=None, chuoi="user:tram-kiem", co_che="user", khe=None):
@@ -68,7 +68,8 @@ def test_thuc_hien_ghi_du_dinh_truoc_da_tao_kem_dinh_danh_sau(tram_home_tam, tmp
     he = HeGia()
     thuc_hien(ke_hoach(tmp_path, he), chay=he.chay)
     muc = SoCai().muc().values()
-    assert {m.su for m in muc} == {"da_tao"} and len(muc) == 10    # 3 user, 2 nhà, 2 thư mục, hồ sơ, sudoers, daemon
+    assert {m.su for m in muc} == {"da_tao"} and len(muc) == 11    # 3 user, 2 nhà, 2 thư mục, hồ sơ + manifest,
+    #                                                                   sudoers, daemon
     assert sorted(m.ten for m in muc if m.kieu == "nha") == ["/Users/tram-k-1", "/Users/tram-tho"]
     assert "-home /var/empty" in next(x for x in he.lenh if "-addUser tram-kiem" in x)    # C01: không nhà ghi được
     assert not any("createhomedir -c -u tram-kiem" in x for x in he.lenh)
@@ -116,3 +117,24 @@ def test_lenh_doc_cau_hinh_khong_con_co_tram_kiem(tram_home_tam, tmp_path, monke
     assert lenh_tho._cai_dat_tho(args) == 1 and f"{tmp_path}/kiem" in capsys.readouterr().out
     assert lenh_tho._cai_dat_tho(SimpleNamespace(**{**vars(args), "co_che": "sandbox"})) == 2
     assert "khác --co-che" in capsys.readouterr().err
+
+
+def test_manifest_cai_sau_ho_so_cung_so_va_sinh_lai_dung_ho_so(tram_home_tam, tmp_path):
+    """V2-5: manifest (input bộ sinh + phiên bản + digest) cài root:wheel 0644 SAU hồ sơ, cùng sổ cài."""
+    kh, soan = ke_hoach(tmp_path), tram_home_tam / "cai-dat-tho"
+    m, hs = ho_so_tu_manifest(kh.tep[soan / MANIFEST_KIEM.name])
+    assert hs == kh.tep[soan / HO_SO_KIEM.name] and m["nha_quan_ly"] == "/Users/tram-tho"
+    assert (m["tram_home"], m["goc"]) == (str(tram_home_tam), str(tmp_path / "kiem"))
+    buoc = [x for x, _ in kh.buoc]
+    i_hs = next(i for i, x in enumerate(buoc) if x.endswith(f"{soan / HO_SO_KIEM.name} {HO_SO_KIEM}"))
+    assert buoc[i_hs + 1].endswith(f"install -m 0644 -o root -g wheel {soan / MANIFEST_KIEM.name} {MANIFEST_KIEM}")
+
+
+def test_cai_hong_giua_ho_so_va_manifest_thi_so_ghi_dung_phan_da_cai(tram_home_tam, tmp_path):
+    he = HeGia()
+    he.hong.add(f"install -m 0644 -o root -g wheel {tram_home_tam / 'cai-dat-tho' / MANIFEST_KIEM.name}")
+    with pytest.raises(LoiCaiDat):
+        thuc_hien(ke_hoach(tmp_path, he), chay=he.chay)
+    su = {m.ten: m.su for m in SoCai().muc().values()}
+    assert su[str(HO_SO_KIEM)] == "da_tao" and su[str(MANIFEST_KIEM)] == "khong_tao"
+    assert str(HO_SO_KIEM) in he.tep and str(MANIFEST_KIEM) not in he.tep    # runtime: thiếu manifest → cổng đóng
```

`tests/test_go_cai_dat_tho.py` (sửa — bản vá):

```diff
diff --git a/tests/test_go_cai_dat_tho.py b/tests/test_go_cai_dat_tho.py
index 65c531c..87a9725 100644
--- a/tests/test_go_cai_dat_tho.py
+++ b/tests/test_go_cai_dat_tho.py
@@ -16,7 +16,7 @@ from tram.chu.so_cai_tho import SoCai
 from tram.chu.tai_nguyen import LoiCaiDat
 from tram.cli import tao_parser
 from tram.giao_viec.principal_kiem import tu_cach_ly
-from tram.tho.quyen_kiem import HO_SO_KIEM, THU_MUC_CAI
+from tram.tho.quyen_kiem import HO_SO_KIEM, MANIFEST_KIEM, THU_MUC_CAI
 
 
 def cai(tmp_path, he, *, co_che="sandbox", chay=None):
@@ -37,7 +37,8 @@ def test_go_dung_thu_tu_het_sach_va_chay_lai_rong(tram_home_tam, tmp_path):
     kh = ke_hoach_go(he)
     assert [m.split(":")[0] for m, _ in kh.buoc] == [
         "Đối soát sổ cài đặt (khép bản ghi dở do crash)", f"Gỡ tep {DAEMON} nếu còn đúng định danh trong sổ",
-        f"Gỡ tep {HO_SO_KIEM} nếu còn đúng định danh trong sổ", f"Gỡ tep {SUDOERS} nếu còn đúng định danh trong sổ",
+        f"Gỡ tep {HO_SO_KIEM} nếu còn đúng định danh trong sổ",
+        f"Gỡ tep {MANIFEST_KIEM} nếu còn đúng định danh trong sổ", f"Gỡ tep {SUDOERS} nếu còn đúng định danh trong sổ",
         f"Gỡ thu_muc {tmp_path}/kiem nếu còn đúng định danh trong sổ",
         *(f"Gỡ user {u} nếu còn đúng định danh trong sổ" for u in ("tram-k-1", "tram-kiem", "tram-tho")),
         f"Gỡ thu_muc {THU_MUC_CAI} nếu còn đúng định danh trong sổ"]
```

- [ ] **Step 2: Chạy, thấy ĐỎ**

```bash
C=<thư mục PATH chặn host>; PATH="$C/bin:$PATH" PYTHONPATH="$C/plugin" UV_OFFLINE=1 uv run pytest -p chan_host -q tests/test_cai_dat_tho_kiem.py tests/test_go_cai_dat_tho.py
```

Kết quả THẬT (trước khi có mã của task):

```
E       AssertionError: assert ({'da_tao'} == {'da_tao'} … and 10 == 11)
E       KeyError: PosixPath('…/tram-home/cai-dat-tho/tram-kiem.sb.json')
E       Failed: DID NOT RAISE <class 'tram.chu.tai_nguyen.LoiCaiDat'>
E       AssertionError: … At index 3 diff: 'Gỡ tep /etc/sudoers.d/tram-tho …' != 'Gỡ tep /usr/local/tram/tram-kiem.sb.json …'
FAILED tests/test_cai_dat_tho_kiem.py::test_thuc_hien_ghi_du_dinh_truoc_da_tao_kem_dinh_danh_sau
FAILED tests/test_cai_dat_tho_kiem.py::test_manifest_cai_sau_ho_so_cung_so_va_sinh_lai_dung_ho_so
FAILED tests/test_cai_dat_tho_kiem.py::test_cai_hong_giua_ho_so_va_manifest_thi_so_ghi_dung_phan_da_cai
FAILED tests/test_go_cai_dat_tho.py::test_go_dung_thu_tu_het_sach_va_chay_lai_rong
4 failed, 16 passed in 1.88s
```

- [ ] **Step 3: Viết mã**

`tram/chu/cai_dat_kiem.py` (sửa — bản vá):

```diff
diff --git a/tram/chu/cai_dat_kiem.py b/tram/chu/cai_dat_kiem.py
index 7717ba9..f6bca54 100644
--- a/tram/chu/cai_dat_kiem.py
+++ b/tram/chu/cai_dat_kiem.py
@@ -12,7 +12,7 @@ from tram.chu.tai_nguyen import TaiNguyen
 from tram.cli_dich_vu import CONG_MAC_DINH
 from tram.duong_dan import tram_home
 from tram.giao_viec.principal_kiem import PrincipalKiem
-from tram.tho.quyen_kiem import HO_SO_KIEM, THU_MUC_CAI, goc_hop_le, ho_so_tram_kiem
+from tram.tho.quyen_kiem import HO_SO_KIEM, MANIFEST_KIEM, THU_MUC_CAI, goc_hop_le, manifest_ho_so
 
 NHA_KIEM = "/var/empty"        # C01: tram-kiem KHÔNG có nhà ghi được (root, 0755); lệnh kiểm nhận HOME mới mỗi lần
 
@@ -51,12 +51,13 @@ def phan_kiem(*, kiem: PrincipalKiem | None, thu_muc_kiem: Path | None, co_che:
     uid_kiem = lambda i: {"chu": kiem.ten, "uid": (quan_sat("user", kiem.ten) or {}).get("uid")}  # noqa: E731
     pk = PhanKiem(tai_nguyen=[TaiNguyen("thu_muc", goc, lambda i: [["sudo", "-u", kiem.ten, "/bin/mkdir", "-m", "0755",
                                                                      goc]], uid_kiem)])
-    hs = ho_so_tram_kiem(tram_home_tram=tram_home(), nha_quan_ly=Path(f"/Users/{quan_ly}"), goc=Path(goc),
-                         cong=cong_cam(db_nghiep_vu)).encode()
-    pk.tep[soan / HO_SO_KIEM.name] = hs
+    hs, mf = manifest_ho_so(tram_home_tram=tram_home(), nha_quan_ly=Path(f"/Users/{quan_ly}"), goc=Path(goc),
+                            cong=cong_cam(db_nghiep_vu))      # V2-5: manifest cài SAU hồ sơ — thiếu/cũ → cổng đóng
+    pk.tep[soan / HO_SO_KIEM.name], pk.tep[soan / MANIFEST_KIEM.name] = hs, mf
     pk.tai_nguyen += [TaiNguyen("thu_muc", str(THU_MUC_CAI), lambda i: [
         ["sudo", "install", "-d", "-o", "root", "-g", "wheel", "-m", "0755", str(THU_MUC_CAI)]], lambda i: {"uid": 0}),
-                      tep_root(soan / HO_SO_KIEM.name, HO_SO_KIEM, hs, "0644")]
+                      tep_root(soan / HO_SO_KIEM.name, HO_SO_KIEM, hs, "0644"),
+                      tep_root(soan / MANIFEST_KIEM.name, MANIFEST_KIEM, mf, "0644")]
     pk.canh_bao = [
         f"D22: KHÔNG có dòng sudoers nào chạy root — {tram} chỉ được chạy lệnh DƯỚI {kiem.ten}. {kiem.ten} tự tạo, tự "
         f"giải nén, tự dọn bản chép dưới {goc}; cây kiểm là repo git MỘT commit do {kiem.ten} tự dựng (D40).",
```

- [ ] **Step 4: Chạy, thấy XANH**

```bash
C=<thư mục PATH chặn host>; PATH="$C/bin:$PATH" PYTHONPATH="$C/plugin" UV_OFFLINE=1 uv run pytest -p chan_host -q tests/test_cai_dat_tho_kiem.py tests/test_go_cai_dat_tho.py
```

Kết quả THẬT: `20 passed in 1.81s`; nhật ký chặn host không thêm dòng.

- [ ] **Step 5: Commit**

```bash
git add tests/test_cai_dat_tho_kiem.py tests/test_go_cai_dat_tho.py tram/chu/cai_dat_kiem.py
git commit -m "feat(v2-5): installer cài manifest hồ sơ root:wheel 0644 sau hồ sơ, cùng sổ (bs-2bd.1.15)"
```

### Task 5: Runtime attestation: hồ sơ khớp từng byte bản sinh từ manifest root (V2-5)

**Đợt:** 2 · **Phải xong trước:** — (cần Task 3; ghép cùng đợt Task 4 để bản cài mới có manifest) · **Bead:** bs-2bd.1.15. `ho_so_cai` cũ chỉ tìm `(deny default)` và `(subpath "<TRAM_HOME>")` — hồ sơ thêm `(allow file-write*)`/`(allow network*)` hay chuỗi trong comment vẫn qua. Mới: đọc manifest + hồ sơ an toàn (cha của root không ai khác ghi, O_NOFOLLOW, fstat trên fd đã mở, file thường root không nhóm/khác ghi, ≤ 64 KiB), sinh lại hồ sơ từ manifest, so TOÀN BỘ byte; TRAM_HOME/gốc trong manifest phải bằng cấu hình HIỆN HÀNH (`goc` của `dung_cong`). Hai test cũ tìm chuỗi bị xoá vì hợp đồng của chúng (hồ sơ ba dòng là đạt) chính là lỗi dot7-Q04.

**Files:**
- Create: `tests/test_ho_so_cai_attest.py`
- Modify: `tests/test_cong_that.py`
- Modify: `tram/giao_viec/cong_that.py`

**Interfaces:**
- Consumes: Task 3: `ho_so_tu_manifest`, `MANIFEST_KIEM`.
- Produces: `HO_SO_TOI_DA = 65536`; `doc_tep_root(p, *, chu=0, lstat=os.lstat, fstat=os.fstat) -> bytes`; `ho_so_cai(goc, p=HO_SO_KIEM, mf=MANIFEST_KIEM, *, chu=0, lstat=os.lstat, fstat=os.fstat) -> None` (ném `LoiBanChep`); `dung_cong` dùng `partial(ho_so_cai, goc)` — mọi caller (`noi_that`, `lenh_nghiem_thu`, `kiem_principal`) đi qua `dung_cong`, không đổi chữ ký.

- [ ] **Step 1: Viết test thất bại**

`tests/test_ho_so_cai_attest.py` (mới, nguyên văn):

```python
"""V2-5 (dot7-Q04): hồ sơ Seatbelt đã cài phải ĐÚNG TỪNG BYTE bản sinh lại từ manifest root của installer — không tìm
hai chuỗi. Tệp thật trong tmp_path; chủ/quyền/loại do `lstat`/`fstat` GIẢ trả (root:wheel) — không chmod/chown/sudo."""
import os
import stat
from pathlib import Path
from types import SimpleNamespace

import pytest

from tram.giao_viec.ban_chep import LoiBanChep
from tram.giao_viec.cong_that import ho_so_cai
from tram.tho.quyen_kiem import manifest_ho_so

THU_MUC_ROOT = SimpleNamespace(st_mode=stat.S_IFDIR | 0o755, st_uid=0)


class StatGia:
    """`lstat` thư mục cha mặc định root 0755; `fstat` theo inode: mặc định root 0644, `sai` đổi riêng từng tệp."""
    def __init__(self, cha: dict | None = None, tep: dict | None = None):
        self.cha, self.tep = cha or {}, tep or {}

    def lstat(self, p):
        return self.cha.get(Path(p), THU_MUC_ROOT)

    def fstat(self, fd):
        that = os.fstat(fd)
        for p, (quyen, chu) in self.tep.items():
            if os.stat(p).st_ino == that.st_ino:
                return SimpleNamespace(st_mode=stat.S_IFMT(that.st_mode) | quyen, st_uid=chu)
        return SimpleNamespace(st_mode=stat.S_IFMT(that.st_mode) | 0o644, st_uid=0)


@pytest.fixture
def cai(tmp_path, tram_home_tam):
    """Bản cài giả: (hồ sơ, manifest, gốc) sinh bởi CÙNG hàm installer dùng."""
    goc = (tmp_path / "kiem").resolve()
    hs, mf = manifest_ho_so(tram_home_tram=tram_home_tam, nha_quan_ly=Path("/Users/tram-tho"), goc=goc, cong=[7700])
    (d := tmp_path / "usr-local-tram").mkdir()
    (d / "tram-kiem.sb").write_bytes(hs)
    (d / "tram-kiem.sb.json").write_bytes(mf)
    return d / "tram-kiem.sb", d / "tram-kiem.sb.json", goc


def kiem(cai, st=None, goc=None):
    st = st or StatGia()
    ho_so_cai(goc or cai[2], cai[0], cai[1], lstat=st.lstat, fstat=st.fstat)


def test_ban_cai_dung_tung_byte_thi_dat(cai):
    kiem(cai)


@pytest.mark.parametrize("sua", [
    lambda b: b.replace(b"(allow signal)", b"(allow network*)"),                 # sửa một allow
    lambda b: b + b"(allow file-write*)\n",                                       # mở rộng, vẫn đủ hai chuỗi cũ
    lambda b: b + b"; (deny default) BIMAT\n",                                    # comment giả deny
    lambda b: b.replace(b"(deny job-creation)\n", b""),
    lambda b: b.replace(b"\n", b"\r\n"),
    lambda b: b"x" * 70000])
def test_ho_so_lech_mot_byte_bi_tu_choi_khong_lo_noi_dung(cai, sua):
    cai[0].write_bytes(sua(cai[0].read_bytes()))
    with pytest.raises(LoiBanChep, match="khác bản đã duyệt|quá lớn") as e:
        kiem(cai)
    assert "BIMAT" not in str(e.value) and "allow" not in str(e.value)


def test_ba_dong_hai_chuoi_cu_khong_con_du(cai, tram_home_tam):
    cai[0].write_text(f'(version 1)\n(deny default)\n(deny file-read* (subpath "{tram_home_tam}"))\n(allow network*)\n')
    with pytest.raises(LoiBanChep, match="khác bản đã duyệt"):
        kiem(cai)


def test_goc_hoac_tram_home_doi_thi_phai_cai_lai(cai, tmp_path, monkeypatch):
    with pytest.raises(LoiBanChep, match="khác cấu hình hiện hành"):
        kiem(cai, goc=(tmp_path / "goc-moi").resolve())                           # đường gốc cũ trong manifest
    monkeypatch.setenv("TRAM_HOME", str(tmp_path / "tram-home-khac"))
    with pytest.raises(LoiBanChep, match="khác cấu hình hiện hành"):
        kiem(cai)


def test_manifest_thieu_hong_hoac_cu_hon_ho_so(cai, tram_home_tam):
    hs, mf, goc = cai
    _, mf_khac = manifest_ho_so(tram_home_tram=tram_home_tam, nha_quan_ly=Path("/Users/quan-ly-cu"), goc=goc,
                                cong=[7700])
    mf.write_bytes(mf_khac)                         # cài hỏng giữa hai tệp: manifest của lần cài khác, hồ sơ mới
    with pytest.raises(LoiBanChep, match="khác bản đã duyệt"):
        kiem(cai)
    mf.write_bytes(b'{"BIMAT": 1}')
    with pytest.raises(LoiBanChep, match="sai dạng") as e:
        kiem(cai)
    assert "BIMAT" not in str(e.value)
    mf.unlink()                                     # cài dừng sau hồ sơ, trước manifest
    with pytest.raises(LoiBanChep, match="không đọc được"):
        kiem(cai)


def test_symlink_hoac_khong_phai_tep_thuong(cai, tmp_path):
    that = tmp_path / "ho-so-that.sb"
    that.write_bytes(cai[0].read_bytes())
    cai[0].unlink()
    cai[0].symlink_to(that)
    with pytest.raises(LoiBanChep, match="không đọc được"):
        kiem(cai)                                   # O_NOFOLLOW: symlink bị từ chối dù đích đúng từng byte
    cai[0].unlink()
    cai[0].mkdir()
    with pytest.raises(LoiBanChep, match="sai chủ/quyền/loại"):
        kiem(cai)


@pytest.mark.parametrize("tep, quyen, chu", [(0, 0o644, 501), (0, 0o664, 0), (0, 0o646, 0), (1, 0o644, 501),
                                             (1, 0o666, 0)])
def test_chu_hoac_quyen_root_sai(cai, tep, quyen, chu):
    with pytest.raises(LoiBanChep, match="sai chủ/quyền/loại"):
        kiem(cai, StatGia(tep={cai[tep]: (quyen, chu)}))


@pytest.mark.parametrize("st", [SimpleNamespace(st_mode=stat.S_IFDIR | 0o775, st_uid=0),
                                SimpleNamespace(st_mode=stat.S_IFDIR | 0o755, st_uid=501),
                                SimpleNamespace(st_mode=stat.S_IFLNK | 0o755, st_uid=0)])
def test_thu_muc_cha_ghi_duoc_hoac_khong_cua_root(cai, st):
    with pytest.raises(LoiBanChep, match="thư mục cha"):
        kiem(cai, StatGia(cha={cai[0].parent: st}))
```

`tests/test_cong_that.py` (sửa — bản vá):

```diff
diff --git a/tests/test_cong_that.py b/tests/test_cong_that.py
index 57273c8..8333200 100644
--- a/tests/test_cong_that.py
+++ b/tests/test_cong_that.py
@@ -1,5 +1,5 @@
 """3C-D4/D5: cổng thật ghép thu hồi + quan sát; thu hồi theo UID (`test_thu_hoi_uid.py`) không gỡ lịch; hồ sơ Seatbelt
-đã cài phải đúng chủ/quyền/nội dung; tệp môi trường kiểm của mọi dự án phải kín. Không chạy lệnh hệ thống thật."""
+đã cài: `test_ho_so_cai_attest.py` (V2-5); tệp môi trường kiểm của mọi dự án phải kín. Không chạy lệnh hệ thống thật."""
 import os
 from functools import partial
 from types import SimpleNamespace
@@ -12,28 +12,6 @@ from tram.giao_viec.principal_kiem import tu_cach_ly
 from tram.giao_viec.quan_sat_kiem import cron_at, goc_rong, launchd, tep_ngoai, tien_trinh
 
 
-def test_ho_so_cai_dung_chu_quyen_noi_dung(tmp_path, tram_home_tam):
-    p = tmp_path / "hs.sb"
-    p.write_text(f'(version 1)\n(deny default)\n(deny file-read* (subpath "{tram_home_tam}"))\n')
-    p.chmod(0o644)
-    ho_so_cai(p, chu=os.getuid())
-    with pytest.raises(LoiBanChep, match="sai chủ"):
-        ho_so_cai(p)                                               # tệp của user đang test, không phải root
-    with pytest.raises(LoiBanChep, match="không đọc"):
-        ho_so_cai(tmp_path / "khong-co.sb")
-
-
-@pytest.mark.parametrize("nd, quyen", [('(deny default)\n(subpath "{h}")', 0o664),
-                                       ('(allow default)\n(subpath "{h}")', 0o644),
-                                       ('(deny default)\n(subpath "/Users/khac/.tram")', 0o644)])
-def test_ho_so_cai_sai_quyen_hoac_noi_dung(tmp_path, tram_home_tam, nd, quyen):
-    p = tmp_path / "hs.sb"
-    p.write_text(nd.format(h=tram_home_tam))
-    p.chmod(quyen)
-    with pytest.raises(LoiBanChep, match="sai chủ/quyền/nội dung"):
-        ho_so_cai(p, chu=os.getuid())
-
-
 def test_env_kin_doi_0600_cua_tram(tmp_path):
     f = tmp_path / "env.testing"
     f.write_text("DB=x\n")
@@ -53,4 +31,5 @@ def test_dung_cong_du_quan_sat_va_thu_hoi_mac_dinh_khong_go_lich(tram_home_tam,
     assert c.tep == tram_home_tam / "kiem-lai" / "cong.json" and c.thu_hoi.func is thu_hoi_theo_uid
     ham = [q.func if isinstance(q, partial) else q for q in c.quan_sat]
     assert ham == [tien_trinh, tep_ngoai, goc_rong, cron_at, ho_so_cai, env_kin, launchd]
+    assert c.quan_sat[4].args == (tmp_path,)                       # V2-5: hồ sơ so với gốc bản chép HIỆN HÀNH
     assert dung_cong(pk, tmp_path, cac_du_an=list, thu_hoi=print).thu_hoi is print
```

- [ ] **Step 2: Chạy, thấy ĐỎ**

```bash
C=<thư mục PATH chặn host>; PATH="$C/bin:$PATH" PYTHONPATH="$C/plugin" UV_OFFLINE=1 uv run pytest -p chan_host -q tests/test_ho_so_cai_attest.py tests/test_cong_that.py
```

Kết quả THẬT (trước khi có mã của task):

```
E       TypeError: ho_so_cai() got an unexpected keyword argument 'lstat'      (×19, mọi ca attestation)
E       AttributeError: 'function' object has no attribute 'args'               (test_dung_cong_…: quan sát hồ sơ chưa nhận goc)
20 failed, 1 passed
```

Đỏ ở mức hành vi đã có sẵn trong V2 (dot7-Q04): với mã cũ, `ho_so_cai(p, chu=os.getuid())` trên hồ sơ ba dòng + `(allow network*)` không ném — đúng ca `test_ba_dong_hai_chuoi_cu_khong_con_du` chặn ở mã mới.

- [ ] **Step 3: Viết mã**

`tram/giao_viec/cong_that.py` (sửa — bản vá):

```diff
diff --git a/tram/giao_viec/cong_that.py b/tram/giao_viec/cong_that.py
index 7ae235b..5b2e497 100644
--- a/tram/giao_viec/cong_that.py
+++ b/tram/giao_viec/cong_that.py
@@ -5,10 +5,11 @@ Thu hồi (3C-D5, hợp đồng P1/3C-B): mở `CongLich` (UID THỰC của `tra
 `setsid`). Mã thoát không là bằng chứng: TRẠM chụp `ps` (cột số) tới khi không còn tiến trình nào có uid/ruid đó;
 rồi dọn + xác nhận rỗng `DARWIN_USER_*` của `tram-kiem` (`thu_muc_he`, phần còn giữ của r47 T11).
 KHÔNG gỡ lịch — lịch để `cron_at` thấy và đóng cổng. Quan sát: tiến trình, tệp ngoài, gốc rỗng, cron/at, hồ sơ
-Seatbelt đã cài đúng, tệp môi trường kiểm của mọi dự án kín (0600, của trạm — lượt N không đọc được env của N+1),
+Seatbelt đúng TỪNG BYTE bản sinh từ manifest root (V2-5), tệp môi trường kiểm của mọi dự án kín (0600, của trạm),
 launchd (`user/<uid>`, `gui/<uid>`, `login/<asid>` — 3C-D6: khung, chưa có bộ đọc đã đo ở G3 thì ném, cổng giữ đóng;
 I1 KHÔNG bật `giao_viec.bat`)."""
 import os
+import stat
 import subprocess
 import time
 from collections.abc import Callable
@@ -23,10 +24,11 @@ from tram.giao_viec.thu_muc_he import don_thu_muc_he
 from tram.kiem.cay_tien_trinh import chup_he
 from tram.kiem.danh_tinh import LoiDanhTinh
 from tram.kiem.vong_doi import LoiThuHoi
-from tram.tho.quyen_kiem import HO_SO_KIEM
+from tram.tho.quyen_kiem import HO_SO_KIEM, MANIFEST_KIEM, ho_so_tu_manifest
 
 GIET = ["/bin/kill", "-KILL", "-1"]
 HAN_HET = 5.0
+HO_SO_TOI_DA = 65536
 
 
 def cho_het_uid(uid: int, *, chup: Callable = chup_he, han: float = HAN_HET, ngu: Callable = time.sleep) -> None:
@@ -58,14 +60,44 @@ def thu_hoi_theo_uid(pk, *, mo_cong: Callable | None = None, cho_het: Callable[[
     don_he(pk, cong)
 
 
-def ho_so_cai(p: Path = HO_SO_KIEM, *, chu: int = 0) -> None:
-    """Hồ sơ đã cài: root, không ai khác ghi được, cấm mặc định, cấm đọc kho trạm HIỆN TẠI (đổi TRAM_HOME → cài lại)."""
+def doc_tep_root(p: Path, *, chu: int = 0, lstat: Callable = os.lstat, fstat: Callable = os.fstat) -> bytes:
+    """File của root: mọi thư mục cha thật, của `chu`, không ai khác ghi; mở O_NOFOLLOW, `fstat` CHÍNH fd đó."""
     try:
-        st, nd = p.stat(), p.read_text(encoding="utf-8")
+        for cha in reversed(p.parents):
+            st = lstat(cha)
+            if not stat.S_ISDIR(st.st_mode) or st.st_uid != chu or st.st_mode & 0o022:
+                raise LoiBanChep(f"thư mục cha của {p.name} không do root giữ riêng — cài lại (`tram chu cai-dat-tho`)")
+        fd, du_lieu = os.open(p, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK), b""
+        try:
+            st = fstat(fd)
+            if not stat.S_ISREG(st.st_mode) or st.st_uid != chu or st.st_mode & 0o022:
+                raise LoiBanChep(f"{p.name} sai chủ/quyền/loại — cài lại bằng `tram chu cai-dat-tho`")
+            while len(du_lieu) <= HO_SO_TOI_DA and (k := os.read(fd, 65536)):
+                du_lieu += k
+        finally:
+            os.close(fd)
+    except LoiBanChep:
+        raise
     except OSError as e:
-        raise LoiBanChep(f"không đọc được hồ sơ {p}: {e.strerror}") from e
-    if st.st_uid != chu or st.st_mode & 0o022 or "(deny default)" not in nd or f'(subpath "{tram_home()}")' not in nd:
-        raise LoiBanChep(f"hồ sơ {p} sai chủ/quyền/nội dung — cài lại bằng `tram chu cai-dat-tho`")
+        raise LoiBanChep(f"không đọc được {p.name}: {e.strerror}") from None
+    if len(du_lieu) > HO_SO_TOI_DA:
+        raise LoiBanChep(f"{p.name} quá lớn — cài lại bằng `tram chu cai-dat-tho`")
+    return du_lieu
+
+
+def ho_so_cai(goc: Path, p: Path = HO_SO_KIEM, mf: Path = MANIFEST_KIEM, *, chu: int = 0, lstat: Callable = os.lstat,
+              fstat: Callable = os.fstat) -> None:
+    """V2-5 (dot7-Q04): hồ sơ đã cài ĐÚNG từng byte bản sinh lại từ manifest root (không tìm chuỗi); input manifest
+    khớp cấu hình hiện hành (TRAM_HOME, gốc bản chép). Thiếu/lệch/sai chủ → `LoiBanChep`, cổng đóng, cài lại."""
+    doc = partial(doc_tep_root, chu=chu, lstat=lstat, fstat=fstat)
+    try:
+        m, mong = ho_so_tu_manifest(doc(mf))
+    except ValueError as e:
+        raise LoiBanChep(str(e)) from None
+    if (m["tram_home"], m["goc"]) != (str(tram_home()), str(goc)):
+        raise LoiBanChep("manifest hồ sơ cài cho TRAM_HOME/gốc bản chép khác cấu hình hiện hành — cài lại")
+    if doc(p) != mong:
+        raise LoiBanChep(f"hồ sơ {p} khác bản đã duyệt (sinh lại từ manifest) — cài lại bằng `tram chu cai-dat-tho`")
 
 
 def env_kin(cac_du_an: Callable[[], list]) -> None:
@@ -86,4 +118,5 @@ def dung_cong(pk, goc: Path | None, *, cac_du_an: Callable[[], list],
     goc = goc or tram_home() / "kiem"
     return CongLuot(tram_home() / "kiem-lai" / "cong.json", thu_hoi=thu_hoi or partial(thu_hoi_theo_uid, pk),
                     quan_sat=[partial(tien_trinh, pk.ten), partial(tep_ngoai, pk.ten, goc), partial(goc_rong, goc),
-                              partial(cron_at, pk), ho_so_cai, partial(env_kin, cac_du_an), partial(launchd, pk)])
+                              partial(cron_at, pk), partial(ho_so_cai, goc), partial(env_kin, cac_du_an),
+                              partial(launchd, pk)])
```

- [ ] **Step 4: Chạy, thấy XANH**

```bash
C=<thư mục PATH chặn host>; PATH="$C/bin:$PATH" PYTHONPATH="$C/plugin" UV_OFFLINE=1 uv run pytest -p chan_host -q tests/test_ho_so_cai_attest.py tests/test_cong_that.py tests/test_lenh_nghiem_thu.py tests/test_kiem_principal_dong.py
```

Kết quả THẬT: `39 passed in 0.41s (riêng hai file của task: 21 passed)`; nhật ký chặn host không thêm dòng.

- [ ] **Step 5: Commit**

```bash
git add tests/test_ho_so_cai_attest.py tests/test_cong_that.py tram/giao_viec/cong_that.py
git commit -m "fix(v2-5): kiểm hồ sơ Seatbelt khớp từng byte bản sinh từ manifest root, không tìm chuỗi (bs-2bd.1.15, dot7-Q04)"
```

### Task 6: `term_thanh_ngat` trên cơ chế `hoan()` của plan A + `chay_gioi_han(stdin=)` trên thân hàm A-T4 (H1, V2-6a; B03 vòng 1; R2-02, R2-03 vòng 2)

**Đợt:** 1 · **Phải xong trước:** Task 7, Task 8 · **Cần trước:** plan A Task 1–8 đã ghép (A-T2 tạo `tram/kiem/ngat.py` + hợp đồng `tram/kiem/so_huu.py`; A-T4 viết thân hàm cuối của `chay_gioi_han`/`chay_han_tong`) · **Bead:** bs-863.18, bs-863.19.

**Vì sao đổi so với bản vòng 2 (R2-02, R2-03):** bản trước vá `chay_gioi_han` CŨ (`communicate`) và có `ngat.hoan()` RIÊNG đặt bên ngoài `so_huu.hoan_ngat()` của A — hai cơ chế hoãn lồng nhau, hai bản thân hàm cạnh tranh, và tín hiệu nhận trong lớp A vẫn dẫn tới `bo_khan` rồi lỗi trước khi B kịp nhận `Nhom`. Nay chỉ còn MỘT cơ chế và MỘT bản thân hàm: plan A sở hữu `hoan()` (bộ ghi + phát lại qua handler cũ), hợp đồng sở hữu (`khoi_chay(chu=)` bắt buộc, `Nhom` vào `chu` trong `hoan()`), `chay_gioi_han` (selector, hạn trước spawn, `_don` đóng từng ống rồi LUÔN thu hồi trong `hoan()`, chưa xác nhận → `LoiThuHoi` thắng trừ ngắt) và `chay_han_tong`. Task này CHỈ: (a) thêm `NgatTerm` + `term_thanh_ngat` vào `ngat.py` của A — handler của CLI cha; trong `hoan()` tín hiệu được ghi rồi phát lại QUA chính handler này; (b) thêm `stdin=` vào thân hàm A-T4 (chữ ký + chọn `vao` + loại trừ `input`). Fault injection viết lại theo điểm đọc THẬT (`_doc` trong vòng selector), không còn Popen giả có `communicate`. Test SIGTERM THẬT (`raise_signal` vào chính tiến trình test) đi qua cả hai lớp.

`ban_chep._chay` còn `subprocess.run` dưới principal vì primitive chưa nhận ống làm stdin: `stdin=` (file object/FD) truyền THẲNG cho Popen — không đọc archive vào RAM; `p.stdin` khi đó là None nên bộ chạy không đụng tới; người gọi giữ và đóng bản sao của mình.

**Files:**
- Create: `tests/test_ngat.py`, `tests/test_chay_gioi_han_ngat.py`
- Modify: `tests/test_chay_gioi_han.py`, `tram/kiem/ngat.py` (của A-T2), `tram/kiem/chay_gioi_han.py` (của A-T4)

**Interfaces:**
- Consumes (plan A): `ngat.hoan`, hợp đồng sở hữu `so_huu` (thay "H-A03" của bản trước — nguyên văn ở docstring `tram/kiem/so_huu.py`), `khoi_chay(argv, *, kill, chu, …)`, `Nhom`, `chay_gioi_han` bản A-T4 (điểm tiêm `_doc`).
- Produces: `tram.kiem.ngat.NgatTerm(KeyboardInterrupt)`, `term_thanh_ngat(dat=signal.signal)` (context manager; cài SIGTERM → `NgatTerm`, SIGINT → `KeyboardInterrupt`; chỉ CLI cha, luồng chính; khôi phục cả hai); `chay_gioi_han(argv, *, kill, timeout, capture_output=False, text=False, input=None, stdin=None, env=None, cwd=None, check=False, khoi=khoi_chay)` — `input` và `stdin` cùng khác None → ValueError, không spawn.

- [ ] **Step 1: Viết test thất bại**

`tests/test_ngat.py` (mới, nguyên văn):

```python
"""bs-863.19 + B03 (vòng 1), R2-02 (vòng 2): SIGTERM/SIGINT ở CLI cha thành ngắt có kiểm soát; `hoan()` (MỘT cơ chế,
do plan A tạo) chỉ GHI tín hiệu và phát lại QUA handler của `term_thanh_ngat` khi ra khỏi khối ngoài cùng; handler
cũ của cả hai tín hiệu luôn được khôi phục. KHÔNG gửi tín hiệu thật — `giao` gọi handler ĐANG CÀI (như nhân giao tín
hiệu cho luồng chính: trong `hoan()` là bộ ghi, ngoài `hoan()` là handler của `term_thanh_ngat`)."""
import signal
import threading

import pytest

from tram.kiem.ngat import NgatTerm, hoan, term_thanh_ngat


def giao(so):
    signal.getsignal(so)(so, None)


@pytest.mark.parametrize("so, loi", [(signal.SIGTERM, NgatTerm), (signal.SIGINT, KeyboardInterrupt)])
def test_trong_khoi_tin_hieu_thanh_ngat_ra_khoi_thi_khoi_phuc(so, loi):
    truoc = {s: signal.getsignal(s) for s in (signal.SIGTERM, signal.SIGINT)}
    with pytest.raises(loi) as e:
        with term_thanh_ngat():
            giao(so)
    assert type(e.value) is loi and issubclass(NgatTerm, KeyboardInterrupt)
    assert {s: signal.getsignal(s) for s in truoc} == truoc


def test_loi_bat_ky_trong_khoi_van_khoi_phuc_ca_hai_handler():
    goi = []
    truoc = {s: signal.getsignal(s) for s in (signal.SIGTERM, signal.SIGINT)}
    dat = lambda so, h: goi.append((so, h)) or f"CU-{so}"                      # noqa: E731
    with pytest.raises(RuntimeError):
        with term_thanh_ngat(dat=dat):
            raise RuntimeError("x")
    assert [g[0] for g in goi] == [signal.SIGTERM, signal.SIGINT, signal.SIGINT, signal.SIGTERM]
    assert [g[1] for g in goi[2:]] == [truoc[signal.SIGINT], truoc[signal.SIGTERM]]


@pytest.mark.parametrize("luc", [2, 3])
def test_ngat_giua_cai_hay_khoi_phuc_handler_khong_de_lai_handler(luc):
    truoc = {s: signal.getsignal(s) for s in (signal.SIGTERM, signal.SIGINT)}
    goi = []

    def dat(s, h):
        cu = signal.signal(s, h)
        goi.append(s)
        if len(goi) == luc:
            raise KeyboardInterrupt()
        return cu

    try:
        with pytest.raises(KeyboardInterrupt):
            with term_thanh_ngat(dat=dat):
                pass
        assert {s: signal.getsignal(s) for s in truoc} == truoc
    finally:
        for s, h in truoc.items():
            signal.signal(s, h)


@pytest.mark.parametrize("than_loi", [False, True])
def test_hoan_ghi_tin_hieu_dau_va_phat_lai_qua_term_thanh_ngat_khi_ra_khoi_khoi_ngoai_cung(than_loi):
    da = []
    with pytest.raises(NgatTerm):
        with term_thanh_ngat():
            with hoan():
                with hoan():
                    giao(signal.SIGTERM)                       # giữa ranh giới sở hữu: chỉ ghi
                    giao(signal.SIGINT)                        # tín hiệu sau không thay tín hiệu đầu
                    da.append("trong")
                da.append("ra-khoi-trong")                     # khối trong ra: chưa ném
                if than_loi:
                    raise OSError("lỗi thân khối")             # ngắt đang chờ vẫn thắng — không bị nuốt
            da.append("KHONG-TOI")
    assert da == ["trong", "ra-khoi-trong"]


def test_luong_phu_hoan_khong_doi_handler_khong_hoan():
    with term_thanh_ngat():
        cai, thay = signal.getsignal(signal.SIGTERM), []

        def chay():
            with hoan():
                thay.append(signal.getsignal(signal.SIGTERM))
        t = threading.Thread(target=chay)
        t.start()
        t.join()
        assert thay == [cai] and signal.getsignal(signal.SIGTERM) is cai
```

`tests/test_chay_gioi_han_ngat.py` (mới, nguyên văn):

```python
"""B03 (vòng 1), R2-02/R2-03 (vòng 2): `chay_gioi_han` (thân hàm của A-T4 + `stdin=`) dưới `term_thanh_ngat`. SIGTERM
THẬT (`raise_signal` vào CHÍNH tiến trình test) tới ngay sau Popen đi qua CẢ HAI lớp — bộ ghi của `hoan()` trong
`khoi_chay` (A) rồi handler `term_thanh_ngat` (B) khi `Nhom` đã ở `chu` — con vẫn bị đóng ống + thu hồi rồi `NgatTerm`
mới nổi lên. Lỗi/ngắt tiêm tại ĐIỂM ĐỌC THẬT (`_doc` trong vòng selector), ngắt lần hai lúc thu hồi: vẫn đóng ống +
thu hồi đúng một lần. Tiến trình thật chỉ là `python -c` của user test."""
import os
import signal
import subprocess
import sys
from types import SimpleNamespace

import pytest

from test_vong_doi import _song
from tram.kiem import chay_gioi_han as cgh
from tram.kiem.chay_gioi_han import chay_gioi_han
from tram.kiem.ngat import NgatTerm, term_thanh_ngat
from tram.kiem.vong_doi import LoiThuHoi, khoi_chay, kill_cuc_bo

PY = sys.executable


def popen_term(goi):
    def popen(argv, **kw):
        p = subprocess.Popen(argv, **kw)
        goi.append(p)
        assert callable(signal.getsignal(signal.SIGTERM))           # bộ ghi của `hoan()` — không phải mặc định
        signal.raise_signal(signal.SIGTERM)
        return p
    return popen


def test_sigterm_that_ngay_sau_popen_qua_hai_lop_con_van_bi_thu_hoi():
    goi = []
    try:
        with term_thanh_ngat():
            with pytest.raises(NgatTerm):
                chay_gioi_han([PY, "-c", "import time; time.sleep(60)"], kill=kill_cuc_bo, timeout=30,
                              capture_output=True, khoi=lambda a, **kw: khoi_chay(a, popen=popen_term(goi), **kw))
        assert not _song(goi[0].pid) and goi[0].stdout.closed and goi[0].returncode is not None
    finally:
        for p in goi:
            if p.poll() is None:
                p.kill()
                p.wait(5)


def nhom_gia(goi, sach, sau_thu=None):
    r, w = os.pipe()
    os.write(w, b"BI-MAT-ENV")                                       # có dữ liệu: selector báo đọc được ngay

    class N:
        p = SimpleNamespace(pid=4242, returncode=None, stdin=None, stdout=os.fdopen(r, "rb"), stderr=None)

        def thu_hoi(self):
            goi.append("thu")
            if sau_thu:
                sau_thu()
            return sach
    return N(), w


@pytest.mark.parametrize("sach", [True, False])
@pytest.mark.parametrize("loi", [KeyboardInterrupt, OSError])
def test_loi_hay_ngat_tai_diem_doc_van_dong_ong_va_thu_hoi(monkeypatch, loi, sach):
    """`_doc` (os.read của vòng selector) ném: đóng ống của ta rồi thu hồi. Chưa xác nhận → `LoiThuHoi` THAY lỗi
    thường (không nối chuỗi); ngắt vẫn là ngắt."""
    goi = []
    n, w = nhom_gia(goi, sach)

    def doc(fd, k):
        raise loi("BI-MAT-ENV")
    monkeypatch.setattr(cgh, "_doc", doc)
    mong = LoiThuHoi if loi is OSError and not sach else loi
    try:
        with pytest.raises(mong) as e:
            chay_gioi_han(["x"], kill=kill_cuc_bo, timeout=10, capture_output=True, khoi=lambda *a, **kw: n)
        assert goi == ["thu"] and n.p.stdout.closed
        assert mong is not LoiThuHoi or ("BI-MAT-ENV" not in str(e.value) and e.value.__suppress_context__)
    finally:
        os.close(w)


def test_sigterm_lan_hai_luc_thu_hoi_khong_cat_ngang_va_thang_loi_doc(monkeypatch):
    goi = []
    n, w = nhom_gia(goi, True, sau_thu=lambda: signal.getsignal(signal.SIGTERM)(signal.SIGTERM, None))

    def doc(fd, k):
        raise OSError("đọc hỏng")
    monkeypatch.setattr(cgh, "_doc", doc)
    try:
        with term_thanh_ngat():
            with pytest.raises(NgatTerm):
                chay_gioi_han(["x"], kill=kill_cuc_bo, timeout=10, capture_output=True, khoi=lambda *a, **kw: n)
        assert goi == ["thu"] and n.p.stdout.closed                  # thu hồi chạy hết MỘT lần, rồi mới ngắt
    finally:
        os.close(w)
```

`tests/test_chay_gioi_han.py` (sửa — bản vá):

```diff
--- a/tests/test_chay_gioi_han.py
+++ b/tests/test_chay_gioi_han.py
@@ -1,4 +1,5 @@
 """`chay_gioi_han` (3C-B): như `subprocess.run` nhưng có hạn, thu hồi cả cây, ngoại lệ không mang argv/stdout."""
+import os
 import subprocess
 import sys
 import time
@@ -60,6 +61,40 @@
     assert goi == []
 
 
+def test_stdin_la_file_object_truyen_thang_khong_doc_vao_ram(tmp_path):
+    goi = []
+
+    def khoi(argv, **kw):
+        goi.append(kw["stdin"])
+        return khoi_chay(argv, **kw)
+    (f := tmp_path / "vao").write_bytes(b"abc")
+    with open(f, "rb") as vao:
+        r = chay_gioi_han([PY, "-c", "import sys; print(sys.stdin.read().upper())"], kill=kill_cuc_bo, timeout=10,
+                          capture_output=True, text=True, stdin=vao, khoi=khoi)
+        assert goi == [vao] and not vao.closed                      # người gọi giữ và tự đóng bản sao của mình
+    assert r.stdout == "ABC\n"
+
+
+def test_input_va_stdin_loai_tru_truoc_khi_spawn(tmp_path):
+    goi = []
+    with pytest.raises(ValueError, match="loại trừ"):
+        chay_gioi_han(["x"], kill=kill_cuc_bo, timeout=1, input=b"BI-MAT-ENV", stdin=subprocess.DEVNULL,
+                      khoi=lambda *a, **k: goi.append(1))
+    assert goi == []
+
+
+def test_stdin_ong_nguon_qua_han_thi_thu_hoi_khong_kem_du_lieu(tmp_path):
+    r, w = os.pipe()
+    os.write(w, b"BI-MAT-ENV")                                      # nguồn còn mở, không EOF: đích chờ mãi
+    try:
+        with pytest.raises(subprocess.TimeoutExpired) as e:
+            chay_gioi_han([PY, "-c", "import sys; sys.stdin.read()"], kill=kill_cuc_bo, timeout=0.3, stdin=r)
+        assert "BI-MAT-ENV" not in str(e.value) and e.value.output is None
+    finally:
+        os.close(r)
+        os.close(w)
+
+
 class _PopenTreo(PopenGia):
     stdin = stdout = stderr = None
 
```

- [ ] **Step 2: Chạy, thấy ĐỎ**

```bash
C=<thư mục PATH chặn host>; PATH="$C/bin:$PATH" PYTHONPATH="$C/plugin" UV_OFFLINE=1 uv run pytest -p chan_host -q tests/test_ngat.py tests/test_chay_gioi_han.py tests/test_chay_gioi_han_ngat.py
```

Kết quả THẬT trên `f4fa3a8` + plan A T1–T8 + Task 1–5 (18/10):

```
E   ImportError: cannot import name 'NgatTerm' from 'tram.kiem.ngat'          (test_ngat.py, test_chay_gioi_han_ngat.py)
!!!!!!!!!!!!!!!!!!! Interrupted: 2 errors during collection !!!!!!!!!!!!!!!!!!!!
2 errors in 0.13s
```

Đỏ ở mức hành vi (đã thêm `NgatTerm`/`term_thanh_ngat` vào `ngat.py`, `chay_gioi_han.py` còn là bản A-T4):

```
E           TypeError: chay_gioi_han() got an unexpected keyword argument 'stdin'   (×3)
FAILED tests/test_chay_gioi_han.py::test_input_va_stdin_loai_tru_truoc_khi_spawn
FAILED tests/test_chay_gioi_han.py::test_stdin_la_file_object_truyen_thang_khong_doc_vao_ram
FAILED tests/test_chay_gioi_han.py::test_stdin_ong_nguon_qua_han_thi_thu_hoi_khong_kem_du_lieu
3 failed, 18 passed in 8.29s
```

Sáu ca `tests/test_chay_gioi_han_ngat.py` XANH ngay trên thân hàm A-T4 khi đã có `term_thanh_ngat` — đó là chủ đích của bản tích hợp (R2-03): hợp đồng sở hữu B03 nay do A giữ, test của B khoá nó qua cả hai lớp (SIGTERM THẬT ngay sau Popen; `_doc` ném OSError/KeyboardInterrupt với thu hồi True/False; SIGTERM lần hai lúc thu hồi). Bằng chứng đỏ của hành vi đó nằm ở A-T2/A-T4 (người gọi để con sống; `_don` cũ bị lỗi đóng ống chặn thu hồi). Bản vòng 2 của B-T6/T7 không ghép được với hợp đồng A: `ong_chep.py` vòng 2 trên cây A → `TypeError: nguon_archive() missing 1 required keyword-only argument: 'chu'` (Task 7).

- [ ] **Step 3: Viết mã**

`tram/kiem/ngat.py` (sửa — bản vá):

```diff
--- a/tram/kiem/ngat.py
+++ b/tram/kiem/ngat.py
@@ -4,7 +4,10 @@
 khôi phục — rồi PHÁT LẠI theo thứ tự nhận (`raise_signal`, handler cũ chạy đồng bộ: KeyboardInterrupt, handler của
 người gọi, hay mặc định). Tín hiệu đầu ném thì các tín hiệu sau không phát lại; ngắt đang chờ thắng lỗi của thân khối.
 Khối lồng nhau dùng chung một lần ghi. Không hoãn ngoài luồng chính (handler Python chỉ chạy ở luồng chính) và với tín
-hiệu có handler đặt từ C (`getsignal` None). Không hứa gì với SIGKILL."""
+hiệu có handler đặt từ C (`getsignal` None). Không hứa gì với SIGKILL.
+Plan B (bs-863.19, B03): `term_thanh_ngat` — CHỈ CLI cha cài, ở luồng chính — biến SIGTERM thành `NgatTerm` (một
+`KeyboardInterrupt`), SIGINT thành `KeyboardInterrupt`; trong `hoan()` chúng được ghi rồi phát lại QUA chính handler này
+khi rời khối (sau khi `Nhom` đã ở `chu` / sau khi thu hồi xong), ra khỏi thì khôi phục handler cũ của CẢ HAI."""
 import signal
 import threading
 from contextlib import contextmanager
@@ -52,3 +55,29 @@
         _muc -= 1
         if _muc == 0:
             _khoi_phuc()
+
+
+class NgatTerm(KeyboardInterrupt):
+    """CLI cha nhận SIGTERM — đi đường dọn như Ctrl-C."""
+
+
+def _thanh_ngat(so, khung):
+    raise NgatTerm("SIGTERM") if so == signal.SIGTERM else KeyboardInterrupt()
+
+
+@contextmanager
+def term_thanh_ngat(dat=signal.signal):
+    cu = [(so, signal.getsignal(so)) for so in (signal.SIGTERM, signal.SIGINT)]
+    try:
+        for so, _ in cu:
+            dat(so, _thanh_ngat)
+        yield
+    finally:
+        loi = None
+        for so, h in reversed(cu):
+            try:
+                dat(so, h)
+            except BaseException as e:          # ngắt ngay sau khi trả handler: khôi phục nốt
+                loi = loi or e
+        if loi is not None:
+            raise loi
```

`tram/kiem/chay_gioi_han.py` (sửa — bản vá):

```diff
--- a/tram/kiem/chay_gioi_han.py
+++ b/tram/kiem/chay_gioi_han.py
@@ -7,7 +7,10 @@
 `with` ở mọi lối ra) và chờ gốc bằng `Nhom.cho` (xác giữ số nhóm gốc tới `thu_hoi`). Hạn tuyệt đối tính TRƯỚC spawn;
 spawn và mọi bước sau trong vùng sở hữu (`so_huu`): lỗi/ngắt ở đâu cũng `_don` — đóng TỪNG ống (lỗi đóng không chặn
 ống sau) rồi LUÔN thu hồi, cả hai trong `ngat.hoan()`. Chưa xác nhận → `LoiThuHoi` THAY lỗi thường/lỗi ống (`from
-None`); ngắt (KeyboardInterrupt) vẫn là ngắt — mọi ngắt đều là "chưa công nhận" ở người gọi."""
+None`); ngắt (KeyboardInterrupt) vẫn là ngắt — mọi ngắt đều là "chưa công nhận" ở người gọi.
+H1 (V2-6a, bs-863.18 — plan B): `stdin=` (file object/FD, vd. ống của `git archive`) đưa THẲNG cho Popen — không đọc vào
+RAM, `p.stdin` khi đó là None nên `_ong`/`_don` không đụng tới; loại trừ `input` TRƯỚC spawn; người gọi giữ và đóng bản
+sao của mình (sau khi hàm trả, để nguồn nhận SIGPIPE)."""
 import contextlib
 import math
 import os
@@ -75,19 +78,21 @@
 
 
 def chay_gioi_han(argv: list[str], *, kill: Kill, timeout: float, capture_output: bool = False, text: bool = False,
-                  input=None, env=None, cwd=None, check: bool = False,
+                  input=None, stdin=None, env=None, cwd=None, check: bool = False,
                   khoi: Callable = khoi_chay) -> subprocess.CompletedProcess:
     if not math.isfinite(timeout):
         raise ValueError("timeout phải hữu hạn")
+    if input is not None and stdin is not None:
+        raise ValueError("input và stdin loại trừ nhau")
     ten = [Path(str(argv[0])).name] if argv else []
     ong = subprocess.PIPE if capture_output else subprocess.DEVNULL
     if text and isinstance(input, str):
         input = input.encode()
+    vao = stdin if stdin is not None else subprocess.PIPE if input is not None else subprocess.DEVNULL
     het, chu = time.monotonic() + timeout, []                            # hạn tuyệt đối tính TRƯỚC spawn
     try:
         try:
-            n = khoi(list(argv), kill=kill, stdin=subprocess.PIPE if input is not None else subprocess.DEVNULL,
-                     stdout=ong, stderr=ong, env=env, cwd=cwd, chu=chu)
+            n = khoi(list(argv), kill=kill, stdin=vao, stdout=ong, stderr=ong, env=env, cwd=cwd, chu=chu)
         except OSError as e:                    # `khoi_chay`: OSError chỉ khi Popen chưa tạo được tiến trình
             raise OSError(f"{ten}: không khởi chạy được ({type(e).__name__})") from None
         chu[:] = chu or [n]                     # `khoi` giả không tự ghi `chu`: nhận Nhom nó trả
```

- [ ] **Step 4: Chạy, thấy XANH**

```bash
C=<thư mục PATH chặn host>; PATH="$C/bin:$PATH" PYTHONPATH="$C/plugin" UV_OFFLINE=1 uv run pytest -p chan_host -q tests/test_ngat.py tests/test_chay_gioi_han.py tests/test_chay_gioi_han_ngat.py tests/test_vong_doi.py tests/test_danh_tinh.py tests/test_so_huu_ong.py tests/test_so_huu_bo_chay.py
```

Kết quả THẬT: ba file của task `21 passed in 8.55s`; cùng test của A (`test_vong_doi`, `test_danh_tinh`, `test_so_huu_ong`, `test_so_huu_bo_chay`): `57 passed in 18.80s`; nhật ký chặn không thêm dòng; `ps` sau chạy không còn `time.sleep(60)` của test.

- [ ] **Step 5: Commit**

```bash
git add tests/test_ngat.py tests/test_chay_gioi_han_ngat.py tests/test_chay_gioi_han.py tram/kiem/ngat.py tram/kiem/chay_gioi_han.py
git commit -m "feat(v2-6a): term_thanh_ngat trên hoan() của V2-0, chay_gioi_han nhận stdin (bs-863.18, B03, R2-03)"
```

### Task 7: Ống `git archive | tar` có chủ hai đầu, một ngân sách hạn, nguồn chưa thu hồi thắng mọi lỗi (V2-6a; B02 vòng 1)

**Đợt:** 2 · **Phải xong trước:** — (cần Task 6) · **Bead:** bs-863.18. dot7-C02: `git archive` chỉ `wait(timeout)` trong finally — quá hạn thì nguồn còn sống; `_chay` dưới sudo dùng `subprocess.run` ngoài primitive. Mới: nguồn qua `khoi_chay` (nhóm riêng, kill cục bộ — tiến trình của trạm), spawn trong `ngat.hoan()`; đích `tar` qua `chay_gioi_han(stdin=ống)`; luôn đóng bản sao ống của trạm và thu hồi nguồn trong `finally`. **B02 (vòng 1):** (1) hợp đồng ưu tiên — nguồn CHƯA xác nhận thu hồi thì `chay_ong` ném `loi` (bản chép truyền `LoiBanChep`) THAY mọi lỗi khác (đích lỗi, đích không khởi chạy, đóng ống lỗi), `from None` — không nối chuỗi lỗi bên dưới (lỗi đích có thể mang byte môi trường); ngắt vẫn là ngắt; (2) MỘT hạn thật cho cả ống: hạn tính TRƯỚC khi chuẩn bị nguồn, đích nhận `timeout=` đúng phần còn lại (hết thì không chạy đích, ném `TimeoutExpired`), nguồn chờ phần còn lại sau đó; (3) mọi nhánh lỗi ra khỏi `chep_ban` là ngoại lệ không phải `CayKhacNguon` nên `kiem_lai` đóng cổng (`cong.dong` trong `except BaseException`) — test ở mức `kiem_lai` khoá lý do đóng là `LoiBanChep` của nguồn chứ không phải lỗi đích. `LoiThuHoi` của lệnh bản chép → `LoiBanChep` vì vòng tick chỉ bắt OSError. `kiem_lai` truyền kill của principal. Tách `ong_chep.py` để `ban_chep.py` giữ 122 dòng; `ong_chep` nhận lớp lỗi qua tham số `loi` thay vì import `LoiBanChep` (tránh import vòng). Không đổi metadata tar/cây (R7). **R2-02/R2-03 (vòng 2):** nguồn theo hợp đồng sở hữu của plan A — `nguon_archive(..., chu=chu)` (bắt buộc), `Nhom` vào `chu` trong `hoan()` của `khoi_chay` trước mọi lối ra (kể cả ngắt phát lại), `chay_ong` thu hồi bằng `thu_hoi_con_lai(chu)` trong `finally`; không còn khối `hoan()` riêng quanh spawn nguồn (đã nằm trong `khoi_chay`).

**Files:**
- Create: `tests/test_ban_chep_pipeline_han.py`
- Create: `tests/test_ong_chep_uu_tien.py`
- Create: `tram/giao_viec/ong_chep.py`
- Modify: `tram/giao_viec/cay_kiem.py`
- Modify: `tram/giao_viec/ban_chep.py`
- Modify: `tram/giao_viec/kiem_lai.py`

**Interfaces:**
- Consumes: Task 6: `chay_gioi_han(stdin=)`; plan A: hợp đồng sở hữu `so_huu` (`khoi_chay(chu=)` bắt buộc, `thu_hoi_con_lai`), `Nhom.p/.cho/.thu_hoi`, `kill_cuc_bo`, `Kill`, `LoiThuHoi`.
- Produces: `cay_kiem.nguon_archive(kho, commit, *, chu, khoi=khoi_chay) -> Nhom` (`chu` bắt buộc — `Nhom` của nguồn vào danh sách sở hữu của `chay_ong` TRƯỚC mọi lối ra, kể cả ngắt phát lại); `ong_chep.chay_ong(kho, commit, dich, *, chay, han, loi=LoiThuHoi) -> tuple[int | None, int]` (mã nguồn — None khi hết hạn, mã đích; ném `loi` khi nguồn chưa xác nhận thu hồi, `TimeoutExpired` khi hết hạn chung; `chay(dich, stdin=…, timeout=…)`); `ban_chep._chay(argv, *, kill, timeout=None, **kw)`; `ban_chep.chep_ban/nhan_moi_truong/don_ban(..., kill=kill_cuc_bo)` (kill mặc định cục bộ — production truyền kill của principal qua `kiem_lai`).

- [ ] **Step 1: Viết test thất bại**

`tests/test_ban_chep_pipeline_han.py` (mới, nguyên văn):

```python
"""H1 (V2-6a, bs-863.18; dot7-C02): ống `git archive | tar` của bản chép có chủ HAI đầu và một hạn chung. Đích hết hạn,
lỗi, thoát sớm, không khởi chạy được hay không xác nhận thu hồi → nguồn vẫn bị thu hồi, kết quả không công nhận, byte
môi trường không vào ngoại lệ. Tiến trình thật chỉ là `git archive` + `python -c` của user test trong tmp_path. Ưu tiên
trạng thái chưa thu hồi và ngân sách hạn còn lại (B02): `test_ong_chep_uu_tien.py`."""
import signal
import subprocess
import sys
import time

import pytest

from kho_kiem_gia import dung_kho
from test_kiem_lai_principal import chay, m  # noqa: F401 — fixture `m` dùng chung
from test_vong_doi import _song
from tram.giao_viec import ban_chep, cay_kiem, kiem_lai, ong_chep
from tram.giao_viec.ban_chep import CayKhacNguon, LoiBanChep, chep_ban, nhan_moi_truong
from tram.giao_viec.git_kiem import fetch
from tram.kiem.vong_doi import LoiThuHoi, khoi_chay, kill_cuc_bo

PY = sys.executable
TAR = "/usr/bin/tar"


@pytest.fixture
def ong(tmp_path, monkeypatch):
    """Kho có archive 2 MiB (lớn hơn bộ đệm ống: nguồn còn đang ghi khi đích dừng); ghi lại Nhom của nguồn."""
    k = dung_kho(tmp_path)
    sha = k.day("tram/hr-1", {"lon.txt": "x" * (2 << 20)}, tu=k.main)
    fetch(k.kho)
    monkeypatch.setattr(ban_chep, "THOI_GIAN", 1.0)
    nguon = []
    goc = ong_chep.nguon_archive
    monkeypatch.setattr(ong_chep, "nguon_archive", lambda *a, **kw: nguon.append(goc(*a, **kw)) or nguon[-1])
    return k, sha, tmp_path / "kiem" / "g-1-ab", nguon


def boc_tar(thay: list[str]):
    return lambda a: thay if a[0] == TAR else a


def test_nguon_archive_la_nhom_rieng_kill_cuc_bo_va_co_chu(tmp_path):
    k, goi, chu = dung_kho(tmp_path), [], []
    cay_kiem.nguon_archive(k.kho, k.main, chu=chu, khoi=lambda a, **kw: goi.append((a, kw)))
    (a, kw), = goi
    assert a[-3:] == ["archive", "--format=tar", k.main] and kw["kill"] is kill_cuc_bo and kw["chu"] is chu
    assert (kw["stdin"], kw["stdout"], kw["stderr"]) == (subprocess.DEVNULL, subprocess.PIPE, subprocess.DEVNULL)


@pytest.mark.parametrize("dich, loi", [([PY, "-c", "import time; time.sleep(60)"], subprocess.TimeoutExpired),
                                       ([PY, "-c", "import sys; sys.exit(3)"], LoiBanChep),
                                       (["/khong-co/tar"], OSError)])
def test_dich_qua_han_loi_hoac_khong_chay_thi_nguon_van_bi_thu_hoi(ong, dich, loi):
    k, sha, wt, nguon = ong
    t0 = time.monotonic()
    with pytest.raises(loi):
        chep_ban(k.kho, sha, wt, boc=boc_tar(dich))
    assert time.monotonic() - t0 < 15
    n, = nguon
    assert n.p.returncode is not None and not _song(n.p.pid) and n.p.stdout.closed


def test_nguon_treo_khi_dich_xong_thi_het_phan_han_con_lai_roi_thu_hoi(ong, monkeypatch):
    k, sha, wt, nguon = ong
    treo = lambda *a, chu, **kw: nguon.append(khoi_chay([PY, "-c", "import time; time.sleep(60)"], kill=kill_cuc_bo,
                                                        chu=chu, stdout=subprocess.PIPE)) or nguon[-1]
    monkeypatch.setattr(ong_chep, "nguon_archive", treo)
    t0 = time.monotonic()
    with pytest.raises(LoiBanChep, match=r"git archive \(mã None\)"):
        chep_ban(k.kho, sha, wt, boc=boc_tar([PY, "-c", "pass"]))
    assert time.monotonic() - t0 < 10 and not _song(nguon[0].p.pid)


def test_dich_khong_xac_nhan_thu_hoi_thanh_loi_ban_chep_nguon_van_thu_hoi(ong, monkeypatch):
    k, sha, wt, nguon = ong
    that = ban_chep.chay_gioi_han

    def chay(argv, **kw):
        if argv[0] == TAR:
            raise LoiThuHoi("tar: không xác nhận thu hồi")
        return that(argv, **kw)
    monkeypatch.setattr(ban_chep, "chay_gioi_han", chay)
    with pytest.raises(LoiBanChep, match="không xác nhận thu hồi"):        # tick chỉ bắt OSError, không RuntimeError
        chep_ban(k.kho, sha, wt, boc=lambda a: a)
    assert not _song(nguon[0].p.pid)


def test_moi_truong_qua_han_khong_lo_byte_env(ong):
    k, sha, wt, _ = ong
    (env := wt.parent / "env.testing").parent.mkdir(parents=True)
    env.write_text("DB_PASSWORD=BI_MAT_ENV\n")
    with pytest.raises(subprocess.TimeoutExpired) as e:
        nhan_moi_truong(k.kho, sha, wt, env, ".env.testing", boc=boc_tar([PY, "-c", "import time; time.sleep(60)"]))
    assert "BI_MAT_ENV" not in f"{e.value}{e.value!r}" and e.value.output is None and e.value.stderr is None


def test_kiem_lai_truyen_kill_cua_principal_cho_ban_chep(m, monkeypatch):
    goi = []

    def kill(g, s):
        pass

    def chep(*a, **kw):
        goi.append(kw["kill"])
        raise CayKhacNguon("giả")
    monkeypatch.setattr(kiem_lai, "chep_ban", chep)
    monkeypatch.setattr(kiem_lai, "don_ban", lambda wt, **kw: goi.append(kw["kill"]))
    assert chay(m, {"kiem.sh": "exit 0\n"}, kill=kill).loi == "cay-khac-nguon" and goi == [kill, kill]


def test_ctrl_c_ngay_sau_khi_nguon_spawn_nguon_da_co_chu_va_bi_thu_hoi(ong, monkeypatch):
    """R2-02: Ctrl-C THẬT ngay sau Popen của nguồn — hoãn, phát lại khi nguồn đã ở `chu`: thu hồi rồi mới ngắt."""
    k, sha, wt, _ = ong
    goi, that = [], cay_kiem.nguon_archive

    def popen(a, **kw):
        goi.append(subprocess.Popen(a, **kw))
        signal.raise_signal(signal.SIGINT)
        return goi[-1]
    monkeypatch.setattr(ong_chep, "nguon_archive", lambda *a, **kw: that(
        *a, khoi=lambda x, **k: khoi_chay(x, popen=popen, **k), **kw))
    with pytest.raises(KeyboardInterrupt):
        chep_ban(k.kho, sha, wt, boc=lambda a: a)
    assert goi[0].returncode is not None and not _song(goi[0].pid)
```

`tests/test_ong_chep_uu_tien.py` (mới, nguyên văn):

```python
"""B02 (vòng 1): ống `git archive | tar` — nguồn CHƯA xác nhận thu hồi thắng MỌI lỗi khác (đích xong/lỗi/không khởi
chạy, đóng ống lỗi), không nối chuỗi lỗi bên dưới, cổng đóng vì bản chép; MỘT hạn cho cả ống: đích nhận đúng phần còn
lại, chuẩn bị nguồn tiêu hết hạn thì không chạy đích. Tiến trình thật chỉ là `git archive` + `python -c` của user test
trong tmp_path; nguồn "không thu hồi được" là Nhom GIẢ."""
import os
import subprocess
import time

import pytest

from test_ban_chep_pipeline_han import PY, TAR, boc_tar, ong  # noqa: F401 — fixture `ong` dùng chung
from test_kiem_lai_cong import chay as chay_cong, cong
from test_kiem_lai_principal import m  # noqa: F401 — fixture `m` dùng chung
from test_vong_doi import _song
from tram.giao_viec import ban_chep, cay_kiem, ong_chep
from tram.giao_viec.ban_chep import LoiBanChep, chep_ban
from tram.kiem.vong_doi import Nhom


class _OngLoi:
    """Ống THẬT của nguồn, nhưng `close` ném (lỗi đóng ống mang byte môi trường)."""
    def __init__(self, f):
        self.f = f

    def fileno(self):
        return self.f.fileno()

    def close(self):
        self.f.close()
        raise OSError("đóng ống: BI_MAT_ENV")


def _nguon_khong_thu_hoi(monkeypatch, dong_loi: bool, goi: list):
    r, w = os.pipe()
    os.close(w)

    class NguonGia(Nhom):
        def __init__(self):
            f = os.fdopen(r, "rb")
            self.p = type("P", (), {"stdout": _OngLoi(f) if dong_loi else f, "pid": 0})()

        def cho(self, giay):
            return 0

        def thu_hoi(self, **kw):
            goi.append("thu")
            return False
    monkeypatch.setattr(ong_chep, "nguon_archive", lambda *a, **kw: NguonGia())


def _dich_loi(monkeypatch):
    that = ban_chep.chay_gioi_han

    def chay(argv, **kw):
        if argv[0] == TAR:
            raise OSError("tar: BI_MAT_ENV")                        # lỗi đích có thể mang byte môi trường
        return that(argv, **kw)
    monkeypatch.setattr(ban_chep, "chay_gioi_han", chay)


@pytest.mark.parametrize("dich", ["xong", "loi", "khong_chay", "dong_ong_loi"])
def test_nguon_khong_xac_nhan_thu_hoi_thang_moi_loi_khac(ong, monkeypatch, dich):
    """B02: nguồn trả thu_hoi False — dù đích xong, lỗi (mang byte env), không khởi chạy hay đóng ống lỗi — kết quả
    LUÔN là `LoiBanChep` "thu hồi CHƯA", không nối chuỗi lỗi bên dưới."""
    k, sha, wt, _ = ong
    goi = []
    _nguon_khong_thu_hoi(monkeypatch, dich == "dong_ong_loi", goi)
    if dich == "loi":
        _dich_loi(monkeypatch)
    tar = {"khong_chay": ["/khong-co/tar"]}.get(dich, [PY, "-c", "import sys; sys.stdin.buffer.read()"])
    with pytest.raises(LoiBanChep, match="thu hồi CHƯA") as e:
        chep_ban(k.kho, sha, wt, boc=(lambda a: a) if dich == "loi" else boc_tar(tar))
    assert goi == ["thu"] and "BI_MAT_ENV" not in f"{e.value}{e.value!r}"
    assert e.value.__cause__ is None and e.value.__suppress_context__


def test_dich_loi_va_nguon_chua_thu_hoi_thi_cong_dong_vi_nguon(m, monkeypatch):
    """B02: tổ hợp nguy hiểm ở mức `kiem_lai` — cổng đóng với lý do là bản chép chưa thu hồi (LoiBanChep), không phải
    lỗi của đích."""
    goi, c = [], cong(m[2])
    _nguon_khong_thu_hoi(monkeypatch, False, goi)
    _dich_loi(monkeypatch)
    with pytest.raises(LoiBanChep, match="thu hồi CHƯA"):
        chay_cong(m, c)
    assert goi == ["thu"] and c.trang_thai() == {"trang_thai": "dong", "ly_do": "lượt g-1: LoiBanChep"}


def test_dich_nhan_phan_han_con_lai_chuan_bi_het_han_thi_khong_chay_dich(ong, monkeypatch):
    """B02: MỘT hạn cho cả ống (THOI_GIAN = 1 s) tính trước khi chuẩn bị nguồn — đích nhận đúng phần còn lại; chuẩn bị
    đã tiêu hết hạn → không chạy đích, nguồn vẫn thu hồi, ném TimeoutExpired."""
    k, sha, wt, nguon = ong
    goc, cham, han = cay_kiem.chuan_bi_thuoc_tinh, [0.4], []
    monkeypatch.setattr(cay_kiem, "chuan_bi_thuoc_tinh", lambda kho: time.sleep(cham[0]) or goc(kho))

    that = ban_chep.chay_gioi_han

    class Dung(Exception):
        pass

    def chay(argv, **kw):
        if "stdin" in kw:                                           # đích của ống
            han.append(kw.get("timeout"))
            raise Dung
        return that(argv, **kw)
    monkeypatch.setattr(ban_chep, "chay_gioi_han", chay)
    with pytest.raises(Dung):
        chep_ban(k.kho, sha, wt, boc=lambda a: a)
    assert han and 0 < han[0] <= 0.6 and not _song(nguon[0].p.pid)
    cham[0], han[:] = 1.2, []
    with pytest.raises(subprocess.TimeoutExpired):
        chep_ban(k.kho, sha, wt.with_name("g-1-cd"), boc=lambda a: a)
    assert han == [] and not _song(nguon[1].p.pid) and nguon[1].p.stdout.closed
```

- [ ] **Step 2: Chạy, thấy ĐỎ**

```bash
C=<thư mục PATH chặn host>; PATH="$C/bin:$PATH" PYTHONPATH="$C/plugin" UV_OFFLINE=1 uv run pytest -p chan_host -q tests/test_ban_chep_pipeline_han.py tests/test_ong_chep_uu_tien.py
```

Kết quả THẬT trên `f4fa3a8` + plan A T1–T8 + Task 1–6 (trước khi có mã của task):

```
E   ImportError: cannot import name 'ong_chep' from 'tram.giao_viec' (…/tram/giao_viec/__init__.py)   (×2)
!!!!!!!!!!!!!!!!!!! Interrupted: 2 errors during collection !!!!!!!!!!!!!!!!!!!!
2 errors in 0.12s
```

**R2-03 — bản vòng 2 không ghép được với hợp đồng của A:** `ong_chep.py` của bản vòng 2 đặt lên cây A + Task 1–7 (mã mới còn lại giữ nguyên): `7 failed, 8 passed` — `TypeError: nguon_archive() missing 1 required keyword-only argument: 'chu'` (×6) và `test_nguon_treo_…` (`<lambda>() missing … 'chu'`): bản cũ spawn nguồn KHÔNG có danh sách sở hữu.

Lịch sử vòng 1 — tái hiện B02 bằng `ong_chep.py`/`ban_chep.py`/`cay_kiem.py`/`kiem_lai.py` của bản plan trước vòng 1 (trên `7921f26`):

```
E       AssertionError: assert (None is None and False)                   ← [xong]: có báo "thu hồi CHƯA" nhưng nối chuỗi
E           OSError: tar: BI_MAT_ENV                                       ← [loi]: lỗi đích (mang byte env) che nguồn chưa thu hồi
E                   OSError: ['tar']: không khởi chạy được (FileNotFoundError)   ← [khong_chay]: như trên
E       OSError: đóng ống: BI_MAT_ENV                                      ← [dong_ong_loi]: như trên
E           OSError: tar: BI_MAT_ENV                                       ← kiem_lai: cổng đóng vì "OSError", không vì nguồn
E       assert ([1.0] and 1.0 <= 0.6)                                      ← đích nhận cả hạn, không phải phần còn lại
FAILED tests/test_ban_chep_pipeline_han.py::test_nguon_treo_khi_dich_xong_thi_het_phan_han_con_lai_roi_thu_hoi   (thông báo đổi)
FAILED tests/test_ong_chep_uu_tien.py::test_nguon_khong_xac_nhan_thu_hoi_thang_moi_loi_khac[xong]
FAILED tests/test_ong_chep_uu_tien.py::test_nguon_khong_xac_nhan_thu_hoi_thang_moi_loi_khac[loi]
FAILED tests/test_ong_chep_uu_tien.py::test_nguon_khong_xac_nhan_thu_hoi_thang_moi_loi_khac[khong_chay]
FAILED tests/test_ong_chep_uu_tien.py::test_nguon_khong_xac_nhan_thu_hoi_thang_moi_loi_khac[dong_ong_loi]
FAILED tests/test_ong_chep_uu_tien.py::test_dich_loi_va_nguon_chua_thu_hoi_thi_cong_dong_vi_nguon
FAILED tests/test_ong_chep_uu_tien.py::test_dich_nhan_phan_han_con_lai_chuan_bi_het_han_thi_khong_chay_dich
7 failed, 7 passed in 8.35s
```

Các ca còn xanh với mã cũ (`test_nguon_archive_la_nhom_rieng_kill_cuc_bo`, ba ca `test_dich_qua_han_loi_hoac_khong_chay_…`, `test_dich_khong_xac_nhan_…`, `test_moi_truong_qua_han_khong_lo_byte_env`, `test_kiem_lai_truyen_kill_…`) là regression của dot7-C02 / dot6-Q06.

- [ ] **Step 3: Viết mã**

`tram/giao_viec/ong_chep.py` (mới, nguyên văn):

```python
"""Ống `git archive | tar -x` của bản chép kiểm có CHỦ cả hai đầu (H1 — V2-6a, bs-863.18; dot7-C02; B02/B03 vòng 1;
R2-02/R2-03 vòng 2). Nguồn `git archive` của TRẠM qua primitive P1 (nhóm riêng, kill cục bộ) theo hợp đồng sở hữu
`kiem.so_huu`: `nguon_archive(..., chu=chu)` — `Nhom` vào `chu` TRONG `ngat.hoan()` trước mọi lối ra, ngắt phát lại
lúc đó vẫn để nguồn có chủ ở `finally`. Đích `tar` dưới `tram-kiem` qua `chay` của người gọi (`chay_gioi_han` với kill
của principal), `stdin=` là ống của nguồn — không đọc archive vào RAM. MỘT hạn cho cả ống, tính TRƯỚC khi chuẩn bị
nguồn: đích nhận `timeout=` đúng phần CÒN LẠI (hết rồi thì không chạy đích), nguồn chờ phần còn lại sau đó. Mọi lối ra
(đích xong/lỗi/quá hạn/không khởi chạy, đóng ống lỗi, ngắt) → `thu_hoi_con_lai(chu)` trong `finally` (trong `hoan()`).
Ưu tiên: nguồn CHƯA xác nhận thu hồi → ném `loi` (mặc định `LoiThuHoi`) THAY mọi lỗi khác, kể cả lỗi đích, `from None`
— không nối chuỗi lỗi bên dưới (có thể mang byte môi trường); riêng ngắt (KeyboardInterrupt) vẫn là ngắt — người gọi
coi mọi ngắt là chưa sạch (cổng đóng)."""
import subprocess
import time
from collections.abc import Callable
from pathlib import Path

from tram.giao_viec.cay_kiem import nguon_archive
from tram.kiem.so_huu import thu_hoi_con_lai
from tram.kiem.vong_doi import LoiThuHoi


def chay_ong(kho: Path, commit: str, dich: list[str], *, chay: Callable, han: float,
             loi: type[BaseException] = LoiThuHoi) -> tuple[int | None, int]:
    """(mã `git archive` — None khi hết phần hạn còn lại, mã của đích). Ném `loi` khi nguồn chưa xác nhận thu hồi,
    `TimeoutExpired` khi hết hạn chung, hoặc lỗi của đích/đóng ống — SAU khi nguồn đã thu hồi."""
    het, chu, ma, ngat = time.monotonic() + han, [], None, False
    try:
        nguon = nguon_archive(kho, commit, chu=chu)
        chu[:] = chu or [nguon]             # nguồn giả không tự ghi `chu`: nhận Nhom nó trả
        try:
            con = het - time.monotonic()
            if con <= 0:                    # chuẩn bị nguồn đã tiêu hết hạn chung: không chạy đích
                raise subprocess.TimeoutExpired([Path(dich[0]).name], han)
            r = chay(dich, stdin=nguon.p.stdout, timeout=con)
        finally:
            nguon.p.stdout.close()
        ma = nguon.cho(max(0.0, het - time.monotonic()))
    except KeyboardInterrupt:
        ngat = True
        raise
    finally:
        if chu and not thu_hoi_con_lai(chu) and not ngat:
            raise loi("git archive: nguồn của ống CHƯA xác nhận thu hồi (thu hồi CHƯA) — không công nhận") from None
    return ma, r.returncode
```

`tram/giao_viec/cay_kiem.py` (sửa — bản vá):

```diff
--- a/tram/giao_viec/cay_kiem.py
+++ b/tram/giao_viec/cay_kiem.py
@@ -9,8 +9,11 @@
 import subprocess
 import tarfile
 import time
+from collections.abc import Callable
 from pathlib import Path
 
+from tram.kiem.vong_doi import Nhom, khoi_chay, kill_cuc_bo
+
 GIT = ("git", "-c", "core.hooksPath=/dev/null")
 THUOC_TINH = "* -export-ignore -export-subst\n"
 ARCHIVE = ("-c", "core.autocrlf=false", "-c", "core.eol=lf", "-c", "core.attributesFile=/dev/null", "-c",
@@ -55,11 +58,13 @@
         p.write_text(THUOC_TINH, encoding="utf-8")
 
 
-def nguon_archive(kho: Path, commit: str) -> subprocess.Popen:
-    """`git archive` của commit, stdout là ống — người gọi đóng ống và `wait()`."""
+def nguon_archive(kho: Path, commit: str, *, chu: list, khoi: Callable = khoi_chay) -> Nhom:
+    """`git archive` của commit qua primitive P1 (H1, V2-6a): nhóm/phiên riêng, kill cục bộ (tiến trình của TRẠM),
+    stdout là ống. Người gọi SỞ HỮU qua `chu` (hợp đồng `kiem.so_huu`): đóng `n.p.stdout` khi đích xong, `cho` có hạn,
+    thu hồi `chu` trong `finally`."""
     chuan_bi_thuoc_tinh(kho)
-    return subprocess.Popen([*GIT, *ARCHIVE, "-C", str(kho), "archive", "--format=tar", commit], env=_env(),
-                            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
+    return khoi([*GIT, *ARCHIVE, "-C", str(kho), "archive", "--format=tar", commit], kill=kill_cuc_bo, chu=chu,
+                env=_env(), stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
 
 
 def loi_cau_hinh_kho(kho: Path) -> str | None:
```

`tram/giao_viec/ban_chep.py` (sửa — bản vá):

```diff
--- a/tram/giao_viec/ban_chep.py
+++ b/tram/giao_viec/ban_chep.py
@@ -1,14 +1,11 @@
 """Bản chép kiểm do `tram-kiem` SỞ HỮU (D22, lát 3c; spec 3 §7.3 mục 5, spec 4 §6.2 bước 1, 3) — không root, không ACL.
-
 Trạm `git archive <commit>` từ kho kiểm, đưa qua stdin cho `tar -x` chạy DƯỚI `tram-kiem` (`boc`) vào một thư mục MỚI
-dưới `thu_muc_kiem`; môi trường kiểm cũng qua stdin (tar một file); `tram-kiem` tự `rm -rf` khi xong. Mọi thao tác
-trên cây đều dưới quyền `tram-kiem`, nên symlink/hardlink trong cây không với tới thứ gì `tram-kiem` vốn không với tới.
-Cây kiểm là repo git MỘT commit do `tram-kiem` tự dựng (D40 (b), `repo_ban_chep.py`) — không lịch sử kho thật.
-Fail-closed:
-- một lần kiểm lại một lúc trên máy (khoá `~/.tram/kiem-lai.khoa`, không chờ) — lần thứ hai ném `KiemLaiDangBan`;
-- `don_sach` (giết mọi tiến trình `tram-kiem`, xác nhận không còn) chạy trước khi chép và trước khi dọn — lỗi → ném;
-- `tar`, `git init/add/commit` lỗi hoặc cây git của bản chép khác cây commit gốc (R7) → ném, không chạy lệnh kiểm;
-- dọn xong mà thư mục vẫn còn → ném `LoiBanChep`: kết quả kiểm lại KHÔNG được trả về."""
+dưới `thu_muc_kiem`; môi trường kiểm cũng qua stdin (tar một file); `tram-kiem` tự `rm -rf` khi xong. H1: mọi lệnh
+qua `chay_gioi_han`, ống `git archive | tar` có chủ hai đầu (`ong_chep.py`). Mọi thao tác trên cây dưới quyền
+`tram-kiem`, nên symlink/hardlink trong cây không với tới thứ gì `tram-kiem` vốn không với tới. Cây kiểm là repo git
+MỘT commit do `tram-kiem` tự dựng (D40 (b), `repo_ban_chep.py`). Fail-closed: một lần kiểm lại một lúc (khoá
+`~/.tram/kiem-lai.khoa`, không chờ — lần hai ném `KiemLaiDangBan`); `don_sach` trước khi chép và trước khi dọn — lỗi
+→ ném; `tar`/`git` lỗi hoặc cây khác cây commit gốc (R7) → ném, không chạy lệnh kiểm; dọn xong mà thư mục còn → ném."""
 import fcntl
 import os
 import secrets
@@ -18,9 +15,12 @@
 from pathlib import Path
 
 from tram.duong_dan import tram_home
-from tram.giao_viec.cay_kiem import cay_goc, loi_cau_hinh_kho, loi_dich_trong_cay, nguon_archive, tar_mot_tep
+from tram.giao_viec.cay_kiem import cay_goc, loi_cau_hinh_kho, loi_dich_trong_cay, tar_mot_tep
+from tram.giao_viec.ong_chep import chay_ong
 from tram.giao_viec.repo_ban_chep import lenh_cay, lenh_repo
+from tram.kiem.chay_gioi_han import chay_gioi_han
 from tram.kiem.moi_truong import LoiMoiTruongKiem, loi_dich
+from tram.kiem.vong_doi import Kill, LoiThuHoi, kill_cuc_bo
 
 TAR_NHAN = ("/usr/bin/tar", "-x", "--no-mac-metadata", "-f", "-", "-C")
 THOI_GIAN = 600
@@ -62,52 +62,52 @@
     return f"{giao_id}-{secrets.token_hex(4)}"
 
 
-def _chay(argv: list[str], **kw) -> subprocess.CompletedProcess:
-    return subprocess.run(argv, capture_output=True, timeout=THOI_GIAN, **kw)
+def _chay(argv: list[str], *, kill: Kill, timeout: float | None = None, **kw) -> subprocess.CompletedProcess:
+    try:
+        return chay_gioi_han(argv, kill=kill, capture_output=True, timeout=timeout or THOI_GIAN, **kw)
+    except LoiThuHoi:                       # tick chỉ bắt OSError: chưa xác nhận thu hồi = bản chép không công nhận
+        raise LoiBanChep("lệnh dưới tram-kiem: không xác nhận thu hồi cây tiến trình — không công nhận") from None
 
 
-def chep_ban(kho: Path, commit: str, wt: Path, *, boc: Boc) -> None:
+def chep_ban(kho: Path, commit: str, wt: Path, *, boc: Boc, kill: Kill = kill_cuc_bo) -> None:
     """`tram-kiem` tạo `wt` MỚI (đã có → lỗi), tự `tar -x` nội dung đúng commit từ stdin, rồi tự dựng repo git một
     commit (D40) — TRƯỚC khi môi trường kiểm vào cây, nên `.env.testing` không bao giờ thành đối tượng git. Cây của
     repo đó phải ĐÚNG cây commit gốc (R7): `git add` chuẩn hoá khác commit thì ném, không sửa cho khớp."""
     goc, loi = cay_goc(kho, commit), loi_cau_hinh_kho(kho)
     if loi is not None:
         raise CayKhacNguon(loi)
-    _chay(boc(["/bin/mkdir", "-p", str(wt.parent)]), check=True)
-    _chay(boc(["/bin/mkdir", str(wt)]), check=True)
-    _chay(boc(["/bin/mkdir", "-m", "700", f"{wt}.nha", f"{wt}.nha/tmp"]), check=True)   # HOME/TMP MỚI của lượt (D45)
-    nguon = nguon_archive(kho, commit)
-    try:
-        nhan = _chay(boc([*TAR_NHAN, str(wt)]), stdin=nguon.stdout)
-    finally:
-        nguon.stdout.close()
-        ma = nguon.wait(timeout=THOI_GIAN)
-    if ma or nhan.returncode:
-        raise LoiBanChep(f"git archive (mã {ma}) | tar dưới tram-kiem (mã {nhan.returncode}) lỗi")
+    _chay(boc(["/bin/mkdir", "-p", str(wt.parent)]), kill=kill, check=True)
+    _chay(boc(["/bin/mkdir", str(wt)]), kill=kill, check=True)
+    _chay(boc(["/bin/mkdir", "-m", "700", f"{wt}.nha", f"{wt}.nha/tmp"]), kill=kill, check=True)   # HOME/TMP lượt
+    ma, tar = chay_ong(kho, commit, boc([*TAR_NHAN, str(wt)]), chay=lambda a, **kw: _chay(a, kill=kill, **kw),
+                       han=THOI_GIAN, loi=LoiBanChep)               # nguồn chưa thu hồi → LoiBanChep, thắng lỗi đích
+    if ma is None or ma or tar:
+        raise LoiBanChep(f"git archive (mã {ma}) | tar (mã {tar}) lỗi")
     for buoc, argv in lenh_repo(wt).items():
-        r = _chay(boc(argv))
+        r = _chay(boc(argv), kill=kill)
         if r.returncode:
             raise LoiBanChep(f"git {buoc} dưới tram-kiem lỗi (mã {r.returncode}) — bản chép không thành repo kiểm")
-    r = _chay(boc(lenh_cay(wt)))
+    r = _chay(boc(lenh_cay(wt)), kill=kill)
     if r.returncode:
         raise LoiBanChep(f"git rev-parse dưới tram-kiem lỗi (mã {r.returncode}) — không đọc được cây bản chép")
     if r.stdout.decode(errors="replace").strip() != goc:
         raise CayKhacNguon(f"cây git của bản chép khác cây commit gốc {goc[:12]} (CRLF/encoding/hoa-thường/submodule)")
 
 
-def nhan_moi_truong(kho: Path, commit: str, wt: Path, nguon: Path, dich: str, *, boc: Boc) -> None:
+def nhan_moi_truong(kho: Path, commit: str, wt: Path, nguon: Path, dich: str, *, boc: Boc,
+                    kill: Kill = kill_cuc_bo) -> None:
     """Môi trường kiểm vào bản chép QUA STDIN (tar một file, mode 0600) — không qua argv, trạm không ghi vào cây."""
     loi = loi_dich(dich) or loi_dich_trong_cay(kho, commit, dich)
     if loi is not None:
         raise LoiMoiTruongKiem(loi)
     if not nguon.is_file():
         raise LoiMoiTruongKiem(f"Không thấy file môi trường kiểm {nguon}")
-    r = _chay(boc([*TAR_NHAN, str(wt)]), input=tar_mot_tep(dich, nguon.read_bytes()))
+    r = _chay(boc([*TAR_NHAN, str(wt)]), kill=kill, input=tar_mot_tep(dich, nguon.read_bytes()))
     if r.returncode:
         raise LoiMoiTruongKiem(f"tram-kiem không ghi được {dich} (tar mã {r.returncode})")
 
 
-def don_ban(wt: Path, *, boc: Boc, don_sach: Callable[[], None] | None = None) -> None:
+def don_ban(wt: Path, *, boc: Boc, don_sach: Callable[[], None] | None = None, kill: Kill = kill_cuc_bo) -> None:
     """Giết mọi tiến trình `tram-kiem` rồi `tram-kiem` tự `rm -rf` bản chép và nhà của lượt. Còn sót → ném."""
     loi = None
     if don_sach is not None:
@@ -115,7 +115,7 @@
             don_sach()
         except (OSError, subprocess.SubprocessError) as e:
             loi = e
-    r = _chay(boc(["/bin/rm", "-rf", str(wt), f"{wt}.nha"]))
+    r = _chay(boc(["/bin/rm", "-rf", str(wt), f"{wt}.nha"]), kill=kill)
     if r.returncode or os.path.lexists(wt) or os.path.lexists(f"{wt}.nha"):
         raise LoiBanChep(f"không dọn được bản chép {wt} — không công nhận kết quả") from loi
     if loi is not None:
```

`tram/giao_viec/kiem_lai.py` (sửa — bản vá):

```diff
--- a/tram/giao_viec/kiem_lai.py
+++ b/tram/giao_viec/kiem_lai.py
@@ -87,11 +87,11 @@
         don_sach()                           # tiến trình tram-kiem của lần trước không được sống sang lần này
     try:
         try:
-            chep_ban(kho_git, commit, wt, boc=boc)
+            chep_ban(kho_git, commit, wt, boc=boc, kill=kill)
         except CayKhacNguon:
             return KetQuaKiemLai(False, loi="cay-khac-nguon")           # R7: tất định — escalation, không thử lại mãi
         try:
-            nhan_moi_truong(kho_git, commit, wt, mt.file, mt.dich, boc=boc)
+            nhan_moi_truong(kho_git, commit, wt, mt.file, mt.dich, boc=boc, kill=kill)
         except LoiMoiTruongKiem:
             return KetQuaKiemLai(False, loi="thieu-moi-truong-kiem")      # không bao giờ chạy với .env có thể thật
         env, ket_qua = moi_truong_kiem(env_goc), []
@@ -102,5 +102,5 @@
                 raise LoiBanChep(f"lệnh kiểm {i}: chưa thu hồi được cây tiến trình — không công nhận kết quả")
             ket_qua.append(kq.sang_lenh_kiem())
     finally:
-        don_ban(wt, boc=boc, don_sach=don_sach)   # lỗi → ném: không công nhận kết quả khi chưa dọn sạch
+        don_ban(wt, boc=boc, don_sach=don_sach, kill=kill)   # lỗi → ném: không công nhận kết quả khi chưa dọn
     return KetQuaKiemLai(bool(ket_qua) and all(k["ket_qua"] == "pass" for k in ket_qua), tuple(ket_qua))
```

- [ ] **Step 4: Chạy, thấy XANH**

```bash
C=<thư mục PATH chặn host>; PATH="$C/bin:$PATH" PYTHONPATH="$C/plugin" UV_OFFLINE=1 uv run pytest -p chan_host -q tests/test_ban_chep_pipeline_han.py tests/test_ong_chep_uu_tien.py tests/test_ban_chep.py tests/test_ban_chep_cay.py tests/test_ban_chep_git.py tests/test_ban_chep_cay_kho.py tests/test_kiem_lai_principal.py tests/test_kiem_lai_cong.py tests/test_kiem_lai_thu_hoi.py tests/test_thu_hoi_uid.py tests/test_nghiem_thu_kiem.py tests/test_chay_gioi_han.py tests/test_kiem_principal_dong.py tests/test_ngat.py
```

Kết quả THẬT (vòng 3, trên `f4fa3a8` + plan A + Task 1–7): hai file của task `15 passed in 10.36s` (thêm `test_ctrl_c_ngay_sau_khi_nguon_spawn_nguon_da_co_chu_va_bi_thu_hoi` — Ctrl-C THẬT ngay sau Popen của `git archive`); cả nhóm bản chép/kiểm lại/harness `109 passed in 42.01s`; nhật ký chặn host không thêm dòng.

- [ ] **Step 5: Commit**

```bash
git add tests/test_ban_chep_pipeline_han.py tests/test_ong_chep_uu_tien.py tram/giao_viec/ong_chep.py tram/giao_viec/cay_kiem.py tram/giao_viec/ban_chep.py tram/giao_viec/kiem_lai.py
git commit -m "fix(v2-6a): ống git archive | tar có chủ hai đầu, một ngân sách hạn, nguồn chưa thu hồi thắng mọi lỗi (bs-863.18, B02)"
```

### Task 8: SIGTERM ở CLI cha phủ MỌI đoạn sở hữu con: preflight, tạo dấu + spawn, chờ, thu hồi, dọn (bs-863.19; B03 vòng 1; R2-02, R2-03 vòng 2)

**Đợt:** 2 · **Phải xong trước:** — (cần Task 6) · **Bead:** bs-863.19. V2-1 (`a06eefb`) dọn khi KeyboardInterrupt/exception nhưng SIGTERM mặc định giết CLI cha ngay — con harness (phiên riêng) chạy tiếp, dấu còn nhưng tác động không dừng. **R2-03 (vòng 2):** bản trước sửa cùng thân `chay_han_tong` với A (bằng `n` thay vì `chu`). Nay `tram/kiem/han_tong.py` có MỘT bản thân hàm cuối do plan A-T4 viết (tạo dấu + spawn trong `try` và `hoan()`, `Nhom` vào `chu` trước mọi lối ra, thu hồi `chu` trong `hoan()` rồi mới ghi kết quả, `don()` luôn chạy, dấu chỉ xoá khi cả hai xác nhận, `khoi` ném lạ → dấu giữ) — **Task này KHÔNG sửa `han_tong.py`**, chỉ:
- `lenh_nghiem_thu` cài `term_thanh_ngat` TỪ ĐẦU lệnh cha (con `--trong` giữ tín hiệu mặc định — cha thu hồi cả cây của nó); preflight (cấu hình + `xac_minh_uid`) bọc `hoan()`: SIGTERM tới giữa chừng chỉ được ghi, tiến trình dò chạy tới hết KỂ CẢ thu hồi của nó (hữu hạn: hạn dò 10 s + cận trên `thu_hoi(1, 1, 2)`; dò danh tính có khối sở hữu riêng từ A-T2), rồi CLI trả 143, không tạo dấu, không spawn harness. `_don` bắt `BaseException` → `cong.dong` cả khi bị ngắt.
- Mã thoát: 143 (SIGTERM) / 130 (Ctrl-C), stderr in trạng thái dấu.
- Test trên đường A+B thật: `tests/test_han_tong_ngat.py` (ngắt lần hai lúc thu hồi/dọn, SIGTERM giữa lúc spawn, `khoi` ném lạ — tín hiệu giao qua handler ĐANG CÀI: trong `hoan()` là bộ ghi của A), `tests/test_lenh_nghiem_thu_ngat.py` (bốn đoạn của CLI cha), `tests/test_ngat_ab.py` (SIGTERM THẬT `raise_signal` qua cả hai lớp: ngay sau Popen harness, lần hai lúc thu hồi, kill bị từ chối + gốc treo → dấu giữ, preflight → 143). Mọi test có handler canh `chan_sigterm_mac_dinh`: mã chưa cài `term_thanh_ngat` thì test ĐỎ (`SigtermLot`) thay vì SIGTERM mặc định giết pytest — lần chạy đỏ đầu tiên (không có canh) đã làm đúng điều đó.

**Files:**
- Create: `tests/test_lenh_nghiem_thu_ngat.py`, `tests/test_ngat_ab.py`
- Modify: `tests/test_han_tong_ngat.py`, `tram/giao_viec/lenh_nghiem_thu.py`

**Interfaces:**
- Consumes: Task 6: `NgatTerm`, `term_thanh_ngat`; plan A: `hoan`, hợp đồng `so_huu`, `chay_han_tong` (A-T4); V2-1: dấu `kiem-lai.dong`.
- Produces: `lenh_nghiem_thu` trả 143 / 130, in trạng thái dấu; `_chay(args, han_tong, xac_minh)`, `_trang_thai(dau)` (nội bộ).

- [ ] **Step 1: Viết test thất bại**

`tests/test_lenh_nghiem_thu_ngat.py` (mới, nguyên văn):

```python
"""bs-863.19 phần còn lại + B03 (vòng 1): SIGTERM ở CLI cha `tram giao nghiem-thu-kiem` đi đường ngắt có kiểm soát ở
MỌI đoạn đã/đang sở hữu tiến trình con — preflight (tiến trình dò UID), tạo dấu + spawn harness, chờ, dọn. Con GIẢ,
không tín hiệu thật (gọi thẳng handler đang cài), không sudo/tiến trình con. `chan_sigterm_mac_dinh`: handler canh của
test — nếu mã chưa cài `term_thanh_ngat` mà tín hiệu (kể cả bản phát lại của `hoan()`) tới, test ĐỎ thay vì SIGTERM
mặc định giết luôn pytest."""
import signal

import pytest

from test_lenh_nghiem_thu import args, cau_hinh  # noqa: F401 — fixture `cau_hinh` dùng chung
from tram.giao_viec import lenh_nghiem_thu as lnt
from tram.giao_viec.cong_luot import CongLuot
from tram.kiem.ngat import NgatTerm


class SigtermLot(Exception):
    """SIGTERM tới mà CLI cha chưa cài handler — mặc định sẽ giết CLI cha, bỏ lại con/tiến trình dò."""


@pytest.fixture(autouse=True)
def chan_sigterm_mac_dinh():
    def canh(so, khung):
        raise SigtermLot()
    cu = signal.signal(signal.SIGTERM, canh)
    yield
    signal.signal(signal.SIGTERM, cu)


def _sigterm():
    h = signal.getsignal(signal.SIGTERM)
    assert callable(h), "SIGTERM chưa có handler ở đoạn này — mặc định giết CLI cha, con/tiến trình dò bị bỏ lại"
    h(signal.SIGTERM, None)                                         # như nhân giao SIGTERM — không gửi tín hiệu thật


class ConGia:
    """Harness con GIẢ dưới `chay_han_tong` thật: SIGTERM tới cha trong lúc chờ."""
    def __init__(self, goi):
        self.goi = goi

    def cho(self, han):
        _sigterm()

    def thu_hoi(self):
        self.goi.append("thu")
        return True


def test_sigterm_o_cha_thu_hoi_con_va_don_xong_moi_tra(cau_hinh, tram_home_tam, monkeypatch, capsys):
    goi, truoc = [], signal.getsignal(signal.SIGTERM)
    monkeypatch.setattr("tram.kiem.vong_doi.khoi_chay", lambda a, **kw: ConGia(goi))
    monkeypatch.setattr(lnt, "_don", lambda pk, goc: goi.append("don") or True)
    assert lnt.lenh_nghiem_thu(args(), xac_minh=lambda *a: 777) == 143
    assert goi == ["thu", "don"] and not (tram_home_tam / "kiem-lai.dong").exists()
    assert signal.getsignal(signal.SIGTERM) is truoc and "SIGTERM" in (e := capsys.readouterr().err) and "đã xoá" in e


def test_sigterm_luc_xac_minh_uid_cho_tien_trinh_do_thu_hoi_xong_roi_moi_dung(cau_hinh, tram_home_tam, capsys):
    """B03: preflight có spawn (tiến trình dò UID dưới principal) — SIGTERM tới giữa chừng: dò chạy tới hết (gồm thu
    hồi của nó), rồi CLI dừng 143, KHÔNG tạo dấu, KHÔNG spawn harness."""
    goi = []

    def xac_minh(*a):
        _sigterm()
        goi.append("do-da-thu-hoi")
        return 777
    assert lnt.lenh_nghiem_thu(args(), xac_minh=xac_minh, han_tong=lambda *a, **kw: goi.append("harness")) == 143
    assert goi == ["do-da-thu-hoi"] and not (tram_home_tam / "kiem-lai.dong").exists()
    assert "SIGTERM" in capsys.readouterr().err


def test_sigterm_giua_luc_spawn_harness_thu_hoi_con_roi_moi_tra(cau_hinh, tram_home_tam, monkeypatch):
    """B03: SIGTERM tới khi `khoi_chay` của harness đang chạy (sau Popen) — con vẫn được nhận chủ, thu hồi, dọn."""
    goi = []

    def khoi(a, **kw):
        _sigterm()
        goi.append("khoi")
        return ConGia(goi)
    monkeypatch.setattr("tram.kiem.vong_doi.khoi_chay", khoi)
    monkeypatch.setattr(lnt, "_don", lambda pk, goc: goi.append("don") or True)
    assert lnt.lenh_nghiem_thu(args(), xac_minh=lambda *a: 777) == 143
    assert goi == ["khoi", "thu", "don"] and not (tram_home_tam / "kiem-lai.dong").exists()


def test_ngat_lan_hai_trong_luc_don_giu_dau_va_dong_cong(cau_hinh, tram_home_tam, monkeypatch, tmp_path, capsys):
    goi = []
    c = CongLuot(tmp_path / "c.json", thu_hoi=lambda: None, quan_sat=[], ngu=lambda s: None)
    c.mo_lai()
    c.quan_sat = [_sigterm]                                          # SIGTERM lần hai tới giữa lúc `_don` quan sát
    monkeypatch.setattr("tram.kiem.vong_doi.khoi_chay", lambda a, **kw: ConGia(goi))
    monkeypatch.setattr("tram.giao_viec.cong_that.dung_cong", lambda pk, goc, cac_du_an: c)
    assert lnt.lenh_nghiem_thu(args(), xac_minh=lambda *a: 777) == 143
    assert goi == ["thu"] and (tram_home_tam / "kiem-lai.dong").exists() and c.trang_thai()["trang_thai"] == "dong"
    assert "CÒN" in capsys.readouterr().err and not isinstance(NgatTerm(), Exception)   # `except Exception` không nuốt
```

`tests/test_ngat_ab.py` (mới, nguyên văn):

```python
"""R2-02/R2-03 (vòng 2): SIGTERM THẬT đi qua CẢ HAI lớp trên đường A+B — `hoan()` + hợp đồng sở hữu của plan A (bộ ghi
trong `khoi_chay`/thu hồi) và `term_thanh_ngat` của plan B (CLI cha). Tín hiệu chỉ phát vào CHÍNH tiến trình test
(`signal.raise_signal`), luôn có handler canh của test bên dưới (`chan_sigterm_mac_dinh`) — không bao giờ để SIGTERM
mặc định giết pytest. Tiến trình thật chỉ là `python -c` của user test; backend kill/Popen giả cho ca
kill bị từ chối, gốc treo."""
import signal
import subprocess
import sys

import pytest

from test_lenh_nghiem_thu import args, cau_hinh  # noqa: F401 — fixture `cau_hinh` dùng chung
from test_lenh_nghiem_thu_ngat import chan_sigterm_mac_dinh  # noqa: F401 — handler canh tự dùng
from test_vong_doi import PopenGia, _song
from tram.giao_viec import lenh_nghiem_thu as lnt
from tram.kiem.han_tong import chay_han_tong
from tram.kiem.ngat import NgatTerm, term_thanh_ngat
from tram.kiem.vong_doi import khoi_chay, kill_cuc_bo

NGU = [sys.executable, "-c", "import time; time.sleep(60)"]


def sigterm_that():
    assert callable(signal.getsignal(signal.SIGTERM)), "SIGTERM mặc định ở đoạn này sẽ giết CLI cha"
    signal.raise_signal(signal.SIGTERM)


def don_con(goi):
    for p in goi:
        if p.poll() is None:
            p.kill()
            p.wait(5)


def test_sigterm_that_ngay_sau_popen_harness_con_co_chu_thu_hoi_don_roi_moi_ngat(tmp_path):
    goi, don = [], []

    def popen(a, **kw):
        goi.append(subprocess.Popen(a, **kw))
        sigterm_that()                                              # bộ ghi của `hoan()` trong `chay_han_tong`
        return goi[-1]
    try:
        with term_thanh_ngat(), pytest.raises(NgatTerm):
            chay_han_tong(NGU, han=30, kill=kill_cuc_bo, dau=tmp_path / "dau", don=lambda: don.append(1) or True,
                          khoi=lambda a, **kw: khoi_chay(a, popen=popen, **kw))
        assert not _song(goi[0].pid) and don == [1] and not (tmp_path / "dau").exists()
    finally:
        don_con(goi)


def test_sigterm_that_lan_hai_luc_thu_hoi_khong_cat_ngang_roi_thay_het_han(tmp_path):
    goi, gui = [], []

    def kill(g, s):
        if not gui:
            sigterm_that()                                          # tới giữa lúc thu hồi: bộ ghi của `hoan()`
        gui.append(s)
        kill_cuc_bo(g, s)
    try:
        with term_thanh_ngat(), pytest.raises(NgatTerm):
            chay_han_tong(NGU, han=0.3, kill=kill, dau=tmp_path / "dau", don=lambda: True,
                          khoi=lambda a, **kw: goi.append(khoi_chay(a, **kw)) or goi[-1])
        assert gui and not _song(goi[0].p.pid) and not (tmp_path / "dau").exists()
    finally:
        don_con([n.p for n in goi])


def test_sigterm_that_kill_bi_tu_choi_goc_treo_dau_giu_nhom_con_trong_chu(tmp_path):
    chu = []

    def tu_choi(g, s):
        if g == 4242 and s == signal.SIGTERM:
            sigterm_that()
        raise PermissionError

    def khoi(a, **kw):
        chu.append(kw["chu"])
        return khoi_chay(a, popen=lambda *x, **k: PopenGia(), chup=lambda: [], **kw)
    with term_thanh_ngat(), pytest.raises(NgatTerm):
        chay_han_tong(["gia"], han=0.2, kill=tu_choi, dau=tmp_path / "dau", don=lambda: True, khoi=khoi)
    assert (tmp_path / "dau").exists() and chu[0][0].ket_thu_hoi is False             # không xác nhận: cổng đóng


def test_sigterm_that_luc_preflight_cli_cha_tra_143_khong_dau_khong_harness(cau_hinh, tram_home_tam, capsys):
    goi, truoc = [], signal.getsignal(signal.SIGTERM)

    def xac_minh(*a):
        sigterm_that()                                              # bộ ghi của `hoan()` quanh preflight
        goi.append("do-xong")
        return 777
    assert lnt.lenh_nghiem_thu(args(), xac_minh=xac_minh, han_tong=lambda *a, **kw: goi.append("harness")) == 143
    assert goi == ["do-xong"] and not (tram_home_tam / "kiem-lai.dong").exists()
    assert "SIGTERM" in capsys.readouterr().err and signal.getsignal(signal.SIGTERM) is truoc
```

`tests/test_han_tong_ngat.py` (sửa — bản vá):

```diff
--- a/tests/test_han_tong_ngat.py
+++ b/tests/test_han_tong_ngat.py
@@ -1,7 +1,14 @@
+import signal
+
 import pytest
 from tram.kiem.han_tong import chay_han_tong
+from tram.kiem.ngat import NgatTerm, term_thanh_ngat
 
 
+def giao(so):
+    signal.getsignal(so)(so, None)                                  # như nhân giao tín hiệu: chạy handler ĐANG CÀI
+
+
 @pytest.mark.parametrize("sach", [True, False])
 @pytest.mark.parametrize("loi", [KeyboardInterrupt, RuntimeError])
 def test_ngat_van_thu_hoi_roi_don(tmp_path, sach, loi):
@@ -35,3 +42,80 @@
                       dau=tmp_path / "dau", don=lambda: goi.append(1) or True,
                       khoi=lambda *a, **kw: N())
     assert goi == [1] and (tmp_path / "dau").exists()
+
+
+@pytest.mark.parametrize("o", ["thu_hoi", "don"])
+def test_ngat_lan_hai_trong_luc_don_van_giu_dau(tmp_path, o):
+    """bs-863.19: Ctrl-C/SIGTERM lần hai giữa lúc thu hồi hoặc dọn — `don` vẫn được gọi sau thu hồi, dấu GIỮ."""
+    goi, dau = [], tmp_path / "dau"
+
+    class N:
+        def cho(self, han):
+            raise KeyboardInterrupt
+
+        def thu_hoi(self):
+            goi.append("thu")
+            if o == "thu_hoi":
+                raise KeyboardInterrupt
+            return True
+
+    def don():
+        goi.append("don")
+        if o == "don":
+            raise KeyboardInterrupt
+        return True
+    with pytest.raises(KeyboardInterrupt):
+        chay_han_tong(["gia"], han=1, kill=lambda *a: None, dau=dau, don=don, khoi=lambda *a, **kw: N())
+    assert goi == ["thu", "don"] and dau.exists()
+
+
+def test_ngat_toi_giua_luc_spawn_chi_nem_khi_con_da_co_chu(tmp_path):
+    """B03: SIGTERM tới khi `khoi` đã Popen, chưa trả Nhom — hoãn; ném khi `n` đã có chủ: thu hồi, dọn, xoá dấu."""
+    goi, dau = [], tmp_path / "dau"
+
+    class N:
+        def cho(self, han):
+            goi.append("cho")
+
+        def thu_hoi(self):
+            goi.append("thu")
+            return True
+    with term_thanh_ngat():
+        def khoi(*a, **kw):
+            giao(signal.SIGTERM)
+            goi.append("khoi-xong")
+            return N()
+        with pytest.raises(NgatTerm):
+            chay_han_tong(["gia"], han=1, kill=lambda *a: None, dau=dau, don=lambda: goi.append("don") or True,
+                          khoi=khoi)
+    assert goi == ["khoi-xong", "thu", "don"] and not dau.exists()
+
+
+def test_khoi_nem_loi_khac_oserror_thi_van_don_nhung_giu_dau(tmp_path):
+    """Hợp đồng `khoi_chay` (V2-0/A03) bị vi phạm — vd. dựng theo dõi hỏng SAU Popen, ném RuntimeError: không biết con
+    còn hay không → `don` vẫn chạy, dấu GIỮ (cổng đóng), lỗi nổi lên."""
+    goi, dau = [], tmp_path / "dau"
+
+    def khoi(*a, **kw):
+        raise RuntimeError("theo dõi hỏng sau Popen")
+    with pytest.raises(RuntimeError):
+        chay_han_tong(["gia"], han=1, kill=lambda *a: None, dau=dau, don=lambda: goi.append("don") or True, khoi=khoi)
+    assert goi == ["don"] and dau.exists()
+
+
+def test_ngat_lan_hai_trong_luc_thu_hoi_khong_cat_ngang(tmp_path):
+    """B03: SIGTERM lần hai tới giữa lúc thu hồi — thu hồi chạy hết (hữu hạn), dọn, rồi mới ném một lần."""
+    goi, dau = [], tmp_path / "dau"
+    with term_thanh_ngat():
+        class N:
+            def cho(self, han):
+                giao(signal.SIGTERM)                     # lần một: ngoài ranh giới hoãn → ném ngay
+
+            def thu_hoi(self):
+                giao(signal.SIGTERM)                     # lần hai: hoãn
+                goi.append("thu-xong")
+                return True
+        with pytest.raises(NgatTerm):
+            chay_han_tong(["gia"], han=1, kill=lambda *a: None, dau=dau, don=lambda: goi.append("don") or True,
+                          khoi=lambda *a, **kw: N())
+    assert goi == ["thu-xong", "don"] and not dau.exists()
```

- [ ] **Step 2: Chạy, thấy ĐỎ**

```bash
C=<thư mục PATH chặn host>; PATH="$C/bin:$PATH" PYTHONPATH="$C/plugin" UV_OFFLINE=1 uv run pytest -p chan_host -q tests/test_han_tong_ngat.py tests/test_lenh_nghiem_thu_ngat.py tests/test_ngat_ab.py
```

Kết quả THẬT trên `f4fa3a8` + plan A T1–T8 + Task 1–7 (18/10):

```
E       test_lenh_nghiem_thu_ngat.SigtermLot          ← ×5: SIGTERM tới CLI cha chưa có handler (preflight, spawn harness,
                                                         chờ, dọn) — mặc định sẽ giết cha, bỏ lại con/tiến trình dò
FAILED tests/test_lenh_nghiem_thu_ngat.py::test_sigterm_o_cha_thu_hoi_con_va_don_xong_moi_tra
FAILED tests/test_lenh_nghiem_thu_ngat.py::test_sigterm_luc_xac_minh_uid_cho_tien_trinh_do_thu_hoi_xong_roi_moi_dung
FAILED tests/test_lenh_nghiem_thu_ngat.py::test_sigterm_giua_luc_spawn_harness_thu_hoi_con_roi_moi_tra
FAILED tests/test_lenh_nghiem_thu_ngat.py::test_ngat_lan_hai_trong_luc_don_giu_dau_va_dong_cong
FAILED tests/test_ngat_ab.py::test_sigterm_that_luc_preflight_cli_cha_tra_143_khong_dau_khong_harness
5 failed, 13 passed in 4.76s
```

Mười ba ca xanh ngay là hợp đồng của A-T4 + Task 6 nhìn từ B (ngắt lần hai lúc thu hồi/dọn, SIGTERM giữa lúc spawn, `khoi` ném lạ, ba ca SIGTERM thật của `chay_han_tong`) — đúng chủ đích "một bản thân hàm": B không còn bản `han_tong` riêng. Lần chạy đỏ ĐẦU TIÊN (chưa có handler canh) dừng giữa chừng sau `..........FF`: bản phát lại của `hoan()` gặp SIGTERM mặc định và giết chính pytest — đúng lỗi bs-863.19 mà task này sửa; vì vậy test mới có `chan_sigterm_mac_dinh`.

- [ ] **Step 3: Viết mã**

`tram/giao_viec/lenh_nghiem_thu.py` (sửa — bản vá):

```diff
--- a/tram/giao_viec/lenh_nghiem_thu.py
+++ b/tram/giao_viec/lenh_nghiem_thu.py
@@ -5,9 +5,12 @@
 900`, quá hạn thu hồi cả cây (kill gộp principal + cục bộ). Con chỉ chạy khi cha của nó đúng là pid đó VÀ dấu
 `~/.tram/kiem-lai.dong` còn, đúng inode cha vừa tạo (gọi `--trong` tay, dấu cũ → mã 2). Cổng và quan sát của harness
 là cổng THẬT với mọi dự án thật (`env_kin` đủ). Sau đó `_don` dưới khoá kiểm lại: thu hồi theo UID + HAI lượt mọi quan
-sát cách `cho` của cổng (kể cả launchd — chưa đo ở G3 thì ném); lỗi → `cong.dong` rồi ném. Chỉ khi xác nhận mới xoá
-dấu; còn dấu thì kiểm lại, `tram giao kiem`, `mo-cong-kiem` từ chối. Đánh đổi: Ctrl-C ở cha để lại con (phiên riêng)
-chạy tiếp — kịch bản G3/G4 dặn dừng con bằng đúng PID. Mã: 0 không đỏ, 1 đỏ/quá hạn/chưa dọn, 2 không chạy."""
+sát cách `cho` của cổng (kể cả launchd — chưa đo ở G3 thì ném); lỗi hay ngắt → `cong.dong` rồi ném. Chỉ khi xác nhận
+mới xoá dấu; còn dấu thì kiểm lại, `tram giao kiem`, `mo-cong-kiem` từ chối. Ctrl-C/SIGTERM ở cha (bs-863.19, B03):
+`term_thanh_ngat` cài TỪ ĐẦU lệnh cha — phủ preflight (tiến trình dò UID, bọc `hoan()`: ngắt chờ nó thu hồi xong) lẫn
+tạo dấu + spawn harness (`chay_han_tong` tự hoãn tới khi con có chủ) — rồi thu hồi + dọn trong `finally` mới trả. Con
+`--trong` giữ tín hiệu mặc định (cha thu hồi cả cây). Mã: 0 không đỏ, 1 đỏ/quá hạn/chưa dọn, 2 không chạy, 130
+Ctrl-C, 143 SIGTERM (dấu còn hay đã xoá in ra stderr)."""
 import argparse
 import math
 import os
@@ -40,7 +43,7 @@
                     c.ngu(c.cho)                     # tái sinh trễ phải lộ ra giữa hai lượt quan sát
                 for q in c.quan_sat:
                     q()
-        except Exception as e:                       # noqa: BLE001 — dọn không xác nhận: cổng đóng, dấu giữ
+        except BaseException as e:                   # noqa: BLE001 — dọn không xác nhận (kể cả ngắt): cổng đóng
             c.dong(f"nghiệm thu S6: dọn không xác nhận ({type(e).__name__})")
             raise
     return True
@@ -62,16 +65,36 @@
     return ma
 
 
+def _trang_thai(dau) -> str:
+    return ("dấu kiem-lai.dong CÒN — xem ~/.tram/log/nghiem-thu, `tram giao mo-cong-kiem` hiện trạng thái"
+            if dau.exists() else "đã thu hồi + dọn (hoặc chưa chạy harness), dấu đã xoá")
+
+
 def lenh_nghiem_thu(args, *, han_tong=None, xac_minh=None) -> int:
+    from tram.kiem.ngat import NgatTerm, term_thanh_ngat
+    if args.trong:                          # con: tín hiệu mặc định — cha thu hồi cả cây của nó
+        return _chay(args, han_tong, xac_minh)
+    try:
+        with term_thanh_ngat():             # B03: phủ preflight có spawn lẫn tạo dấu + spawn harness
+            return _chay(args, han_tong, xac_minh)
+    except KeyboardInterrupt as e:          # NgatTerm là KeyboardInterrupt
+        ngat, ma = ("SIGTERM", 143) if isinstance(e, NgatTerm) else ("Ctrl-C", 130)
+        print(f"[ĐỎ] bị ngắt ({ngat}) — {_trang_thai(tram_home() / 'kiem-lai.dong')}", file=sys.stderr)
+        return ma
+
+
+def _chay(args, han_tong, xac_minh) -> int:
     from tram.kiem.danh_tinh import LoiDanhTinh, xac_minh_uid
     from tram.kiem.han_tong import chay_han_tong, gop_kill
+    from tram.kiem.ngat import hoan
     from tram.kiem.vong_doi import LoiThuHoi, khoi_chay, kill_cuc_bo
     dau = tram_home() / "kiem-lai.dong"
     try:
-        pk, goc = _pk_goc()
-        if not (math.isfinite(args.cho) and args.cho > 0) or (args.tai_sinh and args.cho < 240):
-            raise ValueError("--cho phải hữu hạn, > 0, và ≥ 240 giây với --tai-sinh (lịch hẹn 121–180 s)")
-        (xac_minh or xac_minh_uid)(pk.ten, pk.boc_lenh, pk.kill_nhom)
+        with hoan():                        # tiến trình dò UID (hữu hạn): ngắt tới lúc này chờ nó thu hồi xong
+            pk, goc = _pk_goc()
+            if not (math.isfinite(args.cho) and args.cho > 0) or (args.tai_sinh and args.cho < 240):
+                raise ValueError("--cho phải hữu hạn, > 0, và ≥ 240 giây với --tai-sinh (lịch hẹn 121–180 s)")
+            (xac_minh or xac_minh_uid)(pk.ten, pk.boc_lenh, pk.kill_nhom)
     except (ValueError, LoiDanhTinh, LoiThuHoi) as e:
         print(f"Không chạy nghiệm thu: {type(e).__name__}: {e}", file=sys.stderr)
         return 2
@@ -84,10 +107,8 @@
                                            don=partial(_don, pk, goc), khoi=lambda a, **kw: khoi_chay(
                                                [*a, "--dau-ino", str(dau.stat().st_ino), "--cha", str(os.getpid())],
                                                **kw))
-    except LoiThuHoi as e:                                  # HetHanTong là LoiThuHoi
-        con = "dấu kiem-lai.dong CÒN — xem ~/.tram/log/nghiem-thu, `tram giao mo-cong-kiem` hiện trạng thái" \
-            if dau.exists() else "đã thu hồi + dọn, dấu đã xoá"
-        print(f"[ĐỎ] {e} — {con}", file=sys.stderr)
+    except LoiThuHoi as e:                  # HetHanTong là LoiThuHoi
+        print(f"[ĐỎ] {e} — {_trang_thai(dau)}", file=sys.stderr)
         return 1
 
 
```

- [ ] **Step 4: Chạy, thấy XANH**

```bash
C=<thư mục PATH chặn host>; PATH="$C/bin:$PATH" PYTHONPATH="$C/plugin" UV_OFFLINE=1 uv run pytest -p chan_host -q tests/test_ngat.py tests/test_lenh_nghiem_thu_ngat.py tests/test_ngat_ab.py tests/test_han_tong_ngat.py tests/test_han_tong.py tests/test_lenh_nghiem_thu.py tests/test_so_huu_han_tong.py
```

Kết quả THẬT: `49 passed in 18.74s`; nhật ký chặn không thêm dòng; `ps` sau chạy không còn `time.sleep(60)` của test.

- [ ] **Step 5: Commit**

```bash
git add tests/test_lenh_nghiem_thu_ngat.py tests/test_ngat_ab.py tests/test_han_tong_ngat.py tram/giao_viec/lenh_nghiem_thu.py
git commit -m "fix(v2-1): SIGTERM ở CLI cha phủ preflight, spawn, thu hồi; ngắt lần hai giữ dấu (bs-863.19, B03, R2-03)"
```

### Task 9: Ghi bước cổng G3.0/G4 vào phụ lục cổng (docs)

**Đợt:** 3 · **Phải xong trước:** — (cần T1–T8 đã ghép) · **Bead:** bs-2bd.1.14, bs-2bd.1.15. Docs-only, không test.

**Files:**
- Modify: `docs/handovers/2026-10-17-cong-sau-review-dot7.md`

- [ ] **Step 1:** Thêm cuối file một mục `## V2c — G3.0 hồ sơ có manifest, G4 ma trận probe` gồm NGUYÊN VĂN hai tiểu mục "G3.0 — sau khi cài lại…" và "G4 — ma trận chứng cứ OS…" của mục "Bước cổng cho sổ tay" dưới đây (đổi cấp tiêu đề `###` → `####`). Không sửa các dòng lịch sử phía trên.
- [ ] **Step 2:** Kiểm docs (`AGENT_RULES.md` §13): mọi đường dẫn code được nhắc tồn tại (`ls tram/giao_viec/chung_cu_probe.py tram/tho/quyen_kiem.py tram/giao_viec/cong_that.py`).
- [ ] **Step 3: Commit** — `git add docs/handovers/2026-10-17-cong-sau-review-dot7.md && git commit -m "docs(v2c): bước cổng G3.0 manifest hồ sơ và ma trận probe G4"`.

## Bước cổng cho sổ tay (KHÔNG chạy trong plan; trình Đại ca từng kịch bản khi tới cổng)

Đây là nội dung Task 9 (docs) thêm vào phụ lục `docs/handovers/2026-10-17-cong-sau-review-dot7.md` sau khi T1–T8 ghép. Không lệnh nào dưới đây được chạy khi viết plan.

### G3.0 — sau khi cài lại bằng `tram chu cai-dat-tho` (Đại ca gõ `dong-y`, Terminal.app)

1. Đại ca ghi (chỉ đọc, không sudo): `ls -ld / /usr /usr/local /usr/local/tram`, `stat -f '%Su:%Sg %Lp %HT' /usr/local/tram/tram-kiem.sb /usr/local/tram/tram-kiem.sb.json`, `shasum -a 256 /usr/local/tram/tram-kiem.sb /usr/local/tram/tram-kiem.sb.json`. Đạt: mọi dòng `root:wheel`, thư mục 755, file 644 `Regular File`. Máy viết plan (macOS 15.6.1, 24G90) đo 17/10: `/`, `/usr`, `/usr/local` đều `root wheel drwxr-xr-x`; **máy B chưa đo** — nếu `/usr/local` không phải root (ví dụ Homebrew cũ trên Intel đổi chủ) thì `doc_tep_root` đóng cổng: dừng, hỏi Đại ca (xem Câu hỏi 2), không tự nới.
2. Ghi vào biên bản: `phien_ban` trong manifest (= `PHIEN_BAN_HO_SO` của mã đã ghép), hai digest, commit của mã. Không ghi nội dung hồ sơ hay đường dẫn có tên người ngoài phạm vi.
3. `tram giao kiem` (Đại ca chạy): mục cổng không báo `LoiBanChep` về hồ sơ/manifest. Đổi `TRAM_HOME`/`giao_viec.thu_muc_kiem` sau đó → phải đỏ cho tới khi cài lại (kiểm một lần, ghi kết quả).

### G4 — ma trận chứng cứ OS (V2-4 phần OS; phụ lục đợt 7 mục "Matrix bắt buộc")

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

## Câu hỏi cho Đại ca

1. **Harness `--tai-sinh` sẽ luôn báo ĐỎ ở mục "đủ bằng chứng S6"** (mã thoát 1) cho tới khi có biên bản OS G4, kể cả khi mọi nguồn đều thất bại đúng như mong muốn. Nghĩa thực tế: máy không tự tuyên bố "cách ly đạt" chỉ vì lệnh cài lịch bị lỗi; Đại ca đọc biên bản G4 mới kết luận. *Đề xuất: chấp nhận.* Nếu chọn "cho mục tổng vàng khi mọi nguồn thất bại" thì harness có thể thoát mã 0 mà chưa có bằng chứng OS — Codex đã chỉ ra đúng lỗi này (dot7-Q03).
2. **Thư mục chứa hồ sơ phải do root giữ từ gốc ổ đĩa xuống** (`/`, `/usr`, `/usr/local`, `/usr/local/tram`). Nếu máy B có `/usr/local` thuộc tài khoản khác (thường do Homebrew trên máy Intel cũ), cổng kiểm lại sẽ đóng. *Đề xuất: giữ chặt, đo ở G3.0; nếu máy B lệch thì Em trình phương án chuyển nơi cài (ví dụ `/Library/Application Support/tram`) thay vì nới kiểm tra.*
3. **Đổi `TRAM_HOME` hoặc thư mục bản chép kiểm sau khi cài = phải cài lại hồ sơ** (gõ `dong-y` ở `tram chu cai-dat-tho`) thì kiểm lại mới chạy. *Đề xuất: chấp nhận* — đây là cách duy nhất để hồ sơ đang chặn đúng thư mục hiện dùng.
4. **Thử "mạng ra ngoài máy" ở G4 tới đâu?** Để chứng minh agent không gọi được ra ngoài, cần một máy đích để thử kết nối (lúc không có hồ sơ thì phải kết nối được — đó là đối chứng). Em không dùng địa chỉ Internet bất kỳ. *Đề xuất: Đại ca chỉ định một máy của mình trong Tailscale (ví dụ máy A) mở tạm một cổng nghe trong lúc kiểm, tắt ngay sau.* Nếu Đại ca không muốn, hàng này ghi "chưa đo" và G4 chưa được tính là đạt phần mạng ngoài — không lấy phép thử nội máy thay vào.
5. **Bấm Ctrl-C/gửi SIGTERM cho lệnh nghiệm thu lúc nó đang dò danh tính hoặc đang dọn tiến trình con thì lệnh không dừng ngay** — nó chạy nốt bước đó (dò ≤ khoảng 25 s; thu hồi ≤ khoảng 40 s, đúng cận trên đã ghi trong mã) rồi mới dừng với mã 143/130, để không bỏ lại tiến trình chạy dưới tài khoản kiểm. Muốn dừng tức thì vẫn có SIGKILL, nhưng khi đó máy không hứa dọn gì và dấu khoá cổng sẽ còn — Đại ca phải kiểm tay. *Đề xuất: chấp nhận* (đây là cái giá của "không để sót tiến trình").

## Kết quả chạy thử (worktree `plan/ab-tich-hop`, 18/10/2026, sau Codex review vòng 2)

- Mốc: `main` `f4fa3a8` (đã ghép V2-1/2/3/7, V3-1/5/8/9/10/16/17) → **N₀ = 2809** (PATH chặn host). Thứ tự ghép cuối: plan A T1→T8 (`2947 passed`), rồi plan B T1→T8 (T9 là docs).
- Mỗi task chạy lại RED → GREEN thật trên cây đó (RED: test của task + mã của task trước). B-T1…T5 không đổi so với vòng 1, chạy lại trên cây A: đỏ `1 error` / `6 failed, 3 passed` / `1 error` / `4 failed, 16 passed` / `20 failed` (cùng các ca như bản trước), xanh `100 passed` cả năm task. B-T6/T7/T8 viết lại trên thân hàm của A — số đỏ/xanh ở Step 2/Step 4 từng task.
- Áp đủ A-T1…T8 + B-T1…T8 trên cây đang làm: `3062 passed in 272.54s`. **Áp lại toàn bộ khối mã hai plan lên bản SẠCH** (`git archive f4fa3a8`, trích từng khối theo tiêu đề rồi tạo file/áp bản vá theo thứ tự task): `diff -r` của `tram/` và `tests/` với cây đã chạy — **không khác byte nào**; cả bộ trên bản sạch: **`3062 passed in 266.06s`**. Nhật ký chặn `nhat-ky.log`: 32 dòng trước, 32 dòng sau mọi lần chạy (0 dòng mới).
- Test chạm tiến trình thật chỉ dùng `git archive`, `/bin/sh` (`echo`/`exit`/`grep`/`rm` trong `tmp_path`), `python -c` của user test; tín hiệu thật chỉ là `raise_signal` vào chính tiến trình test khi handler đang cài là của `hoan`/`term_thanh_ngat`/handler canh; test để sót con khi đỏ tự thu hồi trong `finally` (`ps` sau mọi lần chạy: không còn `time.sleep(60)` của test).
- Kiểm độ dài: mọi file sửa/mới ≤ 120 ký tự Unicode/dòng (`ruff --select F,E,W --line-length 120` sạch trên các file của hai plan); số dòng ghi ở Global Constraints.
- Lệnh OS đã chạy đều CHỈ ĐỌC (từ bản trước): `ls -ld / /usr /usr/local`, `sw_vers`, đọc header SDK; vòng này chỉ thêm `ps` để xác nhận không còn tiến trình test. Không chạy `sandbox-exec`, sudo, cron/at/launchctl, kịch bản lịch hay installer. Sau chạy thử đã hoàn nguyên mọi thay đổi ngoài file plan.

## Ghi chú triển khai

- Không có subagent code nào được giao từ plan này trước khi Đại ca duyệt + Codex review (kill list).
- **Thứ tự ghép (review §4):** plan A T1 → T8 trước (MỘT subagent cho A-T1…T4); rồi B-T1 → T2; T3 → T4 → T5; **T6 trên A đã ghép → T7 → T8 → T9**. Các bản vá B-T6/T7/T8 là hunk viết trên cây đã có A (đã kiểm: áp nguyên văn lên bản sạch khớp từng byte). Chạy lại `tests/test_han_tong*.py`, `tests/test_lenh_nghiem_thu*.py`, `tests/test_ban_chep*.py`, `tests/test_ong_chep_uu_tien.py`, `tests/test_ngat*.py`, `tests/test_so_huu*.py` sau mỗi lần ghép.
- Áp theo nội dung (`git apply --3way` từng bản vá), không mù số dòng; bản vá T8 tạo trên mã có V2-3 — giữ import/callback `cac_du_an_quan_sat` lẫn `except BaseException` của `_don`.
- `hoan()` (của A) hoãn SIGINT/SIGTERM ở LUỒNG CHÍNH với mọi người gọi, rồi phát lại qua handler đang có trước khối: CLI cha có `term_thanh_ngat` → `NgatTerm`/`KeyboardInterrupt` đi đường dọn; worker/tick giữ handler của chúng; tiến trình mà SIGTERM còn MẶC ĐỊNH thì bản phát lại vẫn giết tiến trình như khi không hoãn (chỉ trễ tới khi `Nhom` đã có chủ). Tiến trình con `--trong` không cài `term_thanh_ngat`.
- `cong` (danh sách cổng cấm) vẫn ghi trong manifest dù bộ sinh hiện không dùng nó (mọi mạng đã cấm — D48); runtime KHÔNG so `cong` với `cach_ly.db_nghiep_vu` để tránh buộc cài lại khi đổi DB mà byte hồ sơ không đổi. Bộ sinh dùng `cong` lần sau thì phải tăng `PHIEN_BAN_HO_SO` và thêm phép so — Codex xem lại điểm này.
- Bead: T1–T2 + bước cổng G4 → `bs-2bd.1.14`; T3–T5 + G3.0 → `bs-2bd.1.15`; T6–T7 → `bs-863.18` (T6 cũng phục vụ `bs-863.19`); T8 → `bs-863.19`. Không đóng bead từ plan; đóng sau QC + bằng chứng.

## Phản hồi review vòng 1

Báo cáo: `.handover/review-codex-plan/REVIEW-CODEX-dot8-vong1.md` mục 2 (B01–B04), mục 4 (thứ tự ghép, phụ thuộc A03). Mọi bằng chứng là lần chạy THẬT trong worktree `plan/v2-cach-ly` trên `main` `7921f26`, PATH chặn host, 0 dòng nhật ký chặn mới.

| Mã | Mức | Đã sửa ở đâu | Bằng chứng (đỏ → xanh thật) |
|---|---|---|---|
| B01 | Quan trọng | Task 1 (`chung_cu_probe.py`: bộ phân loại trong khối shell, `LY_DO` hữu hạn, xoá tệp đầu ra; `ly_do` chỉ trả khoá của `LY_DO`), Task 2 (test khoá ở mức harness), mục G4 "Biên bản sạch" | Mã bản trước: `12 failed, 15 passed` — log chứa `ly-do:cron:BIMAT_OUT BIMAT_ERR …`, dòng lạ được chép nguyên. Mã mới: `27 passed` (T1), `36 passed` (T1 + T2, gồm `test_dong_ly_do_mang_byte_la_khong_vao_ket_qua_harness`; đỏ trên `main`: `6 failed, 3 passed`). Sentinel ở cả stdout lẫn stderr. |
| B02 | Quan trọng | Task 7 (`ong_chep.chay_ong`: nguồn chưa thu hồi → `loi` thay mọi lỗi khác, `from None`; MỘT hạn tính trước khi chuẩn bị nguồn, đích nhận `timeout` phần còn lại, hết hạn thì không chạy đích; `ban_chep` truyền `loi=LoiBanChep`, `_chay(timeout=)`), test mức `kiem_lai` khoá cổng đóng vì bản chép | Mã bản trước: `7 failed, 7 passed` — `OSError: tar: BI_MAT_ENV` che nguồn chưa thu hồi (đích lỗi / không khởi chạy / đóng ống lỗi), cổng đóng với lý do `OSError`, đích nhận cả hạn `1.0` thay vì phần còn lại. Mã mới: `14 passed`; nhóm bản chép/kiểm lại/harness `113 passed`. |
| B03 | Chặn | Task 6 (`ngat.py`: `term_thanh_ngat` SIGTERM + SIGINT, `hoan()`; `chay_gioi_han`: spawn và thu hồi trong `hoan()`, mọi lối ra sau khi có `Nhom` đóng ống + thu hồi), Task 8 (`han_tong.chay_han_tong`: tạo dấu + spawn trong `try`/`hoan()`, thu hồi trong `hoan()`, `khoi` ném lạ → dấu giữ; `lenh_nghiem_thu`: handler TỪ ĐẦU, preflight `xac_minh_uid` trong `hoan()`). Không sửa `vong_doi.py`/`danh_tinh.py` (plan A) — phụ thuộc ghi là hợp đồng H-A03, phần không khép được thay A thì chọn phía an toàn (dấu/cổng giữ đóng) | Mã bản trước: bộ chạy `5 failed, 15 passed` (con THẬT còn sống sau SIGTERM ngay sau Popen; `communicate` ném KeyboardInterrupt/OSError không thu hồi); CLI/hạn tổng `5 failed, 9 passed` ("SIGTERM chưa có handler" ở preflight, spawn harness thoát trước khi con có chủ, `khoi` ném RuntimeError không dọn, ngắt lần hai cắt ngang thu hồi). Mã mới: T6 `20 passed` (+ `test_vong_doi`, `test_danh_tinh`: `40 passed`), T8 `40 passed`. Ngắt/lỗi được tiêm ở từng ranh giới: preflight, tạo dấu/spawn, sau Popen trước khi trả `Nhom`, lúc đọc, lúc thu hồi, lúc dọn — không tín hiệu thật. |
| B04 | Nhỏ | Mục G4: tách ba loại tiêu chí A (phải bị chặn) / B (được phép, phải thu hồi — setsid, Unix socket trong `LUOT`; `ket` ≠ 0 là CHƯA ĐO) / C (mạng ra ngoài máy chỉ tới endpoint Đại ca duyệt, không Internet tuỳ ý); bảng có cột "Loại", hàng mạng loopback và mạng ngoài tách riêng; Câu hỏi 4 | Docs — không có test; kiểm tay đối chiếu phụ lục cổng mục "Matrix bắt buộc" (IPC/mạng: không traffic ra Internet). |

**Giới hạn còn lại, ghi rõ — không tuyên bố đã đạt:**
- `LoiThuHoi` nghĩa là KHÔNG xác nhận, không phải "không còn con" (hợp đồng `so_huu` của A): kill bị từ chối, gốc treo sau SIGKILL, hậu duệ tách phiên dưới tài khoản quản lý → dấu/cổng giữ đóng, `Nhom` còn trong `chu`; dưới `tram-kiem` lưới `cong_that.thu_hoi_theo_uid` dọn ở lượt sau; tiến trình của trạm (nguồn `git archive`) không có lưới UID — chỉ cổng đóng + Đại ca kiểm tay.
- `subprocess.Popen` hỏng NỘI BỘ sau fork mà không phải lỗi exec (plan A Rủi ro 1): Popen không trả đối tượng nào, con có thể sống không chủ trong phiên — ngắt không gây được ca này (đã hoãn).
- SIGKILL vào CLI cha: không handler nào chạy; dấu còn (cổng đóng), con có thể còn — Đại ca kiểm tay theo phụ lục. Không hứa gì.
- Tín hiệu tới đúng lúc giữa `hoan()` của preflight và lúc tạo dấu: không có con nào thuộc CLI cha ở khoảng đó, nên ném ngay là an toàn; dấu chưa tạo.
- Mã `ly-do` chỉ là gợi ý; "Seatbelt chặn" chỉ kết luận được bằng biên bản G4 (mục tổng S6 vẫn luôn đỏ).

## Phản hồi review vòng 2

Báo cáo: `.handover/review-codex-plan/REVIEW-CODEX-dot8-vong2.md` mục 1 (B01–B04), mục 2 (R2-02, R2-03 phần B), mục 3 (mặt ghép), mục 4.1 (thống nhất A-T1…T4 với B-T6/T8). Bằng chứng là lần chạy THẬT trong worktree `plan/ab-tich-hop` trên `main` `f4fa3a8` + plan A T1–T8, PATH chặn host, 0 dòng nhật ký chặn mới.

| Mã | Mức | Đã sửa ở đâu | Bằng chứng (đỏ → xanh thật) |
|---|---|---|---|
| R2-03 (§4.1) | Quan trọng | MỘT bản thân hàm: `chay_gioi_han`/`chay_han_tong` do plan A-T4 viết (hạn trước spawn, selector `with`, `_don` đóng từng ống rồi luôn thu hồi trong `hoan()`, `chu` + `GopKill` + `_don` của V2-1 giữ nguyên); B-T6 chỉ thêm `stdin=` (hunk trên bản A), B-T8 không sửa `han_tong.py`. MỘT cơ chế ngắt: `ngat.hoan` của A-T2; B-T6 thêm `term_thanh_ngat` cuối file. Fault injection viết lại tại điểm đọc thật (`_doc` của vòng selector) — không còn Popen giả có `communicate`. | Bản vòng 2 không ghép được: `ong_chep.py` vòng 2 trên cây A → `7 failed, 8 passed` (`TypeError … 'chu'`). B-T6: đỏ `2 errors` (thiếu `NgatTerm`) / `3 failed, 18 passed` (thiếu `stdin=`) → `21 passed`; sáu ca `test_chay_gioi_han_ngat.py` (SIGTERM THẬT ngay sau Popen qua hai lớp; `_doc` ném OSError/KeyboardInterrupt × thu hồi True/False; SIGTERM lần hai lúc thu hồi) xanh trên bản A. Áp lại hai plan lên bản sạch: `diff -r` khớp; cả bộ `3062 passed in 266.06s`. |
| R2-02 (phần B) | Chặn | Không còn dựa vào "H-A03": mọi spawn của B theo hợp đồng `so_huu` — `nguon_archive(chu=)` bắt buộc, `ong_chep` thu hồi `chu` trong `finally` (Task 7); `lenh_nghiem_thu` có `term_thanh_ngat` từ đầu + preflight trong `hoan()` (Task 8); `han_tong` của A thu hồi `chu` trong `hoan()` rồi mới ghi kết quả. Test SIGTERM/Ctrl-C THẬT trên đường A+B với backend giả: `test_ngat_ab.py` (ngay sau Popen harness; lần hai lúc thu hồi; kill bị từ chối + gốc treo → dấu giữ, `Nhom` còn trong `chu`; preflight → 143), `test_ctrl_c_ngay_sau_khi_nguon_spawn…` (nguồn `git archive`). | B-T8 đỏ: `5 failed, 13 passed` (`SigtermLot` ×5 — CLI cha chưa có handler; lần chạy đỏ đầu tiên không có handler canh bị chính SIGTERM mặc định phát lại giết pytest sau `..........FF`) → `49 passed`. B-T7 `15 passed`, nhóm bản chép/kiểm lại `109 passed`. |
| B03 | Chặn (vòng 1) | Nay ĐÓNG hẳn: phần còn mở ở vòng 2 (ghép với ownership của A; SIGTERM thật qua hai lớp) giải bằng hai dòng trên | như trên |
| B01, B02, B04 | — | Đã đóng ở vòng 2 — không đổi (Task 1, 2, 7, mục G4) | B-T1…T5 chạy lại trên cây A: cùng số đỏ, `100 passed`; B-T7 giữ nguyên các ca B02 (`test_ong_chep_uu_tien.py` 7 ca + `test_ban_chep_pipeline_han.py`) |
