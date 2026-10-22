# Kế hoạch tích hợp — 3c, 4d, bs-78r.10 sau chốt đợt 6

Nguồn quyết định: [D45–D47](../docs/quyet-dinh/2026-10-16-chot-sau-review-dot6.md). Phạm vi hiện tại là kế hoạch và bàn giao; chưa thực thi source/tests dự án.

> **Cập nhật 17/10/2026 (I1):** câu "chưa thực thi source/tests" ở trên là trạng thái lúc lập kế hoạch. Nay B0 → 4D-3 đã có mã trên `main` `59f8281` (2697 pytest, 101 node). Thêm D48–D53 ở cùng file quyết định. Xem mục "Trạng thái 17/10" cuối file. Không task nào được chạy thật.

## Thứ tự và phụ thuộc

| Task | Đầu ra / nghiệm thu | Phụ thuộc | Quy mô, xác minh |
|---|---|---|---|
| B0 | Đối chiếu HEAD, governance, phần đã ghép, môi trường test an toàn; finding ledger | Không | Nhỏ; status/diff + manifest, không reset thay đổi người khác |
| 3C-A | Boundary cưỡng chế và bảng control/OS proof; khả thi trong D45 | B0 | Vừa; review threat matrix, dừng nếu không khả thi |
| 4D-0 | API/storage/state machine và mọi cửa sổ crash | B0 | Vừa; source/spike cô lập và review contract |
| P1 | Deadline/ownership process chung | B0 | Chia runner + app-server adapter nếu lớn; regression lifecycle |
| 3C-B | UID và harness quản lý được | P1 | Vừa; fake spies + child tree bỏ được |
| 3C-C | Cây Git giữ đúng nguồn | B0 | Vừa; fixture CRLF/encoding/mode/symlink |
| Q1 | Principal xuyên suốt quota | P1 | Chia propagation/callers; identity/env tests |
| Q2 | Quota lỗi/timeout không hỏng heartbeat | Q1, P1 | Vừa; heartbeat/sentinel/cleanup tests |
| 3C-D | Thực hiện boundary | 3C-A, 3C-B, 3C-C | Phải chia S/M theo thiết kế trước code; regression threat matrix |
| 4D-1 | Dịch vụ tạo và recovery bền trên B | 4D-0 | Chia claim/create/reconcile; multi-process + storage tests |
| 4D-2 | API auth và đúng kho | 4D-1 | Vừa; ASGI/auth denial spies |
| 4D-3 | Client A và skill dùng mã ổn định | 4D-0; tích hợp sau 4D-2 | Chia nháp/client/skill; fake HTTP + contract tests |
| I1 | Spec/plan/runbook khớp code cuối, tích hợp và review | Các nhánh hoàn thành | Diff + focused/full suite phù hợp, ledger gates |
| LIVE | Các phép thử thật 3c/quota/4D-4 | I1 và gate liên quan, quyền Đại ca | CHƯA ĐƯỢC CHẠY |

Sau B0/thiết kế: checkpoint xác nhận không đổi quyết định. Sau P1/3C-B/Q2: checkpoint lifecycle/callers. Sau 4D-1/2: checkpoint crash/auth trước client. Sau I1: báo mức sẵn sàng từng nhánh, không gộp xanh chung. Không hai task cùng sửa primitive process/`noi_that.py`. Không mặc định phải dùng subagent.

## Mapping và bảo toàn sửa cũ

- dot6-C01 → 3C-A/3C-D + G4; dot6-C02 → P1/3C-B + G3/G4; R7 → 3C-C.
- dot6-Q02 = bs-78r.10 → Q1/Q2 + G5. Không nhầm Q02 đợt 5.
- dot6-Q04 → 4D-0..3 + G6; C1–C6 đã được xử lý bằng D46/D47, không hỏi lại.
- Giữ dot6-Q01 returncode/3 regression; giữ ý nghĩa Q03 schema/đa kết quả và Q06 lỗi không lộ argv/stderr khi chuyển qua B. Đổi tests cũ cho đúng flow, không giữ assertions buộc A gọi bd/hash nội dung.
- Journal/home đợt 5, D1–D44 không bị thay ngoài phần D46/D47 nêu rõ. V1 ngoài phạm vi; không mở lại/sửa chung V1 chỉ để tăng số test.

## Cách Claude triển khai

Bổ sung task chi tiết, Files và code/test đầy đủ theo quy ước repo trước giao worker; không giao từ một mô tả chung. Chi tiết kỹ thuật thông thường được tự giải quyết trong D45–D47. Gặp yêu cầu root/VM, credential mới, bỏ auth hoặc giảm cách ly thì dừng phần phụ thuộc và trình phương án, không ngừng nhánh độc lập.

TDD trên bản thử cô lập, kiểm fixture trước để tránh tác động host. Dùng lệnh repo sau khi xác minh môi trường; `UV_OFFLINE=1 uv run pytest -q` là lệnh lịch sử cần đối chiếu, không bảo đảm tự nó cô lập được cron/Keychain/mạng. Ghi baseline hiện tại, failures có sẵn và RED/GREEN thực tế. Không bỏ qua test chập chờn rồi ghi all-pass. Không invent số test mới.

## Rủi ro / điều chưa có bằng chứng

Cơ chế OS đóng C01 chưa được chứng minh; transaction Beads + receipt có thể không nguyên tử; auth route ghi từ A phải giữ đủ bảo vệ; source đích có thể khác snapshot. Đây là công việc thiết kế/xác minh, không phải câu hỏi Đại ca chưa chốt. Quyền chạy thật vẫn riêng theo runbook.

## Trạng thái 17/10/2026 (I1)

