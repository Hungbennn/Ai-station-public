# Lát 2f — Giao diện theo mockup: phần 1 — nền và API — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ] **Step N: …**`) syntax for tracking. Hướng dẫn chung khi code: `.handover/qc/huong-dan-code.md` (repo chính). **Mọi dòng mã thêm vào phải có nguyên văn trong plan** — chép đúng khối mã; file sửa thì áp khối `diff` bằng `git apply --check` rồi `git apply`.

> **Sửa 16/10 theo D41** ([chốt đợt 4](../quyet-dinh/2026-10-15-chot-dot-4.md), mục "Chốt câu mở của 5 plan sửa"). Đại ca đã chốt cả ba câu ở "Chờ Đại ca chốt" và các giả định G22, G23, G24, G27:
> - **G19:** đổi API của 2d — `GET /api/doi-ngu` → `bang_diem` đã có hàng cho mọi (khe, vai ưu tiên) của khe đã khai, kèm mẫu 0 (plan 2d Task 6 `du_hang_khe`, G22 của 2d). 2f **bỏ** hàm ghép phía trình duyệt `hangBangDiem` và test của nó (Task 10, phần 2): trang đọc thẳng `bang_diem`. Task 10 còn 4 test node (trước 5).
> - **G21:** lý do tắt khe (`vi_sao`) chỉ hiện ở thẻ khe trang Đội ngũ AI, không hiện trong "Sự kiện gần đây". Mã Task 5 vốn đã không đọc `vi_sao` (mẫu `khe.tat` = "<khe> · Đại ca tắt"), không đổi.
> - **G13:** người điều phối gắn nhãn `san-sang` cho các bead cổng chạy thật khi bắt đầu đợt chạy thật. Không đổi mã.
> - **G22, G23, G24, G27:** giữ như plan.
> - Task 7 sửa `tram/suy/doi_ngu.py` trên bản sau 2d Task 6 mới (có `du_hang_khe`), nên khối diff của Task 7 được sinh lại; nội dung thay đổi của Task 7 giữ nguyên.
> - Chạy thử lại trên `main` `503ff64` + 2d (bản D41) + 2e: N₀ = **2031**, M₀ = **38**; sau 2f: **2061 passed** (N₀ + 30), node **95** (M₀ + 57), build + `kiem-dist` xanh. Xem "Kết quả chạy thử".

**Goal:** Dựng lại dashboard (tram-api + frontend Vue) đúng mockup Đại ca đã duyệt (D20, D33, D39): khung sidebar mới, chín trang, font tự host, bỏ chế độ tối, và các API đọc mới mà mockup cần (`/api/tong-quan`, `/api/su-kien/gan-day`, `/api/cai-dat`, `/api/san-sang`, mô tả sự kiện dễ đọc, trường bổ sung T1/T2/T4/T6).

**Architecture:** Lát chia hai file plan. **File này (phần 1)** làm nền dùng chung và toàn bộ backend: token CSS + font + khung + menu + tìm ⌘K + tuyến (Task 1), thành phần khe dùng chung (Task 2), cổng an toàn CSP mở rộng (Task 3), đọc launchd/Keychain chỉ đọc (Task 4), mô tả sự kiện từ mẫu cố định (Task 5), API Cài đặt + bảng sẵn sàng (Task 6), trường bổ sung cho API có sẵn (Task 7), API Tổng quan + sự kiện gần đây (Task 8). **Phần 2** (`docs/plans/2026-10-16-lat-2f-2-cac-trang.md`) dựng chín trang trên nền này (Task 9–17) và kiểm trên trình duyệt dưới CSP thật (Task 18). Backend chỉ đọc: route `def` đồng bộ, danh sách cho phép từng trường, lệnh ngoài argv hằng số + timeout 3 giây + bộ đệm, không bao giờ trả stdout/stderr/giá trị bí mật. Frontend không thêm gói: icon là `path d` tự vẽ, chibi là SVG, cảnh 3D dùng three/TresJS sẵn có trong chunk nạp lười.

**Tech Stack:** Python 3.12 + FastAPI + pytest (`uv run --offline`); Vue 3.5.43, vue-router 5.4.0, Vite 8.3.4, `@tresjs/core` 5.9.1, `three` 0.186.1; node `--test`.

**Spec / đầu vào:** spec 2 (dashboard) §4, §5, §7; mockup đã duyệt `docs/mockup/2026-10-15-giao-dien/` (D20, D33, D39); khảo sát `docs/handovers/2026-10-15-khao-sat-giao-dien.md`; quyết định `docs/quyet-dinh/2026-10-15-chot-dot-4.md` (D17–D20, D31, D33–D39, D41); plan 2d (`docs/plans/2026-10-15-lat-2d-dashboard-bu-khoang-trong.md`, mục "Ranh giới 2d ↔ 2f"), plan 2e (`docs/plans/2026-10-15-lat-2e-den-dieu-phoi.md`, mục "Ranh giới 2e / 2f"), plan 1a-2 (G26: `du_an[].bat_ghi`), plan 1b-4 (G22: `nho.bo_bi_mat`).

## Global Constraints

- **Mockup là chuẩn hình ảnh.** Mỗi task ghi file và ảnh mockup nó bám. QC đối chiếu ảnh `docs/mockup/2026-10-15-giao-dien/anh-*.png`, không chỉ chạy test.
- **CSP chặt (spec 2 §4 mục 6):** `default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; font-src 'self'`. Không `style="…"` tĩnh trong template `.vue` (Vue 3.5 gộp ≥ 20 nút tĩnh thành chuỗi HTML chèn bằng innerHTML — `style=` trong chuỗi đó bị `style-src 'self'` chặn); giá trị động dùng `:style` (CSSOM, hợp lệ). Không `v-html`/`innerHTML`/`outerHTML`/`insertAdjacentHTML`/`document.write`. Không URL ngoài trong `src/` (trừ link GitHub kiểm bằng `laLinkAnToan`). Không `eval`, `new Function`.
- **Font tự host (D35):** Be Vietnam Pro 400–800, JetBrains Mono 400/500 đã có ở `frontend/src/assets/fonts/` (OFL). Độ đậm mockup 450 → 500, 650 → 600.
- **Chỉ nền sáng** — bỏ chế độ tối (D38).
- **Không thêm phụ thuộc** npm/pypi. Không mạng, không Claude/Codex thật, không Keychain/launchctl/`~/.tram` thật trong test.
- **API mới chỉ đọc:** Host lạ 421, CSP + header an toàn trên mọi phản hồi (qua `GiuaAnToan` sẵn có). Quyền xét theo từng yêu cầu (`la_dai_ca_yeu_cau`). Chỉ trả trường trong danh sách cho phép; chuỗi qua `lam_sach`. Trạng thái launchd và Keychain chỉ "có/chưa/không rõ" — không bao giờ trả giá trị, stdout, stderr, argv, pid. **Không bao giờ gọi `tram tho kiem` hay `tram giao kiem`** (có `sudo`, `touch`, `sleep 30`) từ API.
- **Không sửa** `tram/api/phu_thuoc.py`, `tram/api/tuyen_doc.py` (lát 1a-2 sửa), `tram/chu/cai_dat.py`, `tram/cau_hinh/giao_viec.py` (lát 3c sửa), `tram/su_kien/kho.py`.
- Mỗi file mã mới ≤ ~120 dòng, mỗi dòng ≤ 120 ký tự. Comment và chữ hiển thị tiếng Việt.
- Chunk lười: chỉ `/van-phong` kéo `three`; `kiem-dist` báo lỗi nếu gói chính có `WebGLRenderer`.

## Phụ thuộc đã có — dùng, không sửa trừ chỗ ghi rõ

2f chạy **sau khi** 2d, 2e, 1a-2, 1b-4 đã ghép vào `main` (mốc N₀/M₀ đo sau khi ghép — xem "Chuẩn bị").

| Thứ | Ở đâu | Lát | Dùng ở task |
|---|---|---|---|
| `GiuaAnToan` (Host 421, CSP), `la_dai_ca_yeu_cau`, `yeu_cau_ghi` | `tram/api/bao_mat.py` | 2a | 6, 8 |
| `yeu_cau_dai_ca` (403 khi không phải Đại ca) | `tram/api/tuyen_nho.py` | 1b-3 | 6 |
| Route `phe_duyet(request)`, `du_an(request)`, `trang_thai(request)` (gọi lại như 2c G6) | `tram/api/tuyen_doc.py` | 2a | 8 |
| `r_doi_ngu(request, du_an, so_ngay)`; `the_khe`, `doi_ngu`, `du_hang_khe` (`bang_diem` có hàng mọi khe đã khai — D41) | `tram/api/doi_ngu.py`, `tram/suy/doi_ngu.py` | 2b + 2d T6 | 7, 8, trang 10 |
| `nhan_vat`, `ten_nhan_vat` | `tram/suy/nhan_vat.py` | 2c | 7 |
| `gom_phe_duyet`, `gan_pr_tram` (`chi_tiet.pr_tram`) | `tram/suy/phe_duyet.py` | 2b + 2d T7 | 7 |
| `suc_khoe`, `cac_phong(..., dieu_phoi=)` | `tram/suy/van_phong.py` | 2c + 2e T1 | 7 |
| `doc_dong_usage`, `tong_hop` | `tram/usage/su_kien.py` | 2b | 8 |
| `KhoSuKien.sau_id`, `id_moi_nhat`, `gan_day(..., du_lieu_co=)` | `tram/su_kien/kho.py` | 1a/2a | 5, 7 |
| `su_kien_khe` | `tram/phieu/khe.py` | 3a | 7 |
| `nap_du_an`, `liet_ke_du_an`, `nap_cau_hinh_*`, `doc_bam` (mã Đại ca, mã điều phối 2e T6) | `tram/cau_hinh/*`, `tram/nho/ma_dai_ca.py`, `tram/chu/ma_dieu_phoi.py` | nhiều | 6 |
| `NHAN_LOAI` (có `pr_da_merge`, `pr_khong_xac_minh` của 2d T4) | `tram/bao_tin/tin.py` | 2a + 2d | 6 |
| `Bd(goc_repo()).tat_ca()` (chỉ đọc) | `tram/beads/bd.py` | 0 | 6 |
| `GET /api/du-an` → `du_an[].bat_ghi` | `tram/api/tuyen_doc.py` | **1a-2 Task 5 (G26, D37)** | 8 (đi qua `du_an(request)`), trang 9, 11, 12, 13, 14, 15 |
| Sự kiện `nho.bo_bi_mat {su_kien_id, loai_nguon, nhom}` | `tram/nho/vong.py` | **1b-4 (G22)** | 5 (mẫu câu), 16 |
| `api.js`, `kho.js`, `luat.js`, `luat_doi_ngu.js`, `luat_spec.js`, `giao_viec.js` (2d T5: `prTram`, `nhanPrTram`, `lopPrTram`, `moTaPrTram`, `canhBaoPrTram`, `NHAN_PR_TRAM`), `luat_doi_ngu.js` (2d T2: `oTiLe`, `SO_NGAY_BANG_DIEM`, `duongDanDoiNgu`), `van_phong/hien_thi.js` (2e T4: `chuNhip`, `MAU.den '#f2c14e'`) | `frontend/src/` | 2a–2e | mọi task frontend |

**Phụ thuộc chưa ghép lúc viết plan (đánh dấu rõ):**
- **1a-2 (D37):** frontend đọc `bat_ghi` bằng `d.bat_ghi === false` — thiếu trường (API cũ) coi như đã bật ghi, nên 2f chạy được cả khi 1a-2 chưa ghép; chip "chỉ quét thử" chỉ hiện khi 1a-2 đã ghép. `/api/tong-quan` lấy `du_an[]` bằng chính `du_an(request)` của `tuyen_doc.py` nên tự có `bat_ghi` khi 1a-2 ghép — 2f **không** sửa `tuyen_doc.py`, `phu_thuoc.py`.
- **1b-4 (G22):** mẫu câu `nho.bo_bi_mat` (Task 5) và nhãn "Bỏ vì bí mật" (Task 16) theo đúng tên trường của plan 1b-4; nếu 1b-4 đổi tên trường khi code, phải sửa mẫu trong `tram/suy/mau_nho.py`.

## Câu hỏi / giả định

Cột cuối: **giả định** (Em tự chọn, Đại ca gạch nếu muốn khác) · **HỢP ĐỒNG MỚI** (tên/trường mới các lát sau dựa vào) · **đã chốt** (quyết định nào).

| # | Chủ đề | Plan làm | Lý do | Trạng thái |
|---|---|---|---|---|
| G1 | Font | `@font-face` tự viết cho 21 file woff2 có sẵn (3 bộ ký tự × độ đậm), `font-display: swap`, font hệ thống dự phòng | CSP `font-src 'self'` | đã chốt — D35 |
| G2 | Chế độ tối | Bỏ; `color-scheme: light` | Mockup chỉ có nền sáng | đã chốt — D38 (Q2) |
| G3 | Phần bản thật có mà mockup không vẽ | Giữ bố cục cũ, đổi sang token + lớp mới (hàng Chưa chấm/Feature/Epic, kéo cột + "Vì sao?", Chuyển cột, Bàn giao, Bộ giao việc, Decision/Cờ đỏ/Spec/Feature xong, cảnh báo hạn mức, luật vai) | — | đã chốt — D36 |
| G4 | Dự án `bat_ghi: false` | Chip chữ "chỉ quét thử", thẻ/phòng mờ; nút ghi của dự án đó khoá kèm câu `CHU_CHI_QUET_THU` (server vẫn trả 422) | Không dùng chữ "tạm đóng" | đã chốt — D37; phụ thuộc 1a-2 G26 |
| G5 | Ô tìm ⌘K | Tìm phía trình duyệt: dự án (`kho.trangThai`), bead (`/api/cong-viec`), khe (`/api/doi-ngu`) — tải khi focus, giữ 30 giây; không dấu; tối đa 8 kết quả | Không cần API mới | đã chốt — D38 (Q5); phạm vi tìm: giả định |
| G6 | Số việc chờ | Badge menu + huy hiệu Giám đốc giữ `so` của `/api/phe-duyet`; Tổng quan hiện 5 ô riêng (gồm cột 2) và số tổng = `so` kèm chữ "chờ ở Phê duyệt" | spec 2 §5.2 | đã chốt — D38 (Q6) |
| G7 | PR trạm ở Phê duyệt | Thẻ "Chờ review để đóng" có chip PR, link "PR #n ↗", cảnh báo không xác minh, nút theo trạng thái | Mockup đã duyệt | đã chốt — D38 (Q7) |
| G8 | Bấm nhân vật / phòng | Mở panel trước, nút trong panel mới dẫn đi | Mockup | đã chốt — D38 (Q8) |
| G9 | Hơn 3 dự án | Ô dự án theo thứ tự (-1,0), (0,-1), (1,-1) rồi thêm hàng phía sau (z = -2, -3…), camera tự khít | Mockup chỉ vẽ 3 | đã chốt — D38 (Q9); thứ tự ô: giả định |
| G10 | Tủ máy chủ | `suc_khoe.muc[] {mau, ly_do}` — tủ i màu `muc[i]`, thiếu → xanh | Mockup mỗi tủ một màu | đã chốt — D38 (Q10); **HỢP ĐỒNG MỚI** T6 |
| G11 | "Phiên 1/2" | "1 phiên đang chạy" / "Không có phiên" | Spec 3 không có số phiên tối đa | đã chốt — D38 (Q11) |
| G12 | Dữ liệu Tổng quan | `GET /api/tong-quan` gom bằng chính các hàm route có sẵn + `GET /api/su-kien/gan-day` | Một lần gọi mỗi 5 giây | đã chốt — D38 (Q12); **HỢP ĐỒNG MỚI** |
| G13 | Cài đặt + bảng sẵn sàng | Chỉ Đại ca (403). Sẵn sàng = bead repo trạm có nhãn `san-sang` (đọc `bd` chỉ đọc) + mục tự kiểm rẻ (lệnh trong PATH, dịch vụ đã cài, Keychain) | — | đã chốt — D38 (Q13); **ĐÃ CHỐT D41**: người điều phối gắn nhãn `san-sang` cho các bead cổng chạy thật khi bắt đầu đợt chạy thật; **HỢP ĐỒNG MỚI** `/api/cai-dat`, `/api/san-sang` |
| G14 | Thứ tự với 2d/2e | Ghép 2d/2e nguyên văn trước, 2f làm lại `.vue` của chúng; luật thuần giữ | — | đã chốt — D38 (Q14) |
| G15 | Không có danh tính Đại ca | Thẻ người dùng "Chỉ đọc · không có danh tính Đại ca", nút ghi khoá | — | đã chốt — D38 (Q15) |
| G16 | Đường dẫn Ký ức | Giữ `/nho`, thêm bí danh `/ky-uc`; menu trỏ `/ky-uc` | Link cũ từ máy A, Telegram | đã chốt — D38 (Q16) |
| G17 | Bóng đổ | `PCFShadowMap` + `shadow.radius`, so ảnh ở Task 18 | three 0.186 bỏ `PCFSoftShadowMap` | đã chốt — D38 (Q17) |
| G18 | Đèn Điều phối | Vàng ấm `#f2c14e` phát sáng khi `sang`, xám khi không; chữ như `chuBien`; dòng "nhịp cuối" (`chuNhip`) ở panel và bản danh sách | — | đã chốt — D38 (Q18) |
| G19 | Câu Q2 của plan 2d: hàng khe 0 phiếu | **Đổi API 2d** (plan 2d Task 6, G22): `GET /api/doi-ngu` → `bang_diem` có một hàng cho mỗi (khe, vai ưu tiên) của mọi khe đã khai — cùng danh sách `trang_thai_khe` với `khe[]`; hàng chưa có phiếu: 0 phiếu, coder mẫu 0 ("chưa có"), vai khác mẫu `null` ("—"); bộ lọc dự án / số ngày không làm mất hàng. 2f đọc thẳng `dl.bang_diem`, **không** ghép phía trình duyệt (bỏ `hangBangDiem`) | Mockup có hàng `codex-2 coder 0`; Đại ca chọn đổi API | **ĐÃ CHỐT D41** |
| G20 | Mô tả sự kiện | Mẫu câu cố định theo loại (`tram/suy/mau_su_kien.py`, `mau_nho.py`), chỉ ghép mã khe, mã bead, lượt, bước, cột, kết luận, mã lý do → câu hằng; trường lạ → "?"; loại lạ → "". Không bao giờ đưa chữ tự do (`vi_sao`, `gop_y`, `loi`, `tra_loi`, `noi_dung`, `ly_do` tự do, `tieu_de`, nội dung ký ức) | D39 | đã chốt — D39; **HỢP ĐỒNG MỚI** trường `mo_ta` |
| G21 | Lý do tắt khe trong "Sự kiện gần đây" | Mockup ghi "claude-3 · Đại ca tắt (để dành)"; plan **bỏ phần ngoặc** vì `vi_sao` là chữ tự do (khảo sát A3): mẫu `khe.tat` = "<khe> · Đại ca tắt", không đọc `vi_sao` (Task 5). `vi_sao` chỉ hiện ở thẻ khe trang Đội ngũ AI (`vi_sao_tat`, T1, đã `lam_sach`, ≤ 120) | An toàn hơn chữ mockup | **ĐÃ CHỐT D41** |
| G22 | Lọc sự kiện ồn | "Sự kiện gần đây" bỏ `dieu_phoi.nhip`, `khe.han_muc`, `khe.han_muc_khong_ro` (nhịp, hạn mức đổi mỗi vài giây/phút) | Ranh giới 2e/2f khuyên bỏ `dieu_phoi.nhip` | **ĐÃ CHỐT D41** — giữ như plan |
| G23 | "Mới xong" theo dự án | Chỉ ở `/api/tong-quan` (`du_an[].moi_xong`), bead `closed` có `closed_at` lớn nhất trong bộ đệm beads; không thêm vào `/api/du-an` | Tránh sửa `tuyen_doc.py` (1a-2 đang sửa) | **ĐÃ CHỐT D41** — giữ như plan; **HỢP ĐỒNG MỚI** |
| G24 | Trạng thái dịch vụ công khai | `/api/tong-quan` trả `dich_vu[{nhan, viec, da_cai, dang_chay}]` cho mọi người xem (nhãn cố định, chỉ boolean); chi tiết đầy đủ ở `/api/cai-dat` chỉ Đại ca | Khảo sát A4 | **ĐÃ CHỐT D41** — giữ như plan |
| G25 | Cách đọc launchd / Keychain | `launchctl print gui/<uid>/<nhãn>` (mã 0 → đọc `state = running`), file plist trong `~/Library/LaunchAgents`; `security find-generic-password -s <tên>` **không** `-w` (0 có, 44 chưa, khác không rõ). Timeout 3 giây, bộ đệm 30/60 giây, chạy tuần tự | Khảo sát §1.6, §1.10 | **giả định** |
| G26 | Trường bổ sung | T1 `khe[].ten`, `khe[].vi_sao_tat`; T2 `nhan_vat[].cau_dao_ngat`; T4 mục escalation/decision `chi_tiet.cau_hoi` (+ escalation `khe_id`, `buoc`, `bead_goc`); T6 `suc_khoe.muc`. T3 chuyển vào `/api/tong-quan` (G23); T5 gộp vào T4; T7 ghép phía trình duyệt | Khảo sát §1.10 | **HỢP ĐỒNG MỚI** |
| G27 | Escalation ở Phê duyệt | Nút "Trả lời" dẫn sang ngăn bên trang Công việc (nơi có ô trả lời) như mockup; bỏ ô trả lời ngay trong mục | Mockup Phê duyệt đã duyệt | **ĐÃ CHỐT D41** — giữ như plan |
| G28 | Đăng ký route | `/api/cai-dat`, `/api/san-sang` dùng `cai_dat.router` riêng, đăng ký trong `app.py` ở T6; `/api/tong-quan`, `/api/su-kien/gan-day` đăng ký `tong_quan.router` trong cùng file ở T8 | T8 ghép sau T6, giữ cả hai router | **giả định** |
| G29 | Lệnh kiểm sẵn sàng hiện trên trang | `uv run tram giao kiem` và `bd list --status open --label san-sang` (thay `--parent bs-8eh` của mockup cho khớp nguồn G13) — chỉ hiện để Đại ca tự chạy | — | **giả định** |
| G30 | Tiêu đề tab | "(n) <tên trang> · Ben Station" | Mockup app.js | **giả định** (đổi chữ của 2a) |

## Chờ Đại ca chốt — ĐÃ CHỐT D41 (16/10)

Không còn câu nào chờ. Ghi lại câu hỏi và lựa chọn của Đại ca:
1. ~~**G19 — hàng khe 0 phiếu ở bảng điểm**~~ (Q2 của plan 2d). Em từng đề xuất ghép phía trình duyệt. **D41: đổi API của 2d** — `bang_diem` trả đủ mọi khe đã khai, kèm mẫu 0 (plan 2d Task 6, G22). 2f đọc thẳng, bỏ `hangBangDiem` (Task 10).
2. ~~**G21 — lý do tắt khe trong "Sự kiện gần đây"**~~. **D41: theo đề xuất** — `vi_sao` chỉ hiện ở thẻ khe Đội ngũ AI, không hiện trong danh sách sự kiện.
3. ~~**G13 — ai gắn nhãn `san-sang` cho bead repo trạm**~~. **D41: theo đề xuất** — người điều phối gắn nhãn cho các bead cổng chạy thật (bs-g28.*, bs-8eh.*, bs-6o0.11, bs-urj.4, bs-hpc.5) khi bắt đầu đợt chạy thật; chưa gắn thì bảng chỉ có mục tự kiểm.
4. **G22, G23, G24, G27:** D41 giữ như plan.

## Hợp đồng (lát 2f) — dùng chung hai file plan

**API mới / trường mới** (backend phần 1; trang phần 2 đọc đúng tên này):

```json
GET /api/su-kien/gan-day?gioi_han=20          (1–50, công khai; mới nhất trước; bỏ dieu_phoi.nhip, khe.han_muc*)
{"su_kien": [{"id": 812, "luc": "2026-10-15T15:12:00Z", "loai": "chay.bat_dau", "du_an": "hr-codex",
              "bead_id": "hr-1", "tac_nhan": "tho/B/claude-1", "mo_ta": "B/claude-1 · lượt 2"}]}
  nho.* khi không phải Đại ca: "mo_ta": "Ký ức: chỉ Đại ca xem chi tiết."

GET /api/tong-quan                              (công khai)
{"phe_duyet": {"muc": [...], "so": 4, "loi": {}},                    // y như GET /api/phe-duyet
 "du_an": [{...như GET /api/du-an (có bat_ghi khi 1a-2 ghép)..., "moi_xong": {"id", "tieu_de", "luc"} | null}],
 "tram": {"estop": false, "la_dai_ca": true},
 "doi_ngu": {"bat": true, "khe": [...như GET /api/doi-ngu khe[], có ten, vi_sao_tat...]},
 "usage": {"theo_nguon": [...], "theo_ngay": [...]},                  // hôm nay (giờ VN), dòng như /api/usage
 "dich_vu": [{"nhan": "vn.tram.api", "viec": "dashboard + API", "da_cai": true, "dang_chay": true | false | null}],
 "su_kien": [...≤ 18 như gan-day...], "doc_luc": "<ISO>"}

GET /api/cai-dat                                (chỉ Đại ca; khác → 403 {"detail": "..."})
{"du_an": [{"ten", "duong_dan": "~/...", "nhanh_chinh", "gitnexus": str | null, "lenh_cho_phep": [str],
            "hang_rao": [{"loai", "tu_khoa": [str], "duong_dan": [str]}], "moi_truong_kiem": bool, "loi": str | null}],
 "dich_vu": [{"nhan", "viec", "da_cai", "dang_chay": bool | null, "kiem_duoc": bool}],
 "telegram": {"co_chat_id": bool, "gio_yen_lang": str | null, "loai_tin": [str]},
 "co": [{"khoa", "bat": bool | null, "gia_tri": str | null, "ghi_chu"}],
 "keychain": [{"ten", "trang_thai": "co" | "chua" | "khong_ro"}], "loi_cau_hinh": [str]}

GET /api/san-sang                               (chỉ Đại ca)
{"muc": [{"ma": "bs-8eh.17" | "—", "ten", "trang_thai": "dat" | "thieu" | "cho", "ghi_chu", "nguon": "bead" | "tu_kiem"}],
 "dem": {"dat", "thieu", "cho"}, "doc_luc": "<ISO>", "loi": str | null}

Của 2d (đọc, không sửa ở 2f — D41):
  /api/doi-ngu   bang_diem[] có hàng cho mọi (khe, vai ưu tiên) của khe đã khai (plan 2d Task 6, G22);
                 hàng chưa có phiếu: so_phieu 0, coder *_mau 0 (→ "chưa có"), vai khác *_mau null (→ "—")

Trường bổ sung (chỉ THÊM khoá):
  /api/doi-ngu   khe[].ten ("Claude 1"), khe[].vi_sao_tat (str ≤ 120 | null — chỉ khi trang_thai "tat")       T1
  /api/van-phong nhan_vat[].cau_dao_ngat (bool)                                                              T2
  /api/phe-duyet mục escalation|decision: chi_tiet.cau_hoi (≤ 300, bỏ dòng máy ly_do/bead_goc/giao_id/mốc);
                 mục escalation: chi_tiet.khe_id, chi_tiet.buoc, chi_tiet.bead_goc (str | null)               T4
  /api/van-phong phòng may-chu: suc_khoe.muc [{"mau": "do" | "vang", "ly_do"}] (cùng thứ tự, cùng cắt ly_do)  T6
  /api/nho/su-kien su_kien[].mo_ta (câu từ mẫu cố định, D39); giữ tom_tat                                     D39
```

**Nền frontend (Task 1–2) — tên trang phần 2 dùng:**
- CSS toàn cục (import ở `main.js`): `kieu/font-be-vietnam.css`, `kieu/font-mono.css`, `kieu/nen.css` (token `--nen --nen-2 --nen-3 --the --vien --vien-dam --chu --chu-2 --chu-phu --nhan --nhan-dam --nhan-nhat --xanh --vang --do --tim --xam`, nền cảnh báo, lệnh; `.mono .cham(.xanh .do .xam) .an-chu`), `kieu/khung.css`, `kieu/chung.css` (`.trang .dau-trang .nho .loi .the .mo h2.muc .so .so-dem .tieu-de-khoi .lk-phai select .o textarea .truong .nhom-nut .nut(.chinh .nguy) .hang-nut .chip(.mono) .tt-lam .tt-ranh .tt-can_nguoi .tt-loi .tt-tat .tt-cau_dao .tt-mat_ket_noi .pr-da_merge .pr-khong_xac_minh .pr-mo .chu-do .bang .bang-cuon .canh-bao .cot-rong .cho-chot .the-chan .van-ban .nen-mo .hop`). CSS riêng mỗi trang: `kieu/<trang>.css`, import trong `<script setup>` của trang. `button` không có kiểu mặc định ngoài font/cursor — mọi nút mang lớp.
- JS: `dinh_dang.js` (`gon soDayDu usd gioPhut ngayGio ngayNgan truocDay conLai gioReset`), `menu.js` (`MENU mucCua tenTrang`), `bieu_tuong.js` (`BIEU_TUONG duongVe`), `tim.js` (`timKiem laPhimTim`), `estop.js` (`dungEstop`), `luat.js` thêm `tieuDeTab(so, ten)`, `duAnChiQuetThu(dsDuAn) -> Set`, `CHU_CHI_QUET_THU`; `mau_khe.js` (`BANG_MAU fnv1a mauKhe`), `luat_han_muc.js` (`cuaSo oHanMuc hanMucThapNhat tenKhe`).
- Component: `thanh/DauTrang.vue` (props `tieuDe`, `moTa`; slot `cong-cu`, `sau-tieu-de`), `thanh/BieuTuong.vue` (`ten`), `thanh/Chibi.vue` (`kheId`, `mo`), `thanh/ThanhHanMuc.vue` (`ten`, `cuaSo`), `thanh/ThanhBen.vue`, `thanh/ThanhTren.vue`, `thanh/OTim.vue`, `thanh/BangEstop.vue`, `KhungChinh.vue`. Trang giữ chỗ `trang/TongQuan.vue`, `trang/CaiDat.vue` (Task 13, 14 thay toàn bộ).

## Ranh giới

| Với | 2f làm | 2f không làm |
|---|---|---|
| 2d | Làm lại `.vue` của 2d T2 (`DoiNgu.vue`), T5 (`TheBead.vue`, `OGiaoViec.vue`) theo mockup; đọc `chi_tiet.pr_tram`; đọc thẳng `bang_diem` (hàng khe 0 phiếu do 2d trả — G19, D41) | Không đổi luật thuần (`oTiLe`, `prTram`…), backend, Telegram của 2d; không ghép hàng bảng điểm phía trình duyệt (D41) |
| 2e | Biển phòng / panel / danh sách hiện đèn Điều phối theo `sang` + `chuNhip`; màu `MAU.den` giữ `#f2c14e` | Không đổi `POST /api/dieu-phoi/nhip`, hook máy A; không có ô đèn ở Tổng quan; "Sự kiện gần đây" bỏ `dieu_phoi.nhip` |
| 1a-2 | Đọc `du_an[].bat_ghi` (chip, khoá nút) | Không sửa `tuyen_doc.py`, `phu_thuoc.py`, `tuyen_ghi.py` |
| 1b-4 | Mẫu câu `nho.bo_bi_mat`, nhãn "Bỏ vì bí mật", thêm loại vào `/api/nho/su-kien` | Không sửa `tram/nho/*` |
| 3c | Đọc `nap_cau_hinh_giao_viec().bat`, `nap_cau_hinh_cach_ly()` | Không sửa `tram/chu/cai_dat.py`, `tram/cau_hinh/giao_viec.py`; không gọi `tram giao kiem` |
| Chạy thật | Task 18 chỉ kiểm trên `127.0.0.1` của máy B với dữ liệu giả (`tests/chay_thu_giao_dien.py`) | Kiểm qua tailnet (máy A, điện thoại) chờ 2a T26 (bs-6o0.11) như mọi phần dashboard |

## File Structure

