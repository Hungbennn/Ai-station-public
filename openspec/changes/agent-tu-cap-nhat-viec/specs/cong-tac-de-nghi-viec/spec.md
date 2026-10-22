# Spec Delta — cong-tac-de-nghi-viec

## Purpose

Cho Đại ca bật, tắt việc agent tự cập nhật Beads theo từng dự án và theo từng loại đề nghị ngay trên dashboard, an toàn
như các thao tác ghi hiện có, và báo Đại ca đúng lúc mà không lộ nội dung nghiệp vụ (D85, D86, D105, D108, D110,
INV-005).

## ADDED Requirements

### Requirement: Một nút theo dự án, mặc định tắt, ba nút con
Mỗi dự án SHALL có một nút "agent tự cập nhật việc", mặc định tắt, và ba nút con: tiến độ, việc mới, bị chặn — bật
sẵn (D105). Một loại
đề nghị chỉ được ghi khi cả nút dự án lẫn nút con của loại đó đang bật; nếu không, trạm MUST nhận rồi bỏ đề nghị, ghi
nhật ký "tắt" (D85, D105).

#### Scenario: Dự án chưa từng chỉnh
- **WHEN** dự án mới được khai và chưa ai chỉnh
- **THEN** nút dự án tắt, ba nút con hiện bật; mọi đề nghị của agent trong dự án đó bị bỏ với lý do "tắt", Beads không đổi

#### Scenario: Chỉ tắt việc mới
- **GIVEN** nút dự án bật, nút tiến độ bật, nút việc mới tắt
- **WHEN** agent gửi một tiến độ và một đề nghị việc mới
- **THEN** tiến độ được ghi; đề nghị việc mới bị bỏ với lý do "tắt"

### Requirement: Kiểm nút lúc nhận và ngay trước khi ghi
Trạm SHALL kiểm nút lúc nhận đề nghị và kiểm lại ngay trước khi ghi Beads. Đề nghị đã bỏ vì nút tắt MUST NOT được ghi
bù khi Đại ca bật nút sau đó.

#### Scenario: Tắt nút khi việc mới đang chờ QC
- **GIVEN** `rn-12` có 2 đề nghị việc mới đang chờ QC
- **WHEN** Đại ca tắt nút việc mới, rồi QC đạt
- **THEN** trạm không tạo việc nào; hai đề nghị bị bỏ với lý do "tắt"

#### Scenario: Bật lại không ghi bù
- **GIVEN** một tiến độ đã bị bỏ lúc nút tiến độ tắt
- **WHEN** Đại ca bật nút tiến độ
- **THEN** tiến độ cũ đó không được ghi; chỉ tiến độ gửi sau lúc bật mới được ghi

### Requirement: Chỉnh trên dashboard qua cửa ghi có xác thực
Mọi thay đổi nút SHALL đi qua cửa ghi hiện có của dashboard: kênh ghi hợp lệ, danh tính Đại ca, header chống giả mạo,
gốc trang máy B; mỗi yêu cầu MUST mang mã thao tác để gửi lại không tạo trùng, và phiên bản đang xem để từ chối màn
hình cũ (D85).

#### Scenario: Thiếu danh tính
- **WHEN** một yêu cầu bật nút không mang danh tính Đại ca
- **THEN** máy chủ trả 403, nút không đổi

#### Scenario: Gửi lại cùng mã thao tác
- **WHEN** trình duyệt gửi lại đúng yêu cầu bật nút với cùng mã thao tác
- **THEN** máy chủ trả kết quả của lần đầu; lịch sử chỉ có một dòng

#### Scenario: Màn hình cũ
- **GIVEN** Đại ca mở cài đặt ở hai tab, tab kia vừa tắt nút việc mới
- **WHEN** tab này lưu với phiên bản cũ
- **THEN** máy chủ trả 409; dashboard báo "Cài đặt đã đổi — tải lại"

### Requirement: Bật nút dự án cần xác nhận
Bật nút dự án SHALL cần Đại ca xác nhận thêm một lần trên dashboard trước khi gửi. Tắt nút dự án và đổi nút con MUST
làm được bằng một lần bấm (D108).

#### Scenario: Bật nút dự án
- **WHEN** Đại ca gạt nút "agent tự cập nhật việc" của `repo-nhap` sang bật
- **THEN** dashboard hỏi lại "Agent sẽ được ghi vào Beads của dự án này qua trạm. Bật?" và chỉ gửi khi Đại ca đồng ý

