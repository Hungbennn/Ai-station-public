Plan bổ sung token file (thắng phần Keychain của plan 20/10):
[2026-10-21-doi-ngu-token-file.md](../../../docs/plans/2026-10-21-doi-ngu-token-file.md).

Plan TDD: [2026-10-20-doi-ngu-tho.md](../../../docs/plans/2026-10-20-doi-ngu-tho.md).

Các ô dưới là mốc nghiệm thu, **chưa đánh dấu đạt bằng việc soạn xong tài liệu**.

- [x] 1a. Đại ca chốt QĐ1–QĐ4 = A, QĐ5 = B (20/10/2026).
- [ ] 1b. Ghi ADR và cập nhật nguồn sở hữu cho INV-001/quyền commit trong phiên triển khai.
- [ ] 2. Cài khe 2 trong trạng thái tắt, không sửa Uq. Kiểm: Task 1 qua TDD và bằng chứng R1.
- [ ] 3. Đăng ký B hiện hai thẻ tắt; HTTP lỗi/retry và token khác máy được xử lý đúng.
  Kiểm: Task 2, API giả, R2/R3; không gọi lệnh cấp mã ghép cũ.
- [ ] 4. Kiểm đúng phạm vi ben-station; HR chưa clone không chặn kiểm repo.
  Kiểm: Task 3 và kết quả chẩn đoán R4.
- [ ] 5. Hai token setup-token riêng hoạt động qua FD từ daemon và tự chạy sau reboot không mở khoá.
  Kiểm: plan bổ sung Task 1–4, S2/S3/R5; không chỉ auth status tại Terminal.
- [x] 5a. QĐ2 sửa 21/10: ghi bằng chứng Keychain daemon mã 36 và ngoại lệ file; ADR-0009 cập nhật.
- [ ] 5b. Token máy B file 0600, nguyên tử/no-follow; từ xa vẫn Keychain; bootstrap trước YAML.
  Kiểm: plan bổ sung Task 1–2 RED→GREEN trên bản sao HEAD, sau code/QC mới nghiệm thu.
- [ ] 5c. Wrapper dưới UID khe, FD sau sudo, không token trong argv/log/env quản lý; sổ tay bỏ keychain.
  Kiểm: plan bổ sung Task 3–4; S2 bản CLI thực và không credential ngoài dự kiến.
- [ ] 5d. Sáu phép S6 file có đối chứng: khe kia/quản lý→token khe, khe→token máy bị từ chối quyền.
  Kiểm: Task 4; thiếu đích/lệnh không đạt. Giới hạn sudoers ALL theo QĐ2 phải được chốt rõ;
  không tuyên bố chống quản lý đổi UID. bs-2bd.11 chỉ được giải sau bằng chứng R5, không đóng ở phiên plan.
- [ ] 6. Khe không ghi Git/settings, quản lý chốt SHA sau thu hồi.
  Kiểm: Task 5–7, bài vòng thợ đầy đủ, thăm dò S6 có đối chứng ở R4. Task 6 có cổng cha riêng/lượt; kiểm thêm restart/phiếu cũ, dọn lỗi và file UID khe ở R4/R7.
- [ ] 6b. Worktree ben-station có dependency Python/Node đã kiểm lock để chạy kiểm offline dưới khe.
  Kiểm: Task 6 dùng bundle root hiện có (reader/helper G4), ca lock/hash/symlink/đích sai;
  chạy đủ 6 lệnh kiểm mặc định offline ở R4/R7, không dùng cache/venv nhà hungle.
- [ ] 7. Nguồn đọc cục bộ cập nhật đúng SHA; origin/github đối chiếu; đường trả kho-tho đạt.
  Kiểm: Task 9 và S7/R3; không có credential GitHub ở khe/quản lý thợ.
- [ ] 8. Mọi bead đủ điều kiện của ben-station được xét; HR bị chặn trước claim/cấp. Giữ hạn mức/quota.
  Kiểm: Task 8 với bộ giao thật trên dữ liệu giả, R6.
- [ ] 9. S1/S4/S8, nhịp/thu hồi/estop/API/DB của hai Claude có bằng chứng; không kéo Codex G5 vào.
  Kiểm: hồi quy và bảng R4; chưa biết quota vẫn hiện chưa biết.
- [ ] 10. Các bước sudo có một lệnh, log kín, lỗi dừng đúng bước, đăng nhập không bị thu log.
  Kiểm: Task 9 và từng R1–R7, không chạy thử wrapper bằng sudo trong test.
  Tắt giao giữ nguyên `bat_ghi` ben-station; đếm phiếu theo `TRAM_HOME`, chỉ đọc và không tạo DB khi thiếu.
- [ ] 11. Toàn suite + QC đạt, một việc thật hoàn tất với QC khác khe, thử đường dừng.
  Kiểm: cuối plan và R7. Chỉ sau đó archive; cập nhật Beads ở phiên được phép.