```
tram/
  suy/he_thong.py            (mới, T4)  đọc launchd + Keychain, bộ đệm
  suy/mo_ta_su_kien.py       (mới, T5)  kiểm dạng + mo_ta()
  suy/mau_su_kien.py         (mới, T5)  mẫu câu phần 0–4
  suy/mau_nho.py             (mới, T5)  mẫu câu nho.*, may.*, …
  suy/su_kien_gan_day.py     (mới, T5)  gan_day()
  suy/cai_dat.py             (mới, T6)  gom cấu hình cho /api/cai-dat
  suy/san_sang.py            (mới, T6)  bảng sẵn sàng
  suy/phe_duyet_bi.py        (mới, T7)  T4: câu hỏi + khe/bước/bead gốc của escalation
  suy/moi_xong.py            (mới, T8)  "Mới xong" theo dự án
  suy/doi_ngu.py, nhan_vat.py, phe_duyet.py, van_phong.py   (sửa, T7)
  api/cai_dat.py             (mới, T6)  GET /api/cai-dat, /api/san-sang
  api/tuyen_chu.py           (sửa, T6)  include_router(cai_dat.router)
  api/tong_quan.py           (mới, T8)  GET /api/tong-quan, /api/su-kien/gan-day
  api/app.py                 (sửa, T8)  CAC_TUYEN += (tong_quan.router,)
  api/tuyen_nho.py           (sửa, T5)  mo_ta, nho.bo_bi_mat
frontend/
  kiem-an-toan.mjs, kiem-dist.mjs        (sửa, T3)
  index.html                             (sửa, T1)
  src/kieu/{font-be-vietnam,font-mono,nen,khung,chung}.css   (mới, T1) · khe.css (T2) · <trang>.css (T9–T17)
  src/{bieu_tuong,menu,tim,dinh_dang,estop}.js               (mới, T1)
  src/{mau_khe,luat_han_muc}.js                              (mới, T2)
  src/luat_{cong_viec,the_khe,phe_duyet,tong_quan,cai_dat,du_an,usage}.js   (mới, T9–T17); nho.js (sửa, T16)
  src/KhungChinh.vue, main.js, tuyen.js, kho.js, luat.js     (sửa, T1)
  src/thanh/{BieuTuong,DauTrang,ThanhBen,ThanhTren,OTim,BangEstop}.vue       (mới, T1) · {Chibi,ThanhHanMuc}.vue (T2)
  src/thanh/phe_duyet/*, tong_quan/*, cai_dat/*, usage/*, LenhCli.vue        (mới, T11, T13, T14, T17)
  src/trang/*.vue                        (viết lại, T9–T17)
  src/van_phong/*                        (viết lại / mới / xoá, T12)
  src/kieu.css, thanh/ThanhTrangThai.vue, thanh/MucPheDuyet.vue, van_phong/{NhanVat3D,Phong3D,TheChu3D}.vue,
  van_phong/the_chu.js                   (xoá)
tests/  test_he_thong.py, test_mo_ta_su_kien.py, test_api_cai_dat.py, test_san_sang.py, test_truong_2f.py,
        test_api_tong_quan.py, chay_thu_giao_dien.py + du_lieu_giao_dien.py (T18, không phải test pytest)
frontend/tests/  khung, dinh_dang, khe_chung, kiem_an_toan, cong_viec, doi_ngu_2f, phe_duyet, van_phong_canh,
                 tong_quan, cai_dat, du_an, ky_uc, usage (.test.mjs, mới); luat, kiem_dist, van_phong (sửa)
```

## Chuẩn bị (người điều phối)

1. Ghép đủ 2d (Task 1–7), 2e (Task 1–4, 6), 1a-2, 1b-4 vào `main`. Ghép xong mới tạo worktree 2f.
2. Đo mốc trên `main` lúc bắt đầu: `uv run --offline pytest -q` → **N₀**; `cd frontend && npm ci --offline --ignore-scripts && npm run kiem` → **M₀** test node. Chạy thử của plan này (bản D41: main `503ff64` + 2d bản D41 + 2e, **chưa** có mã 1a-2/1b-4): N₀ = **2031**, M₀ = **38** (bản trước D41 trên `a3c10ee`: 2030 / 38 — 2d D41 thêm 1 test py). Khi 1a-2 và 1b-4 đã ghép, N₀ lớn hơn — mọi số "N₀ + k" trong plan vẫn đúng theo k.
3. Mỗi task một worktree từ `main` của đợt trước, một commit. Không cần `npm install` (không thêm gói); frontend `npm ci --offline --ignore-scripts`.
4. Font: không tải gì — 21 file woff2 + OFL đã có ở `frontend/src/assets/fonts/` (D35).

### Task 1: Nền giao diện — token, font, khung sidebar, thanh trên, tìm ⌘K, tuyến mới

**Đợt:** 1 · **Độ khó:** vừa · **Phải xong trước:** 2d, 2e, 1a-2, 1b-4 đã ghép · **Test mới:** 7 node (khung 3, định dạng 3, luat +1)

**Mockup bám:** `index.html` (khung sidebar | thanh trên | băng estop | trang), `style.css` (`:root`, "Sidebar", "Thanh trên", "Trang", chip / nút / bảng / cảnh báo, `@media 900px`), `app.js` (bảng icon `I`, `MENU`, ⌘K, estop, `document.title`), ảnh `anh-tong-quan.png` và mọi ảnh trang (khung giống nhau). Thẻ người dùng khi không có danh tính: G15. Ô tìm: G5.

**Files:**
- Create: `frontend/src/kieu/font-be-vietnam.css`, `frontend/src/kieu/font-mono.css` (21 `@font-face`, unicode-range lấy từ `assets/fonts/tham-khao-fontsource-*.css`), `frontend/src/kieu/nen.css`, `frontend/src/kieu/khung.css`, `frontend/src/kieu/chung.css`, `frontend/src/bieu_tuong.js`, `frontend/src/menu.js`, `frontend/src/tim.js`, `frontend/src/dinh_dang.js`, `frontend/src/estop.js`, `frontend/src/thanh/BieuTuong.vue`, `frontend/src/thanh/DauTrang.vue`, `frontend/src/thanh/ThanhBen.vue`, `frontend/src/thanh/ThanhTren.vue`, `frontend/src/thanh/OTim.vue`, `frontend/src/thanh/BangEstop.vue`, `frontend/src/trang/TongQuan.vue` (giữ chỗ — Task 13 thay), `frontend/src/trang/CaiDat.vue` (giữ chỗ — Task 14 thay)
- Modify: `frontend/src/KhungChinh.vue` (viết lại hẳn — khối diff), `frontend/src/main.js` (import CSS mới; `scrollBehavior` cuộn lên đầu khi đổi trang), `frontend/src/tuyen.js`, `frontend/src/kho.js` (bỏ đặt tiêu đề tab), `frontend/src/luat.js` (`tieuDeTab`, `duAnChiQuetThu`, `CHU_CHI_QUET_THU`), `frontend/index.html` (`<title>`), `frontend/vite.config.js` (`assetsInlineLimit: 0` — Vite mặc định nhúng tài nguyên < 4 kB thành `data:`; file JetBrains Mono tiếng Việt ~3,9 kB khi đó bị CSP `font-src 'self'` chặn — lỗi này tìm ra khi chạy thử trên trình duyệt)
- Delete: `frontend/src/kieu.css` (có chế độ tối — D38), `frontend/src/thanh/ThanhTrangThai.vue` (tách thành ThanhTren + BangEstop + `estop.js`, logic `bam()` giữ nguyên)
- Test: `frontend/tests/khung.test.mjs` (mới), `frontend/tests/dinh_dang.test.mjs` (mới), `frontend/tests/luat.test.mjs` (sửa)

**Interfaces:**
- Produces: xem "Hợp đồng (lát 2f)" mục "Nền frontend". `tieuDeTab(so, ten = 'Tổng quan') -> "(n) <ten> · Ben Station"`; `duAnChiQuetThu(dsDuAn) -> Set<string>` (`bat_ghi === false`); `timKiem(q, {duAn, the, khe}) -> [{loai, nhan, phu, den}]` (≤ 8); `gon(n)` ("4,20 tr"), `gioReset(iso, bayGio)` ("23:40" | "T2 07:00"); `dungEstop() -> {dangGui, thongBao, bam(laEstop)}`.
- Consumes: `kho` (`trangThai`, `soPheDuyet`, `matKetNoi`, `loi`, `moLuong`), `api.js`.

Ghi chú: sau Task 1 các trang cũ vẫn chạy (logic không đổi) nhưng mất kiểu cũ cho tới khi Task 9–17 làm lại từng trang. Bố cục `#app` là lưới 272 px | 1fr; dưới 900 px sidebar thành khối phía trên, menu xếp hàng ngang. `/` và đường lạ chuyển về `/tong-quan` (D17).

- [ ] **Step 1: Viết test (chép nguyên văn)**

`frontend/tests/dinh_dang.test.mjs` (mới):

```js
import assert from 'node:assert/strict'
import { test } from 'node:test'
import { conLai, gioPhut, gioReset, gon, ngayGio, ngayNgan, soDayDu, truocDay, usd } from '../src/dinh_dang.js'

test('số gọn như mockup Usage (D39)', () => {
  assert.equal(gon(4_200_000), '4,20 tr')
  assert.equal(gon(212_345), '212 n')
  assert.equal(gon(1_250_000_000), '1,25 tỷ')
  assert.equal(gon(999), '999')
  assert.equal(gon(null), '—')
  assert.equal(soDayDu(4200000), (4200000).toLocaleString('vi-VN'))
  assert.equal(usd(3.1), '$3.10')
  assert.equal(usd(0.4213), '$0.4213')
  assert.equal(usd(null), 'chưa có giá')
})

test('giờ theo Asia/Ho_Chi_Minh', () => {
  assert.equal(gioPhut('2026-10-15T15:14:00Z'), '22:14')
  assert.equal(gioPhut('2026-10-15T17:05:00Z'), '00:05')
  assert.equal(ngayGio('2026-10-15T13:58:00Z'), '15/10 20:58')
  assert.equal(ngayNgan('2026-10-02'), '02/10')
  assert.equal(gioPhut(null), '')
  assert.equal(gioPhut('rác'), '')
})

test('trước đây, còn lại, giờ reset', () => {
  const bay = '2026-10-15T15:17:00Z'
  assert.equal(truocDay('2026-10-15T15:16:54Z', bay), '6 giây trước')
  assert.equal(truocDay('2026-10-15T15:14:00Z', bay), '3 phút trước')
  assert.equal(truocDay('2026-10-13T15:14:00Z', bay), '2 ngày trước')
  assert.equal(truocDay('2026-10-16T00:00:00Z', bay), '')
  assert.equal(conLai('2026-10-15T17:12:00Z', bay), 'còn 2 giờ')
  assert.equal(conLai('2026-10-15T15:30:00Z', bay), 'còn 13 phút')
  assert.equal(conLai('2026-10-15T15:00:00Z', bay), '')
  assert.equal(gioReset('2026-10-15T16:40:00Z', bay), '23:40')
  assert.equal(gioReset('2026-10-19T00:00:00Z', bay), 'T2 07:00')
  assert.equal(gioReset(null, bay), '—')
})
```

`frontend/tests/khung.test.mjs` (mới):

```js
import assert from 'node:assert/strict'
import { test } from 'node:test'
import { BIEU_TUONG, duongVe } from '../src/bieu_tuong.js'
import { MENU, mucCua, tenTrang } from '../src/menu.js'
import { laPhimTim, timKiem } from '../src/tim.js'

test('menu 9 mục đúng thứ tự mockup, bí danh /nho và / ', () => {
  assert.deepEqual(MENU.map((m) => m.ten), ['Tổng quan', 'Dự án', 'Văn phòng', 'Công việc', 'Đội ngũ AI', 'Ký ức',
    'Usage & chi phí', 'Phê duyệt', 'Cài đặt'])
  assert.equal(mucCua('/nho').ma, 'ky-uc')
  assert.equal(mucCua('/').ma, 'tong-quan')
  assert.equal(mucCua('/cong-viec?du_an=hr&bead=hr-1').ma, 'cong-viec')
  assert.equal(mucCua('/phan-luong'), null)
  assert.equal(tenTrang('/doi-ngu'), 'Đội ngũ AI')
  assert.equal(tenTrang('/la'), 'Ben Station')
})

test('mỗi mục menu có icon; icon chỉ gồm lệnh path hợp lệ', () => {
  for (const m of MENU) assert.ok(duongVe(m.ma).length > 0, m.ma)
  for (const [ten, ds] of Object.entries(BIEU_TUONG)) {
    for (const d of ds) assert.match(d, /^[MmLlHhVvCcSsQqTtAaZz0-9 .,-]+$/, ten)
  }
  assert.deepEqual(duongVe('khong-co'), [])
})

test('tìm ⌘K: không dấu, dự án → bead → khe, tối đa 8', () => {
  const dl = { duAn: ['hr-codex', 'tram'], the: [{ id: 'hr-3', du_an: 'hr-codex', tieu_de: 'Chọn cách tính thuế' }],
    khe: [{ khe_id: 'B/codex-1', ten: 'Codex 1', ten_goi_nho: 'codex-chinh' }] }
  assert.deepEqual(timKiem('thue', dl).map((k) => k.den),
    [{ path: '/cong-viec', query: { du_an: 'hr-codex', bead: 'hr-3' } }])
  assert.deepEqual(timKiem('hr', dl).map((k) => k.loai), ['du-an', 'bead'])
  assert.deepEqual(timKiem('codex 1', dl)[0],
    { loai: 'khe', nhan: 'Codex 1', phu: 'B/codex-1', den: { path: '/doi-ngu' } })
  assert.deepEqual(timKiem('  ', dl), [])
  const nhieu = { the: Array.from({ length: 12 }, (_, i) => ({ id: `x-${i}`, du_an: 'x', tieu_de: 'việc' })) }
  assert.equal(timKiem('viec', nhieu).length, 8)
  assert.equal(laPhimTim({ metaKey: true, key: 'k' }), true)
  assert.equal(laPhimTim({ ctrlKey: true, key: 'K' }), true)
  assert.equal(laPhimTim({ key: 'k' }), false)
})
```

`frontend/tests/luat.test.mjs` (sửa):

```diff
diff --git a/frontend/tests/luat.test.mjs b/frontend/tests/luat.test.mjs
index f258e7a..73bdd1c 100644
--- a/frontend/tests/luat.test.mjs
+++ b/frontend/tests/luat.test.mjs
@@ -1,7 +1,8 @@
 import assert from 'node:assert/strict'
 import { test } from 'node:test'
 import { ghi, thanGhi } from '../src/api.js'
-import { choPhepKeo, gioVN, khoaMucPheDuyet, laLinkAnToan, nhomPheDuyet, nhomTheoHang, tieuDeTab } from '../src/luat.js'
+import { choPhepKeo, duAnChiQuetThu, gioVN, khoaMucPheDuyet, laLinkAnToan, nhomPheDuyet, nhomTheoHang, tieuDeTab }
+  from '../src/luat.js'
 
 test('nhomTheoHang xếp thẻ theo hàng và ưu tiên; hàng lạ về chưa chấm', () => {
   const n = nhomTheoHang([{ id: 'b', hang: 'ai-lam', uu_tien: 2 }, { id: 'a', hang: 'ai-lam', uu_tien: 1 },
@@ -21,8 +22,8 @@ test('choPhepKeo chỉ giữa cột 1 và cột 2', () => {
 })
 
 test('tiêu đề tab và link an toàn', () => {
-  assert.equal(tieuDeTab(0), 'Bàn điều hành')
-  assert.equal(tieuDeTab(3), '(3) Bàn điều hành')
+  assert.equal(tieuDeTab(0), 'Tổng quan · Ben Station')
+  assert.equal(tieuDeTab(3, 'Phê duyệt'), '(3) Phê duyệt · Ben Station')
   assert.equal(laLinkAnToan('https://github.com/o/r/pull/7'), true)
   assert.equal(laLinkAnToan('javascript:alert(1)'), false)
   assert.equal(laLinkAnToan('http://github.com/o/r/pull/7'), false)
@@ -66,3 +67,9 @@ test('ghi gửi X-Tram và ném lỗi kèm status', async () => {
   assert.equal(goi.opt.headers['X-Tram'], '1')
   assert.equal(goi.opt.body, '{"a":1}')
 })
+
+test('duAnChiQuetThu chỉ lấy dự án bat_ghi === false', () => {
+  const ds = [{ ten: 'hr', bat_ghi: true }, { ten: 'kt', bat_ghi: false }, { ten: 'cu' }]
+  assert.deepEqual([...duAnChiQuetThu(ds)], ['kt'])
+  assert.deepEqual([...duAnChiQuetThu(null)], [])
+})
```

- [ ] **Step 2: Chạy thấy FAIL**

```bash
cd frontend && node --test tests/dinh_dang.test.mjs tests/khung.test.mjs tests/luat.test.mjs
```

Kỳ vọng: FAIL — `Error [ERR_MODULE_NOT_FOUND]: Cannot find module '…/frontend/src/dinh_dang.js' imported from …/frontend/tests/dinh_dang.test.mjs`

- [ ] **Step 3: Viết mã (chép nguyên văn; file sửa: chép khối diff ra file tạm, `git apply --check` rồi `git apply`)**

`frontend/index.html` (sửa):

```diff
diff --git a/frontend/index.html b/frontend/index.html
index 19d01ff..1abfb32 100644
--- a/frontend/index.html
+++ b/frontend/index.html
@@ -3,7 +3,7 @@
   <head>
     <meta charset="utf-8">
     <meta name="viewport" content="width=device-width, initial-scale=1">
-    <title>Bàn điều hành</title>
+    <title>Ben Station</title>
   </head>
   <body>
     <div id="app"></div>
```

`frontend/src/KhungChinh.vue` (sửa):

```diff
diff --git a/frontend/src/KhungChinh.vue b/frontend/src/KhungChinh.vue
index b41953f..dc34873 100644
--- a/frontend/src/KhungChinh.vue
+++ b/frontend/src/KhungChinh.vue
@@ -1,27 +1,30 @@
 <script setup>
-import { onMounted } from 'vue'
+import { computed, onMounted, watch } from 'vue'
+import { useRoute } from 'vue-router'
+import { dungEstop } from './estop.js'
 import { kho, moLuong, taiSoPheDuyet, taiTrangThai } from './kho.js'
-import ThanhTrangThai from './thanh/ThanhTrangThai.vue'
+import { tieuDeTab } from './luat.js'
+import { tenTrang } from './menu.js'
+import BangEstop from './thanh/BangEstop.vue'
+import ThanhBen from './thanh/ThanhBen.vue'
+import ThanhTren from './thanh/ThanhTren.vue'
 
+// Khung mockup (index.html): sidebar | thanh trên + băng estop + trang. Tiêu đề tab "<trang> · Ben Station".
+const route = useRoute()
+const estop = dungEstop()
+const khoa = computed(() => !(kho.trangThai && kho.trangThai.la_dai_ca) || estop.dangGui.value)
 onMounted(() => { taiTrangThai(); taiSoPheDuyet(); moLuong() })
+watch([() => route.path, () => kho.soPheDuyet],
+  () => { document.title = tieuDeTab(kho.soPheDuyet, tenTrang(route.path)) }, { immediate: true })
 </script>
 
 <template>
-  <header class="dau">
-    <nav class="menu" aria-label="Menu chính">
-      <router-link to="/cong-viec">Công việc</router-link>
-      <router-link to="/du-an">Dự án</router-link>
-      <router-link to="/phe-duyet">Phê duyệt
-        <span v-if="kho.soPheDuyet" class="dem" :aria-label="kho.soPheDuyet + ' việc chờ'">{{ kho.soPheDuyet }}</span>
-      </router-link>
-      <router-link to="/nho">Ký ức</router-link>
-      <router-link to="/doi-ngu">Đội ngũ AI</router-link>
-      <router-link to="/usage">Usage</router-link>
-      <router-link to="/van-phong">Văn phòng</router-link>
-    </nav>
-    <ThanhTrangThai />
-  </header>
-  <p v-if="kho.matKetNoi" class="canh-bao" role="status">Mất kết nối luồng sự kiện — đang thử lại…</p>
-  <p v-if="kho.loi" class="loi" role="alert">{{ kho.loi }}</p>
-  <main><router-view /></main>
+  <ThanhBen />
+  <div class="khung">
+    <ThanhTren :estop="estop" />
+    <BangEstop v-if="kho.trangThai && kho.trangThai.estop" :khoa="khoa" @tiep-tuc="estop.bam(false)" />
+    <p v-if="estop.thongBao.value" class="loi-chung" role="alert">{{ estop.thongBao.value }}</p>
+    <p v-if="kho.loi" class="loi-chung" role="alert">{{ kho.loi }}</p>
+    <main class="trang"><router-view /></main>
+  </div>
 </template>
```

`frontend/src/bieu_tuong.js` (mới):

```js
// Icon nét mảnh của mockup (app.js `I`, D20) đổi hết sang `path d` — vẽ bằng <path v-for>, không chuỗi SVG,
// không chèn HTML thô (spec 2 §4 mục 4). Nét do lớp .bieu-tuong (kieu/khung.css).
const BANH_RANG = 'M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3'
  + ' 1.7 1.7 0 0 0-1 1.5V21'
  + 'a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8'
  + ' 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1'
  + 'a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1'
  + 'a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z'
const KHUNG = 'M5 3h14a2 2 0 0 1 2 2v14a2 2 0 0 1 -2 2h-14a2 2 0 0 1 -2 -2v-14a2 2 0 0 1 2 -2z'
const HUY_HIEU = 'M12 2.5l2.3 1.7 2.8-.2.9 2.7 2.3 1.6-.9 2.7.9 2.7-2.3 1.6-.9 2.7-2.8-.2L12 21.5l-2.3-1.7-2.8.2-.9-2.7'
  + 'L3.7 15.7l.9-2.7-.9-2.7 2.3-1.6.9-2.7 2.8.2z'

export const BIEU_TUONG = {
  'tong-quan': [KHUNG, 'M3 9h18M9 21V9'],
  'du-an': ['M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v3', 'M3 7v11a2 2 0 0 0 2 2h7',
    'M15 17.5a2.5 2.5 0 1 0 5 0a2.5 2.5 0 1 0 -5 0', 'M17.5 13.5v1.5M17.5 20v1.5M13.5 17.5H15M20 17.5h1.5'],
  'van-phong': ['M4 21V5a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v16', 'M16 9h3a1 1 0 0 1 1 1v11',
    'M2 21h20M8 7h1M11 7h1M8 11h1M11 11h1M8 15h1M11 15h1'],
  'cong-viec': [KHUNG, 'M8 7v7M12 7v4M16 7v9'],
  'doi-ngu': ['M8 8h8a3 3 0 0 1 3 3v5a3 3 0 0 1 -3 3h-8a3 3 0 0 1 -3 -3v-5a3 3 0 0 1 3 -3z', 'M12 8V5M10 4h4',
    'M8.5 13a1 1 0 1 0 2 0a1 1 0 1 0 -2 0', 'M13.5 13a1 1 0 1 0 2 0a1 1 0 1 0 -2 0', 'M3 12v3M21 12v3'],
  'ky-uc': ['M12 5a3 3 0 0 0-5.8-1A3 3 0 0 0 4 8a3 3 0 0 0 .5 5.5A3.5 3.5 0 0 0 9 19a3 3 0 0 0 3-1',
    'M12 5a3 3 0 0 1 5.8-1A3 3 0 0 1 20 8a3 3 0 0 1-.5 5.5A3.5 3.5 0 0 1 15 19a3 3 0 0 1-3-1V5'],
  usage: ['M3 3v18h18', 'M7 16v-3M11 16V9M15 16v-5M19 16V6'],
  'phe-duyet': [HUY_HIEU, 'm8.5 12 2.5 2.5 4.5-5'],
  'cai-dat': ['M9 12a3 3 0 1 0 6 0a3 3 0 1 0 -6 0', BANH_RANG],
  tim: ['M4 11a7 7 0 1 0 14 0a7 7 0 1 0 -14 0', 'm20 20-3.5-3.5'],
  estop: ['M12 3v8', 'M6.3 6.3a8 8 0 1 0 11.4 0'],
  khoa: ['M7 11h10a2 2 0 0 1 2 2v5a2 2 0 0 1 -2 2h-10a2 2 0 0 1 -2 -2v-5a2 2 0 0 1 2 -2z', 'M8 11V8a4 4 0 0 1 8 0v3'],
}

export function duongVe(ten) {
  return BIEU_TUONG[ten] ?? []
}
```

`frontend/src/dinh_dang.js` (mới):

```js
// Định dạng số / giờ dùng chung các trang mới (mockup: "1,84 tr", "212 n", "22:14", "3 phút trước", "T2 07:00").
// Giờ luôn theo Asia/Ho_Chi_Minh như gioVN (luat.js). Hàm thuần, test bằng node --test.
const VN = 'Asia/Ho_Chi_Minh'
const THU = ['CN', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7']

const phan = (iso) => {
  const d = new Date(iso)
  if (!iso || Number.isNaN(d.getTime())) return null
  const p = Object.fromEntries(new Intl.DateTimeFormat('en-GB', { timeZone: VN, hour12: false, weekday: 'short',
    year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
    .formatToParts(d).map((x) => [x.type, x.value]))
  const thu = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].indexOf(p.weekday)
  return { ...p, hour: p.hour === '24' ? '00' : p.hour, thu }
}

// Số gọn của mockup Usage (D39): ≥ 1 tỷ "x,xx tỷ"; ≥ 1 triệu "x,xx tr"; ≥ 1 nghìn "n n"; không phải số → "—".
export function gon(n) {
  if (typeof n !== 'number' || Number.isNaN(n)) return '—'
  const a = Math.abs(n)
  if (a >= 1e9) return `${(n / 1e9).toFixed(2).replace('.', ',')} tỷ`
  if (a >= 1e6) return `${(n / 1e6).toFixed(2).replace('.', ',')} tr`
  if (a >= 1e3) return `${Math.round(n / 1e3)} n`
  return String(n)
}

export function soDayDu(n) {
  return typeof n === 'number' ? n.toLocaleString('vi-VN') : '—'
}

export function usd(x) {
  if (typeof x !== 'number') return 'chưa có giá'
  return `$${x < 1 && x > 0 ? x.toFixed(4) : x.toFixed(2)}`
}

export function gioPhut(iso) {
  const p = phan(iso)
  return p ? `${p.hour}:${p.minute}` : ''
}

export function ngayGio(iso) {
  const p = phan(iso)
  return p ? `${p.day}/${p.month} ${p.hour}:${p.minute}` : ''
}

export function ngayNgan(isoNgay) {
  const m = /^(\d{4})-(\d{2})-(\d{2})/.exec(String(isoNgay || ''))
  return m ? `${m[3]}/${m[2]}` : ''
}

// "6 giây trước", "3 phút trước", "2 giờ trước", "4 ngày trước"; tương lai hoặc lỗi → "".
export function truocDay(iso, bayGio = new Date()) {
  const giay = Math.floor((new Date(bayGio).getTime() - new Date(iso).getTime()) / 1000)
  if (!iso || Number.isNaN(giay) || giay < 0) return ''
  if (giay < 60) return `${giay} giây trước`
  if (giay < 3600) return `${Math.floor(giay / 60)} phút trước`
  if (giay < 86400) return `${Math.floor(giay / 3600)} giờ trước`
  return `${Math.floor(giay / 86400)} ngày trước`
}

// "còn 2 giờ", "còn 15 phút" tới mốc; đã qua → "".
export function conLai(iso, bayGio = new Date()) {
  const phut = Math.ceil((new Date(iso).getTime() - new Date(bayGio).getTime()) / 60000)
  if (!iso || Number.isNaN(phut) || phut <= 0) return ''
  return phut < 60 ? `còn ${phut} phút` : `còn ${Math.round(phut / 60)} giờ`
}

// Giờ reset hạn mức: trong 24 giờ tới → "23:40", xa hơn → "T2 07:00" (mockup Đội ngũ AI).
export function gioReset(iso, bayGio = new Date()) {
  const p = phan(iso)
  if (!p) return '—'
  const xa = new Date(iso).getTime() - new Date(bayGio).getTime() > 86400000
  return xa ? `${THU[p.thu]} ${p.hour}:${p.minute}` : `${p.hour}:${p.minute}`
}
```

`frontend/src/estop.js` (mới):

```js
// Bật estop / tiếp tục từ thanh trên và băng estop (logic giữ nguyên ThanhTrangThai.vue cũ của lát 2a).
import { ref } from 'vue'
import { ghi, thanGhi } from './api.js'
import { kho, taiTrangThai } from './kho.js'

export function dungEstop() {
  const dangGui = ref(false)
  const thongBao = ref('')
  async function bam(laEstop) {
    const tt = kho.trangThai
    if (!tt || (laEstop && !window.confirm('Bật estop: dừng mọi lượt quét ngay?'))) return
    dangGui.value = true
    try {
      await ghi(laEstop ? '/api/chu/estop' : '/api/chu/tiep-tuc', thanGhi({}, tt.estop ? 'bat' : 'tat'))
      thongBao.value = ''
      await taiTrangThai()
    } catch (e) {
      thongBao.value = e.message
    } finally {
      dangGui.value = false
    }
  }
  return { dangGui, thongBao, bam }
}
```

`frontend/src/kho.js` (sửa):

```diff
diff --git a/frontend/src/kho.js b/frontend/src/kho.js
index a1301a6..190ff44 100644
--- a/frontend/src/kho.js
+++ b/frontend/src/kho.js
@@ -1,7 +1,6 @@
 // Trạng thái dùng chung giữa các trang; mọi trạng thái nghiệp vụ tính ở server (Q12).
 import { reactive } from 'vue'
 import { doc } from './api.js'
-import { tieuDeTab } from './luat.js'
 import { laSuKienNho } from './nho.js'
 
 export const kho = reactive({ trangThai: null, soPheDuyet: 0, phienBan: 0, phienBanNho: 0, phienBanDoiNgu: 0, suKienCuoi: null,
@@ -19,7 +18,6 @@ export async function taiSoPheDuyet() {
   try {
     const r = await doc('/api/phe-duyet')
     kho.soPheDuyet = r.so
-    document.title = tieuDeTab(r.so)
   } catch (e) {
     kho.loi = e.message
   }
```

`frontend/src/kieu/chung.css` (mới):

```css
/* Lớp dùng chung mọi trang (mockup style.css "Trang", chip trạng thái, PR, bảng, cảnh báo). */
.trang { padding: 18px 30px 40px; min-width: 0; }
.dau-trang {
  display: flex; align-items: flex-end; gap: 18px; padding-bottom: 14px; border-bottom: 1px solid var(--vien);
  margin-bottom: 18px; flex-wrap: wrap;
}
.dau-trang h1 { margin: 0 0 4px; font-size: 30px; font-weight: 800; letter-spacing: -.6px; }
.dau-trang p { margin: 0; color: var(--chu-2); font-size: 14px; }
.dau-trang .cong-cu {
  margin-left: auto; display: flex; gap: 10px; align-items: center; flex-wrap: wrap; justify-content: flex-end;
}
.nho { color: var(--chu-phu); font-size: 13px; }
.loi { color: var(--do); font-size: 13.5px; }
.the {
  background: var(--the); border: 1px solid var(--vien); border-radius: 12px; padding: 14px 16px;
  box-shadow: 0 1px 0 #00000005;
}
.the.mo, .mo { opacity: .6; }
h2.muc { font-size: 17px; margin: 26px 0 10px; display: flex; align-items: center; gap: 8px; }
h2.muc .so, .so-dem {
  font-size: 12px; background: var(--nhan-nhat); color: var(--nhan); border-radius: 999px; padding: 1px 8px;
  font-weight: 700;
}
.tieu-de-khoi { margin: 0 0 10px; font-size: 16px; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.tieu-de-khoi .lk-phai { margin-left: auto; font-size: 13px; color: var(--chu-phu); text-decoration: none; }
select, .o {
  font: inherit; font-size: 13.5px; color: var(--chu); background: var(--the); border: 1px solid var(--vien-dam);
  border-radius: 8px; height: 32px; padding: 0 10px;
}
textarea {
  font: inherit; font-size: 14px; color: var(--chu); border: 1px solid var(--vien-dam); border-radius: 8px;
  padding: 8px 10px; resize: vertical; min-height: 54px; width: 100%; background: var(--the);
}
.truong { display: flex; flex-direction: column; gap: 4px; font-size: 13px; font-weight: 600; color: var(--chu-2); }
.truong .o, .truong select, .truong textarea, .truong input { width: 100%; font-weight: 400; }
.nhom-nut { display: inline-flex; border: 1px solid var(--vien-dam); border-radius: 8px; overflow: hidden;
  background: var(--the); }
.nhom-nut button { border: 0; background: none; padding: 0 12px; height: 30px; font-size: 13px; color: var(--chu-2); }
.nhom-nut button + button { border-left: 1px solid var(--vien); }
.nhom-nut button.chon { background: var(--nhan); color: #fff; font-weight: 600; }
.nut {
  display: inline-flex; align-items: center; justify-content: center; gap: 6px; text-decoration: none;
  border: 1px solid var(--vien-dam); background: var(--the); color: var(--chu); border-radius: 8px;
  height: 32px; padding: 0 13px; font-size: 13.5px; font-weight: 600; white-space: nowrap;
}
.nut:hover { border-color: var(--chu-phu); }
.nut.chinh { background: var(--nhan); border-color: var(--nhan); color: #fff; }
.nut.chinh:hover { background: var(--nhan-dam); }
.nut.nguy { color: var(--do); border-color: #e3bcb1; }
.nut:disabled { opacity: .45; cursor: not-allowed; }
.hang-nut { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin: 10px 0; }
.chip {
  display: inline-flex; align-items: center; gap: 5px; font-size: 12px; font-weight: 600; border-radius: 999px;
  padding: 2px 9px; background: var(--nen-2); color: var(--chu-2); border: 1px solid var(--vien); white-space: nowrap;
}
.chip.mono { font-weight: 500; }
.chip .cham { margin: 0; width: 7px; height: 7px; background: currentColor; }
.tt-lam { background: #e5f2e8; color: #2f6f45; border-color: #c4e0cc; }
.tt-ranh { background: #f1ece4; color: #6e5d50; }
.tt-can_nguoi, .tt-loi { background: #fbe3dc; color: #a2321f; border-color: #f0c2b4; }
.tt-tat { background: #eeecea; color: #7d7670; }
.tt-cau_dao { background: #fbefd9; color: #9a6510; border-color: #efd8a8; }
.tt-mat_ket_noi { background: #ece8f6; color: #5a4b97; border-color: #d7d0ee; }
.pr-da_merge { background: #e5f2e8; color: #2f6f45; border-color: #c4e0cc; }
.pr-khong_xac_minh { background: #fbefd9; color: #9a6510; border-color: #efd8a8; }
.pr-mo { background: #e6eef6; color: #3b6187; }
.chu-do { color: var(--do); font-weight: 700; }
.bang { width: 100%; border-collapse: collapse; font-size: 13.5px; }
.bang th, .bang td { text-align: left; padding: 8px 10px; border-bottom: 1px solid var(--vien); }
.bang thead th { font-size: 12px; color: var(--chu-phu); font-weight: 600; text-transform: uppercase;
  letter-spacing: .4px; }
.bang td.so { font-variant-numeric: tabular-nums; }
.bang tr:last-child td, .bang tr:last-child th { border-bottom: 0; }
.bang a { color: var(--nhan); text-decoration: none; }
.bang th a { color: var(--chu); font-weight: 700; }
.bang-cuon { overflow-x: auto; }
.canh-bao {
  font-size: 13px; color: var(--chu-canh-bao); background: var(--nen-canh-bao); border: 1px solid var(--vien-canh-bao);
  border-radius: 8px; padding: 6px 10px; margin: 6px 0 0;
}
.cot-rong {
  color: var(--chu-phu); font-size: 13px; text-align: center; padding: 30px 10px;
  border: 1.5px dashed var(--vien-dam); border-radius: 10px;
}
.cho-chot {
  border: 1.5px dashed var(--vien-dam); border-radius: 16px; padding: 60px 30px; text-align: center;
  color: var(--chu-2);
  background: repeating-linear-gradient(135deg, #fbf7f1 0 14px, #f7f0e6 14px 28px);
}
.cho-chot strong { display: block; font-size: 18px; color: var(--chu); margin-bottom: 6px; }
.the-chan { border-left: 5px solid var(--do); padding: 18px 20px; max-width: 760px; }
.the-chan strong { font-size: 17px; }
.the-chan p { color: var(--chu-2); margin: 6px 0 12px; }
.van-ban { white-space: pre-wrap; overflow-wrap: anywhere; font-family: inherit; margin: 0; }
.nen-mo { position: fixed; inset: 0; z-index: 60; display: grid; place-items: center; padding: 16px;
  background: #2f262266; }
.hop { background: var(--the); border-radius: 14px; padding: 18px 20px; width: min(480px, 100%);
  box-shadow: 0 10px 30px #5a3a2230; }
.hop h2 { margin: 0 0 10px; font-size: 18px; }
@media (max-width: 900px) { .trang { padding: 16px; } }
```

