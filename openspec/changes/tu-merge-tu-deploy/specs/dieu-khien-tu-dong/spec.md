# Spec Delta — dieu-khien-tu-dong

## Purpose

Cho Đại ca bật, tắt, chỉnh và tạm dừng tự merge, tự deploy của từng dự án và của cả trạm ngay trên dashboard, an
toàn như các thao tác ghi hiện có, và bảo đảm estop luôn dừng được cả hai (D77–D79, D87, D88, D97, D99, D101,
INV-004, INV-005).

## ADDED Requirements

### Requirement: Cài đặt theo dự án lưu bền, có lịch sử
Với mỗi dự án, trạm SHALL lưu bền: công tắc tự merge, hai nút điều kiện (cột, hàng rào) và CI bắt buộc, ba lệnh, nút tự
deploy, trạng thái TẠM DỪNG — trong sổ ghi sự kiện của trạm, không trong `du-an/*.yaml` (D88). Mỗi lần đổi MUST ghi
lại ai đổi, lúc nào, giá trị cũ và mới; trạm khởi động lại vẫn giữ nguyên giá trị.

#### Scenario: Giá trị mặc định
- **WHEN** dự án chưa từng được chỉnh
- **THEN** công tắc tự merge tắt, tự deploy tắt, hai nút điều kiện bật, CI bắt buộc không có nút tắt, ba lệnh trống, không tạm dừng

#### Scenario: Xem lịch sử đổi
- **WHEN** Đại ca bật công tắc tự merge lúc 09:12 rồi tắt lúc 21:40
- **THEN** lịch sử của dự án có hai dòng, mỗi dòng ghi "Đại ca (dashboard)", giờ, giá trị trước và sau

### Requirement: Chỉnh trên dashboard qua cửa ghi có xác thực
Mọi thay đổi cài đặt, nút Deploy và nút TẠM DỪNG SHALL đi qua cùng cửa ghi của dashboard hiện có: kênh ghi hợp lệ,
danh tính Đại ca, header chống giả mạo, gốc trang máy B. Mỗi yêu cầu MUST mang mã thao tác để gửi lại không tạo
trùng (D79).

#### Scenario: Thiếu danh tính
- **WHEN** một yêu cầu bật công tắc tự merge không mang danh tính Đại ca
- **THEN** máy chủ trả 403, cài đặt không đổi

#### Scenario: Gửi lại cùng mã thao tác
- **WHEN** trình duyệt gửi lại đúng yêu cầu bật công tắc với cùng mã thao tác
- **THEN** máy chủ trả kết quả của lần đầu, lịch sử chỉ có một dòng

#### Scenario: Màn hình cũ
- **GIVEN** Đại ca mở trang ở hai tab, tab kia vừa đổi lệnh deploy
- **WHEN** tab này lưu lệnh deploy với phiên bản cũ
- **THEN** máy chủ trả 409; dashboard báo "Cài đặt đã đổi — tải lại", giữ nội dung ô nhập

### Requirement: Cửa người theo passkey hiện hành
Bật/sửa cài đặt, Deploy tay và Tiếp tục SHALL dùng cửa passkey theo change `xac-thuc-passkey`.
Bật tự deploy và sửa ba lệnh MUST có xác nhận mới mức R (D140). TẠM DỪNG giữ cửa an toàn hiện có.
Header localhost hoặc kênh unix-socket một mình MUST NOT thay phiên passkey hợp lệ.

#### Scenario: Chưa có phiên passkey
- **WHEN** yêu cầu bật/sửa/Deploy/Tiếp tục chỉ có header danh tính, không có phiên passkey
- **THEN** từ chối 403; không đổi trạng thái

#### Scenario: Tạm dừng vẫn được
- **WHEN** Đại ca gửi yêu cầu TẠM DỪNG hợp lệ theo cửa an toàn hiện có
- **THEN** nhận và tạm dừng, không cần xác nhận mới để giảm quyền

