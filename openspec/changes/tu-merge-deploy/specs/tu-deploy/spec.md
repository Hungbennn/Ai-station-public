# Tự deploy và quay lại theo dự án

## ADDED Requirements

### Requirement: Mỗi dự án có đích và đường deploy được cấp riêng
Trạm SHALL giữ công tắc tự deploy riêng, mặc định tắt, một môi trường mỗi dự án và ba thao tác đã duyệt:
deploy, kiểm hoạt động, rollback. Thiếu đích hoặc một thao tác MUST từ chối deploy cả tay lẫn tự động.
Cài đặt SHALL lưu bằng sự kiện theo D88; bật tự deploy/sửa lệnh SHALL qua xác nhận passkey mới theo D140.
**[QĐ3, mặc định A]** Ba thao tác MUST dùng đường deploy hiện có với quyền chỉ của dự án đích.
Mã/build của dự án MUST NOT chạy dưới tài khoản giữ bí mật trạm; agent MUST NOT sửa mã/config mà đường này nạp.
Trạm MUST NOT tự cài dịch vụ, tạo user hoặc lấy thêm quyền để đáp ứng điều kiện.

#### Scenario: Chưa khai đủ đường deploy
- **WHEN** dự án thiếu lệnh rollback, chưa có đích hoặc chưa có quyền deploy riêng
- **THEN** không bật được tự deploy và không chạy Deploy tay; dashboard nêu phần còn thiếu

#### Scenario: Hai dự án dùng chung máy
- **GIVEN** A và B có các đích launchd riêng đã cài
- **WHEN** A deploy hoặc rollback lỗi
- **THEN** chỉ đụng đúng bản và dịch vụ của A; không khởi động lại, đổi bản hoặc tạm dừng B

#### Scenario: Sửa gián tiếp đường deploy
- **WHEN** agent sửa tệp được script deploy nạp, workflow hoặc cấu hình chọn dịch vụ
- **THEN** quyền ghi/vùng bảo vệ chặn hoặc việc chờ Đại ca; không chạy mã mới đó bằng quyền triển khai

### Requirement: Bản phát hành phải cố định và đã kiểm
**[QĐ2, mặc định A]** Trạm SHALL chọn commit merge M đã xác minh trên nhánh đích;
Uq SHALL kiểm lại chính M theo tiêu chí/lệnh hiện hành trước khi deploy.
QC trên đầu PR H không được trình bày thành QC trên M; kết quả Uq của H MUST NOT thay kiểm M.
Bản chạy/artifact SHALL truy về đúng M, build ở môi trường cách ly; deploy MUST NOT kéo HEAD mới hay build
bằng tài khoản giữ bí mật. Nếu M chứa thay đổi ngoài các PR đủ bằng chứng đã xác minh kể từ bản ổn định,
trạm MUST chờ Đại ca xác nhận phạm vi bản đó cùng kiểm Uq tại M; không tự lấy đầu nhánh bỏ qua phần chưa kiểm.

#### Scenario: Bản gộp hỏng dù PR xanh
- **GIVEN** H có QC và kiểm đạt, GitHub merge ra M
- **WHEN** kiểm Uq trên M lỗi
- **THEN** không deploy M, giữ bản đang chạy; việc đã merge không bị ghi sai thành chưa merge

#### Scenario: Code đẩy thẳng chen vào
- **GIVEN** đã chọn M
- **WHEN** nhánh chính lên N do một lần đẩy thẳng
- **THEN** không thay M bằng N; N chờ xác nhận phạm vi và kiểm trên N, không tự deploy theo HEAD

#### Scenario: Artifact không khớp
- **WHEN** bản đưa lên không chứng minh được thuộc M hoặc build/kiểm chưa xong
- **THEN** không chuyển bản đang phục vụ; ghi “chưa có bản đã kiểm”

### Requirement: Chọn thời điểm mà không deploy trùng
Sau merge đã xác minh, tự deploy tắt hoặc merge tay SHALL chỉ tạo một hàng “sẵn sàng deploy”.
Tự deploy bật SHALL chỉ khởi động cho sự kiện tự merge mới sau khi bật (D123);
bật nút không tự chạy các bản đã chờ. Bản từ merge tay SHALL chờ Deploy tay (D96).
Mỗi dự án SHALL có tối đa một chuỗi deploy/kiểm/rollback; nhiều bản chờ được gộp tới bản đủ kiểm mới nhất.
Mỗi chuỗi MUST cố định bản đích, bản trước và phiên bản cài đặt từ lúc bắt đầu.
Yêu cầu tay SHALL mang commit đang thấy và mã thao tác; bản/cài đặt đổi MUST trả 409.

