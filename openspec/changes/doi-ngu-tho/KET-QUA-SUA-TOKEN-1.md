# Kết quả sửa token lần 1 — 21/10/2026

Đại ca, Bé thực hiện trên worktree `code-token`, nhánh `code/token-file`, HEAD `7b31edf`.
Đã đọc `../../.handover/codex-viec/CHUNG.md`, báo cáo `KET-QUA-CODE-TOKEN.md` và luật dự án.
Việc loại ca vòng thợ khỏi lần kiểm trước đã bỏ sót hồi quy thật Đại ca đo trên B.
Lần này chạy lại nguyên ca đó và toàn bộ file test dùng `tho_chay_gia`, không bỏ/chọn loại test.

## Đã sửa

Nguyên nhân: `PrincipalGia.boc()` chỉ thay argv mở đầu bằng `claude`; đường B mới dựng
`python -I …/claude_token.py chay …` trước khi qua principal, nên đi vào CLI/UID/token thật.

- `tram/tho/claude_token.py`: thêm hai tham số Python chỉ định bằng tên, `kiem_token` và `exec_cli`.
  Mặc định vẫn gọi `kiem()` và `os.execve()` như trước. `main()` không truyền tham số tiêm;
  không thêm cờ CLI, biến môi trường hay khoá YAML cho phép bật đường giả.
- `tests/tho_chay_gia.py`: principal giả nhận đúng tiền tố từ `lenh_token_khe('chay')`, kể cả
  sau lớp `/usr/bin/env` của kiểm dependency B, rồi thay bằng helper chỉ nằm trong `tests/`.
  Mỗi fixture tạo token `oauth-gia-lap` trong thư mục tạm với thư mục 0700/file 0600 bằng kho token thật.
- `tests/claude_token_gia.py`: gọi hàm wrapper thật với đường token giả và exec giả. Sau exec,
  tiến trình CLI giả phải đọc đúng token từ FD rồi đóng FD trước khi chạy kịch bản cũ.
- `tests/test_tho_token_gia.py`: kiểm subprocess chạy được CLI giả qua FD; sai quyền bị từ chối;
  exec lỗi vẫn đóng FD; giá trị token không xuất hiện trong argv/env/stdout/stderr.

Phạm vi sản phẩm chỉ một file, hiện 70 dòng. Không sửa assertion của bất kỳ test cũ nào.
Giữ CLI `/opt/homebrew/bin/claude`, kiểm UID `tram-khe1/2`, lọc env, kiểm file kín/no-follow/hardlink,
kiểm dạng token và truyền FD của đường mặc định. Không thêm dependency hay sửa cơ chế thu hồi/cách ly.

## Kiểm chứng đã chạy

Mọi lượt test dùng cùng môi trường và runner Đại ca chỉ định:

```bash
export PYTHONPATH="$PWD"
export UV_PROJECT_ENVIRONMENT='/Users/dai-ca/Developer/Ben Station/.venv'
export UV_NO_SYNC=1 UV_CACHE_DIR=/private/tmp/codex-token/uv
```

| Lượt | Kết quả thật | Nhật ký chặn |
| --- | --- | --- |
| Baseline: ca vòng thợ + wrapper token + độ dài | 1 failed, 10 passed | 0 dòng mới |
| RED: test mới + độ dài | 3 failed, 3 passed | 0 dòng mới |
| GREEN: test mới + wrapper + kho token + độ dài | 26 passed | 0 dòng mới |
| Toàn bộ file dùng fixture + nhóm token/principal liên quan | 20 failed, 136 passed; 464,75 giây | 0 dòng mới |
| Quyền/đăng nhập/launchd/đội ngũ/vòng import/độ dài bổ sung | 62 passed | 0 dòng mới |

RED thật: subprocess nhận `TOKEN-KHE: CHUA-XAC-NHAN`; hai ca còn lại nhận
`TypeError: chay() got an unexpected keyword argument 'kiem_token'`. Sau sửa cả ba xanh,
trong đó subprocess đã qua exec và đọc FD thật, không phụ thuộc chụp cây tiến trình.
Đây là vòng RED → GREEN theo systematic-debugging/TDD; đã tự rà diff theo code-review-and-quality.

Lệnh tích hợp, không `-k`, không bỏ ca:

```bash
tests/chan_host/chay.sh -q $(rg -l tho_chay_gia tests) \
  tests/test_tho_token_gia.py tests/test_claude_token_file.py \
  tests/test_token_file.py tests/test_token_may_file.py tests/test_doi_ngu_token_file.py \
  tests/test_token_may.py tests/test_principal.py tests/test_kiem_cong.py \
  tests/test_dang_nhap_principal.py tests/test_do_dai_ma.py
```

Lệnh bổ sung:

```bash
tests/chan_host/chay.sh -q tests/test_launchd_token_tho.py tests/test_doi_ngu_nen.py \
  tests/test_doi_ngu_cong_cu.py tests/test_doi_ngu_cai.py tests/test_doi_ngu_dang_ky.py \
  tests/test_doi_ngu_giao.py tests/test_doi_ngu_bao.py tests/test_doi_ngu_pham_vi_kiem.py \
  tests/test_doi_ngu_quyen.py tests/test_vong_import.py tests/test_do_dai_ma.py
```

