# Lát TM-2 — tự merge có điều kiện: lệnh `gh pr merge` chặt, đọc CI, xét điều kiện, đối soát, PR spec — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: dùng `ai-skills:subagent-driven-development` (khuyến nghị) hoặc `ai-skills:executing-plans` để làm từng task. Step dùng checkbox (`- [ ]`). **Chưa được code:** lát chạm kill list mục 5 (`gh pr merge` — lần đầu trạm có quyền merge) và mục 7 (lần đầu có mã ĐỌC công tắc tự merge để hành động) — Đại ca duyệt plan và review Codex trước (Global Constraints). **Phụ thuộc cứng: TM-1 bản vòng 2** (hợp đồng D89 mới của `tram.tu_dong.file_cam.duong_dan_tu_lenh` — callback trả `(đường dẫn, loại)`); ghép TM-2 ngay SAU TM-1 vòng 2, không ghép trên TM-1 vòng 1.

**Trạng thái:** sửa vòng review cuối (3/3), ngày 18/10/2026, từ `dc238a0` trong worktree `sua/tm2-v2`.
Phạm vi mới: **V2-C1** của `REVIEW-CODEX-tm-vong2.md`; giữ sửa V2-Q4/V2-N2 đã có.
**Hunk viết trên `85ce7f4` (`nen/tm-1-ap-v2`)**. Bằng chứng hiện hành ở mục cuối
"Phản hồi review Codex vòng 2"; mục kiểm chứng vòng trước chỉ là lịch sử.
**Chưa đạt cổng cả bộ:** sandbox chặn đọc bảng tiến trình macOS; không nới cơ chế thu hồi.
Chưa áp vào `main`; phiên này **không commit**, chỉ giữ plan và `KET-QUA-CODEX.md` theo yêu cầu.

**Goal:** Khi dự án bật công tắc tự merge, trạm tự gộp PR do chính trạm mở cho một bead ở cột 3 — chỉ khi đủ mọi điều kiện Đại ca chốt (D70–D72, D76, D90–D93, D112) — và tự gộp PR spec Đại ca đã duyệt (D95); thiếu điều kiện nào thì bead chờ Đại ca như hôm nay, kèm lý do bằng lời thường trên dashboard. Lệnh merge chỉ có một dạng chặt (design D-3), đọc lại cài đặt / TẠM DỪNG / estop / `bat_ghi` ngay trước lệnh, ghi sự kiện trước lệnh và đối soát khi kết quả không rõ (design D-7). Công tắc tắt (mặc định) → hành vi trạm **không đổi chút nào**: không đọc thêm GitHub, không ghi sự kiện mới.

**Architecture:** Sáu module mới trong `tram/giao_viec/`: `gh_tu_merge.py` (hàm thuần — dạng duy nhất của lệnh merge, đọc CI từ `statusCheckRollup`), `tu_merge_xet.py` (hàm thuần — mã lý do theo thứ tự cố định của design D-2, nhãn lời thường, tính lại QC/kiểm lại từ sự kiện), `tu_merge_gui.py` (ghi `tu_merge.*`, gửi lệnh, đối soát, đếm 3 lần), `tu_merge_rao.py` (phần đọc Git: diff, hàng rào, cấu trúc DB, và **D89 tại cửa merge** — tập file cấm từ ba lệnh của cài đặt ĐỌC LẠI ngay trước lệnh, so với diff PR), `tu_merge_tuoi.py` (đọc Beads/sự kiện hiện hành sau lệnh chậm, kiểm lại bản duyệt spec), `tu_merge.py` (thu dữ kiện từ sự kiện + Beads + kho kiểm, hai điểm vào `xet_tu_merge` và `tu_merge_spec`). Sửa lỗi có sẵn `tick_cot_3.py` (con của feature `theo-plan` không vào được cột 3 — Codex Q3). `gh.py` cho thêm lệnh `merge` nhưng chặn ở cửa `_gh` mọi dạng khác `la_dang_merge`; `view` đọc thêm `statusCheckRollup`. `tick_github.buoc_github` chen bước mới: `mo_pr_bead → xet_tu_merge → kiem_merge` và `mo_pr_spec → tu_merge_spec` (design D-1, D-11). Luồng xác minh merge, đóng bead, điều kiện 8 của spec 4 §5.1 giữ nguyên, không viết lại. Trạng thái hiển thị: `tram/suy/tu_merge.py` tính `cho_dai_ca` lúc đọc từ sự kiện và giữ cả hàm đọc tiêu đề; `tram/suy/tu_dong.py`, `tram/api/tuyen_tu_dong.py` (file chung với TM-1, TM-3) chỉ thêm dòng import + dòng gọi. Không bảng mới, không sửa `tram/bao_tin/` (tin `tu_merge`, `tram_loi` đã có ở TM-1).

**Tech Stack:** Python 3.12 stdlib (`hashlib`, `fnmatch`, `subprocess`, `dataclasses`), pytest 8. Không dependency mới.

**Spec / nguồn:** change [`openspec/changes/tu-merge-tu-deploy/`](../../openspec/changes/tu-merge-tu-deploy/) — `specs/tu-merge/spec.md` (mọi Requirement, trừ hai vế đã thuộc TM-1: "Yêu cầu tắt điều kiện QC bị từ chối", phần soạn tin của "Báo Telegram mỗi lần tự merge"), `specs/dieu-khien-tu-dong/spec.md` (Estop dừng cả tự merge và tự deploy — vế tự merge; Kiểm lại công tắc ngay trước lúc merge — thực ra nằm ở `tu-merge`), `design.md` D-1, D-2, D-3, D-7 (merge), D-11, bảng §15; `tasks.md` mốc 2.1–2.7. Quyết định D70, D72, D76, D89, D90–D93, D95, D112, **D119–D122** (Đại ca trả lời Câu hỏi 1–4 của plan này, `docs/quyet-dinh/2026-10-18-tu-merge-tu-deploy.md` ở `main`). Hợp đồng D89 mới (luật chung sửa plan vòng 2, `.handover/qc/SUA-TM-V2-CHUNG.md`). Review Codex gộp vòng 1 (`.handover/review-codex-plan/REVIEW-CODEX-tm-vong1.md`): C2, Q2, Q3, Q15 và sửa trực tiếp #2. Chia lát: [`2026-10-18-tm-0-chia-lat.md`](2026-10-18-tm-0-chia-lat.md). Hợp đồng nền: [`2026-10-18-lat-tm-1-nen-cai-dat.md`](2026-10-18-lat-tm-1-nen-cai-dat.md) mục "Interfaces cho lát sau". Mã thật đã đọc: `tram/giao_viec/{gh,tick_github,tick,tick_cot_3,tick_pipeline,doc_lai,su_kien,pr,pr_merge,pr_bang_chung,bang_chung,co_do_gn,spec_merge,kiem_lai,xet_xong,xet_spec,pipeline,dieu_kien,bo,noi_that,phu_thuoc_4c}.py`, `tram/tu_dong/file_cam.py`, `tram/tu_dong/{cai_dat,luu,khoa}.py`, `tram/suy/tu_dong.py`, `tram/bao_tin/{nguon,nguon_tu_dong}.py`, `tram/chu/estop.py`, `tram/cau_hinh/{bat_ghi,du_an,cach_ly}.py`, `tram/cham_cot/luat_cung.py`, `tram/kiem/{diff,duong_dan_cam}.py`, `tram/phieu/{kho,cap}.py`, `tram/api/tuyen_tu_dong.py`; test `tests/{gh_gia,test_gh,test_tick_4c,test_pr,giao_viec_gia,su_kien_gia,kho_kiem_gia,api_gia}.py`.

## Global Constraints

- **Kill list (`AGENT_RULES.md` §2) — STOP, Đại ca duyệt trước khi code.** Chấm blast radius: không đảo ngược trong 1 giờ (một PR đã merge vào nhánh chính của dự án thật) + chạm 2 package (`giao_viec`, `suy`) = 1 điểm, cộng kill list:
  - mục **5 đẩy code, PR, merge**: `tram/giao_viec/gh.py` thêm `merge` vào lệnh được phép — **lần đầu trạm có quyền merge**. Chỉ một dạng `gh pr merge <so> --repo <owner/repo> --merge --match-head-commit <sha>`; cửa `GhCli._gh` từ chối mọi dạng khác (test khoá mới quét cả `tram/` cấm `--admin`, `--squash`, `--rebase`, `--auto`, `--delete-branch`). `tram/giao_viec/tick_github.py` chen bước tự merge. **Không sửa** `pr.py`, `pr_merge.py`, `tram/cong_bo/`.
  - mục **7 công tắc lớn**: lát này là mã đầu tiên ĐỌC công tắc tự merge, ba nút điều kiện, TẠM DỪNG để hành động. Không thêm công tắc mới; không đổi mặc định (tắt). `bat_ghi` chỉ đọc (`tram/cau_hinh/bat_ghi.py` không sửa).
  - **Không chạm:** mục 1 (cửa danh tính — không tuyến ghi mới), mục 2, mục 3 (`kiem_lai.py`, `tram/kiem/duong_dan_cam.py` không sửa; QC/kiểm lại chỉ ĐỌC sự kiện; D89 tại cửa merge là một lần so THÊM, không nới kiểm đường cấm nào và không đọc `duong_dan_cam_cho_phep`), mục 4 (không `CREATE TABLE`, chỉ thêm 4 loại sự kiện `tu_merge.*` đúng hợp đồng TM-1), mục 6, mục 8 (không chạy `gh` thật).
  - **Ngoài kill list nhưng ngoài phạm vi chia lát cũ:** `tram/giao_viec/tick_cot_3.py` sửa lỗi có sẵn (Codex Q3, bead `bs-2bd.1.28`, Đại ca giao đưa vào lát này) — chỉ thêm tập "spec đã merge" cho lần xét lại cuối; không đổi luật §5.1.
- **Hợp đồng TM-1:** không sửa `tram/bao_tin/`, `tram/tu_dong/{luu,cai_dat,khoa}.py`, `tram/thao_tac/tu_dong.py`. Sự kiện ghi đúng bảng "Sự kiện" của TM-1 (`tu_merge.cho {ly_do, commit}`, `tu_merge.bat_dau {ma_thao_tac, commit, pr, loai}` — thêm khoá `lan`, `tu_merge.xong {ma_thao_tac, loai}`, `tu_merge.loi {ma_thao_tac, ma_loi}`; tác nhân `tram/tu-merge`). `tram/suy/tu_dong.py` chỉ THÊM khoá `cho_dai_ca`. **Dùng hợp đồng D89 MỚI** của `tram.tu_dong.file_cam.duong_dan_tu_lenh(cd, loai_trong_repo)` (callback nhận token nguyên văn, trả `(đường dẫn tương đối POSIX, "file"|"dir") | None`; `file_cam` không tự bỏ token `/…`) — TM-1 vòng 2 sửa `file_cam.py` và test của nó; lát này KHÔNG sửa `file_cam.py`. Không áp lát này trên hợp đồng callback trả chuỗi của TM-1 vòng 1. Không đổi hợp đồng TM-1; V2-C1 thêm `bd` vào hai hàm nội bộ TM-2 và cập nhật caller cùng lượt.
- **Số lịch sử vòng trước — số hiện hành xem mục cuối:** N₀ = 3422 test được thu thập trên nền `85ce7f4` (không gọi là 3422 passed trong phiên này).
  Sau lát **3510 test được thu thập**, tăng **88**: Task 1 = 17, Task 2 = 27, Task 3 = 34,
  Task 4 = 6, Task 5 = 2, Task 6 = 2. Bộ kiểm tập trung **120 passed**, nhật ký chặn 0 dòng mới.
  Cả bộ bị lỗi nền do sandbox; chi tiết ở mục "Kiểm chứng plan". Phải chạy lại cả bộ trước nghiệm thu triển khai.
- Chạy test BẮT BUỘC qua `tests/chan_host/chay.sh -q [đường test]`; "0 dòng mới" trong nhật ký chặn là điều kiện xanh. Test không bao giờ gọi `gh` thật, Telegram, `bd`, mạng: GitHub giả `tests/gh_gia.py` (merge thật trên remote Git cục bộ trong `tmp_path`), `du-an/*.yaml` giả qua `TRAM_REPO` tạm, SQLite tạm.
- Mỗi file `tram/` ≤ 120 dòng, mỗi dòng ≤ 120 ký tự (`tests/test_do_dai_ma.py`). Sau lát (đếm thật): `tram/giao_viec/gh.py` 114, `tu_merge_rao.py` 113, `tu_merge.py` 102, `tu_merge_gui.py` 81, `tu_merge_xet.py` 77, `tu_merge_tuoi.py` 22, `tick_cot_3.py` 51, `gh_tu_merge.py` 48, `tick_github.py` 40, `tram/api/tuyen_tu_dong.py` **104** (TM-1: 102), `tram/suy/tu_dong.py` **31** (TM-1: 29), `tram/suy/tu_merge.py` 46. Không vòng import cấp module (`tests/test_vong_import.py`).
- Bí mật / nội dung: sự kiện `tu_merge.*` chỉ mang mã lý do cố định, mã thao tác, SHA, số PR — không tiêu đề bead, không tên file, không từ khoá, không đầu ra `gh` (`LoiGh` chỉ có mã thoát). Dashboard `cho_dai_ca` không trả SHA. Tin Telegram do TM-1 soạn (chỉ dự án, mã bead, loại).
- Git của lát chỉ ĐỌC (`merge-base`, `diff`, `ls-tree`); lời gọi mới trong `tu_merge_rao.py` có hạn 60 giây (`HAN_GIT`) — hết hạn/lỗi → `file_lenh_loi`, luôn chờ.
- Hunk viết trên `85ce7f4`; áp theo NỘI DUNG (`git apply --check` trước; không sạch thì DỪNG, báo điều phối). Một task một commit trên nhánh task; không push, không merge, không `bd` ghi.

## Bảng G — điều plan bảo đảm và bằng chứng

| # | Bảo đảm | Ở đâu | Bằng chứng offline |
|---|---|---|---|
| G1 | Công tắc tắt (mặc định) → không đọc thêm GitHub, không ghi `tu_merge.*`, bead chờ Đại ca như trước | `xet_tu_merge`, `tu_merge_spec` (dòng đầu) | `test_cong_tac_tat_khong_doc_github_khong_ghi_gi`, `test_cong_tac_tat_thi_pr_spec_cho_dai_ca`; cả bộ test cũ (`test_tick_4c`, `test_pr`) xanh không sửa |
| G2 | Lệnh merge chỉ một dạng `--merge --match-head-commit <commit đã kiểm>`; mọi cờ khác bị cửa `_gh` từ chối; mã `tram/` không chứa chuỗi cờ cấm | `gh_tu_merge.dang_merge`, `la_dang_merge`, `GhCli._gh`, `merge_pr` | `test_merge_chi_mot_dang_chat`, `test_dang_merge_duy_nhat` |
| G3 | CI: mọi kiểm tra xong + đạt mới xanh; một cái hỏng = đỏ; còn chạy = chờ (không lỗi); không có CI = chưa xanh (D93); dạng lạ = chưa xanh | `gh_tu_merge.trang_thai_ci`, `GhCli.xem_pr` | `test_trang_thai_ci` (15 ca), `test_xem_pr_doc_ci_tren_dau_pr` |
| G4 | Xét điều kiện là hàm thuần, thứ tự cố định estop → tạm dừng toàn trạm → tạm dừng dự án → `bat_ghi` → công tắc → QC → kiểm lại → đúng PR → đầu PR → cấu trúc DB/xoá dữ liệu → file ba lệnh dùng (D89) → CI → cột → hàng rào; QC, kiểm lại, cấu trúc DB, file lệnh không theo nút; spike không QC → không tự merge (D121) | `tu_merge_xet.ly_do_chua_merge` | `test_moi_scenario_mot_dong` (23 ca), `test_thu_tu_ly_do_co_dinh` |
| G5 | QC và kiểm lại tính lại từ sự kiện cho đúng bằng chứng hiện hành, QC do khe khác khe code (INV-006), không biết khe QC → không đạt | `kiem_lai_qc` | `test_kiem_lai_qc_tinh_lai_tu_su_kien` |
| G6 | Hàng rào chỉ theo đường dẫn diff từ gốc nhánh (D91); `schema` theo đường dẫn + từ khoá nội dung bead, luôn chặn (D76, D92, D112); cờ đỏ (kể cả "gitnexus lỗi") không khớp loại nào vẫn là chạm (D120); không đọc được diff → luôn chờ | `tu_merge_rao.cham_rao` | `test_dieu_kien_tren_du_lieu_that` (9 ca trên Git thật), `test_khong_doc_duoc_diff_thi_luon_cho` |
| G7 | V2-C1: đọc lại bead/sự kiện sau Git/GitHub, tái kiểm seal/PR/QC/kiểm lại/hàng rào; spec tái kiểm bản duyệt và bead. `test_tu_merge_tuoi.py` qua caller thật. Đọc lại cài đặt, TẠM DỪNG dự án/toàn trạm, estop, `bat_ghi` SAU lệnh `gh pr view` (lệnh chậm), ngay trước khi ghi `bat_dau` và gửi merge | `xet_tu_merge.ly_do`, `gui_merge` | `test_doc_lai_ngay_truoc_lenh_merge` (6 ca: đột biến "đọc một lần đầu vòng" → 5 đỏ) |
| G8 | `tu_merge.bat_dau` ghi TRƯỚC lệnh; kết quả không rõ → vòng sau đọc PR: đã merge → `xong`; còn mở + đủ điều kiện → gửi lại đúng commit; còn mở mà điều kiện không còn đủ → chờ, ghi lý do (D119); đóng / merge ở đầu khác → `loi`; lần gửi thứ 3 lỗi vẫn đối soát ở vòng sau (có thể GitHub đã merge) rồi mới `loi`, không gửi lần 4 | `tu_merge_gui.gui_merge` | `test_tram_tat_ngay_sau_lenh_merge_thi_doi_soat`, `test_con_mo_thi_gui_lai_cung_commit_ba_lan_roi_loi`, `test_lan_ba_mat_phan_hoi_van_doi_soat_thanh_cong`, `test_dau_pr_doi_hay_pr_dong` |
| G9 | `tu_merge.cho` chỉ ghi khi lý do đổi (không ghi mỗi vòng tick) | `ghi_cho` | `test_ci_cho_khong_ghi_lap_moi_vong` (đột biến bỏ so sánh → đỏ) |
| G10 | Sau tự merge, luồng xác minh có sẵn đóng bead; tin `tu_merge` sinh từ `tu_merge.xong` (TM-1) | `buoc_github`, `kiem_merge` (không sửa) | `test_tu_merge_roi_xac_minh_dong_bead` |
| G11 | PR spec đã duyệt tự gộp khi bật; đầu PR khác commit duyệt → chờ; tắt → chờ; điều kiện 8 thấy commit vào nhánh chính | `tu_merge_spec` | `test_tu_merge_spec.py` (5 test) |
| G12 | Dashboard: `cho_dai_ca` tính lúc đọc từ sự kiện, lời thường, không SHA; tiêu đề bead ghép lúc đọc từ bộ đệm Beads (chỉ đọc khi có việc chờ, Beads lỗi → rỗng), không vào sự kiện; công tắc tắt → `[]` | `tram/suy/tu_merge.py`, `chi_tiet_du_an`, `tram.suy.tu_merge.tieu_de_bead` | `test_suy_tu_merge.py` (2 test) |
| G13 | Ghép không đổi hành vi khi công tắc tắt; cả bộ xanh | — | Test công tắc tắt xanh; **cổng cả bộ chưa đạt do sandbox**, xem Kiểm chứng plan |
| G14 | **D89 tại cửa merge** (Codex Q2, C2): ngay trước `gh pr merge` (sau `gh pr view`), tập file cấm tính lại từ ba lệnh của CÀI ĐẶT HIỆN HÀNH so với diff PR; chạm → chờ `file_lenh` (luôn, không theo nút, không bị `duong_dan_cam_cho_phep` miễn, dấu QC cũ không thay được); không đọc được cây → `file_lenh_loi`; áp cả PR spec. Token tuyệt đối/tương đối/sau `=`/thư mục; `..` thoát gốc → ngoài repo; symlink trong cây → chờ bảo thủ `file_lenh_loi` | `tu_merge_rao.cham_file_lenh`, `loai_trong_repo`; `xet_tu_merge.ly_do`, `tu_merge_spec.ly_do` | `test_doi_lenh_trong_luc_doc_pr_thi_cho_file_lenh` (5 ca, đổi lệnh trong lúc đọc PR), `test_loai_trong_repo_theo_cay_git`, `test_cham_file_lenh`, `test_pr_spec_sua_file_lenh_thi_cho` |
| G15 | Con của feature `theo-plan` có spec đã vào nhánh chính đi được vòng tick thật: cột 3 → PR → tự merge → đóng; spec chưa vào → chưa vào cột 3 (Codex Q3) | `tick_cot_3.vao_cot_3_an_toan` | `test_con_feature_spec_da_merge_vao_cot_3_roi_tu_merge`, `test_con_feature_spec_chua_merge_thi_chua_vao_cot_3` |

## Thiết kế — các chỗ chọn

1. **Điểm nối và thứ tự trong `buoc_github`** (design D-1). `mo_pr_bead(...) or xet_tu_merge(...) or kiem_merge(...)`: bước mới chỉ chạy khi `mo_pr_bead` không làm gì (PR đã có `pr.mo` cho commit hiện hành). `xet_tu_merge` trả `None` mọi khi nó không merge (chờ điều kiện, công tắc tắt, Đại ca đã merge tay) để `kiem_merge` chạy tiếp trong cùng vòng — Đại ca merge tay vẫn được xác minh ngay. Sau khi trạm merge (`"tu_merge"`), `kiem_merge` xác minh ở vòng sau (đầu vòng `vong_git` có `git fetch`).
2. **"Ngay trước lúc merge" nghĩa là sau lệnh chậm (V2-C1).** Nguồn `bd` từ caller thật, không bộ đệm: sau `gh pr view` và đọc cây Git, đọc `bd.tat_ca()` rồi `su_kien_bead`; sau đó tính lại seal, PR hiện hành, QC, kiểm lại và hàng rào theo bead mới. PR spec kiểm feature, trạng thái/nội dung/nhãn, sự kiện duyệt và PR còn nguyên. Lỗi đọc/mất bead → `du_lieu_loi`; spec đổi → `du_lieu_doi`. Không giữ giao dịch SQLite trong lúc đọc Beads.  Dòng đầu `xet_tu_merge` đọc công tắc chỉ để lọc rẻ (tắt → không gọi GitHub). Cài đặt, TẠM DỪNG, estop, `bat_ghi` được đọc LẠI trong `ly_do(pr)` — gọi sau `gh pr view` (tới 60 giây) và sau mọi lệnh Git, ngay trước khi ghi `bat_dau` và gửi merge. Kiểm D89 có thể đọc cây Git chậm, nên sau nó còn đọc lại khoá/cài đặt lần cuối; nếu cài đặt đã đổi thì chờ `file_lenh_loi`, không gửi trên kết quả D89 cũ. Khoảng hở còn lại nằm giữa lần đọc cuối và gửi; GitHub không có "merge nếu trạm còn cho phép" nên không đóng được hơn.
3. **Đối soát: PR còn mở nhưng điều kiện không còn đủ → chờ (ghi lý do), không báo lỗi.** Design D-7 viết "`OPEN` và điều kiện vẫn đủ → gửi lại; khác → `tu_merge.loi`". Plan hiểu "khác" là trạng thái PR khác (`CLOSED`, hay `MERGED` ở đầu khác commit đã kiểm) → `loi`; còn PR mở mà Đại ca vừa bấm TẠM DỪNG / CI đỏ lại → `tu_merge.cho` như mọi lần chờ. Lý do: báo "trạm lỗi" và ngừng hẳn bead chỉ vì Đại ca tạm dừng là sai nghĩa. **Đại ca chốt D119: chờ, ghi lý do** — mã khớp (`gui_merge`: `ly_do(pr)` khác rỗng → `ghi_cho`, return None, xét trước bộ đếm 3 lần).
4. **Đếm 3 lần bằng chính `tu_merge.bat_dau`** (khoá `ma_thao_tac` + `lan`): mỗi lần gửi một dòng ghi trước lệnh, không thêm loại sự kiện. Lần gửi thứ 3 lỗi vẫn chờ đối soát ở vòng sau: đã merge thì ghi `xong`, còn mở và đủ điều kiện thì ghi `tu_merge.loi {ma_loi: gh-loi-3-lan}`, không gửi lần thứ tư. Lần không rõ (trạm tắt sau `bat_dau`) cũng tính một lần. Sau `merge_pr` thành công trạm ĐỌC LẠI PR — chỉ thấy `MERGED` mới ghi `xong` (GitHub có thể nhận lệnh mà chưa merge, vd hàng đợi merge); chưa thấy thì vòng sau đối soát.
5. **QC/kiểm lại tính lại, không tin nhãn.** `kiem_lai_qc` dùng lại `bo_bang_chung` (đúng hàm đã dựng bằng chứng cột 3) hai lần: không QC (lượt code mới nhất đã kiểm lại đạt đúng commit) và có QC (QC đạt sau đó, đúng commit), so với `bead.vao_cot_3` hiện hành; thêm kiểm khe QC khác khe code từ hai sự kiện `giao.nhan`. Spike (không có QC) không bao giờ tự merge — khoá cứng QC không có ngoại lệ (**Đại ca chốt D121** — mã khớp: `bo_bang_chung(..., la_spike=False)` của spike trả None → `qc`).
6. **Hàng rào theo diff, tính lại tại `commit_ban_giao`** (D91): `tep_doi(goc_nhanh(...))` như `bang_chung.co_do`, khớp `duong_dan` từng loại → mã `hang_rao_<loai>`. `schema` tách riêng, luôn chặn: đường dẫn **hoặc** từ khoá nội dung bead — dùng lại `tram.cham_cot.luat_cung.kiem` với một hàng rào chỉ có từ khoá của `schema` (D92, D112). Bead mang `co-do` (vd cờ đỏ theo gitnexus, hay `gitnexus-loi`) mà không khớp loại nào → `hang_rao_co_do` (**Đại ca chốt D120: có tính chạm** — mã khớp: nhãn `co-do` hoặc `co_do` của `bead.vao_cot_3`). Không đọc được diff → `diff_loi`, luôn chờ.
7. **Cột (D90) = không có `cot-khoa`.** Mọi `giao.nhan` chỉ được cấp khi bead đúng `cot:ai-lam` (`dieu_kien.ly_do_khong_giao`), và bằng chứng hiện hành đòi `giao.nhan` của lượt code — nên phần "đi từ cột 1 theo luồng tự động" đã đúng theo cách dựng; điều còn phải xét là dấu Đại ca tự gán cột.
8. **`bat_ghi` đọc lại từ `du-an/<ten>.yaml`** (`tram.cau_hinh.bat_ghi`), đọc lỗi = `false` — dù `cac_du_an_that` đã bỏ dự án `bat_ghi: false` khỏi vòng tick, Đại ca có thể sửa file giữa vòng (INV-005).
9. **Kênh ghi không xét ở vòng tick.** Design D-11 liệt kê "kênh ghi không chặn" cho PR spec. Kênh ghi là cửa của dashboard; D87 đã chặn mọi lệnh bật công tắc qua kênh `header`, nên công tắc chỉ bật được qua cửa thật. Plan không đọc `cach_ly.kenh_ghi` trong vòng tick (cả bead lẫn spec) — **Đại ca chốt D122: không xét** (luật kênh chỉ áp cho nút dashboard) — mã khớp: `tram/giao_viec/tu_merge*.py` không import `cach_ly`.
10. **Chờ Đại ca tính lúc đọc** (`tram/suy/tu_merge.py`): mỗi bead lấy sự kiện mới nhất trong nhóm `tu_merge.*`, `pr.da_merge`, `pr.khong_xac_minh`, `cot.tra_ve`, `cot.dai_ca_sua`, `bead.dong`; còn chờ khi mới nhất là `tu_merge.cho` / `tu_merge.loi` / `pr.khong_xac_minh`. Tiêu đề bead KHÔNG nằm trong sự kiện; tuyến GET ghép `tieu_de` lúc đọc từ bộ đệm Beads của tram-api (`pt.bo_dem`, như `/api/du-an`), chỉ khi có việc chờ — theo dạng TM-4 cần. Hàm đọc tiêu đề (`tieu_de_bead`) nằm ở `tram/suy/tu_merge.py`, không ở router (Codex Q15: router chung với TM-1/TM-3 chỉ thêm dòng gọi).
11. **D89 tại cửa merge (Codex Q2, C2).** Kiểm lại/QC chạy với ba lệnh của LÚC ĐÓ; Đại ca có thể đổi lệnh sau QC sang một script mà PR đang sửa. Vì vậy `ly_do(pr)` — đúng chỗ đã đọc lại công tắc, sau `gh pr view` — tính lại tập cấm từ `tt.cai_dat` vừa đọc (`tram.tu_dong.file_cam.duong_dan_tu_lenh`, hợp đồng D89 mới) và so với diff PR (`khop_mau` của kiểm đường cấm, không phân biệt hoa thường). Chạm → `file_lenh`, mục `loi`: luôn chờ, không nút nào tắt được, không đọc `duong_dan_cam_cho_phep` (tập BẮT BUỘC — Codex C2), không có đường "QC cũ đã đạt nên merge". Callback `loai_trong_repo` dựng từ gốc đáng tin: cây Git của kho kiểm ở commit PR **và** nhánh chính (`git ls-tree -r -t`, một lần mỗi ref, có hạn 60 giây — tạo mới hay xoá script lệnh sẽ chạy đều bị bắt); token tuyệt đối đổi theo `da.duong_dan` / kho kiểm (cả dạng đã `resolve`); `..` thoát gốc → ngoài repo; một đoạn là symlink trong cây → chờ bảo thủ `file_lenh_loi`, không đi theo; gốc repo (`.`) không thành mẫu cấm cả repo. Không đọc được cây → `file_lenh_loi` (luôn chờ). Áp cho cả PR spec (D95 bỏ năm điều kiện của việc code, không bỏ D89).
12. **Con của feature `theo-plan` (Codex Q3).** `vao_cot_3_an_toan` xét lại §5.1 trên bản Beads vừa đọc nhưng thiếu tập "spec đã merge" → con không bao giờ vào cột 3. Sửa: tính `feature_da_merge` cho đúng feature cha của bản vừa đọc (không gọi Git khi bead không có cha). Đường thật có test tích hợp tới tận merge (Task 6).

