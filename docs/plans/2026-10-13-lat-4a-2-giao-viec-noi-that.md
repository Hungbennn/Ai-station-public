# Lát 4a-2 — Bộ giao việc nối vào trạm chạy thật — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use ai-skills:subagent-driven-development (recommended) or ai-skills:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Nối bộ giao việc 4a-1 (`BoGiaoViec.chon`/`con_hop_le`, `mot_vong_tick`) vào tram-api và máy trạm thật: router `/api/tho/nhip` cấp phiếu qua bộ giao việc, đọc lại Beads ngay trước cấp, bộ đệm beads, vòng tick hai pha ở hai luồng (G5 ≤ 3 phút dù kiểm lại dài), lệnh `tram giao tick|kho-kiem|kiem`, kho kiểm clone từ remote, kiểm lại dưới principal `tram-kiem`, phiên bản file quyền trong khoá chống trùng, kiểm ref công bố trên remote trước cột 3, dashboard hiện lý do không giao + lệnh/link tạo PR — tất cả **tắt mặc định** (`giao_viec.bat: false`) tới khi qua cổng.

**Architecture:** Không đổi mô hình của 4a-1 (trạng thái suy từ sự kiện, ghi idempotent theo ID nguồn). Thêm một lớp "nối thật" mỏng: `tram/giao_viec/noi_that.py` dựng `BoGiaoViec` thật (dự án từ `du-an/*.yaml`, `Bd` actor `tram/giao-viec`, kho phiếu thật, bộ đệm beads của tram-api, principal `tram-kiem` từ cấu hình) và, chỉ khi `giao_viec.bat`, gắn `chon_phieu`/`con_hop_le_phieu` vào `PhuThuocApi` + chạy hai luồng `tram-giao-nhanh` (escalation/câu hỏi/hết ngân sách — không Git) và `tram-giao-git` (fetch, xét `bao.xong`, kiểm lại, cột 3) trong `tram api`, mỗi pha một khoá `flock`. Mọi thứ cần từ 3a-2 (ChayCLI thật, push + `giao.cong_bo`, cách ly) đi qua sự kiện/Protocol 3a-1 đã chừa; mọi thao tác chạm hệ thống (clone GitHub, tạo `tram-kiem`) chỉ in kế hoạch + chờ `dong-y` hoặc để Đại ca làm sau S6/S7.

**Tech Stack:** Python 3.12 (`uv`), FastAPI 0.143.0 (đã có), SQLite stdlib (kho phiếu 3a-1), `git` CLI, `fcntl.flock` (stdlib), Vue 3.5.43 + Vite 8.3.4 (đã có). **Không thêm phụ thuộc nào.**

