# Review độc lập plan — 21/10/2026

**Nền:** `51ec56f0e063b3d4cc3bad6119e7bc4c235cd479`, nhánh `spec/giao-viec-theo-co`.
Đối chiếu QĐ1–3,5=A, QĐ4=C, S1–S11 và mã thật đã có đội ngũ thợ.
Review này thay kết luận sẵn sàng của `KET-QUA-PLAN.md`; không đổi các QĐ hay spec đã duyệt.
Mọi mã thử chỉ ở bản sao tạm; worktree chỉ sửa plan/change/báo cáo.

## Phát hiện, từ nặng đến nhẹ

### 1. Nặng — nhận plan/review bỏ qua đường cấm (đã sửa)

Task 11 cũ thêm nhánh sớm trong `xu_ly_viec._xet`, gọi `xet_plan` trước
`cam_tu_lenh` và kiểm đường cấm vốn có trong `xet_xong_spec`. Chỉ giới hạn
`docs/plans/<bead>`/`docs/handovers/` không đủ: dự án có thể cấm chính đường đó.
Test thực với Git và kho phiếu giả: cấm `docs/handovers/cam.md`, plan cũ vẫn nhận, trả `None`.

Task 5 mới kiểm `diff_cham_cam` với đường cấm dự án, đường bắt buộc từ lệnh và
ngoại lệ hiện hành trước nhận plan; chạm cấm trả `dong-file-cau-hinh` và escalation.
Không sửa cơ chế kiểm danh tính/cách ly hay định nghĩa đường cấm.
Hồi quy: `test_plan_phai_giu_duong_cam_du_an`.

### 2. Nặng — cỡ tự mở quyền chạy lệnh cho spike tài liệu (đã sửa)

Task 5/8 cũ gán lại `lenh_cho_phep` bằng toàn bộ danh sách dự án dù đề xuất gốc
cho spike tài liệu có danh sách rỗng. Nhãn/cỡ không được trở thành nguồn cấp quyền.
Test cũ trả phiếu thay vì chờ, có thể claim.

Task 5 mới giữ `dx.lenh_cho_phep`; không đủ quyền cho lệnh bắt buộc thì chưa cấp,
không claim. Không bỏ kiểm bắt buộc hay mở quyền để làm test xanh.
Hồi quy: `test_co_khong_tu_noi_lenh_cho_spike_tai_lieu`.

### 3. Nặng — plan/nhận xét được nối thẳng vào prompt (đã sửa)

Task 5/13 cũ chỉ thêm chữ “dữ liệu, không cấp quyền”, rồi nối blob thẳng vào gói.
Không dùng cơ chế `boc_khong_tin_cay` đang bảo vệ dữ liệu trong `goi.py`.
Nội dung thêm cũng có thể vượt trần gói 150.000 ký tự hiện có, dù schema phiếu cho 400.000.

Task 4–5 mới dùng bộ bọc hiện có cho cả plan và nhận xét, giữ trần gói cũ sau ghép.
Hồi quy: `test_plan_khong_noi_thang_du_lieu_vao_prompt`.

### 4. Nặng — S9 giữ chờ nhưng không tới được plan (đã sửa)

Sau code xong, pipeline ở `kiem_lai`. `chan_buoc` thấy cần plan thì dừng, nhưng
`liet_ke` chỉ đưa ứng viên `code/qc` vào bộ chọn. Dấu `co.can-code-lai` lại chỉ ghi
sau khi plan đã đạt: hai bên chờ nhau. Test cũ Task 10 chỉ gọi hàm thuần nên không thấy.

Task 5 mới: sau xác nhận phạm vi, nếu cỡ tăng thì ghi dấu cần code lại ngay cả khi
đang chờ plan. Pipeline quay về ứng viên code; `gan_co` vẫn chặn code và phát plan/review
trước, giữ tất cả cổng. Test dùng Git/sự kiện thật trong bản giả, gọi cả `chan_buoc`
và `BoGiaoViec.chon`, chứng minh nhận được phiếu plan.
Hồi quy: `test_s9_sau_code_nang_co_phai_den_duoc_plan`.

### 5. Cao — phiếu spec nhưng prompt vẫn là coder, tiêu chí không khớp (đã sửa)

