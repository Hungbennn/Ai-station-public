# Hai thợ Claude làm việc trên máy B

Status: `REVIEW` · 20/10/2026 · nền `19a86c0`, nhánh `spec/doi-ngu-tho`.

## Why

Đại ca đã chốt: chạy thật **ben-station trước**, với hai khe `B/claude-1`,
`B/claude-2`. Trang Đội ngũ đang trống; chỉ xác nhận có tài khoản Mac `tram-khe1`.
`vn.tram.tho` đã bị bootout và disable sau lỗi lặp khi khởi động máy.
Bộ quản lý kiểm Uq đã chạy chính thức và qua phép thử khởi động lại.

Nguồn: yêu cầu Đại ca trong chat 20/10; `docs/handovers/2026-10-20-log-phien.md`,
hai bản bối cảnh được giao trong worktree. Căn cứ mã được giữ trong `design.md`;
hai bản bối cảnh sẽ xoá theo yêu cầu khi bàn giao.

**Bead:** chưa gắn mã; Đại ca cấm gọi `bd` trong phiên này. Đây là ngoại lệ có chủ đích
với quy ước bead trước trong `docs/OPENSPEC.md`, không tự đặt mã bead giả.

## What Changes

- Cài phần thợ ở trạng thái tắt, tạo khe 2, giữ nguyên phần kiểm Uq đã cài.
- Đăng ký máy B ngay tại B bằng token máy trong file 0600 của `tram-tho` trên B;
  không đi qua lệnh cấp mã ghép từ xa đã đóng.
- QĐ2 sửa 21/10: Claude dùng setup-token trong file 0600 riêng từng UID; wrapper sau sudo
  mở file rồi truyền FD. Không chép phiên hungle, không token trong argv/log/env quản lý.
- Bổ sung đường gửi thay đổi để quản lý thợ chốt commit. Khe chỉ sửa cây mã của
  phiếu, không cần quyền ghi kho Git chung, cấu hình Git hay hooks.
- Mỗi lượt có cây/cổng quyền riêng; đóng cổng và dọn cây khi kết thúc. Cấp dependency offline từ
  bundle root đã cài cho Uq bằng helper sẵn có, không sửa Uq hoặc mở quyền root.
- Dùng kho đọc cục bộ trên B, trạm giữ quyền GitHub. Giữ remote `github` của
  Đại ca, thêm `origin` cùng đích khi chưa có; gặp đích khác thì dừng.
- Kiểm riêng ben-station; sau các cổng, mở ngay mọi việc đủ điều kiện của dự án (QĐ5-B).
  Giữ ngân sách/quota/cầu dao, HR và tự merge/deploy tắt. Không thêm màn hình.

## Capabilities

### New Capabilities

- `doi-ngu-tho`: chuẩn bị, đăng ký và vận hành hai khe Claude trên B cho ben-station.

### Modified Capabilities

Không sửa capability đã archive. Thay đổi theo QĐ2-A/QĐ3-A đã chốt với ý đồ cũ được nêu ở
`design.md`: quyền commit của khe và nghĩa “không credential”.

## Impact

Plan bổ sung token: [2026-10-21-doi-ngu-token-file.md](../../../docs/plans/2026-10-21-doi-ngu-token-file.md).
Plan nền: [2026-10-20-doi-ngu-tho.md](../../../docs/plans/2026-10-20-doi-ngu-tho.md).
Chạm `tram/chu`, `tram/tho`, `tram/chay_cli`, `tram/cau_hinh`, `tram/giao_viec`,
prompt vai và công cụ chạy thật; không đổi schema, API người dùng hay UI.
Kill list §2: mục 2 (đăng nhập/Keychain), 3 (quyền khe), 6 (cài dịch vụ),
7 (giao việc), 8 (chạy thật). **Phiên này chỉ soạn tài liệu**, không cấp quyền thực hiện.

## Ngoài phạm vi

HR Codex, khe Codex, Mac thợ từ xa, tự merge/deploy ben-station, cài lại Uq,
đổi passkey, bỏ kiểm lại/QC, thêm dịch vụ nền hay bảng chứng nhận tự ghi tay.
Đích bổ sung 21/10: tự chạy sau reboot không mở Keychain; phải đo ở S2/R5 trước khi xác nhận.

## Quyết định đã chốt

[Năm quyết định](QUYET-DINH.md): QĐ1–QĐ4 = A, QĐ5 = B. Đây là duyệt hướng thiết kế,
không cấp phép chạy thật. Chỉ archive khi đủ bằng chứng offline **và** chạy thật.
