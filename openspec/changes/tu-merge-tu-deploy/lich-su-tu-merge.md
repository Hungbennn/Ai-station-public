> **SUPERSEDED 20/10/2026:** chỉ để đối chiếu. Nguồn hiện hành: `../tu-merge-deploy/specs/tu-merge/spec.md`. QĐ1–QĐ4 đã chốt.

# Spec Delta — tu-merge

## Purpose

Trạm tự gộp (merge) vào nhánh chính PR do chính trạm mở, khi dự án đã bật công tắc và việc đủ mọi điều kiện an toàn
Đại ca chốt (D69–D72, D76, D90–D93, D95); thiếu điều kiện nào thì việc chờ Đại ca như trước.

## Yêu cầu lịch sử — không phải delta để archive

### Requirement: Công tắc tự merge theo dự án, mặc định tắt
Mỗi dự án SHALL có một công tắc tự merge riêng. Dự án chưa từng được Đại ca bật SHALL coi là tắt. Công tắc tắt thì
trạm MUST NOT merge bất kỳ PR nào của dự án đó; Đại ca merge tay như trước (D69).

#### Scenario: Dự án mới thêm vào trạm
- **GIVEN** dự án `repo-nhap` vừa được thêm, chưa ai chỉnh công tắc tự merge
- **WHEN** một bead của dự án vào cột 3, PR đã mở và đủ cả 5 điều kiện
- **THEN** trạm không merge, bead ở lại cột 3 chờ Đại ca

#### Scenario: Bật cho một dự án không ảnh hưởng dự án khác
- **GIVEN** công tắc tự merge của `repo-nhap` bật, của `hr-codex` tắt
- **WHEN** cả hai dự án có PR đủ điều kiện
- **THEN** trạm chỉ merge PR của `repo-nhap`; PR của `hr-codex` chờ Đại ca

### Requirement: Chỉ merge PR của trạm, đúng commit đã kiểm
Trạm SHALL chỉ tự merge PR mà chính trạm đã mở cho bead đó, khi đầu PR đúng bằng commit bàn giao trong bằng chứng
hiện hành của bead (spec 4 §6.4, §6.7). Lúc gửi lệnh merge, trạm MUST buộc GitHub chỉ merge nếu đầu PR vẫn là
commit đó.

#### Scenario: Đầu PR đổi sau khi kiểm
- **GIVEN** PR của bead `rn-7` do trạm mở tại commit `c1`, bằng chứng hiện hành trỏ `c1`
- **WHEN** nhánh của PR bị đẩy thêm commit `c2` trước lúc merge
- **THEN** trạm không merge; bead chờ Đại ca, dashboard ghi lý do "đầu PR khác commit đã kiểm"

#### Scenario: PR không do trạm mở
- **WHEN** dự án có PR do người khác mở vào nhánh chính
- **THEN** trạm không bao giờ tự merge PR đó

### Requirement: Khoá cứng QC đạt
Trạm SHALL chỉ tự merge khi QC của một khe khác khe đã code kết luận đạt cho đúng commit đang xét (INV-006).
Điều kiện này MUST NOT có nút tắt ở bất kỳ đâu (D71).

#### Scenario: QC trả về
- **GIVEN** QC mới nhất của bead kết luận `tra_ve`
- **WHEN** vòng tick xét tự merge
- **THEN** trạm không merge

#### Scenario: Yêu cầu tắt điều kiện QC bị từ chối
- **WHEN** một yêu cầu ghi cấu hình cố đặt điều kiện QC thành tắt
- **THEN** máy chủ từ chối yêu cầu (lỗi 422), cấu hình không đổi; dashboard hiện điều kiện QC là "luôn bật", không có nút

### Requirement: Khoá cứng kiểm lại đạt
Trạm SHALL chỉ tự merge khi lần kiểm lại trong vùng cách ly của đúng lượt code và đúng commit đang xét đạt, và
bằng chứng còn hiệu lực (INV-003). Điều kiện này MUST NOT có nút tắt (D71).

#### Scenario: Kiểm lại không đạt
- **GIVEN** lần kiểm lại mới nhất của bead không đạt
- **WHEN** vòng tick xét tự merge
- **THEN** trạm không merge

#### Scenario: Bằng chứng hết hiệu lực
- **GIVEN** bead đã kiểm lại và QC đạt tại commit `c1`
- **WHEN** tiêu chí nghiệm thu của bead bị sửa sau lần kiểm đó
- **THEN** trạm không merge; bead phải kiểm lại như luật hiện hành

### Requirement: Điều kiện CI GitHub xanh, có nút
Khi nút "CI xanh" của dự án bật (mặc định bật), trạm SHALL chỉ tự merge khi mọi kiểm tra CI của GitHub trên đầu PR
đã xong và đều đạt. PR không có kiểm tra CI nào MUST coi là chưa xanh (D93). Nút tắt thì trạm bỏ qua điều kiện này
(D70).

