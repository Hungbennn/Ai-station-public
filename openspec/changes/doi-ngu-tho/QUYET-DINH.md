# Năm quyết định để bật hai thợ

Đại ca đã chốt đích: **hai Claude trên B, ben-station trước, làm gọn**.
**ĐÃ CHỐT 20/10/2026:** QĐ1 = A, QĐ2 = A, QĐ3 = A, QĐ4 = A, **QĐ5 = B (mở ngay mọi việc đủ điều kiện của ben-station; HR vẫn tắt, tự merge/deploy vẫn tắt)**.

## QĐ1 — Lúc nào thợ bắt đầu làm sau khi bật máy?

**Quyết định gì:** có cần thợ làm trước khi ai đăng nhập máy B không?

- **A:** đợt đầu chấp nhận Đại ca đăng nhập máy B, mở kho đăng nhập cần thiết,
  rồi chạy một lệnh bật thợ. Vẫn dùng dịch vụ thợ hiện có.
- **B:** bắt buộc tự làm ngay sau reboot, chưa ai đăng nhập; chỉ nhận sau khi
  phép thử Keychain chứng minh được, có thể kéo dài đợt này.

**Khuyến nghị: A.** Máy hiện cũng cần đăng nhập để Tailscale/Keychain lên.
**Nếu chọn sai:** chọn A khi Đại ca cần hoàn toàn không người ngồi thì máy
reboot xong sẽ chờ; chọn B khi không cần có thể mất thời gian sửa phần đăng nhập.
Phụ thuộc: S2, Task 4, bước R2/R5 của plan. Bổ sung 21/10 ở QĐ2 bỏ phụ thuộc mở Keychain;
đích nghiệm thu là daemon tự chạy sau reboot, chỉ xác nhận khi R5 có bằng chứng.

## QĐ2 — Hai thợ giữ đăng nhập Claude ở đâu?

**Quyết định gì:** cho mỗi tài khoản Mac giữ đăng nhập Claude của chính nó?

**QĐ2-A sửa 21/10/2026 — Đại ca đã chốt trong phiên:** chỉ thay phần giữ/đưa token;
giữ user riêng, quyền Git/QC/cách ly còn lại của QĐ2-A và ADR-0009.

- Claude: `claude setup-token` dưới từng user khe tại Terminal.app; Đại ca dán vào ô ẩn.
  Ghi qua stdin dưới chính UID khe vào `/Users/tram-kheN/claude/oauth-token`: file 0600,
  thư mục 0700, đúng chủ, không symlink. Không dùng `.credentials.json` hoặc phiên hungle.
- Chạy Claude: wrapper tin cậy **sau sudo**, dưới UID khe, mở file rồi exec CLI với
  `CLAUDE_CODE_OAUTH_TOKEN_FILE_DESCRIPTOR` chỉ chứa số FD. Không đưa token vào argv,
  log, env của tram-tho hoặc `sudo --preserve-env`; không fallback sang token env.
- Token máy B: `/Users/tram-tho/.tram/token-may`, 0600, chủ tram-tho, thư mục 0700;
  ghi tmp 0600 + fsync + rename, không symlink. Chọn file khi `tren_may_b`, máy từ xa giữ Keychain.
- Sổ tay B bỏ `keychain`/`set-keychain-settings`; login ghi file rồi kiểm chủ/quyền,
  auth status qua wrapper và không `.credentials.json`. S2 vẫn đòi headless từ daemon.
  R5 phải đo tự chạy sau reboot, không mở khoá; đây là đích giải `bs-2bd.11`, chưa đóng bead.

**Bằng chứng Đại ca cung cấp (21/10, B, macOS 15.6.1, CLI 2.1.227):** log
`/private/tmp/chan-doan-tho-nen.txt`; `vn.tram.tho` system/UserName tram-tho và con
`sudo -n -u tram-kheN` thấy default/search list chỉ System.keychain. Login Keychain
đã mở ở Terminal vẫn báo `User interaction is not allowed` (36); token máy không đọc
được, Claude loggedIn=false. Mở khoá gắn phiên; cách Keychain user riêng cũ không dùng
được trong daemon, **S2 đỏ**. Đây là bằng chứng được cung cấp, không phải lần chạy của phiên soạn plan.

**Ngoại lệ bí mật:** lời chốt này thay lệnh cấm file ở AGENT_RULES §14 và ENGINEERING_STANDARDS
chỉ cho hai loại token trên B. Khoá trạm khác/GitHub/passkey không đổi; API vẫn giữ hash token máy.
Mã cùng UID khe có thể đọc và dùng token Claude của khe.

