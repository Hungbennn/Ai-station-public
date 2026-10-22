# PRODUCT_ARCHITECTURE — từ vựng, thực thể, sở hữu dữ liệu, bất biến

Project: `ben-station`
Status: `ACTIVE`
Cập nhật: `2026-10-20`

## Mục đích và sở hữu
Sở hữu: từ vựng miền, thực thể lõi, ma trận nguồn sự thật, phân loại dữ liệu, **bất biến nghiệp vụ (INV-xxx)**.
Không sở hữu: sản phẩm và non-goals (`PROJECT.md`), cơ chế kỹ thuật giữ bất biến, tầng, luồng dữ liệu, tích hợp
ngoài (`ARCHITECTURE.md`), lý do của từng lựa chọn lớn (`decisions/ADR-*.md`), luật vận hành agent (`AGENT_RULES.md`).

> Dựng ngày 2026-10-17 từ spec đã duyệt, quyết định D1–D53, code `main` `d2a74a9` và câu trả lời của Đại ca
> cùng ngày. Chỗ chỉ suy từ code có dấu `(suy từ code, chưa xác nhận)`.

## Sứ mệnh sản phẩm
Trạm điều phối riêng của Đại ca: thay Đại ca xếp việc, giao việc cho agent AI, kiểm chéo, mở PR và dừng ở điểm
cần duyệt — để Đại ca không phải canh agent và hạn mức các tài khoản AI được dùng hết. Chi tiết: `PROJECT.md`.

## Bối cảnh hệ thống
```
Đại ca ── máy A (Mac làm việc) ──Tailscale──► máy B (Mac mini 24/7): trạm chủ + thợ
              │ phiếu yêu cầu, xem/duyệt dashboard        │ Beads dự án con · GitHub · Claude API · Telegram
              │ merge PR trên GitHub                       │ agent thợ (Claude Code, Codex) chạy dưới principal riêng
```
Bố trí máy A/B và hai khe đầu tiên: [spec kiến trúc §4.1](specs/2026-10-12-tram-dieu-phoi-kien-truc.md).

## Ranh giới hệ thống

### Ứng dụng sở hữu
- Gói `tram` (trạm chủ, tram-api, quản lý thợ, memory, báo tin) và dashboard `frontend/`.
- Dữ liệu dưới `~/.tram` của máy B: nhật ký sự kiện, kho vận hành, ký ức, cấu hình trạm, dấu estop và dấu cổng.
- Prompt và quyền theo vai (`vai/`), cấu hình dự án (`du-an/`), skill và hook máy A (`ky-nang/`, `may-a/`).

### Ứng dụng không sở hữu
- **Nội dung việc** của dự án con: nằm ở Beads của dự án đó; trạm chỉ đọc và ghi theo luật ([ADR-0001](decisions/ADR-0001-beads-nguon-viec-tram-ghi.md)).
- **Mã nguồn** dự án con và nhánh chính trên GitHub: Đại ca merge ([ADR-0007](decisions/ADR-0007-tram-giu-quyen-day.md)).
- Tài khoản Claude/Codex của từng khe, đăng nhập Tailscale, tài khoản macOS — Đại ca tạo và giữ.
- App Claude trên máy A: nơi Đại ca thảo luận; trạm không thay nó (non-goal, `PROJECT.md`).

### Hệ thống ngoài
Beads (`bd`), Git/GitHub (`gh`), CLI `claude`/`codex`, Anthropic API, Ollama (bge-m3), Telegram, Tailscale,
`ccusage`, Keychain (`security`), launchd/sudo/Seatbelt. Timeout và "hỏng thì sao": `ARCHITECTURE.md` mục Tích hợp ngoài.

