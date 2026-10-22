# PROJECT — ben-station (Trạm điều phối)

Project: `ben-station`
Status: `ACTIVE`
Cập nhật: `2026-10-17`

## Mục đích và sở hữu
Sở hữu: sản phẩm là gì, cho ai, phạm vi, non-goals, tầm nhìn. Nguồn: câu trả lời của Đại ca 17/10/2026.
Không sở hữu: từ vựng và bất biến (`PRODUCT_ARCHITECTURE.md`), bản đồ kỹ thuật (`ARCHITECTURE.md`), việc (Beads).

## Là gì
Một **trạm điều phối riêng của Đại ca**: phần mềm chạy trên Mac của Đại ca, thay Đại ca điều khiển nhiều
**agent AI** (chương trình AI tự viết code, như Claude Code và Codex) làm việc trên **nhiều dự án**, bằng
**nhiều tài khoản AI**, trên **vài máy Mac**.

Trạm tự xếp việc, giao việc cho agent, chạy agent trong vùng **cách ly** (agent không chạm được bí mật hay
máy ngoài phần được cấp), cho một agent khác **kiểm chéo** (QC), mở **PR** (đề nghị gộp code vào nhánh
chính trên GitHub), rồi **dừng ở những điểm cần Đại ca duyệt**.

Đây **không** phải app chat hay trình soạn code. Đại ca vẫn dùng app Claude để thảo luận; trạm lo phần chạy.

## Vấn đề giải quyết
- Hôm nay Đại ca phải **ngồi canh agent** từng bước: giao việc, chờ, kiểm, giao tiếp.
- **Hạn mức** (số lượt dùng AI mỗi tài khoản được phép trong một khoảng thời gian) của các tài khoản không
  được dùng hết, vì không ai giao việc lúc Đại ca vắng.
- Không có một chỗ nhìn toàn bộ việc: việc nào AI tự làm được, việc nào cần Đại ca chốt, việc nào chờ duyệt.

## User chính
- **Đại ca** — người dùng duy nhất giai đoạn này: thảo luận và chốt yêu cầu, duyệt spec, trả lời câu hỏi
  agent, xem kết quả, bấm dừng khẩn cấp khi cần.
- **Agent của trạm** — không phải người dùng mà là "thợ": mỗi agent nhận một vai (viết spec, viết code, QC)
  và chạy dưới tài khoản AI riêng.

## Các cục / luồng chính
**Xếp việc** — đọc danh sách việc của dự án (Beads) và xếp từng việc vào ba cột: AI tự làm · cần Đại ca chốt ·
chờ Đại ca duyệt (suy từ code, chưa xác nhận).

**Giao việc** — chọn agent còn hạn mức, giao việc, theo dõi, thu hồi khi agent treo hay hết lượt.

**Cách ly và kiểm lại** — agent chạy dưới tài khoản máy riêng, không có bí mật; trạm tự chạy lại phần kiểm
trong vùng cách ly trước khi tin kết quả. Kiểm lại lỗi thì dừng.

**Memory chung** — trí nhớ dài hạn cục bộ cho agent theo từng dự án, có bộ lọc bí mật.

**Dashboard và báo tin** — trang web xem việc, đội agent, hạn mức, văn phòng 3D; nút dừng khẩn cấp;
tin ngắn qua Telegram (suy từ code, chưa xác nhận).

**Luồng một feature** (theo spec kiến trúc §5.7 đã duyệt; chi tiết máy A/B ở `ARCHITECTURE.md`):
```
Đại ca thảo luận trên máy A → chốt phiếu yêu cầu → trạm tạo việc
  → agent viết spec + plan → ⏸ Đại ca duyệt spec
  → agent code → agent khác QC → trạm kiểm lại trong vùng cách ly → mở PR
  → ⏸ Đại ca duyệt và merge
```

## Scope hiện tại
- Một người dùng (Đại ca). Chỉ chạy trên Mac của Đại ca.
- Khoảng 80% đã code. Phần còn lại, theo thứ tự ưu tiên Đại ca chốt: **vá lỗi kỹ thuật + dọn code thừa →
  chạy thật** (song song viết spec tự merge và tự deploy) **→ tự merge + tự deploy → chọn model theo độ khó**.
  Việc cụ thể: Beads, epic `bs-2bd`.
- **Tự merge và tự deploy là mục tiêu**, làm sớm: sẽ đổi điểm dừng "Đại ca merge" và luật cấm merge.
  Tới khi spec đó được duyệt, Đại ca vẫn merge.
- Đại ca muốn cho agent **tự cập nhật danh sách việc** (hiện agent không được sửa); cần spec riêng.

## Non-goals
- **Không nhiều người dùng** ở giai đoạn này. Ngoại lệ (D136): cửa ghi bằng passkey (D135) thiết kế sẵn "danh sách
  người + quyền" — hiện chỉ có Đại ca — để giai đoạn trạm chung công ty không phải làm lại.
- **Không chạy trên cloud, Linux hay Windows** — chỉ Mac của Đại ca.
- **Không thay app Claude**: không làm khung chat, không làm IDE.
- **Không tích hợp Jira.**
- Khách hàng bên ngoài **không** thuộc phần việc còn lại (xem Tầm nhìn sau).

## Tầm nhìn sau
**Giai đoạn kế tiếp (D136, Đại ca chốt 18/10/2026): trạm chung cho nhiều người trong công ty.** Sẽ thảo luận và viết
spec riêng (mỗi người: dự án, quyền, hạn mức, dữ liệu và bí mật tách biệt) sau khi tự merge + tự deploy chạy thật.
Tới lúc đó các mục Scope/Non-goals ở trên vẫn đúng.

Sau này trạm có thể có **người dùng bên ngoài (khách hàng)**. Đây là hướng dài hạn, chưa thiết kế, không
được để nó kéo theo kiến trúc nhiều người dùng trong giai đoạn này.
