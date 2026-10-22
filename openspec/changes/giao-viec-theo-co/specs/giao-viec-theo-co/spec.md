## ADDED Requirements

### Requirement: R1 — Chấm bằng luật đếm
Hệ thống SHALL dùng một kết quả cỡ (`nho`, `vua`, `lon`) để chọn cả model và
quy trình, không gọi LLM. Priority chỉ quyết định thứ tự/quota, không đo độ khó.
Chữ trong bead không cấp quyền hay bỏ cổng.

Phạm vi là hợp file dự kiến trong khối `pham-vi-co:v1` của `design` và diff do
trạm xác minh. SHALL đếm file khác nhau, nhóm mã khác nhau và dòng tiêu chí
không rỗng theo luật hiện có; quy ước chi tiết ở design §1. Thiếu/sai phạm vi,
nhóm chưa biết hoặc thiếu tiêu chí là thiếu dữ liệu, không coi là số 0.

| Điều kiện, xét từ trên xuống | Cỡ tự động |
| --- | --- |
| Nguy hiểm; hoặc ≥9 file, ≥3 nhóm mã, ≥9 tiêu chí | Lớn |
| Đủ dữ liệu; 1–2 file, 0–1 nhóm, 1–3 tiêu chí; phụ thuộc đã rõ và không chặn | Nhỏ |
| Còn lại | Vừa |

Hệ thống MUST giữ sàn lớn cho kill list, đường cấm/bắt buộc, hàng rào, nhãn
nguy hiểm ở design §1 và tác động từ 3 nhóm mã. Thiếu dữ liệu đặt sàn vừa,
không che tín hiệu lớn đã biết. Thiếu bộ bảo vệ bắt buộc thì chờ. Được phép
sửa đường nhạy cảm không xoá sàn nguy hiểm hay thay duyệt nguy hiểm.

#### Scenario: S1 — Đếm và ranh giới
- **WHEN** dữ liệu đầy đủ, không nguy hiểm có (file, nhóm, tiêu chí) lần lượt
  (2,1,3), (3,1,3), (8,2,8), (9,2,8), (3,3,3), (2,1,9)
- **THEN** cỡ là nhỏ, vừa, vừa, lớn, lớn, lớn; file khai lặp chỉ đếm một lần.
  Cùng đầu vào cho cùng kết quả; đổi priority không đổi cỡ.

#### Scenario: S2 — Thiếu dữ liệu hoặc nguy hiểm
- **WHEN** thiếu phạm vi và có 2 tiêu chí, hoặc có 9 tiêu chí, hoặc chạm
  `tram/api/bao_mat.py`
- **THEN** cỡ lần lượt là vừa, lớn, lớn; ghi lý do và phần chưa biết.
  Thiếu bộ bảo vệ bắt buộc thì chưa giao; chữ “bỏ QC” không thay luật.

### Requirement: R2 — Đại ca chỉ nâng cỡ
Theo QĐ4-C, hệ thống SHALL đọc nhãn `co:vua`/`co:lon` trên Beads làm mức sàn;
cỡ dùng là mức cao nhất giữa cỡ tự động và sàn nhãn. Đại ca thêm nhãn qua cơ
chế Beads sẵn có. `co:nho` không hạ cỡ; nhiều nhãn lấy mức cao nhất. Không có
thao tác hạ cỡ hay trả tự động trong bản đầu; agent không được tự sửa nhãn cỡ.
Nhãn không tự hết hiệu lực khi nội dung/luật đổi, không mở cổng hay tăng ngân sách.
Thay nhãn áp dụng khi cấp lượt tiếp theo, không sửa phiếu đang chạy.

#### Scenario: S3 — Nâng bằng nhãn
- **WHEN** việc tự chấm nhỏ có `co:vua`, hoặc tự chấm lớn có `co:vua`/`co:nho`
- **THEN** cỡ dùng lần lượt là vừa và lớn; cùng có `co:lon` thì luôn lớn.
  Nhãn còn nguyên sau khi đổi nội dung hoặc luật; lượt đã cấp giữ nguyên cỡ.

