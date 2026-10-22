# Lát TM-4 — giao diện tự merge / tự deploy: trang "Tự động", nút TẠM DỪNG toàn trạm, chip ở Dự án, dòng ở Phê duyệt — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: dùng `ai-skills:subagent-driven-development` (khuyến nghị) hoặc `ai-skills:executing-plans` để làm từng task. Step dùng checkbox (`- [ ]`). Hướng dẫn chung: `.handover/qc/huong-dan-code.md`. **Mọi dòng mã thêm vào phải có nguyên văn trong plan.** **Chưa được code** trước khi: Đại ca duyệt plan này, TM-1 → TM-2 → TM-3 đã ghép `main` (lát này dùng hợp đồng của cả ba).

**Trạng thái:** viết 18/10/2026 trong worktree `plan/tm-4-giao-dien`; **sửa vòng 2 (18/10, worktree `sua/tm4-v2`) theo Codex review gộp vòng 1** (`.handover/review-codex-plan/REVIEW-CODEX-tm-vong1.md`: áp + chạy thật sửa SSE của Codex, Q9, Q10, mục Nhỏ dữ liệu giả) và quyết định D127–D130 của Đại ca (D129: nút Deploy ngay ở dòng Phê duyệt) — mục "Phản hồi review Codex vòng 1" cuối plan. **Ghép sau TM-3** (thứ tự TM-1 → TM-2 → TM-3 → TM-4 → TC) — mục "Ghép trên lát trước". **Hunk gốc viết trên `0f88957`; đã kiểm lại trên nền TM-1 mới `nen/tm-1-ap-v2` @ `85ce7f4`** (plan TM-1 @ `874e7c4`). Khi triển khai, áp sau TM-3; các file TM-4 sửa không giao chữ với ba lát trước. Lần tiếp tục đã chạy RED→GREEN, dựng lại từ plan và kiểm frontend; **cửa kiểm cả bộ Python chưa đạt do lỗi nền thu hồi cây tiến trình trong môi trường này**. Kiểm trình duyệt của agent trước được ghi riêng là bằng chứng kế thừa — mục "Kiểm chứng plan". Cây cuối chỉ thay đổi file plan. CHƯA áp vào `main`.

**Goal:** Dựng phần giao diện của change `tu-merge-tu-deploy` theo mockup Đại ca đã duyệt (D101): trang "Tự động" của từng dự án `#/du-an/<ten>` (sẵn sàng deploy + nút Deploy, việc chờ Đại ca kèm lý do, lịch sử, bộ đếm hỏng liên tiếp, cài đặt: công tắc tự merge, hai điều kiện "luôn bật", ba nút điều kiện, dòng "cấu trúc DB — luôn chờ Đại ca", ba lệnh, tự deploy, lịch sử đổi), nút TẠM DỪNG dự án; nút TẠM DỪNG toàn trạm màu vàng trên thanh trên cạnh Estop kèm băng vàng trên mọi trang; hàng chip tự merge / tự deploy + link "Tự động →" trên thẻ ở trang Dự án; dòng "sẵn sàng deploy" ở Phê duyệt. Mọi nút ghi đi qua cửa ghi của TM-1 với mã thao tác; bật cần hỏi lại; kênh `header` (`chi_tam_dung`) chỉ cho TẠM DỪNG, mọi nút khác khoá kèm câu giải thích; không phải Đại ca thì chỉ xem.

**Architecture:** Chỉ giao diện (`frontend/`) + dữ liệu giả cho kiểm tay (`tests/`). Luật hiển thị thuần, test bằng `node --test`: `luat_tu_dong.js` (chung: lọc sự kiện SSE, nút TẠM DỪNG toàn trạm, câu khoá, chip), `luat_trang_tu_dong.js` (hằng điều kiện/lệnh, câu hỏi lại, thân POST, sẵn sàng deploy, chờ Đại ca), `luat_bao_tu_dong.js` (khối báo đầu trang), `luat_lich_su_tu_dong.js` (lịch sử, bộ đếm hỏng, lịch sử đổi). Trạng thái chung `kho.tuDong` (GET `/api/tu-dong`) nạp lúc mở khung và mỗi khi luồng SSE báo sự kiện `tu_dong.*`, `tu_merge.*`, `deploy.*`, `estop.*`. Trang `trang/TuDong.vue` + khối `thanh/tu_dong/*` đọc GET `/api/du-an/<ten>/tu-dong`, ghi qua `thanh/tu_dong/ghi_tu_dong.js` (một chỗ dựng mọi POST). Không đổi tuyến, không đổi mã Python của trạm.

**Tech Stack:** Vue 3.5.43, vue-router 5.4.0, Vite 8.3.4, `node --test`; pytest 8 cho dữ liệu giả. Không dependency mới.

**Spec / nguồn:** change [`openspec/changes/tu-merge-tu-deploy/`](../../openspec/changes/tu-merge-tu-deploy/) — `tasks.md` mốc **5.1, 5.2**; `specs/dieu-khien-tu-dong/spec.md` (Requirement: Trang tự merge/deploy của dự án · Bật công tắc cần xác nhận · Cửa ghi còn tạm thì chỉ cho TẠM DỪNG (phần dashboard) · TẠM DỪNG theo dự án · TẠM DỪNG toàn trạm (nút + băng) · Estop dừng cả hai (nút Deploy khoá "Estop đang bật") · Dự án khoá ghi (chip, công tắc khoá) · Màn hình cũ (409 giữ ô nhập)); `specs/tu-deploy/spec.md` (Ba lệnh — "Chưa khai đủ 3 lệnh"; Sẵn sàng deploy — hàng + dòng ở Phê duyệt; Nút Deploy — hỏi lại, 409; Một chuỗi một lúc — "gồm N việc đã merge"; Kết quả không rõ — "deploy không rõ kết quả — cần Đại ca kiểm"; Không lọt bí mật — chỉ mã thoát/thời gian); `specs/tu-merge/spec.md` "Thiếu điều kiện thì chờ Đại ca và nói rõ vì sao" (phần hiển thị); `design.md` D-5, D-10. Quyết định D78, D87, D97, D101, D127 (lịch sử có dòng "Deploy bị huỷ"), D128 (tắt công tắc có hỏi lại), D129 (dòng "sẵn sàng deploy" ở Phê duyệt CÓ nút Deploy — spec `tu-deploy` Scenario "Hiện ở trang Phê duyệt" đã sửa ở `main`), D130 (khối thiếu dữ liệu hiện "chưa có dữ liệu") (`docs/quyet-dinh/2026-10-18-tu-merge-tu-deploy.md`); câu trả lời của Đại ca cho plan TM-1 (18/10, ghi ở `.handover/qc/PLAN-TM-CHUNG.md`): câu 4 (dự án chỉ quét thử không Deploy tay), câu 5 (**không** vẽ khối "agent tự cập nhật việc"). Chia lát: [`2026-10-18-tm-0-chia-lat.md`](2026-10-18-tm-0-chia-lat.md); hợp đồng: mục "Interfaces cho lát sau" của [`2026-10-18-lat-tm-1-nen-cai-dat.md`](2026-10-18-lat-tm-1-nen-cai-dat.md).

**Mockup đã duyệt (D101) — bám đúng:** `docs/mockup/2026-10-18-tu-merge-tu-deploy/` — `trang-tu-dong.js`, `trang-du-an.js`, `app.js`, `index.html`, `them.css`, `du-lieu.js`; ảnh `anh-tu-dong.png`, `anh-tu-dong-sua-lenh.png`, `anh-tu-dong-tu-tat.png`, `anh-tu-dong-lui-hong.png`, `anh-tu-dong-cua-tam.png`, `anh-hr-codex-khoa.png`, `anh-du-an.png`, `anh-tam-dung-toan-tram.png`. Chỗ lệch có lý do: mục "Lệch mockup".

Mã thật đã đọc: `frontend/src/{api,kho,estop,tuyen,menu,luat,luat_du_an,luat_phe_duyet,dinh_dang,bieu_tuong}.js`, `frontend/src/{KhungChinh,main}.*`, `frontend/src/thanh/{ThanhTren,ThanhBen,BangEstop,DauTrang,HopKhe,BieuTuong}.vue`, `frontend/src/thanh/phe_duyet/{TheBi.vue,thao_tac.js}`, `frontend/src/trang/{DuAn,PheDuyet,NganBen}.vue`, `frontend/src/kieu/{nen,khung,chung,du-an,phe-duyet,cong-viec,cai-dat}.css`, `frontend/kiem-an-toan.mjs`, `frontend/tests/{kho,khung,du_an,phe_duyet,cai_dat}.test.mjs`; `tram/suy/tu_dong.py`, `tram/api/{tuyen_tu_dong,than,luong,tuyen_doc}.py`, `tram/tu_dong/{cai_dat,luu,khoa}.py`, `tram/suy/phe_duyet.py`, `tram/cau_hinh/bat_ghi.py`, `tram/api/phu_thuoc.py`, `tests/{du_lieu_giao_dien,chay_thu_giao_dien,test_api_tu_dong}.py`.

## Global Constraints

- **Kill list (`AGENT_RULES.md` §2): không chạm.** Lát này chỉ sửa `frontend/` (component Vue theo mockup đã duyệt — "Luôn BUILD ngay"), `tests/du_lieu_giao_dien.py`, `tests/chay_thu_giao_dien.py` (công cụ kiểm tay), một test pytest mới và `docs/DESIGN_SYSTEM.md`. Không sửa `tram/` (kiểm: `git diff 85ce7f4 -- tram | wc -l` = 0), không sửa `tram/api/bao_mat.py`, `kenh_ghi.py`, CSP. Khoá nút ở giao diện chỉ là tiện — quyền thật do máy chủ (TM-1) giữ: 403/422/409.
- **Phụ thuộc:** TM-1 đã ghép (tuyến `GET /api/tu-dong`, `GET /api/du-an/{ten}/tu-dong`, các POST tạm dừng / tiếp tục / cài đặt). Khoá TM-2 (`cho_dai_ca`) và TM-3 (`san_sang`, `dang_deploy`, `lich_su`, `dem_hong`, tuyến `POST …/tu-dong/deploy`, dòng `san-sang-deploy` ở `GET /api/phe-duyet`) **chưa có**: giao diện hiện "Chưa có dữ liệu — phần này của trạm chưa chạy." khi khoá thiếu (không đoán, DESIGN_SYSTEM "Nhãn trạng thái"); dữ liệu giả cho kiểm tay ở `tests/du_lieu_giao_dien.py` (Task 6), ghép vào phản hồi thật và **nhường khoá thật** khi TM-2/TM-3 ghép. Dạng khoá đề nghị: mục "Hợp đồng TM-4 cần từ TM-2 / TM-3".
- **Đo nền:** số lịch sử trên `0f88957`: Python 3412, frontend 102. Lần tiếp tục trên TM-1 mới `85ce7f4`: thu thập 3422 test Python; lần đo cả bộ bị lỗi nền thu hồi tiến trình (chi tiết Kiểm chứng), không có N₀ xanh mới. Frontend N₀ = 102 → sau lát 133 (+31); ba test dữ liệu giả xanh. Không lấy số thu thập hay số dự kiến thay số passed.
- Kiểm frontend sau mỗi task: `cd frontend && npm run kiem && npm run build && npm run kiem-dist`. Python BẮT BUỘC qua `tests/chan_host/chay.sh -q`; "0 dòng mới" trong nhật ký chặn là điều kiện xanh.
- Luật CSP (`DESIGN_SYSTEM.md`): không `style="…"` tĩnh, không `v-html`/`innerHTML`, không URL ngoài; câu có đoạn mono dựng bằng danh sách `[chữ, mono?]` và `<span v-for>` (không chèn HTML). Màu chỉ token (`nen.css` thêm `--xanh-bien`, `--vien-xanh-bien` cho khối "Sẵn sàng deploy" — mockup viết hex). Mỗi file mới ≤ ~120 dòng, dòng ≤ 120 ký tự (dài nhất trong file lát này tạo/sửa: `luat_phe_duyet.js` 104 dòng, `trang/TuDong.vue` 95).
- Nội dung bead (tiêu đề ở "Chờ Đại ca"), lệnh, lý do: chỉ hiện bằng `{{ }}`. Lệnh deploy hiện cho mọi người như TM-1 trả (rủi ro 2 của plan TM-1).
- Một task một commit trên nhánh task; không push, không merge, không `bd` ghi. Áp theo NỘI DUNG: `git apply --check` từng bản vá; không sạch thì DỪNG, báo điều phối.

## Bảng G — điều plan bảo đảm và bằng chứng

| # | Bảo đảm | Ở đâu | Bằng chứng offline |
|---|---|---|---|
| G1 | Nút TẠM DỪNG toàn trạm vàng ở thanh trên cạnh Estop, có trên mọi trang; bật hỏi lại, Tiếp tục một lần bấm; băng vàng khi bật; kênh `header` vẫn bấm được TẠM DỪNG, Tiếp tục khoá kèm câu; không phải Đại ca / chưa đọc được trạng thái → khoá | `luat_tu_dong.nutTamDungTram`, `tam_dung.js`, `ThanhTren`, `BangTamDung`, `KhungChinh` | `tu_dong_khung.test.mjs` "nút TẠM DỪNG toàn trạm…"; trình duyệt: bấm qua kênh `header` → băng hiện, Tiếp tục khoá (mục Kiểm chứng) |
| G2 | Trạng thái tự động theo kịp: sự kiện SSE `tu_dong.*`/`tu_merge.*`/`deploy.*`/`estop.*` → tải lại `/api/tu-dong`, số Phê duyệt, trang Tự động; đọc lỗi → `null` (khoá) | `kho.js` | `tu_dong_khung.test.mjs` "SSE: sự kiện tự động…" |
| G3 | Mục "Dự án" sáng ở `/du-an/<ten>` (mockup); tuyến `/du-an/:ten` có trong `tuyen.js` | `ThanhBen` (`mucCua`), `tuyen.js` | `tu_dong_khung.test.mjs` "đường /du-an/<ten>…", `tu_dong_ghi.test.mjs` "tuyến /du-an/:ten…" |
| G4 | Thẻ Dự án: tên → Công việc, chip tự merge/tự deploy (hoặc chỉ quét thử / estop / tạm dừng toàn trạm / tạm dừng), "1 sẵn sàng deploy", "tự deploy đã tự tắt", link "Tự động →" | `luat_du_an.theDuAn`, `luat_tu_dong.chipTuDong`, `DuAn.vue` | `du_an.test.mjs` "TM-4: thẻ dự án…", `tu_dong_khung.test.mjs` "chip tóm tắt…" |
| G5 | Khoá mọi nút ghi trừ TẠM DỪNG theo thứ tự: không phải Đại ca ("Chỉ đọc…") → kênh `header` ("Cửa ghi còn tạm — chỉ bấm được TẠM DỪNG") → `bat_ghi: false` (câu D37); TẠM DỪNG chỉ cần danh tính | `lyDoKhoaGhi`, `lyDoKhoaTamDung` | `tu_dong_khung.test.mjs` "khoá nút ghi…"; trình duyệt chế độ chỉ đọc: mọi nút ghi `disabled` |
| G6 | Hỏi lại trước khi gửi: bật tự merge, bật tự deploy (đúng câu spec), lưu 3 lệnh; tắt công tắc, tắt điều kiện, TẠM DỪNG cũng hỏi (như estop); bật lại điều kiện không hỏi; huỷ thì không gửi gì | `hoiCongTac`, `hoiTamDung`, `hoiDeploy`, `hoiLuuLenh`, `ghi_tu_dong.js` | `tu_dong_trang.test.mjs` "hỏi lại…", `tu_dong_ghi.test.mjs` "lưu cài đặt…" |
| G7 | POST đúng hợp đồng TM-1: thân cài đặt đủ khoá + `expected_version` = phiên bản lúc Đại ca bắt đầu sửa (công tắc: bản đang xem; ba lệnh: bản chụp lúc mở form — G17), `X-Tram`, mã thao tác mới mỗi lần; TẠM DỪNG/Tiếp tục không kiểm phiên bản; Deploy mang `expected_commit`; lưu lệnh thiếu khi tự deploy bật → gửi kèm tắt tự deploy (mockup) | `thanCaiDat`, `doiCongTac`, `doiLenh`, `ghi_tu_dong.js` | `tu_dong_trang.test.mjs` "thân POST…", `tu_dong_ghi.test.mjs` (3 test) |
| G8 | Lỗi 422/403 (và 409 của Deploy) hiện tại chỗ bằng câu của máy chủ (`role="alert"`); 409 của cài đặt hiện "Cài đặt đã đổi — tải lại" + nút "Tải lại"; không tự tải lại, giữ ô nhập ba lệnh | `ghi_tu_dong.js`, `KhoiCaiDat` | `tu_dong_ghi.test.mjs` "409 / 422 / 403…" |
| G9 | Khối báo đầu trang theo mockup: chỉ quét thử (đoạn mono), cửa tạm, estop (đỏ), tạm dừng do Đại ca / LÙI HỎNG (đỏ, "Tiếp tục dự án") / không rõ kết quả (đỏ), trạm tự tắt tự deploy (giờ lấy từ lịch sử đổi) | `luat_bao_tu_dong.baoTuDong` | `tu_dong_trang.test.mjs` "khối báo…" |
| G10 | Sẵn sàng deploy: một hàng cho commit mới nhất "gồm N việc đã merge", bản đang chạy, hàng "đang deploy"; nút Deploy khoá estop → thiếu lệnh → đang deploy → khoá ghi; **tạm dừng không khoá** (D97) | `sanSang`, `lyDoKhoaDeploy`, `KhoiSanSang` | `tu_dong_trang.test.mjs` "sẵn sàng deploy…" |
| G11 | Chờ Đại ca: lý do là câu của máy chủ (`nhan`); màu theo `muc` của máy chủ — `loi` đỏ (cấu trúc DB `schema_duong_dan`/`schema_tu_khoa`, `diff_loi`, `tu_merge_loi`), `tat` xám (`ci_dang_chay`), còn lại "cần người"; khoá thiếu → "Chưa có dữ liệu" | `choDaiCa`, `KhoiChoDaiCa` | `tu_dong_trang.test.mjs` "chờ Đại ca…" |
| G12 | Lịch sử: nhãn/màu theo mockup (+ "Không rõ kết quả", "Deploy bị huỷ"), giờ VN, commit 7 ký tự, "Ai" bằng lời; bộ đếm 3 đèn; lịch sử đổi: ai, giờ, việc, trước → sau (lệnh rút gọn, "trống") | `luat_lich_su_tu_dong.js`, `KhoiLichSu`, `NganLichSuDoi` | `tu_dong_lich_su.test.mjs` (4 test) |
| G13 | Phê duyệt: nhóm "Sẵn sàng deploy" (cuối), mỗi dự án một thẻ có **nút Deploy (D129)** — cùng hộp hỏi, cùng thân `{ma_thao_tac, expected_version: "", expected_commit}`, cùng xử lý 409/422 (hàm ghi chung `ghi_tu_dong.js`), cùng khoá (estop → thiếu lệnh → không phải Đại ca / kênh `header` / `bat_ghi: false`; chưa đọc được trạng thái → khoá) — và link "Mở trang Tự động"; số đếm do máy chủ (TM-3) | `luat.js`, `sanSangDeploy`, `khoaDeploy`, `TheSanSang` | `phe_duyet.test.mjs` "TM-4: dòng…", "TM-4 D129…"; trình duyệt kênh `header`: Deploy khoá "Cửa ghi đang khoá" |
| G14 | Dữ liệu giả: cài đặt THẬT qua hàm TM-1; khoá TM-2/TM-3 giả không đè khoá thật; dòng giả ở Phê duyệt **không nối khi đã có hàng thật** (dự án có hàng thật, hoặc trạm đã có TM-3); cờ xem `--gia-deploy` thay (không trùng) | `du_lieu_giao_dien.gieo_tu_dong`, `them_gia`, `them_phe_duyet_gia` | `test_du_lieu_giao_dien_tu_dong.py` (3 test) |
| G15 | CSP: không HTML thô, style tĩnh, URL ngoài; bundle sạch; console không lỗi CSP trên trình duyệt | — | `npm run kiem` (`kiem-an-toan: 153 file`), `npm run kiem-dist`, mục Kiểm chứng |
| G16 | Ghép không đổi hành vi trang khác; không sửa `tram/` | — | frontend `133 pass`; số Python hiện hành xem mục Kiểm chứng, `git diff 85ce7f4 -- tram` rỗng |
| G17 | (Codex Q9) Form "Sửa 3 lệnh" chụp `{du_an, phien_ban, cai_dat}` lúc MỞ, gửi đúng bản chụp đó; SSE tải lại trang chen giữa không đổi phiên bản gửi đi; 409 → giữ nháp, "Cài đặt đã đổi — tải lại", nút "Tải lại" lấy bản mới làm gốc, nháp còn, cạnh ô hiện "Đang lưu ở trạm: …" để đối chiếu | `sua_lenh.js`, `ghi_tu_dong.luu(doi, hoi, ban)`, `KhoiCaiDat` | `tu_dong_ghi.test.mjs` "Q9…", `tu_dong_dong_bo.test.mjs` "Q9: SSE chen giữa…" |
| G18 | (Codex Q10) Trang Tự động ràng dữ liệu và thao tác với tên dự án của route: phản hồi cũ (thế hệ trước) bị bỏ; đổi dự án → xoá dữ liệu cũ ngay, tải B lỗi không còn dữ liệu A; mọi POST dùng tên của route, dữ liệu của dự án khác thì không gửi cài đặt; kết quả về muộn không ghi lỗi lên trang mới; khối Cài đặt/Sẵn sàng dựng lại theo `:key` (form về trống); `kho.taiTuDong` cũng bỏ phản hồi cũ | `tai_du_an.js`, `ghi_tu_dong.js` (`layTen`), `TuDong.vue`, `kho.js` | `tu_dong_dong_bo.test.mjs` (4 test Q10), `tu_dong_ghi.test.mjs` "Q10…", `tu_dong_khung.test.mjs` "tải /api/tu-dong dồn…"; trình duyệt: đang sửa lệnh ở `tram` → sang `ke-toan` → form đóng, dữ liệu `ke-toan` |

## Thiết kế — bốn chỗ chọn

1. **Khoá TM-2/TM-3 chưa có thì nói thật "chưa có dữ liệu".** TM-4 ghép sau TM-3 theo thứ tự bắt buộc TM-1 → TM-2 → TM-3 → TM-4 → TC. Mỗi khoá được đọc riêng (`dl.cho_dai_ca === undefined` khác `[]`; `san_sang === undefined` khác `null`) — không hiện số giả, không ẩn khối spec đòi có. Không tự suy trạng thái từ sự kiện; thiếu khoá phải hiện chữ đúng D130, kể cả khi ghép tuần tự.
2. **Một chỗ dựng mọi POST (`ghi_tu_dong.js`)**, mỗi khối có bản riêng để lỗi hiện ngay tại khối đó (DESIGN_SYSTEM "Phản hồi sau khi ghi"); nút Deploy ở Phê duyệt (D129) dùng chính hàm này. URL dựng từ tên dự án của route (Codex Q10). Thân cài đặt luôn là bản gốc + phần đổi (TM-1 nhận đủ khoá, `extra="forbid"`), bản gốc và `expected_version` là bản Đại ca đang nhìn LÚC BẮT ĐẦU sửa — công tắc: bản đang xem lúc bấm; ba lệnh: bản chụp lúc mở form, không bị SSE thay (Codex Q9) → hai tab cùng sửa thì tab cũ nhận 409, giao diện báo "Cài đặt đã đổi — tải lại", giữ ô nhập, có nút "Tải lại".
3. **Hỏi lại bằng `window.confirm` như estop** (spec "như nút estop hiện có"), câu lấy từ mockup; tắt công tắc cũng hỏi (spec: "một lần bấm và xác nhận"), bật lại điều kiện thì không (chiều chặt hơn — mockup).
4. **Trạng thái chung `kho.tuDong` (GET `/api/tu-dong`)** cho thanh trên, băng vàng, chip trang Dự án; làm mới theo sự kiện SSE `su_kien` có tiền tố `tu_dong.`, `tu_merge.`, `deploy.`, `estop.` (luồng `/api/luong` đã gửi mọi sự kiện — không sửa máy chủ). Cùng lúc tải lại số Phê duyệt (dòng "sẵn sàng deploy" của TM-3) — `deploy.san_sang` không nằm trong `LOAI_LAM_MOI` của `tram/api/luong.py`.

## Bản đồ tác động

- **File:** mới `frontend/src/{luat_tu_dong,luat_trang_tu_dong,luat_bao_tu_dong,luat_lich_su_tu_dong,tam_dung}.js`, `frontend/src/trang/TuDong.vue`, `frontend/src/thanh/{BangTamDung.vue,phe_duyet/TheSanSang.vue}`, `frontend/src/thanh/tu_dong/{ghi_tu_dong,sua_lenh,tai_du_an}.js`, `frontend/src/thanh/tu_dong/{CongTac,KhoiSanSang,KhoiChoDaiCa,KhoiLichSu,KhoiCaiDat,NganLichSuDoi}.vue`, `frontend/src/kieu/tu-dong.css`, 5 file test node, `tests/test_du_lieu_giao_dien_tu_dong.py`; sửa `frontend/src/{kho,bieu_tuong,luat,luat_du_an,luat_phe_duyet,tuyen}.js`, `frontend/src/KhungChinh.vue`, `frontend/src/thanh/{ThanhTren,ThanhBen,BangEstop,DauTrang}.vue`, `frontend/src/trang/{DuAn,PheDuyet}.vue`, `frontend/src/kieu/{nen,khung,du-an}.css`, `frontend/tests/{du_an,phe_duyet}.test.mjs`, `tests/{du_lieu_giao_dien,chay_thu_giao_dien}.py`, `docs/DESIGN_SYSTEM.md`.
- **Tuyến dùng:** GET `/api/tu-dong`, GET `/api/du-an/{ten}/tu-dong`, POST `/api/tu-dong/{tam-dung,tiep-tuc}`, POST `/api/du-an/{ten}/tu-dong/{cai-dat,tam-dung,tiep-tuc,deploy}`, GET `/api/phe-duyet`. Không tuyến mới, không lệnh `tram` mới. **Dữ liệu:** không ghi gì ngoài qua tuyến TM-1. **Kill list:** không. **Giao diện cần soi:** thanh trên (mọi trang), Dự án, trang Tự động (8 ảnh mockup), Phê duyệt. **Đường lui:** revert nhánh.

## Hợp đồng TM-4 cần từ TM-2 / TM-3 (đã khớp plan TM-2 và plan TM-3 ngày 18/10)

TM-1 chỉ hứa **tên** khoá. Giao diện này đọc **dạng** dưới đây; khác thì sửa ở đây trước (hàm `choDaiCa`, `sanSang`, `dongLichSu`, `sanSangDeploy`, `theDuAn`). Thiếu khoá thì giao diện hiện "chưa có dữ liệu", không vỡ.

- **TM-2 → `GET /api/du-an/{ten}/tu-dong` (đã khớp plan TM-2 `docs/plans/2026-10-18-lat-tm-2-tu-merge.md`, mục "Interfaces cho lát sau" và Task 5):** `cho_dai_ca: [{bead_id, tieu_de, luc, ly_do: [{ma, nhan, muc}]}]`, mới → cũ; `tieu_de` = `""` khi Beads lỗi; công tắc tự merge tắt → `[]`. `nhan` là câu lời thường (`tram.giao_viec.tu_merge_xet.NHAN`), `muc` ∈ {`loi`, `tat`, `can_nguoi`} (`MUC`, mặc định `can_nguoi`) — **giao diện chọn màu theo `muc`, không theo `ma`**: `loi` → `tt-loi` (đỏ), `tat` → `tt-tat` (xám), còn lại → `tt-can_nguoi`. Đối chiếu bảng mã TM-2 (18/10): `loi` = `schema_duong_dan`, `schema_tu_khoa`, `diff_loi`, `tu_merge_loi`; `tat` = `ci_dang_chay`; `can_nguoi` = mọi mã khác (`estop`, `tam_dung_tram`, `tam_dung_du_an`, `bat_ghi`, `tu_merge_tat`, `qc`, `kiem_lai`, `pr_khac`, `dau_pr_khac`, `ci_do`, `ci_rong`, `cot`, `hang_rao_tien`, `hang_rao_quyen`, `hang_rao_khach_thay`, `hang_rao_co_do`, `pr_khong_xac_minh`) — khớp màu mockup (`du-lieu.js` `CHO_DAI_CA`: CI chưa xanh / hàng rào / cờ đỏ đỏ nhạt "cần người", cấu trúc DB đỏ, CI đang chạy xám). Giao diện không có bảng nhãn riêng; `luc` chưa hiện (mockup không vẽ).
- **TM-3 → `GET /api/du-an/{ten}/tu-dong` (đã khớp plan TM-3 `docs/plans/2026-10-18-lat-tm-3-tu-deploy.md`, `tram/deploy/hien_thi.py`):** `san_sang: null | {commit, so_merge, bead_ids: [..], luc, commit_dang_chay: str | null}` (`null` khi thiếu lệnh hoặc đang deploy); `dang_deploy: null | {trang_thai: "cho" | "chay", commit, nguon: "dai_ca" | "tu_dong", luc}` — giao diện hiện "Chờ trạm nhận bản …" (nút "Đã gửi…") khi `cho`, "Đang deploy bản …" khi `chay`; `dem_hong: int`; `lich_su` mới → cũ, tối đa 20, đúng sáu khoá `{luc, loai, bead_id | null, commit | null, chi_tiet, ai}`. `loai` ∈ `LOAI_LICH_SU` = `tu_merge`, `san_sang`, `deploy_dat`, `deploy_lui`, `lui_hong`, `khong_ro`, `tu_tat`, `tam_dung` — giao diện có nhãn/màu cho đủ tám loại, **cộng `huy` ("Deploy bị huỷ", xám) — D127 Đại ca chốt "có"**: TM-3 (đang sửa vòng 2) thêm `huy` vào `LOAI_LICH_SU` (`deploy.huy` vào lịch sử, `chi_tiet` là lý do bằng lời, `ai` = `dai_ca_bam`); loại lạ hiện nguyên mã. `ai` ∈ `AI` = `dai_ca` (TM-3 chưa sinh), `dai_ca_bam`, `tu_deploy`, `tram` (dòng `san_sang` của TM-3 có `ai = tram`). `chi_tiet` do máy chủ dựng, chỉ mã thoát, giây, quá hạn, số PR, commit ngắn (ví dụ "deploy: mã thoát 0 · 48 giây → kiểm còn sống: mã thoát 0 · 3 giây", "… (bản trước 5d3e8b2)").
- **TM-3 → `GET /api/tu-dong` (`du_an[]`):** thêm `san_sang: bool` (đủ 3 lệnh và đang có hàng sẵn sàng), `dem_hong: int` — chip "1 sẵn sàng deploy", "tự deploy đã tự tắt" (`dem_hong >= 3`) trên thẻ Dự án. Khớp.
- **TM-3 → `POST /api/du-an/{ten}/tu-dong/deploy`:** thân `{ma_thao_tac, expected_version: "", expected_commit}` — gửi từ HAI chỗ, cùng hàm `ghi_tu_dong.deploy`: trang Tự động (`san_sang.commit`) và dòng Phê duyệt (D129, `chi_tiet.commit` của mục `san-sang-deploy`); 409 `{"loi": "Có bản mới hơn — tải lại (bản chờ deploy của … đã đổi: hiện …, đang xem …)"}` — giao diện hiện nguyên câu tại khối (test `tu_dong_ghi.test.mjs` "409 / 422 / 403…"); 422 `{"loi"}`: nhãn khoá chung, "Đang có một lần deploy…", "Không có bản mới nào chờ deploy". Khớp.
- **TM-3 → `GET /api/phe-duyet`:** mục `{loai: "san-sang-deploy", du_an, bead_id: null, tieu_de: "", uu_tien: null, updated_at: <san_sang.luc>, chi_tiet: <toàn bộ san_sang>}`, tính vào `so`; `THU_TU` thêm `"san-sang-deploy"` cuối (TM-3 đã làm). Giao diện đọc `chi_tiet.commit`, `chi_tiet.so_merge`, `updated_at` ("merge cuối HH:MM"). Khớp.
- **TM-3:** tạm dừng vì lùi hỏng / không rõ giữ `ly_do` `lui-hong` / `khong-ro` trong `tu_dong.tam_dung` (hợp đồng TM-1) — khối báo đỏ dựa vào đó. Khớp.

## Lệch mockup — và lý do

