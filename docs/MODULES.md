# MODULES — bản đồ package, tích hợp ngoài, bộ test

Project: `ben-station`
Status: `ACTIVE`
Cập nhật: `2026-10-20`

## Mục đích và sở hữu
Tầng 2 — đọc khi task chạm package, tích hợp ngoài hay bộ test. Tách từ `ARCHITECTURE.md` để giữ Tầng 1 trong ngân sách.
Sở hữu: package nào giữ gì, vòng import, tích hợp ngoài, bộ test. Không sở hữu: tầng, hợp đồng chung, luồng, ràng buộc (`ARCHITECTURE.md`).

## Vòng import
- Nguồn sự thật danh sách package: `ls tram/`. Không có registry, không có test cưỡng chế ranh giới package.
  `tests/test_vong_import.py` chặn vòng import ở cấp **module** (import chạy lúc nạp) và `__init__.py` có import.
- **Có vòng import ở cấp package**, ví dụ `cau_hinh ↔ giao_viec`, `giao_viec ↔ tho`, `api ↔ chu`,
  `cham_cot ↔ nho`, `chay_cli ↔ phieu`. Chạy được vì mỗi file import đúng module con nó cần (không qua
  `__init__`), và một số chỗ **import trễ trong hàm**: `tram/cli*.py`, `chu → phieu`, `nho → api, llm`,
  `bao_tin → cau_hinh, su_kien`, `thao_tac → cau_hinh`.
- Thêm import xuyên package: import module con cụ thể; nếu tạo vòng ở cấp module thì import trễ trong hàm
  và ghi lý do (suy từ code, chưa xác nhận).