Task 11 cũ đổi `buoc/vai/tieu_chi` trên JSON nhưng dùng lại gói coder/QC nguyên vẹn.
Gói còn yêu cầu chép tiêu chí code cũ, trong khi bộ nhận so tiêu chí plan mới:
agent theo đúng gói có thể bị từ chối bàn giao hoặc làm nhầm bước.

Task 4 mới dựng gói bằng `DauVaoGoi`/`dung_goi`, vai spec và đúng tiêu chí của phiếu;
giữ tài liệu dự án, dữ liệu bead được bọc, lệnh rỗng.
Hồi quy: `test_phieu_plan_khong_mang_vai_coder_va_tieu_chi_cu`.

### 6. Vừa — ép code lại chỉ vì đổi ngưỡng (đã cắt)

Task 10 cũ coi mọi thay đổi `ban_luat` là lý do code lại, kể cả cỡ/model/quy trình không đổi.
S11 đòi luật mới áp lượt sau và giữ lịch sử, không đòi chạy lại code chỉ vì hash khác.
Task 5 mới chỉ dùng tăng cỡ làm điều kiện này; vẫn chấm lại và giữ cổng plan theo luật hiện tại.
Đã sửa cả test cũ vốn đòi hành vi thừa.
Hồi quy: `test_doi_nguong_khong_bat_code_lai_luot_da_xong`.

### 7. Vừa — luật chồng nhau và vi phạm “thêm một, bỏ một” (đã sửa)

Task 5 cũ chép cùng 15 dòng vào bốn tài liệu, không sửa các câu bắt mọi việc
có plan nguyên văn/review/cả bộ test. AGENT_RULES thêm một mục mà không bỏ luật.

Task 6 mới thay câu tại §3/§13; AGENT_RULES vẫn **200 dòng, 20 heading cấp 2** như HEAD.
PLAYBOOK sở hữu bảng theo cỡ, sửa phạm vi review/giao việc/QC; ENGINEERING_STANDARDS
và OPENSPEC chỉ sửa câu tương ứng và dẫn nguồn. Không đổi merge, danh tính, kill list,
cổng thảo luận, ngân sách hay cả bộ test sau ghép. Không thêm phụ lục luật mới.

### 8. Nhẹ — plan là lịch sử vá nối tiếp, trạng thái change cũ (đã sửa)

Task 6–14 sửa nhiều chi tiết vừa dựng ở Task 1–5, có cả CLI ghi plan/review thủ công
sau đó mới xoá. Đã viết lại từng file một lần ở trạng thái cuối và nối lại mốc nghiệm thu.
Proposal/design/tasks còn “chưa có plan”; đã cập nhật, không tick nghiệm thu triển khai.

## Cắt gọn

| Hạng mục | Trước | Sau |
| --- | ---: | ---: |
| Task | 14 | 6 |
| File triển khai | 52 | 42 |
| File test mới | 14 | 5 |
| Khối diff | 31 | 11 |
| Dòng plan | 3.205 | 2.385 |

- Task 9 → Task 5; Task 10 → Task 5, bỏ nhánh code lại chỉ do hash luật.
- Task 11–13 → Task 3–5: chỉ giữ phiên bản cuối của duyệt/plan/review, không xây CLI rồi xoá.
- Task 14 → Task 1. Test dữ liệu/model/tương thích ở Task 6–8 cũ được gộp theo trách nhiệm.
- Bỏ sửa `du-an/ben-station.yaml` chỉ để thêm 57 dòng chú thích; cấu hình hiện hành không đổi.
- Gộp chín file test phụ: `test_co_cong`, `test_co_sau_review`, `test_co_tuong_thich`,
  `test_co_spec`, `test_co_cam_dong`, `test_co_nang_luot`, `test_co_phieu_plan`,
  `test_co_plan_nguon`, `test_co_phu_tro`. Giữ các ca nghiệm thu, thêm sáu hồi quy độc lập.
- 42 file vẫn là thay đổi xuyên nhiều lớp. Không cắt tiếp snapshot/model/gate chỉ để đẹp số:
  các phần đó phục vụ S1–S11. Không thêm abstraction hay bảng DB.

## Kiểm chứng tự chạy

Tất cả tại `/private/tmp/codex-chon-co/review-1/`, dùng `PYTHONPATH` trỏ đúng bản sao,
`UV_PROJECT_ENVIRONMENT='/Users/dai-ca/Developer/Ben Station/.venv'`, `UV_NO_SYNC=1`,
`UV_CACHE_DIR=/private/tmp/codex-chon-co/uv-cache`; chỉ `tests/chan_host/chay.sh`.