Nhật ký trong `/private/tmp/codex-token/sua-token-1/`: `baseline.log`, `red.log`, `green.log`,
`integration-default-tmp.log`, `security-related.log`, `events.json`, `sysctl.log`.
Lượt tích hợp có 23 điểm mù Python con và 131 push giả lập; lượt bổ sung không có điểm mù,
4 push giả lập. Không có push thật.

Có một lượt chạy sai do Bé tự đặt `--basetemp=/private/tmp/codex-token/sua-token-1/pytest`:
**68 failed, 88 passed, 62 dòng chặn mới** (`integration.log`). Git giả từ chối kho ngoài gốc tạm
của runner; kiểm đường dẫn SQLite cũng từ chối. Đã bỏ tuỳ chọn này và chạy lại đủ nhóm như trên.
Lượt sai không dùng làm bằng chứng hồi quy hay kết luận xanh; bộ chặn không được nới.

## Phân biệt các ca còn đỏ

Đo trực tiếp trong chính sandbox (`sysctl.log`): `chup_nhan()` ném
`PermissionError: [Errno 1] sysctl: không đọc được kích thước bảng`; `mot_nhan()` của chính
Python đọc được. `/bin/ps` cũng bị `operation not permitted`.

Ca `test_chay_may_tron_vong_roi_don_worktree_bead_da_dong` sau sửa có:
`khe.dang_ky` ×3, `khe.bat` ×2, `giao.nhan`, `chay.bat_dau` ×1, `khe.han_muc_khong_ro`.
CLI giả đã ghi `.tram/stdin-1.md` và argv; không có `chay.xong`, không có `khe.cau_dao_ngat`.
Khe giữ phiếu/PID và dừng vì không chứng minh được thu hồi. Khác chuỗi lỗi thật ngoài sandbox
Đại ca cung cấp: `chay.xong` lặp ba lần rồi ngắt cầu dao. Không dùng thông báo thu hồi đơn lẻ để phân loại.
Lượt tích hợp sau sửa không còn thông báo `TOKEN-KHE`.

Ở nhóm đỏ chạy tiến trình CLI giả, mỗi fixture ghi một `chay.bat_dau`, không ghi `chay.xong`
hay cầu dao; CLI giả đã nhận stdin. Các ca mock CLI bằng Python object được phân biệt riêng.
Dữ liệu từng fixture, gồm sự kiện đã bỏ nội dung nhạy cảm và số file stdin/argv, nằm trong `events.json`.

**19 ca đỏ liên quan xác nhận thu hồi trong sandbox**, giữ nguyên assertion:

- `test_tho_lenh_chay.py`: ca vòng thợ nêu trên (1).
- `test_kich_ban_3a2.py`: trọn vòng code (B/từ xa), CLI thoát rồi tiếp tục (B/từ xa), tắt khe,
  thu hồi cứng (B/từ xa), hết hạn mức, cần hỏi, tắt rồi khởi động lại (10).
- `test_tho_chuan_bi.py`: ba lần chạy/cầu dao và nguồn lùi log hạn mức (2).
- `test_khe_tan_du.py`: tàn dư sau lần chạy; dừng sớm ở thu hồi cây nên chỉ có 2 lần gọi dọn UID thay vì 3 (1).
- `test_tho_theo_doi_ket_thuc.py`: báo xong và ref bị đẩy ngoài luồng; thu hồi nhóm lệnh kiểm lỗi (2).
- `test_chay_cli_vong_doi.py`: thu hồi cả cây Claude/Codex và lỗi giữa spawn/chờ (3).

**1 ca đỏ riêng, không quy cho sandbox:**
`tests/test_bo_codex.py::test_dang_ky_vao_bo_cli_cua_vong_tho` so
`captured['factory'][0] == pc.principal.boc`, nhưng B cấp hàm `boc_kiem_b(pc)`.
Ca này có đúng một `chay.xong`, không có cầu dao; CLI đã được mock nên không lỗi token.
`git diff main -- tests/test_bo_codex.py tram/tho/mot_lan.py` rỗng: assertion và caller giống hệt
main hiện tại `2bfe428`. Chưa chạy đối chứng ca này trên main; không tự sửa assertion hay mở rộng phạm vi.

## Bàn giao

Đã sửa đường nối và chứng minh CLI giả/token giả qua FD chạy được; các nhóm bảo mật liên quan xanh.
**Chưa xác nhận ca vòng thợ xanh ngoài sandbox.** Cần người điều phối chạy lại nguyên lệnh tích hợp
trên B ngoài sandbox và đối chứng riêng ca Codex trên main. Không coi 20 ca đỏ là đã đạt.

`git diff --check` đạt; test độ dài và vòng import xanh. Không chạy toàn suite, không commit/push,
không dùng bd/sudo, không sửa CURRENT_STATE hay tạo handover, không chạm token/tài khoản/dịch vụ thật.
Báo cáo đặt tại file này theo chỉ định của Đại ca, thay tên báo cáo chung trong CHUNG.md.