## Bản đồ module
| Package | Sở hữu |
| --- | --- |
| `tram/su_kien/` | kho sự kiện, ghi thêm, sao lưu (`ban_sao.py`); phiên bản cấu trúc (`phien_ban.py`); mở kho theo chuỗi cha được tin (`mo_an_toan.py`, `thu_muc_an_toan.py`); hợp đồng ở `ARCHITECTURE.md`, quyền ở `ENGINEERING_STANDARDS.md` |
| `tram/cau_hinh/` | đọc `~/.tram/cau-hinh.yaml`, `du-an/*.yaml`; khoá `cach_ly`, `giao_viec`, `cong_bo`, `usage`, `bat_ghi` |
| `tram/beads/` | gọi `bd` của dự án con (đọc, ghi nhãn), mô hình bead; `bd` của đề nghị agent — actor `tram/de-nghi`, mô tả qua stdin, liên kết `discovered-from`, mọi lệnh qua `chay_gioi_han` (`bd_de_nghi.py`) |
| `tram/cham_cot/` | chấm cột: luật cứng trước, Claude API sau, ghi `cot:*` |
| `tram/llm/` | client Anthropic (khoá lấy từ Keychain); hạn chờ mỗi lời gọi, trần lời gọi còn sống (`han_goi.py`) |
| `tram/du_an/` | `tram du-an them`: thêm dự án ở chế độ chỉ đọc |
| `tram/phieu/` | kho phiếu: khe, máy thợ, lượt, giữ ngân sách, cầu dao hạn mức, mã ghép (`ma_ghep.py`: tác nhân mặc định `tram/api`; CLI cấp mã cũ đóng theo D155) |
| `tram/passkey/` | verifier WebAuthn, kho quyền riêng `passkey.db` (v1 chưa phát hành), ceremony/phiên, ràng buộc mã/nội dung, quản lý thiết bị và kết quả retry nguyên tử, outbox an ninh |
| `tram/han_muc/` | đọc hạn mức CLI, ngưỡng ngừng |
| `tram/usage/` | đếm usage (ccusage tuỳ chọn) |
| `tram/giao_viec/` | vòng tick (ba pha, ba luồng: nhanh, Git, deploy), tự merge có điều kiện (`tu_merge.py`, `tu_merge_rao.py`, `tu_merge_gui.py`, `gh_tu_merge.py`), pipeline theo loại bead, chọn khe, kiểm lại, QC, luồng feature, PR, xác minh merge; harness S6 (chứng cứ từng nguồn lịch `chung_cu_probe.py`), ống `git archive \| tar` có chủ hai đầu, đóng ống nguồn cả khi ngắt trước khi trả handle (`ong_chep.py`); escalation quét lý do gốc qua `nho.bi_mat.quet` trước chuẩn hoá/cắt và ghi mới/gộp |
| `tram/tho/` | quản lý thợ: đăng ký B (`dang_ky_b.py`), nhịp tim, CLI/principal, bàn giao; B có cây/cổng riêng mỗi lượt (`luot_b.py`), ACL (`quyen_cay_b.py`), bundle offline (`deps_b.py`), quản lý chốt SHA (`chot_bao_b.py`); dọn UID (`don_uid.py`), thăm dò (`cham_tham_do.py`), giữ `sudo -n` |
| `tram/chay_cli/` | dựng lệnh `claude -p` / `codex`, đọc stream, quyền theo vai |
| `tram/kiem/` | chạy lệnh có giới hạn, cây tiến trình, danh tính UID, vòng đời tiến trình, đường cấm; hợp đồng sở hữu tiến trình con (`so_huu.py`), hoãn ngắt (`ngat.py`), bảng tiến trình của nhân (`bang_tien_trinh.py`), giữ xác gốc (`giu_xac.py`), gửi tín hiệu nhóm (`gui_tin.py`) |
| `tram/cong_bo/` | công bố nhánh `tram/<bead>`, đối soát push |
| `tram/ban_giao/` | schema và đọc file bàn giao của agent |
| `tram/nho/` | memory service + MCP (cổng 7710): tách/gộp ký ức, embed, quét bí mật, thăng cấp, phạm vi |
| `tram/yeu_cau/` | sổ tiếp nhận phiếu yêu cầu feature từ máy A |
| `tram/thao_tac/` | thao tác ghi từ dashboard: chốt, duyệt spec, kéo cột, estop, khe, cài đặt tự động và TẠM DỪNG (`tu_dong.py`), nút Deploy (`deploy.py`), nút agent tự cập nhật việc (`tu_cap_nhat.py`); `chay.py` kiểm quyền trước bước mới/thử lại chưa hoàn thành, sau nhánh trả kết quả đã lưu |
| `tram/de_nghi/` | agent tự cập nhật việc: lọc nội dung (`loc.py`), nút theo dự án (`cai_dat.py`), nhận (`nhan.py`), cổng việc mới (`cong.py`), ghi Beads trong `vong_nhanh` có cửa kiểm tươi sát mỗi lệnh `bd` và ngân sách mỗi nhịp (`cua.py`, `cho.py`, `ghi.py`, `vong.py`), lý do bị chặn (`bi_chan.py`), hướng dẫn lớp 2 (`huong_dan.py`) |
| `tram/tu_dong/` | tự merge / tự deploy: cài đặt theo dự án lưu bằng sự kiện (`luu.py`), kiểm lệnh (`cai_dat.py`), khoá chung trước thao tác tự động (`khoa.py`), đường cấm từ ba lệnh (`file_cam.py`) |
| `tram/deploy/` | tự deploy (pha `vong_deploy`): trạng thái tính từ sự kiện (`trang_thai.py`, `hien_thi.py`), chạy một lệnh có hạn + log đã che bí mật (`lenh.py`, `ong.py`), Git có hạn (`git.py`), chuỗi deploy → kiểm còn sống → lùi (`chuoi.py`), ghi `deploy.*` (`ghi.py`), một vòng của một dự án (`vong.py`, `chay.py`), đường cấm từ ba lệnh nối vào kiểm đường cấm (`cam.py`) |
| `tram/suy/` | tính trạng thái hiển thị từ sự kiện + beads |
| `tram/api/` | tram-api: router, bảo mật, kênh ghi, API thợ, ghép máy, nội bộ, điều phối; `passkey*`: cửa người N/P/R, giới hạn body trước parse, adapter TM/TC so cấu hình để chọn P/R dưới khoá ledger |
| `tram/chu/` | lệnh trạm chủ: cài từng dịch vụ launchd kèm biên nhận, gỡ theo biên nhận (`go_dich_vu.py`, `chung_cu_go.py`), khôi phục kho sự kiện (`khoi_phuc_su_kien.py`), siết quyền `~/.tram` (`siet_quyen.py`), estop, `passkey.py` bootstrap/khôi phục TTY, CLI ghép cũ trả 2, kiểm cách ly, trạng thái |
| `tram/bao_tin/` | vòng báo tin Telegram, chống ồn, giờ yên lặng theo loại tin; nguồn tin tự merge / tự deploy (`nguon_tu_dong.py`), việc mới do agent tạo (`nguon_de_nghi.py`), outbox passkey (`passkey.py`) giữ đủ ID qua giờ yên lặng |
| `tram/keychain.py` | đọc mục Keychain có hạn (module ở gốc gói) |

