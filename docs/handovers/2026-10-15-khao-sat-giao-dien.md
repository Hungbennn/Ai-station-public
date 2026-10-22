# Khảo sát dữ liệu và kiểm kê frontend cho giao diện mới (lát 2f) — 15/10/2026

Tài liệu khảo sát, **chưa phải plan**. Mục đích: chuẩn bị plan "2f — giao diện theo mockup đã duyệt" (D20, D33). Không sửa mã, không chạy dịch vụ, không gọi mạng.

## Bản đã đọc

| Thứ | Bản |
|---|---|
| Nhánh làm | `plan/khao-sat-ui`, worktree `.worktrees/khao-sat-ui`. Tạo từ `main` `afc8262`, sau đó fast-forward lên `main` `60bc562` (D33) để đọc mockup mới nhất. |
| Mockup | `docs/mockup/2026-10-15-giao-dien/` tại commit **`449b4a4`**, bản Đại ca duyệt ở D33. Gồm `index.html`, `style.css`, `app.js`, `chung.js`, `du-lieu.js`, `trang.js`, `trang-van-phong.js`, `van-phong.js`, `bo-tri-nhan.js` (mới), `trang-tong-quan.js` (mới), `trang-cai-dat.js` (mới) cùng các ảnh `anh-*.png`. Trước đó Em đã đọc bản `afc8262` và bản đang sửa dở lúc 22:31 (khi đó `bo-tri-nhan.js` chưa commit). Nội dung bản sửa dở nay nằm cả trong `449b4a4`. |
| Quyết định | `docs/quyet-dinh/2026-10-15-chot-dot-4.md` đến D33. Liên quan trực tiếp: D12–D15 (2d), D17–D20, D24 (2e), D25–D29 (2d), D31 (`bat_ghi`), D33. |
| Spec, plan | Spec 2 toàn văn (đã duyệt). Plan 2a, 2b, 2c, 2d, 2e cùng phần "Ghi chú triển khai" của 2a và 2c. Plan 2b có mục này nhưng chỉ đọc phần hợp đồng. 2d và 2e chưa có ghi chú triển khai vì chưa code. |
| Mã | `frontend/src/**`, `frontend/tests/**`, `kiem-an-toan.mjs`, `kiem-dist.mjs`, `vite.config.js`. `tram/api/*.py`, `tram/suy/*.py`, cùng các module được gọi tới: `tram/phieu/trang_thai.py`, `tram/cau_hinh/*.py`, `tram/chu/{cai_dat,launchd}.py`, `tram/usage/*`, `tram/giao_viec/kiem_san_sang.py`. Phần mã giống `1e7e9b0`, vì từ đó đến nay `main` chỉ thêm tài liệu. |

**Đo trên worktree, offline** (`npm ci --offline --ignore-scripts`; `uv run --offline`):
- `uv run pytest -q` → **1987 passed**
- `npm run kiem` → **33** test node, `kiem-an-toan` quét 42 file, sạch
- `npm run build` xanh. Gói chính `index-*.js` 139,89 kB (gzip 51,15 kB). Chunk lười `VanPhong-*.js` 864,34 kB (gzip 231,49 kB).
- `npm run kiem-dist` xanh

---

## 0. Tóm tắt

- **API đọc cần thêm**: 4 API mới, kèm 7 trường bổ sung cho API đang có (chi tiết ở §1.10):
  1. `GET /api/cai-dat` — chỉ Đại ca xem. Gồm cấu hình dự án, trạng thái dịch vụ launchd, Telegram, các cờ, Keychain có/chưa (không bao giờ trả giá trị).
  2. `GET /api/san-sang` — bảng sẵn sàng chạy thật, chỉ Đại ca xem.
  3. `GET /api/su-kien/gan-day` — sự kiện gần đây. Chỉ trả trường trong danh sách cho phép, mô tả dựng từ mẫu cố định.
  4. `GET /api/tong-quan` — gom dữ liệu cho Tổng quan, tái dùng hàm của các route đang có.
- **Kiểm kê frontend**: tổng 42 file nguồn trong `src/`.
  - **30 file giữ logic, đổi giao diện**: 9 trong số đó giữ nguyên hoặc chỉ đổi chữ (`api.js`, các file `luat*.js`, `kho.js`…).
  - **10 file viết lại**: khung, CSS, Phê duyệt và cảnh 3D.
  - **2 file bỏ**: `TheChu3D.vue`, `the_chu.js`. Chữ vẽ bằng canvas được thay bằng nhãn HTML phủ lên cảnh.
  - Test: giữ 6 file, viết lại một phần 1 file (`van_phong.test.mjs`).
- **2d/2e**: Em đề xuất **ghép 2d (T1–T6) và 2e (T1–T4) theo đúng plan trước 2f**. Sau đó 2f làm lại phần giao diện của 2d T2, T5 và 2e T4, phần logic thuần của ba task này giữ nguyên. Backend của 2d và 2e không đổi.
- **2f đề xuất**: 15 task, chạy trong 4 đợt cộng đợt kiểm trên trình duyệt. Ước lượng thêm khoảng **27 test Python** và **30 test node**.
- **Câu hỏi mở**: 18 câu (§3.5). Ba câu chặn plan:
  - font;
  - phần bản thật có nhưng mockup không vẽ;
  - "dự án tạm đóng".

---

## Phần 1 — Dữ liệu cho từng trang

Cột **Tình trạng** dùng các nhãn sau:
- **Có**: API trả sẵn.
- **Tự tính**: trình duyệt tự tính từ dữ liệu đã có, không cần API.
- **Thiếu trường**: API có nhưng thiếu khoá.
- **Thiếu API**: chưa có route nào trả dữ liệu này.
- **2d** / **2e**: dữ liệu sẽ có khi ghép plan tương ứng.
- **Không có nguồn**: mockup minh hoạ một khái niệm mà spec chưa có.

### 1.0 Khung chung: sidebar, thanh trên, estop

| Mockup hiển thị | Nguồn thật | Tình trạng |
|---|---|---|
| Logo "B", "Ben Station · Trạm điều phối", huy hiệu "Bàn điều hành" | hằng chữ (D20) | Tự tính |
| Menu 9 mục: Tổng quan, Dự án, Văn phòng, Công việc, Đội ngũ AI, Ký ức, Usage & chi phí, Phê duyệt, Cài đặt. Phân luồng đã bỏ (D18) | `tuyen.js` | Tự tính |
| Badge số ở Phê duyệt | `GET /api/phe-duyet` → `so` (`kho.soPheDuyet`) | Có. **Lưu ý:** hàm `so_viec_cho()` của mockup cộng cả bead cột 2 "Cần chốt", còn `so` của API **không** tính cột 2 (spec 2 §5.2). Xem câu hỏi Q6. |
| "Máy trạm cục bộ 127.0.0.1" | `location.hostname` | Tự tính |
| Thẻ "Đại ca · Chủ trạm" | `GET /api/chu/trang-thai` → `la_dai_ca` | Có. Khi `false` (gọi thẳng 127.0.0.1, không có header) thì cần một nhãn khác, ví dụ "Chỉ đọc". Xem Q15. |
| Ô tìm "Tìm nhiệm vụ, dự án, agent phụ trách… (⌘K)" | — | **Thiếu API**. Tìm phía trình duyệt trên dữ liệu đã tải thì không cần API mới. Xem Q5. |
| Viên "Đồng bộ · quét cuối 22:14" | `/api/chu/trang-thai` → `du_an[].quet_cuoi` (lấy giá trị lớn nhất), `kho.matKetNoi` của SSE | Có / Tự tính |
| Nút Estop, băng đỏ "Estop đang bật… Tiếp tục" | `/api/chu/trang-thai.estop`; `POST /api/chu/estop`, `/api/chu/tiep-tuc` | Có. Giữ hộp xác nhận `window.confirm` hiện có, dù mockup không có. |
| Tiêu đề tab `<trang> · Ben Station` | `tieuDeTab` (hiện là "(n) Bàn điều hành") | Tự tính. Đổi chữ nên phải sửa 1 test. |

### 1.1 Tổng quan (D17; mockup `trang-tong-quan.js`, `anh-tong-quan.png`)

| Khối / mục | Nguồn thật | Tình trạng |
|---|---|---|
| **Việc chờ Đại ca**: tổng, cùng 5 ô | | |
| · Cần Đại ca chốt (số bead cột 2) | `/api/du-an` → cộng `so_bead["can-chot"]` của mọi dự án | Có (Tự tính) |
| · Chờ review để đóng, kèm "1 PR không xác minh được" | `/api/phe-duyet` → đếm mục `loai = cho-review`. Số PR không xác minh: `/api/giao-viec` → `giao[*].pr.tram.trang_thai` | Có / **2d T3** |
| · Escalation bí, kèm "codex-1 hỏi ở hr-3" | đếm `loai ∈ {escalation, decision}`. Phần "khe nào hỏi ở bead nào" **thiếu**: mục escalation chưa có `khe_id`, `bead_goc` | **Thiếu trường** (T4) |
| · Spec chờ duyệt | đếm `loai = spec` | Có |
| · Hệ cần xem, kèm "cầu dao claude-4" | đếm `loai = he`; `chi_tiet.khe_id`, `chi_tiet.su_kien` | Có |
| · Số tổng | Mockup cộng 4 ô, không tính "Hệ cần xem", trong khi `/api/phe-duyet.so` tính cả `he`, `co-do`, `decision`, `feature-xong` và **không** tính cột 2 | Lệch. Xem Q6. |
| **Sức khoẻ trạm**: 5 dịch vụ `vn.tram.{api,quet,nho,bao-tin,sao-luu}` (chạy / dừng / chưa cài) | — | **Thiếu API** (A1, A4) |
| · Quét cuối, kèm "3 phút trước" | `/api/chu/trang-thai` | Có |
| · Estop | `/api/chu/trang-thai.estop` | Có |
| · Lỗi memory | mục `he` có `chi_tiet.su_kien ∈ {nho.loi_llm, nho.loi_embedder}` | Có |
| · Cầu dao khe (số ngắt, mã khe) | `/api/doi-ngu` → `khe[].cau_dao.ngat`, hoặc mục `he` có `khe.cau_dao_ngat` | Có |
| **Đội ngũ**: chibi, tên "Claude 1"… | `/api/doi-ngu` có `khe_id` và `ten_goi_nho` nhưng **không có** tên nhân vật "Claude 1". Tên này có ở `/api/van-phong` → `nhan_vat[].ten` | **Thiếu trường** (T1), hoặc gọi thêm `/api/van-phong` |
| · Màu thân/tóc của chibi | không có ở server | Tự tính: bảng màu cố định, chọn theo băm `khe_id` |
| · Chip đếm theo trạng thái | `/api/doi-ngu` → `trang_thai`, `cau_dao.ngat` | Có |
| · "Hạn mức thấp nhất: Claude 4 — 5 giờ còn 0%, reset 00:12" | `han_muc.cua_so[]` (`loai = 5h`, `phan_tram` là phần **đã dùng**, `reset_luc`) | Có (Tự tính) |
| **Theo dự án**: cột 1/2/3 | `/api/du-an` → `so_bead` | Có |
| · "Mới xong": `hr-5`, tiêu đề, giờ | Bộ đệm beads có cả bead đã đóng (`bd list --all`) cùng `closed_at`, nhưng `/api/du-an` chưa trả | **Thiếu trường** (T3: `moi_xong`) |
| · Chip "tạm đóng" | spec và cấu hình chưa có khái niệm này | **Không có nguồn**. Xem Q4. |
| **Usage hôm nay**: token vào, token ra | `/api/usage?so_ngay=1` → `theo_ngay[0]` | Có |
| · "$ khe · tương đương" và "$ Claude API chấm cột" | `theo_nguon[]`: dòng `khoa = cham-cot` là Claude API, các dòng còn lại là khe | Có (Tự tính) |
| · Thanh chi phí theo khe, số lượt chạy | `theo_nguon[].chi_phi_usd`, `so_lan` | Có |
| **Sự kiện gần đây**: giờ, loại, dự án, bead, mô tả | Chưa có route GET nào. SSE `/api/luong` chỉ đẩy sự kiện **mới** từ lúc kết nối, không có mô tả. `/api/nho/su-kien` chỉ có sự kiện `nho.*` và chỉ Đại ca xem | **Thiếu API** (A3) |
| "cập nhật 22:17" | giờ tải cuối | Tự tính |

