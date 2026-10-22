# ADR-0003 — Giao việc theo phiếu có lượt cho từng khe; máy thợ xác thực bằng token máy

**Trạng thái:** Chấp nhận (hồi tố) · 2026-10-17 — quyết định có từ trước, ghi lại từ code và quyết định đã chốt

**Bối cảnh**
Nhiều CLI, nhiều tài khoản, nhiều Mac; Mac thợ có thể gập hay mất mạng giữa chừng. Qua `tailscale serve`, mọi yêu
cầu tới tram-api đều đến từ `127.0.0.1`, nên trạm không phân biệt được máy theo địa chỉ nguồn.

**Quyết định**
Đơn vị giao việc là **khe** = (máy, CLI, tài khoản), mỗi khe một thư mục cấu hình và một hạn mức (Q10). Mỗi bước là
một **phiếu**: cấp phiếu, tăng `luot`, giữ trước ngân sách, giữ khe trong một giao dịch; báo cáo mang lượt cũ bị từ
chối (§5.5). Máy thợ gọi `/api/tho/*` bằng **token máy** (trạm chỉ giữ sha256), lấy bằng mã ghép một lần, sống 10
phút. CLI của phiếu dùng `ma_giao` 128 bit làm credential riêng.

**Vì sao**
Thẻ chắn theo lượt (ý của ruflo) chặn máy gập rồi thức dậy ghi đè việc đã giao lại. Địa chỉ nguồn không phân biệt
được máy (spec 3 §5.1), nên cần token; token máy không bao giờ có quyền Đại ca. `giao_id` đoán được, không là bằng chứng.

**Phương án đã loại**
- Nhận máy theo địa chỉ hay danh tính Tailscale: mọi yêu cầu đến từ localhost; Mac thợ là thiết bị gắn tag (Q9).
- Hợp đồng giữ việc không thẻ chắn; "mỗi bước một lần chạy CLI" (thay bằng tối đa 3 lần mỗi phiếu, #13).

**Hệ quả**
Được: giao lại an toàn khi khe chết; hạn mức tính theo khe. Mất: GitHub không biết `luot`, nên chặn tới remote cần
trạm công bố ([ADR-0007](ADR-0007-tram-giu-quyen-day.md)). Thu hồi token máy vô hiệu mọi phiếu và `ma_giao` của máy đó.
Chạy thật còn chờ cổng S2/S6 (Keychain của tài khoản quản lý thợ khi không có phiên đăng nhập).

**Nguồn**
[Spec kiến trúc](../specs/2026-10-12-tram-dieu-phoi-kien-truc.md) Q9, Q10, §5.5, §6 · [spec 3](../specs/2026-10-13-phan-3-may-tho-han-muc.md) §4, §5.1, §6, §9.2 · #13 ·
`tram/phieu/cap.py`, `tram/phieu/luoc_do.py`, `tram/phieu/ma_ghep.py`, `tram/tho/token_may.py`, `tram/api/tho.py`, `tram/api/ghep.py`.
