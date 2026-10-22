# ADR-0005 — Trạm tự kiểm lại mọi việc trong vùng cách ly trước khi tin

**Trạng thái:** Chấp nhận (hồi tố) · 2026-10-17 — quyết định có từ trước, ghi lại từ code và quyết định đã chốt

**Bối cảnh**
Agent báo "xong" kèm log có thể sai; lệnh kiểm chạy chính mã agent vừa sửa — mã không tin cậy, có thể để lại tác vụ
hay dữ liệu làm hỏng lượt kiểm sau (thiết kế 3c §1).

**Quyết định**
"Báo xong" khác "đã kiểm chứng": trạm tự chạy lại mọi lệnh bắt buộc của phiếu tại SHA đã công bố, sau khi kiểm đường
dẫn cấm, trước QC và cột 3. Chạy dưới principal riêng `tram-kiem`, không credential, **không root lúc chạy**: bản chép
từ `git archive` (D22, D40), mọi lệnh trong Seatbelt cấm mặc định, cấm mạng kể cả loopback và IPC, HOME/TMP riêng
mỗi lượt (D45, D48). Có bất thường → cổng đóng, chỉ Đại ca mở bằng `tram giao mo-cong-kiem` (D49).

**Vì sao**
Digest log chỉ chứng minh log nguyên vẹn, không chứng minh test đạt. Trên macOS không root, chỉ Seatbelt chặn trước
được việc ghi, IPC và tạo tác vụ cho cả cây tiến trình (thiết kế 3c §2–3).

**Phương án đã loại**
- Tin log/digest của thợ. Helper root, ACL/`chmod` để trao quyền (D22). Quét/dọn sau lượt thay cho cưỡng chế (D45).
- Helper root giữa các lượt hay VM mỗi lượt: chỉ xét nếu cổng G4 bác thiết kế hiện tại (thiết kế 3c §5).

**Hệ quả**
Dự án phải test được không mạng (D48); cây lạ (CRLF dưới `text`, submodule…) bị từ chối (D50); Đại ca mở cổng tay.
Cách ly khe chỉ thử cơ chế `user` (D53). **Cố ý** (Đại ca, 17/10): agent thợ khi làm việc **được vào mạng** — chỉ lượt
kiểm lại bị cấm; hồ sơ sandbox khe để `allow default` (suy từ code, chưa xác nhận). Chưa có bằng chứng OS: chờ G3, G4.

**Nguồn**
[Spec kiến trúc](../specs/2026-10-12-tram-dieu-phoi-kien-truc.md) §5.2 · [spec 3](../specs/2026-10-13-phan-3-may-tho-han-muc.md) §7.3 · [spec 4](../specs/2026-10-13-phan-4-giao-viec.md) §6.2 · D22, D40 ([15/10](../quyet-dinh/2026-10-15-chot-dot-4.md)),
D45, D48–D53 ([16/10](../quyet-dinh/2026-10-16-chot-sau-review-dot6.md)) · [thiết kế 3c](../handovers/2026-10-16-thiet-ke-3c-boundary.md) · `tram/giao_viec/kiem_lai.py`, `tram/giao_viec/principal_kiem.py`, `tram/kiem/`, `tram/tho/sandbox.py`.
