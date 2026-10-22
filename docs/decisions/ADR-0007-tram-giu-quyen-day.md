# ADR-0007 — Trạm giữ quyền đẩy code và mở PR; chỉ Đại ca merge

**Trạng thái:** Chấp nhận (hồi tố) · 2026-10-17 — quyết định có từ trước, ghi lại từ code và quyết định đã chốt

**Bối cảnh**
Agent viết code trong worktree trên máy thợ. GitHub không biết `luot`, nên một lần push trễ của lượt đã bị thu hồi vẫn
có thể đè lên nhánh (spec 3 §6.4). Gộp vào nhánh chính là bước khó đảo ngược.

**Quyết định**
Agent từ xa tự commit; B do quản lý chốt sau thu hồi (QĐ3-A, [ADR-0009](ADR-0009-quyen-khe-b.md)); quyền vai cấm `git push`, `git remote`, `git fetch`. Chỉ trạm cập nhật nhánh công bố
`tram/<bead>` sau khi kiểm lượt: máy B trạm tự lấy từ kho thợ rồi đẩy, máy từ xa đẩy ref tạm theo lượt rồi trạm
compare-and-swap (D4 "lai", chính thức khi S7 đạt). Trạm mở PR bằng `gh`, chỉ trỏ commit có bằng chứng, **không
merge**; nhánh chính bật branch protection; **chỉ Đại ca merge** (Q7). Trạm xác minh merge rồi mới đóng bead.

**Vì sao**
Chặn theo lượt tới tận remote chỉ làm được ở trạm (§5.5). Merge là ngoại lệ duy nhất của quy tắc thận trọng (Q7):
Đại ca muốn tự xem trước khi mã vào nhánh chính (điểm dừng #2, Q6).

**Phương án đã loại**
- Thợ đẩy thẳng nhánh công bố với `--force-with-lease`: chỉ giảm xung đột, không chứng minh (spec 3 §6.4).
- Trạm tự merge, merge queue (spec 4 §17); merge từ dashboard (spec 2 §10).

**Hệ quả**
Mọi bước sau dùng SHA trạm đã công bố. Đại ca là điểm chờ ở merge. `cong_bo.phuong_an` chưa chọn thì trạm không công
bố gì. **Mục tiêu chưa hiệu lực** (Đại ca, 17/10): tiến tới tự merge và tự deploy, làm sớm; cần spec mới đổi điểm dừng
#2 và luật cấm merge. Tới khi spec đó được duyệt, Đại ca vẫn merge; deploy, migrate, xoá dữ liệu vẫn do Đại ca (Q6).

**Nguồn**
[Spec kiến trúc](../specs/2026-10-12-tram-dieu-phoi-kien-truc.md) Q6, Q7, §5.5 · [spec 3](../specs/2026-10-13-phan-3-may-tho-han-muc.md) §6.4 · [spec 4](../specs/2026-10-13-phan-4-giao-viec.md) §6.4, §17 · D4, D34 ·
`tram/cong_bo/nguon_lai.py`, `tram/giao_viec/pr.py`, `tram/giao_viec/pr_merge.py`, `vai/quyen/coder.json`.