**Spec:** [docs/specs/2026-10-13-phan-4-giao-viec.md](../specs/2026-10-13-phan-4-giao-viec.md) (ĐÃ DUYỆT 13/10) — phần lát 4a còn lại sau 4a-1: §3 (4a "chạy được khi"), §5.1 "giới hạn nhất quán" (đọc lại trước cấp), §5.4 (claim có đối soát khi nối thật), §6.2 bước 1 + 4 (kho kiểm của trạm, principal `tram-kiem`), §6.4 mục 4 (lệnh/link PR trên dashboard), §6.7 (ref công bố), §9 (`nhanh-bi-day`), §10 (tick 2 phút trong tram-api, `tram giao tick`, "ràng buộc lúc nối 4a-2"), §13 (nối `chon`/`con_hop_le`), §16 mục 3 (phần nối), mục 4 (chạy thật — chỉ viết thành task chờ cổng). Đọc kèm: plan 4a-1 (`docs/plans/2026-10-13-lat-4a-1-giao-viec.md` — mục "Để sau", G1–G31), plan 3a-1 (`docs/plans/2026-10-13-lat-3a-1-may-tho.md` — G11, G31, Task 22–24, "Để 3a-2"), spec 3 [§6.4, §7.2, §7.3, §11](../specs/2026-10-13-phan-3-may-tho-han-muc.md), spec 2 [§4, §12.5](../specs/2026-10-12-phan-2-dashboard.md), [quyết định 13/10](../quyet-dinh/2026-10-13-tra-loi-cau-hoi-gop.md) (#2, #3, #4, #5), [phản hồi review Codex đợt 1+2](../handovers/2026-10-13-phan-hoi-review-codex-dot12.md) (4a-1 G3 chấp nhận rủi ro snapshot — "4a-2 đọc lại Beads ngay trước cấp").

**Không làm:** 4b (feature, `spec`, phiếu yêu cầu, Duyệt/Trả về spec, `POST /api/phieu/kiem`), 4c (PR tự động, gitnexus, lớp 5 memory); chạy CLI thật, push/công bố ref (3a-2 — chỉ đọc `giao.cong_bo`); tạo user `tram-kiem`, sửa sudoers/ACL (S6); đăng nhập `gh`/credential GitHub của trạm (S7, #2); chạy thử repo nháp 3 bug (#4 — Task 14, **chờ cổng**, không phải task code); bật `giao_viec.bat` trên máy thật.

> **Trạng thái:** đã review tĩnh14/10. Bản gốc từng chạy trên bản sao; mã mẫu sửa trong lần review này CHƯA chạy. Giữ TDD và cổng thật khi triển khai.

## Global Constraints

- **Điều kiện tiên quyết:** `main` đã ghép xong **3a-1 → 1b-3 → 2b → 4a-1 → 1b-2 → 3a-2** (thứ tự code đã chốt). Gọi **N₀** = số test `uv run pytest -q` trên `main` lúc đó (đo trước Task 1). Bản sao Em chạy thử không có 1b-2 và 3a-2: **1361 passed** trước plan này, **1425** sau (+64). Test cũ luôn xanh; plan **không sửa** test cũ nào.
- **TDD:** mỗi task viết test trước, chạy thấy fail (thông báo Step 2 là kết quả chạy thật trên bản sao), viết mã, chạy thấy pass. Ngoại lệ: Task 13 (chỉ test tích hợp), Task 14 (chạy thật — chờ cổng, không phải task code). **Mỗi file nguồn ≤ ~120 dòng** (cả `.vue`; dài nhất: `tests/test_luong_giao.py` 117, `tram/giao_viec/bo.py` 106). Định danh tiếng Việt không dấu. Giờ UTC `YYYY-MM-DDTHH:MM:SSZ`; hàm nghiệp vụ nhận `dong_ho`/`luc` tiêm được.
- **Mỗi task một worktree, một nhánh, một commit**, tạo từ `main` **sau khi đã ghép đợt trước** ("Chuẩn bị", "Sơ đồ đợt chạy"). Task cùng đợt không sửa chung file. Không push, không merge (người điều phối ghép).
- **Không thêm phụ thuộc mới** (`fcntl` là stdlib; frontend không thêm gói).
- **Test không:** gọi Claude/Codex/Ollama thật; gọi mạng (remote Git là repo bare cục bộ; URL GitHub chỉ là chuỗi); đụng Keychain; đụng `~/.tram` thật (`TRAM_HOME` tạm — `tests/conftest.py`); chạy `sudo`, tạo user, sửa sudoers/ACL (principal `tram-kiem` giả bằng `boc`/`trao_quyen`/`chay` tiêm); chạy launchd; `git push` ra ngoài; chạy `bd` trên repo thật (`BdGia`; test CLI đặt `TRAM_REPO` tạm và vá `cac_du_an_that`); đọc file đăng nhập CLI. Luồng nền trong test luôn được `dung.set()` + `join`.
- **Bản giả chỉ ở `tests/`**, ghi "CHỈ DÙNG TRONG TEST"; mã `tram/` không import chúng. **Không đánh dấu 4a sẵn sàng triển khai bằng fixture giả:** `giao_viec.bat` mặc định `false`; `tram giao kiem` báo ĐỎ mọi mục chưa chứng minh trên máy thật.
- **Trạm là bên duy nhất ghi beads** (Q11) — qua `Bd(..., actor="tram/giao-viec")`; không bao giờ gắn `cot:ai-lam`/`cot:can-chot`.
- **Mã repo không bao giờ chạy dưới quyền tram-api** (G4 spec 4): `giao_viec.bat: true` bắt buộc có `principal_kiem`; thiếu `boc` → kiểm lại không chạy lệnh (`cho_boc`).
- **Không gọi `bd`/Git/HTTP khi giữ khoá SQLite** (3a-1 G11): đọc lại Beads trong `chon` (ngoài giao dịch), `con_hop_le` chỉ đọc kho.
- **Thao tác chạm hệ thống/mạng** (clone kho kiểm từ GitHub) chỉ in kế hoạch + chờ `dong-y` (khuôn `tram chu cai-dat`); tạo `tram-kiem`, sudoers, ACL, đăng nhập `gh` **không** nằm trong plan (S6, S7 — Đại ca làm/duyệt riêng).
- **Frontend** theo quy ước bảo mật 2a: CSP chặt (không đổi), không `v-html`/`:innerHTML`, chỉ đọc (không thao tác ghi mới — không cần `ma_thao_tac`), link ra ngoài chỉ qua `laLinkAnToan` (`https://github.com/…`); `npm run kiem` + `npm run build` xanh.
- Lệnh test: `uv run pytest -q` từ thư mục worktree của task; frontend: `cd frontend && npm run kiem && npm run build`.

## Phụ thuộc đã có (main + plan trước — plan này dùng, không sửa trừ chỗ ghi rõ)

| Thứ dùng | Ở đâu | Từ | Plan dùng ở |
|---|---|---|---|
| `BoGiaoViec(cac_du_an, tao_bd, mo_kho, ch, dong_ho, kho_git=kho_kiem_co_san, boc=None, env_goc)` + `.chon`, `.con_hop_le`, `._da_nhan`; `kho_kiem_co_san` (**sửa** `bo.py` — Task 4) | `tram/giao_viec/bo.py` | 4a-1 Task 18 | 3, 4, 7, 9, 13 |
| `mot_vong_tick(bo)` (**sửa** — Task 7), `ghi_escalation_dong`, `ghi_bead_dong`, `mo_chu_ky_con_thieu`; `day_pipeline` (**sửa** — Task 7) | `tram/giao_viec/tick.py`, `tick_doc.py`, `tick_pipeline.py` | 4a-1 Task 19 | 7, 8 |
| `kiem_lai(…, boc, env_goc, thoi_gian_cho)` (**sửa** — Task 5), `KetQuaKiemLai` | `tram/giao_viec/kiem_lai.py` | 4a-1 Task 14 | 5, 7 |
| `kho_kiem`, `fetch` (**sửa** — Task 3), `sha_cua`, `GIT`, `tao_worktree`, `xoa_worktree` | `tram/giao_viec/git_kiem.py` | 4a-1 Task 5 | 3, 7, 11 |
| `dung_de_xuat`, `PHIEN_BAN_QUYEN` (**sửa/bỏ** — Task 2) | `tram/giao_viec/de_xuat.py` | 4a-1 Task 17 | 2 |
| `ly_do_khong_giao`, `ASSIGNEE`, `NHAN_COT_1`; `buoc_ke_tiep`; `trang_thai_bead`, `viec_ton_cua`; `vao_cot_3`; `tao_escalation`, `LY_DO_BI` (ánh xạ `nhanh-bi-day-ngoai-luong` → `nhanh-bi-day`); `bat_dau_chu_ky`; `su_kien_bead`, `moi_nhat`; `lenh_bat_buoc`; `xu_ly_cong_viec`, `escalation_cau_hoi` | `tram/giao_viec/*` | 4a-1 | 4, 7, 11 |
| `bi_chan_boi` | `tram/cham_cot/luat_cung.py` | 1a | 4 |
| `BoDemBeads(tao_bd, *, tuoi_toi_da)` + `.lay`, `.phien_ban`, `.danh_dau_cu` | `tram/api/bo_dem.py` | 2a | 4, 9, 11 |
| `PhuThuocApi` (`chon_phieu`, `bo_dem`, `cau_hinh`, `mo_kho`, `mo_kho_phieu`, `cac_du_an`) (**sửa** — Task 9, chèn theo mốc); `phu_thuoc_that`; `kiem_du_an_bead` | `tram/api/phu_thuoc.py` | 2a, 3a-1 T23, 1b-3 T9, 2b T11 | 9, 11 |
| Router `/api/tho/nhip` (**sửa** — Task 9, chèn theo mốc); `CAC_TUYEN`, `tao_app` (**sửa** `app.py` — Task 11, chèn theo mốc) | `tram/api/tho.py`, `tram/api/app.py` | 3a-1 T23, 1b-3, 2b | 9, 11 |
| `xu_ly_nhip(…, chon, con_hop_le)`, `cap_phieu(…, con_hop_le)` | `tram/phieu/nhip.py`, `cap.py` | 3a-1 T17, T22 | 9, 13 |
| `ThanBao`, `LY_DO_BI` (**sửa có điều kiện** — Task 6), `nhan_bao` | `tram/phieu/bao.py` | 3a-1 T18 (+ 3a-2?) | 6 |
| `chay_mot_lenh(…, boc, cho_kill)`, `moi_truong_kiem`, `KetQuaLenh` | `tram/kiem/chay_lenh.py` | 3a-1 T8 | 10 |
| `KhoPhieu`, `mo_kho_phieu` | `tram/phieu/kho.py` | 3a-1 T13 | 9, 13 |
| `MucKiem`, `in_ket_qua` | `tram/tho/kiem_may.py` | 3a-1 T24 | 10 |
| `_api` (bộ canh trong `tram api`), `them_lenh` (**sửa** — Task 9, 10, chèn theo mốc) | `tram/cli_dich_vu.py` | 2a, 3a-1 T6/T24, 1b-2 T3 | 9, 10 |
| `nap_du_an(ten, *, thu_muc)`, `liet_ke_du_an`, `DuAn` (`.giao`, `.moi_truong_kiem`, `.nhanh_chinh`, `.lenh_cho_phep`) | `tram/cau_hinh/du_an.py`, `du_an_giao.py` | 3a-1 T10, 4a-1 T2 | 9, 10, 11 |
| `KhoSuKien.moi_nhat(du_an, bead_id, loai)`, `.ghi` | `tram/su_kien/kho.py` | 0 | 11 |
| Dashboard: `CongViec.vue`, `TheBead.vue`, `NganBen.vue` (**sửa** — Task 12), `doc`, `laLinkAnToan`, lớp CSS `nhan-nho vang`, `canh-bao`, `van-ban` | `frontend/src/…` | 2a | 12 |
| Công cụ test: `giao_viec_gia.py` (`dung`, `bug`, `du_an_gia`, `TC`), `kho_kiem_gia.py`, `su_kien_gia.py`, `xu_ly_gia.py`, `test_tick.py` (`GIU`, `chuan_bi_code_xong`, `loai`), `test_xet_xong.py` (`F`, `bg`), `test_kich_ban_4a1.py` (`xin`, `bao`), `kho_phieu_gia.py`, `phieu_gia.py`, `tho_api_gia.py` (`tao_tram`), `api_gia.py` (`tao_pt`), `asgi_gia.py` (`goi`), `bd_gia.py`, `bead_gia.py`, `git_gia.py` | `tests/` | 2a, 3a-1, 4a-1 | test mọi task |

**Từ 3a-2 (cùng đợt 3, Em không đọc được bản plan):** chỉ dùng qua sự kiện/giao diện 3a-1 đã chừa — xem bảng G, các dòng "HỢP ĐỒNG MỚI (3a-2)". **Đụng chung file với plan khác:** `tram/api/phu_thuoc.py`, `tram/api/tho.py`, `tram/api/app.py`, `tram/cli_dich_vu.py` (3a-1, 1b-3, 2b, 1b-2 đã sửa; 3a-2 có thể sửa) → **chèn theo mốc** bằng script có `assert` đúng một mốc, không dùng bản vá; `tram/phieu/bao.py` (3a-2 có thể đã thêm giá trị) → chèn có điều kiện. File của 4a-1 (`bo.py`, `de_xuat.py`, `git_kiem.py`, `kiem_lai.py`, `tick.py`, `tick_pipeline.py`) và 2a (`CongViec.vue`, `TheBead.vue`, `NganBen.vue`) → bản vá `git apply` sinh từ bản sao `main` + plan trước (chưa có 3a-2): `git apply --check` lỗi → `git apply --3way`; vẫn lỗi (3a-2 đã sửa cùng chỗ) → **dừng, báo người điều phối**, không tự sửa tay.

## Câu hỏi / giả định

Chỗ spec để ngỏ — Em chọn phương án an toàn nhất, không tự mở rộng phạm vi. Cột "Loại": **HỢP ĐỒNG MỚI** = giao diện/dữ liệu phần khác dựa vào hoặc plan này dựa vào phần khác (3a-2 cùng đợt), Đại ca cần chốt; **lệch chữ spec** = làm khác câu chữ spec; **giả định** = chi tiết thực thi, Đại ca gạch nếu không đồng ý.

| # | Chỗ mơ hồ | Chọn | Vì sao | Loại |
|---|---|---|---|---|
| G1 | "Nối sau các cổng" (spec 4 §10, 4a-1 G1) mà code trước, chạy thật sau | Mọi thứ nối sẵn nhưng **tắt**: khoá `giao_viec.bat` (mặc định `false`) trong `~/.tram/cau-hinh.yaml`. Tắt → `chon_phieu` vẫn `None`, không luồng tick, `tram giao tick` chỉ cho `--thu`; `bo_giao` vẫn gắn để dashboard hiện lý do không giao. Bật chỉ sau Task 14 (chờ cổng) | Đại ca chốt "code xong hết rồi mới chạy thật"; một công tắc rõ ràng thay vì nhánh mã chưa ghép | giả định |
| G2 | Khoá cấu hình 4a-2 | `giao_viec: {bat, chu_ky_giay (30–150, mặc định 120), thu_muc_kiem, principal_kiem: {ten, boc: [argv], trao_quyen?: [argv]}}`, đọc riêng (không sửa `tram/cau_hinh/tram.py` — `nap_cau_hinh_tram` bỏ qua khoá lạ). `bat: true` mà thiếu `principal_kiem` → lỗi cấu hình | Spec 2 §12.5 gom con số vào `cau-hinh.yaml`; ≤ 150 giây giữ G5 ≤ 3 phút; G4 spec 4 | **HỢP ĐỒNG MỚI** (dạng khoá) |
| G3 | `giao.cong_bo` thật (3a-2) | 4a-2 **chỉ đọc**: 3a-2 ghi `giao.cong_bo {bead_id, luot, commit, ref}` (cột `du_an` = dự án, `bead_id` = bead) sau CAS lên ref công bố; `ref` = tên nhánh `tram/<bead>` (chấp nhận tiền tố `refs/heads/`); `commit` 40 hex đã có trên remote lúc ghi. Không có producer → mọi `bao.xong` kết luận `chua-cong-bo` (an toàn, tốn ngân sách) — `Chuẩn bị` kiểm có producer | Spec 3 §6.4, §11: công bố ref là phần 3; 4a-1 G15/"Để sau" | **HỢP ĐỒNG MỚI** (3a-2) |
| G4 | `bao.bi {ly_do: "nhanh-bi-day-ngoai-luong"}` (4a-1 G20) | 3a-2 thêm vào `LY_DO_BI` khi có push; Task 6 **chèn có điều kiện** (đã có thì không sửa) + test hợp đồng đầu-cuối (`nhan_bao` thật → escalation `nhanh-bi-day`) | Hai plan cùng đợt viết song song; idempotent thì thứ tự nào cũng đúng | **HỢP ĐỒNG MỚI** (3a-2) |
| G5 | `phien_ban_quyen` trong `khoa_chong_trung` (4a-1 G14) | Băm nội dung `vai/quyen/<vai>.json` của repo trạm (`sha256:` + 16 hex); chưa có file → `"0"` như 4a-1, `tram giao kiem` báo ĐỎ | Spec 3 §7.2 đặt file ở đây và "có phiên bản"; băm nội dung không phụ thuộc định dạng (chưa chốt tới S4) và đổi khoá với mọi thay đổi quyền | **HỢP ĐỒNG MỚI** (đường dẫn — 3a-2) + giả định |
| G6 | Chữ ký 3a-1 mà 3a-2 có thể chạm | Giả định 3a-2 giữ: `xu_ly_nhip(…, chon, con_hop_le)`, `cap_phieu(…, con_hop_le)`, `chay_mot_lenh(…, boc, cho_kill)`, `PhuThuocApi.chon_phieu`, dòng `chon=pt.chon_phieu))` (`tram/api/tho.py`), `_api` theo 3a-1 Task 24, `them_lenh_tho(sub, chu)`. Mốc không còn → script dừng | Không đọc được 3a-2 | **HỢP ĐỒNG MỚI** (3a-2) |
| G7 | Principal `tram-kiem` (S6) | **Adapter cấu hình**: `boc` = tiền tố argv chạy một lệnh dưới `tram-kiem`; `trao_quyen` = lệnh (tài khoản trạm) trao quyền ghi worktree kiểm, nhận thêm đối số thư mục, gọi SAU khi chép môi trường kiểm, TRƯỚC lệnh đầu; lỗi → ném (không ghi `kiem.lai`, vòng sau thử lại). Plan **không** tạo user/sudoers/ACL. `tram giao kiem` chạy thật 5 điều: danh tính = `ten` ≠ người chạy, lệnh thấy `APP_ENV=testing`, không đọc được `~/.tram/su-kien.db`, ghi được thư mục sau `trao_quyen` và trạm xoá lại được, timeout dừng được cả nhóm tiến trình | Spec 3 §7.3 mục 5: cơ chế chốt cùng S6; hình dạng chưa xác minh → cô lập trong adapter + bước kiểm thật | **HỢP ĐỒNG MỚI** (khoá) + chờ S6 |
| G8 | Thư mục worktree kiểm khi có principal | `thu_muc_kiem` bắt buộc, phải **ngoài** `~/.tram` (`tram-kiem` không được đọc kho trạm); không principal → `~/.tram/kiem` như 4a-1 | Spec 3 §7.3 mục 1, 5 | giả định |
| G9 | Đọc lại Beads ngay trước cấp (4a-1 G3 — Đại ca đã chấp nhận rủi ro còn lại) | Trong `chon`, với bead được chọn: đọc lại `bd list` (dạng đã spike), so **dấu nội dung** (tiêu đề, mô tả, tiêu chí, design, loại, nhãn, phụ thuộc, cha, ưu tiên — không `updated_at`, `notes`), trạng thái/người nhận, chạy lại §5.1 trên bản mới ("bị chặn" tính trên trạng thái mới của bead chặn). Bead `open`: đọc lại → `--claim` → đọc lại lần hai. Huỷ sau claim → bead ở lại `in_progress` của trạm (spec 4 §5.4), lần sau xét như "bước sau". Rủi ro còn lại: thay đổi trong khe từ lần đọc cuối tới `COMMIT` cấp phiếu (vài mili-giây, không giao dịch xuyên Beads/SQLite) | Spec 4 §5.1 "4a-2 đọc lại Beads ngay trước cấp, huỷ khi version/nội dung đổi" | giả định |
| G10 | Bộ đệm beads (4a-1 rủi ro c) | Bộ chọn dùng `BoDemBeads` của tram-api (chung với dashboard, tuổi 30 s) + đệm `bd ready` cùng tuổi, hết hạn khi danh sách đổi phiên bản; sau claim đánh dấu cũ. Vòng tick **không** dùng bộ đệm (đọc mới mỗi vòng) | Snapshot cũ ≤ 30 s an toàn nhờ G9 | giả định |
| G11 | "Xử lý escalation/câu hỏi phải tiếp tục trong khi suite kiểm lại dài đang chạy" (spec 4 §10) | Hai pha, hai luồng trong `tram api`: **nhanh** (`escalation.dong`, `bead.dong`, chu kỳ, công việc chờ KHÔNG phải `xong`, câu hỏi agent, hết ngân sách — không Git, không lệnh) và **Git** (fetch có hạn 120 s, công việc `xong`, kiểm lại, cột 3, thiếu môi trường kiểm). Lịch nhịp cố định theo lúc BẮT ĐẦU vòng; mỗi pha một khoá `flock` (`~/.tram/khoa/giao-{nhanh,git}.lock`) dùng chung với `tram giao tick` chạy tay. G5 ≤ `chu_ky` + một vòng nhanh (120 s + vài giây) | Một luồng duy nhất sẽ để suite 15 phút chặn escalation; mỗi loại escalation chỉ do một pha tạo → không đua tạo trùng | giả định |
| G12 | Kiểm lại nhiều bead | Tuần tự trong pha Git (không song song); bead khác chờ tới ≤ 15 phút × số bead đang chờ kiểm lại | Thông lượng, không phải G5; giữ một principal, một worktree mỗi lúc | giả định |
| G13 | Trước cột 3 khi chạy thật | Đọc lại bead + sự kiện ngay trước ghi nhãn; so ref công bố **trên remote** (kho kiểm vừa fetch) với `giao.cong_bo` mới nhất — khác → không vào cột 3, escalation `nhanh-bi-day` (một lần mỗi (chu kỳ ngân sách, SHA remote)) | G10 spec 4: PR Đại ca tạo từ `tram/<bead>` phải trỏ đúng commit đã kiểm. Không SUY bằng chứng từ remote — chỉ chặn khi remote lệch (fail-closed) | lệch chữ spec (thêm một cổng) |
| G14 | Kho kiểm (4a-1 G15, "Để sau") | `tram giao kho-kiem <du_an> [--dong-y]`: remote = `remote.origin.url` của repo dự án (chỉ đọc), chỉ nhận GitHub https/ssh hoặc thư mục cục bộ (repo nháp); clone `--no-checkout`, hook tắt, `GIT_TERMINAL_PROMPT=0`; kho có sẵn trỏ remote khác → lỗi, **không tự xoá**; có sẵn đúng remote → fetch. Không thêm khoá yaml `remote` | #2 GitHub; không fetch vào repo làm việc của Đại ca; clone là thao tác mạng → kế hoạch + `dong-y` | giả định |
| G15 | `tram giao tick [--thu]` | Chạy pha nhanh rồi pha Git qua cùng khoá; `--thu` = pha nhanh ở chế độ estop (chỉ ghi sự kiện suy từ beads); `bat: false` → chỉ cho `--thu` (tránh tạo escalation `thieu-moi-truong-kiem` khi bộ giao việc chưa bật) | 4a-1 "Để sau" | giả định |
| G16 | Dashboard (spec 4 §5.1, §6.4 mục 4) | Endpoint riêng `GET /api/giao-viec?du_an=` (không sửa `/api/cong-viec`): `{bat, giao: {"<du_an>/<id>": {khong_giao: văn bản | null, pr: {nhanh, commit, tu_xa, lech, link, lenh} | null}}}`. Lý do chỉ cho bead mang `cot:ai-lam` đang mở (bỏ "bị chặn" — thẻ đã hiện "chờ …"), không gọi `bd ready`/fetch. PR: link GitHub `compare/<nhanh_chinh>...tram/<bead>?expand=1` + lệnh `gh pr create [--repo o/r] --base … --head tram/<bead> --fill` (không chèn tiêu đề bead vào lệnh), cảnh báo khi nhánh remote lệch `commit_ban_giao`. Thẻ hiện nhãn "chưa giao", ngăn bên hiện mục "Bộ giao việc" | Chỉ đọc; chuỗi dựng từ hằng số, id đã kiểm dạng, SHA hex | **HỢP ĐỒNG MỚI** (JSON — 2c có thể dùng) |
| G17 | Trường mới của `PhuThuocApi` | `con_hop_le_phieu: Callable = lambda d: True`, `bo_giao: object | None = None` | Router truyền `con_hop_le` (3a-1 Task 23 mới truyền `chon`) | **HỢP ĐỒNG MỚI** |
| G18 | Lỗi của phần 4 trong nhịp tim | `chon`/`con_hop_le` bọc an toàn trong tram-api: lỗi → không phát phiếu (ghi stderr), không HTTP 500 | Nhịp tim còn gia hạn phiếu khác; 500 làm thợ lặp lỗi | giả định |
| G19 | Restart tram-api giữa kiểm lại | Lệnh kiểm mồ côi dưới `tram-kiem` chạy tới hết (≤ 15 phút); vòng sau kiểm lại lại từ đầu (không `kiem.lai` dở); worktree cũ cùng đường dẫn chưa xoá được → lỗi dự án, vòng sau thử lại | Trạng thái suy từ sự kiện; không có giao dịch xuyên tiến trình | giả định (rủi ro) |
| G20 | Dừng lệnh quá hạn của `tram-kiem` | `chay_mot_lenh` sau 3a-2 nhận `kill(pgid, sig)`. Task 1/4/5/7/9/10 truyền `PrincipalKiem.kill_nhom` xuyên bộ giao và readiness; mặc định `_kill_nhom` (os.killpg bỏ qua nhóm đã thoát) chỉ cho fixture cùng user. Mục "dừng được lệnh quá hạn" của `tram giao kiem` phải XANH trước khi bật | Cơ chế chốt cùng S6 | chờ S6 (rủi ro) |
| G21 | Chạy thử repo nháp 3 bug (#4, G8 spec 4) | Task 14: danh sách bước chạy thật + kết quả mong đợi, **chờ cổng**, không phải task code | Quy ước đợt 3 | giả định |

## File Structure

```
tram/
  giao_viec/principal_kiem.py   # PrincipalKiem: boc_lenh, trao — adapter `tram-kiem` (chờ S6)              — Task 1
  cau_hinh/giao_viec.py         # CauHinhGiaoViec, nap_cau_hinh_giao_viec (khoá `giao_viec:`)              — Task 1
  giao_viec/quyen.py            # phien_ban_quyen (băm vai/quyen/<vai>.json)                              — Task 2
  giao_viec/de_xuat.py          # (sửa) khoá chống trùng dùng phien_ban_quyen                             — Task 2
  giao_viec/kho_kiem_tao.py     # kế hoạch clone/cập nhật kho kiểm, url_origin, github_repo               — Task 3
  giao_viec/git_kiem.py         # (sửa) fetch có hạn giờ                                                  — Task 3
  giao_viec/doc_beads.py        # DocBeads: BoDemBeads + đệm `bd ready`                                   — Task 4
  giao_viec/doc_lai.py          # dau_bead, con_nguyen: đọc lại ngay trước cấp                           — Task 4
  giao_viec/bo.py               # (sửa) _chot, doc_beads, trao_quyen, thu_muc_kiem                        — Task 4
  giao_viec/kiem_lai.py         # (sửa) trao_quyen sau môi trường kiểm, trước lệnh                       — Task 5
  phieu/bao.py                  # (sửa có điều kiện) LY_DO_BI + nhanh-bi-day-ngoai-luong                  — Task 6
  giao_viec/tick.py             # (sửa) vong_nhanh, vong_git, mot_vong_tick hai pha                       — Task 7
  giao_viec/tick_pipeline.py    # (sửa) viec theo pha, principal + thư mục kiểm                           — Task 7
  giao_viec/tick_cot_3.py       # vao_cot_3_an_toan: ref remote = công bố, đọc lại bead                   — Task 7
  giao_viec/luong.py            # giu_khoa, chay_vong, lap, bat_dau_luong_giao                            — Task 8
  giao_viec/noi_that.py         # dung_bo_that, noi_giao_viec, an_toan                                    — Task 9
  api/phu_thuoc.py, api/tho.py, cli_dich_vu.py   # (chèn theo mốc) con_hop_le_phieu, bo_giao; nối `tram api` — Task 9
  giao_viec/kiem_san_sang.py    # tram giao kiem                                                          — Task 10
  giao_viec/lenh.py             # tram giao tick|kho-kiem|kiem                                            — Task 10
  cli_dich_vu.py                # (chèn theo mốc) đăng ký `tram giao`                                     — Task 10
  suy/giao_viec.py              # ly_do_hien, thong_tin_pr, suy_giao                                      — Task 11
  api/tuyen_giao.py, api/app.py # GET /api/giao-viec (app.py chèn theo mốc)                               — Task 11
frontend/src/
  giao_viec.js, thanh/OGiaoViec.vue   # (mới)                                                             — Task 12
  trang/CongViec.vue, thanh/TheBead.vue, trang/NganBen.vue   # (sửa)                                      — Task 12
frontend/tests/giao_viec.test.mjs                                                                         — Task 12
tests/
  test_cau_hinh_giao_viec.py (1) · test_quyen_giao.py (2) · test_kho_kiem_tao.py (3) · test_doc_lai.py (4)
  test_kiem_lai_principal.py (5) · test_nhanh_bi_day.py (6) · test_tick_hai_pha.py (7) · test_luong_giao.py (8)
  test_noi_giao_viec.py (9) · test_giao_kiem.py (10) · test_giao_viec_api.py (11) · test_kich_ban_4a2.py (13)
```

Đối chiếu spec 4 §13: không thêm module ngoài `tram/giao_viec/` trừ `cau_hinh/giao_viec.py` (khoá cấu hình), `suy/giao_viec.py` + `api/tuyen_giao.py` (dashboard — theo khuôn 2a: suy lúc đọc ở `tram/suy/`, router ở `tram/api/`).

Công cụ test là module cấp cao trong `tests/` (pytest chế độ `prepend`); test sau dùng lại hàm của test trước (`from test_tick_hai_pha import bi`, `from test_luong_giao import BdKhoa, cho_toi`) — task đó phải đã ghép.

## Chuẩn bị (người điều phối)

```bash
cd "/Users/dai-ca/Developer/Ben Station"
git status --short            # chỉ được có .beads/interactions.jsonl, .DS_Store — không đụng
git log --oneline -1          # main đã ghép 3a-1, 1b-3, 2b, 4a-1, 1b-2, 3a-2
uv run pytest -q              # ghi lại N₀ (bản sao chưa có 1b-2 Task 9 và 3a-2: 1457 passed)
```

**Kiểm hợp đồng với 3a-2 trước Task 1** (bảng G — G3, G4, G5, G6). Mục nào sai → dừng, báo Em/Đại ca; không tự sửa:

```bash
grep -c 'chon=pt.chon_phieu))' tram/api/tho.py                                     # 1
grep -c '^    chon_phieu: Callable | None = None' tram/api/phu_thuoc.py             # 1
grep -c 'chay_api(tao_app(phu_thuoc_that(), cong=args.cong)' tram/cli_dich_vu.py # 1
grep -c '^    them_lenh_tho(sub, chu)$' tram/cli_dich_vu.py                         # 1
uv run python -c "import inspect; from tram.phieu.nhip import xu_ly_nhip; from tram.kiem.chay_lenh import chay_mot_lenh; assert {'chon', 'con_hop_le'} <= set(inspect.signature(xu_ly_nhip).parameters); assert {'boc', 'cho_kill'} <= set(inspect.signature(chay_mot_lenh).parameters); print('ok')"
grep -rn '"giao.cong_bo"' tram/ | grep -v 'tram/giao_viec/'   # kỳ vọng: producer của 3a-2 (ghi khi công bố ref)
ls vai/quyen/ 2>/dev/null                                      # kỳ vọng: coder.json, qc.json (3a-2); chưa có → G5 dùng "0"
```

**Mỗi task một worktree**, tạo từ `main` **sau khi đã ghép mọi task của đợt trước**:

```bash
N=7   # số task
git worktree add .worktrees/4a2-t$N -b 4a2/t$N main
cd .worktrees/4a2-t$N && uv sync && uv run pytest -q    # kỳ vọng: số "sau đợt trước" trong Sơ đồ đợt chạy
```

Cuối mỗi task: người thực thi commit trong worktree của mình; người điều phối kiểm (mọi dòng thêm có nguyên văn trong plan; số test đúng kỳ vọng) rồi `git merge --no-ff 4a2/t$N` vào `main` (không push). Ghép xong cả đợt → `uv run pytest -q` trên `main` phải bằng số "sau đợt" trong bảng.

Mã: file **mới** cho nguyên văn đầy đủ; file **có sẵn** cho bản vá `git apply` (unified diff, chạy từ gốc worktree) hoặc **script chèn theo mốc** (file nhiều plan cùng sửa). Áp bản vá: lưu khối `diff` ra file rồi `git apply --check <file> && git apply <file>`; lỗi → `git apply --3way <file>`; vẫn lỗi → dừng, báo người điều phối. Script chèn theo mốc tự `assert` đúng một mốc — `AssertionError` → dừng, báo người điều phối.

Dòng ghi công trong lệnh commit: thay `<model đang thực thi>` bằng đúng tên model của người thực thi task đó.

---

### Task 1: Khoá `giao_viec:` + adapter principal `tram-kiem`

**Độ khó:** `de` · **Đợt:** 1 · **Song song với:** Task 2–6 · **Phải xong trước:** — (chỉ cần `main` N₀)

**Files:**
- Create: `tram/giao_viec/principal_kiem.py`
- Create: `tram/cau_hinh/giao_viec.py`
- Test: `tests/test_cau_hinh_giao_viec.py` (mới)

**Interfaces:**
- Consumes: `tram_home()`.
- Produces: `PrincipalKiem(ten, boc: tuple[str, ...], trao_quyen: tuple[str, ...] = ())` + `.boc_lenh(argv) -> list[str]`, `.trao(thu_muc, *, chay=subprocess.run)`. `CauHinhGiaoViec(bat=False, chu_ky_giay=120, thu_muc_kiem=None, principal_kiem=None)`, `nap_cau_hinh_giao_viec(duong_dan=None) -> CauHinhGiaoViec` (ValueError khi sai), `CHU_KY = (30, 150)`.

- [ ] **Step 1: Viết test thất bại**

`tests/test_cau_hinh_giao_viec.py` (mới):

```python
"""Khoá `giao_viec:` (4a-2) và adapter principal `tram-kiem` (chờ S6) — không chạy sudo thật."""
import pytest

from tram.cau_hinh.giao_viec import CauHinhGiaoViec, nap_cau_hinh_giao_viec
from tram.giao_viec.principal_kiem import PrincipalKiem

PK = "  principal_kiem:\n    ten: tram-kiem\n    boc: [/usr/bin/sudo, -n, -u, tram-kiem, --]\n"


def _nap(tram_home, noi_dung: str) -> CauHinhGiaoViec:
    tram_home.mkdir(parents=True, exist_ok=True)
    (tram_home / "cau-hinh.yaml").write_text(noi_dung, encoding="utf-8")
    return nap_cau_hinh_giao_viec()


def test_thieu_file_hoac_thieu_khoa_la_tat(tram_home_tam):
    assert nap_cau_hinh_giao_viec() == CauHinhGiaoViec()
    cg = _nap(tram_home_tam, "dai_ca_logins: [a@b.c]\n")
    assert (cg.bat, cg.chu_ky_giay, cg.thu_muc_kiem, cg.principal_kiem) == (False, 120, None, None)


def test_doc_du_khoa(tram_home_tam, tmp_path):
    cg = _nap(tram_home_tam, f"giao_viec:\n  bat: true\n  chu_ky_giay: 90\n  thu_muc_kiem: {tmp_path}/kiem\n" + PK
              + "    trao_quyen: [/usr/local/libexec/trao, --ghi]\n")
    assert (cg.bat, cg.chu_ky_giay, cg.thu_muc_kiem) == (True, 90, tmp_path / "kiem")
    pk = cg.principal_kiem
    assert pk == PrincipalKiem("tram-kiem", ("/usr/bin/sudo", "-n", "-u", "tram-kiem", "--"),
                               ("/usr/local/libexec/trao", "--ghi"))
    assert pk.boc_lenh(["sh", "kiem.sh"]) == ["/usr/bin/sudo", "-n", "-u", "tram-kiem", "--", "sh", "kiem.sh"]


@pytest.mark.parametrize("noi_dung", [
    "giao_viec:\n  bat: 'co'\n",
    "giao_viec:\n  chu_ky_giay: 10\n",
    "giao_viec:\n  chu_ky_giay: 200\n",
    "giao_viec:\n  la: 1\n",
    "giao_viec:\n  bat: true\n",                                                     # bật mà chưa có principal
    "giao_viec:\n  thu_muc_kiem: tuong/doi\n",
    "giao_viec:\n" + PK,                                                             # principal mà thiếu thư mục
    "giao_viec:\n  thu_muc_kiem: {home}/kiem\n" + PK,                                # thư mục trong ~/.tram
    "giao_viec:\n  thu_muc_kiem: /tmp/k\n  principal_kiem:\n    ten: Tram Kiem\n    boc: [/usr/bin/sudo]\n",
    "giao_viec:\n  thu_muc_kiem: /tmp/k\n  principal_kiem:\n    ten: tram-kiem\n    boc: [sudo, -u, x]\n",
    "giao_viec:\n  thu_muc_kiem: /tmp/k\n  principal_kiem:\n    ten: tram-kiem\n    boc: []\n",
])
def test_sai_bao_loi(tram_home_tam, noi_dung):
    with pytest.raises(ValueError):
        _nap(tram_home_tam, noi_dung.replace("{home}", str(tram_home_tam)))


def test_trao_quyen_goi_lenh_voi_thu_muc(tmp_path):
    goi = []
    PrincipalKiem("tram-kiem", ("/usr/bin/sudo",), ("/usr/local/libexec/trao",)).trao(
        tmp_path, chay=lambda argv, **kw: goi.append((argv, kw["check"])))
    PrincipalKiem("tram-kiem", ("/usr/bin/sudo",)).trao(tmp_path, chay=lambda *a, **k: goi.append("khong"))
    assert goi == [(["/usr/local/libexec/trao", str(tmp_path)], True)]

def test_kill_nhom_chay_cung_principal_khong_qua_shell():
    import signal
    goi = []
    pk = PrincipalKiem("tram-kiem", ("sudo", "-n", "-u", "tram-kiem", "--"))
    pk.kill_nhom(123, signal.SIGKILL, chay=lambda *args, **kw: goi.append((args, kw)))
    assert goi == [((["sudo", "-n", "-u", "tram-kiem", "--", "/bin/kill", "-s", "KILL", "--", "-123"],),
                    {"capture_output": True, "timeout": 20})]

```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_cau_hinh_giao_viec.py -q`
Expected: FAIL — `1 error` (`ModuleNotFoundError: No module named 'tram.cau_hinh.giao_viec'`)

- [ ] **Step 3: Viết mã**

`tram/giao_viec/principal_kiem.py` (mới):

```python
"""Principal kiểm lại của trạm `tram-kiem` (spec 3 §7.3 mục 5; spec 4 §6.2 bước 1, 4) — ADAPTER, chờ spike S6.

Cơ chế cách ly (user macOS riêng, sudoers, ACL…) chốt sau S6; mã chỉ biết hai tiền tố argv Đại ca đặt trong
`~/.tram/cau-hinh.yaml`: `boc` (chạy MỘT lệnh dưới `tram-kiem`) và `trao_quyen` (tài khoản trạm trao quyền ghi
worktree kiểm cho `tram-kiem`; nhận thêm một đối số là thư mục). Hình dạng chưa xác minh — `tram giao kiem` chạy thật
từng điều kiện (danh tính, giữ `APP_ENV`, không đọc kho trạm, ghi được worktree, dừng được lệnh quá hạn)."""
import subprocess
import signal
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PrincipalKiem:
    ten: str
    boc: tuple[str, ...]
    trao_quyen: tuple[str, ...] = ()

    def boc_lenh(self, argv: list[str]) -> list[str]:
        """Tham số `boc` của `chay_mot_lenh`/`kiem_lai` (3a-1): argv chạy dưới `tram-kiem`, không qua shell."""
        return [*self.boc, *argv]

    def kill_nhom(self, pgid: int, sig: int, *, chay=subprocess.run) -> None:
        """S6: kill trong cùng principal; không nuốt lỗi quyền/timeout."""
        chay(self.boc_lenh(["/bin/kill", "-s", signal.Signals(sig).name.removeprefix("SIG"),
                           "--", f"-{pgid}"]), capture_output=True, timeout=20)

    def trao(self, thu_muc: Path, *, chay: Callable = subprocess.run) -> None:
        """Trao quyền ghi `thu_muc` — gọi SAU khi trạm chép môi trường kiểm, TRƯỚC lệnh đầu tiên. Lỗi → ném."""
        if self.trao_quyen:
            chay([*self.trao_quyen, str(thu_muc)], check=True, capture_output=True, timeout=60)
```

`tram/cau_hinh/giao_viec.py` (mới):

```python
"""Khoá `giao_viec:` trong `~/.tram/cau-hinh.yaml` (lát 4a-2). `nap_cau_hinh_tram` bỏ qua khoá lạ nên đọc riêng ở
đây — không sửa `tram/cau_hinh/tram.py`. Thiếu khoá → bộ giao việc TẮT: tram-api không phát phiếu, không chạy tick.

    giao_viec:
      bat: false                     # true chỉ sau mọi cổng (3a-2, S6, S7) — cần principal_kiem
      chu_ky_giay: 120               # vòng tick (spec 4 §10); ≤ 150 để giữ G5 ≤ 3 phút
      thu_muc_kiem: /Users/Shared/tram-kiem      # worktree kiểm lại — NGOÀI ~/.tram (tram-kiem không đọc kho trạm)
      principal_kiem:                # chờ S6 — hình dạng lệnh chưa xác minh, `tram giao kiem` kiểm khi chạy thật
        ten: tram-kiem
        boc: [/usr/bin/sudo, -n, -u, tram-kiem, --]
        trao_quyen: [/usr/bin/sudo, -n, /usr/local/libexec/tram-trao-quyen-kiem]
"""
import re
from dataclasses import dataclass
from pathlib import Path

import yaml

from tram.duong_dan import tram_home
from tram.giao_viec.principal_kiem import PrincipalKiem

KHOA = {"bat", "chu_ky_giay", "thu_muc_kiem", "principal_kiem"}
TEN_RE = re.compile(r"[a-z_][a-z0-9_-]{0,31}")
CHU_KY = (30, 150)


@dataclass(frozen=True)
class CauHinhGiaoViec:
    bat: bool = False
    chu_ky_giay: int = 120
    thu_muc_kiem: Path | None = None
    principal_kiem: PrincipalKiem | None = None


def _argv(raw, khoa: str, *, bat_buoc: bool) -> tuple[str, ...]:
    if raw is None and not bat_buoc:
        return ()
    if not isinstance(raw, list) or not raw or not all(isinstance(x, str) and x for x in raw) \
            or not raw[0].startswith("/"):
        raise ValueError(f"giao_viec.principal_kiem.{khoa}: danh sách argv, phần tử đầu là đường dẫn tuyệt đối")
    return tuple(raw)


def _principal(raw) -> PrincipalKiem | None:
    if raw is None:
        return None
    if not isinstance(raw, dict) or not set(raw) <= {"ten", "boc", "trao_quyen"} or "ten" not in raw:
        raise ValueError("giao_viec.principal_kiem phải là bảng {ten, boc, trao_quyen?}")
    if not isinstance(raw["ten"], str) or not TEN_RE.fullmatch(raw["ten"]):
        raise ValueError("giao_viec.principal_kiem.ten không hợp lệ")
    return PrincipalKiem(raw["ten"], _argv(raw.get("boc"), "boc", bat_buoc=True),
                         _argv(raw.get("trao_quyen"), "trao_quyen", bat_buoc=False))


def _thu_muc(raw, pk: PrincipalKiem | None) -> Path | None:
    p = None if raw is None else Path(str(raw)).expanduser()
    if p is not None and not p.is_absolute():
        raise ValueError("giao_viec.thu_muc_kiem phải là đường dẫn tuyệt đối")
    if pk is not None and (p is None or p.resolve().is_relative_to(tram_home().resolve())):
        raise ValueError("giao_viec.thu_muc_kiem phải đặt NGOÀI ~/.tram khi có principal_kiem")
    return p


def nap_cau_hinh_giao_viec(duong_dan: Path | None = None) -> CauHinhGiaoViec:
    p = duong_dan or tram_home() / "cau-hinh.yaml"
    raw = (yaml.safe_load(p.read_text(encoding="utf-8")) or {}) if p.exists() else {}
    gv = raw.get("giao_viec") if isinstance(raw, dict) else None
    if gv is None:
        return CauHinhGiaoViec()
    if not isinstance(gv, dict) or set(gv) - KHOA:
        raise ValueError(f"giao_viec phải là bảng với các khoá {sorted(KHOA)}")
    bat, chu_ky = gv.get("bat", False), gv.get("chu_ky_giay", 120)
    if not isinstance(bat, bool):
        raise ValueError("giao_viec.bat phải là true/false")
    if isinstance(chu_ky, bool) or not isinstance(chu_ky, int) or not CHU_KY[0] <= chu_ky <= CHU_KY[1]:
        raise ValueError(f"giao_viec.chu_ky_giay phải là số nguyên trong {CHU_KY} (giữ G5 ≤ 3 phút)")
    pk = _principal(gv.get("principal_kiem"))
    if bat and pk is None:
        raise ValueError("giao_viec.bat cần principal_kiem — kiểm lại không bao giờ chạy dưới quyền tram-api (G4)")
    return CauHinhGiaoViec(bat, chu_ky, _thu_muc(gv.get("thu_muc_kiem"), pk), pk)
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_cau_hinh_giao_viec.py -q`
Expected: `15 passed`

Run: `uv run pytest -q`
Expected: `N₀ + 15 passed`

- [ ] **Step 5: Commit**

```bash
git add tram/giao_viec/principal_kiem.py tram/cau_hinh/giao_viec.py tests/test_cau_hinh_giao_viec.py
git commit -m "feat(giao-viec): khoá giao_viec trong cau-hinh.yaml + adapter principal tram-kiem (spec 4 §6.2; spec 3 §7.3 mục 5 — chờ S6)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 2: Phiên bản file quyền trong khoá chống trùng

**Độ khó:** `de` · **Đợt:** 1 · **Song song với:** Task 1, 3–6 · **Phải xong trước:** —

**Files:**
- Create: `tram/giao_viec/quyen.py`
- Modify: `tram/giao_viec/de_xuat.py` (bỏ `PHIEN_BAN_QUYEN`)
- Test: `tests/test_quyen_giao.py` (mới)

**Interfaces:**
- Consumes: `goc_repo()`; `dung_de_xuat`, `UngVien` (4a-1); `dung_kho` (`tests/kho_kiem_gia.py`).
- Produces: `KHONG_CO = "0"`, `phien_ban_quyen(vai, *, goc=None) -> str` (`"sha256:<16 hex>"` hoặc `"0"`). `de_xuat.PHIEN_BAN_QUYEN` **bị bỏ** (không ai import).

- [ ] **Step 1: Viết test thất bại**

`tests/test_quyen_giao.py` (mới):

```python
"""`phien_ban_quyen` thật trong khoá chống trùng (spec 4 §5.1 điều kiện 7; 4a-1 G14 → 4a-2)."""
from pathlib import Path

from bead_gia import bead
from kho_kiem_gia import dung_kho
from tram.cau_hinh.du_an import DuAn, MoiTruongKiem
from tram.cau_hinh.du_an_giao import CauHinhGiao
from tram.giao_viec.chon import UngVien
from tram.giao_viec.de_xuat import dung_de_xuat
from tram.giao_viec.git_kiem import fetch
from tram.giao_viec.quyen import KHONG_CO, phien_ban_quyen

DA = DuAn("hr-codex", Path("/r"), None, {}, lenh_cho_phep=("sh kiem.sh",),
          moi_truong_kiem=MoiTruongKiem(Path("/env"), ".env.testing"), giao=CauHinhGiao(lenh_kiem_mac_dinh=("sh kiem.sh",)))


def test_phien_ban_theo_noi_dung_file(tmp_path):
    assert phien_ban_quyen("coder", goc=tmp_path) == KHONG_CO
    (tmp_path / "coder.json").write_text('{"cho_phep": ["Read"]}')
    a = phien_ban_quyen("coder", goc=tmp_path)
    (tmp_path / "coder.json").write_text('{"cho_phep": ["Read", "Edit"]}')
    b = phien_ban_quyen("coder", goc=tmp_path)
    assert a.startswith("sha256:") and a != b and phien_ban_quyen("qc", goc=tmp_path) == KHONG_CO


def test_khoa_chong_trung_doi_khi_file_quyen_doi(tmp_path, monkeypatch):
    k = dung_kho(tmp_path)
    fetch(k.kho)
    goc = tmp_path / "repo-tram"
    (goc / "vai" / "quyen").mkdir(parents=True)
    monkeypatch.setattr("tram.giao_viec.quyen.goc_repo", lambda: goc)
    b = bead("hr-1", labels=["cot:ai-lam"], acceptance_criteria="- Tên kết thúc 'ỷ'", issue_type="bug")
    uv = UngVien(DA, b, "code", False, frozenset())
    k1 = dung_de_xuat(uv, [], {b.id: b}, k.kho).khoa_chong_trung
    (goc / "vai" / "quyen" / "coder.json").write_text('{"cho_phep": ["Read"]}')
    k2 = dung_de_xuat(uv, [], {b.id: b}, k.kho).khoa_chong_trung
    (goc / "vai" / "quyen" / "qc.json").write_text('{"cho_phep": ["Bash"]}')
    assert k1 != k2 == dung_de_xuat(uv, [], {b.id: b}, k.kho).khoa_chong_trung   # đổi quyền vai khác: không đổi
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_quyen_giao.py -q`
Expected: FAIL — `1 error` (`ModuleNotFoundError: No module named 'tram.giao_viec.quyen'`)

- [ ] **Step 3: Viết mã**

`tram/giao_viec/quyen.py` (mới):

```python
"""Phiên bản file quyền theo vai (spec 3 §7.2; spec 4 §5.1 điều kiện 7) — thành phần `phien_ban_quyen` của
`khoa_chong_trung`. File `vai/quyen/<vai>.json` của repo trạm do 3a-2 tạo (đường dẫn theo spec 3 §7.2). Phiên bản =
băm NỘI DUNG file: mọi thay đổi quyền đổi khoá, không phụ thuộc định dạng file (chưa chốt tới S4). Chưa có file
(trước 3a-2) → "0" như 4a-1; `tram giao kiem` báo ĐỎ trường hợp này."""
import hashlib
from pathlib import Path

from tram.duong_dan import goc_repo

KHONG_CO = "0"


def phien_ban_quyen(vai: str, *, goc: Path | None = None) -> str:
    p = (goc or goc_repo() / "vai" / "quyen") / f"{vai}.json"
    if not p.is_file():
        return KHONG_CO
    return "sha256:" + hashlib.sha256(p.read_bytes()).hexdigest()[:16]
```

`tram/giao_viec/de_xuat.py` (sửa — bản vá):

```diff
diff --git a/tram/giao_viec/de_xuat.py b/tram/giao_viec/de_xuat.py
index 9519764..46a24ce 100644
--- a/tram/giao_viec/de_xuat.py
+++ b/tram/giao_viec/de_xuat.py
@@ -13,12 +13,11 @@ from tram.giao_viec.git_kiem import sha_cua
 from tram.giao_viec.goi import DauVaoGoi, GoiQuaLon, dung_goi
 from tram.giao_viec.lop_4 import doc_tai_lieu, thu_lop_4
 from tram.giao_viec.ngan_sach import ngan_sach_phieu
+from tram.giao_viec.quyen import phien_ban_quyen
 from tram.giao_viec.su_kien import SK, cua_so, moi_nhat
 from tram.giao_viec.tieu_chi import khoa_chong_trung, lenh_bat_buoc, tach_tieu_chi
 from tram.phieu.mo_hinh import DeXuatPhieu, Repo
 
-PHIEN_BAN_QUYEN = "0"          # file quyền theo vai `vai/quyen/<vai>.json` — 3a-2 (S2–S4)
-
 
 def cha_cua(ds: list[SK], buoc: str, kho_git: Path, nhanh_chinh: str) -> str | None:
     if buoc == "qc":
@@ -50,6 +49,6 @@ def dung_de_xuat(uv: UngVien, ds: list[SK], theo_id: dict, kho_git: Path) -> DeX
             goi_ngu_canh=goi, ngan_sach=ngan_sach_phieu(buoc, da.giao.ngan_sach), lenh_kiem=lenh,
             lenh_cho_phep=list(da.lenh_cho_phep) if chay_ma else [], can_lenh_kiem=buoc == "code" and chay_ma,
             can_moi_truong_kiem=chay_ma, tieu_chi=tieu_chi,
-            khoa_chong_trung=khoa_chong_trung(da.ten, cha, b.id, buoc, phien_ban, PHIEN_BAN_QUYEN))
+            khoa_chong_trung=khoa_chong_trung(da.ten, cha, b.id, buoc, phien_ban, phien_ban_quyen(VAI[buoc])))
     except (ValidationError, GoiQuaLon):
         return None
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_quyen_giao.py tests/test_ung_vien.py -q`
Expected: `12 passed`

Run: `uv run pytest -q`
Expected: `N₀ + 2 passed`

- [ ] **Step 5: Commit**

```bash
git add tram/giao_viec/quyen.py tram/giao_viec/de_xuat.py tests/test_quyen_giao.py
git commit -m "feat(giao-viec): phien_ban_quyen thật (băm vai/quyen/<vai>.json) trong khoá chống trùng (spec 4 §5.1 đk 7)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 3: Kho kiểm từ remote dự án + fetch có hạn giờ

**Độ khó:** `de` · **Đợt:** 1 · **Song song với:** Task 1, 2, 4–6 · **Phải xong trước:** —

**Files:**
- Create: `tram/giao_viec/kho_kiem_tao.py`
- Modify: `tram/giao_viec/git_kiem.py`
- Test: `tests/test_kho_kiem_tao.py` (mới)

**Interfaces:**
- Consumes: `GIT`, `kho_kiem`, `sha_cua` (4a-1 Task 5); `kho_kiem_co_san` (4a-1 Task 18, chỉ trong test); `dung_kho`, `git` (test).
- Produces: `url_origin(repo) -> str | None`, `github_repo(url) -> "owner/repo" | None`, `loi_remote(url) -> str | None`, `KeHoachKhoKiem(du_an, dich, remote, co_san, lenh)`, `lap_ke_hoach(da) -> KeHoachKhoKiem` (ValueError), `in_ke_hoach(kh) -> str`, `thuc_hien(kh, nhanh_chinh) -> sha | None`. `fetch(kho, *, thoi_gian_cho=120.0)` (quá hạn → `subprocess.TimeoutExpired`).

- [ ] **Step 1: Viết test thất bại**

`tests/test_kho_kiem_tao.py` (mới):

```python
"""Kho kiểm từ remote dự án (spec 4 §6.2 bước 1; S7) — remote là repo bare cục bộ, không mạng."""
import subprocess
from pathlib import Path

import pytest

from git_gia import git
from kho_kiem_gia import dung_kho
from tram.cau_hinh.du_an import DuAn
from tram.giao_viec.bo import kho_kiem_co_san
from tram.giao_viec.git_kiem import fetch
from tram.giao_viec.kho_kiem_tao import github_repo, in_ke_hoach, lap_ke_hoach, loi_remote, thuc_hien


def test_github_repo_va_loi_remote(tmp_path):
    assert github_repo("https://github.com/hung/hr-codex.git") == "hung/hr-codex"
    assert github_repo("git@github.com:hung/hr.codex") == "hung/hr.codex"
    assert github_repo("https://gitlab.com/hung/x.git") is None and github_repo(None) is None
    assert loi_remote("https://github.com/hung/x") is None and loi_remote(str(tmp_path)) is None
    assert loi_remote("http://github.com/hung/x") and loi_remote(None) and loi_remote(str(tmp_path / "khong"))


def test_tao_moi_roi_cap_nhat(tmp_path, tram_home_tam):
    k = dung_kho(tmp_path)
    da = DuAn("hr-codex", k.dev, None, {})
    kh = lap_ke_hoach(da)
    assert (kh.co_san, kh.dich, kh.remote) == (False, tram_home_tam / "kho-kiem" / "hr-codex", str(k.origin))
    assert "TẠO MỚI" in in_ke_hoach(kh) and "--no-checkout" in in_ke_hoach(kh)
    assert kho_kiem_co_san(da) is None and thuc_hien(kh, "main") == k.main
    assert kho_kiem_co_san(da) == kh.dich and not (kh.dich / "AGENTS.md").exists()      # không checkout file
    moi = k.day("main", {"src/tom_tat.py": "x = 9\n"}, tu=k.main)
    kh2 = lap_ke_hoach(da)
    assert kh2.co_san and "cập nhật" in in_ke_hoach(kh2) and thuc_hien(kh2, "main") == moi


def test_kho_co_san_tro_remote_khac_thi_tu_choi(tmp_path):
    k = dung_kho(tmp_path)
    da = DuAn("hr-codex", k.dev, None, {})
    thuc_hien(lap_ke_hoach(da), "main")
    khac = tmp_path / "khac.git"
    git(tmp_path, "clone", "-q", "--bare", str(k.origin), str(khac))
    git(k.dev, "remote", "set-url", "origin", str(khac))
    with pytest.raises(ValueError, match="khác remote"):
        lap_ke_hoach(da)


def test_fetch_qua_han_nem_timeout(tmp_path):
    k = dung_kho(tmp_path)
    with pytest.raises(subprocess.TimeoutExpired):
        fetch(k.kho, thoi_gian_cho=0.000001)
    fetch(k.kho)                                                        # mặc định vẫn chạy được
    assert Path(k.kho / ".git").is_dir()
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_kho_kiem_tao.py -q`
Expected: FAIL — `1 error` (`ModuleNotFoundError: No module named 'tram.giao_viec.kho_kiem_tao'`)

- [ ] **Step 3: Viết mã**

`tram/giao_viec/kho_kiem_tao.py` (mới):

```python
"""Tạo / cập nhật kho kiểm của trạm từ remote dự án (spec 4 §6.2 bước 1; #2 GitHub; credential thật chờ S7).

Kho kiểm `~/.tram/kho-kiem/<du_an>` là bản clone `--no-checkout` do TÀI KHOẢN TRẠM giữ — không bao giờ fetch vào repo
làm việc của Đại ca; chỉ ĐỌC `remote.origin.url` của repo đó. Clone gọi mạng bằng credential của trạm → chỉ chạy sau
khi Đại ca đọc kế hoạch và gõ `dong-y` (khuôn `tram chu cai-dat`). Kho có sẵn trỏ remote khác → báo lỗi, không tự xoá."""
import os
import re
import subprocess
import signal
from dataclasses import dataclass
from pathlib import Path

from tram.cau_hinh.du_an import DuAn
from tram.giao_viec.git_kiem import GIT, kho_kiem, sha_cua

GITHUB_RE = re.compile(r"(?:https://github\.com/|git@github\.com:)([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?/?")


def _env() -> dict[str, str]:
    return {**os.environ, "GIT_TERMINAL_PROMPT": "0"}


def url_origin(repo: Path) -> str | None:
    kq = subprocess.run([*GIT, "-C", str(repo), "config", "--get", "remote.origin.url"], capture_output=True,
                        text=True, env=_env())
    return (kq.stdout.strip() or None) if kq.returncode == 0 else None


def github_repo(url: str | None) -> str | None:
    """`owner/repo` nếu `url` là remote GitHub (https hoặc ssh), ngược lại None."""
    m = GITHUB_RE.fullmatch(url or "")
    return f"{m[1]}/{m[2]}" if m else None


def loi_remote(url: str | None) -> str | None:
    if not url:
        return "repo dự án chưa có remote origin"
    if github_repo(url) or (url.startswith("/") and Path(url).is_dir()):
        return None                     # GitHub (#2) hoặc repo cục bộ (repo nháp, kiểm thử không mạng)
    return f"remote không phải GitHub hay thư mục cục bộ: {url[:200]}"


@dataclass(frozen=True)
class KeHoachKhoKiem:
    du_an: str
    dich: Path
    remote: str
    co_san: bool
    lenh: tuple[tuple[str, ...], ...]


def lap_ke_hoach(da: DuAn) -> KeHoachKhoKiem:
    url = url_origin(da.duong_dan)
    if (loi := loi_remote(url)) is not None:
        raise ValueError(f"{da.ten}: {loi}")
    dich = kho_kiem(da.ten)
    if (dich / ".git").exists():
        if (cu := url_origin(dich)) != url:
            raise ValueError(f"{da.ten}: kho kiểm {dich} trỏ {cu!r}, khác remote dự án {url!r} — xoá tay rồi tạo lại")
        return KeHoachKhoKiem(da.ten, dich, url, True,
                              ((*GIT, "-C", str(dich), "fetch", "--quiet", "--prune", "origin"),))
    return KeHoachKhoKiem(da.ten, dich, url, False, (
        (*GIT, "clone", "--quiet", "--no-checkout", "--config", "core.hooksPath=/dev/null", url, str(dich)),))


def in_ke_hoach(kh: KeHoachKhoKiem) -> str:
    dau = f"Kho kiểm {kh.du_an}: {'cập nhật' if kh.co_san else 'TẠO MỚI'} {kh.dich}\n  remote: {kh.remote}"
    return dau + "".join(f"\n  $ {' '.join(lenh)}" for lenh in kh.lenh)


def thuc_hien(kh: KeHoachKhoKiem, nhanh_chinh: str) -> str | None:
    """Chạy kế hoạch (hook tắt, không hỏi mật khẩu); trả SHA `origin/<nhanh_chinh>` sau khi xong."""
    kh.dich.parent.mkdir(parents=True, exist_ok=True)
    for lenh in kh.lenh:
        subprocess.run(list(lenh), check=True, capture_output=True, env=_env(), timeout=600)
    return sha_cua(kh.dich, f"origin/{nhanh_chinh}")
```

`tram/giao_viec/git_kiem.py` (sửa — bản vá):

```diff
diff --git a/tram/giao_viec/git_kiem.py b/tram/giao_viec/git_kiem.py
index 5c8f8e1..ff94121 100644
--- a/tram/giao_viec/git_kiem.py
+++ b/tram/giao_viec/git_kiem.py
@@ -16,13 +16,14 @@ def kho_kiem(ten_du_an: str) -> Path:
     return tram_home() / "kho-kiem" / ten_du_an
 
 
-def _git(kho: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
-    return subprocess.run([*GIT, "-C", str(kho), *args], capture_output=True, check=check,
+def _git(kho: Path, *args: str, check: bool = True, timeout: float | None = None) -> subprocess.CompletedProcess:
+    return subprocess.run([*GIT, "-C", str(kho), *args], capture_output=True, check=check, timeout=timeout,
                           env={**os.environ, "GIT_TERMINAL_PROMPT": "0"})
 
 
-def fetch(kho: Path) -> None:
-    _git(kho, "fetch", "--quiet", "--prune", "origin")
+def fetch(kho: Path, *, thoi_gian_cho: float = 120.0) -> None:
+    """Quá `thoi_gian_cho` giây → `subprocess.TimeoutExpired` (vòng tick đếm lỗi dự án đó, dự án khác chạy tiếp)."""
+    _git(kho, "fetch", "--quiet", "--prune", "origin", timeout=thoi_gian_cho)
 
 
 def sha_cua(kho: Path, ref: str) -> str | None:
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_kho_kiem_tao.py tests/test_git_kiem.py -q`
Expected: `9 passed`

Run: `uv run pytest -q`
Expected: `N₀ + 4 passed`

- [ ] **Step 5: Commit**

```bash
git add tram/giao_viec/kho_kiem_tao.py tram/giao_viec/git_kiem.py tests/test_kho_kiem_tao.py
git commit -m "feat(giao-viec): kế hoạch clone/cập nhật kho kiểm từ remote dự án, fetch có hạn giờ (spec 4 §6.2 bước 1; #2)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 4: Đọc lại Beads ngay trước cấp + bộ đệm beads cho bộ chọn

**Độ khó:** `kho` · **Đợt:** 1 · **Song song với:** Task 1–3, 5, 6 · **Phải xong trước:** —

**Files:**
- Create: `tram/giao_viec/doc_beads.py`
- Create: `tram/giao_viec/doc_lai.py`
- Modify: `tram/giao_viec/bo.py`
- Test: `tests/test_doc_lai.py` (mới)

**Interfaces:**
- Consumes: `BoDemBeads` (2a); `bi_chan_boi` (1a); `ly_do_khong_giao`, `ASSIGNEE` (4a-1 Task 10); `BoGiaoViec` (4a-1 Task 18); `dung`, `bug` (`tests/giao_viec_gia.py`).
- Produces: `DocBeads(bo_dem, *, tuoi=30.0, dong_ho=time.monotonic)` + `.lay(da, bd) -> (list[Bead], set[str])`, `.danh_dau_cu(du_an)`. `dau_bead(b) -> str`, `con_nguyen(bd, da, cu, *, sau_claim=False) -> bool`. `BoGiaoViec` thêm trường `doc_beads: DocBeads | None = None`, `trao_quyen: Callable[[Path], None] | None = None`, `thu_muc_kiem: Path | None = None` (hai trường sau do Task 7 dùng) và `._chot(bd, uv) -> bool`.

- [ ] **Step 1: Viết test thất bại**

`tests/test_doc_lai.py` (mới):

```python
"""Đọc lại Beads ngay trước cấp (4a-1 G3 → 4a-2) + bộ đệm beads cho bộ chọn (BoDemBeads).
Kéo cột xen kẽ: Đại ca kéo bead sang cột 2 sau khi bộ chọn lấy snapshot → không claim, không đề xuất."""
from dataclasses import replace

from giao_viec_gia import bug, dung
from tram.api.bo_dem import BoDemBeads
from tram.giao_viec.doc_beads import DocBeads
from tram.giao_viec.doc_lai import dau_bead
from tram.giao_viec.git_kiem import fetch


def co_dem(t, tuoi=3600.0):
    t.bo.doc_beads = DocBeads(BoDemBeads(lambda ten: t.g, tuoi_toi_da=tuoi), tuoi=tuoi)
    t.bo.doc_beads.lay(t.da, t.g)                       # mồi bộ đệm = snapshot cũ
    fetch(t.k.kho)
    return t


def keo(t, bead_id="hr-1", **kw):
    t.g.beads[bead_id] = replace(t.g.beads[bead_id], **kw)


def test_dau_bead_bo_qua_updated_at_va_notes():
    b = bug()
    assert dau_bead(b) == dau_bead(replace(b, updated_at="2027-01-01T00:00:00Z", notes="x"))
    assert dau_bead(b) != dau_bead(replace(b, labels=("cot:can-chot",)))
    assert dau_bead(b) != dau_bead(replace(b, acceptance_criteria="- khác"))


def test_keo_sang_cot_2_sau_snapshot_thi_khong_claim(tmp_path):
    t = co_dem(dung(tmp_path, bug()))
    keo(t, labels=("cot:can-chot",))
    assert t.bo.chon("B/claude-1", None) is None and t.g.so_lan("nhan_viec") == 0


def test_tieu_chi_doi_sau_snapshot_thi_huy(tmp_path):
    t = co_dem(dung(tmp_path, bug()))
    keo(t, acceptance_criteria="- Tiêu chí mới")
    assert t.bo.chon("B/claude-1", None) is None and t.g.so_lan("nhan_viec") == 0


def test_bead_chan_moi_mo_lai_thi_huy(tmp_path):
    t = co_dem(dung(tmp_path, bug(chan_boi=["hr-2"]), bug("hr-2", status="closed", labels=[])))
    keo(t, "hr-2", status="open")                       # bead chặn mở lại: bd ready trong bộ đệm đã cũ
    assert t.bo.chon("B/claude-1", None) is None


def test_keo_cot_giua_claim_va_cap_thi_huy(tmp_path):
    t = co_dem(dung(tmp_path, bug()))
    goc = t.g.nhan_viec
    t.g.nhan_viec = lambda i: (goc(i), keo(t, i, labels=("cot:can-chot",)))
    assert t.bo.chon("B/claude-1", None) is None
    assert t.g.beads["hr-1"].status == "in_progress"    # đã claim: bead ở lại cho Đại ca thấy (spec 4 §5.4)


def test_khong_doi_thi_de_xuat_va_danh_dau_bo_dem_cu(tmp_path):
    t = co_dem(dung(tmp_path, bug()))
    so = t.g.so_lan("tat_ca")
    dx = t.bo.chon("B/claude-1", None)
    assert dx.bead_id == "hr-1" and t.g.beads["hr-1"].status == "in_progress"
    assert t.g.so_lan("tat_ca") == so + 2               # đúng hai lần đọc lại (trước và sau claim)
    t.bo.doc_beads.lay(t.da, t.g)
    assert t.g.so_lan("tat_ca") == so + 3               # bộ đệm đã bị đánh dấu cũ → đọc mới


def test_bo_dem_khong_goi_bd_moi_lan_xin_viec(tmp_path):
    t = co_dem(dung(tmp_path, bug(labels=["cot:can-chot"])))
    so_list, so_ready = t.g.so_lan("tat_ca"), t.g.so_lan("san_sang")
    for _ in range(3):
        assert t.bo.chon("B/claude-1", None) is None
    assert (t.g.so_lan("tat_ca"), t.g.so_lan("san_sang")) == (so_list, so_ready)

def test_adr_regex_khong_mo_gate_khi_chua_co_adapter(tmp_path):
    from tram.cau_hinh.du_an import HangRao
    from tram.giao_viec.doc_lai import con_nguyen
    t = dung(tmp_path, bug(description="chưa có ADR-0083; đổi schema"))
    da = replace(t.da, hang_rao={"schema": HangRao(tu_khoa=("schema",))})
    assert not con_nguyen(t.g, da, t.g.beads["hr-1"])


def test_adr_adapter_phai_xac_minh_dung_repo_va_cong_viec(tmp_path):
    from tram.cau_hinh.du_an import HangRao
    from tram.giao_viec.doc_lai import con_nguyen
    t = dung(tmp_path, bug(description="đổi schema ADR-0083"))
    da = replace(t.da, hang_rao={"schema": HangRao(tu_khoa=("schema",))})
    b = t.g.beads["hr-1"]
    # CHỈ DÙNG TRONG TEST: kết quả adapter đã kiểm tồn tại/được duyệt/phạm vi.
    for hop_le in (False, True):
        assert con_nguyen(t.g, da, b, adr_hop_le=lambda d, x: hop_le and d == da and x == b) is hop_le


def test_quyet_dinh_blocks_da_dong_van_duoc_chot(tmp_path):
    from bead_gia import bead
    from tram.cau_hinh.du_an import HangRao
    from tram.giao_viec.doc_lai import con_nguyen
    t = dung(tmp_path, bug(description="đổi schema", chan_boi=["hr-d"]),
             bead("hr-d", issue_type="decision", status="closed"))
    da = replace(t.da, hang_rao={"schema": HangRao(tu_khoa=("schema",))})
    assert con_nguyen(t.g, da, t.g.beads["hr-1"])

```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_doc_lai.py -q`
Expected: FAIL — `1 error` (`ModuleNotFoundError: No module named 'tram.giao_viec.doc_beads'`)

- [ ] **Step 3: Viết mã**

`tram/giao_viec/doc_beads.py` (mới):

```python
"""Đọc beads cho bộ chọn việc qua bộ đệm của tram-api (`BoDemBeads`, tuổi ≤ 30 s — 4a-1 rủi ro c): mỗi lần khe xin
việc không còn chạy `bd list` cho mọi dự án. `bd ready` đệm cùng tuổi, hết hạn khi danh sách beads đổi phiên bản.
Snapshot cũ ≤ 30 s chấp nhận được vì bộ chọn luôn đọc lại bead được chọn ngay trước cấp (`doc_lai.py`)."""
import threading
import time
from collections.abc import Callable

from tram.api.bo_dem import BoDemBeads
from tram.beads.mo_hinh import Bead
from tram.cau_hinh.du_an import DuAn


class DocBeads:
    def __init__(self, bo_dem: BoDemBeads, *, tuoi: float = 30.0, dong_ho: Callable[[], float] = time.monotonic):
        self._bo_dem, self._tuoi, self._dong_ho = bo_dem, tuoi, dong_ho
        self._khoa = threading.Lock()
        self._san: dict[str, tuple[int, float, set[str]]] = {}

    def lay(self, da: DuAn, bd) -> tuple[list[Bead], set[str]]:
        """(beads từ bộ đệm, id trong `bd ready`)."""
        beads = self._bo_dem.lay(da.ten)
        pb = self._bo_dem.phien_ban(da.ten)
        with self._khoa:
            co = self._san.get(da.ten)
        if co is not None and co[0] == pb and self._dong_ho() - co[1] < self._tuoi:
            return beads, co[2]
        san = bd.san_sang()
        with self._khoa:
            self._san[da.ten] = (pb, self._dong_ho(), san)
        return beads, san

    def danh_dau_cu(self, du_an: str) -> None:
        """Sau khi trạm ghi beads (claim): lần đọc sau — của bộ chọn và của dashboard — đọc mới."""
        self._bo_dem.danh_dau_cu(du_an)
        with self._khoa:
            self._san.pop(du_an, None)
```

`tram/giao_viec/doc_lai.py` (mới):

```python
"""Đọc lại Beads NGAY TRƯỚC cấp phiếu (spec 4 §5.1 "giới hạn nhất quán"; 4a-1 G3 — Đại ca đã chấp nhận rủi ro còn lại).

Snapshot dùng để chọn có thể cũ (bộ đệm ≤ 30 s; `bd list` đọc trước khi dựng gói). Trước khi trả đề xuất cho phần 3,
bộ chọn đọc lại danh sách (`bd list` — dạng JSON đã spike) và HUỶ nếu bead được chọn đã đổi nội dung có ý nghĩa
(nhãn, tiêu chí, mô tả, design, loại, phụ thuộc, cha, ưu tiên), đổi trạng thái/người nhận ngoài dự kiến, hoặc không
còn đủ điều kiện §5.1 trên bản mới (gồm "bị chặn" tính trên trạng thái MỚI của bead chặn). `updated_at`, `notes`
không tính. Thay đổi SAU lần đọc cuối tới lúc phần 3 cấp xong vẫn là rủi ro còn lại — không có giao dịch xuyên
Beads/SQLite, không gọi `bd` khi giữ khoá SQLite (3a-1 G11)."""
import hashlib
import json

from tram.beads.bd import LoiBd
from tram.beads.mo_hinh import Bead
from tram.cau_hinh.du_an import DuAn
from tram.cham_cot.luat_cung import bi_chan_boi, kiem, quyet_dinh_da_chot
from tram.giao_viec.dieu_kien import ASSIGNEE, ly_do_khong_giao


def dau_bead(b: Bead) -> str:
    noi_dung = [b.title, b.description, b.acceptance_criteria, b.design, b.issue_type, sorted(b.labels),
                sorted([p.depends_on_id, p.loai] for p in b.phu_thuoc), b.parent, b.priority]
    return hashlib.sha256(json.dumps(noi_dung, ensure_ascii=False).encode()).hexdigest()


def con_nguyen(bd, da: DuAn, cu: Bead, *, sau_claim: bool = False, adr_hop_le=lambda da, b: False) -> bool:
    """True = bead vẫn như snapshot `cu` và vẫn đủ điều kiện. `sau_claim`: vừa `--claim` nên phải là `in_progress`
    với assignee trạm; ngược lại trạng thái/người nhận phải y như snapshot."""
    try:
        theo_id = {b.id: b for b in bd.tat_ca()}
    except LoiBd:
        return False
    moi = theo_id.get(cu.id)
    if moi is None or dau_bead(moi) != dau_bead(cu):
        return False
    if (moi.status, moi.assignee) != (("in_progress", ASSIGNEE) if sau_claim else (cu.status, cu.assignee)):
        return False
    # Regex ADR trong nội dung không chứng minh quyết định đã được duyệt.
    if kiem(moi, da, theo_id).cham and not quyet_dinh_da_chot(moi, theo_id):
        if not adr_hop_le(da, moi):
            return False
    san = {moi.id} if moi.status == "open" and not bi_chan_boi(moi, theo_id) else set()
    return ly_do_khong_giao(moi, theo_id, san, da) is None
```

`tram/giao_viec/bo.py` (sửa — bản vá):

```diff
diff --git a/tram/giao_viec/bo.py b/tram/giao_viec/bo.py
--- a/tram/giao_viec/bo.py
+++ b/tram/giao_viec/bo.py
@@ -1,6 +1,7 @@
 """Bộ giao việc — giao diện với phần 3 (spec 4 §13; hợp đồng 3a-1 G11): `chon(khe_id, han_muc)` gọi NGOÀI giao
 dịch cấp phiếu (được đọc/ghi beads), `con_hop_le(de_xuat)` gọi TRONG giao dịch (chỉ đọc kho, nhanh).
-Nối vào tram-api (`PhuThuocApi.chon_phieu`, luồng tick) là việc của lát sau khi qua cổng 3a-2 — xem plan."""
+4a-2: đọc lại Beads ngay trước cấp (`doc_lai.py`), bộ đệm beads của tram-api (`doc_beads.py`); nối vào tram-api ở
+`noi_that.py`."""
 import os
 from collections.abc import Callable, Mapping
 from contextlib import closing
@@ -14,6 +15,8 @@
 from tram.giao_viec.chon import khe_nhan, khoa_sap_xep
 from tram.giao_viec.de_xuat import dung_de_xuat
 from tram.giao_viec.dieu_kien import ASSIGNEE
+from tram.giao_viec.doc_beads import DocBeads
+from tram.giao_viec.doc_lai import con_nguyen
 from tram.giao_viec.git_kiem import kho_kiem
 from tram.giao_viec.ngan_sach import du_mot_phieu
 from tram.giao_viec.su_kien import su_kien_bead
@@ -40,6 +43,11 @@
     kho_git: Callable[[DuAn], Path | None] = kho_kiem_co_san
     boc: Callable[[list[str]], list[str]] | None = None   # principal `tram-kiem` (chờ S6); None: chưa kiểm lại
     env_goc: Mapping[str, str] = field(default_factory=lambda: dict(os.environ))
+    doc_beads: DocBeads | None = None                     # 4a-2: bộ đệm beads của tram-api; None: đọc `bd` mỗi lần
+    trao_quyen: Callable[[Path], None] | None = None      # 4a-2: trao quyền ghi worktree kiểm cho `tram-kiem` (S6)
+    adr_hop_le: Callable[[DuAn, object], bool] = lambda da, b: False
+    kill: Callable[[int, int], None] = _kill_nhom        # 3a-2: kill nhóm qua principal kiểm
+    thu_muc_kiem: Path | None = None                      # 4a-2: thư mục worktree kiểm lại; None: ~/.tram/kiem
 
     def _da_nhan(self, bd, bead_id: str) -> bool:
         """`--claim` có ID thao tác là chính trạng thái đích: đã `in_progress` với assignee trạm → coi như xong."""
@@ -47,8 +55,23 @@
             bd.nhan_viec(bead_id)
             return True
         except LoiBd:
-            b = bd.mot(bead_id)
+            try:
+                b = bd.mot(bead_id)
+            except LoiBd:
+                return False
             return b.status == "in_progress" and b.assignee == ASSIGNEE
+
+    def _chot(self, bd, uv) -> bool:
+        """Đọc lại NGAY TRƯỚC cấp (4a-1 G3); bead `open` → `--claim` rồi đọc lại lần nữa (spec 4 §5.4)."""
+        if not con_nguyen(bd, uv.du_an, uv.bead, adr_hop_le=self.adr_hop_le):
+            return False
+        if uv.bead.status != "open":
+            return True
+        if not self._da_nhan(bd, uv.bead.id):
+            return False
+        if self.doc_beads is not None:
+            self.doc_beads.danh_dau_cu(uv.du_an.ten)
+        return con_nguyen(bd, uv.du_an, uv.bead, sau_claim=True, adr_hop_le=self.adr_hop_le)
 
     def chon(self, khe_id: str, han_muc: HanMuc | None) -> DeXuatPhieu | None:
         with closing(self.mo_kho()) as kho:
@@ -58,7 +81,7 @@
                     continue
                 bd = self.tao_bd(da)
                 try:
-                    beads, san = bd.tat_ca(), bd.san_sang()
+                    beads, san = self.doc_beads.lay(da, bd) if self.doc_beads else (bd.tat_ca(), bd.san_sang())
                 except LoiBd:
                     continue
                 ung_vien += [(uv, beads, bd, kg) for uv in liet_ke(kho, da, beads, san)]
@@ -66,7 +89,7 @@
                 if not khe_nhan(khe_id, han_muc, uv, cac_khe, self.ch):
                     continue
                 dx = dung_de_xuat(uv, su_kien_bead(kho, uv.du_an.ten, uv.bead.id), {b.id: b for b in beads}, kg)
-                if dx is None or (uv.bead.status == "open" and not self._da_nhan(bd, uv.bead.id)):
+                if dx is None or not self._chot(bd, uv):
                     continue
                 return dx
         return None
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_doc_lai.py tests/test_bo_giao_viec.py tests/test_kich_ban_4a1.py -q`
Expected: PASS tất cả test được gọi; riêng test mới xem bảng đợt

Run: `uv run pytest -q`
Expected: `N₀ + 10 passed`

- [ ] **Step 5: Commit**

```bash
git add tram/giao_viec/doc_beads.py tram/giao_viec/doc_lai.py tram/giao_viec/bo.py tests/test_doc_lai.py
git commit -m "feat(giao-viec): đọc lại Beads ngay trước cấp (trước và sau claim) + bộ đệm beads của tram-api cho bộ chọn (spec 4 §5.1; 4a-1 G3)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 5: Kiểm lại trao quyền cho `tram-kiem` trước khi chạy lệnh

**Độ khó:** `de` · **Đợt:** 1 · **Song song với:** Task 1–4, 6 · **Phải xong trước:** —

**Files:**
- Modify: `tram/giao_viec/kiem_lai.py`
- Test: `tests/test_kiem_lai_principal.py` (mới)

**Interfaces:**
- Consumes: `kiem_lai` (4a-1 Task 14); `dung_kho`.
- Produces: `kiem_lai(…, trao_quyen: Callable[[Path], None] | None = None)` — gọi `trao_quyen(worktree)` sau `chep_moi_truong_kiem`, trước lệnh đầu tiên; ném lỗi thì không chạy lệnh, worktree vẫn được dọn.

- [ ] **Step 1: Viết test thất bại**

`tests/test_kiem_lai_principal.py` (mới):

```python
"""Kiểm lại dưới principal `tram-kiem` (spec 3 §7.3 mục 5; spec 4 §6.2 bước 1): worktree do trạm tạo, chép môi
trường kiểm, RỒI mới trao quyền ghi, rồi mới chạy lệnh. Không chạy sudo thật — `trao_quyen` giả."""
import os
import subprocess
from pathlib import Path

import pytest

from kho_kiem_gia import dung_kho
from tram.cau_hinh.du_an import DuAn, MoiTruongKiem
from tram.giao_viec.git_kiem import fetch
from tram.giao_viec.kiem_lai import kiem_lai


@pytest.fixture
def m(tmp_path):
    k = dung_kho(tmp_path)
    env = tmp_path / "env.testing"
    env.write_text("DB_DATABASE=test\n")
    return k, DuAn("hr-codex", Path("/r"), None, {}, moi_truong_kiem=MoiTruongKiem(env, ".env.testing")), tmp_path


def chay(m, tep, *, lenh=("sh kiem.sh",), trao_quyen=None, chay_lenh=True, kill=_kill_nhom):
    k, da, tmp = m
    sha = k.day("tram/hr-1", tep, tu=k.main)
    fetch(k.kho)
    return kiem_lai(k.kho, da, giao_id="g-1", commit=sha, lenh_kiem=list(lenh), lenh_cho_phep=["sh kiem.sh"],
                    chay_lenh=chay_lenh, thu_muc=tmp / "kiem-ngoai", thu_muc_log=tmp / "log", boc=lambda a: a,
                    env_goc=os.environ, trao_quyen=trao_quyen, kill=kill)


def test_trao_quyen_sau_moi_truong_kiem_truoc_lenh(m):
    thay = []

    def trao(wt: Path):
        thay.append((wt, (wt / ".env.testing").is_file(), (wt / "DA_CHAY").exists()))

    kq = chay(m, {"kiem.sh": "touch DA_CHAY\n"}, trao_quyen=trao)
    assert kq.dat and thay == [(m[2] / "kiem-ngoai" / "g-1", True, False)]


def test_trao_quyen_loi_thi_nem_khong_chay_lenh_va_don_worktree(m):
    def trao(wt: Path):
        raise subprocess.CalledProcessError(1, ["trao"])

    with pytest.raises(subprocess.CalledProcessError):
        chay(m, {"kiem.sh": f"touch {m[2]}/DA_CHAY\n"}, trao_quyen=trao)
    assert not (m[2] / "DA_CHAY").exists() and not (m[2] / "kiem-ngoai" / "g-1").exists()


def test_spike_va_cham_cam_khong_trao_quyen(m):
    goi = []
    assert chay(m, {"docs/spikes/x.md": "kết luận"}, lenh=(), chay_lenh=False, trao_quyen=goi.append).dat
    assert chay(m, {"package.json": "{}"}, trao_quyen=goi.append).loi == "dong-file-cau-hinh" and goi == []

def test_kiem_lai_truyen_kill_principal(m, monkeypatch):
    from types import SimpleNamespace
    kill = lambda pid, sig: None
    goi = []
    def gia(*args, **kw):
        goi.append(kw["kill"])
        return SimpleNamespace(sang_lenh_kiem=lambda: {"ket_qua": "pass", "digest_log": "sha256:x"})
    monkeypatch.setattr("tram.giao_viec.kiem_lai.chay_mot_lenh", gia)
    assert chay(m, {"kiem.sh": "true\n"}, kill=kill).dat
    assert goi == [kill]

```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_kiem_lai_principal.py -q`
Expected: FAIL — `3 failed` (`TypeError: kiem_lai() got an unexpected keyword argument 'trao_quyen'`)

- [ ] **Step 3: Viết mã**

`tram/giao_viec/kiem_lai.py` (sửa — bản vá):

```diff
diff --git a/tram/giao_viec/kiem_lai.py b/tram/giao_viec/kiem_lai.py
--- a/tram/giao_viec/kiem_lai.py
+++ b/tram/giao_viec/kiem_lai.py
@@ -4,6 +4,7 @@
 kiểm; 2. spike tài liệu: dừng ở đây (không chạy lệnh); 3. chép môi trường kiểm; 4. chạy MỌI lệnh bắt buộc của phiếu
 (khớp `lenh_cho_phep`, không shell, 15 phút/lệnh, kill cả nhóm); 5. đạt ⇔ mọi lệnh chạy được và pass.
 `boc` chọn principal `tram-kiem` (phần 3 §7.3 mục 5 — chờ S6); mã này không tự chạy dưới quyền trạm."""
+import os
 from collections.abc import Callable, Mapping
 from dataclasses import dataclass
 from pathlib import Path
@@ -33,7 +34,9 @@
 def kiem_lai(kho_git: Path, du_an: DuAn, *, giao_id: str, commit: str, lenh_kiem: list[str],
              lenh_cho_phep: list[str], chay_lenh: bool, thu_muc: Path, thu_muc_log: Path,
              boc: Callable[[list[str]], list[str]], env_goc: Mapping[str, str],
-             thoi_gian_cho: float = THOI_GIAN_CHO) -> KetQuaKiemLai:
+             thoi_gian_cho: float = THOI_GIAN_CHO,
+             trao_quyen: Callable[[Path], None] | None = None,
+             kill: Callable[[int, int], None] = _kill_nhom) -> KetQuaKiemLai:
     cham = diff_cham_cam(kho_git, f"origin/{du_an.nhanh_chinh}", commit, them=du_an.giao.duong_dan_cam,
                          cho_phep=du_an.giao.duong_dan_cam_cho_phep)
     if cham:
@@ -50,10 +53,12 @@
             chep_moi_truong_kiem(mt.file, wt, mt.dich)
         except LoiMoiTruongKiem:
             return KetQuaKiemLai(False, loi="thieu-moi-truong-kiem")      # không bao giờ chạy với .env có thể thật
+        if trao_quyen is not None:
+            trao_quyen(wt)            # 4a-2: trao quyền ghi cho `tram-kiem` SAU khi chép môi trường kiểm (spec 3 §7.3)
         env, ket_qua = moi_truong_kiem(env_goc), []
         for i, lenh in enumerate(lenh_kiem, 1):
             kq = chay_mot_lenh(lenh, khop_bat_ky(lenh, lenh_cho_phep), cwd=wt, env=env, boc=boc,
-                               log=thu_muc_log / f"{giao_id}-kiem-lai-{i}.log", thoi_gian_cho=thoi_gian_cho)
+                               log=thu_muc_log / f"{giao_id}-kiem-lai-{i}.log", thoi_gian_cho=thoi_gian_cho, kill=kill)
             ket_qua.append(kq.sang_lenh_kiem())
     finally:
         xoa_worktree(kho_git, wt)
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_kiem_lai_principal.py tests/test_kiem_lai.py -q`
Expected: `15 passed`

Run: `uv run pytest -q`
Expected: `N₀ + 4 passed`

- [ ] **Step 5: Commit**

```bash
git add tram/giao_viec/kiem_lai.py tests/test_kiem_lai_principal.py
git commit -m "feat(giao-viec): kiểm lại trao quyền ghi worktree cho tram-kiem sau môi trường kiểm, trước lệnh (spec 3 §7.3 mục 5)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 6: `nhanh-bi-day-ngoai-luong` trong `LY_DO_BI` (hợp đồng với 3a-2)

**Độ khó:** `de` · **Đợt:** 1 · **Song song với:** Task 1–5 · **Phải xong trước:** —

**Files:**
- Modify (có điều kiện): `tram/phieu/bao.py`
- Test: `tests/test_nhanh_bi_day.py` (mới)

**Interfaces:**
- Consumes: `ThanBao`, `LY_DO_BI`, `nhan_bao` (3a-1 Task 18); `xin`, `bao` (`tests/test_kich_ban_4a1.py`); `mot_vong_tick`; ánh xạ `LY_DO_BI` của `tram/giao_viec/escalation.py` (4a-1).
- Produces: `LY_DO_BI` chứa `"nhanh-bi-day-ngoai-luong"` (G4).

- [ ] **Step 1: Viết test thất bại**

`tests/test_nhanh_bi_day.py` (mới):

```python
"""Hợp đồng `bao.bi {ly_do: "nhanh-bi-day-ngoai-luong"}` (spec 4 §9; 4a-1 G20): thợ báo được (3a-1 `LY_DO_BI`),
trạm nhận qua `nhan_bao` thật và vòng tick tạo escalation `nhanh-bi-day`, không giao lại."""
from giao_viec_gia import bug, dung
from test_kich_ban_4a1 import bao, xin
from tram.giao_viec.tick import mot_vong_tick
from tram.phieu.bao import LY_DO_BI, ThanBao


def test_ly_do_bi_nhan_nhanh_bi_day():
    assert "nhanh-bi-day-ngoai-luong" in LY_DO_BI
    assert ThanBao(khe_id="B/claude-1", giao_id="g-20261013-0001", luot=1, loai="bi", request_id="r-12345678",
                   ly_do="nhanh-bi-day-ngoai-luong").ly_do == "nhanh-bi-day-ngoai-luong"


def test_bao_bi_nhanh_bi_day_thanh_escalation(tmp_path):
    t = dung(tmp_path, bug())
    mot_vong_tick(t.bo)
    p = xin(t, "claude-1")
    bao(t, p, "bi", ly_do="nhanh-bi-day-ngoai-luong", noi_dung="CAS ref công bố thất bại")
    mot_vong_tick(t.bo)
    esc = [b for b in t.g.beads.values() if b.issue_type == "decision"]
    assert len(esc) == 1 and "ly_do: nhanh-bi-day" in esc[0].description and "CAS" in esc[0].description
    assert xin(t, "claude-1") is None and xin(t, "claude-2") is None                 # bead bị chặn, không giao lại
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_nhanh_bi_day.py -q`
Expected: FAIL — `2 failed` (`AssertionError` ở `"nhanh-bi-day-ngoai-luong" in LY_DO_BI`). **Nếu 3a-2 đã thêm giá trị này: `2 passed` ngay** — vẫn chạy Step 3 (script không sửa gì) và ghi vào commit.

- [ ] **Step 3: Viết mã** (chèn có điều kiện — 3a-2 có thể đã thêm)

```bash
uv run python - <<'EOF'
from pathlib import Path

f = Path("tram/phieu/bao.py")
s = f.read_text(encoding="utf-8")
if '"nhanh-bi-day-ngoai-luong"' in s:
    print("LY_DO_BI đã có nhanh-bi-day-ngoai-luong (3a-2) — không sửa")
else:
    moc = '"can-hoi", "thieu-moi-truong-kiem")'
    assert s.count(moc) == 1, "không thấy đúng một mốc cuối LY_DO_BI — dừng, báo người điều phối"
    f.write_text(s.replace(moc, '"can-hoi", "thieu-moi-truong-kiem",\n            "nhanh-bi-day-ngoai-luong")'),
                 encoding="utf-8")
    print("đã thêm nhanh-bi-day-ngoai-luong vào LY_DO_BI")
EOF
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_nhanh_bi_day.py tests/test_nhan_bao.py -q`
Expected: PASS tất cả test được gọi; riêng test mới xem bảng đợt

Run: `uv run pytest -q`
Expected: `N₀ + 2 passed`

- [ ] **Step 5: Commit**

```bash
git add tests/test_nhanh_bi_day.py tram/phieu/bao.py
git commit -m "feat(phieu): bao.bi nhanh-bi-day-ngoai-luong → escalation nhanh-bi-day, test hợp đồng đầu-cuối (spec 4 §9; 4a-1 G20)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 7: Vòng tick hai pha + cột 3 kiểm ref công bố trên remote

**Độ khó:** `kho` · **Đợt:** 2 · **Song song với:** — · **Phải xong trước:** Task 3, 4, 5

**Files:**
- Create: `tram/giao_viec/hang_doi.py`
- Modify: `tram/giao_viec/pipeline.py`
- Test: `tests/test_hoi_quy_4a2.py` (9 ca)
- Create: `tram/giao_viec/tick_cot_3.py`
- Modify: `tram/giao_viec/tick.py`, `tram/giao_viec/tick_pipeline.py`
- Test: `tests/test_tick_hai_pha.py` (mới)

**Interfaces:**
- Consumes: `fetch(kho, *, thoi_gian_cho)` (Task 3); `BoGiaoViec.trao_quyen`, `.thu_muc_kiem` (Task 4); `kiem_lai(…, trao_quyen)` (Task 5); `vao_cot_3`, `tao_escalation`, `ly_do_khong_giao`, `buoc_ke_tiep`, `trang_thai_bead`, `viec_ton_cua`, `bat_dau_chu_ky`, `sha_cua`, `su_kien_bead`, `moi_nhat` (4a-1); test: `GIU`, `chuan_bi_code_xong`, `loai` (`test_tick.py`), `F`, `bg`.
- Produces: `tick.py`: `LOI` (thêm `subprocess.TimeoutExpired`), `FETCH_GIAY = 120`, `vong_nhanh(bo, *, thu=False) -> dict`, `vong_git(bo) -> dict`, `mot_vong_tick(bo, *, thu=False) -> dict` (= hai pha nối tiếp). `tick_pipeline.py`: `VIEC_NHANH = {"het_ngan_sach"}`, `VIEC_GIT = {"kiem_lai", "cot_3", "moi_truong"}`, `day_pipeline(…, *, viec=VIEC_NHANH | VIEC_GIT)`. `tick_cot_3.py`: `ten_nhanh(ref)`, `vao_cot_3_an_toan(bd, kho, kg, da, b, luc) -> "cot_3" | "nhanh_bi_day" | None`. Test: `bi(t, bead_id="hr-1")`, `qc_dat(t)` (`tests/test_tick_hai_pha.py`).

- [ ] **Step 1: Viết test thất bại**

`tests/test_tick_hai_pha.py` (mới):

```python
"""Vòng tick hai pha (spec 4 §10 "ràng buộc lúc nối 4a-2"; G5): pha nhanh không cần Git/lệnh kiểm; pha Git xét
`bao.xong`, kiểm lại (dưới principal + thư mục kiểm cấu hình được), cột 3 có kiểm ref công bố trên remote."""
import subprocess

from giao_viec_gia import bug, dung
from kho_phieu_gia import LUC, dat_phieu
from su_kien_gia import cong_bo, ds, ket_thuc, kiem, nhan, qc, sk
from test_tick import GIU, chuan_bi_code_xong, loai
from test_xet_xong import F, bg
from tram.giao_viec import tick
from tram.giao_viec.escalation import tao_escalation
from tram.giao_viec.tick import mot_vong_tick, vong_git, vong_nhanh
from tram.giao_viec.tick_pipeline import VIEC_GIT, day_pipeline
from tram.giao_viec.tieu_chi import digest_tieu_chi
from tram.phieu.cong_viec import cong_viec_cho
from xu_ly_gia import ket_thuc_bang


def bi(t, bead_id="hr-1"):
    p = dat_phieu(t.kho, "B/claude-2", bead_id=bead_id)
    ket_thuc_bang(t.kho, p, "bi", ly_do="agent", noi_dung="vướng")


def qc_dat(t):
    """Bead hr-1 đã code (c), kiểm lại đạt, QC đạt (q) — ref công bố = q trên remote."""
    c = t.k.day("tram/hr-1", {"src/tom_tat.py": "x = 2\n"}, tu=t.k.main)
    q = t.k.day("tram/hr-1", {F: "qc"}, tu=c)
    nhan(t.kho, "g-1", 1)
    cong_bo(t.kho, 1, c)
    ket_thuc(t.kho, "g-1", 1, commit=c)
    sk(t.kho, "bao.xong", {"giao_id": "g-1", "commit": c, "ban_giao": bg(c)})
    kiem(t.kho, "g-1", c, digest=digest_tieu_chi(["Tên kết thúc 'ỷ' không mất byte"]))
    cong_bo(t.kho, 2, q)
    qc(t.kho, "g-2", c, q)
    return c, q


def test_pha_nhanh_khong_dung_git(tmp_path):
    t = dung(tmp_path, bug(**GIU))
    bi(t)
    t.bo.kho_git = lambda d: (_ for _ in ()).throw(AssertionError("pha nhanh không được chạm kho kiểm"))
    assert vong_nhanh(t.bo)["cong_viec"] == 1
    assert "ly_do: agent-bi" in next(b for b in t.g.beads.values() if b.issue_type == "decision").description


def test_pha_git_xu_ly_xong_va_kiem_lai_pha_nhanh_thi_khong(tmp_path):
    t = dung(tmp_path, bug(**GIU))
    chuan_bi_code_xong(t, {"src/tom_tat.py": "x = 2\n", F: "x", "kiem.sh": "exit 0\n"})
    assert "cong_viec" not in vong_nhanh(t.bo) and len(cong_viec_cho(t.kho)) == 1
    r = vong_git(t.bo)
    assert (r["cong_viec"], r["kiem_lai"]) == (1, 1) and loai(t, "kiem.lai")[0].du_lieu["dat"] is True


def test_fetch_qua_han_chi_dem_loi_khong_chan_escalation(tmp_path, monkeypatch):
    t = dung(tmp_path, bug(**GIU))
    bi(t)
    monkeypatch.setattr(tick, "fetch", lambda kg, **kw: (_ for _ in ()).throw(subprocess.TimeoutExpired("git", 1)))
    r = mot_vong_tick(t.bo)
    assert (r["cong_viec"], r["loi"]) == (1, 1) and t.g.so_lan("tao") == 1


def test_kiem_lai_dung_thu_muc_va_trao_quyen_cua_bo(tmp_path):
    t = dung(tmp_path, bug(**GIU))
    trao = []
    t.bo.thu_muc_kiem, t.bo.trao_quyen = tmp_path / "kiem-ngoai", trao.append
    chuan_bi_code_xong(t, {"src/tom_tat.py": "x = 2\n", F: "x", "kiem.sh": "exit 0\n"})
    assert vong_git(t.bo)["kiem_lai"] == 1 and trao == [tmp_path / "kiem-ngoai" / loai(t, "giao.nhan")[0].du_lieu[
        "giao_id"]]


def test_cot_3_nhanh_bi_day_ngoai_luong(tmp_path):
    t = dung(tmp_path, bug(**GIU))
    _, q = qc_dat(t)
    la = t.k.day("tram/hr-1", {"src/la.py": "x\n"}, tu=q)                # ai đó push thẳng lên nhánh công bố
    assert vong_git(t.bo)["nhanh_bi_day"] == 1 and "nhanh_bi_day" not in vong_git(t.bo)
    esc = next(b for b in t.g.beads.values() if b.issue_type == "decision")
    assert "ly_do: nhanh-bi-day" in esc.description and la in esc.description
    assert t.g.beads["hr-1"].labels == ("cot:ai-lam",)


def test_cot_3_doc_lai_bead_bi_keo_thi_khong_ghi(tmp_path):
    from dataclasses import replace
    t = dung(tmp_path, bug(**GIU))
    qc_dat(t)
    cu = list(t.g.beads.values())
    t.g.beads["hr-1"] = replace(t.g.beads["hr-1"], labels=("cot:can-chot",))      # Đại ca kéo khi pha Git đang chạy
    from tram.giao_viec.git_kiem import fetch
    fetch(t.k.kho)
    assert day_pipeline(t.bo, t.kho, t.da, t.g, cu, set(), t.k.kho, LUC, viec=VIEC_GIT) == {}
    assert t.g.beads["hr-1"].labels == ("cot:can-chot",) and loai(t, "bead.vao_cot_3") == []


def test_thu_chi_ghi_su_kien_suy_tu_beads(tmp_path):
    t = dung(tmp_path, bug(**GIU))
    e = tao_escalation(t.g, t.kho, "hr-codex", t.g.beads["hr-1"], ly_do="agent-bi", cau_hoi="?", giao_id="g-1",
                       nguon="g-1", luc=LUC)
    t.g.dong(e, "Làm cách B")
    bi(t)
    so = len(t.g.goi)
    r = mot_vong_tick(t.bo, thu=True)
    assert r == {"escalation_dong": 1, "chu_ky_moi": 1} and len(cong_viec_cho(t.kho)) == 1
    assert [g for g in t.g.goi[so:] if g[0] != "tat_ca"] == [] and len(ds(t.kho)) > 0
```

`tests/test_hoi_quy_4a2.py` (mới; 9 ca: bs-ecd ×6, bs-s52, queue, gate truyền qua bộ chọn):

```python
"""Ca biên trên main; SQLite/BdGia/remote Git cục bộ, không quota thật."""
import pytest
from dataclasses import replace
from test_pipeline import code_xong, TT, C1, Q1
from su_kien_gia import ds, nhan, cong_bo, ket_thuc, kiem, sk
from kho_phieu_gia import LUC, kho_tam
from test_escalation import moi, tao
from tram.beads.bd import LoiBd
from tram.giao_viec.pipeline import buoc_ke_tiep
from tram.giao_viec.tick_doc import ghi_escalation_dong, mo_chu_ky_con_thieu
from tram.giao_viec.hang_doi import viec_cua_pha


@pytest.mark.parametrize("doi,muon", [("khong", "qc"), ("ref-khac", "code"), ("luot-khac", "code"),
                                      ("digest", "code"), ("tra-ve", "code"), ("qc-dat", "cot_3")])
def test_bs_ecd_qc_cong_bo_roi_thu_hoi(tmp_path, doi, muon):
    from su_kien_gia import qc
    kho = kho_tam(tmp_path)
    code_xong(kho)
    kiem(kho, "g-1", C1)
    nhan(kho, "g-2", 2, buoc="qc")
    cong_bo(kho, 2, Q1)
    ket_thuc(kho, "g-2", 2, ket_thuc="thu_hoi", buoc="qc")
    if doi == "ref-khac":
        cong_bo(kho, 9, "eeeeeee")
    if doi == "luot-khac":
        nhan(kho, "g-3", 3, buoc="qc")
        ket_thuc(kho, "g-3", 3, ket_thuc="thu_hoi", buoc="qc")
    if doi == "tra-ve":
        sk(kho, "cot.tra_ve", {"gop_y": "sửa lại"})
    if doi == "qc-dat":
        qc(kho, "g-2", C1, Q1)
    tt = replace(TT, digest_tieu_chi="sha256:moi") if doi == "digest" else TT
    assert buoc_ke_tiep(ds(kho), tt) == muon


def test_bs_s52_escalation_dong_giua_crash_va_doi_soat(tmp_path):
    g, kho = moi(tmp_path, ra_loi_sau={"tao": 1})
    with pytest.raises(LoiBd):
        tao(g, kho)
    e = next(b.id for b in g.tat_ca() if b.issue_type == "decision")
    g.dong(e, "Đại ca đã trả lời")
    assert tao(g, kho) == e and g.so_lan("tao") == 1
    assert ghi_escalation_dong(kho, "hr-codex", g.tat_ca(), LUC) == 1
    assert mo_chu_ky_con_thieu(kho, "hr-codex", LUC) == 1
    assert tao(g, kho) is None
    assert ghi_escalation_dong(kho, "hr-codex", g.tat_ca(), LUC) == 0
    assert mo_chu_ky_con_thieu(kho, "hr-codex", LUC) == 0


def test_queue_loc_du_an_va_pha_truoc_limit(tmp_path):
    kho = kho_tam(tmp_path)
    with kho.giao_dich() as db:
        db.executemany("INSERT INTO cong_viec_cho(giao_id,du_an,bead_id,ket_thuc,su_kien_id,luc) "
                       "VALUES (?,?,?,?,?,?)", [(f"g-{i}", "khac", "b", "xong", i, "2026-10-13T00:00:00Z")
                                                for i in range(1001)])
        db.execute("INSERT INTO cong_viec_cho(giao_id,du_an,bead_id,ket_thuc,su_kien_id,luc) "
                   "VALUES ('can-xu-ly','hr-codex','hr-1','bi',2000,'2026-10-13T00:00:00Z')")
    assert [v.giao_id for v in viec_cua_pha(kho, "hr-codex", git=False, gioi_han=1)] == ["can-xu-ly"]
    assert viec_cua_pha(kho, "hr-codex", git=True) == []


def test_gate_adr_duoc_noi_vao_bo_chon(tmp_path):
    from giao_viec_gia import dung, bug
    from tram.cau_hinh.du_an import HangRao
    from tram.giao_viec.git_kiem import fetch
    t = dung(tmp_path, bug(description="schema ADR-0083"))
    da = replace(t.da, hang_rao={"schema": HangRao(tu_khoa=("schema",))})
    t.bo.cac_du_an = lambda: [da]
    fetch(t.k.kho)
    assert t.bo.chon("B/claude-1", None) is None and t.g.so_lan("nhan_viec") == 0
    t.bo.adr_hop_le = lambda d, b: True  # CHỈ DÙNG TRONG TEST; không phải adapter được duyệt.
    assert t.bo.chon("B/claude-1", None).bead_id == "hr-1"
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_hoi_quy_4a2.py tests/test_tick_hai_pha.py -q`
Expected: FAIL — `1 error` (`ImportError: cannot import name 'VIEC_GIT' from 'tram.giao_viec.tick_pipeline'`)

- [ ] **Step 3: Viết mã**

`tram/giao_viec/hang_doi.py` (mới — Task 7; lọc trước LIMIT, không để backlog khác pha/dự án chặn G5):

```python
"""Hàng đợi riêng từng dự án/pha. Mọi giá trị dữ liệu dùng SQL parameters."""
from tram.phieu.cong_viec import CongViecCho


def viec_cua_pha(kho, du_an: str, *, git: bool, gioi_han: int = 1000) -> list[CongViecCho]:
    so_sanh = "=" if git else "<>"
    sql = ("SELECT id,giao_id,du_an,bead_id,ket_thuc,su_kien_id,luc FROM cong_viec_cho "
           f"WHERE xong_luc IS NULL AND du_an = ? AND ket_thuc {so_sanh} 'xong' ORDER BY id LIMIT ?")
    return [CongViecCho(*h) for h in kho.db.execute(sql, (du_an, gioi_han))]
```

`tram/giao_viec/pipeline.py` (sửa — bs-ecd; không thay bằng chứng cột 3):

```diff
diff --git a/tram/giao_viec/pipeline.py b/tram/giao_viec/pipeline.py
--- a/tram/giao_viec/pipeline.py
+++ b/tram/giao_viec/pipeline.py
@@ -32,6 +32,18 @@
     return kt.du_lieu.get("commit")
 
 
+def _qc_chua_ket_qua(w: list[SK], kl: SK) -> bool:
+    """Công bố mới nhất thuộc đúng QC mới nhất, sau kiểm lại và đã kết thúc chưa có kết luận."""
+    q = moi_nhat(w, "giao.nhan", lambda s: s.id > kl.id and s.du_lieu.get("buoc") == "qc")
+    cb = moi_nhat(w, "giao.cong_bo")
+    if q is None or cb is None or cb.id <= q.id or cb.du_lieu.get("luot") != q.du_lieu.get("luot"):
+        return False
+    kt = moi_nhat(w, "giao.ket_thuc", lambda s: s.id > cb.id
+                  and s.du_lieu.get("giao_id") == q.du_lieu.get("giao_id")
+                  and s.du_lieu.get("luot") == q.du_lieu.get("luot"))
+    return kt is not None and kt.du_lieu.get("ket_thuc") in {"thu_hoi", "het_han_muc", "bi"}
+
+
 def buoc_ke_tiep(ds: list[SK], tt: TrangThaiBead) -> Buoc:
     if tt.co_phieu or tt.bi_chan or tt.cong_viec_ton or tt.cho_review:          # dòng 1, 2
         return "cho"
@@ -50,6 +62,8 @@
     if (kl_dung and sha is not None and kl.du_lieu["commit"] == sha and ref == sha     # dòng 4
             and qk is None):
         return "cot_3" if tt.la_spike else "qc"
+    if kl_dung and qk is None and not tt.la_spike and _qc_chua_ket_qua(w, kl):
+        return "qc"
     if sha is not None and kl is None:   # dòng 5
         return "kiem_lai"
     return "code"                                                                      # dòng 6
```

**bs-s52:** main đã đối soát đúng dấu thao tác kể cả decision đã đóng. Giữ nguyên mã `escalation.py`; hồi quy trên bảo vệ điều này, không thêm lọc trạng thái `open`.

`tram/giao_viec/tick_cot_3.py` (mới):

```python
"""Vào cột 3 khi chạy thật (4a-2) — trước `vao_cot_3` của 4a-1 kiểm thêm hai điều mà pha Git dài có thể làm cũ:

1. Ref công bố TRÊN REMOTE (kho kiểm vừa `git fetch` đầu pha) đúng bằng commit trong `giao.cong_bo` mới nhất (3a-2
   công bố bằng CAS). Khác = nhánh bị đẩy ngoài luồng → không vào cột 3, escalation `nhanh-bi-day` (G10: PR Đại ca
   tạo từ `tram/<bead>` phải trỏ đúng commit trạm đã kiểm). Một escalation mỗi (chu kỳ ngân sách, SHA remote).
2. Đọc lại bead và sự kiện ngay trước khi ghi nhãn: bead có thể đã bị kéo, bị chặn trong lúc kiểm lại bead khác."""
from datetime import datetime
from pathlib import Path

from tram.beads.bd import LoiBd
from tram.cau_hinh.du_an import DuAn
from tram.giao_viec.bang_chung import vao_cot_3
from tram.giao_viec.dieu_kien import ly_do_khong_giao
from tram.giao_viec.escalation import tao_escalation
from tram.giao_viec.git_kiem import sha_cua
from tram.giao_viec.ngan_sach import bat_dau_chu_ky
from tram.giao_viec.pipeline import buoc_ke_tiep
from tram.giao_viec.su_kien import moi_nhat, su_kien_bead
from tram.giao_viec.ung_vien import trang_thai_bead, viec_ton_cua
from tram.phieu.kho import KhoPhieu


def ten_nhanh(ref: str) -> str:
    return ref.removeprefix("refs/heads/")


def vao_cot_3_an_toan(bd, kho: KhoPhieu, kg: Path, da: DuAn, b, luc: datetime) -> str | None:
    ds = su_kien_bead(kho, da.ten, b.id)
    cb = moi_nhat(ds, "giao.cong_bo")
    if cb is None:
        return None
    tu_xa = sha_cua(kg, f"origin/{ten_nhanh(cb.du_lieu['ref'])}")
    if tu_xa != cb.du_lieu["commit"]:
        cau = (f"Nhánh {cb.du_lieu['ref']} trên remote đang ở {tu_xa or '(không có)'}, khác commit trạm đã công bố "
               f"{cb.du_lieu['commit']}. Đưa nhánh về đúng commit (hoặc trả bead về cột 1) rồi trả lời.")
        return "nhanh_bi_day" if tao_escalation(bd, kho, da.ten, b, ly_do="nhanh-bi-day", cau_hoi=cau, giao_id=None,
                                                 nguon=f"ref-{bat_dau_chu_ky(ds)}-{tu_xa or 'mat'}", luc=luc) else None
    try:
        theo_id = {x.id: x for x in bd.tat_ca()}
    except LoiBd:
        return None
    moi = theo_id.get(b.id)
    if moi is None or ly_do_khong_giao(moi, theo_id, set(), da) is not None or buoc_ke_tiep(
            ds, trang_thai_bead(kho, da.ten, moi, theo_id, viec_ton_cua(kho, da.ten))) != "cot_3":
        return None
    return "cot_3" if vao_cot_3(bd, kho, kg, da, moi, ds, la_spike=moi.issue_type == "spike", luc=luc) else None
```

`tram/giao_viec/tick_pipeline.py` (sửa — bản vá):

```diff
diff --git a/tram/giao_viec/tick_pipeline.py b/tram/giao_viec/tick_pipeline.py
index 0c6557a..0aa3511 100644
--- a/tram/giao_viec/tick_pipeline.py
+++ b/tram/giao_viec/tick_pipeline.py
@@ -1,22 +1,26 @@
 """Vòng tick — phần đẩy pipeline (spec 4 §10 bước 1, §6.2, §6.4, §5.1 điều kiện 9): với mỗi bead trạm đang giữ
 (`in_progress`, assignee trạm) tính `buoc_ke_tiep`: `kiem_lai` → chạy kiểm lại; `cot_3` → vào cột 3; `code`/`qc`
-mà `not du_mot_phieu` → escalation `het-ngan-sach`. Dự án thiếu `moi_truong_kiem` → MỘT escalation mở mỗi dự án."""
+mà `not du_mot_phieu` → escalation `het-ngan-sach`. Dự án thiếu `moi_truong_kiem` → MỘT escalation mở mỗi dự án.
+4a-2: `viec` chọn phần việc theo pha — pha nhanh chỉ `het_ngan_sach` (G5), pha Git làm phần còn lại."""
 from datetime import datetime
 from pathlib import Path
 
 from tram.cau_hinh.du_an import DuAn
 from tram.duong_dan import tram_home
-from tram.giao_viec.bang_chung import vao_cot_3
 from tram.giao_viec.dieu_kien import ASSIGNEE, ly_do_khong_giao
 from tram.giao_viec.escalation import tao_escalation
 from tram.giao_viec.kiem_lai import kiem_lai
 from tram.giao_viec.ngan_sach import bat_dau_chu_ky, du_mot_phieu, ngan_sach_phieu
 from tram.giao_viec.pipeline import buoc_ke_tiep, sha_code_hop_le
 from tram.giao_viec.su_kien import SK, cua_so, ghi_mot_lan, moi_nhat, su_kien_bead
+from tram.giao_viec.tick_cot_3 import vao_cot_3_an_toan
 from tram.giao_viec.tieu_chi import digest_tieu_chi
 from tram.giao_viec.ung_vien import trang_thai_bead, viec_ton_cua
 from tram.phieu.kho import KhoPhieu
 
+VIEC_NHANH = frozenset({"het_ngan_sach"})
+VIEC_GIT = frozenset({"kiem_lai", "cot_3", "moi_truong"})
+
 
 def _esc_moi_truong_dang_mo(kho: KhoPhieu, du_an: str) -> bool:
     tao = {r[0] for r in kho.db.execute("SELECT json_extract(du_lieu, '$.escalation_id') FROM su_kien WHERE du_an = ?"
@@ -34,8 +38,9 @@ def _kiem_lai(bo, kho: KhoPhieu, da: DuAn, bd, b, ds: list[SK], kg: Path, luc: d
     if p.can_lenh_kiem and bo.boc is None:
         return "cho_boc"                                 # chưa có principal tram-kiem (S6) — không chạy dưới quyền trạm
     kq = kiem_lai(kg, da, giao_id=p.giao_id, commit=sha, lenh_kiem=list(p.lenh_kiem), lenh_cho_phep=list(p.lenh_cho_phep),
-                  chay_lenh=p.can_lenh_kiem, thu_muc=tram_home() / "kiem", thu_muc_log=tram_home() / "log" / "kiem-lai",
-                  boc=bo.boc or (lambda a: a), env_goc=bo.env_goc)
+                  chay_lenh=p.can_lenh_kiem, thu_muc=bo.thu_muc_kiem or tram_home() / "kiem",
+                  thu_muc_log=tram_home() / "log" / "kiem-lai", boc=bo.boc or (lambda a: a), env_goc=bo.env_goc,
+                  trao_quyen=bo.trao_quyen, kill=bo.kill)
     if kq.loi is not None:
         tao_escalation(bd, kho, da.ten, b, ly_do=kq.loi, cau_hoi="", giao_id=p.giao_id, nguon=f"kl-{sha}", luc=luc)
         if kq.loi == "thieu-moi-truong-kiem":
@@ -48,11 +53,11 @@ def _kiem_lai(bo, kho: KhoPhieu, da: DuAn, bd, b, ds: list[SK], kg: Path, luc: d
 
 
 def day_pipeline(bo, kho: KhoPhieu, da: DuAn, bd, beads: list, san_sang: set[str], kg: Path | None,
-                 luc: datetime) -> dict[str, int]:
+                 luc: datetime, *, viec: frozenset[str] = VIEC_NHANH | VIEC_GIT) -> dict[str, int]:
     theo_id, ton, dem = {b.id: b for b in beads}, viec_ton_cua(kho, da.ten), {}
     for b in beads:
         ly = ly_do_khong_giao(b, theo_id, san_sang, da)
-        if ly == "thieu-moi-truong-kiem" and not _esc_moi_truong_dang_mo(kho, da.ten):
+        if ly == "thieu-moi-truong-kiem" and "moi_truong" in viec and not _esc_moi_truong_dang_mo(kho, da.ten):
             tao_escalation(bd, kho, da.ten, b, ly_do=ly, cau_hoi="", giao_id=None, nguon=f"du-an-{luc:%Y%m%d%H%M}",
                            luc=luc)
             dem["escalation"] = dem.get("escalation", 0) + 1
@@ -60,12 +65,12 @@ def day_pipeline(bo, kho: KhoPhieu, da: DuAn, bd, beads: list, san_sang: set[str
             continue
         ds = su_kien_bead(kho, da.ten, b.id)
         buoc, kq = buoc_ke_tiep(ds, trang_thai_bead(kho, da.ten, b, theo_id, ton)), None
-        if buoc == "kiem_lai" and kg is not None:
+        if buoc == "kiem_lai" and kg is not None and "kiem_lai" in viec:
             kq = _kiem_lai(bo, kho, da, bd, b, ds, kg, luc)
-        elif buoc == "cot_3" and kg is not None:
-            kq = "cot_3" if vao_cot_3(bd, kho, kg, da, b, ds, la_spike=b.issue_type == "spike", luc=luc) else None
-        elif buoc in ("code", "qc") and not du_mot_phieu(kho, ds, ngan_sach_phieu(buoc, da.giao.ngan_sach),
-                                                         da.giao.ngan_sach.bead):
+        elif buoc == "cot_3" and kg is not None and "cot_3" in viec:
+            kq = vao_cot_3_an_toan(bd, kho, kg, da, b, luc)
+        elif buoc in ("code", "qc") and "het_ngan_sach" in viec and not du_mot_phieu(
+                kho, ds, ngan_sach_phieu(buoc, da.giao.ngan_sach), da.giao.ngan_sach.bead):
             kq = "het_ngan_sach" if tao_escalation(bd, kho, da.ten, b, ly_do="het-ngan-sach", cau_hoi="", giao_id=None,
                                                    nguon=f"ns-{bat_dau_chu_ky(ds)}", luc=luc) else None
         if kq:
```

`tram/giao_viec/tick.py` (sửa — bản vá):

```diff
diff --git a/tram/giao_viec/tick.py b/tram/giao_viec/tick.py
--- a/tram/giao_viec/tick.py
+++ b/tram/giao_viec/tick.py
@@ -1,8 +1,11 @@
-"""`tram giao tick` — một vòng (spec 4 §10), idempotent theo ID nguồn. Lịch 2 phút trong tram-api: lát sau.
+"""`tram giao tick` — vòng tick (spec 4 §10), idempotent theo ID nguồn; 4a-2 tách HAI PHA chạy ở hai luồng riêng:
 
-Thứ tự mỗi dự án: (2) `escalation.dong` · (3) `bead.dong` · chu kỳ ngân sách mới — chỉ ghi sự kiện, chạy cả khi
-estop; estop bật thì DỪNG ở đây (không ghi beads, không chạy lệnh). Sau đó: `git fetch` kho kiểm · (0) công việc
-chờ + câu hỏi của agent · (1) đẩy pipeline (kiểm lại, cột 3, hết ngân sách, thiếu môi trường kiểm)."""
+- `vong_nhanh` (G5 ≤ 3 phút — không Git, không chạy lệnh): (2) `escalation.dong` · (3) `bead.dong` · chu kỳ ngân
+  sách mới — chỉ ghi sự kiện, chạy cả khi estop; estop bật (hoặc `thu`) thì DỪNG ở đây. Sau đó: công việc chờ KHÔNG
+  phải `xong` (bí, hết hạn mức, thu hồi), câu hỏi của agent, (1) hết ngân sách.
+- `vong_git` (có thể dài — kiểm lại tới 15 phút/lệnh): `git fetch` kho kiểm (có hạn giờ) · công việc `xong` (xét
+  bàn giao, QC) · kiểm lại · cột 3 · thiếu môi trường kiểm. Estop bật → không làm gì.
+`mot_vong_tick` = hai pha nối tiếp (lệnh `tram giao tick`, test). Một dự án lỗi không chặn dự án khác."""
 import subprocess
 from collections import Counter
 from contextlib import closing
@@ -11,14 +14,15 @@
 from tram.chu import estop
 from tram.giao_viec.git_kiem import fetch
 from tram.giao_viec.tick_doc import ghi_bead_dong, ghi_escalation_dong, mo_chu_ky_con_thieu
-from tram.giao_viec.tick_pipeline import day_pipeline
+from tram.giao_viec.tick_pipeline import VIEC_GIT, VIEC_NHANH, day_pipeline
 from tram.giao_viec.xu_ly_viec import escalation_cau_hoi, xu_ly_cong_viec
-from tram.phieu.cong_viec import cong_viec_cho
+from tram.giao_viec.hang_doi import viec_cua_pha
 
-LOI = (LoiBd, subprocess.CalledProcessError, OSError)
+LOI = (LoiBd, subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError)
+FETCH_GIAY = 120
 
 
-def _mot_du_an(bo, kho, da, luc, dung: bool, dem: Counter) -> None:
+def _nhanh(bo, kho, da, luc, dung: bool, dem: Counter) -> None:
     bd = bo.tao_bd(da)
     beads = bd.tat_ca()
     dem["escalation_dong"] += ghi_escalation_dong(kho, da.ten, beads, luc)
@@ -26,23 +30,48 @@
     dem["chu_ky_moi"] += mo_chu_ky_con_thieu(kho, da.ten, luc)
     if dung:
         return
-    kg = bo.kho_git(da)
-    if kg is not None:
-        fetch(kg)
-    for cv in cong_viec_cho(kho, 1000):
-        if cv.du_an == da.ten:
-            dem["cong_viec"] += xu_ly_cong_viec(kho, cv, du_an=da, bd=bd, kho_git=kg, luc=luc)
+    for cv in viec_cua_pha(kho, da.ten, git=False):
+        dem["cong_viec"] += xu_ly_cong_viec(kho, cv, du_an=da, bd=bd, kho_git=None, luc=luc)
     dem["cau_hoi"] += escalation_cau_hoi(kho, da, bd, luc)
-    dem.update(day_pipeline(bo, kho, da, bd, bd.tat_ca(), bd.san_sang(), kg, luc))
+    dem.update(day_pipeline(bo, kho, da, bd, bd.tat_ca(), bd.san_sang(), None, luc, viec=VIEC_NHANH))
 
 
-def mot_vong_tick(bo) -> dict[str, int]:
-    """Một dự án lỗi (`bd`, git) không chặn dự án khác; lỗi được đếm, vòng sau làm lại."""
-    luc, dung, dem = bo.dong_ho(), estop.dang_bat(), Counter()
+def _git(bo, kho, da, luc, dem: Counter) -> None:
+    kg = bo.kho_git(da)
+    if kg is None:
+        return                                           # chưa có kho kiểm: công việc `xong` để nguyên (4a-1 G15)
+    fetch(kg, thoi_gian_cho=FETCH_GIAY)
+    bd = bo.tao_bd(da)
+    for cv in viec_cua_pha(kho, da.ten, git=True):
+        dem["cong_viec"] += xu_ly_cong_viec(kho, cv, du_an=da, bd=bd, kho_git=kg, luc=luc)
+    dem.update(day_pipeline(bo, kho, da, bd, bd.tat_ca(), bd.san_sang(), kg, luc, viec=VIEC_GIT))
+
+
+def _vong(bo, lam) -> dict[str, int]:
+    luc, dem = bo.dong_ho(), Counter()
     with closing(bo.mo_kho()) as kho:
         for da in bo.cac_du_an():
             try:
-                _mot_du_an(bo, kho, da, luc, dung, dem)
+                lam(kho, da, luc, dem)
             except LOI:
                 dem["loi"] += 1
     return {k: v for k, v in dem.items() if v}
+
+
+def vong_nhanh(bo, *, thu: bool = False) -> dict[str, int]:
+    """`thu` = như estop: chỉ ghi sự kiện suy từ beads — không ghi beads, không chạy lệnh."""
+    dung = thu or estop.dang_bat()
+    return _vong(bo, lambda kho, da, luc, dem: _nhanh(bo, kho, da, luc, dung, dem))
+
+
+def vong_git(bo) -> dict[str, int]:
+    if estop.dang_bat():
+        return {}
+    return _vong(bo, lambda kho, da, luc, dem: _git(bo, kho, da, luc, dem))
+
+
+def mot_vong_tick(bo, *, thu: bool = False) -> dict[str, int]:
+    dem = Counter(vong_nhanh(bo, thu=thu))
+    if not thu:
+        dem.update(vong_git(bo))
+    return {k: v for k, v in dem.items() if v}
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_hoi_quy_4a2.py tests/test_tick_hai_pha.py tests/test_tick.py tests/test_kich_ban_4a1.py tests/test_nhanh_bi_day.py -q`
Expected: PASS; file hồi quy mới9ca, mọi test liên quan cũ phải pass

Run: `uv run pytest -q`
Expected: `N₀ + 53 passed`

- [ ] **Step 5: Commit**

```bash
git add tram/giao_viec/hang_doi.py tram/giao_viec/pipeline.py tests/test_hoi_quy_4a2.py tram/giao_viec/tick_cot_3.py tram/giao_viec/tick.py tram/giao_viec/tick_pipeline.py tests/test_tick_hai_pha.py
git commit -m "feat(giao-viec): vòng tick hai pha (nhanh không Git / Git), kiểm lại dưới principal, cột 3 kiểm ref công bố trên remote (spec 4 §10, §6.4; G5)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 8: Hai luồng tick, khoá mỗi pha, lịch nhịp cố định (G5)

**Độ khó:** `kho` · **Đợt:** 3 · **Song song với:** — · **Phải xong trước:** Task 7

**Files:**
- Create: `tram/giao_viec/luong.py`
- Test: `tests/test_luong_giao.py` (mới)

**Interfaces:**
- Consumes: `vong_nhanh`, `vong_git` (Task 7); `tram_home()`; test: `bi` (`test_tick_hai_pha.py`), `GIU`, `chuan_bi_code_xong`, `loai`, `F`.
- Produces: `KHOA_NHANH`, `KHOA_GIT`, `giu_khoa(ten) -> ContextManager[bool]`, `chay_vong(khoa, lam) -> dict | None`, `lap(dung, lam, chu_ky, ten, *, dong_ho)`, `bat_dau_luong_giao(bo, dung, *, chu_ky) -> list[Thread]` (tên `tram-giao-nhanh`, `tram-giao-git`). Test: `BdKhoa(g)`, `cho_toi(dieu_kien, giay=10.0)` (`tests/test_luong_giao.py`).

- [ ] **Step 1: Viết test thất bại**

`tests/test_luong_giao.py` (mới):

```python
"""Hai luồng tick (spec 4 §10 "ràng buộc lúc nối 4a-2"; G5): bí của agent thành escalation trong khi kiểm lại dài
đang chạy; khoá mỗi pha; lịch nhịp cố định; khởi động lại giữa kiểm lại thì vòng sau kiểm lại lại, không trùng.
Kiểm lại "dài 15 phút" giả bằng `boc` chờ một Event — không ngủ thật."""
import threading
import time

import pytest

from giao_viec_gia import bug, dung
from test_tick import GIU, chuan_bi_code_xong, loai
from test_tick_hai_pha import bi
from test_xet_xong import F
from tram.giao_viec.luong import KHOA_GIT, KHOA_NHANH, bat_dau_luong_giao, chay_vong, giu_khoa, lap
from tram.giao_viec.tick import vong_git


class BdKhoa:
    """BdGia dùng chung giữa hai luồng tick (CHỈ DÙNG TRONG TEST): mọi lời gọi tuần tự hoá."""

    def __init__(self, g):
        self._g, self._k = g, threading.RLock()

    def __getattr__(self, ten):
        f = getattr(self._g, ten)

        def goi(*a, **kw):
            with self._k:
                return f(*a, **kw)
        return goi if callable(f) else f


def cho_toi(dieu_kien, giay: float = 10.0) -> bool:
    het = time.monotonic() + giay
    while time.monotonic() < het:
        if dieu_kien():
            return True
        time.sleep(0.02)
    return False


class DungGia:
    def __init__(self, n):
        self.n, self.cho = n, []

    def is_set(self):
        return len(self.cho) >= self.n

    def wait(self, giay):
        self.cho.append(giay)


def test_lap_giu_nhip_co_dinh_va_song_qua_loi(capsys):
    gio, buoc = [0.0], iter([10.0, 200.0, 5.0])

    def lam():
        gio[0] += (x := next(buoc))
        if x == 5.0:
            raise RuntimeError("lỗi một vòng")

    d = DungGia(3)
    lap(d, lam, 120, "thu", dong_ho=lambda: gio[0])
    assert d.cho == [110.0, 0.0, 115.0] and "[thu] lỗi: RuntimeError" in capsys.readouterr().err


def test_khoa_mot_vong_moi_pha():
    with giu_khoa(KHOA_GIT) as duoc:
        assert duoc and chay_vong(KHOA_GIT, lambda: {"x": 1}) is None
        assert chay_vong(KHOA_NHANH, lambda: {"x": 1}) == {"x": 1}
    assert chay_vong(KHOA_GIT, lambda: {}) == {}


def test_g5_bi_thanh_escalation_trong_khi_kiem_lai_dai(tmp_path):
    vao, tha = threading.Event(), threading.Event()

    def boc(argv):
        vao.set()
        tha.wait(20)                                    # "suite 15 phút" của bead hr-1
        return argv

    t = dung(tmp_path, bug(**GIU), bug("hr-2", **GIU), boc=boc)
    g = BdKhoa(t.g)
    t.bo.tao_bd = lambda d: g
    chuan_bi_code_xong(t, {"src/tom_tat.py": "x = 2\n", F: "x", "kiem.sh": "exit 0\n"})
    dung_ev = threading.Event()
    luong = bat_dau_luong_giao(t.bo, dung_ev, chu_ky=0.05)
    try:
        assert vao.wait(10)                             # luồng Git đang kẹt trong kiểm lại
        bi(t, "hr-2")
        assert cho_toi(lambda: any("bead_goc: hr-2" in b.description for b in g.tat_ca()
                                   if b.issue_type == "decision"))
        assert not tha.is_set() and loai(t, "kiem.lai") == []
        tha.set()
        assert cho_toi(lambda: len(loai(t, "kiem.lai")) == 1)
    finally:
        tha.set()
        dung_ev.set()
        for x in luong:
            x.join(timeout=10)
    assert not any(x.is_alive() for x in luong) and len(loai(t, "kiem.lai")) == 1


def test_khoi_dong_lai_giua_kiem_lai_thi_vong_sau_kiem_lai_lai(tmp_path, tram_home_tam):
    lan = []

    def boc(argv):
        lan.append(argv)
        if len(lan) == 1:
            raise RuntimeError("tram-api tắt giữa chừng")
        return argv

    t = dung(tmp_path, bug(**GIU), boc=boc)
    chuan_bi_code_xong(t, {"src/tom_tat.py": "x = 2\n", F: "x", "kiem.sh": "exit 0\n"})
    with pytest.raises(RuntimeError):
        chay_vong(KHOA_GIT, lambda: vong_git(t.bo))
    assert loai(t, "kiem.lai") == [] and list((tram_home_tam / "kiem").iterdir()) == []
    assert chay_vong(KHOA_GIT, lambda: vong_git(t.bo))["kiem_lai"] == 1
    assert "kiem_lai" not in chay_vong(KHOA_GIT, lambda: vong_git(t.bo)) and len(loai(t, "kiem.lai")) == 1
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_luong_giao.py -q`
Expected: FAIL — `1 error` (`ModuleNotFoundError: No module named 'tram.giao_viec.luong'`)

- [ ] **Step 3: Viết mã**

`tram/giao_viec/luong.py` (mới):

```python
"""Hai luồng tick trong tiến trình tram-api (spec 4 §10; G5 ≤ 3 phút): `tram-giao-nhanh` (escalation, câu hỏi, hết
ngân sách — không bao giờ chờ Git hay lệnh kiểm) và `tram-giao-git` (fetch, xét `bao.xong`, kiểm lại tới 15 phút/lệnh,
cột 3). Lịch theo nhịp cố định: vòng sau bắt đầu `chu_ky` giây sau khi vòng trước BẮT ĐẦU (vòng dài hơn thì chạy
ngay) → bí/câu hỏi được xử lý trong ≤ chu_ky + một vòng nhanh. Khoá file (`flock`) mỗi pha giữ một vòng trên cả máy:
`tram giao tick` chạy tay song song với tram-api không làm trùng việc (khoá tự nhả khi tiến trình chết)."""
import fcntl
import sys
import threading
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager

from tram.duong_dan import tram_home
from tram.giao_viec.tick import vong_git, vong_nhanh

KHOA_NHANH, KHOA_GIT = "giao-nhanh.lock", "giao-git.lock"


@contextmanager
def giu_khoa(ten: str) -> Iterator[bool]:
    p = tram_home() / "khoa" / ten
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a") as f:
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            yield False
            return
        try:
            yield True
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


def chay_vong(khoa: str, lam: Callable[[], dict]) -> dict | None:
    """None = pha này đang có vòng khác chạy (luồng của tram-api hoặc lệnh tay)."""
    with giu_khoa(khoa) as duoc:
        return lam() if duoc else None


def lap(dung: threading.Event, lam: Callable[[], object], chu_ky: float, ten: str, *,
        dong_ho: Callable[[], float] = time.monotonic) -> None:
    while not dung.is_set():
        bat_dau = dong_ho()
        try:
            lam()
        except Exception as e:                          # noqa: BLE001 — ghi stderr, vòng sau làm lại (idempotent)
            print(f"[{ten}] lỗi: {type(e).__name__}: {e}", file=sys.stderr, flush=True)
        dung.wait(max(0.0, chu_ky - (dong_ho() - bat_dau)))


def bat_dau_luong_giao(bo, dung: threading.Event, *, chu_ky: float) -> list[threading.Thread]:
    ra = []
    for ten, khoa, pha in (("tram-giao-nhanh", KHOA_NHANH, lambda: vong_nhanh(bo)),
                           ("tram-giao-git", KHOA_GIT, lambda: vong_git(bo))):
        t = threading.Thread(target=lap, args=(dung, lambda k=khoa, p=pha: chay_vong(k, p), chu_ky, ten),
                             name=ten, daemon=True)
        t.start()
        ra.append(t)
    return ra
```

- [ ] **Step 4: Chạy, thấy pass** (chạy 3 lần — test có luồng)

Run: `for i in 1 2 3; do uv run pytest tests/test_luong_giao.py -q; done`
Expected: `4 passed` cả 3 lần

Run: `uv run pytest -q`
Expected: `N₀ + 57 passed`

- [ ] **Step 5: Commit**

```bash
git add tram/giao_viec/luong.py tests/test_luong_giao.py
git commit -m "feat(giao-viec): hai luồng tick trong tram-api, khoá flock mỗi pha, nhịp cố định — bí thành escalation khi kiểm lại dài (spec 4 §10; G5)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 9: Nối bộ giao việc vào tram-api

**Độ khó:** `kho` · **Đợt:** 4 · **Song song với:** — · **Phải xong trước:** Task 1, 4, 8

**Files:**
- Create: `tram/giao_viec/noi_that.py`
- Modify (chèn theo mốc): `tram/api/phu_thuoc.py`, `tram/api/tho.py`, `tram/cli_dich_vu.py`
- Test: `tests/test_noi_giao_viec.py` (mới)

**Interfaces:**
- Consumes: `CauHinhGiaoViec`, `nap_cau_hinh_giao_viec`, `PrincipalKiem` (Task 1); `BoGiaoViec(…, doc_beads, trao_quyen, thu_muc_kiem)`, `DocBeads` (Task 4); `bat_dau_luong_giao` (Task 8); `Bd`, `liet_ke_du_an`, `nap_du_an`, `mo_kho_phieu`; test: `tao_pt`, `tao_tram`, `de_xuat`, `dung`, `bug`.
- Produces: `cac_du_an_that(thu_muc=None) -> list[DuAn]`, `dung_bo_that(cg, ch, *, bo_dem=None, thu_muc_du_an=None) -> BoGiaoViec`, `an_toan(ham, mac_dinh, ten) -> Callable`, `noi_giao_viec(pt, dung, *, cg=None, tao_bo=dung_bo_that) -> (PhuThuocApi, list[Thread])`. `PhuThuocApi` thêm `con_hop_le_phieu`, `bo_giao` (G17); router `/api/tho/nhip` truyền `con_hop_le=pt.con_hop_le_phieu`; `tram api` gọi `noi_giao_viec` và `join` luồng khi thoát.

- [ ] **Step 1: Viết test thất bại**

`tests/test_noi_giao_viec.py` (mới):

```python
"""Nối bộ giao việc vào tram-api (spec 4 §13; 3a-1 G11): chỉ khi `giao_viec.bat`; router nhịp tim truyền
`con_hop_le`; lỗi phần 4 không làm hỏng nhịp tim. Không chạy `bd` thật: bộ giả, dự án trong thư mục tạm."""
import threading
from pathlib import Path

from api_gia import tao_pt
from giao_viec_gia import bug, dung
from phieu_gia import de_xuat
from tho_api_gia import tao_tram
from tram.cau_hinh.giao_viec import CauHinhGiaoViec
from tram.giao_viec.noi_that import an_toan, dung_bo_that, noi_giao_viec
from tram.giao_viec.principal_kiem import PrincipalKiem

PK = PrincipalKiem("tram-kiem", ("/usr/bin/sudo", "-n", "-u", "tram-kiem", "--"), ("/usr/local/libexec/trao",))
NHIP = {"khe_id": "B/claude-1", "buoc_tho": "ranh"}


def test_tat_thi_chi_gan_bo_giao(tmp_path):
    t = dung(tmp_path, bug())
    pt, luong = noi_giao_viec(tao_pt(tmp_path, {}), threading.Event(), cg=CauHinhGiaoViec(),
                              tao_bo=lambda cg, ch, bo_dem: t.bo)
    assert (pt.bo_giao, pt.chon_phieu, luong) == (t.bo, None, [])


def test_bat_thi_noi_chon_con_hop_le_va_hai_luong(tmp_path):
    t = dung(tmp_path, bug())
    t.bo.cac_du_an = lambda: []
    dung_ev, nhan = threading.Event(), []
    cg = CauHinhGiaoViec(bat=True, chu_ky_giay=30, thu_muc_kiem=tmp_path / "k", principal_kiem=PK)
    pt, luong = noi_giao_viec(tao_pt(tmp_path, {}), dung_ev, cg=cg,
                              tao_bo=lambda cg, ch, bo_dem: nhan.append(bo_dem) or t.bo)
    try:
        assert pt.bo_giao is t.bo and nhan[0] is not None
        assert pt.chon_phieu("B/claude-1", None) is None and pt.con_hop_le_phieu(de_xuat()) is False
        assert sorted(x.name for x in luong) == ["tram-giao-git", "tram-giao-nhanh"]
    finally:
        dung_ev.set()
        for x in luong:
            x.join(timeout=10)
    assert not any(x.is_alive() for x in luong)


def test_loi_phan_4_khong_lam_hong_nhip(capsys):
    def no(*a):
        raise RuntimeError("bd treo")
    assert an_toan(no, None, "chon")("B/claude-1", None) is None and an_toan(no, False, "con_hop_le")(1) is False
    assert "[giao-viec] chon: RuntimeError" in capsys.readouterr().err


def test_router_nhip_truyen_con_hop_le(tmp_path):
    t = tao_tram(tmp_path, chon=lambda khe, hm: de_xuat())
    t.app.state.pt.con_hop_le_phieu = lambda d: False
    assert t.goi("POST", "/api/tho/nhip", json_body=NHIP).json() == {"tiep_tuc": True, "phieu": None}
    t.app.state.pt.con_hop_le_phieu = lambda d: True
    assert t.goi("POST", "/api/tho/nhip", json_body=NHIP).json()["phieu"]["bead_id"] == "hr-6xe1"


def test_dung_bo_that_noi_principal_va_bo_qua_du_an_hong(tmp_path, capsys):
    (tmp_path / "du-an").mkdir()
    (tmp_path / "du-an" / "hr-x.yaml").write_text(f"ten: hr-x\nduong_dan: {tmp_path}\n")
    (tmp_path / "du-an" / "hong.yaml").write_text("ten: khac\nduong_dan: /x\n")
    (tmp_path / "du-an" / "_mau.yaml").write_text("ten: _mau\n")
    cg = CauHinhGiaoViec(bat=True, thu_muc_kiem=tmp_path / "k", principal_kiem=PK)
    bo = dung_bo_that(cg, tao_pt(tmp_path, {}).cau_hinh, thu_muc_du_an=tmp_path / "du-an")
    assert [d.ten for d in bo.cac_du_an()] == ["hr-x"] and "bỏ qua dự án hong" in capsys.readouterr().err
    assert bo.boc(["sh", "kiem.sh"]) == [*PK.boc, "sh", "kiem.sh"] and bo.trao_quyen == PK.trao
    assert bo.kill == PK.kill_nhom
    assert bo.thu_muc_kiem == tmp_path / "k" and bo.doc_beads is None
    assert bo.tao_bd(bo.cac_du_an()[0]).actor == "tram/giao-viec" and Path(bo.tao_bd(bo.cac_du_an()[0]).repo) == tmp_path
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_noi_giao_viec.py -q`
Expected: FAIL — `1 error` (`ModuleNotFoundError: No module named 'tram.giao_viec.noi_that'`)

- [ ] **Step 3: Viết mã**

`tram/giao_viec/noi_that.py` (mới):

```python
"""Nối bộ giao việc vào tram-api (spec 4 §10, §13; 3a-1 G11) — CHỈ khi `giao_viec.bat: true` (sau mọi cổng):
`chon_phieu` = `bo.chon` và `con_hop_le_phieu` = `bo.con_hop_le` (router `/api/tho/nhip` truyền vào `cap_phieu`),
bọc an toàn — lỗi của phần 4 thành "không phát phiếu", không thành HTTP 500; hai luồng tick. `bo_giao` luôn được
gắn (cả khi tắt) để dashboard đọc lý do không giao. Dựng `BoGiaoViec` không gọi `bd`/Git nào."""
import os
import sys
import threading
from collections.abc import Callable
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

import yaml

from tram.cau_hinh.giao_viec import CauHinhGiaoViec, nap_cau_hinh_giao_viec
from tram.cau_hinh.tram import CauHinhTram
from tram.giao_viec.bo import BoGiaoViec
from tram.giao_viec.dieu_kien import ASSIGNEE
from tram.giao_viec.doc_beads import DocBeads
from tram.giao_viec.luong import bat_dau_luong_giao


def _bao(ten: str, e: Exception) -> None:
    print(f"[giao-viec] {ten}: {type(e).__name__}: {e}", file=sys.stderr, flush=True)


def cac_du_an_that(thu_muc: Path | None = None) -> list:
    """Mọi `du-an/<ten>.yaml` (bỏ tên bắt đầu `_`); một file hỏng chỉ làm dự án đó bị bỏ qua."""
    from tram.cau_hinh.du_an import liet_ke_du_an, nap_du_an
    ra = []
    for ten in liet_ke_du_an(thu_muc):
        if ten.startswith("_"):
            continue
        try:
            ra.append(nap_du_an(ten, thu_muc=thu_muc))
        except (ValueError, OSError, KeyError, AttributeError, yaml.YAMLError) as e:
            _bao(f"bỏ qua dự án {ten}", e)
    return ra


def dung_bo_that(cg: CauHinhGiaoViec, ch: CauHinhTram, *, bo_dem=None,
                 thu_muc_du_an: Path | None = None) -> BoGiaoViec:
    from tram.beads.bd import Bd
    from tram.phieu.kho import mo_kho_phieu
    pk = cg.principal_kiem
    return BoGiaoViec(cac_du_an=lambda: cac_du_an_that(thu_muc_du_an),
                      tao_bd=lambda da: Bd(da.duong_dan, actor=ASSIGNEE), mo_kho=mo_kho_phieu, ch=ch,
                      dong_ho=lambda: datetime.now(timezone.utc), boc=pk.boc_lenh if pk else None,
                      trao_quyen=pk.trao if pk and pk.trao_quyen else None,
                      kill=pk.kill_nhom if pk else _kill_nhom,
                      doc_beads=DocBeads(bo_dem) if bo_dem is not None else None, thu_muc_kiem=cg.thu_muc_kiem)


def an_toan(ham: Callable, mac_dinh, ten: str) -> Callable:
    def boc(*a):
        try:
            return ham(*a)
        except Exception as e:                       # noqa: BLE001 — nhịp tim không được hỏng vì phần 4
            _bao(ten, e)
            return mac_dinh
    return boc


def noi_giao_viec(pt, dung: threading.Event, *, cg: CauHinhGiaoViec | None = None,
                  tao_bo: Callable = dung_bo_that) -> tuple[object, list[threading.Thread]]:
    cg = cg or nap_cau_hinh_giao_viec()
    bo = tao_bo(cg, pt.cau_hinh, bo_dem=pt.bo_dem)
    if not cg.bat:
        return replace(pt, bo_giao=bo), []
    luong = bat_dau_luong_giao(bo, dung, chu_ky=cg.chu_ky_giay)
    return replace(pt, bo_giao=bo, chon_phieu=an_toan(bo.chon, None, "chon"),
                   con_hop_le_phieu=an_toan(bo.con_hop_le, False, "con_hop_le")), luong
```

`tram/api/phu_thuoc.py`, `tram/api/tho.py`, `tram/cli_dich_vu.py` (sửa — chèn theo mốc; nhiều plan đã sửa các file này nên không dùng bản vá):

```bash
uv run python - <<'EOF'
from pathlib import Path


def chen(p: str, moc: str, moi: str) -> None:
    f = Path(p)
    s = f.read_text(encoding="utf-8")
    assert s.count(moc) == 1, f"{p}: không thấy đúng một mốc {moc[:50]!r} — dừng, báo người điều phối"
    f.write_text(s.replace(moc, moi), encoding="utf-8")


s = Path("tram/api/phu_thuoc.py").read_text(encoding="utf-8")
dong = [x for x in s.splitlines(keepends=True) if x.startswith("    chon_phieu: Callable | None = None")]
assert len(dong) == 1, "không thấy đúng một dòng `chon_phieu` trong PhuThuocApi — dừng, báo người điều phối"
chen("tram/api/phu_thuoc.py", dong[0], dong[0]
     + "    con_hop_le_phieu: Callable = lambda d: True          # 4a-2: phần 4 kiểm lại trong giao dịch cấp phiếu\n"
     + "    bo_giao: object | None = None                        # 4a-2: BoGiaoViec — dashboard đọc lý do không giao, PR\n")
chen("tram/api/tho.py", "chon=pt.chon_phieu))",
     "chon=pt.chon_phieu,\n                                          con_hop_le=pt.con_hop_le_phieu))")
chen("tram/cli_dich_vu.py", "    try:                                     # kênh ghi",
     "    from tram.giao_viec.noi_that import noi_giao_viec\n"
     "    pt, luong_giao = noi_giao_viec(phu_thuoc_that(), dung)      # 4a-2: chỉ phát phiếu/chạy tick khi giao_viec.bat\n"
     "    try:                                     # kênh ghi")
chen("tram/cli_dich_vu.py", "chay_api(tao_app(phu_thuoc_that(), cong=args.cong)",
     "chay_api(tao_app(pt, cong=args.cong)")
chen("tram/cli_dich_vu.py", "        canh.join(timeout=10)\n",
     "        canh.join(timeout=10)\n        for t in luong_giao:\n            t.join(timeout=10)\n")
print("đã chèn 4a-2 Task 9")
EOF
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_noi_giao_viec.py tests/test_api_tho.py tests/test_tho_lenh.py -q`
Expected: `17 passed`

Run: `uv run pytest -q`
Expected: `N₀ + 62 passed`

- [ ] **Step 5: Commit**

```bash
git add tram/giao_viec/noi_that.py tram/api/phu_thuoc.py tram/api/tho.py tram/cli_dich_vu.py tests/test_noi_giao_viec.py
git commit -m "feat(giao-viec): nối bộ giao việc vào tram-api — chon/con_hop_le qua nhịp tim, hai luồng tick, chỉ khi giao_viec.bat (spec 4 §10, §13; 3a-1 G11)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 10: Lệnh `tram giao tick|kho-kiem|kiem` + kiểm sẵn sàng

**Độ khó:** `de` · **Đợt:** 5 · **Song song với:** Task 11, 12 · **Phải xong trước:** Task 1, 2, 3, 9

**Files:**
- Create: `tram/giao_viec/kiem_san_sang.py`
- Create: `tram/giao_viec/lenh.py`
- Modify (chèn theo mốc): `tram/cli_dich_vu.py`
- Test: `tests/test_giao_kiem.py` (mới)

**Interfaces:**
- Consumes: `CauHinhGiaoViec`, `PrincipalKiem` (Task 1); `phien_ban_quyen`, `KHONG_CO` (Task 2); `url_origin`, `lap_ke_hoach`, `in_ke_hoach`, `thuc_hien` (Task 3); `chay_vong`, `KHOA_*` (Task 8); `vong_nhanh`, `vong_git` (Task 7); `dung_bo_that`, `cac_du_an_that` (Task 9); `MucKiem`, `in_ket_qua` (3a-1 Task 24); `chay_mot_lenh`, `moi_truong_kiem`, `KetQuaLenh` (3a-1 Task 8); `kho_kiem` (4a-1).
- Produces: `kiem_principal(pk, thu_muc, *, chay, chay_lenh, toi) -> list[MucKiem]`, `kiem_du_an(da) -> list[MucKiem]`, `kiem_giao_viec(cg, cac_du_an, *, goc_quyen=None, **kw) -> list[MucKiem]`; `them_lenh_giao(sub)` — `tram giao tick [--thu]`, `tram giao kho-kiem <du_an> [--dong-y]`, `tram giao kiem`.

- [ ] **Step 1: Viết test thất bại**

`tests/test_giao_kiem.py` (mới):

```python
"""`tram giao kiem|tick|kho-kiem` (4a-2). Không chạy sudo, `bd` hay mạng thật: `chay`/`chay_lenh` giả, TRAM_REPO tạm
(du-an/ rỗng hoặc trỏ remote bare cục bộ)."""
import subprocess
from pathlib import Path

import pytest

from kho_kiem_gia import dung_kho
from tram.cau_hinh.du_an import DuAn, MoiTruongKiem
from tram.cau_hinh.giao_viec import CauHinhGiaoViec
from tram.cli import main
from tram.giao_viec.kho_kiem_tao import lap_ke_hoach, thuc_hien
from tram.giao_viec.kiem_san_sang import kiem_du_an, kiem_giao_viec
from tram.giao_viec.principal_kiem import PrincipalKiem
from tram.kiem.chay_lenh import KetQuaLenh
from tram.tho.kiem_may import in_ket_qua

PK = PrincipalKiem("tram-kiem", ("/usr/bin/sudo", "-n", "-u", "tram-kiem", "--"), ("/usr/local/libexec/trao",))


def chay_gia(ten="tram-kiem", env="APP_ENV=testing\nPATH=/usr/bin", doc_duoc=False, ghi_duoc=True):
    def chay(argv, **kw):
        lenh = argv[len(PK.boc):] if argv[:len(PK.boc)] == list(PK.boc) else argv
        ra = {"/usr/bin/id": (0, ten), "/usr/bin/env": (0, env), "/bin/test": (0 if doc_duoc else 1, ""),
              "/usr/bin/touch": (0 if ghi_duoc else 1, ""), "/usr/local/libexec/trao": (0, "")}[lenh[0]]
        if kw.get("check") and ra[0]:
            raise subprocess.CalledProcessError(ra[0], argv)
        return subprocess.CompletedProcess(argv, ra[0], ra[1], "")
    return chay


def dung_lenh(het_gio=True):
    return lambda lenh, argv, **kw: KetQuaLenh(lenh, "fail", "", "sha256:0", None, het_gio)


def muc(ds):
    return {m.muc: m.muc_do for m in ds}


def test_thieu_het_thi_do(tmp_path):
    ds = kiem_giao_viec(CauHinhGiaoViec(), [], goc_quyen=tmp_path)
    m = muc(ds)
    assert (m["giao_viec.bat"], m["file quyền coder"], m["principal kiểm lại"]) == ("vang", "do", "do")
    assert in_ket_qua(ds)[1] == 1


def test_principal_dat_moi_muc(tmp_path):
    (tmp_path / "quyen").mkdir()
    for v in ("coder", "qc"):
        (tmp_path / "quyen" / f"{v}.json").write_text("{}")
    cg = CauHinhGiaoViec(bat=True, thu_muc_kiem=tmp_path, principal_kiem=PK)
    ds = kiem_giao_viec(cg, [], goc_quyen=tmp_path / "quyen", chay=chay_gia(), chay_lenh=dung_lenh(), toi="hung")
    assert set(muc(ds).values()) == {"xanh"} and in_ket_qua(ds)[1] == 0
    assert not (tmp_path / "tram-giao-kiem-thu").exists()


@pytest.mark.parametrize("sai, muc_do", [
    ({"ten": "hung"}, "principal: danh tính"), ({"env": "PATH=/usr/bin"}, "principal: giữ APP_ENV"),
    ({"doc_duoc": True}, "principal: không đọc kho trạm"), ({"ghi_duoc": False}, "principal: ghi worktree kiểm")])
def test_principal_sai_tung_muc_la_do(tmp_path, sai, muc_do):
    m = muc(kiem_giao_viec(CauHinhGiaoViec(thu_muc_kiem=tmp_path, principal_kiem=PK), [], goc_quyen=tmp_path,
                           chay=chay_gia(**sai), chay_lenh=dung_lenh(), toi="hung"))
    assert m[muc_do] == "do" and m["principal: dừng được lệnh quá hạn"] == "xanh"


def test_khong_dung_duoc_lenh_qua_han_la_do(tmp_path):
    m = muc(kiem_giao_viec(CauHinhGiaoViec(thu_muc_kiem=tmp_path, principal_kiem=PK), [], goc_quyen=tmp_path,
                           chay=chay_gia(), chay_lenh=dung_lenh(het_gio=False), toi="hung"))
    assert m["principal: dừng được lệnh quá hạn"] == "do"


def test_du_an_kho_kiem_va_moi_truong(tmp_path):
    k = dung_kho(tmp_path)
    (tmp_path / "env.testing").write_text("DB_DATABASE=test\n")
    da = DuAn("hr-codex", k.dev, None, {}, moi_truong_kiem=MoiTruongKiem(tmp_path / "env.testing", ".env.testing"))
    assert muc(kiem_du_an(da)) == {"hr-codex: kho kiểm": "do", "hr-codex: moi_truong_kiem": "xanh",
                                   "hr-codex: lệnh kiểm mặc định": "vang"}
    thuc_hien(lap_ke_hoach(da), "main")
    assert muc(kiem_du_an(da))["hr-codex: kho kiểm"] == "xanh"


def test_cli_tick_va_kho_kiem(tmp_path, monkeypatch, capsys):
    k = dung_kho(tmp_path)
    (tmp_path / "repo-tram" / "du-an").mkdir(parents=True)
    (tmp_path / "repo-tram" / "du-an" / "hr-x.yaml").write_text(f"ten: hr-x\nduong_dan: {k.dev}\n")
    monkeypatch.setenv("TRAM_REPO", str(tmp_path / "repo-tram"))
    monkeypatch.setattr("tram.giao_viec.noi_that.cac_du_an_that", lambda thu_muc=None: [])   # không chạy `bd` thật
    assert main(["giao", "tick"]) == 1 and "chỉ chạy được" in capsys.readouterr().out
    assert main(["giao", "tick", "--thu"]) == 0 and "pha nhanh: không có việc" in capsys.readouterr().out
    monkeypatch.setattr("builtins.input", lambda *_: "không")
    assert main(["giao", "kho-kiem", "hr-x"]) == 1 and "TẠO MỚI" in capsys.readouterr().out
    assert main(["giao", "kho-kiem", "hr-x", "--dong-y"]) == 0 and k.main in capsys.readouterr().out
    assert Path(tmp_path / "tram-home" / "kho-kiem" / "hr-x" / ".git").is_dir()
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_giao_kiem.py -q`
Expected: FAIL — `1 error` (`ModuleNotFoundError: No module named 'tram.giao_viec.kiem_san_sang'`)

- [ ] **Step 3: Viết mã**

`tram/giao_viec/kiem_san_sang.py` (mới):

```python
"""`tram giao kiem` — kiểm sẵn sàng của bộ giao việc trước khi bật `giao_viec.bat`: đây là BƯỚC KIỂM KHI CHẠY THẬT
của mọi adapter chờ cổng (S6 principal `tram-kiem`, S7 kho kiểm/remote, 3a-2 file quyền). Chưa chứng minh được → ĐỎ;
không đánh dấu sẵn sàng bằng bản giả. Mọi lần chạy thật đi qua `chay`/`chay_lenh` tiêm được (test dùng bản giả)."""
import getpass
import shutil
import subprocess
import threading
from collections.abc import Callable
from pathlib import Path

from tram.cau_hinh.du_an import DuAn
from tram.cau_hinh.giao_viec import CauHinhGiaoViec
from tram.duong_dan import tram_home
from tram.giao_viec.git_kiem import kho_kiem
from tram.giao_viec.kho_kiem_tao import url_origin
from tram.giao_viec.principal_kiem import PrincipalKiem
from tram.giao_viec.quyen import KHONG_CO, phien_ban_quyen
from tram.kiem.chay_lenh import chay_mot_lenh, moi_truong_kiem
from tram.tho.kiem_may import MucKiem

LOI_CHAY = (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError)


def _muc(ten: str, dat: bool, chi_tiet: str, *, khong_dat: str = "do") -> MucKiem:
    return MucKiem(ten, "xanh" if dat else khong_dat, chi_tiet)


def _ra(chay: Callable, argv: list[str], **kw):
    return chay(argv, capture_output=True, text=True, timeout=30, **kw)


def _ghi_duoc(pk: PrincipalKiem, thu_muc: Path | None, chay: Callable) -> MucKiem:
    if thu_muc is None or not thu_muc.is_dir():
        return _muc("principal: ghi worktree kiểm", False, f"thu_muc_kiem không có: {thu_muc}")
    d = thu_muc / "tram-giao-kiem-thu"
    shutil.rmtree(d, ignore_errors=True)
    d.mkdir()
    try:
        pk.trao(d, chay=chay)
        ghi = _ra(chay, pk.boc_lenh(["/usr/bin/touch", str(d / "x")])).returncode == 0
    except LOI_CHAY:
        ghi = False
    shutil.rmtree(d, ignore_errors=True)
    return _muc("principal: ghi worktree kiểm", ghi and not d.exists(), "trao quyền → tram-kiem ghi → trạm xoá được")


def _dung_duoc(pk: PrincipalKiem, thu_muc: Path | None, chay_lenh: Callable) -> MucKiem:
    kq: list = []
    t = threading.Thread(target=lambda: kq.append(chay_lenh(
        "sleep 30", ["/bin/sleep", "30"], cwd=thu_muc or tram_home(), env=moi_truong_kiem({}),
        log=tram_home() / "log" / "giao-kiem-dung.log", thoi_gian_cho=1, boc=pk.boc_lenh, cho_kill=2, kill=pk.kill_nhom)), daemon=True)
    t.start()
    t.join(15)
    return _muc("principal: dừng được lệnh quá hạn", bool(kq) and kq[0].het_gio, "kill cả nhóm tiến trình tram-kiem")


def kiem_principal(pk: PrincipalKiem | None, thu_muc: Path | None, *, chay: Callable = subprocess.run,
                   chay_lenh: Callable = chay_mot_lenh, toi: str | None = None) -> list[MucKiem]:
    if pk is None:
        return [_muc("principal kiểm lại", False, "chưa đặt giao_viec.principal_kiem — chờ S6")]
    try:
        id_ = _ra(chay, pk.boc_lenh(["/usr/bin/id", "-un"]))
        env = _ra(chay, pk.boc_lenh(["/usr/bin/env"]), env=moi_truong_kiem({}))
        doc = _ra(chay, pk.boc_lenh(["/bin/test", "-r", str(tram_home() / "su-kien.db")]))
    except LOI_CHAY as e:
        return [_muc("principal kiểm lại", False, f"không chạy được boc: {type(e).__name__}")]
    ten = id_.stdout.strip()
    return [_muc("principal: danh tính", id_.returncode == 0 and ten == pk.ten != (toi or getpass.getuser()), ten[:40]),
            _muc("principal: giữ APP_ENV", "APP_ENV=testing" in env.stdout.splitlines(), "lệnh kiểm phải thấy APP_ENV"),
            _muc("principal: không đọc kho trạm", doc.returncode != 0, str(tram_home() / "su-kien.db")),
            _ghi_duoc(pk, thu_muc, chay), _dung_duoc(pk, thu_muc, chay_lenh)]


def kiem_du_an(da: DuAn) -> list[MucKiem]:
    kg, mt = kho_kiem(da.ten), da.moi_truong_kiem
    if (kg / ".git").exists():
        cu, goc = url_origin(kg), url_origin(da.duong_dan)
        ra = [_muc(f"{da.ten}: kho kiểm", bool(cu) and cu == goc, f"origin {cu} — dự án {goc}")]
    else:
        ra = [_muc(f"{da.ten}: kho kiểm", False, f"chưa có — chạy `tram giao kho-kiem {da.ten}`")]
    return ra + [_muc(f"{da.ten}: moi_truong_kiem", mt is not None and mt.file.is_file(), str(mt.file if mt else "")),
                 _muc(f"{da.ten}: lệnh kiểm mặc định", bool(da.giao.lenh_kiem_mac_dinh),
                      "không có thì mỗi bead phải nêu lệnh trong design", khong_dat="vang")]


def kiem_giao_viec(cg: CauHinhGiaoViec, cac_du_an: list[DuAn], *, goc_quyen: Path | None = None,
                   **kw) -> list[MucKiem]:
    ra = [_muc("giao_viec.bat", cg.bat, "bật" if cg.bat else "tắt — tram-api không phát phiếu", khong_dat="vang")]
    ra += [_muc(f"file quyền {v}", phien_ban_quyen(v, goc=goc_quyen) != KHONG_CO, "vai/quyen/<vai>.json — 3a-2")
           for v in ("coder", "qc")]
    ra += kiem_principal(cg.principal_kiem, cg.thu_muc_kiem, **kw)
    for da in cac_du_an:
        ra += kiem_du_an(da)
    return ra
```

`tram/giao_viec/lenh.py` (mới):

```python
"""Lệnh `tram giao tick [--thu]`, `tram giao kho-kiem <du_an> [--dong-y]`, `tram giao kiem` (spec 4 §10; 4a-2) —
chạy ở TÀI KHOẢN TRẠM. `tick` chạy hai pha như các luồng của tram-api, qua cùng khoá file (không trùng vòng đang chạy).
Bộ giao việc tắt (`giao_viec.bat: false`) thì chỉ cho `tick --thu` (không ghi beads, không chạy lệnh)."""
import sys


def _bo():
    from tram.cau_hinh.giao_viec import nap_cau_hinh_giao_viec
    from tram.cau_hinh.tram import nap_cau_hinh_tram
    from tram.giao_viec.noi_that import dung_bo_that
    cg = nap_cau_hinh_giao_viec()
    return cg, dung_bo_that(cg, nap_cau_hinh_tram())


def _tick(args) -> int:
    from tram.giao_viec.luong import KHOA_GIT, KHOA_NHANH, chay_vong
    from tram.giao_viec.tick import vong_git, vong_nhanh
    cg, bo = _bo()
    if not cg.bat and not args.thu:
        print("giao_viec.bat đang tắt — chỉ chạy được `tram giao tick --thu`.")
        return 1
    pha = [("nhanh", KHOA_NHANH, lambda: vong_nhanh(bo, thu=args.thu))]
    if not args.thu:
        pha.append(("git", KHOA_GIT, lambda: vong_git(bo)))
    for ten, khoa, lam in pha:
        kq = chay_vong(khoa, lam)
        print(f"pha {ten}: " + ("đang có vòng khác chạy — bỏ qua" if kq is None else str(kq or "không có việc")))
    return 0


def _kho_kiem(args) -> int:
    from tram.cau_hinh.du_an import nap_du_an
    from tram.giao_viec.kho_kiem_tao import in_ke_hoach, lap_ke_hoach, thuc_hien
    da = nap_du_an(args.du_an)
    try:
        kh = lap_ke_hoach(da)
    except ValueError as e:
        print(e, file=sys.stderr)
        return 2
    print(in_ke_hoach(kh))
    if not args.dong_y and input("Gõ dong-y để thực hiện: ").strip() != "dong-y":
        print("Không làm gì.")
        return 1
    print(f"Xong: origin/{da.nhanh_chinh} = {thuc_hien(kh, da.nhanh_chinh)}")
    return 0


def _kiem(args) -> int:
    from tram.giao_viec.kiem_san_sang import kiem_giao_viec
    from tram.tho.kiem_may import in_ket_qua
    cg, bo = _bo()
    van_ban, ma = in_ket_qua(kiem_giao_viec(cg, bo.cac_du_an()))
    print(van_ban)
    return ma


def them_lenh_giao(sub) -> None:
    g = sub.add_parser("giao", help="Bộ giao việc (phần 4)").add_subparsers(dest="lenh_giao", required=True)
    t = g.add_parser("tick", help="Chạy một vòng tick (pha nhanh rồi pha Git)")
    t.add_argument("--thu", action="store_true", help="Chỉ ghi sự kiện suy từ beads: không ghi beads, không chạy lệnh")
    t.set_defaults(ham=_tick)
    k = g.add_parser("kho-kiem", help="Tạo/cập nhật kho kiểm của trạm từ remote dự án (liệt kê, chờ dong-y)")
    k.add_argument("du_an")
    k.add_argument("--dong-y", action="store_true", help="Bỏ bước hỏi (chỉ khi Đại ca đã đọc kế hoạch)")
    k.set_defaults(ham=_kho_kiem)
    g.add_parser("kiem", help="Kiểm sẵn sàng: xanh/vàng/đỏ, mã ≠ 0 nếu có đỏ").set_defaults(ham=_kiem)
```

`tram/cli_dich_vu.py` (sửa — chèn hai dòng sau mốc `    them_lenh_tho(sub, chu)`):

```bash
uv run python - <<'EOF'
from pathlib import Path

f = Path("tram/cli_dich_vu.py")
s = f.read_text(encoding="utf-8")
moc = "    them_lenh_tho(sub, chu)\n"
assert s.count(moc) == 1, "không thấy đúng một dòng mốc — dừng, báo người điều phối"
f.write_text(s.replace(moc, moc + "    from tram.giao_viec.lenh import them_lenh_giao\n    them_lenh_giao(sub)\n"),
             encoding="utf-8")
print("đã chèn 4a-2 Task 10")
EOF
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_giao_kiem.py -q`
Expected: `9 passed`

Run: `uv run pytest -q`
Expected: `N₀ + 71 passed`

- [ ] **Step 5: Commit**

```bash
git add tram/giao_viec/kiem_san_sang.py tram/giao_viec/lenh.py tram/cli_dich_vu.py tests/test_giao_kiem.py
git commit -m "feat(giao-viec): tram giao tick|kho-kiem|kiem — kiểm sẵn sàng chạy thật (S6 principal, S7 kho kiểm, file quyền) (spec 4 §10)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 11: `GET /api/giao-viec` — lý do không giao, lệnh/link tạo PR

**Độ khó:** `de` · **Đợt:** 5 · **Song song với:** Task 10, 12 · **Phải xong trước:** Task 3, 9

**Files:**
- Create: `tram/suy/giao_viec.py`
- Create: `tram/api/tuyen_giao.py`
- Modify (chèn theo mốc): `tram/api/app.py`
- Test: `tests/test_giao_viec_api.py` (mới)

**Interfaces:**
- Consumes: `ly_do_khong_giao`, `NHAN_COT_1` (4a-1 Task 10); `lenh_bat_buoc` (4a-1 Task 3); `sha_cua` (4a-1 Task 5); `url_origin`, `github_repo` (Task 3); `PhuThuocApi.bo_giao`, `.chon_phieu` (Task 9); `kiem_du_an_bead`; `KhoSuKien.moi_nhat`.
- Produces: `VAN_BAN` (mã lý do → văn bản), `ly_do_hien(b, theo_id, da, co_kho_kiem) -> str | None`, `thong_tin_pr(da, b, vao_cot_3, kg) -> dict | None`, `suy_giao(da, beads, kho, kg) -> dict`; `GET /api/giao-viec?du_an=` (G16).

- [ ] **Step 1: Viết test thất bại**

`tests/test_giao_viec_api.py` (mới):

```python
"""Dashboard 4a (spec 4 §5.1, §6.4 mục 4): lý do không giao + lệnh/link tạo PR — `GET /api/giao-viec`."""
from dataclasses import replace

from api_gia import tao_pt
from asgi_gia import goi
from bd_gia import BdGia
from git_gia import git
from giao_viec_gia import bug, du_an_gia, dung
from tram.api.app import tao_app
from tram.cau_hinh.du_an_giao import CauHinhGiao
from tram.giao_viec.git_kiem import fetch
from tram.su_kien.kho import KhoSuKien
from tram.suy.giao_viec import VAN_BAN, ly_do_hien, thong_tin_pr


def test_ly_do_hien(tmp_path):
    da = du_an_gia(tmp_path)
    ds = [bug("a", acceptance_criteria=""), bug("b", labels=["cot:ai-lam", "cot:can-chot"]),
          bug("c", parent="f-1"), bug("d", issue_type="feature"), bug("e", labels=["cot:can-chot"]),
          bug("f", chan_boi=["x"]), bug("g"), bug("h", status="in_progress", assignee="hung")]
    theo_id = {b.id: b for b in ds}
    assert [ly_do_hien(b, theo_id, da, True) for b in ds] == [
        "thieu-tieu-chi", "nhan-lech", "cho-merge-spec", "loai-khong-giao", None, None, None, "nguoi-khac-nhan"]
    assert ly_do_hien(bug("g"), theo_id, da, False) == "chua-co-kho-kiem"
    khong_lenh = replace(da, giao=CauHinhGiao())
    assert ly_do_hien(bug("g"), theo_id, khong_lenh, True) == "thieu-lenh-kiem"
    assert ly_do_hien(bug("s", issue_type="spike"), theo_id, khong_lenh, True) is None
    assert ly_do_hien(bug("g"), theo_id, du_an_gia(tmp_path, env=False), True) == "thieu-moi-truong-kiem"


def test_thong_tin_pr_github_va_lech(tmp_path):
    t = dung(tmp_path, bug(labels=["cot:cho-review"]))
    c = t.k.day("tram/hr-1", {"src/tom_tat.py": "x = 2\n"}, tu=t.k.main)
    fetch(t.k.kho)
    b = t.g.beads["hr-1"]
    pr = thong_tin_pr(t.da, b, {"commit_ban_giao": c}, t.k.kho)
    assert (pr["nhanh"], pr["commit"], pr["tu_xa"], pr["lech"], pr["link"]) == ("tram/hr-1", c, c, False, None)
    assert pr["lenh"] == "gh pr create --base main --head tram/hr-1 --fill"
    git(t.k.kho, "remote", "set-url", "origin", "https://github.com/hung/hr-codex.git")
    t.k.day("tram/hr-1", {"src/la.py": "x\n"}, tu=c)
    git(t.k.kho, "fetch", "-q", str(t.k.origin), "+refs/heads/*:refs/remotes/origin/*")
    pr = thong_tin_pr(t.da, b, {"commit_ban_giao": c}, t.k.kho)
    assert pr["lech"] and pr["link"] == "https://github.com/hung/hr-codex/compare/main...tram/hr-1?expand=1"
    assert pr["lenh"].startswith("gh pr create --repo hung/hr-codex ")
    assert thong_tin_pr(t.da, b, {"commit_ban_giao": "khong-phai-sha"}, t.k.kho) is None
    assert thong_tin_pr(t.da, bug(), {"commit_ban_giao": c}, t.k.kho) is None              # không ở cột 3


def test_api_giao_viec(tmp_path):
    t = dung(tmp_path, bug("hr-1", acceptance_criteria=""), bug("hr-2", labels=["cot:cho-review"]))
    c = t.k.day("tram/hr-2", {"src/tom_tat.py": "x = 2\n"}, tu=t.k.main)
    fetch(t.k.kho)
    pt = tao_pt(tmp_path, {"hr-codex": t.g})
    pt.bo_giao = t.bo
    KhoSuKien(tmp_path / "sk.db").ghi("hr-codex", "bead.vao_cot_3", {"commit_ban_giao": c}, bead_id="hr-2")
    r = goi(tao_app(pt), "GET", "/api/giao-viec?du_an=hr-codex")
    assert r.status == 200 and r.json()["bat"] is False
    g = r.json()["giao"]
    assert g["hr-codex/hr-1"] == {"khong_giao": VAN_BAN["thieu-tieu-chi"], "pr": None}
    assert g["hr-codex/hr-2"]["pr"]["commit"] == c and g["hr-codex/hr-2"]["khong_giao"] is None
    assert goi(tao_app(pt), "GET", "/api/giao-viec?du_an=khong-co").status == 404


def test_api_khi_chua_noi_bo_giao_viec(tmp_path):
    r = goi(tao_app(tao_pt(tmp_path, {"hr-codex": BdGia([bug()])})), "GET", "/api/giao-viec")
    assert r.status == 200 and r.json() == {"bat": False, "giao": {}}
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_giao_viec_api.py -q`
Expected: FAIL — `1 error` (`ModuleNotFoundError: No module named 'tram.suy.giao_viec'`)

- [ ] **Step 3: Viết mã**

`tram/suy/giao_viec.py` (mới):

```python
"""Dashboard 4a (spec 4 §5.1, §6.4 mục 4): vì sao bead cột 1 CHƯA được giao, và lệnh/link để Đại ca tự tạo PR từ
`tram/<bead>` tại `commit_ban_giao` (trước 4c trạm không mở PR, không coi `pr` null là đã merge). Chỉ đọc: bộ đệm
beads, sự kiện `bead.vao_cot_3`, ref CỤC BỘ của kho kiểm (không fetch, không `bd ready` — "bị chặn" đã hiện bằng
"chờ …" trên thẻ). Mọi chuỗi trả về dựng từ hằng số, id đã kiểm dạng, SHA hex, tên nhánh đã kiểm."""
import re
from pathlib import Path
from urllib.parse import quote

from tram.beads.mo_hinh import Bead
from tram.cau_hinh.du_an import DuAn
from tram.giao_viec.dieu_kien import NHAN_COT_1, ly_do_khong_giao
from tram.giao_viec.git_kiem import sha_cua
from tram.giao_viec.kho_kiem_tao import github_repo, url_origin
from tram.giao_viec.tieu_chi import lenh_bat_buoc

ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}")
SHA_RE = re.compile(r"[0-9a-f]{40}")
VAN_BAN = {
    "nhan-lech": "nhãn lệch — bead mang nhiều nhãn cột",
    "nhan-luong": "bead đang trong luồng feature (can-spec / cho-duyet-spec / theo-plan)",
    "loai-khong-giao": "loại bead này không giao ở 4a (chỉ bug, task, chore, spike)",
    "thieu-tieu-chi": "thiếu tiêu chí máy đọc được — chép tiêu chí vào acceptance_criteria",
    "cho-merge-spec": "chờ merge spec",
    "nguoi-khac-nhan": "bead đang do người khác nhận",
    "thieu-moi-truong-kiem": "dự án chưa có moi_truong_kiem",
    "thieu-lenh-kiem": "không có lệnh kiểm bắt buộc khớp lenh_cho_phep",
    "chua-co-kho-kiem": "trạm chưa có kho kiểm của dự án (tram giao kho-kiem)",
}
BO_QUA = {"bi-chan", "trang-thai", "khong-o-cot-1"}


def ly_do_hien(b: Bead, theo_id: dict[str, Bead], da: DuAn, co_kho_kiem: bool) -> str | None:
    if NHAN_COT_1 not in b.labels or b.status not in ("open", "in_progress"):
        return None
    ly = ly_do_khong_giao(b, theo_id, {b.id}, da)
    if ly in BO_QUA:
        return None
    if ly is None and b.issue_type != "spike" and not lenh_bat_buoc(da.giao.lenh_kiem_mac_dinh, b.design,
                                                                    da.lenh_cho_phep):
        ly = "thieu-lenh-kiem"
    return "chua-co-kho-kiem" if ly is None and not co_kho_kiem else ly


def thong_tin_pr(da: DuAn, b: Bead, vao_cot_3: dict | None, kg: Path | None) -> dict | None:
    commit = (vao_cot_3 or {}).get("commit_ban_giao")
    if "cot:cho-review" not in b.labels or not ID_RE.fullmatch(b.id) or not isinstance(commit, str) \
            or not SHA_RE.fullmatch(commit):
        return None
    nhanh = f"tram/{b.id}"
    tu_xa = sha_cua(kg, f"origin/{nhanh}") if kg else None
    repo = github_repo(url_origin(kg)) if kg else None
    link = (f"https://github.com/{repo}/compare/{quote(da.nhanh_chinh, safe='/')}...{quote(nhanh, safe='/')}"
            "?expand=1") if repo else None
    lenh = f"gh pr create {f'--repo {repo} ' if repo else ''}--base {da.nhanh_chinh} --head {nhanh} --fill"
    return {"nhanh": nhanh, "commit": commit, "tu_xa": tu_xa, "lech": tu_xa is not None and tu_xa != commit,
            "link": link, "lenh": lenh}


def suy_giao(da: DuAn, beads: list[Bead], kho, kg: Path | None) -> dict[str, dict]:
    """{"<du_an>/<bead_id>": {"khong_giao": văn bản | None, "pr": {...} | None}} — chỉ bead có điều để hiện."""
    theo_id, ra = {b.id: b for b in beads}, {}
    for b in beads:
        ly = ly_do_hien(b, theo_id, da, kg is not None)
        vc3 = kho.moi_nhat(da.ten, b.id, "bead.vao_cot_3") if "cot:cho-review" in b.labels else None
        pr = thong_tin_pr(da, b, vc3.du_lieu if vc3 else None, kg)
        if ly or pr:
            ra[f"{da.ten}/{b.id}"] = {"khong_giao": VAN_BAN[ly] if ly else None, "pr": pr}
    return ra
```

`tram/api/tuyen_giao.py` (mới):

```python
"""`GET /api/giao-viec?du_an=` (4a-2; chỉ đọc như các GET khác của 2a): lý do không giao của bead cột 1 và
lệnh/link tạo PR của bead cột 3, theo khoá "<du_an>/<bead_id>". `bat` = tram-api có đang phát phiếu không."""
from contextlib import closing

from fastapi import APIRouter, Request

from tram.api.phu_thuoc import kiem_du_an_bead
from tram.beads.bd import LoiBd
from tram.suy.giao_viec import suy_giao

router = APIRouter()


@router.get("/api/giao-viec")
def giao_viec(request: Request, du_an: str = "") -> dict:
    pt = request.app.state.pt
    if du_an:
        kiem_du_an_bead(pt, du_an)
    bo, ra = pt.bo_giao, {}
    if bo is None:
        return {"bat": False, "giao": ra}
    ten = set(pt.cac_du_an())
    with closing(pt.mo_kho()) as kho:
        for da in bo.cac_du_an():
            if da.ten not in ten or (du_an and da.ten != du_an):
                continue
            try:
                ra.update(suy_giao(da, pt.bo_dem.lay(da.ten), kho, bo.kho_git(da)))
            except LoiBd:
                continue
    return {"bat": pt.chon_phieu is not None, "giao": ra}
```

`tram/api/app.py` (sửa — chèn theo mốc):

```bash
uv run python - <<'EOF'
from pathlib import Path

f = Path("tram/api/app.py")
s = f.read_text(encoding="utf-8")
for moc in ("from tram.api.phu_thuoc import PhuThuocApi\n", "\n\n\ndef _xu_ly(ma: int):"):
    assert s.count(moc) == 1, f"không thấy đúng một mốc {moc.strip()!r} — dừng, báo người điều phối"
s = s.replace("from tram.api.phu_thuoc import PhuThuocApi\n",
              "from tram.api.phu_thuoc import PhuThuocApi\nfrom tram.api.tuyen_giao import router as tuyen_giao\n")
s = s.replace("\n\n\ndef _xu_ly(ma: int):", "\nCAC_TUYEN += (tuyen_giao,)                     # 4a-2: GET /api/giao-viec\n\n\ndef _xu_ly(ma: int):")
f.write_text(s, encoding="utf-8")
print("đã chèn 4a-2 Task 11")
EOF
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_giao_viec_api.py tests/test_api_doc.py -q`
Expected: `12 passed`

Run: `uv run pytest -q`
Expected: `N₀ + 66 passed`

- [ ] **Step 5: Commit**

```bash
git add tram/suy/giao_viec.py tram/api/tuyen_giao.py tram/api/app.py tests/test_giao_viec_api.py
git commit -m "feat(api): GET /api/giao-viec — lý do bead cột 1 chưa giao, lệnh/link tạo PR tại commit_ban_giao (spec 4 §5.1, §6.4 mục 4)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 12: Dashboard — nhãn "chưa giao" trên thẻ, mục "Bộ giao việc" ở ngăn bên

**Độ khó:** `de` · **Đợt:** 5 · **Song song với:** Task 10, 11 · **Phải xong trước:** — (hợp đồng JSON ở G16; chạy chung với Task 11 sau khi ghép)

**Files:**
- Create: `frontend/src/giao_viec.js`, `frontend/src/thanh/OGiaoViec.vue`
- Modify: `frontend/src/trang/CongViec.vue`, `frontend/src/thanh/TheBead.vue`, `frontend/src/trang/NganBen.vue`
- Test: `frontend/tests/giao_viec.test.mjs` (mới)

**Interfaces:**
- Consumes: `GET /api/giao-viec?du_an=` (Task 11, G16); `doc` (`api.js`), `laLinkAnToan` (`luat.js`).
- Produces: `ganGiaoViec(dsThe, giao)`, `nhanChuaGiao(the)`, `canhBaoPr(pr)`; thẻ có trường `giao` (`{khong_giao, pr}` hoặc `null`); `<OGiaoViec :giao>`.

- [ ] **Step 1: Viết test thất bại**

`frontend/tests/giao_viec.test.mjs` (mới):

```js
import assert from 'node:assert/strict'
import { test } from 'node:test'
import { canhBaoPr, ganGiaoViec, nhanChuaGiao } from '../src/giao_viec.js'

test('ganGiaoViec gắn theo khoá du_an/id, thiếu thì null', () => {
  const ds = ganGiaoViec([{ du_an: 'hr', id: 'a' }, { du_an: 'hr', id: 'b' }],
    { 'hr/a': { khong_giao: 'thiếu tiêu chí', pr: null } })
  assert.deepEqual(ds.map((t) => t.giao), [{ khong_giao: 'thiếu tiêu chí', pr: null }, null])
  assert.deepEqual(ganGiaoViec([{ du_an: 'hr', id: 'a' }], undefined)[0].giao, null)
})

test('nhanChuaGiao chỉ khi có lý do', () => {
  assert.equal(nhanChuaGiao({ giao: { khong_giao: 'chờ merge spec' } }), 'chờ merge spec')
  assert.equal(nhanChuaGiao({ giao: null }), '')
  assert.equal(nhanChuaGiao(null), '')
})

test('canhBaoPr: lệch nhánh, chưa kiểm được, khớp', () => {
  const pr = { nhanh: 'tram/hr-1', commit: 'a'.repeat(40), tu_xa: 'a'.repeat(40), lech: false }
  assert.equal(canhBaoPr(pr), '')
  assert.match(canhBaoPr({ ...pr, tu_xa: 'b'.repeat(40), lech: true }), /KHÁC commit/)
  assert.match(canhBaoPr({ ...pr, tu_xa: null }), /Chưa kiểm được/)
  assert.equal(canhBaoPr(null), '')
})
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `cd frontend && npm run kiem`
Expected: FAIL — `giao_viec.test.mjs` báo `ERR_MODULE_NOT_FOUND` (`Cannot find module '…/src/giao_viec.js'`)

- [ ] **Step 3: Viết mã**

`frontend/src/giao_viec.js` (mới):

```js
// Bộ giao việc trên bảng (lát 4a-2): gắn lý do chưa giao / thông tin PR vào thẻ; chuỗi hiển thị thuần (node --test).
// Server dựng mọi chuỗi từ hằng số + id/SHA đã kiểm dạng; ở đây chỉ hiển thị bằng text, link qua laLinkAnToan.
export function ganGiaoViec(dsThe, giao) {
  const g = giao || {}
  return dsThe.map((t) => ({ ...t, giao: g[`${t.du_an}/${t.id}`] ?? null }))
}

export function nhanChuaGiao(the) {
  return the && the.giao && the.giao.khong_giao ? the.giao.khong_giao : ''
}

export function canhBaoPr(pr) {
  if (!pr) return ''
  if (pr.tu_xa == null) return 'Chưa kiểm được nhánh trên remote — kiểm trước khi tạo PR.'
  if (pr.lech) return `Nhánh ${pr.nhanh} trên remote đang ở ${pr.tu_xa}, KHÁC commit trạm đã kiểm — đừng tạo PR.`
  return ''
}
```

`frontend/src/thanh/OGiaoViec.vue` (mới):

```vue
<script setup>
import { computed } from 'vue'
import { canhBaoPr } from '../giao_viec.js'
import { laLinkAnToan } from '../luat.js'

const props = defineProps({ giao: { type: Object, required: true } })
const canhBao = computed(() => canhBaoPr(props.giao.pr))
</script>

<template>
  <section aria-label="Bộ giao việc">
    <h3>Bộ giao việc</h3>
    <p v-if="giao.khong_giao" class="canh-bao">Chưa giao: {{ giao.khong_giao }}</p>
    <template v-if="giao.pr">
      <p class="nho">Tạo PR từ nhánh {{ giao.pr.nhanh }} tại commit {{ giao.pr.commit }} (trạm đã kiểm lại và QC).</p>
      <p v-if="canhBao" class="canh-bao" role="alert">{{ canhBao }}</p>
      <p v-else-if="laLinkAnToan(giao.pr.link)">
        <a :href="giao.pr.link" target="_blank" rel="noopener noreferrer">Mở trang tạo PR trên GitHub</a>
      </p>
      <pre class="van-ban">{{ giao.pr.lenh }}</pre>
    </template>
  </section>
</template>
```

`frontend/src/trang/CongViec.vue`, `frontend/src/thanh/TheBead.vue`, `frontend/src/trang/NganBen.vue` (sửa — bản vá, chạy từ gốc worktree):

```diff
diff --git a/frontend/src/trang/CongViec.vue b/frontend/src/trang/CongViec.vue
index 670bf33..eafa17d 100644
--- a/frontend/src/trang/CongViec.vue
+++ b/frontend/src/trang/CongViec.vue
@@ -1,6 +1,7 @@
 <script setup>
 import { computed, onMounted, ref, watch } from 'vue'
 import { doc, ghi, thanGhi } from '../api.js'
+import { ganGiaoViec } from '../giao_viec.js'
 import { kho } from '../kho.js'
 import { HANG_COT, TEN_HANG, choPhepKeo, nhomTheoHang } from '../luat.js'
 import HopViSao from '../thanh/HopViSao.vue'
@@ -19,10 +20,12 @@ const nhom = computed(() => nhomTheoHang(dsThe.value))
 
 async function tai() {
   try {
-    const r = await doc(`/api/cong-viec?du_an=${encodeURIComponent(duAn.value)}`)
-    dsThe.value = r.the
+    const q = encodeURIComponent(duAn.value)
+    const [r, g] = await Promise.all([doc(`/api/cong-viec?du_an=${q}`),
+      doc(`/api/giao-viec?du_an=${q}`).catch(() => ({ giao: {} }))])     // bộ giao việc là phần thêm, lỗi thì bỏ qua
+    dsThe.value = ganGiaoViec(r.the, g.giao)
     loiDoc.value = r.loi
-    if (chon.value) chon.value = r.the.find((t) => t.du_an === chon.value.du_an && t.id === chon.value.id) ?? null
+    if (chon.value) chon.value = dsThe.value.find((t) => t.du_an === chon.value.du_an && t.id === chon.value.id) ?? null
   } catch (e) {
     thongBao.value = e.message
   }
```

```diff
diff --git a/frontend/src/thanh/TheBead.vue b/frontend/src/thanh/TheBead.vue
index 6f8078a..e84fc01 100644
--- a/frontend/src/thanh/TheBead.vue
+++ b/frontend/src/thanh/TheBead.vue
@@ -18,6 +18,7 @@ function batDauKeo(e) {
       <span v-if="the.khoa" class="nhan-nho" title="Đại ca đã khoá cột">khoá</span>
       <span v-if="the.co_do" class="nhan-nho do">cờ đỏ</span>
       <span v-if="the.lech" class="nhan-nho vang" title="Nhiều nhãn cột">nhãn lệch</span>
+      <span v-if="the.giao && the.giao.khong_giao" class="nhan-nho vang" :title="the.giao.khong_giao">chưa giao</span>
     </header>
     <p class="tieu-de">{{ the.tieu_de }}</p>
     <footer class="nho">{{ the.loai }} · P{{ the.uu_tien ?? '?' }}<span v-if="the.khe_spec"> · khe spec</span><span
```

```diff
diff --git a/frontend/src/trang/NganBen.vue b/frontend/src/trang/NganBen.vue
index d437272..c42aebb 100644
--- a/frontend/src/trang/NganBen.vue
+++ b/frontend/src/trang/NganBen.vue
@@ -4,6 +4,7 @@ import { doc, ghi, thanGhi } from '../api.js'
 import { kho } from '../kho.js'
 import { gioVN, laLinkAnToan } from '../luat.js'
 import DongThoiGian from '../thanh/DongThoiGian.vue'
+import OGiaoViec from '../thanh/OGiaoViec.vue'
 import OChot from '../thanh/OChot.vue'
 import OTraLoi from '../thanh/OTraLoi.vue'
 
@@ -69,6 +70,7 @@ const traLoi = (vb) => gui(`/api/phe-duyet/${duongDan()}/tra-loi`, { tra_loi: vb
         <p class="nho">Nhánh {{ ct.ban_giao.nhanh || '—' }} · commit {{ ct.ban_giao.commit || '—' }}</p>
         <ul v-if="ct.ban_giao.loi.length" class="canh-bao"><li v-for="l in ct.ban_giao.loi" :key="l">{{ l }}</li></ul>
       </section>
+      <OGiaoViec v-if="the.giao" :giao="the.giao" />
       <section><h3>Mô tả</h3><pre class="van-ban">{{ ct.mo_ta || '(trống)' }}</pre></section>
       <section><h3>Tiêu chí nghiệm thu</h3><pre class="van-ban">{{ ct.nghiem_thu || '(trống)' }}</pre></section>
       <DongThoiGian :ds="ct.dong_thoi_gian" />
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `cd frontend && npm run kiem && npm run build`
Expected: `ℹ fail 0` (thêm 3 test so với trước task), `kiem-an-toan: … không có chèn HTML thô`, build `✓ built`

Run: `uv run pytest -q`
Expected: `N₀ + 62 passed` (task này không thêm test Python)

- [ ] **Step 5: Commit**

```bash
git add frontend/src/giao_viec.js frontend/src/thanh/OGiaoViec.vue frontend/src/trang/CongViec.vue frontend/src/thanh/TheBead.vue frontend/src/trang/NganBen.vue frontend/tests/giao_viec.test.mjs
git commit -m "feat(dashboard): nhãn 'chưa giao' trên thẻ cột 1, mục Bộ giao việc — lý do, link/lệnh tạo PR, cảnh báo nhánh lệch (spec 4 §5.1, §6.4)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 13: Kịch bản giả lập 4a-2

**Độ khó:** `de` · **Đợt:** 6 · **Song song với:** — · **Phải xong trước:** Task 1–12

**Files:**
- Test: `tests/test_kich_ban_4a2.py` (mới)

**Interfaces:**
- Consumes: `tao_tram` (`tests/tho_api_gia.py`); `BoGiaoViec`, `DocBeads`, `an_toan`, `bat_dau_luong_giao`; `BdKhoa`, `cho_toi` (Task 8); `GIU`, `F`, `bg`, `TC`, `bug`, `du_an_gia`, `dung_kho`, `dat_phieu`, `nhan`, `cong_bo`, `ket_thuc_bang`.
- Produces: không (chỉ test).

Task chỉ có test tích hợp — mã đã có từ Task 1–12 nên test **pass ngay**. Fail → dừng, báo người điều phối, mở task sửa có test; không sửa mã trong task này.

- [ ] **Step 1: Viết test (pass ngay)**

`tests/test_kich_ban_4a2.py` (mới):

```python
"""Kịch bản giả lập 4a-2 (spec 4 §16 mục 3 — phần nối thật, chưa cần cổng): tram-api thật trong tiến trình phát phiếu
qua `/api/tho/nhip` bằng bộ giao việc (bộ đệm beads + đọc lại trước cấp); kéo cột xen kẽ; G5 với kiểm lại dài ở dự
án này và Git hỏng ở dự án kia. Thợ, remote GitHub, principal đều giả (CHỈ trong test)."""
import threading
from dataclasses import replace

from bd_gia import BdGia
from giao_viec_gia import TC, bug, du_an_gia
from kho_kiem_gia import dung_kho
from kho_phieu_gia import LUC, dat_phieu
from su_kien_gia import cong_bo, nhan
from test_luong_giao import BdKhoa, cho_toi
from test_tick import GIU
from test_xet_xong import F, bg
from tho_api_gia import tao_tram
from tram.api.bo_dem import BoDemBeads
from tram.cau_hinh.tram import CauHinhTram
from tram.giao_viec.bo import BoGiaoViec
from tram.giao_viec.doc_beads import DocBeads
from tram.giao_viec.git_kiem import fetch
from tram.giao_viec.luong import bat_dau_luong_giao
from tram.giao_viec.noi_that import an_toan
from tram.giao_viec.su_kien import su_kien_bead
from tram.phieu.kho import KhoPhieu
from xu_ly_gia import ket_thuc_bang

NHIP = {"khe_id": "B/claude-1", "buoc_tho": "ranh"}


def tram_http(tmp_path, *beads):
    t = tao_tram(tmp_path)
    k, da, g = dung_kho(tmp_path), du_an_gia(tmp_path), BdGia(beads)
    fetch(k.kho)
    bo = BoGiaoViec(cac_du_an=lambda: [da], tao_bd=lambda d: g, mo_kho=t.pt.mo_kho_phieu, ch=t.pt.cau_hinh,
                    dong_ho=lambda: t.gio[0], kho_git=lambda d: k.kho, boc=lambda a: a,
                    doc_beads=DocBeads(BoDemBeads(lambda ten: g, tuoi_toi_da=3600), tuoi=3600))
    pt = t.app.state.pt
    pt.chon_phieu, pt.con_hop_le_phieu = an_toan(bo.chon, None, "chon"), an_toan(bo.con_hop_le, False, "con_hop_le")
    pt.bo_giao = bo
    return t, bo, g, da


def test_http_phat_phieu_qua_bo_giao_viec(tmp_path):
    t, bo, g, _ = tram_http(tmp_path, bug())
    p = t.goi("POST", "/api/tho/nhip", json_body=NHIP).json()["phieu"]
    assert (p["bead_id"], p["buoc"], p["luot"]) == ("hr-1", "code", 1) and g.beads["hr-1"].status == "in_progress"
    assert t.goi("POST", "/api/tho/nhip", json_body={**NHIP, "khe_id": "B/claude-2"}).json()["phieu"] is None
    assert t.goi("GET", "/api/giao-viec").json()["bat"] is True


def test_http_keo_cot_xen_ke_khong_cap(tmp_path):
    t, bo, g, da = tram_http(tmp_path, bug())
    bo.doc_beads.lay(da, g)                                              # bộ chọn đã có snapshot
    g.beads["hr-1"] = replace(g.beads["hr-1"], labels=("cot:can-chot",))  # Đại ca kéo sang cột 2
    assert t.goi("POST", "/api/tho/nhip", json_body=NHIP).json() == {"tiep_tuc": True, "phieu": None}
    assert g.so_lan("nhan_viec") == 0 and g.beads["hr-1"].status == "open"


def test_g5_hai_du_an_kiem_lai_dai_va_git_hong(tmp_path):
    vao, tha = threading.Event(), threading.Event()

    def boc(argv):
        vao.set()
        tha.wait(20)
        return argv

    k, db = dung_kho(tmp_path), tmp_path / "su-kien.db"
    da_a = du_an_gia(tmp_path)
    da_b = replace(da_a, ten="hr-hong")
    g_a, g_b = BdKhoa(BdGia([bug(**GIU)])), BdKhoa(BdGia([bug("hb-1", **GIU)], tien_to="hb"))
    bo = BoGiaoViec(cac_du_an=lambda: [da_a, da_b], tao_bd=lambda d: g_a if d.ten == da_a.ten else g_b,
                    mo_kho=lambda: KhoPhieu(db), ch=CauHinhTram(), dong_ho=lambda: LUC,
                    kho_git=lambda d: k.kho if d.ten == da_a.ten else tmp_path / "khong-phai-git", boc=boc)
    kho = KhoPhieu(db)
    sha = k.day("tram/hr-1", {"src/tom_tat.py": "x = 2\n", F: "x", "kiem.sh": "exit 0\n"}, tu=k.main)
    p = dat_phieu(kho, bead_id="hr-1", lenh_kiem=["sh kiem.sh"], lenh_cho_phep=["sh kiem.sh"], tieu_chi=[TC])
    nhan(kho, p.giao_id, p.luot)
    cong_bo(kho, p.luot, sha)
    ket_thuc_bang(kho, p, "xong", commit=sha, ban_giao=bg(sha, lenh_kiem=[
        {"lenh": "sh kiem.sh", "ket_qua": "pass", "tom_tat": "", "digest_log": "sha256:1"}]))
    dung_ev = threading.Event()
    luong = bat_dau_luong_giao(bo, dung_ev, chu_ky=0.05)
    try:
        assert vao.wait(10)
        pb = dat_phieu(kho, "B/claude-2", du_an="hr-hong", bead_id="hb-1")
        ket_thuc_bang(kho, pb, "bi", ly_do="agent", noi_dung="vướng")
        assert cho_toi(lambda: any("bead_goc: hb-1" in b.description for b in g_b.tat_ca()
                                   if b.issue_type == "decision"))
        assert not [s for s in su_kien_bead(kho, da_a.ten, "hr-1") if s.loai == "kiem.lai"]
        tha.set()
        assert cho_toi(lambda: [s for s in su_kien_bead(kho, da_a.ten, "hr-1") if s.loai == "kiem.lai"])
    finally:
        tha.set()
        dung_ev.set()
        for x in luong:
            x.join(timeout=10)
    assert not any(x.is_alive() for x in luong)
```

- [ ] **Step 2: Chạy (3 lần — có luồng)**

Run: `for i in 1 2 3; do uv run pytest tests/test_kich_ban_4a2.py -q; done`
Expected: `3 passed` cả 3 lần

Run: `uv run pytest -q`
Expected: `N₀ + 78 passed`

- [ ] **Step 3: Commit**

```bash
git add tests/test_kich_ban_4a2.py
git commit -m "test(giao-viec): kịch bản 4a-2 — phát phiếu qua /api/tho/nhip, kéo cột xen kẽ, G5 với kiểm lại dài + Git hỏng (spec 4 §16 mục 3)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---
### Task 14: Kiểm chứng trên máy thật — repo nháp 3 bug (#4) — **CHỜ CỔNG, KHÔNG PHẢI TASK CODE**

**Không thực thi** cho tới khi đủ: 3a-2 đã ghép và chạy thật được (S1–S4, S8 theo #5 — **chưa duyệt**), S6 (cách ly + `tram-kiem`), S7 (repo nháp GitHub + branch protection + `gh` của trạm, #2), và **Đại ca cho phép tốn quota**. Người làm: Đại ca hoặc Em theo lệnh Đại ca, trên máy B, từng bước, dừng ngay khi một bước sai. Không tự bật `giao_viec.bat` trên HR Codex — chỉ repo nháp.

- [ ] **Bước 1 — cấu hình (Đại ca sửa tay `~/.tram/cau-hinh.yaml` của tài khoản trạm):** khối `giao_viec:` như docstring `tram/cau_hinh/giao_viec.py`, `bat: false`; `thu_muc_kiem` ngoài `~/.tram`; `principal_kiem` theo cơ chế S6 đã chốt. `du-an/<repo-nhap>.yaml`: `lenh_cho_phep`, `lenh_kiem_mac_dinh`, `moi_truong_kiem` (DB test), `nhanh_chinh: main`.
- [ ] **Bước 2 — kho kiểm:** `tram giao kho-kiem <repo-nhap>` → đọc kế hoạch (remote GitHub đúng repo nháp, đích `~/.tram/kho-kiem/<repo-nhap>`) → gõ `dong-y`. Kỳ vọng: in SHA `origin/main`.
- [ ] **Bước 3 — kiểm sẵn sàng:** `tram giao kiem` → **mọi mục XANH** trừ `giao_viec.bat` (vàng). Đặc biệt năm mục `principal: …` (G7, G20) và `file quyền coder/qc` (G5). Còn đỏ → dừng, không bật.
- [ ] **Bước 4 — chạy khô:** `tram giao tick --thu` → `pha nhanh: …` không lỗi.
- [ ] **Bước 5 — bật:** `bat: true`, khởi động lại `tram api` (launchd). Repo nháp có 3 bead `bug` ở cột 1, mỗi bead có `acceptance_criteria` máy đọc được. Kỳ vọng (G8 spec 4): mỗi bead đi `code` (B/claude-1) → kiểm lại đạt (dưới `tram-kiem`) → `qc` (B/claude-2, khác khe — G2) → cột 3 với bằng chứng gắn `commit_ban_giao`; dashboard thẻ cột 3 có mục "Bộ giao việc" với link/lệnh PR, không cảnh báo lệch; Telegram báo.
- [ ] **Bước 6 — G5 thật:** trong lúc một bead đang kiểm lại, cho agent của bead khác `tram bao --bi "thử G5"` → escalation ở cột 2 trong ≤ 3 phút (đo bằng `luc` của `bao.bi` và `escalation.tao`).
- [ ] **Bước 7 — kéo cột xen kẽ:** kéo một bead cột 1 sang cột 2 ngay khi một khe vừa rảnh → không có `giao.nhan` cho bead đó (G3 spec 4).
- [ ] **Bước 8 — ghi kết quả** vào `docs/spikes/<ngày>-chay-thu-4a-repo-nhap.md` (lệnh, thời điểm, SHA, sự kiện, ảnh dashboard đã che bí mật) và báo Đại ca; Đại ca tự tạo/merge PR (trước 4c), bấm Duyệt.

---

## Sơ đồ đợt chạy

Số dưới đây là số ca dự kiến sau chỉnh review tĩnh, chưa chạy. N₀ đo sau1b-2T9 và3a-2; không dùng số bản sao cũ thay kết quả main.

```
Đợt 1: T1, T2, T3, T4, T5, T6 → N₀ + 37 (tăng 37)
Đợt 2: T7                     → N₀ + 53 (tăng 16)
Đợt 3: T8                     → N₀ + 57 (tăng 4)
Đợt 4: T9                     → N₀ + 62 (tăng 5)
Đợt 5: T10, T11, T12          → N₀ + 75 (tăng 13; frontend +3 test node)
Đợt 6: T13                    → N₀ + 78 (tăng 3)
(T14: chờ cổng — không chạy)
```

| Task | Độ khó | Đợt | Phải xong trước | File chạm (ngoài test) | Test mới | Toàn bộ sau task (trên main đợt trước) |
|---|---|---|---|---|---|---|
| 1 | de | 1 | — | `tram/giao_viec/principal_kiem.py`, `tram/cau_hinh/giao_viec.py` | 15 | N₀ + 15 |
| 2 | de | 1 | — | `tram/giao_viec/quyen.py`, `tram/giao_viec/de_xuat.py` | 2 | N₀ + 2 |
| 3 | de | 1 | — | `tram/giao_viec/kho_kiem_tao.py`, `tram/giao_viec/git_kiem.py` | 4 | N₀ + 4 |
| 4 | kho | 1 | — | `tram/giao_viec/doc_beads.py`, `tram/giao_viec/doc_lai.py`, `tram/giao_viec/bo.py` | 10 | N₀ + 10 |
| 5 | de | 1 | — | `tram/giao_viec/kiem_lai.py` | 4 | N₀ + 4 |
| 6 | de | 1 | — | `tram/phieu/bao.py` (có điều kiện) | 2 | N₀ + 2 |
| 7 | kho | 2 | 3, 4, 5 | `tram/giao_viec/tick_cot_3.py`, `tram/giao_viec/tick.py`, `tram/giao_viec/tick_pipeline.py` | 16 | N₀ + 53 |
| 8 | kho | 3 | 7 | `tram/giao_viec/luong.py` | 4 | N₀ + 57 |
| 9 | kho | 4 | 1, 4, 8 | `tram/giao_viec/noi_that.py`, `tram/api/phu_thuoc.py`, `tram/api/tho.py`, `tram/cli_dich_vu.py` | 5 | N₀ + 62 |
| 10 | de | 5 | 1, 2, 3, 9 | `tram/giao_viec/kiem_san_sang.py`, `tram/giao_viec/lenh.py`, `tram/cli_dich_vu.py` | 9 | N₀ + 71 |
| 11 | de | 5 | 3, 9 | `tram/suy/giao_viec.py`, `tram/api/tuyen_giao.py`, `tram/api/app.py` | 4 | N₀ + 66 |
| 12 | de | 5 | — | `frontend/src/giao_viec.js`, `frontend/src/thanh/OGiaoViec.vue`, `frontend/src/trang/CongViec.vue`, `frontend/src/thanh/TheBead.vue`, `frontend/src/trang/NganBen.vue` | 3 (node) | N₀ + 62 |
| 13 | de | 6 | 1–12 | (chỉ test) | 3 | N₀ + 78 |
| 14 | — | chờ cổng | mọi cổng | (không mã) | — | — |

File dùng chung giữa các đợt (đúng một task sở hữu mỗi lần sửa): `tram/cli_dich_vu.py` — Task 9 (đợt 4, `_api`) rồi Task 10 (đợt 5, `them_lenh`). Không file nào bị hai task cùng đợt sửa. Task 3 (đợt 1) chỉ *import* `kho_kiem_co_san` từ `bo.py` mà Task 4 (cùng đợt) sửa — không xung đột.

## Để sau (chờ cổng / lát khác) — không lập task code ở plan này

| Phần | Spec | Chờ | Plan này chừa sẵn |
|---|---|---|---|
| Bật bộ giao việc thật (`giao_viec.bat: true`), chạy thử repo nháp 3 bug | §16 mục 4, #4 | 3a-2 chạy thật, S1–S4/S8 (#5 chưa duyệt), S6, S7, Đại ca cho tốn quota | Task 14, `tram giao kiem` |
| Tạo principal `tram-kiem`, sudoers/ACL, lệnh `trao_quyen` thật, kill nhóm tiến trình dưới principal khác (G20) | spec 3 §7.3 mục 5, 7 | S6 (#3) — có thể nằm trong `tram chu cai-dat` của 3a-2 | `PrincipalKiem` (`boc`, `trao_quyen`), 5 mục `principal: …` của `tram giao kiem` |
| Đăng nhập `gh`/credential GitHub của tài khoản trạm cho clone/fetch kho kiểm | #2 | S7 | `tram giao kho-kiem` (`GIT_TERMINAL_PROMPT=0` — thiếu credential thì lỗi rõ) |
| Công bố ref (CAS), `da-push`, xoá ref tạm | spec 3 §6.4, §11 | 3a-2 | 4a-2 chỉ đọc `giao.cong_bo` + kiểm ref remote trước cột 3 (G3, G13) |
| Kiểm lại song song nhiều bead | §10 | không cần ở 4a (G12) | pha Git tuần tự |
| Hàng "Feature xong, chờ đóng", `POST /api/phieu/kiem`, luồng `spec` | §7 | 4b | — |
| Tự mở PR + xác minh merge, cờ đỏ gitnexus, lớp 5 | §3 | 4c | `pr` trong `bead.vao_cot_3` vẫn `None`; dashboard hiện link/lệnh tay |
| Hiện "bộ giao việc tắt/bật" và nút bật/tắt trên dashboard | spec 2 | 2c (nếu Đại ca muốn) | `GET /api/giao-viec` trả `bat` |

> **Ghi chú 15/10/2026** (không đổi bảng trên và Task 14): #5 mới mở một phần. Các phần Task 14 cần đều **chưa duyệt**: S1–S4 và S8, S6 (tạo user/sudoers), S7 (repo GitHub), bật giao việc, tốn quota. Xem [quyết định 13/10, mục "Ghi chú 15/10"](../quyet-dinh/2026-10-13-tra-loi-cau-hoi-gop.md). Thêm hai điều kiện chạy thật mà Task 14 chưa ghi: (1) `tram-noi-bo-token` phải được tạo ở 1b-2 Task 10 bước 1 (`bs-8eh.1`), xem ghi chú "Để sau" của plan 3a-2; (2) `vn.tram.api` chưa cài trên máy B, nên bước "khởi động lại `tram api` (launchd)" cần 2a Task 26 cài dịch vụ trước. Principal kiểm hiện phải khai ở hai chỗ (`giao_viec.principal_kiem` và `cach_ly.tram_kiem`) với cùng một user, cho tới khi xong `bs-urj.12`.

## Tự review

**1. Độ phủ (phần lát 4a còn lại sau 4a-1)**

| Yêu cầu | Task | Kiểm bằng |
|---|---|---|
| Nối `chon` vào `PhuThuocApi.chon_phieu`, router `/api/tho/nhip` truyền `con_hop_le` (spec 4 §13; 3a-1 G11, spec 3 §17) | 9, 13 | `test_router_nhip_truyen_con_hop_le`, `test_bat_thi_noi_chon_con_hop_le_va_hai_luong`, `test_http_phat_phieu_qua_bo_giao_viec` |
| Đọc lại Beads ngay trước cấp, huỷ khi nội dung/trạng thái đổi; test kéo cột xen kẽ (spec 4 §5.1; review Codex 4a-1 G3) | 4, 13 | `test_keo_sang_cot_2_sau_snapshot_thi_khong_claim`, `test_keo_cot_giua_claim_va_cap_thi_huy`, `test_tieu_chi_doi_sau_snapshot_thi_huy`, `test_bead_chan_moi_mo_lai_thi_huy`, `test_http_keo_cot_xen_ke_khong_cap` |
| `BoDemBeads` cho bộ chọn (4a-1 rủi ro c) | 4 | `test_bo_dem_khong_goi_bd_moi_lan_xin_viec`, `test_khong_doi_thi_de_xuat_va_danh_dau_bo_dem_cu` |
| Tick 2 phút trong tram-api + `tram giao tick` (§10) | 7, 8, 9, 10 | `test_bat_thi_noi_…_hai_luong`, `test_lap_giu_nhip_co_dinh_va_song_qua_loi`, `test_khoa_mot_vong_moi_pha`, `test_cli_tick_va_kho_kiem` |
| Tách kiểm lại dài khỏi escalation; G5 ≤ 3 phút với suite dài, lỗi Git một dự án, restart (§10 "ràng buộc lúc nối 4a-2") | 7, 8, 13 | `test_g5_bi_thanh_escalation_trong_khi_kiem_lai_dai`, `test_g5_hai_du_an_kiem_lai_dai_va_git_hong`, `test_fetch_qua_han_chi_dem_loi_khong_chan_escalation`, `test_khoi_dong_lai_giua_kiem_lai_thi_vong_sau_kiem_lai_lai`, `test_pha_nhanh_khong_dung_git` |
| Clone/cập nhật kho kiểm từ remote (S7, #2) | 3, 10 | `test_tao_moi_roi_cap_nhat`, `test_kho_co_san_tro_remote_khac_thi_tu_choi`, `test_cli_tick_va_kho_kiem` |
| Principal `tram-kiem` (S6): chạy kiểm lại dưới principal, trao quyền ghi sau môi trường kiểm, kiểm chứng khi chạy thật | 1, 5, 7, 10 | `test_trao_quyen_sau_moi_truong_kiem_truoc_lenh`, `test_kiem_lai_dung_thu_muc_va_trao_quyen_cua_bo`, `test_principal_dat_moi_muc`, `test_principal_sai_tung_muc_la_do` (4 ca), `test_khong_dung_duoc_lenh_qua_han_la_do` |
| `giao.cong_bo` thật (S7): đọc sự kiện của 3a-2; ref remote lệch → không cột 3 | 7 | `test_cot_3_nhanh_bi_day_ngoai_luong` |
| Phiên bản file quyền | 2 | `test_phien_ban_theo_noi_dung_file`, `test_khoa_chong_trung_doi_khi_file_quyen_doi` |
| Dashboard: lý do không giao + link/lệnh PR (§5.1, §6.4 mục 4) | 11, 12 | `test_ly_do_hien`, `test_thong_tin_pr_github_va_lech`, `test_api_giao_viec`, `giao_viec.test.mjs` (3) |
| `nhanh-bi-day-ngoai-luong` trong `LY_DO_BI` | 6 | `test_ly_do_bi_nhan_nhanh_bi_day`, `test_bao_bi_nhanh_bi_day_thanh_escalation` |
| Chạy thử repo nháp 3 bug (#4) | 14 | chờ cổng |

**2. Quét placeholder:** không có "TBD/TODO/tương tự Task N"; mọi bước mã có khối mã đầy đủ (file mới nguyên văn; file có sẵn bằng bản vá sinh từ bản sao đã chạy, hoặc script chèn theo mốc đã chạy); mọi lệnh có kết quả mong đợi. `<model đang thực thi>` trong lệnh commit là cố ý.

**3. Khớp chữ ký:** khối Interfaces lấy từ chính mã đã chạy. Điểm nối: `BoGiaoViec(…, doc_beads, trao_quyen, thu_muc_kiem)` (4) ↔ 7, 9, 13; `con_nguyen(bd, da, cu, *, sau_claim)` (4) ↔ `bo._chot`; `kiem_lai(…, trao_quyen)` (5) ↔ `tick_pipeline._kiem_lai` (7); `fetch(kho, *, thoi_gian_cho)` (3) ↔ `tick._git` (7); `vong_nhanh(bo, *, thu)`, `vong_git(bo)` (7) ↔ 8, 10; `bat_dau_luong_giao(bo, dung, *, chu_ky)` (8) ↔ 9; `dung_bo_that(cg, ch, *, bo_dem, thu_muc_du_an)`, `cac_du_an_that` (9) ↔ 10; `PhuThuocApi.bo_giao`, `.con_hop_le_phieu` (9) ↔ 11, 13; `url_origin`, `github_repo` (3) ↔ 10, 11; `PrincipalKiem.boc_lenh`, `.trao` (1) ↔ 9, 10. Với 3a-1/4a-1: `xu_ly_nhip(…, chon, con_hop_le)`, `chay_mot_lenh(…, boc, cho_kill)`, `KetQuaLenh(lenh, ket_qua, tom_tat, digest_log, ma_thoat, het_gio)`, `MucKiem(muc, muc_do, chi_tiet)`, `KhoSuKien.moi_nhat(du_an, bead_id, loai)`, `BoDemBeads.lay/phien_ban/danh_dau_cu` — đúng mã trên bản sao.

**4. Đã chạy thử (13/10):** dựng bản sao trong scratchpad, không đụng repo thật: `git archive main` (`1b685de`, 3a-1 đã ghép tới Task 22) + mã các plan trước **dựng từ văn bản plan** (3a-1 Task 23–25, 1b-3, 2b, 4a-1, 1b-2 Task 1–8; 1b-2 Task 9 bỏ vì gói `mcp` không có trong cache offline; 3a-2 chưa có) → **1457 passed**. Áp plan này theo đúng sơ đồ đợt, commit từng đợt, trước tiên trên bản sao chưa có 1b-2: 1361 → 1393 sau đợt 1 → … → 1425 sau đợt 6 (đo thật đầu, đợt 1 và cuối; +64 đúng bảng); rồi đặt lại sáu commit đó lên bản sao có 1b-2 Task 1–8: **1457 → 1521 passed** (+64). Bản vá trong plan được kiểm lại `git apply --check` và ba script mốc chạy lại nguyên văn trên bản sao có 1b-2 — đều áp sạch; test có luồng (`test_luong_giao.py`, `test_kich_ban_4a2.py`) chạy 3 lần liên tiếp đều xanh. Frontend (`node_modules` của repo thật, chỉ đọc): `npm run kiem` 21 pass, `kiem-an-toan` sạch, `npm run build` xanh. Thông báo fail ở Step 2 là kết quả chạy thật trên bản sao trước khi có mã của task. Chưa chạy được: phần phụ thuộc 3a-2 (giả định G3–G6 — bước "Kiểm hợp đồng với 3a-2" trong Chuẩn bị), mọi lệnh chạy thật của Task 10/14.

**5. Rủi ro còn lại (Đại ca biết):** (a) khe đua giữa lần đọc Beads cuối và `COMMIT` cấp phiếu (G9 — đã chấp nhận ở 4a-1 G3); (b) `sudo`/cơ chế S6 có thể làm mất `APP_ENV` hoặc không kill được nhóm tiến trình (G7, G20) — `tram giao kiem` chặn bật khi đỏ; (c) restart giữa kiểm lại để lệnh mồ côi chạy tới hết (G19); (d) pha Git tuần tự — bead chờ sau kiểm lại dài (G12); (e) bốn file dùng chung với 3a-2 (`phu_thuoc.py`, `tho.py`, `app.py`, `cli_dich_vu.py`) — script mốc dừng nếu 3a-2 đổi đúng dòng mốc; sáu file 4a-1 sửa bằng bản vá — 3a-2 không được sửa các file này (G6); (f) nhận định segfault của bản sao cũ đã lỗi thời: main `eb97f87` sửa bs-64w; không bỏ test hoặc chạy lại để che lỗi.

## Cần sửa spec sau (Codex/Đại ca đối chiếu khi review)

- **Spec 4 §10, §13:** tick là **hai pha, hai luồng** (`vong_nhanh` không Git, `vong_git`), khoá `flock` mỗi pha, `tram giao tick [--thu]`, `tram giao kho-kiem`, `tram giao kiem`; module thêm `doc_beads`, `doc_lai`, `kho_kiem_tao`, `principal_kiem`, `quyen`, `tick_cot_3`, `luong`, `noi_that`, `lenh`, `kiem_san_sang` (G11, G14, G15).
- **Spec 4 §5.1 "giới hạn nhất quán":** mô tả cụ thể lần đọc lại (dấu nội dung, hai lần quanh claim, huỷ sau claim để bead `in_progress`) (G9).
- **Spec 4 §6.4 / §9:** trước cột 3 so ref công bố trên remote với `giao.cong_bo`; lệch → `nhanh-bi-day` nguồn `ref-<chu kỳ>-<sha remote>` (G13).
- **Spec 4 §6.4 mục 4 / spec 2:** hợp đồng `GET /api/giao-viec` và mục "Bộ giao việc" trên dashboard (G16).
- **Spec 2 §12.5 (khoá `cau-hinh.yaml`):** thêm `giao_viec:` (G2); `bat: true` cần `principal_kiem`.
- **Spec 3 §7.3 mục 5:** worktree kiểm lại ở `thu_muc_kiem` ngoài `~/.tram`; `trao_quyen` nhận đối số thư mục (G7, G8); tiêu chí "dừng được lệnh quá hạn dưới principal khác" vào bộ kiểm chứng S6 (G20).
- **Spec 3 §7.2:** `phien_ban_quyen` = băm nội dung `vai/quyen/<vai>.json` (G5).
- **Plan 3a-2 (đối chiếu):** G3 (dạng `giao.cong_bo`, `ref`), G4 (`LY_DO_BI`), G5 (đường dẫn file quyền), G6 (giữ chữ ký/mốc 3a-1).

## Đồng bộ review độc lập đợt 3 — 14/10/2026

Chỉ kiểm tra tĩnh văn bản/mã trên `main eb97f87`; chưa chạy mã mẫu hay test. Con số bản sao cũ là lịch sử, không phải chứng cứ cho bản sửa này. N₀ phải đo sau `1458 + 1b-2 T9 + 3a-2`; tổng tăng dự kiến của plan là **78 Python + 3 node** (thêm14Python: T1+1, T4+3, T5+1, T7+9). Sau từng task chạy cả bộ test task và hồi quy liên quan theo TDD; không bỏ SSE/không cộng tay suite lỗi. File mới Task7 phải thêm vào lệnh `git add` cùng tick/pipeline.

- **G6/G7/G20 đổi:** dùng `chay_mot_lenh(..., kill=...)` đã có sau3a-2; `PrincipalKiem.kill_nhom(pgid,sig)` chạy cùng prefix principal, nối qua `BoGiaoViec.kill`, `kiem_lai`, tick và readiness. Fixture truyền kill giả chỉ chứng minh nối đúng, S6 vẫn phải chứng minh timeout dừng process tree thật và không giữ credential trạm.
- **G22 — hợp đồng mới (gate ADR):** `BoGiaoViec.adr_hop_le(du_an, bead)->bool`, mặc định False, chạy trong bước đọc lại ngoài giao dịch cấp phiếu. Bead chạm hàng rào chỉ tiếp tục khi có decision `blocks` đã đóng (#6 giữ nguyên) hoặc callback xác minh ADR tồn tại ở đúng repo, được Đại ca duyệt, và bao phủ nhiệm vụ. Mention/regex, phủ định, draft, sai repo không phải bằng chứng. Chưa có schema approved ADR đã chốt nên **không cung cấp adapter permissive**; việc dựa riêng vào ADR dừng an toàn tới khi Đại ca chọn nguồn và adapter được kiểm. Đây là gate vận hành còn chờ, không tuyên snapshot/lease atomic.
- **G23 — hợp đồng nội bộ mới (queue):** `viec_cua_pha(kho, du_an, *, git, gioi_han=1000)` lọc dự án/pha ngay trong SQL trước LIMIT. Không đổi giao diện `cong_viec_cho` công khai cho consumer khác. Không dùng queue Git lỗi của dự án A để làm đói escalation dự án B.
- **bs-s52:** main đã nhận đúng marker kể cả decision đóng; chỉ thêm hồi quy crash→đóng→đối soát→reset budget đúng một lần.
- **bs-ecd:** khi lần kiểm code vẫn đúng và QC mới nhất sau kiểm đã công bố rồi thu hồi/bi/hết hạn mức chưa có `qc.ket_qua`, công bố mới nhất phải thuộc đúng `luot` QC đó; giao lại QC. Ref lượt khác, tiêu chí đổi, trả cột đều không tái dùng. Không đủ chứng cứ thì không đi cột3.

## Sửa khi code (14/10/2026) — mặc định `kill`

Plan sau review ghi mặc định `kill = os.killpg` ở `bo.py` (Task 4), ở `kiem_lai` và helper test (Task 5), và ở readiness (Task 9). Nhưng `chay_mot_lenh` **luôn** gọi `kill(pgid, SIGKILL)` sau khi lệnh chính thoát để dọn con cháu, mà lúc đó nhóm thường đã mất. `os.killpg` khi ấy ném `ProcessLookupError`: Task 5 áp nguyên văn thì 7 test fail. Vì vậy mọi mặc định đổi thành `tram.kiem.chay_lenh._kill_nhom`. Hàm này vốn đã là mặc định của `chay_mot_lenh` và bỏ qua `ProcessLookupError`/`PermissionError`.
- `bo.py` cần thêm `from tram.kiem.chay_lenh import _kill_nhom`. Task 4 đã ghép với `os.killpg`, Em sửa bằng commit riêng trên `main`.
- `kiem_lai.py` thay `import os` trong bản vá bằng import `_kill_nhom`.
- Task 9: `kill=pk.kill_nhom if pk else _kill_nhom`. File có dòng này cần import `_kill_nhom`.
- `PrincipalKiem.kill_nhom` không dùng `check=True`, nên `/bin/kill` trả mã khác 0 khi nhóm đã thoát cũng không ném lỗi. Không cần sửa.

## Ghi chú triển khai (code 14/10/2026)

- **Kết quả:** đã code Task 1–13. Task 14 chờ cổng.
  - Thêm **78 test Python**, đúng kỳ vọng sau review. Sau Task 13, `main` có 1692 passed.
  - Thêm **3 test node** (21/21). Build xanh.
- **Chạy song song với 3a-2:** đợt 1–5 chạy cùng 3a-2 Task 17–20, hai bên không sửa chung file nào.
- **Lệch plan:**
  1. **Mặc định `kill`:** xem mục "Sửa khi code (14/10/2026)". Đổi `os.killpg` thành `_kill_nhom` ở `bo.py`, `kiem_lai`, helper test của Task 5 và `noi_that.py` (Task 9, thêm import). Các dòng ngữ cảnh trong plan 4c cũng đã đồng bộ.
  2. **Task 9:** bỏ `import os` thừa trong `noi_that.py`.
  3. **Task 5:** số test fail và pass ghi ở Step 2 và Step 4 chưa cập nhật theo test thứ 4 do review thêm vào (thực tế 4 failed, 16 passed).
- **Script chèn theo mốc** (Task 9, 10, 11): mọi mốc khớp đúng một chỗ. Các dòng do script chèn đều có trong plan, nằm ở dạng chuỗi Python.
- **Còn chờ cổng:** Task 14 (repo nháp 3 bug, principal `tram-kiem` thật, S6/S7, cho phép tốn quota). Cổng ADR (G22) vẫn đóng cho tới khi Đại ca chọn nguồn ADR đã duyệt.

## Đồng bộ quyết định sau review đợt 4

D16 đã chốt chỉ decision blocks đóng, không còn task chọn adapter ADR. Sau 3c principal chỉ khai cach_ly.tram_kiem và gốc giao_viec.thu_muc_kiem; không chép cấu hình argv cũ. _kill_nhom hợp lý cho fixture cùng user, nhưng bỏ qua PermissionError không chứng minh cleanup principal thành công; vẫn cần S6/R1.
