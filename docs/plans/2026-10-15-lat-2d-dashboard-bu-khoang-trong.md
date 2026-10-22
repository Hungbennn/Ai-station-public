# Lát 2d — Dashboard bù khoảng trống — Implementation Plan

> **Sửa 16/10 theo D41 (G19 của plan 2f)** ([chốt đợt 4](../quyet-dinh/2026-10-15-chot-dot-4.md), mục "Chốt câu mở của 5 plan sửa"):
> - Bảng điểm trên trang Đội ngũ AI phải có hàng cho khe chưa có phiếu nào ("chưa có"), như mockup `anh-doi-ngu.png` (hàng `codex-2 · coder · 0`). Đại ca chọn **đổi API của 2d**, 2f không ghép hàng phía trình duyệt nữa.
> - **Task 6** thêm `du_hang_khe`: `GET /api/doi-ngu` → `bang_diem` có một hàng cho mỗi (khe, vai ưu tiên) của mọi khe đã khai, lấy từ chính danh sách `trang_thai_khe` mà route dùng cho thẻ khe. Hàng không có phiếu: 0 phiếu, vai `coder` mẫu 0 (tỉ lệ `null`), vai khác mẫu `null`. Bộ lọc dự án / số ngày không làm mất hàng (G22). Thêm 1 test py.
> - Câu mở Q2 đóng. Task 1–5, 7 không đổi mã. Đã chạy thử lại trên bản sao `main` `503ff64`: 1994 → 2005 (đợt 1) → **2009** (đợt 2), node 33 → **37**; build và `kiem-dist` xanh.
> - Mục "Sửa 15/10" dưới đây giữ nguyên chữ; chỗ nào khác bản D41 thì theo bản D41.

> **Sửa 15/10 theo D25–D29, D33 và D38** ([chốt đợt 4](../quyet-dinh/2026-10-15-chot-dot-4.md)). Bản này xử lý F06 của review Codex đợt 4.
> - **D25–D29:** Đại ca đã trả lời S1–S8. Bỏ cổng "chờ S1–S8"; Task 1, 2, 6 giao được. Mã và test Task 1 viết lại vì hai câu đổi so với cách hiểu tạm:
>   - S2 (D26): QC "đầu tiên" phải **ghi sau** lần kiểm lại sớm nhất.
>   - S5 (D27): mỗi lần vào cột 3 là một mẫu của khe có phiếu code trong bằng chứng.
> - **D20, D33, D38:** mockup giao diện đã duyệt; giao diện làm lại toàn bộ ở **lát 2f** (chưa có plan).
>   - D38 (Q14 của [khảo sát giao diện](../handovers/2026-10-15-khao-sat-giao-dien.md)): **ghép 2d nguyên văn trước 2f**, kể cả phần `.vue` nhỏ của Task 2 và Task 5.
>   - 2f làm lại các file `.vue` đó theo mockup và **giữ nguyên luật hiển thị JS thuần** của 2d. Vì vậy luật thuần phải đúng chữ mockup ngay từ 2d (nhãn PR, câu cảnh báo, dạng "71% (5/7)").
>   - D38 chốt C6 = "có": trang Phê duyệt hiện trạng thái PR trạm. **2d giữ dữ liệu/API** (Task 7 mới: `chi_tiet.pr_tram` trong `/api/phe-duyet`); phần `.vue` của trang này làm ở 2f.
>   - Ranh giới và hợp đồng cho 2f ở mục "Ranh giới 2d ↔ 2f".
> - Đã chạy thử lại trên bản sao `main` `38a016f` (mã giống `main` `4a907cc` hiện tại), mã chép nguyên văn từ plan. Xem "Global Constraints".
> - Review Codex đợt 4 kết luận 2d "chưa sẵn sàng" vì F06. Bản sửa này **chưa** được Codex review lại. Mục "Bổ sung review đợt 4" ở cuối giữ làm lịch sử; chỗ nào khác với bản này thì theo bản này.

> **For agentic workers:** REQUIRED SUB-SKILL: Use ai-skills:subagent-driven-development (recommended) or ai-skills:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **Sửa 15/10 theo quyết định D12–D15** ([chốt đợt 4](../quyet-dinh/2026-10-15-chot-dot-4.md)):
> - **D13:** hai chỉ số bảng điểm theo **đúng chữ spec 4 §12**, bỏ cả ba chỗ hiểu khác chữ spec của bản trước (loại phiếu chờ khỏi mẫu, xử lý riêng spike, xử lý riêng phiếu lỗi). Chỗ spec chưa định ghi thành S1–S8; Đại ca đã chốt ở D25–D29.
> - **D14:** lọc bảng điểm theo dự án + số ngày (mặc định mọi dự án, 30 ngày). Thêm Task 6 (API).
> - **D15:** thêm tin `pr_khong_xac_minh`.
> - **D12:** đèn Điều phối là lát riêng, vẫn không làm ở 2d.

**Goal:** Lấp hai khoảng trống của dashboard phát hiện ngày 15/10 (mục "Trạng thái triển khai" của spec 2 và spec 4):
1. Bảng điểm thợ tính "qua lần đầu" và "bị trả về" từ sự kiện phần 4, theo chữ spec và D25–D29, thay cho `null`; lọc theo dự án và số ngày gần nhất (bead `bs-urj.6`, D13, D14).
2. Dữ liệu trạng thái PR do trạm mở cho thẻ cột 3 và cho mục "Chờ review để đóng" của trang Phê duyệt (D38), nhất là `pr.khong_xac_minh` kèm lý do. Telegram báo "PR đã merge" và "PR không xác minh được" (bead `bs-urj.8`, D15).
3. Luật hiển thị JS thuần cho hai phần trên, theo nhãn và câu của mockup đã duyệt; lát 2f dùng lại nguyên văn. Kèm sửa `.vue` tối thiểu trên bố cục cũ (ô lọc, nhãn PR trên thẻ, khối PR trong ngăn bên) để dữ liệu mới hiện được ngay sau khi ghép; 2f làm lại các file này theo mockup (D38).

Không làm ở lát này:
- **Đèn Điều phối** (`bs-urj.7`). Đại ca đã chọn nguồn tín hiệu (D12), nhưng phần này là một lát riêng, xem "Để sau".
- **Giao diện theo mockup** (bố cục mới, nhóm nút 7/30/92, chip `.pr-*`, thẻ Phê duyệt có PR trạm). Phần này thuộc lát 2f (D20, D33, D38).

**Architecture:** Không thêm kho trạng thái; mọi thứ tính lúc đọc (Q12).
- **Bảng điểm.** Module mới `tram/suy/diem_giao_viec.py`:
  - đọc phiếu `code` theo bộ lọc (dự án, `cap_luc` ≥ mốc — D28);
  - quét một lần năm loại sự kiện `giao.cong_bo`, `kiem.lai`, `qc.ket_qua`, `bead.vao_cot_3`, `cot.tra_ve`. Các sự kiện này nằm cùng file `su-kien.db` với bảng `phieu`;
  - tính hai chỉ số theo chữ spec 4 §12 và D25–D29.

  `bang_diem(db, *, du_an, tu)` gắn tỉ lệ và cỡ mẫu vào hàng vai `coder`, và cùng bộ lọc áp cho mọi cột. `GET /api/doi-ngu` nhận `?du_an=&so_ngay=` (D14) và thêm hàng 0 phiếu cho mỗi (khe, vai ưu tiên) của khe đã khai chưa có hàng (`du_hang_khe`, D41).
- **Thẻ cột 3.** Module mới `tram/suy/pr_tram.py` đọc `pr.mo`, `pr.khong_xac_minh`, `pr.da_merge` ghi sau lần `bead.vao_cot_3` hiện hành, rồi gắn vào `giao.pr.tram` của `GET /api/giao-viec` có sẵn (4a-2). Không thêm route, không đụng `app.py`. SSE thêm ba loại `pr.*` vào `LOAI_LAM_MOI`.
- **Phê duyệt (D38, Task 7).** `gom_phe_duyet` gắn `chi_tiet.pr_tram` (cùng hàm `pr_tram`) vào mục `cho-review` của `GET /api/phe-duyet` có sẵn. Không route mới.
- **Telegram.** Hai loại tin mới `pr_da_merge` và `pr_khong_xac_minh`, đi qua `tin_tu_su_kien` → `BoChongOn` có sẵn. Nội dung chỉ có dự án, mã bead và link dashboard.
- **Frontend.**
  - Luật hiển thị thuần, test bằng `node --test`, theo nhãn/câu của mockup đã duyệt. `luat_doi_ngu.js`: đường dẫn API có bộ lọc, ô tỉ lệ kèm cỡ mẫu. `giao_viec.js`: nhãn, lớp chip, dòng mô tả và câu cảnh báo của PR trạm. Lát 2f giữ nguyên các hàm này (D38).
  - Sửa nhỏ trên bố cục cũ: `DoiNgu.vue` (ô chọn dự án + khoảng ngày), `TheBead.vue`, `OGiaoViec.vue`. Không đổi CSS. 2f làm lại ba file này theo mockup (D38).

**Tech Stack:** Python 3.12 (`uv`), FastAPI (đã khoá ở 2a), SQLite stdlib (`json_extract`), `pytest`; Vue 3.5.43, Vite 8.3.4, `@vitejs/plugin-vue` 6.0.10 (đã khoá), `node:test`. **Không thêm phụ thuộc** (Python lẫn npm).

**Spec:**
- [Spec 2](../specs/2026-10-12-phan-2-dashboard.md) (ĐÃ DUYỆT): §5.4 bảng điểm thợ; §5.2 hàng "Chờ review để đóng" (Duyệt tay sau 4c); §6 Telegram và chống ồn; §4 mục 4–5; §2 D2; "Trạng thái triển khai (15/10/2026)" và "Lệch so với spec khi code" (dòng §5.2 (4c)).
- [Spec 4](../specs/2026-10-13-phan-4-giao-viec.md) (ĐÃ DUYỆT): §12 "Bảng điểm thợ" — định nghĩa hai chỉ số, **làm theo chữ spec** và D25–D29; §4; §6.1–§6.6; "Lệch so với spec khi code" (4c G3, G6).
- [Quyết định chốt đợt 4](../quyet-dinh/2026-10-15-chot-dot-4.md): D12–D15, D20, D25–D29, D33, D38 (Q7, Q14 của khảo sát).
- [Khảo sát giao diện cho lát 2f](../handovers/2026-10-15-khao-sat-giao-dien.md): §1.11 "Đối chiếu với plan 2d và 2e", §3.5 Q7, Q14.
- [Mockup giao diện đã duyệt](../mockup/2026-10-15-giao-dien/) (D20, D33): `trang.js` (`theBead`, `moBead`, `veDoiNgu`, `theReview`), `du-lieu.js` (`NHAN_PR`, `BANG_DIEM`), `chung.js` (`tiLe`), `style.css` (`.pr-*`, `.canh-bao`); ảnh `anh-doi-ngu.png`, `anh-phe-duyet.png`, `anh-cong-viec*.png`.
- Đọc kèm các plan: [2b](2026-10-13-lat-2b-doi-ngu-usage.md) (G9, Task 9 — `bang_diem`); [4c](2026-10-13-lat-4c-pr-gitnexus-lop5.md) (G3, G6, G7, G20, Task 5 — `pr_merge.py`); [2a](2026-10-13-lat-2a-dashboard.md) (Telegram, `/api/luong`); [2c](2026-10-13-lat-2c-van-phong-3d.md) (G4 — đèn Điều phối). Plan 4a-2 cho `GET /api/giao-viec` và `thong_tin_pr`.

## Global Constraints

- **Mốc (bản D41):** plan sửa lại trên `main` `503ff64`; mã (`tram/`, `tests/`, `frontend/`) giống hệt `38a016f` và `4a907cc`, chỉ khác docs. Đo 16/10 trên `503ff64`: N₀ = **1994**, M₀ = **33**.
- **Mốc (bản 15/10):** plan sửa trên `main` `4a907cc`. `4a907cc` so với `38a016f` chỉ thêm D39 và mockup Ký ức/Usage (docs), mã giống hệt. Từ `1e7e9b0` (mốc bản trước) tới `38a016f`, mã chỉ đổi ở 3c T2, T4, R3 (`tram/cong_bo/`, `tram/cau_hinh/cong_bo.py`, `tram/chu/cai_dat.py`, `tram/tho/principal_khe.py`) và thêm font vào `frontend/src/assets/fonts/`. Không file nào 2d vá. **N₀** là số `passed` của `uv run pytest -q`, **M₀** là số test của `npm run kiem`, đo trên `main` lúc bắt đầu lát — **đo lại khi thực thi**. Đo 15/10 trên `38a016f`: N₀ = **1994**, M₀ = **33**. Mọi số viết dạng `N₀ + k`, kèm số tuyệt đối trên bản dựng thử.
- **Đã chạy thử (bản D41, ngày 16/10):** bản sao `main` `503ff64` trong scratchpad, thư mục riêng; mã chép nguyên văn từ plan này bằng script trích khối, áp theo thứ tự đợt.
  - Sau đợt 1: **2005 passed** (N₀ + 11). Sau đợt 2: **2009 passed** (N₀ + 15); `npm run kiem` → **37** (M₀ + 4); `npm run build`, `npm run kiem-dist` xanh.
  - Step 2 của Task 6 chạy trên main sau đợt 1, thông báo fail ghi trong Task 6 là kết quả thật.
  - Áp tiếp plan 2e rồi 2f-1, 2f-2 nguyên văn: xem "Kết quả chạy thử" của plan 2f-1.
- **Đã chạy thử (bản sửa D25–D29, D33, D38, ngày 15/10):**
  - Bản sao `main` `38a016f` trong scratchpad, thư mục riêng, không đụng repo thật.
  - Mã, test và bản vá chép nguyên văn từ chính file plan này bằng script trích khối mã, áp theo thứ tự đợt.
  - `uv run pytest -q` → **2008 passed** (N₀ + 14).
  - `npm run kiem` → **37** (M₀ + 4).
  - `npm run build` và `npm run kiem-dist` xanh.
  - Mọi bản vá đã qua `git apply --check`. Thông báo fail ở Step 2 là kết quả chạy thật.
- **TDD:** mỗi task viết test trước, chạy thấy fail, viết mã, chạy thấy pass. Component `.vue` không có test đơn vị riêng. Cổng kiểm của chúng là `npm run kiem` (luật thuần + quét chèn HTML), `npm run build`, `npm run kiem-dist`.
- **Mỗi file ≤ ~120 dòng, mỗi dòng ≤ 120 ký tự.** Dòng dài có sẵn trong file cũ thì không sửa. File dài nhất sau plan: `tests/test_bang_diem_4.py` 120, `tram/suy/phe_duyet.py` 103, `frontend/src/trang/DoiNgu.vue` 86, `tram/api/luong.py` 83, `tram/suy/diem_giao_viec.py` 82.
- **Mỗi task một worktree, một nhánh, một commit**, tạo từ `main` sau khi đã ghép đợt trước. Task cùng đợt không sửa chung file. Không push, không merge hộ.
- **Không thêm phụ thuộc.** Không gọi mạng. Frontend cài bằng `npm ci --offline --ignore-scripts` (đã thử chạy được từ cache npm của máy).
- **Test không được:**
  - gửi Telegram thật (`gui` là hàm giả `list.append`);
  - gọi mạng, GitHub hay `gh`;
  - đọc Keychain;
  - đụng `~/.tram` thật (`TRAM_HOME` tạm — `tests/conftest.py`);
  - đụng dịch vụ đang chạy (tram-api, tram-bao-tin của launchd);
  - chạy `bd` thật (dùng `BdGia`).
- **Không vá các file sau:**
  - `tram/tho/vong_khe.py`, `tram/giao_viec/bo.py`, `tram/tho/ngu_canh.py`, `tram/api/app.py`, `tram/giao_viec/tick_theo_plan.py`;
  - `tram/nho/**`, `tram/cau_hinh/cach_ly.py`, `tram/chu/cai_dat_tho.py`;
  - CSS và mọi file `.vue` ngoài `DoiNgu.vue`, `TheBead.vue`, `OGiaoViec.vue`. Giao diện trang Phê duyệt (`MucPheDuyet.vue`, `PheDuyet.vue`) để 2f làm; 2d chỉ thêm dữ liệu ở `tram/suy/phe_duyet.py` (Task 7, G21).

  Plan **không** cần vá `app.py` vì không thêm route.
- **Producer phần 4 chỉ đọc:** không sửa file nào trong `tram/giao_viec/`.
- **Định nghĩa bảng điểm (D13, D25–D29):** theo chữ spec 4 §12 và các câu Đại ca đã chốt. Không tự loại phiếu khỏi mẫu, không xử lý riêng spike hay phiếu lỗi. Mỗi chỗ trong mã ghi số quyết định ngay tại chỗ. Chỗ còn hỏi được ghi ở "Còn mở", không tự chọn thêm.
- **Bảo mật (spec 2 §4) giữ nguyên:**
  - CSP không đổi; cấm `v-html`; chuỗi từ server hiện bằng `{{ }}`. Luật thuần trả **chuỗi**, không trả HTML. Phần "(5/7)" in nhạt của mockup được tách thành trường riêng (`oTiLe`), không chèn thẻ.
  - Link PR qua hai lớp: server kiểm dạng URL GitHub; frontend kiểm lại bằng `laLinkAnToan` trước khi gắn `href`.
  - Lý do `pr.khong_xac_minh` là câu hằng do server ánh xạ.
  - Telegram chỉ mang tên dự án, mã bead đã qua `ID_AN_TOAN` và link dashboard. Không số PR, URL PR, SHA, nhánh hay lý do.
  - `?du_an=` chỉ nhận dự án có trong `du-an/*.yaml` (`kiem_du_an_bead` → 404); `?so_ngay=` chỉ nhận số nguyên 1–92 (422).
- **Chống ồn giữ nguyên `BoChongOn`:** tin đầu gửi ngay; tin cùng loại trong 5 phút gom lại; không lặp (loại, dự án, bead) trong 1 giờ; giờ yên lặng chặn mọi loại trừ `tram_loi`; gửi lỗi thì xếp lại.
- **Lệnh kiểm:** `uv run pytest -q` ở gốc worktree; trong `frontend/` chạy `npm run kiem`, `npm run build`, `npm run kiem-dist`.

## Phụ thuộc đã có (main `4a907cc`, mã như `38a016f`) — dùng, không sửa trừ chỗ ghi rõ

| Thứ dùng | Ở đâu (plan) | Plan 2d dùng ở |
|---|---|---|
| `KhoPhieu(duong_dan)`: `.db`, `.giao_dich()`, `.ghi_su_kien(…)`; `chuoi_gio(datetime) -> "YYYY-MM-DDTHH:MM:SSZ"`. Bảng `phieu(giao_id, du_an, bead_id, khe_id, luot, noi_dung, trang_thai, ket_thuc, cap_luc, …)`: `noi_dung` là JSON của `Phieu` (`buoc`, `vai`, `can_lenh_kiem`). Bảng `su_kien` nằm cùng file | `tram/phieu/kho.py`, `luoc_do.py` (3a-1 T13) | Task 1, 6 |
| `bang_diem(db)` (**sửa ở Task 1**); `doi_ngu(kho, *, bay_gio, ch)` (**sửa ở Task 6**) | `tram/suy/bang_diem.py`, `doi_ngu.py` (2b T9) | Task 1, 6 |
| `r_doi_ngu` của `GET /api/doi-ngu` (**sửa ở Task 6**); `kiem_du_an_bead(pt, du_an)` → `KhongThay` 404; `KhongHopLe` 422; mẫu tham số `so_ngay` 1–92 của `/api/usage` | `tram/api/doi_ngu.py` (2b T11), `phu_thuoc.py`, `usage.py` | Task 6 |
| `giao.cong_bo {bead_id, luot, commit, ref}`, cột `bead_id`, ghi khi trạm công bố SHA của một lượt | `tram/cong_bo/op.py::ghi_cong_bo` (3a-2) | Task 1 (D25) |
| `kiem.lai {giao_id, bead_id, luot, commit, digest_tieu_chi, dat, …}`, với `commit` = SHA công bố của lượt code | `tram/giao_viec/tick_pipeline.py::_kiem_lai` | Task 1 (D26) |
| `qc.ket_qua {giao_id, bead_id, commit_code, commit_qc, ket_luan: dat \| tra_ve \| khong_cong_nhan, …}` | `tram/giao_viec/xu_ly_viec.py::_xet` | Task 1 (D26) |
| `bead.vao_cot_3 {bead_id, commit_code, commit_ban_giao, digest_tieu_chi, giao_id_code, luot_code, co_do, co_do_ly_do, pr: null, ma_thao_tac}`. **`giao_id_code`** = `giao_id` của phiếu code trong bằng chứng (`bo_bang_chung` lấy từ `kiem.lai` khớp `giao.nhan` bước `code`); ghi một lần theo `ma_thao_tac` | `tram/giao_viec/bang_chung.py::vao_cot_3` | Task 1 (D27), 3 |
| `cot.tra_ve {gop_y, ma_thao_tac}` do nút Trả về của dashboard ghi, cột `bead_id` | `tram/thao_tac/phe_duyet.py` (2a) | Task 1 (D27) |
| `pr.mo {bead_id, loai: bead \| spec, pr, url, nhanh, commit, ma_thao_tac}` | `tram/giao_viec/pr.py::_ghi` (4c T5) | Task 3 |
| `pr.khong_xac_minh {bead_id, pr, commit, ly_do, ma_thao_tac}`: 7 mã lý do; chỉ ghi khi PR đã `MERGED` | `tram/giao_viec/pr_merge.py` (4c T5) | Task 3, 4 |
| `pr.da_merge {bead_id, pr, url, commit, merge_commit, nhanh_chinh, ma_thao_tac}`: ghi một lần, **trước** `bd close` | `pr_merge.py::kiem_merge` (4c T5, G7) | Task 3, 4 |
| `suy_giao(da, beads, kho, kg)` (**sửa ở Task 3**); `thong_tin_pr` (đọc); route `GET /api/giao-viec` (đọc) | `tram/suy/giao_viec.py`, `tram/api/tuyen_giao.py` (4a-2) | Task 3 |
| `gom_phe_duyet(cac_du_an, theo_du_an, kho, them)` (**sửa ở Task 7**); `muc_tu_beads` (đọc); mục `cho-review` có `chi_tiet {pr, nhanh, commit, file_ban_giao, loi}`; route `GET /api/phe-duyet` (đọc) | `tram/suy/phe_duyet.py`, `tram/api/tuyen_doc.py` (2a) | Task 7 |
| `KhoSuKien.ghi(…)`, `.moi_nhat(du_an, bead_id, loai, *, dieu_kien)` → `SuKien(…, id)` | `tram/su_kien/kho.py` (2a) | Task 3, 4 |
| `LOAI_LAM_MOI` (**sửa ở Task 3**), `mot_nhip`, `TrangThaiLuong` | `tram/api/luong.py` | Task 3 |
| `LOAI_TIN`, `NHAN_LOAI` (**sửa ở Task 4**); `Tin`, `soan_tin`, `ID_AN_TOAN`. `tin_tu_su_kien` (**sửa ở Task 4**). `BoChongOn`, `mot_vong`, `NguCanhBaoTin` | `tram/bao_tin/` | Task 4 |
| Test: `kho_tam`, `dat_phieu(kho, khe_id, *, luc, **kw)`, `LUC`; `danh_dau_ket_thuc`; `bug`, `du_an_gia`; `BdGia`, `bead`; `BoDemBeads`; `tao_pt`, `goi` | `tests/` | Task 1, 3, 4, 6 |
| Frontend: `tiLe`, `dinhDangSo` (`luat_doi_ngu.js` — **sửa ở Task 2**); `DoiNgu.vue` (**sửa ở Task 2**); `GET /api/du-an` → `{du_an: [{ten, …}]}`; `ganGiaoViec`, `canhBaoPr` (`giao_viec.js` — **sửa ở Task 5**); `TheBead.vue`, `OGiaoViec.vue` (**sửa ở Task 5**); `laLinkAnToan`; lớp CSS `.cong-cu`, `.nhan-nho`, `.vang`, `.canh-bao`, `.nho` | 2a, 2b, 4a-2 | Task 2, 5 |
| Mockup đã duyệt: `NHAN_PR` (`du-lieu.js`), `tiLe` (`chung.js`), câu cảnh báo PR của `theReview`, dòng "PR #n — lý do" của `moBead` (`trang.js`), lớp `.pr-mo`, `.pr-khong_xac_minh`, `.pr-da_merge` (`style.css`) | `docs/mockup/2026-10-15-giao-dien/` (D20, D33) | Task 2, 5 (chữ của luật thuần); lát 2f (bố cục) |

