# Lát TM-1 — nền tự merge / tự deploy: cài đặt lưu bằng sự kiện, cửa ghi, TẠM DỪNG, khoá chung, báo tin — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: dùng `ai-skills:subagent-driven-development` (khuyến nghị) hoặc `ai-skills:executing-plans` để làm từng task. Step dùng checkbox (`- [ ]`). **Chưa được code:** lát chạm kill list mục 1 (đường ghi mới qua cửa danh tính), mục 7 (công tắc lớn mới) và chỉ gọi bộ quét bí mật (mục 2) — Đại ca duyệt plan và review Codex trước (Global Constraints).

**Trạng thái:** viết 18/10/2026 trong worktree `plan/tm-1-nen` trên `main` `e2a09ef` (spec `tu-merge-tu-deploy` đã duyệt mốc 0.3, mockup D101). Đã chạy RED→GREEN thật cho cả 8 task theo đúng thứ tự, đo cả bộ qua `tests/chan_host/chay.sh -q`, rồi hoàn nguyên, **áp lại mọi khối mã/docs của chính file này lên cây sạch** (test trước → chạy đỏ → mã → chạy xanh, từng task) và so `diff -r` với trạng thái đã chạy — mục "Kiểm chứng plan". Nhánh chỉ có file plan. CHƯA áp vào `main`. Không có bước OS nào trong lát này. **Sửa vòng 2 (18/10, sau review Codex vòng 1):** hợp đồng D89 mới cho `file_cam` (Q1), áp và chạy thật sửa chống ồn của Codex (D98/D114), đồng bộ D114–D116; chạy lại RED→GREEN cả 8 task trên cây sạch `e2a09ef` và cả bộ — mục "Kiểm chứng plan", "Phản hồi review Codex vòng 1".

**Goal:** Dựng phần nền mà ba lát sau (TM-2 tự merge, TM-3 tự deploy, TM-4 giao diện) dùng chung: cài đặt tự động theo dự án lưu **bằng sự kiện** trong kho sự kiện (D88), đọc trạng thái, tuyến đọc/ghi qua cửa ghi có mã thao tác và `expected_version` (D79), kênh `header` chỉ nhận TẠM DỪNG (D87), TẠM DỪNG dự án và toàn trạm (D78), kiểm lệnh khi lưu và từ chối lệnh có vẻ chứa bí mật (D97 luật 4), khoá cứng QC/kiểm lại/cấu trúc DB không có trường (D71, D76), khoá chung trước mọi thao tác tự động (design D-2, D-9), đường cấm từ ba lệnh dưới dạng hàm tính (D89), và toàn bộ báo tin Telegram của tính năng (D-8, D98, D99). Ghép lát này **không đổi hành vi nào** của trạm: mọi công tắc mặc định tắt, chưa có mã nào merge hay deploy.

**Architecture:** Package mới `tram/tu_dong/` giữ mô hình và luật (`cai_dat.py` — hàm thuần), lưu/đọc (`luu.py` — mọi hàm nhận **kết nối** `su-kien.db`, dùng được với `KhoSuKien.db` của tram-api lẫn `KhoPhieu.db` của tiến trình giao việc; ghi trong một `BEGIN IMMEDIATE`), khoá chung (`khoa.py`) và đường cấm D89 (`file_cam.py`). Thao tác ghi dashboard ở `tram/thao_tac/tu_dong.py` (cùng khuôn `chay_thao_tac` + bảng `thao_tac` như estop/khe). Trạng thái hiển thị ở `tram/suy/tu_dong.py`; tuyến ở `tram/api/tuyen_tu_dong.py` (hai router: `doc` không cần danh tính, `ghi` qua `Depends(yeu_cau_ghi)` + `TuyenEnvelopeKin`). Báo tin: `tram/bao_tin/nguon_tu_dong.py` ánh xạ mọi sự kiện `tu_dong.*`, `tu_merge.*`, `deploy.*` sang tin; `chong_on.py` thêm giờ yên lặng theo loại (D98). Không bảng mới, không YAML mới.

**Tech Stack:** Python 3.12 stdlib (`shlex`, `sqlite3`, `dataclasses`), FastAPI/pydantic có sẵn, pytest 8. Không dependency mới.

**Spec / nguồn:** change [`openspec/changes/tu-merge-tu-deploy/`](../../openspec/changes/tu-merge-tu-deploy/) — `specs/dieu-khien-tu-dong/spec.md` (Requirement: Cài đặt theo dự án lưu bền · Chỉnh trên dashboard qua cửa ghi · Cửa ghi còn tạm thì chỉ cho TẠM DỪNG · Báo Telegram mỗi lần cài đặt đổi · Lệnh deploy không được chứa bí mật · Dự án khoá ghi không bật được tự động · TẠM DỪNG theo dự án · TẠM DỪNG toàn trạm — phía máy chủ), `specs/tu-merge/spec.md` (Khoá cứng QC — Scenario "Yêu cầu tắt điều kiện QC bị từ chối"; Báo Telegram mỗi lần tự merge), `specs/tu-deploy/spec.md` (Ba lệnh deploy — lưu và khoá tự deploy khi thiếu lệnh; Báo Telegram mỗi lần deploy và lùi); `design.md` D-2, D-4, D-5, D-8, D-9; `tasks.md` mốc 1.1–1.7, 4.1. Quyết định D69–D79, D87–D101, D112 (`docs/quyet-dinh/2026-10-18-tu-merge-tu-deploy.md`). Chia lát: [`2026-10-18-tm-0-chia-lat.md`](2026-10-18-tm-0-chia-lat.md). Mã thật đã đọc: `tram/api/{bao_mat,kenh_ghi,tuyen_ghi,tuyen_chu,tuyen_doc,than,app,phu_thuoc,loi_envelope}.py`, `tram/thao_tac/{chay,chung,khe,estop,kho,loi}.py`, `tram/su_kien/{kho,ket_noi,ghi_trong}.py`, `tram/phieu/kho.py`, `tram/bao_tin/{tin,nguon,vong,chong_on}.py`, `tram/nho/bi_mat.py`, `tram/cau_hinh/{bat_ghi,cach_ly,du_an}.py`, `tram/kiem/duong_dan_cam.py`, `tram/giao_viec/{tick_github,su_kien}.py`.

## Global Constraints

- **Kill list (`AGENT_RULES.md` §2) — STOP, Đại ca duyệt trước khi code.** Chấm blast radius: chạm ranh giới bảo mật/dữ liệu (đường ghi mới, kho sự kiện) + hơn 2 package (`tu_dong`, `thao_tac`, `suy`, `api`, `bao_tin`, `su_kien`) = 2 điểm, cộng kill list:
  - mục **1 cửa danh tính**: thêm 5 tuyến ghi dùng `Depends(yeu_cau_ghi)` và một phụ thuộc mới `can_kenh_that` (D87) đọc `app.state.kenh_ghi`. **Không sửa** `tram/api/bao_mat.py`, `tram/api/kenh_ghi.py`.
  - mục **7 công tắc lớn**: công tắc tự merge, tự deploy, ba nút điều kiện, TẠM DỪNG dự án/toàn trạm — mặc định tắt, chưa có mã nào đọc chúng để merge/deploy (TM-2, TM-3).
  - mục **2 bộ quét bí mật**: **chỉ gọi** `tram.nho.bi_mat.quet`, không sửa `bi_mat.py`; không sửa `tram/bao_tin/telegram.py`.
  - mục **4 cấu trúc DB: không chạm.** Không `CREATE TABLE`, không sửa `tram/su_kien/ket_noi.py`, `tram/phieu/luoc_do.py`. `tram/su_kien/kho.py` chỉ thêm thuộc tính `db` (trả kết nối có sẵn, như `KhoPhieu.db`). Kiểm: `git diff e2a09ef -- tram | grep -c "CREATE TABLE"` = 0.
  - mục **5 đẩy code/merge/deploy: không chạm** (`tram/giao_viec/gh.py`, `pr*.py`, `tram/cong_bo/`): thuộc TM-2/TM-3.
- **Đổi hợp đồng giữa package (`AGENT_RULES.md` §11):** mục "Interfaces cho lát sau" là hợp đồng mới cho TM-2/3/4 — Đại ca duyệt cùng plan. Đổi sau khi TM-2/3/4 đã viết plan thì sửa ở đây trước.
- **N₀ = 3321** (`tests/chan_host/chay.sh -q` trên `e2a09ef`, đo 18/10/2026: `3321 passed in 340.75s`, nhật ký chặn 0 dòng mới, điểm mù 48, push giả lập 629). **Sau lát: `3422 passed` (+101 test mới: 20 + 10 + 23 + 8 + 9 + 27 + 4)** — đo thật trên cây đã chạy và trên cây dựng lại từ plan (mục "Kiểm chứng plan"). Đo lại N₀ trước Task 1; lệch thì tìm nguyên nhân trước.
- Chạy test BẮT BUỘC qua `tests/chan_host/chay.sh -q [đường test]`; "0 dòng mới" trong nhật ký chặn là điều kiện xanh. Test không bao giờ gọi Telegram, `gh`, `bd`, mạng; tram-api chạy trong bộ nhớ (`api_gia`, `asgi_gia`), SQLite tạm.
- Mỗi file `tram/` ≤ 120 dòng, mỗi dòng ≤ 120 ký tự (`tests/test_do_dai_ma.py`). Sau lát: `tram/tu_dong/luu.py` 114, `tram/su_kien/kho.py` 113, `tram/bao_tin/chong_on.py` 118, `tram/api/tuyen_tu_dong.py` 102, `tram/tu_dong/cai_dat.py` 90, `tram/api/than.py` 74, `tram/bao_tin/tin.py` 64, `tram/bao_tin/nguon_tu_dong.py` 47, `tram/thao_tac/tu_dong.py` 42, `tram/tu_dong/file_cam.py` 45, `tram/suy/tu_dong.py` 29, `tram/tu_dong/khoa.py` 28. Không vòng import cấp module (`tests/test_vong_import.py`).
- Bí mật: lỗi kiểm lệnh là **câu hằng**, không chép lệnh; lỗi thân yêu cầu không vọng lại nội dung (`TuyenEnvelopeKin`); tin Telegram chỉ có dự án, mã bead, nhãn loại, mã chi tiết từ bảng cố định — không lệnh, SHA, URL, đầu ra lệnh (INV-001).
- Hunk viết trên `e2a09ef`; áp theo NỘI DUNG (`git apply --check` trước; không sạch thì DỪNG, báo điều phối). Một task một commit trên nhánh task; không push, không merge, không `bd` ghi. Giữ `bat_ghi: false` của `hr-codex`, `giao_viec.bat: false`.

## Bảng G — điều plan bảo đảm và bằng chứng

| # | Bảo đảm | Ở đâu | Bằng chứng offline |
|---|---|---|---|
| G1 | Mặc định đúng spec: tự merge tắt, tự deploy tắt, ba nút điều kiện bật, ba lệnh trống, không tạm dừng; phiên bản "0" | `cai_dat.MAC_DINH`, `luu.doc_cai_dat` | `test_gia_tri_mac_dinh_theo_spec`, `test_chua_chinh_thi_mac_dinh_phien_ban_0`, `test_xem_mac_dinh_ai_cung_xem_duoc` |
| G2 | Lưu bền qua khởi động lại, không bảng mới; lịch sử ai đổi, lúc nào, trước → sau (so hai bản liền nhau) | `luu.doi_cai_dat`, `lich_su_doi` | `test_ghi_roi_doc_lai_sau_khi_khoi_dong_lai`, `test_lich_su_doi_hai_dong_moi_nhat_truoc`, `test_luu_qua_unix_socket_gui_lai_va_lich_su` |
| G3 | Đọc–so–ghi trong một `BEGIN IMMEDIATE`: ghi của trạm (`KhoPhieu`, tiến trình khác) áp lên bản mới nhất, không đè thay đổi của Đại ca; nhập vào giao dịch của người gọi | `luu.giao_dich` | `test_giao_dich_giu_khoa_ghi_voi_tien_trinh_khac`, `test_ghi_cua_tram_ap_tren_ban_moi_nhat_qua_kho_phieu`, `test_giao_dich_loi_thi_khong_ghi_gi` |
| G4 | Cửa ghi: thiếu/giả danh tính, thiếu `X-Tram`, sai `Origin` → 403 (cả qua `unix-socket`); cùng mã thao tác → kết quả lần đầu, một dòng lịch sử; phiên bản cũ → 409, không để bản ghi `thao_tac` treo | `tuyen_tu_dong.ghi`, `thao_tac/tu_dong.py` | `test_thieu_hoac_gia_danh_tinh_bi_403` (4 ca), `test_luu_mot_lan_theo_ma`, `test_ma_loi_409_422`, `test_cung_ma_khac_noi_dung_va_phien_ban_cu_la_xung_dot` |
| G5 | D87: kênh `header` → mọi ghi 403 "cần kênh ghi unix-socket" trừ TẠM DỪNG dự án và toàn trạm (Tiếp tục cũng 403 — giả định Câu hỏi 1); GET có `chi_tam_dung` | `can_kenh_that`, `suy.chung` | `test_kenh_header_chi_nhan_tam_dung` |
| G6 | D71/D76: QC, kiểm lại, cấu trúc DB không có trường ở mô hình lẫn thân yêu cầu — gửi trường lạ (trong `dieu_kien` hay ở gốc) → 422, cài đặt không đổi | `CaiDatTuDong`, `ThanCaiDat` (`extra="forbid"`) | `test_khoa_cung_khong_co_truong_nao`, `test_ma_loi_409_422` |
| G7 | Lệnh: > 500 ký tự, ký tự điều khiển, không tách được, rỗng, có vẻ chứa bí mật → 422 câu hằng; không lưu, không vào lịch sử, không bản ghi `thao_tac`; phản hồi không chứa chuỗi bí mật (kể cả lệnh > 2000 ký tự bị pydantic chặn) | `cai_dat.loi_lenh`, `loi_cai_dat` | `test_lenh_bi_tu_choi_bang_cau_hang` (9 ca), `test_tu_choi_khong_luu_khong_ghi_thao_tac`, `test_lenh_co_bi_mat_bi_tu_choi_khong_vong_lai` |
| G8 | `bat_ghi: false` → bật công tắc nào cũng 422 "chỉ quét thử"; lưu lệnh khi công tắc tắt vẫn được; TẠM DỪNG vẫn bấm được. Tự deploy cần đủ 3 lệnh | `loi_cai_dat`, `_bat_ghi` | `test_loi_cai_dat_luat_bat_ghi_va_du_lenh`, `test_ma_loi_409_422` |
| G9 | TẠM DỪNG / Tiếp tục không kiểm phiên bản (như estop); đã ở trạng thái đó thì không ghi thêm; dự án và toàn trạm độc lập; công tắc giữ nguyên sau Tiếp tục | `luu.ghi_tam_dung`, `tam_dung_thao_tac` | `test_tam_dung_tiep_tuc_khong_kiem_phien_ban`, `test_tam_dung_toan_tram`, `test_tam_dung_du_an_va_toan_tram_doc_lap` |
| G10 | Khoá chung thứ tự cố định estop → tạm dừng toàn trạm → tạm dừng dự án → `bat_ghi` → công tắc → đủ 3 lệnh; nút Deploy tay bỏ qua tạm dừng/công tắc, khoá khi estop (D97) | `khoa.ly_do_chan` | `test_thu_tu_ly_do_estop_truoc_cong_tac_sau`, `test_deploy_tay_duoc_khi_tam_dung_khoa_khi_estop` |
| G11 | D89 (hàm, hợp đồng sau Codex Q1): mọi token argv (kể cả sau `=`, kể cả đường tuyệt đối và `..`) đi nguyên văn tới callback của bên gọi; callback nói có trong repo → mẫu cấm (`thu-muc/**` cho thư mục); tuyệt đối trỏ vào repo → cấm; tuyệt đối ngoài repo, `..` thoát gốc, chính gốc → bỏ (callback); `~`, glob, cờ, rỗng → không hỏi; kết quả callback dạng lạ → bỏ; dùng thẳng được với `duong_dan_cham_cam` (không kèm `cho_phep` — tập bắt buộc, C2) | `file_cam.duong_dan_tu_lenh` | `test_duong_dan_cam_tu_ba_lenh`, `test_duong_dan_tuyet_doi_hoac_vong_trong_repo_bi_cam` (5 ca), `test_bo_qua_token_ngoai_repo_hoac_la` (10 ca), `test_token_nguyen_van_toi_callback`, `test_ket_qua_callback_la_bi_bo` |
| G12 | Mỗi sự kiện của hợp đồng → đúng loại tin; tin đọc bằng lời thường ("tự deploy bật", "trạm: …", "hỏng liên tiếp 2 lần"); không chứa lệnh | `nguon_tu_dong.tin_tu_dong`, `tin.soan_tin` | `test_su_kien_sang_tin` (17 ca), `test_soan_tin_loi_thuong` (7 ca), `test_dau_cuoi_dashboard_den_tin_khong_chua_lenh` |
| G13 | D98/D99/D114: tin xấu và tin đổi cài đặt gửi NGAY cả trong giờ yên lặng, không bị cửa sổ gom 5 phút giữ lại (lần 2, 3 trong 5 phút vẫn gửi ngay); tin tốt gom gửi khi hết giờ yên lặng, bền qua khởi động lại `tram-bao-tin`; loại "mỗi lần một tin" không bị luật 1 giờ; loại tin cũ giữ hành vi cũ | `chong_on.BoChongOn` | `test_chong_on_tu_dong.py` (4 test, gồm tin xấu ở phút 0, 1, 2 và tin đang gom trong cửa sổ 5 phút khi bước vào giờ yên lặng), `test_chong_on.py` không sửa, xanh |
| G14 | Ghép không đổi hành vi: tuyến cũ, loại tin cũ, cả bộ xanh | — | cả bộ `3422 passed` (+101 test mới: 20 + 10 + 23 + 8 + 9 + 27 + 4), 0 dòng chặn mới |

## Thiết kế — bốn chỗ chọn

1. **Lưu: sự kiện mang toàn bộ cài đặt, phiên bản = id sự kiện (design D-4).** Đọc lúc nào cũng từ sự kiện mới nhất; lịch sử tính lúc đọc. Hàm `luu.py` nhận `sqlite3.Connection` vì hai tiến trình dùng hai lớp kho khác nhau trên cùng `su-kien.db`: tram-api (`KhoSuKien`) và vòng tick (`KhoPhieu`, nơi TM-2/TM-3 chạy). `KhoSuKien` chỉ thêm thuộc tính `db` (như `KhoPhieu.db` có sẵn). Ghi luôn trong `BEGIN IMMEDIATE`: nếu trạm tự tắt tự deploy (TM-3) đúng lúc Đại ca tắt tự merge, cả hai thay đổi đều còn (không "ghi đè bằng ảnh cũ"). *Loại:* thêm `giao_dich()` vào `KhoSuKien` (đẩy file quá 120 dòng, và `KhoPhieu` vẫn khác giao diện); bảng mới (kill list mục 4).
2. **D87 hiểu chặt: kênh `header` chỉ nhận TẠM DỪNG**, Tiếp tục cũng 403. Lời Đại ca ở D87 là "chỉ cho bấm TẠM DỪNG"; spec/design viết "TẠM DỪNG và Tiếp tục". Mã theo D87 vì một tiến trình agent giả danh qua `header` không được gỡ tạm dừng Đại ca vừa bấm; mọi Scenario của spec vẫn đạt. Đây là chỗ nguồn lệch nhau — **Câu hỏi 1**, đổi bằng một dòng (`dependencies=[Depends(can_kenh_that)]` ở hai tuyến Tiếp tục).
3. **Báo tin của cả tính năng nằm ở lát này.** Tên sự kiện là hợp đồng của TM-1 nên ánh xạ sự kiện → tin viết một lần (`nguon_tu_dong.py`), TM-2/TM-3 chỉ ghi sự kiện, không ai sửa `tram/bao_tin/` song song. Tin đổi cài đặt mang mã chi tiết trong ô `bead_id` (ví dụ `tu-deploy-bat`, `tram-tam-dung`) — `soan_tin` dịch sang lời thường **chỉ** cho hai loại `cai_dat_doi`, `deploy_da_lui` (mã bead thật của loại khác không bị dịch).
4. **Giờ yên lặng theo loại (D98, D99).** `LOAI_LUON_GUI` thành tập: `tram_loi` như cũ + bốn tin xấu của deploy + `cai_dat_doi` (Đại ca chốt **D114**: tin cài đặt gửi ngay). Tin xấu mới và `cai_dat_doi` gửi ngay mỗi lần, **không qua cửa sổ gom 5 phút** (Codex review vòng 1 — trước đó lần thứ hai trong 5 phút bị giữ tới hết cửa sổ); `tram_loi` giữ hành vi cũ. Ba tin tốt (`tu_merge`, `san_sang_deploy`, `deploy_xong`) trong giờ yên lặng vào hàng `cho_sang` (lưu trong `chong-on.json`), gửi ở lần `den_han` đầu tiên sau giờ yên lặng. Loại "mỗi lần một tin" (đổi cài đặt, mọi kết quả deploy) bỏ luật "không lặp trong 1 giờ"; riêng `deploy_xong` (tin tốt) vẫn gom trong cửa sổ 5 phút. Các loại tin cũ (chờ review, cờ đỏ…) giữ nguyên: trong giờ yên lặng vẫn bị bỏ như trước.

## Bản đồ tác động và cổng khảo sát (`DEVELOPMENT_PLAYBOOK.md`)

