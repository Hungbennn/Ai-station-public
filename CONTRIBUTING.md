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
