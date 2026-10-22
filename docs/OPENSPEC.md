# Đặc tả thay đổi bằng OpenSpec

Project: `ben-station`
Status: `ACTIVE`
Cập nhật: `2026-10-17`

## Mục đích và sở hữu
Sở hữu **cách đặc tả một thay đổi hành vi** trong repo này, và cách OpenSpec nối với plan TDD và Beads.
Không sở hữu: trình tự plan → review → code → QC (`DEVELOPMENT_PLAYBOOK.md`), quy ước việc (`BEADS.md`).

**Đại ca chốt 17/10/2026:** giữ quy trình hiện tại (spec → plan TDD → review Codex → code đúng plan → QC) và
**bổ sung** OpenSpec. OpenSpec giữ **hành vi** (đề xuất, spec hành vi, nghiệm thu, archive); `docs/plans/` giữ
**cách làm** (dạng plan theo QĐ2-A tại `DEVELOPMENT_PLAYBOOK.md` §1; lớn/cũ có mã nguyên văn).

## Bốn chỗ, bốn câu hỏi
| Chỗ | Trả lời | Ví dụ |
| --- | --- | --- |
| Beads (`bd`) | **Còn việc gì**, việc nào chặn việc nào | `bs-2bd` |
| `openspec/changes/<tên>/` | Thay đổi này **phải làm hệ thống cư xử ra sao**, nghiệm thu là gì | proposal, `specs/`, `tasks.md` |
| `docs/plans/<ngày>-<tên>.md` | **Làm thế nào**: dạng theo cỡ ở PLAYBOOK §1; lớn/cũ có mã nguyên văn | khung ở `DEVELOPMENT_PLAYBOOK.md` |
| `docs/` còn lại | Hệ thống **là gì**, luật gì, đã quyết gì | ADR, ARCHITECTURE |

## Ba bên nối nhau thế nào
```
bead bs-xxx ──▶ change openspec/changes/<tên>/ ──▶ plan docs/plans/<ngày>-<tên>.md ──▶ code ──▶ archive ──▶ bd close
 (việc)          (hành vi + nghiệm thu)              (cách làm, mã nguyên văn)
```
1. **Bead trước.** Việc có bead. Proposal ghi mã bead và nguồn ý Đại ca (`openspec/config.yaml` bắt buộc).
2. **Change sau cổng thảo luận** (`AGENT_RULES.md` §11). Proposal + spec hành vi (`### Requirement:` /
   `#### Scenario:`) + `design.md` khi chạm nhiều package, dữ liệu, bảo mật hay tích hợp ngoài. Pha này không chạm code.
3. **`tasks.md` = mốc nghiệm thu**, không chép mã. Mỗi mốc nói cách kiểm chứng và trỏ Task tương ứng của plan.
4. **Nối nghiệm thu:** nhỏ đối chiếu yêu cầu/Scenario với test; vừa/lớn có plan dẫn change và Scenario tương ứng.
   Dạng plan/review/QC theo QĐ2-A tại `DEVELOPMENT_PLAYBOOK.md` §1–4; không bỏ nghiệm thu OpenSpec.
5. **Review Codex** nhận cả change lẫn plan trong cùng gói. Sửa hành vi thì sửa change; sửa cách làm thì sửa plan.
6. **Code đúng plan, QC, ghép** theo `DEVELOPMENT_PLAYBOOK.md`; tick `tasks.md` khi mốc có bằng chứng.
7. **Archive** khi mọi Scenario có bằng chứng. Scenario chỉ chứng minh được trên máy thật thì chờ cổng trong sổ tay
   chạy thật; chưa đạt thì change ở lại `changes/`.
8. **`bd close`** sau archive. Việc phát sinh giữa chừng: `bd create`, không thêm vào `tasks.md` của change khác.

Lệch giữa change và plan: change thắng về hành vi, plan thắng về cách làm. Phát hiện yêu cầu mơ hồ giữa chừng
thì **dừng, sửa change**, cho Đại ca duyệt lại, rồi mới sửa plan.

**Không cần change** khi không đổi hành vi quan sát được: sửa bug có test tái hiện, văn bản, dọn code thừa,
refactor trong phạm vi (suy từ `AGENT_RULES.md` §2 "Luôn BUILD ngay", chưa xác nhận). Khi đó bead + plan nhỏ là đủ.

## Spec cũ trong `docs/specs/`
Sáu spec đã duyệt và D1–D53 là nguồn gốc (Tầng 3), không chuyển sang OpenSpec một lượt. Change đầu tiên chạm vùng
nào thì spec hành vi của vùng đó chuyển vào `openspec/specs/` lúc archive và từ đó thắng (`docs/AGENTS.md`
thứ bậc mục 7). Change nói khác spec cũ hay D đã chốt: báo Đại ca, không tự chọn.

