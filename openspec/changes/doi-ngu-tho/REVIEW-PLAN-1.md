# Review độc lập + sửa — doi-ngu-tho

Ngày 20/10/2026 · nhánh `spec/doi-ngu-tho` · HEAD `be58ca9` (mã nền `19a86c0`).
Đọc CHUNG.md, CLAUDE.md, bộ luật/tài liệu dự án, toàn change, plan và các luồng mã liên quan.
Lời Đại ca trong phiên này thắng CHUNG.md ở phạm vi: giữ thay đổi spec/plan và báo cáo này;
không hoàn nguyên tài liệu về HEAD, không tạo KET-QUA-CODEX.md thay cho báo cáo được yêu cầu.

## Lỗi, theo mức nặng → nhẹ

| Mức | Lỗi và bằng chứng | Xử lý / trạng thái |
|---|---|---|
| **Chặn C1** | Task 6 cấp các ACL mới, nhưng `tram/tho/phieu_chay.py:don_phieu` vẫn gọi `lenh_trao_quyen(..., thu=True)` với `QUYEN_GHI` cũ. Các entry `chmod -a` không khớp entry `+a`; cùng worktree dự án/nhánh được dùng lại khi đổi code → QC. File mới còn thuộc UID khe, nên không thể giả định manager luôn thu quyền/chmod được. | **Còn mở.** Đã siết gốc cây/phiếu về 700 và thêm quyền đọc settings rõ ràng, nhưng đó chưa sửa vòng đời thu quyền. Plan/design đã ghi chặn triển khai; cần bản vá và test đổi lượt/khe, retry/dừng mềm, sở hữu file. Không mở sudo root/Git để chữa. |
| **Quan trọng C2** | R1 chỉ `uv sync` cho runtime quản lý. `chuan_bi_worktree` + `chuan_bi` không chuẩn bị `.venv`/`frontend/node_modules` của worktree, trong khi cấu hình ben-station yêu cầu Python và npm. Chưa có đường cấp cache/artifact offline cho khe. Phép kiểm worktree mới xác nhận không có `.venv/bin/python`. | **Còn mở.** Cần mã/test chuẩn bị dependency đúng lock dưới quyền phù hợp và chạy đủ lệnh kiểm ben-station offline. Không dùng venv/cache trong nhà hungle hoặc sửa Uq. Ghi thành C2 trong plan/design/tasks. |
| **Quan trọng** | Kho nguồn không checkout chỉ fetch `refs/remotes/origin/main`; thợ fetch mặc định `refs/heads/main`, nên nhận SHA cũ. Test Git cục bộ tạo commit mới đã tái hiện `origin/main != SHA mới`. | **Đã sửa Task 9/R3/design:** đặt refspec `+refs/remotes/origin/*:refs/remotes/origin/*`, fetch rồi kiểm thấy đúng commit mới. Không thêm mirror/dịch vụ. |
| **Quan trọng** | QĐ5-B đã chốt nhưng Goal, G7, Task 8, spec và R6/R7 còn khóa một bead và đòi duyệt lần mở rộng. | **Đã sửa xuyên suốt:** chỉ whitelist dự án `[ben-station]`; bỏ trường/parser/predicate bead, bỏ hỏi mã bead và bước mở rộng sau thử. `bat-giao` dọn khóa bead cũ, giữ các hạn mức. QĐ1–QĐ4=A, QĐ5=B được ghi là đã chốt. |
| **Quan trọng** | Sổ tay nói tự merge/deploy tắt, nhưng `bat-giao` không kiểm trạng thái thực lưu trong sự kiện. Nếu đã bật từ trước thì mở giao vẫn chạy tiếp. | **Đã sửa Task 9:** đọc DB chỉ đọc qua `doc_cai_dat`, từ chối trước khi ghi cấu hình nếu một công tắc đang bật. Không tự tắt công tắc hoặc ghi quyền thay Đại ca. Hai test bật từng công tắc đều từ đỏ sang xanh. |
| **Vừa** | `KeHoach.han_lenh=30` chỉ áp `kh.lenh`; lệnh tạo tài nguyên nằm trong callback `kh.buoc` vẫn nhận `timeout=None`. | **Đã sửa Task 1:** truyền runner có timeout 30 vào callback; test thực thi callback với hệ giả chứng minh hạn được áp. Bắt cả `SubprocessError` tại cửa cài. |
| **Vừa** | YAML hỏng làm daemon thoát lỗi thay vì dừng sạch; timeout khi ghi token chưa được `_nhan_token` bắt. | **Đã sửa Task 4:** bắt lỗi YAML và lỗi tiến trình/I/O, trả câu hằng; không chép stdout/stderr/ngoại lệ chứa dữ liệu con. Test lỗi ghi token dùng dữ liệu giả và xác nhận không lộ ra stderr. |
| **Vừa** | Plan chưa có RED→GREEN thật; fixture Task 7 thiếu trường nên có thể đỏ bằng AttributeError; test cũ vẫn đòi công bố mốc ở B; hai đường test hồi quy không tồn tại. | **Đã sửa:** fixture đầy đủ, thêm bài hàng đợi + Git thật chốt SHA; giữ test mốc từ xa riêng, cập nhật kỳ vọng commit B; sửa tên test. Áp/chạy bản vá trong bản sao tạm, ghi kết quả thật vào plan. |
| **Nhỏ** | Thêm callback lọc bead vào `BoGiaoViec` là thừa sau QĐ5-B; helper `gan_commit` chỉ chuyển tiếp một chỗ; nhiều đoạn hướng dẫn lặp lại. | **Đã gọn:** bỏ toàn bộ bản vá `bo.py`, dùng nguồn `cac_du_an` chung cho tick/chọn/cấp, gộp helper chốt SHA, rút bớt văn bản lặp. |

