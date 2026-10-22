# Phản hồi review Codex đợt 1+2 — 5 plan + spec 4 (13/10/2026)

Nguồn: `REVIEW-CODEX.md` và `thay-doi.patch` trong gói `ben-station-review-plan-dot12-2026-10-13-CODEX-reviewed.zip` (Đại ca gửi 13/10; bản sao ở `.handover/review-codex-dot12/`, git bỏ qua). Gói gửi đi: `.handover/ben-station-review-plan-dot12-2026-10-13.zip` (ảnh `main` `6d1cbe3`).

## Kết quả

- Codex review tĩnh (không chạy mã), **sửa thẳng vào `docs/`**: 5 plan (3a-1, 1b-3, 2b, 4a-1, 1b-2) và spec 0+1a, 2, 1b, 3, 4 — 3 Chặn (C01–C03), 19 Quan trọng (Q01–Q19), 3 Nhỏ (N01–N03), đều đã sửa trong tài liệu. Không sửa mã, không đổi quyết định đã chốt. Spec đã duyệt chỉ được thêm phụ lục đối chiếu (spec 1b §18, spec 3 §17, spec 0+1a mục bổ sung 4a-1, spec 2 các mục đồng bộ).
- Điều phối kiểm: `docs/` trên `main` trùng bản gửi; ngoài `docs/` không file nào đổi; trạng thái duyệt không bị tự đổi. Nhận toàn bộ vào commit `e5653f0`.
- Mã trong plan đã sửa **chưa chạy** (review tĩnh; Codex kiểm 124 hunk khớp ngữ cảnh theo thứ tự code, 179 khối Python parse được). Lúc code, mỗi task TDD sẽ lộ chỗ sai.

## Quyết định Đại ca (chat 13/10/2026): "Đồng ý toàn bộ, duyệt spec 4, code luôn"

- **Duyệt spec 4** (bản sau review).
- **Chốt mọi mục HỢP ĐỒNG MỚI theo đề xuất ở `REVIEW-CODEX.md` §3**:
  - 3a-1: giữ G2, G5, G6, G7, G8, G11, G18, G20, G23, G28; G31 bổ sung 422 `lan-chay-sai`; **thêm G35** (một bắt đầu/một kết thúc mỗi `(giao_id, lan)`, kết thúc cần bắt đầu, `lan` ≤ ngân sách).
  - 1b-3: giữ G9, G14; đổi G10 (`/ghi` 409 cùng mã khác nội dung), G13 (xoá cứng chỉ rút nội dung bước sinh đúng ID, giữ tombstone), G15 (timeline bead công khai che `nho.*`).
  - 1b-2: giữ G1; đổi G2 (lịch nạp 2 phút danh nghĩa, không SLA; tối đa 20 bài học khác nhau/phiếu, dedup); giữ đề xuất `mcp==1.30.0` (kiểm khi code Task 9).
  - 2b: giữ G3, G4, G7, G8, G14; đổi G6 (ccusage chỉ báo mã lỗi, cache tuần tự, TTL sau hoàn tất, từ chối ngày sai/NaN), G15 (polling 5 giây).
  - 4a-1: giữ G2, G5, G6, G7, G15, G28; đổi G8 (đối soát escalation chặt); **thêm G29** (chứng cứ theo `giao_id`+`luot`, kiểm digest trước cột 3), **G30** (câu hỏi chưa có escalation là công việc tồn), **G31** (gói quá trần thì không cấp/claim); chấp nhận rủi ro snapshot G3 (4a-2 đọc lại Beads ngay trước cấp).
- **Code ngay** theo thứ tự `3a-1 → 1b-3 → 2b → 4a-1 → 1b-2` (Opus effort high, task song song theo sơ đồ đợt; Em QC + ghép từng task; mốc test `main` = 720).
