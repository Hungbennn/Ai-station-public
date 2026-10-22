# Checklist bàn giao

> **Đóng băng 17/10/2026** (Đại ca chốt). Việc còn mở đã chuyển sang Beads (`bd ready`, epic `bs-2bd`, `bs-8eh`, `bs-863`). Không thêm việc mới vào đây.

- [x] Ghi xác nhận ba nhóm thành D45–D47, phân biệt chốt hướng và nghiệm thu.
- [x] Thay plan 3c/4d hiện hành, lưu nguyên lịch sử đối chiếu.
- [x] Thêm plan quota và phụ thuộc primitive process.
- [x] Cập nhật cổng runbook và prompt Claude.
- [x] B0: đối chiếu repo đích, baseline và độ an toàn test. (2242 py / 95 node, `bs-863.1`)
- [x] 3C-A: chứng minh thiết kế boundary khả thi. (thiết kế; điều kiện OS ở G4)
- [x] 4D-0: chốt kỹ thuật API/storage/recovery.
- [x] P1, 3C-B: lifecycle hữu hạn và UID thực. (`0e33fbf`)
- [x] 3C-C: tree identity CRLF/encoding. (`9ee1ed3`)
- [x] Q1, Q2: quota đúng principal, heartbeat và cleanup. (`0e33fbf`; G5 chưa chạy)
- [x] 3C-D: thực hiện boundary, regression và review. (D1–D6 + S6: `9ee1ed3`, `59f8281`; còn 3C-D7 chờ G3)
- [x] 4D-1, 4D-2, 4D-3: service/API/client và tests. (`a02728b`)
- [ ] I1: đồng bộ spec, kiểm tích hợp, báo cáo bằng chứng. **Đang làm 17/10** (nhánh `docs/i1-dot7`).
- [ ] G3–G7: xin quyền kịch bản cụ thể, nghiệm thu thật; không đánh dấu trước.

## Thêm sau 17/10 (I1)

- [x] V1 Task 1–3 (`9a0c0ff`) và 1a-2 Task 4–6 (`2d0b5ba`) ghép trước 3c.
- [ ] Review Codex gói đợt 7–8 (plan 3c + P1 + phụ lục 3C-A; sửa chu kỳ 2 đợt 8 chưa qua người review mới).
- [ ] 3C-D7: bộ đọc launchd — sau G3.3, fixture là tệp đo thật.
- [ ] `bs-863.14` kiem_am/kiem_cong/kiem_cach_ly dưới sudo (đang làm).
- [ ] `bs-863.15` mo_coi kiểm thời điểm khởi động của PID.
- [ ] `bs-863.16` theo_doi.py `join()` không hạn.
- [ ] `bs-863.17` `codex login status` dưới principal của khe.
- [ ] `bs-863.18` H1 `stdin=` cho `chay_gioi_han` (`ban_chep._chay`).
- [ ] `bs-863.19` Ctrl-C ở CLI cha của harness.
- [ ] Người điều phối xem lại bead: `bs-863.13` đóng sớm; `bs-urj.10` đóng trước 4D-4; `bs-urj.12`–`.14` còn mở dù mã đã ghép.


## Review độc lập đợt 7 — 17/10/2026

- [x] Review tĩnh snapshot; tạo REVIEW-CODEX.md và plan V2. Không chạy tests/OS/API, không sửa source.
- [ ] V2-0 identity process (.15), V2-1 interruption (.19), V2-6a stdin (.18): chưa G4/G5 theo phụ thuộc.
- [ ] V2-2 schema đối soát: trước G6.
- [ ] V2-3 inventory mọi dự án, V2-4 probe evidence, V2-5 profile attestation: trước G4.
- [ ] V2-6b .14/.17 trước G5; V2-6c .16 trước G7.
- [ ] V2-7 cleanup tests/error body; guard host/mạng phải kiểm trước chạy test.
- [ ] V2-8 nghiệm thu gate theo `docs/handovers/2026-10-17-cong-sau-review-dot7.md`.

Các tick/count cũ là lịch sử tác giả, không phải reviewer đo lại. Không tự đóng/mở Beads; người điều phối đối soát bs-863.13 và bs-urj.10 cùng backlog. V2 có task thiết kế còn mở, chưa đủ giao code toàn lát.
