Plan TDD: chưa có; viết trong `docs/plans/` sau khi Đại ca duyệt change và mockup này.

# Tasks — mốc nghiệm thu, không phải mã triển khai

Mỗi task của plan sau phải dẫn Requirement/Scenario tương ứng trong `specs/cua-ghi-passkey/spec.md`.
Các ô để trống tới khi có bằng chứng. Kiểm tài liệu ở `KET-QUA-CODEX.md` không thay nghiệm thu feature.

## 0. Duyệt và nối với các change khác

- [x] 0.1 D146–D149 đã chốt trong quyết định 18/10: profile riêng, hai tuyến N, cấm thu hồi cuối,
  Telegram gom gửi sáng. Cập nhật spec không phải bằng chứng đã triển khai.
- [x] 0.2 D150 đã duyệt chín màn mockup 18/10; kiểm browser/CSP runtime của bản triển khai vẫn ở 3.3.
- [ ] 0.3 Đối chiếu lại 23 POST và mọi router TM/TC khi plan viết: không sót route, phân loại theo hành vi;
  sửa điều kiện socket/D87 trong hai change song song, ADR-0004 và docs sở hữu khi tích hợp, không mở Tiếp tục cũ.
- [ ] 0.4 Plan ghim bản `webauthn` đủ tuổi ≥14 ngày và các phụ thuộc theo D145, không npm mới; kiểm metadata nguồn
  và lockfile. Bản đồ kho/schema, quyền OS cho CLI/cookie và đường phục hồi được review trước code.

## 1. Cửa người, phiên và xác nhận lại

- [ ] 1.1 Test người/quyền và D143: thiếu/trùng/giả header, login khác, người khoá, sai quyền, CSRF/Host;
  403 trước side effect, đúng trường hợp Host giữ 421. Token máy không mở cửa người.
- [ ] 1.2 Test có tham số cho **từng dòng** design D-2/D-3: N/P/R/M/B, trước/sau đăng ký, trước/sau hết phiên;
  tuyến chưa biết bị từ chối; `/tra-loi` đóng decision luôn P; sửa nhiều trường lấy mức cao nhất.
- [ ] 1.3 Test cookie đủ cờ và 8 giờ tuyệt đối: 7:59:59 nhận P, 8:00:00 từ chối; không sliding, R không gia hạn;
  credential/người thu hồi mất phiên ngay, browser khác không thừa hưởng.
- [ ] 1.4 Test WebAuthn với verifier thật trên fixture offline: chữ ký, challenge, RP/Origin, UV, replay và race;
  thử mọi thao tác D140 trong phiên; quyền R gắn mã/nội dung/đích, huỷ/hết hạn không ghi.
- [ ] 1.5 Test idempotency + race: hai yêu cầu cùng mã, crash/mất phản hồi sau ghi, đổi payload → 409,
  sai người không đọc được kết quả; phiên bản/commit/Estop/bat_ghi vẫn được kiểm sau xác nhận.

## 2. Mã, thiết bị, khôi phục và đường vòng

- [ ] 2.1 Test CLI bằng host giả và TRAM_HOME tạm: không argv/stdout redirect/log bí mật, chỉ TTY/đúng quyền,
  `dong-y`, hạn mã đúng 10 phút, cấp mã mới huỷ mã cũ, rate limit, hai browser tranh mã chỉ một đăng ký.
- [ ] 2.2 Test D142: thiết bị cũ R → mời mã/QR → thiết bị mới UV đúng login; mã B vẫn hoạt động;
  thu hồi lẻ huỷ phiên/mã con, xử lý credential cuối theo chốt; không nhầm QR mời và QR browser.
- [ ] 2.3 Test D144: huỷ không đổi; khôi phục nguyên tử huỷ toàn bộ key/phiên/challenge/mã cũ, cấp mã mới,
  restart vẫn mất quyền cũ, Telegram lỗi không hoàn tác, không tự bật lại công việc.
- [ ] 2.4 Test đường vòng máy: đăng ký khe đổi thông tin không bật khe đã tắt; khe mới chưa được phép không chạy;
  mã ghép chỉ cấp sau quyền ghép, không dùng mã passkey thay mã ghép; hook nhịp vẫn chỉ ghi nhịp.
- [ ] 2.5 Test Telegram giả: mỗi sự kiện quản lý thiết bị một cảnh báo, giờ yên lặng giữ bền rồi gom gửi sáng, đủ từng ID (D149);
  hàng chờ sống qua restart, lỗi có retry; quét marker bí mật trong log/sự kiện/argv/Telegram cả nhánh lỗi.

## 3. Giao diện và kiểm chứng offline