- **Package/file:** mới `tram/tu_dong/` (4 module), `tram/thao_tac/tu_dong.py`, `tram/suy/tu_dong.py`, `tram/api/tuyen_tu_dong.py`, `tram/bao_tin/nguon_tu_dong.py`; sửa `tram/su_kien/kho.py` (thuộc tính `db`), `tram/api/{than,app}.py`, `tram/bao_tin/{tin,nguon,chong_on}.py`. Vòng import: `tu_dong → thao_tac.loi, su_kien.ghi_trong, nho.bi_mat`; `thao_tac.tu_dong → tu_dong`; `api.tuyen_tu_dong → suy, thao_tac, tu_dong`; `bao_tin.nguon → bao_tin.nguon_tu_dong → bao_tin.tin` — không vòng (test canh).
- **Lệnh/tuyến:** thêm 2 GET + 5 POST (mục "Tuyến"); không lệnh `tram` mới. **Dữ liệu:** kho sự kiện thêm 3 loại do lát này ghi (`tu_dong.cai_dat`, `tu_dong.tam_dung`, `tu_dong.tiep_tuc`), bảng `thao_tac` thêm dòng của 5 thao tác — không bảng/cột mới; `~/.tram/bao-tin/chong-on.json` thêm khoá `cho_sang` (thiếu = rỗng). Không chạm Beads, LanceDB, repo dự án.
- **Ai sở hữu dữ liệu:** cài đặt tự động = trạm (kho sự kiện), chỉ đổi qua thao tác của Đại ca (tram-api) hoặc mã của trạm (TM-3, tác nhân `tram/…`). **Bí mật:** không có bí mật nào đi qua lát này; lệnh có dấu hiệu bí mật bị từ chối trước khi lưu, lỗi là câu hằng.
- **Hệ ngoài:** không thêm. Telegram đi qua `tram-bao-tin` có sẵn (`telegram.py` không sửa). **Hỏng thì cổng đóng:** đọc cài đặt lỗi → mặc định tắt; `bat_ghi` đọc lỗi → coi `false`; kênh không phải `unix-socket` → chỉ TẠM DỪNG.
- **Đường lui:** revert nhánh. Sự kiện mới chỉ là dòng ghi thêm; mã cũ bỏ qua loại lạ (`tin_tu_su_kien` trả `[]`, `BoChongOn` cũ bỏ khoá `cho_sang`). Giao diện: không (TM-4).
- **Chỉ chứng minh trên máy thật:** không có trong lát này (kênh `unix-socket` thật thuộc G29, trước khi bật công tắc).

## Interfaces cho lát sau (HỢP ĐỒNG — TM-2, TM-3, TM-4 dựa vào đây)

Import đúng module con. Mọi tên dưới đây có trong mã của plan này (Task 1–7).

**`tram.tu_dong.cai_dat`** (hàm thuần)
- `CaiDatTuDong` (frozen): `tu_merge=False`, `tu_deploy=False`, `dk_ci=True`, `dk_cot=True`, `dk_hang_rao=True`, `lenh_deploy=""`, `lenh_kiem_song=""`, `lenh_lui=""`; `.du_lenh -> bool` (đủ 3 lệnh); `.phang() -> dict` (dạng trong sự kiện). `MAC_DINH = CaiDatTuDong()`.
- `KHOA_CUNG = ("qc", "kiem_lai", "schema")` — hiển thị "luôn bật", không bao giờ có trường. `TRUONG_LENH`, `TEN_LENH`, `DO_DAI_LENH = 500`.
- `sang_api(cd) -> {"tu_merge", "tu_deploy", "dieu_kien": {"ci", "cot", "hang_rao"}, "lenh": {"deploy", "kiem_song", "lui"}}`; `tu_api(dict)`; `tu_phang(dict)` (khoá lạ bỏ qua, thiếu lấy mặc định); `truong_doi(cu, moi) -> list[str]`.
- `loi_lenh(lenh) -> str | None`, `loi_cai_dat(cd, *, bat_ghi) -> str | None` (câu hằng, không chép lệnh).

**`tram.tu_dong.luu`** — mọi hàm nhận `db: sqlite3.Connection` = `KhoSuKien.db` (tram-api) hoặc `KhoPhieu.db` (vòng tick)
- Hằng: `DU_AN_TRAM = "_tram"`, `LOAI_CAI_DAT = "tu_dong.cai_dat"`, `LOAI_TAM_DUNG = "tu_dong.tam_dung"`, `LOAI_TIEP_TUC = "tu_dong.tiep_tuc"`.
- `TamDung(boi: str, luc: str, ly_do: str)`; `TrangThaiTuDong(cai_dat, phien_ban: str, tam_dung_du_an: TamDung | None, tam_dung_tram: TamDung | None)`.
- `doc_trang_thai(db, du_an) -> TrangThaiTuDong` — TM-2/TM-3 gọi **ngay trước** lệnh merge/deploy.
- `doc_cai_dat(db, du_an) -> (CaiDatTuDong, phien_ban)`; `tam_dung_cua(db, du_an)`; `lich_su_doi(db, du_an, gioi_han=20)`.
- `doi_cai_dat(db, du_an, doi: Callable[[CaiDatTuDong], CaiDatTuDong], *, tac_nhan, expected=None, them=None) -> int | None` — TM-3 tự tắt: `doi_cai_dat(kho.db, du_an, lambda c: replace(c, tu_deploy=False), tac_nhan="tram/tu-deploy", them={"ly_do": "hong-3-lan"})` (lùi hỏng: `"ly_do": "lui-hong"`).
- `ghi_tam_dung(db, du_an, *, tam_dung, tac_nhan, them=None) -> bool` — TM-3 lùi hỏng/không rõ: `ghi_tam_dung(kho.db, du_an, tam_dung=True, tac_nhan="tram/tu-deploy", them={"ly_do": "lui-hong" | "khong-ro"})`.
- `giao_dich(db)` — gọi bên trong `KhoPhieu.giao_dich()` thì nhập vào giao dịch đó (người gọi commit).

**`tram.tu_dong.khoa`**
- `ly_do_chan(tt, *, viec: "merge" | "deploy" | "deploy_tay", bat_ghi: bool, estop_bat: bool) -> list[str]`; rỗng = được làm. Mã: `estop`, `tam_dung_tram`, `tam_dung_du_an`, `bat_ghi`, `tu_merge_tat`, `tu_deploy_tat`, `thieu_lenh` — nhãn ở `NHAN_LY_DO`. TM-2 đặt các mã lý do riêng của nó **sau** danh sách này (thứ tự design D-2) và tự giữ nhãn của chúng.
- Nguồn tham số: `estop_bat = tram.chu.estop.dang_bat()`; `bat_ghi = tram.cau_hinh.bat_ghi.bat_ghi(ten)` (lỗi đọc → coi `False`).

**`tram.tu_dong.file_cam`** (hợp đồng D89 sau review Codex vòng 1 — Q1, C2)
- `duong_dan_tu_lenh(cd, loai_trong_repo: LoaiTrongRepo) -> tuple[str, ...]`, với `LoaiTrongRepo = Callable[[str], tuple[str, Literal["file", "dir"]] | None]`. Trả mẫu cấm đã sắp xếp, không trùng: file → `rel`, thư mục → `rel/**`.
- `file_cam` tách ba lệnh bằng `shlex`, lấy mỗi token và phần sau `=` đầu tiên của nó, chỉ bỏ token rỗng, bắt đầu bằng `~` hoặc `-` (cờ), có ký tự glob `*?[`. Mọi token khác — **kể cả đường tuyệt đối và token có `..`** — đi NGUYÊN VĂN tới callback. Kết quả callback dạng lạ (rel rỗng, bắt đầu `/`, có đoạn `..`/`.`/rỗng, loại khác `file`/`dir`) bị bỏ.
- **Bên gọi (TM-2, TM-3) dựng `loai_trong_repo`** từ gốc repo đáng tin của dự án (không lấy từ lệnh hay từ agent): token tương đối nối vào gốc, token tuyệt đối giữ nguyên; chuẩn hoá (resolve `..`, symlink); nằm ngoài gốc hoặc chính là gốc → `None`; có trong repo (cây git ở commit đang xét / nhánh chính) → `(đường dẫn tương đối POSIX từ gốc, "file" | "dir")`. Callback mẫu: `_repo` trong `tests/test_tu_dong_khoa.py` (Task 3). Dự án có nhiều gốc hợp lệ (bản checkout của trạm, worktree deploy) thì callback coi tuyệt đối dưới gốc nào cũng là "trong repo".
- **Tập này là tập cấm BẮT BUỘC** (Codex C2): bên gọi cộng vào kiểm đường cấm ở mọi chỗ đang truyền `du_an.giao.duong_dan_cam` (`kiem_lai.py`, `xet_spec.py`, `xet_xong.py`, `tram/tho/ket_thuc.py`) theo cách **không bị `cho_phep` (ngoại lệ dự án) miễn** — `them=` của `duong_dan_cham_cam` hiện lọc ngoại lệ trước, nên TM-3 phải kiểm tập này riêng (thuộc plan TM-3).

**Sự kiện** (bảng `su_kien`; `bead_id` trống trừ khi ghi rõ). TM-1 đã có tin cho mọi dòng — TM-2/TM-3 chỉ ghi đúng dạng:

| Loại | `du_an` | `du_lieu` (khoá bắt buộc) | `tac_nhan` | Ai ghi | Tin |
|---|---|---|---|---|---|
| `tu_dong.cai_dat` | dự án | `cai_dat` (toàn bộ, dạng `phang()`), `doi` (trường đổi); tuỳ: `ma_thao_tac`, `ly_do` (`hong-3-lan`, `lui-hong`) | `dai-ca/dashboard` · `tram/tu-deploy` | TM-1 (qua `doi_cai_dat`), TM-3 | `cai_dat_doi` mỗi trường; trạm + `hong-3-lan` → `tu_deploy_tu_tat` |
| `tu_dong.tam_dung` / `tu_dong.tiep_tuc` | dự án hoặc `_tram` | tuỳ: `ma_thao_tac`, `ly_do` (`lui-hong`, `khong-ro`) | như trên | TM-1 (qua `ghi_tam_dung`), TM-3 | `cai_dat_doi` (`tam-dung`, `tram-tam-dung`, `tam-dung-toan-tram`…) |
| `tu_merge.cho` | dự án, `bead_id` | `ly_do: [mã]`, `commit` | `tram/tu-merge` | TM-2 (chỉ khi lý do khác lần trước) | không |
| `tu_merge.bat_dau` | dự án, `bead_id` | `ma_thao_tac` (`tm-…`), `commit`, `pr`, `loai: code \| spec` | `tram/tu-merge` | TM-2, **trước** lệnh `gh` | không |
| `tu_merge.xong` | dự án, `bead_id` (feature khi `spec`) | `ma_thao_tac`, `loai` | `tram/tu-merge` | TM-2 | `tu_merge` (gom sau giờ yên lặng) |
| `tu_merge.loi` | dự án, `bead_id` | `ma_thao_tac`, `ma_loi` (mã cố định) | `tram/tu-merge` | TM-2 | `tram_loi` |
| `deploy.san_sang` | dự án | `commit`, `so_merge` | `tram/tu-deploy` | TM-3 | `san_sang_deploy` (gom) |
| `deploy.bat_dau` | dự án | `ma_thao_tac` (`dp-…`), `commit`, `commit_truoc`, `nguon: dai_ca \| tu_dong` | `tram/tu-deploy` | TM-3 | không |
| `deploy.lenh` | dự án | `buoc`, `ma_thoat`, `giay`, `digest_log` | `tram/tu-deploy` | TM-3 | không |
| `deploy.xong` | dự án | `ma_thao_tac`, `ket_qua: dat \| da_lui \| lui_hong \| khong_ro`, `dem_hong` (int) | `tram/tu-deploy` | TM-3 | `deploy_xong` · `deploy_da_lui` (+`hong-N-lan`) · `lui_hong` · `deploy_khong_ro` |

Không đưa vào `du_lieu` của sự kiện có tin: lệnh, URL, đầu ra lệnh, tiêu đề bead. Tác nhân của trạm luôn bắt đầu bằng `tram/` (tin thêm "trạm:").

**Tuyến** (`tram/api/tuyen_tu_dong.py`)
- `GET /api/tu-dong` (mọi người) → `{tam_dung_tram, estop, kenh_ghi, chi_tam_dung, la_dai_ca, du_an: [{ten, bat_ghi, tu_merge, tu_deploy, du_lenh, tam_dung}]}`; `tam_dung` = `null | {boi, luc, ly_do}`.
- `GET /api/du-an/{ten}/tu-dong` (mọi người; 404 dự án lạ) → phần chung + `{du_an, bat_ghi, cai_dat: sang_api(...), du_lenh, phien_ban, tam_dung, khoa_cung, lich_su_doi: [{luc, tac_nhan, doi: [{truong, truoc, sau}]}]}`. TM-2 thêm khoá `cho_dai_ca`; TM-3 thêm `san_sang`, `dang_deploy`, `lich_su`, `dem_hong` (vào `tram/suy/tu_dong.py`, chỉ THÊM khoá).
- `POST /api/du-an/{ten}/tu-dong/cai-dat` `{ma_thao_tac, expected_version, cai_dat: {tu_merge, tu_deploy, dieu_kien: {ci, cot, hang_rao}, lenh: {deploy, kiem_song, lui}}}` → `{ket_qua: {"tu_dong.cai_dat": {phien_ban}}, lap_lai}`. Cần kênh `unix-socket`.
- `POST /api/du-an/{ten}/tu-dong/tam-dung`, `POST /api/tu-dong/tam-dung` `{ma_thao_tac, expected_version}` (phiên bản không kiểm) → `{ket_qua: {"tu_dong.tam_dung": bool}, lap_lai}`; nhận cả kênh `header`.
- `POST …/tu-dong/tiep-tuc`, `POST /api/tu-dong/tiep-tuc` — như trên, cần kênh `unix-socket` (Câu hỏi 1).
- TM-3 sở hữu router riêng `tram/api/tuyen_deploy.py`: `POST /api/du-an/{ten}/tu-dong/deploy`,
  dùng cả `Depends(yeu_cau_ghi)` và `Depends(can_kenh_that)`, kiểm `ly_do_chan(viec="deploy_tay")`
  (khác rỗng → 422 kèm nhãn) và `expected_commit` (409). `ThanDeploy` cũng ở router đó, không ở `than.py`.
- Mã lỗi: 403 `{"detail"}` (danh tính/kênh — `CAN_KENH` bắt đầu bằng "cần kênh ghi unix-socket"); 404/409/422 nghiệp vụ `{"loi": "…"}` (409 luôn có "đã đổi … — tải lại"); 422 thân sai `{"trang_thai": "khong_hop_le", "loi": ["Thân yêu cầu không hợp lệ"]}`.

**Báo tin** (TM-2/TM-3 không sửa): loại mới `tu_merge`, `san_sang_deploy`, `deploy_xong`, `deploy_da_lui`, `tu_deploy_tu_tat`, `deploy_khong_ro`, `lui_hong`, `cai_dat_doi` (`tram.bao_tin.tin.LOAI_TIN`).

## Task ↔ file

| Task | Mốc `tasks.md` | ⛔ | File |
|---|---|---|---|
| 1 | 1.1, 1.3 | không | Create `tram/tu_dong/__init__.py`, `tram/tu_dong/cai_dat.py`, `tests/test_tu_dong_cai_dat.py` |
| 2 | 1.1 | dữ liệu (không đổi cấu trúc) | Modify `tram/su_kien/kho.py`; Create `tram/tu_dong/luu.py`, `tests/test_tu_dong_luu.py` |
| 3 | (hợp đồng TM-2/3) | không | Create `tram/tu_dong/khoa.py`, `tram/tu_dong/file_cam.py`, `tests/test_tu_dong_khoa.py` |
| 4 | 1.2, 1.4, 1.6 | mục 7 | Create `tram/thao_tac/tu_dong.py`, `tests/test_thao_tac_tu_dong.py` |
| 5 | 1.2–1.6 | **mục 1, 7** | Modify `tram/api/than.py`, `tram/api/app.py`; Create `tram/suy/tu_dong.py`, `tram/api/tuyen_tu_dong.py`, `tests/test_api_tu_dong.py` |
| 6 | 1.7, 4.1 | không | Modify `tram/bao_tin/tin.py`, `tram/bao_tin/nguon.py`; Create `tram/bao_tin/nguon_tu_dong.py`, `tests/test_bao_tin_tu_dong.py` |
| 7 | 4.1 (D98) | không | Modify `tram/bao_tin/chong_on.py`; Create `tests/test_chong_on_tu_dong.py` |
| 8 | — | không (docs) | Modify `docs/MODULES.md`, `openspec/changes/tu-merge-tu-deploy/tasks.md` |

Thứ tự bắt buộc 1 → 8 (mỗi task import mã của task trước). Không file nào bị hai task cùng sửa.

## Tasks

### Task 1: Mô hình cài đặt tự động, mặc định, kiểm lệnh khi lưu

**Scenario:** "Giá trị mặc định"; "Dán token vào lệnh kiểm còn sống" (phần kiểm); "Yêu cầu tắt điều kiện QC bị từ chối" (mô hình không có trường); D73 "thiếu lệnh không bật được tự deploy"; INV-005.

**Interfaces:** như mục hợp đồng `tram.tu_dong.cai_dat`.

- [ ] **Step 0: Kiểm điều kiện vào** — Đại ca đã duyệt plan (kill list mục 1, 2, 7; hợp đồng). HEAD có `e2a09ef` và `git diff e2a09ef HEAD -- tram/su_kien/kho.py tram/api/than.py tram/api/app.py tram/bao_tin docs/MODULES.md openspec/changes/tu-merge-tu-deploy/tasks.md` rỗng; khác thì `git apply --check` từng bản vá, hỏng thì DỪNG. Đo N₀: `tests/chan_host/chay.sh -q` → mong đợi `3321 passed`, 0 dòng chặn mới.

- [ ] **Step 1: Viết test**

Tạo mới `tests/test_tu_dong_cai_dat.py` (nguyên văn):

```python
"""TM-1 (change tu-merge-tu-deploy, dieu-khien-tu-dong): mô hình cài đặt tự động, mặc định, dạng API/sự kiện, kiểm khi
lưu (D69, D71, D73–D76, D88, D97 luật 4 "lệnh có vẻ chứa bí mật bị từ chối"). Hàm thuần — không kho, không mạng."""
from dataclasses import fields, replace

import pytest

from tram.tu_dong.cai_dat import (KHOA_CUNG, MAC_DINH, CaiDatTuDong, loi_cai_dat, loi_lenh, sang_api, truong_doi,
                                  tu_api, tu_phang)

LENH = {"deploy": "/Users/Shared/tram-deploy/repo-nhap/deploy.sh",
        "kiem_song": "curl -fsS --max-time 20 https://repo-nhap.example.vn/suc-khoe",
        "lui": "sh scripts/lui.sh --ve 'ban truoc'"}
DU = tu_api({"tu_merge": True, "tu_deploy": True, "dieu_kien": {"ci": False, "cot": True, "hang_rao": True},
             "lenh": LENH})


def test_gia_tri_mac_dinh_theo_spec():
    """Scenario "Giá trị mặc định": tự merge tắt, tự deploy tắt, ba nút điều kiện bật, ba lệnh trống."""
    assert MAC_DINH == CaiDatTuDong()
    assert (MAC_DINH.tu_merge, MAC_DINH.tu_deploy) == (False, False)
    assert (MAC_DINH.dk_ci, MAC_DINH.dk_cot, MAC_DINH.dk_hang_rao) == (True, True, True)
    assert (MAC_DINH.lenh_deploy, MAC_DINH.lenh_kiem_song, MAC_DINH.lenh_lui) == ("", "", "") and not MAC_DINH.du_lenh


def test_khoa_cung_khong_co_truong_nao():
    """D71, D76: QC, kiểm lại, hàng rào cấu trúc DB luôn bật — mô hình không có chỗ để tắt."""
    ten = {f.name for f in fields(CaiDatTuDong)}
    assert KHOA_CUNG == ("qc", "kiem_lai", "schema")
    assert not set(KHOA_CUNG) & {t.removeprefix("dk_") for t in ten}


def test_dang_api_va_dang_su_kien_qua_lai():
    assert sang_api(DU) == {"tu_merge": True, "tu_deploy": True,
                            "dieu_kien": {"ci": False, "cot": True, "hang_rao": True}, "lenh": LENH}
    assert tu_api(sang_api(DU)) == DU and DU.du_lenh
    assert tu_phang(DU.phang()) == DU
    assert tu_phang({"tu_merge": True, "khoa_tuong_lai": 1}) == replace(MAC_DINH, tu_merge=True)   # mã cũ/mới đọc nhau
    assert tu_api({**sang_api(MAC_DINH), "lenh": {"deploy": "  a.sh  ", "kiem_song": "", "lui": ""}}).lenh_deploy == "a.sh"


def test_truong_doi_theo_thu_tu_mo_hinh():
    assert truong_doi(MAC_DINH, MAC_DINH) == []
    assert truong_doi(MAC_DINH, DU) == ["tu_merge", "tu_deploy", "dk_ci", "lenh_deploy", "lenh_kiem_song", "lenh_lui"]


@pytest.mark.parametrize("lenh", ["", *LENH.values(), "make deploy", "./scripts/kiem-song.sh"])
def test_lenh_hop_le(lenh):
    assert loi_lenh(lenh) is None


@pytest.mark.parametrize("lenh, loi", [
    ("a" * 501, "dài quá 500"),
    ("deploy.sh\nrm -rf /", "ký tự điều khiển"),
    ("deploy.sh\tx", "ký tự điều khiển"),
    ("sh 'thieu nhay", "không tách được"),
    ('""', "Lệnh rỗng"),
    ("curl -H 'Authorization: Bearer abcdefghijklmnopqrstuvwxyz0123456789' https://x.vn", "có vẻ chứa bí mật"),
    ("deploy.sh --token ghp_" + "A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q7r8", "có vẻ chứa bí mật"),
    ("API_KEY=sk-ant-" + "x" * 30 + " ./deploy.sh", "có vẻ chứa bí mật"),
    ("psql postgres://tram:matkhau123@db.local/app -c 'select 1'", "có vẻ chứa bí mật"),
])
def test_lenh_bi_tu_choi_bang_cau_hang(lenh, loi):
    ly_do = loi_lenh(lenh)
    assert ly_do is not None and loi in ly_do
    assert lenh not in ly_do and "matkhau123" not in ly_do and "ghp_" not in ly_do      # không chép lệnh vào lỗi


def test_loi_cai_dat_luat_bat_ghi_va_du_lenh():
    assert loi_cai_dat(DU, bat_ghi=True) is None
    assert loi_cai_dat(MAC_DINH, bat_ghi=False) is None                 # dự án chỉ quét thử vẫn lưu lệnh, công tắc tắt
    assert "chỉ quét thử" in loi_cai_dat(replace(MAC_DINH, tu_merge=True), bat_ghi=False)
    assert "chỉ quét thử" in loi_cai_dat(replace(DU, tu_merge=False), bat_ghi=False)
    assert "Chưa khai đủ 3 lệnh" in loi_cai_dat(replace(DU, lenh_lui=""), bat_ghi=True)
    assert loi_cai_dat(replace(DU, tu_deploy=False, lenh_lui=""), bat_ghi=True) is None
    bi_mat = replace(MAC_DINH, lenh_kiem_song="curl -H 'X-Api-Key: " + "Zx9" * 12 + "' https://x.vn")
    assert loi_cai_dat(bi_mat, bat_ghi=True) == "Lệnh kiểm còn sống: Lệnh có vẻ chứa bí mật — để bí mật ngoài lệnh"
```

