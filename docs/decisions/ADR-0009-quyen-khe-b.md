# ADR-0009 — Khe B giữ đăng nhập Claude riêng, quản lý giữ quyền Git
**Trạng thái:** Chấp nhận · 2026-10-21 — QĐ2-A sửa phần token; QĐ3-A giữ nguyên
**Bối cảnh**
Hai khe Claude trên B cần dùng hai tài khoản riêng, sửa cây mã và báo kết quả,
trong khi Git chung, cấu hình phiếu và bí mật trạm phải nằm ngoài quyền ghi của khe.
**Quyết định**
Mỗi khe B giữ token `claude setup-token` trong file riêng 0600/thư mục 0700, không symlink;
wrapper dưới UID khe mở file và exec Claude qua FD, không token trong argv/log/env quản lý.
Token máy B ở file 0600 của tram-tho; máy từ xa giữ Keychain. Ngoại lệ file chỉ cho hai loại này;
INV-001 vẫn cấm credential trạm/GitHub/khe khác. Sudoers ALL hiện có không chống quản lý đổi UID.
Khe B chỉ sửa mã và append hàng đợi. Quản lý thợ chốt commit sau thu hồi sạch,
tự gắn SHA/nhánh/lượt; mốc tạm chưa công bố. Máy từ xa giữ luồng commit hiện có.
**Vì sao**
Không cần chuyển OAuth qua quản lý hoặc cấp quyền ghi metadata Git chung cho khe.
Mỗi lượt có cổng cha quản lý giữ; đóng cổng trước dọn, lỗi thì giữ phiếu và dừng khe.
**Phương án đã loại**
Dùng chung đăng nhập của Đại ca, chuyển token Claude qua env hoặc cho khe B ghi Git chung.
**Hệ quả**
Mã cùng UID có quyền dùng token Claude của khe. Keychain nền đã thất bại (36) ngày 21/10.
CLI qua FD, ACL hai UID và tự chạy sau reboot phải đo thật qua S2/S3/S6/R5/R7; test offline không cấp phép bật giao hoặc tự merge/deploy.
Kiểm lại Uq và QC khác khe vẫn bắt buộc; không đổi quyền hay policy của Uq.
**Nguồn**
[QĐ2–QĐ4](../../openspec/changes/doi-ngu-tho/QUYET-DINH.md),
[design §2–5](../../openspec/changes/doi-ngu-tho/design.md),
[plan Task 5–7](../plans/2026-10-20-doi-ngu-tho.md), [token file](../plans/2026-10-21-doi-ngu-token-file.md).
