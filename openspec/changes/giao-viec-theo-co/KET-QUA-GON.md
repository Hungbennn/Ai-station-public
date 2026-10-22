# Kết quả chốt và cắt gọn spec — 20/10/2026

Đại ca, Bé đã sửa 5 tài liệu của change `giao-viec-theo-co` trên nhánh
`spec/giao-viec-theo-co`, từ bản `ea8a2da`. Chốt QĐ1=A, QĐ2=A, QĐ3=A,
QĐ4=C, QĐ5=A; chưa viết plan hay code.

- Chọn nhãn Beads `co:vua`/`co:lon` làm mức sàn vì trường nhãn và cách cập
  nhật đã có. Chỉ nâng; nhãn thấp hơn không hạ cỡ tự chấm. Lượt đang chạy
  giữ nguyên, nhãn được đọc khi cấp lượt tiếp theo.
- Bỏ API POST/GET riêng, revision/409/mã thao tác, nút trả tự động, UI/mockup,
  sửa tay hết hiệu lực theo dấu vân tay, chuẩn hoá Unicode/gộp hoa thường và
  các tình huống phụ ít gặp.
- Giữ đếm file/nhóm/tiêu chí, sàn nguy hiểm, thiếu dữ liệu ít nhất vừa,
  cỡ→model→quy trình, chờ khe đúng model, tối đa 3 vòng review, kiểm lại
  cách ly, QC khác khe, lịch sử theo lượt, ngưỡng theo dự án; không LLM chấm.
- Ghi rõ plan TDD chỉ viết sau khi `doi-ngu-tho` ghép main, dựa nền khe/lệnh
  chạy của change đó. Luật plan/QC chung cần đồng bộ trước khi bật nhánh gọn.

Đếm chữ bằng tách khoảng trắng, cùng cách cho bản gốc và bản sau:

| Tài liệu | Trước | Sau |
| --- | ---: | ---: |
| spec.md | 3.303 | 1.544 |
| design.md | 2.566 | 1.016 |
| QUYET-DINH.md | 932 | 207 |
| proposal.md | 531 | 333 |
| tasks.md | 370 | 264 |
| Tình huống trong spec | 31 | 11 |

Spec giảm 53%, design giảm 60%. Tình huống đánh số liên tục S1–S11;
`tasks.md` trỏ đủ các nhóm tình huống, bỏ mốc giao diện.

Kiểm chứng:
- `DO_NOT_TRACK=1 OPENSPEC_TELEMETRY=0 openspec validate giao-viec-theo-co --strict`:
  đạt, mã thoát 0, “Change 'giao-viec-theo-co' is valid”.
- Kiểm đường dẫn/liên kết: tất cả tồn tại; mẫu `du-an/<ten>.yaml` được ghi rõ
  là quy ước tên. Kiểm số tình huống: liên tục, không trùng.
- `git diff --check`: đạt. Không chạy test ứng dụng vì chỉ đổi tài liệu;
  không có số passed/failed của ứng dụng để báo.

Không sửa `tram/` hay tài liệu trạng thái; không bd, commit, push hoặc mạng.
Không còn câu hỏi cần Đại ca chốt trong phạm vi này. Các mốc triển khai vẫn
chưa đánh dấu đạt; validate chỉ kiểm định dạng, không chứng minh đã triển khai.
