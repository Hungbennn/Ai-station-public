> **LỊCH SỬ 18/10 — không phải yêu cầu thực thi hiện hành.** Giữ nguyên để tra quyết định và
> bằng chứng cũ; link `KET-QUA-CODEX.md` bên dưới là tên báo cáo dùng ở phiên 18/10,
> cần tra đúng phiên Git để xem nội dung cũ, không lấy báo cáo 20/10 thay bằng chứng đó. Đọc `proposal.md` và plan 20/10 để biết phần đã thay. Dấu nghiệm thu cũ không chứng minh change mới.

# Tasks — tự merge + tự deploy

Plan TDD: chia bốn lát — bảng ở `docs/plans/2026-10-18-tm-0-chia-lat.md`; lát nền (mốc 1.1–1.7, 4.1) ở
`docs/plans/2026-10-18-lat-tm-1-nen-cai-dat.md`; tự merge (mốc 2.1–2.7) ở
`docs/plans/2026-10-18-lat-tm-2-tu-merge.md`. Mỗi mốc dưới đây là một mốc nghiệm thu, không chép mã; bằng chứng là
test của plan (chạy qua `tests/chan_host/chay.sh -q`) hoặc kịch bản cổng trong sổ tay chạy thật.

Lát tự deploy (mốc 3.1–3.6): [plan TM-3](../../../docs/plans/2026-10-18-lat-tm-3-tu-deploy.md).
Task 1–9 đã áp trong `code/tm3`, chưa commit. Bằng chứng đỏ/xanh và một sửa tối thiểu so với plan:
[KET-QUA-CODEX.md](../../../KET-QUA-CODEX.md). Giữ các mốc TM-3 chưa tích: runner/Git thật không xác nhận
được thu hồi trong sandbox; cả bộ và G8 cần người điều phối kiểm ngoài sandbox. Không thay dấu TM-1/TM-2.

## 0. Cổng trước khi viết plan

- [x] 0.1 Đại ca trả lời 16 câu hỏi mở; kiểm chứng: D87–D101 trong `docs/quyet-dinh/2026-10-18-tu-merge-tu-deploy.md`, change đã sửa theo, `openspec validate tu-merge-tu-deploy --strict` xanh
- [x] 0.2 Đại ca duyệt mockup `docs/mockup/2026-10-18-tu-merge-tu-deploy/`; kiểm chứng: D101 ghi "mockup Tự động đã duyệt"
- [ ] 0.3 Đại ca duyệt bản change đã sửa theo D87–D101 (nhất là cách hiểu D92 ở `design.md` Open Questions); kiểm chứng: Đại ca nói duyệt trong chat, ghi vào bàn giao phiên; `DESIGN_SYSTEM.md` liệt kê mockup mới

## 1. Cài đặt theo dự án và cửa ghi (`dieu-khien-tu-dong`)

- [ ] 1.1 Cài đặt lưu bằng sự kiện, giá trị mặc định, phiên bản, lịch sử đổi; kiểm chứng: test các Scenario "Giá trị mặc định", "Xem lịch sử đổi"; không có `CREATE TABLE` mới (grep diff)
- [ ] 1.2 Tuyến đọc và ghi cài đặt qua `yeu_cau_ghi` + mã thao tác + `expected_version`; trường QC/kiểm lại/D76 bị từ chối; kiểm chứng: test 403 (thiếu và giả danh tính), 409, 422, gửi lại cùng mã thao tác
- [ ] 1.3 Kiểm lệnh khi lưu (tách đối số, độ dài, bộ quét bí mật); kiểm chứng: test Scenario "Dán token vào lệnh kiểm còn sống"
- [ ] 1.4 `bat_ghi: false` khoá bật công tắc; kiểm chứng: test Scenario "Dự án chỉ quét thử"
- [ ] 1.5 Kênh `header` chỉ nhận TẠM DỪNG/Tiếp tục, còn lại 403 (D87); kiểm chứng: test Scenario "Kênh header", "Tạm dừng vẫn được" và cùng thao tác qua `unix-socket` được nhận
- [ ] 1.6 TẠM DỪNG dự án và toàn trạm, Tiếp tục, không kiểm `expected_version`; kiểm chứng: test Scenario "Tạm dừng rồi tiếp tục", "Toàn trạm tạm dừng"
- [ ] 1.7 Tin Telegram mỗi lần cài đặt đổi (D99); kiểm chứng: test Scenario "Bật tự deploy", "Trạm tự tắt" với Telegram giả, tin không chứa nội dung lệnh

## 2. Tự merge (`tu-merge`)

- [ ] 2.1 Hàm thuần xét điều kiện trả danh sách lý do, đúng thứ tự estop → tạm dừng → `bat_ghi` → công tắc → QC → kiểm lại → đầu PR → D76 → CI/cột/hàng rào; kiểm chứng: test một dòng cho mỗi Scenario của `tu-merge`
- [ ] 2.2 Đọc trạng thái CI từ `gh pr view`; kiểm chứng: test với `gh` giả cho xanh, đỏ, đang chạy, rỗng
- [ ] 2.3 `gh.py` cho đúng một dạng `gh pr merge --merge --match-head-commit`; kiểm chứng: test khoá mới cấm `--admin`, `--squash`, `--rebase`, `--auto`, `--delete-branch`
- [ ] 2.4 Bước tự merge chen giữa mở PR và xác minh merge trong `buoc_github`, ghi `tu_merge.bat_dau` trước lệnh, đối soát khi không rõ, 3 lỗi liền → `tu_merge.loi`; kiểm chứng: test Scenario "Trạm tắt ngay sau lệnh merge", "Đại ca bấm tạm dừng giữa vòng tick"; luồng xác minh merge cũ vẫn xanh
- [ ] 2.5 Ghi `tu_merge.cho` khi lý do đổi; kiểm chứng: test không ghi lặp mỗi vòng tick
- [ ] 2.6 Hàng rào chỉ theo đường dẫn (D91), hàng rào `schema` theo đường dẫn + từ khoá và luôn chặn (D76, D92); kiểm chứng: test Scenario "Việc chỉ nhắc từ khoá…", "Tắt nút hàng rào vẫn chặn migration", "Việc nói tới xoá dữ liệu"
- [ ] 2.7 Tự gộp PR spec đã duyệt (D95); kiểm chứng: test Scenario "Duyệt spec xong thì PR spec tự vào nhánh chính", "Nhánh spec đổi sau khi duyệt", "Công tắc tắt"; điều kiện 8 của spec 4 §5.1 thấy commit đã vào nhánh chính