Ghi chú về dữ liệu mockup: một số loại sự kiện trong `du-lieu.js` **không có** trong mã. Không có `giao.cap` (mã dùng `giao.nhan`, `giao.cong_bo`, `giao.ket_thuc`, `giao.thu_hoi`). Không có `tho.mat_nhip`, vì nhịp tim không phải sự kiện (spec 3 §10). Mẫu mô tả của A3 phải theo đúng loại sự kiện có thật.

### 1.2 Văn phòng (D20; `van-phong.js`, `bo-tri-nhan.js`, `trang-van-phong.js`)

| Mockup hiển thị | Nguồn thật | Tình trạng |
|---|---|---|
| Phòng cố định (Giám đốc, Điều phối, Máy chủ, Cà phê) và phòng dự án | `/api/van-phong` → `phong[] {ma, loai, ten, du_an?}` | Có |
| Bố trí: lưới 3×3, ô 10 m, tường chung có cửa, Góc cà phê chiếm 2 ô | mockup đặt tay cho đúng 3 dự án; `bo_tri.js` hiện xếp lưới ô 6 m | **Tự tính, phải viết lại** `bo_tri.js`. Chưa có luật khi có hơn 3 dự án. Xem Q9. |
| Màu sàn/tường riêng từng phòng | không có ở server | Tự tính (bảng màu theo thứ tự hoặc băm `ma`) |
| Phòng "ke-toan (tạm đóng)" mờ | — | **Không có nguồn** (Q4) |
| Biển "Điều phối · chưa có tín hiệu" và đèn xám | `phong[dieu-phoi].sang = null` | Có. **2e T1** thêm `sang: true\|false` và `nhip_cuoi`. Mockup chưa vẽ trạng thái đèn sáng, cần chốt màu. |
| Huy hiệu "4 việc chờ" ở Phòng giám đốc | `phong[giam-doc].so_cho` (= `/api/phe-duyet.so`) | Có. Lệch với cách đếm của mockup (Q6). |
| Tủ máy chủ, mỗi tủ một màu (3 xanh, 1 vàng) | `phong[may-chu].suc_khoe = {mau, ly_do[≤10]}`: một màu chung, `ly_do` là chuỗi không kèm mức | **Thiếu trường** (T6: `suc_khoe.muc[] {mau, ly_do}`). Xem Q10. |
| Nhân vật: tên, nhãn phụ (Làm / Rảnh / Cần người / Lỗi · cầu dao ngắt / Tắt / Mất kết nối), tư thế | `nhan_vat[] {khe_id, ten, cli, trang_thai, hien_thi, phong, bead}`, `cau_dao` lấy từ `/api/doi-ngu` | Có. Chuỗi "Lỗi · cầu dao ngắt" cần thêm `cau_dao.ngat` (lấy từ `/api/doi-ngu` hoặc thêm vào `nhan_vat`). |
| Chỗ đứng/ngồi: Làm và Cần người ở phòng dự án, còn lại ở Góc cà phê | `nhan_vat[].phong` theo 2c G7: `loi`/`tat` ngồi ở phòng của **phiếu cuối**, chưa có phiếu thì ở Góc cà phê | Có. Chú thích trong mockup nói gọn hơn G7. Dữ liệu giả của mockup không có phiếu cuối nên trùng kết quả. Giữ G7. |
| Bong bóng "hr-1 Sửa cắt UTF-8… · code" | `nhan_vat[].bead {du_an, bead_id, tieu_de, buoc}` | Có |
| Huy hiệu đỏ "1" trên khe cần người | `hien_thi = can_nguoi` | Có |
| Màn hình bàn đỏ nhấp nháy khi lỗi | `hien_thi = loi` | Có |
| Panel khi bấm nhân vật/phòng, nút "Mở bead hr-1" / "Lọc Công việc" / "Mở Phê duyệt" | `duongDanNhanVat`, `duongDanPhong` (2c G9). Panel máy chủ dùng `suc_khoe.ly_do` | Có. Bản hiện tại bấm là chuyển trang ngay, mockup mở panel trước. Xem Q8. |
| Bản danh sách: thẻ phòng có chip nhân vật | như trên | Có |
| Ô "Giảm chuyển động" (nhớ trong `localStorage`) | hiện dùng `prefers-reduced-motion` + ô chọn trong phiên | Tự tính. Mockup nhớ lựa chọn bằng `localStorage`. Đây chỉ là tiện ích riêng mỗi trình duyệt, được phép, phải bọc try/catch. |

### 1.3 Công việc và ngăn bên (`trang.js` → `veCongViec`, `moBead`)

| Mockup hiển thị | Nguồn thật | Tình trạng |
|---|---|---|
| Lọc dự án, `?du_an=` trên địa chỉ | `/api/du-an`, `/api/cong-viec?du_an=` | Có |
| Ba cột: số thứ tự, tên, mô tả, đếm | `the[].hang` (`luat.nhomTheoHang`) | Có |
| Thẻ: mã, chip dự án, "loại · P", tiêu đề | `the[] {id, du_an, loai, uu_tien, tieu_de}` | Có |
| Chip nhãn `cot:ai-lam`… | API không trả danh sách nhãn. Có `hang`, `khoa`, `co_do`, `lech`, `khe_spec`, `cho` | Tự tính: suy chip từ `hang`; giữ "khoá", "cờ đỏ", "nhãn lệch", "chờ …", "chưa giao" của bản hiện tại |
| Chip PR (đã mở / không xác minh được / đã merge) | `/api/giao-viec` → `giao[k].pr.tram` | **2d T3** (backend), 2d T5 (luật hiển thị) |
| Dòng khe đang giữ: "Claude 1 · code · **đang hỏi Đại ca**" | không có trong `/api/cong-viec`. Có ở `/api/doi-ngu` → `khe[].phieu {du_an, bead_id, buoc}`, `trang_thai = can_nguoi`, cộng tên (T1) | Tự tính, ghép phía trình duyệt. Hoặc thêm trường `khe` vào thẻ, xem T7. |
| Ngăn bên: `du_an · id · cột n`, tiêu đề, chip loại/P | `/api/bead/{du_an}/{id}` → `the` | Có |
| Lý do lần chấm gần nhất | `cham_gan_nhat.ly_do` | Có |
| Câu hỏi cần chốt, ô trả lời từng câu, nút Chốt / Dẫn ADR | `cham_gan_nhat.cau_hoi[]`, `the.chot_duoc`; `POST …/chot {tra_loi[] \| adr}` | Có |
| Khối PR trong ngăn bên | `ban_giao.pr` (đã kiểm bằng `laLinkAnToan`), `giao.pr.tram` | Có / 2d |
| Mô tả | `mo_ta` (chuỗi) | Có |
| Tiêu chí nghiệm thu (mockup vẽ thành danh sách) | `nghiem_thu` là một chuỗi văn bản tự do | Có. Hiện bằng `white-space: pre-wrap`, không tự tách dòng thành gạch đầu dòng. |
| Dòng thời gian (giờ, tóm tắt) | `dong_thoi_gian[] {luc, loai, tac_nhan, tom_tat}`. Sự kiện `nho.*` bị che nếu không phải Đại ca | Có |

**Bản thật có, mockup không vẽ**, nhưng phải giữ vì spec 2 §5.1 bắt buộc:
- hàng "Chưa chấm", "Feature đang chạy plan", "Epic";
- kéo thẻ giữa cột 1 và cột 2, cùng hộp "Vì sao?";
- nút "Chuyển sang cột 1/2" (thay cho kéo bằng bàn phím);
- ô Trả lời decision ở ngăn bên;
- khối Bàn giao (nhánh, commit, lỗi);
- khối "Bộ giao việc" (lý do chưa giao, lệnh `gh pr create`);
- lỗi đọc từng dự án (`loi`).

Xem Q3.

### 1.4 Đội ngũ AI (`trang.js` → `veDoiNgu`, `anh-doi-ngu.png`)