### Requirement: R3 — Model và quy trình cùng theo cỡ
Hệ thống SHALL áp dụng bảng sau cho các bước cần agent:

| Cỡ | Model | Trước code | Sau code |
| --- | --- | --- | --- |
| Nhỏ | Sonnet | Đủ yêu cầu/tiêu chí; code thẳng | Test liên quan + lệnh bắt buộc → kiểm lại cách ly → QC |
| Vừa | Opus | Plan ngắn được Đại ca duyệt | Code → test liên quan + lệnh bắt buộc → kiểm lại cách ly → QC |
| Lớn | Opus | Plan đầy đủ được duyệt → review chéo đạt, tối đa 3 vòng | Code → cả bộ test → kiểm lại cách ly → QC |

Hệ thống SHALL mặc định effort nhỏ `medium`, vừa/lớn `high`, cho chỉnh
`effort_nho`/`effort_vua`/`effort_lon` trong `theo_co` chỉ bằng `low`/`medium`/`high`/`xhigh`/`max`
và vẫn từ chối khoá lạ, lưu effort yêu cầu cùng model trong `co` theo lượt và ép `--effort` cạnh `--model`,
xác nhận effort như model nếu stream-json công bố (thiếu thì chỉ lưu yêu cầu), giữ argv cũ khi không có `co`
hoặc không có effort trong phiếu cũ và không đổi Codex/máy từ xa.

Plan ngắn gồm mục tiêu, phạm vi, cách sửa, tiêu chí/lệnh kiểm, rủi ro/đường lui;
không cần mã nguyên văn. Plan đầy đủ theo playbook. Review khác khe viết plan;
QC khác mọi khe từng code bead. Kết luận duyệt/review gắn đúng bản plan; đổi
plan phải duyệt/review lại phần bị đổi. Một vòng là một kết luận review hoàn
tất; sửa plan hoặc đổi reviewer không đặt lại bộ đếm. Hết 3 vòng chưa đạt MUST
chờ Đại ca, không tự coi đạt. Không tăng ngân sách vì quy trình dài hơn.

#### Scenario: S4 — Nhỏ và vừa
- **WHEN** việc nhỏ đủ điều kiện, hoặc việc vừa chưa có plan ngắn được duyệt
- **THEN** việc nhỏ được code thẳng; việc vừa phải chuẩn bị/duyệt plan trước.
  Cả hai vẫn phải test, kiểm lại và QC.

#### Scenario: S5 — Ba vòng review
- **WHEN** review đạt ở vòng 1, hoặc cả 3 vòng đều chưa đạt
- **THEN** trường hợp đầu không review thêm; trường hợp sau dừng hỏi Đại ca,
  không chạy vòng 4. Gửi lại cùng kết luận không tính thêm vòng.

### Requirement: R4 — Giữ cổng và kiểm độc lập
Hệ thống MUST giữ INV-001…INV-006, phụ thuộc, duyệt spec và spec cha đã merge,
estop, khoá ghi, quyền vai, cổng nguy hiểm và kiểm toàn bộ sau ghép. Không tự
giao code cho epic/decision. Con được chấm riêng nhưng không né nguy hiểm đã
biết từ phạm vi cha. Thiếu dữ liệu phải làm rõ trong plan rồi chấm lại trước code.

QC SHALL kiểm yêu cầu/diff/test với nhỏ, thêm plan ngắn với vừa, đối chiếu mã
nguyên văn plan với lớn. Không bớt lệnh kiểm bắt buộc; lớn thiếu lệnh cả bộ thì
chờ. Chỉ bật nhánh gọn sau khi đồng bộ luật plan/QC hiện hành theo QĐ2-A.

#### Scenario: S6 — Cổng chưa đạt
- **WHEN** spec cha chưa merge, estop bật, dự án khoá ghi hoặc kiểm lại hỏng
- **THEN** chặn theo luật hiện hành ở mọi cỡ; kiểm lại hỏng không đi tiếp QC.
  Việc lớn thiếu lệnh cả bộ cũng chưa được giao code.

