# Điểm vào cho coding agent — ben-station

> **Bản public:** việc của cộng đồng nằm ở GitHub Issues và [ROADMAP.md](ROADMAP.md), không có Beads. Đóng góp qua
> fork + Pull Request theo [CONTRIBUTING.md](CONTRIBUTING.md); luật "không push" bên dưới là luật cho agent chạy trong trạm.

Gọi người dùng là **Đại ca**, xưng **Em**, viết tiếng Việt.

Bắt đầu từ **[docs/AGENTS.md](docs/AGENTS.md)** — bộ định tuyến tài liệu: thứ bậc nguồn sự
thật, bảng sở hữu thông tin, và lối đọc cho từng loại task.

Đọc mỗi phiên, theo thứ tự:

1. `docs/AGENT_RULES.md` — luật vận hành, kill list, lệnh cấm
2. `docs/PROJECT.md` — sản phẩm là gì, không làm gì
3. `docs/ARCHITECTURE.md` — bản đồ hệ thống và ràng buộc
4. `docs/CURRENT_STATE.md` — đang ở đâu; dòng *Bàn giao gần nhất*

Các tài liệu còn lại chỉ đọc khi task chạm tới — `docs/AGENTS.md` chỉ rõ khi nào.

Mã nằm trong `tram/` (Python) và `frontend/` (Vue). Test:

```bash
tests/chan_host/chay.sh -q             # bộ chặn host + git giả; KHÔNG chạy pytest trần — AGENT_RULES.md §13
cd frontend && npm run kiem && npm run build && npm run kiem-dist
```

## Theo dõi công việc

Việc còn dở nằm ở **Beads (`bd`)**, không nằm trong docs. Quy ước:
**[docs/BEADS.md](docs/BEADS.md)**.

```bash
bd ready                # việc làm được ngay
bd show <id>            # đọc trước khi nhận
bd update <id> --claim  # nhận việc
bd close <id>           # đóng khi đã kiểm chứng
```

Liệt kê việc trước, chỉ làm khi Đại ca bảo "bắt đầu". Commit chỉ trên nhánh task trong worktree
(`docs/DEVELOPMENT_PLAYBOOK.md`); commit hay ghép vào `main` theo `AGENT_RULES.md` §11. Không bao giờ
`git push` hay `bd dolt push`.
