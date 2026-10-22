# ADR-0008 — Dashboard là SPA Vue dịch sẵn, phục vụ cùng gốc dưới CSP chặt

**Trạng thái:** Chấp nhận (hồi tố) · 2026-10-17 — quyết định có từ trước, ghi lại từ code và quyết định đã chốt

**Bối cảnh**
Dashboard hiện nội dung bead (dữ liệu không tin cậy, có thể do agent viết) và có nút ghi (kéo cột, duyệt, estop).
Một trang bị chèn script sẽ ghi được thay Đại ca, vì danh tính đến từ Tailscale chứ không từ thao tác của người dùng.

**Quyết định**
SPA Vue 3 + vue-router chế độ hash; component `.vue` dịch sẵn lúc build bằng `@vitejs/plugin-vue`; build ra `dist/`,
tram-api phục vụ tĩnh cùng gốc. Mọi phản hồi mang CSP chặt (`default-src 'none'`, `script-src 'self'`, không
`unsafe-eval`, không `unsafe-inline`) cùng `nosniff`, `X-Frame-Options: DENY`. Cấm `v-html`/`innerHTML`; chữ từ server
hiện dạng text, lọc ký tự điều khiển/bidi. Hai bộ quét: `kiem-an-toan.mjs` (nguồn), `kiem-dist.mjs` (bundle).

**Vì sao**
Vue dịch template lúc chạy cần `unsafe-eval`; dịch sẵn mới bật được CSP chặt (G13 plan 2a, Đại ca đồng ý 13/10). Cùng
gốc với API nên `connect-src 'self'` là đủ. Chọn hash để phục vụ tĩnh không cần luật viết lại đường dẫn (suy từ code, chưa xác nhận).

**Phương án đã loại**
- Vue dịch template lúc chạy (cần `unsafe-eval`); chèn HTML bằng `v-html`.
- Loader 3D dùng WebAssembly (Draco, KTX2 — cần `wasm-unsafe-eval`, plan 2c G1). Nới CSP khi một gói đòi: phải dừng, hỏi Đại ca.

**Hệ quả**
Mỗi thư viện frontend mới phải qua `kiem-dist`; văn phòng 3D tự dựng hình, không loader. Máy B cần bước build; `dist/`
không commit. Font tự host (D35), hợp `font-src 'self'`. Trang mới cần mockup được duyệt trước (D20, D33, D39).

**Nguồn**
[Spec 2](../specs/2026-10-12-phan-2-dashboard.md) §3, §4 mục 4 và 6, §8 · [plan 2a](../plans/2026-10-13-lat-2a-dashboard.md) G13 · [plan 2c](../plans/2026-10-13-lat-2c-van-phong-3d.md) G1 · D35 ·
`tram/api/bao_mat.py`, `tram/api/app.py`, `frontend/kiem-an-toan.mjs`, `frontend/kiem-dist.mjs`, `frontend/src/main.js`.
