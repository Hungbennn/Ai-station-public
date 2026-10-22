# Phần 2 — Dashboard "Bàn điều hành"

Status: `ĐÃ DUYỆT` — Đại ca duyệt trên chat 13/10/2026 (bản tại commit 09ba973) · câu hỏi §12 đã được trả lời 13/10, xem §12
Ngày: 2026-10-12 (sửa 13/10 sau lát 1b-1: "Hệ cần xem", tin Telegram và bảng sự kiện thêm lỗi nạp ký ức `nho.loi_llm`, `nho.loi_embedder`, `nho.phuc_hoi` — G9 plan 1b-1, Đại ca chốt 13/10)
Kiến trúc tổng: [2026-10-12-tram-dieu-phoi-kien-truc.md](2026-10-12-tram-dieu-phoi-kien-truc.md)
Mẫu học theo: ảnh "NAPH AI — Bàn điều hành" (Đại ca gửi 12/10/2026; không tìm thấy trang công khai). Lấy cấu trúc menu và ý "văn phòng"; giao diện tự làm.

## 1. Mục tiêu

Một trang web trên máy B, mở từ máy A hoặc điện thoại qua Tailscale, cho Đại ca:
- thấy mọi việc của mọi dự án theo ba cột;
- xử lý mọi thứ đang chờ mình ở một chỗ (phê duyệt);
- biết từng khe AI đang làm gì, còn bao nhiêu hạn mức, tốn bao nhiêu;
- nhận tin Telegram khi có việc cần mình, thay vì ngồi canh.

## 2. Tiêu chí thành công

| # | Tiêu chí | Ngưỡng |
|---|---|---|
| D1 | Ba cột khớp nhãn beads theo luật suy cột §5.1 (so với `bd list --json`) | 100% |
| D2 | Bead đổi trên beads hiện trên dashboard không cần tải lại | ≤ 10 giây sau lượt quét |
| D3 | Kéo cột trên dashboard → bead có nhãn mới + `cot-khoa` + sự kiện `cot.dai_ca_sua` có `vi_sao` | đúng 100% lần thử |
| D4 | Thiết bị/người ngoài danh sách Đại ca gọi API ghi | bị từ chối 100% |
| D5 | Việc chờ Đại ca xuất hiện ở Phê duyệt và có tin Telegram | ≤ 2 phút; không quá 1 tin / 5 phút cho cùng loại |
| D6 | Trang tải trên máy A qua Tailscale | ≤ 2 giây (lát 2a) |

## 3. Kiến trúc

```
Máy B
  tram-api (FastAPI, trong gói tram, nghe 127.0.0.1:7700)
    ├─ đọc  : bd --json (mọi dự án trong du-an/) · nhật ký sự kiện SQLite · ccusage --json · trạng thái khe (phần 3)
    ├─ đẩy  : /api/luong (SSE) — phát khi có sự kiện mới trong SQLite
    ├─ ghi  : chỉ khi danh tính Tailscale ∈ danh sách Đại ca; lệnh bd dùng --actor dai-ca/dashboard
    └─ phục vụ file tĩnh của frontend (Vue build sẵn)
  tailscale serve https / → 127.0.0.1:7700        (chỉ trong tailnet; không funnel)
  tram-bao-tin (tiến trình launchd): đọc sự kiện mới → luật báo → Telegram
Frontend: Vue 3 + Vite + vue-router + TresJS (lát 2c); build ra dist/, commit không kèm dist
```

- **Trạng thái tính lúc đọc** (Q12): cột, việc chờ duyệt, trạng thái nhân vật đều suy ra từ beads + sự kiện; dashboard không có kho trạng thái riêng.
- **Một tiến trình đọc `bd` cho mỗi yêu cầu** là chậm; tram-api giữ bộ đệm beads theo dự án, làm mới khi có sự kiện `quet.xong` hoặc sau thao tác ghi, tối đa 30 giây một lần.

## 4. Bảo mật