**Giới hạn sudo cần phân biệt:** `cai_dat_tho.noi_dung_sudoers` hiện sinh
`tram-tho ALL=(tram-khe1,tram-khe2) NOPASSWD:SETENV: ALL`. 0600 chặn UID tram-tho
đọc trực tiếp, không chặn đổi UID qua quyền sudo đó. S6 đo trực tiếp bằng UID quản lý
và khe kia; không dùng kết quả ấy để tuyên bố chống quản lý có sudo. Nếu yêu cầu bao
trùm cả sudo, đây là blocker cần quyết định ranh giới thực thi riêng, không tự đổi sudoers
hay làm yếu câu “không đọc được”. Phạm vi này đã được hỏi, chưa mặc nhiên coi là được duyệt.

**Phương án vẫn loại:** chung phiên hungle; quản lý giữ token Claude rồi phân phát;
đưa token vào env/argv; daemon mở Keychain tự động. Token hết hạn/thu hồi → giữ cổng đóng,
Đại ca tạo lại bằng cùng bước login; không tự xoay hay thử lặp.

Phụ thuộc: S2/S3/S6, ADR-0009; plan bổ sung
[2026-10-21-doi-ngu-token-file.md](../../../docs/plans/2026-10-21-doi-ngu-token-file.md).

## QĐ3 — Ai chốt bản sửa thành commit?

**Quyết định gì:** cấp quyền Git chung cho khe hay để quản lý thợ chốt bản sửa?

- **A:** khe sửa mã và gửi báo cáo qua hàng đợi sẵn có; quản lý thợ chốt commit,
  điền mã commit vào báo cáo rồi công bố theo luồng cũ.
- **B:** khe tự commit; cần mở quyền index/objects/ref và chứng minh không sửa
  được nhánh, cấu hình, hooks hay dữ liệu của khe bên cạnh.

**Khuyến nghị: A.** Bớt quyền phải cấp trên kho chung, dùng quản lý thợ đã có.
**Nếu chọn sai:** A cần sửa `tram bao` và lời dặn thợ; nếu chỉ bỏ quyền Git mà
không sửa báo cáo, thợ sẽ mắc ở bước hoàn tất. B có thể làm commit được nhưng
mở quá rộng quyền của hai khe. A không có nghĩa tin báo cáo: kiểm lại và QC
khác khe vẫn bắt buộc.
Phụ thuộc: S6, Task 5–7; QĐ3-A đã duyệt thay phần “agent commit” trong ý đồ cũ.

## QĐ4 — Thợ lấy và trả mã bằng đường nào?

**Quyết định gì:** đưa quyền GitHub xuống thợ hay dùng bản kho cục bộ trên B?

- **A:** trạm lấy GitHub; thợ đọc bản kho cục bộ, trả commit qua `kho-tho`.
  Giữ `github`; thêm `origin` cùng URL nếu thiếu. Hai tên có URL khác thì dừng.
- **B:** cấp quyền GitHub riêng cho quản lý thợ và dùng ref tạm trên mạng.

**Khuyến nghị: A.** Đúng đường máy B sẵn có, không thêm một bộ khoá GitHub.
**Nếu chọn sai:** kho đọc cục bộ không được cập nhật thì thợ thiếu commit cha;
plan dùng chính kho kiểm do trạm cập nhật làm nguồn đọc, không tạo bản mirror
quên đồng bộ. B tăng việc giữ và thu hồi khoá.
Phụ thuộc: S7, R3; `cong_bo.phuong_an: lai` với ánh xạ B giữ quyết định D4 cũ.

## QĐ5 — Mở việc rộng đến đâu lần đầu?

**Quyết định gì:** nhận một việc thử hay toàn bộ việc đủ điều kiện của ben-station?

- **A:** chỉ một bead Đại ca đã chọn, cho hai khe đi hết code → kiểm lại → QC.
  Sau khi xem kết quả mới bỏ giới hạn bead; dự án vẫn chỉ ben-station.
- **B:** mở ngay tất cả việc đủ điều kiện của ben-station.

**Đã chọn: B.** Mở ngay mọi việc đủ điều kiện của ben-station sau các cổng chạy thật.
Không thêm danh sách bead. Giữ ngân sách bead/phiếu, trần giờ/ngày, quota và cầu dao hiện có.
**Nếu chọn sai:** B có thể tiêu lượt và sửa nhiều việc cùng lúc; A mà quên
bỏ giới hạn thì các việc sau sẽ chờ. HR luôn để tắt, tự merge/deploy cũng tắt.
Phụ thuộc: Task 8, R6/R7; công tắc lớn chỉ bật sau khi các cổng trước đạt.