### Requirement: Cửa ghi còn tạm thì không bật được
Khi cửa ghi của dashboard còn là kênh `header` tạm, máy chủ SHALL từ chối mọi yêu cầu bật hay chỉnh nút, và dashboard
MUST khoá các nút kèm giải thích, cho tới khi cửa ghi chuyển `unix-socket`. Tắt nút dự án vẫn làm được (D87, D110).

#### Scenario: Kênh header
- **GIVEN** `cach_ly.kenh_ghi = header`
- **WHEN** Đại ca thử bật nút của `repo-nhap`
- **THEN** máy chủ từ chối, nút không đổi; dashboard khoá nút kèm chữ "Cửa ghi còn tạm — chỉ bật được sau khi chuyển unix-socket"

### Requirement: Lưu bền, có lịch sử
Trạm SHALL lưu bền trạng thái nút của từng dự án; khởi động lại MUST giữ nguyên. Mỗi lần đổi MUST ghi ai đổi, lúc nào,
giá trị trước và sau.

#### Scenario: Khởi động lại trạm
- **GIVEN** Đại ca bật nút dự án `repo-nhap` và nút tiến độ
- **WHEN** trạm khởi động lại
- **THEN** hai nút vẫn bật; lịch sử có dòng "Đại ca (dashboard)", giờ, giá trị trước và sau

### Requirement: Dự án khoá ghi không bật được
Dự án `bat_ghi: false` SHALL không bật được nút dự án (máy chủ trả 422); trạm MUST NOT ghi đề nghị của dự án đó dù cài
đặt cũ đang bật (INV-005). Tắt nút vẫn làm được.

#### Scenario: Dự án chỉ quét thử
- **GIVEN** `hr-codex` có `bat_ghi: false`
- **WHEN** Đại ca thử bật nút agent tự cập nhật việc
- **THEN** máy chủ trả 422; dashboard hiện chip "chỉ quét thử" và nút bị khoá

### Requirement: Nằm chung màn cài đặt tự động của dự án
Các nút SHALL hiện trên cùng trang cài đặt theo dự án với tự merge/tự deploy, theo mockup Đại ca duyệt. Người không
mang danh tính Đại ca MUST chỉ xem được (D85).

#### Scenario: Xem khi không phải Đại ca
- **WHEN** trang mở từ máy trong tailnet không mang danh tính Đại ca
- **THEN** nút dự án và ba nút con hiện đúng trạng thái nhưng bị khoá; thẻ người dùng ghi "Chỉ đọc"

### Requirement: Telegram khi agent bị chặn
Khi agent báo bị chặn, Đại ca SHALL nhận đúng một tin Telegram cho lượt đó — chính tin escalation hiện có, không thêm
tin thứ hai. Tin MUST chỉ có tên dự án, mã việc, loại tin và link dashboard, không có lý do của agent (D86).

#### Scenario: Báo bị chặn
- **WHEN** agent của `rn-12` báo bị chặn
- **THEN** Đại ca nhận một tin dạng "[tram] repo-nhap · 1 escalation bí (rn-30) → link" (`rn-30` là mã escalation chặn `rn-12`); không có tin thứ hai cho cùng lần báo; tin không chứa chữ của agent

### Requirement: Telegram gộp khi có việc mới
Khi trạm ghi xong việc mới do agent tạo, Đại ca SHALL nhận một tin gộp cho cả đợt ghi đó (các lượt trong cùng bằng
chứng vào cột 3), không quá một tin mỗi lượt. Tin MUST chỉ có tên dự án, số việc mới, mã việc mới và link (D86).

#### Scenario: Ba việc mới
- **WHEN** `rn-12` vào cột 3 và trạm tạo 3 việc mới từ lượt code 1 và lượt QC 2
- **THEN** Đại ca nhận một tin "[tram] repo-nhap · 3 việc mới do agent tạo (rn-20, rn-21, rn-22) → link"; tin không chứa tiêu đề hay mô tả

### Requirement: Tiến độ chỉ hiện trên dashboard
Tiến độ đã ghi SHALL hiện trên dashboard ở việc tương ứng (mới nhất trước, kèm khe, lượt, giờ) và MUST NOT gửi
Telegram (D86).

#### Scenario: Agent ghi năm dòng tiến độ
- **WHEN** agent của `rn-12` ghi 5 dòng tiến độ trong một lượt
- **THEN** dashboard hiện 5 dòng ở việc `rn-12`; Đại ca không nhận tin Telegram nào vì tiến độ