## Từ vựng miền
| Thuật ngữ | Nghĩa | Không nhầm với |
| --- | --- | --- |
| **Đại ca** | Chủ trạm, người dùng duy nhất; danh tính là login Tailscale trong `dai_ca_logins` | agent điều phối trên máy A |
| **Máy A / máy B** | A: Mac làm việc của Đại ca. B: Mac mini 24/7, trạm chủ kiêm thợ | "máy" trong bảng `may_tho` (máy thợ đã ghép) |
| **Trạm (trạm chủ)** | Phần mềm trên máy B dưới tài khoản trạm: tram-api, quét, giao việc, memory | thợ |
| **Dự án** | Một repo được trạm điều phối, khai ở `du-an/<ten>.yaml` | repo trạm (ben-station) |
| **Bead** | Một việc trong Beads của dự án con (bug, task, chore, spike, feature, decision, epic) | bead `bs-…` của repo trạm |
| **Cột** | Ba cột: 1 `cot:ai-lam` (AI tự làm) · 2 `cot:can-chot` (cần Đại ca chốt) · 3 `cot:cho-review` (chờ Đại ca review). Mỗi bead tối đa một nhãn `cot:*` | trạng thái `status` của Beads |
| **Nhãn luồng** | `can-spec`, `cho-duyet-spec`, `theo-plan` của bead feature; dashboard suy cột từ đây | nhãn cột |
| **`cot-khoa`** | Đại ca tự gán cột, bộ chấm không lật lại | khoá ghi dự án |
| **Hàng rào** | Bốn loại nhạy cảm: tiền/giá · schema/migration · quyền/bảo mật · thứ khách thấy. Chạm mà chưa chốt → cột 2 | `duong_dan_cam` |
| **`co-do`** | Cờ đỏ: diff thật chạm vùng nhạy cảm, gắn ở tầng kiểm | hàng rào tầng chốt |
| **Decision / escalation** | Bead `decision` chặn bead khác; escalation là decision trạm tạo khi agent bí hay hệ gặp lỗi (`tram:escalation`) | ADR, quyết định D |
| **Điểm dừng** | Bốn chỗ trạm chờ Đại ca: sau spec/plan · trước merge · agent bí · trước thao tác nguy hiểm (Q6) | estop |
| **Khe** | (máy, CLI, tài khoản), vd `B/claude-1`; một thư mục cấu hình CLI, một hạn mức | máy, vai |
| **Vai** | Việc một khe làm: `coder`, `qc`, `spec` (+ vai nội bộ chấm cột, memory). Prompt `vai/*.md`, quyền `vai/quyen/*.json` | khe |
| **Vai ưu tiên** | Vai khe nhận trước; không cố định, khe cạn thì khe khác nhận (Q14) | vai cố định |
| **Principal** | Tài khoản macOS chạy một nhóm tiến trình: **trạm** giữ bí mật/kho; **quản lý thợ** giữ token máy; **khe** không giữ credential trạm/GitHub/khe khác, riêng Claude B có phiên riêng (ADR-0009); **`tram-kiem`** kiểm lại | user đăng nhập của Đại ca |
| **Phiếu (phiếu giao)** | Một bước việc (`code`, `qc`, `spec`) trạm giao cho một khe; mã `giao_id` | **phiếu yêu cầu** |
| **Phiếu hiệu lực** | Phiếu đã cấp, chưa kết thúc được chấp nhận, chưa thu hồi. Một định nghĩa duy nhất (`tram/phieu/`) | phiếu đã có bàn giao |
| **Lượt (`luot`)** | Bộ đếm theo bead, tăng mỗi lần phát phiếu; báo cáo mang lượt cũ bị từ chối (thẻ chắn) | **lần (`lan`)**: lần chạy CLI trong một phiếu, tối đa 3 |
| **`ma_giao`** | Credential 128 bit của một phiếu, CLI dùng gọi memory | `giao_id` (đoán được, không phải bằng chứng) |
| **Token máy / mã ghép** | Token máy: credential của máy thợ gọi `/api/tho/*`. Mã ghép: mã một lần, 10 phút, đổi lấy token máy | mã Đại ca, mã điều phối |
| **Mã Đại ca / mã điều phối** | Hai mã riêng trên máy A: mã Đại ca đọc memory; mã điều phối chỉ gửi nhịp hook (D24) | token máy |
| **Hạn mức / cầu dao** | Hạn mức: lượt dùng còn lại của tài khoản một khe. Cầu dao: ngắt khe khi gặp 429/hết hạn mức | **ngân sách**: trần lần chạy, phút, token của một phiếu/bead |
| **Bàn giao** | File agent viết khi xong (`chinh-thuc`) hoặc theo mốc (`tam`), có khối máy đọc được | bàn giao phiên của repo trạm (`docs/handovers/`) |
| **Kiểm lại** | Trạm tự chạy lại lệnh kiểm của phiếu tại SHA đã công bố, dưới `tram-kiem` trong Seatbelt | lệnh kiểm do thợ chạy, QC |
| **Cổng kiểm** | Trạng thái cho phép lượt kiểm lại kế tiếp chạy; đóng khi bất thường, Đại ca mở (D49) | cổng chạy thật G0–G7 của sổ tay |
| **QC** | Bước một khe **khác** kiểm mã của khe đã code; chỉ ghi bàn giao, không sửa mã | kiểm lại |
| **Công bố / ref tạm** | Trạm xác minh commit của lượt rồi cập nhật nhánh `tram/<bead>`; thợ chỉ đẩy ref tạm theo lượt | merge |
| **Phiếu yêu cầu** | Yêu cầu feature Đại ca chốt trên máy A, mang **mã yêu cầu** cố định (D47); B tạo bead feature (D46) | phiếu giao |
| **Sự kiện** | Một dòng ghi thêm trong nhật ký `su_kien`; trạng thái hiển thị tính từ sự kiện + Beads | thao tác |
| **Thao tác (`ma_thao_tac`)** | Một lần ghi từ dashboard mang ID để gửi lại không tạo trùng | sự kiện |
| **Estop** | Công tắc dừng khẩn cấp toàn trạm | tắt một khe |
| **`bat_ghi`** | Khoá ghi của dự án: `false` = chỉ đọc và quét thử ("chỉ quét thử" trên dashboard) | `giao_viec.bat` (công tắc giao việc toàn trạm) |
| **Ký ức / phạm vi / vùng cấp** | Ký ức: một bài học trong memory. Phạm vi: `/du-an/<ten>/nghiep-vu`, `/du-an/<ten>/cach-lam`, `/vai/<vai>`, `/chung`. Vùng cấp: tập phạm vi trạm cấp cho một phiếu | memory riêng của một CLI |
| **Thăng cấp** | Ký ức cách-làm lặp ở ≥ 2 dự án được nâng lên `/chung` hay `/vai`, chờ 7 ngày mới có hiệu lực | gộp ký ức |
| **Kênh ghi** | Đường mà API ghi của dashboard nhận yêu cầu: `header` (tạm) hoặc `unix-socket` | kênh báo tin Telegram |

