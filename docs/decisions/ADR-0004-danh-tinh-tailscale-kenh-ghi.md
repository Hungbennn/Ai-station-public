# ADR-0004 — Danh tính qua Tailscale: xem tự do trong tailnet, ghi qua kênh có xác thực

**Trạng thái:** Chấp nhận (hồi tố) · 2026-10-17 — quyết định có từ trước, ghi lại từ code và quyết định đã chốt

**Bối cảnh**
Dashboard chạy trên máy B, Đại ca mở từ máy A hay điện thoại; một người dùng; không mở ra Internet. Header danh tính
Tailscale trên TCP `127.0.0.1` giả được bởi mọi tiến trình cục bộ, kể cả agent dưới principal khác (spec 2 §4 mục 2b).

**Quyết định**
tram-api chỉ nghe `127.0.0.1:7700`, ra tailnet qua `tailscale serve`, không funnel; `Host` lạ → 421. **Đọc** không cần
đăng nhập — cố ý (Đại ca, 17/10). **Ghi** cần đủ: kênh hợp lệ + `Tailscale-User-Login` thuộc `dai_ca_logins` + `X-Tram: 1`
+ `Origin` máy B. Kênh `header` hiện hành là **tạm**: chuyển sang `unix-socket` (socket trong thư mục 0700 của tài
khoản trạm) **trước khi giao việc thật** (Đại ca, 17/10; D51, cổng G29).

**Vì sao**
Tailscale đã là lưới riêng của Đại ca, không cần hệ đăng nhập; API đọc đã lọc (không bí mật, không `ma_giao`). Header
đủ khi chưa có thợ trên B; khi có, chỉ kênh mà principal thực thi không mở được mới chặn được header giả.

**Phương án đã loại**
- Funnel hay đăng nhập ngoài Tailscale (spec 2 §10). Bắt đăng nhập để xem: Đại ca chọn xem tự do.
- Mã truy cập dài + cookie: phương án lùi của spec 2 §4 khi header không đạt; chưa cần.

**Hệ quả**
Mọi thiết bị trong tailnet đọc được dashboard. Tới khi đổi kênh, tiến trình cục bộ trên B giả được yêu cầu ghi — nên
không bật giao việc thật với kênh `header`. Hook máy A và memory phiên tay đòi thêm mã riêng (D24, spec 1b §9.3);
API thợ dùng token máy ([ADR-0003](ADR-0003-phieu-khe-token-may.md)).

**Nguồn**
[Spec 2](../specs/2026-10-12-phan-2-dashboard.md) §3, §4, §10 · [spec 3](../specs/2026-10-13-phan-3-may-tho-han-muc.md) §7.3 mục 4 · D24, D51 ·
`tram/api/bao_mat.py`, `tram/api/kenh_ghi.py`, `tram/cau_hinh/cach_ly.py`.
