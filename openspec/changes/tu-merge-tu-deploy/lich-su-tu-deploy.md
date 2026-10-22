> **SUPERSEDED 20/10/2026:** chỉ để đối chiếu. Nguồn hiện hành: `../tu-merge-deploy/specs/tu-deploy/spec.md`. QĐ1–QĐ4 đã chốt.

# Spec Delta — tu-deploy

## Purpose

Đưa bản code đã merge của một dự án lên môi trường khách đang dùng bằng ba lệnh dự án khai (deploy, kiểm còn sống,
lùi), do Đại ca bấm hoặc trạm tự chạy khi Đại ca đã bật, có tự lùi và tự tắt khi hỏng lặp lại (D73–D75, D88,
D89, D96–D98, D100, D101).

## Yêu cầu lịch sử — không phải delta để archive

### Requirement: Ba lệnh deploy của dự án
Mỗi dự án SHALL có ba lệnh: **deploy**, **kiểm còn sống** sau deploy, **lùi về bản trước**, Đại ca khai trên
dashboard và trạm lưu trong sổ ghi sự kiện của trạm, không trong `du-an/*.yaml` (D73, D88). Thiếu một trong ba thì
trạm MUST NOT deploy dự án đó, kể cả khi Đại ca bấm nút, và nút tự deploy MUST NOT bật được.

#### Scenario: Dự án chưa khai lệnh lùi
- **GIVEN** dự án có lệnh deploy và kiểm còn sống, chưa có lệnh lùi
- **WHEN** Đại ca mở trang tự merge/deploy của dự án
- **THEN** nút Deploy và nút tự deploy bị khoá, kèm chữ "Chưa khai đủ 3 lệnh"; máy chủ cũng từ chối yêu cầu deploy (422)

### Requirement: File mà ba lệnh dùng là file cấm sửa
Mọi file trong repo dự án mà ba lệnh nhắc tới SHALL tự thuộc danh sách đường dẫn cấm của dự án (D89). Agent sửa một
file như vậy thì trạm MUST dừng hỏi Đại ca (escalation như đường dẫn cấm hiện có) và MUST NOT tự merge việc đó.

#### Scenario: Agent sửa script deploy
- **GIVEN** lệnh deploy của dự án là `scripts/deploy.sh`
- **WHEN** diff của một bead sửa `scripts/deploy.sh`
- **THEN** trạm không chạy lệnh kiểm, tạo escalation `dong-file-cau-hinh`, việc chờ Đại ca

### Requirement: Sẵn sàng deploy chờ Đại ca bấm
Khi nút tự deploy của dự án tắt (mặc định), sau mỗi lần merge đã xác minh — do trạm tự merge hay do Đại ca gộp tay
(D96) — trạm SHALL đánh dấu dự án "sẵn sàng deploy", báo Telegram, và MUST NOT tự chạy lệnh deploy (D74). Mỗi dự án
đang sẵn sàng deploy SHALL có một dòng ở trang Phê duyệt và được tính vào số đếm việc chờ Đại ca (D101).

#### Scenario: Tự merge xong, tự deploy tắt
- **GIVEN** dự án `repo-nhap` đủ 3 lệnh, nút tự deploy tắt
- **WHEN** trạm tự merge và xác minh xong PR của `rn-7`
- **THEN** dashboard hiện hàng "sẵn sàng deploy" kèm nút Deploy; Telegram nhận tin "repo-nhap · sẵn sàng deploy"

#### Scenario: Đại ca gộp tay
- **GIVEN** dự án đủ 3 lệnh, công tắc tự merge tắt
- **WHEN** Đại ca tự merge một PR của trạm trên GitHub và trạm xác minh được
- **THEN** dự án vẫn được đánh dấu "sẵn sàng deploy"

#### Scenario: Hiện ở trang Phê duyệt
- **WHEN** `repo-nhap` đang sẵn sàng deploy
- **THEN** trang Phê duyệt có một dòng "repo-nhap · sẵn sàng deploy" có nút Deploy (cùng xác nhận, cùng khoá và cùng kiểm bản như nút ở trang Tự động — D129) và link sang trang Tự động của dự án, số đếm ở thanh bên tăng 1