- Plan cũ: 31 khối áp sạch trên HEAD; bộ cỡ + trần dòng/import cũ **72 passed**.
  Sáu test review độc lập trên bản cũ: **6 failed**, không phải lỗi sandbox.
- Plan mới: trích lại **11 khối** từ chính Markdown, từng khối `git apply --check` rồi apply
  lên HEAD sạch. **42 file khớp từng byte** cây đã thử; không tự chữa patch khi áp.
- Bản sao cuối từ Markdown sau dọn định dạng: năm file test mới + trần dòng/import
  **72 passed** trong 6,48 giây, nhật ký chặn 0 dòng mới.
- TDD sau gộp Task 1–5: RED thật lần lượt thiếu module `theo_co`, `co_model`,
  `co_plan`, `co_xet_plan`, `co_nguon`; GREEN lũy kế **22, 30, 32, 34, 65 passed**.
  Sáu hồi quy review nằm trong 65 ca này; lỗi cũ không bị xfail/skip.
- Baseline riêng, 18 file liên quan: **147 passed, 4 failed** trong 62,74 giây.
  Cùng 18 file + 5 file test mới: **212 passed, 4 failed** trong 68,33 giây.
  Trần dòng/import nằm trong bộ này. Nhật ký chặn **0 dòng mới**; 7 điểm mù Python con,
  81 push giả lập trên bản cuối, không push thật.
- Bốn lỗi giống baseline: hai ca `test_tho_chuan_bi` (bắt đầu/xong, CLI lỗi/nguồn lùi)
  và hai ca `test_tho_theo_doi_ket_thuc` (xong/công bố, ref bị đẩy ngoài luồng).
  Đều `LoiThuHoi` khi sandbox chặn `ps`; không tính là lỗi feature hoặc ca đạt.
- `DO_NOT_TRACK=1 openspec validate giao-viec-theo-co --strict`: **valid**, CLI sẵn có **1.11.0**.
  Repo ghi pin 1.14.0; không tải thêm. Không tuyên bố đã validate bằng 1.14.0.
- `git diff --check` sạch. Không sửa file `tram/`, test hay bốn tài liệu luật trong worktree:
  thay đổi triển khai của chúng chỉ nằm trong khối diff của plan.

Lệnh bộ 18 file: `test_bo_giao_viec`, `test_bo_giao_viec_spec`, `test_chon_khe`, `test_cap_phieu`,
`test_doc_stream`, `test_cau_hinh_tho`, `test_doi_ngu_dang_ky`, `test_tho_chuan_bi`,
`test_tho_theo_doi_ket_thuc`, `test_pipeline`, `test_noi_giao_viec`, `test_nhip_nguyen_tu`,
`test_phieu_mo_hinh`, `test_cau_hinh`, `test_feature`, `test_tick_feature`,
`test_do_dai_ma`, `test_vong_import` — mỗi tên là `tests/<tên>.py`.
Log: `baseline.log`, `replay-related.log`, `probes-six-red.log`, `stage-*-{red,green}.log`;
manifest `proof.json` trong thư mục tạm trên. Số liệu cần giữ đã ghi tại đây.

## Ranh giới kết luận

Giữ đủ QĐ/S1–S11, không sửa spec để hợp thức hoá lỗi. Không đổi schema DB/cửa danh tính/
principal/quyền vai; không ép model khi phiếu không có `co`, không sửa adapter Codex hay cách chạy máy từ xa.
Kiểm thêm trực tiếp đã xác nhận: `ke_hoach.TIEN_TO_CAM` chặn nhãn `co:` của agent;
kênh đề nghị việc mới hiện có không có trường nhãn. Công tắc và YAML mặc định giữ nguyên.

Không buộc agent tự lập plan khi thiếu tiêu chí để vượt cổng cũ: phải bổ sung đầu vào qua Beads
rồi chấm lại. Đó là giữ cổng R4, không phải lý do nới luật hay tạo đường ghi mới.
Chưa chạy cả suite hoặc model/cách ly thật; vẫn phải kiểm khi triển khai và qua cổng được Đại ca cho phép.

**ĐẠT để code theo plan đã sửa; chưa nghiệm thu triển khai hoặc bật chạy thật.**
