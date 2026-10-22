# Mockup — Tự động: tự merge, tự deploy, agent tự cập nhật việc (18/10/2026)

Trạng thái: **đã duyệt** (D101, 18/10/2026). Chưa có plan, chưa có code giao diện.

## Mở xem
Chạy từ **gốc repo** (mockup dùng lại `style.css` của mockup 15/10 và phông tự host trong `frontend/`):

```bash
python3 -m http.server 7802 --bind 127.0.0.1
# rồi mở http://127.0.0.1:7802/docs/mockup/2026-10-18-tu-merge-tu-deploy/index.html
```

Không cần mạng: không CDN, không URL ngoài, không `style="…"`, không script nội tuyến; `index.html` tự đặt CSP giống
tram-api để chính mockup chứng minh điều đó (console không có lỗi CSP khi mở). Dữ liệu giả, mọi nút chỉ đổi giao diện.

## Các màn và ảnh chụp
| Ảnh | Đường dẫn | Thấy gì |
| --- | --- | --- |
| `anh-du-an.png` | `#/du-an` | Thẻ dự án (giữ mockup 15/10) thêm hàng chip tự merge / tự deploy / agent cập nhật việc, "1 sẵn sàng deploy", link "Tự động →" |
| `anh-tu-dong.png` | `#/du-an/repo-nhap` | Trang Tự động của một dự án: sẵn sàng deploy + nút Deploy, việc chờ Đại ca kèm lý do, lịch sử, bộ đếm hỏng liên tiếp, cài đặt (công tắc chính, 2 điều kiện "luôn bật", 3 nút điều kiện, dòng "cấu trúc DB — luôn chờ Đại ca", 3 lệnh, tự deploy), khối agent tự cập nhật việc |
| `anh-tu-dong-sua-lenh.png` | `…/repo-nhap?sua=1` | Ô sửa 3 lệnh (Lưu cần xác nhận; lệnh có token bị từ chối tại chỗ) |
| `anh-tu-dong-tu-tat.png` | `…?th=tu-tat` | Hỏng 3 lần liên tiếp → trạm tự tắt tự deploy, bộ đếm 3/3 |
| `anh-tu-dong-lui-hong.png` | `…?th=lui-hong` | Lùi cũng hỏng → dự án tạm dừng, băng đỏ, nút Tiếp tục |
| `anh-tu-dong-cua-tam.png` | `…?th=cua-tam` | Cửa ghi còn tạm: mọi nút khoá trừ Tạm dừng (câu hỏi mở 1) |
| `anh-hr-codex-khoa.png` | `#/du-an/hr-codex` | Dự án `bat_ghi: false`: chip "chỉ quét thử", công tắc khoá, chưa khai lệnh |
| `anh-tam-dung-toan-tram.png` | `#/du-an?tram=tam-dung` | Nút TẠM DỪNG toàn trạm (thanh trên, cạnh Estop) đang bật + băng vàng trên mọi trang |
| `anh-cong-viec.png` | `#/cong-viec` | Thẻ việc: dòng tiến độ do agent ghi, nhãn "do agent tạo" + link việc gốc, "bị chặn — cần Đại ca" + lý do |

Hàng nút "Tình huống (chỉ có trong mockup)" trên trang repo-nhap chỉ để Đại ca xem các trạng thái; bản thật không có.

## Đặt ở đâu trong điều hướng — và vì sao
- **Trang Tự động của từng dự án `#/du-an/<ten>`**, đi tới từ thẻ ở trang **Dự án**. Lý do: cài đặt và trạng thái
  (sẵn sàng deploy, lịch sử, bộ đếm) đều theo dự án nên để chung một chỗ; trang **Cài đặt** đã duyệt (D19, mockup
  15/10) là **chỉ đọc**, mỗi mục kèm lệnh CLI — thêm nút ghi vào đó sẽ phá luật của trang đó. Router thật đã nhận
  đường con (`mucCua` trong `frontend/src/menu.js`) nên mục "Dự án" vẫn sáng, không thêm mục menu.
- **Nút TẠM DỪNG toàn trạm ở thanh trên, cạnh Estop**, cùng hình nút Estop nhưng màu vàng: nút dừng phải bấm được từ
  mọi trang (như Estop); màu khác để không nhầm với dừng khẩn toàn bộ. Khi bật có băng vàng dưới thanh trên, cùng kiểu
  băng Estop. Phương án khác (chỉ ở trang Dự án) ở câu hỏi mở 16.
- **Nút TẠM DỪNG dự án** ở góc phải đầu trang Tự động của dự án đó.
- Các mục menu khác giữ mockup 15/10 (trang tạm có link sang bản đã duyệt).

## Phần nào thuộc spec nào
| Phần giao diện | Thuộc |
| --- | --- |
| Sẵn sàng deploy, nút Deploy, bộ đếm hỏng, lịch sử, việc chờ Đại ca kèm lý do, công tắc tự merge, điều kiện, 3 lệnh, tự deploy, TẠM DỪNG dự án/toàn trạm, chip ở trang Dự án | OpenSpec change [`tu-merge-tu-deploy`](../../../openspec/changes/tu-merge-tu-deploy/) (bead `bs-2bd.3`, D69–D80) |
| Khối "Agent tự cập nhật việc" (công tắc chính + 3 nút con, mặc định tắt), chip "agent cập nhật việc", toàn bộ phần thêm trên thẻ việc ở `#/cong-viec` | Spec riêng của `bs-2bd.5` (D81–D86, `docs/quyet-dinh/2026-10-18-agent-tu-cap-nhat-viec.md`) — do agent khác viết; mockup này chỉ vẽ chỗ đặt theo D85 "chung màn cài đặt" |

## Thành phần mới (sẽ vào `DESIGN_SYSTEM.md` khi duyệt)
Công tắc `role="switch"` (`.cong-tac`), chip "luôn bật" có ổ khoá, băng tạm dừng (`.bang-tam-dung`), biến thể vàng của
nút Estop, khối báo trong trang (`.td-bao`), dòng tiến độ và lý do bị chặn trên thẻ việc. Màu chỉ dùng token đã có
trong `frontend/src/kieu/nen.css` (chép vào `them.css` cho mockup), không thêm token mới.
