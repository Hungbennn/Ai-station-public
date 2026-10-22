# Kết quả thực hiện đội ngũ thợ — 20/10/2026

Nhánh `code/doi-ngu-tho`, HEAD nền `e0ae24b`. Đã áp Task 1→9 theo thứ tự,
QĐ1–QĐ4=A, QĐ5=B; vòng 3 thắng phần thân. Chưa commit, ghép hay chạy thật.

**DỪNG trước kết luận đạt:** có một bất khớp thật giữa Task 6 và test tích hợp hiện hành,
đã đối chứng HEAD sạch; không phải sandbox. Mã đã áp đủ nhưng nghiệm thu chưa xong.

## Điểm dừng cần review lại

`tests/test_kich_ban_3a2.py::test_thieu_moi_truong_kiem_bao_bi_khong_chay_cli`:

- HEAD sạch: **4 passed** (gồm ba test trần dòng), 0 dòng chặn mới.
- Bản vá: **1 failed, 3 passed**, 0 dòng chặn mới; `IndexError` vì không có sự kiện `bao.bi`.
- Nguyên nhân: `chuan_bi()` chuyển B sang `luot_b.chuan_bi_b()`; khi file môi trường thiếu,
  Task 6 bắt lỗi chuẩn bị và ném `LoiThuHoi`, giữ phiếu/cổng đóng. `VongKhe` dừng khe.
  Luồng cũ trả `thieu-moi-truong-kiem` rồi gửi `bao.bi` như test đang đòi hỏi.
- Sửa mã để gửi lại `bao.bi` sẽ đổi thiết kế giữ phiếu của plan; sửa test sẽ đổi kỳ vọng.
  Theo lệnh Đại ca, dừng sửa ở đây, không tự chọn. Đề nghị người review thống nhất lại
  hành vi B khi thiếu môi trường và phạm vi các test tích hợp cũ trước khi tiếp tục.
- Các giả định cũ về mốc công bố/cây worktree trong cùng file cũng cần được rà khi review;
  hiện chưa có phép chạy ngoài sandbox chứng minh chúng đạt. Không tự sửa các assertion đó.

Log: `legacy-prep-baseline.log`, `legacy-prep-current.log` trong thư mục kiểm chứng cuối báo cáo.

## TDD từng task

Các số dưới đây đều là kết quả mới của phiên này, không lấy số từ review.
Mỗi lượt test đều kèm `tests/test_do_dai_ma.py`; số passed bao gồm bộ này.

| Task | RED đã thấy | GREEN đã thấy |
|---|---|---|
| 1 — cài riêng, giữ tắt | 6 failed, 4 passed: còn lệnh nạp; user trùng chưa bị từ chối; callback timeout=None | 39 passed, gồm sổ cài/gỡ/phần kiểm |
| 2 — đăng ký B | 4 failed, 4 passed: không từ chối HTTP/token sai, chưa ghi cấu hình/sao lưu | 14 passed, gồm API retry/403, khe vẫn tắt và lỗi replace sau POST |
| 3 — phạm vi kiểm | 1 failed, 3 passed: danh sách còn hr-codex | 19 passed, gồm các bài kiểm máy/cách ly cũ |
| 4 — auth nền | 6 failed, 3 passed: chưa sẵn sàng; exit 0/JSON false bị tin; YAML/timeout thoát CLI | 26 passed, 1 failed trong hồi quy rộng; sáu test mới đều xanh trong nhóm 145 cuối |
| 5 — báo không Git | 1 failed, 3 passed: AssertionError “Khe không được chạy Git để báo” | 23 passed, gồm báo cáo/hàng đợi cũ |
| 6 — quyền/vòng đời/deps | 21 failed, 4 passed; có 20 lỗi hành vi và 1 TypeError phụ do đường dọn cũ | 25 passed trọng tâm; hồi quy rộng 81 passed, 2 failed ở thu hồi CLI; **chưa đạt nghiệm thu** do test thiếu môi trường nêu trên |
| 7 — quản lý chốt SHA | 3 failed, 3 passed: còn SHA giả, mốc gọi công bố, chưa commit cây thật | 6 passed trọng tâm; hồi quy vòng thợ 11 passed, 3 failed ở thu hồi; còn fixture thiếu tren_may_b trong toàn suite |
| 8 — lọc dự án | 7 failed, 3 passed: dữ liệu sai không bị chặn, HR còn trong nguồn; lần RED hành vi bổ sung có thêm 1 lỗi trần dòng của scaffold | 47 passed, gồm ngân sách/cầu dao/nhịp hạn mức |
| 9 — công cụ | 10 failed, 3 passed trên stub (runtime chưa tồn tại); riêng sửa vòng 3 có 3 failed, 3 passed, 7 deselected: YAML bị đổi/URI sai TRAM_HOME | 13 passed |