## Thực thể lõi
- **Dự án** → có nhiều **bead** (ở Beads dự án con) và một khoá `bat_ghi`.
- **Bead** → nhận nhãn **cột**; có thể bị **decision/escalation** chặn; có nhiều **phiếu** qua các **lượt**.
- **Máy** → có nhiều **khe**; mỗi khe một **principal thực thi**, một **hạn mức**, một **vai ưu tiên**.
- **Phiếu** → gắn một bead, một khe, một lượt, một bước; có **ngân sách**, `ma_giao`, tối đa 3 **lần** chạy CLI;
  kết thúc bằng **bàn giao**, rồi **kiểm lại**, **QC**, **công bố**, **PR**.
- **Phiếu yêu cầu** → sinh đúng một bead feature theo **mã yêu cầu**.
- **Sự kiện** → ghi lại mọi việc trên; **ký ức** được tách từ một số sự kiện nguồn.

Lược đồ bảng không chép ở đây. Nguồn: `tram/su_kien/ket_noi.py`, `tram/phieu/luoc_do.py`, `tram/thao_tac/kho.py`,
`tram/yeu_cau/so_nhan.py`, `tram/nho/bang.py`; mô hình bead `tram/beads/mo_hinh.py`.

## Ma trận nguồn sự thật
| Dữ liệu | Nguồn sự thật | Ai được ghi | Ai được đọc |
| --- | --- | --- | --- |
| Việc, nhãn cột của dự án con | Beads của dự án đó | trạm (`--actor tram/*`, chỉ khi `bat_ghi: true`); Đại ca (dashboard, phiên tay) | trạm; agent chỉ qua gói ngữ cảnh |
| Việc của repo trạm (`bs-…`) | `.beads/` repo này | agent điều phối, Đại ca — `BEADS.md` | mọi agent của repo trạm |
| Nhật ký sự kiện | `~/.tram/su-kien.db`, bảng `su_kien` | chỉ tiến trình tài khoản trạm; thợ gửi qua tram-api | dashboard, báo tin, memory, bảng điểm |
| Phiếu, lượt, khe, máy thợ, ngân sách | `~/.tram/su-kien.db`, kho vận hành | tram-api (phần 3), trong một giao dịch | trạm |
| Thao tác ghi dashboard, sổ yêu cầu feature | `~/.tram/su-kien.db` | tram-api | tram-api |
| Ký ức | LanceDB `~/.tram/nho/lancedb` | chỉ tiến trình `tram nho chay`; agent qua MCP vào `/du-an/X` của phiếu; Đại ca ghi tay | thợ theo vùng cấp; máy A chỉ đọc (#20) |
| Cấu hình trạm | `~/.tram/cau-hinh.yaml` | Đại ca (tay) | trạm |
| Cấu hình dự án, `bat_ghi` | `du-an/<ten>.yaml` | Đại ca (tay); `tram du-an them` chỉ sinh nháp `bat_ghi: false` | trạm |
| Cấu hình máy thợ | `~/.tram/tho.yaml` của tài khoản quản lý thợ | `tram tho dang-ky`, Đại ca | tiến trình quản lý thợ |
| Bí mật | Keychain của tài khoản sở hữu | Đại ca (Terminal.app), lệnh cài qua stdin | chỉ tiến trình của tài khoản đó; **không bao giờ** agent |
| Mã dự án con | Git; nhánh chính trên GitHub | agent commit trong worktree; trạm công bố `tram/*`; Đại ca merge | trạm, thợ, Đại ca |
| Bàn giao của agent | file trong nhánh `tram/<bead>`; trạm chép vào notes bead | agent viết; trạm chép | trạm, QC, memory (sau QC đạt, D8) |
| Prompt, quyền vai | `vai/` repo trạm | qua plan đã duyệt | trạm khi dựng phiếu |
| Estop | file `~/.tram/estop` | Đại ca (CLI, dashboard) | mọi vòng của trạm và thợ |
| Dấu cổng kiểm | `~/.tram/kiem-lai.dong`, trạng thái cổng lượt | trạm đóng; **chỉ Đại ca** mở (D49) | kiểm lại |

## Phân loại dữ liệu
| Loại | Ví dụ | Luật |
| --- | --- | --- |
| **Bí mật** | khoá Anthropic, token Telegram, token nội bộ, token memory, token máy, mã Đại ca, mã điều phối | Chỉ Keychain; trạm giữ băm khi cần so. Tên mục Keychain: `CURRENT_STATE.md`. Xem INV-001 |
| **Credential theo phiếu** | `ma_giao` | Chỉ trong bảng `phieu` và môi trường CLI của phiếu; che trong log, lỗi, dashboard |
| **Nội dung nghiệp vụ dự án con** | mô tả bead, mã, bàn giao, ký ức `nghiep-vu`, log CLI (có thể chứa `.env`) | Không ra Telegram; ký ức không rời phạm vi dự án; log CLI ở lại máy thợ, giữ 30 ngày (spec 3 §7.3) |
| **Dữ liệu cá nhân** | login Tailscale trong `dai_ca_logins`, tên khách trong `tu_khoa_khach` | Tên gợi nhớ của khe cấm `@` để không thành email (`tram/api/tho.py`); ký ức có tên khách ép về `nghiep-vu` |
| **Dữ liệu vận hành** | sự kiện, phiếu, hạn mức, usage | Chỉ ghi thêm (sự kiện); có lịch sao lưu `vn.tram.sao-luu` (`tram/chu/launchd.py`). Chưa có luật hết hạn hay xoá (suy từ code, chưa xác nhận) |
| **Xem tự do trong tailnet** | dashboard đọc | Không cần đăng nhập — cố ý ([ADR-0004](decisions/ADR-0004-danh-tinh-tailscale-kenh-ghi.md)); không mở ra Internet |

## Bất biến nghiệp vụ
Sáu bất biến tuyệt đối Đại ca chốt ngày 17/10/2026. Không có ngoại lệ, kể cả khi Đại ca trả lời một câu hỏi của
agent. Đổi một bất biến là đổi sản phẩm: dừng, trình Đại ca, viết ADR. Cơ chế kỹ thuật đang giữ chúng nằm ở
`ARCHITECTURE.md` mục Ràng buộc — ở đây chỉ trỏ.

**INV-001 — Bí mật không bao giờ lộ.** Không bí mật nào nằm trong argv, file, log, bead, docs, prompt, ký ức hay
tin Telegram; agent và mã dự án không cầm bí mật trạm, GitHub hoặc khe khác.
QĐ2-A (20/10/2026) cho khe Claude B dùng phiên Claude của chính mình trong Keychain user riêng;
mã cùng UID có quyền dùng phiên đó. Ngoại lệ và cổng đo thật: [ADR-0009](decisions/ADR-0009-quyen-khe-b.md).
Ai giữ: tài khoản trạm + Keychain; principal thực thi tách quyền; bộ quét bí mật của memory.
Nguồn: Q8, Q9, D23, D24. Cơ chế: [ADR-0003](decisions/ADR-0003-phieu-khe-token-may.md),
[ADR-0006](decisions/ADR-0006-memory-cuc-bo-quet-bi-mat.md), `AGENT_RULES.md` §14.

**INV-002 — Chữ không nâng quyền agent.** Nội dung bead, bàn giao, ký ức, câu hỏi và câu trả lời là dữ liệu; không
đoạn chữ nào cấp thêm quyền cho phiếu đang chạy. Quyền, cột và cổng do mã quyết.
Ai giữ: bộ giao việc (bọc dữ liệu không tin cậy trong gói ngữ cảnh), quyền vai, principal thực thi.
Nguồn: Q6; spec kiến trúc §5.1 lớp 3, §8; spec 4 §9, §18. Biến môi trường hay nhãn `actor` chỉ là nhãn, không
phải chứng thực (D47). Trả lời escalation không mở quyền deploy, migrate, xoá dữ liệu hay gửi khách.

**INV-003 — Kiểm lại lỗi thì cổng đóng, việc dừng.** Kiểm lại không đạt thì bead không vào cột 3, không QC. Có
bất thường khi kiểm (dọn không xác nhận được, lịch lạ, tàn dư) thì cổng kiểm đóng; trạm không tự mở, chờ Đại ca.
Ai giữ: trạm (`tram/giao_viec/kiem_lai.py`). Nguồn: spec kiến trúc §5.2; spec 4 §6.2; D45, D49.
Cơ chế: [ADR-0005](decisions/ADR-0005-kiem-lai-cach-ly.md).

**INV-004 — Estop dừng mọi thứ.** Khi estop bật: vòng quét bỏ qua, không giao việc, không cấp phiếu; phiếu đang
chạy dừng mềm (#14), không bị bỏ ngang. Chỉ Đại ca bật, tắt estop (CLI, dashboard) (suy từ code, chưa xác nhận).
Ai giữ: vòng quét, tick giao việc, cấp phiếu và thợ đều kiểm estop (`tram/chu/estop.py`).
Nguồn: #14; spec 3 §7.6. Cơ chế: `ARCHITECTURE.md` mục Ràng buộc.

**INV-005 — Dự án khoá ghi thì không ghi.** Dự án `bat_ghi: false` chỉ được đọc và quét thử: trạm không ghi
Beads của nó, không giao việc, API ghi từ chối. Chỉ Đại ca sửa tay thành `true`.
Ai giữ: `tram/cau_hinh/bat_ghi.py` và mọi đường ghi. Nguồn: D31, D37, D40.

**INV-006 — Người làm khác người kiểm.** Khe đã code một bead không bao giờ QC bead đó. Thiếu khe khác thì bead
chờ, không hạ chuẩn. Kiểm lại do trạm chạy, không do khe đã code.
Ai giữ: chọn khe (`tram/giao_viec/chon.py`). Nguồn: Q14, #17; spec 4 §5.3. Hai khe cùng model Claude vẫn hợp lệ (#17).

### Luật thiết kế, không tuyệt đối
- **Mỗi việc một agent một lúc:** một bead có tối đa một phiếu hiệu lực; không chạy song song nhiều bước của một
  bead (kho phiếu `tram/phieu/luoc_do.py`; spec 4 §5.1 điều 5, §17) (suy từ code, chưa xác nhận). Đại ca giữ như
  thiết kế nhưng không coi là bất biến.

### Mục tiêu đã chốt, chưa hiệu lực
- **Agent tự cập nhật việc.** Hiện agent thợ không ghi Beads của dự án con: vai `coder` cấm `bd`, chỉ báo qua
  `tram bao`, trạm ghi thay (Q11; [ADR-0001](decisions/ADR-0001-beads-nguon-viec-tram-ghi.md)). Đại ca muốn đổi
  cho agent tự cập nhật việc. Cần spec riêng; tới khi spec được duyệt, luật hiện hành giữ nguyên.
- **Tự merge, tự deploy.** Hiện chỉ Đại ca merge. Mục tiêu và điều kiện: [ADR-0007](decisions/ADR-0007-tram-giu-quyen-day.md), `PROJECT.md`.

## Hành trình xuyên hệ thống
Luồng chi tiết: `PROJECT.md` (luồng một feature), `ARCHITECTURE.md` (luồng dữ liệu). Ở đây chỉ ghi **ai ghi gì**:

| Bước | Ai ghi | Ghi vào |
| --- | --- | --- |
| Đại ca chốt phiếu yêu cầu trên A | skill máy A gửi, B tạo | sổ yêu cầu SQLite → bead feature (Beads) |
| Chấm cột | bộ chấm 1a | nhãn `cot:*` (Beads) + sự kiện |
| Cấp phiếu | tram-api | kho phiếu (lượt, ngân sách) + `bd update --claim` |
| Agent làm | agent trong worktree; B do quản lý chốt commit sau thu hồi | bản sửa + bàn giao; `tram bao` → hàng đợi → sự kiện (ADR-0009) |
| Công bố, kiểm lại, QC | trạm; khe QC khác khe code | nhánh `tram/<bead>`; sự kiện `kiem.lai`, `qc.ket_qua` |
| Vào cột 3, mở PR | trạm | `cot:cho-review` + notes (Beads); PR GitHub |
| Merge | **Đại ca** | nhánh chính GitHub; trạm xác minh rồi đóng bead |
| Nạp ký ức | memory service | LanceDB, sau QC đạt (D8) |

## Sổ quyết định kiến trúc
| ADR | Chốt |
| --- | --- |
| [ADR-0001](decisions/ADR-0001-beads-nguon-viec-tram-ghi.md) | Beads là nguồn việc; trạm là bên ghi |
| [ADR-0002](decisions/ADR-0002-sqlite-nhat-ky-su-kien.md) | Nhật ký sự kiện SQLite, trạng thái tính lúc đọc |
| [ADR-0003](decisions/ADR-0003-phieu-khe-token-may.md) | Phiếu theo lượt, khe, token máy |
| [ADR-0004](decisions/ADR-0004-danh-tinh-tailscale-kenh-ghi.md) | Danh tính Tailscale, xem tự do, kênh ghi |
| [ADR-0005](decisions/ADR-0005-kiem-lai-cach-ly.md) | Kiểm lại trong vùng cách ly |
| [ADR-0006](decisions/ADR-0006-memory-cuc-bo-quet-bi-mat.md) | Memory cục bộ, một nơi ghi, quét bí mật |
| [ADR-0007](decisions/ADR-0007-tram-giu-quyen-day.md) | Trạm giữ quyền đẩy; Đại ca merge |
| [ADR-0008](decisions/ADR-0008-dashboard-spa-csp.md) | Dashboard SPA dưới CSP chặt |
| [ADR-0009](decisions/ADR-0009-quyen-khe-b.md) | Khe B giữ đăng nhập Claude riêng, quản lý giữ quyền Git |

Quyết định chi tiết hơn: D1–D53 trong `docs/quyet-dinh/`.

## Câu hỏi kiến trúc còn treo
- Cơ chế cách ly khe: chỉ thử `user` (D53); nhánh `sandbox` giữ mã, cổng đóng — chốt sau cổng S6/G4.
- Công bố lai (D4) chỉ chính thức khi S7 đạt.
- Q11 định Beads mọi dự án con chạy Dolt server trên máy B; chưa dựng, chờ spike beads từ xa (#1).
- Dự án có file cấu hình nhưng thiếu khoá `bat_ghi` hiện được coi là `true` (`tram/cau_hinh/bat_ghi.py`).
  Đại ca chốt 17/10: đổi sang `false` cho khớp INV-005 — bead `bs-2bd.1.22`.