#### Scenario: CI đang chạy
- **WHEN** CI trên đầu PR chưa chạy xong
- **THEN** trạm chưa merge và xét lại ở vòng tick sau, không báo lỗi

#### Scenario: CI đỏ
- **WHEN** một kiểm tra CI trên đầu PR thất bại
- **THEN** trạm không merge; bead chờ Đại ca với lý do "CI chưa xanh"

#### Scenario: Dự án tắt nút CI
- **GIVEN** nút "CI xanh" của dự án tắt
- **WHEN** PR không có kiểm tra CI nào và bốn điều kiện còn lại đủ
- **THEN** trạm merge

### Requirement: Điều kiện việc thuộc cột "AI tự làm", có nút
Khi nút "cột AI tự làm" bật (mặc định bật), trạm SHALL chỉ tự merge bead đi vào cột 3 theo luồng tự động từ cột 1:
mọi phiếu của bằng chứng hiện hành được cấp khi bead mang đúng nhãn cột 1, và bead không có nhãn `cot-khoa`
(Đại ca tự gán cột). Nút tắt thì bỏ qua điều kiện này, vẫn phải đủ QC và kiểm lại (D70, D90).

#### Scenario: Đại ca đã tự gán cột
- **GIVEN** bead mang `cot-khoa` vì Đại ca kéo tay
- **WHEN** bead vào cột 3 với QC và kiểm lại đạt
- **THEN** trạm không merge khi nút "cột AI tự làm" bật

#### Scenario: Tắt nút cột
- **GIVEN** nút "cột AI tự làm" tắt, bead mang `cot-khoa`
- **WHEN** bead vào cột 3, QC và kiểm lại đạt, các điều kiện còn lại đủ
- **THEN** trạm merge

### Requirement: Điều kiện không chạm hàng rào, có nút
Khi nút "hàng rào" bật (mặc định bật), trạm SHALL coi việc là chạm hàng rào **chỉ khi code sửa vào vùng nhạy cảm**:
diff từ gốc nhánh khớp đường dẫn của bất kỳ hàng rào nào trong cấu hình dự án (cờ đỏ `co-do`). Nội dung việc chỉ
nhắc từ khoá nhạy cảm MUST NOT tính là chạm. Chạm thì MUST NOT tự merge (D70, D91).

#### Scenario: Diff chạm đường dẫn tiền
- **GIVEN** diff của bead khớp đường dẫn hàng rào `tien`, bead có `co-do`
- **WHEN** vòng tick xét tự merge
- **THEN** trạm không merge; lý do "chạm hàng rào: tiền/giá"

#### Scenario: Việc chỉ nhắc từ khoá, code không chạm vùng nhạy cảm
- **GIVEN** mô tả bead nhắc "hoá đơn", diff không khớp đường dẫn hàng rào nào, bead không có `co-do`
- **WHEN** bead vào cột 3 đủ QC, kiểm lại, CI, cột
- **THEN** trạm merge

### Requirement: Cấu trúc DB và xoá dữ liệu luôn chờ Đại ca
Việc chạm hàng rào cấu trúc dữ liệu `schema` SHALL luôn chờ Đại ca, bất kể nút "hàng rào" bật hay tắt (D76). Mỗi dự
án khai vào hàng rào này cả đường dẫn lẫn từ khoá cho cấu trúc DB và xoá dữ liệu; chạm là diff khớp đường dẫn **hoặc**
nội dung bead khớp từ khoá của hàng rào này (D92). Điều này MUST NOT có nút ở bất kỳ đâu.

#### Scenario: Tắt nút hàng rào vẫn chặn migration
- **GIVEN** nút "hàng rào" của dự án tắt
- **WHEN** diff của bead khớp đường dẫn hàng rào `schema`
- **THEN** trạm không merge; lý do "cấu trúc DB — luôn chờ Đại ca"

#### Scenario: Việc nói tới xoá dữ liệu
- **GIVEN** hàng rào `schema` của dự án có từ khoá "xoá dữ liệu"
- **WHEN** mô tả bead nhắc "xoá dữ liệu khách cũ", diff không khớp đường dẫn nào
- **THEN** trạm không merge; lý do "xoá dữ liệu — luôn chờ Đại ca"

### Requirement: Thiếu điều kiện thì chờ Đại ca và nói rõ vì sao
Bead ở cột 3 không được tự merge SHALL ở lại cột 3 cho Đại ca xử lý như hôm nay (Duyệt, Trả về, merge tay trên
GitHub). Dashboard MUST hiện từng điều kiện còn thiếu của bead bằng lời thường.

#### Scenario: Thiếu hai điều kiện
- **WHEN** bead có CI đỏ và chạm hàng rào `khach_thay`
- **THEN** dashboard hiện bead trong danh sách "chờ Đại ca" với hai lý do "CI chưa xanh", "chạm hàng rào: thứ khách thấy"

#### Scenario: Đại ca merge tay
- **WHEN** Đại ca tự merge PR trên GitHub
- **THEN** trạm xác minh merge và đóng bead như luật hiện hành (spec 4 §6.5)

