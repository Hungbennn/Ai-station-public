# Lỗ G3.9 (`submit` lọt vào phiên Đại ca) — 18/10/2026 đêm

Bối cảnh: G3 lần 22:03 — tram-kiem (qua `sudo` từ Terminal của Đại ca, KHÔNG có hồ sơ Seatbelt) `launchctl submit` → 0,
job hiện trong `gui/501`. Claude + Codex (astra high) thảo luận 2 vòng (`.handover/thao-luan-phien-rieng/v1-codex.md`,
`v2-codex.md`): lượt thật luôn có hồ sơ (`boc_luot`, `deny job-creation`), nên trước hết đo rào hồ sơ (G3.11 giai đoạn 1,
không sudo mật khẩu). Phát hiện kèm: mọi user trạm (`tram-kiem`, `tram-khe1`, `tram-tho`) có nhóm chính `staff`;
`/Users/dai-ca` là 750 nhóm staff, hồ sơ cho `file-read*` toàn cục → đọc được file 644 trong nhà Đại ca.

| # | Câu hỏi | Đại ca chọn |
|---|---|---|
| D158 | Thảo luận thiết kế khó | Claude bàn với Codex `gpt-6-astra` effort **high** nhiều vòng trước khi chốt; quá 5 vòng chưa thống nhất thì báo Đại ca. |
| D159 | Rào hồ sơ chặn được rồi thì có giữ cách chạy cũ (agent kiểm bật từ phiên Đại ca) không | **Tách phiên bằng mọi giá**: dù giai đoạn 1 đạt vẫn đo + làm bộ chạy kiểm KHÔNG kế thừa phiên Đại ca (giai đoạn 2, M1 của v2: chạy từ miền system dưới UID quản lý ≠ 501/503, giữ Seatbelt). Sổ tay giữ tiêu chí "S6 đóng tới khi cắt kế thừa phiên". Sửa quyền đọc nhà Đại ca vẫn bắt buộc. |
| D160 | Bộ quản lý kiểm (19/10, sau G3.11/G3.12 sáng 19/10 và phân tích `.handover/thao-luan-phien-rieng/v3-codex.md`) chạy dưới tài khoản nào | **Tạo tài khoản mới `tram-quan-kiem`** (nonroot, nhóm riêng, UID do bộ cài chọn), không dùng lại `tram-tho` (giữ token máy + quản lý thợ). |
| D161 | `contactsd` (Apple, launchd tự bật dưới tram-kiem, đo 19/10 12:49: chặn G3.11 + G3.12 ở kiểm trước, tự tắt sau vài phút) | **Cho qua** như D157 (khớp nguyên văn `/System/Library/Frameworks/Contacts.framework/Support/contactsd`, ppid 1, uid=ruid=tài khoản đó, bản 24G90). Đại ca: "nếu vướng thì em cho qua đi". |
| D162 | Tiến trình hệ thống Apple macOS tự bật dưới tài khoản trạm (tram-kiem, tram-quan-kiem, khe) khi xác nhận dọn | **Cho qua chung, không liệt kê từng cái** (thay danh sách cứng D157/D161): executable do nhân trả (proc_pidpath) nằm trong thư mục hệ thống chỉ Apple ghi được — `/System/`, `/usr/libexec/`, `/usr/sbin/` — cộng ppid 1 và uid=ruid=chính tài khoản đó. **Trừ** shell/trình thông dịch và lệnh thường ở `/bin`, `/usr/bin` (mã lạ có thể để lại `sh`/`python` mồ côi dưới launchd). Bước dọn vẫn giết mọi thứ dưới UID; ngoại lệ chỉ áp cho bước "xác nhận không còn tiến trình". Đại ca 19/10: "tiến trình của Apple macOS thì cứ cho qua đi, đó là tiến trình hệ thống". Cũng 19/10: dừng sửa kịch bản đo G3.12, **làm thẳng** bộ quản lý kiểm (D159/D160); đo dưới tài khoản quản lý gộp vào G4. |