## Bản đồ tác động và cổng khảo sát (`DEVELOPMENT_PLAYBOOK.md`)

- **Package/file:** mới `tram/giao_viec/{gh_tu_merge,tu_merge_xet,tu_merge_gui,tu_merge_rao,tu_merge}.py`, `tram/suy/tu_merge.py`; sửa `tram/giao_viec/{gh,tick_github,tick_cot_3}.py`, `tram/suy/tu_dong.py` (1 dòng import + 1 khoá), `tram/api/tuyen_tu_dong.py` (1 dòng import + dòng gọi tuyến GET chi tiết), `tests/{gh_gia,test_gh}.py`, `docs/MODULES.md`, `openspec/changes/tu-merge-tu-deploy/tasks.md`. Vòng import mới: `giao_viec.gh → gh_tu_merge`; `giao_viec.tu_merge → tu_merge_rao, tu_dong.luu, cau_hinh.bat_ghi, chu.estop`; `giao_viec.tu_merge_rao → cham_cot.luat_cung, kiem.diff, kiem.duong_dan_cam, tu_dong.file_cam`; `giao_viec.tick_cot_3 → spec_merge`; `suy.tu_merge → giao_viec.tu_merge_xet, beads.bd` — không vòng cấp module (test canh).
- **Lệnh/tuyến:** không lệnh `tram` mới, không tuyến mới; `GET /api/du-an/{ten}/tu-dong` thêm khoá `cho_dai_ca`. **Dữ liệu:** kho sự kiện thêm 4 loại `tu_merge.*` (hợp đồng TM-1); không bảng/cột mới; ghi GitHub: merge PR của trạm vào nhánh chính dự án (chỉ khi công tắc bật). Không chạm LanceDB; Beads chỉ qua luồng cũ (`kiem_merge` đóng bead).
- **Bốn câu `AGENT_RULES.md` §15 cho `gh pr merge`** (đúng bảng design): timeout 60 giây do `chay_gh` áp · hỏng thì Đại ca thấy bead trong "Chờ Đại ca" (lý do), sau 3 lần "Tự merge lỗi — cần Đại ca" + tin "trạm lỗi", PR vẫn mở để merge tay · retry an toàn nhờ `--match-head-commit` + đọc lại PR trước khi gửi lại, tối đa 3 lần · log không lọt gì: `LoiGh` chỉ mã thoát, sự kiện không tiêu đề/tên file/đầu ra.
- **Hỏng thì cổng đóng:** đọc cài đặt lỗi → mặc định tắt (TM-1); `bat_ghi` đọc lỗi → `false`; CI dạng lạ → chưa xanh; không biết khe QC → QC chưa đạt; không đọc được diff → luôn chờ; không đọc được cây Git để tính file ba lệnh dùng → `file_lenh_loi`, luôn chờ; `gh` lỗi → không merge, vòng sau đọc PR lại.
- **Đường lui:** tắt công tắc hoặc TẠM DỪNG (có hiệu lực vòng tick kế); lui mã: revert nhánh — sự kiện mới chỉ là dòng ghi thêm, mã cũ bỏ qua loại lạ; gỡ `"merge"` khỏi `LENH_DUOC_PHEP` là về lại ADR-0007.
- **Chỉ chứng minh trên máy thật (cổng G8, plan tài liệu 6.1–6.4):** cú pháp/hành vi `gh pr merge --match-head-commit` và dạng `statusCheckRollup` của `gh` 2.x thật; bảo vệ nhánh repo nháp chỉ bắt buộc CI xanh (D94).

## Interfaces cho lát sau

- **TM-3** (sẵn sàng deploy sau tự merge vs gộp tay, D96): một merge là tự merge khi có `tu_merge.xong` với `ma_thao_tac == tram.giao_viec.tu_merge_gui.ma_tu_merge(du_an, bead_id, commit_ban_giao)` (với PR spec: `bead_id` = feature, `commit` = commit của `spec.duyet`). `pr.da_merge` vẫn là mốc "đã merge và xác minh". **D89:** TM-3 có thể dùng lại `tram.giao_viec.tu_merge_rao.loai_trong_repo(kg, goc, refs)` làm callback `loai_trong_repo` theo hợp đồng D89 mới (gốc đáng tin, cây Git ở các `refs`, không đi theo symlink, có hạn 60 giây; lỗi Git → ném `subprocess.SubprocessError`/`OSError` cho bên gọi đóng cổng) thay vì viết thêm một bản — không bắt buộc.
- **TM-4** (trang Tự động): `GET /api/du-an/{ten}/tu-dong` → `cho_dai_ca: [{bead_id, tieu_de, luc, ly_do: [{ma, nhan, muc}]}]`, mới → cũ — chứa đúng dạng TM-4 đề nghị (`{bead_id, tieu_de, ly_do: [{ma, nhan}]}`) cộng `luc`, `muc`. **Chọn màu:** mã cấu trúc DB là `schema_duong_dan` / `schema_tu_khoa` (không phải `schema` trơn) — TM-4 chọn màu theo `muc` = `loi` (đỏ: cấu trúc DB, không đọc được diff, tự merge lỗi) | `tat` (xám: `ci_dang_chay`) | `can_nguoi`, hoặc `ma.startsWith('schema')`. Bảng nhãn: `tram.giao_viec.tu_merge_xet.NHAN`, `MUC`. `tieu_de` = `""` khi Beads lỗi. V2-C1 thêm `du_lieu_loi`, `du_lieu_doi` (`muc=can_nguoi`), không đổi dạng dữ liệu. Mã mới vòng 2: `file_lenh` ("Sửa file mà lệnh deploy / kiểm còn sống / lùi dùng — luôn chờ Đại ca"), `file_lenh_loi` (gồm đường lệnh qua symlink chưa chứng minh được an toàn) — cả hai `muc` = `loi` (đỏ).

## Task ↔ file

| Task | Mốc `tasks.md` | ⛔ | File |
|---|---|---|---|
| 1 | 2.2, 2.3 | **mục 5** | Create `tram/giao_viec/gh_tu_merge.py`, `tests/test_gh_tu_merge.py`; Modify `tram/giao_viec/gh.py`, `tests/test_gh.py` |
| 2 | 2.1 | không | Create `tram/giao_viec/tu_merge_xet.py`, `tests/test_tu_merge_xet.py` |
| 3 | 2.4, 2.5, 2.6 (+ D89 tại cửa merge) | **mục 5, 7** | Create `tram/giao_viec/tu_merge_tuoi.py`, `tram/giao_viec/tu_merge_gui.py`, `tram/giao_viec/tu_merge_rao.py`, `tram/giao_viec/tu_merge.py`, `tests/test_tu_merge.py`, `tests/test_tu_merge_rao.py`; Modify `tram/giao_viec/tick_github.py`, `tests/gh_gia.py` |
| 4 | 2.7 | **mục 5, 7** | Modify `tram/giao_viec/tu_merge.py`, `tram/giao_viec/tick_github.py`; Create `tests/test_tu_merge_spec.py`, `tests/test_tu_merge_tuoi.py` |
| 5 | (dashboard 2.x, cho TM-4) | không | Create `tram/suy/tu_merge.py`, `tests/test_suy_tu_merge.py`; Modify `tram/suy/tu_dong.py`, `tram/api/tuyen_tu_dong.py` |
| 6 | (D72 Scenario "Con của feature đã duyệt"; bead `bs-2bd.1.28`) | không | Modify `tram/giao_viec/tick_cot_3.py`; Create `tests/test_tu_merge_con_feature.py` |
| 7 | — | không (docs) | Modify `docs/MODULES.md`, `openspec/changes/tu-merge-tu-deploy/tasks.md` |

Thứ tự bắt buộc 1 → 7 (mỗi task import mã của task trước; test Task 6 dùng bộ dựng của `tests/test_tu_merge.py`). Task 4 sửa lại hai file của Task 3 (thêm nhánh PR spec) — bản vá Task 4 viết trên kết quả Task 3.

## Tasks

### Task 1: Lệnh `gh pr merge` chặt và đọc CI (design D-2, D-3; D93) ⛔ kill list mục 5

**Scenario:** "CI đang chạy", "CI đỏ" (phần đọc), D93 "không có CI = chưa xanh"; "Merge rồi xác minh như luồng hiện có" (merge commit thường); "Đầu PR đổi sau khi kiểm" (phần GitHub từ chối nhờ `--match-head-commit`).

**Interfaces:** `gh_tu_merge.dang_merge(repo, so, commit) -> list[str] | None`, `la_dang_merge(args) -> bool`, `trang_thai_ci(ds) -> "xanh" | "do" | "dang_chay" | "rong"`, `REPO_RE`, `SHA_RE` (chuyển từ `gh.py`, `gh.py` nhập lại nên tên cũ vẫn dùng được). `GhCli.merge_pr(repo, so, commit) -> None` (lỗi/không rõ → `LoiGh`); `PrInfo.ci: str | None = None` (chỉ `xem_pr` đọc).

- [ ] **Step 0: Kiểm điều kiện vào** — Đại ca đã duyệt plan (kill list mục 5, 7; D119–D122 đã chốt). **TM-1 vòng 2** đã ghép `main` (`grep -q "def _mau" tram/tu_dong/file_cam.py` — hợp đồng D89 mới; thiếu thì DỪNG). `git diff 85ce7f4 HEAD -- tram/giao_viec/gh.py tram/giao_viec/tick_github.py tram/giao_viec/tick_cot_3.py tram/suy/tu_dong.py tram/api/tuyen_tu_dong.py tram/tu_dong/file_cam.py tests/gh_gia.py tests/test_gh.py docs/MODULES.md openspec/changes/tu-merge-tu-deploy/tasks.md` rỗng; khác thì `git apply --check` từng bản vá, hỏng thì DỪNG. Đo N₀: `tests/chan_host/chay.sh -q` → mong đợi `3422` (nền `85ce7f4`), 0 dòng chặn mới.

- [ ] **Step 1: Viết test**

Tạo mới `tests/test_gh_tu_merge.py` (nguyên văn):

```python
"""TM-2 (spec `tu-merge` "Điều kiện CI GitHub xanh", D93; design D-2, D-3): đọc CI từ `statusCheckRollup`, dạng duy
nhất của lệnh merge. Hàm thuần — không `gh`, không mạng."""
import pytest

from tram.giao_viec.gh_tu_merge import dang_merge, la_dang_merge, trang_thai_ci

R, H = "dai-ca/repo-nhap", "c" * 40


def run(status="COMPLETED", conclusion="SUCCESS"):
    return {"__typename": "CheckRun", "name": "test", "status": status, "conclusion": conclusion}


def ctx(state):
    return {"__typename": "StatusContext", "context": "ci/x", "state": state}


@pytest.mark.parametrize("ds, ky_vong", [
    ([], "rong"),                                                            # D93: không có CI = chưa xanh
    ([run(), run(conclusion="NEUTRAL"), run(conclusion="SKIPPED"), ctx("SUCCESS")], "xanh"),
    ([run(), run(status="IN_PROGRESS", conclusion="")], "dang_chay"),         # Scenario "CI đang chạy"
    ([run(status="QUEUED", conclusion=None), ctx("PENDING")], "dang_chay"),
    ([ctx("EXPECTED")], "dang_chay"),
    ([run(), run(conclusion="FAILURE")], "do"),                               # Scenario "CI đỏ"
    ([run(status="IN_PROGRESS"), run(conclusion="CANCELLED")], "do"),         # một cái hỏng là đỏ, dù cái khác chạy
    ([run(conclusion="TIMED_OUT")], "do"), ([run(conclusion="ACTION_REQUIRED")], "do"), ([ctx("ERROR")], "do"),
    ([ctx("FAILURE")], "do"), ([{"__typename": "Lạ"}], "do"), (["x"], "do"), (None, "do"), ({"a": 1}, "do"),
])
def test_trang_thai_ci(ds, ky_vong):
    assert trang_thai_ci(ds) == ky_vong


def test_dang_merge_duy_nhat():
    a = dang_merge(R, 12, H)
    assert a == ["12", "--repo", R, "--merge", "--match-head-commit", H] and la_dang_merge(tuple(a))
    assert dang_merge("x y", 12, H) is None and dang_merge(R, 0, H) is None and dang_merge(R, True, H) is None
    assert dang_merge(R, 12, "C" * 40) is None and dang_merge(R, 12, H[:39]) is None
    assert not la_dang_merge(("12", "--repo", R, "--squash", "--match-head-commit", H))
    assert not la_dang_merge(("+12", "--repo", R, "--merge", "--match-head-commit", H))
    assert not la_dang_merge(("12", "--repo", R, "--merge", "--match-head-commit", H, "--admin"))
```

Sửa `tests/test_gh.py` (bản vá, áp bằng `git apply`):

```diff
--- a/tests/test_gh.py
+++ b/tests/test_gh.py
@@ -1,4 +1,5 @@
-"""Adapter `gh` (lát 4c): chỉ đọc/mở PR, kiểm dạng JSON, không bao giờ merge (Q7). `gh` thật KHÔNG chạy."""
+"""Adapter `gh` (lát 4c): đọc/mở PR, kiểm dạng JSON; TM-2 (design D-3): merge đúng MỘT dạng chặt, đọc CI ở `view`.
+`gh` thật KHÔNG chạy."""
 import json
 import re
 from pathlib import Path
@@ -59,13 +60,40 @@
     assert argv[argv.index("--body-file") + 1] == "-" and dau_vao == "thân @ai $(rm -rf /)"
 
 
-def test_khong_bao_gio_merge():
-    assert LENH_DUOC_PHEP == {"list", "view", "create"}
-    with pytest.raises(LoiGh):
-        GhCli(Chay())._gh("merge", "7")
+def test_merge_chi_mot_dang_chat():
+    """Mốc 2.3: chỉ `gh pr merge <so> --repo <r> --merge --match-head-commit <sha>`; cờ khác không bao giờ chạy."""
+    assert LENH_DUOC_PHEP == {"list", "view", "create", "merge"}
+    c = Chay((0, "", ""))
+    GhCli(c).merge_pr(R, 7, H)
+    assert c.goi == [(["gh", "pr", "merge", "7", "--repo", R, "--merge", "--match-head-commit", H], None)]
+    for co in ("--admin", "--squash", "--rebase", "--auto", "--delete-branch"):
+        with pytest.raises(LoiGh, match="không được phép"):
+            GhCli(Chay())._gh("merge", "7", "--repo", R, "--merge", "--match-head-commit", H, co)
+        with pytest.raises(LoiGh, match="không được phép"):
+            GhCli(Chay())._gh("merge", "7", "--repo", R, co, "--match-head-commit", H)
+    for sai in (("7", "--repo", R, "--merge"), ("07", "--repo", R, "--merge", "--match-head-commit", H),
+                ("7", "--repo", "a b", "--merge", "--match-head-commit", H), ("7", "--repo", R, "--merge",
+                                                                              "--match-head-commit", "abc")):
+        with pytest.raises(LoiGh, match="không được phép"):
+            GhCli(Chay())._gh("merge", *sai)
+    for so, commit in ((0, H), ("7", H), (7, "B" * 40)):
+        with pytest.raises(LoiGh, match="tham số"):
+            GhCli(Chay()).merge_pr(R, so, commit)
+    with pytest.raises(LoiGh, match="lỗi 1"):
+        GhCli(Chay((1, "", "Pull request is not mergeable"))).merge_pr(R, 7, H)
     goc = Path(__file__).resolve().parents[1] / "tram"
     for f in goc.rglob("*.py"):
-        assert not re.search(r"""["']merge["']\s*,\s*["']--(auto|squash|rebase|merge|admin)""", f.read_text()), f
+        assert not re.search(r"--(admin|squash|rebase|auto|delete-branch)\b", f.read_text()), f
+
+
+def test_xem_pr_doc_ci_tren_dau_pr():
+    xanh = [{"__typename": "CheckRun", "status": "COMPLETED", "conclusion": "SUCCESS"}]
+    c = Chay((0, json.dumps(pr(statusCheckRollup=xanh)), ""), (0, json.dumps([pr()]), ""))
+    assert GhCli(c).xem_pr(R, 7).ci == "xanh"
+    argv = c.goi[0][0]
+    assert argv[:4] == ["gh", "pr", "view", "7"] and argv[argv.index("--json") + 1].endswith(",statusCheckRollup")
+    assert GhCli(c).ds_pr(R, "tram/hr-1")[0].ci is None                     # `list` không đọc CI
+    assert GhCli(Chay((0, json.dumps(pr(statusCheckRollup="lạ")), ""))).xem_pr(R, 7).ci == "do"
 
 
 @pytest.mark.parametrize("url,ky_vong", [
```

- [ ] **Step 2: Chạy, mong đợi ĐỎ**

```bash
tests/chan_host/chay.sh -q tests/test_gh.py tests/test_gh_tu_merge.py
```
Đỏ thật (khi viết plan): lỗi khi thu thập — dừng trước khi chạy `test_gh.py`:

```
E   ModuleNotFoundError: No module named 'tram.giao_viec.gh_tu_merge'
ERROR tests/test_gh_tu_merge.py
1 error in 0.11s
```
thoát 2, nhật ký chặn 0 dòng mới.
Riêng `tests/chan_host/chay.sh -q tests/test_gh.py` trên `gh.py` gốc (đã có `gh_tu_merge.py`): `2 failed, 15 passed in 0.24s` — `test_merge_chi_mot_dang_chat` (AssertionError: `LENH_DUOC_PHEP` chưa có `merge`), `test_xem_pr_doc_ci_tren_dau_pr` (AttributeError: `PrInfo` chưa có `ci`).

- [ ] **Step 3: Viết mã**

Tạo mới `tram/giao_viec/gh_tu_merge.py` (nguyên văn):

```python
"""Phần `gh` của tự merge (change `tu-merge-tu-deploy`, design D-2, D-3; D93): dạng DUY NHẤT của lệnh merge và đọc
CI từ `statusCheckRollup` của `gh pr view`. Hàm thuần — `gh.py` gọi.

Lệnh merge chỉ có một dạng: `gh pr merge <so> --repo <owner/repo> --merge --match-head-commit <sha>` — merge commit
thường (xác minh merge hiện có không chứng minh được squash/rebase), GitHub từ chối nếu đầu PR đã khác commit đã kiểm.
Không bao giờ thêm cờ khác (quyền quản trị, gộp dồn, tự động, xoá nhánh)."""
import re

SHA_RE = re.compile(r"[0-9a-f]{40}")
REPO_RE = re.compile(r"[A-Za-z0-9-]{1,39}/[A-Za-z0-9._-]{1,100}")
KET_LUAN_XANH = frozenset({"SUCCESS", "NEUTRAL", "SKIPPED"})
CI = ("xanh", "do", "dang_chay", "rong")


def dang_merge(repo: str, so: int, commit: str) -> list[str] | None:
    """Đối số sau `gh pr merge` — None khi tham số không hợp lệ (không chạy gì)."""
    if not REPO_RE.fullmatch(repo) or type(so) is not int or so <= 0 or not SHA_RE.fullmatch(commit):
        return None
    return [str(so), "--repo", repo, "--merge", "--match-head-commit", commit]


def la_dang_merge(args: tuple[str, ...]) -> bool:
    """Chặn ở cửa `GhCli._gh`: đối số của `merge` phải đúng y dạng `dang_merge` sinh ra."""
    return (len(args) == 6 and args[0].isdigit() and args[0] == str(int(args[0]))
            and dang_merge(args[2], int(args[0]), args[5]) == list(args))


def _mot(c: object) -> str:
    if not isinstance(c, dict):
        return "do"
    if c.get("__typename") == "CheckRun":
        if c.get("status") != "COMPLETED":
            return "dang_chay"
        return "xanh" if c.get("conclusion") in KET_LUAN_XANH else "do"
    if c.get("__typename") == "StatusContext":
        s = c.get("state")
        return "xanh" if s == "SUCCESS" else "dang_chay" if s in ("PENDING", "EXPECTED") else "do"
    return "do"                                 # dạng lạ → coi là chưa xanh (đóng khi không biết)


def trang_thai_ci(ds: object) -> str:
    """`xanh` khi MỌI kiểm tra đã xong và đạt; một cái hỏng → `do`; còn chạy → `dang_chay`; không có → `rong` (D93)."""
    if not isinstance(ds, list):
        return "do"
    if not ds:
        return "rong"
    kq = {_mot(c) for c in ds}
    return "do" if "do" in kq else "dang_chay" if "dang_chay" in kq else "xanh"
```

Sửa `tram/giao_viec/gh.py` (bản vá, áp bằng `git apply`):

