## ADDED Requirements

### Requirement: Hai khe có danh tính riêng
Hệ thống SHALL biểu diễn khe bằng (máy, CLI, tài khoản). Hai khe đầu là
`B/claude-1`, `B/claude-2`, chạy bằng `tram-khe1`, `tram-khe2`, khác UID,
khác tài khoản trạm, quản lý thợ và kiểm lại. Vai chỉ là ưu tiên.

#### Scenario: Thêm khe thứ hai khi phần kiểm đã chạy
- **WHEN** chuẩn bị hai khe ở máy B đã có Uq và plist thợ đang disable
- **THEN** chỉ phần tài nguyên thợ được đối soát/cài, không sửa Uq hoặc hồ sơ
  kiểm, không bootstrap/enable thợ, không tự nhận user lạ là của trạm.

### Requirement: Token B chỉ lưu dưới đúng UID và chạy không cần mở Keychain
Theo QĐ2-A sửa 21/10, hệ thống MUST giữ token `claude setup-token` của mỗi khe B trong
`/Users/tram-kheN/claude/oauth-token` (0600, chủ khe, thư mục 0700, không symlink).
Token máy B MUST ở `/Users/tram-tho/.tram/token-may` (0600, chủ tram-tho, thư mục 0700).
Writer MUST dùng tmp 0600 và rename nguyên tử, từ chối sai chủ/quyền, symlink/hardlink/file đặc biệt.
B dùng file khi `tren_may_b`; thợ từ xa MUST giữ Keychain. Không fallback khi file B lỗi.
Ngoại lệ lưu file chỉ cho hai loại token này; không credential trạm/GitHub/passkey/khe khác.

#### Scenario: Cấp token máy trước khi đăng ký B
- **WHEN** `nhan-token --may-b` nhận token qua stdin hoặc ô ẩn khi chưa có tho.yaml
- **THEN** ghi file dưới UID tram-tho, không cần Keychain; không in token, không tự bật thợ.
  Lỗi trước rename giữ file cũ; đọc/ghi bị từ chối khi sai chủ/quyền hoặc đích là symlink.

#### Scenario: Chạy Claude từ quản lý thợ
- **WHEN** B chạy auth status, phép đo nền hoặc Claude của một phiếu
- **THEN** wrapper tin cậy SHALL chạy sau sudo dưới UID khe, mở file rồi exec Claude với
  `CLAUDE_CODE_OAUTH_TOKEN_FILE_DESCRIPTOR` chỉ mang số FD. Token không nằm trong argv,
  log, env của tram-tho hay sudo preserve-env; không fallback token env thường.
  Wrapper lọc auth env cũ/CLAUDE_CODE_REMOTE, giữ stdin cho prompt và kiểm `.credentials.json` vắng.

#### Scenario: Nhập token Claude có chủ ý
- **WHEN** Đại ca chạy login-N tại Terminal.app
- **THEN** chạy setup-token dưới đúng khe, chỉ hiện màn tương tác tại Terminal;
  getpass nhận token không echo rồi gửi stdin cho writer dưới khe. Không có TTY/ô ẩn thì dừng.
  Kiểm chủ/quyền, auth status qua FD và không `.credentials.json`; chưa coi là S2 nền đạt.

#### Scenario: Token thiếu sai quyền hết hạn hoặc có credential ngoài dự kiến
- **WHEN** file không hợp lệ, CLI không xác nhận loggedIn hoặc headless thất bại
- **THEN** giữ cổng nhận việc đóng, chỉ in kết luận hằng, không tự xoay token hoặc mở Keychain.
  Token hết hạn/thu hồi cần Đại ca thực hiện lại login-N; không nhận lỗi dò là đăng nhập thành công.

#### Scenario: Cách ly file token có đối chứng
- **GIVEN** owner đã kiểm file đúng chủ/quyền và đọc được; token có thật
- **WHEN** khe kia và UID tram-tho thử mở token khe, hoặc khe thử mở token máy
- **THEN** MUST bị từ chối quyền, không đọc/trả nội dung token ngay cả khi phép thử lọt;
  thiếu file, thiếu lệnh, timeout không tính đạt. S6 ghi sáu kết luận trực tiếp bằng UID.
  Sudoers ALL cho quản lý đổi UID là giới hạn riêng trong QĐ2; phép này không chứng minh chống sudo.

#### Scenario: Daemon tự lên sau reboot
- **WHEN** reboot B sau khi token và plist đã được chuẩn bị, dịch vụ được enable có chủ ý
- **THEN** daemon SHALL tự đọc token máy và dùng hai token khe, không ai mở khoá Keychain;
  phải có bằng chứng system domain, UserName, auth/headless và nhịp, gồm thời điểm trước mở khoá.
  Test giả hoặc auth status tại Terminal không thay bằng chứng S2/R5; chưa đóng bs-2bd.11 khi chưa đo.

#### Scenario: Hai thư mục nhưng cùng tài khoản Claude
- **WHEN** hai CLI báo cùng danh tính tài khoản
- **THEN** S3 không đạt; tên khe/thư mục khác nhau không thay bằng chứng danh tính.
  Đại ca xem danh tính tại Terminal, log chỉ ghi khác nhau hay chưa xác nhận.

