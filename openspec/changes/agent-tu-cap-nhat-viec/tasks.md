# Tasks

Plan TDD: [lát TC](../../../docs/plans/2026-10-18-lat-tc-agent-tu-cap-nhat-viec.md), được duyệt code theo D151.
Theo Task 13 của plan, chỉ đánh dấu các mốc hoàn tất sau khi lát ghép và cổng 4.2 đạt.
Mỗi mốc dưới đây là một mốc nghiệm thu; mã nguyên văn và test nằm ở plan. Test chạy qua `tests/chan_host/chay.sh -q`,
`bd` và Telegram dùng bản giả.

## 0. Trước khi viết plan

- [x] 0.1 Đại ca trả lời 12 câu hỏi mở (D102–D111); câu trả lời đã chép vào proposal, spec, design — kiểm chứng: `openspec validate agent-tu-cap-nhat-viec --strict` xanh
- [ ] 0.1b Đại ca duyệt bản change đã sửa theo D102–D111 — kiểm chứng: lời duyệt của Đại ca trong chat, ghi vào bàn giao phiên
- [x] 0.2 Thử `bd dep add <mới> <gốc> --type discovered-from` trên kho Beads tạm (D109) — kiểm chứng: kết quả đo nguyên văn ở `design.md` D-5; kho tạm đã xoá
- [ ] 0.3 Mockup chung `docs/mockup/2026-10-18-tu-merge-tu-deploy/` có nhóm nút "agent tự cập nhật việc" và chỗ hiện tiến độ; Đại ca duyệt — kiểm chứng: dòng duyệt của Đại ca ghi trong mockup

## 1. Bộ lọc và nhận đề nghị

- [ ] 1.1 Hàm lọc nội dung (cấu trúc, độ dài, ký tự điều khiển, dấu dành riêng, bí mật) — kiểm chứng: test từng mã lý do của Requirement "Lọc nội dung trước khi nhận", kể cả U+202E, `<!-- ban-giao -->`, token giả; sự kiện từ chối không chứa đoạn chữ
- [ ] 1.2 `tram bao --tien-do` / `--viec-moi` và hàng đợi phía thợ bỏ mã agent tự ghi, lọc sớm — kiểm chứng: test Scenario "Agent tự ghi mã việc khác vào hàng đợi"; quyền vai `coder`/`qc` không đổi (`bd` vẫn bị cấm)
- [ ] 1.3 `POST /api/tho/bao` nhận `tien_do`, `viec_moi`: thẻ chắn lượt, thuộc máy, `request_id`, đếm ≤ 5 việc mới và ≤ 20 tiến độ, phiếu `spec` không được việc mới — kiểm chứng: test Scenario "Dòng tiến độ thứ hai mươi mốt", "Lượt cũ gửi tiến độ" (409), "Khe của máy khác" (403), "Đề nghị thứ sáu", "Gửi lại đề nghị thứ năm", "Cùng mã, khác nội dung", "Đề nghị đóng việc", "Đề nghị kèm trường đổi ưu tiên", "Phiếu viết spec"

## 2. Ghi vào Beads

- [ ] 2.1 Bước ghi trong `vong_nhanh`: tiến độ → dòng ghi chú có tiền tố và dấu mã; kiểm nút và `bat_ghi` ngay trước khi ghi; không chạy khi estop — kiểm chứng: test Scenario "Ghi tiến độ", "Tiến độ đòi chuyển cột", "Tiến độ khi estop", "Khoá ghi giữa chừng", "Bật lại không ghi bù"
- [ ] 2.2 Bị chặn: dòng ghi chú trên việc gốc sau escalation, lý do đã lọc hoặc câu thay thế; escalation không đổi khi nút tắt — kiểm chứng: test Scenario "Báo bị chặn", "Lý do bị chặn có bí mật", "Nút bị chặn tắt"

Tiền đề cho 2.2: Task 1 plan [V5](../../../docs/plans/2026-10-18-lat-v5-va-truoc-chay-that.md) đã áp trên
`code/v5` (chưa commit): escalation quét lý do gốc trước khi cắt, che cả mô tả mới và notes gộp, độc lập
nút tự cập nhật; nhóm escalation/xử lý việc 34 passed, 0 dòng chặn mới. Giữ 2.2 chưa tích vì dòng ghi chú
trên việc gốc và các nút TC chưa được triển khai trong V5.

