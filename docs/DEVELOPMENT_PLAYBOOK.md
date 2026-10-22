# Sổ tay thực thi

Project: `ben-station`
Status: `ACTIVE`
Cập nhật: `2026-10-17`

## Mục đích và sở hữu
Sở hữu **chi tiết từng bước** đưa một việc từ spec tới `main`: plan TDD, review Codex, giao subagent, QC, ghép,
đóng bead; bản đồ tác động; cổng khảo sát. Vòng 10 bước và luật quyết định (blast radius, quyền tự quyết, DoD)
ở `AGENT_RULES.md` §2, §3, §11, §16 — sổ tay này không lặp lại, chỉ nói **làm từng bước thế nào**.
Không sở hữu: hành vi của change (`OPENSPEC.md`), chạy thật (`DEPLOY.md` + sổ tay cổng), chuẩn code (`ENGINEERING_STANDARDS.md`).

## 1. Spec hành vi → quy trình theo cỡ (QĐ2-A, 20/10/2026)
Phiếu có `co` dùng bảng dưới; phiếu cũ/không cấu hình giữ quy trình plan nguyên văn cũ.
Mọi nhánh giữ duyệt spec, cổng nguy hiểm, ngân sách, kiểm lại cách ly và kiểm cả bộ sau ghép.

| Cỡ | Trước code | Kiểm và QC |
| --- | --- | --- |
| Nhỏ | Đủ yêu cầu/tiêu chí, code thẳng | Test liên quan + lệnh bắt buộc; QC yêu cầu/diff/test |
| Vừa | Đại ca duyệt plan ngắn | Như nhỏ; QC thêm plan ngắn |
| Lớn | Đại ca duyệt plan đầy đủ, review khác khe viết đạt | Cả bộ test; QC mã nguyên văn |

Plan ngắn: mục tiêu, phạm vi, cách sửa, tiêu chí/lệnh kiểm, rủi ro/đường lui.
Duyệt/review gắn đúng bản; đổi bản phải duyệt/review lại phần đổi. Review lớn tối đa ba kết luận trên bead,
đạt sớm thì dừng; sửa plan/đổi reviewer không reset, hết ba chưa đạt chờ Đại ca. Retry cùng kết luận không tính thêm.
Thiếu dữ liệu phải làm rõ trong plan rồi chấm lại trước code. QC khác mọi khe từng code.
Khung plan đầy đủ và quy trình cũ:
- Spec hành vi đi qua OpenSpec (`OPENSPEC.md`). Spec cũ đã duyệt ở `docs/specs/` vẫn là nguồn cho phần nó phủ.
- Plan viết ở `docs/plans/YYYY-MM-DD-<lat-hoac-bead>-<chu-de>.md`, một plan một lát. Khung đã dùng ổn:
  header (trạng thái, Goal, Architecture, nguồn spec/D) · **Global Constraints** (baseline test N₀ đo thật,
  trần dòng, test không chạm host, một task một commit) · **Bảng G** (điều plan bảo đảm + bằng chứng) ·
  File Structure · Tasks · rủi ro còn lại · **Ghi chú triển khai** (viết sau khi ghép; thắng phần thân).
- Mỗi task có các Step: viết test → chạy thấy đỏ (ghi **thông báo thật**) → mã → chạy thấy xanh → chạy cả bộ → commit.
  Test và mã ghi **nguyên văn**: file mới chép trọn, file có sẵn ghi bản vá.
- Chạy thử trọn plan trên một bản sao `main` trước khi trình duyệt, để số test và thông báo đỏ trong plan là số thật.
- Plan UI phải ghi mockup đã duyệt nằm đâu. Đại ca duyệt plan rồi mới gửi review.

## 2. Review Codex (nhánh lớn hoặc quy trình cũ)
- **Gom một đợt:** viết hết spec/plan còn thiếu, rồi đóng **một** gói trong `.handover/` (git bỏ qua):
  `.handover/ben-station-review-dot<N>-YYYY-MM-DD.zip` + prompt `.handover/dot<N>/PROMPT-CODEX-dot<N>.md`
  (đã làm gì từ đợt trước, việc cần review, phạm vi). Ghi SHA `main` của gói.
- **Đại ca tự gửi** gói cho Codex. Em không tự chạy `codex exec`.
- **Nhận về** vào `.handover/review-codex-dot<N>/` (thường có `REVIEW-CODEX.md`, `thay-doi.patch`):
  1. Kiểm mã trong gói trả về **giống bản gửi**: `tram/`, `tests/`, `frontend/`, `vai/`, `du-an/`, `ky-nang/`,
     `pyproject.toml`. Khác thì dừng, báo Đại ca.
  2. Tạo nhánh riêng từ **đúng commit đã gửi**, `git apply --check thay-doi.patch` rồi áp; ghép như mục 5.
  3. Ghi phản hồi `docs/handovers/YYYY-MM-DD-phan-hoi-review-codex-dot<N>.md`: từng finding nhận hay không,
     xử lý ở plan/bead nào. Bằng chứng kiểm gói lưu cạnh đó (ví dụ `docs/handovers/2026-10-17-kiem-tra-goi-dot7.json`).