## Tích hợp ngoài
Cột "Hỏng thì" suy từ code, chưa xác nhận.

| Hệ ngoài | Dùng để | Timeout | Hỏng thì |
| --- | --- | --- | --- |
| `bd` (Beads) | đọc/ghi việc của dự án con | 120 giây; `bd` của đề nghị agent 30 giây qua `chay_gioi_han` (thu hồi cả nhóm tiến trình), ngân sách nhận thêm 20 giây, dự phòng một ghi sau đọc chậm; chờ lệnh TC ≤ 80 giây/nhịp + xử lý cục bộ/thu hồi | API trả 502; vòng quét ghi lỗi; đề nghị: `de_nghi.loi_ghi` (chỉ mã lỗi), nhịp sau thử lại, đối soát dấu mã nên không ghi trùng |
| `git`, `gh` | worktree, công bố, mở/xem PR; `gh pr merge --merge --match-head-commit` chỉ khi dự án bật tự merge | theo lệnh; `gh` 60 giây | bead ở lại cột 3, sự kiện lỗi; tự merge lỗi 3 lần → `tu_merge.loi`, tin "trạm lỗi" |
| `claude -p`, `codex` | agent thợ chạy việc | trần của phiếu | thu hồi phiếu, giao lại |
| Anthropic API | chấm cột, tách/gộp ký ức | chờ tối đa 120 giây/lời gọi, kể cả đợi chỗ; SDK không retry (`tram/llm/han_goi.py`) | quá hạn: bỏ chờ, không huỷ luồng; tối đa 2 luồng sống/tiến trình; hết chỗ: chờ tới hạn rồi lỗi, không mở lời gọi mới |
| Ollama bge-m3 | embed ký ức (chỉ localhost) | 30 giây | memory báo lỗi, không lùi về vector giả |
| Telegram | báo tin ngắn | 10 giây | mất tin, vòng sau gửi lại |
| WebAuthn | passkey người dùng, không dùng token máy | challenge/UV 120 giây, phiên tuyệt đối 8 giờ, mã 10 phút; HTTP nhận thân 5 giây ở cửa N/P/R, ceremony client 15 giây/lời gọi | giữ đóng ghi, báo thử lại/thiết bị khác; không log ceremony/cookie/mã; ledger nghiệp vụ giữ kết quả TM/TC |
| Tailscale | danh tính Đại ca, nối A–B | — | ghi bị 403 |
| `ccusage` | đếm usage (tuỳ chọn) | 60 giây | trang Usage báo chưa biết |
| `security` (Keychain) | lấy khoá | 10 giây (`tram/keychain.py`) | đọc lỗi hay quá hạn: coi như chưa có khoá, dịch vụ báo thiếu token; kiểm tồn tại lỗi: dừng, không tạo khoá thay |
| `sudo -u`, `sandbox-exec` | chạy dưới principal, cách ly | theo `tram/kiem/` | cổng đóng |
| Ba lệnh deploy / kiểm còn sống / lùi của dự án | tự deploy (`tram/deploy/`), dưới tài khoản trạm, không qua shell | 15 / 2 / 15 phút (`tram/deploy/lenh.py` `HAN`), quá hạn giết cả nhóm tiến trình | hỏng: tự lùi, tin "đã tự lùi"; 3 lần liên tiếp: tự tắt tự deploy; lùi hỏng: tắt + tạm dừng dự án, tin khẩn; không rõ kết quả: tạm dừng dự án, không chạy lại; đầu ra chỉ ở `~/.tram/deploy-log/` (0600, đã che bí mật, giữ 30 ngày) |
| `launchctl` | cài/gỡ dịch vụ trạm chủ, cài thợ | 30 giây mỗi lệnh (`tram/chu/dich_vu_tram.py`, `cai_dat_tho.py` kể cả callback tài nguyên) | dừng, lệnh sau không chạy, thoát 3 |
| `brew`, `ollama pull` | cài memory | install 30 phút, services 60 giây, pull 60 phút (`tram/chu/cai_dat_nho.py`) | quá hạn: dừng kế hoạch, thoát 3; đối soát cây con ở cổng |