`frontend/src/kieu/font-be-vietnam.css` (mới):

```css
/* Be Vietnam Pro tự host (D35, OFL — assets/fonts/OFL-be-vietnam-pro.txt). CSP font-src 'self': không tải ngoài. */
@font-face { font-family: 'Be Vietnam Pro'; font-weight: 400; font-style: normal; font-display: swap;
  src: url(../assets/fonts/be-vietnam-pro-vietnamese-400-normal.woff2) format('woff2');
  unicode-range: U+0102-0103,U+0110-0111,U+0128-0129,U+0168-0169,U+01A0-01A1,U+01AF-01B0,U+0300-0301,U+0303-0304,
    U+0308-0309,U+0323,U+0329,U+1EA0-1EF9,U+20AB; }
@font-face { font-family: 'Be Vietnam Pro'; font-weight: 500; font-style: normal; font-display: swap;
  src: url(../assets/fonts/be-vietnam-pro-vietnamese-500-normal.woff2) format('woff2');
  unicode-range: U+0102-0103,U+0110-0111,U+0128-0129,U+0168-0169,U+01A0-01A1,U+01AF-01B0,U+0300-0301,U+0303-0304,
    U+0308-0309,U+0323,U+0329,U+1EA0-1EF9,U+20AB; }
@font-face { font-family: 'Be Vietnam Pro'; font-weight: 600; font-style: normal; font-display: swap;
  src: url(../assets/fonts/be-vietnam-pro-vietnamese-600-normal.woff2) format('woff2');
  unicode-range: U+0102-0103,U+0110-0111,U+0128-0129,U+0168-0169,U+01A0-01A1,U+01AF-01B0,U+0300-0301,U+0303-0304,
    U+0308-0309,U+0323,U+0329,U+1EA0-1EF9,U+20AB; }
@font-face { font-family: 'Be Vietnam Pro'; font-weight: 700; font-style: normal; font-display: swap;
  src: url(../assets/fonts/be-vietnam-pro-vietnamese-700-normal.woff2) format('woff2');
  unicode-range: U+0102-0103,U+0110-0111,U+0128-0129,U+0168-0169,U+01A0-01A1,U+01AF-01B0,U+0300-0301,U+0303-0304,
    U+0308-0309,U+0323,U+0329,U+1EA0-1EF9,U+20AB; }
@font-face { font-family: 'Be Vietnam Pro'; font-weight: 800; font-style: normal; font-display: swap;
  src: url(../assets/fonts/be-vietnam-pro-vietnamese-800-normal.woff2) format('woff2');
  unicode-range: U+0102-0103,U+0110-0111,U+0128-0129,U+0168-0169,U+01A0-01A1,U+01AF-01B0,U+0300-0301,U+0303-0304,
    U+0308-0309,U+0323,U+0329,U+1EA0-1EF9,U+20AB; }
@font-face { font-family: 'Be Vietnam Pro'; font-weight: 400; font-style: normal; font-display: swap;
  src: url(../assets/fonts/be-vietnam-pro-latin-ext-400-normal.woff2) format('woff2');
  unicode-range: U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1D00-1DBF,
    U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF; }
@font-face { font-family: 'Be Vietnam Pro'; font-weight: 500; font-style: normal; font-display: swap;
  src: url(../assets/fonts/be-vietnam-pro-latin-ext-500-normal.woff2) format('woff2');
  unicode-range: U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1D00-1DBF,
    U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF; }
@font-face { font-family: 'Be Vietnam Pro'; font-weight: 600; font-style: normal; font-display: swap;
  src: url(../assets/fonts/be-vietnam-pro-latin-ext-600-normal.woff2) format('woff2');
  unicode-range: U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1D00-1DBF,
    U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF; }
@font-face { font-family: 'Be Vietnam Pro'; font-weight: 700; font-style: normal; font-display: swap;
  src: url(../assets/fonts/be-vietnam-pro-latin-ext-700-normal.woff2) format('woff2');
  unicode-range: U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1D00-1DBF,
    U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF; }
@font-face { font-family: 'Be Vietnam Pro'; font-weight: 800; font-style: normal; font-display: swap;
  src: url(../assets/fonts/be-vietnam-pro-latin-ext-800-normal.woff2) format('woff2');
  unicode-range: U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1D00-1DBF,
    U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF; }
@font-face { font-family: 'Be Vietnam Pro'; font-weight: 400; font-style: normal; font-display: swap;
  src: url(../assets/fonts/be-vietnam-pro-latin-400-normal.woff2) format('woff2');
  unicode-range: U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,
    U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD; }
@font-face { font-family: 'Be Vietnam Pro'; font-weight: 500; font-style: normal; font-display: swap;
  src: url(../assets/fonts/be-vietnam-pro-latin-500-normal.woff2) format('woff2');
  unicode-range: U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,
    U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD; }
@font-face { font-family: 'Be Vietnam Pro'; font-weight: 600; font-style: normal; font-display: swap;
  src: url(../assets/fonts/be-vietnam-pro-latin-600-normal.woff2) format('woff2');
  unicode-range: U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,
    U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD; }
@font-face { font-family: 'Be Vietnam Pro'; font-weight: 700; font-style: normal; font-display: swap;
  src: url(../assets/fonts/be-vietnam-pro-latin-700-normal.woff2) format('woff2');
  unicode-range: U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,
    U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD; }
@font-face { font-family: 'Be Vietnam Pro'; font-weight: 800; font-style: normal; font-display: swap;
  src: url(../assets/fonts/be-vietnam-pro-latin-800-normal.woff2) format('woff2');
  unicode-range: U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,
    U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD; }
```

`frontend/src/kieu/font-mono.css` (mới):

```css
/* JetBrains Mono tự host (D35, OFL — assets/fonts/OFL-jetbrains-mono.txt). */
@font-face { font-family: 'JetBrains Mono'; font-weight: 400; font-style: normal; font-display: swap;
  src: url(../assets/fonts/jetbrains-mono-vietnamese-400-normal.woff2) format('woff2');
  unicode-range: U+0102-0103,U+0110-0111,U+0128-0129,U+0168-0169,U+01A0-01A1,U+01AF-01B0,U+0300-0301,U+0303-0304,
    U+0308-0309,U+0323,U+0329,U+1EA0-1EF9,U+20AB; }
@font-face { font-family: 'JetBrains Mono'; font-weight: 500; font-style: normal; font-display: swap;
  src: url(../assets/fonts/jetbrains-mono-vietnamese-500-normal.woff2) format('woff2');
  unicode-range: U+0102-0103,U+0110-0111,U+0128-0129,U+0168-0169,U+01A0-01A1,U+01AF-01B0,U+0300-0301,U+0303-0304,
    U+0308-0309,U+0323,U+0329,U+1EA0-1EF9,U+20AB; }
@font-face { font-family: 'JetBrains Mono'; font-weight: 400; font-style: normal; font-display: swap;
  src: url(../assets/fonts/jetbrains-mono-latin-ext-400-normal.woff2) format('woff2');
  unicode-range: U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1D00-1DBF,
    U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF; }
@font-face { font-family: 'JetBrains Mono'; font-weight: 500; font-style: normal; font-display: swap;
  src: url(../assets/fonts/jetbrains-mono-latin-ext-500-normal.woff2) format('woff2');
  unicode-range: U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1D00-1DBF,
    U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF; }
@font-face { font-family: 'JetBrains Mono'; font-weight: 400; font-style: normal; font-display: swap;
  src: url(../assets/fonts/jetbrains-mono-latin-400-normal.woff2) format('woff2');
  unicode-range: U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,
    U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD; }
@font-face { font-family: 'JetBrains Mono'; font-weight: 500; font-style: normal; font-display: swap;
  src: url(../assets/fonts/jetbrains-mono-latin-500-normal.woff2) format('woff2');
  unicode-range: U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,
    U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD; }
```

`frontend/src/kieu/khung.css` (mới):

```css
/* Khung: sidebar, thanh trên, ô tìm ⌘K, Estop (mockup style.css "Sidebar", "Thanh trên"; anh-tong-quan.png). */
.sidebar {
  position: sticky; top: 0; height: 100vh; background: var(--nen-2);
  border-right: 1px solid var(--vien); display: flex; flex-direction: column;
}
.ws { display: flex; align-items: center; gap: 9px; padding: 12px 12px 13px; border-bottom: 1px solid var(--vien); }
.ws-logo {
  width: 30px; height: 30px; border-radius: 8px; background: var(--nhan); color: #fff;
  display: grid; place-items: center; font-weight: 800; font-size: 14px; flex: none;
}
.ws-ten { display: flex; flex-direction: column; line-height: 1.15; min-width: 0; flex: 1; white-space: nowrap; }
.ws-ten strong { font-size: 16px; font-weight: 700; letter-spacing: -.2px; }
.ws-ten span { font-size: 10.5px; color: var(--chu-2); overflow: hidden; text-overflow: ellipsis; }
.ws-huy-hieu {
  margin-left: auto; background: var(--nen-huy-hieu); color: var(--nhan-dam); font-weight: 700; font-size: 11.5px;
  padding: 3px 7px; border-radius: 6px; white-space: nowrap; flex: none;
}
.menu { padding: 18px 9px; display: flex; flex-direction: column; gap: 4px; overflow-y: auto; }
.menu a {
  display: flex; align-items: center; gap: 13px; padding: 10px 14px; border-radius: 9px;
  color: var(--chu); text-decoration: none; font-size: 16px; font-weight: 500;
}
.menu a:hover { background: var(--nen-hover); }
.menu a.chon { background: var(--nhan); color: #fff; font-weight: 600; box-shadow: 0 1px 2px #7f321a40; }
.bieu-tuong {
  width: 19px; height: 19px; fill: none; stroke: currentColor; stroke-width: 1.6;
  stroke-linecap: round; stroke-linejoin: round; flex: none;
}
.menu .dem {
  margin-left: auto; background: var(--nhan); color: #fff; font-size: 11px; font-weight: 700;
  min-width: 20px; height: 20px; border-radius: 10px; display: grid; place-items: center; padding: 0 6px;
}
.menu a.chon .dem { background: #fff; color: var(--nhan); }
.sb-day {
  margin-top: auto; border-top: 1px solid var(--vien); padding: 10px 9px; display: flex; flex-direction: column;
  gap: 8px;
}
.may-tram { font-size: 12px; color: var(--chu-2); background: var(--nen-may); border-radius: 7px; padding: 7px 10px; }
.may-tram b { font-weight: 500; color: var(--chu); margin-left: 6px; }
.nguoi-dung {
  display: flex; align-items: center; gap: 10px; background: var(--the); border: 1px solid var(--vien);
  border-radius: 10px; padding: 8px 10px;
}
.nguoi-dung div:last-child { display: flex; flex-direction: column; line-height: 1.25; }
.nguoi-dung strong { font-size: 14px; }
.nguoi-dung span { font-size: 11px; color: var(--chu-2); }
.avatar {
  width: 32px; height: 32px; border-radius: 50%; background: var(--chu); color: #fff;
  display: grid; place-items: center; font-size: 12px; font-weight: 700; flex: none;
}
.avatar.chi-doc { background: var(--xam); }
.khung { min-width: 0; display: flex; flex-direction: column; min-height: 100vh; }
.thanh-tren {
  position: sticky; top: 0; z-index: 20; height: 54px; flex: none; display: flex; align-items: center; gap: 16px;
  padding: 0 22px 0 30px; background: var(--nen); border-bottom: 1px solid var(--vien);
}
.tim {
  position: relative; display: flex; align-items: center; gap: 10px; flex: 0 1 720px; height: 36px; padding: 0 14px;
  background: var(--the); border: 1px solid var(--vien-dam); border-radius: 999px;
}
.tim .bieu-tuong { width: 16px; height: 16px; stroke: var(--chu-2); stroke-width: 2; }
.tim input { border: 0; outline: 0; background: none; flex: 1; min-width: 0; font: inherit; font-size: 14px;
  color: var(--chu); }
.tim input::placeholder { color: var(--chu-phu); }
.tim:focus-within { border-color: var(--nhan); box-shadow: 0 0 0 3px #9a3f2218; }
.ket-qua-tim {
  position: absolute; left: 0; right: 0; top: 40px; z-index: 30; margin: 0; padding: 6px; list-style: none;
  background: var(--the); border: 1px solid var(--vien-dam); border-radius: 12px; box-shadow: 0 10px 30px #5a3a2230;
}
.ket-qua-tim li { display: flex; gap: 10px; align-items: center; padding: 7px 10px; border-radius: 8px;
  cursor: pointer; }
.ket-qua-tim li.chon { background: var(--nen-3); }
.ket-qua-tim .loai { font-size: 11px; color: var(--chu-phu); width: 52px; flex: none; }
.ket-qua-tim .phu { margin-left: auto; font-size: 12px; color: var(--chu-phu); }
.tt-phai { margin-left: auto; display: flex; align-items: center; gap: 10px; }
.vien-tt {
  font-size: 12px; color: var(--chu-2); border: 1px solid var(--vien-dam); background: var(--the);
  padding: 6px 11px; border-radius: 999px; white-space: nowrap;
}
.nut-estop {
  display: flex; align-items: center; gap: 6px; height: 30px; padding: 0 11px; border-radius: 999px;
  border: 1px solid var(--vien-estop); background: var(--nen-estop); color: var(--do); font-size: 12.5px;
  font-weight: 700;
}
.nut-estop .bieu-tuong { width: 14px; height: 14px; stroke-width: 2.2; }
.nut-estop:hover:not(:disabled), .nut-estop.bat { background: var(--do); color: #fff; border-color: var(--do); }
.nut-estop:disabled { opacity: .55; cursor: not-allowed; }
.bang-estop {
  background: var(--nen-bang-estop); color: var(--chu-bang-estop); border-bottom: 1px solid #e8bfb2;
  padding: 9px 30px; font-size: 14px; display: flex; gap: 10px; align-items: center;
}
.bang-estop button {
  margin-left: auto; border: 1px solid var(--chu-bang-estop); background: #fff; color: var(--chu-bang-estop);
  border-radius: 7px; padding: 4px 12px; font-weight: 600;
}
.loi-chung { margin: 0; padding: 8px 30px; background: var(--nen-canh-bao); color: var(--do); font-size: 13.5px; }
@media (max-width: 900px) {
  .sidebar { position: static; height: auto; }
  .menu { flex-direction: row; flex-wrap: wrap; padding: 10px 9px; }
  .thanh-tren { padding: 0 16px; flex-wrap: wrap; height: auto; min-height: 54px; }
  .tim { flex: 1 1 100%; order: 2; margin-bottom: 8px; }
  .bang-estop, .loi-chung { padding: 9px 16px; }
}
```

`frontend/src/kieu/nen.css` (mới):

```css
/* Token và nền chung (mockup style.css :root, D20/D33). Chỉ nền sáng — bỏ chế độ tối (D38). */
:root {
  --nen: #faf6f0; --nen-2: #f3ece2; --nen-3: #f7f1e8; --the: #ffffff;
  --vien: #e7dccf; --vien-dam: #d6c7b6; --chu: #3b2a21; --chu-2: #6e5d50; --chu-phu: #9a8a7c;
  --nhan: #9a3f22; --nhan-dam: #7f321a; --nhan-nhat: #f5e1d6;
  --xanh: #4f9a6a; --vang: #c98d22; --do: #b8392b; --tim: #7563b4; --xam: #9a9189;
  --nen-hover: #eadfcf; --nen-may: #ece3d6; --nen-huy-hieu: #ecdcc9;
  --nen-canh-bao: #fcf3e2; --vien-canh-bao: #efd8a8; --chu-canh-bao: #8a5a0e;
  --nen-estop: #fbefea; --vien-estop: #e0b9ab; --nen-bang-estop: #f8e1da; --chu-bang-estop: #7c2416;
  --nen-lenh: #2f2622; --chu-lenh: #f6e9dc;
  --r: 10px;
  --mono: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace;
  --sans: 'Be Vietnam Pro', -apple-system, 'Segoe UI', Roboto, sans-serif;
  color-scheme: light;
}
* { box-sizing: border-box; }
[hidden] { display: none !important; }
html, body { margin: 0; min-height: 100%; }
body {
  font-family: var(--sans); color: var(--chu); background: var(--nen); font-size: 15px;
  -webkit-font-smoothing: antialiased;
}
#app { display: grid; grid-template-columns: 272px 1fr; min-height: 100vh; }
.mono { font-family: var(--mono); }
button { font-family: inherit; cursor: pointer; }
a { color: var(--nhan); }
.cham { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 7px; vertical-align: 1px; }
.cham.xanh { background: var(--xanh); box-shadow: 0 0 0 3px #4f9a6a22; }
.cham.do { background: var(--do); box-shadow: 0 0 0 3px #b8392b22; }
.cham.xam { background: var(--xam); }
button:focus-visible, a:focus-visible, select:focus-visible, textarea:focus-visible, input:focus-visible,
[tabindex]:focus-visible { outline: 2px solid var(--nhan); outline-offset: 2px; }
.an-chu { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }
@media (prefers-reduced-motion: reduce) { * { transition: none !important; animation: none !important; } }
@media (max-width: 900px) { #app { grid-template-columns: 1fr; } }
```

`frontend/src/luat.js` (sửa):

```diff
diff --git a/frontend/src/luat.js b/frontend/src/luat.js
index e83d585..c270b75 100644
--- a/frontend/src/luat.js
+++ b/frontend/src/luat.js
@@ -34,10 +34,18 @@ export function choPhepKeo(the, hangDich) {
   return Boolean(the && the.keo_duoc) && (hangDich === 'ai-lam' || hangDich === 'can-chot') && the.hang !== hangDich
 }
 
-export function tieuDeTab(so) {
-  return so > 0 ? `(${so}) Bàn điều hành` : 'Bàn điều hành'
+// Tiêu đề tab "<tên trang> · Ben Station" (mockup app.js, D20); số việc chờ Phê duyệt đứng trước khi > 0.
+export function tieuDeTab(so, ten = 'Tổng quan') {
+  return `${so > 0 ? `(${so}) ` : ''}${ten} · Ben Station`
 }
 
+// Dự án `bat_ghi: false` (1a-2 G26, D37): chỉ đọc + quét thử — trạm từ chối mọi thao tác ghi (422). Thiếu trường
+// (API cũ) coi như đã bật ghi.
+export function duAnChiQuetThu(dsDuAn) {
+  return new Set((dsDuAn || []).filter((d) => d && d.bat_ghi === false).map((d) => d.ten))
+}
+export const CHU_CHI_QUET_THU = 'Dự án chỉ quét thử (bat_ghi: false) — trạm từ chối thao tác ghi.'
+
 // Chỉ link PR trên GitHub (N1): server đã lọc https://, trình duyệt chặn thêm host lạ.
 export function laLinkAnToan(url) {
   return typeof url === 'string' && /^https:\/\/github\.com\/[^\s"'<>]+$/.test(url)
```

`frontend/src/main.js` (sửa):

```diff
diff --git a/frontend/src/main.js b/frontend/src/main.js
index a44cbfb..fd06e45 100644
--- a/frontend/src/main.js
+++ b/frontend/src/main.js
@@ -1,7 +1,14 @@
 import { createApp } from 'vue'
 import { createRouter, createWebHashHistory } from 'vue-router'
 import KhungChinh from './KhungChinh.vue'
-import './kieu.css'
+import './kieu/font-be-vietnam.css'
+import './kieu/font-mono.css'
+import './kieu/nen.css'
+import './kieu/khung.css'
+import './kieu/chung.css'
 import { tuyen } from './tuyen.js'
 
-createApp(KhungChinh).use(createRouter({ history: createWebHashHistory(), routes: tuyen })).mount('#app')
+// Đổi trang thì cuộn lên đầu như mockup (app.js `window.scrollTo(0, 0)`); chỉ đổi query thì giữ chỗ.
+const cuon = (den, tu, daLuu) => daLuu || (den.path === tu.path ? false : { top: 0 })
+createApp(KhungChinh).use(createRouter({ history: createWebHashHistory(), routes: tuyen, scrollBehavior: cuon }))
+  .mount('#app')
```

`frontend/src/menu.js` (mới):

```js
// Menu sidebar 9 mục theo mockup (app.js MENU, D20). Phân luồng đã bỏ (D18). Ký ức giữ đường /nho, /ky-uc là bí danh
// (D38) — menu trỏ /ky-uc như mockup. Đường dẫn ở đây phải khớp tuyen.js.
export const MENU = [
  { ma: 'tong-quan', ten: 'Tổng quan', duong: '/tong-quan' },
  { ma: 'du-an', ten: 'Dự án', duong: '/du-an' },
  { ma: 'van-phong', ten: 'Văn phòng', duong: '/van-phong' },
  { ma: 'cong-viec', ten: 'Công việc', duong: '/cong-viec' },
  { ma: 'doi-ngu', ten: 'Đội ngũ AI', duong: '/doi-ngu' },
  { ma: 'ky-uc', ten: 'Ký ức', duong: '/ky-uc' },
  { ma: 'usage', ten: 'Usage & chi phí', duong: '/usage' },
  { ma: 'phe-duyet', ten: 'Phê duyệt', duong: '/phe-duyet', dem: true },
  { ma: 'cai-dat', ten: 'Cài đặt', duong: '/cai-dat' },
]
const BI_DANH = { '/nho': '/ky-uc', '/': '/tong-quan' }

// Mục menu của một đường dẫn (bỏ query); đường lạ → null.
export function mucCua(duong) {
  const p = String(duong || '/').split('?')[0].replace(/\/+$/, '') || '/'
  const goc = BI_DANH[p] ?? p
  return MENU.find((m) => goc === m.duong || goc.startsWith(`${m.duong}/`)) ?? null
}

export function tenTrang(duong) {
  return mucCua(duong)?.ten ?? 'Ben Station'
}
```

`frontend/src/thanh/BangEstop.vue` (mới):

```vue
<script setup>
// Băng đỏ dưới thanh trên khi estop bật (mockup index.html `.bang-estop`). Nút "Tiếp tục" gọi lại hàm của ThanhTren.
defineProps({ khoa: { type: Boolean, default: false } })
const emit = defineEmits(['tiep-tuc'])
</script>

<template>
  <div class="bang-estop" role="status">
    <b>Estop đang bật</b> — trạm không giao việc mới, khe đang chạy dừng mềm sau lượt hiện tại.
    <button type="button" :disabled="khoa" @click="emit('tiep-tuc')">Tiếp tục</button>
  </div>
</template>
```

`frontend/src/thanh/BieuTuong.vue` (mới):

```vue
<script setup>
import { duongVe } from '../bieu_tuong.js'

defineProps({ ten: { type: String, required: true } })
</script>

<template>
  <svg class="bieu-tuong" viewBox="0 0 24 24" aria-hidden="true" focusable="false">
    <path v-for="(d, i) in duongVe(ten)" :key="i" :d="d" />
  </svg>
</template>
```

`frontend/src/thanh/DauTrang.vue` (mới):

```vue
<script setup>
// Đầu trang chung của mockup (`.dau-trang`): tiêu đề, một câu mô tả, công cụ bên phải (slot `cong-cu`).
defineProps({ tieuDe: { type: String, required: true }, moTa: { type: String, default: '' } })
</script>

<template>
  <div class="dau-trang">
    <div>
      <h1>{{ tieuDe }}<slot name="sau-tieu-de" /></h1>
      <p v-if="moTa">{{ moTa }}</p>
    </div>
    <div v-if="$slots['cong-cu']" class="cong-cu"><slot name="cong-cu" /></div>
  </div>
</template>
```

`frontend/src/thanh/OTim.vue` (mới):

```vue
<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { doc } from '../api.js'
import { kho } from '../kho.js'
import { laPhimTim, timKiem } from '../tim.js'
import BieuTuong from './BieuTuong.vue'

// Ô tìm ⌘K (mockup index.html `.tim`; D38/Q5: tìm phía trình duyệt). Tải bead + khe một lần khi focus, giữ 30 giây.
const GIU_MS = 30000
const router = useRouter()
const o = ref(null)
const q = ref('')
const mo = ref(false)
const chon = ref(0)
const dl = ref({ the: [], khe: [] })
let taiLuc = 0
const duAn = computed(() => (kho.trangThai ? kho.trangThai.du_an.map((d) => d.ten) : []))
const ketQua = computed(() => timKiem(q.value, { duAn: duAn.value, ...dl.value }))

async function tai() {
  if (Date.now() - taiLuc < GIU_MS) return
  taiLuc = Date.now()
  const [cv, dn] = await Promise.all([doc('/api/cong-viec').catch(() => ({ the: [] })),
    doc('/api/doi-ngu').catch(() => ({ khe: [] }))])
  dl.value = { the: cv.the || [], khe: dn.khe || [] }
}
function di(kq) {
  if (!kq) return
  router.push(kq.den)
  q.value = ''
  mo.value = false
}
function phim(e) {
  const n = ketQua.value.length
  if (e.key === 'ArrowDown' && n) { e.preventDefault(); chon.value = (chon.value + 1) % n }
  else if (e.key === 'ArrowUp' && n) { e.preventDefault(); chon.value = (chon.value + n - 1) % n }
  else if (e.key === 'Enter') di(ketQua.value[chon.value])
  else if (e.key === 'Escape') { mo.value = false; o.value?.blur() }
}
const toanCuc = (e) => { if (laPhimTim(e)) { e.preventDefault(); o.value?.focus() } }
onMounted(() => window.addEventListener('keydown', toanCuc))
onUnmounted(() => window.removeEventListener('keydown', toanCuc))
</script>

<template>
  <label class="tim">
    <BieuTuong ten="tim" />
    <span class="an-chu">Tìm nhiệm vụ, dự án, agent phụ trách</span>
    <input ref="o" v-model="q" type="search" placeholder="Tìm nhiệm vụ, dự án, agent phụ trách… (⌘K)"
           role="combobox" aria-controls="ket-qua-tim" :aria-expanded="mo && ketQua.length > 0"
           @focus="mo = true; tai()" @input="mo = true; chon = 0" @keydown="phim" @blur="mo = false">
    <ul v-if="mo && ketQua.length" id="ket-qua-tim" class="ket-qua-tim" role="listbox">
      <li v-for="(k, i) in ketQua" :key="k.loai + k.nhan" role="option" :aria-selected="i === chon"
          :class="{ chon: i === chon }" @mousedown.prevent="di(k)">
        <span class="loai">{{ k.loai === 'bead' ? 'bead' : k.loai === 'khe' ? 'khe' : 'dự án' }}</span>
        <span>{{ k.nhan }}</span><span class="phu mono">{{ k.phu }}</span>
      </li>
    </ul>
  </label>
</template>
```

`frontend/src/thanh/ThanhBen.vue` (mới):

```vue
<script setup>
import { computed } from 'vue'
import { kho } from '../kho.js'
import { MENU } from '../menu.js'
import BieuTuong from './BieuTuong.vue'

// Sidebar 272 px (mockup index.html `.sidebar`, anh-tong-quan.png): logo, menu 9 mục, máy trạm, thẻ người dùng.
// Không có danh tính Đại ca (gọi thẳng 127.0.0.1) → thẻ "Chỉ đọc" (D38/Q15).
const may = window.location.hostname
const cucBo = ['127.0.0.1', 'localhost', '::1'].includes(may)
const laDaiCa = computed(() => Boolean(kho.trangThai && kho.trangThai.la_dai_ca))
</script>

<template>
  <aside class="sidebar">
    <div class="ws">
      <div class="ws-logo" aria-hidden="true">B</div>
      <div class="ws-ten"><strong>Ben Station</strong><span class="mono">Trạm điều phối</span></div>
      <span class="ws-huy-hieu">Bàn điều hành</span>
    </div>
    <nav class="menu" aria-label="Điều hướng chính">
      <router-link v-for="m in MENU" :key="m.ma" :to="m.duong" active-class="chon">
        <BieuTuong :ten="m.ma" />{{ m.ten }}
        <span v-if="m.dem && kho.soPheDuyet" class="dem" :aria-label="kho.soPheDuyet + ' việc chờ'">
          {{ kho.soPheDuyet }}</span>
      </router-link>
    </nav>
    <div class="sb-day">
      <div class="may-tram mono">
        <span class="cham xanh" />{{ cucBo ? 'Máy trạm cục bộ' : 'Máy trạm' }}<b>{{ may }}</b>
      </div>
      <div class="nguoi-dung">
        <div class="avatar" :class="{ 'chi-doc': !laDaiCa }" aria-hidden="true">{{ laDaiCa ? 'ĐC' : '?' }}</div>
        <div v-if="laDaiCa"><strong>Đại ca</strong><span class="mono">Chủ trạm</span></div>
        <div v-else><strong>Chỉ đọc</strong><span>không có danh tính Đại ca</span></div>
      </div>
    </div>
  </aside>
</template>
```

`frontend/src/thanh/ThanhTren.vue` (mới):

```vue
<script setup>
import { computed } from 'vue'
import { gioPhut } from '../dinh_dang.js'
import { kho } from '../kho.js'
import BieuTuong from './BieuTuong.vue'
import OTim from './OTim.vue'

// Thanh trên (mockup index.html `.thanh-tren`): ô tìm ⌘K, viên đồng bộ (quét cuối mới nhất của mọi dự án; mất luồng
// SSE thì báo "Mất kết nối"), nút Estop. Chỉ Đại ca bấm được (khoá như ThanhTrangThai cũ).
const props = defineProps({ estop: { type: Object, required: true } })
const tt = computed(() => kho.trangThai)
const quetCuoi = computed(() => {
  const ds = (tt.value ? tt.value.du_an : []).map((d) => d.quet_cuoi).filter(Boolean).sort()
  return ds.length ? gioPhut(ds[ds.length - 1]) : 'chưa quét'
})
const khoa = computed(() => !tt.value || !tt.value.la_dai_ca || props.estop.dangGui.value)
</script>

<template>
  <header class="thanh-tren">
    <OTim />
    <div class="tt-phai">
      <span class="vien-tt mono" role="status">
        <span class="cham" :class="kho.matKetNoi ? 'do' : 'xanh'" />
        {{ kho.matKetNoi ? 'Mất kết nối · đang thử lại' : `Đồng bộ · quét cuối ${quetCuoi}` }}</span>
      <button type="button" class="nut-estop" :class="{ bat: tt && tt.estop }" :disabled="khoa"
              :title="tt && !tt.la_dai_ca ? 'Chỉ đọc: thiếu danh tính Đại ca' : 'Dừng khẩn: trạm ngừng giao việc mới'"
              @click="estop.bam(!(tt && tt.estop))">
        <BieuTuong ten="estop" /><span>{{ tt && tt.estop ? 'Estop đang bật' : 'Estop' }}</span>
      </button>
    </div>
  </header>
</template>
```

`frontend/src/tim.js` (mới):

```js
// Ô tìm ⌘K phía trình duyệt (D38/Q5): tìm trên dữ liệu đã tải — dự án, bead, khe. Không API mới. Hàm thuần.
const TOI_DA = 8
const thuong = (s) => String(s ?? '').normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/đ/g, 'd')
  .replace(/Đ/g, 'D').toLowerCase()

// Kết quả: [{loai: 'du-an'|'bead'|'khe', nhan, phu, den}] — `den` là đích router (object path/query).
export function timKiem(q, { duAn = [], the = [], khe = [] } = {}) {
  const k = thuong(q).trim()
  if (!k) return []
  const khop = (...s) => s.some((x) => thuong(x).includes(k))
  const ra = []
  for (const d of duAn) {
    if (khop(d)) ra.push({ loai: 'du-an', nhan: d, phu: 'dự án', den: { path: '/cong-viec', query: { du_an: d } } })
  }
  for (const t of the) {
    if (khop(t.id, t.tieu_de)) {
      ra.push({ loai: 'bead', nhan: `${t.id} · ${t.tieu_de}`, phu: t.du_an,
        den: { path: '/cong-viec', query: { du_an: t.du_an, bead: t.id } } })
    }
  }
  for (const x of khe) {
    if (khop(x.khe_id, x.ten, x.ten_goi_nho)) {
      ra.push({ loai: 'khe', nhan: x.ten || x.khe_id, phu: x.khe_id, den: { path: '/doi-ngu' } })
    }
  }
  return ra.slice(0, TOI_DA)
}

export function laPhimTim(e) {
  return Boolean(e.metaKey || e.ctrlKey) && String(e.key).toLowerCase() === 'k'
}
```

