# Spec Delta — cua-ghi-passkey

## Purpose

Cửa ghi dành cho người trên dashboard: giữ Tailscale làm mạng riêng và danh tính, dùng passkey cho thao tác
nguy hiểm (D135–D150), chuẩn bị người/quyền (D136). Hành vi cập nhật theo các quyết định đã chốt;
các lựa chọn triển khai ở design và plan vẫn cần review, duyệt trước triển khai.

## ADDED Requirements

### Requirement: Người và quyền được kiểm phía máy chủ
Trạm SHALL có người dùng với ID ổn định, login Tailscale, vai và trạng thái; credential và phiên MUST thuộc một
người. Hiện SHALL chỉ có Đại ca vai `chu` (chủ), có các quyền dashboard theo hành vi được liệt kê trong design D-2/D-3
(D136). Agent MUST NOT được coi là người dùng. Danh sách/quyền không hợp lệ MUST đóng cửa ghi, không tự cấp quyền.

#### Scenario: Một chủ trạm
- **GIVEN** cấu hình có một người hoạt động là Đại ca, vai chủ
- **WHEN** đăng ký credential
- **THEN** credential gắn ID người này; không tạo người mới từ tên thiết bị hoặc header gửi lên

#### Scenario: Đúng chữ ký nhưng không đủ quyền
- **GIVEN** fixture có người không hoạt động hoặc không có quyền thao tác đích
- **WHEN** gửi chữ ký hợp lệ hoặc cookie còn hạn để bật tự merge
- **THEN** trả 403 trước mọi tác dụng phụ; quyền không được suy từ chữ trong bead hay payload

### Requirement: Login Tailscale phải khớp người sở hữu passkey
Mọi đăng ký, xác nhận, dùng phiên và quản lý passkey SHALL yêu cầu đúng một login Tailscale hợp lệ; login MUST
khớp người sở hữu credential, phiên và mã đăng ký (D143). Trạm MUST giữ kiểm Host, Origin chính xác máy B,
`X-Tram: 1` và chống CSRF cho tuyến ghi trình duyệt. Header đúng một mình MUST NOT mở P/R.

#### Scenario: Passkey của người A dùng với login khác
- **GIVEN** credential và phiên thuộc login A
- **WHEN** yêu cầu mang login B dù chữ ký đúng
- **THEN** trả 403, không mở phiên hay ghi nghiệp vụ

#### Scenario: Thiếu hoặc giả danh tính
- **GIVEN** không có phiên hay assertion hợp lệ
- **WHEN** gọi thao tác nguy hiểm với header thiếu, header trùng, hoặc giả đúng login từ localhost
- **THEN** trả 403, không ghi; giả Origin và X-Tram cũng không đủ

#### Scenario: Sai nguồn trang
- **GIVEN** cookie và login hợp lệ
- **WHEN** yêu cầu ghi thiếu X-Tram hoặc Origin không khớp HTTPS máy B
- **THEN** trả 403; Host lạ bị từ chối ở cửa Host trước khi ghi

### Requirement: Phân loại mọi thao tác nguy hiểm theo D138
Trạm SHALL áp mức P cho bốn nhóm: (1) công tắc tự động và Deploy, gồm bật/chỉnh tự merge, tự deploy, ba lệnh,
Tiếp tục sau tạm dừng, Deploy tay, agent tự cập nhật việc; (2) Duyệt spec, chốt/đóng việc, trả lời decision;
(3) bật lại khe/máy thợ, ghép máy mới, xoá ký ức, Tiếp tục sau Estop; (4) thêm/thu hồi passkey.
Các mục D140 SHALL nâng lên R. P SHALL yêu cầu phiên 8 giờ, khi chưa có phiên phải xác nhận passkey trước khi ghi.
Máy chủ MUST quyết mức theo hành vi và dữ liệu hiện hành; tuyến chưa phân loại MUST từ chối ghi.

