# Lát 2a — Dashboard "Bàn điều hành" — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use ai-skills:subagent-driven-development (recommended) or ai-skills:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Đại ca mở một trang web trên máy B (qua Tailscale) để thấy mọi bead của mọi dự án theo ba cột, kéo cột / chốt câu hỏi / duyệt / trả về / trả lời escalation hoặc decision mở / thử lại / estop ngay trên trang — mọi thao tác ghi bền và idempotent — và nhận tin Telegram ngắn khi có việc chờ mình.

**Architecture:** Hai tiến trình mới trong gói `tram`, cùng đọc `~/.tram/su-kien.db` (SQLite WAL): (1) **tram-api** (FastAPI, chỉ nghe `127.0.0.1:7700`, một worker) — đọc beads qua `bd` với bộ đệm theo dự án, suy cột / phê duyệt / trạng thái lúc đọc (Q12), ghi qua khung thao tác bền (bảng `thao_tac`, khoá theo bead, `ma_thao_tac` + `expected_version`), đẩy thay đổi qua SSE và phục vụ frontend Vue build sẵn; (2) **tram-bao-tin** — đọc sự kiện mới theo `sau_id`, so ảnh beads sau mỗi `quet.xong`, chống ồn, gửi Telegram bằng `urllib` (gửi lỗi thì xếp lại, gửi lại vòng sau). Frontend Vue 3 + vue-router, component `.vue` dịch sẵn lúc build bằng `@vitejs/plugin-vue` (spec §8, G13) nên dùng được bản Vue chỉ-runtime; mọi phản hồi của tram-api mang CSP chặt (không `unsafe-eval`, không `unsafe-inline`) và `Host` lạ bị 421 (spec §4 mục 6). Logic thuần test bằng `node --test`; `vite build` là cổng kiểm template.

**Tech Stack:** Python 3.12 (`uv`), `fastapi==0.143.0` (starlette 1.7.0) + `uvicorn==0.54.0` — số đã giải và chạy thử 13/10 (G20), `pydantic` 2, `pyyaml`, SQLite stdlib, `urllib` stdlib, `pytest`; Node (máy B đang có v26) + `vue@3.5.43`, `vue-router@5.4.0`, `vite@8.3.4`, `@vitejs/plugin-vue@6.0.10` (ghim chính xác trong `package-lock.json`), `node:test`.

**Spec:** [docs/specs/2026-10-12-phan-2-dashboard.md](../specs/2026-10-12-phan-2-dashboard.md) — §4 (gồm mục 6: CSP + kiểm `Host`, commit 3c4940b), §5 "Lát 2a", §6 (gồm "Gửi lỗi"), §7 (API lát 2a), §8 (có `@vitejs/plugin-vue` — bd58255), §9, §12 (bảng sở hữu dữ liệu, bảng sự kiện, §12.3 `ma_thao_tac`/`expected_version`, bảng `thao_tac`, §12.5). Đọc kèm: spec 0+1a [§4.3, §5, §7, §11](../specs/2026-10-12-phan-0-1a-cham-cot.md) · kiến trúc [Q12, Q15, §3](../specs/2026-10-12-tram-dieu-phoi-kien-truc.md) · [quyết định 13/10](../quyet-dinh/2026-10-13-tra-loi-cau-hoi-gop.md) (#2, #5, #7–#12) · [spike `bd`](../spikes/2026-10-13-bd-cli.md) · **điều kiện tiên quyết:** [plan sửa mã 1a cho lát 2a](2026-10-13-sua-ma-1a-lat-2a.md).

## Global Constraints

- **Điều kiện tiên quyết:** plan [2026-10-13-sua-ma-1a-lat-2a.md](2026-10-13-sua-ma-1a-lat-2a.md) đã thực thi và merge vào `main` (commit `d63c41c`), `uv run pytest -q` = **239 passed**. Plan này không lặp lại việc của plan đó (xem "Phụ thuộc plan 1a").
- Test **không** gọi Claude API thật, **không** gọi Telegram thật (hàm mở URL giả), **không** chạy `bd` thật (`tests/bd_gia.py` hoặc `runner=` giả), **không** đụng DB beads thật / repo HR Codex thật, **không** gọi mạng. `TRAM_HOME` trỏ thư mục tạm (`tests/conftest.py` đã có). Bước duy nhất cần mạng là cài gói (Task 1 bước 1, Task 23 bước 2).
- **Không** cài launchd (không chạy `tram chu cai-dat` thật), **không** đổi cài đặt hệ thống, **không** đăng nhập / cấu hình Tailscale — quyết định #5 **chưa duyệt**. Phần `tailscale serve` và header danh tính viết thành mã + test với header giả; mọi bước chạy thật qua tailnet đánh dấu **"chờ #5"** (Task 26).
- Bí mật: token bot Telegram chỉ đọc từ Keychain dịch vụ `tram-telegram-bot-token` hoặc biến môi trường `TRAM_TELEGRAM_BOT_TOKEN` do **Đại ca tự đặt**; agent không nhập hộ, không ghi ra file/log (che bằng `***`). `~/.tram/cau-hinh.yaml` không chứa bí mật.
- Phụ thuộc mới **chỉ** theo spec §8: Python `fastapi`, `uvicorn` (ghim `==` phiên bản cụ thể); frontend `vue`, `vue-router` (dependencies) và `vite`, `@vitejs/plugin-vue` (devDependencies — G13, Đại ca chọn 13/10), `npm install --save-exact`, khoá trong `frontend/package-lock.json`. **Không** ORM, không SDK Telegram (dùng `urllib`), không `httpx` (test dùng `tests/asgi_gia.py` tự viết), không `vitest`, không gói npm nào khác.
- tram-api chỉ nghe `127.0.0.1` (không có tuỳ chọn đổi host), cổng mặc định `7700`, **một tiến trình một worker** (khoá theo bead nằm trong bộ nhớ). Không `tailscale funnel`. Mọi phản hồi mang CSP chặt + `X-Content-Type-Options`, `Referrer-Policy`, `X-Frame-Options`; `Host` ∉ {`127.0.0.1:<cổng>`, `localhost:<cổng>`, `<ten_may_b>`, `<ten_may_b>:443`} → 421; uvicorn `server_header=False` (spec §4 mục 6).
- Mọi lệnh `bd` ghi từ dashboard dùng `--actor dai-ca/dashboard`; mọi sự kiện dashboard ghi có `tac_nhan = "dai-ca/dashboard"`. Không sửa `title/description/acceptance_criteria/assignee` của bead; không `bd dolt push`.
- Mọi `POST` ghi: header `Tailscale-User-Login` ∈ `dai_ca_logins` (đúng một giá trị) + `X-Tram: 1` + `Origin == https://<ten_may_b>`; thân có `ma_thao_tac` (8–64 ký tự `[A-Za-z0-9-]`) + `expected_version`; tiến độ ghi vào bảng `thao_tac` **trước** khi gọi `bd`.
- Nội dung bead hiển thị bằng text: component `.vue` (`<script setup>`) chỉ nội suy `{{ }}`; không dùng `v-html`, `:innerHTML`/`v-bind:innerHTML`, `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write` (script `kiem-an-toan.mjs` quét mọi file trong `src/` chặn); không script/style nội tuyến (CSP chặt); server lọc ký tự `Cc/Cf/Cs/Co` (giữ `\n`, `\t`) và cắt độ dài trước khi trả JSON; link PR: server chỉ trả `https://…`, trình duyệt chỉ hiện link `https://github.com/…` (N1).
- Telegram chỉ mang: mã bead, loại việc, tên dự án, link dashboard — không tiêu đề, không mô tả.
- Sự kiện hệ không gắn dự án dùng `du_an = "_tram"`; mọi chỗ liệt kê dự án bỏ tên bắt đầu `_`.
- Mỗi file nguồn ≤ ~120 dòng; TDD (test fail → mã → pass); giữ mọi test cũ xanh; định danh tiếng Việt không dấu như mã hiện có. Giờ lưu UTC ISO-8601 có `Z`; giờ hiển thị `Asia/Ho_Chi_Minh`.
- Mỗi task một commit riêng trên nhánh `feat/lat-2a-dashboard` trong worktree `.worktrees/lat-2a-dashboard` (người thực thi tạo — "Chuẩn bị"). Commit chỉ `git add` đúng file của task; không hai `git commit` cùng lúc; không push.
- Lệnh test Python: `uv run pytest -q` từ thư mục worktree. Lệnh kiểm frontend trong `frontend/`: `npm run kiem` (`node --test` + `kiem-an-toan.mjs`) và `npm run build` (`vite build` — cổng biên dịch template `.vue`: lỗi template làm build đỏ).

## Phụ thuộc plan 1a

Plan 1a ([2026-10-13-sua-ma-1a-lat-2a.md](2026-10-13-sua-ma-1a-lat-2a.md)) đã thực thi xong và merge vào `main` (`d63c41c`, 239 test) trong lúc viết plan này; tên hàm/kiểu dưới đây đối chiếu với **mã thật trên `main`**, và mã của plan 2a (các task Python không cần FastAPI) đã chạy thử nguyên văn trên một bản sao `git archive HEAD` — xem "Tự review" mục 4. Plan 2a **dùng** các interface sau (không sửa chúng, trừ chỗ ghi rõ):

| Thứ dùng | Từ task plan 1a | Plan 2a dùng ở |
|---|---|---|
| `Bead(..., priority: int \| None = None, parent: str = "", assignee: str = "", created_at: str = "", close_reason: str = "", closed_at: str = "")`; `Bead.tu_json` đọc các khoá cùng tên | T2 | `tests/bead_gia.py`, `tests/bd_gia.py` (`dataclasses.replace(..., close_reason=...)`), thẻ bead (`priority`) |
| `Bd.tat_ca()` ném `LoiBd` khi JSON hỏng; `Bd.phien_ban(id)` (đọc `updated_at` qua `bd show`) | T2 | bộ đệm, `Bd.mot()` (Task 6) |
| `BanGiao.pr: str \| None = None` (chỉ nhận `http(s)://host/đường-dẫn`) | T1 | `tram/ban_giao/doc.py` (Task 7) |
| `bi_chan_boi(bead, theo_id) -> tuple[str, ...]` (gồm cả ID thiếu — fail-closed) trong `tram/cham_cot/luat_cung.py` | T3 | suy cột (Task 8) |
| `NHAN_COT`, `NHAN_KHOA`, `GIO_VN` trong `tram/cham_cot/ghi.py` (tên giữ nguyên) | T4 | Task 8, 13, 14, 15, 19 |
| `cham_cot.ket_qua` có thể mang `"huy": "bead_doi_khi_cham" \| "khong_doc_duoc_version"` (`da_ghi: false`); `ket_qua{huy}` không cắt chuỗi lỗi | T4, T10 | lần chấm gần nhất, câu hỏi của Chốt, mục "Hệ cần xem" đều bỏ qua kết quả bị huỷ (Task 8, 9, 14) |
| `tram/su_kien/kho.py` bản plan 1a (112 dòng): `SuKien(..., id: int = 0)`, hằng `_CHON`, `KhoSuKien.yeu_cau` (`YeuCauChamLai` dùng chung kết nối), `dem_loi_lien_tiep` cắt ở `cham_cot.thu_lai` | T5 | Task 2 thay cả file (giữ nguyên hành vi 1a) |
| `quet.loi {loi}` (không `bead_id`) khi `bd list` lỗi; lượt lỗi **không** ghi `quet.bat_dau`/`quet.xong` | T7 | Phê duyệt "Hệ cần xem", Telegram "trạm lỗi" (Task 9, 20) |
| 1a **đọc** `cham_cot.thu_lai` (`YeuCauChamLai.nhan_su_kien_nguon` biến thành yêu cầu, `dem_loi_lien_tiep` cắt chuỗi lỗi) — dashboard là bên **ghi** (G14 của plan 1a) | T5, T10 | Task 13 ghi sự kiện; test gọi `nhan_su_kien_nguon` để chứng minh nối được |
| Sự kiện mới `cham_cot.can_cham_lai` (1a ghi, 1a đọc — Đại ca duyệt G4, spec §12.2 đã thêm, commit b448ef3) | T5, T9 | chỉ hiện trong dòng thời gian bead; 2a không xử lý thêm |
| `kiem()` → `KetQuaLuat.la_decision_mo` ép bead `decision` đang mở vào cột 2 (`luat_cung.py`, mã 1a gốc); `anh_decision` so `[đã_đóng, close_reason]` (`cham_lai.py`) | 1a gốc, T9 | nút Trả lời decision mở (Task 15, Q4): đóng decision kèm `close_reason` → lượt quét sau 1a thấy decision đổi → yêu cầu chấm lại bead phụ thuộc |

**Chênh lệch so với giả định ban đầu của plan 2a, và cách xử lý:**

1. **`cot.da_chot` không phải nguồn yêu cầu chấm lại trực tiếp trong plan 1a** (G4 plan 1a, Đại ca đồng ý 13/10). Plan 1a tạo yêu cầu từ `cham_cot.thu_lai`, `cham_cot.ket_qua{huy}` và từ **so ảnh decision** (G5: decision mới đã đóng / mở lại / đổi `close_reason` / biến mất → yêu cầu cho mọi bead phụ thuộc `blocks`). Nút Chốt tạo decision **đã đóng** rồi `bd dep add <bead> <decision>` → lượt quét sau thấy "decision mới đã đóng" mà bead phụ thuộc → yêu cầu chấm lại bền (nguồn `cham_cot.can_cham_lai`); thêm nữa, việc gỡ nhãn làm `updated_at` đổi → bead vào lượt chấm theo mốc. Kết quả giống spec §5.1 bước 4. **Plan 2a không thêm mã cho việc này**; Chốt vẫn ghi `cot.da_chot` đúng bảng sự kiện (cho 1b và lịch sử). Nếu Đại ca muốn `cot.da_chot` là nguồn trực tiếp, đó là việc thêm vào `YeuCauChamLai` (plan 1a), không phải 2a.
2. **`SuKien` nằm trong `tram/su_kien/kho.py`** (không tách `mo_hinh.py`), `id: int = 0` (không phải `None`). Task 2 giữ cấu trúc đó, chỉ thêm 4 trường token/mô hình **sau** `id`, mở rộng `_CHON`, đổi `sqlite3.connect` → `mo_ket_noi` (WAL + timeout), thêm `sau_id`, `id_moi_nhat`, `cua_bead`, và chuyển `LUOC_DO` sang `ket_noi.py` để giữ `kho.py` ≤ 120 dòng.
3. **`bd show` chưa được spike dạng `dependencies`** (G3 plan 1a). `Bd.mot(id)` của plan 2a đọc bằng `bd list` (dạng đã spike) rồi lọc theo id — chậm hơn nhưng an toàn; tối ưu sang `bd show` khi có spike.
4. **`bi_chan_boi` đã có** trong `luat_cung.py` → suy cột dùng lại, không viết hàm thứ hai.
5. `BanGiao.pr` của plan 1a nhận cả `http://`; dashboard chỉ hiện link khi `https://` (thêm lỗi hiển thị "pr không phải URL https"), không đổi schema.
6. Nhánh: plan 1a đã merge vào `main` → worktree 2a tạo thẳng từ `main`.
7. Tên hàm plan 1a dùng trong test 2a: `YeuCauChamLai.nhan_su_kien_nguon` (không phải `nhan_thu_lai` như bản nháp đầu của plan 1a).
8. **Decision mở** (không phải escalation) đã được 1a đưa vào cột 2 (`la_decision_mo`). Nút Trả lời của 2a (Task 15, Q4) đóng chính decision bằng `bd close --reason`; 1a tự tạo yêu cầu chấm lại bead phụ thuộc qua ảnh decision (G5 plan 1a) — **không** thêm mã 1a.

## Câu hỏi / giả định

Chỗ spec mơ hồ — chọn phương án an toàn nhất, không bịa hợp đồng mới. **Đại ca đã chốt 13/10** (sau review Fable của bản 850646a): G3 (thêm Trả lời decision mở — Q4), G5, G7, G9 (đồng ý — Q5), G11 (gửi lại — Q3), G13 (thêm `@vitejs/plugin-vue`, CSP chặt — C1), G17 (làm ngay — Q1); spec phần 2 đã ghi ở bd58255 và 3c4940b. G21–G24 là giả định mới của lần sửa này — Đại ca gạch nếu không đồng ý.

| # | Chỗ mơ hồ | Chọn | Vì sao |
|---|---|---|---|
| G1 | §3 "bộ đệm … tối đa 30 giây một lần" | Tuổi tối đa 30 giây: đọc lại khi bản đệm cũ hơn 30 s, **hoặc** bị đánh dấu cũ (sự kiện `quet.xong`, `quet.loi`, sự kiện ghi của dashboard, sau mọi `POST` ghi) | Đọc thành "chỉ làm mới mỗi 30 s" sẽ làm thao tác ghi xong mà bảng chưa đổi, trái D2/D3. Thao tác ghi luôn đọc bead tươi để kiểm version. |
| G2 | Kéo cột cho bead nào | Chỉ bead có nhãn `cot:ai-lam`/`cot:can-chot` (vị trí đến từ nhãn), không epic, không `cot:cho-review`, không nhãn luồng (`can-spec`, `cho-duyet-spec`, `theo-plan`), không `tram:escalation`, trạng thái mở. Không kéo từ hàng "chưa chấm" | Spec chỉ nói "giữa cột 1 và cột 2"; bead luồng feature không được mang `cot:*` (kiến trúc §3). Giao diện có thêm nút "Chuyển sang cột 1/2" trong ngăn bên cho điện thoại (kéo-thả HTML5 không chạy trên cảm ứng). |
| G3 | Chốt cho bead nào; khớp câu trả lời với câu hỏi nào; decision mở | Chốt: chỉ bead có nhãn `cot:can-chot`, không epic/decision/escalation/luồng feature. Câu hỏi = `cau_hoi` của sự kiện `cham_cot.ket_qua` gần nhất **không bị huỷ**; cần đủ một câu trả lời không rỗng cho mỗi câu; không có câu hỏi → một câu "Chốt chung cho bead". ADR (`ADR-\d{4}`) thay cho **toàn bộ** câu trả lời, không trộn. **Decision mở** (kể cả không phải escalation): nút **Trả lời** dùng chung luồng escalation — `bd close <decision> --reason`, sự kiện `escalation.tra_loi {escalation_id = id decision}`; nút ở ngăn bên (thẻ cột 2) và trang Phê duyệt | API spec là `{tra_loi[] \| adr}` (loại trừ nhau). **Đại ca chọn 13/10** thêm nút Trả lời decision mở; spec §5.2, §7, §12.2 đã ghi (3c4940b) — không tạo `decision.tra_loi`. |
| G4 | Duyệt / Trả về **spec** ở 2a | Nút có (spec "nút có từ 2a"), server trả **501** "nối ở phần 4b", không ghi gì | Phần xử lý (commit, digest, tạo bead từ plan) thuộc 4b; làm nửa vời ở 2a nguy hiểm hơn là từ chối rõ. |
| G5 | Duyệt cột 3 có sự kiện không | Không thêm sự kiện mới (bảng sự kiện 2a không có); thao tác nằm trong bảng `thao_tac`; `close_reason` ghi rõ "Đại ca xác nhận đã merge PR … — thao tác tay trên dashboard, không phải bằng chứng máy" khi có `pr`; dashboard và Telegram thấy bead đóng ở lượt quét kế | Không bịa loại sự kiện; phần 4 phát `bead.dong` ở vòng tick. **Đại ca đồng ý 13/10** (spec §12.2 đã ghi). |
| G6 | `expected_version` cho estop / tiếp tục | Nhận và lưu, **không** kiểm | Dừng khẩn cấp không được hỏng vì màn hình cũ; thao tác vẫn idempotent theo `ma_thao_tac`. |
| G7 | Chống ghi trùng sự kiện khi crash giữa "ghi sự kiện" và "đánh dấu bước xong" | Mọi sự kiện dashboard ghi có trường `ma_thao_tac`; trước khi ghi, tìm sự kiện cùng loại + bead + `ma_thao_tac`. Bảng sự kiện đã có `ma_thao_tac` cho `cot.da_chot`, `cot.tra_ve`, `cham_cot.thu_lai`, `escalation.tra_loi`; **thêm** trường tuỳ chọn `ma_thao_tac` vào `cot.dai_ca_sua` (nguồn dashboard) và `estop.bat/tat` (nguồn dashboard) | Trường phụ, người đọc cũ bỏ qua; CLI vẫn ghi `estop.bat {ly_do}` như cũ. **Đại ca đồng ý 13/10** (spec §12.2: `ma_thao_tac?`). |
| G8 | Giờ yên lặng | Trong giờ yên lặng chỉ gửi loại "trạm lỗi"; loại khác **bỏ** (không hoãn) — Phê duyệt trên dashboard vẫn có | Câu chữ spec "chỉ gửi loại trạm lỗi"; hoãn rồi xả lúc 07:00 là hợp đồng mới. |
| G9 | D5 "≤ 2 phút" vs "gom trong cửa sổ 5 phút" | Tin **đầu tiên** của một loại gửi ngay và mở cửa sổ 5 phút; tin cùng loại trong cửa sổ được gom, gửi một tin lúc cửa sổ hết hạn; không gửi lại cùng (loại, dự án, bead) trong 1 giờ | Thoả cả hai: độ trễ ≤ 1 nhịp (15 s) cho tin đầu, ≤ 1 tin / 5 phút / loại; tin sau có thể trễ tới 5 phút. **Đại ca đồng ý 13/10** (spec §6 đã ghi). |
| G10 | "trạm lỗi (quét thất bại 3 lần liền, `bd` lỗi)" | Tin `tram_loi` khi số `quet.loi` sau `quet.xong` gần nhất của dự án ≥ 3; và mỗi `cham_cot.bo_qua` (bead đã lỗi 3 lần) | `quet.loi` chính là "`bd list` lỗi"; ngưỡng 3 theo câu chữ spec. |
| G11 | Telegram gửi lỗi | **Gửi lại**: in lỗi (đã che token) ra stderr rồi `BoChongOn.tra_lai(tg)` — xoá dấu "đã gửi" của các tin đó (không tính luật 1 giờ), đưa lên đầu hàng chờ, coi cửa sổ của loại đã hết hạn → `den_han` của vòng sau (15 s) gửi lại. Mốc `sau_id` và ảnh beads vẫn tiến vì tin đã nằm trong `chong-on.json`; `mot_vong` xả hàng chờ (`den_han`) **trước** tin mới (`nhan`) | **Đại ca chọn 13/10** (spec §6 "Gửi lỗi"). Vòng lặp không kẹt: mỗi vòng thử một lần, lỗi thì chờ vòng sau. |
| G12 | Bead nào hiện trên bảng | `status ∈ {open, in_progress, blocked}`; `closed`/`deferred` không hiện | Khớp tập trạng thái bộ chấm 1a. |
| G13 | Vite cần `@vitejs/plugin-vue` để dịch file `.vue` | **Thêm** `@vitejs/plugin-vue` (devDependency, ghim chính xác). 12 component là `.vue` (`<script setup>` + `<template>`); `api.js`, `luat.js`, `kho.js`, `tuyen.js`, `main.js` giữ `.js`. Không alias `vue` → bản esm-bundler: dùng bản chỉ-runtime (không `new Function`) → CSP chặt ở Task 10/12 | **Đại ca chọn 13/10**; spec §8 (bd58255), §4 mục 6 (3c4940b). Đã kiểm trên bản sao: bundle không có `new Function`, trang chạy dưới CSP không vi phạm (Tự review mục 4). |
| G14 | Không có `vitest` | Logic thuần (`luat.js`, `api.js`) test bằng `node --test` (thư viện chuẩn Node) + script cấm chèn HTML thô + `vite build` phải xanh (plugin-vue dịch mọi template lúc build — lỗi template làm build đỏ, đã thử; bỏ `kiem-template.mjs` của bản trước); giao diện kiểm tay ở Task 26 | §8 không có vitest. |
| G15 | Thứ tự "theo độ gấp" của Phê duyệt | escalation → decision mở → cờ đỏ → hệ cần xem → chờ review → spec; trong một loại: `priority` tăng dần (thiếu = 9), rồi `updated_at` cũ trước | Việc chặn thợ và rủi ro trước, việc đóng sau. |
| G16 | Sao lưu "bằng `sqlite3 .backup`" | Dùng `sqlite3.Connection.backup()` của thư viện chuẩn (cùng API online backup mà lệnh `.backup` gọi); giữ 14 bản; launchd chạy hằng ngày 03:15 | Không phụ thuộc có CLI `sqlite3` trong PATH của launchd. |
| G17 | Kiểm `Host` (chống DNS rebinding cho các `GET`) | **Làm ngay** cùng middleware CSP (Task 10, nối ở Task 12): `Host` (không phân biệt hoa thường) ∉ {`127.0.0.1:<cổng>`, `localhost:<cổng>`, `<ten_may_b>`, `<ten_may_b>:443`} → 421 `{"loi": "Host không hợp lệ"}`; `ten_may_b` từ `cau-hinh.yaml`. Task 26 bước 7.4 xác nhận Host thật mà `tailscale serve` gửi (chờ #5) — khác thì bổ sung `host_hop_le` | Điều phối chọn làm ngay 13/10 (review Fable Q1); spec §4 mục 6 (3c4940b). Rủi ro còn lại: nếu `tailscale serve` gửi Host khác danh sách thì dashboard qua tailnet bị 421 cho tới khi sửa — lỗi lộ rõ, không âm thầm. |
| G18 | Câu hỏi của Chốt lấy ở server | Server dùng `cau_hoi` gần nhất, trình duyệt không gửi lại câu hỏi | API spec chỉ có `{tra_loi[] \| adr}`. Rủi ro nhỏ: lần chấm lại ở chế độ thử đổi câu hỏi mà không đổi `updated_at` — số câu khác thì bị 422, Đại ca tải lại. |
| G19 | `ma_thao_tac` trong mô tả decision | Dòng cuối mô tả: `<!-- tram:ma_thao_tac=<ma> -->`; đối soát crash bằng cách tìm decision có dòng này trong `bd list --all` | Spec §12.3 "tìm decision có dấu `ma_thao_tac` trong mô tả". |
| G20 | Phiên bản gói chính xác | Lệnh ghim giữ nguyên (`uv add` rồi ghim `==`; `npm install --save-exact`). **Số đã giải trên bản sao 13/10:** `fastapi==0.143.0` (kéo theo starlette 1.7.0, annotated-doc 0.0.5, opentelemetry-api 1.45.1), `uvicorn==0.54.0` (click 8.5.0, h11 0.16.0); `vue@3.5.43`, `vue-router@5.4.0`, `vite@8.3.4`, `@vitejs/plugin-vue@6.0.10` (49 gói trong `node_modules`, `npm audit` 0 lỗ hổng). Lúc thực thi giải ra số khác → chạy lại toàn bộ test + build, ghi số thật vào commit Task 1 / Task 23 | Cả 408 test Python và `vite build` đã chạy trên đúng các số này. FastAPI 0.143 đổi nội bộ: `app.routes` trả `_IncludedRouter` không có `.path` — test kiểm hành vi (gọi route), không soi `app.routes`. |
| G21 | Decision mở trên trang Phê duyệt | Loại mục riêng `decision` ("Decision mở chờ trả lời") đặt ngay sau `escalation`; bead có `tram:escalation` chỉ là mục `escalation`. Thẻ `The` thêm `tra_loi_duoc` (decision đang hiện trên bảng) để ngăn bên hiện nút Trả lời | Spec §5.2 gộp một hàng "Bí / escalation, decision mở"; tách loại để nhãn nút rõ ("đóng escalation" / "đóng decision"), cùng route `/tra-loi`, cùng sự kiện. |
| G22 | Danh sách `Host` khi chạy cổng khác | `host_hop_le(cau_hinh, cong)` dùng cổng thật của `tram api --cong N` (`tao_app(pt, cong=N)`) | Chạy thử cục bộ ở cổng khác không bị 421 oan. |
| G23 | Link PR | Server giữ luật `https://…` (Task 7); trình duyệt chỉ hiện link khi `https://github.com/…` (N1); khác → "Chưa có link PR GitHub" | Đại ca chỉ merge trên GitHub (Q7); link lạ trong notes là dấu hiệu sai. |
| G24 | Kết nối SQLite mỗi yêu cầu | `KhoSuKien.close()`, `KhoThaoTac.close()`; mọi route mở kho bằng `contextlib.closing` (N5) — luồng SSE đóng khi trình duyệt ngắt | Không để kết nối treo tới lúc GC; giữ cách "mở theo yêu cầu" đơn giản (không pool). |

## File Structure

```
pyproject.toml, uv.lock          # (sửa) fastapi, uvicorn ghim ==                         — Task 1
tram/
  api/__init__.py                # (mới, rỗng)                                              — Task 1
  api/bao_mat.py                 # danh tính Tailscale + CSRF; CSP + header an toàn, Host 421 — Task 10
  api/bo_dem.py                  # BoDemBeads: đệm beads theo dự án                        — Task 11
  api/phu_thuoc.py               # PhuThuocApi, kiem_du_an_bead, phu_thuoc_that            — Task 12
  api/app.py                     # tao_app: middleware an toàn, router, lỗi → HTTP, file tĩnh — Task 12 (17, 18 thêm router)
  api/tuyen_doc.py               # GET du-an, cong-viec, bead, phe-duyet, chu/trang-thai    — Task 12
  api/than.py                    # pydantic: thân POST                                      — Task 17
  api/tuyen_ghi.py               # POST bead/... và phe-duyet/...                           — Task 17
  api/tuyen_chu.py               # POST chu/estop, chu/tiep-tuc                             — Task 17
  api/luong.py                   # GET /api/luong (SSE)                                      — Task 18
  suy/__init__.py                # (mới, rỗng)                                              — Task 1
  suy/lam_sach.py                # lọc ký tự điều khiển/bidi, cắt độ dài                    — Task 8
  suy/cot.py                     # ViTri, suy_vi_tri, the_bead, luật kéo / chốt / trả lời    — Task 8
  suy/chi_tiet.py                # chi_tiet_bead, ban_giao_sach                              — Task 9
  suy/phe_duyet.py               # gom_phe_duyet                                             — Task 9
  suy/trang_thai.py              # trang_thai_du_an, trang_thai_tram                         — Task 9
  thao_tac/__init__.py           # (mới, rỗng)                                              — Task 1
  thao_tac/loi.py                # XungDot 409, KhongHopLe 422, ChuaHoTro 501, KhongThay 404 — Task 4
  thao_tac/kho.py                # KhoThaoTac: bảng thao_tac, close()                        — Task 4
  thao_tac/chay.py               # chay_thao_tac: khoá bead, digest, version, làm tiếp      — Task 4
  thao_tac/chung.py              # NguCanhGhi, kiem_version, ghi_su_kien_mot_lan            — Task 4
  thao_tac/cot.py                # keo_cot, thu_lai                                          — Task 13
  thao_tac/chot.py               # chot (decision + đối soát)                                — Task 14
  thao_tac/phe_duyet.py          # duyet, tra_ve, tra_loi_decision (escalation / decision mở) — Task 15
  thao_tac/estop.py              # bat_estop_thao_tac, tiep_tuc_thao_tac                     — Task 16
  bao_tin/__init__.py            # (mới, rỗng)                                              — Task 1
  bao_tin/tin.py                 # Tin, soan_tin                                             — Task 19
  bao_tin/chong_on.py            # BoChongOn: gom 5 phút, 1 giờ, giờ yên lặng, tra_lai       — Task 19
  bao_tin/nguon.py               # tin từ ảnh beads và từ sự kiện                           — Task 20
  bao_tin/telegram.py            # gui_telegram (urllib), doc_token                          — Task 21
  bao_tin/luu.py                 # doc_json / ghi_json nguyên tử                              — Task 21
  bao_tin/vong.py                # mot_vong, chay_mai, tao_ngu_canh_that                     — Task 21
  cau_hinh/tram.py               # CauHinhTram (~/.tram/cau-hinh.yaml)                       — Task 5
  ban_giao/doc.py                # doc_khoi_ban_giao_co_loi, tom_tat_ban_giao                 — Task 7
  beads/bd.py                    # (sửa) KhongThayBead (Task 1); mot, tao, dong, them_phu_thuoc — Task 6
  su_kien/ket_noi.py             # mo_ket_noi: WAL + busy timeout                            — Task 2
  su_kien/kho.py                 # (sửa) token qua SuKien, sau_id, id_moi_nhat, cua_bead, close — Task 2
  su_kien/sao_luu.py             # sao_luu (online backup, giữ N bản)                        — Task 3
  chu/dieu_khien.py              # bat_estop / tat_estop dùng chung CLI + dashboard           — Task 16
  chu/launchd.py, chu/cai_dat.py # (sửa) plist api, bao-tin, sao-luu; cảnh báo; Q15          — Task 22
  cli.py                         # (sửa) estop dùng dieu_khien (16); đăng ký lệnh mới (22)
  cli_dich_vu.py                 # tram api · tram bao-tin · tram chu sao-luu                 — Task 22
frontend/
  package.json, package-lock.json, vite.config.js (plugin-vue), index.html, kiem-an-toan.mjs — Task 23
  src/main.js, src/tuyen.js, src/kho.js, src/api.js, src/luat.js, src/kieu.css,
  src/KhungChinh.vue, src/thanh/ThanhTrangThai.vue, src/trang/DuAn.vue                      — Task 23
  src/trang/CongViec.vue, src/trang/NganBen.vue, src/thanh/TheBead.vue, src/thanh/HopViSao.vue,
  src/thanh/OChot.vue, src/thanh/OTraLoi.vue, src/thanh/DongThoiGian.vue, src/tuyen.js (sửa) — Task 24
  src/trang/PheDuyet.vue, src/thanh/MucPheDuyet.vue, src/tuyen.js (sửa)                    — Task 25
  tests/luat.test.mjs                                                                      — Task 23
.gitignore                       # (sửa) frontend/node_modules/, frontend/dist/              — Task 23
tests/
  asgi_gia.py, bead_gia.py, bd_gia.py (công cụ test)                                      — Task 1
  api_gia.py (công cụ test)                                                                — Task 12
  test_ho_tro_gia.py (1) · test_su_kien_2a.py (2) · test_sao_luu.py (3) · test_thao_tac_khung.py (4)
  test_cau_hinh_tram.py (5) · test_bd_ghi.py (6) · test_doc_ban_giao.py (7) · test_suy_cot.py (8)
  test_suy_phe_duyet.py (9) · test_bao_mat.py (10) · test_bo_dem.py (11) · test_api_doc.py (12)
  test_keo_cot.py (13) · test_chot.py (14) · test_thao_tac_phe_duyet.py (15) · test_estop_2a.py (16)
  test_api_ghi.py (17) · test_luong.py (18) · test_chong_on.py (19) · test_nguon_tin.py (20)
  test_bao_tin.py (21) · test_cli_dich_vu.py (22)
```

Công cụ test (`asgi_gia.py`, `bd_gia.py`, …) là module cấp cao trong `tests/` (pytest chế độ `prepend` đưa `tests/` vào `sys.path`), import bằng `from bd_gia import BdGia`.

## Hợp đồng JSON của tram-api (lát 2a)

Backend (Task 12, 17, 18) và frontend (Task 23–25) cùng theo bảng này — frontend làm song song được nhờ hợp đồng cố định.

**Thẻ bead `The`:** `{du_an, id, tieu_de, loai, uu_tien: int|null, hang, mo: bool, cho: [id], khoa: bool, co_do: bool, lech: bool, khe_spec: bool, keo_duoc: bool, chot_duoc: bool, tra_loi_duoc: bool, updated_at}` (`tra_loi_duoc` = bead `decision` đang hiện trên bảng — escalation hoặc decision mở, G21) với `hang ∈ {"ai-lam","can-chot","cho-review","chua-cham","epic","theo-plan"}`.

| Phương thức + đường dẫn | Thân yêu cầu | Trả về 200 |
|---|---|---|
| `GET /api/du-an` | — | `{du_an: [{ten, quet_cuoi: luc\|null, loi_gan_nhat: {luc, loai, loi, bead_id}\|null, so_bead: {<hang>: n}, loi_doc: str\|null}]}` |
| `GET /api/cong-viec?du_an=<ten>` (rỗng = tất cả) | — | `{the: [The], loi: {du_an: thông báo}}` |
| `GET /api/bead/{du_an}/{id}` | — | `{the: The, mo_ta, nghiem_thu, cham_gan_nhat: {luc, cot, ly_do, cau_hoi: []}\|null, ban_giao: {pr, nhanh, commit, file_ban_giao, loi: []}\|null, dong_thoi_gian: [{id, luc, loai, tac_nhan, tom_tat}]}` |
| `GET /api/phe-duyet` | — | `{muc: [{loai ∈ escalation\|decision\|co-do\|he\|cho-review\|spec, du_an, bead_id\|null, tieu_de, uu_tien, updated_at\|null, chi_tiet}], so: n, loi: {}}`; `chi_tiet` của `cho-review`/`co-do` = khối `ban_giao` ở trên; của `he` = `{su_kien, luc, loi}` |
| `GET /api/chu/trang-thai` | — | `{estop: bool, du_an: [{ten, quet_cuoi, loi_gan_nhat}], la_dai_ca: bool}` |
| `POST /api/bead/{du_an}/{id}/cot` | `{cot: "ai-lam"\|"can-chot", vi_sao?: str, ma_thao_tac, expected_version}` | `{ket_qua: {...}, lap_lai: bool}` |
| `POST /api/bead/{du_an}/{id}/chot` | `{tra_loi?: [str], adr?: "ADR-0000", ma_thao_tac, expected_version}` | `{ket_qua: {tao_decision: id, ...}, lap_lai}` |
| `POST /api/bead/{du_an}/{id}/thu-lai` | `{ma_thao_tac, expected_version}` | như trên |
| `POST /api/phe-duyet/{du_an}/{id}/duyet` | `{expected_commit?, digest_bead?, ma_thao_tac, expected_version}` | như trên; bead `cho-duyet-spec` → 501 |
| `POST /api/phe-duyet/{du_an}/{id}/tra-ve` | `{gop_y, ma_thao_tac, expected_version}` | như trên; spec → 501 |
| `POST /api/phe-duyet/{du_an}/{id}/tra-loi` | `{tra_loi, ma_thao_tac, expected_version}` | như trên; escalation **hoặc decision mở** — đóng chính decision, sự kiện `escalation.tra_loi {escalation_id = id decision}` (spec §12.2) |
| `POST /api/chu/estop` · `POST /api/chu/tiep-tuc` | `{ly_do?, ma_thao_tac, expected_version}` (version = `"bat"`/`"tat"` đang thấy, không kiểm — G6) | như trên |
| `GET /api/luong` | — | SSE: `event: su_kien` (`id:` = id sự kiện, `data: {id, luc, du_an, bead_id, loai}`), `event: cong_viec_doi` (`{du_an}`), `event: phe_duyet_doi` (`{}`), chú thích `: nhip` mỗi ~16 s; nhận `Last-Event-ID` |

Mọi phản hồi (kể cả lỗi, file tĩnh, SSE) mang `Content-Security-Policy` (chuỗi đúng spec §4 mục 6), `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer`, `X-Frame-Options: DENY`, không có header `server`. Lỗi: `{"loi": "<thông báo>"}` với 421 (`Host` ngoài danh sách — G17), 404 (dự án/bead không có), 409 (bead đã đổi so với `expected_version`, hoặc cùng `ma_thao_tac` khác nội dung), 422 (sai luật; lỗi kiểm thân của FastAPI trả `{"detail": [...]}`), 501 (Duyệt/Trả về spec), 502 (`bd` lỗi); 403 `{"detail": "<lý do>"}` khi thiếu danh tính / CSRF.

## Chuẩn bị (người thực thi, một lần)

```bash
cd "/Users/dai-ca/Developer/Ben Station"
git status --short                   # chỉ được có .beads/interactions.jsonl, .DS_Store — không đụng
git log --oneline main | grep -q d63c41c   # plan 1a đã merge vào main
git worktree add .worktrees/lat-2a-dashboard -b feat/lat-2a-dashboard main
cd .worktrees/lat-2a-dashboard
uv sync
uv run pytest -q                     # kỳ vọng: 239 passed (sau plan 1a)
```

Chạy song song trong cùng worktree: mỗi task chỉ sửa đúng file của mình, chạy file test của mình ở bước kiểm; người điều phối commit lần lượt. Chạy `uv run pytest -q` đầy đủ ở cuối mỗi đợt (xem "Sơ đồ đợt chạy").

---

### Task 1: Phụ thuộc FastAPI/uvicorn + khung gói + công cụ test

**Độ khó:** `de` · **Song song:** đợt 1 — chạy cùng Task 2, 3, 5, 7, 19, 23 (không chung file). Phải xong trước Task 6 (cùng sửa `tram/beads/bd.py`), 8, 10, 11, 12 và mọi task dùng `bead_gia`/`bd_gia`/`asgi_gia`.

**Files:**
- Modify: `pyproject.toml`, `uv.lock` (qua `uv add`); `tram/beads/bd.py` (chỉ thêm lớp `KhongThayBead` — C2)
- Create: `tram/api/__init__.py`, `tram/suy/__init__.py`, `tram/thao_tac/__init__.py`, `tram/bao_tin/__init__.py` (rỗng)
- Create: `tests/asgi_gia.py`, `tests/bead_gia.py`, `tests/bd_gia.py`
- Test: `tests/test_ho_tro_gia.py`

**Interfaces:**
- Consumes: `Bead`, `PhuThuoc` (`tram/beads/mo_hinh.py`, bản plan 1a); `LoiBd` (`tram/beads/bd.py`).
- Produces:
  - `tram/beads/bd.py`: `class KhongThayBead(LoiBd)` — bead không có trong `bd list` (Task 6 `Bd.mot` ném; tram-api ánh xạ 404).
  - `goi(app, phuong_thuc: str, duong_dan: str, *, json_body=None, headers: dict | None = None) -> PhanHoi` với `PhanHoi(status: int, headers: dict[str, str], body: bytes)` + `.json()`.
  - `bead(id="hr-1", *, title="Việc", status="open", issue_type="task", labels=(), chan_boi=(), updated_at="2026-10-13T01:00:00Z", **them) -> Bead` (khoá `them` là khoá JSON của `bd list`, vd `priority`, `notes`, `description`, `dependencies`).
  - `notes_ban_giao(**ghi_de) -> str` — notes có một khối `<!-- ban-giao -->` hợp lệ (có `pr`).
  - `BdGia(beads=(), *, ra_loi_truoc: dict[str, int] | None = None, ra_loi_sau: dict[str, int] | None = None, tien_to="hr")` với `beads: dict[str, Bead]`, `goi: list[tuple]`, `so_lan(ten) -> int`, `tat_ca()`, `mot(id)`, `cap_nhat_nhan(id, *, them=(), bo=(), ghi_chu=None)`, `tao(tieu_de, *, loai, mo_ta, nhan=()) -> str`, `dong(id, ly_do)`, `them_phu_thuoc(id, phu_thuoc_vao)`; `mot(id)` không có → `KhongThayBead` (giống `Bd.mot` thật — C2). `ra_loi_truoc={"dong": 1}` = lần gọi `dong` thứ 1 ném `LoiBd` **trước** khi đổi gì; `ra_loi_sau={"tao": 1}` = lần thứ 1 đổi dữ liệu xong **rồi** ném `LoiBd` (giả lập crash sau khi `bd` đã ghi).

- [ ] **Step 1: Cài phụ thuộc, ghim phiên bản chính xác (cần mạng — chỉ bước này)**

```bash
uv add fastapi uvicorn
FA=$(uv run python -c "import importlib.metadata as m; print(m.version('fastapi'))")
UV=$(uv run python -c "import importlib.metadata as m; print(m.version('uvicorn'))")
uv add "fastapi==$FA" "uvicorn==$UV"
grep -n "fastapi\|uvicorn" pyproject.toml     # phải là dạng ==X.Y.Z
echo "fastapi==$FA uvicorn==$UV"               # ghi vào thông điệp commit
```

Kết quả trên bản sao 13/10 (G20): `fastapi==0.143.0 uvicorn==0.54.0`; `uv.lock` thêm `annotated-doc`, `click`, `fastapi`, `opentelemetry-api`, `starlette`, `uvicorn`. Số khác → vẫn ghim số đã giải, chạy đủ test ở bước 6.

- [ ] **Step 2: Kiểm API dùng trong plan có trên bản đã cài**

```bash
uv run python -c "
import fastapi, starlette
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
print('fastapi', fastapi.__version__, 'starlette', starlette.__version__)"
```

Expected: `fastapi 0.143.0 starlette 1.7.0` (hoặc số đã giải), không `ImportError`. Có lỗi → dừng, báo người điều phối (đọc tài liệu bản mới theo skill `source-driven-development`, không tự đoán API).

- [ ] **Step 3: Viết test thất bại**

`tests/test_ho_tro_gia.py`:

```python
import pytest
from fastapi import FastAPI, Request

from asgi_gia import goi
from bd_gia import BdGia
from bead_gia import bead, notes_ban_giao
from tram.ban_giao.schema import doc_khoi_ban_giao
from tram.beads.bd import KhongThayBead, LoiBd


def test_asgi_gia_get_post_va_header():
    app = FastAPI()

    @app.get("/a")
    def a(request: Request, q: str = ""):
        return {"q": q, "h": request.headers.get("x-thu")}

    @app.post("/b")
    async def b(request: Request):
        return {"than": await request.json()}

    r = goi(app, "GET", "/a?q=1", headers={"X-Thu": "co"})
    assert r.status == 200 and r.json() == {"q": "1", "h": "co"}
    r = goi(app, "POST", "/b", json_body={"x": "ă"})
    assert r.status == 200 and r.json() == {"than": {"x": "ă"}}
    assert goi(app, "GET", "/khong-co").status == 404


def test_bead_gia_mac_dinh_va_chan():
    b = bead("hr-9", labels=["cot:ai-lam"], chan_boi=["hr-1"], priority=1)
    assert b.id == "hr-9" and b.labels == ("cot:ai-lam",)
    assert b.phu_thuoc[0].depends_on_id == "hr-1" and b.phu_thuoc[0].loai == "blocks"
    assert b.priority == 1 and b.close_reason == ""
    assert doc_khoi_ban_giao(notes_ban_giao()).pr == "https://github.com/o/r/pull/7"


def test_bd_gia_ghi_nhan_tao_dong_noi():
    bd = BdGia([bead("hr-1", labels=["cot:ai-lam"])])
    bd.cap_nhat_nhan("hr-1", them=["cot:can-chot"], bo=["cot:ai-lam"], ghi_chu="n")
    b = bd.mot("hr-1")
    assert b.labels == ("cot:can-chot",) and b.notes == "n" and b.updated_at > "2026-10-13T01:00:00Z"
    moi = bd.tao("Chốt: x", loai="decision", mo_ta="m")
    bd.dong(moi, "đáp")
    bd.them_phu_thuoc("hr-1", moi)
    assert bd.mot(moi).status == "closed" and bd.mot(moi).close_reason == "đáp"
    assert bd.mot("hr-1").phu_thuoc[-1].depends_on_id == moi
    assert [g[0] for g in bd.goi] == ["cap_nhat_nhan", "tao", "dong", "them_phu_thuoc"]


def test_bd_gia_loi_truoc_va_sau():
    bd = BdGia([bead("hr-1")], ra_loi_truoc={"dong": 1}, ra_loi_sau={"tao": 1})
    with pytest.raises(LoiBd):
        bd.dong("hr-1", "x")
    assert bd.mot("hr-1").status == "open"
    with pytest.raises(LoiBd):
        bd.tao("t", loai="decision", mo_ta="m")
    assert bd.so_lan("tao") == 1 and len(bd.beads) == 2      # đã tạo rồi mới lỗi
    bd.dong("hr-1", "x")
    assert bd.mot("hr-1").status == "closed"
    with pytest.raises(KhongThayBead):
        bd.mot("hr-99")
```

- [ ] **Step 4: Chạy, thấy fail**

Run: `uv run pytest tests/test_ho_tro_gia.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'asgi_gia'`.

- [ ] **Step 5: Viết mã**

Bốn file `__init__.py` rỗng:

```bash
touch tram/api/__init__.py tram/suy/__init__.py tram/thao_tac/__init__.py tram/bao_tin/__init__.py
```

`tram/beads/bd.py` — thêm ngay dưới `class LoiBd` (không sửa gì khác; Task 6 thêm các phương thức đọc/ghi):

```python
class KhongThayBead(LoiBd):
    """Bead không có trong `bd list` của dự án."""
```

`tests/asgi_gia.py`:

```python
"""Gọi một ứng dụng ASGI trong bộ nhớ — thay TestClient để khỏi thêm httpx (spec §8)."""
import asyncio
import json as _json
from dataclasses import dataclass


@dataclass
class PhanHoi:
    status: int
    headers: dict[str, str]
    body: bytes

    def json(self):
        return _json.loads(self.body)


def goi(app, phuong_thuc: str, duong_dan: str, *, json_body=None, headers: dict | None = None) -> PhanHoi:
    path, _, query = duong_dan.partition("?")
    body = b"" if json_body is None else _json.dumps(json_body, ensure_ascii=False).encode()
    hdr = {"host": "127.0.0.1:7700"}
    if json_body is not None:
        hdr["content-type"] = "application/json"
    hdr.update({k.lower(): v for k, v in (headers or {}).items()})
    scope = {
        "type": "http", "asgi": {"version": "3.0"}, "http_version": "1.1",
        "method": phuong_thuc, "scheme": "http", "path": path, "raw_path": path.encode(),
        "query_string": query.encode(), "root_path": "",
        "headers": [(k.encode("latin-1"), v.encode("latin-1")) for k, v in hdr.items()],
        "client": ("127.0.0.1", 50000), "server": ("127.0.0.1", 7700),
    }
    nhan = [{"type": "http.request", "body": body, "more_body": False}]
    gui: list[dict] = []

    async def receive():
        return nhan.pop(0) if nhan else {"type": "http.disconnect"}

    async def send(m):
        gui.append(m)

    asyncio.run(app(scope, receive, send))
    dau = next(m for m in gui if m["type"] == "http.response.start")
    return PhanHoi(dau["status"], {k.decode(): v.decode() for k, v in dau["headers"]},
                   b"".join(m.get("body", b"") for m in gui if m["type"] == "http.response.body"))
```

`tests/bead_gia.py`:

```python
"""Dựng Bead/notes mẫu cho test lát 2a qua Bead.tu_json (không phụ thuộc thứ tự trường)."""
import json

from tram.beads.mo_hinh import Bead

KHOI_BAN_GIAO = {
    "phien_ban": 1, "loai": "chinh-thuc", "luot": 1, "file_ban_giao": "docs/handovers/x.md",
    "nhanh": "fix/x", "commit": "abc1234", "pr": "https://github.com/o/r/pull/7",
    "doi_chieu_nghiem_thu": [], "lenh_kiem": [], "quyet_dinh": [], "huong_da_bo": [],
    "vuong_mac": [], "buoc_tiep": [], "cau_hoi_mo": [], "thay_doi_vung_nhay_cam": [],
}


def bead(id="hr-1", *, title="Việc", status="open", issue_type="task", labels=(), chan_boi=(),
         updated_at="2026-10-13T01:00:00Z", **them) -> Bead:
    d = {"id": id, "title": title, "status": status, "issue_type": issue_type, "labels": list(labels),
         "updated_at": updated_at,
         "dependencies": [{"issue_id": id, "depends_on_id": x, "type": "blocks"} for x in chan_boi]}
    return Bead.tu_json({**d, **them})


def notes_ban_giao(**ghi_de) -> str:
    return f"ghi chú\n<!-- ban-giao -->\n{json.dumps({**KHOI_BAN_GIAO, **ghi_de})}\n<!-- ban-giao -->"
```

`tests/bd_gia.py`:

```python
"""Bd giả lập trong bộ nhớ cho test lát 2a — không chạy `bd` thật."""
from collections import Counter
from dataclasses import replace
from datetime import datetime, timedelta, timezone

from tram.beads.bd import KhongThayBead, LoiBd
from tram.beads.mo_hinh import Bead, PhuThuoc

GOC = datetime(2026, 10, 13, 2, 0, tzinfo=timezone.utc)


class BdGia:
    def __init__(self, beads=(), *, ra_loi_truoc=None, ra_loi_sau=None, tien_to="hr"):
        self.beads: dict[str, Bead] = {b.id: b for b in beads}
        self.goi: list[tuple] = []
        self._truoc, self._sau = dict(ra_loi_truoc or {}), dict(ra_loi_sau or {})
        self._dem: Counter = Counter()
        self._nhip = 0
        self._tien_to = tien_to

    def _bat_dau(self, ten: str) -> None:
        self._dem[ten] += 1
        if self._truoc.get(ten) == self._dem[ten]:
            raise LoiBd(f"giả lập lỗi trước khi {ten}")

    def _ket_thuc(self, ten: str, *args) -> None:
        self.goi.append((ten, *args))
        if self._sau.get(ten) == self._dem[ten]:
            raise LoiBd(f"giả lập lỗi sau khi {ten}")

    def _luc_moi(self) -> str:
        self._nhip += 1
        return (GOC + timedelta(seconds=self._nhip)).strftime("%Y-%m-%dT%H:%M:%SZ")

    def so_lan(self, ten: str) -> int:
        return sum(1 for g in self.goi if g[0] == ten)

    def tat_ca(self) -> list[Bead]:
        self._bat_dau("tat_ca")
        self._ket_thuc("tat_ca")
        return list(self.beads.values())

    def mot(self, bead_id: str) -> Bead:
        if bead_id not in self.beads:
            raise KhongThayBead(f"Không thấy bead {bead_id}")   # như Bd.mot thật (Task 6) → 404
        return self.beads[bead_id]

    def cap_nhat_nhan(self, bead_id, *, them=(), bo=(), ghi_chu=None) -> None:
        self._bat_dau("cap_nhat_nhan")
        b = self.beads[bead_id]
        nhan = [n for n in b.labels if n not in bo] + [n for n in them if n not in b.labels]
        notes = b.notes
        if ghi_chu:
            notes = f"{notes}\n{ghi_chu}" if notes else ghi_chu
        self.beads[bead_id] = replace(b, labels=tuple(nhan), notes=notes, updated_at=self._luc_moi())
        self._ket_thuc("cap_nhat_nhan", bead_id, tuple(them), tuple(bo), ghi_chu)

    def tao(self, tieu_de, *, loai, mo_ta, nhan=()) -> str:
        self._bat_dau("tao")
        moi = f"{self._tien_to}-d{len(self.beads) + 1}"
        self.beads[moi] = Bead.tu_json({"id": moi, "title": tieu_de, "description": mo_ta, "issue_type": loai,
                                        "status": "open", "labels": list(nhan), "updated_at": self._luc_moi()})
        self._ket_thuc("tao", tieu_de, loai, mo_ta, tuple(nhan))
        return moi

    def dong(self, bead_id, ly_do) -> None:
        self._bat_dau("dong")
        self.beads[bead_id] = replace(self.beads[bead_id], status="closed", close_reason=ly_do,
                                      updated_at=self._luc_moi())
        self._ket_thuc("dong", bead_id, ly_do)

    def them_phu_thuoc(self, bead_id, phu_thuoc_vao) -> None:
        self._bat_dau("them_phu_thuoc")
        b = self.beads[bead_id]
        self.beads[bead_id] = replace(b, phu_thuoc=b.phu_thuoc + (PhuThuoc(phu_thuoc_vao, "blocks"),),
                                      updated_at=self._luc_moi())
        self._ket_thuc("them_phu_thuoc", bead_id, phu_thuoc_vao)
```

- [ ] **Step 6: Chạy, thấy pass**

Run: `uv run pytest tests/test_ho_tro_gia.py -q` → Expected: `4 passed`.
Run: `uv run pytest -q` → Expected: `243 passed` (239 + 4).

- [ ] **Step 7: Commit**

```bash
git add pyproject.toml uv.lock tram/beads/bd.py tram/api/__init__.py tram/suy/__init__.py tram/thao_tac/__init__.py \
  tram/bao_tin/__init__.py tests/asgi_gia.py tests/bead_gia.py tests/bd_gia.py tests/test_ho_tro_gia.py
git commit -m "build: thêm fastapi==$FA, uvicorn==$UV; khung gói 2a, KhongThayBead, công cụ test (ASGI, bd giả)"
```

---

### Task 2: Kho sự kiện 2a — WAL + timeout, cột token qua `SuKien`, `sau_id`, `id_moi_nhat`, `cua_bead`

**Độ khó:** `de` · **Song song:** đợt 1 — chạy cùng Task 1, 3, 5, 7, 19, 23. Phải xong trước Task 4, 9, 12, 18, 20, 21.

**Files:**
- Create: `tram/su_kien/ket_noi.py`
- Modify: `tram/su_kien/kho.py` (thay cả file — bản trên `main` sau plan 1a, 112 dòng)
- Test: `tests/test_su_kien_2a.py`

**Interfaces:**
- Consumes: `tram/su_kien/kho.py` bản plan 1a (`SuKien(..., id: int = 0)`, `_CHON`, `_CAT_CHUOI_LOI`, `self.yeu_cau = YeuCauChamLai(self._db)`, `dem_loi_lien_tiep` bỏ qua `ket_qua{huy}`) — giữ nguyên hành vi; `YeuCauChamLai.nhan_su_kien_nguon` (`tram/su_kien/yeu_cau.py`, không sửa).
- Produces:
  - `tram/su_kien/ket_noi.py`: `THOI_GIAN_CHO_GIAY = 10`; `LUOC_DO` (chuyển nguyên văn từ `kho.py` để `kho.py` ≤ 120 dòng); `mo_ket_noi(duong_dan: Path) -> sqlite3.Connection` — `busy_timeout = 10000`, `journal_mode=WAL` (thử lại tối đa 10 s khi hai tiến trình cùng mở DB mới), `check_same_thread=False`.
  - `SuKien(luc, du_an, bead_id, loai, tac_nhan, du_lieu, id: int = 0, token_vao: int | None = None, token_ra: int | None = None, mo_hinh: str | None = None, thoi_gian_ms: int | None = None)`.
  - `KhoSuKien.sau_id(id: int, gioi_han: int) -> list[SuKien]` (id tăng dần, `id > ?`); `KhoSuKien.id_moi_nhat() -> int` (0 khi rỗng); `KhoSuKien.cua_bead(du_an, bead_id, gioi_han=200) -> list[SuKien]` (N sự kiện mới nhất của bead, xếp cũ → mới); `KhoSuKien.close() -> None` (tram-api đóng bằng `contextlib.closing` — N5).

- [ ] **Step 0: Đối chiếu `tram/su_kien/kho.py` hiện tại**

`git log --oneline -1 -- tram/su_kien/kho.py` phải là commit của plan 1a (Task 5/10). Bản mới ở bước 3 = bản đó + đúng các thay đổi: bỏ `import sqlite3`; `LUOC_DO` chuyển sang `ket_noi.py`; `_CHON` thêm 4 cột; `SuKien` thêm 4 trường sau `id`; `sqlite3.connect` → `mo_ket_noi`; `_doc` dựng thêm `*h[6:11]`; thêm `sau_id`, `id_moi_nhat`, `cua_bead`, `close`. Nếu file trên nhánh khác bản plan 1a ở chỗ khác → dừng, báo người điều phối.

- [ ] **Step 1: Viết test thất bại**

`tests/test_su_kien_2a.py`:

```python
import sqlite3

import pytest

from tram.su_kien.ket_noi import THOI_GIAN_CHO_GIAY, mo_ket_noi
from tram.su_kien.kho import KhoSuKien


def test_ket_noi_wal_va_timeout(tmp_path):
    db = mo_ket_noi(tmp_path / "sk.db")
    assert db.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
    assert db.execute("PRAGMA busy_timeout").fetchone()[0] == THOI_GIAN_CHO_GIAY * 1000


def test_doc_dang_mo_khong_chan_ghi(tmp_path):
    p = tmp_path / "sk.db"
    KhoSuKien(p).ghi("hr", "x", {})
    doc = mo_ket_noi(p)
    doc.execute("BEGIN")
    assert doc.execute("SELECT COUNT(*) FROM su_kien").fetchone()[0] == 1
    KhoSuKien(p).ghi("hr", "y", {})          # WAL: giao dịch đọc không khoá người ghi
    doc.execute("COMMIT")
    assert doc.execute("SELECT COUNT(*) FROM su_kien").fetchone()[0] == 2


def test_su_kien_giu_cot_token_qua_mo_hinh_doc(tmp_path):
    k = KhoSuKien(tmp_path / "sk.db")
    k.ghi("hr", "cham_cot.ket_qua", {"cot": "ai-lam"}, bead_id="hr-1",
          token_vao=10, token_ra=5, mo_hinh="m", thoi_gian_ms=7)
    s = k.moi_nhat("hr", "hr-1", "cham_cot.ket_qua")
    assert (s.id, s.token_vao, s.token_ra, s.mo_hinh, s.thoi_gian_ms) == (1, 10, 5, "m", 7)
    assert k.gan_day("hr", "cham_cot.ket_qua", 1)[0].token_vao == 10


def test_sau_id_phan_trang(tmp_path):
    k = KhoSuKien(tmp_path / "sk.db")
    for i in range(5):
        k.ghi("hr", "x", {"i": i})
    t1 = k.sau_id(0, 2)
    t2 = k.sau_id(t1[-1].id, 2)
    t3 = k.sau_id(t2[-1].id, 10)
    assert [s.du_lieu["i"] for s in t1 + t2 + t3] == [0, 1, 2, 3, 4]
    assert k.sau_id(5, 10) == []


def test_id_moi_nhat(tmp_path):
    k = KhoSuKien(tmp_path / "sk.db")
    assert k.id_moi_nhat() == 0
    k.ghi("hr", "x", {})
    k.ghi("_tram", "estop.bat", {})
    assert k.id_moi_nhat() == 2


def test_cua_bead_cu_truoc_moi_sau(tmp_path):
    k = KhoSuKien(tmp_path / "sk.db")
    k.ghi("hr", "a", {}, bead_id="hr-1")
    k.ghi("hr", "b", {}, bead_id="hr-2")
    k.ghi("hr", "c", {}, bead_id="hr-1")
    k.ghi("web", "d", {}, bead_id="hr-1")
    assert [s.loai for s in k.cua_bead("hr", "hr-1")] == ["a", "c"]
    assert [s.loai for s in k.cua_bead("hr", "hr-1", gioi_han=1)] == ["c"]


def test_yeu_cau_plan_1a_van_dung_chung_ket_noi(tmp_path):
    k = KhoSuKien(tmp_path / "sk.db")
    k.ghi("hr", "cham_cot.thu_lai", {"ma_thao_tac": "m"}, bead_id="hr-1", tac_nhan="dai-ca/dashboard")
    assert k.yeu_cau.nhan_su_kien_nguon("hr") == 1


def test_close_dong_ket_noi(tmp_path):
    k = KhoSuKien(tmp_path / "sk.db")
    k.close()
    with pytest.raises(sqlite3.ProgrammingError):
        k.id_moi_nhat()
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_su_kien_2a.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'tram.su_kien.ket_noi'`.

- [ ] **Step 3: Viết mã**

`tram/su_kien/ket_noi.py`:

```python
"""Kết nối SQLite dùng chung cho mọi tiến trình trạm (quét, tram-api, tram-bao-tin) — spec 2 §12.2."""
import sqlite3
import time
from pathlib import Path

THOI_GIAN_CHO_GIAY = 10
LUOC_DO = """
CREATE TABLE IF NOT EXISTS su_kien (
  id INTEGER PRIMARY KEY,
  luc TEXT NOT NULL,
  du_an TEXT NOT NULL,
  bead_id TEXT,
  loai TEXT NOT NULL,
  tac_nhan TEXT NOT NULL,
  du_lieu TEXT NOT NULL,
  token_vao INTEGER, token_ra INTEGER,
  mo_hinh TEXT,
  thoi_gian_ms INTEGER
);
CREATE INDEX IF NOT EXISTS su_kien_bead ON su_kien(du_an, bead_id, loai, id);
CREATE TABLE IF NOT EXISTS moc_quet (du_an TEXT PRIMARY KEY, updated_at TEXT NOT NULL);
"""


def mo_ket_noi(duong_dan: Path) -> sqlite3.Connection:
    """WAL: người đọc không chặn người ghi; busy_timeout: người ghi chờ nhau thay vì lỗi ngay.
    check_same_thread=False: tram-api dùng một kết nối qua threadpool, mỗi lúc một luồng.
    Chuyển sang WAL cần khoá độc quyền — hai tiến trình cùng mở DB mới lần đầu có thể đụng nhau, nên thử lại."""
    db = sqlite3.connect(duong_dan, timeout=THOI_GIAN_CHO_GIAY, check_same_thread=False)
    db.execute(f"PRAGMA busy_timeout={THOI_GIAN_CHO_GIAY * 1000}")
    so_lan = THOI_GIAN_CHO_GIAY * 10
    for lan in range(so_lan):
        try:
            db.execute("PRAGMA journal_mode=WAL")
            break
        except sqlite3.OperationalError:
            if lan == so_lan - 1:
                raise
            time.sleep(0.1)
    return db
```

`tram/su_kien/kho.py` (cả file):

```python
import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from tram.duong_dan import bay_gio, tram_home
from tram.su_kien.ket_noi import LUOC_DO, mo_ket_noi
from tram.su_kien.yeu_cau import YeuCauChamLai

_CHON = ("SELECT luc, du_an, bead_id, loai, tac_nhan, du_lieu, id,"
         " token_vao, token_ra, mo_hinh, thoi_gian_ms FROM su_kien")
# Sự kiện cắt chuỗi lỗi liên tiếp: chấm được, hoặc Đại ca bấm "thử lại" (spec 0+1a §5.6).
_CAT_CHUOI_LOI = ("cham_cot.ket_qua", "cham_cot.thu_lai")


@dataclass(frozen=True)
class SuKien:
    luc: str
    du_an: str
    bead_id: str | None
    loai: str
    tac_nhan: str
    du_lieu: dict
    id: int = 0
    token_vao: int | None = None
    token_ra: int | None = None
    mo_hinh: str | None = None
    thoi_gian_ms: int | None = None


class KhoSuKien:
    """Bảng chỉ thêm. Trạng thái hiển thị tính lúc đọc."""

    def __init__(self, duong_dan: Path):
        self._db = mo_ket_noi(duong_dan)
        self._db.executescript(LUOC_DO)
        self.yeu_cau = YeuCauChamLai(self._db)

    def ghi(self, du_an: str, loai: str, du_lieu: dict, *, bead_id: str | None = None,
            tac_nhan: str = "tram/cham-cot", token_vao: int | None = None,
            token_ra: int | None = None, mo_hinh: str | None = None,
            thoi_gian_ms: int | None = None) -> str:
        luc = bay_gio()
        with self._db:
            self._db.execute(
                "INSERT INTO su_kien (luc, du_an, bead_id, loai, tac_nhan, du_lieu,"
                " token_vao, token_ra, mo_hinh, thoi_gian_ms) VALUES (?,?,?,?,?,?,?,?,?,?)",
                (luc, du_an, bead_id, loai, tac_nhan,
                 json.dumps(du_lieu, ensure_ascii=False, sort_keys=True),
                 token_vao, token_ra, mo_hinh, thoi_gian_ms))
        return luc

    def _doc(self, sql: str, tham_so: tuple) -> list[SuKien]:
        hang = self._db.execute(sql, tham_so).fetchall()
        return [SuKien(h[0], h[1], h[2], h[3], h[4], json.loads(h[5]), *h[6:11]) for h in hang]

    def moi_nhat(self, du_an: str, bead_id: str, loai: str, *,
                 dieu_kien: Callable[[SuKien], bool] | None = None) -> SuKien | None:
        ds = self._doc(f"{_CHON} WHERE du_an=? AND bead_id=? AND loai=? ORDER BY id DESC",
                       (du_an, bead_id, loai))
        return next((s for s in ds if dieu_kien is None or dieu_kien(s)), None)

    def moi_nhat_cac_loai(self, du_an: str, bead_id: str, loai: tuple[str, ...], *,
                          dieu_kien: Callable[[SuKien], bool] | None = None) -> SuKien | None:
        """Sự kiện ghi sau cùng (theo thứ tự ghi trong bảng) trong nhiều loại."""
        ds = self._doc(
            f"{_CHON} WHERE du_an=? AND bead_id=? AND loai IN ({','.join('?' * len(loai))}) ORDER BY id DESC",
            (du_an, bead_id, *loai))
        return next((s for s in ds if dieu_kien is None or dieu_kien(s)), None)

    def gan_day(self, du_an: str, loai: str, gioi_han: int) -> list[SuKien]:
        return self._doc(f"{_CHON} WHERE du_an=? AND loai=? ORDER BY id DESC LIMIT ?", (du_an, loai, gioi_han))

    def doc_moc(self, du_an: str) -> str | None:
        h = self._db.execute("SELECT updated_at FROM moc_quet WHERE du_an=?", (du_an,)).fetchone()
        return h[0] if h else None

    def ghi_moc(self, du_an: str, updated_at: str) -> None:
        with self._db:
            self._db.execute(
                "INSERT INTO moc_quet (du_an, updated_at) VALUES (?, ?)"
                " ON CONFLICT(du_an) DO UPDATE SET updated_at=excluded.updated_at",
                (du_an, updated_at))

    def dem_loi_lien_tiep(self, du_an: str, bead_id: str) -> int:
        dem = 0
        for s in self._doc(f"{_CHON} WHERE du_an=? AND bead_id=? AND loai IN (?, ?, ?) ORDER BY id DESC",
                           (du_an, bead_id, "cham_cot.loi", *_CAT_CHUOI_LOI)):
            if s.loai == "cham_cot.ket_qua" and s.du_lieu.get("huy"):
                continue  # kết quả bị huỷ không phải lần chấm thành công (§5.6)
            if s.loai != "cham_cot.loi":
                break
            dem += 1
        return dem

    def sau_id(self, id: int, gioi_han: int) -> list[SuKien]:
        """Sự kiện có id > `id`, tăng dần — SSE và tram-bao-tin đọc theo mốc riêng (spec 2 §6, §12.2)."""
        return self._doc(f"{_CHON} WHERE id > ? ORDER BY id LIMIT ?", (id, gioi_han))

    def id_moi_nhat(self) -> int:
        return self._db.execute("SELECT COALESCE(MAX(id), 0) FROM su_kien").fetchone()[0]

    def cua_bead(self, du_an: str, bead_id: str, gioi_han: int = 200) -> list[SuKien]:
        """Dòng thời gian của bead: `gioi_han` sự kiện mới nhất, xếp cũ → mới."""
        ds = self._doc(f"{_CHON} WHERE du_an=? AND bead_id=? ORDER BY id DESC LIMIT ?",
                       (du_an, bead_id, gioi_han))
        return ds[::-1]

    def cac_du_an(self) -> list[str]:
        return [h[0] for h in self._db.execute("SELECT DISTINCT du_an FROM su_kien ORDER BY du_an")]

    def close(self) -> None:
        """tram-api mở một kho cho mỗi yêu cầu và đóng bằng `contextlib.closing` (N5)."""
        self._db.close()


def mo_kho() -> KhoSuKien:
    return KhoSuKien(tram_home() / "su-kien.db")
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_su_kien_2a.py tests/test_su_kien.py tests/test_yeu_cau_kho.py tests/test_quet.py tests/test_quet_yeu_cau.py tests/test_chu.py -q`
Expected: `test_su_kien_2a.py` 8 passed; các file khác không có fail mới. Rồi `uv run pytest -q` → không có fail. `wc -l tram/su_kien/kho.py` = 118.

- [ ] **Step 5: Commit**

```bash
git add tram/su_kien/ket_noi.py tram/su_kien/kho.py tests/test_su_kien_2a.py
git commit -m "feat(su-kien): WAL + busy timeout, SuKien giữ cột token, sau_id, id_moi_nhat, cua_bead, close"
```

---

### Task 3: Sao lưu kho sự kiện

**Độ khó:** `de` · **Song song:** đợt 1 — chạy cùng Task 1, 2, 5, 7, 19, 23 (file mới riêng; test dùng `KhoSuKien` hiện có). Phải xong trước Task 22.

**Files:**
- Create: `tram/su_kien/sao_luu.py`
- Test: `tests/test_sao_luu.py`

**Interfaces:**
- Consumes: `bay_gio()` (`tram/duong_dan.py`).
- Produces: `sao_luu(nguon: Path, thu_muc: Path, *, giu: int = 14, luc: str | None = None) -> Path` — bản sao trực tuyến `thu_muc/su-kien-<YYYYmmddTHHMMSSZ>.db`, chỉ giữ `giu` bản mới nhất; nguồn không có → `FileNotFoundError`; `giu < 1` → `ValueError`.

- [ ] **Step 1: Viết test thất bại**

`tests/test_sao_luu.py`:

```python
import sqlite3

import pytest

from tram.su_kien.kho import KhoSuKien
from tram.su_kien.sao_luu import sao_luu


def test_sao_luu_co_du_lieu_dang_nam_trong_wal(tmp_path):
    p = tmp_path / "sk.db"
    k = KhoSuKien(p)
    for i in range(3):
        k.ghi("hr", "x", {"i": i})
    dich = sao_luu(p, tmp_path / "sl", luc="2026-10-13T03:15:00Z")
    assert dich.name == "su-kien-20261013T031500Z.db"
    db = sqlite3.connect(dich)
    assert db.execute("SELECT COUNT(*) FROM su_kien").fetchone()[0] == 3
    db.close()


def test_giu_n_ban_moi_nhat(tmp_path):
    p = tmp_path / "sk.db"
    KhoSuKien(p).ghi("hr", "x", {})
    for gio in ("01", "02", "03"):
        sao_luu(p, tmp_path / "sl", giu=2, luc=f"2026-10-13T{gio}:00:00Z")
    assert sorted(x.name for x in (tmp_path / "sl").glob("su-kien-*.db")) == [
        "su-kien-20261013T020000Z.db", "su-kien-20261013T030000Z.db"]


def test_khong_co_nguon(tmp_path):
    with pytest.raises(FileNotFoundError):
        sao_luu(tmp_path / "khong.db", tmp_path / "sl")


def test_giu_phai_duong(tmp_path):
    p = tmp_path / "sk.db"
    KhoSuKien(p).ghi("hr", "x", {})
    with pytest.raises(ValueError):
        sao_luu(p, tmp_path / "sl", giu=0)
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_sao_luu.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'tram.su_kien.sao_luu'`.

- [ ] **Step 3: Viết mã**

`tram/su_kien/sao_luu.py`:

```python
"""Sao lưu ~/.tram/su-kien.db bằng online backup của SQLite (cùng API với lệnh `.backup`) — spec 2 §12.2."""
import sqlite3
from pathlib import Path

from tram.duong_dan import bay_gio


def sao_luu(nguon: Path, thu_muc: Path, *, giu: int = 14, luc: str | None = None) -> Path:
    if giu < 1:
        raise ValueError("giu phải ≥ 1")
    if not nguon.is_file():
        raise FileNotFoundError(f"Không thấy {nguon}")
    thu_muc.mkdir(parents=True, exist_ok=True)
    nhan = (luc or bay_gio()).replace("-", "").replace(":", "")
    dich = thu_muc / f"su-kien-{nhan}.db"
    src, dst = sqlite3.connect(nguon), sqlite3.connect(dich)
    try:
        src.backup(dst)
    finally:
        dst.close()
        src.close()
    for cu in sorted(thu_muc.glob("su-kien-*.db"))[:-giu]:
        cu.unlink()
    return dich
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_sao_luu.py -q` → Expected: `4 passed`.

- [ ] **Step 5: Commit**

```bash
git add tram/su_kien/sao_luu.py tests/test_sao_luu.py
git commit -m "feat(su-kien): sao lưu trực tuyến su-kien.db, giữ N bản mới nhất"
```

---

### Task 4: Khung thao tác ghi bền — bảng `thao_tac`, khoá theo bead, `ma_thao_tac`, `expected_version`

**Độ khó:** `kho` (bền khi crash, đồng thời) · **Song song:** đợt 2 — chạy cùng Task 6, 8, 10, 11, 20, 24. **Phải xong trước:** Task 2 (`mo_ket_noi`). Task 12–17 cần task này.

**Files:**
- Create: `tram/thao_tac/loi.py`, `tram/thao_tac/kho.py`, `tram/thao_tac/chay.py`, `tram/thao_tac/chung.py`
- Test: `tests/test_thao_tac_khung.py`

**Interfaces:**
- Consumes: `mo_ket_noi` (Task 2); `bay_gio`, `doc_luc`, `tram_home` (`tram/duong_dan.py`); `KhoSuKien.moi_nhat`, `.gan_day`, `.ghi`.
- Produces:
  - `tram/thao_tac/loi.py`: `XungDot(Exception)` (409), `KhongHopLe(ValueError)` (422), `ChuaHoTro(Exception)` (501), `KhongThay(LookupError)` (404).
  - `tram/thao_tac/kho.py`: `BanGhiThaoTac(ma_thao_tac, loai, du_an, bead_id, digest_noi_dung, expected_version, buoc_da_xong: dict, ket_qua: dict | None, luc)`; `KhoThaoTac(duong_dan)` với `lay(ma) -> BanGhiThaoTac | None`, `tao(ma, *, loai, du_an, bead_id, digest, expected_version) -> None` (trùng mã → `sqlite3.IntegrityError`), `xong_buoc(ma, buoc: str, gia_tri) -> None`, `ket_thuc(ma, ket_qua: dict) -> None`, `close() -> None` (N5); `mo_kho_thao_tac() -> KhoThaoTac`.
  - `tram/thao_tac/chay.py`: `MA_RE`; `YeuCau(ma, loai, du_an, bead_id, noi_dung: dict, expected_version)`; `KetQuaThaoTac(ket_qua: dict, lap_lai: bool)`; `Buoc = tuple[str, Callable[[dict], object]]`; `khoa_bead(du_an, bead_id)` (context manager); `digest(yc) -> str`; `cung_version(a: str, b: str) -> bool`; `chay_thao_tac(kho_tt, yc, *, kiem_moi: Callable[[], None], cac_buoc: Sequence[Buoc]) -> KetQuaThaoTac`.
  - `tram/thao_tac/chung.py`: `TAC_NHAN = "dai-ca/dashboard"`; `NguCanhGhi(bd, kho, kho_tt, du_an)`; `kiem_version(bead, expected: str) -> None` (khác → `XungDot`); `co_su_kien(kho, du_an, bead_id, loai, ma) -> bool`; `ghi_su_kien_mot_lan(kho, du_an, bead_id, loai, du_lieu: dict, *, ma: str) -> bool`.

Luật của `chay_thao_tac` (spec §12.3): trong khoá `(du_an, bead_id)`: (1) đã có bản ghi cùng mã — digest khác → `XungDot`; đã có `ket_qua` → trả kết quả cũ, `lap_lai=True`, **không** gọi `kiem_moi`, không làm lại bước nào; chưa có `ket_qua` (crash/lỗi giữa chừng) → làm tiếp các bước chưa đánh dấu, không gọi `kiem_moi`. (2) Mã mới — gọi `kiem_moi()` (kiểm version + luật; ném lỗi thì **không ghi gì**), ghi bản ghi `thao_tac` **trước** khi chạy bước nào. (3) Mỗi bước nhận dict kết quả các bước trước, trả giá trị JSON được, được đánh dấu ngay sau khi xong. Mỗi bước tự đối soát với thực tế (đọc lại `bd`) trước khi ghi — không đoán bước trước đã thất bại. (4) `digest` gồm loại, dự án, bead, nội dung — **không** gồm `expected_version` (N4, ghi trong docstring): gửi lại cùng mã sau khi chính thao tác đó làm bead đổi vẫn nhận kết quả cũ, không 409.

- [ ] **Step 1: Viết test thất bại**

`tests/test_thao_tac_khung.py`:

```python
import sqlite3
import threading
import time

import pytest

from bead_gia import bead
from tram.su_kien.kho import KhoSuKien
from tram.thao_tac.chay import YeuCau, chay_thao_tac, cung_version
from tram.thao_tac.chung import ghi_su_kien_mot_lan, kiem_version
from tram.thao_tac.kho import KhoThaoTac
from tram.thao_tac.loi import KhongHopLe, XungDot

MA = "ma-thu-0001"


def yc(ma=MA, noi_dung=None, bead_id="hr-1"):
    return YeuCau(ma, "thu", "hr", bead_id, noi_dung or {"a": 1}, "2026-10-13T01:00:00Z")


def test_kho_tao_lay_danh_dau_ket_thuc(tmp_path):
    k = KhoThaoTac(tmp_path / "sk.db")
    k.tao(MA, loai="thu", du_an="hr", bead_id="hr-1", digest="d", expected_version="v")
    k.xong_buoc(MA, "a", 1)
    k.xong_buoc(MA, "b", {"x": "ă"})
    bg = k.lay(MA)
    assert bg.buoc_da_xong == {"a": 1, "b": {"x": "ă"}} and bg.ket_qua is None
    assert (bg.loai, bg.du_an, bg.bead_id, bg.expected_version) == ("thu", "hr", "hr-1", "v")
    k.ket_thuc(MA, {"xong": True})
    assert k.lay(MA).ket_qua == {"xong": True}
    assert k.lay("ma-khac-0001") is None
    k.close()
    with pytest.raises(sqlite3.ProgrammingError):
        k.lay(MA)


def test_kho_trung_ma_nem_integrity(tmp_path):
    k = KhoThaoTac(tmp_path / "sk.db")
    k.tao(MA, loai="thu", du_an="hr", bead_id=None, digest="d", expected_version="v")
    with pytest.raises(sqlite3.IntegrityError):
        k.tao(MA, loai="thu", du_an="hr", bead_id=None, digest="d", expected_version="v")


def test_chay_dung_thu_tu_va_lan_hai_tra_ket_qua_cu(tmp_path):
    k, goi = KhoThaoTac(tmp_path / "sk.db"), []
    buoc = [("a", lambda d: goi.append("a") or 1), ("b", lambda d: goi.append("b") or d["a"] + 1)]
    kq = chay_thao_tac(k, yc(), kiem_moi=lambda: None, cac_buoc=buoc)
    assert kq.ket_qua == {"a": 1, "b": 2} and kq.lap_lai is False and goi == ["a", "b"]
    kq2 = chay_thao_tac(k, yc(), kiem_moi=lambda: pytest.fail("không được kiểm lại"), cac_buoc=buoc)
    assert kq2.lap_lai is True and kq2.ket_qua == {"a": 1, "b": 2} and goi == ["a", "b"]


def test_cung_ma_khac_noi_dung_la_xung_dot(tmp_path):
    k = KhoThaoTac(tmp_path / "sk.db")
    chay_thao_tac(k, yc(), kiem_moi=lambda: None, cac_buoc=[("a", lambda d: 1)])
    with pytest.raises(XungDot):
        chay_thao_tac(k, yc(noi_dung={"a": 2}), kiem_moi=lambda: None, cac_buoc=[("a", lambda d: 1)])


def test_kiem_moi_that_bai_thi_khong_ghi_gi(tmp_path):
    k = KhoThaoTac(tmp_path / "sk.db")

    def kiem():
        raise XungDot("bead đã đổi")

    with pytest.raises(XungDot):
        chay_thao_tac(k, yc(), kiem_moi=kiem, cac_buoc=[("a", lambda d: 1)])
    assert k.lay(MA) is None


def test_buoc_loi_thi_lan_sau_lam_tiep_khong_lam_lai(tmp_path):
    k, goi, lan = KhoThaoTac(tmp_path / "sk.db"), [], {"n": 0}

    def b(d):
        lan["n"] += 1
        if lan["n"] == 1:
            raise RuntimeError("crash")
        goi.append("b")
        return d["a"] + 1

    buoc = [("a", lambda d: goi.append("a") or 1), ("b", b)]
    with pytest.raises(RuntimeError):
        chay_thao_tac(k, yc(), kiem_moi=lambda: None, cac_buoc=buoc)
    assert k.lay(MA).buoc_da_xong == {"a": 1} and k.lay(MA).ket_qua is None
    kq = chay_thao_tac(k, yc(), kiem_moi=lambda: pytest.fail("không kiểm lại khi làm tiếp"), cac_buoc=buoc)
    assert goi == ["a", "b"] and kq.ket_qua == {"a": 1, "b": 2} and kq.lap_lai is False


def test_ma_khong_hop_le(tmp_path):
    with pytest.raises(KhongHopLe):
        chay_thao_tac(KhoThaoTac(tmp_path / "sk.db"), yc(ma="ngắn"), kiem_moi=lambda: None, cac_buoc=[])


def test_hai_luong_cung_ma_chi_chay_mot_lan(tmp_path):
    db, dem, kq = tmp_path / "sk.db", [], []

    def b(d):
        time.sleep(0.05)
        dem.append(1)
        return 1

    def chay():
        kq.append(chay_thao_tac(KhoThaoTac(db), yc(), kiem_moi=lambda: None, cac_buoc=[("b", b)]))

    luong = [threading.Thread(target=chay) for _ in range(2)]
    for t in luong:
        t.start()
    for t in luong:
        t.join()
    assert len(dem) == 1 and sorted(x.lap_lai for x in kq) == [False, True]


def test_cung_version():
    assert cung_version("2026-10-13T01:00:00Z", "2026-10-13T01:00:00+00:00")
    assert not cung_version("2026-10-13T01:00:00Z", "2026-10-13T01:00:01Z")
    assert cung_version("bat", "bat") and not cung_version("bat", "tat")


def test_kiem_version_bead():
    kiem_version(bead(updated_at="2026-10-13T01:00:00Z"), "2026-10-13T01:00:00Z")
    with pytest.raises(XungDot):
        kiem_version(bead(updated_at="2026-10-13T01:00:05Z"), "2026-10-13T01:00:00Z")


def test_ghi_su_kien_mot_lan_theo_ma(tmp_path):
    k = KhoSuKien(tmp_path / "sk.db")
    assert ghi_su_kien_mot_lan(k, "hr", "hr-1", "cot.tra_ve", {"gop_y": "x"}, ma=MA) is True
    assert ghi_su_kien_mot_lan(k, "hr", "hr-1", "cot.tra_ve", {"gop_y": "x"}, ma=MA) is False
    assert ghi_su_kien_mot_lan(k, "_tram", None, "estop.bat", {}, ma=MA) is True
    assert ghi_su_kien_mot_lan(k, "_tram", None, "estop.bat", {}, ma=MA) is False
    s = k.moi_nhat("hr", "hr-1", "cot.tra_ve")
    assert s.du_lieu == {"gop_y": "x", "ma_thao_tac": MA} and s.tac_nhan == "dai-ca/dashboard"
    assert len(k.gan_day("hr", "cot.tra_ve", 10)) == 1
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_thao_tac_khung.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'tram.thao_tac.chay'`.

- [ ] **Step 3: Viết mã**

`tram/thao_tac/loi.py`:

```python
"""Lỗi nghiệp vụ của thao tác ghi; tram-api ánh xạ sang mã HTTP (tram/api/app.py)."""


class XungDot(Exception):
    """409: bead đã đổi so với expected_version, hoặc cùng ma_thao_tac mà nội dung khác."""


class KhongHopLe(ValueError):
    """422: yêu cầu sai luật (sai cột, thiếu câu trả lời, mã không hợp lệ, ...)."""


class ChuaHoTro(Exception):
    """501: nút có từ 2a nhưng phần xử lý thuộc lát sau (Duyệt / Trả về spec — phần 4b)."""


class KhongThay(LookupError):
    """404: dự án hoặc bead không có."""
```

`tram/thao_tac/kho.py`:

```python
"""Bảng `thao_tac` trong ~/.tram/su-kien.db: tiến độ từng thao tác ghi của dashboard (spec 2 §12.2, §12.3)."""
import json
from dataclasses import dataclass
from pathlib import Path

from tram.duong_dan import bay_gio, tram_home
from tram.su_kien.ket_noi import mo_ket_noi

LUOC_DO = """
CREATE TABLE IF NOT EXISTS thao_tac (
  ma_thao_tac TEXT PRIMARY KEY,
  loai TEXT NOT NULL,
  du_an TEXT NOT NULL,
  bead_id TEXT,
  digest_noi_dung TEXT NOT NULL,
  expected_version TEXT NOT NULL,
  buoc_da_xong TEXT NOT NULL DEFAULT '{}',
  ket_qua TEXT,
  luc TEXT NOT NULL
);
"""
_COT = ("ma_thao_tac, loai, du_an, bead_id, digest_noi_dung, expected_version,"
        " buoc_da_xong, ket_qua, luc")


@dataclass(frozen=True)
class BanGhiThaoTac:
    ma_thao_tac: str
    loai: str
    du_an: str
    bead_id: str | None
    digest_noi_dung: str
    expected_version: str
    buoc_da_xong: dict
    ket_qua: dict | None
    luc: str


class KhoThaoTac:
    def __init__(self, duong_dan: Path):
        self._db = mo_ket_noi(duong_dan)
        self._db.executescript(LUOC_DO)

    def lay(self, ma: str) -> BanGhiThaoTac | None:
        h = self._db.execute(f"SELECT {_COT} FROM thao_tac WHERE ma_thao_tac=?", (ma,)).fetchone()
        if h is None:
            return None
        return BanGhiThaoTac(*h[:6], json.loads(h[6]), None if h[7] is None else json.loads(h[7]), h[8])

    def tao(self, ma: str, *, loai: str, du_an: str, bead_id: str | None, digest: str,
            expected_version: str) -> None:
        with self._db:
            self._db.execute(
                "INSERT INTO thao_tac (ma_thao_tac, loai, du_an, bead_id, digest_noi_dung,"
                " expected_version, luc) VALUES (?,?,?,?,?,?,?)",
                (ma, loai, du_an, bead_id, digest, expected_version, bay_gio()))

    def xong_buoc(self, ma: str, buoc: str, gia_tri) -> None:
        with self._db:
            h = self._db.execute("SELECT buoc_da_xong FROM thao_tac WHERE ma_thao_tac=?", (ma,)).fetchone()
            da = json.loads(h[0])
            da[buoc] = gia_tri
            self._db.execute("UPDATE thao_tac SET buoc_da_xong=? WHERE ma_thao_tac=?",
                             (json.dumps(da, ensure_ascii=False), ma))

    def ket_thuc(self, ma: str, ket_qua: dict) -> None:
        with self._db:
            self._db.execute("UPDATE thao_tac SET ket_qua=? WHERE ma_thao_tac=?",
                             (json.dumps(ket_qua, ensure_ascii=False), ma))

    def close(self) -> None:
        self._db.close()


def mo_kho_thao_tac() -> KhoThaoTac:
    return KhoThaoTac(tram_home() / "su-kien.db")
```

`tram/thao_tac/chay.py`:

```python
"""Chạy một thao tác ghi idempotent theo ma_thao_tac (spec 2 §12.3)."""
import hashlib
import json
import re
import sqlite3
import threading
from collections.abc import Callable, Iterator, Sequence
from contextlib import contextmanager
from dataclasses import dataclass

from tram.duong_dan import doc_luc
from tram.thao_tac.kho import KhoThaoTac
from tram.thao_tac.loi import KhongHopLe, XungDot

MA_RE = re.compile(r"[A-Za-z0-9-]{8,64}")
Buoc = tuple[str, Callable[[dict], object]]


@dataclass(frozen=True)
class YeuCau:
    ma: str
    loai: str
    du_an: str
    bead_id: str | None
    noi_dung: dict
    expected_version: str


@dataclass(frozen=True)
class KetQuaThaoTac:
    ket_qua: dict
    lap_lai: bool


_KHOA_CHUNG = threading.Lock()
_KHOA: dict[tuple[str, str | None], threading.Lock] = {}


@contextmanager
def khoa_bead(du_an: str, bead_id: str | None) -> Iterator[None]:
    """Một tram-api một tiến trình (Global Constraints) → khoá trong bộ nhớ đủ tuần tự hoá theo bead."""
    with _KHOA_CHUNG:
        k = _KHOA.setdefault((du_an, bead_id), threading.Lock())
    with k:
        yield


def digest(yc: YeuCau) -> str:
    tho = json.dumps({"loai": yc.loai, "du_an": yc.du_an, "bead_id": yc.bead_id, "noi_dung": yc.noi_dung},
                     ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(tho.encode()).hexdigest()


def cung_version(a: str, b: str) -> bool:
    try:
        return doc_luc(a) == doc_luc(b)
    except ValueError:
        return a == b


def chay_thao_tac(kho_tt: KhoThaoTac, yc: YeuCau, *, kiem_moi: Callable[[], None],
                  cac_buoc: Sequence[Buoc]) -> KetQuaThaoTac:
    """`digest` gồm loại, dự án, bead, nội dung — **không** gồm `expected_version` (N4): gửi lại cùng mã
    sau khi bead đã đổi (do chính thao tác này) vẫn nhận kết quả cũ thay vì 409."""
    if not MA_RE.fullmatch(yc.ma):
        raise KhongHopLe("ma_thao_tac phải 8–64 ký tự chữ, số hoặc '-'")
    dg = digest(yc)
    with khoa_bead(yc.du_an, yc.bead_id):
        bg = kho_tt.lay(yc.ma)
        if bg is not None:
            if bg.digest_noi_dung != dg:
                raise XungDot("Cùng ma_thao_tac nhưng nội dung khác")
            if bg.ket_qua is not None:
                return KetQuaThaoTac(bg.ket_qua, True)
            da_xong = dict(bg.buoc_da_xong)
        else:
            kiem_moi()
            try:
                kho_tt.tao(yc.ma, loai=yc.loai, du_an=yc.du_an, bead_id=yc.bead_id, digest=dg,
                           expected_version=yc.expected_version)
            except sqlite3.IntegrityError:
                raise XungDot("ma_thao_tac đã được dùng cho thao tác khác") from None
            da_xong = {}
        for ten, ham in cac_buoc:
            if ten not in da_xong:
                da_xong[ten] = ham(da_xong)
                kho_tt.xong_buoc(yc.ma, ten, da_xong[ten])
        kho_tt.ket_thuc(yc.ma, da_xong)
        return KetQuaThaoTac(da_xong, False)
```

`tram/thao_tac/chung.py`:

```python
"""Phần dùng chung của các thao tác ghi dashboard."""
from dataclasses import dataclass

from tram.beads.bd import Bd
from tram.beads.mo_hinh import Bead
from tram.su_kien.kho import KhoSuKien
from tram.thao_tac.chay import cung_version
from tram.thao_tac.kho import KhoThaoTac
from tram.thao_tac.loi import XungDot

TAC_NHAN = "dai-ca/dashboard"


@dataclass(frozen=True)
class NguCanhGhi:
    bd: Bd               # actor dai-ca/dashboard (test: BdGia)
    kho: KhoSuKien
    kho_tt: KhoThaoTac
    du_an: str


def kiem_version(bead: Bead, expected: str) -> None:
    if not cung_version(bead.updated_at, expected):
        raise XungDot(f"Bead {bead.id} đã đổi (hiện {bead.updated_at}, đang xem {expected}) — tải lại")


def co_su_kien(kho: KhoSuKien, du_an: str, bead_id: str | None, loai: str, ma: str) -> bool:
    def khop(s) -> bool:
        return s.du_lieu.get("ma_thao_tac") == ma

    if bead_id is not None:
        return kho.moi_nhat(du_an, bead_id, loai, dieu_kien=khop) is not None
    return any(khop(s) for s in kho.gan_day(du_an, loai, 50))


def ghi_su_kien_mot_lan(kho: KhoSuKien, du_an: str, bead_id: str | None, loai: str, du_lieu: dict,
                        *, ma: str) -> bool:
    """Ghi sự kiện kèm ma_thao_tac nếu chưa có — crash giữa 'ghi' và 'đánh dấu bước' không sinh bản thứ hai (G7)."""
    if co_su_kien(kho, du_an, bead_id, loai, ma):
        return False
    kho.ghi(du_an, loai, {**du_lieu, "ma_thao_tac": ma}, bead_id=bead_id, tac_nhan=TAC_NHAN)
    return True
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_thao_tac_khung.py -q` → Expected: `11 passed`.

- [ ] **Step 5: Commit**

```bash
git add tram/thao_tac/loi.py tram/thao_tac/kho.py tram/thao_tac/chay.py tram/thao_tac/chung.py \
  tests/test_thao_tac_khung.py
git commit -m "feat(thao-tac): bảng thao_tac, chạy thao tác idempotent theo ma_thao_tac, khoá theo bead, kiểm version"
```

---

### Task 5: Cấu hình trạm `~/.tram/cau-hinh.yaml`

**Độ khó:** `de` · **Song song:** đợt 1 — chạy cùng Task 1, 2, 3, 7, 19, 23. Phải xong trước Task 10, 12, 21.

**Files:**
- Create: `tram/cau_hinh/tram.py`
- Test: `tests/test_cau_hinh_tram.py`

**Interfaces:**
- Consumes: `tram_home()`.
- Produces: `CauHinhTelegram(chat_id: str | None = None, gio_yen_lang: str | None = None)`; `CauHinhTram(dai_ca_logins: tuple[str, ...] = (), ten_may_b: str | None = None, telegram: CauHinhTelegram = CauHinhTelegram(), dashboard_url: str | None = None)`; `nap_cau_hinh_tram(duong_dan: Path | None = None) -> CauHinhTram` (mặc định `tram_home()/"cau-hinh.yaml"`; file không có → mặc định = **chỉ đọc**, không báo tin; sai dạng → `ValueError`).

Mẫu file (Đại ca tự tạo, không chứa bí mật — spec §12.5):

```yaml
dai_ca_logins: ["dai-ca@example.com"]   # login Tailscale của Đại ca
ten_may_b: "may-b.tail1234.ts.net"          # tên máy B trong tailnet (Origin hợp lệ = https://<ten_may_b>)
dashboard_url: "https://may-b.tail1234.ts.net/"
telegram:
  chat_id: "123456789"
  gio_yen_lang: "23:00-07:00"               # tuỳ chọn, giờ Việt Nam
```

- [ ] **Step 1: Viết test thất bại**

`tests/test_cau_hinh_tram.py`:

```python
import pytest

from tram.cau_hinh.tram import CauHinhTelegram, CauHinhTram, nap_cau_hinh_tram


def _ghi(tmp_path, noi_dung: str):
    p = tmp_path / "cau-hinh.yaml"
    p.write_text(noi_dung, encoding="utf-8")
    return p


def test_khong_co_file_la_mac_dinh_chi_doc(tram_home_tam):
    ch = nap_cau_hinh_tram()
    assert ch == CauHinhTram() and ch.dai_ca_logins == () and ch.telegram == CauHinhTelegram()


def test_doc_du_truong(tmp_path):
    p = _ghi(tmp_path, 'dai_ca_logins: ["a@b.c"]\nten_may_b: may-b.tail.ts.net\n'
                       'dashboard_url: "https://may-b.tail.ts.net/"\n'
                       'telegram: {chat_id: 123456789, gio_yen_lang: "23:00-07:00"}\n')
    ch = nap_cau_hinh_tram(p)
    assert ch.dai_ca_logins == ("a@b.c",) and ch.ten_may_b == "may-b.tail.ts.net"
    assert ch.telegram == CauHinhTelegram("123456789", "23:00-07:00")
    assert ch.dashboard_url == "https://may-b.tail.ts.net/"


@pytest.mark.parametrize("noi_dung", [
    'telegram: {gio_yen_lang: "23h-7h"}\n',
    'dai_ca_logins: "a@b.c"\n',
    'dai_ca_logins: ["", 3]\n',
    'dashboard_url: "http://may-b/"\n',
    'ten_may_b: "may b/x"\n',
    '- danh sách\n',
])
def test_sai_dang_bao_loi(tmp_path, noi_dung):
    with pytest.raises(ValueError):
        nap_cau_hinh_tram(_ghi(tmp_path, noi_dung))


def test_file_rong_la_mac_dinh(tmp_path):
    assert nap_cau_hinh_tram(_ghi(tmp_path, "")) == CauHinhTram()
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_cau_hinh_tram.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'tram.cau_hinh.tram'`.

- [ ] **Step 3: Viết mã**

`tram/cau_hinh/tram.py`:

```python
"""~/.tram/cau-hinh.yaml (spec 2 §12.5): không chứa bí mật; thiếu file → dashboard chỉ đọc, không báo tin."""
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from tram.duong_dan import tram_home

GIO_RE = re.compile(r"([01]\d|2[0-3]):[0-5]\d-([01]\d|2[0-3]):[0-5]\d")
TEN_MAY_RE = re.compile(r"[A-Za-z0-9.-]+")


@dataclass(frozen=True)
class CauHinhTelegram:
    chat_id: str | None = None
    gio_yen_lang: str | None = None


@dataclass(frozen=True)
class CauHinhTram:
    dai_ca_logins: tuple[str, ...] = ()
    ten_may_b: str | None = None
    telegram: CauHinhTelegram = field(default_factory=CauHinhTelegram)
    dashboard_url: str | None = None


def _chuoi(x) -> str | None:
    return None if x is None else (str(x).strip() or None)


def nap_cau_hinh_tram(duong_dan: Path | None = None) -> CauHinhTram:
    p = duong_dan or tram_home() / "cau-hinh.yaml"
    if not p.exists():
        return CauHinhTram()
    raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        raise ValueError(f"{p}: phải là một bảng khoá → giá trị")
    logins = raw.get("dai_ca_logins") or []
    if not isinstance(logins, list) or not all(isinstance(x, str) and x.strip() for x in logins):
        raise ValueError("dai_ca_logins phải là danh sách chuỗi không rỗng")
    ten_may = _chuoi(raw.get("ten_may_b"))
    if ten_may is not None and not TEN_MAY_RE.fullmatch(ten_may):
        raise ValueError("ten_may_b chỉ gồm chữ, số, '.', '-'")
    url = _chuoi(raw.get("dashboard_url"))
    if url is not None and not url.startswith("https://"):
        raise ValueError("dashboard_url phải bắt đầu bằng https://")
    tg = raw.get("telegram") or {}
    if not isinstance(tg, dict):
        raise ValueError("telegram phải là bảng {chat_id, gio_yen_lang}")
    gio = _chuoi(tg.get("gio_yen_lang"))
    if gio is not None and not GIO_RE.fullmatch(gio):
        raise ValueError("telegram.gio_yen_lang phải dạng HH:MM-HH:MM")
    return CauHinhTram(tuple(x.strip() for x in logins), ten_may,
                       CauHinhTelegram(_chuoi(tg.get("chat_id")), gio), url)
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_cau_hinh_tram.py -q` → Expected: `9 passed`.

- [ ] **Step 5: Commit**

```bash
git add tram/cau_hinh/tram.py tests/test_cau_hinh_tram.py
git commit -m "feat(cau-hinh): đọc ~/.tram/cau-hinh.yaml (dai_ca_logins, ten_may_b, telegram, dashboard_url)"
```

---

### Task 6: Bọc `bd` cho thao tác ghi của dashboard — `mot`, `tao`, `dong`, `them_phu_thuoc`

**Độ khó:** `de` · **Song song:** đợt 2 — chạy cùng Task 4, 8, 10, 11, 20, 24. **Phải xong trước:** Task 1 (`KhongThayBead`, cùng file `bd.py`). Task 12, 13, 14, 15 cần task này.

**Files:**
- Modify: `tram/beads/bd.py` (bản plan 1a + `KhongThayBead` của Task 1 — thêm, không sửa phần có sẵn)
- Test: `tests/test_bd_ghi.py`

**Interfaces:**
- Consumes: `Bd._chay`, `Bd.tat_ca` (bản plan 1a), `LoiBd`, `KhongThayBead` (Task 1).
- Produces:
  - `Bd.mot(bead_id: str) -> Bead` — đọc qua `tat_ca()` (dạng `bd list` đã spike) rồi lọc; không có → `KhongThayBead`.
  - `Bd.tao(tieu_de: str, *, loai: str, mo_ta: str, nhan: Sequence[str] = ()) -> str` — `bd create <tiêu đề> -t <loai> -d <mo_ta> --silent --actor <actor>` (+ `-l a,b` khi có nhãn); trả mã bead (một từ), khác → `LoiBd`.
  - `Bd.dong(bead_id: str, ly_do: str) -> None` — `bd close <id> --reason <ly_do> --actor <actor>`.
  - `Bd.them_phu_thuoc(bead_id: str, phu_thuoc_vao: str) -> None` — `bd dep add <bead_id> <phu_thuoc_vao> --actor <actor>` (**bead_id phụ thuộc phu_thuoc_vao**, tức `phu_thuoc_vao` chặn `bead_id` — spike mục "Phụ thuộc"). Lệnh này báo "Added" cả khi cặp đã có → người gọi tự kiểm trùng.

- [ ] **Step 1: Viết test thất bại**

`tests/test_bd_ghi.py`:

```python
from pathlib import Path

import pytest

from tram.beads.bd import Bd, KhongThayBead, LoiBd

MAU = Path(__file__).parent / "du_lieu" / "beads-mau.json"


class RunnerGia:
    def __init__(self, ra: str = ""):
        self.goi: list[list[str]] = []
        self.ra = ra

    def __call__(self, args):
        self.goi.append(list(args))
        return self.ra


def _bd(ra=""):
    r = RunnerGia(ra)
    return Bd(Path("/repo"), actor="dai-ca/dashboard", runner=r), r


def test_mot_doc_qua_bd_list():
    bd, r = _bd(MAU.read_text())
    b = bd.mot("hr-3")
    assert b.id == "hr-3" and "cot:ai-lam" in b.labels
    assert r.goi[0] == ["-C", "/repo", "list", "--json", "--all", "--limit", "0"]


def test_mot_khong_co_nem_khong_thay():
    bd, _ = _bd(MAU.read_text())
    with pytest.raises(KhongThayBead):
        bd.mot("hr-99")
    assert issubclass(KhongThayBead, LoiBd)


def test_tao_dung_co_va_tra_ma():
    bd, r = _bd("hr-77\n")
    assert bd.tao("Chốt: Giá tour", loai="decision", mo_ta="Hỏi: …") == "hr-77"
    assert r.goi[0] == ["-C", "/repo", "create", "Chốt: Giá tour", "-t", "decision", "-d", "Hỏi: …",
                        "--silent", "--actor", "dai-ca/dashboard"]


def test_tao_co_nhan():
    bd, r = _bd("hr-78")
    bd.tao("t", loai="task", mo_ta="m", nhan=["a", "b"])
    assert r.goi[0][-2:] == ["-l", "a,b"]


@pytest.mark.parametrize("ra", ["", "\n", "hai từ\n"])
def test_tao_dau_ra_la_nem_LoiBd(ra):
    bd, _ = _bd(ra)
    with pytest.raises(LoiBd):
        bd.tao("t", loai="decision", mo_ta="m")


def test_dong_va_them_phu_thuoc():
    bd, r = _bd()
    bd.dong("hr-5", "- câu trả lời bắt đầu bằng gạch")
    bd.them_phu_thuoc("hr-5", "hr-77")
    assert r.goi == [
        ["-C", "/repo", "close", "hr-5", "--reason", "- câu trả lời bắt đầu bằng gạch", "--actor", "dai-ca/dashboard"],
        ["-C", "/repo", "dep", "add", "hr-5", "hr-77", "--actor", "dai-ca/dashboard"],
    ]
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_bd_ghi.py -q`
Expected: FAIL — `8 failed`, `AttributeError: 'Bd' object has no attribute 'mot'` (và `tao`, `dong`, `them_phu_thuoc`).

- [ ] **Step 3: Viết mã**

Thêm bốn phương thức cuối lớp `Bd` trong `tram/beads/bd.py` (lớp `KhongThayBead` đã có từ Task 1):

```python
    def mot(self, bead_id: str) -> Bead:
        """Đọc một bead qua `bd list` — dạng JSON đã spike; chưa dựng Bead từ `bd show` (plan 1a G3)."""
        for b in self.tat_ca():
            if b.id == bead_id:
                return b
        raise KhongThayBead(f"Không thấy bead {bead_id}")

    def tao(self, tieu_de: str, *, loai: str, mo_ta: str, nhan: Sequence[str] = ()) -> str:
        args = ["create", tieu_de, "-t", loai, "-d", mo_ta, "--silent", "--actor", self.actor]
        if nhan:
            args += ["-l", ",".join(nhan)]
        ra = self._chay(*args).strip()
        if len(ra.split()) != 1:
            raise LoiBd(f"bd create không trả về một mã bead: {ra[:100]!r}")
        return ra

    def dong(self, bead_id: str, ly_do: str) -> None:
        self._chay("close", bead_id, "--reason", ly_do, "--actor", self.actor)

    def them_phu_thuoc(self, bead_id: str, phu_thuoc_vao: str) -> None:
        """`bd dep add A B`: A phụ thuộc B (B chặn A). Lặp cặp cũ vẫn 'Added' — người gọi tự kiểm trùng."""
        self._chay("dep", "add", bead_id, phu_thuoc_vao, "--actor", self.actor)
```

Ghi chú: giá trị bắt đầu bằng `-` truyền dưới dạng phần tử argv riêng sau cờ đòi giá trị — `bd` (cobra/pflag) nhận nguyên làm giá trị. Ca này kiểm tay trên DB `bd` tạm ở Task 26 bước 6.

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_bd_ghi.py tests/test_beads.py -q`
Expected: `test_bd_ghi.py` 8 passed; `test_beads.py` không có fail mới. `wc -l tram/beads/bd.py` = 98.

- [ ] **Step 5: Commit**

```bash
git add tram/beads/bd.py tests/test_bd_ghi.py
git commit -m "feat(beads): bọc bd create/close/dep add và đọc một bead cho dashboard"
```

---

### Task 7: Đọc bàn giao có danh sách lỗi

**Độ khó:** `de` · **Song song:** đợt 1 — chạy cùng Task 1, 2, 3, 5, 19, 23. Phải xong trước Task 9, 15.

**Files:**
- Create: `tram/ban_giao/doc.py`
- Test: `tests/test_doc_ban_giao.py`

**Interfaces:**
- Consumes: `BanGiao` (có `pr` — plan 1a T1), `KHOI_RE`, `GIOI_HAN_BYTE` (`tram/ban_giao/schema.py`).
- Produces:
  - `doc_khoi_ban_giao_co_loi(notes: str | None) -> tuple[BanGiao | None, list[str]]` — không có dấu khối → `(None, [])`; có dấu mà hỏng / quá 64 KB / sai schema → `(None, [lỗi…])` (tối đa 10 dòng); hợp lệ → `(bg, [])`. (Spec §12.5: `doc_khoi_ban_giao` cũ trả `None` cho cả "không có" lẫn "hỏng" — giữ hàm cũ cho 1a.)
  - `tom_tat_ban_giao(notes: str | None) -> dict | None` — `None` khi không có khối; ngược lại `{pr, nhanh, commit, file_ban_giao, loi: [str]}`; `pr` không khớp `https://…` → `pr = None` + lỗi "pr không phải URL https — không hiện link".

- [ ] **Step 1: Viết test thất bại**

`tests/test_doc_ban_giao.py`:

```python
from bead_gia import notes_ban_giao
from tram.ban_giao.doc import doc_khoi_ban_giao_co_loi, tom_tat_ban_giao


def test_khong_co_khoi():
    assert doc_khoi_ban_giao_co_loi("chỉ là ghi chú") == (None, [])
    assert doc_khoi_ban_giao_co_loi(None) == (None, [])
    assert tom_tat_ban_giao("chỉ là ghi chú") is None


def test_khoi_hop_le_co_pr():
    bg, loi = doc_khoi_ban_giao_co_loi(notes_ban_giao())
    assert loi == [] and bg.pr == "https://github.com/o/r/pull/7"
    assert tom_tat_ban_giao(notes_ban_giao()) == {
        "pr": "https://github.com/o/r/pull/7", "nhanh": "fix/x", "commit": "abc1234",
        "file_ban_giao": "docs/handovers/x.md", "loi": []}


def test_khoi_sai_schema_co_loi():
    bg, loi = doc_khoi_ban_giao_co_loi(notes_ban_giao(luot="một"))
    assert bg is None and loi and any("luot" in x for x in loi)
    tt = tom_tat_ban_giao(notes_ban_giao(luot="một"))
    assert tt["pr"] is None and tt["loi"]


def test_thieu_dau_dong():
    bg, loi = doc_khoi_ban_giao_co_loi('<!-- ban-giao -->\n{"phien_ban": 1}')
    assert bg is None and loi == ["Khối bàn giao thiếu dấu đóng hoặc không phải một JSON object"]


def test_pr_http_khong_hien_link():
    tt = tom_tat_ban_giao(notes_ban_giao(pr="http://github.com/o/r/pull/7"))
    assert tt["pr"] is None and "pr không phải URL https — không hiện link" in tt["loi"]


def test_khoi_qua_64kb():
    bg, loi = doc_khoi_ban_giao_co_loi(notes_ban_giao(vuong_mac=["x" * 70_000]))
    assert bg is None and loi == ["Khối bàn giao vượt 64 KB"]
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_doc_ban_giao.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'tram.ban_giao.doc'`.

- [ ] **Step 3: Viết mã**

`tram/ban_giao/doc.py`:

```python
"""Đọc khối bàn giao trong notes kèm danh sách lỗi — dashboard cần phân biệt 'không có' và 'hỏng' (spec 2 §12.5)."""
import re

from pydantic import ValidationError

from tram.ban_giao.schema import GIOI_HAN_BYTE, KHOI_RE, BanGiao

DAU = "<!-- ban-giao -->"
PR_HTTPS = re.compile(r"https://[^\s<>\"']+")


def doc_khoi_ban_giao_co_loi(notes: str | None) -> tuple[BanGiao | None, list[str]]:
    notes = notes or ""
    khop = KHOI_RE.findall(notes)
    if not khop:
        return (None, ["Khối bàn giao thiếu dấu đóng hoặc không phải một JSON object"]) if DAU in notes else (None, [])
    tho = khop[-1]
    if len(tho.encode()) > GIOI_HAN_BYTE:
        return None, ["Khối bàn giao vượt 64 KB"]
    try:
        return BanGiao.model_validate_json(tho), []
    except ValidationError as e:
        return None, [f"{'.'.join(str(x) for x in l['loc']) or 'khoi'}: {l['msg']}" for l in e.errors()][:10]


def tom_tat_ban_giao(notes: str | None) -> dict | None:
    bg, loi = doc_khoi_ban_giao_co_loi(notes)
    if bg is None and not loi:
        return None
    pr = bg.pr if bg is not None else None
    if pr is not None and not PR_HTTPS.fullmatch(pr):
        loi, pr = loi + ["pr không phải URL https — không hiện link"], None
    return {"pr": pr, "nhanh": bg.nhanh if bg else None, "commit": bg.commit if bg else None,
            "file_ban_giao": bg.file_ban_giao if bg else None, "loi": loi}
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_doc_ban_giao.py tests/test_ban_giao.py -q`
Expected: `test_doc_ban_giao.py` 6 passed; `test_ban_giao.py` không có fail mới.

- [ ] **Step 5: Commit**

```bash
git add tram/ban_giao/doc.py tests/test_doc_ban_giao.py
git commit -m "feat(ban-giao): đọc khối bàn giao trả danh sách lỗi, tóm tắt cho dashboard"
```

---

### Task 8: Suy cột lúc đọc + làm sạch chuỗi

**Độ khó:** `kho` (luật suy cột, ca biên) · **Song song:** đợt 2 — chạy cùng Task 4, 6, 10, 11, 20, 24. **Phải xong trước:** Task 1 (`bead_gia`). Task 9, 12, 13, 14 cần task này.

**Files:**
- Create: `tram/suy/lam_sach.py`, `tram/suy/cot.py`
- Test: `tests/test_suy_cot.py`

**Interfaces:**
- Consumes: `Bead.nhan_cot()`, `Bead.priority` (plan 1a); `bi_chan_boi(bead, theo_id)` (`tram/cham_cot/luat_cung.py`, plan 1a T3); `NHAN_KHOA` (`tram/cham_cot/ghi.py`); `KhoSuKien.moi_nhat`.
- Produces:
  - `lam_sach(s: str | None, toi_da: int = 500) -> str` — bỏ ký tự loại `Cc`, `Cf`, `Cs`, `Co` (giữ `\n`, `\t`); dài hơn `toi_da` → cắt còn `toi_da - 1` ký tự + `…`.
  - Hằng: `HANG = ("ai-lam", "can-chot", "cho-review", "chua-cham", "epic", "theo-plan")`, `NHAN_ESCALATION = "tram:escalation"`, `NHAN_CO_DO = "co-do"`, `NHAN_LUONG = {"can-spec", "cho-duyet-spec", "theo-plan"}`, `TRANG_THAI_HIEN = {"open", "in_progress", "blocked"}`.
  - `ViTri(hang: str, tu_nhan_cot: bool, lech: bool, khe_spec: bool, cho: tuple[str, ...])`.
  - `suy_vi_tri(bead, theo_id: dict[str, Bead]) -> ViTri` — luật spec §5.1 (epic trước; có `cot:*` → cột theo ưu tiên `cho-review` > `can-chot` > `ai-lam`, `lech` khi ≥ 2 nhãn `cot:*` hoặc nhãn lạ; không `cot:*`: `can-spec` → cột 1 khe spec, `cho-duyet-spec` → cột 2, `tram:escalation` → cột 2, `theo-plan` → hàng `theo-plan`; còn lại → `chua-cham`). `cho` = `bi_chan_boi`.
  - `hien_tren_bang(bead) -> bool`; `ly_do_khong_keo(bead, vt) -> str | None` (G2); `ly_do_khong_chot(bead, vt) -> str | None` (G3); `ly_do_khong_tra_loi(bead) -> str | None` (Q4/G21: chỉ bead `decision` đang hiện trên bảng — escalation hoặc decision mở).
  - `the_bead(du_an: str, bead, theo_id) -> dict` — đúng khoá của `The` trong "Hợp đồng JSON" (có `tra_loi_duoc`).
  - `cham_gan_nhat(kho, du_an: str, bead_id: str) -> SuKien | None` — `cham_cot.ket_qua` mới nhất **không** có `huy`.

- [ ] **Step 1: Viết test thất bại**

`tests/test_suy_cot.py`:

```python
from bead_gia import bead
from tram.su_kien.kho import KhoSuKien
from tram.suy.cot import (ViTri, cham_gan_nhat, hien_tren_bang, ly_do_khong_chot, ly_do_khong_keo,
                          ly_do_khong_tra_loi, suy_vi_tri, the_bead)
from tram.suy.lam_sach import lam_sach


def vt(*labels, **kw):
    return suy_vi_tri(bead(labels=labels, **kw), {})


def test_cot_theo_nhan():
    assert vt("cot:ai-lam") == ViTri("ai-lam", True, False, False, ())
    assert vt("cot:can-chot").hang == "can-chot"
    assert vt("cot:cho-review").hang == "cho-review"


def test_nhieu_nhan_cot_chon_an_toan_va_bao_lech():
    v = vt("cot:ai-lam", "cot:cho-review")
    assert v.hang == "cho-review" and v.lech and v.tu_nhan_cot
    v = vt("cot:la")
    assert v.hang == "chua-cham" and v.lech and not v.tu_nhan_cot


def test_nhan_luong_va_escalation():
    assert vt("can-spec") == ViTri("ai-lam", False, False, True, ())
    assert vt("cho-duyet-spec").hang == "can-chot"
    assert vt("theo-plan").hang == "theo-plan"
    assert vt("tram:escalation", issue_type="decision").hang == "can-chot"
    assert vt().hang == "chua-cham" and vt("b2b").hang == "chua-cham"


def test_epic_hang_rieng_ke_ca_co_nhan_cot():
    assert vt("cot:ai-lam", issue_type="epic").hang == "epic"


def test_bi_chan_mo_va_fail_closed():
    b = bead("hr-1", labels=["cot:ai-lam"], chan_boi=["hr-2", "hr-3", "hr-9"])
    theo_id = {x.id: x for x in (b, bead("hr-2"), bead("hr-3", status="closed"))}
    assert suy_vi_tri(b, theo_id).cho == ("hr-2", "hr-9")
    t = the_bead("hr", b, theo_id)
    assert t["mo"] is True and t["cho"] == ["hr-2", "hr-9"] and t["hang"] == "ai-lam"


def test_the_bead_truong_va_lam_sach():
    b = bead("hr-1", title="Sửa‮ giá\x00", labels=["cot:can-chot", "cot-khoa", "co-do"], priority=2,
             updated_at="2026-10-13T05:00:00Z")
    assert the_bead("hr", b, {"hr-1": b}) == {
        "du_an": "hr", "id": "hr-1", "tieu_de": "Sửa giá", "loai": "task", "uu_tien": 2, "hang": "can-chot",
        "mo": False, "cho": [], "khoa": True, "co_do": True, "lech": False, "khe_spec": False,
        "keo_duoc": True, "chot_duoc": True, "tra_loi_duoc": False, "updated_at": "2026-10-13T05:00:00Z"}


def _ly_do(ham, *labels, **kw):
    b = bead(labels=labels, **kw)
    return ham(b, suy_vi_tri(b, {}))


def test_luat_keo():
    assert _ly_do(ly_do_khong_keo, "cot:ai-lam") is None
    assert _ly_do(ly_do_khong_keo, "cot:can-chot", "cot-khoa") is None
    for labels, kw in ((("cot:ai-lam",), {"issue_type": "epic"}), (("cot:cho-review",), {}), ((), {}),
                       (("can-spec",), {}), (("cot:can-chot", "tram:escalation"), {"issue_type": "decision"}),
                       (("cot:ai-lam",), {"status": "closed"}), (("cot:ai-lam", "theo-plan"), {})):
        assert _ly_do(ly_do_khong_keo, *labels, **kw), labels


def test_luat_chot():
    assert _ly_do(ly_do_khong_chot, "cot:can-chot", "cot-khoa") is None
    for labels, kw in ((("cot:ai-lam",), {}), (("cho-duyet-spec",), {}), (("cot:can-chot",), {"issue_type": "decision"}),
                       (("cot:can-chot",), {"issue_type": "epic"}), (("cot:can-chot", "tram:escalation"), {}),
                       (("cot:can-chot",), {"status": "deferred"})):
        assert _ly_do(ly_do_khong_chot, *labels, **kw), labels


def test_luat_tra_loi():
    assert ly_do_khong_tra_loi(bead(issue_type="decision", labels=["tram:escalation"])) is None
    assert ly_do_khong_tra_loi(bead(issue_type="decision", labels=["cot:can-chot"])) is None   # decision mở
    for kw in ({"issue_type": "task"}, {"issue_type": "decision", "status": "closed"},
               {"issue_type": "decision", "status": "deferred"}):
        assert ly_do_khong_tra_loi(bead(**kw)), kw


def test_hien_tren_bang():
    assert hien_tren_bang(bead(status="in_progress")) and hien_tren_bang(bead(status="blocked"))
    assert not hien_tren_bang(bead(status="closed")) and not hien_tren_bang(bead(status="deferred"))


def test_cham_gan_nhat_bo_ket_qua_bi_huy(tmp_path):
    k = KhoSuKien(tmp_path / "sk.db")
    assert cham_gan_nhat(k, "hr", "hr-1") is None
    k.ghi("hr", "cham_cot.ket_qua", {"ly_do": "đúng"}, bead_id="hr-1")
    k.ghi("hr", "cham_cot.ket_qua", {"ly_do": "huỷ", "huy": "bead_doi_khi_cham"}, bead_id="hr-1")
    assert cham_gan_nhat(k, "hr", "hr-1").du_lieu["ly_do"] == "đúng"


def test_lam_sach_loc_ky_tu():
    assert lam_sach("a\x00b‮c⁦d​e­f\ng\th") == "abcdef\ng\th"
    assert lam_sach("Tiếng Việt có dấu") == "Tiếng Việt có dấu"


def test_lam_sach_cat_do_dai_va_none():
    assert lam_sach("x" * 10, 5) == "xxxx…"
    assert lam_sach(None) == "" and lam_sach("abc", 5) == "abc"
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_suy_cot.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'tram.suy.cot'`.

- [ ] **Step 3: Viết mã**

`tram/suy/lam_sach.py`:

```python
"""Làm sạch chuỗi trước khi trả cho trình duyệt (spec 2 §4 mục 4 — bài học ruflo)."""
import unicodedata

LOAI_BO = {"Cc", "Cf", "Cs", "Co"}   # điều khiển, định dạng (bidi, zero-width, soft hyphen), surrogate, dùng riêng
GIU = {"\n", "\t"}


def lam_sach(s: str | None, toi_da: int = 500) -> str:
    if not s:
        return ""
    sach = "".join(c for c in str(s) if c in GIU or unicodedata.category(c) not in LOAI_BO)
    return sach if len(sach) <= toi_da else sach[: toi_da - 1] + "…"
```

`tram/suy/cot.py`:

```python
"""Suy vị trí bead trên bảng lúc đọc (spec 2 §5.1, kiến trúc Q12) — không lưu trạng thái riêng."""
from dataclasses import dataclass

from tram.beads.mo_hinh import Bead
from tram.cham_cot.ghi import NHAN_KHOA
from tram.cham_cot.luat_cung import bi_chan_boi
from tram.suy.lam_sach import lam_sach

HANG = ("ai-lam", "can-chot", "cho-review", "chua-cham", "epic", "theo-plan")
NHAN_COT_HANG = {"cot:ai-lam": "ai-lam", "cot:can-chot": "can-chot", "cot:cho-review": "cho-review"}
NHAN_LUONG = {"can-spec", "cho-duyet-spec", "theo-plan"}
NHAN_ESCALATION = "tram:escalation"
NHAN_CO_DO = "co-do"
TRANG_THAI_HIEN = {"open", "in_progress", "blocked"}


@dataclass(frozen=True)
class ViTri:
    hang: str
    tu_nhan_cot: bool      # vị trí đến từ nhãn cot:* (chỉ khi đó mới được kéo / chốt)
    lech: bool             # ≥ 2 nhãn cot:* hoặc nhãn cot:* lạ
    khe_spec: bool         # feature can-spec: hiện mờ ở cột 1
    cho: tuple[str, ...]   # bị chặn bởi (kể cả ID không có trong snapshot — fail-closed)


def hien_tren_bang(bead: Bead) -> bool:
    return bead.status in TRANG_THAI_HIEN


def suy_vi_tri(bead: Bead, theo_id: dict[str, Bead]) -> ViTri:
    cho = bi_chan_boi(bead, theo_id)
    so_cot = sum(1 for n in bead.labels if n.startswith("cot:"))
    if bead.issue_type == "epic":
        return ViTri("epic", False, so_cot > 1, False, cho)
    nhan = bead.nhan_cot()
    if nhan is not None:
        hang = NHAN_COT_HANG.get(nhan)
        return ViTri(hang or "chua-cham", hang is not None, so_cot > 1 or hang is None, False, cho)
    tap = set(bead.labels)
    if "can-spec" in tap:
        return ViTri("ai-lam", False, False, True, cho)
    if "cho-duyet-spec" in tap or NHAN_ESCALATION in tap:
        return ViTri("can-chot", False, False, False, cho)
    if "theo-plan" in tap:
        return ViTri("theo-plan", False, False, False, cho)
    return ViTri("chua-cham", False, False, False, cho)


def _ngoai_luong(bead: Bead) -> str | None:
    if bead.status not in TRANG_THAI_HIEN:
        return "Bead đã đóng hoặc hoãn"
    if NHAN_ESCALATION in bead.labels or NHAN_LUONG & set(bead.labels):
        return "Bead trong luồng feature / escalation do phần 4 quản"
    return None


def ly_do_khong_keo(bead: Bead, vt: ViTri) -> str | None:
    if bead.issue_type == "epic":
        return "Epic không được kéo (#9)"
    if (ly_do := _ngoai_luong(bead)) is not None:
        return ly_do
    if not vt.tu_nhan_cot or vt.hang not in ("ai-lam", "can-chot"):
        return "Chỉ kéo giữa cột 1 và cột 2"
    return None


def ly_do_khong_chot(bead: Bead, vt: ViTri) -> str | None:
    if bead.issue_type in ("epic", "decision"):
        return "Không chốt epic / bead quyết định"
    if (ly_do := _ngoai_luong(bead)) is not None:
        return ly_do
    if not vt.tu_nhan_cot or vt.hang != "can-chot":
        return "Chỉ chốt bead ở cột 2"
    return None


def ly_do_khong_tra_loi(bead: Bead) -> str | None:
    """Nút Trả lời (spec 2 §5.2): escalation hoặc decision mở — đóng chính decision kèm câu trả lời."""
    if bead.issue_type != "decision" or not hien_tren_bang(bead):
        return "Chỉ trả lời escalation / decision đang mở"
    return None


def the_bead(du_an: str, bead: Bead, theo_id: dict[str, Bead]) -> dict:
    vt = suy_vi_tri(bead, theo_id)
    return {"du_an": du_an, "id": bead.id, "tieu_de": lam_sach(bead.title, 200), "loai": bead.issue_type,
            "uu_tien": bead.priority, "hang": vt.hang, "mo": bool(vt.cho) or vt.khe_spec, "cho": list(vt.cho),
            "khoa": NHAN_KHOA in bead.labels, "co_do": NHAN_CO_DO in bead.labels, "lech": vt.lech,
            "khe_spec": vt.khe_spec, "keo_duoc": ly_do_khong_keo(bead, vt) is None,
            "chot_duoc": ly_do_khong_chot(bead, vt) is None, "tra_loi_duoc": ly_do_khong_tra_loi(bead) is None,
            "updated_at": bead.updated_at}


def cham_gan_nhat(kho, du_an: str, bead_id: str):
    """`cham_cot.ket_qua` mới nhất không bị huỷ (plan 1a G8: `huy = bead_doi_khi_cham`)."""
    return kho.moi_nhat(du_an, bead_id, "cham_cot.ket_qua", dieu_kien=lambda s: not s.du_lieu.get("huy"))
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_suy_cot.py -q` → Expected: `13 passed`.

- [ ] **Step 5: Commit**

```bash
git add tram/suy/lam_sach.py tram/suy/cot.py tests/test_suy_cot.py
git commit -m "feat(suy): suy cột lúc đọc, luật kéo/chốt/trả lời, làm sạch chuỗi hiển thị"
```

---

### Task 9: Suy Phê duyệt, chi tiết bead, trạng thái trạm

**Độ khó:** `kho` (gom nhiều nguồn, thứ tự) · **Song song:** đợt 3 — chạy cùng Task 13, 14, 15, 16, 21, 25. **Phải xong trước:** Task 2 (`SuKien.id`, `cua_bead`), Task 7 (`tom_tat_ban_giao`), Task 8. Task 12 cần task này.

**Files:**
- Create: `tram/suy/chi_tiet.py`, `tram/suy/phe_duyet.py`, `tram/suy/trang_thai.py`
- Test: `tests/test_suy_phe_duyet.py`

**Interfaces:**
- Consumes: `tom_tat_ban_giao` (Task 7); `the_bead`, `cham_gan_nhat`, `NHAN_CO_DO`, `NHAN_ESCALATION`, `TRANG_THAI_HIEN` (Task 8); `lam_sach` (Task 8); `KhoSuKien.gan_day`, `.moi_nhat`, `.moi_nhat_cac_loai`, `.cua_bead` (Task 2).
- Produces:
  - `ban_giao_sach(tt: dict | None) -> dict | None`; `chi_tiet_bead(du_an, bead, theo_id, kho) -> dict` (khoá như `GET /api/bead`).
  - `THU_TU = ("escalation", "decision", "co-do", "he", "cho-review", "spec")` (G15, G21: bead `decision` mở không mang `tram:escalation` → mục `decision`); `gom_phe_duyet(cac_du_an: list[str], theo_du_an: dict[str, list[Bead]], kho) -> list[dict]` (khoá mục như `GET /api/phe-duyet`; dự án đọc `bd` lỗi vẫn có mục `quet.loi`).
  - `trang_thai_du_an(kho, du_an) -> {ten, quet_cuoi, loi_gan_nhat}`; `trang_thai_tram(kho, cac_du_an, *, estop_bat: bool) -> {estop, du_an: [...]}`.

Luật "Hệ cần xem" (spec §5.2): bead có `cham_cot.bo_qua` mà sự kiện mới nhất trong (`cham_cot.bo_qua`, `cham_cot.ket_qua` **không bị huỷ**, `cham_cot.thu_lai`) vẫn là `bo_qua`, bead còn mở; và dự án có `quet.loi` mới hơn `quet.xong` gần nhất. Cầu dao khe → 2b.

- [ ] **Step 1: Viết test thất bại**

`tests/test_suy_phe_duyet.py`:

```python
from bead_gia import bead, notes_ban_giao
from tram.su_kien.kho import KhoSuKien
from tram.suy.chi_tiet import chi_tiet_bead
from tram.suy.phe_duyet import gom_phe_duyet
from tram.suy.trang_thai import trang_thai_du_an, trang_thai_tram


def kho(tmp_path):
    return KhoSuKien(tmp_path / "sk.db")


def _beads():
    return [
        bead("hr-1", labels=["cot:cho-review"], notes=notes_ban_giao(), priority=2),
        bead("hr-2", issue_type="decision", labels=["tram:escalation"]),
        bead("hr-3", labels=["co-do", "cot:cho-review"], priority=1),
        bead("hr-4", issue_type="feature", labels=["cho-duyet-spec"]),
        bead("hr-5", status="closed", labels=["cot:cho-review"]),
        bead("hr-6", labels=["cot:ai-lam"]),
        bead("hr-7", labels=["cot:ai-lam"]),
        bead("hr-8", issue_type="decision", labels=["cot:can-chot"]),
        bead("hr-9", issue_type="decision", status="closed"),
    ]


def test_gom_phe_duyet_du_loai_va_thu_tu(tmp_path):
    k = kho(tmp_path)
    k.ghi("hr", "cham_cot.loi", {"loi": "API hết hạn mức"}, bead_id="hr-6")
    k.ghi("hr", "cham_cot.bo_qua", {"vi_sao": "loi_lien_tiep"}, bead_id="hr-6")
    k.ghi("hr", "cham_cot.ket_qua", {"huy": "bead_doi_khi_cham", "da_ghi": False}, bead_id="hr-6")
    k.ghi("hr", "cham_cot.bo_qua", {"vi_sao": "loi_lien_tiep"}, bead_id="hr-7")
    k.ghi("hr", "cham_cot.thu_lai", {"ma_thao_tac": "m"}, bead_id="hr-7")
    k.ghi("hr", "quet.xong", {})
    k.ghi("hr", "quet.loi", {"loi": "bd list: JSON hỏng"})
    muc = gom_phe_duyet(["hr"], {"hr": _beads()}, k)
    assert [(m["loai"], m["bead_id"]) for m in muc] == [
        ("escalation", "hr-2"), ("decision", "hr-8"), ("co-do", "hr-3"), ("he", None), ("he", "hr-6"),
        ("cho-review", "hr-3"), ("cho-review", "hr-1"), ("spec", "hr-4")]
    he = {m["bead_id"]: m["chi_tiet"] for m in muc if m["loai"] == "he"}
    assert he["hr-6"]["su_kien"] == "cham_cot.bo_qua" and he["hr-6"]["loi"] == "API hết hạn mức"
    assert he[None] == {"su_kien": "quet.loi", "luc": he[None]["luc"], "loi": "bd list: JSON hỏng"}
    cr = {m["bead_id"]: m["chi_tiet"] for m in muc if m["loai"] == "cho-review"}
    assert cr["hr-1"]["pr"] == "https://github.com/o/r/pull/7" and cr["hr-1"]["loi"] == []
    assert cr["hr-3"]["loi"] == ["Thiếu khối bàn giao"] and cr["hr-3"]["pr"] is None


def test_quet_loi_cu_hon_quet_xong_khong_hien(tmp_path):
    k = kho(tmp_path)
    k.ghi("hr", "quet.loi", {"loi": "x"})
    k.ghi("hr", "quet.xong", {})
    assert gom_phe_duyet(["hr"], {"hr": []}, k) == []


def test_du_an_doc_bd_loi_van_hien_quet_loi(tmp_path):
    k = kho(tmp_path)
    k.ghi("web", "quet.loi", {"loi": "bd hỏng"})
    muc = gom_phe_duyet(["hr", "web"], {"hr": []}, k)
    assert [(m["du_an"], m["loai"]) for m in muc] == [("web", "he")]


def test_trang_thai(tmp_path):
    k = kho(tmp_path)
    assert trang_thai_du_an(k, "hr") == {"ten": "hr", "quet_cuoi": None, "loi_gan_nhat": None}
    k.ghi("hr", "quet.xong", {})
    k.ghi("hr", "cham_cot.loi", {"loi": "cũ"}, bead_id="hr-1")
    k.ghi("hr", "quet.loi", {"loi": "mới‮"})
    tt = trang_thai_du_an(k, "hr")
    assert tt["quet_cuoi"] is not None
    assert tt["loi_gan_nhat"]["loai"] == "quet.loi" and tt["loi_gan_nhat"]["loi"] == "mới"
    assert trang_thai_tram(k, ["hr"], estop_bat=True) == {"estop": True, "du_an": [tt]}


def test_chi_tiet_bead(tmp_path):
    k = kho(tmp_path)
    b = bead("hr-1", labels=["cot:can-chot"], description="Mô tả\x07", acceptance_criteria="Test pass",
             notes=notes_ban_giao())
    k.ghi("hr", "cham_cot.ket_qua", {"cot": "can-chot", "ly_do": "Chạm giá", "cau_hoi": ["Có VAT?"], "da_ghi": True},
          bead_id="hr-1")
    k.ghi("hr", "cham_cot.ket_qua", {"cot": "ai-lam", "ly_do": "huỷ", "cau_hoi": [], "da_ghi": False,
                                     "huy": "bead_doi_khi_cham"}, bead_id="hr-1")
    k.ghi("hr", "cot.dai_ca_sua", {"vi_sao": "x"}, bead_id="hr-1")
    ct = chi_tiet_bead("hr", b, {"hr-1": b}, k)
    assert ct["the"]["id"] == "hr-1" and ct["mo_ta"] == "Mô tả" and ct["nghiem_thu"] == "Test pass"
    assert ct["cham_gan_nhat"]["ly_do"] == "Chạm giá" and ct["cham_gan_nhat"]["cau_hoi"] == ["Có VAT?"]
    assert ct["ban_giao"]["pr"] == "https://github.com/o/r/pull/7"
    assert [s["loai"] for s in ct["dong_thoi_gian"]] == ["cham_cot.ket_qua", "cham_cot.ket_qua", "cot.dai_ca_sua"]
    assert ct["dong_thoi_gian"][2]["tom_tat"] == '{"vi_sao": "x"}'


def test_chi_tiet_khong_co_cham_va_ban_giao(tmp_path):
    b = bead("hr-1")
    ct = chi_tiet_bead("hr", b, {"hr-1": b}, kho(tmp_path))
    assert ct["cham_gan_nhat"] is None and ct["ban_giao"] is None and ct["dong_thoi_gian"] == []
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_suy_phe_duyet.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'tram.suy.chi_tiet'`.

- [ ] **Step 3: Viết mã**

`tram/suy/chi_tiet.py`:

```python
"""Ngăn bên của bead (spec 2 §5.1): lý do chấm, câu hỏi, mô tả, nghiệm thu, bàn giao, dòng thời gian."""
import json

from tram.ban_giao.doc import tom_tat_ban_giao
from tram.suy.cot import cham_gan_nhat, the_bead
from tram.suy.lam_sach import lam_sach


def ban_giao_sach(tt: dict | None) -> dict | None:
    if tt is None:
        return None
    return {"pr": tt["pr"], **{k: lam_sach(tt[k], 200) or None for k in ("nhanh", "commit", "file_ban_giao")},
            "loi": [lam_sach(x, 300) for x in tt["loi"]]}


def chi_tiet_bead(du_an: str, bead, theo_id: dict, kho) -> dict:
    cham = cham_gan_nhat(kho, du_an, bead.id)
    return {
        "the": the_bead(du_an, bead, theo_id),
        "mo_ta": lam_sach(bead.description, 8000),
        "nghiem_thu": lam_sach(bead.acceptance_criteria, 4000),
        "cham_gan_nhat": None if cham is None else {
            "luc": cham.luc, "cot": cham.du_lieu.get("cot"), "ly_do": lam_sach(cham.du_lieu.get("ly_do"), 1000),
            "cau_hoi": [lam_sach(q, 500) for q in cham.du_lieu.get("cau_hoi") or []]},
        "ban_giao": ban_giao_sach(tom_tat_ban_giao(bead.notes)),
        "dong_thoi_gian": [
            {"id": s.id, "luc": s.luc, "loai": s.loai, "tac_nhan": s.tac_nhan,
             "tom_tat": lam_sach(json.dumps(s.du_lieu, ensure_ascii=False), 300)}
            for s in kho.cua_bead(du_an, bead.id)],
    }
```

`tram/suy/phe_duyet.py`:

```python
"""Gom việc chờ Đại ca cho trang Phê duyệt (spec 2 §5.2) — tính lúc đọc từ beads + sự kiện."""
from tram.ban_giao.doc import tom_tat_ban_giao
from tram.beads.mo_hinh import Bead
from tram.suy.chi_tiet import ban_giao_sach
from tram.suy.cot import NHAN_CO_DO, NHAN_ESCALATION, TRANG_THAI_HIEN
from tram.suy.lam_sach import lam_sach

THU_TU = ("escalation", "decision", "co-do", "he", "cho-review", "spec")
HET_BO_QUA = ("cham_cot.bo_qua", "cham_cot.ket_qua", "cham_cot.thu_lai")


def _khong_huy(s) -> bool:
    """`ket_qua{huy}` không phải lần chấm được (plan 1a G8) — không gỡ bead khỏi 'Hệ cần xem'."""
    return not (s.loai == "cham_cot.ket_qua" and s.du_lieu.get("huy"))


def _muc(loai: str, du_an: str, b: Bead | None, chi_tiet: dict | None = None) -> dict:
    return {"loai": loai, "du_an": du_an, "bead_id": b.id if b else None,
            "tieu_de": lam_sach(b.title, 200) if b else "", "uu_tien": b.priority if b else None,
            "updated_at": b.updated_at if b else None, "chi_tiet": chi_tiet or {}}


def _ban_giao(b: Bead) -> dict:
    return ban_giao_sach(tom_tat_ban_giao(b.notes)) or {
        "pr": None, "nhanh": None, "commit": None, "file_ban_giao": None, "loi": ["Thiếu khối bàn giao"]}


def muc_tu_beads(du_an: str, beads: list[Bead]) -> list[dict]:
    ra = []
    for b in beads:
        if b.status not in TRANG_THAI_HIEN:
            continue
        nhan = set(b.labels)
        if NHAN_ESCALATION in nhan:
            ra.append(_muc("escalation", du_an, b))
        elif b.issue_type == "decision":            # decision mở: cùng nút Trả lời (spec 2 §5.2)
            ra.append(_muc("decision", du_an, b))
        if NHAN_CO_DO in nhan:
            ra.append(_muc("co-do", du_an, b, _ban_giao(b)))
        if "cot:cho-review" in nhan:
            ra.append(_muc("cho-review", du_an, b, _ban_giao(b)))
        if "cho-duyet-spec" in nhan:
            ra.append(_muc("spec", du_an, b))
    return ra


def muc_he(du_an: str, kho, theo_id: dict[str, Bead]) -> list[dict]:
    ra, da_xet = [], set()
    for s in kho.gan_day(du_an, "cham_cot.bo_qua", 100):
        if s.bead_id in da_xet:
            continue
        da_xet.add(s.bead_id)
        b = theo_id.get(s.bead_id)
        cuoi = kho.moi_nhat_cac_loai(du_an, s.bead_id, HET_BO_QUA, dieu_kien=_khong_huy)
        if b is None or b.status not in TRANG_THAI_HIEN or cuoi is None or cuoi.loai != "cham_cot.bo_qua":
            continue
        loi = kho.moi_nhat(du_an, b.id, "cham_cot.loi")
        ra.append(_muc("he", du_an, b, {"su_kien": "cham_cot.bo_qua", "luc": cuoi.luc,
                                        "loi": lam_sach(loi.du_lieu.get("loi") if loi else "", 300)}))
    loi_q, xong = kho.gan_day(du_an, "quet.loi", 1), kho.gan_day(du_an, "quet.xong", 1)
    if loi_q and (not xong or loi_q[0].id > xong[0].id):
        ra.append(_muc("he", du_an, None, {"su_kien": "quet.loi", "luc": loi_q[0].luc,
                                           "loi": lam_sach(loi_q[0].du_lieu.get("loi"), 300)}))
    return ra


def gom_phe_duyet(cac_du_an: list[str], theo_du_an: dict[str, list[Bead]], kho) -> list[dict]:
    ra = []
    for du_an in cac_du_an:
        beads = theo_du_an.get(du_an, [])
        ra += muc_tu_beads(du_an, beads) + muc_he(du_an, kho, {b.id: b for b in beads})
    return sorted(ra, key=lambda m: (THU_TU.index(m["loai"]), 9 if m["uu_tien"] is None else m["uu_tien"],
                                     m["updated_at"] or "", m["du_an"], m["bead_id"] or ""))
```

`tram/suy/trang_thai.py`:

```python
"""Thanh trạng thái trạm chủ (spec 2 §5.3) và trang Dự án: lần quét cuối, lỗi gần nhất."""
from tram.suy.lam_sach import lam_sach


def _loi_gan_nhat(kho, du_an: str) -> dict | None:
    ds = [s for loai in ("cham_cot.loi", "quet.loi") for s in kho.gan_day(du_an, loai, 1)]
    if not ds:
        return None
    s = max(ds, key=lambda x: x.id)
    return {"luc": s.luc, "loai": s.loai, "loi": lam_sach(s.du_lieu.get("loi"), 200), "bead_id": s.bead_id}


def trang_thai_du_an(kho, du_an: str) -> dict:
    cuoi = kho.gan_day(du_an, "quet.xong", 1)
    return {"ten": du_an, "quet_cuoi": cuoi[0].luc if cuoi else None, "loi_gan_nhat": _loi_gan_nhat(kho, du_an)}


def trang_thai_tram(kho, cac_du_an: list[str], *, estop_bat: bool) -> dict:
    return {"estop": estop_bat, "du_an": [trang_thai_du_an(kho, t) for t in cac_du_an]}
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_suy_phe_duyet.py -q` → Expected: `6 passed`.

- [ ] **Step 5: Commit**

```bash
git add tram/suy/chi_tiet.py tram/suy/phe_duyet.py tram/suy/trang_thai.py tests/test_suy_phe_duyet.py
git commit -m "feat(suy): gom Phê duyệt theo độ gấp, chi tiết bead, trạng thái trạm"
```

---

### Task 10: Danh tính Tailscale + chống CSRF + header an toàn (CSP) + kiểm `Host`

**Độ khó:** `de` · **Song song:** đợt 2 — chạy cùng Task 4, 6, 8, 11, 20, 24. **Phải xong trước:** Task 1 (fastapi, `asgi_gia`), Task 5 (`CauHinhTram`). Task 12, 17 cần task này.

Middleware CSP + `Host` nằm ở task này (cùng file bảo mật, test bằng app tối thiểu); Task 12 nối vào `tao_app` và kiểm trên app thật (C1, Q1/G17 — spec §4 mục 6).

**Files:**
- Create: `tram/api/bao_mat.py`
- Test: `tests/test_bao_mat.py`

**Interfaces:**
- Consumes: `CauHinhTram` (Task 5); `request.app.state.pt.cau_hinh` (đặt ở Task 12; test dựng tay).
- Produces: `HEADER_DANH_TINH = "tailscale-user-login"`; `la_dai_ca(headers: Mapping[str, str], ch) -> bool` (khoá header viết thường); `kiem_ghi(headers, ch) -> str | None` (lý do từ chối hoặc `None`); `yeu_cau_ghi(request) -> None` (dependency FastAPI, ném `HTTPException(403)`; nhiều header danh tính → 403); `la_dai_ca_yeu_cau(request) -> bool`.
  - `CSP` (chuỗi đúng spec §4 mục 6), `HEADER_AN_TOAN` (CSP, `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer`, `X-Frame-Options: DENY`); `host_hop_le(ch, cong: int) -> frozenset[str]` (`127.0.0.1:<cong>`, `localhost:<cong>`, + `<ten_may_b>`, `<ten_may_b>:443` khi có; viết thường — G17, G22); `GiuaAnToan(app, *, host)` (middleware ASGI thuần: `Host` lạ → 421 `{"loi": "Host không hợp lệ"}`, mọi phản hồi kể cả 404/421/SSE thêm `HEADER_AN_TOAN`); `them_header_an_toan(app, ch, *, cong: int) -> None`.

- [ ] **Step 1: Viết test thất bại**

`tests/test_bao_mat.py`:

```python
from types import SimpleNamespace

import pytest
from fastapi import Depends, FastAPI, HTTPException
from starlette.datastructures import Headers

from asgi_gia import goi
from tram.api.bao_mat import CSP, host_hop_le, kiem_ghi, la_dai_ca, them_header_an_toan, yeu_cau_ghi
from tram.cau_hinh.tram import CauHinhTram

CH = CauHinhTram(dai_ca_logins=("dai-ca@example.com",), ten_may_b="may-b.tail.ts.net")
DU = {"tailscale-user-login": "dai-ca@example.com", "x-tram": "1", "origin": "https://may-b.tail.ts.net"}


def test_la_dai_ca():
    assert la_dai_ca(DU, CH)
    assert not la_dai_ca({}, CH)
    assert not la_dai_ca({**DU, "tailscale-user-login": "khac@x.y"}, CH)
    assert not la_dai_ca(DU, CauHinhTram())          # chưa cấu hình danh sách → không ai ghi được


def test_kiem_ghi_tung_dieu_kien():
    assert kiem_ghi(DU, CH) is None
    assert "Chỉ đọc" in kiem_ghi({k: v for k, v in DU.items() if k != "tailscale-user-login"}, CH)
    assert "X-Tram" in kiem_ghi({**DU, "x-tram": "0"}, CH)
    assert "Origin" in kiem_ghi({**DU, "origin": "https://evil.example"}, CH)
    assert "Origin" in kiem_ghi({k: v for k, v in DU.items() if k != "origin"}, CH)
    assert "ten_may_b" in kiem_ghi(DU, CauHinhTram(dai_ca_logins=("dai-ca@example.com",)))


def _app():
    app = FastAPI()
    app.state.pt = SimpleNamespace(cau_hinh=CH)

    @app.post("/ghi", dependencies=[Depends(yeu_cau_ghi)])
    def ghi():
        return {"ok": True}

    return app


def test_dependency_qua_asgi():
    hdr = {"Tailscale-User-Login": "dai-ca@example.com", "X-Tram": "1", "Origin": "https://may-b.tail.ts.net"}
    assert goi(_app(), "POST", "/ghi", json_body={}, headers=hdr).json() == {"ok": True}
    r = goi(_app(), "POST", "/ghi", json_body={}, headers={"X-Tram": "1"})
    assert r.status == 403 and "Chỉ đọc" in r.json()["detail"]


def test_hai_header_danh_tinh_bi_tu_choi():
    raw = [(b"tailscale-user-login", b"dai-ca@example.com"), (b"tailscale-user-login", b"khac@x.y"),
           (b"x-tram", b"1"), (b"origin", b"https://may-b.tail.ts.net")]
    req = SimpleNamespace(headers=Headers(raw=raw),
                          app=SimpleNamespace(state=SimpleNamespace(pt=SimpleNamespace(cau_hinh=CH))))
    with pytest.raises(HTTPException) as e:
        yeu_cau_ghi(req)
    assert e.value.status_code == 403


def _app_doc():
    app = FastAPI()
    app.state.pt = SimpleNamespace(cau_hinh=CH)

    @app.get("/doc")
    def doc():
        return {"ok": True}

    them_header_an_toan(app, CH, cong=7700)
    return app


def test_header_an_toan_tren_moi_phan_hoi():
    assert "unsafe-eval" not in CSP and "unsafe-inline" not in CSP and "script-src 'self'" in CSP
    for duong, ma in (("/doc", 200), ("/khong-co", 404)):
        r = goi(_app_doc(), "GET", duong)
        assert r.status == ma and r.headers["content-security-policy"] == CSP
        assert r.headers["x-content-type-options"] == "nosniff" and r.headers["x-frame-options"] == "DENY"
        assert r.headers["referrer-policy"] == "no-referrer"


def test_host_ngoai_danh_sach_la_421():
    assert host_hop_le(CH, 7700) == {"127.0.0.1:7700", "localhost:7700", "may-b.tail.ts.net", "may-b.tail.ts.net:443"}
    assert host_hop_le(CauHinhTram(), 7701) == {"127.0.0.1:7701", "localhost:7701"}
    for host in ("127.0.0.1:7700", "localhost:7700", "MAY-B.tail.ts.net", "may-b.tail.ts.net:443"):
        assert goi(_app_doc(), "GET", "/doc", headers={"Host": host}).status == 200, host
    for host in ("evil.example", "evil.example:7700", "127.0.0.1:8080", ""):
        r = goi(_app_doc(), "GET", "/doc", headers={"Host": host})
        assert r.status == 421 and "content-security-policy" in r.headers, host
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_bao_mat.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'tram.api.bao_mat'`.

- [ ] **Step 3: Viết mã**

`tram/api/bao_mat.py`:

```python
"""Danh tính Tailscale + chống CSRF cho API ghi; header an toàn + kiểm Host cho mọi phản hồi (spec 2 §4 mục 2, 3, 6).

Lát 2a tin header `Tailscale-User-Login` do `tailscale serve` gắn. Header này giả được bởi mọi tiến trình
cục bộ gọi thẳng 127.0.0.1 (spec §4 mục 2b) — chấp nhận ở 2a vì chưa có thợ chạy trên B; phải thay trước 3a.
Hành vi header thật kiểm ở Task 26 (chờ #5).
"""
from collections.abc import Mapping

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from tram.cau_hinh.tram import CauHinhTram

HEADER_DANH_TINH = "tailscale-user-login"
CSP = ("default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; "
       "font-src 'self'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'")
HEADER_AN_TOAN = [(b"content-security-policy", CSP.encode()), (b"x-content-type-options", b"nosniff"),
                  (b"referrer-policy", b"no-referrer"), (b"x-frame-options", b"DENY")]


def la_dai_ca(headers: Mapping[str, str], ch: CauHinhTram) -> bool:
    login = (headers.get(HEADER_DANH_TINH) or "").strip()
    return bool(login) and login in ch.dai_ca_logins


def kiem_ghi(headers: Mapping[str, str], ch: CauHinhTram) -> str | None:
    if not la_dai_ca(headers, ch):
        return "Chỉ đọc: yêu cầu không mang danh tính Đại ca (Tailscale-User-Login)"
    if headers.get("x-tram") != "1":
        return "Thiếu header X-Tram: 1"
    if not ch.ten_may_b:
        return "Chưa cấu hình ten_may_b trong ~/.tram/cau-hinh.yaml — từ chối mọi thao tác ghi"
    if headers.get("origin") != f"https://{ch.ten_may_b}":
        return "Origin không khớp máy B"
    return None


def _header(request) -> dict[str, str]:
    return {k.lower(): v for k, v in request.headers.items()}


def yeu_cau_ghi(request: Request) -> None:
    if len(request.headers.getlist(HEADER_DANH_TINH)) > 1:
        raise HTTPException(status_code=403, detail="Nhiều header danh tính — từ chối")
    loi = kiem_ghi(_header(request), request.app.state.pt.cau_hinh)
    if loi:
        raise HTTPException(status_code=403, detail=loi)


def la_dai_ca_yeu_cau(request: Request) -> bool:
    return (len(request.headers.getlist(HEADER_DANH_TINH)) == 1
            and la_dai_ca(_header(request), request.app.state.pt.cau_hinh))


def host_hop_le(ch: CauHinhTram, cong: int) -> frozenset[str]:
    """Host trình duyệt được dùng: localhost (cổng tram-api) và tên máy B qua `tailscale serve` (Task 26 bước 7.4)."""
    ds = {f"127.0.0.1:{cong}", f"localhost:{cong}"}
    if ch.ten_may_b:
        ds |= {ch.ten_may_b.lower(), f"{ch.ten_may_b.lower()}:443"}
    return frozenset(ds)


class GiuaAnToan:
    """ASGI thuần: Host lạ → 421 (chống DNS rebinding đọc API); mọi phản hồi mang CSP chặt + header an toàn."""

    def __init__(self, app, *, host: frozenset[str]):
        self.app, self.host = app, host

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        async def gui(m):
            if m["type"] == "http.response.start":
                m = {**m, "headers": [*m.get("headers", []), *HEADER_AN_TOAN]}
            await send(m)

        host = dict(scope["headers"]).get(b"host", b"").decode("latin-1").lower()
        if host not in self.host:
            return await JSONResponse({"loi": "Host không hợp lệ"}, status_code=421)(scope, receive, gui)
        await self.app(scope, receive, gui)


def them_header_an_toan(app: FastAPI, ch: CauHinhTram, *, cong: int) -> None:
    app.add_middleware(GiuaAnToan, host=host_hop_le(ch, cong))
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_bao_mat.py -q` → Expected: `6 passed`. `wc -l tram/api/bao_mat.py` = 85.

- [ ] **Step 5: Commit**

```bash
git add tram/api/bao_mat.py tests/test_bao_mat.py
git commit -m "feat(api): danh tính Tailscale-User-Login, X-Tram, Origin; CSP chặt + header an toàn, Host lạ → 421"
```

---

### Task 11: Bộ đệm beads theo dự án

**Độ khó:** `de` · **Song song:** đợt 2 — chạy cùng Task 4, 6, 8, 10, 20, 24. **Phải xong trước:** Task 1 (`bd_gia`). Task 12, 18 cần task này.

**Files:**
- Create: `tram/api/bo_dem.py`
- Test: `tests/test_bo_dem.py`

**Interfaces:**
- Consumes: đối tượng có `tat_ca() -> list[Bead]` (`Bd` hoặc `BdGia`).
- Produces: `BoDemBeads(tao_bd: Callable[[str], Bd], *, tuoi_toi_da: float = 30.0, dong_ho: Callable[[], float] = time.monotonic)` với `lay(du_an) -> list[Bead]` (đọc lại khi cũ hơn `tuoi_toi_da` hoặc đã bị đánh dấu; `LoiBd` lan ra, lần sau thử lại), `danh_dau_cu(du_an) -> None`, `phien_ban(du_an) -> int` (tăng mỗi khi nội dung đọc được khác lần trước — so `(id, updated_at, status, nhãn)`; 0 khi chưa đọc).

- [ ] **Step 1: Viết test thất bại**

`tests/test_bo_dem.py`:

```python
import pytest

from bd_gia import BdGia
from bead_gia import bead
from tram.api.bo_dem import BoDemBeads
from tram.beads.bd import LoiBd


class DongHo:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


def _bo(bd, dh=None):
    return BoDemBeads(lambda ten: bd, dong_ho=dh or DongHo())


def test_dem_trong_30_giay_roi_doc_lai():
    bd, dh = BdGia([bead()]), DongHo()
    bo = _bo(bd, dh)
    bo.lay("hr")
    dh.t = 29
    bo.lay("hr")
    assert bd.so_lan("tat_ca") == 1
    dh.t = 30.5
    bo.lay("hr")
    assert bd.so_lan("tat_ca") == 2


def test_danh_dau_cu_thi_doc_lai_ngay():
    bd = BdGia([bead()])
    bo = _bo(bd)
    bo.lay("hr")
    bo.danh_dau_cu("hr")
    bo.lay("hr")
    assert bd.so_lan("tat_ca") == 2


def test_phien_ban_chi_tang_khi_noi_dung_doi():
    bd = BdGia([bead()])
    bo = _bo(bd)
    assert bo.phien_ban("hr") == 0
    bo.lay("hr")
    assert bo.phien_ban("hr") == 1
    bo.danh_dau_cu("hr")
    bo.lay("hr")
    assert bo.phien_ban("hr") == 1
    bd.beads["hr-1"] = bead(labels=["cot:ai-lam"], updated_at="2026-10-13T02:00:00Z")
    bo.danh_dau_cu("hr")
    bo.lay("hr")
    assert bo.phien_ban("hr") == 2


def test_loi_bd_lan_ra_va_lan_sau_thu_lai():
    bd = BdGia([bead()], ra_loi_truoc={"tat_ca": 1})
    bo = _bo(bd)
    with pytest.raises(LoiBd):
        bo.lay("hr")
    assert [b.id for b in bo.lay("hr")] == ["hr-1"]
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_bo_dem.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'tram.api.bo_dem'`.

- [ ] **Step 3: Viết mã**

`tram/api/bo_dem.py`:

```python
"""Bộ đệm beads theo dự án (spec 2 §3): tuổi tối đa 30 s, làm mới ngay khi bị đánh dấu cũ (G1)."""
import threading
import time
from collections.abc import Callable

from tram.beads.mo_hinh import Bead


class BoDemBeads:
    def __init__(self, tao_bd: Callable[[str], object], *, tuoi_toi_da: float = 30.0,
                 dong_ho: Callable[[], float] = time.monotonic):
        self._tao_bd, self._tuoi, self._dong_ho = tao_bd, tuoi_toi_da, dong_ho
        self._khoa = threading.Lock()
        self._du_lieu: dict[str, tuple[float, list[Bead]]] = {}
        self._cu: set[str] = set()
        self._dau: dict[str, tuple] = {}
        self._phien_ban: dict[str, int] = {}

    def lay(self, du_an: str) -> list[Bead]:
        with self._khoa:
            co = self._du_lieu.get(du_an)
            if co is not None and du_an not in self._cu and self._dong_ho() - co[0] < self._tuoi:
                return co[1]
            self._cu.discard(du_an)          # đánh dấu xảy ra trong lúc đọc sẽ được giữ cho lần sau
        beads = self._tao_bd(du_an).tat_ca()
        dau = tuple(sorted((b.id, b.updated_at, b.status, tuple(sorted(b.labels))) for b in beads))
        with self._khoa:
            self._du_lieu[du_an] = (self._dong_ho(), beads)
            if self._dau.get(du_an) != dau:
                self._dau[du_an] = dau
                self._phien_ban[du_an] = self._phien_ban.get(du_an, 0) + 1
        return beads

    def danh_dau_cu(self, du_an: str) -> None:
        with self._khoa:
            self._cu.add(du_an)

    def phien_ban(self, du_an: str) -> int:
        with self._khoa:
            return self._phien_ban.get(du_an, 0)
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_bo_dem.py -q` → Expected: `4 passed`.

- [ ] **Step 5: Commit**

```bash
git add tram/api/bo_dem.py tests/test_bo_dem.py
git commit -m "feat(api): bộ đệm beads theo dự án, tuổi tối đa 30 giây, phiên bản nội dung"
```

---

### Task 12: tram-api — ứng dụng, phụ thuộc, các `GET`, phục vụ file tĩnh

**Độ khó:** `kho` (ghép nhiều phần, ánh xạ lỗi) · **Song song:** đợt 4 — một mình (cần gần hết đợt 1–3). **Phải xong trước:** Task 1, 2, 4 (`loi.py`, `KhoThaoTac`), 5, 8, 9, 10, 11. Task 17, 18, 22 cần task này.

**Files:**
- Create: `tram/api/phu_thuoc.py`, `tram/api/app.py`, `tram/api/tuyen_doc.py`, `tests/api_gia.py`
- Test: `tests/test_api_doc.py`

**Interfaces:**
- Consumes: `BoDemBeads` (11); `la_dai_ca_yeu_cau`, `them_header_an_toan` (10); `CauHinhTram`, `nap_cau_hinh_tram` (5); `the_bead`, `hien_tren_bang`, `HANG` (8); `chi_tiet_bead`, `gom_phe_duyet`, `trang_thai_du_an`, `trang_thai_tram` (9); `KhoThaoTac`, `mo_kho_thao_tac`, `XungDot`, `KhongHopLe`, `ChuaHoTro`, `KhongThay`, `TAC_NHAN` (4); `Bd`, `LoiBd`, `KhongThayBead` (1, 6); `KhoSuKien.close`, `KhoThaoTac.close` (2, 4); `estop.dang_bat`; `liet_ke_du_an`, `nap_du_an`, `goc_repo`, `mo_kho`.
- Produces:
  - `PhuThuocApi(cau_hinh, cac_du_an: Callable[[], list[str]], tao_bd: Callable[[str], Bd], bo_dem: BoDemBeads, mo_kho: Callable[[], KhoSuKien], mo_kho_tt: Callable[[], KhoThaoTac], thu_muc_tinh: Path | None = None)`; `ID_RE`; `kiem_du_an_bead(pt, du_an: str, bead_id: str | None = None) -> None` (`KhongThay` / `KhongHopLe`); `phu_thuoc_that() -> PhuThuocApi` (dự án = `du-an/*.yaml` bỏ tên `_*`; `Bd(..., actor="dai-ca/dashboard")`; file tĩnh = `<repo>/frontend/dist` nếu có).
  - `tao_app(pt, *, cong: int = 7700) -> FastAPI` (gắn `them_header_an_toan(app, pt.cau_hinh, cong=cong)` đầu tiên; tắt `/docs`, `/openapi.json`); `MA_LOI` (ánh xạ lỗi → HTTP, thân `{"loi": ...}` đã làm sạch); `CAC_TUYEN` (tuple router — Task 17, 18 thêm).
  - `tram/api/tuyen_doc.py`: `router` với `GET /api/du-an`, `/api/cong-viec`, `/api/bead/{du_an}/{bead_id}`, `/api/phe-duyet`, `/api/chu/trang-thai` (đúng "Hợp đồng JSON"); mỗi route mở kho bằng `contextlib.closing(pt.mo_kho())` (N5, G24).
  - `tests/api_gia.py`: `MAY_B`, `LOGIN`, `DAI_CA` (header đủ quyền ghi), `tao_pt(tmp_path, bds, *, thu_muc_tinh=None) -> PhuThuocApi`, `tao_app_gia(tmp_path, bds, **kw) -> (FastAPI, PhuThuocApi)`.

- [ ] **Step 1: Viết công cụ test + test thất bại**

`tests/api_gia.py`:

```python
"""Dựng tram-api với phụ thuộc giả cho test (bd giả, SQLite tạm)."""
from pathlib import Path

from bd_gia import BdGia
from tram.api.app import tao_app
from tram.api.bo_dem import BoDemBeads
from tram.api.phu_thuoc import PhuThuocApi
from tram.cau_hinh.tram import CauHinhTram
from tram.su_kien.kho import KhoSuKien
from tram.thao_tac.kho import KhoThaoTac

MAY_B = "may-b.tail.ts.net"
LOGIN = "dai-ca@example.com"
DAI_CA = {"Tailscale-User-Login": LOGIN, "X-Tram": "1", "Origin": f"https://{MAY_B}"}


def tao_pt(tmp_path: Path, bds: dict[str, BdGia], *, thu_muc_tinh: Path | None = None) -> PhuThuocApi:
    db = tmp_path / "sk.db"
    return PhuThuocApi(
        cau_hinh=CauHinhTram(dai_ca_logins=(LOGIN,), ten_may_b=MAY_B),
        cac_du_an=lambda: sorted(bds),
        tao_bd=lambda ten: bds[ten],
        bo_dem=BoDemBeads(lambda ten: bds[ten]),
        mo_kho=lambda: KhoSuKien(db),
        mo_kho_tt=lambda: KhoThaoTac(db),
        thu_muc_tinh=thu_muc_tinh,
    )


def tao_app_gia(tmp_path: Path, bds: dict[str, BdGia], **kw):
    pt = tao_pt(tmp_path, bds, **kw)
    return tao_app(pt), pt
```

`tests/test_api_doc.py`:

```python
from api_gia import DAI_CA, tao_app_gia
from asgi_gia import goi
from bd_gia import BdGia
from bead_gia import bead
from tram.chu import estop


def _bds():
    return {
        "hr": BdGia([bead("hr-1", title="Sửa ‮giá", labels=["cot:ai-lam"], priority=1),
                     bead("hr-2", labels=["cot:cho-review"]),
                     bead("hr-3", status="closed", labels=["cot:ai-lam"])]),
        "web": BdGia([bead("web-1")], tien_to="web"),
    }


def test_cong_viec_tat_ca_va_loc(tmp_path):
    app, _ = tao_app_gia(tmp_path, _bds())
    r = goi(app, "GET", "/api/cong-viec")
    assert r.status == 200
    the = {(t["du_an"], t["id"]): t for t in r.json()["the"]}
    assert set(the) == {("hr", "hr-1"), ("hr", "hr-2"), ("web", "web-1")}
    assert the[("hr", "hr-1")]["hang"] == "ai-lam" and the[("hr", "hr-1")]["tieu_de"] == "Sửa giá"
    assert the[("web", "web-1")]["hang"] == "chua-cham"
    assert [t["id"] for t in goi(app, "GET", "/api/cong-viec?du_an=web").json()["the"]] == ["web-1"]


def test_du_an_khong_co_la_404(tmp_path):
    app, _ = tao_app_gia(tmp_path, _bds())
    r = goi(app, "GET", "/api/cong-viec?du_an=khong-co")
    assert r.status == 404 and "khong-co" in r.json()["loi"]


def test_du_an_dem_cot_va_quet_cuoi(tmp_path):
    app, pt = tao_app_gia(tmp_path, _bds())
    pt.mo_kho().ghi("hr", "quet.xong", {"da_cham": 1})
    ds = {d["ten"]: d for d in goi(app, "GET", "/api/du-an").json()["du_an"]}
    assert ds["hr"]["so_bead"]["ai-lam"] == 1 and ds["hr"]["so_bead"]["cho-review"] == 1
    assert ds["hr"]["quet_cuoi"] is not None and ds["web"]["quet_cuoi"] is None


def test_chi_tiet_bead(tmp_path):
    app, pt = tao_app_gia(tmp_path, _bds())
    pt.mo_kho().ghi("hr", "cham_cot.ket_qua", {"cot": "ai-lam", "ly_do": "Rõ", "cau_hoi": []}, bead_id="hr-1")
    r = goi(app, "GET", "/api/bead/hr/hr-1").json()
    assert r["the"]["id"] == "hr-1" and r["cham_gan_nhat"]["ly_do"] == "Rõ"
    assert [s["loai"] for s in r["dong_thoi_gian"]] == ["cham_cot.ket_qua"]
    assert goi(app, "GET", "/api/bead/hr/hr-9").status == 404
    assert goi(app, "GET", "/api/bead/hr/-x").status == 422


def test_phe_duyet_va_trang_thai(tmp_path):
    app, _ = tao_app_gia(tmp_path, _bds())
    r = goi(app, "GET", "/api/phe-duyet").json()
    assert r["so"] == 1 and r["muc"][0]["loai"] == "cho-review"
    tt = goi(app, "GET", "/api/chu/trang-thai").json()
    assert tt["estop"] is False and tt["la_dai_ca"] is False and [d["ten"] for d in tt["du_an"]] == ["hr", "web"]
    assert goi(app, "GET", "/api/chu/trang-thai", headers=DAI_CA).json()["la_dai_ca"] is True
    estop.bat("thử")
    assert goi(app, "GET", "/api/chu/trang-thai").json()["estop"] is True


def test_bd_loi_mot_du_an_van_tra_du_an_khac(tmp_path):
    bds = _bds()
    bds["web"] = BdGia(ra_loi_truoc={"tat_ca": 1})
    app, _ = tao_app_gia(tmp_path, bds)
    r = goi(app, "GET", "/api/cong-viec").json()
    assert {t["du_an"] for t in r["the"]} == {"hr"} and "web" in r["loi"]


def test_phuc_vu_file_tinh_va_tat_docs(tmp_path):
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text("<p>bàn điều hành</p>", encoding="utf-8")
    app, _ = tao_app_gia(tmp_path, _bds(), thu_muc_tinh=dist)
    r = goi(app, "GET", "/")
    assert r.status == 200 and "bàn điều hành" in r.body.decode()
    assert goi(app, "GET", "/api/du-an").status == 200
    assert goi(app, "GET", "/openapi.json").status == 404


def test_header_an_toan_va_host_421(tmp_path):
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text("<p>x</p>", encoding="utf-8")
    app, _ = tao_app_gia(tmp_path, _bds(), thu_muc_tinh=dist)
    for duong in ("/", "/api/du-an"):
        r = goi(app, "GET", duong)
        csp = r.headers["content-security-policy"]
        assert r.status == 200 and "script-src 'self'" in csp, duong
        assert "unsafe-eval" not in csp and "unsafe-inline" not in csp and r.headers["x-frame-options"] == "DENY"
    assert goi(app, "GET", "/api/du-an", headers={"Host": "may-b.tail.ts.net"}).status == 200
    assert goi(app, "GET", "/api/du-an", headers={"Host": "rebind.evil.example"}).status == 421
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_api_doc.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'tram.api.app'`.

- [ ] **Step 3: Viết mã**

`tram/api/phu_thuoc.py`:

```python
"""Phụ thuộc của tram-api gom một chỗ — test thay bằng bản giả (tests/api_gia.py)."""
import re
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from tram.api.bo_dem import BoDemBeads
from tram.beads.bd import Bd
from tram.cau_hinh.tram import CauHinhTram
from tram.su_kien.kho import KhoSuKien
from tram.thao_tac.chung import TAC_NHAN
from tram.thao_tac.kho import KhoThaoTac
from tram.thao_tac.loi import KhongHopLe, KhongThay

ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}")


@dataclass
class PhuThuocApi:
    cau_hinh: CauHinhTram
    cac_du_an: Callable[[], list[str]]
    tao_bd: Callable[[str], Bd]
    bo_dem: BoDemBeads
    mo_kho: Callable[[], KhoSuKien]
    mo_kho_tt: Callable[[], KhoThaoTac]
    thu_muc_tinh: Path | None = None


def kiem_du_an_bead(pt: PhuThuocApi, du_an: str, bead_id: str | None = None) -> None:
    """Chặn tên dự án lạ (không bao giờ dựng đường dẫn repo từ URL) và mã bead có thể thành cờ `bd`."""
    if du_an not in pt.cac_du_an():
        raise KhongThay(f"Không có dự án {du_an}")
    if bead_id is not None and not ID_RE.fullmatch(bead_id):
        raise KhongHopLe("Mã bead không hợp lệ")


def phu_thuoc_that() -> PhuThuocApi:
    from tram.cau_hinh.du_an import liet_ke_du_an, nap_du_an
    from tram.cau_hinh.tram import nap_cau_hinh_tram
    from tram.duong_dan import goc_repo
    from tram.su_kien.kho import mo_kho
    from tram.thao_tac.kho import mo_kho_thao_tac

    def tao_bd(ten: str) -> Bd:
        return Bd(nap_du_an(ten).duong_dan, actor=TAC_NHAN)

    dist = goc_repo() / "frontend" / "dist"
    return PhuThuocApi(
        cau_hinh=nap_cau_hinh_tram(),
        cac_du_an=lambda: [t for t in liet_ke_du_an() if not t.startswith("_")],
        tao_bd=tao_bd, bo_dem=BoDemBeads(tao_bd), mo_kho=mo_kho, mo_kho_tt=mo_kho_thao_tac,
        thu_muc_tinh=dist if dist.is_dir() else None)
```

`tram/api/app.py`:

```python
"""tram-api (spec 2 §3, §7). Chỉ chạy qua `tram api` — nghe 127.0.0.1 (tram/cli_dich_vu.py)."""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from tram.api import tuyen_doc
from tram.api.bao_mat import them_header_an_toan
from tram.api.phu_thuoc import PhuThuocApi
from tram.beads.bd import KhongThayBead, LoiBd
from tram.suy.lam_sach import lam_sach
from tram.thao_tac.loi import ChuaHoTro, KhongHopLe, KhongThay, XungDot

MA_LOI = {XungDot: 409, KhongHopLe: 422, ChuaHoTro: 501, KhongThay: 404, KhongThayBead: 404, LoiBd: 502}
CAC_TUYEN = (tuyen_doc.router,)


def _xu_ly(ma: int):
    async def xu_ly(request: Request, loi: Exception) -> JSONResponse:
        return JSONResponse({"loi": lam_sach(str(loi), 500)}, status_code=ma)
    return xu_ly


def tao_app(pt: PhuThuocApi, *, cong: int = 7700) -> FastAPI:
    app = FastAPI(title="tram-api", docs_url=None, redoc_url=None, openapi_url=None)
    app.state.pt = pt
    them_header_an_toan(app, pt.cau_hinh, cong=cong)          # CSP + Host (spec 2 §4 mục 6)
    for loai, ma in MA_LOI.items():
        app.add_exception_handler(loai, _xu_ly(ma))
    for r in CAC_TUYEN:
        app.include_router(r)
    if pt.thu_muc_tinh is not None:      # mount sau cùng: /api/* khớp trước
        app.mount("/", StaticFiles(directory=pt.thu_muc_tinh, html=True), name="tinh")
    return app
```

`tram/api/tuyen_doc.py`:

```python
"""Các GET lát 2a (spec 2 §7) — mọi trạng thái tính lúc đọc từ beads + sự kiện (Q12)."""
from collections import Counter
from contextlib import closing

from fastapi import APIRouter, Request

from tram.api.bao_mat import la_dai_ca_yeu_cau
from tram.api.phu_thuoc import kiem_du_an_bead
from tram.beads.bd import LoiBd
from tram.chu import estop
from tram.suy.chi_tiet import chi_tiet_bead
from tram.suy.cot import HANG, hien_tren_bang, the_bead
from tram.suy.lam_sach import lam_sach
from tram.suy.phe_duyet import gom_phe_duyet
from tram.suy.trang_thai import trang_thai_du_an, trang_thai_tram
from tram.thao_tac.loi import KhongThay

router = APIRouter()


def _doc_beads(pt, ten: list[str]) -> tuple[dict, dict]:
    beads, loi = {}, {}
    for t in ten:
        try:
            beads[t] = pt.bo_dem.lay(t)
        except LoiBd as e:
            loi[t] = lam_sach(str(e), 300)
    return beads, loi


def _the(beads: dict) -> list[dict]:
    ra = []
    for du_an, ds in beads.items():
        theo_id = {b.id: b for b in ds}
        ra += [the_bead(du_an, b, theo_id) for b in ds if hien_tren_bang(b)]
    return ra


@router.get("/api/du-an")
def du_an(request: Request) -> dict:
    pt = request.app.state.pt
    ten = pt.cac_du_an()
    beads, loi = _doc_beads(pt, ten)
    the, ra = _the(beads), []
    with closing(pt.mo_kho()) as kho:
        for t in ten:
            dem = Counter(x["hang"] for x in the if x["du_an"] == t)
            ra.append({**trang_thai_du_an(kho, t), "so_bead": {h: dem.get(h, 0) for h in HANG}, "loi_doc": loi.get(t)})
    return {"du_an": ra}


@router.get("/api/cong-viec")
def cong_viec(request: Request, du_an: str = "") -> dict:
    pt = request.app.state.pt
    if du_an:
        kiem_du_an_bead(pt, du_an)
    beads, loi = _doc_beads(pt, [du_an] if du_an else pt.cac_du_an())
    return {"the": _the(beads), "loi": loi}


@router.get("/api/bead/{du_an}/{bead_id}")
def bead(du_an: str, bead_id: str, request: Request) -> dict:
    pt = request.app.state.pt
    kiem_du_an_bead(pt, du_an, bead_id)
    theo_id = {b.id: b for b in pt.bo_dem.lay(du_an)}
    if bead_id not in theo_id:
        raise KhongThay(f"Không thấy bead {bead_id}")
    with closing(pt.mo_kho()) as kho:
        return chi_tiet_bead(du_an, theo_id[bead_id], theo_id, kho)


@router.get("/api/phe-duyet")
def phe_duyet(request: Request) -> dict:
    pt = request.app.state.pt
    ten = pt.cac_du_an()
    beads, loi = _doc_beads(pt, ten)
    with closing(pt.mo_kho()) as kho:
        muc = gom_phe_duyet(ten, beads, kho)
    return {"muc": muc, "so": len(muc), "loi": loi}


@router.get("/api/chu/trang-thai")
def trang_thai(request: Request) -> dict:
    pt = request.app.state.pt
    with closing(pt.mo_kho()) as kho:
        tt = trang_thai_tram(kho, pt.cac_du_an(), estop_bat=estop.dang_bat())
    return {**tt, "la_dai_ca": la_dai_ca_yeu_cau(request)}
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_api_doc.py -q` → Expected: `8 passed` (gồm `test_header_an_toan_va_host_421`: CSP có trên `/` và `/api/du-an`, không `unsafe-eval`/`unsafe-inline`; Host tên máy B → 200, Host lạ → 421). Rồi `uv run pytest -q` → không có fail.

- [ ] **Step 5: Commit**

```bash
git add tram/api/phu_thuoc.py tram/api/app.py tram/api/tuyen_doc.py tests/api_gia.py tests/test_api_doc.py
git commit -m "feat(api): tram-api đọc — dự án, công việc, chi tiết bead, phê duyệt, trạng thái, file tĩnh; CSP + Host"
```

---

### Task 13: Thao tác kéo cột + thử lại

**Độ khó:** `kho` · **Song song:** đợt 3 — chạy cùng Task 9, 14, 15, 16, 21, 25 (file riêng). **Phải xong trước:** Task 4, 6 (giao diện `Bd`, `BdGia`), 8. Task 17 cần task này.

**Files:**
- Create: `tram/thao_tac/cot.py`
- Test: `tests/test_keo_cot.py`

**Interfaces:**
- Consumes: `chay_thao_tac`, `YeuCau`, `KetQuaThaoTac` (4); `NguCanhGhi`, `kiem_version`, `ghi_su_kien_mot_lan` (4); `suy_vi_tri`, `ly_do_khong_keo` (8); `NHAN_COT`, `NHAN_KHOA` (`tram/cham_cot/ghi.py`); `nc.bd.mot`, `nc.bd.cap_nhat_nhan`.
- Produces:
  - `keo_cot(nc: NguCanhGhi, bead_id: str, *, cot: str, vi_sao: str | None, ma: str, expected_version: str) -> KetQuaThaoTac` — bước `ngu_canh` → `nhan` (một lệnh `bd update`: gỡ mọi `cot:*` khác đích, thêm đích + `cot-khoa` nếu chưa có) → `su_kien` (`cot.dai_ca_sua {tieu_de, cot_he, cot_moi, ly_do_he, vi_sao?, nguon: "dashboard", da_ghi: true, ma_thao_tac}`; `cot_he`, `cot_moi` là nhãn đầy đủ `cot:…` như 1a ghi; `cot_he` = cột hệ ghi lần cuối).
  - `thu_lai(nc, bead_id, *, ma, expected_version) -> KetQuaThaoTac` — một bước: sự kiện `cham_cot.thu_lai {ma_thao_tac}` (1a đọc thành yêu cầu chấm lại + cắt chuỗi lỗi — plan 1a T5, T10). Không sửa nhãn.

- [ ] **Step 1: Viết test thất bại**

`tests/test_keo_cot.py`:

```python
import pytest

from bd_gia import BdGia
from bead_gia import bead
from tram.beads.bd import LoiBd
from tram.su_kien.kho import KhoSuKien
from tram.thao_tac.chung import NguCanhGhi
from tram.thao_tac.cot import keo_cot, thu_lai
from tram.thao_tac.kho import KhoThaoTac
from tram.thao_tac.loi import KhongHopLe, XungDot

V = "2026-10-13T01:00:00Z"


def nc(tmp_path, *beads, **kw):
    db = tmp_path / "sk.db"
    return NguCanhGhi(bd=BdGia(beads, **kw), kho=KhoSuKien(db), kho_tt=KhoThaoTac(db), du_an="hr")


def test_keo_ai_lam_sang_can_chot(tmp_path):
    n = nc(tmp_path, bead("hr-1", labels=["cot:ai-lam", "b2b"]))
    n.kho.ghi("hr", "cham_cot.ket_qua", {"cot": "ai-lam", "ly_do": "Rõ", "da_ghi": True}, bead_id="hr-1")
    kq = keo_cot(n, "hr-1", cot="can-chot", vi_sao="Chạm giá", ma="ma-keo-0001", expected_version=V)
    assert set(n.bd.beads["hr-1"].labels) == {"b2b", "cot:can-chot", "cot-khoa"} and kq.lap_lai is False
    assert n.bd.goi == [("cap_nhat_nhan", "hr-1", ("cot:can-chot", "cot-khoa"), ("cot:ai-lam",), None)]
    sk = n.kho.moi_nhat("hr", "hr-1", "cot.dai_ca_sua")
    assert sk.du_lieu == {"tieu_de": "Việc", "cot_he": "cot:ai-lam", "cot_moi": "cot:can-chot", "ly_do_he": "Rõ",
                          "vi_sao": "Chạm giá", "nguon": "dashboard", "da_ghi": True, "ma_thao_tac": "ma-keo-0001"}
    assert sk.tac_nhan == "dai-ca/dashboard"


def test_hai_nhan_cot_sau_keo_con_dung_mot(tmp_path):
    n = nc(tmp_path, bead("hr-1", labels=["cot:ai-lam", "cot:can-chot"]))
    keo_cot(n, "hr-1", cot="ai-lam", vi_sao=None, ma="ma-keo-0002", expected_version=V)
    assert sorted(n.bd.beads["hr-1"].labels) == ["cot-khoa", "cot:ai-lam"]
    sk = n.kho.moi_nhat("hr", "hr-1", "cot.dai_ca_sua")
    assert "vi_sao" not in sk.du_lieu and sk.du_lieu["cot_he"] is None


def test_bead_da_doi_thi_409_khong_ghi_gi(tmp_path):
    n = nc(tmp_path, bead("hr-1", labels=["cot:ai-lam"]))
    with pytest.raises(XungDot):
        keo_cot(n, "hr-1", cot="can-chot", vi_sao=None, ma="ma-keo-0003", expected_version="2026-10-12T00:00:00Z")
    assert n.bd.goi == [] and n.kho_tt.lay("ma-keo-0003") is None


@pytest.mark.parametrize("labels,kw", [
    (["cot:ai-lam"], {"issue_type": "epic"}), (["cot:cho-review"], {}), ([], {}), (["can-spec"], {}),
    (["cot:can-chot"], {}),
])
def test_khong_keo_duoc(tmp_path, labels, kw):
    n = nc(tmp_path, bead("hr-1", labels=labels, **kw))
    with pytest.raises(KhongHopLe):
        keo_cot(n, "hr-1", cot="can-chot", vi_sao=None, ma="ma-keo-0004", expected_version=V)
    assert n.bd.goi == []


def test_cot_dich_sai(tmp_path):
    with pytest.raises(KhongHopLe):
        keo_cot(nc(tmp_path, bead()), "hr-1", cot="cho-review", vi_sao=None, ma="ma-keo-0005", expected_version=V)


def test_bam_hai_lan_chi_ghi_mot_lan(tmp_path):
    n = nc(tmp_path, bead("hr-1", labels=["cot:ai-lam"]))
    a = keo_cot(n, "hr-1", cot="can-chot", vi_sao=None, ma="ma-keo-0006", expected_version=V)
    b = keo_cot(n, "hr-1", cot="can-chot", vi_sao=None, ma="ma-keo-0006", expected_version=V)
    assert a.lap_lai is False and b.lap_lai is True and n.bd.so_lan("cap_nhat_nhan") == 1
    assert len(n.kho.gan_day("hr", "cot.dai_ca_sua", 10)) == 1


def test_crash_sau_khi_bd_ghi_nhan_lam_tiep_khong_ghi_lai(tmp_path):
    n = nc(tmp_path, bead("hr-1", labels=["cot:ai-lam"]), ra_loi_sau={"cap_nhat_nhan": 1})
    with pytest.raises(LoiBd):
        keo_cot(n, "hr-1", cot="can-chot", vi_sao=None, ma="ma-keo-0007", expected_version=V)
    kq = keo_cot(n, "hr-1", cot="can-chot", vi_sao=None, ma="ma-keo-0007", expected_version=V)
    assert kq.lap_lai is False and n.bd.so_lan("cap_nhat_nhan") == 1
    assert len(n.kho.gan_day("hr", "cot.dai_ca_sua", 10)) == 1


def test_thu_lai_ghi_su_kien_mot_lan(tmp_path):
    n = nc(tmp_path, bead("hr-1", labels=["cot:ai-lam"]))
    thu_lai(n, "hr-1", ma="ma-thulai-01", expected_version=V)
    thu_lai(n, "hr-1", ma="ma-thulai-01", expected_version=V)
    ds = n.kho.gan_day("hr", "cham_cot.thu_lai", 10)
    assert len(ds) == 1 and ds[0].du_lieu == {"ma_thao_tac": "ma-thulai-01"} and ds[0].tac_nhan == "dai-ca/dashboard"
    assert n.bd.goi == [] and n.kho.yeu_cau.nhan_su_kien_nguon("hr") == 1     # 1a nhận thành yêu cầu chấm lại
    with pytest.raises(XungDot):
        thu_lai(n, "hr-1", ma="ma-thulai-02", expected_version="2026-10-12T00:00:00Z")
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_keo_cot.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'tram.thao_tac.cot'`.

- [ ] **Step 3: Viết mã**

`tram/thao_tac/cot.py`:

```python
"""Kéo cột (spec 2 §5.1) và nút 'thử lại' (§12.5) — thao tác ghi bền theo ma_thao_tac."""
from tram.cham_cot.ghi import NHAN_COT, NHAN_KHOA
from tram.suy.cot import ly_do_khong_keo, suy_vi_tri
from tram.thao_tac.chay import KetQuaThaoTac, YeuCau, chay_thao_tac
from tram.thao_tac.chung import NguCanhGhi, ghi_su_kien_mot_lan, kiem_version
from tram.thao_tac.loi import KhongHopLe


def _cot_he(kho, du_an: str, bead_id: str) -> tuple[str | None, str | None]:
    """Cột hệ ghi lần cuối — cùng cách 1a tính trong kiem_sua_tay."""
    s = kho.moi_nhat(du_an, bead_id, "cham_cot.ket_qua", dieu_kien=lambda x: x.du_lieu.get("da_ghi"))
    return (NHAN_COT.get(s.du_lieu.get("cot")), s.du_lieu.get("ly_do")) if s else (None, None)


def keo_cot(nc: NguCanhGhi, bead_id: str, *, cot: str, vi_sao: str | None, ma: str,
            expected_version: str) -> KetQuaThaoTac:
    if cot not in NHAN_COT:
        raise KhongHopLe("Cột đích phải là ai-lam hoặc can-chot")
    dich = NHAN_COT[cot]

    def kiem_moi() -> None:
        b = nc.bd.mot(bead_id)
        kiem_version(b, expected_version)
        vt = suy_vi_tri(b, {})
        if (ly_do := ly_do_khong_keo(b, vt)) is not None:
            raise KhongHopLe(ly_do)
        if vt.hang == cot:
            raise KhongHopLe("Bead đã ở cột này")

    def ngu_canh(_) -> dict:
        cot_he, ly_do_he = _cot_he(nc.kho, nc.du_an, bead_id)
        return {"tieu_de": nc.bd.mot(bead_id).title, "cot_he": cot_he, "ly_do_he": ly_do_he}

    def nhan(_) -> dict:
        b = nc.bd.mot(bead_id)                     # đối soát: crash sau bd update thì không ghi lại
        bo = [n for n in b.labels if n.startswith("cot:") and n != dich]
        them = [n for n in (dich, NHAN_KHOA) if n not in b.labels]
        if bo or them:
            nc.bd.cap_nhat_nhan(bead_id, them=them, bo=bo)
        return {"them": them, "bo": bo}

    def su_kien(d: dict) -> bool:
        nt = d["ngu_canh"]
        du_lieu = {"tieu_de": nt["tieu_de"], "cot_he": nt["cot_he"], "cot_moi": dich, "ly_do_he": nt["ly_do_he"],
                   "nguon": "dashboard", "da_ghi": True}
        if vi_sao:
            du_lieu["vi_sao"] = vi_sao
        return ghi_su_kien_mot_lan(nc.kho, nc.du_an, bead_id, "cot.dai_ca_sua", du_lieu, ma=ma)

    yc = YeuCau(ma, "keo_cot", nc.du_an, bead_id, {"cot": cot, "vi_sao": vi_sao}, expected_version)
    return chay_thao_tac(nc.kho_tt, yc, kiem_moi=kiem_moi,
                         cac_buoc=[("ngu_canh", ngu_canh), ("nhan", nhan), ("su_kien", su_kien)])


def thu_lai(nc: NguCanhGhi, bead_id: str, *, ma: str, expected_version: str) -> KetQuaThaoTac:
    def kiem_moi() -> None:
        kiem_version(nc.bd.mot(bead_id), expected_version)

    def su_kien(_) -> bool:
        return ghi_su_kien_mot_lan(nc.kho, nc.du_an, bead_id, "cham_cot.thu_lai", {}, ma=ma)

    yc = YeuCau(ma, "thu_lai", nc.du_an, bead_id, {}, expected_version)
    return chay_thao_tac(nc.kho_tt, yc, kiem_moi=kiem_moi, cac_buoc=[("su_kien", su_kien)])
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_keo_cot.py -q` → Expected: `12 passed`.

- [ ] **Step 5: Commit**

```bash
git add tram/thao_tac/cot.py tests/test_keo_cot.py
git commit -m "feat(thao-tac): kéo cột thay toàn bộ cot:* + cot-khoa + cot.dai_ca_sua; nút thử lại ghi cham_cot.thu_lai"
```

---

### Task 14: Thao tác Chốt — decision, đóng, nối, gỡ nhãn, sự kiện; đối soát khi crash

**Độ khó:** `kho` (nhiều bước `bd`, ca crash §12.3) · **Song song:** đợt 3 — chạy cùng Task 9, 13, 15, 16, 21, 25. **Phải xong trước:** Task 4, 6, 8 (`cham_gan_nhat`, `ly_do_khong_chot`). Task 17 cần task này.

**Files:**
- Create: `tram/thao_tac/chot.py`
- Test: `tests/test_chot.py`

**Interfaces:**
- Consumes: như Task 13, thêm `cham_gan_nhat`, `ly_do_khong_chot` (8); `nc.bd.tat_ca`, `.tao`, `.dong`, `.them_phu_thuoc` (6).
- Produces:
  - Hằng `ADR_RE`, `CAU_CHUNG`, `DAU_MA = "<!-- tram:ma_thao_tac={} -->"`.
  - `cau_hoi_hien_tai(kho, du_an, bead_id) -> list[str]` (G3/G18); `kiem_noi_dung(hoi, tra_loi, adr) -> None`; `mo_ta_decision(bead_id, hoi, tra_loi, adr, ma) -> str`; `ly_do_dong(tra_loi, adr) -> str`.
  - `chot(nc, bead_id, *, tra_loi: list[str] | None, adr: str | None, ma: str, expected_version: str) -> KetQuaThaoTac` — các bước theo đúng thứ tự spec §5.1: `ngu_canh` → `tao_decision` (tìm decision có `DAU_MA` trong mô tả trước; không có mới `bd create -t decision`, tiêu đề "Chốt: <tiêu đề bead>") → `dong_decision` (`bd close --reason` = tóm tắt câu trả lời, nếu chưa đóng) → `noi` (`bd dep add <bead> <decision>` nếu chưa có) → `go_nhan` (gỡ `cot-khoa` + mọi `cot:*` → bead về "chưa chấm") → `su_kien` (`cot.da_chot {decision_id, cau_hoi[], tra_loi[], adr?, ma_thao_tac}`). `ket_qua["tao_decision"]` = mã decision.

Yêu cầu chấm lại bền sau Chốt do 1a tạo khi so ảnh decision (xem "Phụ thuộc plan 1a" mục 1) — task này không gọi gì thêm.

- [ ] **Step 1: Viết test thất bại**

`tests/test_chot.py`:

```python
import pytest

from bd_gia import BdGia
from bead_gia import bead
from tram.beads.bd import LoiBd
from tram.beads.mo_hinh import PhuThuoc
from tram.su_kien.kho import KhoSuKien
from tram.thao_tac.chot import CAU_CHUNG, chot
from tram.thao_tac.chung import NguCanhGhi
from tram.thao_tac.kho import KhoThaoTac
from tram.thao_tac.loi import KhongHopLe, XungDot

V = "2026-10-13T01:00:00Z"
HOI = ["Giá gồm VAT?", "Áp từ ngày nào?"]


def nc(tmp_path, *, labels=("cot:can-chot", "cot-khoa"), cau_hoi=HOI, **kw):
    db = tmp_path / "sk.db"
    n = NguCanhGhi(bd=BdGia([bead("hr-5", title="Giá tour", labels=labels)], **kw),
                   kho=KhoSuKien(db), kho_tt=KhoThaoTac(db), du_an="hr")
    if cau_hoi is not None:
        n.kho.ghi("hr", "cham_cot.ket_qua", {"cot": "can-chot", "ly_do": "Chạm giá", "cau_hoi": cau_hoi,
                                             "da_ghi": True}, bead_id="hr-5")
    return n


def _decision(n):
    return [b for b in n.bd.beads.values() if b.issue_type == "decision"]


def _chot(n, ma, tra_loi=("a", "b"), adr=None, version=V):
    return chot(n, "hr-5", tra_loi=list(tra_loi) if tra_loi is not None else None, adr=adr, ma=ma,
                expected_version=version)


def test_chot_tra_loi_du_buoc(tmp_path):
    n = nc(tmp_path)
    kq = _chot(n, "ma-chot-0001", tra_loi=["Có VAT", " Từ 1/11 "])
    (d,) = _decision(n)
    assert kq.ket_qua["tao_decision"] == d.id and kq.lap_lai is False
    assert d.title == "Chốt: Giá tour" and d.status == "closed" and d.close_reason == "(1) Có VAT; (2) Từ 1/11"
    assert "Hỏi: Giá gồm VAT?\nĐáp: Có VAT" in d.description
    assert d.description.endswith("<!-- tram:ma_thao_tac=ma-chot-0001 -->")
    b = n.bd.beads["hr-5"]
    assert PhuThuoc(d.id, "blocks") in b.phu_thuoc
    assert not [x for x in b.labels if x.startswith("cot:") or x == "cot-khoa"]
    sk = n.kho.moi_nhat("hr", "hr-5", "cot.da_chot")
    assert sk.du_lieu == {"decision_id": d.id, "cau_hoi": HOI, "tra_loi": ["Có VAT", "Từ 1/11"],
                          "ma_thao_tac": "ma-chot-0001"}
    assert [g[0] for g in n.bd.goi] == ["tat_ca", "tao", "dong", "them_phu_thuoc", "cap_nhat_nhan"]


def test_chot_dan_adr(tmp_path):
    n = nc(tmp_path)
    _chot(n, "ma-chot-0002", tra_loi=None, adr="ADR-0012")
    (d,) = _decision(n)
    assert d.close_reason == "Theo ADR-0012" and "Dẫn ADR: ADR-0012" in d.description
    sk = n.kho.moi_nhat("hr", "hr-5", "cot.da_chot")
    assert sk.du_lieu["adr"] == "ADR-0012" and sk.du_lieu["tra_loi"] == []


def test_khong_co_cau_hoi_thi_mot_cau_chung(tmp_path):
    n = nc(tmp_path, cau_hoi=None)
    _chot(n, "ma-chot-0003", tra_loi=["Làm theo giá cũ"])
    assert n.kho.moi_nhat("hr", "hr-5", "cot.da_chot").du_lieu["cau_hoi"] == [CAU_CHUNG]


@pytest.mark.parametrize("tra_loi,adr", [
    (["chỉ một"], None), (["a", " "], None), (None, None), (["a", "b"], "ADR-0001"), (None, "ADR-12"),
])
def test_noi_dung_sai_luat_khong_ghi_gi(tmp_path, tra_loi, adr):
    n = nc(tmp_path)
    with pytest.raises(KhongHopLe):
        _chot(n, "ma-chot-0004", tra_loi=tra_loi, adr=adr)
    assert n.bd.goi == [] and n.kho_tt.lay("ma-chot-0004") is None


@pytest.mark.parametrize("labels", [("cot:ai-lam",), ("cot:can-chot", "tram:escalation"), ("cho-duyet-spec",)])
def test_bead_khong_chot_duoc(tmp_path, labels):
    with pytest.raises(KhongHopLe):
        _chot(nc(tmp_path, labels=labels), "ma-chot-0005")


def test_bead_da_doi_409(tmp_path):
    with pytest.raises(XungDot):
        _chot(nc(tmp_path), "ma-chot-0006", version="2026-10-12T00:00:00Z")


def test_bam_hai_lan_chi_mot_decision(tmp_path):
    n = nc(tmp_path)
    a = _chot(n, "ma-chot-0007")
    b = _chot(n, "ma-chot-0007")
    assert b.lap_lai is True and b.ket_qua == a.ket_qua
    assert n.bd.so_lan("tao") == 1 and len(_decision(n)) == 1


def test_crash_sau_bd_create_truoc_bd_close(tmp_path):
    n = nc(tmp_path, ra_loi_sau={"tao": 1})
    with pytest.raises(LoiBd):
        _chot(n, "ma-chot-0008")
    (d,) = _decision(n)
    assert d.status == "open" and set(n.kho_tt.lay("ma-chot-0008").buoc_da_xong) == {"ngu_canh"}
    kq = _chot(n, "ma-chot-0008")
    assert n.bd.so_lan("tao") == 1 and len(_decision(n)) == 1 and kq.ket_qua["tao_decision"] == d.id
    assert n.bd.beads[d.id].status == "closed" and PhuThuoc(d.id, "blocks") in n.bd.beads["hr-5"].phu_thuoc


def test_crash_sau_bd_close_truoc_dep_add(tmp_path):
    n = nc(tmp_path, ra_loi_truoc={"them_phu_thuoc": 1})
    with pytest.raises(LoiBd):
        _chot(n, "ma-chot-0009")
    kq = _chot(n, "ma-chot-0009")
    assert (n.bd.so_lan("tao"), n.bd.so_lan("dong"), n.bd.so_lan("them_phu_thuoc")) == (1, 1, 1)
    assert kq.lap_lai is False and len(n.kho.gan_day("hr", "cot.da_chot", 10)) == 1


def test_dep_add_da_co_khong_them_lan_hai(tmp_path):
    n = nc(tmp_path, ra_loi_sau={"them_phu_thuoc": 1})
    with pytest.raises(LoiBd):
        _chot(n, "ma-chot-0010")
    _chot(n, "ma-chot-0010")
    d = _decision(n)[0].id
    assert n.bd.so_lan("them_phu_thuoc") == 1
    assert n.bd.beads["hr-5"].phu_thuoc.count(PhuThuoc(d, "blocks")) == 1
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_chot.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'tram.thao_tac.chot'`.

- [ ] **Step 3: Viết mã**

`tram/thao_tac/chot.py`:

```python
"""Nút Chốt (spec 2 §5.1, §12.3): decision → đóng → nối → gỡ nhãn → sự kiện; idempotent, đối soát khi crash."""
import re

from tram.cham_cot.ghi import NHAN_KHOA
from tram.suy.cot import cham_gan_nhat, ly_do_khong_chot, suy_vi_tri
from tram.thao_tac.chay import KetQuaThaoTac, YeuCau, chay_thao_tac
from tram.thao_tac.chung import NguCanhGhi, ghi_su_kien_mot_lan, kiem_version
from tram.thao_tac.loi import KhongHopLe

ADR_RE = re.compile(r"ADR-\d{4}")
CAU_CHUNG = "Chốt chung cho bead (lần chấm không có câu hỏi cụ thể)"
DAU_MA = "<!-- tram:ma_thao_tac={} -->"


def cau_hoi_hien_tai(kho, du_an: str, bead_id: str) -> list[str]:
    s = cham_gan_nhat(kho, du_an, bead_id)
    hoi = [q for q in (s.du_lieu.get("cau_hoi") or []) if q] if s else []
    return hoi or [CAU_CHUNG]


def kiem_noi_dung(hoi: list[str], tra_loi: list[str], adr: str | None) -> None:
    if adr is not None:
        if tra_loi:
            raise KhongHopLe("Chọn trả lời từng câu hoặc dẫn ADR, không cả hai")
        if not ADR_RE.fullmatch(adr):
            raise KhongHopLe("ADR phải có dạng ADR-0000")
        return
    if not tra_loi or len(tra_loi) != len(hoi) or any(not t.strip() for t in tra_loi):
        raise KhongHopLe(f"Cần đủ {len(hoi)} câu trả lời, không để trống")


def mo_ta_decision(bead_id: str, hoi: list[str], tra_loi: list[str], adr: str | None, ma: str) -> str:
    dong = [f"Chốt cho {bead_id} từ dashboard.", ""]
    if adr:
        dong.append(f"Dẫn ADR: {adr}")
    else:
        for q, a in zip(hoi, tra_loi):
            dong += [f"Hỏi: {q}", f"Đáp: {a.strip()}", ""]
    return "\n".join(dong + ["", DAU_MA.format(ma)])


def ly_do_dong(tra_loi: list[str], adr: str | None) -> str:
    s = f"Theo {adr}" if adr else "; ".join(f"({i}) {a.strip()}" for i, a in enumerate(tra_loi, 1))
    return s[:2000]


def chot(nc: NguCanhGhi, bead_id: str, *, tra_loi: list[str] | None, adr: str | None, ma: str,
         expected_version: str) -> KetQuaThaoTac:
    tra_loi = list(tra_loi or [])

    def kiem_moi() -> None:
        b = nc.bd.mot(bead_id)
        kiem_version(b, expected_version)
        if (ly_do := ly_do_khong_chot(b, suy_vi_tri(b, {}))) is not None:
            raise KhongHopLe(ly_do)
        kiem_noi_dung(cau_hoi_hien_tai(nc.kho, nc.du_an, bead_id), tra_loi, adr)

    def ngu_canh(_) -> dict:
        return {"tieu_de": nc.bd.mot(bead_id).title, "cau_hoi": cau_hoi_hien_tai(nc.kho, nc.du_an, bead_id)}

    def tao_decision(d: dict) -> str:
        dau = DAU_MA.format(ma)                    # đối soát: crash sau bd create thì không tạo cái thứ hai
        co = sorted(b.id for b in nc.bd.tat_ca() if b.issue_type == "decision" and dau in b.description)
        if co:
            return co[0]
        nt = d["ngu_canh"]
        return nc.bd.tao(f"Chốt: {nt['tieu_de']}"[:200], loai="decision",
                         mo_ta=mo_ta_decision(bead_id, nt["cau_hoi"], tra_loi, adr, ma))

    def dong_decision(d: dict) -> bool:
        if nc.bd.mot(d["tao_decision"]).status != "closed":
            nc.bd.dong(d["tao_decision"], ly_do_dong(tra_loi, adr))
        return True

    def noi(d: dict) -> bool:
        b = nc.bd.mot(bead_id)                     # `bd dep add` lặp vẫn "Added" — tự kiểm trùng (spike)
        if not any(p.depends_on_id == d["tao_decision"] and p.loai == "blocks" for p in b.phu_thuoc):
            nc.bd.them_phu_thuoc(bead_id, d["tao_decision"])
        return True

    def go_nhan(_) -> list[str]:
        b = nc.bd.mot(bead_id)
        bo = [n for n in b.labels if n.startswith("cot:") or n == NHAN_KHOA]
        if bo:
            nc.bd.cap_nhat_nhan(bead_id, bo=bo)
        return bo

    def su_kien(d: dict) -> bool:
        du_lieu = {"decision_id": d["tao_decision"], "cau_hoi": d["ngu_canh"]["cau_hoi"],
                   "tra_loi": [t.strip() for t in tra_loi]}
        if adr:
            du_lieu["adr"] = adr
        return ghi_su_kien_mot_lan(nc.kho, nc.du_an, bead_id, "cot.da_chot", du_lieu, ma=ma)

    yc = YeuCau(ma, "chot", nc.du_an, bead_id, {"tra_loi": tra_loi, "adr": adr}, expected_version)
    return chay_thao_tac(nc.kho_tt, yc, kiem_moi=kiem_moi, cac_buoc=[
        ("ngu_canh", ngu_canh), ("tao_decision", tao_decision), ("dong_decision", dong_decision),
        ("noi", noi), ("go_nhan", go_nhan), ("su_kien", su_kien)])
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_chot.py -q` → Expected: `16 passed`. `wc -l tram/thao_tac/chot.py` ≤ 120.

- [ ] **Step 5: Commit**

```bash
git add tram/thao_tac/chot.py tests/test_chot.py
git commit -m "feat(thao-tac): nút Chốt tạo decision đã đóng, nối blocks, gỡ nhãn cột; đối soát theo ma_thao_tac khi crash"
```

---

### Task 15: Thao tác Phê duyệt — Duyệt, Trả về + góp ý, Trả lời escalation / decision mở

**Độ khó:** `kho` · **Song song:** đợt 3 — chạy cùng Task 9, 13, 14, 16, 21, 25. **Phải xong trước:** Task 4, 6, 7 (`tom_tat_ban_giao`), 8 (`hien_tren_bang`, `ly_do_khong_tra_loi`). Task 17 cần task này.

**Files:**
- Create: `tram/thao_tac/phe_duyet.py`
- Test: `tests/test_thao_tac_phe_duyet.py`

**Interfaces:**
- Consumes: như Task 13; `tom_tat_ban_giao` (7); `hien_tren_bang`, `ly_do_khong_tra_loi` (8); `GIO_VN`, `NHAN_KHOA` (`tram/cham_cot/ghi.py`); `bay_gio`, `doc_luc`; `ChuaHoTro`.
- Produces:
  - `ly_do_duyet(pr: str | None) -> str`.
  - `duyet(nc, bead_id, *, ma, expected_version, expected_commit: str | None = None, digest_bead: str | None = None) -> KetQuaThaoTac` — bead `cho-duyet-spec` → `ChuaHoTro` (G4); phải có `cot:cho-review` và `hien_tren_bang` (không đóng, **không hoãn** — Q2); bước `dong`: `bd close <id> --reason <ly_do_duyet(pr)>` nếu chưa đóng; `ket_qua["dong"] = {"pr": ...}`. Bàn giao thiếu/lỗi vẫn cho Duyệt.
  - `tra_ve(nc, bead_id, *, gop_y: str, ma, expected_version) -> KetQuaThaoTac` — spec → `ChuaHoTro`; phải ở cột 3 và `hien_tren_bang` (Q2); bước `nhan_va_ghi_chu` (một `bd update`: gỡ mọi `cot:*` + `cot-khoa`, `--append-notes "[dai-ca/dashboard <giờ VN>] Trả về: <góp ý> (ma_thao_tac <ma>)"` — notes đã có dấu mã thì không ghi lại) → `su_kien` (`cot.tra_ve {gop_y, ma_thao_tac}`).
  - `tra_loi_decision(nc, bead_id, *, tra_loi: str, ma, expected_version) -> KetQuaThaoTac` (thay `tra_loi_escalation` của bản trước — Q4) — bead phải qua `ly_do_khong_tra_loi`: `decision` đang hiện trên bảng, **có hoặc không** `tram:escalation` (không đóng, không hoãn — Q2); bước `dong` (`bd close <decision> --reason <tra_loi>` — đóng **chính** decision, không tạo decision thứ hai) → `su_kien` (`escalation.tra_loi {escalation_id = id decision, ma_thao_tac}`, `bead_id` = decision — dùng chung sự kiện theo spec §12.2, không có `decision.tra_loi`). Đóng decision mở làm 1a (so ảnh decision) tạo yêu cầu chấm lại bead phụ thuộc.

- [ ] **Step 1: Viết test thất bại**

`tests/test_thao_tac_phe_duyet.py`:

```python
import pytest

from bd_gia import BdGia
from bead_gia import bead, notes_ban_giao
from tram.beads.bd import LoiBd
from tram.su_kien.kho import KhoSuKien
from tram.thao_tac.chung import NguCanhGhi
from tram.thao_tac.kho import KhoThaoTac
from tram.thao_tac.loi import ChuaHoTro, KhongHopLe
from tram.thao_tac.phe_duyet import duyet, tra_loi_decision, tra_ve

V = "2026-10-13T01:00:00Z"


def nc(tmp_path, *beads, **kw):
    db = tmp_path / "sk.db"
    return NguCanhGhi(bd=BdGia(beads, **kw), kho=KhoSuKien(db), kho_tt=KhoThaoTac(db), du_an="hr")


def test_duyet_khong_pr(tmp_path):
    n = nc(tmp_path, bead("hr-2", labels=["cot:cho-review"]))
    kq = duyet(n, "hr-2", ma="ma-duyet-001", expected_version=V)
    b = n.bd.beads["hr-2"]
    assert b.status == "closed" and b.close_reason == "Đại ca duyệt trên dashboard"
    assert kq.ket_qua == {"dong": {"pr": None}}


def test_duyet_co_pr_ghi_ro_la_thao_tac_tay(tmp_path):
    n = nc(tmp_path, bead("hr-2", labels=["cot:cho-review"], notes=notes_ban_giao()))
    duyet(n, "hr-2", ma="ma-duyet-002", expected_version=V)
    ly_do = n.bd.beads["hr-2"].close_reason
    assert "https://github.com/o/r/pull/7" in ly_do and "thao tác tay" in ly_do and "không phải bằng chứng máy" in ly_do


def test_duyet_ban_giao_loi_van_dong(tmp_path):
    n = nc(tmp_path, bead("hr-2", labels=["cot:cho-review"], notes=notes_ban_giao(luot="x")))
    duyet(n, "hr-2", ma="ma-duyet-003", expected_version=V)
    assert n.bd.beads["hr-2"].status == "closed"


def test_spec_la_501_khong_ghi_gi(tmp_path):
    n = nc(tmp_path, bead("hr-4", issue_type="feature", labels=["cho-duyet-spec"]))
    with pytest.raises(ChuaHoTro):
        duyet(n, "hr-4", ma="ma-duyet-004", expected_version=V, expected_commit="abc", digest_bead="d")
    with pytest.raises(ChuaHoTro):
        tra_ve(n, "hr-4", gop_y="x", ma="ma-trave-004", expected_version=V)
    assert n.bd.goi == [] and n.kho_tt.lay("ma-duyet-004") is None


def test_duyet_khong_phai_cot_3(tmp_path):
    n = nc(tmp_path, bead("hr-1", labels=["cot:ai-lam"]))
    with pytest.raises(KhongHopLe):
        duyet(n, "hr-1", ma="ma-duyet-005", expected_version=V)


def test_tra_ve_go_nhan_ghi_gop_y_va_su_kien(tmp_path):
    n = nc(tmp_path, bead("hr-2", labels=["cot:cho-review", "cot-khoa", "b2b"]))
    tra_ve(n, "hr-2", gop_y="Thiếu test biên", ma="ma-trave-001", expected_version=V)
    b = n.bd.beads["hr-2"]
    assert b.labels == ("b2b",) and b.notes.startswith("[dai-ca/dashboard ")
    assert "Trả về: Thiếu test biên (ma_thao_tac ma-trave-001)" in b.notes
    sk = n.kho.moi_nhat("hr", "hr-2", "cot.tra_ve")
    assert sk.du_lieu == {"gop_y": "Thiếu test biên", "ma_thao_tac": "ma-trave-001"}


def test_tra_ve_hai_lan_cung_ma(tmp_path):
    n = nc(tmp_path, bead("hr-2", labels=["cot:cho-review"]))
    tra_ve(n, "hr-2", gop_y="x", ma="ma-trave-002", expected_version=V)
    assert tra_ve(n, "hr-2", gop_y="x", ma="ma-trave-002", expected_version=V).lap_lai is True
    assert n.bd.so_lan("cap_nhat_nhan") == 1 and len(n.kho.gan_day("hr", "cot.tra_ve", 10)) == 1


def test_tra_ve_crash_sau_bd_update(tmp_path):
    n = nc(tmp_path, bead("hr-2", labels=["cot:cho-review"]), ra_loi_sau={"cap_nhat_nhan": 1})
    with pytest.raises(LoiBd):
        tra_ve(n, "hr-2", gop_y="x", ma="ma-trave-003", expected_version=V)
    tra_ve(n, "hr-2", gop_y="x", ma="ma-trave-003", expected_version=V)
    assert n.bd.so_lan("cap_nhat_nhan") == 1 and n.bd.beads["hr-2"].notes.count("ma_thao_tac ma-trave-003") == 1
    assert len(n.kho.gan_day("hr", "cot.tra_ve", 10)) == 1


def test_tra_ve_gop_y_rong(tmp_path):
    with pytest.raises(KhongHopLe):
        tra_ve(nc(tmp_path, bead("hr-2", labels=["cot:cho-review"])), "hr-2", gop_y="  ", ma="ma-trave-005",
               expected_version=V)


def test_tra_loi_decision(tmp_path):
    n = nc(tmp_path, bead("hr-3", issue_type="decision", labels=["tram:escalation"]))
    tra_loi_decision(n, "hr-3", tra_loi=" Làm theo hướng A ", ma="ma-traloi-01", expected_version=V)
    tra_loi_decision(n, "hr-3", tra_loi=" Làm theo hướng A ", ma="ma-traloi-01", expected_version=V)
    b = n.bd.beads["hr-3"]
    assert b.status == "closed" and b.close_reason == "Làm theo hướng A" and n.bd.so_lan("dong") == 1
    ds = n.kho.gan_day("hr", "escalation.tra_loi", 10)
    assert len(ds) == 1 and ds[0].bead_id == "hr-3"
    assert ds[0].du_lieu == {"escalation_id": "hr-3", "ma_thao_tac": "ma-traloi-01"}


def test_tra_loi_decision_mo_khong_phai_escalation(tmp_path):
    n = nc(tmp_path, bead("hr-8", issue_type="decision", labels=["cot:can-chot"]))
    tra_loi_decision(n, "hr-8", tra_loi="Chọn B", ma="ma-traloi-04", expected_version=V)
    b = n.bd.beads["hr-8"]
    assert b.status == "closed" and b.close_reason == "Chọn B"
    ds = n.kho.gan_day("hr", "escalation.tra_loi", 10)
    assert len(ds) == 1 and ds[0].du_lieu == {"escalation_id": "hr-8", "ma_thao_tac": "ma-traloi-04"}


def test_bead_hoan_khong_duyet_khong_tra_loi(tmp_path):
    n = nc(tmp_path, bead("hr-2", status="deferred", labels=["cot:cho-review"]),
           bead("hr-3", status="deferred", issue_type="decision", labels=["tram:escalation"]))
    with pytest.raises(KhongHopLe):
        duyet(n, "hr-2", ma="ma-duyet-006", expected_version=V)
    with pytest.raises(KhongHopLe):
        tra_ve(n, "hr-2", gop_y="x", ma="ma-trave-006", expected_version=V)
    with pytest.raises(KhongHopLe):
        tra_loi_decision(n, "hr-3", tra_loi="x", ma="ma-traloi-05", expected_version=V)
    assert n.bd.goi == []


def test_tra_loi_khong_phai_decision_hoac_rong(tmp_path):
    n = nc(tmp_path, bead("hr-1", labels=["cot:can-chot"]),
           bead("hr-3", issue_type="decision", labels=["tram:escalation"]))
    with pytest.raises(KhongHopLe):
        tra_loi_decision(n, "hr-1", tra_loi="x", ma="ma-traloi-02", expected_version=V)
    with pytest.raises(KhongHopLe):
        tra_loi_decision(n, "hr-3", tra_loi="  ", ma="ma-traloi-03", expected_version=V)
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_thao_tac_phe_duyet.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'tram.thao_tac.phe_duyet'`.

- [ ] **Step 3: Viết mã**

`tram/thao_tac/phe_duyet.py`:

```python
"""Phê duyệt (spec 2 §5.2): Duyệt cột 3, Trả về + góp ý, Trả lời escalation / decision mở. Spec → phần 4b."""
from tram.ban_giao.doc import tom_tat_ban_giao
from tram.cham_cot.ghi import GIO_VN, NHAN_KHOA
from tram.duong_dan import bay_gio, doc_luc
from tram.suy.cot import hien_tren_bang, ly_do_khong_tra_loi
from tram.thao_tac.chay import KetQuaThaoTac, YeuCau, chay_thao_tac
from tram.thao_tac.chung import TAC_NHAN, NguCanhGhi, ghi_su_kien_mot_lan, kiem_version
from tram.thao_tac.loi import ChuaHoTro, KhongHopLe

NHAN_REVIEW = "cot:cho-review"


def ly_do_duyet(pr: str | None) -> str:
    if pr:
        return (f"Đại ca xác nhận đã merge PR {pr} trên GitHub — thao tác tay trên dashboard, "
                "không phải bằng chứng máy")
    return "Đại ca duyệt trên dashboard"


def _kiem_cot_3(nc: NguCanhGhi, bead_id: str, expected_version: str) -> None:
    b = nc.bd.mot(bead_id)
    if "cho-duyet-spec" in b.labels:
        raise ChuaHoTro("Duyệt / Trả về spec được nối ở phần 4b")
    kiem_version(b, expected_version)
    if NHAN_REVIEW not in b.labels or not hien_tren_bang(b):     # đã đóng hoặc hoãn (Q2)
        raise KhongHopLe("Chỉ thao tác với bead đang chờ review (cột 3)")


def duyet(nc: NguCanhGhi, bead_id: str, *, ma: str, expected_version: str, expected_commit: str | None = None,
          digest_bead: str | None = None) -> KetQuaThaoTac:
    def dong(_) -> dict:
        b = nc.bd.mot(bead_id)
        tt = tom_tat_ban_giao(b.notes)
        pr = tt["pr"] if tt else None
        if b.status != "closed":
            nc.bd.dong(bead_id, ly_do_duyet(pr))
        return {"pr": pr}

    yc = YeuCau(ma, "duyet", nc.du_an, bead_id, {"expected_commit": expected_commit, "digest_bead": digest_bead},
                expected_version)
    return chay_thao_tac(nc.kho_tt, yc, kiem_moi=lambda: _kiem_cot_3(nc, bead_id, expected_version),
                         cac_buoc=[("dong", dong)])


def tra_ve(nc: NguCanhGhi, bead_id: str, *, gop_y: str, ma: str, expected_version: str) -> KetQuaThaoTac:
    gop_y = gop_y.strip()
    if not gop_y:
        raise KhongHopLe("Cần góp ý khi trả về")
    dau = f"(ma_thao_tac {ma})"

    def nhan_va_ghi_chu(_) -> dict:
        b = nc.bd.mot(bead_id)                     # đối soát: notes đã có dấu mã thì không ghi lại
        bo = [n for n in b.labels if n.startswith("cot:") or n == NHAN_KHOA]
        gio = doc_luc(bay_gio()).astimezone(GIO_VN).strftime("%Y-%m-%d %H:%M")
        ghi_chu = None if dau in b.notes else f"[{TAC_NHAN} {gio}] Trả về: {gop_y} {dau}"
        if bo or ghi_chu:
            nc.bd.cap_nhat_nhan(bead_id, bo=bo, ghi_chu=ghi_chu)
        return {"bo": bo}

    def su_kien(_) -> bool:
        return ghi_su_kien_mot_lan(nc.kho, nc.du_an, bead_id, "cot.tra_ve", {"gop_y": gop_y}, ma=ma)

    yc = YeuCau(ma, "tra_ve", nc.du_an, bead_id, {"gop_y": gop_y}, expected_version)
    return chay_thao_tac(nc.kho_tt, yc, kiem_moi=lambda: _kiem_cot_3(nc, bead_id, expected_version),
                         cac_buoc=[("nhan_va_ghi_chu", nhan_va_ghi_chu), ("su_kien", su_kien)])


def tra_loi_decision(nc: NguCanhGhi, bead_id: str, *, tra_loi: str, ma: str,
                     expected_version: str) -> KetQuaThaoTac:
    """Escalation hoặc decision mở: `bd close <decision> --reason <trả lời>` — đóng **chính** decision;
    sự kiện dùng chung `escalation.tra_loi {escalation_id = id decision}` (spec 2 §12.2)."""
    tra_loi = tra_loi.strip()
    if not tra_loi:
        raise KhongHopLe("Cần câu trả lời")

    def kiem_moi() -> None:
        b = nc.bd.mot(bead_id)
        kiem_version(b, expected_version)
        if (ly_do := ly_do_khong_tra_loi(b)) is not None:
            raise KhongHopLe(ly_do)

    def dong(_) -> bool:
        if nc.bd.mot(bead_id).status != "closed":
            nc.bd.dong(bead_id, tra_loi)           # câu trả lời = close_reason; không mở quyền nguy hiểm (Q6)
        return True

    def su_kien(_) -> bool:
        return ghi_su_kien_mot_lan(nc.kho, nc.du_an, bead_id, "escalation.tra_loi", {"escalation_id": bead_id}, ma=ma)

    yc = YeuCau(ma, "tra_loi", nc.du_an, bead_id, {"tra_loi": tra_loi}, expected_version)
    return chay_thao_tac(nc.kho_tt, yc, kiem_moi=kiem_moi, cac_buoc=[("dong", dong), ("su_kien", su_kien)])
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_thao_tac_phe_duyet.py -q` → Expected: `13 passed` (thêm `test_tra_loi_decision_mo_khong_phai_escalation`, `test_bead_hoan_khong_duyet_khong_tra_loi`).

- [ ] **Step 5: Commit**

```bash
git add tram/thao_tac/phe_duyet.py tests/test_thao_tac_phe_duyet.py
git commit -m "feat(thao-tac): Duyệt cột 3, Trả về + góp ý, Trả lời escalation / decision mở; chặn bead hoãn; spec 501 tới 4b"
```

---

### Task 16: Estop dùng chung CLI + dashboard

**Độ khó:** `de` · **Song song:** đợt 3 — chạy cùng Task 9, 13, 14, 15, 21, 25 (task duy nhất của đợt sửa `tram/cli.py`). **Phải xong trước:** Task 4. Task 17, 22 cần task này.

**Files:**
- Create: `tram/chu/dieu_khien.py`, `tram/thao_tac/estop.py`
- Modify: `tram/cli.py` (hằng `DU_AN_TRAM`, hàm `_estop`, `_tiep_tuc`)
- Test: `tests/test_estop_2a.py`

**Interfaces:**
- Consumes: `tram.chu.estop.bat/tat`; `KhoSuKien.ghi`; `chay_thao_tac`, `YeuCau`, `TAC_NHAN`, `co_su_kien` (4).
- Produces:
  - `tram/chu/dieu_khien.py`: `DU_AN_TRAM = "_tram"`; `bat_estop(kho, ly_do: str, *, tac_nhan: str, them: dict | None = None) -> None` (cờ estop + `estop.bat {ly_do, **them}`); `tat_estop(kho, *, tac_nhan: str, them: dict | None = None) -> None`.
  - `tram/thao_tac/estop.py`: `LY_DO_MAC_DINH`; `bat_estop_thao_tac(kho, kho_tt, *, ly_do: str | None, ma: str, expected_version: str) -> KetQuaThaoTac`; `tiep_tuc_thao_tac(kho, kho_tt, *, ma: str, expected_version: str) -> KetQuaThaoTac` (G6: không kiểm version; sự kiện có `ma_thao_tac`, `tac_nhan = dai-ca/dashboard`).

- [ ] **Step 1: Viết test thất bại**

`tests/test_estop_2a.py`:

```python
from tram.chu import estop
from tram.chu.dieu_khien import bat_estop, tat_estop
from tram.su_kien.kho import KhoSuKien
from tram.thao_tac.estop import bat_estop_thao_tac, tiep_tuc_thao_tac
from tram.thao_tac.kho import KhoThaoTac


def _kho(tmp_path):
    db = tmp_path / "sk.db"
    return KhoSuKien(db), KhoThaoTac(db)


def test_dieu_khien_dung_chung(tmp_path):
    k, _ = _kho(tmp_path)
    bat_estop(k, "thử", tac_nhan="dai-ca")
    s = k.gan_day("_tram", "estop.bat", 1)[0]
    assert estop.dang_bat() and s.du_lieu == {"ly_do": "thử"} and s.tac_nhan == "dai-ca"
    tat_estop(k, tac_nhan="dai-ca")
    assert not estop.dang_bat() and k.gan_day("_tram", "estop.tat", 1)[0].du_lieu == {}


def test_estop_thao_tac_mot_lan_theo_ma(tmp_path):
    k, kt = _kho(tmp_path)
    a = bat_estop_thao_tac(k, kt, ly_do=None, ma="ma-estop-001", expected_version="tat")
    b = bat_estop_thao_tac(k, kt, ly_do=None, ma="ma-estop-001", expected_version="bat")
    assert estop.dang_bat() and a.lap_lai is False and b.lap_lai is True
    ds = k.gan_day("_tram", "estop.bat", 10)
    assert len(ds) == 1 and ds[0].tac_nhan == "dai-ca/dashboard"
    assert ds[0].du_lieu == {"ly_do": "Đại ca bấm estop trên dashboard", "ma_thao_tac": "ma-estop-001"}


def test_tiep_tuc_thao_tac(tmp_path):
    k, kt = _kho(tmp_path)
    estop.bat("x")
    tiep_tuc_thao_tac(k, kt, ma="ma-tieptuc-01", expected_version="bat")
    assert not estop.dang_bat()
    assert k.gan_day("_tram", "estop.tat", 1)[0].du_lieu == {"ma_thao_tac": "ma-tieptuc-01"}


def test_cli_estop_van_ghi_nhu_cu(tram_home_tam):
    from tram.cli import main
    from tram.su_kien.kho import mo_kho
    assert main(["chu", "estop", "--ly-do", "thử"]) == 0
    s = mo_kho().gan_day("_tram", "estop.bat", 1)[0]
    assert s.tac_nhan == "dai-ca" and s.du_lieu == {"ly_do": "thử"}
    assert main(["chu", "tiep-tuc"]) == 0 and not estop.dang_bat()
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_estop_2a.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'tram.chu.dieu_khien'`.

- [ ] **Step 3: Viết mã**

`tram/chu/dieu_khien.py`:

```python
"""Bật/tắt estop dùng chung cho `tram chu estop|tiep-tuc` và nút trên dashboard (spec 2 §5.3)."""
from tram.chu import estop
from tram.su_kien.kho import KhoSuKien

DU_AN_TRAM = "_tram"


def bat_estop(kho: KhoSuKien, ly_do: str, *, tac_nhan: str, them: dict | None = None) -> None:
    estop.bat(ly_do)
    kho.ghi(DU_AN_TRAM, "estop.bat", {"ly_do": ly_do, **(them or {})}, tac_nhan=tac_nhan)


def tat_estop(kho: KhoSuKien, *, tac_nhan: str, them: dict | None = None) -> None:
    estop.tat()
    kho.ghi(DU_AN_TRAM, "estop.tat", dict(them or {}), tac_nhan=tac_nhan)
```

`tram/thao_tac/estop.py`:

```python
"""Nút estop / tiếp tục của dashboard — cùng logic `tram chu estop` (spec 2 §5.3), idempotent theo ma_thao_tac."""
from collections.abc import Callable

from tram.chu.dieu_khien import DU_AN_TRAM, bat_estop, tat_estop
from tram.thao_tac.chay import KetQuaThaoTac, YeuCau, chay_thao_tac
from tram.thao_tac.chung import TAC_NHAN, co_su_kien

LY_DO_MAC_DINH = "Đại ca bấm estop trên dashboard"


def _chay(kho, kho_tt, loai_sk: str, noi_dung: dict, lam: Callable[[], None], ma: str,
          expected_version: str) -> KetQuaThaoTac:
    def buoc(_) -> bool:
        if not co_su_kien(kho, DU_AN_TRAM, None, loai_sk, ma):   # crash sau khi đặt cờ: đặt lại + ghi sự kiện
            lam()
        return True

    yc = YeuCau(ma, loai_sk, DU_AN_TRAM, None, noi_dung, expected_version)
    # G6: không kiểm expected_version — dừng khẩn cấp không được hỏng vì màn hình cũ.
    return chay_thao_tac(kho_tt, yc, kiem_moi=lambda: None, cac_buoc=[(loai_sk, buoc)])


def bat_estop_thao_tac(kho, kho_tt, *, ly_do: str | None, ma: str, expected_version: str) -> KetQuaThaoTac:
    ly_do = (ly_do or "").strip() or LY_DO_MAC_DINH
    return _chay(kho, kho_tt, "estop.bat", {"ly_do": ly_do},
                 lambda: bat_estop(kho, ly_do, tac_nhan=TAC_NHAN, them={"ma_thao_tac": ma}), ma, expected_version)


def tiep_tuc_thao_tac(kho, kho_tt, *, ma: str, expected_version: str) -> KetQuaThaoTac:
    return _chay(kho, kho_tt, "estop.tat", {},
                 lambda: tat_estop(kho, tac_nhan=TAC_NHAN, them={"ma_thao_tac": ma}), ma, expected_version)
```

Sửa `tram/cli.py`: xoá dòng `DU_AN_TRAM = "_tram"` (không chỗ nào khác dùng — `grep -rn DU_AN_TRAM tram tests` chỉ còn `tram/chu/dieu_khien.py`, `tram/thao_tac/estop.py`), thay hai hàm:

```python
def _estop(args) -> int:
    from tram.chu.dieu_khien import bat_estop
    from tram.su_kien.kho import mo_kho
    bat_estop(mo_kho(), args.ly_do, tac_nhan="dai-ca")
    print("Đã bật estop: mọi lượt quét dừng cho tới khi chạy `tram chu tiep-tuc`.")
    return 0


def _tiep_tuc(args) -> int:
    from tram.chu.dieu_khien import tat_estop
    from tram.su_kien.kho import mo_kho
    tat_estop(mo_kho(), tac_nhan="dai-ca")
    print("Đã tắt estop.")
    return 0
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_estop_2a.py tests/test_quet.py tests/test_chu.py -q`
Expected: `test_estop_2a.py` 4 passed; `test_cli_estop`, `test_cli_estop_ghi_su_kien` (test cũ) vẫn pass.

- [ ] **Step 5: Commit**

```bash
git add tram/chu/dieu_khien.py tram/thao_tac/estop.py tram/cli.py tests/test_estop_2a.py
git commit -m "feat(chu): estop dùng chung CLI và dashboard; thao tác estop/tiếp tục idempotent"
```

---

### Task 17: tram-api — các `POST` ghi

**Độ khó:** `kho` (ghép bảo mật + thao tác + mã lỗi) · **Song song:** đợt 5 — chạy cùng Task 22. **Phải xong trước:** Task 10, 12, 13, 14, 15, 16. Task 18 cần task này (cùng sửa `tram/api/app.py`).

**Files:**
- Create: `tram/api/than.py`, `tram/api/tuyen_ghi.py`, `tram/api/tuyen_chu.py`
- Modify: `tram/api/app.py` (import + `CAC_TUYEN`)
- Test: `tests/test_api_ghi.py`

**Interfaces:**
- Consumes: `yeu_cau_ghi` (10); `kiem_du_an_bead`, `PhuThuocApi` (12); `keo_cot`, `thu_lai` (13); `chot` (14); `duyet`, `tra_ve`, `tra_loi_decision` (15); `bat_estop_thao_tac`, `tiep_tuc_thao_tac` (16); `NguCanhGhi`, `KetQuaThaoTac`, `KhoSuKien.close`/`KhoThaoTac.close` (2, 4).
- Produces:
  - Pydantic (`extra="forbid"`): `ThanGhi(ma_thao_tac: str 8–64, expected_version: str ≤ 100)`; `ThanCot(cot: Literal["ai-lam","can-chot"], vi_sao: str | None ≤ 2000)`; `ThanChot(tra_loi: list[str ≤ 4000] | None ≤ 20 phần tử, adr: str | None ≤ 20)`; `ThanTraVe(gop_y: str 1–4000)`; `ThanTraLoi(tra_loi: str 1–4000)`; `ThanDuyet(expected_commit: str | None ≤ 64, digest_bead: str | None ≤ 128)`; `ThanEstop(ly_do: str | None ≤ 500)`.
  - Route đúng bảng "Hợp đồng JSON" (`/tra-loi` gọi `tra_loi_decision` — escalation hoặc decision mở); mọi route ghi qua `Depends(yeu_cau_ghi)`; trả `{"ket_qua", "lap_lai"}`; mở `kho`, `kho_tt` bằng `contextlib.closing` (N5); sau mọi thao tác bead (kể cả lỗi) đánh dấu bộ đệm dự án cũ. Bead không có → `KhongThayBead` → 404 (C2, test `hr-99`).

- [ ] **Step 1: Viết test thất bại**

`tests/test_api_ghi.py`:

```python
from api_gia import DAI_CA, tao_app_gia
from asgi_gia import goi
from bd_gia import BdGia
from bead_gia import bead
from tram.chu import estop

V = "2026-10-13T01:00:00Z"


def _app(tmp_path, *beads):
    bd = BdGia(beads)
    app, pt = tao_app_gia(tmp_path, {"hr": bd})
    return app, pt, bd


def _than(**kw):
    return {"ma_thao_tac": "ma-api-00001", "expected_version": V, **kw}


def test_ghi_khong_du_danh_tinh_hoac_csrf_bi_403(tmp_path):
    app, _, bd = _app(tmp_path, bead("hr-1", labels=["cot:ai-lam"]))
    for h in ({}, {**DAI_CA, "Tailscale-User-Login": "nguoi-la@example.com"},
              {k: v for k, v in DAI_CA.items() if k != "X-Tram"}, {**DAI_CA, "Origin": "https://evil.example"}):
        r = goi(app, "POST", "/api/bead/hr/hr-1/cot", json_body=_than(cot="can-chot"), headers=h)
        assert r.status == 403
    assert bd.so_lan("cap_nhat_nhan") == 0


def test_keo_cot_qua_api_lap_lai_va_lam_moi_bo_dem(tmp_path):
    app, pt, bd = _app(tmp_path, bead("hr-1", labels=["cot:ai-lam"]))
    pt.bo_dem.lay("hr")
    r = goi(app, "POST", "/api/bead/hr/hr-1/cot", json_body=_than(cot="can-chot", vi_sao="giá"), headers=DAI_CA)
    assert r.status == 200 and r.json()["lap_lai"] is False and "cot:can-chot" in bd.beads["hr-1"].labels
    r2 = goi(app, "POST", "/api/bead/hr/hr-1/cot", json_body=_than(cot="can-chot", vi_sao="giá"), headers=DAI_CA)
    assert r2.json()["lap_lai"] is True and bd.so_lan("cap_nhat_nhan") == 1
    assert bd.so_lan("tat_ca") == 1
    pt.bo_dem.lay("hr")
    assert bd.so_lan("tat_ca") == 2


def test_ma_loi_http(tmp_path):
    app, _, _ = _app(tmp_path, bead("hr-1", labels=["cot:ai-lam"]),
                     bead("hr-2", labels=["cot:cho-review", "cho-duyet-spec"]))
    cot = "/api/bead/hr/hr-1/cot"
    r = goi(app, "POST", cot, json_body=_than(cot="can-chot", expected_version="2026-10-12T00:00:00Z"), headers=DAI_CA)
    assert r.status == 409 and "đã đổi" in r.json()["loi"]
    assert goi(app, "POST", cot, json_body=_than(cot="cho-review"), headers=DAI_CA).status == 422
    assert goi(app, "POST", cot, json_body=_than(cot="can-chot", la="x"), headers=DAI_CA).status == 422
    assert goi(app, "POST", "/api/bead/khong/hr-1/cot", json_body=_than(cot="can-chot"), headers=DAI_CA).status == 404
    assert goi(app, "POST", "/api/bead/hr/hr-99/cot", json_body=_than(cot="can-chot"), headers=DAI_CA).status == 404
    assert goi(app, "POST", "/api/phe-duyet/hr/hr-2/duyet", json_body=_than(), headers=DAI_CA).status == 501


def test_chot_tra_ve_tra_loi_thu_lai(tmp_path):
    app, pt, bd = _app(tmp_path, bead("hr-1", title="Giá", labels=["cot:can-chot"]),
                       bead("hr-2", labels=["cot:cho-review"]),
                       bead("hr-3", issue_type="decision", labels=["tram:escalation"]),
                       bead("hr-4", issue_type="decision", labels=["cot:can-chot"]))
    pt.mo_kho().ghi("hr", "cham_cot.ket_qua", {"cot": "can-chot", "ly_do": "x", "cau_hoi": ["Có VAT?"]}, bead_id="hr-1")
    r = goi(app, "POST", "/api/bead/hr/hr-1/chot", json_body=_than(ma_thao_tac="ma-chot-0001", tra_loi=["Có"]),
            headers=DAI_CA)
    assert r.status == 200 and r.json()["ket_qua"]["tao_decision"].startswith("hr-")
    r = goi(app, "POST", "/api/phe-duyet/hr/hr-2/tra-ve", json_body=_than(ma_thao_tac="ma-trave-001", gop_y="Thiếu test"),
            headers=DAI_CA)
    assert r.status == 200 and "cot:cho-review" not in bd.beads["hr-2"].labels
    r = goi(app, "POST", "/api/phe-duyet/hr/hr-3/tra-loi", json_body=_than(ma_thao_tac="ma-traloi-01", tra_loi="Làm A"),
            headers=DAI_CA)
    assert r.status == 200 and bd.beads["hr-3"].status == "closed"
    r = goi(app, "POST", "/api/phe-duyet/hr/hr-4/tra-loi", json_body=_than(ma_thao_tac="ma-traloi-02", tra_loi="Chọn B"),
            headers=DAI_CA)
    assert r.status == 200 and bd.beads["hr-4"].close_reason == "Chọn B"     # decision mở (Q4)
    r = goi(app, "POST", "/api/bead/hr/hr-1/thu-lai",
            json_body=_than(ma_thao_tac="ma-thulai-01", expected_version=bd.beads["hr-1"].updated_at), headers=DAI_CA)
    assert r.status == 200 and pt.mo_kho().gan_day("hr", "cham_cot.thu_lai", 1)


def test_duyet_dong_bead(tmp_path):
    app, _, bd = _app(tmp_path, bead("hr-2", labels=["cot:cho-review"]))
    r = goi(app, "POST", "/api/phe-duyet/hr/hr-2/duyet", json_body=_than(), headers=DAI_CA)
    assert r.status == 200 and bd.beads["hr-2"].status == "closed"
    assert bd.beads["hr-2"].close_reason == "Đại ca duyệt trên dashboard"


def test_estop_va_tiep_tuc_qua_api(tmp_path):
    app, pt, _ = _app(tmp_path)
    r = goi(app, "POST", "/api/chu/estop",
            json_body={"ma_thao_tac": "ma-estop-001", "expected_version": "tat", "ly_do": "thử"}, headers=DAI_CA)
    assert r.status == 200 and estop.dang_bat()
    assert pt.mo_kho().gan_day("_tram", "estop.bat", 1)[0].du_lieu["ly_do"] == "thử"
    r = goi(app, "POST", "/api/chu/tiep-tuc", json_body={"ma_thao_tac": "ma-tieptuc-01", "expected_version": "bat"},
            headers=DAI_CA)
    assert r.status == 200 and not estop.dang_bat()
    assert goi(app, "POST", "/api/chu/estop",
               json_body={"ma_thao_tac": "ma-estop-002", "expected_version": "tat"}).status == 403
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_api_ghi.py -q`
Expected: FAIL — các POST trả 404/405 (chưa có route), `assert 404 == 403`.

- [ ] **Step 3: Viết mã**

`tram/api/than.py`:

```python
"""Thân yêu cầu POST lát 2a (spec 2 §7, §12.3) — trường lạ bị từ chối (422)."""
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


class ThanGhi(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ma_thao_tac: str = Field(min_length=8, max_length=64)
    expected_version: str = Field(max_length=100)


class ThanCot(ThanGhi):
    cot: Literal["ai-lam", "can-chot"]
    vi_sao: str | None = Field(default=None, max_length=2000)


class ThanChot(ThanGhi):
    tra_loi: list[Annotated[str, Field(max_length=4000)]] | None = Field(default=None, max_length=20)
    adr: str | None = Field(default=None, max_length=20)


class ThanTraVe(ThanGhi):
    gop_y: str = Field(min_length=1, max_length=4000)


class ThanTraLoi(ThanGhi):
    tra_loi: str = Field(min_length=1, max_length=4000)


class ThanDuyet(ThanGhi):
    expected_commit: str | None = Field(default=None, max_length=64)
    digest_bead: str | None = Field(default=None, max_length=128)


class ThanEstop(ThanGhi):
    ly_do: str | None = Field(default=None, max_length=500)
```

`tram/api/tuyen_ghi.py`:

```python
"""POST ghi trên bead (spec 2 §7): cần danh tính Đại ca + CSRF; idempotent theo ma_thao_tac (§12.3)."""
from collections.abc import Callable
from contextlib import closing

from fastapi import APIRouter, Depends, Request

from tram.api.bao_mat import yeu_cau_ghi
from tram.api.phu_thuoc import kiem_du_an_bead
from tram.api.than import ThanChot, ThanCot, ThanDuyet, ThanGhi, ThanTraLoi, ThanTraVe
from tram.thao_tac.chay import KetQuaThaoTac
from tram.thao_tac.chot import chot
from tram.thao_tac.chung import NguCanhGhi
from tram.thao_tac.cot import keo_cot, thu_lai
from tram.thao_tac.phe_duyet import duyet, tra_loi_decision, tra_ve

router = APIRouter(dependencies=[Depends(yeu_cau_ghi)])


def _chay(request: Request, du_an: str, bead_id: str, lam: Callable[[NguCanhGhi], KetQuaThaoTac]) -> dict:
    pt = request.app.state.pt
    kiem_du_an_bead(pt, du_an, bead_id)
    try:
        with closing(pt.mo_kho()) as kho, closing(pt.mo_kho_tt()) as kho_tt:     # N5: đóng kết nối mỗi yêu cầu
            kq = lam(NguCanhGhi(bd=pt.tao_bd(du_an), kho=kho, kho_tt=kho_tt, du_an=du_an))
    finally:
        pt.bo_dem.danh_dau_cu(du_an)               # kể cả khi lỗi giữa chừng: beads có thể đã đổi
    return {"ket_qua": kq.ket_qua, "lap_lai": kq.lap_lai}


@router.post("/api/bead/{du_an}/{bead_id}/cot")
def r_cot(du_an: str, bead_id: str, than: ThanCot, request: Request) -> dict:
    return _chay(request, du_an, bead_id, lambda nc: keo_cot(
        nc, bead_id, cot=than.cot, vi_sao=than.vi_sao, ma=than.ma_thao_tac, expected_version=than.expected_version))


@router.post("/api/bead/{du_an}/{bead_id}/chot")
def r_chot(du_an: str, bead_id: str, than: ThanChot, request: Request) -> dict:
    return _chay(request, du_an, bead_id, lambda nc: chot(
        nc, bead_id, tra_loi=than.tra_loi, adr=than.adr, ma=than.ma_thao_tac, expected_version=than.expected_version))


@router.post("/api/bead/{du_an}/{bead_id}/thu-lai")
def r_thu_lai(du_an: str, bead_id: str, than: ThanGhi, request: Request) -> dict:
    return _chay(request, du_an, bead_id, lambda nc: thu_lai(
        nc, bead_id, ma=than.ma_thao_tac, expected_version=than.expected_version))


@router.post("/api/phe-duyet/{du_an}/{bead_id}/duyet")
def r_duyet(du_an: str, bead_id: str, than: ThanDuyet, request: Request) -> dict:
    return _chay(request, du_an, bead_id, lambda nc: duyet(
        nc, bead_id, ma=than.ma_thao_tac, expected_version=than.expected_version,
        expected_commit=than.expected_commit, digest_bead=than.digest_bead))


@router.post("/api/phe-duyet/{du_an}/{bead_id}/tra-ve")
def r_tra_ve(du_an: str, bead_id: str, than: ThanTraVe, request: Request) -> dict:
    return _chay(request, du_an, bead_id, lambda nc: tra_ve(
        nc, bead_id, gop_y=than.gop_y, ma=than.ma_thao_tac, expected_version=than.expected_version))


@router.post("/api/phe-duyet/{du_an}/{bead_id}/tra-loi")
def r_tra_loi(du_an: str, bead_id: str, than: ThanTraLoi, request: Request) -> dict:
    return _chay(request, du_an, bead_id, lambda nc: tra_loi_decision(
        nc, bead_id, tra_loi=than.tra_loi, ma=than.ma_thao_tac, expected_version=than.expected_version))
```

`tram/api/tuyen_chu.py`:

```python
"""POST estop / tiếp tục từ thanh trạng thái (spec 2 §5.3) — cùng logic `tram chu estop`."""
from contextlib import closing

from fastapi import APIRouter, Depends, Request

from tram.api.bao_mat import yeu_cau_ghi
from tram.api.than import ThanEstop, ThanGhi
from tram.thao_tac.estop import bat_estop_thao_tac, tiep_tuc_thao_tac

router = APIRouter(dependencies=[Depends(yeu_cau_ghi)])


@router.post("/api/chu/estop")
def r_estop(than: ThanEstop, request: Request) -> dict:
    pt = request.app.state.pt
    with closing(pt.mo_kho()) as kho, closing(pt.mo_kho_tt()) as kho_tt:
        kq = bat_estop_thao_tac(kho, kho_tt, ly_do=than.ly_do, ma=than.ma_thao_tac,
                                expected_version=than.expected_version)
    return {"ket_qua": kq.ket_qua, "lap_lai": kq.lap_lai}


@router.post("/api/chu/tiep-tuc")
def r_tiep_tuc(than: ThanGhi, request: Request) -> dict:
    pt = request.app.state.pt
    with closing(pt.mo_kho()) as kho, closing(pt.mo_kho_tt()) as kho_tt:
        kq = tiep_tuc_thao_tac(kho, kho_tt, ma=than.ma_thao_tac, expected_version=than.expected_version)
    return {"ket_qua": kq.ket_qua, "lap_lai": kq.lap_lai}
```

Sửa `tram/api/app.py`: dòng import router và `CAC_TUYEN` thành:

```python
from tram.api import tuyen_chu, tuyen_doc, tuyen_ghi
```

```python
CAC_TUYEN = (tuyen_doc.router, tuyen_ghi.router, tuyen_chu.router)
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_api_ghi.py tests/test_api_doc.py -q`
Expected: `test_api_ghi.py` 6 passed, `test_api_doc.py` 8 passed.

- [ ] **Step 5: Commit**

```bash
git add tram/api/than.py tram/api/tuyen_ghi.py tram/api/tuyen_chu.py tram/api/app.py tests/test_api_ghi.py
git commit -m "feat(api): POST kéo cột, Chốt, thử lại, Duyệt, Trả về, Trả lời, estop — có danh tính + CSRF"
```

---

### Task 18: Luồng SSE `/api/luong`

**Độ khó:** `kho` (async, đẩy thay đổi đúng lúc) · **Song song:** đợt 6 — chạy cùng Task 22 nếu Task 22 chưa xong. **Phải xong trước:** Task 2 (`sau_id`, `id_moi_nhat`), 11, 17 (cùng sửa `app.py`).

**Files:**
- Create: `tram/api/luong.py`
- Modify: `tram/api/app.py` (thêm `luong.router` vào `CAC_TUYEN`)
- Test: `tests/test_luong.py`

**Interfaces:**
- Consumes: `KhoSuKien.sau_id`, `.id_moi_nhat` (2); `BoDemBeads.lay`, `.danh_dau_cu`, `.phien_ban` (11); `LoiBd`.
- Produces: `NHIP_GIAY = 2`; `LOAI_LAM_MOI` (tập loại sự kiện làm bảng/Phê duyệt đổi); `khung(su_kien: str, du_lieu: dict, id: int | None = None) -> str`; `TrangThaiLuong(moc: int, phien_ban: dict[str, int])`; `mot_nhip(kho, bo_dem, cac_du_an: list[str], tt: TrangThaiLuong) -> list[str]` (khung SSE của một nhịp: mọi sự kiện mới → `su_kien`; loại trong `LOAI_LAM_MOI` của dự án thường → đánh dấu bộ đệm cũ; dự án có `phien_ban` đổi → `cong_viec_doi`; có đổi → một `phe_duyet_doi`; nhịp đầu chỉ ghi nhận phiên bản); route `GET /api/luong` (nhận `Last-Event-ID`; không có → bắt đầu từ `id_moi_nhat()`; kho mở bằng `closing` suốt luồng, đóng khi trình duyệt ngắt — N5). Test route bằng cách gọi thật qua `asgi_gia` (FastAPI 0.143: `app.routes` không còn `.path` — G20).

- [ ] **Step 1: Viết test thất bại**

`tests/test_luong.py`:

```python
from api_gia import tao_app_gia
from asgi_gia import goi
from bd_gia import BdGia
from bead_gia import bead
from tram.api.bo_dem import BoDemBeads
from tram.api.luong import TrangThaiLuong, khung, mot_nhip
from tram.su_kien.kho import KhoSuKien


def _moi(tmp_path, bd):
    return KhoSuKien(tmp_path / "sk.db"), BoDemBeads(lambda ten: bd)


def test_khung_dung_dinh_dang():
    assert khung("su_kien", {"a": "ă"}, 7) == 'event: su_kien\nid: 7\ndata: {"a": "ă"}\n\n'
    assert khung("phe_duyet_doi", {}) == "event: phe_duyet_doi\ndata: {}\n\n"


def test_su_kien_moi_va_moc(tmp_path):
    k, bo = _moi(tmp_path, BdGia([bead("hr-1")]))
    k.ghi("hr", "cham_cot.ket_qua", {"cot": "ai-lam"}, bead_id="hr-1")
    tt = TrangThaiLuong(moc=0)
    ra = mot_nhip(k, bo, ["hr"], tt)
    assert len(ra) == 1 and ra[0].startswith("event: su_kien\nid: 1\n") and '"bead_id": "hr-1"' in ra[0]
    assert tt.moc == 1 and tt.phien_ban == {"hr": 1}
    assert mot_nhip(k, bo, ["hr"], tt) == []


def test_quet_xong_lam_moi_va_bao_doi(tmp_path):
    bd = BdGia([bead("hr-1")])
    k, bo = _moi(tmp_path, bd)
    tt = TrangThaiLuong(moc=0)
    mot_nhip(k, bo, ["hr"], tt)
    bd.beads["hr-1"] = bead("hr-1", labels=["cot:ai-lam"], updated_at="2026-10-13T02:00:00Z")
    k.ghi("hr", "quet.xong", {})
    ra = mot_nhip(k, bo, ["hr"], tt)
    assert any(x.startswith("event: cong_viec_doi") and '"du_an": "hr"' in x for x in ra)
    assert ra[-1].startswith("event: phe_duyet_doi")


def test_su_kien_tram_khong_doc_lai_du_an_nhung_bao_phe_duyet(tmp_path):
    bd = BdGia([bead("hr-1")])
    k, bo = _moi(tmp_path, bd)
    tt = TrangThaiLuong(moc=0)
    mot_nhip(k, bo, ["hr"], tt)
    k.ghi("_tram", "estop.bat", {"ly_do": "x"})
    ra = mot_nhip(k, bo, ["hr"], tt)
    assert bd.so_lan("tat_ca") == 1 and ra[-1].startswith("event: phe_duyet_doi")


def test_bd_loi_bo_qua_du_an(tmp_path):
    k, bo = _moi(tmp_path, BdGia(ra_loi_truoc={"tat_ca": 1}))
    assert mot_nhip(k, bo, ["hr"], TrangThaiLuong(moc=0)) == []


def test_tuyen_luong_tra_event_stream(tmp_path):
    app, _ = tao_app_gia(tmp_path, {"hr": BdGia()})
    r = goi(app, "GET", "/api/luong")       # asgi_gia báo ngắt kết nối ngay sau thân → luồng dừng
    assert r.status == 200 and r.headers["content-type"].startswith("text/event-stream")
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_luong.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'tram.api.luong'`.

- [ ] **Step 3: Viết mã**

`tram/api/luong.py`:

```python
"""GET /api/luong (SSE, spec 2 §7): đẩy sự kiện mới theo sau_id, báo bảng / Phê duyệt đổi (D2 ≤ 10 s)."""
import asyncio
import json
from contextlib import closing
from dataclasses import dataclass, field

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from tram.beads.bd import LoiBd

router = APIRouter()
NHIP_GIAY = 2
NHIP_GIU_KET_NOI = 8          # mỗi 8 nhịp (~16 s) một dòng chú thích giữ kết nối
LOAI_LAM_MOI = {"quet.xong", "quet.loi", "cot.dai_ca_sua", "cot.da_chot", "cot.tra_ve", "escalation.tra_loi",
                "cham_cot.thu_lai", "cham_cot.bo_qua", "estop.bat", "estop.tat"}


def khung(su_kien: str, du_lieu: dict, id: int | None = None) -> str:
    dong = [f"event: {su_kien}"] + ([f"id: {id}"] if id is not None else [])
    dong.append(f"data: {json.dumps(du_lieu, ensure_ascii=False)}")
    return "\n".join(dong) + "\n\n"


@dataclass
class TrangThaiLuong:
    moc: int
    phien_ban: dict[str, int] = field(default_factory=dict)


def mot_nhip(kho, bo_dem, cac_du_an: list[str], tt: TrangThaiLuong) -> list[str]:
    ra, can_bao = [], False
    for sk in kho.sau_id(tt.moc, 200):
        ra.append(khung("su_kien", {"id": sk.id, "luc": sk.luc, "du_an": sk.du_an, "bead_id": sk.bead_id,
                                    "loai": sk.loai}, sk.id))
        tt.moc = sk.id
        if sk.loai in LOAI_LAM_MOI:
            can_bao = True
            if not sk.du_an.startswith("_"):
                bo_dem.danh_dau_cu(sk.du_an)
    for du_an in cac_du_an:
        try:
            bo_dem.lay(du_an)
        except LoiBd:
            continue
        pb = bo_dem.phien_ban(du_an)
        if tt.phien_ban.get(du_an) not in (None, pb):
            ra.append(khung("cong_viec_doi", {"du_an": du_an}))
            can_bao = True
        tt.phien_ban[du_an] = pb
    if can_bao:
        ra.append(khung("phe_duyet_doi", {}))
    return ra


@router.get("/api/luong")
async def luong(request: Request) -> StreamingResponse:
    pt = request.app.state.pt
    cuoi = request.headers.get("last-event-id", "")

    async def sinh():
        with closing(pt.mo_kho()) as kho:                      # N5: đóng khi trình duyệt ngắt
            moc = int(cuoi) if cuoi.isdigit() else await asyncio.to_thread(kho.id_moi_nhat)
            tt, dem = TrangThaiLuong(moc=moc), 0
            while not await request.is_disconnected():
                for k in await asyncio.to_thread(mot_nhip, kho, pt.bo_dem, pt.cac_du_an(), tt):
                    yield k
                dem += 1
                if dem % NHIP_GIU_KET_NOI == 0:
                    yield ": nhip\n\n"
                await asyncio.sleep(NHIP_GIAY)

    return StreamingResponse(sinh(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
```

Sửa `tram/api/app.py`:

```python
from tram.api import luong, tuyen_chu, tuyen_doc, tuyen_ghi
```

```python
CAC_TUYEN = (tuyen_doc.router, tuyen_ghi.router, tuyen_chu.router, luong.router)
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_luong.py tests/test_api_doc.py tests/test_api_ghi.py -q`
Expected: `test_luong.py` 6 passed (`test_tuyen_luong_tra_event_stream`: 200 + `text/event-stream`); hai file kia không có fail mới.

- [ ] **Step 5: Commit**

```bash
git add tram/api/luong.py tram/api/app.py tests/test_luong.py
git commit -m "feat(api): SSE /api/luong — sự kiện mới theo sau_id, báo công việc và phê duyệt đổi"
```

---

### Task 19: Báo tin — mô hình tin + chống ồn

**Độ khó:** `kho` (cửa sổ thời gian, giờ yên lặng qua nửa đêm, lưu/nạp trạng thái) · **Song song:** đợt 1 — chạy cùng Task 1, 2, 3, 5, 7, 23 (logic thuần, file riêng). Task 20, 21 cần task này.

**Files:**
- Create: `tram/bao_tin/tin.py`, `tram/bao_tin/chong_on.py`
- Test: `tests/test_chong_on.py`

**Interfaces:**
- Consumes: `GIO_VN` (`tram/cham_cot/ghi.py`).
- Produces:
  - `tram/bao_tin/tin.py`: `LOAI_TIN = ("cho_review", "spec_cho_duyet", "escalation", "co_do", "tram_loi", "estop_bat", "estop_tat")`; `NHAN_LOAI: dict[str, str]`; `Tin(loai: str, du_an: str, bead_id: str | None = None)` (frozen); `soan_tin(loai: str, tins: Sequence[Tin], dashboard_url: str | None) -> str` — chỉ tên dự án, số việc, mã bead (≤ 5, mã phải khớp `[A-Za-z0-9][A-Za-z0-9._-]{0,63}`), link; dự án `_*` chỉ in nhãn loại.
  - `tram/bao_tin/chong_on.py`: `CUA_SO = 5 phút`, `KHONG_LAP = 1 giờ`; `TinGui(loai: str, tins: tuple[Tin, ...])`; `trong_gio_yen_lang(gio_yen_lang: str | None, luc: datetime) -> bool` (giờ VN, hỗ trợ qua nửa đêm); `BoChongOn(gio_yen_lang: str | None = None, trang_thai: dict | None = None)` với `nhan(tins: list[Tin], luc: datetime) -> list[TinGui]`, `den_han(luc: datetime) -> list[TinGui]`, `tra_lai(tg: TinGui) -> None` (gửi lỗi — G11), `trang_thai() -> dict` (JSON được).

Luật (G8, G9): trong giờ yên lặng chỉ `tram_loi` qua; cùng (loại, dự án, bead) đã gửi < 1 giờ → bỏ; loại chưa có cửa sổ mở → gửi ngay mọi tin loại đó trong lô (một `TinGui`) và mở cửa sổ 5 phút; loại đang có cửa sổ → xếp hàng chờ, `den_han` gửi một `TinGui` khi cửa sổ hết và mở cửa sổ mới; cửa sổ hết mà hàng rỗng → đóng. Gửi lỗi (G11, Đại ca chọn 13/10): `tra_lai(tg)` xoá dấu "đã gửi" của các tin trong `tg` (lần lỗi không tính luật 1 giờ), đưa chúng lên đầu hàng chờ của loại, lùi mốc cửa sổ của loại thêm `CUA_SO` (coi như hết hạn) → `den_han` kế tiếp gửi lại ngay.

- [ ] **Step 1: Viết test thất bại**

`tests/test_chong_on.py`:

```python
import json
from datetime import datetime, timedelta, timezone

from tram.bao_tin.chong_on import BoChongOn, trong_gio_yen_lang
from tram.bao_tin.tin import Tin, soan_tin

T0 = datetime(2026, 10, 13, 3, 0, tzinfo=timezone.utc)      # 10:00 giờ Việt Nam


def p(phut):
    return T0 + timedelta(minutes=phut)


def test_tin_dau_gui_ngay_cung_loai_gom_mot_tin():
    ra = BoChongOn().nhan([Tin("cho_review", "hr", "hr-1"), Tin("cho_review", "hr", "hr-2"),
                           Tin("co_do", "hr", "hr-1"), Tin("cho_review", "hr", "hr-1")], T0)
    assert [(g.loai, [t.bead_id for t in g.tins]) for g in ra] == [("cho_review", ["hr-1", "hr-2"]),
                                                                   ("co_do", ["hr-1"])]


def test_trong_cua_so_5_phut_thi_gom_den_han():
    bo = BoChongOn()
    bo.nhan([Tin("cho_review", "hr", "hr-1")], T0)
    assert bo.nhan([Tin("cho_review", "hr", "hr-2")], p(1)) == []
    assert bo.nhan([Tin("cho_review", "hr", "hr-3")], p(2)) == []
    assert bo.den_han(p(4)) == []
    ra = bo.den_han(p(5))
    assert len(ra) == 1 and [t.bead_id for t in ra[0].tins] == ["hr-2", "hr-3"]
    assert bo.den_han(p(10)) == []                  # hàng rỗng → đóng cửa sổ
    assert len(bo.nhan([Tin("cho_review", "hr", "hr-4")], p(11))) == 1


def test_khong_gui_lai_cung_loai_bead_trong_1_gio():
    bo = BoChongOn()
    bo.nhan([Tin("co_do", "hr", "hr-1")], T0)
    bo.den_han(p(6))
    assert bo.nhan([Tin("co_do", "hr", "hr-1")], p(30)) == []
    bo.den_han(p(36))
    assert len(bo.nhan([Tin("co_do", "hr", "hr-1")], p(61))) == 1


def test_gio_yen_lang_chi_gui_tram_loi():
    dem = datetime(2026, 10, 12, 17, 30, tzinfo=timezone.utc)   # 00:30 giờ VN
    ra = BoChongOn("23:00-07:00").nhan([Tin("cho_review", "hr", "hr-1"), Tin("tram_loi", "hr")], dem)
    assert [g.loai for g in ra] == ["tram_loi"]
    assert trong_gio_yen_lang("23:00-07:00", dem) and not trong_gio_yen_lang("23:00-07:00", T0)
    assert trong_gio_yen_lang("12:00-14:00", datetime(2026, 10, 13, 6, 0, tzinfo=timezone.utc))   # 13:00 VN
    assert not trong_gio_yen_lang(None, dem)


def test_gui_loi_tra_lai_thi_vong_sau_gui_lai_khong_chan_1_gio():
    bo = BoChongOn()
    (tg,) = bo.nhan([Tin("co_do", "hr", "hr-1"), Tin("co_do", "hr", "hr-2")], T0)
    bo.tra_lai(tg)                                   # Telegram lỗi: xếp lại, xoá dấu "đã gửi"
    ra = bo.den_han(T0 + timedelta(seconds=15))      # vòng sau (15 s) gửi lại cả hai, không chờ 5 phút
    assert [(g.loai, [t.bead_id for t in g.tins]) for g in ra] == [("co_do", ["hr-1", "hr-2"])]
    assert bo.nhan([Tin("co_do", "hr", "hr-1")], p(30)) == []   # lần gửi được mới tính luật 1 giờ


def test_trang_thai_luu_va_nap_lai():
    bo = BoChongOn()
    bo.nhan([Tin("cho_review", "hr", "hr-1")], T0)
    bo.nhan([Tin("cho_review", "hr", "hr-2")], p(1))
    bo2 = BoChongOn(None, json.loads(json.dumps(bo.trang_thai())))
    assert [t.bead_id for t in bo2.den_han(p(5))[0].tins] == ["hr-2"]


def test_soan_tin_khong_co_noi_dung_nghiep_vu():
    s = soan_tin("cho_review", (Tin("cho_review", "hr", "hr-1"), Tin("cho_review", "hr", "hr-2"),
                                Tin("cho_review", "web", "web-1")), "https://may-b.tail.ts.net/")
    assert s == ("[tram] hr · 2 việc chờ review (hr-1, hr-2) · web · 1 việc chờ review (web-1)"
                 " → https://may-b.tail.ts.net/")
    assert soan_tin("estop_bat", (Tin("estop_bat", "_tram"),), None) == "[tram] estop BẬT"
    assert soan_tin("tram_loi", (Tin("tram_loi", "hr", "id lạ;x"),), None) == "[tram] hr · 1 trạm lỗi"
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_chong_on.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'tram.bao_tin.chong_on'`.

- [ ] **Step 3: Viết mã**

`tram/bao_tin/tin.py`:

```python
"""Tin Telegram (spec 2 §6): chỉ mã bead, loại việc, tên dự án, link — không nội dung nghiệp vụ (§4 mục 5)."""
import re
from collections.abc import Sequence
from dataclasses import dataclass

LOAI_TIN = ("cho_review", "spec_cho_duyet", "escalation", "co_do", "tram_loi", "estop_bat", "estop_tat")
NHAN_LOAI = {"cho_review": "việc chờ review", "spec_cho_duyet": "spec chờ duyệt", "escalation": "escalation bí",
             "co_do": "cờ đỏ", "tram_loi": "trạm lỗi", "estop_bat": "estop BẬT", "estop_tat": "estop tắt"}
ID_AN_TOAN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}")


@dataclass(frozen=True)
class Tin:
    loai: str
    du_an: str
    bead_id: str | None = None


def soan_tin(loai: str, tins: Sequence[Tin], dashboard_url: str | None) -> str:
    theo: dict[str, list[str]] = {}
    for t in tins:
        theo.setdefault(t.du_an, []).append(t.bead_id if t.bead_id and ID_AN_TOAN.fullmatch(t.bead_id) else "")
    phan = []
    for du_an in sorted(theo):
        if du_an.startswith("_"):
            phan.append(NHAN_LOAI[loai])
            continue
        ma = [i for i in theo[du_an] if i]
        s = f"{du_an} · {len(theo[du_an])} {NHAN_LOAI[loai]}"
        if ma:
            s += f" ({', '.join(ma[:5])}{', …' if len(ma) > 5 else ''})"
        phan.append(s)
    return "[tram] " + " · ".join(phan) + (f" → {dashboard_url}" if dashboard_url else "")
```

`tram/bao_tin/chong_on.py`:

```python
"""Chống ồn Telegram (spec 2 §6): tin đầu gửi ngay, gom phần sau trong 5 phút, không lặp trong 1 giờ, giờ yên lặng;
gửi lỗi thì xếp lại cho vòng sau."""
from dataclasses import dataclass
from datetime import datetime, time, timedelta

from tram.bao_tin.tin import Tin
from tram.cham_cot.ghi import GIO_VN

CUA_SO = timedelta(minutes=5)
KHONG_LAP = timedelta(hours=1)
LOAI_LUON_GUI = "tram_loi"


@dataclass(frozen=True)
class TinGui:
    loai: str
    tins: tuple[Tin, ...]


def _khoa(t: Tin) -> str:
    return f"{t.loai}|{t.du_an}|{t.bead_id or ''}"


def _gio(s: str) -> time:
    h, m = s.split(":")
    return time(int(h), int(m))


def trong_gio_yen_lang(gio_yen_lang: str | None, luc: datetime) -> bool:
    if not gio_yen_lang:
        return False
    bat, ket = (_gio(x) for x in gio_yen_lang.split("-"))
    t = luc.astimezone(GIO_VN).time()
    return bat <= t < ket if bat < ket else (t >= bat or t < ket)


class BoChongOn:
    def __init__(self, gio_yen_lang: str | None = None, trang_thai: dict | None = None):
        tt = trang_thai or {}
        self._yen = gio_yen_lang
        self._da_gui: dict[str, str] = dict(tt.get("da_gui", {}))
        self._cua_so: dict[str, str] = dict(tt.get("cua_so", {}))
        self._cho: dict[str, list[list]] = {k: [list(x) for x in v] for k, v in tt.get("cho", {}).items()}

    def trang_thai(self) -> dict:
        return {"da_gui": self._da_gui, "cua_so": self._cua_so, "cho": self._cho}

    def _duoc_gui(self, t: Tin, luc: datetime) -> bool:
        if t.loai != LOAI_LUON_GUI and trong_gio_yen_lang(self._yen, luc):
            return False
        cu = self._da_gui.get(_khoa(t))
        return cu is None or luc - datetime.fromisoformat(cu) >= KHONG_LAP

    def _gui(self, loai: str, tins: list[Tin], luc: datetime) -> TinGui:
        self._cua_so[loai] = luc.isoformat()
        for t in tins:
            self._da_gui[_khoa(t)] = luc.isoformat()
        return TinGui(loai, tuple(tins))

    def nhan(self, tins: list[Tin], luc: datetime) -> list[TinGui]:
        ngay: dict[str, list[Tin]] = {}
        for t in tins:
            if not self._duoc_gui(t, luc):
                continue
            cs = self._cua_so.get(t.loai)
            if cs is not None and luc - datetime.fromisoformat(cs) < CUA_SO:
                hang = self._cho.setdefault(t.loai, [])
                if [t.du_an, t.bead_id] not in hang:
                    hang.append([t.du_an, t.bead_id])
            elif t not in (ds := ngay.setdefault(t.loai, [])):
                ds.append(t)
        return [self._gui(loai, ds, luc) for loai, ds in ngay.items()]

    def tra_lai(self, tg: TinGui) -> None:
        """Gửi lỗi (spec 2 §6): xoá dấu 'đã gửi' (không tính luật 1 giờ), đưa tin lên đầu hàng chờ và coi cửa sổ
        đã hết hạn — `den_han` của vòng sau (15 s) gửi lại ngay."""
        for t in tg.tins:
            self._da_gui.pop(_khoa(t), None)
        self._cua_so[tg.loai] = (datetime.fromisoformat(self._cua_so[tg.loai]) - CUA_SO).isoformat()
        hang = self._cho.get(tg.loai, [])
        self._cho[tg.loai] = [[t.du_an, t.bead_id] for t in tg.tins if [t.du_an, t.bead_id] not in hang] + hang

    def den_han(self, luc: datetime) -> list[TinGui]:
        ra = []
        for loai in list(self._cua_so):
            if luc - datetime.fromisoformat(self._cua_so[loai]) < CUA_SO:
                continue
            cho = [t for d, b in self._cho.pop(loai, []) if self._duoc_gui(t := Tin(loai, d, b), luc)]
            if cho:
                ra.append(self._gui(loai, cho, luc))
            else:
                del self._cua_so[loai]
        han = luc - KHONG_LAP
        self._da_gui = {k: v for k, v in self._da_gui.items() if datetime.fromisoformat(v) > han}
        return ra
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_chong_on.py -q` → Expected: `7 passed`.

- [ ] **Step 5: Commit**

```bash
git add tram/bao_tin/tin.py tram/bao_tin/chong_on.py tests/test_chong_on.py
git commit -m "feat(bao-tin): soạn tin không nội dung nghiệp vụ, chống ồn 5 phút / 1 giờ / giờ yên lặng, trả lại khi gửi lỗi"
```

---

### Task 20: Báo tin — nguồn tin từ ảnh beads và sự kiện

**Độ khó:** `de` · **Song song:** đợt 2 — chạy cùng Task 4, 8, 10, 11, 24. **Phải xong trước:** Task 2 (`SuKien.id`, `sau_id`), Task 19 (`Tin`). Task 21 cần task này.

**Files:**
- Create: `tram/bao_tin/nguon.py`
- Test: `tests/test_nguon_tin.py`

**Interfaces:**
- Consumes: `Tin` (19); `KhoSuKien.gan_day` (có `id`); `Bead`.
- Produces: `NHAN_TIN = {"cot:cho-review": "cho_review", "cho-duyet-spec": "spec_cho_duyet", "co-do": "co_do"}`; `NGUONG_QUET_LOI = 3`; `anh_tu_beads(beads) -> dict[str, dict]` (`{id: {"nhan": [..], "status": ..}}`); `tin_tu_anh(du_an, truoc: dict, beads) -> list[Tin]` (nhãn mới xuất hiện trên bead chưa đóng; escalation mới hoặc mở lại); `so_quet_loi_lien_tiep(kho, du_an) -> int`; `tin_tu_su_kien(sk, kho) -> list[Tin]` (`estop.bat/tat` → `estop_bat/tat`; `cham_cot.bo_qua` → `tram_loi` theo bead; `quet.loi` khi đếm ≥ 3 → `tram_loi` theo dự án — G10).

Lát 2a chưa có phần 4 nên nguồn "bead vào cột 3 / spec chờ duyệt / escalation / cờ đỏ" là so ảnh beads trước/sau `quet.xong` (spec §6). Từ phần 4 thay bằng `bead.vao_cot_3`, `spec.xong`, `escalation.tao`; từ phần 3 thêm `khe.cau_dao_ngat` — không làm ở 2a.

- [ ] **Step 1: Viết test thất bại**

`tests/test_nguon_tin.py`:

```python
from bead_gia import bead
from tram.bao_tin.nguon import anh_tu_beads, so_quet_loi_lien_tiep, tin_tu_anh, tin_tu_su_kien
from tram.bao_tin.tin import Tin
from tram.su_kien.kho import KhoSuKien


def test_tin_khi_nhan_moi_xuat_hien():
    truoc = anh_tu_beads([bead("hr-1"), bead("hr-2", labels=["co-do"])])
    sau = [bead("hr-1", labels=["cot:cho-review", "co-do"]), bead("hr-2", labels=["co-do"]),
           bead("hr-3", issue_type="feature", labels=["cho-duyet-spec"]),
           bead("hr-4", status="closed", labels=["cot:cho-review"])]
    assert tin_tu_anh("hr", truoc, sau) == [Tin("cho_review", "hr", "hr-1"), Tin("co_do", "hr", "hr-1"),
                                            Tin("spec_cho_duyet", "hr", "hr-3")]


def test_escalation_moi_hoac_mo_lai():
    esc = {"issue_type": "decision", "labels": ["tram:escalation"]}
    assert tin_tu_anh("hr", {}, [bead("hr-9", **esc)]) == [Tin("escalation", "hr", "hr-9")]
    assert tin_tu_anh("hr", anh_tu_beads([bead("hr-9", **esc)]), [bead("hr-9", **esc)]) == []
    da_dong = anh_tu_beads([bead("hr-9", status="closed", **esc)])
    assert tin_tu_anh("hr", da_dong, [bead("hr-9", **esc)]) == [Tin("escalation", "hr", "hr-9")]


def test_tin_tu_su_kien(tmp_path):
    k = KhoSuKien(tmp_path / "sk.db")
    k.ghi("_tram", "estop.bat", {})
    k.ghi("_tram", "estop.tat", {})
    k.ghi("hr", "cham_cot.bo_qua", {}, bead_id="hr-1")
    k.ghi("hr", "cham_cot.ket_qua", {}, bead_id="hr-1")
    assert [t for s in k.sau_id(0, 10) for t in tin_tu_su_kien(s, k)] == [
        Tin("estop_bat", "_tram"), Tin("estop_tat", "_tram"), Tin("tram_loi", "hr", "hr-1")]


def test_quet_loi_3_lan_lien_moi_bao(tmp_path):
    k = KhoSuKien(tmp_path / "sk.db")
    for _ in range(2):
        k.ghi("hr", "quet.loi", {"loi": "x"})
    assert so_quet_loi_lien_tiep(k, "hr") == 2
    assert tin_tu_su_kien(k.gan_day("hr", "quet.loi", 1)[0], k) == []
    k.ghi("hr", "quet.loi", {"loi": "x"})
    assert tin_tu_su_kien(k.gan_day("hr", "quet.loi", 1)[0], k) == [Tin("tram_loi", "hr")]
    k.ghi("hr", "quet.xong", {})
    k.ghi("hr", "quet.loi", {"loi": "x"})
    assert so_quet_loi_lien_tiep(k, "hr") == 1
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_nguon_tin.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'tram.bao_tin.nguon'`.

- [ ] **Step 3: Viết mã**

`tram/bao_tin/nguon.py`:

```python
"""Nguồn tin lát 2a (spec 2 §6): so ảnh beads trước/sau `quet.xong`; trạm lỗi và estop từ sự kiện."""
from tram.bao_tin.tin import Tin
from tram.beads.mo_hinh import Bead

NHAN_TIN = {"cot:cho-review": "cho_review", "cho-duyet-spec": "spec_cho_duyet", "co-do": "co_do"}
NHAN_ESCALATION = "tram:escalation"
NGUONG_QUET_LOI = 3


def anh_tu_beads(beads: list[Bead]) -> dict[str, dict]:
    return {b.id: {"nhan": sorted(b.labels), "status": b.status} for b in beads}


def tin_tu_anh(du_an: str, truoc: dict, beads: list[Bead]) -> list[Tin]:
    ra = []
    for b in beads:
        if b.status == "closed":
            continue
        cu = truoc.get(b.id) or {"nhan": [], "status": ""}
        ra += [Tin(loai, du_an, b.id) for nhan, loai in NHAN_TIN.items() if nhan in b.labels and nhan not in cu["nhan"]]
        if NHAN_ESCALATION in b.labels and not (NHAN_ESCALATION in cu["nhan"] and cu["status"] != "closed"):
            ra.append(Tin("escalation", du_an, b.id))
    return ra


def so_quet_loi_lien_tiep(kho, du_an: str) -> int:
    xong = kho.gan_day(du_an, "quet.xong", 1)
    moc = xong[0].id if xong else 0
    return sum(1 for s in kho.gan_day(du_an, "quet.loi", 20) if s.id > moc)


def tin_tu_su_kien(sk, kho) -> list[Tin]:
    if sk.loai == "estop.bat":
        return [Tin("estop_bat", sk.du_an)]
    if sk.loai == "estop.tat":
        return [Tin("estop_tat", sk.du_an)]
    if sk.loai == "cham_cot.bo_qua":
        return [Tin("tram_loi", sk.du_an, sk.bead_id)]
    if sk.loai == "quet.loi" and so_quet_loi_lien_tiep(kho, sk.du_an) >= NGUONG_QUET_LOI:
        return [Tin("tram_loi", sk.du_an)]
    return []
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_nguon_tin.py -q` → Expected: `4 passed`.

- [ ] **Step 5: Commit**

```bash
git add tram/bao_tin/nguon.py tests/test_nguon_tin.py
git commit -m "feat(bao-tin): nguồn tin từ ảnh beads sau quet.xong và từ sự kiện trạm lỗi / estop"
```

---

### Task 21: Báo tin — gửi Telegram (`urllib`), lưu trạng thái, vòng lặp `tram-bao-tin`

**Độ khó:** `kho` (bí mật, bền, không kẹt vòng) · **Song song:** đợt 3 — chạy cùng Task 9, 13, 14, 15, 16, 25. **Phải xong trước:** Task 5 (`nap_cau_hinh_tram`), 19, 20. Task 22 cần task này.

**Files:**
- Create: `tram/bao_tin/telegram.py`, `tram/bao_tin/luu.py`, `tram/bao_tin/vong.py`
- Test: `tests/test_bao_tin.py`

**Interfaces:**
- Consumes: `BoChongOn`, `TinGui` (19); `soan_tin` (19); `anh_tu_beads`, `tin_tu_anh`, `tin_tu_su_kien` (20); `KhoSuKien.sau_id`, `.id_moi_nhat` (2); `nap_cau_hinh_tram` (5); `Bd`, `LoiBd`; `nap_du_an`; `tram_home`; `mo_kho`.
- Produces:
  - `tram/bao_tin/telegram.py`: `KEYCHAIN_TELEGRAM = "tram-telegram-bot-token"`, `BIEN_MOI_TRUONG = "TRAM_TELEGRAM_BOT_TOKEN"`, `class LoiTelegram(RuntimeError)`; `doc_token(*, chay=subprocess.run) -> str | None` (biến môi trường trước, rồi Keychain); `gui_telegram(token, chat_id, van_ban, *, mo=urllib.request.urlopen, thoi_gian_cho=10.0) -> None` (POST JSON tới `https://api.telegram.org/bot<token>/sendMessage`, `disable_web_page_preview`; mọi lỗi → `LoiTelegram` đã che token, không xâu chuỗi ngoại lệ gốc).
  - `tram/bao_tin/luu.py`: `doc_json(p: Path, mac_dinh)` (thiếu/hỏng → mặc định); `ghi_json(p: Path, du_lieu) -> None` (ghi file tạm rồi `os.replace`).
  - `tram/bao_tin/vong.py`: `CHU_KY_GIAY = 15`; `NguCanhBaoTin(kho, tao_bd, gui: Callable[[str], None], thu_muc: Path, gio_yen_lang=None, dashboard_url=None, bay_gio=<UTC now>)`; `mot_vong(nc) -> int` (số tin đã gửi; xả `den_han` trước `nhan`; `LoiTelegram` → in lỗi + `bo.tra_lai(tg)` — G11); `chay_mai(nc, *, nghi=time.sleep, chu_ky_giay=15, so_vong: int | None = None) -> None` (lỗi một vòng chỉ in ra stderr); `tao_ngu_canh_that() -> NguCanhBaoTin | None` (`None` khi thiếu `telegram.chat_id` hoặc token).

Trạng thái riêng của `tram-bao-tin` (mốc `sau_id` riêng — spec §6) nằm ở `~/.tram/bao-tin/`: `moc.json`, `chong-on.json`, `anh-<du_an>.json`. Lần chạy đầu chỉ đặt mốc = `id_moi_nhat()` (không gửi lịch sử); ảnh đầu tiên của một dự án chỉ làm mốc. Ảnh và mốc ghi **sau** khi gửi. Tin gửi lỗi không mất: nằm lại trong hàng chờ của `chong-on.json`, vòng sau (15 s) gửi lại; mốc vẫn tiến để không sinh tin trùng.

- [ ] **Step 1: Viết test thất bại**

`tests/test_bao_tin.py`:

```python
import json
import subprocess
import urllib.error
from datetime import datetime, timezone

import pytest

from bd_gia import BdGia
from bead_gia import bead
from tram.bao_tin.luu import doc_json, ghi_json
from tram.bao_tin.telegram import LoiTelegram, doc_token, gui_telegram
from tram.bao_tin.vong import NguCanhBaoTin, chay_mai, mot_vong, tao_ngu_canh_that
from tram.su_kien.kho import KhoSuKien

T0 = datetime(2026, 10, 13, 3, 0, tzinfo=timezone.utc)


class PhanHoiGia:
    def __init__(self, du_lieu):
        self._d = json.dumps(du_lieu).encode()

    def read(self):
        return self._d

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def test_gui_telegram_dung_yeu_cau():
    goi = []

    def mo(yc, timeout):
        goi.append((yc, timeout))
        return PhanHoiGia({"ok": True})

    gui_telegram("123:ABC", "42", "[tram] hr · 1 cờ đỏ (hr-1)", mo=mo)
    yc, timeout = goi[0]
    assert yc.full_url == "https://api.telegram.org/bot123:ABC/sendMessage" and yc.get_method() == "POST"
    assert json.loads(yc.data) == {"chat_id": "42", "text": "[tram] hr · 1 cờ đỏ (hr-1)",
                                   "disable_web_page_preview": True}
    assert timeout == 10.0


def test_gui_telegram_loi_che_token():
    def mo(yc, timeout):
        raise urllib.error.URLError(f"không tới được {yc.full_url}")

    with pytest.raises(LoiTelegram) as e:
        gui_telegram("123:ABC", "42", "x", mo=mo)
    assert "123:ABC" not in str(e.value) and "***" in str(e.value) and e.value.__cause__ is None
    with pytest.raises(LoiTelegram):
        gui_telegram("t", "42", "x", mo=lambda yc, timeout: PhanHoiGia({"ok": False, "description": "chat not found"}))


def test_doc_token_env_roi_keychain(monkeypatch):
    monkeypatch.setenv("TRAM_TELEGRAM_BOT_TOKEN", " abc ")
    assert doc_token(chay=lambda *a, **k: pytest.fail("không được gọi Keychain")) == "abc"
    monkeypatch.delenv("TRAM_TELEGRAM_BOT_TOKEN")
    assert doc_token(chay=lambda lenh, **k: subprocess.CompletedProcess(lenh, 0, "tok\n", "")) == "tok"
    assert doc_token(chay=lambda lenh, **k: subprocess.CompletedProcess(lenh, 44, "", "")) is None


def test_luu_json_nguyen_tu_va_file_hong(tmp_path):
    p = tmp_path / "a" / "x.json"
    assert doc_json(p, {"mac": 1}) == {"mac": 1}
    ghi_json(p, {"ă": 2})
    assert doc_json(p, None) == {"ă": 2} and not list(p.parent.glob("*.tam"))
    p.write_text("{hỏng", encoding="utf-8")
    assert doc_json(p, "md") == "md"


def _nc(tmp_path, bd, gui):
    return NguCanhBaoTin(kho=KhoSuKien(tmp_path / "sk.db"), tao_bd=lambda ten: bd, gui=gui,
                         thu_muc=tmp_path / "bao-tin", dashboard_url="https://may-b.tail.ts.net/",
                         bay_gio=lambda: T0)


def test_mot_vong_tu_moc_den_tin(tmp_path):
    da_gui, bd = [], BdGia([bead("hr-1")])
    nc = _nc(tmp_path, bd, da_gui.append)
    nc.kho.ghi("hr", "quet.xong", {})              # sự kiện cũ trước khi dịch vụ chạy
    assert mot_vong(nc) == 0                       # lần đầu: chỉ đặt mốc
    nc.kho.ghi("hr", "quet.xong", {})
    assert mot_vong(nc) == 0                       # ảnh đầu của dự án: làm mốc, không báo
    bd.beads["hr-1"] = bead("hr-1", labels=["cot:cho-review"], updated_at="2026-10-13T02:00:00Z")
    nc.kho.ghi("hr", "quet.xong", {})
    assert mot_vong(nc) == 1
    assert da_gui == ["[tram] hr · 1 việc chờ review (hr-1) → https://may-b.tail.ts.net/"]
    assert mot_vong(nc) == 0


def test_mot_vong_gui_loi_thi_vong_sau_gui_lai(tmp_path, capsys):
    loi, da_gui = {"con": True}, []

    def gui(van_ban):
        if loi["con"]:
            raise LoiTelegram("Gửi Telegram lỗi: ***")
        da_gui.append(van_ban)

    nc = _nc(tmp_path, BdGia(), gui)
    mot_vong(nc)
    nc.kho.ghi("_tram", "estop.bat", {"ly_do": "x"})
    assert mot_vong(nc) == 0 and "Gửi Telegram lỗi" in capsys.readouterr().err
    assert json.loads((tmp_path / "bao-tin" / "moc.json").read_text())["sau_id"] == 1   # mốc tiến, tin nằm ở hàng chờ
    loi["con"] = False
    assert mot_vong(nc) == 1 and da_gui == ["[tram] estop BẬT → https://may-b.tail.ts.net/"]
    assert mot_vong(nc) == 0


def test_chay_mai_nuot_loi_tung_vong(monkeypatch, capsys):
    import tram.bao_tin.vong as v
    dem = []
    monkeypatch.setattr(v, "mot_vong", lambda nc: (dem.append(1), 1 / 0))
    v.chay_mai(object(), nghi=lambda s: None, so_vong=2)
    assert len(dem) == 2 and "ZeroDivisionError" in capsys.readouterr().err


def test_tao_ngu_canh_that_thieu_chat_id_la_none(tram_home_tam):
    assert tao_ngu_canh_that() is None
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_bao_tin.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'tram.bao_tin.luu'`.

- [ ] **Step 3: Viết mã**

`tram/bao_tin/telegram.py`:

```python
"""Gửi Telegram bằng urllib (spec 2 §6, §8 — không SDK). Token chỉ đọc từ biến môi trường / Keychain do Đại ca đặt."""
import json
import os
import subprocess
import urllib.error
import urllib.request

KEYCHAIN_TELEGRAM = "tram-telegram-bot-token"
BIEN_MOI_TRUONG = "TRAM_TELEGRAM_BOT_TOKEN"
API = "https://api.telegram.org/bot{token}/sendMessage"


class LoiTelegram(RuntimeError):
    pass


def doc_token(*, chay=subprocess.run) -> str | None:
    if os.environ.get(BIEN_MOI_TRUONG, "").strip():
        return os.environ[BIEN_MOI_TRUONG].strip()
    kq = chay(["security", "find-generic-password", "-s", KEYCHAIN_TELEGRAM, "-w"], capture_output=True, text=True)
    return (kq.stdout.strip() or None) if kq.returncode == 0 else None


def _che(s: str, token: str) -> str:
    return s.replace(token, "***") if token else s


def gui_telegram(token: str, chat_id: str, van_ban: str, *, mo=urllib.request.urlopen,
                 thoi_gian_cho: float = 10.0) -> None:
    yc = urllib.request.Request(
        API.format(token=token), method="POST", headers={"Content-Type": "application/json"},
        data=json.dumps({"chat_id": chat_id, "text": van_ban, "disable_web_page_preview": True}).encode())
    try:
        with mo(yc, timeout=thoi_gian_cho) as r:
            kq = json.loads(r.read() or b"{}")
    except (urllib.error.URLError, OSError, ValueError) as e:
        raise LoiTelegram(_che(f"Gửi Telegram lỗi: {e}", token)) from None    # không xâu chuỗi: URL chứa token
    if not kq.get("ok"):
        raise LoiTelegram(_che(f"Telegram từ chối: {str(kq.get('description', ''))[:200]}", token))
```

`tram/bao_tin/luu.py`:

```python
"""Trạng thái riêng của tram-bao-tin (~/.tram/bao-tin/): ghi nguyên tử, file hỏng thì dùng mặc định."""
import json
import os
import sys
from pathlib import Path


def doc_json(p: Path, mac_dinh):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return mac_dinh
    except ValueError:
        print(f"bao-tin: {p} hỏng — dùng mặc định", file=sys.stderr)
        return mac_dinh


def ghi_json(p: Path, du_lieu) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    tam = p.with_name(p.name + ".tam")
    tam.write_text(json.dumps(du_lieu, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    os.replace(tam, p)
```

`tram/bao_tin/vong.py`:

```python
"""Vòng lặp tram-bao-tin (spec 2 §6): đọc sự kiện mới theo mốc riêng → nguồn tin → chống ồn → Telegram."""
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from tram.bao_tin.chong_on import BoChongOn
from tram.bao_tin.luu import doc_json, ghi_json
from tram.bao_tin.nguon import anh_tu_beads, tin_tu_anh, tin_tu_su_kien
from tram.bao_tin.telegram import LoiTelegram
from tram.bao_tin.tin import soan_tin
from tram.beads.bd import LoiBd

CHU_KY_GIAY = 15


def _bay_gio_utc() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class NguCanhBaoTin:
    kho: object
    tao_bd: Callable[[str], object]
    gui: Callable[[str], None]
    thu_muc: Path
    gio_yen_lang: str | None = None
    dashboard_url: str | None = None
    bay_gio: Callable[[], datetime] = _bay_gio_utc


def _anh(nc: NguCanhBaoTin, du_an: str) -> tuple[list, dict | None]:
    try:
        beads = nc.tao_bd(du_an).tat_ca()
    except (LoiBd, OSError, ValueError) as e:
        print(f"bao-tin {du_an}: {e}", file=sys.stderr)
        return [], None
    truoc = doc_json(nc.thu_muc / f"anh-{du_an}.json", None)
    return ([] if truoc is None else tin_tu_anh(du_an, truoc, beads)), anh_tu_beads(beads)


def mot_vong(nc: NguCanhBaoTin) -> int:
    p_moc = nc.thu_muc / "moc.json"
    moc = doc_json(p_moc, None)
    if moc is None:
        ghi_json(p_moc, {"sau_id": nc.kho.id_moi_nhat()})
        return 0
    ds = nc.kho.sau_id(moc["sau_id"], 500)
    tins = [t for sk in ds for t in tin_tu_su_kien(sk, nc.kho)]
    anh_moi = {}
    for du_an in sorted({sk.du_an for sk in ds if sk.loai == "quet.xong" and not sk.du_an.startswith("_")}):
        them, anh = _anh(nc, du_an)
        tins += them
        if anh is not None:
            anh_moi[du_an] = anh
    p_co = nc.thu_muc / "chong-on.json"
    bo, luc, da_gui = BoChongOn(nc.gio_yen_lang, doc_json(p_co, None)), nc.bay_gio(), 0
    for tg in bo.den_han(luc) + bo.nhan(tins, luc):  # hàng chờ (kể cả tin gửi lỗi vòng trước) trước, tin mới sau
        try:
            nc.gui(soan_tin(tg.loai, tg.tins, nc.dashboard_url))
            da_gui += 1
        except LoiTelegram as e:
            print(f"bao-tin: {e} — xếp lại, gửi lại vòng sau", file=sys.stderr)
            bo.tra_lai(tg)
    ghi_json(p_co, bo.trang_thai())
    for du_an, anh in anh_moi.items():
        ghi_json(nc.thu_muc / f"anh-{du_an}.json", anh)
    if ds:
        ghi_json(p_moc, {"sau_id": ds[-1].id})
    return da_gui


def chay_mai(nc, *, nghi=time.sleep, chu_ky_giay: int = CHU_KY_GIAY, so_vong: int | None = None) -> None:
    i = 0
    while so_vong is None or i < so_vong:
        try:
            mot_vong(nc)
        except Exception as e:                       # một vòng lỗi không được giết dịch vụ
            print(f"bao-tin: vòng lỗi {type(e).__name__}: {e}", file=sys.stderr)
        i += 1
        nghi(chu_ky_giay)


def tao_ngu_canh_that() -> NguCanhBaoTin | None:
    from tram.bao_tin.telegram import doc_token, gui_telegram
    from tram.beads.bd import Bd
    from tram.cau_hinh.du_an import nap_du_an
    from tram.cau_hinh.tram import nap_cau_hinh_tram
    from tram.duong_dan import tram_home
    from tram.su_kien.kho import mo_kho

    ch = nap_cau_hinh_tram()
    if not ch.telegram.chat_id:
        return None
    token = doc_token()
    if not token:
        return None
    return NguCanhBaoTin(kho=mo_kho(), tao_bd=lambda ten: Bd(nap_du_an(ten).duong_dan),
                         gui=lambda vb: gui_telegram(token, ch.telegram.chat_id, vb), thu_muc=tram_home() / "bao-tin",
                         gio_yen_lang=ch.telegram.gio_yen_lang, dashboard_url=ch.dashboard_url)
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_bao_tin.py -q` → Expected: `8 passed` (gồm `test_mot_vong_gui_loi_thi_vong_sau_gui_lai`). `wc -l tram/bao_tin/vong.py` = 102.

- [ ] **Step 5: Commit**

```bash
git add tram/bao_tin/telegram.py tram/bao_tin/luu.py tram/bao_tin/vong.py tests/test_bao_tin.py
git commit -m "feat(bao-tin): gửi Telegram qua urllib (che token), mốc sau_id riêng, vòng lặp tram-bao-tin, gửi lại khi lỗi"
```

---

### Task 22: Lệnh `tram api`, `tram bao-tin`, `tram chu sao-luu` + kế hoạch launchd

**Độ khó:** `de` · **Song song:** đợt 5 — chạy cùng Task 17 (không chung file). **Phải xong trước:** Task 3, 12, 16 (cùng sửa `tram/cli.py`), 21.

**Files:**
- Create: `tram/cli_dich_vu.py`
- Modify: `tram/cli.py` (hai dòng trong `tao_parser`), `tram/chu/launchd.py` (cả file), `tram/chu/cai_dat.py` (cả file)
- Test: `tests/test_cli_dich_vu.py`

**Interfaces:**
- Consumes: `tao_app` (12), `phu_thuoc_that` (12), `sao_luu` (3), `chay_mai`, `mot_vong`, `tao_ngu_canh_that` (21), `KEYCHAIN_TELEGRAM` (21).
- Produces:
  - `tram/cli_dich_vu.py`: `HOST = "127.0.0.1"`, `CONG_MAC_DINH = 7700`, `them_lenh(sub, chu) -> None` (đăng ký `tram api [--cong N]` — **không** có tuỳ chọn host; chạy `uvicorn.run(tao_app(pt, cong=N), host=HOST, port=N, server_header=False)` (N9, G22); `tram bao-tin [--mot-lan]`; `tram chu sao-luu [--giu N]`).
  - `tram/chu/launchd.py`: `NHAN_QUET`, `NHAN_API = "vn.tram.api"`, `NHAN_BAO_TIN = "vn.tram.bao-tin"`, `NHAN_SAO_LUU = "vn.tram.sao-luu"`; `tao_plist(*, uv, repo, log, chu_ky_giay=120)` (giữ nguyên đầu ra); `tao_plist_thuong_truc(nhan, lenh: list[str], *, uv, repo, log) -> bytes` (`RunAtLoad`, `KeepAlive: {SuccessfulExit: false}`); `tao_plist_hang_ngay(nhan, lenh, *, uv, repo, log, gio=3, phut=15) -> bytes`.
  - `tram/chu/cai_dat.py`: `LENH_TAILSCALE_SERVE`; `lap_ke_hoach` ghi 4 plist (quét, api, bao-tin, sao-lưu) + `bootout`/`bootstrap` từng cái; `_canh_bao` thêm token Telegram, `cau-hinh.yaml`, lệnh `tailscale serve` (chờ #5, Đại ca tự chạy) và — khi thiếu token hoặc `cau-hinh.yaml` — dòng nhắc `launchctl kickstart -k gui/<uid>/vn.tram.bao-tin` sau khi cấu hình (N3: `tram bao-tin` thoát mã 0 khi chưa cấu hình, `KeepAlive.SuccessfulExit=false` nên launchd không tự bật lại); `in_ke_hoach` in "gọi ra ngoài: Claude API, api.telegram.org, GitHub" (spec §12.5, Q15). `trang_thai` giữ nguyên.

Task này **chỉ viết mã + test**. Không chạy `tram chu cai-dat` thật (Global Constraints) — Đại ca tự chạy ở Task 26.

- [ ] **Step 1: Viết test thất bại**

`tests/test_cli_dich_vu.py`:

```python
import os
import plistlib
import subprocess
from pathlib import Path

import pytest

from tram.chu import cai_dat
from tram.cli import main


def test_tram_api_chi_nghe_localhost(monkeypatch):
    import uvicorn
    goi = {}
    monkeypatch.setattr(uvicorn, "run", lambda app, **kw: goi.update(kw, app=app))
    assert main(["api"]) == 0
    assert goi["host"] == "127.0.0.1" and goi["port"] == 7700 and goi["app"].title == "tram-api"
    assert goi["server_header"] is False                    # không lộ phiên bản server (spec 2 §4 mục 6)


def test_tram_api_khong_co_tuy_chon_host():
    with pytest.raises(SystemExit):
        main(["api", "--host", "0.0.0.0"])


def test_sao_luu_cli(tram_home_tam, capsys):
    from tram.su_kien.kho import mo_kho
    mo_kho().ghi("hr", "x", {})
    assert main(["chu", "sao-luu", "--giu", "3"]) == 0
    assert len(list((tram_home_tam / "sao-luu").glob("su-kien-*.db"))) == 1
    assert "Đã sao lưu" in capsys.readouterr().out


def test_bao_tin_chua_cau_hinh_thoat_0(capsys):
    assert main(["bao-tin", "--mot-lan"]) == 0 and "Chưa cấu hình" in capsys.readouterr().out


def test_ke_hoach_cai_dat_co_bon_dich_vu(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setattr(cai_dat, "_canh_bao", lambda: [])
    kh = cai_dat.lap_ke_hoach(uv="/u", repo=Path("/r"))
    la = tmp_path / "Library/LaunchAgents"
    assert sorted(p.name for p in kh.tep) == ["vn.tram.api.plist", "vn.tram.bao-tin.plist",
                                              "vn.tram.quet.plist", "vn.tram.sao-luu.plist"]
    api = plistlib.loads(kh.tep[la / "vn.tram.api.plist"])
    assert api["ProgramArguments"] == ["/u", "run", "--project", "/r", "tram", "api"]
    assert api["KeepAlive"] == {"SuccessfulExit": False} and api["RunAtLoad"] is True
    sl = plistlib.loads(kh.tep[la / "vn.tram.sao-luu.plist"])
    assert sl["StartCalendarInterval"] == {"Hour": 3, "Minute": 15}
    assert sl["ProgramArguments"][-3:] == ["tram", "chu", "sao-luu"]
    assert ["launchctl", "bootstrap", f"gui/{os.getuid()}", str(la / "vn.tram.bao-tin.plist")] in kh.lenh
    assert "api.telegram.org" in cai_dat.in_ke_hoach(kh)


def test_canh_bao_telegram_cau_hinh_tailscale(monkeypatch):
    def chay_gia(lenh, **k):
        if lenh[0] == "security":
            return subprocess.CompletedProcess(lenh, 44, "", "")
        return subprocess.CompletedProcess(lenh, 0, "", "")

    monkeypatch.setattr(cai_dat.subprocess, "run", chay_gia)
    cb = "\n".join(cai_dat._canh_bao())
    assert "tram-telegram-bot-token" in cb and "cau-hinh.yaml" in cb and "tailscale serve" in cb
    assert f"launchctl kickstart -k gui/{os.getuid()}/vn.tram.bao-tin" in cb   # bao-tin thoát 0 → launchd không bật lại
```

- [ ] **Step 2: Chạy, thấy fail**

Run: `uv run pytest tests/test_cli_dich_vu.py -q`
Expected: FAIL — `SystemExit: 2` ở `main(["api"])` (lệnh chưa có) và `ImportError` ở các test cài đặt.

- [ ] **Step 3: Viết mã**

`tram/cli_dich_vu.py`:

```python
"""Lệnh dịch vụ lát 2a: `tram api`, `tram bao-tin`, `tram chu sao-luu`."""
HOST = "127.0.0.1"          # spec 2 §4 mục 1: chỉ nghe localhost; ra tailnet chỉ qua `tailscale serve`
CONG_MAC_DINH = 7700


def _api(args) -> int:
    import uvicorn

    from tram.api.app import tao_app
    from tram.api.phu_thuoc import phu_thuoc_that
    uvicorn.run(tao_app(phu_thuoc_that(), cong=args.cong), host=HOST, port=args.cong, log_level="info",
                server_header=False)
    return 0


def _bao_tin(args) -> int:
    from tram.bao_tin.vong import chay_mai, mot_vong, tao_ngu_canh_that
    nc = tao_ngu_canh_that()
    if nc is None:
        print("Chưa cấu hình telegram.chat_id trong ~/.tram/cau-hinh.yaml hoặc chưa có token Telegram "
              "trong Keychain — tram-bao-tin không chạy.")
        return 0
    if args.mot_lan:
        print(f"Đã gửi {mot_vong(nc)} tin.")
        return 0
    chay_mai(nc)
    return 0


def _sao_luu(args) -> int:
    from tram.duong_dan import tram_home
    from tram.su_kien.sao_luu import sao_luu
    print(f"Đã sao lưu: {sao_luu(tram_home() / 'su-kien.db', tram_home() / 'sao-luu', giu=args.giu)}")
    return 0


def them_lenh(sub, chu) -> None:
    a = sub.add_parser("api", help="Chạy tram-api (chỉ nghe 127.0.0.1)")
    a.add_argument("--cong", type=int, default=CONG_MAC_DINH)
    a.set_defaults(ham=_api)
    b = sub.add_parser("bao-tin", help="Chạy dịch vụ báo tin Telegram")
    b.add_argument("--mot-lan", action="store_true", help="Chạy một vòng rồi thoát")
    b.set_defaults(ham=_bao_tin)
    s = chu.add_parser("sao-luu", help="Sao lưu ~/.tram/su-kien.db vào ~/.tram/sao-luu/")
    s.add_argument("--giu", type=int, default=14, help="Số bản giữ lại")
    s.set_defaults(ham=_sao_luu)
```

Sửa `tram/cli.py` — trong `tao_parser`, ngay sau dòng `chu.add_parser("trang-thai", …).set_defaults(ham=_trang_thai)` thêm:

```python
    from tram.cli_dich_vu import them_lenh
    them_lenh(sub, chu)
```

`tram/chu/launchd.py` (cả file):

```python
import plistlib
from pathlib import Path

NHAN_QUET = "vn.tram.quet"
NHAN_API = "vn.tram.api"
NHAN_BAO_TIN = "vn.tram.bao-tin"
NHAN_SAO_LUU = "vn.tram.sao-luu"
# launchd không có ~/.local/bin (nơi `bd` nằm trên máy B) — ghép thêm ở đầu PATH.
PATH_HE_THONG = "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"


def _chung(nhan: str, lenh: list[str], *, uv: str, repo: Path, log: Path) -> dict:
    return {
        "Label": nhan,
        "ProgramArguments": [uv, "run", "--project", str(repo), "tram", *lenh],
        "WorkingDirectory": str(repo),
        "StandardOutPath": str(log),
        "StandardErrorPath": str(log),
        "EnvironmentVariables": {"PATH": f"{Path.home() / '.local/bin'}:{PATH_HE_THONG}"},
    }


def tao_plist(*, uv: str, repo: Path, log: Path, chu_ky_giay: int = 120) -> bytes:
    return plistlib.dumps({**_chung(NHAN_QUET, ["quet", "--ghi"], uv=uv, repo=repo, log=log),
                           "StartInterval": chu_ky_giay, "RunAtLoad": True})


def tao_plist_thuong_truc(nhan: str, lenh: list[str], *, uv: str, repo: Path, log: Path) -> bytes:
    """Dịch vụ chạy liên tục; thoát mã 0 (vd chưa cấu hình Telegram) thì launchd không bật lại."""
    return plistlib.dumps({**_chung(nhan, lenh, uv=uv, repo=repo, log=log),
                           "RunAtLoad": True, "KeepAlive": {"SuccessfulExit": False}})


def tao_plist_hang_ngay(nhan: str, lenh: list[str], *, uv: str, repo: Path, log: Path,
                        gio: int = 3, phut: int = 15) -> bytes:
    return plistlib.dumps({**_chung(nhan, lenh, uv=uv, repo=repo, log=log),
                           "StartCalendarInterval": {"Hour": gio, "Minute": phut}})
```

`tram/chu/cai_dat.py` (cả file):

```python
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from tram.bao_tin.telegram import KEYCHAIN_TELEGRAM
from tram.chu import estop
from tram.chu.launchd import (NHAN_API, NHAN_BAO_TIN, NHAN_QUET, NHAN_SAO_LUU, tao_plist, tao_plist_hang_ngay,
                              tao_plist_thuong_truc)
from tram.duong_dan import tram_home
from tram.llm.claude import KEYCHAIN_DICH_VU

LENH_TAILSCALE_SERVE = ["tailscale", "serve", "--bg", "--https=443", "http://127.0.0.1:7700"]


@dataclass
class KeHoach:
    tep: dict[Path, bytes]
    lenh: list[list[str]]
    canh_bao: list[str]


def _co_keychain(dich_vu: str) -> bool:
    return subprocess.run(["security", "find-generic-password", "-s", dich_vu], capture_output=True).returncode == 0


def _canh_bao() -> list[str]:
    cb = []
    if not shutil.which("tailscale") and not Path("/Applications/Tailscale.app").exists():
        cb.append("Chưa thấy Tailscale — Đại ca cài và đăng nhập trước (#5, chưa duyệt).")
    if not _co_keychain(KEYCHAIN_DICH_VU):
        cb.append(f"Chưa có API key trong Keychain. Đại ca tự chạy: "
                  f"security add-generic-password -s {KEYCHAIN_DICH_VU} -a tram -w")
    thieu_tin = not _co_keychain(KEYCHAIN_TELEGRAM)
    if thieu_tin:
        cb.append(f"Chưa có token bot Telegram. Đại ca tự tạo bot (@BotFather) rồi chạy: "
                  f"security add-generic-password -s {KEYCHAIN_TELEGRAM} -a tram -w")
    if not (tram_home() / "cau-hinh.yaml").exists():
        thieu_tin = True
        cb.append("Chưa có ~/.tram/cau-hinh.yaml (dai_ca_logins, ten_may_b, telegram.chat_id, dashboard_url) — "
                  "dashboard chỉ đọc, không báo tin.")
    if thieu_tin:
        cb.append("tram-bao-tin thoát ngay (mã 0) khi chưa có token / chat_id và launchd không tự bật lại. Cấu hình "
                  f"xong, Đại ca chạy: launchctl kickstart -k gui/{os.getuid()}/{NHAN_BAO_TIN}")
    ngu = subprocess.run(["pmset", "-g"], capture_output=True, text=True).stdout
    if any(l.split()[:1] == ["sleep"] and l.split()[1] != "0" for l in ngu.splitlines() if l.strip()):
        cb.append("Máy đang bật chế độ ngủ — Đại ca tắt trong System Settings → Energy.")
    if not shutil.which("bd"):
        cb.append("Không thấy `bd` trong PATH.")
    cb.append("Mở dashboard trong tailnet — Đại ca tự chạy khi #5 được duyệt (kiểm cú pháp với bản Tailscale "
              "trên máy B): " + " ".join(LENH_TAILSCALE_SERVE))
    return cb


def lap_ke_hoach(*, uv: str, repo: Path) -> KeHoach:
    la = Path(os.environ["HOME"]) / "Library/LaunchAgents"
    log = tram_home() / "log"
    tep = {
        la / f"{NHAN_QUET}.plist": tao_plist(uv=uv, repo=repo, log=log / "quet.log"),
        la / f"{NHAN_API}.plist": tao_plist_thuong_truc(NHAN_API, ["api"], uv=uv, repo=repo, log=log / "api.log"),
        la / f"{NHAN_BAO_TIN}.plist": tao_plist_thuong_truc(NHAN_BAO_TIN, ["bao-tin"], uv=uv, repo=repo,
                                                            log=log / "bao-tin.log"),
        la / f"{NHAN_SAO_LUU}.plist": tao_plist_hang_ngay(NHAN_SAO_LUU, ["chu", "sao-luu"], uv=uv, repo=repo,
                                                          log=log / "sao-luu.log"),
    }
    mien = f"gui/{os.getuid()}"
    lenh = [["mkdir", "-p", str(log)]]
    for p in tep:
        lenh += [["launchctl", "bootout", f"{mien}/{p.stem}"], ["launchctl", "bootstrap", mien, str(p)]]
    return KeHoach(tep=tep, lenh=lenh, canh_bao=_canh_bao())


def in_ke_hoach(kh: KeHoach) -> str:
    dong = ["Sẽ ghi các file:"] + [f"  - {p}" for p in kh.tep]
    dong += ["Sẽ chạy các lệnh:"] + [f"  - {' '.join(c)}" for c in kh.lenh]
    dong += ["Cảnh báo (Đại ca tự xử lý, trạm không đổi cài đặt hệ thống):"] + [f"  - {c}" for c in kh.canh_bao or ["không có"]]
    dong += ["Trạm không tự cập nhật. Lúc chạy chỉ gọi ra ngoài tới: Claude API, api.telegram.org, GitHub (Q15)."]
    return "\n".join(dong)


def thuc_hien(kh: KeHoach, *, chay=subprocess.run) -> None:
    for p, noi_dung in kh.tep.items():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(noi_dung)
    for c in kh.lenh:
        chay(c, check=c[:2] != ["launchctl", "bootout"])


def trang_thai(kho) -> str:
    dong = [f"estop: {'BẬT' if estop.dang_bat() else 'tắt'}"]
    for du_an in (d for d in kho.cac_du_an() if not d.startswith("_")):  # "_tram": sự kiện nội bộ
        cuoi = kho.gan_day(du_an, "quet.xong", 1)
        loi = kho.gan_day(du_an, "cham_cot.loi", 1)
        dong.append(f"{du_an}: quét cuối {cuoi[0].luc if cuoi else 'chưa'} {cuoi[0].du_lieu if cuoi else ''}"
                    f" · lỗi gần nhất: {loi[0].luc + ' ' + loi[0].du_lieu.get('loi', '')[:80] if loi else 'không'}")
    return "\n".join(dong)
```

- [ ] **Step 4: Chạy, thấy pass**

Run: `uv run pytest tests/test_cli_dich_vu.py tests/test_chu.py tests/test_quet.py -q`
Expected: `test_cli_dich_vu.py` 6 passed; `test_chu.py`, `test_quet.py` không có fail mới. `wc -l tram/cli.py tram/chu/cai_dat.py` = 115, 97.

- [ ] **Step 5: Commit**

```bash
git add tram/cli_dich_vu.py tram/cli.py tram/chu/launchd.py tram/chu/cai_dat.py tests/test_cli_dich_vu.py
git commit -m "feat(chu): lệnh tram api / bao-tin / chu sao-luu; kế hoạch launchd 4 dịch vụ, cảnh báo Telegram và tailscale serve"
```

---

### Task 23: Frontend — khung Vue (`.vue` + plugin-vue), gọi API, luật thuần, thanh trạng thái, trang Dự án

**Độ khó:** `de` · **Song song:** đợt 1 — chạy cùng mọi task Python đợt 1 (chỉ đụng `frontend/` và `.gitignore`; làm theo "Hợp đồng JSON", không chờ backend). Task 24 cần task này.

**Files:**
- Create: `frontend/package.json`, `frontend/package-lock.json` (npm sinh), `frontend/vite.config.js`, `frontend/index.html`, `frontend/kiem-an-toan.mjs`
- Create: `frontend/src/main.js`, `frontend/src/tuyen.js`, `frontend/src/kho.js`, `frontend/src/api.js`, `frontend/src/luat.js`, `frontend/src/kieu.css`, `frontend/src/KhungChinh.vue`, `frontend/src/thanh/ThanhTrangThai.vue`, `frontend/src/trang/DuAn.vue`
- Test: `frontend/tests/luat.test.mjs`
- Modify: `.gitignore`

**Interfaces:**
- Consumes: "Hợp đồng JSON" (`GET /api/du-an`, `GET /api/phe-duyet`, `GET /api/chu/trang-thai`, `POST /api/chu/estop|tiep-tuc`, SSE `/api/luong`).
- Produces (dùng ở Task 24, 25):
  - `src/api.js`: `taoMaThaoTac() -> string` (UUID); `thanGhi(noiDung, version, ma?) -> {...noiDung, ma_thao_tac, expected_version}`; `doc(duongDan) -> Promise<object>`; `ghi(duongDan, than) -> Promise<object>` (gắn `X-Tram: 1`; lỗi → `Error` có `.status`, thông điệp từ `loi` hoặc `detail`).
  - `src/luat.js`: `HANG_COT`, `TEN_HANG`, `TEN_PHE_DUYET` (có `decision`), `nhomTheoHang(dsThe) -> {hang: The[]}`, `choPhepKeo(the, hangDich) -> boolean`, `tieuDeTab(so) -> string`, `laLinkAnToan(url) -> boolean` (chỉ `https://github.com/…` — N1, G23), `nhomPheDuyet(muc) -> [loai, muc[]][]` (theo thứ tự G15), `gioVN(iso) -> string`.
  - `src/kho.js`: `kho` (reactive `{trangThai, soPheDuyet, phienBan, suKienCuoi, matKetNoi, loi}`), `taiTrangThai()`, `taiSoPheDuyet()` (cập nhật badge + `document.title`), `moLuong()` (SSE: `cong_viec_doi`/`phe_duyet_doi` tăng `phienBan`; `su_kien` đặt `suKienCuoi`).
  - `src/tuyen.js`: `tuyen` (mảng route của vue-router) — Task 24, 25 thêm route.
  - Component `.vue` viết bằng `<script setup>` + `<template>` (G13): `KhungChinh.vue`, `thanh/ThanhTrangThai.vue`, `trang/DuAn.vue`. File `.vue` > ~120 dòng thì tách composable `.js`.

Giao diện dựng theo skill `frontend-ui-engineering` (spec §12.5): chữ hệ thống, màu trung tính, chế độ tối theo hệ điều hành, focus nhìn thấy, bố cục một cột dưới 760 px, giảm chuyển động. Mọi nội dung bead hiển thị bằng nội suy `{{ }}` (text), không `v-html`. Không script/style nội tuyến: `vite build` xuất `<script type="module" src>` + `<link rel="stylesheet">` riêng, hợp CSP `script-src 'self'; style-src 'self'` (Task 10). Thay đổi style lúc chạy chỉ qua CSSOM (`v-show`) — CSP không chặn.

- [ ] **Step 1: Tạo `frontend/package.json` (chưa có phụ thuộc)**

```json
{
  "name": "tram-dashboard",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "kiem": "node --test tests/*.test.mjs && node kiem-an-toan.mjs"
  }
}
```

- [ ] **Step 2: Cài phụ thuộc, ghim chính xác (cần mạng — chỉ bước này)**

```bash
cd frontend
npm install --save-exact vue vue-router
npm install --save-dev --save-exact vite @vitejs/plugin-vue
node -e "const p=require('./package.json'); console.log(p.dependencies, p.devDependencies)"   # không có ^ hay ~
cd ..
```

Kết quả trên bản sao 13/10 (G20): `{ vue: '3.5.43', 'vue-router': '5.4.0' } { '@vitejs/plugin-vue': '6.0.10', vite: '8.3.4' }`, 49 gói trong `node_modules`, "found 0 vulnerabilities". `vue-router` 5 vẫn có `createRouter`, `createWebHashHistory`, `RouterLink` (đã kiểm); `vite` 8 cần Node `^20.19.0 || >=22.12.0` (máy B có v26). Số khác → vẫn ghim số đã giải, chạy đủ bước 6.

Thêm vào cuối `.gitignore`:

```
frontend/node_modules/
frontend/dist/
```

- [ ] **Step 3: Viết test thất bại**

`frontend/tests/luat.test.mjs`:

```js
import assert from 'node:assert/strict'
import { test } from 'node:test'
import { ghi, thanGhi } from '../src/api.js'
import { choPhepKeo, gioVN, laLinkAnToan, nhomPheDuyet, nhomTheoHang, tieuDeTab } from '../src/luat.js'

test('nhomTheoHang xếp thẻ theo hàng và ưu tiên; hàng lạ về chưa chấm', () => {
  const n = nhomTheoHang([{ id: 'b', hang: 'ai-lam', uu_tien: 2 }, { id: 'a', hang: 'ai-lam', uu_tien: 1 },
    { id: 'c', hang: 'la' }])
  assert.deepEqual(n['ai-lam'].map((t) => t.id), ['a', 'b'])
  assert.deepEqual(n['chua-cham'].map((t) => t.id), ['c'])
  assert.deepEqual(n.epic, [])
})

test('choPhepKeo chỉ giữa cột 1 và cột 2', () => {
  const t = { keo_duoc: true, hang: 'ai-lam' }
  assert.equal(choPhepKeo(t, 'can-chot'), true)
  assert.equal(choPhepKeo(t, 'ai-lam'), false)
  assert.equal(choPhepKeo(t, 'cho-review'), false)
  assert.equal(choPhepKeo({ ...t, keo_duoc: false }, 'can-chot'), false)
  assert.equal(choPhepKeo(null, 'can-chot'), false)
})

test('tiêu đề tab và link an toàn', () => {
  assert.equal(tieuDeTab(0), 'Bàn điều hành')
  assert.equal(tieuDeTab(3), '(3) Bàn điều hành')
  assert.equal(laLinkAnToan('https://github.com/o/r/pull/7'), true)
  assert.equal(laLinkAnToan('javascript:alert(1)'), false)
  assert.equal(laLinkAnToan('http://github.com/o/r/pull/7'), false)
  assert.equal(laLinkAnToan('https://evil.example/o/r/pull/7'), false)
  assert.equal(laLinkAnToan('https://github.com.evil.example/x'), false)
  assert.equal(laLinkAnToan(null), false)
})

test('nhomPheDuyet giữ thứ tự độ gấp, bỏ nhóm rỗng', () => {
  const n = nhomPheDuyet([{ loai: 'cho-review', bead_id: '1' }, { loai: 'decision', bead_id: '3' },
    { loai: 'escalation', bead_id: '2' }])
  assert.deepEqual(n.map(([loai]) => loai), ['escalation', 'decision', 'cho-review'])
})

test('gioVN đổi sang giờ Việt Nam', () => {
  assert.match(gioVN('2026-10-13T01:00:00Z'), /08:00/)
  assert.equal(gioVN(null), '')
})

test('thanGhi gắn ma_thao_tac và expected_version', () => {
  assert.deepEqual(thanGhi({ cot: 'ai-lam' }, 'v1', 'ma-co-dinh-01'),
    { cot: 'ai-lam', ma_thao_tac: 'ma-co-dinh-01', expected_version: 'v1' })
  assert.match(thanGhi({}, 'v').ma_thao_tac, /^[0-9a-f-]{36}$/)
})

test('ghi gửi X-Tram và ném lỗi kèm status', async () => {
  let goi
  globalThis.fetch = async (url, opt) => {
    goi = { url, opt }
    return new Response(JSON.stringify({ loi: 'Bead đã đổi' }), { status: 409 })
  }
  await assert.rejects(ghi('/api/x', { a: 1 }), (e) => e.status === 409 && e.message === 'Bead đã đổi')
  assert.equal(goi.opt.method, 'POST')
  assert.equal(goi.opt.headers['X-Tram'], '1')
  assert.equal(goi.opt.body, '{"a":1}')
})
```

- [ ] **Step 4: Chạy, thấy fail**

Run: `cd frontend && node --test tests/*.test.mjs`
Expected: FAIL — `Cannot find module '.../src/api.js'`.

- [ ] **Step 5: Viết mã**

`frontend/vite.config.js`:

```js
import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'

// Component `.vue` dịch sẵn lúc build (G13, spec §8): bản Vue chỉ-runtime, không `new Function` → bật được CSP chặt.
export default defineConfig({
  plugins: [vue()],
  define: {
    __VUE_OPTIONS_API__: 'true',
    __VUE_PROD_DEVTOOLS__: 'false',
    __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: 'false',
  },
  // changeOrigin: tram-api chỉ nhận Host 127.0.0.1:<cổng> / localhost:<cổng> / tên máy B (421 nếu khác).
  server: { proxy: { '/api': { target: 'http://127.0.0.1:7700', changeOrigin: true } } },
  build: { outDir: 'dist', emptyOutDir: true },
})
```

`frontend/index.html`:

```html
<!doctype html>
<html lang="vi">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Bàn điều hành</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.js"></script>
  </body>
</html>
```

`frontend/kiem-an-toan.mjs`:

```js
// Chặn chèn HTML thô vào trang (spec §4 mục 4): nội dung bead chỉ hiển thị bằng text. Quét mọi file trong src/.
import { readFileSync, readdirSync, statSync } from 'node:fs'
import { join } from 'node:path'
import { fileURLToPath } from 'node:url'

const CAM = [/v-html/, /v-bind:innerHTML/, /:innerHTML/, /innerHTML/, /outerHTML/, /insertAdjacentHTML/, /document\.write/]
const goc = fileURLToPath(new URL('./src', import.meta.url))
const duyet = (d) => readdirSync(d).flatMap((t) => (statSync(join(d, t)).isDirectory() ? duyet(join(d, t)) : [join(d, t)]))
const tep = duyet(goc)
const viPham = tep.filter((p) => CAM.some((re) => re.test(readFileSync(p, 'utf8'))))
if (viPham.length) {
  console.error('Cấm v-html / innerHTML / document.write trong:', viPham)
  process.exit(1)
}
console.log(`kiem-an-toan: ${tep.length} file, không có chèn HTML thô`)
```

`frontend/src/api.js`:

```js
// Gọi tram-api. POST ghi gắn X-Tram (chống CSRF — spec §4 mục 3) và ma_thao_tac + expected_version (§12.3).
export function taoMaThaoTac() {
  return crypto.randomUUID()
}

export function thanGhi(noiDung, version, ma = taoMaThaoTac()) {
  return { ...noiDung, ma_thao_tac: ma, expected_version: version ?? '' }
}

async function xuLy(r) {
  let than = {}
  try {
    than = await r.json()
  } catch {
    than = {}
  }
  if (!r.ok) {
    const loi = new Error(than.loi || (typeof than.detail === 'string' ? than.detail : `Lỗi HTTP ${r.status}`))
    loi.status = r.status
    throw loi
  }
  return than
}

export async function doc(duongDan) {
  return xuLy(await fetch(duongDan, { headers: { Accept: 'application/json' } }))
}

export async function ghi(duongDan, than) {
  return xuLy(await fetch(duongDan, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-Tram': '1' },
    body: JSON.stringify(than),
  }))
}
```

`frontend/src/luat.js`:

```js
// Luật hiển thị thuần (test được bằng node --test). Luật nghiệp vụ thật nằm ở server (tram/suy/cot.py).
export const HANG_COT = ['ai-lam', 'can-chot', 'cho-review']
export const TEN_HANG = {
  'ai-lam': '1 · AI tự làm',
  'can-chot': '2 · Cần Đại ca chốt',
  'cho-review': '3 · Chờ review để đóng',
  'chua-cham': 'Chưa chấm',
  'theo-plan': 'Feature đang chạy plan',
  epic: 'Epic',
}
const THU_TU_PHE_DUYET = ['escalation', 'decision', 'co-do', 'he', 'cho-review', 'spec']
export const TEN_PHE_DUYET = {
  escalation: 'Bí / escalation',
  decision: 'Decision mở chờ trả lời',
  'co-do': 'Cờ đỏ',
  he: 'Hệ cần xem',
  'cho-review': 'Chờ review để đóng',
  spec: 'Spec chờ duyệt',
}

function soThe(a, b) {
  return (a.uu_tien ?? 9) - (b.uu_tien ?? 9) || String(a.id).localeCompare(String(b.id))
}

export function nhomTheoHang(dsThe) {
  const nhom = Object.fromEntries(Object.keys(TEN_HANG).map((h) => [h, []]))
  for (const t of dsThe) (nhom[t.hang] ?? nhom['chua-cham']).push(t)
  for (const h of Object.keys(nhom)) nhom[h].sort(soThe)
  return nhom
}

export function choPhepKeo(the, hangDich) {
  return Boolean(the && the.keo_duoc) && (hangDich === 'ai-lam' || hangDich === 'can-chot') && the.hang !== hangDich
}

export function tieuDeTab(so) {
  return so > 0 ? `(${so}) Bàn điều hành` : 'Bàn điều hành'
}

// Chỉ link PR trên GitHub (N1): server đã lọc https://, trình duyệt chặn thêm host lạ.
export function laLinkAnToan(url) {
  return typeof url === 'string' && /^https:\/\/github\.com\/[^\s"'<>]+$/.test(url)
}

export function nhomPheDuyet(ds) {
  return THU_TU_PHE_DUYET.map((l) => [l, ds.filter((m) => m.loai === l)]).filter(([, m]) => m.length)
}

export function gioVN(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  return Number.isNaN(d.getTime()) ? String(iso)
    : d.toLocaleString('vi-VN', { timeZone: 'Asia/Ho_Chi_Minh', hour12: false })
}
```

`frontend/src/kho.js`:

```js
// Trạng thái dùng chung giữa các trang; mọi trạng thái nghiệp vụ tính ở server (Q12).
import { reactive } from 'vue'
import { doc } from './api.js'
import { tieuDeTab } from './luat.js'

export const kho = reactive({ trangThai: null, soPheDuyet: 0, phienBan: 0, suKienCuoi: null, matKetNoi: false, loi: '' })

export async function taiTrangThai() {
  try {
    kho.trangThai = await doc('/api/chu/trang-thai')
  } catch (e) {
    kho.loi = e.message
  }
}

export async function taiSoPheDuyet() {
  try {
    const r = await doc('/api/phe-duyet')
    kho.soPheDuyet = r.so
    document.title = tieuDeTab(r.so)
  } catch (e) {
    kho.loi = e.message
  }
}

export function moLuong() {
  const es = new EventSource('/api/luong')
  const doi = () => { kho.phienBan += 1 }
  es.addEventListener('cong_viec_doi', doi)
  es.addEventListener('phe_duyet_doi', () => { doi(); taiSoPheDuyet(); taiTrangThai() })
  es.addEventListener('su_kien', (e) => {
    try {
      kho.suKienCuoi = JSON.parse(e.data)
    } catch {
      kho.suKienCuoi = null
    }
  })
  es.onerror = () => { kho.matKetNoi = true }
  es.onopen = () => { kho.matKetNoi = false }
  return es
}
```

`frontend/src/main.js`:

```js
import { createApp } from 'vue'
import { createRouter, createWebHashHistory } from 'vue-router'
import KhungChinh from './KhungChinh.vue'
import './kieu.css'
import { tuyen } from './tuyen.js'

createApp(KhungChinh).use(createRouter({ history: createWebHashHistory(), routes: tuyen })).mount('#app')
```

`frontend/src/tuyen.js`:

```js
import DuAn from './trang/DuAn.vue'

export const tuyen = [
  { path: '/', redirect: '/du-an' },
  { path: '/du-an', component: DuAn },
]
```

`frontend/src/KhungChinh.vue`:

```vue
<script setup>
import { onMounted } from 'vue'
import { kho, moLuong, taiSoPheDuyet, taiTrangThai } from './kho.js'
import ThanhTrangThai from './thanh/ThanhTrangThai.vue'

onMounted(() => { taiTrangThai(); taiSoPheDuyet(); moLuong() })
</script>

<template>
  <header class="dau">
    <nav class="menu" aria-label="Menu chính">
      <router-link to="/cong-viec">Công việc</router-link>
      <router-link to="/du-an">Dự án</router-link>
      <router-link to="/phe-duyet">Phê duyệt
        <span v-if="kho.soPheDuyet" class="dem" :aria-label="kho.soPheDuyet + ' việc chờ'">{{ kho.soPheDuyet }}</span>
      </router-link>
    </nav>
    <ThanhTrangThai />
  </header>
  <p v-if="kho.matKetNoi" class="canh-bao" role="status">Mất kết nối luồng sự kiện — đang thử lại…</p>
  <p v-if="kho.loi" class="loi" role="alert">{{ kho.loi }}</p>
  <main><router-view /></main>
</template>
```

`frontend/src/thanh/ThanhTrangThai.vue`:

```vue
<script setup>
import { ref } from 'vue'
import { ghi, thanGhi } from '../api.js'
import { kho, taiTrangThai } from '../kho.js'
import { gioVN } from '../luat.js'

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
</script>

<template>
  <section class="thanh-trang-thai" aria-label="Trạng thái trạm chủ">
    <template v-if="kho.trangThai">
      <span class="chip" :class="{ bat: kho.trangThai.estop }">estop {{ kho.trangThai.estop ? 'BẬT' : 'tắt' }}</span>
      <span v-for="d in kho.trangThai.du_an" :key="d.ten" class="nho">
        {{ d.ten }}: quét {{ d.quet_cuoi ? gioVN(d.quet_cuoi) : 'chưa' }}<template v-if="d.loi_gan_nhat"> ·
        <span class="loi">lỗi {{ gioVN(d.loi_gan_nhat.luc) }}</span></template>
      </span>
      <button v-if="!kho.trangThai.estop" type="button" :disabled="dangGui || !kho.trangThai.la_dai_ca"
              :title="kho.trangThai.la_dai_ca ? '' : 'Chỉ đọc: thiếu danh tính Đại ca'" @click="bam(true)">Estop</button>
      <button v-else type="button" :disabled="dangGui || !kho.trangThai.la_dai_ca" @click="bam(false)">Tiếp tục</button>
      <span v-if="thongBao" class="loi" role="alert">{{ thongBao }}</span>
    </template>
    <span v-else class="nho">Đang tải trạng thái…</span>
  </section>
</template>
```

`frontend/src/trang/DuAn.vue`:

```vue
<script setup>
import { onMounted, ref, watch } from 'vue'
import { doc } from '../api.js'
import { kho } from '../kho.js'
import { TEN_HANG, gioVN } from '../luat.js'

const COT_HIEN = ['ai-lam', 'can-chot', 'cho-review', 'chua-cham']
const ds = ref([])
const loi = ref('')

async function tai() {
  try {
    ds.value = (await doc('/api/du-an')).du_an
    loi.value = ''
  } catch (e) {
    loi.value = e.message
  }
}
onMounted(tai)
watch(() => kho.phienBan, tai)
</script>

<template>
  <section>
    <h1>Dự án</h1>
    <p v-if="loi" class="loi" role="alert">{{ loi }}</p>
    <p v-if="!ds.length && !loi" class="nho">Chưa có dự án nào trong du-an/.</p>
    <div v-if="ds.length" class="bang-cuon">
      <table>
        <thead><tr>
          <th scope="col">Dự án</th><th v-for="h in COT_HIEN" :key="h" scope="col">{{ TEN_HANG[h] }}</th>
          <th scope="col">Quét cuối</th><th scope="col">Lỗi gần nhất</th>
        </tr></thead>
        <tbody><tr v-for="d in ds" :key="d.ten">
          <th scope="row">{{ d.ten }}</th>
          <td v-for="h in COT_HIEN" :key="h">{{ d.so_bead[h] }}</td>
          <td>{{ d.quet_cuoi ? gioVN(d.quet_cuoi) : 'chưa' }}</td>
          <td>{{ d.loi_doc || (d.loi_gan_nhat ? gioVN(d.loi_gan_nhat.luc) + ' · ' + d.loi_gan_nhat.loi : 'không') }}</td>
        </tr></tbody>
      </table>
    </div>
  </section>
</template>
```

`frontend/src/kieu.css`:

```css
:root {
  --nen: #f6f5f2; --mat: #ffffff; --chu: #1d1d1f; --phu: #5f6368; --vien: #dcd9d2;
  --nhan: #2f5d8a; --do: #b3261e; --vang: #8a6100; --bong: 0 1px 2px rgb(0 0 0 / 8%);
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  color: var(--chu); background: var(--nen);
}
@media (prefers-color-scheme: dark) {
  :root { --nen: #161718; --mat: #202124; --chu: #e8eaed; --phu: #9aa0a6; --vien: #3c4043;
          --nhan: #8ab4f8; --do: #f28b82; --vang: #fdd663; }
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--nen); }
.dau { position: sticky; top: 0; z-index: 2; display: flex; flex-wrap: wrap; gap: .5rem 1.5rem; align-items: center;
       justify-content: space-between; padding: .5rem 1rem; background: var(--mat); border-bottom: 1px solid var(--vien); }
.menu { display: flex; gap: 1rem; }
.menu a { color: var(--phu); text-decoration: none; padding: .25rem 0; border-bottom: 2px solid transparent; }
.menu a.router-link-active { color: var(--chu); border-color: var(--nhan); }
.dem { display: inline-block; min-width: 1.4em; padding: 0 .35em; border-radius: 999px; background: var(--do);
       color: #fff; font-size: .75rem; text-align: center; }
main { padding: 1rem; max-width: 1400px; margin: 0 auto; }
h1 { font-size: 1.25rem; } h2 { font-size: 1rem; margin: 0 0 .5rem; } h3 { font-size: .9rem; margin: 1rem 0 .25rem; }
.nho { color: var(--phu); font-size: .8rem; }
.loi { color: var(--do); }
.canh-bao { color: var(--vang); }
.thanh-trang-thai { display: flex; flex-wrap: wrap; gap: .5rem 1rem; align-items: center; font-size: .8rem; }
.chip { padding: .1rem .5rem; border-radius: 999px; border: 1px solid var(--vien); }
.chip.bat { background: var(--do); color: #fff; border-color: var(--do); }
button { font: inherit; padding: .35rem .75rem; border-radius: 6px; border: 1px solid var(--vien);
         background: var(--mat); color: var(--chu); cursor: pointer; }
button:disabled { opacity: .5; cursor: not-allowed; }
button:focus-visible, a:focus-visible, .the:focus-visible, select:focus-visible, textarea:focus-visible, input:focus-visible {
  outline: 2px solid var(--nhan); outline-offset: 2px; }
.nut { display: flex; flex-wrap: wrap; gap: .5rem; margin: .5rem 0; }
textarea, input, select { font: inherit; width: 100%; padding: .4rem; border: 1px solid var(--vien); border-radius: 6px;
                          background: var(--mat); color: var(--chu); }
input[type="checkbox"] { width: auto; margin-right: .4rem; }
label { display: block; margin: .5rem 0; font-size: .85rem; }
.cong-cu { display: flex; flex-wrap: wrap; gap: 1rem; align-items: end; margin-bottom: 1rem; }
.cong-cu label { min-width: 12rem; }
.ba-cot { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1rem; }
@media (max-width: 760px) { .ba-cot { grid-template-columns: 1fr; } main { padding: .75rem; } }
.cot, .hang-ngang { background: color-mix(in srgb, var(--mat) 60%, var(--nen)); border: 1px solid var(--vien);
                    border-radius: 8px; padding: .75rem; min-height: 6rem; }
.hang-ngang { margin-bottom: 1rem; }
.day { display: flex; gap: .5rem; overflow-x: auto; }
.day .the { min-width: 16rem; }
.the { background: var(--mat); border: 1px solid var(--vien); border-radius: 6px; padding: .5rem .6rem;
       margin-bottom: .5rem; box-shadow: var(--bong); cursor: pointer; }
.the[draggable="true"] { cursor: grab; }
.the.mo { opacity: .55; }
.the.lech { border-color: var(--vang); }
.ma { font-family: ui-monospace, monospace; font-size: .8rem; }
.tieu-de { margin: .25rem 0; overflow-wrap: anywhere; }
.nhan-nho { font-size: .7rem; padding: 0 .35rem; border-radius: 4px; border: 1px solid var(--vien); margin-left: .25rem; }
.nhan-nho.do { color: var(--do); border-color: var(--do); }
.nhan-nho.vang { color: var(--vang); border-color: var(--vang); }
.dem-nho { color: var(--phu); font-weight: normal; }
.ngan-ben { position: fixed; top: 0; right: 0; bottom: 0; width: min(36rem, 100vw); overflow-y: auto; z-index: 3;
            background: var(--mat); border-left: 1px solid var(--vien); padding: 1rem; box-shadow: -4px 0 12px rgb(0 0 0 / 15%); }
.ngan-ben .dong { float: right; }
.van-ban { white-space: pre-wrap; overflow-wrap: anywhere; font-family: inherit; margin: 0; }
.nen-mo { position: fixed; inset: 0; z-index: 4; display: grid; place-items: center; padding: 1rem; background: rgb(0 0 0 / 40%); }
.hop { background: var(--mat); border-radius: 8px; padding: 1rem; width: min(30rem, 100%); }
.muc { background: var(--mat); border: 1px solid var(--vien); border-radius: 8px; padding: .75rem; margin-bottom: .75rem; }
.bang-cuon { overflow-x: auto; }
table { border-collapse: collapse; width: 100%; background: var(--mat); }
th, td { text-align: left; padding: .4rem .6rem; border-bottom: 1px solid var(--vien); font-size: .85rem; }
.dong-thoi-gian { padding-left: 1.2rem; font-size: .8rem; }
.dong-thoi-gian li { padding: .25rem 0; border-bottom: 1px dashed var(--vien); }
@media (prefers-reduced-motion: reduce) { * { transition: none !important; animation: none !important; } }
```

- [ ] **Step 6: Chạy kiểm, thấy pass**

```bash
cd frontend
npm run kiem      # Expected: "ℹ tests 7", "ℹ pass 7", "ℹ fail 0", "kiem-an-toan: 9 file, không có chèn HTML thô"
npm run build     # Expected: "✓ built in …", dist/index.html + dist/assets/index-*.js + dist/assets/index-*.css
grep -c "new Function" dist/assets/*.js   # Expected: 0 (bản Vue chỉ-runtime — CSP không cần unsafe-eval)
cd ..
```

Kiểm tối thiểu (không có vitest — G14): logic thuần qua `node --test`; cấm chèn HTML thô qua `kiem-an-toan`; `vite build` (plugin-vue dịch mọi `<template>` lúc build — sai cú pháp template thì build đỏ, đã thử với một thẻ đóng sai: "RolldownError: Invalid end tag."). Giao diện thật kiểm tay ở Task 26.

- [ ] **Step 7: Commit**

```bash
git add .gitignore frontend/package.json frontend/package-lock.json frontend/vite.config.js frontend/index.html \
  frontend/kiem-an-toan.mjs frontend/src frontend/tests
git commit -m "feat(frontend): khung Vue 3 (.vue + plugin-vue) + vue-router, gọi API có X-Tram và ma_thao_tac, thanh trạng thái, trang Dự án"
```

(Ghi phiên bản `vue`, `vue-router`, `vite`, `@vitejs/plugin-vue` từ `package.json` vào thân commit.)

---

### Task 24: Frontend — trang Công việc (ba cột, kéo thả, ngăn bên, Chốt, Trả lời decision)

**Độ khó:** `kho` (kéo thả, nhiều trạng thái giao diện) · **Song song:** đợt 2 — chạy cùng Task 4, 6, 8, 10, 11, 20 (chỉ đụng `frontend/`). **Phải xong trước:** Task 23. Task 25 cần task này (cùng sửa `src/tuyen.js`, dùng lại `OTraLoi.vue`).

**Files:**
- Create: `frontend/src/trang/CongViec.vue`, `frontend/src/trang/NganBen.vue`, `frontend/src/thanh/TheBead.vue`, `frontend/src/thanh/HopViSao.vue`, `frontend/src/thanh/OChot.vue`, `frontend/src/thanh/OTraLoi.vue`, `frontend/src/thanh/DongThoiGian.vue`
- Modify: `frontend/src/tuyen.js`

**Interfaces:**
- Consumes: `doc`, `ghi`, `thanGhi` (`api.js`); `kho` (`kho.js`); `HANG_COT`, `TEN_HANG`, `choPhepKeo`, `nhomTheoHang`, `laLinkAnToan`, `gioVN` (`luat.js`); `GET /api/du-an`, `GET /api/cong-viec`, `GET /api/bead/...`, `POST .../cot`, `POST .../chot`, `POST /api/phe-duyet/.../tra-loi`.
- Produces: route `/cong-viec` (mặc định `/`); component `TheBead` (props `the`; emits `mo`, `keo`), `HopViSao` (props `the`, `cot`; emits `huy`, `xac-nhan(viSao)`), `NganBen` (props `the`; emits `dong`, `chuyen(cot)`, `doi`), `OChot` (props `cauHoi: string[]`, `gui: (noiDung) => Promise`), `OTraLoi` (props `gui: (traLoi) => Promise<boolean>` — `false` = lỗi, giữ nội dung; `khoa: boolean`; `nhan: string`), `DongThoiGian` (props `ds`).

Hành vi (spec §5.1): chọn dự án / "Tất cả"; hàng "chưa chấm" phía trên; ba cột; hàng "Feature đang chạy plan" và "Epic" phía dưới; thẻ mờ + "chờ <id>" khi bị chặn; khoá / cờ đỏ / nhãn lệch; kéo chỉ khi `keo_duoc` và chỉ thả vào cột 1/2 (cột 3 không nhận); `dragstart` gọi `dataTransfer.setData('text/plain', id)` (Firefox chỉ kéo khi có dữ liệu — N2); thả → hộp "vì sao?" (tuỳ chọn) → `POST /cot`; 409 → tải lại và báo; ngăn bên có nút "Chuyển sang cột 1/2" (thay kéo thả trên điện thoại), lý do chấm, câu hỏi, Chốt / dẫn ADR, **ô Trả lời khi `tra_loi_duoc`** (escalation / decision mở ở cột 2 — Q4, G21; nút tắt khi `la_dai_ca` false), bàn giao, mô tả, nghiệm thu, dòng thời gian; ngăn bên tự tải lại khi có `su_kien` của chính bead.

- [ ] **Step 1: Viết mã**

`frontend/src/thanh/TheBead.vue`:

```vue
<script setup>
const props = defineProps({ the: { type: Object, required: true } })
const emit = defineEmits(['mo', 'keo'])

function batDauKeo(e) {
  e.dataTransfer.setData('text/plain', props.the.id)   // Firefox chỉ bắt đầu kéo khi có dữ liệu (N2)
  e.dataTransfer.effectAllowed = 'move'
  emit('keo')
}
</script>

<template>
  <article class="the" :class="{ mo: the.mo, lech: the.lech }" tabindex="0" :draggable="the.keo_duoc ? 'true' : 'false'"
           :aria-label="the.id + ': ' + the.tieu_de" @click="emit('mo')" @keydown.enter="emit('mo')"
           @dragstart="batDauKeo">
    <header>
      <span class="ma">{{ the.id }}</span> <span class="nho">{{ the.du_an }}</span>
      <span v-if="the.khoa" class="nhan-nho" title="Đại ca đã khoá cột">khoá</span>
      <span v-if="the.co_do" class="nhan-nho do">cờ đỏ</span>
      <span v-if="the.lech" class="nhan-nho vang" title="Nhiều nhãn cột">nhãn lệch</span>
    </header>
    <p class="tieu-de">{{ the.tieu_de }}</p>
    <footer class="nho">{{ the.loai }} · P{{ the.uu_tien ?? '?' }}<span v-if="the.khe_spec"> · khe spec</span><span
      v-if="the.cho.length"> · chờ {{ the.cho.join(', ') }}</span></footer>
  </article>
</template>
```

`frontend/src/thanh/HopViSao.vue`:

```vue
<script setup>
import { ref } from 'vue'
import { TEN_HANG } from '../luat.js'

defineProps({ the: { type: Object, required: true }, cot: { type: String, required: true } })
const emit = defineEmits(['huy', 'xac-nhan'])
const viSao = ref('')
</script>

<template>
  <div class="nen-mo" role="dialog" aria-modal="true" aria-labelledby="hop-vi-sao-td" @keydown.esc="emit('huy')">
    <form class="hop" @submit.prevent="emit('xac-nhan', viSao.trim())">
      <h2 id="hop-vi-sao-td">Chuyển {{ the.id }} sang "{{ TEN_HANG[cot] }}"</h2>
      <label>Vì sao? (tuỳ chọn)<textarea v-model="viSao" rows="3" maxlength="2000" autofocus></textarea></label>
      <p class="nho">Bead sẽ được khoá cột (cot-khoa); bộ chấm không lật lại cho tới khi Đại ca gỡ khoá.</p>
      <div class="nut">
        <button type="button" @click="emit('huy')">Huỷ</button>
        <button type="submit">Chuyển cột</button>
      </div>
    </form>
  </div>
</template>
```

`frontend/src/thanh/DongThoiGian.vue`:

```vue
<script setup>
import { gioVN } from '../luat.js'

defineProps({ ds: { type: Array, required: true } })
</script>

<template>
  <section>
    <h3>Dòng thời gian</h3>
    <p v-if="!ds.length" class="nho">Chưa có sự kiện.</p>
    <ol v-else class="dong-thoi-gian" reversed>
      <li v-for="s in [...ds].reverse()" :key="s.id">
        <span class="nho">{{ gioVN(s.luc) }} · {{ s.tac_nhan }}</span> <strong>{{ s.loai }}</strong>
        <span class="van-ban">{{ s.tom_tat }}</span>
      </li>
    </ol>
  </section>
</template>
```

`frontend/src/thanh/OChot.vue`:

```vue
<script setup>
import { ref, watch } from 'vue'

const CAU_CHUNG = 'Chốt chung cho bead (lần chấm không có câu hỏi cụ thể)'
const props = defineProps({ cauHoi: { type: Array, required: true }, gui: { type: Function, required: true } })
const traLoi = ref([])
const adr = ref('')
const dungAdr = ref(false)
const dangGui = ref(false)
const cau = () => (props.cauHoi.length ? props.cauHoi : [CAU_CHUNG])
watch(() => props.cauHoi, () => { traLoi.value = cau().map(() => '') }, { immediate: true })
const du = () => (dungAdr.value ? /^ADR-\d{4}$/.test(adr.value.trim()) : traLoi.value.every((t) => t.trim()))

async function chot() {
  if (!du() || dangGui.value) return
  dangGui.value = true
  try {
    await props.gui(dungAdr.value ? { adr: adr.value.trim() } : { tra_loi: traLoi.value.map((t) => t.trim()) })
  } catch {
    // NganBen đã hiện lỗi; mở lại nút để Đại ca sửa và gửi lại
  } finally {
    dangGui.value = false
  }
}
</script>

<template>
  <form class="o-chot" @submit.prevent="chot">
    <h3>Trả lời câu hỏi cần chốt</h3>
    <label><input type="checkbox" v-model="dungAdr">Dẫn ADR thay cho trả lời (câu trả lời dài / kiến trúc)</label>
    <label v-if="dungAdr">Mã ADR<input v-model="adr" placeholder="ADR-0000" maxlength="8" required></label>
    <template v-else>
      <label v-for="(q, i) in cau()" :key="i">{{ q }}
        <textarea v-model="traLoi[i]" rows="2" maxlength="4000" required></textarea></label>
    </template>
    <button type="submit" :disabled="dangGui || !du()">Chốt</button>
    <p class="nho">Tạo bead decision đã đóng, nối vào bead này, gỡ nhãn cột; lượt quét sau chấm lại.</p>
  </form>
</template>
```

`frontend/src/thanh/OTraLoi.vue`:

```vue
<script setup>
import { ref } from 'vue'

// Nút Trả lời escalation / decision mở (spec 2 §5.2) — dùng ở ngăn bên và trang Phê duyệt.
const props = defineProps({
  gui: { type: Function, required: true },          // (traLoi) => Promise<boolean>; false = lỗi, giữ nội dung
  khoa: { type: Boolean, default: false },
  nhan: { type: String, default: 'Trả lời' },
})
const traLoi = ref('')
const dangGui = ref(false)

async function guiTraLoi() {
  const vb = traLoi.value.trim()
  if (!vb || dangGui.value) return
  dangGui.value = true
  try {
    if ((await props.gui(vb)) !== false) traLoi.value = ''
  } finally {
    dangGui.value = false
  }
}
</script>

<template>
  <form class="o-tra-loi" @submit.prevent="guiTraLoi">
    <label>Trả lời<textarea v-model="traLoi" rows="3" maxlength="4000" required></textarea></label>
    <button type="submit" :disabled="khoa || dangGui || !traLoi.trim()">{{ nhan }}</button>
    <p class="nho">Đóng chính bead quyết định, câu trả lời thành lý do đóng. Câu trả lời không cấp quyền làm thao tác
      nguy hiểm (deploy, migrate DB thật, xoá dữ liệu, gửi khách).</p>
  </form>
</template>
```

`frontend/src/trang/NganBen.vue`:

```vue
<script setup>
import { ref, watch } from 'vue'
import { doc, ghi, thanGhi } from '../api.js'
import { kho } from '../kho.js'
import { gioVN, laLinkAnToan } from '../luat.js'
import DongThoiGian from '../thanh/DongThoiGian.vue'
import OChot from '../thanh/OChot.vue'
import OTraLoi from '../thanh/OTraLoi.vue'

const props = defineProps({ the: { type: Object, required: true } })
const emit = defineEmits(['dong', 'chuyen', 'doi'])
const ct = ref(null)
const loi = ref('')
const duongDan = () => `${encodeURIComponent(props.the.du_an)}/${encodeURIComponent(props.the.id)}`

async function tai() {
  try {
    ct.value = await doc(`/api/bead/${duongDan()}`)
    loi.value = ''
  } catch (e) {
    loi.value = e.message
  }
}
watch(() => [props.the.du_an, props.the.id, props.the.updated_at], tai, { immediate: true })
watch(() => kho.suKienCuoi, (sk) => {
  if (sk && sk.du_an === props.the.du_an && sk.bead_id === props.the.id) tai()
})

async function gui(duong, noiDung) {
  try {
    await ghi(duong, thanGhi(noiDung, ct.value.the.updated_at))
    loi.value = ''
    emit('doi')
    return true
  } catch (e) {
    loi.value = e.status === 409 ? 'Bead đã đổi — đã tải lại, Đại ca xem lại.' : e.message
    await tai()
    return false
  }
}
async function chot(noiDung) {
  if (!(await gui(`/api/bead/${duongDan()}/chot`, noiDung))) throw new Error(loi.value)
}
const traLoi = (vb) => gui(`/api/phe-duyet/${duongDan()}/tra-loi`, { tra_loi: vb })
</script>

<template>
  <aside class="ngan-ben" aria-label="Chi tiết bead">
    <button class="dong" type="button" aria-label="Đóng ngăn chi tiết" @click="emit('dong')">×</button>
    <p v-if="loi" class="loi" role="alert">{{ loi }}</p>
    <template v-if="ct">
      <h2>{{ ct.the.id }} · {{ ct.the.tieu_de }}</h2>
      <p class="nho">{{ ct.the.du_an }} · {{ ct.the.loai }} · P{{ ct.the.uu_tien ?? '?' }} · cập nhật {{ gioVN(ct.the.updated_at) }}</p>
      <div v-if="ct.the.keo_duoc" class="nut">
        <button v-if="ct.the.hang !== 'ai-lam'" type="button" @click="emit('chuyen', 'ai-lam')">Chuyển sang cột 1</button>
        <button v-if="ct.the.hang !== 'can-chot'" type="button" @click="emit('chuyen', 'can-chot')">Chuyển sang cột 2</button>
      </div>
      <section v-if="ct.cham_gan_nhat">
        <h3>Lần chấm gần nhất · {{ gioVN(ct.cham_gan_nhat.luc) }}</h3>
        <p class="van-ban">{{ ct.cham_gan_nhat.ly_do }}</p>
        <ol v-if="ct.cham_gan_nhat.cau_hoi.length"><li v-for="(q, i) in ct.cham_gan_nhat.cau_hoi" :key="i">{{ q }}</li></ol>
      </section>
      <OChot v-if="ct.the.chot_duoc" :cau-hoi="ct.cham_gan_nhat ? ct.cham_gan_nhat.cau_hoi : []" :gui="chot" />
      <OTraLoi v-if="ct.the.tra_loi_duoc" :gui="traLoi" :khoa="!(kho.trangThai && kho.trangThai.la_dai_ca)"
               nhan="Trả lời (đóng decision)" />
      <section v-if="ct.ban_giao">
        <h3>Bàn giao</h3>
        <p v-if="laLinkAnToan(ct.ban_giao.pr)"><a :href="ct.ban_giao.pr" target="_blank" rel="noopener noreferrer">Mở PR</a></p>
        <p class="nho">Nhánh {{ ct.ban_giao.nhanh || '—' }} · commit {{ ct.ban_giao.commit || '—' }}</p>
        <ul v-if="ct.ban_giao.loi.length" class="canh-bao"><li v-for="l in ct.ban_giao.loi" :key="l">{{ l }}</li></ul>
      </section>
      <section><h3>Mô tả</h3><pre class="van-ban">{{ ct.mo_ta || '(trống)' }}</pre></section>
      <section><h3>Tiêu chí nghiệm thu</h3><pre class="van-ban">{{ ct.nghiem_thu || '(trống)' }}</pre></section>
      <DongThoiGian :ds="ct.dong_thoi_gian" />
    </template>
  </aside>
</template>
```

`frontend/src/trang/CongViec.vue`:

```vue
<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { doc, ghi, thanGhi } from '../api.js'
import { kho } from '../kho.js'
import { HANG_COT, TEN_HANG, choPhepKeo, nhomTheoHang } from '../luat.js'
import HopViSao from '../thanh/HopViSao.vue'
import TheBead from '../thanh/TheBead.vue'
import NganBen from './NganBen.vue'

const duAn = ref('')
const dsDuAn = ref([])
const dsThe = ref([])
const loiDoc = ref({})
const thongBao = ref('')
const dangKeo = ref(null)
const keoCho = ref(null)
const chon = ref(null)
const nhom = computed(() => nhomTheoHang(dsThe.value))

async function tai() {
  try {
    const r = await doc(`/api/cong-viec?du_an=${encodeURIComponent(duAn.value)}`)
    dsThe.value = r.the
    loiDoc.value = r.loi
    if (chon.value) chon.value = r.the.find((t) => t.du_an === chon.value.du_an && t.id === chon.value.id) ?? null
  } catch (e) {
    thongBao.value = e.message
  }
}
onMounted(async () => {
  try {
    dsDuAn.value = (await doc('/api/du-an')).du_an.map((d) => d.ten)
  } catch (e) {
    thongBao.value = e.message
  }
  await tai()
})
watch([duAn, () => kho.phienBan], tai)

function tha(hang) {
  if (choPhepKeo(dangKeo.value, hang)) keoCho.value = { the: dangKeo.value, cot: hang }
  dangKeo.value = null
}
async function xacNhanKeo(viSao) {
  const { the, cot } = keoCho.value
  keoCho.value = null
  try {
    await ghi(`/api/bead/${encodeURIComponent(the.du_an)}/${encodeURIComponent(the.id)}/cot`,
      thanGhi({ cot, vi_sao: viSao || null }, the.updated_at))
    thongBao.value = ''
  } catch (e) {
    thongBao.value = e.status === 409 ? 'Bead đã đổi trên beads — đã tải lại, Đại ca kéo lại nếu vẫn muốn.' : e.message
  }
  await tai()
}
</script>

<template>
  <section class="cong-viec">
    <div class="cong-cu">
      <label>Dự án
        <select v-model="duAn"><option value="">Tất cả</option>
          <option v-for="d in dsDuAn" :key="d" :value="d">{{ d }}</option></select>
      </label>
      <span v-for="(l, t) in loiDoc" :key="t" class="loi">{{ t }}: {{ l }}</span>
      <span v-if="thongBao" class="loi" role="alert">{{ thongBao }}</span>
    </div>
    <section v-if="nhom['chua-cham'].length" class="hang-ngang" :aria-label="TEN_HANG['chua-cham']">
      <h2>{{ TEN_HANG['chua-cham'] }} <span class="dem-nho">{{ nhom['chua-cham'].length }}</span></h2>
      <div class="day"><TheBead v-for="t in nhom['chua-cham']" :key="t.du_an + '/' + t.id" :the="t" @mo="chon = t" /></div>
    </section>
    <div class="ba-cot">
      <section v-for="h in HANG_COT" :key="h" class="cot" :aria-label="TEN_HANG[h]" @dragover.prevent @drop.prevent="tha(h)">
        <h2>{{ TEN_HANG[h] }} <span class="dem-nho">{{ nhom[h].length }}</span></h2>
        <TheBead v-for="t in nhom[h]" :key="t.du_an + '/' + t.id" :the="t" @mo="chon = t" @keo="dangKeo = t" />
      </section>
    </div>
    <section v-for="h in ['theo-plan', 'epic']" :key="h" v-show="nhom[h].length" class="hang-ngang" :aria-label="TEN_HANG[h]">
      <h2>{{ TEN_HANG[h] }} <span class="dem-nho">{{ nhom[h].length }}</span></h2>
      <div class="day"><TheBead v-for="t in nhom[h]" :key="t.du_an + '/' + t.id" :the="t" @mo="chon = t" /></div>
    </section>
    <NganBen v-if="chon" :the="chon" @dong="chon = null" @chuyen="(cot) => (keoCho = { the: chon, cot })" @doi="tai" />
    <HopViSao v-if="keoCho" :the="keoCho.the" :cot="keoCho.cot" @huy="keoCho = null" @xac-nhan="xacNhanKeo" />
  </section>
</template>
```

`frontend/src/tuyen.js` (cả file):

```js
import CongViec from './trang/CongViec.vue'
import DuAn from './trang/DuAn.vue'

export const tuyen = [
  { path: '/', redirect: '/cong-viec' },
  { path: '/cong-viec', component: CongViec },
  { path: '/du-an', component: DuAn },
]
```

- [ ] **Step 2: Chạy kiểm**

```bash
cd frontend && npm run kiem && npm run build && cd ..
```

Expected: `ℹ pass 7`, "kiem-an-toan: 16 file, không có chèn HTML thô", "✓ built". Mỗi file `.vue` ≤ 120 dòng (`wc -l frontend/src/*/*.vue` — dài nhất `CongViec.vue` 85, `NganBen.vue` 77).

- [ ] **Step 3: Commit**

```bash
git add frontend/src/trang/CongViec.vue frontend/src/trang/NganBen.vue frontend/src/thanh/TheBead.vue \
  frontend/src/thanh/HopViSao.vue frontend/src/thanh/OChot.vue frontend/src/thanh/OTraLoi.vue \
  frontend/src/thanh/DongThoiGian.vue frontend/src/tuyen.js
git commit -m "feat(frontend): trang Công việc — ba cột, kéo giữa cột 1/2 có vì sao, ngăn bên, Chốt / dẫn ADR, Trả lời decision, dòng thời gian"
```

---

### Task 25: Frontend — trang Phê duyệt

**Độ khó:** `de` · **Song song:** đợt 3 — chạy cùng Task 9, 13, 14, 15, 16, 21. **Phải xong trước:** Task 24 (cùng sửa `src/tuyen.js`; dùng `OTraLoi.vue`).

**Files:**
- Create: `frontend/src/trang/PheDuyet.vue`, `frontend/src/thanh/MucPheDuyet.vue`
- Modify: `frontend/src/tuyen.js`

**Interfaces:**
- Consumes: `doc`, `ghi`, `thanGhi`; `kho`, `taiSoPheDuyet`; `TEN_PHE_DUYET`, `nhomPheDuyet`, `laLinkAnToan`, `gioVN`; `OTraLoi` (24); `GET /api/phe-duyet`; `POST /api/phe-duyet/.../duyet|tra-ve|tra-loi`; `POST /api/bead/.../thu-lai`.
- Produces: route `/phe-duyet`; component `MucPheDuyet` (props `muc`, `laDaiCa: boolean`; emits `doi`).

Hành vi (spec §5.2): nhóm theo độ gấp; Chờ review: link PR (chỉ `https://github.com/` — N1), cảnh báo bàn giao thiếu/lỗi, nút "Đã merge trên GitHub → đóng bead" khi có PR (kèm câu "thao tác tay, không phải bằng chứng máy") hoặc "Duyệt (đóng bead)", "Trả về + góp ý"; Spec chờ duyệt: nút Duyệt / Trả về có từ 2a (server 501 → "Chưa nối — phần 4b"), dòng hướng dẫn "Mở trên máy A"; Escalation **và decision mở** (Q4, G21): `OTraLoi` — "Trả lời (đóng escalation)" / "Trả lời (đóng decision)" + câu nhắc Q6; Cờ đỏ: link PR + lỗi bàn giao; Hệ cần xem: sự kiện, giờ, lỗi, nút "Thử lại" (khi có bead). Nút ghi tắt khi `la_dai_ca` false.

- [ ] **Step 1: Viết mã**

`frontend/src/thanh/MucPheDuyet.vue`:

```vue
<script setup>
import { ref } from 'vue'
import { ghi, thanGhi } from '../api.js'
import { gioVN, laLinkAnToan } from '../luat.js'
import OTraLoi from './OTraLoi.vue'

const props = defineProps({ muc: { type: Object, required: true }, laDaiCa: { type: Boolean, default: false } })
const emit = defineEmits(['doi'])
const gopY = ref('')
const loi = ref('')
const dangGui = ref(false)
const moTraVe = ref(false)
const ma = () => `${encodeURIComponent(props.muc.du_an)}/${encodeURIComponent(props.muc.bead_id)}`

async function lam(duongDan, noiDung) {
  dangGui.value = true
  loi.value = ''
  try {
    await ghi(duongDan, thanGhi(noiDung, props.muc.updated_at))
    gopY.value = ''
    moTraVe.value = false
    emit('doi')
    return true
  } catch (e) {
    loi.value = e.status === 501 ? 'Chưa nối — Duyệt / Trả về spec xử lý ở phần 4b.'
      : e.status === 409 ? 'Bead đã đổi — đã tải lại.' : e.message
    if (e.status === 409) emit('doi')
    return false
  } finally {
    dangGui.value = false
  }
}
const duyet = () => lam(`/api/phe-duyet/${ma()}/duyet`, {})
const traVe = () => lam(`/api/phe-duyet/${ma()}/tra-ve`, { gop_y: gopY.value.trim() })
const traLoi = (vb) => lam(`/api/phe-duyet/${ma()}/tra-loi`, { tra_loi: vb })
const thuLai = () => lam(`/api/bead/${ma()}/thu-lai`, {})
</script>

<template>
  <article class="muc">
    <header><span class="ma">{{ muc.bead_id || '(cả dự án)' }}</span> <span class="nho">{{ muc.du_an }}</span> {{ muc.tieu_de }}</header>
    <template v-if="muc.loai === 'cho-review' || muc.loai === 'co-do'">
      <p v-if="laLinkAnToan(muc.chi_tiet.pr)"><a :href="muc.chi_tiet.pr" target="_blank" rel="noopener noreferrer">Mở PR (bàn giao + diff)</a></p>
      <p v-else class="nho">Chưa có link PR GitHub.</p>
      <ul v-if="muc.chi_tiet.loi.length" class="canh-bao"><li v-for="l in muc.chi_tiet.loi" :key="l">{{ l }}</li></ul>
    </template>
    <div v-if="muc.loai === 'cho-review' || muc.loai === 'spec'" class="nut">
      <button type="button" :disabled="dangGui || !laDaiCa" @click="duyet">{{ muc.loai === 'spec' ? 'Duyệt spec'
        : laLinkAnToan(muc.chi_tiet.pr) ? 'Đã merge trên GitHub → đóng bead' : 'Duyệt (đóng bead)' }}</button>
      <button type="button" :disabled="dangGui || !laDaiCa" @click="moTraVe = !moTraVe">Trả về + góp ý</button>
    </div>
    <p v-if="muc.loai === 'cho-review' && laLinkAnToan(muc.chi_tiet.pr)" class="nho">
      Xác nhận "đã merge" là thao tác tay của Đại ca, không phải bằng chứng máy.</p>
    <form v-if="moTraVe" @submit.prevent="traVe">
      <label>Góp ý<textarea v-model="gopY" rows="3" maxlength="4000" required></textarea></label>
      <button type="submit" :disabled="dangGui || !gopY.trim()">Gửi trả về</button>
    </form>
    <p v-if="muc.loai === 'spec'" class="nho">Mở trên máy A: trong phiên Claude, dùng skill xem spec chờ duyệt
      (chỉ đọc) cho {{ muc.du_an }}/{{ muc.bead_id }}.</p>
    <OTraLoi v-if="muc.loai === 'escalation' || muc.loai === 'decision'" :gui="traLoi" :khoa="!laDaiCa"
             :nhan="muc.loai === 'escalation' ? 'Trả lời (đóng escalation)' : 'Trả lời (đóng decision)'" />
    <template v-if="muc.loai === 'he'">
      <p class="nho">{{ muc.chi_tiet.su_kien }} · {{ gioVN(muc.chi_tiet.luc) }}</p>
      <pre class="van-ban">{{ muc.chi_tiet.loi }}</pre>
      <button v-if="muc.bead_id" type="button" :disabled="dangGui || !laDaiCa" @click="thuLai">Thử lại</button>
    </template>
    <p v-if="loi" class="loi" role="alert">{{ loi }}</p>
  </article>
</template>
```

`frontend/src/trang/PheDuyet.vue`:

```vue
<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { doc } from '../api.js'
import { kho, taiSoPheDuyet } from '../kho.js'
import { TEN_PHE_DUYET, nhomPheDuyet } from '../luat.js'
import MucPheDuyet from '../thanh/MucPheDuyet.vue'

const ds = ref([])
const loi = ref('')
const loiDoc = ref({})
const nhom = computed(() => nhomPheDuyet(ds.value))

async function tai() {
  try {
    const r = await doc('/api/phe-duyet')
    ds.value = r.muc
    loiDoc.value = r.loi
    loi.value = ''
  } catch (e) {
    loi.value = e.message
  }
}
async function doi() {
  await tai()
  await taiSoPheDuyet()
}
onMounted(tai)
watch(() => kho.phienBan, tai)
</script>

<template>
  <section>
    <h1>Phê duyệt <span class="dem-nho">{{ kho.soPheDuyet }}</span></h1>
    <p v-if="loi" class="loi" role="alert">{{ loi }}</p>
    <p v-for="(l, t) in loiDoc" :key="t" class="loi">{{ t }}: {{ l }}</p>
    <p v-if="!nhom.length && !loi" class="nho">Không có việc nào chờ Đại ca.</p>
    <section v-for="[loai, muc] in nhom" :key="loai">
      <h2>{{ TEN_PHE_DUYET[loai] }} <span class="dem-nho">{{ muc.length }}</span></h2>
      <MucPheDuyet v-for="m in muc" :key="m.loai + '/' + m.du_an + '/' + (m.bead_id || '')" :muc="m"
                   :la-dai-ca="Boolean(kho.trangThai && kho.trangThai.la_dai_ca)" @doi="doi" />
    </section>
  </section>
</template>
```

`frontend/src/tuyen.js` (cả file):

```js
import CongViec from './trang/CongViec.vue'
import DuAn from './trang/DuAn.vue'
import PheDuyet from './trang/PheDuyet.vue'

export const tuyen = [
  { path: '/', redirect: '/cong-viec' },
  { path: '/cong-viec', component: CongViec },
  { path: '/du-an', component: DuAn },
  { path: '/phe-duyet', component: PheDuyet },
]
```

- [ ] **Step 2: Chạy kiểm**

```bash
cd frontend && npm run kiem && npm run build && cd ..
```

Expected: `ℹ pass 7`, "kiem-an-toan: 18 file, không có chèn HTML thô", "✓ built". `wc -l frontend/src/thanh/MucPheDuyet.vue` ≤ 120.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/trang/PheDuyet.vue frontend/src/thanh/MucPheDuyet.vue frontend/src/tuyen.js
git commit -m "feat(frontend): trang Phê duyệt — Duyệt / xác nhận merge tay, Trả về, Trả lời escalation / decision mở, thử lại, spec chờ 4b"
```

---

### Task 26: Kiểm chứng trên máy B + kiểm tay giao diện (Đại ca + agent; phần tailnet **chờ #5**)

**Độ khó:** `kho` (thao tác thật, cần Đại ca) · **Song song:** không — sau mọi task 1–25, `uv run pytest -q` = 408 passed, `npm run kiem` + `npm run build` xanh.

Không viết mã sản phẩm. Kết quả ghi vào mục "Ghi chú triển khai" cuối plan này (như plan 0+1a). Mọi bước có **(Đại ca)** do Đại ca tự làm; agent không nhập bí mật, không chạy `tram chu cai-dat`, không đăng nhập Tailscale.

> **Ghi chú 15/10/2026** (không đổi task): phần "chờ #5" của task này là đăng nhập Tailscale máy B, việc đó đã xong (`bs-g28.9`). Task 26 vẫn chưa chạy (`bs-6o0.11`). Trên máy B hiện chỉ `vn.tram.bao-tin` và `vn.tram.nho` đang chạy (LaunchAgent). `vn.tram.api`, `vn.tram.quet`, `vn.tram.sao-luu` chưa cài, nên Step 5 vẫn phải làm. Plist `vn.tram.bao-tin` đã có sẵn và sẽ được nạp lại cùng ba plist kia. Xem [quyết định 13/10, mục "Ghi chú 15/10"](../quyet-dinh/2026-10-13-tra-loi-cau-hoi-gop.md).

- [ ] **Step 1 (Đại ca): Cấu hình** — tạo `~/.tram/cau-hinh.yaml` theo mẫu ở Task 5 (login Tailscale của mình, tên máy B, `dashboard_url`; `telegram.chat_id` khi đã có bot).

- [ ] **Step 2: Build frontend trên máy B**

```bash
cd frontend && npm ci && npm run kiem && npm run build && cd ..
```

- [ ] **Step 3: Chạy thử cục bộ, chỉ đọc (không cần #5)**

```bash
uv run tram api &                                          # nghe 127.0.0.1:7700
curl -sI http://127.0.0.1:7700/                            # có content-security-policy, x-frame-options; KHÔNG có "server:"
curl -s -o /dev/null -w '%{http_code}\n' -H 'Host: evil.example:7700' http://127.0.0.1:7700/api/du-an   # 421
curl -s http://127.0.0.1:7700/api/chu/trang-thai           # "la_dai_ca": false
curl -s -o /dev/null -w '%{http_code}\n' -X POST -H 'Content-Type: application/json' -H 'X-Tram: 1' \
  -d '{"ma_thao_tac":"ma-thu-cuc-bo-1","expected_version":"tat"}' http://127.0.0.1:7700/api/chu/estop   # 403
lsof -nP -iTCP:7700 -sTCP:LISTEN                           # chỉ 127.0.0.1
kill %1
```

Expected: header CSP đúng chuỗi spec §4 mục 6, không `server`; Host lạ → 421 (G17); trạng thái đọc được, POST không danh tính → 403 (D4 phía cục bộ), chỉ nghe localhost (§4 mục 1). (Đã chạy đúng các lệnh này trên bản sao 13/10 với `TRAM_HOME`/`TRAM_REPO` tạm, cổng 7799 — Tự review mục 4.) Lưu ý đã biết (§4 mục 2b): một tiến trình cục bộ **gửi kèm** header danh tính vẫn ghi được — chấp nhận ở 2a, phải đóng trước 3a.

- [ ] **Step 4 (Đại ca): Kiểm tay giao diện trên máy B** — mở `http://127.0.0.1:7700/` (chỉ đọc vì thiếu header): ba cột, hàng chưa chấm / epic, ngăn bên (decision mở có ô Trả lời), Phê duyệt, Dự án, thanh trạng thái; chế độ tối; thu cửa sổ còn 375 px; điều hướng bằng bàn phím (Tab, Enter mở thẻ); kéo thẻ trên Firefox (N2). Mở DevTools → Console: **không** có lỗi `Content-Security-Policy` / `Refused to …` (C1). Ghi góp ý giao diện vào "Ghi chú triển khai".

- [ ] **Step 5 (Đại ca): Cài dịch vụ** — `uv run tram chu cai-dat`, đọc kế hoạch (4 plist, cảnh báo, "gọi ra ngoài: Claude API, api.telegram.org, GitHub"), gõ `dong-y` nếu đồng ý. `tram bao-tin` thoát mã 0 khi chưa có token / `chat_id` và launchd **không** tự bật lại (N3): cấu hình Telegram xong thì chạy `launchctl kickstart -k gui/$UID/vn.tram.bao-tin`, rồi `tail ~/.tram/log/bao-tin.log` không còn dòng "Chưa cấu hình".

- [ ] **Step 6 (Đại ca, tuỳ chọn): Kiểm cờ `bd` với giá trị bắt đầu bằng `-`** — trên một DB `bd` tạm (như spike 13/10), không phải repo dự án: `bd create "t" -t decision -d "- mô tả" --silent`, `bd close <id> --reason "- trả lời"`, rồi `bd list --json --all --limit 0` phải có đúng mô tả và `close_reason` đó. Sai → báo agent đổi `Bd.tao/dong` sang dạng `--reason=<giá trị>`.

- [ ] **Step 7 (Đại ca — chờ #5): Mở qua tailnet và kiểm danh tính**

1. Chạy lệnh `tailscale serve` mà `tram chu cai-dat` in ra (kiểm cú pháp với phiên bản Tailscale trên B).
2. Từ máy A (trình duyệt, đăng nhập tailnet bằng tài khoản Đại ca): `https://<ten_may_b>/` → thanh trạng thái có nút Estop bật được (`la_dai_ca: true`).
3. Từ một thiết bị **gắn tag** hoặc người khác trong tailnet: `curl -s https://<ten_may_b>/api/chu/trang-thai` → `la_dai_ca: false`; thêm `-H 'Tailscale-User-Login: <login Đại ca>'` → **vẫn** `false` (Tailscale phải ghi đè/bỏ header khách gửi). Nếu `true` → **dừng**, không dùng dashboard ghi; báo để chuyển phương án "mã truy cập dài + cookie" (spec §4 mục 2 — cần spec bổ sung).
4. Xác nhận `Host` mà `tailscale serve` gửi tới `127.0.0.1:7700` (log truy cập của uvicorn: yêu cầu bị 421 nghĩa là Host ngoài danh sách; hoặc `tcpdump -A -i lo0 port 7700`). Phải là `<ten_may_b>` hoặc `<ten_may_b>:443` (G17). Khác → báo agent bổ sung `host_hop_le` (Task 10), không tắt kiểm Host.

- [ ] **Step 8 (chờ #5): D1–D6 trên một dự án nháp (không phải HR Codex, theo #4)**

| # | Cách kiểm | Đạt khi |
|---|---|---|
| D1 | `bd -C <repo nháp> list --json --all --limit 0 > <scratch>/bd.json` (`bd.json` là ảnh của **DB beads nháp** — không chạy trên HR Codex, N8); `curl -s "http://127.0.0.1:7700/api/cong-viec?du_an=<tên>" > <scratch>/cv.json`; chạy đoạn Python dưới | `lệch: []` |
| D2 | `bd update <id> --add-label cot:ai-lam` trên repo nháp, đợi lượt quét (`quet.xong`) | thẻ đổi trên dashboard ≤ 10 s sau `quet.xong`, không tải lại trang |
| D3 | Kéo một thẻ cột 1 → cột 2, nhập "vì sao"; Chốt một bead cột 2 và ghi thời gian từ bấm tới khi ngăn bên tải lại (Chốt gọi khoảng 6 lần `bd list --all` — N6; > 10 s thì ghi vào "Ghi chú triển khai" để tối ưu sang `bd show` khi có spike) | `bd show <id> --json` có `cot:can-chot` + `cot-khoa`, không còn `cot:ai-lam`; `sqlite3 ~/.tram/su-kien.db "select du_lieu from su_kien where loai='cot.dai_ca_sua' order by id desc limit 1"` có `vi_sao`, `"nguon": "dashboard"`, `"da_ghi": true`; bấm lại cùng thao tác (F5 rồi double-click) không sinh sự kiện thứ hai |
| D4 | Step 7.3 + Step 3 | mọi POST từ ngoài danh sách bị 403 |
| D5 | (Đại ca tạo bot, đưa token vào Keychain, điền `chat_id`) đưa bead nháp vào cột 3 | tin Telegram ≤ 2 phút, chỉ có tên dự án + số việc + mã bead + link; bead thứ hai trong 5 phút không có tin riêng ngay, đến hạn cửa sổ thì có một tin gom |
| D6 | Từ máy A: `curl -o /dev/null -s -w '%{time_total}\n' https://<ten_may_b>/` và DevTools (tải lần đầu, xoá cache) | ≤ 2 giây |

Đoạn kiểm D1 (chạy từ thư mục repo trạm; `<scratch>` là thư mục tạm của phiên):

```bash
uv run python - "<scratch>/bd.json" "<scratch>/cv.json" <<'PY'
import json, sys
bd = {b["id"]: b for b in json.load(open(sys.argv[1]))}
cv = json.load(open(sys.argv[2]))["the"]
LUONG = {"can-spec": "ai-lam", "cho-duyet-spec": "can-chot", "tram:escalation": "can-chot"}
lech = []
for t in cv:
    nhan = set(bd[t["id"]].get("labels") or [])
    if t["hang"] in ("ai-lam", "can-chot", "cho-review"):
        hop_le = f"cot:{t['hang']}" in nhan or any(LUONG.get(n) == t["hang"] for n in nhan)
        if not hop_le:
            lech.append(t["id"])
print("lệch:", lech)
PY
```

- [ ] **Step 9: Ghi kết quả** vào mục "Ghi chú triển khai" cuối plan (bảng D1–D6, Host thật của `tailscale serve` (G17), thời gian Chốt (N6), góp ý giao diện của Đại ca, chỗ mã khác plan và lý do), commit `docs: ghi chú triển khai lát 2a`.

---

## Sơ đồ đợt chạy

Số test dưới đây là kết quả **chạy thật** trên bản sao 13/10: dựng trạng thái sau từng đợt từ `git archive HEAD` + đúng file của các task đã xong (kể cả bản trung gian của `bd.py` sau Task 1, `cli.py` sau Task 16, `app.py` sau Task 12/17), rồi `uv run pytest -q` (Tự review mục 4).

```
Đợt 0 — điều kiện tiên quyết
  plan 1a (2026-10-13-sua-ma-1a-lat-2a) đã merge vào main (d63c41c) → uv run pytest -q = 239 passed

Đợt 1 — song song (T1 bước 1–2 chạy trước vì đổi môi trường uv; các task Python khác chờ `uv add` xong rồi chạy)
  T1 phụ thuộc + KhongThayBead + công cụ test · T2 kho sự kiện WAL/sau_id/close · T3 sao lưu
  T5 cấu hình trạm · T7 đọc bàn giao có lỗi · T19 tin + chống ồn + tra_lai · T23 khung frontend (.vue)
  → 277 passed (239 + 4 + 8 + 4 + 9 + 6 + 7); frontend: pass 7, kiem-an-toan 9 file, vite build xanh

Đợt 2 — song song
  T4 khung thao tác (T2) · T6 bọc bd ghi (T1 — cùng file bd.py) · T8 suy cột (T1)
  T10 danh tính + CSRF + CSP + Host (T1, T5) · T11 bộ đệm (T1) · T20 nguồn tin (T2, T19)
  T24 trang Công việc (T23)
  → 323 passed (+11 +8 +13 +6 +4 +4); frontend: kiem-an-toan 16 file, build xanh

Đợt 3 — song song
  T9 suy Phê duyệt (T2, T7, T8) · T13 kéo cột + thử lại (T4, T6, T8) · T14 Chốt (T4, T6, T8)
  T15 Duyệt/Trả về/Trả lời decision (T4, T6, T7, T8) · T16 estop dùng chung (T4; sửa cli.py)
  T21 Telegram + vòng lặp + gửi lại (T5, T19, T20) · T25 trang Phê duyệt (T24)
  → 382 passed (+6 +12 +16 +13 +4 +8); frontend: kiem-an-toan 18 file, build xanh

Đợt 4
  T12 tram-api đọc + nối middleware (T1, T2, T4, T5, T8, T9, T10, T11)
  → 390 passed (+8)

Đợt 5 — song song
  T17 POST ghi (T10, T12–T16; sửa app.py) · T22 lệnh dịch vụ + launchd (T3, T12, T16, T21; sửa cli.py)
  → 402 passed (+6 +6)

Đợt 6
  T18 SSE (T2, T11, T17; sửa app.py)
  → 408 passed (+6)

Đợt 7 — Đại ca + agent
  T26 kiểm chứng máy B (phần tailnet, Telegram thật, D1–D6: chờ #5)
```

| Task | Độ khó | Đợt | Phải xong trước | File chạm (ngoài test) | Test mới |
|---|---|---|---|---|---|
| 1 | de | 1 | plan 1a (đã xong) | `pyproject.toml`, `uv.lock`, `beads/bd.py` (`KhongThayBead`), 4 `__init__.py`; `tests/asgi_gia.py`, `bead_gia.py`, `bd_gia.py` | 4 |
| 2 | de | 1 | plan 1a | `su_kien/ket_noi.py`, `su_kien/kho.py` | 8 |
| 3 | de | 1 | — | `su_kien/sao_luu.py` | 4 |
| 4 | kho | 2 | 2 | `thao_tac/loi.py`, `kho.py`, `chay.py`, `chung.py` | 11 |
| 5 | de | 1 | — | `cau_hinh/tram.py` | 9 |
| 6 | de | 2 | 1 | `beads/bd.py` | 8 |
| 7 | de | 1 | plan 1a | `ban_giao/doc.py` | 6 |
| 8 | kho | 2 | 1 | `suy/lam_sach.py`, `suy/cot.py` | 13 |
| 9 | kho | 3 | 2, 7, 8 | `suy/chi_tiet.py`, `phe_duyet.py`, `trang_thai.py` | 6 |
| 10 | de | 2 | 1, 5 | `api/bao_mat.py` | 6 |
| 11 | de | 2 | 1 | `api/bo_dem.py` | 4 |
| 12 | kho | 4 | 1, 2, 4, 5, 8, 9, 10, 11 | `api/phu_thuoc.py`, `app.py`, `tuyen_doc.py`; `tests/api_gia.py` | 8 |
| 13 | kho | 3 | 4, 6, 8 | `thao_tac/cot.py` | 12 |
| 14 | kho | 3 | 4, 6, 8 | `thao_tac/chot.py` | 16 |
| 15 | kho | 3 | 4, 6, 7, 8 | `thao_tac/phe_duyet.py` | 13 |
| 16 | de | 3 | 4 | `chu/dieu_khien.py`, `thao_tac/estop.py`, `cli.py` | 4 |
| 17 | kho | 5 | 10, 12–16 | `api/than.py`, `tuyen_ghi.py`, `tuyen_chu.py`, `app.py` | 6 |
| 18 | kho | 6 | 2, 11, 17 | `api/luong.py`, `app.py` | 6 |
| 19 | kho | 1 | — | `bao_tin/tin.py`, `chong_on.py` | 7 |
| 20 | de | 2 | 2, 19 | `bao_tin/nguon.py` | 4 |
| 21 | kho | 3 | 5, 19, 20 | `bao_tin/telegram.py`, `luu.py`, `vong.py` | 8 |
| 22 | de | 5 | 3, 12, 16, 21 | `cli_dich_vu.py`, `cli.py`, `chu/launchd.py`, `chu/cai_dat.py` | 6 |
| 23 | de | 1 | — | `frontend/*` khung (`package.json` có plugin-vue, 3 `.vue`), `.gitignore` | 7 (node) |
| 24 | kho | 2 | 23 | `frontend/src/trang/CongViec.vue`, `NganBen.vue`, 5 file `thanh/*.vue`, `tuyen.js` | — (build) |
| 25 | de | 3 | 24 | `frontend/src/trang/PheDuyet.vue`, `thanh/MucPheDuyet.vue`, `tuyen.js` | — (build) |
| 26 | kho | 7 | 1–25 | (không mã) ghi chú triển khai | — |

## Tự review

**1. Độ phủ spec lát 2a**

| Yêu cầu spec | Task | Kiểm bằng |
|---|---|---|
| §3 tram-api FastAPI trong gói, nghe 127.0.0.1:7700, phục vụ file tĩnh | 12, 22 | `test_phuc_vu_file_tinh_va_tat_docs`, `test_tram_api_chi_nghe_localhost`, `test_tram_api_khong_co_tuy_chon_host` |
| §3 bộ đệm beads theo dự án, làm mới khi `quet.xong` / sau ghi, ≤ 30 s | 11, 17, 18 | `test_bo_dem.py`, `test_keo_cot_qua_api_lap_lai_va_lam_moi_bo_dem`, `test_quet_xong_lam_moi_va_bao_doi` |
| §3 / Q12 trạng thái tính lúc đọc | 8, 9 | `test_suy_cot.py`, `test_suy_phe_duyet.py` |
| §4.1 chỉ 127.0.0.1, không funnel | 22, 26 | test host; Task 26 bước 3 `lsof` |
| §4.2 danh tính `Tailscale-User-Login` ∈ `dai_ca_logins`, thiếu → chỉ đọc | 5, 10, 26 | `test_bao_mat.py`, `test_ghi_khong_du_danh_tinh_hoac_csrf_bi_403`; thật: Task 26 bước 7 (chờ #5) |
| §4.2b cách ly | — | ngoài 2a (điều kiện trước 3a) — ghi rủi ro ở `bao_mat.py` và Task 26 bước 3 |
| §4.3 CSRF `X-Tram` + `Origin` | 10, 23 | `test_kiem_ghi_tung_dieu_kien`; frontend `ghi` gắn `X-Tram` (test node) |
| §4.4 text, lọc điều khiển/bidi, cắt độ dài | 8, 9, 23 | `test_lam_sach_*`, `test_the_bead_truong_va_lam_sach`; `kiem-an-toan.mjs` (cả `:innerHTML`, `v-bind:innerHTML`); `vite build` dịch mọi template `.vue` |
| §4.6 CSP chặt + `nosniff`/`no-referrer`/`DENY` trên mọi phản hồi; Host lạ → 421; không header phiên bản server | 10, 12, 22, 23, 26 | `test_header_an_toan_tren_moi_phan_hoi`, `test_host_ngoai_danh_sach_la_421`, `test_header_an_toan_va_host_421`, `test_tram_api_chi_nghe_localhost` (`server_header=False`); bundle không có `new Function`; trình duyệt trên bản sao: 0 vi phạm CSP; Task 26 bước 3–4, 7.4 |
| §4.5 Telegram không nội dung nghiệp vụ | 19 | `test_soan_tin_khong_co_noi_dung_nghiep_vu` |
| §5.1 chọn dự án / tất cả, ba cột, luật suy cột, nhãn lệch, khe spec, theo-plan, escalation, chưa chấm, mờ "chờ <id>" | 8, 12, 24 | `test_cot_theo_nhan`, `test_nhan_luong_va_escalation`, `test_bi_chan_mo_va_fail_closed`, `test_cong_viec_tat_ca_va_loc` |
| §5.1 thẻ: mã, tiêu đề, loại, ưu tiên, dự án, khoá, chờ, cờ đỏ | 8, 24 | `test_the_bead_truong_va_lam_sach` |
| §5.1 ngăn bên: lý do, câu hỏi, mô tả, nghiệm thu, dòng thời gian | 2 (`cua_bead`), 9, 12, 24 | `test_chi_tiet_bead` (×2) |
| §5.1 kéo cột 1↔2, vì sao, gỡ **mọi** `cot:*`, `cot-khoa`, `cot.dai_ca_sua {…, nguon, da_ghi}`, `ma_thao_tac` + `expected_version` | 13, 17, 24 | `test_keo_cot.py` (12 ca) |
| §5.1 epic hàng riêng, không chốt; không kéo vào/ra cột 3 | 8, 13, 24 | `test_epic_hang_rieng…`, `test_luat_keo`, `test_khong_keo_duoc` |
| §5.1 Chốt: create decision + close reason → dep add blocks → gỡ `cot-khoa` + mọi `cot:*` → `cot.da_chot`; idempotent; dẫn ADR | 14, 17, 24 | `test_chot.py` (16 ca) |
| §5.1 yêu cầu chấm lại bền sau Chốt | plan 1a (so ảnh decision) | "Phụ thuộc plan 1a" mục 1 |
| §5.1 trang Dự án | 9, 12, 23 | `test_du_an_dem_cot_va_quet_cuoi` |
| §5.2 badge menu + tiêu đề tab | 23 | `tieuDeTab` (node test) |
| §5.2 Chờ review: Duyệt có/không `pr`, ghi rõ thao tác tay; bàn giao lỗi vẫn Duyệt + cảnh báo; Trả về gỡ `cot:*` + `cot-khoa`, góp ý vào notes, `cot.tra_ve`; bead hoãn không Duyệt / Trả về (Q2) | 7, 9, 15, 25 | `test_thao_tac_phe_duyet.py` (gồm `test_bead_hoan_khong_duyet_khong_tra_loi`), `test_gom_phe_duyet_du_loai_va_thu_tu` |
| §5.2 Spec chờ duyệt: nút có từ 2a, xử lý 4b; "Mở trên máy A" | 15, 17, 25 | `test_spec_la_501_khong_ghi_gi`, `test_ma_loi_http` |
| §5.2 Escalation **và decision mở**: Trả lời = `bd close <decision> --reason`, sự kiện chung `escalation.tra_loi {escalation_id = id decision}`; nút ở ngăn bên (cột 2) và Phê duyệt | 8, 9, 15, 17, 24, 25 | `test_tra_loi_escalation`, `test_tra_loi_decision_mo_khong_phai_escalation`, `test_luat_tra_loi`, `test_gom_phe_duyet_du_loai_va_thu_tu` (mục `decision`), `test_chot_tra_ve_tra_loi_thu_lai` (API) |
| §5.2 Cờ đỏ: link PR | 9, 25 | `test_gom_phe_duyet_du_loai_va_thu_tu` |
| §5.2 Hệ cần xem: `cham_cot.bo_qua`, `quet.loi`; thử lại = `cham_cot.thu_lai` | 9, 13, 25 | `test_gom_phe_duyet…`, `test_du_an_doc_bd_loi_van_hien_quet_loi`, `test_thu_lai_ghi_su_kien_mot_lan` |
| §5.3 thanh trạng thái: estop, quét cuối, lỗi gần nhất, nút estop / tiếp tục cùng logic CLI | 9, 12, 16, 17, 23 | `test_trang_thai`, `test_estop_2a.py`, `test_estop_va_tiep_tuc_qua_api` |
| §6 `tram/bao_tin/`, dịch vụ launchd riêng, đọc theo `sau_id` mốc riêng | 2, 21, 22 | `test_mot_vong_tu_moc_den_tin`, `test_ke_hoach_cai_dat_co_bon_dich_vu` |
| §6 nguồn tin lát 2a (so ảnh sau `quet.xong`; `quet.loi`, `cham_cot.bo_qua`; estop) | 20 | `test_nguon_tin.py` |
| §6 chống ồn: tin đầu gửi ngay, gom 5 phút, 1 giờ, giờ yên lặng | 19 | `test_chong_on.py` |
| §6 gửi lỗi → xếp lại, gửi lại vòng sau, không tính luật 1 giờ | 19, 21 | `test_gui_loi_tra_lai_thi_vong_sau_gui_lai_khong_chan_1_gio`, `test_mot_vong_gui_loi_thi_vong_sau_gui_lai` |
| §6 token Keychain `tram-telegram-bot-token`, `chat_id` trong cấu hình; Q15 thêm api.telegram.org | 5, 21, 22 | `test_doc_token_env_roi_keychain`, `test_canh_bao_telegram_cau_hinh_tailscale` |
| §7 mọi API lát 2a (GET 5, POST 8, SSE) | 12, 17, 18 | `test_api_doc.py`, `test_api_ghi.py`, `test_luong.py` |
| §8 phụ thuộc chỉ fastapi, uvicorn, Vue 3, Vite, vue-router, `@vitejs/plugin-vue`; khoá chính xác; Telegram bằng urllib | 1, 21, 23 | bước ghim phiên bản (số thật ở G20); `gui_telegram` dùng `urllib` |
| §9.1 unit test suy cột / phê duyệt / báo tin / danh tính + CSRF | 8, 9, 10, 19, 20 | các file test tương ứng |
| §9.2 test API với `bd` giả lập | 12, 17, 18 | `BdGia` |
| §9.3–9.4 máy B thật D1–D6, kiểm tay A + điện thoại | 26 | chờ #5 |
| §12.2 `SuKien.id` (1a) + `sau_id` + cột token qua mô hình đọc | 2 | `test_su_kien_giu_cot_token…`, `test_sau_id_phan_trang` |
| §12.2 WAL + timeout; sao lưu | 2, 3, 22 | `test_ket_noi_wal_va_timeout`, `test_doc_dang_mo_khong_chan_ghi`, `test_sao_luu.py`, plist `sao-luu` |
| §12.2 bảng `thao_tac` đúng cột | 4 | `test_kho_tao_lay_danh_dau_ket_thuc` |
| §12.2 `_tram` cho sự kiện hệ; liệt kê dự án bỏ `_*` | 12, 16, 18, 21 | `phu_thuoc_that`, `test_su_kien_tram_khong_doc_lai…` |
| §12.2 bảng sự kiện 2a (producer dashboard; `ma_thao_tac?` trong `cot.dai_ca_sua`/`estop.*`; Duyệt không có sự kiện; decision mở dùng `escalation.tra_loi`) | 13–16 | dữ liệu sự kiện kiểm nguyên văn trong test |
| §12.3 khoá theo bead, ghi tiến độ trước `bd`, cùng mã → kết quả cũ, khác nội dung → 409, crash → đối soát làm tiếp, version → 409 | 4, 13–15 | `test_thao_tac_khung.py`; ca: double-click Chốt, crash sau create trước close, crash sau close trước dep add, Trả về hai lần — `test_chot.py`, `test_tra_ve_hai_lan_cung_ma` |
| §12.5 thử lại (phía ghi), `quet.loi` (1a), đọc bàn giao có lỗi, `cau-hinh.yaml`, bọc `bd create/close/dep add`, dòng "gọi ra ngoài" của cài đặt, giao diện theo skill | 13, plan 1a, 7, 5, 6, 22, 23–26 | như trên |

Không làm (đúng phạm vi): lát 2b/2c/2d, `POST /api/phieu/kiem` và hàng "Feature xong" (phần 4), xử lý Duyệt spec (4b), cách ly §4 mục 2b (trước 3a), tự đóng theo PR (4c), plan 1a.

**2. Quét placeholder:** không có "TBD/TODO/tương tự task N/thêm xử lý lỗi phù hợp"; mọi bước mã có mã đầy đủ; mọi lệnh kiểm có kết quả mong đợi. Số phiên bản gói đã ghi số thật đã chạy (G20) — lúc thực thi giải ra số khác thì làm theo thủ tục Task 1 bước 1 / Task 23 bước 2. Giá trị chỉ biết lúc chạy là tên máy / login / chat_id của Đại ca (Task 26, Đại ca tự điền) và Host thật của `tailscale serve` (Task 26 bước 7.4). `<scratch>` ở Task 26 là thư mục tạm của phiên người thực thi.

**3. Khớp chữ ký giữa task**

- `NguCanhGhi(bd, kho, kho_tt, du_an)` (T4) = chỗ dựng ở T13–T15 test và `tuyen_ghi._chay` (T17).
- `chay_thao_tac(kho_tt, yc, *, kiem_moi, cac_buoc)` / `YeuCau(ma, loai, du_an, bead_id, noi_dung, expected_version)` / `KetQuaThaoTac(ket_qua, lap_lai)` (T4) = T13, T14, T15, T16.
- `keo_cot(nc, bead_id, *, cot, vi_sao, ma, expected_version)`, `thu_lai(nc, bead_id, *, ma, expected_version)` (T13); `chot(nc, bead_id, *, tra_loi, adr, ma, expected_version)` (T14); `duyet(..., expected_commit=None, digest_bead=None)`, `tra_ve(..., gop_y, ...)`, `tra_loi_decision(..., tra_loi, ...)` (T15); `bat_estop_thao_tac(kho, kho_tt, *, ly_do, ma, expected_version)`, `tiep_tuc_thao_tac(kho, kho_tt, *, ma, expected_version)` (T16) = lời gọi ở T17.
- `cham_gan_nhat(kho, du_an, bead_id)` (T8) = T9 (`chi_tiet`), T14 (`cau_hoi_hien_tai`).
- `tom_tat_ban_giao(notes) -> dict | None` (T7) = T9 (`ban_giao_sach`), T15 (`duyet`).
- `BoDemBeads.lay / danh_dau_cu / phien_ban` (T11) = T12, T17, T18.
- `kiem_du_an_bead(pt, du_an, bead_id=None)`, `PhuThuocApi` (T12) = T17; `tests/api_gia.tao_app_gia` (T12) = T17, T18.
- `KhoSuKien.sau_id / id_moi_nhat / cua_bead` (T2) = T9, T18, T20, T21.
- `Tin(loai, du_an, bead_id)`, `soan_tin(loai, tins, url)`, `BoChongOn.nhan/den_han/trang_thai` (T19) = T20, T21.
- `KEYCHAIN_TELEGRAM` (T21) = T22; `bat_estop/tat_estop/DU_AN_TRAM` (T16) = T16 CLI, `thao_tac/estop.py`.
- `KhongThayBead` (T1) = `BdGia.mot` (T1), `Bd.mot` (T6), `MA_LOI` 404 (T12); `them_header_an_toan(app, ch, *, cong)`, `host_hop_le` (T10) = `tao_app(pt, *, cong=7700)` (T12) = `_api` (T22, `cong=args.cong`); `KhoSuKien.close`, `KhoThaoTac.close` (T2, T4) = `closing(...)` ở T12, T17, T18; `BoChongOn.tra_lai(tg)` (T19) = `mot_vong` (T21); `ly_do_khong_tra_loi`, `hien_tren_bang` (T8) = T15; `OTraLoi` (T24) = `NganBen` (T24), `MucPheDuyet` (T25).
- Khoá JSON `The` (T8 `the_bead`) = frontend `TheBead`, `CongViec`, `NganBen` (`keo_duoc`, `chot_duoc`, `tra_loi_duoc`, `hang`, `cho`, `khoa`, `co_do`, `lech`, `khe_spec`, `uu_tien`, `updated_at`); mục Phê duyệt (T9, `loai` có `decision`) = `luat.js` `TEN_PHE_DUYET` + `MucPheDuyet` (`chi_tiet.pr`, `chi_tiet.loi`, `chi_tiet.su_kien`, `chi_tiet.luc`, `updated_at`).
- Tên sự kiện ghi = bảng §12.2: `cot.dai_ca_sua`, `cot.da_chot`, `cot.tra_ve`, `cham_cot.thu_lai`, `escalation.tra_loi`, `estop.bat`, `estop.tat` (T13–T16) — đúng chuỗi trong `LOAI_LAM_MOI` (T18).

**4. Chạy thử mã trong plan (13/10, bản sửa theo review Fable — có mạng để cài gói vào bản sao):** dựng bản sao `git archive HEAD` (`main` = `3c4940b`, mã như `d63c41c`), `uv add fastapi uvicorn` rồi ghim `==` (đúng Task 1 bước 1), `npm install --save-exact …` (đúng Task 23 bước 2) — chỉ trong bản sao, repo thật không đổi. Tách nguyên văn mọi khối "cả file"/file mới của plan này, áp các sửa từng phần (Task 1 + 6 `bd.py`, Task 16/22 `cli.py`, Task 17/18 `app.py`):

- `pytest`: **408 passed** = 239 cũ + 169 mới, **gồm cả 32 test cần FastAPI/uvicorn** (`test_ho_tro_gia` 4, `test_bao_mat` 6, `test_api_doc` 8, `test_api_ghi` 6, `test_luong` 6, 2 test `tram api` của `test_cli_dich_vu`) mà bản trước chưa chạy được. Lần chạy đầu lộ một lỗi thật của bản trước: `test_tuyen_luong_da_dang_ky` soi `app.routes[i].path` — FastAPI 0.143 trả `_IncludedRouter` không có `.path` → đổi thành gọi `GET /api/luong` qua `asgi_gia` (200 + `text/event-stream`).
- **Mô phỏng từng đợt** (dựng lại từ `git archive` + file của các task đã xong, kể cả bản trung gian `bd.py` sau T1, `cli.py` sau T16, `app.py` sau T12/T17): đợt 1 → 277, đợt 2 → 323, đợt 3 → 382, đợt 4 → 390, đợt 5 → 402, đợt 6 → 408 passed; trạng thái cuối trùng từng byte với bản sao đầy đủ. Bước "thấy fail" của Task 6 đổi thành `AttributeError … 'mot'` vì `KhongThayBead` đã có từ Task 1 (đã chạy).
- Frontend: `npm run kiem` → `ℹ pass 7`, `kiem-an-toan` sạch (9 → 16 → 18 file theo Task 23 → 24 → 25); `npm run build` xanh ở cả ba mốc (vite 8.3.4, 112 KB JS / 4,3 KB CSS); `grep "new Function" dist/assets/*.js` = 0; build đỏ khi cố ý làm sai một thẻ đóng (`RolldownError: Invalid end tag.`) — `vite build` đủ làm cổng thay `kiem-template.mjs` (đã xoá).
- **Kiểm CSP thật:** chạy `uv run tram api --cong 7799` từ bản sao với `TRAM_HOME`, `TRAM_REPO` trỏ thư mục tạm (`du-an/` rỗng → không gọi `bd`, `frontend/dist` liên kết tới bản build): `curl -sI /` có `content-security-policy` đúng chuỗi spec, `x-content-type-options`, `referrer-policy`, `x-frame-options`, **không** có `server:`; `Host: evil.example:7799` → 421; POST estop không danh tính → 403; `lsof` chỉ thấy `127.0.0.1:7799`. Mở trang trong trình duyệt (Công việc, Phê duyệt, Dự án): console không có log nào, sự kiện `securitypolicyviolation` = 0, stylesheet nạp, SSE nối được (không hiện "Mất kết nối").
- File nguồn dài nhất: `tram/su_kien/kho.py` 118, `tram/cli.py` 115, `tram/bao_tin/vong.py` 102, `tram/beads/bd.py` 98, `tram/chu/cai_dat.py` 97; `.vue` dài nhất `CongViec.vue` 85.

**5. Đối chiếu review Fable (bản 850646a) — đã làm:** C1 (`.vue` + plugin-vue, CSP — Task 10/12/23–26), C2 (`KhongThayBead` dời sang Task 1, `BdGia.mot` ném nó, ca 404 `hr-99`), Q1 (Host 421 — G17), Q2 (`hien_tren_bang` trong Duyệt / Trả về / Trả lời), Q3 (`tra_lai` — G11), Q4 (`tra_loi_decision`, mục `decision`, `tra_loi_duoc`, `OTraLoi`), Q5 (G5/G7/G9 ghi "Đại ca đồng ý 13/10"), N1 (`laLinkAnToan` chỉ GitHub — G23), N2 (`setData` khi kéo), N3 (cảnh báo + `kickstart` ở `cai_dat` và Task 26 bước 5), N4 (docstring `chay_thao_tac`), N5 (`close` + `closing` — G24), N6 (đo thời gian Chốt — Task 26 D3), N7 (bảng số test, Expected Task 23–25), N8 (ghi chú `bd.json` là DB nháp — Task 26 D1), N9 (`server_header=False`).

Số test: 239 → đợt 1 +38 (277) → đợt 2 +46 (323) → đợt 3 +59 (382) → T12 +8 (390) → T17 +6, T22 +6 (402) → T18 +6 (408). Frontend: 7 test `node --test` + `vite build`.

## Ghi chú triển khai

(Người thực thi điền sau Task 26: chỗ mã khác plan và lý do, kết quả D1–D6, câu trả lời G17, góp ý giao diện của Đại ca.)

## Ghi chú triển khai 13/10/2026 (Task 1–25, nhánh feat/lat-2a-dashboard)

Cách chạy: mỗi task một worktree riêng tạo từ nhánh chính sau khi ghép đợt trước; Sonnet 5.5 cho task `de`, Opus 5.5 effort high cho task `kho`; Em QC từng task (mọi dòng thêm có nguyên văn trong plan — trừ `pyproject.toml`, `uv.lock`, `package.json`, `package-lock.json` do công cụ sinh — và số test đúng kỳ vọng) rồi merge `--no-ff`. Fable review plan một lần (Đại ca chốt bỏ vòng 2).

| Task | Khác plan | Vì sao |
|---|---|---|
| 1–25 | Không về mã | Kiểm tự động từng dòng thêm |
| 7 | Chạy sau khi ghép Task 1 | Test cần `tests/bead_gia.py` của Task 1; plan giả định một worktree chung |
| 22 | `tram/cli.py` 116 dòng (plan ghi 115) | Mọi dòng có trong plan; vẫn ≤ 120 |
| Sửa gộp (nhánh `2a/sua`) | 5 sửa ngoài plan, mỗi sửa một commit có test | Lỗi do subagent phát hiện khi tự soát: `pr` có ký tự điều khiển Unicode không hiện link (bs-6o0.9); 500 bất ngờ vẫn mang CSP/header an toàn (bs-6o0.10); giờ yên lặng đầu = cuối là khoảng rỗng (bs-6o0.5); `gui_telegram` bắt `http.client.HTTPException` (bs-6o0.7); kéo cột lưu `nhan_dau` để kết quả đúng sau crash, thử lại chặn epic/bead đóng/hoãn (bs-6o0.8) |

- Số test: đợt 1 → 277, đợt 2 → 323, đợt 3 → 382, đợt 4 → 390, đợt 5 → 402, đợt 6 → 408, sửa gộp → **418 passed**. Frontend: `node --test` 7/7, `kiem-an-toan` 18 file sạch, `vite build` xanh, không có `new Function`.
- Phiên bản đã ghim: `fastapi==0.143.0`, `uvicorn==0.54.0`; `vue@3.5.43`, `vue-router@5.4.0`, `vite@8.3.4`, `@vitejs/plugin-vue@6.0.10`.
- Còn mở: Task 26 (chạy thật trên máy B — Tailscale, Telegram, D1–D6) chờ #5; bs-6o0.6 (chặn kéo bead decision mở) chờ Đại ca; khoá liên tiến trình cho `chay_thao_tac` chỉ cần nếu sau này có tiến trình thứ hai gọi nó (tram-api hiện một worker).
