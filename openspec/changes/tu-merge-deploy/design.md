# Design — Ranh giới tối thiểu

**ĐÃ CHỐT QĐ1–QĐ4 (20/10).** Đọc cùng spec và plan 20/10.
QĐ1–QĐ4 trong [QUYET-DINH.md](QUYET-DINH.md) đều đã chọn khuyến nghị A.

## Giữ cơ chế sẵn có

| Việc | Nơi chịu trách nhiệm |
| --- | --- |
| Kiểm mã không tin cậy | Uq quản lý lượt, principal `tram-kiem`, Seatbelt và cổng hiện có; trạm nhận kết quả sau thu hồi |
| Kiểm chéo, quyền làm, đúng lượt/commit | Luồng phiếu, QC, bằng chứng và sự kiện hiện có |
| CI bắt buộc, nhánh cập nhật, quyền merge | Bảo vệ nhánh/ruleset GitHub; không tài khoản bypass cho trạm [QĐ1] |
| Chọn bản chạy, trạng thái, chống lặp | Luồng deploy và kho sự kiện hiện có, không sổ biên nhận mới |
| Chạy/giữ dịch vụ dự án trên Mac | launchd đã cài đúng nhãn và miền; không tự tạo dịch vụ cho từng lần deploy [QĐ3] |
| Bật quyền, sửa lệnh, tiếp tục | Cửa passkey và quyền hiện hành; agent không tự cấp |

GitHub hỗ trợ kiểm bắt buộc, nguồn check đáng tin và chế độ yêu cầu nhánh cập nhật;
quyền bypass phải được loại khỏi tài khoản trạm. Repo/gói không hỗ trợ cấu hình cần thiết thì giữ merge tay.
Đây là lựa chọn QĐ1, không phải điều đã kiểm trên repo thật.
[Nguồn GitHub](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches).

Trạm gửi merge ngay với commit dự kiến; không đăng ký `--auto` hay merge queue rồi để GitHub chạy sau
khi trạm đã dừng. `--match-head-commit` ràng buộc đầu PR, không khoá đầu nhánh chính;
bảo vệ nhánh xử lý điều kiện phía GitHub, bản merge vẫn cần kiểm lại trước deploy [QĐ2].
Giữ merge commit thường để dùng xác minh tổ tiên hiện có.
[Nguồn gh](https://cli.github.com/manual/gh_pr_merge).

## Đường deploy theo dự án

Giữ ba thao tác đã có, cài đặt trong sự kiện theo D88. Mỗi dự án khai một đích, ba thao tác có giới hạn,
định danh bản đang chạy và bản quay lại. Đây là hợp đồng của đường deploy, không định nghĩa schema mới.
Không có một bộ lệnh dùng chung được tự đoán cho mọi dự án.

**[QĐ3]** Trên Mac: dùng dịch vụ launchd hiện có của dự án; chọn bản phát hành cố định, chuyển bản,
khởi động đúng dịch vụ rồi kiểm ứng dụng. launchd quản lý tiến trình; trạng thái “running” không chứng minh
ứng dụng hoạt động đúng. Cài/gỡ plist, thay quyền hoặc thay tài khoản vẫn là việc được duyệt riêng.
[Nguồn Apple](https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CreatingLaunchdJobs.html).

Dự án đã có workflow triển khai trên GitHub có thể giữ nó làm đường thực thi ba thao tác:
trạm phải nhận định danh lượt, theo dõi đến kết quả cuối và truyền bản đích cố định.
Không tự thêm workflow khi push để vượt nút deploy/Estop; không bật huỷ lượt đang deploy để nhường bản mới.
Chỉ cấu hình loại đích thực tế của dự án đầu tiên, không xây hệ plugin chung.
GitHub có cơ chế environment/concurrency; áp dụng chúng là lựa chọn thiết kế, không tự bảo đảm rollback.
[Nguồn GitHub Actions](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/control-deployments).

Build và lệnh của mã dự án không được chạy bằng principal giữ Keychain của trạm.
Phần có quyền triển khai chỉ chuyển bản đã kiểm và điều khiển đúng đích được cấp.
Ba lệnh và toàn bộ mã/config/workflow chúng nạp phải thuộc vùng được Đại ca kiểm soát;
không suy “an toàn” chỉ vì tệp đầu vào không đổi. Quyền OS/GitHub giữ ranh giới này,
không thêm danh sách hash ghi tay; thiếu ranh giới thì dự án chưa được bật.

## Tích hợp ngoài — bốn câu §15

| Tích hợp | Hạn và bên áp | Đại ca thấy khi hỏng | Thử lại | Log |
| --- | --- | --- | --- | --- |
| GitHub đọc/merge | 60 giây mỗi lời gọi, trạm áp như adapter hiện có | Lý do chờ; lỗi liên lạc ba vòng liên tiếp thì dừng thử và báo | Đọc PR trước; còn mở thì xét lại toàn bộ, giữ đúng commit | Chỉ mã lỗi, repo/PR/commit; không stdout/stderr hay nội dung bead |
| Uq kiểm bản merge | Theo giới hạn lượt/lệnh và thu hồi của bộ quản lý hiện có; không tạo timeout thứ hai | “Bản gộp chưa kiểm đạt” hoặc “cổng kiểm đóng” | Theo cổng hiện có; không tự mở cổng lỗi | Dùng kết quả/log hiện có đã xử lý bí mật |
| Deploy / kiểm hoạt động / rollback | Trạm áp 15 / 2 / 15 phút (D100); kiểm sau rollback cũng 2 phút | Bản đang chạy, bản đích, đạt/hỏng/đã lùi/không rõ | Không tự lặp tác dụng phụ; không huỷ/restart trạm rồi chạy lại mù | Chỉ kết quả, mã, thời gian; đầu ra cục bộ qua lọc bí mật |
| launchd hoặc workflow sẵn có | Nằm trong hạn của thao tác deploy/rollback, không cộng thêm vô hạn | Đúng dịch vụ/lượt nào chưa xác minh; “không rõ” khi không chứng minh đã dừng | Đọc trạng thái; không gửi lượt mới để đoán | Không token, biến môi trường hay đầu ra thô |
| Telegram | Bộ báo tin hiện có áp timeout/retry | Dashboard vẫn có kết quả và trạng thái chờ gửi | Thử gửi lại thông báo; không chạy lại deploy | Mẫu tin ngắn, không nội dung lệnh/bead/bí mật |

Timeout lệnh gọi không chứng minh công việc phía dịch vụ/GitHub đã dừng.
Chỉ rollback khi biết lượt deploy đã kết thúc và không còn bên nào ghi cùng đích.
Mất điện, đứt mạng không đối soát được hoặc thu hồi không rõ → tạm dừng cả dự án, không đánh cược bằng rollback.

## Giới hạn và đường lui

Rollback chuyển mã/artifact về bản ổn định, không revert lịch sử Git, mở lại bead hay phục hồi DB.
Mã đã merge vẫn ở nhánh chính; sửa bằng PR mới. Dữ liệu do bản lỗi tạo ra không tự biến mất.
Bản có migration/phá dữ liệu hoặc không chạy được với dữ liệu hiện tại luôn chờ kịch bản riêng.
Uq đạt và GitHub cho merge không chứng minh tương thích dữ liệu production.

Đại ca tắt tự động là đường lui khỏi tính năng; một chuỗi deploy đã bắt đầu làm nốt phần kiểm/lùi an toàn.
Chưa có bằng chứng chạy thật của change này. Cổng repo nháp phải đo cả GitHub, quyền deploy,
khởi động lại giữa lượt và bản thực sự phục vụ; không suy từ validate hay test giả.
