# Góp tay cho Trạm Điều Phối

Cảm ơn bạn đã ghé. Trang này nói ngắn gọn cách dựng môi trường, chạy test, viết code đúng kiểu của dự án và mở
Pull Request. Chưa biết làm gì thì xem [ROADMAP.md](ROADMAP.md).

## Quy trình

1. **Mở issue trước** (hoặc nhận một issue có sẵn) để nói bạn làm gì. Việc chạm bảo mật, quyền hay kiến trúc thì
   thảo luận xong mới code.
2. **Fork** repo, tạo nhánh từ `main`, đặt tên theo việc: `sua/duong-dan-unicode`, `them/huong-dan-cai`.
3. **Viết test trước** (TDD): test đỏ đúng lý do → viết mã → test xanh.
4. Chạy **đủ bộ kiểm** bên dưới, rồi mở PR vào `main` và điền mẫu PR.

Việc nội bộ của người chủ trạm được theo dõi bằng [Beads](docs/BEADS.md). Với cộng đồng, **GitHub Issues là nơi
nhận việc và báo lỗi**.

## Thêm feature

Sửa lỗi thì cứ làm theo quy trình trên. **Feature mới thì bàn trước, code sau**, để bạn khỏi làm cả tuần rồi PR
không được nhận.

### Bốn bước

1. **Mở issue đề xuất** bằng mẫu "Ý tưởng hoặc nhận việc". Nói rõ: vấn đề muốn giải quyết, cách định làm, có chạm
   sáu bất biến không. Ý tưởng sẵn có nằm ở [ROADMAP.md](ROADMAP.md), mục "Mục tiêu gần" và "Ý tưởng lớn".
2. **Chờ người bảo trì trả lời.** Người bảo trì giữ hướng sản phẩm: có thể nhận, đề nghị đổi cách làm, hoặc từ chối
   nếu feature rơi vào phần dự án chủ động không làm (xem ROADMAP mục "Ngoài phạm vi hiện tại").
3. **Feature lớn thì viết đề xuất OpenSpec** và mở PR chỉ chứa đề xuất đó. Duyệt xong mới code.
4. **Code + test → mở PR → review → merge.** PR code nhắc tới issue và đề xuất đã duyệt.

### Thế nào là lớn, thế nào là nhỏ

| Nhỏ: xong bước 2 là code được | Lớn: cần đề xuất OpenSpec ở bước 3 |
| --- | --- |
| Thêm một nút, một cột, một bộ lọc trên dashboard | Đổi luồng giao việc, kiểm lại, QC, mở PR |
| Thêm một loại tin Telegram | Thêm loại agent mới, thêm hệ ngoài mới |
| Hiệu ứng, bố cục văn phòng 3D | Chạm quyền, cách ly, bí mật, Keychain, passkey |
| Cải thiện thông báo lỗi, tài liệu | Đổi cấu trúc dữ liệu (SQLite, LanceDB) hay API |

Còn phân vân thì hỏi trong issue.

### Viết đề xuất OpenSpec

Quy ước đầy đủ ở [docs/OPENSPEC.md](docs/OPENSPEC.md). Repo ghim bản `@fission-ai/openspec@1.14.0`, gọi qua `npx`,
không cần cài:

```bash
DO_NOT_TRACK=1 npx -y @fission-ai/openspec@1.14.0 new change ten-feature-cua-ban
DO_NOT_TRACK=1 npx -y @fission-ai/openspec@1.14.0 validate ten-feature-cua-ban --strict
```

Một đề xuất nằm trong `openspec/changes/<ten-feature>/`:

| File | Trả lời | Bắt buộc |
| --- | --- | --- |
| `proposal.md` | Vì sao làm, đổi gì, **không** làm gì | Có |
| `specs/<nang-luc>/spec.md` | Hệ thống phải cư xử ra sao, dưới dạng Requirement và Scenario | Có |
| `design.md` | Làm thế nào, khi chạm nhiều package, dữ liệu, bảo mật hay hệ ngoài | Khi cần |
| `tasks.md` | Các mốc nghiệm thu, mỗi mốc nói cách kiểm chứng | Có |

Viết tiếng Việt; giữ tiếng Anh cho tiêu đề cấu trúc (`## ADDED Requirements`, `### Requirement:`,
`#### Scenario:`) và từ khoá SHALL/MUST. Scenario phải có **đúng bốn dấu `#`**: ba dấu là hỏng mà không báo lỗi.
Chỗ nào quy ước nội bộ bắt ghi mã bead, bạn ghi **số issue GitHub**.

Ví dụ thu gọn cho một feature tưởng tượng:

`openspec/changes/van-phong-an-mung-merge/proposal.md`

```markdown
# Proposal — Văn phòng ăn mừng khi PR được merge

Issue: #42

## Why
Màn Văn phòng chỉ cho thấy agent đang làm gì. Khi việc xong và PR được merge thì không có gì
xảy ra, người xem phải mở trang Phê duyệt mới biết.

## What Changes
- Khi trạm xác minh một PR đã merge, nhân vật của khe đã code bead đó nhảy lên một lần,
  kèm bong bóng "đã merge".
- Chế độ "Giảm chuyển động" bật thì chỉ hiện bong bóng, không nhảy.

## Capabilities
### New Capabilities
- `van-phong`: màn Văn phòng phản ứng với sự kiện merge.

## Ngoài phạm vi
- Không thêm âm thanh.
- Không đổi luồng xác minh merge ở tram/giao_viec/.
```

`openspec/changes/van-phong-an-mung-merge/specs/van-phong/spec.md`