#### Scenario: Mỗi thao tác trong bốn nhóm
- **GIVEN** người đã đăng ký passkey nhưng chưa có phiên, fixture lần lượt chứa mọi hành vi trong bảng design D-2/D-3
- **WHEN** gửi từng thao tác P hoặc R trực tiếp bằng HTTP, bỏ qua nút bị khoá
- **THEN** từng thao tác trả 403 yêu cầu xác nhận, không đổi dữ liệu; sau xác nhận đúng mức mới được xét nghiệp vụ

#### Scenario: Decision không giả thành câu hỏi thường
- **GIVEN** bead ở server là decision hoặc escalation mà trả lời sẽ đóng nó
- **WHEN** client gọi `/api/phe-duyet/{du_an}/{bead_id}/tra-loi` với cờ tự khai là câu hỏi thường
- **THEN** vẫn áp P, không đóng khi thiếu phiên; cờ client không hạ quyền

#### Scenario: Nhiều thay đổi cùng yêu cầu
- **GIVEN** một lần lưu vừa chỉnh tự merge vừa đổi lệnh kiểm còn sống
- **WHEN** phiên còn hạn nhưng không có xác nhận mới
- **THEN** áp R cho cả yêu cầu, không ghi một phần

### Requirement: Thao tác không nguy hiểm không bắt chạm
Sau khi người có passkey hoạt động, trạm SHALL cho TẠM DỪNG, bật Estop, kéo cột, Trả về, thử lại, trả lời
câu hỏi thường và tắt khe qua mức N, không đòi phiên passkey (D137–D138). N MUST vẫn kiểm người/quyền,
CSRF và luật nghiệp vụ; không cấp P/R. Ghi ký ức tay và gửi phiếu yêu cầu SHALL là N theo D147; vẫn khoá khi chưa có passkey.

#### Scenario: Phiên hết hạn nhưng tắt khe được
- **GIVEN** người có credential hoạt động, login và CSRF đúng, phiên 8 giờ đã hết
- **WHEN** tắt khe, kéo cột, Trả về hoặc thử lại
- **THEN** không mở hộp passkey; chỉ ghi nếu các điều kiện nghiệp vụ còn hợp lệ

#### Scenario: Câu hỏi thường
- **GIVEN** một thao tác trả lời chỉ ghi thông tin, không tạo/đóng decision hay mở quyền
- **WHEN** người đúng quyền trả lời khi không có phiên
- **THEN** không cần chạm; không dùng tuyến đóng decision hiện có để giả lập câu hỏi thường

### Requirement: Chưa có passkey chỉ được dừng ở cửa dashboard cũ
Khi người chưa có credential hoạt động, trạm SHALL chỉ nhận ghi nghiệp vụ dashboard là TẠM DỪNG dự án/toàn trạm
và bật Estop (D135, ghi chú D141, thay D87). Mọi ghi dashboard khác MUST trả 403, kể cả Tiếp tục, kéo cột và tắt khe.
Đăng ký bằng mã B SHALL vẫn được để mở cửa lần đầu; các giao thức máy có xác thực riêng không trở thành cửa người.

#### Scenario: Trước đăng ký
- **GIVEN** trạm chưa có passkey
- **WHEN** người có login đúng bấm TẠM DỪNG hoặc Estop
- **THEN** nhận lệnh dừng không cần chạm, giữ idempotency và kiểm danh tính/CSRF

#### Scenario: Tiếp tục không còn là ngoại lệ D87
- **GIVEN** chưa có passkey, trạm hoặc dự án đang dừng
- **WHEN** gọi Tiếp tục sau tạm dừng hoặc Estop qua TCP dù header đúng
- **THEN** trả 403; trạng thái dừng giữ nguyên và UI giải thích cần đăng ký passkey