`frontend/src/trang/CaiDat.vue` (mới):

```vue
<script setup>
import DauTrang from '../thanh/DauTrang.vue'
</script>

<template>
  <DauTrang tieu-de="Cài đặt" />
  <div class="cho-chot"><strong>Cài đặt</strong>Trang đang dựng trong lát 2f.</div>
</template>
```

`frontend/src/trang/TongQuan.vue` (mới):

```vue
<script setup>
import DauTrang from '../thanh/DauTrang.vue'
</script>

<template>
  <DauTrang tieu-de="Tổng quan" />
  <div class="cho-chot"><strong>Tổng quan</strong>Trang đang dựng trong lát 2f.</div>
</template>
```

`frontend/src/tuyen.js` (sửa):

```diff
diff --git a/frontend/src/tuyen.js b/frontend/src/tuyen.js
index 9e91ec3..191eb40 100644
--- a/frontend/src/tuyen.js
+++ b/frontend/src/tuyen.js
@@ -1,17 +1,23 @@
+import CaiDat from './trang/CaiDat.vue'
 import CongViec from './trang/CongViec.vue'
 import DoiNgu from './trang/DoiNgu.vue'
 import DuAn from './trang/DuAn.vue'
 import KyUc from './trang/KyUc.vue'
 import PheDuyet from './trang/PheDuyet.vue'
+import TongQuan from './trang/TongQuan.vue'
 import Usage from './trang/Usage.vue'
 
+// Trang mở đầu là Tổng quan (D17). Ký ức giữ /nho (link cũ từ máy A, Telegram) và thêm bí danh /ky-uc (D38).
 export const tuyen = [
-  { path: '/', redirect: '/cong-viec' },
-  { path: '/cong-viec', component: CongViec },
+  { path: '/', redirect: '/tong-quan' },
+  { path: '/tong-quan', component: TongQuan },
   { path: '/du-an', component: DuAn },
-  { path: '/phe-duyet', component: PheDuyet },
-  { path: '/nho', component: KyUc },
+  { path: '/van-phong', component: () => import('./trang/VanPhong.vue') },   // lát 2c: nạp lười (three.js)
+  { path: '/cong-viec', component: CongViec },
   { path: '/doi-ngu', component: DoiNgu },
+  { path: '/nho', alias: '/ky-uc', component: KyUc },
   { path: '/usage', component: Usage },
-  { path: '/van-phong', component: () => import('./trang/VanPhong.vue') },   // lát 2c: nạp lười (three.js)
+  { path: '/phe-duyet', component: PheDuyet },
+  { path: '/cai-dat', component: CaiDat },
+  { path: '/:khac(.*)*', redirect: '/tong-quan' },
 ]
```

`frontend/vite.config.js` (sửa):

```diff
diff --git a/frontend/vite.config.js b/frontend/vite.config.js
index 587208c..f4018ea 100644
--- a/frontend/vite.config.js
+++ b/frontend/vite.config.js
@@ -13,5 +13,7 @@ export default defineConfig({
   },
   // changeOrigin: tram-api chỉ nhận Host 127.0.0.1:<cổng> / localhost:<cổng> / tên máy B (421 nếu khác).
   server: { proxy: { '/api': { target: 'http://127.0.0.1:7700', changeOrigin: true } } },
-  build: { outDir: 'dist', emptyOutDir: true },
+  // Lát 2f: không nhúng tài nguyên nhỏ thành `data:` (mặc định < 4 kB) — font JetBrains Mono tiếng Việt ~3,9 kB sẽ
+  // thành `data:font/woff2` và bị CSP `font-src 'self'` chặn (phát hiện khi kiểm trình duyệt).
+  build: { outDir: 'dist', emptyOutDir: true, assetsInlineLimit: 0 },
 })
```

Xoá file thay thế:

```bash
git rm -q frontend/src/kieu.css frontend/src/thanh/ThanhTrangThai.vue
```

- [ ] **Step 4: Chạy thấy PASS**

```bash
cd frontend && node --test tests/dinh_dang.test.mjs tests/khung.test.mjs tests/luat.test.mjs
npm run kiem && npm run build && npm run kiem-dist && cd ..
```

Kỳ vọng: PASS — lệnh test của task: pass 15 · fail 0; toàn bộ tăng đúng 7 node test so với main trước task (bảng "Sơ đồ đợt chạy"); `npm run build`, `npm run kiem-dist` xanh. Số đo trên bản chạy thử.

- [ ] **Step 5: Commit**

```bash
git add frontend/tests/dinh_dang.test.mjs frontend/tests/khung.test.mjs frontend/tests/luat.test.mjs frontend/index.html frontend/src/KhungChinh.vue frontend/src/bieu_tuong.js frontend/src/dinh_dang.js frontend/src/estop.js frontend/src/kho.js frontend/src/kieu/chung.css frontend/src/kieu/font-be-vietnam.css frontend/src/kieu/font-mono.css frontend/src/kieu/khung.css frontend/src/kieu/nen.css frontend/src/luat.js frontend/src/main.js frontend/src/menu.js frontend/src/thanh/BangEstop.vue frontend/src/thanh/BieuTuong.vue frontend/src/thanh/DauTrang.vue frontend/src/thanh/OTim.vue frontend/src/thanh/ThanhBen.vue frontend/src/thanh/ThanhTren.vue frontend/src/tim.js frontend/src/trang/CaiDat.vue frontend/src/trang/TongQuan.vue frontend/src/tuyen.js frontend/vite.config.js && git rm -q --cached --ignore-unmatch frontend/src/kieu.css frontend/src/thanh/ThanhTrangThai.vue
git commit -m "feat(dashboard): 2f nền giao diện — token, font, khung, menu, tìm ⌘K, tuyến"
```

### Task 2: Thành phần khe dùng chung — chibi, màu khe, thanh hạn mức

**Đợt:** 2 · **Độ khó:** dễ · **Phải xong trước:** Task 1 · **Test mới:** 3 node

**Mockup bám:** `chung.js` (`chibi`), `du-lieu.js` (`KHE[].mau/.toc` → bảng 8 màu), `trang.js` (`thanhHm`: "còn x% · reset hh:mm", lớp `thap` < 30%, `het` 0%), CSS `.chibi .han-muc .thanh-hm` trong `style.css`; ảnh `anh-doi-ngu.png`, `anh-tong-quan.png` (hàng chibi), `anh-usage.png` (khối hạn mức).

**Files:**
- Create: `frontend/src/mau_khe.js`, `frontend/src/luat_han_muc.js`, `frontend/src/kieu/khe.css`, `frontend/src/thanh/Chibi.vue`, `frontend/src/thanh/ThanhHanMuc.vue`
- Test: `frontend/tests/khe_chung.test.mjs` (mới)

**Interfaces:**
- Consumes: `gioReset` (Task 1).
- Produces: `mauKhe(khe_id) -> {than, toc}` (FNV-1a của `khe_id` mod 8 — thêm khe không đổi màu khe cũ), `cuaSo(khe, '5h' | 'tuan')`, `oHanMuc(cs, bayGio?) -> {con, lop, rong, chu}` (`phan_tram` của server là phần ĐÃ dùng → `con = 100 − phan_tram`), `hanMucThapNhat(dsKhe) -> {khe, con, reset} | null`, `tenKhe(khe | khe_id)` ("Codex 1"); `<Chibi :khe-id :mo>`, `<ThanhHanMuc :ten :cua-so>` (3 phần tử con cho lưới `.han-muc`). Dùng ở Task 10, 12, 13, 17.

- [ ] **Step 1: Viết test (chép nguyên văn)**

`frontend/tests/khe_chung.test.mjs` (mới):

```js
import assert from 'node:assert/strict'
import { test } from 'node:test'
import { cuaSo, hanMucThapNhat, oHanMuc, tenKhe } from '../src/luat_han_muc.js'
import { BANG_MAU, fnv1a, mauKhe } from '../src/mau_khe.js'

const cs = (loai, dung, reset = '2026-10-15T16:40:00Z') =>
  ({ loai, trang_thai: 'biet', phan_tram: dung, reset_luc: reset })
const BAY = '2026-10-15T15:17:00Z'

test('màu khe ổn định theo băm, nằm trong bảng mockup', () => {
  assert.equal(fnv1a('a'), 0xe40c292c)
  assert.deepEqual(mauKhe('B/claude-1'), mauKhe('B/claude-1'))
  assert.ok(BANG_MAU.some(([than, toc]) => than === mauKhe('B/codex-9').than && toc === mauKhe('B/codex-9').toc))
})

test('ô hạn mức: còn = 100 − đã dùng, lớp thấp/hết, chưa biết', () => {
  assert.deepEqual(oHanMuc(cs('5h', 38), BAY), { con: 62, lop: '', rong: 62, chu: 'còn 62% · reset 23:40' })
  assert.equal(oHanMuc(cs('5h', 75), BAY).lop, 'thap')
  assert.deepEqual(oHanMuc(cs('5h', 100), BAY), { con: 0, lop: 'het', rong: 2, chu: 'còn 0% · reset 23:40' })
  assert.equal(oHanMuc({ loai: '5h', trang_thai: 'chua_biet', phan_tram: null }, BAY).chu, 'chưa biết')
  assert.equal(oHanMuc(null).con, null)
})

test('hạn mức thấp nhất và tên khe', () => {
  const ds = [{ khe_id: 'B/claude-1', ten: 'Claude 1', han_muc: { cua_so: [cs('5h', 38), cs('tuan', 19)] } },
    { khe_id: 'B/claude-4', han_muc: { cua_so: [cs('5h', 100, '2026-10-15T17:12:00Z')] } },
    { khe_id: 'B/codex-2', han_muc: { cua_so: [] } }]
  assert.equal(cuaSo(ds[0], 'tuan').phan_tram, 19)
  const t = hanMucThapNhat(ds, BAY)
  assert.deepEqual([t.khe.khe_id, t.con, t.reset], ['B/claude-4', 0, '00:12'])
  assert.equal(hanMucThapNhat([ds[2]], BAY), null)
  assert.equal(tenKhe(ds[0]), 'Claude 1')
  assert.equal(tenKhe(ds[1]), 'Claude 4')
  assert.equal(tenKhe('B/codex-de-danh'), 'Codex de danh')
})
```

- [ ] **Step 2: Chạy thấy FAIL**

```bash
cd frontend && node --test tests/khe_chung.test.mjs
```

Kỳ vọng: FAIL — `Error [ERR_MODULE_NOT_FOUND]: Cannot find module '…/frontend/src/luat_han_muc.js' imported from …/frontend/tests/khe_chung.test.mjs`

- [ ] **Step 3: Viết mã (chép nguyên văn; file sửa: chép khối diff ra file tạm, `git apply --check` rồi `git apply`)**

`frontend/src/kieu/khe.css` (mới):

```css
/* Chibi và thanh hạn mức dùng chung Đội ngũ AI, Tổng quan, Usage (mockup style.css "Đội ngũ AI"). */
.chibi { width: 46px; height: 46px; flex: none; background: var(--nen-2); border-radius: 12px;
  border: 1px solid var(--vien); }
.han-muc { display: grid; grid-template-columns: 52px 1fr auto; gap: 6px 10px; align-items: center; font-size: 12.5px;
  color: var(--chu-2); }
.thanh-hm { height: 7px; background: #efe7dc; border-radius: 99px; overflow: hidden; }
.thanh-hm i { display: block; height: 100%; background: var(--xanh); border-radius: 99px; }
.thanh-hm i.thap { background: var(--vang); }
.thanh-hm i.het { background: var(--do); }
```

`frontend/src/luat_han_muc.js` (mới):

```js
// Hạn mức khe theo mockup Đội ngũ AI (trang.js thanhHm): thanh "còn x% · reset hh:mm", lớp thấp (< 30%) / hết (0%).
// `phan_tram` của server là phần ĐÃ DÙNG (spec 3 §8.1) — ở đây đổi sang phần CÒN LẠI như mockup. Hàm thuần.
import { gioReset } from './dinh_dang.js'

export function cuaSo(khe, loai) {
  return ((khe && khe.han_muc && khe.han_muc.cua_so) || []).find((c) => c.loai === loai) ?? null
}

export function oHanMuc(cs, bayGio = new Date()) {
  if (!cs || cs.trang_thai !== 'biet' || typeof cs.phan_tram !== 'number') {
    return { con: null, lop: '', rong: 0, chu: 'chưa biết' }
  }
  const con = Math.max(0, Math.min(100, Math.round(100 - cs.phan_tram)))
  const lop = con === 0 ? 'het' : con < 30 ? 'thap' : ''
  return { con, lop, rong: Math.max(con, 2), chu: `còn ${con}% · reset ${gioReset(cs.reset_luc, bayGio)}` }
}

// Khe có cửa sổ 5 giờ còn ít nhất (mockup Tổng quan "Hạn mức thấp nhất"); không khe nào biết → null.
export function hanMucThapNhat(dsKhe, bayGio = new Date()) {
  let tot = null
  for (const k of dsKhe || []) {
    const o = oHanMuc(cuaSo(k, '5h'), bayGio)
    if (o.con !== null && (!tot || o.con < tot.con)) tot = { khe: k, con: o.con, reset: o.chu.split(' · reset ')[1] }
  }
  return tot
}

// Tên hiển thị của khe: `ten` từ server (lát 2f T1, "Claude 1"); thiếu thì dựng từ khe_id "B/codex-1" → "Codex 1".
export function tenKhe(khe) {
  if (khe && khe.ten) return khe.ten
  const rieng = String((khe && khe.khe_id) || khe || '').split('/').pop()
  return rieng.split('-').map((x, i) => (i === 0 ? x.charAt(0).toUpperCase() + x.slice(1) : x)).join(' ')
}
```

`frontend/src/mau_khe.js` (mới):

```js
// Màu thân / tóc của nhân vật mỗi khe — dùng chung cảnh 3D, Đội ngũ AI, Tổng quan, Usage (mockup du-lieu.js KHE).
// Chọn theo băm FNV-1a của khe_id nên thêm khe mới không làm đổi màu khe cũ. Server không giữ màu (khảo sát §1.1).
export const BANG_MAU = [
  ['#c8623a', '#3a2620'], ['#d39a3c', '#2b2b33'], ['#4f7a99', '#1f2a33'], ['#5f8f5a', '#33261d'],
  ['#6a5bb5', '#1d1b2e'], ['#b8507a', '#2a1f24'], ['#3f8a8a', '#1f2a2a'], ['#a8744a', '#2e2420'],
]

export function fnv1a(s) {
  let h = 0x811c9dc5
  for (const c of String(s)) {
    h ^= c.codePointAt(0)
    h = Math.imul(h, 0x01000193) >>> 0
  }
  return h
}

export function mauKhe(kheId) {
  const [than, toc] = BANG_MAU[fnv1a(kheId) % BANG_MAU.length]
  return { than, toc }
}
```

`frontend/src/thanh/Chibi.vue` (mới):

```vue
<script setup>
import { computed } from 'vue'
import '../kieu/khe.css'
import { mauKhe } from '../mau_khe.js'

// Avatar chibi SVG (mockup chung.js `chibi`), màu theo khe_id (mau_khe.js). Khe tắt / mất kết nối vẽ mờ.
const props = defineProps({ kheId: { type: String, required: true }, mo: { type: Boolean, default: false } })
const mau = computed(() => mauKhe(props.kheId))
</script>

<template>
  <svg class="chibi" viewBox="0 0 46 46" aria-hidden="true" focusable="false">
    <g :opacity="mo ? 0.4 : 1">
      <ellipse cx="23" cy="41" rx="10" ry="2.6" fill="#3a241822" />
      <rect x="17.5" y="32" width="4" height="8" rx="2" fill="#2b2523" />
      <rect x="24.5" y="32" width="4" height="8" rx="2" fill="#2b2523" />
      <path d="M15 34 L16.5 22 Q23 19 29.5 22 L31 34 Z" :fill="mau.than" />
      <circle cx="23" cy="15" r="8" fill="#f2c9a3" />
      <path d="M14.8 14.5 A8.3 8.3 0 0 1 31.2 14.5 Q27 9.5 23 10.5 Q18 9.8 14.8 14.5 Z" :fill="mau.toc" />
    </g>
  </svg>
</template>
```

`frontend/src/thanh/ThanhHanMuc.vue` (mới):

```vue
<script setup>
import { computed } from 'vue'
import '../kieu/khe.css'
import { oHanMuc } from '../luat_han_muc.js'

// Một dòng của lưới `.han-muc` (mockup trang.js thanhHm): tên cửa sổ | thanh | "còn x% · reset hh:mm".
const props = defineProps({ ten: { type: String, required: true }, cuaSo: { type: Object, default: null } })
const o = computed(() => oHanMuc(props.cuaSo))
</script>

<template>
  <span>{{ ten }}</span>
  <div class="thanh-hm" role="img" :aria-label="`${ten}: ${o.chu}`"><i v-if="o.con !== null" :class="o.lop"
    :style="{ width: `${o.rong}%` }" /></div>
  <span :class="{ nho: o.con === null }">{{ o.chu }}</span>
</template>
```

- [ ] **Step 4: Chạy thấy PASS**

```bash
cd frontend && node --test tests/khe_chung.test.mjs
npm run kiem && npm run build && npm run kiem-dist && cd ..
```

Kỳ vọng: PASS — lệnh test của task: pass 3 · fail 0; toàn bộ tăng đúng 3 node test so với main trước task (bảng "Sơ đồ đợt chạy"); `npm run build`, `npm run kiem-dist` xanh. Số đo trên bản chạy thử.

- [ ] **Step 5: Commit**

```bash
git add frontend/tests/khe_chung.test.mjs frontend/src/kieu/khe.css frontend/src/luat_han_muc.js frontend/src/mau_khe.js frontend/src/thanh/Chibi.vue frontend/src/thanh/ThanhHanMuc.vue
git commit -m "feat(dashboard): 2f thành phần khe dùng chung — chibi, màu khe, thanh hạn mức"
```

### Task 3: Cổng an toàn mở rộng — style tĩnh, URL ngoài, font/CDN ngoài, style trong khối tĩnh

**Đợt:** 1 · **Độ khó:** dễ · **Phải xong trước:** — · **Test mới:** 5 node (kiem_an_toan 3, kiem_dist +2)

**Mockup bám:** không (cổng CI). Khảo sát §2.3 mục 1, 3: mockup dùng Google Fonts, importmap + three từ jsdelivr và 37 thuộc tính `style="…"` — những thứ đó không được lọt vào `src/` hay `dist/`.

**Files:**
- Modify: `frontend/kiem-an-toan.mjs` (viết lại thành hàm `quetNguon(ten, van)` + chạy khi là script chính — giữ đủ luật cũ), `frontend/kiem-dist.mjs` (thêm `quetNgoai`, `quetKhoiTinh`, quét cả file CSS)
- Test: `frontend/tests/kiem_an_toan.test.mjs` (mới), `frontend/tests/kiem_dist.test.mjs` (sửa)

**Interfaces:**
- Produces: `quetNguon(ten, van) -> string[]` (luật cũ + `'style="…" tĩnh'` cho `.vue` + `'URL ngoài'` cho `.js/.mjs/.vue/.css`, trừ `https://github.com/`); `quetNgoai(van)` (fonts.googleapis.com, fonts.gstatic.com, cdn.jsdelivr.net, unpkg.com, `url(http…)`, font nhúng `url(data:font…)` — CSP `font-src 'self'` không cho `data:`); `quetKhoiTinh(van)` (`<tag … style=` trong chuỗi khối tĩnh Vue — đã thử: `sa(\`<li style="color:red;">…\`)` trong `index-*.js`; bundle hiện tại không có mẫu này, three/Tres không báo nhầm).

Ghi chú: luật mới chạy trên mọi task sau (`npm run kiem`, `npm run kiem-dist`). Task 18 vẫn phải kiểm CSP thật trên trình duyệt — quét tĩnh không thay được.

- [ ] **Step 1: Viết test (chép nguyên văn)**

`frontend/tests/kiem_an_toan.test.mjs` (mới):

```js
import assert from 'node:assert/strict'
import { test } from 'node:test'
import { quetNguon } from '../kiem-an-toan.mjs'

test('kiem-an-toan: giữ luật cũ (chèn HTML thô)', () => {
  assert.deepEqual(quetNguon('a.vue', '<div v-html="x" />'), ['v-html'])
  assert.deepEqual(quetNguon('a.js', 'el.innerHTML = s'), ['innerHTML'])
  assert.deepEqual(quetNguon('a.js', 'const a = 1'), [])
})

test('kiem-an-toan: cấm style="…" tĩnh trong .vue, cho :style động (lát 2f)', () => {
  assert.deepEqual(quetNguon('a.vue', '<template><i class="a" style="width:3px" /></template>'), ['style="…" tĩnh'])
  assert.deepEqual(quetNguon('a.vue', '<template><i :style="{ width: w + \'%\' }" /></template>'), [])
  assert.deepEqual(quetNguon('a.js', "el.setAttribute('x', 'style=\"a\"')"), [])
})

test('kiem-an-toan: cấm URL ngoài trong mã nguồn, trừ GitHub', () => {
  assert.deepEqual(quetNguon('a.css', '@import url(https://fonts.googleapis.com/css2)'), ['URL ngoài'])
  assert.deepEqual(quetNguon('a.js', "import x from 'http://cdn.example/x.js'"), ['URL ngoài'])
  assert.deepEqual(quetNguon('a.js', "const m = 'https://github.com/o/r/pull/1'"), [])
  assert.deepEqual(quetNguon('OFL.txt', 'http://scripts.sil.org/OFL'), [])
})
```

`frontend/tests/kiem_dist.test.mjs` (sửa):

```diff
diff --git a/frontend/tests/kiem_dist.test.mjs b/frontend/tests/kiem_dist.test.mjs
index 4f6bc81..8996e8c 100644
--- a/frontend/tests/kiem_dist.test.mjs
+++ b/frontend/tests/kiem_dist.test.mjs
@@ -1,6 +1,6 @@
 import assert from 'node:assert/strict'
 import { test } from 'node:test'
-import { kiemGoiChinh, quetHtml, quetJs } from '../kiem-dist.mjs'
+import { kiemGoiChinh, quetHtml, quetJs, quetKhoiTinh, quetNgoai } from '../kiem-dist.mjs'
 
 test('quetJs bắt eval, new Function, biên dịch WebAssembly', () => {
   assert.deepEqual(quetJs('const a = 1; retrieval(x); obj.evaluate()'), [])
@@ -21,3 +21,20 @@ test('kiemGoiChinh: three không nằm trong gói chính', () => {
   assert.deepEqual(kiemGoiChinh('import("./VanPhong-x.js")'), [])
   assert.deepEqual(kiemGoiChinh('class WebGLRenderer {}'), ['three nằm trong gói chính — trang Văn phòng phải nạp lười'])
 })
+
+test('quetNgoai bắt font / CDN ngoài (CSP font-src, script-src chỉ self — lát 2f)', () => {
+  assert.deepEqual(quetNgoai('url(./be-vietnam-pro-latin-400-normal-x.woff2)'), [])
+  assert.deepEqual(quetNgoai('@import url(https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro)'),
+    ['fonts.googleapis.com', 'url(http…) trong CSS'])
+  assert.deepEqual(quetNgoai('import "https://cdn.jsdelivr.net/npm/three@0.160.0"; src: url(http://x.io/a.woff2)'),
+    ['cdn.jsdelivr.net', 'url(http…) trong CSS'])
+  assert.deepEqual(quetNgoai('src:url(data:font/woff2;base64,d09GMg) format("woff2")'),
+    ['font nhúng data: (CSP font-src)'])
+})
+
+test('quetKhoiTinh bắt style= trong chuỗi khối tĩnh Vue gộp (CSP style-src chặn)', () => {
+  assert.deepEqual(quetKhoiTinh('sa(`<li style="color:red;">x</li><li class="a">`,26)'),
+    ['style= trong khối tĩnh'])
+  assert.deepEqual(quetKhoiTinh('sa("<div class=\\"a\\" style=\\"b\\">",3)'), ['style= trong khối tĩnh'])
+  assert.deepEqual(quetKhoiTinh('t.style=fe(n);el.style.transform=`translate(${x}px)`;e===`style`'), [])
+})
```

- [ ] **Step 2: Chạy thấy FAIL**

```bash
cd frontend && node --test tests/kiem_an_toan.test.mjs tests/kiem_dist.test.mjs
```

Kỳ vọng: FAIL — `SyntaxError: The requested module '../kiem-an-toan.mjs' does not provide an export named 'quetNguon'`

- [ ] **Step 3: Viết mã (chép nguyên văn; file sửa: chép khối diff ra file tạm, `git apply --check` rồi `git apply`)**

`frontend/kiem-an-toan.mjs` (sửa):

```diff
diff --git a/frontend/kiem-an-toan.mjs b/frontend/kiem-an-toan.mjs
index b58b522..9252405 100644
--- a/frontend/kiem-an-toan.mjs
+++ b/frontend/kiem-an-toan.mjs
@@ -1,15 +1,36 @@
 // Chặn chèn HTML thô vào trang (spec §4 mục 4): nội dung bead chỉ hiển thị bằng text. Quét mọi file trong src/.
+// Lát 2f thêm: cấm `style="…"` tĩnh trong .vue (Vue gộp khối tĩnh thành chuỗi HTML → CSP `style-src 'self'` chặn;
+// `:style` động đặt qua CSSOM thì được) và cấm URL ngoài trong mã nguồn (CSP chỉ 'self'; link PR chỉ GitHub).
 import { readFileSync, readdirSync, statSync } from 'node:fs'
-import { join } from 'node:path'
-import { fileURLToPath } from 'node:url'
-
-const CAM = [/v-html/, /v-bind:innerHTML/, /:innerHTML/, /innerHTML/, /outerHTML/, /insertAdjacentHTML/, /document\.write/]
-const goc = fileURLToPath(new URL('./src', import.meta.url))
-const duyet = (d) => readdirSync(d).flatMap((t) => (statSync(join(d, t)).isDirectory() ? duyet(join(d, t)) : [join(d, t)]))
-const tep = duyet(goc)
-const viPham = tep.filter((p) => CAM.some((re) => re.test(readFileSync(p, 'utf8'))))
-if (viPham.length) {
-  console.error('Cấm v-html / innerHTML / document.write trong:', viPham)
-  process.exit(1)
+import { extname, join } from 'node:path'
+import { fileURLToPath, pathToFileURL } from 'node:url'
+
+const CAM = [[/v-html/, 'v-html'], [/v-bind:innerHTML/, 'v-bind:innerHTML'], [/:innerHTML/, ':innerHTML'],
+  [/innerHTML/, 'innerHTML'], [/outerHTML/, 'outerHTML'], [/insertAdjacentHTML/, 'insertAdjacentHTML'],
+  [/document\.write/, 'document.write']]
+const MA = new Set(['.js', '.mjs', '.vue', '.css'])
+const STYLE_TINH = /<[a-zA-Z][^<>]*\sstyle=["']/
+const URL_NGOAI = /\bhttps?:\/\/(?!github\.com\/)[a-z0-9]/i
+
+export function quetNguon(ten, van) {
+  const loi = []
+  for (const [re, nhan] of CAM) if (re.test(van) && !loi.some((l) => nhan.includes(l))) loi.push(nhan)
+  if (extname(ten) === '.vue' && STYLE_TINH.test(van)) loi.push('style="…" tĩnh')
+  if (MA.has(extname(ten)) && URL_NGOAI.test(van)) loi.push('URL ngoài')
+  return loi
 }
-console.log(`kiem-an-toan: ${tep.length} file, không có chèn HTML thô`)
+
+function chay() {
+  const goc = fileURLToPath(new URL('./src', import.meta.url))
+  const duyet = (d) => readdirSync(d)
+    .flatMap((t) => (statSync(join(d, t)).isDirectory() ? duyet(join(d, t)) : [join(d, t)]))
+  const tep = duyet(goc)
+  const viPham = tep.map((p) => [p, quetNguon(p, readFileSync(p, 'utf8'))]).filter(([, l]) => l.length)
+  if (viPham.length) {
+    console.error('Cấm chèn HTML thô / style tĩnh / URL ngoài trong:', viPham.map(([p, l]) => `${p}: ${l.join(', ')}`))
+    process.exit(1)
+  }
+  console.log(`kiem-an-toan: ${tep.length} file, không có chèn HTML thô, style tĩnh hay URL ngoài`)
+}
+
+if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) chay()
```

`frontend/kiem-dist.mjs` (sửa):

```diff
diff --git a/frontend/kiem-dist.mjs b/frontend/kiem-dist.mjs
index 4978968..4f534de 100644
--- a/frontend/kiem-dist.mjs
+++ b/frontend/kiem-dist.mjs
@@ -22,6 +22,20 @@ export function quetHtml(van) {
   return loi
 }
 
+// Lát 2f: font tự host (D35) — không được còn font / CDN ngoài; CSS không `url(http…)`.
+const HOST_NGOAI = ['fonts.googleapis.com', 'fonts.gstatic.com', 'cdn.jsdelivr.net', 'unpkg.com']
+export function quetNgoai(van) {
+  const loi = HOST_NGOAI.filter((h) => van.includes(h))
+  if (/url\(\s*["']?https?:/i.test(van)) loi.push('url(http…) trong CSS')
+  if (/url\(\s*["']?data:font/i.test(van)) loi.push('font nhúng data: (CSP font-src)')
+  return loi
+}
+
+// Lát 2f: Vue gộp khối tĩnh thành chuỗi HTML chèn bằng innerHTML — `style=` trong chuỗi đó bị CSP chặn.
+export function quetKhoiTinh(van) {
+  return /<[a-zA-Z][^<>]*?\sstyle=\\?["']/.test(van) ? ['style= trong khối tĩnh'] : []
+}
+
 export function kiemGoiChinh(van) {
   return /\bWebGLRenderer\b/.test(van) ? ['three nằm trong gói chính — trang Văn phòng phải nạp lười'] : []
 }
@@ -29,16 +43,24 @@ export function kiemGoiChinh(van) {
 function chay() {
   const dist = fileURLToPath(new URL('./dist', import.meta.url))
   const html = readFileSync(join(dist, 'index.html'), 'utf8')
-  const loi = quetHtml(html).map((l) => `index.html: ${l}`)
+  const loi = [...quetHtml(html), ...quetNgoai(html)].map((l) => `index.html: ${l}`)
   const chinh = [...html.matchAll(/<script[^>]*\bsrc="\/?([^"]+)"/g)].map((m) => m[1])
   for (const f of chinh) loi.push(...kiemGoiChinh(readFileSync(join(dist, f), 'utf8')).map((l) => `${f}: ${l}`))
   const tep = readdirSync(join(dist, 'assets')).filter((t) => t.endsWith('.js'))
-  for (const t of tep) loi.push(...quetJs(readFileSync(join(dist, 'assets', t), 'utf8')).map((l) => `assets/${t}: ${l}`))
+  for (const t of tep) {
+    const van = readFileSync(join(dist, 'assets', t), 'utf8')
+    loi.push(...[...quetJs(van), ...quetNgoai(van), ...quetKhoiTinh(van)].map((l) => `assets/${t}: ${l}`))
+  }
+  const css = readdirSync(join(dist, 'assets')).filter((t) => t.endsWith('.css'))
+  for (const t of css) {
+    loi.push(...quetNgoai(readFileSync(join(dist, 'assets', t), 'utf8')).map((l) => `assets/${t}: ${l}`))
+  }
   if (loi.length) {
     console.error('kiem-dist: vi phạm CSP chặt:\n' + loi.join('\n'))
     process.exit(1)
   }
-  console.log(`kiem-dist: ${tep.length} file JS, không thấy mẫu eval/inline trong quét tĩnh; cần kiểm CSP runtime ở Task 8`)
+  console.log(`kiem-dist: ${tep.length} file JS, ${css.length} file CSS, không thấy eval/inline/style tĩnh/font ngoài; `
+    + 'cần kiểm CSP runtime trên trình duyệt (task K)')
 }
 
 if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) chay()
```

- [ ] **Step 4: Chạy thấy PASS**

```bash
cd frontend && node --test tests/kiem_an_toan.test.mjs tests/kiem_dist.test.mjs
npm run kiem && npm run build && npm run kiem-dist && cd ..
```

Kỳ vọng: PASS — lệnh test của task: pass 8 · fail 0; toàn bộ tăng đúng 5 node test so với main trước task (bảng "Sơ đồ đợt chạy"); `npm run build`, `npm run kiem-dist` xanh. Số đo trên bản chạy thử.

- [ ] **Step 5: Commit**

```bash
git add frontend/tests/kiem_an_toan.test.mjs frontend/tests/kiem_dist.test.mjs frontend/kiem-an-toan.mjs frontend/kiem-dist.mjs
git commit -m "feat(dashboard): 2f cổng an toàn — style tĩnh, URL ngoài, font/CDN ngoài"
```

### Task 4: Đọc hệ thống chỉ đọc — dịch vụ launchd, Keychain có/chưa (bộ đệm, tiêm được)

**Đợt:** 1 · **Độ khó:** vừa · **Phải xong trước:** — · **Test mới:** 7 py

**Mockup bám:** `trang-cai-dat.js` (bảng "Dịch vụ launchd", khối "Keychain"), `trang-tong-quan.js` (`khoiSucKhoe`), `du-lieu.js` (`DICH_VU`, `KEYCHAIN`); ảnh `anh-cai-dat.png`, `anh-tong-quan.png`. Khảo sát §1.6, §1.10 (luật chung mục 4–6), G25.

