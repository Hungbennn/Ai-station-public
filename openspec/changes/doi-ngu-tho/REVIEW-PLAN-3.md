# Vòng 3 — sửa gọn theo main

20/10/2026 · `spec/doi-ngu-tho` · HEAD `c73248d` (đã ghép main `d149183`, gồm `71ff846`).
Đã đọc CHUNG.md và REVIEW-PLAN-2; chỉ sửa hai điểm được yêu cầu, không review lại toàn bộ.

## Đã sửa

- Task 9: bỏ nhánh ghi `bat_ghi=False` khi tắt giao; giữ nguyên từng byte YAML dự án.
  Nhánh bật vẫn đảm bảo True. Sửa câu sổ tay “trả về chỉ đọc”, đồng bộ spec/design/tasks.
- `con_phieu_b()` lấy `su-kien.db` qua `tram.duong_dan.tram_home()`/`TRAM_HOME`, URI mã hoá đúng,
  giữ `mode=ro`, timeout 5 giây; thiếu DB thì lỗi, không tạo DB mới.
- Rà các giả định `bat_ghi` trong plan/change/test: không còn giả định main ben-station tắt ghi.
  Fixture `false` tự tạo trong tmp được giữ để kiểm bật; policy của HEAD vẫn kiểm True.

## Đã kiểm

- RED thật trên mã vòng 2: **3 failed, 7 deselected** (`AssertionError`: hai ca YAML bị đổi khi tắt,
  một ca URI không theo TRAM_HOME). Mock kiểm URI trước mở nên không đụng DB thật.
  Log: `/private/tmp/doi-v3-nhuw8jrj/red.txt`.
- Bản sao sạch HEAD `/private/tmp/doi-v3-4iqor45l/rehearsal`: áp **45 khối Create/Modify**, **51 tệp**
  kể cả test Step 1; toàn bộ **29 diff** qua `git apply --check` rồi áp theo thứ tự task, không cần sửa diff.
- Chạy từ bản sao bằng thư viện có sẵn, offline:
  `TRAM_KIEM_DA_CHUAN_BI=1 tests/chan_host/chay.sh -q tests/test_doi_ngu*.py tests/test_phu_thuoc*.py tests/test_do_dai_ma.py tests/test_vong_import.py`
  → **145 passed, 0 failed**. Bao gồm giữ True/False khi tắt, bật thành True, lọc phiếu B hiệu lực,
  đường TRAM_HOME có khoảng trắng/`#`, thiếu DB không tạo mới và policy main True.
  Log: `/private/tmp/doi-v3-4iqor45l/green.txt`.
- **0 dòng chặn mới**; runner ghi 11 điểm mù Python con của helper dependency và 26 push giả lập.
  Không chạy toàn suite hay cổng máy thật trong vòng sửa gọn này.
- `DO_NOT_TRACK=1 OPENSPEC_TELEMETRY=0 openspec validate doi-ngu-tho --strict` → **valid**;
  `git diff --check` sạch. Skill kiểm chứng được dùng để ghi RED/GREEN mới, không lấy kết quả vòng 2 thay thế.

Không sửa `tram/`, tests hay cấu hình của worktree; không commit/bd/push. Giữ nguyên các cổng chạy thật.

**ĐẠT để code.**