### Requirement: Phiên trình duyệt có hạn tuyệt đối tám giờ
Sau xác nhận đăng nhập hợp lệ, trạm SHALL cấp phiên gắn người, login, credential và trình duyệt, hạn 8 giờ
(D139). Cookie MUST có HttpOnly, Secure, SameSite=Strict; bản thiết kế dùng tên `__Host-tram-phien`, Path=/,
không Domain, Max-Age=28800. Server MUST kiểm hạn và thu hồi trên mỗi yêu cầu; không gia hạn ngầm do hoạt động
hay chạm R; không lưu credential phiên trong localStorage, URL hoặc JS. Thanh trên SHALL hiện thời gian còn lại từ server.

#### Scenario: Dùng lại trong tám giờ
- **GIVEN** phiên mở lúc 09:00 và chưa thu hồi
- **WHEN** lúc 16:59 người gọi P với đúng login và quyền
- **THEN** không cần chạm lại; vẫn kiểm các điều kiện nghiệp vụ; thanh trên hiện “Đã xác nhận, còn …”

#### Scenario: Đúng mốc hết hạn
- **GIVEN** phiên mở lúc 09:00
- **WHEN** gọi P lúc 17:00 hoặc sau đó, kể cả trình duyệt còn cookie
- **THEN** trả 403 yêu cầu xác nhận mới, không ghi và không kéo dài phiên

#### Scenario: Trình duyệt khác và thu hồi
- **GIVEN** một trình duyệt đã xác nhận, trình duyệt khác không có cookie; hoặc credential nguồn vừa bị thu hồi
- **WHEN** gọi P từ trình duyệt kia hoặc bằng phiên đã bị thu hồi
- **THEN** từ chối; passkey đồng bộ không đồng nghĩa tự có phiên trên mọi trình duyệt

### Requirement: Các thao tác D140 luôn xác nhận mới
Thêm/thu hồi passkey, bật tự deploy, sửa bất kỳ một trong ba lệnh deploy/kiểm còn sống/lùi MUST yêu cầu R dù
phiên còn hạn (D140). Xác nhận SHALL gắn người, phiên, đích, loại, băm nội dung và `ma_thao_tac`, chỉ dùng cho
một thao tác, hạn đề xuất 2 phút; không dùng cờ “vừa chạm” chung. Tắt tự deploy hoặc Deploy tay chỉ P.

#### Scenario: Phiên mới vẫn cần chạm
- **GIVEN** vừa mở phiên một phút trước
- **WHEN** lần lượt thêm thiết bị, thu hồi thiết bị, bật tự deploy, sửa một trong ba lệnh
- **THEN** mỗi thao tác cần xác nhận mới riêng trước khi ghi

#### Scenario: Đổi đích hoặc payload sau chạm
- **GIVEN** xác nhận R cho lệnh deploy dự án X với một mã thao tác
- **WHEN** đổi lệnh, dự án, credential cần thu hồi hoặc mã thao tác rồi gửi
- **THEN** từ chối; xác nhận không cấp quyền cho nội dung khác

#### Scenario: Huỷ xác nhận
- **GIVEN** đang mở hộp “Chạm Touch ID để xác nhận”
- **WHEN** chủ huỷ hoặc hết hạn
- **THEN** không ghi, không chạy lại tự động; giữ ô nghiệp vụ và cho chủ chủ động thử lại

### Requirement: Kiểm WebAuthn đầy đủ trước khi mở quyền
Trạm MUST kiểm challenge ngẫu nhiên còn hạn dùng một lần, RP ID cố định, Origin HTTPS máy B chính xác,
chữ ký, credential owner, user presence và user verification (UV) bắt buộc. Đăng ký và assertion SHALL dùng
verifier `webauthn`; không tự coi click nút, Touch ID trong ảnh hay header là bằng chứng sinh trắc.

#### Scenario: Bằng chứng không hợp lệ
- **GIVEN** challenge chưa dùng
- **WHEN** gửi sai RP/Origin, sai chữ ký, credential lạ, thiếu UV hoặc challenge quá hạn
- **THEN** từ chối, không thêm credential, mở phiên hay cấp R; lỗi không chứa dữ liệu xác thực gốc