### Requirement: Nút Deploy của Đại ca
Nút Deploy SHALL đi qua cửa ghi có xác thực như mọi thao tác ghi dashboard, mang mã thao tác và commit Đại ca đang
thấy. Commit mới nhất đã merge khác commit đó thì máy chủ MUST từ chối (409) để Đại ca xem lại.

#### Scenario: Đại ca bấm Deploy
- **WHEN** Đại ca bấm Deploy cho commit `m5` và xác nhận
- **THEN** trạm chạy chuỗi deploy cho `m5`; hàng "sẵn sàng deploy" chuyển sang "đang deploy"

#### Scenario: Bấm trên màn hình cũ
- **GIVEN** sau khi trang tải, trạm vừa merge thêm, commit mới nhất là `m6`
- **WHEN** Đại ca bấm Deploy với commit `m5`
- **THEN** máy chủ trả 409; dashboard báo "Có bản mới hơn — tải lại"

#### Scenario: Yêu cầu không mang danh tính Đại ca
- **WHEN** yêu cầu deploy thiếu hoặc giả danh tính
- **THEN** máy chủ trả 403, không chạy lệnh nào

### Requirement: Tự deploy khi Đại ca bật
Khi nút tự deploy của dự án bật, sau mỗi lần tự merge đã xác minh, trạm SHALL tự chạy chuỗi deploy cho bản mới
nhất của nhánh chính mà không chờ Đại ca (D74).

#### Scenario: Tự deploy sau tự merge
- **GIVEN** nút tự deploy của `repo-nhap` bật
- **WHEN** trạm tự merge và xác minh xong PR của `rn-7`
- **THEN** trạm chạy lệnh deploy, rồi lệnh kiểm còn sống; Telegram nhận tin kết quả

### Requirement: Kiểm còn sống sau mỗi lần deploy
Sau khi lệnh deploy thoát thành công, trạm SHALL chạy lệnh kiểm còn sống. Deploy chỉ được coi là thành công khi
lệnh kiểm còn sống thoát thành công trong thời hạn.

#### Scenario: Deploy chạy xong nhưng trang chết
- **WHEN** lệnh deploy thoát 0, lệnh kiểm còn sống thoát khác 0
- **THEN** lần deploy này tính là hỏng và trạm chuyển sang lùi

### Requirement: Deploy hỏng thì tự lùi và báo
Lệnh deploy lỗi, quá hạn, hoặc kiểm còn sống không đạt thì trạm SHALL chạy lệnh lùi về bản trước rồi chạy lại lệnh
kiểm còn sống, báo Telegram, và MUST NOT tắt tự deploy vì một lần hỏng (D75).

#### Scenario: Lùi thành công
- **WHEN** deploy hỏng, lệnh lùi chạy xong và kiểm còn sống đạt
- **THEN** Telegram nhận tin "repo-nhap · deploy hỏng, đã tự lùi"; bộ đếm hỏng liên tiếp tăng 1; nút tự deploy giữ nguyên

### Requirement: Hỏng 3 lần liên tiếp thì tự tắt tự deploy
Khi bộ đếm hỏng liên tiếp của dự án đạt 3, trạm SHALL tự tắt nút tự deploy của dự án đó và báo Telegram, rồi chờ
Đại ca bật lại (D75). Một lần deploy thành công SHALL đặt bộ đếm về 0; Đại ca bật lại nút cũng đặt về 0.

#### Scenario: Lần hỏng thứ ba
- **GIVEN** bộ đếm hỏng liên tiếp của `repo-nhap` là 2
- **WHEN** lần deploy kế tiếp hỏng và đã tự lùi
- **THEN** nút tự deploy chuyển tắt, sự kiện ghi tác nhân là trạm; Telegram báo "đã tự tắt tự deploy sau 3 lần hỏng"; các lần merge sau quay về "sẵn sàng deploy"

#### Scenario: Thành công xen giữa
- **GIVEN** bộ đếm là 2
- **WHEN** lần deploy kế tiếp thành công
- **THEN** bộ đếm về 0

### Requirement: Lùi cũng hỏng thì dừng hẳn và báo khẩn
Lệnh lùi lỗi, quá hạn, hoặc kiểm còn sống sau lùi vẫn không đạt thì trạm SHALL tắt tự deploy, TẠM DỪNG tự merge và
tự deploy của dự án đó, và báo Telegram loại khẩn kể cả trong giờ yên lặng (D97).

