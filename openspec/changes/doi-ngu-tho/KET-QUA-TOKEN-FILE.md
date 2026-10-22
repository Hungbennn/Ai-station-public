# Kết quả token file — 21/10/2026

Nền `b26cb9e`, nhánh `plan/token-file`. Chỉ sửa tài liệu; mã/test áp ở `/private/tmp/codex-token/`.
Không sửa `tram/`/`tests/`/`cong-cu/` trong worktree, không commit/bd/push, không gọi Claude/Keychain/sudo thật.

## Đã làm

- Cập nhật QĐ2 sửa 21/10 + bằng chứng Đại ca cung cấp; proposal/design/spec/tasks và đúng ADR-0009.
- Viết [plan TDD bổ sung](../../../docs/plans/2026-10-21-doi-ngu-token-file.md): 4 task, test/mã
  nguyên văn bằng 8 patch; R2/R4/R5 thay phần Keychain, giữ phần còn lại của plan 20/10.
- Token B chọn file, từ xa giữ Keychain; file kín/no-follow/nguyên tử. Wrapper mở FD dưới UID khe,
  lọc auth env rồi exec CLI. Sổ tay setup-token/getpass/stdin; S6 sáu phép mở/đóng không đọc nội dung.
- Đọc mã nhúng binary Claude 2.1.227: HEu đọc `/dev/fd/N`; tA ưu tiên OAuth env thường;
  Lgs chỉ persist file remote khi CLAUDE_CODE_REMOTE bật. Wrapper không giữ biến này.
  Hash/đường nguồn ở design §2; khảo sát tĩnh không phải chứng minh chạy CLI thật.

## Kiểm chứng

| Phép kiểm | Kết quả thật |
|---|---|
| Trích trực tiếp 8 patch từ plan, áp tuần tự lên bản sao HEAD | `git apply --check` đạt cả 8; cây Python khớp từng byte với cây đã test |
| Task 1 | RED 13 failed → GREEN 13 passed |
| Task 2 | RED 6 failed/6 passed → GREEN 12 passed |
| Task 3 | RED 8 failed/10 passed → GREEN 18 passed |
| Task 4 | RED 8 failed/15 passed/1 deselected → GREEN 23 passed/1 deselected |
| Nhóm hồi quy cuối + độ dài/import | **166 passed, 2 deselected**, 14.57s; 0 dòng chặn mới |
| `openspec validate doi-ngu-tho --strict` | đạt với bản **1.11.0** đang cài, telemetry tắt |
| Bản pin OpenSpec 1.14.0 qua npm offline | **ENOTCACHED**; chưa kiểm được bản pin, không tải mạng/gói |
| `git diff --check` | đạt |

Lệnh test đầy đủ và hai tên bị loại có trong plan. Baseline 30 passed/1 failed do test đọc đường kho
thật đã tồn tại; đây không phải lỗi sandbox. Test vòng thợ trên HEAD chưa sửa cũng failed, báo không xác
nhận thu hồi; chưa đủ bằng chứng quy hết cho sandbox. Không sửa hoặc coi hai lỗi này là xanh.
Nhóm hồi quy cuối có 11 điểm mù Python con từ test dependency cũ và 44 push **giả lập**, không push thật.

Một RED ban đầu thiếu stub gọi đường Keychain đã bị bộ chặn giữ lại (1 dòng); đã sửa fake và chạy lại
chuỗi từ bản sao mới: mọi RED/GREEN cuối đều 0 dòng chặn. Log tạm:
`/private/tmp/codex-token/replay-{1..4}-{red,green}.log`, `final-related-clean.log`, `baseline-loop.log`.
Không chạy toàn suite trong phiên này; chưa có chứng nhận QC độc lập.

## Rủi ro và phần chỉ chứng minh ở máy thật

- **Phạm vi sudo chưa chốt:** sudoers hiện cho tram-tho `NOPASSWD:SETENV: ALL` dưới UID khe.
  0600 chặn đọc bằng UID quản lý trực tiếp nhưng không chống quản lý dùng sudo đổi UID.
  Đã hỏi Đại ca; chưa có trả lời trong phiên. Không tự nới nghĩa “quản lý không đọc được”.
  Nếu yêu cầu bao gồm chống sudo, plan này chưa đáp ứng và cần thiết kế ranh giới riêng trước triển khai.
- Mode POSIX không chứng minh ACL macOS. S6 phải xác nhận owner đọc được, sáu phép âm đúng lỗi quyền,
  không có ACL kế thừa cấp đọc token. Mã cùng UID khe vẫn đọc/dùng được token của chính khe.
- S2/S3: FD thực qua sudo/exec/CLI, hai account khác nhau, auth status và headless từ system daemon,
  không `.credentials.json` hoặc cache credential khác ngoài file đã duyệt. Hai vị trí dò không chứng minh
  toàn bộ hành vi lưu của CLI. Token setup-token hết hạn/thu hồi cần cấp lại có chủ ý.
- R5: tự chạy sau reboot, không unlock/login lại/cấp token mới; phải đo đúng lần boot, readiness API,
  daemon gốc và nhịp. Do-nen thủ công sau đăng nhập không đủ. **bs-2bd.11 chưa được giải bằng bằng chứng.**
- Nâng CLI phải đo lại; sửa runtime/sudoers/ACL/plist thật, bật giao và đóng bead không thuộc phiên này.
  Quyền Git, Uq, kiểm lại/QC, quota và công tắc cũ giữ nguyên.

**Kết luận: Đã soạn và kiểm plan trên bản sao HEAD; chưa đủ điều kiện triển khai/nghiệm thu do phạm vi sudo chưa chốt và S2/S6/R5 máy thật chưa đo.**