```diff
--- a/tram/giao_viec/gh.py
+++ b/tram/giao_viec/gh.py
@@ -1,7 +1,7 @@
-"""Adapter `gh` (GitHub CLI) cho lát 4c (spec 4 §6.4 mục 4, §6.5; kiến trúc Q7): CHỈ đọc PR và mở PR.
-Không có hàm merge, đóng hay sửa PR — quyền merge là của Đại ca (Q7). Lệnh chạy bằng danh sách đối số, không
-qua shell, không hỏi tương tác. Hình dạng JSON của `gh pr list/view --json` theo tài liệu gh 2.x — CHỜ S7 kiểm
-trên repo nháp (tài khoản trạm đã `gh auth login`); test dùng bản giả `chay`."""
+"""Adapter `gh` (GitHub CLI) cho lát 4c (spec 4 §6.4 mục 4, §6.5; kiến trúc Q7): đọc PR, mở PR, và (TM-2, D-3)
+merge đúng MỘT dạng chặt khi dự án bật tự merge (`gh_tu_merge.dang_merge`). Không đóng hay sửa PR. Lệnh chạy
+bằng danh sách đối số, không qua shell, không hỏi tương tác. Hình dạng JSON của `gh pr list/view/merge` theo tài
+liệu gh 2.x — CHỜ S7 kiểm trên repo nháp (tài khoản trạm đã `gh auth login`); test dùng bản giả `chay`."""
 import json
 import os
 import re
@@ -10,12 +10,12 @@
 from dataclasses import dataclass
 from pathlib import Path
 
+from tram.giao_viec.gh_tu_merge import REPO_RE, SHA_RE, dang_merge, la_dang_merge, trang_thai_ci
 from tram.giao_viec.git_kiem import GIT
 
 TRUONG = "number,url,state,headRefName,headRefOid,baseRefName,isCrossRepository,mergedAt,mergeCommit"
-LENH_DUOC_PHEP = frozenset({"list", "view", "create"})       # test khoá: không bao giờ `gh pr merge`
-REPO_RE = re.compile(r"[A-Za-z0-9-]{1,39}/[A-Za-z0-9._-]{1,100}")
-SHA_RE = re.compile(r"[0-9a-f]{40}")
+TRUONG_XEM = TRUONG + ",statusCheckRollup"                    # CI trên đầu PR (D-2) — chỉ `view`
+LENH_DUOC_PHEP = frozenset({"list", "view", "create", "merge"})   # `merge`: chỉ dạng `la_dang_merge` (test khoá)
 REMOTE_RE = re.compile(r"(?:https://github\.com/|git@github\.com:|ssh://git@github\.com/)"
                        r"([A-Za-z0-9-]{1,39}/[A-Za-z0-9._-]{1,100}?)(?:\.git)?/?")
 Chay = Callable[[list[str], str | None], tuple[int, str, str]]
@@ -35,6 +35,7 @@
     base: str
     ngoai_repo: bool
     merge_commit: str | None
+    ci: str | None = None    # xanh | do | dang_chay | rong (`gh_tu_merge.trang_thai_ci`); None: lệnh không đọc CI
 
 
 def chay_gh(argv: list[str], dau_vao: str | None) -> tuple[int, str, str]:
@@ -58,7 +59,8 @@
     try:
         so, mc = d["number"], d["mergeCommit"]
         pr = PrInfo(so, d["url"], d["state"], d["headRefName"], d["headRefOid"], d["baseRefName"],
-                    d["isCrossRepository"], mc["oid"] if mc else None)
+                    d["isCrossRepository"], mc["oid"] if mc else None,
+                    trang_thai_ci(d["statusCheckRollup"]) if "statusCheckRollup" in d else None)
     except (TypeError, KeyError) as e:
         raise LoiGh(f"gh trả PR sai dạng: {type(e).__name__}") from None
     if (type(so) is not int or so <= 0 or pr.url != f"https://github.com/{repo}/pull/{so}"
@@ -74,7 +76,7 @@
         self._chay = chay
 
     def _gh(self, lenh: str, *args: str, dau_vao: str | None = None) -> str:
-        if lenh not in LENH_DUOC_PHEP:
+        if lenh not in LENH_DUOC_PHEP or (lenh == "merge" and not la_dang_merge(args)):
             raise LoiGh(f"gh pr {lenh}: không được phép")
         ma, ra, loi = self._chay(["gh", "pr", lenh, *args], dau_vao)
         if ma != 0:
@@ -96,7 +98,7 @@
 
     def xem_pr(self, repo: str, so: int) -> PrInfo:
         try:
-            return _pr(json.loads(self._gh("view", str(so), "--repo", repo, "--json", TRUONG)), repo)
+            return _pr(json.loads(self._gh("view", str(so), "--repo", repo, "--json", TRUONG_XEM)), repo)
         except ValueError:
             raise LoiGh("gh pr view không trả JSON") from None
 
@@ -104,3 +106,9 @@
         """Kết quả không rõ (lỗi sau khi GitHub đã nhận) → người gọi đối soát bằng `ds_pr`, không tạo lại mù."""
         self._gh("create", "--repo", repo, "--head", nhanh, "--base", base, f"--title={tieu_de}",
                  "--body-file", "-", dau_vao=than)
+
+    def merge_pr(self, repo: str, so: int, commit: str) -> None:
+        """Lỗi hay không rõ → `LoiGh`; người gọi ĐỌC LẠI PR trước khi gửi lại (spec `tu-merge`, design D-7)."""
+        if (args := dang_merge(repo, so, commit)) is None:
+            raise LoiGh("gh pr merge: tham số không hợp lệ")
+        self._gh("merge", *args)
```

- [ ] **Step 4: Chạy, mong đợi XANH**

```bash
tests/chan_host/chay.sh -q tests/test_gh.py tests/test_gh_tu_merge.py tests/test_pr.py tests/test_tick_4c.py tests/test_vong_import.py tests/test_do_dai_ma.py
```
Xanh thật phiên tiếp tục: `56 passed in 13.62s` (lệnh trên), nhật ký chặn 0 dòng mới.

Rồi cả bộ: `tests/chan_host/chay.sh -q` → mong đợi `3439 passed` (N₀ + 17 — số tính; số đo thật ở Task 7), nhật ký chặn 0 dòng mới.

- [ ] **Step 5: Commit**

```bash
git add tram/giao_viec/gh_tu_merge.py tram/giao_viec/gh.py tests/test_gh_tu_merge.py tests/test_gh.py
git commit -m "feat(giao-viec): gh pr merge một dạng chặt, đọc CI ở gh pr view (TM-2 Task 1)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

### Task 2: Hàm thuần xét tự merge (design D-2; D70–D72, D76, D90–D93, D112)

**Scenario:** một dòng cho mỗi Scenario của `tu-merge` (mốc 2.1) + "Estop bật", "Dự án chỉ quét thử", "Tạm dừng" của `dieu-khien-tu-dong`; "Khoá cứng QC đạt" (khe khác — INV-006), "Khoá cứng kiểm lại đạt".

**Interfaces:** `DuKien(qc_dat, kiem_lai_dat, dung_pr, dau_pr_dung, schema=(), ci="rong", cot_ai=True, hang_rao=(), file_lenh=())`; `ly_do_chua_merge(tt, dk, *, bat_ghi, estop_bat) -> list[str]`; `ly_do_chua_merge_spec(tt, *, dung_pr, dau_pr_dung, bat_ghi, estop_bat, file_lenh=()) -> list[str]`; `kiem_lai_qc(ds, v) -> (qc_dat, kiem_lai_dat)`; `NHAN` (gồm cả `tram.tu_dong.khoa.NHAN_LY_DO`), `MUC`.

- [ ] **Step 1: Viết test**

Tạo mới `tests/test_tu_merge_xet.py` (nguyên văn):

```python
"""TM-2 mốc 2.1 (spec `tu-merge`, design D-2): hàm thuần xét tự merge — một dòng cho mỗi Scenario; thứ tự lý do cố
định; QC/kiểm lại tính lại từ sự kiện (QC khác khe — INV-006). Không kho, không Git, không `gh`."""
from dataclasses import replace

import pytest

from tram.giao_viec.su_kien import SK
from tram.giao_viec.tu_merge_xet import (MUC, NHAN, DuKien, kiem_lai_qc, ly_do_chua_merge,
                                         ly_do_chua_merge_spec)
from tram.tu_dong.cai_dat import MAC_DINH
from tram.tu_dong.luu import TamDung, TrangThaiTuDong

BAT = TrangThaiTuDong(replace(MAC_DINH, tu_merge=True), "7", None, None)
DU = DuKien(qc_dat=True, kiem_lai_dat=True, dung_pr=True, dau_pr_dung=True, ci="xanh")
TD = TamDung("dai-ca/dashboard", "2026-10-18T03:00:00Z", "")


def _ly(tt=BAT, *, bat_ghi=True, estop_bat=False, **dk):
    return ly_do_chua_merge(tt, replace(DU, **dk), bat_ghi=bat_ghi, estop_bat=estop_bat)


def _nut(**nut):
    return replace(BAT, cai_dat=replace(BAT.cai_dat, **nut))


@pytest.mark.parametrize("canh, ly_do", [
    ("Dự án mới thêm vào trạm (công tắc tắt)", _ly(TrangThaiTuDong(MAC_DINH, "0", None, None))),
    ("Bật cho một dự án: đủ điều kiện", _ly()),
    ("Đầu PR đổi sau khi kiểm", _ly(dau_pr_dung=False)),
    ("PR không do trạm mở", _ly(dung_pr=False)),
    ("QC trả về", _ly(qc_dat=False)),
    ("Kiểm lại không đạt / bằng chứng hết hiệu lực", _ly(kiem_lai_dat=False)),
    ("CI đang chạy", _ly(ci="dang_chay")),
    ("CI đỏ", _ly(ci="do")),
    ("Repo chưa có CI, nút CI bật (D93)", _ly(ci="rong")),
    ("Dự án tắt nút CI", _ly(_nut(dk_ci=False), ci="rong")),
    ("Đại ca đã tự gán cột", _ly(cot_ai=False)),
    ("Tắt nút cột", _ly(_nut(dk_cot=False), cot_ai=False)),
    ("Diff chạm đường dẫn tiền", _ly(hang_rao=("hang_rao_tien",))),
    ("Việc chỉ nhắc từ khoá, code không chạm", _ly(hang_rao=())),
    ("Tắt nút hàng rào vẫn chặn migration", _ly(_nut(dk_hang_rao=False), schema=("schema_duong_dan",),
                                               hang_rao=("hang_rao_co_do",))),
    ("Việc nói tới xoá dữ liệu", _ly(schema=("schema_tu_khoa",))),
    ("Agent sửa file lệnh deploy dùng, tắt nút hàng rào (D89)", _ly(_nut(dk_hang_rao=False), file_lenh=("file_lenh",))),
    ("Thiếu hai điều kiện", _ly(ci="do", hang_rao=("hang_rao_khach_thay",))),
    ("Con của feature đã duyệt", _ly()),
    ("Estop bật", _ly(estop_bat=True)),
    ("Dự án chỉ quét thử", _ly(bat_ghi=False)),
    ("Tạm dừng dự án", _ly(replace(BAT, tam_dung_du_an=TD))),
    ("Toàn trạm tạm dừng", _ly(replace(BAT, tam_dung_tram=TD))),
])
def test_moi_scenario_mot_dong(canh, ly_do):
    ky_vong = {"Dự án mới thêm vào trạm (công tắc tắt)": ["tu_merge_tat"], "Đầu PR đổi sau khi kiểm": ["dau_pr_khac"],
               "PR không do trạm mở": ["pr_khac"], "QC trả về": ["qc"],
               "Kiểm lại không đạt / bằng chứng hết hiệu lực": ["kiem_lai"], "CI đang chạy": ["ci_dang_chay"],
               "CI đỏ": ["ci_do"], "Repo chưa có CI, nút CI bật (D93)": ["ci_rong"], "Đại ca đã tự gán cột": ["cot"],
               "Diff chạm đường dẫn tiền": ["hang_rao_tien"],
               "Tắt nút hàng rào vẫn chặn migration": ["schema_duong_dan"],
               "Việc nói tới xoá dữ liệu": ["schema_tu_khoa"],
               "Agent sửa file lệnh deploy dùng, tắt nút hàng rào (D89)": ["file_lenh"],
               "Thiếu hai điều kiện": ["ci_do", "hang_rao_khach_thay"], "Estop bật": ["estop"],
               "Dự án chỉ quét thử": ["bat_ghi"], "Tạm dừng dự án": ["tam_dung_du_an"],
               "Toàn trạm tạm dừng": ["tam_dung_tram"]}.get(canh, [])
    assert ly_do == ky_vong


def test_nhan_loi_thuong_theo_spec():
    assert NHAN["dau_pr_khac"] == "Đầu PR khác commit đã kiểm" and NHAN["ci_do"] == "CI chưa xanh"
    assert NHAN["hang_rao_tien"] == "Chạm hàng rào: tiền/giá"
    assert NHAN["hang_rao_khach_thay"] == "Chạm hàng rào: thứ khách thấy"
    assert NHAN["schema_duong_dan"] == "Cấu trúc DB — luôn chờ Đại ca"
    assert NHAN["schema_tu_khoa"].endswith("xoá dữ liệu — luôn chờ Đại ca") and NHAN["estop"] == "Estop đang bật"
    assert MUC["schema_duong_dan"] == MUC["schema_tu_khoa"] == "loi" and MUC["ci_dang_chay"] == "tat"
    assert NHAN["file_lenh"].endswith("— luôn chờ Đại ca") and MUC["file_lenh"] == MUC["file_lenh_loi"] == "loi"


def test_thu_tu_ly_do_co_dinh():
    """Design D-2: khoá chung → QC → kiểm lại → đúng PR → đầu PR → cấu trúc DB → file lệnh (D89) → CI → cột → hàng
    rào; tắt cả ba nút vẫn còn cấu trúc DB và file lệnh."""
    het = DuKien(False, False, False, False, ("schema_duong_dan", "schema_tu_khoa"), "do", False,
                 ("hang_rao_tien", "hang_rao_co_do"), ("file_lenh",))
    tt = TrangThaiTuDong(MAC_DINH, "0", TD, TD)
    assert ly_do_chua_merge(tt, het, bat_ghi=False, estop_bat=True) == [
        "estop", "tam_dung_tram", "tam_dung_du_an", "bat_ghi", "tu_merge_tat", "qc", "kiem_lai", "pr_khac",
        "dau_pr_khac", "schema_duong_dan", "schema_tu_khoa", "file_lenh", "ci_do", "cot", "hang_rao_tien",
        "hang_rao_co_do"]
    tat_nut = replace(tt, cai_dat=replace(MAC_DINH, dk_ci=False, dk_cot=False, dk_hang_rao=False))
    assert ly_do_chua_merge(tat_nut, het, bat_ghi=True, estop_bat=False)[-3:] == ["schema_duong_dan",
                                                                                 "schema_tu_khoa", "file_lenh"]
    assert all(m in NHAN for m in ly_do_chua_merge(tt, het, bat_ghi=False, estop_bat=True))


def test_pr_spec_chi_khoa_chung_va_dau_pr():
    """D95, design D-11 — Scenario "Duyệt spec xong", "Nhánh spec đổi sau khi duyệt", "Công tắc tắt"."""
    kw = {"bat_ghi": True, "estop_bat": False}
    assert ly_do_chua_merge_spec(BAT, dung_pr=True, dau_pr_dung=True, **kw) == []
    assert ly_do_chua_merge_spec(BAT, dung_pr=True, dau_pr_dung=False, **kw) == ["dau_pr_khac"]
    assert ly_do_chua_merge_spec(TrangThaiTuDong(MAC_DINH, "0", None, None), dung_pr=True, dau_pr_dung=True,
                                 **kw) == ["tu_merge_tat"]
    assert ly_do_chua_merge_spec(replace(BAT, tam_dung_du_an=TD), dung_pr=False, dau_pr_dung=True,
                                 bat_ghi=True, estop_bat=True) == ["estop", "tam_dung_du_an", "pr_khac"]
    assert ly_do_chua_merge_spec(BAT, dung_pr=True, dau_pr_dung=True, file_lenh=("file_lenh",), **kw) == ["file_lenh"]


C, Q = "a" * 40, "b" * 40


def _ds(*them, khe_qc="B/claude-2", ket_luan="dat", dat=True):
    goc = [("giao.nhan", {"giao_id": "g-1", "luot": 1, "buoc": "code", "khe_id": "B/claude-1"}),
           ("giao.ket_thuc", {"giao_id": "g-1", "ket_thuc": "xong", "ly_do": None, "commit": C}),
           ("kiem.lai", {"giao_id": "g-1", "bead_id": "hr-1", "luot": 1, "commit": C, "digest_tieu_chi": "d",
                         "dat": dat}),
           ("giao.nhan", {"giao_id": "g-2", "luot": 2, "buoc": "qc", "khe_id": khe_qc}),
           ("qc.ket_qua", {"giao_id": "g-2", "commit_code": C, "commit_qc": Q, "ket_luan": ket_luan}),
           ("bead.vao_cot_3", {"commit_code": C, "commit_ban_giao": Q, "giao_id_code": "g-1", "luot_code": 1}),
           *them]
    return [SK(i, l, d, "2026-10-18T03:00:00Z") for i, (l, d) in enumerate(goc, 1)]


def test_kiem_lai_qc_tinh_lai_tu_su_kien():
    ds = _ds()
    v = ds[5]
    assert kiem_lai_qc(ds, v) == (True, True)
    assert kiem_lai_qc(_ds(ket_luan="tra_ve"), v) == (False, True)                 # Scenario "QC trả về"
    assert kiem_lai_qc(_ds(khe_qc="B/claude-1"), v) == (False, True)               # QC cùng khe code (INV-006)
    assert kiem_lai_qc(_ds(khe_qc=None), v) == (False, True)                       # không biết khe QC → không đạt
    assert kiem_lai_qc(_ds(dat=False), v) == (False, False)                        # Scenario "Kiểm lại không đạt"
    moi = _ds(("giao.nhan", {"giao_id": "g-3", "luot": 3, "buoc": "code", "khe_id": "B/claude-1"}))
    assert kiem_lai_qc(moi, v) == (False, False)                                   # lượt code mới chưa kiểm lại
```

- [ ] **Step 2: Chạy, mong đợi ĐỎ**

```bash
tests/chan_host/chay.sh -q tests/test_tu_merge_xet.py
```
Đỏ thật (khi viết plan): lỗi khi thu thập:

```
E   ModuleNotFoundError: No module named 'tram.giao_viec.tu_merge_xet'
ERROR tests/test_tu_merge_xet.py
1 error in 0.12s
```
thoát 2, nhật ký chặn 0 dòng mới.

- [ ] **Step 3: Viết mã**

Tạo mới `tram/giao_viec/tu_merge_xet.py` (nguyên văn):

```python
"""Xét tự merge (spec `tu-merge`, design D-2; D70–D72, D76, D90–D93, D112) — hàm thuần trả danh sách MÃ lý do,
rỗng = được merge. Thứ tự cố định: khoá chung (`tram.tu_dong.khoa`: estop → tạm dừng toàn trạm → tạm dừng dự án →
`bat_ghi` → công tắc) → QC → kiểm lại → đúng PR → đầu PR → cấu trúc DB / xoá dữ liệu (luôn) → file ba lệnh dùng
(luôn, D89) → CI → cột → hàng rào. Ba điều kiện cuối theo nút của dự án; QC, kiểm lại, cấu trúc DB, file lệnh không
có nút (D71, D76, D89). Mã lý do là hợp đồng với
dashboard (`NHAN`, `MUC`) và nằm trong sự kiện `tu_merge.cho` — không chứa tên file, từ khoá hay nội dung bead."""
from dataclasses import dataclass

from tram.giao_viec.bang_chung import bo_bang_chung
from tram.giao_viec.su_kien import SK, cua_so, moi_nhat
from tram.tu_dong.khoa import NHAN_LY_DO, ly_do_chan
from tram.tu_dong.luu import TrangThaiTuDong

NHAN = {**NHAN_LY_DO, "du_lieu_loi": "Không đọc được dữ kiện hiện hành — chờ xét lại",
        "du_lieu_doi": "Dữ kiện duyệt spec đã đổi — chờ xét lại", "qc": "QC chưa đạt cho đúng commit này",
        "kiem_lai": "Kiểm lại chưa đạt hoặc bằng chứng hết hiệu lực", "pr_khac": "PR không phải PR trạm đã mở",
        "dau_pr_khac": "Đầu PR khác commit đã kiểm", "schema_duong_dan": "Cấu trúc DB — luôn chờ Đại ca",
        "schema_tu_khoa": "Nội dung việc nhắc cấu trúc DB / xoá dữ liệu — luôn chờ Đại ca",
        "ci_do": "CI chưa xanh", "ci_rong": "CI chưa xanh — repo chưa có CI",
        "ci_dang_chay": "CI đang chạy — xét lại vòng sau", "cot": "Đại ca đã tự gán cột",
        "hang_rao_tien": "Chạm hàng rào: tiền/giá", "hang_rao_quyen": "Chạm hàng rào: quyền/bảo mật",
        "hang_rao_khach_thay": "Chạm hàng rào: thứ khách thấy", "hang_rao_co_do": "Cờ đỏ",
        "tu_merge_loi": "Tự merge lỗi — cần Đại ca", "pr_khong_xac_minh": "Trạm không xác minh được merge — cần Đại ca",
        "diff_loi": "Không đọc được thay đổi của việc — chờ Đại ca",
        "file_lenh": "Sửa file mà lệnh deploy / kiểm còn sống / lùi dùng — luôn chờ Đại ca",
        "file_lenh_loi": "Không đọc được file mà ba lệnh dùng — chờ Đại ca"}
MUC = {"schema_duong_dan": "loi", "schema_tu_khoa": "loi", "diff_loi": "loi", "tu_merge_loi": "loi",
       "file_lenh": "loi", "file_lenh_loi": "loi", "ci_dang_chay": "tat"}


@dataclass(frozen=True)
class DuKien:
    """Điều trạm đọc được về một bead ở cột 3, tại `commit_ban_giao` của bằng chứng hiện hành."""
    qc_dat: bool
    kiem_lai_dat: bool
    dung_pr: bool                       # PR là PR trạm đã ghi ở `pr.mo`: số, nhánh `tram/<bead>`, base, cùng repo
    dau_pr_dung: bool                   # đầu PR đúng commit đã kiểm
    schema: tuple[str, ...] = ()        # schema_duong_dan, schema_tu_khoa (D76, D92, D112); diff_loi
    ci: str = "rong"                    # xanh | do | dang_chay | rong (D93)
    cot_ai: bool = True                 # không có `cot-khoa` (D90)
    hang_rao: tuple[str, ...] = ()      # hang_rao_<loai> theo đường dẫn diff; hang_rao_co_do (D91)
    file_lenh: tuple[str, ...] = ()     # file_lenh / file_lenh_loi — từ ba lệnh của cài đặt ĐỌC LẠI (D89)


def ly_do_chua_merge(tt: TrangThaiTuDong, dk: DuKien, *, bat_ghi: bool, estop_bat: bool) -> list[str]:
    cd = tt.cai_dat
    ra = ly_do_chan(tt, viec="merge", bat_ghi=bat_ghi, estop_bat=estop_bat)
    ra += [m for m, chan in (("qc", not dk.qc_dat), ("kiem_lai", not dk.kiem_lai_dat), ("pr_khac", not dk.dung_pr),
                             ("dau_pr_khac", not dk.dau_pr_dung)) if chan]
    ra += [*dk.schema, *dk.file_lenh]
    ra += [f"ci_{dk.ci}"] if cd.dk_ci and dk.ci != "xanh" else []
    ra += ["cot"] if cd.dk_cot and not dk.cot_ai else []
    return ra + (list(dk.hang_rao) if cd.dk_hang_rao else [])


def ly_do_chua_merge_spec(tt: TrangThaiTuDong, *, dung_pr: bool, dau_pr_dung: bool, bat_ghi: bool,
                          estop_bat: bool, file_lenh: tuple[str, ...] = ()) -> list[str]:
    """PR spec đã duyệt (D95, design D-11): khoá chung + đúng PR + đầu PR đúng commit của lần duyệt mới nhất + file ba
    lệnh dùng (D89, bắt buộc như việc code). Năm điều kiện còn lại của việc code không áp — lần duyệt của Đại ca thay
    QC, spec chỉ đổi tài liệu đã kiểm lúc `spec.xong`."""
    ra = ly_do_chan(tt, viec="merge", bat_ghi=bat_ghi, estop_bat=estop_bat)
    return ra + [m for m, chan in (("pr_khac", not dung_pr), ("dau_pr_khac", not dau_pr_dung)) if chan] + [*file_lenh]


def kiem_lai_qc(ds: list[SK], v: SK) -> tuple[bool, bool]:
    """(QC đạt, kiểm lại đạt) cho ĐÚNG bằng chứng `v` (`bead.vao_cot_3` hiện hành) — tính lại từ sự kiện, không tin
    nhãn. Kiểm lại: lượt code mới nhất đạt tại `commit_code` của `v`. QC: kết luận đạt sau lần kiểm lại đó, cho đúng
    commit, do khe KHÁC khe đã code (INV-006); thiếu sự kiện nhận việc của khe QC → không đạt (đóng khi không biết)."""
    d, w = v.du_lieu, cua_so(ds)
    kl = bo_bang_chung("", ds, la_spike=True)
    kl_dat = kl is not None and (kl["commit_code"], kl["giao_id_code"]) == (d["commit_code"], d["giao_id_code"])
    bc = bo_bang_chung("", ds, la_spike=False)
    if not kl_dat or bc is None or bc["commit_ban_giao"] != d["commit_ban_giao"]:
        return False, kl_dat
    khe = {s.du_lieu["giao_id"]: s.du_lieu.get("khe_id") for s in w if s.loai == "giao.nhan"}
    qk = moi_nhat(w, "qc.ket_qua")
    return khe.get(qk.du_lieu.get("giao_id")) not in (None, khe.get(bc["giao_id_code"])), True
```

- [ ] **Step 4: Chạy, mong đợi XANH**

```bash
tests/chan_host/chay.sh -q tests/test_tu_merge_xet.py tests/test_vong_import.py tests/test_do_dai_ma.py
```
Xanh thật phiên tiếp tục: `34 passed in 0.71s`, nhật ký chặn 0 dòng mới.

Rồi cả bộ → mong đợi `3466 passed` (số tính), nhật ký chặn 0 dòng mới.

- [ ] **Step 5: Commit**

```bash
git add tram/giao_viec/tu_merge_xet.py tests/test_tu_merge_xet.py
git commit -m "feat(giao-viec): xét điều kiện tự merge — hàm thuần, thứ tự cố định (TM-2 Task 2)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

### Task 3: Bước tự merge trong vòng tick — gửi, đọc lại, đối soát, chờ kèm lý do ⛔ kill list mục 5, 7

**Scenario:** "Dự án mới thêm vào trạm", "Đầu PR đổi sau khi kiểm", "CI đang chạy", "CI đỏ", "Dự án tắt nút CI" (D93), "Đại ca đã tự gán cột", "Tắt nút cột", "Diff chạm đường dẫn tiền", "Việc chỉ nhắc từ khoá", "Tắt nút hàng rào vẫn chặn migration", "Việc nói tới xoá dữ liệu", "Merge xong, xác minh đạt", "Đại ca merge tay", "Trạm tắt ngay sau lệnh merge", "Đại ca bấm tạm dừng giữa vòng tick", "Tạm dừng rồi tiếp tục" (phần tự merge), "Estop bật" (đọc lại), "Dự án chỉ quét thử" (đọc lại), "Tin tự merge" (sự kiện → tin của TM-1); mốc 2.5 không ghi lặp. Vòng 2: Codex sửa trực tiếp #2 (lần gửi thứ 3 lỗi vẫn đối soát — `test_lan_ba_mat_phan_hoi_van_doi_soat_thanh_cong`); D119 (PR còn mở, điều kiện không còn đủ → chờ); **D89 tại cửa merge** (Codex Q2/C2 — "Agent sửa script deploy" của `tu-deploy` ở phía merge: lệnh đổi trong lúc đọc PR).

**Interfaces:** `tu_merge_gui.ma_tu_merge(du_an, bead_id, commit) -> "tm-…"`, `TAC_NHAN = "tram/tu-merge"`, `SO_LAN = 3`, `gui_merge(gh, repo, kho, du_an, bead_id, ds, *, so_pr, commit, loai, ly_do, luc) -> str | None` (`"tu_merge"`, `"tu_merge_gui"`, `"tu_merge_loi"`, None). `tu_merge.xet_tu_merge(gh, repo, kho, kg, da, bd, b, ds, luc) -> str | None`. `tu_merge_rao.doc_tep(kg, da, c) -> list[str] | None`, `cham_rao(da, b, v, tep) -> (schema, hang_rao)`, `loai_trong_repo(kg, goc, refs) -> Callable[[str], (đường dẫn, "file"|"dir") | None]` (callback hợp đồng D89 mới), `cham_file_lenh(cd, kg, da, c, tep) -> () | ("file_lenh",) | ("file_lenh_loi",)`. `GhGia` (test) thêm `merge_pr`, `lam_merge`, `loi_merge`, `mat_phan_hoi_khi_merge`, `khi_xem`.

- [ ] **Step 1: Viết test**

Sửa `tests/gh_gia.py` (bản vá, áp bằng `git apply`):