| Mockup hiển thị | Nguồn thật | Tình trạng |
|---|---|---|
| Bảng điểm: Khe, Vai, Số phiếu, Xong, Lần chạy TB | `/api/doi-ngu` → `bang_diem[] {khe_id, vai, so_phieu, so_xong, lan_chay_tb}` | Có |
| Qua lần đầu, Bị trả về dạng `x% (x/m)`, "chưa có", "—" | hiện luôn `null` | **2d T1**: tỉ lệ đúng chữ spec, theo D25–D29. **2d T2**: `tiLe(x, mau)` |
| Lọc dự án và nhóm nút 7/30/92 ngày | chưa có | **2d T6** (`?du_an=&so_ngay=`), 2d T2 (ô chọn). Mockup dùng nhóm nút thay cho `<select>`, chỉ khác giao diện. |
| Thẻ khe: chibi, "Claude 1", phụ đề "claude-1 · máy B · claude-chinh" | `khe_id`, `may`, `ten_goi_nho` (tên tài khoản gợi nhớ, đã chặn email) | Có. Riêng tên "Claude 1" thiếu (T1). |
| Chip trạng thái: Đang làm / Rảnh / Tắt / Cầu dao ngắt / Cần Đại ca / Mất kết nối | `trang_thai`, `cau_dao.ngat` (`nhanTrangThai`) | Có |
| Việc: "hr-1 tiêu đề · code" | `phieu {du_an, bead_id, buoc, tieu_de}` | Có |
| Cầu dao: lý do, "tự đóng 00:12 (còn 2 giờ)" | `cau_dao {ngat, ly_do, toi_luc}` | Có (Tự tính phần "còn …") |
| "Đại ca tắt khe · *để dành*" | `vi_sao` nằm trong sự kiện `khe.tat` (`tram/phieu/khe.py`) nhưng `/api/doi-ngu` không trả | **Thiếu trường** (T1: `vi_sao_tat`) |
| Thanh hạn mức 5 giờ / tuần, kèm "còn x% · reset hh:mm" | `han_muc.cua_so[] {loai, trang_thai, phan_tram (đã dùng), reset_luc, doc_luc}`; `muc_han_muc` | Có. Mockup chưa vẽ cảnh báo `chi_p0_p1` / `chua_biet` / `ngung` (`CANH_BAO_HAN_MUC`), phải giữ. |
| Vai | `vai_uu_tien` | Có |
| "Phiên: 1/2" | `so_phien` = 0/1 (phiếu đang giữ). Spec 3 **không có** số phiên tối đa | Thiếu mẫu số. Đề xuất chỉ hiện "1 phiên" (Q11). |
| "♥ nhịp tim cuối: 6 giây trước" | `nhip_cuoi` | Có (Tự tính) |
| Nút Bật khe / Tắt khe / Đóng cầu dao | `POST /api/khe/{may}/{ten}/{bat,tat,cau-dao-dong}`, `phien_ban` | Có |
| Luật vai ↔ khe | `luat_vai {vai_cua_buoc, luat[]}` | Có. Mockup chỉ vẽ phần chip, còn danh sách luật (5 câu) phải giữ. |

### 1.5 Phê duyệt (`trang.js` → `vePheDuyet`, `anh-phe-duyet.png`)

| Mockup hiển thị | Nguồn thật | Tình trạng |
|---|---|---|
| Nhóm "Hệ cần xem": chip loại, `_tram`, tiêu đề, chi tiết, link "Mở Đội ngũ AI" | `muc[loai=he] {du_an, bead_id, tieu_de, chi_tiet {su_kien, luc, loi, khe_id?, toi_luc?}}` | Có. Nút "Thử lại" của mục có bead phải giữ. |
| Nhóm "Bí / escalation": mã bead, dự án, chip "Codex 1 hỏi · QC", câu hỏi, nút Trả lời | `muc[loai=escalation\|decision] {bead_id, tieu_de}`. **Chưa có** khe hỏi, bước, câu hỏi | **Thiếu trường** (T4). Câu hỏi nằm ở mô tả bead escalation, lấy được qua `/api/bead`. |
| Trả lời: mockup dẫn sang ngăn bên trang Công việc | `POST /api/phe-duyet/{du_an}/{id}/tra-loi` (bản hiện tại có ô trả lời ngay trong mục) | Có. Mockup dẫn tới ngăn bên của bead escalation, nơi đã có `OTraLoi`. |
| Nhóm "Chờ review để đóng": chip PR, link "PR #12 ↗", lý do, cảnh báo "không xác minh được…", "trạm đã xác minh — sẽ tự đóng" | `muc[loai=cho-review].chi_tiet {pr, nhanh, commit, loi[]}`. Trạng thái PR trạm **chưa** có trong mục Phê duyệt | **Thiếu trường** (T4: `chi_tiet.pr_tram`). Đây là câu C6 của 2d. Mockup đã duyệt có phần này, nên C6 coi như "có" (Q7). |
| Nút Duyệt / Đã merge trên GitHub → đóng bead / Trả về + góp ý | `POST …/duyet`, `…/tra-ve` | Có |

**Bản thật có, mockup không vẽ** (Q3):
- nhóm "Decision mở", "Cờ đỏ", "Spec chờ duyệt" (có `ChiTietSpec`: commit, file, bead đề xuất, lệnh máy A), "Feature xong, chờ đóng";
- dòng "Xác nhận đã merge là thao tác tay…";
- khoá nút khi không phải Đại ca;
- lỗi đọc từng dự án.

### 1.6 Cài đặt (D19; `trang-cai-dat.js`, `anh-cai-dat.png`)

Toàn bộ trang **thiếu API**. Cột "Nguồn đề xuất" là chỗ API mới A1/A2 sẽ đọc. Em không chạy các lệnh trong bảng.

| Khối / mục mockup | Nguồn đề xuất (chỉ đọc) | Không bao giờ trả |
|---|---|---|
| **Bảng sẵn sàng**: mã bead, bước, trạng thái Đạt / Thiếu / Chưa tới lượt, ghi chú, chip đếm, lệnh `uv run tram giao kiem` và `bd list --status open --parent bs-8eh` | A2, xem §1.10 | nội dung ghi chú bead (chỉ trả tiêu đề đã `lam_sach`) |
| **Dự án đã thêm**: tên, đường dẫn, nhánh chính, GitNexus, lệnh được phép, hàng rào (loại → từ khoá) | `tram.cau_hinh.du_an.nap_du_an(ten)` cho từng `liet_ke_du_an()` → `ten`, `duong_dan` (rút gọn `~`), `nhanh_chinh`, `gitnexus_repo`, `lenh_cho_phep`, `hang_rao{loai: tu_khoa}`, `moi_truong_kiem` (có/chưa), `bat_ghi` (D31, khi 1a-2 ghép) | `tu_khoa_khach`, nội dung file `moi_truong_kiem` |
| **Dịch vụ launchd**: dịch vụ, việc, đã cài, đang chạy | Nhãn cố định: `vn.tram.{api,quet,nho,bao-tin,sao-luu}` (`tram/chu/launchd.py`). Kiểm "đã cài" bằng việc có file `~/Library/LaunchAgents/<nhãn>.plist`. Kiểm "đã nạp, đang chạy, mã thoát cuối" bằng `launchctl print gui/<uid>/<nhãn>`: mã thoát 0 thì đọc dòng `state = …`, `last exit code = …`; mã khác 0 nghĩa là chưa nạp | stdout/stderr thô (có PATH, đường dẫn, biến môi trường), `pid` |
| **Telegram**: `chat_id` có/chưa, giờ yên lặng, loại tin | `nap_cau_hinh_tram().telegram` → `chat_id is not None`, `gio_yen_lang`. Loại tin lấy từ `tram.bao_tin.tin.NHAN_LOAI` (2d T4 thêm 2 loại). Token kiểm qua Keychain | giá trị `chat_id`, token |
| **Cờ** | `estop.dang_bat()`; `nap_cau_hinh_giao_viec().bat`; `nap_cau_hinh_cong_bo().phuong_an` (null = chưa chốt); `nap_cau_hinh_cach_ly().kenh_ghi`; `nap_cau_hinh_usage()` (ccusage có cấu hình, phiên bản, có bảng giá); `CauHinhTram.han_muc`, `.tho` (ngưỡng); `ten_may_b`, `dashboard_url` có/chưa; số `dai_ca_logins`; băm mã Đại ca (`tram.nho.ma_dai_ca.doc_bam()` → có/chưa); băm mã điều phối (D24, khi 2e ghép) → có/chưa | danh sách `dai_ca_logins` (email), mọi bản băm |
| **Keychain**: `tram-telegram-bot-token`, `tram-anthropic-api-key`, `tram-nho-token`, `tram-noi-bo-token` | `security find-generic-password -s <tên>`, **không** kèm `-w`, giống `tram/chu/cai_dat.py::_co_keychain`. Mã 0 = có; 44 = chưa có; mã khác = "không kiểm được" (Keychain khoá…) | mọi đầu ra của `security` (bỏ stdout, vì không có `-w` stdout chỉ chứa thuộc tính) |
| **Lệnh CLI gợi ý**, nút Sao chép | Hằng chữ phía trình duyệt (`luat_cai_dat.js`). Dùng `gui/$(id -u)/…` nguyên văn, không gửi uid thật | — |

### 1.7 Dự án (`trang.js` → `veDuAn`)

| Mockup hiển thị | Nguồn thật | Tình trạng |
|---|---|---|
| Thẻ mỗi dự án: tên, "quét cuối 22:14", chip `1 · n`, `2 · n`, `3 · n`, "Lỗi gần nhất", bấm để lọc Công việc | `/api/du-an` → `{ten, quet_cuoi, loi_gan_nhat {luc, loai, loi, bead_id}, so_bead {6 hàng}, loi_doc}` | Có. Bảng hiện tại còn cột "Chưa chấm", mockup bỏ cột này nên cần chốt có giữ không (Q3). |
| "tạm đóng" | — | Không có nguồn (Q4) |

### 1.8 Ký ức

Mockup chỉ có ô giữ chỗ: "Đã có trong spec; mockup đợt này chưa vẽ chi tiết". Dữ liệu và thao tác giữ như hiện tại:
- `GET /api/nho?pham_vi=&cho=`, `GET /api/nho/su-kien` (chỉ Đại ca);
- `POST /api/nho/ghi`, `POST /api/nho/xoa`.

Không thiếu API. Theo luật "mockup trước" thì trang này chỉ được thay vỏ (Q3).

### 1.9 Usage & chi phí

Mockup cũng chỉ có ô giữ chỗ. Dữ liệu: `GET /api/usage?so_ngay=` (1–92) → `theo_ngay`, `theo_tuan`, `theo_nguon`, `theo_du_an`, `co_bang_gia`, `ccusage {trang_thai, theo_ngay, loi, phien_ban}`. Không thiếu API. Trang này cũng chỉ thay vỏ (Q3).

### 1.10 API đọc đề xuất thêm

**Luật chung cho mọi API mới.** Theo spec 2 §4, §8 và tiền lệ ccusage, `/api/nho`.

1. **Chỉ `GET`**, không ghi gì, không `ma_thao_tac`.
2. **Host và CSP**: đi qua `GiuaAnToan` như mọi route. Host lạ trả 421. Phản hồi mang CSP và các header an toàn, kể cả 500. Không thêm middleware riêng.
3. **Quyền đọc xét theo từng yêu cầu**:
   - A1, A2 dùng `Depends(yeu_cau_dai_ca)` y như `/api/nho`: không có đúng một `Tailscale-User-Login` thuộc `dai_ca_logins`, hoặc sai kênh, thì trả 403.
   - A3, A4 đọc công khai như `/api/phe-duyet`, nhưng che phần chỉ Đại ca được xem (như `/api/bead` đang che `nho.*`).
