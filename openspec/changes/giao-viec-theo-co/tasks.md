# Mốc nghiệm thu

QĐ1=A, QĐ2=A, QĐ3=A, QĐ4=C, QĐ5=A đã chốt 20/10/2026.
Plan dựa nền đội ngũ thợ trên HEAD `51ec56f`:
[6 task TDD](../../../docs/plans/2026-10-21-giao-viec-theo-co.md).
Review/rehearsal không phải triển khai; bằng chứng ở [REVIEW-PLAN-1.md](REVIEW-PLAN-1.md).
Các ô dưới là nghiệm thu triển khai, chưa được đánh dấu đạt.

- [ ] 1. Đồng bộ luật plan/review/QC theo QĐ2-A trước khi bật nhánh gọn;
  đối chiếu các nguồn ở design §3; Task 6.
- [ ] 2. Đếm và ngưỡng đúng, thiếu dữ liệu ít nhất vừa, giữ sàn nguy hiểm.
  Kiểm offline S1–S2 với Beads/diff giả; Task 1, 5.
- [ ] 3. Nhãn chỉ nâng cỡ, giữ nguyên lượt đang chạy. Kiểm offline S3; Task 1–2, 5.
- [ ] 4. Ba quy trình, trần 3 vòng và các cổng giữ đúng. Kiểm offline S4–S6; Task 3–6.
- [ ] 5. Model đúng, thiếu khe thì chờ, QC khác khe code. Kiểm offline S7–S8
  với khe/CLI giả, không coi lời tự khai của thợ là chứng cứ; Task 2, 4–5.
- [ ] 6. Phạm vi mở rộng được kiểm lại; lưu/khôi phục theo lượt và luật mới
  không sửa lịch sử. Kiểm offline S9–S11, không log bead/prompt/bí mật; Task 1–2, 5.
- [ ] 7. Chứng minh hai model chạy đúng, kiểm lại cách ly và QC khác khe trên
  máy thật theo cổng được Đại ca cho phép. Test giả không thay bằng chứng này.

Kiểm tài liệu: `openspec validate giao-viec-theo-co --strict`, đường dẫn và
liên kết. Khi có code: `tests/chan_host/chay.sh -q`, không có dòng chặn mới.
Chỉ archive khi mọi tình huống có bằng chứng, không chỉ vì validate xanh.