## Kiểm thử
- **pytest** (`tests/`): mỗi test có `TRAM_HOME` tạm, chạy ngoài `tests/chan_host/chay.sh` thì thoát 4 (`tests/conftest.py`, D61); hệ ngoài thay bằng bản giả
  `tests/*_gia.py`. Không bộ nào chạm macOS thật — cách ly, launchd, Keychain chỉ chứng minh qua cổng sổ tay.
- **Frontend:** `frontend/tests/*.test.mjs` (logic), `frontend/kiem-an-toan.mjs` (quét nguồn),
  `frontend/kiem-dist.mjs` (quét bundle cho CSP).
- **Giao diện tự động (TM-4):** `frontend/src/trang/TuDong.vue`, luật `luat_*tu_dong.js`, khối
  `frontend/src/thanh/tu_dong/`; `ghi_tu_dong.js` dùng chung cho Deploy ở trang Tự động và Phê duyệt.
  Dữ liệu kiểm tay: `tests/test_du_lieu_giao_dien_tu_dong.py`; cờ `--gia-deploy` chỉ dùng để xem dữ liệu giả.
- **Kiểm tay giao diện:** `tests/chay_thu_giao_dien.py` chạy tram-api thật với dữ liệu giả, CSP thật.
- Chạy cả bộ qua `tests/chan_host/chay.sh -q` (bộ chặn host); lệnh và cách chạy an toàn: `AGENT_RULES.md` §13.
- Test canh giữ cấu trúc: `tests/test_vong_import.py` (vòng import cấp module), `tests/test_do_dai_ma.py` (file và
  dòng của `tram/`: giới hạn và ngoại lệ ở `ENGINEERING_STANDARDS.md` mục Kiểu code).

Hồi quy V5: `tests/test_v5_contract_4.py`, `tests/test_v5_contract_5.py`, `tests/test_v5_contract_6.py` kiểm hợp đồng
join/principal/stdin; `tests/test_v5_sqlite_unlink.py` dùng SQLite thật; `tests/test_v5_cap_ma.py` kiểm tác nhân
sự kiện mặc định API và CLI đã đóng (D155); `tests/test_v5_sudo_khong_tuong_tac.py` kiểm lỗi sudo bằng bộ chạy giả. Test Ctrl-C đồng bộ ở
`tests/test_ban_chep_pipeline_han.py` kiểm sở hữu và đóng ống; bằng chứng OS vẫn cần cổng chạy thật.

Passkey: `tests/test_passkey*.py` dùng chữ ký thật với authenticator giả; `test_passkey_tm_tc.py` kiểm N/P/R,
ràng buộc toàn thân, retry/lỗi/race cùng ledger TM/TC thật. Frontend `passkey*.test.mjs` kiểm bridge, snapshot,
Vue SSR/runtime và retry UUID/quyền trong RAM; browser/CSP/focus và xác minh OS vẫn cần cổng riêng.