**Files:**
- Create: `tram/suy/he_thong.py` (`DICH_VU`, `KEYCHAIN`, `MA_KEYCHAIN`, `chay_that`, lớp `DocHeThong(chay=, home=, uid=, dong_ho=)` với `dich_vu()` (bộ đệm 30 giây) và `keychain()` (60 giây), `doc_he_thong()` — một thể hiện dùng chung, test thay `_CHUNG` bằng monkeypatch)
- Test: `tests/test_he_thong.py` (mới)

**Interfaces:**
- Produces: `doc_he_thong().dich_vu() -> [{nhan, viec, da_cai, dang_chay: bool | None, kiem_duoc}]` (5 nhãn cố định `vn.tram.api|quet|nho|bao-tin|sao-luu`); `doc_he_thong().keychain() -> [{ten, trang_thai: "co" | "chua" | "khong_ro"}]` (4 mục: `tram-telegram-bot-token`, `tram-anthropic-api-key`, `tram-nho-token`, `tram-noi-bo-token`). Task 6, 8 dùng.

Bảo mật: argv chỉ dựng từ hằng số (`launchctl print gui/<uid>/<nhãn>`, `security find-generic-password -s <tên>` — **không bao giờ `-w`**); timeout 3 giây; exception, stdout, stderr, pid không bao giờ ra khỏi module; không sửa `tram/chu/cai_dat.py` (lát 3c đang sửa — `_co_keychain` của nó chỉ được đọc tham khảo).

- [ ] **Step 1: Viết test (chép nguyên văn)**

`tests/test_he_thong.py` (mới):

```python
"""2f P1: đọc dịch vụ launchd + Keychain cho trang Cài đặt — chỉ đọc, không lộ stdout, có bộ đệm (khảo sát §1.10)."""
import json
import subprocess

from tram.suy import he_thong
from tram.suy.he_thong import DocHeThong

BI_MAT = "BI-MAT-STDOUT keychain: \"acct\"<blob>=\"dai-ca@example.com\" PATH=/Users/x/.local/bin"
CHAY = f"gui/501/vn.tram.api = {{\n\tactive count = 1\n\tpath = /x\n\tstate = running\n\tpid = 4242\n\t{BI_MAT}\n}}"
DUNG = "gui/501/vn.tram.quet = {\n\tstate = not running\n\tlast exit code = 1\n}"


class ChayGia:
    def __init__(self, tra: dict[str, object] | None = None, mac_dinh=(113, "Could not find service")):
        self.tra, self.mac_dinh, self.argv = tra or {}, mac_dinh, []

    def __call__(self, argv: list[str]):
        self.argv.append(list(argv))
        kq = self.tra.get(argv[-1], self.mac_dinh)
        if isinstance(kq, BaseException):
            raise kq
        return kq


class DongHo:
    def __init__(self):
        self.t = 1000.0

    def __call__(self):
        return self.t


def _doc(tmp_path, chay, dong_ho=None, cai=("vn.tram.api", "vn.tram.quet")):
    la = tmp_path / "Library" / "LaunchAgents"
    la.mkdir(parents=True, exist_ok=True)
    for n in cai:
        (la / f"{n}.plist").write_text("<plist/>")
    return DocHeThong(chay=chay, home=tmp_path, uid=501, dong_ho=dong_ho or DongHo())


def test_dich_vu_doc_state_va_chua_nap(tmp_path):
    chay = ChayGia({"gui/501/vn.tram.api": (0, CHAY), "gui/501/vn.tram.quet": (0, DUNG)})
    ds = _doc(tmp_path, chay).dich_vu()
    assert [d["nhan"] for d in ds] == ["vn.tram.api", "vn.tram.quet", "vn.tram.nho", "vn.tram.bao-tin",
                                       "vn.tram.sao-luu"]
    assert ds[0] == {"nhan": "vn.tram.api", "viec": "dashboard + API", "da_cai": True, "dang_chay": True,
                     "kiem_duoc": True}
    assert ds[1]["da_cai"] is True and ds[1]["dang_chay"] is False and ds[1]["kiem_duoc"] is True
    assert ds[2] == {"nhan": "vn.tram.nho", "viec": "memory 127.0.0.1:7710", "da_cai": False,
                     "dang_chay": False, "kiem_duoc": True}          # mã ≠ 0: chưa nạp
    assert [d["viec"] for d in ds[3:]] == ["Telegram", "sao lưu su-kien.db"]


def test_chua_cai_va_timeout_khong_kiem_duoc(tmp_path):
    chay = ChayGia(mac_dinh=subprocess.TimeoutExpired(["launchctl"], 3))
    ds = _doc(tmp_path, chay, cai=()).dich_vu()
    assert all(d["da_cai"] is False and d["dang_chay"] is None and d["kiem_duoc"] is False for d in ds)
    ds = _doc(tmp_path, ChayGia(mac_dinh=OSError("không có launchctl"))).dich_vu()
    assert ds[0]["da_cai"] is True and ds[0]["dang_chay"] is None and ds[0]["kiem_duoc"] is False


def test_keychain_ma_0_44_khac_va_loi(tmp_path):
    chay = ChayGia({"tram-telegram-bot-token": (0, BI_MAT), "tram-anthropic-api-key": (44, ""),
                    "tram-nho-token": (36, "keychain locked"), "tram-noi-bo-token": OSError("x")})
    assert _doc(tmp_path, chay).keychain() == [
        {"ten": "tram-telegram-bot-token", "trang_thai": "co"}, {"ten": "tram-anthropic-api-key", "trang_thai": "chua"},
        {"ten": "tram-nho-token", "trang_thai": "khong_ro"}, {"ten": "tram-noi-bo-token", "trang_thai": "khong_ro"}]


def test_argv_tu_hang_so_khong_co_w(tmp_path):
    chay = ChayGia()
    d = _doc(tmp_path, chay)
    d.dich_vu(), d.keychain()
    assert chay.argv[0] == ["launchctl", "print", "gui/501/vn.tram.api"]
    sec = [a for a in chay.argv if a[0] == "security"]
    assert len(sec) == 4 and all(a[:3] == ["security", "find-generic-password", "-s"] and len(a) == 4 for a in sec)
    assert not any("-w" in a or "-g" in a for a in chay.argv)


def test_bo_dem_30_giay_dich_vu_60_giay_keychain(tmp_path):
    chay, dh = ChayGia(), DongHo()
    d = _doc(tmp_path, chay, dh)
    d.dich_vu(), d.keychain()
    n = len(chay.argv)
    dh.t += 29
    d.dich_vu(), d.keychain()
    assert len(chay.argv) == n                          # trong hạn: không gọi lại
    dh.t += 2
    d.dich_vu(), d.keychain()
    assert len(chay.argv) == n + 5                      # dịch vụ hết hạn 30 giây, Keychain chưa
    dh.t += 30
    d.keychain()
    assert len(chay.argv) == n + 9
    d.dich_vu()[0]["dang_chay"] = "sua"                 # sửa bản trả về không làm bẩn bộ đệm
    assert d.dich_vu()[0]["dang_chay"] is False


def test_khong_lo_stdout_pid_argv(tmp_path):
    chay = ChayGia({"gui/501/vn.tram.api": (0, CHAY), "tram-nho-token": (0, BI_MAT)}, mac_dinh=(0, BI_MAT))
    d = _doc(tmp_path, chay)
    s = json.dumps([d.dich_vu(), d.keychain()], ensure_ascii=False)
    for x in ("BI-MAT", "4242", "dai-ca@example.com", "PATH", "launchctl", "find-generic-password", "gui/501"):
        assert x not in s


def test_doc_he_thong_dung_chung_va_thay_duoc(monkeypatch):
    monkeypatch.setattr(he_thong, "_CHUNG", None)
    a = he_thong.doc_he_thong()
    assert isinstance(a, DocHeThong) and he_thong.doc_he_thong() is a
    gia = DocHeThong(chay=ChayGia(), uid=1)
    monkeypatch.setattr(he_thong, "_CHUNG", gia)
    assert he_thong.doc_he_thong() is gia
```

- [ ] **Step 2: Chạy thấy FAIL**

```bash
uv run --offline pytest -q tests/test_he_thong.py
```

Kỳ vọng: FAIL — `ImportError: cannot import name 'he_thong' from 'tram.suy' (…/tram/suy/__init__.py)`

- [ ] **Step 3: Viết mã (chép nguyên văn; file sửa: chép khối diff ra file tạm, `git apply --check` rồi `git apply`)**

`tram/suy/he_thong.py` (mới):

```python
"""Đọc dịch vụ launchd + Keychain cho trang Cài đặt (D19; khảo sát §1.6, §1.10 mục 4–6). CHỈ ĐỌC.

argv chỉ dựng từ hằng số (+ uid của tiến trình), timeout 3 giây, gọi tuần tự. KHÔNG BAO GIỜ trả stdout, stderr,
argv, nội dung exception hay pid — chỉ trả boolean / mã trạng thái cố định. `security` không bao giờ kèm `-w`
(như `tram/chu/cai_dat.py::_co_keychain`). Bộ đệm trong tiến trình (mẫu `BoDemCcusage`): dịch vụ 30 giây,
Keychain 60 giây."""
import os
import subprocess
import threading
import time
from collections.abc import Callable
from pathlib import Path

from tram.chu.launchd import NHAN_API, NHAN_BAO_TIN, NHAN_NHO, NHAN_QUET, NHAN_SAO_LUU

DICH_VU = ((NHAN_API, "dashboard + API"), (NHAN_QUET, "quét + chấm cột"), (NHAN_NHO, "memory 127.0.0.1:7710"),
           (NHAN_BAO_TIN, "Telegram"), (NHAN_SAO_LUU, "sao lưu su-kien.db"))
# Tên mục Keychain: bao_tin/telegram.py, llm/claude.py, nho/khach.py, api/noi_bo.py — chỉ kiểm có/chưa.
KEYCHAIN = ("tram-telegram-bot-token", "tram-anthropic-api-key", "tram-nho-token", "tram-noi-bo-token")
MA_KEYCHAIN = {0: "co", 44: "chua"}          # 44 = errSecItemNotFound; mã khác (Keychain khoá…) → khong_ro
GIAY_CHO, GIAY_DICH_VU, GIAY_KEYCHAIN = 3, 30, 60

Chay = Callable[[list[str]], tuple[int, str]]


def chay_that(argv: list[str]) -> tuple[int, str]:
    """Chạy argv (không shell), trả (mã thoát, stdout). Lỗi/timeout ném ra — `DocHeThong` nuốt, không trả tiếp."""
    kq = subprocess.run(argv, capture_output=True, text=True, timeout=GIAY_CHO, stdin=subprocess.DEVNULL)
    return kq.returncode, kq.stdout


def _dang_chay(stdout: str) -> bool:
    """Dòng `state = …` đầu tiên của `launchctl print` (khối ngoài cùng đứng trước khối con)."""
    for dong in stdout.splitlines():
        s = dong.strip()
        if s.startswith("state ="):
            return s == "state = running"
    return False


class DocHeThong:
    def __init__(self, *, chay: Chay = chay_that, home: Path | None = None, uid: int | None = None,
                 dong_ho: Callable[[], float] = time.monotonic):
        self._chay, self._dong_ho = chay, dong_ho
        self._home = home if home is not None else Path.home()
        self._uid = uid if uid is not None else os.getuid()
        self._nho: dict[str, tuple[float, list[dict]]] = {}
        self._khoa = threading.Lock()

    def _dem(self, khoa: str, giay: int, doc: Callable[[], list[dict]]) -> list[dict]:
        with self._khoa:                                   # một lượt đọc tại một thời điểm; request khác chờ
            bay = self._dong_ho()
            cu = self._nho.get(khoa)
            if cu is None or bay - cu[0] >= giay:
                cu = self._nho[khoa] = (bay, doc())
            return [dict(x) for x in cu[1]]

    def _mot_dich_vu(self, nhan: str, viec: str) -> dict:
        da_cai = (self._home / "Library" / "LaunchAgents" / f"{nhan}.plist").is_file()
        try:
            ma, ra = self._chay(["launchctl", "print", f"gui/{self._uid}/{nhan}"])
        except Exception:                                  # không đưa exception ra ngoài (khảo sát §1.10 mục 4)
            return {"nhan": nhan, "viec": viec, "da_cai": da_cai, "dang_chay": None, "kiem_duoc": False}
        return {"nhan": nhan, "viec": viec, "da_cai": da_cai, "dang_chay": ma == 0 and _dang_chay(ra),
                "kiem_duoc": True}                         # mã ≠ 0: chưa nạp → không chạy

    def _mot_keychain(self, ten: str) -> dict:
        try:
            ma, _ = self._chay(["security", "find-generic-password", "-s", ten])   # KHÔNG -w: không đọc giá trị
        except Exception:
            return {"ten": ten, "trang_thai": "khong_ro"}
        return {"ten": ten, "trang_thai": MA_KEYCHAIN.get(ma, "khong_ro")}

    def dich_vu(self) -> list[dict]:
        return self._dem("dich_vu", GIAY_DICH_VU, lambda: [self._mot_dich_vu(n, v) for n, v in DICH_VU])

    def keychain(self) -> list[dict]:
        return self._dem("keychain", GIAY_KEYCHAIN, lambda: [self._mot_keychain(t) for t in KEYCHAIN])


_CHUNG: DocHeThong | None = None
_KHOA_CHUNG = threading.Lock()


def doc_he_thong() -> DocHeThong:
    """Một thể hiện dùng chung cho cả tiến trình (bộ đệm chung). Test thay `_CHUNG` bằng monkeypatch."""
    global _CHUNG
    with _KHOA_CHUNG:
        if _CHUNG is None:
            _CHUNG = DocHeThong()
        return _CHUNG
```

- [ ] **Step 4: Chạy thấy PASS**

```bash
uv run --offline pytest -q tests/test_he_thong.py
uv run --offline pytest -q
```

Kỳ vọng: PASS — lệnh test của task: 7 passed in 0.03s; toàn bộ tăng đúng 7 py test so với main trước task (bảng "Sơ đồ đợt chạy"). Số đo trên bản chạy thử.

- [ ] **Step 5: Commit**

```bash
git add tests/test_he_thong.py tram/suy/he_thong.py
git commit -m "feat(api): 2f đọc launchd + Keychain chỉ đọc"
```

### Task 5: Mô tả sự kiện từ mẫu cố định + sự kiện gần đây + `mo_ta` cho `/api/nho/su-kien` (D39)

**Đợt:** 1 · **Độ khó:** vừa · **Phải xong trước:** — (1b-4 cho mẫu `nho.bo_bi_mat`) · **Test mới:** 5 py

**Mockup bám:** `du-lieu.js` `SU_KIEN` (câu "claude-1 · lượt 2", "→ cột 1", "→ claude-1 · code", "PR #12 — không phải merge commit", "claude-4 · hết hạn mức"), `trang-tong-quan.js` `khoiSuKien`, `trang-ky-uc.js` `khoiSuKien` (D39 thay khối JSON bằng câu). Danh sách loại sự kiện và trường lấy từ mã thật (khảo sát Phần 1 ghi chú: mockup có `giao.cap`, `tho.mat_nhip` không tồn tại — dùng `giao.nhan`, `khe.mat_ket_noi`).

**Files:**
- Create: `tram/suy/mo_ta_su_kien.py` (hàm kiểm dạng `ma so sha pham_vi chon adr khe_tho`, `mo_ta(s)`), `tram/suy/mau_su_kien.py` (mẫu ~55 loại của phần 0–4), `tram/suy/mau_nho.py` (mẫu `nho.*`, `may.*`, `ngan_sach.*`, `phieu.loi`, `dieu_phoi.nhip`; `nho.bo_bi_mat` theo câu của plan 1b-4 G22), `tram/suy/su_kien_gan_day.py` (`gan_day(kho, gioi_han, *, la_dai_ca)`, `CHE_NHO`, `BO`)
- Modify: `tram/api/tuyen_nho.py` (thêm `mo_ta` cho mỗi sự kiện, thêm `nho.bo_bi_mat` vào `LOAI_SU_KIEN`)
- Test: `tests/test_mo_ta_su_kien.py` (mới)

**Interfaces:**
- Produces: `mo_ta(s: SuKien) -> str` (loại lạ / dữ liệu lỗi → `""`; trường không đúng dạng → `"?"`); `gan_day(kho: KhoSuKien, gioi_han: int, *, la_dai_ca: bool) -> list[dict]` (khoá `id luc loai du_an bead_id tac_nhan mo_ta`, mới nhất trước, đọc tối đa 500 sự kiện cuối rồi lọc `BO`). Task 8 dùng cả hai.

Ghi chú bảo mật: mẫu KHÔNG BAO GIỜ đọc `vi_sao`, `gop_y`, `loi`, `tra_loi`, `noi_dung`, `ly_do` tự do, `tieu_de`, nội dung ký ức — test `test_khong_bao_gio_lo_chu_tu_do` đặt một chuỗi giống khoá API vào các trường đó và kiểm không lọt ra. Mã lý do (`ly_do` dạng mã: cầu dao, PR, bí, escalation…) đổi qua bảng câu hằng; mã lạ → "?" (G20).

- [ ] **Step 1: Viết test (chép nguyên văn)**

`tests/test_mo_ta_su_kien.py` (mới):

```python
"""Lát 2f (D39, khảo sát A3): mô tả sự kiện dựng từ mẫu cố định theo loại — không bao giờ lộ chữ tự do."""
from api_gia import DAI_CA, tao_app_gia
from asgi_gia import goi
from bd_gia import BdGia
from tram.su_kien.kho import SuKien
from tram.suy.mo_ta_su_kien import mo_ta
from tram.suy.su_kien_gan_day import CHE_NHO, gan_day

BI_MAT = "sk-ant-api03-BIMAT"


def sk(loai, du_lieu, tac_nhan="tram/api", id=1):
    return SuKien("2026-10-15T15:14:00Z", "hr", "hr-1", loai, tac_nhan, du_lieu, id)


def test_mau_theo_loai_nhu_mockup():
    assert mo_ta(sk("giao.nhan", {"khe_id": "B/claude-1", "buoc": "code", "luot": 1})) == "→ B/claude-1 · code"
    assert mo_ta(sk("chay.bat_dau", {"khe_id": "B/claude-1", "luot": 2, "lan": 1})) == "B/claude-1 · lượt 2"
    assert mo_ta(sk("cham_cot.ket_qua", {"cot": "ai-lam", "ly_do": BI_MAT})) == "→ cột 1"
    assert mo_ta(sk("khe.cau_dao_ngat", {"khe_id": "B/claude-4", "ly_do": "het-han-muc"})) == \
        "B/claude-4 · cầu dao ngắt (hết hạn mức)"
    assert mo_ta(sk("pr.khong_xac_minh", {"pr": 12, "ly_do": "khong-phai-merge-commit"})) == \
        "PR #12 — không phải merge commit (squash / rebase)"
    assert mo_ta(sk("qc.ket_qua", {"ket_luan": "dat"})) == "QC đạt"
    assert mo_ta(sk("bao.can_hoi", {"loai_hoi": "can_quyet_dinh", "noi_dung": BI_MAT}, "tho/B/codex-1")) == \
        "B/codex-1 hỏi Đại ca (cần quyết định)"


def test_khong_bao_gio_lo_chu_tu_do():
    tu_do = [("khe.tat", {"khe_id": "B/claude-3", "vi_sao": BI_MAT}), ("cot.tra_ve", {"gop_y": BI_MAT}),
             ("quet.loi", {"loi": BI_MAT}), ("escalation.dong", {"escalation_id": "hr-9", "tra_loi": BI_MAT}),
             ("nho.tu_choi", {"ly_do": BI_MAT, "nguon": "dai_ca_ghi"}), ("bao.xong", {"luot": 1, "noi_dung": BI_MAT}),
             ("nho.agent_ghi", {"noi_dung": BI_MAT}), ("giao.ket_thuc", {"buoc": "code", "loi": [BI_MAT], "luot": 1}),
             ("cot.dai_ca_sua", {"cot_moi": "cot:can-chot", "vi_sao": BI_MAT, "tieu_de": BI_MAT})]
    for loai, d in tu_do:
        assert BI_MAT not in mo_ta(sk(loai, d)) and mo_ta(sk(loai, d)), loai
    assert mo_ta(sk("giao.nhan", {"khe_id": "B/x; rm -rf", "buoc": "lạ"})) == "→ ? · ?"
    assert mo_ta(sk("loai.la", {"a": 1})) == ""


def test_nho_bo_bi_mat_theo_mau_1b4():
    d = {"su_kien_id": 42, "loai_nguon": "ban_giao", "nhom": {"khoa_da_biet": 2, "entropy_cao": 1}}
    assert mo_ta(sk("nho.bo_bi_mat", d)) == \
        "Bỏ nguồn bàn giao (sự kiện #42) vì có dấu hiệu bí mật: khoá đã biết ×2, chuỗi entropy cao ×1"


def test_gan_day_moi_nhat_truoc_bo_nhip_che_nho(tmp_path):
    _, pt = tao_app_gia(tmp_path, {"hr": BdGia([])})
    kho = pt.mo_kho()
    kho.ghi("hr", "giao.nhan", {"khe_id": "B/claude-1", "buoc": "code"}, bead_id="hr-1")
    kho.ghi("_tram", "dieu_phoi.nhip", {"su_kien": "Stop", "phien": "0" * 16})
    kho.ghi("hr", "nho.ghi", {"id": "m-1", "pham_vi": "/du-an/hr/cach-lam", "nguon": []}, bead_id="hr-1")
    ds = gan_day(kho, 5, la_dai_ca=False)
    assert [s["loai"] for s in ds] == ["nho.ghi", "giao.nhan"]
    assert ds[0]["mo_ta"] == CHE_NHO and ds[1]["mo_ta"] == "→ B/claude-1 · code"
    assert set(ds[1]) == {"id", "luc", "loai", "du_an", "bead_id", "tac_nhan", "mo_ta"}
    assert gan_day(kho, 1, la_dai_ca=True)[0]["mo_ta"] == "ghi ký ức m-1 vào /du-an/hr/cach-lam"


def test_api_nho_su_kien_co_mo_ta(tmp_path):
    app, pt = tao_app_gia(tmp_path, {"hr": BdGia([])})
    pt.mo_kho().ghi("hr", "nho.xoa", {"id": "m-1", "pham_vi": "/du-an/hr/cach-lam"}, bead_id="hr-1")
    r = goi(app, "GET", "/api/nho/su-kien", headers=DAI_CA)
    assert r.json()["su_kien"][0]["mo_ta"] == "xoá mềm ký ức m-1"
```

- [ ] **Step 2: Chạy thấy FAIL**

```bash
uv run --offline pytest -q tests/test_mo_ta_su_kien.py
```

Kỳ vọng: FAIL — `ModuleNotFoundError: No module named 'tram.suy.mo_ta_su_kien'`

- [ ] **Step 3: Viết mã (chép nguyên văn; file sửa: chép khối diff ra file tạm, `git apply --check` rồi `git apply`)**

`tram/api/tuyen_nho.py` (sửa):

```diff
diff --git a/tram/api/tuyen_nho.py b/tram/api/tuyen_nho.py
index 838c963..02928da 100644
--- a/tram/api/tuyen_nho.py
+++ b/tram/api/tuyen_nho.py
@@ -15,6 +15,7 @@ from tram.duong_dan import bay_gio
 from tram.nho.khach import LoiNhoKhach
 from tram.nho.pham_vi import du_an_cua
 from tram.suy.lam_sach import lam_sach
+from tram.suy.mo_ta_su_kien import mo_ta
 from tram.thao_tac.chay import YeuCau, chay_thao_tac
 from tram.thao_tac.loi import KhongHopLe, KhongThay, XungDot
 
@@ -23,7 +24,7 @@ DU_AN_HE = "_tram"
 KHOA_NHO = "nho"            # khoá riêng của thao tác ký ức trong bảng thao_tac —
                             # không chờ chung khoá estop (`_tram`, None)
 LOAI_SU_KIEN = ("nho.ghi", "nho.gop", "nho.xoa", "nho.xoa_cung", "nho.thang_cap", "nho.tu_choi", "nho.loi_tach",
-                "nho.loi_llm", "nho.loi_embedder", "nho.phuc_hoi")
+                "nho.loi_llm", "nho.loi_embedder", "nho.phuc_hoi", "nho.bo_bi_mat")   # 2f: + bỏ vì bí mật (1b-4)
 SO_SU_KIEN = 50
 
 
@@ -76,7 +77,8 @@ def su_kien(request: Request) -> dict:
         ds = [s for d in [*pt.cac_du_an(), DU_AN_HE] for l in LOAI_SU_KIEN for s in kho.gan_day(d, l, SO_SU_KIEN)]
     ds = sorted(ds, key=lambda s: -s.id)[:SO_SU_KIEN]
     return {"su_kien": [{"id": s.id, "luc": s.luc, "du_an": s.du_an, "bead_id": s.bead_id, "loai": s.loai,
-                         "tom_tat": lam_sach(json.dumps(s.du_lieu, ensure_ascii=False), 300)} for s in ds]}
+                         "tom_tat": lam_sach(json.dumps(s.du_lieu, ensure_ascii=False), 300),
+                         "mo_ta": mo_ta(s)} for s in ds]}                  # 2f (D39): câu từ mẫu cố định
 
 
 def _chay(pt, than, loai: str, noi_dung: dict, buoc) -> dict:
```

`tram/suy/mau_nho.py` (mới):

```python
"""Mẫu câu của sự kiện ký ức (`nho.*`, D39) và vài loại hệ thống. Không bao giờ đưa nội dung ký ức, `ly_do` tự do,
`loi` ra ngoài — chỉ mã ký ức, phạm vi đã kiểm dạng, số sự kiện. `nho.bo_bi_mat` theo mẫu plan 1b-4 G22."""
from tram.suy.mo_ta_su_kien import chon, ma, pham_vi, so

NGUON_BI_MAT = {"ban_giao": "bàn giao", "da_chot": "trả lời escalation", "tra_ve": "trả về spec"}
NHOM_BI_MAT = {"khoa_da_biet": "khoá đã biết", "khoa_rieng": "khối khoá riêng", "gan_gia_tri": "gán giá trị nhạy cảm",
               "entropy_cao": "chuỗi entropy cao"}
NGUON_TU_CHOI = {"dai_ca_ghi": "Đại ca ghi tay", "thang_cap": "thăng cấp"}
LOI_NAP = {"llm": "Claude API", "embedder": "embedder"}


def _bo_bi_mat(d, s) -> str:
    nhom = d.get("nhom") if isinstance(d.get("nhom"), dict) else {}
    ds = ", ".join(f"{NHOM_BI_MAT[k]} ×{so(v)}" for k, v in nhom.items() if k in NHOM_BI_MAT)
    return (f"Bỏ nguồn {chon(NGUON_BI_MAT, d.get('loai_nguon'))} (sự kiện #{so(d.get('su_kien_id'))}) vì có dấu hiệu "
            f"bí mật: {ds or '?'}")


MAU_NHO = {
    "nho.ghi": lambda d, s: f"ghi ký ức {ma(d.get('id'))} vào {pham_vi(d.get('pham_vi'))}",
    "nho.gop": lambda d, s: f"gộp {len(d.get('cu') or [])} ký ức thành {ma(d.get('moi'))}",
    "nho.thang_cap": lambda d, s: f"thăng cấp ký ức {ma(d.get('id'))} lên {pham_vi(d.get('pham_vi'))}",
    "nho.tu_choi": lambda d, s: f"từ chối ghi ký ức ({chon(NGUON_TU_CHOI, d.get('nguon'))})",
    "nho.xoa": lambda d, s: f"xoá mềm ký ức {ma(d.get('id'))}",
    "nho.xoa_cung": lambda d, s: f"xoá cứng ký ức {ma(d.get('id'))}",
    "nho.loi_llm": lambda d, s: f"lỗi Claude API khi nạp sự kiện #{so(d.get('su_kien_id'))}",
    "nho.loi_embedder": lambda d, s: f"lỗi embedder khi nạp sự kiện #{so(d.get('su_kien_id'))}",
    "nho.loi_tach": lambda d, s: f"bỏ sự kiện #{so(d.get('su_kien_id'))} không tách được",
    "nho.phuc_hoi": lambda d, s: f"nạp ký ức chạy lại ({chon(LOI_NAP, d.get('loai'))})",
    "nho.agent_ghi": lambda d, s: "agent ghi ký ức",
    "nho.bo_bi_mat": _bo_bi_mat,
    "may.cap_ma": lambda d, s: f"cấp mã ghép máy {ma(d.get('may_id'))}",
    "may.ghep_sai": lambda d, s: f"ghép máy sai {so(d.get('so_lan'))} lần",
    "may.ghep": lambda d, s: f"máy {ma(d.get('may_id'))} đã ghép",
    "ngan_sach.chu_ky_moi": lambda d, s: "ngân sách chu kỳ mới",
    "ngan_sach.dot_spec_moi": lambda d, s: "đợt spec mới",
    "phieu.loi": lambda d, s: f"phiếu lỗi ({len(d.get('loi') or [])} lỗi)",
    "dieu_phoi.nhip": lambda d, s: "nhịp phiên điều phối",
}
```

`tram/suy/mau_su_kien.py` (mới):