#### Scenario: Trang chết sau lùi
- **WHEN** lùi xong nhưng kiểm còn sống vẫn không đạt
- **THEN** dự án chuyển "tạm dừng", nút tự deploy tắt; Telegram gửi ngay tin "repo-nhap · LÙI HỎNG — cần Đại ca"

### Requirement: Một chuỗi deploy một lúc, deploy bản mới nhất
Mỗi dự án SHALL chạy tối đa một chuỗi deploy (deploy → kiểm còn sống → lùi nếu cần) cùng lúc. Nhiều lần merge dồn
lại trước khi deploy MUST gộp thành một lần deploy cho commit mới nhất của nhánh chính (D97).

#### Scenario: Ba lần merge chờ deploy
- **GIVEN** tự deploy tắt, trạm đã tự merge `rn-7`, `rn-8`, `rn-9` mà Đại ca chưa bấm
- **WHEN** Đại ca mở dashboard
- **THEN** chỉ có một hàng "sẵn sàng deploy" cho commit mới nhất, ghi "gồm 3 việc đã merge"

#### Scenario: Merge mới trong lúc đang deploy
- **WHEN** trạm tự merge thêm một PR khi chuỗi deploy trước còn chạy
- **THEN** chuỗi đang chạy làm nốt; bản mới chờ tới lượt sau

### Requirement: Kết quả deploy không rõ thì không chạy lại mù
Trạm tắt hay máy khởi động lại giữa một chuỗi deploy thì khi chạy lại trạm SHALL ghi chuỗi đó là "không rõ kết
quả", TẠM DỪNG tự deploy của dự án và báo Telegram. Trạm MUST NOT tự chạy lại lệnh deploy hay lệnh lùi đó (D97).

#### Scenario: Mất điện giữa deploy
- **WHEN** trạm khởi động lại và thấy chuỗi deploy bắt đầu mà chưa có kết quả
- **THEN** dashboard hiện "deploy không rõ kết quả — cần Đại ca kiểm"; không lệnh nào chạy lại tự động

### Requirement: Mỗi lệnh có giới hạn thời gian
Lệnh deploy SHALL có hạn 15 phút, lệnh kiểm còn sống 2 phút, lệnh lùi 15 phút, chung cho mọi dự án (D100). Quá hạn
MUST coi là hỏng và dừng cả nhóm tiến trình của lệnh đó.

#### Scenario: Lệnh deploy treo
- **WHEN** lệnh deploy chạy quá giới hạn
- **THEN** trạm dừng lệnh, tính là deploy hỏng và chuyển sang lùi

### Requirement: Không lọt bí mật qua kết quả deploy
Dashboard và Telegram SHALL chỉ hiện kết quả deploy dạng đạt/hỏng, mã thoát, thời gian chạy. Đầu ra của lệnh MUST
NOT hiện trên dashboard hay Telegram; nó chỉ được lưu cục bộ trên máy B sau khi qua bộ quét bí mật.

#### Scenario: Lệnh deploy in ra token
- **WHEN** đầu ra lệnh deploy có một chuỗi giống token
- **THEN** dashboard chỉ hiện "hỏng · mã thoát 1 · 42 giây"; file log cục bộ có chuỗi đó đã bị che

### Requirement: Báo Telegram mỗi lần deploy và lùi
Mỗi lần tự deploy, Deploy do Đại ca bấm, và tự lùi SHALL sinh một tin Telegram (D78), chỉ gồm tên dự án, loại tin,
số lần hỏng liên tiếp khi có, và link dashboard. Tin xấu (hỏng, đã lùi, tự tắt, lùi hỏng, không rõ kết quả) MUST gửi
ngay cả trong giờ yên lặng; tin tốt (deploy xong, sẵn sàng deploy) gom gửi sau giờ yên lặng (D98).

#### Scenario: Deploy thành công
- **WHEN** chuỗi deploy của `repo-nhap` thành công
- **THEN** Telegram nhận tin "repo-nhap · deploy xong" kèm link dashboard

#### Scenario: Hỏng lúc nửa đêm
- **WHEN** lúc 02:00 (giờ yên lặng) deploy hỏng và đã tự lùi
- **THEN** tin "đã tự lùi" gửi ngay; tin "deploy xong" của một lần khác lúc 01:00 được gom gửi sau giờ yên lặng