#### Scenario: Ba bản dồn và một bản đang chạy
- **GIVEN** A đang deploy M1; M2 và M3 lần lượt đủ điều kiện trong lúc đó
- **WHEN** chuỗi M1 kết thúc an toàn
- **THEN** không ngắt M1; tối đa một lượt mới chọn M3, không chạy thêm M2; nếu dự án đã dừng thì cả hai chờ

#### Scenario: Bật nút hoặc gửi lại yêu cầu cũ
- **GIVEN** M đã sẵn sàng trước khi bật; hoặc yêu cầu Deploy tay cho M đã được nhận
- **WHEN** bật tự deploy hoặc gửi lại cùng mã/nội dung
- **THEN** trường hợp đầu M vẫn chờ bấm; trường hợp sau trả trạng thái cũ, không sinh chuỗi thứ hai

### Requirement: Khoá chung và dừng giữa chuỗi
Ngay trước bắt đầu, deploy SHALL kiểm `bat_ghi`, Estop, cổng kiểm, quyền và bản đã kiểm.
Tự deploy SHALL còn kiểm nút bật và tạm dừng dự án/toàn trạm.
Deploy tay SHALL dùng cửa passkey, được vượt tạm dừng thông thường nhưng không vượt Estop,
khoá ghi, cổng kiểm đóng hoặc chuỗi chưa rõ kết quả chưa đối soát.
Tắt nút/tạm dừng/Estop giữa chuỗi SHALL chặn lượt mới; chuỗi đang chạy làm nốt kiểm/rollback an toàn
với bản và cài đặt đã cố định (D97). Không phát động lần deploy mới nhân danh rollback.

#### Scenario: Dừng khi đang deploy
- **WHEN** Estop bật trong khi deploy M đang chạy
- **THEN** chuỗi M kiểm hoạt động, rollback nếu cần và còn đủ chứng cứ an toàn; không bắt đầu bản tiếp;
  Deploy tay mới bị từ chối

#### Scenario: Tạm dừng không xoá trạng thái chưa rõ
- **GIVEN** lần trước chưa xác định được đã chuyển bản hay chưa
- **WHEN** Đại ca bấm Deploy tay hoặc Tiếp tục thông thường
- **THEN** chưa chạy lượt mới; phải xác minh bản thực tế và lượt cũ đã kết thúc trước

### Requirement: Bản quay lại phải sẵn trước khi bắt đầu
**[QĐ4, mặc định A]** Trước deploy, trạm SHALL biết bản ổn định L đang phục vụ,
giữ đủ artifact/config tương thích và đường rollback đã thử tại đích này.
Thiếu L, không đọc được bản thực tế hoặc L không tương thích dữ liệu hiện tại MUST chặn trước tác dụng phụ.
Lần đầu SHALL cần Đại ca thiết lập/xác nhận bản nền và thử đường lui theo cổng riêng.
Rollback MUST chỉ đổi mã/artifact và cấu hình thuộc lần triển khai; không phục hồi DB, xoá dữ liệu,
reset/force-push Git hoặc tự mở lại bead. Migration hay thay đổi dữ liệu không đảo được SHALL chờ kịch bản riêng.

#### Scenario: Deploy đầu chưa có bản nền
- **WHEN** dự án chưa xác định bản ổn định và chưa thử quay lại
- **THEN** không bắt đầu deploy tự động; thông báo “cần bản quay lại đã kiểm”

#### Scenario: Bản cũ không chạy được với dữ liệu mới
- **WHEN** bản đích cần migration hoặc bản quay lại không tương thích dữ liệu hiện tại
- **THEN** dừng trước deploy, chờ Đại ca; không coi sao lưu DB là giấy phép tự khôi phục

### Requirement: Chỉ thành công khi đúng bản hoạt động
Sau deploy thoát thành công, trạm SHALL kiểm ứng dụng trong hạn 2 phút, xác nhận đúng bản đích
và phép thử chức năng cốt lõi đã khai. Chỉ lúc đó SHALL ghi thành công và đổi bản ổn định từ L sang M.
Một PID còn sống, launchd “running”, HTTP 200 chung hoặc lời gọi workflow được nhận MUST NOT đủ.
Trước lần đạt này, L SHALL vẫn là bản quay lại.

#### Scenario: Dịch vụ sống nhưng vẫn là bản cũ
- **WHEN** launchd báo running hoặc HTTP 200 nhưng định danh bản vẫn L thay vì M
- **THEN** deploy không đạt, chuyển nhánh xử lý lỗi, không ghi M là bản ổn định

#### Scenario: Kiểm đủ bản và chức năng
- **WHEN** xác minh M đang phục vụ và phép thử cốt lõi đạt trong hạn
- **THEN** ghi deploy thành công một lần, M thành bản ổn định cho lượt sau, bộ đếm hỏng về 0

