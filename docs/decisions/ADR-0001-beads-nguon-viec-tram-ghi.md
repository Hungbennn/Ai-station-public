# ADR-0001 — Beads là nguồn sự thật của việc; trạm là bên ghi

**Trạng thái:** Chấp nhận (hồi tố) · 2026-10-17 — quyết định có từ trước, ghi lại từ code và quyết định đã chốt

**Bối cảnh**
Trạm điều phối nhiều dự án, vốn đã giữ việc trong Beads. Agent chạy không người canh; nội dung bead là dữ liệu
không tin cậy. Phải chọn nơi giữ việc và ai được sửa nó.

**Quyết định**
Beads của từng dự án giữ **việc**; `docs/` giữ **tri thức** (Q2). Trạm chủ là bên ghi Beads dự án con (Q11): nhãn cột,
nhận việc, cột 3, escalation, bead con — `--actor tram/*`, chỉ khi `bat_ghi: true`. Agent thợ không gọi `bd`, chỉ báo
qua `tram bao`; khe spec chỉ đề xuất bead. Máy A không `bd create`: B tạo bead feature qua API, chống trùng (D46, D47).

**Vì sao**
Giữ đúng ranh giới việc/tri thức Đại ca đã dùng. Một bên ghi duy nhất thì mỗi lần ghi có ID thao tác bền và đối
soát được sau sự cố (spec 4 §5.4). Agent không tự đổi cột hay tự mở việc, nên chữ trong bead không nâng quyền (INV-002).

**Phương án đã loại**
- Kho việc riêng trong SQLite của trạm: mất nguồn việc chung với phiên tay của Đại ca (suy từ code, chưa xác nhận).
- Agent thợ tự ghi `bd`: máy thợ không được giữ quyền ghi Beads (Q11, spec 3 §7.2). Jira: non-goal (`PROJECT.md`).
- Skill máy A tự `bd create`: không chống trùng bền khi kết quả chưa rõ — thay bằng D46.

**Hệ quả**
Được: một luồng ghi kiểm soát được. Mất: Beads và SQLite không có giao dịch chung, chỉ thu hẹp cửa sổ đua (đã chấp
nhận, spec 4 §5.1). Dolt server trên B (Q11) chưa dựng. **Mục tiêu chưa hiệu lực** (Đại ca, 17/10): cho agent tự cập
nhật việc — cần spec riêng; khi duyệt, ADR này bị thay một phần.

**Nguồn**
[Spec kiến trúc](../specs/2026-10-12-tram-dieu-phoi-kien-truc.md) Q2, Q11, §5.7, §8 · [spec 4](../specs/2026-10-13-phan-4-giao-viec.md) §5.4 · D31, D46, D47
([16/10](../quyet-dinh/2026-10-16-chot-sau-review-dot6.md)) · `tram/beads/bd.py`, `tram/cham_cot/ghi.py`, `tram/yeu_cau/so_nhan.py`, `vai/quyen/coder.json`.
