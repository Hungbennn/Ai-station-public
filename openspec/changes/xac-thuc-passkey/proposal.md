# Proposal — Cửa ghi dashboard bằng passkey

Bead: **bs-2bd.9** · Ngày: 18/10/2026 · Trạng thái: **Đã cập nhật D146–D150 — chờ review plan; mockup đã duyệt D150**.
Nguồn chính: [D137–D150](../../../docs/quyet-dinh/2026-10-18-passkey.md);
[G29, D135–D136](../../../docs/quyet-dinh/2026-10-18-tu-merge-tu-deploy.md),
[PROJECT — D136](../../../docs/PROJECT.md).

## Why

G29 đo được app Tailscale trên macOS trả 502 khi Serve trỏ vào Unix socket. Header Tailscale qua TCP lại có thể
bị tiến trình cục bộ giả. Đại ca chọn passkey để thao tác nguy hiểm cần bằng chứng xác nhận của người, kể cả
khi agent chạy trên máy A. Tailscale giữ vai trò mạng riêng và danh tính, Serve chuyển tới cổng TCP (D135).

## What Changes

- Có danh sách người và quyền; hiện đúng một người là Đại ca, vai `chu` (chủ), chưa mở trạm nhiều người (D136).
- Cửa ghi phân biệt thao tác thường, nguy hiểm (D138), luôn chạm lại (D140). Quyền do máy chủ quyết.
- Passkey phải thuộc đúng người có login Tailscale của yêu cầu (D143). Sau xác nhận, trình duyệt có phiên 8 giờ
  với cookie HttpOnly, Secure, SameSite=Strict (D139); quản lý thiết bị, bật tự deploy, sửa ba lệnh vẫn chạm lại.
- Đăng ký lần đầu bằng mã một lần từ lệnh máy B, hạn 10 phút (D141). Thêm thiết bị bằng thiết bị cũ hoặc mã máy B;
  mỗi lần thêm/thu hồi có tin Telegram (D142); trong giờ yên lặng gom gửi buổi sáng (D149). Khôi phục tại B với `dong-y`, thu hồi tất cả passkey và phiên (D144).
- Windows dùng Windows Hello, điện thoại qua QR của trình duyệt, hoặc khoá USB; không giả định iCloud đồng bộ sang Windows.
- **BREAKING:** thay điều kiện `unix-socket` của D87 bằng passkey. Khi chưa có passkey, cửa dashboard cũ chỉ nhận
  TẠM DỪNG/Estop; Tiếp tục bị từ chối. Đây cũng sửa phần spec tự động cũ đang cho Tiếp tục qua kênh tạm.
- Giữ `ma_thao_tac`, phiên bản dữ liệu, khoá ghi dự án, kiểm lại và Estop; không đưa bí mật vào sự kiện/log/Telegram.
- D145 cho phép `webauthn` và các phụ thuộc đã nêu; plan ghim bản đã phát hành ít nhất hai tuần. Phiên này không tải gói.

## Capabilities

### New Capabilities
- `cua-ghi-passkey`: danh tính người/quyền, phân loại toàn bộ cửa ghi, phiên, xác nhận lại, đăng ký, thiết bị,
  khôi phục, tương thích trình duyệt, chống lặp và bảo vệ bí mật.

### Modified Capabilities
- Không có spec đã archive tương ứng. Khi tích hợp, đồng bộ change `tu-merge-tu-deploy` và
  `agent-tu-cap-nhat-viec`: bỏ điều kiện mở nút dựa vào socket, dùng cửa này. Không sửa hai change trong phiên này.

## Impact

Kill list khi triển khai: **1** cửa danh tính, **2** credential và Telegram, **4** kho người/passkey/phiên,
**7** công tắc lớn, **8** cổng chạy thật. Bản đồ tuyến và nơi nối ở [design.md](design.md).
Ảnh hưởng API, cấu hình, CLI chủ trạm, lưu trữ xác thực, báo tin, frontend. Không viết mã các vùng này ở việc hiện tại.
Mockup: [docs/mockup/2026-10-18-passkey](../../../docs/mockup/2026-10-18-passkey/README.md).

## Ngoài phạm vi

Không làm phân quyền công ty, mời người, đăng nhập mật khẩu, dịch vụ danh tính ngoài, hỗ trợ server Windows/Linux,
đổi luật tự merge/deploy hay quyền agent. Không mở mạng công cộng. Không triển khai, tải dependency, đổi Serve,
chạy Touch ID thật, sửa cấu hình máy, commit hoặc ghi Beads trong phiên spec.

## Plan và các chốt bổ sung

D146 yêu cầu hồ sơ trình duyệt dashboard riêng, không cho agent điều khiển và phải đo cổng thật.
D147 miễn chạm cho ghi ký ức tay/gửi phiếu yêu cầu (vẫn khoá trước đăng ký); D148 cấm thu hồi passkey cuối trên web.
D150 đã duyệt chín màn mockup. Plan TDD: [2026-10-18-lat-passkey.md](../../../docs/plans/2026-10-18-lat-passkey.md).