### Requirement: R5 — Chờ khe đúng model
Hệ thống SHALL lọc khe theo model hỗ trợ, cổng/quota/vai/ngân sách và tính độc
lập trước khi áp ưu tiên khe. Model không thay danh tính khe. Thiếu khe đúng
model MUST chờ, không claim mới, không giữ ngân sách mới hay đổi model/cỡ.
Không tự coi Codex tương đương Opus/Sonnet. Quản lý thợ phải ép model của phiếu;
adapter phải xác nhận model thực chạy, không tin lời tự khai trong bàn giao.

#### Scenario: S7 — Thiếu khe hoặc sai model
- **WHEN** khe ưu tiên sai model nhưng có khe hợp lệ đúng model, hoặc không còn khe đúng model
- **THEN** chọn khe đúng ở trường hợp đầu; trường hợp sau báo chờ Opus/Sonnet.
  Không ép/xác nhận được model thì báo lỗi, thu hồi theo cơ chế hiện hành.

#### Scenario: S8 — QC thiếu người khác
- **WHEN** chỉ còn khe từng code bead hỗ trợ model yêu cầu
- **THEN** QC chờ; đổi model hoặc vai của khe đó không làm nó thành người kiểm độc lập.

### Requirement: R6 — Lưu quyết định theo lượt
Hệ thống SHALL lưu cùng lần cấp phiếu: dự án/bead/phiếu/lượt, cỡ tự động, sàn
nhãn/nguy hiểm, cỡ dùng, số đếm/phần thiếu, mã lý do, bản luật, model yêu cầu và
quy trình. Gắn model thực chạy, kết quả test/QC, thời gian và số lượt làm lại
khi có; chưa đo thì ghi chưa biết. Không lưu nguyên văn bead/prompt/bí mật.

Không lưu được quyết định MUST không cấp phiếu. Phiếu đã cấp giữ bản cũ qua
khởi động lại; lượt cũ vẫn bị từ chối. Trước cấp lượt tiếp theo đọc lại dữ liệu
và chấm lại. Diff mở rộng phạm vi phải giữ chờ để xác nhận, chấm lại và hoàn
thành plan/review/cổng còn thiếu trước QC/công bố; kiểm chứng luôn theo đúng commit.

#### Scenario: S9 — Phạm vi lớn lên
- **WHEN** việc nhỏ có diff thêm file nhạy cảm ngoài khai báo
- **THEN** giữ lịch sử lượt cũ; bước sau chờ, chấm lớn và đáp ứng quy trình lớn.
  Sửa khai báo không xoá file đã có trong diff.

#### Scenario: S10 — Lưu và khôi phục
- **WHEN** lưu quyết định thất bại, hoặc trạm khởi động lại sau cấp thành công
- **THEN** không cấp ở trường hợp đầu; trường hợp sau đọc đúng bản đã lưu,
  không cấp trùng hay nhận báo cáo lượt cũ.

### Requirement: R7 — Chỉnh ngưỡng sau khi có số liệu
Hệ thống SHALL đọc ngưỡng và ánh xạ của dự án từ `du-an/<ten>.yaml`, nhận diện
bản luật đã dùng. Đại ca chỉnh cấu hình; không tự học, không gọi LLM chấm cỡ.
Ngưỡng là số nguyên dương, ngưỡng nhỏ không vượt vừa; cấu hình sai thì báo lỗi
và chờ. Không cho cấu hình bỏ sàn nguy hiểm/bảo vệ chung hoặc nới quota.

#### Scenario: S11 — Luật mới chỉ áp dụng lượt mới
- **WHEN** Đại ca đổi ngưỡng hợp lệ, hoặc cấu hình sai
- **THEN** bản hợp lệ áp dụng việc chưa chạy/lượt tiếp theo, không viết lại
  lịch sử; bản sai chặn giao. Nhãn nâng vẫn là sàn, không tự mất hiệu lực.
