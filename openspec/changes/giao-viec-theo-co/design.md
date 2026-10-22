# Thiết kế bản đầu

Đã chốt 20/10/2026: QĐ1=A, QĐ2=A, QĐ3=A, QĐ4=C, QĐ5=A.
Đây là hợp đồng hành vi. Cách làm và mã nguyên văn ở
[plan TDD](../../../docs/plans/2026-10-21-giao-viec-theo-co.md);
bằng chứng review độc lập ở [REVIEW-PLAN-1.md](REVIEW-PLAN-1.md).

## 1. Đếm đơn giản, giữ sàn an toàn

Phạm vi dự kiến dùng trường `design` sẵn có của Beads: khối duy nhất mở bằng
`<!-- pham-vi-co:v1 -->`, đóng bằng `<!-- /pham-vi-co -->`, mỗi dòng ở giữa
là `- đường/tương/đối`. Thiếu/rỗng/sai khối thì chưa biết phạm vi; không đoán
file từ văn xuôi. Đường từ gốc repo, bỏ `./`, gộp tên trùng chính xác; không
đọc đường tuyệt đối, `..` hoặc glob. Cho phép khai file mới chưa tồn tại.

Đếm cả file thêm/sửa/xoá, test/docs; đổi tên tính tên cũ và mới. Dùng hợp file
khai và diff thật trạm xác minh theo SHA. Không có chuẩn hoá Unicode hay gộp
hoa thường. Tiêu chí đếm dòng sau bỏ đầu mục/khoảng trắng/dòng rỗng bằng luật
ở `tram/giao_viec/tieu_chi.py`.

Nhóm mã theo tiền tố dài nhất trong cấu hình: ben-station mỗi package dưới
`tram/` một nhóm, mỗi module ngay gốc `tram/` một nhóm; `frontend/src/` một
nhóm. `tests/`, `docs/`, `openspec/` là phụ trợ, chỉ tăng số file. Đường khác
chưa có ánh xạ thì thiếu dữ liệu. Không lấy từ vựng nghiệp vụ làm tên nhóm.

Nguy hiểm gồm kill list dự án, đường cấm/bắt buộc, kết quả hàng rào, nhãn
`co-do`, `rui-ro:bao-mat`, `rui-ro:he-thong`, `rui-ro:kien-truc`, `rui-ro:du-lieu`.
Bộ bảo vệ ben-station phải phủ `docs/AGENT_RULES.md` §2 trước khi bật nhánh gọn.
Sàn lớn khi nguy hiểm hoặc từ 3 nhóm mã; thiếu dữ liệu ít nhất vừa. Bảng ngưỡng
ở spec R1; không coi số file là cách hiểu hết rủi ro kiến trúc.

Ngưỡng, ánh xạ nhóm, mẫu nguy hiểm và model nằm trong khối cấu hình mới của
`du-an/<ten>.yaml` (mẫu tên file, chưa phải file cụ thể). Mỗi bản hiệu lực có
mã nhận diện gồm mặc định và cấu hình dự án. Sai cấu hình thì chờ; cấu hình
không được xoá bảo vệ chung hoặc nới quota. Chưa có số liệu thì dùng ngưỡng đã
chốt; Đại ca xem kết quả/lượt làm lại/thời gian rồi chỉnh, không tự học.

## 2. Nâng bằng nhãn sẵn có

Chọn `co:vua`/`co:lon` làm sàn do Đại ca đặt qua Beads. Cỡ dùng = mức cao nhất
giữa tự chấm và nhãn; `co:nho` không có tác dụng hạ. Đại ca chỉ thêm/nâng nhãn,
không dùng xoá/thay nhãn để hạ cỡ trong quy trình này. Agent không tự sửa nhãn.
Nhãn còn hiệu lực đến các lượt sau, không hết hiệu lực vì dữ liệu/luật đổi.

Cơ chế đã có ở `tram/beads/mo_hinh.py` (`labels`) và `tram/beads/bd.py`
(`cap_nhat_nhan`); không cần thêm lệnh trạm, kho sửa tay hay xác thực mới.
Trạm đọc nhãn khi cấp lượt mới; thay trong lúc chạy không sửa phiếu đã cấp.
Không ghi cỡ tự chấm ngược vào Beads: nhãn là đầu vào, lịch sử lượt là kết quả.