#### Scenario: Replay và tranh chấp
- **GIVEN** hai yêu cầu cùng dùng assertion cho một challenge
- **WHEN** gửi đồng thời hoặc gửi lại sau khi challenge đã tiêu thụ
- **THEN** tối đa một lần mở quyền; lần còn lại không tạo phiên/quyền mới

### Requirement: Đăng ký đầu tiên bằng mã một lần từ máy B
Trạm SHALL cung cấp CLI đề xuất `tram chu passkey cap-ma` trên B: in kế hoạch, xác nhận tương tác, cấp mã
ngẫu nhiên ≥128 bit gắn đúng người/login, hết hạn 10 phút, dùng một lần (D141). Mã MUST chỉ in một lần vào TTY
của người được quyền, không argv/log/file, không cho agent gọi CLI hay đọc mã. Server chỉ lưu băm mã.
Trang SHALL nhận mã qua HTTPS body, yêu cầu tạo passkey có UV; mã một mình MUST NOT cấp phiên ghi.

#### Scenario: Đăng ký trên máy A
- **GIVEN** chủ vừa cấp mã tại Terminal.app máy B và đăng nhập đúng Tailscale trên A
- **WHEN** trong 10 phút nhập mã trên dashboard A rồi hoàn tất tạo passkey có UV
- **THEN** thêm credential cho đúng chủ và tiêu thụ mã nguyên tử; mở phiên chỉ sau xác thực hợp lệ, báo thêm thiết bị

#### Scenario: Hết hạn hoặc dùng lần hai
- **GIVEN** mã đã hết đúng 10 phút hoặc đã đăng ký thành công một lần
- **WHEN** nhập mã để đăng ký tiếp
- **THEN** từ chối với lỗi chung, không thêm credential, không gia hạn mã

#### Scenario: Hai máy tranh mã
- **GIVEN** hai browser nhận challenge từ cùng mã còn hạn
- **WHEN** cả hai hoàn tất đăng ký
- **THEN** chỉ một credential được ghi thành công; lần còn lại bị từ chối

#### Scenario: Không đưa mã vào chỗ dễ lộ
- **GIVEN** CLI bị gọi với xác nhận trong argv hoặc stdout bị chuyển hướng; hoặc thử mã sai nhiều lần
- **WHEN** cấp/đổi mã
- **THEN** CLI từ chối in mã ra file; lỗi không echo bí mật; API giới hạn đề xuất 5 lần mã sai/10 phút/người và nguồn,
  trả 429 khi vượt; không ghi mã vào log, lịch sử shell, sự kiện hay Telegram

### Requirement: Thêm và thu hồi thiết bị có xác nhận và cảnh báo
Từ credential đã đăng ký, chủ SHALL thêm thiết bị bằng R để cấp mã/QR một lần gắn người/login, 10 phút;
thiết bị mới vẫn cần UV (D142). Mã CLI B SHALL vẫn dùng được khi đã có credential. Mỗi lần thêm thành công
hoặc thu hồi SHALL có sự kiện và một cảnh báo Telegram, không chứa mã/QR. Danh sách SHALL hiện tên gợi nhớ,
lúc thêm/dùng gần nhất, trạng thái; không hiển thị public key/raw credential. Thu hồi SHALL vô hiệu credential,
phiên liên quan và mã mời chưa dùng do credential đó cấp ngay khi commit.

#### Scenario: Thêm bằng thiết bị đang có
- **GIVEN** chủ đang dùng thiết bị đã đăng ký
- **WHEN** bấm Thêm, xác nhận mới, chuyển mã/QR cho browser mới đúng login và đăng ký có UV
- **THEN** thêm một credential và một cảnh báo, mã không dùng tiếp được; không tự cấp quyền cho login khác

