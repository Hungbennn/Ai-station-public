# Design — phần giữ sau hợp nhất 20/10/2026

Nguồn hiện hành về merge/deploy: [design kế tiếp](../tu-merge-deploy/design.md),
[QĐ1–QĐ4 đã chốt](../tu-merge-deploy/QUYET-DINH.md) và plan 20/10.

Giữ cấu hình bằng sự kiện (`tram/tu_dong/`), idempotency `tram/thao_tac/`,
passkey hiện có, màn Tự động/Phê duyệt và Telegram. Không thêm bảng DB, màn hay dịch vụ trạm.
D-2 cũ về tự phân loại mọi CI và D-6 cũ về HEAD/tài khoản trạm không còn dùng để triển khai.
Các plan TM-1…TM-4 ngày 18/10 là lịch sử mã đã có, không phải lệnh áp lại.

`dieu-khien-tu-dong` ở change này đã chỉnh CI thành khoá cứng và dẫn cửa passkey để tránh
archive làm sống lại nút bỏ CI hoặc ngoại lệ Tiếp tục bằng header.

Bản đầy đủ trước hợp nhất: [design 18/10](lich-su-design.md).