Bản đầu không có giao diện hoặc mockup, không thêm API đọc/ghi cỡ. Dashboard
chưa có nhu cầu riêng buộc mở GET; lịch sử dùng kho sự kiện hiện có.

## 3. Chọn khe và giữ quy trình

`tram/giao_viec/chon.py` hiện chọn theo hạn mức/vai/khe đã code; cần thêm lọc
khả năng model trước ưu tiên. Khe vẫn là máy/CLI/tài khoản, có thể hỗ trợ cả
Sonnet và Opus. Không gán cố định mỗi khe một model; thiếu khe QC đúng model
thì chờ. Không tự coi Codex tương đương. Model yêu cầu nằm trong phiếu, quản
lý thợ ép lựa chọn và adapter xác nhận model thực chạy.

Ba quy trình theo spec R3. Review plan khác khe viết, tối đa 3 kết luận, không
reset khi sửa plan; đạt sớm thì dừng review. QC luôn khác mọi khe từng code.
Plan thiếu phạm vi phải làm rõ rồi chấm lại trước code. Diff mở rộng phải
đối chiếu phạm vi và bổ sung các bước còn thiếu trước khi tiếp tục.

QĐ2-A thay yêu cầu mọi việc có plan nguyên văn trong `docs/AGENT_RULES.md`
§3/§13, `docs/ENGINEERING_STANDARDS.md`, `docs/DEVELOPMENT_PLAYBOOK.md` §1–4,
`docs/OPENSPEC.md`. Task 6 của plan thay đúng câu luật cũ tại nơi sở hữu;
không thêm phụ lục lặp lại hay luật ngoài QĐ2-A. Đồng bộ trước khi bật
nhánh gọn. Giữ duyệt spec, cổng nguy hiểm, kiểm lại
cách ly, QC và kiểm toàn bộ sau ghép. Không tự bật giao việc.

## 4. Lưu theo lượt và ranh giới triển khai

`giao_viec` chấm một lần cho cả model/quy trình; `phieu` và `su_kien` giữ bản
quyết định cùng lần cấp. Lưu không được thì không cấp. Đọc lại dữ liệu trước
lượt tiếp theo, giữ nguyên bản của phiếu đang chạy và lịch sử; không cần dấu
vân tay phạm vi hay kho sửa tay riêng. Gắn test/QC với đúng commit, không lưu
nguyên văn bead/prompt hoặc bí mật. Phiếu cũ chưa có cỡ đi hết quy trình cũ,
không gán cỡ hồi tố.

| Vùng dự kiến | Trách nhiệm |
| --- | --- |
| `tram/giao_viec/` | Chấm cỡ, chọn khe, quy trình và điều kiện chờ |
| `tram/phieu/`, `tram/su_kien/` | Quyết định theo lượt, ngân sách và lịch sử |
| `tram/cau_hinh/`, `tram/tho/`, `tram/chay_cli/` | Ngưỡng, khả năng khe và model thực chạy |
| `vai/` | Chỉ dẫn plan/code/QC theo cỡ, không đổi quyền |

Không thêm bảng DB, dependency, dịch vụ hay tích hợp ngoài. Đọc Beads dùng
hạn 120 giây hiện có; Git cục bộ dùng runner có hạn tối đa 60 giây; lỗi đọc
thì chờ, nhịp sau thử lại. CLI theo ngân sách phiếu, lỗi model/hạn mức dùng
thu hồi hiện có; không tự đổi model hoặc log đầu ra thô.

Plan đã đối chiếu nền khe và lệnh chạy đội ngũ thợ trên HEAD `51ec56f`.
Change đó giữ việc cài/đăng nhập/đăng ký thợ và quyền Git; ở đây
không quyết định lại. Khi triển khai, kiểm luật bằng dữ liệu giả; model thực
chạy và cách ly phải có bằng chứng ở cổng chạy thật được Đại ca cho phép.
Đường lui: ngừng cấp theo chính sách mới ở ranh giới phiếu, trở về quy trình
đầy đủ, giữ lịch sử và mọi cổng đang chặn.