4. **Không lộ bí mật và nội dung nghiệp vụ**:
   - Danh sách cho phép từng trường.
   - Lệnh ngoài chỉ có argv dựng từ hằng số, không lấy gì từ URL. Không bao giờ trả stdout, stderr, argv hay nội dung exception (như ccusage, spec 2 §8).
   - Chuỗi lỗi cấu hình đi qua `lam_sach(…, 200)`.
5. **Không chạy lệnh có tác dụng phụ.** `tram tho kiem` và `tram giao kiem` có `sudo`, `touch`, `sleep 30` (`tram/giao_viec/kiem_san_sang.py`), nên **không bao giờ** gọi từ API. Trang chỉ hiện lệnh để Đại ca tự chạy.
6. **Chịu tải**:
   - Lệnh ngoài có timeout 3 giây.
   - Kết quả giữ trong bộ nhớ tiến trình: dịch vụ 30 giây, Keychain 60 giây (mẫu `BoDemCcusage`).
   - Gọi tuần tự.
   - Route `def` đồng bộ (FastAPI tự chạy trong threadpool).
7. **Đăng ký route**: `tram/api/app.py` nằm trong danh sách "không vá" của 2d/2e, vì refactor đơn nợ. Có hai cách, plan 2f phải chọn một:
   - thêm một dòng `CAC_TUYEN += (...)`, như 2c đã làm;
   - gắn router mới vào một router có sẵn, như 2e gắn vào `van_phong.router`.

| # | API | Trả về (phác thảo) | Đọc từ | Quyền |
|---|---|---|---|---|
| **A1** | `GET /api/cai-dat` | `{du_an: [...], dich_vu: [{nhan, viec, da_cai, da_nap, dang_chay, ma_thoat_cuoi \| null, kiem_duoc}], telegram: {co_chat_id, gio_yen_lang, co_token, loai_tin[]}, co: [{khoa, gia_tri: bool \| str \| null, ghi_chu}], keychain: [{ten, trang_thai: co \| chua \| khong_ro}], loi_cau_hinh: [str]}` | bảng §1.6 | Đại ca |
| **A2** | `GET /api/san-sang` | `{muc: [{ma, ten, trang_thai: dat \| thieu \| cho, ghi_chu, nguon: bead \| tu_kiem}], dem: {dat, thieu, cho}, doc_luc}` | Hai nguồn. **(a) Tự kiểm rẻ, chỉ đọc**: dịch vụ và Keychain (dùng lại A1); có lệnh trong PATH của dịch vụ (`shutil.which` cho `bd`, `tailscale`, `gh`, `codex`, `claude`, `gitnexus`, `uv`); file ccusage cấu hình có tồn tại; `pmset -g` để biết máy có ngủ không (như `cai_dat._canh_bao`). **(b) Các cổng chạy thật**: đọc bead của **repo trạm** bằng `Bd(goc_repo()).tat_ca()`, chỉ đọc, lọc theo nhãn đề xuất `san-sang` (Q13). Suy trạng thái: `closed` → Đạt; mở mà bị chặn bởi bead mở khác → Chưa tới lượt (ghi chú "cần <id>"); mở và không bị chặn → Thiếu. | Đại ca |
| **A3** | `GET /api/su-kien/gan-day?gioi_han=20` (1–50) | `{su_kien: [{id, luc, loai, du_an, bead_id, tac_nhan, mo_ta}]}` | `KhoSuKien`: thêm hàm đọc N sự kiện mới nhất mọi dự án, hoặc dùng `sau_id(id_moi_nhat − k)`. `mo_ta` dựng ở module thuần `tram/suy/mo_ta_su_kien.py` từ **mẫu cố định theo loại**, chỉ ghép các trường đã kiểm dạng (mã khe, mã bead, lượt, bước, cột, `ket_luan`, mã lý do → câu hằng). Loại lạ thì `mo_ta = ""`. Không bao giờ đưa `vi_sao`, `gop_y`, `loi`, nội dung ký ức. Sự kiện `nho.*`: chỉ Đại ca thấy `mo_ta`. | công khai, che một phần |
| **A4** | `GET /api/tong-quan` | `{phe_duyet: {so, dem_theo_loai, muc_dau: [≤5]}, cot_2: n, pr_khong_xac_minh: n, suc_khoe: <như van-phong>, dich_vu: [{nhan, dang_chay}], tram: {estop, quet_cuoi, loi_nho}, doi_ngu: {khe: [{khe_id, ten, trang_thai, han_muc_5h_con, reset}], dem}, du_an: [{ten, so_bead, moi_xong}], usage_hom_nay: {token_vao, token_ra, usd_khe, usd_api, so_lan, theo_khe[]}, su_kien: [≤18]}` | Gọi lại **chính các hàm route** đang có, như `/api/van-phong` gọi `phe_duyet(request)` (2c G6): `phe_duyet`, `du_an`, `trang_thai`, `r_doi_ngu`, `r_usage(so_ngay=1)`, A3. Phần dịch vụ lấy từ bộ đệm của A1 nhưng chỉ trả boolean. Gọi `phe_duyet` một lần rồi dùng chung cho `suc_khoe` (tách một hàm nhỏ khỏi `r_van_phong`). | công khai |

**Trường bổ sung cho API đang có:**

| # | Route | Trường | Đọc từ | Ghi chú |
|---|---|---|---|---|
| T1 | `/api/doi-ngu` | `khe[].ten` ("Claude 1"), `khe[].vi_sao_tat` (chỉ khi `tat`, đã `lam_sach(…, 120)`) | `nhan_vat.ten_nhan_vat`; `phieu.khe.su_kien_khe(…, ("khe.bat", "khe.tat"))` | Đụng file của 2d T6 (`tram/suy/doi_ngu.py`), nên làm sau 2d |
| T2 | `/api/van-phong` | `nhan_vat[].cau_dao_ngat` | `trang_thai_khe().cau_dao` | để hiện nhãn "Lỗi · cầu dao ngắt" |
| T3 | `/api/du-an` | `du_an[].moi_xong {id, tieu_de, luc} \| null` | bead `closed` có `closed_at` lớn nhất trong bộ đệm | `tieu_de` qua `lam_sach(…, 200)` |
| T4 | `/api/phe-duyet` | mục `escalation`: `chi_tiet {khe_id, bead_goc, buoc}`; mục `cho-review`: `chi_tiet.pr_tram` | sự kiện `escalation.tao {escalation_id, bead_goc, giao_id}`, rồi `phieu.khe_id` và `buoc`. `pr_tram(kho, du_an, bead_id, vc3)` của 2d T3 ("Để sau" của 2d đã ghi là dùng lại được) | Làm sau 2d. Phải thêm vào `_muc` ở `tram/suy/phe_duyet.py` mà không đổi thứ tự hay khoá cũ. |
| T5 | (tuỳ chọn) mục escalation | `chi_tiet.cau_hoi` (cắt ≤ 300) | mô tả bead escalation | Có thể bỏ: trang tải `/api/bead` khi mở mục |
| T6 | `/api/van-phong` | `phong[may-chu].suc_khoe.muc[] {mau, ly_do}` (giữ `mau`, `ly_do`) | `tram/suy/van_phong.py::suc_khoe` đã tách sẵn hai danh sách `do` và `vang` | Đụng file của 2e T1, nên làm sau 2e |
| T7 | (tuỳ chọn) `/api/cong-viec` | `the[].khe {khe_id, ten, buoc, can_nguoi}` | kho phiếu: `phieu_hieu_luc` theo (dự án, bead) | Em khuyên ghép phía trình duyệt với `/api/doi-ngu` (đã có `phieu`, `trang_thai`) và tải lại khi có `doi_ngu_doi`, để khỏi kéo kho phiếu vào `/api/cong-viec`. |

### 1.11 Đối chiếu với plan 2d và 2e

| Task | Nội dung | Ai đảm nhận | Ghi chú |
|---|---|---|---|
| 2d T1 | Bảng điểm đúng chữ spec (`diem_giao_viec.py`, `bang_diem.py`) | **2d** | Plan phải sửa theo D25–D29 trước khi chạy. Sau đó 2f chỉ đọc kết quả. |
| 2d T3 | `pr_tram` trong `/api/giao-viec`, SSE thêm `pr.*` | **2d** | 2f dùng lại `pr_tram` cho T4 (trang Phê duyệt). |
| 2d T4 | Hai loại tin Telegram PR | **2d** | 2f chỉ hiện `NHAN_LOAI` ở trang Cài đặt. |
| 2d T6 | `GET /api/doi-ngu?du_an=&so_ngay=` | **2d** | T1 của 2f đụng cùng file, nên làm sau. |
| 2d T2 | `luat_doi_ngu.js` (`tiLe(x, mau)`, `duongDanDoiNgu`, `SO_NGAY_BANG_DIEM`) và `DoiNgu.vue` (ô lọc) | Phần `.js` giữ ở **2d**; phần `.vue` do **2f** làm lại | Nếu chạy 2d nguyên văn thì chỉ phí khoảng 20 dòng `.vue`. Đổi lại không phải sửa bản vá đã `git apply --check`. |
| 2d T5 | `giao_viec.js` (`prTram`, `nhanPrTram`, `moTaPrTram`) và `TheBead.vue`, `OGiaoViec.vue` | `.js` ở **2d**; `.vue` do **2f** làm lại | như trên |
| 2d C6 | Trạng thái PR ở trang Phê duyệt | **2f** (T4) | Mockup đã duyệt có phần này (Q7). |
| 2e T1 | Suy đèn từ nhịp, `/api/van-phong` trả `sang`, `nhip_cuoi` | **2e** | T6 của 2f đụng cùng file `tram/suy/van_phong.py`, nên làm sau. |
| 2e T2, T3, T5 | `POST /api/dieu-phoi/nhip`, hook máy A, chạy thật | **2e** | Theo D24 dùng mã riêng `tram-dieu-phoi-ma`, plan 2e phải sửa. Trang Cài đặt hiện băm mã điều phối "có/chưa". |
| 2e T4 | `chuNhip` (`hien_thi.js`) và dòng "nhịp cuối" trong `DanhSachVanPhong.vue` | `chuNhip` giữ ở **2e**; `.vue` do **2f** làm lại | Mockup chưa vẽ trạng thái "đèn sáng" và dòng "nhịp cuối". 2f phải thêm, cần chốt kiểu hiển thị. |

**Em khuyên thứ tự**: 2d (sau khi sửa theo D25–D29) và 2e (sau khi sửa theo D24) ghép xong trên `main`, rồi mới bắt đầu 2f. 2f không viết lại logic nào của hai lát này.

---

## Phần 2 — Kiểm kê frontend hiện tại (`frontend/src/`)

### 2.1 Hiện trạng