### Requirement: Lỗi đã rõ thì quay lại một lần
Deploy lỗi hoặc quá hạn đã xác nhận thu hồi, hay kiểm hoạt động lỗi SHALL kích hoạt đúng một rollback về L.
Trước rollback MUST biết deploy đã chấm dứt, không còn tác vụ khác ghi đích.
Sau rollback SHALL kiểm lại đúng L và chức năng trong 2 phút; chỉ đạt mới ghi “đã lùi”.
Lệnh rollback SHALL dùng đường tin cậy đã cố định, không lấy script từ bản M vừa hỏng.
Bản M SHALL vẫn ở hàng sẵn sàng nhưng MUST NOT tự thử lại (D124).

#### Scenario: Deploy lỗi một phần nhưng đã dừng
- **GIVEN** đích đã đổi một phần sang M, tác vụ deploy đã kết thúc
- **WHEN** rollback về L và kiểm L đạt
- **THEN** báo “deploy hỏng, đã tự lùi”, giữ L ổn định, tăng đếm hỏng một lần; không sửa lịch sử Git

#### Scenario: Rollback lỗi
- **WHEN** rollback lỗi, quá hạn, không xác định được bản hoặc kiểm L thất bại
- **THEN** tắt tự deploy, tạm dừng cả tự merge và tự deploy của dự án, báo khẩn;
  không rollback đệ quy, không tuyên bố đã phục hồi

### Requirement: Kết quả không rõ thì đối soát, không lặp lệnh
Trạm SHALL ghi bắt đầu trước tác dụng phụ, giữ định danh chuỗi/lượt thực thi trong sự kiện.
Mất điện, khởi động lại, mất phản hồi hoặc timeout mà chưa xác nhận dừng SHALL thành “không rõ kết quả”;
trạm MUST tạm dừng cả dự án, không tự chạy lại deploy/rollback.
Đọc trạng thái đích/lượt SHALL được phép để đối soát; chỉ Đại ca xác nhận kết quả thực tế và cho tiếp tục.
Không rõ SHALL không tính vào ba lần hỏng (D115/D126).

#### Scenario: Mất điện sau chuyển bản
- **GIVEN** đã ghi bắt đầu, chưa ghi kết quả cuối
- **WHEN** trạm khởi động lại dù launchd tự bật ứng dụng
- **THEN** hiện bản dự kiến và “không rõ”; không tự gửi deploy/rollback; bản ổn định chưa bị ghi đè

#### Scenario: Lệnh gọi hết hạn nhưng công việc từ xa còn chạy
- **WHEN** lời gọi workflow hết hạn, chưa xác nhận lượt deploy phía GitHub đã kết thúc
- **THEN** dừng dự án và báo không rõ, không chạy rollback chồng với công việc đó

### Requirement: Giữ thời hạn, ngưỡng hỏng và báo tin hiện có
Deploy/rollback SHALL có hạn 15 phút mỗi thao tác; kiểm hoạt động 2 phút, do trạm áp (D100).
Thu hồi không xác nhận được MUST đi nhánh không rõ.
Ba lần deploy hỏng đã rõ liên tiếp SHALL tắt tự deploy; đạt hoặc Đại ca bật lại SHALL đặt đếm về 0 (D75).
Một lần hỏng đã lùi thành công SHALL không tự tắt công tắc và không tự thử lại cùng bản.
Dashboard SHALL phân biệt “đã merge”, “sẵn sàng”, “đang deploy”, “đạt”, “đã lùi”, “lùi hỏng”, “không rõ”,
kèm dự án, bản trước/đích, thời điểm, lý do và mã lượt; không thêm màn mới.
Merge, deploy, rollback và đổi cài đặt SHALL báo qua nguồn sự kiện hiện có, chống thông báo trùng.
Tin lỗi/đổi cài đặt SHALL gửi ngay; tin tốt theo giờ yên lặng. Telegram lỗi MUST NOT làm lặp thao tác.
Bí mật, đầu ra thô và nội dung bead MUST NOT vào dashboard/Telegram; log cục bộ qua lọc hiện có.

#### Scenario: Hỏng lần thứ ba
- **GIVEN** dự án đã hỏng hai lần liên tiếp
- **WHEN** một bản mới deploy hỏng và lùi thành công
- **THEN** đếm thành 3, tắt tự deploy; merge sau chỉ tạo hàng sẵn sàng; dự án khác không đổi

#### Scenario: Báo tin hỏng hoặc lệnh in bí mật
- **WHEN** deploy thành công nhưng Telegram mất mạng, hoặc đầu ra có token giả trong phép thử
- **THEN** kết quả deploy vẫn giữ; chỉ tin được thử gửi lại; token không xuất hiện trong sự kiện,
  dashboard, Telegram hay log chưa lọc