Module mới dùng stub tối thiểu/chữ ký trước khi đo RED, rồi thay bằng mã nguyên văn plan.
Không dùng lỗi import làm bằng chứng hành vi. Riêng RED Task 4 dùng plugin tạm giả
`doc_token_may` để mã cũ không gọi Keychain; plugin không dùng trong GREEN hay lưu vào repo.
TypeError phụ Task 6 và lỗi trần dòng scaffold Task 8 không tính là bằng chứng hành vi;
mã cuối cùng và toàn bộ test nguyên văn không chứa scaffold/plugin này.

## Kiểm chứng tích hợp

- `tests/test_doi_ngu*.py tests/test_phu_thuoc*.py tests/test_do_dai_ma.py tests/test_vong_import.py`:
  **145 passed**, 0 dòng chặn mới, 11 điểm mù Python con, 26 push giả lập.
- Hồi quy 21 file cài/đăng ký/API/kiểm máy/báo cáo/giao/ngân sách/hạn mức/UID/cấu trúc:
  **149 passed**, 0 dòng chặn mới, 0 điểm mù, 16 push giả lập.
- Nhóm Task 6 rộng: **81 passed, 2 failed**; nhóm Task 7 rộng: **11 passed, 3 failed**.
  Năm lỗi thu hồi này được đối chứng trên bản sao HEAD sạch, xem mục sandbox bên dưới.
- Toàn suite: **2108 passed, 144 failed, 1 warning**, kết thúc bằng `KeyboardInterrupt`
  sau 27 phút 32 giây; thu thập 4664 test nhưng chưa chạy hết. Runner thoát 2,
  **0 dòng chặn mới**, 33 điểm mù Python con, 404 push giả lập.
  Sau điểm dừng thật đã yêu cầu ngắt lượt kiểm; SIGINT trực tiếp tới đúng PID pytest của phiên
  bị sandbox từ chối, rồi gửi Ctrl-C qua session. Session hiện đã kết thúc, không còn chờ runner.
  Không coi đây là toàn suite xanh; không nới timeout hay sửa code để né lỗi.
- QC dựng lại mã từ `git archive HEAD`, áp tuần tự mọi Create/Modify bằng
  `git apply --check` rồi áp: **51 tệp khớp từng byte** với cây hiện tại.
- `git diff --check` đạt. Bốn công cụ biên dịch đạt; `.pyc` chỉ ghi trong tmp.
  Liên kết tài liệu đã sửa tồn tại. Trần dòng và vòng import đạt trong nhóm 145.

Lệnh test dùng đúng runner và venv được chỉ định:

```bash
UV_CACHE_DIR=/private/tmp/codex-doi-ngu-20261020/uv-cache \
PYTHONPATH="$PWD" UV_PROJECT_ENVIRONMENT='/Users/dai-ca/Developer/Ben Station/.venv' \
UV_NO_SYNC=1 tests/chan_host/chay.sh -q <files> tests/test_do_dai_ma.py
```

Lần đầu uv lỗi mở cache trong nhà người dùng; đổi riêng cache sang tmp, không sync/tải gói.
Không chạm frontend nên không chạy các lệnh npm. Không thêm dependency hoặc sửa lockfile.

## Chỗ lệch plan

- **51 tệp nguyên văn plan vẫn khớp từng byte**; không sửa hunk, thiết kế hoặc kỳ vọng test.
- Lệch nhỏ Task 1: `tests/test_chu_tho.py` còn fixture `SimpleNamespace` thiếu `chi_tho`/`giu_tat`.
  RED mới **1 failed, 14 passed** (`AttributeError: chi_tho`); thêm đúng hai cờ False như
  fixture Task 1, giữ nguyên assertion; GREEN **15 passed**. Không cần sửa mã sản phẩm.
  Toàn suite được thu thập trước sửa fixture này; nếu còn ghi lỗi cũ thì dùng lượt GREEN này đối chiếu.