1. Chỉ nghe `127.0.0.1`; ra ngoài **chỉ qua `tailscale serve`** (không `funnel`).
2. **Danh tính:** `tailscale serve` gắn header `Tailscale-User-Login` cho yêu cầu từ người dùng tailnet. API ghi chỉ chấp nhận khi header có mặt và nằm trong `dai_ca_logins` của `~/.tram/cau-hinh.yaml`. Thiếu header (gọi thẳng localhost, thiết bị gắn tag) → chỉ đọc. *Plan kiểm hành vi header thực tế với phiên bản Tailscale trên máy B (cần đăng nhập Tailscale — #5, chưa duyệt); không đạt → dùng mã truy cập dài + cookie.*
2b. **Cách ly — điều kiện trước khi bật phần 3a (#3, sửa 13/10):** header danh tính trên kết nối TCP `127.0.0.1` **giả được** bởi bất kỳ tiến trình cục bộ nào; tách user cho thợ mà backend vẫn nhận header trên TCP localhost thì **chưa đạt**. Yêu cầu: tram-api, Dolt, kho sự kiện, memory, khoá nội bộ và quyền Đại ca chỉ thuộc **tài khoản trạm**; `tram-tho` chạy dưới tài khoản quản lý thợ (giữ token máy), agent và mã repo chạy dưới **principal thực thi** không credential — cả hai không có quyền đọc/ghi các thứ đó (ba nhóm quyền, spec phần 3 §7.3); API ghi chỉ nhận yêu cầu đi qua một đường proxy được xác thực mà hai nhóm này không giả được. Cơ chế cụ thể (Unix socket chỉ tài khoản trạm đọc được, hay proxy khác) là **đề xuất cần spike** — chưa coi là năng lực đã có của `tailscale serve`. Trước 3a phải có kiểm chứng âm: từ principal thực thi (và principal kiểm lại `tram-kiem` của trạm), gọi API Duyệt với header giả, đọc khoá nội bộ, kết nối DB nghiệp vụ đều bị chặn. Lát 2a (chưa có thợ chạy trên B) dùng header như mục 2. Mac thợ từ xa (3b) là thiết bị **gắn tag** Tailscale.
3. **Chống CSRF:** mọi `POST` phải có header `X-Tram: 1` (trình duyệt không tự gắn cho form khác nguồn) và `Origin` khớp tên máy B trong tailnet.
4. Nội dung bead hiển thị bằng text, không bao giờ `v-html`; lọc ký tự điều khiển/bidi và cắt độ dài trước khi hiện (bài học ruflo).
5. Không gửi nội dung nghiệp vụ ra Telegram — chỉ mã bead, loại việc, tên dự án, link.
6. **Header an toàn và kiểm `Host`** (thêm 13/10 — G13, G17 plan 2a; Đại ca chốt dùng `@vitejs/plugin-vue` để bật CSP chặt): mọi phản hồi của tram-api mang `Content-Security-Policy: default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; font-src 'self'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'` (không `unsafe-eval`, không `unsafe-inline`), `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer`, `X-Frame-Options: DENY`; không gửi header phiên bản server. Yêu cầu có `Host` ngoài danh sách (`127.0.0.1:7700`, `localhost:7700`, tên máy B trong tailnet) → 421, chống DNS rebinding đọc API qua trình duyệt. Host mà `tailscale serve` chuyển tới cần kiểm khi #5 mở.

> **Ghi chú 16/10 (lát 2e, D24, D40):** `POST /api/dieu-phoi/nhip` (hook máy A, §5.5) đi qua đúng bộ kiểm của mục 2b và 3 (kênh ghi, danh tính Tailscale, `X-Tram`, `Origin`) và đòi **thêm** mã điều phối riêng `Authorization: Bearer` (trạm chỉ giữ sha256 ở khoá `dieu_phoi_ma_sha256`). Mã này không mở route nào khác; API ghi dashboard bỏ qua `Authorization`. Thêm giới hạn 30 lời gọi mỗi 60 giây cho cả route và thân tối đa 512 byte. Thứ tự kiểm: 421 Host → 403 kênh → 429 → 403 danh tính/CSRF → 401 mã điều phối → 413 → 422. Mã: `tram/api/dieu_phoi.py`, `tram/chu/ma_dieu_phoi.py`. Header Tailscale cho yêu cầu không từ trình duyệt chưa kiểm thật (spike H5 của 2e Task 5); nếu không có thì C4 của D40 cho phép bỏ đòi header riêng ở route này, vẫn đòi mã điều phối.

## 5. Màn hình

> **Ghi chú 16/10 (lát 2f, D17–D20, D33, D35, D38, D39):** giao diện đã làm lại theo mockup trong `docs/mockup/2026-10-15-giao-dien/`, chín mục menu: Tổng quan (trang mở đầu, D17; `/` chuyển về `/tong-quan`), Dự án, Văn phòng, Công việc, Đội ngũ AI, Ký ức (giữ `/nho`, thêm bí danh `/ky-uc`), Usage & chi phí, Phê duyệt, Cài đặt (chỉ đọc, chỉ Đại ca, D19). Trang Phân luồng bỏ khỏi menu (D18); luật vai ↔ khe vẫn ở Đội ngũ AI. Bỏ chế độ tối (D38). Font tự host (D35). Khi không có danh tính Đại ca, giao diện hiện thẻ "Chỉ đọc" và khoá mọi thao tác ghi. Mã: `frontend/src/trang/`, `frontend/src/tuyen.js`. Chỉ chạy trên máy chủ dữ liệu giả (`tests/chay_thu_giao_dien.py`) dưới CSP thật; chưa chạy qua tailnet.

### Lát 2a — dùng được ngay khi 1a chạy

**5.1 Công việc + Dự án**
- Chọn một dự án hoặc "Tất cả". Ba cột: `cot:ai-lam` · `cot:can-chot` · `cot:cho-review`. **Suy cột lúc đọc:** có nhãn `cot:*` → cột tương ứng (nhiều nhãn: `cho-review` > `can-chot` > `ai-lam`, dấu "nhãn lệch"); không có `cot:*` thì `can-spec` → cột 1 (mờ, "khe spec"), `cho-duyet-spec` → cột 2, `theo-plan` → hàng "feature đang chạy plan" (cạnh trang Dự án), bead `tram:escalation` → cột 2; còn lại → hàng "chưa chấm" phía trên. Bead mang `cot:ai-lam` nhưng bị chặn (kể cả bởi escalation) hiện mờ "chờ <id>".
- Thẻ bead: mã, tiêu đề, loại, ưu tiên, dự án; dấu khoá nếu `cot-khoa`; mờ + "chờ hr-xxx" nếu bị chặn; cờ đỏ nếu `co-do`.
- Bấm thẻ → ngăn bên: lý do của lần chấm gần nhất, câu hỏi cần chốt, mô tả, tiêu chí nghiệm thu, **dòng thời gian sự kiện** của bead.
- **Kéo thẻ giữa cột 1 và cột 2** → hộp "vì sao?" (tuỳ chọn) → `bd update --actor dai-ca/dashboard` (gỡ **mọi** nhãn `cot:*`, gắn nhãn mới + `cot-khoa`) + sự kiện `cot.dai_ca_sua` có `vi_sao`, `nguon: dashboard`, `da_ghi: true`. Thao tác có `ma_thao_tac` + `expected_version` (§12.3).
- **Epic** hiện ở hàng riêng, không được chấm, không có nút Chốt (#9). Không cho kéo vào/ra cột 3 (cột 3 do thợ và Phê duyệt quản).
- Bead decision đang mở không kéo được — trả lời bằng nút Trả lời (Đại ca chốt 13/10).
- **Trả lời câu hỏi cần chốt** (ở ngăn bên, cột 2): mỗi câu hỏi một ô trả lời → nút "Chốt":
  1. `bd create` một bead `decision` (tiêu đề "Chốt: <tiêu đề bead>", mô tả = các cặp hỏi–đáp + dấu `ma_thao_tac`), rồi `bd close` nó với `--reason` = tóm tắt câu trả lời;
  2. `bd dep add <bead> <decision>` (loại `blocks`);
  3. gỡ `cot-khoa` **và mọi nhãn `cot:*`** (#7) → bead về hàng "chưa chấm";
  4. sự kiện `cot.da_chot` → tạo **yêu cầu chấm lại bền** cho bead (spec 0+1a §5.6) và nạp vào memory ở phần 1b.
  Lượt quét sau chấm lại với prompt v2 có mục "Quyết định đã chốt". Thao tác idempotent theo `ma_thao_tac` (§12.3) — double-click hay crash giữa chừng không tạo hai decision.
  Câu trả lời dài hoặc mang tính kiến trúc: ô "dẫn ADR" thay cho trả lời — ghi `ADR-xxxx` vào decision.
- Trang **Dự án**: danh sách dự án đã `them` vào trạm, số bead mỗi cột, lần quét cuối, lỗi gần nhất.

**5.2 Phê duyệt** (badge số đếm trên menu và tiêu đề tab)

Gom, sắp theo độ gấp:

| Loại | Nguồn | Thao tác |
|---|---|---|
| Chờ review để đóng | bead `cot:cho-review` | **Duyệt** (Đại ca chốt 21/10 sau bs-8zi) → trước khi ghi thao tác, lấy `commit_ban_giao` của `bead.vao_cot_3` mới nhất sau `cot.tra_ve`, fetch kho kiểm và chỉ đóng khi commit là tổ tiên nhánh chính remote, hoặc PR trong bàn giao/`pr.mo` được `gh` xác nhận đã merge (`mergedAt` khác null, base đúng nhánh chính; giữ Duyệt tay sau squash/rebase). Thiếu commit/kho kiểm, fetch lỗi, hoặc cần kiểm PR mà thiếu/lỗi `gh`: từ chối `KhongHopLe`, nói rõ lý do, không đóng. PR chưa merge: "PR <url> chưa merge — merge trên GitHub (Create a merge commit) rồi bấm Duyệt"; chưa có PR và commit chưa vào: "Commit chưa vào main và trạm chưa mở PR — ghép nhánh tram/<bead> vào main rồi bấm Duyệt" (dùng tên nhánh chính cấu hình). Lý do đóng theo commit: "Đại ca duyệt — commit <sha7> đã vào <nhánh>"; theo PR: giữ "Đại ca xác nhận đã merge PR …". Bàn giao thiếu/lỗi chỉ duyệt được nếu vẫn xác minh commit từ sự kiện. Từ phần 4, Duyệt hiện commit đã kiểm (spec phần 4 §6.7); lát 4c giữ tự đóng khi xác minh được PR đúng repo/nhánh đã merge bản đã kiểm · **Trả về + góp ý** → gỡ **mọi** `cot:*` và `cot-khoa`, ghi góp ý vào notes, sự kiện `cot.tra_ve` (bài học); lượt quét sau chấm lại. Trả về không tái dùng kết quả QC của vòng trước |
| Spec chờ duyệt | bead `cho-duyet-spec` (phần 4) | (nút có từ 2a, nối phần xử lý ở 4b) **Duyệt** / **Trả về + góp ý**. Trang hiện commit spec đang xem; request Duyệt mang `expected_commit` + digest danh sách bead đề xuất — server thấy bản khác → 409, buộc Đại ca xem bản mới (spec phần 4 §7.3). Nút **"Mở trên máy A"** hiện lệnh/skill để thảo luận trong phiên Claude (skill chỉ đọc) |
| Bí / escalation, decision mở | bead `tram:escalation` (phần 4); bead `decision` đang mở không phải escalation (thêm 13/10 — Đại ca chọn: dùng chung nút Trả lời, đóng decision kèm câu trả lời; 1a chấm lại bead phụ thuộc qua ảnh decision) | Nút **Trả lời** (#11): ô trả lời → `bd close <escalation> --reason "<trả lời>" --actor dai-ca/dashboard` — đóng **chính** escalation, không tạo decision thứ hai như nút Chốt; sự kiện `escalation.tra_loi`; phần 4 phát `escalation.dong` đúng một lần ở vòng tick. Câu trả lời không cấp quyền làm thao tác nguy hiểm (Q6) |
| Cờ đỏ | bead có `co-do` | Mở bàn giao + diff (link PR) |
| Hệ cần xem | sự kiện `cham_cot.bo_qua` (lỗi liên tiếp), `quet.loi`, cầu dao khe (phần 3); từ 1b-1: nạp ký ức đứng — `nho.loi_llm`, `nho.loi_embedder` của dự án, hiện tới khi có `nho.phuc_hoi` cùng loại (spec 1b §6.2) | Xem lỗi; nút "thử lại" → sự kiện `cham_cot.thu_lai` = reset chuỗi lỗi **và** yêu cầu chấm lại bền (§12.5). Mục lỗi nạp ký ức **không** có nút "thử lại" (nút đó chấm lại cột, không phải memory; memory tự thử lại mỗi 2 phút) — mã bead kẹt nằm trong nội dung lỗi |

> **Ghi chú 16/10 (lát 2d, 4c; D15, D38):** thẻ cột 3 và ngăn bên hiện **trạng thái PR do trạm mở**: `pr.tram {so, url, trang_thai: "mo" | "khong_xac_minh" | "da_merge", ly_do}`, chỉ tính sự kiện `pr.*` ghi sau `bead.vao_cot_3` đang hiện và đúng `commit_ban_giao` (`tram/suy/pr_tram.py`, `GET /api/giao-viec`). Lý do không xác minh là câu dựng từ bảng cố định, không lấy chữ từ GitHub. Mục "Chờ review để đóng" của `GET /api/phe-duyet` mang `chi_tiet.pr_tram` và trang Phê duyệt hiện trạng thái này (C6 = có, D38). SSE làm mới khi có sự kiện `pr.*`. Nút Duyệt tay vẫn còn cho squash/rebase và PR mà trạm tự động không xác minh được, nhưng phải qua một trong hai bằng chứng ở hàng trên; thiếu bằng chứng thì từ chối (Đại ca chốt 21/10 sau bs-8zi).

**5.3 Thanh trạng thái trạm chủ** (mọi màn): estop bật/tắt, lần quét cuối, lỗi gần nhất. **Nút estop / tiếp tục** (gọi cùng logic `tram chu estop`).

### Lát 2b — cần phần 3

**5.4 Đội ngũ AI + Usage**
- Mỗi khe một thẻ: máy, CLI, tài khoản (tên gợi nhớ, không hiện email), vai ưu tiên, trạng thái (đang làm `<bead>` / rảnh / tắt / cầu dao ngắt / mất kết nối / cần Đại ca / lỗi lần chạy cuối), hạn mức còn lại + giờ reset, số phiên đồng thời.
- **Bật/tắt từng khe** (vd để dành hạn mức Claude cho việc tay) → sự kiện `khe.bat` / `khe.tat`; bộ giao việc (phần 4) tôn trọng.
- Usage: token + chi phí theo ngày/tuần, theo khe, theo dự án — từ sự kiện của trạm + `ccusage --json` trên máy B.
- Bảng điểm thợ: theo khe × vai — ở 2b có số phiếu, số xong, số lần chạy trung bình trên phiếu kết thúc; ~~tỉ lệ qua lần đầu và bị trả về là `null`, ghi rõ chờ phần 4, không hiện 0 giả.~~ (xem ghi chú 16/10 ngay dưới: hai tỉ lệ này đã tính từ sự kiện phần 4.)
- **Ghi chú 16/10 (lát 2d; D14, D25–D29, D41; `tram/suy/{bang_diem,diem_giao_viec,doi_ngu}.py`, `tram/api/doi_ngu.py`):** hai tỉ lệ tính lúc đọc, **chỉ cho vai `coder`** (phiếu bước `code`); vai khác để `qua_lan_dau`, `bi_tra_ve` và cả hai cỡ mẫu là `null` (D29). Mẫu 0 thì tỉ lệ là `null` và giao diện hiện "chưa có", không hiện 0 giả. JSON mỗi hàng có thêm `qua_lan_dau_mau`, `bi_tra_ve_mau`.
  - **SHA của phiếu (D25):** `commit` của sự kiện `giao.cong_bo` cùng dự án, bead và lượt; nhiều bản thì lấy bản sau cùng. Phiếu chưa công bố không vào tử nhưng vẫn nằm trong mẫu.
  - **Qua lần đầu (D26, D29):** tử = số phiếu `code` mà `kiem.lai` sớm nhất có đúng SHA đạt, **và** `qc.ket_qua` sớm nhất cho cùng commit mà được ghi **sau** lần kiểm lại ấy có `ket_luan = dat`. Mẫu = số phiếu `code` có `phieu.ket_thuc = xong`. Tử không đòi phiếu đã xong.
  - **Bị trả về (D27):** mỗi sự kiện `bead.vao_cot_3` là một mẫu của khe giữ phiếu code trong bằng chứng của lần vào cột 3 đó (`giao_id_code`). Mẫu bị trả về khi sự kiện kế tiếp của bead (trong `bead.vao_cot_3`, `cot.tra_ve`) là `cot.tra_ve`, tức trả về xảy ra trước lần vào cột 3 kế tiếp.
  - **Lọc (D14, D28):** `GET /api/doi-ngu?du_an=&so_ngay=`; rỗng = mọi dự án, `so_ngay` 1–92, mặc định 30, tính theo thời điểm cấp phiếu (`cap_luc`). Dự án lạ → 404. Dự án lấy theo phiếu (D29). Trang Đội ngũ AI có ô chọn dự án và khoảng ngày; tỉ lệ hiện kèm cỡ mẫu, ví dụ "71% (5/7)".
  - **Đủ khe (D41):** `bang_diem` luôn có một hàng cho mỗi (khe, vai ưu tiên) của mọi khe đã khai, kể cả khe chưa có phiếu nào (0 phiếu, vai `coder` mẫu 0, vai khác mẫu `null`). Bộ lọc không làm mất hàng. Giao diện không tự ghép hàng.
  - Định nghĩa tương ứng ở spec phần 4 §12.
- Luật vai ↔ khe hiện ở đây (chưa có màn "Phân luồng" riêng).
- **Ghi chú 16/10 (lát 3b, 2f; D18, D44):** khe có `cli: "codex"` (3b) hiện trên Đội ngũ AI và Văn phòng 3D như mọi khe, với nhãn CLI "Codex" và tên nhân vật dùng chung hai nơi, ví dụ "Codex 1" (`tram/suy/nhan_vat.py`); hạn mức của khe Codex đến từ bộ đọc riêng (spec phần 3 §8.1). Trang Phân luồng riêng đã bỏ khỏi menu (D18).
- Hạn mức hiển thị `100 − phan_tram` đã dùng; cửa sổ chưa biết hiển thị “chưa biết” và thời điểm đọc. Không dùng ccusage để chặn nhận việc.
- SSE `doi_ngu_doi` khi có `khe.*`, `chay.*`, `giao.*`, `bao.*`, `tho.*`; polling 5 giây bổ sung cho trạng thái suy từ thời gian/nhịp tim không có sự kiện, đáp ứng D2 trong điều kiện kết nối bình thường.
- `phien_ban` của thẻ = `<id đăng ký/bật/tắt mới nhất>:<id cầu dao mới nhất>`. Bật/đóng cầu dao kiểm phiên bản dưới cùng giao dịch SQLite với ghi sự kiện, kể cả resume. Retry chưa ghi giữ phiên bản gốc; phiên bản mới cần mã thao tác mới. Tắt không kiểm phiên bản (dừng mềm #14). Cầu dao đã đóng → 409; khe lạ → 404; kho phiếu chưa bật → 501.
- Mục Hệ cần xem của cầu dao liên kết sang Đội ngũ AI, không có nút thử lại. Phiếu trên thẻ dùng danh sách trường cho phép, không trả credential hay toàn `noi_dung`.
- Usage dùng `chay.xong` (khe) + `cham_cot.ket_qua` (Claude API), ngày giờ VN/tuần ISO; ccusage là nguồn riêng của tài khoản trạm, không cộng hai nguồn để tránh đếm trùng. Thiếu giá → `null`/`thieu_gia`; giá của khe thuê bao chỉ là tương đương, không phải tiền trả thêm.

### Lát 2c — cần phần 3 + 4

**5.5 Văn phòng 3D isometric** (TresJS)
- **Phòng:** mỗi dự án đã `them` là một phòng (tên dự án trên biển); phòng cố định: **Điều phối** (máy A — sáng đèn khi có phiên điều phối), **Góc cà phê** (khe rảnh), **Phòng máy chủ** (máy B: tủ máy xanh/vàng/đỏ theo sức khoẻ trạm), **Phòng giám đốc** (badge số việc chờ Đại ca).
- **Nhân vật = khe**, tên theo CLI + số khe. Trạng thái suy từ nhịp tim + sự kiện:

| Trạng thái | Điều kiện | Hiển thị |
|---|---|---|
| Làm | khe đang giữ việc | ngồi bàn ở phòng dự án; bong bóng = tiêu đề bead + bước (spec/code/QC) |
| Rảnh | khe bật, không giữ việc | đứng ở góc cà phê |
| Cần người | bead của khe chờ Đại ca (`--can-hoi`, bí) | giơ tay, chấm đỏ trên đầu |
| Lỗi | thử lại thất bại / cầu dao ngắt | màn hình bàn đỏ |
| Tắt / mất kết nối | Đại ca tắt khe / mất nhịp tim | mờ, ngồi yên |

- Bấm nhân vật → mở bead đang làm; bấm phòng → lọc Công việc theo dự án.
- Hình **tự dựng bằng khối hình học** (hộp, trụ) + màu pastel; không dùng bộ sprite/mô hình có giấy phép mập mờ. Có chế độ giảm chuyển động.
- **Ghi chú 16/10 (lát 2e, 2f; D12, D24, D38, D40; `tram/suy/dieu_phoi.py`, `tram/api/dieu_phoi.py`, `may-a/hook-dieu-phoi/`):** **nguồn đèn Điều phối là hook của phiên Claude Code trên máy A** (mặc định mọi phiên; muốn hẹp hơn thì cài hook ở mức dự án). Hook báo `SessionStart`, `UserPromptSubmit`, `Stop`, `SessionEnd` cùng 16 hex băm của `session_id` — không gửi nội dung — qua `POST /api/dieu-phoi/nhip` (§7), mã điều phối lấy từ Keychain máy A (`tram-dieu-phoi-ma`, D24). Mỗi nhịp là sự kiện `dieu_phoi.nhip` của dự án `_tram`. `GET /api/van-phong` trả cho phòng Điều phối `sang` và `nhip_cuoi`: `null` = chưa từng có nhịp ("chưa có tín hiệu"); `true` = có phiên mà nhịp cuối không phải `SessionEnd` và cách đây không quá **15 phút**; `false` = mọi phiên đã `SessionEnd` hoặc quá hạn. Mỗi phiên ghi tối đa một nhịp mỗi 60 giây, trừ khi đổi giữa "đang chạy" và "kết thúc". Đèn vàng ấm `#f2c14e`; biển và danh sách hiện "đang có phiên" / "tắt đèn" và dòng "nhịp cuối". Hook không bao giờ chặn phiên: mỗi thao tác 2 giây, cả hook 4 giây, lỗi gì cũng im lặng. **Chưa chạy thật** (2e Task 5, chờ Tailscale máy A — D6).

## 6. Thông báo Telegram

- **Có trong lát 2a** (#12). Module `tram/bao_tin/`, chạy thành dịch vụ launchd riêng; đọc sự kiện mới từ SQLite bằng `sau_id` (mốc riêng).
- Gửi khi: bead vào cột 3 · spec chờ duyệt · escalation "bí" · cờ đỏ · cầu dao khe ngắt / khe hết hạn mức · trạm lỗi (quét thất bại 3 lần liền, `bd` lỗi; từ 1b-1: memory nạp đứng — `nho.loi_llm`, `nho.loi_embedder`) · estop bật/tắt.
- **Nguồn từng loại tin.** Lát 2a (chưa có phần 4): `tram-bao-tin` so bộ đệm beads trước/sau mỗi `quet.xong` để thấy nhãn `cot:cho-review`, `cho-duyet-spec`, `co-do`, bead `tram:escalation` mới xuất hiện; trạm lỗi từ `quet.loi` (sự kiện mới, §12) và `cham_cot.bo_qua`, từ 1b-1 thêm `nho.loi_llm`, `nho.loi_embedder` (một tin mỗi đợt lỗi — memory chỉ ghi một sự kiện mỗi đợt); estop từ `estop.bat/tat`. Từ phần 4: dùng `bead.vao_cot_3`, `spec.xong`, `escalation.tao`; từ phần 3: `khe.cau_dao_ngat`.
- **Chống ồn:** tin đầu tiên của một loại gửi ngay; các tin cùng loại tới sau trong cửa sổ 5 phút gom thành một tin (nên có thể trễ tới 5 phút — G9 plan 2a, Đại ca đồng ý 13/10); không gửi lại cùng (loại, bead) trong 1 giờ; giờ yên lặng tuỳ chọn (vd 23:00–07:00, chỉ gửi loại "trạm lỗi").
- Loại tin 2b: `khe_cau_dao`, `khe_het_han_muc` từ `khe.cau_dao_ngat`, dự án `_tram`, chỉ mã khe đã kiểm cú pháp; chống ồn theo (loại, khe), chịu giờ yên lặng như trên.
- **Ghi chú 16/10 (lát 2d, D15; `tram/bao_tin/{tin,nguon}.py`):** thêm hai loại tin `pr_da_merge` (từ sự kiện `pr.da_merge`) và `pr_khong_xac_minh` (từ `pr.khong_xac_minh`, "PR đã merge nhưng trạm không xác minh được"). Cả hai chịu chống ồn và giờ yên lặng như các loại khác; nội dung chỉ có tên dự án và mã bead, không URL PR, SHA hay lý do.
- **Gửi lỗi** (mạng, Telegram sập — Đại ca chọn 13/10): tin không gửi được được xếp lại và gửi lại ở vòng sau (15 giây); không mất tin, và lần gửi lỗi không tính vào luật "1 giờ".
- Nội dung: `[tram] hr-codex · 3 việc chờ review · 1 spec chờ duyệt → <link dashboard>` — không có nội dung nghiệp vụ.
- Token bot: Keychain dịch vụ `tram-telegram-bot-token`; `chat_id` trong `~/.tram/cau-hinh.yaml`. Đại ca tự tạo bot (@BotFather) và tự đưa token vào Keychain.
- **Sửa Q15 kiến trúc:** ngoại lệ gọi ra ngoài thêm `api.telegram.org` (Đại ca chọn 12/10/2026).

## 7. API (phác thảo — plan chốt chi tiết)

| Phương thức | Đường dẫn | Lát |
|---|---|---|
| GET | `/api/du-an` · `/api/cong-viec?du_an=` · `/api/bead/{du_an}/{id}` | 2a |
| POST | `/api/bead/{du_an}/{id}/cot` `{cot, vi_sao}` · `/api/bead/{du_an}/{id}/chot` `{tra_loi[] \| adr}` · `/api/bead/{du_an}/{id}/thu-lai` | 2a |
| GET | `/api/phe-duyet` | 2a |
| POST | `/api/phe-duyet/{du_an}/{id}/duyet` `{expected_commit?, digest_bead? (Duyệt spec — phần 4 §7.3)}` · `/tra-ve` `{gop_y}` · `/tra-loi` `{tra_loi}` (escalation hoặc decision mở) | 2a |
| GET/POST | `/api/chu/trang-thai` · `/api/chu/estop` · `/api/chu/tiep-tuc` | 2a |
| GET | `/api/luong` (SSE: `su_kien`, `cong_viec_doi`, `phe_duyet_doi`; 2b thêm `doi_ngu_doi`) | 2a |
| GET/POST | `/api/doi-ngu` · `/api/khe/{may_id}/{ten}/bat` · `/api/khe/{may_id}/{ten}/tat` · `/api/khe/{may_id}/{ten}/cau-dao-dong` · `/api/usage?so_ngay=14` (1–92) | 2b |
| GET/POST | `/api/nho/*` (xem, xoá, ghi tay ký ức; xem/xoá ký ức thăng cấp đang chờ tự có hiệu lực — spec 1b-3) | 1b-3 (màn Ký ức, trước 2b) |
| GET | `/api/van-phong` (phòng + nhân vật + trạng thái đã suy) | 2c |
| POST | `/api/dieu-phoi/nhip` `{su_kien, phien}` (hook máy A; §4 ghi chú 16/10, §5.5) | 2e |
| GET | `/api/tong-quan` · `/api/su-kien/gan-day?gioi_han=` (1–50; sự kiện `nho.*` che mô tả khi không phải Đại ca) | 2f |
| GET | `/api/cai-dat` · `/api/san-sang` (chỉ Đại ca, chỉ đọc; D19) | 2f |

Mọi `POST` ghi mang `ma_thao_tac` và `expected_version` (§12.3).

> **Ghi chú 16/10 (D14, D38, D39, D40):**
> - **Ngoại lệ (2e C6, D40):** `POST /api/dieu-phoi/nhip` **không** mang `ma_thao_tac` và `expected_version`. Nhịp không gắn bead nên không có phiên bản để so; gửi lặp vô hại vì trạm gộp ghi (mỗi phiên tối đa một nhịp mỗi 60 giây, kiểm và ghi trong một giao dịch `BEGIN IMMEDIATE`). Phản hồi `200 {"ghi": true | false}`, `false` nghĩa là đã gộp.
> - `GET /api/doi-ngu` nhận `?du_an=&so_ngay=` (§5.4). `GET /api/giao-viec` có `pr.tram`. `GET /api/phe-duyet` mục `cho-review` có `chi_tiet.pr_tram` (§5.2).
> - `GET /api/nho/su-kien` trả thêm `mo_ta`, câu tiếng Việt dựng từ mẫu cố định theo loại sự kiện thay cho `tom_tat` là JSON cắt dở (D39).
> - Lát 2f thêm trường cho Đội ngũ AI (`ten`, `vi_sao_tat` ở thẻ khe) và sự kiện mô tả sẵn; không đổi hành vi các API cũ.

## 8. Phụ thuộc mới

- Python: `fastapi`, `uvicorn` (chỉ thêm khi làm lát 2a). Không thêm ORM.
- Node trên máy B (build frontend): Vue 3, Vite, vue-router, `@vitejs/plugin-vue` (thêm 13/10 — G13 plan 2a, Đại ca đồng ý: component viết dạng `.vue`, dịch sẵn lúc build để bật được CSP chặt); lát 2c thêm TresJS (`@tresjs/core`) + `three`. Khoá phiên bản chính xác trong `package-lock.json`.
- `ccusage` (MIT) cài cố định khi Đại ca cho phép chạy thật: `npm install --prefix ~/.tram/ccusage --save-exact --ignore-scripts ccusage@<x.y.z>`. Không dùng `npx`; đường tuyệt đối, phiên bản `x.y.z` trong cấu hình, kiểm `--version` trước `daily --json --offline --since/--until`. Dạng JSON/cờ/TZ phải kiểm với bản thật sau cổng. Cache ok 10 phút, lỗi 1 phút từ lúc hoàn tất; tuần tự hoá lời gọi ngoài. Không trả stderr/argv/nội dung exception qua API. JSON ngày không hợp lệ hoặc số không hữu hạn bị từ chối.
- Telegram: gọi HTTPS trực tiếp bằng thư viện chuẩn (`urllib`), không thêm SDK.

## 9. Kiểm chứng

1. Unit test: suy cột/phê duyệt/trạng thái nhân vật từ beads + sự kiện giả; luật báo tin + chống ồn; kiểm danh tính + CSRF.
2. Test API với `bd` giả lập (không ghi beads thật).
3. Trên máy B thật: D1–D6; thử gọi API ghi từ thiết bị không thuộc danh sách (D4).
4. Kiểm tay giao diện trên máy A (trình duyệt) và điện thoại.

## 10. Ngoài phạm vi

- Màn "Phân luồng" riêng, "Muse Studio".
- Mở dashboard ra Internet (funnel), đăng nhập ngoài Tailscale.
- Sửa nội dung bead (tiêu đề, mô tả) từ dashboard — dùng `bd` hoặc phiên Claude.
- Merge PR từ dashboard (Q7: chỉ Đại ca merge trên GitHub).

## 11. Tham khảo (đã xem, 12/10/2026)

Cubicle, Star Office UI, Pixel Agents, pixtuoid (trạng thái nhân vật); disler/claude-code-hooks-multi-agent-observability (đường sự kiện → Vue 3, chưa rõ giấy phép — chỉ học); BeadBoard (SSE trên dữ liệu beads); beads-ui (sửa trực tiếp trên board); ccusage, Claude-Code-Usage-Monitor, CodexBar (usage/hạn mức — dùng ở 2b/phần 3); TresJS (3D trong Vue).

## 12. Quyết định đã chốt và việc cần làm trước plan 2a (sửa 13/10/2026)

Ban đầu là danh sách câu hỏi C1–C8; Đại ca đã trả lời ngày 13/10 ([quyết định 13/10](../quyet-dinh/2026-10-13-tra-loi-cau-hoi-gop.md), đánh số #). Sau đó [review Codex](../handovers/2026-10-13-phan-hoi-review-codex.md) bổ sung các hợp đồng còn thiếu. Mục này thay danh sách câu hỏi cũ. Trả lời câu hỏi **không** có nghĩa là toàn văn spec đã được duyệt.

### 12.1 Quyết định

| Mã cũ | Quyết định | Đã ghi vào |
|---|---|---|
| C1 | Nút **Chốt**: gỡ `cot-khoa` và **mọi** nhãn `cot:*`, tạo yêu cầu chấm lại bền; prompt chấm v2 có mục "Quyết định đã chốt" gồm `close_reason` (#7) | §5.1; spec 0+1a §5.3, §5.6 |
| C2 | Schema bàn giao thêm `pr: URL \| null`; Duyệt có nút "Đã merge trên GitHub → đóng bead" do Đại ca xác nhận tay ở 2a (#2) | §5.2; spec 0+1a §4.3 |
| C3 | Danh tính: xem §4 — đăng nhập Tailscale trên B thuộc #5, **chưa duyệt** | §4 |
| C4 | Bộ chấm **bỏ qua epic**; epic hiện ở hàng riêng, không có nút Chốt (#9). Lý do là quyết định của Đại ca, không dựa vào suy luận chiều lệnh `bd` (spike `bd` mục 3 ghi lệnh và lời kết luận chưa khớp — chưa có transcript hai chiều) | §5.1; spec 0+1a §5 |
| C5 | Mỗi bead **tối đa một** nhãn `cot:*`; mọi bên ghi thay toàn bộ tập `cot:*`; khối chèn tách phiên tay / agent trạm (#8). Mã 1a hiện **đã** đọc nhãn theo ưu tiên an toàn (`cho-review` > `can-chot` > `ai-lam`); phần còn thiếu là bên **ghi** — mã hiện chỉ gỡ một nhãn | §5.1, §5.2; kiến trúc §3, §8; spec 0+1a §5.4, §7 |
| C6 | **Telegram có trong 2a** (#12). Đại ca tự tạo bot và đưa token vào Keychain | §6 |
| C7 | Nút **Trả lời** escalation có trong 2a (#11) = `bd close <escalation> --reason "<trả lời>"` | §5.2, §7 |
| C8 | Cách ly (#3): xem §4 | §4 |
| — | Bộ chấm bỏ qua bead đang có phiếu hiệu lực (#10) | spec 0+1a §5 |

### 12.2 Phụ thuộc dữ liệu — lát nào sở hữu (Q05 của review)

| Thứ | Lát sở hữu | Ghi chú |
|---|---|---|
| `Bead` thêm `priority`, `parent`, `assignee`, `created_at`, `close_reason`, `closed_at` (mặc định cho trường thiếu) | **2a** | dashboard cần ưu tiên, escalation cần `close_reason`; 4a chỉ thêm trường chưa có |
| `SuKien.id`, `KhoSuKien.sau_id(id, gioi_han)` (phân trang), giữ cột `token_vao`, `token_ra`, `mo_hinh`, `thoi_gian_ms` qua mô hình đọc | **2a** | SSE, `tram-bao-tin`; Usage (2b) dùng lại, không đọc JSON để đoán cột đã lưu riêng |
| SQLite `journal_mode=WAL` + `timeout`; sao lưu bằng `sqlite3 .backup` | **2a** | dashboard là tiến trình ghi thứ hai |
| Bảng `thao_tac(ma_thao_tac PRIMARY KEY, loai, du_an, bead_id, digest_noi_dung, expected_version, buoc_da_xong, ket_qua, luc)` trong `~/.tram/su-kien.db` — tiến độ thao tác của §12.3 | **2a** | "kho vận hành" ở §12.3 nghĩa là bảng này; 3a thêm bảng phiếu và công việc chờ vào cùng file (spec phần 3 §6.6) |
| Khoá cấu hình lệnh/môi trường kiểm trong `du-an/<ten>.yaml` | 3a | spec phần 3 §3 |
| Sự kiện hệ không gắn dự án | mọi lát | dùng `du_an = "_tram"`; mọi chỗ liệt kê dự án bỏ tên bắt đầu `_` |

**Bảng sự kiện 2a** (producer → consumer, phiên bản dữ liệu 1). Nút **Duyệt** không có sự kiện riêng: dashboard và Telegram thấy bead đóng ở lượt quét kế tiếp (G5 plan 2a, Đại ca đồng ý 13/10). Nút Trả lời decision mở dùng chung sự kiện `escalation.tra_loi` (trường `escalation_id` là id decision).

| Sự kiện | Ghi bởi | Đọc bởi | Dữ liệu |
|---|---|---|---|
| `cot.dai_ca_sua` | dashboard (kéo cột), 1a (phát hiện sửa tay) | 1a (bài học, gỡ khoá), 1b | `{tieu_de, cot_he, cot_moi, ly_do_he, vi_sao?, nguon, da_ghi: true, ma_thao_tac?}` — `ma_thao_tac` khi nguồn là dashboard (G7, Đại ca đồng ý 13/10) |
| `cot.da_chot` | dashboard (Chốt) | 1a (yêu cầu chấm lại), 1b | `{decision_id, cau_hoi[], tra_loi[], adr?, ma_thao_tac}` |
| `cot.tra_ve` | dashboard (Trả về) | 1a, 1b, phần 4 | `{gop_y, ma_thao_tac}` |
| `cham_cot.thu_lai` | dashboard (thử lại) | 1a (reset chuỗi lỗi + yêu cầu chấm lại) | `{ma_thao_tac}` |
| `escalation.tra_loi` | dashboard (Trả lời) | phần 4 vòng tick (phát `escalation.dong`) | `{escalation_id, ma_thao_tac}` |
| `quet.loi` | 1a | dashboard, Telegram | `{loi}` |
| `cham_cot.can_cham_lai` | 1a (bộ quét thấy decision đổi/đóng/mở lại giữa hai lượt) | 1a (nguồn của yêu cầu chấm lại bền, spec 0+1a §5.6) | `{nguon, decision_ids[]}` — thêm 13/10 theo G4 plan sửa mã 1a, Đại ca đồng ý |
| `estop.bat` / `estop.tat` | CLI, dashboard | dashboard, Telegram | `{ly_do?, ma_thao_tac?}` — `ma_thao_tac` khi nguồn là dashboard (G7) |
| `nho.loi_llm`, `nho.loi_embedder` | memory service (1b-1) | dashboard ("Hệ cần xem"), Telegram (trạm lỗi) | `{su_kien_id, loi}` — một lần mỗi đợt lỗi; `du_an` + `bead_id` của sự kiện nguồn đang kẹt, **không** `_tram` (dashboard chỉ liệt kê dự án trong `du-an/*.yaml`) — spec 1b §6.2 |
| `nho.phuc_hoi` | memory service (1b-1) | dashboard (ẩn mục lỗi cùng loại) | `{loai: "llm" \| "embedder"}` |
| `dieu_phoi.nhip` | `POST /api/dieu-phoi/nhip` (hook máy A, lát 2e; thêm 16/10) | `GET /api/van-phong` (đèn Điều phối, §5.5) | `{su_kien, phien}`; `du_an = "_tram"`, `tac_nhan = "dai-ca/may-a"`; không vào SSE, Telegram hay ký ức |

Các sự kiện `nho.*` khác (`nho.ghi`, `nho.gop`, `nho.xoa`, `nho.loi_tach`) ở spec 1b §9.4; dashboard đọc từ 1b-3.

### 12.3 Tính bền của thao tác ghi (C04 của review)

Mọi nút ghi (kéo cột, Chốt, Duyệt, Trả về, Trả lời, thử lại, estop) gửi `ma_thao_tac` do trình duyệt sinh và `expected_version` (thời điểm `updated_at` hoặc commit mà Đại ca đang xem):

- Server khoá theo bead, ghi tiến độ từng bước của thao tác (ví dụ Chốt: tạo decision → đóng → nối → gỡ nhãn → sự kiện) vào bảng `thao_tac` (§12.2) **trước** khi gọi `bd`.
- Gửi lại cùng `ma_thao_tac` (double-click, mạng chập) trả kết quả cũ, không làm lại. Cùng mã mà nội dung khác → 409.
- Crash giữa chừng: lần sau đối soát với `bd list` (tìm decision có dấu `ma_thao_tac` trong mô tả) rồi làm tiếp bước chưa xong; không đoán "bước trước đã thất bại".
- Bead đổi so với `expected_version` → 409, dashboard tải lại.
- Ca kiểm: double-click Chốt; crash sau `bd create` trước `bd close`; crash sau `bd close` trước `bd dep add`; Trả về hai lần.

### 12.4 Việc chưa mở (giữ nguyên)

- Đăng nhập Tailscale trên B, tạo bot Telegram — việc tay của Đại ca; Tailscale thuộc #5, **chưa duyệt**. Plan 2a viết được, phần chạy thật qua tailnet chờ #5.

> **Ghi chú 15/10/2026** (không đổi C3 và đoạn trên): Tailscale máy B đã đăng nhập (`bs-g28.9`), Keychain đã có `tram-telegram-bot-token`, dịch vụ `vn.tram.bao-tin` đang chạy. `vn.tram.api` chưa cài và các bước `tailscale serve` chưa làm, nên 2a Task 26 (`bs-6o0.11`) vẫn treo. Phần #5 còn chờ xem [quyết định 13/10, mục "Ghi chú 15/10"](../quyet-dinh/2026-10-13-tra-loi-cau-hoi-gop.md).

### 12.5 Em tự quyết — làm trong plan 2a

- **Nút "thử lại"**: `cham_cot.thu_lai` vừa reset chuỗi lỗi vừa tạo yêu cầu chấm lại bền, độc lập `updated_at` (spec 0+1a §5.6). Chỉ reset bộ đếm là chưa đủ: khi đếm về 0, bead vẫn bị coi là "chưa đổi". Ca kiểm: bead đã 3 lỗi, không đổi nội dung, bấm thử lại → lượt sau chấm đúng một lần.
- **Bộ quét ghi `quet.loi {loi}`** khi `bd list` lỗi.
- **Đọc bàn giao có lỗi**: hàm trả danh sách lỗi (hiện `doc_khoi_ban_giao` trả `None` cho cả "không có" lẫn "hỏng").
- **`~/.tram/cau-hinh.yaml`**: `dai_ca_logins: [..]`, `ten_may_b`, `telegram: {chat_id, gio_yen_lang: "23:00-07:00"}`, `dashboard_url`. Không chứa bí mật; có thể chứa **băm** của mã Đại ca (spec 1b §9.3). (16/10, 2e D24: thêm khoá `dieu_phoi_ma_sha256`, băm mã điều phối của hook máy A; đặt bằng `tram chu dat-ma-dieu-phoi`.)
- **Bọc `bd`**: thêm `create`, `close`, `dep add` theo đúng cờ ở `docs/spikes/2026-10-13-bd-cli.md`; mọi lệnh ghi dùng `--actor dai-ca/dashboard`.
- **`tram chu cai-dat`** khi thêm `tram-bao-tin` in "gọi ra ngoài: Claude API, api.telegram.org, GitHub" (Q15 đã sửa).
- **Phần 4 thêm vào tram-api** (không phải việc của 2a): `POST /api/phieu/kiem` và hàng Phê duyệt "Feature xong, chờ đóng".
- **Giao diện**: spec không có bản vẽ; dựng theo skill frontend-ui-engineering, Đại ca xem lại khi kiểm tay (§9 mục 4).
- **Lát 2b, 2c** viết plan sau khi spec phần 3, 4 được duyệt.


## 13. Đồng bộ hợp đồng 2b sau review 13/10/2026

Các chi tiết dưới đây đã được Đại ca chấp nhận cùng plan 2b (bàn giao phản hồi đợt 1–2 ngày 13/10); không thay quyết định #1–#21, không mở cổng chạy thật.

- `khe.bat`, `khe.tat`, `khe.cau_dao_dong` từ dashboard có `ma_thao_tac`, `tac_nhan = dai-ca/dashboard`, `du_an = _tram`; đóng tay có `ly_do = dai-ca`, `toi_luc = null`. Ghi qua hàm worker chuẩn, không tạo đường ghi riêng. Producer dashboard 2b; consumer worker 3a, bộ giao việc 4a, dashboard/SSE.
- Cấu hình `usage` đọc riêng từ `~/.tram/cau-hinh.yaml`: `ccusage` (đường tuyệt đối), `ccusage_phien_ban` (`x.y.z`, phải cùng có/cùng thiếu); `gia_usd_moi_trieu_token: {model: {vao, ra, cache_doc?, cache_ghi?}}`, giá 0–1000 USD/triệu token, do Đại ca điền, không giá mặc định.
- API GET mới theo chính sách đọc chung của §4; POST dùng chung danh tính Đại ca + CSRF, Bearer thợ không cấp quyền. Cách ly proxy/local principal vẫn chờ S6; chưa là bằng chứng triển khai an toàn.
- Bộ mẫu ca kiểm 2b phải có resume sau crash trước ghi rồi CLI tắt khe → bật cũ bị 409; crash sau ghi → không ghi lại; lỗi ccusage chứa bí mật không ra JSON; dữ liệu ngày/NaN/Infinity không làm API 500; tích hợp giữ nguyên API/Ký ức 1b-3.


## 14. Đề xuất riêng lát 2c sau review đợt 3 — chờ duyệt

Không mở lại các quyết định đã duyệt và hợp đồng 2b §13. Lát 2c giữ API chỉ đọc và CSP §4 nguyên văn.

- Nhân vật có trạng thái gốc `ranh` hoặc `loi`, cầu dao không ngắt, phiếu cuối có escalation chưa đóng: hiển thị `can_nguoi`. Đây là phép chiếu riêng Văn phòng, không sửa trạng thái làm đầu vào giao việc.
- Chưa có producer chứng minh phiên điều phối đang mở: `sang: null`, đèn xám và chữ “chưa có tín hiệu”; không bịa trạng thái bật/tắt.
- Badge Phòng giám đốc lấy cùng hàm `phe_duyet(request)`; JSON/deep link ở G6/G8/G9 của plan 2c là hợp đồng mới chờ duyệt.
- Quét chuỗi bundle chỉ là kiểm tĩnh sơ bộ. Điều kiện nghiệm thu còn gồm WebGL2, CSP thực tế, giảm chuyển động, danh sách bàn phím, kích thước/tải lazy chunk ở Task 8; review tài liệu không xác nhận các kiểm này đã chạy.

## Trạng thái triển khai (15/10/2026)

Đối chiếu với mã trên `main` (1c5f507: 1987 test Python pass; frontend có 33 test node). Lát 2c đã ghép đủ Task 1–8 (cập nhật sau khi Task 7–8 xong 15/10). Dashboard mới chạy trên `127.0.0.1`, chưa chạy qua tailnet. D1–D6 chưa nghiệm thu.

**Cập nhật 16/10/2026:** đối chiếu lại với `main` `f5b1fdb` (2242 test Python pass, 95 test node; `npm run build` và `kiem-dist` xanh), bằng `ls` và `grep` trong `tram/`, `frontend/`, `may-a/`. Đã ghép thêm lát 2d (7/7 task), lát 2e (Task 1, 2, 3, 4, 6; Task 5 chạy thật chưa làm) và lát 2f (18/18 task, giao diện theo mockup). Hàng đổi có nhãn "(16/10)".

| Mục spec | Trạng thái | Nơi trong mã | Plan/Task |
|---|---|---|---|
| §3 tram-api, bộ đệm beads, SSE `/api/luong` | đã có mã + test | `tram/api/{app,bo_dem,luong,tuyen_doc}.py` | 2a |
| §4 mục 1–3 Danh tính Tailscale, CSRF | đã có mã + test; header thật chờ cổng chạy thật (#5) | `tram/api/bao_mat.py` | 2a |
| §4 mục 2b Kênh ghi cách ly (Unix socket) | đã có mã, chờ cổng chạy thật (S6, N2); mặc định `kenh_ghi: header` | `tram/api/kenh_ghi.py`, `tram/cau_hinh/cach_ly.py` | 3a-2 T10 |
| §4 mục 4, 6 Lọc bidi, CSP, kiểm `Host` | đã có mã + test | `tram/suy/lam_sach.py`, `tram/api/bao_mat.py`, `frontend/kiem-an-toan.mjs`, `kiem-dist.mjs` | 2a; 2c T4 |
| §5.1 Công việc, Dự án, kéo cột, Chốt | đã có mã + test | `tram/suy/{cot,chi_tiet}.py`, `tram/thao_tac/{cot,chot}.py`, `frontend/src/trang/{CongViec,DuAn}.vue` | 2a |
| §5.2 Phê duyệt: Duyệt, Trả về, Trả lời, Cờ đỏ, Hệ cần xem | đã có mã + test | `tram/suy/phe_duyet.py`, `tram/thao_tac/phe_duyet.py`, `frontend/src/trang/PheDuyet.vue` | 2a; 1b-1 |
| §5.2 Spec chờ duyệt, "Feature xong, chờ đóng" | đã có mã + test | `tram/suy/phe_duyet_spec.py`, `tram/thao_tac/{spec,duyet_spec}.py`, `frontend/src/thanh/ChiTietSpec.vue` | 4b |
| §5.2 Tự đóng sau khi xác minh PR đã merge (từ 4c) | đã có mã, chờ cổng chạy thật (S7); mặc định tắt | `tram/giao_viec/{pr,pr_merge,tick_github}.py` | 4c T5, T7 |
| §5.3 Thanh trạng thái, estop | đã có mã + test | `tram/thao_tac/estop.py`, `frontend/src/thanh/ThanhTrangThai.vue` | 2a |
| §5.4 Đội ngũ AI: thẻ khe, bật/tắt, đóng cầu dao | đã có mã + test; dữ liệu khe thật chờ cổng chạy thật (3a-2) | `tram/suy/doi_ngu.py`, `tram/thao_tac/khe.py`, `frontend/src/trang/DoiNgu.vue` | 2b |
| §5.4 Usage từ sự kiện + ccusage | đã có mã + test; ccusage chưa cài (chờ Đại ca cho phép) | `tram/usage/`, `tram/api/usage.py`, `frontend/src/trang/Usage.vue` | 2b T2–4, T11–12 |
| §5.4 Bảng điểm: số phiếu, số xong, lần chạy TB | đã có mã + test | `tram/suy/bang_diem.py` | 2b T9 |
| §5.4 Bảng điểm: "qua lần đầu", "bị trả về", cỡ mẫu, lọc dự án + ngày, hàng cho mọi khe đã khai | (16/10) đã có mã + test (D14, D25–D29, D41); số thật chờ chạy thật (bộ giao việc tắt mặc định) | `tram/suy/{bang_diem,diem_giao_viec,doi_ngu}.py`, `tram/api/doi_ngu.py`, `frontend/src/luat_doi_ngu.js` | 2d T1, T2, T6 |
| §5.5 Văn phòng: phòng, nhân vật, trạng thái, `/api/van-phong` | đã có mã + test | `tram/suy/{nhan_vat,van_phong}.py`, `tram/api/van_phong.py` | 2c T1–2, T5 |
| §5.5 Cảnh 3D TresJS, giảm chuyển động | đã có mã + test; 2c T8 đã kiểm trên trình duyệt dưới CSP thật (sửa camera `:look-at`) | `frontend/src/van_phong/`, `frontend/src/trang/VanPhong.vue` | 2c T3–4, T6 |
| §5.5 Bấm nhân vật → bead, bấm phòng → lọc Công việc; bản danh sách | đã có mã; kiểm tay ở 2c T8 | `frontend/src/van_phong/DanhSachVanPhong.vue`, `trang/CongViec.vue` | 2c T7, T8 |
| §5.5 Đèn Điều phối sáng khi có phiên điều phối | (16/10) đã có mã + test phía trạm (D12, D24): `POST /api/dieu-phoi/nhip`, mã điều phối riêng, hook máy A, `sang`/`nhip_cuoi` trong `/api/van-phong`; giao diện đèn ở 2f; **chưa chạy thật** (2e Task 5, chờ Tailscale máy A — D6) | `tram/api/dieu_phoi.py`, `tram/suy/{dieu_phoi,kho_nhip}.py`, `tram/chu/ma_dieu_phoi.py`, `may-a/hook-dieu-phoi/`, `frontend/src/van_phong/hien_thi.js` | 2e T1–T4, T6 |
| §6 Telegram, chống ồn, gửi lại | đã có mã + test; chờ cổng chạy thật (#5, bot). (16/10) thêm hai loại tin PR (D15) | `tram/bao_tin/` | 2a; 2b T6; 4b T7; 2d T4 |
| §7 API 2a, 2b, 1b-3, 2c | đã có mã + test | `tram/api/tuyen_*.py`, `doi_ngu.py`, `usage.py`, `van_phong.py` | 2a; 2b; 1b-3; 2c T5 |
| §5.2 PR trạm trên thẻ cột 3 và trang Phê duyệt (`pr.tram`, `chi_tiet.pr_tram`) | (16/10) đã có mã + test; PR thật chờ chạy thật (4c GitHub, S7) | `tram/suy/{pr_tram,giao_viec,phe_duyet}.py`, `tram/api/luong.py`, `frontend/src/giao_viec.js` | 2d T3, T5, T7 |
| §7 `GET /api/tong-quan`, `/api/su-kien/gan-day`, `/api/cai-dat`, `/api/san-sang`; mô tả sự kiện ký ức | (16/10) đã có mã + test | `tram/api/{tong_quan,cai_dat}.py`, `tram/suy/{cai_dat,san_sang,su_kien_gan_day,mo_ta_su_kien,mau_su_kien,mau_nho}.py` | 2f T4–T8 |
| §5 Giao diện theo mockup: Tổng quan, Cài đặt, Dự án, Văn phòng, Công việc, Đội ngũ AI, Ký ức, Usage, Phê duyệt; thẻ khe, chibi, thanh hạn mức | (16/10) đã có mã + test node; đã kiểm trên trình duyệt dưới CSP thật với máy chủ dữ liệu giả; **chưa chạy qua tailnet** | `frontend/src/{trang,thanh,van_phong}/`, `frontend/src/tuyen.js`, `tests/chay_thu_giao_dien.py` | 2f T1–T18 |
| §12.3 Thao tác ghi bền (`ma_thao_tac`, `expected_version`) | đã có mã + test | `tram/thao_tac/{kho,chung,chay}.py` | 2a |

### Lệch so với spec khi code

- §5.2, §4 mục 4 (bản sửa gộp 2a): `pr` có ký tự điều khiển Unicode thì không hiện thành link (bs-6o0.9). Lỗi 500 bất ngờ vẫn mang CSP và các header an toàn (bs-6o0.10). Kéo cột lưu `nhan_dau` để kết quả vẫn đúng khi chạy lại sau crash. Nút thử lại từ chối epic, bead đã đóng hoặc đã hoãn (bs-6o0.8).
- §6 (bs-6o0.5): giờ yên lặng có giờ đầu bằng giờ cuối được hiểu là khoảng rỗng, tức không chặn tin nào.
- §5.5 (2c G3): Văn phòng hiện "Cần người" cho khe có escalation mở của phiếu cuối, trong khi Đội ngũ AI vẫn hiện "Rảnh". Lý do: `trang_thai_khe` không đổi, vì bộ giao việc dựa vào trạng thái `ranh` (`tram/suy/nhan_vat.py`).
- ~~§5.5 (2c G4): đèn Điều phối luôn xám, chữ "chưa có tín hiệu", không đoán bật/tắt.~~ **Hết lệch từ 16/10** (2e): đèn suy từ nhịp hook máy A. Khi chưa có nhịp nào vẫn là `sang: null`, chữ "chưa có tín hiệu".
- §7: 4a-2 thêm `GET /api/giao-viec` và mục "Bộ giao việc" (lý do không giao, link/lệnh tạo PR). 4b thêm `POST /api/phieu/kiem`, hàng "Feature xong, chờ đóng" với nút đóng feature, và hai loại tin `spec_cho_merge`, `feature_xong` (`tram/bao_tin/tin.py`).
- §5.2 (4c): nút Duyệt tay vẫn còn cho squash/rebase khi `gh` xác nhận PR đã merge đúng nhánh chính; hoặc duyệt theo commit đã vào nhánh chính remote sau fetch. Không còn ngoại lệ đóng khi thiếu bằng chứng (Đại ca chốt 21/10 sau bs-8zi). ~~Thẻ cột 3 **chưa** hiện `pr.khong_xac_minh`, và chưa có tin "PR đã merge".~~ **Hết lệch từ 16/10** (2d): thẻ cột 3 hiện `pr.khong_xac_minh` kèm lý do, và có hai tin Telegram PR (D15).
- §7 (2e C6): `POST /api/dieu-phoi/nhip` không có `ma_thao_tac`/`expected_version` — ngoại lệ ghi ở §7.
- 2f (D38): giao diện bỏ chế độ tối; ô tìm ⌘K chạy phía trình duyệt; `/nho` giữ, thêm bí danh `/ky-uc`.

### Cổng còn treo

| Cổng | Việc | Bead |
|---|---|---|
| #5, §9 mục 3–4 | 2a Task 26: chạy trên máy B qua `tailscale serve`, Telegram, D1–D6, kiểm tay trên máy A và điện thoại | `bs-6o0.11` |
| §4 mục 2b (S6, N2) | Kênh ghi cách ly, kiểm chứng âm từ principal | `bs-8eh.4` |
| §8 ccusage | Cài ccusage cố định, kiểm cờ và JSON thật | — |
| 2c Task 8 | Kiểm trên trình duyệt: WebGL2, CSP thật, giảm chuyển động, kích thước chunk | đã xong 15/10; còn tinh chỉnh cỡ biển chữ (bs-78r.5) |
| ~~§5.5, §14~~ | ~~Đại ca chọn nguồn đèn Điều phối~~ — **đã chốt D12** (hook máy A) và D24 (mã riêng); bead `bs-urj.7` đóng phần code 16/10 | `bs-urj.7` |
| 2e Task 5 | Chạy thật hook trên máy A: H1–H6, kiểm header Tailscale cho yêu cầu không từ trình duyệt, đếm nhịp một ngày. Chờ #5 (2a T26) và Tailscale máy A (D6) | `bs-6o0.11`, `bs-8eh.17` |
| 2f theo dõi | Danh tính đổi giữa phiên chưa làm mới nút ghi cho tới khi `taiTrangThai()` chạy lại (máy chủ vẫn từ chối ghi 403); tiêu đề "Việc chờ Đại ca" bẻ dòng ở 375 px; chưa kiểm bàn phím đầy đủ (Tab qua nhãn Văn phòng, ⌘K), chế độ không WebGL, `prefers-reduced-motion` — làm ở đợt chạy thật cùng 2a T26 | — |

**Bỏ theo D58 (18/10/2026, bs-2bd.1.6):** route `GET /api/su-kien/gan-day` (bảng §7, hàng 161, và dòng §7 `GET /api/tong-quan`, `/api/su-kien/gan-day` ở bảng trên) đã bỏ khỏi `tram/api/tong_quan.py`; không màn nào gọi, Tổng quan lấy sự kiện gần đây qua `GET /api/tong-quan`. Spec giữ nguyên chữ cũ để lưu vết. Cũng bỏ `POST /api/phieu/kiem` (phần 4 từng thêm; còn nhắc ở dòng "Phần 4 thêm vào tram-api" và ghi chú §7 của 4b) — xem spec 4.

## Đồng bộ quyết định D1–D16 sau review đợt 4

Nguồn có thẩm quyền: [quyết định 15/10](../quyet-dinh/2026-10-15-chot-dot-4.md); không sửa quyết định. Những câu “chưa chốt” bên trên là lịch sử nếu đã có Dn thay thế:

- D1 chọn HR Codex bản sao trên B, sau Task 0; D2 chọn S1 sơ bộ → S6 → S1–S4 dưới principal; D3 thử user riêng mỗi khe trước, giữ nhánh sandbox dự phòng.
- D4 chọn công bố lai, chính thức sau S7. Snapshot có hai adapter nhưng chỉ chọn một nguồn toàn cục; **chưa có mã phối hợp lai trên cùng trạm**. Task 3c R3 bổ sung phần thiếu; không đánh đồng “có cả hai adapter” với “đã hỗ trợ D4”.
- D6 máy A chưa có Tailscale; D7 giữ memory đã cài; D8 chờ QC đạt đối với bàn giao code, spike giữ kiểm-lại đạt; D9/D10 không bỏ escalation máy móc/không cờ nguồn; D11 restart ngay sau 1b-4 T4 hoàn chỉnh.
- D12 đèn từ hook máy A: đã có plan 2e, chưa có mã/hook chạy thật. D13 không tự chọn S1–S8 của bảng điểm; D14 lọc mọi dự án/30 ngày mặc định; D15 cả hai loại tin PR. Mã snapshot chưa có các bổ sung 2d/2e này. **Cập nhật 16/10:** 2d và 2e (Task 1–4, 6) đã có mã, xem "Trạng thái triển khai"; S1–S8 đã chốt D25–D29; hook máy A chưa chạy thật.
- D16: cổng ADR không còn chờ adapter/nguồn mới. Chỉ decision `blocks` đã đóng; callback ADR giữ False. Các hàng `bs-8eh.11` chờ chọn nguồn bên trên được thay bằng D16 đã chốt.

“Đã có mã + test” chỉ là có module và test trong gói; số pass là lời bàn giao, không phải kết quả review độc lập. Root helper/hoàn tác 3c còn blocker R1/R2; không nâng trạng thái chạy thật dựa vào patch áp được hoặc fixture. Xem `../../REVIEW-CODEX.md` và sổ tay đã sửa đường cài dịch vụ.

