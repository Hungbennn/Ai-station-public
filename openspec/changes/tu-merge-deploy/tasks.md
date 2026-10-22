# Mốc nghiệm thu — không phải danh sách việc code

Plan TDD: [2026-10-20-tu-merge-deploy](../../../docs/plans/2026-10-20-tu-merge-deploy.md).
QĐ1–QĐ4 đã chốt A; đã hợp nhất ownership hai change. Chỉ NT1 có bằng chứng tài liệu;
NT2–NT8 giữ trống tới khi có log đúng cổng, không suy từ mã trong plan hay test nền.

- [x] **NT1 — Chốt hành vi và nguồn:** QĐ1–QĐ4 theo `QUYET-DINH.md`; bảng giữ/bỏ trong plan.
  Change này chỉ giữ ADDED `tu-merge`/`tu-deploy`; change 18/10 chỉ giữ `dieu-khien-tu-dong`.
  Bản cũ lưu ngoài `specs/`. Đây chưa phải bằng chứng validate bản pin hay được phép chạy thật.
- [ ] **NT2 — Đúng bằng chứng:** Task 2, G3–G4; thiếu/sai lượt/ref/tiêu chí/QC/thu hồi đều không merge;
  duyệt spec không duyệt commit mới. Chạy test bằng chứng cùng hồi quy spec/code.
- [ ] **NT3 — GitHub:** Task 1 và 8, G2, R1; required checks/strict/app nguồn/không bypass;
  nhánh đổi, check thiếu, xung đột, mất phản hồi, ba lần lỗi đọc, gửi lại và merge queue đều có kiểm chứng.
- [ ] **NT4 — Quyền và điểm dừng:** Task 2, 6–8, G4/G8–G10, R5; passkey, cài đặt phiên bản,
  Estop/tạm dừng/khoá ghi/cổng kiểm; API trực tiếp không vượt cửa.
- [ ] **NT5 — Đúng bản và đích:** Task 3–5, 7–8, G5–G8, R2–R3; H đạt/M lỗi không deploy,
  code ngoài luồng không tự lọt, artifact đúng bản, hai dự án không đụng nhau, mỗi đích một chuỗi.
- [ ] **NT6 — Rollback:** Task 3, 5, 7–8, G7/G9, R4; thiếu L/tương thích dữ liệu thì chặn;
  HTTP 200 sai bản không đạt; deploy lỗi đã rõ mới lùi; hỏng ba lần tắt; không sửa dữ liệu/Git.
- [ ] **NT7 — Gián đoạn và báo tin:** Task 5–8, G8–G10, R5; timeout/mất điện/đích còn chạy
  giữ không rõ; đối soát có passkey; yêu cầu lặp/Telegram lỗi không lặp tác dụng phụ hoặc lộ bí mật.
- [ ] **NT8 — Trước archive:** toàn bộ G1–G12 và R0–R5 của plan đạt, review/QC xong,
  đúng OpenSpec 1.14.0 validate cả hai change. Đại ca chuẩn bị branch protection, đường deploy từng
  dự án và thử quay lại; ghi vào sổ tay cổng hiện có rồi mới bật từng dự án con.