Đối chiếu `git log --merges 5da881e..59f8281` và bead con của `bs-863`. "Xong" = đã code, test offline đạt, đã ghép `main`. **Không** có nghĩa đã chạy thật.

| Task | Trạng thái | Merge / commit | Bead |
|---|---|---|---|
| B0 | Xong. Nền `5da881e`: 2242 pytest, 95 node | — | `bs-863.1` ✓ |
| 3C-A | Xong ở mức thiết kế: khả thi trong D45, có điều kiện G4 | `036183a` (phụ lục `docs/handovers/2026-10-16-thiet-ke-3c-boundary.md`) | `bs-863.2` ✓ |
| 4D-0 | Xong (thiết kế) | `a4455d3` | `bs-863.9` ✓ |
| P1 | Xong (T1–T5) | `0e33fbf` | `bs-863.4` ✓ |
| 3C-B | Xong (T6–T9) | `0e33fbf` | `bs-863.5` ✓ |
| 3C-C | Xong | `9ee1ed3` (`3df144b`) | `bs-863.3` ✓ |
| Q1 | Xong (Q1-a, Q1-b) | `0e33fbf` | `bs-863.6` ✓ |
| Q2 | Xong | `0e33fbf` | `bs-863.7` ✓ |
| 3C-D | Xong D1–D6 + S6 harness. **Còn 3C-D7** (bộ đọc launchd, chờ G3) | `9ee1ed3` (D1–D4), `59f8281` (H2/H6, D5a/b, D6a/b/c, S6) | `bs-863.8` ✓ |
| 4D-1 | Xong (1a, 1b) | `a02728b` | `bs-863.10` ✓ |
| 4D-2 | Xong | `a02728b` | `bs-863.11` ✓ |
| 4D-3 | Xong (3a, 3b, 3c) | `a02728b` | `bs-863.12` ✓ |
| I1 | **Đang làm** (nhánh `docs/i1-dot7`) | — | `bs-863.13` (đã đóng 16/10, xem dưới) |
| LIVE | **CHƯA CHẠY.** G3/G4 (3c Task 9), G5 (quota), G6 (4D-4) | — | `bs-8eh.4`, `bs-8eh.6`, `bs-urj.10` |

Ngoài bảng gốc nhưng đã ghép trong cùng đợt: V1 Task 1–3 (`9a0c0ff`, 2242 → 2243) và 1a-2 Task 4–6 (`2d0b5ba`, 2243 → 2269; Đại ca duyệt ghép trước 3c).

**Số test trên `main`** (pytest): 2242 → 2243 (V1) → 2269 (1a-2) → 2398 (4d) → 2566 (3c đợt 7) → 2650 (P1 + 3C-B + Q1/Q2) → **2697** (3c đợt 8). Node 95 → 101 (V1), sau đó không đổi.

**Bead tồn đọng (con của `bs-863`, P2):**

| Bead | Việc | Ghi chú |
|---|---|---|
| `bs-863.14` | Rủi ro P1: `kiem_am`/`kiem_cong`/`kiem_cach_ly` còn `subprocess.run` dưới `sudo` (cần tty cho mật khẩu) | Đang làm (17/10) |
| `bs-863.15` | Rủi ro P1: `mo_coi` dọn theo file pid, không kiểm thời điểm khởi động | |
| `bs-863.16` | Rủi ro P1: `theo_doi.py` còn `join()` không hạn | |
| `bs-863.17` | Rủi ro P1: `codex login status` của `tram tho kiem` chạy dưới tài khoản quản lý | |
| `bs-863.18` | H1 `stdin`: `chay_gioi_han` nhận `stdin=` để `ban_chep._chay` đi qua primitive | H1 còn mở; treo thì fail-closed |
| `bs-863.19` | Ctrl-C: `chay_han_tong` bắt `KeyboardInterrupt` để con harness không chạy tiếp | Kịch bản G3/G4 dặn dừng con theo PID |

**Cần người điều phối xem lại (không sửa trong I1):**
- `bs-863.13` (I1) đã đóng ngày 16/10 với lý do "4D-1a..3c ghép main" — có vẻ nhầm, vì I1 mới làm 17/10.
- `bs-urj.10` đã đóng, nhưng plan 4d nói chỉ đóng sau 4D-4 Step 2–5 (chưa chạy).
- `bs-urj.12`, `bs-urj.13`, `bs-urj.14` vẫn mở dù r47 T5/T6/T8 đã ghép.

**Thứ tự còn lại:** review Codex gói đợt 7–8 → G3 (Đại ca duyệt từng bước) → 3C-D7 → G4 (S6). G5 sau S2/S5. G6 sau Tailscale máy A và H5. `giao_viec.bat` giữ `false` suốt.


## Review độc lập đợt 7 — 17/10/2026

- [x] Review tĩnh snapshot; tạo REVIEW-CODEX.md và plan V2. Không chạy tests/OS/API, không sửa source.
- [ ] V2-0 identity process (.15), V2-1 interruption (.19), V2-6a stdin (.18): chưa G4/G5 theo phụ thuộc.
- [ ] V2-2 schema đối soát: trước G6.
- [ ] V2-3 inventory mọi dự án, V2-4 probe evidence, V2-5 profile attestation: trước G4.
- [ ] V2-6b .14/.17 trước G5; V2-6c .16 trước G7.
- [ ] V2-7 cleanup tests/error body; guard host/mạng phải kiểm trước chạy test.
- [ ] V2-8 nghiệm thu gate theo `docs/handovers/2026-10-17-cong-sau-review-dot7.md`.

Các tick/count cũ là lịch sử tác giả, không phải reviewer đo lại. Không tự đóng/mở Beads; người điều phối đối soát bs-863.13 và bs-urj.10 cùng backlog. V2 có task thiết kế còn mở, chưa đủ giao code toàn lát.
