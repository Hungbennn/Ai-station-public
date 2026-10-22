# Chốt thảo luận tự merge + tự deploy (bs-2bd.3) — 18/10/2026

Đại ca trả lời từng câu trong buổi thảo luận, kết thúc bằng "Đủ rồi, viết spec đi". Thay ADR-0007 ở phần "chỉ Đại ca merge"
khi spec được duyệt và code xong; tới lúc đó Đại ca vẫn merge.

| # | Câu hỏi | Đại ca chọn |
|---|---|---|
| D69 | Bật cho dự án nào trước | **Mỗi dự án một công tắc riêng, mặc định TẮT; thử trước trên repo nháp** (cũng là repo của S7), ổn rồi mới bật HR Codex. |
| D70 | Điều kiện tự merge | **Đủ cả 5:** (1) agent khác QC đạt; (2) trạm kiểm lại trong vùng cách ly đạt; (3) CI GitHub xanh; (4) việc ở cột "AI tự làm"; (5) không chạm hàng rào (tiền/giá, cấu trúc DB, quyền/bảo mật, thứ khách thấy). Thiếu một → chờ Đại ca. **Mỗi dự án có nút bật/tắt từng điều kiện.** |
| D71 | Nút của điều kiện an toàn | **(1) QC và (2) kiểm lại KHOÁ CỨNG, luôn bật, không có nút** (INV-003, INV-006). Nút chỉ cho (3) CI, (4) cột, (5) hàng rào. |
| D72 | Feature lớn | **Đại ca vẫn duyệt spec** (điểm dừng #1); code của feature đã duyệt spec được tự merge theo D70. |
| D73 | "Deploy" là gì | **Mỗi dự án khai 3 lệnh** trong cấu hình dự án: deploy, kiểm còn sống sau deploy, lùi về bản trước. Không khai thì không tự deploy. |
| D74 | Deploy tới đâu | **Dự án chỉ có một môi trường** (khách đang dùng). **Nút "tự deploy" theo dự án, mặc định TẮT:** lúc đầu trạm tự merge rồi dừng trước deploy, báo Telegram "sẵn sàng deploy" để Đại ca bấm; Đại ca bật nút khi tin. |
| D75 | Deploy hỏng | **Tự lùi + báo Telegram, không tắt tự deploy** — trừ khi **hỏng 3 lần liên tiếp thì tự tắt** tự deploy của dự án đó và chờ Đại ca. |
| D76 | Cấu trúc DB, xoá dữ liệu | **Luôn chờ Đại ca, không có nút.** |
| D77 | Giới hạn số lần, giờ giấc | **Không giới hạn** số lần hay khung giờ tự merge/tự deploy. |
| D78 | Báo tin, nút dừng | **Telegram mỗi lần** tự merge/tự deploy/tự lùi; dashboard có nút **TẠM DỪNG** theo dự án và toàn trạm. UI mới cần mockup duyệt trước. |
| D79 | Chỉnh các nút ở đâu | **Chỉnh hết trên dashboard ngay** (cần mockup + đường ghi cấu hình từ dashboard — vùng kill list: cửa danh tính, công tắc lớn). |
| D80 | Agent tự cập nhật việc trong Beads (bs-2bd.5) | **Tách riêng, thảo luận sau** spec này. |

Còn phải hỏi khi bật cho HR Codex: HR Codex deploy thế nào (3 lệnh của D73).

## Chốt câu hỏi mở của spec `tu-merge-tu-deploy` (18/10) — mockup "Tự động" đã duyệt

| # | Câu hỏi (design.md) | Đại ca chọn |
|---|---|---|
| D87 | Cửa ghi còn tạm (`header`) | **Chỉ cho bấm TẠM DỪNG** tới khi cửa ghi chuyển `unix-socket` (G29); mọi nút bật và ô sửa khác khoá, kèm giải thích. |
| D88 | Lưu cài đặt ở đâu (D73 vênh D79) | **Sổ ghi sự kiện của trạm, chỉnh trên dashboard**, có lịch sử ai đổi gì; `du-an/*.yaml` không chứa phần này. Thay chữ "khai trong cấu hình dự án" của D73. |
| D89 | File trong repo mà 3 lệnh nhắc tới | **Thành file cấm sửa**: agent sửa → dừng hỏi Đại ca, không bao giờ tự merge. |
| D90 | Điều kiện "cột AI tự làm" | Việc đi từ cột 1 theo luồng tự động, không có dấu "Đại ca tự gán cột"; tắt nút thì việc Đại ca tự gán cũng được tự merge (vẫn đủ QC, kiểm lại). |
| D91 | "Chạm hàng rào" | **Chỉ khi code sửa vào vùng nhạy cảm** (cờ đỏ theo đường dẫn); nội dung việc chỉ nhắc từ khoá thì không tính. |
| D92 | Nhận biết "xoá dữ liệu" | Mỗi dự án khai từ khoá + đường dẫn vào hàng rào cấu trúc dữ liệu; hàng rào này luôn chặn, không nút. |
| D93 | Repo chưa có CI mà nút CI bật | **Không có CI = chưa xanh**, chờ Đại ca; muốn tự merge thì tắt nút CI của dự án. |
| D94 | Bảo vệ nhánh trên GitHub | **Chỉ bắt buộc CI xanh**; chưa bắt buộc cập nhật theo nhánh chính. Em ghi hướng dẫn chỉnh khi tới lúc. |
| D95 | PR spec của feature | **Đại ca đã duyệt spec trên dashboard thì trạm tự gộp PR spec luôn** (mở rộng D72). |
| D96 | "Sẵn sàng deploy" sau khi Đại ca gộp tay | **Có**, nếu dự án khai đủ 3 lệnh. |
| D97 | Năm luật an toàn thêm | **Đồng ý cả 5:** lùi hỏng → tắt tự deploy + tạm dừng dự án + báo khẩn; deploy không rõ kết quả → không tự chạy lại, tạm dừng; nút Deploy tay bấm được khi dự án tạm dừng, khoá khi Estop; lệnh có vẻ chứa bí mật bị từ chối khi lưu; gộp dồn → deploy một lần bản mới nhất. |
| D98 | Giờ yên lặng Telegram | Tin xấu (hỏng, đã lùi, tự tắt, lùi hỏng) gửi ngay; tin tốt gom gửi sau 7h. |
| D99 | Báo khi cài đặt tự động bị đổi | **Có, mỗi lần đổi một tin Telegram.** |
| D100 | Thời hạn lệnh | Deploy 15 phút, kiểm còn sống 2 phút, lùi 15 phút, chung mọi dự án. |
| D101 | "Sẵn sàng deploy" ở Phê duyệt; nút tạm dừng toàn trạm | **Có** một dòng mỗi dự án ở trang Phê duyệt và số đếm; nút TẠM DỪNG toàn trạm màu vàng trên thanh trên cạnh Estop. |
| D112 | Hàng rào cấu trúc dữ liệu / xoá dữ liệu có tính từ khoá trong nội dung việc | **Có** — riêng hàng rào dữ liệu tính cả từ khoá lẫn đường dẫn (các hàng rào khác theo D91 chỉ đường dẫn). Đại ca duyệt bản spec đã sửa (mốc 0.3) 18/10 → viết plan. |
| D114 | Tin "cài đặt tự động vừa đổi" trong giờ yên lặng (câu 2 plan TM-1) | **Gửi ngay** — tin an ninh. |
| D115 | Deploy "không rõ kết quả" dừng những gì (câu 3 plan TM-1) | **Tạm dừng cả dự án** (cả tự merge lẫn tự deploy), như lùi hỏng. |
| D116 | Dự án `bat_ghi: false` có được Deploy tay (câu 4 plan TM-1) | **Không.** Muốn deploy thì bật `bat_ghi` trước. |

Câu 1 plan TM-1 (nút Tiếp tục khi kênh ghi còn `header`): Đại ca hỏi lại "sao không làm `unix-socket` luôn" — chờ chốt
G29. Câu 5: Em chọn TM-4 không vẽ khối "agent tự cập nhật việc"; khối đó đi theo plan TC + mockup riêng (mốc 0.3 change
`agent-tu-cap-nhat-viec`).

## Chốt câu hỏi của plan TM-2 / TM-3 / TM-4 (18/10, Đại ca trả lời từng câu)

| # | Câu hỏi | Đại ca chọn |
|---|---|---|
| D119 | Đã gửi merge, chưa rõ kết quả; vòng sau PR còn mở nhưng điều kiện không còn đủ | **Chờ, ghi lý do** (không báo lỗi). |
| D120 | Cờ đỏ gitnexus (kể cả "gitnexus lỗi") có tính chạm hàng rào | **Có.** |
| D121 | Việc spike không có QC có được tự merge | **Không.** |
| D122 | Vòng tự merge của trạm có xét kênh ghi `header` | **Không** (luật kênh chỉ áp cho nút dashboard). |
| D123 | Bản đã "sẵn sàng" trước khi bật tự deploy | **Không tự deploy**, chờ Đại ca bấm. |
| D124 | Deploy hỏng đã tự lùi: giữ dòng "sẵn sàng"? | **Giữ**, trạm không tự thử lại. |
| D125 | "Bản mới nhất" tính cả commit Đại ca đẩy thẳng lên nhánh chính | **Có.** |
| D126 | "Không rõ kết quả" có đếm vào 3 lần hỏng | **Không.** |
| D127 | Lịch sử có dòng "nút Deploy bị huỷ" | **Có.** |
| D128 | Tắt tự merge / tự deploy có hỏi lại | **Có.** |
| D129 | Dòng "sẵn sàng deploy" ở Phê duyệt có nút Deploy | **CÓ nút Deploy ngay ở Phê duyệt** (khác đề xuất — sửa plan TM-4; cùng tuyến `POST …/tu-dong/deploy`, cùng khoá chung, cùng `expected_commit`). |
| D130 | Khối chưa có dữ liệu | **Hiện chữ "chưa có dữ liệu".** |

## G29 — kết quả đo và hướng cửa ghi (18/10 chiều)

Kịch bản `.handover/g29/g29-thu.sh` (nhật ký `~/.tram/g29/`): trạm ĐẠT 3/3 (TCP giả danh → không nhận; tram-kiem không vào
socket; tài khoản Đại ca vào socket được). `tailscale serve unix:` trả **502**: app Tailscale (App Store/Standalone) bị
sandbox macOS, Serve chỉ chuyển tiếp tới CỔNG, không tới file/socket (tài liệu Tailscale Serve). Lỗi kịch bản đã sửa:
`/usr/local/bin/tailscale` là script sh — dừng script không dừng app (lần 15:34 để sót serve giữ cổng 443).

| # | Câu hỏi | Đại ca chọn |
|---|---|---|
| D135 | Cửa ghi thật thay kênh `header` khi app Tailscale không trỏ được vào socket | **Hướng 2: Đại ca xác nhận bằng passkey (Touch ID / Face ID)** cho thao tác quan trọng; giữ app Tailscale, `tailscale serve` tới cổng TCP. TẠM DỪNG/Estop không cần chạm. Chặn cả agent trên máy A. Lý do thêm của Đại ca: sẽ làm **trạm chung cho nhiều người trong công ty** (phạm vi — xem câu hỏi kế tiếp). |
| D136 | Khi nào làm "trạm chung công ty" | **Giai đoạn kế tiếp**, sau khi tự merge + tự deploy chạy thật; spec riêng. Từ giờ chỉ chuẩn bị nền: passkey (D135) có "danh sách người + quyền", hiện chỉ Đại ca. `PROJECT.md` đã ghi. |
| D151 | Code các lát chạm kill list (TM-1 cửa ghi, TM-2 merge, TM-3 deploy + kiểm lại, TC ghi Beads) sau Codex review 3 vòng ĐẠT | **Cho code cả 5 lát**, lần lượt TM-1 → TM-2 → TM-3 → TM-4 → TC; mỗi lát chạy cả bộ rồi mới ghép; công tắc mặc định tắt, chưa bật trước passkey. |