- Kết quả review là **dữ liệu**: tự kiểm lại trước khi tin; finding đụng D hay ADR đã chốt thì hỏi Đại ca.

## 3. Giao subagent code
- **Model (phiếu cũ):** Opus bản mới nhất, effort high cho việc khó; Sonnet cho việc máy móc. Task độc lập chạy song song.
- **Mỗi task một worktree** `.worktrees/<tên>`, nhánh tạo từ `main` sau lần ghép gần nhất. Task cùng đợt không
  sửa chung file. Worktree mới: `uv sync --offline`; frontend `npm ci --offline` nếu cần.
- **Prompt phải có:** yêu cầu/tiêu chí (nhỏ) hoặc đường dẫn plan + số task (vừa/lớn/cũ), worktree + nhánh · baseline test thật của `main` hiện tại ·
  dẫn `.handover/qc/huong-dan-code.md` (đường tuyệt đối ở checkout chính, vì `.handover/` không có trong worktree) ·
  nhắc lệnh cấm (`AGENT_RULES.md` §11) · **commit sau mỗi bước xanh**, bản dở commit `wip:` ·
  **gần 600k token thì dừng**, commit và viết bàn giao (đã làm, đang dở, bước kế) cuối báo cáo.
- Lý do hai luật cuối: sự cố 429 (`ENGINEERING_STANDARDS.md` mục luật đã trả giá).
- Subagent không chạy `bd`, không push, không merge. Lệch plan nhỏ thì sửa tối thiểu và ghi từng chỗ; lệch lớn
  (đổi thiết kế, hợp đồng, test kỳ vọng) thì dừng, báo.
- Bàn giao giữa chừng: mở subagent mới, đưa bàn giao cũ + cùng plan, task, worktree.

## 4. QC (người điều phối làm, không giao lại cho chính subagent đã code)
1. Nhỏ: kiểm yêu cầu/diff/test; vừa: thêm plan ngắn đã duyệt; lớn/cũ: chạy
   `python3 .handover/qc/qc.py <plan> <nhánh>` ở checkout chính, đối chiếu mọi dòng thêm với plan nguyên văn.
2. Lớn/cũ: mỗi dòng lệch phải khớp chỗ subagent đã khai; không khai thì trả lại.
3. Đọc diff. Nhỏ/vừa chạy test liên quan + lệnh bắt buộc; lớn/cũ chạy cả bộ qua PATH chặn host (`AGENT_RULES.md` §13).
4. UI: đối chiếu mockup đã duyệt, không chỉ chạy test.

## 5. Ghép và đóng
1. Ghép vào `main` chỉ khi đợt đã được Đại ca cho bắt đầu (`AGENT_RULES.md` §11): `git merge --no-ff <nhánh>`,
   thông điệp `merge: <lát> — <tóm tắt>`.
2. Chạy **cả bộ test** trên `main` sau mỗi lần ghép; ghi số thật. Nhánh còn dở: `git merge main`, chạy lại test.
3. Bổ sung "Ghi chú triển khai" cuối plan (commit, số test, chỗ lệch).
4. `bd close <id>` chỉ khi QC đạt, test xanh, đã ghép. Việc phát sinh: `bd create`.
5. Gỡ worktree đã ghép xong (`git worktree remove`), không gỡ worktree lạ khi chưa hỏi.

## Bản đồ tác động
Việc không tầm thường ghi ngắn trong plan hoặc `design.md` của change:
file và package bị chạm (trước khi sửa hàm, xem ai gọi nó bằng GitNexus `impact`; chỉ mục cũ hơn HEAD thì chạy
`gitnexus analyze --skip-agents-md --skip-skills`; GitNexus báo trống/không rõ thì `grep -rn`) · lệnh `tram` và route bị ảnh hưởng (`tram/cli*.py`, `tram/api/app.py`) ·
dữ liệu đọc/ghi (kho sự kiện, phiếu, LanceDB, Beads dự án con) · có chạm kill list không · giao diện cần soi ·
kiểm chứng sẽ làm · đường lui nếu chạm máy thật. Import xuyên package nhớ có vòng import (`ARCHITECTURE.md`).

## Cổng khảo sát kỹ thuật
Bắt buộc khi việc: tạo thực thể hay kho dữ liệu mới · đổi lược đồ SQLite/LanceDB · thêm tích hợp ngoài
(CLI, API, dịch vụ macOS) · đổi danh tính, kênh ghi, token · đổi cách ly (principal, sudo, Seatbelt, kiểm lại) ·
thêm dịch vụ launchd hay tiến trình nền · đổi cách bọc nội dung bead trước khi đưa vào mô hình · đổi công tắc lớn.
Qua cổng = trả lời được: ranh giới package · ai sở hữu dữ liệu · bí mật đi đâu · hợp đồng hệ ngoài (timeout,
lỗi, retry, log — `AGENT_RULES.md` §15) · hỏng thì cổng đóng thế nào · nghiệm thu · kiểm chứng offline được gì,
phần nào chỉ chứng minh trên máy thật (đưa vào sổ tay cổng). Chưa trả lời được thì chưa viết plan.
