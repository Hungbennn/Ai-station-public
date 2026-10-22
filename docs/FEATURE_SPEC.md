# Đặc tả feature

Project: `ben-station`
Status: `ACTIVE`
Cập nhật: `2026-10-17`

## Mục đích và sở hữu
Sở hữu: bảng feature (lát đã làm, phần còn lại), nơi tìm quy tắc nghiệp vụ của feature **đã build mà chưa có
change OpenSpec nào chạm tới**, tiêu chí nghiệm thu chung.
Không sở hữu: việc còn dở (Beads — `docs/BEADS.md`), trạng thái chạy thật (`CURRENT_STATE.md`), từ vựng và bất biến
([PRODUCT_ARCHITECTURE.md](PRODUCT_ARCHITECTURE.md)), cách làm từng lát (plan trong `docs/plans/`).
Feature mới **không** mở mục quy tắc ở đây: đi qua OpenSpec ([OPENSPEC.md](OPENSPEC.md)). File này teo dần theo mỗi lần archive.

## Chữ "DONE (code)" nghĩa là gì
**Đã code và có test chạy offline xanh (bản giả thay hệ ngoài). CHƯA chạy thật** — chưa cổng nào ở mức hệ điều hành
đạt (xem `CURRENT_STATE.md`). Đừng đọc `DONE` là "dùng được trên máy thật". Lát 3c và P1 còn lỗi Chặn của review
Codex đợt 7, chờ plan V2 (xem hàng PROPOSED đầu tiên).

## Bảng feature
Cột Hợp đồng: spec đã duyệt (Tầng 3, nguồn gốc) và plan TDD của lát. Spec thắng khi docs mới nói khác (xem `docs/AGENTS.md`).