#### Scenario: Thu hồi thiết bị lẻ
- **GIVEN** có hai credential và phiên mở từ credential thứ hai
- **WHEN** chủ xác nhận R để thu hồi credential thứ hai
- **THEN** credential và phiên đó hết hiệu lực ngay; credential thứ nhất giữ nguyên; gửi cảnh báo

#### Scenario: Credential cuối cùng
- **GIVEN** chỉ còn một credential hoạt động
- **WHEN** chủ bấm thu hồi nó trên web
- **THEN** theo D148, server từ chối và chỉ đường khôi phục tại B; không để chủ mất cửa ghi mà không có mã mới

#### Scenario: Credential đồng bộ
- **GIVEN** một credential dùng qua nhiều thiết bị nhờ đồng bộ
- **WHEN** chủ xem và thu hồi mục đó
- **THEN** UI giải thích các bản sao cùng passkey cũng mất quyền; không hứa chỉ thu hồi một máy vật lý

### Requirement: Khôi phục tại B thu hồi toàn bộ quyền cũ
CLI đề xuất `tram chu passkey khoi-phuc` SHALL chỉ chạy tại B dưới quyền chủ được cách ly khỏi agent; yêu cầu
gõ chính xác `dong-y` tương tác (D144). Thành công MUST thu hồi mọi credential, phiên, challenge và mã cũ của
người, cấp mã đăng ký mới 10 phút, xếp cảnh báo Telegram; không tự Tiếp tục hay bật tự động. Không có HTTP reset.

#### Scenario: Mất hết thiết bị
- **GIVEN** chủ không còn thiết bị dùng được
- **WHEN** tại B xem kế hoạch và gõ `dong-y`
- **THEN** mọi credential/phiên cũ bị thu hồi, in mã mới một lần; đăng ký lại được bằng đúng login, chỉ dừng được
  ở cửa dashboard cũ cho đến khi đăng ký; Telegram được xếp gửi

#### Scenario: Huỷ khôi phục và agent gọi thử
- **GIVEN** chưa commit khôi phục
- **WHEN** không gõ đúng `dong-y`, hết hạn xác nhận, hoặc principal agent gọi CLI
- **THEN** không đổi dữ liệu, không in mã; principal agent không được vượt bằng cách tự gõ `dong-y`

#### Scenario: Mã và cookie cũ sau khôi phục
- **GIVEN** khôi phục đã commit
- **WHEN** thử tất cả mã mời chưa dùng, cookie còn hạn và chữ ký bằng passkey cũ
- **THEN** đều bị từ chối; restart trạm không khôi phục quyền cũ

### Requirement: Windows có đường xác nhận phù hợp
Dashboard SHALL cho browser Windows dùng Windows Hello, QR điện thoại của WebAuthn, hoặc khoá USB;
không giả định passkey iCloud tự xuất hiện trên Windows. RP, Origin, login, UV, phiên và R MUST giữ cùng luật.
Mockup SHALL phân biệt QR mời đăng ký với QR xác thực do trình duyệt cung cấp; không tự giả chữ ký hay UV.

#### Scenario: Windows Hello hoặc khoá USB
- **GIVEN** browser Windows hỗ trợ WebAuthn và authenticator tương thích có UV
- **WHEN** chủ đăng ký/đăng nhập bằng Windows Hello hoặc khoá USB
- **THEN** cùng kiểm xác thực và phiên 8 giờ; khoá không đáp ứng UV không được hạ xuống chỉ chạm vật lý

#### Scenario: Dùng điện thoại trên Windows
- **GIVEN** passkey ở điện thoại, Windows không có bản iCloud tương ứng
- **WHEN** chọn dùng thiết bị khác trong hộp của browser và xác nhận trên điện thoại
- **THEN** đăng nhập được nếu ceremony hợp lệ và login khớp; không đồng nghĩa thêm credential Windows mới