1. **Không vẽ khối "Agent tự cập nhật việc" và chip "agent cập nhật việc: bật/tắt"** (trang Tự động, thẻ Dự án, mô tả hai trang) — Đại ca chốt câu 5: thuộc plan TC, cần mockup riêng.
2. **Bỏ hàng "Tình huống (chỉ có trong mockup)"** — README mockup ghi bản thật không có.
3. **Tắt tự merge / tắt tự deploy có hộp xác nhận** (mockup tắt ngay) — spec "Tắt công tắc và TẠM DỪNG MUST làm được bằng một lần bấm và xác nhận như nút estop".
4. **Thêm khối đỏ "Deploy không rõ kết quả lúc HH:MM — cần Đại ca kiểm"** (khi `tam_dung.ly_do = khong-ro`) và nhãn lịch sử "Không rõ kết quả" — spec `tu-deploy` "Kết quả deploy không rõ" đòi câu này, mockup chưa vẽ; dùng đúng kiểu khối LÙI HỎNG.
5. **Thêm hàng "Đang deploy bản …" / "Chờ trạm nhận bản …" (nút "Đang deploy…" / "Đã gửi…" khoá)** — spec "Đại ca bấm Deploy → hàng chuyển sang đang deploy"; TM-3 có thêm bước "chờ trạm nhận" (`dang_deploy.trang_thai = cho`); mockup chỉ đổi chữ nút tạm thời. Thêm nhãn lịch sử "Deploy bị huỷ" (D127 đã chốt) — mockup không có.
6. **Khối nào thiếu dữ liệu của TM-2/TM-3 hiện "Chưa có dữ liệu — phần này của trạm chưa chạy."** — mockup không có trạng thái này.
7. **Dòng "sẵn sàng deploy" ở Phê duyệt CÓ nút Deploy (D129 — lệch mockup MỚI, Đại ca chốt 18/10, khác đề xuất cũ "chỉ link")** — mockup 18/10 không vẽ trang Phê duyệt; dùng khung thẻ `.the-duyet` có sẵn (D36), chip `pr-mo`, nút chính "Deploy" (cùng hộp hỏi, cùng thân, cùng 409/422, cùng khoá như nút trang Tự động; câu khoá hiện dưới thẻ và ở `title`) và nút phụ "Mở trang Tự động".
8. **Câu khoá kèm giải thích ở đầu khối Cài đặt và ở `title` công tắc** (mockup chỉ mờ nút) — spec "khoá … kèm lời giải thích".
9. **Câu khối "Cửa ghi còn tạm" bỏ "(đề xuất ở câu hỏi mở 1)"** — câu hỏi đã được Đại ca trả lời.
10. **Lịch sử đổi thêm "· ai" mỗi dòng** — spec "Xem lịch sử đổi": mỗi dòng ghi "Đại ca (dashboard)", giờ, trước và sau.
11. **Băng Estop đổi chữ theo mockup 18/10** ("… không tự merge, không deploy; …") — mockup `index.html` mới; không đổi hộp xác nhận của Estop.
12. **Khối "Sẵn sàng deploy" dùng token mới `--xanh-bien`, `--vien-xanh-bien`** thay hex của `them.css` (DESIGN_SYSTEM: màu mới thêm token ở `nen.css`); giá trị giữ nguyên.
14. **Khối Cài đặt có nút "Tải lại" khi 409 và dòng "Đang lưu ở trạm: …" dưới ô lệnh sau khi tải lại** (Codex Q9) — mockup không vẽ xung đột hai tab; spec "Màn hình cũ" đòi giữ ô nhập + "tải lại".
13. Trên thẻ Dự án, chip "chỉ quét thử" chuyển từ hàng chip cột xuống hàng tự động (đúng `anh-du-an.png`); thẻ không còn là một link lớn (lồng link không hợp lệ) — tên dự án là link sang Công việc như mockup.

## Task ↔ file

| Task | Mốc | File | Test mới |
|---|---|---|---|
| 1 | 5.2 | Create `frontend/src/{luat_tu_dong,tam_dung}.js`, `frontend/src/thanh/BangTamDung.vue`, `frontend/tests/tu_dong_khung.test.mjs`; Modify `frontend/src/{bieu_tuong,kho}.js`, `frontend/src/KhungChinh.vue`, `frontend/src/thanh/{ThanhTren,ThanhBen,BangEstop}.vue`, `frontend/src/kieu/khung.css` | 6 node |
| 2 | 5.1 | Modify `frontend/src/luat_du_an.js`, `frontend/src/trang/DuAn.vue`, `frontend/src/kieu/du-an.css`, `frontend/tests/du_an.test.mjs` | 1 node |
| 3 | 5.1, 5.2 | Create `frontend/src/{luat_trang_tu_dong,luat_bao_tu_dong,luat_lich_su_tu_dong}.js`, `frontend/tests/{tu_dong_trang,tu_dong_lich_su}.test.mjs` | 10 node |
| 4 | 5.1, 5.2 | Create `frontend/src/thanh/tu_dong/*` (9 file), `frontend/src/trang/TuDong.vue`, `frontend/src/kieu/tu-dong.css`, `frontend/tests/{tu_dong_ghi,tu_dong_dong_bo}.test.mjs`; Modify `frontend/src/tuyen.js`, `frontend/src/thanh/DauTrang.vue`, `frontend/src/kieu/nen.css` | 10 node |
| 5 | 5.1 (D101, D129) | Create `frontend/src/thanh/phe_duyet/TheSanSang.vue`; Modify `frontend/src/{luat,luat_phe_duyet}.js`, `frontend/src/trang/PheDuyet.vue`, `frontend/tests/phe_duyet.test.mjs` | 2 node |
| 6 | (kiểm tay 5.1/5.2) | Modify `tests/du_lieu_giao_dien.py`, `tests/chay_thu_giao_dien.py`; Create `tests/test_du_lieu_giao_dien_tu_dong.py` | 3 pytest |
| 7 | 5.1, 5.2 | kiểm trên trình duyệt dưới CSP thật; Modify `docs/DESIGN_SYSTEM.md` | — |

Thứ tự bắt buộc 1 → 7 (Task 2 dùng `chipTuDong` của Task 1; Task 4 dùng luật Task 3; Task 5 dùng `ghi_tu_dong.js` của Task 4 và `lyDoKhoaDeploy` của Task 3; Task 7 cần Task 6). Không file nào bị hai task cùng sửa.

## Tasks

### Task 1: Nút TẠM DỪNG toàn trạm, băng vàng, trạng thái tự động chung

**Spec:** `dieu-khien-tu-dong` "TẠM DỪNG toàn trạm" (nút vàng cạnh Estop trên mọi trang, băng "Tự merge · tự deploy đang tạm dừng toàn trạm"), "Cửa ghi còn tạm…" (TẠM DỪNG vẫn bấm được; Tiếp tục cần kênh thật — D87, câu 1 plan TM-1), "Xem khi không phải Đại ca". **Mockup:** `index.html` (`#nut-tam-dung-tram`, `.bang-tam-dung`, băng estop), `app.js`, `them.css`; ảnh `anh-tam-dung-toan-tram.png`.

**Interfaces:** Produces `laSuKienTuDong(loai)`, `lyDoKhoaGhi(dl, laDaiCa)`, `lyDoKhoaTamDung(dl, laDaiCa, dangBat)`, `nutTamDungTram(td, laDaiCa) -> {bat, chu, khoa, lyDo, title}`, `chipTuDong(da, tram) -> [{chu, lop, title}]`, hằng `CHU_CHI_DOC`, `CHU_CUA_TAM`, `HOI_TAM_DUNG_TRAM`; `kho.tuDong`, `kho.phienBanTuDong`, `taiTuDong()` (bỏ phản hồi của lần tải cũ — Codex Q10); `dungTamDungTram() -> {dangGui, thongBao, bam(bat)}`; icon `tam-dung`. Consumes GET `/api/tu-dong`, POST `/api/tu-dong/{tam-dung,tiep-tuc}` (TM-1).

- [ ] **Step 0: Kiểm điều kiện vào** — Đại ca đã duyệt plan; TM-1 → TM-2 → TM-3 đã ghép `main`; dùng TM-1 mới `85ce7f4`, plan TM-1 `874e7c4` (`ls tram/api/tuyen_tu_dong.py tram/suy/tu_dong.py`). `git apply --check` mọi bản vá của plan này trên HEAD (áp theo nội dung); hỏng thì DỪNG. Đo N₀: `tests/chan_host/chay.sh -q` (mong đợi `3412 passed` nếu `main` = `0f88957` về mã), M₀: `cd frontend && npm run kiem` (mong đợi `ℹ tests 102`).

- [ ] **Step 1: Viết test**

Tạo mới `frontend/tests/tu_dong_khung.test.mjs` (nguyên văn):

```js
import assert from 'node:assert/strict'
import { test } from 'node:test'
import { duongVe } from '../src/bieu_tuong.js'
import { kho, moLuong, taiTuDong } from '../src/kho.js'
import { CHU_CHI_QUET_THU } from '../src/luat.js'
import { CHU_CHI_DOC, CHU_CUA_TAM, chipTuDong, laSuKienTuDong, lyDoKhoaGhi, lyDoKhoaTamDung, nutTamDungTram }
  from '../src/luat_tu_dong.js'
import { MENU, mucCua } from '../src/menu.js'

const TD = { tam_dung_tram: null, estop: false, kenh_ghi: 'unix-socket', chi_tam_dung: false, la_dai_ca: true }
const TAM = { boi: 'dai-ca/dashboard', luc: '2026-10-18T14:52:00Z', ly_do: '' }

test('sự kiện làm trạng thái tự động đổi: tu_dong.*, tu_merge.*, deploy.*, estop.*', () => {
  for (const l of ['tu_dong.cai_dat', 'tu_dong.tam_dung', 'tu_merge.xong', 'deploy.san_sang', 'estop.bat']) {
    assert.equal(laSuKienTuDong(l), true, l)
  }
  for (const l of ['quet.xong', 'pr.da_merge', 'tu_dongx', '', null, undefined]) assert.equal(laSuKienTuDong(l), false)
})

test('nút TẠM DỪNG toàn trạm: chữ theo trạng thái; khoá khi chưa đọc, không phải Đại ca, Tiếp tục qua header', () => {
  assert.deepEqual(nutTamDungTram(TD, true), { bat: false, chu: 'Tạm dừng tự động', khoa: false, lyDo: '',
    title: 'Tạm dừng tự merge và tự deploy của mọi dự án. Trạm vẫn giao việc, kiểm lại, QC, mở PR.' })
  const bat = nutTamDungTram({ ...TD, tam_dung_tram: TAM }, true)
  assert.equal(bat.bat, true)
  assert.equal(bat.chu, 'Đang tạm dừng tự động')
  assert.equal(bat.khoa, false)
  assert.equal(bat.title, 'Bấm để tiếp tục tự merge và tự deploy')
  assert.equal(nutTamDungTram(TD, false).lyDo, CHU_CHI_DOC)
  assert.equal(nutTamDungTram(null, true).khoa, true)
  assert.equal(nutTamDungTram(null, true).lyDo, 'Chưa đọc được trạng thái tự động')
  const header = { ...TD, chi_tam_dung: true }
  assert.equal(nutTamDungTram(header, true).khoa, false)                     // D87: TẠM DỪNG vẫn bấm được
  const tiepTuc = nutTamDungTram({ ...header, tam_dung_tram: TAM }, true)
  assert.equal(tiepTuc.khoa, true)
  assert.equal(tiepTuc.lyDo, 'Cửa ghi còn tạm — Tiếp tục cần cửa ghi unix-socket')
})

test('khoá nút ghi trừ TẠM DỪNG: danh tính → cửa ghi tạm → chỉ quét thử; TẠM DỪNG chỉ cần danh tính', () => {
  assert.equal(lyDoKhoaGhi({ ...TD, bat_ghi: true }, true), '')
  assert.equal(lyDoKhoaGhi({ ...TD, bat_ghi: true }, false), CHU_CHI_DOC)
  assert.equal(lyDoKhoaGhi({ ...TD, bat_ghi: false, chi_tam_dung: true }, true), CHU_CUA_TAM)
  assert.equal(lyDoKhoaGhi({ ...TD, bat_ghi: false }, true), CHU_CHI_QUET_THU)
  assert.equal(lyDoKhoaGhi(null, true), 'Chưa đọc được trạng thái tự động')
  assert.equal(CHU_CUA_TAM, 'Cửa ghi còn tạm — chỉ bấm được TẠM DỪNG')
  assert.equal(lyDoKhoaTamDung({ ...TD, bat_ghi: false, chi_tam_dung: true }, true, false), '')
  assert.equal(lyDoKhoaTamDung(TD, false, false), CHU_CHI_DOC)
  assert.equal(lyDoKhoaTamDung({ ...TD, chi_tam_dung: true }, true, true),
    'Cửa ghi còn tạm — Tiếp tục cần cửa ghi unix-socket')
})

test('chip tóm tắt của dự án theo mockup chipTuDong (không có chip agent cập nhật việc)', () => {
  const da = { ten: 'repo-nhap', bat_ghi: true, tu_merge: true, tu_deploy: false, du_lenh: true, tam_dung: null }
  assert.deepEqual(chipTuDong(da, TD), [{ chu: 'tự merge: bật', lop: 'tt-lam', title: '' },
    { chu: 'tự deploy: tắt', lop: 'tt-tat', title: '' }])
  assert.deepEqual(chipTuDong({ ...da, tam_dung: TAM }, TD), [{ chu: 'tạm dừng', lop: 'tt-cau_dao', title: '' }])
  assert.deepEqual(chipTuDong(da, { ...TD, tam_dung_tram: TAM }),
    [{ chu: 'tạm dừng toàn trạm', lop: 'tt-cau_dao', title: '' }])
  assert.deepEqual(chipTuDong(da, { ...TD, estop: true }), [{ chu: 'estop đang bật', lop: 'tt-loi', title: '' }])
  assert.deepEqual(chipTuDong({ ...da, bat_ghi: false }, { ...TD, estop: true }),
    [{ chu: 'chỉ quét thử', lop: '', title: CHU_CHI_QUET_THU }])
  assert.deepEqual(chipTuDong(null, TD), [])
})

test('đường /du-an/<ten> thuộc mục Dự án; có icon tạm dừng', () => {
  assert.equal(mucCua('/du-an/repo-nhap').ma, 'du-an')
  assert.equal(MENU.find((m) => m.ma === 'du-an').duong, '/du-an')
  assert.ok(duongVe('tam-dung').length === 2)
})

class NguonGia {
  constructor(url) { this.url = url; this.nghe = {} }
  addEventListener(ten, f) { this.nghe[ten] = f }
}
const xong = () => new Promise((r) => setImmediate(r))

test('SSE: sự kiện tự động → tải lại /api/tu-dong và số Phê duyệt, tăng phienBanTuDong; khác thì không', async () => {
  const goi = []
  globalThis.fetch = async (url) => { goi.push(url); return new Response(JSON.stringify({ ...TD, so: 1 })) }
  globalThis.EventSource = NguonGia
  const es = moLuong()
  const truoc = kho.phienBanTuDong
  const phienBanTruoc = kho.phienBan
  es.nghe.su_kien({ data: JSON.stringify({ id: 9, loai: 'quet.xong', du_an: 'a' }) })
  await xong()
  assert.deepEqual(goi, [])
  es.nghe.su_kien({ data: JSON.stringify({ id: 10, loai: 'tu_dong.tam_dung', du_an: '_tram' }) })
  await xong()
  assert.deepEqual(goi.sort(), ['/api/phe-duyet', '/api/tu-dong'])
  assert.equal(kho.phienBanTuDong, truoc + 1)
  assert.equal(kho.phienBan, phienBanTruoc + 1)       // Phê duyệt đang mở theo dõi phienBan, không chỉ số đếm
  assert.equal(kho.tuDong.chi_tam_dung, false)
  globalThis.fetch = async () => new Response('{}', { status: 500 })
  await taiTuDong()
  assert.equal(kho.tuDong, null)                       // đọc lỗi → khoá nút (nutTamDungTram(null) khoá)
})

test('tải /api/tu-dong dồn (SSE liên tiếp): phản hồi cũ về sau không ghi đè bản mới — Codex Q10', async () => {
  const tra = []
  globalThis.fetch = () => new Promise((r) => { tra.push(r) })
  const dau = taiTuDong()
  const sau = taiTuDong()
  tra[1](new Response(JSON.stringify({ ...TD, estop: true })))
  await sau
  tra[0](new Response(JSON.stringify({ ...TD, estop: false })))
  await dau
  assert.equal(kho.tuDong.estop, true)                 // nút Deploy ở Phê duyệt (D129) khoá theo bản mới nhất
})
```

- [ ] **Step 2: Chạy, mong đợi ĐỎ**

```bash
cd frontend && node --test tests/tu_dong_khung.test.mjs
```
Đỏ thật: `Error [ERR_MODULE_NOT_FOUND]: Cannot find module '…/frontend/src/luat_tu_dong.js' imported from …/frontend/tests/tu_dong_khung.test.mjs` — `ℹ tests 1`, `ℹ fail 1`.

- [ ] **Step 3: Viết mã**

Tạo mới `frontend/src/luat_tu_dong.js` (nguyên văn):

```js
// Luật hiển thị chung của tự merge / tự deploy (change tu-merge-tu-deploy, mockup 2026-10-18, D78, D87, D101) —
// thuần, test bằng node --test. Trạng thái do máy chủ suy (GET /api/tu-dong, /api/du-an/<ten>/tu-dong); ở đây chỉ
// chọn chữ, màu và câu khoá. Khoá ở giao diện chỉ là tiện: máy chủ vẫn từ chối (403/422) dù nút bị mở.
import { CHU_CHI_QUET_THU } from './luat.js'

const TIEN_TO = ['tu_dong.', 'tu_merge.', 'deploy.', 'estop.']
export const CHU_CHI_DOC = 'Chỉ đọc: thiếu danh tính Đại ca'
export const CHU_CUA_TAM = 'Cửa ghi còn tạm — chỉ bấm được TẠM DỪNG'
const CHU_CHUA_DOC = 'Chưa đọc được trạng thái tự động'
const CHU_TIEP_TUC_TAM = 'Cửa ghi còn tạm — Tiếp tục cần cửa ghi unix-socket'
export const HOI_TAM_DUNG_TRAM =
  'Tạm dừng tự merge và tự deploy của MỌI dự án? Trạm vẫn giao việc, kiểm lại, QC, mở PR.'

// Sự kiện SSE (`su_kien`) làm trạng thái tự động đổi → tải lại thanh trên, trang Tự động, số đếm Phê duyệt.
export function laSuKienTuDong(loai) {
  return typeof loai === 'string' && TIEN_TO.some((t) => loai.startsWith(t))
}

// Mọi nút ghi trừ TẠM DỪNG (spec "Cửa ghi còn tạm…", "Dự án khoá ghi…", "Xem khi không phải Đại ca"): '' = mở.
export function lyDoKhoaGhi(dl, laDaiCa) {
  if (!laDaiCa) return CHU_CHI_DOC
  if (!dl) return CHU_CHUA_DOC
  if (dl.chi_tam_dung) return CHU_CUA_TAM
  return dl.bat_ghi === false ? CHU_CHI_QUET_THU : ''
}

// TẠM DỪNG: chỉ cần danh tính (kênh header vẫn nhận — D87; `bat_ghi: false` vẫn bấm được). Tiếp tục thì cần kênh thật.
export function lyDoKhoaTamDung(dl, laDaiCa, dangBat) {
  if (!laDaiCa) return CHU_CHI_DOC
  return dangBat && dl && dl.chi_tam_dung ? CHU_TIEP_TUC_TAM : ''
}

// Nút TẠM DỪNG toàn trạm trên thanh trên (mockup index.html `#nut-tam-dung-tram`, cạnh Estop, màu vàng, D101).
export function nutTamDungTram(td, laDaiCa) {
  const bat = Boolean(td && td.tam_dung_tram)
  const lyDo = td ? lyDoKhoaTamDung(td, laDaiCa, bat) : CHU_CHUA_DOC
  const title = lyDo || (bat ? 'Bấm để tiếp tục tự merge và tự deploy'
    : 'Tạm dừng tự merge và tự deploy của mọi dự án. Trạm vẫn giao việc, kiểm lại, QC, mở PR.')
  return { bat, chu: bat ? 'Đang tạm dừng tự động' : 'Tạm dừng tự động', khoa: Boolean(lyDo), lyDo, title }
}

// Chip tóm tắt một dự án (mockup trang-du-an.js `chipTuDong`; chip "agent cập nhật việc" thuộc plan TC, không vẽ).
// `da`: phần tử `du_an` của GET /api/tu-dong; `tram`: phần chung {estop, tam_dung_tram}.
export function chipTuDong(da, tram) {
  if (!da) return []
  const chip = (chu, lop = '', title = '') => ({ chu, lop, title })
  if (da.bat_ghi === false) return [chip('chỉ quét thử', '', CHU_CHI_QUET_THU)]
  if (tram && tram.estop) return [chip('estop đang bật', 'tt-loi')]
  if (tram && tram.tam_dung_tram) return [chip('tạm dừng toàn trạm', 'tt-cau_dao')]
  if (da.tam_dung) return [chip('tạm dừng', 'tt-cau_dao')]
  const cong = (ten, bat) => chip(`${ten}: ${bat ? 'bật' : 'tắt'}`, bat ? 'tt-lam' : 'tt-tat')
  return [cong('tự merge', da.tu_merge), cong('tự deploy', da.tu_deploy)]
}
```

Tạo mới `frontend/src/tam_dung.js` (nguyên văn):

```js
// TẠM DỪNG toàn trạm từ thanh trên và băng vàng (spec dieu-khien-tu-dong "TẠM DỪNG toàn trạm", D78, D101).
// Như estop.js: bật có hộp xác nhận, Tiếp tục một lần bấm; không kiểm phiên bản (máy chủ bỏ qua `expected_version`).
import { ref } from 'vue'
import { ghi, thanGhi } from './api.js'
import { kho, taiTuDong } from './kho.js'
import { HOI_TAM_DUNG_TRAM } from './luat_tu_dong.js'

export function dungTamDungTram() {
  const dangGui = ref(false)
  const thongBao = ref('')
  async function bam(bat) {
    if (!kho.tuDong || (bat && !window.confirm(HOI_TAM_DUNG_TRAM))) return
    dangGui.value = true
    try {
      await ghi(bat ? '/api/tu-dong/tam-dung' : '/api/tu-dong/tiep-tuc', thanGhi({}, ''))
      thongBao.value = ''
      await taiTuDong()
    } catch (e) {
      thongBao.value = e.message
    } finally {
      dangGui.value = false
    }
  }
  return { dangGui, thongBao, bam }
}
```

Tạo mới `frontend/src/thanh/BangTamDung.vue` (nguyên văn):

```vue
<script setup>
// Băng vàng dưới thanh trên khi TẠM DỪNG toàn trạm bật (mockup index.html `.bang-tam-dung`, D101) — có trên mọi trang.
// "Tiếp tục" gọi lại hàm của thanh trên; khoá khi không phải Đại ca hoặc cửa ghi còn tạm (D87), câu giải thích ở title.
defineProps({ khoa: { type: Boolean, default: false }, lyDo: { type: String, default: '' } })
const emit = defineEmits(['tiep-tuc'])
</script>

<template>
  <div class="bang-tam-dung" role="status">
    <span><b>Tự merge · tự deploy đang tạm dừng toàn trạm</b> — trạm vẫn giao việc, kiểm lại, QC và mở PR; chỉ không
      tự merge, không tự deploy. Việc đang deploy dở được làm nốt.</span>
    <button type="button" :disabled="khoa" :title="lyDo" @click="emit('tiep-tuc')">Tiếp tục</button>
  </div>
</template>
```

Bản vá `frontend/src/bieu_tuong.js`:

```diff
diff --git a/frontend/src/bieu_tuong.js b/frontend/src/bieu_tuong.js
index caacc4b..3c0f7e9 100644
--- a/frontend/src/bieu_tuong.js
+++ b/frontend/src/bieu_tuong.js
@@ -26,6 +26,8 @@ export const BIEU_TUONG = {
   'cai-dat': ['M9 12a3 3 0 1 0 6 0a3 3 0 1 0 -6 0', BANH_RANG],
   tim: ['M4 11a7 7 0 1 0 14 0a7 7 0 1 0 -14 0', 'm20 20-3.5-3.5'],
   estop: ['M12 3v8', 'M6.3 6.3a8 8 0 1 0 11.4 0'],
+  'tam-dung': ['M7 5h2a1 1 0 0 1 1 1v12a1 1 0 0 1 -1 1h-2a1 1 0 0 1 -1 -1v-12a1 1 0 0 1 1 -1z',      // tô đặc (.dac)
+    'M15 5h2a1 1 0 0 1 1 1v12a1 1 0 0 1 -1 1h-2a1 1 0 0 1 -1 -1v-12a1 1 0 0 1 1 -1z'],
   khoa: ['M7 11h10a2 2 0 0 1 2 2v5a2 2 0 0 1 -2 2h-10a2 2 0 0 1 -2 -2v-5a2 2 0 0 1 2 -2z', 'M8 11V8a4 4 0 0 1 8 0v3'],
 }
 
```

Bản vá `frontend/src/kho.js`:

```diff
diff --git a/frontend/src/kho.js b/frontend/src/kho.js
index 07463a2..ec9cf16 100644
--- a/frontend/src/kho.js
+++ b/frontend/src/kho.js
@@ -1,10 +1,11 @@
 // Trạng thái dùng chung giữa các trang; mọi trạng thái nghiệp vụ tính ở server (Q12).
 import { reactive } from 'vue'
 import { doc } from './api.js'
+import { laSuKienTuDong } from './luat_tu_dong.js'
 import { laSuKienNho } from './nho.js'
 
 export const kho = reactive({ trangThai: null, soPheDuyet: 0, phienBan: 0, phienBanNho: 0, phienBanDoiNgu: 0, suKienCuoi: null,
-  matKetNoi: false, loi: '' })
+  matKetNoi: false, loi: '', tuDong: null, phienBanTuDong: 0 })
 
 let lanTaiTrangThai = 0
 export async function taiTrangThai() {
@@ -31,6 +32,19 @@ export async function taiSoPheDuyet() {
   }
 }
 