| Feature (lát) | Trạng thái | Hợp đồng | ADR |
| --- | --- | --- | --- |
| **0 + 1a** — chấm cột: trạm tự gắn nhãn cột cho bead mở (kèm sửa mã 1a cho 2a) | DONE (code) | [spec 0+1a](specs/2026-10-12-phan-0-1a-cham-cot.md) · [plan](plans/2026-10-12-phan-0-1a-cham-cot.md) · [plan sửa mã](plans/2026-10-13-sua-ma-1a-lat-2a.md) | ADR-0001 |
| **1a-2** — `tram du-an them` đủ bước, dự án mới `bat_ghi: false`, LLM chế độ chỉ soạn câu hỏi | DONE (code) | [spec 0+1a](specs/2026-10-12-phan-0-1a-cham-cot.md) · [plan](plans/2026-10-15-lat-1a-2-du-an-them-va-che-do-cau-hoi.md) | ADR-0001 |
| **1b-1** — memory chung nhiều dự án: dịch vụ cổng 7710, LanceDB, phạm vi | DONE (code) | [spec 1b](specs/2026-10-13-phan-1b-memory.md) · [plan](plans/2026-10-13-lat-1b-1-memory.md) | ADR-0006 |
| **1b-2** — MCP memory cho CLI máy thợ (theo phiếu) và phiên tay máy A chỉ đọc | DONE (code) | [spec 1b](specs/2026-10-13-phan-1b-memory.md) · [plan](plans/2026-10-13-lat-1b-2-mcp-nho.md) | ADR-0006 |
| **1b-3** — thăng cấp ký ức lên `/chung`, `/vai`; màn Ký ức | DONE (code) | [spec 1b](specs/2026-10-13-phan-1b-memory.md) · [plan](plans/2026-10-13-lat-1b-3-thang-cap-man-nho.md) | ADR-0006 |
| **1b-4** — nguồn ký ức từ phần 3/4 (bàn giao sau kiểm lại, trả lời escalation, trả về spec) | DONE (code) | [spec 1b](specs/2026-10-13-phan-1b-memory.md) · [plan](plans/2026-10-15-lat-1b-4-nguon-ky-uc-phan-3-4.md) | ADR-0006 |
| **2a** — dashboard "Bàn điều hành": ba cột, kéo cột, chốt, duyệt, estop | DONE (code) | [spec 2](specs/2026-10-12-phan-2-dashboard.md) · [plan](plans/2026-10-13-lat-2a-dashboard.md) | ADR-0004, ADR-0008 |
| **2b** — trang Đội ngũ AI + Usage | DONE (code) | [spec 2](specs/2026-10-12-phan-2-dashboard.md) · [plan](plans/2026-10-13-lat-2b-doi-ngu-usage.md) | ADR-0008 |
| **2c** — Văn phòng 3D isometric | DONE (code) | [spec 2](specs/2026-10-12-phan-2-dashboard.md) · [plan](plans/2026-10-13-lat-2c-van-phong-3d.md) | ADR-0008 |
| **2d** — dashboard bù khoảng trống (bảng điểm khe, PR trạm trong Phê duyệt…) | DONE (code) | [spec 2](specs/2026-10-12-phan-2-dashboard.md) · [plan](plans/2026-10-15-lat-2d-dashboard-bu-khoang-trong.md) | ADR-0008 |
| **2e** — đèn phòng Điều phối, hook phiên điều phối máy A | DONE (code) | [spec 2](specs/2026-10-12-phan-2-dashboard.md) · [plan](plans/2026-10-15-lat-2e-den-dieu-phoi.md) | ADR-0004 |
| **2f** — giao diện làm lại theo mockup đã duyệt (9 trang, nền + API) | DONE (code) | [spec 2](specs/2026-10-12-phan-2-dashboard.md) · [plan phần 1](plans/2026-10-16-lat-2f-1-nen-va-api.md) · [plan phần 2](plans/2026-10-16-lat-2f-2-cac-trang.md) · luật giao diện: [DESIGN_SYSTEM](DESIGN_SYSTEM.md) | ADR-0008 |
| **3a-1** — máy thợ + hạn mức, phần không qua cổng | DONE (code) | [spec 3](specs/2026-10-13-phan-3-may-tho-han-muc.md) · [plan](plans/2026-10-13-lat-3a-1-may-tho.md) | ADR-0003 |
| **3a-2** — máy thợ chạy thật (mã của phần chờ cổng) | DONE (code) | [spec 3](specs/2026-10-13-phan-3-may-tho-han-muc.md) · [plan](plans/2026-10-13-lat-3a-2-may-tho-chay-that.md) | ADR-0003 |
| **3b** — Mac thợ từ xa qua Tailscale + khe Codex | DONE (code) | [spec 3](specs/2026-10-13-phan-3-may-tho-han-muc.md) · [plan](plans/2026-10-13-lat-3b-tho-tu-xa-codex.md) | ADR-0003 |
| **3c** — principal riêng, kiểm lại trong vùng cách ly, trao quyền | DONE (code), còn lỗi Chặn đợt 7 | [spec 3](specs/2026-10-13-phan-3-may-tho-han-muc.md) §7, §14 · [plan](plans/2026-10-15-lat-3c-principal-kiem-trao-quyen.md) · [phụ lục thiết kế](handovers/2026-10-16-thiet-ke-3c-boundary.md) | ADR-0005 |
| **4a-1** — bộ giao việc, phần không qua cổng (chọn bead, chọn khe, pipeline) | DONE (code) | [spec 4](specs/2026-10-13-phan-4-giao-viec.md) · [plan](plans/2026-10-13-lat-4a-1-giao-viec.md) | ADR-0003 |
| **4a-2** — nối bộ giao việc vào trạm chạy thật (nhịp thợ, vòng tick) | DONE (code) | [spec 4](specs/2026-10-13-phan-4-giao-viec.md) · [plan](plans/2026-10-13-lat-4a-2-giao-viec-noi-that.md) | ADR-0003 |
| **4b** — luồng feature: phiếu yêu cầu, khe spec, duyệt spec | DONE (code) | [spec 4](specs/2026-10-13-phan-4-giao-viec.md) §7 · [plan](plans/2026-10-13-lat-4b-luong-feature.md) | — |
| **4c** — mở PR tự động, xác minh merge, cờ đỏ gitnexus, lớp 5 từ memory | DONE (code) | [spec 4](specs/2026-10-13-phan-4-giao-viec.md) · [plan](plans/2026-10-13-lat-4c-pr-gitnexus-lop5.md) | ADR-0007 |
| **4d** — máy A phỏng vấn, máy B tạo bead feature | DONE (code) | [kiến trúc](specs/2026-10-12-tram-dieu-phoi-kien-truc.md) §5.7 · D46, D47 · [plan](plans/2026-10-16-lat-4d-skill-phong-van-may-a.md) | ADR-0004 |
| **P1 + 3C-B** — vòng đời tiến trình có hạn, UID thực của principal, cổng lịch | DONE (code), còn lỗi Chặn đợt 7 | D45–D47 · [plan](plans/2026-10-16-lat-p1-vong-doi-tien-trinh.md) | ADR-0005 |
| **bs-78r.10** — đọc quota Codex rảnh chạy đúng principal của khe | DONE (code) | D45–D47 · [plan](plans/2026-10-16-bs-78r-10-quota-dung-principal.md) | ADR-0005 |
| **V1** — vá sau code: mã Đại ca không trùng mã điều phối, tải lại quyền, bố cục màn nhỏ | DONE (code) | [plan](plans/2026-10-16-lat-v1-va-sau-code.md) | — |

Quyết định D1–D53 nằm ở `docs/quyet-dinh/` (Tầng 3). Kiến trúc tổng đã duyệt:
[spec kiến trúc](specs/2026-10-12-tram-dieu-phoi-kien-truc.md).

## Phần 20% còn lại — PROPOSED
Thứ tự ưu tiên Đại ca chốt 17/10: vá + dọn → chạy thật (song song viết spec tự merge/deploy) → tự merge/deploy →
chọn model theo độ khó. Epic Beads: **`bs-2bd`**. Danh sách task chi tiết ở Beads, không chép vào đây.