#### Scenario: Browser không hỗ trợ hoặc huỷ
- **GIVEN** WebAuthn không khả dụng hoặc người huỷ
- **WHEN** bấm thao tác P/R
- **THEN** báo hướng dùng browser/thiết bị hỗ trợ; không tự hạ cửa ghi, vẫn cho TẠM DỪNG/Estop

### Requirement: Serve tới TCP không biến địa chỉ mạng thành quyền người
Trạm SHALL phục vụ API tại loopback TCP, Tailscale Serve chuyển tiếp HTTPS tới cổng này (D135, G29).
Passkey MUST là bằng chứng bổ sung cho P/R; không dùng socket, WhoIs, IP tailnet hoặc header đơn lẻ để mở P/R.
Các cửa máy MUST giữ token và phạm vi riêng, không nhận cookie người thay token hoặc token máy thay passkey.

#### Scenario: Agent A và B giả yêu cầu người
- **GIVEN** agent A có danh tính mạng giống chủ nhưng không có cookie/passkey; agent B chỉ có thể gọi loopback
- **WHEN** giả login, Origin, X-Tram để gọi từng P/R
- **THEN** cả hai bị 403, không ghi; bằng chứng cổng ghi rõ quyền OS/cookie của agent, không suy rộng tới cookie bị lấy cắp

#### Scenario: Cửa máy không bị buộc Touch ID
- **GIVEN** thợ có token đúng, phiếu/lượt đúng
- **WHEN** báo nhịp, báo kết quả hoặc công bố theo luồng được cấp
- **THEN** giữ xác thực máy, không gọi hộp passkey; token đó không gọi được tuyến P/R của chủ

#### Scenario: Đăng ký khe không bật lại trái phép
- **GIVEN** khe đã bị chủ tắt, hoặc khe mới chưa được cấp quyền chạy
- **WHEN** thợ gọi `/api/tho/dang-ky` với thông tin đổi để sinh `khe.dang_ky`
- **THEN** không làm khe chạy lại hay tự cấp quyền; bật/cho chạy vẫn cần P từ chủ

#### Scenario: Ghép máy không vượt quyền cấp mã
- **GIVEN** chưa có quyền ghép máy do chủ xác nhận P
- **WHEN** agent xin cấp mã ghép hoặc dùng mã đăng ký passkey ở `/api/ghep-may`
- **THEN** không cấp token máy; chỉ mã ghép đúng mục đích do chủ cho phép mới đổi được một lần

### Requirement: Giữ idempotency và kiểm nghiệp vụ sau xác thực
Mọi ghi dashboard SHALL giữ `ma_thao_tac` và các kiểm phiên bản/commit hiện có. Cùng người, mã, thao tác,
đích và nội dung SHALL chỉ có một tác dụng, kể cả sau xác nhận hay mất phản hồi. Cùng mã khác nội dung MUST
trả 409; người khác không nhận kết quả cũ. Retry đã ghi thành công không đòi R lần nữa nếu phiên/quyền còn hợp lệ,
nhưng MUST NOT tạo tác dụng mới. Xác thực thất bại MUST NOT đánh dấu thao tác nghiệp vụ đã hoàn tất.

#### Scenario: Mất phản hồi sau sửa lệnh
- **GIVEN** xác nhận R và sửa lệnh thành công nhưng client mất phản hồi
- **WHEN** gửi lại đúng mã/nội dung với cùng người, phiên hợp lệ
- **THEN** trả kết quả cũ, không sửa lần hai, không lặp sự kiện hoặc tin cảnh báo do nghiệp vụ

#### Scenario: Dữ liệu đổi giữa chạm và ghi
- **GIVEN** chủ đã chạm nhưng dữ liệu phiên bản/commit đã đổi hoặc dự án bị khoá ghi
- **WHEN** gửi thao tác
- **THEN** vẫn từ chối theo 409/422 hiện có, không bỏ qua khoá/Estop/cổng kiểm; sửa nội dung cần mã và R mới