```python
"""Mẫu câu cố định theo loại sự kiện (D39). Mỗi mẫu nhận `(du_lieu, su_kien)` và chỉ dùng hàm kiểm dạng của
`tram/suy/mo_ta_su_kien.py`. Mã lý do → câu hằng; mã lạ → "?". Không mẫu nào đọc trường chữ tự do."""
from tram.suy.mau_nho import MAU_NHO
from tram.suy.mo_ta_su_kien import BUOC, COT, adr, chon, khe_tho, ma, sha, so

KET_CHAY = {"xong": "xong", "loi": "lỗi", "loi_he": "lỗi hệ", "het_han_muc": "hết hạn mức", "dung": "dừng",
            "mo-coi": "mồ côi"}
KET_GIAO = {"xong": "xong", "bi": "bí", "het_han_muc": "hết hạn mức", "thu_hoi": "thu hồi"}
CAU_DAO = {"het-han-muc": "hết hạn mức", "loi-lien-tiep": "lỗi liên tiếp", "het-gio": "hết giờ",
           "dai-ca": "Đại ca đóng"}
THU_HOI = {"mat-nhip": "mất nhịp tim", "go-may": "gỡ máy"}
HOI = {"can_quyet_dinh": "cần quyết định", "thao_tac_nguy_hiem": "thao tác nguy hiểm"}
BI = {"agent": "agent bí", "het-ngan-sach": "hết ngân sách", "khe-tat": "khe tắt", "estop": "estop",
      "cau-dao": "cầu dao", "can-hoi": "cần hỏi", "thieu-moi-truong-kiem": "thiếu môi trường kiểm",
      "nhanh-bi-day-ngoai-luong": "nhánh bị đẩy ngoài luồng", "loi-may-tho": "lỗi máy thợ"}
ESC = {"agent-bi": "agent bí", "can-thao-tac-nguy-hiem": "cần thao tác nguy hiểm", "agent-can-hoi": "agent cần hỏi",
       "het-ngan-sach": "hết ngân sách", "nhanh-bi-day": "nhánh bị đẩy",
       "thieu-moi-truong-kiem": "thiếu môi trường kiểm", "dong-file-cau-hinh": "đụng file cấu hình",
       "qc-doi-ma": "QC đổi mã", "spec-tra-ve-nhieu": "spec bị trả về nhiều", "phieu-thieu": "phiếu thiếu"}
QC = {"dat": "QC đạt", "tra_ve": "QC trả về", "khong_cong_nhan": "QC không công nhận"}
PR_LY_DO = {"pr-khac": "PR khác PR trạm mở", "sai-nhanh": "sai nhánh", "sai-nhanh-chinh": "sai nhánh chính",
            "thieu-merge-commit": "thiếu merge commit",
            "merge-khong-tren-nhanh-chinh": "merge không nằm trên nhánh chính",
            "khong-phai-merge-commit": "không phải merge commit (squash / rebase)",
            "head-khac-commit-ban-giao": "head khác commit bàn giao"}


def _khe(d):
    return ma(d.get("khe_id"))


def _luot(d):
    return f"lượt {so(d.get('luot'))}"


MAU = {
    "quet.bat_dau": lambda d, s: f"bắt đầu quét {so(d.get('so_bead'))} bead"
    + (" (quét thử)" if d.get("thu") else ""),
    "quet.xong": lambda d, s: f"đã chấm {so(d.get('da_cham'))} bead"
    + (f", {so(d['loi'])} lỗi" if d.get("loi") else ""),
    "quet.loi": lambda d, s: "lỗi đọc beads",
    "quet.bo_qua": lambda d, s: "bỏ lượt quét vì estop",
    "cham_cot.ket_qua": lambda d, s: f"→ {chon(COT, d.get('cot'))}" + (" (huỷ)" if d.get("huy") else ""),
    "cham_cot.loi": lambda d, s: "lỗi khi chấm",
    "cham_cot.bo_qua": lambda d, s: "bỏ chấm vì lỗi liên tiếp",
    "cham_cot.thu_lai": lambda d, s: "Đại ca bấm thử lại",
    "cham_cot.can_cham_lai": lambda d, s: "cần chấm lại sau khi decision đóng",
    "cot.dai_ca_sua": lambda d, s: f"Đại ca chuyển sang {chon(COT, d.get('cot_moi'))}",
    "cot.da_chot": lambda d, s: "Đại ca chốt câu hỏi"
    + (f" (dẫn {adr(d.get('adr'))})" if adr(d.get("adr")) else ""),
    "cot.tra_ve": lambda d, s: "Đại ca trả về kèm góp ý",
    "escalation.tao": lambda d, s: f"mở escalation {ma(d.get('escalation_id'))} ({chon(ESC, d.get('ly_do'))})",
    "escalation.dong": lambda d, s: f"đóng escalation {ma(d.get('escalation_id'))}",
    "escalation.tra_loi": lambda d, s: "Đại ca trả lời escalation",
    "estop.bat": lambda d, s: "Estop bật",
    "estop.tat": lambda d, s: "Estop tắt",
    "khe.dang_ky": lambda d, s: f"{_khe(d)} đăng ký ({chon({'claude': 'claude', 'codex': 'codex'}, d.get('cli'))})",
    "khe.bat": lambda d, s: f"{_khe(d)} · Đại ca bật",
    "khe.tat": lambda d, s: f"{_khe(d)} · Đại ca tắt",
    "khe.ket_noi": lambda d, s: f"{_khe(d)} kết nối lại",
    "khe.mat_ket_noi": lambda d, s: f"{_khe(d)} mất nhịp tim",
    "khe.han_muc": lambda d, s: f"{_khe(d)} cập nhật hạn mức",
    "khe.han_muc_khong_ro": lambda d, s: f"{_khe(d)} chưa đọc được hạn mức",
    "khe.cau_dao_ngat": lambda d, s: f"{_khe(d)} · cầu dao ngắt ({chon(CAU_DAO, d.get('ly_do'))})",
    "khe.cau_dao_dong": lambda d, s: f"{_khe(d)} · cầu dao đóng ({chon(CAU_DAO, d.get('ly_do'))})",
    "chay.bat_dau": lambda d, s: f"{_khe(d)} · {_luot(d)}"
    + (f" · lần {so(d['lan'])}" if isinstance(d.get("lan"), int) and d["lan"] > 1 else ""),
    "chay.xong": lambda d, s: f"{_khe(d)} · {_luot(d)} · {chon(KET_CHAY, d.get('ket_thuc'))}",
    "chay.don_rac": lambda d, s: f"{_khe(d)} · dọn nhánh rác",
    "giao.nhan": lambda d, s: f"→ {_khe(d)} · {chon(BUOC, d.get('buoc'))}",
    "giao.snapshot": lambda d, s: f"lưu snapshot {_luot(d)}",
    "giao.thu_hoi": lambda d, s: f"thu hồi {_luot(d)} ({chon(THU_HOI, d.get('ly_do'))})",
    "giao.cong_bo": lambda d, s: f"công bố {_luot(d)} · {sha(d.get('commit'))}",
    "giao.ket_thuc": lambda d, s: f"{chon(BUOC, d.get('buoc'))} {_luot(d)} · {chon(KET_GIAO, d.get('ket_thuc'))}",
    "bao.moc": lambda d, s: f"{khe_tho(s.tac_nhan)} báo mốc {_luot(d)}",
    "bao.can_hoi": lambda d, s: f"{khe_tho(s.tac_nhan)} hỏi Đại ca ({chon(HOI, d.get('loai_hoi'))})",
    "bao.bi": lambda d, s: f"{khe_tho(s.tac_nhan)} báo bí ({chon(BI, d.get('ly_do'))})",
    "bao.xong": lambda d, s: f"{khe_tho(s.tac_nhan)} báo xong {_luot(d)}",
    "bao.het_han_muc": lambda d, s: f"{khe_tho(s.tac_nhan)} báo hết hạn mức",
    "tho.tu_choi": lambda d, s: f"trạm từ chối báo cáo của {_khe(d)}",
    "kiem.lai": lambda d, s: f"kiểm lại {_luot(d)}: {'đạt' if d.get('dat') is True else 'không đạt'}",
    "qc.ket_qua": lambda d, s: chon(QC, d.get("ket_luan"), "QC ?"),
    "pr.mo": lambda d, s: f"mở PR #{so(d.get('pr'))}",
    "pr.khong_xac_minh": lambda d, s: f"PR #{so(d.get('pr'))} — {chon(PR_LY_DO, d.get('ly_do'))}",
    "pr.da_merge": lambda d, s: f"PR #{so(d.get('pr'))} đã merge đúng commit đã kiểm",
    "bead.vao_cot_3": lambda d, s: "chờ review" + (" · cờ đỏ" if d.get("co_do") is True else ""),
    "bead.dong": lambda d, s: "đã đóng",
    "spec.duyet": lambda d, s: f"Đại ca duyệt spec · {len(d.get('bead_moi') or [])} bead mới",
    "spec.tra_ve": lambda d, s: "Đại ca trả về spec",
    "spec.xong": lambda d, s: f"spec xong · {sha(d.get('commit'))}",
    "spec.cho_merge": lambda d, s: "spec đã duyệt, chờ merge",
    "feature.xong": lambda d, s: "feature xong, chờ Đại ca đóng",
    **MAU_NHO,
}
```

`tram/suy/mo_ta_su_kien.py` (mới):

```python
"""Câu mô tả dễ đọc của một sự kiện (D39; khảo sát giao diện A3) — dùng cho "Sự kiện gần đây" (Tổng quan) và khối
sự kiện ký ức. Dựng từ MẪU CỐ ĐỊNH theo loại (`tram/suy/mau_su_kien.py`); chỉ ghép trường đã kiểm dạng: mã khe, mã
bead, số lượt, bước, cột, kết luận, mã lý do → câu hằng. KHÔNG BAO GIỜ đưa chữ tự do ra ngoài (`vi_sao`, `gop_y`,
`loi`, `tra_loi`, `noi_dung`, `ly_do` tự do, `tieu_de`, nội dung ký ức). Loại lạ hoặc mẫu lỗi → ""."""
import re

from tram.su_kien.kho import SuKien

MA = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}(/[A-Za-z0-9][A-Za-z0-9._-]{0,63})?")
PHAM_VI = re.compile(r"/[a-z0-9/-]{1,120}")
SHA = re.compile(r"[0-9a-f]{7,40}")
ADR = re.compile(r"ADR-\d{4}")
COT = {"ai-lam": "cột 1", "can-chot": "cột 2", "cho-review": "cột 3",
       "cot:ai-lam": "cột 1", "cot:can-chot": "cột 2", "cot:cho-review": "cột 3"}
BUOC = {"code": "code", "qc": "QC", "spec": "spec"}


def ma(x) -> str:
    return x if isinstance(x, str) and MA.fullmatch(x) else "?"


def so(x) -> str:
    return str(x) if isinstance(x, int) and not isinstance(x, bool) else "?"


def sha(x) -> str:
    return x[:7] if isinstance(x, str) and SHA.fullmatch(x) else "?"


def pham_vi(x) -> str:
    return x if isinstance(x, str) and PHAM_VI.fullmatch(x) and ".." not in x else "?"


def chon(bang: dict, x, mac_dinh: str = "?") -> str:
    return bang.get(x, mac_dinh) if isinstance(x, str) else mac_dinh


def adr(x) -> str:
    return x if isinstance(x, str) and ADR.fullmatch(x) else ""


def khe_tho(tac_nhan: str) -> str:
    """Báo cáo của thợ mang tác nhân `tho/<khe_id>` — chỉ lấy khi đúng dạng mã khe."""
    return ma(tac_nhan[4:]) if isinstance(tac_nhan, str) and tac_nhan.startswith("tho/") else "?"


def mo_ta(s: SuKien) -> str:
    from tram.suy.mau_su_kien import MAU
    mau = MAU.get(s.loai)
    if mau is None or not isinstance(s.du_lieu, dict):
        return ""
    try:
        return mau(s.du_lieu, s)
    except (KeyError, TypeError, ValueError, AttributeError):
        return ""
```

`tram/suy/su_kien_gan_day.py` (mới):

```python
"""Sự kiện gần đây mọi dự án cho Tổng quan (D17/D38, khảo sát A3): danh sách cho phép từng trường + mô tả từ mẫu cố
định. Bỏ loại ồn (`dieu_phoi.nhip` ~1 dòng/phút — ranh giới 2e/2f; cập nhật hạn mức mỗi nhịp). Sự kiện `nho.*`
chỉ Đại ca thấy mô tả (như dòng thời gian bead của `/api/bead`)."""
from tram.su_kien.kho import KhoSuKien
from tram.suy.lam_sach import lam_sach
from tram.suy.mo_ta_su_kien import ma, mo_ta

QUET = 500                       # đọc tối đa 500 sự kiện mới nhất rồi lọc
BO = frozenset({"dieu_phoi.nhip", "khe.han_muc", "khe.han_muc_khong_ro"})
CHE_NHO = "Ký ức: chỉ Đại ca xem chi tiết."


def dong(s, *, la_dai_ca: bool) -> dict:
    che = s.loai.startswith("nho.") and not la_dai_ca
    return {"id": s.id, "luc": s.luc, "loai": lam_sach(s.loai, 40), "du_an": lam_sach(s.du_an, 64),
            "bead_id": ma(s.bead_id) if s.bead_id else None, "tac_nhan": lam_sach(s.tac_nhan, 80),
            "mo_ta": CHE_NHO if che else mo_ta(s)}


def gan_day(kho: KhoSuKien, gioi_han: int, *, la_dai_ca: bool) -> list[dict]:
    moc = max(0, kho.id_moi_nhat() - QUET)
    ds = [s for s in kho.sau_id(moc, QUET) if s.loai not in BO]
    return [dong(s, la_dai_ca=la_dai_ca) for s in reversed(ds[-gioi_han:])] if gioi_han > 0 else []
```

- [ ] **Step 4: Chạy thấy PASS**

```bash
uv run --offline pytest -q tests/test_mo_ta_su_kien.py
uv run --offline pytest -q
```

Kỳ vọng: PASS — lệnh test của task: 5 passed in 0.78s; toàn bộ tăng đúng 5 py test so với main trước task (bảng "Sơ đồ đợt chạy"). Số đo trên bản chạy thử.

- [ ] **Step 5: Commit**

```bash
git add tests/test_mo_ta_su_kien.py tram/api/tuyen_nho.py tram/suy/mau_nho.py tram/suy/mau_su_kien.py tram/suy/mo_ta_su_kien.py tram/suy/su_kien_gan_day.py
git commit -m "feat(api): 2f mô tả sự kiện từ mẫu cố định (D39)"
```

### Task 6: API Cài đặt + bảng sẵn sàng — `GET /api/cai-dat`, `GET /api/san-sang` (chỉ Đại ca)

**Đợt:** 2 · **Độ khó:** vừa · **Phải xong trước:** Task 4 · **Test mới:** 10 py (API 7, sẵn sàng 3)

**Mockup bám:** `trang-cai-dat.js`, `du-lieu.js` (`CAU_HINH_DU_AN`, `DICH_VU`, `TELEGRAM`, `CO`, `KEYCHAIN`, `SAN_SANG`); ảnh `anh-cai-dat.png`. Khảo sát §1.6, §1.10 bảng A1/A2. D19, D24 (mã điều phối có/chưa), D38/Q13 (G13).

**Files:**
- Create: `tram/suy/cai_dat.py` (gom cấu hình: dự án — đường dẫn rút gọn `~`, không `tu_khoa_khach`, không nội dung `moi_truong_kiem`; Telegram; cờ; lỗi cấu hình chỉ "YAML hỏng ở dòng N" vì thông báo PyYAML chép nguyên dòng hỏng có thể chứa email/từ khoá khách), `tram/suy/san_sang.py` (tự kiểm rẻ chỉ đọc + bead repo trạm nhãn `san-sang`, bộ đệm 60 giây, `bd` timeout 3 giây), `tram/api/cai_dat.py` (hai route, `Depends(yeu_cau_dai_ca)`)
- Modify: `tram/api/app.py` (một import + `CAC_TUYEN += (cai_dat.router,)` — G28; `tuyen_chu.router` mang `Depends(yeu_cau_ghi)` cấp router nên không gắn được route GET vào đó)
- Test: `tests/test_api_cai_dat.py`, `tests/test_san_sang.py` (mới)

**Interfaces:**
- Consumes: `doc_he_thong()` (Task 4), `nap_du_an`, `liet_ke_du_an`, `nap_cau_hinh_tram`, `nap_cau_hinh_giao_viec`, `nap_cau_hinh_cong_bo`, `nap_cau_hinh_cach_ly`, `nap_cau_hinh_usage`, `doc_bam` (mã Đại ca, mã điều phối), `NHAN_LOAI`, `estop.dang_bat`, `Bd(goc_repo())`.
- Produces: JSON `/api/cai-dat`, `/api/san-sang` ở "Hợp đồng (lát 2f)". Task 14 đọc.

Bảo mật: test đặt token, email `dai_ca_logins`, stdout giả của `security`, `tu_khoa_khach` vào nguồn và kiểm chúng không có trong JSON; bộ chạy giả ghi lại argv để kiểm không bao giờ có `-w`, `sudo`, `tram tho kiem`, `tram giao kiem`; 403 cho cả hai route khi không phải Đại ca; 421 Host lạ; có CSP. Bead `san-sang`: `closed` → `dat`; mở và có `blocks` vào bead chưa đóng (kể cả mã không có trong danh sách) → `cho` "cần <id>"; còn lại → `thieu`; chỉ trả `lam_sach(title, 120)`, không mô tả/notes. Repo trạm hiện chưa có bead nhãn `san-sang` → bảng chỉ có mục tự kiểm cho tới khi gắn nhãn (Chờ chốt 3).

- [ ] **Step 1: Viết test (chép nguyên văn)**

`tests/test_api_cai_dat.py` (mới):

```python
"""2f P3: GET /api/cai-dat, /api/san-sang — chỉ Đại ca, Host + CSP, không lộ bí mật, không chạy lệnh có tác dụng phụ."""
import json
import subprocess
from pathlib import Path

from api_gia import DAI_CA, LOGIN, MAY_B, tao_pt
from asgi_gia import goi
from bd_gia import BdGia
from test_he_thong import ChayGia
from test_san_sang import BEADS
from tram.api.app import tao_app
from tram.cau_hinh.tram import CauHinhTelegram, CauHinhTram
from tram.suy import he_thong, san_sang
from tram.suy.he_thong import DocHeThong
from tram.suy.san_sang import BangSanSang

H = {"Tailscale-User-Login": LOGIN}
EMAIL_2, CHAT_ID, BAM = "bi-mat-2@example.com", "CHAT-987654321", "ab" * 32
BI_MAT_SEC = "BI-MAT-STDOUT \"acct\"<blob>=\"tram\" pid = 777"
DU_AN_YAML = ('ten: hr\nduong_dan: "{home}/Developer/hr-thu"\ngitnexus_repo: hr-graph\ntu_khoa_khach: [KHACH-BI-MAT]\n'
              'lenh_cho_phep: ["uv run pytest -q"]\nmoi_truong_kiem: {{file: "{mt}", dich: ".env.testing"}}\n'
              'hang_rao: {{tien: {{tu_khoa: [hoàn tiền, thuế], duong_dan: ["*Fin/*"]}}}}\n')

def _dung(tmp_path, monkeypatch, *, du_an_yaml=DU_AN_YAML, cau_hinh=f"ma_dai_ca_sha256: {BAM}\n"):
    lenh = []

    def cam(*a, **k):                                         # mọi lệnh thật đều bị ghi lại rồi chặn
        lenh.append(a)
        raise AssertionError("không được chạy lệnh thật")
    monkeypatch.setattr(subprocess, "run", cam)
    monkeypatch.setattr(subprocess, "Popen", cam)
    (tmp_path / "mt.env").write_text("DB_PASSWORD=MT-BI-MAT")
    (tmp_path / "repo" / "du-an").mkdir(parents=True)
    (tmp_path / "repo" / "du-an" / "hr.yaml").write_text(du_an_yaml.format(home=Path.home(), mt=tmp_path / "mt.env"))
    monkeypatch.setenv("TRAM_REPO", str(tmp_path / "repo"))
    (tmp_path / "tram-home").mkdir(exist_ok=True)
    (tmp_path / "tram-home" / "cau-hinh.yaml").write_text(cau_hinh)
    chay = ChayGia({"tram-telegram-bot-token": (0, BI_MAT_SEC), "gui/501/vn.tram.api": (0, "state = running\npid=777")})
    monkeypatch.setattr(he_thong, "_CHUNG", DocHeThong(chay=chay, home=tmp_path, uid=501))
    monkeypatch.setattr(san_sang, "CHUNG", BangSanSang(doc_bead=lambda: BEADS, which=lambda l: l != "ollama" or None))
    pt = tao_pt(tmp_path, {"hr": BdGia([])})
    pt.cau_hinh = CauHinhTram(dai_ca_logins=(LOGIN, EMAIL_2), ten_may_b=MAY_B,
                              telegram=CauHinhTelegram(CHAT_ID, "23:00-07:00"), dashboard_url="https://x.ts.net")
    return tao_app(pt), chay, lenh


def test_403_khi_khong_phai_dai_ca(tmp_path, monkeypatch):
    app, chay, lenh = _dung(tmp_path, monkeypatch)
    for h in ({}, {"Tailscale-User-Login": "nguoi-la@example.com"}, {**DAI_CA, "Tailscale-User-Login": "x@y.z"}):
        for duong in ("/api/cai-dat", "/api/san-sang"):
            r = goi(app, "GET", duong, headers=h)
            assert r.status == 403 and "content-security-policy" in r.headers and "Đại ca" in r.json()["detail"]
    assert chay.argv == [] and lenh == []


def test_421_host_la_va_csp(tmp_path, monkeypatch):
    app, _, _ = _dung(tmp_path, monkeypatch)
    for duong in ("/api/cai-dat", "/api/san-sang"):
        r = goi(app, "GET", duong, headers={**H, "Host": "rebind.evil.example"})
        assert r.status == 421 and "content-security-policy" in r.headers
        r = goi(app, "GET", duong, headers=H)                 # GET không cần X-Tram / Origin
        assert r.status == 200 and "default-src 'none'" in r.headers["content-security-policy"]


def test_cai_dat_hinh_json(tmp_path, monkeypatch):
    app, _, _ = _dung(tmp_path, monkeypatch)
    j = goi(app, "GET", "/api/cai-dat", headers=H).json()
    assert set(j) == {"du_an", "dich_vu", "telegram", "co", "keychain", "loi_cau_hinh"} and j["loi_cau_hinh"] == []
    assert j["du_an"] == [{"ten": "hr", "duong_dan": "~/Developer/hr-thu", "nhanh_chinh": "main",
                           "gitnexus": "hr-graph", "lenh_cho_phep": ["uv run pytest -q"], "moi_truong_kiem": True,
                           "hang_rao": [{"loai": "tien", "tu_khoa": ["hoàn tiền", "thuế"], "duong_dan": ["*Fin/*"]}],
                           "loi": None}]
    assert j["dich_vu"][0] == {"nhan": "vn.tram.api", "viec": "dashboard + API", "da_cai": False, "dang_chay": True,
                               "kiem_duoc": True} and len(j["dich_vu"]) == 5
    assert j["telegram"]["co_chat_id"] is True and j["telegram"]["gio_yen_lang"] == "23:00-07:00" \
        and "cờ đỏ" in j["telegram"]["loai_tin"]
    co = {c["khoa"]: c for c in j["co"]}
    assert all(set(c) == {"khoa", "bat", "gia_tri", "ghi_chu"} and c["ghi_chu"] for c in j["co"])
    assert co["estop"]["bat"] is False and co["giao_viec.bat"]["bat"] is False and co["ma_dai_ca"]["bat"] is True
    assert co["dai_ca_logins"]["gia_tri"] == "2" and co["ma_dieu_phoi"]["bat"] is False
    assert co["cach_ly.kenh_ghi"]["gia_tri"] == "header" and co["cong_bo.phuong_an"]["gia_tri"] is None
    assert [k["trang_thai"] for k in j["keychain"]] == ["co", "khong_ro", "khong_ro", "khong_ro"]
    # G15/G13: kênh hợp lệ dùng enum unix-socket, không phải unix; kiểm cả hai trạng thái.
    from tram.cau_hinh.cach_ly import CauHinhCachLy
    from tram.suy import cai_dat as suy_cai_dat
    for kenh, bat in (("header", False), ("unix-socket", True)):
        monkeypatch.setattr(suy_cai_dat, "nap_cau_hinh_cach_ly", lambda: CauHinhCachLy(kenh_ghi=kenh))
        cs = {c["khoa"]: c for c in goi(app, "GET", "/api/cai-dat", headers=H).json()["co"]}
        assert cs["cach_ly.kenh_ghi"]["gia_tri"] == kenh and cs["cach_ly.kenh_ghi"]["bat"] is bat


def test_khong_lo_bi_mat(tmp_path, monkeypatch):
    app, _, _ = _dung(tmp_path, monkeypatch)
    s = "".join(goi(app, "GET", d, headers=H).body.decode() for d in ("/api/cai-dat", "/api/san-sang"))
    for x in ("KHACH-BI-MAT", "MT-BI-MAT", "mt.env", EMAIL_2, LOGIN, CHAT_ID, BAM, "BI-MAT-STDOUT", "777",
              "MO-TA-BI-MAT", "NOTES-BI-MAT", "x.ts.net", MAY_B, "gui/501", "find-generic-password"):
        assert x not in s, x


def test_loi_cau_hinh_khong_hong_ca_trang(tmp_path, monkeypatch):
    hong = "dai_ca_logins: [lo@x.vn]\ngiao_viec: {bat: [\n"           # YAML hỏng: lỗi không được chép dòng có email
    app, _, _ = _dung(tmp_path, monkeypatch, du_an_yaml="ten: hr\ntu_khoa_khach: [KHACH-BI-MAT\n", cau_hinh=hong)
    r = goi(app, "GET", "/api/cai-dat", headers=H)
    j, co = r.json(), {c["khoa"]: c for c in r.json()["co"]}
    assert r.status == 200 and co["giao_viec.bat"]["bat"] is None and co["cong_bo.phuong_an"]["bat"] is None
    assert co["estop"]["bat"] is False and len(j["dich_vu"]) == 5 and len(j["loi_cau_hinh"]) == 3
    assert all(len(x) <= 200 for x in j["loi_cau_hinh"]) and j["du_an"][0]["loi"] == "YAML hỏng ở dòng 3"
    assert "lo@x.vn" not in r.body.decode() and "KHACH-BI-MAT" not in r.body.decode()
    from tram.suy.cai_dat import mo_ta_loi

    for e in (ValueError("TEN-BI-MAT"), FileNotFoundError("/private/ENV-BI-MAT"), RuntimeError("NOI-DUNG-BI-MAT")):
        loi = mo_ta_loi(e)
        assert loi and "BI-MAT" not in loi and "/private/" not in loi


def test_khong_goi_lenh_co_tac_dung_phu(tmp_path, monkeypatch):
    app, chay, lenh = _dung(tmp_path, monkeypatch)
    for _ in range(2):
        for duong in ("/api/san-sang", "/api/cai-dat"):
            assert goi(app, "GET", duong, headers=H).status == 200
    assert lenh == []                                         # không có subprocess thật nào
    assert all(a[:2] in (["launchctl", "print"], ["security", "find-generic-password"]) for a in chay.argv)
    assert len(chay.argv) == 9                                # bộ đệm: các lần sau không chạy lại
    s = json.dumps(chay.argv)
    assert "sudo" not in s and "kiem" not in s and "-w" not in s and all(a[0] != "tram" for a in chay.argv)
    j = goi(app, "GET", "/api/san-sang", headers=H).json()
    assert set(j) == {"muc", "dem", "doc_luc", "loi"} and j["loi"] is None
    assert [m["ma"] for m in j["muc"] if m["nguon"] == "bead"] == ["bs-1", "bs-2", "bs-3", "bs-5", "bs-6"]


def test_estop_post_van_can_x_tram(tmp_path, monkeypatch):
    app, _, _ = _dung(tmp_path, monkeypatch)                  # route chủ: thêm /api/cai-dat không nới POST estop
    than = {"ly_do": "thử", "ma_thao_tac": "ma-estop-0001", "expected_version": ""}
    for duong in ("/api/chu/estop", "/api/chu/tiep-tuc"):
        assert goi(app, "POST", duong, json_body=than, headers=H).status == 403
```

`tests/test_san_sang.py` (mới):

```python
"""2f P3: bảng sẵn sàng — suy trạng thái bead nhãn `san-sang`, tự kiểm, lỗi bd không làm mất phần tự kiểm, bộ đệm."""
import json

from test_he_thong import ChayGia, DongHo
from tram.beads.bd import LoiBd
from tram.beads.mo_hinh import Bead
from tram.suy.he_thong import DocHeThong
from tram.suy.san_sang import LOI_BEAD, BangSanSang, tu_bead


def _bead(id_, status="open", nhan=("san-sang",), chan=(), con=()):
    phu = [{"depends_on_id": c, "type": "blocks"} for c in chan] + [{"depends_on_id": c, "type": "parent-child"}
                                                                     for c in con]
    return Bead.tu_json({"id": id_, "title": f"Cổng {id_}‮", "description": "MO-TA-BI-MAT", "notes": "NOTES-BI-MAT",
                         "status": status, "labels": list(nhan), "updated_at": "2026-10-16T00:00:00Z",
                         "dependencies": phu})


BEADS = [_bead("bs-1", "closed"), _bead("bs-2", chan=["bs-3"]), _bead("bs-3", chan=["bs-1"]),
         _bead("bs-4", nhan=()), _bead("bs-5", con=["bs-3"]), _bead("bs-6", chan=["bs-3", "bs-x"])]


def test_suy_trang_thai_bead():
    ds = tu_bead(BEADS)
    assert [(m["ma"], m["trang_thai"], m["ghi_chu"]) for m in ds] == [
        ("bs-1", "dat", ""), ("bs-2", "cho", "cần bs-3"), ("bs-3", "thieu", ""),        # blocks vào bead đã đóng
        ("bs-5", "thieu", ""), ("bs-6", "cho", "cần bs-3, bs-x")]                       # parent-child không chặn
    assert ds[0] == {"ma": "bs-1", "ten": "Cổng bs-1", "trang_thai": "dat", "ghi_chu": "", "nguon": "bead"}
    s = json.dumps(ds, ensure_ascii=False)
    assert "MO-TA-BI-MAT" not in s and "NOTES-BI-MAT" not in s and "bs-4" not in s


def _bang(tmp_path, doc_bead, dong_ho=None):
    he = DocHeThong(chay=ChayGia({"tram-nho-token": (0, "x")}), home=tmp_path, uid=501, dong_ho=DongHo())
    return BangSanSang(doc_bead=doc_bead, which=lambda l: l == "bd" or None, dong_ho=dong_ho or DongHo()), he


def test_tu_kiem_va_dem(tmp_path):
    bang, he = _bang(tmp_path, lambda: BEADS)
    j = bang.lay(he)
    tu = {m["ma"]: m for m in j["muc"] if m["nguon"] == "tu_kiem"}
    assert [m for m in tu if m.startswith("lenh:")] == ["lenh:bd", "lenh:tailscale", "lenh:gh", "lenh:codex",
                                                        "lenh:claude", "lenh:gitnexus", "lenh:uv", "lenh:ollama"]
    assert tu["lenh:bd"]["trang_thai"] == "dat" and tu["lenh:ollama"]["trang_thai"] == "thieu"
    assert [m for m in tu if m.startswith("dich-vu:")] == ["dich-vu:vn.tram.api", "dich-vu:vn.tram.quet",
                                                           "dich-vu:vn.tram.nho", "dich-vu:vn.tram.bao-tin"]
    assert tu["dich-vu:vn.tram.api"] == {"ma": "dich-vu:vn.tram.api", "ten": "Đã cài vn.tram.api",
                                         "trang_thai": "thieu", "ghi_chu": "chưa có plist trong ~/Library/LaunchAgents",
                                         "nguon": "tu_kiem"}
    assert tu["keychain:tram-nho-token"]["trang_thai"] == "dat"
    assert tu["keychain:tram-noi-bo-token"]["ghi_chu"] == "không kiểm được (Keychain khoá?)"
    assert j["dem"] == {"dat": 3, "thieu": 16, "cho": 2} and j["loi"] is None and j["doc_luc"].endswith("Z")


def test_loi_bd_van_tra_tu_kiem_va_bo_dem_60_giay(tmp_path):
    goi, dh = [], DongHo()

    def doc():
        goi.append(1)
        raise LoiBd("bd lỗi: STDERR-BI-MAT /Users/x/.beads")
    bang, he = _bang(tmp_path, doc, dh)
    j = bang.lay(he)
    assert j["loi"] == LOI_BEAD and j["muc"] and all(m["nguon"] == "tu_kiem" for m in j["muc"])
    assert "STDERR-BI-MAT" not in json.dumps(j, ensure_ascii=False)
    dh.t += 59
    bang.lay(he)
    assert len(goi) == 1
    dh.t += 1
    bang.lay(he)
    assert len(goi) == 2
```

- [ ] **Step 2: Chạy thấy FAIL**

```bash
uv run --offline pytest -q tests/test_api_cai_dat.py tests/test_san_sang.py
```

Kỳ vọng: FAIL — `ModuleNotFoundError: No module named 'tram.suy.san_sang'`

- [ ] **Step 3: Viết mã (chép nguyên văn; file sửa: chép khối diff ra file tạm, `git apply --check` rồi `git apply`)**

`tram/api/app.py` (sửa):

```diff
diff --git a/tram/api/app.py b/tram/api/app.py
index 5536e3b..4d427e2 100644
--- a/tram/api/app.py
+++ b/tram/api/app.py
@@ -4,7 +4,7 @@ from fastapi.responses import JSONResponse
 from fastapi.staticfiles import StaticFiles
 
 from tram.api import doi_ngu, ghep, luong, noi_bo, tho, tho_them, tuyen_chu, tuyen_doc, tuyen_ghi, tuyen_nho, usage
-from tram.api import tuyen_feature, van_phong
+from tram.api import cai_dat, tuyen_feature, van_phong
 from tram.api.bao_mat import them_header_an_toan
 from tram.api.phu_thuoc import PhuThuocApi
 from tram.api.tuyen_giao import router as tuyen_giao
@@ -19,6 +19,7 @@ CAC_TUYEN = (tuyen_feature.router, tuyen_doc.router, tuyen_ghi.router, tuyen_chu
              luong.router, tho.router, noi_bo.router, doi_ngu.router, usage.router, tho_them.router, ghep.router)
 CAC_TUYEN += (tuyen_giao,)                     # 4a-2: GET /api/giao-viec
 CAC_TUYEN += (van_phong.router,)               # 2c: GET /api/van-phong
+CAC_TUYEN += (cai_dat.router,)                 # 2f: GET /api/cai-dat, /api/san-sang (chỉ Đại ca)
 
 
 def _xu_ly(ma: int):
```

`tram/api/cai_dat.py` (mới):

```python
"""Trang Cài đặt (D19, D38/Q13; khảo sát §1.10 A1, A2): `GET /api/cai-dat`, `GET /api/san-sang` — CHỈ Đại ca, chỉ đọc.

Quyền giống `/api/nho` (`la_dai_ca_yeu_cau`: đúng một `Tailscale-User-Login` thuộc `dai_ca_logins`, đúng kênh) →
khác thì 403. Không ghi, không `ma_thao_tac`, không chạy lệnh có tác dụng phụ. Route `def` đồng bộ (threadpool).
Đăng ký router riêng trong app.py ở Task 6; Task 8 giữ đăng ký này khi thêm tong_quan.router."""
from fastapi import APIRouter, Depends, HTTPException, Request

from tram.api.bao_mat import la_dai_ca_yeu_cau
from tram.suy import he_thong, san_sang
from tram.suy.cai_dat import gom_cai_dat


def yeu_cau_dai_ca(request: Request) -> None:
    """Như `tuyen_nho.yeu_cau_dai_ca`, câu 403 riêng cho trang Cài đặt."""
    if not la_dai_ca_yeu_cau(request):
        raise HTTPException(status_code=403, detail="Cài đặt chỉ Đại ca xem được (cần danh tính Tailscale của Đại ca)")


router = APIRouter(dependencies=[Depends(yeu_cau_dai_ca)])


@router.get("/api/cai-dat")
def r_cai_dat(request: Request) -> dict:
    pt = request.app.state.pt
    return gom_cai_dat(pt.cau_hinh, pt.usage, pt.cac_du_an, he_thong.doc_he_thong())


@router.get("/api/san-sang")
def r_san_sang() -> dict:
    return san_sang.CHUNG.lay(he_thong.doc_he_thong())
```

`tram/suy/cai_dat.py` (mới):