| Feature | Trạng thái | Hợp đồng | Bead |
| --- | --- | --- | --- |
| **Vá kỹ thuật + dọn code thừa** trước chạy thật (timeout Claude API và Keychain, migration SQLite, siết quyền `~/.tram`, Host check memory 7710, lỗi Chặn đợt 7) | PROPOSED | [plan V2](plans/2026-10-17-lat-v2-va-sau-review-dot7.md) (đề xuất, chưa chạy RED/GREEN) | `bs-2bd.1` |
| **Chạy thật** theo cổng G0–G7 | PROPOSED | [sổ tay](handovers/2026-10-15-so-tay-chay-that.md) · [cổng sau đợt 7](handovers/2026-10-17-cong-sau-review-dot7.md) | `bs-2bd.2` (chi tiết: `bs-8eh`) |
| **Tự merge + tự deploy** (mục tiêu Đại ca chốt; đổi điểm dừng "Đại ca merge" và luật cấm merge) | PROPOSED | chưa có spec; cần change OpenSpec + plan | `bs-2bd.3`, `bs-2bd.4` |
| **Chọn model theo độ khó** (bead khó vào khe Opus, dễ vào khe Sonnet) | PROPOSED | chưa có spec | `bs-2bd.7` |
| **Agent tự cập nhật danh sách việc** (hiện agent thợ không được sửa) | PROPOSED | chưa có spec; cần change OpenSpec | `bs-2bd.5` |
| **Subagent cho vai coder và spec** (QC giữ tắt), sau khi spike S4 xác nhận lệnh cấm vẫn áp vào subagent | PROPOSED | chưa có spec | `bs-2bd.6` |

Ngoài phạm vi 20%: người dùng bên ngoài / khách hàng (tầm nhìn sau, `PROJECT.md`).

## Quy tắc nghiệp vụ đang có hiệu lực
Chưa có change OpenSpec nào được archive, nên **quy tắc nghiệp vụ của các feature trên nằm ở spec đã duyệt**
(cột Hợp đồng). Docs này không chép lại để tránh lệch hai nơi. Muốn biết một quy tắc:

| Muốn biết | Đọc |
| --- | --- |
| Ba cột, nhãn, luồng một feature từ ý tưởng tới merge | [spec kiến trúc](specs/2026-10-12-tram-dieu-phoi-kien-truc.md) §3, §5.7 |
| Chấm cột, hàng rào, thêm dự án | [spec 0+1a](specs/2026-10-12-phan-0-1a-cham-cot.md) |
| Phạm vi ký ức, quét bí mật, thăng cấp | [spec 1b](specs/2026-10-13-phan-1b-memory.md) |
| Màn hình, API đọc/ghi, bảo mật dashboard, Telegram | [spec 2](specs/2026-10-12-phan-2-dashboard.md) |
| Máy thợ, hạn mức, principal, cách ly | [spec 3](specs/2026-10-13-phan-3-may-tho-han-muc.md) |
| Bộ giao việc, QC, PR, luồng feature | [spec 4](specs/2026-10-13-phan-4-giao-viec.md) |

Bất biến tuyệt đối (bí mật, quyền, cổng kiểm lại, estop, khoá ghi, người làm khác người kiểm) thuộc
`docs/PRODUCT_ARCHITECTURE.md`; cơ chế giữ chúng thuộc [ARCHITECTURE.md](ARCHITECTURE.md).
Khi một change OpenSpec archive, hành vi chuyển sang `openspec/specs/<capability>/spec.md` và dòng tương ứng ở đây
chỉ còn trỏ tới đó.

## Tiêu chí nghiệm thu chung
Một feature "xong" khi đạt Definition of Done ở [AGENT_RULES.md](AGENT_RULES.md) §16, kiểm chứng theo loại thay đổi
ở §13, và: chạy được, đạt hết nghiệm thu của change, luồng chính có test, test xanh không hồi quy, QC đạt, docs bị
ảnh hưởng đã cập nhật. Phân biệt rõ trong báo cáo: **xong code (test offline)** khác **đã chạy thật (cổng hệ điều
hành)**; không tuyên bố "sẵn sàng chạy thật" khi chưa có bằng chứng trong sổ tay.

## Quy tắc cập nhật
- Lát mới code xong và test xanh: thêm một hàng `DONE (code)`; chỉ đổi thành chạy thật khi sổ tay có bằng chứng cổng.
- Phần 20%: hàng `PROPOSED` đổi thành `BUILDING` khi có change OpenSpec được duyệt và bắt đầu code, thành `DONE (code)`
  khi xong. Mã bead giữ ở cột Bead; chi tiết task chỉ ở Beads.
- Không liệt kê task, không ghi TODO ở đây. Việc phát sinh → `bd create`.
- Đường dẫn trong bảng phải tồn tại; đổi tên file spec/plan thì sửa cả hàng.