#### Scenario: Gửi lại với mã khác nội dung
- **GIVEN** mã thao tác đã gắn với một yêu cầu
- **WHEN** cùng người đổi payload hoặc người khác dùng lại mã để đọc kết quả
- **THEN** không ghi mới, không lộ kết quả cho người khác; nội dung xung đột trả 409

### Requirement: Bí mật không vào nhật ký sự kiện và báo tin
Trạm MUST NOT ghi private key, cookie, mã phiên, mã một lần, QR bí mật, assertion, attestation hoặc nội dung
challenge vào argv, log, sự kiện, Telegram, bead hay báo cáo. Phản hồi có mã/cookie và trang xác thực SHALL dùng
`Cache-Control: no-store`; lỗi phải là mã/lời chung. Tin thêm/thu hồi/khôi phục SHALL dùng ID sự kiện riêng và mẫu
cố định, link sạch, không tên thiết bị tuỳ ý. Hàng chờ bền MUST không gộp mất các lần quản lý thiết bị (D142/D144).
Theo D149, tin thêm/thu hồi/khôi phục trong giờ yên lặng MUST được giữ bền, gom gửi buổi sáng khi hết
giờ yên lặng cấu hình; bản gom giữ đủ ID, loại và thời điểm từng sự kiện. Telegram lỗi không hoàn tác thu hồi.

#### Scenario: Nhiều thay đổi thiết bị gần nhau
- **GIVEN** thêm hai credential rồi thu hồi một credential trong một phút
- **WHEN** vòng báo tin xử lý
- **THEN** ngoài giờ yên lặng có đủ ba ID sự kiện; trong giờ yên lặng giữ cả ba rồi gom gửi buổi sáng,
  không gộp mất lần; không chứa mã hay tên tuỳ ý

#### Scenario: Telegram mất kết nối
- **GIVEN** thu hồi đã commit, Telegram trả lỗi hoặc timeout
- **WHEN** vòng sau thử lại sau restart
- **THEN** quyền đã thu hồi vẫn mất; cảnh báo còn trong hàng chờ bền, UI báo chờ gửi; retry không chứa bí mật

#### Scenario: Quét rò rỉ cả nhánh lỗi
- **GIVEN** fixture đặt dấu nhận diện giả vào cookie, mã mời, assertion và tên thiết bị
- **WHEN** chạy thành công, lỗi kiểm cấu trúc, lỗi xác thực và lỗi Telegram
- **THEN** không dấu bí mật nào xuất hiện trong sự kiện, log, argv hay nội dung Telegram; mã chỉ hiện tại nơi cấp/nhập được phép

### Requirement: Dependency theo D145 và không thêm gói browser
Plan triển khai SHALL chọn và ghim đúng một phiên bản PyPI `webauthn` (duo-labs/py_webauthn) đã phát hành
ít nhất 14 ngày, ghi bằng chứng ngày phát hành và khoá phụ thuộc `cbor2`, `cryptography`, `pyasn1`, `pyOpenSSL`
(D145). Browser MUST dùng WebAuthn có sẵn, không thêm gói npm. Phiên spec offline MUST NOT tải gói.

#### Scenario: Chọn thư viện trong plan
- **GIVEN** đến pha plan và được phép truy cập nguồn phát hành
- **WHEN** chọn phiên bản verifier
- **THEN** ghi đúng phiên bản, ngày phát hành và ngày kiểm ≥14 ngày sau; lockfile khớp, không range phiên bản

#### Scenario: Không có cache trong phiên này
- **GIVEN** phiên bàn giao cấm mạng và tải gói
- **WHEN** cần validate hoặc chụp mockup nhưng thiếu công cụ cục bộ
- **THEN** không tải; báo rõ bước chưa chạy, không tuyên bố đã kiểm bằng công cụ đó

