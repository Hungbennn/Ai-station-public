# Bốn quyết định Đại ca đã chốt

Bản nháp 20/10/2026, bead `bs-2bd.3`. **ĐÃ CHỐT 20/10/2026: Đại ca chọn đúng khuyến nghị ở cả QĐ1–QĐ4** (QĐ1 GitHub chặn, QĐ2 bản đã kiểm, QĐ3 quyền riêng từng dự án, QĐ4 bắt buộc đường quay lại trước).
[Spec](proposal.md) dùng lựa chọn A đã chốt và đánh dấu QĐ1–QĐ4.
Các chốt 18/10 còn lại giữ nguyên; bảng đối chiếu nằm trong proposal.

## QĐ1 — Ai giữ luật “đủ kiểm mới được gộp code”?

**Quyết định gì →** Có để GitHub chặn bắt buộc trước mỗi lần trạm gộp code không?

**2–3 lựa chọn →** A. GitHub bắt đủ bài kiểm và nhánh phải cập nhật theo nhánh chính;
trạm chỉ giữ thêm kết quả kiểm chéo, kiểm cách ly và quyền được làm.
B. Giữ cách cũ: trạm tự đọc mọi bài kiểm, Đại ca có thể tắt điều kiện này.
C. Chỉ dựa vào kiểm tại máy Mac, không cần bài kiểm trên GitHub.

**Khuyến nghị 1 →** Chọn A. Luật ở nơi thực sự gộp code, bớt một bộ luật ghi riêng trong trạm.
Đây là đề nghị đổi D70–D71/D93 ở phần nút tắt CI và D94 ở phần cập nhật nhánh.
Repo chưa dùng được bảo vệ nhánh thì vẫn gộp tay.

**Hệ quả nếu chọn sai →** Luật quá lỏng có thể gộp hai bản riêng lẻ đều đạt nhưng dùng chung lại hỏng.
Luật quá chặt khiến việc chờ cập nhật nhánh hoặc cần đổi gói GitHub.

## QĐ2 — Bản nào được tự đưa lên cho người dùng?

**Quyết định gì →** Khi nhánh chính vừa có thêm code, trạm có lấy luôn bản mới nhất để deploy không?

**2–3 lựa chọn →** A. Chỉ lấy bản gộp đã xác minh, kiểm lại đạt trên chính bản đó.
B. Lấy đầu nhánh chính lúc deploy, kể cả code vừa được đẩy thẳng.

**Khuyến nghị 1 →** Chọn A. Nhiều việc dồn lại thì chọn bản mới nhất đã đủ kiểm;
bản có code ngoài luồng phải qua một lượt kiểm và xác nhận riêng. Đề nghị thu hẹp D125.

**Hệ quả nếu chọn sai →** B có thể đưa lên code chưa từng được kiểm. A tốn thêm một lượt kiểm
cho bản gộp và có thể chậm hơn khi có người sửa nhánh chính bằng tay.

## QĐ3 — Trạm được dùng quyền gì khi deploy?

**Quyết định gì →** Có chạy mã của dự án bằng tài khoản đang giữ bí mật của cả trạm không?

**2–3 lựa chọn →** A. Dùng đường deploy sẵn có của từng dự án, quyền chỉ đủ cho dự án đó;
trên Mac dùng dịch vụ launchd đã cài. B. Cho ba lệnh của dự án chạy bằng tài khoản trạm như thiết kế cũ.
C. Chuyển mọi dự án sang một hệ thống deploy mới.

**Khuyến nghị 1 →** Chọn A. Vẫn ba việc: đưa bản lên, kiểm hoạt động, quay lại.
Dự án chưa có đường deploy với quyền riêng thì để chờ thiết lập một lần, không tự nâng quyền.
Giữ D73/D88; thay cách chạy dưới tài khoản trạm trong design cũ D-6.

**Hệ quả nếu chọn sai →** B có thể làm lỗi hoặc mã lạ của một dự án chạm bí mật của cả trạm.
C kéo thêm việc vận hành; A cần chuẩn bị đường deploy cho từng dự án trước khi bật.

## QĐ4 — Lần deploy đầu có bắt buộc có bản quay lại?

**Quyết định gì →** Có bật tự deploy khi chưa xác định được bản đang chạy tốt và cách quay lại không?

**2–3 lựa chọn →** A. Phải xác nhận bản đang chạy tốt và thử quay lại trước khi bật.
B. Cho deploy trước; nếu hỏng mà chưa có bản cũ thì dừng chờ Đại ca.

**Khuyến nghị 1 →** Chọn A. Quay lại đúng bản đã chạy tốt, không tự khôi phục dữ liệu.
Đây là bổ sung điều kiện lần đầu cho D73/D75; vẫn giữ tự tắt sau ba lần deploy hỏng liên tiếp.

**Hệ quả nếu chọn sai →** B có thể để dịch vụ nằm chết ngay lần đầu. A mất một lần chuẩn bị;
dự án mới hoàn toàn cần dựng bản đầu bằng tay trước khi bật tự động.