### Requirement: Đăng ký B độc lập với cài dịch vụ
Hệ thống SHALL có lệnh đăng ký B qua API loopback bằng token máy hiện có;
plist hệ thống tồn tại không phải lỗi. Lệnh không cấp mã ghép, không tự đổi
token, không khởi động dịch vụ, không mở khe và không bật giao việc.

#### Scenario: Đăng ký lần đầu và gửi lại
- **WHEN** cấu hình ứng viên đúng B/hai khe được gửi thành công
- **THEN** API có đúng hai khe, mặc định tắt; cấu hình chỉ được thay nguyên tử
  sau HTTP thành công. Gửi lại cùng nội dung không thêm sự kiện đăng ký trùng.

#### Scenario: HTTP lỗi hoặc mất phản hồi
- **WHEN** chưa xác nhận được đăng ký
- **THEN** giữ cấu hình cũ; thử lại cùng nội dung/token để đối soát. Nếu máy đã
  nhận token nhưng lưu kho token hỏng, báo cần cấp lại riêng, không tự xoay token.

### Requirement: Khe sửa mã mà không ghi kho Git chung
Theo QĐ3-A, hệ thống SHALL chỉ cấp khe quyền sửa cây mã và ghi hàng đợi của
phiếu; metadata Git, settings, MCP và kho của quản lý thợ vẫn không ghi được.
Quản lý thợ chốt commit khi nhận yêu cầu bàn giao, gắn SHA/lượt của chính phiếu.
Không mở ghi objects/ref chung để chữa lỗi commit.

#### Scenario: Hoàn tất một việc
- **WHEN** khe gửi xong và toàn bộ tiến trình của lượt đã thu hồi
- **THEN** quản lý chốt cây mã, điền cùng SHA vào báo cáo và bàn giao,
  chạy kiểm của thợ rồi công bố; trạm kiểm lại qua Uq và QC khác khe.

#### Scenario: Mốc tạm hoặc báo cáo giả SHA
- **WHEN** khe gửi mốc tạm hoặc tự điền SHA
- **THEN** B không tin SHA do khe gửi; mốc chỉ lưu tiến độ trong lượt.
  Khi dừng mềm, quản lý chốt WIP sau thu hồi. Không hứa mốc tạm đã được công bố.

#### Scenario: Thử vượt quyền
- **WHEN** mỗi khe thử sửa config/hooks/index/objects/refs, `.git`, settings,
  đọc khoá trạm, nhà Đại ca, cấu hình/hàng đợi khe khác hoặc gọi API ghi giả danh
- **THEN** phép thử có đối chứng phải bị chặn, đúng UID; lỗi dò/đích không tồn
  tại không tính là đạt. G4 của tram-kiem không thay S6 của khe.

#### Scenario: Đổi lượt code sang QC hoặc đổi khe
- **WHEN** phiếu mới có lượt hoặc khe khác
- **THEN** hệ thống tạo cây riêng tại đúng SHA cha; quyền lượt cũ không chuyển sang cây mới.
  Cổng thư mục cha do quản lý sở hữu, khe không sửa được; đóng cổng rồi dọn UID/cây khi kết thúc.

#### Scenario: Restart và dừng mềm
- **WHEN** cùng phiếu tiếp tục sau tắt daemon, hoặc phiếu kết thúc mềm
- **THEN** restart giữ bản sửa chưa commit, không reset cây hay cấp lại thư viện/ACL; tắt daemon đóng
  cổng nhưng giữ cây/phiếu. Dừng mềm giữ commit WIP theo cơ chế công bố hiện có rồi dọn cây.
  Phiếu cũ bị từ chối sau restart cũng được dọn trước khi xoá sổ.

#### Scenario: File thuộc UID khe hoặc dọn thất bại
- **WHEN** khe tạo file/thư mục với umask 077, hoặc làm quản lý không dọn được
- **THEN** ACL kế thừa cho quản lý đọc/dọn file bình thường mà không chmod/chown từng file.
  Lỗi dọn hoặc chưa chứng minh UID sạch giữ cổng đóng/phiếu và dừng khe; không mở sudo root/Git.

### Requirement: Worktree có dependency offline từ bundle root
Hệ thống SHALL dùng bộ thư viện root đã cài cho ben-station, kiểm đúng bốn file nguồn, runtime/ABI,
hash và giới hạn archive bằng cơ chế G4 hiện có. Runtime và mỗi lượt có bản thư viện riêng;
không sửa Uq, không dùng venv/cache nhà hungle, không tải mạng hoặc chạy mã repo bằng UID quản lý.

#### Scenario: Lượt mới có lock đúng bundle đã cài
- **WHEN** quản lý chuẩn bị cây mới trước khi mở quyền cho khe
- **THEN** helper Python ghim, chế độ isolated, có hạn sẽ cấp `.venv` và `frontend/node_modules` từ
  artifact root đã kiểm. Cả CLI và kiểm sau xong chạy runner với cờ đã chuẩn bị sau chuyển principal;
  đủ sáu lệnh kiểm ben-station chạy offline. Uq vẫn kiểm độc lập trong lượt riêng.