## Câu hỏi / giả định

Ý nghĩa cột "Loại":
- **HỢP ĐỒNG MỚI**: giao diện hoặc dữ liệu mà bên khác dựa vào (kể cả lát 2f).
- **lệch chữ spec**: làm khác câu chữ spec. Bản này **không có dòng nào thuộc loại này**.
- **D…**: đã có quyết định của Đại ca.
- **giả định**: chi tiết thực thi.

| # | Chỗ mơ hồ | Chọn | Vì sao | Loại — lệch chữ spec / HỢP ĐỒNG MỚI |
|---|---|---|---|---|
| G1 | Mốc test | N₀/M₀ đo lại khi thực thi. Đo 15/10 trên `38a016f` và 16/10 trên `503ff64`: 1994 / 33 | Plan khác có thể ghép trước | giả định |
| G2 | "Qua lần đầu" (spec 4 §12) | **Tử:** số phiếu `code` thoả cả hai điều kiện: (1) `kiem.lai` sớm nhất có `commit` = SHA của phiếu là đạt; (2) `qc.ket_qua` sớm nhất có `commit_code` = SHA **và ghi sau lần kiểm lại (1)** là `dat`. **SHA của phiếu** = `commit` của `giao.cong_bo` cùng dự án, bead và `luot` của phiếu; nhiều bản thì lấy bản sau cùng. **Mẫu:** số phiếu `code` có `phieu.ket_thuc = 'xong'`. Tử không đòi phiếu xong. Phiếu chưa công bố, phiếu chờ QC, spike: vẫn ở mẫu, không vào tử; không xử lý riêng | Chữ spec + Đại ca chốt | **D13, D25, D26, D29** |
| G3 | "Bị trả về" (spec 4 §12) | **Mẫu:** mỗi sự kiện `bead.vao_cot_3` là một mẫu. Mẫu quy cho khe của phiếu có `giao_id` = `giao_id_code` trong payload, tức phiếu code nằm trong bằng chứng. **Tử:** mẫu bị trả về khi sự kiện kế tiếp của cùng (dự án, bead), xét trong hai loại `bead.vao_cot_3` / `cot.tra_ve`, là `cot.tra_ve`, tức lần trả về xảy ra trước lần vào cột 3 kế tiếp. Nhiều lần trả về liền nhau vẫn tính một. Phiếu `giao_id_code` ngoài bộ lọc (dự án, `cap_luc`) hoặc không có trong bảng `phieu` → bỏ mẫu | Đại ca chốt | **D13, D27, D28** |
| G4 | Vai | Hai chỉ số chỉ có ở hàng `coder`. Hàng `qc`, `spec` để `null` (tỉ lệ và mẫu) | Spec chỉ định nghĩa trên phiếu code | **D29** |
| G5 | Lọc bảng điểm | `GET /api/doi-ngu?du_an=<tên>&so_ngay=<1–92>`. Mặc định: `du_an` rỗng = mọi dự án, `so_ngay = 30`. Dự án lạ → 404; `so_ngay` ngoài 1–92 hoặc không phải số → 422. Chỉ lọc `bang_diem`; thẻ khe và luật vai không đổi. Bộ lọc áp cho **mọi cột** của bảng điểm, nhưng không làm mất hàng của khe đã khai (G22, D41). Phiếu thuộc cửa sổ khi `cap_luc` ≥ bây giờ − `so_ngay` × 24 giờ (UTC); dự án lấy theo `phieu.du_an`. Sự kiện đi theo phiếu, không lọc thời gian | D14; khoảng 1–92 giống `/api/usage` | **D14, D28, D29** + **HỢP ĐỒNG MỚI** (tham số) |
| G6 | JSON `bang_diem` | Thêm `qua_lan_dau_mau`, `bi_tra_ve_mau` (`int \| null`). Tỉ lệ làm tròn 4 chữ số. Mẫu 0 → tỉ lệ `null`, không 0 giả (§5.4). Giao diện suy lại tử bằng `round(tỉ lệ × mẫu)`, đúng khi mẫu < 5000 | Phân biệt 1/1 với 20/20; mockup hiện "(5/7)" | **HỢP ĐỒNG MỚI** |
| G7 | Luật hiển thị bảng điểm (JS thuần, Task 2) | `SO_NGAY_BANG_DIEM = [7, 30, 92]`; `duongDanDoiNgu(duAn, soNgay)`; `oTiLe(x, mau) -> {chinh, phu}`: `71%` + `(5/7)`; `null` + mẫu 0 → `chưa có`; `null` không mẫu → `—`. `tiLe(x, mau)` nối hai phần thành một chuỗi | Theo `tiLe` và `veDoiNgu` của mockup (D20) | **HỢP ĐỒNG MỚI** (hàm cho 2f) |
| G8 | Giao diện bảng điểm (Task 2, bố cục cũ) | `DoiNgu.vue`: ô "Dự án" (Tất cả + các dự án của `/api/du-an`) và ô "Khoảng" (7 / **30** / 92 ngày gần nhất); tỉ lệ dạng `tiLe(x, mau)`; chú thích định nghĩa theo G2, G3. Khe đã khai luôn có hàng (G22), kể cả khi không có phiếu trong khoảng. Dòng "Không có phiếu nào được cấp trong khoảng này" chỉ còn hiện khi `bang_diem` rỗng (chưa khai khe nào và không có phiếu); ô chọn vẫn hiện. Lát 2f làm lại theo mockup (nhóm nút, `oTiLe` in nhạt phần ngoặc) | D14; D38 | giả định — 2f làm lại |
| G9 | Hiệu năng | Mỗi lần `/api/doi-ngu` (5 s/lần) quét `su_kien` với `loai IN (5 loại)` (+ `du_an` nếu có). Bản trước đo 200k sự kiện: 34 ms. Không thêm chỉ mục | Chậm thì làm sau | giả định — "Để sau" |
| G10 | Thẻ cột 3 — dữ liệu | `GET /api/giao-viec`: `giao["<du_an>/<id>"].pr.tram = {so: int \| null, url: str \| null, trang_thai: "mo" \| "khong_xac_minh" \| "da_merge", ly_do: str \| null}` hoặc `null`. Không route mới | Khoá cấp trên không đổi | **HỢP ĐỒNG MỚI** |
| G11 | Sự kiện nào thuộc thẻ | `pr.*` có `id` lớn hơn `bead.vao_cot_3` mới nhất và `commit` = `commit_ban_giao`; với `pr.mo` thêm điều kiện `loai = bead`. Ưu tiên `da_merge` > `khong_xac_minh` > `mo` | Như `cua_so` + lọc commit của `pr_merge.py` | giả định |
| G12 | Câu lý do | Bảng hằng `LY_DO` cho 7 mã; mã lạ → "lý do khác — xem nhật ký sự kiện của bead". Câu của `khong-phai-merge-commit` lấy đúng chữ mockup: "không phải merge commit (squash / rebase)" | §4 mục 4; mockup ghép câu này sau "trạm không xác minh được:" | giả định |
| G13 | URL và số PR | Server chỉ trả `url` khớp `https://github.com/<owner>/<repo>/pull/<số>`, chỉ trả `so` khi là số nguyên; frontend kiểm thêm bằng `laLinkAnToan` (`OGiaoViec.vue` ở Task 5; 2f giữ lớp này) | Hai lớp | giả định |
| G14 | PR trạm (Task 5) | **Luật thuần:** `NHAN_PR_TRAM` = nhãn mockup: "PR đã mở", "PR không xác minh được", "PR đã merge". `nhanPrTram(the)`, `lopPrTram(t)` → `pr-<trạng thái>` (chỉ trạng thái đã biết), `moTaPrTram(t)` → "PR #12 — <lý do>", `canhBaoPrTram(t)` → câu cảnh báo của mockup Phê duyệt, chỉ khi `khong_xac_minh`. **Vue (bố cục cũ):** thẻ có nhãn PR, vàng khi không xác minh được; ngăn bên ẩn khối "Tạo PR / `gh pr create`" của 4a-2, thay bằng "<nhãn> · PR #n — lý do", câu cảnh báo và link PR | Chữ theo `NHAN_PR`, `moBead`, `theReview` của mockup (D20); spec 2 §5.2 (4c) | **HỢP ĐỒNG MỚI** (hàm cho 2f) |
| G15 | Telegram PR | Hai loại tin mới: `pr_da_merge` (nguồn `pr.da_merge`, nhãn "PR đã merge, trạm xác minh đúng commit đã kiểm") và `pr_khong_xac_minh` (nguồn `pr.khong_xac_minh`, nhãn "PR đã merge nhưng trạm không xác minh được, cần Đại ca Duyệt tay"). Nội dung: `[tram] <dự án> · n <nhãn> (<mã bead>) → <dashboard_url>`. Không số PR, URL, SHA, nhánh, lý do | Đại ca chốt gửi cả hai | **D15** + **HỢP ĐỒNG MỚI** (loại tin) |
| G16 | Chống ồn | Cả hai loại dùng nguyên `BoChongOn`. Chịu giờ yên lặng: tin rơi vào giờ yên lặng bị bỏ, không dồn tới sáng (hành vi sẵn có). Khoá 1 giờ theo (loại, dự án, bead); gom 5 phút | D15 | **D15** |
| G17 | `pr.mo` | Không thành tin | Bead đã có tin `cho_review` lúc vào cột 3 | giả định |
| G18 | SSE | Thêm `pr.mo`, `pr.khong_xac_minh`, `pr.da_merge` vào `LOAI_LAM_MOI` (D2 ≤ 10 s) | Trước đây thẻ chỉ đổi khi beads đổi | giả định |
| G19 | Đèn Điều phối (`bs-urj.7`) | Không làm ở 2d; giữ `sang: null` | D12: lát riêng, phụ thuộc #5/S6 và Tailscale máy A (D6) | **D12** |
| G20 | Ranh giới 2d ↔ 2f | 2d ghép nguyên văn trước 2f: dữ liệu/API, luật hiển thị JS thuần (có test `node`), sửa `.vue` nhỏ. 2f làm lại `.vue` theo mockup, **giữ nguyên** luật thuần và API của 2d | D38 (Q14) | **D38** + **HỢP ĐỒNG MỚI** |
| G21 | Trang Phê duyệt có hiện PR trạm không (C6 cũ) | **Có** (D38, Q7). **2d (Task 7):** mục `cho-review` của `GET /api/phe-duyet` thêm `chi_tiet.pr_tram` = `pr_tram(...)` theo lần `bead.vao_cot_3` mới nhất, hoặc `null` khi chưa vào cột 3 / trạm chưa mở PR. Khoá cũ của `chi_tiet` giữ nguyên; mục khác (kể cả `co-do`) không có khoá này. **2f:** giao diện theo `theReview` của mockup, dùng `nhanPrTram`, `lopPrTram`, `canhBaoPrTram`. Khảo sát giao diện từng đặt việc thêm trường này ở 2f T4; nay 2d làm, 2f T4 chỉ còn trường của mục `escalation` | D38; người điều phối: "2d giữ dữ liệu và API" | **D38** + **HỢP ĐỒNG MỚI** |
| G22 | Hàng khe chưa có phiếu (Q2 cũ; G19 của plan 2f) | **ĐÃ CHỐT D41 — đổi API 2d.** `GET /api/doi-ngu` → `bang_diem` có một hàng cho **mỗi (khe, vai) với vai thuộc `vai_uu_tien` của khe**, cho mọi khe đã khai. Nguồn khe = chính danh sách `trang_thai_khe(kho, …)` (`cac_khe`, sự kiện `khe.dang_ky` từ cấu hình máy thợ) mà route dùng cho `khe[]`. Hàng chưa có phiếu trong bộ lọc: `so_phieu = so_xong = 0`, `lan_chay_tb = null`, tỉ lệ `null`; mẫu = 0 nếu vai `coder` (giao diện hiện "chưa có"), `null` nếu vai khác (hiện "—", D29). Hàng có phiếu giữ nguyên, kể cả khi vai đó không thuộc `vai_uu_tien` (vai là ưu tiên, không cố định — Q14), và phiếu của khe không còn khai vẫn có hàng như cũ. Bộ lọc dự án / số ngày không làm mất hàng. Thứ tự: theo (khe, vai), như `bang_diem` và như thứ tự thẻ khe. Kho phiếu chưa bật → `bang_diem: []` như cũ | Mockup Đội ngũ AI có hàng `codex-2 · coder · 0 · chưa có`; Đại ca chọn trả từ API để 2f chỉ đọc thẳng (D41) | **D41** + **HỢP ĐỒNG MỚI** |

## Chờ Đại ca chốt

**Đã chốt (15/10, [chốt đợt 4](../quyet-dinh/2026-10-15-chot-dot-4.md)):**
- ~~C1~~ → **D12**: nguồn đèn Điều phối là hook phiên điều phối trên máy A. Lát riêng, xem "Để sau".
- ~~C2~~ → **D13**: theo sát chữ spec (G2, G3).
- ~~C3~~ → **D14**: lọc theo dự án + 30 ngày gần nhất (G5, G7, Task 6).
- ~~C4~~, ~~C5~~ → **D15**: gửi cả `pr_da_merge` và `pr_khong_xac_minh`; cả hai chịu chống ồn và giờ yên lặng (G15, G16).
- ~~C6~~ → **D38** (Q7): trang Phê duyệt có hiện trạng thái PR trạm, như mockup đã duyệt. Dữ liệu ở 2d (Task 7), giao diện ở 2f (G21).
- ~~S1–S8~~ → **D25–D29**, bảng dưới. Mã Task 1 và Task 6 theo đúng các câu này. Không còn cổng chờ nào cho Task 1, 2, 6.

| # | Spec 4 §12 / D14 nói | Câu hỏi | Đại ca chốt | Khác cách hiểu tạm? | Chỗ trong mã |
|---|---|---|---|---|---|
| S1 | "SHA của phiếu đó" | Lấy SHA ở đâu | **D25:** `commit` của `giao.cong_bo` cùng dự án, bead, `luot`; nhiều bản lấy bản sau cùng. Chưa công bố → không vào tử, vẫn ở mẫu | Không | `qua_lan_dau` |
| S2 | "`kiem.lai` đầu tiên cho SHA", "`qc.ket_qua` đầu tiên cho commit đó" | "Đầu tiên" theo gì | **D26:** `kiem.lai` sớm nhất có đúng SHA; rồi `qc.ket_qua` sớm nhất cho cùng commit **ghi sau** lần kiểm lại ấy | **Có** — bản tạm không đòi thứ tự | `_dau_tien(…, sau=)`, `qua_lan_dau` |
| S3 | "phiếu `code` kết thúc `xong`" | Theo bảng phiếu hay sự kiện | **D29:** `phieu.ket_thuc = 'xong'` | Không | `doc_phieu_code`, `qua_lan_dau` |
| S4 | Tử: "số phiếu `code` mà …" | Tử có đòi phiếu xong | **D29:** không đòi | Không | `qua_lan_dau` |
| S5 | "bead khe đã code", "sau khi vào cột 3 có `cot.tra_ve`" | Quy cho khe nào; lần vào cột 3 nào | **D27:** mỗi lần vào cột 3 là một mẫu, quy cho khe có phiếu code trong bằng chứng (`giao_id_code`); chỉ tính trả về xảy ra trước lần vào cột 3 kế tiếp | **Có** — bản tạm tính mọi khe từng code bead, so với lần vào cột 3 đầu tiên | `bi_tra_ve` |
| S6 | D14 "30 ngày gần nhất" | Mốc thời gian | **D28:** lúc cấp phiếu (`cap_luc`) | Không | `dieu_kien_phieu`, `doi_ngu` |
| S7 | D14 "theo dự án" | Dự án của phiếu hay sự kiện | **D29:** `phieu.du_an`; sự kiện lọc cùng dự án | Không | `dieu_kien_phieu`, `doc_su_kien` |
| S8 | §12 "tính theo (khe, vai)" | Hai chỉ số cho vai `qc`, `spec` | **D29:** `null` | Không | `bang_diem` |

**Còn mở — không chặn task nào của 2d:**
- **Q1 — Phạm vi "cho SHA" ở D26.** Mã chỉ tìm `kiem.lai` / `qc.ket_qua` **cùng dự án và bead** với phiếu; giữ nguyên phạm vi của S2 tạm, D26 không nói khác. Thực tế hai bead khác nhau gần như không có cùng SHA. Nếu Đại ca muốn tính cả sự kiện của bead khác cùng SHA thì chỉ sửa `_dau_tien`.
- ~~**Q2 — Hàng 0 phiếu trong bảng điểm (cho lát 2f).**~~ → **ĐÃ CHỐT D41** (16/10): đổi API 2d, `bang_diem` trả đủ mọi khe đã khai theo vai ưu tiên (G22, Task 6). 2f đọc thẳng, không ghép phía trình duyệt.

## Hợp đồng JSON (lát 2d)

`GET /api/doi-ngu?du_an=&so_ngay=30` — mỗi phần tử `bang_diem` (G5, G6). Kho phiếu chưa bật thì giữ nguyên `{"bat": false, "khe": [], "luat_vai": null, "bang_diem": []}`.

```json
{"khe_id": "B/claude-1", "vai": "coder", "so_phieu": 10, "so_xong": 9, "lan_chay_tb": 1.5,
 "qua_lan_dau": 0.2222, "qua_lan_dau_mau": 9, "bi_tra_ve": 0.3333, "bi_tra_ve_mau": 3}
{"khe_id": "B/claude-2", "vai": "qc", "so_phieu": 1, "so_xong": 0, "lan_chay_tb": null,
 "qua_lan_dau": null, "qua_lan_dau_mau": null, "bi_tra_ve": null, "bi_tra_ve_mau": null}
{"khe_id": "B/codex-2", "vai": "coder", "so_phieu": 0, "so_xong": 0, "lan_chay_tb": null,
 "qua_lan_dau": null, "qua_lan_dau_mau": 0, "bi_tra_ve": null, "bi_tra_ve_mau": 0}
```

Chú ý:
- `bi_tra_ve_mau` đếm **lần vào cột 3** của khe (D27), không đếm bead.
- Hàng thứ ba là khe đã khai (vai ưu tiên `coder`) chưa có phiếu trong bộ lọc (G22, D41). Mọi (khe, vai ưu tiên) của khe đã khai đều có hàng; vai khác `coder` thì mẫu `null`.

`GET /api/giao-viec` — bead cột 3 khi trạm đã mở PR (G10). Các khoá cũ của `pr` giữ nguyên:

```json
{"bat": true, "giao": {"hr-codex/hr-2": {"khong_giao": null, "pr": {
  "nhanh": "tram/hr-2", "commit": "<40 hex>", "tu_xa": "<40 hex> | null", "lech": false, "link": null,
  "lenh": "gh pr create --base main --head tram/hr-2 --fill",
  "tram": {"so": 7, "url": "https://github.com/hung/hr-codex/pull/7", "trang_thai": "khong_xac_minh",
           "ly_do": "không phải merge commit (squash / rebase)"}}}}}
```

`GET /api/phe-duyet` — mục `cho-review` (G21). Các khoá cũ của `chi_tiet` giữ nguyên:

