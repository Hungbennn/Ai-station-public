# Kết quả soạn plan giao việc theo cỡ — 2026-10-21

> Báo cáo lịch sử của bản 14 task. Kết luận hiện hành sau review độc lập và bản plan
> 6 task: [REVIEW-PLAN-1.md](REVIEW-PLAN-1.md). Số đo dưới đây không phải số đo bản đã sửa.

**Plan:** [2026-10-21-giao-viec-theo-co.md](../../../docs/plans/2026-10-21-giao-viec-theo-co.md).
**Nền:** HEAD `f1ebb30`, nhánh `spec/giao-viec-theo-co`; QĐ1–3,5=A, QĐ4=C.

## Công việc

14 task TDD bám S1–S11: cấu hình/chấm cỡ, model của khe và kiểm stream, plan/review/duyệt đúng bản,
nối chọn/cấp phiếu và cổng pipeline, lịch sử sự kiện, tương thích cũ, bảo vệ vùng nhạy cảm,
nâng cỡ sau code, phiếu plan/review tự động, nguồn công bố đã kiểm và cách đếm file phụ trợ.
Plan có Global Constraints, bảng G/cổng, Files, test/mã nguyên văn và kết quả RED→GREEN từng task.
Sổ tay chạy Opus/Sonnet trên hai khe thật nằm cuối plan, **chưa chạy**.

## Kiểm chứng

- Trích 31 khối diff từ chính plan; `git apply --check` rồi áp tuần tự trên bản sao sạch của HEAD.
  52 file kết quả khớp từng byte với cây đã thử. Không sửa mã trong worktree.
- Mỗi task đã đo RED trước mã và GREEN sau mã; test liên quan chạy bằng `tests/chan_host/chay.sh`,
  PYTHONPATH trỏ bản sao, đúng ba biến UV Đại ca chỉ định.
- Lần cuối: **219 passed, 4 failed**, 73.75s; có kiểm trần dòng và vòng import.
  Baseline riêng: **160 passed, cùng 4 failed**, 70.17s. Bốn ca thu hồi tiến trình được ghi tên trong plan;
  sandbox chặn `ps`, không tính các ca này thành lỗi feature hoặc test đạt.
- Nhật ký chặn: **0 dòng mới**, 7 điểm mù Python con, 66 push giả lập, không push thật.
  Full suite từng chạy dở rồi ngắt; không dùng làm bằng chứng toàn bộ suite đạt.
- `DO_NOT_TRACK=1 openspec validate giao-viec-theo-co --strict`: **đạt**, CLI cài sẵn 1.11.0.
- `/opt/homebrew/bin/claude --version`: **2.1.227**; help xác nhận `--model <model>`, alias opus/sonnet.
  Không chạy sinh nội dung, không đoán cờ.
- GitNexus impact không có chỉ mục `ben-station`; dùng `rg` truy caller theo playbook.

## Rủi ro và giới hạn

Chưa chứng minh model/cách ly/quota/QC trên hai khe thật. Cần chạy lại toàn bộ suite ngoài sandbox
và OpenSpec đúng bản 1.14.0 ghim trong tài liệu kho. Luồng phiếu spec dùng cho plan/review cần review
kỹ trước triển khai; bản vá có đồng bộ bốn nguồn luật và giữ nguyên ngân sách, principal, kiểm công bố.
Đọc Beads và ghi SQLite vẫn không phải giao dịch phân tán. Khối cấu hình mới chưa được bật;
thiếu khối mới tiếp tục hành vi cũ. Log rehearsal nằm trong `/private/tmp/codex-chon-co/`, có thể bị dọn.

Phiên này chỉ tạo plan và báo cáo này; không sửa `tram/`, không commit, không gọi `bd`, không push.

**Kết luận: ĐẠT kiểm chứng offline cho bản plan để review; chưa nghiệm thu triển khai hoặc chạy thật.**
