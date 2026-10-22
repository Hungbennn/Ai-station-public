# Phần 4 — Bộ giao việc

Status: `ĐÃ DUYỆT` — Đại ca duyệt trên chat 13/10/2026 sau review độc lập lần hai của Codex (cùng plan 4a-1; đồng ý toàn bộ đề xuất hợp đồng — xem [phản hồi review Codex đợt 1+2](../handovers/2026-10-13-phan-hoi-review-codex-dot12.md)). Trước đó: Em viết đêm 13/10/2026; ba vòng review Fable, một vòng review Codex; Đại ca trả lời câu hỏi 13/10 — §15. Cổng chạy thật (#5, S6, S7) vẫn chờ
Ngày: 2026-10-13 (sửa lần 2 cùng ngày: [quyết định 13/10](../quyet-dinh/2026-10-13-tra-loi-cau-hoi-gop.md) và [phản hồi review Codex](../handovers/2026-10-13-phan-hoi-review-codex.md))
Kiến trúc tổng: [2026-10-12-tram-dieu-phoi-kien-truc.md](2026-10-12-tram-dieu-phoi-kien-truc.md) (Q6, Q7, Q11, Q14, §3, §5.1, §5.2, §5.3, §5.5, §5.7)
Dựa trên: [phần 0+1a](2026-10-12-phan-0-1a-cham-cot.md) (nhãn cột, schema bàn giao, luật `chinh-thuc` chặt) · [phần 2](2026-10-12-phan-2-dashboard.md) (Phê duyệt, §12) · [phần 3](2026-10-13-phan-3-may-tho-han-muc.md) (khe, phiếu, kho phiếu bền, thẻ chắn `luot`, công bố ref, cách ly, hạn mức) · [phần 1b](2026-10-13-phan-1b-memory.md) (lớp 5) · [spike bd](../spikes/2026-10-13-bd-cli.md)

Thuật ngữ theo phần 3: **`luot`** = thẻ chắn theo bead; **lần chạy** (`lan`) = một lần gọi CLI trong một phiếu; **phiếu hiệu lực** = định nghĩa duy nhất của phần 3; **SHA công bố** = commit trạm đã chấp nhận trên ref công bố (phần 3 §6.4). Cách đọc: quyết định đã chốt ghi `#`; "đề xuất" là chưa chốt; mọi mô tả là hành vi sẽ triển khai.

## 1. Mục tiêu

Bead ở cột 1 tự đi từ "AI tự làm" tới "chờ Đại ca review" mà Đại ca **không phải ngồi canh**, chỉ dừng ở bốn điểm dừng (Q6); feature đi từ phiếu yêu cầu tới spec chờ duyệt rồi thành các bead việc.

Phần 4 quyết **giao gì, cho khe nào, bước nào, kèm ngữ cảnh gì**, và **khi nào một bead được sang cột 3**. Cách chạy một bước là việc của phần 3.

**Một ngày của bead `hr-6xe1`** (bug "cắt UTF-8 tóm tắt hoàn tiền", bộ quét 1a xếp cột 1):
1. `B/claude-1` (ưu tiên coder) rảnh, nhịp tim xin việc → trạm chọn `hr-6xe1`, cấp phiếu `code` (`luot` 1) trong một giao dịch.
2. claude-1 sửa, viết test, `tram bao --xong` → thợ chạy lệnh bắt buộc, push ref tạm → trạm công bố `tram/hr-6xe1` = SHA `c1`.
3. Trạm kiểm lại **mọi lệnh bắt buộc** tại `c1` trong môi trường cách ly → đạt.
4. `B/claude-2` (khe khác — Q14) nhận phiếu `qc` (`luot` 2) từ `c1` → trả về: "thiếu test tên kết thúc bằng 'ỷ'".
5. claude-1 nhận lại `code` (`luot` 3) → `c2` → kiểm lại đạt → claude-2 QC (`luot` 4) → công bố `c3` và đạt; trạm xác minh `c3` chỉ thêm file bàn giao so với `c2`.
6. Bead sang cột3 với bằng chứng `(commit_code=c2, commit_ban_giao=c3)`; ref công bố bằng `c3`. Telegram báo Đại ca; Đại ca tạo/merge PR tại `c3`, bấm Duyệt.

## 2. Tiêu chí thành công

Con số là mặc định đã giữ 13/10 (#21), cấu hình được.

| # | Tiêu chí | Ngưỡng |
|---|---|---|
| G1 | Bead vào cột 3 mà một **lệnh bắt buộc** không pass khi trạm chạy lại, hoặc một tiêu chí bắt buộc không `dat` | **0** |
| G2 | Bước QC do chính khe đã code bead đó làm | **0** |
| G3 | Phiếu giao cho bead không đủ điều kiện §5.1 | **0** |
| G4 | Lệnh kiểm không khớp `lenh_cho_phep` được chạy, hoặc chạy qua shell, hoặc chạy dưới quyền của tram-api | **0** |
| G5 | Bead hết ngân sách hoặc agent báo "bí" → có escalation ở cột 2 | ≤ 3 phút, 100% |
| G6 | Feature có phiếu hợp lệ → spec + plan trên nhánh, ở "Spec chờ duyệt", không cần Đại ca giữa chừng | chạy đúng trên bead thử |
| G7 | Sau khi Đại ca duyệt spec: bead đề xuất được tạo đúng phụ thuộc, cha, nhãn, không trùng khi duyệt lại hoặc crash giữa chừng | 100% trên bead thử |
| G8 | Một bug rõ ràng đi từ cột 1 tới cột 3 không có Đại ca | chạy đúng trên repo nháp 3 bug (#4) |
| G9 | Diff chạm file cấu hình agent (`duong_dan_cam`) vào cột 3 | **0** |
| G10 | QC đổi mã thực thi mà vẫn được công nhận; bằng chứng cột 3 gắn commit khác commit đang ở ref công bố | **0** |
| G11 | Duyệt spec tạo bead từ bản khác bản Đại ca đang xem | **0** |

## 3. Lát

| Lát | Nội dung | Chạy được khi |
|---|---|---|
| **4a** | Pipeline bug/task/chore/spike: chọn bead → code → kiểm lại → QC chéo → cột 3; gói ngữ cảnh lớp 1–4; escalation; ngân sách; vòng tick; bằng chứng gắn commit | phần 3a (gồm cách ly và GitHub, #2, #3); phần 2a có nút Trả lời escalation (#11); chạy thử trên **repo nháp 3 bug** trước HR Codex (#4) |
| **4b** | Luồng feature: phiếu yêu cầu, bước spec, Spec chờ duyệt theo commit, tạo bead từ plan có đối soát; skill "xem spec chờ duyệt" trên máy A (chỉ đọc) | 4a + phần 2a (Phê duyệt) |
| **4c** | Tự mở PR trên GitHub và tự xác minh đã merge; cờ đỏ theo `detect_changes` của gitnexus; lớp 5 từ memory (gọi HTTP recall khi 1b-1 sẵn sàng) | 4b; 1b-1 |

GitHub có từ 3a (#2). Trước 4c, PR do **Đại ca tạo và merge tay** từ ref công bố tại SHA trạm ghi trong bằng chứng; trạm chỉ hiện link và lệnh. Không coi `pr` null là bằng chứng đã merge. Bảo vệ nhánh chính bật từ 3a, không đợi 4c.

## 4. Pipeline theo loại bead

| Loại bead | Bước | Ghi chú |
|---|---|---|
| `bug`, `task`, `chore` | `code` → *kiểm lại* → `qc` → cột 3 | QC trả về → `code` lại với góp ý QC |
| `spike` | `code` (vai coder, kết quả là file `docs/spikes/…`) → *kiểm tài liệu* → cột 3 | không qua cổng lệnh kiểm, không QC; vẫn qua kiểm đường dẫn cấm, bàn giao, SHA (§6.2); G1 không áp dụng |
| `feature` có nhãn `can-spec` | `spec` → nhãn `cho-duyet-spec` | điểm dừng #1; §7 |
| `feature` không có nhãn luồng; `feature` có `theo-plan`; `epic`, `decision`, `story`, `milestone` | **không giao** | feature muốn chạy phải có `can-spec`; decision luôn ở cột 2 (luật cứng 1a) |

*Kiểm lại* không phải bước của khe: trạm điều phối một lần chạy lệnh trong môi trường thực thi cách ly (§6.2).

## 5. Chọn việc và chọn khe

### 5.1 Bead đủ điều kiện (luật cứng, chạy trước mọi thứ — G3)

**Giao `code` lần đầu** khi đủ cả:

1. Có đúng một nhãn cột và đó là `cot:ai-lam`; không có `cot:cho-review`, `can-spec`, `cho-duyet-spec`, `theo-plan`. Bead đang mang nhiều nhãn cột trái nhau → không giao, hiện "nhãn lệch" (#8).
2. `status = open` và nằm trong `bd ready --json --limit 0` của dự án (không bị chặn). (`bd ready` loại `in_progress` — điều này chưa có trong spike bd, plan kiểm — nên điều kiện này chỉ dùng cho lần đầu; phụ thuộc `parent-child` không chặn — spike bd.)
3. `issue_type` ∈ {`bug`, `task`, `chore`, `spike`}.
4. `acceptance_criteria` sau khi tách dòng và chuẩn hoá **không rỗng** (tiêu chí là thứ cổng hoàn thành đối chiếu — spec 0+1a §4.3). Readiness của 1a có thể đọc tiêu chí từ mô tả; khi đó bead vẫn ở cột 1 nhưng **không giao** cho tới khi tiêu chí được chép vào `acceptance_criteria` — dashboard hiện "thiếu tiêu chí máy đọc được".

**Giao các bước sau** (`qc`, `code` lại sau QC/kiểm lại/trả về/thu hồi, kiểm tài liệu của spike) khi đủ cả:

1. `status = in_progress`, `assignee = tram/giao-viec`; nhãn cột duy nhất là `cot:ai-lam`.
2. **Không bị chặn**: không có phụ thuộc loại `blocks` tới bead chưa đóng **hoặc không có trong snapshot** (fail-closed) — cùng logic tính "bị chặn" của luật cứng 1a, tách thành hàm công khai ở `tram/cham_cot/luat_cung.py`.

**Chung cho mọi bước:**

5. Bead không có phiếu hiệu lực (`phieu_hieu_luc` của phần 3).
6. `du_mot_phieu(bead, buoc)` đúng (§8) — giữ trước ngân sách bằng bản ghi bền trong giao dịch cấp phiếu.
7. Không có phiếu hiệu lực mang cùng `khoa_chong_trung` = `sha256(du_an, cha, bead_id, buoc, phien_ban_vai, phien_ban_quyen)` (phần 4 tính, phần 3 giữ sổ và từ chối).
8. Con của feature (`parent` có nhãn `theo-plan`): commit spec đã duyệt (ghi trong `spec.duyet`) là tổ tiên của `origin/<nhanh_chinh>` (`git merge-base --is-ancestor`). Chưa merge → không giao; dashboard hiện "chờ merge spec".
9. Phiếu chạy mã dự án (`code` của bug/task/chore, `qc`): dự án có khoá `moi_truong_kiem` (thiếu → không phát phiếu, vòng tick tạo tối đa một escalation `thieu-moi-truong-kiem` đang mở mỗi dự án (gắn bead đủ điều kiện đầu tiên); đóng mà vẫn thiếu thì tạo lại; thợ chặn lần nữa — phần 3 §7.1). Phiếu spike tài liệu và `spec` không cần.

**Phiếu code bug/task/chore:** danh sách lệnh bắt buộc phải khác rỗng. `design` chỉ lấy từng dòng sau bỏ đầu dòng hoặc nội dung giữa backtick, giữ lệnh khớp allowlist; không khớp thì không chạy.

**Bead feature** được giao bước `spec` khi có `can-spec`, phiếu yêu cầu hợp lệ (§7.1), `status = open`, **không bị chặn** (nằm trong `bd ready` — escalation chặn feature thì không giao lại), và điều kiện 5, 6, 7.

Cấp phiếu theo hợp đồng 3a-1 G11: `BoGiaoViec.chon(khe_id, han_muc)` đọc Beads/Git và chọn ngoài giao dịch; `con_hop_le(de_xuat)` chạy bên trong giao dịch cấp phiếu, chỉ đọc kho bền để kiểm công việc tồn, câu hỏi chưa chuyển escalation, escalation mở và ngân sách. Phần 3 kiểm phiếu hiệu lực, khe, hạn mức, khoá chống trùng và giữ trước ngân sách trong cùng giao dịch. Không gọi Beads/Git/HTTP khi giữ khoá SQLite.

**Giới hạn nhất quán đã được Đại ca chấp nhận13/10 (4a-1 G3):** nhãn, `bd ready`, tiêu chí, cấu hình và trạng thái Beads là snapshot ngoài giao dịch; không có giao dịch nguyên tử xuyên Beads/SQLite, cũng không có bằng chứng giới hạn cửa sổ đua dưới một giây. 4a-2 đọc lại Beads ngay trước cấp, huỷ khi version/nội dung đổi và có test thao tác kéo cột xen kẽ. Thay đổi sau lần đọc cuối vẫn là rủi ro còn lại đã được Đại ca chấp nhận (handover đợt1+2); không gọi đó là hành vi của “phiếu đã cấp”. Bộ chấm 1a bỏ qua bead có phiếu hiệu lực (#10), nên bead không bị 1a lật cột giữa phiếu. Nếu **Đại ca** đổi cột trong lúc phiếu chạy (kéo sang cột 2), phiếu hiện tại chạy nốt, không giao bước sau.

### 5.2 Thứ tự

Khi một khe rảnh xin việc qua nhịp tim (phần 3 §6.2), trạm duyệt bead đủ điều kiện của **mọi dự án**, sắp theo: (1) bead dở (đã có phiếu kết thúc không phải `xong`, chờ giao lại) trước; (2) bước `qc` trước `code`; (3) ưu tiên P0 → P4; (4) `created_at` cũ trước; (5) `id`. Chọn bead đầu tiên mà khe nhận được theo §5.3.

### 5.3 Khe nào nhận bước nào

Cho khe X đang xin việc và bead B, bước S, vai V(S):

1. **Hạn mức:** `duoc_nhan(han_muc_X, uu_tien_B)` (phần 3 §8.2) phải đúng.
2. **Q14 (luật cứng):** `S = qc` mà X đã chạy bất kỳ phiếu `code` nào của B (tra `giao.nhan`) → X không nhận B. Không có khe hợp lệ khác → B chờ, không hạ chuẩn. Hai khe cùng model Claude được chấp nhận (#17).
3. **Tập khe hợp lệ của (B, S)** = các khe đang bật, cầu dao đóng, `duoc_nhan` đúng, **và** không bị luật 2 cấm với B — lấy từ `trang_thai_khe()` của phần 3 §10.1.
4. **Vai ưu tiên:** nếu V(S) có trong `vai_uu_tien` của X → X nhận. Nếu không: X chỉ nhận khi **không** khe nào trong tập hợp lệ của (B, S) vừa có V(S) trong `vai_uu_tien` vừa đang `ranh` hoặc `lam` — để vai lan sang khe khác (kiến trúc §4.1).
5. **Ưu tiên khe đã code** (cho `code` lại): nếu khe Y ≠ X đã code B, Y thuộc tập hợp lệ và đang `ranh` → X bỏ qua B ở lần xin này. Y không rảnh → X nhận.

### 5.4 Ghi lên beads

Trạm là bên duy nhất ghi beads (Q11), `--actor tram/giao-viec`. Mọi lần ghi có **ID thao tác bền** và đối soát sau sự cố (phần 3 §6.6).

- Giao `code` lần đầu: `bd update <id> --claim` (status → `in_progress`, assignee = `tram/giao-viec`) ngoài giao dịch, ngay trước trả đề xuất. Lỗi/không rõ kết quả → đọc lại: chỉ nhận trạng thái đích đúng assignee của trạm; người khác nhận thì bỏ. Cấp phiếu thất bại sau claim → lần xin sau nhận tiếp bead đang `in_progress`, không claim lại. `--claim` không thay khoá của trạm; khoá thật là giao dịch cấp phiếu. Không khẳng định claim và cấp là một giao dịch.
- **Không bao giờ gắn** `cot:ai-lam` / `cot:can-chot` — gắn `cot:can-chot` sẽ bị 1a hiểu là Đại ca kéo tay và khoá.
- Vào cột 3: gỡ **mọi** nhãn `cot:*` hiện có rồi gắn duy nhất `cot:cho-review` (#8).
- Đưa bead về cột 2 bằng **escalation** (§9), không bằng nhãn cột.

## 6. Một bead bug/task/chore/spike từ cột 1 tới cột 3

### 6.1 Bước `code`

Phiếu (phần 3 §6.1): `vai = coder`, `buoc = code`, `repo.nhanh = tram/<bead>`, `cha` = `origin/<nhanh_chinh>` (lần đầu) hoặc snapshot (giao lại) hoặc SHA công bố mới nhất của `tram/<bead>` (code lại). Phần 4 điền:

- `lenh_kiem` = **lệnh bắt buộc**: `lenh_kiem_mac_dinh` của `du-an/<ten>.yaml` cộng lệnh nêu trong `design` của bead nếu khớp `lenh_cho_phep`. Lưu trong phiếu; trạm kiểm lại **chính danh sách này**, không suy từ lời báo của agent/thợ;
- `tieu_chi[]` = `acceptance_criteria` tách dòng, chuẩn hoá (bỏ khoảng trắng đầu cuối, bỏ đầu dòng `- `, `* `, `1.`, gộp khoảng trắng, bỏ dòng rỗng); lưu kèm `digest_tieu_chi` = sha256 của danh sách;
- `ngan_sach` theo §8;
- `can_lenh_kiem` = `true` cho `code` của bug/task/chore; `false` cho spike, `qc`, `spec`. `can_moi_truong_kiem` = `true` cho `code` của bug/task/chore và `qc`; `false` cho spike tài liệu và `spec`. `tieu_chi[]` của phiếu `qc` = của bead; của phiếu `spec` = `nghiem_thu_so_bo` của phiếu yêu cầu.
- `lenh_cho_phep` = của `du-an/<ten>.yaml` cho phiếu `code` của bug/task/chore và phiếu `qc`; **rỗng** cho spike và `spec`. Ở 4a mọi spike là **spike tài liệu**: `lenh_kiem = []`, `lenh_cho_phep = []`, không có môi trường kiểm. File quyền theo vai nạp `lenh_cho_phep` **của phiếu**, không của dự án (phần 3 §7.2). Quyền CLI chỉ là lớp bổ sung; lớp thật là principal thực thi không credential và không có `.env` kiểm (phần 3 §7.3). Spike cần chạy mã dự án chưa được hỗ trợ: agent báo `tram bao --bi "spike-can-chay-ma: …"` → ánh xạ `bao.bi {ly_do: "agent"}` như §9.

Thợ báo `bao.xong` kèm bàn giao `chinh-thuc` đã có kết quả lệnh kiểm thật (phần 3 §7.5). Trạm xử lý (công việc bền, phần 3 §6.6): **§6.2 bước 0 trước**; không chạm thì kiểm bàn giao bằng luật `chinh-thuc` chặt của spec 0+1a §4.3 với `tieu_chi[]` và `can_lenh_kiem` của phiếu; `commit` phải là SHA trạm đã công bố cho lượt này. Không hợp lệ → `code` lại với lỗi ở lớp 4 nếu ngân sách còn, hết thì escalation.

### 6.2 Kiểm lại (trạm điều phối — "báo xong" khác "đã kiểm chứng", kiến trúc §5.2)

Kiểm lại luôn gắn **một commit** = SHA công bố của lượt vừa báo xong (§6.7).

0. **Đường dẫn cấm — kiểm trước tiên**, trước khi chạy bất cứ lệnh nào (lệnh kiểm như `npm run test:unit` chạy chính `scripts` agent có thể vừa sửa).
   - Diff tính từ gốc nhánh: `git diff --name-status -z --find-renames $(git merge-base origin/<nhanh_chinh> <commit>)..<commit>` — đọc tách bằng NUL, xét **cả tên cũ và tên mới** của rename; không tính từ `cha` của phiếu (với `code` lại, `cha` là đầu nhánh nên diff sẽ rỗng).
   - Đường dẫn chuẩn hoá: tương đối POSIX từ gốc repo. Mẫu khớp **ở mọi cấp thư mục** theo ngữ nghĩa glob có test (vd `**/package.json` khớp cả `erp/package.json`).
   - Danh sách tối thiểu của trạm: `**/.claude/**`, `**/.mcp.json`, `**/CLAUDE.md`, `**/AGENTS.md`, `.github/workflows/**`, `**/.tram/**`, `**/composer.json`, `**/package.json`, `**/phpunit.xml*`, `**/vitest.config.*`, `**/jest.config.*`, `**/.git/**`, `.gitmodules`. Dự án **thêm** được (`duong_dan_cam`); ngoại lệ chỉ ghi được **từng đường dẫn cụ thể** trong `duong_dan_cam_cho_phep` (Đại ca sửa tay), không dùng glob gỡ cả nhóm.
   - Chạm → không chạy lệnh, không QC, escalation `dong-file-cau-hinh` (G9). Đại ca trả lời "hoàn tác" (bước kế là `code`, agent bỏ thay đổi ở các file đó) hoặc thêm ngoại lệ cụ thể rồi trả lời "cho phép". Mọi câu trả lời đều dẫn tới lượt `code` mới; không phân tích văn bản trả lời để cấp quyền hoặc tự chạy lại lệnh. Bead thêm thư viện (đổi `package.json`/`composer.json`) luôn qua escalation ở 4a — chấp nhận.
   - `duong_dan_cam` bảo vệ **chỉ dẫn** cho lượt sau; mã test do agent viết vẫn là mã không tin cậy — bảo vệ máy là việc của cách ly (phần 3 §7.3). Thợ (phần 3 §7.5) cũng chạy bước này bằng cùng hàm.
1. Kho kiểm riêng `~/.tram/kho-kiem/<du_an>` do tài khoản trạm giữ; không fetch vào repo làm việc của Đại ca. Clone/credential/trao quyền là việc của 4a-2 sau S6/S7. Trạm `git fetch origin` (hook Git tắt) vào kho kiểm của trạm, xoá worktree kiểm cũ, rồi `git worktree add --detach <thư mục kiểm>/<giao_id> <commit>`. Worktree kiểm do tài khoản trạm tạo, chép môi trường kiểm vào (bước 3), rồi mới trao quyền ghi cho **principal kiểm lại `tram-kiem`** (phần 3 §7.3 mục 5); sau đó tài khoản trạm chỉ đọc log và mã thoát.
2. **Spike:** dừng ở đây — kiểm bàn giao (file thường dưới `docs/handovers/`, đối chiếu tiêu chí), không chạy lệnh → `kiem.lai {giao_id, bead_id, luot, commit, digest_tieu_chi, dat}` (cùng trường như bước 5, để §6.6 so được).
3. Chép **môi trường kiểm** `moi_truong_kiem` (Đại ca đặt tay, trỏ DB test) vào worktree; đích không thoát worktree qua symlink. Thiếu khoá → escalation `thieu-moi-truong-kiem` (không bao giờ chạy với `.env` có thể trỏ DB thật — điểm dừng #4).
4. Chạy **mọi lệnh bắt buộc của phiếu** (`lenh_kiem`), mỗi lệnh khớp `lenh_cho_phep` bằng hàm chung `khop_lenh(lenh, mau) -> list[str] | None` (`tram/cau_hinh/lenh.py`): `shlex.split` cả lệnh và mẫu; `*` thay **đúng một token**, token không chứa `; & | < > $ \` ` hay xuống dòng, không bắt đầu bằng `-`, không là đường dẫn tuyệt đối, không chứa `..`; số token bằng nhau. Mỗi nhóm lệnh trong allowlist phải giới hạn cả tham số có ý nghĩa thực thi (vd `--filter *` chỉ nhận tên lọc, không nhận `--bootstrap`), không chỉ ký tự shell. Chạy bằng `subprocess.run(argv)` **không qua shell**, dưới **principal kiểm lại `tram-kiem`** (phần 3 §7.3 mục 5) — không bao giờ dưới quyền tram-api — `APP_ENV=testing`, hook tắt, giới hạn 15 phút mỗi lệnh, kill cả nhóm tiến trình khi quá hạn.
5. **Đạt khi và chỉ khi:** mọi lệnh bắt buộc chạy được và pass; lệnh bắt buộc không khớp allowlist, lỗi khởi chạy, timeout → **không đạt**. Lệnh agent đề xuất thêm không thay được lệnh bắt buộc. Sự kiện `kiem.lai {giao_id, bead_id, luot, commit, digest_tieu_chi, dat, ket_qua[], digest_log[]}` (memory 1b nạp bàn giao khi `dat = true`).
6. Không đạt → `code` lại với kết quả kiểm lại ở lớp 4.

### 6.3 Bước `qc`

Phiếu `vai = qc`, `buoc = qc`, `cha` = **commit code đã kiểm lại đạt** (`commit_code`), cho khe hợp lệ khác (§5.3). Lớp 4 có bàn giao của bước `code` + kết quả kiểm lại + `git diff <cha-ban-đầu>..<commit_code>`. QC **không sửa mã**; kết quả là file bàn giao có khối JSON giữa hai dấu `<!-- qc -->`:

```json
{"qc": {"ket_luan": "dat" | "tra_ve", "commit_code": "c2…", "phat_hien": [{"muc": "chan|quan-trong|nho", "noi_dung": "…", "vi_tri": "file:dòng"}]}}
```

Sau `bao.xong` của phiếu `qc`, trạm:

1. lấy `commit_qc` = SHA công bố của lượt QC; kiểm **diff `commit_code..commit_qc` chỉ gồm file trong `docs/handovers/**`** — có đổi bất kỳ file nào khác → **không công nhận QC** (G10), escalation `qc-doi-ma`;
2. đọc khối QC bằng `git show <commit_qc>:<file_ban_giao>`; thiếu, lỗi, hoặc `commit_code` trong khối khác `commit_code` của phiếu → coi như `tra_ve` với lý do "khối QC lỗi";
3. `ban_giao.commit` phải bằng SHA công bố `commit_qc`; khác thì `ban-giao-qc-loi` và `tra_ve`. Kiểm bàn giao của phiếu `qc` bằng luật `chinh-thuc` bản QC (spec 0+1a §4.3): mỗi tiêu chí đúng một dòng đối chiếu có bằng chứng; `dat: false` được phép khi `ket_luan = tra_ve`. `loi_ban_giao` do thợ gửi (thợ đã áp bản QC ở phần 3 §7.5 bước 4, nên chỉ còn lỗi thiếu/trùng đối chiếu, sai cấu trúc), hoặc `ket_luan = dat` mà có tiêu chí `dat: false` → coi như `tra_ve` với lý do "bàn giao QC lỗi", giống bước 2;
4. ghi `qc.ket_qua {giao_id, bead_id, commit_code, commit_qc, ket_luan, phat_hien[], ly_do}`. `ket_luan` gồm `dat`, `tra_ve`, `khong_cong_nhan`; giá trị cuối dành cho `qc-doi-ma`. Chưa có SHA công bố hoặc `bao.xong.commit` không khớp → không ghi `qc.ket_qua`, giao QC lại nếu còn ngân sách, không tính là vòng trả về.

- `dat` → §6.4.
- `tra_ve` → `code` lại, phát hiện của QC vào lớp 4.

### 6.4 Vào cột 3

1. **Bộ bằng chứng** `(du_an, bead_id, giao_id_code, luot_code, commit_code, commit_ban_giao, digest_tieu_chi)` — `commit_ban_giao` là `commit_qc` (bug/task/chore) hoặc commit của spike. Trạm xác minh cả hai commit thuộc ref công bố của bead và ref công bố hiện tại **đúng bằng** `commit_ban_giao`.
2. `bd update` (ID thao tác bền): gỡ mọi `cot:*`, gắn `cot:cho-review`, `--append-notes` hai khối riêng: `<!-- ban-giao -->{khối bàn giao code nguyên schema}<!-- ban-giao -->` và `<!-- bang-chung -->{bộ bằng chứng, ma_thao_tac}<!-- bang-chung -->`. Không nhét trường bằng chứng vào schema `BanGiao` đang `extra=forbid`.
3. **Cờ đỏ:** diff từ gốc nhánh (§6.2 bước 0) khớp `duong_dan` của bất kỳ `hang_rao` nào → gắn `co-do`. 4c thêm `detect_changes` của gitnexus.
4. **PR:** trước 4c, dashboard hiện lệnh/link để Đại ca tạo PR từ `tram/<bead>` tại `commit_ban_giao`; 4c trạm tự mở PR bằng `gh` và điền `pr`. PR phải trỏ đúng commit cuối đã xác minh.
5. Sự kiện `bead.vao_cot_3 {bead_id, commit_code, commit_ban_giao, digest_tieu_chi, co_do, pr}`; phần 2 báo Telegram.

### 6.5 Sau cột 3 (Đại ca, qua dashboard phần 2)

- **Duyệt** → `bd close` (phần 2). Ở 2a/4a/4b, xác nhận "đã merge" là **thao tác của Đại ca**, không phải bằng chứng máy. Từ 4c, trạm chỉ tự đóng khi xác minh được PR đúng repo/nhánh đã merge **đúng `commit_ban_giao`** (phạm vi hậu duệ chỉ thêm commit merge cần chứng minh nội dung riêng; đề xuất 4c G6 hiện chỉ tự xác minh head đúng SHA đã kiểm, xem §19.7). Vòng tick thấy bead đóng → `bead.dong`; thợ dọn worktree.
- **Trả về + góp ý** → phần 2 gỡ mọi `cot:*` và `cot-khoa`, ghi `cot.tra_ve`. Bộ quét 1a chấm lại; về cột 1 thì phần 4 giao `code` lại với góp ý ở lớp 4, `cha` = SHA công bố mới nhất. Trả về **không tái dùng** kết quả kiểm lại hay QC của vòng trước. `cot.tra_ve` mở chu kỳ ngân sách mới (§8).

### 6.6 Bước kế tiếp — `buoc_ke_tiep(bead, su_kien) -> code | kiem_lai | qc | cot_3 | cho`

Tính lúc đọc (Q12) từ sự kiện của bead kể từ `cot.tra_ve` gần nhất (hoặc lần giao đầu) — **không** cắt ở `escalation.dong`; chu kỳ của §8 chỉ dùng đếm ngân sách. Xét theo thứ tự, gặp dòng khớp thì dừng:

| # | Điều kiện | Kết quả |
|---|---|---|
| 1 | có phiếu hiệu lực, hoặc escalation mở chặn bead, hoặc có công việc chờ xử lý chưa xong, hoặc `bao.can_hoi` chưa có `escalation.tao` theo đúng ID nguồn | `cho` |
| 2 | bead có `cot:cho-review` | `cho` (Đại ca xử lý) |
| 3 | `qc.ket_qua` mới nhất sau lần kiểm lại của phiếu code mới nhất là `dat`, phiếu code đó đã xong hợp lệ, `commit_code` của QC = `commit` của kiểm lại đó, ref công bố = `commit_qc`, và `digest_tieu_chi` của `kiem.lai` đó = digest tiêu chí hiện tại của bead | `cot_3` |
| 4 | `kiem.lai` của đúng `giao_id` và `luot` phiếu code mới nhất đã xong hợp lệ là `dat`, `commit` = SHA công bố của phiếu đó, `digest_tieu_chi` = digest tiêu chí hiện tại của bead, chưa có `qc.ket_qua` sau lần kiểm lại đó | `qc` (spike: `cot_3`) |
| 5 | `bao.xong` của phiếu code mới nhất hợp lệ, chưa có `kiem.lai` cho đúng `giao_id` + `luot` của nó (cùng SHA ở lượt cũ không được tái dùng) | `kiem_lai` |
| 6 | còn lại: chưa có phiếu nào; `qc.ket_qua` mới nhất `tra_ve` hoặc không công nhận; `kiem.lai` mới nhất không đạt; `bao.xong` không hợp lệ hoặc chạm `duong_dan_cam` (sau khi Đại ca trả lời "hoàn tác"); phiếu cuối kết thúc `bi`/`het_han_muc`/`thu_hoi`; `cot.tra_ve`; ref công bố đổi sau lần kiểm/QC cuối, hoặc tiêu chí hiện tại của bead khác `digest_tieu_chi` của `kiem.lai` mới nhất (bằng chứng hết hiệu lực — trở về dòng 5 nếu có `bao.xong` mới, nếu không thì `code`) | `code` (từ snapshot hoặc SHA công bố mới nhất) |

Escalation đóng không tự đưa bead về `code`: bead rơi xuống dòng 3–5 để làm tiếp đúng chỗ (vd `thieu-moi-truong-kiem` đóng → dòng 5 → chạy lại kiểm lại).

**Với feature:** `cho-duyet-spec`, phiếu hiệu lực, hoặc bị chặn → `cho`; `theo-plan` → không giao; có `can-spec` + phiếu yêu cầu hợp lệ → `spec`.

"Mới nhất" so theo thứ tự ghi sự kiện, trong phạm vi đúng lượt code. Khi ghi cột 3, kiểm lại digest tiêu chí của bead đầu vào, phiếu code mới nhất xong hợp lệ, lần kiểm không phải kết quả pass cũ trước một lần fail. Cùng SHA không đồng nghĩa cùng phiếu hoặc cùng chứng cứ. Hàm có test cho từng dòng (§16).

### 6.7 Bằng chứng gắn commit (tổng hợp — điểm dừng #2 của Q6)

- Cổng bằng chứng không lấy kết quả pass lịch sử nếu lượt code mới hơn lỗi hoặc chưa kiểm; QC phải sau lần kiểm của lượt đang xét.
- Mọi kiểm lại, QC, vào cột 3, phê duyệt gắn với `(du_an, bead_id, giao_id, luot, commit_code, commit_ban_giao, digest_tieu_chi)`.
- Trạm tự xác minh commit thuộc ref đã nhận của phiếu (phần 3 §6.4); không suy từ HEAD remote đang di động.
- Ref công bố đổi, hoặc `acceptance_criteria` đổi (`digest_tieu_chi` khác) sau khi kiểm → bằng chứng **hết hiệu lực**; bead phải kiểm lại.
- Đây là chốt Q6 vào nội dung cụ thể; không thay quyền Đại ca merge (Q7).

## 7. Luồng feature (thực hiện §5.7 kiến trúc)

### 7.1 Phiếu yêu cầu

Khối máy đọc được trong **mô tả** bead feature, giữa hai dấu `<!-- phieu-yeu-cau -->`:

```json
{
  "phien_ban": 1,
  "muc_tieu": "Sale xem được hoa hồng tạm tính ngay trên booking",
  "nghiep_vu_da_chot": ["Hoa hồng tính trên giá sau giảm giá (ADR-0083)"],
  "pham_vi": "Màn chi tiết booking (Book) + API đọc hoa hồng (Comp)",
  "khong_lam": ["Không sửa công thức hoa hồng"],
  "nghiem_thu_so_bo": ["Booking có giảm giá hiện đúng số tạm tính"],
  "cau_hoi_mo": [],
  "du_an": "hr-codex",
  "module": ["Book", "Comp"],
  "bien_ban": "docs/discussions/2026-10-13-hoa-hong-tam-tinh.md"
}
```

- Thiếu `muc_tieu` hoặc `pham_vi`, JSON sai schema, hoặc `du_an` khác dự án của bead → **không giao**; escalation `phieu-thieu`.
- `cau_hoi_mo` khác rỗng → vẫn giao `spec`; prompt vai spec yêu cầu agent `tram bao --can-hoi --loai can_quyet_dinh` cho từng câu thay vì đoán.
- ~~Phiên điều phối trên máy A tạo bead feature + phiếu (skill phỏng vấn); khối được kiểm qua `POST /api/phieu/kiem` của tram-api trước khi `bd create`.~~ **Thay theo D46/D47 (16/10/2026, plan 4d):** phiên điều phối trên máy A chỉ phỏng vấn, lưu nháp **ngoài repo** và **gửi** yêu cầu; **máy B tạo** bead `feature` nhãn `can-spec` qua `POST /api/feature/yeu-cau` (xem trước: `POST /api/feature/yeu-cau/xem`), cùng bảo vệ API ghi của dashboard (`yeu_cau_ghi`: kênh ghi, danh tính Tailscale do `tailscale serve` gắn, `X-Tram`, `Origin`, Host), dự án phải `bat_ghi` (D31), kho chọn theo `du-an/<du_an>.yaml` của B, actor `dai-ca/may-a` chỉ là nhãn nguồn. Khoá chống trùng là **mã yêu cầu** `yc-<32 hex>` sinh một lần trên A, độc lập nội dung; B lưu biên nhận (bảng `yeu_cau_feature` trong `su-kien.db`) với digest payload: cùng mã cùng nội dung → feature cũ / đang xử lý / chưa rõ; cùng mã khác nội dung → xung đột, không ghi đè, không tạo. `bd create` nhiều nhất một lần mỗi mã; kết quả chưa rõ **chỉ đối soát** theo dòng đầu mô tả `<!-- ma-yeu-cau: yc-… -->`, không tự tạo lại. **Dòng đầu mô tả feature là bất biến** (không luồng nào được sửa). Không fallback A gọi `bd`/SSH. `POST /api/phieu/kiem` giữ nguyên (4b G5) nhưng không còn là bước của skill. D46 không bãi bỏ Task 0/D1 cho luồng Beads từ xa khác.

### 7.2 Bước `spec`

Phiếu `vai = spec`, nhánh `tram/spec-<bead>`, `cha` = `origin/<nhanh_chinh>`. Khe viết, theo đúng định dạng skill `writing-plans`:

- `docs/specs/<ngày>-<ten>.md`, `docs/plans/<ngày>-<ten>.md` — đường dẫn khai trong `spec_file`, `plan_file` của `*.beads.json` (file thường dưới `docs/`, tương đối, không `..`, không symlink);
- **`docs/plans/<feature-id>.beads.json`** (tên cố định theo id feature):

```json
{"phien_ban": 1, "feature": "hr-abc",
 "spec_file": "docs/specs/2026-10-14-hoa-hong-tam-tinh.md", "plan_file": "docs/plans/2026-10-14-hoa-hong-tam-tinh.md",
 "bead": [{"khoa": "t1", "tieu_de": "…", "loai": "task", "uu_tien": 2,
           "mo_ta": "… (trỏ Task N của plan)", "nghiem_thu": "…", "phu_thuoc": [], "nhan": []},
          {"khoa": "t2", "tieu_de": "…", "loai": "task", "uu_tien": 2,
           "mo_ta": "…", "nghiem_thu": "…", "phu_thuoc": ["t1"], "nhan": []}]}
```

**Kiểm** (dữ liệu không tin cậy): `feature` = id bead; 1–30 bead; `khoa` `[a-z0-9-]{1,20}` không trùng; `loai` ∈ {task, bug, chore, spike}; `uu_tien` 0–4; `tieu_de` ≤ 200 ký tự, `mo_ta` ≤ 8.000, `nghiem_thu` ≤ 4.000 và **không rỗng**; `nhan` **không** chứa `cot:*`, `cot-khoa`, `co-do`, `tram:*`, `can-spec`, `cho-duyet-spec`, `theo-plan`; `phu_thuoc` chỉ trỏ `khoa` trong cùng file, không vòng.

Báo `bao.xong` → trạm kiểm (tại SHA công bố của lượt spec): ba file tồn tại, JSON đạt kiểm, diff chỉ trong `docs/**` → gỡ `can-spec`, gắn `cho-duyet-spec`; sự kiện `spec.xong {feature, nhanh, commit, digest_bead, file[]}` → Phê duyệt "Spec chờ duyệt" + Telegram. **Điểm dừng #1.** Khe spec chỉ đề xuất, không tạo bead (Q11).

### 7.3 Duyệt / trả về

- **Đại ca duyệt trên dashboard.** Trang hiện `commit` spec và danh sách bead đề xuất; request Duyệt mang `expected_commit` + `digest_bead` + `ma_thao_tac`. Bản hiện hành khác → **409**, Đại ca phải xem bản mới (G11). **Skill "xem spec chờ duyệt" trên máy A chỉ đọc**: đọc nhánh tại commit đó, tóm tắt, thảo luận, rồi in link dashboard để Đại ca tự bấm; skill không gọi API duyệt.
- **Duyệt** → trạm (`--actor tram/giao-viec`), khoá theo feature, ghi tiến độ từng bước theo `ma_thao_tac` (spec phần 2 §12.3, phần 3 §6.6):
  1. đọc con hiện có của feature; con nào có dòng `<!-- khoa: <khoa> -->` đầu `mo_ta` thì bỏ qua khi tạo lại;
  2. tạo bead còn thiếu: `bd create "<tieu_de>" -t <loai> -p <uu_tien> -d "<!-- khoa: <khoa> -->\n<mo_ta>" --acceptance "<nghiem_thu>" [-l <nhan> khi không rỗng] --parent <feature> --silent`; kết quả không rõ → đối soát theo dòng khoá trước khi tạo lại;
  3. tạo phụ thuộc bằng `bd dep add <bead-sau> <bead-trước>` — **không** dùng `bd create --deps blocks:…` (chiều ngược, spike bd); đọc `dependencies` hiện có và bỏ cặp đã có (`bd dep add` lặp vẫn báo thành công);
  4. gỡ `cho-duyet-spec`, gắn `theo-plan`; sự kiện `spec.duyet {feature, commit, digest_bead, bead_moi[], ma_thao_tac}`.
  **Merge spec:** trước 4c, Đại ca tạo/merge PR `tram/spec-<bead>` tại `commit` đã duyệt; con chỉ được giao khi commit đó đã vào nhánh chính (§5.1 điều kiện 8).
- **Trả về + góp ý** → góp ý vào notes feature + sự kiện `spec.tra_ve {gop_y}`; gỡ `cho-duyet-spec`, gắn lại `can-spec`; lần `spec` sau có góp ý ở lớp 4, `cha` = SHA công bố mới nhất của nhánh spec.
- Feature cha: trạm **không** tự đóng; khi mọi con đóng, vòng tick đưa feature vào Phê duyệt "Feature xong, chờ đóng" — **Đại ca tự đóng** (#16).

## 8. Ngân sách

| Mức | Mặc định | Đo bằng | Hết thì |
|---|---|---|---|
| Phiếu `code` (phần 3 thực thi) | 3 lần chạy, 90 phút wall-clock, 200k token ra | phần 3 §7.6 | thợ báo `bao.bi {ly_do: "het-ngan-sach"}` |
| Phiếu `qc`, `spec` | 2 lần chạy, 45 phút, 100k token ra (trần 3 lần của #13 không bắt nâng lên) | như trên | như trên |
| **Ngân sách thực thi** của bead, mỗi chu kỳ | 3 vòng QC trả về, 9 lần chạy, 6 giờ | vòng = số `qc.ket_qua` `tra_ve`; lần chạy duy nhất theo `(giao_id, lan)`, `request_id` chỉ chống phát lại HTTP; giờ = thời gian đã quyết toán của các phiếu (phần 3 §7.6 — phiếu thiếu `chay.xong` không tính bằng 0) | escalation `het-ngan-sach` |
| **Đợt sửa spec** của feature | 2 lần trả về | số `spec.tra_ve` trong đợt | escalation `spec-tra-ve-nhieu` |

- **Chu kỳ ngân sách thực thi** bắt đầu ở lần giao đầu, và **bắt đầu lại** sau `escalation.dong`, `cot.tra_ve` của bead, hoặc `spec.tra_ve` của feature (#16). Mỗi lần mở chu kỳ ghi `ngan_sach.chu_ky_moi {bead_id, nguon_su_kien_id}` — phát lại cùng nguồn không mở chu kỳ hai lần.
- **Đợt sửa spec** là bộ đếm riêng: `spec.tra_ve` **không** reset bộ đếm này (nếu không, ngưỡng 2 không bao giờ đạt). Đạt 2 → escalation; Đại ca trả lời escalation đó mới mở đợt mới (`ngan_sach.dot_spec_moi`).
- **Giữ trước** (kiến trúc §5.5): một hàm duy nhất `du_mot_phieu(bead, buoc) -> bool` = phần còn lại của chu kỳ ≥ `so_lan_chay` **và** ≥ `phut` của phiếu sắp giao **và** số vòng QC trả về < trần. Giữ trước là **bản ghi bền** trong giao dịch cấp phiếu (phần 3 §6.6), quyết toán khi phiếu kết thúc. §5.1 và vòng tick (§10 bước 1) dùng chung hàm này.
- Phần 4 đọc `doc_quyet_toan` của 3a-1; phiếu chưa quyết toán dùng toàn bộ phần giữ trước trong `giao.nhan.ngan_sach`, không cộng cả hai. Mở chu kỳ theo ID sự kiện nguồn, bù idempotent sau crash; 4a xử lý `escalation.dong`, `cot.tra_ve`; 4b bổ sung `spec.tra_ve`.
- Ghi đè theo dự án trong `du-an/<ten>.yaml` (`ngan_sach:`).

## 9. Escalation (điểm dừng #3) và thao tác nguy hiểm (điểm dừng #4)

**Escalation là một bead `decision`** — luật cứng 1a xếp decision đang mở vào cột 2. Trạm tạo (ID thao tác bền; dấu ID trong mô tả để đối soát):

```
bd create "Bí: <tiêu đề bead gốc>" -t decision -l tram:escalation --silent
  mô tả: lý do (enum bên dưới) + câu hỏi cụ thể + link bead gốc + dấu ma_thao_tac
bd dep add <bead-gốc> <escalation>      # bead gốc bị chặn (blocks) → không được giao
```

| Nguồn | `ly_do` escalation | Làm gì |
|---|---|---|
| `bao.bi {ly_do: "agent"}` | `agent-bi` | escalation ngay |
| `bao.can_hoi {loai_hoi: "thao_tac_nguy_hiem"}` | `can-thao-tac-nguy-hiem` | escalation ngay; trạm gửi **dừng mềm** cho phiếu |
| `bao.can_hoi {loai_hoi: "can_quyet_dinh"}` | `agent-can-hoi` | escalation ngay; mặc định **dừng mềm** phiếu (xem dưới) |
| `bao.bi {ly_do: "het-ngan-sach"}` (ngân sách phiếu) | — | giao lại từ snapshot nếu `du_mot_phieu`; không → `het-ngan-sach` |
| `bao.bi {ly_do: "khe-tat" \| "estop" \| "cau-dao"}`, `bao.het_han_muc` | — | giao lại cho khe khác, **không** escalation |
| `bao.bi {ly_do: "can-hoi"}` (phiếu dừng mềm sau câu hỏi) | — | không tạo escalation mới (đã có từ `bao.can_hoi`); bead chờ câu trả lời |
| `bao.bi {ly_do: "nhanh-bi-day-ngoai-luong"}` | `nhanh-bi-day` | escalation |
| `bao.bi {ly_do: "thieu-moi-truong-kiem"}`; dự án thiếu `moi_truong_kiem` | `thieu-moi-truong-kiem` | escalation, không giao lại |
| vòng tick: `not du_mot_phieu` | `het-ngan-sach` | escalation |
| đợt sửa spec đạt 2 lần trả về | `spec-tra-ve-nhieu` | escalation |
| phiếu yêu cầu không hợp lệ | `phieu-thieu` | escalation |
| diff chạm `duong_dan_cam` | `dong-file-cau-hinh` | escalation |
| QC đổi mã thực thi | `qc-doi-ma` | escalation |

**Câu hỏi của agent và Q6** (Q09 của review): trạm không bao giờ cấp thêm quyền cho phiếu đang chạy. Mặc định, mọi `can_hoi` làm phiếu **dừng mềm** — bước phụ thuộc câu trả lời chuyển sang chờ, không có tác dụng phụ trước khi Đại ca trả lời. "Làm tiếp phần độc lập" chỉ được phép khi phiếu có phạm vi cho phép tường minh do phần 4 cấp (trường `pham_vi_doc_lap` — 4a không cấp, nên ở 4a mọi câu hỏi đều dừng mềm). Trả lời escalation **không** mở quyền deploy/migrate/xoá/gửi khách; thao tác nguy hiểm vẫn do Đại ca tự làm.

- **Trả lời** = đóng escalation: `bd close <esc> --reason "<câu trả lời>"` qua nút **Trả lời** của dashboard 2a (#11). Câu trả lời đọc lại từ `close_reason`.
- **Vòng tick** thấy decision `tram:escalation` chuyển `closed` (dashboard hay `bd` tay) → `escalation.dong {escalation_id, bead_goc, giao_id, tra_loi}` đúng một lần (theo ID escalation); bead gốc hết bị chặn → `buoc_ke_tiep`, câu trả lời ở lớp 4, chu kỳ ngân sách mới.
- **Trùng:** bead gốc đã có escalation **mở** cùng `ly_do` → thêm nội dung vào notes của escalation đó, không tạo bead mới.
- **Escalation đóng chốt mọi hàng rào** (#6 — đã chốt): luật cứng 1a coi bead gốc là đã chốt mọi loại hàng rào khi có escalation đã đóng chặn nó (`blocks`). **Rủi ro đã biết:** trả lời một escalation về chuyện khác (vd hạn mức) cũng gỡ hàng rào tiền/schema của bead đó. Điều này không cấp quyền thao tác production và không xoá cờ đỏ `co-do` ở tầng kiểm. Prompt vai `cham-cot` v2 đưa nội dung escalation vào mục "Quyết định đã chốt", nên LLM vẫn thấy câu trả lời thật nói về gì.

## 10. Vòng tick

`tram giao tick` chạy mỗi 2 phút **trong tram-api** (cùng nhịp với bộ canh hợp đồng của phần 3), không cần khe nào đang xin việc. Mỗi bước idempotent theo ID nguồn. **4a-1 chỉ cung cấp hàm và test giả:** không luồng tick, không CLI `tram giao tick`, không nối `chon_phieu` trong tram-api. Việc nối là 4a-2 sau các cổng; giữ `PhuThuocApi.chon_phieu=None` trước đó. Estop bật → tick chỉ phát sự kiện đọc được (`bead.dong`, `escalation.dong`), **không** ghi beads.

0. Xử lý **công việc chờ** do phần 3 ghi khi phiếu kết thúc (phần 3 §6.6): kiểm bàn giao, kiểm lại, đọc QC, vào cột 3, escalation; đánh dấu xong sau khi xong; ghi `giao.ket_thuc` làm xác nhận.
1. Bead `not du_mot_phieu` mà chưa có escalation mở → escalation `het-ngan-sach` (G5).
2. Decision `tram:escalation` mới đóng → `escalation.dong`.
3. Bead mới đóng (so với bộ đệm beads) → `bead.dong {du_an, bead_id}`.
**Ràng buộc lúc nối 4a-2:** xử lý escalation/câu hỏi phải tiếp tục trong khi suite kiểm lại dài đang chạy; không đặt kiểm lại đồng bộ trên luồng duy nhất xử lý tick. Kiểm G5 ≤3 phút với suite giả dài 15 phút, lỗi Git một dự án và restart. Hàm `kiem_lai` đồng bộ của 4a-1 là đơn vị công việc, chưa bảo đảm thời hạn hệ thống. Không đổi mặc định G5.

4. Feature `theo-plan`: commit spec đã vào nhánh chính → mở điều kiện 8 cho con; chưa sau 24 giờ → `spec.cho_merge` (Telegram nhắc). Mọi con đã đóng → `feature.xong` → Phê duyệt "Feature xong, chờ đóng".

## 11. Gói ngữ cảnh (thực hiện §5.1 kiến trúc)

`dung_goi(phieu) -> str` — markdown, thứ tự cố định trước, hay đổi sau (hợp prompt cache):

| Lớp | Nội dung | Nguồn |
|---|---|---|
| 1. Dự án | các file trong `tai_lieu_du_an` (mặc định `AGENTS.md`, `CLAUDE.md`, `docs/ARCHITECTURE.md`, `docs/CURRENT_STATE.md` nếu có), đọc tại **`origin/<nhanh_chinh>`** — không tại `cha` (agent có thể đã sửa các file đó trên nhánh của nó); 4c thêm luồng liên quan từ gitnexus | repo |
| 2. Vai | `vai/<vai>.md` (coder, qc, spec — có `phien_ban`) + hướng dẫn chung: dùng `tram bao` (kể cả phân loại `--can-hoi`), cập nhật `.tram/tien-do.md`, viết bàn giao đúng schema, **chép nguyên văn** từng dòng `tieu_chi` của phiếu vào `doi_chieu_nghiem_thu[].tieu_chi` (hàm kiểm so khớp từng ký tự), QC ghi khối `<!-- qc -->` có `commit_code` | repo trạm |
| 3. Task | bead: id, loại, tiêu đề, mô tả, `acceptance_criteria`, `design` (hoặc phiếu yêu cầu) — **bọc `<du_lieu_khong_tin_cay>`** | beads |
| 4. Đầu vào tường minh | bàn giao chính thức của bead phụ thuộc `blocks` (đã đóng); bàn giao tạm gần nhất của chính bead; kết quả kiểm lại; phát hiện QC; góp ý trả về; câu trả lời escalation; với `qc`: diff tới `commit_code` | sự kiện + notes |
| 5. Bài học & quyết định | 4c: gọi HTTP recall của memory (`nho_lai` với vùng cấp `[/du-an/X, /vai/V, /chung]`, spec 1b §7) khi 1b-1 sẵn sàng; trước đó để trống. Bead `decision` đã đóng mà bead phụ thuộc `blocks` (kèm `close_reason`) | memory + beads |

- **Ngân sách token** của gói: 60.000 token, ước lượng thận trọng 1 token ≈ 2,5 ký tự. Vượt → cắt lớp 4 trước: giữ `quyet_dinh`, `huong_da_bo`, `buoc_tiep`, `cau_hoi_mo`, bỏ `doi_chieu_nghiem_thu` và `lenh_kiem`; vẫn vượt → bỏ bàn giao phụ thuộc cũ nhất trước; diff QC cắt theo file, ghi "đã cắt".
- Sau khi cắt phần được phép mà gói vẫn vượt 150.000 ký tự (ước lượng 60k token), `dung_goi` báo `GoiQuaLon`; không cấp/claim phiếu. Không cắt ngầm chỉ dẫn bắt buộc hoặc tiêu chí.
- Lớp 3, 4, 5 bọc `<du_lieu_khong_tin_cay>` (dùng chung hàm bọc chặt `_boc` của 1a — đổi thành hàm công khai).

## 12. Sự kiện (bảng `su_kien` phần 0)

Phần 3 ghi `giao.nhan` (dữ liệu theo bảng này); `escalation.tra_loi` do dashboard ghi; còn lại phần 4 ghi.

| Loại | Dữ liệu |
|---|---|
| `giao.nhan` | `{giao_id, luot, khe_id, bead_id, buoc, vai, cha, khoa_chong_trung, ngan_sach, ref_phieu}` (không có `ma_giao`) |
| `giao.ket_thuc` | `{giao_id, luot, buoc, ket_thuc: "xong"\|"bi"\|"het_han_muc"\|"thu_hoi", ly_do, commit, loi[]}` — xác nhận đã xử lý pipeline; **không** định nghĩa hiệu lực phiếu |
| `kiem.lai` | §6.2 |
| `qc.ket_qua` | §6.3 |
| `bead.vao_cot_3` | §6.4 |
| `bead.dong` | `{du_an, bead_id}` |
| `escalation.tao` / `escalation.dong` | `{escalation_id, bead_goc, giao_id, ly_do, ma_thao_tac}` / `{…, tra_loi}` |
| `escalation.tra_loi` | `{escalation_id, ma_thao_tac}` (dashboard) |
| `spec.xong` / `spec.duyet` / `spec.tra_ve` / `spec.cho_merge` | §7, §10 |
| `feature.xong` | `{feature}` |
| `ngan_sach.chu_ky_moi` / `ngan_sach.dot_spec_moi` | `{bead_id, nguon_su_kien_id}` |
| `phieu.loi` | `{bead_id, loi[]}` |

**Bảng điểm thợ** (phần 2b), tính lúc đọc theo (khe, vai):

- *Qua lần đầu* = số phiếu `code` mà `kiem.lai` đầu tiên cho SHA của phiếu đó đạt **và** `qc.ket_qua` đầu tiên cho commit đó là `dat` ÷ số phiếu `code` kết thúc `xong`.
- *Bị trả về* = số bead khe đã code mà sau khi vào cột 3 có `cot.tra_ve` ÷ số bead khe đã code vào cột 3.
- *Số lần chạy trung bình* = trung bình số `chay.bat_dau` mỗi phiếu.

> **Ghi chú 16/10, D13, D25–D29 (lát 2d, đã có mã** `tram/suy/{bang_diem,diem_giao_viec}.py`**):** các chỗ spec chưa định nay đã được Đại ca chốt, và mã theo đúng chữ này. Chỉ tính cho vai `coder` (phiếu bước `code`); vai `qc`, `spec` để `null` (D29).
> - **SHA của phiếu (D25):** `commit` của `giao.cong_bo` cùng dự án, bead và lượt; nhiều bản thì lấy bản sau cùng. Phiếu chưa công bố không vào tử nhưng vẫn nằm trong mẫu.
> - **Qua lần đầu (D26, D29):** `kiem.lai` sớm nhất có đúng SHA phải đạt, và `qc.ket_qua` sớm nhất cho cùng commit mà được ghi **sau** lần kiểm lại ấy phải là `dat`. Mẫu = số phiếu `code` có `phieu.ket_thuc = xong`. Tử không đòi phiếu đã xong.
> - **Bị trả về (D27):** mỗi lần `bead.vao_cot_3` là một mẫu, tính cho khe giữ phiếu code trong bằng chứng của lần vào cột 3 đó. Bị trả về khi `cot.tra_ve` xảy ra trước lần vào cột 3 kế tiếp của cùng bead. (Thay chữ "số bead khe đã code" ở trên: một bead vào cột 3 nhiều lần thì có nhiều mẫu.)
> - **Lọc (D14, D28):** theo dự án (lấy theo phiếu) và số ngày gần nhất (mặc định 30) tính theo thời điểm cấp phiếu. Kết quả có cỡ mẫu; mẫu 0 thì tỉ lệ `null`. Bảng luôn có hàng cho mọi khe đã khai (D41).
> - `qc.ket_qua` và `kiem.lai` (phiếu spike: `ket_qua: []`) còn là cửa kích hoạt nguồn ký ức bàn giao của spec 1b §6.1 (D8, lát 1b-4).

## 13. Thành phần và giao diện với phần 3

```
tram/giao_viec/
  dieu_kien.py   # §5.1
  chon.py        # §5.2, §5.3 — thứ tự và luật chọn khe
  bo.py          # chon(khe_id, han_muc) -> DeXuatPhieu | None; con_hop_le(de_xuat) -> bool
  pipeline.py    # §4, §6.6: buoc_ke_tiep(bead, su_kien)
  kiem_lai.py    # §6.2: duong_dan_cam, worktree kiểm, môi trường kiểm, lệnh bắt buộc
  bang_chung.py  # §6.7
  goi.py         # §11
  escalation.py  # §9
  feature.py     # §7: phiếu yêu cầu, *.beads.json, duyệt/trả về có đối soát
  ngan_sach.py   # §8: du_mot_phieu, chu kỳ, đợt spec
  tick.py        # §10
vai/coder.md, vai/qc.md, vai/spec.md
```

- Phần 3 gọi `chon_phieu(khe_id, han_muc)` ngoài giao dịch, callback `con_hop_le(de_xuat)` trong giao dịch cấp phiếu (3a-1 G11); phần 4 tự gọi `trang_thai_khe()`, dùng `duoc_nhan()` và `phieu_hieu_luc()` của phần 3. `BoGiaoViec` nhận `(cac_du_an, tao_bd, mo_kho, ch, dong_ho, kho_git, boc, env_goc)`; `boc=None` chặn chạy lệnh kiểm lại. Không đổi chữ ký đã chốt của 3a-1.
- Phần 3 ghi công việc chờ khi phiếu kết thúc; phần 4 xử lý ở vòng tick bước 0.
- Khoá trong `du-an/<ten>.yaml`: `lenh_cho_phep`, `moi_truong_kiem`, `nhanh_chinh` (phần 3 dựng ở 3a), `lenh_kiem_mac_dinh`, `duong_dan_cam`, `duong_dan_cam_cho_phep`, `tai_lieu_du_an`, `ngan_sach`.
- Phần 4 **tái dùng** các hàm phần 3a đã dựng: `khop_lenh`, kiểm `duong_dan_cam`, `kiem_ban_giao(can_lenh_kiem)` theo luật chặt.

## 14. Chi tiết đã được Đại ca duyệt cùng spec ngày 13/10/2026

1. **Escalation là bead `decision`**; trả lời = `bd close --reason`.
2. **Không bao giờ gắn `cot:ai-lam`/`cot:can-chot`**; vào cột 3 thay mọi `cot:*` bằng `cot:cho-review`.
3. **Trạm điều phối kiểm lại** mọi lệnh bắt buộc tại SHA công bố, trong môi trường thực thi cách ly, không qua shell.
4. **QC không sửa mã** — kiểm bằng diff `commit_code..commit_qc` chỉ trong `docs/handovers/**` (Đại ca chốt 13/10).
5. **Nhãn mới `theo-plan`** cho feature đã duyệt spec; 1a thêm vào nhãn bỏ qua (spec 0+1a §5).
6. **Sửa nhỏ ở phần 0**: `kiem_ban_giao` luật chặt + `can_lenh_kiem` (spec 0+1a §4.3, §11); mở rộng `Bead` (2a) và `nap_du_an` (3a).
7. **Sửa nhỏ ở 1a** (làm cùng 4a): bead `decision` đang mở không gọi LLM chấm (luật cứng đã xếp cột 2) — mỗi lần phần 4 thêm notes vào escalation không còn là một lần gọi LLM.
8. **Lớp 1 đọc tại nhánh chính**, không tại `cha`.
9. **`duong_dan_cam` tối thiểu của trạm**, khớp ở mọi cấp; ngoại lệ chỉ theo từng đường dẫn.
10. **Thứ tự** §5.2 và luật chọn khe §5.3.
11. **Ngân sách mặc định** bảng §8; gói 60k token.
12. **Một bead một phiếu** tại một thời điểm.
13. **Cờ đỏ 4a theo đường dẫn file**, gitnexus để 4c.
14. **`*.beads.json` tên cố định theo id feature**; tạo bead idempotent theo `khoa` và đối soát.
15. **Skill trên máy A chỉ đọc**, không gọi API duyệt.
16. **Kiểm phiếu yêu cầu qua `POST /api/phieu/kiem`**; phần 4 tự thêm route này và hàng "Feature xong, chờ đóng".
17. **Bead cột 1 thiếu `acceptance_criteria` máy đọc được thì không giao** (§5.1 điều kiện 4).

## 15. Quyết định đã chốt 13/10 (thay mục câu hỏi)

| Câu cũ | Quyết định | Ghi ở |
|---|---|---|
| 1 | Escalation đóng **chốt mọi hàng rào** (#6); rủi ro ghi ở §9 | §9 |
| 2 | Nút **Trả lời escalation** có trong 2a — điều kiện của 4a (#11) | §3, §9 |
| 3 | **GitHub** từ 3a, không dùng bare repo tạm; sửa Q15 kiến trúc (#2) | §3, §6.4, §7.3 |
| 4 | Lệnh kiểm của thợ chạy dưới principal thực thi của khe; kiểm lại của trạm dưới principal kiểm lại `tram-kiem` (đề xuất, phần 3 §13 mục 12); không bao giờ dưới quyền trạm (#3) | §6.2 |
| 5 | Con của feature **chờ commit spec đã duyệt vào nhánh chính** (theo đề xuất, câu 2 của bàn giao gộp) | §5.1 điều kiện 8, §7.3 |
| 6 | QC chéo hai khe cùng model Claude: **chấp nhận** (#17) | §5.3 |
| 7 | Feature cha: trạm nhắc, **Đại ca tự đóng** (#16) | §7.3, §10 |
| 8 | Ngân sách **bắt đầu lại** khi Đại ca trả lời hoặc trả về (#16), tách đợt sửa spec | §8 |
| 9 | 4a chạy thử trên **repo nháp 3 bug** trước HR Codex (#4) | §2 G8, §3 |
| 10 | Bộ chấm 1a **bỏ qua bead có phiếu hiệu lực**, chấm lại khi phiếu kết thúc (#10) | §5.1; spec 0+1a §5, §5.6 |
| Codex 3 | QC chỉ được đổi `docs/handovers/**`; đổi mã → escalation `qc-doi-ma` (Đại ca chốt 13/10) | §6.3 |
| Codex 4 | Mọi `can_hoi` dừng mềm phiếu ở 4a; `pham_vi_doc_lap` để sau (Đại ca chốt 13/10) | §9 |
| Codex 5 | Đợt sửa spec là bộ đếm riêng, không reset bởi `spec.tra_ve` (Đại ca chốt 13/10) | §8 |

**Đề xuất kỹ thuật mới cần Đại ca chốt** (từ review Codex):

- Phụ thuộc vào ref tạm/công bố của phần 3 §6.4 (chờ S7).

## 16. Kiểm chứng

1. **Unit test** (beads giả, sự kiện SQLite tạm, khe giả, đồng hồ tiêm): điều kiện §5.1 cả hai nhánh — bead `in_progress` vẫn được giao `qc`; spike được giao; bead thiếu tiêu chí máy đọc không được giao; bead nhiều nhãn cột không được giao (G3); Q14 kể cả khi vai lan (G2); vai lan khi khe chính cạn; ưu tiên khe đã code; thứ tự và tie-break; `du_mot_phieu` dùng chung cho chọn và tick; chu kỳ không mở hai lần khi phát lại; đợt spec đạt 2 lần trả về → escalation; `khop_lenh` loại `;`, `&&`, `$(…)`, xuống dòng, token thừa, tham số thực thi ngoài mẫu (G4); kiểm lại: một tiêu chí `false` + lint pass → không đạt; suite bắt buộc fail + test nhỏ pass → không đạt; thiếu lệnh bắt buộc → không đạt; lệnh bắt buộc timeout → không đạt (G1); spike tài liệu không chạy lệnh; `duong_dan_cam`: `erp/package.json`, `AGENTS.md` lồng, đổi tên sang file cấm, symlink bàn giao/`.env.testing` (G9); QC đổi một file nguồn → không công nhận (G10); push mới sau QC đạt → bằng chứng hết hiệu lực; bàn giao mang SHA của bead khác → bị từ chối; ánh xạ `bao.bi` theo `ly_do`; `can_hoi` mặc định dừng mềm; `buoc_ke_tiep` từng dòng §6.6; feature bị escalation chặn không được giao `spec` lại; escalation không trùng; `escalation.dong` khi đóng bằng `bd` tay, đúng một lần; dựng gói đúng thứ tự, lớp 1 tại nhánh chính, bọc dữ liệu, cắt khi vượt; kiểm phiếu yêu cầu; kiểm `*.beads.json`; Duyệt spec với `expected_commit` cũ → 409 (G11); Duyệt lại hoặc crash sau `bd create` không tạo trùng (G7); vào cột 3 thay toàn bộ nhãn cột.
2. **Tương tác với mã 1a thật** (bộ quét 1a với `bd` giả + phần 4 ghi): phần 4 ghi beads không làm 1a khoá; bead có phiếu hiệu lực không bị 1a chấm; phiếu kết thúc tạo yêu cầu chấm lại; escalation decision được 1a xếp cột 2.
3. **Kịch bản giả lập đầu-cuối** với thợ giả của phần 3 và remote Git cục bộ giả: bug đi hết code → kiểm lại → QC trả về → code → QC đạt → cột 3 (G1, G8); bead bí → escalation → đóng → giao lại (G5); tắt khe giữa chừng → giao lại không escalation; feature → spec → duyệt → bead con (G6, G7); injection trong mô tả bead và trong `*.beads.json` không đổi được nhãn/cột.
4. **Trên máy thật** (Đại ca cho phép, tốn quota): repo nháp với 3 bead bug nhỏ chạy trọn 4a (#4); một feature nhỏ chạy trọn 4b.

## 17. Ngoài phạm vi

Merge queue; tự merge; chạy song song nhiều bước của một bead; manager LLM tự quyết giao việc (kiến trúc §6 "Không lấy"); giao việc qua nhiều trạm chủ; bead `tram:merge-request` của kiến trúc §3 (không dùng — PR trên GitHub thay thế).


## 18. Hợp đồng trình duyệt sau review độc lập 13/10

Các hợp đồng của phụ lục này đã được Đại ca chấp thuận ngày13/10 theo handover đợt1+2; chưa mở cổng chạy thật. Việc sửa văn bản không phải chứng cứ test/spike. Thứ tự code giữ nguyên **3a-1 → 1b-3 → 2b → 4a-1 → 1b-2**. Các điều chỉnh G2/G5/G6/G7/G8/G15/G28 và G29–G31 của plan 4a-1 đã chốt trong lần duyệt đó; quyết định §15 không đổi.

- **Sự kiện:** `giao.nhan`, `bao.*`, `giao.cong_bo` do phần 3 ghi; `giao.ket_thuc`, `kiem.lai`, `qc.ket_qua`, `bead.vao_cot_3`, `escalation.tao/dong`, chu kỳ do phần 4 ghi; `escalation.tra_loi`, `cot.tra_ve` do dashboard. Các sự kiện này mang cột `du_an` của dự án và `bead_id`, không dùng `_tram`. `_tram` dành sự kiện máy/khe/cầu dao của phần 3 và 2b. Consumer 2b đọc số liệu, 1b-2 đọc nguồn ký ức; không đổi schema bằng cách giả các producer đã chạy.
- **`giao.ket_thuc`:** `ly_do=null` chỉ khi xong hợp lệ; lỗi code gồm `chua-cong-bo`, `commit-khong-cong-bo`, `dong-file-cau-hinh`, `ban-giao-loi`; lỗi QC gồm `qc-doi-ma`, `khoi-qc-loi`, `ban-giao-qc-loi`; `bi/thu_hoi` giữ lý do nguồn. `commit` chỉ là SHA đã xác minh, `loi` tối đa 20 mục. Hiệu lực phiếu vẫn thuộc bảng `phieu`, không suy từ sự kiện này.
- **`kiem.lai`:** có `giao_id`, `bead_id`, `luot`, `commit`, `digest_tieu_chi` của phiếu (so với tiêu chí hiện tại khi dùng), `dat`, `ket_qua[]`, `digest_log[]`, `cham_cam[]`. Thiếu/không đọc được môi trường kiểm hoặc đích symlink → escalation, không ghi `kiem.lai`; sau trả lời được kiểm lại. Spike tài liệu không chạy lệnh.
- **Escalation:** mô tả có dòng `ly_do`, `bead_goc`, `giao_id`, câu hỏi và dấu `<!-- ma_thao_tac: esc-<20 hex> -->`. ID là băm của `(du_an, bead_id, ly_do, nguon)`: nguồn phiếu, `hoi-<id sự kiện>`, `ns-<mốc chu kỳ>`, `kl-<sha>`, `du-an-<phút>`. Đối soát chỉ nhận decision đúng nhãn `tram:escalation`, bead gốc, lý do, dấu nguyên dòng; không lấy bead tuỳ ý có nhúng dấu trong văn bản. Mọi câu hỏi chưa chuyển thành decision vẫn chặn giao tiếp (G30).
- **Cấu hình:** `lenh_kiem_mac_dinh: [lệnh khớp allowlist]`, `duong_dan_cam: [glob tương đối]`, `duong_dan_cam_cho_phep: [đường dẫn cụ thể không glob]`, `tai_lieu_du_an: [đường dẫn]`, `ngan_sach: {code: {so_lan_chay, phut, token_ra}, qc: {...}, bead: {vong_qc, lan_chay, phut}}`; mỗi phiếu không quá 3 lần CLI. Mặc định §8 giữ nguyên.
- **Tách module theo plan:** thêm `tieu_chi`, `su_kien`, `git_kiem`, `lop_4`, `khoi_qc`, `xet_xong`, `xu_ly_viec`, `ung_vien`, `de_xuat`, `tick_doc`, `tick_pipeline`; dùng `tram/cau_hinh/lenh.py`, `tram/kiem/*` của 3a-1. Đầu vào agent luôn là dữ liệu, các chốt bằng mã quyết định quyền và cột.
- **Ngoài 4a-1:** feature/theo-plan chưa giao, cha thiếu trong snapshot fail-closed; `phien_ban_quyen="0"` chỉ trước 3a-2; lớp 5 chưa bật; clone/công bố ref/principal/callback thật chờ 4a-2. G1–G11 là tiêu chí nghiệm thu các lát tương ứng, không phải kết quả đã đạt.

## 19. Đồng bộ plan đợt3 sau review tĩnh 14/10

Không đổi quyết định ngày13/10; các chi tiết mới chưa qua cổng chạy thật.

1. **§6.6/bs-ecd:** dòng4 áp dụng khi ref vẫn là code đã kiểm **hoặc** ref mới nhất do đúng lượt QC mới nhất sau lần kiểm công bố rồi QC kết thúc `thu_hoi`/`bi`/`het_han_muc`, chưa có kết luận. Trường hợp sau chỉ giao `qc` lại, không vào cột3. `giao_id`/`luot` code, digest hiện tại, cửa sổ trả cột phải còn đúng; công bố khác lượt không được tái dùng. TDD4a-2T7 bao gồm các ca âm này.
2. **§9/bs-s52:** đối soát marker thao tác escalation nhận decision đúng nhãn/gốc/lý do kể cả đã đóng sau crash. Khôi phục sự kiện tạo rồi đối soát đóng và mở ngân sách một lần; nguồn mới khác vẫn có thể tạo escalation mới. Main đã làm đúng, plan thêm hồi quy bảo vệ.
3. **§7.3/Q6:** request Duyệt dùng `expected_version`, `expected_commit`, `digest_bead`, `ma_thao_tac`. Resume thao tác dở phải kiểm lại bản hiện hành trước từng bước chưa hoàn tất; bản đã bị trả về/công bố khác →409, không tiếp tục tạo con/đổi nhãn. Chỉ nhãn do đúng thao tác đã đổi được resume; thao tác hoàn tất trả lại kết quả cũ. Không có giao dịch xuyên Beads/Git/SQLite, không tuyên atomic.
4. **ADR trước tự giao:** regex ADR không là chứng cứ đã được duyệt. 4a-2 thêm callback xác minh tồn tại, trạng thái approved, đúng repo/phạm vi; thiếu adapter tin cậy thì fail-closed cho trường hợp chỉ dựa ADR. Decision `blocks` đã đóng giữ nguyên #6 và rủi ro đã chấp nhận. Nguồn/schema approved ADR chưa chốt; không tự thêm adapter tin vào text agent.
5. **Tách tick:** nhanh không Git; queue lọc project/pha trước LIMIT. `feature.xong` chỉ do pha nhanh ghi, `spec.cho_merge` do pha Git sau fetch khi estop tắt. Kill lệnh kiểm qua cùng principal được nối bằng callback3a-2, còn S6 phải kiểm thật.
6. **G23 plan4b:** schema `*.beads.json` hiện chưa có `lenh_kiem`/`design`; lấy lệnh mặc định/allowlist dự án. Đề xuất thêm `lenh_kiem` từng bead là **chưa duyệt**, không nằm trong mã mẫu được thực thi. Nếu Đại ca chấp thuận sau, phải sửa schema/validator, skill, bước tạo `design`, digest, UI tóm tắt và TDD cùng một thay đổi.

7. **PR và bằng chứng hiện hành — đề xuất kỹ thuật 4c G6 cần duyệt:** trước tạo PR và sau tạo phải đọc head, đối chiếu đúng SHA đã kiểm. Trước tự đóng phải đọc lại bead, ref công bố, digest tiêu chí và bằng chứng đúng lượt; PR đúng repo/head/base, đã merge, commit đã kiểm nằm trong merge commit và nhánh chính. Plan 4c chỉ tự xác minh khi head PR bằng `commit_ban_giao`; topology của hậu duệ merge không chứng minh tree không chứa mã chưa kiểm. Hậu duệ khác, squash/rebase hoặc thiếu bằng chứng → giữ cột 3, chờ kiểm lại/Đại ca xử lý. Đây là phạm vi tự xác minh bảo thủ, không thay quyền merge Q7 và không chọn phương án công bố §14 spec 3. Push ngoài luồng giữa hai lần đọc vẫn là cửa sổ đua phải kiểm qua S7. Crash sau tạo PR phải tìm cả PR OPEN/MERGED cùng định danh trước khi tạo lại.
8. **Nối phụ thuộc 4c — đề xuất G1/Task 8 cần duyệt:** cấu hình riêng `phu_thuoc_4c: {github: false, gitnexus: false, memory: false}`, boolean nghiêm ngặt, thiếu là tắt. `dung_bo_that` nối bộ phụ thuộc; `giao_viec.bat=false` không dò CLI/Keychain hay dựng kết nối 4c. GitHub chỉ bật sau S7, Gitnexus sau spike GN; memory bật riêng khi dịch vụ/token sẵn sàng. Không xem việc có wiring là đã qua cổng. Gitnexus JSON sai schema tạo cờ đỏ; recall sai vùng cấp bị loại, decision vẫn giữ.

## Trạng thái triển khai (15/10/2026)

Đối chiếu với mã trên `main` (1c5f507, 1987 test pass). 4a-1, 4a-2 (T1–13), 4b và 4c đã có mã. **Cập nhật 16/10/2026:** đối chiếu lại với `main` `f5b1fdb` (2242 test Python pass); phần 4 không đổi mã trong đợt 15–16/10, chỉ bảng điểm (§12) và các nguồn đọc sự kiện phần 4 có thêm người dùng mới (2d, 1b-4). Hàng đổi có nhãn "(16/10)". Bộ giao việc thật mặc định **tắt** (`giao_viec.bat = false`); GitHub, gitnexus và memory của 4c cũng tắt (`phu_thuoc_4c`). Chưa bead thật nào đi qua pipeline. G1–G11 mới đạt trên kịch bản giả lập.

**Cập nhật 17/10/2026 (I1):** đối chiếu lại với `main` `59f8281` (2697 test Python, 101 node) bằng `ls`/`grep`. Phần 4 đổi ở ba chỗ: (1) kiểm lại dưới `tram-kiem` theo 3c (`9ee1ed3`, `59f8281`); (2) tạo feature qua API trên B theo D46/D47 (4d, `a02728b`); (3) khoá `bat_ghi` (D31) chặn giao việc và thao tác ghi (1a-2 Task 5, `2d0b5ba`). Vẫn **chưa bead thật nào đi qua pipeline**; `giao_viec.bat` vẫn `false`. Hàng đổi có nhãn "(17/10)".

Hành vi đã chốt và đã có mã (17/10):
- **Kiểm lại trong Seatbelt cấm mạng và IPC (D48).** Mọi lệnh của lượt chạy dưới `tram-kiem` trong hồ sơ cấm mặc định, chỉ ghi trong thư mục lượt, HOME/TMP riêng mỗi lượt (D45); không mạng (chỉ unix socket trong lượt), không IPC POSIX/SysV. Dự án cần DB/Redis dùng chung sẽ báo lỗi rõ, không nới hồ sơ.
- **Cổng kiểm đóng thì chờ Đại ca mở (D49).** Cổng lượt bền ở `~/.tram/kiem-lai/cong.json` (`mo`/`dang-chay`/`dong`). Quan sát thấy tàn dư, không quan sát được, không thu hồi được → `dong`, lượt sau bị chặn. Trạm không tự mở; Đại ca mở bằng `tram giao mo-cong-kiem` (thu hồi + quan sát lại, chờ `dong-y`).
- **R7 từ chối repo lạ (D50).** Bản chép kiểm phải đúng cây commit (so mã cây). Repo có CRLF dưới `text`, `ident`, submodule, trùng tên hoa–thường, `._*`, kho sha256, hoặc kho kiểm có `filter.*` → escalation `cay-khac-nguon`, không ghi `kiem.lai`.
- **Tạo feature qua API B (D46/D47).** Máy A phỏng vấn và gửi; tram-api trên B xác thực (`yeu_cau_ghi`), chọn kho theo `du-an/<du_an>.yaml`, tạo đúng một bead `feature` `can-spec` cho mỗi mã yêu cầu. Mã yêu cầu cố định, độc lập nội dung; cùng mã khác nội dung → xung đột; kết quả chưa rõ (`khong_ro`) chỉ đối soát, không tạo lại.
- **`bat_ghi` (D31, D37).** Dự án `bat_ghi: false` không vào danh sách giao việc (`cac_du_an_that`), tram-api từ chối thao tác ghi (422), `tram quet --ghi` bỏ qua dự án đó; dashboard hiện chip "chỉ quét thử". Thiếu khoá = bật. `du-an/hr-codex.yaml` có `bat_ghi: false` (D40).

| Mục spec | Trạng thái | Nơi trong mã | Plan/Task |
|---|---|---|---|
| §4, §6.6 Pipeline theo loại, `buoc_ke_tiep` | đã có mã + test | `tram/giao_viec/pipeline.py` | 4a-1 T8; 4a-2 T7 |
| §5.1 Điều kiện giao, đọc lại Beads ngay trước cấp | đã có mã + test | `tram/giao_viec/{dieu_kien,doc_lai,doc_beads}.py` | 4a-1 T10; 4a-2 T4 |
| §5.1 điều kiện 7 `phien_ban_quyen` | đã có mã + test | `tram/giao_viec/quyen.py` | 4a-2 T2 |
| §5.1 điều kiện 8 Con chờ merge spec | đã có mã + test | `tram/giao_viec/{dieu_kien,spec_merge}.py` | 4b T4, T17 |
| §5.2–5.3 Thứ tự, chọn khe, Q14 | đã có mã + test | `tram/giao_viec/{chon,ung_vien}.py` | 4a-1 T7, T17 |
| §5.4 Ghi beads: claim, cột 3 | đã có mã + test | `tram/beads/bd.py`, `tram/giao_viec/{bo,bang_chung}.py` | 4a-1 T1, T15, T18 |
| §6.1 Bước `code`: lệnh bắt buộc, tiêu chí, xét `bao.xong` | đã có mã + test | `tram/giao_viec/{tieu_chi,de_xuat,xet_xong,xu_ly_viec}.py` | 4a-1 T3, T12, T16–17 |
| §6.2 Kiểm lại: đường dẫn cấm, worktree tách rời, lệnh bắt buộc | đã có mã + test; kho kiểm thật chờ cổng chạy thật (S7), `tram-kiem` chờ S6. (17/10) Bản chép do `tram-kiem` dựng (repo một commit, D40), đúng cây commit (R7, D50); mọi lệnh trong hồ sơ Seatbelt cấm mặc định, không mạng/IPC (D45, D48); cổng lượt bền, chờ `mo-cong-kiem` (D49); thu hồi theo UID thực; `da_thu_hoi = False` hoặc còn dấu `kiem-lai.dong` → không công nhận. Quan sát launchd mới là khung (cổng luôn đóng tới 3C-D7, sau G3). C01 chưa đóng (G4) | `tram/giao_viec/{kiem_lai,git_kiem,kho_kiem_tao,principal_kiem}.py`, `tram/kiem/`; (17/10) `tram/giao_viec/{ban_chep,repo_ban_chep,cay_kiem,cong_luot,cong_that,quan_sat_kiem,thu_muc_he}.py`, `tram/tho/quyen_kiem.py` | 4a-1 T5, T14; 4a-2 T1, T3, T5; 3c r47 T3, T5, T10, 3C-C, 3C-D1..D6 |
| §6.3 Bước `qc`, khối QC, `qc-doi-ma` | đã có mã + test | `tram/giao_viec/{khoi_qc,xet_xong}.py` | 4a-1 T12, T16 |
| §6.4 Cột 3, bằng chứng, cờ đỏ theo đường dẫn | đã có mã + test | `tram/giao_viec/{bang_chung,tick_cot_3}.py` | 4a-1 T15; 4a-2 T7 |
| §6.4 mục 4, §6.5 Tự mở PR, tự xác minh merge | đã có mã, chờ cổng chạy thật (S7); mặc định tắt | `tram/giao_viec/{gh,pr,pr_bang_chung,pr_merge,tick_github}.py` | 4c T1, T5, T7 |
| §6.4 mục 3 Cờ đỏ theo gitnexus | đã có mã, chờ cổng chạy thật (spike GN); mặc định tắt | `tram/giao_viec/{gitnexus,co_do_gn}.py` | 4c T2, T6 |
| §7.1 Phiếu yêu cầu, `POST /api/phieu/kiem` | đã có mã + test | `tram/giao_viec/phieu_yeu_cau.py`, `tram/api/tuyen_feature.py` | 4b T2, T19 |
| §7.1 (17/10) Skill phỏng vấn máy A; B tạo feature qua `POST /api/feature/yeu-cau` và `/xem` (D46/D47) | đã có mã + test; chạy thật chờ G6 (4D-4) | `tram/yeu_cau/{so_nhan,mau,dich_vu}.py`, `tram/api/tuyen_yeu_cau.py`, `ky-nang/phong-van-yeu-cau/{nhap,khach,yeu_cau}.py`, `SKILL.md` | 4d 4D-1a..3c |
| §7.2 Bước `spec`, `*.beads.json`, vai `spec` | đã có mã + test | `tram/giao_viec/{ke_hoach,xet_spec,de_xuat_spec,ung_vien_spec,feature}.py`, `vai/spec.md` | 4b T3, T9–10, T13–15 |
| §7.3 Duyệt (409 theo commit), tạo con có đối soát, Trả về, Đóng feature | đã có mã + test | `tram/thao_tac/{duyet_spec,tao_con,spec}.py`, `tram/beads/bd.py` | 4b T1, T11, T16 |
| §7.3 Skill "xem spec chờ duyệt" trên máy A | đã có mã + test; chưa cài lên máy A | `ky-nang/xem-spec-cho-duyet/` | 4b T12 |
| §8 Ngân sách: phiếu, chu kỳ, đợt sửa spec | đã có mã + test | `tram/giao_viec/{ngan_sach,feature}.py` | 4a-1 T9; 4b T9 |
| §9 Escalation, ánh xạ `bao.*` | đã có mã + test. (17/10) Thêm lý do `cay-khac-nguon` (R7, D50) | `tram/giao_viec/escalation.py` | 4a-1 T13, T16; 4a-2 T6 |
| §9 `pham_vi_doc_lap` | chưa có mã (Đại ca để sau; mọi `can_hoi` dừng mềm) | — | — |
| §10 Vòng tick, luồng trong tram-api, `tram giao tick` | đã có mã + test; bật chờ cổng chạy thật. (17/10) `tram giao kiem` chạy dưới khoá kiểm lại, chỉ khi cổng chưa đóng, xác minh UID thực trước mọi probe; mục đỏ → đóng cổng. Thêm `tram giao mo-cong-kiem` và `tram giao nghiem-thu-kiem` (harness S6, chưa chạy) | `tram/giao_viec/{tick,tick_doc,tick_pipeline,tick_feature,tick_theo_plan,luong,noi_that,lenh,kiem_san_sang}.py` | 4a-1 T19; 4a-2 T7–10; 4b T6, T18 |
| §11 Gói lớp 1–4, cắt, `GoiQuaLon` | đã có mã + test | `tram/giao_viec/{goi,lop_4}.py` | 4a-1 T11 |
| §11 Lớp 5, luồng gitnexus ở lớp 1 | đã có mã, chờ cổng chạy thật (memory, spike GN); mặc định tắt | `tram/giao_viec/{lop_5,noi_4c,phu_thuoc_4c}.py` | 4c T3–4, T8 |
| §12 Sự kiện phần 4 | đã có mã + test | `tram/giao_viec/su_kien.py` | 4a-1 T4 |
| §12 Bảng điểm: "qua lần đầu", "bị trả về" | (16/10) đã có mã + test theo D25–D29, kèm cỡ mẫu và lọc dự án + ngày (D14); số thật chờ chạy thật (bộ giao việc tắt mặc định) | `tram/suy/{bang_diem,diem_giao_viec}.py` | 2d T1, T6 |
| §13 Nối phần 3: `chon_phieu`, `con_hop_le` | đã có mã + test; chỉ nối khi `giao_viec.bat = true`. (17/10) `cac_du_an_that` bỏ dự án `bat_ghi: false` (D31) | `tram/giao_viec/noi_that.py`, `tram/api/phu_thuoc.py` | 4a-2 T9, T13 |
| §19 mục 4 Cổng ADR | đã có mã, mặc định chặn (`adr_hop_le = False`). (16/10, D16) đã chốt: nguồn ADR cho cổng chỉ là decision `blocks` đã đóng (#6), không viết adapter ADR; bead chỉ dựa vào ADR trong văn bản vẫn bị chặn tới khi có decision đã đóng | `tram/giao_viec/{doc_lai,bo}.py` | 4a-2 (G22) |

### Lệch so với spec khi code

- §6.2 bước 4 (4a-2 "Sửa khi code"): mặc định `kill` là `tram.kiem.chay_lenh._kill_nhom`, không phải `os.killpg`. (17/10: tên `_kill_nhom` vẫn giữ làm bí danh — hợp đồng P1 H8; đầu mối kill/wait nay là `tram/kiem/vong_doi.py`.) Lý do: `chay_mot_lenh` luôn kill cả nhóm sau khi lệnh chính thoát, lúc đó nhóm thường đã mất. `_kill_nhom` bỏ qua `ProcessLookupError` và `PermissionError`. Đổi ở `bo.py`, `kiem_lai`, `noi_that.py`; 4b và 4c giữ mặc định này.
- §10 (4a-2 G11, G14, G15): vòng tick tách hai pha, chạy trên hai luồng: `vong_nhanh` không gọi Git, `vong_git` thì có. Mỗi pha giữ khoá `flock` riêng, lịch nhịp cố định 120 giây. Có thêm lệnh `tram giao tick [--thu]`, `tram giao kho-kiem`, `tram giao kiem`.
- §6.4 (4a-2 G13): trước khi vào cột 3, trạm so ref công bố trên remote với `giao.cong_bo`. Lệch thì tạo escalation `nhanh-bi-day`.
- §5.1 điều kiện 7 (4a-2 G5): `phien_ban_quyen` là băm nội dung `vai/quyen/<vai>.json`, thay hằng `"0"`.
- §7.2 (4b G8): xét `bao.xong` của phiếu spec có thêm hai lý do `spec-ngoai-docs` và `ke-hoach-loi`.
- §7.2, §19 mục 6 (4b G23): `*.beads.json` không có `lenh_kiem`. Con chỉ lấy `lenh_kiem_mac_dinh` của dự án; dự án chưa đặt khoá này thì con nằm cột 1 mà không được giao.
- §6.4 mục 4–5 (4c G3, G9): PR mở ở bước tick riêng, nên `bead.vao_cot_3.pr` luôn là `null`. Link PR đi qua sự kiện `pr.mo`.
- §6.5 (4c G6): trạm chỉ tự đóng bead khi head PR đúng bằng `commit_ban_giao` và PR merge bằng merge commit. Squash, rebase hoặc hậu duệ khác thì bead giữ ở cột 3.

Các hợp đồng mới khác xem mục "Cần sửa spec sau" của plan 4a-2, 4b, 4c.

### Cổng còn treo

| Cổng | Việc | Bead |
|---|---|---|
| #4, §16 mục 4 | 4a-2 Task 14: repo nháp 3 bug với bộ giao việc thật (tốn quota) | `bs-8eh.7` |
| S6 | Principal `tram-kiem`, trao quyền, kill lệnh quá hạn dưới principal | `bs-8eh.4` |
| S7 | Kho kiểm từ GitHub, công bố ref, `gh auth`, repo chỉ cho merge commit | `bs-8eh.5` |
| ~~§19 mục 4~~ | ~~Chọn nguồn ADR đã duyệt~~ — **đã chốt D16**, bead `bs-8eh.11` đã đóng | `bs-8eh.11` |
| §16 mục 4 (4b) | Cài skill lên máy A, chạy trọn một feature, spike `bd` cho bead con | `bs-8eh.9` |
| Spike GN (4c) | gitnexus trên trạm chủ; bật GitHub, gitnexus, memory; đo hiệu năng recall và GN | `bs-8eh.10` |
| §7.1 | Skill phỏng vấn trên máy A + API tạo feature trên B (D46/D47) — plan 4d có mã TDD, chưa code; chạy thật theo cổng G6 (4D-4). (17/10) **Đã có mã** (`a02728b`); 4D-4 chờ G6. Bead `bs-urj.10` đã đóng trước 4D-4 — cần xem lại | `bs-urj.10` |
| S6 (17/10) | G3 đo trên OS → 3C-D7 bộ đọc launchd → G4 (plan 3c Task 9). Trước 3C-D7, cổng kiểm lại luôn đóng | `bs-8eh.4` |

**Bỏ theo D58 (18/10/2026, bs-2bd.1.6):** route `POST /api/phieu/kiem` (§7.1, §14 mục 16, hàng §7.1 của bảng trên và dòng "giữ nguyên (4b G5)" ở §7.1) đã bỏ cùng `tram/api/tuyen_feature.py`; từ D46 skill gửi yêu cầu qua `POST /api/feature/yeu-cau`. `doc_phieu` vẫn dùng cho luồng đó. Spec giữ nguyên chữ cũ để lưu vết.

## Đồng bộ quyết định D1–D16 sau review đợt 4

Nguồn có thẩm quyền: [quyết định 15/10](../quyet-dinh/2026-10-15-chot-dot-4.md); không sửa quyết định. Những câu “chưa chốt” bên trên là lịch sử nếu đã có Dn thay thế:

- D1 chọn HR Codex bản sao trên B, sau Task 0; D2 chọn S1 sơ bộ → S6 → S1–S4 dưới principal; D3 thử user riêng mỗi khe trước, giữ nhánh sandbox dự phòng.
- D4 chọn công bố lai, chính thức sau S7. Snapshot có hai adapter nhưng chỉ chọn một nguồn toàn cục; **chưa có mã phối hợp lai trên cùng trạm**. Task 3c R3 bổ sung phần thiếu; không đánh đồng “có cả hai adapter” với “đã hỗ trợ D4”.
- D6 máy A chưa có Tailscale; D7 giữ memory đã cài; D8 chờ QC đạt đối với bàn giao code, spike giữ kiểm-lại đạt; D9/D10 không bỏ escalation máy móc/không cờ nguồn; D11 restart ngay sau 1b-4 T4 hoàn chỉnh.
- D12 đèn từ hook máy A: đã có plan 2e, chưa có mã/hook chạy thật. D13 không tự chọn S1–S8 của bảng điểm; D14 lọc mọi dự án/30 ngày mặc định; D15 cả hai loại tin PR. Mã snapshot chưa có các bổ sung 2d/2e này. **Cập nhật 16/10:** bảng điểm theo D25–D29 và hai tin PR đã có mã (lát 2d); xem "Trạng thái triển khai".
- D16: cổng ADR không còn chờ adapter/nguồn mới. Chỉ decision `blocks` đã đóng; callback ADR giữ False. Các hàng `bs-8eh.11` chờ chọn nguồn bên trên được thay bằng D16 đã chốt.

“Đã có mã + test” chỉ là có module và test trong gói; số pass là lời bàn giao, không phải kết quả review độc lập. Root helper/hoàn tác 3c còn blocker R1/R2; không nâng trạng thái chạy thật dựa vào patch áp được hoặc fixture. Xem `../../REVIEW-CODEX.md` và sổ tay đã sửa đường cài dịch vụ.