```diff
--- a/tests/gh_gia.py
+++ b/tests/gh_gia.py
@@ -1,5 +1,8 @@
 """GitHub giả trong bộ nhớ cho test lát 4c (CHỈ DÙNG TRONG TEST): cùng giao diện `GhCli` — không gọi `gh`, không
-mạng. Head của PR mới lấy từ remote Git cục bộ (`head_cua(nhanh)`), như GitHub đọc nhánh trên remote."""
+mạng. Head của PR mới lấy từ remote Git cục bộ (`head_cua(nhanh)`), như GitHub đọc nhánh trên remote.
+TM-2: `merge_pr` như `gh pr merge --merge --match-head-commit` (PR không mở hay đầu PR khác commit → lỗi);
+`lam_merge(pr)` làm merge thật trên remote cục bộ và trả merge commit; `khi_xem(so)` chạy mỗi lần đọc PR (giả
+Đại ca bấm gì đó trong lúc lệnh `gh` đang chạy)."""
 from dataclasses import replace
 
 from tram.giao_viec.gh import LoiGh, PrInfo
@@ -8,8 +11,11 @@
 
 
 class GhGia:
-    def __init__(self, head_cua, *, mat_phan_hoi_khi_tao=False, loi=False):
+    def __init__(self, head_cua, *, mat_phan_hoi_khi_tao=False, loi=False, lam_merge=None, loi_merge=False,
+                 mat_phan_hoi_khi_merge=False, khi_xem=None):
         self.head_cua, self.mat, self.loi = head_cua, mat_phan_hoi_khi_tao, loi
+        self.lam_merge, self.loi_merge, self.mat_merge, self.khi_xem = (lam_merge, loi_merge, mat_phan_hoi_khi_merge,
+                                                                        khi_xem)
         self.prs: dict[int, PrInfo] = {}
         self.goi: list[tuple] = []
 
@@ -24,7 +30,18 @@
 
     def xem_pr(self, repo, so):
         self._kiem("xem_pr", repo, so)
+        if self.khi_xem is not None:
+            self.khi_xem(so)
         return self.prs[so]
+
+    def merge_pr(self, repo, so, commit):
+        self._kiem("merge_pr", repo, so, commit)
+        p = self.prs[so]
+        if self.loi_merge or p.trang_thai != "OPEN" or p.head != commit:
+            raise LoiGh("gh giả: merge bị từ chối")
+        self.prs[so] = replace(p, trang_thai="MERGED", merge_commit=self.lam_merge(p) if self.lam_merge else None)
+        if self.mat_merge:
+            raise LoiGh("mất phản hồi sau khi GitHub đã merge")
 
     def tao_pr(self, repo, nhanh, base, tieu_de, than):
         self._kiem("tao_pr", repo, nhanh, base, tieu_de, than)
```

Tạo mới `tests/test_tu_merge.py` (nguyên văn):

```python
"""TM-2 mốc 2.2, 2.4–2.6 (spec `tu-merge`; `dieu-khien-tu-dong` "Estop dừng cả tự merge", "Kiểm lại công tắc ngay
trước lúc merge"): vòng tick thật trên GitHub giả + Git cục bộ — cột 3 → PR → tự merge → xác minh → đóng bead; chờ
Đại ca kèm lý do (không ghi lặp); đọc lại cài đặt ngay trước lệnh — gồm tập file cấm từ ba lệnh (D89, Codex Q2);
đối soát khi kết quả không rõ; 3 lần lỗi."""
from dataclasses import replace

import pytest

from gh_gia import REPO, GhGia
from giao_viec_gia import TC, bug, dung
from git_gia import git
from su_kien_gia import cong_bo, ds, ket_thuc, kiem, nhan, qc, sk
from test_xet_xong import F, bg
from tram.bao_tin.nguon import tin_tu_su_kien
from tram.bao_tin.tin import Tin
from tram.cau_hinh.du_an import HangRao
from tram.chu import estop
from tram.giao_viec.git_kiem import fetch
from tram.giao_viec.phu_thuoc_4c import PhuThuoc4c
from tram.giao_viec.su_kien import SK
from tram.giao_viec.tu_merge_rao import cham_rao, doc_tep
from tram.giao_viec.tick import mot_vong_tick
from tram.giao_viec.tieu_chi import digest_tieu_chi
from tram.tu_dong.luu import DU_AN_TRAM, doi_cai_dat, ghi_tam_dung

GIU = {"status": "in_progress", "assignee": "tram/giao-viec"}
TIEN = {"tien": HangRao(tu_khoa=("hoá đơn",), duong_dan=("*Modules/Fin/*",))}


def lam_merge(k):
    """Merge commit thường vào `main` của remote cục bộ `k` — như GitHub làm khi nhận `gh pr merge --merge`."""
    def lam(p):
        git(k.dev, "checkout", "-q", "-B", "main", git(k.origin, "rev-parse", "main"))
        git(k.dev, "merge", "-q", "--no-ff", "-m", f"Merge PR #{p.so}", p.head)
        git(k.dev, "push", "-q", "origin", "HEAD:refs/heads/main")
        return git(k.dev, "rev-parse", "HEAD")
    return lam


def doi(t, **kw):
    doi_cai_dat(t.kho.db, "hr-codex", lambda c: replace(c, **kw), tac_nhan="dai-ca/dashboard")


def dung_tu_merge(tmp_path, monkeypatch, *, bat=True, bat_ghi=True, hang_rao=None, tep=None, gh_kw=None, them=(),
                  cho_phep=(), **b_kw):
    """Bead `hr-1` sẵn sàng vào cột 3 (kiểm lại + QC khác khe đạt); `du-an/hr-codex.yaml` giả có `bat_ghi`; `them`:
    bead khác trong Beads giả; `cho_phep`: ngoại lệ đường cấm của dự án (`duong_dan_cam_cho_phep`)."""
    (goc := tmp_path / "repo-tram" / "du-an").mkdir(parents=True)
    (goc / "hr-codex.yaml").write_text(f"ten: hr-codex\nbat_ghi: {'true' if bat_ghi else 'false'}\n")
    monkeypatch.setenv("TRAM_REPO", str(tmp_path / "repo-tram"))
    t = dung(tmp_path, bug(**{**GIU, **b_kw}), *them)
    da = replace(t.da, hang_rao=TIEN if hang_rao is None else hang_rao,
                 giao=replace(t.da.giao, duong_dan_cam_cho_phep=cho_phep))
    t.bo.cac_du_an = lambda: [da]
    gh = GhGia(lambda nhanh: git(t.k.origin, "rev-parse", nhanh), lam_merge=lam_merge(t.k), **(gh_kw or {}))
    t.bo.p4c = PhuThuoc4c(gh=gh, github_repo=lambda kg: REPO)
    c = t.k.day("tram/hr-1", tep or {"src/tom_tat.py": "x = 2\n"}, tu=t.k.main)
    q = t.k.day("tram/hr-1", {F: "qc"}, tu=c)
    nhan(t.kho, "g-1", 1)
    cong_bo(t.kho, 1, c)
    ket_thuc(t.kho, "g-1", 1, commit=c)
    sk(t.kho, "bao.xong", {"giao_id": "g-1", "commit": c, "ban_giao": bg(c)})
    kiem(t.kho, "g-1", c, digest=digest_tieu_chi([TC]))
    nhan(t.kho, "g-2", 2, buoc="qc", khe_id="B/claude-2")                   # QC ở khe khác khe code (INV-006)
    cong_bo(t.kho, 2, q)
    qc(t.kho, "g-2", c, q)
    if bat:
        doi(t, tu_merge=True)
    return t, gh, q


def cot_3_co_pr(t, gh, ci="xanh"):
    r = mot_vong_tick(t.bo)
    assert (r["cot_3"], r["pr_mo"]) == (1, 1)
    gh.dat(1, ci=ci)


def tm(t, loai=None):
    return [s for s in ds(t.kho) if s.loai.startswith("tu_merge.") and (loai is None or s.loai == loai)]


def merge_goi(gh):
    return [g for g in gh.goi if g[0] == "merge_pr"]


def test_tu_merge_roi_xac_minh_dong_bead(tmp_path, monkeypatch):
    """Scenario "Merge xong, xác minh đạt" + "Tin tự merge"; mốc 2.4 luồng xác minh cũ vẫn chạy."""
    t, gh, q = dung_tu_merge(tmp_path, monkeypatch)
    cot_3_co_pr(t, gh)
    assert mot_vong_tick(t.bo)["tu_merge"] == 1 and gh.prs[1].trang_thai == "MERGED"
    assert merge_goi(gh) == [("merge_pr", REPO, 1, q)]
    bd, xong = tm(t)
    assert (bd.loai, bd.du_lieu["commit"], bd.du_lieu["pr"], bd.du_lieu["loai"], bd.du_lieu["lan"]) == (
        "tu_merge.bat_dau", q, 1, "code", 1)
    assert bd.du_lieu["ma_thao_tac"].startswith("tm-") and xong.du_lieu == {"ma_thao_tac": bd.du_lieu["ma_thao_tac"],
                                                                            "loai": "code"}
    assert mot_vong_tick(t.bo)["da_merge"] == 1 and t.g.beads["hr-1"].status == "closed"
    assert len(merge_goi(gh)) == 1 and len(tm(t)) == 2
    sk_xong = t.kho.db.execute("SELECT id, loai, tac_nhan, du_an, bead_id FROM su_kien WHERE loai = 'tu_merge.xong'"
                               ).fetchone()
    assert sk_xong[2] == "tram/tu-merge"
    ban = type("SK", (), {"loai": "tu_merge.xong", "du_an": "hr-codex", "bead_id": "hr-1", "du_lieu": xong.du_lieu,
                          "tac_nhan": sk_xong[2]})
    assert tin_tu_su_kien(ban, None) == [Tin("tu_merge", "hr-codex", "hr-1")]


def test_cong_tac_tat_khong_doc_github_khong_ghi_gi(tmp_path, monkeypatch):
    """Scenario "Dự án mới thêm vào trạm": công tắc tắt → như trước TM-2, chờ Đại ca merge tay."""
    t, gh, q = dung_tu_merge(tmp_path, monkeypatch, bat=False)
    cot_3_co_pr(t, gh)
    gh.goi.clear()
    assert "tu_merge" not in mot_vong_tick(t.bo)
    assert [g[0] for g in gh.goi] == ["xem_pr"] and tm(t) == [] and gh.prs[1].trang_thai == "OPEN"


def test_ci_cho_khong_ghi_lap_moi_vong(tmp_path, monkeypatch):
    """Mốc 2.5 + Scenario "CI đang chạy" (xét lại vòng sau, không lỗi), "CI đỏ"."""
    t, gh, q = dung_tu_merge(tmp_path, monkeypatch)
    cot_3_co_pr(t, gh, ci="dang_chay")
    for _ in range(3):
        r = mot_vong_tick(t.bo)
        assert "tu_merge" not in r and "loi_gh" not in r and "loi" not in r
    assert [s.du_lieu for s in tm(t)] == [{"ly_do": ["ci_dang_chay"], "commit": q}]
    gh.dat(1, ci="do")
    mot_vong_tick(t.bo)
    mot_vong_tick(t.bo)
    assert [s.du_lieu["ly_do"] for s in tm(t)] == [["ci_dang_chay"], ["ci_do"]] and merge_goi(gh) == []
    assert {r[0] for r in t.kho.db.execute("SELECT tac_nhan FROM su_kien WHERE loai LIKE 'tu_merge.%'")} == {
        "tram/tu-merge"}
    gh.dat(1, ci="xanh")
    assert mot_vong_tick(t.bo)["tu_merge"] == 1


@pytest.mark.parametrize("bam, ly_do", [
    (lambda t: ghi_tam_dung(t.kho.db, "hr-codex", tam_dung=True, tac_nhan="dai-ca/dashboard"), ["tam_dung_du_an"]),
    (lambda t: ghi_tam_dung(t.kho.db, DU_AN_TRAM, tam_dung=True, tac_nhan="dai-ca/dashboard"), ["tam_dung_tram"]),
    (lambda t: doi(t, tu_merge=False), ["tu_merge_tat"]),
    (lambda t: doi(t, dk_hang_rao=False), []),                                   # đổi không chặn → vẫn merge
    (lambda t: estop.bat("thử"), ["estop"]),
    (lambda t: (t.k.kho.parent / "repo-tram" / "du-an" / "hr-codex.yaml").write_text(
        "ten: hr-codex\nbat_ghi: false\n"), ["bat_ghi"]),
])
def test_doc_lai_ngay_truoc_lenh_merge(tmp_path, monkeypatch, bam, ly_do):
    """Scenario "Đại ca bấm tạm dừng giữa vòng tick", "Estop bật", "Dự án chỉ quét thử": thay đổi xảy ra SAU khi
    trạm bắt đầu xét (trong lúc chờ `gh pr view`) vẫn chặn lệnh merge."""
    t, gh, q = dung_tu_merge(tmp_path, monkeypatch)
    cot_3_co_pr(t, gh)
    lan = []
    gh.khi_xem = lambda so: lan or (lan.append(1), bam(t))
    try:
        mot_vong_tick(t.bo)
    finally:
        estop.tat()
    if not ly_do:
        assert len(merge_goi(gh)) == 1
        return
    assert merge_goi(gh) == [] and gh.prs[1].trang_thai == "OPEN"
    assert [s.du_lieu["ly_do"] for s in tm(t, "tu_merge.cho")] == [ly_do]


@pytest.mark.parametrize("lenh", ["sh scripts/deploy.sh", "/r/scripts/deploy.sh", "sh ./src/../scripts/deploy.sh",
                                  "deploy --file=scripts/deploy.sh", "make -C scripts"])
def test_doi_lenh_trong_luc_doc_pr_thi_cho_file_lenh(tmp_path, monkeypatch, lenh):
    """Codex Q2 + C2 (D89 tại cửa merge): PR sửa `scripts/deploy.sh`; QC, kiểm lại đã đạt khi ba lệnh còn trống. Trong
    lúc trạm chờ `gh pr view`, Đại ca khai lệnh dùng đúng file đó (tương đối, tuyệt đối theo gốc dự án, sau `=`, cả
    thư mục) → không merge, chờ `file_lenh` — dấu QC cũ không đủ; dự án miễn đúng file đó ở `duong_dan_cam_cho_phep`
    cũng không miễn được tập bắt buộc này. Lệnh đổi sang file PR không sửa → merge."""
    t, gh, q = dung_tu_merge(tmp_path, monkeypatch, tep={"scripts/deploy.sh": "echo 2\n"},
                             cho_phep=("scripts/deploy.sh",))
    cot_3_co_pr(t, gh)
    gh.khi_xem = lambda so: doi(t, lenh_deploy=lenh)
    mot_vong_tick(t.bo)
    assert merge_goi(gh) == [] and [s.du_lieu["ly_do"] for s in tm(t, "tu_merge.cho")] == [["file_lenh"]]
    gh.khi_xem = lambda so: doi(t, lenh_deploy="sh kiem.sh")
    assert mot_vong_tick(t.bo)["tu_merge"] == 1 and merge_goi(gh) == [("merge_pr", REPO, 1, q)]


def test_doi_lenh_trong_luc_doc_cay_git_thi_cho(tmp_path, monkeypatch):
    from tram.giao_viec import tu_merge_rao

    t, gh, q = dung_tu_merge(tmp_path, monkeypatch, tep={"scripts/deploy.sh": "echo 2\n"})
    cot_3_co_pr(t, gh)
    doi(t, lenh_deploy="sh kiem.sh")
    doc = tu_merge_rao._cay

    def doi_khi_doc(*args):
        doi(t, lenh_deploy="sh scripts/deploy.sh")
        return doc(*args)
    monkeypatch.setattr(tu_merge_rao, "_cay", doi_khi_doc)
    mot_vong_tick(t.bo)
    assert merge_goi(gh) == []
    assert tm(t, "tu_merge.cho")[-1].du_lieu["ly_do"] == ["file_lenh_loi"]


def test_lenh_tuyet_doi_trong_worktree_deploy_van_cam_merge(tmp_path, monkeypatch):
    """Review vòng 2: cùng file ở gốc deploy cũng thuộc repo, kể cả lệnh đổi sau QC."""
    from tram.duong_dan import tram_home

    t, gh, q = dung_tu_merge(tmp_path, monkeypatch, tep={"scripts/deploy.sh": "echo 2\n"},
                             cho_phep=("scripts/deploy.sh",))
    cot_3_co_pr(t, gh)
    p = tram_home() / "kho-deploy" / "hr-codex" / "scripts" / "deploy.sh"
    gh.khi_xem = lambda so: doi(t, lenh_deploy=f'sh "{p}"')
    mot_vong_tick(t.bo)
    assert merge_goi(gh) == []
    assert tm(t, "tu_merge.cho")[-1].du_lieu["ly_do"] == ["file_lenh"]


def test_tam_dung_roi_tiep_tuc(tmp_path, monkeypatch):
    """Scenario "Tạm dừng rồi tiếp tục" (phần tự merge): công tắc vẫn như cũ sau Tiếp tục."""
    t, gh, q = dung_tu_merge(tmp_path, monkeypatch)
    cot_3_co_pr(t, gh)
    ghi_tam_dung(t.kho.db, "hr-codex", tam_dung=True, tac_nhan="dai-ca/dashboard")
    mot_vong_tick(t.bo)
    assert merge_goi(gh) == []
    ghi_tam_dung(t.kho.db, "hr-codex", tam_dung=False, tac_nhan="dai-ca/dashboard")
    assert mot_vong_tick(t.bo)["tu_merge"] == 1


def test_tram_tat_ngay_sau_lenh_merge_thi_doi_soat(tmp_path, monkeypatch):
    """Scenario "Trạm tắt ngay sau lệnh merge": vòng sau đọc PR — đã merge → đi tiếp xác minh, không gửi lại."""
    t, gh, q = dung_tu_merge(tmp_path, monkeypatch, gh_kw={"mat_phan_hoi_khi_merge": True})
    cot_3_co_pr(t, gh)
    assert mot_vong_tick(t.bo)["loi_gh"] == 1 and [s.loai for s in tm(t)] == ["tu_merge.bat_dau"]
    gh.mat_merge = False
    assert mot_vong_tick(t.bo)["tu_merge"] == 1 and [s.loai for s in tm(t)] == ["tu_merge.bat_dau", "tu_merge.xong"]
    assert mot_vong_tick(t.bo)["da_merge"] == 1 and len(merge_goi(gh)) == 1


def test_con_mo_thi_gui_lai_cung_commit_ba_lan_roi_loi(tmp_path, monkeypatch):
    """Mốc 2.4: lỗi `gh` → vòng sau đọc PR, còn mở + vẫn đủ điều kiện → gửi lại ĐÚNG commit; 3 lần → `tu_merge.loi`,
    ngừng thử, báo "trạm lỗi"; PR vẫn mở cho Đại ca merge tay."""
    t, gh, q = dung_tu_merge(tmp_path, monkeypatch, gh_kw={"loi_merge": True})
    cot_3_co_pr(t, gh)
    assert [mot_vong_tick(t.bo).get("loi_gh") for _ in range(3)] == [1, 1, 1]
    assert not tm(t, "tu_merge.loi")
    assert mot_vong_tick(t.bo)["tu_merge_loi"] == 1             # đọc lại OPEN trước khi kết luận lỗi
    assert merge_goi(gh) == [("merge_pr", REPO, 1, q)] * 3
    assert [s.du_lieu.get("lan") for s in tm(t, "tu_merge.bat_dau")] == [1, 2, 3]
    [loi] = tm(t, "tu_merge.loi")
    assert loi.du_lieu["ma_loi"] == "gh-loi-3-lan" and gh.prs[1].trang_thai == "OPEN"
    mot_vong_tick(t.bo)
    assert len(merge_goi(gh)) == 3 and len(tm(t, "tu_merge.loi")) == 1
    gh.dat(1, trang_thai="MERGED", merge_commit=lam_merge(t.k)(gh.prs[1]))          # Đại ca merge tay
    assert mot_vong_tick(t.bo)["da_merge"] == 1


def test_lan_ba_mat_phan_hoi_van_doi_soat_thanh_cong(tmp_path, monkeypatch):
    """Lần thứ ba cũng có thể đã merge dù CLI báo lỗi: không kết luận lỗi trước khi đọc lại PR."""
    t, gh, q = dung_tu_merge(tmp_path, monkeypatch, gh_kw={"loi_merge": True})
    cot_3_co_pr(t, gh)
    assert mot_vong_tick(t.bo)["loi_gh"] == 1
    assert mot_vong_tick(t.bo)["loi_gh"] == 1
    gh.loi_merge, gh.mat_merge = False, True
    assert mot_vong_tick(t.bo)["loi_gh"] == 1
    assert gh.prs[1].trang_thai == "MERGED" and not tm(t, "tu_merge.loi")
    assert mot_vong_tick(t.bo)["tu_merge"] == 1
    assert len(tm(t, "tu_merge.xong")) == 1 and len(merge_goi(gh)) == 3
    assert mot_vong_tick(t.bo)["da_merge"] == 1


def test_dau_pr_doi_hay_pr_dong(tmp_path, monkeypatch):
    """Scenario "Đầu PR đổi sau khi kiểm"; PR đã gửi lệnh mà bị đóng → `tu_merge.loi`."""
    t, gh, q = dung_tu_merge(tmp_path, monkeypatch)
    cot_3_co_pr(t, gh)
    gh.dat(1, head="d" * 40)
    mot_vong_tick(t.bo)
    assert merge_goi(gh) == [] and tm(t, "tu_merge.cho")[-1].du_lieu["ly_do"] == ["dau_pr_khac"]
    t2, gh2, _ = dung_tu_merge(tmp_path / "b", monkeypatch, gh_kw={"mat_phan_hoi_khi_merge": True})
    cot_3_co_pr(t2, gh2)
    gh2.lam_merge = None
    mot_vong_tick(t2.bo)
    gh2.dat(1, trang_thai="CLOSED")
    assert mot_vong_tick(t2.bo)["tu_merge_loi"] == 1
    assert tm(t2, "tu_merge.loi")[0].du_lieu["ma_loi"] == "pr-da-dong"


@pytest.mark.parametrize("canh, kw, nut, ly_do", [
    ("Diff chạm đường dẫn tiền", {"tep": {"erp/app/Modules/Fin/So.php": "x\n"}}, {}, ["hang_rao_tien"]),
    ("Tắt nút hàng rào thì merge", {"tep": {"erp/app/Modules/Fin/So.php": "x\n"}}, {"dk_hang_rao": False}, []),
    ("Việc chỉ nhắc từ khoá", {"description": "Sửa hoá đơn hiển thị sai"}, {}, []),
    ("Tắt nút hàng rào vẫn chặn migration",
     {"tep": {"db/migrations/001.sql": "alter\n"}, "hang_rao": {"schema": HangRao(duong_dan=("db/migrations/*",))}},
     {"dk_hang_rao": False}, ["schema_duong_dan"]),
    ("Việc nói tới xoá dữ liệu",
     {"description": "Xoá dữ liệu khách cũ", "hang_rao": {"schema": HangRao(tu_khoa=("xoá dữ liệu",))}},
     {"dk_hang_rao": False}, ["schema_tu_khoa"]),
    ("Đại ca đã tự gán cột", {"labels": ["cot:ai-lam", "cot-khoa"]}, {}, ["cot"]),
    ("Tắt nút cột", {"labels": ["cot:ai-lam", "cot-khoa"]}, {"dk_cot": False}, []),
    ("Repo chưa có CI, nút CI bật", {}, {"ci": "rong"}, ["ci_rong"]),
    ("Dự án tắt nút CI", {}, {"ci": "rong", "dk_ci": False}, []),
])
def test_dieu_kien_tren_du_lieu_that(tmp_path, monkeypatch, canh, kw, nut, ly_do):
    """Mốc 2.6: hàng rào chỉ theo đường dẫn diff (D91); `schema` theo đường dẫn + từ khoá, không theo nút (D76, D92,
    D112); cột theo `cot-khoa` (D90); CI rỗng = chưa xanh (D93)."""
    ci = nut.pop("ci", "xanh")
    t, gh, q = dung_tu_merge(tmp_path, monkeypatch, **kw)
    if nut:
        doi(t, **nut)
    cot_3_co_pr(t, gh, ci=ci)
    mot_vong_tick(t.bo)
    assert [s.du_lieu["ly_do"] for s in tm(t, "tu_merge.cho")] == ([ly_do] if ly_do else [])
    assert len(merge_goi(gh)) == (0 if ly_do else 1)


def test_khong_doc_duoc_diff_thi_luon_cho(tmp_path, monkeypatch):
    """Commit không có trong kho kiểm → không biết diff chạm gì → chờ Đại ca, không theo nút (như D76)."""
    t, gh, q = dung_tu_merge(tmp_path, monkeypatch, bat=False)
    da, b, v = t.bo.cac_du_an()[0], t.g.beads["hr-1"], SK(1, "bead.vao_cot_3", {"commit_ban_giao": "f" * 40}, "")
    assert doc_tep(t.k.kho, da, "f" * 40) is None and cham_rao(da, b, v, None) == (("diff_loi",), ())
    fetch(t.k.kho)
    assert cham_rao(da, b, replace(v, du_lieu={"commit_ban_giao": q}), doc_tep(t.k.kho, da, q)) == ((), ())
```

Tạo mới `tests/test_tu_merge_rao.py` (nguyên văn):

