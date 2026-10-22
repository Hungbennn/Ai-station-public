# Chốt thảo luận agent tự cập nhật việc trong Beads (bs-2bd.5) — 18/10/2026

Đại ca trả lời từng câu, kết thúc bằng "Đủ rồi, viết spec đi". Spec riêng, tách khỏi tự merge/tự deploy (D80). Sửa một
phần ADR-0001 khi spec được duyệt và code xong: trạm vẫn là bên DUY NHẤT ghi Beads; agent chỉ gửi đề nghị.

| # | Câu hỏi | Đại ca chọn |
|---|---|---|
| D81 | Agent được làm gì với Beads | **Ba việc:** (1) ghi tiến độ vào đúng việc của phiếu mình; (2) tạo việc mới phát hiện ra, liên kết với việc gốc; (3) báo "bị chặn"/cần Đại ca kèm lý do. **Không** tự đóng việc (vẫn chỉ đóng sau khi trạm xác minh code đã gộp), **không** sửa mô tả/ưu tiên, **không** đụng việc khác. |
| D82 | Đường ghi | **Agent gửi đề nghị qua trạm** (bàn giao hoặc API thợ có khoá máy); trạm kiểm đúng việc của phiếu, đúng loại thao tác, không chứa bí mật rồi trạm ghi. Agent không có quyền `bd` trực tiếp (ADR-0001, INV-002). |
| D83 | Việc mới do agent tạo | **Nhãn "do agent tạo" + liên kết việc gốc; không tự giao ngay — bộ chấm cột xếp như mọi việc** (chạm hàng rào → cột cần Đại ca chốt); **tối đa 5 việc mới mỗi phiếu.** |
| D84 | Khi nào trạm ghi | **Tiến độ và "bị chặn" ghi ngay** trong lúc agent làm (qua API thợ); **việc mới ghi cuối lượt, sau khi QC + kiểm lại đạt.** |
| D85 | Bật/tắt | **Mỗi dự án một nút, mặc định TẮT, 3 nút con** (tiến độ / việc mới / bị chặn); chỉnh trên dashboard, chung màn cài đặt tự merge/deploy (cần mockup). |
| D86 | Báo Đại ca | **Telegram khi "bị chặn" và khi có việc mới (gộp 1 tin/lượt)**; tiến độ chỉ hiện trên dashboard. |

## Chốt câu hỏi mở của spec `agent-tu-cap-nhat-viec` (18/10)

| # | Câu hỏi (design.md) | Đại ca chọn |
|---|---|---|
| D102 | "Bị chặn" | **Dùng đường `tram bao --bi/--can-hoi` có sẵn**; việc "Bí: …" vẫn luôn tạo; nút con chỉ quyết có ghi thêm dòng "bị chặn" vào việc đang làm. |
| D103 | Việc mới từ lượt không đạt; phiếu spec/spike | **Lượt không đạt → bỏ đề nghị việc mới.** Phiếu viết spec không được đề nghị việc mới; phiếu spike được, ghi sau khi kiểm tài liệu đạt. |
| D104 | Agent chọn gì cho việc mới | **Loại (bug/task/chore) + tiêu chí nghiệm thu; không chọn ưu tiên** (mặc định P2). |
| D105 | 3 nút con khi bật nút dự án | **Bật sẵn** (nút dự án vẫn mặc định tắt). |
| D106 | Giới hạn chữ | Tiến độ 1.000 ký tự, lý do bị chặn 2.000, tiêu đề 200, mô tả 4.000, tiêu chí 2.000; **tối đa 20 dòng tiến độ mỗi phiếu.** |
| D107 | Đề nghị tới lúc Estop | **Giữ lại trong hàng đợi, ghi sau khi tắt Estop.** |
| D108 | Bật nút dự án | **Hỏi xác nhận một lần.** |
| D109 | Thử `bd dep add --type discovered-from` | **Cho thử trên một kho Beads tạm** (thư mục tạm, xoá sau; không đụng kho thật). |
| D110 | Kênh ghi `header` còn tạm | Theo D87: chỉ cho TẠM DỪNG tới khi có `unix-socket`. |
| D111 | Lỗ quét bí mật ở lý do "bí" (INV-001) | Sửa riêng, bead `bs-2bd.1.27` (P1). |
| D113 | Kênh ghi `header` còn tạm — tính năng không có nút Tạm dừng | **Khoá mọi thao tác BẬT/chỉnh; TẮT nút dự án vẫn được.** Đại ca duyệt bản spec đã sửa (mốc 0.1b) 18/10 → viết plan. |

## Chốt câu hỏi của plan TC (18/10, Đại ca trả lời từng câu)

| # | Câu hỏi | Đại ca chọn |
|---|---|---|
| D131 | Báo Telegram khi nút "agent tự cập nhật việc" đổi | **Chưa báo** ở lát này (lịch sử đổi vẫn trên dashboard). |
| D132 | Tin "việc mới do agent tạo" trong giờ yên lặng | **Gom, gửi buổi sáng** (thêm loại vào `GOM_SAU_YEN_LANG` — sửa plan TC). |
| D133 | Lọc bí mật lý do "bị chặn" khi nút tắt | **Giữ D111**, sửa riêng ở `bs-2bd.1.27`. |
| D134 | Khoá ghi giữa chừng rồi mở lại: đề nghị đang chờ | **GHI BÙ** (khác đề xuất — sửa plan TC: đề nghị chờ giữ nguyên khi `bat_ghi` tắt, ghi khi mở lại; vẫn kiểm lại nút + `bat_ghi` + estop ngay trước khi ghi). |
