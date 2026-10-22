# Theo dõi công việc bằng Beads

Project: `ben-station`
Status: `ACTIVE`
Cập nhật: `2026-10-17`

## Mục đích
Sở hữu **cách theo dõi công việc của repo trạm**. Việc còn dở không nằm trong tài liệu markdown.
Không sở hữu: cú pháp lệnh (chạy `bd prime`), trạng thái hệ thống (`CURRENT_STATE.md`), tri thức thường
trực (`docs/AGENTS.md` giữ bảng sở hữu), cách trạm đọc/ghi Beads của dự án con (`ARCHITECTURE.md`, ADR-0001).

## Hai kho beads khác nhau — đừng nhầm
| | Kho việc của repo trạm | Kho beads của dự án con (vd HR Codex) |
| --- | --- | --- |
| Chứa gì | việc phát triển chính ben-station | việc của dự án mà trạm điều phối |
| Mã việc | `bs-…` (vd `bs-2bd`) | tiền tố riêng của dự án đó |
| Nằm ở | `.beads/` của repo này | trong repo của dự án đó |
| Ai ghi | agent điều phối trên repo này, qua `bd` | **chỉ trạm**, qua `tram/beads/bd.py`, và chỉ khi dự án `bat_ghi: true` |
| Agent làm repo trạm được | `bd create/update/close` (trừ subagent code) | **không ghi gì**; test dùng bản giả `tests/bd_gia.py` |

Agent thợ của trạm hiện **không** tự sửa danh sách việc của dự án con; trạm ghi thay. Đại ca muốn đổi
(cho agent tự cập nhật việc) — cần spec riêng, xem `PROJECT.md`.

## Ranh giới docs / việc
**Beads trả lời "còn việc gì, việc nào làm được ngay, việc nào chặn việc nào"; `docs/` trả lời "hệ thống là
gì, luật là gì, đã quyết những gì".** Việc phát sinh giữa phiên thì tạo bead ngay — không viết TODO trong
code, không chèn gạch đầu dòng vào `CURRENT_STATE.md` hay bàn giao.

| Trước kia nằm ở docs | Giờ |
| --- | --- |
| "Việc tiếp theo" trong bàn giao, `tasks/todo.md` | `bd ready` |
| Phần mã còn thiếu, lỗi tồn đọng | `bd list --status=open` |
| Chờ Đại ca chốt | bead có quan hệ chặn chờ quyết định |
| Nợ chấp nhận được | bead `chore` P4 |
| Việc nào chặn việc nào | `bd dep add <việc> <bị-chặn-bởi>` |
| Nhóm việc lớn (20% còn lại, chạy thật) | epic, ví dụ `bs-2bd` |

Bàn giao phiên vẫn được ghi **một** "Việc tiếp theo" trong khối TÓM TẮT, kèm mã bead.

## Quy trình một phiên
1. `bd ready` · 2. `bd show <id>` · 3. `bd update <id> --claim` · 4. làm theo `DEVELOPMENT_PLAYBOOK.md` và
`AGENT_RULES.md` · 5. việc phát sinh: `bd create`; quan hệ chặn: `bd dep add` · 6. `bd close <id>` khi xong
**và đã kiểm chứng** (QC đạt, test xanh, ghép xong) · 7. kết phiên: bàn giao + `CURRENT_STATE.md` nếu trạng thái đổi.

Subagent code không chạy `bd`; agent điều phối nhận, đóng và tạo bead thay.

## Quyền git
Agent **không** tự `git push`, **không bao giờ** `bd dolt push`. `git commit` chờ Đại ca duyệt. Báo cáo và
đề xuất lệnh.

## Lưu ý vận hành
- Kho Dolt chạy **nhúng** trong lệnh `bd` (không có máy chủ), cơ sở dữ liệu `bs`, dữ liệu ở
  `.beads/embeddeddolt/` — git bỏ qua thư mục này. `git push` **không** mang danh sách việc đi đâu cả.
- Sao lưu cục bộ ở `.beads/backup/`; hỏng ổ là mất cùng. Đường khôi phục từ xa **chưa có** vì cấm `bd dolt push`.
- `.beads/` trong worktree không có `embeddeddolt/`: chạy `bd` ở checkout chính `/Users/dai-ca/Developer/Ben Station`
  (suy từ cây thư mục, chưa kiểm hành vi `bd` trong worktree).
- `.beads/interactions.jsonl` có trong git và đổi theo mỗi lần dùng `bd`; đừng ngạc nhiên khi nó hiện trong `git status`.
- Spec kiến trúc (Q11) định cho Beads của mọi dự án con chạy Dolt server trên máy B; phần này **chưa dựng**.
  Khi dựng, cách nối và sao lưu ghi ở `DEPLOY.md`.