```json
{"loai": "cho-review", "du_an": "hr-codex", "bead_id": "hr-2", "chi_tiet": {"pr": null, "nhanh": "tram/hr-2", "commit": "<40 hex>",
  "file_ban_giao": "docs/handovers/…", "loi": [],
  "pr_tram": {"so": 7, "url": "https://github.com/hung/hr-codex/pull/7", "trang_thai": "khong_xac_minh",
              "ly_do": "không phải merge commit (squash / rebase)"}}}
```

Telegram (G15):
- `[tram] hr-codex · 1 PR đã merge, trạm xác minh đúng commit đã kiểm (hr-1) → https://may-b.tail.ts.net/`
- `[tram] hr-codex · 1 PR đã merge nhưng trạm không xác minh được, cần Đại ca Duyệt tay (hr-2) → https://may-b.tail.ts.net/`

## Ranh giới 2d ↔ 2f (G20)

**Đại ca đã chốt (D38, Q14 của khảo sát giao diện).**
- Ghép 2d nguyên văn trước 2f, kể cả phần `.vue` nhỏ của Task 2 và Task 5.
- 2f làm lại các file `.vue` đó theo mockup. Luật thuần và backend của 2d giữ nguyên.

Người điều phối từng đề xuất chuyển hẳn phần Vue của 2d sang 2f. Bản này **không** làm theo đề xuất đó, vì D38 đã chốt khác. Chi phí của D38 nhỏ: khoảng 30 dòng `.vue` trên bố cục cũ sẽ bị 2f viết lại. Đổi lại:
- dữ liệu mới hiện được ngay sau khi ghép 2d, không phải chờ 2f;
- ngăn bên không còn gợi `gh pr create` khi trạm đã mở PR.

Vì 2f dùng lại luật thuần nguyên văn, 2d sửa luật thuần cho đúng chữ mockup ngay bây giờ (yêu cầu (a) "bám đúng mockup" áp cho phần 2f giữ lại).

**2d giao cho 2f (không đổi tên/chữ ký nếu không sửa plan 2d):**

| Hợp đồng | Dạng | Dùng ở trang (mockup) |
|---|---|---|
| `GET /api/doi-ngu?du_an=&so_ngay=` | JSON ở trên; mặc định mọi dự án, 30 ngày; 404 / 422 như G5. **`bang_diem` có sẵn hàng 0 phiếu** cho mọi (khe, vai ưu tiên) đã khai (G22, **ĐÃ CHỐT D41**) — 2f đọc thẳng, không ghép phía trình duyệt | Đội ngũ AI — "Bảng điểm thợ" (cả hàng "chưa có") |
| `SO_NGAY_BANG_DIEM`, `duongDanDoiNgu(duAn, soNgay)` | `luat_doi_ngu.js` | nhóm nút 7 / 30 / 92 ngày, ô "Tất cả dự án" |
| `oTiLe(x, mau) -> {chinh, phu}`, `tiLe(x, mau)` | `luat_doi_ngu.js` | ô "Qua lần đầu", "Bị trả về": `chinh` chữ thường, `phu` lớp nhạt (`.nho`) |
| `GET /api/giao-viec` → `giao[k].pr.tram` | JSON ở trên | Công việc (thẻ, ngăn bên) |
| `GET /api/phe-duyet` → mục `cho-review` có `chi_tiet.pr_tram` (Task 7) | JSON ở trên | Phê duyệt — "Chờ review để đóng" (G21) |
| `NHAN_PR_TRAM`, `prTram(the)`, `nhanPrTram(the)`, `lopPrTram(t)` | `giao_viec.js` | chip PR trên thẻ cột 3 và thẻ Phê duyệt; lớp `.pr-*` |
| `moTaPrTram(t)` | `giao_viec.js` | mục "PR" trong ngăn bên: chip + "PR #12 — <lý do>" |
| `canhBaoPrTram(t)` | `giao_viec.js` | khối `.canh-bao` trên thẻ "Chờ review để đóng" |
| SSE `pr.mo`, `pr.khong_xac_minh`, `pr.da_merge` | `LOAI_LAM_MOI` | làm mới thẻ ≤ 10 s |
| Loại tin `pr_da_merge`, `pr_khong_xac_minh` | `NHAN_LOAI` | danh sách loại tin ở trang Cài đặt |

**2d sửa trên bố cục cũ (2f sẽ làm lại):**
- `DoiNgu.vue`: ô chọn dự án và khoảng ngày (G8).
- `TheBead.vue`: nhãn PR.
- `OGiaoViec.vue`: khối PR trạm (G14).

**2f tự làm (theo mockup, cần plan riêng; mockup đã duyệt nên không cần duyệt lại):**
- Đội ngũ AI: bố cục khối "Bảng điểm thợ", nhóm nút thay `<select>`, `oTiLe` in nhạt phần ngoặc. Hàng 0 phiếu **không** làm ở 2f: API 2d đã trả (G22, D41).
- Công việc: chip `.pr-*` trên thẻ; mục "PR" trong ngăn bên.
- Phê duyệt (G21): đọc `chi_tiet.pr_tram` (2d Task 7 đã có), hiện chip PR, link "PR #n ↗", `canhBaoPrTram`, nút đóng theo trạng thái.

## File Structure

```
tram/
  suy/diem_giao_viec.py    # dieu_kien_phieu, doc_phieu_code, doc_su_kien, qua_lan_dau, bi_tra_ve   — Task 1 (mới, 82)
  suy/bang_diem.py         # (sửa) bang_diem(db, *, du_an, tu): lọc + tỉ lệ + cỡ mẫu cho coder      — Task 1 (41)
  suy/doi_ngu.py           # (sửa) doi_ngu(..., du_an, so_ngay=30); SO_NGAY_BANG_DIEM; du_hang_khe — Task 6 (75)
  api/doi_ngu.py           # (sửa) GET /api/doi-ngu?du_an=&so_ngay=                                 — Task 6 (72)
  suy/pr_tram.py           # pr_tram, LY_DO, URL_PR (G10–G13)                                       — Task 3 (mới, 40)
  suy/giao_viec.py         # (sửa) suy_giao gắn pr["tram"]                                           — Task 3 (72)
  api/luong.py             # (sửa) LOAI_LAM_MOI thêm pr.* (G18)                                      — Task 3 (83)
  suy/phe_duyet.py         # (sửa) gan_pr_tram; gom_phe_duyet gắn chi_tiet.pr_tram cho mục cho-review — Task 7 (103)
  bao_tin/tin.py           # (sửa) LOAI_TIN, NHAN_LOAI thêm pr_da_merge, pr_khong_xac_minh           — Task 4 (41)
  bao_tin/nguon.py         # (sửa) TIN_PR; tin_tu_su_kien                                             — Task 4 (52)
frontend/                  # luật thuần giữ nguyên ở 2f; ba file .vue 2f làm lại theo mockup (D38)
  src/luat_doi_ngu.js      # (sửa) SO_NGAY_BANG_DIEM, duongDanDoiNgu, oTiLe, tiLe(x, mau)            — Task 2 (77)
  src/trang/DoiNgu.vue     # (sửa) ô chọn dự án + khoảng; tỉ lệ kèm mẫu; chú thích                    — Task 2 (86)
  src/giao_viec.js         # (sửa) NHAN_PR_TRAM, prTram, nhanPrTram, lopPrTram, moTaPrTram, canhBaoPrTram — Task 5 (49)
  src/thanh/TheBead.vue    # (sửa) nhãn PR trên thẻ                                                   — Task 5 (33)
  src/thanh/OGiaoViec.vue  # (sửa) khối "PR do trạm mở" trong ngăn bên                               — Task 5 (32)
  tests/doi_ngu.test.mjs (Task 2, sửa) · tests/giao_viec.test.mjs (Task 5, sửa)
tests/
  test_bang_diem_4.py (Task 1, mới) · test_suy_doi_ngu.py (Task 1, sửa) · test_the_cot_3_pr.py (Task 3, mới)
  test_bao_tin_pr.py (Task 4, mới) · test_api_doi_ngu_loc.py (Task 6, mới) · test_phe_duyet_pr_tram.py (Task 7, mới)
```

## Chuẩn bị (người điều phối)

```bash
cd "/Users/dai-ca/Developer/Ben Station"
git status --short            # chỉ được có .beads/interactions.jsonl, .DS_Store — không đụng
git log --oneline -1 main     # bản D41 chạy thử trên 503ff64 (mã như 38a016f); khác thì chạy `git apply --check` mọi bản vá trước
uv run pytest -q              # ghi N₀ (lúc viết: 1994)
(cd frontend && npm ci --offline --ignore-scripts && npm run kiem && npm run build && npm run kiem-dist)  # M₀ (33)
```

**Mỗi task một worktree**, tạo từ `main` sau khi đã ghép mọi task của đợt trước:

```bash
N=1   # số task
git worktree add .worktrees/2d-t$N -b 2d/t$N main
cd .worktrees/2d-t$N && uv sync && uv run pytest -q                 # kỳ vọng: số "sau đợt trước" ở Sơ đồ đợt
(cd frontend && npm ci --offline --ignore-scripts)                    # chỉ Task 2, 5
```

**Mã:**
- File **mới**: chép nguyên văn đầy đủ.
- File **có sẵn**: bản vá unified diff, sinh bằng `git diff` trên bản dựng thử `38a016f`. Lưu khối `diff` ra file (vd `../t1.diff`) rồi chạy `git apply --check ../t1.diff && git apply ../t1.diff`. `--check` lỗi thì **dừng** và báo người điều phối; không áp tay đoán mò.

Cuối mỗi task: người thực thi commit trong worktree. Người điều phối kiểm: mọi dòng thêm có nguyên văn trong plan, số test đúng kỳ vọng, file ≤ ~120 dòng. Sau đó `git merge --no-ff 2d/t$N` vào `main` (không push). Ghép xong cả đợt thì chạy lại các lệnh kiểm trên `main`, phải khớp số "sau đợt". Dòng ghi công: thay `<model đang thực thi>` bằng đúng tên model của người thực thi.

---

### Task 1: Bảng điểm — "qua lần đầu", "bị trả về" theo chữ spec và D25–D29, có bộ lọc

**Độ khó:** `vua` · **Đợt:** 1 · **Song song với:** Task 3, 4 · **Phải xong trước:** —

**Files:**
- Create: `tram/suy/diem_giao_viec.py`
- Modify: `tram/suy/bang_diem.py` (docstring, chữ ký và thân `bang_diem`)
- Test: `tests/test_bang_diem_4.py` (mới); `tests/test_suy_doi_ngu.py` (sửa kỳ vọng `test_bang_diem_lan_chay_trung_binh_tren_phieu_da_ket_thuc`)

**Interfaces:**
- Consumes: bảng `phieu`, `su_kien` qua `sqlite3.Connection` (`KhoPhieu.db`); sự kiện `giao.cong_bo`, `kiem.lai`, `qc.ket_qua`, `bead.vao_cot_3` (trường `giao_id_code`), `cot.tra_ve`.
- Produces:
  - `tram/suy/diem_giao_viec.py`:
    - `LOAI`;
    - `dieu_kien_phieu(du_an, tu) -> (sql, tham)`;
    - `doc_phieu_code(db, du_an=None, tu=None) -> [(giao_id, khe_id, du_an, bead_id, luot, ket_thuc)]`;
    - `doc_su_kien(db, du_an=None) -> {loai: [(id, du_an, bead_id, du_lieu)]}`;
    - `qua_lan_dau(phieu, sk) -> {khe_id: (tu, mau)}` (G2: D25, D26, D29);
    - `bi_tra_ve(phieu, sk) -> {khe_id: (tu, mau)}` (G3: D27, D28).
  - `bang_diem(db, *, du_an: str | None = None, tu: str | None = None) -> list[{khe_id, vai, so_phieu, so_xong, lan_chay_tb, qua_lan_dau, qua_lan_dau_mau, bi_tra_ve, bi_tra_ve_mau}]` — đúng "Hợp đồng JSON". Task 6 truyền `du_an`, `tu`; lát 2f đọc các khoá qua `oTiLe` (Task 2).

Ca test chính (G2, G3):
- **Qua lần đầu:** 10 phiếu code của `B/claude-1`, 9 phiếu xong → mẫu 9; qua 2 (`hr-1`, `hr-11`):
  - `hr-1` qua; D25 lấy bản `giao.cong_bo` sau cùng của lượt (`c0` rồi `c1` → dùng `c1`).
  - `hr-2`: QC đầu trả về → không qua.
  - `hr-3`: kiểm lại đầu trượt → không qua.
  - `hr-4`: chưa công bố SHA → không qua, vẫn ở mẫu.
  - `hr-5`: chờ QC → không qua, vẫn ở mẫu.
  - `hr-6`: spike, không có QC → không qua.
  - `hr-7`: kết thúc `bi` → ngoài mẫu.
  - `hr-8`: chỉ có QC của bead khác cùng SHA (Q1) → không qua.
  - `hr-10` (D26): QC `dat` ghi **trước** kiểm lại bị bỏ qua; QC đầu sau kiểm lại là `tra_ve` → không qua.
  - `hr-11` (D26): QC `tra_ve` ghi trước kiểm lại bị bỏ qua; QC đầu sau kiểm lại là `dat` → qua.
- **Bị trả về (D27):** `B/claude-1` 2/3, `B/claude-2` 0/1:
  - Trả về trước mọi lần vào cột 3 → không tính.
  - `hr-1` vào cột 3 lần một (bằng chứng: phiếu của `B/claude-1`), bị trả về hai lần → một mẫu bị trả về của `B/claude-1`.
  - `hr-1` vào cột 3 lần hai (bằng chứng: phiếu của `B/claude-2`), không bị trả về → một mẫu không bị trả về của `B/claude-2`.
  - `hr-2` vào cột 3 hai lần liền rồi mới bị trả về → chỉ lần thứ hai tính bị trả về.
  - `hr-3` có bằng chứng trỏ phiếu không tồn tại → bỏ mẫu. Khe `B/claude-2` có code `hr-3` nhưng không nằm trong bằng chứng → không có mẫu.
- **Bộ lọc (D28, D29):** phiếu cấp 40 ngày trước và phiếu dự án khác bị loại khỏi mọi cột. Mẫu "bị trả về" của chúng cũng bị loại theo phiếu.

- [ ] **Step 1: Viết test thất bại**

`tests/test_bang_diem_4.py` (mới):

```python
"""Bảng điểm thợ — "qua lần đầu", "bị trả về" theo spec 4 §12 + D25–D29; lọc D14, D28 (plan 2d Task 1, G2–G6)."""
from datetime import timedelta

from kho_phieu_gia import LUC, dat_phieu, kho_tam
from tram.phieu.ghi import danh_dau_ket_thuc
from tram.phieu.kho import chuoi_gio
from tram.suy.bang_diem import bang_diem
from tram.suy.diem_giao_viec import bi_tra_ve, doc_phieu_code, doc_su_kien, qua_lan_dau

DA = "hr-codex"


def phieu(kho, khe, bead, i, ket_thuc="xong", luc=LUC, **kw):
    p = dat_phieu(kho, khe, luc=luc + timedelta(minutes=i), bead_id=bead, **kw)
    with kho.giao_dich() as db:
        danh_dau_ket_thuc(db, p.giao_id, ket_thuc, luc)
    return p


def ghi(kho, loai, bead, du_an=DA, **d):
    with kho.giao_dich():
        kho.ghi_su_kien(du_an, loai, d, luc=LUC, bead_id=bead)


def cong_bo(kho, p, commit):
    ghi(kho, "giao.cong_bo", p.bead_id, p.du_an, bead_id=p.bead_id, luot=p.luot, commit=commit)


def kiem(kho, bead, commit, dat=True):
    ghi(kho, "kiem.lai", bead, commit=commit, dat=dat)


def qc(kho, bead, commit, ket_luan):
    ghi(kho, "qc.ket_qua", bead, commit_code=commit, commit_qc="q" + commit, ket_luan=ket_luan)


def vao(kho, bead, giao_id, du_an=DA):
    ghi(kho, "bead.vao_cot_3", bead, du_an, bead_id=bead, giao_id_code=giao_id)


def dung_qua_lan_dau(kho):
    k = "B/claude-1"
    p1, p2, p3, _, p5 = (phieu(kho, k, f"hr-{i}", i) for i in range(1, 6))      # hr-4: chưa công bố SHA, ở mẫu
    p6 = phieu(kho, k, "hr-6", 6, can_lenh_kiem=False, lenh_kiem=[])           # spike: không xử lý riêng
    phieu(kho, k, "hr-7", 7, ket_thuc="bi")                                       # không xong: ngoài mẫu
    p8, p10, p11 = (phieu(kho, k, f"hr-{i}", i) for i in (8, 10, 11))
    phieu(kho, "B/claude-2", "hr-1", 9, buoc="qc")
    cong_bo(kho, p1, "c0")
    cong_bo(kho, p1, "c1")                                                        # D25: bản sau cùng của lượt
    kiem(kho, "hr-1", "c1")
    qc(kho, "hr-1", "c1", "dat")                                                  # qua
    for p, c in ((p2, "c2"), (p3, "c3"), (p5, "c5"), (p6, "c6"), (p8, "c8"), (p10, "c10"), (p11, "c11")):
        cong_bo(kho, p, c)
    kiem(kho, "hr-2", "c2")
    qc(kho, "hr-2", "c2", "tra_ve")                                               # QC đầu trả về
    qc(kho, "hr-2", "c2", "dat")
    kiem(kho, "hr-3", "c3", dat=False)                                            # kiểm lại đầu trượt
    kiem(kho, "hr-3", "c3")
    qc(kho, "hr-3", "c3", "dat")
    kiem(kho, "hr-5", "c5")                                                       # chờ QC: vẫn trong mẫu
    kiem(kho, "hr-6", "c6")                                                       # spike không có QC
    kiem(kho, "hr-8", "c8")
    qc(kho, "hr-9", "c8", "dat")                                                  # QC của bead khác cùng SHA
    qc(kho, "hr-10", "c10", "dat")                                                # D26: QC ghi trước kiểm lại
    kiem(kho, "hr-10", "c10")
    qc(kho, "hr-10", "c10", "tra_ve")                                             # → QC đầu sau kiểm lại trả về
    qc(kho, "hr-11", "c11", "tra_ve")                                             # D26: QC trước kiểm lại bỏ qua
    kiem(kho, "hr-11", "c11")
    qc(kho, "hr-11", "c11", "dat")                                                # → qua


def test_qua_lan_dau_qc_dau_tien_sau_kiem_lai(tmp_path):
    kho = kho_tam(tmp_path)
    dung_qua_lan_dau(kho)
    assert qua_lan_dau(doc_phieu_code(kho.db), doc_su_kien(kho.db)) == {"B/claude-1": (2, 9)}


def test_bi_tra_ve_moi_lan_vao_cot_3_mot_mau_cua_khe_trong_bang_chung(tmp_path):
    kho = kho_tam(tmp_path)
    a, b = phieu(kho, "B/claude-1", "hr-1", 0), phieu(kho, "B/claude-2", "hr-1", 1)
    c = phieu(kho, "B/claude-1", "hr-2", 2)
    phieu(kho, "B/claude-2", "hr-3", 3)                                           # code hr-3 nhưng không ở bằng chứng
    ghi(kho, "cot.tra_ve", "hr-2", gop_y="trước mọi lần vào cột 3")
    vao(kho, "hr-1", a.giao_id)
    ghi(kho, "cot.tra_ve", "hr-1", gop_y="x")
    ghi(kho, "cot.tra_ve", "hr-1", gop_y="lần hai, cùng mẫu")
    vao(kho, "hr-1", b.giao_id)                                                   # vòng mới của khe khác: không bị trả
    vao(kho, "hr-2", c.giao_id)
    vao(kho, "hr-2", c.giao_id)                                                   # vào lại trước khi bị trả về
    ghi(kho, "cot.tra_ve", "hr-2", gop_y="x")                                     # chỉ tính cho lần vào thứ hai
    vao(kho, "hr-3", "khong-co-phieu")
    ghi(kho, "cot.tra_ve", "hr-3", gop_y="x")
    assert bi_tra_ve(doc_phieu_code(kho.db), doc_su_kien(kho.db)) == {"B/claude-1": (2, 3), "B/claude-2": (0, 1)}


def test_loc_du_an_va_cua_so_theo_luc_cap_phieu(tmp_path):
    kho = kho_tam(tmp_path)
    phieu(kho, "B/claude-1", "hr-1", 1)
    p2 = phieu(kho, "B/claude-1", "hr-2", 2, luc=LUC - timedelta(days=40))
    p3 = phieu(kho, "B/claude-1", "hr-3", 3, du_an="hr-khac")
    for p in (p2, p3):
        vao(kho, p.bead_id, p.giao_id, p.du_an)
        ghi(kho, "cot.tra_ve", p.bead_id, p.du_an, gop_y="x")
    tu = chuoi_gio(LUC - timedelta(days=30))
    (h,) = bang_diem(kho.db, du_an=DA, tu=tu)
    assert (h["so_phieu"], h["so_xong"], h["qua_lan_dau_mau"], h["bi_tra_ve"], h["bi_tra_ve_mau"]) == (1, 1, 1, None, 0)
    (h,) = bang_diem(kho.db, tu=tu)
    assert (h["so_phieu"], h["bi_tra_ve"], h["bi_tra_ve_mau"]) == (2, 1.0, 1)
    (h,) = bang_diem(kho.db)
    assert (h["so_phieu"], h["qua_lan_dau_mau"], h["bi_tra_ve"], h["bi_tra_ve_mau"]) == (3, 3, 1.0, 2)


def test_bang_diem_gan_ti_le_va_mau_chi_cho_coder(tmp_path):
    kho = kho_tam(tmp_path)
    dung_qua_lan_dau(kho)
    h1, h2 = bang_diem(kho.db)
    assert (h1["khe_id"], h1["vai"], h1["so_phieu"], h1["so_xong"]) == ("B/claude-1", "coder", 10, 9)
    assert (h1["qua_lan_dau"], h1["qua_lan_dau_mau"], h1["bi_tra_ve"], h1["bi_tra_ve_mau"]) == (0.2222, 9, None, 0)
    assert (h2["vai"], h2["qua_lan_dau"], h2["qua_lan_dau_mau"], h2["bi_tra_ve"], h2["bi_tra_ve_mau"]) == (
        "qc", None, None, None, None)
```