#### Scenario: Dependency thiếu, bị đổi hoặc chuẩn bị dở
- **WHEN** không có đúng một manifest khớp, lock/runtime/hash sai, nguồn symlink hoặc đích không trống
- **THEN** giữ cổng đóng và không chạy CLI; không fallback cache hay tải gói. Retry chuẩn bị dở dọn
  cây riêng rồi làm lại; retry phiếu đã sẵn sàng giữ bản sửa, không chia sẻ dependency với khe khác.

### Requirement: Nguồn mã cục bộ có đích rõ ràng
Theo QĐ4-A, hệ thống SHALL dùng `chay.day: kho-tho` và trạm dùng `lai` với
ánh xạ B; chỉ trạm có quyền GitHub. Kho kiểm đang được trạm fetch là nguồn đọc
cục bộ của thợ, không phải snapshot cần cập nhật tay.

#### Scenario: Remote github đã có, origin thiếu
- **WHEN** URL github đã đối chiếu đúng `Hungbennn/ben-station`
- **THEN** tạo origin cùng URL, giữ github; kho thợ có origin là đường cục bộ
  đã cấp đọc, không mang URL có credential.

#### Scenario: Remote khác nhau hoặc không đọc được commit cha
- **WHEN** origin/github trỏ khác đích, hay phiếu có SHA chưa có trong nguồn
- **THEN** dừng với lỗi rõ, không đổi remote ngầm, không dùng HEAD thay SHA,
  không cấp credential GitHub xuống khe.

### Requirement: Chỉ kiểm và giao đúng phạm vi
Theo QĐ5-B, hệ thống SHALL mở mọi việc đủ điều kiện của ben-station, không giới hạn
một bead thử. Giới hạn dự án được kiểm trước claim và khi cấp phiếu; HR luôn tắt,
tự merge/deploy tắt. `bat_ghi` vẫn bắt buộc; cài phạm vi không tự bật ghi.
Kiểm máy thợ cho ben-station không yêu cầu HR có repo.

#### Scenario: Tắt giao vẫn nhận yêu cầu từ máy A
- **GIVEN** ben-station đang có `bat_ghi: true` để nhận yêu cầu từ máy A
- **WHEN** tắt giao việc bằng sổ tay
- **THEN** `giao_viec.bat` là false; hệ thống SHALL giữ nguyên `bat_ghi` ben-station,
  để kênh nhận yêu cầu máy A vẫn mở độc lập với giao việc.

#### Scenario: HR chưa clone
- **WHEN** kiểm thợ với `--du-an ben-station`
- **THEN** chỉ dò kho/quyền ben-station; vẫn kiểm đủ đăng nhập, danh tính,
  thu hồi và cách ly cả hai khe. Tên dự án lạ phải bị từ chối.

#### Scenario: Mở mọi việc đủ điều kiện của ben-station
- **WHEN** bật giao việc với danh sách dự án `[ben-station]` và nhiều bead đủ điều kiện
- **THEN** tất cả các bead đó được xét theo bộ xếp việc hiện có; không claim/cấp HR
  kể cả khi cấu hình dự án khác bật ghi. Không có danh sách bead thử.

#### Scenario: Mở rộng việc vẫn giữ hạn mức
- **WHEN** ngân sách bead/phiếu, số lần chạy, trần giờ/ngày, quota hoặc cầu dao chặn lượt mới
- **THEN** hệ thống giữ nguyên quyết định dừng/chờ hiện có, không nới ngưỡng để chạy tiếp;
  kiểm lại và QC khác khe vẫn bắt buộc.

### Requirement: Bật dịch vụ bằng bước có kết quả kiểm được
Hệ thống SHALL có sổ tay một lệnh cho mỗi bước cần sudo, log riêng 700/600
chỉ chứa giai đoạn/mã lỗi/kết luận. Đăng nhập tương tác không được thu log.
Không bật công tắc để thử khi chưa đạt cổng.

#### Scenario: Bật lại daemon bị disable
- **WHEN** S2/S3/S4/S6/S7/S8 và phạm vi việc đã đạt, Đại ca cho phép bước bật
- **THEN** dùng enable rồi bootstrap đúng `system/vn.tram.tho`, đối chiếu
  UserName/plist/nhịp tim; lỗi thì giữ giao việc tắt và có lệnh dừng riêng.

#### Scenario: Hạn mức chưa biết
- **WHEN** Claude chưa có dữ liệu quota lúc rảnh
- **THEN** hiển thị chưa biết, không bịa phần trăm; thử có ngân sách nhỏ và
  cầu dao/thu hồi được đo. Không bắt thêm Codex chỉ để vượt G5 của Codex.

#### Scenario: Nghiệm thu thật
- **WHEN** hai khe có nhịp tim và một việc ben-station đi hết code, kiểm lại,
  QC khác khe, công bố đúng SHA
- **THEN** ghi bằng chứng máy thật; chỉ việc hiện thẻ hoặc test giả xanh
  không đủ để tuyên bố hai thợ đã làm được việc.