+// TM-4: GET /api/tu-dong — TẠM DỪNG toàn trạm, cửa ghi tạm (`chi_tam_dung`), tóm tắt từng dự án. Lỗi → null (khoá nút).
+// Phản hồi của lần tải cũ về sau (SSE tải dồn) bị bỏ — như taiTrangThai (Codex Q10).
+let lanTaiTuDong = 0
+export async function taiTuDong() {
+  const lan = ++lanTaiTuDong
+  try {
+    const td = await doc('/api/tu-dong')
+    if (lan === lanTaiTuDong) kho.tuDong = td
+  } catch {
+    if (lan === lanTaiTuDong) kho.tuDong = null
+  }
+}
+
 export function moLuong() {
   const es = new EventSource('/api/luong')
   const doi = () => { kho.phienBan += 1 }
@@ -41,6 +55,12 @@ export function moLuong() {
     try {
       kho.suKienCuoi = JSON.parse(e.data)
       if (laSuKienNho(kho.suKienCuoi.loai)) kho.phienBanNho += 1     // màn Ký ức tải lại (1b-3)
+      if (laSuKienTuDong(kho.suKienCuoi.loai)) {                       // TM-4: thanh trên, trang Tự động, Phê duyệt
+        kho.phienBanTuDong += 1
+        doi()                                                       // tải lại danh sách Phê duyệt đang mở
+        taiTuDong()
+        taiSoPheDuyet()
+      }
     } catch {
       kho.suKienCuoi = null
     }
```

Bản vá `frontend/src/KhungChinh.vue`:

```diff
diff --git a/frontend/src/KhungChinh.vue b/frontend/src/KhungChinh.vue
index eaa8bb9..8baac5f 100644
--- a/frontend/src/KhungChinh.vue
+++ b/frontend/src/KhungChinh.vue
@@ -2,18 +2,24 @@
 import { computed, onMounted, watch } from 'vue'
 import { useRoute } from 'vue-router'
 import { dungEstop } from './estop.js'
-import { kho, moLuong, taiSoPheDuyet, taiTrangThai, theoDoiTab } from './kho.js'
+import { kho, moLuong, taiSoPheDuyet, taiTrangThai, taiTuDong, theoDoiTab } from './kho.js'
 import { tieuDeTab } from './luat.js'
+import { nutTamDungTram } from './luat_tu_dong.js'
 import { tenTrang } from './menu.js'
+import { dungTamDungTram } from './tam_dung.js'
 import BangEstop from './thanh/BangEstop.vue'
+import BangTamDung from './thanh/BangTamDung.vue'
 import ThanhBen from './thanh/ThanhBen.vue'
 import ThanhTren from './thanh/ThanhTren.vue'
 
-// Khung mockup (index.html): sidebar | thanh trên + băng estop + trang. Tiêu đề tab "<trang> · Ben Station".
+// Khung mockup (index.html): sidebar | thanh trên + băng estop + băng tạm dừng (TM-4) + trang.
+// Tiêu đề tab "<trang> · Ben Station".
 const route = useRoute()
 const estop = dungEstop()
 const khoa = computed(() => !(kho.trangThai && kho.trangThai.la_dai_ca) || estop.dangGui.value)
-onMounted(() => { taiTrangThai(); taiSoPheDuyet(); moLuong(); theoDoiTab() })
+const tamDung = dungTamDungTram()
+const nutTD = computed(() => nutTamDungTram(kho.tuDong, Boolean(kho.trangThai && kho.trangThai.la_dai_ca)))
+onMounted(() => { taiTrangThai(); taiSoPheDuyet(); taiTuDong(); moLuong(); theoDoiTab() })
 watch([() => route.path, () => kho.soPheDuyet],
   () => { document.title = tieuDeTab(kho.soPheDuyet, tenTrang(route.path)) }, { immediate: true })
 </script>
@@ -21,9 +27,12 @@ watch([() => route.path, () => kho.soPheDuyet],
 <template>
   <ThanhBen />
   <div class="khung">
-    <ThanhTren :estop="estop" />
+    <ThanhTren :estop="estop" :tam-dung="tamDung" :nut-tam-dung="nutTD" />
     <BangEstop v-if="kho.trangThai && kho.trangThai.estop" :khoa="khoa" @tiep-tuc="estop.bam(false)" />
+    <BangTamDung v-if="nutTD.bat" :khoa="nutTD.khoa || tamDung.dangGui.value" :ly-do="nutTD.lyDo"
+                 @tiep-tuc="tamDung.bam(false)" />
     <p v-if="estop.thongBao.value" class="loi-chung" role="alert">{{ estop.thongBao.value }}</p>
+    <p v-if="tamDung.thongBao.value" class="loi-chung" role="alert">{{ tamDung.thongBao.value }}</p>
     <p v-if="kho.loi" class="loi-chung" role="alert">{{ kho.loi }}</p>
     <main class="trang"><router-view /></main>
   </div>
```

Bản vá `frontend/src/thanh/ThanhTren.vue`:

```diff
diff --git a/frontend/src/thanh/ThanhTren.vue b/frontend/src/thanh/ThanhTren.vue
index f86558e..76349f6 100644
--- a/frontend/src/thanh/ThanhTren.vue
+++ b/frontend/src/thanh/ThanhTren.vue
@@ -6,8 +6,9 @@ import BieuTuong from './BieuTuong.vue'
 import OTim from './OTim.vue'
 
 // Thanh trên (mockup index.html `.thanh-tren`): ô tìm ⌘K, viên đồng bộ (quét cuối mới nhất của mọi dự án; mất luồng
-// SSE thì báo "Mất kết nối"), nút Estop. Chỉ Đại ca bấm được (khoá như ThanhTrangThai cũ).
-const props = defineProps({ estop: { type: Object, required: true } })
+// SSE thì báo "Mất kết nối"), nút TẠM DỪNG toàn trạm màu vàng (TM-4, D101), nút Estop. Chỉ Đại ca bấm được.
+const props = defineProps({ estop: { type: Object, required: true }, tamDung: { type: Object, required: true },
+  nutTamDung: { type: Object, required: true } })
 const tt = computed(() => kho.trangThai)
 const quetCuoi = computed(() => {
   const ds = (tt.value ? tt.value.du_an : []).map((d) => d.quet_cuoi).filter(Boolean).sort()
@@ -23,6 +24,10 @@ const khoa = computed(() => !tt.value || !tt.value.la_dai_ca || props.estop.dang
       <span class="vien-tt mono" role="status">
         <span class="cham" :class="kho.matKetNoi ? 'do' : 'xanh'" />
         {{ kho.matKetNoi ? 'Mất kết nối · đang thử lại' : `Đồng bộ · quét cuối ${quetCuoi}` }}</span>
+      <button type="button" class="nut-estop vang" :class="{ bat: nutTamDung.bat }" :title="nutTamDung.title"
+              :disabled="nutTamDung.khoa || tamDung.dangGui.value" @click="tamDung.bam(!nutTamDung.bat)">
+        <BieuTuong ten="tam-dung" class="dac" /><span>{{ nutTamDung.chu }}</span>
+      </button>
       <button type="button" class="nut-estop" :class="{ bat: tt && tt.estop }" :disabled="khoa"
               :title="tt && !tt.la_dai_ca ? 'Chỉ đọc: thiếu danh tính Đại ca' : 'Dừng khẩn: trạm ngừng giao việc mới'"
               @click="estop.bam(!(tt && tt.estop))">
```

Bản vá `frontend/src/thanh/ThanhBen.vue`:

```diff
diff --git a/frontend/src/thanh/ThanhBen.vue b/frontend/src/thanh/ThanhBen.vue
index 86ae1a2..a35a4fd 100644
--- a/frontend/src/thanh/ThanhBen.vue
+++ b/frontend/src/thanh/ThanhBen.vue
@@ -1,7 +1,8 @@
 <script setup>
 import { computed } from 'vue'
+import { useRoute } from 'vue-router'
 import { kho } from '../kho.js'
-import { MENU } from '../menu.js'
+import { MENU, mucCua } from '../menu.js'
 import BieuTuong from './BieuTuong.vue'
 
 // Sidebar 272 px (mockup index.html `.sidebar`, anh-tong-quan.png): logo, menu 9 mục, máy trạm, thẻ người dùng.
@@ -9,6 +10,9 @@ import BieuTuong from './BieuTuong.vue'
 const may = window.location.hostname
 const cucBo = ['127.0.0.1', 'localhost', '::1'].includes(may)
 const laDaiCa = computed(() => Boolean(kho.trangThai && kho.trangThai.la_dai_ca))
+// Mục sáng theo `mucCua` (TM-4): /du-an/<ten> (trang Tự động) vẫn sáng "Dự án" như mockup.
+const route = useRoute()
+const chon = computed(() => mucCua(route.path)?.ma)
 </script>
 
 <template>
@@ -19,7 +23,7 @@ const laDaiCa = computed(() => Boolean(kho.trangThai && kho.trangThai.la_dai_ca)
       <span class="ws-huy-hieu">Bàn điều hành</span>
     </div>
     <nav class="menu" aria-label="Điều hướng chính">
-      <router-link v-for="m in MENU" :key="m.ma" :to="m.duong" active-class="chon">
+      <router-link v-for="m in MENU" :key="m.ma" :to="m.duong" :class="{ chon: chon === m.ma }">
         <BieuTuong :ten="m.ma" />{{ m.ten }}
         <span v-if="m.dem && kho.soPheDuyet" class="dem" :aria-label="kho.soPheDuyet + ' việc chờ'">
           {{ kho.soPheDuyet }}</span>
```

Bản vá `frontend/src/thanh/BangEstop.vue`:

```diff
diff --git a/frontend/src/thanh/BangEstop.vue b/frontend/src/thanh/BangEstop.vue
index fda6ae3..4deaf83 100644
--- a/frontend/src/thanh/BangEstop.vue
+++ b/frontend/src/thanh/BangEstop.vue
@@ -6,7 +6,8 @@ const emit = defineEmits(['tiep-tuc'])
 
 <template>
   <div class="bang-estop" role="status">
-    <b>Estop đang bật</b> — trạm không giao việc mới, khe đang chạy dừng mềm sau lượt hiện tại.
+    <b>Estop đang bật</b> — trạm không giao việc mới, không tự merge, không deploy; khe đang chạy dừng mềm sau lượt
+    hiện tại.
     <button type="button" :disabled="khoa" @click="emit('tiep-tuc')">Tiếp tục</button>
   </div>
 </template>
```

Bản vá `frontend/src/kieu/khung.css`:

```diff
diff --git a/frontend/src/kieu/khung.css b/frontend/src/kieu/khung.css
index b6b8368..8c3bee2 100644
--- a/frontend/src/kieu/khung.css
+++ b/frontend/src/kieu/khung.css
@@ -85,6 +85,22 @@
 .nut-estop .bieu-tuong { width: 14px; height: 14px; stroke-width: 2.2; }
 .nut-estop:hover:not(:disabled), .nut-estop.bat { background: var(--do); color: #fff; border-color: var(--do); }
 .nut-estop:disabled { opacity: .55; cursor: not-allowed; }
+/* TM-4: nút TẠM DỪNG — cùng hình nút Estop, màu vàng cảnh báo (mockup them.css); băng vàng cùng kiểu băng Estop. */
+.nut-estop { white-space: nowrap; }
+.nut-estop.vang { border-color: var(--vien-canh-bao); background: var(--nen-canh-bao); color: var(--chu-canh-bao); }
+.nut-estop.vang:hover:not(:disabled), .nut-estop.vang.bat {
+  background: var(--vang); border-color: var(--vang); color: var(--the);
+}
+.nut-estop .bieu-tuong.dac { fill: currentColor; stroke: none; }
+.bang-tam-dung {
+  background: var(--nen-canh-bao); color: var(--chu-canh-bao); border-bottom: 1px solid var(--vien-canh-bao);
+  padding: 9px 30px; font-size: 14px; display: flex; gap: 10px; align-items: center;
+}
+.bang-tam-dung button {
+  margin-left: auto; border: 1px solid var(--chu-canh-bao); background: var(--the); color: var(--chu-canh-bao);
+  border-radius: 7px; padding: 4px 12px; font-weight: 600; white-space: nowrap;
+}
+.bang-tam-dung button:disabled { opacity: .55; cursor: not-allowed; }
 .bang-estop {
   background: var(--nen-bang-estop); color: var(--chu-bang-estop); border-bottom: 1px solid #e8bfb2;
   padding: 9px 30px; font-size: 14px; display: flex; gap: 10px; align-items: center;
@@ -99,5 +115,5 @@
   .menu { flex-direction: row; flex-wrap: wrap; padding: 10px 9px; }
   .thanh-tren { padding: 0 16px; flex-wrap: wrap; height: auto; min-height: 54px; }
   .tim { flex: 1 1 100%; order: 2; margin-bottom: 8px; }
-  .bang-estop, .loi-chung { padding: 9px 16px; }
+  .bang-estop, .bang-tam-dung, .loi-chung { padding: 9px 16px; }
 }
```

- [ ] **Step 4: Chạy, mong đợi XANH**

```bash
cd frontend && node --test tests/tu_dong_khung.test.mjs && npm run kiem && npm run build && npm run kiem-dist
```
Xanh thật: `ℹ tests 7`, `ℹ pass 7` (file test); `npm run kiem` → `ℹ tests 109`, `ℹ pass 109`, `kiem-an-toan: 138 file, không có chèn HTML thô, style tĩnh hay URL ngoài`; `kiem-dist: 2 file JS, 2 file CSS, không thấy eval/inline/style tĩnh/font ngoài`. Test cũ `kho.test.mjs` "SSE: lần mở đầu không tải lại…" vẫn xanh (nối lại SSE **không** thêm lời gọi — đã thử thêm `taiTuDong()` lúc nối lại thì test này đỏ `+ '/api/tu-dong'`, nên bỏ; tab hiện lại thì sự kiện mới tới qua SSE).

- [ ] **Step 5: Commit**

```bash
git add frontend/src/luat_tu_dong.js frontend/src/tam_dung.js frontend/src/thanh/BangTamDung.vue frontend/tests/tu_dong_khung.test.mjs frontend/src/bieu_tuong.js frontend/src/kho.js frontend/src/KhungChinh.vue frontend/src/thanh/ThanhTren.vue frontend/src/thanh/ThanhBen.vue frontend/src/thanh/BangEstop.vue frontend/src/kieu/khung.css
git commit -m "feat(giao-dien): nút TẠM DỪNG toàn trạm + băng vàng, trạng thái tự động chung (TM-4 Task 1)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

### Task 2: Thẻ Dự án — chip tự merge / tự deploy, link "Tự động →"

**Spec:** "Trang tự merge/deploy của dự án" (đi tới được từ trang Dự án), "Dự án khoá ghi" (chip "chỉ quét thử"). **Mockup:** `trang-du-an.js` (`chipTuDong`, `veDuAn`), `them.css` (`.the-phong .ten-lk`, `.tu-dong`); ảnh `anh-du-an.png`, `anh-tam-dung-toan-tram.png`.

**Interfaces:** `theDuAn(d, td = null)` thêm `tuDongDen`, `chipTuDong`, `chipPhu`. Consumes `kho.tuDong` (Task 1); khoá `san_sang`, `dem_hong` của TM-3 (thiếu → không có chip phụ).

- [ ] **Step 1: Viết test**

Bản vá `frontend/tests/du_an.test.mjs`:

```diff
diff --git a/frontend/tests/du_an.test.mjs b/frontend/tests/du_an.test.mjs
index 779ead1..9a885f8 100644
--- a/frontend/tests/du_an.test.mjs
+++ b/frontend/tests/du_an.test.mjs
@@ -26,3 +26,21 @@ test('theDuAn: chưa quét, hết chưa chấm, lỗi gần nhất + loi_doc, ch
   assert.equal(t.loiDoc, 'không đọc được bead')
   assert.equal(t.chiQuetThu, true)
 })
+
+test('TM-4: thẻ dự án có link tên → Công việc, "Tự động →" → /du-an/<ten>, chip tự động và chip phụ', () => {
+  const td = { estop: false, tam_dung_tram: null, du_an: [
+    { ten: 'ben-web', bat_ghi: true, tu_merge: true, tu_deploy: false, du_lenh: true, tam_dung: null,
+      san_sang: true, dem_hong: 3 }] }
+  const t = theDuAn(goc, td)
+  assert.equal(t.tuDongDen, '/du-an/ben-web')
+  assert.deepEqual(t.chipTuDong.map((c) => c.chu), ['tự merge: bật', 'tự deploy: tắt'])
+  assert.deepEqual(t.chipPhu, [{ chu: '1 sẵn sàng deploy', lop: 'pr-mo' },
+    { chu: 'tự deploy đã tự tắt', lop: 'tt-can_nguoi' }])
+  // Chưa đọc được /api/tu-dong hoặc dự án không có trong đó: chỉ còn chip "chỉ quét thử" từ /api/du-an (D37).
+  assert.deepEqual(theDuAn(goc, null).chipTuDong, [])
+  assert.deepEqual(theDuAn(goc, null).chipPhu, [])
+  assert.deepEqual(theDuAn({ ...goc, bat_ghi: false }, null).chipTuDong.map((c) => c.chu), ['chỉ quét thử'])
+  assert.equal(theDuAn({ ...goc, ten: 'a b' }, td).tuDongDen, '/du-an/a%20b')
+  const khongKhoa = { ...td, du_an: [{ ...td.du_an[0], san_sang: false, dem_hong: 0 }] }
+  assert.deepEqual(theDuAn(goc, khongKhoa).chipPhu, [])
+})
```

- [ ] **Step 2: Chạy, mong đợi ĐỎ**

```bash
cd frontend && node --test tests/du_an.test.mjs
```
Đỏ thật: `✖ TM-4: thẻ dự án có link tên → Công việc, "Tự động →" → /du-an/<ten>, chip tự động và chip phụ` — `AssertionError [ERR_ASSERTION]: Expected values to be strictly equal: … actual: undefined` (mong `'/du-an/ben-web'`); `ℹ pass 2`, `ℹ fail 1`.

- [ ] **Step 3: Viết mã**

Bản vá `frontend/src/luat_du_an.js`:

```diff
diff --git a/frontend/src/luat_du_an.js b/frontend/src/luat_du_an.js
index 55c35cf..b8b40a2 100644
--- a/frontend/src/luat_du_an.js
+++ b/frontend/src/luat_du_an.js
@@ -1,12 +1,18 @@
-// Dựng dữ liệu một thẻ dự án từ phần tử /api/du-an (mockup trang.js veDuAn, D36, D37).
+// Dựng dữ liệu một thẻ dự án từ phần tử /api/du-an (mockup trang.js veDuAn, D36, D37) + tóm tắt tự merge/tự deploy
+// của /api/tu-dong (TM-4, mockup 2026-10-18 trang-du-an.js: hàng chip + link "Tự động →").
 import { gioPhut } from './dinh_dang.js'
+import { chipTuDong } from './luat_tu_dong.js'
 
 // Ba chip cột: 1 = ai-lam, 2 = can-chot, 3 = cho-review (mockup đếm cột 1/2/3).
 const COT_CHIP = ['ai-lam', 'can-chot', 'cho-review']
 
-export function theDuAn(d) {
+// `td`: GET /api/tu-dong (null khi chưa đọc được). `san_sang`, `dem_hong`: khoá TM-3 hứa thêm — thiếu thì bỏ chip.
+export function theDuAn(d, td = null) {
   const sb = d.so_bead || {}
   const lg = d.loi_gan_nhat
+  const da = td && (td.du_an || []).find((x) => x.ten === d.ten)
+  const chipPhu = da ? [da.san_sang && { chu: '1 sẵn sàng deploy', lop: 'pr-mo' },
+    da.dem_hong >= 3 && { chu: 'tự deploy đã tự tắt', lop: 'tt-can_nguoi' }].filter(Boolean) : []
   return {
     ten: d.ten,
     den: '/cong-viec?du_an=' + encodeURIComponent(d.ten),
@@ -17,5 +23,8 @@ export function theDuAn(d) {
     loiGanNhat: 'Lỗi gần nhất: ' + (lg ? `${gioPhut(lg.luc)} · ${lg.loi}` : 'không có'),
     loiDoc: d.loi_doc || '',
     chiQuetThu: d.bat_ghi === false, // D37: "chỉ quét thử", không dùng chữ "tạm đóng"
+    tuDongDen: '/du-an/' + encodeURIComponent(d.ten),
+    chipTuDong: da ? chipTuDong(da, td) : chipTuDong(d.bat_ghi === false ? { bat_ghi: false } : null, null),
+    chipPhu,
   }
 }
```

Bản vá `frontend/src/trang/DuAn.vue`:

```diff
diff --git a/frontend/src/trang/DuAn.vue b/frontend/src/trang/DuAn.vue
index 5c00d9b..4597143 100644
--- a/frontend/src/trang/DuAn.vue
+++ b/frontend/src/trang/DuAn.vue
@@ -1,16 +1,16 @@
 <script setup>
-// Trang Dự án — mockup trang.js veDuAn: lưới thẻ, mỗi thẻ dẫn tới /cong-viec?du_an=<ten>.
+// Trang Dự án — mockup trang.js veDuAn: lưới thẻ, tên dẫn tới /cong-viec?du_an=<ten>. TM-4 (mockup 2026-10-18
+// trang-du-an.js, anh-du-an.png): hàng chip tự merge / tự deploy (từ kho.tuDong) + link "Tự động →" sang /du-an/<ten>.
 import { computed, onMounted, ref, watch } from 'vue'
 import { doc } from '../api.js'
 import { kho } from '../kho.js'
 import { theDuAn } from '../luat_du_an.js'
-import { CHU_CHI_QUET_THU } from '../luat.js'
 import DauTrang from '../thanh/DauTrang.vue'
 import '../kieu/du-an.css'
 
 const ds = ref([])
 const loi = ref('')
-const the = computed(() => ds.value.map(theDuAn))
+const the = computed(() => ds.value.map((d) => theDuAn(d, kho.tuDong)))
 
 async function tai() {
   try {
@@ -27,22 +27,25 @@ watch(() => kho.phienBan, tai)
 <template>
   <DauTrang
     tieu-de="Dự án"
-    mo-ta="Các dự án đã thêm vào trạm: số bead mỗi cột, lần quét cuối, lỗi gần nhất."
+    mo-ta="Các dự án đã thêm vào trạm: số bead mỗi cột, lần quét cuối, lỗi gần nhất, tự merge, tự deploy."
   />
   <p v-if="loi" class="loi" role="alert">{{ loi }}</p>
   <p v-if="!the.length && !loi" class="nho">Chưa có dự án nào trong du-an/.</p>
   <div v-if="the.length" class="ds-du-an">
-    <router-link
-      v-for="t in the" :key="t.ten" :to="t.den" class="the the-du-an" :class="{ mo: t.chiQuetThu }"
-    >
-      <div class="dau"><strong>{{ t.ten }}</strong><span class="nho">{{ t.quet }}</span></div>
+    <div v-for="t in the" :key="t.ten" class="the the-du-an" :class="{ mo: t.chiQuetThu }">
+      <div class="dau"><router-link class="ten-lk" :to="t.den">{{ t.ten }}</router-link>
+        <span class="nho">{{ t.quet }}</span></div>
       <div class="ds-chip">
         <span v-for="c in t.chip" :key="c.chu" class="chip">{{ c.chu }}</span>
         <span v-if="t.chuaCham" class="chip">{{ t.chuaCham }}</span>
-        <span v-if="t.chiQuetThu" class="chip" :title="CHU_CHI_QUET_THU">chỉ quét thử</span>
       </div>
       <div class="nho">{{ t.loiGanNhat }}</div>
       <div v-if="t.loiDoc" class="loi">{{ t.loiDoc }}</div>
-    </router-link>
+      <div class="tu-dong">
+        <span v-for="c in [...t.chipTuDong, ...t.chipPhu]" :key="c.chu" class="chip" :class="c.lop"
+              :title="c.title || null">{{ c.chu }}</span>
+        <router-link :to="t.tuDongDen">Tự động →</router-link>
+      </div>
+    </div>
   </div>
 </template>
```

Bản vá `frontend/src/kieu/du-an.css`:

```diff
diff --git a/frontend/src/kieu/du-an.css b/frontend/src/kieu/du-an.css
index cf9330a..dabbd29 100644
--- a/frontend/src/kieu/du-an.css
+++ b/frontend/src/kieu/du-an.css
@@ -1,11 +1,17 @@
-/* Trang Dự án — chép .ds-phong / .the-phong của mockup style.css (mục Văn phòng). */
+/* Trang Dự án — chép .ds-phong / .the-phong của mockup style.css (mục Văn phòng); TM-4: tên là link, hàng tự động
+   (mockup 2026-10-18 them.css `.the-phong .ten-lk`, `.the-phong .tu-dong`). */
 .ds-du-an { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 12px; }
-.the-du-an {
-  cursor: pointer; display: flex; flex-direction: column; gap: 8px; border-left: 6px solid var(--nhan);
-  text-decoration: none; color: inherit;
-}
+.the-du-an { display: flex; flex-direction: column; gap: 8px; border-left: 6px solid var(--nhan); }
 .the-du-an:hover { border-color: var(--vien-dam); border-left-color: var(--nhan); box-shadow: 0 4px 14px #6b4a3014; }
 .the-du-an .dau { display: flex; align-items: center; gap: 8px; }
-.the-du-an .dau strong { font-size: 15.5px; }
 .the-du-an .dau .nho { margin-left: auto; }
 .the-du-an .ds-chip { display: flex; flex-wrap: wrap; gap: 6px; }
+.the-du-an .ten-lk { color: inherit; text-decoration: none; font-weight: 700; font-size: 15.5px; }
+.the-du-an .ten-lk:hover { color: var(--nhan); }
+.the-du-an .tu-dong {
+  display: flex; flex-wrap: wrap; gap: 6px; align-items: center; border-top: 1px dashed var(--vien); padding-top: 8px;
+}
+.the-du-an .tu-dong a {
+  margin-left: auto; font-size: 13px; font-weight: 600; color: var(--nhan); text-decoration: none;
+}
+.the-du-an .tu-dong a:hover { text-decoration: underline; }
```

- [ ] **Step 4: Chạy, mong đợi XANH**

```bash
cd frontend && node --test tests/du_an.test.mjs && npm run kiem && npm run build && npm run kiem-dist
```
Xanh thật: `ℹ pass 3` (file test); `npm run kiem` → `ℹ tests 110`, `ℹ pass 110`; `kiem-dist` sạch.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/luat_du_an.js frontend/src/trang/DuAn.vue frontend/src/kieu/du-an.css frontend/tests/du_an.test.mjs
git commit -m "feat(giao-dien): thẻ Dự án có chip tự merge/tự deploy và link Tự động (TM-4 Task 2)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

### Task 3: Luật trang Tự động — hỏi lại, thân POST, khối báo, sẵn sàng deploy, chờ Đại ca, lịch sử

**Spec:** "Trang tự merge/deploy của dự án", "Bật công tắc cần xác nhận" (câu "Trạm sẽ tự đưa bản mới lên cho khách dùng, không chờ Đại ca. Bật?"), "TẠM DỪNG theo dự án", "Estop…" ("Estop đang bật"), `tu-deploy` "Ba lệnh" ("Chưa khai đủ 3 lệnh"), "Một chuỗi một lúc" ("gồm 3 việc đã merge"), "Lùi cũng hỏng…", "Kết quả … không rõ…", "Hỏng 3 lần…", "Xem lịch sử đổi"; `tu-merge` "Thiếu điều kiện thì chờ Đại ca…". **Mockup:** `trang-tu-dong.js` (`veBao`, `veSanSang`, `veCho`, `veLichSu`, `veDemHong`, `veCaiDat`, các `confirm`), `du-lieu.js` (`DIEU_KIEN`, `LENH`, `LOAI_SU_KIEN`, `LICH_SU_DOI`).

**Interfaces:** `luat_trang_tu_dong.js`: `DIEU_KIEN`, `LENH`, `CHUA_CO`, `ma7`, `hoiCongTac(ma, bat, ten)`, `hoiTamDung(ten)`, `hoiDeploy(ten, commit)`, `hoiLuuLenh(tatTuDeploy)`, `doiCongTac(ma, bat)`, `doiLenh(cd, moi)`, `thanCaiDat(cd, doi)`, `lyDoKhoaDeploy(dl, laDaiCa)`, `sanSang(dl, laDaiCa)`, `choDaiCa(dl)`. `luat_bao_tu_dong.js`: `gioTuTat(lichSuDoi)`, `baoTuDong(dl) -> [{lop, tieuDe, than: [[chữ, mono]], nut}]`. `luat_lich_su_tu_dong.js`: `dongLichSu(r)`, `demHong(n)`, `tenTacNhan(t)`, `dongLichSuDoi(r)`, `doiCuoi(ds)`. Không import vòng (`luat_lich_su` → `luat_trang`; `luat_bao` → `luat_tu_dong`).

- [ ] **Step 1: Viết test**

Tạo mới `frontend/tests/tu_dong_trang.test.mjs` (nguyên văn):

```js
import assert from 'node:assert/strict'
import { test } from 'node:test'
import { CHU_CHI_QUET_THU } from '../src/luat.js'
import { CHU_CHI_DOC } from '../src/luat_tu_dong.js'
import { baoTuDong } from '../src/luat_bao_tu_dong.js'
import { DIEU_KIEN, LENH, choDaiCa, doiCongTac, doiLenh, hoiCongTac, hoiDeploy, hoiLuuLenh, hoiTamDung,
  lyDoKhoaDeploy, ma7, sanSang, thanCaiDat } from '../src/luat_trang_tu_dong.js'

const LENH_DU = { deploy: '/Users/Shared/tram-deploy/repo-nhap/deploy.sh',
  kiem_song: '/Users/Shared/tram-deploy/repo-nhap/kiem-song.sh', lui: '/Users/Shared/tram-deploy/repo-nhap/lui.sh' }
const CD = { tu_merge: true, tu_deploy: false, dieu_kien: { ci: true, cot: true, hang_rao: true }, lenh: LENH_DU }
// GET /api/du-an/repo-nhap/tu-dong: khoá TM-1 + khoá TM-2/TM-3 hứa thêm (cho_dai_ca, san_sang, dang_deploy, dem_hong).
const DL = { du_an: 'repo-nhap', bat_ghi: true, estop: false, chi_tam_dung: false, tam_dung_tram: null, tam_dung: null,
  cai_dat: CD, du_lenh: true, phien_ban: '41', lich_su_doi: [], dem_hong: 1, dang_deploy: null,
  san_sang: { commit: 'a41c07e9d2b8c0ffee', so_merge: 2, bead_ids: ['rn-11', 'rn-12'], luc: '2026-10-18T14:52:00Z',
    commit_dang_chay: '5d3e8b2aa' },
  // TM-2 (`tram/suy/tu_merge.py`): {bead_id, tieu_de, luc, ly_do: [{ma, nhan, muc}]}, muc ∈ loi | tat | can_nguoi.
  cho_dai_ca: [{ bead_id: 'rn-15', tieu_de: 'Làm tròn tổng tiền hoá đơn', luc: '2026-10-18T14:00:00Z',
    ly_do: [{ ma: 'hang_rao_tien', nhan: 'Chạm hàng rào: tiền/giá', muc: 'can_nguoi' },
      { ma: 'schema_duong_dan', nhan: 'Cấu trúc DB — luôn chờ Đại ca', muc: 'loi' },
      { ma: 'ci_dang_chay', nhan: 'CI đang chạy — xét lại vòng sau', muc: 'tat' },
      { ma: 'ma_moi', nhan: 'Mã lạ', muc: 'khac' }] }] }

test('hằng theo mockup: 5 điều kiện (2 luôn bật), 3 lệnh; mã commit 7 ký tự', () => {
  assert.deepEqual(DIEU_KIEN.map((d) => [d.ma, Boolean(d.khoa)]),
    [['qc', true], ['kiem_lai', true], ['ci', false], ['cot', false], ['hang_rao', false]])
  assert.equal(DIEU_KIEN[3].ten, 'Việc ở cột "AI tự làm"')
  assert.deepEqual(LENH.map((l) => l.ma), ['deploy', 'kiem_song', 'lui'])
  assert.equal(ma7('a41c07e9d2b8'), 'a41c07e')
  assert.equal(ma7(null), '—')
})

test('hỏi lại: bật tự merge/tự deploy, tắt công tắc, tắt điều kiện; bật lại điều kiện không hỏi', () => {
  assert.equal(hoiCongTac('tu_deploy', true, 'repo-nhap'),
    'Trạm sẽ tự đưa bản mới lên cho khách dùng, không chờ Đại ca. Bật?')
  assert.match(hoiCongTac('tu_merge', true, 'repo-nhap'), /^Bật tự merge cho repo-nhap\? Trạm sẽ tự gộp PR/)
  assert.match(hoiCongTac('tu_merge', false, 'repo-nhap'), /^Tắt tự merge của repo-nhap\?/)
  assert.match(hoiCongTac('tu_deploy', false, 'repo-nhap'), /^Tắt tự deploy của repo-nhap\?/)
  assert.equal(hoiCongTac('ci', false, 'repo-nhap'),
    'Tắt điều kiện "CI GitHub xanh"? Trạm sẽ tự merge cả việc không đạt điều kiện này.')
  assert.equal(hoiCongTac('ci', true, 'repo-nhap'), '')
  assert.equal(hoiTamDung('repo-nhap'),
    'Tạm dừng tự merge và tự deploy của repo-nhap? Cài đặt giữ nguyên; bấm Tiếp tục để chạy lại.')
  assert.equal(hoiDeploy('repo-nhap', 'a41c07e9d2'), 'Deploy bản a41c07e của repo-nhap lên cho khách dùng?\n'
    + 'Trạm chạy lệnh deploy rồi lệnh kiểm còn sống; hỏng thì tự lùi.')
  assert.equal(hoiLuuLenh(false), 'Lưu 3 lệnh? Lệnh sẽ chạy trên máy B dưới tài khoản trạm.')
  assert.match(hoiLuuLenh(true), /\nThiếu lệnh nên tự deploy sẽ tắt\.$/)
})

test('thân POST cài đặt luôn đủ khoá: đổi một công tắc / điều kiện / ba lệnh trên bản đang xem', () => {
  assert.deepEqual(thanCaiDat(CD, doiCongTac('tu_deploy', true)), { ...CD, tu_deploy: true })
  assert.deepEqual(thanCaiDat(CD, doiCongTac('cot', false)),
    { ...CD, dieu_kien: { ci: true, cot: false, hang_rao: true } })
  const moi = { deploy: ' make deploy ', kiem_song: 'sh kiem.sh', lui: 'sh lui.sh' }
  assert.deepEqual(doiLenh(CD, moi), { lenh: { deploy: 'make deploy', kiem_song: 'sh kiem.sh', lui: 'sh lui.sh' } })
  const bat = { ...CD, tu_deploy: true }
  assert.deepEqual(doiLenh(bat, { ...moi, lui: '  ' }),
    { lenh: { deploy: 'make deploy', kiem_song: 'sh kiem.sh', lui: '' }, tu_deploy: false })   // thiếu lệnh → tắt
  assert.deepEqual(thanCaiDat(bat, doiLenh(bat, { ...moi, lui: '' })).tu_deploy, false)
})

test('khối báo: chỉ quét thử, cửa tạm, estop, tạm dừng (Đại ca / lùi hỏng / không rõ), trạm tự tắt', () => {
  assert.deepEqual(baoTuDong(DL), [])
  const qt = baoTuDong({ ...DL, bat_ghi: false })
  assert.equal(qt[0].tieuDe, 'Dự án đang chỉ quét thử')
  assert.deepEqual(qt[0].than.filter((p) => p[1]).map((p) => p[0]), ['bat_ghi: false', 'du-an/repo-nhap.yaml'])
  assert.equal(baoTuDong({ ...DL, chi_tam_dung: true })[0].tieuDe, 'Cửa ghi còn tạm — chỉ bấm được TẠM DỪNG')
  assert.deepEqual(baoTuDong({ ...DL, estop: true }).map((b) => [b.lop, b.tieuDe]), [['do', 'Estop đang bật']])
  const td = (boi, ly_do) => baoTuDong({ ...DL, tam_dung: { boi, luc: '2026-10-18T20:12:00Z', ly_do } })[0]
  const daiCa = td('dai-ca/dashboard', '')
  assert.deepEqual([daiCa.lop, daiCa.tieuDe, daiCa.nut], ['', 'Dự án đang tạm dừng', 'Tiếp tục'])
  assert.match(daiCa.than[0][0], /^Đại ca bấm lúc 03:12\. Trạm vẫn giao việc và mở PR/)
  const lui = td('tram/tu-deploy', 'lui-hong')
  assert.deepEqual([lui.lop, lui.tieuDe, lui.nut],
    ['do', 'LÙI HỎNG lúc 03:12 — trang của khách có thể đang chết', 'Tiếp tục dự án'])
  assert.deepEqual([td('tram/tu-deploy', 'khong-ro').lop, td('tram/tu-deploy', 'khong-ro').tieuDe],
    ['do', 'Deploy không rõ kết quả lúc 03:12 — cần Đại ca kiểm'])
  const tat = baoTuDong({ ...DL, dem_hong: 3, lich_su_doi: [
    { luc: '2026-10-18T19:41:00Z', tac_nhan: 'tram/tu-deploy',
      doi: [{ truong: 'tu_deploy', truoc: true, sau: false }] }] })
  assert.equal(tat[0].tieuDe, 'Trạm đã tự tắt tự deploy lúc 02:41')
  assert.equal(baoTuDong({ ...DL, dem_hong: 3 })[0].tieuDe, 'Trạm đã tự tắt tự deploy')
  assert.deepEqual(baoTuDong({ ...DL, dem_hong: 3, cai_dat: { ...CD, tu_deploy: true } }), [])
})

test('sẵn sàng deploy: một hàng cho commit mới nhất, khoá Deploy theo thứ tự estop → thiếu lệnh → khoá ghi', () => {
  const s = sanSang(DL, true)
  assert.equal(s.phu, 'tự deploy đang tắt — trạm chờ Đại ca bấm')
  assert.deepEqual(s.ban, { commit: 'a41c07e', soMerge: 2, bead: 'rn-11, rn-12', luc: '21:52', dangChay: '5d3e8b2' })
  assert.equal(s.lyDo, '')
  assert.equal(sanSang({ ...DL, cai_dat: { ...CD, tu_deploy: true } }, true).phu,
    'tự deploy đang bật — trạm tự chạy sau mỗi lần merge')
  assert.equal(sanSang({ ...DL, san_sang: null }, true).rong, 'Không có bản nào chờ deploy.')
  assert.equal(sanSang({ ...DL, san_sang: undefined }, true).chuaCo, true)
  // TM-3 (`tram/deploy/hien_thi.dang_deploy`): trang_thai "cho" = Đại ca vừa bấm, pha deploy chưa nhận; "chay".
  const dd = (trang_thai, nguon = 'dai_ca') => sanSang({ ...DL, san_sang: null,
    dang_deploy: { trang_thai, commit: 'a41c07e9', nguon, luc: '2026-10-18T15:20:00Z' } }, true).dangDeploy
  assert.deepEqual(dd('chay'), { commit: 'a41c07e', nguon: 'Đại ca bấm', luc: '22:20', cho: false })
  assert.deepEqual(dd('cho'), { commit: 'a41c07e', nguon: 'Đại ca bấm', luc: '22:20', cho: true })
  assert.equal(dd('chay', 'tu_dong').nguon, 'tự deploy')
  assert.equal(lyDoKhoaDeploy({ ...DL, estop: true, du_lenh: false }, false), 'Estop đang bật')
  assert.equal(lyDoKhoaDeploy({ ...DL, du_lenh: false }, false), 'Chưa khai đủ 3 lệnh')
  assert.equal(lyDoKhoaDeploy({ ...DL, chi_tam_dung: true }, true), 'Cửa ghi đang khoá')
  assert.equal(lyDoKhoaDeploy(DL, false), CHU_CHI_DOC)
  assert.equal(lyDoKhoaDeploy({ ...DL, bat_ghi: false }, true), CHU_CHI_QUET_THU)
  assert.equal(lyDoKhoaDeploy({ ...DL, tam_dung: { boi: 'x', luc: '', ly_do: '' } }, true), '')   // D97: vẫn bấm được
})

test('chờ Đại ca: câu của máy chủ, màu theo `muc` (loi đỏ, tat xám, còn lại cần người); thiếu khoá → null', () => {
  assert.deepEqual(choDaiCa(DL), [{ bead: 'rn-15', tieuDe: 'Làm tròn tổng tiền hoá đơn', lyDo: [
    { chu: 'Chạm hàng rào: tiền/giá', lop: 'tt-can_nguoi' }, { chu: 'Cấu trúc DB — luôn chờ Đại ca', lop: 'tt-loi' },
    { chu: 'CI đang chạy — xét lại vòng sau', lop: 'tt-tat' }, { chu: 'Mã lạ', lop: 'tt-can_nguoi' }] }])
  assert.equal(choDaiCa({ ...DL, cho_dai_ca: undefined }), null)
  assert.deepEqual(choDaiCa({ ...DL, cho_dai_ca: [] }), [])
})
```

Tạo mới `frontend/tests/tu_dong_lich_su.test.mjs` (nguyên văn):

```js
import assert from 'node:assert/strict'
import { test } from 'node:test'
import { demHong, doiCuoi, dongLichSu, dongLichSuDoi, tenTacNhan } from '../src/luat_lich_su_tu_dong.js'
import { gioTuTat } from '../src/luat_bao_tu_dong.js'

test('lịch sử gần đây: nhãn + màu theo loại như mockup, giờ VN, commit 7 ký tự, "Ai" bằng lời', () => {
  assert.deepEqual(dongLichSu({ luc: '2026-10-18T09:30:00Z', loai: 'deploy_lui', bead_id: null,
    commit: '77f0a19c3d', chi_tiet: 'kiểm còn sống: mã thoát 22 · 34 giây → lùi về 5d3e8b2: đạt', ai: 'dai_ca_bam' }),
  { gio: '16:30', nhan: 'Hỏng · đã tự lùi', lop: 'tt-cau_dao', bead: '—', commit: '77f0a19',
    chiTiet: 'kiểm còn sống: mã thoát 22 · 34 giây → lùi về 5d3e8b2: đạt', ai: 'Đại ca bấm' })
  const nhan = (loai) => { const d = dongLichSu({ luc: '', loai, ai: 'tram' }); return [d.nhan, d.lop, d.ai] }
  assert.deepEqual(nhan('tu_merge'), ['Tự merge', 'pr-da_merge', 'trạm'])
  assert.deepEqual(nhan('san_sang'), ['Sẵn sàng deploy', 'pr-mo', 'trạm'])
  assert.deepEqual(nhan('deploy_dat'), ['Deploy xong', 'tt-lam', 'trạm'])
  assert.deepEqual(nhan('lui_hong'), ['LÙI HỎNG', 'tt-loi', 'trạm'])
  assert.deepEqual(nhan('khong_ro'), ['Không rõ kết quả', 'tt-loi', 'trạm'])
  assert.deepEqual(nhan('tu_tat'), ['Tự tắt tự deploy', 'tt-can_nguoi', 'trạm'])
  assert.deepEqual(nhan('tam_dung'), ['Tạm dừng', 'tt-tat', 'trạm'])
  assert.deepEqual(nhan('huy'), ['Deploy bị huỷ', 'tt-tat', 'trạm'])   // TM-3 câu hỏi 5 (a): `deploy.huy` vào lịch sử
  assert.deepEqual(nhan('la'), ['la', '', 'trạm'])
  assert.equal(dongLichSu({ loai: 'deploy_dat', ai: 'tu_deploy' }).ai, 'tự deploy')
  assert.equal(dongLichSu({ loai: 'san_sang', ai: 'dai_ca' }).ai, 'Đại ca')
  assert.equal(dongLichSu({ loai: 'tu_merge', bead_id: 'rn-12', commit: null }).bead, 'rn-12')
})

test('bộ đếm hỏng liên tiếp: ba đèn, chữ "n / 3"; thiếu khoá → null', () => {
  assert.deepEqual(demHong(1), { den: ['thieu', 'cho', 'cho'], chu: '1 / 3' })
  assert.deepEqual(demHong(3), { den: ['thieu', 'thieu', 'thieu'], chu: '3 / 3' })
  assert.deepEqual(demHong(0), { den: ['cho', 'cho', 'cho'], chu: '0 / 3' })
  assert.equal(demHong(undefined), null)
})

test('lịch sử đổi cài đặt: ai, giờ, việc bằng lời, trước → sau (lệnh rút gọn, trống)', () => {
  assert.equal(tenTacNhan('dai-ca/dashboard'), 'Đại ca (dashboard)')
  assert.equal(tenTacNhan('tram/tu-deploy'), 'trạm')
  assert.equal(tenTacNhan('khac'), 'khac')
  assert.deepEqual(dongLichSuDoi({ luc: '2026-10-18T02:12:00Z', tac_nhan: 'dai-ca/dashboard',
    doi: [{ truong: 'tu_merge', truoc: false, sau: true }] }),
  { gio: '18/10 09:12', ai: 'Đại ca (dashboard)', viec: 'Bật tự merge', doi: 'tắt → bật' })
  assert.deepEqual(dongLichSuDoi({ luc: '2026-10-18T02:04:00Z', tac_nhan: 'dai-ca/dashboard', doi: [
    { truong: 'lenh_deploy', truoc: '', sau: '/Users/Shared/tram-deploy/repo-nhap/deploy.sh' },
    { truong: 'lenh_lui', truoc: '', sau: 'sh scripts/lui.sh' }] }),
  { gio: '18/10 09:04', ai: 'Đại ca (dashboard)', viec: 'Sửa lệnh deploy, lệnh lùi',
    doi: 'trống → …/deploy.sh, trống → …/lui.sh' })
  assert.deepEqual(dongLichSuDoi({ luc: '2026-10-17T15:40:00Z', tac_nhan: 'tram/tu-deploy', doi: [
    { truong: 'dk_cot', truoc: true, sau: false }, { truong: 'tu_deploy', truoc: true, sau: false }] }),
  { gio: '17/10 22:40', ai: 'trạm', viec: 'Tắt nút "Việc ở cột AI tự làm", Tắt tự deploy',
    doi: 'bật → tắt, bật → tắt' })
  const xoa = { luc: '', tac_nhan: 'x', doi: [{ truong: 'lenh_kiem_song', truoc: 'make kiem', sau: '' }] }
  assert.equal(dongLichSuDoi(xoa).doi, 'make kiem → trống')
})

test('đổi lần cuối và giờ trạm tự tắt tự deploy (dòng mới nhất do trạm tắt tu_deploy)', () => {
  const ds = [{ luc: '2026-10-18T19:41:00Z', tac_nhan: 'tram/tu-deploy', doi: [{ truong: 'tu_deploy', truoc: true,
    sau: false }] }, { luc: '2026-10-18T02:12:00Z', tac_nhan: 'dai-ca/dashboard', doi: [] }]
  assert.equal(doiCuoi(ds), 'Đổi lần cuối: trạm · 19/10 02:41')
  assert.equal(doiCuoi([]), 'Chưa từng đổi — đang dùng mặc định')
  assert.equal(doiCuoi(undefined), 'Chưa từng đổi — đang dùng mặc định')
  assert.equal(gioTuTat(ds), '02:41')
  assert.equal(gioTuTat(ds.slice(1)), '')
  assert.equal(gioTuTat(undefined), '')
})
```

- [ ] **Step 2: Chạy, mong đợi ĐỎ**

```bash
cd frontend && node --test tests/tu_dong_trang.test.mjs tests/tu_dong_lich_su.test.mjs
```
Đỏ thật: `Error [ERR_MODULE_NOT_FOUND]: Cannot find module '…/frontend/src/luat_lich_su_tu_dong.js' imported from …/frontend/tests/tu_dong_lich_su.test.mjs` và `Error [ERR_MODULE_NOT_FOUND]: Cannot find module '…/frontend/src/luat_bao_tu_dong.js' imported from …/frontend/tests/tu_dong_trang.test.mjs` — `ℹ tests 2`, `ℹ fail 2`.

- [ ] **Step 3: Viết mã**

Tạo mới `frontend/src/luat_trang_tu_dong.js` (nguyên văn):

```js
// Luật trang Tự động của một dự án `#/du-an/<ten>` (mockup 2026-10-18 trang-tu-dong.js, anh-tu-dong*.png; spec
// dieu-khien-tu-dong "Trang tự merge/deploy của dự án", "Bật công tắc cần xác nhận"; tu-deploy) — thuần. Khoá TM-2/TM-3
// (`cho_dai_ca`, `san_sang`, `dang_deploy`, `lich_su`, `dem_hong`) thiếu → "chưa có dữ liệu", không đoán.
import { gioPhut } from './dinh_dang.js'
import { CHU_CUA_TAM, lyDoKhoaGhi } from './luat_tu_dong.js'

export const DIEU_KIEN = [
  { ma: 'qc', ten: 'QC đạt', mo_ta: 'Một agent khác agent đã code kiểm và kết luận đạt', khoa: true },
  { ma: 'kiem_lai', ten: 'Kiểm lại đạt', mo_ta: 'Trạm tự chạy lại lệnh kiểm trong vùng cách ly', khoa: true },
  { ma: 'ci', ten: 'CI GitHub xanh', ngan: 'CI GitHub xanh',
    mo_ta: 'Mọi kiểm tra tự động trên GitHub đã chạy xong và đạt' },
  { ma: 'cot', ten: 'Việc ở cột "AI tự làm"', ngan: 'Việc ở cột AI tự làm',
    mo_ta: 'Việc đi từ cột 1, Đại ca không tự gán cột' },
  { ma: 'hang_rao', ten: 'Không chạm hàng rào', ngan: 'Không chạm hàng rào',
    mo_ta: 'Tiền/giá · quyền/bảo mật · thứ khách thấy' },
]
export const LENH = [
  { ma: 'deploy', ten: 'Lệnh deploy', ngan: 'lệnh deploy', goi_y: 'đưa bản mới lên' },
  { ma: 'kiem_song', ten: 'Lệnh kiểm còn sống', ngan: 'lệnh kiểm còn sống', goi_y: 'chạy sau deploy, thoát 0 = sống' },
  { ma: 'lui', ten: 'Lệnh lùi về bản trước', ngan: 'lệnh lùi', goi_y: 'chạy khi deploy hỏng' },
]
export const CHUA_CO = 'Chưa có dữ liệu — phần này của trạm chưa chạy.'
export const ma7 = (c) => (c ? String(c).slice(0, 7) : '—')
const dk = (ma) => DIEU_KIEN.find((d) => d.ma === ma)

// Hỏi lại trước khi gửi: bật tự merge/tự deploy, lưu ba lệnh (spec "Bật công tắc cần xác nhận"); tắt công tắc, tắt
// điều kiện, TẠM DỪNG — một lần bấm + xác nhận như estop. Bật lại điều kiện (chiều chặt hơn) không hỏi ('').
export function hoiCongTac(ma, bat, ten) {
  if (ma === 'tu_merge') {
    return bat ? `Bật tự merge cho ${ten}? Trạm sẽ tự gộp PR vào nhánh chính khi đủ mọi điều kiện, `
      + 'không chờ Đại ca.'
      : `Tắt tự merge của ${ten}? Việc xong sẽ chờ Đại ca merge như trước.`
  }
  if (ma === 'tu_deploy') {
    return bat ? 'Trạm sẽ tự đưa bản mới lên cho khách dùng, không chờ Đại ca. Bật?'
      : `Tắt tự deploy của ${ten}? Bản mới sẽ chờ ở "Sẵn sàng deploy" cho Đại ca bấm.`
  }
  return bat ? '' : `Tắt điều kiện "${dk(ma).ngan}"? Trạm sẽ tự merge cả việc không đạt điều kiện này.`
}
export const hoiTamDung = (ten) =>
  `Tạm dừng tự merge và tự deploy của ${ten}? Cài đặt giữ nguyên; bấm Tiếp tục để chạy lại.`
export const hoiDeploy = (ten, commit) => `Deploy bản ${ma7(commit)} của ${ten} lên cho khách dùng?\n`
  + 'Trạm chạy lệnh deploy rồi lệnh kiểm còn sống; hỏng thì tự lùi.'
export const hoiLuuLenh = (tatTuDeploy) => 'Lưu 3 lệnh? Lệnh sẽ chạy trên máy B dưới tài khoản trạm.'
  + (tatTuDeploy ? '\nThiếu lệnh nên tự deploy sẽ tắt.' : '')

// Thân POST …/tu-dong/cai-dat luôn mang ĐỦ cài đặt (TM-1 `ThanCaiDat`): bản đang xem + phần đổi.
export const doiCongTac = (ma, bat) => (ma === 'tu_merge' || ma === 'tu_deploy' ? { [ma]: bat }
  : { dieu_kien: { [ma]: bat } })
export function doiLenh(cd, moi) {
  const lenh = Object.fromEntries(LENH.map((l) => [l.ma, String(moi[l.ma] ?? '').trim()]))
  return cd.tu_deploy && LENH.some((l) => !lenh[l.ma]) ? { lenh, tu_deploy: false } : { lenh }
}
export const thanCaiDat = (cd, doi) => ({ ...cd, ...doi, dieu_kien: { ...cd.dieu_kien, ...doi.dieu_kien },
  lenh: { ...cd.lenh, ...doi.lenh } })

// Khoá nút Deploy (mockup: estop → thiếu lệnh → cửa ghi). Tạm dừng KHÔNG khoá (D97: Deploy tay vẫn dùng được).
export function lyDoKhoaDeploy(dl, laDaiCa) {
  if (dl.estop) return 'Estop đang bật'
  if (!dl.du_lenh) return 'Chưa khai đủ 3 lệnh'
  if (dl.dang_deploy) return 'Đang có một lần deploy chạy'
  const k = lyDoKhoaGhi(dl, laDaiCa)
  return k === CHU_CUA_TAM ? 'Cửa ghi đang khoá' : k
}

// Khối "Sẵn sàng deploy": một hàng cho commit mới nhất (TM-3 gộp nhiều merge), hoặc hàng "đang deploy" (`cho`: Đại ca
// vừa bấm, pha deploy của trạm chưa nhận — TM-3 `dang_deploy.trang_thai`).
export function sanSang(dl, laDaiCa) {
  const phu = dl.cai_dat.tu_deploy ? 'tự deploy đang bật — trạm tự chạy sau mỗi lần merge'
    : 'tự deploy đang tắt — trạm chờ Đại ca bấm'
  if (dl.san_sang === undefined) return { phu, chuaCo: true }
  const ss = dl.san_sang
  const dd = dl.dang_deploy
  return { phu, lyDo: lyDoKhoaDeploy(dl, laDaiCa), rong: !ss && !dd ? 'Không có bản nào chờ deploy.' : '',
    ban: ss ? { commit: ma7(ss.commit), soMerge: ss.so_merge, bead: (ss.bead_ids || []).join(', '),
      luc: gioPhut(ss.luc), dangChay: ss.commit_dang_chay ? ma7(ss.commit_dang_chay) : '' } : null,
    dangDeploy: dd ? { commit: ma7(dd.commit), nguon: dd.nguon === 'dai_ca' ? 'Đại ca bấm' : 'tự deploy',
      luc: gioPhut(dd.luc), cho: dd.trang_thai === 'cho' } : null }
}

// "Chờ Đại ca" (TM-2 `cho_dai_ca`: {bead_id, tieu_de, luc, ly_do: [{ma, nhan, muc}]}): lý do là câu của máy chủ;
// màu theo `muc` của máy chủ (`tu_merge_xet.MUC`) — loi đỏ (luôn chờ: cấu trúc DB, không đọc được diff, tự merge
// lỗi), tat xám (CI đang chạy), còn lại "cần người". Thiếu khoá → null ("chưa có dữ liệu").
const LOP_MUC = { loi: 'tt-loi', tat: 'tt-tat' }
export function choDaiCa(dl) {
  if (!Array.isArray(dl.cho_dai_ca)) return null
  return dl.cho_dai_ca.map((c) => ({ bead: c.bead_id, tieuDe: c.tieu_de || '',
    lyDo: (c.ly_do || []).map((l) => ({ chu: l.nhan, lop: LOP_MUC[l.muc] ?? 'tt-can_nguoi' })) }))
}
```

Tạo mới `frontend/src/luat_bao_tu_dong.js` (nguyên văn):

```js
// Khối báo đầu trang Tự động (mockup 2026-10-18 trang-tu-dong.js `veBao`; ảnh anh-hr-codex-khoa.png,
// anh-tu-dong-cua-tam.png, anh-tu-dong-lui-hong.png, anh-tu-dong-tu-tat.png) — thuần.
// `than`: danh sách [chữ, mono?] để trang vẽ bằng {{ }} (không chèn HTML).
import { gioPhut } from './dinh_dang.js'
import { CHU_CUA_TAM } from './luat_tu_dong.js'

// Giờ trạm tự tắt tự deploy: dòng `lich_su_doi` mới nhất do trạm (`tram/…`) đổi tu_deploy sang tắt; không có → ''.
export function gioTuTat(ds) {
  const r = (ds || []).find((x) => String(x.tac_nhan).startsWith('tram/')
    && x.doi.some((d) => d.truong === 'tu_deploy' && d.sau === false))
  return r ? gioPhut(r.luc) : ''
}

const doan = (...p) => p.map((x, i) => [x, i % 2 === 1])      // đoạn lẻ hiện chữ mono
const bao = (lop, tieuDe, than, nut = '') => ({ lop, tieuDe, than, nut })

function baoTamDung(td) {
  const gio = gioPhut(td.luc)
  if (td.ly_do === 'lui-hong') {
    return bao('do', `LÙI HỎNG lúc ${gio} — trang của khách có thể đang chết`, doan('Deploy hỏng, trạm đã chạy '
      + 'lệnh lùi nhưng kiểm còn sống vẫn không đạt. Trạm đã tắt tự deploy và tạm dừng dự án này. Telegram đã báo '
      + 'khẩn. Đại ca kiểm trang, sửa tay, rồi bấm Tiếp tục.'), 'Tiếp tục dự án')
  }
  if (td.ly_do === 'khong-ro') {
    return bao('do', `Deploy không rõ kết quả lúc ${gio} — cần Đại ca kiểm`, doan('Trạm tắt hay máy khởi động lại giữa '
      + 'lúc deploy. Trạm không tự chạy lại lệnh deploy hay lệnh lùi và đã tạm dừng dự án này. Đại ca kiểm trang của '
      + 'khách, rồi bấm Tiếp tục.'), 'Tiếp tục dự án')
  }
  const ai = String(td.boi).startsWith('tram/') ? 'Trạm' : String(td.boi).startsWith('dai-ca') ? 'Đại ca' : td.boi
  return bao('', 'Dự án đang tạm dừng', doan(`${ai} bấm lúc ${gio}. Trạm vẫn giao việc và mở PR, nhưng không tự merge, `
    + 'không tự deploy. Cài đặt bên dưới giữ nguyên. Nút Deploy của Đại ca vẫn dùng được.'), 'Tiếp tục')
}

// Khối báo đầu trang (mockup veBao), theo thứ tự: chỉ quét thử, cửa tạm, estop, tạm dừng dự án, trạm tự tắt.
export function baoTuDong(dl) {
  const ra = []
  if (dl.bat_ghi === false) {
    ra.push(bao('', 'Dự án đang chỉ quét thử', doan('Khoá ghi ', 'bat_ghi: false', ' — không bật được tự merge hay tự '
      + 'deploy. Đại ca bật ghi bằng tay trong ', `du-an/${dl.du_an}.yaml`, ' sau các cổng chạy thật. Nút tạm dừng vẫn '
      + 'bấm được.')))
  }
  if (dl.chi_tam_dung) {
    ra.push(bao('', CHU_CUA_TAM, doan('Trạm chưa chuyển cửa ghi sang loại chắc chắn (', 'unix-socket', '). Lúc này một '
      + 'chương trình trên máy B có thể giả là Đại ca, nên mọi nút bật và ô sửa ở đây bị khoá.')))
  }
  if (dl.estop) ra.push(bao('do', 'Estop đang bật', doan('Không tự merge, không tự deploy, nút Deploy cũng bị khoá.')))
  if (dl.tam_dung) ra.push(baoTamDung(dl.tam_dung))
  if (!dl.cai_dat.tu_deploy && dl.dem_hong >= 3) {
    const gio = gioTuTat(dl.lich_su_doi)
    ra.push(bao('', `Trạm đã tự tắt tự deploy${gio ? ` lúc ${gio}` : ''}`, doan('Hỏng 3 lần liên tiếp, lần nào cũng đã '
      + 'tự lùi thành công. Tự merge vẫn chạy; bản mới sẽ chờ ở "Sẵn sàng deploy". Bật lại tự deploy khi Đại ca đã '
      + 'kiểm — bộ đếm về 0.')))
  }
  return ra
}
```

Tạo mới `frontend/src/luat_lich_su_tu_dong.js` (nguyên văn):

```js
// Luật hiển thị lịch sử của trang Tự động (mockup 2026-10-18 du-lieu.js LOAI_SU_KIEN, trang-tu-dong.js veLichSu,
// veDemHong, ngăn "Lịch sử đổi cài đặt") — thuần. Máy chủ dựng `chi_tiet` (chỉ mã thoát, thời gian — không có log);
// ở đây chỉ chọn nhãn, màu, giờ VN và ghép câu.
import { gioPhut, ngayGio } from './dinh_dang.js'
import { DIEU_KIEN, LENH, ma7 } from './luat_trang_tu_dong.js'

// loai (TM-3 `tram/deploy/hien_thi.LOAI_LICH_SU`) → [nhãn, lớp chip]; loại lạ hiện nguyên mã, không màu.
const LOAI = {
  tu_merge: ['Tự merge', 'pr-da_merge'], san_sang: ['Sẵn sàng deploy', 'pr-mo'], deploy_dat: ['Deploy xong', 'tt-lam'],
  deploy_lui: ['Hỏng · đã tự lùi', 'tt-cau_dao'], lui_hong: ['LÙI HỎNG', 'tt-loi'],
  khong_ro: ['Không rõ kết quả', 'tt-loi'], tu_tat: ['Tự tắt tự deploy', 'tt-can_nguoi'],
  tam_dung: ['Tạm dừng', 'tt-tat'], huy: ['Deploy bị huỷ', 'tt-tat'],     // huy: TM-3 câu hỏi 5 (a), `deploy.huy`
}
const AI = { dai_ca: 'Đại ca', dai_ca_bam: 'Đại ca bấm', tu_deploy: 'tự deploy', tram: 'trạm' }

export function dongLichSu(r) {
  const [nhan, lop] = LOAI[r.loai] ?? [r.loai, '']
  return { gio: gioPhut(r.luc), nhan, lop, bead: r.bead_id || '—', commit: ma7(r.commit), chiTiet: r.chi_tiet || '',
    ai: AI[r.ai] ?? r.ai ?? '' }
}

export function demHong(n) {
  if (typeof n !== 'number') return null
  return { den: [0, 1, 2].map((i) => (i < n ? 'thieu' : 'cho')), chu: `${n} / 3` }
}

export function tenTacNhan(t) {
  if (t === 'dai-ca/dashboard') return 'Đại ca (dashboard)'
  if (String(t).startsWith('dai-ca')) return 'Đại ca'
  return String(t).startsWith('tram/') ? 'trạm' : t
}

const TEN_BAT = { tu_merge: 'tự merge', tu_deploy: 'tự deploy',
  ...Object.fromEntries(DIEU_KIEN.filter((d) => !d.khoa).map((d) => [`dk_${d.ma}`, `nút "${d.ngan}"`])) }
const TEN_LENH = Object.fromEntries(LENH.map((l) => [`lenh_${l.ma}`, l.ngan]))
const giaTri = (v) => (typeof v === 'boolean' ? (v ? 'bật' : 'tắt')
  : !v ? 'trống' : v.includes('/') ? `…/${v.split('/').pop()}` : v)

// Một dòng của `lich_su_doi` (TM-1: {luc, tac_nhan, doi: [{truong, truoc, sau}]}) → {gio, ai, viec, doi}.
export function dongLichSuDoi(r) {
  const bat = r.doi.filter((d) => TEN_BAT[d.truong]).map((d) => `${d.sau ? 'Bật' : 'Tắt'} ${TEN_BAT[d.truong]}`)
  const lenh = r.doi.filter((d) => TEN_LENH[d.truong]).map((d) => TEN_LENH[d.truong])
  const viec = [...bat, ...(lenh.length ? [`Sửa ${lenh.join(', ')}`] : [])].join(', ')
  return { gio: ngayGio(r.luc), ai: tenTacNhan(r.tac_nhan), viec,
    doi: r.doi.map((d) => `${giaTri(d.truoc)} → ${giaTri(d.sau)}`).join(', ') }
}

export function doiCuoi(ds) {
  if (!ds || !ds.length) return 'Chưa từng đổi — đang dùng mặc định'
  return `Đổi lần cuối: ${tenTacNhan(ds[0].tac_nhan)} · ${ngayGio(ds[0].luc)}`
}
```

- [ ] **Step 4: Chạy, mong đợi XANH**

```bash
cd frontend && node --test tests/tu_dong_trang.test.mjs tests/tu_dong_lich_su.test.mjs && npm run kiem
```
Xanh thật: `ℹ tests 10`, `ℹ pass 10`; `npm run kiem` → `ℹ tests 120`, `ℹ pass 120`.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/luat_trang_tu_dong.js frontend/src/luat_bao_tu_dong.js frontend/src/luat_lich_su_tu_dong.js frontend/tests/tu_dong_trang.test.mjs frontend/tests/tu_dong_lich_su.test.mjs
git commit -m "feat(giao-dien): luật hiển thị trang Tự động (TM-4 Task 3)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

### Task 4: Trang Tự động `#/du-an/<ten>` — khối, công tắc, ba lệnh, Deploy, TẠM DỪNG dự án

**Spec:** như Task 3, cộng "Chỉnh trên dashboard qua cửa ghi" (mã thao tác, 409 "… — tải lại" giữ ô nhập; Codex Q9 — phiên bản giữ từ lúc mở form; Codex Q10 — dữ liệu và thao tác ràng với dự án của route), "Lệnh deploy không được chứa bí mật" (422 câu của máy chủ, giữ ô nhập), `tu-deploy` "Nút Deploy của Đại ca" (`expected_commit`, 409), "Xem khi không phải Đại ca". **Mockup:** `trang-tu-dong.js` toàn bộ (trừ `veCapNhat` và hàng tình huống), `them.css` (mục "Trang tự merge/deploy", công tắc, ba lệnh); ảnh `anh-tu-dong.png`, `anh-tu-dong-sua-lenh.png`, `anh-tu-dong-tu-tat.png`, `anh-tu-dong-lui-hong.png`, `anh-tu-dong-cua-tam.png`, `anh-hr-codex-khoa.png`.

**Interfaces:** `dungGhiTuDong(layDl, taiLai, layTen) -> {dangGui, loi, xungDot, luu(doi, hoi, ban = layDl()), tamDung(bat), deploy(commit)}` (URL theo `layTen()` = tên dự án của route; `ban` = `{du_an, phien_ban, cai_dat}` — khác dự án của route thì không gửi), `CHU_XUNG_DOT`; `dungSuaLenh(layDl, g, taiLai) -> {dangSua, o, doiChieu, mo, dong, luu, taiLaiGoc}`; `dungTaiDuAn(layTen) -> {dl, loi, khongCo, tai, doiDuAn}`; component `CongTac` (props `bat`, `khoa`, `nhan`, `lyDo`; emit `doi`), `KhoiSanSang`/`KhoiCaiDat` (props `ten`, `dl`, `laDaiCa`, `taiLai`; trang gắn `:key="ten"`), `KhoiChoDaiCa`/`KhoiLichSu` (prop `dl`), `NganLichSuDoi` (props `duAn`, `ds`; emit `dong`); slot `tren-tieu-de` của `DauTrang`; tuyến `/du-an/:ten`.

- [ ] **Step 1: Viết test**

Tạo mới `frontend/tests/tu_dong_ghi.test.mjs` (nguyên văn):

```js
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { test } from 'node:test'
import { dungGhiTuDong } from '../src/thanh/tu_dong/ghi_tu_dong.js'

const CD = { tu_merge: true, tu_deploy: false, dieu_kien: { ci: true, cot: true, hang_rao: true },
  lenh: { deploy: 'make deploy', kiem_song: 'sh kiem.sh', lui: 'sh lui.sh' } }
const DL = { du_an: 'repo nhap', phien_ban: '41', cai_dat: CD }
const TEN = () => 'repo nhap'                              // tên dự án của route
const XUNG_DOT = 'Cài đặt đã đổi — tải lại'

function gia(phanHoi) {
  const goi = []
  globalThis.fetch = async (url, o) => {
    goi.push({ url, than: JSON.parse(o.body), xTram: o.headers['X-Tram'] })
    return phanHoi()
  }
  return goi
}
const boMa = ({ ma_thao_tac: ma, ...r }) => { assert.ok(ma.length >= 8); return r }

test('lưu cài đặt: thân đủ khoá + expected_version đang xem, X-Tram; huỷ hộp xác nhận thì không gửi gì', async () => {
  const hoi = []
  globalThis.window = { confirm: (c) => { hoi.push(c); return hoi.length > 1 } }
  let tai = 0
  const g = dungGhiTuDong(() => DL, async () => { tai += 1 }, TEN)
  const goi = gia(() => new Response('{"ket_qua": {}, "lap_lai": false}'))
  assert.equal(await g.luu({ tu_merge: false }, 'Tắt tự merge?'), false)
  assert.deepEqual(goi, [])
  assert.equal(await g.luu({ tu_merge: false }, 'Tắt tự merge?'), true)
  assert.deepEqual(hoi, ['Tắt tự merge?', 'Tắt tự merge?'])
  assert.equal(goi[0].url, '/api/du-an/repo%20nhap/tu-dong/cai-dat')
  assert.equal(goi[0].xTram, '1')
  assert.deepEqual(boMa(goi[0].than), { expected_version: '41', cai_dat: { ...CD, tu_merge: false } })
  assert.equal(tai, 1)
  assert.equal(await g.luu({ dieu_kien: { ci: true } }, ''), true)          // không hỏi khi câu hỏi rỗng
  assert.equal(hoi.length, 2)
})

test('409 / 422 / 403: báo tại chỗ, không tải lại, nút mở lại; 409 cài đặt → "Cài đặt đã đổi — tải lại"', async () => {
  globalThis.window = { confirm: () => true }
  let tai = 0
  const g = dungGhiTuDong(() => DL, async () => { tai += 1 }, TEN)
  const loi409 = 'Cài đặt tự động của repo nhap đã đổi (hiện 42, đang xem 41) — tải lại'
  gia(() => new Response(JSON.stringify({ loi: loi409 }), { status: 409 }))
  assert.equal(await g.luu({ lenh: { deploy: 'x' } }, 'Lưu?'), false)
  assert.equal(g.loi.value, XUNG_DOT)
  assert.equal(g.xungDot.value, true)                                       // khối hiện nút "Tải lại"
  assert.equal(g.dangGui.value, false)
  gia(() => new Response(JSON.stringify({ detail: 'cần kênh ghi unix-socket — cửa ghi còn tạm' }), { status: 403 }))
  assert.equal(await g.luu({ tu_merge: false }, ''), false)
  assert.match(g.loi.value, /^cần kênh ghi unix-socket/)
  assert.equal(g.xungDot.value, false)
  const cu = 'Có bản mới hơn — tải lại (bản chờ deploy của repo nhap đã đổi: hiện b2, đang xem a41c07e)'   // TM-3
  gia(() => new Response(JSON.stringify({ loi: cu }), { status: 409 }))
  assert.equal(await g.deploy('a41c07e9d2b8'), false)
  assert.equal(g.loi.value, cu)
  assert.equal(tai, 0)
})

test('TẠM DỪNG hỏi lại, Tiếp tục không hỏi; cả hai không kiểm phiên bản; Deploy mang expected_commit', async () => {
  const hoi = []
  globalThis.window = { confirm: (c) => { hoi.push(c); return true } }
  const g = dungGhiTuDong(() => DL, async () => {}, TEN)
  const goi = gia(() => new Response('{}'))
  await g.tamDung(true)
  await g.tamDung(false)
  await g.deploy('a41c07e9d2b8')
  assert.deepEqual(goi.map((x) => x.url), ['/api/du-an/repo%20nhap/tu-dong/tam-dung',
    '/api/du-an/repo%20nhap/tu-dong/tiep-tuc', '/api/du-an/repo%20nhap/tu-dong/deploy'])
  assert.deepEqual(goi.map((x) => boMa(x.than)), [{ expected_version: '' }, { expected_version: '' },
    { expected_version: '', expected_commit: 'a41c07e9d2b8' }])
  assert.equal(hoi.length, 2)
  assert.match(hoi[0], /^Tạm dừng tự merge và tự deploy của repo nhap\?/)
  assert.match(hoi[1], /^Deploy bản a41c07e của repo nhap/)
})

test('Q9: lưu theo bản chụp lúc mở form — SSE đổi `dl` giữa chừng không đổi phiên bản gửi đi', async () => {
  globalThis.window = { confirm: () => true }
  let dl = DL
  const g = dungGhiTuDong(() => dl, async () => {}, TEN)
  const ban = JSON.parse(JSON.stringify(DL))                                 // chụp lúc mở form (phiên bản 41)
  dl = { ...DL, phien_ban: '42', cai_dat: { ...CD, lenh: { ...CD.lenh, deploy: 'make deploy-moi' } } }  // tab khác lưu
  const goi = gia(() => new Response(JSON.stringify({ loi: 'đã đổi — tải lại' }), { status: 409 }))
  assert.equal(await g.luu({ lenh: { deploy: 'make deploy-cu' } }, '', ban), false)
  assert.deepEqual(boMa(goi[0].than), { expected_version: '41',
    cai_dat: { ...CD, lenh: { ...CD.lenh, deploy: 'make deploy-cu' } } })
  assert.equal(g.loi.value, XUNG_DOT)
})

test('Q10: thao tác theo tên dự án của route; dữ liệu dự án khác thì không gửi; kết quả về muộn thì bỏ', async () => {
  globalThis.window = { confirm: () => true }
  let ten = 'a'
  let tai = 0
  const g = dungGhiTuDong(() => ({ ...DL, du_an: 'a' }), async () => { tai += 1 }, () => ten)
  const goi = gia(() => new Response('{}'))
  ten = 'b'                                                                  // route đã sang b, `dl` còn của a
  assert.equal(await g.luu({ tu_merge: false }, ''), false)
  assert.deepEqual(goi, [])
  assert.equal(g.loi.value, XUNG_DOT)
  await g.tamDung(true)
  await g.deploy('a41c07e9d2b8')
  assert.deepEqual(goi.map((x) => x.url), ['/api/du-an/b/tu-dong/tam-dung', '/api/du-an/b/tu-dong/deploy'])
  assert.equal(tai, 2)
  let tra
  globalThis.fetch = () => new Promise((r) => { tra = r })
  const viec = g.tamDung(false)
  ten = 'c'                                                                  // chuyển trang khi đang gửi
  tra(new Response(JSON.stringify({ loi: 'Estop đang bật' }), { status: 422 }))
  assert.equal(await viec, false)
  assert.deepEqual([g.loi.value, tai], ['', 2])                              // không ghi lỗi của b lên trang c
})

test('tuyến /du-an/:ten tới trang Tự động (mục "Dự án" sáng theo mucCua)', () => {
  const tuyen = readFileSync(new URL('../src/tuyen.js', import.meta.url), 'utf8')
  assert.match(tuyen, /\{ path: '\/du-an\/:ten', component: TuDong \}/)
  assert.match(tuyen, /^import TuDong from '\.\/trang\/TuDong\.vue'$/m)
})
```

Tạo mới `frontend/tests/tu_dong_dong_bo.test.mjs` (nguyên văn — Codex Q9, Q10):

```js
// Codex vòng 1 Q9, Q10: form sửa lệnh giữ bản chụp lúc mở; trang Tự động bỏ phản hồi cũ, xoá dữ liệu khi đổi dự án.
import assert from 'node:assert/strict'
import { test } from 'node:test'
import { dungGhiTuDong } from '../src/thanh/tu_dong/ghi_tu_dong.js'
import { dungSuaLenh } from '../src/thanh/tu_dong/sua_lenh.js'
import { dungTaiDuAn } from '../src/thanh/tu_dong/tai_du_an.js'

const LENH = { deploy: 'make deploy', kiem_song: 'sh kiem.sh', lui: 'sh lui.sh' }
const ban = (du_an, phien_ban, deploy = 'make deploy') => ({ du_an, phien_ban, cai_dat: { tu_merge: true,
  tu_deploy: false, dieu_kien: { ci: true, cot: true, hang_rao: true }, lenh: { ...LENH, deploy } } })
const json = (o, status = 200) => new Response(JSON.stringify(o), { status })
const XUNG_DOT = 'Cài đặt đã đổi — tải lại'

test('Q9: SSE chen giữa mở form và lưu → 409 giữ nháp; "Tải lại" lấy bản mới làm gốc, nháp còn, lưu lại', async () => {
  globalThis.window = { confirm: () => true }
  let dl = ban('a', '41')
  const g = dungGhiTuDong(() => dl, async () => {}, () => 'a')
  const s = dungSuaLenh(() => dl, g, async () => { dl = ban('a', '42', 'make deploy-moi'); return true })
  s.mo()
  s.o.deploy = 'make deploy-cua-a'
  dl = ban('a', '42', 'make deploy-moi')                     // tab khác lưu → SSE → trang tải lại `dl`
  const goi = []
  globalThis.fetch = async (url, o) => {
    goi.push(JSON.parse(o.body))
    return goi.length === 1 ? json({ loi: 'Cài đặt tự động của a đã đổi (hiện 42, đang xem 41) — tải lại' }, 409)
      : json({ ket_qua: {}, lap_lai: false })
  }
  await s.luu()
  assert.deepEqual([goi[0].expected_version, goi[0].cai_dat.lenh.deploy], ['41', 'make deploy-cua-a'])
  assert.deepEqual([s.dangSua.value, s.o.deploy, g.loi.value, g.xungDot.value],
    [true, 'make deploy-cua-a', XUNG_DOT, true])
  await s.taiLaiGoc()
  assert.equal(s.o.deploy, 'make deploy-cua-a')                // nháp giữ nguyên
  assert.equal(s.doiChieu.value.deploy, 'make deploy-moi')      // lệnh đang lưu ở trạm để đối chiếu
  assert.deepEqual([g.loi.value, g.xungDot.value], ['', false])
  await s.luu()
  assert.deepEqual([goi[1].expected_version, goi[1].cai_dat.lenh.deploy], ['42', 'make deploy-cua-a'])
  assert.deepEqual([s.dangSua.value, s.doiChieu.value], [false, null])
})

for (const status of [500, 404]) {
  test(`V2-N1: tải lại lỗi ${status} giữ xung đột và bản gốc của form`, async () => {
    globalThis.window = { confirm: () => true }
    const t = dungTaiDuAn(() => 'a')
    globalThis.fetch = async () => json(ban('a', '41'))
    assert.equal(await t.tai(), true)
    const g = dungGhiTuDong(() => t.dl.value, t.tai, () => 'a')
    const s = dungSuaLenh(() => t.dl.value, g, t.tai)
    s.mo()
    s.o.deploy = 'make nhap'
    g.loi.value = XUNG_DOT
    g.xungDot.value = true
    globalThis.fetch = async () => json({ loi: 'tải lỗi' }, status)
    await s.taiLaiGoc()
    assert.deepEqual([g.loi.value, g.xungDot.value, s.doiChieu.value], [XUNG_DOT, true, null])
    assert.deepEqual([s.dangSua.value, s.o.deploy], [true, 'make nhap'])
    globalThis.fetch = async () => json(ban('a', '42', 'make moi'))
    await t.tai()                                // SSE thành công không tự thay bản gốc đang sửa
    let than
    globalThis.fetch = async (url, o) => { than = JSON.parse(o.body); return json({ loi: XUNG_DOT }, 409) }
    await s.luu()
    assert.equal(than.expected_version, '41')
  })
}

test('Q10: chuyển route khi đang sửa A — không gửi nháp của A sang B', async () => {
  globalThis.window = { confirm: () => true }
  let ten = 'a'
  let dl = ban('a', '41')
  const g = dungGhiTuDong(() => dl, async () => {}, () => ten)
  const s = dungSuaLenh(() => dl, g, async () => {})
  s.mo()
  s.o.deploy = 'make deploy-cua-a'
  ten = 'b'
  dl = ban('b', '7')
  const goi = []
  globalThis.fetch = async (url) => { goi.push(url); return json({}) }
  await s.luu()
  assert.deepEqual(goi, [])
  assert.equal(g.loi.value, XUNG_DOT)
})

test('Q10: phản hồi về đảo thứ tự — chỉ giữ dữ liệu của dự án đang xem', async () => {
  let ten = 'a'
  const t = dungTaiDuAn(() => ten)
  const cho = {}
  globalThis.fetch = (url) => new Promise((r) => { cho[url] = r })
  const ta = t.doiDuAn()
  ten = 'b'
  const tb = t.doiDuAn()
  cho['/api/du-an/b/tu-dong'](json(ban('b', '7')))
  await tb
  cho['/api/du-an/a/tu-dong'](json(ban('a', '41')))
  await ta
  assert.equal(t.dl.value.du_an, 'b')
})

test('Q10: đổi sang B thì xoá dữ liệu A ngay; tải B lỗi → không còn dữ liệu A; 404 → không có dự án', async () => {
  let ten = 'a'
  const t = dungTaiDuAn(() => ten)
  globalThis.fetch = async (url) => (url.includes('/a/') ? json(ban('a', '41')) : json({ loi: 'trạm lỗi' }, 500))
  await t.doiDuAn()
  assert.equal(t.dl.value.du_an, 'a')
  globalThis.fetch = async () => json({ loi: 'mất kết nối' }, 502)
  await t.tai()                                                // tải lại CÙNG dự án lỗi: giữ dữ liệu A, báo lỗi
  assert.deepEqual([t.dl.value.du_an, t.loi.value], ['a', 'mất kết nối'])
  globalThis.fetch = async () => json({ loi: 'trạm lỗi' }, 500)
  ten = 'b'
  const viec = t.doiDuAn()
  assert.deepEqual([t.dl.value, t.loi.value], [null, ''])      // khoá ngay, không chờ B
  await viec
  assert.deepEqual([t.dl.value, t.loi.value, t.khongCo.value], [null, 'trạm lỗi', false])
  globalThis.fetch = async () => json({ detail: 'không có' }, 404)
  ten = 'c'
  await t.doiDuAn()
  assert.deepEqual([t.dl.value, t.khongCo.value, t.loi.value], [null, true, ''])
})

test('Q10: route đổi trước watcher tải mới — phản hồi A không được nhận vào B', async () => {
  let ten = 'a'
  const t = dungTaiDuAn(() => ten)
  let tra
  globalThis.fetch = () => new Promise((r) => { tra = r })
  const viec = t.tai()
  ten = 'b'
  tra(json(ban('a', '41')))
  await viec
  assert.equal(t.dl.value, null)
})
```

- [ ] **Step 2: Chạy, mong đợi ĐỎ**

```bash
cd frontend && node --test tests/tu_dong_ghi.test.mjs tests/tu_dong_dong_bo.test.mjs
```
Đỏ thật: `Error [ERR_MODULE_NOT_FOUND]: Cannot find module '…/frontend/src/thanh/tu_dong/ghi_tu_dong.js' imported from …/frontend/tests/tu_dong_ghi.test.mjs` (và tương tự cho `tu_dong_dong_bo.test.mjs`) — `ℹ tests 2`, `ℹ fail 2`.

- [ ] **Step 3: Viết mã**

Tạo mới `frontend/src/thanh/tu_dong/ghi_tu_dong.js` (nguyên văn):

```js
// Thao tác ghi của trang Tự động và nút Deploy ở Phê duyệt (spec dieu-khien-tu-dong "Chỉnh trên dashboard qua cửa
// ghi", tu-deploy "Nút Deploy", D129): mọi POST qua api.ghi (X-Tram) + mã thao tác mới mỗi lần bấm; URL dựng từ TÊN
// DỰ ÁN CỦA ROUTE (`layTen`, Codex Q10), kết quả về khi đã sang dự án khác thì bỏ. Cài đặt gửi đủ khoá +
// `expected_version` của bản chụp lúc bắt đầu sửa (`ban`, Codex Q9; mặc định bản đang xem) — 409 → "Cài đặt đã đổi —
// tải lại", giữ ô nhập; TẠM DỪNG / Tiếp tục không kiểm phiên bản (như estop); Deploy gửi `expected_commit` (TM-3).
// Hỏi lại bằng hộp xác nhận của trình duyệt như estop; câu hỏi rỗng thì gửi luôn.
import { ref } from 'vue'
import { ghi, thanGhi } from '../../api.js'
import { hoiDeploy, hoiTamDung, thanCaiDat } from '../../luat_trang_tu_dong.js'

export const CHU_XUNG_DOT = 'Cài đặt đã đổi — tải lại'

export function dungGhiTuDong(layDl, taiLai, layTen) {
  const dangGui = ref(false)
  const loi = ref('')
  const xungDot = ref(false)

  async function lam(ten, duoi, than, hoi, cau409 = '') {
    if (hoi && !window.confirm(hoi)) return false
    dangGui.value = true
    loi.value = ''
    xungDot.value = false
    try {
      await ghi(`/api/du-an/${encodeURIComponent(ten)}/tu-dong/${duoi}`, than)
      if (ten === layTen()) await taiLai()
      return true
    } catch (e) {
      if (ten === layTen()) {
        xungDot.value = e.status === 409
        loi.value = xungDot.value && cau409 ? cau409 : e.message
      }
      return false
    } finally {
      dangGui.value = false
    }
  }
  function luu(doi, hoi, ban = layDl()) {
    const ten = layTen()
    if (!ban || ban.du_an !== ten) {               // chưa tải xong / dữ liệu của dự án khác: không gửi
      loi.value = CHU_XUNG_DOT
      xungDot.value = true
      return Promise.resolve(false)
    }
    return lam(ten, 'cai-dat', thanGhi({ cai_dat: thanCaiDat(ban.cai_dat, doi) }, ban.phien_ban), hoi, CHU_XUNG_DOT)
  }
  function tamDung(bat) {
    const ten = layTen()
    return lam(ten, bat ? 'tam-dung' : 'tiep-tuc', thanGhi({}, ''), bat ? hoiTamDung(ten) : '')
  }
  function deploy(commit) {
    const ten = layTen()
    return lam(ten, 'deploy', thanGhi({ expected_commit: commit }, ''), hoiDeploy(ten, commit))
  }
  return { dangGui, loi, xungDot, luu, tamDung, deploy }
}
```

Tạo mới `frontend/src/thanh/tu_dong/sua_lenh.js` (nguyên văn — Codex Q9):

```js
// Form "Sửa 3 lệnh" của khối Cài đặt (Codex Q9): chụp {du_an, phien_ban, cai_dat} lúc MỞ form và giữ tới lúc gửi —
// SSE tải lại trang chen giữa không đổi phiên bản đang sửa, nên tab cũ nhận 409 thay vì ghi đè lệnh mới bằng nháp cũ.
// 409 → giữ nháp, khối hiện "Cài đặt đã đổi — tải lại" + nút "Tải lại": lấy bản mới làm gốc, nháp giữ nguyên, cạnh ô
// nào khác thì hiện lệnh đang lưu ở trạm (`doiChieu`) để Đại ca đối chiếu rồi lưu lại hoặc huỷ.
import { reactive, ref } from 'vue'
import { doiLenh, hoiLuuLenh } from '../../luat_trang_tu_dong.js'

const chup = (dl) => ({ du_an: dl.du_an, phien_ban: dl.phien_ban, cai_dat: JSON.parse(JSON.stringify(dl.cai_dat)) })

export function dungSuaLenh(layDl, g, taiLai) {
  const dangSua = ref(false)
  const o = reactive({ deploy: '', kiem_song: '', lui: '' })
  const doiChieu = ref(null)
  let goc = null
  const xoaLoi = () => { g.loi.value = ''; g.xungDot.value = false }

  function mo() {
    goc = chup(layDl())
    Object.assign(o, goc.cai_dat.lenh)
    doiChieu.value = null
    xoaLoi()
    dangSua.value = true
  }
  function dong() {
    goc = null
    doiChieu.value = null
    xoaLoi()
    dangSua.value = false
  }
  async function luu() {
    if (!goc) return
    const d = doiLenh(goc.cai_dat, o)
    if (await g.luu(d, hoiLuuLenh(d.tu_deploy === false), goc)) dong()
  }
  async function taiLaiGoc() {
    if (await taiLai() !== true) return
    const moi = layDl()
    if (!goc || !moi || moi.du_an !== goc.du_an) return
    goc = chup(moi)
    doiChieu.value = { ...goc.cai_dat.lenh }
    xoaLoi()
  }
  return { dangSua, o, doiChieu, mo, dong, luu, taiLaiGoc }
}
```

Tạo mới `frontend/src/thanh/tu_dong/tai_du_an.js` (nguyên văn — Codex Q10):

```js
// Tải GET /api/du-an/<ten>/tu-dong cho trang Tự động, ràng với tên dự án của route (Codex Q10): mỗi lần tải mang một
// thế hệ, phản hồi của lần cũ (kể cả của dự án trước) bị bỏ. Đổi dự án → xoá dữ liệu cũ NGAY (khối và nút biến mất)
// rồi mới tải dự án mới, nên tải lỗi không để lại dữ liệu của dự án khác. Tải lại cùng dự án lỗi: giữ dữ liệu, báo lỗi.
import { ref } from 'vue'
import { doc } from '../../api.js'

export function dungTaiDuAn(layTen) {
  const dl = ref(null)
  const loi = ref('')
  const khongCo = ref(false)
  let theHe = 0

  async function tai() {
    const lan = ++theHe
    const ten = layTen()
    try {
      const r = await doc(`/api/du-an/${encodeURIComponent(ten)}/tu-dong`)
      if (lan !== theHe || ten !== layTen()) return false
      dl.value = r
      loi.value = ''
      khongCo.value = false
      return true
    } catch (e) {
      if (lan !== theHe || ten !== layTen()) return false
      khongCo.value = e.status === 404
      if (khongCo.value) dl.value = null
      loi.value = khongCo.value ? '' : e.message
      return false
    }
  }
  function doiDuAn() {
    dl.value = null
    loi.value = ''
    khongCo.value = false
    return tai()
  }
  return { dl, loi, khongCo, tai, doiDuAn }
}
```

Tạo mới `frontend/src/thanh/tu_dong/CongTac.vue` (nguyên văn):

```vue
<script setup>
// Công tắc `role="switch"` (mockup them.css `.cong-tac`, design D-10). Chỉ phát `doi` với giá trị mới; khối cha hỏi
// lại và gửi. Khoá kèm câu giải thích ở `title` (máy chủ vẫn là nơi từ chối).
defineProps({ bat: { type: Boolean, default: false }, khoa: { type: Boolean, default: false },
  nhan: { type: String, required: true }, lyDo: { type: String, default: '' } })
const emit = defineEmits(['doi'])
</script>

<template>
  <button type="button" class="cong-tac" role="switch" :aria-checked="bat ? 'true' : 'false'" :aria-label="nhan"
          :disabled="khoa" :title="lyDo || null" @click="emit('doi', !bat)" />
</template>
```

Tạo mới `frontend/src/thanh/tu_dong/KhoiSanSang.vue` (nguyên văn):

```vue
<script setup>
import { computed } from 'vue'
import { CHUA_CO, sanSang } from '../../luat_trang_tu_dong.js'
import { dungGhiTuDong } from './ghi_tu_dong.js'

// Khối "Sẵn sàng deploy" (mockup veSanSang, anh-tu-dong.png): một hàng cho commit mới nhất (TM-3 gộp nhiều merge)
// + nút Deploy có hỏi lại, hoặc hàng "đang deploy". Deploy khoá khi estop / thiếu lệnh / cửa ghi; tạm dừng thì không.
const props = defineProps({ ten: { type: String, required: true }, dl: { type: Object, required: true },
  laDaiCa: { type: Boolean, default: false }, taiLai: { type: Function, required: true } })
const s = computed(() => sanSang(props.dl, props.laDaiCa))
const g = dungGhiTuDong(() => props.dl, props.taiLai, () => props.ten)
</script>

<template>
  <section class="the ss-deploy">
    <h3 class="td-h">Sẵn sàng deploy <span class="nho">{{ s.phu }}</span></h3>
    <div v-if="s.chuaCo" class="ss-rong">{{ CHUA_CO }}</div>
    <div v-else-if="s.rong" class="ss-rong">{{ s.rong }}</div>
    <div v-else-if="s.dangDeploy" class="ss-hang">
      <div><div class="tieu-de">{{ s.dangDeploy.cho ? 'Chờ trạm nhận bản' : 'Đang deploy bản' }}
        <span class="mono">{{ s.dangDeploy.commit }}</span></div>
        <div class="nho">{{ s.dangDeploy.nguon }} · {{ s.dangDeploy.cho ? 'bấm lúc' : 'bắt đầu' }}
          {{ s.dangDeploy.luc }}</div></div>
      <button type="button" class="nut chinh" disabled>{{ s.dangDeploy.cho ? 'Đã gửi…' : 'Đang deploy…' }}</button>
      <div class="chu-thich nho">Trạm chạy lệnh deploy → lệnh kiểm còn sống; hỏng thì tự lùi và báo Telegram.</div>
    </div>
    <div v-else class="ss-hang">
      <div>
        <div class="tieu-de">Bản <span class="mono">{{ s.ban.commit }}</span> — gồm {{ s.ban.soMerge }} việc đã
          merge</div>
        <div class="nho">{{ s.ban.bead ? `${s.ban.bead} · ` : '' }}merge cuối {{ s.ban.luc }}<template
          v-if="s.ban.dangChay"> · bản đang chạy <span class="mono">{{ s.ban.dangChay }}</span></template></div>
      </div>
      <button type="button" class="nut chinh" :disabled="Boolean(s.lyDo) || g.dangGui.value" :title="s.lyDo || null"
              @click="g.deploy(dl.san_sang.commit)">{{ g.dangGui.value ? 'Đang gửi…' : 'Deploy' }}</button>
      <div class="chu-thich nho">Trạm chạy lệnh deploy → lệnh kiểm còn sống; hỏng thì tự lùi<template
        v-if="s.ban.dangChay"> về <span class="mono">{{ s.ban.dangChay }}</span></template> và báo Telegram.<b
        v-if="s.lyDo">{{ ` ${s.lyDo}.` }}</b></div>
      <p v-if="g.loi.value" class="loi chu-thich" role="alert">{{ g.loi.value }}</p>
    </div>
  </section>
</template>
```

Tạo mới `frontend/src/thanh/tu_dong/KhoiChoDaiCa.vue` (nguyên văn):

```vue
<script setup>
import { computed } from 'vue'
import { CHUA_CO, choDaiCa } from '../../luat_trang_tu_dong.js'

// Khối "Chờ Đại ca" (mockup veCho; spec tu-merge "Thiếu điều kiện thì chờ Đại ca và nói rõ vì sao"): việc không
// được tự merge kèm từng lý do bằng lời của máy chủ (TM-2 `cho_dai_ca`). Xử lý như hôm nay ở Phê duyệt.
const props = defineProps({ dl: { type: Object, required: true } })
const ds = computed(() => choDaiCa(props.dl))
</script>

<template>
  <section class="the">
    <h3 class="td-h">Chờ Đại ca <span class="chip">{{ ds ? ds.length : '—' }}</span>
      <span class="nho">thiếu điều kiện nên không tự merge — xử lý như hôm nay ở Phê duyệt</span></h3>
    <div v-if="!ds" class="ss-rong">{{ CHUA_CO }}</div>
    <ul v-else-if="ds.length" class="ds-cho">
      <li v-for="c in ds" :key="c.bead"><span class="mono">{{ c.bead }}</span><span>{{ c.tieuDe }}</span>
        <span class="ly-do"><span v-for="l in c.lyDo" :key="l.chu" class="chip" :class="l.lop">{{ l.chu }}</span></span>
      </li>
    </ul>
    <div v-else class="ss-rong">Không có việc nào đang chờ.</div>
  </section>
</template>
```

Tạo mới `frontend/src/thanh/tu_dong/KhoiLichSu.vue` (nguyên văn):

```vue
<script setup>
import { computed } from 'vue'
import { dongLichSu } from '../../luat_lich_su_tu_dong.js'
import { CHUA_CO } from '../../luat_trang_tu_dong.js'

// Khối "Lịch sử gần đây" (mockup veLichSu): tự merge, sẵn sàng, deploy, lùi — chỉ mã thoát và thời gian, không log
// (spec tu-deploy "Không lọt bí mật qua kết quả deploy"). Dữ liệu TM-2/TM-3 dựng trong `lich_su`.
const props = defineProps({ dl: { type: Object, required: true } })
const ds = computed(() => (Array.isArray(props.dl.lich_su) ? props.dl.lich_su.map(dongLichSu) : null))
</script>

<template>
  <section class="the">
    <h3 class="td-h">Lịch sử gần đây
      <span class="nho">tự merge, deploy, lùi — chỉ mã thoát và thời gian, không có log</span></h3>
    <div v-if="!ds" class="ss-rong">{{ CHUA_CO }}</div>
    <div v-else-if="ds.length" class="bang-cuon">
      <table class="bang bang-ls">
        <thead><tr><th>Giờ</th><th>Việc</th><th>Bead</th><th>Commit</th><th>Chi tiết</th><th>Ai</th></tr></thead>
        <tbody>
          <tr v-for="(r, i) in ds" :key="i">
            <td class="mono">{{ r.gio }}</td><td><span class="chip" :class="r.lop">{{ r.nhan }}</span></td>
            <td class="mono ma">{{ r.bead }}</td><td class="mono">{{ r.commit }}</td>
            <td class="nho">{{ r.chiTiet }}</td><td class="nho">{{ r.ai }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-else class="ss-rong">Chưa có lần tự merge hay deploy nào.</div>
  </section>
</template>
```

Tạo mới `frontend/src/thanh/tu_dong/KhoiCaiDat.vue` (nguyên văn):

```vue
<script setup>
import { computed } from 'vue'
import { doiCuoi } from '../../luat_lich_su_tu_dong.js'
import { DIEU_KIEN, LENH, doiCongTac, hoiCongTac } from '../../luat_trang_tu_dong.js'
import { lyDoKhoaGhi } from '../../luat_tu_dong.js'
import BieuTuong from '../BieuTuong.vue'
import CongTac from './CongTac.vue'
import { dungGhiTuDong } from './ghi_tu_dong.js'
import { dungSuaLenh } from './sua_lenh.js'

// Khối "Cài đặt" (mockup veCaiDat, anh-tu-dong.png, anh-tu-dong-sua-lenh.png, anh-hr-codex-khoa.png): công tắc tự
// merge, 2 điều kiện "luôn bật" không có nút (D71), 3 nút điều kiện, dòng "cấu trúc DB — luôn chờ Đại ca" (D76),
// 3 lệnh (xem / sửa, Lưu hỏi lại), tự deploy (khoá khi chưa đủ 3 lệnh, D73). Lỗi của máy chủ hiện tại chỗ; 409 →
// "Cài đặt đã đổi — tải lại" + nút Tải lại, form sửa lệnh giữ bản chụp lúc mở và giữ nháp (Codex Q9, `sua_lenh.js`).
const props = defineProps({ ten: { type: String, required: true }, dl: { type: Object, required: true },
  laDaiCa: { type: Boolean, default: false }, taiLai: { type: Function, required: true } })
const emit = defineEmits(['xem-lich-su'])
const g = dungGhiTuDong(() => props.dl, props.taiLai, () => props.ten)
const s = dungSuaLenh(() => props.dl, g, props.taiLai)
const cd = computed(() => props.dl.cai_dat)
const lyDo = computed(() => lyDoKhoaGhi(props.dl, props.laDaiCa))
const khoa = computed(() => Boolean(lyDo.value) || g.dangGui.value)
const thieuLenh = computed(() => !props.dl.du_lenh && !cd.value.tu_deploy)
const doi = (ma, bat) => g.luu(doiCongTac(ma, bat), hoiCongTac(ma, bat, props.ten))
async function taiLaiXungDot() {
  if (s.dangSua.value) return s.taiLaiGoc()
  if (await props.taiLai() !== true) return
  g.loi.value = ''
  g.xungDot.value = false
}
const conTram = (ma) => (s.doiChieu.value && s.doiChieu.value[ma] !== s.o[ma] ? s.doiChieu.value[ma] || 'trống' : '')
</script>

<template>
  <section class="the">
    <h3 class="td-h">Cài đặt</h3>
    <p v-if="lyDo" class="nho">{{ lyDo }}</p>
    <p v-if="g.loi.value && !s.dangSua.value" class="loi" role="alert">{{ g.loi.value }}
      <button v-if="g.xungDot.value" type="button" class="nut" @click="taiLaiXungDot">Tải lại</button></p>
    <div class="cd-hang chinh"><span class="ten">Tự merge</span>
      <span class="mo-ta">Mặc định tắt. Bật: trạm tự gộp PR của chính nó khi đủ mọi điều kiện dưới đây.</span>
      <span class="ben-phai"><CongTac :bat="cd.tu_merge" :khoa="khoa" nhan="Tự merge" :ly-do="lyDo"
                                       @doi="doi('tu_merge', $event)" /></span></div>
    <div class="cd-nhom">Điều kiện — thiếu một thì chờ Đại ca</div>
    <div v-for="d in DIEU_KIEN" :key="d.ma" class="cd-hang" :class="{ khoa: d.khoa }">
      <span class="ten">{{ d.ten }}</span><span class="mo-ta">{{ d.mo_ta }}</span>
      <span v-if="d.khoa" class="ben-phai chip khoa"><BieuTuong ten="khoa" />luôn bật</span>
      <span v-else class="ben-phai"><CongTac :bat="cd.dieu_kien[d.ma]" :khoa="khoa" :nhan="d.ten" :ly-do="lyDo"
                                             @doi="doi(d.ma, $event)" /></span>
    </div>
    <div class="cd-hang khoa"><span class="ten">Cấu trúc DB, xoá dữ liệu</span>
      <span class="mo-ta">Luôn chờ Đại ca, kể cả khi tắt nút hàng rào</span>
      <span class="ben-phai chip tt-loi khoa"><BieuTuong ten="khoa" />luôn chờ Đại ca</span></div>
    <div class="cd-nhom">Deploy — 3 lệnh của dự án</div>
    <div v-if="s.dangSua.value" class="lenh-ds">
      <label v-for="l in LENH" :key="l.ma" class="lenh-o">
        <span class="nhan">{{ l.ten }}<span class="nho">{{ l.goi_y }}</span></span>
        <input v-model="s.o[l.ma]" class="o" spellcheck="false" autocomplete="off" maxlength="500">
        <span v-if="conTram(l.ma)" class="nho">Đang lưu ở trạm: <code>{{ conTram(l.ma) }}</code></span></label>
      <p class="nho">Mỗi lệnh chạy trên máy B dưới tài khoản trạm, trong bản sạch của nhánh chính, không qua shell.
        Không dán mật khẩu hay token vào lệnh.</p>
      <div class="lenh-nut">
        <button type="button" class="nut chinh" :disabled="khoa" @click="s.luu">Lưu 3 lệnh</button>
        <button type="button" class="nut" @click="s.dong">Huỷ</button>
        <span v-if="g.loi.value" class="loi-tai-cho" role="alert">{{ g.loi.value }}</span>
        <button v-if="g.xungDot.value" type="button" class="nut" @click="taiLaiXungDot">Tải lại</button></div>
    </div>
    <div v-else class="lenh-ds">
      <div v-for="l in LENH" :key="l.ma" class="lenh-o">
        <span class="nhan">{{ l.ten }}<span class="nho">{{ l.goi_y }}</span></span>
        <code v-if="cd.lenh[l.ma]">{{ cd.lenh[l.ma] }}</code><code v-else class="trong">chưa khai</code></div>
      <div class="lenh-nut"><button type="button" class="nut" :disabled="khoa" :title="lyDo || null"
                                    @click="s.mo">Sửa 3 lệnh</button></div>
    </div>
    <div class="cd-hang chinh"><span class="ten">Tự deploy</span>
      <span class="mo-ta">Mặc định tắt: trạm merge xong thì báo "sẵn sàng deploy" và chờ Đại ca bấm. Bật: trạm tự
        deploy ngay sau khi merge.<b v-if="!dl.du_lenh"> Chưa khai đủ 3 lệnh.</b></span>
      <span class="ben-phai"><CongTac :bat="cd.tu_deploy" :khoa="khoa || thieuLenh" nhan="Tự deploy"
                                       :ly-do="lyDo || (thieuLenh ? 'Chưa khai đủ 3 lệnh' : '')"
                                       @doi="doi('tu_deploy', $event)" /></span></div>
    <div class="cd-chan">{{ doiCuoi(dl.lich_su_doi) }}
      <button v-if="dl.lich_su_doi.length" type="button" @click="emit('xem-lich-su')">Xem lịch sử đổi</button></div>
  </section>
</template>
```

Tạo mới `frontend/src/thanh/tu_dong/NganLichSuDoi.vue` (nguyên văn):

```vue
<script setup>
import { computed } from 'vue'
import { dongLichSuDoi } from '../../luat_lich_su_tu_dong.js'

// Ngăn bên "Lịch sử đổi cài đặt" (mockup nút "Xem lịch sử đổi" → moNganBen; spec "Xem lịch sử đổi"): ai, lúc nào,
// trước → sau. Dùng lại lớp `.ngan-ben`, `.dtg` của ngăn bên Công việc.
const props = defineProps({ duAn: { type: String, required: true }, ds: { type: Array, required: true } })
const emit = defineEmits(['dong'])
const dong = computed(() => props.ds.map(dongLichSuDoi))
</script>

<template>
  <aside class="ngan-ben" aria-label="Lịch sử đổi cài đặt" @keydown.esc="emit('dong')">
    <button class="dong" type="button" aria-label="Đóng lịch sử đổi" @click="emit('dong')">×</button>
    <h2>Lịch sử đổi cài đặt</h2>
    <p>{{ duAn }} · mỗi dòng do Đại ca (dashboard) hoặc trạm ghi; không bao giờ có giá trị bí mật.</p>
    <ul class="dtg">
      <li v-for="(r, i) in dong" :key="i"><span class="mono">{{ r.gio }}</span>{{ r.viec }} —
        <span class="nho">{{ r.doi }} · {{ r.ai }}</span></li>
    </ul>
  </aside>
</template>
```

Tạo mới `frontend/src/trang/TuDong.vue` (nguyên văn):

```vue
<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { kho } from '../kho.js'
import { baoTuDong } from '../luat_bao_tu_dong.js'
import { demHong } from '../luat_lich_su_tu_dong.js'
import { CHUA_CO } from '../luat_trang_tu_dong.js'
import { chipTuDong, lyDoKhoaTamDung } from '../luat_tu_dong.js'
import BieuTuong from '../thanh/BieuTuong.vue'
import DauTrang from '../thanh/DauTrang.vue'
import KhoiCaiDat from '../thanh/tu_dong/KhoiCaiDat.vue'
import KhoiChoDaiCa from '../thanh/tu_dong/KhoiChoDaiCa.vue'
import KhoiLichSu from '../thanh/tu_dong/KhoiLichSu.vue'
import KhoiSanSang from '../thanh/tu_dong/KhoiSanSang.vue'
import NganLichSuDoi from '../thanh/tu_dong/NganLichSuDoi.vue'
import { dungGhiTuDong } from '../thanh/tu_dong/ghi_tu_dong.js'
import { dungTaiDuAn } from '../thanh/tu_dong/tai_du_an.js'
import '../kieu/tu-dong.css'

// Trang Tự động của một dự án `#/du-an/<ten>` (mockup 2026-10-18 trang-tu-dong.js, anh-tu-dong.png; spec
// dieu-khien-tu-dong "Trang tự merge/deploy của dự án"). Trái: sẵn sàng deploy, chờ Đại ca, lịch sử; phải: bộ đếm
// hỏng, cài đặt. Khối "agent tự cập nhật việc" của mockup thuộc plan TC — không vẽ. Không phải Đại ca: chỉ xem.
// Codex Q10: dữ liệu và mọi thao tác ràng với tên dự án của route (`tai_du_an.js`, `ghi_tu_dong.js`); đổi dự án thì
// bỏ dữ liệu, lỗi, ngăn lịch sử đổi của dự án cũ; khối Cài đặt / Sẵn sàng dựng lại theo `:key` (form sửa về trống).
const MO_TA = 'Tự merge và tự deploy của dự án này. Mỗi nút ở đây ghi qua cửa ghi có xác thực như các nút khác '
  + 'của dashboard.'
const route = useRoute()
const ten = computed(() => String(route.params.ten))
const { dl, loi, khongCo, tai, doiDuAn } = dungTaiDuAn(() => ten.value)
const xemLichSu = ref(false)
const laDaiCa = computed(() => Boolean(kho.trangThai && kho.trangThai.la_dai_ca))
const g = dungGhiTuDong(() => dl.value, tai, () => ten.value)
watch(ten, () => { xemLichSu.value = false; g.loi.value = ''; doiDuAn() }, { immediate: true })
watch(() => kho.phienBanTuDong, tai)
const bao = computed(() => (dl.value ? baoTuDong(dl.value) : []))
const chip = computed(() => (dl.value ? chipTuDong({ ...dl.value, ...dl.value.cai_dat }, dl.value) : []))
const tamDung = computed(() => Boolean(dl.value && dl.value.tam_dung))
const lyDoTD = computed(() => lyDoKhoaTamDung(dl.value, laDaiCa.value, tamDung.value))
const khoaTD = computed(() => !dl.value || Boolean(lyDoTD.value) || g.dangGui.value)
const dem = computed(() => (dl.value ? demHong(dl.value.dem_hong) : null))
</script>

<template>
  <div v-if="khongCo" class="cho-chot"><strong>Không có dự án này</strong>
    Dự án "{{ ten }}" không có trong du-an/. <router-link to="/du-an">Về trang Dự án</router-link></div>
  <template v-else>
    <DauTrang :tieu-de="`${ten} · Tự động`"
              :mo-ta="MO_TA">
      <template #tren-tieu-de>
        <div class="duong-dan"><router-link to="/du-an">Dự án</router-link> / {{ ten }}</div>
      </template>
      <template #cong-cu>
        <div class="td-cong-cu">
          <div class="hang-chip"><span v-for="c in chip" :key="c.chu" class="chip" :class="c.lop"
                                       :title="c.title || null">{{ c.chu }}</span></div>
          <button type="button" class="nut-estop vang" :class="{ bat: tamDung }" :disabled="khoaTD"
                  :title="lyDoTD || null" @click="g.tamDung(!tamDung)">
            <BieuTuong ten="tam-dung" class="dac" />
            <span>{{ tamDung ? 'Dự án đang tạm dừng' : 'Tạm dừng dự án' }}</span>
          </button>
        </div>
      </template>
    </DauTrang>
    <p v-if="loi" class="loi" role="alert">{{ loi }}</p>
    <p v-if="g.loi.value" class="loi" role="alert">{{ g.loi.value }}</p>
    <template v-if="dl">
      <div v-for="b in bao" :key="b.tieuDe" class="the td-bao" :class="b.lop">
        <strong>{{ b.tieuDe }}</strong>
        <p><span v-for="(p, i) in b.than" :key="i" :class="{ mono: p[1] }">{{ p[0] }}</span></p>
        <div v-if="b.nut" class="hang-nut">
          <button type="button" class="nut" :disabled="khoaTD" :title="lyDoTD || null"
                  @click="g.tamDung(false)">{{ b.nut }}</button></div>
      </div>
      <div class="td-luoi">
        <div class="td-cot">
          <KhoiSanSang :key="ten" :ten="ten" :dl="dl" :la-dai-ca="laDaiCa" :tai-lai="tai" />
          <KhoiChoDaiCa :dl="dl" />
          <KhoiLichSu :dl="dl" />
        </div>
        <div class="td-cot">
          <section class="the"><h3 class="td-h">Deploy hỏng liên tiếp</h3>
            <div v-if="dem" class="dem-hong"><span v-for="(d, i) in dem.den" :key="i" class="den-ss" :class="d" />
              <b>{{ dem.chu }}</b></div>
            <div v-else class="ss-rong">{{ CHUA_CO }}</div>
            <p class="nho">Mỗi lần hỏng trạm tự lùi và báo Telegram. Đủ 3 lần liền thì trạm tự tắt tự deploy. Về 0 khi
              một lần deploy thành công.</p>
          </section>
          <KhoiCaiDat :key="ten" :ten="ten" :dl="dl" :la-dai-ca="laDaiCa" :tai-lai="tai"
                      @xem-lich-su="xemLichSu = true" />
        </div>
      </div>
      <NganLichSuDoi v-if="xemLichSu" :du-an="dl.du_an" :ds="dl.lich_su_doi" @dong="xemLichSu = false" />
    </template>
  </template>
</template>
```

Tạo mới `frontend/src/kieu/tu-dong.css` (nguyên văn):

```css
/* Trang Tự động của một dự án (mockup 2026-10-18 them.css "Trang tự merge/deploy", công tắc, ba lệnh).
   Màu chỉ dùng token. */
.duong-dan { font-size: 13px; color: var(--chu-phu); margin-bottom: 2px; }
.duong-dan a { color: var(--nhan); text-decoration: none; }
.td-cong-cu { display: flex; flex-direction: column; align-items: flex-end; gap: 8px; }
.td-cong-cu .hang-chip { display: flex; gap: 6px; flex-wrap: wrap; justify-content: flex-end; }
.td-luoi { display: grid; grid-template-columns: minmax(0, 1.2fr) minmax(0, 1fr); gap: 16px; align-items: start; }
.td-cot { display: flex; flex-direction: column; gap: 16px; min-width: 0; }
.td-h { margin: 0 0 10px; font-size: 16px; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.td-h .nho { font-weight: 400; font-size: 12.5px; }
.td-bao {
  margin-bottom: 16px; border-left: 5px solid var(--vang); background: var(--nen-canh-bao);
  border-color: var(--vien-canh-bao); color: var(--chu-canh-bao);
}
.td-bao.do { border-left-color: var(--do); background: var(--nen-estop); border-color: var(--vien-estop);
  color: var(--chu-bang-estop); }
.td-bao strong { display: block; font-size: 15px; margin-bottom: 4px; }
.td-bao p { margin: 0 0 8px; font-size: 13.5px; }
.td-bao .hang-nut { display: flex; gap: 8px; flex-wrap: wrap; }

/* Sẵn sàng deploy */
.ss-deploy { border-color: var(--vien-xanh-bien); border-left: 5px solid var(--xanh-bien); }
.ss-hang { display: grid; grid-template-columns: 1fr auto; gap: 6px 16px; align-items: center; }
.ss-hang .tieu-de { font-weight: 650; font-size: 15.5px; }
.ss-hang .mono { color: var(--nhan); font-size: 12.5px; }
.ss-hang .chu-thich { grid-column: 1 / -1; margin: 0; }
.ss-rong { color: var(--chu-phu); font-size: 13.5px; }

/* Bộ đếm hỏng liên tiếp (đèn `.den-ss` của trang Cài đặt) */
.dem-hong { display: flex; align-items: center; gap: 10px; }
.dem-hong .den-ss { width: 14px; height: 14px; }
.dem-hong b { font-size: 20px; font-variant-numeric: tabular-nums; }

/* Chờ Đại ca */
.ds-cho { list-style: none; margin: 0; padding: 0; }
.ds-cho li { display: grid; grid-template-columns: 64px 1fr; gap: 4px 10px; padding: 8px 0;
  border-bottom: 1px solid var(--vien); font-size: 13.5px; }
.ds-cho li:last-child { border-bottom: 0; }
.ds-cho .mono { color: var(--nhan); font-size: 12.5px; padding-top: 2px; }
.ds-cho .ly-do { grid-column: 2; display: flex; gap: 6px; flex-wrap: wrap; }

/* Bảng lịch sử */
.bang-ls td { vertical-align: top; }
.bang-ls td.mono { font-size: 12.5px; white-space: nowrap; }
.bang-ls td.mono.ma { color: var(--nhan); }

/* Cài đặt: hàng có công tắc */
.cd-hang { display: grid; grid-template-columns: 1fr auto; gap: 2px 14px; align-items: center; padding: 10px 0;
  border-bottom: 1px solid var(--vien); }
.cd-hang:last-child { border-bottom: 0; }
.cd-hang .ten { font-weight: 600; font-size: 14px; }
.cd-hang .mo-ta { grid-column: 1; font-size: 12.5px; color: var(--chu-phu); }
.cd-hang .ben-phai { grid-row: 1 / span 2; grid-column: 2; }
.cd-hang.chinh .ten { font-size: 15.5px; font-weight: 700; }
.cd-hang.khoa .ten { color: var(--chu-2); }
.cd-nhom { margin: 14px 0 2px; font-size: 12px; text-transform: uppercase; letter-spacing: .5px; color: var(--chu-phu);
  font-weight: 600; }
.cd-chan { margin-top: 12px; padding-top: 10px; border-top: 1px dashed var(--vien-dam); font-size: 12.5px;
  color: var(--chu-phu); display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
.cd-chan button { border: 0; background: none; color: var(--nhan); font-size: 12.5px; padding: 0;
  text-decoration: underline; }

/* Công tắc (role=switch) */
.cong-tac { position: relative; width: 44px; height: 24px; border-radius: 999px; border: 1px solid var(--vien-dam);
  background: var(--nen-2); padding: 0; flex: none; }
.cong-tac::after { content: ''; position: absolute; top: 2px; left: 2px; width: 18px; height: 18px; border-radius: 50%;
  background: var(--the); box-shadow: 0 1px 2px #00000033; transition: left .15s; }
.cong-tac[aria-checked="true"] { background: var(--nhan); border-color: var(--nhan); }
.cong-tac[aria-checked="true"]::after { left: 22px; }
.cong-tac:disabled { opacity: .45; cursor: not-allowed; }
.cong-tac:focus-visible { outline: 2px solid var(--nhan); outline-offset: 2px; }

/* Chip "luôn bật" có ổ khoá */
.chip.khoa .bieu-tuong { width: 12px; height: 12px; stroke-width: 2; }

/* Ba lệnh */
.lenh-ds { display: flex; flex-direction: column; gap: 10px; }
.lenh-o { display: flex; flex-direction: column; gap: 4px; }
.lenh-o .nhan { font-size: 13px; font-weight: 600; color: var(--chu-2); display: flex; gap: 8px;
  align-items: baseline; }
.lenh-o .nhan .nho { font-weight: 400; font-size: 12px; }
.lenh-o code { font-family: var(--mono); font-size: 12.5px; background: var(--nen-lenh); color: var(--chu-lenh);
  padding: 6px 10px; border-radius: 7px; word-break: break-all; }
.lenh-o code.trong { background: var(--nen-3); color: var(--chu-phu); border: 1px dashed var(--vien-dam); }
.lenh-o .o { font-family: var(--mono); font-size: 12.5px; width: 100%; }
.lenh-nut { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; margin-top: 4px; }
.loi-tai-cho { color: var(--do); font-size: 12.5px; }

@media (max-width: 1100px) { .td-luoi { grid-template-columns: 1fr; } }
```

Bản vá `frontend/src/tuyen.js`:

```diff
diff --git a/frontend/src/tuyen.js b/frontend/src/tuyen.js
index 191eb40..ec11d63 100644
--- a/frontend/src/tuyen.js
+++ b/frontend/src/tuyen.js
@@ -5,6 +5,7 @@ import DuAn from './trang/DuAn.vue'
 import KyUc from './trang/KyUc.vue'
 import PheDuyet from './trang/PheDuyet.vue'
 import TongQuan from './trang/TongQuan.vue'
+import TuDong from './trang/TuDong.vue'
 import Usage from './trang/Usage.vue'
 
 // Trang mở đầu là Tổng quan (D17). Ký ức giữ /nho (link cũ từ máy A, Telegram) và thêm bí danh /ky-uc (D38).
@@ -12,6 +13,7 @@ export const tuyen = [
   { path: '/', redirect: '/tong-quan' },
   { path: '/tong-quan', component: TongQuan },
   { path: '/du-an', component: DuAn },
+  { path: '/du-an/:ten', component: TuDong },                                  // TM-4: trang Tự động của dự án
   { path: '/van-phong', component: () => import('./trang/VanPhong.vue') },   // lát 2c: nạp lười (three.js)
   { path: '/cong-viec', component: CongViec },
   { path: '/doi-ngu', component: DoiNgu },
```

Bản vá `frontend/src/thanh/DauTrang.vue`:

```diff
diff --git a/frontend/src/thanh/DauTrang.vue b/frontend/src/thanh/DauTrang.vue
index f32f608..cca6c53 100644
--- a/frontend/src/thanh/DauTrang.vue
+++ b/frontend/src/thanh/DauTrang.vue
@@ -1,11 +1,13 @@
 <script setup>
 // Đầu trang chung của mockup (`.dau-trang`): tiêu đề, một câu mô tả, công cụ bên phải (slot `cong-cu`).
+// Slot `tren-tieu-de` (TM-4): đường dẫn "Dự án / <tên>" trên tiêu đề như mockup trang Tự động.
 defineProps({ tieuDe: { type: String, required: true }, moTa: { type: String, default: '' } })
 </script>
 
 <template>
   <div class="dau-trang">
     <div>
+      <slot name="tren-tieu-de" />
       <h1>{{ tieuDe }}<slot name="sau-tieu-de" /></h1>
       <p v-if="moTa">{{ moTa }}</p>
     </div>
```

Bản vá `frontend/src/kieu/nen.css`:

```diff
diff --git a/frontend/src/kieu/nen.css b/frontend/src/kieu/nen.css
index 0756828..9cb7f73 100644
--- a/frontend/src/kieu/nen.css
+++ b/frontend/src/kieu/nen.css
@@ -8,6 +8,7 @@
   --nen-canh-bao: #fcf3e2; --vien-canh-bao: #efd8a8; --chu-canh-bao: #8a5a0e;
   --nen-estop: #fbefea; --vien-estop: #e0b9ab; --nen-bang-estop: #f8e1da; --chu-bang-estop: #7c2416;
   --nen-lenh: #2f2622; --chu-lenh: #f6e9dc;
+  --xanh-bien: #3b6187; --vien-xanh-bien: #cfdcea;     /* TM-4: viền khối "Sẵn sàng deploy" (mockup them.css) */
   --r: 10px;
   --mono: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace;
   --sans: 'Be Vietnam Pro', -apple-system, 'Segoe UI', Roboto, sans-serif;
```

- [ ] **Step 4: Chạy, mong đợi XANH**

```bash
cd frontend && node --test tests/tu_dong_ghi.test.mjs tests/tu_dong_dong_bo.test.mjs && npm run kiem && npm run build && npm run kiem-dist
```
Xanh thật sau thêm ca Q10: `ℹ tests 11`, `ℹ pass 11`; `npm run kiem` → `ℹ tests 131`, `ℹ pass 131`, `kiem-an-toan: 152 file, …`; `✓ built`; `kiem-dist` sạch (three vẫn chỉ trong chunk lười).

- [ ] **Step 5: Commit**

```bash
git add frontend/src/thanh/tu_dong frontend/src/trang/TuDong.vue frontend/src/kieu/tu-dong.css frontend/tests/tu_dong_ghi.test.mjs frontend/tests/tu_dong_dong_bo.test.mjs frontend/src/tuyen.js frontend/src/thanh/DauTrang.vue frontend/src/kieu/nen.css
git commit -m "feat(giao-dien): trang Tự động của dự án theo mockup D101 (TM-4 Task 4)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

### Task 5: Phê duyệt — dòng "sẵn sàng deploy" có nút Deploy (D101, D129)

**Spec:** `tu-deploy` "Sẵn sàng deploy chờ Đại ca bấm" — Scenario "Hiện ở trang Phê duyệt" (bản đã sửa ở `main` theo D129: dòng "repo-nhap · sẵn sàng deploy" **có nút Deploy** — cùng xác nhận, cùng khoá và cùng kiểm bản như nút ở trang Tự động — và link sang trang Tự động; số đếm do máy chủ). **Mockup:** không có ảnh trang Phê duyệt cho đợt này → khung `.the-duyet` có sẵn (D36; lệch 7).

**Interfaces:** `TEN_PHE_DUYET['san-sang-deploy']`, nhóm cuối của `nhomPheDuyet`; `sanSangDeploy(m) -> {tieuDe, moTa, den}`; `khoaDeploy(m, td, laDaiCa) -> str` ('' = mở; dùng `lyDoKhoaDeploy` của Task 3 trên `kho.tuDong` + phần tử `du_an` cùng tên); component `TheSanSang` (props như `TheBi`, emit `doi`). Consumes mục TM-3 (mục "Hợp đồng TM-4 cần…"), `dungGhiTuDong` (Task 4), `kho.tuDong` (Task 1).

- [ ] **Step 1: Viết test**

Bản vá `frontend/tests/phe_duyet.test.mjs`:

```diff
diff --git a/frontend/tests/phe_duyet.test.mjs b/frontend/tests/phe_duyet.test.mjs
index 2e010ee..05f4ecf 100644
--- a/frontend/tests/phe_duyet.test.mjs
+++ b/frontend/tests/phe_duyet.test.mjs
@@ -1,8 +1,11 @@
 import assert from 'node:assert/strict'
+import { readFileSync } from 'node:fs'
 import { test } from 'node:test'
 import { CHU_CHI_QUET_THU } from '../src/luat.js'
-import { chiTietHe, chipHe, chipNguoiHoi, duongDanTraLoi, khoaThaoTac, linkPrReview, moTaReview, nutDongReview,
-  tieuDeHe } from '../src/luat_phe_duyet.js'
+import { TEN_PHE_DUYET, nhomPheDuyet } from '../src/luat.js'
+import { chiTietHe, chipHe, chipNguoiHoi, duongDanTraLoi, khoaDeploy, khoaThaoTac, linkPrReview, moTaReview,
+  nutDongReview, sanSangDeploy, tieuDeHe } from '../src/luat_phe_duyet.js'
+import { CHU_CHI_DOC } from '../src/luat_tu_dong.js'
 
 const LUC = '2026-10-15T17:12:00Z'   // 00:12 giờ VN
 const CAU_DAO = {
@@ -64,3 +67,38 @@ test('khoá nút: không phải Đại ca khoá không chữ; dự án chỉ qu
   assert.deepEqual(khoaThaoTac(true, true), { khoa: true, chu: CHU_CHI_QUET_THU })
   assert.deepEqual(khoaThaoTac(false, true), { khoa: true, chu: CHU_CHI_QUET_THU })
 })
+
+test('TM-4: dòng "sẵn sàng deploy" (D101) — nhóm cuối, một dòng mỗi dự án, dẫn sang trang Tự động', () => {
+  const m = { loai: 'san-sang-deploy', du_an: 'repo-nhap', bead_id: null, tieu_de: '', uu_tien: null,
+    updated_at: '2026-10-18T14:52:00Z', chi_tiet: { commit: 'a41c07e9d2b8', so_merge: 3 } }
+  assert.equal(TEN_PHE_DUYET['san-sang-deploy'], 'Sẵn sàng deploy')
+  assert.deepEqual(nhomPheDuyet([m, { loai: 'feature-xong', bead_id: 'f' }]).map(([l]) => l),
+    ['feature-xong', 'san-sang-deploy'])
+  assert.deepEqual(sanSangDeploy(m), { tieuDe: 'repo-nhap · sẵn sàng deploy',
+    moTa: 'Bản a41c07e — gồm 3 việc đã merge · merge cuối 21:52', den: '/du-an/repo-nhap' })
+  assert.deepEqual(sanSangDeploy({ ...m, du_an: 'a b', updated_at: null, chi_tiet: {} }),
+    { tieuDe: 'a b · sẵn sàng deploy', moTa: '', den: '/du-an/a%20b' })
+})
+
+test('TM-4 D129: nút Deploy ở dòng "sẵn sàng deploy" — cùng khoá, hộp hỏi, thân như nút trang Tự động', () => {
+  const da = { ten: 'repo-nhap', bat_ghi: true, du_lenh: true }
+  const td = { estop: false, chi_tam_dung: false, tam_dung_tram: null, du_an: [da] }
+  const m = { loai: 'san-sang-deploy', du_an: 'repo-nhap', chi_tiet: { commit: 'a41c07e9d2b8', so_merge: 3 } }
+  assert.equal(khoaDeploy(m, td, true), '')
+  assert.equal(khoaDeploy(m, { ...td, estop: true }, true), 'Estop đang bật')
+  assert.equal(khoaDeploy(m, { ...td, chi_tam_dung: true }, true), 'Cửa ghi đang khoá')        // kênh header
+  assert.equal(khoaDeploy(m, td, false), CHU_CHI_DOC)
+  assert.equal(khoaDeploy(m, { ...td, du_an: [{ ...da, bat_ghi: false }] }, true), CHU_CHI_QUET_THU)
+  assert.equal(khoaDeploy(m, { ...td, du_an: [{ ...da, du_lenh: false }] }, true), 'Chưa khai đủ 3 lệnh')
+  assert.equal(khoaDeploy(m, { ...td, tam_dung_tram: { boi: 'x', luc: '', ly_do: '' } }, true), '')   // D97
+  assert.equal(khoaDeploy(m, null, true), 'Chưa đọc được trạng thái tự động')
+  assert.equal(khoaDeploy(m, null, false), CHU_CHI_DOC)
+  assert.equal(khoaDeploy({ ...m, chi_tiet: {} }, td, true), 'Không có bản mới nào chờ deploy')
+  // Thẻ dùng đúng hàm ghi của trang Tự động (hộp hỏi hoiDeploy, thân {ma_thao_tac, expected_version: "",
+  // expected_commit}, 409/422 hiện câu máy chủ — test ở tu_dong_ghi.test.mjs) + link sang trang Tự động.
+  const vue = readFileSync(new URL('../src/thanh/phe_duyet/TheSanSang.vue', import.meta.url), 'utf8')
+  assert.match(vue, /dungGhiTuDong\(\(\) => null, /)
+  assert.match(vue, /@click="g\.deploy\(muc\.chi_tiet\.commit\)"/)
+  assert.match(vue, /khoaDeploy\(props\.muc, kho\.tuDong, laDaiCa\.value\)/)
+  assert.match(vue, />Mở trang Tự động</)
+})
```

- [ ] **Step 2: Chạy, mong đợi ĐỎ**

```bash
cd frontend && node --test tests/phe_duyet.test.mjs
```
Đỏ thật: `SyntaxError: The requested module '../src/luat_phe_duyet.js' does not provide an export named 'khoaDeploy'` — `ℹ pass 0`, `ℹ fail 1`. (Trên mã Task 5 cũ — chỉ có link, chưa có Deploy — vẫn đỏ đúng câu này: test D129 đòi `khoaDeploy` và nút trong `TheSanSang.vue`.)

- [ ] **Step 3: Viết mã**

Bản vá `frontend/src/luat.js`:

```diff
diff --git a/frontend/src/luat.js b/frontend/src/luat.js
index b430d48..a8f0ca2 100644
--- a/frontend/src/luat.js
+++ b/frontend/src/luat.js
@@ -7,7 +7,8 @@ export const TEN_HANG = {
   'theo-plan': 'Feature đang chạy plan',
   epic: 'Epic',
 }
-const THU_TU_PHE_DUYET = ['escalation', 'decision', 'co-do', 'he', 'cho-review', 'spec', 'feature-xong']
+const THU_TU_PHE_DUYET = ['escalation', 'decision', 'co-do', 'he', 'cho-review', 'spec', 'feature-xong',
+  'san-sang-deploy']
 export const TEN_PHE_DUYET = {
   escalation: 'Bí / escalation',
   decision: 'Decision mở chờ trả lời',
@@ -16,6 +17,7 @@ export const TEN_PHE_DUYET = {
   'cho-review': 'Chờ review để đóng',
   spec: 'Spec chờ duyệt',
   'feature-xong': 'Feature xong, chờ đóng',
+  'san-sang-deploy': 'Sẵn sàng deploy',          // TM-4 (D101): mục do TM-3 thêm vào GET /api/phe-duyet
 }
 
 function soThe(a, b) {
```

Bản vá `frontend/src/luat_phe_duyet.js`:

```diff
diff --git a/frontend/src/luat_phe_duyet.js b/frontend/src/luat_phe_duyet.js
index 1f2f24b..e8cb8c7 100644
--- a/frontend/src/luat_phe_duyet.js
+++ b/frontend/src/luat_phe_duyet.js
@@ -3,6 +3,8 @@
 import { gioPhut, ngayGio } from './dinh_dang.js'
 import { CHU_CHI_QUET_THU, laLinkAnToan } from './luat.js'
 import { tenKhe } from './luat_han_muc.js'
+import { lyDoKhoaDeploy } from './luat_trang_tu_dong.js'
+import { lyDoKhoaGhi } from './luat_tu_dong.js'
 
 // Sự kiện của mục "Hệ cần xem" (tram/suy/phe_duyet.py, phe_duyet_khe.py): [chữ chip, tiêu đề khi mục không gắn bead].
 const SU_KIEN_HE = {
@@ -81,3 +83,22 @@ export function nutDongReview(m) {
 export function khoaThaoTac(laDaiCa, chiQuetThu) {
   return { khoa: !laDaiCa || Boolean(chiQuetThu), chu: chiQuetThu ? CHU_CHI_QUET_THU : '' }
 }
+
+// Dòng "sẵn sàng deploy" (spec tu-deploy "Hiện ở trang Phê duyệt", D101, D129): một dòng mỗi dự án, có nút Deploy và
+// link sang trang Tự động. `chi_tiet` {commit, so_merge} do TM-3 dựng.
+export function sanSangDeploy(m) {
+  const c = ct(m)
+  const moTa = c.commit ? [`Bản ${String(c.commit).slice(0, 7)} — gồm ${c.so_merge} việc đã merge`,
+    m.updated_at ? `merge cuối ${gioPhut(m.updated_at)}` : ''].filter(Boolean).join(' · ') : ''
+  return { tieuDe: `${m.du_an} · sẵn sàng deploy`, moTa, den: '/du-an/' + encodeURIComponent(m.du_an) }
+}
+
+// Khoá nút Deploy ở dòng đó (D129): cùng thứ tự với nút trang Tự động (`lyDoKhoaDeploy`: estop → thiếu lệnh → danh
+// tính / cửa ghi `header` / chỉ quét thử), trạng thái lấy từ GET /api/tu-dong (`kho.tuDong`). Chưa đọc được → khoá.
+export function khoaDeploy(m, td, laDaiCa) {
+  const da = td && (td.du_an || []).find((x) => x.ten === m.du_an)
+  if (!da) return lyDoKhoaGhi(null, laDaiCa)
+  if (!ct(m).commit) return 'Không có bản mới nào chờ deploy'
+  return lyDoKhoaDeploy({ estop: td.estop, chi_tam_dung: td.chi_tam_dung, bat_ghi: da.bat_ghi, du_lenh: da.du_lenh,
+    dang_deploy: null }, laDaiCa)
+}
```

Tạo mới `frontend/src/thanh/phe_duyet/TheSanSang.vue` (nguyên văn):

```vue
<script setup>
import { computed } from 'vue'
import { kho } from '../../kho.js'
import { khoaDeploy, sanSangDeploy } from '../../luat_phe_duyet.js'
import { dungGhiTuDong } from '../tu_dong/ghi_tu_dong.js'

// Thẻ "sẵn sàng deploy" ở Phê duyệt (spec tu-deploy "Hiện ở trang Phê duyệt", D101, D129). Mockup 2026-10-18 không vẽ
// trang này → khung `.the-duyet` sẵn có (D36). Nút Deploy dùng đúng hàm ghi của trang Tự động (`ghi_tu_dong.js`: cùng
// hộp hỏi, cùng thân {ma_thao_tac, expected_version: "", expected_commit}, 409/422 hiện câu máy chủ tại chỗ) và cùng
// khoá (`khoaDeploy`); thành công → emit('doi') để trang tải lại. Link sang trang Tự động để xem đủ chi tiết.
const props = defineProps({
  muc: { type: Object, required: true },
  khoa: { type: Boolean, default: false },
  chuKhoa: { type: String, default: '' },
})
const emit = defineEmits(['doi'])
const t = computed(() => sanSangDeploy(props.muc))
const laDaiCa = computed(() => Boolean(kho.trangThai && kho.trangThai.la_dai_ca))
const lyDo = computed(() => khoaDeploy(props.muc, kho.tuDong, laDaiCa.value))
const g = dungGhiTuDong(() => null, async () => emit('doi'), () => props.muc.du_an)
</script>

<template>
  <article class="the the-duyet">
    <div>
      <div class="tren"><span class="chip">{{ muc.du_an }}</span><span class="chip pr-mo">sẵn sàng deploy</span></div>
      <div class="tieu-de">{{ t.tieuDe }}</div>
      <div v-if="t.moTa" class="nho">{{ t.moTa }}</div>
    </div>
    <div class="hanh-dong">
      <button type="button" class="nut chinh" :disabled="Boolean(lyDo) || g.dangGui.value" :title="lyDo || null"
              @click="g.deploy(muc.chi_tiet.commit)">{{ g.dangGui.value ? 'Đang gửi…' : 'Deploy' }}</button>
      <router-link class="nut" :to="t.den">Mở trang Tự động</router-link>
    </div>
    <p v-if="lyDo" class="nho dong-day">{{ lyDo }}</p>
    <p v-if="g.loi.value" class="loi dong-day" role="alert">{{ g.loi.value }}</p>
  </article>
</template>
```

Bản vá `frontend/src/trang/PheDuyet.vue`:

```diff
diff --git a/frontend/src/trang/PheDuyet.vue b/frontend/src/trang/PheDuyet.vue
index f68cc2b..6a539d7 100644
--- a/frontend/src/trang/PheDuyet.vue
+++ b/frontend/src/trang/PheDuyet.vue
@@ -10,12 +10,13 @@ import TheBi from '../thanh/phe_duyet/TheBi.vue'
 import TheFeatureXong from '../thanh/phe_duyet/TheFeatureXong.vue'
 import TheHe from '../thanh/phe_duyet/TheHe.vue'
 import TheReview from '../thanh/phe_duyet/TheReview.vue'
+import TheSanSang from '../thanh/phe_duyet/TheSanSang.vue'
 import TheSpec from '../thanh/phe_duyet/TheSpec.vue'
 import '../kieu/phe-duyet.css'
 
 // Trang Phê duyệt (mockup trang.js vePheDuyet, anh-phe-duyet.png): nhóm theo độ gấp, mỗi mục một thẻ `.the-duyet`.
 const THE = { he: TheHe, escalation: TheBi, decision: TheBi, 'cho-review': TheReview, 'co-do': TheReview,
-  spec: TheSpec, 'feature-xong': TheFeatureXong }
+  spec: TheSpec, 'feature-xong': TheFeatureXong, 'san-sang-deploy': TheSanSang }      // TM-4: D101
 const MO_TA = 'Việc chờ Đại ca, sắp theo độ gấp. Duyệt / Trả về ghi thẳng vào beads với tác nhân dai-ca/dashboard.'
 const ds = ref([])
 const loi = ref('')
```

- [ ] **Step 4: Chạy, mong đợi XANH**

```bash
cd frontend && node --test tests/phe_duyet.test.mjs && npm run kiem && npm run build && npm run kiem-dist
```
Xanh thật: `ℹ tests 6`, `ℹ pass 6` (file test); `npm run kiem` → `ℹ tests 133`, `ℹ pass 133`, `kiem-an-toan: 153 file, …`; `kiem-dist` sạch. Test cũ `luat.test.mjs`, `spec.test.mjs` (thứ tự nhóm) vẫn xanh.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/luat.js frontend/src/luat_phe_duyet.js frontend/src/thanh/phe_duyet/TheSanSang.vue frontend/src/trang/PheDuyet.vue frontend/tests/phe_duyet.test.mjs
git commit -m "feat(giao-dien): dòng sẵn sàng deploy có nút Deploy ở Phê duyệt (TM-4 Task 5, D129)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

### Task 6: Dữ liệu giả cho kiểm tay trang Tự động

**Mục đích:** `tests/chay_thu_giao_dien.py` (máy chủ kiểm tay, CSP thật) có đủ trạng thái để so mockup. Cài đặt của dự án `tram` (đóng vai `repo-nhap`) ghi THẬT qua `tram.tu_dong.luu.doi_cai_dat`; khoá TM-2/TM-3 là bản giả **ghép vào phản hồi thật, khoá thật thắng**; dòng Phê duyệt giả **không nối khi đã có hàng thật** (Codex vòng 1, mục Nhỏ) — trạm đã có TM-3 (`"san-sang-deploy" in THU_TU`) thì không thêm, dự án đã có hàng thật thì không thêm. Vì TM-4 ghép SAU TM-3, khi code mặc định trang chỉ hiện trạng thái thật (rỗng trong dữ liệu kiểm tay); cờ `--gia-deploy` (CHỈ ĐỂ XEM) cho khoá/hàng giả THAY khoá/hàng thật của dự án giả (không bao giờ hai hàng) để so mockup "sẵn sàng deploy" và nút Deploy ở Phê duyệt; dự án `ke-toan` là "chỉ quét thử" (`pt.bat_ghi`). Cờ `--kenh-that` CHỈ ĐỂ XEM như khi kênh `unix-socket` (TCP khi đó mất danh tính Đại ca → trang ở chế độ "Chỉ đọc" — đúng để kiểm mốc 5.2 "khi không phải Đại ca").

- [ ] **Step 1: Viết test**

Tạo mới `tests/test_du_lieu_giao_dien_tu_dong.py` (nguyên văn):

```python
"""TM-4: dữ liệu GIẢ cho kiểm tay trang Tự động (`tests/chay_thu_giao_dien.py`) — cài đặt thật qua hàm TM-1 (`luu.py`),
khoá TM-2/TM-3 chưa có (`cho_dai_ca`, `san_sang`, `dang_deploy`, `lich_su`, `dem_hong`, dòng Phê duyệt) là bản giả và
KHÔNG đè khoá/hàng thật khi TM-2/TM-3 đã ghép (Codex vòng 1, mục Nhỏ), trừ cờ xem `--gia-deploy` (`ep=True`)."""
from du_lieu_giao_dien import RONG, gieo_tu_dong, them_gia, them_phe_duyet_gia
from tram.phieu.kho import KhoPhieu
from tram.suy import phe_duyet
from tram.tu_dong.luu import doc_trang_thai, lich_su_doi


def test_gieo_tu_dong_dung_trang_thai_mockup(tmp_path):
    kho = KhoPhieu(tmp_path / "sk.db")
    gieo_tu_dong(kho)
    tt = doc_trang_thai(kho.db, "tram")
    assert tt.cai_dat.tu_merge and not tt.cai_dat.tu_deploy and tt.cai_dat.du_lenh and tt.tam_dung_du_an is None
    assert [d["doi"][0]["truong"] for d in lich_su_doi(kho.db, "tram")] == ["tu_merge", "lenh_kiem_song", "lenh_deploy"]
    assert doc_trang_thai(kho.db, "hr-codex").phien_ban == "0"
    kho.close()


def test_khoa_that_thang_khoa_gia():
    ct = them_gia("tram", {"du_an": "tram", "dem_hong": 2})
    assert ct["dem_hong"] == 2 and ct["san_sang"]["so_merge"] == 2 and len(ct["cho_dai_ca"]) == 4
    # dạng TM-2 (`tram/suy/tu_merge.py`): mã + nhãn + mức của `tu_merge_xet.NHAN` / `MUC`
    assert ct["cho_dai_ca"][2]["ly_do"] == [{"ma": "schema_duong_dan", "nhan": "Cấu trúc DB — luôn chờ Đại ca",
                                            "muc": "loi"}]
    assert all({"bead_id", "tieu_de", "luc"} <= set(c) for c in ct["cho_dai_ca"])
    # dạng TM-3 (`tram/deploy/hien_thi.py`): sáu khoá, `loai` ∈ LOAI_LICH_SU (+ `huy` nếu Đại ca chọn câu 5a), `ai` ∈ AI
    assert all(set(r) == {"luc", "loai", "bead_id", "commit", "chi_tiet", "ai"} for r in ct["lich_su"])
    assert {r["ai"] for r in ct["lich_su"]} <= {"dai_ca", "dai_ca_bam", "tu_deploy", "tram"}
    assert [r["ai"] for r in ct["lich_su"] if r["loai"] == "san_sang"] == ["tram"]
    assert set(ct["san_sang"]) == {"commit", "so_merge", "bead_ids", "luc", "commit_dang_chay"}
    assert {r["loai"] for r in ct["lich_su"]} >= {"tu_merge", "san_sang", "deploy_lui", "deploy_dat"}
    assert them_gia("tram", {"ten": "tram"}, tom_tat=True) == {"ten": "tram", "san_sang": True, "dem_hong": 1}
    assert them_gia("ke-toan", {}) == {"cho_dai_ca": [], "san_sang": None, "dang_deploy": None, "lich_su": [],
                                       "dem_hong": 0}
    # TM-3 đã ghép (khoá thật có, `san_sang: None`): mặc định thật thắng; `ep` (--gia-deploy) giả thay cho dự án giả
    assert them_gia("tram", {"du_an": "tram", "san_sang": None})["san_sang"] is None
    assert them_gia("tram", {"du_an": "tram", "san_sang": None}, ep=True)["san_sang"] == ct["san_sang"]
    assert them_gia("ke-toan", {"san_sang": None}, ep=True) == RONG


def test_phe_duyet_gia_khong_noi_khi_da_co_hang_that(monkeypatch):
    ct = them_gia("tram", {"du_an": "tram"})
    [m] = them_phe_duyet_gia([])                                            # trạm chưa có TM-3: thêm một dòng giả
    assert (m["loai"], m["du_an"], m["updated_at"]) == ("san-sang-deploy", "tram", ct["san_sang"]["luc"])
    assert m["chi_tiet"] == ct["san_sang"]                                  # TM-3: chi_tiet = toàn bộ san_sang
    that = {**m, "updated_at": "2026-10-18T10:00:00Z", "chi_tiet": {"commit": "b" * 40, "so_merge": 1}}
    khac = {**m, "loai": "escalation", "bead_id": "bs-1"}
    assert them_phe_duyet_gia([khac, that]) == [khac, that]                 # đã có hàng thật của tram: không nối
    assert them_phe_duyet_gia([khac, that], ep=True) == [khac, m]           # --gia-deploy: thay, không trùng
    monkeypatch.setattr(phe_duyet, "THU_TU", (*phe_duyet.THU_TU, "san-sang-deploy"))
    assert them_phe_duyet_gia([khac]) == [khac]                             # TM-3 đã ghép: chỉ trạng thái thật
```

- [ ] **Step 2: Chạy, mong đợi ĐỎ**

```bash
tests/chan_host/chay.sh -q tests/test_du_lieu_giao_dien_tu_dong.py
```
Đỏ thật: `E   ImportError: cannot import name 'RONG' from 'du_lieu_giao_dien' (…/tests/du_lieu_giao_dien.py)`; nhật ký chặn 0 dòng mới. (Trên dữ liệu giả cũ — có `RONG`, `them_gia`, `muc_phe_duyet_gia` — đỏ `ImportError: cannot import name 'them_phe_duyet_gia' … Did you mean: 'muc_phe_duyet_gia'?`.)

- [ ] **Step 3: Viết mã**

Bản vá `tests/du_lieu_giao_dien.py`:

```diff
diff --git a/tests/du_lieu_giao_dien.py b/tests/du_lieu_giao_dien.py
index d24e11f..08fe663 100644
--- a/tests/du_lieu_giao_dien.py
+++ b/tests/du_lieu_giao_dien.py
@@ -1,6 +1,8 @@
 """Dữ liệu GIẢ cho máy chủ kiểm giao diện lát 2f (`tests/chay_thu_giao_dien.py`) — CHỈ DÙNG KHI KIỂM TAY, không phải
-test pytest. Bám mockup `docs/mockup/2026-10-15-giao-dien/du-lieu.js`, `du-lieu-ky-uc-usage.js`; giờ lùi từ `LUC`."""
+test pytest. Bám mockup `docs/mockup/2026-10-15-giao-dien/du-lieu.js`, `du-lieu-ky-uc-usage.js`; giờ lùi từ `LUC`.
+TM-4: trang Tự động theo mockup `docs/mockup/2026-10-18-tu-merge-tu-deploy/du-lieu.js` (`gieo_tu_dong`, `them_gia`)."""
 import random
+from dataclasses import replace
 from datetime import datetime, timedelta, timezone
 
 from bead_gia import bead, notes_ban_giao
@@ -10,6 +12,8 @@ from tram.phieu.cau_dao import ngat_cau_dao
 from tram.phieu.khe import bat_tat_khe, dang_ky_khe
 from tram.phieu.kho import chuoi_gio as iso
 from tram.phieu.nhip_tim import ghi_nhip
+from tram.suy import phe_duyet
+from tram.tu_dong.luu import doi_cai_dat
 
 LUC = datetime.now(timezone.utc).replace(microsecond=0)
 P, NGAY = timedelta(minutes=1), timedelta(days=1)
@@ -125,3 +129,73 @@ def gieo(kho) -> str:
             ghi_nhip(kho, f"B/{t}", luc=LUC, giao_id=None, luot=None, buoc_tho="ranh",
                      han_muc=HanMuc(khe_id=f"B/{t}", cua_so=cs, nguon="stream"))
     return g3
+
+
+# ---- TM-4: trang Tự động (mockup 2026-10-18). "tram" đóng vai repo-nhap; "ke-toan" chỉ quét thử ----
+LENH_TRAM = {"lenh_deploy": "/Users/Shared/tram-deploy/tram/deploy.sh",
+             "lenh_kiem_song": "/Users/Shared/tram-deploy/tram/kiem-song.sh",
+             "lenh_lui": "/Users/Shared/tram-deploy/tram/lui.sh"}
+
+
+def gieo_tu_dong(kho) -> None:
+    """Cài đặt THẬT qua hàm TM-1: Đại ca khai lệnh deploy + lùi, rồi lệnh kiểm còn sống, rồi bật tự merge."""
+    for doi in ({"lenh_deploy": LENH_TRAM["lenh_deploy"], "lenh_lui": LENH_TRAM["lenh_lui"]},
+                {"lenh_kiem_song": LENH_TRAM["lenh_kiem_song"]}, {"tu_merge": True}):
+        doi_cai_dat(kho.db, "tram", lambda c, d=doi: replace(c, **d), tac_nhan="dai-ca/dashboard")
+
+
+C_MOI, C_9B, C_77, C_5D = "a41c07e" + "1" * 33, "9be2d40" + "2" * 33, "77f0a19" + "3" * 33, "5d3e8b2" + "4" * 33
+RONG = {"cho_dai_ca": [], "san_sang": None, "dang_deploy": None, "lich_su": [], "dem_hong": 0}
+# Khoá TM-2/TM-3 hứa thêm vào GET /api/du-an/<ten>/tu-dong — GIẢ tới khi hai lát đó ghép (khoá thật thắng, `them_gia`).
+TU_DONG_GIA = {"tram": {
+    "cho_dai_ca": [  # dạng TM-2 (`tram/suy/tu_merge.cho_dai_ca`; mã/nhãn/mức như `tu_merge_xet.NHAN`, `MUC`)
+        {"bead_id": "bs-17", "tieu_de": "Đổi chữ nút Lưu", "luc": iso(LUC - 3 * P),
+         "ly_do": [{"ma": "ci_dang_chay", "nhan": "CI đang chạy — xét lại vòng sau", "muc": "tat"}]},
+        {"bead_id": "bs-14", "tieu_de": "Sửa định dạng ngày ở trang danh sách", "luc": iso(LUC - 9 * P),
+         "ly_do": [{"ma": "ci_do", "nhan": "CI chưa xanh", "muc": "can_nguoi"}]},
+        {"bead_id": "bs-16", "tieu_de": "Thêm cột ghi chú cho bảng khách", "luc": iso(LUC - 14 * P),
+         "ly_do": [{"ma": "schema_duong_dan", "nhan": "Cấu trúc DB — luôn chờ Đại ca", "muc": "loi"}]},
+        {"bead_id": "bs-15", "tieu_de": "Làm tròn tổng tiền hoá đơn", "luc": iso(LUC - 31 * P),
+         "ly_do": [{"ma": "hang_rao_tien", "nhan": "Chạm hàng rào: tiền/giá", "muc": "can_nguoi"},
+                   {"ma": "hang_rao_co_do", "nhan": "Cờ đỏ", "muc": "can_nguoi"}]}],
+    "san_sang": {"commit": C_MOI, "so_merge": 2, "bead_ids": ["bs-11", "bs-12"], "luc": iso(LUC - 22 * P),
+                 "commit_dang_chay": C_5D},
+    "dang_deploy": None, "dem_hong": 1,
+    "lich_su": [  # dạng TM-3 (`tram/deploy/hien_thi.lich_su`): chi_tiet chỉ mã thoát, giây, số PR, commit ngắn
+        {"luc": iso(LUC - 22 * P), "loai": "san_sang", "bead_id": None, "commit": C_MOI,
+         "chi_tiet": "gồm 2 việc đã merge", "ai": "tram"},
+        {"luc": iso(LUC - 22 * P), "loai": "tu_merge", "bead_id": "bs-12", "commit": C_MOI,
+         "chi_tiet": "PR #31", "ai": "tram"},
+        {"luc": iso(LUC - 127 * P), "loai": "tu_merge", "bead_id": "bs-11", "commit": C_9B,
+         "chi_tiet": "PR #30", "ai": "tram"},
+        {"luc": iso(LUC - 200 * P), "loai": "huy", "bead_id": None, "commit": C_9B,
+         "chi_tiet": "Estop đang bật", "ai": "dai_ca_bam"},
+        {"luc": iso(LUC - 344 * P), "loai": "deploy_lui", "bead_id": None, "commit": C_77,
+         "chi_tiet": "deploy: mã thoát 0 · 51 giây → kiểm còn sống: mã thoát 22 · 34 giây → lùi: mã thoát 0 · 40 giây"
+                     " → kiểm còn sống sau lùi: mã thoát 0 · 2 giây (bản trước 5d3e8b2)", "ai": "dai_ca_bam"},
+        {"luc": iso(LUC - 654 * P), "loai": "deploy_dat", "bead_id": None, "commit": C_5D,
+         "chi_tiet": "deploy: mã thoát 0 · 48 giây → kiểm còn sống: mã thoát 0 · 3 giây", "ai": "dai_ca_bam"}]}}
+
+
+def them_gia(ten: str, that: dict, *, tom_tat: bool = False, ep: bool = False) -> dict:
+    """Ghép khoá giả TM-2/TM-3 vào phản hồi thật. Mặc định khoá thật (khi đã có) thắng; `ep` (cờ `--gia-deploy`, CHỈ ĐỂ
+    XEM): khoá giả thay khoá thật của dự án có trong `TU_DONG_GIA`. `tom_tat`: phần tử GET /api/tu-dong."""
+    gia = TU_DONG_GIA.get(ten, RONG)
+    if tom_tat:
+        gia = {"san_sang": gia["san_sang"] is not None, "dem_hong": gia["dem_hong"]}
+    return {**that, **gia} if ep and ten in TU_DONG_GIA else {**gia, **that}
+
+
+def them_phe_duyet_gia(that: list[dict], *, ep: bool = False) -> list[dict]:
+    """Dòng "sẵn sàng deploy" GIẢ ở GET /api/phe-duyet (D101; dạng TM-3: chi_tiet = san_sang). Không nối hàng giả khi đã
+    có hàng thật (Codex vòng 1, mục Nhỏ): mặc định chỉ thêm khi trạm chưa có TM-3 (`THU_TU` chưa có loại này) và dự án
+    chưa có hàng thật; `ep` (CHỈ ĐỂ XEM): bỏ hàng thật của dự án giả rồi thêm hàng giả — không bao giờ trùng."""
+    gia = [{"loai": "san-sang-deploy", "du_an": ten, "bead_id": None, "tieu_de": "", "uu_tien": None,
+            "updated_at": v["san_sang"]["luc"], "chi_tiet": dict(v["san_sang"])}
+           for ten, v in TU_DONG_GIA.items() if v["san_sang"]]
+    if ep:
+        return [m for m in that if m["loai"] != "san-sang-deploy" or m["du_an"] not in TU_DONG_GIA] + gia
+    if "san-sang-deploy" in phe_duyet.THU_TU:          # TM-3 đã ghép: trạng thái thật quyết, không thêm hàng giả
+        return that
+    co_that = {m["du_an"] for m in that if m["loai"] == "san-sang-deploy"}
+    return that + [m for m in gia if m["du_an"] not in co_that]
```

Bản vá `tests/chay_thu_giao_dien.py`:

```diff
diff --git a/tests/chay_thu_giao_dien.py b/tests/chay_thu_giao_dien.py
index 8679024..ceb02c7 100644
--- a/tests/chay_thu_giao_dien.py
+++ b/tests/chay_thu_giao_dien.py
@@ -3,7 +3,10 @@
 `uv run python tests/chay_thu_giao_dien.py [cong] [--dai-ca]` (mặc định 7798) sau `npm run build`. Mọi thứ trong thư mục
 tạm (TRAM_HOME, su-kien.db, TRAM_REPO/du-an, HOME giả có plist); bd, launchctl, security, memory service đều giả — không
 mạng, không ~/.tram, Keychain, launchctl, beads thật. `--dai-ca`: lớp ASGI CHỈ ĐỂ KIỂM TAY, gắn `Tailscale-User-Login`
-của Đại ca giả + đổi Origin cục bộ thành máy B giả (xem Cài đặt, Ký ức, nút ghi). Không phải test pytest."""
+của Đại ca giả + đổi Origin cục bộ thành máy B giả (xem Cài đặt, Ký ức, nút ghi). Không phải test pytest.
+TM-4 `--kenh-that`: CHỈ ĐỂ XEM trang Tự động như khi cửa ghi là `unix-socket` (nút mở); ghi qua cổng TCP này bị 403.
+TM-4 `--gia-deploy`: CHỈ ĐỂ XEM — khoá/hàng giả TM-2/TM-3 THAY khoá/hàng thật của dự án giả (dùng khi TM-3 đã ghép);
+không có cờ thì khoá/hàng thật thắng, giả chỉ lấp chỗ trạm chưa có."""
 import os
 import sys
 import tempfile
@@ -22,7 +25,9 @@ import yaml  # noqa: E402
 from api_gia import LOGIN, MAY_B, tao_pt  # noqa: E402
 from bd_gia import BdGia  # noqa: E402
 from bead_gia import bead  # noqa: E402
-from du_lieu_giao_dien import GIA, LUC, cac_bead, gieo, iso, ky_uc  # noqa: E402
+from du_lieu_giao_dien import (GIA, LUC, cac_bead, gieo, gieo_tu_dong, iso, ky_uc,  # noqa: E402
+                               them_gia, them_phe_duyet_gia)
+from tram.api import tuyen_doc, tuyen_tu_dong  # noqa: E402
 from tram.api.app import tao_app  # noqa: E402
 from tram.cau_hinh.du_an import nap_du_an  # noqa: E402
 from tram.phieu.kho import KhoPhieu  # noqa: E402
@@ -101,21 +106,35 @@ def moi_truong() -> None:
     he_thong._CHUNG = he_thong.DocHeThong(chay=chay_gia, home=TAM / "home", uid=501)
     ds = [bead(i, title=t, status=st, labels=["san-sang"], chan_boi=cb) for i, t, st, cb in SAN_SANG]
     san_sang.CHUNG = san_sang.BangSanSang(doc_bead=lambda: ds, which=lambda lenh: f"/gia/bin/{lenh}")
+    tu_dong_gia("--gia-deploy" in sys.argv)
+
+
+def tu_dong_gia(ep: bool) -> None:
+    """TM-4: ghép khoá giả TM-2/TM-3 vào GET tự động và dòng "sẵn sàng deploy" ở Phê duyệt (khoá/hàng thật thắng,
+    `ep` thì giả thay thật — `them_gia`, `them_phe_duyet_gia`)."""
+    ct, tt, gom = tuyen_tu_dong.chi_tiet_du_an, tuyen_tu_dong.tom_tat_du_an, tuyen_doc.gom_phe_duyet
+    tuyen_tu_dong.chi_tiet_du_an = lambda kho, ten, **kw: them_gia(ten, ct(kho, ten, **kw), ep=ep)
+    tuyen_tu_dong.tom_tat_du_an = lambda kho, ten, **kw: them_gia(ten, tt(kho, ten, **kw), tom_tat=True, ep=ep)
+    tuyen_doc.gom_phe_duyet = lambda *a, **kw: them_phe_duyet_gia(gom(*a, **kw), ep=ep)
 
 
 def main() -> None:
-    cong = int(next((a for a in sys.argv[1:] if a != "--dai-ca"), 7798))
+    cong = int(next((a for a in sys.argv[1:] if not a.startswith("--")), 7798))
     dist = Path(__file__).resolve().parents[1] / "frontend" / "dist"
     moi_truong()
     kho = KhoPhieu(TAM / "sk.db")
     g3 = gieo(kho)
+    gieo_tu_dong(kho)
     kho.close()
     pt = tao_pt(TAM, {t: BdGia(ds) for t, ds in cac_bead(g3).items()}, thu_muc_tinh=dist)
     ch = replace(pt.cau_hinh, telegram=replace(pt.cau_hinh.telegram, chat_id="1", gio_yen_lang="23:00–07:00"))
     pt = replace(pt, mo_kho_phieu=lambda: KhoPhieu(TAM / "sk.db"), dong_ho=lambda: LUC, nho=NhoGia(ky_uc()),
                  usage=replace(pt.usage, gia=GIA), cau_hinh=ch,
-                 bo_giao=SimpleNamespace(cac_du_an=lambda: [nap_du_an(t) for t in DU_AN], kho_git=lambda da: None))
+                 bo_giao=SimpleNamespace(cac_du_an=lambda: [nap_du_an(t) for t in DU_AN], kho_git=lambda da: None),
+                 bat_ghi=lambda ten: ten != "ke-toan")                  # TM-4: ke-toan "chỉ quét thử"
     app = tao_app(pt, cong=cong)
+    if "--kenh-that" in sys.argv:
+        app.state.kenh_ghi = "unix-socket"
     print(f"Dữ liệu giả ở {TAM} — mở http://127.0.0.1:{cong}/ (Ctrl+C để dừng)", flush=True)
     uvicorn.run(DaiCaGia(app, cong) if "--dai-ca" in sys.argv else app, host="127.0.0.1", port=cong,
                 server_header=False, log_level="warning")
```

- [ ] **Step 4: Chạy, mong đợi XANH**

```bash
tests/chan_host/chay.sh -q tests/test_du_lieu_giao_dien_tu_dong.py
```
Đã chạy: `3 passed`, nhật ký chặn 0 dòng mới. Sau đó chạy cả bộ `tests/chan_host/chay.sh -q`; ở môi trường phiên tiếp tục, cửa kiểm cả bộ còn bị lỗi nền thu hồi tiến trình (mục Kiểm chứng), chưa được ghi là xanh. Tổng thu thập dự kiến trên TM-1 mới: 3425 (3422 + 3), không phải số passed.

- [ ] **Step 5: Commit**

```bash
git add tests/du_lieu_giao_dien.py tests/chay_thu_giao_dien.py tests/test_du_lieu_giao_dien_tu_dong.py
git commit -m "test(giao-dien): dữ liệu giả cho kiểm tay trang Tự động (TM-4 Task 6)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

### Task 7: Kiểm trên trình duyệt dưới CSP thật, so mockup; DESIGN_SYSTEM

**Mốc:** 5.1, 5.2 — "mở dưới CSP thật với `tests/chay_thu_giao_dien.py`, console không lỗi CSP, đi tới được từ thanh bên"; "thử khi không phải Đại ca (mọi nút khoá, 'Chỉ đọc')".

- [ ] **Step 1: Sửa tài liệu**

Bản vá `docs/DESIGN_SYSTEM.md`:

```diff
diff --git a/docs/DESIGN_SYSTEM.md b/docs/DESIGN_SYSTEM.md
index 594ba50..2684434 100644
--- a/docs/DESIGN_SYSTEM.md
+++ b/docs/DESIGN_SYSTEM.md
@@ -54,6 +54,9 @@ Lớp ở `frontend/src/kieu/chung.css`:
 - Việc **dừng khẩn cấp (estop)**: nút trên thanh trên; bật có hộp xác nhận của trình duyệt, khi bật có `BangEstop`
   đỏ dưới thanh trên; chỉ Đại ca bấm được.
 - Thao tác khó đảo ngược hiện đang dùng hộp xác nhận (`HopKhe` bật/tắt khe, `HopViSao` lý do kéo thẻ); giữ cách đó cho thao tác tương tự.
+- **TẠM DỪNG tự merge / tự deploy** (mockup `docs/mockup/2026-10-18-tu-merge-tu-deploy/`, D101): `.nut-estop.vang` — cùng hình
+  nút Estop, màu vàng; toàn trạm ở thanh trên cạnh Estop, khi bật có `BangTamDung` vàng; của dự án ở đầu trang Tự động.
+  Công tắc bật/tắt: `CongTac` (`role="switch"`, lớp `.cong-tac`); bật và tắt đều hỏi lại bằng hộp xác nhận như estop.
 
 ## Phản hồi sau khi ghi
 - Mọi thao tác ghi đi qua `frontend/src/api.js`: `ghi()` gắn `X-Tram: 1`; `thanGhi()` gắn `ma_thao_tac` (để thử lại không
@@ -149,6 +152,8 @@ Tên và vai trò (code ở `frontend/src/thanh/`; tìm trước khi tự viết
 | `DongThoiGian`, `SuKienNho` | dòng thời gian bead, sự kiện ký ức |
 | `BangUsage`, `usage/BieuDoUsage` | bảng và biểu đồ usage |
 | `LenhCli` | lệnh CLI gợi ý + nút sao chép |
+| `BangTamDung`, `tu_dong/CongTac` | băng vàng TẠM DỪNG toàn trạm; công tắc `role="switch"` |
+| `tu_dong/*` | khối trang Tự động `#/du-an/<ten>`: sẵn sàng deploy, chờ Đại ca, lịch sử, cài đặt, ngăn lịch sử đổi |
 | `cai_dat/*`, `phe_duyet/*`, `tong_quan/*`, `usage/*` | khối riêng từng trang; dùng lại lớp chung ở `chung.css` |
 
 ## Khi cần thứ chưa có ở đây
```

- [ ] **Step 2: Kịch bản trình duyệt** (cục bộ `127.0.0.1`, không mạng; tram-api phục vụ `frontend/dist/` với CSP thật)

```bash
cd frontend && npm run build && cd ..
uv run python tests/chay_thu_giao_dien.py 7798 --dai-ca          # Đại ca giả, kênh header (cửa tạm)
uv run python tests/chay_thu_giao_dien.py 7798 --dai-ca --kenh-that   # chỉ để xem: kênh unix-socket → "Chỉ đọc"
# Khi TM-3 đã ghép (thứ tự ghép chuẩn): thêm --gia-deploy để có trạng thái "sẵn sàng deploy" giả thay trạng thái thật.
```
Kiểm (kết quả đã chạy ghi ở mục "Kiểm chứng plan"):
1. `#/du-an` → thẻ có hàng chip + "Tự động →"; `tram` có "1 sẵn sàng deploy"; mục "Dự án" sáng ở `#/du-an/tram` (so `anh-du-an.png`).
2. `#/du-an/tram` (kênh header) → khối "Cửa ghi còn tạm — chỉ bấm được TẠM DỪNG", công tắc/Sửa 3 lệnh/Deploy khoá, Deploy kèm "Cửa ghi đang khoá." (so `anh-tu-dong-cua-tam.png`); bấm "Tạm dừng dự án" → nhận (D87), khối "Dự án đang tạm dừng", nút Tiếp tục khoá kèm "Cửa ghi còn tạm — Tiếp tục cần cửa ghi unix-socket".
3. Thanh trên "Tạm dừng tự động" → băng vàng trên mọi trang, chip "tạm dừng toàn trạm" ở thẻ Dự án, Tiếp tục khoá (kênh header) (so `anh-tam-dung-toan-tram.png`).
4. `#/du-an/ke-toan` → khối "Dự án đang chỉ quét thử", chip "chỉ quét thử", "Chưa từng đổi — đang dùng mặc định", `0 / 3` (so `anh-hr-codex-khoa.png`).
5. `--kenh-that`: thẻ người dùng "Chỉ đọc", mọi nút ghi trên trang Tự động và nút TẠM DỪNG toàn trạm `disabled` (title "Chỉ đọc: thiếu danh tính Đại ca"); "Xem lịch sử đổi" mở ngăn bên 3 dòng ai/giờ/trước → sau.
6. `#/phe-duyet` → nhóm "Sẵn sàng deploy 1" (đúng MỘT thẻ), thẻ "tram · sẵn sàng deploy" có nút "Deploy" (kênh `header`: khoá, dưới thẻ "Cửa ghi đang khoá"; `--kenh-that`: "Chỉ đọc: thiếu danh tính Đại ca") và "Mở trang Tự động" → `#/du-an/tram`; số đếm thanh bên tăng.
8. (Codex Q10) Ở `#/du-an/tram` mở "Sửa 3 lệnh" (kênh `header` nút khoá — bỏ `disabled` qua DevTools chỉ để mở form), gõ nháp, đổi hash sang `#/du-an/ke-toan` → form đóng, tiêu đề/lệnh của `ke-toan`; quay lại `tram` → form đóng, lệnh đã lưu (không còn nháp); `#/du-an/khong-co` → "Không có dự án này".
7. Console: không lỗi CSP; màn hẹp (566 px) một cột.

- [ ] **Step 3: Commit**

```bash
git add docs/DESIGN_SYSTEM.md
git commit -m "docs: DESIGN_SYSTEM thêm nút TẠM DỪNG, công tắc, khối trang Tự động (TM-4 Task 7)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

## Kiểm chứng plan (18/10/2026)

### Lần tiếp tục — nền TM-1 mới `85ce7f4`, plan TM-1 `874e7c4`

- Nhận cây dở ở HEAD `8a81c16` sau `ae2dc0b`; sao lưu và tiếp tục 45 file mã/test/docs đã áp. Chỉ bổ sung kiểm tên route trong `tai_du_an.js` và một test khe thời gian trước watcher; không viết lại các task đã có. Tạm thay bốn file nền bằng `git show 85ce7f4:<file>`: `tram/tu_dong/file_cam.py`, `tram/bao_tin/chong_on.py`, `tests/test_tu_dong_khoa.py`, `tests/test_chong_on_tu_dong.py`. TM-4 không sửa nội dung bốn file này.
- **N₀ mới:** `npm run kiem` → **102 pass**, 135 file quét. Python qua runner: lần đầu uv không ghi được cache ngoài workspace; đặt `UV_CACHE_DIR="$PWD/scratchpad/tm4-v2/uv-cache"`, runner vẫn giữ `UV_OFFLINE=1`. `tests/chan_host/chay.sh --collect-only -q` → **3422 tests collected**. Chạy `tests/chan_host/chay.sh -q` trước áp TM-4: **11 failed, 140 passed in 93.39s**, dừng bằng Ctrl-C sau lỗi nền lặp lại; **0 dòng chặn mới**, 33 push giả. Không có N₀ xanh mới.
- **Nguyên nhân cửa kiểm Python chưa đạt:** test nền `tests/test_ban_chep.py::test_ban_chep_dung_commit_co_repo_git_khong_bi_export_ignore_giau` ném `LoiBanChep: lệnh dưới tram-kiem: không xác nhận thu hồi cây tiến trình — không công nhận`; chạy riêng qua runner `-q tests/test_ban_chep.py -x` cũng **1 failed in 8.51s**. `ps` bị môi trường từ chối (`operation not permitted`), `pgrep` không lấy được danh sách tiến trình. Không nới bộ chặn/test hay sửa mã thu hồi ngoài phạm vi để làm xanh.
- **Áp nguyên văn task 1–7:** mỗi task áp test → chạy đỏ → áp mã → chạy xanh. Frontend lần đầu **109 → 110 → 120 → 130 → 132**; sau bổ sung một test Q10 thành **133/133**. Task 6 đỏ `ImportError: cannot import name 'RONG'` → **3 passed**, **0 dòng chặn mới**. Task 7 là docs, không có test đỏ riêng. `npm run build` và `npm run kiem-dist` qua; quét nguồn **153 file**. Cảnh báo bundle Văn phòng >500 kB vẫn có, không phải lỗi build.
- **SSE sửa trực tiếp vòng 1 đã chạy thật:** tạm bỏ riêng `doi()` trong nhánh SSE → **1 failed, 6 passed**, `actual: 0, expected: 1`; trả lại → **7 pass**. Q9: tạm cho lưu dùng `layDl().phien_ban` → test “SSE chen giữa mở form và lưu” đỏ **1 failed**, actual `['42', 'make deploy-cua-a']`, expected `['41', 'make deploy-cua-a']`; trả về bản chụp → xanh.
- **Q10 bổ sung:** route A → B trước watcher gọi lần tải mới; test đỏ trên phần dở (`actual: dữ liệu a`, `expected: null`). `tai()` chụp cả `ten` và `theHe`; nhánh thành công/lỗi đều bỏ kết quả nếu tên hoặc thế hệ không còn khớp. Sau sửa, **5 test đồng bộ pass** (Q9: SSE; Q10: đảo thứ tự, B lỗi/404, chuyển route khi sửa A, khe trước watcher).
- **Cửa kiểm cả bộ sau áp:** `tests/chan_host/chay.sh -q --maxfail=1` → **1 failed, 139 passed in 22.33s**, **0 dòng chặn mới**, 14 push giả; dừng ở cùng lỗi nền `test_ban_chep` trước khi tới test TM-4. Đây là chạy cửa kiểm cả bộ có dừng sớm, không phải chứng cứ toàn bộ 3425 test xanh. Cần chạy lại cả bộ trong môi trường cho phép kiểm cây tiến trình trước nghiệm thu triển khai.
- **Dựng lại:** hoàn nguyên đúng 45 file đã áp về HEAD (xoá đúng file mới trong danh sách), giữ bốn file TM-1 mới; trích lại tất cả khối `Tạo mới`/`Bản vá` theo thứ tự task. Mỗi patch qua `git apply --check`, rồi áp; chạy RED→GREEN. So byte cả 45 file với cây đã kiểm: **0 khác biệt**. Frontend dựng lại **133/133 pass**, build + `kiem-dist` qua; runner cho ba file `test_du_lieu_giao_dien_tu_dong.py`, `test_tu_dong_khoa.py`, `test_chong_on_tu_dong.py` → **30 passed in 1.08s**, **0 dòng chặn mới**. Kết thúc hoàn nguyên mọi mã/test/docs ngoài plan, kể cả bốn file nền về HEAD; không commit, không tạo báo cáo ngoài plan theo yêu cầu chỉ giữ một file.
- Không chạy lại trình duyệt trong lần tiếp tục; kiểm CSP runtime bên dưới là bằng chứng kế thừa. Thay đổi mới chỉ ở kiểm phản hồi bất đồng bộ, đã có test node đỏ/xanh. Hai trình duyệt và cửa ghi thật vẫn thuộc cổng OS, không tuyên bố đã kiểm ở đây.

### Bằng chứng kế thừa của agent trước — vòng 2 trên nền TM-1 cũ

Các số và kiểm trình duyệt dưới đây đã có trong phần dở lúc nhận việc; giữ làm lịch sử, không thay cho lần kiểm mới trên `85ce7f4`.

- **N₀** (đo lại trước khi áp): `3412 passed in 402.87s (0:06:42)`, nhật ký chặn 0 dòng mới, điểm mù 48, push giả lập 629. **M₀**: `ℹ tests 102`, `kiem-an-toan: 135 file`.
- **Áp bản plan sau Codex (chưa sửa vòng 2)** task 1 → 7, RED → GREEN đúng như Step 2/4 cũ: frontend `124 pass`, pytest `2 passed`; mọi bản vá `git apply` sạch (không `--recount`). **Sửa trực tiếp của Codex (SSE → `doi()`)**: bỏ riêng dòng `doi()` trong `kho.js` → `tu_dong_khung.test.mjs` đỏ thật `✖ SSE: sự kiện tự động → …` `actual: 0, expected: 1` (phienBan không tăng); trả lại → `ℹ pass 6`. Giữ nguyên sửa của Codex.
- **Test mới chạy trên mã CŨ (bản sau Codex) — đỏ thật:** `tu_dong_khung` "tải /api/tu-dong dồn…" `actual: false, expected: true`; `tu_dong_ghi` "409 / 422 / 403…" `actual: 'Cài đặt tự động của repo nhap đã đổi (hiện 42, đang xem 41) — tải lại'` / `expected: 'Cài đặt đã đổi — tải lại'`; "Q9: lưu theo bản chụp…" `+ expected_version: '42'` / `- expected_version: '41'` (đúng kịch bản Codex: nháp cũ đi cùng phiên bản mới); "Q10: thao tác theo tên dự án của route…" `actual: true, expected: false` (vẫn gửi cài đặt của `a` khi route đã sang `b`); `tu_dong_dong_bo.test.mjs` `ERR_MODULE_NOT_FOUND … sua_lenh.js`; `phe_duyet.test.mjs` `SyntaxError: … does not provide an export named 'khoaDeploy'`; pytest `ImportError: cannot import name 'them_phe_duyet_gia' … Did you mean: 'muc_phe_duyet_gia'?`. Sau sửa: frontend `ℹ tests 132`, `ℹ pass 132`, `kiem-an-toan: 153 file`, build + `kiem-dist` sạch; pytest `3 passed`.
- **Trình duyệt dưới CSP thật** (`tests/chay_thu_giao_dien.py 7798 --dai-ca`, Browser pane `http://127.0.0.1:7798`): `#/phe-duyet` → nhóm "Sẵn sàng deploy 1", đúng MỘT thẻ "tram · sẵn sàng deploy — Bản a41c07e — gồm 2 việc đã merge · merge cuối …", nút "Deploy" khoá + dòng "Cửa ghi đang khoá" (kênh `header`), nút "Mở trang Tự động"; `#/du-an/tram` → mở "Sửa 3 lệnh" (bỏ `disabled` qua DevTools chỉ để mở form) → ô nhập là ba lệnh đã lưu; gõ nháp rồi đổi hash sang `#/du-an/ke-toan` → form đóng, tiêu đề "ke-toan · Tự động", khối "Dự án đang chỉ quét thử", ba lệnh "chưa khai"; quay lại `tram` → form đóng, ba lệnh đã lưu (không còn nháp); `#/du-an/khong-co` → "Không có dự án này …". Console: lỗi duy nhất là 404 của `/api/du-an/khong-co/tu-dong` (đúng chủ đích), **không lỗi CSP**. Không thử được 409 thật trên trình duyệt (kênh `header` trả 403 trước khi tới kiểm phiên bản; `--kenh-that` thì chỉ đọc) — 409 phủ bằng test node.
- **Áp lại từ plan:** hoàn nguyên (`git checkout -- frontend tests docs/DESIGN_SYSTEM.md`, `git clean -fdq frontend/src frontend/tests tests`), trích mọi khối theo thứ tự task — mỗi task áp test → đỏ đúng Step 2 → áp mã → xanh: frontend 109, 110, 120, 130, 132 (`kiem-an-toan` 138, 138, 141, 152, 153 file), build + `kiem-dist` sạch mỗi task; pytest đỏ `cannot import name 'RONG'` → `3 passed`; so `diff -r` với bản đã chạy (`frontend/src`, `frontend/tests`, 3 file `tests/`, `docs/DESIGN_SYSTEM.md`): **0 khác biệt**. `git diff 0f88957 -- tram` rỗng.
- **Cả bộ Python trên cây dựng lại từ plan:** xem lần tiếp tục dưới đây; không dùng số dự kiến làm kết quả.
- Không chạy lệnh cấm; không mạng, `gh`, `bd`, Telegram; trình duyệt chỉ `127.0.0.1`; `npm ci --offline`, `uv sync --offline`.

### Lần đầu (lịch sử, trước review Codex)

- **N₀** trên `0f88957`: `3412 passed in 353.84s`, nhật ký chặn 0 dòng mới, điểm mù 48, push giả lập 629. **M₀** frontend: `ℹ tests 102`, `kiem-an-toan: 135 file`.
- **Chạy thật lần đầu** (viết mã từng task trong worktree, RED → GREEN từng task, thông báo đỏ ở Step 2 là thật): frontend `ℹ tests 124`, `ℹ pass 124`, `kiem-an-toan: 151 file`, `npm run build` xanh, `kiem-dist` sạch; cả bộ Python trên cây đã chạy `3414 passed in 367.27s`, 0 dòng chặn mới, điểm mù 48, push giả lập 629. Khi viết, ba chỗ sửa trong chính lần chạy: (1) thử gọi `taiTuDong()` lúc SSE nối lại làm đỏ test cũ `kho.test.mjs` (`+ '/api/tu-dong'`) → bỏ, không đổi test cũ; (2) `luat_trang_tu_dong.js` vượt 120 dòng và nhập vòng với luật lịch sử → tách `luat_bao_tu_dong.js`; (3) trình duyệt cho thấy mất khoảng trắng trước câu khoá ("Telegram.Cửa ghi đang khoá") vì Vue gộp khoảng trắng đầu thẻ → viết `{{ ` ${s.lyDo}.` }}`.
- **Trình duyệt dưới CSP thật** (Task 7 Step 2, `tests/chay_thu_giao_dien.py 7798 --dai-ca` rồi `--dai-ca --kenh-that`, Browser pane trỏ `http://127.0.0.1:7798`, 1440×1100 và 566 px): bố cục trang Tự động khớp `anh-tu-dong-cua-tam.png` (khối cửa tạm, hai cột, công tắc mờ, Deploy khoá "Cửa ghi đang khoá."); bấm "Tạm dừng dự án" qua kênh `header` → máy chủ TM-1 nhận, nút thành "Dự án đang tạm dừng", chip "tạm dừng", khối "Dự án đang tạm dừng" có Tiếp tục khoá + title "Cửa ghi còn tạm — Tiếp tục cần cửa ghi unix-socket"; bấm "Tạm dừng tự động" trên thanh trên → "Đang tạm dừng tự động", băng vàng, Tiếp tục khoá, thẻ Dự án ghi "tạm dừng toàn trạm" (+ "1 sẵn sàng deploy" ở `tram`); mục "Dự án" sáng ở `#/du-an/tram`; `#/du-an/ke-toan` → khối chỉ quét thử, chip "chỉ quét thử", ba khối rỗng đúng chữ, `0 / 3`, "Chưa từng đổi — đang dùng mặc định"; `--kenh-that` → thẻ người dùng "Chỉ đọc", 8 nút ghi trên trang và nút toàn trạm `disabled`, "Xem lịch sử đổi" mở ngăn bên 3 dòng ("Bật tự merge — tắt → bật · Đại ca (dashboard)", "Sửa lệnh kiểm còn sống — trống → …/kiem-song.sh …", "Sửa lệnh deploy, lệnh lùi — trống → …/deploy.sh, trống → …/lui.sh …"); `#/phe-duyet` → nhóm "Sẵn sàng deploy 1", thẻ "tram · sẵn sàng deploy … Mở trang Tự động" → `#/du-an/tram`, tab "(5) Phê duyệt · Ben Station". Console: **không lỗi CSP**; lỗi duy nhất `net::ERR_INCOMPLETE_CHUNKED_ENCODING` của luồng SSE khi Em tắt máy chủ cũ để đổi chế độ. Ở 566 px trang xuống một cột.
- **Áp lại từ plan:** hoàn nguyên worktree về `0f88957` (`git checkout -- frontend tests docs/DESIGN_SYSTEM.md`, `git clean -fd` thư mục mã/test), trích MỌI khối "Tạo mới"/"Bản vá" từ chính file này theo thứ tự task — mỗi task: áp khối test → chạy (đỏ đúng thông báo ở Step 2) → áp khối mã → chạy (xanh: 6, 3, 10, 4, 5 pass; pytest `2 passed in 0.11s`) — rồi so `diff -r` với bản sao trạng thái đã chạy (`frontend/src`, `frontend/tests`, `tests/`, `docs/DESIGN_SYSTEM.md`, bỏ `__pycache__`): **0 khác biệt**.
- **Cả bộ trên cây dựng lại từ plan:** frontend `ℹ tests 124`, `ℹ pass 124`, `kiem-an-toan: 151 file`, build + `kiem-dist` sạch; Python `3414 passed in 379.91s (0:06:19)`, nhật ký chặn 0 dòng mới, điểm mù 48, push giả lập 629.
- **Sửa theo plan TM-2 (18/10, sau bản đầu):** `cho_dai_ca` có thêm `luc`, `muc`; mã cấu trúc DB là `schema_duong_dan`/`schema_tu_khoa`. Đổi `choDaiCa` sang chọn màu theo `muc`, sửa test `tu_dong_trang.test.mjs` "chờ Đại ca…" (đỏ thật trên mã cũ: `+ lop: 'tt-can_nguoi'` / `- lop: 'tt-loi'` cho lý do `schema_duong_dan`) và dữ liệu giả + `test_khoa_that_thang_khoa_gia` (đỏ thật trên dữ liệu cũ: `{'ma': 'schema', …} != {'ma': 'schema_duong_dan', …, 'muc': 'loi'}`). Sau sửa: `tu_dong_trang.test.mjs` 6 pass, frontend `ℹ tests 124`, `ℹ pass 124`, build + `kiem-dist` sạch; pytest `2 passed`. Áp lại cả plan lên cây sạch và so `diff -r` với cây đã sửa: **0 khác biệt** (RED→GREEN từng task như lần đầu: 6, 3, 10, 4, 5 pass; pytest `2 passed`). Cả bộ Python không chạy lại (chỉ đổi dữ liệu giả trong `tests/`, test liên quan xanh).
- **Sửa theo plan TM-3 (18/10):** `dang_deploy.trang_thai` → hàng "Chờ trạm nhận bản …" khi `cho`; nhãn lịch sử `huy` "Deploy bị huỷ"; dữ liệu giả theo dạng TM-3 (dòng `san_sang` có `ai = tram`, `chi_tiet` theo `_buoc`, một dòng `huy`, mục Phê duyệt có `chi_tiet` = toàn bộ `san_sang`); test 409 của nút Deploy với câu "Có bản mới hơn — tải lại …". Đỏ thật trên mã cũ: `tu_dong_lich_su.test.mjs` (`+ 'huy', + ''` / `- 'Deploy bị huỷ', - 'tt-tat'`), `tu_dong_trang.test.mjs` (`- cho: false`), pytest `assert ['dai_ca'] == ['tram']`; test 409 Deploy xanh ngay (giao diện vốn hiện nguyên câu máy chủ — giữ làm mốc). Sau sửa: frontend `ℹ tests 124`, `ℹ pass 124`, build + `kiem-dist` sạch; pytest `2 passed`. Áp lại cả plan lên cây sạch và so `diff -r`: **0 khác biệt** (RED→GREEN từng task: 6, 3, 10, 4, 5 pass; pytest `2 passed`).
- `git diff 0f88957 -- tram` rỗng. Không chạy lệnh cấm nào; không mạng, không `gh`/`bd`/Telegram; trình duyệt chỉ mở `127.0.0.1`. Không tải gói (`npm ci --offline`, `uv sync --offline` trong worktree).

## Bước cổng trên OS thật

Không có bước riêng cho lát này. Mọi thao tác thật (bật công tắc, Deploy) chỉ có nghĩa sau TM-2/TM-3 và cổng G8 (mốc 6.4). Khi kênh `unix-socket` thật (G29) xong, thêm vào sổ tay cổng đó mục Codex vòng 1 "Cần đo trên OS thật" số 6 — phần giao diện: hai trình duyệt cùng mở `#/du-an/<ten>`, A mở "Sửa 3 lệnh", B lưu lệnh khác → A bấm Lưu phải thấy "Cài đặt đã đổi — tải lại" và nháp còn; chuyển `#/du-an/A` ↔ `#/du-an/B` khi mạng chậm (DevTools throttling) không thấy dữ liệu/nháp của dự án kia; nút Deploy ở Phê duyệt và ở trang Tự động cùng khoá khi bật Estop; máy/kênh `header` chỉ bấm được TẠM DỪNG (D87).

## Rủi ro còn lại (không đóng bằng plan này)

1. **Dạng khoá đã khớp plan TM-2/TM-3 ngày 18/10** (mục "Hợp đồng TM-4 cần…"); TM-2/TM-3 đang sửa vòng 2 (Q2, Q6, Q7, Q8 có thể đổi cách tính `san_sang`). Đổi tên khoá giao diện đang đọc thì sửa hàm luật tương ứng (có test) trước khi code — xem "Ghép trên lát trước". Loại `huy` đã chốt D127 (TM-3 thêm).
2. **Kênh `header` hiện tại** → trên máy B thật mọi nút trừ TẠM DỪNG luôn khoá tới G29 (đúng D87); Đại ca sẽ chỉ thấy trang ở trạng thái `anh-tu-dong-cua-tam.png`, Deploy ở Phê duyệt khoá "Cửa ghi đang khoá".
3. **`window.confirm`** là hộp của trình duyệt (như estop) — đủ cho spec, không có câu dài định dạng đẹp.
4. **Số Phê duyệt và khoá nút Deploy ở Phê duyệt** theo `kho.tuDong`/danh sách chỉ làm mới khi có sự kiện `tu_dong.*`/`tu_merge.*`/`deploy.*`/`estop.*` hoặc `phe_duyet_doi`; nếu TM-3 đổi sẵn sàng mà không ghi sự kiện `deploy.*`, thẻ chỉ đổi ở lần tải sau. Máy chủ vẫn từ chối (409/422) nên không chạy nhầm bản.
5. Giờ trạm tự tắt tự deploy lấy từ `lich_su_doi` (20 dòng gần nhất của TM-1) — rất nhiều lần đổi sau đó thì khối tự tắt không có giờ (vẫn hiện).
6. Xung đột 409 khi bật/tắt **công tắc** (không phải form lệnh) cũng hiện "Cài đặt đã đổi — tải lại" + nút; SSE thường đã tải lại trước khi Đại ca bấm — nút "Tải lại" chỉ xoá câu báo và tải lại một lần.

## Ghép trên lát trước (TM-4 ghép sau TM-1 → TM-2 → TM-3; TC ghép sau TM-4)

Hunk viết trên `0f88957`, kiểm áp trên TM-1 mới `85ce7f4`. Đối chiếu từng khối mã của plan TM-2 (`+++ b/…`: `docs/MODULES.md`, `openspec/changes/tu-merge-tu-deploy/tasks.md`, `tests/gh_gia.py`, `tests/test_gh.py`, `tram/api/tuyen_tu_dong.py`, `tram/giao_viec/{gh,tick_github,tu_merge}.py`, `tram/suy/tu_dong.py` + file mới chỉ trong `tram/`, `tests/test_*`) và TM-3 (`diff --git`: `docs/MODULES.md`, `tests/{test_api_tu_dong,test_noi_giao_viec}.py`, `tram/api/{than,tuyen_tu_dong}.py`, `tram/giao_viec/{kiem_lai,lenh,luong,tick,tick_pipeline,xet_spec,xet_xong,xu_ly_viec}.py`, `tram/suy/{phe_duyet,tu_dong}.py`, `tram/tho/ket_thuc.py` + file mới trong `tram/deploy/`, `tram/thao_tac/`, `tests/test_*`) với danh sách file TM-4 sửa — đã đọc lại plan TM-3 trực tiếp tại `/Users/dai-ca/Developer/Ben Station/.worktrees/sua-tm3/docs/plans/2026-10-18-lat-tm-3-tu-deploy.md` trong lần tiếp tục. Bản file này vẫn có thuật toán/Interfaces vòng 1 và câu hỏi D127 cũ; không coi đó là bằng chứng TM-3 vòng 2 đã xong. Nền TM-1 đối chiếu `85ce7f4` (chỉ bốn file Python/test đổi, không file nào TM-4 sửa), nên Step 0 Task 1 vẫn `git apply --check` từng bản vá:

| File TM-4 sửa | TM-1 (đã trong nền) | TM-2 | TM-3 | Nội dung hợp nhất sau ghép | ≤ 120 dòng |
|---|---|---|---|---|---|
| `frontend/src/{bieu_tuong,kho,luat,luat_du_an,luat_phe_duyet,tuyen}.js`, `KhungChinh.vue`, `thanh/{ThanhTren,ThanhBen,BangEstop,DauTrang}.vue`, `trang/{DuAn,PheDuyet}.vue`, `kieu/{nen,khung,du-an}.css` | không | không | không | đúng bản vá ở Task 1/2/4/5 | `luat_phe_duyet.js` 104, `kho.js` 87; còn lại dưới |
| `frontend/tests/{du_an,phe_duyet}.test.mjs` | không | không | không | đúng bản vá Task 2/5 | — (test) |
| `tests/du_lieu_giao_dien.py`, `tests/chay_thu_giao_dien.py` | không (TM-1 không sửa) | không | không (plan TM-3 ghi rõ "TM-3 **không** sửa") | đúng bản vá Task 6 (201 và 144 dòng — `tests/` ngoài luật 120 dòng của `tests/test_do_dai_ma.py`, vốn 127/125 dòng) | — |
| `docs/DESIGN_SYSTEM.md` | không | không | không | đúng bản vá Task 7 | — |

→ **Không có file chung về chữ**; nội dung hợp nhất của mỗi file là nguyên bản vá TM-4. TM-4 không sửa `tram/` nên không góp vào vụ `tram/api/tuyen_tu_dong.py` 123 dòng (Codex Q15). Các file TM-4 tạo mới (`frontend/src/thanh/tu_dong/*`, `luat_*_tu_dong.js`, …) không lát nào khác tạo. TC (ghép sau) theo plan hiện tại không sửa `frontend/` hay hai file `tests/` trên; nếu TC thêm khối "agent tự cập nhật việc" (cần mockup riêng, câu 5) thì viết trên nội dung TM-4.

**Ghép về nghĩa (không xung đột chữ nhưng phải kiểm khi code):**

1. `tests/chay_thu_giao_dien.py` thay hàm module `tuyen_tu_dong.chi_tiet_du_an`, `tuyen_tu_dong.tom_tat_du_an`, `tuyen_doc.gom_phe_duyet`. TM-2 thêm tham số `tieu_de=` cho `chi_tiet_du_an` (lambda `**kw` chuyển tiếp nguyên); TM-3 giữ chữ ký `gom_phe_duyet(cac_du_an, theo_du_an, kho, them=())`. Bản TM-3 vừa đọc vẫn gọi hai hàm đọc tại `tuyen_tu_dong`, nên bản vá Task 6 giữ nguyên. Nếu khi ghép Q15 dời lời gọi sang module khác, phải sửa và kiểm lại đích vá theo module mới — thiếu tên thì dòng gán ở `tu_dong_gia` ném `AttributeError` ngay khi chạy (không lặng lẽ mất dữ liệu giả). Kiểm: `--dai-ca --gia-deploy` → trang `tram` có "Sẵn sàng deploy", Phê duyệt đúng MỘT thẻ.
2. Sau TM-3: `tram.suy.phe_duyet.THU_TU` có `"san-sang-deploy"` → mặc định `them_phe_duyet_gia` không thêm hàng giả; khoá thật `san_sang`/`dang_deploy`/`lich_su`/`dem_hong` (và `cho_dai_ca` của TM-2) có trong phản hồi → khoá giả không hiện. Trang khi đó hiện trạng thái thật (rỗng trong dữ liệu kiểm tay) — đúng ý Codex "không che trạng thái thật"; muốn so mockup thì `--gia-deploy`.
3. Dạng khoá: hàm đọc — `sanSang` (`san_sang.{commit, so_merge, bead_ids, luc, commit_dang_chay}`, `dang_deploy.{trang_thai, commit, nguon, luc}`), `sanSangDeploy`/`khoaDeploy` (`chi_tiet.commit`, `chi_tiet.so_merge`, `updated_at`; `GET /api/tu-dong` `du_an[].{ten, bat_ghi, du_lenh}`), `dongLichSu` (6 khoá + `huy`), `choDaiCa` (`ly_do[].{nhan, muc}`). Khoá thêm của TM-3 vòng 2 (ví dụ tập merge được bao phủ — Q6) không phá giao diện; đổi tên khoá đang đọc thì sửa hàm + test trước.
4. 409 của Deploy (TM-3; Q7 có thể thêm 409 lúc khởi chạy): giao diện hiện nguyên câu máy chủ tại chỗ ở cả hai nơi, không đổi gì.

## Đề nghị đổi hợp đồng TM-1

Không cần đổi. Lát này dùng đúng tuyến, khoá và mã lỗi của TM-1. Chỉ **bổ sung** (thuộc TM-2/TM-3, không phải TM-1): dạng khoá ở mục "Hợp đồng TM-4 cần từ TM-2 / TM-3".

## Câu hỏi cho Đại ca

Không còn câu hỏi. Ba câu cũ đã có quyết định (18/10): **D128** — tắt tự merge / tự deploy có hỏi lại (plan đã làm thế: `hoiCongTac`); **D129** — dòng "sẵn sàng deploy" ở Phê duyệt CÓ nút Deploy (đã sửa: Task 5, lệch mockup 7); **D130** — khối chưa có dữ liệu hiện "Chưa có dữ liệu — phần này của trạm chưa chạy." (plan đã làm thế: `CHUA_CO`). **D127** — lịch sử có dòng "Deploy bị huỷ" (nhãn `huy` đã có, giữ).

## Ghi chú triển khai

(trống — ghi khi code: chỗ lệch plan, số đo thật)

## Phản hồi review Codex vòng 1

| Mã | Sửa ở đâu | Test (đỏ thật trên mã cũ → xanh) |
|---|---|---|
| Sửa trực tiếp #3 (SSE tự động đánh thức phiên bản chung) | Giữ nguyên `kho.js` (`doi()` trong nhánh `laSuKienTuDong`) và assertion `kho.phienBan` | `tu_dong_khung` "SSE: sự kiện tự động…": bỏ `doi()` → `actual: 0, expected: 1`; có → xanh (chạy thật vòng 2) |
| **Q9** — phiên bản mới đi cùng nội dung form cũ | `ghi_tu_dong.luu(doi, hoi, ban)` gửi `ban.phien_ban` + `ban.cai_dat`; `sua_lenh.js` (mới) chụp `{du_an, phien_ban, cai_dat}` lúc mở form, 409 giữ nháp, "Tải lại" đổi gốc + `doiChieu`; `KhoiCaiDat` nút "Tải lại", dòng "Đang lưu ở trạm"; câu `CHU_XUNG_DOT` = "Cài đặt đã đổi — tải lại" (G8, G17; lệch mockup 14) | `tu_dong_ghi` "Q9: lưu theo bản chụp…" (`+ expected_version: '42'` / `- '41'`), "409 / 422 / 403…" (câu máy chủ ≠ "Cài đặt đã đổi — tải lại"); `tu_dong_dong_bo` "Q9: SSE chen giữa mở form và lưu…" (thiếu module `sua_lenh.js`) |
| **Q10** — dữ liệu/nháp của A hiện ở B | `tai_du_an.js` (mới): thế hệ yêu cầu, `doiDuAn` xoá dữ liệu ngay; `ghi_tu_dong` dựng URL từ `layTen` (route), không gửi cài đặt khi `ban.du_an` ≠ route, bỏ kết quả về muộn; `TuDong.vue` `watch(ten)` xoá lỗi/ngăn lịch sử, `:key="ten"` cho khối Cài đặt/Sẵn sàng; `kho.taiTuDong` bỏ phản hồi cũ (G18) | `tu_dong_ghi` "Q10: thao tác theo tên dự án của route…" (`actual: true, expected: false`); `tu_dong_dong_bo` "phản hồi về đảo thứ tự", "đổi sang B … tải B lỗi … 404", "chuyển route khi đang sửa A" (thiếu module); ca mới "route đổi trước watcher tải mới" đỏ trên mã dở (`actual: a`, `expected: null`) → xanh khi chụp tên + thế hệ; `tu_dong_khung` "tải /api/tu-dong dồn…" (`actual: false, expected: true`); trình duyệt (mục Kiểm chứng) |
| Nhỏ — `gom_phe_duyet` nối hàng giả khi đã có hàng thật | `them_phe_duyet_gia` thay `muc_phe_duyet_gia`: không thêm khi dự án có hàng thật hoặc trạm đã có TM-3; `--gia-deploy` thay (không trùng); `them_gia(…, ep=)` (G14) | `test_phe_duyet_gia_khong_noi_khi_da_co_hang_that` (`ImportError … them_phe_duyet_gia`); `test_khoa_that_thang_khoa_gia` thêm 3 assertion `ep` |
| Nhỏ — spec header cho Tiếp tục, trái D87 | Không đổi: giao diện theo quyết định — Tiếp tục khoá ở kênh `header` (G1, G5) | có sẵn: `tu_dong_khung` "nút TẠM DỪNG toàn trạm…", "khoá nút ghi…" |
| Cần đo OS #6 (hai trình duyệt, hai dự án, SSE, route, đảo thứ tự) | Phần logic phủ bằng test node; phần thật → mục "Bước cổng trên OS thật" (sau G29) | — |
| Giao nhau giữa các lát (`tests/du_lieu_giao_dien.py` TM-4 sở hữu) | Mục "Ghép trên lát trước" | — |
| C1, C2, Q1–Q8, Q11–Q15 | Không thuộc TM-4 (TM-4 không sửa `tram/`); Q15 không bị TM-4 làm nặng thêm | — |
| D129 (Đại ca chốt, khác đề xuất cũ) | Task 5: `khoaDeploy`, `TheSanSang` có nút Deploy dùng `dungGhiTuDong(() => null, …, () => muc.du_an).deploy(chi_tiet.commit)` (cùng hộp hỏi `hoiDeploy`, cùng thân, cùng 409/422) + link; lệch mockup 7; G13 | `phe_duyet` "TM-4 D129…" (`SyntaxError … 'khoaDeploy'` trên mã cũ — Task 5 cũ chỉ có link) |
| D127, D128, D130 | Đã đúng plan — giữ; bỏ khỏi "Câu hỏi cho Đại ca" | có sẵn: `tu_dong_lich_su` (nhãn `huy`), `tu_dong_trang` "hỏi lại…", "chờ Đại ca…"/"sẵn sàng deploy…" (`CHUA_CO`) |

## Sửa trực tiếp của reviewer gộp vòng 3

Đóng V2-N1: `dungTaiDuAn.tai()`/`doiDuAn()` trả `Promise<boolean>`; chỉ `true` khi nhận bản mới đúng
thế hệ/tên dự án. Form và nút tải lại ngoài form chỉ xoá xung đột sau `true`; form còn kiểm bản khác null,
đúng dự án rồi mới thay gốc. Nháp giữ nguyên khi GET 500/404. Task 4 thêm hai ca kiểm lỗi tải lại, giữ
phiên bản 41 sau SSE phiên bản 42; cập nhật callback giả của ca tải thành công. Không đổi bố cục/mockup.
Reviewer chỉ đọc/sửa plan, **chưa chạy hai test mới hay frontend build**. Không cộng vào số xanh lịch sử.
