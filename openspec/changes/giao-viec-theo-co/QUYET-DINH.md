# Đã chốt 20/10/2026

Theo quyết định của Đại ca trong chat:

| Mục | Chọn | Nội dung |
| --- | --- | --- |
| QĐ1 | A | Đếm file, nhóm mã, tiêu chí; giữ sàn nguy hiểm; thiếu dữ liệu ít nhất vừa. |
| QĐ2 | A | Nhỏ code thẳng; vừa plan ngắn; lớn plan đầy đủ, review chéo tối đa 3 vòng. Mọi cỡ giữ test, kiểm lại và QC. |
| QĐ3 | A | Nhỏ Sonnet, vừa/lớn Opus; thiếu khe đúng model thì chờ. |
| QĐ4 | C | Chỉ nâng cỡ bằng nhãn Beads `co:vua`/`co:lon` làm mức sàn. Không hạ, không UI/mockup hay API riêng. |
| QĐ5 | A | Đại ca chỉnh ngưỡng theo dự án sau khi xem số liệu; bản mới không sửa lịch sử lượt cũ. |

Chọn nhãn vì Beads đã có trường nhãn và cơ chế cập nhật, không cần thêm lệnh
hay cửa ghi mới. Cỡ dùng lấy mức cao hơn giữa luật tự chấm và nhãn.

Điều kiện đã chốt: plan TDD chỉ viết **sau khi change `doi-ngu-tho` ghép main**,
dựa trên nền khe và lệnh chạy của change đó. Khi chốt 20/10 chưa plan/code;
review 21/10 đã đối chiếu nền này trên HEAD `51ec56f`. Không thay QĐ1–QĐ5.

**21/10 Đại ca thêm effort theo cỡ**: nhỏ `medium`, vừa/lớn `high`; chỉnh qua
`effort_nho`/`effort_vua`/`effort_lon` trong `theo_co`, chỉ nhận `low`, `medium`, `high`, `xhigh`, `max`.
Lưu yêu cầu cùng model trong `co` theo lượt và ép `--effort` cạnh `--model`; phiếu cũ thiếu effort vẫn chạy.
Stream không công bố effort thì chỉ lưu yêu cầu, không coi là đã xác nhận thực chạy; Codex/máy từ xa không đổi.