`tests/test_suy_doi_ngu.py` — kỳ vọng mới của hàng bảng điểm cũ. Một phiếu code xong, chưa có SHA công bố → qua lần đầu 0/1 (D25). Không có lần vào cột 3 → bị trả về `null`, mẫu 0. Vai `qc` để `null` (D29):

```diff
diff --git a/tests/test_suy_doi_ngu.py b/tests/test_suy_doi_ngu.py
--- a/tests/test_suy_doi_ngu.py
+++ b/tests/test_suy_doi_ngu.py
@@ -63,6 +63,6 @@ def test_bang_diem_lan_chay_trung_binh_tren_phieu_da_ket_thuc(tmp_path):
     dat_phieu(kho, "B/claude-2", bead_id="hr-9", buoc="qc")
     assert bang_diem(kho.db) == [
         {"khe_id": "B/claude-1", "vai": "coder", "so_phieu": 3, "so_xong": 1, "lan_chay_tb": 2.0,
-         "qua_lan_dau": None, "bi_tra_ve": None},
+         "qua_lan_dau": 0.0, "qua_lan_dau_mau": 1, "bi_tra_ve": None, "bi_tra_ve_mau": 0},
         {"khe_id": "B/claude-2", "vai": "qc", "so_phieu": 1, "so_xong": 0, "lan_chay_tb": None,
-         "qua_lan_dau": None, "bi_tra_ve": None}]
+         "qua_lan_dau": None, "qua_lan_dau_mau": None, "bi_tra_ve": None, "bi_tra_ve_mau": None}]
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_bang_diem_4.py -q`
Expected: FAIL — `1 error` (`ModuleNotFoundError: No module named 'tram.suy.diem_giao_viec'`)

Run: `uv run pytest tests/test_suy_doi_ngu.py -q`
Expected: FAIL — `1 failed, 2 passed` (dict thiếu `qua_lan_dau_mau`, `bi_tra_ve_mau`)

- [ ] **Step 3: Viết mã**

`tram/suy/diem_giao_viec.py` (mới):

```python
"""Hai chỉ số của bảng điểm thợ cần sự kiện phần 4 — theo chữ spec 4 §12 (D13) và các câu Đại ca chốt D25–D29
(15/10). Tính lúc đọc (Q12) theo khe, cho phiếu `code` (vai `coder`); lọc theo dự án và lúc cấp phiếu (D14, D28).

*Qua lần đầu* = số phiếu `code` mà `kiem.lai` đầu tiên cho SHA của phiếu đạt VÀ `qc.ket_qua` đầu tiên cho commit
đó, ghi SAU lần kiểm lại ấy (D26), là `dat` ÷ số phiếu `code` kết thúc `xong`.
*Bị trả về* (D27) = mỗi lần `bead.vao_cot_3` là một mẫu của khe giữ phiếu code trong bằng chứng (`giao_id_code`);
mẫu bị trả về khi có `cot.tra_ve` của bead trước lần vào cột 3 kế tiếp ÷ số mẫu."""
import json
import sqlite3
from collections import defaultdict

LOAI = ("giao.cong_bo", "kiem.lai", "qc.ket_qua", "bead.vao_cot_3", "cot.tra_ve")


def dieu_kien_phieu(du_an: str | None, tu: str | None) -> tuple[str, list]:
    """Mảnh WHERE cho bảng `phieu`. D29: dự án = `phieu.du_an`. D28: thuộc cửa sổ khi `cap_luc` ≥ `tu` (UTC)."""
    sql, tham = "", []
    if du_an:
        sql, tham = sql + " AND du_an = ?", tham + [du_an]
    if tu:
        sql, tham = sql + " AND cap_luc >= ?", tham + [tu]
    return sql, tham


def doc_phieu_code(db: sqlite3.Connection, du_an: str | None = None, tu: str | None = None) -> list[tuple]:
    """[(giao_id, khe_id, du_an, bead_id, luot, ket_thuc)] của phiếu `code`. D29: "kết thúc xong" = `phieu.ket_thuc`."""
    loc, tham = dieu_kien_phieu(du_an, tu)
    return db.execute("SELECT giao_id, khe_id, du_an, bead_id, luot, ket_thuc FROM phieu"
                      f" WHERE json_extract(noi_dung, '$.buoc') = 'code'{loc} ORDER BY giao_id", tham).fetchall()


def doc_su_kien(db: sqlite3.Connection, du_an: str | None = None) -> dict[str, list[tuple]]:
    """{loai: [(id, du_an, bead_id, du_lieu), …]} theo thứ tự ghi. Sự kiện đi theo phiếu, không lọc thời gian (D28)."""
    loc, tham = (" AND du_an = ?", [du_an]) if du_an else ("", [])
    ra: dict[str, list[tuple]] = defaultdict(list)
    for i, a, b, loai, d in db.execute(
            f"SELECT id, du_an, bead_id, loai, du_lieu FROM su_kien WHERE loai IN ({','.join('?' * len(LOAI))}){loc}"
            " ORDER BY id", (*LOAI, *tham)):
        ra[loai].append((i, a, b, json.loads(d)))
    return ra


def _dau_tien(ds: list[tuple], du_an: str, bead_id: str, khoa: str, sha: str, sau: int = 0) -> tuple | None:
    """(id, du_lieu) ghi sớm nhất cùng dự án + bead, có `khoa` = `sha`, id lớn hơn `sau`."""
    return next(((i, d) for i, a, b, d in ds if i > sau and (a, b) == (du_an, bead_id) and d.get(khoa) == sha), None)


def qua_lan_dau(phieu: list[tuple], sk: dict[str, list[tuple]]) -> dict[str, tuple[int, int]]:
    """{khe_id: (tử, mẫu)}. D25: SHA của phiếu = `commit` của `giao.cong_bo` cùng dự án, bead và `luot` (bản sau cùng);
    chưa công bố → không vào tử, vẫn ở mẫu. D26: `kiem.lai` sớm nhất có đúng SHA, rồi `qc.ket_qua` sớm nhất cho cùng
    commit ghi sau lần kiểm lại ấy. D29: tử không đòi phiếu `xong`."""
    cong_bo = {(a, b, d.get("luot")): d.get("commit") for _, a, b, d in sk["giao.cong_bo"]}
    dem: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for _, khe, a, b, luot, ket_thuc in phieu:
        x = dem[khe]
        x[1] += ket_thuc == "xong"
        if (sha := cong_bo.get((a, b, luot))) is None:
            continue
        kl = _dau_tien(sk["kiem.lai"], a, b, "commit", sha)
        qc = kl and _dau_tien(sk["qc.ket_qua"], a, b, "commit_code", sha, sau=kl[0])
        x[0] += bool(qc and kl[1].get("dat") is True and qc[1].get("ket_luan") == "dat")
    return {k: (tu, mau) for k, (tu, mau) in dem.items()}


def bi_tra_ve(phieu: list[tuple], sk: dict[str, list[tuple]]) -> dict[str, tuple[int, int]]:
    """{khe_id: (tử, mẫu)}. D27: mỗi `bead.vao_cot_3` là một mẫu, quy cho khe của phiếu `giao_id_code` trong bằng chứng
    (phiếu ngoài bộ lọc → bỏ mẫu). Bị trả về khi sự kiện kế tiếp của bead (trong hai loại) là `cot.tra_ve`, tức trả
    về xảy ra trước lần vào cột 3 kế tiếp."""
    khe_cua = {g: khe for g, khe, *_ in phieu}
    dong: dict[tuple, list[tuple]] = defaultdict(list)
    for loai in ("bead.vao_cot_3", "cot.tra_ve"):
        for i, a, b, d in sk[loai]:
            dong[(a, b)].append((i, loai, d.get("giao_id_code")))
    dem: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for ds in dong.values():
        ds.sort()
        for j, (_, loai, g) in enumerate(ds):
            if loai == "bead.vao_cot_3" and g in khe_cua:
                x = dem[khe_cua[g]]
                x[1] += 1
                x[0] += j + 1 < len(ds) and ds[j + 1][1] == "cot.tra_ve"
    return {k: (tu, mau) for k, (tu, mau) in dem.items()}
```

`tram/suy/bang_diem.py`:

```diff
diff --git a/tram/suy/bang_diem.py b/tram/suy/bang_diem.py
--- a/tram/suy/bang_diem.py
+++ b/tram/suy/bang_diem.py
@@ -1,23 +1,41 @@
-"""Bảng điểm thợ theo (khe, vai) — spec 2 §5.4; công thức ở spec 4 §12 (spec 4 CHƯA DUYỆT).
+"""Bảng điểm thợ theo (khe, vai) — spec 2 §5.4; công thức ở spec 4 §12.
 
-Lát 2b chỉ tính phần có sẵn trong kho phiếu của phần 3: số phiếu, số phiếu kết thúc `xong`, và *số lần chạy trung
-bình* = trung bình số `chay.bat_dau` (bảng `lan_chay`, duy nhất theo `request_id`) trên các phiếu ĐÃ kết thúc.
-*Qua lần đầu* và *bị trả về* cần `kiem.lai`, `qc.ket_qua`, `bead.vao_cot_3` của phần 4 → luôn None ở 2b
-(plan 2b mục "Để sau")."""
+Từ kho phiếu của phần 3: số phiếu, số phiếu kết thúc `xong`, và *số lần chạy trung bình* = trung bình số
+`chay.bat_dau` (bảng `lan_chay`, duy nhất theo `request_id`) trên các phiếu ĐÃ kết thúc. *Qua lần đầu* và *bị trả
+về* (lát 2d) tính từ sự kiện phần 4 trong `tram/suy/diem_giao_viec.py`, chỉ cho vai `coder`; kèm cỡ mẫu `*_mau`.
+Mẫu 0 → tỉ lệ `null` (không hiện 0 giả); vai khác → tỉ lệ và mẫu đều `null` (D29).
+Lọc (D14): `du_an` (None = mọi dự án) và `tu` (UTC; None = từ đầu) áp cho MỌI cột, theo phiếu (D28, D29)."""
 import sqlite3
 
+from tram.suy.diem_giao_viec import bi_tra_ve, dieu_kien_phieu, doc_phieu_code, doc_su_kien, qua_lan_dau
 
-def bang_diem(db: sqlite3.Connection) -> list[dict]:
+
+def _ti_le(x: tuple[int, int]) -> tuple[float | None, int]:
+    tu, mau = x
+    return (round(tu / mau, 4) if mau else None), mau
+
+
+def bang_diem(db: sqlite3.Connection, *, du_an: str | None = None, tu: str | None = None) -> list[dict]:
     lan = dict(db.execute("SELECT giao_id, COUNT(*) FROM lan_chay GROUP BY giao_id").fetchall())
+    loc, tham = dieu_kien_phieu(du_an, tu)
     nhom: dict[tuple[str, str], dict] = {}
     for giao_id, khe_id, vai, trang_thai, ket_thuc in db.execute(
             "SELECT giao_id, khe_id, json_extract(noi_dung, '$.vai'), trang_thai, ket_thuc"
-            " FROM phieu ORDER BY giao_id"):
+            f" FROM phieu WHERE 1 = 1{loc} ORDER BY giao_id", tham):
         x = nhom.setdefault((khe_id, vai), {"so_phieu": 0, "so_xong": 0, "lan": []})
         x["so_phieu"] += 1
         x["so_xong"] += ket_thuc == "xong"
         if trang_thai == "ket_thuc":
             x["lan"].append(lan.get(giao_id, 0))
-    return [{"khe_id": k, "vai": v, "so_phieu": x["so_phieu"], "so_xong": x["so_xong"],
+    phieu, sk = doc_phieu_code(db, du_an, tu), doc_su_kien(db, du_an)
+    qld, btv = qua_lan_dau(phieu, sk), bi_tra_ve(phieu, sk)
+    ra = []
+    for (k, v), x in sorted(nhom.items()):
+        h = {"khe_id": k, "vai": v, "so_phieu": x["so_phieu"], "so_xong": x["so_xong"],
              "lan_chay_tb": round(sum(x["lan"]) / len(x["lan"]), 2) if x["lan"] else None,
-             "qua_lan_dau": None, "bi_tra_ve": None} for (k, v), x in sorted(nhom.items())]
+             "qua_lan_dau": None, "qua_lan_dau_mau": None, "bi_tra_ve": None, "bi_tra_ve_mau": None}
+        if v == "coder":
+            h["qua_lan_dau"], h["qua_lan_dau_mau"] = _ti_le(qld.get(k, (0, 0)))
+            h["bi_tra_ve"], h["bi_tra_ve_mau"] = _ti_le(btv.get(k, (0, 0)))
+        ra.append(h)
+    return ra
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_bang_diem_4.py tests/test_suy_doi_ngu.py tests/test_api_doi_ngu.py -q`
Expected: `12 passed`

Run: `uv run pytest -q`
Expected: `N₀ + 4 passed` (1998 trên bản dựng thử)

- [ ] **Step 5: Commit**

```bash
git add tram/suy/diem_giao_viec.py tram/suy/bang_diem.py tests/test_bang_diem_4.py tests/test_suy_doi_ngu.py
git commit -m "feat(suy): bảng điểm thợ tính qua lần đầu và bị trả về theo chữ spec 4 §12 và D25–D29, kèm cỡ mẫu, lọc dự án + lúc cấp phiếu (D13, D14; plan 2d G2–G6; bs-urj.6)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 2: Frontend — luật bảng điểm theo mockup; ô lọc và tỉ lệ kèm cỡ mẫu trên trang cũ

**Độ khó:** `de` · **Đợt:** 2 · **Song song với:** Task 5, 6 · **Phải xong trước:** Task 1 (hợp đồng `*_mau`); dùng tham số API của Task 6 (cùng đợt, chỉ dựa vào hợp đồng)

**Phạm vi (D38):** luật thuần trong `luat_doi_ngu.js` là phần 2f giữ nguyên, nên theo đúng chữ mockup. Phần `DoiNgu.vue` sửa nhỏ trên bố cục cũ; 2f làm lại theo mockup (nhóm nút 7/30/92, phần ngoặc in nhạt).

**Files:**
- Modify: `frontend/src/luat_doi_ngu.js` (`SO_NGAY_BANG_DIEM`, `duongDanDoiNgu`, `oTiLe`, `tiLe`), `frontend/src/trang/DoiNgu.vue` (ô chọn, hai ô tỉ lệ, chú thích)
- Test: `frontend/tests/doi_ngu.test.mjs` (sửa một kỳ vọng, thêm hai test)

**Interfaces:**
- Consumes: `GET /api/doi-ngu?du_an=&so_ngay=` (Task 6, G5); `bang_diem[].qua_lan_dau`, `.qua_lan_dau_mau`, `.bi_tra_ve`, `.bi_tra_ve_mau` (Task 1, G6); `GET /api/du-an`.
- Produces (giữ nguyên cho lát 2f, G7): `SO_NGAY_BANG_DIEM = [7, 30, 92]`; `duongDanDoiNgu(duAn, soNgay) -> string`; `oTiLe(x, mau?) -> {chinh, phu}`; `tiLe(x, mau?) -> string`. Chữ theo `tiLe` của mockup (`chung.js`): `71%` + `(5/7)`, `chưa có`, `—`.

- [ ] **Step 1: Viết test thất bại**

`frontend/tests/doi_ngu.test.mjs`:

```diff
diff --git a/frontend/tests/doi_ngu.test.mjs b/frontend/tests/doi_ngu.test.mjs
--- a/frontend/tests/doi_ngu.test.mjs
+++ b/frontend/tests/doi_ngu.test.mjs
@@ -2,6 +2,7 @@ import assert from 'node:assert/strict'
 import { test } from 'node:test'
 import { CANH_BAO_HAN_MUC, dinhDangSo, dinhDangUsd, khoaMuc, lyDoCauDao, moTaCuaSo, nhanTrangThai, nutKhe, tenNguon, tiLe }
   from '../src/luat_doi_ngu.js'