## 3. Tự deploy (`tu-deploy`)

- [ ] 3.1 Sẵn sàng deploy sau tự merge và sau gộp tay (D96), gộp nhiều merge, dòng ở Phê duyệt + số đếm (D101); kiểm chứng: test Scenario "Tự merge xong, tự deploy tắt", "Đại ca gộp tay", "Ba lần merge chờ deploy", "Hiện ở trang Phê duyệt"
- [ ] 3.2 Tuyến Deploy của Đại ca (`expected_commit`, estop, thiếu lệnh); kiểm chứng: test 403, 409, 422 và Scenario "Estop bật"
- [ ] 3.3 Luồng `vong_deploy`: một chuỗi một lúc mỗi dự án, bản sạch, môi trường tối thiểu, hạn giờ, giết nhóm tiến trình; kiểm chứng: test với lệnh giả trong thư mục tạm (không lệnh thật nào), Scenario "Lệnh deploy treo", "Merge mới trong lúc đang deploy"
- [ ] 3.4 Kiểm còn sống, tự lùi, bộ đếm hỏng, tự tắt sau 3 lần, lùi hỏng, không rõ kết quả; kiểm chứng: test Scenario "Lùi thành công", "Lần hỏng thứ ba", "Thành công xen giữa", "Trang chết sau lùi", "Mất điện giữa deploy"
- [ ] 3.5 Log deploy qua bộ quét bí mật, file 0600, sự kiện chỉ mã thoát/thời gian/digest; kiểm chứng: test Scenario "Lệnh deploy in ra token"
- [ ] 3.6 File trong repo mà ba lệnh nhắc tới vào đường dẫn cấm (D89); kiểm chứng: test Scenario "Agent sửa script deploy"

## 4. Báo tin

- [ ] 4.1 Loại tin mới và nguồn sự kiện; tin không chứa SHA, URL, đầu ra lệnh; tin xấu gửi ngay, tin tốt gom sau giờ yên lặng (D98); kiểm chứng: test `soan_tin` và nguồn tin với Telegram giả

## 5. Giao diện (mockup đã duyệt, D101)

- [ ] 5.1 Trang `#/du-an/<ten>` "Tự động", chip trên thẻ dự án, dòng "sẵn sàng deploy" ở Phê duyệt theo mockup đã duyệt (D101); kiểm chứng: `npm run kiem && npm run build && npm run kiem-dist`; mở dưới CSP thật với `tests/chay_thu_giao_dien.py`, console không lỗi CSP, đi tới được từ thanh bên
- [ ] 5.2 Nút TẠM DỪNG toàn trạm, băng cảnh báo, công tắc có hộp xác nhận; kiểm chứng: như 5.1, thêm thử khi không phải Đại ca (mọi nút khoá, "Chỉ đọc")

TM-4 đã áp nguyên văn Task 1–7 trên `code/tm4` (HEAD nền `e17c68d`, chưa commit): frontend 135/135,
build + `kiem-dist` đạt; test dữ liệu giả 3/3, nhóm Python liên quan và kiểm cấu trúc 111/111, 0 dòng chặn mới.
Giữ 5.1/5.2 chưa tích: sandbox chặn bind localhost nên chưa kiểm trình duyệt dưới CSP thật và so bố cục.
TM-2/TM-3 chưa có trong nền này; phần tích hợp sau ghép và cả bộ Python ngoài sandbox còn do điều phối kiểm.

## 6. Tài liệu và cổng chạy thật

- [ ] 6.1 ADR mới thay một phần ADR-0007; sửa `AGENT_RULES.md` §11, `PROJECT.md`, `PRODUCT_ARCHITECTURE.md`, `MODULES.md` (hai dòng tích hợp ngoài), `DESIGN_SYSTEM.md`; kiểm chứng: mọi đường dẫn file trong docs tồn tại (`ls`), không còn câu "chỉ Đại ca merge" lỗi thời
- [ ] 6.2 Thêm cổng "tự merge/tự deploy repo nháp" vào sổ tay chạy thật với kịch bản từng bước; kiểm chứng: Đại ca duyệt kịch bản
- [ ] 6.3 Hướng dẫn Đại ca chỉnh bảo vệ nhánh repo nháp: chỉ bắt buộc CI xanh (D94); kiểm chứng: có trong kịch bản cổng 6.2
- [ ] 6.4 Chạy thật trên repo nháp sau S7 và kênh `unix-socket`, từng kịch bản Đại ca cho phép; kiểm chứng: bằng chứng (lệnh, giờ, kết quả) ghi vào sổ tay; chưa đạt thì change ở lại `changes/`