- [ ] 3.1 Frontend thật theo mockup được duyệt: đăng ký, hộp chạm Mac/Windows/QR/USB, thiết bị/thêm/thu hồi,
  chưa có passkey, chip còn giờ; lỗi tại chỗ, keyboard/focus/huỷ; không chứa secret trong storage/URL.
- [ ] 3.2 Chạy test Python qua `tests/chan_host/chay.sh -q` (đúng 0 dòng chặn mới), frontend
  `npm run kiem && npm run build && npm run kiem-dist`; ghi passed/failed thực tế, không suy từ số cũ.
- [ ] 3.3 Mở giao diện với dữ liệu giả dưới CSP thật; không lỗi console/CSP, mọi màn vào được từ điều hướng,
  kiểm desktop/hẹp; không dùng ảnh mockup làm bằng chứng Touch ID thật.

## 4. Cổng chạy thật — mỗi kịch bản phải được Đại ca cho phép trước

- [ ] 4.1 Soạn kịch bản trong sổ tay, sao lưu/đường lui giữ đóng P/R. Trên B kiểm đúng tài khoản trạm, principal
  thợ/agent, quyền cookie/DB/CLI/TTY và Tailscale login. Không đạt cách ly thì dừng, không ghi cổng xanh.
- [ ] 4.2 **Đổi `tailscale serve` từ socket sang cổng TCP loopback**: ghi lệnh theo bản app đang dùng, thời điểm,
  cấu hình trước/sau; HTTPS trả đúng dashboard, không 502, không nghe công khai; header đúng không mở P/R.
- [ ] 4.3 **Đăng ký trên máy A**: chủ cấp mã tại B, nhập trên A đúng login, Touch ID/Face ID có UV, cookie đúng cờ;
  hết hạn/dùng lại mã thất bại; giữ ảnh/log bằng chứng đã che mã, không quay màn hình mã thật.
- [ ] 4.4 **Đo agent máy A và B không làm được thao tác nguy hiểm**: từ principal thật của mỗi agent thử từng nhóm
  D138 với header giả, không phiên; sau đó thử quyền đọc cookie/điều khiển browser/CLI cứu hộ. Ghi UID, quyền,
  ma trận HTTP và side effect bằng 0. Nếu A cùng tài khoản đọc được cookie thì ghi lỗ giới hạn D139, cổng chưa đạt;
  không gọi kết quả thiếu-cookie là chặn được mọi agent. Đo R bằng phiên còn hạn vẫn đòi người xác nhận.
- [ ] 4.5 **Windows thật**: Windows Hello, QR điện thoại, khoá USB có UV trên browser hỗ trợ; đúng login thành công,
  khác login thất bại; thiếu hỗ trợ/hủy không hạ cửa ghi. Đây là client Windows, server vẫn Mac.
- [ ] 4.6 **Thiết bị/khôi phục thật**: thêm thiết bị thứ hai, thu hồi lẻ, thử cookie cũ; mất hết → B `dong-y`,
  đăng ký lại; kiểm Telegram từng lần và thử hồi phục khi báo tin lỗi có kiểm soát. Chỉ dùng dữ liệu/cổng được duyệt.
- [ ] 4.7 Cập nhật tài liệu sở hữu và ADR thay phần socket; archive chỉ sau mọi Scenario có bằng chứng,
  người điều phối đóng bead sau QC/tích hợp. Không archive hay đóng bead ở phiên viết spec này.

## Bằng chứng triển khai offline — 18/10/2026, nhánh code/passkey

Đã áp Task 1–13 (bản cuối sau review vòng 2, coverage vòng 3), đóng CLI ghép theo D155 và nối mọi tuyến TM/TC:
N cho TẠM DỪNG/Estop, P cho Tiếp tục/Deploy tay/TC/tự merge/tắt hoặc chỉnh tự deploy, R cho bật tự deploy,
sửa ba lệnh và quản lý passkey. Máy chủ tự so cấu hình dưới khoá ledger; retry có kết quả vẫn xác thực phiên,
retry chưa hoàn thành kiểm lại quyền. Inventory giữ tập đóng 30 POST ngoài passkey.

Tập tích hợp cuối (API/passkey/khe/ghép máy/báo tin/kiến trúc) đã đo 472 passed, 1 deselected (ca bind Unix socket đã thử riêng và bị sandbox chặn).
Frontend đã đo 154 passed; build và kiểm bundle đạt. Các mốc trên không thay toàn repo, QC độc lập hoặc cổng
browser/OS; chưa đánh dấu những ô nghiệm thu tổng hợp đó là xong. Chi tiết lệnh, số đo cuối và ca lỗi sandbox
ở `KET-QUA-CODEX.md` tại gốc worktree. Không archive, đóng Beads hay mở cổng thật trong phiên này.