- Plan yêu cầu cập nhật ADR/tài liệu sở hữu nhưng không cho nguyên văn: thêm ADR-0009 (30 dòng),
  cập nhật ngoại lệ QĐ2-A và quản lý chốt Git QĐ3-A trong PRODUCT_ARCHITECTURE/ARCHITECTURE/ADR-0007,
  cập nhật bản đồ module và timeout cài thợ trong MODULES. Không tạo quyết định mới.
- Những scaffold RED tạm, plugin giả Keychain và bản dựng QC chỉ phục vụ kiểm chứng như mô tả trên.
  Không sửa `docs/CURRENT_STATE.md`, không tạo/sửa `docs/handovers/`, không sửa plan/change.

## Test đỏ nghi do sandbox

- Baseline rộng dừng với `--maxfail=40`: **175 passed, 40 failed**, 0 dòng chặn mới;
  chủ yếu nhóm bản chép/thu hồi tiến trình. Không có N₀ toàn suite hợp lệ.
- Đo trực tiếp `tram.kiem.bang_tien_trinh.chup_nhan()` bằng Python có sẵn:
  `PermissionError [Errno 1] sysctl: không đọc được kích thước bảng`.
- Đối chứng trên bản sao HEAD sạch (`baseline-src/`): **9 failed, 8 passed**.
  Đỏ cùng cả năm ca thu hồi liên quan và bốn ca `test_deploy_lenh.py`; 0 dòng chặn mới, 2 điểm mù.
  Đây là đối chứng lỗi có sẵn trong cùng sandbox, không phải bằng chứng máy thật đạt.
- Bind `127.0.0.1` vào cổng tự chọn trả `PermissionError [Errno 1] Operation not permitted`.
  Vì thế chưa mở được Đội ngũ dưới CSP thật trên trình duyệt; không coi kiểm API giả là kiểm UI.
- Toàn suite còn 10 lỗi fixture thiếu `tren_may_b` và bất khớp thật của test thiếu môi trường,
  tách khỏi nhóm nghi sandbox. Fixture `chi_tho` được thu thập trước sửa nên còn hiện trong 144 lỗi.
- Không sửa mã/test/timeout để né sandbox. Helper `-I` không nạp audithook được ghi là điểm mù,
  không coi 0 dòng chặn là sandbox tuyệt đối. Push của fixture chỉ do runner giả lập.

## Việc còn lại

- **Chốt lại bất khớp Task 6/test tích hợp trước khi tiếp tục; chưa thể kết luận plan đạt.**
- Bổ sung fixture cũ thiếu `tren_may_b` sau review: 1 ca trong `tests/test_de_nghi_tho.py`
  và 9 ca trong `tests/test_deploy_review_v2.py` đỏ `AttributeError` do Task 7 đọc cờ mới.
  Chưa sửa vì đã gặp điểm dừng lớn; không gọi các lỗi fixture này là sandbox.
- Chạy lại đầy đủ sau sửa/review và ngoài sandbox; chưa có kết luận cho 2412 test chưa chạy.
  144 lỗi gồm cả fixture `chi_tho` đã sửa bằng lượt 15 passed riêng; không coi toàn bộ 144 lỗi là môi trường.
  Những nhóm chưa đối chứng (như kịch bản 4a1/4a2/đề nghị, G3, API/socket) cần phân loại tiếp.
- QC độc lập trước ghép; tự kiểm trong phiên này không thay QC của người điều phối.
- Đo UI/CSP, Keychain/CLI nền sau reboot, ACL/file UID khe, S2/S3/S4/S6/S7/S8 và chuỗi R7
  chỉ sau code/QC/ghép và kịch bản được Đại ca cho phép. Không archive hoặc mở giao bằng test offline.
- Đã giữ nguyên mọi công tắc, cấu hình dự án và máy thật. Không gọi `bd`, commit, push, sudo,
  launchctl ghi, GitHub/deploy thật; không chạy sổ tay `doi_ngu_b.py` thật.

Log/mã kiểm chứng: `/private/tmp/codex-doi-ngu-20261020/`.
`task-*-red.log`, `task-*-green.log`, `task-9-v3-red.log`, `final-focused.log`,
`final-regression.log`, `full-final.log`, `baseline-control.log`, `qc-plan.log`,
`fixture-old-red.log`, `fixture-old-green.log`, `legacy-prep-baseline.log`, `legacy-prep-current.log`.
