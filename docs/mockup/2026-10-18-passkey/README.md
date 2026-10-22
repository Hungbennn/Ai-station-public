> **Đã duyệt** — Đại ca duyệt 18/10/2026 (D150).

# Mockup — cửa ghi dashboard bằng passkey

**DRAFT — chờ Đại ca duyệt**, 18/10/2026 · bead `bs-2bd.9`.
Nguồn: [D137–D145](../../quyet-dinh/2026-10-18-passkey.md),
[change xac-thuc-passkey](../../../openspec/changes/xac-thuc-passkey/proposal.md).
Không xác thực thật, không gửi lệnh, không mã/QR bí mật thật. Các liên kết chỉ chuyển giữa ảnh trạng thái HTML;
ô nhập không gửi dữ liệu; nút TẠM DỪNG/Estop chỉ là hình thức minh hoạ.

## Mở xem

Tại gốc repo, chạy cục bộ:

```bash
python3 -m http.server 7809 --bind 127.0.0.1
```

Mở `http://127.0.0.1:7809/docs/mockup/2026-10-18-passkey/index.html`.
Phục vụ từ gốc repo để CSS/phông dùng chung được tải đúng. Có thể mở file HTML trực tiếp để đọc bố cục nhưng
quy tắc tải font/CSS qua `file:` tuỳ browser; dùng HTTP cục bộ để duyệt chính thức.

## Các màn

| Màn | File | Điều cần duyệt |
| --- | --- | --- |
| Đăng ký lần đầu | [index.html](index.html) | Hai bước: CLI trên B → nhập mã trên A → tạo passkey; hết hạn mã |
| Xác nhận nguy hiểm | [xac-nhan.html](xac-nhan.html) | Hộp “Chạm Touch ID để xác nhận”, đích/hậu quả, huỷ/quá hạn; ví dụ bật tự deploy luôn chạm lại |
| Windows | [windows.html](windows.html) | Windows Hello / khoá USB có xác minh người dùng / đường sang điện thoại |
| QR điện thoại | [qr.html](qr.html) | Vùng QR do trình duyệt cung cấp; không nhầm QR mời thêm thiết bị |
| Thiết bị đã đăng ký | [thiet-bi.html](thiet-bi.html) | Danh sách, thêm, thu hồi, cảnh báo passkey đồng bộ, lệnh khôi phục |
| Thêm thiết bị | [them-thiet-bi.html](them-thiet-bi.html) | Chạm trên thiết bị cũ → mã/QR một lần 10 phút; bản vẽ chỉ dùng chữ minh hoạ |
| Thu hồi | [thu-hoi.html](thu-hoi.html) | Chạm mới, thu hồi phiên liên quan, Telegram; trường hợp chiếc cuối |
| Chưa có passkey | [chua-co.html](chua-co.html) | Chỉ TẠM DỪNG/Estop; Tiếp tục và mọi ghi khác khoá, đường đăng ký rõ |
| Còn thời gian phiên | [phien.html](phien.html) | Thanh trên “Đã xác nhận, còn 6 giờ”; nêu ngoại lệ luôn chạm lại |

Các nút “Xem sau xác nhận” chỉ đi tới bản vẽ tiếp theo, không mô phỏng xác thực thành công.
Hộp hệ điều hành/browser là minh hoạ vị trí và lời hướng dẫn, không khẳng định giao diện browser giống hệt.
Dữ liệu giờ/thiết bị đều giả; bản thật phải lấy thời gian hết hạn từ server, không đếm dựa trên dữ liệu tự lưu.

## Vị trí trong điều hướng và lý do

- **Thiết bị đã đăng ký** ở trang riêng dự kiến `#/tai-khoan/thiet-bi`, đi từ thẻ **Đại ca · Chủ trạm** cuối sidebar
  và chip xác nhận trên thanh trên. Danh tính thuộc người, không thuộc dự án; không thêm mục menu thứ mười.
- Không thêm form ghi vào **Cài đặt** đã duyệt vốn chỉ đọc. Các mục sidebar khác dẫn sang mockup 15/10 để giữ khung.
- **Đăng ký** đi từ băng “Chưa có passkey” và trang thiết bị; không giấu đường đăng ký sau một nút yêu cầu passkey.
- **Hộp xác nhận** mở tại nút nguy hiểm trên màn hiện tại (Dự án, Phê duyệt, Đội ngũ, Ký ức…), không đưa chủ sang
  trang khác rồi mất nội dung. Trong bộ HTML tĩnh nó là trang riêng để duyệt được từng trạng thái.
- **TẠM DỪNG/Estop và chip còn giờ** luôn ở thanh trên. Các tab tình huống chỉ có trong mockup, không vào sản phẩm.
- Bản thật cần modal có quản lý focus, Escape/huỷ, trả focus về nút mở và lỗi `role="alert"`; mockup không có JS
  nên không giả thực hiện focus trap. Liên kết và input dùng được bằng bàn phím; có focus ring và bố cục hẹp.

## Khuôn, CSP và ảnh

Dùng nguyên CSS 15/10, CSS bổ sung 18/10 (gồm phông tự host), chỉ thêm bố cục tại [passkey.css](passkey.css).
Mỗi HTML có CSP meta: `default-src 'none'`, `script-src 'none'`, style/font `'self'`, không connect/form;
không script, style nội tuyến, handler `on…`, CDN hoặc yêu cầu API. Đây chặt hơn mẫu ở phần script vì không cần JS.
`frame-ancestors` phải là HTTP header ở bản thật; không đặt vào meta rồi tuyên bố chống nhúng.

**Ảnh PNG: chưa chụp được.** Phiên này thử mở server cục bộ bằng lệnh trên nhưng sandbox từ chối bind
(`PermissionError: [Errno 1] Operation not permitted`). Không vượt quyền hoặc tải browser/package.
Chưa kiểm bằng browser/CSP runtime, chưa xác nhận bố cục qua ảnh. Đã kiểm tĩnh HTML/CSP và liên kết;
chi tiết phép kiểm/số liệu ở `KET-QUA-CODEX.md` tại gốc repo.

Khi có môi trường xem cục bộ: chụp từng màn ở 1440×1000, thêm màn thiết bị/đăng ký ở 390×844;
đặt tên `anh-<ten-man>.png`, kiểm font, tràn ngang, console/CSP rồi ghi kết quả thực tế. Không chụp mã thật.
