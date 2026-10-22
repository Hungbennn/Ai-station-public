# ADR-0002 — Nhật ký sự kiện SQLite chỉ ghi thêm; trạng thái tính lúc đọc

**Trạng thái:** Chấp nhận (hồi tố) · 2026-10-17 — quyết định có từ trước, ghi lại từ code và quyết định đã chốt

**Bối cảnh**
Nhiều tiến trình trên máy B (quét, tram-api, báo tin, memory, giao việc) và máy thợ ở xa cùng sinh sự kiện. Dashboard,
Telegram, bảng điểm thợ và memory cần đọc chung một lịch sử. Trạm chỉ chạy trên Mac của Đại ca.

**Quyết định**
Chỉ lưu sự kiện; trạng thái hiển thị tính lúc đọc (Q12). Một file SQLite `~/.tram/su-kien.db` (WAL) trên trạm chủ cho
mọi dự án; bảng `su_kien` chỉ ghi thêm, không sửa; chỉ tiến trình của tài khoản trạm ghi, thợ gửi qua tram-api.
Kho vận hành (phiếu, thao tác ghi, sổ yêu cầu feature) là bảng riêng cùng file, sửa tại chỗ trong giao dịch.

**Vì sao**
Ý "sự kiện bền, trạng thái tính lúc đọc" lấy từ agent-orchestrator: không có kho trạng thái thứ hai để lệch, đọc lại
được từ một mốc. SQLite có sẵn, cho giao dịch nguyên tử khi cấp phiếu (spec 3 §6.6).

**Phương án đã loại**
- Kho trạng thái riêng cho dashboard, cập nhật tại chỗ: trái Q12 (spec 2 §3).
- Máy thợ tự ghi kho, hay máy chủ DB riêng: trái "chỉ trạm chủ ghi" (§5.8); không có lý do ghi lại cho việc không dùng
  máy chủ DB (suy từ code, chưa xác nhận).

**Hệ quả**
Được: lịch sử đầy đủ, nhiều bên đọc độc lập. Mất: phải suy trạng thái mỗi lần đọc; nhiều tiến trình ghi cùng file
nên cần WAL + timeout. **Nợ đã biết** (Đại ca, 17/10): lược đồ chỉ `CREATE TABLE IF NOT EXISTS`, **chưa có migration** —
tạm, phải thêm trước chạy thật. Chưa có luật hết hạn sự kiện (suy từ code, chưa xác nhận).

**Nguồn**
[Spec kiến trúc](../specs/2026-10-12-tram-dieu-phoi-kien-truc.md) Q12, §5.8, §6 · [spec 0+1a](../specs/2026-10-12-phan-0-1a-cham-cot.md) §4.1 · [spec 2](../specs/2026-10-12-phan-2-dashboard.md) §12.2–12.3 ·
[spec 3](../specs/2026-10-13-phan-3-may-tho-han-muc.md) §6.6 · `tram/su_kien/ket_noi.py`, `tram/su_kien/kho.py`, `tram/phieu/luoc_do.py`, `tram/thao_tac/kho.py`.