### Requirement: Hồ sơ dashboard tách khỏi agent (D146)
Đại ca SHALL dùng hồ sơ trình duyệt riêng cho dashboard; agent MUST NOT được điều khiển hồ sơ đó.
Đây là luật vận hành và cổng đo, không phải khẳng định profile riêng tự ngăn đọc cookie ở cấp OS.

#### Scenario: Đo đúng hồ sơ của Đại ca
- **GIVEN** dashboard có phiên trên hồ sơ riêng và agent A/B chạy dưới quyền thực tế
- **WHEN** đo đọc cookie, điều khiển trình duyệt và gọi CLI cấp mã/khôi phục từ agent
- **THEN** ghi UID/quyền, kết quả và rủi ro còn lại; theo D153, nếu agent vẫn với tới hồ sơ dashboard
  hoặc lệnh khôi phục thì Đại ca chấp nhận rủi ro và vẫn mở cửa; dự án thật xét riêng khi bật.
  Không gọi phép đo này là cách ly đạt và không lấy request thiếu cookie trả 403 làm bằng chứng cách ly.

#### Scenario: Tin ban đêm sống qua restart
- **GIVEN** thêm, thu hồi và khôi phục thiết bị trong giờ yên lặng rồi khởi động lại vòng báo tin
- **WHEN** đến buổi sáng, hết giờ yên lặng cấu hình
- **THEN** gửi bản gom giữ đủ từng sự kiện, không gửi ngay ban đêm và không mất tin; lỗi gửi giữ để retry


### Requirement: Quyết định vận hành D152–D155
Kho xác thực SQLite riêng SHALL được dùng theo D152 đã duyệt; không sửa schema kho nghiệp vụ.
D153 cho phép mở cửa khi phép đo còn thấy agent truy cập hồ sơ dashboard/lệnh khôi phục; MUST ghi rủi ro
vào sổ tay, dự án thật xét riêng khi bật. Quyết định này thay điều kiện đóng cửa vì cùng UID trong design cũ.
Giờ yên lặng D154 SHALL là 23:00–07:00 theo Asia/Ho_Chi_Minh, Đại ca tự bật cấu hình (hiện tắt);
agent không tự sửa cấu hình thật. D155 SHALL đóng CLI cấp mã ghép cũ; nút dashboard làm sau có mockup duyệt.

#### Scenario: Quyết định đã chốt không bị hỏi lại
- **GIVEN** áp plan passkey sau review vòng 1
- **WHEN** chuẩn bị cổng vận hành
- **THEN** dùng D152–D155 trên, ghi rủi ro D153 và chờ Đại ca tự bật giờ yên lặng; không mở lại CLI ghép cũ


#### Scenario: Chưa triển khai nút ghép máy theo D155
- **GIVEN** lát passkey chưa có mockup và luồng dashboard cấp mã ghép máy
- **WHEN** gọi CLI cấp mã ghép cũ hoặc POST `/api/passkey/ghep-ma`, kể cả với phiên hợp lệ
- **THEN** CLI từ chối; endpoint chưa mở (404), không cấp/hủy mã hay ghi sự kiện cấp mã.
  API đổi mã `/api/ghep-may` giữ hợp đồng riêng; không mở lại CLI để bù.

### Requirement: Kết quả quản lý thiết bị bền theo mã
Cùng người/mã/nội dung MUST không tạo tác dụng lần hai, kể cả phiên mới. Khác nội dung MUST trả 409.
Kiểm R, ledger và tác dụng MUST trong cùng giao dịch. Không lưu mã mời rõ để phục hồi phản hồi.

#### Scenario: Mất phản hồi cấp mã
- **GIVEN** lần cấp mã đã commit nhưng phản hồi bị mất
- **WHEN** retry cùng mã/nội dung với quyền hợp lệ, kể cả từ phiên mới hoặc mã mời đã dùng
- **THEN** trả trạng thái đã cấp, không cấp/hủy mã khác; muốn mã mới người dùng chủ động tạo yêu cầu mới