```python
"""TM-2, Codex Q2 + C2 (D89 tại cửa merge; hợp đồng D89 TM-1 vòng 2): `loai_trong_repo` — token NGUYÊN VĂN → đường
dẫn trong repo theo cây Git (commit của PR hoặc nhánh chính), không thoát gốc qua `..`/symlink; `cham_file_lenh` —
diff chạm tập file ba lệnh dùng → `file_lenh`; không đọc được cây → `file_lenh_loi`. Git cục bộ thật, không mạng."""
import os
from dataclasses import replace
from pathlib import Path

import pytest

from kho_kiem_gia import dung_kho
from tram.cau_hinh.du_an import DuAn
from tram.giao_viec.git_kiem import fetch
from tram.giao_viec.tu_merge_rao import cham_file_lenh, doc_tep, loai_trong_repo
from tram.tu_dong.cai_dat import MAC_DINH

DA = DuAn("hr-codex", Path("/r"), None, {})


def _pr(tmp_path):
    """PR tạo `scripts/deploy.sh`, symlink `ngoai` → `/etc`, xoá `kiem.sh` (còn ở nhánh chính)."""
    k = dung_kho(tmp_path)
    k.day("tram/hr-1", {}, tu=k.main)
    os.symlink("/etc", k.dev / "ngoai")
    c = k.day("tram/hr-1", {"scripts/deploy.sh": "echo 1\n", "kiem.sh": None})
    fetch(k.kho)
    return k, c


def test_loai_trong_repo_theo_cay_git(tmp_path):
    k, c = _pr(tmp_path)
    loai = loai_trong_repo(k.kho, (DA.duong_dan, k.kho), (c, "origin/main"))
    assert loai("scripts/deploy.sh") == ("scripts/deploy.sh", "file")           # chỉ có ở commit PR (tạo mới)
    assert loai("./kiem.sh") == ("kiem.sh", "file")                              # PR xoá, nhánh chính còn
    assert loai("scripts") == ("scripts", "dir") and loai("Scripts/Deploy.SH") == ("scripts/deploy.sh", "file")
    assert loai("/r/src/tom_tat.py") == ("src/tom_tat.py", "file")              # tuyệt đối theo gốc dự án
    assert loai(f"{k.kho}/src/../kiem.sh") == ("kiem.sh", "file")                 # tuyệt đối theo kho kiểm
    for token in ("ngoai/passwd", "ngoai/../kiem.sh"):
        with pytest.raises(OSError, match="symlink"):
            loai(token)
    for ngoai in ("../kiem.sh", "src/../../kiem.sh", "/etc/passwd", "/rr/kiem.sh", "/r", ".", "scripts/khong.sh"):
        assert loai(ngoai) is None, ngoai


def test_cham_file_lenh(tmp_path):
    k, c = _pr(tmp_path)
    tep = doc_tep(k.kho, DA, c)

    def cham(**lenh):
        return cham_file_lenh(replace(MAC_DINH, **lenh), k.kho, DA, c, tep)
    assert cham() == () and cham(lenh_deploy="sh src/tom_tat.py") == ()        # chưa khai; file lệnh dùng không đổi
    assert cham(lenh_lui="sh ./kiem.sh") == ("file_lenh",)                       # PR xoá file lệnh dùng
    assert cham(lenh_kiem_song="make -C scripts") == ("file_lenh",)              # thư mục lệnh dùng
    assert cham(lenh_deploy="sh /r/ngoai/x.sh") == ("file_lenh_loi",)                # PR thêm symlink lệnh đi qua
    assert cham_file_lenh(replace(MAC_DINH, lenh_deploy="sh x.sh"), k.kho, DA, c, None) == ()   # đã `diff_loi`
    assert cham_file_lenh(replace(MAC_DINH, lenh_deploy="sh x.sh"), k.kho, DA, "f" * 40, tep) == ("file_lenh_loi",)

@pytest.mark.parametrize("lenh", ["sh lien-ket/deploy.sh", "sh lien-ket/../scripts/deploy.sh"])
def test_lenh_qua_symlink_khong_mien_dich_cua_link(tmp_path, lenh):
    k = dung_kho(tmp_path)
    os.symlink("scripts", k.dev / "lien-ket")
    goc = k.day("main", {"scripts/deploy.sh": "echo 1\n"}, tu=k.main)
    c = k.day("tram/hr-1", {"scripts/deploy.sh": "echo 2\n"}, tu=goc)
    fetch(k.kho)
    tep = doc_tep(k.kho, DA, c)
    assert "lien-ket" not in tep and "scripts/deploy.sh" in tep
    cd = replace(MAC_DINH, lenh_deploy=lenh)
    assert cham_file_lenh(cd, k.kho, DA, c, tep) == ("file_lenh_loi",)

```

- [ ] **Step 2: Chạy, mong đợi ĐỎ**

```bash
tests/chan_host/chay.sh -q tests/test_tu_merge.py
```
Đỏ thật (khi viết plan): lỗi khi thu thập:

```
E   ModuleNotFoundError: No module named 'tram.giao_viec.tu_merge_rao'
ERROR tests/test_tu_merge.py
1 error in 0.19s
```
thoát 2, nhật ký chặn 0 dòng mới.

- [ ] **Step 3: Viết mã**

Tạo mới `tram/giao_viec/tu_merge_gui.py` (nguyên văn):

```python
"""Gửi lệnh tự merge và đối soát (spec `tu-merge` "Không merge lặp", "Kiểm lại công tắc ngay trước lúc merge";
design D-7). Mỗi lần tự merge mang mã `tm-` cố định theo (dự án, bead, commit). Thứ tự: đọc PR → đối soát lần trước
→ xét điều kiện (đọc lại khoá chung NGAY lúc này, sau mọi lệnh chậm) → ghi `tu_merge.bat_dau` → `gh pr merge` chặt →
đọc lại PR. Kết quả không rõ thì vòng sau đọc PR trước: đã merge → `tu_merge.xong`; còn mở và vẫn đủ điều kiện → gửi
lại đúng lệnh cùng commit; đóng, hay merge ở đầu khác → `tu_merge.loi`. Gửi tối đa 3 lần rồi `tu_merge.loi`."""
import hashlib
from collections.abc import Callable
from datetime import datetime

from tram.giao_viec.gh import GhCli, PrInfo
from tram.giao_viec.su_kien import SK, cua_so, da_co, moi_nhat
from tram.phieu.kho import KhoPhieu

TAC_NHAN = "tram/tu-merge"
SO_LAN = 3
LyDo = Callable[[PrInfo], list[str]]


def ma_tu_merge(du_an: str, bead_id: str, commit: str) -> str:
    return "tm-" + hashlib.sha256(f"{du_an}:{bead_id}:{commit}".encode()).hexdigest()[:20]


def ghi(kho: KhoPhieu, du_an: str, loai: str, du_lieu: dict, *, bead_id: str, luc: datetime,
        khoa: tuple[str, ...]) -> None:
    """Một giao dịch; đã có sự kiện cùng các trường `khoa` thì thôi (phát lại vòng tick không ghi hai lần)."""
    with kho.giao_dich():
        if not da_co(kho, du_an, loai, {k: du_lieu[k] for k in khoa}):
            kho.ghi_su_kien(du_an, loai, du_lieu, luc=luc, bead_id=bead_id, tac_nhan=TAC_NHAN)


def ghi_cho(kho: KhoPhieu, du_an: str, bead_id: str, ds: list[SK], ly_do: list[str], commit: str,
            luc: datetime) -> None:
    """Spec mốc 2.5: chỉ ghi khi khác lần trước (lần trước = `tu_merge.cho` hay lần gửi lệnh gần nhất trong cửa sổ)."""
    w = cua_so(ds)
    tr, gui = moi_nhat(w, "tu_merge.cho"), moi_nhat(w, "tu_merge.bat_dau")
    if tr is not None and (gui is None or tr.id > gui.id) and tr.du_lieu == {"ly_do": ly_do, "commit": commit}:
        return
    with kho.giao_dich():
        kho.ghi_su_kien(du_an, "tu_merge.cho", {"ly_do": ly_do, "commit": commit}, luc=luc, bead_id=bead_id,
                        tac_nhan=TAC_NHAN)


def _loi(kho, du_an, bead_id, ma, ma_loi, luc) -> str:
    ghi(kho, du_an, "tu_merge.loi", {"ma_thao_tac": ma, "ma_loi": ma_loi}, bead_id=bead_id, luc=luc,
        khoa=("ma_thao_tac",))
    return "tu_merge_loi"


def _xong(kho, du_an, bead_id, ma, loai, luc) -> str:
    ghi(kho, du_an, "tu_merge.xong", {"ma_thao_tac": ma, "loai": loai}, bead_id=bead_id, luc=luc,
        khoa=("ma_thao_tac",))
    return "tu_merge"


def gui_merge(gh: GhCli, repo: str, kho: KhoPhieu, du_an: str, bead_id: str, ds: list[SK], *, so_pr: int,
              commit: str, loai: str, ly_do: LyDo, luc: datetime) -> str | None:
    """`ly_do(pr)` đọc lại cài đặt, TẠM DỪNG, estop, `bat_ghi` mỗi lần gọi và trả mã lý do (rỗng = được merge).
    None = không làm gì để `kiem_merge` chạy tiếp (Đại ca merge tay, hoặc đang chờ điều kiện)."""
    ma = ma_tu_merge(du_an, bead_id, commit)
    if any(s.loai in ("tu_merge.xong", "tu_merge.loi") and s.du_lieu.get("ma_thao_tac") == ma for s in ds):
        return None
    da_gui = sum(1 for s in ds if s.loai == "tu_merge.bat_dau" and s.du_lieu.get("ma_thao_tac") == ma)
    pr = gh.xem_pr(repo, so_pr)
    if pr.trang_thai == "MERGED":
        if not da_gui:
            return None                                     # Đại ca merge tay — xác minh như luồng cũ
        return _xong(kho, du_an, bead_id, ma, loai, luc) if pr.head == commit else _loi(
            kho, du_an, bead_id, ma, "merge-khac-commit", luc)
    if pr.trang_thai != "OPEN":
        return _loi(kho, du_an, bead_id, ma, "pr-da-dong", luc) if da_gui else None
    if ly := ly_do(pr):
        ghi_cho(kho, du_an, bead_id, ds, ly, commit, luc)
        return None
    if da_gui >= SO_LAN:
        return _loi(kho, du_an, bead_id, ma, "gh-loi-3-lan", luc)
    ghi(kho, du_an, "tu_merge.bat_dau", {"ma_thao_tac": ma, "commit": commit, "pr": pr.so, "loai": loai,
                                          "lan": da_gui + 1}, bead_id=bead_id, luc=luc, khoa=("ma_thao_tac", "lan"))
    gh.merge_pr(repo, pr.so, commit)                         # LoiGh: luôn đối soát vòng sau, kể cả lần thứ ba
    if gh.xem_pr(repo, pr.so).trang_thai == "MERGED":
        return _xong(kho, du_an, bead_id, ma, loai, luc)
    return "tu_merge_gui"                                   # chưa thấy MERGED: vòng sau đối soát
```

Tạo mới `tram/giao_viec/tu_merge_rao.py` (nguyên văn):

```python
"""Đọc diff của một lần tự merge (spec `tu-merge`; D76, D89, D91, D92, D112) — phần cần Git của `tu_merge.py`.

- `cham_rao`: hàng rào chỉ theo đường dẫn diff từ gốc nhánh (D91); `schema` thêm từ khoá nội dung bead (D92, D112).
- `cham_file_lenh` (D89 tại cửa merge — Codex Q2): tập file cấm tính từ ba lệnh của CÀI ĐẶT HIỆN HÀNH (người gọi đọc
  lại ngay trước `gh pr merge`) so với diff. Tập này BẮT BUỘC: không theo nút, không bị `duong_dan_cam_cho_phep` miễn
  (Codex C2); dấu QC/kiểm lại cũ không thay được lần so này.
- `loai_trong_repo`: callback cho `tram.tu_dong.file_cam.duong_dan_tu_lenh` (hợp đồng D89 TM-1 vòng 2). "Có trong
  repo" = có trong cây Git ở MỘT trong `refs` (commit của PR, nhánh chính) — tạo mới hay xoá script lệnh sẽ chạy
  đều bị bắt. Token tuyệt đối → tương đối theo gốc đáng tin (`da.duong_dan`, kho kiểm); `..` thoát gốc → ngoài repo.
  Một đoạn là symlink → đóng bảo thủ (`file_lenh_loi`), không theo ra ngoài cây và không chỉ cấm tên link:
  cấm riêng tên link sẽ bỏ lọt PR sửa đích mà giữ nguyên link. Kiểm từng đoạn TRƯỚC khi rút gọn `..`."""
import fnmatch
import os
import subprocess
from collections.abc import Callable
from dataclasses import replace
from pathlib import Path, PurePosixPath

from tram.beads.mo_hinh import Bead
from tram.cau_hinh.du_an import DuAn, HangRao
from tram.cham_cot.luat_cung import kiem
from tram.duong_dan import tram_home
from tram.giao_viec.su_kien import SK
from tram.kiem.diff import goc_nhanh, tep_doi
from tram.kiem.duong_dan_cam import khop_mau
from tram.tu_dong.cai_dat import CaiDatTuDong
from tram.tu_dong.file_cam import duong_dan_tu_lenh

NHAN_CO_DO = "co-do"
GIT = ("git", "--literal-pathspecs", "-c", "core.hooksPath=/dev/null")
HAN_GIT = 60                                                # giây — lời gọi Git không bao giờ chờ vô hạn
LoaiTrongRepo = Callable[[str], tuple[str, str] | None]


def doc_tep(kg: Path, da: DuAn, c: str) -> list[str] | None:
    """File đổi từ gốc nhánh tới `c`; None = không đọc được (người gọi luôn chờ: `diff_loi`)."""
    try:
        return tep_doi(kg, goc_nhanh(kg, f"origin/{da.nhanh_chinh}", c), c)
    except (subprocess.CalledProcessError, OSError):
        return None


def cham_rao(da: DuAn, b: Bead, v: SK, tep: list[str] | None) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """(cấu trúc DB, hàng rào có nút). Bead mang cờ đỏ mà không khớp loại nào (D120) vẫn là chạm."""
    if tep is None:
        return ("diff_loi",), ()                            # không biết diff chạm gì → luôn chờ, như cấu trúc DB
    loai = [l for l, r in da.hang_rao.items() if any(fnmatch.fnmatch(p, g) for g in r.duong_dan for p in tep)]
    sc = da.hang_rao.get("schema")
    tu_khoa = sc is not None and bool(kiem(b, replace(da, hang_rao={"schema": HangRao(tu_khoa=sc.tu_khoa)}), {}).cham)
    schema = (("schema_duong_dan",) if "schema" in loai else ()) + (("schema_tu_khoa",) if tu_khoa else ())
    rao = tuple(f"hang_rao_{l}" for l in loai if l != "schema")
    if not rao and "schema" not in loai and (NHAN_CO_DO in b.labels or v.du_lieu.get("co_do") is True):
        rao = ("hang_rao_co_do",)
    return schema, rao


def _tuong_doi(tok: str, goc: tuple[str, ...]) -> str | None:
    if os.path.isabs(tok):
        g = next((g for g in goc if tok.lower().startswith(g.lower() + "/")), None)
        return None if g is None else tok[len(g) + 1:]
    return tok if tok not in ("", ".") else None


def _cay(kg: Path, ref: str) -> dict[str, tuple[str, str, str]]:
    """Cả cây ở `ref`, không đi vào symlink; khoá chữ thường (ổ macOS không phân biệt hoa) → (tên, mode, kiểu)."""
    tho = subprocess.run([*GIT, "-C", str(kg), "ls-tree", "-r", "-t", "-z", "--full-tree", ref], capture_output=True,
                         timeout=HAN_GIT, check=True).stdout
    ra = {}
    for x in (x for x in tho.split(b"\0") if x):
        dau, ten = x.split(b"\t", 1)
        ra[os.fsdecode(ten).lower()] = (os.fsdecode(ten), *dau.decode().split(" ")[:2])
    return ra


def loai_trong_repo(kg: Path, goc: tuple[Path, ...], refs: tuple[str, ...]) -> LoaiTrongRepo:
    goc_s = tuple(dict.fromkeys(os.path.normpath(s) for g in goc for s in (g, g.resolve())))
    cay: dict[str, dict] = {}

    def loai(tok: str) -> tuple[str, str] | None:
        if (p := _tuong_doi(tok, goc_s)) is None:
            return None
        for ref in refs:
            muc = cay[ref] if ref in cay else cay.setdefault(ref, _cay(kg, ref))
            doan = []
            for d in PurePosixPath(p).parts:
                if d == "..":
                    if not doan:
                        return None
                    doan.pop()
                    continue
                doan.append(d.lower())
                m = muc.get("/".join(doan))
                if m is None:
                    break
                if m[1] == "120000":
                    raise OSError("đường lệnh qua symlink: chưa chứng minh được đích an toàn")
            else:
                if m := muc.get("/".join(doan)):
                    return m[0], "dir" if m[2] == "tree" else "file"
        return None
    return loai


def cham_file_lenh(cd: CaiDatTuDong, kg: Path, da: DuAn, c: str, tep: list[str] | None) -> tuple[str, ...]:
    """`("file_lenh",)` khi diff chạm file ba lệnh dùng; `("file_lenh_loi",)` khi không đọc được cây Git."""
    if tep is None:
        return ()                                           # đã có `diff_loi` (luôn chờ)
    try:
        gocs = (da.duong_dan, kg, tram_home() / "kho-deploy" / da.ten)
        cam = duong_dan_tu_lenh(cd, loai_trong_repo(kg, gocs, (c, f"origin/{da.nhanh_chinh}")))
    except (subprocess.SubprocessError, OSError):
        return ("file_lenh_loi",)
    return ("file_lenh",) if any(khop_mau(p, m) for p in tep for m in cam) else ()
```

Tạo mới `tram/giao_viec/tu_merge_tuoi.py` (nguyên văn; nguồn đọc cuối V2-C1):

```python
"""V2-C1: đọc nguồn Beads/sự kiện sau Git/GitHub; lỗi đọc luôn chờ, không chép nội dung lỗi."""
import sqlite3

from tram.beads.bd import LoiBd
from tram.giao_viec.doc_lai import dau_bead
from tram.giao_viec.su_kien import cua_so, moi_nhat, su_kien_bead


def doc_hien_hanh(bd, kho, da, bead_id):
    """Không dùng bộ đệm. Đọc Beads trước SQLite vì bd list có thể chậm; không giữ giao dịch khi đọc bd."""
    try:
        b = next((b for b in bd.tat_ca() if b.id == bead_id), None)
        return (b, su_kien_bead(kho, da.ten, bead_id)) if b is not None else None
    except (LoiBd, OSError, ValueError, sqlite3.Error):
        return None


def spec_con_nguyen(cu, moi, ds, dy, mo):
    """D95: đúng feature theo-plan, bản duyệt/PR hiện hành; không dùng digest kế hoạch làm digest bead."""
    return (moi.status != 'closed' and moi.issue_type == 'feature' and 'theo-plan' in moi.labels
            and (moi.status, moi.assignee, dau_bead(moi)) == (cu.status, cu.assignee, dau_bead(cu))
            and moi_nhat(cua_so(ds), 'spec.duyet') == dy and moi_nhat(cua_so(ds), 'pr.mo') == mo)
```

Tạo mới `tram/giao_viec/tu_merge.py` (nguyên văn):

```python
"""Bước tự merge của vòng tick (spec `tu-merge`; design D-1, D-2, D-11): chen giữa mở PR và xác minh merge trong
`buoc_github`. Công tắc tự merge của dự án tắt → không đọc GitHub, không ghi gì (hành vi như trước TM-2). Bật → đọc
PR + CI, tính lại mọi điều kiện từ sự kiện, Beads, kho kiểm (không tin nhãn hay notes), đọc lại cài đặt / TẠM DỪNG
/ estop / `bat_ghi` và tập file cấm từ ba lệnh hiện hành (D89, `tu_merge_rao`) ngay trước lệnh (`tu_merge_gui`).
Sau khi merge, `kiem_merge` (bead) hay điều kiện 8 của spec 4 §5.1 (`spec_merge`, PR spec) xác minh như cũ."""
from datetime import datetime
from pathlib import Path

import yaml

from tram.beads.mo_hinh import Bead
from tram.cau_hinh.bat_ghi import bat_ghi
from tram.cau_hinh.du_an import DuAn
from tram.chu import estop
from tram.giao_viec.gh import GhCli, PrInfo
from tram.giao_viec.pr_bang_chung import bang_chung_hien_hanh
from tram.giao_viec.su_kien import SK, cua_so, moi_nhat
from tram.giao_viec.tu_merge_gui import gui_merge
from tram.giao_viec.tu_merge_tuoi import doc_hien_hanh, spec_con_nguyen
from tram.giao_viec.tu_merge_rao import cham_file_lenh, cham_rao, doc_tep
from tram.giao_viec.tu_merge_xet import DuKien, kiem_lai_qc, ly_do_chua_merge
from tram.phieu.kho import KhoPhieu
from tram.tu_dong.luu import TrangThaiTuDong, doc_trang_thai

NHAN_KHOA_COT = "cot-khoa"


def _bat_ghi(ten: str) -> bool:
    try:
        return bat_ghi(ten)
    except (OSError, ValueError, AttributeError, yaml.YAMLError):
        return False                                        # INV-005: đọc lỗi = chỉ quét thử


def _khoa(kho: KhoPhieu, da: DuAn) -> tuple[TrangThaiTuDong, bool, bool]:
    return doc_trang_thai(kho.db, da.ten), _bat_ghi(da.ten), estop.dang_bat()


def _dung_pr(pr: PrInfo, mo: dict, nhanh: str, da: DuAn) -> bool:
    return (pr.so, pr.url, pr.nhanh, pr.base, pr.ngoai_repo) == (mo["pr"], mo["url"], nhanh, da.nhanh_chinh, False)


def xet_tu_merge(gh: GhCli, repo: str, kho: KhoPhieu, kg: Path, da: DuAn, bd, b: Bead, ds: list[SK],
                 luc: datetime) -> str | None:
    """Bead ở cột 3 đã có `pr.mo` cho `commit_ban_giao` hiện hành."""
    if not doc_trang_thai(kho.db, da.ten).cai_dat.tu_merge or (v := bang_chung_hien_hanh(b, ds)) is None:
        return None
    c = v.du_lieu["commit_ban_giao"]
    if (mo := moi_nhat(cua_so(ds), "pr.mo", lambda s: s.du_lieu["commit"] == c)) is None:
        return None
    tep = doc_tep(kg, da, c)

    def ly_do(pr: PrInfo) -> list[str]:
        tt, _, _ = _khoa(kho, da)                           # đọc ba lệnh SAU `gh pr view` (D89)
        cam = cham_file_lenh(tt.cai_dat, kg, da, c, tep)
        if (hien := doc_hien_hanh(bd, kho, da, b.id)) is None:
            return ["du_lieu_loi"]
        bead, sk = hien
        seal = bang_chung_hien_hanh(bead, sk)
        if seal is None or seal != v:
            return ["kiem_lai"]
        if moi_nhat(cua_so(sk), "pr.mo") != mo:
            return ["pr_khac"]
        qc_dat, kl_dat = kiem_lai_qc(sk, seal)
        schema, rao = cham_rao(da, bead, seal, tep)
        moi, bg, es = _khoa(kho, da)                        # sau cả Beads; từ đây không gọi lệnh đọc chậm
        cam = cam if moi.cai_dat == tt.cai_dat else ("file_lenh_loi",)
        dk = DuKien(qc_dat, kl_dat, _dung_pr(pr, mo.du_lieu, f"tram/{b.id}", da), pr.head == c, schema,
                    pr.ci or "do", NHAN_KHOA_COT not in bead.labels, rao, cam)
        return ly_do_chua_merge(moi, dk, bat_ghi=bg, estop_bat=es)
    return gui_merge(gh, repo, kho, da.ten, b.id, ds, so_pr=mo.du_lieu["pr"], commit=c, loai="code", ly_do=ly_do,
                     luc=luc)
```

Sửa `tram/giao_viec/tick_github.py` (bản vá, áp bằng `git apply`):

```diff
--- a/tram/giao_viec/tick_github.py
+++ b/tram/giao_viec/tick_github.py
@@ -1,5 +1,6 @@
 """Vòng tick — bước GitHub của lát 4c (spec 4 §6.4 mục 4, §6.5, §7.3), chạy SAU khi đẩy pipeline: bead đang ở cột
-3 → mở PR / điền `pr` / xác minh merge rồi đóng; feature `theo-plan` → mở PR cho commit spec đã duyệt.
+3 → mở PR / điền `pr` / tự merge khi dự án bật (TM-2, design D-1) / xác minh merge rồi đóng; feature `theo-plan` →
+mở PR cho commit spec đã duyệt.
 Không chạy khi estop (ghi GitHub + beads), khi `p4c.gh` chưa nối, hoặc remote kho kiểm không phải github.com.
 `gh` lỗi ở một bead → đếm `loi_gh`, bead khác chạy tiếp; vòng sau làm lại (mọi bước idempotent)."""
 from collections import Counter
@@ -11,6 +12,7 @@
 from tram.giao_viec.pr import NHAN_REVIEW, NHAN_THEO_PLAN, mo_pr_bead, mo_pr_spec
 from tram.giao_viec.pr_merge import kiem_merge
 from tram.giao_viec.su_kien import su_kien_bead
+from tram.giao_viec.tu_merge import xet_tu_merge
 from tram.phieu.kho import KhoPhieu
 
 
@@ -26,6 +28,7 @@
         try:
             if NHAN_REVIEW in b.labels:
                 k = (mo_pr_bead(gh, repo, kho, kg, da, bd, b, ds, luc)
+                     or xet_tu_merge(gh, repo, kho, kg, da, bd, b, ds, luc)
                      or kiem_merge(gh, repo, kho, kg, da, bd, b, ds, luc))
             else:
                 k = mo_pr_spec(gh, repo, kho, kg, da, b, ds, luc)
```

- [ ] **Step 4: Chạy, mong đợi XANH**

```bash
tests/chan_host/chay.sh -q tests/test_tu_merge.py tests/test_tick_4c.py tests/test_pr.py tests/test_tick.py tests/test_tick_hai_pha.py tests/test_vong_import.py tests/test_do_dai_ma.py
```
Lệnh rộng trên trong sandbox: `3 failed, 65 passed` trước hai bổ sung symlink/cửa chốt cuối; ba lỗi thuộc kiểm lại thật của bộ tick cũ. Bộ tập trung bản cuối ở mục Kiểm chứng plan xanh, gồm cả `test_tu_merge_rao.py`; không dùng số lịch sử làm bằng chứng hiện hành.

Rồi cả bộ → mong đợi `3500 passed` (số tính), nhật ký chặn 0 dòng mới.

- [ ] **Step 5: Commit**

```bash
git add tram/giao_viec/tu_merge_tuoi.py tram/giao_viec/tu_merge_gui.py tram/giao_viec/tu_merge.py tram/giao_viec/tu_merge_rao.py tram/giao_viec/tick_github.py tests/gh_gia.py tests/test_tu_merge.py tests/test_tu_merge_rao.py
git commit -m "feat(giao-viec): tự merge PR của bead ở cột 3 khi đủ điều kiện, đối soát khi không rõ (TM-2 Task 3)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

### Task 4: Tự gộp PR spec đã được Đại ca duyệt (D95, design D-11) ⛔ kill list mục 5, 7

**Scenario:** "Duyệt spec xong thì PR spec tự vào nhánh chính", "Nhánh spec đổi sau khi duyệt", "Công tắc tắt"; "Feature chưa duyệt spec" (không có `spec.duyet` → không làm gì); điều kiện 8 của spec 4 §5.1 thấy commit đã vào nhánh chính; D89 tại cửa merge cho PR spec (`test_pr_spec_sua_file_lenh_thi_cho`).

**Interfaces:** `tu_merge.tu_merge_spec(gh, repo, kho, kg, da, bd, b, ds, luc) -> str | None`; `buoc_github` nhánh feature `theo-plan`: `mo_pr_spec(...) or tu_merge_spec(...)`.

- [ ] **Step 1: Viết test**

Tạo mới `tests/test_tu_merge_spec.py` (nguyên văn):

```python
"""TM-2 mốc 2.7 (spec `tu-merge` "Tự gộp PR spec đã được Đại ca duyệt", D95, design D-11): bước GitHub của feature
`theo-plan` — mở PR spec rồi tự gộp khi dự án bật; sau đó điều kiện 8 của spec 4 §5.1 thấy commit đã vào nhánh chính.
GitHub giả + Git cục bộ."""
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