## Vòng đời và lệnh
Không cài global. Gọi đúng bản đã pin, tắt telemetry bằng biến môi trường:
```bash
DO_NOT_TRACK=1 npx -y @fission-ai/openspec@1.14.0 <lệnh>
```
| Bước | Lệnh |
| --- | --- |
| Tạo khung change | `openspec new change <ten-kebab-case>` |
| Xem còn thiếu artifact nào | `openspec status --change <tên>` |
| Hướng dẫn viết từng artifact (đã gồm context và rules) | `openspec instructions <proposal\|specs\|design\|tasks> --change <tên>` |
| Kiểm định dạng — xanh trước khi viết plan | `openspec validate <tên> --strict` |
| Xem change, spec đang có | `openspec list`, `openspec list --specs`, `openspec show <tên>` |
| Nhập spec vào `openspec/specs/` | `openspec archive <tên> --yes` |

Bốn dấu `#` cho Scenario; ba dấu là hỏng âm thầm. `validate` từ chối change không có delta spec nào.

## Ngôn ngữ
`openspec/config.yaml` đặt artifact viết tiếng Việt; heading cấu trúc (`## ADDED Requirements`, `### Requirement:`,
`#### Scenario:`) và SHALL/MUST giữ tiếng Anh. File đó còn có `context` (tóm tắt dự án) và `rules` cho proposal,
design, tasks — OpenSpec chèn chúng vào hướng dẫn mỗi lần viết artifact.

## Cài đặt (17/10/2026)
- **Bản pin `@fission-ai/openspec@1.14.0`** (phát hành 30/09/2026). Bản mới nhất 1.14.3 ra đúng 17/10 nên chưa dùng.
  Cần Node ≥ 20.19. Nâng bản: hỏi Đại ca (thêm/đổi phụ thuộc, `AGENT_RULES.md` §11), đổi số ở đây và trong `config.yaml`.
- Đã áp vào repo **chỉ** cây `openspec/`: `config.yaml`, `specs/`, `changes/archive/` (rỗng). Sinh bằng
  `openspec init --tools none --language vi` trong thư mục tạm, rồi thêm `context` và `rules`.
- **Chưa cài** skill và lệnh của OpenSpec cho Claude Code và Codex. Nếu chọn `--tools claude,codex`, init ghi
  6 lệnh `.claude/commands/opsx/*.md`, 6 skill `.claude/skills/openspec-*/` và 6 skill `.agents/skills/openspec-*/`.
  Không chèn gì vào `CLAUDE.md` hay `AGENTS.md`. Đại ca chốt 17/10: **chưa cài**, xem lại khi viết change đầu tiên
  (`bs-2bd.3`). Lý do: skill tự kích hoạt được; `opsx:apply` code thẳng từ `tasks.md`, đi tắt qua plan TDD, review
  Codex và QC; các lệnh gọi `openspec` trên PATH, mà dự án chỉ dùng bản pin qua `npx`.
- Telemetry bật mặc định; `DO_NOT_TRACK=1` hoặc `OPENSPEC_TELEMETRY=0` tắt nó (đọc từ mã nguồn bản 1.14.0).
- Bản 1.14.0 **không có lệnh `openspec verify`** (chỉ là workflow tuỳ chọn); đối chiếu code với spec bằng test của plan.

## Ranh giới với `docs/`
OpenSpec giữ hành vi. Vẫn ở `docs/`: quyết định sống lâu hơn một change (`docs/decisions/`), từ vựng và bất biến
(`PRODUCT_ARCHITECTURE.md`), bản đồ (`ARCHITECTURE.md`), chuẩn cài đặt (`ENGINEERING_STANDARDS.md`), giao diện
(`DESIGN_SYSTEM.md`), bảng feature đã build (`FEATURE_SPEC.md`, teo dần theo mỗi lần archive).

## Change đang mở
- `openspec/changes/tu-merge-deploy/` — nguồn duy nhất cho `tu-merge`/`tu-deploy`, QĐ1–QĐ4 đã chốt 20/10;
  plan `docs/plans/2026-10-20-tu-merge-deploy.md`.
- `openspec/changes/tu-merge-tu-deploy/` — sau hợp nhất chỉ còn `dieu-khien-tu-dong`;
  hai spec merge/deploy 18/10 được giữ ngoài cây delta để đối chiếu, không archive lần hai.
