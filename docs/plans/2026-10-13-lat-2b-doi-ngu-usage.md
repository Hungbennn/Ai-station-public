# Lát 2b — Đội ngũ AI + Usage — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use ai-skills:subagent-driven-development (recommended) or ai-skills:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Thêm vào dashboard màn **Đội ngũ AI** (mỗi khe một thẻ: máy, CLI, tên gợi nhớ, vai ưu tiên, trạng thái, hạn mức còn lại + giờ reset, số phiên; nút tắt/bật khe và đóng cầu dao; luật vai ↔ khe; bảng điểm thợ phần tính được) và màn **Usage** (token + chi phí theo ngày/tuần/khe/dự án từ sự kiện trạm, kèm số liệu `ccusage --json` qua adapter), cùng mục "Hệ cần xem" và tin Telegram khi cầu dao khe ngắt / khe hết hạn mức.

**Architecture:** Không có kho trạng thái mới (Q12): màn Đội ngũ đọc `trang_thai_khe()` của lát 3a-1 (spec 3 §10.1) qua `KhoPhieu`, bảng điểm đọc bảng `phieu` + `lan_chay` của kho phiếu; Usage tổng hợp sự kiện `chay.xong` (khe) và `cham_cot.ket_qua` (bộ chấm 1a, Claude API) bằng cột `token_vao/token_ra/mo_hinh` đã lưu riêng (spec 2 §12.2). Thao tác tắt/bật khe và đóng cầu dao đi qua khung thao tác bền của 2a (`chay_thao_tac`, bảng `thao_tac`) và ghi **bằng đúng hàm của 3a-1** (`bat_tat_khe`, `dong_cau_dao` trong `KhoPhieu.giao_dich()`), nên nhịp tim (dừng mềm `khe-tat`), cấp phiếu và `trang_thai_khe` thấy y như lệnh `tram tho tat-khe`. `ccusage` là công cụ ngoài: chạy bản cài cố định qua adapter `DocCcusage` (kiểm `--version`, môi trường tối thiểu, `--offline`) + bộ đệm — test chỉ dùng hàm `chay` giả; phần chạy thật **chờ chạy thật**. Frontend thêm hai trang Vue (`/doi-ngu`, `/usage`), luật hiển thị thuần trong `luat_doi_ngu.js` (test `node --test`), SSE thêm sự kiện `doi_ngu_doi`.

**Tech Stack:** Python 3.12 (`uv`), FastAPI 0.143.0 + uvicorn 0.54.0, pydantic 2, SQLite stdlib (WAL — `mo_ket_noi`), `subprocess` stdlib cho ccusage, `pytest`; Vue 3.5.43 + vue-router 5.4.0 + Vite 8.3.4 + `@vitejs/plugin-vue` 6.0.10 (đã khoá ở 2a), `node:test`. **Không thêm phụ thuộc nào vào repo.** `ccusage` (MIT) **không** là phụ thuộc của repo — Đại ca cài cố định khi chạy thật (G6).

**Spec:** [docs/specs/2026-10-12-phan-2-dashboard.md](../specs/2026-10-12-phan-2-dashboard.md) (ĐÃ DUYỆT) — §5 "Lát 2b — cần phần 3" mục **5.4**, §4 (bảo mật), §5.2 (hàng "Hệ cần xem" — cầu dao khe), §6 (tin cầu dao khe / hết hạn mức), §7 (API lát 2b), §8 (ccusage — "chốt ở plan 2b"), §12.2–§12.3. Đọc kèm: spec 3 [§8.1–§8.3, §10, §10.1](../specs/2026-10-13-phan-3-may-tho-han-muc.md) (ĐÃ DUYỆT) · kiến trúc [Q12, Q14, Q15](../specs/2026-10-12-tram-dieu-phoi-kien-truc.md) · spec 4 [§5.3, §12 "Bảng điểm thợ"](../specs/2026-10-13-phan-4-giao-viec.md) (**chưa duyệt** — chỉ để biết công thức; không lập task phần 4) · plan [3a-1](2026-10-13-lat-3a-1-may-tho.md) (Task 4, 5, 13, 15, 17, 18, 21, 23, 24) · plan [2a](2026-10-13-lat-2a-dashboard.md).

## Global Constraints

