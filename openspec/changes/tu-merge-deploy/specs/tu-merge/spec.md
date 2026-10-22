# Tự merge có điều kiện

## ADDED Requirements

### Requirement: Quyền tự merge riêng từng dự án
Trạm SHALL chỉ tự merge khi dự án đã được Đại ca bật tự merge qua cửa passkey hiện có,
`bat_ghi` bật, không Estop, không tạm dừng dự án/toàn trạm, không decision/escalation đang chặn
và cổng kiểm đang mở. Mặc định SHALL tắt. Trạm MUST đọc lại các điều kiện ngay trước yêu cầu merge.
Nhật ký SHALL ghi dự án, PR, commit, kết quả và lý do chờ bằng lời thường.

#### Scenario: Bật một dự án
- **GIVEN** A bật tự merge, B chưa bật; cả hai có PR đủ kiểm
- **WHEN** trạm xét merge
- **THEN** chỉ A được merge; B chờ Đại ca

#### Scenario: Quyền bị rút trước khi gửi
- **GIVEN** PR đủ điều kiện ở đầu vòng xét
- **WHEN** lần lượt bật Estop, tạm dừng, khoá ghi, đóng cổng kiểm hoặc mở decision chặn trước yêu cầu merge
- **THEN** trong từng trường hợp trạm không gửi yêu cầu merge, ghi lý do; không tự mở lại quyền

### Requirement: Bằng chứng hiện hành từ Uq và QC khác khe
PR code SHALL có QC đạt từ khe khác khe code, sau kiểm lại đạt do Uq + Seatbelt quản lý.
Bằng chứng MUST khớp bộ hiện có `(du_an, bead_id, giao_id, luot, commit_code, commit_ban_giao,
digest_tieu_chi)` và ref công bố. Kết quả MUST là lượt hiện hành hoàn tất thu hồi theo bộ quản lý kiểm.
Trạm MUST NOT chấp nhận lời agent, kết quả kiểm chạy ngoài bộ quản lý, lần đạt cũ trước lần lỗi
hay dấu xác nhận G4 thay cho bằng chứng của PR. Không có nút bỏ QC/kiểm lại.

#### Scenario: Đủ bằng chứng tại đúng bản
- **GIVEN** Uq trả đạt cho lượt code L tại H, thu hồi xong; khe QC khác đạt sau đó; ref và tiêu chí giữ nguyên
- **WHEN** PR code trỏ H và các điều kiện còn lại đủ
- **THEN** PR đủ điều kiện bằng chứng để trạm đề nghị merge

#### Scenario: Bằng chứng không còn hiệu lực
- **GIVEN** lần cũ đạt tại H
- **WHEN** lần lượt có lượt code mới chưa kiểm, lần kiểm mới lỗi, tiêu chí đổi, ref đổi hoặc QC cùng khe code
- **THEN** mỗi trường hợp đều chặn merge; cùng SHA không cứu được bằng chứng sai lượt

#### Scenario: Kiểm bị gián đoạn
- **WHEN** client mất kết nối Uq, lệnh kiểm thoát 0 nhưng thu hồi chưa xác nhận, hoặc chỉ agent báo đạt
- **THEN** không công nhận kiểm đạt, không merge; áp cơ chế đóng cổng hiện có, chỉ Đại ca mở lại

### Requirement: Phạm vi việc được tự gộp
Trạm SHALL chỉ xét PR đã ghi nhận do chính trạm mở, đúng repo, nhánh công bố, nhánh đích cấu hình,
loại PR và bằng chứng; PR ngoài repo, draft, đóng chưa merge, sai đích hoặc xung đột MUST chờ.
Điều kiện cột AI tự làm và hàng rào SHALL giữ D70/D90–D92/D112/D120:
nút mặc định bật; hàng rào thường theo diff/cờ đỏ, hàng rào schema theo đường dẫn hoặc từ khoá.
Cấu trúc DB, xoá dữ liệu, đường dẫn cấm và mã điều khiển kiểm/deploy MUST luôn chờ Đại ca, không nút bỏ.
Spike thiếu QC MUST NOT tự merge. Agent MUST NOT tự giải quyết xung đột hay sửa luật GitHub để mở cổng.

#### Scenario: PR đúng tên nhưng khác nguồn
- **WHEN** một PR dùng tên nhánh giống trạm nhưng thiếu sự kiện mở tương ứng, sai repo/đích hoặc là draft
- **THEN** không merge dù CI xanh

#### Scenario: Tắt hàng rào vẫn chặn dữ liệu
- **GIVEN** nút hàng rào tắt
- **WHEN** diff chạm schema, nội dung việc khớp từ khoá xoá dữ liệu hoặc sửa script/workflow deploy được bảo vệ
- **THEN** không tự merge; nêu phần cần Đại ca xử lý