- [ ] 2.3 Cổng việc mới (lượt trong bằng chứng / lượt không đạt) là hàm thuần đọc sự kiện — kiểm chứng: test từng dòng của D-7 và Scenario "QC đạt", "Kiểm lại không đạt", "Việc spike", "Tắt nút khi việc mới đang chờ QC"
- [ ] 2.4 Tạo việc mới: nhãn `tram:agent-tao`, liên kết "phát hiện từ", không ưu tiên/cha/nhãn cột/nhận việc; đối soát dấu mã sau crash — kiểm chứng: test Scenario "Việc mới được tạo", "Agent gửi kèm ưu tiên", "Loại không cho phép", "Trạm hỏng sau khi tạo việc mới"; test tương tác với bộ chấm cột 1a thật + `bd` giả cho Scenario "Việc mới chạm hàng rào tiền"
- [ ] 2.5 Dữ liệu không tin cậy: việc mới khi được giao nằm trong khối bọc của gói ngữ cảnh — kiểm chứng: test Scenario "Việc mới chứa lệnh cho agent sau"
- [ ] 2.6 Sự kiện đủ dấu vết (nhận, từ chối, đã ghi, bỏ, lỗi ghi) — kiểm chứng: test Scenario "Xem dấu vết của một phiếu"

## 3. Nút, dashboard, báo tin

- [ ] 3.1 Nút theo dự án lưu bằng sự kiện, đọc mặc định, lịch sử — kiểm chứng: test Scenario "Dự án chưa từng chỉnh", "Chỉ tắt việc mới", "Khởi động lại trạm"
- [ ] 3.2 Tuyến ghi cài đặt dưới cửa ghi sẵn có — kiểm chứng: test yêu cầu **thiếu** và **giả** danh tính → 403; Scenario "Gửi lại cùng mã thao tác", "Màn hình cũ" (409), "Dự án chỉ quét thử" (422), "Kênh header"; dashboard hỏi xác nhận khi bật (Scenario "Bật nút dự án")
- [ ] 3.3 Hướng dẫn trong vai `coder`/`qc` và gói ngữ cảnh lớp 2 chỉ cho loại đang bật — kiểm chứng: test dựng gói với từng tổ hợp nút
- [ ] 3.4 Telegram: tin escalation dùng lại cho bị chặn (không tin thứ hai); loại tin mới gộp việc mới; không Telegram cho tiến độ — kiểm chứng: test với Telegram giả cho Scenario "Báo bị chặn", "Ba việc mới", "Agent ghi năm dòng tiến độ"; tin không chứa chữ của agent
- [ ] 3.5 Giao diện theo mockup đã duyệt (nút trên trang cài đặt chung, tiến độ ở việc) — kiểm chứng: `npm run kiem && npm run build && npm run kiem-dist`; mở dưới CSP thật với dữ liệu giả; Scenario "Xem khi không phải Đại ca"

## 4. Nghiệm thu tích hợp và chạy thật

- [ ] 4.1 Kịch bản giả lập đầu-cuối (thợ giả, `bd` giả, remote Git giả): code → tiến độ → đề nghị 2 việc mới → kiểm lại → QC đạt → cột 3 → 2 việc mới + 1 tin; và nhánh bị chặn → escalation + dòng ghi chú — kiểm chứng: test đầu-cuối xanh, 0 dòng chặn mới
- [ ] 4.2 Chạy thật trên repo nháp theo cổng mới trong sổ tay, mỗi kịch bản Đại ca cho phép một lần — kiểm chứng: bằng chứng (lệnh, giờ, kết quả) ghi vào sổ tay
- [ ] 4.3 ADR mới thay một phần ADR-0001; cập nhật `PRODUCT_ARCHITECTURE.md`, `ARCHITECTURE.md`, `MODULES.md`, `FEATURE_SPEC.md` — kiểm chứng: mọi đường dẫn trong tài liệu tồn tại (`ls`), ADR-0001 ghi "Superseded một phần"