from bd_gia import BdGia
from bead_gia import bead
from gh_gia import REPO, GhGia
from git_gia import git
from kho_kiem_gia import dung_kho
from kho_phieu_gia import LUC, kho_tam
from su_kien_gia import cong_bo, ds, sk
from test_tu_merge import lam_merge
from tram.cau_hinh.du_an import DuAn
from tram.giao_viec.git_kiem import fetch
from tram.giao_viec.phu_thuoc_4c import PhuThuoc4c
from tram.giao_viec.spec_merge import feature_da_merge
from tram.giao_viec.tick_github import buoc_github
from tram.giao_viec.tu_merge import tu_merge_spec
from tram.tu_dong.luu import doi_cai_dat

DA = DuAn("hr-codex", Path("/r"), None, {})
F = bead("hr-f", issue_type="feature", title="Hoa hồng tạm tính", labels=["theo-plan"])


def dung_spec(tmp_path, monkeypatch, *, bat=True):
    (goc := tmp_path / "repo-tram" / "du-an").mkdir(parents=True)
    (goc / "hr-codex.yaml").write_text("ten: hr-codex\nbat_ghi: true\n")
    monkeypatch.setenv("TRAM_REPO", str(tmp_path / "repo-tram"))
    k, kho = dung_kho(tmp_path), kho_tam(tmp_path)
    s = k.day("tram/spec-hr-f", {"docs/specs/x.md": "spec\n"}, tu=k.main)
    fetch(k.kho)
    cong_bo(kho, 1, s, bead_id="hr-f")
    sk(kho, "spec.duyet", {"feature": "hr-f", "commit": s, "digest_bead": "sha256:b", "bead_moi": [],
                           "ma_thao_tac": "dy-1"}, bead_id="hr-f")
    gh = GhGia(lambda nhanh: git(k.origin, "rev-parse", nhanh), lam_merge=lam_merge(k))
    bo = SimpleNamespace(p4c=PhuThuoc4c(gh=gh, github_repo=lambda kg: REPO))
    if bat:
        doi_cai_dat(kho.db, "hr-codex", lambda c: replace(c, tu_merge=True), tac_nhan="dai-ca/dashboard")
    bd = BdGia([F])
    chay = lambda: buoc_github(bo, kho, DA, bd, [F], k.kho, LUC)        # noqa: E731
    chay.bd = bd
    return k, kho, gh, s, chay


def tm(kho, loai):
    return [e for e in ds(kho, "hr-f") if e.loai == loai]


def test_duyet_spec_xong_thi_pr_spec_tu_vao_nhanh_chinh(tmp_path, monkeypatch):
    k, kho, gh, s, chay = dung_spec(tmp_path, monkeypatch)
    assert chay() == {"pr_mo": 1}
    assert chay() == {"tu_merge": 1} and gh.prs[1].trang_thai == "MERGED"
    assert [g for g in gh.goi if g[0] == "merge_pr"] == [("merge_pr", REPO, 1, s)]
    assert [e.du_lieu["loai"] for e in tm(kho, "tu_merge.xong")] == ["spec"]
    fetch(k.kho)
    assert feature_da_merge(kho, DA, [F], k.kho) == {"hr-f"}                 # điều kiện 8: việc con được giao
    assert chay() == {} and len([g for g in gh.goi if g[0] == "merge_pr"]) == 1


def test_nhanh_spec_doi_sau_khi_duyet_thi_cho(tmp_path, monkeypatch):
    k, kho, gh, s, chay = dung_spec(tmp_path, monkeypatch)
    chay()
    gh.dat(1, head="e" * 40)
    assert chay() == {} and gh.prs[1].trang_thai == "OPEN"
    assert [e.du_lieu["ly_do"] for e in tm(kho, "tu_merge.cho")] == [["dau_pr_khac"]]


def test_cong_tac_tat_thi_pr_spec_cho_dai_ca(tmp_path, monkeypatch):
    k, kho, gh, s, chay = dung_spec(tmp_path, monkeypatch, bat=False)
    assert chay() == {"pr_mo": 1} and chay() == {}
    assert gh.prs[1].trang_thai == "OPEN" and not [e for e in ds(kho, "hr-f") if e.loai.startswith("tu_merge.")]


def test_dai_ca_gop_tay_truoc_thi_khong_doc_lai(tmp_path, monkeypatch):
    k, kho, gh, s, chay = dung_spec(tmp_path, monkeypatch, bat=False)
    chay()
    gh.dat(1, trang_thai="MERGED", merge_commit=lam_merge(k)(gh.prs[1]))
    fetch(k.kho)
    doi_cai_dat(kho.db, "hr-codex", lambda c: replace(c, tu_merge=True), tac_nhan="dai-ca/dashboard")
    gh.goi.clear()
    assert chay() == {} and gh.goi == [] and not tm(kho, "tu_merge.xong")


def test_feature_chua_duyet_spec_khong_lam_gi(tmp_path, monkeypatch):
    """Scenario "Feature chưa duyệt spec": không có `spec.duyet` → không đọc GitHub, không merge gì."""
    k, kho, gh, s, chay = dung_spec(tmp_path, monkeypatch)
    cho = bead("hr-g", issue_type="feature", labels=["cho-duyet-spec", "theo-plan"])
    assert tu_merge_spec(gh, REPO, kho, k.kho, DA, chay.bd, cho, [], LUC) is None and gh.goi == []


def test_pr_spec_sua_file_lenh_thi_cho(tmp_path, monkeypatch):
    """Codex Q2 (D89 tại cửa merge, cả PR spec): lệnh kiểm còn sống dùng file mà nhánh spec tạo → chờ `file_lenh`,
    không merge dù Đại ca đã duyệt spec; tập này không theo nút."""
    k, kho, gh, s, chay = dung_spec(tmp_path, monkeypatch)
    chay()
    doi_cai_dat(kho.db, "hr-codex", lambda c: replace(c, lenh_kiem_song="sh docs/specs/x.md"),
                tac_nhan="dai-ca/dashboard")
    assert chay() == {} and gh.prs[1].trang_thai == "OPEN"
    assert [e.du_lieu["ly_do"] for e in tm(kho, "tu_merge.cho")] == [["file_lenh"]]
```

Tạo mới `tests/test_tu_merge_tuoi.py` (nguyên văn; V2-C1, dùng fixture Task 3 và Task 4):

```python
"""V2-C1: thay dữ kiện khi đang đọc PR/cây Git, đi qua caller thật."""
from dataclasses import replace

import pytest

from su_kien_gia import ds, sk
from test_tu_merge import cot_3_co_pr, dung_tu_merge, merge_goi, tm
from test_tu_merge_spec import F, dung_spec
from tram.beads.bd import LoiBd
from tram.cau_hinh.du_an import HangRao
from tram.giao_viec.tick import mot_vong_tick


def doi_code(t, cach):
    b = t.g.beads['hr-1']
    if cach == 'tieu_chi':
        t.g.beads[b.id] = replace(b, acceptance_criteria='- Tiêu chí mới')
    elif cach == 'khoa_cot':
        t.g.beads[b.id] = replace(b, labels=(*b.labels, 'cot-khoa'))
    elif cach == 'seal':
        sk(t.kho, 'cot.tra_ve', {})
    elif cach == 'qc':
        q = next(s for s in reversed(ds(t.kho)) if s.loai == 'qc.ket_qua')
        sk(t.kho, q.loai, {**q.du_lieu, 'ket_luan': 'khong_dat'})
    elif cach == 'kiem_lai':
        k = next(s for s in reversed(ds(t.kho)) if s.loai == 'kiem.lai')
        sk(t.kho, k.loai, {**k.du_lieu, 'dat': False})
    elif cach == 'schema':
        t.g.beads[b.id] = replace(b, description='Xoá dữ liệu bằng drop table')
    elif cach == 'pr':
        p = next(s for s in reversed(ds(t.kho)) if s.loai == 'pr.mo')
        sk(t.kho, p.loai, {**p.du_lieu, 'pr': 2})
    elif cach == 'dong':
        t.g.beads[b.id] = replace(b, status='closed')
    elif cach == 'mat_bead':
        t.g.beads.pop(b.id)
    elif cach == 'loi_doc':
        def loi():
            raise LoiBd('nội dung không được ghi vào sự kiện')
        t.g.tat_ca = loi


@pytest.mark.parametrize('luc_doi', ['pr', 'cay'])
@pytest.mark.parametrize('cach', ['tieu_chi', 'khoa_cot', 'seal', 'qc', 'kiem_lai', 'schema', 'pr', 'dong', 'mat_bead', 'loi_doc'])
def test_code_doc_tuoi_sau_lenh_cham(tmp_path, monkeypatch, cach, luc_doi):
    from tram.giao_viec import tu_merge_rao
    from test_tu_merge import doi

    t, gh, _ = dung_tu_merge(tmp_path, monkeypatch,
                              hang_rao={'schema': HangRao(tu_khoa=('drop table',))})
    cot_3_co_pr(t, gh)
    doi(t, lenh_deploy='sh kiem.sh')
    da_doi = []

    def doi_mot_lan():
        if not da_doi:
            da_doi.append(True)
            doi_code(t, cach)
    if luc_doi == 'pr':
        gh.khi_xem = lambda so: doi_mot_lan()
    else:
        doc = tu_merge_rao._cay

        def doc_va_doi(*args):
            ra = doc(*args)
            doi_mot_lan()
            return ra
        monkeypatch.setattr(tu_merge_rao, '_cay', doc_va_doi)
    mot_vong_tick(t.bo)
    assert da_doi and merge_goi(gh) == []
    assert tm(t, 'tu_merge.bat_dau') == []
    assert tm(t, 'tu_merge.cho')
    assert 'nội dung không được' not in str(tm(t))


@pytest.mark.parametrize('luc_doi', ['pr', 'cay'])
@pytest.mark.parametrize('cach', ['tieu_chi', 'khoa_cot', 'duyet', 'pr', 'dong', 'loi_doc'])
def test_spec_doc_tuoi_sau_lenh_cham(tmp_path, monkeypatch, cach, luc_doi):
    from tram.giao_viec import tu_merge_rao
    from tram.tu_dong.luu import doi_cai_dat
    k, kho, gh, sha, chay = dung_spec(tmp_path, monkeypatch)
    chay()

    doi_cai_dat(kho.db, 'hr-codex', lambda c: replace(c, lenh_deploy='sh kiem.sh'), tac_nhan='dai-ca/dashboard')
    da_doi = []

    def doi(so):
        if da_doi:
            return
        da_doi.append(True)
        if cach == 'tieu_chi':
            chay.bd.beads[F.id] = replace(F, acceptance_criteria='- Mới')
        elif cach == 'khoa_cot':
            chay.bd.beads[F.id] = replace(F, labels=(*F.labels, 'cot-khoa'))
        elif cach == 'dong':
            chay.bd.beads[F.id] = replace(F, status='closed')
        elif cach == 'duyet':
            sk(kho, 'spec.duyet', {'commit': 'e' * 40}, bead_id=F.id)
        elif cach == 'pr':
            p = next(s for s in reversed(ds(kho, F.id)) if s.loai == 'pr.mo')
            sk(kho, p.loai, {**p.du_lieu, 'pr': 2}, bead_id=F.id)
        else:
            def loi():
                raise LoiBd('đọc thất bại')
            chay.bd.tat_ca = loi
    if luc_doi == 'pr':
        gh.khi_xem = doi
    else:
        doc = tu_merge_rao._cay

        def doc_va_doi(*args):
            ra = doc(*args)
            doi(1)
            return ra
        monkeypatch.setattr(tu_merge_rao, '_cay', doc_va_doi)
    chay()
    assert da_doi and merge_goi(gh) == []
    assert not [s for s in ds(kho, F.id) if s.loai == 'tu_merge.bat_dau']
    assert [s for s in ds(kho, F.id) if s.loai == 'tu_merge.cho']
```

- [ ] **Step 2: Chạy, mong đợi ĐỎ**

```bash
tests/chan_host/chay.sh -q tests/test_tu_merge_spec.py tests/test_tu_merge_tuoi.py
```
Đỏ thật (khi viết plan): lỗi khi thu thập:

```
E   ImportError: cannot import name 'tu_merge_spec' from 'tram.giao_viec.tu_merge' (…/tram/giao_viec/tu_merge.py)
ERROR tests/test_tu_merge_spec.py
1 error in 0.21s
```
thoát 2, nhật ký chặn 0 dòng mới.

- [ ] **Step 3: Viết mã**

Sửa `tram/giao_viec/tu_merge.py` (bản vá, áp bằng `git apply`):

```diff
--- a/tram/giao_viec/tu_merge.py
+++ b/tram/giao_viec/tu_merge.py
@@ -13,12 +13,13 @@
 from tram.cau_hinh.du_an import DuAn
 from tram.chu import estop
 from tram.giao_viec.gh import GhCli, PrInfo
+from tram.giao_viec.git_kiem import la_to_tien
 from tram.giao_viec.pr_bang_chung import bang_chung_hien_hanh
 from tram.giao_viec.su_kien import SK, cua_so, moi_nhat
 from tram.giao_viec.tu_merge_gui import gui_merge
 from tram.giao_viec.tu_merge_tuoi import doc_hien_hanh, spec_con_nguyen
 from tram.giao_viec.tu_merge_rao import cham_file_lenh, cham_rao, doc_tep
-from tram.giao_viec.tu_merge_xet import DuKien, kiem_lai_qc, ly_do_chua_merge
+from tram.giao_viec.tu_merge_xet import DuKien, kiem_lai_qc, ly_do_chua_merge, ly_do_chua_merge_spec
 from tram.phieu.kho import KhoPhieu
 from tram.tu_dong.luu import TrangThaiTuDong, doc_trang_thai
 
@@ -70,3 +71,32 @@
         return ly_do_chua_merge(moi, dk, bat_ghi=bg, estop_bat=es)
     return gui_merge(gh, repo, kho, da.ten, b.id, ds, so_pr=mo.du_lieu["pr"], commit=c, loai="code", ly_do=ly_do,
                      luc=luc)
+
+
+def tu_merge_spec(gh: GhCli, repo: str, kho: KhoPhieu, kg: Path, da: DuAn, bd, b: Bead, ds: list[SK],
+                  luc: datetime) -> str | None:
+    """Feature `theo-plan` đã được Đại ca duyệt spec, trạm đã mở PR `tram/spec-<feature>` (D95, design D-11)."""
+    dy = moi_nhat(ds, "spec.duyet")
+    if dy is None or b.status == "closed" or not doc_trang_thai(kho.db, da.ten).cai_dat.tu_merge:
+        return None
+    c = dy.du_lieu["commit"]
+    mo = moi_nhat(ds, "pr.mo", lambda s: s.du_lieu["commit"] == c and s.du_lieu.get("loai") == "spec")
+    gui = moi_nhat(ds, "tu_merge.bat_dau", lambda s: s.du_lieu.get("commit") == c)
+    if mo is None or (gui is None and la_to_tien(kg, c, f"origin/{da.nhanh_chinh}")):
+        return None                                     # đã vào nhánh chính mà trạm chưa gửi lệnh: Đại ca gộp tay
+    tep = doc_tep(kg, da, c)
+
+    def ly_do(pr: PrInfo) -> list[str]:
+        tt, bg, es = _khoa(kho, da)
+        cam = ("diff_loi",) if tep is None else cham_file_lenh(tt.cai_dat, kg, da, c, tep)      # D89, như mã
+        if (hien := doc_hien_hanh(bd, kho, da, b.id)) is None:
+            return ["du_lieu_loi"]
+        bead, sk = hien
+        if not spec_con_nguyen(b, bead, sk, dy, mo):
+            return ["du_lieu_doi"]
+        moi, bg, es = _khoa(kho, da)
+        cam = cam if moi.cai_dat == tt.cai_dat else ("file_lenh_loi",)
+        return ly_do_chua_merge_spec(moi, dung_pr=_dung_pr(pr, mo.du_lieu, f"tram/spec-{b.id}", da),
+                                     dau_pr_dung=pr.head == c, bat_ghi=bg, estop_bat=es, file_lenh=cam)
+    return gui_merge(gh, repo, kho, da.ten, b.id, ds, so_pr=mo.du_lieu["pr"], commit=c, loai="spec", ly_do=ly_do,
+                     luc=luc)
```

Sửa `tram/giao_viec/tick_github.py` (bản vá, áp bằng `git apply`):

```diff
--- a/tram/giao_viec/tick_github.py
+++ b/tram/giao_viec/tick_github.py
@@ -1,6 +1,6 @@
 """Vòng tick — bước GitHub của lát 4c (spec 4 §6.4 mục 4, §6.5, §7.3), chạy SAU khi đẩy pipeline: bead đang ở cột
 3 → mở PR / điền `pr` / tự merge khi dự án bật (TM-2, design D-1) / xác minh merge rồi đóng; feature `theo-plan` →
-mở PR cho commit spec đã duyệt.
+mở PR cho commit spec đã duyệt, rồi tự gộp PR đó khi dự án bật (D95, design D-11).
 Không chạy khi estop (ghi GitHub + beads), khi `p4c.gh` chưa nối, hoặc remote kho kiểm không phải github.com.
 `gh` lỗi ở một bead → đếm `loi_gh`, bead khác chạy tiếp; vòng sau làm lại (mọi bước idempotent)."""
 from collections import Counter
@@ -12,7 +12,7 @@
 from tram.giao_viec.pr import NHAN_REVIEW, NHAN_THEO_PLAN, mo_pr_bead, mo_pr_spec
 from tram.giao_viec.pr_merge import kiem_merge
 from tram.giao_viec.su_kien import su_kien_bead
-from tram.giao_viec.tu_merge import xet_tu_merge
+from tram.giao_viec.tu_merge import tu_merge_spec, xet_tu_merge
 from tram.phieu.kho import KhoPhieu
 
 
@@ -31,7 +31,8 @@
                      or xet_tu_merge(gh, repo, kho, kg, da, bd, b, ds, luc)
                      or kiem_merge(gh, repo, kho, kg, da, bd, b, ds, luc))
             else:
-                k = mo_pr_spec(gh, repo, kho, kg, da, b, ds, luc)
+                k = (mo_pr_spec(gh, repo, kho, kg, da, b, ds, luc)
+                     or tu_merge_spec(gh, repo, kho, kg, da, bd, b, ds, luc))
         except LoiGh:
             k = "loi_gh"
         if k:
```

- [ ] **Step 4: Chạy, mong đợi XANH**

```bash
tests/chan_host/chay.sh -q tests/test_tu_merge_spec.py tests/test_tu_merge_tuoi.py tests/test_tu_merge.py tests/test_pr.py tests/test_tick_theo_plan.py tests/test_tick_feature.py tests/test_vong_import.py tests/test_do_dai_ma.py
```
Xanh thật phiên tiếp tục: `13 passed in 3.35s` với `tests/test_tu_merge_spec.py tests/test_do_dai_ma.py tests/test_vong_import.py`, nhật ký chặn 0 dòng mới.

Rồi cả bộ → mong đợi `3506 passed` (số tính), nhật ký chặn 0 dòng mới.

- [ ] **Step 5: Commit**

```bash
git add tram/giao_viec/tu_merge.py tram/giao_viec/tick_github.py tests/test_tu_merge_spec.py tests/test_tu_merge_tuoi.py
git commit -m "feat(giao-viec): tự gộp PR spec Đại ca đã duyệt khi bật tự merge (TM-2 Task 4)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

### Task 5: Việc chờ Đại ca kèm lý do trên dashboard (khoá `cho_dai_ca`)

**Scenario:** "Thiếu hai điều kiện" (dashboard hiện hai lý do bằng lời thường), "Đại ca merge tay" (không còn chờ), "Xem khi không phải Đại ca" (GET không cần danh tính — tuyến có sẵn).

**Interfaces:** `tram.suy.tu_merge.cho_dai_ca(db, du_an, tieu_de=dict) -> list[dict]`, `TieuDe`, `tieu_de_bead(bo_dem, du_an) -> TieuDe` (Beads lỗi → `{}`); `chi_tiet_du_an(kho, ten, *, bat_ghi, tieu_de=dict)` — `tieu_de` là hàm không đối số trả `{bead_id: tiêu đề}`, chỉ gọi khi có việc chờ; `chi_tiet_du_an(...)["cho_dai_ca"]` (mục "Interfaces cho lát sau").

- [ ] **Step 1: Viết test**

Tạo mới `tests/test_suy_tu_merge.py` (nguyên văn):

```python
"""TM-2 (spec `tu-merge` "Thiếu điều kiện thì chờ Đại ca và nói rõ vì sao", "Đại ca merge tay"): khoá `cho_dai_ca`
của `GET /api/du-an/{ten}/tu-dong` — tính lúc đọc từ sự kiện, lý do bằng lời thường, tiêu đề bead ghép lúc đọc (không
nằm trong sự kiện); công tắc tắt → rỗng."""
from dataclasses import replace

from api_gia import tao_app_gia
from asgi_gia import goi
from bd_gia import BdGia
from bead_gia import bead
from kho_phieu_gia import LUC
from tram.phieu.kho import KhoPhieu
from tram.suy.tu_merge import cho_dai_ca
from tram.tu_dong.luu import doi_cai_dat


def _sk(kho, loai, du_lieu, bead_id, du_an="repo-nhap"):
    with kho.giao_dich():
        kho.ghi_su_kien(du_an, loai, du_lieu, luc=LUC, bead_id=bead_id, tac_nhan="tram/tu-merge")


def test_cho_dai_ca_tu_su_kien(tmp_path):
    kho = KhoPhieu(tmp_path / "sk.db")
    _sk(kho, "tu_merge.cho", {"ly_do": ["ci_dang_chay"], "commit": "c" * 40}, "rn-1")
    _sk(kho, "tu_merge.cho", {"ly_do": ["ci_do", "hang_rao_khach_thay"], "commit": "c" * 40}, "rn-1")
    _sk(kho, "tu_merge.cho", {"ly_do": ["schema_duong_dan"], "commit": "d" * 40}, "rn-2")
    _sk(kho, "tu_merge.cho", {"ly_do": ["ci_do"], "commit": "e" * 40}, "rn-3")
    _sk(kho, "tu_merge.bat_dau", {"ma_thao_tac": "tm-1", "commit": "e" * 40, "pr": 3, "loai": "code"}, "rn-3")
    _sk(kho, "tu_merge.loi", {"ma_thao_tac": "tm-4", "ma_loi": "gh-loi-3-lan"}, "rn-4")
    _sk(kho, "tu_merge.cho", {"ly_do": ["cot"], "commit": "f" * 40}, "rn-5")
    _sk(kho, "pr.da_merge", {"bead_id": "rn-5"}, "rn-5")                                # Đại ca merge tay
    _sk(kho, "tu_merge.cho", {"ly_do": ["qc"], "commit": "f" * 40}, "rn-6", du_an="khac")
    cho = {c["bead_id"]: c["ly_do"] for c in cho_dai_ca(kho.db, "repo-nhap")}
    assert set(cho) == {"rn-1", "rn-2", "rn-4"}
    assert [(l["nhan"], l["muc"]) for l in cho["rn-1"]] == [("CI chưa xanh", "can_nguoi"),
                                                            ("Chạm hàng rào: thứ khách thấy", "can_nguoi")]
    assert cho["rn-2"] == [{"ma": "schema_duong_dan", "nhan": "Cấu trúc DB — luôn chờ Đại ca", "muc": "loi"}]
    assert cho["rn-4"][0]["nhan"] == "Tự merge lỗi — cần Đại ca"
    goi = []
    ds = cho_dai_ca(kho.db, "repo-nhap", lambda: goi.append(1) or {"rn-2": "Thêm cột ghi chú"})
    assert {c["bead_id"]: c["tieu_de"] for c in ds} == {"rn-1": "", "rn-2": "Thêm cột ghi chú", "rn-4": ""}
    assert goi == [1] and cho_dai_ca(kho.db, "rong", lambda: goi.append(2) or {}) == [] and goi == [1]


def test_api_cho_dai_ca_chi_khi_bat(tmp_path):
    app, _ = tao_app_gia(tmp_path, {"repo-nhap": BdGia([bead("rn-1", title="Sửa định dạng ngày")])})
    kho = KhoPhieu(tmp_path / "sk.db")
    _sk(kho, "tu_merge.cho", {"ly_do": ["ci_do"], "commit": "c" * 40}, "rn-1")
    assert goi(app, "GET", "/api/du-an/repo-nhap/tu-dong").json()["cho_dai_ca"] == []
    doi_cai_dat(kho.db, "repo-nhap", lambda c: replace(c, tu_merge=True), tac_nhan="dai-ca/dashboard")
    [c] = goi(app, "GET", "/api/du-an/repo-nhap/tu-dong").json()["cho_dai_ca"]
    assert (c["bead_id"], c["tieu_de"], c["ly_do"][0]["nhan"]) == ("rn-1", "Sửa định dạng ngày", "CI chưa xanh")
    assert "commit" not in c
    sk_tieu_de = kho.db.execute("SELECT count(*) FROM su_kien WHERE du_lieu LIKE '%Sửa định dạng%'").fetchone()[0]
    assert sk_tieu_de == 0                                                     # tiêu đề không vào sự kiện
```

- [ ] **Step 2: Chạy, mong đợi ĐỎ**

```bash
tests/chan_host/chay.sh -q tests/test_suy_tu_merge.py
```
Đỏ thật (khi viết plan): lỗi khi thu thập:

```
E   ModuleNotFoundError: No module named 'tram.suy.tu_merge'
ERROR tests/test_suy_tu_merge.py
1 error in 1.21s
```
thoát 2, nhật ký chặn 0 dòng mới.

- [ ] **Step 3: Viết mã**

Tạo mới `tram/suy/tu_merge.py` (nguyên văn):

