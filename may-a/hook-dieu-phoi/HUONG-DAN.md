# Hook đèn Điều phối — cài trên máy A (Đại ca làm tay)

Hook này báo cho trạm (máy B) biết máy A đang có phiên Claude Code điều phối. Đèn phòng **Điều phối** trên trang Văn
phòng sẽ sáng khi có phiên, và xám khi phiên đã đóng hoặc 15 phút không có nhịp (spec 2 §5.5, plan 2e).

Hook chỉ gửi tên sự kiện và 16 ký tự băm của mã phiên. Nó **không** gửi prompt, thư mục hay transcript. Trạm không
với tới thì hook im lặng, không in gì và không chặn phiên. Mỗi bước (đọc Keychain, gửi HTTP) chờ tối đa 2 giây; cả
hook tối đa 4 giây rồi tự thoát (Claude Code còn tự dừng hook ở 5 giây).

Hook dùng **mã điều phối**, một mã riêng chỉ để gửi nhịp (D24). Mã này **khác** mã Đại ca của MCP phiên tay. Lộ mã
điều phối thì kẻ có mã chỉ bật/tắt được đèn giả, không đọc được memory, không mở được việc ghi nào khác.

## Điều kiện trước

1. Tailscale đã cài và đăng nhập trên máy A bằng tài khoản của Đại ca (D6, `bs-8eh.17`).
2. Dashboard đã chạy qua `tailscale serve` trên máy B (2a Task 26). Trang `https://<máy B>.<tailnet>.ts.net/` mở
   được từ máy A.
3. `/usr/bin/python3 --version` trên máy A in ra 3.9 trở lên. Nếu macOS hỏi cài Command Line Tools thì cài xong rồi
   mới làm tiếp. Không thì mỗi lần hook chạy sẽ bật hộp thoại cài đặt.

## Tạo mã điều phối (làm một lần)

Mở **Terminal.app** trên máy A, không dùng khung terminal của app Claude vì nó làm hỏng chuỗi dán vào ô ẩn.

1. Tạo mã vào clipboard, không hiện ra màn hình: `openssl rand -hex 32 | tr -d '\n' | pbcopy`
2. Lưu vào Keychain máy A. Chạy lệnh sau, dán mã khi được hỏi (hai lần):
   `security add-generic-password -s tram-dieu-phoi-ma -a "$USER" -w`
3. Đặt bản băm trên máy B: mở phiên Terminal.app tới máy B (ví dụ `ssh`), chạy `tram chu dat-ma-dieu-phoi`, gõ
   `dong-y`, dán mã hai lần. Trạm chỉ lưu sha256 ở khoá `dieu_phoi_ma_sha256` trong `~/.tram/cau-hinh.yaml`.
   Lệnh từ chối nếu mã trùng mã Đại ca.
4. Xoá clipboard: `pbcopy < /dev/null`

**Không** ghi mã vào `settings.json`, biến môi trường cố định hay bất kỳ file nào. Biến `TRAM_DIEU_PHOI_MA` chỉ dùng
cho lệnh kiểm nhanh bên dưới, không đặt trong cấu hình.

## Cài

1. Chép script: `mkdir -p ~/.claude/hooks && cp may-a/hook-dieu-phoi/hook_dieu_phoi.py ~/.claude/hooks/`
2. Gộp `settings.mau.json` vào `~/.claude/settings.json`: thêm khoá `env.TRAM_DIEU_PHOI_URL` với địa chỉ thật của
   máy B (chỉ `https://<tên máy>`, không có đường dẫn), rồi thêm bốn mục trong `hooks`. **Gộp**, không chép đè, vì
   file có thể đã có cấu hình khác.
3. Mở một phiên Claude Code **mới**. Gõ `/hooks` để xem bốn hook đã nhận, duyệt nếu Claude Code hỏi.

Muốn chỉ phiên mở trong một thư mục điều phối mới làm sáng đèn (C3 của plan 2e)? Đặt khối `hooks` và `env` vào
`<thư mục>/.claude/settings.json` thay cho `~/.claude/settings.json`.

## Kiểm nhanh không cần Claude

```bash
echo '{"hook_event_name":"Stop","session_id":"thu-tay"}' \
  | TRAM_DIEU_PHOI_URL=https://<máy B>.<tailnet>.ts.net /usr/bin/python3 ~/.claude/hooks/hook_dieu_phoi.py; echo $?
```

Kết quả mong đợi: in `0`, không in gì khác. Trong 5 giây, trang Văn phòng hiện "Điều phối · đang có phiên". Tắt
Tailscale rồi chạy lại: vẫn in `0` sau tối đa khoảng 4 giây.

## Gỡ

Xoá bốn mục hook và khoá `env.TRAM_DIEU_PHOI_URL` khỏi `settings.json`, xoá `~/.claude/hooks/hook_dieu_phoi.py`,
xoá Keychain: `security delete-generic-password -s tram-dieu-phoi-ma`. Trên máy B, xoá dòng `dieu_phoi_ma_sha256`
trong `~/.tram/cau-hinh.yaml`: route nhịp sẽ từ chối mọi lời gọi.

## Giả định chưa kiểm (spike ở plan 2e Task 5)

- Claude Code chạy hook `SessionStart`, `UserPromptSubmit`, `Stop`, `SessionEnd`. JSON trên stdin có
  `hook_event_name`, `session_id`. Hook được kế thừa khối `env`. Lệnh vượt `timeout` thì bị dừng và phiên đi tiếp.
- Phiên Claude Code trong app Claude desktop cũng đọc `~/.claude/settings.json`.
- `tailscale serve` gắn `Tailscale-User-Login` cho yêu cầu không đến từ trình duyệt, và giữ nguyên `Host`,
  `Origin`, `Authorization`.
- `python3` của macOS xác minh được chứng chỉ HTTPS của `tailscale serve`.
- Hạn 4 giây của cả hook giữ đúng khi DNS tên tailnet treo (Tailscale tắt).