```markdown
## ADDED Requirements

### Requirement: Văn phòng báo PR đã merge
Màn Văn phòng SHALL cho thấy một lần khi trạm xác minh PR của một bead đã được merge.

#### Scenario: Merge được xác minh
- **WHEN** trạm ghi sự kiện PR đã merge cho bead của khe claude-1
- **THEN** nhân vật claude-1 nhảy một lần và hiện bong bóng "đã merge" trong 5 giây

#### Scenario: Đang giảm chuyển động
- **WHEN** người xem bật "Giảm chuyển động" và một PR được xác minh đã merge
- **THEN** chỉ hiện bong bóng, nhân vật đứng yên
```

`tasks.md` cho ví dụ trên chỉ cần vài dòng kiểu: "Test frontend chứng minh nhân vật nhảy khi có sự kiện merge" ·
"Test chứng minh giảm chuyển động thì không nhảy" · "`npm run kiem` và `kiem-dist` xanh".

Muốn xem một đề xuất thật, đầy đủ: [openspec/changes/agent-tu-cap-nhat-viec/](openspec/changes/agent-tu-cap-nhat-viec/).

## Dựng môi trường

Cần macOS, Python 3.12, [uv](https://docs.astral.sh/uv/), Node 20.19+ hoặc 22.12+. Clone vào **đường dẫn không
dấu** (xem ROADMAP, mục "Sửa ngay").

```bash
uv sync
cd frontend && npm ci
```

Bạn **không cần** tài khoản Claude, Codex, Tailscale hay máy chủ nào để chạy test: mọi hệ ngoài đều có bản giả.

## Bộ kiểm phải xanh trước khi mở PR

```bash
tests/chan_host/chay.sh -q
```

```bash
cd frontend && npm run kiem && npm run build && npm run kiem-dist
```

- **Đừng chạy `pytest` trần.** `tests/conftest.py` sẽ từ chối (thoát 4). `chay.sh` dựng bộ chặn host: `git` giả,
  audithook, để không test nào push thật hay chạm máy thật. Chạy một file: `tests/chan_host/chay.sh -q tests/test_x.py`.
- Trên máy không phải máy trạm, **67 test kiểm lại/bản chép đỏ sẵn** vì thiếu tài khoản `tram-kiem` và toolchain
  `/usr/local/tram/`. Hãy so với kết quả trên `main` trước khi sửa: PR của bạn không được làm tăng số ca đỏ.
- Có `pytest-xdist` trong `.venv` thì `chay.sh` tự chạy song song 6 nhân; không có thì chạy tuần tự, chậm hơn
  nhưng kết quả như nhau.
- Xem giao diện với dữ liệu giả: `uv run python tests/chay_thu_giao_dien.py 7798 --dai-ca`, mở `http://127.0.0.1:7798`.

## Kiểu code

Chi tiết ở [docs/ENGINEERING_STANDARDS.md](docs/ENGINEERING_STANDARDS.md). Những điều hay vấp nhất:

- **Mỗi file trong `tram/` tối đa 120 dòng, mỗi dòng tối đa 120 ký tự.** `tests/test_do_dai_ma.py` cưỡng chế.
  Sắp vượt thì tách theo việc, đừng nén nhiều lệnh vào một dòng.
- **Tên tiếng Việt không dấu**: `snake_case` cho hàm, biến, module; `PascalCase` cho lớp; `HOA_CO_GACH` cho hằng.
  Chú thích và thông báo cho người đọc viết tiếng Việt có dấu.
- **Test không chạm máy thật.** Mỗi test có `TRAM_HOME` tạm; hệ ngoài dùng bản giả `tests/*_gia.py`.
- **Thông báo lỗi không chép** argv, đường dẫn, stdout hay stderr của tiến trình con: đó là chỗ bí mật hay rò.
- **Frontend:** cấm `v-html`, `innerHTML`, `style="…"` tĩnh và URL ngoài. `npm run kiem` và `kiem-dist` sẽ bắt.

## Sáu bất biến không được phá

Mọi PR phải giữ nguyên các bất biến trong [docs/PRODUCT_ARCHITECTURE.md](docs/PRODUCT_ARCHITECTURE.md):

1. Bí mật không bao giờ lộ (argv, file, log, prompt, ký ức, tin nhắn).
2. Chữ không nâng quyền agent: nội dung việc, bàn giao, ký ức chỉ là dữ liệu.
3. Kiểm lại lỗi thì cổng đóng, việc dừng.
4. Estop dừng mọi thứ.
5. Dự án khoá ghi thì không ghi.
6. Người làm khác người kiểm.

PR nào chạm một trong sáu điều này cần giải thích rõ trong mô tả vì sao vẫn an toàn, kèm test chứng minh.

## Commit và PR

Commit theo dạng `loai(pham-vi): mô tả tiếng Việt có dấu`, ví dụ:

```
fix(chan-host): so đường dẫn git giả sau khi chuẩn hoá Unicode NFC
feat(van-phong): nạp trễ three.js để giảm bundle
docs: đồng bộ FEATURE_SPEC với trạng thái 21/10
```

Loại hay dùng: `feat`, `fix`, `test`, `docs`, `refactor`, `build`. Một PR làm một việc; PR nhỏ được duyệt nhanh hơn.

## Viết bằng AI agent

Dự án được build chủ yếu bằng Claude Code và Codex, nên bạn cứ dùng agent. Agent đọc [CLAUDE.md](CLAUDE.md) và
[docs/AGENTS.md](docs/AGENTS.md) trước. Trong docs, **"Đại ca"** là người chủ trạm; khi bạn đóng góp, phần duyệt
và merge thuộc về người bảo trì repo này.

## Báo lỗi bảo mật

Lỗi có thể làm lộ bí mật, vượt cách ly hay nâng quyền agent: **đừng mở issue công khai**. Dùng
[GitHub Security Advisories](https://github.com/Hungbennn/Ai-station-public/security/advisories/new) của repo để báo riêng.