### Requirement: Feature vẫn qua duyệt spec
Bead `feature` SHALL vẫn dừng ở bước duyệt spec của Đại ca (điểm dừng #1). Bead con của feature đã được duyệt spec
SHALL được tự merge theo đúng các điều kiện trên như mọi bead khác (D72). Feature cha MUST NOT được trạm tự đóng.

#### Scenario: Con của feature đã duyệt
- **GIVEN** feature `rn-10` đã được Đại ca duyệt spec, con `rn-11` vào cột 3 đủ điều kiện
- **WHEN** vòng tick xét tự merge
- **THEN** trạm merge PR của `rn-11`

#### Scenario: Feature chưa duyệt spec
- **WHEN** feature còn nhãn `cho-duyet-spec`
- **THEN** không có gì của feature đó được tự merge

### Requirement: Tự gộp PR spec đã được Đại ca duyệt
Khi công tắc tự merge của dự án bật, Đại ca đã bấm Duyệt spec trên dashboard và trạm đã mở PR `tram/spec-<feature>`,
trạm SHALL tự merge PR đó (D95). Năm điều kiện của việc code không áp; trạm MUST chỉ merge khi đầu PR đúng commit
trong lần duyệt mới nhất, và vẫn tôn trọng khoá ghi, TẠM DỪNG, estop như mọi lần tự merge.

#### Scenario: Duyệt spec xong thì PR spec tự vào nhánh chính
- **GIVEN** công tắc tự merge của `repo-nhap` bật, Đại ca duyệt spec của feature `rn-10` tại commit `s1`, PR spec trỏ `s1`
- **WHEN** vòng tick kế tiếp chạy
- **THEN** trạm merge PR spec, báo Telegram; khi `s1` đã vào nhánh chính, các việc con của `rn-10` được giao như luật hiện hành

#### Scenario: Nhánh spec đổi sau khi duyệt
- **WHEN** đầu PR spec khác commit trong lần duyệt mới nhất
- **THEN** trạm không merge; PR chờ Đại ca

#### Scenario: Công tắc tắt
- **WHEN** công tắc tự merge của dự án tắt
- **THEN** PR spec chờ Đại ca merge như hôm nay

### Requirement: Merge rồi xác minh như luồng hiện có
Trạm SHALL merge bằng merge commit thường (không squash, không rebase) để luồng xác minh merge hiện có kiểm được.
Sau khi merge, trạm SHALL chỉ đóng bead khi xác minh được như spec 4 §6.5; không xác minh được thì bead ở lại cột 3
cho Đại ca.

#### Scenario: Merge xong, xác minh đạt
- **WHEN** trạm merge PR của bead `rn-7` tại commit `c1`
- **THEN** trạm ghi sự kiện tự merge, xác minh `c1` nằm trên nhánh chính, rồi đóng bead

### Requirement: Không merge lặp, đối soát khi kết quả không rõ
Mỗi lần tự merge SHALL mang một mã thao tác cố định theo (dự án, bead, commit) và được ghi trước khi gọi GitHub.
Kết quả không rõ (lỗi mạng, trạm tắt giữa chừng) thì trạm MUST đọc lại trạng thái PR trước khi làm gì tiếp.

#### Scenario: Trạm tắt ngay sau lệnh merge
- **GIVEN** trạm đã ghi bắt đầu tự merge `rn-7` rồi tắt trước khi nhận kết quả
- **WHEN** trạm chạy lại
- **THEN** trạm đọc PR: đã merge thì đi tiếp bước xác minh; còn mở và vẫn đủ điều kiện thì gửi lại đúng lệnh merge với cùng commit; không bao giờ merge commit khác

### Requirement: Kiểm lại công tắc ngay trước lúc merge
Ngay trước khi gửi lệnh merge, trạm SHALL đọc lại công tắc dự án, nút điều kiện, trạng thái TẠM DỪNG của dự án và
toàn trạm, estop. Một trong số đó chặn thì MUST NOT merge.

#### Scenario: Đại ca bấm tạm dừng giữa vòng tick
- **WHEN** Đại ca bấm TẠM DỪNG dự án sau khi trạm xét điều kiện xong nhưng trước lệnh merge
- **THEN** trạm không merge

### Requirement: Báo Telegram mỗi lần tự merge
Mỗi lần tự merge thành công SHALL sinh một tin Telegram (D78); trong giờ yên lặng tin này được gom gửi sau giờ yên
lặng (D98). Tin MUST chỉ có tên dự án, mã bead, loại tin và link dashboard — không tiêu đề bead, không nội dung
nghiệp vụ, không SHA hay URL PR.

#### Scenario: Tin tự merge
- **WHEN** trạm tự merge PR của bead `rn-7` dự án `repo-nhap`
- **THEN** Telegram nhận một tin dạng "repo-nhap · 1 tự merge (rn-7) → <link dashboard>"