```python
"""Việc chờ Đại ca của tự merge (spec `tu-merge` "Thiếu điều kiện thì chờ Đại ca và nói rõ vì sao") — tính lúc đọc
từ sự kiện, không gọi GitHub hay Beads. Mỗi bead lấy sự kiện MỚI NHẤT trong nhóm dưới đây: `tu_merge.cho` (lý do do
trạm ghi khi lý do đổi), `tu_merge.loi`, `pr.khong_xac_minh` → bead đang chờ; các loại còn lại (gửi lệnh, xong, PR
đã merge, trả về, Đại ca kéo cột, bead đóng) → không còn chờ vì tự merge. Tiêu đề bead chỉ ghép lúc đọc cho
dashboard (`tieu_de_bead`, từ bộ đệm Beads của tram-api) — không bao giờ nằm trong sự kiện (INV-001). Logic nằm ở
đây; `suy/tu_dong.py` và `api/tuyen_tu_dong.py` (file chung với TM-1, TM-3) chỉ thêm dòng gọi."""
import json
import sqlite3
from collections.abc import Callable

from tram.beads.bd import LoiBd
from tram.giao_viec.tu_merge_xet import MUC, NHAN

TieuDe = Callable[[], dict[str, str]]

CHO = {"tu_merge.loi": ["tu_merge_loi"], "pr.khong_xac_minh": ["pr_khong_xac_minh"]}
LOAI = ("tu_merge.cho", "tu_merge.bat_dau", "tu_merge.xong", "tu_merge.loi", "pr.da_merge", "pr.khong_xac_minh",
        "cot.tra_ve", "cot.dai_ca_sua", "bead.dong")


def cho_dai_ca(db: sqlite3.Connection, du_an: str, tieu_de: TieuDe = dict) -> list[dict]:
    """Mới → cũ: `{bead_id, tieu_de, luc, ly_do: [{ma, nhan, muc}]}`; `muc` = loi (luôn chờ) | tat (đang chờ CI) |
    can_nguoi. `tieu_de()` (đọc Beads) chỉ gọi khi có việc chờ; thiếu → chuỗi rỗng."""
    cuoi = {}
    for bead_id, loai, luc, du_lieu in db.execute(
            f"SELECT bead_id, loai, luc, du_lieu FROM su_kien WHERE du_an = ? AND bead_id IS NOT NULL"
            f" AND loai IN ({','.join('?' * len(LOAI))}) ORDER BY id", (du_an, *LOAI)):
        cuoi[bead_id] = (loai, luc, du_lieu)
    ra = []
    for bead_id, (loai, luc, du_lieu) in cuoi.items():
        ma = json.loads(du_lieu).get("ly_do") if loai == "tu_merge.cho" else CHO.get(loai)
        if isinstance(ma, list) and ma:
            ra.append({"bead_id": bead_id, "luc": luc, "ly_do": [
                {"ma": m, "nhan": NHAN.get(m, m), "muc": MUC.get(m, "can_nguoi")} for m in ma if isinstance(m, str)]})
    ten = tieu_de() if ra else {}
    return sorted(({**c, "tieu_de": ten.get(c["bead_id"], "")} for c in ra), key=lambda x: x["luc"], reverse=True)


def tieu_de_bead(bo_dem, du_an: str) -> TieuDe:
    """Hàm đọc tiêu đề cho `cho_dai_ca` — chỉ chạy khi có việc chờ; Beads lỗi → rỗng (dashboard vẫn hiện lý do)."""
    def doc() -> dict[str, str]:
        try:
            return {b.id: b.title for b in bo_dem.lay(du_an)}
        except LoiBd:
            return {}
    return doc
```

Sửa `tram/suy/tu_dong.py` (bản vá, áp bằng `git apply`):

```diff
--- a/tram/suy/tu_dong.py
+++ b/tram/suy/tu_dong.py
@@ -2,6 +2,7 @@
 TM-2 (việc chờ kèm lý do), TM-3 (sẵn sàng deploy, lịch sử, bộ đếm hỏng) THÊM khoá vào hai bảng này, không đổi khoá
 có sẵn."""
 from tram.su_kien.kho import KhoSuKien
+from tram.suy.tu_merge import TieuDe, cho_dai_ca  # TM-2
 from tram.tu_dong.cai_dat import KHOA_CUNG, sang_api
 from tram.tu_dong.luu import DU_AN_TRAM, TamDung, doc_trang_thai, lich_su_doi, tam_dung_cua
 
@@ -22,8 +23,9 @@ def tom_tat_du_an(kho: KhoSuKien, ten: str, *, bat_ghi: bool) -> dict:
             "du_lenh": tt.cai_dat.du_lenh, "tam_dung": tam_dung_api(tt.tam_dung_du_an)}
 
 
-def chi_tiet_du_an(kho: KhoSuKien, ten: str, *, bat_ghi: bool) -> dict:
+def chi_tiet_du_an(kho: KhoSuKien, ten: str, *, bat_ghi: bool, tieu_de: TieuDe = dict) -> dict:
     tt = doc_trang_thai(kho.db, ten)
     return {"du_an": ten, "bat_ghi": bat_ghi, "cai_dat": sang_api(tt.cai_dat), "du_lenh": tt.cai_dat.du_lenh,
             "phien_ban": tt.phien_ban, "tam_dung": tam_dung_api(tt.tam_dung_du_an), "khoa_cung": list(KHOA_CUNG),
-            "lich_su_doi": lich_su_doi(kho.db, ten)}
+            "lich_su_doi": lich_su_doi(kho.db, ten),
+            "cho_dai_ca": cho_dai_ca(kho.db, ten, tieu_de) if tt.cai_dat.tu_merge else []}   # TM-2: tắt → []
```

Sửa `tram/api/tuyen_tu_dong.py` (bản vá, áp bằng `git apply`):

```diff
--- a/tram/api/tuyen_tu_dong.py
+++ b/tram/api/tuyen_tu_dong.py
@@ -13,6 +13,7 @@ from tram.api.phu_thuoc import kiem_du_an_bead
 from tram.api.than import ThanCaiDatTuDong, ThanGhi
 from tram.chu import estop
 from tram.suy.tu_dong import chi_tiet_du_an, chung, tom_tat_du_an
+from tram.suy.tu_merge import tieu_de_bead  # TM-2
 from tram.thao_tac.tu_dong import luu_cai_dat_thao_tac, tam_dung_thao_tac
 from tram.tu_dong.cai_dat import tu_api
 from tram.tu_dong.luu import DU_AN_TRAM
@@ -56,7 +57,8 @@ def r_chi_tiet(ten: str, request: Request) -> dict:
     pt = request.app.state.pt
     kiem_du_an_bead(pt, ten)
     with closing(pt.mo_kho()) as kho:
-        return {**_chung(request, kho), **chi_tiet_du_an(kho, ten, bat_ghi=_bat_ghi(pt, ten))}
+        return {**_chung(request, kho), **chi_tiet_du_an(kho, ten, bat_ghi=_bat_ghi(pt, ten),
+                                                         tieu_de=tieu_de_bead(pt.bo_dem, ten))}
 
 
 def _chay(request: Request, lam) -> dict:
```

- [ ] **Step 4: Chạy, mong đợi XANH**

```bash
tests/chan_host/chay.sh -q tests/test_suy_tu_merge.py tests/test_api_tu_dong.py tests/test_vong_import.py tests/test_do_dai_ma.py
```
Xanh thật phiên tiếp tục: `9 passed in 1.65s` với `tests/test_suy_tu_merge.py tests/test_do_dai_ma.py tests/test_vong_import.py`; API TM-1 nằm trong bộ tập trung cuối, nhật ký chặn 0 dòng mới.

Rồi cả bộ → mong đợi `3508 passed` (số tính), nhật ký chặn 0 dòng mới.

- [ ] **Step 5: Commit**

```bash
git add tram/suy/tu_merge.py tram/suy/tu_dong.py tram/api/tuyen_tu_dong.py tests/test_suy_tu_merge.py
git commit -m "feat(suy): việc chờ Đại ca của tự merge kèm lý do lời thường (TM-2 Task 5)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

### Task 6: Con của feature `theo-plan` vào được cột 3 rồi tự merge (Codex Q3, bead `bs-2bd.1.28`)

**Scenario:** "Con của feature đã duyệt — trạm merge PR của `rn-11`" (spec `tu-merge`, D72) đi hết đường THẬT; điều kiện 8 của spec 4 §5.1 (spec chưa vào nhánh chính → con chưa vào cột 3).

**Lỗi có sẵn (đọc mã + tái hiện đỏ thật):** `tram/giao_viec/tick_cot_3.py:43` gọi `ly_do_khong_giao(moi, theo_id, set(), da)` — thiếu `spec_da_merge` (mặc định rỗng), trong khi `doc_lai.py:46` truyền `da_merge(...)` và `tick_pipeline.py:60` tính đúng tập. Feature cha còn nhãn `theo-plan` tới khi `feature.xong` → mọi con trả `cho-merge-spec` ở lần xét lại cuối, KHÔNG BAO GIỜ vào cột 3 qua vòng tick. Ca `_ly()` "Con của feature đã duyệt" ở Task 2 chỉ là hàm thuần, không chứng minh gì cho đường này. Lát TM-2 nhận sửa (Đại ca giao, bead `bs-2bd.1.28` chỉ đóng sau nghiệm thu triển khai).

**Interfaces:** không đổi chữ ký. `vao_cot_3_an_toan` tính `feature_da_merge(kho, da, [cha], kg)` trên bản Beads vừa đọc lại (chỉ cha của bead — không gọi Git khi bead không có cha).

- [ ] **Step 1: Viết test**

Tạo mới `tests/test_tu_merge_con_feature.py` (nguyên văn):

```python
"""Codex Q3 — bead bs-2bd.1.28 (spec 4 §5.1 điều kiện 8; spec `tu-merge` Scenario "Con của feature đã duyệt"): con của
feature `theo-plan` mà commit spec đã duyệt NẰM TRONG nhánh chính đi hết đường thật — kiểm lại + QC đạt → vòng tick
đưa vào cột 3 (`vao_cot_3_an_toan` đọc lại Beads rồi xét lại điều kiện, CÓ tập feature đã merge spec) → mở PR → tự
merge → xác minh → đóng. Spec chưa vào nhánh chính → con vẫn chờ (`cho-merge-spec`), không vào cột 3."""
from bead_gia import bead
from gh_gia import REPO
from su_kien_gia import sk
from test_tu_merge import dung_tu_merge, merge_goi, tm
from tram.giao_viec.tick import mot_vong_tick

F = bead("hr-f", issue_type="feature", title="Hoa hồng tạm tính", labels=["theo-plan"])


def _duyet(t, commit):
    sk(t.kho, "spec.duyet", {"feature": "hr-f", "commit": commit, "digest_bead": "sha256:b", "bead_moi": [],
                             "ma_thao_tac": "dy-1"}, bead_id="hr-f")


def test_con_feature_spec_da_merge_vao_cot_3_roi_tu_merge(tmp_path, monkeypatch):
    t, gh, q = dung_tu_merge(tmp_path, monkeypatch, them=(F,), parent="hr-f")
    _duyet(t, t.k.main)                                          # commit spec đã duyệt là tổ tiên origin/main
    r = mot_vong_tick(t.bo)
    assert (r.get("cot_3"), r.get("pr_mo")) == (1, 1)
    gh.dat(1, ci="xanh")
    assert mot_vong_tick(t.bo)["tu_merge"] == 1 and merge_goi(gh) == [("merge_pr", REPO, 1, q)]
    assert len(tm(t, "tu_merge.xong")) == 1
    assert mot_vong_tick(t.bo)["da_merge"] == 1 and t.g.beads["hr-1"].status == "closed"


def test_con_feature_spec_chua_merge_thi_chua_vao_cot_3(tmp_path, monkeypatch):
    t, gh, q = dung_tu_merge(tmp_path, monkeypatch, them=(F,), parent="hr-f")
    _duyet(t, t.k.day("tram/spec-hr-f", {"docs/specs/x.md": "spec\n"}, tu=t.k.main))
    r = mot_vong_tick(t.bo)
    assert "cot_3" not in r and "pr_mo" not in r and gh.goi == [] and tm(t) == []
```

- [ ] **Step 2: Chạy, mong đợi ĐỎ**

```bash
tests/chan_host/chay.sh -q tests/test_tu_merge_con_feature.py
```
Đỏ thật (mã Task 1–5, `tick_cot_3.py` gốc) — đúng lỗi có sẵn, vòng tick không đưa con vào cột 3:

```
E       assert (None, None) == (1, 1)
FAILED tests/test_tu_merge_con_feature.py::test_con_feature_spec_da_merge_vao_cot_3_roi_tu_merge
1 failed, 1 passed
```
thoát 1, nhật ký chặn 0 dòng mới (ca đối chứng "spec chưa merge" xanh cả trước lẫn sau sửa — canh sửa quá tay).

- [ ] **Step 3: Viết mã**

Sửa `tram/giao_viec/tick_cot_3.py` (bản vá, áp bằng `git apply`):

```diff
--- a/tram/giao_viec/tick_cot_3.py
+++ b/tram/giao_viec/tick_cot_3.py
@@ -3,7 +3,9 @@
 1. Ref công bố TRÊN REMOTE (kho kiểm vừa `git fetch` đầu pha) đúng bằng commit trong `giao.cong_bo` mới nhất (3a-2
    công bố bằng CAS). Khác = nhánh bị đẩy ngoài luồng → không vào cột 3, escalation `nhanh-bi-day` (G10: PR Đại ca
    tạo từ `tram/<bead>` phải trỏ đúng commit trạm đã kiểm). Một escalation mỗi (chu kỳ ngân sách, SHA remote).
-2. Đọc lại bead và sự kiện ngay trước khi ghi nhãn: bead có thể đã bị kéo, bị chặn trong lúc kiểm lại bead khác."""
+2. Đọc lại bead và sự kiện ngay trước khi ghi nhãn: bead có thể đã bị kéo, bị chặn trong lúc kiểm lại bead khác.
+   Điều kiện 8 xét trên feature cha của bản vừa đọc (TM-2, Codex Q3): thiếu tập "spec đã merge" thì con của feature
+   `theo-plan` không bao giờ vào cột 3."""
 from datetime import datetime
 from pathlib import Path
 
@@ -15,6 +17,7 @@ from tram.giao_viec.escalation import tao_escalation
 from tram.giao_viec.git_kiem import sha_cua
 from tram.giao_viec.ngan_sach import bat_dau_chu_ky
 from tram.giao_viec.pipeline import buoc_ke_tiep
+from tram.giao_viec.spec_merge import feature_da_merge
 from tram.giao_viec.su_kien import moi_nhat, su_kien_bead
 from tram.giao_viec.ung_vien import trang_thai_bead, viec_ton_cua
 from tram.phieu.kho import KhoPhieu