- [ ] **Step 2: Chạy, mong đợi ĐỎ**

```bash
tests/chan_host/chay.sh -q tests/test_tu_dong_cai_dat.py
```
Đỏ thật (khi viết plan): `ERROR tests/…` khi thu thập — `ModuleNotFoundError: No module named 'tram.tu_dong'` (`1 error in 0.06s`, thoát 2), nhật ký chặn 0 dòng mới.

- [ ] **Step 3: Viết mã**

Tạo mới `tram/tu_dong/__init__.py` (nguyên văn — file rỗng 0 byte như mọi `__init__.py` của `tram/`, không import gì):

```python

```

Tạo mới `tram/tu_dong/cai_dat.py` (nguyên văn):

```python
"""Cài đặt tự merge / tự deploy của một dự án (change `tu-merge-tu-deploy`, D69–D75, D88, D97): mô hình, mặc định,
dạng API và dạng sự kiện, kiểm khi lưu. Hàm thuần — lưu/đọc ở `luu.py`.

QC đạt, kiểm lại đạt, hàng rào cấu trúc DB (D71, D76) KHÔNG có trường: không có chỗ nào để tắt chúng."""
import shlex
from dataclasses import asdict, dataclass, fields

from tram.nho.bi_mat import quet

DO_DAI_LENH = 500
KHOA_CUNG = ("qc", "kiem_lai", "schema")
TEN_LENH = {"lenh_deploy": "Lệnh deploy", "lenh_kiem_song": "Lệnh kiểm còn sống", "lenh_lui": "Lệnh lùi"}
TRUONG_LENH = tuple(TEN_LENH)


@dataclass(frozen=True)
class CaiDatTuDong:
    tu_merge: bool = False          # D69: mặc định tắt
    tu_deploy: bool = False         # D74: mặc định tắt
    dk_ci: bool = True              # ba nút điều kiện có nút (D70), mặc định bật
    dk_cot: bool = True
    dk_hang_rao: bool = True
    lenh_deploy: str = ""           # D73: trống = chưa khai
    lenh_kiem_song: str = ""
    lenh_lui: str = ""

    @property
    def du_lenh(self) -> bool:
        return all(getattr(self, t) for t in TRUONG_LENH)

    def phang(self) -> dict:
        return asdict(self)


MAC_DINH = CaiDatTuDong()
_TEN = tuple(f.name for f in fields(CaiDatTuDong))


def tu_phang(d: dict) -> CaiDatTuDong:
    """Đọc từ sự kiện: khoá lạ bỏ qua, khoá thiếu lấy mặc định — mã cũ đọc được sự kiện mới và ngược lại."""
    return CaiDatTuDong(**{k: v for k, v in d.items() if k in _TEN})


def sang_api(cd: CaiDatTuDong) -> dict:
    return {"tu_merge": cd.tu_merge, "tu_deploy": cd.tu_deploy,
            "dieu_kien": {"ci": cd.dk_ci, "cot": cd.dk_cot, "hang_rao": cd.dk_hang_rao},
            "lenh": {"deploy": cd.lenh_deploy, "kiem_song": cd.lenh_kiem_song, "lui": cd.lenh_lui}}


def tu_api(d: dict) -> CaiDatTuDong:
    """`d` đã qua kiểm thân yêu cầu (đủ khoá, đúng kiểu, không khoá lạ). Lệnh bỏ khoảng trắng hai đầu."""
    dk, ln = d["dieu_kien"], d["lenh"]
    return CaiDatTuDong(d["tu_merge"], d["tu_deploy"], dk["ci"], dk["cot"], dk["hang_rao"],
                        ln["deploy"].strip(), ln["kiem_song"].strip(), ln["lui"].strip())


def truong_doi(cu: CaiDatTuDong, moi: CaiDatTuDong) -> list[str]:
    return [t for t in _TEN if getattr(cu, t) != getattr(moi, t)]


def loi_lenh(lenh: str) -> str | None:
    """Lý do từ chối một lệnh — câu hằng, KHÔNG chép lệnh (INV-001); None = được. Trống = chưa khai (được)."""
    if not lenh:
        return None
    if len(lenh) > DO_DAI_LENH:
        return f"Lệnh dài quá {DO_DAI_LENH} ký tự"
    if any(ord(c) < 32 or ord(c) == 127 for c in lenh):
        return "Lệnh có ký tự điều khiển (xuống dòng, tab…)"
    try:
        argv = shlex.split(lenh)
    except ValueError:
        return "Lệnh không tách được thành các đối số (thiếu dấu nháy?)"
    if not argv or not argv[0]:
        return "Lệnh rỗng"
    if quet([lenh]):
        return "Lệnh có vẻ chứa bí mật — để bí mật ngoài lệnh"
    return None


def loi_cai_dat(cd: CaiDatTuDong, *, bat_ghi: bool) -> str | None:
    """Kiểm khi Đại ca lưu (422 khi khác None). `bat_ghi: false` không bật được công tắc nào (INV-005);
    tự deploy cần đủ 3 lệnh (D73)."""
    for t in TRUONG_LENH:
        if (loi := loi_lenh(getattr(cd, t))) is not None:
            return f"{TEN_LENH[t]}: {loi}"
    if not bat_ghi and (cd.tu_merge or cd.tu_deploy):
        return "Dự án chỉ quét thử (bat_ghi: false) — không bật được tự merge, tự deploy"
    if cd.tu_deploy and not cd.du_lenh:
        return "Chưa khai đủ 3 lệnh — không bật được tự deploy"
    return None
```

- [ ] **Step 4: Chạy, mong đợi XANH**

```bash
tests/chan_host/chay.sh -q tests/test_tu_dong_cai_dat.py tests/test_vong_import.py tests/test_do_dai_ma.py
```
Xanh thật: `27 passed in 0.56s` (lệnh trên), nhật ký chặn 0 dòng mới.

Rồi cả bộ: `tests/chan_host/chay.sh -q` → mong đợi `3341 passed` (N₀ + test mới tới task này — số tính; số đo thật ở Task 8 Step 2), nhật ký chặn 0 dòng mới.

- [ ] **Step 5: Commit**

```bash
git add tram/tu_dong/__init__.py tram/tu_dong/cai_dat.py tests/test_tu_dong_cai_dat.py
git commit -m "feat(tu-dong): mô hình cài đặt tự merge/tự deploy, kiểm lệnh khi lưu (TM-1 Task 1)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

### Task 2: Lưu cài đặt và TẠM DỪNG bằng sự kiện (D88, design D-4)

**Scenario:** "Giá trị mặc định" (đọc), "Xem lịch sử đổi"; trạm khởi động lại vẫn giữ; "Tạm dừng rồi tiếp tục" (lưu); ghi của trạm không đè ghi của Đại ca.

**Interfaces:** như mục hợp đồng `tram.tu_dong.luu`; `KhoSuKien.db -> sqlite3.Connection` (thuộc tính mới, trả kết nối có sẵn).

- [ ] **Step 1: Viết test**

Tạo mới `tests/test_tu_dong_luu.py` (nguyên văn):

```python
"""TM-1: cài đặt tự động và TẠM DỪNG lưu bằng sự kiện trong kho sự kiện (D88, design D-4) — không bảng mới; đọc–so–ghi
trong một giao dịch `BEGIN IMMEDIATE` để ghi của trạm (tiến trình khác) không đè ghi của Đại ca. Hàm nhận kết nối của
`KhoSuKien` (tram-api) lẫn `KhoPhieu` (tiến trình giao việc của TM-2, TM-3)."""
import sqlite3
from dataclasses import replace

import pytest

from tram.phieu.kho import KhoPhieu
from tram.su_kien.kho import KhoSuKien
from tram.thao_tac.loi import XungDot
from tram.tu_dong.cai_dat import MAC_DINH
from tram.tu_dong.luu import (DU_AN_TRAM, LOAI_CAI_DAT, doc_cai_dat, doc_trang_thai, doi_cai_dat, ghi_tam_dung,
                              giao_dich, lich_su_doi, tam_dung_cua)

BAT = replace(MAC_DINH, tu_merge=True)


def _db(tmp_path):
    return KhoSuKien(tmp_path / "sk.db").db


def test_chua_chinh_thi_mac_dinh_phien_ban_0(tmp_path):
    assert doc_cai_dat(_db(tmp_path), "repo-nhap") == (MAC_DINH, "0")


def test_ghi_roi_doc_lai_sau_khi_khoi_dong_lai(tmp_path):
    k = KhoSuKien(tmp_path / "sk.db")
    id_ = doi_cai_dat(k.db, "repo-nhap", lambda _: BAT, tac_nhan="dai-ca/dashboard", expected="0",
                      them={"ma_thao_tac": "ma-cd-0001"})
    k.close()
    k2 = KhoSuKien(tmp_path / "sk.db")                          # trạm khởi động lại: kho mới, cùng file
    assert doc_cai_dat(k2.db, "repo-nhap") == (BAT, str(id_))
    s = k2.gan_day("repo-nhap", LOAI_CAI_DAT, 1)[0]
    assert s.tac_nhan == "dai-ca/dashboard" and s.bead_id is None and s.id == id_
    assert s.du_lieu == {"cai_dat": BAT.phang(), "doi": ["tu_merge"], "ma_thao_tac": "ma-cd-0001"}
    assert doc_cai_dat(k2.db, "hr-codex") == (MAC_DINH, "0")   # dự án khác không đổi


def test_phien_ban_cu_thi_xung_dot_va_khong_ghi(tmp_path):
    db = _db(tmp_path)
    doi_cai_dat(db, "repo-nhap", lambda _: BAT, tac_nhan="dai-ca/dashboard", expected="0")
    with pytest.raises(XungDot, match="đã đổi"):
        doi_cai_dat(db, "repo-nhap", lambda c: replace(c, lenh_deploy="a.sh"), tac_nhan="dai-ca/dashboard",
                    expected="0")
    assert db.execute("SELECT COUNT(*) FROM su_kien").fetchone()[0] == 1 and not db.in_transaction


def test_khong_doi_gi_thi_khong_ghi(tmp_path):
    db = _db(tmp_path)
    assert doi_cai_dat(db, "repo-nhap", lambda c: c, tac_nhan="dai-ca/dashboard", expected="0") is None
    assert db.execute("SELECT COUNT(*) FROM su_kien").fetchone()[0] == 0


def test_ghi_cua_tram_ap_tren_ban_moi_nhat_qua_kho_phieu(tmp_path):
    """TM-3 tự tắt tự deploy (tiến trình giao việc, `KhoPhieu.db`, expected=None) không làm mất thay đổi Đại ca vừa
    ghi qua `KhoSuKien.db` — kể cả khi gọi bên trong `KhoPhieu.giao_dich()` của người gọi."""
    k, kp = KhoSuKien(tmp_path / "sk.db"), KhoPhieu(tmp_path / "sk.db")
    doi_cai_dat(k.db, "repo-nhap", lambda _: replace(BAT, tu_deploy=True), tac_nhan="dai-ca/dashboard", expected="0")
    doi_cai_dat(k.db, "repo-nhap", lambda c: replace(c, tu_merge=False), tac_nhan="dai-ca/dashboard",
                expected=doc_cai_dat(k.db, "repo-nhap")[1])
    with kp.giao_dich():
        doi_cai_dat(kp.db, "repo-nhap", lambda c: replace(c, tu_deploy=False), tac_nhan="tram/tu-deploy",
                    them={"ly_do": "hong-3-lan"})
        assert ghi_tam_dung(kp.db, "repo-nhap", tam_dung=True, tac_nhan="tram/tu-deploy", them={"ly_do": "lui-hong"})
    cd, _ = doc_cai_dat(k.db, "repo-nhap")
    assert (cd.tu_merge, cd.tu_deploy) == (False, False) and tam_dung_cua(k.db, "repo-nhap").ly_do == "lui-hong"
    assert k.gan_day("repo-nhap", LOAI_CAI_DAT, 1)[0].du_lieu["ly_do"] == "hong-3-lan"


def test_giao_dich_loi_thi_khong_ghi_gi(tmp_path):
    db = _db(tmp_path)

    def hong(_):
        raise RuntimeError("giữa giao dịch")
    with pytest.raises(RuntimeError):
        doi_cai_dat(db, "repo-nhap", hong, tac_nhan="dai-ca/dashboard")
    assert not db.in_transaction and db.execute("SELECT COUNT(*) FROM su_kien").fetchone()[0] == 0
    doi_cai_dat(db, "repo-nhap", lambda _: BAT, tac_nhan="dai-ca/dashboard")      # kết nối vẫn dùng được


def test_giao_dich_giu_khoa_ghi_voi_tien_trinh_khac(tmp_path):
    db = _db(tmp_path)
    khac = sqlite3.connect(tmp_path / "sk.db", timeout=0.1)
    with giao_dich(db):
        with pytest.raises(sqlite3.OperationalError, match="locked"):
            khac.execute("BEGIN IMMEDIATE")
    khac.execute("BEGIN IMMEDIATE")
    khac.rollback()


def test_lich_su_doi_hai_dong_moi_nhat_truoc(tmp_path):
    """Scenario "Xem lịch sử đổi": bật rồi tắt → hai dòng, ai đổi, giờ, trước/sau."""
    db = _db(tmp_path)
    doi_cai_dat(db, "repo-nhap", lambda _: BAT, tac_nhan="dai-ca/dashboard")
    doi_cai_dat(db, "repo-nhap", lambda _: MAC_DINH, tac_nhan="dai-ca/dashboard")
    ls = lich_su_doi(db, "repo-nhap")
    assert [d["doi"] for d in ls] == [[{"truong": "tu_merge", "truoc": True, "sau": False}],
                                      [{"truong": "tu_merge", "truoc": False, "sau": True}]]
    assert {d["tac_nhan"] for d in ls} == {"dai-ca/dashboard"} and all(d["luc"] for d in ls)
    assert lich_su_doi(db, "repo-nhap", gioi_han=1) == ls[:1]                # dòng cũ nhất bị cắt vẫn so đúng bản trước


def test_tam_dung_du_an_va_toan_tram_doc_lap(tmp_path):
    db = _db(tmp_path)
    assert tam_dung_cua(db, "repo-nhap") is None
    assert ghi_tam_dung(db, "repo-nhap", tam_dung=True, tac_nhan="dai-ca/dashboard", them={"ma_thao_tac": "m1-aaaa"})
    assert not ghi_tam_dung(db, "repo-nhap", tam_dung=True, tac_nhan="dai-ca/dashboard")      # đã tạm dừng: không ghi
    td = tam_dung_cua(db, "repo-nhap")
    assert td.boi == "dai-ca/dashboard" and td.luc and td.ly_do == ""
    assert tam_dung_cua(db, DU_AN_TRAM) is None and tam_dung_cua(db, "hr-codex") is None
    ghi_tam_dung(db, DU_AN_TRAM, tam_dung=True, tac_nhan="tram/tu-deploy", them={"ly_do": "lui-hong"})
    assert tam_dung_cua(db, DU_AN_TRAM).ly_do == "lui-hong"
    assert ghi_tam_dung(db, "repo-nhap", tam_dung=False, tac_nhan="dai-ca/dashboard")
    assert tam_dung_cua(db, "repo-nhap") is None and not ghi_tam_dung(db, "hr-codex", tam_dung=False, tac_nhan="x")
    assert [h[0] for h in db.execute("SELECT loai FROM su_kien ORDER BY id")] == [
        "tu_dong.tam_dung", "tu_dong.tam_dung", "tu_dong.tiep_tuc"]


def test_doc_trang_thai_gom_mot_lan(tmp_path):
    db = _db(tmp_path)
    doi_cai_dat(db, "repo-nhap", lambda _: BAT, tac_nhan="dai-ca/dashboard")
    ghi_tam_dung(db, DU_AN_TRAM, tam_dung=True, tac_nhan="dai-ca/dashboard")
    tt = doc_trang_thai(db, "repo-nhap")
    assert tt.cai_dat == BAT and tt.phien_ban == doc_cai_dat(db, "repo-nhap")[1]
    assert tt.tam_dung_du_an is None and tt.tam_dung_tram.boi == "dai-ca/dashboard"
```

- [ ] **Step 2: Chạy, mong đợi ĐỎ**

```bash
tests/chan_host/chay.sh -q tests/test_tu_dong_luu.py
```
Đỏ thật: `ERROR tests/…` khi thu thập — `ModuleNotFoundError: No module named 'tram.tu_dong.luu'` (`1 error in 0.11s`, thoát 2), nhật ký chặn 0 dòng mới.

- [ ] **Step 3: Viết mã**

Sửa `tram/su_kien/kho.py` (bản vá, áp bằng `git apply`):

```diff
diff --git a/tram/su_kien/kho.py b/tram/su_kien/kho.py
index 195f23c..9e739b3 100644
--- a/tram/su_kien/kho.py
+++ b/tram/su_kien/kho.py
@@ -1,4 +1,5 @@
 import json
+import sqlite3
 from collections.abc import Callable
 from pathlib import Path
 
@@ -21,6 +22,11 @@ class KhoSuKien:
         self._db.executescript(LUOC_DO)
         self.yeu_cau = YeuCauChamLai(self._db)
 