### Requirement: Báo Telegram mỗi lần cài đặt đổi
Mỗi lần cài đặt tự động của một dự án hay trạng thái TẠM DỪNG đổi, trạm SHALL gửi một tin Telegram gồm tên dự án,
loại thay đổi và link dashboard (D99). Tin MUST NOT chứa nội dung lệnh.

#### Scenario: Bật tự deploy
- **WHEN** Đại ca bật tự deploy của `repo-nhap`
- **THEN** Telegram nhận tin "repo-nhap · cài đặt tự động vừa đổi: tự deploy bật"

#### Scenario: Trạm tự tắt
- **WHEN** trạm tự tắt tự deploy sau 3 lần hỏng
- **THEN** Telegram nhận tin cài đặt đổi kèm tác nhân "trạm"

### Requirement: Lệnh deploy không được chứa bí mật
Lệnh trống được lưu khi chưa bật deploy; thiếu một lệnh MUST chặn cả Deploy tay lẫn tự động.
Khi lưu ba lệnh, máy chủ SHALL từ chối (422) lệnh không tách được thành các đối số, hoặc lệnh mà bộ quét
bí mật của trạm nhận ra có mật khẩu hay token (INV-001, D97). Lệnh bị từ chối MUST NOT được lưu hay ghi vào lịch sử.

#### Scenario: Dán token vào lệnh kiểm còn sống
- **WHEN** Đại ca lưu lệnh kiểm còn sống có chuỗi giống token API
- **THEN** máy chủ trả 422 "Lệnh có vẻ chứa bí mật — để bí mật ngoài lệnh"; dashboard giữ ô nhập để sửa

### Requirement: Bật công tắc cần xác nhận
Bật công tắc tự merge, bật tự deploy, và lưu ba lệnh SHALL cần Đại ca xác nhận thêm một lần trên dashboard trước
khi gửi. Tắt công tắc và TẠM DỪNG MUST làm được bằng một lần bấm và xác nhận như nút estop hiện có.

#### Scenario: Bật tự deploy
- **WHEN** Đại ca gạt nút tự deploy sang bật
- **THEN** dashboard hỏi lại "Trạm sẽ tự đưa bản mới lên cho khách dùng, không chờ Đại ca. Bật?" và chỉ gửi khi Đại ca đồng ý

### Requirement: Dự án khoá ghi không bật được tự động
Dự án có `bat_ghi: false` SHALL không bật được công tắc tự merge hay tự deploy (máy chủ trả 422), và trạm MUST NOT
tự merge hay tự deploy dự án đó dù cài đặt cũ đang bật (INV-005). TẠM DỪNG vẫn bấm được.

#### Scenario: Dự án chỉ quét thử
- **GIVEN** `hr-codex` có `bat_ghi: false`
- **WHEN** Đại ca thử bật công tắc tự merge
- **THEN** máy chủ trả 422; dashboard hiện chip "chỉ quét thử" và công tắc bị khoá

### Requirement: TẠM DỪNG theo dự án
Nút TẠM DỪNG của một dự án SHALL ngừng mọi tự merge và tự deploy mới của dự án đó ngay vòng tick kế, không đổi các
cài đặt khác. Bấm "Tiếp tục" SHALL trả về đúng hành vi theo cài đặt cũ khi không còn deploy chưa đối soát. Lệnh tạm dừng MUST không bị từ chối vì màn
hình cũ (D78). Nút Deploy của Đại ca vẫn dùng được khi dự án tạm dừng (D97).

#### Scenario: Tạm dừng rồi tiếp tục
- **GIVEN** `repo-nhap` bật tự merge và tự deploy, không còn kết quả deploy chưa rõ
- **WHEN** Đại ca bấm TẠM DỪNG dự án, rồi một giờ sau bấm Tiếp tục
- **THEN** trong giờ đó không có tự merge hay tự deploy nào của `repo-nhap`; sau Tiếp tục cả hai chạy lại, công tắc vẫn như cũ