- **Stack**:
  - Vue 3.5.43, vue-router 5.4.0 (hash history), Vite 8.3.4, `@vitejs/plugin-vue` 6.0.10;
  - `@tresjs/core` 5.9.1 và `three` 0.186.1, chỉ dùng ở chunk Văn phòng.
  - Không thêm gói nào khác. Phiên bản khoá chính xác trong `package-lock.json`.
- **Trạng thái dùng chung (`kho.js`)**: `trangThai`, `soPheDuyet`, `phienBan`, `phienBanNho`, `phienBanDoiNgu`, `suKienCuoi`, `matKetNoi`, `loi`.
- **SSE `/api/luong`**:

  | Sự kiện SSE | Tác dụng |
  |---|---|
  | `cong_viec_doi` | `phienBan++` |
  | `phe_duyet_doi` | `phienBan++`, tải lại badge và trạng thái |
  | `doi_ngu_doi` | `phienBanDoiNgu++` |
  | `su_kien` | đặt `suKienCuoi`; với `nho.*` thì `phienBanNho++` |

- **Polling 5 giây** ở Đội ngũ AI và Văn phòng: nhịp tim không phải sự kiện (2b G15, 2c G15).
- **Tuyến**: `/` → `/cong-viec`; `/cong-viec`, `/du-an`, `/phe-duyet`, `/nho`, `/doi-ngu`, `/usage`; `/van-phong` nạp lười.
- **CSS**: một file `kieu.css` (70 dòng, có chế độ tối theo `prefers-color-scheme`) cùng một vài `<style scoped>`. Không có `style=` tĩnh nào trong `src/`.

### 2.2 Bảng kiểm kê

Ba lựa chọn: **G** = giữ logic, đổi giao diện (gồm cả giữ nguyên hẳn) · **V** = viết lại · **B** = bỏ.

| File | Vai trò | Chọn | Lý do |
|---|---|---|---|
| `main.js` | tạo app, router hash | G | Thêm import font/CSS mới, còn lại giữ nguyên. |
| `tuyen.js` | bảng tuyến | G | Thêm `/tong-quan` (trang mở đầu, `/` chuyển tới đây) và `/cai-dat`. Giữ `/nho` (lệnh máy A và Telegram dẫn link theo đường cũ), có thể thêm bí danh `/ky-uc` (Q16). Giữ `/van-phong` nạp lười. |
| `api.js` | `doc`, `ghi` (X-Tram), `thanGhi` (`ma_thao_tac` + `expected_version`) | G (giữ nguyên) | Hợp đồng ghi §12.3, chống CSRF §4.3. |
| `kho.js` | trạng thái chung, `moLuong()` SSE | G | Có thể thêm `phienBanHeThong` cho trang Cài đặt và Tổng quan, đơn giản là tải lại khi `phe_duyet_doi`. |
| `KhungChinh.vue` | thanh menu ngang và `ThanhTrangThai` | **V** | Thành khung sidebar 272 px, thanh trên (ô tìm, viên đồng bộ, Estop), băng estop, thẻ người dùng. |
| `kieu.css` | biến màu, lớp chung | **V** | Thay bằng token của mockup (§2.4). Phải chốt có giữ chế độ tối không (Q2). |
| `luat.js` | nhóm hàng, `choPhepKeo`, `tieuDeTab`, **`laLinkAnToan`**, `khoaMucPheDuyet`, `nhomPheDuyet`, `gioVN` | G | Chỉ đổi chữ (`TEN_HANG` theo mockup "AI tự làm"…, `tieuDeTab` thành "Ben Station"). `laLinkAnToan` giữ nguyên văn. |
| `luat_doi_ngu.js` | nhãn trạng thái, mô tả cửa sổ hạn mức, nút khe, định dạng số/USD, `tiLe`, `khoaMuc` | G | Thêm hàm thuần cho thanh hạn mức (`phanTramCon`, lớp `thap`/`het`), giờ reset ngắn, chọn hạn mức thấp nhất. 2d T2 sửa `tiLe`. |
| `luat_spec.js` | Duyệt spec (commit + digest), lệnh máy A | G (giữ nguyên) | Hợp đồng 409 của spec 4 §7.3. |
| `nho.js` | phạm vi ký ức, nhãn sự kiện | G (giữ nguyên) | |
| `giao_viec.js` | gắn bộ giao việc vào thẻ, cảnh báo PR | G | 2d T5 thêm hàm PR trạm. |
| `thanh/BangUsage.vue` | bảng token/chi phí | G | đổi lớp CSS |
| `thanh/ChiTietSpec.vue` | chi tiết spec chờ duyệt | G | đổi lớp CSS |
| `thanh/DongThoiGian.vue` | dòng thời gian bead | G | Kiểu chấm tròn và đường dọc theo `.dtg` của mockup. |
| `thanh/HopKhe.vue` | hộp bật/tắt khe, có "vì sao" | G | đổi lớp CSS |
| `thanh/HopViSao.vue` | hộp "vì sao" khi chuyển cột | G | đổi lớp CSS |
| `thanh/MucPheDuyet.vue` | một mục Phê duyệt, mọi loại (76 dòng, nhiều nhánh `v-if`) | **V** | Mockup dùng lưới hai cột (nội dung \| hành động), chip loại, ô góp ý nằm trong thẻ. Tách theo loại (`TheReview`, `TheHe`, `TheBi`, `TheSpec`, `TheFeatureXong`), giữ nguyên hàm `lam/duyet/traVe/traLoi/thuLai` và cách xử lý 409/501. |
| `thanh/OChot.vue` | ô Chốt hoặc dẫn ADR | G | Mockup đặt hai nút "Chốt" và "Dẫn ADR" thay cho ô đánh dấu. Logic giữ. |
| `thanh/OGhiNho.vue` | ghi tay ký ức | G | chờ mockup Ký ức (Q3) |
| `thanh/OGiaoViec.vue` | bộ giao việc trong ngăn bên | G | 2d T5 sửa trước |
| `thanh/OTraLoi.vue` | Trả lời escalation/decision | G | đổi lớp CSS |
| `thanh/SuKienNho.vue` | sự kiện ký ức | G | chờ mockup Ký ức |
| `thanh/ThanhTrangThai.vue` | estop, quét cuối từng dự án | **V** | Tách thành `ThanhTren.vue` (viên đồng bộ, nút Estop) và `BangEstop.vue`. Logic `bam()` và hộp xác nhận giữ nguyên. |
| `thanh/TheBead.vue` | thẻ bead, kéo thả | G | Thêm chip, dòng khe, chip PR. Giữ `draggable`, `dataTransfer.setData` (Firefox), Enter để mở. |
| `thanh/TheKhe.vue` | thẻ khe, nút | G | Thêm chibi, thanh hạn mức. Giữ `lam()`, 409, xác nhận đóng cầu dao. |
| `thanh/TheKyUc.vue` | một ký ức | G | chờ mockup Ký ức |
| `trang/CongViec.vue` | ba cột, lọc, mở theo địa chỉ, kéo | G | Đầu cột (số, tên, mô tả), ô "Không có bead". Logic `moTheoDiaChi`, `tha`, `xacNhanKeo` giữ nguyên. |
| `trang/DoiNgu.vue` | thẻ khe, luật vai, bảng điểm, polling 5 giây | G | Bố cục theo mockup: bảng điểm trên, khe ở giữa, luật vai dưới. Bộ lọc từ 2d. |
| `trang/DuAn.vue` | bảng dự án | G | Đổi bảng thành lưới thẻ (mockup). Dữ liệu giữ nguyên. |
| `trang/KyUc.vue` | màn Ký ức | G | chỉ thay vỏ (Q3) |
| `trang/NganBen.vue` | ngăn bên bead | G | Bố cục theo mockup (`h4` viết hoa nhỏ). Giữ mọi khối của bản thật (§1.3). |
| `trang/PheDuyet.vue` | nhóm theo loại, tải lại | G | Tiêu đề nhóm có số đếm. Logic giữ. |
| `trang/Usage.vue` | bảng usage | G | chỉ thay vỏ (Q3) |
| `trang/VanPhong.vue` | trang 3D, WebGL2, polling, giảm chuyển động | **V** | Lớp nhãn HTML phủ, panel khi bấm, khung chuyển màu nền, khung nhìn khít cảnh. Phải giữ: kiểm WebGL2, `luotTai` (bỏ kết quả tải cũ), polling 5 giây, `:key` dựng lại canvas khi đổi chế độ. |
| `van_phong/CanhVanPhong.vue` | camera, ánh sáng, phòng, nhân vật | **V** | Camera khít khung như hàm `khit()` của mockup. Ánh sáng ambient + hemisphere + directional có bóng đổ. Chiếu toạ độ nhãn ra 2D (§2.3.8). |
| `van_phong/DanhSachVanPhong.vue` | bản danh sách (bàn phím, không có WebGL) | **V** | Thẻ phòng có viền màu, chip nhân vật (mockup). Vẫn là đường dùng được bằng bàn phím và trình đọc màn hình (2c G16). |
| `van_phong/NhanVat3D.vue` | nhân vật trụ + cầu | **V** | Chibi của mockup: chân, thân, đầu, tóc, tay giơ, bóng tròn, ghế khi ngồi, `CO_NV = 1.4`. |
| `van_phong/Phong3D.vue` | sàn + 2 tường + biển chữ | **V** | Sàn, tường chung có cửa, tường trước thấp, đồ đạc (bàn, màn hình, cây, quầy, tủ máy, đèn Điều phối). |
| `van_phong/TheChu3D.vue` | sprite chữ (texture canvas) | **B** | Thay bằng nhãn HTML phủ: chữ nét, đúng font, chọn được, có `aria`. Tránh luôn lỗi chữ quá nhỏ ở 975×536 (`bs-78r.5`). |
| `van_phong/bo_tri.js` | lưới phòng ô 6 m, chỗ ngồi | **V** | Lưới ô 10 m theo mockup, phòng cố định, Góc cà phê 2 ô, luật thêm dự án (Q9), bàn và chỗ của khe. |
| `van_phong/hien_thi.js` | tư thế, màu, chữ biển/bong bóng, đường dẫn khi bấm | G | Giữ `tuThe`, `catChu`, `chuBien`, `chuBongBong`, `duongDanNhanVat`, `duongDanPhong` (2c G9), `chuNhip` (2e T4). Đổi `MAU` sang bảng màu mockup. |
| `van_phong/the_chu.js` | vẽ chữ lên canvas | **B** | đi cùng `TheChu3D.vue` |

**Tổng**: 42 file. **G 30** (trong đó 9 file `.js` gốc giữ nguyên hoặc chỉ đổi chữ) · **V 10** · **B 2**.

**Test node (`frontend/tests/`)**:

| File | Chọn | Ghi chú |
|---|---|---|
| `luat.test.mjs` | giữ | Sửa kỳ vọng `tieuDeTab` nếu đổi chữ. |
| `doi_ngu.test.mjs` | giữ | 2d T2 thêm test. |
| `giao_viec.test.mjs` | giữ | 2d T5 thêm test. |
| `nho.test.mjs` | giữ | |
| `spec.test.mjs` | giữ | |
| `kiem_dist.test.mjs` | giữ, mở rộng | Thêm mẫu mới (§2.3.3). |
| `van_phong.test.mjs` | viết lại phần `bo_tri` | Giữ phần `hien_thi`. 2e T4 thêm `dieu_phoi.test.mjs`. |

**Script và cấu hình**:
- `kiem-an-toan.mjs`, `kiem-dist.mjs`: giữ, mở rộng.
- `vite.config.js`: giữ.
- `index.html`: đổi `<title>`.
- `package.json`: không thêm gói, trừ khi Đại ca chọn gói font (Q1).

### 2.3 Ràng buộc PHẢI giữ

1. **CSP chặt** (spec 2 §4 mục 6): `default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; font-src 'self'; …`. Không `unsafe-inline`, không `unsafe-eval`, không tài nguyên ngoài.
   - **Mockup vi phạm ở nhiều chỗ, phải chuyển hết.** Chép mockup sang Vue không được, phải dựng lại theo token.
     - `<link>` tới Google Fonts;
     - `importmap` nội tuyến và three từ jsdelivr;
     - 37 thuộc tính `style="…"` (`trang.js` 21, `trang-tong-quan.js` 8, `trang-van-phong.js` 5, `trang-cai-dat.js` 3);
     - `innerHTML` ở mọi file.
   - **Phát hiện thêm về Vue khi build.** Trình biên dịch Vue 3.5 gộp khối tĩnh lớn thành **chuỗi HTML** rồi chèn bằng `innerHTML`: từ 20 nút liên tiếp, hoặc 5 phần tử có thuộc tính tĩnh (`stringifyStatic` trong `@vue/compiler-dom`).
     - Bản thân CSP không chặn `innerHTML`. Nhưng `style="…"` nằm trong chuỗi đó thì bị `style-src 'self'` chặn.
     - Vì vậy **cấm `style="` tĩnh trong mọi template `.vue`**.
     - `:style="{…}"` vẫn dùng được: Vue đặt qua CSSOM (`el.style`), CSP không chặn.
     - Các icon SVG nhiều `<path>` sẽ bị gộp thành chuỗi. Không sao, vì thuộc tính trình bày như `stroke` hay `d` không phải `style`.
   - **Font.** `font-src 'self'` không cho Google Fonts. Ba cách:

     | Cách | Mô tả | Tốt | Kém |
     |---|---|---|---|
     | **(a)** Font hệ thống | `--sans: -apple-system, "SF Pro Text", "Segoe UI", Roboto, sans-serif`; `--mono: ui-monospace, SFMono-Regular, Menlo, monospace` | Không tải gì. SF hiển thị tiếng Việt tốt trên macOS/iOS. | Hình chữ khác mockup: Be Vietnam Pro tròn hơn, đậm hơn ở 800. |
     | **(b)** Tự host woff2, **Em khuyên** | Be Vietnam Pro 400/500/600/700/800 và JetBrains Mono 400/500, subset `latin` + `vietnamese`. Cả hai font giấy phép **SIL OFL 1.1**, được nhúng và phân phối lại, phải kèm `OFL.txt`. Đặt ở `frontend/src/assets/font/`, khai báo `@font-face` trong CSS để Vite băm tên và phát ra `dist/assets/` (cùng nguồn), `font-display: swap`, font hệ thống làm dự phòng. Mockup có trọng lượng 450 và 650, đổi thành 500 và 600. | Giống mockup. Nhãn HTML trên cảnh 3D dùng chung font. | Phải **tải một lần** (cần Đại ca cho phép, như lần tải gói npm 15/10). Ước tính 200–250 kB cho 7 file, phải đo khi tải. Thêm file nhị phân vào git. |
     | **(c)** Gói `@fontsource/be-vietnam-pro` và `@fontsource/jetbrains-mono` | phiên bản chính xác, `--ignore-scripts` | Có sẵn file và giấy phép. | Thêm hai phụ thuộc npm. Phải chọn đúng file subset để khỏi kéo cả gói vào `dist`. |

2. **Chunk lười cho Văn phòng**:
   - `component: () => import('./trang/VanPhong.vue')`;
   - `kiemGoiChinh` báo lỗi nếu gói chính chứa `WebGLRenderer`.
   - Trang Tổng quan **không** được import gì từ `van_phong/*.vue` hay `three`.
   - Panel và nhãn của Văn phòng ở trong chunk lười.
   - Chibi SVG dùng ở Đội ngũ AI và Tổng quan là SVG thuần trong component riêng, không kéo three.
   - Giữ D6 (≤ 2 giây): đo lại kích thước gói chính sau khi thêm font và icon.

3. **`kiem-an-toan` / `kiem-dist`**: giữ nguyên các luật hiện có.
   - `kiem-an-toan`: cấm `v-html`, `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write` trong `src/`.
   - `kiem-dist`: cấm `eval(`, `new Function`, biên dịch WebAssembly; `index.html` không có script/style nội tuyến hay thuộc tính `on*`; three không nằm ở gói chính.

   Đề xuất thêm (task F9):
   - `kiem-an-toan`: cấm `style="` tĩnh trong `.vue`. Cấm URL `http(s)://` ngoài trong `src/`, trừ chuỗi kiểm `https://github.com/` của `laLinkAnToan`.
   - `kiem-dist`: cấm `fonts.googleapis`, `fonts.gstatic`, `cdn.jsdelivr`, `unpkg` trong `dist/`. Cấm `style=` nằm trong chuỗi khối tĩnh của bundle (`createStaticVNode`).

4. **`laLinkAnToan`**: chỉ link `https://github.com/…`. Mọi link PR (`ban_giao.pr`, `pr.tram.url`, `giao.pr.link`) phải qua hàm này, cộng `target="_blank" rel="noopener noreferrer"`. Link "PR #12 ↗" của mockup cũng vậy.

5. **SSE và polling**:
   - Giữ `moLuong()` và ba bộ đếm `phienBan*`.
   - Trang mới tải lại theo các tín hiệu sau:
     - Tổng quan: `phe_duyet_doi`, `cong_viec_doi`, `doi_ngu_doi`, cộng polling 5 giây (vì có nhịp tim và hạn mức);
     - Cài đặt: không cần SSE, tải khi mở trang và có nút "Kiểm lại";
     - Công việc: thêm `doi_ngu_doi` (dòng khe trên thẻ).
   - Viên "Đồng bộ" đổi thành "Mất kết nối" khi `kho.matKetNoi`.

6. **Ô Giảm chuyển động**:
   - Mặc định theo `prefers-reduced-motion`.
   - Bật thì `render-mode="on-demand"`, không nhún, không lắc, không vẫy, màn hình đỏ không nhấp nháy.
   - Đổi chế độ thì dựng lại `TresCanvas` (`:key`).
   - Mockup nhớ lựa chọn trong `localStorage`: được phép, phải bọc try/catch.
   - CSS chung giữ `@media (prefers-reduced-motion: reduce)`.

7. **Bài học camera của 2c T8**: TresJS 5.9.1 chỉ gọi `lookAt(0,0,0)` một lần lúc tạo camera, khi vị trí chưa đặt.
   - **Bắt buộc giữ `:look-at="[0, 0, 0]"`** trên `TresOrthographicCamera`.
   - Hàm "khít khung" mới (chiếu các góc sàn qua `matrixWorldInverse`) phải chạy **sau** khi camera đã đặt vị trí và `lookAt`, rồi gọi `updateMatrixWorld()`.
   - Quét tĩnh và test node không bắt được lỗi này. Phải kiểm trên trình duyệt.
   - Thêm hai lưu ý từ ghi chú 2c:
     - pointer-events dò điểm bấm theo lần di chuột trước, nên công cụ tự động phải `hover` trước khi `click`;
     - `prefers-reduced-motion` không giả lập được trong khung Browser.

