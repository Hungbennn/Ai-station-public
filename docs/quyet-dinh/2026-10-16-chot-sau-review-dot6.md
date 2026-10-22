# Quyết định Đại ca chốt — 16/10/2026, sau review đợt 6

Trạng thái: **ĐÃ CHỐT hướng và hợp đồng; CHƯA nghiệm thu triển khai/chạy thật.**
Nguồn: Đại ca xác nhận “Chốt cả 3 theo đề xuất của em nhé. Em cập nhật plan rồi soạn prompt bàn giao cho Claude làm, ghi rõ các cổng cần nghiệm thu trước khi chạy thật.” Ba nhóm được trình ngay trước lời xác nhận này.

Tiếp nối D1–D44 của `2026-10-15-chot-dot-4.md`; không sửa lịch sử. Nếu repo đích đã dùng D45–D47 cho quyết định khác, giữ nguyên nội dung, đổi số nối tiếp và cập nhật mọi tham chiếu, không ghi đè.

| # | Đại ca chốt | Hệ quả / giới hạn |
|---|---|---|
| D45 | Giữ cách ly nghiêm ngặt giữa các lần kiểm, không root lúc chạy. HOME/TMP riêng mỗi lượt, home tài khoản kiểm `/var/empty`. | Giữ D22/D40. Thiết kế phải cưỡng chế giới hạn nơi ghi và nguồn thực thi; quét/dọn đơn thuần không đủ. Không chứng minh được thì chặn S6 và trình thay đổi kiến trúc, không tự dùng VM/root helper. |
| D46 | Máy A phỏng vấn và gửi yêu cầu; **máy B sở hữu tạo feature qua API có xác thực**, chống trùng bền. | Thay đường skill gọi `bd create` từ A trong 4d. Không còn là fallback đợi Task 0 thất bại. Cùng yêu cầu trả cùng feature; kết quả chưa rõ phải đối soát, không tự tạo lại. Chỉ thêm API/khóa cục bộ không đủ. |
| D47 | Mã yêu cầu cố định, độc lập nội dung. | Sửa nháp trước gửi giữ mã. Sau tạo: cùng mã/cùng nội dung trả feature cũ; khác nội dung báo xung đột, không tạo thêm/ghi đè. Yêu cầu mới phải được chọn rõ và có mã mới. Giữ marker trong mô tả; actor `dai-ca/may-a` chỉ là nhãn nguồn, không chứng thực. |

## Các điều kiện kèm theo đã chốt

- Lịch ngoài phạm vi cho phép hoặc không xác nhận được cleanup: lượt kiểm không hợp lệ, chặn lượt tiếp. Cho phép thiết kế bước Đại ca chụp mốc launchd ban đầu; mốc chỉ hỗ trợ quan sát, không phải bằng chứng cách ly. Chưa sửa `cron.deny`/`at.deny` trên máy.
- Giữ xác thực; thiếu danh tính thì dừng, không bỏ kiểm tra `/api/phieu/kiem` hoặc mở đường ghi thay thế. Không mở rộng token D24; không đưa token/Keychain vào skill.
- Nháp/biên bản ngoài repo. Không tự lưu `docs/discussions/`; chưa có UI mới, mockup vẫn cần duyệt nếu sau này thêm UI.
- Timeout hữu hạn, thu hồi tiến trình, kiểm UID thực, quota đúng principal và kiểm cây Git CRLF/encoding là yêu cầu kỹ thuật phải sửa; không cần hỏi lại Đại ca có muốn an toàn hay không.
- Chốt thiết kế không xác nhận blocker đã đóng, không cấp quyền chạy cron/at/launchd, sửa tài khoản/sudoers/Keychain, bật dịch vụ, tạo bead thật hay bật giao việc.

## Phạm vi thay quyết định cũ

D46 thay cách tạo của riêng skill 4d trong spec §7.1 và plan 4d G7/G9; không bãi bỏ Task 0/D1 cho các luồng Beads từ xa khác. Đường mới phải có cổng chứng minh ánh xạ dự án → kho B riêng. D47 thay hash-nội-dung làm danh tính yêu cầu ở G10. C1/C3/C4/C5/C6 của 4d đã có hướng xử lý; C2 chọn giữ xác thực và dừng nếu H5 không đạt. Không coi các thay đổi này là D42 hoặc D44 đã duyệt từ trước.

## Chốt thêm sau thiết kế (16/10)

| # | Câu hỏi | Đại ca chọn |
|---|---|---|
| D48 | 3c Q-A: kiểm lại chạy trong Seatbelt cấm mạng (kể cả loopback) và semaphore/IPC | **Chấp nhận.** Dự án dùng SQLite/file cục bộ cho `.env.testing`, gói cài sẵn trước. Dự án không đáp ứng được thì lượt kiểm báo lỗi rõ ràng. |
| D49 | 3c Q-B: cổng kiểm đóng khi có bất thường | **Đóng và chờ Đại ca mở** bằng `tram giao mo-cong-kiem`; trạm không tự mở. |
| D50 | 3c Q-C: R7 từ chối repo có CRLF dưới `text`, `ident`, submodule, trùng tên hoa–thường, `._*`, kho sha256 | **Chấp nhận.** Báo `cay-khac-nguon` + escalation. |
| D51 | 4d: tuyến tạo feature ở chế độ kênh ghi `header` | **Giữ ngang dashboard**; cổng G6.5 kiểm khi chạy thật; lâu dài chuyển cả trạm sang `unix-socket` (G29, sau N2). |
| D52 | G3: lệnh `sudo launchctl procinfo <pid>` (root, chỉ đọc) để lấy asid miền `login/<asid>` | **Cho phép, Đại ca tự gõ** trong Terminal.app khi tới bước G3. Agent không chạy sudo. |
| D53 | S6 thử cơ chế nào | **Chỉ cơ chế `user`** (đúng D3). Nhánh `sandbox` giữ mã, cổng đóng; chỉ xem lại nếu S6 cho thấy `user` hỏng. |