```python
"""Gom cấu hình cho trang Cài đặt (D19; khảo sát §1.6, §1.10 A1). CHỈ ĐỌC, danh sách cho phép từng trường.

Không bao giờ trả: `tu_khoa_khach`, nội dung/đường dẫn file `moi_truong_kiem`, `chat_id`, email `dai_ca_logins`,
`ten_may_b`, `dashboard_url`, mọi bản băm, đường dẫn ccusage. Mỗi lỗi nạp cấu hình chỉ làm hỏng mục của nó:
câu lỗi cố định qua `lam_sach(…, 200)` vào `loi_cau_hinh`; YAML chỉ thêm số dòng, các lỗi khác không dùng str(e)."""
from collections.abc import Callable
from pathlib import Path

import yaml

from tram.bao_tin.tin import NHAN_LOAI
from tram.cau_hinh.cach_ly import nap_cau_hinh_cach_ly
from tram.cau_hinh.cong_bo import nap_cau_hinh_cong_bo
from tram.cau_hinh.du_an import DuAn, nap_du_an
from tram.cau_hinh.giao_viec import nap_cau_hinh_giao_viec
from tram.cau_hinh.tram import CauHinhTram
from tram.cau_hinh.usage import CauHinhUsage
from tram.chu import estop, ma_dieu_phoi
from tram.nho import ma_dai_ca
from tram.suy.he_thong import DocHeThong
from tram.suy.lam_sach import lam_sach

TOI_DA_DS = 50


def mo_ta_loi(e: Exception) -> str:
    """Không đưa giá trị cấu hình/đường dẫn từ exception vào API; YAML chỉ nêu vị trí."""
    if isinstance(e, yaml.MarkedYAMLError) and e.problem_mark is not None:
        return f"YAML hỏng ở dòng {e.problem_mark.line + 1}"
    if isinstance(e, yaml.YAMLError):
        return "YAML hỏng"
    if isinstance(e, ValueError):
        return "Giá trị cấu hình không hợp lệ"
    if isinstance(e, OSError):
        return "Không đọc được cấu hình"
    return "Không nạp được cấu hình"


def _rut_gon(p: Path) -> str:
    try:
        return "~/" + str(p.relative_to(Path.home()))
    except ValueError:
        return str(p)


def _ds(xs) -> list[str]:
    return [lam_sach(str(x), 200) for x in list(xs)[:TOI_DA_DS]]


def mot_du_an(ten: str, nap: Callable[[str], DuAn] = nap_du_an) -> dict:
    try:
        d = nap(ten)
    except Exception as e:
        return {"ten": lam_sach(ten, 64), "duong_dan": "", "nhanh_chinh": "", "gitnexus": None, "lenh_cho_phep": [],
                "hang_rao": [], "moi_truong_kiem": False, "loi": lam_sach(mo_ta_loi(e), 200)}
    return {"ten": lam_sach(d.ten, 64), "duong_dan": lam_sach(_rut_gon(d.duong_dan), 300),
            "nhanh_chinh": lam_sach(d.nhanh_chinh, 100),
            "gitnexus": lam_sach(d.gitnexus_repo, 100) if d.gitnexus_repo else None,
            "lenh_cho_phep": _ds(d.lenh_cho_phep),
            "hang_rao": [{"loai": loai, "tu_khoa": _ds(r.tu_khoa), "duong_dan": _ds(r.duong_dan)}
                         for loai, r in d.hang_rao.items()],
            "moi_truong_kiem": d.moi_truong_kiem is not None, "loi": None}


def _co(ch: CauHinhTram, usage: CauHinhUsage) -> list[tuple[str, str, Callable[[], tuple]]]:
    """(khoá, ghi chú cố định, hàm đọc → (bat, gia_tri)). Cờ bool: gia_tri None; cờ giá trị: bat = có giá trị."""
    def pa():
        p = nap_cau_hinh_cong_bo().phuong_an
        return p is not None, lam_sach(p, 40) or None

    def kenh():
        k = nap_cau_hinh_cach_ly().kenh_ghi
        return k == "unix-socket", lam_sach(k, 40)
    return [
        ("estop", "BẬT = dừng khẩn cấp, trạm không tự làm việc", lambda: (estop.dang_bat(), None)),
        ("giao_viec.bat", "chỉ bật sau 3a-2, S6, S7", lambda: (nap_cau_hinh_giao_viec().bat, None)),
        ("cong_bo.phuong_an", "cách công bố PR; trống = chưa chốt (sau S7)", pa),
        ("cach_ly.kenh_ghi", "unix-socket = API ghi chỉ qua socket cục bộ; header = qua header Tailscale", kenh),
        ("usage.ccusage", "màn Usage đọc log Claude Code qua ccusage",
         lambda: (usage.ccusage is not None, lam_sach(usage.ccusage_phien_ban, 40) or None)),
        ("usage.gia", "bảng giá USD theo mô hình", lambda: (bool(usage.gia), f"{len(usage.gia)} mô hình")),
        ("ten_may_b", "tên máy B trên tailnet — cần cho mọi thao tác ghi", lambda: (ch.ten_may_b is not None, None)),
        ("dashboard_url", "link dashboard gắn vào tin Telegram", lambda: (ch.dashboard_url is not None, None)),
        ("dai_ca_logins", "số danh tính Tailscale của Đại ca (không hiện email)",
         lambda: (bool(ch.dai_ca_logins), str(len(ch.dai_ca_logins)))),
        ("ma_dai_ca", "băm mã Đại ca cho phiên tay ký ức (1b-2)", lambda: (ma_dai_ca.doc_bam() is not None, None)),
        ("ma_dieu_phoi", "băm mã điều phối cho hook máy A (D24)", lambda: (ma_dieu_phoi.doc_bam() is not None, None)),
    ]


def doc_co(ch: CauHinhTram, usage: CauHinhUsage, loi: list[str]) -> list[dict]:
    ra = []
    for khoa, ghi_chu, doc in _co(ch, usage):
        try:
            bat, gia_tri = doc()
        except Exception as e:                             # lỗi một khoá không làm hỏng cả trang
            loi.append(lam_sach(f"{khoa}: {mo_ta_loi(e)}", 200))
            bat, gia_tri = None, None
        ra.append({"khoa": khoa, "bat": bat, "gia_tri": gia_tri, "ghi_chu": ghi_chu})
    return ra


def gom_cai_dat(ch: CauHinhTram, usage: CauHinhUsage, cac_du_an: Callable[[], list[str]], he: DocHeThong,
                nap: Callable[[str], DuAn] = nap_du_an) -> dict:
    loi: list[str] = []
    try:
        ds = [mot_du_an(t, nap) for t in cac_du_an()]
    except Exception as e:
        ds = []
        loi.append(lam_sach(f"du-an: {mo_ta_loi(e)}", 200))
    tg = {"co_chat_id": ch.telegram.chat_id is not None, "gio_yen_lang": ch.telegram.gio_yen_lang,
          "loai_tin": list(NHAN_LOAI.values())}
    co = doc_co(ch, usage, loi)
    return {"du_an": ds, "dich_vu": he.dich_vu(), "telegram": tg, "co": co, "keychain": he.keychain(),
            "loi_cau_hinh": loi}
```

`tram/suy/san_sang.py` (mới):

```python
"""Bảng sẵn sàng chạy thật cho trang Cài đặt (D19, D38/Q13; khảo sát §1.10 A2). CHỈ ĐỌC.

Hai nguồn: (b) bead của REPO TRẠM có nhãn `san-sang` (`Bd(goc_repo()).tat_ca()`, bộ đệm 60 giây) — closed → dat; mở
và bị `blocks` bởi bead chưa đóng → cho ("cần <id>"); còn lại → thieu; chỉ trả tiêu đề đã làm sạch, KHÔNG mô tả/notes.
(a) tự kiểm rẻ: lệnh trong PATH (`shutil.which`), dịch vụ đã cài, Keychain (`DocHeThong`, có bộ đệm riêng).
KHÔNG BAO GIỜ gọi `tram tho kiem` / `tram giao kiem` (có sudo, touch, sleep — khảo sát §1.10 mục 5)."""
import shutil
import subprocess
import threading
import time
from collections.abc import Callable, Sequence

from tram.beads.bd import Bd, LoiBd
from tram.beads.mo_hinh import Bead
from tram.chu.launchd import NHAN_API, NHAN_BAO_TIN, NHAN_NHO, NHAN_QUET
from tram.duong_dan import bay_gio, goc_repo
from tram.suy.he_thong import GIAY_CHO, DocHeThong
from tram.suy.lam_sach import lam_sach

NHAN_SAN_SANG = "san-sang"
LENH = ("bd", "tailscale", "gh", "codex", "claude", "gitnexus", "uv", "ollama")
DICH_VU_CAN = (NHAN_API, NHAN_QUET, NHAN_NHO, NHAN_BAO_TIN)
GIAY_BEAD = 60
LOI_BEAD = "Không đọc được bead của repo trạm (bd) — bảng chỉ còn phần tự kiểm"
GHI_KEYCHAIN = {"co": ("dat", ""), "chua": ("thieu", "chưa có trong Keychain"),
                "khong_ro": ("thieu", "không kiểm được (Keychain khoá?)")}


def _chay_bd(args: Sequence[str]) -> str:
    """Runner chỉ đọc cho `Bd`: timeout 3 giây; câu lỗi cố định, không mang stderr."""
    try:
        kq = subprocess.run(["bd", *args], capture_output=True, text=True, timeout=GIAY_CHO, stdin=subprocess.DEVNULL)
    except (OSError, subprocess.TimeoutExpired):
        raise LoiBd("bd không chạy được") from None
    if kq.returncode != 0:
        raise LoiBd("bd trả mã lỗi")
    return kq.stdout


def doc_bead_tram() -> list[Bead]:
    return Bd(goc_repo(), runner=_chay_bd).tat_ca()


def _muc(ma: str, ten: str, tt: str, ghi_chu: str, nguon: str) -> dict:
    return {"ma": ma, "ten": ten, "trang_thai": tt, "ghi_chu": ghi_chu, "nguon": nguon}


def tu_bead(ds: list[Bead]) -> list[dict]:
    dong = {b.id for b in ds if b.status == "closed"}
    ra = []
    for b in ds:
        if NHAN_SAN_SANG not in b.labels:
            continue
        # phụ thuộc `blocks` vào bead chưa đóng (kể cả mã không còn trong danh sách) → chưa tới lượt
        can = [lam_sach(p.depends_on_id, 64) for p in b.phu_thuoc if p.loai == "blocks" and p.depends_on_id not in dong]
        if b.status == "closed":
            tt, ghi = "dat", ""
        elif can:
            tt, ghi = "cho", "cần " + ", ".join(can[:3])
        else:
            tt, ghi = "thieu", ""
        ra.append(_muc(lam_sach(b.id, 64), lam_sach(b.title, 120), tt, ghi, "bead"))
    return ra


def _ghi_dich_vu(d: dict) -> str:
    if not d["da_cai"]:
        return "chưa có plist trong ~/Library/LaunchAgents"
    if d["dang_chay"]:
        return ""
    return "đã cài, chưa chạy" if d["kiem_duoc"] else "không kiểm được launchctl"


def tu_kiem(he: DocHeThong, which: Callable[[str], object] = shutil.which) -> list[dict]:
    ra = []
    for l in LENH:
        co = bool(which(l))
        ra.append(_muc(f"lenh:{l}", f"Có lệnh {l} trong PATH", "dat" if co else "thieu",
                       "" if co else "không thấy trong PATH của tram-api", "tu_kiem"))
    for d in he.dich_vu():
        if d["nhan"] in DICH_VU_CAN:
            ra.append(_muc(f"dich-vu:{d['nhan']}", f"Đã cài {d['nhan']}", "dat" if d["da_cai"] else "thieu",
                           _ghi_dich_vu(d), "tu_kiem"))
    for k in he.keychain():
        ra.append(_muc(f"keychain:{k['ten']}", f"Keychain có {k['ten']}", *GHI_KEYCHAIN[k["trang_thai"]], "tu_kiem"))
    return ra


class BangSanSang:
    def __init__(self, *, doc_bead: Callable[[], list[Bead]] = doc_bead_tram,
                 which: Callable[[str], object] = shutil.which, dong_ho: Callable[[], float] = time.monotonic):
        self._doc_bead, self._which, self._dong_ho = doc_bead, which, dong_ho
        self._nho: tuple[float, list[dict], str | None, str] | None = None
        self._khoa = threading.Lock()

    def _bead(self) -> tuple[list[dict], str | None, str]:
        with self._khoa:
            bay = self._dong_ho()
            if self._nho is None or bay - self._nho[0] >= GIAY_BEAD:
                try:
                    muc, loi = tu_bead(self._doc_bead()), None
                except Exception:                          # không đưa câu lỗi bd ra ngoài
                    muc, loi = [], LOI_BEAD
                self._nho = (bay, muc, loi, bay_gio())
            return [dict(m) for m in self._nho[1]], self._nho[2], self._nho[3]

    def lay(self, he: DocHeThong) -> dict:
        muc, loi, luc = self._bead()
        muc += tu_kiem(he, self._which)
        return {"muc": muc, "dem": {k: sum(m["trang_thai"] == k for m in muc) for k in ("dat", "thieu", "cho")},
                "doc_luc": luc, "loi": loi}


CHUNG = BangSanSang()                                       # dùng chung cả tiến trình; test thay bằng monkeypatch
```

- [ ] **Step 4: Chạy thấy PASS**

```bash
uv run --offline pytest -q tests/test_api_cai_dat.py tests/test_san_sang.py
uv run --offline pytest -q
```

Kỳ vọng: PASS — lệnh test của task: 10 passed in 0.89s; toàn bộ tăng đúng 10 py test so với main trước task (bảng "Sơ đồ đợt chạy"). Số đo trên bản chạy thử.

- [ ] **Step 5: Commit**

```bash
git add tests/test_api_cai_dat.py tests/test_san_sang.py tram/api/app.py tram/api/cai_dat.py tram/suy/cai_dat.py tram/suy/san_sang.py
git commit -m "feat(api): 2f GET /api/cai-dat, /api/san-sang"
```

### Task 7: Trường bổ sung cho API có sẵn — T1, T2, T4, T6

**Đợt:** 1 · **Độ khó:** vừa · **Phải xong trước:** 2d (T6, T7 sửa `doi_ngu.py`, `phe_duyet.py`), 2e (T1 sửa `van_phong.py`) · **Test mới:** 6 py

**Mockup bám:** `trang.js` `theKhe` ("Claude 1", "Đại ca tắt khe · “để dành”"), `vePheDuyet` (chip "Codex 1 hỏi · QC" + câu hỏi), `van-phong.js` (nhãn "Lỗi · cầu dao ngắt", tủ máy mỗi tủ một màu `SUC_KHOE`), `trang-tong-quan.js` (ô "codex-1 hỏi ở hr-3"); ảnh `anh-doi-ngu.png`, `anh-phe-duyet.png`, `anh-van-phong.png`. Khảo sát §1.10 bảng T1–T7.

**Files:**
- Create: `tram/suy/phe_duyet_bi.py` (`cau_hoi`, `nguon_escalation`, `gan_bi`)
- Modify: `tram/suy/doi_ngu.py` (T1), `tram/suy/nhan_vat.py` (T2), `tram/suy/phe_duyet.py` (1 import + 1 dòng gọi `gan_bi` trong `gom_phe_duyet`), `tram/suy/van_phong.py` (T6)
- Test: `tests/test_truong_2f.py` (mới); sửa tối thiểu `tests/test_suy_van_phong.py`, `tests/test_api_van_phong.py`, `tests/test_suy_nhan_vat.py` (ba test này so nguyên dict nên phải thêm khoá mới vào dict kỳ vọng — không đổi hành vi cũ)

**Interfaces:**
- Produces: các trường ở "Hợp đồng (lát 2f)" mục "Trường bổ sung". `ten` dùng chung `ten_nhan_vat` nên khớp tên nhân vật Văn phòng. `vi_sao_tat` = `lam_sach(vi_sao, 120)` của `khe.tat` mới nhất, chỉ khi `trang_thai == "tat"`. T4 suy `escalation.tao {escalation_id, bead_goc, giao_id}` → `giao.nhan` cùng `giao_id` → `khe_id`, `buoc` (đọc bằng `KhoSuKien.gan_day(..., du_lieu_co=)` — không sửa `kho.py`); `cau_hoi` bỏ các dòng máy `ly_do:`, `bead_goc:`, `giao_id:`, `<!-- ma_thao_tac: … -->` mà 4a-1 ghi quanh câu hỏi.
- Không sửa `tram/api/*.py`.

Ghi chú D41: khối diff `tram/suy/doi_ngu.py` dưới đây tính trên bản sau 2d Task 6 bản D41 (đã có `du_hang_khe`, `ds = trang_thai_khe(...)` trong `doi_ngu`); Task 7 chỉ thêm `ten`, `vi_sao_tat` và dùng lại `ds` để tính `ten_nhan_vat`, không đụng `bang_diem`.

Ghi chú: `pr_tram` chỉ có ở mục `cho-review` (2d T7); mục `co-do` không có — trang Phê duyệt (Task 11) coi `co-do` không có PR trạm.

- [ ] **Step 1: Viết test (chép nguyên văn)**

`tests/test_api_van_phong.py` (sửa):

```diff
diff --git a/tests/test_api_van_phong.py b/tests/test_api_van_phong.py
index 9bb0d9a..2b98667 100644
--- a/tests/test_api_van_phong.py
+++ b/tests/test_api_van_phong.py
@@ -33,7 +33,7 @@ def test_van_phong_phong_nhan_vat_va_badge(tmp_path):
     assert r.status == 200 and "unsafe-eval" not in r.headers["content-security-policy"]
     d = r.json()
     phong = {p["ma"]: p for p in d["phong"]}
-    assert phong["giam-doc"]["so_cho"] == 1 and phong["may-chu"]["suc_khoe"] == {"mau": "xanh", "ly_do": []}
+    assert phong["giam-doc"]["so_cho"] == 1 and phong["may-chu"]["suc_khoe"] == {"mau": "xanh", "ly_do": [], "muc": []}
     assert phong["dieu-phoi"]["sang"] is None and "du-an:hr-codex" in phong
     (nv,) = d["nhan_vat"]
     assert (nv["ten"], nv["hien_thi"], nv["phong"], nv["bead"]["bead_id"]) == ("Claude 1", "lam", "du-an:hr-codex", "hr-2")
@@ -47,4 +47,4 @@ def test_van_phong_khi_kho_phieu_tat_va_tram_loi(tmp_path, tram_home_tam):
     d = goi(_app(tmp_path, bds, kho_phieu=False), "GET", "/api/van-phong").json()
     assert d["kho_phieu"] is False and d["nhan_vat"] == []
     sk = {p["ma"]: p for p in d["phong"]}["may-chu"]["suc_khoe"]
-    assert sk == {"mau": "do", "ly_do": ["Estop đang bật", "Không đọc được beads của dự án tram"]}
+    assert (sk["mau"], sk["ly_do"]) == ("do", ["Estop đang bật", "Không đọc được beads của dự án tram"])
```

`tests/test_suy_nhan_vat.py` (sửa):

```diff
diff --git a/tests/test_suy_nhan_vat.py b/tests/test_suy_nhan_vat.py
index 90d12aa..79da90a 100644
--- a/tests/test_suy_nhan_vat.py
+++ b/tests/test_suy_nhan_vat.py
@@ -46,7 +46,7 @@ def test_phong_va_hien_thi_theo_trang_thai(tmp_path):
     dat_phieu(kho, "B/la", bead_id="x-1", du_an="da-go")
     nv = _nv(kho)
     assert nv["B/lam"] == {"khe_id": "B/lam", "ten": "Claude lam", "cli": "claude", "trang_thai": "lam",
-                           "hien_thi": "lam", "phong": "du-an:hr-codex",
+                           "hien_thi": "lam", "phong": "du-an:hr-codex", "cau_dao_ngat": False,
                            "bead": {"du_an": "hr-codex", "bead_id": "hr-1", "tieu_de": "Sửa giá", "buoc": "qc"}}
     assert (nv["B/ranh"]["phong"], nv["B/ranh"]["hien_thi"], nv["B/ranh"]["bead"]) == ("ca-phe", "ranh", None)
     assert (nv["B/tat"]["phong"], nv["B/tat"]["hien_thi"], nv["B/tat"]["bead"]) == ("du-an:hr-codex", "tat", None)
```

`tests/test_suy_van_phong.py` (sửa):

```diff
diff --git a/tests/test_suy_van_phong.py b/tests/test_suy_van_phong.py
index 43935e0..a0b2086 100644
--- a/tests/test_suy_van_phong.py
+++ b/tests/test_suy_van_phong.py
@@ -7,10 +7,10 @@ REVIEW = {"loai": "cho-review", "du_an": "hr-codex", "bead_id": "hr-1", "chi_tie
 
 
 def test_suc_khoe_xanh_vang_do():
-    assert suc_khoe(estop_bat=False, muc=[REVIEW], loi_doc={}, nhan_vat=[]) == {"mau": "xanh", "ly_do": []}
+    assert suc_khoe(estop_bat=False, muc=[REVIEW], loi_doc={}, nhan_vat=[]) == {"mau": "xanh", "ly_do": [], "muc": []}
     nv = [{"khe_id": "B/claude-1", "trang_thai": "mat_ket_noi"}, {"khe_id": "B/claude-3", "trang_thai": "lam"}]
-    assert suc_khoe(estop_bat=False, muc=[HE_DAO], loi_doc={}, nhan_vat=nv) == {
-        "mau": "vang", "ly_do": ["Cầu dao khe B/claude-2 đang ngắt", "Khe B/claude-1: mất kết nối"]}
+    v = suc_khoe(estop_bat=False, muc=[HE_DAO], loi_doc={}, nhan_vat=nv)
+    assert (v["mau"], v["ly_do"]) == ("vang", ["Cầu dao khe B/claude-2 đang ngắt", "Khe B/claude-1: mất kết nối"])
     r = suc_khoe(estop_bat=True, muc=[HE_QUET, HE_DAO], loi_doc={"tram": "bd lỗi <bí mật>"}, nhan_vat=[])
     assert r["mau"] == "do"
     assert r["ly_do"] == ["Estop đang bật", "Không đọc được beads của dự án tram", "hr-codex: lỗi quét beads",
```

`tests/test_truong_2f.py` (mới):

```python
"""Trường bổ sung lát 2f (khảo sát giao diện §1.10): T1 đội ngũ `ten`/`vi_sao_tat`, T2 `cau_dao_ngat`,
T4 phê duyệt `cau_hoi`/`khe_id`/`buoc`/`bead_goc`, T6 `suc_khoe.muc`. Chỉ THÊM khoá, khoá cũ giữ nguyên."""
from datetime import timedelta

from bead_gia import bead
from kho_phieu_gia import LUC, kho_tam
from tram.cau_hinh.tram import CauHinhTram
from tram.phieu.cau_dao import ngat_cau_dao
from tram.phieu.khe import bat_tat_khe, dang_ky_khe
from tram.phieu.nhip_tim import ghi_nhip
from tram.phieu.trang_thai import trang_thai_khe
from tram.su_kien.kho import KhoSuKien
from tram.suy.doi_ngu import doi_ngu
from tram.suy.nhan_vat import nhan_vat
from tram.suy.phe_duyet import gom_phe_duyet
from tram.suy.van_phong import GIU_TOI_DA, suc_khoe

CH = CauHinhTram()


def _khe(kho, *ten, cli="claude"):
    with kho.giao_dich():
        dang_ky_khe(kho, "B", [{"ten": t, "cli": cli, "ten_goi_nho": "x", "vai_uu_tien": ["coder"]} for t in ten],
                    luc=LUC)
        for t in ten:
            ghi_nhip(kho, f"B/{t}", luc=LUC, giao_id=None, luot=None, buoc_tho="ranh", han_muc=None)


def test_t1_doi_ngu_ten_nhan_vat_va_vi_sao_tat_chi_khi_tat(tmp_path):
    kho = kho_tam(tmp_path)
    _khe(kho, "claude-1", "claude-2", "claude-3")
    with kho.giao_dich():
        bat_tat_khe(kho, "B/claude-1", bat=False, vi_sao="Để dành ‮hạn mức " + "x" * 200, tac_nhan="dai-ca",
                    luc=LUC)
        bat_tat_khe(kho, "B/claude-2", bat=False, vi_sao="tạm nghỉ", tac_nhan="dai-ca", luc=LUC)
        bat_tat_khe(kho, "B/claude-2", bat=True, vi_sao="làm lại", tac_nhan="dai-ca", luc=LUC)
        bat_tat_khe(kho, "B/claude-3", bat=False, vi_sao="", tac_nhan="dai-ca", luc=LUC)
    k = {x["khe_id"]: x for x in doi_ngu(kho, bay_gio=LUC, ch=CH)["khe"]}
    assert [k[i]["ten"] for i in ("B/claude-1", "B/claude-2", "B/claude-3")] == ["Claude 1", "Claude 2", "Claude 3"]
    v = k["B/claude-1"]["vi_sao_tat"]
    assert k["B/claude-1"]["trang_thai"] == "tat" and v.startswith("Để dành hạn mức") and len(v) == 120
    assert (k["B/claude-2"]["trang_thai"], k["B/claude-2"]["vi_sao_tat"]) == ("ranh", None)
    assert (k["B/claude-3"]["trang_thai"], k["B/claude-3"]["vi_sao_tat"]) == ("tat", None)       # rỗng → None
    assert list(k["B/claude-1"])[-2:] == ["ten", "vi_sao_tat"]                                     # chỉ thêm ở cuối


def test_t2_nhan_vat_cau_dao_ngat(tmp_path):
    kho = kho_tam(tmp_path)
    _khe(kho, "claude-1", "claude-2")
    with kho.giao_dich():
        ngat_cau_dao(kho, "B/claude-2", ly_do="het-han-muc", toi_luc=LUC + timedelta(hours=1), luc=LUC)
    nv = {x["khe_id"]: x for x in nhan_vat(kho, trang_thai_khe(kho, bay_gio=LUC, ch=CH), ["hr-codex"])}
    assert nv["B/claude-1"]["cau_dao_ngat"] is False
    assert nv["B/claude-2"]["cau_dao_ngat"] is True and nv["B/claude-2"]["hien_thi"] == "loi"


def _ghi(kho, loai, bead_id, **d):
    kho.ghi("hr", loai, d, bead_id=bead_id, tac_nhan="tram/giao-viec")


def test_t4_escalation_co_cau_hoi_khe_buoc_bead_goc(tmp_path):
    kho = KhoSuKien(tmp_path / "sk.db")
    mo_ta = ("ly_do: qc-tra-ve\nbead_goc: hr-1\ngiao_id: G-1\n\nCần chọn ‮hướng " + "y" * 400
             + "\n\n<!-- ma_thao_tac: m -->")
    beads = [bead("hr-9", issue_type="decision", labels=["tram:escalation"], description=mo_ta), bead("hr-1")]
    _ghi(kho, "giao.nhan", "hr-1", giao_id="G-1", khe_id="B/claude-2", buoc="qc", vai="qc", ma_giao="bí-mật")
    _ghi(kho, "giao.nhan", "hr-1", giao_id="G-0", khe_id="B/claude-1", buoc="code", vai="coder")
    _ghi(kho, "escalation.tao", "hr-1", escalation_id="hr-9", bead_goc="hr-1", giao_id="G-1", ly_do="qc-tra-ve")
    (m,) = [x for x in gom_phe_duyet(["hr"], {"hr": beads}, kho) if x["loai"] == "escalation"]
    ct = m["chi_tiet"]
    assert (ct["khe_id"], ct["buoc"], ct["bead_goc"]) == ("B/claude-2", "qc", "hr-1")
    assert ct["cau_hoi"].startswith("Cần chọn hướng") and len(ct["cau_hoi"]) == 300
    assert "ma_thao_tac" not in ct["cau_hoi"]
    assert set(ct) == {"cau_hoi", "khe_id", "buoc", "bead_goc"} and "bí-mật" not in str(m)


def test_t4_escalation_khong_su_kien_thi_none_va_decision_chi_cau_hoi(tmp_path):
    kho = KhoSuKien(tmp_path / "sk.db")
    beads = [bead("hr-9", issue_type="decision", labels=["tram:escalation"], description="Hỏi gì?"),
             bead("hr-8", issue_type="decision", description="Chọn A hay B?"), bead("hr-7", issue_type="decision"),
             bead("hr-6", issue_type="decision", labels=["tram:escalation"], description="Không giao")]
    _ghi(kho, "escalation.tao", "hr-1", escalation_id="hr-6", bead_goc="hr-1", giao_id=None, ly_do="khac")
    ct = {m["bead_id"]: m["chi_tiet"] for m in gom_phe_duyet(["hr"], {"hr": beads}, kho)}
    assert ct["hr-9"] == {"cau_hoi": "Hỏi gì?", "khe_id": None, "buoc": None, "bead_goc": None}
    assert ct["hr-6"] == {"cau_hoi": "Không giao", "khe_id": None, "buoc": None, "bead_goc": "hr-1"}
    assert ct["hr-8"] == {"cau_hoi": "Chọn A hay B?"} and ct["hr-7"] == {"cau_hoi": ""}


def test_t4_muc_khac_khong_them_khoa(tmp_path):
    kho = KhoSuKien(tmp_path / "sk.db")
    beads = [bead("hr-1", labels=["cot:cho-review"], description="mô tả"), bead("hr-2", labels=["cho-duyet-spec"])]
    for m in gom_phe_duyet(["hr"], {"hr": beads}, kho):
        assert not {"cau_hoi", "khe_id", "buoc", "bead_goc"} & set(m["chi_tiet"])


def test_t6_suc_khoe_muc_cung_thu_tu_va_cung_cat_voi_ly_do():
    he_dao = {"loai": "he", "du_an": "_tram", "bead_id": None,
              "chi_tiet": {"su_kien": "khe.cau_dao_ngat", "khe_id": "B/claude-2"}}
    nv = [{"khe_id": "B/claude-1", "trang_thai": "loi"}]
    r = suc_khoe(estop_bat=True, muc=[he_dao], loi_doc={}, nhan_vat=nv)
    assert r["muc"] == [{"mau": "do", "ly_do": "Estop đang bật"},
                        {"mau": "vang", "ly_do": "Cầu dao khe B/claude-2 đang ngắt"},
                        {"mau": "vang", "ly_do": "Khe B/claude-1: lỗi lần chạy cuối"}]
    assert list(r) == ["mau", "ly_do", "muc"] and r["mau"] == "do"
    r = suc_khoe(estop_bat=True, muc=[he_dao], loi_doc={f"da-{i}": "x" for i in range(GIU_TOI_DA)}, nhan_vat=nv)
    assert len(r["muc"]) == len(r["ly_do"]) == GIU_TOI_DA and [x["ly_do"] for x in r["muc"]] == r["ly_do"]
    assert {x["mau"] for x in r["muc"]} == {"do"}
    assert suc_khoe(estop_bat=False, muc=[], loi_doc={}, nhan_vat=[]) == {"mau": "xanh", "ly_do": [], "muc": []}
```

- [ ] **Step 2: Chạy thấy FAIL**

```bash
uv run --offline pytest -q tests/test_api_van_phong.py tests/test_suy_nhan_vat.py tests/test_suy_van_phong.py tests/test_truong_2f.py
```

Kỳ vọng: FAIL — `AssertionError: assert (1 == 1 and {'ly_do': [], 'mau': 'xanh'} == {'ly_do': [],...h', 'muc': []}`

- [ ] **Step 3: Viết mã (chép nguyên văn; file sửa: chép khối diff ra file tạm, `git apply --check` rồi `git apply`)**

`tram/suy/doi_ngu.py` (sửa):

```diff
diff --git a/tram/suy/doi_ngu.py b/tram/suy/doi_ngu.py
index 55d4996..951fe0f 100644
--- a/tram/suy/doi_ngu.py
+++ b/tram/suy/doi_ngu.py
@@ -6,12 +6,13 @@ from datetime import datetime, timedelta
 from tram.cau_hinh.tram import CauHinhHanMuc, CauHinhTram
 from tram.han_muc.luat import cham_nguong_ngung, duoc_nhan
 from tram.han_muc.mo_hinh import HanMuc, co_chua_biet
-from tram.phieu.khe import phien_ban_khe
+from tram.phieu.khe import phien_ban_khe, su_kien_khe
 from tram.phieu.kho import KhoPhieu, chuoi_gio
 from tram.phieu.mo_hinh import VAI_CUA_BUOC
 from tram.phieu.trang_thai import TrangThaiKhe, trang_thai_khe
 from tram.suy.bang_diem import bang_diem
 from tram.suy.lam_sach import lam_sach
+from tram.suy.nhan_vat import ten_nhan_vat
 
 SO_NGAY_BANG_DIEM = 30                    # D14: mặc định bảng điểm = 30 ngày gần nhất, mọi dự án
 LUAT_VAI = (
@@ -38,7 +39,13 @@ def _ten(tt: TrangThaiKhe) -> str:
     return tt.khe_id if not ten or "@" in ten else ten
 
 
-def the_khe(kho: KhoPhieu, tt: TrangThaiKhe, ch: CauHinhTram) -> dict:
+def vi_sao_tat(kho: KhoPhieu, tt: TrangThaiKhe) -> str | None:
+    """2f T1: lý do của `khe.tat` mới nhất, chỉ khi khe đang `tat`; rỗng → None."""
+    x = su_kien_khe(kho, tt.khe_id, ("khe.bat", "khe.tat")) if tt.trang_thai == "tat" else None
+    return (lam_sach(x[2].get("vi_sao"), 120) or None) if x and x[1] == "khe.tat" else None
+
+
+def the_khe(kho: KhoPhieu, tt: TrangThaiKhe, ch: CauHinhTram, ten: str | None = None) -> dict:
     # Danh sách cho phép, không serialize cả phiếu nếu upstream thêm credential.
     phieu = None if tt.phieu is None else {
         **{k: tt.phieu[k] for k in ("giao_id", "du_an", "bead_id", "buoc", "vai") if k in tt.phieu},
@@ -47,7 +54,9 @@ def the_khe(kho: KhoPhieu, tt: TrangThaiKhe, ch: CauHinhTram) -> dict:
             "vai_uu_tien": list(tt.vai_uu_tien), "trang_thai": tt.trang_thai, "phieu": phieu,
             "han_muc": tt.han_muc, "muc_han_muc": muc_han_muc(HanMuc.model_validate(tt.han_muc), ch.han_muc),
             "cau_dao": tt.cau_dao, "so_phien": tt.so_phien, "nhip_cuoi": tt.nhip_cuoi,
-            "phien_ban": phien_ban_khe(kho, tt.khe_id)}
+            "phien_ban": phien_ban_khe(kho, tt.khe_id),
+            # 2f T1: tên nhân vật dùng chung với Văn phòng ("Claude 1"); `ten` None → tính riêng cho khe này
+            "ten": ten or ten_nhan_vat([(tt.khe_id, tt.cli)])[tt.khe_id], "vi_sao_tat": vi_sao_tat(kho, tt)}
 
 
 def du_hang_khe(hang: list[dict], ds: list[TrangThaiKhe]) -> list[dict]:
@@ -70,6 +79,7 @@ def doi_ngu(kho: KhoPhieu, *, bay_gio: datetime, ch: CauHinhTram, du_an: str | N
     không làm mất hàng của khe đã khai (D41)."""
     tu = chuoi_gio(bay_gio - timedelta(days=so_ngay))
     ds = trang_thai_khe(kho, bay_gio=bay_gio, ch=ch)
-    return {"bat": True, "khe": [the_khe(kho, tt, ch) for tt in ds],
+    ten = ten_nhan_vat([(tt.khe_id, tt.cli) for tt in ds])
+    return {"bat": True, "khe": [the_khe(kho, tt, ch, ten[tt.khe_id]) for tt in ds],
             "luat_vai": {"vai_cua_buoc": dict(VAI_CUA_BUOC), "luat": list(LUAT_VAI)},
             "bang_diem": du_hang_khe(bang_diem(kho.db, du_an=du_an, tu=tu), ds)}
```