+    @property
+    def db(self) -> sqlite3.Connection:
+        """Kết nối thô, như `KhoPhieu.db` — `tram/tu_dong/luu.py` đọc/ghi trong giao dịch của riêng nó (TM-1)."""
+        return self._db
+
     def ghi(self, du_an: str, loai: str, du_lieu: dict, *, bead_id: str | None = None,
             tac_nhan: str = "tram/cham-cot", token_vao: int | None = None,
             token_ra: int | None = None, mo_hinh: str | None = None,
```

Tạo mới `tram/tu_dong/luu.py` (nguyên văn):

```python
"""Lưu cài đặt tự động và TẠM DỪNG bằng sự kiện trong kho sự kiện (D88, design D-4) — không bảng mới, không YAML.

`tu_dong.cai_dat` mang TOÀN BỘ cài đặt sau khi đổi (`cai_dat`) + tên các trường đổi (`doi`); giá trị hiện hành =
sự kiện mới nhất của dự án, phiên bản = id của nó ("0" khi chưa có). `tu_dong.tam_dung` / `tu_dong.tiep_tuc` trên
dự án, hoặc trên `_tram` cho toàn trạm; trạng thái = sự kiện mới nhất trong hai loại.

Mọi hàm nhận KẾT NỐI `su-kien.db`: `KhoSuKien.db` (tram-api) hay `KhoPhieu.db` (tiến trình giao việc — TM-2, TM-3).
Ghi: đọc–so–ghi trong một `BEGIN IMMEDIATE` (`giao_dich`) nên ghi của trạm không đè ghi của Đại ca và ngược lại;
gọi khi đang trong giao dịch của người gọi thì nhập vào giao dịch đó (người gọi commit)."""
import json
import sqlite3
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass

from tram.duong_dan import bay_gio
from tram.su_kien.ghi_trong import ghi_trong_giao_dich
from tram.thao_tac.loi import XungDot
from tram.tu_dong.cai_dat import MAC_DINH, CaiDatTuDong, truong_doi, tu_phang

DU_AN_TRAM = "_tram"
LOAI_CAI_DAT = "tu_dong.cai_dat"
LOAI_TAM_DUNG, LOAI_TIEP_TUC = "tu_dong.tam_dung", "tu_dong.tiep_tuc"


@dataclass(frozen=True)
class TamDung:
    boi: str            # tác nhân: dai-ca/dashboard | tram/...
    luc: str
    ly_do: str          # mã của trạm (vd lui-hong); "" khi Đại ca bấm


@dataclass(frozen=True)
class TrangThaiTuDong:
    cai_dat: CaiDatTuDong
    phien_ban: str
    tam_dung_du_an: TamDung | None
    tam_dung_tram: TamDung | None


@contextmanager
def giao_dich(db: sqlite3.Connection) -> Iterator[sqlite3.Connection]:
    if db.in_transaction:                       # trong giao dịch của người gọi (vd `KhoPhieu.giao_dich()`)
        yield db
        return
    db.execute("BEGIN IMMEDIATE")
    try:
        yield db
    except BaseException:
        db.execute("ROLLBACK")
        raise
    db.execute("COMMIT")


def _moi_nhat(db: sqlite3.Connection, du_an: str, *loai: str) -> tuple | None:
    return db.execute(f"SELECT id, loai, luc, tac_nhan, du_lieu FROM su_kien WHERE du_an=? AND loai IN"
                      f" ({','.join('?' * len(loai))}) ORDER BY id DESC LIMIT 1", (du_an, *loai)).fetchone()


def doc_cai_dat(db: sqlite3.Connection, du_an: str) -> tuple[CaiDatTuDong, str]:
    h = _moi_nhat(db, du_an, LOAI_CAI_DAT)
    return (tu_phang(json.loads(h[4])["cai_dat"]), str(h[0])) if h else (MAC_DINH, "0")


def doi_cai_dat(db: sqlite3.Connection, du_an: str, doi: Callable[[CaiDatTuDong], CaiDatTuDong], *, tac_nhan: str,
                expected: str | None = None, them: dict | None = None) -> int | None:
    """Đọc bản mới nhất, áp `doi`, ghi nếu khác — cùng một giao dịch. `expected` (Đại ca) khác phiên bản hiện hành →
    `XungDot`; trạm truyền `expected=None` (áp lên bản mới nhất). Trả id sự kiện mới, None khi không có gì đổi."""
    with giao_dich(db):
        cu, pb = doc_cai_dat(db, du_an)
        if expected is not None and expected != pb:
            raise XungDot(f"Cài đặt tự động của {du_an} đã đổi (hiện {pb}, đang xem {expected}) — tải lại")
        moi = doi(cu)
        if not (ds := truong_doi(cu, moi)):
            return None
        return ghi_trong_giao_dich(db, du_an, LOAI_CAI_DAT, {**(them or {}), "cai_dat": moi.phang(), "doi": ds},
                                   tac_nhan=tac_nhan, luc=bay_gio())


def lich_su_doi(db: sqlite3.Connection, du_an: str, gioi_han: int = 20) -> list[dict]:
    """Mới → cũ; mỗi dòng: lúc, tác nhân, các trường đổi kèm giá trị trước/sau (so hai bản liền nhau)."""
    ds = db.execute("SELECT luc, tac_nhan, du_lieu FROM su_kien WHERE du_an=? AND loai=? ORDER BY id DESC LIMIT ?",
                    (du_an, LOAI_CAI_DAT, gioi_han + 1)).fetchall()[::-1]
    truoc = tu_phang(json.loads(ds.pop(0)[2])["cai_dat"]) if len(ds) > gioi_han else MAC_DINH
    ra = []
    for luc, tac_nhan, du_lieu in ds:
        sau = tu_phang(json.loads(du_lieu)["cai_dat"])
        ra.append({"luc": luc, "tac_nhan": tac_nhan, "doi": [
            {"truong": t, "truoc": getattr(truoc, t), "sau": getattr(sau, t)} for t in truong_doi(truoc, sau)]})
        truoc = sau
    return ra[::-1]


def tam_dung_cua(db: sqlite3.Connection, du_an: str) -> TamDung | None:
    h = _moi_nhat(db, du_an, LOAI_TAM_DUNG, LOAI_TIEP_TUC)
    if h is None or h[1] != LOAI_TAM_DUNG:
        return None
    return TamDung(h[3], h[2], str(json.loads(h[4]).get("ly_do") or ""))


def ghi_tam_dung(db: sqlite3.Connection, du_an: str, *, tam_dung: bool, tac_nhan: str,
                 them: dict | None = None) -> bool:
    """`du_an` = tên dự án hoặc `DU_AN_TRAM`. Đã ở đúng trạng thái → không ghi, trả False."""
    with giao_dich(db):
        if (tam_dung_cua(db, du_an) is not None) == tam_dung:
            return False
        ghi_trong_giao_dich(db, du_an, LOAI_TAM_DUNG if tam_dung else LOAI_TIEP_TUC, dict(them or {}),
                            tac_nhan=tac_nhan, luc=bay_gio())
        return True


def doc_trang_thai(db: sqlite3.Connection, du_an: str) -> TrangThaiTuDong:
    cd, pb = doc_cai_dat(db, du_an)
    return TrangThaiTuDong(cd, pb, tam_dung_cua(db, du_an), tam_dung_cua(db, DU_AN_TRAM))
```

- [ ] **Step 4: Chạy, mong đợi XANH**

```bash
tests/chan_host/chay.sh -q tests/test_tu_dong_luu.py tests/test_su_kien.py tests/test_vong_import.py tests/test_do_dai_ma.py
```
Xanh thật: `25 passed in 0.77s` (lệnh trên), nhật ký chặn 0 dòng mới.

Rồi cả bộ: `tests/chan_host/chay.sh -q` → mong đợi `3351 passed` (N₀ + test mới tới task này — số tính; số đo thật ở Task 8 Step 2), nhật ký chặn 0 dòng mới.

- [ ] **Step 5: Commit**

```bash
git add tram/su_kien/kho.py tram/tu_dong/luu.py tests/test_tu_dong_luu.py
git commit -m "feat(tu-dong): lưu cài đặt và tạm dừng bằng sự kiện, ghi trong BEGIN IMMEDIATE (TM-1 Task 2)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

### Task 3: Khoá chung trước thao tác tự động và đường cấm từ ba lệnh (D89)

**Scenario:** "Estop bật" (phần khoá), "Deploy tay khi dự án tạm dừng" (phần khoá), "Dự án chưa khai lệnh lùi" (khoá `thieu_lenh`), "Agent sửa script deploy" (phần hàm tính — nối vào kiểm đường cấm ở TM-3).

**Interfaces:** như mục hợp đồng `tram.tu_dong.khoa`, `tram.tu_dong.file_cam`.

- [ ] **Step 1: Viết test**

Tạo mới `tests/test_tu_dong_khoa.py` (nguyên văn):

```python
"""TM-1: hai hàm tính cho lát sau — khoá chung trước mọi thao tác tự động (design D-2 năm dòng đầu, D-9, D97) và
đường dẫn cấm sinh từ ba lệnh (D89). Hàm thuần."""
import posixpath
from dataclasses import replace

import pytest

from tram.kiem.duong_dan_cam import duong_dan_cham_cam
from tram.tu_dong.cai_dat import MAC_DINH
from tram.tu_dong.file_cam import duong_dan_tu_lenh
from tram.tu_dong.khoa import NHAN_LY_DO, VIEC, ly_do_chan
from tram.tu_dong.luu import TamDung, TrangThaiTuDong

DU = replace(MAC_DINH, tu_merge=True, tu_deploy=True, lenh_deploy="d.sh", lenh_kiem_song="k.sh", lenh_lui="l.sh")
TD = TamDung("dai-ca/dashboard", "2026-10-18T02:00:00Z", "")


def _tt(cd=DU, du_an=None, tram=None):
    return TrangThaiTuDong(cd, "7", du_an, tram)


def test_du_dieu_kien_thi_khong_chan():
    for viec in VIEC:
        assert ly_do_chan(_tt(), viec=viec, bat_ghi=True, estop_bat=False) == []


def test_thu_tu_ly_do_estop_truoc_cong_tac_sau():
    tat = _tt(MAC_DINH, TD, TD)
    assert ly_do_chan(tat, viec="merge", bat_ghi=False, estop_bat=True) == [
        "estop", "tam_dung_tram", "tam_dung_du_an", "bat_ghi", "tu_merge_tat"]
    assert ly_do_chan(tat, viec="deploy", bat_ghi=False, estop_bat=True) == [
        "estop", "tam_dung_tram", "tam_dung_du_an", "bat_ghi", "tu_deploy_tat", "thieu_lenh"]


def test_tung_cong_tac_chi_chan_viec_cua_no():
    assert ly_do_chan(_tt(replace(DU, tu_merge=False)), viec="deploy", bat_ghi=True, estop_bat=False) == []
    assert ly_do_chan(_tt(replace(DU, tu_deploy=False)), viec="merge", bat_ghi=True, estop_bat=False) == []
    assert ly_do_chan(_tt(replace(DU, lenh_lui="")), viec="merge", bat_ghi=True, estop_bat=False) == []
    assert ly_do_chan(_tt(replace(DU, lenh_lui="")), viec="deploy", bat_ghi=True, estop_bat=False) == ["thieu_lenh"]


def test_deploy_tay_duoc_khi_tam_dung_khoa_khi_estop():
    """D97: nút Deploy của Đại ca bấm được khi dự án (hay toàn trạm) tạm dừng, công tắc tắt; khoá khi Estop."""
    tt = _tt(replace(DU, tu_merge=False, tu_deploy=False), TD, TD)
    assert ly_do_chan(tt, viec="deploy_tay", bat_ghi=True, estop_bat=False) == []
    assert ly_do_chan(tt, viec="deploy_tay", bat_ghi=True, estop_bat=True) == ["estop"]
    assert ly_do_chan(_tt(MAC_DINH), viec="deploy_tay", bat_ghi=False, estop_bat=False) == ["bat_ghi", "thieu_lenh"]


def test_viec_la_va_nhan_du():
    with pytest.raises(ValueError):
        ly_do_chan(_tt(), viec="xoa", bat_ghi=True, estop_bat=False)
    assert set(NHAN_LY_DO) == {"estop", "tam_dung_tram", "tam_dung_du_an", "bat_ghi", "tu_merge_tat",
                               "tu_deploy_tat", "thieu_lenh"}


GOC = "/Users/Shared/repo-rn"                                        # gốc repo đáng tin của bên gọi (giả)
CO = {"scripts/deploy.sh": "file", "deploy/cau-hinh.yml": "file", "deploy": "dir", "scripts": "dir"}


def _repo(tok: str) -> tuple[str, str] | None:
    """Callback mẫu như TM-2/TM-3 dựng (hợp đồng D89): nhận token nguyên văn, chuẩn hoá từ gốc repo; ngoài gốc (kể cả
    thoát bằng `..`) hay chính gốc → None; có trong repo → (đường dẫn tương đối, loại)."""
    p = posixpath.normpath(tok if tok.startswith("/") else posixpath.join(GOC, tok))
    rel = p[len(GOC) + 1:] if p.startswith(GOC + "/") else ""
    return (rel, CO[rel]) if rel in CO else None


def test_duong_dan_cam_tu_ba_lenh():
    """Scenario "Agent sửa script deploy": file trong repo mà lệnh nhắc tới → mẫu cấm; thư mục → `thu-muc/**`. Tập
    bắt buộc (Codex C2): bên gọi kiểm nó KHÔNG kèm `cho_phep` — như dòng cuối."""
    cd = replace(MAC_DINH, lenh_deploy="sh ./scripts/deploy.sh --cau-hinh=deploy/cau-hinh.yml",
                 lenh_kiem_song="curl -fsS https://x.vn/song", lenh_lui="./deploy lui")
    them = duong_dan_tu_lenh(cd, _repo)
    assert them == ("deploy/**", "deploy/cau-hinh.yml", "scripts/deploy.sh")
    assert duong_dan_cham_cam(["scripts/deploy.sh", "deploy/a/b.sh", "src/app.py"], them=them) == [
        "deploy/a/b.sh", "scripts/deploy.sh"]


@pytest.mark.parametrize("lenh,mong", [
    (f"{GOC}/scripts/deploy.sh", ("scripts/deploy.sh",)),
    (f"bash --tep={GOC}/scripts/deploy.sh", ("scripts/deploy.sh",)),
    (f"{GOC}/deploy/../scripts/deploy.sh", ("scripts/deploy.sh",)),
    ("sh scripts/../deploy/cau-hinh.yml", ("deploy/cau-hinh.yml",)),
    (f"make -C {GOC}/deploy", ("deploy/**",)),
])
def test_duong_dan_tuyet_doi_hoac_vong_trong_repo_bi_cam(lenh, mong):
    """Codex Q1: gọi thẳng `/…/repo/scripts/deploy.sh` (hay vòng qua `..` mà vẫn trong repo) vẫn bảo vệ file đó."""
    assert duong_dan_tu_lenh(replace(MAC_DINH, lenh_deploy=lenh), _repo) == mong


@pytest.mark.parametrize("lenh", ["/Users/Shared/tram-deploy/deploy.sh", f"{GOC}-khac/scripts/deploy.sh",
                                  "sh ../scripts/deploy.sh", f"sh {GOC}/../repo-cu/scripts/deploy.sh", f"sh {GOC}",
                                  "~/deploy.sh", "sh scripts/*.sh", "sh -x", "sh 'thieu nhay", ""])
def test_bo_qua_token_ngoai_repo_hoac_la(lenh):
    """Tuyệt đối ngoài repo, `..` thoát gốc, chính gốc repo → callback trả None; `~`, glob, cờ, rỗng → không hỏi."""
    nhin = []
    assert duong_dan_tu_lenh(replace(MAC_DINH, lenh_deploy=lenh),
                             lambda p: nhin.append(p) or _repo(p)) == ()
    assert not any(not p or p.startswith(("~", "-")) or set(p) & set("*?[") for p in nhin)


def test_token_nguyen_van_toi_callback():
    """Hợp đồng D89: `file_cam` không tự bỏ đường tuyệt đối hay `..` — callback (biết gốc repo) quyết."""
    nhin = []
    duong_dan_tu_lenh(replace(MAC_DINH, lenh_deploy="/x/a.sh ../b.sh --f=/y/c ./d"), lambda p: nhin.append(p))
    assert nhin == ["/x/a.sh", "../b.sh", "/y/c", "./d"]


def test_ket_qua_callback_la_bi_bo():
    """Callback trả dạng lạ (gốc rỗng, tuyệt đối, `..`, chưa chuẩn hoá, loại khác) → không sinh mẫu nào."""
    for kq in [("", "dir"), ("/etc/x", "file"), ("../x", "file"), ("a/./b", "file"), ("a", "link"), "a", ("a",)]:
        assert duong_dan_tu_lenh(replace(MAC_DINH, lenh_deploy="a"), lambda p, kq=kq: kq) == ()
```

- [ ] **Step 2: Chạy, mong đợi ĐỎ**

```bash
tests/chan_host/chay.sh -q tests/test_tu_dong_khoa.py
```
Đỏ thật: `ERROR tests/…` khi thu thập — `ModuleNotFoundError: No module named 'tram.tu_dong.file_cam'` (`1 error in 0.07s`, thoát 2), nhật ký chặn 0 dòng mới.

- [ ] **Step 3: Viết mã**

Tạo mới `tram/tu_dong/khoa.py` (nguyên văn):

```python
"""Khoá chung trước mọi thao tác tự động (design D-2 năm dòng đầu, D-9, D97; INV-004, INV-005) — hàm thuần.

TM-2 (tự merge) và TM-3 (tự deploy, nút Deploy) đọc `doc_trang_thai` + `estop.dang_bat()` + `bat_ghi` NGAY TRƯỚC
lệnh rồi gọi hàm này; danh sách rỗng mới được làm. Thứ tự lý do cố định: estop → tạm dừng toàn trạm → tạm dừng dự
án → `bat_ghi` → công tắc → đủ 3 lệnh. Mã lý do là hợp đồng với dashboard (nhãn ở `NHAN_LY_DO`)."""
from tram.tu_dong.luu import TrangThaiTuDong

VIEC = ("merge", "deploy", "deploy_tay")
NHAN_LY_DO = {"estop": "Estop đang bật", "tam_dung_tram": "Tự merge · tự deploy đang tạm dừng toàn trạm",
              "tam_dung_du_an": "Dự án đang tạm dừng", "bat_ghi": "Dự án chỉ quét thử (bat_ghi: false)",
              "tu_merge_tat": "Công tắc tự merge tắt", "tu_deploy_tat": "Tự deploy tắt",
              "thieu_lenh": "Chưa khai đủ 3 lệnh"}


def ly_do_chan(tt: TrangThaiTuDong, *, viec: str, bat_ghi: bool, estop_bat: bool) -> list[str]:
    """`merge`: tự merge (cả PR spec D95). `deploy`: tự deploy sau tự merge. `deploy_tay`: nút Deploy của Đại ca —
    không xét tạm dừng, công tắc (D97), vẫn khoá khi estop, `bat_ghi: false`, thiếu lệnh (D73)."""
    if viec not in VIEC:
        raise ValueError(f"việc không hợp lệ: {viec!r}")
    tu_dong, cd = viec != "deploy_tay", tt.cai_dat
    co = (("estop", estop_bat),
          ("tam_dung_tram", tu_dong and tt.tam_dung_tram is not None),
          ("tam_dung_du_an", tu_dong and tt.tam_dung_du_an is not None),
          ("bat_ghi", not bat_ghi),
          ("tu_merge_tat", viec == "merge" and not cd.tu_merge),
          ("tu_deploy_tat", viec == "deploy" and not cd.tu_deploy),
          ("thieu_lenh", viec != "merge" and not cd.du_lenh))
    return [ma for ma, chan in co if chan]
```

Tạo mới `tram/tu_dong/file_cam.py` (nguyên văn):

```python
"""D89: file trong repo dự án mà ba lệnh nhắc tới thành đường dẫn cấm hiệu lực (spec 4 §6.2 bước 0) — hàm tính.
TM-3 cộng kết quả vào `them=` của kiểm đường dẫn cấm; agent sửa file đó → `dong-file-cau-hinh`, không tự merge.
Đây là tập cấm BẮT BUỘC: bên gọi không để ngoại lệ dự án (`cho_phep`) miễn nó (Codex C2).

Hợp đồng (Codex Q1): `loai_trong_repo` nhận token NGUYÊN VĂN (tương đối hay tuyệt đối, kể cả phần sau `=` của
`--x=y`), tự chuẩn hoá từ gốc repo đáng tin (resolve, chặn thoát gốc qua `..`/symlink) và trả (đường dẫn tương đối
POSIX từ gốc, "file" | "dir") hoặc None. Hàm này chỉ bỏ token rỗng, `~…`, cờ `-…`, glob. Còn hở (design Risks):
script gọi tiếp file khác không nhắc trong lệnh, `make` đọc `Makefile` ngầm — khuyên để script deploy ngoài repo."""
import shlex
from collections.abc import Callable
from typing import Literal

from tram.tu_dong.cai_dat import TRUONG_LENH, CaiDatTuDong

KY_TU_GLOB = frozenset("*?[")
LoaiTrongRepo = Callable[[str], tuple[str, Literal["file", "dir"]] | None]


def _ung_vien(tok: str) -> list[str]:
    """Token và phần sau `=` đầu tiên. Đường tuyệt đối, `..` đi tiếp tới callback — chỉ nó biết gốc repo."""
    return [p for p in (tok, tok.split("=", 1)[1] if "=" in tok else "")
            if p and not p.startswith(("~", "-")) and not set(p) & KY_TU_GLOB]


def _mau(kq: object) -> str | None:
    """(rel, loại) → mẫu cấm: file → `rel`, thư mục → `rel/**`. Dạng lạ (gốc rỗng, tuyệt đối, `..`, `.`, loại
    khác) → None: không sinh mẫu sai từ callback hỏng."""
    rel, loai = kq if isinstance(kq, tuple) and len(kq) == 2 else ("", None)
    if not isinstance(rel, str) or loai not in ("file", "dir") or {"", ".", ".."} & set(rel.split("/")):
        return None
    return rel if loai == "file" else f"{rel}/**"


def duong_dan_tu_lenh(cd: CaiDatTuDong, loai_trong_repo: LoaiTrongRepo) -> tuple[str, ...]:
    """Mẫu cấm từ ba lệnh, đã sắp xếp, không trùng. Lệnh không tách được → bỏ qua (khi lưu đã bị từ chối)."""
    ra = set()
    for t in TRUONG_LENH:
        try:
            argv = shlex.split(getattr(cd, t))
        except ValueError:
            continue
        for p in (p for tok in argv for p in _ung_vien(tok)):
            if mau := _mau(loai_trong_repo(p)):
                ra.add(mau)
    return tuple(sorted(ra))
```

- [ ] **Step 4: Chạy, mong đợi XANH**

```bash
tests/chan_host/chay.sh -q tests/test_tu_dong_khoa.py tests/test_vong_import.py tests/test_do_dai_ma.py
```
Xanh thật: `30 passed in 0.58s` (lệnh trên), nhật ký chặn 0 dòng mới.

Rồi cả bộ: `tests/chan_host/chay.sh -q` → mong đợi `3374 passed` (N₀ + test mới tới task này — số tính; số đo thật ở Task 8 Step 2), nhật ký chặn 0 dòng mới.

- [ ] **Step 5: Commit**

```bash
git add tram/tu_dong/khoa.py tram/tu_dong/file_cam.py tests/test_tu_dong_khoa.py
git commit -m "feat(tu-dong): khoá chung trước thao tác tự động, đường cấm từ ba lệnh D89 (TM-1 Task 3)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

### Task 4: Thao tác ghi — lưu cài đặt, TẠM DỪNG / Tiếp tục (idempotent theo mã thao tác)

**Scenario:** "Gửi lại cùng mã thao tác", "Màn hình cũ" (409), "Dự án chỉ quét thử" (422), "Dán token vào lệnh kiểm còn sống" (không lưu, không lịch sử), "Tạm dừng rồi tiếp tục", "Toàn trạm tạm dừng" (phía lưu).

**Interfaces:**
- `luu_cai_dat_thao_tac(kho: KhoSuKien, kho_tt: KhoThaoTac, du_an, cd, *, bat_ghi, ma, expected_version) -> KetQuaThaoTac` — `ket_qua = {"tu_dong.cai_dat": {"phien_ban": str}}`; `KhongHopLe` (422) / `XungDot` (409) trước khi tạo bản ghi `thao_tac`.
- `tam_dung_thao_tac(kho, kho_tt, du_an | DU_AN_TRAM, *, tam_dung, ma, expected_version) -> KetQuaThaoTac` — `ket_qua = {"tu_dong.tam_dung" | "tu_dong.tiep_tuc": bool}`; không kiểm phiên bản.

- [ ] **Step 1: Viết test**

Tạo mới `tests/test_thao_tac_tu_dong.py` (nguyên văn):

```python
"""TM-1: thao tác ghi dashboard của tự merge / tự deploy — lưu cài đặt (kiểm `expected_version`, `bat_ghi`, lệnh),
TẠM DỪNG / Tiếp tục dự án và toàn trạm (không kiểm phiên bản, như estop — D78). Idempotent theo `ma_thao_tac`."""
from dataclasses import replace

import pytest

from tram.su_kien.kho import KhoSuKien
from tram.thao_tac.kho import KhoThaoTac
from tram.thao_tac.loi import KhongHopLe, XungDot
from tram.thao_tac.tu_dong import luu_cai_dat_thao_tac, tam_dung_thao_tac
from tram.tu_dong.cai_dat import MAC_DINH
from tram.tu_dong.luu import DU_AN_TRAM, LOAI_CAI_DAT, doc_cai_dat, tam_dung_cua

BAT = replace(MAC_DINH, tu_merge=True)


def _kho(tmp_path):
    db = tmp_path / "sk.db"
    return KhoSuKien(db), KhoThaoTac(db)


def _luu(k, kt, cd=BAT, *, ma="ma-luu-00001", ev="0", bat_ghi=True):
    return luu_cai_dat_thao_tac(k, kt, "repo-nhap", cd, bat_ghi=bat_ghi, ma=ma, expected_version=ev)


def test_luu_mot_lan_theo_ma(tmp_path):
    """Scenario "Gửi lại cùng mã thao tác": kết quả lần đầu, lịch sử một dòng."""
    k, kt = _kho(tmp_path)
    a = _luu(k, kt)
    b = _luu(k, kt)
    cd, pb = doc_cai_dat(k.db, "repo-nhap")
    assert cd == BAT and a.ket_qua == b.ket_qua == {"tu_dong.cai_dat": {"phien_ban": pb}}
    assert (a.lap_lai, b.lap_lai) == (False, True)
    ds = k.gan_day("repo-nhap", LOAI_CAI_DAT, 10)
    assert len(ds) == 1 and ds[0].tac_nhan == "dai-ca/dashboard" and ds[0].du_lieu["ma_thao_tac"] == "ma-luu-00001"


def test_cung_ma_khac_noi_dung_va_phien_ban_cu_la_xung_dot(tmp_path):
    k, kt = _kho(tmp_path)
    _luu(k, kt)
    with pytest.raises(XungDot):
        _luu(k, kt, MAC_DINH)                                           # cùng mã, nội dung khác
    with pytest.raises(XungDot, match="đã đổi"):
        _luu(k, kt, replace(BAT, dk_ci=False), ma="ma-luu-00002")       # Scenario "Màn hình cũ": phiên bản "0" đã cũ
    assert doc_cai_dat(k.db, "repo-nhap")[0] == BAT and kt.lay("ma-luu-00002") is None    # 409 không để bản ghi treo


def test_khong_doi_gi_tra_phien_ban_hien_hanh(tmp_path):
    k, kt = _kho(tmp_path)
    pb = _luu(k, kt).ket_qua["tu_dong.cai_dat"]["phien_ban"]
    kq = _luu(k, kt, ma="ma-luu-00003", ev=pb)
    assert kq.ket_qua == {"tu_dong.cai_dat": {"phien_ban": pb}} and len(k.gan_day("repo-nhap", LOAI_CAI_DAT, 9)) == 1


@pytest.mark.parametrize("cd, bat_ghi, loi", [
    (BAT, False, "chỉ quét thử"),                                                          # Scenario "Dự án chỉ quét thử"
    (replace(MAC_DINH, tu_deploy=True, lenh_deploy="d.sh"), True, "Chưa khai đủ 3 lệnh"),
    (replace(MAC_DINH, lenh_kiem_song="curl -H 'Authorization: Bearer " + "q8W" * 12 + "' https://x.vn"), True,
     "Lệnh kiểm còn sống: Lệnh có vẻ chứa bí mật — để bí mật ngoài lệnh"),                # Scenario "Dán token…"
])
def test_tu_choi_khong_luu_khong_ghi_thao_tac(tmp_path, cd, bat_ghi, loi):
    k, kt = _kho(tmp_path)
    with pytest.raises(KhongHopLe, match=loi):
        _luu(k, kt, cd, bat_ghi=bat_ghi)
    assert k.gan_day("repo-nhap", LOAI_CAI_DAT, 9) == [] and kt.lay("ma-luu-00001") is None    # không lưu, không lịch sử


def test_tam_dung_tiep_tuc_khong_kiem_phien_ban(tmp_path):
    """Scenario "Tạm dừng rồi tiếp tục": tạm dừng không hỏng vì màn hình cũ; công tắc giữ nguyên."""
    k, kt = _kho(tmp_path)
    _luu(k, kt)
    a = tam_dung_thao_tac(k, kt, "repo-nhap", tam_dung=True, ma="ma-td-000001", expected_version="man-hinh-cu")
    b = tam_dung_thao_tac(k, kt, "repo-nhap", tam_dung=True, ma="ma-td-000001", expected_version="khac")
    assert a.ket_qua == {"tu_dong.tam_dung": True} and b.lap_lai and tam_dung_cua(k.db, "repo-nhap").boi == "dai-ca/dashboard"
    assert k.gan_day("repo-nhap", "tu_dong.tam_dung", 9)[0].du_lieu == {"ma_thao_tac": "ma-td-000001"}
    tam_dung_thao_tac(k, kt, "repo-nhap", tam_dung=False, ma="ma-tt-000001", expected_version="x")
    assert tam_dung_cua(k.db, "repo-nhap") is None and doc_cai_dat(k.db, "repo-nhap")[0] == BAT


def test_tam_dung_toan_tram(tmp_path):
    k, kt = _kho(tmp_path)
    tam_dung_thao_tac(k, kt, DU_AN_TRAM, tam_dung=True, ma="ma-tram-0001", expected_version="")
    assert tam_dung_cua(k.db, DU_AN_TRAM) is not None and tam_dung_cua(k.db, "repo-nhap") is None
    kq = tam_dung_thao_tac(k, kt, DU_AN_TRAM, tam_dung=True, ma="ma-tram-0002", expected_version="")
    assert kq.ket_qua == {"tu_dong.tam_dung": False}                       # đã tạm dừng: không ghi thêm
    assert len(k.gan_day(DU_AN_TRAM, "tu_dong.tam_dung", 9)) == 1
```

- [ ] **Step 2: Chạy, mong đợi ĐỎ**

```bash
tests/chan_host/chay.sh -q tests/test_thao_tac_tu_dong.py
```
Đỏ thật: `ERROR tests/…` khi thu thập — `ModuleNotFoundError: No module named 'tram.thao_tac.tu_dong'` (`1 error in 0.07s`, thoát 2), nhật ký chặn 0 dòng mới.

- [ ] **Step 3: Viết mã**

Tạo mới `tram/thao_tac/tu_dong.py` (nguyên văn):

```python
"""Thao tác ghi dashboard của tự merge / tự deploy (`dieu-khien-tu-dong`, D79, D87, D88): lưu cài đặt, TẠM DỪNG /
Tiếp tục một dự án hoặc toàn trạm (`DU_AN_TRAM`). Idempotent theo `ma_thao_tac` (bảng `thao_tac`); sự kiện mang
`ma_thao_tac`, tác nhân `dai-ca/dashboard`. Lưu cài đặt kiểm `expected_version` = phiên bản cài đặt (409 khi cũ);
tạm dừng / tiếp tục KHÔNG kiểm (như estop — không hỏng vì màn hình cũ, D78). Kênh ghi (D87) kiểm ở tuyến API."""
from tram.thao_tac.chay import KetQuaThaoTac, YeuCau, chay_thao_tac
from tram.thao_tac.chung import TAC_NHAN, co_su_kien
from tram.thao_tac.loi import KhongHopLe, XungDot
from tram.tu_dong.cai_dat import CaiDatTuDong, loi_cai_dat
from tram.tu_dong.luu import LOAI_CAI_DAT, LOAI_TAM_DUNG, LOAI_TIEP_TUC, doc_cai_dat, doi_cai_dat, ghi_tam_dung


def luu_cai_dat_thao_tac(kho, kho_tt, du_an: str, cd: CaiDatTuDong, *, bat_ghi: bool, ma: str,
                         expected_version: str) -> KetQuaThaoTac:
    """Từ chối (422, 409) xảy ra TRƯỚC khi tạo bản ghi `thao_tac`: lệnh bị từ chối không lưu ở đâu cả. Bước ghi vẫn
    so phiên bản lần nữa trong giao dịch (`doi_cai_dat`)."""
    def kiem() -> None:
        if (loi := loi_cai_dat(cd, bat_ghi=bat_ghi)) is not None:
            raise KhongHopLe(loi)
        if (hien := doc_cai_dat(kho.db, du_an)[1]) != expected_version:
            raise XungDot(f"Cài đặt tự động của {du_an} đã đổi (hiện {hien}, đang xem {expected_version}) — tải lại")

    def buoc(_) -> dict:
        if not co_su_kien(kho, du_an, None, LOAI_CAI_DAT, ma):        # crash sau khi ghi: không ghi lần hai
            doi_cai_dat(kho.db, du_an, lambda _cu: cd, tac_nhan=TAC_NHAN, expected=expected_version,
                        them={"ma_thao_tac": ma})
        return {"phien_ban": doc_cai_dat(kho.db, du_an)[1]}

    yc = YeuCau(ma, LOAI_CAI_DAT, du_an, None, {"cai_dat": cd.phang()}, expected_version)
    return chay_thao_tac(kho_tt, yc, kiem_moi=kiem, cac_buoc=[(LOAI_CAI_DAT, buoc)])


def tam_dung_thao_tac(kho, kho_tt, du_an: str, *, tam_dung: bool, ma: str, expected_version: str) -> KetQuaThaoTac:
    """`du_an` = tên dự án hoặc `DU_AN_TRAM`. Kết quả `{loai: True}` khi đã ghi, `False` khi vốn đã ở trạng thái đó."""
    loai = LOAI_TAM_DUNG if tam_dung else LOAI_TIEP_TUC

    def buoc(_) -> bool:
        if co_su_kien(kho, du_an, None, loai, ma):
            return True
        return ghi_tam_dung(kho.db, du_an, tam_dung=tam_dung, tac_nhan=TAC_NHAN, them={"ma_thao_tac": ma})

    yc = YeuCau(ma, loai, du_an, None, {}, expected_version)
    return chay_thao_tac(kho_tt, yc, kiem_moi=lambda: None, cac_buoc=[(loai, buoc)])
```

- [ ] **Step 4: Chạy, mong đợi XANH**

```bash
tests/chan_host/chay.sh -q tests/test_thao_tac_tu_dong.py tests/test_estop_2a.py tests/test_thao_tac_khe.py tests/test_vong_import.py tests/test_do_dai_ma.py
```
Xanh thật: `23 passed in 0.71s` (lệnh trên), nhật ký chặn 0 dòng mới.

Rồi cả bộ: `tests/chan_host/chay.sh -q` → mong đợi `3382 passed` (N₀ + test mới tới task này — số tính; số đo thật ở Task 8 Step 2), nhật ký chặn 0 dòng mới.

- [ ] **Step 5: Commit**

```bash
git add tram/thao_tac/tu_dong.py tests/test_thao_tac_tu_dong.py
git commit -m "feat(thao-tac): lưu cài đặt tự động, tạm dừng/tiếp tục dự án và toàn trạm (TM-1 Task 4)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

### Task 5: Tuyến đọc/ghi qua cửa ghi; kênh `header` chỉ nhận TẠM DỪNG (D79, D87) ⛔ kill list mục 1, 7

**Scenario:** "Thiếu danh tính", "Gửi lại cùng mã thao tác", "Màn hình cũ", "Kênh header", "Tạm dừng vẫn được", "Dán token vào lệnh kiểm còn sống", "Dự án chỉ quét thử", "Yêu cầu tắt điều kiện QC bị từ chối", "Xem lịch sử đổi" (qua API), "Xem khi không phải Đại ca" (phía máy chủ: GET mở, `la_dai_ca` false).

**Interfaces:** như mục hợp đồng "Tuyến"; `tram.suy.tu_dong.{chung, tom_tat_du_an, chi_tiet_du_an, tam_dung_api}`; `tram.api.than.{ThanDieuKien, ThanLenh, ThanCaiDat, ThanCaiDatTuDong}` (`extra="forbid"`).

- [ ] **Step 1: Viết test**

Tạo mới `tests/test_api_tu_dong.py` (nguyên văn):

```python
"""TM-1: tuyến tự merge / tự deploy (dieu-khien-tu-dong, design D-5). GET xem được cho mọi người; POST qua cửa ghi
(`yeu_cau_ghi`) + mã thao tác; kênh `header` (tạm) chỉ nhận TẠM DỪNG (D87); thân yêu cầu không có chỗ cho QC/kiểm
lại/cấu trúc DB (D71, D76); lỗi thân không vọng lại lệnh."""
import pytest

from api_gia import DAI_CA, tao_app_gia
from asgi_gia import goi
from bd_gia import BdGia
from tram.api.kenh_ghi import KenhUnix
from tram.chu import estop

LENH = {"deploy": "/Users/Shared/tram-deploy/repo-nhap/deploy.sh", "kiem_song": "", "lui": ""}
CAI_DAT = {"tu_merge": True, "tu_deploy": False, "dieu_kien": {"ci": True, "cot": True, "hang_rao": True},
           "lenh": LENH}
CD = "/api/du-an/repo-nhap/tu-dong/cai-dat"


def _app(tmp_path, *, unix=True):
    app, pt = tao_app_gia(tmp_path, {"repo-nhap": BdGia(), "hr-codex": BdGia()})
    pt.bat_ghi = lambda ten: ten == "repo-nhap"
    if unix:
        app.state.kenh_ghi = "unix-socket"
        return KenhUnix(app), pt
    return app, pt


def _than(ma="ma-api-td-001", ev="0", **cai_dat):
    return {"ma_thao_tac": ma, "expected_version": ev, "cai_dat": {**CAI_DAT, **cai_dat}}


def _xem(app, ten="repo-nhap", **kw):
    return goi(app, "GET", f"/api/du-an/{ten}/tu-dong", **kw).json()


def test_xem_mac_dinh_ai_cung_xem_duoc(tmp_path):
    app, _ = _app(tmp_path, unix=False)
    tt = goi(app, "GET", "/api/tu-dong").json()
    assert tt["chi_tam_dung"] is True and tt["kenh_ghi"] == "header" and tt["la_dai_ca"] is False
    assert tt["tam_dung_tram"] is None and tt["estop"] is False
    assert tt["du_an"] == [
        {"ten": "hr-codex", "bat_ghi": False, "tu_merge": False, "tu_deploy": False, "du_lenh": False, "tam_dung": None},
        {"ten": "repo-nhap", "bat_ghi": True, "tu_merge": False, "tu_deploy": False, "du_lenh": False, "tam_dung": None}]
    ct = _xem(app)
    assert ct["cai_dat"] == {"tu_merge": False, "tu_deploy": False, "dieu_kien": {"ci": True, "cot": True,
                             "hang_rao": True}, "lenh": {"deploy": "", "kiem_song": "", "lui": ""}}
    assert ct["phien_ban"] == "0" and ct["khoa_cung"] == ["qc", "kiem_lai", "schema"] and ct["lich_su_doi"] == []
    assert _xem(app, headers=DAI_CA)["la_dai_ca"] is True
    estop.bat("thử")
    assert _xem(app)["estop"] is True
    assert goi(app, "GET", "/api/du-an/khong-co/tu-dong").status == 404


@pytest.mark.parametrize("h", [{}, {**DAI_CA, "Tailscale-User-Login": "nguoi-la@example.com"},
                               {k: v for k, v in DAI_CA.items() if k != "X-Tram"},
                               {**DAI_CA, "Origin": "https://evil.example"}])
def test_thieu_hoac_gia_danh_tinh_bi_403(tmp_path, h):
    """Scenario "Thiếu danh tính": 403, cài đặt không đổi — cả qua kênh unix-socket."""
    app, _ = _app(tmp_path)
    g = {"ma_thao_tac": "ma-td-danh-tinh", "expected_version": ""}
    for duong, than in ((CD, _than()), ("/api/du-an/repo-nhap/tu-dong/tam-dung", g), ("/api/tu-dong/tam-dung", g)):
        assert goi(app, "POST", duong, json_body=than, headers=h).status == 403
    assert _xem(app)["phien_ban"] == "0" and _xem(app)["tam_dung"] is None


def test_kenh_header_chi_nhan_tam_dung(tmp_path):
    """D87 — Scenario "Kênh header", "Tạm dừng vẫn được"."""
    app, _ = _app(tmp_path, unix=False)
    r = goi(app, "POST", CD, json_body=_than(), headers=DAI_CA)
    assert r.status == 403 and "cần kênh ghi unix-socket" in r.json()["detail"]
    g = {"ma_thao_tac": "ma-td-header1", "expected_version": ""}
    assert goi(app, "POST", "/api/du-an/repo-nhap/tu-dong/tam-dung", json_body=g, headers=DAI_CA).status == 200
    assert goi(app, "POST", "/api/tu-dong/tam-dung", json_body={**g, "ma_thao_tac": "ma-td-header2"},
               headers=DAI_CA).status == 200
    for duong in ("/api/du-an/repo-nhap/tu-dong/tiep-tuc", "/api/tu-dong/tiep-tuc"):
        assert goi(app, "POST", duong, json_body={**g, "ma_thao_tac": "ma-tt-header1"}, headers=DAI_CA).status == 403
    xem = _xem(app)
    assert xem["tam_dung"]["boi"] == "dai-ca/dashboard" and xem["tam_dung_tram"] is not None
    assert xem["phien_ban"] == "0"


def test_luu_qua_unix_socket_gui_lai_va_lich_su(tmp_path):
    app, _ = _app(tmp_path)
    r = goi(app, "POST", CD, json_body=_than(), headers=DAI_CA)
    assert r.status == 200 and r.json()["lap_lai"] is False
    r2 = goi(app, "POST", CD, json_body=_than(), headers=DAI_CA)                    # cùng mã thao tác
    assert r2.json() == {**r.json(), "lap_lai": True}
    pb = r.json()["ket_qua"]["tu_dong.cai_dat"]["phien_ban"]
    xem = _xem(app)
    assert xem["cai_dat"] == CAI_DAT and xem["phien_ban"] == pb and len(xem["lich_su_doi"]) == 1
    tat = goi(app, "POST", CD, json_body=_than("ma-api-td-002", pb, tu_merge=False), headers=DAI_CA)
    assert tat.status == 200
    ls = _xem(app)["lich_su_doi"]
    assert [(d["tac_nhan"], d["doi"][0]["truong"], d["doi"][0]["sau"]) for d in ls] == [
        ("dai-ca/dashboard", "tu_merge", False), ("dai-ca/dashboard", "tu_merge", True)]


def test_ma_loi_409_422(tmp_path):
    app, _ = _app(tmp_path)
    goi(app, "POST", CD, json_body=_than(), headers=DAI_CA)
    r = goi(app, "POST", CD, json_body=_than("ma-api-td-003", "0", tu_merge=False), headers=DAI_CA)
    assert r.status == 409 and "đã đổi" in r.json()["loi"]                          # Scenario "Màn hình cũ"
    pb = _xem(app)["phien_ban"]
    qc = _than("ma-api-td-004", pb)
    qc["cai_dat"]["dieu_kien"] = {**CAI_DAT["dieu_kien"], "qc": False}                # D71: không có trường QC
    assert goi(app, "POST", CD, json_body=qc, headers=DAI_CA).status == 422
    assert goi(app, "POST", CD, json_body={**_than("ma-api-td-005", pb), "kiem_lai": False},
               headers=DAI_CA).status == 422
    r = goi(app, "POST", "/api/du-an/hr-codex/tu-dong/cai-dat", json_body=_than("ma-api-td-006"), headers=DAI_CA)
    assert r.status == 422 and "chỉ quét thử" in r.json()["loi"]                    # Scenario "Dự án chỉ quét thử"
    assert goi(app, "POST", "/api/du-an/khong-co/tu-dong/cai-dat", json_body=_than("ma-api-td-007"),
               headers=DAI_CA).status == 404
    g = {"ma_thao_tac": "ma-api-td-008", "expected_version": ""}
    assert goi(app, "POST", "/api/du-an/_tram/tu-dong/tam-dung", json_body=g, headers=DAI_CA).status == 404
    assert goi(app, "GET", "/api/tu-dong").json()["tam_dung_tram"] is None           # không tạm dừng toàn trạm
    assert _xem(app)["phien_ban"] == pb and _xem(app, "hr-codex")["phien_ban"] == "0"


def test_lenh_co_bi_mat_bi_tu_choi_khong_vong_lai(tmp_path):
    """Scenario "Dán token vào lệnh kiểm còn sống": 422, câu hằng; phản hồi không chứa token, không lưu."""
    app, _ = _app(tmp_path)
    token = "ghp_" + "Zq7" * 12
    for lenh in (f"curl -H 'Authorization: token {token}' https://x.vn", f"{token}" + "x" * 2000):
        r = goi(app, "POST", CD, json_body=_than(lenh={**LENH, "kiem_song": lenh}), headers=DAI_CA)
        assert r.status == 422 and token.encode() not in r.body
    r = goi(app, "POST", CD, json_body=_than(lenh={**LENH, "kiem_song": f"curl -u a:{token} https://x.vn"}),
            headers=DAI_CA)
    assert r.json()["loi"] == "Lệnh kiểm còn sống: Lệnh có vẻ chứa bí mật — để bí mật ngoài lệnh"
    assert _xem(app)["phien_ban"] == "0"
```

- [ ] **Step 2: Chạy, mong đợi ĐỎ**

```bash
tests/chan_host/chay.sh -q tests/test_api_tu_dong.py
```
Đỏ thật: `9 failed in 1.08s` — tuyến chưa có nên mọi yêu cầu trả 404 `{"detail":"Not Found"}`: `KeyError: 'chi_tam_dung'`, `assert 404 == 403` (4 ca danh tính), `assert (404 == 409)`…; nhật ký chặn 0 dòng mới.

- [ ] **Step 3: Viết mã**

Sửa `tram/api/than.py` (bản vá, áp bằng `git apply`):

```diff
diff --git a/tram/api/than.py b/tram/api/than.py
index 4eccd7c..ba80573 100644
--- a/tram/api/than.py
+++ b/tram/api/than.py
@@ -45,3 +45,30 @@ class ThanNhoGhi(ThanGhi):
     noi_dung: str = Field(min_length=1, max_length=600)
     pham_vi: str = Field(min_length=1, max_length=200)
     nhan: list[Annotated[str, Field(min_length=1, max_length=30)]] = Field(default_factory=list, max_length=5)
+
+
+class _Kin(BaseModel):
+    model_config = ConfigDict(extra="forbid")
+
+
+class ThanDieuKien(_Kin):                                   # TM-1 (D70, D71): chỉ ba nút có nút; QC/kiểm lại → 422
+    ci: bool
+    cot: bool
+    hang_rao: bool
+
+
+class ThanLenh(_Kin):                                       # D73: trần thật 500 ký tự kiểm ở tram/tu_dong/cai_dat.py
+    deploy: str = Field(max_length=2000)
+    kiem_song: str = Field(max_length=2000)
+    lui: str = Field(max_length=2000)
+
+
+class ThanCaiDat(_Kin):
+    tu_merge: bool
+    tu_deploy: bool
+    dieu_kien: ThanDieuKien
+    lenh: ThanLenh
+
+
+class ThanCaiDatTuDong(ThanGhi):
+    cai_dat: ThanCaiDat
```

Tạo mới `tram/suy/tu_dong.py` (nguyên văn):

```python
"""Trạng thái hiển thị của tự merge / tự deploy (`dieu-khien-tu-dong`, design D-5) — tính lúc đọc từ sự kiện.
TM-2 (việc chờ kèm lý do), TM-3 (sẵn sàng deploy, lịch sử, bộ đếm hỏng) THÊM khoá vào hai bảng này, không đổi khoá
có sẵn."""
from tram.su_kien.kho import KhoSuKien
from tram.tu_dong.cai_dat import KHOA_CUNG, sang_api
from tram.tu_dong.luu import DU_AN_TRAM, TamDung, doc_trang_thai, lich_su_doi, tam_dung_cua


def tam_dung_api(td: TamDung | None) -> dict | None:
    return None if td is None else {"boi": td.boi, "luc": td.luc, "ly_do": td.ly_do}


def chung(kho: KhoSuKien, *, kenh_ghi: str, la_dai_ca: bool, estop_bat: bool) -> dict:
    """Phần chung của mọi GET: `chi_tam_dung` (D87) — dashboard khoá mọi nút trừ TẠM DỪNG, kèm giải thích."""
    return {"tam_dung_tram": tam_dung_api(tam_dung_cua(kho.db, DU_AN_TRAM)), "estop": estop_bat, "kenh_ghi": kenh_ghi,
            "chi_tam_dung": kenh_ghi == "header", "la_dai_ca": la_dai_ca}


def tom_tat_du_an(kho: KhoSuKien, ten: str, *, bat_ghi: bool) -> dict:
    tt = doc_trang_thai(kho.db, ten)
    return {"ten": ten, "bat_ghi": bat_ghi, "tu_merge": tt.cai_dat.tu_merge, "tu_deploy": tt.cai_dat.tu_deploy,
            "du_lenh": tt.cai_dat.du_lenh, "tam_dung": tam_dung_api(tt.tam_dung_du_an)}


def chi_tiet_du_an(kho: KhoSuKien, ten: str, *, bat_ghi: bool) -> dict:
    tt = doc_trang_thai(kho.db, ten)
    return {"du_an": ten, "bat_ghi": bat_ghi, "cai_dat": sang_api(tt.cai_dat), "du_lenh": tt.cai_dat.du_lenh,
            "phien_ban": tt.phien_ban, "tam_dung": tam_dung_api(tt.tam_dung_du_an), "khoa_cung": list(KHOA_CUNG),
            "lich_su_doi": lich_su_doi(kho.db, ten)}
```

Tạo mới `tram/api/tuyen_tu_dong.py` (nguyên văn):

```python
"""Tuyến tự merge / tự deploy (`dieu-khien-tu-dong`, design D-5). GET: ai trong tailnet cũng xem (như `/api/du-an`),
kèm `la_dai_ca` để dashboard khoá nút. POST: `yeu_cau_ghi` (kênh, danh tính Đại ca, X-Tram, Origin) + mã thao tác;
lỗi thân yêu cầu không vọng lại nội dung (`TuyenEnvelopeKin` — ô lệnh có thể chứa thứ Đại ca lỡ dán).
D87: kênh `header` (tạm) giả được danh tính từ máy B → chỉ nhận TẠM DỪNG (dự án, toàn trạm); mọi ghi khác 403."""
from contextlib import closing

import yaml
from fastapi import APIRouter, Depends, HTTPException, Request

from tram.api.bao_mat import la_dai_ca_yeu_cau, yeu_cau_ghi
from tram.api.loi_envelope import TuyenEnvelopeKin
from tram.api.phu_thuoc import kiem_du_an_bead
from tram.api.than import ThanCaiDatTuDong, ThanGhi
from tram.chu import estop
from tram.suy.tu_dong import chi_tiet_du_an, chung, tom_tat_du_an
from tram.thao_tac.tu_dong import luu_cai_dat_thao_tac, tam_dung_thao_tac
from tram.tu_dong.cai_dat import tu_api
from tram.tu_dong.luu import DU_AN_TRAM

CAN_KENH = "cần kênh ghi unix-socket — cửa ghi còn tạm, chỉ bấm được TẠM DỪNG (D87)"
doc = APIRouter()
ghi = APIRouter(dependencies=[Depends(yeu_cau_ghi)], route_class=TuyenEnvelopeKin)


def kenh_ghi(request: Request) -> str:
    return getattr(request.app.state, "kenh_ghi", "header")


def can_kenh_that(request: Request) -> None:
    if kenh_ghi(request) == "header":
        raise HTTPException(status_code=403, detail=CAN_KENH)


def _bat_ghi(pt, ten: str) -> bool:
    """Như `tuyen_doc._bat_ghi`: yaml lỗi/khoá sai → False (INV-005: không bật được gì)."""
    try:
        return pt.bat_ghi(ten)
    except (OSError, ValueError, AttributeError, yaml.YAMLError):
        return False


def _chung(request: Request, kho) -> dict:
    return chung(kho, kenh_ghi=kenh_ghi(request), la_dai_ca=la_dai_ca_yeu_cau(request), estop_bat=estop.dang_bat())


@doc.get("/api/tu-dong")
def r_tom_tat(request: Request) -> dict:
    pt = request.app.state.pt
    with closing(pt.mo_kho()) as kho:
        ds = [tom_tat_du_an(kho, t, bat_ghi=_bat_ghi(pt, t)) for t in pt.cac_du_an()]
        return {**_chung(request, kho), "du_an": ds}


@doc.get("/api/du-an/{ten}/tu-dong")
def r_chi_tiet(ten: str, request: Request) -> dict:
    pt = request.app.state.pt
    kiem_du_an_bead(pt, ten)
    with closing(pt.mo_kho()) as kho:
        return {**_chung(request, kho), **chi_tiet_du_an(kho, ten, bat_ghi=_bat_ghi(pt, ten))}


def _chay(request: Request, lam) -> dict:
    pt = request.app.state.pt
    with closing(pt.mo_kho()) as kho, closing(pt.mo_kho_tt()) as kho_tt:      # N5: đóng kết nối mỗi yêu cầu
        kq = lam(kho, kho_tt)
    return {"ket_qua": kq.ket_qua, "lap_lai": kq.lap_lai}


@ghi.post("/api/du-an/{ten}/tu-dong/cai-dat", dependencies=[Depends(can_kenh_that)])
def r_cai_dat(ten: str, than: ThanCaiDatTuDong, request: Request) -> dict:
    pt = request.app.state.pt
    kiem_du_an_bead(pt, ten)
    cd, bg = tu_api(than.cai_dat.model_dump()), _bat_ghi(pt, ten)
    return _chay(request, lambda k, kt: luu_cai_dat_thao_tac(
        k, kt, ten, cd, bat_ghi=bg, ma=than.ma_thao_tac, expected_version=than.expected_version))


def _tam_dung(request: Request, du_an: str, than: ThanGhi, tam_dung: bool, *, toan_tram: bool = False) -> dict:
    if not toan_tram:                     # `/api/du-an/_tram/…` → 404: tuyến dự án không tạm dừng cả trạm
        kiem_du_an_bead(request.app.state.pt, du_an)
    return _chay(request, lambda k, kt: tam_dung_thao_tac(
        k, kt, du_an, tam_dung=tam_dung, ma=than.ma_thao_tac, expected_version=than.expected_version))


@ghi.post("/api/du-an/{ten}/tu-dong/tam-dung")
def r_tam_dung(ten: str, than: ThanGhi, request: Request) -> dict:
    return _tam_dung(request, ten, than, True)


@ghi.post("/api/du-an/{ten}/tu-dong/tiep-tuc", dependencies=[Depends(can_kenh_that)])
def r_tiep_tuc(ten: str, than: ThanGhi, request: Request) -> dict:
    return _tam_dung(request, ten, than, False)


@ghi.post("/api/tu-dong/tam-dung")
def r_tam_dung_tram(than: ThanGhi, request: Request) -> dict:
    return _tam_dung(request, DU_AN_TRAM, than, True, toan_tram=True)


@ghi.post("/api/tu-dong/tiep-tuc", dependencies=[Depends(can_kenh_that)])
def r_tiep_tuc_tram(than: ThanGhi, request: Request) -> dict:
    return _tam_dung(request, DU_AN_TRAM, than, False, toan_tram=True)
```

Sửa `tram/api/app.py` (bản vá, áp bằng `git apply`):

```diff
diff --git a/tram/api/app.py b/tram/api/app.py
index 519dce3..1348624 100644
--- a/tram/api/app.py
+++ b/tram/api/app.py
@@ -4,7 +4,7 @@ from fastapi.responses import JSONResponse
 from fastapi.staticfiles import StaticFiles
 
 from tram.api import doi_ngu, ghep, luong, noi_bo, tho, tho_them, tuyen_chu, tuyen_doc, tuyen_ghi, tuyen_nho, usage
-from tram.api import cai_dat, tong_quan, tuyen_yeu_cau, van_phong
+from tram.api import cai_dat, tong_quan, tuyen_tu_dong, tuyen_yeu_cau, van_phong
 from tram.api.bao_mat import them_header_an_toan
 from tram.api.phu_thuoc import PhuThuocApi
 from tram.api.tuyen_giao import router as tuyen_giao
@@ -22,6 +22,7 @@ CAC_TUYEN += (van_phong.router,)               # 2c: GET /api/van-phong
 CAC_TUYEN += (cai_dat.router,)                 # 2f: GET /api/cai-dat, /api/san-sang (chỉ Đại ca)
 CAC_TUYEN += (tong_quan.router,)               # 2f: GET /api/tong-quan
 CAC_TUYEN += (tuyen_yeu_cau.router,)           # 4d: POST /api/feature/yeu-cau[/xem] — máy A gửi, B tạo feature
+CAC_TUYEN += (tuyen_tu_dong.doc, tuyen_tu_dong.ghi)   # TM-1: /api/tu-dong, /api/du-an/{ten}/tu-dong[/…]
 
 
 def _xu_ly(ma: int):
```

- [ ] **Step 4: Chạy, mong đợi XANH**

```bash
tests/chan_host/chay.sh -q tests/test_api_tu_dong.py tests/test_api_ghi.py tests/test_kenh_ghi.py tests/test_api_doc.py tests/test_api_cai_dat.py tests/test_bao_mat.py tests/test_vong_import.py tests/test_do_dai_ma.py
```
Xanh thật: `48 passed in 2.35s` (lệnh trên), nhật ký chặn 0 dòng mới.

Rồi cả bộ: `tests/chan_host/chay.sh -q` → mong đợi `3391 passed` (N₀ + test mới tới task này — số tính; số đo thật ở Task 8 Step 2), nhật ký chặn 0 dòng mới.

- [ ] **Step 5: Commit**

```bash
git add tram/api/than.py tram/api/app.py tram/suy/tu_dong.py tram/api/tuyen_tu_dong.py tests/test_api_tu_dong.py
git commit -m "feat(api): tuyến tự merge/tự deploy qua cửa ghi, kênh header chỉ nhận tạm dừng (TM-1 Task 5)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

### Task 6: Tin Telegram của tự merge / tự deploy / đổi cài đặt (design D-8, D99)

**Scenario:** "Bật tự deploy" (tin), "Trạm tự tắt" (tin), "Tin tự merge", "Deploy thành công", "Lùi thành công" (tin + số lần hỏng), "Trang chết sau lùi" (tin khẩn), "Mất điện giữa deploy" (tin).

**Interfaces:** `tram.bao_tin.nguon_tu_dong.{TIEN_TO, tin_tu_dong(sk) -> list[Tin]}`; `tram.bao_tin.tin.{LOAI_CHI_TIET, NHAN_CHI_TIET, chi_tiet(ma) -> str}`; `tin_tu_su_kien` chuyển mọi sự kiện có tiền tố `tu_dong.`, `tu_merge.`, `deploy.` cho `tin_tu_dong`.

- [ ] **Step 1: Viết test**

Tạo mới `tests/test_bao_tin_tu_dong.py` (nguyên văn):

```python
"""TM-1: tin Telegram của tự merge / tự deploy (design D-8, D99; spec "Báo Telegram mỗi lần cài đặt đổi", "Báo
Telegram mỗi lần tự merge", "… mỗi lần deploy và lùi"). Hợp đồng sự kiện → tin cho TM-2/TM-3: hai lát đó chỉ GHI sự
kiện, không sửa `tram/bao_tin/`. Tin chỉ có dự án, mã bead, nhãn loại, chi tiết từ bảng mã — không lệnh, SHA, URL."""
from dataclasses import replace

import pytest

from tram.bao_tin.nguon import tin_tu_su_kien
from tram.bao_tin.nguon_tu_dong import tin_tu_dong
from tram.bao_tin.tin import LOAI_TIN, NHAN_LOAI, Tin, soan_tin
from tram.su_kien.kho import KhoSuKien
from tram.su_kien.mo_hinh import SuKien
from tram.thao_tac.kho import KhoThaoTac
from tram.thao_tac.tu_dong import luu_cai_dat_thao_tac, tam_dung_thao_tac
from tram.tu_dong.cai_dat import MAC_DINH
from tram.tu_dong.luu import doi_cai_dat

MOI = ("tu_merge", "san_sang_deploy", "deploy_xong", "deploy_da_lui", "tu_deploy_tu_tat", "deploy_khong_ro",
       "lui_hong", "cai_dat_doi")
URL = "https://may-b.tail.ts.net"
LENH = "/Users/Shared/tram-deploy/repo-nhap/deploy.sh"


def _sk(loai, du_lieu=None, *, du_an="repo-nhap", bead_id=None, tac_nhan="dai-ca/dashboard"):
    return SuKien("2026-10-18T02:00:00Z", du_an, bead_id, loai, tac_nhan, du_lieu or {}, 1)


def test_dang_ky_du_loai_tin_moi():
    assert set(MOI) <= set(LOAI_TIN) and set(MOI) <= set(NHAN_LOAI)


@pytest.mark.parametrize("sk, tin", [
    (_sk("tu_dong.cai_dat", {"cai_dat": {"tu_deploy": True}, "doi": ["tu_deploy"]}),
     [Tin("cai_dat_doi", "repo-nhap", "tu-deploy-bat")]),
    (_sk("tu_dong.cai_dat", {"cai_dat": {"dk_ci": False, "lenh_deploy": LENH}, "doi": ["dk_ci", "lenh_deploy", "la"]}),
     [Tin("cai_dat_doi", "repo-nhap", "dk-ci-tat"), Tin("cai_dat_doi", "repo-nhap", "lenh-deploy-doi")]),
    (_sk("tu_dong.cai_dat", {"cai_dat": {"tu_deploy": False}, "doi": ["tu_deploy"], "ly_do": "hong-3-lan"},
         tac_nhan="tram/tu-deploy"), [Tin("tu_deploy_tu_tat", "repo-nhap")]),
    (_sk("tu_dong.cai_dat", {"cai_dat": {"tu_deploy": False}, "doi": ["tu_deploy"], "ly_do": "lui-hong"},
         tac_nhan="tram/tu-deploy"), [Tin("cai_dat_doi", "repo-nhap", "tram-tu-deploy-tat")]),
    (_sk("tu_dong.tam_dung"), [Tin("cai_dat_doi", "repo-nhap", "tam-dung")]),
    (_sk("tu_dong.tam_dung", {"ly_do": "lui-hong"}, tac_nhan="tram/tu-deploy"),
     [Tin("cai_dat_doi", "repo-nhap", "tram-tam-dung")]),
    (_sk("tu_dong.tiep_tuc", du_an="_tram"), [Tin("cai_dat_doi", "_tram", "tiep-tuc-toan-tram")]),
    (_sk("tu_merge.xong", {"loai": "code"}, bead_id="rn-7", tac_nhan="tram/tu-merge"), [Tin("tu_merge", "repo-nhap", "rn-7")]),
    (_sk("tu_merge.loi", {"ma_loi": "gh-3-lan"}, bead_id="rn-7"), [Tin("tram_loi", "repo-nhap", "rn-7")]),
    (_sk("tu_merge.cho", {"ly_do": ["ci"]}, bead_id="rn-7"), []),
    (_sk("deploy.san_sang", {"commit": "a" * 40, "so_merge": 3}), [Tin("san_sang_deploy", "repo-nhap")]),
    (_sk("deploy.xong", {"ket_qua": "dat", "dem_hong": 0}), [Tin("deploy_xong", "repo-nhap")]),
    (_sk("deploy.xong", {"ket_qua": "da_lui", "dem_hong": 2}), [Tin("deploy_da_lui", "repo-nhap", "hong-2-lan")]),
    (_sk("deploy.xong", {"ket_qua": "lui_hong", "dem_hong": 1}), [Tin("lui_hong", "repo-nhap")]),
    (_sk("deploy.xong", {"ket_qua": "khong_ro"}), [Tin("deploy_khong_ro", "repo-nhap")]),
    (_sk("deploy.xong", {"ket_qua": "la"}), []),
    (_sk("deploy.lenh", {"buoc": "deploy", "ma_thoat": 1}), []),
])
def test_su_kien_sang_tin(sk, tin):
    assert tin_tu_dong(sk) == tin == tin_tu_su_kien(sk, None)


@pytest.mark.parametrize("loai, tins, vb", [
    ("cai_dat_doi", [Tin("cai_dat_doi", "repo-nhap", "tu-deploy-bat")],
     "[tram] repo-nhap · 1 cài đặt tự động vừa đổi (tự deploy bật) → " + URL),
    ("cai_dat_doi", [Tin("cai_dat_doi", "repo-nhap", "tram-tu-deploy-tat")],
     "[tram] repo-nhap · 1 cài đặt tự động vừa đổi (trạm: tự deploy tắt) → " + URL),
    ("cai_dat_doi", [Tin("cai_dat_doi", "_tram", "tam-dung-toan-tram")],
     "[tram] cài đặt tự động vừa đổi (TẠM DỪNG toàn trạm) → " + URL),
    ("tu_merge", [Tin("tu_merge", "repo-nhap", "rn-7")], "[tram] repo-nhap · 1 tự merge (rn-7) → " + URL),
    ("deploy_da_lui", [Tin("deploy_da_lui", "repo-nhap", "hong-2-lan")],
     "[tram] repo-nhap · 1 deploy hỏng, đã tự lùi (hỏng liên tiếp 2 lần) → " + URL),
    ("tu_deploy_tu_tat", [Tin("tu_deploy_tu_tat", "repo-nhap")],
     "[tram] repo-nhap · 1 trạm đã tự tắt tự deploy sau 3 lần hỏng → " + URL),
    ("lui_hong", [Tin("lui_hong", "repo-nhap")], "[tram] repo-nhap · 1 LÙI HỎNG — cần Đại ca → " + URL),
])
def test_soan_tin_loi_thuong(loai, tins, vb):
    assert soan_tin(loai, tins, URL) == vb


def test_cho_review_khong_bi_dich_chi_tiet():
    assert soan_tin("cho_review", [Tin("cho_review", "hr", "tam-dung")], None) == "[tram] hr · 1 việc chờ review (tam-dung)"


def test_dau_cuoi_dashboard_den_tin_khong_chua_lenh(tmp_path):
    """Scenario "Bật tự deploy" + "Trạm tự tắt": thao tác dashboard / trạm → sự kiện → tin; không chép lệnh."""
    k, kt = KhoSuKien(tmp_path / "sk.db"), KhoThaoTac(tmp_path / "sk.db")
    du = replace(MAC_DINH, lenh_deploy=LENH, lenh_kiem_song="k.sh", lenh_lui="l.sh")
    luu_cai_dat_thao_tac(k, kt, "repo-nhap", du, bat_ghi=True, ma="ma-tin-00001", expected_version="0")
    pb = k.gan_day("repo-nhap", "tu_dong.cai_dat", 1)[0].id
    luu_cai_dat_thao_tac(k, kt, "repo-nhap", replace(du, tu_deploy=True), bat_ghi=True, ma="ma-tin-00002",
                         expected_version=str(pb))
    doi_cai_dat(k.db, "repo-nhap", lambda c: replace(c, tu_deploy=False), tac_nhan="tram/tu-deploy",
                them={"ly_do": "hong-3-lan"})
    tam_dung_thao_tac(k, kt, "_tram", tam_dung=True, ma="ma-tin-00003", expected_version="")
    tins = [t for s in k.sau_id(0, 20) for t in tin_tu_su_kien(s, k)]
    assert tins == [Tin("cai_dat_doi", "repo-nhap", "lenh-deploy-doi"), Tin("cai_dat_doi", "repo-nhap", "lenh-kiem-song-doi"),
                    Tin("cai_dat_doi", "repo-nhap", "lenh-lui-doi"), Tin("cai_dat_doi", "repo-nhap", "tu-deploy-bat"),
                    Tin("tu_deploy_tu_tat", "repo-nhap"), Tin("cai_dat_doi", "_tram", "tam-dung-toan-tram")]
    vb = soan_tin("cai_dat_doi", tins[:4], URL)
    assert vb == ("[tram] repo-nhap · 4 cài đặt tự động vừa đổi (lệnh deploy đổi, lệnh kiểm còn sống đổi, lệnh lùi đổi, "
                  "tự deploy bật) → " + URL)
    assert "tram-deploy" not in vb and "k.sh" not in vb
```

- [ ] **Step 2: Chạy, mong đợi ĐỎ**

```bash
tests/chan_host/chay.sh -q tests/test_bao_tin_tu_dong.py
```
Đỏ thật: `ERROR tests/…` khi thu thập — `ModuleNotFoundError: No module named 'tram.bao_tin.nguon_tu_dong'` (`1 error in 0.06s`, thoát 2), nhật ký chặn 0 dòng mới.

- [ ] **Step 3: Viết mã**

Sửa `tram/bao_tin/tin.py` (bản vá, áp bằng `git apply`):

```diff
diff --git a/tram/bao_tin/tin.py b/tram/bao_tin/tin.py
index 06e7e1a..6beef04 100644
--- a/tram/bao_tin/tin.py
+++ b/tram/bao_tin/tin.py
@@ -6,12 +6,28 @@ from dataclasses import dataclass
 LOAI_TIN = ("cho_review", "spec_cho_duyet", "escalation", "co_do", "tram_loi", "estop_bat", "estop_tat",
             "khe_cau_dao", "khe_het_han_muc", "spec_cho_merge", "feature_xong", "pr_da_merge",
             "pr_khong_xac_minh")
+LOAI_TIN += ("tu_merge", "san_sang_deploy", "deploy_xong", "deploy_da_lui", "tu_deploy_tu_tat", "deploy_khong_ro",
+             "lui_hong", "cai_dat_doi")                                   # TM-1: tự merge / tự deploy (D-8, D99)
 NHAN_LOAI = {"cho_review": "việc chờ review", "spec_cho_duyet": "spec chờ duyệt", "escalation": "escalation bí",
              "co_do": "cờ đỏ", "tram_loi": "trạm lỗi", "estop_bat": "estop BẬT", "estop_tat": "estop tắt",
              "khe_cau_dao": "cầu dao khe ngắt", "khe_het_han_muc": "khe hết hạn mức",
              "spec_cho_merge": "spec đã duyệt chưa merge sau 24 giờ", "feature_xong": "feature xong, chờ Đại ca đóng",
              "pr_da_merge": "PR đã merge, trạm xác minh đúng commit đã kiểm",           # 2d: pr.da_merge (4c)
              "pr_khong_xac_minh": "PR đã merge nhưng trạm không xác minh được, cần Đại ca Duyệt tay"}   # 2d D15
+NHAN_LOAI |= {"tu_merge": "tự merge", "san_sang_deploy": "sẵn sàng deploy", "deploy_xong": "deploy xong",
+              "deploy_da_lui": "deploy hỏng, đã tự lùi", "tu_deploy_tu_tat": "trạm đã tự tắt tự deploy sau 3 lần hỏng",
+              "deploy_khong_ro": "deploy không rõ kết quả — cần Đại ca kiểm", "lui_hong": "LÙI HỎNG — cần Đại ca",
+              "cai_dat_doi": "cài đặt tự động vừa đổi"}
+# Loại mà ô `bead_id` mang MÃ CHI TIẾT (do `nguon_tu_dong.py` đặt) thay cho mã bead → dịch sang lời thường.
+LOAI_CHI_TIET = frozenset({"cai_dat_doi", "deploy_da_lui"})
+NHAN_CHI_TIET = {"tu-merge-bat": "tự merge bật", "tu-merge-tat": "tự merge tắt", "tu-deploy-bat": "tự deploy bật",
+                 "tu-deploy-tat": "tự deploy tắt", "dk-ci-bat": "nút CI xanh bật", "dk-ci-tat": "nút CI xanh tắt",
+                 "dk-cot-bat": "nút cột AI tự làm bật", "dk-cot-tat": "nút cột AI tự làm tắt",
+                 "dk-hang-rao-bat": "nút hàng rào bật", "dk-hang-rao-tat": "nút hàng rào tắt",
+                 "lenh-deploy-doi": "lệnh deploy đổi", "lenh-kiem-song-doi": "lệnh kiểm còn sống đổi",
+                 "lenh-lui-doi": "lệnh lùi đổi", "tam-dung": "TẠM DỪNG", "tiep-tuc": "tiếp tục",
+                 "tam-dung-toan-tram": "TẠM DỪNG toàn trạm", "tiep-tuc-toan-tram": "tiếp tục toàn trạm"}
+HONG_RE = re.compile(r"hong-([1-9][0-9]?)-lan")
 ID_AN_TOAN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}")
 KHE_AN_TOAN = re.compile(r"[A-Za-z0-9-]{1,32}/[a-z0-9-]{1,32}")      # khe_id (spec 3 §4) — tin hệ của lát 2b
 
@@ -23,11 +39,18 @@ class Tin:
     bead_id: str | None = None
 
 
+def chi_tiet(ma: str) -> str:
+    goc = ma.removeprefix("tram-")
+    hong = HONG_RE.fullmatch(goc)
+    nhan = f"hỏng liên tiếp {hong[1]} lần" if hong else NHAN_CHI_TIET.get(goc, goc)
+    return ("trạm: " if goc != ma else "") + nhan
+
+
 def soan_tin(loai: str, tins: Sequence[Tin], dashboard_url: str | None) -> str:
     theo: dict[str, list[str]] = {}
     for t in tins:
         ok = t.bead_id and (ID_AN_TOAN.fullmatch(t.bead_id) or KHE_AN_TOAN.fullmatch(t.bead_id))
-        theo.setdefault(t.du_an, []).append(t.bead_id if ok else "")
+        theo.setdefault(t.du_an, []).append((chi_tiet(t.bead_id) if loai in LOAI_CHI_TIET else t.bead_id) if ok else "")
     phan = []
     for du_an in sorted(theo):
         ma = [i for i in theo[du_an] if i]
```

Tạo mới `tram/bao_tin/nguon_tu_dong.py` (nguyên văn):

```python
"""Nguồn tin của tự merge / tự deploy (design D-8, D98, D99) — HỢP ĐỒNG sự kiện → tin cho TM-2, TM-3: hai lát đó
chỉ ghi đúng sự kiện dưới đây, không sửa `tram/bao_tin/`. Tin chỉ mang dự án, mã bead, nhãn loại và MÃ CHI TIẾT từ
bảng cố định (`tin.NHAN_CHI_TIET`) — không lệnh, SHA, URL PR, đầu ra lệnh, lý do tự do (INV-001, spec 2 §4 mục 5)."""
from tram.bao_tin.tin import Tin

TIEN_TO = ("tu_dong.", "tu_merge.", "deploy.")
KET_QUA_DEPLOY = {"dat": "deploy_xong", "da_lui": "deploy_da_lui", "lui_hong": "lui_hong",
                  "khong_ro": "deploy_khong_ro"}
MA_TRUONG = {"tu_merge": "tu-merge", "tu_deploy": "tu-deploy", "dk_ci": "dk-ci", "dk_cot": "dk-cot",
             "dk_hang_rao": "dk-hang-rao", "lenh_deploy": "lenh-deploy", "lenh_kiem_song": "lenh-kiem-song",
             "lenh_lui": "lenh-lui"}


def _tram(sk) -> str:
    return "tram-" if sk.tac_nhan.startswith("tram/") else ""


def _cai_dat(sk) -> list[Tin]:
    """Một tin mỗi trường đổi. Trạm tự tắt tự deploy sau 3 lần hỏng (TM-3, `ly_do: hong-3-lan`) → một tin riêng."""
    cd = sk.du_lieu.get("cai_dat") or {}
    if _tram(sk) and sk.du_lieu.get("ly_do") == "hong-3-lan" and cd.get("tu_deploy") is False:
        return [Tin("tu_deploy_tu_tat", sk.du_an)]
    ra = []
    for t in (t for t in sk.du_lieu.get("doi") or [] if t in MA_TRUONG):
        duoi = "doi" if t.startswith("lenh_") else ("bat" if cd.get(t) else "tat")
        ra.append(Tin("cai_dat_doi", sk.du_an, f"{_tram(sk)}{MA_TRUONG[t]}-{duoi}"))
    return ra


def tin_tu_dong(sk) -> list[Tin]:
    if sk.loai == "tu_dong.cai_dat":
        return _cai_dat(sk)
    if sk.loai in ("tu_dong.tam_dung", "tu_dong.tiep_tuc"):
        ma = sk.loai.removeprefix("tu_dong.").replace("_", "-")
        return [Tin("cai_dat_doi", sk.du_an, f"{ma}-toan-tram" if sk.du_an == "_tram" else _tram(sk) + ma)]
    if sk.loai == "tu_merge.xong":
        return [Tin("tu_merge", sk.du_an, sk.bead_id)]
    if sk.loai == "tu_merge.loi":
        return [Tin("tram_loi", sk.du_an, sk.bead_id)]
    if sk.loai == "deploy.san_sang":
        return [Tin("san_sang_deploy", sk.du_an)]
    loai = KET_QUA_DEPLOY.get(sk.du_lieu.get("ket_qua")) if sk.loai == "deploy.xong" else None
    if loai is None:
        return []
    dem = sk.du_lieu.get("dem_hong")
    hong = loai == "deploy_da_lui" and type(dem) is int and 0 < dem < 100
    return [Tin(loai, sk.du_an, f"hong-{dem}-lan" if hong else None)]
```

Sửa `tram/bao_tin/nguon.py` (bản vá, áp bằng `git apply`):

```diff
diff --git a/tram/bao_tin/nguon.py b/tram/bao_tin/nguon.py
index 7e5e58f..25b7429 100644
--- a/tram/bao_tin/nguon.py
+++ b/tram/bao_tin/nguon.py
@@ -1,5 +1,6 @@
 """Nguồn tin lát 2a (spec 2 §6): so ảnh beads trước/sau `quet.xong`; trạm lỗi và estop từ sự kiện.
 Lát 2b: `khe.cau_dao_ngat` (spec 3 §8.3) → "khe hết hạn mức" (ly_do `het-han-muc`) hoặc "cầu dao khe ngắt"."""
+from tram.bao_tin.nguon_tu_dong import TIEN_TO, tin_tu_dong
 from tram.bao_tin.tin import Tin
 from tram.beads.mo_hinh import Bead
 
@@ -34,6 +35,8 @@ def so_quet_loi_lien_tiep(kho, du_an: str) -> int:
 
 
 def tin_tu_su_kien(sk, kho) -> list[Tin]:
+    if sk.loai.startswith(TIEN_TO):                # TM-1: tự merge / tự deploy / cài đặt tự động
+        return tin_tu_dong(sk)
     if sk.loai == "estop.bat":
         return [Tin("estop_bat", sk.du_an)]
     if sk.loai == "estop.tat":
```

- [ ] **Step 4: Chạy, mong đợi XANH**

```bash
tests/chan_host/chay.sh -q tests/test_bao_tin_tu_dong.py tests/test_nguon_tin.py tests/test_bao_tin.py tests/test_bao_tin_pr.py tests/test_bao_tin_khe.py tests/test_bao_tin_feature.py tests/test_api_cai_dat.py tests/test_vong_import.py tests/test_do_dai_ma.py
```
Xanh thật: `63 passed in 1.69s` (lệnh trên), nhật ký chặn 0 dòng mới.

Rồi cả bộ: `tests/chan_host/chay.sh -q` → mong đợi `3418 passed` (N₀ + test mới tới task này — số tính; số đo thật ở Task 8 Step 2), nhật ký chặn 0 dòng mới.

- [ ] **Step 5: Commit**

```bash
git add tram/bao_tin/tin.py tram/bao_tin/nguon.py tram/bao_tin/nguon_tu_dong.py tests/test_bao_tin_tu_dong.py
git commit -m "feat(bao-tin): tin tự merge/tự deploy/đổi cài đặt từ sự kiện (TM-1 Task 6)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

### Task 7: Giờ yên lặng theo loại tin (D98, D99)

**Scenario:** "Hỏng lúc nửa đêm" (cả hai vế), D99 "mỗi lần đổi một tin", tu-deploy "Mỗi lần … deploy … sinh một tin".

**Interfaces:** `tram.bao_tin.chong_on.{LOAI_LUON_GUI, GOM_SAU_YEN_LANG, MOI_LAN_MOT_TIN}` (frozenset); `BoChongOn.trang_thai()` thêm khoá `cho_sang: [[loai, du_an, bead_id]]` (thiếu khoá khi đọc trạng thái cũ = rỗng).

- [ ] **Step 1: Viết test**

Tạo mới `tests/test_chong_on_tu_dong.py` (nguyên văn):

```python
"""TM-1: giờ yên lặng cho tin tự merge / tự deploy (D98, D99). Tin xấu và tin đổi cài đặt gửi ngay; tin tốt gom
gửi khi hết giờ yên lặng (không mất); "mỗi lần một tin" không bị luật 1 giờ nuốt. Các loại tin cũ giữ hành vi cũ."""
from datetime import datetime, timedelta, timezone

from tram.bao_tin.chong_on import BoChongOn
from tram.bao_tin.tin import Tin

YEN = "23:00-07:00"
DEM = datetime(2026, 10, 17, 19, 0, tzinfo=timezone.utc)          # 02:00 giờ VN — trong giờ yên lặng
SANG = datetime(2026, 10, 18, 0, 5, tzinfo=timezone.utc)          # 07:05 giờ VN


def _loai(ra):
    return [(g.loai, [(t.du_an, t.bead_id) for t in g.tins]) for g in ra]


def test_tin_xau_va_doi_cai_dat_gui_ngay_trong_gio_yen_lang():
    """Scenario "Hỏng lúc nửa đêm": tin "đã tự lùi" gửi ngay."""
    tins = [Tin("deploy_da_lui", "rn", "hong-1-lan"), Tin("lui_hong", "rn"), Tin("tu_deploy_tu_tat", "rn"),
            Tin("deploy_khong_ro", "rn"), Tin("cai_dat_doi", "rn", "tu-merge-bat"), Tin("cho_review", "rn", "rn-1")]
    assert [g.loai for g in BoChongOn(YEN).nhan(tins, DEM)] == [
        "deploy_da_lui", "lui_hong", "tu_deploy_tu_tat", "deploy_khong_ro", "cai_dat_doi"]
    bo = BoChongOn(YEN)
    for phut in (0, 1, 2):
        assert [g.loai for g in bo.nhan(tins[:5], DEM + timedelta(minutes=phut))] == [
            "deploy_da_lui", "lui_hong", "tu_deploy_tu_tat", "deploy_khong_ro", "cai_dat_doi"]
    assert bo.den_han(DEM + timedelta(minutes=6)) == []


def test_tin_tot_gom_gui_sau_gio_yen_lang_qua_luu_trang_thai():
    """Scenario "Hỏng lúc nửa đêm" vế sau: "deploy xong" lúc 01:00 gom gửi sau giờ yên lặng; tin cũ vẫn bỏ như trước."""
    bo = BoChongOn(YEN)
    assert bo.nhan([Tin("deploy_xong", "rn"), Tin("tu_merge", "rn", "rn-7"), Tin("tu_merge", "rn", "rn-8"),
                    Tin("san_sang_deploy", "rn"), Tin("cho_review", "rn", "rn-1")], DEM) == []
    assert bo.nhan([Tin("tu_merge", "rn", "rn-7")], DEM + timedelta(minutes=30)) == []        # trùng: gom một
    assert bo.den_han(DEM + timedelta(hours=1)) == []                                         # vẫn yên lặng
    bo = BoChongOn(YEN, bo.trang_thai())                                                      # tram-bao-tin chạy lại
    ra = bo.den_han(SANG)
    assert _loai(ra) == [("deploy_xong", [("rn", None)]), ("tu_merge", [("rn", "rn-7"), ("rn", "rn-8")]),
                         ("san_sang_deploy", [("rn", None)])]
    assert bo.den_han(SANG + timedelta(minutes=1)) == [] and bo.trang_thai()["cho_sang"] == []


def test_tin_tot_dang_gom_khi_vao_gio_yen_lang_khong_mat():
    """Tin thứ hai rơi vào cửa sổ 5 phút lúc 22:59, cửa sổ hết hạn lúc 23:04 (đã yên lặng) → hoãn tới sáng."""
    toi = datetime(2026, 10, 17, 15, 57, tzinfo=timezone.utc)                     # 22:57 giờ VN
    bo = BoChongOn(YEN)
    assert len(bo.nhan([Tin("tu_merge", "rn", "rn-1")], toi)) == 1
    assert bo.nhan([Tin("tu_merge", "rn", "rn-2")], toi + timedelta(minutes=2)) == []
    assert bo.den_han(toi + timedelta(minutes=7)) == [] and bo.trang_thai()["cho_sang"] == [["tu_merge", "rn", "rn-2"]]
    assert _loai(bo.den_han(SANG)) == [("tu_merge", [("rn", "rn-2")])]


def test_moi_lan_mot_tin_khong_bi_luat_mot_gio():
    """D99 "mỗi lần đổi một tin", spec tu-deploy "Mỗi lần … deploy … SHALL sinh một tin"."""
    t0 = datetime(2026, 10, 18, 3, 0, tzinfo=timezone.utc)
    bo = BoChongOn(YEN)
    for loai, ma in (("deploy_xong", None),):
        assert len(bo.nhan([Tin(loai, "rn", ma)], t0)) == 1
        assert bo.nhan([Tin(loai, "rn", ma)], t0 + timedelta(minutes=2)) == []            # trong cửa sổ 5 phút: gom
    assert {g.loai for g in bo.den_han(t0 + timedelta(minutes=5))} == {"deploy_xong"}
    assert bo.den_han(t0 + timedelta(minutes=10)) == []
    assert len(bo.nhan([Tin("deploy_xong", "rn")], t0 + timedelta(minutes=20))) == 1        # chưa đủ 1 giờ vẫn gửi
    bo.nhan([Tin("co_do", "rn", "rn-1")], t0)
    bo.den_han(t0 + timedelta(minutes=6))
    assert bo.nhan([Tin("co_do", "rn", "rn-1")], t0 + timedelta(minutes=30)) == []             # loại cũ: luật 1 giờ giữ
```

- [ ] **Step 2: Chạy, mong đợi ĐỎ**

```bash
tests/chan_host/chay.sh -q tests/test_chong_on_tu_dong.py
```
Đỏ thật: `4 failed in 0.75s` — `assert [] == ['deploy_da_lui', …]` (tin xấu bị bỏ trong giờ yên lặng), `assert [] == [('deploy_xong', …)]` (tin tốt mất thay vì gom), `KeyError: 'cho_sang'` (tin trong cửa sổ không có hàng hoãn tới sáng), `assert set() == {'deploy_xong'}` (luật 1 giờ nuốt tin); nhật ký chặn 0 dòng mới.

- [ ] **Step 3: Viết mã**

Sửa `tram/bao_tin/chong_on.py` (bản vá, áp bằng `git apply`):

```diff
diff --git a/tram/bao_tin/chong_on.py b/tram/bao_tin/chong_on.py
index 4bff1f3..743d219 100644
--- a/tram/bao_tin/chong_on.py
+++ b/tram/bao_tin/chong_on.py
@@ -1,5 +1,7 @@
 """Chống ồn Telegram (spec 2 §6): tin đầu gửi ngay, gom phần sau trong 5 phút, không lặp trong 1 giờ, giờ yên lặng;
-gửi lỗi thì xếp lại cho vòng sau."""
+gửi lỗi thì xếp lại cho vòng sau. TM-1 (D98, D99): tin xấu của tự deploy và tin đổi cài đặt gửi cả trong giờ yên
+lặng; tin tốt của tự merge / tự deploy gom tới khi hết giờ yên lặng (loại cũ vẫn bỏ như trước); loại "mỗi lần một
+tin" không theo luật 1 giờ."""
 from dataclasses import dataclass
 from datetime import datetime, time, timedelta
 
@@ -8,7 +10,11 @@ from tram.cham_cot.ghi import GIO_VN
 
 CUA_SO = timedelta(minutes=5)
 KHONG_LAP = timedelta(hours=1)
-LOAI_LUON_GUI = "tram_loi"
+LOAI_LUON_GUI = frozenset({"tram_loi", "deploy_da_lui", "tu_deploy_tu_tat", "deploy_khong_ro", "lui_hong",
+                           "cai_dat_doi"})
+GOM_SAU_YEN_LANG = frozenset({"tu_merge", "san_sang_deploy", "deploy_xong"})
+MOI_LAN_MOT_TIN = frozenset({"cai_dat_doi", "deploy_xong", "deploy_da_lui", "tu_deploy_tu_tat", "deploy_khong_ro",
+                             "lui_hong"})
 
 
 @dataclass(frozen=True)
@@ -43,14 +49,23 @@ class BoChongOn:
         self._da_gui: dict[str, str] = dict(tt.get("da_gui", {}))
         self._cua_so: dict[str, str] = dict(tt.get("cua_so", {}))
         self._cho: dict[str, list[list]] = {k: [list(x) for x in v] for k, v in tt.get("cho", {}).items()}
+        self._sang: list[list] = [list(x) for x in tt.get("cho_sang", [])]        # [loai, du_an, bead_id]
 
     def trang_thai(self) -> dict:
-        return {"da_gui": self._da_gui, "cua_so": self._cua_so, "cho": self._cho}
+        return {"da_gui": self._da_gui, "cua_so": self._cua_so, "cho": self._cho, "cho_sang": self._sang}
+
+    def _hoan(self, t: Tin, luc: datetime) -> bool:
+        """D98: tin tốt trong giờ yên lặng vào hàng `cho_sang` (không mất); True = đã hoãn."""
+        if t.loai not in GOM_SAU_YEN_LANG or not trong_gio_yen_lang(self._yen, luc):
+            return False
+        if [t.loai, t.du_an, t.bead_id] not in self._sang:
+            self._sang.append([t.loai, t.du_an, t.bead_id])
+        return True
 
     def _duoc_gui(self, t: Tin, luc: datetime) -> bool:
-        if t.loai != LOAI_LUON_GUI and trong_gio_yen_lang(self._yen, luc):
+        if t.loai not in LOAI_LUON_GUI and trong_gio_yen_lang(self._yen, luc):
             return False
-        cu = self._da_gui.get(_khoa(t))
+        cu = None if t.loai in MOI_LAN_MOT_TIN else self._da_gui.get(_khoa(t))
         return cu is None or luc - datetime.fromisoformat(cu) >= KHONG_LAP
 
     def _gui(self, loai: str, tins: list[Tin], luc: datetime) -> TinGui:
@@ -62,7 +77,7 @@ class BoChongOn:
     def nhan(self, tins: list[Tin], luc: datetime) -> list[TinGui]:
         ngay: dict[str, list[Tin]] = {}
         for t in tins:
-            if not self._duoc_gui(t, luc):
+            if self._hoan(t, luc) or not self._duoc_gui(t, luc):
                 continue
-            cs = self._cua_so.get(t.loai)
+            cs = None if t.loai in LOAI_LUON_GUI - {"tram_loi"} else self._cua_so.get(t.loai)
             if cs is not None and luc - datetime.fromisoformat(cs) < CUA_SO:
@@ -84,10 +99,16 @@ class BoChongOn:
 
     def den_han(self, luc: datetime) -> list[TinGui]:
         ra = []
+        if self._sang and not trong_gio_yen_lang(self._yen, luc):           # D98: hết giờ yên lặng → gửi phần gom
+            nhom: dict[str, list[Tin]] = {}
+            for loai, d, b in self._sang:
+                nhom.setdefault(loai, []).append(Tin(loai, d, b))
+            self._sang, ra = [], [self._gui(loai, ds, luc) for loai, ds in nhom.items()]
         for loai in list(self._cua_so):
             if luc - datetime.fromisoformat(self._cua_so[loai]) < CUA_SO:
                 continue
-            cho = [t for d, b in self._cho.pop(loai, []) if self._duoc_gui(t := Tin(loai, d, b), luc)]
+            cho = [t for d, b in self._cho.pop(loai, [])
+                   if not self._hoan(t := Tin(loai, d, b), luc) and self._duoc_gui(t, luc)]
             if cho:
                 ra.append(self._gui(loai, cho, luc))
             else:
```

- [ ] **Step 4: Chạy, mong đợi XANH**

```bash
tests/chan_host/chay.sh -q tests/test_chong_on_tu_dong.py tests/test_chong_on.py tests/test_bao_tin.py tests/test_tram_bao.py tests/test_do_dai_ma.py
```
Xanh thật: `40 passed in 2.08s` (lệnh trên), nhật ký chặn 0 dòng mới.

Rồi cả bộ: `tests/chan_host/chay.sh -q` → mong đợi `3422 passed` (N₀ + test mới tới task này — số tính; số đo thật ở Task 8 Step 2), nhật ký chặn 0 dòng mới.

- [ ] **Step 5: Commit**

```bash
git add tram/bao_tin/chong_on.py tests/test_chong_on_tu_dong.py
git commit -m "feat(bao-tin): giờ yên lặng theo loại tin — tin xấu gửi ngay, tin tốt gom (TM-1 Task 7)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

### Task 8: Tài liệu bị ảnh hưởng

- [ ] **Step 1: Sửa docs**

Sửa `docs/MODULES.md` (bản vá, áp bằng `git apply`):

```diff
diff --git a/docs/MODULES.md b/docs/MODULES.md
index 89221cb..d863b3b 100644
--- a/docs/MODULES.md
+++ b/docs/MODULES.md
@@ -38,11 +38,12 @@ Sở hữu: package nào giữ gì, vòng import, tích hợp ngoài, bộ test.
 | `tram/ban_giao/` | schema và đọc file bàn giao của agent |
 | `tram/nho/` | memory service + MCP (cổng 7710): tách/gộp ký ức, embed, quét bí mật, thăng cấp, phạm vi |
 | `tram/yeu_cau/` | sổ tiếp nhận phiếu yêu cầu feature từ máy A |
-| `tram/thao_tac/` | thao tác ghi từ dashboard: chốt, duyệt spec, kéo cột, estop, khe |
+| `tram/thao_tac/` | thao tác ghi từ dashboard: chốt, duyệt spec, kéo cột, estop, khe, cài đặt tự động và TẠM DỪNG (`tu_dong.py`) |
+| `tram/tu_dong/` | tự merge / tự deploy: cài đặt theo dự án lưu bằng sự kiện (`luu.py`), kiểm lệnh (`cai_dat.py`), khoá chung trước thao tác tự động (`khoa.py`), đường cấm từ ba lệnh (`file_cam.py`) |
 | `tram/suy/` | tính trạng thái hiển thị từ sự kiện + beads |
 | `tram/api/` | tram-api: router, bảo mật, kênh ghi, API thợ, ghép máy, nội bộ, điều phối |
 | `tram/chu/` | lệnh trạm chủ: cài từng dịch vụ launchd kèm biên nhận, gỡ theo biên nhận (`go_dich_vu.py`, `chung_cu_go.py`), khôi phục kho sự kiện (`khoi_phuc_su_kien.py`), siết quyền `~/.tram` (`siet_quyen.py`), estop, cấp mã, kiểm cách ly, trạng thái |
-| `tram/bao_tin/` | vòng báo tin Telegram, chống ồn |
+| `tram/bao_tin/` | vòng báo tin Telegram, chống ồn, giờ yên lặng theo loại tin; nguồn tin tự merge / tự deploy (`nguon_tu_dong.py`) |
 | `tram/keychain.py` | đọc mục Keychain có hạn (module ở gốc gói) |
 
 ## Tích hợp ngoài
```

Sửa `openspec/changes/tu-merge-tu-deploy/tasks.md` (bản vá, áp bằng `git apply`):

```diff
diff --git a/openspec/changes/tu-merge-tu-deploy/tasks.md b/openspec/changes/tu-merge-tu-deploy/tasks.md
index 6e7b9c3..f3769b0 100644
--- a/openspec/changes/tu-merge-tu-deploy/tasks.md
+++ b/openspec/changes/tu-merge-tu-deploy/tasks.md
@@ -1,8 +1,8 @@
 # Tasks — tự merge + tự deploy
 
-Plan TDD: **chưa có** — viết ở `docs/plans/<ngày>-tu-merge-tu-deploy.md` sau khi Đại ca duyệt bản change đã sửa theo
-D87–D101. Mỗi mốc dưới đây là một mốc nghiệm thu, không chép mã; bằng chứng là test của plan
-(chạy qua `tests/chan_host/chay.sh -q`) hoặc kịch bản cổng trong sổ tay chạy thật.
+Plan TDD: chia bốn lát — bảng ở `docs/plans/2026-10-18-tm-0-chia-lat.md`; lát nền (mốc 1.1–1.7, 4.1) ở
+`docs/plans/2026-10-18-lat-tm-1-nen-cai-dat.md`. Mỗi mốc dưới đây là một mốc nghiệm thu, không chép mã; bằng chứng là
+test của plan (chạy qua `tests/chan_host/chay.sh -q`) hoặc kịch bản cổng trong sổ tay chạy thật.
 
 ## 0. Cổng trước khi viết plan
 
```

- [ ] **Step 2: Kiểm docs và cả bộ**

```bash
ls tram/tu_dong/luu.py tram/tu_dong/cai_dat.py tram/tu_dong/khoa.py tram/tu_dong/file_cam.py tram/thao_tac/tu_dong.py tram/bao_tin/nguon_tu_dong.py docs/plans/2026-10-18-tm-0-chia-lat.md docs/plans/2026-10-18-lat-tm-1-nen-cai-dat.md
git diff e2a09ef -- tram | grep -c "CREATE TABLE"      # mong đợi 0
tests/chan_host/chay.sh -q
```
Mong đợi: mọi `ls` thấy file; `0`; `3422 passed` (+101 test mới: 20 + 10 + 23 + 8 + 9 + 27 + 4), nhật ký chặn 0 dòng mới. Tick mốc 1.1–1.7, 4.1 trong `tasks.md` **chỉ sau** QC và ghép (bằng chứng là test của plan). Sau khi ghép: điều phối ghi lại dòng Test ở `docs/CURRENT_STATE.md` (plan không sửa file đó).

- [ ] **Step 3: Commit**

```bash
git add docs/MODULES.md openspec/changes/tu-merge-tu-deploy/tasks.md
git commit -m "docs: MODULES thêm tram/tu_dong, tasks.md trỏ plan TM-0/TM-1

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

## Kiểm chứng plan

**Vòng 2 (18/10/2026, sau review Codex vòng 1) — số hiện hành:**

- **N₀** trên cây sạch `e2a09ef` (worktree tạm trong thư mục nháp, `uv sync --offline`): `3321 passed in 401.59s`, nhật ký chặn 0 dòng mới, điểm mù 48, push giả lập 629.
- **Áp từ plan, từng task** (trích MỌI khối mã/docs của chính file này theo thứ tự task — khối test → chạy lệnh Step 2 (đỏ) → khối mã (file mới chép nguyên văn, bản vá `git apply --check` rồi `git apply`) → chạy lệnh Step 4 (xanh)): đỏ đúng như Step 2 từng task (Task 1–4, 6: `ModuleNotFoundError`; Task 5: `9 failed`; Task 7: `4 failed`), xanh `27, 25, 30, 23, 48, 63, 40 passed` (lệnh Step 4 Task 1→7); Task 8 hai bản vá docs áp sạch. Nhật ký chặn 0 dòng mới mọi lượt.
- **Cả bộ trên cây đó:** `3422 passed in 356.30s (0:05:56)`, nhật ký chặn 0 dòng mới, điểm mù 48, push giả lập 629 (+101 = 20 + 10 + 23 + 8 + 9 + 27 + 4).
- **Đỏ thật trên mã cũ `0f88957`** cho hai sửa của vòng này — bảng "Phản hồi review Codex vòng 1". So với `0f88957`, mã khác đúng hai chỗ: `tram/tu_dong/file_cam.py` (hợp đồng mới) và một dòng `tram/bao_tin/chong_on.py` (sửa của Codex); test khác ở `tests/test_tu_dong_khoa.py`, `tests/test_chong_on_tu_dong.py`.
- **Nền mới** `nen/tm-1-ap-v2`: worktree tạm mới từ `e2a09ef`, trích lại MỌI khối mã/docs từ bản plan cuối (commit `878f49d`) theo thứ tự task; `diff -r` với cây đã chạy ở trên (`tram/`, `tests/`, `openspec/`, `docs/MODULES.md`, bỏ `__pycache__`): **0 khác biệt**; một commit `85ce7f4` `wip(nen): …`; cả bộ trên nhánh này `3422 passed in 383.22s (0:06:23)`, nhật ký chặn 0 dòng mới, điểm mù 48, push giả lập 629. Nhánh cũ `nen/tm-1-ap` (`0f88957`) không đụng.
- `git diff e2a09ef -- tram | grep -c "CREATE TABLE"` = 0. Mọi file `tram/` ≤ 120 dòng, dòng ≤ 120 ký tự (`tests/test_do_dai_ma.py` xanh); không vòng import (`tests/test_vong_import.py` xanh).
- Không chạy lệnh cấm nào; không gọi Telegram, `gh`, `bd`, mạng; `openspec validate` không chạy.

**Vòng 1 (khi viết, lịch sử — trước review):** N₀ `3321 passed in 340.75s`; chạy thật RED→GREEN 8 task, áp lại lên cây sạch + `diff -r` 0 khác biệt; cả bộ `3412 passed in 343.68s`. Tự soát vòng 1 bắt hai lỗi đã sửa: tuyến `POST /api/du-an/_tram/tu-dong/tam-dung` lọt kiểm dự án (nay 404, `test_ma_loi_409_422`); tin tốt đang gom trong cửa sổ 5 phút bị bỏ khi vào giờ yên lặng (nay hoãn tới sáng, `test_tin_tot_dang_gom_khi_vao_gio_yen_lang_khong_mat`). Mã của vòng này là nhánh `nen/tm-1-ap` (`0f88957`) — không dùng làm nền nữa.

## Bước cổng trên OS thật

Không có. Lát này không chạy lệnh nào ngoài Python trong tiến trình (không `gh`, không lệnh deploy, không Telegram thật). Kênh `unix-socket` chạy thật là điều kiện **trước khi bật** công tắc (design Migration Plan bước 2, G29) — không phải điều kiện ghép lát này. Cổng G8 "tự merge/tự deploy repo nháp" viết ở plan tài liệu sau TM-2/TM-3.

## Rủi ro còn lại (không đóng bằng plan này)

1. **Bộ quét bí mật là regex hữu hạn** (D23): lệnh có bí mật viết tự do (ví dụ mật khẩu ngắn sau `-p`) vẫn lọt. Lớp chặn thứ hai là luật Đại ca để bí mật ngoài lệnh (mockup: script ở `/Users/Shared/tram-deploy/…`) và môi trường lệnh tối thiểu của TM-3.
2. **Nội dung ba lệnh hiện cho mọi người trong tailnet** qua GET (spec "Xem khi không phải Đại ca: dữ liệu vẫn hiện"). Lệnh đã qua bộ quét; nếu Đại ca muốn ẩn, chỉ cần cắt khoá `lenh` trong `chi_tiet_du_an` khi `la_dai_ca` sai.
3. **Kênh `header` giả được danh tính** (D51): tới khi chuyển `unix-socket`, kẻ giả danh vẫn bấm được TẠM DỪNG (chiều an toàn, chỉ gây phiền). Mọi bật/sửa đã bị chặn.
4. **D89 chỉ bắt file được nhắc thẳng** trong lệnh (design Risks): script gọi tiếp file khác, `make` đọc `Makefile` ngầm thì không. Khuyên để script deploy ngoài repo.
5. **Tin tốt trong giờ yên lặng** chỉ gom cho ba loại mới; tin cũ (chờ review…) vẫn bị bỏ như trước — không đổi ở lát này.

## Thứ tự code đề xuất và file giao nhau

1. Đại ca duyệt plan TM-0 + TM-1 (kill list mục 1, 2, 7; hợp đồng; Câu hỏi 1) → review Codex vòng 2 → code Task 1 → 8 trên một nhánh → QC → ghép.
2. Ghép tuần tự **TM-1 → TM-2 → TM-3 → TM-4 → TC** (TM-0 sau review). Hunk TM-1 viết trên `e2a09ef`; các lát sau viết trên cây đã có TM-1 và tự ghi mục "Ghép trên lát trước". TM-1 là lát đầu nên không có mục đó.
3. File giao nhau (theo review Codex vòng 1, bảng "File chung và thứ tự ghép"): TM-2 và TM-3 cùng sửa `tram/suy/tu_dong.py` và `tram/api/tuyen_tu_dong.py` (bản ghép cơ học của router thành 123 dòng — Codex Q15, lát sau phải hợp nhất, không chỉ "thêm dòng"); TC sửa `tram/bao_tin/{tin,nguon}.py` sau TM-1 và phải giữ sửa gửi ngay của Task 7 trong `chong_on.py`; nhiều lát cùng sửa hàng package trong `docs/MODULES.md`. `tram/api/app.py`: plan khác thêm router thì giữ dòng `CAC_TUYEN += (tuyen_tu_dong.doc, tuyen_tu_dong.ghi)`.
4. Hợp đồng D89 mới (Task 3) đổi kiểu trả của callback (`(rel, loại) | None` thay cho `"file" | "dir" | None`): TM-3 (`tram/deploy/cam.py` — `loai_trong_cay`) và TM-2 (kiểm ở cửa merge, Codex Q2) phải dựng callback theo mục "Interfaces cho lát sau".

## Câu hỏi cho Đại ca

1. **Khi cửa ghi còn tạm, có cho bấm "Tiếp tục" không?** Đại ca chốt D87 "chỉ cho bấm TẠM DỪNG"; bản spec viết "TẠM DỪNG và Tiếp tục". Hai chỗ lệch nhau — Em không tự chọn, nhưng mã phải theo một bên. (a) **Chỉ TẠM DỪNG (Em đề xuất, plan đang làm thế):** một chương trình lạ trên máy B giả danh Đại ca được thì cũng không gỡ được lệnh tạm dừng Đại ca vừa bấm; Đại ca không mất gì vì khi cửa còn tạm thì cũng không bật được công tắc nào. (b) Cho cả Tiếp tục: đúng chữ trong spec, nhưng kẻ giả danh có thể cho trạm chạy tự động lại sau khi Đại ca dừng. Chọn sai (a) thì chỉ phiền: phải chờ cửa ghi mới để bấm Tiếp tục. Chọn (a) thì Em sửa một dòng trong spec cho khớp D87. *(Đại ca đang cân nhắc chuyển hẳn sang `unix-socket` — G29, D118 cho viết kịch bản thử; khi đó câu này hết ý nghĩa. Mã giữ (a), không phụ thuộc câu trả lời.)*

Các câu 2–5 bản trước đã có quyết định — xem "Ghi chú triển khai".

## Ghi chú triển khai

- **Quyết định của Đại ca (main, `docs/quyet-dinh/2026-10-18-tu-merge-tu-deploy.md`):**
  - **D114** (câu 2 cũ): tin "cài đặt tự động vừa đổi" **gửi ngay** cả trong giờ yên lặng — Task 7 làm thế, và gửi ngay cả khi vừa có tin cùng loại trong 5 phút (sửa review Codex vòng 1).
  - **D115** (câu 3 cũ): deploy "không rõ kết quả" → **tạm dừng cả dự án** (cả tự merge lẫn tự deploy), như lùi hỏng. Lát này đã có sẵn đường: `ghi_tam_dung(…, them={"ly_do": "khong-ro"})` (hợp đồng); TM-3 gọi.
  - **D116** (câu 4 cũ): dự án `bat_ghi: false` **không** được Deploy tay — `ly_do_chan(viec="deploy_tay")` trả `bat_ghi` (test `test_deploy_tay_duoc_khi_tam_dung_khoa_khi_estop`).
  - Câu 5 cũ: TM-4 **không** vẽ khối "agent tự cập nhật việc"; khối đó thuộc plan TC + mockup riêng (Em chọn, ghi ở cùng file quyết định).
- Câu 1 còn mở (xem trên). Mã theo D87 chặt.
- (ghi khi code: chỗ lệch plan, số đo thật.)

### Review Codex vòng 1 — 18/10/2026 (chỉ đọc tĩnh, lịch sử)

- Codex sửa thẳng Task 7 (`cs = None if t.loai in LOAI_LUON_GUI - {"tram_loi"} …`) và test phút 0, 1, 2, nhưng không chạy. Vòng 2 đã áp và chạy thật — mục "Phản hồi review Codex vòng 1".
- Bản mã `0f88957` (nhánh `nen/tm-1-ap`) phản ánh plan trước review; nền mới dựng từ plan đã sửa là `nen/tm-1-ap-v2` (mục "Kiểm chứng plan").

## Phản hồi review Codex vòng 1

| Mã | Mức | Sửa ở đâu | Test | Đỏ thật trên mã cũ (`0f88957`) → xanh |
|---|---|---|---|---|
| Q1 | Quan trọng | Task 3: `tram/tu_dong/file_cam.py` theo hợp đồng D89 mới — callback nhận token nguyên văn, trả `(rel, loại) \| None`; `file_cam` không còn tự bỏ token `/…` và `..`, chỉ bỏ rỗng, `~`, cờ, glob; bỏ kết quả callback dạng lạ. Mục "Interfaces cho lát sau" ghi cách bên gọi dựng callback. | `test_duong_dan_tuyet_doi_hoac_vong_trong_repo_bi_cam` (5 ca: tuyệt đối trong repo, sau `=`, vòng `..` trong repo, `make -C <thư mục>`), `test_bo_qua_token_ngoai_repo_hoac_la` (10 ca: tuyệt đối ngoài repo, gốc giả cùng tiền tố, `..` thoát gốc, chính gốc…), `test_token_nguyen_van_toi_callback`, `test_ket_qua_callback_la_bi_bo` | Đỏ: test mới trên `file_cam` cũ → `7 failed` — 5 ca tuyệt đối/vòng trong repo (`assert () == ('scripts/deploy.sh',)`…), `test_token_nguyen_van_toi_callback` (`assert ['d'] == ['/x/a.sh', '../b.sh', '/y/c', './d']` — mã cũ tự bỏ `/…`, `..`), `test_duong_dan_cam_tu_ba_lenh` (kiểu trả mới). Xanh: `30 passed` (lệnh Step 4 Task 3) trên cây dựng từ plan. |
| C2 (phần TM-1) | Chặn | Interfaces + docstring `file_cam`: tập từ ba lệnh là tập cấm **bắt buộc**, bên gọi không để `cho_phep` miễn. Sửa mã cửa kiểm thuộc TM-3 (`tram/kiem/duong_dan_cam.py` lọc `cho_phep` trước `them`). | `test_duong_dan_cam_tu_ba_lenh` gọi `duong_dan_cham_cam` không kèm `cho_phep` (mẫu cho bên gọi); test "cùng file trong `cho_phep` vẫn chặn" thuộc TM-3 | — (hợp đồng) |
| Sửa trực tiếp 1 (D98/D114) | Quan trọng | Task 7: tin xấu mới và `cai_dat_doi` không qua cửa sổ gom 5 phút (`tram_loi` như cũ). Đã áp và chạy thật bản Codex, giữ nguyên. | `test_tin_xau_va_doi_cai_dat_gui_ngay_trong_gio_yen_lang` (phút 0, 1, 2), `test_moi_lan_mot_tin_khong_bi_luat_mot_gio` (bỏ ca đòi gom `cai_dat_doi`) | Đỏ: test mới trên `chong_on` cũ → `1 failed` ở `phut = 1` (`assert [] == ['deploy_da_lui', …, 'cai_dat_doi']` — lần thứ hai trong 5 phút bị giữ vào hàng chờ). Xanh: thêm đúng dòng Codex → `64 passed` (`test_chong_on_tu_dong`, `test_chong_on`, `test_bao_tin`, `test_tram_bao`, `test_bao_tin_tu_dong`) trên `0f88957`; `40 passed` (lệnh Step 4 Task 7) trên cây dựng từ plan. |
| Q15 (phần TM-1) | Quan trọng | Mục "Thứ tự code đề xuất…" bỏ kết luận "xung đột chỉ là thêm dòng"; hợp nhất router thuộc TM-2/TM-3. | — | — |
| Câu hỏi cũ D114–D116 | — | Bỏ câu 2–5 khỏi "Câu hỏi cho Đại ca", ghi quyết định vào "Ghi chú triển khai". | — | — |

Không còn lỗi Chặn/Quan trọng nào của review nằm trong phạm vi file TM-1 mà chưa sửa. Q2 (kiểm D89 ở cửa merge) và phần mã của C2 thuộc TM-2/TM-3, dùng hợp đồng trên.