#### Scenario: Giữ hai nút hiện có
- **GIVEN** không có cấm cứng và đủ mọi điều kiện khác
- **WHEN** bead có `cot-khoa` hoặc cờ đỏ thường, lần lượt thử với nút tương ứng bật và tắt
- **THEN** bật thì chờ, tắt thì bỏ riêng điều kiện đó; QC, Uq và luật GitHub vẫn bắt buộc

### Requirement: GitHub cưỡng chế điều kiện gộp
**[Phụ thuộc QĐ1, mặc định A]** Nhánh đích SHALL có luật GitHub bắt buộc các check được dự án chọn
từ nguồn tin cậy và cập nhật theo nhánh chính. Tài khoản trạm MUST không có quyền bypass.
Thiếu luật, không đọc/xác nhận được luật, không có check bắt buộc hoặc repo không hỗ trợ MUST chặn tự merge.
Trạm SHALL dùng kết luận cho phép gộp của GitHub thay bảng tự phân loại mọi job; trạng thái chưa rõ MUST chờ.
Không có nút bỏ CI. Agent MUST NOT sửa workflow/check nguồn để tự cấp kết quả.

#### Scenario: Check bắt buộc chưa đạt
- **WHEN** check bắt buộc thiếu, lỗi, đang chạy hoặc GitHub báo chưa gộp được
- **THEN** không merge; job tuỳ chọn xanh không bù được check bắt buộc

#### Scenario: Job tuỳ chọn lỗi
- **GIVEN** mọi check bắt buộc được GitHub chấp nhận, nhánh cập nhật, các điều kiện trạm đủ
- **WHEN** một job không bắt buộc lỗi
- **THEN** trạm không tự biến job đó thành điều kiện mới; GitHub cho phép thì được gửi merge

#### Scenario: Nhánh chính đổi hoặc mất bảo vệ
- **WHEN** PR chưa cập nhật theo nhánh chính mới, luật bảo vệ bị gỡ hoặc tài khoản trạm có bypass
- **THEN** chặn tự merge; cập nhật PR làm đổi commit thì phải lấy lại bằng chứng Uq/QC tương ứng

### Requirement: Merge đúng đầu PR và đối soát trước khi đóng việc
Trạm SHALL yêu cầu merge commit thường, ràng buộc đúng đầu PR đã kiểm.
Trạm MUST NOT dùng quyền quản trị bỏ chặn, squash, rebase, xoá nhánh, tự merge chờ sẵn hay merge queue.
Mỗi thao tác SHALL có định danh ổn định, ghi trước khi gửi; lỗi/quá hạn/mất phản hồi MUST đọc PR để đối soát.
Chỉ khi xác minh đúng PR, commit đã kiểm và merge commit thuộc nhánh đích SHALL đóng bead bằng luồng hiện có.
Không xác minh được MUST giữ việc chờ; lệnh trả thành công một mình không đủ.

#### Scenario: Đầu PR đổi sát lúc merge
- **GIVEN** trạm xét H1
- **WHEN** PR chuyển H2 trước khi GitHub xử lý yêu cầu
- **THEN** GitHub từ chối yêu cầu ràng buộc H1; trạm không tự gửi lại cho H2

#### Scenario: GitHub đã merge nhưng phản hồi mất
- **WHEN** trạm chạy lại và thấy thao tác chưa có kết quả
- **THEN** đọc PR; đã merge đúng thì xác minh và ghi kết quả một lần, không merge/đóng bead trùng;
  còn mở thì chỉ thử lại cùng commit sau khi xét lại đủ điều kiện; đọc không được thì chờ

### Requirement: Giữ các điểm dừng ngoài quyền đã cấp
Feature SHALL vẫn chờ Đại ca duyệt spec tại đúng commit (#1); bí/bất đồng SHALL vẫn hỏi (#3).
PR spec được Đại ca duyệt SHALL giữ ngoại lệ D95: không đòi QC/kiểm code nhưng phải chỉ chứa phạm vi
tài liệu spec hợp lệ, đúng commit duyệt, các khoá chung và luật GitHub theo QĐ1 vẫn đủ.
Con feature SHALL chỉ được giao sau khi spec merge được xác minh. Feature cha MUST NOT tự đóng.
Merge tự động MUST NOT cấp quyền migrate, xoá dữ liệu, sửa hệ thống hay gửi khách (#4).

#### Scenario: Duyệt spec không duyệt commit mới
- **GIVEN** Đại ca duyệt S1
- **WHEN** PR spec vẫn S1 và đủ các khoá thì gộp; nếu đổi S2 hoặc lẫn mã chạy thì xét lại
- **THEN** chỉ trường hợp S1 tài liệu hợp lệ được tự gộp; còn lại chờ Đại ca, không giao việc con

#### Scenario: Trả lời câu hỏi không cấp quyền deploy
- **WHEN** Đại ca trả lời escalation nhưng chưa bật tự deploy cho dự án
- **THEN** trạm không suy câu trả lời thành quyền deploy hay thao tác nguy hiểm