@@ -40,7 +43,8 @@ def vao_cot_3_an_toan(bd, kho: KhoPhieu, kg: Path, da: DuAn, b, luc: datetime, *
     except LoiBd:
         return None
     moi = theo_id.get(b.id)
-    if moi is None or ly_do_khong_giao(moi, theo_id, set(), da) is not None or buoc_ke_tiep(
+    merge = feature_da_merge(kho, da, [theo_id[moi.parent]], kg) if moi and moi.parent in theo_id else frozenset()
+    if moi is None or ly_do_khong_giao(moi, theo_id, set(), da, merge) is not None or buoc_ke_tiep(
             ds, trang_thai_bead(kho, da.ten, moi, theo_id, viec_ton_cua(kho, da.ten))) != "cot_3":
         return None
     return "cot_3" if vao_cot_3(bd, kho, kg, da, moi, ds, la_spike=moi.issue_type == "spike",
```

- [ ] **Step 4: Chạy, mong đợi XANH**

```bash
tests/chan_host/chay.sh -q tests/test_tu_merge_con_feature.py tests/test_tick_4c.py tests/test_tick.py tests/test_tick_hai_pha.py tests/test_tick_feature.py tests/test_vong_import.py tests/test_do_dai_ma.py
```
Xanh thật: `9 passed in 1.99s` với `tests/test_tu_merge_con_feature.py tests/test_do_dai_ma.py tests/test_vong_import.py`; lệnh rộng ở trên còn vướng test nền thu hồi tiến trình trong sandbox, nhật ký chặn 0 dòng mới.

Rồi cả bộ → mong đợi `3510 passed` (số tính; số đo thật ở Task 7), nhật ký chặn 0 dòng mới.

- [ ] **Step 5: Commit**

```bash
git add tram/giao_viec/tick_cot_3.py tests/test_tu_merge_con_feature.py
git commit -m "fix(giao-viec): con của feature theo-plan đã merge spec vào được cột 3 (TM-2 Task 6, bs-2bd.1.28)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

### Task 7: Tài liệu bị ảnh hưởng

- [ ] **Step 1: Sửa docs** — `MODULES.md`: dòng `tram/giao_viec/` và dòng tích hợp `git`, `gh` (không còn đúng "không merge"); `tasks.md` trỏ plan này. ADR thay một phần ADR-0007, `AGENT_RULES.md` §11, `PROJECT.md`… thuộc mốc 6.1 (plan tài liệu sau bốn lát), không làm ở đây.

Sửa `docs/MODULES.md` (bản vá, áp bằng `git apply`):

```diff
--- a/docs/MODULES.md
+++ b/docs/MODULES.md
@@ -30,7 +30,7 @@
 | `tram/phieu/` | kho phiếu: khe, máy thợ, lượt, giữ ngân sách, cầu dao hạn mức, mã ghép |
 | `tram/han_muc/` | đọc hạn mức CLI, ngưỡng ngừng |
 | `tram/usage/` | đếm usage (ccusage tuỳ chọn) |
-| `tram/giao_viec/` | vòng tick, pipeline theo loại bead, chọn khe, kiểm lại, QC, luồng feature, PR, xác minh merge; harness S6 (chứng cứ từng nguồn lịch `chung_cu_probe.py`), ống `git archive \| tar` có chủ hai đầu (`ong_chep.py`) |
+| `tram/giao_viec/` | vòng tick, pipeline theo loại bead, chọn khe, kiểm lại, QC, luồng feature, PR, tự merge có điều kiện (`tu_merge*.py`, `gh_tu_merge.py`), xác minh merge; harness S6 (chứng cứ từng nguồn lịch `chung_cu_probe.py`), ống `git archive \| tar` có chủ hai đầu (`ong_chep.py`) |
 | `tram/tho/` | tiến trình quản lý thợ: đăng ký, nhịp tim, chạy CLI dưới principal, sandbox, worktree, bàn giao; dọn theo UID của khe (`don_uid.py`), chấm thăm dò cách ly (`cham_tham_do.py`) |
 | `tram/chay_cli/` | dựng lệnh `claude -p` / `codex`, đọc stream, quyền theo vai |
 | `tram/kiem/` | chạy lệnh có giới hạn, cây tiến trình, danh tính UID, vòng đời tiến trình, đường cấm; hợp đồng sở hữu tiến trình con (`so_huu.py`), hoãn ngắt (`ngat.py`), bảng tiến trình của nhân (`bang_tien_trinh.py`), giữ xác gốc (`giu_xac.py`), gửi tín hiệu nhóm (`gui_tin.py`) |
@@ -52,7 +52,7 @@
 | Hệ ngoài | Dùng để | Timeout | Hỏng thì |
 | --- | --- | --- | --- |
 | `bd` (Beads) | đọc/ghi việc của dự án con | 120 giây | API trả 502; vòng quét ghi lỗi |
-| `git`, `gh` | worktree, công bố, mở/xem PR (không merge) | theo lệnh | bead ở lại cột 3, sự kiện lỗi |
+| `git`, `gh` | worktree, công bố, mở/xem PR; `gh pr merge --merge --match-head-commit` chỉ khi dự án bật tự merge | theo lệnh; `gh` 60 giây | bead ở lại cột 3, sự kiện lỗi; tự merge lỗi 3 lần → `tu_merge.loi`, tin "trạm lỗi" |
 | `claude -p`, `codex` | agent thợ chạy việc | trần của phiếu | thu hồi phiếu, giao lại |
 | Anthropic API | chấm cột, tách/gộp ký ức | chờ tối đa 120 giây/lời gọi, kể cả đợi chỗ; SDK không retry (`tram/llm/han_goi.py`) | quá hạn: bỏ chờ, không huỷ luồng; tối đa 2 luồng sống/tiến trình; hết chỗ: chờ tới hạn rồi lỗi, không mở lời gọi mới |
 | Ollama bge-m3 | embed ký ức (chỉ localhost) | 30 giây | memory báo lỗi, không lùi về vector giả |
```

Sửa `openspec/changes/tu-merge-tu-deploy/tasks.md` (bản vá, áp bằng `git apply`):

```diff
--- a/openspec/changes/tu-merge-tu-deploy/tasks.md
+++ b/openspec/changes/tu-merge-tu-deploy/tasks.md
@@ -1,7 +1,8 @@
 # Tasks — tự merge + tự deploy
 
 Plan TDD: chia bốn lát — bảng ở `docs/plans/2026-10-18-tm-0-chia-lat.md`; lát nền (mốc 1.1–1.7, 4.1) ở
-`docs/plans/2026-10-18-lat-tm-1-nen-cai-dat.md`. Mỗi mốc dưới đây là một mốc nghiệm thu, không chép mã; bằng chứng là
+`docs/plans/2026-10-18-lat-tm-1-nen-cai-dat.md`; tự merge (mốc 2.1–2.7) ở
+`docs/plans/2026-10-18-lat-tm-2-tu-merge.md`. Mỗi mốc dưới đây là một mốc nghiệm thu, không chép mã; bằng chứng là
 test của plan (chạy qua `tests/chan_host/chay.sh -q`) hoặc kịch bản cổng trong sổ tay chạy thật.
 
 ## 0. Cổng trước khi viết plan
```

- [ ] **Step 2: Kiểm docs và cả bộ**

```bash
ls tram/giao_viec/gh_tu_merge.py tram/giao_viec/tu_merge.py tram/giao_viec/tu_merge_gui.py tram/giao_viec/tu_merge_xet.py docs/plans/2026-10-18-lat-tm-2-tu-merge.md
tests/chan_host/chay.sh -q
```
Mong đợi: `ls` không lỗi; cả bộ `3510 passed` (mục tiêu nghiệm thu, chưa đạt trong sandbox), nhật ký chặn 0 dòng mới. `git diff 85ce7f4 -- tram | grep -c "CREATE TABLE"` = 0.

- [ ] **Step 3: Commit**

```bash
git add docs/MODULES.md openspec/changes/tu-merge-tu-deploy/tasks.md
git commit -m "docs: MODULES thêm tự merge, tasks.md trỏ plan TM-2

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

## Kiểm chứng plan (lịch sử phiên tiếp tục vòng 2, 18/10/2026)

- **Tiếp tục đúng phần dở:** đọc `git log -3`, status và diff trên `411efce`; giữ các sửa Q2/Q3/Q15
  đã có. Bốn file nền TM-1 trong cây trùng `85ce7f4`; `git diff 0f88957 85ce7f4 -- tram tests
  docs/MODULES.md openspec` chỉ có `tram/tu_dong/file_cam.py`, `tram/bao_tin/chong_on.py`,
  `tests/test_tu_dong_khoa.py`, `tests/test_chong_on_tu_dong.py`. Không sửa hợp đồng TM-1.
- **Môi trường:** dùng `.venv` có sẵn, `UV_NO_SYNC=1`, cache UV trong `scratchpad/tm2-v2/uv-cache`
  vì cache mặc định không ghi được. Mọi test đi qua `tests/chan_host/chay.sh`, không mạng, không `gh` thật.
  Bản sao kiểm chứng ở `scratchpad/tm2-v2/check` và `check2`, `PYTHONPATH` trỏ đúng bản đang kiểm.
- **Nền:** `tests/chan_host/chay.sh -q --collect-only` → **3422 tests collected**.
  Lệnh cả bộ đã chạy; lần chẩn đoán `tests/chan_host/chay.sh -q -x` → **1 failed, 139 passed in 19.90s**,
  0 dòng chặn mới. Lỗi đầu tiên là `test_ban_chep_dung_commit_co_repo_git_khong_bi_export_ignore_giau`:
  `LoiBanChep: lệnh dưới tram-kiem: không xác nhận thu hồi cây tiến trình — không công nhận`.
  Đọc trực tiếp `chup_nhan()` cho `PermissionError: [Errno 1] sysctl: không đọc được kích thước bảng`.
  Đây là giới hạn sandbox đã có **trước TM-2**, không sửa test hoặc bỏ hàng rào để làm xanh.
- **Sửa trực tiếp #2 của Codex:** hồi phục hành vi cũ (kết luận lỗi ngay lần gửi thứ ba) → hai test
  `test_con_mo_thi_gui_lai_cung_commit_ba_lan_roi_loi` và
  `test_lan_ba_mat_phan_hoi_van_doi_soat_thanh_cong` **2 failed, 27 deselected**.
  Đỏ lần lượt do `[1, 1, None] != [1, 1, 1]` và `KeyError: 'loi_gh'`.
  Trả lại mã Codex → cả hai nằm trong bộ 120 test xanh.
- **Q2/C2:** bỏ kiểm `cham_file_lenh` để tái hiện cửa merge vòng 1 → **6 failed, 29 deselected**:
  5 ca đổi lệnh trong `gh pr view` (tương đối, tuyệt đối, `..`, sau `=`, thư mục) vẫn gửi merge;
  PR spec cũng merge sai. Trả kiểm D89 về → xanh. Cùng file được đặt trong `cho_phep` vẫn phải chờ.
- **Q3, bead `bs-2bd.1.28`:** Task 6 test trên `tick_cot_3.py` gốc → **1 failed, 1 passed**,
  `assert (None, None) == (1, 1)`. Áp patch truyền tập spec đã merge → **9 passed** khi chạy test
  tích hợp và hai file kiểm cấu trúc. Ca dương đi tới merge + đóng bead; ca spec chưa merge vẫn chờ.
- **Bổ sung D89 khi soát bản dở:** callback cũ chỉ trả tên symlink, bỏ lọt PR sửa đích mà giữ nguyên link.
  Test mới + kỳ vọng chặn symlink → **4 failed** trên bản dở; sửa kiểm từng đoạn trước khi rút gọn `..`,
  gặp symlink → `file_lenh_loi` (đóng bảo thủ) → **7 passed** gồm test đường dẫn và độ dài.
  Không đi theo symlink ra host, không giả định việc cấm tên link bảo vệ được đích.
- **Áp lại từ chính plan:** trên bản sao nền sạch, từng task áp test trước → chạy đỏ → áp mã;
  các bản vá đều qua `git apply --check` trước khi áp. Task 1–5 đỏ do thiếu module/hàm tương ứng;
  Task 6 đỏ đúng lỗi nghiệp vụ ở trên. Áp cả Task 7 rồi so mọi file trong `tram/`, `tests/`,
  `openspec/`, `docs/MODULES.md` với bản đã chạy (bỏ `__pycache__`) → **0 khác biệt**.
- **Cửa chốt sau Git:** `test_doi_lenh_trong_luc_doc_cay_git_thi_cho` đổi lệnh trong `_cay`, sau
  lần đọc cài đặt đầu tiên → **1 failed, 29 deselected** trên bản dở (đã gửi merge).
  Mã cuối đọc lại cài đặt/khoá sau D89 ở cả PR code và PR spec; khác cài đặt đã dùng để so → chờ
  `file_lenh_loi`, vòng sau xét lại. Test xanh trong bộ cuối.
- **Bộ tập trung trên bản cuối:** lệnh dưới → **120 passed in 30.43s**; sau áp lại từ plan: **120 passed in 29.37s**.
  Cả hai lượt: 0 dòng chặn mới, 0 điểm mù, 143 push giả lập (không push thật).

```bash
tests/chan_host/chay.sh -q tests/test_gh.py tests/test_gh_tu_merge.py tests/test_tu_merge_xet.py tests/test_tu_merge.py tests/test_tu_merge_rao.py tests/test_tu_merge_spec.py tests/test_tu_merge_con_feature.py tests/test_suy_tu_merge.py tests/test_api_tu_dong.py tests/test_do_dai_ma.py tests/test_vong_import.py
```

- **Cả bộ sau lát:** 3510 test được thu thập; không tuyên bố 3510 passed. Chạy cả bộ với `-x` để
  đối chiếu lỗi nền: **1 failed, 139 passed in 19.87s**, 0 dòng chặn mới; vẫn dừng ở test bản chép/thu hồi tiến trình, trước các test TM-2 (đo trước hai test symlink và test cửa chốt cuối).
  Lệnh rộng Task 3 trong sandbox: **3 failed, 65 passed**, ba lỗi đều thuộc `test_tick.py` /
  `test_tick_hai_pha.py` gọi kiểm lại thật và thiếu kết quả `kiem_lai` do không đọc được bảng tiến trình.
  **Cần môi trường cho phép đọc bảng tiến trình để đạt cổng cả bộ trước triển khai.**
- **Hoàn nguyên phiên này:** nội dung bốn file nền TM-1 đã trả về HEAD; `git diff HEAD --stat`
  chỉ còn file plan. Lệnh `git restore --source=HEAD --staged --worktree -- <bốn file>` bị sandbox
  từ chối tạo `.git/worktrees/sua-tm2/index.lock`, nên **index vẫn giữ bốn mục staged có từ phiên trước**.
  Cần bỏ staged bốn file nền ngoài sandbox; không stage/commit chúng. Không tạo báo cáo riêng vì Đại ca
  yêu cầu chỉ giữ file plan.
- Không chạy cổng OS, không commit/merge/push, không ghi Beads. Các số xanh toàn bộ từ phiên trước
  (`3412`, `3497`) là lịch sử trên nền cũ; không dùng làm bằng chứng cho nền `85ce7f4` và bản cuối này.

## Bước cổng trên OS thật

Không có trong lát này. Chạy `gh pr merge` thật, đọc `statusCheckRollup` thật, bảo vệ nhánh repo nháp (D94) thuộc cổng G8 "tự merge/tự deploy repo nháp" — viết ở plan tài liệu mốc 6.2–6.4 sau khi TM-2/TM-3 ghép, chạy sau S7 và kênh `unix-socket` (design Migration Plan bước 2). Kịch bản G8 phần tự merge phải kiểm: (a) `gh pr merge <so> --repo <r> --merge --match-head-commit <sha>` của `gh` đang cài chấp nhận đúng các cờ này, không hỏi tương tác khi `GH_PROMPT_DISABLED=1`; (b) đẩy thêm commit vào nhánh PR rồi chạy lệnh với sha cũ → GitHub từ chối; (c) `gh pr view --json statusCheckRollup` trả `__typename` `CheckRun`/`StatusContext` như `gh_tu_merge.trang_thai_ci` giả định; (d) repo không có CI → trạm chờ, tắt nút CI → trạm merge.

## Rủi ro còn lại (không đóng bằng plan này)

1. **Hai PR mỗi cái xanh, gộp lại hỏng** — không có hàng đợi merge (design Risks); lát TM-3 lo kiểm còn sống + tự lùi.
2. **Hàng đợi merge của GitHub** (nếu Đại ca bật): `gh pr merge` nhận lệnh mà chưa merge → trạm không ghi `xong`, đối soát, gửi lại tới 3 lần rồi báo lỗi. An toàn (không merge commit khác) nhưng ồn. Không bật hàng đợi merge trên repo dùng tự merge (ghi vào kịch bản G8).
3. **D91 chỉ xét đường dẫn**: việc nhạy cảm mà diff nằm ngoài `duong_dan` của hàng rào vẫn tự merge — Đại ca giữ `duong_dan` đủ rộng; từ khoá `schema` chỉ bắt được chữ đã khai.
4. **D89 chỉ bắt file lệnh NHẮC TRỰC TIẾP** (design Risks, như TM-1): script gọi tiếp file khác, `make` đọc `Makefile` ngầm, lệnh `cd` sang thư mục khác rồi chạy đường tương đối — không vào tập cấm. Khuyên để script deploy ngoài repo. Token tuyệt đối chỉ đổi được theo `da.duong_dan` và kho kiểm; worktree deploy của TM-3 ở chỗ khác thì TM-3 thêm gốc của nó khi dùng lại `loai_trong_repo`.
5. **Kẽ hở sau lần đọc cuối** giữa lần đọc lại (công tắc, ba lệnh) và `gh pr merge` — GitHub không có "merge nếu trạm còn cho phép" (Thiết kế 2). Đại ca đổi lệnh đúng trong kẽ đó thì lần merge này đi; lần kiểm tiếp theo của TM-3 (kiểm lại trước deploy) vẫn chặn theo lệnh mới.
6. **`doc_tep` dùng `tram/kiem/diff.py` có sẵn — lời gọi `git merge-base`/`git diff` chưa có hạn giờ** (cùng loại Codex Q5 của TM-3). Lời gọi Git MỚI của lát (`ls-tree`) có hạn 60 giây. Thêm hạn cho `tram/kiem/diff.py` là việc của lát sửa Q5 (TM-3 hoặc việc riêng), không sửa ở đây để không chạm file kiểm đường cấm (kill list mục 3).
7. **PR do trạm mở vẫn ghi "Chỉ Đại ca merge (Q7)"** trong thân PR (`pr.py` `_than`, kill list mục 5) — chữ lỗi thời khi tự merge bật; sửa cùng mốc 6.1.
8. **Lệnh `gh` thật chưa từng chạy** (S7 chưa đạt): hình dạng JSON và cú pháp cờ chỉ theo tài liệu `gh` 2.x — cổng G8 (a)–(d).

## Ghép trên lát trước

Thứ tự ghép (luật chung vòng 2): TM-1 → **TM-2** → TM-3 → TM-4 → TC. Lát trước của TM-2 là **TM-1 vòng 2** (`85ce7f4`). File TM-2 sửa mà TM-1 cũng sửa/tạo — đã đọc hunk TM-1 vòng 2; trên `85ce7f4` các file này giống hệt `0f88957`, nên hunk TM-2 áp sạch, không phải ghép tay:

| File chung | TM-1 vòng 2 | TM-2 thêm | Sau ghép (đếm thật) |
| --- | --- | --- | --- |
| `tram/suy/tu_dong.py` | tạo (29 dòng) | 1 dòng import + 1 dòng khoá `cho_dai_ca`; chữ ký `chi_tiet_du_an` thêm `tieu_de: TieuDe = dict` | **31** dòng |
| `tram/api/tuyen_tu_dong.py` | tạo (102 dòng) | 1 dòng import `tieu_de_bead` + tách dòng `return` của `r_chi_tiet` thành 2 (logic đọc tiêu đề ở `tram/suy/tu_merge.py`, không ở router — Codex Q15) | **104** dòng (còn 16 dòng cho TM-3; TM-3 vòng 1 thêm 11 → 115 ≤ 120) |
| `docs/MODULES.md` | sửa dòng `tram/tu_dong/` | sửa dòng `tram/giao_viec/` và dòng `git`, `gh` (khác dòng TM-1) | hai dòng của TM-2 như Task 7; dòng `tram/tu_dong/` giữ của TM-1 |
| `openspec/changes/tu-merge-tu-deploy/tasks.md` | sửa đoạn "Plan TDD" (trỏ plan TM-1) | nối thêm "tự merge (mốc 2.1–2.7) ở …tm-2…" vào CÙNG đoạn | đoạn hợp nhất như dưới |
| `tram/tu_dong/file_cam.py` | sửa theo hợp đồng D89 mới | **không sửa** — chỉ gọi; phụ thuộc cứng | — |

Nội dung hợp nhất `tram/suy/tu_dong.py` (toàn file, 31 dòng — TM-3 thêm khoá của nó thành dòng riêng sau dòng `cho_dai_ca`, thêm import riêng):

```python
"""Trạng thái hiển thị của tự merge / tự deploy (`dieu-khien-tu-dong`, design D-5) — tính lúc đọc từ sự kiện.
TM-2 (việc chờ kèm lý do), TM-3 (sẵn sàng deploy, lịch sử, bộ đếm hỏng) THÊM khoá vào hai bảng này, không đổi khoá
có sẵn."""
from tram.su_kien.kho import KhoSuKien
from tram.suy.tu_merge import TieuDe, cho_dai_ca  # TM-2
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


def chi_tiet_du_an(kho: KhoSuKien, ten: str, *, bat_ghi: bool, tieu_de: TieuDe = dict) -> dict:
    tt = doc_trang_thai(kho.db, ten)
    return {"du_an": ten, "bat_ghi": bat_ghi, "cai_dat": sang_api(tt.cai_dat), "du_lenh": tt.cai_dat.du_lenh,
            "phien_ban": tt.phien_ban, "tam_dung": tam_dung_api(tt.tam_dung_du_an), "khoa_cung": list(KHOA_CUNG),
            "lich_su_doi": lich_su_doi(kho.db, ten),
            "cho_dai_ca": cho_dai_ca(kho.db, ten, tieu_de) if tt.cai_dat.tu_merge else []}   # TM-2: tắt → []
```

Nội dung hợp nhất `tram/api/tuyen_tu_dong.py` (toàn file, **104 dòng**):

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
from tram.suy.tu_merge import tieu_de_bead  # TM-2
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
        return {**_chung(request, kho), **chi_tiet_du_an(kho, ten, bat_ghi=_bat_ghi(pt, ten),
                                                         tieu_de=tieu_de_bead(pt.bo_dem, ten))}


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

Đoạn hợp nhất `openspec/changes/tu-merge-tu-deploy/tasks.md`:

```markdown
Plan TDD: chia bốn lát — bảng ở `docs/plans/2026-10-18-tm-0-chia-lat.md`; lát nền (mốc 1.1–1.7, 4.1) ở
`docs/plans/2026-10-18-lat-tm-1-nen-cai-dat.md`; tự merge (mốc 2.1–2.7) ở
`docs/plans/2026-10-18-lat-tm-2-tu-merge.md`. Mỗi mốc dưới đây là một mốc nghiệm thu, không chép mã; bằng chứng là
test của plan (chạy qua `tests/chan_host/chay.sh -q`) hoặc kịch bản cổng trong sổ tay chạy thật.
```

**Cho lát sau (TM-3, TC):** `tram/giao_viec/tick_cot_3.py` (TM-2 Task 6) chỉ thêm import `feature_da_merge` và một dòng `merge = …` trước lần xét lại; TC/TM-3 sửa file này thì giữ dòng đó. `tram/giao_viec/tu_merge*.py`, `tram/suy/tu_merge.py` là file riêng của TM-2.

## Thứ tự code đề xuất và file giao nhau

1. Đại ca duyệt plan TM-2 (kill list mục 5, 7) → review Codex vòng 2 → sau khi **TM-1 vòng 2** ghép `main`: code Task 1 → 7 trên một nhánh → QC → ghép, rồi mới tới TM-3.
2. **File giao nhau với lát sau:** `tram/suy/tu_dong.py`, `tram/api/tuyen_tu_dong.py` (TM-3 thêm khoá / tuyến — mục "Ghép trên lát trước" ghi bản hợp nhất và số dòng còn lại); `docs/MODULES.md`, `openspec/changes/tu-merge-tu-deploy/tasks.md` (TM-3/TM-4 nối thêm vào cùng đoạn — ghép tay, giữ cả hai); `tram/giao_viec/tick_cot_3.py` (TC chỉ đọc). `tests/gh_gia.py`, `tram/giao_viec/tick_github.py` chỉ TM-2 sửa. Không chạm `tests/du_lieu_giao_dien.py`, `frontend/`. TM-4 dựng dữ liệu giả cho `cho_dai_ca` theo mục "Interfaces cho lát sau" (thêm hai mã `file_lenh`, `file_lenh_loi` mục `loi`).

## Đề nghị đổi hợp đồng TM-1

Không có. Dùng đúng hợp đồng D89 mới của TM-1 vòng 2. Ghi chú nhỏ, không cần đổi: `tu_merge.bat_dau` mang thêm khoá `lan` (số lần gửi) — hợp đồng TM-1 chỉ liệt kê khoá bắt buộc, `nguon_tu_dong` không đọc sự kiện này.

## Câu hỏi cho Đại ca

Không còn câu hỏi. Bốn câu của vòng 1 Đại ca đã trả lời đúng đề xuất (D119–D122, mục "Ghi chú triển khai"); câu 5 (lỗi việc con của tính năng lớn) Đại ca đã giao đưa vào lát này (Task 6).

## Ghi chú triển khai

**Quyết định của Đại ca cho Câu hỏi 1–4 vòng 1 (18/10/2026, `docs/quyet-dinh/2026-10-18-tu-merge-tu-deploy.md`) — đều đúng đề xuất, mã đã khớp, không đổi gì:**
- **D119** — đã gửi merge, chưa rõ kết quả, vòng sau PR còn mở mà điều kiện không còn đủ → **chờ, ghi lý do**, không báo lỗi. Mã: `gui_merge` gọi `ly_do(pr)` trước bộ đếm 3 lần; khác rỗng → `ghi_cho`, return None (`test_doc_lai_ngay_truoc_lenh_merge`, `test_tam_dung_roi_tiep_tuc`).
- **D120** — cờ đỏ gitnexus (kể cả "gitnexus lỗi") **tính là chạm hàng rào**. Mã: `cham_rao` → `hang_rao_co_do` khi nhãn `co-do` hoặc `co_do` của bằng chứng cột 3 mà không khớp loại nào.
- **D121** — spike không có QC **không tự merge**. Mã: `kiem_lai_qc` dựng bằng chứng có QC (`la_spike=False`); spike không có → `qc`.
- **D122** — vòng tự merge **không xét kênh ghi `header`**. Mã: `tram/giao_viec/tu_merge*.py` không đọc `cach_ly.kenh_ghi`.

**Phạm vi Đại ca giao ở vòng 2:** đưa sửa lỗi có sẵn `tick_cot_3.py` vào lát (Task 6), bead `bs-2bd.1.28` đóng bằng lát này sau khi Task 6 xanh trên `main`.

(Ghi khi code: chỗ lệch plan, số đo thật.)

## Phản hồi review Codex vòng 1

| Mã | Nội dung (với TM-2) | Sửa ở đâu | Test — đỏ thật trên mã cũ |
| --- | --- | --- | --- |
| Sửa trực tiếp #2 | Lần gửi merge thứ ba lỗi kết luận `gh-loi-3-lan` ngay dù GitHub có thể đã merge | Codex sửa `gui_merge` (Task 3) — Em áp và chạy thật, giữ nguyên | `test_lan_ba_mat_phan_hoi_van_doi_soat_thanh_cong` (`KeyError: 'loi_gh'` trên mã cũ), `test_con_mo_thi_gui_lai_cung_commit_ba_lan_roi_loi` (`[1, 1, None] == [1, 1, 1]`) |
| **Q2** (Quan trọng) | Cửa merge không tái kiểm D89 bằng cài đặt hiện hành; dấu QC cũ đủ để merge sau khi Đại ca đổi lệnh | `tu_merge_rao.cham_file_lenh` + `loai_trong_repo` (Task 3), gọi trong `ly_do(pr)` sau `gh pr view` của `xet_tu_merge` (Task 3) và `tu_merge_spec` (Task 4); mã lý do `file_lenh`, `file_lenh_loi` (Task 2) | `test_doi_lenh_trong_luc_doc_pr_thi_cho_file_lenh` (5 ca — đổi lệnh TRONG lúc đọc PR; mã cũ merge: 5/5 đỏ), `test_pr_spec_sua_file_lenh_thi_cho` (mã cũ merge: đỏ), `test_loai_trong_repo_theo_cay_git`, `test_cham_file_lenh`; bổ sung `test_doi_lenh_trong_luc_doc_cay_git_thi_cho` (1 đỏ → xanh), `test_lenh_qua_symlink_khong_mien_dich_cua_link` (2 ca đỏ → xanh) |
| **C2** (Chặn, phần TM-2) | Ngoại lệ `cho_phep` vô hiệu hoá cấm file lệnh | Cửa merge không đọc `duong_dan_cam_cho_phep`; `file_lenh` không theo nút | Cùng test Q2: dự án miễn đúng `scripts/deploy.sh` ở `duong_dan_cam_cho_phep` vẫn chờ. Phần kiểm lại/QC/thợ là của TM-3 |
| **Q3** (Quan trọng) | `tick_cot_3.py:43` thiếu `spec_da_merge` → con của feature `theo-plan` không vào cột 3; test cũ dùng hàm thuần | Task 6 (mới): `vao_cot_3_an_toan` tính `feature_da_merge` cho cha của bản vừa đọc | `test_con_feature_spec_da_merge_vao_cot_3_roi_tu_merge` (đi tới merge + đóng bead; mã cũ `(None, None) == (1, 1)`), đối chứng `test_con_feature_spec_chua_merge_thi_chua_vao_cot_3` |
| **Q15** (Quan trọng, phần TM-2) | Router chung vượt 120 dòng khi ghép cơ học | Logic đọc tiêu đề chuyển sang `tram/suy/tu_merge.py` (`tieu_de_bead`); router +2 dòng (102 → 104), `suy/tu_dong.py` +2 (29 → 31) | `test_suy_tu_merge.py`, `test_api_tu_dong.py`, `test_do_dai_ma.py` xanh; mục "Ghép trên lát trước" |
| Q1 (TM-1) | Token tuyệt đối bị bỏ | TM-1 vòng 2 đổi hợp đồng; TM-2 dựng callback đúng hợp đồng | `test_loai_trong_repo_theo_cay_git` (`/r/…`, `{kho kiểm}/…/../…`), ca `/r/scripts/deploy.sh` của test Q2 |

Các sửa mã cho lỗi Chặn/Quan trọng của TM-2 đã có test hồi quy; **chưa đánh dấu ĐẠT toàn lát khi cổng cả bộ còn bị sandbox chặn**. Các mục của lát khác (C1, Q4–Q14) không thuộc TM-2.

## Bổ sung của reviewer gộp vòng 2

Chỉ đối chiếu tĩnh, không chạy mã/test. Thêm gốc `tram_home()/kho-deploy/<dự án>` vào `cham_file_lenh` và test
`test_lenh_tuyet_doi_trong_worktree_deploy_van_cam_merge` (Task 3): đổi lệnh sau QC, trong lúc đọc PR, sang file ở
gốc deploy vẫn phải chặn. Thêm hai file `tu_merge_rao.py`/`test_tu_merge_rao.py` vào danh sách commit Task 3.
Các số RED/GREEN phía trên là bằng chứng tác giả của bản trước bổ sung này, không bao gồm test mới.

**Kết luận lịch sử của reviewer vòng 2 (đã xử lý ở mục phản hồi vòng 2 bên dưới):** `xet_tu_merge` còn dùng bead/dấu QC/kiểm lại lấy trước các lần đọc Git/GitHub có thể chậm. Nếu đổi
tiêu chí hoặc khoá cột trong lúc đọc PR, callback chỉ đọc tươi công tắc, chưa tính lại bằng chứng của bead.
Chi tiết và yêu cầu test hồi quy ở `REVIEW-CODEX-tm-vong2.md` (V2-C1); không coi sửa đường dẫn là đóng lỗi này.


## Phản hồi review Codex vòng 2

Phạm vi Đại ca giao: chỉ sửa **V2-C1**; giữ V2-Q4/V2-N2 mà reviewer đã sửa. Không xử lý lỗi của TM-3/TC.
Nguồn đối chiếu: đọc hết báo cáo vòng 2; TM-0, hợp đồng TM-1/3/4 và đoạn hợp nhất TC trong
`/Users/dai-ca/Developer/Ben Station/.worktrees/review-tm2/docs/plans/`; mã TM-1 đọc bằng
`git show 85ce7f4:<file>`. Không đổi hợp đồng TM-1, sự kiện merge hay dạng `cho_dai_ca`.

| Mã | Sửa ở đâu | Test và kết quả thật |
| --- | --- | --- |
| **V2-C1** | Task 3: `xet_tu_merge` nhận `bd` từ `buoc_github`; `doc_hien_hanh` đọc trực tiếp Beads rồi SQLite sau `gh pr view`/D89; kiểm seal, PR và tính lại QC/kiểm lại/hàng rào bằng bản mới. Task 4: `tu_merge_spec` nhận cùng nguồn, so feature, trạng thái, nội dung/nhãn, bản duyệt và PR mới nhất. Task 2 thêm nhãn lý do cố định; fixture spec dùng `BdGia` thay `None`. | `tests/test_tu_merge_tuoi.py`: **32 failed → 32 passed** trong bộ tập trung 153 xanh. Mỗi đột biến xảy ra ở cả `khi_xem` và `_cay`; không có `merge_pr` hay `tu_merge.bat_dau`, có `tu_merge.cho`. |
| V2-Q4 (đã sửa trước phiên) | Giữ gốc `tram_home()/kho-deploy/<dự án>` trong Task 3. | `test_lenh_tuyet_doi_trong_worktree_deploy_van_cam_merge` chạy xanh trong bộ 153. Không nhận đây là lỗi mới đã sửa ở phiên này. |
| V2-N2 (đã sửa trước phiên) | Giữ danh sách stage Task 3 đủ `tu_merge_rao.py` và test; thêm helper mới vào hướng dẫn. | Kiểm tĩnh danh sách file; phiên này không stage/commit. |

**Hợp đồng cửa cuối:** `bd` là nguồn trực tiếp có `tat_ca()`, không phải snapshot/bộ đệm. Lỗi đọc hoặc bead
biến mất → chờ `du_lieu_loi`; seal hết hiệu lực/đổi → `kiem_lai`; PR mới khác → `pr_khac`. Seal giữ nguyên
nhưng sự kiện QC/kiểm lại đổi thì tính lại bằng `kiem_lai_qc`. Hàng rào dùng bead mới, vì nội dung có thể
đổi mà SHA không đổi. Nhãn `cot-khoa` vẫn theo `dk_cot` đúng D90. Với spec, `digest_bead` trong `spec.duyet`
là digest kế hoạch, không đem so với digest nội dung feature; so bản duyệt hiện hành và dấu nội dung bead
ở đầu/cuối lần xét. Không đọc Beads trong giao dịch SQLite. Sau nguồn đọc cuối mới chốt lại công tắc/estop/`bat_ghi`.

**TDD thực thi (18/10/2026):**

- Nền TM-1 `85ce7f4` + TM-2 trước sửa: `test_tu_merge.py` + `test_tu_merge_spec.py` → **37 passed in 24.69s**.
- Test hồi quy ban đầu: **24 failed in 15.42s**, đúng lỗi gọi merge sau dữ kiện đổi.
  Bổ sung kiểm lại và cả đường đọc cây Git cho spec → trả riêng cửa xét về mã cũ
  (giữ chữ ký `bd` mới để không tạo lỗi TypeError giả): **32 failed in 21.01s**.
  Thông báo đỏ thật: `assert da_doi and merge_goi(gh) == []`, thực tế có
  `('merge_pr', REPO, 1, <SHA PR>)`. SHA PR không đổi trong các phản ví dụ.
- Ca code (20): tiêu chí, khoá cột, seal `cot.tra_ve`, QC không đạt, kiểm lại không đạt,
  nội dung chạm schema, PR hiện hành đổi, bead đóng, mất bead, lỗi Beads; mỗi ca ở hai điểm chậm.
  Ca spec (12): tiêu chí, nhãn khoá, bản duyệt, PR, trạng thái đóng, lỗi đọc; mỗi ca ở hai điểm chậm.
- Lượt xanh đầu có **67 passed, 1 failed**: dòng caller spec dài hơn 120 ký tự; đã xuống dòng lời gọi,
  không nới test. Bộ tập trung sau sửa: **153 passed in 48.97s**.
- Dựng lại từ plan: áp 26 khối mã/bản vá Task 1–7, mỗi diff qua `git apply --check`; so với mã đã kiểm:
  **0 file khác biệt**. Chạy lại trên cây dựng từ plan: **153 passed in 46.49s**.
  `--collect-only`: **3543 tests collected in 4.57s**, không gọi đây là 3543 passed.
  Mọi lượt đỏ/xanh/cả bộ trong phiên: **0 dòng chặn mới, 0 điểm mù, không push thật**.
  Không chạy các khối commit trong plan.

Lệnh bộ tập trung (thêm `UV_CACHE_DIR=/tmp/tm2-v3/uv-cache`; runner tự đặt `UV_OFFLINE=1`):

```bash
tests/chan_host/chay.sh -q tests/test_gh.py tests/test_gh_tu_merge.py tests/test_tu_merge_xet.py tests/test_tu_merge.py tests/test_tu_merge_rao.py tests/test_tu_merge_spec.py tests/test_tu_merge_tuoi.py tests/test_tu_merge_con_feature.py tests/test_suy_tu_merge.py tests/test_api_tu_dong.py tests/test_do_dai_ma.py tests/test_vong_import.py
```

**Cổng cả bộ còn bị sandbox chặn:** `tests/chan_host/chay.sh -q -x` → **1 failed, 139 passed in 20.93s**,
dừng tại `tests/test_ban_chep.py::test_ban_chep_dung_commit_co_repo_git_khong_bi_export_ignore_giau`:
`LoiBanChep: lệnh dưới tram-kiem: không xác nhận thu hồi cây tiến trình — không công nhận`.
Đọc trực tiếp `tram.kiem.bang_tien_trinh.chup_nhan()` xác nhận:
`PermissionError: [Errno 1] sysctl: không đọc được kích thước bảng`.
Đây là test thu hồi tiến trình của nền, không phải test V2-C1; người điều phối cần chạy lại cả bộ ngoài sandbox.
Không suy từ lượt dừng sớm rằng các test còn lại đã xanh; không thay runner/thu hồi/an toàn để né sandbox.
Không có ca bind localhost được chạy tới trong lượt `-x` này; không gán lỗi cho ca chưa chạy.

**Kiểm kiến trúc:** helper đọc nguồn nằm trong `giao_viec`, không bảng DB/dependency mới, không vòng import;
`tu_merge.py` 102 dòng, `tu_merge_tuoi.py` 22, `tick_github.py` 40. Không đổi file của TM-1/3/4/TC.
Cửa sổ từ lần đọc cuối tới gửi merge vẫn không có giao dịch xuyên Beads/SQLite/GitHub; `--match-head-commit`
chỉ bảo vệ SHA. Phiên này chứng minh các đột biến trong thao tác đọc chậm đã bị chặn, không chứng nhận cổng OS.

**Cây bàn giao:** hoàn nguyên mã/test/nền TM-1 và Task 7 về HEAD; chỉ còn plan này và
`KET-QUA-CODEX.md`. Không stage, không commit, không ghi Beads, không chạy cổng thật.