## Kiểm chứng

Tất cả chạy trên bản sao tạm; `tram/`, `tests/`, `frontend/`, công cụ và cấu hình của worktree hiện tại không đổi.
Không gọi Claude, Keychain, sudo, launchd thật; không mạng/tải gói; không commit, bd, push, merge.

- **9 task / 33 khối Create–Modify:** áp tuần tự bằng `git apply --check` rồi `git apply` trên bản sao HEAD;
  AST Python hợp lệ, nội dung đúng bằng bản đã chạy. Import/chữ ký thực được kiểm bằng test, không chỉ đọc tên.
- **Hồi quy cuối: 174 passed, 5 deselected** qua `tests/chan_host/chay.sh -q` trên 30 file;
  gồm test mới, cài/đăng ký, API, báo cáo, hạn mức/ngân sách/cầu dao, trần dòng và vòng import.
- **C1/C2: 2 failed có chủ đích** trong phép kiểm review riêng; không phải lỗi sandbox.
  C1 so tập entry cấp/thu thấy không khớp; C2 chuẩn bị phiếu ben-station rồi kiểm dependency worktree.
- **5 test tiến trình:** chạy riêng trên HEAD chưa sửa, **5 failed**, cùng nhóm lỗi thu hồi như sau áp plan.
  Gọi `tram.kiem.bang_tien_trinh.chup_nhan()` riêng trả `PermissionError [Errno 1] sysctl: không đọc được kích thước bảng`.
  Không tính các lỗi này vào verdict, không sửa test/timeout để giả xanh. Test localhost nếu bị sandbox chặn cũng
  phải phân loại tương tự; phiên này không dùng kết quả bind localhost để suy ra lỗi plan.
- Baseline toàn suite đã chạy nhưng dừng sau **175 passed, 38 failed** do nhóm kiểm tiến trình không chạy được;
  **không có N₀ toàn suite, không tuyên bố toàn suite xanh**.
- Mọi lượt có **0 dòng chặn mới**. Nhóm hồi quy cuối báo **5 điểm mù Python con** của fixture cũ;
  không coi runner là sandbox tuyệt đối. Các Git push trong fixture được runner giả lập, không push thật.
- `DO_NOT_TRACK=1 OPENSPEC_TELEMETRY=0 openspec validate doi-ngu-tho --strict` → **valid**.
  Binary có sẵn là **1.11.0**; repo pin 1.14.0. Không tải/cài bản khác để vượt lệnh cấm mạng.
- `git diff --check` và kiểm phạm vi cuối: chỉ plan, change và báo cáo này.

Log và mã rehearsal cục bộ: `/private/tmp/review-doi-ngu-dr9r1_qn/`.
`logs/final-focused-v2.txt`, `logs/baseline-process.txt`, `logs/blockers.txt` giữ số đo;
`rehearsal/tests/test_review_doi_blockers.py` giữ hai phép kiểm còn đỏ.

## Còn mở trước khi code

C1 và C2 cần bổ sung mã/test nguyên văn, chạy RED→GREEN và review lại. Đây là thiếu sót cài đặt,
không phải yêu cầu Đại ca chốt lại QĐ1–QĐ5. Những cổng S2/S3/S4/S6/S7/S8 máy thật vẫn giữ sau code/QC/ghép;
review này không cấp phép chạy sổ tay, mở giao, gỡ estop, merge hay deploy.

**CHƯA ĐẠT để code — còn C1 (vòng đời quyền) và C2 (dependency worktree); không tính lỗi sandbox.**
