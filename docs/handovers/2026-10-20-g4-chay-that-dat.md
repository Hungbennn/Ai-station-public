# 20/10: G4 chạy thật trên máy B — ĐẠT, đã cài CHÍNH THỨC (còn kiểm khởi động lại)

## Kết quả đo (máy B, macOS 15.6.1 24G90, main ce347a8)
- B1–B4 xong; hồ sơ Seatbelt v3 (đọc chung, cấm chỗ riêng tư) cài và khớp manifest.
- B5: lượt thật qua bộ quản lý (`tram.quan_kiem.g4 sach`) **`"dat": true` 3 lần**, cả 6 lệnh policy pass (~20 s/lượt).
  `sudo -k; sudo -n -u tram-kiem -- /usr/bin/true` → `ma=1` (Đại ca không còn chạy thẳng dưới tram-kiem).
- B6: TERM client giữa lượt (8 s) → client mã 143, không báo đạt, cổng tự **đóng**. (Ctrl-C không dùng được từ shell
  nền vì SIGINT bị bỏ qua cho tiến trình nền.)
- B7 **chưa làm**: Đại ca điều khiển qua AnyDesk, máy không có dịch vụ AnyDesk chạy trước đăng nhập và không tự đăng
  nhập → khởi động lại sẽ mất kết nối. Làm khi Đại ca ngồi ở máy.
- B8: `~/tram-quan-kiem-bang-chung-g4.json` — dấu vân tay `70443099…29c4`, `ket_luan` toàn false (chờ ký).
  Cài chính thức (`cau_hinh.py`) đòi đủ 8 mục true gồm `reboot` → chờ B7.

## Sửa trong ngày (đều đã ghép main)
pyc Python kiểm (`-B`), vault Apple, DARWIN_USER_* bỏ qua `com.apple.*` + gỡ cờ/quyền trước rm, metadata các cha của
goc, D157 (ESRCH/đổi định danh sau `kill -1` → tính là còn, chờ chụp lại), lý do hỏng Uq trả về client (stderr),
launchd G4 chỉ xét nhãn lượt (print ≠ 0 = vắng), cổng thật loại ra dịch vụ nền ngoài mốc (chặn job dựa Seatbelt
`deny job-creation`, đối chứng G4 đạt; kịch bản G3 vẫn bắt job), dọn đồ đo G4 (canary-link) khỏi gốc lượt.

## Việc tiếp
1. Đại ca ở máy: khởi động lại → đăng nhập → nhắn "xong".
2. Em: `launchctl print system/vn.tram.quan-kiem` (state running), `tram giao mo-cong-kiem --dong-y`,
   `bash .handover/g4-luot.sh` → kỳ vọng DAT; nếu `vn.tram.tho` tự nạp lại sau reboot thì đưa Đại ca lệnh bootout.
3. Em chạy lại `tram.quan_kiem.bang_chung` (dấu vân tay đổi nếu đã cài lại), Đại ca đọc + ký (đặt 8 mục true).
4. Đại ca: `"$TRAM_PY" -m tram.chu.lenh_quan_kiem cai --repo "$PWD" --deps-manifest "$DEP_MANIFEST" --bang-chung-g4 <file>`.

Công cụ một lệnh: `.handover/g4-mot-lenh.sh` (cài lại + mở cổng + lượt, log `.handover/g4-mot-lenh.log`),
`.handover/g4-luot.sh` (chỉ lượt, không mật khẩu), `.handover/doc-log-kiem.sh` (đuôi log lệnh kiểm của Uq, cần sudo).

## Cập nhật 11:53 — đã cài chính thức
- Đại ca chọn bỏ `reboot` khỏi điều kiện (`MUC_G4` còn 7 mục, commit 0a700e3 do Đại ca tự ghi).
- Cài chính thức lần 1: Uq dừng mã 1 — vân tay bằng chứng đọc `Cellar/git/.../test.netrc` (0600) bị từ chối. Sửa 30ac30b:
  tệp không cho mọi người đọc chỉ ghi chủ/quyền/cỡ (rà máy: chỉ có đúng tệp đó).
- Lượt thật ĐẠT lần 5 (bản 30ac30b), Đại ca ký 7 mục, cài chính thức: `g4 = False`, `vn.tram.quan-kiem` running
  (chưa thoát lần nào), `tram giao mo-cong-kiem` → `[XANH] Bộ quản lý kiểm: mo`.
- Còn lại: khởi động lại máy khi Đại ca ngồi ở máy (máy dùng AnyDesk, không có dịch vụ AnyDesk trước đăng nhập), sau đó
  `launchctl print system/vn.tram.quan-kiem` + mở cổng. Lệnh gộp lần sau: `.handover/hoan-tat-chinh-thuc.sh`.

## Cập nhật chiều 20/10 — dashboard + máy A
- GitHub riêng tư: `Hungbennn/ben-station` (remote `github`; Đại ca tự `git push github main`, agent không push).
- `vn.tram.api` chạy; `tailscale serve` → `https://may-b.tailnet-vi-du.ts.net` (tailnet only).
  `~/.tram/cau-hinh.yaml` máy B đã có `ten_may_b`, `dashboard_url`, `dai_ca_logins: [dai-ca@example.com]`.
- Máy A: hook điều phối cài (mã trong Keychain A, băm trên B qua `ghi_bam`), đèn Điều phối sáng; skill phỏng vấn
  đã cài; passkey thiết bị đã đăng ký (`tram chu passkey cap-ma` trên B).
- Còn đỏ: phòng máy chủ "Không đọc được beads của dự án hr-codex" — `du-an/hr-codex.yaml` `duong_dan` là đường
  máy A; máy B chưa có repo HR Codex (`Hungbennn/hr-interview-copilot`). Chờ Đại ca chọn đưa lên B.
- Tiếp: thử trọn skill phỏng vấn → B tạo feature (G6, bs-8eh.21); spec + plan tự merge/deploy (bs-2bd.3).