`tram/suy/nhan_vat.py` (sửa):

```diff
diff --git a/tram/suy/nhan_vat.py b/tram/suy/nhan_vat.py
index 2ec2446..cb53125 100644
--- a/tram/suy/nhan_vat.py
+++ b/tram/suy/nhan_vat.py
@@ -64,7 +64,8 @@ def _mot(kho: KhoPhieu, tt: TrangThaiKhe, ten: str, cac_du_an: list[str]) -> dic
     noi = bead or (cuoi if trang_thai != "ranh" else None)
     phong = ma_phong_du_an(noi["du_an"]) if noi and noi["du_an"] in cac_du_an else CA_PHE
     return {"khe_id": tt.khe_id, "ten": ten, "cli": lam_sach(tt.cli, 32), "trang_thai": trang_thai,
-            "hien_thi": HIEN_THI.get(trang_thai, "tat"), "phong": phong, "bead": bead}
+            "hien_thi": HIEN_THI.get(trang_thai, "tat"), "phong": phong, "bead": bead,
+            "cau_dao_ngat": bool(tt.cau_dao.get("ngat"))}        # 2f T2: nhãn "Lỗi · cầu dao ngắt"
 
 
 def nhan_vat(kho: KhoPhieu, ds: list[TrangThaiKhe], cac_du_an: list[str]) -> list[dict]:
```

`tram/suy/phe_duyet.py` (sửa):

```diff
diff --git a/tram/suy/phe_duyet.py b/tram/suy/phe_duyet.py
index a7372d1..4260221 100644
--- a/tram/suy/phe_duyet.py
+++ b/tram/suy/phe_duyet.py
@@ -4,6 +4,7 @@ from tram.beads.mo_hinh import Bead
 from tram.suy.chi_tiet import ban_giao_sach
 from tram.suy.cot import NHAN_CO_DO, NHAN_ESCALATION, TRANG_THAI_HIEN
 from tram.suy.lam_sach import lam_sach
+from tram.suy.phe_duyet_bi import gan_bi
 from tram.suy.phe_duyet_spec import bo_sung_spec
 from tram.suy.pr_tram import pr_tram
 
@@ -97,7 +98,7 @@ def gom_phe_duyet(cac_du_an: list[str], theo_du_an: dict[str, list[Bead]], kho,
     ra = list(them)
     for du_an in cac_du_an:
         beads = theo_du_an.get(du_an, [])
-        muc = gan_pr_tram(du_an, muc_tu_beads(du_an, beads), kho)
+        muc = gan_bi(du_an, gan_pr_tram(du_an, muc_tu_beads(du_an, beads), kho), kho, {b.id: b for b in beads})  # 2f T4
         ra += bo_sung_spec(du_an, muc, beads, kho) + muc_he(du_an, kho, {b.id: b for b in beads})
     return sorted(ra, key=lambda m: (THU_TU.index(m["loai"]), 9 if m["uu_tien"] is None else m["uu_tien"],
                                      m["updated_at"] or "", m["du_an"], m["bead_id"] or ""))
```

`tram/suy/phe_duyet_bi.py` (mới):

```python
"""Trang Phê duyệt — thẻ "Bí / cần quyết định" (lát 2f T4, khảo sát giao diện §1.10): mục `escalation` và
`decision` mang `chi_tiet.cau_hoi` (mô tả bead, ≤ 300); mục `escalation` thêm `khe_id`, `buoc`, `bead_goc` suy từ
`escalation.tao {escalation_id, bead_goc, giao_id}` (4a-1) rồi `giao.nhan` cùng `giao_id` (phần 3). Danh sách cho
phép — không trả thêm trường nào của sự kiện (`giao.nhan` không có `ma_giao`, nhưng vẫn không serialize cả khối)."""
from tram.beads.mo_hinh import Bead
from tram.suy.lam_sach import lam_sach

LOAI_CO_CAU_HOI = ("escalation", "decision")
DAU_MAY = ("ly_do: ", "bead_goc: ", "giao_id: ", "<!-- ma_thao_tac: ")   # dòng máy của escalation 4a-1 (mo_ta)


def cau_hoi(mo_ta: str) -> str:
    """Bỏ các dòng máy (`ly_do:`, `bead_goc:`, `giao_id:`, mốc `ma_thao_tac`) trạm ghi quanh câu hỏi."""
    dong = [d for d in (mo_ta or "").splitlines() if not d.startswith(DAU_MAY)]
    return lam_sach("\n".join(dong).strip(), 300)


def _chuoi(x) -> str | None:
    return lam_sach(x, 64) or None


def nguon_escalation(du_an: str, escalation_id: str, kho) -> dict:
    """`{khe_id, buoc, bead_goc}` — thiếu sự kiện thì None (escalation tạo tay, hoặc không gắn phiếu)."""
    ra = {"khe_id": None, "buoc": None, "bead_goc": None}
    tao = kho.gan_day(du_an, "escalation.tao", 1, du_lieu_co={"escalation_id": escalation_id})
    if not tao:
        return ra
    ra["bead_goc"] = _chuoi(tao[0].du_lieu.get("bead_goc"))
    giao_id = tao[0].du_lieu.get("giao_id")
    nhan = kho.gan_day(du_an, "giao.nhan", 1, du_lieu_co={"giao_id": giao_id}) if isinstance(giao_id, str) else []
    if nhan:
        ra["khe_id"], ra["buoc"] = _chuoi(nhan[0].du_lieu.get("khe_id")), _chuoi(nhan[0].du_lieu.get("buoc"))
    return ra


def gan_bi(du_an: str, muc: list[dict], kho, theo_id: dict[str, Bead]) -> list[dict]:
    """Như `gan_pr_tram` (2d): trả danh sách mới, chỉ THÊM khoá vào `chi_tiet` của mục escalation / decision."""
    ra = []
    for m in muc:
        if m["loai"] in LOAI_CO_CAU_HOI:
            b = theo_id.get(m["bead_id"])
            them = {"cau_hoi": cau_hoi(b.description if b else "")}
            if m["loai"] == "escalation":
                them |= nguon_escalation(du_an, m["bead_id"], kho)
            m = {**m, "chi_tiet": {**m["chi_tiet"], **them}}
        ra.append(m)
    return ra
```

`tram/suy/van_phong.py` (sửa):

```diff
diff --git a/tram/suy/van_phong.py b/tram/suy/van_phong.py
index 9422b09..84ae8d7 100644
--- a/tram/suy/van_phong.py
+++ b/tram/suy/van_phong.py
@@ -26,7 +26,8 @@ def suc_khoe(*, estop_bat: bool, muc: list[dict], loi_doc: dict[str, str], nhan_
             do.append(f"{m['du_an']}: {TEN_HE.get(sk, sk)}" + (f" ({m['bead_id']})" if m.get("bead_id") else ""))
     vang += [f"Khe {x['khe_id']}: {TEN_KHE[x['trang_thai']]}" for x in nhan_vat if x["trang_thai"] in TEN_KHE]
     mau = "do" if do else "vang" if vang else "xanh"
-    return {"mau": mau, "ly_do": (do + vang)[:GIU_TOI_DA]}
+    tu = ([{"mau": "do", "ly_do": x} for x in do] + [{"mau": "vang", "ly_do": x} for x in vang])[:GIU_TOI_DA]
+    return {"mau": mau, "ly_do": (do + vang)[:GIU_TOI_DA], "muc": tu}       # 2f T6: tủ thứ i lấy màu muc[i]
 
 
 def cac_phong(cac_du_an: list[str], *, so_cho: int, suc_khoe: dict, dieu_phoi: dict | None = None) -> list[dict]:
```

- [ ] **Step 4: Chạy thấy PASS**

```bash
uv run --offline pytest -q tests/test_api_van_phong.py tests/test_suy_nhan_vat.py tests/test_suy_van_phong.py tests/test_truong_2f.py
uv run --offline pytest -q
```

Kỳ vọng: PASS — lệnh test của task: 13 passed in 0.90s; toàn bộ tăng đúng 6 py test so với main trước task (bảng "Sơ đồ đợt chạy"). Số đo trên bản chạy thử.

- [ ] **Step 5: Commit**

```bash
git add tests/test_api_van_phong.py tests/test_suy_nhan_vat.py tests/test_suy_van_phong.py tests/test_truong_2f.py tram/suy/doi_ngu.py tram/suy/nhan_vat.py tram/suy/phe_duyet.py tram/suy/phe_duyet_bi.py tram/suy/van_phong.py
git commit -m "feat(api): 2f trường bổ sung T1 T2 T4 T6"
```

### Task 8: API Tổng quan — `GET /api/tong-quan`, `GET /api/su-kien/gan-day`

**Đợt:** 2 · **Độ khó:** dễ · **Phải xong trước:** Task 4 (`doc_he_thong`), Task 5 (`gan_day`) · **Test mới:** 2 py

**Mockup bám:** `trang-tong-quan.js` (sáu khối và dữ liệu cần), `du-lieu.js` (`DICH_VU`, `TRAM`, `VIEC_MOI_XONG`, `USAGE_HOM_NAY`, `SU_KIEN`), ảnh `anh-tong-quan.png`. Khảo sát §1.1, A3, A4.

**Files:**
- Create: `tram/api/tong_quan.py`, `tram/suy/moi_xong.py`
- Modify: `tram/api/app.py` (một import + một dòng `CAC_TUYEN += (tong_quan.router,)` — G28)
- Test: `tests/test_api_tong_quan.py` (mới)

**Interfaces:**
- Consumes: `phe_duyet(request)`, `du_an(request)` (`tram/api/tuyen_doc.py` — không sửa; có `bat_ghi` khi 1a-2 ghép), `r_doi_ngu(request, du_an="", so_ngay=30)`, `doc_dong_usage`, `tong_hop`, `he_thong.doc_he_thong().dich_vu()` (Task 4), `gan_day` (Task 5), `estop.dang_bat()`, `la_dai_ca_yeu_cau`.
- Produces: JSON ở "Hợp đồng (lát 2f)". Task 13 (trang Tổng quan) đọc.

Ghi chú: usage hôm nay dựng thẳng bằng `doc_dong_usage` + `tong_hop` (như `r_usage`) để không gọi ccusage mỗi 5 giây. `dich_vu` chỉ boolean (G24). Lỗi đọc beads một dự án đã nằm ở `loi_doc` (từ `du_an`) — `moi_xong` khi đó là `null`.

- [ ] **Step 1: Viết test (chép nguyên văn)**

`tests/test_api_tong_quan.py` (mới):

```python
"""Lát 2f (D17, D38 Q12): GET /api/tong-quan gom các route có sẵn; GET /api/su-kien/gan-day. Chỉ đọc."""
from dataclasses import replace

import pytest

from api_gia import DAI_CA, tao_pt
from asgi_gia import goi
from bd_gia import BdGia
from bead_gia import bead
from kho_phieu_gia import LUC, dat_phieu
from tram.api.app import tao_app
from tram.phieu.khe import dang_ky_khe
from tram.phieu.kho import KhoPhieu
from tram.suy import he_thong

BDS = {"hr": BdGia([bead("hr-1", labels=["cot:cho-review"]), bead("hr-2", labels=["cot:can-chot"]),
                    bead("hr-5", title="Sửa ngày", status="closed", closed_at="2026-10-13T02:00:00Z"),
                    bead("hr-4", status="closed", closed_at="2026-10-12T02:00:00Z")])}


@pytest.fixture
def app(tmp_path, monkeypatch):
    def chay(argv):
        return (0, "state = running\nPATH=/bi/mat") if argv[0] == "launchctl" else (44, "")
    monkeypatch.setattr(he_thong, "_CHUNG", he_thong.DocHeThong(chay=chay, home=tmp_path, uid=501))
    db = tmp_path / "sk.db"
    kho = KhoPhieu(db)
    with kho.giao_dich():
        dang_ky_khe(kho, "B", [{"ten": "claude-1", "cli": "claude", "ten_goi_nho": "a@b.vn", "vai_uu_tien": ["coder"]}],
                    luc=LUC)
    dat_phieu(kho, "B/claude-1", bead_id="hr-2", tieu_de="Sửa thuế")
    kho.close()
    pt = replace(tao_pt(tmp_path, BDS), mo_kho_phieu=lambda: KhoPhieu(db), dong_ho=lambda: LUC)
    pt.mo_kho().ghi("hr", "giao.nhan", {"khe_id": "B/claude-1", "buoc": "code"}, bead_id="hr-2", tac_nhan="tram/api")
    return tao_app(pt)


def test_tong_quan_gom_du_lieu_cac_trang(app):
    r = goi(app, "GET", "/api/tong-quan")
    assert r.status == 200 and "unsafe-eval" not in r.headers["content-security-policy"]
    d = r.json()
    assert set(d) == {"phe_duyet", "du_an", "tram", "doi_ngu", "usage", "dich_vu", "su_kien", "doc_luc"}
    assert d["phe_duyet"]["so"] == len(d["phe_duyet"]["muc"]) == 1
    (da,) = d["du_an"]
    assert da["so_bead"]["can-chot"] == 1 and da["moi_xong"] == {"id": "hr-5", "tieu_de": "Sửa ngày",
                                                                 "luc": "2026-10-13T02:00:00Z"}
    assert d["tram"] == {"estop": False, "la_dai_ca": False}
    assert d["doi_ngu"]["bat"] is True and [k["khe_id"] for k in d["doi_ngu"]["khe"]] == ["B/claude-1"]
    assert set(d["doi_ngu"]) == {"bat", "khe"} and set(d["usage"]) == {"theo_nguon", "theo_ngay"}
    assert d["dich_vu"][0] == {"nhan": "vn.tram.api", "viec": "dashboard + API", "da_cai": False, "dang_chay": True}
    assert d["su_kien"][0]["mo_ta"] == "→ B/claude-1 · code"
    assert "/bi/mat" not in r.body.decode() and "a@b.vn" not in r.body.decode()


def test_su_kien_gan_day_gioi_han_va_che_nho(app):
    r = goi(app, "GET", "/api/su-kien/gan-day?gioi_han=1")
    assert r.status == 200 and len(r.json()["su_kien"]) == 1
    assert goi(app, "GET", "/api/su-kien/gan-day?gioi_han=51").status == 422
    assert goi(app, "GET", "/api/su-kien/gan-day", headers={"Host": "la.example"}).status == 421
    assert goi(app, "GET", "/api/su-kien/gan-day", headers=DAI_CA).status == 200
```

- [ ] **Step 2: Chạy thấy FAIL**

```bash
uv run --offline pytest -q tests/test_api_tong_quan.py
```

Kỳ vọng: FAIL — `assert (404 == 200)`

- [ ] **Step 3: Viết mã (chép nguyên văn; file sửa: chép khối diff ra file tạm, `git apply --check` rồi `git apply`)**

`tram/api/app.py` (sửa):

```diff
diff --git a/tram/api/app.py b/tram/api/app.py
index 4d427e2..d64fabd 100644
--- a/tram/api/app.py
+++ b/tram/api/app.py
@@ -4,7 +4,7 @@ from fastapi.responses import JSONResponse
 from fastapi.staticfiles import StaticFiles
 
 from tram.api import doi_ngu, ghep, luong, noi_bo, tho, tho_them, tuyen_chu, tuyen_doc, tuyen_ghi, tuyen_nho, usage
-from tram.api import cai_dat, tuyen_feature, van_phong
+from tram.api import cai_dat, tong_quan, tuyen_feature, van_phong
 from tram.api.bao_mat import them_header_an_toan
 from tram.api.phu_thuoc import PhuThuocApi
 from tram.api.tuyen_giao import router as tuyen_giao
@@ -20,6 +20,7 @@ CAC_TUYEN = (tuyen_feature.router, tuyen_doc.router, tuyen_ghi.router, tuyen_chu
 CAC_TUYEN += (tuyen_giao,)                     # 4a-2: GET /api/giao-viec
 CAC_TUYEN += (van_phong.router,)               # 2c: GET /api/van-phong
 CAC_TUYEN += (cai_dat.router,)                 # 2f: GET /api/cai-dat, /api/san-sang (chỉ Đại ca)
+CAC_TUYEN += (tong_quan.router,)               # 2f: GET /api/tong-quan, /api/su-kien/gan-day
 
 
 def _xu_ly(ma: int):
```

`tram/api/tong_quan.py` (mới):

```python
"""Trang Tổng quan (D17, D38 Q12): `GET /api/tong-quan` gom dữ liệu bằng CHÍNH các hàm route có sẵn (như
`/api/van-phong` gọi `phe_duyet` — 2c G6), nên số trên Tổng quan luôn khớp từng trang; `GET /api/su-kien/gan-day`
(khảo sát A3). Công khai như `/api/phe-duyet`: dịch vụ launchd chỉ trả boolean (G24), sự kiện `nho.*` che mô tả
khi không phải Đại ca. Chỉ đọc — không gọi ccusage, không chạy lệnh có tác dụng phụ."""
from contextlib import closing

from fastapi import APIRouter, Request

from tram.api.bao_mat import la_dai_ca_yeu_cau
from tram.api.doi_ngu import r_doi_ngu
from tram.api.tuyen_doc import du_an, phe_duyet
from tram.beads.bd import LoiBd
from tram.cham_cot.ghi import GIO_VN
from tram.chu import estop
from tram.suy import he_thong
from tram.suy.moi_xong import moi_xong
from tram.suy.su_kien_gan_day import gan_day
from tram.thao_tac.loi import KhongHopLe
from tram.usage.su_kien import doc_dong_usage, tong_hop

router = APIRouter()
GIOI_HAN_TOI_DA = 50
SO_SU_KIEN = 18                                   # mockup: "18 dòng mới nhất"
TRUONG_DICH_VU = ("nhan", "viec", "da_cai", "dang_chay")


@router.get("/api/su-kien/gan-day")
def r_gan_day(request: Request, gioi_han: int = 20) -> dict:
    if not 1 <= gioi_han <= GIOI_HAN_TOI_DA:
        raise KhongHopLe(f"gioi_han phải trong 1–{GIOI_HAN_TOI_DA}")
    with closing(request.app.state.pt.mo_kho()) as kho:
        return {"su_kien": gan_day(kho, gioi_han, la_dai_ca=la_dai_ca_yeu_cau(request))}


def _moi_xong(pt, ten: str) -> dict | None:
    try:
        return moi_xong(pt.bo_dem.lay(ten))
    except LoiBd:                                 # lỗi đọc đã nằm ở `loi_doc` của dự án
        return None


def _usage_hom_nay(pt) -> dict:
    nay = pt.dong_ho().astimezone(GIO_VN).date()
    dong = []
    if pt.mo_kho_phieu is not None:
        with closing(pt.mo_kho_phieu()) as kho:
            dong = doc_dong_usage(kho.db, nay, nay)
    th = tong_hop(dong, pt.usage.gia)
    return {"theo_nguon": th["theo_nguon"], "theo_ngay": th["theo_ngay"]}


@router.get("/api/tong-quan")
def r_tong_quan(request: Request) -> dict:
    pt = request.app.state.pt
    dn = r_doi_ngu(request, du_an="", so_ngay=30)
    with closing(pt.mo_kho()) as kho:
        sk = gan_day(kho, SO_SU_KIEN, la_dai_ca=la_dai_ca_yeu_cau(request))
    return {"phe_duyet": phe_duyet(request),
            "du_an": [{**d, "moi_xong": _moi_xong(pt, d["ten"])} for d in du_an(request)["du_an"]],
            "tram": {"estop": estop.dang_bat(), "la_dai_ca": la_dai_ca_yeu_cau(request)},
            "doi_ngu": {"bat": dn["bat"], "khe": dn["khe"]}, "usage": _usage_hom_nay(pt),
            "dich_vu": [{k: d[k] for k in TRUONG_DICH_VU} for d in he_thong.doc_he_thong().dich_vu()],
            "su_kien": sk, "doc_luc": pt.dong_ho().isoformat()}
```

`tram/suy/moi_xong.py` (mới):

```python
"""Cột "Mới xong" của bảng "Theo dự án" ở Tổng quan (mockup trang-tong-quan.js `VIEC_MOI_XONG`): bead đã đóng có
`closed_at` lớn nhất trong bộ đệm beads (`bd list --all`). Chỉ mã, tiêu đề đã làm sạch, giờ."""
from tram.beads.mo_hinh import Bead
from tram.suy.lam_sach import lam_sach


def moi_xong(beads: list[Bead]) -> dict | None:
    xong = [b for b in beads if b.status == "closed" and b.closed_at]
    if not xong:
        return None
    b = max(xong, key=lambda x: x.closed_at)
    return {"id": b.id, "tieu_de": lam_sach(b.title, 200), "luc": b.closed_at}
```

- [ ] **Step 4: Chạy thấy PASS**

```bash
uv run --offline pytest -q tests/test_api_tong_quan.py
uv run --offline pytest -q
```

Kỳ vọng: PASS — lệnh test của task: 2 passed in 0.85s; toàn bộ tăng đúng 2 py test so với main trước task (bảng "Sơ đồ đợt chạy"). Số đo trên bản chạy thử.

- [ ] **Step 5: Commit**

```bash
git add tests/test_api_tong_quan.py tram/api/app.py tram/api/tong_quan.py tram/suy/moi_xong.py
git commit -m "feat(api): 2f GET /api/tong-quan, /api/su-kien/gan-day"
```

## Sơ đồ đợt chạy (cả lát 2f — hai file)

Số trong ngoặc là số chạy thật (bản D41, 16/10) trên bản dựng thử: `main` `503ff64` + plan 2d (bản D41) + plan 2e áp nguyên văn (N₀ = 2031, M₀ = 38), rồi áp plan 2f nguyên văn từ hai file plan (xem "Kết quả chạy thử"). Mỗi task một worktree từ `main` của đợt trước; không file nào bị hai task cùng đợt sửa.

```
Đợt 0 — 2d, 2e, 1a-2, 1b-4 đã ghép → đo N₀ (pytest), M₀ (node)

Đợt 1 — song song, 5 worktree
  T1 nền giao diện (fe) · T3 cổng an toàn (fe) · T4 đọc launchd/Keychain (py) · T5 mô tả sự kiện (py)
  T7 trường bổ sung T1/T2/T4/T6 (py)
  → pytest N₀ + 18 (2049) · node M₀ + 12 (50) · build + kiem-dist xanh

Đợt 2 — song song, 3 worktree
  T2 thành phần khe dùng chung (1) · T6 API cài đặt/sẵn sàng (4) · T8 API tổng quan (4, 5; app.py sau T6 — xem dưới)
  → pytest N₀ + 30 (2061) · node M₀ + 15 (53)

Đợt 3 — song song, 9 worktree (phần 2)
  T9 Công việc · T10 Đội ngũ AI · T11 Phê duyệt · T12 Văn phòng · T13 Tổng quan · T14 Cài đặt · T15 Dự án
  T16 Ký ức · T17 Usage   (mọi task: 1, 2)
  → pytest N₀ + 30 (2061) · node M₀ + 57 (95) · build + kiem-dist xanh

Đợt 4 — T18 kiểm trên trình duyệt dưới CSP thật + ghi chú triển khai (mọi task trước)
Chạy thật qua tailnet (máy A, điện thoại) — chờ 2a T26 (bs-6o0.11) như mọi phần dashboard
```

| Task | File plan | Đợt | Độ khó | Phải xong trước | Test mới | Toàn bộ sau task (trên `main` đợt trước) |
|---|---|---|---|---|---|---|
| 1 Nền giao diện | 1 | 1 | vừa | — | 7 node | node M₀ + 7 |
| 3 Cổng an toàn | 1 | 1 | dễ | — | 5 node | node M₀ + 5 |
| 4 Đọc launchd/Keychain | 1 | 1 | vừa | — | 7 py | N₀ + 7 |
| 5 Mô tả sự kiện | 1 | 1 | vừa | — | 5 py | N₀ + 5 |
| 7 Trường bổ sung | 1 | 1 | vừa | — | 6 py | N₀ + 6 |
| 2 Khe dùng chung | 1 | 2 | dễ | 1 | 3 node | node M₀ + 15 |
| 6 API cài đặt/sẵn sàng | 1 | 2 | vừa | 4 | 10 py | N₀ + 28 |
| 8 API tổng quan | 1 | 2 | dễ | 4, 5 | 2 py | N₀ + 20 |
| 9 Công việc | 2 | 3 | vừa | 1, 2 | 5 node | node M₀ + 20 |
| 10 Đội ngũ AI | 2 | 3 | vừa | 1, 2 | 4 node | node M₀ + 19 |
| 11 Phê duyệt | 2 | 3 | vừa | 1, 2 | 4 node | node M₀ + 19 |
| 12 Văn phòng | 2 | 3 | khó | 1, 2 | 6 node (net) | node M₀ + 21 |
| 13 Tổng quan | 2 | 3 | vừa | 1, 2 | 4 node | node M₀ + 19 |
| 14 Cài đặt | 2 | 3 | vừa | 1, 2 | 6 node | node M₀ + 21 |
| 15 Dự án | 2 | 3 | dễ | 1, 2 | 2 node | node M₀ + 17 |
| 16 Ký ức | 2 | 3 | vừa | 1, 2 | 5 node | node M₀ + 20 |
| 17 Usage | 2 | 3 | vừa | 1, 2 | 6 node | node M₀ + 21 |
| 18 Kiểm trình duyệt | 2 | 4 | vừa | 1–17 | — | — |

**Tổng cuối:** `uv run --offline pytest -q` = **N₀ + 30**; `npm run kiem` = **M₀ + 57**; `npm run build`, `npm run kiem-dist` xanh. Lát 2f có **18 task** (8 ở file này, 10 ở phần 2).

**Đụng chung:** `tram/api/app.py` do T6 và T8 cùng thêm một dòng (cùng đợt 2): ghép T6 trước, T8 sau — khối diff của T8 tính trên `app.py` đã có dòng của T6. Nếu chạy song song, người ghép giữ cả hai dòng `CAC_TUYEN +=`. `trang/TongQuan.vue`, `trang/CaiDat.vue` do T1 tạo (giữ chỗ) và T13, T14 thay toàn bộ (đợt sau). Không file nào khác bị hai task sửa. Không đụng file của 1a-2 (`tuyen_doc.py`, `phu_thuoc.py`, `tuyen_ghi.py`), 1b-4 (`tram/nho/*`), 3c (`tram/chu/cai_dat.py`, `tram/cau_hinh/giao_viec.py`).

## Để sau (không lập task ở lát này)

| Việc | Vì sao để sau |
|---|---|
| Chế độ tối | D38 bỏ ở 2f; cần mockup tối |
| Ô đèn Điều phối ở Tổng quan | Mockup Tổng quan chưa có (ranh giới 2e/2f) |
| Trang Phân luồng | D18 |
| Mẫu câu cho loại sự kiện thêm sau 2f | Loại lạ trả `mo_ta = ""`; lát thêm loại mới thêm mẫu vào `mau_su_kien.py` / `mau_nho.py` |
| `pmset`, file cấu hình ccusage trong bảng sẵn sàng | Khảo sát có nhắc; chưa cần cho các cổng hiện tại |
| Kiểm qua tailnet (máy A, điện thoại 375 px thật) | Chờ 2a T26 (bs-6o0.11), D6 |

## Kết quả chạy thử (16/10/2026)

**Bản D41 (chạy lại 16/10, sau khi sửa plan 2d Task 6, Task 7 và Task 10 của file này).** Bản sao `main` `503ff64` trong thư mục scratchpad riêng, `UV_OFFLINE=1`, `npm ci --offline --ignore-scripts`, không mạng:
1. Đo mốc `main`: **1994 passed**, node **33**. Áp **plan 2d** bản D41 (Task 1, 3, 4 → 2005; Task 6, 7, 5, 2 → **2009**, node **37**) và **plan 2e** (Task 1, 3, 4, 6, 2) nguyên văn → **N₀ = 2031 passed**, **M₀ = 38**, build + kiem-dist xanh.
2. Áp **plan 2f** nguyên văn từ hai file plan bằng cùng bộ trích khối, đúng thứ tự đợt, mỗi task Step 1 → FAIL → Step 3 → PASS → commit. Dòng FAIL của mọi task trùng chữ ghi ở Step 2 (Task 7: `AssertionError: assert (1 == 1 and {'ly_do': [], 'mau': 'xanh'} == …`; Task 10: `Error [ERR_MODULE_NOT_FOUND]: Cannot find module '…/frontend/src/luat_the_khe.js' …`, sau Step 3 `pass 4 · fail 0`).
   - Sau đợt 1: **2049 passed** (N₀ + 18), node **50** (M₀ + 12), build + kiem-dist xanh.
   - Sau đợt 2: **2061 passed** (N₀ + 30), node **53** (M₀ + 15).
   - Sau đợt 3 và đợt 4: **2061 passed**, node **95** (M₀ + 57), `kiem-an-toan` 135 file sạch, `npm run build` (gói chính `index-*.js` 202,8 kB, gzip 72,1 kB; `VanPhong-*.js` 878,5 kB), `npm run kiem-dist` xanh. Không còn `hangBangDiem` trong `frontend/`.
   - **Chưa** kiểm lại trên trình duyệt sau bản D41 (thay đổi giao diện chỉ là `DoiNgu.vue` đọc thẳng `bang_diem`); Task 18 kiểm trên `main` sau khi ghép.

**Bản trước D41 (giữ làm lịch sử).** Bản sao `main` `a3c10ee` (sau khi 1a-2, 1b-4 ghép **plan**; mã 1a-2/1b-4 chưa có) trong thư mục scratchpad riêng, `uv run --offline`, `npm ci --offline --ignore-scripts`:

1. Áp **plan 2d** (Task 1, 3, 4, 6, 7, 5, 2) và **plan 2e** (Task 1, 3, 4, 6, 2) nguyên văn từ hai file plan đó → **N₀ = 2030 passed**, **M₀ = 38** node, build + kiem-dist xanh (main trước 2d/2e: 1994 / 33).
2. Áp **plan 2f** nguyên văn từ hai file plan này bằng bộ trích khối (`` `path` (mới|sửa|thay toàn bộ): `` + khối mã; diff qua `git apply --check` rồi `git apply`), theo đúng thứ tự đợt, mỗi task: Step 1 → chạy test thấy FAIL (dòng lỗi ghi ở Step 2 của từng task là dòng thật) → Step 3 → chạy test thấy PASS → commit.
   - Sau đợt 1: **2048 passed** (N₀ + 18), node **50** (M₀ + 12), build + kiem-dist xanh.
   - Sau đợt 2: **2060 passed** (N₀ + 30), node **53** (M₀ + 15).
   - Sau đợt 3: **2060 passed**, node **96** (M₀ + 58), `npm run kiem` (kiem-an-toan mới: 135 file sạch), `npm run build`, `npm run kiem-dist` (2 JS + 2 CSS, không eval/inline/style tĩnh/font ngoài) xanh. Gói chính `index-*.js` 202,9 kB (gzip 72,2 kB; trước 2f 139,9 / 51,2 kB); chunk lười `VanPhong-*.js` 878,5 kB (gzip 237,9 kB).
   - Cây mã sau đợt 4 trùng khít nhánh tích hợp dùng để viết plan (`diff -r` rỗng trên `tram/`, `tests/`, `frontend/src`, `frontend/tests`, script kiểm).
3. **Kiểm trên trình duyệt** (trước khi chốt plan, dùng máy chủ của Task 18 ở cổng 7798, CSP thật): bắt được hai lỗi mà test/quét tĩnh không thấy, đã sửa ngay trong plan — (a) Vite nhúng font JetBrains Mono tiếng Việt (~3,9 kB) thành `data:font/woff2` → CSP `font-src 'self'` chặn: thêm `assetsInlineLimit: 0` (Task 1) và luật `font nhúng data:` trong `kiem-dist` (Task 3); (b) khối "Việc chờ" in `{}` khi `phe_duyet.loi` rỗng (Task 13). Sau khi sửa: Console không còn lỗi CSP; `document.fonts.check` đúng cả hai font; Văn phòng 17 nhãn, **0 chồng** ở 1024 và 375 px, không cuộn ngang; panel bấm nhân vật mở đúng; các trang so với ảnh mockup khớp bố cục (chỉnh thêm: mã khe/bead không xuống dòng ở bảng điểm và bảng sẵn sàng, câu cầu dao "Lý do … · tự đóng lúc hh:mm", cột hành động thẻ Phê duyệt gói dòng ở 1024 px, cuộn lên đầu khi đổi trang). Chưa kiểm được: chip "chỉ quét thử" (cần mã 1a-2), 1440 px đầy đủ mọi trang, chế độ không có danh tính (đã kiểm 403 bằng curl) — Task 18 làm lại đủ trên `main` sau khi ghép.