- **Điều kiện tiên quyết:** plan **3a-1** và plan **1b-3** đã thực thi và ghép vào `main` (thứ tự code đã chốt: `3a-1` → `1b-3` → `2b`). Mốc test gọi là **N₀** = số `passed` của `uv run pytest -q` trên `main` lúc đó; trên bản dựng thử (main `891ae04` = 720 test + 3a-1 = 295 test, **chưa có 1b-3**) N₀ = **1015** — mọi con số dưới đây viết dạng `N₀ + k` kèm số khi 1b-3 không thêm test. Frontend: M₀ = số test `node --test` (2a: **7**). N₀ test cũ phải xanh suốt plan.
- **Kiểm tài liệu 13/10:** các sửa sau review chỉ được đọc tĩnh, chưa chạy mã/tests/build. Số test `N₀ + 44`, `M₀ + 6` là kỳ vọng; ca hồi quy bổ sung nằm trong hàm test cũ nên không đổi số lượng. Các bằng chứng chạy thử bên dưới là lịch sử bản trước review.
- **TDD:** mỗi task viết test trước, chạy thấy fail (thông báo ở Step 2 là kết quả chạy thật), viết mã, chạy thấy pass. Task giao diện `.vue` (10, 12) không có test đơn vị riêng — cổng kiểm là `npm run kiem` (luật thuần + quét `v-html`) và `npm run build` (biên dịch template), như plan 2a.
- **Mỗi file nguồn ≤ ~120 dòng** (cả `.vue`; dài nhất của plan: `tram/api/phu_thuoc.py` 68, `TheKhe.vue` 70, `MucPheDuyet.vue` 70). Định danh tiếng Việt không dấu như mã hiện có. Giờ lưu UTC `YYYY-MM-DDTHH:MM:SSZ`; giờ hiển thị `Asia/Ho_Chi_Minh`; ngày/tuần của Usage theo giờ Việt Nam (tuần ISO). Hàm nghiệp vụ nhận `bay_gio`/`luc` tiêm được (`PhuThuocApi.dong_ho` của 3a-1).
- **Mỗi task một worktree, một nhánh, một commit**, tạo từ `main` **sau khi đã ghép đợt trước** ("Chuẩn bị", "Sơ đồ đợt chạy"). Task cùng đợt không sửa chung file (ngoại lệ: `tram/usage/__init__.py` rỗng — Task 3, 4 cùng tạo, giống hệt từng byte). Không push, không merge hộ.
- **Không thêm phụ thuộc mới** (Python lẫn npm). Không gọi mạng ngoài, không `npx`.
- **Test không:** gọi Claude/Codex/Ollama thật, gọi **ccusage thật** (mọi lời gọi đi qua tham số `chay` giả; test duy nhất dùng `subprocess.run` thật chỉ trỏ tới đường dẫn **không tồn tại** để kiểm lỗi `FileNotFoundError`), gọi mạng, đọc/ghi Keychain, đụng `~/.tram` thật (`TRAM_HOME` tạm — `tests/conftest.py`), chạy `launchctl`, tạo user macOS, chạy `bd` trên repo thật, đọc file đăng nhập CLI hay log `~/.claude`.
- **Đường ghi khe duy nhất:** dashboard chỉ ghi `khe.bat`, `khe.tat`, `khe.cau_dao_dong` bằng `bat_tat_khe` / `dong_cau_dao` của 3a-1 bên trong `KhoPhieu.giao_dich()` — không `INSERT` sự kiện khe bằng đường khác, không bảng khe riêng (G3).
- **Bảo mật (spec 2 §4):** mọi `POST` mới dùng `yeu_cau_ghi` của 2a (đúng một header `Tailscale-User-Login` ∈ `dai_ca_logins` + `X-Tram: 1` + `Origin == https://<ten_may_b>`) và thân có `ma_thao_tac` (8–64 ký tự) + `expected_version`; Bearer token máy thợ không mở được nhóm này. Frontend theo quy ước 2a: CSP chặt (component `.vue` dịch sẵn; `<style scoped>` được Vite tách ra file `.css`), kiểm `Host` (421), cấm `v-html`/`:innerHTML`/`innerHTML`…(`kiem-an-toan.mjs`), chuỗi từ server hiển thị bằng nội suy `{{ }}`; server `lam_sach` tiêu đề bead, tên gợi nhớ. **Không bao giờ hiện email** (§5.4): tên gợi nhớ chứa `@` → hiện `khe_id` (G12). Telegram chỉ mang mã khe + loại tin (§4 mục 5).
- **ccusage chỉ cho màn Usage, không dùng để chặn giao việc** (spec 3 §8.1). Bản cài cố định, đúng phiên bản trong cấu hình, không tự cập nhật (Q15, spec 2 §8).
- **Cổng chạy thật không chặn plan/code** (Đại ca chốt "code xong hết rồi mới chạy thật"): phần cần ccusage thật, hạn mức thật (S1), quyền đọc log của khe (S6), tailnet (#5) ghi **"chờ chạy thật / chờ spike"** và không đánh dấu sẵn sàng triển khai.
- Lệnh kiểm: `uv run pytest -q` từ gốc worktree; trong `frontend/`: `npm run kiem` và `npm run build`.

## Phụ thuộc đã có (main + plan trước) — dùng, không sửa trừ chỗ ghi rõ

| Thứ dùng | Ở đâu (plan) | Plan 2b dùng ở |
|---|---|---|
| `KhoPhieu(duong_dan)`: `.db`, `.giao_dich()`, `.ghi_su_kien(du_an, loai, du_lieu, *, luc, bead_id=None, tac_nhan='tram/api', **cot)`, `.phieu_hieu_luc_cua_khe`; `DU_AN_TRAM = "_tram"`; `chuoi_gio`; bảng `phieu`, `lan_chay`, `nhip_tim` | `tram/phieu/kho.py`, `luoc_do.py` (3a-1 Task 13) | Task 1, 3, 5, 8, 9, 11 |
| `su_kien_khe(kho, khe_id, loai) -> (id, loai, du_lieu, luc) \| None`, `cac_khe`, `khe_dang_bat`, `dang_ky_khe`, `LOAI_BAT_TAT`, `KheLa`; **`bat_tat_khe(..., bat, vi_sao, tac_nhan, luc)` (sửa ở Task 1)** | `tram/phieu/khe.py` (3a-1 Task 15) | Task 1, 5, 8, 9, 11 |
| `trang_thai_cau_dao(kho, khe_id, bay_gio) -> TrangThaiCauDao(ngat, ly_do, toi_luc)`, `ngat_cau_dao`, `LOAI`; **`dong_cau_dao(..., ly_do, luc, tac_nhan)` (sửa ở Task 1)** | `tram/phieu/cau_dao.py` (3a-1 Task 15) | Task 1, 5, 8 |
| `ghi_nhip`, `han_muc_hieu_luc` | `tram/phieu/nhip_tim.py` (3a-1 Task 15) | test Task 9 |
| `TrangThaiKhe(khe_id, cli, ten_goi_nho, vai_uu_tien, trang_thai, phieu, han_muc, cau_dao, so_phien, nhip_cuoi)`, `trang_thai_khe(kho, *, bay_gio, ch)` — sáu giá trị `tat|mat_ket_noi|loi|can_nguoi|lam|ranh` | `tram/phieu/trang_thai.py` (3a-1 Task 21) | Task 9 |
| `HanMuc`, `CuaSo`, `co_chua_biet`; `duoc_nhan`, `cham_nguong_ngung` | `tram/han_muc/` (3a-1 Task 4) | Task 9 |
| `CauHinhTram.han_muc: CauHinhHanMuc(ngung, tuan_chi_uu_tien, tuoi_toi_da_gio)`, `.tho` | `tram/cau_hinh/tram.py` (3a-1 Task 5) | Task 9, 11 |
| `VAI_CUA_BUOC = {"code": "coder", "qc": "qc", "spec": "spec"}` | `tram/phieu/mo_hinh.py` (3a-1 Task 11) | Task 9 |
| `danh_dau_ket_thuc(db, giao_id, ket_thuc, luc)` | `tram/phieu/ghi.py` (3a-1 Task 13) | test Task 9 |
| `PhuThuocApi(..., mo_kho_phieu=None, chon_phieu=None, doc_token_noi_bo=…, dong_ho=…)`, `phu_thuoc_that()` (**sửa ở Task 11**); `CAC_TUYEN` (**sửa ở Task 11**) | `tram/api/phu_thuoc.py`, `app.py` (3a-1 Task 23) | Task 5, 11 |
| Sự kiện `khe.dang_ky`, `khe.bat/tat`, `khe.cau_dao_ngat/dong {khe_id, ly_do, toi_luc}`, `chay.xong {giao_id, luot, khe_id, request_id, lan, ket_thuc, …, token_cache_doc, token_cache_ghi}` + cột `token_vao, token_ra, mo_hinh, thoi_gian_ms` | 3a-1 Task 15, 18 | Task 3, 5, 6 |
| Test: `kho_tam(tmp_path)`, `dat_phieu(kho, khe_id, *, luc, **kw)`, `LUC` (`tests/kho_phieu_gia.py`); `de_xuat` (`tests/phieu_gia.py`) | 3a-1 Task 11, 13 | test Task 1, 3, 5, 8, 9, 11 |
| `chay_thao_tac(kho_tt, YeuCau(ma, loai, du_an, bead_id, noi_dung, expected_version), *, kiem_moi, cac_buoc)`, `digest`, `KetQuaThaoTac`; `KhoThaoTac`; `TAC_NHAN = "dai-ca/dashboard"`; lỗi `XungDot` 409, `KhongHopLe` 422, `ChuaHoTro` 501, `KhongThay` 404 | `tram/thao_tac/` (2a Task 4) | Task 8, 11 |
| `yeu_cau_ghi`, `ThanGhi(ma_thao_tac, expected_version)` | `tram/api/bao_mat.py`, `than.py` (2a) | Task 11 |
| `gom_phe_duyet(cac_du_an, theo_du_an, kho)` (**sửa ở Task 5**), route `/api/phe-duyet` (**sửa ở Task 5**), `mot_nhip`, `LOAI_LAM_MOI` (**sửa ở Task 5**) | `tram/suy/phe_duyet.py`, `tram/api/tuyen_doc.py`, `luong.py` (2a) | Task 5 |
| `Tin`, `soan_tin`, `LOAI_TIN`, `NHAN_LOAI` (**sửa ở Task 6**), `tin_tu_su_kien` (**sửa ở Task 6**), `BoChongOn` | `tram/bao_tin/` (2a) | Task 6 |
| `lam_sach(s, n)`; `GIO_VN`; `doc_luc` | `tram/suy/lam_sach.py`, `tram/cham_cot/ghi.py`, `tram/duong_dan.py` | Task 3, 4, 5, 9, 11 |
| Frontend: `doc`, `ghi`, `thanGhi` (`api.js`); `kho`, `moLuong` (`kho.js` — **sửa ở Task 10**); `gioVN` (`luat.js`); `tuyen` (`tuyen.js` — **sửa ở Task 10, 12**); `KhungChinh.vue` menu (**sửa ở Task 10, 12**); `PheDuyet.vue`, `MucPheDuyet.vue` (**sửa ở Task 10**); lớp CSS `.chip`, `.nut`, `.nen-mo`, `.hop`, `.bang-cuon`, `.cong-cu`, `.nhan-nho`, `.ma`, `.nho`, `.loi`, `.canh-bao`, `.tieu-de` (`kieu.css`) | 2a Task 23–25 | Task 7, 10, 12 |
| `tao_pt(tmp_path, bds)`, `DAI_CA` (`tests/api_gia.py`); `goi(app, method, path, *, json_body, headers)` (`tests/asgi_gia.py`); `BdGia`, `bead` | 2a | test Task 5, 11 |

**Plan 1b-3** đã có Task 9–10: thêm API và frontend Ký ức. Các file đụng chung là `tram/api/app.py` (`CAC_TUYEN`), `tram/api/phu_thuoc.py`, `tram/api/tuyen_doc.py`, `tram/api/luong.py`, `frontend/src/tuyen.js`, `frontend/src/KhungChinh.vue`, `frontend/src/kho.js` — xem G2.

## Câu hỏi / giả định

Chỗ spec để ngỏ — Em chọn phương án an toàn nhất, không tự mở rộng phạm vi. Cột "Loại": **HỢP ĐỒNG MỚI** = giao diện/hành vi mà phần khác (2c, phần 4, 3a-2, Đại ca khi cài) sẽ dựa vào — **Đại ca cần chốt** trước khi thực thi; **lệch chữ spec** = làm khác câu chữ spec; **giả định** = chi tiết thực thi, Đại ca gạch nếu không đồng ý.

| # | Chỗ mơ hồ | Chọn | Vì sao | Loại |
|---|---|---|---|---|
| G1 | Mốc test khi 1b-3 chưa có plan | Viết số dạng `N₀ + k`; số tuyệt đối ghi kèm là khi 1b-3 không thêm test (N₀ = 1015, M₀ = 7) | Không giả định gì về 1b-3 ngoài việc nó đã ghép | giả định |
| G2 | Đụng chung file với 1b-3 | Bản vá hợp nhất sau 1b-3 phải giữ `tuyen_nho.router`, `LoiNhoKhach: 503`, `KhachNho`, `nho=KhachNho()`, `/nho`, menu Ký ức, `laSuKienNho` và `phienBanNho`. Bản vá chỉ chạm vài dòng có **dòng neo** (vd `{ path: '/phe-duyet', component: PheDuyet },`, dòng `CAC_TUYEN = (…)`). `git apply --check` lỗi vì 1b-3 đã sửa cùng chỗ → áp tay đúng các dòng `+` của bản vá vào cạnh dòng neo, giữ phần của 1b-3, chạy đủ kiểm, ghi vào mô tả commit; nếu dòng neo đã mất → dừng, báo người điều phối | Đã đối chiếu plan 1b-3 Task 9–10; đây là danh sách hợp nhất bắt buộc | giả định |
| G3 | "Bật/tắt khe → `khe.bat`/`khe.tat`" phải đi qua đường ghi của 3a-1 | Thêm tham số tuỳ chọn `them: dict \| None = None` vào `bat_tat_khe` và `dong_cau_dao` (3a-1) để mang `ma_thao_tac`; khoá chính (`khe_id`, `vi_sao`, `ly_do`, `toi_luc`) không bị `them` đè. Sự kiện do dashboard ghi: `{khe_id, vi_sao, ma_thao_tac}` / `{khe_id, ly_do: "dai-ca", toi_luc: null, ma_thao_tac}`, `tac_nhan = "dai-ca/dashboard"`. Lời gọi cũ (`tram tho tat-khe`, bộ canh) không đổi | Cùng mẫu với estop 2a (G7 plan 2a: `ma_thao_tac` khi nguồn là dashboard); crash giữa "ghi sự kiện" và "đánh dấu bước" dò lại bằng `ma_thao_tac` | **HỢP ĐỒNG MỚI** (dữ liệu sự kiện) + sửa nhỏ chữ ký 3a-1 |
| G4 | `expected_version` của một khe | `phien_ban_khe(kho, khe_id) = "<id sự kiện khe.dang_ky\|bat\|tat mới nhất>:<id sự kiện khe.cau_dao_* mới nhất>"` (`0` khi chưa có), trả trong mỗi thẻ của `GET /api/doi-ngu` (`phien_ban`) | Khe không có `updated_at`; id sự kiện tăng dần, đổi đúng khi trạng thái bật/tắt hay cầu dao đổi | **HỢP ĐỒNG MỚI** |
| G5 | Kiểm phiên bản cho từng nút | **Tắt khe: không kiểm** (như estop — G6 plan 2a: để dành hạn mức không được hỏng vì màn hình cũ). **Bật khe, đóng cầu dao: kiểm** (`409` nếu khác) ngay trong giao dịch ghi sự kiện, kể cả resume; thao tác chưa xong giữ expected_version gốc, muốn xác nhận phiên bản mới phải dùng mã mới. Đóng cầu dao khi cầu dao không ngắt → `409 "đang đóng"`. Khe chưa đăng ký → `404`. Kho phiếu chưa bật (`mo_kho_phieu = None`) → `501` | Bật/đóng làm khe nhận việc lại — Đại ca phải nhìn đúng trạng thái mới | giả định |
| G6 | ccusage — spec 2 §8 "chốt ở plan 2b" | **Cài cố định, không `npx`:** Đại ca chạy `npm install --prefix ~/.tram/ccusage --save-exact --ignore-scripts ccusage@<x.y.z>` dưới tài khoản trạm khi chạy thật, ghi vào `~/.tram/cau-hinh.yaml` khoá `usage.ccusage` (đường tuyệt đối tới `…/node_modules/.bin/ccusage`) + `usage.ccusage_phien_ban: "x.y.z"`. Trước mỗi lần chạy, adapter đọc `--version`; số `x.y.z` đầu tiên khác cấu hình → **không chạy**, báo lỗi. Lệnh: `daily --json --offline --since YYYYMMDD --until YYYYMMDD`; môi trường chỉ `PATH, HOME, LANG=C.UTF-8, TZ=Asia/Ho_Chi_Minh`; timeout 60 s; JSON đọc `{daily: [{date, inputTokens, outputTokens, cacheReadTokens, cacheCreationTokens, totalCost}]}`, trường thiếu = 0, dạng lạ → lỗi (không đoán). Bộ đệm: `ok` 10 phút, lỗi 1 phút tính từ lúc hoàn tất; một lời gọi adapter tại một thời điểm. Ngày không tồn tại và số không hữu hạn bị từ chối. **Chờ chạy thật:** cờ `--offline`, `--since/--until`, dạng JSON, cách ccusage chia ngày theo `TZ` chưa kiểm với phiên bản thật; phiên bản cụ thể Đại ca chọn lúc cài. Lỗi trả về chỉ gồm loại lỗi/mã thoát; không stderr, argv hay nội dung exception | Q15: không tự cập nhật, không tải gì lúc chạy; ccusage chưa có trên máy B | **HỢP ĐỒNG MỚI** (cách cài + khoá cấu hình) + chờ chạy thật |
| G7 | "Chi phí" của sự kiện trạm (sự kiện chỉ có token) | Bảng giá tuỳ chọn `usage.gia_usd_moi_trieu_token: {<mô hình>: {vao, ra, cache_doc?, cache_ghi?}}` do **Đại ca điền** (USD / 1 triệu token, 0–1000). **Không có giá mặc định** — Em không đoán giá. Mô hình thiếu giá → chi phí `null` ("chưa có giá") + đếm `thieu_gia`. Khe chạy gói thuê bao → trang ghi rõ "giá tương đương, không phải tiền trả thêm". ccusage có cột chi phí riêng của nó | Spec yêu cầu chi phí theo khe/dự án mà ccusage (toàn máy) không chia được | **HỢP ĐỒNG MỚI** (khoá cấu hình) |
| G8 | Nguồn và nhóm của Usage | Sự kiện `chay.xong` (khe; nhóm theo `du_lieu.khe_id`; token cache từ `du_lieu.token_cache_doc/ghi` vì spec 3 §10 không có cột riêng) + `cham_cot.ket_qua` (nhóm `"cham-cot"` — bộ chấm 1a gọi Claude API, tốn tiền thật). Ngày theo giờ VN, tuần ISO (`2026-W42`). `GET /api/usage?so_ngay=N` (1–92, mặc định 14), `den` = hôm nay giờ VN theo `dong_ho()`. ccusage chạy dưới tài khoản trạm → chỉ thấy Claude Code của **tài khoản trạm** (phiên tay của Đại ca trên B); log của khe nằm trong `CLAUDE_CONFIG_DIR` thuộc principal khe → ccusage theo khe để sau (S6) | Spec §12.2: Usage dùng cột token đã lưu riêng | **HỢP ĐỒNG MỚI** (JSON `/api/usage`) |
| G9 | Bảng điểm thợ (spec 4 §12 chưa duyệt; phần 4 chưa code) | Tính theo (khe, vai) từ bảng `phieu` + `lan_chay` của 3a-1: `so_phieu`, `so_xong`, `lan_chay_tb` = trung bình số `chay.bat_dau` (duy nhất theo `request_id`) trên phiếu **đã kết thúc**. `qua_lan_dau`, `bi_tra_ve` luôn `null` (cần `kiem.lai`, `qc.ket_qua`, `bead.vao_cot_3` của phần 4) — trang ghi "chờ phần 4" | Đúng lời dặn: chỉ phần tính được từ sự kiện 3a-1 | **lệch chữ spec** (thiếu 2 trong 3 chỉ số) |
| G10 | Hiển thị hạn mức "còn lại" | `phan_tram` của 3a-1 là phần **đã dùng** (luật ≥ 90% thì ngừng) → hiện "còn `100 − đã dùng`% (đã dùng …%) · reset … · đọc lúc …"; cửa sổ `chua_biet` hiện "chưa biết" (kèm "số đo cũ, đọc lúc …" nếu có), **không** 0%. Server tính `muc_han_muc ∈ {ngung, chi_p0_p1, chua_biet, ok}` bằng chính `cham_nguong_ngung`/`duoc_nhan` với ngưỡng trong `cau-hinh.yaml` | Spec 3 §8.1 "dashboard hiện số đo kèm đọc lúc, đánh dấu cửa sổ chưa biết"; nghĩa `utilization` thật chờ S1 | giả định (chờ S1) |
| G11 | Trạng thái hiển thị (§5.4 liệt kê 5; 3a-1 có 6) | Nhãn: `lam` "Đang làm", `can_nguoi` "Cần Đại ca", `ranh` "Rảnh", `tat` "Tắt", `mat_ket_noi` "Mất kết nối", `loi` "Lỗi lần chạy cuối"; cầu dao đang ngắt thì nhãn luôn là **"Cầu dao ngắt"** (dù trạng thái suy là gì) | Giữ nguyên định nghĩa duy nhất của 3a-1, chỉ đổi chữ | lệch chữ spec (thêm "Cần Đại ca", "Lỗi lần chạy cuối") |
| G12 | "Tên gợi nhớ, không hiện email" | `lam_sach(ten_goi_nho, 64)`; rỗng hoặc chứa `@` → hiện `khe_id` (3a-1 đã chặn `@` ở `/api/tho/dang-ky`, đây là lớp thứ hai cho dữ liệu cũ/ghi tay) | §5.4 | giả định |
| G13 | "Hệ cần xem" — cầu dao khe (§5.2) | Mỗi khe đang ngắt một mục `{loai: "he", du_an: "_tram", bead_id: null, tieu_de: "Khe <id>", chi_tiet: {su_kien: "khe.cau_dao_ngat", luc, khe_id, toi_luc, loi}}`; không nút "Thử lại"; link "Mở Đội ngũ AI để đóng cầu dao". `gom_phe_duyet` nhận thêm `them` để xếp chung theo độ gấp. Khoá `v-for` của trang Phê duyệt đổi thành `khoaMuc(m)` (gồm `su_kien`, `khe_id`) — sửa luôn trùng khoá có sẵn từ 2a khi một dự án có cả `quet.loi` và `nho.loi_*` | Spec §5.2 bảng "Hệ cần xem" | giả định |
| G14 | Telegram "cầu dao khe ngắt / khe hết hạn mức" (§6) | `khe.cau_dao_ngat` → tin loại `khe_het_han_muc` (khi `ly_do = het-han-muc`) hoặc `khe_cau_dao`, `du_an = "_tram"`, mã khe đặt ở trường `bead_id` của `Tin`; nội dung `[tram] khe hết hạn mức (B/claude-1) → <link>` — chỉ mã khe khớp `^[A-Za-z0-9-]{1,32}/[a-z0-9-]{1,32}$`. Chống ồn như cũ: 1 giờ cho cùng (loại, khe); **giờ yên lặng chặn** hai loại này (chỉ "trạm lỗi" luôn gửi) | §6 "từ phần 3: `khe.cau_dao_ngat`"; khe cạn hạn mức ban đêm không cần đánh thức Đại ca | **HỢP ĐỒNG MỚI** (loại tin) + giả định (giờ yên lặng) |
| G15 | Đội ngũ cập nhật không cần tải lại | SSE thêm sự kiện `doi_ngu_doi` (một lần mỗi nhịp) khi có sự kiện `khe.* \| chay.* \| giao.* \| bao.* \| tho.*`; `khe.cau_dao_ngat/dong` vào `LOAI_LAM_MOI` (→ `phe_duyet_doi`). Nhịp tim không là sự kiện (spec 3 §13 mục 3) → trang Đội ngũ tải lại mỗi 5 s để thấy "mất kết nối" | Spec §7 liệt kê `su_kien`, `cong_viec_doi`, `phe_duyet_doi` | **HỢP ĐỒNG MỚI** (tên sự kiện SSE) |
| G16 | `POST /api/khe/{id}/…` với `khe_id = "B/claude-1"` có `/` | Route `/api/khe/{may_id}/{ten}/tat\|bat\|cau-dao-dong` — URL thực vẫn là `/api/khe/B/claude-1/tat`; `khe_id` ghép lại phải khớp `^[A-Za-z0-9-]{1,32}/[a-z0-9-]{1,32}$` (dạng của 3a-1), sai → 422 | Starlette giải mã `%2F` trước khi khớp route | giả định |
| G17 | Bảo mật API ghi trước 3a (spec 2 §4 mục 2b) | Router 2b dùng đúng `yeu_cau_ghi` của 2a. Đường proxy xác thực thay header (điều kiện trước khi bật thợ thật) là việc 3a-2/S6 — router 2b đi theo vì dùng chung dependency, không có kiểm danh tính riêng | Không mở thêm đường ghi nào ngoài khuôn 2a | giả định |
| G18 | "Luật vai ↔ khe hiện ở đây" | Hiển thị `VAI_CUA_BUOC` (3a-1), `vai_uu_tien` trên từng thẻ, và 5 câu luật cố định (Q14, spec 3 §6.2/§8.2, #15, phần 4 chọn khe). Không có chỗ sửa luật (màn "Phân luồng" ngoài phạm vi — spec 2 §10) | Spec 4 §5.3 chưa duyệt — chỉ trích luật đã chốt | giả định |
| G19 | CSS của trang mới | `<style scoped>` trong `.vue` (Vite tách ra file `.css` lúc build — hợp CSP `style-src 'self'`), không sửa `kieu.css` | Tránh đụng chung file với 1b-3; giữ màu qua biến `--mat`, `--vien` của 2a | giả định |
| G20 | Tên khoá cấu hình `usage:` | Đọc bằng hàm riêng `nap_cau_hinh_usage()` (`tram/cau_hinh/usage.py`) trên cùng file `~/.tram/cau-hinh.yaml`; `nap_cau_hinh_tram` không đổi (bỏ qua khoá lạ như trước) | Giữ `tram/cau_hinh/tram.py` dưới 120 dòng, không đụng file 3a-1 vừa sửa | giả định |

## File Structure

```
tram/
  phieu/khe.py               # (sửa) bat_tat_khe(..., them=None); phien_ban_khe                    — Task 1
  phieu/cau_dao.py           # (sửa) dong_cau_dao(..., them=None)                                    — Task 1
  cau_hinh/usage.py          # CauHinhUsage, nap_cau_hinh_usage (khoá `usage:`)                      — Task 2
  usage/__init__.py          # (rỗng — Task 3, 4 cùng tạo)
  usage/su_kien.py           # DongUsage, moc_utc, doc_dong_usage, tong_hop                          — Task 3
  usage/ccusage.py           # KetQuaCcusage, doc_json_ccusage, DocCcusage (adapter — chờ chạy thật) — Task 4
  usage/bo_dem.py            # BoDemCcusage (ok 10 phút, lỗi 1 phút)                                  — Task 4
  suy/phe_duyet_khe.py       # muc_cau_dao — "Hệ cần xem" cầu dao khe                                  — Task 5
  suy/phe_duyet.py           # (sửa) gom_phe_duyet(..., them=())                                     — Task 5
  api/tuyen_doc.py           # (sửa) /api/phe-duyet thêm mục cầu dao                                 — Task 5
  api/luong.py               # (sửa) LOAI_LAM_MOI + doi_ngu_doi                                       — Task 5
  bao_tin/tin.py             # (sửa) loại tin khe_cau_dao, khe_het_han_muc; mã khe trong tin hệ       — Task 6
  bao_tin/nguon.py           # (sửa) khe.cau_dao_ngat → tin                                           — Task 6
  thao_tac/khe.py            # tat_khe_thao_tac, bat_khe_thao_tac, dong_cau_dao_thao_tac              — Task 8
  suy/bang_diem.py           # bang_diem(db)                                                          — Task 9
  suy/doi_ngu.py             # LUAT_VAI, muc_han_muc, the_khe, doi_ngu                                 — Task 9
  api/doi_ngu.py             # GET /api/doi-ngu; POST /api/khe/{may_id}/{ten}/tat|bat|cau-dao-dong    — Task 11
  api/usage.py               # GET /api/usage                                                         — Task 11
  api/app.py, api/phu_thuoc.py   # (sửa) thêm router; PhuThuocApi.usage, .doc_ccusage                 — Task 11
frontend/
  src/luat_doi_ngu.js        # nhãn trạng thái, mô tả cửa sổ, nút khe, định dạng, khoaMuc             — Task 7
  tests/doi_ngu.test.mjs     #                                                                        — Task 7
  src/thanh/HopKhe.vue, src/thanh/TheKhe.vue, src/trang/DoiNgu.vue                                   — Task 10
  src/kho.js, src/tuyen.js, src/KhungChinh.vue, src/trang/PheDuyet.vue, src/thanh/MucPheDuyet.vue   # (sửa) — Task 10
  src/thanh/BangUsage.vue, src/trang/Usage.vue                                                       — Task 12
  src/tuyen.js, src/KhungChinh.vue   # (sửa) route + menu Usage                                       — Task 12
tests/
  test_khe_2b.py (1) · test_cau_hinh_usage.py (2) · test_usage_su_kien.py (3) · test_ccusage.py (4)
  test_phe_duyet_khe.py (5) · test_bao_tin_khe.py (6) · test_thao_tac_khe.py (8) · test_suy_doi_ngu.py (9)
  test_api_doi_ngu.py (11)
```

## Hợp đồng JSON (lát 2b)

`GET /api/doi-ngu` (chỉ đọc, không cần danh tính):

```json
{"bat": true,
 "khe": [{"khe_id": "B/claude-1", "may": "B", "cli": "claude", "ten_goi_nho": "Claude tài khoản 1",
          "vai_uu_tien": ["coder"], "trang_thai": "lam",
          "phieu": {"giao_id": "g-20261013-0001", "bead_id": "hr-6xe1", "du_an": "hr-codex", "buoc": "code", "tieu_de": "…"},
          "han_muc": {"khe_id": "B/claude-1", "nguon": "stream",
                      "cua_so": [{"loai": "5h", "trang_thai": "biet", "phan_tram": 62.0, "reset_luc": "…Z", "doc_luc": "…Z", "het_hieu_luc": null},
                                 {"loai": "tuan", "trang_thai": "chua_biet", "phan_tram": null, "reset_luc": null, "doc_luc": null, "het_hieu_luc": null}]},
          "muc_han_muc": "chua_biet", "cau_dao": {"ngat": false, "ly_do": null, "toi_luc": null},
          "so_phien": 1, "nhip_cuoi": "2026-10-13T03:00:00Z", "phien_ban": "12:0"}],
 "luat_vai": {"vai_cua_buoc": {"code": "coder", "qc": "qc", "spec": "spec"}, "luat": ["…"]},
 "bang_diem": [{"khe_id": "B/claude-1", "vai": "coder", "so_phieu": 3, "so_xong": 1, "lan_chay_tb": 2.0,
                "qua_lan_dau": null, "bi_tra_ve": null}]}
```

Kho phiếu chưa bật: `{"bat": false, "khe": [], "luat_vai": null, "bang_diem": []}`.

`POST /api/khe/{may_id}/{ten}/tat|bat` thân `{ma_thao_tac, expected_version, vi_sao?}` (≤ 500 ký tự); `POST …/cau-dao-dong` thân `{ma_thao_tac, expected_version}`; trả `{"ket_qua": {"khe.tat": true}, "lap_lai": false}`. Lỗi: 403 (danh tính/CSRF), 404 (khe chưa đăng ký), 409 (phiên bản khác, cầu dao đang đóng, cùng mã khác nội dung), 422 (thân/mã khe sai), 501 (kho phiếu chưa bật).

`GET /api/usage?so_ngay=14`:

```json
{"tu": "2026-09-30", "den": "2026-10-13",
 "theo_ngay": [{"khoa": "2026-10-13", "token_vao": 2500, "token_ra": 500, "token_cache_doc": 0, "token_cache_ghi": 0,
                "so_lan": 2, "chi_phi_usd": 0.015, "thieu_gia": 0}],
 "theo_tuan": [{"khoa": "2026-W42", "…": "…"}], "theo_nguon": [{"khoa": "B/claude-1", "…": "…"}, {"khoa": "cham-cot", "…": "…"}],
 "theo_du_an": [{"khoa": "hr-codex", "…": "…"}], "co_bang_gia": true,
 "ccusage": {"trang_thai": "ok | chua_cau_hinh | loi", "loi": null, "phien_ban": "x.y.z",
             "theo_ngay": [{"ngay": "2026-10-12", "token_vao": 1200, "token_ra": 300, "token_cache_doc": 9000,
                            "token_cache_ghi": 50, "chi_phi_usd": 0.1235}]}}
```

SSE `/api/luong`: thêm `event: doi_ngu_doi` (`data: {}`).

## Chuẩn bị (người điều phối)

```bash
cd "/Users/dai-ca/Developer/Ben Station"
git status --short            # chỉ được có .beads/interactions.jsonl, .DS_Store — không đụng
uv run pytest -q              # kỳ vọng: N₀ passed (1015 nếu 1b-3 không thêm test)
(cd frontend && npm ci && npm run kiem && npm run build)   # npm ci: phụ thuộc đã khoá của 2a, không thêm gói; kỳ vọng M₀ (7) test
```

**Mỗi task một worktree**, tạo từ `main` **sau khi đã ghép mọi task của đợt trước**:

```bash
N=8   # số task
git worktree add .worktrees/2b-t$N -b 2b/t$N main
cd .worktrees/2b-t$N && uv sync && uv run pytest -q    # kỳ vọng: số "sau đợt trước" trong Sơ đồ đợt chạy
(cd frontend && npm ci)                                  # chỉ task có file trong frontend/ (7, 10, 12)
```

Cuối mỗi task: người thực thi commit trong worktree của mình; người điều phối kiểm (mọi dòng thêm có nguyên văn trong plan; số test đúng kỳ vọng) rồi `git merge --no-ff 2b/t$N` vào `main` (không push). Ghép xong cả đợt → `uv run pytest -q`, `npm run kiem`, `npm run build` trên `main` phải khớp số "sau đợt".

Mã: file **mới** cho nguyên văn đầy đủ; file **có sẵn** cho bản vá `git apply` (unified diff, chạy từ gốc worktree — sinh từ chính bản đã chạy thử). Bản vá không áp được → xem G2 (áp tay theo dòng neo nếu do 1b-3, ngược lại dừng và báo). File rỗng (`__init__.py`) tạo bằng `mkdir -p … && touch …`.

Dòng ghi công trong lệnh commit: thay `<model đang thực thi>` bằng đúng tên model của người thực thi task đó.

---

### Task 1: Đường ghi khe của 3a-1 mang `ma_thao_tac` + `phien_ban_khe`

**Độ khó:** `de` · **Đợt:** 1 · **Song song với:** Task 2–7 · **Phải xong (đã ghép vào `main`) trước khi bắt đầu:** — (chỉ cần `main` N₀)

**Files:**
- Modify: `tram/phieu/khe.py` (3a-1)
- Modify: `tram/phieu/cau_dao.py` (3a-1)
- Test: `tests/test_khe_2b.py` (mới)

**Interfaces:**
- Consumes: `su_kien_khe`, `LOAI_BAT_TAT`, `KheLa`, `dang_ky_khe`, `khe_dang_bat` (3a-1 Task 15); `ngat_cau_dao`; `kho_tam`, `LUC` (`tests/kho_phieu_gia.py`).
- Produces: `bat_tat_khe(kho, khe_id, *, bat, vi_sao, tac_nhan, luc, them: dict | None = None) -> None`; `dong_cau_dao(kho, khe_id, *, ly_do, luc, tac_nhan='tram/api', them: dict | None = None) -> None` — `them` gộp vào `du_lieu` nhưng KHÔNG đè khoá chính; `phien_ban_khe(kho, khe_id) -> str` dạng `"<id bật/tắt/đăng ký>:<id cầu dao>"` (G4).

- [ ] **Step 1: Viết test thất bại**

`tests/test_khe_2b.py` (mới):

```python
from datetime import timedelta

from kho_phieu_gia import LUC, kho_tam
from tram.phieu.cau_dao import dong_cau_dao, ngat_cau_dao
from tram.phieu.khe import bat_tat_khe, dang_ky_khe, khe_dang_bat, phien_ban_khe, su_kien_khe

K1 = {"ten": "claude-1", "cli": "claude", "ten_goi_nho": "Claude 1", "vai_uu_tien": ["coder"]}


def _kho(tmp_path):
    kho = kho_tam(tmp_path)
    with kho.giao_dich():
        dang_ky_khe(kho, "B", [K1], luc=LUC)
    return kho


def test_bat_tat_khe_mang_them_nhung_khong_de_khoa_chinh(tmp_path):
    kho = _kho(tmp_path)
    with kho.giao_dich():
        bat_tat_khe(kho, "B/claude-1", bat=False, vi_sao="để dành", tac_nhan="dai-ca/dashboard", luc=LUC,
                    them={"ma_thao_tac": "ma-tat-0001", "khe_id": "B/khac", "vi_sao": "đè"})
    _, loai, du_lieu, _ = su_kien_khe(kho, "B/claude-1", ("khe.tat",))
    assert loai == "khe.tat" and not khe_dang_bat(kho, "B/claude-1")
    assert du_lieu == {"khe_id": "B/claude-1", "vi_sao": "để dành", "ma_thao_tac": "ma-tat-0001"}
    with kho.giao_dich():                                         # CLI 3a vẫn gọi như cũ
        bat_tat_khe(kho, "B/claude-1", bat=True, vi_sao="", tac_nhan="dai-ca", luc=LUC)
    assert su_kien_khe(kho, "B/claude-1", ("khe.bat",))[2] == {"khe_id": "B/claude-1", "vi_sao": ""}


def test_dong_cau_dao_mang_them_va_phien_ban_khe_doi_theo_su_kien(tmp_path):
    kho = _kho(tmp_path)
    v0 = phien_ban_khe(kho, "B/claude-1")
    assert v0.endswith(":0") and phien_ban_khe(kho, "B/claude-9") == "0:0"
    with kho.giao_dich():
        ngat_cau_dao(kho, "B/claude-1", ly_do="het-han-muc", toi_luc=LUC + timedelta(hours=1), luc=LUC)
    v1 = phien_ban_khe(kho, "B/claude-1")
    with kho.giao_dich():
        dong_cau_dao(kho, "B/claude-1", ly_do="dai-ca", luc=LUC, tac_nhan="dai-ca/dashboard",
                     them={"ma_thao_tac": "ma-dao-0001"})
    x = su_kien_khe(kho, "B/claude-1", ("khe.cau_dao_dong",))
    assert x[2] == {"khe_id": "B/claude-1", "ly_do": "dai-ca", "toi_luc": None, "ma_thao_tac": "ma-dao-0001"}
    assert len({v0, v1, phien_ban_khe(kho, "B/claude-1")}) == 3
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_khe_2b.py -q`
Expected: FAIL — `1 error` (`ImportError: cannot import name 'phien_ban_khe' from 'tram.phieu.khe'`)

- [ ] **Step 3: Viết mã**

`tram/phieu/khe.py` (sửa — bản vá):

```diff
diff --git a/tram/phieu/khe.py b/tram/phieu/khe.py
index 8502f84..10a2192 100644
--- a/tram/phieu/khe.py
+++ b/tram/phieu/khe.py
@@ -52,14 +52,22 @@ def dang_ky_khe(kho: KhoPhieu, may_id: str, khe: list[dict], *, luc: datetime) -
     return ra
 
 
-def bat_tat_khe(kho: KhoPhieu, khe_id: str, *, bat: bool, vi_sao: str, tac_nhan: str, luc: datetime) -> None:
-    """Trong giao dịch. `tram tho bat-khe|tat-khe` ở 3a (chưa có dashboard 2b)."""
+def bat_tat_khe(kho: KhoPhieu, khe_id: str, *, bat: bool, vi_sao: str, tac_nhan: str, luc: datetime,
+                them: dict | None = None) -> None:
+    """Trong giao dịch. `tram tho bat-khe|tat-khe` (3a) và dashboard 2b — `them` = `{ma_thao_tac}` của dashboard."""
     if su_kien_khe(kho, khe_id, ("khe.dang_ky",)) is None:
         raise KheLa(f"Khe {khe_id} chưa đăng ký")
-    kho.ghi_su_kien(DU_AN_TRAM, "khe.bat" if bat else "khe.tat", {"khe_id": khe_id, "vi_sao": vi_sao},
+    kho.ghi_su_kien(DU_AN_TRAM, "khe.bat" if bat else "khe.tat", {**(them or {}), "khe_id": khe_id, "vi_sao": vi_sao},
                     luc=luc, tac_nhan=tac_nhan)
 
 
+def phien_ban_khe(kho: KhoPhieu, khe_id: str) -> str:
+    """`expected_version` của thao tác khe trên dashboard (spec 2 §12.3): id sự kiện bật/tắt và cầu dao mới nhất."""
+    a = su_kien_khe(kho, khe_id, LOAI_BAT_TAT)
+    b = su_kien_khe(kho, khe_id, ("khe.cau_dao_ngat", "khe.cau_dao_dong"))
+    return f"{a[0] if a else 0}:{b[0] if b else 0}"
+
+
 def dang_mat_ket_noi(kho: KhoPhieu, khe_id: str) -> bool:
     x = su_kien_khe(kho, khe_id, LOAI_KET_NOI)
     return x is not None and x[1] == "khe.mat_ket_noi"
```

`tram/phieu/cau_dao.py` (sửa — bản vá):

```diff
diff --git a/tram/phieu/cau_dao.py b/tram/phieu/cau_dao.py
index e02c613..121ac89 100644
--- a/tram/phieu/cau_dao.py
+++ b/tram/phieu/cau_dao.py
@@ -67,9 +67,11 @@ def xet_sau_chay(kho: KhoPhieu, khe_id: str, ket_thuc: str, *, reset_luc: str |
     return False
 
 
-def dong_cau_dao(kho: KhoPhieu, khe_id: str, *, ly_do: str, luc: datetime, tac_nhan: str = "tram/api") -> None:
-    kho.ghi_su_kien(DU_AN_TRAM, "khe.cau_dao_dong", {"khe_id": khe_id, "ly_do": ly_do, "toi_luc": None}, luc=luc,
-                    tac_nhan=tac_nhan)
+def dong_cau_dao(kho: KhoPhieu, khe_id: str, *, ly_do: str, luc: datetime, tac_nhan: str = "tram/api",
+                 them: dict | None = None) -> None:
+    """`them` = `{ma_thao_tac}` khi Đại ca đóng tay từ dashboard 2b (spec 3 §8.3)."""
+    kho.ghi_su_kien(DU_AN_TRAM, "khe.cau_dao_dong", {**(them or {}), "khe_id": khe_id, "ly_do": ly_do,
+                                                    "toi_luc": None}, luc=luc, tac_nhan=tac_nhan)
 
 
 def dong_cau_dao_het_gio(kho: KhoPhieu, bay_gio: datetime) -> list[str]:
```

Áp bản vá: lưu từng khối `diff` ra file rồi `git apply --check <file> && git apply <file>`.

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_khe_2b.py -q`
Expected: `2 passed`

Run: `uv run pytest -q`
Expected: `N₀ + 2 passed` (1017 — trên `main` đợt 0 + riêng task này); test 3a-1 (`test_khe_cau_dao.py`, `test_tho_lenh.py`, `test_bo_canh.py`) vẫn xanh vì tham số mới có mặc định.

- [ ] **Step 5: Commit**

```bash
git add tram/phieu/khe.py tram/phieu/cau_dao.py tests/test_khe_2b.py
git commit -m "feat(phieu): bat_tat_khe/dong_cau_dao nhận ma_thao_tac của dashboard, phien_ban_khe (spec 2 §12.3; plan 2b G3, G4)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 2: Khoá `usage:` trong `~/.tram/cau-hinh.yaml`

**Độ khó:** `de` · **Đợt:** 1 · **Song song với:** Task 1, 3–7 · **Phải xong trước:** —

**Files:**
- Create: `tram/cau_hinh/usage.py`
- Test: `tests/test_cau_hinh_usage.py` (mới)

**Interfaces:**
- Consumes: `tram_home()`; `nap_cau_hinh_tram` (chỉ trong test — chứng minh không bị ảnh hưởng).
- Produces: `CauHinhUsage(ccusage: Path | None, ccusage_phien_ban: str | None, gia: dict[str, dict[str, float]])` (frozen; `gia[mô hình] = {vao, ra, cache_doc, cache_ghi}`); `nap_cau_hinh_usage(duong_dan: Path | None = None) -> CauHinhUsage` — thiếu file/khoá → mặc định rỗng; sai → `ValueError`. `PHIEN_BAN_RE`, `LOAI_GIA`.

- [ ] **Step 1: Viết test thất bại**

`tests/test_cau_hinh_usage.py` (mới):

```python
from pathlib import Path

import pytest

from tram.cau_hinh.tram import nap_cau_hinh_tram
from tram.cau_hinh.usage import CauHinhUsage, nap_cau_hinh_usage

DU = """dai_ca_logins: [dai-ca@example.com]
usage:
  ccusage: /Users/tram/.tram/ccusage/node_modules/.bin/ccusage
  ccusage_phien_ban: "17.2.1"
  gia_usd_moi_trieu_token:
    claude-sonnet-5-5: {vao: 3, ra: 15, cache_doc: 0.3}
"""


def _ghi(tmp_path, noi_dung: str) -> Path:
    p = tmp_path / "cau-hinh.yaml"
    p.write_text(noi_dung, encoding="utf-8")
    return p


def test_mac_dinh_khi_thieu_file_hoac_thieu_khoa(tram_home_tam, tmp_path):
    assert nap_cau_hinh_usage() == CauHinhUsage()
    assert nap_cau_hinh_usage(_ghi(tmp_path, "ten_may_b: may-b\n")) == CauHinhUsage()


def test_doc_du_va_cau_hinh_tram_khong_bi_anh_huong(tmp_path):
    p = _ghi(tmp_path, DU)
    ch = nap_cau_hinh_usage(p)
    assert ch.ccusage == Path("/Users/tram/.tram/ccusage/node_modules/.bin/ccusage")
    assert ch.ccusage_phien_ban == "17.2.1"
    assert ch.gia == {"claude-sonnet-5-5": {"vao": 3.0, "ra": 15.0, "cache_doc": 0.3, "cache_ghi": 0.0}}
    assert nap_cau_hinh_tram(p).dai_ca_logins == ("dai-ca@example.com",)


@pytest.mark.parametrize("usage", [
    "[1]", "{la: 1}", "{ccusage: /x/ccusage}", "{ccusage_phien_ban: '1.2.3'}",
    "{ccusage: ccusage, ccusage_phien_ban: '1.2.3'}", "{ccusage: /a/../ccusage, ccusage_phien_ban: '1.2.3'}",
    "{ccusage: /x/ccusage, ccusage_phien_ban: latest}", "{ccusage: /x/ccusage, ccusage_phien_ban: 1.2}",
    "{gia_usd_moi_trieu_token: {m: {vao: 1}}}", "{gia_usd_moi_trieu_token: {m: {vao: 1, ra: -1}}}",
    "{gia_usd_moi_trieu_token: {m: {vao: 1, ra: true}}}", "{gia_usd_moi_trieu_token: {'m x': {vao: 1, ra: 1}}}",
])
def test_sai_bao_loi(tmp_path, usage):
    with pytest.raises(ValueError):
        nap_cau_hinh_usage(_ghi(tmp_path, f"usage: {usage}\n"))
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_cau_hinh_usage.py -q`
Expected: FAIL — `1 error` (`ModuleNotFoundError: No module named 'tram.cau_hinh.usage'`)

- [ ] **Step 3: Viết mã**

`tram/cau_hinh/usage.py` (mới):

```python
"""Khoá `usage:` trong `~/.tram/cau-hinh.yaml` cho màn Usage (spec 2 §5.4, §8; plan 2b G4, G5). Không chứa bí mật.

    usage:
      ccusage: /Users/<tài khoản trạm>/.tram/ccusage/node_modules/.bin/ccusage   # tuyệt đối — bản cài cố định
      ccusage_phien_ban: "x.y.z"                     # bắt buộc đi kèm; `--version` lệch thì KHÔNG chạy (Q15)
      gia_usd_moi_trieu_token:                       # tuỳ chọn; mô hình thiếu giá → chi phí "chưa có giá"
        claude-sonnet-5-5: {vao: 3, ra: 15, cache_doc: 0.3, cache_ghi: 3.75}

Thiếu cả khoá → Usage chỉ có số liệu từ sự kiện trạm, không chạy ccusage, không có chi phí."""
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from tram.duong_dan import tram_home

PHIEN_BAN_RE = re.compile(r"\d+\.\d+\.\d+")
MO_HINH_RE = re.compile(r"[A-Za-z0-9._:-]{1,100}")
LOAI_GIA = ("vao", "ra", "cache_doc", "cache_ghi")
KHOA = {"ccusage", "ccusage_phien_ban", "gia_usd_moi_trieu_token"}


@dataclass(frozen=True)
class CauHinhUsage:
    ccusage: Path | None = None
    ccusage_phien_ban: str | None = None
    gia: dict[str, dict[str, float]] = field(default_factory=dict)   # mô hình → {vao, ra, cache_doc, cache_ghi}


def _so(v) -> bool:
    return not isinstance(v, bool) and isinstance(v, (int, float)) and 0 <= v <= 1000


def _gia(raw) -> dict[str, dict[str, float]]:
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise ValueError("usage.gia_usd_moi_trieu_token phải là bảng mô hình → giá")
    ra = {}
    for mh, g in raw.items():
        if not (isinstance(mh, str) and MO_HINH_RE.fullmatch(mh) and isinstance(g, dict)
                and not set(g) - set(LOAI_GIA) and {"vao", "ra"} <= set(g) and all(_so(v) for v in g.values())):
            raise ValueError(f"usage.gia_usd_moi_trieu_token.{mh}: cần {{vao, ra[, cache_doc, cache_ghi]}} là số 0–1000")
        ra[mh] = {k: float(g.get(k, 0)) for k in LOAI_GIA}
    return ra


def nap_cau_hinh_usage(duong_dan: Path | None = None) -> CauHinhUsage:
    p = duong_dan or tram_home() / "cau-hinh.yaml"
    raw = (yaml.safe_load(p.read_text(encoding="utf-8")) or {}) if p.exists() else {}
    u = raw.get("usage") if isinstance(raw, dict) else None
    if u is None:
        return CauHinhUsage()
    if not isinstance(u, dict) or set(u) - KHOA:
        raise ValueError(f"usage phải là bảng với các khoá {sorted(KHOA)}")
    lenh, pb = u.get("ccusage"), u.get("ccusage_phien_ban")
    if (lenh is None) != (pb is None):
        raise ValueError("usage.ccusage và usage.ccusage_phien_ban phải đi cùng nhau")
    if lenh is not None:
        if not isinstance(lenh, str) or not Path(lenh).is_absolute() or ".." in Path(lenh).parts:
            raise ValueError("usage.ccusage phải là đường dẫn tuyệt đối tới bản cài cố định")
        if not isinstance(pb, str) or not PHIEN_BAN_RE.fullmatch(pb):
            raise ValueError("usage.ccusage_phien_ban phải là chuỗi 'x.y.z' (khoá chính xác — spec 2 §8)")
    return CauHinhUsage(Path(lenh) if lenh else None, pb, _gia(u.get("gia_usd_moi_trieu_token")))
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_cau_hinh_usage.py -q`
Expected: `14 passed`

Run: `uv run pytest -q`
Expected: `N₀ + 14 passed` (1029)

- [ ] **Step 5: Commit**

```bash
git add tram/cau_hinh/usage.py tests/test_cau_hinh_usage.py
git commit -m "feat(cau_hinh): khoá usage: — ccusage cài cố định + phiên bản khoá, bảng giá tuỳ chọn (spec 2 §8; plan 2b G6, G7)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 3: Usage từ sự kiện trạm — đọc và tổng hợp theo ngày / tuần / khe / dự án

**Độ khó:** `de` · **Đợt:** 1 · **Song song với:** Task 1, 2, 4–7 · **Phải xong trước:** —

**Files:**
- Create: `tram/usage/__init__.py` (rỗng — Task 4 cùng tạo, giống hệt)
- Create: `tram/usage/su_kien.py`
- Test: `tests/test_usage_su_kien.py` (mới)

**Interfaces:**
- Consumes: `GIO_VN` (`tram/cham_cot/ghi.py`), `doc_luc`; bảng `su_kien` (cột `luc, du_an, loai, du_lieu, token_vao, token_ra, mo_hinh`); test: `kho_tam` (3a-1) — `KhoPhieu.ghi_su_kien(..., luc=, token_vao=, token_ra=, mo_hinh=)` để đặt `luc` tuỳ ý.
- Produces: `DongUsage(ngay: date, nguon: str, du_an: str, mo_hinh: str | None, token_vao, token_ra, token_cache_doc, token_cache_ghi: int)`; `LOAI = ("chay.xong", "cham_cot.ket_qua")`; `NGUON_CHAM = "cham-cot"`; `moc_utc(ngay) -> str`; `doc_dong_usage(db: sqlite3.Connection, tu: date, den: date) -> list[DongUsage]`; `tong_hop(dong, gia) -> {"theo_ngay"|"theo_tuan"|"theo_nguon"|"theo_du_an": [{khoa, token_vao, token_ra, token_cache_doc, token_cache_ghi, so_lan, chi_phi_usd: float | None, thieu_gia}]}`.

- [ ] **Step 1: Viết test thất bại**

`tests/test_usage_su_kien.py` (mới):

```python
from datetime import date, datetime

from kho_phieu_gia import kho_tam
from tram.usage.su_kien import doc_dong_usage, moc_utc, tong_hop

GIA = {"claude-sonnet-5-5": {"vao": 3.0, "ra": 15.0, "cache_doc": 0.3, "cache_ghi": 3.75}}


def _kho(tmp_path):
    kho = kho_tam(tmp_path)
    with kho.giao_dich():
        for luc, du_an, loai, dl, cot in [
            ("2026-10-12T16:30:00Z", "hr-codex", "chay.xong", {"khe_id": "B/claude-1", "token_cache_doc": 1000,
                                                               "token_cache_ghi": 0}, (1000, 200, "claude-x")),
            ("2026-10-12T17:30:00Z", "hr-codex", "chay.xong", {"khe_id": "B/claude-2", "token_cache_doc": "rác"},
             (2000, 400, "claude-sonnet-5-5")),
            ("2026-10-12T18:00:00Z", "erp", "cham_cot.ket_qua", {"cot": "ai-lam"}, (500, 100, "claude-sonnet-5-5")),
            ("2026-10-12T19:00:00Z", "erp", "cham_cot.loi", {"loi": "x"}, (9, 9, None)),       # loại khác: bỏ
            ("2026-10-14T17:00:00Z", "erp", "cham_cot.ket_qua", {}, (7, 7, None)),             # ngoài khoảng
        ]:
            kho.ghi_su_kien(du_an, loai, dl, luc=datetime.fromisoformat(luc), bead_id="b", token_vao=cot[0], token_ra=cot[1],
                            mo_hinh=cot[2])
    return kho


def test_moc_ngay_theo_gio_viet_nam():
    assert moc_utc(date(2026, 10, 13)) == "2026-10-12T17:00:00Z"


def test_doc_dong_dung_khoang_va_ngay_vn(tmp_path):
    ds = doc_dong_usage(_kho(tmp_path).db, date(2026, 10, 12), date(2026, 10, 14))
    assert [(d.ngay.isoformat(), d.nguon, d.du_an) for d in ds] == [
        ("2026-10-12", "B/claude-1", "hr-codex"), ("2026-10-13", "B/claude-2", "hr-codex"),
        ("2026-10-13", "cham-cot", "erp")]
    assert (ds[0].token_cache_doc, ds[1].token_cache_doc, ds[2].token_cache_ghi) == (1000, 0, 0)


def test_tong_hop_theo_ngay_tuan_nguon_du_an_va_chi_phi(tmp_path):
    th = tong_hop(doc_dong_usage(_kho(tmp_path).db, date(2026, 10, 12), date(2026, 10, 13)), GIA)
    ngay = {x["khoa"]: x for x in th["theo_ngay"]}
    assert ngay["2026-10-12"]["chi_phi_usd"] is None and ngay["2026-10-12"]["thieu_gia"] == 1
    assert ngay["2026-10-13"]["token_vao"] == 2500 and ngay["2026-10-13"]["so_lan"] == 2
    assert ngay["2026-10-13"]["chi_phi_usd"] == round((2500 * 3 + 500 * 15) / 1e6, 4)
    assert [x["khoa"] for x in th["theo_tuan"]] == ["2026-W42"] and th["theo_tuan"][0]["thieu_gia"] == 1
    assert [x["khoa"] for x in th["theo_nguon"]] == ["B/claude-1", "B/claude-2", "cham-cot"]
    assert {x["khoa"]: x["token_ra"] for x in th["theo_du_an"]} == {"erp": 100, "hr-codex": 600}
    assert tong_hop([], GIA) == {"theo_ngay": [], "theo_tuan": [], "theo_nguon": [], "theo_du_an": []}
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_usage_su_kien.py -q`
Expected: FAIL — `1 error` (`ModuleNotFoundError: No module named 'tram.usage'`)

- [ ] **Step 3: Viết mã**

```bash
mkdir -p tram/usage && touch tram/usage/__init__.py    # rỗng; Task 4 cùng tạo — git ghép được
```

`tram/usage/su_kien.py` (mới):

```python
"""Usage từ sự kiện của trạm (spec 2 §5.4; §12.2: dùng cột `token_vao`, `token_ra`, `mo_hinh` đã lưu riêng).

Hai nguồn: `chay.xong` (mỗi lần chạy CLI của một khe — spec 3 §10; token cache nằm trong `du_lieu`) và
`cham_cot.ket_qua` (bộ chấm cột 1a gọi Claude API). Ngày/tuần tính theo giờ Việt Nam, tuần theo ISO."""
import json
import sqlite3
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone

from tram.cham_cot.ghi import GIO_VN
from tram.duong_dan import doc_luc

LOAI = ("chay.xong", "cham_cot.ket_qua")
NGUON_CHAM = "cham-cot"
TRUONG = ("token_vao", "token_ra", "token_cache_doc", "token_cache_ghi")


@dataclass(frozen=True)
class DongUsage:
    ngay: date
    nguon: str                 # khe_id ("B/claude-1") hoặc "cham-cot"
    du_an: str
    mo_hinh: str | None
    token_vao: int
    token_ra: int
    token_cache_doc: int
    token_cache_ghi: int


def moc_utc(ngay: date) -> str:
    """00:00 giờ Việt Nam của `ngay`, viết theo UTC `YYYY-MM-DDTHH:MM:SSZ` (so sánh chuỗi với cột `luc`)."""
    return datetime.combine(ngay, time(0), GIO_VN).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _so(x) -> int:
    return x if isinstance(x, int) and not isinstance(x, bool) and x > 0 else 0


def doc_dong_usage(db: sqlite3.Connection, tu: date, den: date) -> list[DongUsage]:
    """Sự kiện có `luc` trong [00:00 VN ngày `tu`, 00:00 VN ngày sau `den`)."""
    ra = []
    for luc, du_an, loai, dl, tv, tr, mh in db.execute(
            "SELECT luc, du_an, loai, du_lieu, token_vao, token_ra, mo_hinh FROM su_kien"
            " WHERE loai IN (?, ?) AND luc >= ? AND luc < ? ORDER BY id",
            (*LOAI, moc_utc(tu), moc_utc(den + timedelta(days=1)))):
        d = json.loads(dl)
        nguon = str(d.get("khe_id") or "?") if loai == "chay.xong" else NGUON_CHAM
        ra.append(DongUsage(doc_luc(luc).astimezone(GIO_VN).date(), nguon, du_an, mh, _so(tv), _so(tr),
                            _so(d.get("token_cache_doc")), _so(d.get("token_cache_ghi"))))
    return ra


def _chi_phi(d: DongUsage, gia: dict[str, dict[str, float]]) -> float | None:
    g = gia.get(d.mo_hinh or "")
    if g is None:
        return None
    return (d.token_vao * g["vao"] + d.token_ra * g["ra"] + d.token_cache_doc * g["cache_doc"]
            + d.token_cache_ghi * g["cache_ghi"]) / 1_000_000


def _cong(bang: dict, khoa: str, d: DongUsage, chi_phi: float | None) -> None:
    x = bang.setdefault(khoa, {**dict.fromkeys(TRUONG, 0), "so_lan": 0, "chi_phi_usd": 0.0, "thieu_gia": 0})
    for t in TRUONG:
        x[t] += getattr(d, t)
    x["so_lan"] += 1
    if chi_phi is None:
        x["thieu_gia"] += 1
    else:
        x["chi_phi_usd"] += chi_phi


def tong_hop(dong: list[DongUsage], gia: dict[str, dict[str, float]]) -> dict[str, list[dict]]:
    """`theo_ngay`, `theo_tuan`, `theo_nguon`, `theo_du_an`: mỗi dòng `{khoa, token_*, so_lan, chi_phi_usd,
    thieu_gia}`; `chi_phi_usd` = None khi không dòng nào có giá (spec 2 §5.4 — chi phí ước tính từ bảng giá)."""
    nhom: dict[str, dict] = {"theo_ngay": {}, "theo_tuan": {}, "theo_nguon": {}, "theo_du_an": {}}
    for d in dong:
        cp, (nam, tuan, _) = _chi_phi(d, gia), d.ngay.isocalendar()
        for ten, khoa in (("theo_ngay", d.ngay.isoformat()), ("theo_tuan", f"{nam}-W{tuan:02d}"),
                          ("theo_nguon", d.nguon), ("theo_du_an", d.du_an)):
            _cong(nhom[ten], khoa, d, cp)
    return {ten: [{"khoa": k, **v, "chi_phi_usd": None if v["thieu_gia"] == v["so_lan"] else round(v["chi_phi_usd"], 4)}
                  for k, v in sorted(bang.items())] for ten, bang in nhom.items()}
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_usage_su_kien.py -q`
Expected: `3 passed`

Run: `uv run pytest -q`
Expected: `N₀ + 3 passed` (1018)

- [ ] **Step 5: Commit**

```bash
git add tram/usage/__init__.py tram/usage/su_kien.py tests/test_usage_su_kien.py
git commit -m "feat(usage): token + chi phí theo ngày/tuần/khe/dự án từ chay.xong và cham_cot.ket_qua (spec 2 §5.4, §12.2; plan 2b G7, G8)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 4: Adapter `ccusage` (bản cài cố định, kiểm phiên bản) + bộ đệm — chờ chạy thật

**Độ khó:** `de` · **Đợt:** 1 · **Song song với:** Task 1–3, 5–7 · **Phải xong trước:** —

**Files:**
- Create: `tram/usage/__init__.py` (rỗng — giống hệt Task 3)
- Create: `tram/usage/ccusage.py`
- Create: `tram/usage/bo_dem.py`
- Test: `tests/test_ccusage.py` (mới)

**Interfaces:**
- Consumes: `lam_sach`.
- Produces: `KetQuaCcusage(trang_thai: "ok"|"chua_cau_hinh"|"loi", theo_ngay: tuple[dict, ...] = (), loi: str | None = None, phien_ban: str | None = None)` (frozen dataclass); `doc_json_ccusage(van_ban) -> list[{ngay, token_vao, token_ra, token_cache_doc, token_cache_ghi, chi_phi_usd}]` (dạng lạ → `ValueError`); `DocCcusage(lenh: Path, phien_ban: str, chay=subprocess.run, thoi_gian_cho=60.0)` + `.theo_ngay(tu: date, den: date) -> KetQuaCcusage` (không ném lỗi ra ngoài); `BoDemCcusage(doc, *, dong_ho=time.monotonic)` + `.lay(tu, den) -> KetQuaCcusage`.

**Chờ chạy thật (G6):** cờ lệnh và dạng JSON dưới đây là giả định chưa kiểm với ccusage thật; test chỉ dùng `chay` giả. Không đánh dấu sẵn sàng triển khai cho tới khi Đại ca cài ccusage và kiểm ở "Để sau".

- [ ] **Step 1: Viết test thất bại**

`tests/test_ccusage.py` (mới):

```python
"""ccusage KHÔNG được gọi thật — `chay` giả trả JSON mẫu (dạng giả định, chờ chạy thật — plan 2b G6)."""
import json
import subprocess
from datetime import date
from pathlib import Path

import pytest

from tram.usage.bo_dem import BoDemCcusage
from tram.usage.ccusage import DocCcusage, KetQuaCcusage, doc_json_ccusage

MAU = {"daily": [{"date": "2026-10-12", "inputTokens": 1200, "outputTokens": 300, "cacheCreationTokens": 50,
                  "cacheReadTokens": 9000, "totalTokens": 10550, "totalCost": 0.123456, "modelsUsed": ["x"]}],
       "totals": {"totalCost": 0.123456}}
TU, DEN = date(2026, 10, 12), date(2026, 10, 13)


def _chay(phien_ban="17.2.1", ma=0, ra=json.dumps(MAU), goi=None):
    def chay(argv, **kw):
        if goi is not None:
            goi.append((argv, kw))
        if argv[1] == "--version":
            return subprocess.CompletedProcess(argv, 0, f"{phien_ban}\n", "")
        return subprocess.CompletedProcess(argv, ma, ra, "lỗi\x1b[31m đỏ")
    return chay


def test_doc_json_chuan_hoa_va_tu_choi_dang_la():
    assert doc_json_ccusage(json.dumps(MAU)) == [{"ngay": "2026-10-12", "token_vao": 1200, "token_ra": 300,
                                                  "token_cache_doc": 9000, "token_cache_ghi": 50,
                                                  "chi_phi_usd": 0.1235}]
    assert doc_json_ccusage('{"daily": [{"date": "2026-10-12"}]}')[0]["token_vao"] == 0
    for sai in ("không phải json", "[]", '{"daily": {}}', '{"daily": [{"date": "12/10"}]}',
                '{"daily": [{"date": "2026-10-12", "inputTokens": -1}]}',
                '{"daily": [{"date": "2026-10-12", "totalCost": "1"}]}',
                '{"daily": [{"date": "2026-02-30"}]}',
                '{"daily": [{"date": "2026-10-12", "totalCost": NaN}]}',
                '{"daily": [{"date": "2026-10-12", "inputTokens": Infinity}]}'):
        with pytest.raises(ValueError):
            doc_json_ccusage(sai)


def test_chay_dung_lenh_co_dinh_moi_truong_toi_thieu(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "bi-mat")
    goi = []
    kq = DocCcusage(Path("/x/ccusage"), "17.2.1", chay=_chay(goi=goi)).theo_ngay(TU, DEN)
    assert kq.trang_thai == "ok" and kq.theo_ngay[0]["token_vao"] == 1200 and kq.phien_ban == "17.2.1"
    assert goi[1][0] == ["/x/ccusage", "daily", "--json", "--offline", "--since", "20261012", "--until", "20261013"]
    env = goi[1][1]["env"]
    assert set(env) == {"PATH", "HOME", "LANG", "TZ"} and "bi-mat" not in json.dumps(env)
    assert goi[1][1]["timeout"] == 60.0


@pytest.mark.parametrize("chay, chua", [
    (_chay(phien_ban="17.3.0"), "Phiên bản ccusage lệch (cần 17.2.1, thấy 17.3.0)"),
    (_chay(ma=2), "ccusage thoát mã 2"),
    (_chay(ra="{}"), "ccusage không đọc được (ValueError)"),
])
def test_loi_khong_nem_ra_ngoai(chay, chua):
    kq = DocCcusage(Path("/x/ccusage"), "17.2.1", chay=chay).theo_ngay(TU, DEN)
    assert kq.trang_thai == "loi" and kq.loi.startswith(chua) and "\x1b" not in kq.loi and kq.theo_ngay == ()


def test_khong_co_file_va_qua_gio():
    def het_gio(argv, **kw):
        raise subprocess.TimeoutExpired(argv, 60)
    assert DocCcusage(Path("/khong/co/ccusage"), "1.0.0").theo_ngay(TU, DEN).trang_thai == "loi"
    def lo_bi_mat(argv, **kw):
        if "--version" in argv:
            return subprocess.CompletedProcess(argv, 0, "1.0.0", "")
        return subprocess.CompletedProcess(argv, 2, "", "token=BI-MAT email@example.com")
    assert DocCcusage(Path("/x"), "1.0.0", chay=lo_bi_mat).theo_ngay(TU, DEN).loi == "ccusage thoát mã 2"
    def loi_bi_mat(argv, **kw):
        raise OSError("token=BI-MAT email@example.com")
    assert DocCcusage(Path("/x"), "1.0.0", chay=loi_bi_mat).theo_ngay(TU, DEN).loi == "ccusage không đọc được (OSError)"
    assert "TimeoutExpired" in DocCcusage(Path("/x"), "1.0.0", chay=het_gio).theo_ngay(TU, DEN).loi


def test_bo_dem_giu_ok_10_phut_loi_1_phut():
    dem, gio = [], [0.0]

    def doc(tu, den):
        dem.append((tu, den))
        return KetQuaCcusage("ok" if len(dem) != 3 else "loi", loi=None)
    bd = BoDemCcusage(doc, dong_ho=lambda: gio[0])
    bd.lay(TU, DEN)
    gio[0] = 599
    bd.lay(TU, DEN)
    assert len(dem) == 1
    bd.lay(TU, TU)                                   # khoảng khác: đọc riêng
    gio[0] = 600
    assert bd.lay(TU, DEN).trang_thai == "loi" and len(dem) == 3
    gio[0] = 659
    bd.lay(TU, DEN)
    gio[0] = 661
    bd.lay(TU, DEN)
    assert len(dem) == 4
    # Tiêm nguồn chậm: TTL tính từ hoàn tất, không từ lúc bắt đầu.
    def doc_cham(tu, den):
        gio[0] += 120
        return KetQuaCcusage("ok")
    cham = BoDemCcusage(doc_cham, dong_ho=lambda: gio[0])
    dau = cham.lay(TU, DEN)
    gio[0] += 599
    assert cham.lay(TU, DEN) is dau
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_ccusage.py -q`
Expected: FAIL — `1 error` (`ModuleNotFoundError: No module named 'tram.usage'`)

- [ ] **Step 3: Viết mã**

```bash
mkdir -p tram/usage && touch tram/usage/__init__.py    # rỗng; giống hệt Task 3
```

`tram/usage/ccusage.py` (mới):

```python
"""Bộ đọc `ccusage` (MIT — spec 2 §8, §11) cho màn Usage. CHỜ CHẠY THẬT: ccusage chưa cài trên máy B; cờ lệnh
và dạng JSON dưới đây chưa kiểm với phiên bản thật (plan 2b G6) — test chỉ dùng bản giả. Chỉ cho màn Usage,
KHÔNG dùng để chặn giao việc (spec 3 §8.1).

Chạy bản cài cố định `usage.ccusage` (không `npx`, không tự cập nhật — Q15); `--version` phải khớp
`usage.ccusage_phien_ban`, lệch thì không chạy. Lệnh: `<ccusage> daily --json --offline --since YYYYMMDD
--until YYYYMMDD` (`--offline`: bảng giá đóng gói sẵn, không gọi mạng). Môi trường tối thiểu: không khoá, không
token nào đi theo."""
import json
import math
import os
import re
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from tram.suy.lam_sach import lam_sach

PHIEN_BAN_RE = re.compile(r"\d+\.\d+\.\d+")
NGAY_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
TRUONG = {"inputTokens": "token_vao", "outputTokens": "token_ra", "cacheReadTokens": "token_cache_doc",
          "cacheCreationTokens": "token_cache_ghi", "totalCost": "chi_phi_usd"}


@dataclass(frozen=True)
class KetQuaCcusage:
    trang_thai: str                       # "ok" | "chua_cau_hinh" | "loi"
    theo_ngay: tuple[dict, ...] = ()      # {ngay, token_vao, token_ra, token_cache_doc, token_cache_ghi, chi_phi_usd}
    loi: str | None = None
    phien_ban: str | None = None


def doc_json_ccusage(van_ban: str) -> list[dict]:
    """`{"daily": [{"date": "YYYY-MM-DD", "inputTokens": n, …, "totalCost": x}]}` → dòng chuẩn hoá.
    Dạng lạ → ValueError (không đoán); trường thiếu = 0, trường lạ bỏ qua."""
    try:
        raw = json.loads(van_ban)
    except ValueError:
        raise ValueError("ccusage không trả JSON") from None
    ds = raw.get("daily") if isinstance(raw, dict) else None
    if not isinstance(ds, list):
        raise ValueError("JSON ccusage thiếu mảng 'daily'")
    ra = []
    for x in ds:
        if not isinstance(x, dict) or not isinstance(x.get("date"), str) or not NGAY_RE.fullmatch(x["date"]):
            raise ValueError("dòng 'daily' thiếu 'date' dạng YYYY-MM-DD")
        date.fromisoformat(x["date"])
        dong: dict = {"ngay": x["date"]}
        for khoa, ten in TRUONG.items():
            v = x.get(khoa, 0)
            if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or v < 0:
                raise ValueError(f"'{khoa}' không phải số ≥ 0")
            dong[ten] = round(float(v), 4) if ten == "chi_phi_usd" else int(v)
        ra.append(dong)
    return ra


@dataclass
class DocCcusage:
    lenh: Path
    phien_ban: str
    chay: Callable = subprocess.run
    thoi_gian_cho: float = 60.0

    def _goi(self, *doi_so: str) -> subprocess.CompletedProcess:
        env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(Path.home()), "LANG": "C.UTF-8",
               "TZ": "Asia/Ho_Chi_Minh"}
        return self.chay([str(self.lenh), *doi_so], capture_output=True, text=True, timeout=self.thoi_gian_cho,
                         env=env)

    def theo_ngay(self, tu: date, den: date) -> KetQuaCcusage:
        try:
            v = self._goi("--version")
            thay = PHIEN_BAN_RE.search(v.stdout or "")
            if v.returncode != 0 or thay is None or thay.group(0) != self.phien_ban:
                return KetQuaCcusage("loi", loi=f"Phiên bản ccusage lệch (cần {self.phien_ban}, thấy "
                                                f"{thay.group(0) if thay else '?'}) — không chạy")
            kq = self._goi("daily", "--json", "--offline", "--since", f"{tu:%Y%m%d}", "--until", f"{den:%Y%m%d}")
            if kq.returncode != 0:
                return KetQuaCcusage("loi", loi=f"ccusage thoát mã {kq.returncode}")
            return KetQuaCcusage("ok", tuple(doc_json_ccusage(kq.stdout)), phien_ban=self.phien_ban)
        except (OSError, subprocess.TimeoutExpired, ValueError) as e:
            return KetQuaCcusage("loi", loi=f"ccusage không đọc được ({type(e).__name__})")
```

`tram/usage/bo_dem.py` (mới):

```python
"""Bộ đệm kết quả ccusage theo khoảng ngày: `ok` giữ 10 phút, lỗi giữ 1 phút — ccusage quét toàn bộ log Claude
Code nên chậm; màn Usage tải lại không được chạy nó mỗi lần (plan 2b G6)."""
import threading
import time
from collections.abc import Callable
from datetime import date

from tram.usage.ccusage import KetQuaCcusage

GIAY_OK, GIAY_LOI, TOI_DA = 600, 60, 32


class BoDemCcusage:
    def __init__(self, doc: Callable[[date, date], KetQuaCcusage], *, dong_ho: Callable[[], float] = time.monotonic):
        self._doc, self._dong_ho = doc, dong_ho
        self._nho: dict[tuple[date, date], tuple[float, KetQuaCcusage]] = {}
        self._khoa = threading.Lock()

    def lay(self, tu: date, den: date) -> KetQuaCcusage:
        with self._khoa:
            bay_gio = self._dong_ho()
            cu = self._nho.get((tu, den))
            if cu is not None and bay_gio - cu[0] < (GIAY_OK if cu[1].trang_thai == "ok" else GIAY_LOI):
                return cu[1]
            # Một adapter ngoài tại một thời điểm; request đồng thời cùng khoảng dùng kết quả này.
            kq = self._doc(tu, den)
            if len(self._nho) >= TOI_DA:
                self._nho.clear()
            self._nho[(tu, den)] = (self._dong_ho(), kq)
            return kq
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_ccusage.py -q`
Expected: `7 passed`

Run: `uv run pytest -q`
Expected: `N₀ + 7 passed` (1022)

- [ ] **Step 5: Commit**

```bash
git add tram/usage/__init__.py tram/usage/ccusage.py tram/usage/bo_dem.py tests/test_ccusage.py
git commit -m "feat(usage): adapter ccusage — bản cài cố định, khoá phiên bản, --offline, môi trường tối thiểu, bộ đệm; chờ chạy thật (spec 2 §8; plan 2b G6)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 5: "Hệ cần xem" — cầu dao khe; SSE `doi_ngu_doi`

**Độ khó:** `de` · **Đợt:** 1 · **Song song với:** Task 1–4, 6, 7 · **Phải xong trước:** —

**Files:**
- Create: `tram/suy/phe_duyet_khe.py`
- Modify: `tram/suy/phe_duyet.py` (2a)
- Modify: `tram/api/tuyen_doc.py` (2a)
- Modify: `tram/api/luong.py` (2a)
- Test: `tests/test_phe_duyet_khe.py` (mới)

**Interfaces:**
- Consumes: `trang_thai_cau_dao`, `LOAI` (`tram/phieu/cau_dao.py`), `cac_khe`, `su_kien_khe`, `DU_AN_TRAM`, `KhoPhieu` (3a-1); `PhuThuocApi.mo_kho_phieu`, `.dong_ho` (3a-1 Task 23); `mot_nhip`, `TrangThaiLuong` (2a).
- Produces: `muc_cau_dao(kho: KhoPhieu, bay_gio) -> list[dict]` (mục `loai: "he"`, `du_an: "_tram"`, `bead_id: None`, `chi_tiet: {su_kien: "khe.cau_dao_ngat", luc, khe_id, toi_luc, loi}`); `gom_phe_duyet(cac_du_an, theo_du_an, kho, them: list[dict] = ())`; `luong.TIEN_TO_DOI_NGU`; SSE `event: doi_ngu_doi` (G15).

- [ ] **Step 1: Viết test thất bại**

`tests/test_phe_duyet_khe.py` (mới):

```python
from dataclasses import replace
from datetime import timedelta

from api_gia import tao_pt
from asgi_gia import goi
from bd_gia import BdGia
from bead_gia import bead
from kho_phieu_gia import LUC
from tram.api.app import tao_app
from tram.api.bo_dem import BoDemBeads
from tram.api.luong import TrangThaiLuong, mot_nhip
from tram.phieu.cau_dao import ngat_cau_dao
from tram.phieu.khe import dang_ky_khe
from tram.phieu.kho import KhoPhieu
from tram.suy.phe_duyet_khe import muc_cau_dao
from tram.su_kien.kho import KhoSuKien

KHE = [{"ten": t, "cli": "claude", "ten_goi_nho": t, "vai_uu_tien": ["coder"]} for t in ("claude-1", "claude-2")]


def _kho(tmp_path) -> KhoPhieu:
    kho = KhoPhieu(tmp_path / "sk.db")
    with kho.giao_dich():
        dang_ky_khe(kho, "B", KHE, luc=LUC)
        ngat_cau_dao(kho, "B/claude-2", ly_do="het-han-muc", toi_luc=LUC + timedelta(hours=1), luc=LUC)
    return kho


def test_muc_cau_dao_chi_khe_dang_ngat_va_het_khi_toi_gio(tmp_path):
    kho = _kho(tmp_path)
    ds = muc_cau_dao(kho, LUC)
    assert len(ds) == 1 and ds[0]["loai"] == "he" and ds[0]["du_an"] == "_tram" and ds[0]["bead_id"] is None
    assert ds[0]["chi_tiet"] == {"su_kien": "khe.cau_dao_ngat", "luc": "2026-10-13T03:00:00Z", "khe_id": "B/claude-2",
                                 "toi_luc": "2026-10-13T04:00:00Z",
                                 "loi": "Cầu dao khe B/claude-2 ngắt tới 2026-10-13T04:00:00Z — hết hạn mức"}
    assert muc_cau_dao(kho, LUC + timedelta(hours=1)) == []


def test_api_phe_duyet_co_muc_cau_dao_khi_bat_kho_phieu(tmp_path):
    _kho(tmp_path).close()
    bds = {"hr": BdGia([bead("hr-1", labels=["cot:cho-review"])])}
    pt = replace(tao_pt(tmp_path, bds), mo_kho_phieu=lambda: KhoPhieu(tmp_path / "sk.db"), dong_ho=lambda: LUC)
    r = goi(tao_app(pt), "GET", "/api/phe-duyet").json()
    assert r["so"] == 2 and [m["loai"] for m in r["muc"]] == ["he", "cho-review"]
    assert goi(tao_app(tao_pt(tmp_path, bds)), "GET", "/api/phe-duyet").json()["so"] == 1   # kho phiếu tắt


def test_luong_bao_doi_ngu_va_phe_duyet_khi_cau_dao(tmp_path):
    k, bo = KhoSuKien(tmp_path / "sk.db"), BoDemBeads(lambda ten: BdGia([]))
    tt = TrangThaiLuong(moc=0)
    k.ghi("hr", "chay.xong", {"khe_id": "B/claude-1"}, bead_id="hr-1")
    ra = mot_nhip(k, bo, [], tt)
    assert [x.split("\n")[0] for x in ra] == ["event: su_kien", "event: doi_ngu_doi"]
    k.ghi("_tram", "khe.cau_dao_ngat", {"khe_id": "B/claude-1"})
    ra = mot_nhip(k, bo, [], tt)
    assert [x.split("\n")[0] for x in ra] == ["event: su_kien", "event: phe_duyet_doi", "event: doi_ngu_doi"]
    k.ghi("hr", "quet.xong", {})
    assert "event: doi_ngu_doi" not in "".join(mot_nhip(k, bo, [], tt))
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_phe_duyet_khe.py -q`
Expected: FAIL — `1 error` (`ModuleNotFoundError: No module named 'tram.suy.phe_duyet_khe'`)

- [ ] **Step 3: Viết mã**

`tram/suy/phe_duyet_khe.py` (mới):

```python
"""Mục "Hệ cần xem" cho cầu dao khe đang ngắt (spec 2 §5.2 — nguồn "cầu dao khe (phần 3)"; spec 3 §8.3).
Không có nút "thử lại": Đại ca đóng cầu dao ở trang Đội ngũ AI hoặc chờ cầu dao tự đóng khi tới giờ."""
from datetime import datetime

from tram.phieu.cau_dao import LOAI, trang_thai_cau_dao
from tram.phieu.khe import cac_khe, su_kien_khe
from tram.phieu.kho import DU_AN_TRAM, KhoPhieu
from tram.suy.lam_sach import lam_sach

LY_DO = {"het-han-muc": "hết hạn mức", "loi-lien-tiep": "lỗi không do agent liên tiếp"}


def muc_cau_dao(kho: KhoPhieu, bay_gio: datetime) -> list[dict]:
    ra = []
    for khe_id in sorted(cac_khe(kho)):
        cd = trang_thai_cau_dao(kho, khe_id, bay_gio)
        if not cd.ngat:
            continue
        luc = su_kien_khe(kho, khe_id, LOAI)[3]
        loi = f"Cầu dao khe {khe_id} ngắt tới {cd.toi_luc} — {LY_DO.get(cd.ly_do, cd.ly_do)}"
        ra.append({"loai": "he", "du_an": DU_AN_TRAM, "bead_id": None, "tieu_de": f"Khe {khe_id}", "uu_tien": None,
                   "updated_at": None, "chi_tiet": {"su_kien": "khe.cau_dao_ngat", "luc": luc, "khe_id": khe_id,
                                                    "toi_luc": cd.toi_luc, "loi": lam_sach(loi, 300)}})
    return ra
```

`tram/suy/phe_duyet.py` (sửa — bản vá):

```diff
diff --git a/tram/suy/phe_duyet.py b/tram/suy/phe_duyet.py
index 874a7ef..430ac48 100644
--- a/tram/suy/phe_duyet.py
+++ b/tram/suy/phe_duyet.py
@@ -79,8 +79,9 @@ def muc_nho(du_an: str, kho) -> list[dict]:
     return ra
 
 
-def gom_phe_duyet(cac_du_an: list[str], theo_du_an: dict[str, list[Bead]], kho) -> list[dict]:
-    ra = []
+def gom_phe_duyet(cac_du_an: list[str], theo_du_an: dict[str, list[Bead]], kho, them: list[dict] = ()) -> list[dict]:
+    """`them`: mục không gắn dự án (2b: cầu dao khe — `tram/suy/phe_duyet_khe.py`), xếp chung theo độ gấp."""
+    ra = list(them)
     for du_an in cac_du_an:
         beads = theo_du_an.get(du_an, [])
         ra += muc_tu_beads(du_an, beads) + muc_he(du_an, kho, {b.id: b for b in beads})
```

`tram/api/tuyen_doc.py` (sửa — bản vá):

```diff
diff --git a/tram/api/tuyen_doc.py b/tram/api/tuyen_doc.py
index 838891a..96babe4 100644
--- a/tram/api/tuyen_doc.py
+++ b/tram/api/tuyen_doc.py
@@ -12,6 +12,7 @@ from tram.suy.chi_tiet import chi_tiet_bead
 from tram.suy.cot import HANG, hien_tren_bang, the_bead
 from tram.suy.lam_sach import lam_sach
 from tram.suy.phe_duyet import gom_phe_duyet
+from tram.suy.phe_duyet_khe import muc_cau_dao
 from tram.suy.trang_thai import trang_thai_du_an, trang_thai_tram
 from tram.thao_tac.loi import KhongThay
 
@@ -74,8 +75,12 @@ def phe_duyet(request: Request) -> dict:
     pt = request.app.state.pt
     ten = pt.cac_du_an()
     beads, loi = _doc_beads(pt, ten)
+    them = []
+    if pt.mo_kho_phieu is not None:                       # 2b: cầu dao khe đang ngắt (spec 2 §5.2)
+        with closing(pt.mo_kho_phieu()) as kp:
+            them = muc_cau_dao(kp, pt.dong_ho())
     with closing(pt.mo_kho()) as kho:
-        muc = gom_phe_duyet(ten, beads, kho)
+        muc = gom_phe_duyet(ten, beads, kho, them)
     return {"muc": muc, "so": len(muc), "loi": loi}
 
 
```

`tram/api/luong.py` (sửa — bản vá):

```diff
diff --git a/tram/api/luong.py b/tram/api/luong.py
index 65c748a..ff69a70 100644
--- a/tram/api/luong.py
+++ b/tram/api/luong.py
@@ -1,4 +1,4 @@
-"""GET /api/luong (SSE, spec 2 §7): đẩy sự kiện mới theo sau_id, báo bảng / Phê duyệt đổi (D2 ≤ 10 s)."""
+"""GET /api/luong (SSE, spec 2 §7): đẩy sự kiện mới theo sau_id, báo bảng / Phê duyệt / Đội ngũ AI đổi (D2 ≤ 10 s)."""
 import asyncio
 import json
 from contextlib import closing
@@ -13,7 +13,9 @@ router = APIRouter()
 NHIP_GIAY = 2
 NHIP_GIU_KET_NOI = 8          # mỗi 8 nhịp (~16 s) một dòng chú thích giữ kết nối
 LOAI_LAM_MOI = {"quet.xong", "quet.loi", "cot.dai_ca_sua", "cot.da_chot", "cot.tra_ve", "escalation.tra_loi",
-                "cham_cot.thu_lai", "cham_cot.bo_qua", "estop.bat", "estop.tat"}
+                "cham_cot.thu_lai", "cham_cot.bo_qua", "estop.bat", "estop.tat",
+                "khe.cau_dao_ngat", "khe.cau_dao_dong"}                    # 2b: "Hệ cần xem" cầu dao khe
+TIEN_TO_DOI_NGU = ("khe.", "chay.", "giao.", "bao.", "tho.")          # 2b: sự kiện phần 3 → trang Đội ngũ AI tải lại
 
 
 def khung(su_kien: str, du_lieu: dict, id: int | None = None) -> str:
@@ -29,11 +31,12 @@ class TrangThaiLuong:
 
 
 def mot_nhip(kho, bo_dem, cac_du_an: list[str], tt: TrangThaiLuong) -> list[str]:
-    ra, can_bao = [], False
+    ra, can_bao, doi_ngu = [], False, False
     for sk in kho.sau_id(tt.moc, 200):
         ra.append(khung("su_kien", {"id": sk.id, "luc": sk.luc, "du_an": sk.du_an, "bead_id": sk.bead_id,
                                     "loai": sk.loai}, sk.id))
         tt.moc = sk.id
+        doi_ngu = doi_ngu or sk.loai.startswith(TIEN_TO_DOI_NGU)
         if sk.loai in LOAI_LAM_MOI:
             can_bao = True
             if not sk.du_an.startswith("_"):
@@ -50,6 +53,8 @@ def mot_nhip(kho, bo_dem, cac_du_an: list[str], tt: TrangThaiLuong) -> list[str]
         tt.phien_ban[du_an] = pb
     if can_bao:
         ra.append(khung("phe_duyet_doi", {}))
+    if doi_ngu:
+        ra.append(khung("doi_ngu_doi", {}))
     return ra
 
 
```

Áp bản vá: lưu từng khối `diff` ra file rồi `git apply --check <file> && git apply <file>` (G2 nếu 1b-3 đã sửa cùng chỗ).

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_phe_duyet_khe.py tests/test_luong.py tests/test_suy_phe_duyet.py tests/test_api_doc.py -q`
Expected: tất cả pass (`test_phe_duyet_khe.py`: `3 passed`)

Run: `uv run pytest -q`
Expected: `N₀ + 3 passed` (1018)

- [ ] **Step 5: Commit**

```bash
git add tram/suy/phe_duyet_khe.py tram/suy/phe_duyet.py tram/api/tuyen_doc.py tram/api/luong.py tests/test_phe_duyet_khe.py
git commit -m "feat(phe-duyet): Hệ cần xem có cầu dao khe đang ngắt; SSE doi_ngu_doi khi có sự kiện phần 3 (spec 2 §5.2, §7; plan 2b G13, G15)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 6: Telegram — cầu dao khe ngắt / khe hết hạn mức

**Độ khó:** `de` · **Đợt:** 1 · **Song song với:** Task 1–5, 7 · **Phải xong trước:** —

**Files:**
- Modify: `tram/bao_tin/tin.py` (2a)
- Modify: `tram/bao_tin/nguon.py` (2a)
- Test: `tests/test_bao_tin_khe.py` (mới)

**Interfaces:**
- Consumes: `Tin`, `soan_tin`, `tin_tu_su_kien`, `BoChongOn` (2a); sự kiện `khe.cau_dao_ngat {khe_id, ly_do, toi_luc}` (3a-1).
- Produces: `LOAI_TIN` thêm `"khe_cau_dao"`, `"khe_het_han_muc"`; `KHE_AN_TOAN` (regex mã khe); `tin_tu_su_kien` trả `Tin("khe_het_han_muc" | "khe_cau_dao", "_tram", <khe_id>)`; tin hệ (`du_an` bắt đầu `_`) in kèm mã khe hợp lệ (G14).

- [ ] **Step 1: Viết test thất bại**

`tests/test_bao_tin_khe.py` (mới):

```python
from datetime import datetime, timezone

from tram.bao_tin.chong_on import BoChongOn
from tram.bao_tin.nguon import tin_tu_su_kien
from tram.bao_tin.tin import Tin, soan_tin
from tram.su_kien.kho import KhoSuKien


def test_cau_dao_ngat_thanh_tin_theo_ly_do(tmp_path):
    k = KhoSuKien(tmp_path / "sk.db")
    k.ghi("_tram", "khe.cau_dao_ngat", {"khe_id": "B/claude-1", "ly_do": "het-han-muc", "toi_luc": "x"})
    k.ghi("_tram", "khe.cau_dao_ngat", {"khe_id": "B/claude-2", "ly_do": "loi-lien-tiep", "toi_luc": "x"})
    k.ghi("_tram", "khe.cau_dao_dong", {"khe_id": "B/claude-2", "ly_do": "het-gio", "toi_luc": None})
    k.ghi("_tram", "khe.tat", {"khe_id": "B/claude-1", "vi_sao": ""})
    assert [t for s in k.sau_id(0, 10) for t in tin_tu_su_kien(s, k)] == [
        Tin("khe_het_han_muc", "_tram", "B/claude-1"), Tin("khe_cau_dao", "_tram", "B/claude-2")]


def test_soan_tin_khe_chi_ma_khe_va_link():
    tins = (Tin("khe_het_han_muc", "_tram", "B/claude-1"), Tin("khe_het_han_muc", "_tram", "B/claude-2"))
    assert soan_tin("khe_het_han_muc", tins, "https://b.ts.net") == \
        "[tram] khe hết hạn mức (B/claude-1, B/claude-2) → https://b.ts.net"
    assert soan_tin("khe_cau_dao", (Tin("khe_cau_dao", "_tram", "B/x y;z"),), None) == "[tram] cầu dao khe ngắt"
    assert soan_tin("estop_bat", (Tin("estop_bat", "_tram"),), None) == "[tram] estop BẬT"


def test_chong_on_khong_lap_cung_khe_trong_mot_gio():
    bo, luc = BoChongOn(), datetime(2026, 10, 13, 3, 0, tzinfo=timezone.utc)
    t = Tin("khe_cau_dao", "_tram", "B/claude-1")
    assert len(bo.nhan([t], luc)) == 1 and bo.nhan([t], luc.replace(minute=30)) == []
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_bao_tin_khe.py -q`
Expected: FAIL — `2 failed, 1 passed` (`AssertionError: assert [] == [Tin(loai='kh...'B/claude-2')]`)

- [ ] **Step 3: Viết mã**

`tram/bao_tin/tin.py` (sửa — bản vá):

```diff
diff --git a/tram/bao_tin/tin.py b/tram/bao_tin/tin.py
index cdee3b5..8ea864f 100644
--- a/tram/bao_tin/tin.py
+++ b/tram/bao_tin/tin.py
@@ -3,10 +3,13 @@ import re
 from collections.abc import Sequence
 from dataclasses import dataclass
 
-LOAI_TIN = ("cho_review", "spec_cho_duyet", "escalation", "co_do", "tram_loi", "estop_bat", "estop_tat")
+LOAI_TIN = ("cho_review", "spec_cho_duyet", "escalation", "co_do", "tram_loi", "estop_bat", "estop_tat",
+            "khe_cau_dao", "khe_het_han_muc")
 NHAN_LOAI = {"cho_review": "việc chờ review", "spec_cho_duyet": "spec chờ duyệt", "escalation": "escalation bí",
-             "co_do": "cờ đỏ", "tram_loi": "trạm lỗi", "estop_bat": "estop BẬT", "estop_tat": "estop tắt"}
+             "co_do": "cờ đỏ", "tram_loi": "trạm lỗi", "estop_bat": "estop BẬT", "estop_tat": "estop tắt",
+             "khe_cau_dao": "cầu dao khe ngắt", "khe_het_han_muc": "khe hết hạn mức"}
 ID_AN_TOAN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}")
+KHE_AN_TOAN = re.compile(r"[A-Za-z0-9-]{1,32}/[a-z0-9-]{1,32}")      # khe_id (spec 3 §4) — tin hệ của lát 2b
 
 
 @dataclass(frozen=True)
@@ -19,13 +22,14 @@ class Tin:
 def soan_tin(loai: str, tins: Sequence[Tin], dashboard_url: str | None) -> str:
     theo: dict[str, list[str]] = {}
     for t in tins:
-        theo.setdefault(t.du_an, []).append(t.bead_id if t.bead_id and ID_AN_TOAN.fullmatch(t.bead_id) else "")
+        ok = t.bead_id and (ID_AN_TOAN.fullmatch(t.bead_id) or KHE_AN_TOAN.fullmatch(t.bead_id))
+        theo.setdefault(t.du_an, []).append(t.bead_id if ok else "")
     phan = []
     for du_an in sorted(theo):
-        if du_an.startswith("_"):
-            phan.append(NHAN_LOAI[loai])
-            continue
         ma = [i for i in theo[du_an] if i]
+        if du_an.startswith("_"):                      # tin hệ: chỉ nhãn loại (+ mã khe nếu có)
+            phan.append(NHAN_LOAI[loai] + (f" ({', '.join(ma[:5])})" if ma else ""))
+            continue
         s = f"{du_an} · {len(theo[du_an])} {NHAN_LOAI[loai]}"
         if ma:
             s += f" ({', '.join(ma[:5])}{', …' if len(ma) > 5 else ''})"
```

`tram/bao_tin/nguon.py` (sửa — bản vá):

```diff
diff --git a/tram/bao_tin/nguon.py b/tram/bao_tin/nguon.py
index 9ba7423..b6e94e9 100644
--- a/tram/bao_tin/nguon.py
+++ b/tram/bao_tin/nguon.py
@@ -1,4 +1,5 @@
-"""Nguồn tin lát 2a (spec 2 §6): so ảnh beads trước/sau `quet.xong`; trạm lỗi và estop từ sự kiện."""
+"""Nguồn tin lát 2a (spec 2 §6): so ảnh beads trước/sau `quet.xong`; trạm lỗi và estop từ sự kiện.
+Lát 2b: `khe.cau_dao_ngat` (spec 3 §8.3) → "khe hết hạn mức" (ly_do `het-han-muc`) hoặc "cầu dao khe ngắt"."""
 from tram.bao_tin.tin import Tin
 from tram.beads.mo_hinh import Bead
 
@@ -36,6 +37,9 @@ def tin_tu_su_kien(sk, kho) -> list[Tin]:
         return [Tin("estop_tat", sk.du_an)]
     if sk.loai in ("cham_cot.bo_qua", "nho.loi_llm", "nho.loi_embedder"):   # nho.*: memory 1b nạp đứng
         return [Tin("tram_loi", sk.du_an, sk.bead_id)]
+    if sk.loai == "khe.cau_dao_ngat":
+        het = sk.du_lieu.get("ly_do") == "het-han-muc"
+        return [Tin("khe_het_han_muc" if het else "khe_cau_dao", sk.du_an, sk.du_lieu.get("khe_id"))]
     if sk.loai == "quet.loi" and so_quet_loi_lien_tiep(kho, sk.du_an) >= NGUONG_QUET_LOI:
         return [Tin("tram_loi", sk.du_an)]
     return []
```

Áp bản vá: `git apply --check <file> && git apply <file>`.

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_bao_tin_khe.py tests/test_chong_on.py tests/test_nguon_tin.py tests/test_bao_tin.py -q`
Expected: tất cả pass (`test_bao_tin_khe.py`: `3 passed`; tin estop/trạm lỗi của 2a không đổi chữ)

Run: `uv run pytest -q`
Expected: `N₀ + 3 passed` (1018)

- [ ] **Step 5: Commit**

```bash
git add tram/bao_tin/tin.py tram/bao_tin/nguon.py tests/test_bao_tin_khe.py
git commit -m "feat(bao-tin): tin cầu dao khe ngắt / khe hết hạn mức — chỉ mã khe (spec 2 §6; plan 2b G14)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 7: Frontend — luật hiển thị Đội ngũ AI + Usage (`luat_doi_ngu.js`)

**Độ khó:** `de` · **Đợt:** 1 · **Song song với:** Task 1–6 (chỉ đụng `frontend/`; làm theo "Hợp đồng JSON", không chờ backend) · **Phải xong trước:** —

**Files:**
- Create: `frontend/src/luat_doi_ngu.js`
- Test: `frontend/tests/doi_ngu.test.mjs` (mới — `npm run kiem` tự chạy mọi `tests/*.test.mjs`)

**Interfaces:**
- Consumes: `gioVN` (`src/luat.js`).
- Produces (Task 10, 12 dùng): `TEN_TRANG_THAI_KHE`, `CANH_BAO_HAN_MUC` (`muc_han_muc → [lớp CSS, câu]`), `nhanTrangThai(khe) -> string` (cầu dao ngắt thắng — G11), `moTaCuaSo(cs) -> string` (G10), `lyDoCauDao(lyDo) -> string`, `nutKhe(khe) -> {tat, bat, dongCauDao}`, `dinhDangSo(n)`, `dinhDangUsd(x)` (`null` → "chưa có giá"), `tenNguon(khoa)`, `tiLe(x)` (`null` → "chờ phần 4"), `khoaMuc(m)` (khoá `v-for` mục Phê duyệt — G13).

- [ ] **Step 1: Viết test thất bại**

`frontend/tests/doi_ngu.test.mjs` (mới):

```js
import assert from 'node:assert/strict'
import { test } from 'node:test'
import { CANH_BAO_HAN_MUC, dinhDangSo, dinhDangUsd, khoaMuc, lyDoCauDao, moTaCuaSo, nhanTrangThai, nutKhe, tenNguon, tiLe }
  from '../src/luat_doi_ngu.js'

test('nhãn trạng thái: cầu dao ngắt thắng trạng thái suy', () => {
  assert.equal(nhanTrangThai({ trang_thai: 'lam', cau_dao: { ngat: false } }), 'Đang làm')
  assert.equal(nhanTrangThai({ trang_thai: 'loi', cau_dao: { ngat: true } }), 'Cầu dao ngắt')
  assert.equal(nhanTrangThai({ trang_thai: 'mat_ket_noi', cau_dao: { ngat: false } }), 'Mất kết nối')
  assert.equal(nhanTrangThai({ trang_thai: 'la', cau_dao: {} }), 'la')
})

test('mô tả cửa sổ hạn mức: còn lại, reset, chưa biết không phải 0%', () => {
  const s = moTaCuaSo({ loai: '5h', trang_thai: 'biet', phan_tram: 62, reset_luc: '2026-10-13T05:00:00Z',
    doc_luc: '2026-10-13T02:41:10Z' })
  assert.match(s, /^Cửa sổ 5 giờ: còn 38% \(đã dùng 62%\) · reset .*12:00.* · đọc lúc .*09:41/)
  assert.equal(moTaCuaSo({ loai: 'tuan', trang_thai: 'chua_biet', doc_luc: null }), 'Cửa sổ tuần: chưa biết')
  assert.match(moTaCuaSo({ loai: 'x:60m', trang_thai: 'chua_biet', doc_luc: '2026-10-13T01:00:00Z' }),
    /^x:60m: chưa biết \(số đo cũ, đọc lúc .*08:00/)
})

test('lý do cầu dao và cảnh báo hạn mức', () => {
  assert.equal(lyDoCauDao('het-han-muc'), 'hết hạn mức')
  assert.equal(lyDoCauDao('dai-ca'), 'dai-ca')
  assert.equal(lyDoCauDao(null), '')
  assert.equal(CANH_BAO_HAN_MUC.ngung[0], 'loi')
  assert.equal(CANH_BAO_HAN_MUC.ok, undefined)
})

test('nút khe theo trạng thái', () => {
  assert.deepEqual(nutKhe({ trang_thai: 'ranh', cau_dao: { ngat: false } }), { tat: true, bat: false, dongCauDao: false })
  assert.deepEqual(nutKhe({ trang_thai: 'tat', cau_dao: { ngat: true } }), { tat: false, bat: true, dongCauDao: true })
})

test('định dạng số, USD, nguồn, tỉ lệ', () => {
  assert.equal(dinhDangSo(1200), (1200).toLocaleString('vi-VN'))
  assert.equal(dinhDangSo(null), '—')
  assert.equal(dinhDangUsd(null), 'chưa có giá')
  assert.equal(dinhDangUsd(0.01234), '$0.0123')
  assert.equal(dinhDangUsd(12.5), '$12.50')
  assert.equal(tenNguon('cham-cot'), 'Bộ chấm cột (Claude API)')
  assert.equal(tenNguon('B/claude-1'), 'B/claude-1')
  assert.equal(tiLe(0.5), '50%')
  assert.equal(tiLe(null), 'chờ phần 4')
})

test('khoá mục Phê duyệt không trùng giữa các mục hệ', () => {
  const a = khoaMuc({ loai: 'he', du_an: '_tram', bead_id: null, chi_tiet: { su_kien: 'khe.cau_dao_ngat', khe_id: 'B/a' } })
  const b = khoaMuc({ loai: 'he', du_an: '_tram', bead_id: null, chi_tiet: { su_kien: 'khe.cau_dao_ngat', khe_id: 'B/b' } })
  assert.notEqual(a, b)
  assert.equal(khoaMuc({ loai: 'cho-review', du_an: 'hr', bead_id: 'hr-1', chi_tiet: {} }), 'cho-review/hr/hr-1//')
})
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `cd frontend && node --test tests/doi_ngu.test.mjs`
Expected: FAIL — `Error [ERR_MODULE_NOT_FOUND]: Cannot find module '…/frontend/src/luat_doi_ngu.js'`

- [ ] **Step 3: Viết mã**

`frontend/src/luat_doi_ngu.js` (mới):

```js
// Luật hiển thị thuần của trang Đội ngũ AI + Usage (lát 2b). Trạng thái khe, cảnh báo hạn mức tính ở server
// (tram/phieu/trang_thai.py, tram/suy/doi_ngu.py) — ở đây chỉ đổi sang chữ.
import { gioVN } from './luat.js'

export const TEN_TRANG_THAI_KHE = {
  lam: 'Đang làm', can_nguoi: 'Cần Đại ca', ranh: 'Rảnh', tat: 'Tắt', loi: 'Lỗi lần chạy cuối',
  mat_ket_noi: 'Mất kết nối',
}
const TEN_CUA_SO = { '5h': 'Cửa sổ 5 giờ', tuan: 'Cửa sổ tuần' }
const TEN_NGUON = { 'cham-cot': 'Bộ chấm cột (Claude API)' }
const LY_DO_CAU_DAO = { 'het-han-muc': 'hết hạn mức', 'loi-lien-tiep': 'lỗi không do agent liên tiếp' }
export const CANH_BAO_HAN_MUC = {
  ngung: ['loi', 'Hạn mức chạm ngưỡng ngừng — không nhận việc mới'],
  chi_p0_p1: ['canh-bao', 'Cửa sổ tuần cao — chỉ nhận việc P0–P1'],
  chua_biet: ['canh-bao', 'Hạn mức chưa biết — vẫn nhận việc (#15)'],
}

export function nhanTrangThai(khe) {
  if (khe.cau_dao && khe.cau_dao.ngat) return 'Cầu dao ngắt'
  return TEN_TRANG_THAI_KHE[khe.trang_thai] ?? khe.trang_thai
}

// `phan_tram` là phần ĐÃ DÙNG (spec 3 §8.1–8.2: ≥ 90% thì ngừng nhận việc).
export function moTaCuaSo(cs) {
  const ten = TEN_CUA_SO[cs.loai] ?? cs.loai
  if (cs.trang_thai !== 'biet') {
    return `${ten}: chưa biết${cs.doc_luc ? ` (số đo cũ, đọc lúc ${gioVN(cs.doc_luc)})` : ''}`
  }
  const con = Math.max(0, 100 - cs.phan_tram)
  const reset = cs.reset_luc ? ` · reset ${gioVN(cs.reset_luc)}` : ''
  return `${ten}: còn ${con.toFixed(0)}% (đã dùng ${cs.phan_tram.toFixed(0)}%)${reset} · đọc lúc ${gioVN(cs.doc_luc)}`
}

export function lyDoCauDao(lyDo) {
  return LY_DO_CAU_DAO[lyDo] ?? lyDo ?? ''
}

export function nutKhe(khe) {
  return { tat: khe.trang_thai !== 'tat', bat: khe.trang_thai === 'tat', dongCauDao: Boolean(khe.cau_dao?.ngat) }
}

export function dinhDangSo(n) {
  return typeof n === 'number' ? n.toLocaleString('vi-VN') : '—'
}

export function dinhDangUsd(x) {
  if (typeof x !== 'number') return 'chưa có giá'
  return `$${x < 1 ? x.toFixed(4) : x.toFixed(2)}`
}

export function tenNguon(khoa) {
  return TEN_NGUON[khoa] ?? khoa
}

export function tiLe(x) {
  return typeof x === 'number' ? `${(x * 100).toFixed(0)}%` : 'chờ phần 4'
}

// Khoá v-for của mục Phê duyệt: mục "Hệ cần xem" không gắn bead có thể trùng (du_an, bead_id).
export function khoaMuc(m) {
  return [m.loai, m.du_an, m.bead_id || '', m.chi_tiet?.su_kien || '', m.chi_tiet?.khe_id || ''].join('/')
}
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `cd frontend && npm run kiem`
Expected: `ℹ tests 13` · `ℹ fail 0` (M₀ + 6) và `kiem-an-toan: … không có chèn HTML thô`

Run: `cd frontend && npm run build`
Expected: `✓ built in …`

Run: `uv run pytest -q`
Expected: `N₀ passed` (task này không đụng Python)

- [ ] **Step 5: Commit**

```bash
git add frontend/src/luat_doi_ngu.js frontend/tests/doi_ngu.test.mjs
git commit -m "feat(frontend): luật hiển thị Đội ngũ AI + Usage — trạng thái khe, cửa sổ hạn mức, định dạng (spec 2 §5.4; plan 2b G10–G13)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 8: Thao tác tắt / bật khe, đóng cầu dao — idempotent, qua đường ghi của 3a-1

**Độ khó:** `de` · **Đợt:** 2 · **Song song với:** Task 9, 10 · **Phải xong (đã ghép vào `main`) trước khi bắt đầu:** Task 1

**Files:**
- Create: `tram/thao_tac/khe.py`
- Test: `tests/test_thao_tac_khe.py` (mới)

**Interfaces:**
- Consumes: `bat_tat_khe(..., them)`, `dong_cau_dao(..., them)`, `phien_ban_khe` (Task 1); `su_kien_khe`, `trang_thai_cau_dao`, `KhoPhieu`, `DU_AN_TRAM` (3a-1); `chay_thao_tac`, `YeuCau`, `KetQuaThaoTac`, `digest`, `KhoThaoTac`, `TAC_NHAN`, `XungDot`, `KhongThay` (2a).
- Produces: `tat_khe_thao_tac(kho, kho_tt, khe_id, *, vi_sao, ma, expected_version, luc) -> KetQuaThaoTac` (không kiểm phiên bản — G5); `bat_khe_thao_tac(...)` (kiểm phiên bản); `dong_cau_dao_thao_tac(kho, kho_tt, khe_id, *, ma, expected_version, luc)` (kiểm phiên bản + đang ngắt). `YeuCau.du_an = "_tram"`, `YeuCau.bead_id = khe_id` (khoá tuần tự hoá theo khe; cột `thao_tac.bead_id` chứa `khe_id`). `ket_qua = {"khe.tat" | "khe.bat" | "khe.cau_dao_dong": true}`.

- [ ] **Step 1: Viết test thất bại**

`tests/test_thao_tac_khe.py` (mới):

```python
from datetime import timedelta

import pytest

from kho_phieu_gia import LUC, kho_tam
from tram.phieu.cau_dao import ngat_cau_dao, trang_thai_cau_dao
from tram.phieu.khe import bat_tat_khe, dang_ky_khe, khe_dang_bat, phien_ban_khe
from tram.thao_tac.chay import YeuCau, digest
from tram.thao_tac.khe import bat_khe_thao_tac, dong_cau_dao_thao_tac, tat_khe_thao_tac
from tram.thao_tac.kho import KhoThaoTac
from tram.thao_tac.loi import KhongThay, XungDot

KHE = "B/claude-1"


def _kho(tmp_path):
    kho = kho_tam(tmp_path)
    with kho.giao_dich():
        dang_ky_khe(kho, "B", [{"ten": "claude-1", "cli": "claude", "ten_goi_nho": "1", "vai_uu_tien": ["coder"]}],
                    luc=LUC)
    return kho, KhoThaoTac(tmp_path / "su-kien.db")


def _su_kien(kho, loai):
    return kho.db.execute("SELECT du_lieu, tac_nhan FROM su_kien WHERE loai = ?", (loai,)).fetchall()


def test_tat_khe_mot_lan_theo_ma_khong_kiem_version(tmp_path):
    kho, kt = _kho(tmp_path)
    a = tat_khe_thao_tac(kho, kt, KHE, vi_sao=" để dành ", ma="ma-tat-0001", expected_version="cu", luc=LUC)
    b = tat_khe_thao_tac(kho, kt, KHE, vi_sao="để dành", ma="ma-tat-0001", expected_version="khac", luc=LUC)
    assert (a.lap_lai, b.lap_lai, khe_dang_bat(kho, KHE)) == (False, True, False)
    assert _su_kien(kho, "khe.tat") == [('{"khe_id": "B/claude-1", "ma_thao_tac": "ma-tat-0001", "vi_sao": "để dành"}',
                                         "dai-ca/dashboard")]
    with pytest.raises(XungDot):
        tat_khe_thao_tac(kho, kt, KHE, vi_sao="khác", ma="ma-tat-0001", expected_version="", luc=LUC)
    with pytest.raises(KhongThay):
        tat_khe_thao_tac(kho, kt, "B/claude-9", vi_sao="", ma="ma-tat-0002", expected_version="", luc=LUC)


def test_bat_khe_kiem_version(tmp_path):
    kho, kt = _kho(tmp_path)
    tat_khe_thao_tac(kho, kt, KHE, vi_sao="", ma="ma-tat-0001", expected_version="", luc=LUC)
    with pytest.raises(XungDot):
        bat_khe_thao_tac(kho, kt, KHE, vi_sao="", ma="ma-bat-0001", expected_version="0:0", luc=LUC)
    bat_khe_thao_tac(kho, kt, KHE, vi_sao="", ma="ma-bat-0002", expected_version=phien_ban_khe(kho, KHE), luc=LUC)
    assert khe_dang_bat(kho, KHE)
    # Crash sau tạo thao tác, trước ghi sự kiện; CLI tắt khe trong khoảng đó.
    cu = phien_ban_khe(kho, KHE)
    yc = YeuCau("ma-bat-0003", "khe.bat", "_tram", KHE, {"vi_sao": ""}, cu)
    kt.tao(yc.ma, loai=yc.loai, du_an=yc.du_an, bead_id=KHE, digest=digest(yc), expected_version=cu)
    with kho.giao_dich():
        bat_tat_khe(kho, KHE, bat=False, vi_sao="giữ hạn mức", tac_nhan="dai-ca/cli", luc=LUC)
    for version in (cu, phien_ban_khe(kho, KHE)):
        with pytest.raises(XungDot):
            bat_khe_thao_tac(kho, kt, KHE, vi_sao="", ma=yc.ma, expected_version=version, luc=LUC)
    assert not khe_dang_bat(kho, KHE)


def test_dong_cau_dao_chi_khi_dang_ngat(tmp_path):
    kho, kt = _kho(tmp_path)
    with pytest.raises(XungDot, match="đang đóng"):
        dong_cau_dao_thao_tac(kho, kt, KHE, ma="ma-dao-0001", expected_version=phien_ban_khe(kho, KHE), luc=LUC)
    with kho.giao_dich():
        ngat_cau_dao(kho, KHE, ly_do="het-han-muc", toi_luc=LUC + timedelta(hours=1), luc=LUC)
    kq = dong_cau_dao_thao_tac(kho, kt, KHE, ma="ma-dao-0002", expected_version=phien_ban_khe(kho, KHE), luc=LUC)
    assert kq.ket_qua == {"khe.cau_dao_dong": True} and not trang_thai_cau_dao(kho, KHE, LUC).ngat
    assert '"ly_do": "dai-ca"' in _su_kien(kho, "khe.cau_dao_dong")[0][0]


def test_crash_sau_khi_ghi_su_kien_khong_ghi_lan_hai(tmp_path):
    kho, kt = _kho(tmp_path)
    yc = YeuCau("ma-tat-0009", "khe.tat", "_tram", KHE, {"vi_sao": ""}, "")
    kt.tao(yc.ma, loai=yc.loai, du_an=yc.du_an, bead_id=yc.bead_id, digest=digest(yc), expected_version="")
    with kho.giao_dich():
        bat_tat_khe(kho, KHE, bat=False, vi_sao="", tac_nhan="dai-ca/dashboard", luc=LUC,
                    them={"ma_thao_tac": "ma-tat-0009"})
    kq = tat_khe_thao_tac(kho, kt, KHE, vi_sao="", ma="ma-tat-0009", expected_version="", luc=LUC)
    assert kq.lap_lai is False and len(_su_kien(kho, "khe.tat")) == 1
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_thao_tac_khe.py -q`
Expected: FAIL — `1 error` (`ModuleNotFoundError: No module named 'tram.thao_tac.khe'`)

- [ ] **Step 3: Viết mã**

`tram/thao_tac/khe.py` (mới):

```python
"""Tắt / bật khe và đóng cầu dao từ dashboard 2b (spec 2 §5.4, §7, §12.3; spec 3 §8.3, §10).

Idempotent theo `ma_thao_tac` (bảng `thao_tac`), và ghi QUA ĐÚNG đường ghi của phần 3 — `bat_tat_khe`,
`dong_cau_dao` trong `KhoPhieu.giao_dich()` — nên nhịp tim (dừng mềm `khe-tat`), cấp phiếu và `trang_thai_khe`
thấy y như lệnh `tram tho tat-khe`. Sự kiện mang `ma_thao_tac`, `tac_nhan = dai-ca/dashboard`."""
from collections.abc import Callable
from datetime import datetime

from tram.phieu.cau_dao import dong_cau_dao, trang_thai_cau_dao
from tram.phieu.khe import bat_tat_khe, phien_ban_khe, su_kien_khe
from tram.phieu.kho import DU_AN_TRAM, KhoPhieu
from tram.thao_tac.chay import KetQuaThaoTac, YeuCau, chay_thao_tac
from tram.thao_tac.chung import TAC_NHAN
from tram.thao_tac.kho import KhoThaoTac
from tram.thao_tac.loi import KhongThay, XungDot


def _da_ghi(kho: KhoPhieu, loai: str, ma: str) -> bool:
    return kho.db.execute("SELECT 1 FROM su_kien WHERE du_an = ? AND loai = ? AND json_extract(du_lieu,"
                          " '$.ma_thao_tac') = ? LIMIT 1", (DU_AN_TRAM, loai, ma)).fetchone() is not None


def _kiem_khe(kho: KhoPhieu, khe_id: str) -> None:
    if su_kien_khe(kho, khe_id, ("khe.dang_ky",)) is None:
        raise KhongThay(f"Không có khe {khe_id}")


def _kiem_version(kho: KhoPhieu, khe_id: str, expected: str) -> None:
    _kiem_khe(kho, khe_id)
    if (hien := phien_ban_khe(kho, khe_id)) != expected:
        raise XungDot(f"Khe {khe_id} đã đổi (hiện {hien}, đang xem {expected}) — tải lại")


def _chay(kho: KhoPhieu, kho_tt: KhoThaoTac, yc: YeuCau, kiem: Callable[[], None],
          ghi: Callable[[], None]) -> KetQuaThaoTac:
    def buoc(_) -> bool:
        with kho.giao_dich():
            if not _da_ghi(kho, yc.loai, yc.ma):     # crash giữa ghi sự kiện và đánh dấu bước: không ghi lần hai
                # Kiểm và ghi cùng BEGIN IMMEDIATE: cả lần đầu lẫn resume sau crash.
                bg = kho_tt.lay(yc.ma)
                if yc.loai != "khe.tat" and bg.expected_version != yc.expected_version:
                    raise XungDot("Thao tác chưa xong phải giữ phiên bản gốc; tải lại và dùng mã mới")
                kiem()
                ghi()
        return True
    return chay_thao_tac(kho_tt, yc, kiem_moi=kiem, cac_buoc=[(yc.loai, buoc)])


def tat_khe_thao_tac(kho: KhoPhieu, kho_tt: KhoThaoTac, khe_id: str, *, vi_sao: str | None, ma: str,
                     expected_version: str, luc: datetime) -> KetQuaThaoTac:
    """KHÔNG kiểm `expected_version` (như estop — plan 2b G9): tắt khe không được hỏng vì màn hình cũ."""
    vs = (vi_sao or "").strip()
    yc = YeuCau(ma, "khe.tat", DU_AN_TRAM, khe_id, {"vi_sao": vs}, expected_version)
    return _chay(kho, kho_tt, yc, lambda: _kiem_khe(kho, khe_id), lambda: bat_tat_khe(
        kho, khe_id, bat=False, vi_sao=vs, tac_nhan=TAC_NHAN, luc=luc, them={"ma_thao_tac": ma}))


def bat_khe_thao_tac(kho: KhoPhieu, kho_tt: KhoThaoTac, khe_id: str, *, vi_sao: str | None, ma: str,
                     expected_version: str, luc: datetime) -> KetQuaThaoTac:
    vs = (vi_sao or "").strip()
    yc = YeuCau(ma, "khe.bat", DU_AN_TRAM, khe_id, {"vi_sao": vs}, expected_version)
    return _chay(kho, kho_tt, yc, lambda: _kiem_version(kho, khe_id, expected_version), lambda: bat_tat_khe(
        kho, khe_id, bat=True, vi_sao=vs, tac_nhan=TAC_NHAN, luc=luc, them={"ma_thao_tac": ma}))


def dong_cau_dao_thao_tac(kho: KhoPhieu, kho_tt: KhoThaoTac, khe_id: str, *, ma: str, expected_version: str,
                          luc: datetime) -> KetQuaThaoTac:
    def kiem() -> None:
        _kiem_version(kho, khe_id, expected_version)
        if not trang_thai_cau_dao(kho, khe_id, luc).ngat:
            raise XungDot(f"Cầu dao khe {khe_id} đang đóng — tải lại")

    yc = YeuCau(ma, "khe.cau_dao_dong", DU_AN_TRAM, khe_id, {}, expected_version)
    return _chay(kho, kho_tt, yc, kiem, lambda: dong_cau_dao(
        kho, khe_id, ly_do="dai-ca", luc=luc, tac_nhan=TAC_NHAN, them={"ma_thao_tac": ma}))
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_thao_tac_khe.py -q`
Expected: `4 passed`

Run: `uv run pytest -q`
Expected: `N₀ + 36 passed` (1051 — trên `main` sau đợt 1 + riêng task này)

- [ ] **Step 5: Commit**

```bash
git add tram/thao_tac/khe.py tests/test_thao_tac_khe.py
git commit -m "feat(thao_tac): tắt/bật khe, đóng cầu dao từ dashboard — idempotent theo ma_thao_tac, ghi qua bat_tat_khe/dong_cau_dao (spec 2 §5.4, §12.3; spec 3 §8.3)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 9: Suy màn Đội ngũ — thẻ khe, mức hạn mức, luật vai ↔ khe, bảng điểm thợ

**Độ khó:** `de` · **Đợt:** 2 · **Song song với:** Task 8, 10 · **Phải xong trước:** Task 1

**Files:**
- Create: `tram/suy/bang_diem.py`
- Create: `tram/suy/doi_ngu.py`
- Test: `tests/test_suy_doi_ngu.py` (mới)

**Interfaces:**
- Consumes: `trang_thai_khe`, `TrangThaiKhe` (3a-1 Task 21); `phien_ban_khe` (Task 1); `HanMuc`, `co_chua_biet`, `cham_nguong_ngung`, `duoc_nhan` (3a-1 Task 4); `CauHinhTram`, `CauHinhHanMuc` (3a-1 Task 5); `VAI_CUA_BUOC` (3a-1 Task 11); `lam_sach`; test: `dat_phieu`, `kho_tam`, `LUC`, `ghi_nhip`, `danh_dau_ket_thuc`.
- Produces: `bang_diem(db) -> list[{khe_id, vai, so_phieu, so_xong, lan_chay_tb: float | None, qua_lan_dau: None, bi_tra_ve: None}]` (G9); `LUAT_VAI: tuple[str, ...]`; `muc_han_muc(hm: HanMuc, ng: CauHinhHanMuc) -> "ngung" | "chi_p0_p1" | "chua_biet" | "ok"`; `the_khe(kho, tt, ch) -> dict`; `doi_ngu(kho, *, bay_gio, ch) -> {"bat": True, "khe": [...], "luat_vai": {...}, "bang_diem": [...]}` — đúng "Hợp đồng JSON".

- [ ] **Step 1: Viết test thất bại**

`tests/test_suy_doi_ngu.py` (mới):

```python
from datetime import timedelta

from kho_phieu_gia import LUC, dat_phieu, kho_tam
from tram.cau_hinh.tram import CauHinhHanMuc, CauHinhTram
from tram.han_muc.mo_hinh import CuaSo, HanMuc
from tram.phieu.ghi import danh_dau_ket_thuc
from tram.phieu.khe import dang_ky_khe, phien_ban_khe
from tram.phieu.nhip_tim import ghi_nhip
from tram.suy.bang_diem import bang_diem
from tram.suy.doi_ngu import doi_ngu, muc_han_muc

NG = CauHinhHanMuc()


def cs(loai, pt):
    return CuaSo(loai=loai, trang_thai="biet", phan_tram=pt, reset_luc="2026-10-13T05:00:00Z",
                 doc_luc="2026-10-13T02:59:00Z")


def hm(*c):
    return HanMuc(khe_id="B/a", nguon="stream", cua_so=list(c))


def test_muc_han_muc_theo_luat_nhan_viec():
    assert muc_han_muc(hm(cs("5h", 90), cs("tuan", 1)), NG) == "ngung"
    assert muc_han_muc(hm(cs("5h", 10), cs("tuan", 80)), NG) == "chi_p0_p1"
    assert muc_han_muc(hm(cs("5h", 10), CuaSo(loai="tuan", trang_thai="chua_biet")), NG) == "chua_biet"
    assert muc_han_muc(hm(cs("5h", 10), cs("tuan", 10)), NG) == "ok"


def test_doi_ngu_the_khe_ten_goi_nho_khong_email_va_phien_ban(tmp_path):
    kho = kho_tam(tmp_path)
    with kho.giao_dich():
        dang_ky_khe(kho, "B", [{"ten": "claude-1", "cli": "claude", "ten_goi_nho": "Claude 1", "vai_uu_tien": ["coder"]},
                               {"ten": "claude-2", "cli": "claude", "ten_goi_nho": "a@b.vn", "vai_uu_tien": ["qc"]}],
                    luc=LUC)
        ghi_nhip(kho, "B/claude-1", luc=LUC, giao_id=None, luot=None, buoc_tho="chay",
                 han_muc=HanMuc(khe_id="B/claude-1", nguon="stream", cua_so=[cs("5h", 40), cs("tuan", 85)]))
    p = dat_phieu(kho, "B/claude-1", bead_id="hr-1", tieu_de="Sửa ‮giá")
    r = doi_ngu(kho, bay_gio=LUC, ch=CauHinhTram())
    k1, k2 = r["khe"]
    assert (k1["khe_id"], k1["may"], k1["ten_goi_nho"], k1["trang_thai"], k1["so_phien"]) == (
        "B/claude-1", "B", "Claude 1", "lam", 1)
    assert k1["phieu"] == {"giao_id": p.giao_id, "bead_id": "hr-1", "du_an": "hr-codex", "buoc": "code",
                           "tieu_de": "Sửa giá"}
    assert k1["muc_han_muc"] == "chi_p0_p1" and k1["phien_ban"] == phien_ban_khe(kho, "B/claude-1")
    assert (k2["ten_goi_nho"], k2["trang_thai"], k2["muc_han_muc"]) == ("B/claude-2", "mat_ket_noi", "chua_biet")
    assert "a@b.vn" not in str(r) and "ma_giao" not in str(r)
    assert r["luat_vai"]["vai_cua_buoc"] == {"code": "coder", "qc": "qc", "spec": "spec"}
    assert r["bang_diem"][0]["khe_id"] == "B/claude-1"


def test_bang_diem_lan_chay_trung_binh_tren_phieu_da_ket_thuc(tmp_path):
    kho = kho_tam(tmp_path)
    for i, (bead, kt, lan) in enumerate([("hr-1", "xong", 1), ("hr-2", "bi", 3), ("hr-3", None, 2)]):
        p = dat_phieu(kho, "B/claude-1", luc=LUC + timedelta(minutes=i), bead_id=bead)
        with kho.giao_dich() as db:
            for j in range(lan):
                db.execute("INSERT INTO lan_chay VALUES (?, 'B/claude-1', ?, ?, ?)",
                           (f"r-{bead}-{j}", p.giao_id, j + 1, "2026-10-13T03:00:00Z"))
            if kt:
                danh_dau_ket_thuc(db, p.giao_id, kt, LUC)
    dat_phieu(kho, "B/claude-2", bead_id="hr-9", buoc="qc")
    assert bang_diem(kho.db) == [
        {"khe_id": "B/claude-1", "vai": "coder", "so_phieu": 3, "so_xong": 1, "lan_chay_tb": 2.0,
         "qua_lan_dau": None, "bi_tra_ve": None},
        {"khe_id": "B/claude-2", "vai": "qc", "so_phieu": 1, "so_xong": 0, "lan_chay_tb": None,
         "qua_lan_dau": None, "bi_tra_ve": None}]
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_suy_doi_ngu.py -q`
Expected: FAIL — `1 error` (`ModuleNotFoundError: No module named 'tram.suy.bang_diem'`)

- [ ] **Step 3: Viết mã**

`tram/suy/bang_diem.py` (mới):

```python
"""Bảng điểm thợ theo (khe, vai) — spec 2 §5.4; công thức ở spec 4 §12 (spec 4 CHƯA DUYỆT).

Lát 2b chỉ tính phần có sẵn trong kho phiếu của phần 3: số phiếu, số phiếu kết thúc `xong`, và *số lần chạy trung
bình* = trung bình số `chay.bat_dau` (bảng `lan_chay`, duy nhất theo `request_id`) trên các phiếu ĐÃ kết thúc.
*Qua lần đầu* và *bị trả về* cần `kiem.lai`, `qc.ket_qua`, `bead.vao_cot_3` của phần 4 → luôn None ở 2b
(plan 2b mục "Để sau")."""
import sqlite3


def bang_diem(db: sqlite3.Connection) -> list[dict]:
    lan = dict(db.execute("SELECT giao_id, COUNT(*) FROM lan_chay GROUP BY giao_id").fetchall())
    nhom: dict[tuple[str, str], dict] = {}
    for giao_id, khe_id, vai, trang_thai, ket_thuc in db.execute(
            "SELECT giao_id, khe_id, json_extract(noi_dung, '$.vai'), trang_thai, ket_thuc FROM phieu ORDER BY giao_id"):
        x = nhom.setdefault((khe_id, vai), {"so_phieu": 0, "so_xong": 0, "lan": []})
        x["so_phieu"] += 1
        x["so_xong"] += ket_thuc == "xong"
        if trang_thai == "ket_thuc":
            x["lan"].append(lan.get(giao_id, 0))
    return [{"khe_id": k, "vai": v, "so_phieu": x["so_phieu"], "so_xong": x["so_xong"],
             "lan_chay_tb": round(sum(x["lan"]) / len(x["lan"]), 2) if x["lan"] else None,
             "qua_lan_dau": None, "bi_tra_ve": None} for (k, v), x in sorted(nhom.items())]
```

`tram/suy/doi_ngu.py` (mới):

```python
"""Màn Đội ngũ AI (spec 2 §5.4): mỗi khe một thẻ — suy từ `trang_thai_khe` của phần 3 (spec 3 §10.1) — kèm
`phien_ban` cho thao tác bật/tắt/đóng cầu dao (§12.3), mức hạn mức theo luật nhận việc (spec 3 §8.2), luật
vai ↔ khe và bảng điểm thợ. Tên gợi nhớ, KHÔNG BAO GIỜ email (§5.4)."""
from datetime import datetime

from tram.cau_hinh.tram import CauHinhHanMuc, CauHinhTram
from tram.han_muc.luat import cham_nguong_ngung, duoc_nhan
from tram.han_muc.mo_hinh import HanMuc, co_chua_biet
from tram.phieu.khe import phien_ban_khe
from tram.phieu.kho import KhoPhieu
from tram.phieu.mo_hinh import VAI_CUA_BUOC
from tram.phieu.trang_thai import TrangThaiKhe, trang_thai_khe
from tram.suy.bang_diem import bang_diem
from tram.suy.lam_sach import lam_sach

LUAT_VAI = (
    "Vai là ưu tiên, không cố định: khe cạn hạn mức thì khe khác nhận vai đó (kiến trúc Q14).",
    "Luật cứng: khe đã code một bead không bao giờ QC chính bead đó — thiếu khe khác thì bead chờ (Q14).",
    "Khe tắt, cầu dao ngắt, mất kết nối, hoặc có cửa sổ hạn mức đã biết ≥ ngưỡng ngừng: không nhận việc mới "
    "(spec 3 §6.2, §8.2); cửa sổ tuần ≥ ngưỡng ưu tiên: chỉ nhận P0–P1.",
    "Hạn mức chưa biết vẫn nhận việc, kèm cảnh báo vàng (#15).",
    "Chọn bead, bước và khe cụ thể là việc của bộ giao việc phần 4 (spec 4 §5.3 — chưa duyệt).",
)


def muc_han_muc(hm: HanMuc, ng: CauHinhHanMuc) -> str:
    """`ngung` (luật 1) | `chi_p0_p1` (luật 2) | `chua_biet` (luật 3, vàng) | `ok`."""
    if cham_nguong_ngung(hm, ngung=ng.ngung):
        return "ngung"
    if not duoc_nhan(hm, 2, ngung=ng.ngung, tuan_chi_uu_tien=ng.tuan_chi_uu_tien):
        return "chi_p0_p1"
    return "chua_biet" if co_chua_biet(hm) else "ok"


def _ten(tt: TrangThaiKhe) -> str:
    ten = lam_sach(tt.ten_goi_nho, 64)
    return tt.khe_id if not ten or "@" in ten else ten


def the_khe(kho: KhoPhieu, tt: TrangThaiKhe, ch: CauHinhTram) -> dict:
    # Danh sách cho phép, không serialize cả phiếu nếu upstream thêm credential.
    phieu = None if tt.phieu is None else {
        **{k: tt.phieu[k] for k in ("giao_id", "du_an", "bead_id", "buoc", "vai") if k in tt.phieu},
        "tieu_de": lam_sach(tt.phieu["tieu_de"], 200)}
    return {"khe_id": tt.khe_id, "may": tt.khe_id.split("/")[0], "cli": tt.cli, "ten_goi_nho": _ten(tt),
            "vai_uu_tien": list(tt.vai_uu_tien), "trang_thai": tt.trang_thai, "phieu": phieu,
            "han_muc": tt.han_muc, "muc_han_muc": muc_han_muc(HanMuc.model_validate(tt.han_muc), ch.han_muc),
            "cau_dao": tt.cau_dao, "so_phien": tt.so_phien, "nhip_cuoi": tt.nhip_cuoi,
            "phien_ban": phien_ban_khe(kho, tt.khe_id)}


def doi_ngu(kho: KhoPhieu, *, bay_gio: datetime, ch: CauHinhTram) -> dict:
    return {"bat": True, "khe": [the_khe(kho, tt, ch) for tt in trang_thai_khe(kho, bay_gio=bay_gio, ch=ch)],
            "luat_vai": {"vai_cua_buoc": dict(VAI_CUA_BUOC), "luat": list(LUAT_VAI)},
            "bang_diem": bang_diem(kho.db)}
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_suy_doi_ngu.py -q`
Expected: `3 passed`

Run: `uv run pytest -q`
Expected: `N₀ + 35 passed` (1050)

- [ ] **Step 5: Commit**

```bash
git add tram/suy/bang_diem.py tram/suy/doi_ngu.py tests/test_suy_doi_ngu.py
git commit -m "feat(suy): màn Đội ngũ — thẻ khe từ trang_thai_khe, mức hạn mức, luật vai, bảng điểm phần tính được (spec 2 §5.4; plan 2b G9–G12, G18)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 10: Frontend — trang Đội ngũ AI, nút tắt/bật/đóng cầu dao, nối Phê duyệt

**Độ khó:** `de` · **Đợt:** 2 · **Song song với:** Task 8, 9 (chỉ đụng `frontend/`) · **Phải xong trước:** Task 7

**Files:**
- Create: `frontend/src/thanh/HopKhe.vue`
- Create: `frontend/src/thanh/TheKhe.vue`
- Create: `frontend/src/trang/DoiNgu.vue`
- Modify: `frontend/src/kho.js`, `frontend/src/tuyen.js`, `frontend/src/KhungChinh.vue`, `frontend/src/trang/PheDuyet.vue`, `frontend/src/thanh/MucPheDuyet.vue` (2a)

**Interfaces:**
- Consumes: "Hợp đồng JSON" (`GET /api/doi-ngu`, `POST /api/khe/…`, SSE `doi_ngu_doi`); `doc`, `ghi`, `thanGhi` (`api.js`); `kho` (`kho.js`); `gioVN`; mọi hàm của `luat_doi_ngu.js` (Task 7).
- Produces: route `/doi-ngu`, mục menu "Đội ngũ AI"; `kho.phienBanDoiNgu` (tăng khi có `doi_ngu_doi` — Task 12 dùng); `TheKhe` (props `khe`, `laDaiCa`; emit `doi`), `HopKhe` (props `khe`, `bat`; emit `huy`, `xac-nhan(viSao)`).

Giao diện dựng theo skill `frontend-ui-engineering` như 2a (spec 2 §12.5: không có bản vẽ, Đại ca xem lại khi kiểm tay): lưới thẻ một cột dưới ~22 rem, chế độ tối theo biến màu của 2a, focus nhìn thấy. Nút ghi bị khoá khi không có danh tính Đại ca (`kho.trangThai.la_dai_ca`). Tắt khe đang làm → hộp xác nhận nói rõ phiếu sẽ **dừng mềm**; đóng cầu dao → `window.confirm` (như estop). Mọi chuỗi từ server hiển thị bằng `{{ }}`.

- [ ] **Step 1: Chạy kiểm hiện tại (mốc)**

Run: `cd frontend && npm run kiem && npm run build`
Expected: `ℹ tests 13` · `ℹ fail 0`; `✓ built in …` (task này không thêm test đơn vị — cổng kiểm là `kiem-an-toan` + `vite build`, như Task 23–25 plan 2a)

- [ ] **Step 2: Viết component mới**

`frontend/src/thanh/HopKhe.vue` (mới):

```vue
<script setup>
import { ref } from 'vue'

defineProps({ khe: { type: Object, required: true }, bat: { type: Boolean, default: false } })
const emit = defineEmits(['huy', 'xac-nhan'])
const viSao = ref('')
</script>

<template>
  <div class="nen-mo" role="dialog" aria-modal="true" aria-labelledby="hop-khe-td" @keydown.esc="emit('huy')">
    <form class="hop" @submit.prevent="emit('xac-nhan', viSao.trim())">
      <h2 id="hop-khe-td">{{ bat ? 'Bật' : 'Tắt' }} khe {{ khe.ten_goi_nho }} ({{ khe.khe_id }})</h2>
      <p v-if="!bat && khe.phieu" class="canh-bao">Khe đang làm {{ khe.phieu.du_an }}/{{ khe.phieu.bead_id }} — phiếu
        sẽ dừng mềm (lưu phần đã làm, bộ giao việc giao lại cho khe khác).</p>
      <p v-if="!bat" class="nho">Không giao việc mới cho khe này tới khi Đại ca bật lại.</p>
      <label>Vì sao? (tuỳ chọn)<textarea v-model="viSao" rows="2" maxlength="500" autofocus></textarea></label>
      <div class="nut">
        <button type="button" @click="emit('huy')">Huỷ</button>
        <button type="submit">{{ bat ? 'Bật khe' : 'Tắt khe' }}</button>
      </div>
    </form>
  </div>
</template>
```

`frontend/src/thanh/TheKhe.vue` (mới):

```vue
<script setup>
import { ref } from 'vue'
import { ghi, thanGhi } from '../api.js'
import { gioVN } from '../luat.js'
import { CANH_BAO_HAN_MUC, lyDoCauDao, moTaCuaSo, nhanTrangThai, nutKhe } from '../luat_doi_ngu.js'
import HopKhe from './HopKhe.vue'

const props = defineProps({ khe: { type: Object, required: true }, laDaiCa: { type: Boolean, default: false } })
const emit = defineEmits(['doi'])
const hop = ref('')
const dangGui = ref(false)
const loi = ref('')
const duong = () => `/api/khe/${props.khe.khe_id.split('/').map(encodeURIComponent).join('/')}`

async function lam(hanhDong, noiDung = {}) {
  dangGui.value = true
  loi.value = ''
  try {
    await ghi(`${duong()}/${hanhDong}`, thanGhi(noiDung, props.khe.phien_ban))
    hop.value = ''
    emit('doi')
  } catch (e) {
    loi.value = e.status === 409 ? 'Khe đã đổi — đã tải lại.' : e.message
    if (e.status === 409) emit('doi')
  } finally {
    dangGui.value = false
  }
}
function dongCauDao() {
  if (window.confirm(`Đóng cầu dao khe ${props.khe.khe_id}? Khe nhận việc lại ngay dù chưa tới giờ reset.`)) {
    lam('cau-dao-dong')
  }
}
</script>

<template>
  <article class="the-khe" :class="{ mo: khe.trang_thai === 'tat' || khe.trang_thai === 'mat_ket_noi' }">
    <header>
      <strong>{{ khe.ten_goi_nho }}</strong> <span class="ma">{{ khe.khe_id }}</span>
      <span class="chip" :class="{ bat: khe.cau_dao.ngat || khe.trang_thai === 'loi' }">{{ nhanTrangThai(khe) }}</span>
    </header>
    <p class="nho">Máy {{ khe.may }} · CLI {{ khe.cli }} · vai ưu tiên {{ khe.vai_uu_tien.join(', ') }} ·
      {{ khe.so_phien }} phiên đồng thời</p>
    <p v-if="khe.phieu" class="tieu-de">Đang làm <span class="ma">{{ khe.phieu.du_an }}/{{ khe.phieu.bead_id }}</span>
      ({{ khe.phieu.buoc }}) — {{ khe.phieu.tieu_de }}</p>
    <ul class="han-muc">
      <li v-for="cs in khe.han_muc.cua_so" :key="cs.loai">{{ moTaCuaSo(cs) }}</li>
    </ul>
    <p v-if="CANH_BAO_HAN_MUC[khe.muc_han_muc]" :class="CANH_BAO_HAN_MUC[khe.muc_han_muc][0]">
      {{ CANH_BAO_HAN_MUC[khe.muc_han_muc][1] }}</p>
    <p v-if="khe.cau_dao.ngat" class="loi">Cầu dao ngắt tới {{ gioVN(khe.cau_dao.toi_luc) }} —
      {{ lyDoCauDao(khe.cau_dao.ly_do) }}</p>
    <p class="nho">Nhịp tim cuối: {{ khe.nhip_cuoi ? gioVN(khe.nhip_cuoi) : 'chưa có' }}</p>
    <div class="nut">
      <button v-if="nutKhe(khe).tat" type="button" :disabled="dangGui || !laDaiCa" @click="hop = 'tat'">Tắt khe</button>
      <button v-if="nutKhe(khe).bat" type="button" :disabled="dangGui || !laDaiCa" @click="hop = 'bat'">Bật khe</button>
      <button v-if="nutKhe(khe).dongCauDao" type="button" :disabled="dangGui || !laDaiCa" @click="dongCauDao">
        Đóng cầu dao</button>
    </div>
    <HopKhe v-if="hop" :khe="khe" :bat="hop === 'bat'" @huy="hop = ''" @xac-nhan="(vs) => lam(hop, { vi_sao: vs })" />
    <p v-if="loi" class="loi" role="alert">{{ loi }}</p>
  </article>
</template>

<style scoped>
.the-khe { background: var(--mat); border: 1px solid var(--vien); border-radius: 8px; padding: .75rem; }
.the-khe.mo { opacity: .6; }
.the-khe header { display: flex; flex-wrap: wrap; gap: .25rem .5rem; align-items: baseline; }
.han-muc { margin: .25rem 0; padding-left: 1.1rem; font-size: .85rem; }
</style>
```

`frontend/src/trang/DoiNgu.vue` (mới):

```vue
<script setup>
import { onMounted, onUnmounted, ref, watch } from 'vue'
import { doc } from '../api.js'
import { kho } from '../kho.js'
import { dinhDangSo, tiLe } from '../luat_doi_ngu.js'
import TheKhe from '../thanh/TheKhe.vue'

// Nhịp tim không phải sự kiện (spec 3 §10) → "mất kết nối" chỉ thấy khi tải lại; tải lại mỗi 30 giây.
const CHU_KY_MS = 5000
const dl = ref(null)
const loi = ref('')
let hen = null

async function tai() {
  try {
    dl.value = await doc('/api/doi-ngu')
    loi.value = ''
  } catch (e) {
    loi.value = e.message
  }
}
onMounted(() => { tai(); hen = setInterval(tai, CHU_KY_MS) })
onUnmounted(() => clearInterval(hen))
watch(() => kho.phienBanDoiNgu, tai)
</script>

<template>
  <section>
    <h1>Đội ngũ AI</h1>
    <p v-if="loi" class="loi" role="alert">{{ loi }}</p>
    <p v-if="dl && !dl.bat" class="nho">Kho phiếu (phần 3) chưa bật trên trạm.</p>
    <p v-else-if="dl && !dl.khe.length" class="nho">Chưa có khe nào đăng ký với trạm.</p>
    <div v-if="dl && dl.khe.length" class="luoi-khe">
      <TheKhe v-for="k in dl.khe" :key="k.khe_id" :khe="k"
              :la-dai-ca="Boolean(kho.trangThai && kho.trangThai.la_dai_ca)" @doi="tai" />
    </div>
    <template v-if="dl && dl.luat_vai">
      <h2>Luật vai ↔ khe</h2>
      <p class="nho">Bước → vai:
        <span v-for="(vai, buoc) in dl.luat_vai.vai_cua_buoc" :key="buoc" class="nhan-nho">{{ buoc }} → {{ vai }}</span></p>
      <ul class="nho"><li v-for="l in dl.luat_vai.luat" :key="l">{{ l }}</li></ul>
    </template>
    <template v-if="dl && dl.bang_diem.length">
      <h2>Bảng điểm thợ</h2>
      <div class="bang-cuon">
        <table>
          <thead><tr>
            <th scope="col">Khe</th><th scope="col">Vai</th><th scope="col">Số phiếu</th><th scope="col">Xong</th>
            <th scope="col">Lần chạy TB / phiếu</th><th scope="col">Qua lần đầu</th><th scope="col">Bị trả về</th>
          </tr></thead>
          <tbody><tr v-for="d in dl.bang_diem" :key="d.khe_id + '/' + d.vai">
            <th scope="row">{{ d.khe_id }}</th><td>{{ d.vai }}</td><td>{{ d.so_phieu }}</td><td>{{ d.so_xong }}</td>
            <td>{{ d.lan_chay_tb == null ? '—' : dinhDangSo(d.lan_chay_tb) }}</td>
            <td>{{ tiLe(d.qua_lan_dau) }}</td><td>{{ tiLe(d.bi_tra_ve) }}</td>
          </tr></tbody>
        </table>
      </div>
      <p class="nho">"Qua lần đầu" và "Bị trả về" cần kết quả kiểm lại / QC của bộ giao việc (phần 4).</p>
    </template>
  </section>
</template>

<style scoped>
.luoi-khe { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(22rem, 100%), 1fr)); gap: 1rem; }
</style>
```

- [ ] **Step 3: Nối vào khung (bản vá)**

`frontend/src/kho.js`:

```diff
diff --git a/frontend/src/kho.js b/frontend/src/kho.js
index e4a2802..de5a245 100644
--- a/frontend/src/kho.js
+++ b/frontend/src/kho.js
@@ -3,9 +3,9 @@ import { reactive } from 'vue'
 import { doc } from './api.js'
 import { tieuDeTab } from './luat.js'
 import { laSuKienNho } from './nho.js'
 
-export const kho = reactive({ trangThai: null, soPheDuyet: 0, phienBan: 0, phienBanNho: 0, suKienCuoi: null,
+export const kho = reactive({ trangThai: null, soPheDuyet: 0, phienBan: 0, phienBanNho: 0, phienBanDoiNgu: 0, suKienCuoi: null,
   matKetNoi: false, loi: '' })
 
 export async function taiTrangThai() {
   try {
@@ -28,6 +29,7 @@ export function moLuong() {
   const doi = () => { kho.phienBan += 1 }
   es.addEventListener('cong_viec_doi', doi)
   es.addEventListener('phe_duyet_doi', () => { doi(); taiSoPheDuyet(); taiTrangThai() })
+  es.addEventListener('doi_ngu_doi', () => { kho.phienBanDoiNgu += 1 })     // lát 2b: sự kiện khe.*, chay.*, …
   es.addEventListener('su_kien', (e) => {
     try {
       kho.suKienCuoi = JSON.parse(e.data)
```

`frontend/src/tuyen.js`:

```diff
diff --git a/frontend/src/tuyen.js b/frontend/src/tuyen.js
index b12cd13..2c5a1ab 100644
--- a/frontend/src/tuyen.js
+++ b/frontend/src/tuyen.js
@@ -1,5 +1,6 @@
 import CongViec from './trang/CongViec.vue'
+import DoiNgu from './trang/DoiNgu.vue'
 import DuAn from './trang/DuAn.vue'
 import KyUc from './trang/KyUc.vue'
 import PheDuyet from './trang/PheDuyet.vue'
 
@@ -7,5 +8,6 @@ export const tuyen = [
   { path: '/cong-viec', component: CongViec },
   { path: '/du-an', component: DuAn },
   { path: '/phe-duyet', component: PheDuyet },
   { path: '/nho', component: KyUc },
+  { path: '/doi-ngu', component: DoiNgu },
 ]
```

`frontend/src/KhungChinh.vue`:

```diff
diff --git a/frontend/src/KhungChinh.vue b/frontend/src/KhungChinh.vue
index a7063d6..764a83a 100644
--- a/frontend/src/KhungChinh.vue
+++ b/frontend/src/KhungChinh.vue
@@ -14,7 +14,8 @@ onMounted(() => { taiTrangThai(); taiSoPheDuyet(); moLuong() })
       <router-link to="/phe-duyet">Phê duyệt
         <span v-if="kho.soPheDuyet" class="dem" :aria-label="kho.soPheDuyet + ' việc chờ'">{{ kho.soPheDuyet }}</span>
       </router-link>
       <router-link to="/nho">Ký ức</router-link>
+      <router-link to="/doi-ngu">Đội ngũ AI</router-link>
     </nav>
     <ThanhTrangThai />
   </header>
```

`frontend/src/trang/PheDuyet.vue`:

```diff
diff --git a/frontend/src/trang/PheDuyet.vue b/frontend/src/trang/PheDuyet.vue
index 74b89a0..f9cffa0 100644
--- a/frontend/src/trang/PheDuyet.vue
+++ b/frontend/src/trang/PheDuyet.vue
@@ -3,6 +3,7 @@ import { computed, onMounted, ref, watch } from 'vue'
 import { doc } from '../api.js'
 import { kho, taiSoPheDuyet } from '../kho.js'
-import { TEN_PHE_DUYET, khoaMucPheDuyet, nhomPheDuyet } from '../luat.js'
+import { TEN_PHE_DUYET, nhomPheDuyet } from '../luat.js'
+import { khoaMuc } from '../luat_doi_ngu.js'
 import MucPheDuyet from '../thanh/MucPheDuyet.vue'
 
 const ds = ref([])
@@ -36,7 +37,7 @@ watch(() => kho.phienBan, tai)
     <p v-if="!nhom.length && !loi" class="nho">Không có việc nào chờ Đại ca.</p>
     <section v-for="[loai, muc] in nhom" :key="loai">
       <h2>{{ TEN_PHE_DUYET[loai] }} <span class="dem-nho">{{ muc.length }}</span></h2>
-      <MucPheDuyet v-for="m in muc" :key="khoaMucPheDuyet(m)" :muc="m"
+      <MucPheDuyet v-for="m in muc" :key="khoaMuc(m)" :muc="m"
                    :la-dai-ca="Boolean(kho.trangThai && kho.trangThai.la_dai_ca)" @doi="doi" />
     </section>
   </section>
```

`frontend/src/thanh/MucPheDuyet.vue`:

```diff
diff --git a/frontend/src/thanh/MucPheDuyet.vue b/frontend/src/thanh/MucPheDuyet.vue
index cbe84f1..f9b7633 100644
--- a/frontend/src/thanh/MucPheDuyet.vue
+++ b/frontend/src/thanh/MucPheDuyet.vue
@@ -38,7 +38,7 @@ const thuLai = () => lam(`/api/bead/${ma()}/thu-lai`, {})
 
 <template>
   <article class="muc">
-    <header><span class="ma">{{ muc.bead_id || '(cả dự án)' }}</span> <span class="nho">{{ muc.du_an }}</span> {{ muc.tieu_de }}</header>
+    <header><span class="ma">{{ muc.bead_id || (muc.chi_tiet.khe_id ? 'khe' : '(cả dự án)') }}</span> <span class="nho">{{ muc.du_an }}</span> {{ muc.tieu_de }}</header>
     <template v-if="muc.loai === 'cho-review' || muc.loai === 'co-do'">
       <p v-if="laLinkAnToan(muc.chi_tiet.pr)"><a :href="muc.chi_tiet.pr" target="_blank" rel="noopener noreferrer">Mở PR (bàn giao + diff)</a></p>
       <p v-else class="nho">Chưa có link PR GitHub.</p>
@@ -63,6 +63,7 @@ const thuLai = () => lam(`/api/bead/${ma()}/thu-lai`, {})
       <p class="nho">{{ muc.chi_tiet.su_kien }} · {{ gioVN(muc.chi_tiet.luc) }}</p>
       <pre class="van-ban">{{ muc.chi_tiet.loi }}</pre>
       <button v-if="muc.bead_id" type="button" :disabled="dangGui || !laDaiCa" @click="thuLai">Thử lại</button>
+      <router-link v-if="muc.chi_tiet.khe_id" to="/doi-ngu">Mở Đội ngũ AI để đóng cầu dao</router-link>
     </template>
     <p v-if="loi" class="loi" role="alert">{{ loi }}</p>
   </article>
```

Áp bản vá: `git apply --check <file> && git apply <file>` (G2 nếu 1b-3 đã sửa `tuyen.js`/`KhungChinh.vue`/`kho.js`).

- [ ] **Step 4: Chạy kiểm**

Run: `cd frontend && npm run kiem`
Expected: `ℹ tests 13` · `ℹ fail 0`; `kiem-an-toan: … không có chèn HTML thô`

Run: `cd frontend && npm run build`
Expected: `✓ built in …`; `grep -c "<style" dist/index.html` → `0` (CSS của `<style scoped>` nằm trong `dist/assets/*.css`)

Run: `uv run pytest -q`
Expected: `N₀ + 32 passed` (1047 — task này không đụng Python)

- [ ] **Step 5: Commit**

```bash
git add frontend/src/thanh/HopKhe.vue frontend/src/thanh/TheKhe.vue frontend/src/trang/DoiNgu.vue frontend/src/kho.js frontend/src/tuyen.js frontend/src/KhungChinh.vue frontend/src/trang/PheDuyet.vue frontend/src/thanh/MucPheDuyet.vue
git commit -m "feat(frontend): trang Đội ngũ AI — thẻ khe, tắt/bật khe, đóng cầu dao, luật vai, bảng điểm; Phê duyệt link cầu dao (spec 2 §5.4, §5.2)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 11: tram-api — `/api/doi-ngu`, `/api/khe/*`, `/api/usage`

**Độ khó:** `de` · **Đợt:** 3 · **Song song với:** Task 12 · **Phải xong trước:** Task 2, 3, 4, 8, 9

**Files:**
- Create: `tram/api/doi_ngu.py`
- Create: `tram/api/usage.py`
- Modify: `tram/api/app.py` (2a + 3a-1)
- Modify: `tram/api/phu_thuoc.py` (2a + 3a-1)
- Test: `tests/test_api_doi_ngu.py` (mới)

**Interfaces:**
- Consumes: `doi_ngu` (Task 9); `tat_khe_thao_tac`, `bat_khe_thao_tac`, `dong_cau_dao_thao_tac` (Task 8); `doc_dong_usage`, `tong_hop` (Task 3); `KetQuaCcusage`, `DocCcusage`, `BoDemCcusage` (Task 4); `CauHinhUsage`, `nap_cau_hinh_usage` (Task 2); `yeu_cau_ghi`, `ThanGhi`, `KheLa`, lỗi `thao_tac`; `PhuThuocApi.mo_kho_phieu`, `.mo_kho_tt`, `.dong_ho`, `.cau_hinh`.
- Produces: `GET /api/doi-ngu`; `POST /api/khe/{may_id}/{ten}/tat|bat|cau-dao-dong` (`ThanKhe(ThanGhi)` + `vi_sao ≤ 500`); `GET /api/usage?so_ngay=1..92`; `PhuThuocApi.usage: CauHinhUsage = CauHinhUsage()`, `PhuThuocApi.doc_ccusage: Callable[[date, date], KetQuaCcusage] | None = None`; `phu_thuoc_that()` dựng `doc_ccusage` = `BoDemCcusage(DocCcusage(...).theo_ngay).lay` **chỉ khi** có `usage.ccusage` — không chạy ccusage lúc khởi động.

- [ ] **Step 1: Viết test thất bại**

`tests/test_api_doi_ngu.py` (mới):

```python
from dataclasses import replace
from datetime import timedelta

from api_gia import DAI_CA, tao_pt
from asgi_gia import goi
from kho_phieu_gia import LUC
from tram.api.app import tao_app
from tram.cau_hinh.usage import CauHinhUsage
from tram.phieu.cau_dao import ngat_cau_dao
from tram.phieu.khe import dang_ky_khe, khe_dang_bat
from tram.phieu.kho import KhoPhieu
from tram.usage.ccusage import KetQuaCcusage

KHE = [{"ten": "claude-1", "cli": "claude", "ten_goi_nho": "Claude tài khoản 1", "vai_uu_tien": ["coder"]}]
URL = "/api/khe/B/claude-1"


def _app(tmp_path, *, kho_phieu=True, **kw):
    db = tmp_path / "sk.db"
    kho = KhoPhieu(db)
    with kho.giao_dich():
        dang_ky_khe(kho, "B", KHE, luc=LUC)
        kho.ghi_su_kien("hr-codex", "chay.xong", {"khe_id": "B/claude-1"}, luc=LUC, bead_id="hr-1", token_vao=10,
                        token_ra=5, mo_hinh="m")
    kho.close()
    pt = replace(tao_pt(tmp_path, {}), mo_kho_phieu=(lambda: KhoPhieu(db)) if kho_phieu else None,
                 dong_ho=lambda: LUC, **kw)
    return tao_app(pt)


def _than(**kw):
    return {"ma_thao_tac": kw.pop("ma", "ma-khe-0001"), "expected_version": kw.pop("v", ""), **kw}


def test_doi_ngu_doc_khong_can_danh_tinh_va_tat_khi_chua_co_kho_phieu(tmp_path):
    r = goi(_app(tmp_path), "GET", "/api/doi-ngu")
    assert r.status == 200 and r.json()["bat"] is True and r.json()["khe"][0]["ten_goi_nho"] == "Claude tài khoản 1"
    (tmp_path / "x").mkdir()
    assert goi(_app(tmp_path / "x", kho_phieu=False), "GET", "/api/doi-ngu").json() == {
        "bat": False, "khe": [], "luat_vai": None, "bang_diem": []}


def test_tat_bat_khe_qua_api_can_dai_ca_va_idempotent(tmp_path):
    app = _app(tmp_path)
    assert goi(app, "POST", f"{URL}/tat", json_body=_than()).status == 403
    assert goi(app, "POST", f"{URL}/tat", json_body=_than(),
               headers={"Authorization": "Bearer tok-may", "X-Tram": "1"}).status == 403
    r1 = goi(app, "POST", f"{URL}/tat", json_body=_than(vi_sao="để dành"), headers=DAI_CA)
    r2 = goi(app, "POST", f"{URL}/tat", json_body=_than(vi_sao="để dành"), headers=DAI_CA)
    assert (r1.status, r1.json()["lap_lai"], r2.json()["lap_lai"]) == (200, False, True)
    assert not khe_dang_bat(KhoPhieu(tmp_path / "sk.db"), "B/claude-1")
    assert goi(app, "POST", f"{URL}/bat", json_body=_than(ma="ma-bat-0001", v="0:0"), headers=DAI_CA).status == 409
    v = goi(app, "GET", "/api/doi-ngu").json()["khe"][0]["phien_ban"]
    assert goi(app, "POST", f"{URL}/bat", json_body=_than(ma="ma-bat-0002", v=v), headers=DAI_CA).status == 200


def test_cau_dao_dong_va_loi(tmp_path):
    app = _app(tmp_path)
    v = goi(app, "GET", "/api/doi-ngu").json()["khe"][0]["phien_ban"]
    assert goi(app, "POST", f"{URL}/cau-dao-dong", json_body=_than(v=v), headers=DAI_CA).status == 409
    kho = KhoPhieu(tmp_path / "sk.db")
    with kho.giao_dich():
        ngat_cau_dao(kho, "B/claude-1", ly_do="het-han-muc", toi_luc=LUC + timedelta(hours=1), luc=LUC)
    v = goi(app, "GET", "/api/doi-ngu").json()["khe"][0]["phien_ban"]
    assert goi(app, "POST", f"{URL}/cau-dao-dong", json_body=_than(ma="ma-dao-0002", v=v), headers=DAI_CA).status == 200
    assert goi(app, "GET", "/api/doi-ngu").json()["khe"][0]["cau_dao"]["ngat"] is False
    assert goi(app, "POST", "/api/khe/B/claude-9/tat", json_body=_than(ma="ma-tat-0009"), headers=DAI_CA).status == 404
    assert goi(app, "POST", "/api/khe/B/Claude_1/tat", json_body=_than(ma="ma-tat-0010"), headers=DAI_CA).status == 422
    assert goi(app, "POST", f"{URL}/tat", json_body=_than(ma="ma-tat-0011", la=1), headers=DAI_CA).status == 422
    assert goi(app, "POST", f"{URL}/tat", json_body=_than(ma="ma-tat-0012", vi_sao="x" * 501),
               headers=DAI_CA).status == 422
    (tmp_path / "y").mkdir()
    assert goi(_app(tmp_path / "y", kho_phieu=False), "POST", f"{URL}/tat", json_body=_than(),
               headers=DAI_CA).status == 501


def test_usage_tu_su_kien_va_ccusage(tmp_path):
    goi_cc = []

    def cc(tu, den):
        goi_cc.append((tu.isoformat(), den.isoformat()))
        return KetQuaCcusage("ok", ({"ngay": "2026-10-13", "token_vao": 1, "token_ra": 2, "token_cache_doc": 0,
                                     "token_cache_ghi": 0, "chi_phi_usd": 0.5},), phien_ban="17.2.1")
    app = _app(tmp_path, usage=CauHinhUsage(gia={"m": {"vao": 1e6, "ra": 0, "cache_doc": 0, "cache_ghi": 0}}),
               doc_ccusage=cc)
    r = goi(app, "GET", "/api/usage?so_ngay=7").json()
    assert (r["tu"], r["den"], r["co_bang_gia"]) == ("2026-10-07", "2026-10-13", True)
    assert r["theo_nguon"] == [{"khoa": "B/claude-1", "token_vao": 10, "token_ra": 5, "token_cache_doc": 0,
                                "token_cache_ghi": 0, "so_lan": 1, "chi_phi_usd": 10.0, "thieu_gia": 0}]
    assert r["ccusage"]["trang_thai"] == "ok" and r["ccusage"]["theo_ngay"][0]["chi_phi_usd"] == 0.5
    assert goi_cc == [("2026-10-07", "2026-10-13")]
    assert goi(app, "GET", "/api/usage?so_ngay=93").status == 422
    (tmp_path / "z").mkdir()
    r = goi(_app(tmp_path / "z"), "GET", "/api/usage").json()
    assert r["ccusage"] == {"trang_thai": "chua_cau_hinh", "theo_ngay": [], "loi": None, "phien_ban": None}
    assert r["co_bang_gia"] is False and r["theo_ngay"][0]["chi_phi_usd"] is None


def test_phu_thuoc_that_khong_chay_ccusage_luc_khoi_dong(monkeypatch, tram_home_tam):
    import subprocess
    from tram.api.phu_thuoc import phu_thuoc_that
    goi_that = []
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: goi_that.append(a))
    assert phu_thuoc_that().doc_ccusage is None
    tram_home_tam.mkdir(parents=True, exist_ok=True)
    (tram_home_tam / "cau-hinh.yaml").write_text("usage: {ccusage: /x/ccusage, ccusage_phien_ban: '17.2.1'}\n")
    assert callable(phu_thuoc_that().doc_ccusage) and goi_that == []
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_api_doi_ngu.py -q`
Expected: FAIL — `5 failed` (`assert (404 == 200)` — chưa có route; `AttributeError: … 'doc_ccusage'`)

- [ ] **Step 3: Viết mã**

`tram/api/doi_ngu.py` (mới):

```python
"""Lát 2b (spec 2 §5.4, §7): `GET /api/doi-ngu`; `POST /api/khe/{may_id}/{ten}/tat|bat|cau-dao-dong` với
`khe_id = <may_id>/<ten>` (spec 3 §4 — URL đúng dạng `/api/khe/B/claude-1/tat`). POST cần danh tính Đại ca +
CSRF như mọi API ghi (spec 2 §4) và `ma_thao_tac` + `expected_version` (§12.3); Bearer token máy thợ không mở
được nhóm này (spec 3 §5.1)."""
import re
from collections.abc import Callable
from contextlib import closing

from fastapi import APIRouter, Depends, Request
from pydantic import Field

from tram.api.bao_mat import yeu_cau_ghi
from tram.api.than import ThanGhi
from tram.phieu.khe import KheLa
from tram.suy.doi_ngu import doi_ngu
from tram.thao_tac.khe import bat_khe_thao_tac, dong_cau_dao_thao_tac, tat_khe_thao_tac
from tram.thao_tac.loi import ChuaHoTro, KhongHopLe, KhongThay

KHE_RE = re.compile(r"[A-Za-z0-9-]{1,32}/[a-z0-9-]{1,32}")
router = APIRouter()


class ThanKhe(ThanGhi):
    vi_sao: str | None = Field(default=None, max_length=500)


@router.get("/api/doi-ngu")
def r_doi_ngu(request: Request) -> dict:
    pt = request.app.state.pt
    if pt.mo_kho_phieu is None:
        return {"bat": False, "khe": [], "luat_vai": None, "bang_diem": []}
    with closing(pt.mo_kho_phieu()) as kho:
        return doi_ngu(kho, bay_gio=pt.dong_ho(), ch=pt.cau_hinh)


def _ghi(request: Request, may_id: str, ten: str, lam: Callable) -> dict:
    pt, khe_id = request.app.state.pt, f"{may_id}/{ten}"
    if not KHE_RE.fullmatch(khe_id):
        raise KhongHopLe("Mã khe không hợp lệ")
    if pt.mo_kho_phieu is None:
        raise ChuaHoTro("Kho phiếu chưa bật (phần 3)")
    try:
        with closing(pt.mo_kho_phieu()) as kho, closing(pt.mo_kho_tt()) as kho_tt:
            kq = lam(kho, kho_tt, khe_id, pt.dong_ho())
    except KheLa as e:                                   # khe bị gỡ giữa lúc kiểm và lúc ghi
        raise KhongThay(str(e)) from None
    return {"ket_qua": kq.ket_qua, "lap_lai": kq.lap_lai}


@router.post("/api/khe/{may_id}/{ten}/tat", dependencies=[Depends(yeu_cau_ghi)])
def r_tat(may_id: str, ten: str, than: ThanKhe, request: Request) -> dict:
    return _ghi(request, may_id, ten, lambda kho, kt, khe_id, luc: tat_khe_thao_tac(
        kho, kt, khe_id, vi_sao=than.vi_sao, ma=than.ma_thao_tac, expected_version=than.expected_version, luc=luc))


@router.post("/api/khe/{may_id}/{ten}/bat", dependencies=[Depends(yeu_cau_ghi)])
def r_bat(may_id: str, ten: str, than: ThanKhe, request: Request) -> dict:
    return _ghi(request, may_id, ten, lambda kho, kt, khe_id, luc: bat_khe_thao_tac(
        kho, kt, khe_id, vi_sao=than.vi_sao, ma=than.ma_thao_tac, expected_version=than.expected_version, luc=luc))


@router.post("/api/khe/{may_id}/{ten}/cau-dao-dong", dependencies=[Depends(yeu_cau_ghi)])
def r_cau_dao_dong(may_id: str, ten: str, than: ThanGhi, request: Request) -> dict:
    return _ghi(request, may_id, ten, lambda kho, kt, khe_id, luc: dong_cau_dao_thao_tac(
        kho, kt, khe_id, ma=than.ma_thao_tac, expected_version=than.expected_version, luc=luc))
```

`tram/api/usage.py` (mới):

```python
"""`GET /api/usage?so_ngay=14` (spec 2 §5.4, §7): token + chi phí theo ngày / tuần / khe / dự án từ sự kiện của
trạm, và theo ngày từ `ccusage --json` (toàn bộ Claude Code của tài khoản trạm trên máy B — CHỜ CHẠY THẬT,
plan 2b G6). Chỉ đọc; không nội dung nghiệp vụ."""
from contextlib import closing
from dataclasses import asdict
from datetime import timedelta

from fastapi import APIRouter, Request

from tram.cham_cot.ghi import GIO_VN
from tram.thao_tac.loi import KhongHopLe
from tram.usage.ccusage import KetQuaCcusage
from tram.usage.su_kien import doc_dong_usage, tong_hop

router = APIRouter()
SO_NGAY_TOI_DA = 92


@router.get("/api/usage")
def r_usage(request: Request, so_ngay: int = 14) -> dict:
    if not 1 <= so_ngay <= SO_NGAY_TOI_DA:
        raise KhongHopLe(f"so_ngay phải trong 1–{SO_NGAY_TOI_DA}")
    pt = request.app.state.pt
    den = pt.dong_ho().astimezone(GIO_VN).date()
    tu = den - timedelta(days=so_ngay - 1)
    dong = []
    if pt.mo_kho_phieu is not None:
        with closing(pt.mo_kho_phieu()) as kho:
            dong = doc_dong_usage(kho.db, tu, den)
    cc = pt.doc_ccusage(tu, den) if pt.doc_ccusage is not None else KetQuaCcusage("chua_cau_hinh")
    return {"tu": tu.isoformat(), "den": den.isoformat(), **tong_hop(dong, pt.usage.gia),
            "co_bang_gia": bool(pt.usage.gia), "ccusage": {**asdict(cc), "theo_ngay": list(cc.theo_ngay)}}
```

`tram/api/app.py` (sửa — bản vá):

```diff
diff --git a/tram/api/app.py b/tram/api/app.py
index bf3103e..04a4a3a 100644
--- a/tram/api/app.py
+++ b/tram/api/app.py
@@ -3,7 +3,7 @@ from fastapi import FastAPI, Request
 from fastapi.responses import JSONResponse
 from fastapi.staticfiles import StaticFiles
 
-from tram.api import luong, noi_bo, tho, tuyen_chu, tuyen_doc, tuyen_ghi, tuyen_nho
+from tram.api import doi_ngu, luong, noi_bo, tho, tuyen_chu, tuyen_doc, tuyen_ghi, tuyen_nho, usage
 from tram.api.bao_mat import them_header_an_toan
 from tram.api.phu_thuoc import PhuThuocApi
 from tram.beads.bd import KhongThayBead, LoiBd
@@ -11,8 +11,9 @@ from tram.suy.lam_sach import lam_sach
 from tram.thao_tac.loi import ChuaHoTro, KhongHopLe, KhongThay, XungDot
 
 MA_LOI = {XungDot: 409, KhongHopLe: 422, ChuaHoTro: 501, KhongThay: 404, KhongThayBead: 404, LoiBd: 502,
           LoiNhoKhach: 503}
-CAC_TUYEN = (tuyen_doc.router, tuyen_ghi.router, tuyen_chu.router, tuyen_nho.router, luong.router, tho.router, noi_bo.router)
+CAC_TUYEN = (tuyen_doc.router, tuyen_ghi.router, tuyen_chu.router, tuyen_nho.router, luong.router, tho.router, noi_bo.router,
+             doi_ngu.router, usage.router)
 
 
 def _xu_ly(ma: int):
```

`tram/api/phu_thuoc.py` (sửa — bản vá):

```diff
diff --git a/tram/api/phu_thuoc.py b/tram/api/phu_thuoc.py
index 8309c4f..a711493 100644
--- a/tram/api/phu_thuoc.py
+++ b/tram/api/phu_thuoc.py
@@ -1,14 +1,15 @@
 """Phụ thuộc của tram-api gom một chỗ — test thay bằng bản giả (tests/api_gia.py)."""
 import re
 from collections.abc import Callable
-from dataclasses import dataclass
+from dataclasses import dataclass, field
 from datetime import datetime, timezone
 from pathlib import Path
 
 from tram.api.bo_dem import BoDemBeads
 from tram.api.khach_nho import KhachNho
 from tram.beads.bd import Bd
 from tram.cau_hinh.tram import CauHinhTram
+from tram.cau_hinh.usage import CauHinhUsage
 from tram.su_kien.kho import KhoSuKien
 from tram.thao_tac.chung import TAC_NHAN
 from tram.thao_tac.kho import KhoThaoTac
@@ -29,7 +30,9 @@ class PhuThuocApi:
     chon_phieu: Callable | None = None                   # phần 4 `chon_phieu(khe_id, han_muc)`; None: không phát phiếu
     doc_token_noi_bo: Callable[[], str | None] = lambda: None
     dong_ho: Callable[[], datetime] = lambda: datetime.now(timezone.utc)
     nho: KhachNho | None = None          # lát 1b-3: memory service (None → /api/nho/* trả 503)
+    usage: CauHinhUsage = field(default_factory=CauHinhUsage)   # 2b: khoá `usage:` (bảng giá, ccusage)
+    doc_ccusage: Callable | None = None                         # 2b: `(tu, den) -> KetQuaCcusage`; None: chưa cấu hình
 
 
 def kiem_du_an_bead(pt: PhuThuocApi, du_an: str, bead_id: str | None = None) -> None:
@@ -43,18 +46,23 @@ def phu_thuoc_that() -> PhuThuocApi:
     from tram.api.noi_bo import doc_mot_lan
     from tram.cau_hinh.du_an import liet_ke_du_an, nap_du_an
     from tram.cau_hinh.tram import nap_cau_hinh_tram
+    from tram.cau_hinh.usage import nap_cau_hinh_usage
     from tram.duong_dan import goc_repo
     from tram.phieu.kho import mo_kho_phieu
     from tram.su_kien.kho import mo_kho
     from tram.thao_tac.kho import mo_kho_thao_tac
+    from tram.usage.bo_dem import BoDemCcusage
+    from tram.usage.ccusage import DocCcusage
 
     def tao_bd(ten: str) -> Bd:
         return Bd(nap_du_an(ten).duong_dan, actor=TAC_NHAN)
 
     dist = goc_repo() / "frontend" / "dist"
+    cu = nap_cau_hinh_usage()
+    doc_cc = BoDemCcusage(DocCcusage(cu.ccusage, cu.ccusage_phien_ban).theo_ngay).lay if cu.ccusage else None
     return PhuThuocApi(
         cau_hinh=nap_cau_hinh_tram(),
         cac_du_an=lambda: [t for t in liet_ke_du_an() if not t.startswith("_")],
         tao_bd=tao_bd, bo_dem=BoDemBeads(tao_bd), mo_kho=mo_kho, mo_kho_tt=mo_kho_thao_tac,
         thu_muc_tinh=dist if dist.is_dir() else None, mo_kho_phieu=mo_kho_phieu, doc_token_noi_bo=doc_mot_lan(),
-        nho=KhachNho())
+        nho=KhachNho(), usage=cu, doc_ccusage=doc_cc)
```

Áp bản vá: `git apply --check <file> && git apply <file>` (G2 nếu 1b-3 đã thêm router/trường).

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_api_doi_ngu.py tests/test_api_tho.py tests/test_api_doc.py tests/test_api_ghi.py tests/test_api_nho.py -q`
Expected: tất cả pass (`test_api_doi_ngu.py`: `5 passed`)

Run: `uv run pytest -q`
Expected: `N₀ + 44 passed` (1059 — trên `main` sau đợt 2 + riêng task này)

- [ ] **Step 5: Commit**

```bash
git add tram/api/doi_ngu.py tram/api/usage.py tram/api/app.py tram/api/phu_thuoc.py tests/test_api_doi_ngu.py
git commit -m "feat(api): /api/doi-ngu, /api/khe/{id}/tat|bat|cau-dao-dong, /api/usage (spec 2 §7 lát 2b; plan 2b G4–G8, G16, G17)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 12: Frontend — trang Usage

**Độ khó:** `de` · **Đợt:** 3 · **Song song với:** Task 11 (chỉ đụng `frontend/`) · **Phải xong trước:** Task 7, 10

**Files:**
- Create: `frontend/src/thanh/BangUsage.vue`
- Create: `frontend/src/trang/Usage.vue`
- Modify: `frontend/src/tuyen.js`, `frontend/src/KhungChinh.vue` (sau Task 10)

**Interfaces:**
- Consumes: "Hợp đồng JSON" (`GET /api/usage`); `dinhDangSo`, `dinhDangUsd`, `tenNguon` (Task 7); `kho.phienBanDoiNgu` (Task 10).
- Produces: route `/usage`, mục menu "Usage"; `BangUsage` (props `tieuDe`, `tenKhoa`, `dong`, `laNguon`, `coSoLan`).

- [ ] **Step 1: Chạy kiểm hiện tại (mốc)**

Run: `cd frontend && npm run kiem && npm run build`
Expected: `ℹ tests 13` · `ℹ fail 0`; `✓ built in …`

- [ ] **Step 2: Viết component mới**

`frontend/src/thanh/BangUsage.vue` (mới):

```vue
<script setup>
import { dinhDangSo, dinhDangUsd, tenNguon } from '../luat_doi_ngu.js'

defineProps({
  tieuDe: { type: String, default: '' },
  tenKhoa: { type: String, required: true },
  dong: { type: Array, required: true },          // [{khoa, token_vao, token_ra, token_cache_doc, token_cache_ghi, so_lan?, chi_phi_usd, thieu_gia?}]
  laNguon: { type: Boolean, default: false },
  coSoLan: { type: Boolean, default: true },
})
</script>

<template>
  <section class="bang-usage">
    <h2 v-if="tieuDe">{{ tieuDe }}</h2>
    <p v-if="!dong.length" class="nho">Không có số liệu trong khoảng này.</p>
    <div v-else class="bang-cuon">
      <table>
        <thead><tr>
          <th scope="col">{{ tenKhoa }}</th><th scope="col">Token vào</th><th scope="col">Token ra</th>
          <th scope="col">Cache đọc</th><th scope="col">Cache ghi</th><th v-if="coSoLan" scope="col">Số lần gọi</th>
          <th scope="col">Chi phí</th>
        </tr></thead>
        <tbody><tr v-for="d in dong" :key="d.khoa">
          <th scope="row">{{ laNguon ? tenNguon(d.khoa) : d.khoa }}</th>
          <td>{{ dinhDangSo(d.token_vao) }}</td><td>{{ dinhDangSo(d.token_ra) }}</td>
          <td>{{ dinhDangSo(d.token_cache_doc) }}</td><td>{{ dinhDangSo(d.token_cache_ghi) }}</td>
          <td v-if="coSoLan">{{ dinhDangSo(d.so_lan) }}</td>
          <td>{{ dinhDangUsd(d.chi_phi_usd) }}<span v-if="d.thieu_gia && d.chi_phi_usd != null" class="nho">
            · {{ d.thieu_gia }} lần thiếu giá</span></td>
        </tr></tbody>
      </table>
    </div>
  </section>
</template>

<style scoped>
.bang-usage { margin-bottom: 1.25rem; }
</style>
```

`frontend/src/trang/Usage.vue` (mới):

```vue
<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { doc } from '../api.js'
import { kho } from '../kho.js'
import BangUsage from '../thanh/BangUsage.vue'

const SO_NGAY = [7, 14, 30, 92]
const soNgay = ref(14)
const dl = ref(null)
const loi = ref('')
const ccusage = computed(() => (dl.value ? dl.value.ccusage.theo_ngay.map((d) => ({ ...d, khoa: d.ngay })) : []))

async function tai() {
  try {
    dl.value = await doc(`/api/usage?so_ngay=${soNgay.value}`)
    loi.value = ''
  } catch (e) {
    loi.value = e.message
  }
}
onMounted(tai)
watch(soNgay, tai)
watch(() => kho.phienBanDoiNgu, tai)
</script>

<template>
  <section>
    <h1>Usage</h1>
    <div class="cong-cu">
      <label>Khoảng
        <select v-model.number="soNgay">
          <option v-for="n in SO_NGAY" :key="n" :value="n">{{ n }} ngày gần nhất</option>
        </select>
      </label>
    </div>
    <p v-if="loi" class="loi" role="alert">{{ loi }}</p>
    <template v-if="dl">
      <p class="nho">Từ {{ dl.tu }} đến {{ dl.den }} (ngày theo giờ Việt Nam). Nguồn: sự kiện của trạm — mỗi lần
        chạy CLI của khe và mỗi lần bộ chấm cột gọi Claude API. Chi phí của khe (gói thuê bao) là giá tương đương theo
        bảng giá, không phải tiền trả thêm.
        <template v-if="!dl.co_bang_gia"> Chưa có bảng giá (<code>usage.gia_usd_moi_trieu_token</code>) — chi phí để
          trống.</template></p>
      <BangUsage tieu-de="Theo ngày" ten-khoa="Ngày" :dong="dl.theo_ngay" />
      <BangUsage tieu-de="Theo tuần" ten-khoa="Tuần (ISO)" :dong="dl.theo_tuan" />
      <BangUsage tieu-de="Theo khe" ten-khoa="Khe / nguồn" :dong="dl.theo_nguon" la-nguon />
      <BangUsage tieu-de="Theo dự án" ten-khoa="Dự án" :dong="dl.theo_du_an" />
      <h2>ccusage — toàn bộ Claude Code của tài khoản trạm trên máy B</h2>
      <p v-if="dl.ccusage.trang_thai === 'chua_cau_hinh'" class="nho">Chưa cấu hình ccusage
        (<code>usage.ccusage</code> trong <code>~/.tram/cau-hinh.yaml</code>).</p>
      <p v-else-if="dl.ccusage.trang_thai === 'loi'" class="loi">{{ dl.ccusage.loi }}</p>
      <template v-else>
        <p class="nho">ccusage {{ dl.ccusage.phien_ban }} — số liệu giữ tối đa 10 phút.</p>
        <BangUsage ten-khoa="Ngày" :dong="ccusage" :co-so-lan="false" />
      </template>
    </template>
  </section>
</template>
```

- [ ] **Step 3: Nối route + menu (bản vá)**

`frontend/src/tuyen.js`:

```diff
diff --git a/frontend/src/tuyen.js b/frontend/src/tuyen.js
index 2c5a1ab..c057a61 100644
--- a/frontend/src/tuyen.js
+++ b/frontend/src/tuyen.js
@@ -2,7 +2,8 @@ import CongViec from './trang/CongViec.vue'
 import DoiNgu from './trang/DoiNgu.vue'
 import DuAn from './trang/DuAn.vue'
 import KyUc from './trang/KyUc.vue'
 import PheDuyet from './trang/PheDuyet.vue'
+import Usage from './trang/Usage.vue'
 
 export const tuyen = [
   { path: '/', redirect: '/cong-viec' },
@@ -9,5 +10,6 @@ export const tuyen = [
   { path: '/du-an', component: DuAn },
   { path: '/phe-duyet', component: PheDuyet },
   { path: '/nho', component: KyUc },
   { path: '/doi-ngu', component: DoiNgu },
+  { path: '/usage', component: Usage },
 ]
```

`frontend/src/KhungChinh.vue`:

```diff
diff --git a/frontend/src/KhungChinh.vue b/frontend/src/KhungChinh.vue
index 764a83a..3c295bf 100644
--- a/frontend/src/KhungChinh.vue
+++ b/frontend/src/KhungChinh.vue
@@ -15,7 +15,8 @@ onMounted(() => { taiTrangThai(); taiSoPheDuyet(); moLuong() })
         <span v-if="kho.soPheDuyet" class="dem" :aria-label="kho.soPheDuyet + ' việc chờ'">{{ kho.soPheDuyet }}</span>
       </router-link>
       <router-link to="/nho">Ký ức</router-link>
       <router-link to="/doi-ngu">Đội ngũ AI</router-link>
+      <router-link to="/usage">Usage</router-link>
     </nav>
     <ThanhTrangThai />
   </header>
```

Áp bản vá: `git apply --check <file> && git apply <file>`.

- [ ] **Step 4: Chạy kiểm**

Run: `cd frontend && npm run kiem`
Expected: `ℹ tests 13` · `ℹ fail 0`; `kiem-an-toan: … không có chèn HTML thô`

Run: `cd frontend && npm run build`
Expected: `✓ built in …`

Run: `uv run pytest -q`
Expected: `N₀ + 39 passed` (1054 — task này không đụng Python)

- [ ] **Step 5: Commit**

```bash
git add frontend/src/thanh/BangUsage.vue frontend/src/trang/Usage.vue frontend/src/tuyen.js frontend/src/KhungChinh.vue
git commit -m "feat(frontend): trang Usage — token + chi phí theo ngày/tuần/khe/dự án, số liệu ccusage (spec 2 §5.4)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

## Hợp nhất bắt buộc với 1b-3 / 4a-1

| File | Trạng thái sau 2b phải giữ |
|---|---|
| `tram/api/app.py` | Router `tho`, `noi_bo` của 3a-1; `tuyen_nho` và `LoiNhoKhach: 503` của 1b-3; thêm `doi_ngu`, `usage`. Không thay toàn tuple bằng bản chỉ có router 2b. |
| `tram/api/phu_thuoc.py` | `KhachNho`, trường `nho`, `nho=KhachNho()`; toàn bộ trường worker 3a-1; thêm `usage`, `doc_ccusage`. 4a-1 ghép sau phải giữ cả ba nhóm. |
| `frontend/src/kho.js` | `laSuKienNho`, `phienBanNho` và listener memory còn nguyên; thêm `phienBanDoiNgu`. |
| `frontend/src/tuyen.js`, `KhungChinh.vue` | Giữ `/nho`/Ký ức; thêm `/doi-ngu` ở T10 rồi `/usage` ở T12. |
| `tram/phieu/khe.py`, `cau_dao.py` | 2b chỉ mở rộng metadata `them`, không thay thẻ chắn/thu hồi của 3a-1. 4a-1 dùng đường ghi này. |

Mã test cũ trong các khối là cơ sở TDD; test API T11 phải chạy cả `tests/test_api_nho.py` từ 1b-3. Sau ghép, `/api/nho/*` còn hoạt động, `/api/tho/*` và `/api/noi-bo/*` còn router, cả hai listener memory/đội ngũ còn tồn tại. Kiểm build không thay kiểm runtime trình duyệt. **Không coi số 1015/1059/13 là mốc sau 1b-3:** tất cả là số lịch sử trước khi ghép 1b-3; dùng `N₀`, `M₀` đo ở đầu lát. Bộ assertion hồi quy mở rộng ở T4/T8 không tạo test case mới.

## Sơ đồ đợt chạy

Số test dưới đây là kết quả **chạy thật** trên bản dựng thử (Tự review mục 4), với N₀ = 1015, M₀ = 7 (chưa có 1b-3). Ngoặc sau tên task: task phải ghép trước.

```
Đợt 0 — main (sau 3a-1 + 1b-3) → N₀ passed (1015) · node M₀ (7)

Đợt 1 — song song, 7 worktree từ main
  T1 đường ghi khe + phien_ban_khe · T2 cấu hình usage · T3 usage từ sự kiện · T4 adapter ccusage
  T5 Hệ cần xem cầu dao + SSE · T6 Telegram khe · T7 luật frontend
  → N₀ + 32 = 1047 passed (+ 2 + 14 + 3 + 7 + 3 + 3) · node M₀ + 6 = 13

Đợt 2 — song song, 3 worktree từ main sau đợt 1
  T8 thao tác khe (1) · T9 suy Đội ngũ + bảng điểm (1) · T10 trang Đội ngũ AI (7)
  → N₀ + 39 = 1054 passed (+ 4 + 3) · node 13 · build xanh

Đợt 3 — song song, 2 worktree từ main sau đợt 2
  T11 API doi-ngu/khe/usage (2, 3, 4, 8, 9) · T12 trang Usage (7, 10)
  → N₀ + 44 = 1059 passed (+ 5) · node 13 · build xanh
```

| Task | Độ khó | Đợt | Phải xong trước | File chạm (ngoài test) | Test mới | Toàn bộ sau task (trên main đợt trước) |
|---|---|---|---|---|---|---|
| 1 | de | 1 | — | `tram/phieu/khe.py`, `tram/phieu/cau_dao.py` | 2 | N₀ + 2 (1017) |
| 2 | de | 1 | — | `tram/cau_hinh/usage.py` | 14 | N₀ + 14 (1029) |
| 3 | de | 1 | — | `tram/usage/__init__.py`, `tram/usage/su_kien.py` | 3 | N₀ + 3 (1018) |
| 4 | de | 1 | — | `tram/usage/__init__.py`, `tram/usage/ccusage.py`, `tram/usage/bo_dem.py` | 7 | N₀ + 7 (1022) |
| 5 | de | 1 | — | `tram/suy/phe_duyet_khe.py`, `tram/suy/phe_duyet.py`, `tram/api/tuyen_doc.py`, `tram/api/luong.py` | 3 | N₀ + 3 (1018) |
| 6 | de | 1 | — | `tram/bao_tin/tin.py`, `tram/bao_tin/nguon.py` | 3 | N₀ + 3 (1018) |
| 7 | de | 1 | — | `frontend/src/luat_doi_ngu.js` | 6 (node) | node M₀ + 6 (13) |
| 8 | de | 2 | 1 | `tram/thao_tac/khe.py` | 4 | N₀ + 36 (1051) |
| 9 | de | 2 | 1 | `tram/suy/bang_diem.py`, `tram/suy/doi_ngu.py` | 3 | N₀ + 35 (1050) |
| 10 | de | 2 | 7 | `frontend/src/thanh/HopKhe.vue`, `TheKhe.vue`, `trang/DoiNgu.vue`; sửa `kho.js`, `tuyen.js`, `KhungChinh.vue`, `trang/PheDuyet.vue`, `thanh/MucPheDuyet.vue` | — (build) | node 13 |
| 11 | de | 3 | 2, 3, 4, 8, 9 | `tram/api/doi_ngu.py`, `tram/api/usage.py`, `tram/api/app.py`, `tram/api/phu_thuoc.py` | 5 | N₀ + 44 (1059) |
| 12 | de | 3 | 7, 10 | `frontend/src/thanh/BangUsage.vue`, `trang/Usage.vue`; sửa `tuyen.js`, `KhungChinh.vue` | — (build) | node 13 |

**Tổng cuối:** `uv run pytest -q` = **N₀ + 44** (1059 khi 1b-3 không thêm test); `npm run kiem` = **M₀ + 6** (13); `npm run build` xanh.

File dùng chung giữa các đợt (đúng một task sở hữu mỗi lần sửa): `frontend/src/tuyen.js`, `frontend/src/KhungChinh.vue` — Task 10 (đợt 2) rồi Task 12 (đợt 3). File giống hệt từng byte do hai task cùng đợt tạo: `tram/usage/__init__.py` (3, 4). Không file nào bị hai task cùng đợt sửa khác nhau. **Đụng chung với plan khác:** 3a-1 — `tram/phieu/khe.py`, `tram/phieu/cau_dao.py` (Task 1: chỉ thêm tham số có mặc định + một hàm), `tram/api/app.py`, `tram/api/phu_thuoc.py` (Task 11: thêm router, hai trường có mặc định); 2a — `tram/suy/phe_duyet.py`, `tram/api/tuyen_doc.py`, `tram/api/luong.py`, `tram/bao_tin/*`, `frontend/src/*`; 1b-3 Task 9–10 — giữ API/trường dependency/frontend Ký ức theo G2.

## Để sau (chờ cổng / chờ chạy thật) — không lập task code ở plan này

Không đánh dấu lát 2b sẵn sàng triển khai cho tới khi các mục "chờ chạy thật" dưới đây đã làm.

| Phần | Spec | Chờ | Đã chừa sẵn |
|---|---|---|---|
| **Cài và chạy ccusage thật**: chọn phiên bản (bản mới nhất đã phát hành ≥ 2 tuần), `npm install --prefix ~/.tram/ccusage --save-exact --ignore-scripts ccusage@<x.y.z>` dưới tài khoản trạm, ghi `usage.ccusage` + `usage.ccusage_phien_ban`; kiểm thật: `--version` in đúng số, cờ `daily --json --offline --since/--until` tồn tại, dạng JSON khớp `doc_json_ccusage`, `TZ=Asia/Ho_Chi_Minh` làm ccusage chia ngày theo giờ VN, thời gian chạy < 60 s; sai chỗ nào → sửa adapter (một file) + fixture test theo transcript thật | spec 2 §8, §5.4 | **chờ chạy thật** (Đại ca cho phép cài; cần mạng một lần) | `DocCcusage`, `doc_json_ccusage`, `BoDemCcusage`, khoá `usage:`, `/api/usage` trả `chua_cau_hinh`/`loi` rõ ràng |
| ccusage **theo khe** (chạy với `CLAUDE_CONFIG_DIR` của từng khe để có chi phí thật theo khe) | spec 2 §5.4 | **S6** (tài khoản trạm có được đọc thư mục cấu hình thuộc principal của khe không — cách ly §7.3) + S3 | Usage theo khe hiện tính từ `chay.xong` + bảng giá (G7, G8) |
| Hạn mức thật trên thẻ khe (bộ đọc `rate_limit_event`, nghĩa `utilization`) | spec 3 §8.1 | **S1** (#5 chưa duyệt) — 3a-2 | `muc_han_muc`, `moTaCuaSo` dùng mô hình `HanMuc` của 3a-1; cửa sổ chưa biết hiện "chưa biết" |
| Bảng điểm: **qua lần đầu**, **bị trả về** | spec 2 §5.4, spec 4 §12 | **phần 4** (spec 4 chưa duyệt; cần `kiem.lai`, `qc.ket_qua`, `bead.vao_cot_3`) | `bang_diem` trả `null`, trang ghi "chờ phần 4" (G9) |
| Đường proxy xác thực thay header danh tính cho API ghi (gồm `/api/khe/*`) | spec 2 §4 mục 2b | **S6** — 3a-2 | Router 2b dùng `yeu_cau_ghi` chung (G17) |
| Kiểm tay giao diện Đội ngũ AI + Usage trên máy A và điện thoại, qua tailnet | spec 2 §9 mục 3–4 | **#5** (Tailscale chưa duyệt) | trang chạy được qua `127.0.0.1:7700` + `vite` proxy |
| Có khe thật để thấy dữ liệu (thẻ khe, bảng điểm, Usage theo khe) | — | 3a-2 (thợ thật) + phần 4 (`chon_phieu`) | 3a-1 đã có `/api/tho/dang-ky`, `tram tho tat-khe/bat-khe`; 2b đọc đúng các sự kiện đó |

> **Ghi chú 15/10/2026** (không đổi bảng trên): Tailscale máy B đã đăng nhập, nên hàng "Kiểm tay ... qua tailnet" không còn chờ #5. Hàng này giờ chờ 2a Task 26 (`vn.tram.api` chưa cài, `tailscale serve` chưa làm); bead `bs-8eh.16`. Hàng S1 vẫn đúng: S1 **chưa duyệt**. ccusage chưa cài trên máy B (kiểm 15/10); bead `bs-8eh.13`. Phần #5 còn chờ xem [quyết định 13/10, mục "Ghi chú 15/10"](../quyet-dinh/2026-10-13-tra-loi-cau-hoi-gop.md).

## Tự review

**1. Độ phủ spec (phần của lát 2b)**

| Yêu cầu | Task | Kiểm bằng |
|---|---|---|
| §5.4 thẻ khe: máy, CLI, tên gợi nhớ (không email), vai ưu tiên, trạng thái (đang làm `<bead>` / rảnh / tắt / cầu dao ngắt / mất kết nối), hạn mức còn lại + giờ reset, số phiên | 9, 7, 10, 11 | `test_doi_ngu_the_khe_ten_goi_nho_khong_email_va_phien_ban` (email bị thay bằng `khe_id`, `ma_giao` không lộ), `test_muc_han_muc_theo_luat_nhan_viec`, node: `nhãn trạng thái…`, `mô tả cửa sổ hạn mức…`; `TheKhe.vue` |
| §5.4 bật/tắt khe → `khe.bat`/`khe.tat`, phần 4 tôn trọng | 1, 8, 11, 10 | `test_tat_khe_mot_lan_theo_ma_khong_kiem_version`, `test_bat_khe_kiem_version`, `test_crash_sau_khi_ghi_su_kien_khong_ghi_lan_hai`, `test_tat_bat_khe_qua_api_can_dai_ca_va_idempotent` — ghi bằng `bat_tat_khe` của 3a-1 nên `khe_dang_bat` (cấp phiếu) và dừng mềm `khe-tat` (nhịp tim 3a-1) thấy ngay |
| Spec 3 §8.3: Đại ca đóng cầu dao tay từ dashboard 2b (`POST /api/khe/{id}/cau-dao-dong`) | 1, 8, 11 | `test_dong_cau_dao_chi_khi_dang_ngat`, `test_cau_dao_dong_va_loi` |
| §5.4 Usage: token + chi phí theo ngày/tuần, theo khe, theo dự án — sự kiện trạm + `ccusage --json` | 2, 3, 4, 11, 12 | `test_doc_dong_dung_khoang_va_ngay_vn`, `test_tong_hop_theo_ngay_tuan_nguon_du_an_va_chi_phi`, `test_chay_dung_lenh_co_dinh_moi_truong_toi_thieu`, `test_loi_khong_nem_ra_ngoai`, `test_usage_tu_su_kien_va_ccusage` |
| §5.4 bảng điểm thợ khe × vai | 9 | `test_bang_diem_lan_chay_trung_binh_tren_phieu_da_ket_thuc` — 2 chỉ số còn lại `null` (G9, Để sau) |
| §5.4 luật vai ↔ khe | 9, 10 | `luat_vai.vai_cua_buoc` trong `test_doi_ngu_the_khe…`; `DoiNgu.vue` |
| §5.2 "Hệ cần xem" — cầu dao khe | 5, 10 | `test_muc_cau_dao_chi_khe_dang_ngat_va_het_khi_toi_gio`, `test_api_phe_duyet_co_muc_cau_dao_khi_bat_kho_phieu`; node `khoá mục Phê duyệt không trùng…` |
| §6 tin "cầu dao khe ngắt / khe hết hạn mức", từ `khe.cau_dao_ngat`, không nội dung nghiệp vụ, chống ồn | 6 | `test_cau_dao_ngat_thanh_tin_theo_ly_do`, `test_soan_tin_khe_chi_ma_khe_va_link`, `test_chong_on_khong_lap_cung_khe_trong_mot_gio` |
| §7 API lát 2b: `GET /api/doi-ngu`, `POST /api/khe/{id}/bat|tat|cau-dao-dong`, `GET /api/usage`; mọi POST có `ma_thao_tac` + `expected_version` | 11 | `test_api_doi_ngu.py` (5) |
| §4 bảo mật: danh tính + CSRF cho ghi, Bearer thợ không có quyền, không `v-html`, CSP | 11, 10, 12 | `test_tat_bat_khe_qua_api_can_dai_ca_va_idempotent` (403 không danh tính, 403 với Bearer), `kiem-an-toan.mjs`, `vite build` không có `<style>` nội tuyến |
| §8 ccusage "chốt ở plan 2b", không tự cập nhật (Q15) | 2, 4 | G6; `test_sai_bao_loi` (đường tương đối, `latest`, `1.2` bị từ chối), test phiên bản lệch → không chạy |
| §12.2–§12.3 tính bền thao tác ghi, sự kiện mang `ma_thao_tac` | 1, 8 | `test_bat_tat_khe_mang_them_nhung_khong_de_khoa_chinh`, `test_dong_cau_dao_mang_them_va_phien_ban_khe_doi_theo_su_kien`, `test_crash_sau_khi_ghi_su_kien_khong_ghi_lan_hai` |
| §2 D2 (≤ 10 s không tải lại) cho màn 2b | 5, 10, 12 | `test_luong_bao_doi_ngu_va_phe_duyet_khi_cau_dao` (SSE `doi_ngu_doi`); trang Đội ngũ tải lại 5 s cho trạng thái suy từ nhịp tim (G15) |
| Spec 3 §8.1 dashboard hiện "đọc lúc", đánh dấu cửa sổ chưa biết, không 0% | 7, 9 | node `mô tả cửa sổ hạn mức: còn lại, reset, chưa biết không phải 0%`; `muc_han_muc → chua_biet` |
| Spec 3 §8.1 ccusage không dùng để chặn giao việc | 4, 11 | ccusage chỉ được `/api/usage` gọi; không module phần 3/4 nào import `tram.usage` |

**2. Quét placeholder:** không có "TBD/TODO/tương tự Task N"; mọi bước mã có khối mã đầy đủ (file mới nguyên văn; file có sẵn bằng bản vá sinh từ bản đã chạy); mọi lệnh có kết quả mong đợi. `<model đang thực thi>` trong lệnh commit là cố ý. Các chỗ "chờ chạy thật / chờ S1, S6 / chờ phần 4" là cổng có chủ đích, có mục "Để sau" và giao diện chừa sẵn.

**3. Khớp chữ ký:** `bat_tat_khe(..., them)`, `dong_cau_dao(..., them)`, `phien_ban_khe` (1) ↔ 8, 9; `tat_khe_thao_tac/bat_khe_thao_tac/dong_cau_dao_thao_tac(kho, kho_tt, khe_id, *, …, ma, expected_version, luc)` (8) ↔ 11; `doi_ngu(kho, *, bay_gio, ch)` (9) ↔ 11; `doc_dong_usage(db, tu, den)`, `tong_hop(dong, gia)` (3) ↔ 11; `KetQuaCcusage`, `DocCcusage(...).theo_ngay`, `BoDemCcusage(...).lay` (4) ↔ 11; `CauHinhUsage`, `nap_cau_hinh_usage` (2) ↔ 11; `muc_cau_dao(kho, bay_gio)` + `gom_phe_duyet(..., them)` (5); JSON `muc_han_muc`, `phien_ban`, `cau_dao`, `han_muc.cua_so` (9, 11) ↔ `luat_doi_ngu.js` (7) ↔ `TheKhe.vue` (10); `theo_*`, `ccusage.theo_ngay` (11) ↔ `BangUsage.vue`, `Usage.vue` (12); `kho.phienBanDoiNgu` (10) ↔ 12. `PhuThuocApi` chỉ thêm trường có mặc định — `tests/api_gia.py::tao_pt` và `tests/tho_api_gia.py::tao_tram` (3a-1) vẫn chạy.

**4. Đã chạy thử (13/10):** dựng bản sao ở scratchpad (không đụng repo thật, không gọi Claude/Codex/ccusage/mạng, không Keychain, không `~/.tram` thật): `git archive 891ae04` (main, 720 test) + toàn bộ mã của plan 3a-1 lấy từ bản dựng lại nguyên văn từ văn bản plan 3a-1 → **1015 passed** (= 720 + 295). Mọi mã và test của plan này chạy trên bản đó. Mô phỏng thực thi theo worktree: mỗi task dựng trên "main sau đợt trước" + riêng file của task, chạy test của task rồi toàn bộ; ghép từng đợt: 1015 → **1047** → **1054** → **1059 passed**; node 7 → 13 → 13 → 13; `vite build` xanh sau mỗi đợt. Thông báo fail ở Step 2 mỗi task là kết quả chạy thật (test của task trên "main đợt trước", chưa có mã). Bản vá trong plan sinh bằng `git diff` từ chính bản đã chạy (trên nền 3a-1); 1b-3 chưa có nên chưa thử áp lên nền có 1b-3 (G2). `npm ci --offline` dùng gói đã khoá của 2a từ cache — không thêm gói.

**5. Rủi ro còn lại (Đại ca biết):** (a) Trước khi có thợ thật (3a-2) và phần 4, màn Đội ngũ chỉ có khe đăng ký qua `/api/tho/dang-ky`, hạn mức "chưa biết", bảng điểm rỗng — chạy được nhưng ít dữ liệu; (b) adapter ccusage có thể phải sửa sau khi chạy thật (cờ/dạng JSON) — gói gọn trong `tram/usage/ccusage.py` + test; (c) chi phí theo khe/dự án phụ thuộc bảng giá Đại ca điền — để trống thì chỉ có token; (d) `cham_cot.ket_qua` không lưu token cache → chi phí bộ chấm thiếu phần cache (nhỏ); (e) tin khe bị giờ yên lặng chặn (G14) — khe cạn hạn mức lúc 23:00 chỉ báo sau 07:00 (vẫn hiện ngay trên Phê duyệt); (f) bản vá có thể không áp thẳng nếu 1b-3 sửa cùng dòng (G2).

## Đồng bộ spec sau review (đã sửa spec 2; phần spec 3 giao người sở hữu)

- **Spec 2 §7** (bảng API): `POST /api/khe/{may_id}/{ten}/…` (URL thật `/api/khe/B/claude-1/tat`, G16); `GET /api/usage?so_ngay=` (1–92, mặc định 14 — G8); SSE thêm `doi_ngu_doi` (G15); `GET /api/doi-ngu` có `phien_ban` mỗi khe làm `expected_version` (G4).
- **Spec 2 §8**: ccusage **cài cố định** bằng `npm install --prefix ~/.tram/ccusage --save-exact --ignore-scripts`, không `npx`, khoá phiên bản trong `usage.ccusage_phien_ban`, chạy `--offline` (G6).
- **Spec 2 §12.5** (`~/.tram/cau-hinh.yaml`): thêm khoá `usage: {ccusage, ccusage_phien_ban, gia_usd_moi_trieu_token}` (G6, G7).
- **Spec 2 §12.2** (bảng sự kiện) và **spec 3 §10**: `khe.bat`/`khe.tat`/`khe.cau_dao_dong` do dashboard ghi mang `ma_thao_tac`, `tac_nhan = dai-ca/dashboard`; `khe.cau_dao_dong.ly_do = "dai-ca"` khi Đại ca đóng tay (G3).
- **Spec 2 §5.4**: bảng điểm ở 2b chỉ có số phiếu / xong / lần chạy TB; "qua lần đầu", "bị trả về" có từ phần 4 (G9); nhãn trạng thái thêm "Cần Đại ca", "Lỗi lần chạy cuối" theo sáu giá trị của spec 3 §10.1 (G11); "còn lại" = 100 − phần đã dùng (G10, chờ S1).
- **Spec 2 §6**: hai loại tin `khe_cau_dao`, `khe_het_han_muc`, chỉ mang mã khe; chịu giờ yên lặng (G14).
- **Spec 2 §5.2**: mục "Hệ cần xem" cầu dao khe không có nút "thử lại", dẫn sang Đội ngũ AI (G13).

## Ghi chú triển khai (13/10/2026)

- 12 task ghép vào `main` (N₀ = 1119 sau 3a-1 + 1b-3, M₀ = 12 node). Task 5 ghép sau cùng vì phải chờ bản sửa segfault `tram/api/luong.py` (bead bs-64w: `run_in_threadpool` thay `asyncio.to_thread` để không đóng SQLite khi luồng đọc còn chạy) — giữ nguyên bản sửa đó.
- Số test thật: 1119 → 1148 (đợt 1 trừ T5) → 1155 → 1160 → +1 (test bs-64w) → **1164 + 49 của 4a-1 đợt 1 = 1213** tại thời điểm ghép T5; riêng 2b thêm đúng **44** test như plan. Node 12 → **18**, build xanh.
- Mã Codex sửa sau review (C01 version nguyên tử khe, Q11–Q13 ccusage, N02 allowlist, G15 polling 5 giây) chạy xanh ngay lần đầu.
- Lệch plan: Task 10, 12 áp tay hunk frontend trên nền 1b-3 (giữ menu/route "Ký ức"); Task 10 đổi comment "30 giây" → "5 giây (G15)" cho khớp hằng số.