#### Scenario: Deploy tay khi dự án tạm dừng
- **WHEN** dự án đang tạm dừng thông thường, không còn kết quả deploy chưa rõ, các cổng khác đạt và Đại ca bấm Deploy
- **THEN** trạm chạy chuỗi deploy theo lệnh của Đại ca

#### Scenario: Tiếp tục khi deploy chưa rõ
- **GIVEN** chuỗi trước chưa xác minh bản đang phục vụ hoặc còn tác vụ ghi đích
- **WHEN** Đại ca bấm Tiếp tục thông thường
- **THEN** không mở lại tự merge/deploy; cần đối soát chỉ đọc và xác nhận bản thực tế qua passkey theo spec `tu-deploy`

### Requirement: TẠM DỪNG toàn trạm
Nút TẠM DỪNG toàn trạm SHALL ngừng mọi tự merge và tự deploy mới của mọi dự án. Nút màu vàng nằm trên thanh trên
cạnh Estop nên có trên mọi trang, kèm băng cảnh báo khi bật. Phần còn lại của trạm MUST chạy bình thường (D78, D101).

#### Scenario: Toàn trạm tạm dừng
- **WHEN** Đại ca bấm TẠM DỪNG toàn trạm
- **THEN** mọi trang hiện băng "Tự merge · tự deploy đang tạm dừng toàn trạm"; trạm vẫn mở PR, nhưng không merge, không deploy tự động

### Requirement: Đang làm dở thì làm nốt an toàn
Khi TẠM DỪNG (dự án hoặc toàn trạm) hay estop bật giữa một chuỗi deploy, trạm SHALL làm nốt chuỗi đang chạy (deploy
→ kiểm còn sống → lùi nếu hỏng) và MUST NOT bắt đầu thao tác tự động mới. Trạm MUST NOT cắt ngang lệnh deploy hay lùi.

#### Scenario: Bấm tạm dừng khi đang deploy
- **WHEN** Đại ca bấm TẠM DỪNG lúc lệnh deploy đang chạy
- **THEN** lệnh deploy chạy xong, kiểm còn sống chạy, hỏng thì lùi; sau đó không có thao tác tự động mới

### Requirement: Estop dừng cả tự merge và tự deploy
Khi estop bật, trạm SHALL không tự merge, không tự deploy, và máy chủ MUST từ chối cả nút Deploy của Đại ca (INV-004,
D97).
Tắt estop thì hành vi trở lại theo cài đặt và trạng thái TẠM DỪNG; không xoá chốt deploy chưa đối soát.

#### Scenario: Estop bật
- **WHEN** estop bật và một PR đủ điều kiện tự merge
- **THEN** trạm không merge; nút Deploy trên dashboard bị khoá kèm chữ "Estop đang bật"

### Requirement: Không giới hạn số lần hay khung giờ
Trạm SHALL không áp giới hạn số lần hay khung giờ cho tự merge và tự deploy (D77).

#### Scenario: Ban đêm
- **WHEN** lúc 03:00 có PR đủ điều kiện và tự deploy bật
- **THEN** trạm merge và deploy ngay, không chờ sáng

### Requirement: Trang tự merge/deploy của dự án
Dashboard SHALL có một trang cho mỗi dự án, đi tới được từ trang Dự án, hiện: công tắc và nút, ba điều kiện "luôn
bật" không bấm được, dòng "cấu trúc DB, xoá dữ liệu — luôn chờ Đại ca", ba lệnh, hàng "sẵn sàng deploy", việc chờ
Đại ca kèm lý do, lịch sử gần đây, bộ đếm hỏng liên tiếp. Người không phải Đại ca MUST chỉ xem được.

#### Scenario: Xem khi không phải Đại ca
- **WHEN** trang mở từ máy trong tailnet không mang danh tính Đại ca
- **THEN** mọi nút và ô sửa bị khoá, thẻ người dùng ghi "Chỉ đọc"; dữ liệu vẫn hiện