8. **TresJS 5.9.1 + three 0.186.1 so với mockup three thuần 0.160.0**:

   | Điểm | Mockup (three 0.160 thuần) | Khi chuyển sang TresJS 5.9.1 / three 0.186.1 |
   |---|---|---|
   | Tone mapping | mặc định `NoToneMapping` | `TresCanvas` mặc định **`ACESFilmicToneMapping`**, làm màu pastel nhạt và tối đi. Phải truyền `:tone-mapping="NoToneMapping"`. Trong mã Tres có `if (value) renderer.toneMapping = value`, nên giá trị 0 không được ghi. Hiện tại vẫn ra đúng vì renderer mặc định đã là `NoToneMapping`, nhưng **phải kiểm trên trình duyệt**. |
   | Nền | `alpha: true`, nền gradient bằng CSS | `TresCanvas` mặc định `clear-color #000`, `clear-alpha 1`. Truyền `:clear-alpha="0"` để thấy gradient CSS của `.canh-khung`. |
   | Bóng đổ | `shadowMap.enabled`, `PCFSoftShadowMap`, map 2048, khung bóng ±26, `bias -0.0006`, `normalBias 0.03` | `:shadows="true"`, `:shadow-map-type`. **three 0.186 đã bỏ `PCFSoftShadowMap`**: dùng sẽ cảnh báo "has been removed. Using PCFShadowMap instead". Bóng sẽ cứng hơn ảnh mockup. Chọn `PCFShadowMap` + `shadow.radius`, hoặc `VSMShadowMap` (Q17). Thông số đèn đặt qua prop xuyên (`shadow-map-size-width`, `shadow-camera-left`…), hoặc tạo đèn trong JS rồi gắn bằng `<primitive>`. |
   | Ánh sáng | Ambient 1.15, Hemisphere 0.75, Directional 1.55 | Hai bản đều sau r155, cùng đơn vị cường độ, chép số được. |
   | Đồ đạc | hàm JS dựng `Group` (bàn, cây, cốc, tủ…), khoảng 100 mesh | **Em khuyên** chuyển hàm dựng sang module JS thuần (`van_phong/dung_canh.js`, chỉ import `three`, không DOM), gắn vào cảnh bằng `<primitive :object>`. Lý do: viết lại hàng trăm thẻ `<TresMesh>` vừa dài vừa vượt 120 dòng. Huỷ (`dispose`) khi unmount như hàm `huy()` của mockup. Nhân vật dùng cùng cách (`nhan_vat_3d.js`), động tác qua `useLoop().onBeforeRender`. |
   | Camera khít khung | `khit()`: chiếu 8 góc mỗi phòng, đặt `left/right/top/bottom`, `PHONG_TO = 1.12` | Tính trong component con dưới `TresCanvas` (`useTres().sizes`). Đặt prop `left/right/top/bottom` như `CanhVanPhong` hiện tại (2c G13: Tres không tự cập nhật camera trực giao). Tách phần tính khung thành hàm thuần để test bằng node: three chạy được trong node vì không cần WebGL. |
   | Bấm chọn | `Raycaster` tự viết, `userData.chon` | Sự kiện `@click` của Tres (`@pmndrs/pointer-events`) trên mesh hoặc primitive. Với primitive, đặt `userData.chon` rồi đi ngược `parent` như mockup. Con trỏ "pointer" khi rê qua đặt bằng `@pointer-enter` / `@pointer-leave`. |
   | Chữ trên cảnh | HTML phủ lên canvas, chiếu toạ độ **mỗi khung hình**. `bo-tri-nhan.js` chống chồng nhãn, chạy **khi đổi cỡ khung** | Hai cách: **(1)** `CSS2DRenderer` có sẵn trong `three/examples/jsm`, không phải thêm gói, nhưng tự tạo phần tử DOM ngoài Vue và ghi transform mỗi khung, khó dùng `v-for` và khó chống chồng. **(2) Em khuyên**: tự chiếu. Component dưới `TresCanvas` tính toạ độ 2D của các điểm neo (`vector.project(camera)`) khi đổi cỡ hoặc đổi dữ liệu, chạy `boTriNhan` (port từ mockup thành hàm thuần, test bằng node), rồi `emit` ra trang. Trang vẽ lớp `<div class="lop-phu">` gồm các `<button>` nhãn, đặt bằng `:style="{ transform }"` (CSSOM, hợp CSP). Không cập nhật DOM mỗi khung: camera đứng yên, bong bóng không cần nhún. Nhãn là `<button>` thật, có `aria-label`, nên lớp phủ thành thêm một đường dùng bàn phím. |
   | Chống chồng nhãn | `boTriNhan(nhan, thanNv, W, H)` tham lam theo ưu tiên (bong bóng → huy hiệu → tên → huy hiệu Giám đốc → biển phòng), có "đường chỉ" SVG khi dời xa; `demChong()` | Port nguyên thuật toán. Test node: không chồng ở 1280, 1024 và 375 px với dữ liệu giả của mockup, đúng thứ tự ưu tiên, có đường chỉ khi dời > 10 px. Đo kích thước nhãn bằng `getBoundingClientRect` sau khi Vue vẽ (`nextTick`), nên phải chạy lại sau khi font tải xong (`document.fonts.ready`). |
   | WebGL | `try new WebGLRenderer` | Giữ kiểm `getContext('webgl2')` trước khi dựng `TresCanvas` (three bản ghim cần WebGL2). |
   | Dọn dẹp | `huy()`: `dispose` geometry/material, `forceContextLoss` | Tres tự `dispose` renderer khi unmount. Primitive tự dựng thì phải tự `dispose`. |

### 2.4 Đề xuất tổ chức lại

**Khung**:
- `KhungChinh.vue` = `ThanhBen.vue` (logo, menu 9 mục có `BieuTuong`, chân: máy trạm + thẻ người dùng) + `<div class="khung">` gồm `ThanhTren.vue` (ô tìm, viên đồng bộ, Estop), `BangEstop.vue` và `<router-view>`.
- Bảng menu đặt ở `menu.js` (thuần, có test).
- Dưới 900 px sidebar thành khối tĩnh phía trên, theo `@media` của mockup. Cần kiểm ở 375 px vì mockup chưa có ảnh điện thoại.

**Token CSS** (`kieu.css`, viết lại; giữ tên biến tiếng Việt của mockup):
- Màu nền và chữ: `--nen #faf6f0`, `--nen-2 #f3ece2`, `--nen-3 #f7f1e8`, `--the #fff`, `--vien #e7dccf`, `--vien-dam #d6c7b6`, `--chu #3b2a21`, `--chu-2 #6e5d50`, `--chu-phu #9a8a7c`.
- Màu nhấn: `--nhan #9a3f22`, `--nhan-dam #7f321a`, `--nhan-nhat #f5e1d6`.
- Màu trạng thái: `--xanh #4f9a6a`, `--vang #c98d22`, `--do #b8392b`, `--tim #7563b4`, `--xam #9a9189`.
- Khác: `--r 10px`, `--sans`, `--mono`.
- Gom thêm thành token các màu đang viết thẳng: nền chip trạng thái `tt-*`, `pr-*`, `.canh-bao`, hover menu `#eadfcf`, nền Estop `#fbefea`…
- Lớp dùng chung lấy theo mockup: `.the`, `.chip`, `.nut` (`.chinh`, `.nguy`), `.nhom-nut`, `.bang`, `.dau-trang`, `h2.muc`, `.ngan-ben`, `.canh-bao`, `.nho`, `.mono`.
- Đổi tên lớp `.nut` hiện có (nhóm nút) để tránh trùng với `.nut` (nút) của mockup.
- Font theo Q1.
- Chế độ tối theo Q2.

**Icon nét mảnh tự vẽ, không thêm gói**:
- Chép 10 icon từ `app.js` của mockup (9 mục menu và Cài đặt), cùng icon tìm, icon Estop.
- Đổi hết `<rect>` và `<circle>` thành `path d` để component chỉ có một kiểu phần tử.
- `bieu_tuong.js` (bảng `ten → [d…]`, thuần, test: mỗi icon có ít nhất một `d`, chỉ ký tự lệnh path hợp lệ).
- `BieuTuong.vue` vẽ `<svg viewBox="0 0 24 24" aria-hidden="true"><path v-for="d in ds" :d="d"/></svg>`. Nét lấy từ CSS (`fill: none; stroke: currentColor; stroke-width: 1.6`).
- Không `v-html`, không chuỗi SVG.

**Chibi**: `Chibi.vue` là SVG theo `chung.js::chibi`, màu bằng `:fill` binding. Màu chọn qua `mau_khe.js`:
- bảng 8 cặp (thân, tóc) lấy từ `du-lieu.js`;
- chọn theo băm FNV của `khe_id` để không đổi khi thêm khe;
- dùng chung cho cảnh 3D, Đội ngũ AI và Tổng quan.

**Cây file mới, phác thảo; mỗi file ≤ ~120 dòng**:

```
frontend/src/
  menu.js · bieu_tuong.js · mau_khe.js · luat_tong_quan.js · luat_cai_dat.js
  thanh/ThanhBen.vue · ThanhTren.vue · BangEstop.vue · BieuTuong.vue · Chibi.vue · ThanhHanMuc.vue · LenhCli.vue
  thanh/phe_duyet/TheReview.vue · TheHe.vue · TheBi.vue · TheSpec.vue · TheFeatureXong.vue
  trang/TongQuan.vue · CaiDat.vue  (+ thanh/tong_quan/*.vue, thanh/cai_dat/*.vue mỗi khối một file)
  van_phong/bo_tri.js (viết lại) · bo_tri_nhan.js · chieu.js · khung_nhin.js · dung_canh.js · nhan_vat_3d.js
  van_phong/LopNhan.vue · PanelChon.vue · CanhVanPhong.vue · DanhSachVanPhong.vue (viết lại)
  assets/font/*.woff2 + OFL.txt   (nếu Q1 chọn b)
```

---

## Phần 3 — Đề xuất chia lát "2f — giao diện theo mockup"

### 3.1 Điều kiện trước

1. 2d (sửa theo D25–D29) và 2e (sửa theo D24) **đã ghép** trên `main`, kể cả các task backend.
2. Đại ca trả lời các câu hỏi chặn plan: Q1 (font), Q3 (phần không có trong mockup), Q4 ("tạm đóng").
3. Nếu Q1 chọn (b) hoặc (c): Đại ca cho phép tải font hoặc gói một lần.
4. Mốc lấy trên `main` lúc bắt đầu: N₀ (pytest) và M₀ (node). Lúc khảo sát N₀ = 1987, M₀ = 33. Sau 2d và 2e dự kiến N₀ = 1987 + 13 + 14 = 2014, M₀ = 33 + 4 + 1 = 38. Phải **đo lại**.

### 3.2 Danh sách task

Quy ước như các plan trước:
- mỗi task một worktree, một commit, TDD;
- file ≤ ~120 dòng;
- Opus effort high cho task khó, Sonnet cho task dễ;
- Em QC từng task trước khi merge `--no-ff`.

**Backend (P)**:

| Task | Nội dung | File chính | Test py (ước) | Độ khó |
|---|---|---|---|---|
| P1 | Đọc hệ thống, thuần + có thể tiêm: `dich_vu.py` (đọc file plist, chạy `launchctl print`, phân tích `state`, `last exit code`), `keychain.py` (có/chưa/không rõ, không `-w`), `cau_hinh_doc.py` (tóm tắt cấu hình dự án, Telegram, cờ; không email, không băm), bộ đệm 30/60 giây | `tram/suy/he_thong/*.py` (mới) | 9 | vừa |
| P2 | Sự kiện gần đây: `KhoSuKien.moi_nhat_moi_du_an(n)` (hoặc dùng `sau_id`), `mo_ta_su_kien.py` (mẫu theo loại, danh sách cho phép), che `nho.*` | `tram/suy/mo_ta_su_kien.py`, `tram/su_kien/kho.py` | 3 | vừa |
| P3 | Route `GET /api/cai-dat`, `GET /api/san-sang` (Đại ca; 403/421/CSP; chuỗi cấm không xuất hiện trong JSON). Bảng sẵn sàng theo nguồn Q13 | `tram/api/cai_dat.py`, `tram/suy/san_sang.py` | 7 | vừa |
| P4 | Trường bổ sung T1–T4, T6 (và T2) | `tram/suy/{doi_ngu,phe_duyet,van_phong,trang_thai}.py`, `tram/api/tuyen_doc.py` | 6 | vừa |
| P5 | `GET /api/su-kien/gan-day`, `GET /api/tong-quan` (gom hàm route, gọi `phe_duyet` một lần) | `tram/api/tong_quan.py` | 2 | dễ |

**Frontend (F)**:

| Task | Nội dung | Test node (ước) | Độ khó |
|---|---|---|---|
| F1 | **Nền**: token CSS, font (Q1), `BieuTuong`, khung sidebar, thanh trên, băng estop, `menu.js`, tuyến mới (`/tong-quan` mở đầu; `/cai-dat`; hai trang tạm "đang dựng" cho tới F6, F7), `tieuDeTab` | 4 | vừa |
| F9 | **Cổng an toàn mở rộng**: `kiem-an-toan` (cấm `style="` tĩnh, URL ngoài), `kiem-dist` (font/CDN ngoài, `style=` trong khối tĩnh) | 3 | dễ |
| F2 | **Công việc + ngăn bên**: thẻ, chip, dòng khe (ghép với `/api/doi-ngu`), đầu cột, ngăn bên, OChot hai nút, giữ mọi khối của §1.3 | 2 | vừa |
| F3 | **Đội ngũ AI**: `Chibi`, `mau_khe.js`, `ThanhHanMuc`, thẻ khe, bảng điểm có nhóm nút (dùng hàm của 2d T2), luật vai | 4 | vừa |
| F4 | **Phê duyệt**: tách `MucPheDuyet` theo loại, chip PR trạm (T4), escalation có khe/bước, đủ 7 loại | 2 | vừa |
| F5a | **Văn phòng, phần thuần**: `bo_tri.js` (lưới 10 m, N dự án — Q9), `bo_tri_nhan.js` (port), `chieu.js`, `khung_nhin.js`, `dung_canh.js` và `nhan_vat_3d.js` (chỉ three, test khói trong node) | 9 | khó |
| F5b | **Văn phòng, component**: `CanhVanPhong` (camera `:look-at`, khít khung, ánh sáng, bóng, tone mapping, `primitive`), `LopNhan`, `PanelChon` (Q8), `DanhSachVanPhong`, giảm chuyển động, đèn Điều phối 3 trạng thái, tủ máy theo `suc_khoe.muc` | 0 (cổng là build, `kiem-dist`, kiểm trên trình duyệt) | khó |
| F6 | **Tổng quan**: 6 khối theo mockup, `luat_tong_quan.js` (ô việc chờ theo Q6, usage tách khe/API, hạn mức thấp nhất), polling 5 giây + SSE | 3 | vừa |
| F7 | **Cài đặt**: 6 khối, `LenhCli` (nút Sao chép: Clipboard API, dự phòng `execCommand`), `luat_cai_dat.js` (lệnh gợi ý, nhãn sẵn sàng, đếm), báo "Chỉ Đại ca xem" khi 403 | 3 | vừa |
| F8 | **Dự án** (lưới thẻ, "Mới xong"), **Ký ức**, **Usage**: thay vỏ theo Q3 | 0–1 | dễ |
| K | **Kiểm trên trình duyệt** (như 2c T8), dưới CSP thật của tram-api trên `127.0.0.1`: không có lỗi CSP trong Console; WebGL2; nhãn không chồng ở 1280, 1024 và 375 px; giảm chuyển động; font tải từ `'self'`; kích thước gói chính và chunk Văn phòng; bàn phím (Tab qua menu, thẻ, nhãn); 375 px. Cuối cùng ghi "Ghi chú triển khai". | — | vừa |

**Ước lượng**: khoảng **+27 test Python** và **+30 test node**. Mỗi task không chạm file của task khác cùng đợt.

### 3.3 Thứ tự đợt

```
Đợt 0 — điều kiện: 2d + 2e đã ghép; Q1/Q3/Q4 đã chốt; đo N₀, M₀

Đợt 1 — song song, không chung file
  P1 đọc hệ thống · P2 sự kiện gần đây · F1 nền giao diện · F9 cổng an toàn

Đợt 2 — sau đợt 1
  P3 route cài đặt/sẵn sàng (P1) · P4 trường bổ sung (2d, 2e)
  F2 Công việc (F1) · F3 Đội ngũ (F1) · F4 Phê duyệt (F1; chip PR cần P4) · F5a Văn phòng thuần (F1)

Đợt 3 — sau đợt 2
  P5 tổng quan (P2, P4) · F5b Văn phòng component (F5a, P4) · F7 Cài đặt (P3) · F8 Dự án/Ký ức/Usage (F1, P4)
  F6 Tổng quan (P5, F3 vì dùng Chibi/mau_khe) — chạy cuối đợt 3 hoặc đầu đợt 4

Đợt 4 — K kiểm trên trình duyệt + ghi chú triển khai
Chạy thật qua tailnet (máy A, điện thoại) — chờ 2a T26 (bs-6o0.11) như mọi phần dashboard
```

Theo memory "code hết rồi mới chạy thật": đợt K chỉ kiểm trên `127.0.0.1` của máy B với dữ liệu sẵn có. Không chạy dịch vụ mới, không bật gì.

### 3.4 Rủi ro đã thấy

1. **Mockup có khái niệm chưa có trong spec**: "tạm đóng", "Phiên 1/2", tủ máy nhiều màu, số đếm việc chờ gồm cột 2, các loại sự kiện `giao.cap`, `tho.mat_nhip`. Plan phải chốt từng chỗ, không tự bịa dữ liệu.
2. **Luật "mockup trước"**: nhiều phần của bản thật không có trong mockup (§1.3, §1.5, Ký ức, Usage). Nếu Đại ca đòi mockup cho từng phần thì 2f phải chờ thêm một vòng mockup.
3. **Văn phòng là phần khó nhất**: tone mapping, bóng đổ (PCFSoft đã bị bỏ), khít khung, nhãn phủ, bố trí N dự án. Lỗi kiểu camera của 2c T8 chỉ lộ ra trên trình duyệt, nên đợt K là bắt buộc.
4. **Kích thước gói chính**: thêm font, icon, hai trang mới. Đo lại theo D6 (≤ 2 giây).
5. **`tram/api/app.py` nằm trong danh sách tránh** của 2d/2e: cách đăng ký route mới phải ghi rõ trong plan (§1.10 mục 7).
6. **Bảng sẵn sàng đọc bead của repo trạm**: phương án (b) của A2 là một đường đọc mới. Hiện tram-api chỉ đọc bead của dự án trong `du-an/`. Phải chốt (Q13).

### 3.5 Câu hỏi mở cần Đại ca chốt

| # | Câu hỏi | Em đề xuất |
|---|---|---|
| **Q1** (chặn) | Font: (a) font hệ thống, (b) tự host woff2 Be Vietnam Pro + JetBrains Mono (OFL, tải một lần khoảng 200–250 kB), hay (c) gói `@fontsource` | **(b)** |
| Q2 | Chế độ tối: mockup chỉ có nền sáng, bản hiện tại có tối theo hệ thống. Bỏ tối, hay giữ (cần mockup tối)? | Bỏ tối ở 2f, làm sau nếu cần |
| **Q3** (chặn) | Phần bản thật có mà mockup không vẽ (hàng Chưa chấm/Epic/Feature theo plan, kéo cột + hộp Vì sao, Chuyển cột, Bàn giao, Bộ giao việc, Decision mở, Cờ đỏ, Spec chờ duyệt, Feature xong, cảnh báo hạn mức, trang Ký ức và Usage): (a) dựng thêm mockup trước plan, hay (b) cho phép giữ bố cục cũ và chỉ áp token và lớp của mockup | (b) cho phần nhỏ trong trang đã duyệt; (a) cho Ký ức và Usage nếu Đại ca muốn đổi bố cục |
| **Q4** (chặn) | "Dự án tạm đóng" (ke-toan) trong mockup: spec chưa có. Bỏ? Hay coi `bat_ghi: false` (D31) là "tạm đóng"? (Hai thứ khác nghĩa: `bat_ghi: false` là chỉ quét thử, không ghi) Hay thêm khoá mới? | Hiện chip theo `bat_ghi: false` với chữ "chỉ quét thử", bỏ chữ "tạm đóng" |
| Q5 | Ô tìm ⌘K: (a) tìm phía trình duyệt (bead đã tải, dự án, khe) ngay ở 2f, (b) ẩn tới lát sau | (a), bản đơn giản |
| Q6 | Số "việc chờ Đại ca": mockup cộng cả bead cột 2 và bỏ "Hệ cần xem". API `so` theo spec 2 §5.2 (không cột 2, có `he`). Badge menu, huy hiệu Giám đốc và tổng ở Tổng quan theo cách nào? | Badge và huy hiệu giữ `so` của API. Tổng quan hiện từng ô riêng, gồm cả cột 2, và ghi rõ tổng là "chờ ở Phê duyệt" |
| Q7 | Trang Phê duyệt hiện trạng thái PR trạm (mockup có), coi như trả lời C6 của 2d là "có"? | Có |
| Q8 | Bấm nhân vật/phòng: mở panel rồi mới có nút dẫn đi (mockup), hay đi thẳng như bản hiện tại? | Theo mockup |
| Q9 | Bố trí khi có hơn 3 dự án: mockup chỉ vẽ lưới 3×3 với 3 phòng dự án. Thêm hàng phía sau (đầu màn hình), camera tự khít? | Thêm hàng phía sau. Có thể xin một ảnh mockup 5 dự án trước F5b |
| Q10 | Tủ máy chủ mỗi tủ một màu (mockup): thêm `suc_khoe.muc[]` (T6), mỗi tủ ứng với một lý do theo mức, tủ thừa xanh? Hay 4 tủ cùng màu chung? | Thêm `muc[]` |
| Q11 | "Phiên 1/2": spec 3 không có số phiên tối đa. Chỉ hiện "1 phiên đang chạy"? | Có |
| Q12 | Tổng quan: một API gom `/api/tong-quan` (A4), hay trang gọi 5 API sẵn có cộng API sự kiện? D17 ghi "chỉ đọc từ các API đã có", trong khi "Sự kiện gần đây" bắt buộc phải có API mới | A4 gom bằng hàm route sẵn có, cộng A3 |
| Q13 | Cài đặt chỉ Đại ca xem (403 như Ký ức)? Bảng sẵn sàng lấy từ (a) bead repo trạm có nhãn `san-sang`, đọc bằng `bd` chỉ đọc, hay (b) bảng tĩnh trong mã (dễ lệch sổ tay)? | Chỉ Đại ca xem; nguồn (a), cộng các mục tự kiểm |
| Q14 | Thứ tự với 2d/2e: chạy 2d, 2e nguyên văn trước, chấp nhận 2f làm lại vài file `.vue` nhỏ? | Có |
| Q15 | Thẻ người dùng khi không có danh tính Đại ca (mở `127.0.0.1` trực tiếp): hiện "Chỉ đọc · không có danh tính Đại ca"? | Có |
| Q16 | Đường dẫn: giữ `/nho` hay đổi sang `/ky-uc` như mockup? | Giữ `/nho`, thêm bí danh `/ky-uc` |
| Q17 | Bóng đổ: three 0.186 đã bỏ `PCFSoftShadowMap`. Chấp nhận `PCFShadowMap` + `radius` (gần giống), hay thử `VSMShadowMap`? | PCF + radius, so ảnh ở đợt K |
| Q18 | Đèn Điều phối khi `sang: true/false` (2e) và dòng "nhịp cuối": mockup chỉ vẽ trạng thái "chưa có tín hiệu". Màu đèn sáng: vàng ấm `#f2c14e`, phát sáng (emissive)? | Vàng ấm, chữ "đang có phiên" / "tắt đèn" như `chuBien` |