+import { SO_NGAY_BANG_DIEM, duongDanDoiNgu, oTiLe } from '../src/luat_doi_ngu.js'
 
 test('nhãn trạng thái: cầu dao ngắt thắng trạng thái suy', () => {
   assert.equal(nhanTrangThai({ trang_thai: 'lam', cau_dao: { ngat: false } }), 'Đang làm')
@@ -41,7 +42,17 @@ test('định dạng số, USD, nguồn, tỉ lệ', () => {
   assert.equal(tenNguon('cham-cot'), 'Bộ chấm cột (Claude API)')
   assert.equal(tenNguon('B/claude-1'), 'B/claude-1')
   assert.equal(tiLe(0.5), '50%')
-  assert.equal(tiLe(null), 'chờ phần 4')
+  assert.equal(tiLe(null), '—')
+})
+
+test('ô tỉ lệ bảng điểm kèm (tử/mẫu) như mockup Đội ngũ AI; mẫu 0 không hiện 0% giả', () => {
+  assert.equal(tiLe(0.7143, 7), '71% (5/7)')
+  assert.equal(tiLe(0, 6), '0% (0/6)')
+  assert.equal(tiLe(null, 0), 'chưa có')
+  assert.equal(tiLe(null, null), '—')
+  assert.deepEqual(oTiLe(0.5, 2), { chinh: '50%', phu: '(1/2)' })
+  assert.deepEqual(oTiLe(null, 0), { chinh: 'chưa có', phu: '' })
+  assert.deepEqual(oTiLe(1, undefined), { chinh: '100%', phu: '' })
 })
 
 test('khoá mục Phê duyệt không trùng giữa các mục hệ', () => {
@@ -50,3 +61,10 @@ test('khoá mục Phê duyệt không trùng giữa các mục hệ', () => {
   assert.notEqual(a, b)
   assert.equal(khoaMuc({ loai: 'cho-review', du_an: 'hr', bead_id: 'hr-1', chi_tiet: {} }), 'cho-review/hr/hr-1//')
 })
+
+test('đường dẫn bảng điểm: mặc định mọi dự án, 30 ngày; mã hoá tên dự án', () => {
+  assert.deepEqual(SO_NGAY_BANG_DIEM, [7, 30, 92])
+  assert.equal(duongDanDoiNgu('', 30), '/api/doi-ngu?du_an=&so_ngay=30')
+  assert.equal(duongDanDoiNgu('hr-codex', 7), '/api/doi-ngu?du_an=hr-codex&so_ngay=7')
+  assert.equal(duongDanDoiNgu('a&b', undefined), '/api/doi-ngu?du_an=a%26b&so_ngay=30')
+})
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `cd frontend && npm run kiem`
Expected: FAIL — `SyntaxError: The requested module '../src/luat_doi_ngu.js' does not provide an export named 'SO_NGAY_BANG_DIEM'`; `ℹ tests 28` · `ℹ pass 27` · `ℹ fail 1` (trên main sau đợt 1, M₀ = 33: cả file `doi_ngu.test.mjs` tính là một test lỗi)

- [ ] **Step 3: Viết mã**

`frontend/src/luat_doi_ngu.js`:

```diff
diff --git a/frontend/src/luat_doi_ngu.js b/frontend/src/luat_doi_ngu.js
--- a/frontend/src/luat_doi_ngu.js
+++ b/frontend/src/luat_doi_ngu.js
@@ -52,8 +52,23 @@ export function tenNguon(khoa) {
   return TEN_NGUON[khoa] ?? khoa
 }
 
-export function tiLe(x) {
-  return typeof x === 'number' ? `${(x * 100).toFixed(0)}%` : 'chờ phần 4'
+// Bảng điểm (lát 2d, D14; mockup Đội ngũ AI đã duyệt D20): lọc theo dự án ('' = mọi dự án) + số ngày, mặc định 30.
+export const SO_NGAY_BANG_DIEM = [7, 30, 92]
+export function duongDanDoiNgu(duAn, soNgay) {
+  return `/api/doi-ngu?du_an=${encodeURIComponent(duAn || '')}&so_ngay=${Number.isInteger(soNgay) ? soNgay : 30}`
+}
+
+// Ô tỉ lệ bảng điểm, tách hai phần để giao diện (lát 2f) tô "(tử/mẫu)" nhạt như mockup mà không chèn HTML.
+// `mau` = cỡ mẫu từ server: null + mẫu 0 → "chưa có"; null không có mẫu (vai khác coder) → "—".
+export function oTiLe(x, mau) {
+  if (typeof x !== 'number') return { chinh: mau === 0 ? 'chưa có' : '—', phu: '' }
+  const phu = Number.isInteger(mau) && mau > 0 ? `(${Math.round(x * mau)}/${mau})` : ''
+  return { chinh: `${Math.round(x * 100)}%`, phu }
+}
+
+export function tiLe(x, mau) {
+  const o = oTiLe(x, mau)
+  return o.phu ? `${o.chinh} ${o.phu}` : o.chinh
 }
 
 // Khoá v-for của mục Phê duyệt: mục "Hệ cần xem" không gắn bead có thể trùng (du_an, bead_id).
```

`frontend/src/trang/DoiNgu.vue`:

```diff
diff --git a/frontend/src/trang/DoiNgu.vue b/frontend/src/trang/DoiNgu.vue
--- a/frontend/src/trang/DoiNgu.vue
+++ b/frontend/src/trang/DoiNgu.vue
@@ -2,26 +2,33 @@
 import { onMounted, onUnmounted, ref, watch } from 'vue'
 import { doc } from '../api.js'
 import { kho } from '../kho.js'
-import { dinhDangSo, tiLe } from '../luat_doi_ngu.js'
+import { SO_NGAY_BANG_DIEM, dinhDangSo, duongDanDoiNgu, tiLe } from '../luat_doi_ngu.js'
 import TheKhe from '../thanh/TheKhe.vue'
 
 // Nhịp tim không phải sự kiện (spec 3 §10) → "mất kết nối" chỉ thấy khi tải lại; tải lại mỗi 5 giây (G15).
 const CHU_KY_MS = 5000
 const dl = ref(null)
 const loi = ref('')
+const duAn = ref('')                      // D14: bảng điểm lọc theo dự án + số ngày; mặc định mọi dự án, 30 ngày
+const soNgay = ref(30)
+const dsDuAn = ref([])
 let hen = null
 
 async function tai() {
   try {
-    dl.value = await doc('/api/doi-ngu')
+    dl.value = await doc(duongDanDoiNgu(duAn.value, soNgay.value))
     loi.value = ''
   } catch (e) {
     loi.value = e.message
   }
 }
-onMounted(() => { tai(); hen = setInterval(tai, CHU_KY_MS) })
+onMounted(async () => {
+  tai()
+  hen = setInterval(tai, CHU_KY_MS)
+  try { dsDuAn.value = (await doc('/api/du-an')).du_an.map((d) => d.ten) } catch (e) { loi.value = e.message }
+})
 onUnmounted(() => clearInterval(hen))
-watch(() => kho.phienBanDoiNgu, tai)
+watch([() => kho.phienBanDoiNgu, duAn, soNgay], tai)
 </script>
 
 <template>
@@ -40,9 +47,20 @@ watch(() => kho.phienBanDoiNgu, tai)
         <span v-for="(vai, buoc) in dl.luat_vai.vai_cua_buoc" :key="buoc" class="nhan-nho">{{ buoc }} → {{ vai }}</span></p>
       <ul class="nho"><li v-for="l in dl.luat_vai.luat" :key="l">{{ l }}</li></ul>
     </template>
-    <template v-if="dl && dl.bang_diem.length">
+    <template v-if="dl && dl.bat">
       <h2>Bảng điểm thợ</h2>
-      <div class="bang-cuon">
+      <div class="cong-cu">
+        <label>Dự án
+          <select v-model="duAn"><option value="">Tất cả</option>
+            <option v-for="d in dsDuAn" :key="d" :value="d">{{ d }}</option></select>
+        </label>
+        <label>Khoảng
+          <select v-model.number="soNgay">
+            <option v-for="n in SO_NGAY_BANG_DIEM" :key="n" :value="n">{{ n }} ngày gần nhất</option></select>
+        </label>
+      </div>
+      <p v-if="!dl.bang_diem.length" class="nho">Không có phiếu nào được cấp trong khoảng này.</p>
+      <div v-else class="bang-cuon">
         <table>
           <thead><tr>
             <th scope="col">Khe</th><th scope="col">Vai</th><th scope="col">Số phiếu</th><th scope="col">Xong</th>
@@ -51,11 +69,14 @@ watch(() => kho.phienBanDoiNgu, tai)
           <tbody><tr v-for="d in dl.bang_diem" :key="d.khe_id + '/' + d.vai">
             <th scope="row">{{ d.khe_id }}</th><td>{{ d.vai }}</td><td>{{ d.so_phieu }}</td><td>{{ d.so_xong }}</td>
             <td>{{ d.lan_chay_tb == null ? '—' : dinhDangSo(d.lan_chay_tb) }}</td>
-            <td>{{ tiLe(d.qua_lan_dau) }}</td><td>{{ tiLe(d.bi_tra_ve) }}</td>
+            <td>{{ tiLe(d.qua_lan_dau, d.qua_lan_dau_mau) }}</td><td>{{ tiLe(d.bi_tra_ve, d.bi_tra_ve_mau) }}</td>
           </tr></tbody>
         </table>
       </div>
-      <p class="nho">"Qua lần đầu" và "Bị trả về" cần kết quả kiểm lại / QC của bộ giao việc (phần 4).</p>
+      <p class="nho">Tính theo phiếu được cấp trong khoảng đã chọn. Hai cột cuối chỉ cho vai coder (spec 4 §12,
+        D25–D29). "Qua lần đầu": lần kiểm lại đầu cho SHA của phiếu đạt và lần QC đầu sau đó đạt, chia cho số phiếu
+        code xong (phiếu còn chờ QC vẫn ở mẫu). "Bị trả về": mỗi lần bead vào cột 3 bằng phiếu của khe là một mẫu;
+        bị Đại ca trả về trước lần vào cột 3 kế tiếp thì tính. Ngoặc: (số đếm / cỡ mẫu).</p>
     </template>
   </section>
 </template>
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `cd frontend && npm run kiem && npm run build && npm run kiem-dist`
Expected: `ℹ tests 35` · `ℹ fail 0` (M₀ + 2); `kiem-an-toan: … không có chèn HTML thô`; `✓ built`; `kiem-dist` xanh. `wc -l src/trang/DoiNgu.vue` = 86.

Run: `uv run pytest -q` → không đổi do task này.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/luat_doi_ngu.js frontend/src/trang/DoiNgu.vue frontend/tests/doi_ngu.test.mjs
git commit -m "feat(frontend): bảng điểm thợ có ô chọn dự án + khoảng ngày (mặc định 30), tỉ lệ kèm cỡ mẫu theo chữ mockup (spec 2 §5.4; D14, D38; plan 2d G7, G8)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 3: Thẻ cột 3 — trạng thái PR do trạm mở trong `/api/giao-viec` + SSE

**Độ khó:** `de` · **Đợt:** 1 · **Song song với:** Task 1, 4 · **Phải xong trước:** —

**Files:**
- Create: `tram/suy/pr_tram.py`
- Modify: `tram/suy/giao_viec.py` (import, `suy_giao`), `tram/api/luong.py` (`LOAI_LAM_MOI`)
- Test: `tests/test_the_cot_3_pr.py` (mới)

**Interfaces:**
- Consumes: `KhoSuKien.moi_nhat(du_an, bead_id, loai, *, dieu_kien)`; sự kiện `bead.vao_cot_3`, `pr.mo`, `pr.khong_xac_minh`, `pr.da_merge` (4c). Ở `suy_giao`, `vc3` là `SuKien` (có `id`, `du_lieu`).
- Produces:
  - `tram/suy/pr_tram.py`: `URL_PR`, `LY_DO: dict[str, str]`, `LY_DO_KHAC`, `pr_tram(kho, du_an, bead_id, vao_cot_3: SuKien) -> {so, url, trang_thai, ly_do} | None`.
  - `suy_giao(...)[k]["pr"]["tram"]` (G10). Task 5 và lát 2f dựa vào khoá này; Task 7 dùng lại `pr_tram` cho trang Phê duyệt (G21).
  - `LOAI_LAM_MOI` chứa `pr.mo`, `pr.khong_xac_minh`, `pr.da_merge`.

- [ ] **Step 1: Viết test thất bại**

`tests/test_the_cot_3_pr.py` (mới):

```python
"""Thẻ cột 3 hiện PR do trạm mở và `pr.khong_xac_minh` (spec 2 §5.2, spec 4 §6.5; plan 2d Task 3, G10–G13, G16)."""
from bd_gia import BdGia
from bead_gia import bead
from giao_viec_gia import bug, du_an_gia
from tram.api.bo_dem import BoDemBeads
from tram.api.luong import TrangThaiLuong, mot_nhip
from tram.su_kien.kho import KhoSuKien
from tram.suy.giao_viec import suy_giao
from tram.suy.pr_tram import LY_DO, LY_DO_KHAC, pr_tram

DA, C1, C2 = "hr-codex", "a" * 40, "b" * 40
URL = "https://github.com/hung/hr-codex/pull/7"


def ghi(kho, ten, **d):
    kho.ghi(DA, ten, d, bead_id="hr-2", tac_nhan="tram/giao-viec")


def vc3(kho):
    return kho.moi_nhat(DA, "hr-2", "bead.vao_cot_3")


def test_pr_tram_chi_tinh_su_kien_sau_lan_vao_cot_3_hien_tai(tmp_path):
    kho = KhoSuKien(tmp_path / "sk.db")
    ghi(kho, "bead.vao_cot_3", commit_ban_giao=C1)
    assert pr_tram(kho, DA, "hr-2", vc3(kho)) is None                            # trạm chưa mở PR
    ghi(kho, "pr.mo", loai="bead", pr=7, url=URL, commit=C1)
    assert pr_tram(kho, DA, "hr-2", vc3(kho)) == {"so": 7, "url": URL, "trang_thai": "mo", "ly_do": None}
    ghi(kho, "pr.khong_xac_minh", pr=7, commit=C1, ly_do="khong-phai-merge-commit")
    assert pr_tram(kho, DA, "hr-2", vc3(kho)) == {"so": 7, "url": URL, "trang_thai": "khong_xac_minh",
                                                 "ly_do": LY_DO["khong-phai-merge-commit"]}
    ghi(kho, "cot.tra_ve", gop_y="x")
    ghi(kho, "bead.vao_cot_3", commit_ban_giao=C2)                               # vòng mới: PR cũ không dính
    assert pr_tram(kho, DA, "hr-2", vc3(kho)) is None
    ghi(kho, "pr.mo", loai="bead", pr=8, url=URL[:-1] + "8", commit=C1)          # PR của commit khác
    assert pr_tram(kho, DA, "hr-2", vc3(kho)) is None


def test_pr_tram_loc_du_lieu_la_va_da_merge(tmp_path):
    kho = KhoSuKien(tmp_path / "sk.db")
    ghi(kho, "bead.vao_cot_3", commit_ban_giao=C1)
    ghi(kho, "pr.mo", loai="spec", pr=3, url=URL, commit=C1)                     # PR spec của feature: bỏ
    assert pr_tram(kho, DA, "hr-2", vc3(kho)) is None
    ghi(kho, "pr.mo", loai="bead", pr="7", url="javascript:alert(1)", commit=C1)
    ghi(kho, "pr.khong_xac_minh", pr=7, commit=C1, ly_do="<b>lạ</b>")
    assert pr_tram(kho, DA, "hr-2", vc3(kho)) == {"so": None, "url": None, "trang_thai": "khong_xac_minh",
                                                 "ly_do": LY_DO_KHAC}
    ghi(kho, "pr.da_merge", pr=7, url=URL, commit=C1, merge_commit=C2, nhanh_chinh="main", ma_thao_tac="pr-1")
    assert pr_tram(kho, DA, "hr-2", vc3(kho))["trang_thai"] == "da_merge"


def test_suy_giao_gan_pr_tram_vao_the_cot_3(tmp_path):
    kho, da = KhoSuKien(tmp_path / "sk.db"), du_an_gia(tmp_path)
    ghi(kho, "bead.vao_cot_3", commit_ban_giao=C1)
    ghi(kho, "pr.mo", loai="bead", pr=7, url=URL, commit=C1)
    ghi(kho, "pr.khong_xac_minh", pr=7, commit=C1, ly_do="head-khac-commit-ban-giao")
    g = suy_giao(da, [bug("hr-1", labels=["cot:can-chot"]), bug("hr-2", labels=["cot:cho-review"])], kho, None)
    assert list(g) == ["hr-codex/hr-2"]
    assert g["hr-codex/hr-2"]["pr"]["commit"] == C1
    assert g["hr-codex/hr-2"]["pr"]["tram"] == {"so": 7, "url": URL, "trang_thai": "khong_xac_minh",
                                                "ly_do": LY_DO["head-khac-commit-ban-giao"]}


def test_su_kien_pr_lam_moi_bang_qua_sse(tmp_path):
    kho, bo = KhoSuKien(tmp_path / "sk.db"), BoDemBeads(lambda ten: BdGia([bead("hr-2")]))
    tt = TrangThaiLuong(moc=0)
    mot_nhip(kho, bo, [DA], tt)
    ghi(kho, "pr.khong_xac_minh", pr=7, commit=C1, ly_do="khong-phai-merge-commit")
    ra = mot_nhip(kho, bo, [DA], tt)
    assert ra[0].startswith("event: su_kien") and ra[-1].startswith("event: phe_duyet_doi")
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_the_cot_3_pr.py -q`
Expected: FAIL — `1 error` (`ModuleNotFoundError: No module named 'tram.suy.pr_tram'`)

- [ ] **Step 3: Viết mã**

`tram/suy/pr_tram.py` (mới):

```python
"""PR do trạm mở (lát 4c) trên thẻ cột 3 — spec 2 §5.2, spec 4 §6.5; plan 2d G10–G13.

Chỉ đọc sự kiện `pr.mo` (loại `bead`), `pr.da_merge`, `pr.khong_xac_minh` ghi SAU `bead.vao_cot_3` đang hiện và
cùng `commit_ban_giao` — trả về vòng trước không còn dính. Mọi chuỗi trả về dựng từ hằng số, số PR nguyên và URL
GitHub đã kiểm dạng; không lấy chữ từ GitHub hay từ notes của agent."""
import re

URL_PR = re.compile(r"https://github\.com/[A-Za-z0-9_.-]{1,100}/[A-Za-z0-9_.-]{1,100}/pull/[0-9]{1,9}")
LY_DO = {   # mã của tram/giao_viec/pr_merge.py::ly_do_khong_xac_minh
    "pr-khac": "PR trên GitHub không còn là PR trạm đã mở",
    "sai-nhanh": "PR không đi từ nhánh tram/<bead> của cùng repo",
    "sai-nhanh-chinh": "PR không merge vào nhánh chính của dự án",
    "thieu-merge-commit": "GitHub không trả merge commit",
    "merge-khong-tren-nhanh-chinh": "merge commit không nằm trên nhánh chính",
    "khong-phai-merge-commit": "không phải merge commit (squash / rebase)",           # chữ mockup (D20)
    "head-khac-commit-ban-giao": "head của PR khác commit trạm đã kiểm",
}
LY_DO_KHAC = "lý do khác — xem nhật ký sự kiện của bead"


def pr_tram(kho, du_an: str, bead_id: str, vao_cot_3) -> dict | None:
    """`{so, url, trang_thai: mo | khong_xac_minh | da_merge, ly_do}` hoặc None khi trạm chưa mở PR."""
    c = vao_cot_3.du_lieu.get("commit_ban_giao")

    def sau(s) -> bool:
        return s.id > vao_cot_3.id and s.du_lieu.get("commit") == c

    mo = kho.moi_nhat(du_an, bead_id, "pr.mo", dieu_kien=lambda s: sau(s) and s.du_lieu.get("loai") == "bead")
    if mo is None:
        return None
    so, url = mo.du_lieu.get("pr"), mo.du_lieu.get("url")
    ra = {"so": so if type(so) is int else None,
          "url": url if isinstance(url, str) and URL_PR.fullmatch(url) else None,
          "trang_thai": "mo", "ly_do": None}
    if kho.moi_nhat(du_an, bead_id, "pr.da_merge", dieu_kien=sau) is not None:
        return {**ra, "trang_thai": "da_merge"}
    kx = kho.moi_nhat(du_an, bead_id, "pr.khong_xac_minh", dieu_kien=sau)
    if kx is not None:
        return {**ra, "trang_thai": "khong_xac_minh", "ly_do": LY_DO.get(kx.du_lieu.get("ly_do"), LY_DO_KHAC)}
    return ra
```

`tram/suy/giao_viec.py`:

```diff
diff --git a/tram/suy/giao_viec.py b/tram/suy/giao_viec.py
--- a/tram/suy/giao_viec.py
+++ b/tram/suy/giao_viec.py
@@ -12,6 +12,7 @@ from tram.giao_viec.dieu_kien import NHAN_COT_1, ly_do_khong_giao
 from tram.giao_viec.git_kiem import sha_cua
 from tram.giao_viec.kho_kiem_tao import github_repo, url_origin
 from tram.giao_viec.tieu_chi import lenh_bat_buoc
+from tram.suy.pr_tram import pr_tram
 
 ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}")
 SHA_RE = re.compile(r"[0-9a-f]{40}")
@@ -57,12 +58,15 @@ def thong_tin_pr(da: DuAn, b: Bead, vao_cot_3: dict | None, kg: Path | None) ->
 
 
 def suy_giao(da: DuAn, beads: list[Bead], kho, kg: Path | None) -> dict[str, dict]:
-    """{"<du_an>/<bead_id>": {"khong_giao": văn bản | None, "pr": {...} | None}} — chỉ bead có điều để hiện."""
+    """{"<du_an>/<bead_id>": {"khong_giao": văn bản | None, "pr": {..., "tram": {...} | None} | None}} — chỉ bead
+    có điều để hiện. `pr.tram`: PR trạm đã mở ở lát 4c (`tram/suy/pr_tram.py`, plan 2d G10)."""
     theo_id, ra = {b.id: b for b in beads}, {}
     for b in beads:
         ly = ly_do_hien(b, theo_id, da, kg is not None)
         vc3 = kho.moi_nhat(da.ten, b.id, "bead.vao_cot_3") if "cot:cho-review" in b.labels else None
         pr = thong_tin_pr(da, b, vc3.du_lieu if vc3 else None, kg)
+        if pr is not None:
+            pr["tram"] = pr_tram(kho, da.ten, b.id, vc3)
         if ly or pr:
             ra[f"{da.ten}/{b.id}"] = {"khong_giao": VAN_BAN[ly] if ly else None, "pr": pr}
     return ra
```

`tram/api/luong.py`:

```diff
diff --git a/tram/api/luong.py b/tram/api/luong.py
--- a/tram/api/luong.py
+++ b/tram/api/luong.py
@@ -15,7 +15,8 @@ NHIP_GIAY = 2
 NHIP_GIU_KET_NOI = 8          # mỗi 8 nhịp (~16 s) một dòng chú thích giữ kết nối
 LOAI_LAM_MOI = {"quet.xong", "quet.loi", "cot.dai_ca_sua", "cot.da_chot", "cot.tra_ve", "escalation.tra_loi",
                 "cham_cot.thu_lai", "cham_cot.bo_qua", "estop.bat", "estop.tat",
-                "khe.cau_dao_ngat", "khe.cau_dao_dong"}                    # 2b: "Hệ cần xem" cầu dao khe
+                "khe.cau_dao_ngat", "khe.cau_dao_dong",                    # 2b: "Hệ cần xem" cầu dao khe
+                "pr.mo", "pr.khong_xac_minh", "pr.da_merge"}               # 2d: thẻ cột 3 (PR do trạm mở)
 TIEN_TO_DOI_NGU = ("khe.", "chay.", "giao.", "bao.", "tho.")          # 2b: sự kiện phần 3 → trang Đội ngũ AI tải lại
 
 
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_the_cot_3_pr.py tests/test_giao_viec_api.py tests/test_luong.py -q`
Expected: `15 passed`

Run: `uv run pytest -q`
Expected: `N₀ + 4 passed` (1998 trên bản dựng thử)

- [ ] **Step 5: Commit**

```bash
git add tram/suy/pr_tram.py tram/suy/giao_viec.py tram/api/luong.py tests/test_the_cot_3_pr.py
git commit -m "feat(suy): thẻ cột 3 mang trạng thái PR do trạm mở, kể cả pr.khong_xac_minh và lý do; SSE làm mới khi có pr.* (spec 2 §5.2; plan 2d G10–G13, G18; bs-urj.8)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 4: Telegram — tin "PR đã merge" và "PR không xác minh được"

**Độ khó:** `de` · **Đợt:** 1 · **Song song với:** Task 1, 3 · **Phải xong trước:** —

**Files:**
- Modify: `tram/bao_tin/tin.py` (`LOAI_TIN`, `NHAN_LOAI`), `tram/bao_tin/nguon.py` (`TIN_PR`, `tin_tu_su_kien`)
- Test: `tests/test_bao_tin_pr.py` (mới)

**Interfaces:**
- Consumes: sự kiện `pr.da_merge`, `pr.khong_xac_minh` (4c); `BoChongOn`, `mot_vong`, `NguCanhBaoTin`, `soan_tin` (không đổi).
- Produces: loại tin `"pr_da_merge"`, `"pr_khong_xac_minh"` trong `LOAI_TIN` và `NHAN_LOAI`; `TIN_PR = {"pr.da_merge": "pr_da_merge", "pr.khong_xac_minh": "pr_khong_xac_minh"}`; `tin_tu_su_kien` trả `[Tin(<loại>, du_an, bead_id)]` (G15).

- [ ] **Step 1: Viết test thất bại**

`tests/test_bao_tin_pr.py` (mới):

```python
"""Tin Telegram "PR đã merge" / "PR không xác minh được" từ `pr.da_merge`, `pr.khong_xac_minh` của 4c (spec 2 §6,
§4 mục 5; D15; plan 2d Task 4, G15–G17)."""
from datetime import datetime, timedelta, timezone

from bd_gia import BdGia
from tram.bao_tin.chong_on import BoChongOn
from tram.bao_tin.nguon import tin_tu_su_kien
from tram.bao_tin.tin import LOAI_TIN, NHAN_LOAI, Tin, soan_tin
from tram.bao_tin.vong import NguCanhBaoTin, mot_vong
from tram.su_kien.kho import KhoSuKien, SuKien

T0 = datetime(2026, 10, 13, 3, 0, tzinfo=timezone.utc)             # 10:00 giờ VN
SHA, MERGE, URL = "a" * 40, "b" * 40, "https://github.com/hung/hr-codex/pull/7"
DA_MERGE = {"bead_id": "hr-1", "pr": 7, "url": URL, "commit": SHA, "merge_commit": MERGE, "nhanh_chinh": "main",
            "ma_thao_tac": "pr-0123456789abcdef0123"}
KHONG_XM = {"bead_id": "hr-2", "pr": 8, "commit": SHA, "ly_do": "khong-phai-merge-commit",
            "ma_thao_tac": "pr-0123456789abcdef0124"}


def sk(loai, du_lieu=None, bead="hr-1"):
    return SuKien("2026-10-13T03:00:00Z", "hr-codex", bead, loai, "tram/giao-viec", du_lieu or {})


def test_hai_su_kien_pr_thanh_tin_pr_mo_thi_khong():
    assert {"pr_da_merge", "pr_khong_xac_minh"} <= set(LOAI_TIN) and {"pr_da_merge", "pr_khong_xac_minh"} <= set(
        NHAN_LOAI)
    assert tin_tu_su_kien(sk("pr.da_merge", DA_MERGE), None) == [Tin("pr_da_merge", "hr-codex", "hr-1")]
    assert tin_tu_su_kien(sk("pr.khong_xac_minh", KHONG_XM, "hr-2"), None) == [
        Tin("pr_khong_xac_minh", "hr-codex", "hr-2")]
    assert tin_tu_su_kien(sk("pr.mo", {"pr": 7, "url": URL, "commit": SHA}), None) == []


def test_mot_vong_gui_tin_khong_lo_pr_url_sha_ly_do(tmp_path):
    da_gui = []
    nc = NguCanhBaoTin(kho=KhoSuKien(tmp_path / "sk.db"), tao_bd=lambda ten: BdGia([]), gui=da_gui.append,
                       thu_muc=tmp_path / "bao-tin", dashboard_url="https://may-b.tail.ts.net/", bay_gio=lambda: T0)
    assert mot_vong(nc) == 0                                         # lần đầu: chỉ đặt mốc
    nc.kho.ghi("hr-codex", "pr.da_merge", DA_MERGE, bead_id="hr-1", tac_nhan="tram/giao-viec")
    nc.kho.ghi("hr-codex", "pr.khong_xac_minh", KHONG_XM, bead_id="hr-2", tac_nhan="tram/giao-viec")
    assert mot_vong(nc) == 2
    assert sorted(da_gui) == sorted([
        "[tram] hr-codex · 1 PR đã merge, trạm xác minh đúng commit đã kiểm (hr-1) → https://may-b.tail.ts.net/",
        "[tram] hr-codex · 1 PR đã merge nhưng trạm không xác minh được, cần Đại ca Duyệt tay (hr-2)"
        " → https://may-b.tail.ts.net/"])
    assert not any(x in t for t in da_gui for x in ("github", "#7", "#8", SHA[:7], MERGE[:7], "khong-phai", "main"))
    nc.kho.ghi("hr-codex", "pr.da_merge", DA_MERGE, bead_id="hr-1", tac_nhan="tram/giao-viec")
    assert mot_vong(nc) == 0                                         # cùng (loại, bead) trong 1 giờ: không gửi lại


def test_chong_on_gom_5_phut_va_gio_yen_lang():
    bo = BoChongOn("23:00-07:00")
    a, b = Tin("pr_da_merge", "hr-codex", "hr-1"), Tin("pr_da_merge", "hr-codex", "hr-2")
    assert [g.tins for g in bo.nhan([a], T0)] == [(a,)]
    assert bo.nhan([b], T0 + timedelta(minutes=1)) == []                       # trong cửa sổ: chờ gom
    assert [g.tins for g in bo.den_han(T0 + timedelta(minutes=5))] == [(b,)]
    dem = datetime(2026, 10, 13, 16, 30, tzinfo=timezone.utc)                 # 23:30 giờ VN
    k = Tin("pr_khong_xac_minh", "hr-codex", "hr-3")
    assert BoChongOn("23:00-07:00").nhan([a, k], dem) == []
    assert "hr-1" in soan_tin("pr_da_merge", [a], None) and "→" not in soan_tin("pr_da_merge", [a], None)
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_bao_tin_pr.py -q`
Expected: FAIL — `3 failed` (hai loại chưa có trong `LOAI_TIN`; `mot_vong` trả 0; `KeyError: 'pr_da_merge'` ở `soan_tin`)

- [ ] **Step 3: Viết mã**

`tram/bao_tin/tin.py`:

```diff
diff --git a/tram/bao_tin/tin.py b/tram/bao_tin/tin.py
--- a/tram/bao_tin/tin.py
+++ b/tram/bao_tin/tin.py
@@ -4,11 +4,14 @@ from collections.abc import Sequence
 from dataclasses import dataclass
 
 LOAI_TIN = ("cho_review", "spec_cho_duyet", "escalation", "co_do", "tram_loi", "estop_bat", "estop_tat",
-            "khe_cau_dao", "khe_het_han_muc", "spec_cho_merge", "feature_xong")
+            "khe_cau_dao", "khe_het_han_muc", "spec_cho_merge", "feature_xong", "pr_da_merge",
+            "pr_khong_xac_minh")
 NHAN_LOAI = {"cho_review": "việc chờ review", "spec_cho_duyet": "spec chờ duyệt", "escalation": "escalation bí",
              "co_do": "cờ đỏ", "tram_loi": "trạm lỗi", "estop_bat": "estop BẬT", "estop_tat": "estop tắt",
              "khe_cau_dao": "cầu dao khe ngắt", "khe_het_han_muc": "khe hết hạn mức",
-             "spec_cho_merge": "spec đã duyệt chưa merge sau 24 giờ", "feature_xong": "feature xong, chờ Đại ca đóng"}
+             "spec_cho_merge": "spec đã duyệt chưa merge sau 24 giờ", "feature_xong": "feature xong, chờ Đại ca đóng",
+             "pr_da_merge": "PR đã merge, trạm xác minh đúng commit đã kiểm",           # 2d: pr.da_merge (4c)
+             "pr_khong_xac_minh": "PR đã merge nhưng trạm không xác minh được, cần Đại ca Duyệt tay"}   # 2d D15
 ID_AN_TOAN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}")
 KHE_AN_TOAN = re.compile(r"[A-Za-z0-9-]{1,32}/[a-z0-9-]{1,32}")      # khe_id (spec 3 §4) — tin hệ của lát 2b
 
```

`tram/bao_tin/nguon.py`:

```diff
diff --git a/tram/bao_tin/nguon.py b/tram/bao_tin/nguon.py
--- a/tram/bao_tin/nguon.py
+++ b/tram/bao_tin/nguon.py
@@ -7,6 +7,8 @@ NHAN_TIN = {"cot:cho-review": "cho_review", "cho-duyet-spec": "spec_cho_duyet",
 NHAN_ESCALATION = "tram:escalation"
 NGUONG_QUET_LOI = 3
 TIN_FEATURE = {"spec.cho_merge": "spec_cho_merge", "feature.xong": "feature_xong"}   # phần 4 §10 bước 4
+# 2d (D15): PR do trạm mở đã merge — xác minh được / không. Chỉ mã bead; không số PR, URL, SHA, lý do.
+TIN_PR = {"pr.da_merge": "pr_da_merge", "pr.khong_xac_minh": "pr_khong_xac_minh"}
 
 
 def anh_tu_beads(beads: list[Bead]) -> dict[str, dict]:
@@ -40,6 +42,8 @@ def tin_tu_su_kien(sk, kho) -> list[Tin]:
         return [Tin("tram_loi", sk.du_an, sk.bead_id)]
     if sk.loai in TIN_FEATURE:
         return [Tin(TIN_FEATURE[sk.loai], sk.du_an, sk.bead_id)]
+    if sk.loai in TIN_PR:
+        return [Tin(TIN_PR[sk.loai], sk.du_an, sk.bead_id)]
     if sk.loai == "khe.cau_dao_ngat":
         het = sk.du_lieu.get("ly_do") == "het-han-muc"
         return [Tin("khe_het_han_muc" if het else "khe_cau_dao", sk.du_an, sk.du_lieu.get("khe_id"))]
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_bao_tin_pr.py tests/test_bao_tin.py tests/test_bao_tin_feature.py tests/test_bao_tin_khe.py tests/test_chong_on.py -q`
Expected: `26 passed`

Run: `uv run pytest -q`
Expected: `N₀ + 3 passed` (1997 trên bản dựng thử)

- [ ] **Step 5: Commit**

```bash
git add tram/bao_tin/tin.py tram/bao_tin/nguon.py tests/test_bao_tin_pr.py
git commit -m "feat(bao-tin): tin Telegram 'PR đã merge' và 'PR không xác minh được' — chỉ dự án + mã bead, chịu chống ồn và giờ yên lặng (spec 2 §6, §4 mục 5; D15; plan 2d G15–G17; bs-urj.8)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 5: Frontend — luật PR trạm theo mockup; nhãn PR trên thẻ và khối PR trong ngăn bên

**Độ khó:** `de` · **Đợt:** 2 · **Song song với:** Task 2, 6 · **Phải xong trước:** Task 3 (hợp đồng `pr.tram`)

**Phạm vi (D38):** luật thuần trong `giao_viec.js` là phần 2f giữ nguyên, nên theo đúng chữ mockup. `TheBead.vue`, `OGiaoViec.vue` sửa nhỏ trên bố cục cũ; 2f làm lại theo mockup (chip `.pr-*`, mục "PR" trong ngăn bên). Không sửa trang Phê duyệt (G21, việc của 2f).

**Files:**
- Modify: `frontend/src/giao_viec.js` (thêm cuối file), `frontend/src/thanh/TheBead.vue` (script + một nhãn), `frontend/src/thanh/OGiaoViec.vue` (khối PR trạm)
- Test: `frontend/tests/giao_viec.test.mjs` (import + hai test)

**Interfaces:**
- Consumes: `the.giao.pr.tram = {so, url, trang_thai, ly_do} | null` (Task 3, G10).
- Produces (giữ nguyên cho lát 2f, G14): `NHAN_PR_TRAM`, `prTram(the)`, `nhanPrTram(the) -> string`, `lopPrTram(t) -> string`, `moTaPrTram(t) -> string`, `canhBaoPrTram(t) -> string`. Chữ theo mockup: `NHAN_PR` (`du-lieu.js`), dòng "PR #n — lý do" của `moBead` và câu cảnh báo của `theReview` (`trang.js`).

- [ ] **Step 1: Viết test thất bại**

`frontend/tests/giao_viec.test.mjs`:

```diff
diff --git a/frontend/tests/giao_viec.test.mjs b/frontend/tests/giao_viec.test.mjs
--- a/frontend/tests/giao_viec.test.mjs
+++ b/frontend/tests/giao_viec.test.mjs
@@ -1,6 +1,7 @@
 import assert from 'node:assert/strict'
 import { test } from 'node:test'
 import { canhBaoPr, ganGiaoViec, nhanChuaGiao } from '../src/giao_viec.js'
+import { canhBaoPrTram, lopPrTram, moTaPrTram, nhanPrTram, prTram } from '../src/giao_viec.js'
 
 test('ganGiaoViec gắn theo khoá du_an/id, thiếu thì null', () => {
   const ds = ganGiaoViec([{ du_an: 'hr', id: 'a' }, { du_an: 'hr', id: 'b' }],
@@ -22,3 +23,28 @@ test('canhBaoPr: lệch nhánh, chưa kiểm được, khớp', () => {
   assert.match(canhBaoPr({ ...pr, tu_xa: null }), /Chưa kiểm được/)
   assert.equal(canhBaoPr(null), '')
 })
+
+test('nhanPrTram, lopPrTram: nhãn và lớp chip theo mockup; trạng thái lạ thì không có', () => {
+  const the = (tram) => ({ giao: { khong_giao: null, pr: { nhanh: 'tram/hr-1', tram } } })
+  assert.equal(nhanPrTram(the({ so: 7, trang_thai: 'khong_xac_minh', ly_do: 'x' })), 'PR không xác minh được')
+  assert.equal(nhanPrTram(the({ so: 7, trang_thai: 'mo', ly_do: null })), 'PR đã mở')
+  assert.equal(nhanPrTram(the({ so: 7, trang_thai: 'da_merge', ly_do: null })), 'PR đã merge')
+  assert.equal(nhanPrTram(the({ so: 7, trang_thai: 'constructor', ly_do: null })), '')
+  assert.equal(nhanPrTram(the(null)), '')
+  assert.equal(nhanPrTram({ giao: null }), '')
+  assert.equal(prTram(null), null)
+  assert.equal(lopPrTram({ trang_thai: 'khong_xac_minh' }), 'pr-khong_xac_minh')
+  assert.equal(lopPrTram({ trang_thai: 'x" onclick="' }), '')
+  assert.equal(lopPrTram(null), '')
+})
+
+test('moTaPrTram, canhBaoPrTram: số PR chỉ khi là số nguyên; cảnh báo chỉ khi không xác minh được', () => {
+  const t = { so: 12, url: null, trang_thai: 'khong_xac_minh', ly_do: 'không phải merge commit (squash / rebase)' }
+  assert.equal(moTaPrTram(t), 'PR #12 — không phải merge commit (squash / rebase)')
+  assert.equal(moTaPrTram({ ...t, so: '12<b>', trang_thai: 'da_merge', ly_do: null }), 'PR')
+  assert.equal(moTaPrTram(null), '')
+  assert.equal(canhBaoPrTram(t), 'PR đã merge nhưng trạm không xác minh được: không phải merge commit'
+    + ' (squash / rebase). Bead ở lại cột 3 — Đại ca tự kiểm rồi bấm Duyệt.')
+  assert.equal(canhBaoPrTram({ ...t, trang_thai: 'mo' }), '')
+  assert.equal(canhBaoPrTram(null), '')
+})
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `cd frontend && npm run kiem`
Expected: FAIL — `SyntaxError: The requested module '../src/giao_viec.js' does not provide an export named 'canhBaoPrTram'`; `ℹ tests 31` · `ℹ pass 30` · `ℹ fail 1` (trên main sau đợt 1, M₀ = 33)

- [ ] **Step 3: Viết mã**

`frontend/src/giao_viec.js`:

```diff
diff --git a/frontend/src/giao_viec.js b/frontend/src/giao_viec.js
--- a/frontend/src/giao_viec.js
+++ b/frontend/src/giao_viec.js
@@ -15,3 +15,35 @@ export function canhBaoPr(pr) {
   if (pr.lech) return `Nhánh ${pr.nhanh} trên remote đang ở ${pr.tu_xa}, KHÁC commit trạm đã kiểm — đừng tạo PR.`
   return ''
 }
+
+// Lát 2d: PR do trạm mở (4c). Server gửi `giao.pr.tram = {so, url, trang_thai, ly_do}`; `ly_do` là câu hằng của server.
+// Nhãn và câu theo mockup đã duyệt (D20, D33 — docs/mockup/2026-10-15-giao-dien); giao diện Vue làm ở lát 2f.
+export const NHAN_PR_TRAM = { mo: 'PR đã mở', khong_xac_minh: 'PR không xác minh được', da_merge: 'PR đã merge' }
+const biet = (t) => Boolean(t) && Object.hasOwn(NHAN_PR_TRAM, t.trang_thai)
+
+export function prTram(the) {
+  return (the && the.giao && the.giao.pr && the.giao.pr.tram) || null
+}
+
+export function nhanPrTram(the) {
+  const t = prTram(the)
+  return biet(t) ? NHAN_PR_TRAM[t.trang_thai] : ''
+}
+
+// Lớp chip `pr-<trạng thái>` của mockup (style.css) — chỉ cho trạng thái đã biết.
+export function lopPrTram(t) {
+  return biet(t) ? `pr-${t.trang_thai}` : ''
+}
+
+// Dòng PR trong ngăn bên (mockup Công việc): "PR #12 — <lý do>"; số chỉ khi là số nguyên.
+export function moTaPrTram(t) {
+  if (!t) return ''
+  const so = Number.isInteger(t.so) ? `PR #${t.so}` : 'PR'
+  return t.ly_do ? `${so} — ${t.ly_do}` : so
+}
+
+// Cảnh báo trên thẻ "Chờ review để đóng" (mockup Phê duyệt) — chỉ khi PR đã merge mà trạm không xác minh được.
+export function canhBaoPrTram(t) {
+  if (!t || t.trang_thai !== 'khong_xac_minh') return ''
+  return `PR đã merge nhưng trạm không xác minh được: ${t.ly_do}. Bead ở lại cột 3 — Đại ca tự kiểm rồi bấm Duyệt.`
+}
```

`frontend/src/thanh/TheBead.vue`:

```diff
diff --git a/frontend/src/thanh/TheBead.vue b/frontend/src/thanh/TheBead.vue
--- a/frontend/src/thanh/TheBead.vue
+++ b/frontend/src/thanh/TheBead.vue
@@ -1,6 +1,11 @@
 <script setup>
+import { computed } from 'vue'
+import { nhanPrTram, prTram } from '../giao_viec.js'
+
 const props = defineProps({ the: { type: Object, required: true } })
 const emit = defineEmits(['mo', 'keo'])
+const nhanPr = computed(() => nhanPrTram(props.the))
+const prVang = computed(() => prTram(props.the)?.trang_thai === 'khong_xac_minh')
 
 function batDauKeo(e) {
   e.dataTransfer.setData('text/plain', props.the.id)   // Firefox chỉ bắt đầu kéo khi có dữ liệu (N2)
@@ -19,6 +24,7 @@ function batDauKeo(e) {
       <span v-if="the.co_do" class="nhan-nho do">cờ đỏ</span>
       <span v-if="the.lech" class="nhan-nho vang" title="Nhiều nhãn cột">nhãn lệch</span>
       <span v-if="the.giao && the.giao.khong_giao" class="nhan-nho vang" :title="the.giao.khong_giao">chưa giao</span>
+      <span v-if="nhanPr" class="nhan-nho" :class="{ vang: prVang }">{{ nhanPr }}</span>
     </header>
     <p class="tieu-de">{{ the.tieu_de }}</p>
     <footer class="nho">{{ the.loai }} · P{{ the.uu_tien ?? '?' }}<span v-if="the.khe_spec"> · khe spec</span><span
```

`frontend/src/thanh/OGiaoViec.vue`:

```diff
diff --git a/frontend/src/thanh/OGiaoViec.vue b/frontend/src/thanh/OGiaoViec.vue
--- a/frontend/src/thanh/OGiaoViec.vue
+++ b/frontend/src/thanh/OGiaoViec.vue
@@ -1,17 +1,26 @@
 <script setup>
 import { computed } from 'vue'
-import { canhBaoPr } from '../giao_viec.js'
+import { canhBaoPr, canhBaoPrTram, moTaPrTram, nhanPrTram } from '../giao_viec.js'
 import { laLinkAnToan } from '../luat.js'
 
 const props = defineProps({ giao: { type: Object, required: true } })
 const canhBao = computed(() => canhBaoPr(props.giao.pr))
+const tram = computed(() => (props.giao.pr && props.giao.pr.tram) || null)
+const nhanTram = computed(() => nhanPrTram({ giao: props.giao }))
 </script>
 
 <template>
   <section aria-label="Bộ giao việc">
     <h3>Bộ giao việc</h3>
     <p v-if="giao.khong_giao" class="canh-bao">Chưa giao: {{ giao.khong_giao }}</p>
-    <template v-if="giao.pr">
+    <template v-if="tram">
+      <p class="nho">{{ nhanTram }} · {{ moTaPrTram(tram) }}</p>
+      <p v-if="canhBaoPrTram(tram)" class="canh-bao" role="alert">{{ canhBaoPrTram(tram) }}</p>
+      <p v-if="laLinkAnToan(tram.url)">
+        <a :href="tram.url" target="_blank" rel="noopener noreferrer">Mở PR trên GitHub</a>
+      </p>
+    </template>
+    <template v-else-if="giao.pr">
       <p class="nho">Tạo PR từ nhánh {{ giao.pr.nhanh }} tại commit {{ giao.pr.commit }} (trạm đã kiểm lại và QC).</p>
       <p v-if="canhBao" class="canh-bao" role="alert">{{ canhBao }}</p>
       <p v-else-if="laLinkAnToan(giao.pr.link)">
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `cd frontend && npm run kiem && npm run build && npm run kiem-dist`
Expected: `ℹ tests 35` · `ℹ fail 0` (M₀ + 2; sau khi ghép cả Task 2: 37); `kiem-an-toan` xanh; `✓ built`; `kiem-dist` xanh.

Run: `uv run pytest -q` → không đổi do task này.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/giao_viec.js frontend/src/thanh/TheBead.vue frontend/src/thanh/OGiaoViec.vue frontend/tests/giao_viec.test.mjs
git commit -m "feat(frontend): luật PR trạm theo chữ mockup; thẻ cột 3 hiện nhãn PR, ngăn bên thay lệnh tạo PR bằng trạng thái PR trạm (spec 2 §5.2; D38; plan 2d G14; bs-urj.8)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 6: API — `GET /api/doi-ngu?du_an=&so_ngay=` lọc bảng điểm; mọi khe đã khai có hàng (D41)

**Độ khó:** `de` · **Đợt:** 2 · **Song song với:** Task 2, 5 · **Phải xong trước:** Task 1 (`bang_diem(db, *, du_an, tu)`)

**Files:**
- Modify: `tram/suy/doi_ngu.py` (`SO_NGAY_BANG_DIEM`, hàm mới `du_hang_khe`, chữ ký và thân `doi_ngu`), `tram/api/doi_ngu.py` (`r_doi_ngu`)
- Test: `tests/test_api_doi_ngu_loc.py` (mới)

**Interfaces:**
- Consumes: `bang_diem(db, *, du_an, tu)` (Task 1); `chuoi_gio`; `kiem_du_an_bead`; `KhongHopLe`.
- Produces:
  - `SO_NGAY_BANG_DIEM = 30`;
  - `du_hang_khe(hang, ds: list[TrangThaiKhe]) -> list[dict]` (D41, G22): thêm hàng 0 phiếu cho mỗi (khe, vai ưu tiên) chưa có hàng; `ds` là chính danh sách `trang_thai_khe` mà `doi_ngu` dùng cho thẻ khe;
  - `doi_ngu(kho, *, bay_gio, ch, du_an: str | None = None, so_ngay: int = 30) -> dict`, với `tu = chuoi_gio(bay_gio − so_ngay ngày)` (D28) và `bang_diem = du_hang_khe(bang_diem(...), ds)`;
  - `GET /api/doi-ngu?du_an=&so_ngay=` (G5, G22). Task 2 gọi route này; lát 2f đọc thẳng `bang_diem`, không ghép hàng phía trình duyệt.

Ca test của D41 (G22): khe `B/claude-1` khai vai `qc` nhưng có phiếu code → giữ hàng `coder` (có phiếu) và thêm hàng `qc` 0 phiếu; khe `B/codex-2` khai `coder, qc`, phiếu duy nhất cấp 40 ngày trước → mặc định 30 ngày vẫn có hàng `coder` 0 phiếu (mẫu 0, giao diện hiện "chưa có") và hàng `qc` (mẫu `null`, hiện "—"); 92 ngày → hàng `coder` có 1 phiếu; lọc dự án khác vẫn đủ bốn hàng.

- [ ] **Step 1: Viết test thất bại**

`tests/test_api_doi_ngu_loc.py` (mới):

```python
"""`GET /api/doi-ngu?du_an=&so_ngay=` — lọc bảng điểm theo dự án và số ngày, mặc định mọi dự án, 30 ngày (D14;
plan 2d Task 6, G5, D28, D29); mọi khe đã khai có hàng theo vai ưu tiên, kể cả khi chưa có phiếu (D41, G22)."""
from contextlib import closing
from dataclasses import replace
from datetime import timedelta

from api_gia import tao_pt
from asgi_gia import goi
from bd_gia import BdGia
from kho_phieu_gia import LUC, dat_phieu
from tram.api.app import tao_app
from tram.phieu.ghi import danh_dau_ket_thuc
from tram.phieu.khe import dang_ky_khe
from tram.phieu.kho import KhoPhieu

KHE = [{"ten": "claude-1", "cli": "claude", "ten_goi_nho": "Claude 1", "vai_uu_tien": ["qc"]},
       {"ten": "codex-2", "cli": "codex", "ten_goi_nho": "Codex 2", "vai_uu_tien": ["coder", "qc"]}]


def _app(tmp_path):
    kho = KhoPhieu(tmp_path / "sk.db")
    for i, (du_an, luc) in enumerate([("hr-codex", LUC), ("hr-codex", LUC - timedelta(days=40)), ("hr-khac", LUC)]):
        p = dat_phieu(kho, "B/claude-1", luc=luc + timedelta(minutes=i), bead_id=f"hr-{i}", du_an=du_an)
        with kho.giao_dich() as db:
            danh_dau_ket_thuc(db, p.giao_id, "xong", luc)
    kho.close()
    pt = replace(tao_pt(tmp_path, {"hr-codex": BdGia([]), "hr-khac": BdGia([])}),
                 mo_kho_phieu=lambda: KhoPhieu(tmp_path / "sk.db"), dong_ho=lambda: LUC)
    return tao_app(pt)


def so_phieu(app, q=""):
    r = goi(app, "GET", f"/api/doi-ngu{q}")
    assert r.status == 200
    return [h["so_phieu"] for h in r.json()["bang_diem"]]


def test_mac_dinh_moi_du_an_30_ngay_va_loc(tmp_path):
    app = _app(tmp_path)
    assert so_phieu(app) == [2]                                    # phiếu 40 ngày trước nằm ngoài
    assert so_phieu(app, "?so_ngay=92") == [3]
    assert so_phieu(app, "?du_an=hr-codex") == [1]
    assert so_phieu(app, "?du_an=hr-khac&so_ngay=7") == [1]
    assert so_phieu(app, "?du_an=&so_ngay=30") == [2]


def test_tham_so_sai(tmp_path):
    app = _app(tmp_path)
    assert goi(app, "GET", "/api/doi-ngu?du_an=khong-co").status == 404
    assert goi(app, "GET", "/api/doi-ngu?so_ngay=0").status == 422
    assert goi(app, "GET", "/api/doi-ngu?so_ngay=93").status == 422
    assert goi(app, "GET", "/api/doi-ngu?so_ngay=x").status == 422


def test_moi_khe_da_khai_co_hang_ke_ca_khi_bo_loc_khong_con_phieu(tmp_path):
    app = _app(tmp_path)
    with closing(KhoPhieu(tmp_path / "sk.db")) as kho:
        with kho.giao_dich():
            dang_ky_khe(kho, "B", KHE, luc=LUC)
        dat_phieu(kho, "B/codex-2", luc=LUC - timedelta(days=40), bead_id="hr-9")

    def hang(q=""):
        return [(h["khe_id"], h["vai"], h["so_phieu"], h["qua_lan_dau_mau"], h["bi_tra_ve_mau"])
                for h in goi(app, "GET", f"/api/doi-ngu{q}").json()["bang_diem"]]
    assert hang() == [("B/claude-1", "coder", 2, 2, 0),            # có phiếu, ngoài vai ưu tiên: vẫn giữ
                      ("B/claude-1", "qc", 0, None, None),          # vai ưu tiên chưa có phiếu: "—"
                      ("B/codex-2", "coder", 0, 0, 0),              # phiếu 40 ngày trước ở ngoài, hàng vẫn còn
                      ("B/codex-2", "qc", 0, None, None)]
    assert hang("?so_ngay=92")[2] == ("B/codex-2", "coder", 1, 0, 0)
    assert [h[:3] for h in hang("?du_an=hr-khac&so_ngay=7")] == [
        ("B/claude-1", "coder", 1), ("B/claude-1", "qc", 0), ("B/codex-2", "coder", 0), ("B/codex-2", "qc", 0)]
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_api_doi_ngu_loc.py -q`
Expected: FAIL — `3 failed` (trên main sau đợt 1: mặc định trả cả phiếu 40 ngày trước — `[3] != [2]`; `?du_an=khong-co` trả 200, không phải 404 — `assert 200 == 404`; test D41: `At index 0 diff: ('B/claude-1', 'coder', 3, 3, 0) != ('B/claude-1', 'coder', 2, 2, 0)` và `Right contains 2 more items, first extra item: ('B/codex-2', 'coder', 0, 0, 0)`)

- [ ] **Step 3: Viết mã**

`tram/suy/doi_ngu.py`:

```diff
diff --git a/tram/suy/doi_ngu.py b/tram/suy/doi_ngu.py
--- a/tram/suy/doi_ngu.py
+++ b/tram/suy/doi_ngu.py
@@ -1,18 +1,19 @@
 """Màn Đội ngũ AI (spec 2 §5.4): mỗi khe một thẻ — suy từ `trang_thai_khe` của phần 3 (spec 3 §10.1) — kèm
 `phien_ban` cho thao tác bật/tắt/đóng cầu dao (§12.3), mức hạn mức theo luật nhận việc (spec 3 §8.2), luật
 vai ↔ khe và bảng điểm thợ. Tên gợi nhớ, KHÔNG BAO GIỜ email (§5.4)."""
-from datetime import datetime
+from datetime import datetime, timedelta
 
 from tram.cau_hinh.tram import CauHinhHanMuc, CauHinhTram
 from tram.han_muc.luat import cham_nguong_ngung, duoc_nhan
 from tram.han_muc.mo_hinh import HanMuc, co_chua_biet
 from tram.phieu.khe import phien_ban_khe
-from tram.phieu.kho import KhoPhieu
+from tram.phieu.kho import KhoPhieu, chuoi_gio
 from tram.phieu.mo_hinh import VAI_CUA_BUOC
 from tram.phieu.trang_thai import TrangThaiKhe, trang_thai_khe
 from tram.suy.bang_diem import bang_diem
 from tram.suy.lam_sach import lam_sach
 
+SO_NGAY_BANG_DIEM = 30                    # D14: mặc định bảng điểm = 30 ngày gần nhất, mọi dự án
 LUAT_VAI = (
     "Vai là ưu tiên, không cố định: khe cạn hạn mức thì khe khác nhận vai đó (kiến trúc Q14).",
     "Luật cứng: khe đã code một bead không bao giờ QC chính bead đó — thiếu khe khác thì bead chờ (Q14).",
@@ -49,7 +50,26 @@ def the_khe(kho: KhoPhieu, tt: TrangThaiKhe, ch: CauHinhTram) -> dict:
             "phien_ban": phien_ban_khe(kho, tt.khe_id)}
 
 
-def doi_ngu(kho: KhoPhieu, *, bay_gio: datetime, ch: CauHinhTram) -> dict:
-    return {"bat": True, "khe": [the_khe(kho, tt, ch) for tt in trang_thai_khe(kho, bay_gio=bay_gio, ch=ch)],
+def du_hang_khe(hang: list[dict], ds: list[TrangThaiKhe]) -> list[dict]:
+    """D41: mỗi (khe, vai ưu tiên) của khe đã khai — cùng nguồn `trang_thai_khe` với thẻ khe — có một hàng dù bộ lọc
+    không còn phiếu nào: 0 phiếu, vai coder mẫu 0 (tỉ lệ null → "chưa có"), vai khác mẫu null (D29). Hàng có phiếu
+    giữ nguyên, kể cả vai ngoài vai ưu tiên (vai không cố định — Q14). Xếp theo (khe, vai) như `bang_diem`."""
+    theo = {(h["khe_id"], h["vai"]): h for h in hang}
+    for tt in ds:
+        for v in tt.vai_uu_tien:
+            mau = 0 if v == "coder" else None
+            theo.setdefault((tt.khe_id, v), {"khe_id": tt.khe_id, "vai": v, "so_phieu": 0, "so_xong": 0,
+                                             "lan_chay_tb": None, "qua_lan_dau": None, "qua_lan_dau_mau": mau,
+                                             "bi_tra_ve": None, "bi_tra_ve_mau": mau})
+    return [theo[k] for k in sorted(theo)]
+
+
+def doi_ngu(kho: KhoPhieu, *, bay_gio: datetime, ch: CauHinhTram, du_an: str | None = None,
+            so_ngay: int = SO_NGAY_BANG_DIEM) -> dict:
+    """Bảng điểm lọc theo dự án (None = mọi dự án) và `so_ngay` × 24 giờ tính lùi từ `bay_gio` (D14, D28); bộ lọc
+    không làm mất hàng của khe đã khai (D41)."""
+    tu = chuoi_gio(bay_gio - timedelta(days=so_ngay))
+    ds = trang_thai_khe(kho, bay_gio=bay_gio, ch=ch)
+    return {"bat": True, "khe": [the_khe(kho, tt, ch) for tt in ds],
             "luat_vai": {"vai_cua_buoc": dict(VAI_CUA_BUOC), "luat": list(LUAT_VAI)},
-            "bang_diem": bang_diem(kho.db)}
+            "bang_diem": du_hang_khe(bang_diem(kho.db, du_an=du_an, tu=tu), ds)}
```

`tram/api/doi_ngu.py`:

```diff
diff --git a/tram/api/doi_ngu.py b/tram/api/doi_ngu.py
--- a/tram/api/doi_ngu.py
+++ b/tram/api/doi_ngu.py
@@ -10,13 +10,15 @@ from fastapi import APIRouter, Depends, Request
 from pydantic import Field
 
 from tram.api.bao_mat import yeu_cau_ghi
+from tram.api.phu_thuoc import kiem_du_an_bead
 from tram.api.than import ThanGhi
 from tram.phieu.khe import KheLa
-from tram.suy.doi_ngu import doi_ngu
+from tram.suy.doi_ngu import SO_NGAY_BANG_DIEM, doi_ngu
 from tram.thao_tac.khe import bat_khe_thao_tac, dong_cau_dao_thao_tac, tat_khe_thao_tac
 from tram.thao_tac.loi import ChuaHoTro, KhongHopLe, KhongThay
 
 KHE_RE = re.compile(r"[A-Za-z0-9-]{1,32}/[a-z0-9-]{1,32}")
+SO_NGAY_TOI_DA = 92                       # như /api/usage
 router = APIRouter()
 
 
@@ -25,12 +27,17 @@ class ThanKhe(ThanGhi):
 
 
 @router.get("/api/doi-ngu")
-def r_doi_ngu(request: Request) -> dict:
+def r_doi_ngu(request: Request, du_an: str = "", so_ngay: int = SO_NGAY_BANG_DIEM) -> dict:
+    """`?du_an=` (rỗng = mọi dự án; dự án lạ → 404) và `?so_ngay=` (1–92, mặc định 30) chỉ lọc bảng điểm (D14)."""
     pt = request.app.state.pt
+    if not 1 <= so_ngay <= SO_NGAY_TOI_DA:
+        raise KhongHopLe(f"so_ngay phải trong 1–{SO_NGAY_TOI_DA}")
+    if du_an:
+        kiem_du_an_bead(pt, du_an)
     if pt.mo_kho_phieu is None:
         return {"bat": False, "khe": [], "luat_vai": None, "bang_diem": []}
     with closing(pt.mo_kho_phieu()) as kho:
-        return doi_ngu(kho, bay_gio=pt.dong_ho(), ch=pt.cau_hinh)
+        return doi_ngu(kho, bay_gio=pt.dong_ho(), ch=pt.cau_hinh, du_an=du_an or None, so_ngay=so_ngay)
 
 
 def _ghi(request: Request, may_id: str, ten: str, lam: Callable) -> dict:
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_api_doi_ngu_loc.py tests/test_api_doi_ngu.py tests/test_suy_doi_ngu.py -q`
Expected: `11 passed`

Run: `uv run pytest -q`
Expected: `N₀ + 14 passed` (2008 trên bản dựng thử, đã có đủ đợt 1)

- [ ] **Step 5: Commit**

```bash
git add tram/suy/doi_ngu.py tram/api/doi_ngu.py tests/test_api_doi_ngu_loc.py
git commit -m "feat(api): /api/doi-ngu nhận ?du_an=&so_ngay= (mặc định mọi dự án, 30 ngày) để lọc bảng điểm; mọi khe đã khai có hàng kể cả khi chưa có phiếu (D14, D28, D29, D41; plan 2d G5, G22; bs-urj.6)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

### Task 7: Dữ liệu Phê duyệt — `chi_tiet.pr_tram` cho mục "Chờ review để đóng"

**Độ khó:** `de` · **Đợt:** 2 · **Song song với:** Task 2, 5, 6 · **Phải xong trước:** Task 3 (`pr_tram`)

**Phạm vi (D38):** chỉ dữ liệu. Giao diện trang Phê duyệt (`MucPheDuyet.vue`) làm ở lát 2f.

**Files:**
- Modify: `tram/suy/phe_duyet.py` (import, hàm mới `gan_pr_tram`, một dòng trong `gom_phe_duyet`)
- Test: `tests/test_phe_duyet_pr_tram.py` (mới)

**Interfaces:**
- Consumes: `pr_tram(kho, du_an, bead_id, vao_cot_3)` (Task 3); `KhoSuKien.moi_nhat`; `muc_tu_beads`.
- Produces: `gan_pr_tram(du_an, muc, kho) -> list[dict]`; mục `cho-review` của `GET /api/phe-duyet` có `chi_tiet.pr_tram = {so, url, trang_thai, ly_do} | null` (G21). Lát 2f đọc khoá này.

- [ ] **Step 1: Viết test thất bại**

`tests/test_phe_duyet_pr_tram.py` (mới):

```python
"""Trang Phê duyệt: mục "Chờ review để đóng" mang `chi_tiet.pr_tram` (D38 — C6 của 2d; plan 2d Task 7, G21)."""
from bead_gia import bead, notes_ban_giao
from tram.su_kien.kho import KhoSuKien
from tram.suy.phe_duyet import gom_phe_duyet
from tram.suy.pr_tram import LY_DO

C1, URL = "a" * 40, "https://github.com/hung/hr-codex/pull/7"


def ghi(kho, ten, bead_id="hr-1", **d):
    kho.ghi("hr", ten, d, bead_id=bead_id, tac_nhan="tram/giao-viec")


def test_muc_cho_review_mang_pr_tram(tmp_path):
    kho = KhoSuKien(tmp_path / "sk.db")
    beads = [bead("hr-1", labels=["cot:cho-review"], notes=notes_ban_giao()),
             bead("hr-2", labels=["co-do", "cot:cho-review"]), bead("hr-3", labels=["cot:ai-lam"])]
    ghi(kho, "bead.vao_cot_3", commit_ban_giao=C1)
    ghi(kho, "pr.mo", loai="bead", pr=7, url=URL, commit=C1)
    ghi(kho, "pr.khong_xac_minh", pr=7, commit=C1, ly_do="khong-phai-merge-commit")
    ghi(kho, "pr.mo", "hr-2", loai="bead", pr=8, url=URL, commit=C1)            # hr-2 chưa vào cột 3
    muc = gom_phe_duyet(["hr"], {"hr": beads}, kho)
    cr = {m["bead_id"]: m["chi_tiet"] for m in muc if m["loai"] == "cho-review"}
    assert cr["hr-1"]["pr_tram"] == {"so": 7, "url": URL, "trang_thai": "khong_xac_minh",
                                     "ly_do": LY_DO["khong-phai-merge-commit"]}
    assert cr["hr-1"]["pr"] == "https://github.com/o/r/pull/7"                 # khoá cũ của bàn giao giữ nguyên
    assert cr["hr-2"]["pr_tram"] is None
    assert all("pr_tram" not in m["chi_tiet"] for m in muc if m["loai"] != "cho-review")
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_phe_duyet_pr_tram.py -q`
Expected: FAIL — `1 failed` (`KeyError: 'pr_tram'`)

- [ ] **Step 3: Viết mã**

`tram/suy/phe_duyet.py`:

```diff
diff --git a/tram/suy/phe_duyet.py b/tram/suy/phe_duyet.py
--- a/tram/suy/phe_duyet.py
+++ b/tram/suy/phe_duyet.py
@@ -5,6 +5,7 @@ from tram.suy.chi_tiet import ban_giao_sach
 from tram.suy.cot import NHAN_CO_DO, NHAN_ESCALATION, TRANG_THAI_HIEN
 from tram.suy.lam_sach import lam_sach
 from tram.suy.phe_duyet_spec import bo_sung_spec
+from tram.suy.pr_tram import pr_tram
 
 THU_TU = ("escalation", "decision", "co-do", "he", "cho-review", "spec", "feature-xong")
 HET_BO_QUA = ("cham_cot.bo_qua", "cham_cot.ket_qua", "cham_cot.thu_lai")
@@ -80,11 +81,23 @@ def muc_nho(du_an: str, kho) -> list[dict]:
     return ra
 
 
+def gan_pr_tram(du_an: str, muc: list[dict], kho) -> list[dict]:
+    """Mục `cho-review` mang `chi_tiet.pr_tram`: PR trạm mở sau lần vào cột 3 hiện hành, hoặc None (2d G21, D38)."""
+    ra = []
+    for m in muc:
+        if m["loai"] == "cho-review":
+            vc3 = kho.moi_nhat(du_an, m["bead_id"], "bead.vao_cot_3")
+            m = {**m, "chi_tiet": {**m["chi_tiet"], "pr_tram": pr_tram(kho, du_an, m["bead_id"], vc3) if vc3 else None}}
+        ra.append(m)
+    return ra
+
+
 def gom_phe_duyet(cac_du_an: list[str], theo_du_an: dict[str, list[Bead]], kho, them: list[dict] = ()) -> list[dict]:
     """`them`: mục không gắn dự án (2b: cầu dao khe — `tram/suy/phe_duyet_khe.py`), xếp chung theo độ gấp."""
     ra = list(them)
     for du_an in cac_du_an:
         beads = theo_du_an.get(du_an, [])
-        ra += bo_sung_spec(du_an, muc_tu_beads(du_an, beads), beads, kho) + muc_he(du_an, kho, {b.id: b for b in beads})
+        muc = gan_pr_tram(du_an, muc_tu_beads(du_an, beads), kho)
+        ra += bo_sung_spec(du_an, muc, beads, kho) + muc_he(du_an, kho, {b.id: b for b in beads})
     return sorted(ra, key=lambda m: (THU_TU.index(m["loai"]), 9 if m["uu_tien"] is None else m["uu_tien"],
                                      m["updated_at"] or "", m["du_an"], m["bead_id"] or ""))
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_phe_duyet_pr_tram.py tests/test_suy_phe_duyet.py tests/test_phe_duyet_spec.py tests/test_phe_duyet_khe.py -q`
Expected: `13 passed`

Run: `uv run pytest -q`
Expected: `N₀ + 12 passed` trên main sau đợt 1 (2006 trên bản dựng thử); sau khi ghép cả đợt 2: `N₀ + 15` (2009)

- [ ] **Step 5: Commit**

```bash
git add tram/suy/phe_duyet.py tests/test_phe_duyet_pr_tram.py
git commit -m "feat(suy): mục Chờ review để đóng của /api/phe-duyet mang chi_tiet.pr_tram (D38 — C6 của 2d; plan 2d G21; bs-urj.8)" -m "Co-Authored-By: <model đang thực thi> <noreply@anthropic.com>"
```

---

## Sơ đồ đợt chạy

Số test là kết quả chạy thật ngày 16/10 (bản D41) trên bản sao `main` `503ff64` (N₀ = 1994, M₀ = 33; mã như `38a016f`), mã chép nguyên văn từ plan này. Ngoặc sau tên task là task phải ghép trước. Bản này thay sơ đồ của mục "Bổ sung review đợt 4": cổng S1–S8 đã bỏ theo D25–D29, và thứ tự đợt quay về như bản D12–D15.

```
Đợt 0 — main 503ff64 (mã như 38a016f; hoặc main lúc thực thi) → N₀ passed · node M₀ · build + kiem-dist xanh

Đợt 1 — song song, 3 worktree từ main
  T1 bảng điểm D25–D29 + lọc (py) · T3 thẻ cột 3 + SSE (py) · T4 Telegram hai loại tin PR (py)
  → N₀ + 11 = 2005 passed · node M₀ = 33

Đợt 2 — song song, 4 worktree từ main sau đợt 1
  T6 API lọc bảng điểm + hàng khe đã khai (1) · T7 dữ liệu Phê duyệt (3) · T2 bảng điểm frontend (1; hợp đồng T6)
  T5 PR trạm frontend (3)
  → N₀ + 15 = 2009 passed · node M₀ + 4 = 37 · build + kiem-dist xanh
```

| Task | Độ khó | Đợt | Phải xong trước | File chạm (ngoài test) | Test mới | Toàn bộ sau task (trên main đợt trước) |
|---|---|---|---|---|---|---|
| 1 | vua | 1 | — | `tram/suy/diem_giao_viec.py` (mới), `tram/suy/bang_diem.py` | 4 (py) | N₀ + 4 (1998) |
| 3 | de | 1 | — | `tram/suy/pr_tram.py` (mới), `tram/suy/giao_viec.py`, `tram/api/luong.py` | 4 (py) | N₀ + 4 (1998) |
| 4 | de | 1 | — | `tram/bao_tin/tin.py`, `tram/bao_tin/nguon.py` | 3 (py) | N₀ + 3 (1997) |
| 6 | de | 2 | 1 | `tram/suy/doi_ngu.py`, `tram/api/doi_ngu.py` | 3 (py) | N₀ + 14 (2008) |
| 7 | de | 2 | 3 | `tram/suy/phe_duyet.py` | 1 (py) | N₀ + 12 (2006) |
| 2 | de | 2 | 1 | `frontend/src/luat_doi_ngu.js`, `src/trang/DoiNgu.vue` | 2 (node) | node M₀ + 2 (35) |
| 5 | de | 2 | 3 | `frontend/src/giao_viec.js`, `src/thanh/TheBead.vue`, `src/thanh/OGiaoViec.vue` | 2 (node) | node M₀ + 2 (35) |

**Tổng cuối:** `uv run pytest -q` = **N₀ + 15** (2009); `npm run kiem` = **M₀ + 4** (37); `npm run build` và `npm run kiem-dist` xanh. Lát 2d có **7 task**.

Không file nào bị hai task cùng đợt sửa. **Đụng chung với nơi khác:**
- Không file nào thuộc danh sách tránh.
- `tram/api/luong.py` chỉ thêm một dòng vào hằng `LOAI_LAM_MOI`.
- `tram/api/doi_ngu.py`, `tram/suy/doi_ngu.py` (2b) chỉ sửa route GET, chữ ký và thân `doi_ngu` (tham số mới có mặc định), thêm `du_hang_khe`; POST khe không đổi. Plan 2f-1 Task 7 sửa tiếp `tram/suy/doi_ngu.py` (khối diff của nó tính trên bản sau Task 6 này), nên 2f làm sau 2d.
- `DoiNgu.vue`, `TheBead.vue`, `OGiaoViec.vue`: 2f làm lại sau khi 2d ghép (D38).

## Để sau (chờ cổng / chờ chốt) — không lập task code ở plan này

Bead `bs-urj.6` và `bs-urj.8` đóng được sau khi ghép Task 1–7; phần làm lại giao diện theo mockup thuộc lát 2f. `bs-urj.7` vẫn mở.

| Phần | Spec | Chờ | Đã chừa sẵn |
|---|---|---|---|
| **Giao diện theo mockup — lát 2f** (D20, D33, D38): làm lại `DoiNgu.vue`, `TheBead.vue`, `OGiaoViec.vue` theo mockup; thẻ Phê duyệt hiện PR trạm từ `chi_tiet.pr_tram` của Task 7 (G21) | 2 §5.2, §5.4 | viết plan 2f (mockup đã duyệt) | hợp đồng ở "Ranh giới 2d ↔ 2f"; luật thuần có test `node`; `pr_tram` dùng lại được |
| **Đèn Điều phối — lát riêng (`bs-urj.7`, D12).** Hook phiên điều phối trên máy A gửi nhịp qua một đường ghi riêng, có xác thực, của tram-api (không dùng Bearer thợ, không dùng header Tailscale trên TCP localhost — spec 2 §4 mục 2b) → sự kiện nhịp; `cac_phong` (`tram/suy/van_phong.py`) trả `sang: true \| false` theo nhịp cuối | 2 §5.5, §14 | **#5/S6** (kênh ghi xác thực, principal), **Tailscale trên máy A (D6)**; plan 2e | `sang: true \| false \| null`; `chuBien`, `Phong3D` đã xử lý cả ba giá trị |
| Q1 — phạm vi "cho SHA" (cùng bead hay mọi bead) | 4 §12 | Đại ca trả lời nếu muốn đổi | `_dau_tien` |
| Chỉ mục `su_kien(loai, id)` nếu bảng điểm chậm | — | có số liệu thật (G9) | `doc_su_kien` gom một lần quét |
| Bảng điểm có số thật; thẻ cột 3 có PR thật | 4 §16 mục 4 | chạy thật: bộ giao việc (`giao_viec.bat` mặc định tắt), 4c GitHub (S7). `/api/giao-viec` rỗng khi `bo_giao` chưa nối | đọc đúng payload producer hiện có |
| Telegram thật cho `pr_da_merge`, `pr_khong_xac_minh` | 2 §6 | #5, bot Telegram | `soan_tin` dùng chung |
| Kiểm tay giao diện (ô lọc, thẻ cột 3, ngăn bên) trên máy A / điện thoại | 2 §9 mục 4 | #5, D6; lát 2f kiểm lại trên giao diện mới | build xanh; luật hiển thị có test node |

## Tự review

**1. Độ phủ phạm vi và quyết định**

| Yêu cầu | Task | Kiểm bằng |
|---|---|---|
| D13, D25, D26, D29 / `bs-urj.6`: "qua lần đầu" | 1 | `test_qua_lan_dau_qc_dau_tien_sau_kiem_lai`: qua; QC đầu trả về; kiểm lại đầu trượt; chưa công bố SHA vẫn ở mẫu; chờ QC vẫn ở mẫu; spike không xử lý riêng; QC bead khác cùng SHA; phiếu `bi` ngoài mẫu; D25 bản `giao.cong_bo` sau cùng; D26 QC ghi trước kiểm lại bị bỏ qua (cả hai chiều: `dat` trước → không qua, `tra_ve` trước → qua) |
| D13, D27 / `bs-urj.6`: "bị trả về" | 1 | `test_bi_tra_ve_moi_lan_vao_cot_3_mot_mau_cua_khe_trong_bang_chung`: trả về trước khi vào cột 3 không tính; quy cho khe trong bằng chứng, không cho khe khác từng code bead; hai lần trả về liền nhau tính một; vào cột 3 lần nữa trước khi bị trả về → chỉ lần sau tính; bằng chứng trỏ phiếu không có → bỏ mẫu |
| D14, D28, D29: lọc dự án + `cap_luc`, mặc định mọi dự án / 30 ngày | 1, 6, 2 | `test_loc_du_an_va_cua_so_theo_luc_cap_phieu`, `test_mac_dinh_moi_du_an_30_ngay_va_loc`, `test_tham_so_sai`; node `đường dẫn bảng điểm…` |
| Spec 2 §5.4: không hiện 0 giả | 1, 2 | `bi_tra_ve` mẫu 0 → `None`; node `ô tỉ lệ bảng điểm kèm (tử/mẫu)…` |
| `bs-urj.8`: dữ liệu thẻ cột 3 có `pr.khong_xac_minh` + lý do | 3 | `test_pr_tram_…` (2), `test_suy_giao_gan_pr_tram_vao_the_cot_3` |
| D20, D38: nhãn / câu của luật thuần đúng mockup (2f giữ nguyên) | 2, 3, 5 | `LY_DO["khong-phai-merge-commit"]` = chữ mockup; node `nhanPrTram, lopPrTram…`, `moTaPrTram, canhBaoPrTram…` |
| D2: thẻ đổi không cần tải lại | 3 | `test_su_kien_pr_lam_moi_bang_qua_sse` |
| D15 / `bs-urj.8`: Telegram "PR đã merge" + "PR không xác minh được" | 4 | `test_hai_su_kien_pr_thanh_tin_pr_mo_thi_khong`, `test_mot_vong_gui_tin_khong_lo_pr_url_sha_ly_do` |
| Spec 2 §6 chống ồn: gom 5 phút, 1 giờ, giờ yên lặng | 4 | `test_chong_on_gom_5_phut_va_gio_yen_lang` (cả hai loại bị giờ yên lặng chặn); vòng thứ hai của `test_mot_vong_…` không gửi lại |
| Spec 2 §4 mục 5: không lộ dữ liệu ra Telegram | 4 | assert tin không chứa `github`, `#7`, `#8`, SHA, merge commit, mã lý do, tên nhánh |
| Spec 2 §4 mục 4: text, link an toàn; tham số API | 3, 5, 6 | `test_pr_tram_loc_du_lieu_la_va_da_merge`; `lopPrTram` từ chối trạng thái lạ; `kiem-an-toan`; `?du_an=` lạ → 404, `?so_ngay=` sai → 422 |
| D38: 2d ghép nguyên văn, chỉ sửa ba file `.vue` nhỏ; giao diện Phê duyệt để 2f | 2, 5 | danh sách "Files" của Task 2, 5; `npm run build`, `kiem-dist` xanh |
| D38 (C6 = có): dữ liệu PR trạm cho trang Phê duyệt | 7 | `test_muc_cho_review_mang_pr_tram`: có `pr_tram` đúng; khoá cũ giữ nguyên; bead chưa vào cột 3 → `null`; mục khác không có khoá |
| D41 (G19 của 2f): bảng điểm có hàng cho khe chưa có phiếu, bộ lọc không làm mất hàng | 6 | `test_moi_khe_da_khai_co_hang_ke_ca_khi_bo_loc_khong_con_phieu`: (khe, vai ưu tiên) chưa có phiếu → hàng 0 phiếu, `coder` mẫu 0, `qc` mẫu `null`; hàng có phiếu ngoài vai ưu tiên vẫn giữ; phiếu ngoài cửa sổ 30 ngày / lọc dự án khác không làm mất hàng |
| D12 / `bs-urj.7`: không làm, ghi "Để sau" | — | G19, "Để sau" |

**2. Quét placeholder:** không có "TBD/TODO/tương tự Task N". File mới có nguyên văn đầy đủ; file có sẵn có bản vá đã `git apply --check` trên `38a016f`; mọi lệnh có kết quả mong đợi. `<model đang thực thi>` là chỗ người thực thi điền — cố ý.

**3. Khớp chữ ký:**
- Bảng điểm (D41): `doi_ngu` gọi `trang_thai_khe` **một lần**, dùng cùng danh sách `ds` cho `khe[]` và `du_hang_khe(bang_diem(...), ds)` → hàng bảng điểm khớp thẻ khe. Khoá của hàng thêm giống hệt khoá `bang_diem` (Task 1) → `oTiLe(null, 0)` = "chưa có", `oTiLe(null, null)` = "—" (Task 2).
- Bảng điểm: `dieu_kien_phieu` dùng chung cho `doc_phieu_code` và câu SELECT trong `bang_diem` → cùng bộ lọc cho mọi cột. `doc_phieu_code(db, du_an, tu)` trả thêm `giao_id` (cho D27) + `doc_su_kien(db, du_an)` → `qua_lan_dau(phieu, sk)`, `bi_tra_ve(phieu, sk)` (Task 1). `bang_diem(db, *, du_an, tu)` ↔ `doi_ngu(..., du_an, so_ngay)` tính `tu = chuoi_gio(...)` (Task 6) ↔ `r_doi_ngu(du_an, so_ngay)` ↔ `duongDanDoiNgu(duAn, soNgay)` sinh `?du_an=&so_ngay=` (Task 2). Khoá `*_mau` ↔ `oTiLe(x, mau)`.
- Thẻ cột 3: `pr_tram(...)` → `{so, url, trang_thai, ly_do}` (Task 3) ↔ `prTram`, `NHAN_PR_TRAM` (ba khoá), `lopPrTram`, `moTaPrTram`, `canhBaoPrTram` (Task 5).
- Telegram: `TIN_PR` hai khoá → hai loại ∈ `LOAI_TIN`, `NHAN_LOAI` (Task 4).
- `LY_DO` khớp 7 mã của `pr_merge.py::ly_do_khong_xac_minh`.
- `NHAN_PR_TRAM` khớp `NHAN_PR` của mockup từng chữ.

**4. Đã chạy thử (16/10, bản D41):** bản sao `main` `503ff64`, cùng script trích khối như bản 15/10. Mốc 1994 / node 33; đợt 1 → 2005; đợt 2: T6 **+3**, T7 +1 → **2009 passed**; T2 +2, T5 +2 → node **37**; build và `kiem-dist` xanh. Thông báo fail ở Step 2 Task 6 là kết quả thật trên main sau đợt 1. Áp tiếp 2e, 2f-1, 2f-2 nguyên văn: xem plan 2f-1.

**4b. Đã chạy thử (15/10, bản sửa D25–D29, D33, D38):**
- Bản sao `main` `38a016f` trong scratchpad, thư mục riêng; không mạng, không Keychain, không `~/.tram` thật, không Telegram thật. Mốc: 1994 / node 33.
- Script trích khối mã từ chính file plan này rồi áp theo thứ tự đợt:
  - đợt 1: T1 +4, T3 +4, T4 +3 → 2005;
  - đợt 2: T6 +2, T7 +1 → **2008 passed**; T2 +2, T5 +2 → node **37**.
- Step 2 của từng task chạy trên đúng trạng thái "main đợt trước" (T2, T5 mỗi task thử riêng); thông báo fail ghi trong plan là kết quả thật.
- `kiem-an-toan`, `npm run build`, `npm run kiem-dist` xanh.
- **Chưa** kiểm giao diện trên trình duyệt (chỉ build + luật thuần). Giao diện 2d sẽ được 2f làm lại.

**5. Rủi ro còn lại (Đại ca biết):**
- (a) Q1 còn mở (không chặn). Đổi Q1 chỉ sửa `_dau_tien`. Q2 đã chốt D41 (G22).
- (b) Theo chữ spec, tỉ lệ "qua lần đầu" tụt tạm thời khi phiếu đang chờ QC (vẫn ở mẫu, chưa vào tử). Spike không bao giờ "qua" vì không có QC.
- (c) D27 đếm theo **lần vào cột 3**, nên một bead bị trả về nhiều vòng tạo nhiều mẫu cho các khe đã đưa nó vào cột 3. Cột "Bị trả về" là tỉ lệ trên lần vào cột 3, không phải trên bead.
- (d) Chưa có dữ liệu thật: bộ giao việc và 4c đang tắt.
- (e) Bảng điểm quét bảng `su_kien` mỗi 5 giây trên mỗi tab đang mở (G9).
- (f) Khoảng 30 dòng `.vue` của Task 2, 5 sẽ bị 2f viết lại (D38 chấp nhận).
- (g) `pr.da_merge` ghi trước `bd close`, nên tin "PR đã merge" có thể đến khi bead chưa đóng.
- (h) Tin PR rơi vào giờ yên lặng bị bỏ, không dồn tới sáng (G16). Với `pr_khong_xac_minh`, Đại ca chỉ thấy nhãn vàng trên thẻ khi mở dashboard (sau 2f: thêm cảnh báo ở Phê duyệt).

## Cần sửa spec sau (không sửa spec đã duyệt trong plan này)

- **Spec 4 §12:** ghi các câu đã chốt D25–D29 (SHA từ `giao.cong_bo` bản sau cùng; QC đầu tiên ghi sau kiểm lại sớm nhất; mỗi lần vào cột 3 là một mẫu của khe trong bằng chứng; lọc theo `cap_luc`; dự án theo phiếu; vai qc/spec `null`).
- **Spec 2 §5.4:** JSON thêm `*_mau`; mẫu 0 hiện "chưa có"; lọc `?du_an=&so_ngay=`, mặc định mọi dự án / 30 ngày (D14); bảng điểm có hàng cho mọi (khe, vai ưu tiên) đã khai, kể cả khi chưa có phiếu (D41).
- **Spec 2 §6:** thêm hai loại tin `pr_da_merge`, `pr_khong_xac_minh` (nguồn `pr.da_merge`, `pr.khong_xac_minh`, chịu giờ yên lặng) vào "Gửi khi" và "Nguồn từng loại tin" (D15).
- **Spec 2 §7:** `GET /api/doi-ngu` có `?du_an=&so_ngay=`; `GET /api/giao-viec` có `pr.tram`; `GET /api/phe-duyet` mục `cho-review` có `chi_tiet.pr_tram`.
- **Spec 2 §5.2:** thẻ cột 3 hiện trạng thái PR trạm (2d); thẻ Phê duyệt hiện trạng thái PR trạm (D38: dữ liệu ở 2d Task 7, giao diện ở 2f); cập nhật dòng §5.2 (4c) ở "Lệch so với spec khi code".
- **Spec 2 §5.5, §14:** nguồn đèn Điều phối = hook phiên điều phối trên máy A (D12), làm ở lát riêng.
- **Spec 2, spec 4 "Trạng thái triển khai":** sau khi ghép 2d, chuyển dòng bảng điểm và dòng thẻ cột 3 sang "đã có mã + test".

## Bổ sung review đợt 4 — cổng D13 và thứ tự

> **Lịch sử.** Cổng S1–S8 dưới đây đã gỡ bằng D25–D29 (15/10). Sơ đồ có hiệu lực ở "Sơ đồ đợt chạy"; C6 đã chốt ở D38 (G21). Đoạn dưới giữ nguyên chữ của review.

S1–S8 không phải lỗi mới do thiếu spike; lỗi là plan đã chọn cách “TẠM” trong code/test dù D13 cấm tự chọn chỗ spec im lặng. Đã đổi gate ngay tại mục câu hỏi. Ví dụ S5 hiện quy trách nhiệm trả về cho cả khe nhận phiếu sau lần trả về đó; S6 hiện tính cửa sổ theo lúc cấp phiếu. Đây là hậu quả của phương án chưa chốt, không phải quyết định mới của review.

**Sơ đồ cập nhật:** đợt 1 được chuẩn bị độc lập T3 (PR), T4 (Telegram); T1 chờ S1–S8. T5 theo T3; T2 và T6 theo T1 và quyết định bộ lọc. Không đổi mã, không thêm test: dự kiến sau toàn lát vẫn N₀+13 Python, M₀+4 node; các số tuyệt đối chỉ là lịch sử. D14 mặc định mọi dự án/30 ngày, D15 cả hai loại tin giữ nguyên. C6 vẫn mở, không tự thêm nút/PR vào màn Phê duyệt.

Hiệu năng cần đo khi triển khai: `doc_su_kien` tải toàn bộ 5 loại sự kiện (không cắt thời gian), `_dau_tien` quét lại cho mỗi phiếu. Không có bằng chứng đạt độ trễ trên lịch sử lớn; không dùng 4 fixture nhỏ để xác nhận hiệu năng. URL PR được lọc scheme/host/path bằng fullmatch; regex chỉ xác minh dạng, không chứng minh PR thuộc repo hoặc SHA — chứng cứ đó thuộc producer 4c. Telegram chỉ lấy mã bead/dự án đã lọc, không gửi URL PR/SHA/lý do.

## Ghi chú triển khai (16/10/2026)

**Code:** cả 7 task (T1–T7) đã ghép vào `main`, theo hai lần ghép.

| Lần ghép | Task | Commit chính | `pytest` trước → sau | node |
|---|---|---|---|---|
| `2c908e3` `merge: 2d/t3t4` | T3 thẻ cột 3 mang PR trạm; T4 tin Telegram PR | `daeae43`, `827f29a` | 2093 → 2100 (+7) | 34 → 34 |
| `1c4fa98` `merge: 2d Task 1, 6, 7, 2, 5` | T1 bảng điểm D25–D29; T6 API lọc + hàng khe đủ (D41); T7 `chi_tiet.pr_tram` ở Phê duyệt; T2 ô lọc bảng điểm; T5 luật PR trạm | `e53594f`, `3a0e560`, `a5ef905`, `57290b9`, `10cf498` | 2130 → 2138 (+8) | 34 → 38 (+4) |

Số test thật theo từng task (đo bằng `pytest --collect-only` và `node --test` trên từng commit, so với commit cha): T1 +4, T3 +4, T4 +3, T6 +3, T7 +1 (Python); T2 +2, T5 +2 (node). Tổng **+15 Python, +4 node**, đúng bảng "Sơ đồ đợt chạy" (N₀ + 15, M₀ + 4). Mốc N₀ lúc bắt đầu là 1994 (`main` `503ff64`). Sau khi cả bốn lát 2d, 2e, 1b-4 và 1a-2 (T1–T3) đã ghép, `main` có **2212 passed, node 38**. Sau lát 2f, `main` có 2242 passed, node 95.

**Chỗ lệch plan khi code:** không có. Em đối chiếu từng dòng thêm của 7 commit với văn bản plan (16/10): mọi dòng thêm đều có nguyên văn trong plan. Danh sách file chạm khớp mục "File Structure". Không có test cũ nào phải sửa ngoài `tests/test_suy_doi_ngu.py` (đã ghi ở Task 1).

**Sau 2d:**
- Lát 2f (Task 7 của 2f-1 sửa tiếp `tram/suy/doi_ngu.py`; các task trang `DoiNgu.vue`, `TheBead.vue`, `OGiaoViec.vue`, Phê duyệt) đã làm lại phần `.vue` theo mockup, giữ nguyên luật thuần JS của 2d (D38).
- Các bead `bs-urj.6` (bảng điểm) và `bs-urj.8` (PR trạm) đã đóng ngày 16/10.

**Còn lại (không phải việc code):** đúng mục "Để sau" ở trên.
- Bảng điểm có số thật và thẻ cột 3 có PR thật: chờ chạy thật (bộ giao việc `giao_viec.bat` mặc định tắt; 4c GitHub chờ S7).
- Tin Telegram thật cho `pr_da_merge`, `pr_khong_xac_minh`: chờ #5 và bot.
- Hiệu năng `doc_su_kien` trên lịch sử lớn: chưa đo (G9). Chưa thêm chỉ mục `su_kien(loai, id)`.
- Đèn Điều phối (`bs-urj.7`, D12) đã tách sang lát 2e.
