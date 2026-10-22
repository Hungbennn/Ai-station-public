# Phần 3 — Máy thợ + hạn mức

Status: `ĐÃ DUYỆT` — Đại ca duyệt trên chat 13/10/2026, gồm §13 "Em tự quyết" (cả mục 13: chấp nhận rủi ro token khe trong môi trường). Trước đó: nháp Em viết đêm 13/10/2026; qua ba vòng review của Fable và một vòng review độc lập của Codex; Đại ca trả lời câu hỏi 13/10 — §14. Vẫn chờ: cổng trước 3a (§3), spike S1–S8 (§12), hai đề xuất kỹ thuật cuối §14 (chốt sau S6, S7)
Ngày: 2026-10-13 (sửa lần 2 cùng ngày: [quyết định 13/10](../quyet-dinh/2026-10-13-tra-loi-cau-hoi-gop.md) và [phản hồi review Codex](../handovers/2026-10-13-phan-hoi-review-codex.md))
Kiến trúc tổng: [2026-10-12-tram-dieu-phoi-kien-truc.md](2026-10-12-tram-dieu-phoi-kien-truc.md) (§4, §5.3, §5.5, §5.6, Q6, Q7, Q9, Q10, Q11, Q14, Q15)
Đầu vào: [spike hạn mức](../spikes/2026-10-12-han-muc-cli.md) · [spike cờ lệnh bd](../spikes/2026-10-13-bd-cli.md) · thảo luận phần 3 trong [bàn giao 12/10](../handovers/2026-10-12-chuyen-sang-may-b.md)
Phần dùng kết quả: phần 4 (bộ giao việc quyết *giao gì cho ai*), phần 2 lát 2b (Đội ngũ AI + Usage) và 2c (Văn phòng 3D), phần 1b (memory theo phiếu)

Cách đọc: **quyết định đã chốt** ghi kèm số `#`; **đề xuất kỹ thuật** (chưa được Đại ca chốt) ghi rõ "đề xuất"; **cần spike** ghi mã spike; mọi mô tả là **hành vi sẽ triển khai** — chưa có dòng mã nào của phần 3.

## 1. Mục tiêu

Mỗi **khe** = (máy, CLI, tài khoản) chạy được một bước việc do trạm chủ giao, **không người ngồi canh**, và trạm chủ luôn biết:

- khe nào đang sống, đang làm gì, ở lượt giao nào;
- khe nào còn hạn mức, khi nào reset, có đang bị cầu dao ngắt không;
- khi khe chết giữa chừng (Mac gập, CLI crash, hết hạn mức) thì thu hồi được việc mà không mất phần đã làm và không để khe cũ ghi đè.

Phần 3 lo **cách chạy** một bước. Phần 4 lo **chọn** bead, bước, khe và dựng gói ngữ cảnh.

## 2. Tiêu chí thành công

Con số là mặc định đã giữ ngày 13/10 (#21), cấu hình được.

| # | Tiêu chí | Ngưỡng |
|---|---|---|
| H1 | Một khe chạy hai việc cùng lúc (kể cả CLI mồ côi); một bead có hai phiếu hiệu lực | **0** lần |
| H2 | Báo cáo hoặc nhịp tim mang `luot` cũ được chấp nhận; commit của lượt đã hết hiệu lực được công bố lên nhánh `tram/<bead>` | **0** lần. Không coi là đạt chỉ nhờ test HTTP — phải có kịch bản push treo/mất ACK (§15) |
| H3 | Khe mất nhịp tim → việc được thu hồi và sẵn sàng giao lại | ≤ 11 phút sau nhịp tim cuối |
| H4 | Khe nhận việc mới khi một cửa sổ hạn mức **đã biết, còn hiệu lực** ≥ 90% | **0** lần. Hạn mức chưa biết vẫn được nhận theo #15 (§8.2) — H4 không bảo đảm gì cho trường hợp đó |
| H5 | Gặp lỗi hết hạn mức / 429 → khe bị ngắt, không chạy thêm lần nào tới giờ reset | 100% |
| H6 | Việc bị thu hồi giữa chừng → khe khác tiếp tục từ snapshot trạm đã chấp nhận, không làm lại phần đã công bố | đúng trên bộ kịch bản giả lập |
| H7 | `tram tho kiem` báo đỏ đúng khi: thiếu CLI, chưa đăng nhập, không gọi được tram-api, thiếu quyền ghi worktree, **cách ly hỏng** (§7.3) | 100% trên các kịch bản giả |
| H8 | Khe rảnh nhận việc kế (có việc sẵn) | ≤ 60 giây (≤ 2 nhịp tim) |
| H9 | Từ principal thực thi (hoặc `tram-kiem`): đọc được khoá/token của trạm hoặc của khe khác, gọi được API ghi của dashboard, kết nối được DB nghiệp vụ | **0** (kiểm chứng âm trước khi bật 3a) |

## 3. Phạm vi và lát

| Lát | Nội dung | Chạy được khi |
|---|---|---|
| **3a** | Hai khe Claude trên máy B (`B/claude-1`, `B/claude-2`); hạn mức, cầu dao, kho phiếu bền, hợp đồng thuê việc, chạy CLI headless, worktree, `tram bao`, `tram tho kiem`; **dựng trước các hàm dùng chung với phần 4**: `khop_lenh` (`tram/cau_hinh/lenh.py`), danh sách `duong_dan_cam` mặc định + hàm kiểm diff, `kiem_ban_giao(..., can_lenh_kiem)` theo luật chặt của spec 0+1a §4.3, các khoá mới của `du-an/<ten>.yaml` | phần 0+1a xong; tram-api của phần 2a có khung; **cổng trước 3a** bên dưới đều đạt |
| **3b** | Mac thợ từ xa qua Tailscale: `tram chu cap-ma`, `tram tho dang-ky`, launchd trên máy thợ; khe Codex | 3a ổn + Tailscale đăng nhập trên các máy (#5, chưa duyệt) |

**Cổng trước 3a** (không phải câu hỏi — là điều kiện của các quyết định đã chốt):

1. **Cách ly** (#3): tài khoản thực thi tách khỏi tài khoản trạm, và các khe tách nhau, theo §7.3; kiểm chứng âm H9 đạt.
2. **GitHub** (#2): repo có remote GitHub, nhánh chính bật branch protection, quyền push của thợ giới hạn trong `tram/*` theo §6.4; spike S7 đạt.
3. **Spike S1–S4** về Claude headless — **chưa được duyệt chạy** (#5). Plan phần 3 viết được, nhưng các bước adapter hạn mức và file quyền theo vai giữ dạng chờ kết quả spike; không đánh dấu sẵn sàng triển khai bằng fixture giả.
4. **Kho phiếu bền** §6.6.

Ngoài phạm vi: Gemini CLI; tự cài CLI trên máy thợ; tự đăng nhập tài khoản CLI (Đại ca làm tay).

## 4. Khái niệm

| Tên | Nghĩa |
|---|---|
| **Máy** | Một Mac chạy tiến trình quản lý thợ `tram tho chay`. Định danh `may_id` (vd `B`). |
| **Khe** | (máy, CLI, tài khoản). `khe_id = "<may_id>/<ten>"` (vd `B/claude-1`). Mỗi khe một thư mục cấu hình CLI riêng (`CLAUDE_CONFIG_DIR` / `CODEX_HOME`) → một tài khoản, một hạn mức. |
| **Tài khoản trạm** | Tài khoản macOS chạy tram-api, Dolt, kho sự kiện + kho vận hành, memory, giữ khoá API, token nội bộ, credential GitHub của trạm và quyền Đại ca. |
| **Tiến trình quản lý thợ** | `tram tho chay`: giữ token máy và credential push ref tạm; chuẩn bị worktree, khởi chạy CLI, chạy lệnh kiểm, push. |
| **Tiến trình agent/test** | CLI agent và mọi mã repo nó gây ra (test, lint, hook, script). Chạy dưới **principal thực thi của khe**, không có credential nào (§7.3). |
| **Vai ưu tiên** | Danh sách vai khe ưu tiên nhận (vd `[coder]`, `[spec, qc]`). Ưu tiên, không cố định (Q14). |
| **Phiếu giao** | Một bước việc trạm chủ giao cho một khe (§6.1). `giao_id` duy nhất cho mỗi phiếu; giao lại = phiếu mới, `giao_id` mới. |
| **Phiếu hiệu lực** | Phiếu đã cấp, chưa có báo kết thúc được trạm chấp nhận, chưa bị thu hồi. **Một định nghĩa duy nhất** — hàm `phieu_hieu_luc(du_an, bead_id)` và `phieu_hieu_luc_cua_khe(khe_id)` của phần 3 — dùng cho cấp việc, thẻ chắn, phần 4 và bộ chấm 1a (#10). |
| **`luot`** (thẻ chắn) | **Bộ đếm theo bead**, bắt đầu 1, tăng 1 mỗi lần trạm phát phiếu cho bead đó (bất kỳ bước, bất kỳ khe). |
| **`lan`** | Số thứ tự lần chạy CLI trong một phiếu, bắt đầu 1, **tối đa 3** (#13), đồng thời bị giới hạn bởi thời gian/token của phiếu. |
| **Ref tạm / ref công bố** | Đề xuất §6.4: thợ chỉ push ref tạm theo lượt; chỉ trạm cập nhật ref công bố `tram/<bead>`, `tram/spec-<bead>`. |
| **Hợp đồng thuê việc** | Quyền giữ phiếu tới `han_giu`; gia hạn bằng nhịp tim. |

`giao_id`, `luot` và `ma_giao` do **phần 3 (tram-api)** cấp khi phát phiếu; phần 4 chỉ chọn nội dung. `giao_id` dạng `g-<YYYYMMDD>-<số tăng dần>` — **đoán được**, không dùng làm bằng chứng quyền. **`ma_giao`** = 128 bit ngẫu nhiên (base64url) — là **credential**: CLI của phiếu dùng nó gọi dịch vụ của trạm không có token máy (memory MCP — spec 1b).

## 5. Thành phần

```
Máy B
  [tài khoản trạm]
    tram-api (FastAPI, phần 2 dựng khung)  ← phần 3 thêm nhóm /api/tho/*
      ├─ kho phiếu bền: cấp/thu hồi nguyên tử, luot, han_giu, giữ ngân sách   (§6.6)
      ├─ sổ khe: đăng ký, nhịp tim cuối, hạn mức, cầu dao                       (§8, §9)
      ├─ công bố ref: xác minh commit ref tạm → cập nhật tram/<bead> (CAS)      (§6.4)
      └─ gọi phần 4 khi khe rảnh xin việc                                        (§6.2)
  [tài khoản quản lý thợ — có token máy]
    tram tho chay   (một tiến trình / máy, mỗi khe một vòng lặp)
      ├─ nhịp tim 30 s (kiêm xin việc) → chuẩn bị worktree → khởi chạy CLI dưới principal của khe
      ├─ đọc hạn mức từ stream, cầu dao cục bộ, chạy lệnh kiểm, push ref tạm
      └─ hàng đợi báo cáo của phiếu (§7.4)
  [principal thực thi của từng khe — không credential]
    CLI agent + tram bao + mã repo (test/lint/hook)
```

Mã: `tram/tho/` (phía thợ), `tram/api/tho.py` (endpoint), `tram/phieu/` (kho phiếu bền), `tram/han_muc/` (mô hình hạn mức + cầu dao + luật nhận việc), `tram/chay_cli/` (bọc `claude -p`, `codex exec`).

### 5.1 Xác thực nhóm `/api/tho/*`

- **Mọi** lời gọi `/api/tho/*` — kể cả từ máy B — mang `Authorization: Bearer <token máy>`. Lý do: qua `tailscale serve`, yêu cầu từ xa cũng tới tram-api từ `127.0.0.1`, nên địa chỉ nguồn không phân biệt được máy (hành vi này cần kiểm ở spike — spec phần 2 §4).
- Máy B nhận token khi `tram chu cai-dat`; máy khác khi `tram tho dang-ky` (§9.2). Token lưu trong Keychain của **tài khoản quản lý thợ** (dịch vụ `tram-tho-token`), gắn với `may_id`. Mọi `khe_id`/`giao_id` trong thân yêu cầu phải thuộc máy đó, sai → `403`.
- Nhóm `/api/tho/*` **không** dùng danh tính Tailscale và **không** áp kiểm `X-Tram`/`Origin` của dashboard. Ngược lại API dashboard **bỏ qua** Bearer — token máy thợ không bao giờ có quyền của Đại ca.
- **Thu hồi token máy** (`tram chu go-may <may_id>`) vô hiệu mọi phiếu hiệu lực của máy đó (thu hồi như mất nhịp) và mọi `ma_giao` tương ứng.

## 6. Hợp đồng thuê việc (thực hiện §5.5 kiến trúc)

### 6.1 Phiếu giao (trạm chủ → thợ)

Phần 4 dựng nội dung; phần 3 cấp `giao_id`, `luot`, `han_giu`, `ma_giao` và định nghĩa khuôn.

```json
{
  "giao_id": "g-20261013-0042",
  "luot": 3,
  "khe_id": "B/claude-1",
  "du_an": "hr-codex",
  "bead_id": "hr-6xe1",
  "tieu_de": "Sửa cắt UTF-8 tóm tắt hoàn tiền",
  "buoc": "code",
  "vai": "coder",
  "repo": {"kho": "~/tram/kho/hr-codex", "nhanh": "tram/hr-6xe1", "ref_tam": null,
           "cha": "a1b2c3d", "nhanh_chinh": "main"},
  "goi_ngu_canh": "…markdown năm lớp, phần 4 dựng…",
  "ngan_sach": {"so_lan_chay": 3, "phut": 90, "token_ra": 200000},
  "lenh_kiem": ["php artisan test --filter TomTatHoanTien"],
  "lenh_cho_phep": ["php artisan test --filter *", "npm run test:unit"],
  "can_lenh_kiem": true,
  "can_moi_truong_kiem": true,
  "tieu_chi": ["Tên kết thúc 'ỷ' không mất byte", "php artisan test --filter TomTatHoanTien pass"],
  "han_giu": "2026-10-13T03:10:00Z",
  "ma_giao": "q3Xv…(22 ký tự)",
  "khoa_chong_trung": "sha256:…"
}
```

- `repo.nhanh` (ref công bố) luôn bắt đầu bằng `tram/` (Q7) — `tram/<bead>` cho code/qc, `tram/spec-<bead>` cho spec. `repo.ref_tam` hiện để null; hai phía tính `tram/luot/<bead_id>/<luot>` (3a-2 G4). Nếu sau này có giá trị thì phải khớp giá trị tính; ref công bố vẫn theo phương án §14 chưa chốt. Thợ từ chối phiếu có nhánh ngoài `tram/`.
- `cha`: commit thợ bắt đầu từ — luôn là SHA trạm đã chấp nhận (§6.5).
- `lenh_kiem`: **lệnh bắt buộc** do trạm (phần 4) chọn; tất cả phải chạy và pass khi `can_lenh_kiem = true` (§7.5). `lenh_cho_phep`: mẫu lệnh do phần 4 chép từ dự án vào phiếu `code`/`qc`; phiếu spike và `spec` có danh sách **rỗng** (phần 4 §6.1). Khớp lệnh bằng hàm chung `khop_lenh` (luật đầy đủ ở spec phần 4 §6.2): tách token bằng `shlex`, `*` thay đúng một token không chứa ký tự shell, không bắt đầu bằng `-`; chạy bằng danh sách đối số, **không qua shell**. "Không qua shell" không có nghĩa là "không chạy mã không tin cậy" — mã test vẫn là mã repo, nên chạy trong môi trường cách ly §7.3.
- `can_moi_truong_kiem`: phiếu có chạy mã dự án (code, qc) thì `true`; phiếu chỉ ghi tài liệu (spec, spike tài liệu) thì `false` (§7.1).
- `tieu_chi`: tiêu chí nghiệm thu đã tách dòng và chuẩn hoá (phần 4 §6.1).
- `goi_ngu_canh` thợ ghi ra `.tram/goi.md` trong worktree (thư mục `.tram/` nằm trong `.git/info/exclude`, không commit) và đưa vào CLI qua stdin.
- **Phiếu chứa credential** (`ma_giao`): chỉ trao qua nhịp tim đã xác thực cho tiến trình quản lý thợ; không ghi toàn phiếu vào sự kiện, log hay dashboard; che `ma_giao` trong header, tên file và thông báo lỗi trước khi lưu hoặc hiển thị.

### 6.2 Nhịp tim kiêm xin việc

Một endpoint cho cả hai: `POST /api/tho/nhip {khe_id, giao_id|null, luot|null, buoc_tho, han_muc}`, mỗi **30 giây**, kể cả khi rảnh. `buoc_tho` ∈ `ranh | chuan_bi | chay | kiem | push | dung`.

**Khe rảnh** (`giao_id: null`) → trả `{tiep_tuc: true, phieu: <phiếu> | null}`. Trạm chỉ hỏi phần 4 khi **đủ cả** điều kiện của phần 3 (luật cứng):

1. Khe đang **bật**: sự kiện mới nhất trong `khe.dang_ky`, `khe.bat`, `khe.tat` của khe — `khe.tat` → tắt; hai loại kia → bật. Lát 3a chưa có dashboard 2b: `tram tho tat-khe <khe>` / `bat-khe` ghi hai sự kiện này.
2. Khe không có phiếu hiệu lực (`phieu_hieu_luc_cua_khe`).
3. Cầu dao của khe **đóng** (§8.3).
4. Trạm không `estop`. Estop chỉ chặn **phát phiếu**; các báo cáo/push của phiếu đang hiệu lực vẫn được nhận để dừng mềm hoàn tất.
5. Không cửa sổ hạn mức **đã biết, còn hiệu lực** nào của khe ≥ 90% (luật 1 của §8.2) — phòng vệ hai lớp, không phụ thuộc phần 4.
6. Trần lần chạy giờ/ngày của khe còn chỗ (§8.3).

Phần 4 chọn bead/bước cho khe (`chon_phieu`), gọi `duoc_nhan(han_muc, uu_tien)` và áp Q14. Phần 3 **cấp phiếu trong một giao dịch** của kho phiếu (§6.6) — mọi điều kiện trên và điều kiện của phần 4 được kiểm lại trong giao dịch đó; hai nhịp tim đến cùng lúc không thể cùng nhận một bead.

**Khe đang giữ phiếu** → trả `{tiep_tuc: true, han_giu}` hoặc `{tiep_tuc: false, ly_do}` (§6.3). Mỗi nhịp tim hợp lệ đẩy `han_giu = bây giờ + 10 phút`. Nhịp tim **không** kéo dài trần thời gian của phiếu hay hạn chót dừng mềm (§7.6).

### 6.3 Thẻ chắn `luot`, phiếu hiệu lực, dừng, thu hồi

**Thẻ chắn.** Mọi lời gọi `/api/tho/*` liên quan phiếu mang `giao_id` + `luot`. Trạm từ chối `409 {ly_do: "luot-cu"}` khi `giao_id` không phải phiếu hiệu lực của bead **hoặc** `luot` ≠ `luot` hiện hành của bead; ghi `tho.tu_choi {khe_id, giao_id, bead_id, luot_gui, luot_dung}` (H2).

**Phiếu hết hiệu lực** khi trạm chấp nhận một báo kết thúc (`bao.xong`, `bao.bi`, `bao.het_han_muc`) hoặc thu hồi (`giao.thu_hoi`). Ngay trong giao dịch đó, trạm ghi **yêu cầu chấm lại bền** cho bead (spec 0+1a §5.6) và **công việc xử lý bền** cho phần 4 (§6.6). Sự kiện `giao.ket_thuc` của phần 4 chỉ là xác nhận đã xử lý pipeline — **không** phải định nghĩa thứ hai của hiệu lực.

**Hai kiểu dừng** (trả trong nhịp tim `tiep_tuc: false`):

| `ly_do` | Kiểu | Thợ làm |
|---|---|---|
| `luot-cu`, `thu-hoi` | **dừng cứng** | SIGTERM nhóm tiến trình CLI và test, 10 giây, SIGKILL; không push, không báo |
| `khe-tat`, `estop`, `cau-dao`, `can-hoi` | **dừng mềm** (#14; `can-hoi` khi phần 4 dừng phiếu sau câu hỏi của agent — phần 4 §9) | SIGTERM → chờ thoát (10 giây, rồi SIGKILL) → **rồi** commit WIP → push ref tạm → báo `bi {ly_do}` kèm bàn giao tạm (§7.7); trạm thu hồi với snapshot. Có hạn chót §7.6 |

**Bộ canh hợp đồng** (trong tram-api, mỗi 60 giây):

- nhịp tim cuối của khe > 90 giây (khe vừa đăng ký mà chưa có nhịp nào cũng tính) → `khe.mat_ket_noi`; nhịp tim kế tiếp → `khe.ket_noi`;
- phiếu quá `han_giu` (10 phút sau nhịp cuối) → thu hồi (`giao.thu_hoi {giao_id, luot, ly_do: "mat-nhip"}`) trong một giao dịch của kho phiếu; phần 4 quyết giao lại cho ai.

Khe có thể `mat_ket_noi` mà vẫn giữ phiếu thêm ~8,5 phút — cố ý, để Mac ngủ ngắn không mất việc.

### 6.4 Push và công bố commit

GitHub không biết `luot`. Kiểm thẻ chắn trước khi push (`xin-push`) và `--force-with-lease` chỉ **giảm xung đột**, không chứng minh được rằng push của một lượt đã hết hiệu lực bị từ chối: thợ có thể bắt đầu push hợp lệ rồi treo mạng; phiếu bị thu hồi; push cũ hoàn tất sau đó và vẫn thoả SHA mong đợi. Ngược lại push thành công nhưng mất phản hồi làm snapshot bỏ sót commit.

**Đề xuất (cần spike S7, chưa phải quyết định):** tách ref tạm và ref công bố.

1. Agent chỉ `git commit` trong worktree (quyền vai cấm push).
2. Thợ push commit của mình lên **ref tạm của lượt** `repo.ref_tam` (vd `tram/luot/<bead>/<luot>`), không bao giờ lên ref công bố. Credential của thợ chỉ được push trong `tram/luot/*`.
3. Thợ báo `POST /api/tho/da-push {giao_id, luot, commit, request_id}`.
4. Trạm, trong cùng cơ chế tuần tự hoá với thu hồi và phát lượt mới (§6.6): kiểm phiếu còn hiệu lực và `luot` khớp → `git fetch` ref tạm → kiểm commit là hậu duệ của ref công bố hiện tại (hoặc của `cha`) → cập nhật ref công bố `repo.nhanh` bằng **compare-and-swap** (`--force-with-lease=<nhanh>:<sha công bố hiện tại>`, dùng credential của tài khoản trạm) → ghi `giao.cong_bo {bead_id, luot, commit, ref}`.
5. Push ref tạm trễ (sau thu hồi) chỉ đổi ref tạm của lượt cũ — không đổi ref công bố, snapshot hay commit đã duyệt.
6. Mất phản hồi: thợ gửi lại `da-push` với cùng `request_id`; trạm đối soát ref remote theo SHA trước khi làm lại.
7. Mọi bước sau (snapshot, kiểm lại, QC, PR, phê duyệt) dùng **SHA trạm đã công bố**, không suy từ HEAD remote đang di động.
8. Trạm xoá ref tạm của lượt khi lượt kết thúc và đã công bố (hoặc bỏ).

**Phương án lùi nếu GitHub không giới hạn được quyền push theo mẫu ref** (S7): thợ không có credential GitHub; trạm `git fetch` trực tiếp từ kho cục bộ của thợ (đường dẫn file, tài khoản trạm có quyền đọc) rồi tự push ref công bố — dùng được cho máy B (3a); Mac thợ từ xa (3b) khi đó cần cơ chế khác, quyết sau. Lựa chọn giữa hai phương án là **đề xuất cần Đại ca chốt** sau S7.

### 6.5 Snapshot khi thu hồi

Khi phiếu bị thu hồi hoặc kết thúc không phải `xong`, snapshot = SHA mới nhất trong `giao.cong_bo` của bead (hoặc `cha` của phiếu nếu chưa công bố gì), ghi `giao.snapshot {bead_id, luot, commit}`. Phiếu giao lại có `luot` mới và `cha = commit snapshot`. Bàn giao tạm gần nhất (trong `bao.moc` hoặc `bao.bi`) được phần 4 đưa vào lớp 4 của gói ngữ cảnh. Phần 3 chỉ thực thi `ngan_sach` của **một phiếu**; ngân sách **tổng** theo bead là của phần 4.

### 6.6 Kho phiếu bền và tính nguyên tử

Kho vận hành nằm trong `~/.tram/su-kien.db` (tài khoản trạm, WAL), bảng riêng ngoài nhật ký sự kiện. Không coi một giao dịch SQLite bao trùm được Beads hay Git.

- **Cấp phiếu = một giao dịch SQLite** tuần tự hoá: kiểm điều kiện §6.2 + của phần 4 → ghi bản ghi **giữ trước ngân sách** gắn phiếu → giữ khe → tăng `luot` theo `(du_an, bead_id)` → lưu **phiếu đầy đủ** (kể cả `ma_giao`) → ghi `giao.nhan`. Ràng buộc trong kho: tối đa một phiếu hiệu lực cho mỗi bead và cho mỗi khe (chỉ mục duy nhất có điều kiện).
- **Khởi động lại** tram-api: phiếu hiệu lực, `ma_giao`, giữ trước ngân sách đọc lại từ kho; không dựng lại từ sự kiện.
- **Báo cáo idempotent:** mọi báo của thợ (`bao`, `su-kien`, `da-push`) có `request_id` do thợ sinh và lưu bền phía thợ trước khi gửi. Cùng `request_id` + cùng nội dung → trả kết quả cũ; cùng `request_id` khác nội dung → 409. Báo kết thúc được chấp nhận **tối đa một lần**.
- **Công việc chờ xử lý bền:** chấp nhận báo kết thúc hoặc thu hồi → trong cùng giao dịch ghi một dòng "chờ phần 4 xử lý" và "yêu cầu chấm lại 1a"; phần 4 lấy và đánh dấu xong sau khi xử lý; restart giữa chừng thì làm lại được.
- **Thao tác ghi Beads/Git** (claim, tạo escalation, tạo bead con, công bố ref): ghi **ID thao tác bền** trước khi gọi; nếu kết quả không rõ (crash, timeout) thì **đối soát** trước khi gọi lại — với `bd create` tìm bead mang dấu ID thao tác trong mô tả; với Git so SHA của ref remote. Không đoán "lần trước đã thất bại".
- **Ca kiểm:** hai nhịp tim xin việc đồng thời cho cùng bead; HTTP gửi lại sau khi mất phản hồi; restart sau `bd --claim`, sau `bd create`, sau `bao.xong`; phát lại phải cho cùng kết quả và không đếm ngân sách hai lần.

## 7. Chạy một phiếu trên máy thợ

### 7.1 Kho và worktree

- Mỗi dự án một bản clone trên máy thợ: `~/tram/kho/<du-an>` (thuộc tài khoản quản lý thợ). Lát 3a: Đại ca clone tay một lần. Danh sách dự án lấy từ `GET /api/du-an` (phần 2a). Kho **không** được có `.env` thật.
- Mỗi phiếu chạy trong worktree `~/tram/worktrees/<du-an>/<repo.nhanh bỏ tiền tố tram/>`; principal thực thi của khe chỉ ghi được worktree của phiếu nó đang chạy.
- Trước mỗi phiếu, tiến trình quản lý (không phải agent — agent bị cấm mạng) chạy `git fetch origin` với **hook Git tắt** (`core.hooksPath` trỏ thư mục rỗng của trạm). Worktree đã có:
  - HEAD = `cha`, sạch → dùng lại;
  - có thay đổi chưa commit → commit thành `wip: rác lượt trước` lên nhánh cục bộ `rac/<bead>-<thời điểm>` (không push), rồi `git reset --hard <cha>`; sự kiện `chay.don_rac`;
  - HEAD khác `cha`, sạch: HEAD không phải tổ tiên của `cha` → tạo nhánh `rac/<bead>-<thời điểm>` trỏ HEAD rồi `git reset --hard <cha>`, `chay.don_rac`; HEAD là tổ tiên của `cha` → `git reset --hard <cha>`.
  - Khi `luot` đổi: xoá `.tram/tien-do.md`, `.tram/goi.md`, hàng đợi cũ.
- **Môi trường kiểm** (bước riêng, sau khi worktree ở đúng `cha`), chỉ khi `can_moi_truong_kiem = true` (phiếu code, qc): chép `moi_truong_kiem.file` → `<worktree>/<moi_truong_kiem.dich>` (khoá trong `du-an/<ten>.yaml`, Đại ca đặt tay, trỏ DB test). Đích là đường dẫn tương đối, không `..`, và không được thoát worktree qua symlink (kiểm đường dẫn thật sau khi phân giải). Thiếu khoá → không chạy phiếu, báo `bi {ly_do: "thieu-moi-truong-kiem"}`. Phiếu `spec` và spike chỉ ghi tài liệu không cần môi trường kiểm; nếu phiếu đó muốn chạy mã dự án thì phải được cấp như phiếu code — agent không tự bỏ cổng này.
- Dọn: thấy `bead.dong {du_an, bead_id}` (phần 4 phát) → xoá worktree và nhánh cục bộ.

### 7.2 Chạy CLI headless

Mỗi **lần chạy** là một tiến trình con dưới principal thực thi của khe, trong **nhóm tiến trình riêng**; pid ghi vào `~/.tram/tho/<khe>/dang-chay.pid` (thư mục của tiến trình quản lý); worktree có khoá `.tram/khoa` (pid + `giao_id`). Khi `tram tho chay` khởi động: pid còn sống → kill cả nhóm, ghi `chay.xong {ket_thuc: "mo-coi"}`. Khoá worktree còn và pid sống → không chạy (H1).

**Trước mỗi lần chạy** (kể cả lần 2, 3 trong một phiếu) kiểm lại: `lan ≤ ngan_sach.so_lan_chay` (≤ 3, #13) và trần ngân sách phiếu, trần lần chạy giờ/ngày của khe (§8.3), cầu dao, hạn mức đã biết.

Môi trường tối thiểu của CLI:

| Biến | Giá trị |
|---|---|
| `CLAUDE_CONFIG_DIR` / `CODEX_HOME` | thư mục của khe, thuộc principal thực thi của khe |
| `TRAM_GIAO_ID`, `TRAM_HANG_DOI` | để `tram bao` làm việc (§7.4) |
| `TRAM_MA_GIAO`, `TRAM_NHO_URL` | chỉ khi memory MCP (spec 1b-2) đã bật; 3a chưa có 1b-2 thì không đặt, không truyền URL giả |
| `PATH` | `tram`, `git`, công cụ dự án |

Môi trường của CLI **không** có token máy hay credential push.

Lệnh (cờ chính xác chốt ở spike S4):

- Claude: `claude -p --output-format stream-json --verbose --settings <file quyền theo vai>`; prompt qua stdin từ `.tram/goi.md`. **Không** dùng chế độ bỏ qua quyền (Q6); thao tác ngoài danh sách cho phép bị từ chối thay vì hỏi, agent phải `tram bao --can-hoi`.
- Codex: `codex exec --json` với sandbox ghi trong worktree; sự kiện, token, hạn mức của Codex có bộ chuẩn hoá riêng, không dùng parser của Claude; chi tiết ở lát 3b (spike S5).

> **Ghi chú 16/10, D44:** đồng bộ theo mã lát 3b (plan 3b G15, G16). Cờ theo hiểu biết hiện tại, **chưa chạy thật** — chờ S5.
>
> - **Lệnh Codex** (`lenh_codex` trong `tram/chay_cli/codex/bo.py`): `codex exec --json --cd <worktree> --sandbox workspace-write -c approval_policy="never" -c sandbox_workspace_write.network_access=false --add-dir <thư mục phiếu> -`. Prompt qua stdin.
> - Chỉ thêm một chỗ ghi ngoài worktree: thư mục phiếu (hàng đợi `tram bao`). Không mở git common-dir (chờ lời giải S6). Đường ghi phải tuyệt đối, không chứa `..`, không là `/` hay thư mục home. Không bao giờ dùng cờ bỏ qua sandbox/quyền (Q6).
> - Môi trường giống bảng trên; vòng thợ đặt `CODEX_HOME` thay cho `CLAUDE_CONFIG_DIR` (`tram/tho/mot_lan.py`, `BoCodex.bien_thu_muc`).
> - **Codex không có lớp quyền theo vai.** Bảng "File quyền theo vai" dưới đây chỉ áp cho Claude. `vai`, `lenh_cho_phep` của phiếu không vào lệnh Codex. Lớp bổ sung là prompt vai + kiểm diff của phần 4; hàng rào thật là sandbox + principal của khe (S6).
> - **Token Codex** (`DocLuongCodex` trong `tram/chay_cli/codex/luong.py`): cộng qua mọi `turn.completed`. `input_tokens` của Codex gồm phần cache, nên `token_vao = input_tokens − cached_input_tokens`, `token_cache_doc = cached_input_tokens`, `token_ra = output_tokens`, `token_cache_ghi = 0`, `mo_hinh = null`. Trường thiếu/sai đếm 0.
> - Chạy trong nhóm tiến trình riêng; stdout + stderr gộp, che `ma_giao` từng dòng trước khi ghi log và băm `digest_log` (`tram/chay_cli/codex/chay.py`).

**File quyền theo vai** `vai/quyen/<vai>.json`, có phiên bản; thợ sinh file quyền **của phiếu** từ mẫu này cộng `lenh_cho_phep` của phiếu, đặt trong thư mục phiếu — là **lớp bổ sung**, không phải hàng rào bảo mật (§7.3):

| Vai | Cho phép | Cấm |
|---|---|---|
| spec | đọc repo, ghi `docs/**`, `git add/commit`, `tram bao` | sửa mã nguồn, cài gói, mạng, chạy mã dự án |
| coder | đọc/ghi repo, chạy lệnh khớp `lenh_cho_phep` **của phiếu** (phiếu spike: rỗng — không chạy lệnh nào), `git add/commit`, `tram bao` | `git push`, `bd`, migrate DB thật, lệnh mạng, ghi ngoài worktree |
| qc | đọc repo, chạy lệnh khớp `lenh_cho_phep` **của phiếu**, ghi `docs/handovers/**`, `tram bao` | sửa mã nguồn (QC chỉ báo, không sửa — phần 4 §6.3 kiểm lại bằng diff) |

### 7.3 Cách ly (thực hiện #3 — điều kiện trước 3a)

Quyết định #3: CLI agent và mọi mã repo chạy dưới tài khoản tách khỏi tài khoản trạm, **trước khi bật 3a**. Hợp đồng:

1. **Ba nhóm quyền.** Tài khoản trạm giữ tram-api, Dolt, kho sự kiện/vận hành, memory, khoá API, token nội bộ, credential GitHub của trạm và quyền Đại ca. Tài khoản quản lý thợ giữ token máy, credential push ref tạm, cấu hình, log, hàng đợi của các khe. Principal thực thi của từng khe không giữ credential nào. Không cấp quyền đọc/ghi các kho của tài khoản trạm cho hai nhóm còn lại.
2. **Khe tách khe.** Tiến trình agent/test của một khe không đọc được Keychain, file cấu hình, log, hàng đợi, môi trường của tiến trình quản lý hay của khe khác. Giới hạn bằng **quyền truy cập thật** (tài khoản/ACL/sandbox của hệ điều hành) — không dựa vào tên file chứa `ma_giao` hay PATH. Cơ chế cụ thể — một user macOS cho mỗi khe, hay một user thực thi chung cộng sandbox mỗi khe — là **đề xuất**, plan chọn sau spike S6.
3. **Quyền CLI là lớp bổ sung.** Danh sách cấm trong file quyền theo vai, việc `tram` chỉ nhận lệnh con `bao` khi có `TRAM_GIAO_ID`, việc cấm `bd`/`security` — đều không phải hàng rào cho mã test, git hook hay executable do repo cung cấp.
4. **Dashboard và memory.** API ghi của dashboard và MCP phiên tay của memory không nhận được yêu cầu từ principal thực thi hay `tram-kiem` (spec phần 2 §4 mục 2b; spec 1b §9.3).
5. **Lệnh kiểm** của thợ (§7.5) chạy dưới principal thực thi của khe. Lệnh kiểm lại của trạm (phần 4 §6.2) chạy dưới **principal kiểm lại riêng của trạm** (`tram-kiem`), chịu cùng hợp đồng như principal thực thi: không credential, không đọc kho của tài khoản trạm, không đọc hàng đợi, cấu hình hay log của khe nào. Worktree kiểm do tài khoản trạm tạo, chép môi trường kiểm vào, rồi mới trao quyền ghi cho `tram-kiem`; sau đó tài khoản trạm chỉ đọc log và mã thoát. Trạm không bao giờ chạy mã repo với quyền của tram-api. Tên và cách tạo `tram-kiem` là **đề xuất**, chốt cùng S6 (§13 mục 12).
6. **Log** đầy đủ của CLI và lệnh kiểm có thể chứa nội dung `.env` → thuộc tài khoản quản lý thợ, giữ 30 ngày, không đưa lên dashboard, không rời máy thợ; che `ma_giao`.
7. **Kiểm chứng âm (H9), chạy trước khi bật 3a:** từ principal thực thi của khe A, một test giả cố: đọc khoá nội bộ/token máy; đọc/thay hàng đợi của khe B; gọi `security`; gọi `tram` sau khi xoá `TRAM_GIAO_ID`; chạy git hook; gọi API Duyệt của dashboard với header danh tính giả; kết nối DB nghiệp vụ — tất cả phải bị chặn; test hợp lệ vẫn chạy được với DB test. Cùng bộ kiểm chạy lại từ `tram-kiem` (mục 5; thay "hàng đợi của khe B" bằng hàng đợi của mọi khe).

### 7.4 `tram bao` (agent gọi từ trong phiên — thực hiện §5.3 kiến trúc)

`tram bao` chạy **đồng bộ** trong lệnh Bash của agent, dưới principal thực thi, và **không gọi mạng**:

1. **điền** `nhanh` (nhánh hiện tại), `commit: null` (cập nhật sau bước 2) và `luot = 0` (chỗ giữ — thợ ghi đè) vào khối agent viết; rồi kiểm khối ở mức **cấu trúc**: đúng schema phần 0 §4.3 (`extra=forbid`; `file_ban_giao` agent phải điền — bàn giao `tam` cho phép rỗng), ≤ 64 KB, luật của bàn giao `tam`. Luật `chinh-thuc` **không** kiểm ở đây vì `lenh_kiem[]` do thợ điền sau;
2. `git add -A && git commit -m "<loại>: …"` nếu có thay đổi (hook Git tắt);
3. ghi một dòng JSON `{loai, noi_dung, ban_giao?, commit}` vào hàng đợi `$TRAM_HANG_DOI` — file trong thư mục của phiếu mà chỉ principal của khe này ghi được và tiến trình quản lý đọc được.

Tiến trình quản lý chỉ đọc hàng đợi của phiếu nó đang giữ, xoá khi phiếu kết thúc. Thấy dòng `can_hoi` ở phiếu không có `pham_vi_doc_lap` (mọi phiếu ở 4a — phần 4 §9) → gửi `bao.can_hoi` rồi **dừng mềm ngay**, không chờ nhịp tim kế; trạm vẫn trả `{tiep_tuc: false, ly_do: "can-hoi"}` ở nhịp tim sau để hai bên đồng bộ. Với mỗi dòng: **kiểm lại** cấu trúc (agent có thể ghi thẳng vào file), **tự gắn** `khe_id`, `giao_id`, `luot` của phiếu (bỏ mọi id agent ghi), sinh `request_id`, làm phần việc của mình (push ref tạm, lệnh kiểm), rồi gửi `POST /api/tho/bao {khe_id, giao_id, luot, loai, noi_dung, ban_giao?, commit, request_id}`; trạm kiểm cấu trúc lần nữa.

**Thấy `xong`** → thợ chờ CLI thoát (tối đa 60 giây, rồi SIGTERM), **bỏ qua** mọi dòng ghi sau `xong`; worktree phải sạch (còn thay đổi → commit `wip: sau xong`); rồi mới chạy lệnh kiểm (§7.5) và push.

| Lệnh | Ý nghĩa | Thợ làm tiếp | Trạm ghi |
|---|---|---|---|
| `tram bao --moc [--ban-giao <file>]` | xong một mốc | push ref tạm (§6.4) | `bao.moc` (bàn giao tạm trong trường `ban_giao`; ghi vào notes bead là việc phần 4) |
| `tram bao --can-hoi --loai <can_quyet_dinh\|thao_tac_nguy_hiem> "<câu hỏi>"` | cần Đại ca | — | `bao.can_hoi {loai_hoi}`; phần 4 tạo escalation (phần 4 §9). Ở 4a mọi phiếu chưa có `pham_vi_doc_lap` nên thợ **dừng mềm ngay** (§7.4, §7.6) |
| `tram bao --bi "<vì sao>"` | không đi tiếp được | push ref tạm, dừng phiếu | `bao.bi {ly_do: "agent", noi_dung}`; phần 4 tạo escalation |
| `tram bao --xong --ban-giao <file>` | xong bước | chờ CLI thoát, chạy lệnh kiểm, push, rồi gửi `bao.xong` | `bao.xong`; phần 4 kiểm tiếp |

Sự kiện chạy CLI đi qua `POST /api/tho/su-kien {khe_id, giao_id, luot, loai, du_lieu, request_id}` — chỉ nhận `chay.bat_dau`, `chay.xong`, `chay.don_rac`, loại khác `400`.

### 7.5 Lệnh kiểm do thợ chạy

Khi agent `--xong` và CLI đã thoát:

1. **Đường dẫn cấm trước tiên.** Kiểm diff từ gốc nhánh có chạm `duong_dan_cam` không (hàm chung của phần 4 §6.2 bước 0) — chạm thì **không chạy lệnh nào**, gửi `bao.xong` kèm `loi_ban_giao`.
2. **Lệnh bắt buộc.** Khi `can_lenh_kiem = true`: chạy **mọi** lệnh trong `lenh_kiem` của phiếu, dưới principal thực thi, không qua shell, hook tắt, mỗi lệnh có timeout và kill cả nhóm tiến trình khi quá hạn. Lệnh bắt buộc không khớp `lenh_cho_phep`, lỗi khởi chạy, timeout → coi là **fail**. Lệnh agent đề xuất thêm (khớp `lenh_cho_phep`) được chạy và ghi lại, nhưng **không thay** được lệnh bắt buộc; lệnh đề xuất không khớp bị bỏ và ghi vào `vuong_mac`.
3. **Ghi đè kết quả.** Log lưu `~/.tram/log/kiem/<giao_id>-<luot>-<i>.log`. Thợ **ghi đè** `lenh_kiem[]` của khối bàn giao bằng kết quả thật (`lenh`, `ket_qua`, `tom_tat` = 3 dòng cuối, `digest_log` = sha256 log). Agent điền: `doi_chieu_nghiem_thu`, `quyet_dinh`, `huong_da_bo`, `vuong_mac`, `buoc_tiep`, `cau_hoi_mo`, `thay_doi_vung_nhay_cam`, `file_ban_giao`. Thợ điền `luot` và **ghi đè `commit`** trong khối gửi kèm `bao.xong` bằng HEAD cuối của worktree (sau commit `wip: sau xong` nếu có) — chính commit sẽ push lên ref tạm; `tram bao` điền `nhanh`.
4. **Luật `chinh-thuc`** của phần 0 (§4.3, bản chặt 13/10) với `can_lenh_kiem` và `tieu_chi` của phiếu: mọi tiêu chí đúng một lần, có bằng chứng; với phiếu `code`/spike mọi tiêu chí `dat: true`; với phiếu `qc` áp **bản QC** của §4.3 — `dat: false` không là lỗi khi khối `<!-- qc -->` kết luận `tra_ve`; mọi lệnh bắt buộc pass. Trượt → **vẫn** gửi `bao.xong` nguyên kết quả kèm `loi_ban_giao[]` (trong thân `bao`, không trong khối bàn giao); phần 4 quyết. Thợ không tự đổi thành `bi`.

Phần 4 vẫn tự chạy lại lệnh bắt buộc trong môi trường cách ly trước khi cho vào cột 3 (phần 4 §6.2).

### 7.6 Kết thúc phiếu, hạn chót, hạch toán

**Luật chung:** mọi kết thúc **trừ** `xong` và dừng cứng → commit WIP → push ref tạm → dựng bàn giao tạm (§7.7) nếu agent chưa gửi → báo.

| Kết thúc | Tiếp theo |
|---|---|
| Agent `--xong`, lệnh kiểm xong, CLI thoát | `bao.xong` |
| Agent `--bi` | `bao.bi {ly_do: "agent", noi_dung}` |
| CLI thoát mà chưa `--xong`/`--bi` | còn ngân sách phiếu và `lan < ngan_sach.so_lan_chay` (≤ 3, #13) → lần chạy mới (`lan + 1`) với gói + bàn giao tạm gần nhất; hết → `bao.bi {ly_do: "het-ngan-sach"}` |
| Vượt `token_ra` hoặc trần thời gian của phiếu | dừng CLI → `bao.bi {ly_do: "het-ngan-sach"}` |
| Thợ tự phát hiện hết hạn mức giữa chừng | dừng mềm → `bao.het_han_muc`; cầu dao cục bộ ngắt |
| Dừng mềm — do trạm (`khe-tat`, `estop`, `cau-dao`) hoặc do thợ tự dừng sau `can_hoi` (`can-hoi`) | `bao.bi {ly_do}` |
| Thiếu `moi_truong_kiem` khi phiếu cần (§7.1) | `bao.bi {ly_do: "thieu-moi-truong-kiem"}`, không chạy CLI |
| Dừng cứng (`luot-cu`, `thu-hoi`) | không push, không báo |

Một phiếu chỉ có **một** báo kết thúc được chấp nhận (§6.6).

**Hạn chót và hạch toán:**

- **Trần thời gian của phiếu** (`ngan_sach.phut`) tính **wall-clock** từ lúc nhận phiếu, gồm chuẩn bị worktree, các lần chạy CLI, lệnh kiểm và push. Mỗi khâu có timeout riêng và cách kill cả nhóm tiến trình (test sinh tiến trình con giữ file vẫn bị kill).
- **Dừng mềm có hạn chót riêng** (mặc định 3 phút, cấu hình được — Đại ca chốt 13/10): hết hạn chót mà chưa push được thì giữ WIP cục bộ trên nhánh `rac/`, báo snapshot trạm đã công bố gần nhất, **không** ghi "đã lưu toàn bộ".
- Nhịp tim không kéo dài trần thời gian phiếu hay hạn chót dừng mềm.
- **Đếm lần chạy từ `chay.bat_dau`** (duy nhất theo `request_id`). Thiếu `chay.xong` (thợ chết trước khi gửi) thì khi thu hồi trạm quyết toán thời gian theo thời gian đã biết (tới nhịp tim cuối) cộng phần giữ trước — không tính bằng 0.
- Ca kiểm: mất sự kiện kết thúc; gửi lại `chay.bat_dau`; push treo khi estop; test sinh tiến trình con giữ file; đồng hồ máy thợ đổi.

### 7.7 Bàn giao tạm do thợ tự dựng

CLI chết thì không tự viết bàn giao được. Thợ dựng khối `loai: "tam"` từ: nhánh, commit vừa push ref tạm, `buoc_tiep = ["Tiếp tục bước <buoc> của <bead>; đọc .tram/tien-do.md và diff so với <cha>"]`, và nội dung `.tram/tien-do.md` mà prompt vai yêu cầu agent cập nhật ở mỗi mốc. Hook `PreCompact` của Claude Code (khai trong file quyền theo vai) gọi `tram bao --moc` để có snapshot trước khi nén ngữ cảnh — **cần spike S8** (hook có chạy đúng lúc, có lặp hay bị kill không); luôn có đường dự phòng là bàn giao tạm thợ tự dựng.

### 7.8 Theo dõi trong lúc chạy

Thợ đọc stream JSON của CLI từng dòng: cập nhật hạn mức từ `rate_limit_event` (Claude, §8.1); đếm token ra, so ngân sách phiếu; phát hiện hết hạn mức (`rejected` hoặc mẫu chữ của nguồn lùi) → cầu dao; log đầy đủ ghi `~/.tram/log/chay/<giao_id>-<luot>-<lan>.jsonl`, digest sha256 gửi trong `chay.xong`.

## 8. Hạn mức (thực hiện §5.6 kiến trúc)

### 8.1 Mô hình và nguồn

Trạng thái hạn mức của một khe, theo **từng cửa sổ**:

```json
{"khe_id": "B/claude-1",
 "cua_so": [{"loai": "5h", "trang_thai": "biet", "phan_tram": 62.0, "reset_luc": "2026-10-13T05:00:00Z",
             "doc_luc": "2026-10-13T02:41:10Z", "het_hieu_luc": "2026-10-13T05:00:00Z"},
            {"loai": "tuan", "trang_thai": "chua_biet", "doc_luc": null}],
 "nguon": "stream|app-server|log|regex"}
```

- **Đã biết / chưa biết.** Một cửa sổ là `biet` khi có số đo còn hiệu lực. Qua `reset_luc`, hoặc quá tuổi tối đa (mặc định 6 giờ kể từ `doc_luc`, cấu hình được — Đại ca chốt 13/10) → chuyển `chua_biet` — **không** ghi 0% như một số đo, vì tài khoản có thể đã được dùng ngoài trạm. Thiếu cửa sổ trong số đo → cửa sổ đó `chua_biet`, không giả 0%.
- Dashboard hiện số đo kèm "đọc lúc …" và đánh dấu cửa sổ chưa biết.

| CLI | Nguồn chính | Nguồn lùi |
|---|---|---|
| Claude | `rate_limit_event` trong stream-json khi chạy — **chưa xác minh chạy thật** (S1, #5 chưa duyệt). S1 phải chốt: `utilization` là tỷ lệ 0–1 hay phần trăm; mỗi event có đủ các cửa sổ hay chỉ một; `rateLimitType` gồm những giá trị nào | log `projects/*.jsonl` trong `CLAUDE_CONFIG_DIR` của khe (`quotaLimits`, `rate_limit_info` — chỉ khi đã bị chặn); regex hai mức "gần hết" / "đã hết" |
| Codex (3b) | `codex app-server` → `account/rateLimits/read`, hỏi lúc khe rảnh mỗi 5 phút. Bộ đọc app-server dùng trường **`usedPercent`, `windowDurationMins`, `resetsAt`** (theo spike hạn mức) | log `$CODEX_HOME/sessions/**/rollout-*.jsonl`: trường **`used_percent`, `window_minutes`, `resets_at`** |

- Cả hai bộ đọc chuẩn hoá về mô hình nội bộ trước khi áp ngưỡng: thời lượng 300 phút → `5h`, 10080 phút → `tuan`; cửa sổ khác giữ thời lượng và tên gốc, không tự bỏ. Không ánh xạ theo `primary/secondary`. S5 ghi fixture theo đúng phiên bản CLI và cấu trúc kết quả thật.
- **Không** đọc token đăng nhập để lấy hạn mức; **không** gọi endpoint OAuth/cookie không tài liệu.

> **Ghi chú 16/10, D44:** đồng bộ theo mã lát 3b (plan 3b G13). Hình dạng dữ liệu Codex **chưa xác minh** — chờ S5.
>
> - **`codex exec --json` không là nguồn hạn mức.** Stream này không mang số đo hạn mức (theo hiểu biết hiện tại). Thợ chỉ dùng thông điệp lỗi của nó (`error`, `turn.failed`) để **phát hiện** hết hạn mức (khớp `usage limit|rate limit|too many requests|429|quota`) hoặc chưa đăng nhập (`not logged in|log in again|unauthorized|401`). Mã: `NguonHanMucCodex.het_han_muc`, `thong_diep_loi` trong `tram/chay_cli/codex/han_muc.py`.
> - **App-server:** vòng thợ hỏi `codex app-server` khi khe rảnh, mỗi 300 giây (`CHU_KY_RANH_GIAY`, `tram/chay_cli/codex/app_server.py`; gọi từ `tram/tho/vong_khe.py`). Quá 20 giây hoặc lỗi → không có số đo, cửa sổ thành chưa biết, khe vẫn nhận việc (#15). `nguon="app-server"`, `doc_luc` = lúc hỏi.
> - **Rollout:** đã có bộ chuẩn hoá dòng `token_count` (`han_muc_rollout`; `nguon="log"`, `doc_luc` = `timestamp` của dòng). Mã hiện **chưa** có bước đọc file `$CODEX_HOME/sessions/**/rollout-*.jsonl`: `NguonHanMucCodex.doc_dong` chỉ được nạp các dòng của stream `exec`.
> - **Đơn vị `resets_at` / `resetsAt`** (`_gio` trong `tram/chay_cli/codex/han_muc.py`): số là giây epoch; số > 10¹² coi là mili giây; chuỗi ISO 8601 cũng nhận (không múi giờ thì coi là UTC). Giá trị không đọc được → `reset_luc = null`, cửa sổ vẫn giữ.
> - Phần trăm ngoài 0–100, hoặc thời lượng thiếu, < 1 hay không nguyên → bỏ cửa sổ đó (thành chưa biết), không giả 0%. Tên cửa sổ theo thời lượng qua `ten_cua_so`, tên gốc cắt 32 ký tự.
- `ccusage` chỉ dùng cho màn Usage, **không** dùng để chặn giao việc.

### 8.2 Luật nhận việc — `duoc_nhan(han_muc, uu_tien) -> bool`

`uu_tien`: số 0–4 theo `priority` của `bd`. Theo thứ tự, gặp luật nào khớp thì dừng:

1. Một cửa sổ **đã biết** ≥ 90% → **không** nhận.
2. Cửa sổ `tuan` **đã biết** ≥ 80% → chỉ nhận `uu_tien` ≤ 1 (P0–P1).
3. Còn cửa sổ chưa biết → **nhận**, kèm cảnh báo vàng trên dashboard; lần đầu khe ở trạng thái này sau khi đã chạy ghi `khe.han_muc_khong_ro` (#15 — quyết định đã chốt, không dừng khe vì không đọc được hạn mức). Trần giờ/ngày và cầu dao vẫn có hiệu lực.
4. Còn lại → nhận.

Ngưỡng nằm trong `~/.tram/cau-hinh.yaml` (`han_muc: {ngung: 90, tuan_chi_uu_tien: 80, tuoi_toi_da_gio: 6}`).

### 8.3 Sổ hạn mức + cầu dao

- **Trần cứng mỗi khe:** tối đa `lan_chay_moi_gio` (mặc định 6) và `lan_chay_moi_ngay` (mặc định 60) lần chạy; tối đa 1 phiên đồng thời. Đếm từ `chay.bat_dau`; kiểm **trước mỗi lần** khởi chạy CLI, kể cả lần 2–3 trong một phiếu.
- **Cầu dao ngắt** khi: CLI báo hết hạn mức / 429; hoặc 3 lần chạy liên tiếp **lỗi không do agent** = CLI thoát mã ≠ 0 **và** stream không có thông điệp `assistant` nào, hoặc stream có `rejected` / mẫu "chưa đăng nhập". Ngắt tới `reset_luc` của cửa sổ đã cạn; không biết thì 60 phút. Sự kiện `khe.cau_dao_ngat {khe_id, ly_do, toi_luc}`. Hạn mức chưa biết **không** tự làm cầu dao ngắt.
- Cầu dao tự đóng khi tới giờ (`khe.cau_dao_dong`). Đại ca đóng tay từ dashboard 2b (`POST /api/khe/{id}/cau-dao-dong`).
- Phiếu đang chạy khi cầu dao ngắt → dừng mềm (§6.3); phần 4 giao lại cho khe khác.

## 9. Đăng ký máy, khe và kiểm

### 9.1 Cấu hình máy thợ — `~/.tram/tho.yaml` (tài khoản quản lý thợ)

```yaml
may_id: B
tram_api: http://127.0.0.1:7700
khe:
  - ten: claude-1
    cli: claude
    principal: <tài khoản/sandbox thực thi của khe — chốt sau S6>
    thu_muc_cau_hinh: <thư mục CLAUDE_CONFIG_DIR thuộc principal của khe>
    ten_goi_nho: "Claude tài khoản 1"          # dashboard hiện tên này, không hiện email
    vai_uu_tien: [coder]
  - ten: claude-2
    cli: claude
    principal: <…>
    thu_muc_cau_hinh: <…>
    ten_goi_nho: "Claude tài khoản 2"
    vai_uu_tien: [spec, qc]
```

`tram tho them-khe` / `bot-khe` sửa file này và gửi `POST /api/tho/dang-ky {may_id, khe[]}`. Đăng nhập tài khoản cho từng khe **Đại ca làm tay**, dưới đúng principal của khe (`CLAUDE_CONFIG_DIR=… claude` rồi đăng nhập, hoặc `claude setup-token` theo kết quả S2). Nếu phải dùng `CLAUDE_CODE_OAUTH_TOKEN` trong môi trường tiến trình con thì agent chạy `env` sẽ thấy token của chính khe đó — rủi ro Em đề xuất chấp nhận (§13 mục 13), vì token chỉ là quyền của khe đó và không mở được credential của trạm hay khe khác; ưu tiên đăng nhập Keychain theo `CLAUDE_CONFIG_DIR` nếu S2 cho phép.

### 9.2 Lát 3b — ghép máy từ xa

- `tram chu cap-ma` in mã ghép dùng một lần, hết hạn sau 10 phút.
- Mac thợ phải là thiết bị **gắn tag** Tailscale (vd `tag:tram-tho`), không đăng nhập bằng tài khoản Đại ca (#3) — nếu không, `tailscale serve` gắn header danh tính thật của Đại ca cho mọi yêu cầu từ máy thợ.
- Trên Mac thợ: `tram tho dang-ky --tram-chu https://<may-b>.<tailnet>.ts.net` (nhập mã kín sau bước đồng ý; không đặt mã vào argv) → nhận token máy (ngẫu nhiên 32 byte), lưu Keychain của tài khoản quản lý thợ (`tram-tho-token`). Thu hồi: `tram chu go-may <may_id>` (§5.1).
- Cách ly trên Mac thợ cùng hợp đồng §7.3.
- Minh bạch (Q15): `dang-ky` in danh sách thay đổi (tài khoản, file cấu hình, launchd, cấu hình memory MCP — phần 1b) và chờ gõ `dong-y`.

> **Ghi chú 16/10, D44:** đồng bộ theo mã lát 3b (plan 3b G1, G2, G7, G8, G11). Chưa chạy thật trên Mac từ xa (#5, S6, S7).
>
> - **Mã ghép** (`tram/phieu/ma_ghep.py`, `tram/chu/cap_ma.py`): lệnh là `tram chu cap-ma <may_id>`; mã **gắn với `may_id`** do Đại ca đặt lúc cấp (`may_id` khớp `[A-Za-z0-9-]{1,32}`). Mã 12 ký tự Crockford base32 (60 bit), in `XXXX-XXXX-XXXX`; nhập không phân biệt hoa thường, bỏ khoảng trắng và gạch.
> - Trạm chỉ lưu sha256 của mã đã chuẩn hoá (bảng `ma_ghep`, `ghep_sai` trong `su-kien.db`, tạo lười). Cấp mã mới huỷ mã cũ chưa dùng của máy đó. Máy đang có token còn hiệu lực → từ chối cấp (mã thoát 2); phải `tram chu go-may <may_id>` trước.
> - Sai 5 lần trong 10 phút → huỷ mọi mã đang chờ (mọi máy), và từ chối đổi mã (429) tới khi số lần sai trong 10 phút gần nhất xuống dưới 5. Khi bị khoá, trạm không xét mã. Mã đúng nhưng máy đã có token lúc đổi → mã bị tiêu, trả 403, không cấp token.
> - **Endpoint** (`tram/api/ghep.py`): `POST /api/ghep-may {ma}`, **ngoài** nhóm `/api/tho/*` vì máy chưa có token máy; không dùng danh tính Tailscale. 200 `{may_id, token}` kèm `Cache-Control: no-store`; 403 `{loi}` khi mã sai/đã dùng/hết hạn (không nói mã thuộc máy nào); 429 khi khoá; 422 thân sai; 503 khi kho phiếu chưa bật. Token máy ghi vào bảng `may_tho` như `cap_token_may` (3a-1).
> - **Cú pháp** (`tram/tho/lenh_dang_ky.py`, `tram/tho/khai_khe.py`): `tram tho dang-ky --tram-chu https://<máy B>.<tailnet>.ts.net --khe <ten>:<cli>:<vai,…>:<tên gợi nhớ> [--thu-muc-khe DIR] [--khong-nho] [--dong-y]`. `--khe` bắt buộc, lặp được; cùng luật với `nap_cau_hinh_tho` (tên khe, `cli` ∈ `claude|codex`, vai, tên gợi nhớ ≤ 64 ký tự, không chứa `@`).
> - `--thu-muc-khe` mặc định `~/tram/khe`; thư mục cấu hình của khe = `<đó>/<ten>`. `--khong-nho` bỏ cấu hình memory MCP. `--dong-y` bỏ bước hỏi. `principal` để trống (S6). Mã ghép hỏi kín bằng `getpass` sau bước đồng ý.
> - **Từ chối, chưa đổi gì** (mã thoát 2; `tram/tho/ke_hoach_dk.py`): `--tram-chu` không phải `https://<tên>.<miền>`; máy đã có `tho.yaml` hoặc `/Library/LaunchDaemons/vn.tram.tho.plist`; không có `--khe` hoặc tên khe trùng; khai khe sai; máy chưa gắn `tag:tram-tho` (hoặc không đọc được `tailscale status --json`); thiếu `tram` hoặc CLI của một khe.
> - Chưa đăng nhập CLI (Claude luôn "chưa kiểm được", chờ S2) hay chưa có thư mục khe → **chỉ cảnh báo**. Không gõ `dong-y` → không làm gì, mã thoát 1.
> - **Thứ tự thực hiện** (`tram/tho/thuc_hien_dk.py`): kiểm lại chưa có `tho.yaml`/daemon → đổi mã ghép lấy token → Keychain (`security -i` qua stdin, đọc lại so hằng thời gian; `tram/tho/token_may.py`) → `tho.yaml` (kiểm bằng `nap_cau_hinh_tho` trước khi thay) → file (`config.toml` của khe Codex 0600, plist 0644, ghi nguyên tử) → lệnh MCP của Claude → `POST /api/tho/dang-ky`.
> - **Không nạp launchd** (khác bước cuối "nạp launchd" ở plan 3b G11, theo G4 review đợt 3): mã chỉ **ghi** plist `vn.tram.tho` vào `~/Library/LaunchAgents`, **chưa** `bootstrap`; lệnh nạp chỉ in ra để dùng sau khi khai principal/`chay.day` và đạt S2/S6/S7 (xem "Lệch so với spec khi code" bên dưới). Lỗi giữa chừng → dừng, không tự lùi; in hướng dẫn xin mã mới, và `tram chu go-may` trước nếu máy đã nhận token.
> - Beads: `dang-ky` **không** trỏ Beads về trạm chủ; kế hoạch in rõ dòng này (kiến trúc §7, plan 3b G6).

### 9.3 `tram tho kiem`

In xanh/đỏ từng mục, mã thoát ≠ 0 nếu có đỏ:

| Mục | Kiểm |
|---|---|
| tram-api | `GET /api/tho/ping` với token máy được `200` |
| Mỗi khe | CLI có trong PATH của principal + phiên bản; thư mục cấu hình tồn tại; trạng thái đăng nhập qua lệnh trạng thái của CLI (không đọc file đăng nhập — S2); cầu dao |
| Cách ly | chạy bộ kiểm chứng âm §7.3 mục 7 rút gọn: principal của khe không đọc được token máy, hàng đợi khe khác, khoá nội bộ |
| Kho | `~/tram/kho/<du-an>` tồn tại cho mọi dự án trong `GET /api/du-an`, không có `.env` thật; principal của khe ghi được worktree của nó |
| Công cụ | `git`, `uv`, lệnh test của từng dự án có trong PATH của principal |
| Máy | không bật ngủ (cảnh báo); dung lượng trống ≥ 10 GB (cảnh báo) |

> **Ghi chú 16/10, D44:** mục lát 3b, nối vào cuối `kiem_may` (`bo_sung_3b` trong `tram/tho/kiem_3b.py`; plan 3b G17). Chờ S5 cho phần Codex.
>
> - **`tailscale tag`** — chỉ khi `tram_api` trong `tho.yaml` là `https://` (máy từ xa): đọc `tailscale status --json` → `Self.Tags` có `tag:tram-tho` thì xanh, không thì đỏ. Chỉ kiểm, không đổi cài đặt Tailscale (`kiem_tag` trong `tram/tho/do_may.py`).
> - **Khe Codex, đăng nhập:** thay mục "đăng nhập" chung bằng kết quả `codex login status` với `CODEX_HOME` của khe — mã 0 xanh, còn lại đỏ. Không chép đầu ra của lệnh (`do_cli` trong `tram/tho/do_may.py`).
> - **Khe Codex, hạn mức:** thêm mục `<khe> hạn mức`, đọc một lần qua `codex app-server`. Đọc được → xanh kèm số đo từng cửa sổ; không đọc được → **vàng** (vẫn nhận việc, #15), không đỏ.
> - Khe Claude và các mục cách ly, quyền ghi worktree giữ như 3a-1/3a-2.

## 10. Sự kiện (thêm vào bảng `su_kien` phần 0, không đổi cột)

Sự kiện không gắn dự án dùng `du_an = "_tram"`. Sự kiện gắn phiếu (`chay.*`, `bao.*`, `giao.*`) điền đúng `du_an`, `bead_id`. `tac_nhan` = `tho/<khe_id>` hoặc `tram/api`. Không sự kiện nào chứa `ma_giao`.

| Loại | Dữ liệu | Ghi khi |
|---|---|---|
| `khe.dang_ky` | `{khe_id, cli, ten_goi_nho, vai_uu_tien}` | đăng ký / sửa khe (coi như bật) |
| `khe.ket_noi` / `khe.mat_ket_noi` | `{khe_id}` | §6.3 bộ canh |
| `khe.han_muc` | `{khe_id, cua_so[], nguon}` (§8.1) | một cửa sổ đổi ≥ 5 điểm %, đổi `reset_luc`, hoặc đổi `biet`/`chua_biet` |
| `khe.han_muc_khong_ro` | `{khe_id}` | §8.2 luật 3 |
| `khe.cau_dao_ngat` / `khe.cau_dao_dong` | `{khe_id, ly_do, toi_luc, ma_thao_tac?}` | §8.3; đóng tay từ dashboard: `ly_do="dai-ca"`, `toi_luc=null`, có `ma_thao_tac` |
| `khe.bat` / `khe.tat` | `{khe_id, vi_sao, ma_thao_tac?}` | Đại ca bật/tắt; dashboard 2b có `ma_thao_tac`, CLI 3a không bắt buộc trường này |
| `giao.nhan` | dữ liệu theo phần 4 §12 + `ref_phieu` (khoá của phiếu trong kho phiếu bền §6.6) | cấp phiếu |
| `chay.bat_dau` / `chay.xong` | `{giao_id, luot, lan, khe_id, request_id, ket_thuc, ma_thoat, mo_hinh, token_vao, token_ra, token_cache_doc, token_cache_ghi, thoi_gian_ms, digest_log}` | mỗi lần chạy CLI |
| `chay.don_rac` | `{giao_id, nhanh_rac}` | §7.1 |
| `bao.moc` / `bao.can_hoi` / `bao.bi` / `bao.xong` / `bao.het_han_muc` | `{giao_id, luot, request_id, noi_dung, ban_giao?, commit, loi_ban_giao?, ly_do?, loai_hoi?}` | §7.4, §7.6 |
| `giao.da_push` | `{giao_id, luot, commit, ref_tam}` | thợ báo đã push ref tạm (lời báo, chưa phải công bố) |
| `giao.cong_bo` | `{bead_id, luot, commit, ref}` | trạm đã cập nhật ref công bố (§6.4) |
| `giao.thu_hoi` / `giao.snapshot` | §6.3, §6.5 | |
| `tho.tu_choi` | `{khe_id, giao_id, bead_id, luot_gui, luot_dung}` | thẻ chắn từ chối |

> **Ghi chú 16/10, D44:** ba sự kiện mới của lát 3b, `du_an = "_tram"`, ghi trong cùng giao dịch với thay đổi (`tram/phieu/ma_ghep.py`; plan 3b G2). Không sự kiện nào chứa mã ghép hay token.
>
> | Loại | Dữ liệu | Ghi khi |
> |---|---|---|
> | `may.cap_ma` | `{may_id, het_luc}` | `tram chu cap-ma <may_id>` cấp mã mới |
> | `may.ghep` | `{may_id}` | đổi mã thành công, máy nhận token |
> | `may.ghep_sai` | `{so_lan}` — số lần sai trong 10 phút gần nhất, kể cả lần này | mã sai, đã dùng hoặc hết hạn (không ghi khi đang bị khoá) |

**Đối chiếu producer 2b (hợp đồng G3 đã nhận trong phản hồi review đợt 1+2):** `khe.bat`, `khe.tat`, `khe.cau_dao_dong` phát từ dashboard mang cột `du_an="_tram"`, `tac_nhan="dai-ca/dashboard"` và `du_lieu.ma_thao_tac`. Ghi qua `bat_tat_khe`/`dong_cau_dao` của phần 3 trong giao dịch, không dùng sự kiện ở dự án để biểu diễn trạng thái khe. `toi_luc=null` khi đóng tay; tự đóng theo giờ dùng `ly_do="het-gio"`, không giả thành thao tác Đại ca.

Hàm nội bộ cho spec 1b: `phieu_theo_giao_id(giao_id) -> {du_an, vai, ma_giao, con_hieu_luc}`, lộ ra qua `GET /api/noi-bo/phieu/{giao_id}` (trả cả khi phiếu đã hết hiệu lực; `ma_giao` chỉ trả khi phiếu còn hiệu lực), chỉ với **token nội bộ** (cấp khi `tram chu cai-dat`, Keychain của tài khoản trạm, dịch vụ `tram-noi-bo-token`; khác token máy thợ). Chỉ cần khi 1b-2 bật (spec 1b §3).

**Nhịp tim không phải sự kiện.** Bảng vận hành `nhip_tim(khe_id PRIMARY KEY, luc, giao_id, luot, buoc_tho, han_muc)` cùng file `~/.tram/su-kien.db` — ghi đè, không phải lịch sử (§13 mục 3).

### 10.1 Giao diện cho phần 2b, 2c

`trang_thai_khe(kho, nhip) -> list[TrangThaiKhe]`, suy lúc đọc:

| Trường | Nguồn |
|---|---|
| `khe_id, cli, ten_goi_nho, vai_uu_tien` | `khe.dang_ky` mới nhất |
| `trang_thai` | xét theo thứ tự: `tat` → `mat_ket_noi` (nhịp tim cuối > 90 s) → `loi` (cầu dao đang ngắt, **hoặc** không giữ phiếu **và** lần chạy cuối `ket_thuc` ∉ {xong, dung} — `dung` là cố ý dừng, sửa 21/10) → `can_nguoi` (phiếu hiệu lực có `bao.can_hoi`/`bao.bi` chưa giải, escalation liên kết chưa đóng) → `lam` (có phiếu hiệu lực) → `ranh` |
| `phieu` | `{giao_id, bead_id, du_an, buoc, tieu_de}` khi `lam`/`can_nguoi` |
| `han_muc` | `nhip_tim.han_muc` (mới nhất); không có thì `khe.han_muc`; cửa sổ chưa biết hiện rõ |
| `cau_dao` | `khe.cau_dao_*` mới nhất |
| `so_phien` | 1 nếu `lam`/`can_nguoi`, ngược lại 0 |

Sáu giá trị hiển thị thành năm hàng của spec phần 2 §5.5. **Bảng điểm thợ** (2b) công thức ở spec phần 4 §12.

## 11. Ranh giới với phần 4

| Việc | Phần |
|---|---|
| Cấp `giao_id`, `luot`, `han_giu`, `ma_giao`; kho phiếu bền; thẻ chắn; thu hồi; snapshot; hàm phiếu hiệu lực | 3 |
| Công bố ref (CAS) từ ref tạm | 3 |
| Chọn bead, bước, khe; luật Q14; dựng gói; tính `khoa_chong_trung`; chọn `lenh_kiem` bắt buộc | 4 |
| Giữ sổ `khoa_chong_trung` và từ chối trùng | 3 |
| Ngân sách một phiếu | 3 thực thi (kể cả quyết toán khi thiếu `chay.xong`), 4 đặt giá trị |
| Ngân sách tổng theo bead, giữ trước theo chu kỳ, cạn → cột 2 | 4 |
| Chạy lệnh kiểm trong worktree thợ (principal thực thi), ghi digest | 3 |
| Chạy lại lệnh bắt buộc trên worktree sạch trước cột 3 (cũng dưới principal thực thi) | 4 |
| Xử lý công việc chờ sau báo kết thúc; phát `bead.dong`; tạo escalation | 4 |

## 12. Spike trước khi viết plan

Không spike nào đã chạy. Kết quả lưu phiên bản, lệnh, môi trường, mã thoát và transcript đã che bí mật, ghi `docs/spikes/<ngày>-<ten>.md`. Không spike nào cần đọc file đăng nhập.

| # | Spike | Vì sao | Duyệt |
|---|---|---|---|
| S1 | Một lần `claude -p --output-format stream-json --verbose` thật với prompt ngắn: có `rate_limit_event` không, trường nào, `utilization` là tỷ lệ hay %, đủ cửa sổ hay không; thêm fixture lỗi quota | nguồn chính hạn mức Claude **chưa xác minh** | #5 — chưa duyệt |
| S2 | Dưới LaunchAgent của đúng principal: Claude đọc được đăng nhập trong Keychain không, sau reboot trước/sau đăng nhập; nếu không thì `claude setup-token`; lệnh kiểm trạng thái đăng nhập không đọc file | thợ chạy không người ngồi | #5 — chưa duyệt |
| S3 | Hai `CLAUDE_CONFIG_DIR` song song, hai tài khoản, dưới principal riêng; so danh tính và hạn mức đã che | tên thư mục không chứng minh tách credential | #5 — chưa duyệt |
| S4 | Cờ headless: file settings theo vai; cấm thắng cho phép ở mọi nguồn (settings repo, plugin, subagent, MCP); cờ chỉ nạp settings của vai; lệnh bị cấm từ chối trong thời gian hữu hạn, không treo | §7.2 | #5 — chưa duyệt |
| S5 (3b) | `codex app-server` → `account/rateLimits/read` dưới `CODEX_HOME` riêng; `codex exec --json` sandbox ghi trong/ngoài worktree, mạng, hook, approval | khe Codex | cần cho phép |
| S6 | Cơ chế cách ly: user macOS cho mỗi khe hay user thực thi + sandbox; chạy bộ kiểm chứng âm §7.3 mục 7; tạo principal `tram-kiem` và chạy lại bộ kiểm chứng âm từ nó (§7.3 mục 5, §13 mục 12) | #3, H9 | cần cho phép (tạo tài khoản là thay đổi hệ thống) |
| S7 | GitHub: credential thợ chỉ push được `tram/luot/*` (thử push `main`, `tram/<bead>`, ref lượt khác, force, delete — phải bị remote từ chối); host thật mà `gh` cần; push treo qua lúc thu hồi, mất phản hồi sau khi remote đã nhận — ref công bố không bị commit cũ chiếm | §6.4, H2 | cần cho phép (repo nháp) |
| S8 | Hook `PreCompact` gọi `tram bao --moc` đúng lúc, không lặp, không deadlock | §7.7 | #5 — chưa duyệt (cần chạy Claude thật) |

> **Ghi chú 15/10/2026** (không đổi bảng trên):
>
> - **#5 mở một phần.** Phần đã mở (Tailscale máy B, Ollama, `vn.tram.nho`, API key cho chấm cột và memory) không chạm spike nào ở đây. S1–S8, tạo user/sudoers (S6), repo GitHub (S7) và mọi bước tốn quota vẫn **chưa duyệt**. Xem [quyết định 13/10, mục "Ghi chú 15/10"](../quyet-dinh/2026-10-13-tra-loi-cau-hoi-gop.md).
> - **S2 viết cho LaunchAgent**, còn plan 3a-2 (G32, G35) cài thợ máy B dưới **LaunchDaemon** `vn.tram.tho`. Plan 3b G4 giữ LaunchAgent cho Mac từ xa. Vì vậy kết luận Keychain của [spike hạn mức](../spikes/2026-10-12-han-muc-cli.md) chưa áp cho daemon, S2 phải kiểm cả hai dạng.
> - **Thứ tự S1 ↔ S6 vòng nhau — chờ Đại ca/Codex xác nhận.** Bảng trên không bắt S1 chạy dưới principal. Plan 3a-2 ("Để sau") lại chạy S1 dưới principal của `B/claude-1`, tức phải có user của S6 trước. Còn chọn cơ chế S6 thì có thể phụ thuộc S2 (G34, chỉ khi chọn sandbox). [Sổ tay chạy thật](../handovers/2026-10-15-so-tay-chay-that.md) đề xuất theo khuyến nghị review Codex: chốt §14 principal (thử `user` mỗi khe trước), chạy S6, rồi S1–S4 và S8 dưới principal. Nếu S2 buộc đổi cơ chế thì quay lại §14. Đây chỉ là đề xuất, chưa chốt.

## 13. Em tự quyết — chờ Đại ca duyệt cùng spec

1. **Chia lát 3a/3b**: lát đầu chỉ hai khe Claude trên máy B.
2. **Thợ nói chuyện với tram-api qua HTTP có token máy**, kể cả trên máy B; token máy chỉ nằm ở tài khoản quản lý thợ; `tram bao` chỉ ghi hàng đợi cục bộ; dịch vụ khác nhận phiếu qua `ma_giao`.
3. **Bảng `nhip_tim` ghi đè** ngoài nhật ký sự kiện (lệch nhẹ khỏi Q12 để khỏi ~2.900 dòng/khe/ngày vô ích).
4. **Thợ push, agent không** — chi tiết ref tạm/công bố là đề xuất §6.4.
5. **Thợ chạy lệnh kiểm và ghi digest**, agent không tự điền kết quả lệnh kiểm.
6. **Trần cứng** 6 lần/giờ, 60 lần/ngày mỗi khe; cầu dao 60 phút khi không biết giờ reset.
7. **`.tram/tien-do.md`** làm cầu nối khi CLI chết.
8. **Clone dự án trên máy B do Đại ca làm tay** ở 3a.
9. **`du-an/<ten>.yaml` thêm khoá** `lenh_cho_phep`, `moi_truong_kiem`, `nhanh_chinh` (mặc định `main`).
10. **Nhịp tim kiêm xin việc** — bỏ endpoint xin việc riêng.
11. **Kho phiếu bền trong cùng file SQLite với nhật ký sự kiện**, bảng riêng (§6.6).
12. **Principal kiểm lại riêng của trạm** (`tram-kiem`, §7.3 mục 5) — đề xuất thêm sau review Fable 13/10; chốt cùng S6.
13. **Chấp nhận rủi ro token khe trong môi trường** (§9): nếu S2 buộc dùng `CLAUDE_CODE_OAUTH_TOKEN`, agent chạy `env` thấy token của chính khe đó. Token chỉ mang quyền của khe đó, không mở được credential của trạm hay khe khác; ưu tiên đăng nhập Keychain theo `CLAUDE_CONFIG_DIR` nếu S2 cho phép. Cần Đại ca đồng ý khi duyệt spec.

## 14. Quyết định đã chốt 13/10 (thay mục câu hỏi D1–D6)

> **Ghi chú 15/10/2026 — cách đọc mục này:** tiêu đề chỉ đúng với **bảng** ngay dưới (D1–D6, Codex 6), là các quyết định đã chốt. Hai gạch đầu dòng ở cuối mục ("Đề xuất kỹ thuật mới cần Đại ca chốt": cách công bố commit sau S7, cơ chế cách ly sau S6) **chưa chốt**, vẫn là hai đề xuất còn mở. Hàng D3 vẫn đúng ngày 15/10: S1–S4 chưa được duyệt chạy, dù một phần khác của #5 đã mở (xem ghi chú cuối §12).

| Mã cũ | Quyết định | Ghi ở |
|---|---|---|
| D1 | Tối đa **3 lần chạy CLI mỗi phiếu**, trong trần thời gian/token (#13). Mặc định QC/spec 2 lần ở phần 4 giữ nguyên (#21) | §4, §7.2, §7.6 |
| D2 | **Tách tài khoản thực thi trước 3a** (#3); Mac thợ từ xa gắn tag | §3, §7.3, §9.2 |
| D3 | Spike S1–S4 **chưa được duyệt chạy** (#5) | §3, §12 |
| D4 | Hạn mức chưa biết sau khi đã chạy: **chạy tiếp, cảnh báo vàng** (#15) | §8.2 |
| D5 | Tắt khe / estop / cầu dao khi đang làm: **dừng mềm** (#14) | §6.3, §7.6 |
| D6 | Con số H3 11 phút, H8 60 s, trần 6/giờ – 60/ngày, ngân sách 3 lần/90 phút/200k token: **giữ làm mặc định**, cấu hình được (#21) | §2, §8.3, §6.1 |
| Codex 6 | Hạn chót dừng mềm mặc định **3 phút**; tuổi tối đa của số đo hạn mức mặc định **6 giờ** (Đại ca chốt 13/10) | §7.6, §8.1 |

**Đề xuất kỹ thuật mới cần Đại ca chốt** (từ review Codex, chưa phải quyết định):

- Ref tạm theo lượt + trạm công bố bằng CAS, hay phương án lùi "trạm fetch từ kho thợ rồi tự push" — sau S7 (§6.4).
- Cơ chế cách ly: user macOS cho mỗi khe, hay user thực thi chung + sandbox mỗi khe — sau S6 (§7.3).

## 15. Kiểm chứng

1. **Unit test** (CLI giả là script in stream JSON mẫu; tram-api chạy trong tiến trình test với SQLite tạm; đồng hồ giả tiêm `now`): `duoc_nhan` mọi nhánh, kể cả cửa sổ chưa biết (H4); khe đang giữ phiếu không nhận phiếu mới (H1); hai nhịp tim đồng thời không cùng nhận một bead (H1); thẻ chắn từ chối `luot` cũ và `giao_id` lạ (H2); `request_id` lặp cùng nội dung trả kết quả cũ, khác nội dung → 409; báo kết thúc thứ hai bị từ chối; restart tram-api giữ nguyên phiếu hiệu lực và `ma_giao`; thu hồi đúng 10 phút sau nhịp cuối (H3); `mat_ket_noi` sau 90 s; cầu dao chỉ đếm lỗi không do agent (H5); số đo quá `reset_luc` hoặc quá tuổi → chưa biết, không 0%; bộ đọc app-server dùng `windowDurationMins`, bộ đọc log dùng `window_minutes`; trần lần chạy kiểm trước lần 2–3; CLI mồ côi bị kill khi khởi động lại; dọn rác worktree; `tram bao` kiểm cấu trúc, commit, ghi hàng đợi; thợ gắn đúng `giao_id`/`luot`; môi trường CLI không có token máy; mọi lệnh bắt buộc phải pass — suite bắt buộc fail + lệnh nhỏ pass → `loi_ban_giao`; lệnh bắt buộc timeout → fail; lệnh đề xuất không thay lệnh bắt buộc; dòng hàng đợi sau `xong` bị bỏ; dòng sai cấu trúc bị từ chối; đích `moi_truong_kiem` qua symlink ra ngoài worktree bị từ chối; phiếu spec không cần môi trường kiểm; estop vẫn nhận báo của phiếu đang dừng mềm; dừng mềm quá hạn chót → giữ WIP cục bộ, báo snapshot cũ; thiếu `chay.xong` → quyết toán không bằng 0; `tram` chỉ nhận `bao` khi có `TRAM_GIAO_ID`; token máy sai khe → 403; thu hồi token máy vô hiệu phiếu; `trang_thai_khe` đủ sáu giá trị; `tram tho kiem` với các kịch bản đỏ giả (H7).
2. **Kịch bản giả lập** (không gọi CLI thật): hai khe giả, một bead nhiều bước; khe rảnh nhận phiếu trong ≤ 2 nhịp (H8); giết khe 1 giữa chừng → khe 2 tiếp tục từ snapshot đã công bố (H3, H6); khe 1 "thức dậy" gửi nhịp tim/báo với `luot` cũ → bị từ chối; push ref tạm của lượt cũ sau thu hồi không đổi ref công bố (H2 — dùng remote Git cục bộ giả); mất phản hồi `da-push` → gửi lại không công bố hai lần; giả lập `rejected` → cầu dao (H5); tắt khe khi đang chạy → dừng mềm.
3. **Trên máy thật** (Đại ca cho phép): S1–S8; kiểm chứng âm H9; một bead thử trong repo nháp chạy trọn một bước `code` trên `B/claude-1` và một bước `qc` trên `B/claude-2`.

## 16. Ngoài phạm vi

Tự cài/cập nhật CLI; đăng nhập tài khoản thay Đại ca; Gemini CLI; merge queue; nhiều phiên đồng thời trên một khe; đọc hạn mức qua endpoint không tài liệu.


## 17. Đối chiếu hợp đồng triển khai sau review tĩnh 13/10 — đã nhận trong phản hồi đợt 1+2

Phụ lục này **không sửa hay thay thế quyết định đã duyệt**. Các chi tiết API của plan 3a-1 đã được nhận trong `docs/handovers/2026-10-13-phan-hoi-review-codex-dot12.md`; không phải bằng chứng test, spike hay mở cổng chạy thật.

| Plan | Hợp đồng được đối chiếu |
|---|---|
| G2 | `kiem_ban_giao(bg, tieu_chi, goc, *, lenh_bat_buoc, can_lenh_kiem, commit=None, la_qc=False, ket_luan_qc=None)`; hai tham số lệnh bắt buộc, không mặc định lỏng. |
| G5, G6 | `tram/cau_hinh/lenh.py` sở hữu `khop_lenh`, `kiem_mau`, `khop_bat_ky`; `tram/kiem/{duong_dan_cam,diff}.py` sở hữu kiểm đường dẫn và diff, tên cũ/mới, so không phân biệt hoa thường. |
| G7, G8 | Ba khóa yaml `lenh_cho_phep`, `moi_truong_kiem`, `nhanh_chinh`; phần 4 tạo `DeXuatPhieu`, phần 3 cấp `giao_id`, `luot`, `khe_id`, `han_giu`, `ma_giao`. Spec không chạy mã. |
| G11 | Bộ chọn `chon(khe_id, han_muc)` ngoài giao dịch; `con_hop_le(de_xuat)` kiểm kho trong giao dịch. Lát 4a-2 nối cả hai callback; `chon_phieu=None` đến lúc đó. |
| G18 | `chay.xong.ket_thuc`: `xong`, `loi`, `loi_he`, `het_han_muc`, `dung`, `mo-coi`; có thể kèm `reset_luc`. Từng bản ghi chỉ tham gia Usage/cầu dao một lần theo G35. |
| G20, G23 | Thu hồi máy dùng `giao.thu_hoi.ly_do=go-may`; máy chỉ lưu băm token. Hàng đợi `tram bao` mang `{loai, noi_dung, commit, ban_giao?, loai_hoi?}`; không phải quyền truy cập trạm. |
| G28, G31 | Khóa `tho:` đặt trần, thời gian lease/cầu dao; `/api/tho/*` xác thực token máy; `/api/noi-bo/phieu` chỉ nhận `tram-noi-bo-token`, trả `ma_giao` khi phiếu hiệu lực và `Cache-Control: no-store`. |
| G35 — mới trong review | Danh tính thực thi `(giao_id, lan)` chỉ có một bắt đầu, một kết thúc; kết thúc phải có bắt đầu; `lan` không vượt ngân sách phiếu. Retry giữ nguyên `request_id`, nhận kết quả cũ; ID mới cho lần đã có hoặc kết thúc chưa bắt đầu trả 422 `lan-chay-sai` trước khi ghi. Tiến trình quản lý 3a-2 gửi theo thứ tự, giữ hàng đợi/request_id qua restart. Với CLI mồ côi, replay bắt đầu bền trước rồi gửi kết thúc. |

Các lệch chữ đã ghi rõ trong plan cũng phải chốt: nhịp stale trả 200 kèm lệnh dừng; nhịp rảnh khi còn giữ phiếu không gia hạn; thứ tự dừng `khe-tat → estop → cau-dao → can-hoi`; `khe.han_muc` so lần ghi gần nhất; `khe.cau_dao_dong.ly_do` là `het-gio` hoặc `dai-ca`. HTTP `/su-kien` ghi sự kiện đã xảy ra; kiểm trần và ngân sách **trước mỗi spawn** thuộc vòng quản lý 3a-2, không thể thay bằng từ chối sự kiện sau khi đã chạy.


### 17.1 Đối chiếu đợt 3 (tĩnh; không thêm quyết định đã duyệt)

- Mốc mã bàn giao `eb97f87` đã có 3a-1; 3a-2 và 3b vẫn là plan. Mã mẫu tạo `BoCLI/BO_CLI` ở 3b Task 13, không giả registry đã tồn tại ở 3a-2.
- Credential `ma_giao` che trước khi ghi log/digest cả Claude và Codex. `can-hoi` thắng `xong` nếu cùng lần xử lý; không tự vượt Q6.
- Phiếu phục hồi phải được nhịp tim xác nhận đúng `giao_id/luot` trước spawn; đang chuẩn bị vẫn giữ lease. Máy bị thu hồi hoặc hết lease dừng cứng; ngân sách 90 phút không cấp thêm quyền giữ phiếu.
- Không mở ghi toàn bộ Git common-dir. Cổng S6 phải chứng minh ghi commit thành công đồng thời không sửa config/hooks/ref khe khác. Cổng S2/S6 kiểm auth dưới đúng service/principal; không lấy fixture làm bằng chứng sandbox đọc Keychain được.
- S5 chưa cho phép mở endpoint OpenAI: Q15 whitelist hiện hành vẫn giữ nguyên, cần Đại ca duyệt endpoint sau spike. Hai lựa chọn §14 tiếp tục chưa chốt.

## Trạng thái triển khai (15/10/2026)

Đối chiếu với mã trên `main` (1c5f507, 1987 test pass). Đã có mã cho cả 3a-1, 3a-2 và 3b, nhưng chưa thợ thật nào chạy. Mọi spike S1–S8 chưa chạy. Hai đề xuất ở §14 chưa chốt. Bộ giao việc chưa bật (`giao_viec.bat = false`), nên chưa phiếu thật nào được phát.

**Cập nhật 16/10/2026:** đối chiếu lại với `main` `f5b1fdb`. Lát 3c mới có ba task đã code và ghép: Task 2 (trao quyền không đi theo symlink, `bs-urj.15`), Task 4 (bỏ qua lỗi `sudo bootout`, `bs-urj.16`) và Task R3 (nguồn công bố `lai`, D4/D34). Các task còn lại của 3c (R1 trao quyền cho `tram-kiem` không root theo D22, R2 hoàn tác, cây kiểm có repo git một commit theo D40…) **chưa có mã**; plan 3c đang được sửa ở nhánh khác nên bảng dưới không mô tả chúng. Hàng đổi có nhãn "(16/10)".

**Cập nhật 17/10/2026 (I1):** đối chiếu lại với `main` `59f8281` (2697 test Python, 101 node) bằng `ls`/`grep` trong `tram/`. Đã ghép thêm cho phần 3: lát P1 + 3C-B (`0e33fbf`: primitive vòng đời tiến trình, UID thực, cổng lịch), bs-78r.10 Q1/Q2 (`0e33fbf`: quota đi qua principal của khe), 3c r47 T1, T3, T5, T6, T7, T8, T10 (`9ee1ed3`) và 3c đợt 8 (`59f8281`). Câu "các task còn lại của 3c chưa có mã" ở đoạn trên là trạng thái 16/10. Vẫn **chưa chạy thật**: S1–S8, G3, G4, G5 đều CHƯA CHẠY. Hàng đổi có nhãn "(17/10)". Kiểm lại dưới `tram-kiem` (Seatbelt, cổng lượt, R7) thuộc spec 4 §6.2.

| Mục spec | Trạng thái | Nơi trong mã | Plan/Task |
|---|---|---|---|
| §3 Hàm dùng chung với phần 4, khoá yaml mới | đã có mã + test | `tram/cau_hinh/{lenh,du_an}.py`, `tram/kiem/{duong_dan_cam,diff}.py`, `tram/ban_giao/schema.py` | 3a-1 |
| §5.1 Xác thực `/api/tho/*`, token máy, `tram chu go-may` | đã có mã + test | `tram/api/tho.py`, `tram/phieu/{may,yeu_cau_tho}.py`, `tram/tho/lenh.py` | 3a-1 |
| §6.1–6.3 Phiếu, `ma_giao`, nhịp tim kiêm xin việc, thẻ chắn, bộ canh | đã có mã + test | `tram/phieu/{mo_hinh,cap,nhip,nhip_tim,canh}.py` | 3a-1; nối `chon`/`con_hop_le`: 4a-2 T9, T13 |
| §6.4 Ref tạm, `da-push`, công bố CAS, đối soát | đã có mã, chờ cổng chạy thật (S7 + chốt §14). (16/10) thêm nguồn `lai` cho D4: `cong_bo.phuong_an: lai` — máy trong `kho_tho` dùng kho-tho, máy từ xa dùng ref tạm + CAS; tên `lai` Đại ca chốt ở D34; mặc định vẫn `None` | `tram/cong_bo/{nguon,nguon_lai}.py`, `tram/cau_hinh/cong_bo.py`, `tram/tho/day.py`, `tram/api/tho_them.py` | 3a-2 T9, T13–14, T16; 3c R3 |
| §6.5–6.6 Snapshot, kho phiếu bền, `request_id`, công việc chờ | đã có mã + test | `tram/phieu/{kho,luoc_do,ket_thuc,cong_viec,lan_chay}.py`, `tram/tho/hop_thu.py` | 3a-1; 3a-2 T8 |
| §7.1 Kho, worktree, môi trường kiểm, dọn | đã có mã + test; quyền ghi của principal chờ cổng chạy thật (S6) | `tram/tho/{worktree,chuan_bi,don_dep}.py`, `tram/kiem/moi_truong.py` | 3a-2 T17, T19–20 |
| §7.2 Chạy Claude headless, file quyền theo vai | đã có mã, chờ cổng chạy thật (S1–S4) | `tram/chay_cli/{claude,lenh_claude,stream,quyen}.py`, `vai/quyen/*.json` | 3a-2 T1–2, T12 |
| §7.2 Chạy Codex (`codex exec --json`) | đã có mã, chờ cổng chạy thật (S5, allowlist OpenAI) | `tram/chay_cli/codex/` | 3b T2, T7–8, T13 |
| §7.3 Cách ly: principal, sandbox, `tram-kiem`, kiểm chứng âm H9 | đã có mã, chờ cổng chạy thật (S6; chưa chọn cơ chế). (16/10) 3c Task 2: trao quyền ghi cho principal dùng `find` nên không đi theo symlink (`principal_khe.py`). (17/10) Một nguồn principal kiểm lại `cach_ly.tram_kiem` (`tram/cau_hinh/principal_kiem.py`); hồ sơ Seatbelt `tram-kiem` cấm mặc định, không mạng, không IPC (`tram/tho/quyen_kiem.py`, D45, D48). S6 chỉ thử cơ chế `user` (D53); nhánh `sandbox` giữ mã, cổng đóng | `tram/tho/{principal,principal_khe,sandbox,kiem_am}.py`, `tram/chu/kiem_cach_ly.py` | 3a-2 T3, T7, T11, T15 |
| §7.4 `tram bao`, hàng đợi | đã có mã + test | `tram/tho/{bao,bao_lenh,hang_doi,theo_doi}.py`, `tram/phieu/bao.py` | 3a-1; 3a-2 T18 |
| §7.5 Lệnh kiểm do thợ chạy | đã có mã + test. (17/10) Mọi chờ có hạn hữu hạn, thu hồi cả cây; treo sau SIGKILL → `da_thu_hoi = False` (P1) | `tram/kiem/{lenh_tho,chay_lenh}.py`; (17/10) `tram/kiem/{vong_doi,cay_tien_trinh,lenh_ngan}.py` | 3a-2 T18; P1 T1–T3 |
| §7.3, §7.6 (17/10) UID thực của principal, cổng lịch, hạn tổng harness | đã có mã + test; OS thật chờ G3 | `tram/kiem/{chay_gioi_han,danh_tinh,cong_lich,han_tong}.py` | P1 T6–T9 (3C-B) |
| §7.6 Kết thúc phiếu, hạn chót, lần chạy, mồ côi | đã có mã + test. (17/10) CLI của phiếu thu hồi cả cây có hạn; không xác nhận thu hồi → dừng khe, giữ pid cho dọn mồ côi (P1 T5). Còn: `mo_coi` không kiểm thời điểm khởi động của PID (`bs-863.15`); `theo_doi.py` còn `join()` không hạn (`bs-863.16`) | `tram/tho/{ket_thuc,mot_lan,vong_khe,mo_coi}.py` | 3a-2 T17–19; P1 T5 |
| §7.7 Bàn giao tạm do thợ dựng | đã có mã + test; hook `PreCompact` chờ cổng chạy thật (S8) | `tram/tho/ban_giao_tam.py`, `tram/chay_cli/quyen.py` | 3a-2 T2, T6 |
| §8.1 Nguồn hạn mức Claude (stream, log, regex) | đã có mã, chờ cổng chạy thật (S1) | `tram/han_muc/{mo_hinh,claude,log_claude,nguon}.py` | 3a-1; 3a-2 T1 |
| §8.1 Nguồn hạn mức Codex (app-server, rollout) | đã có mã, chờ cổng chạy thật (S5). (17/10) Đọc hạn mức khe rảnh **qua principal của chính khe** (wrapper, env dựng mới, kill qua principal); thiếu principal thì không spawn; UID thực xác minh ở nhịp đầu; lỗi/treo không làm chết nhịp tim, không lộ token (bs-78r.10, Q1/Q2; `tram/tho/han_muc_ranh.py`). Chạy thật chờ G5 | `tram/chay_cli/codex/{han_muc,app_server}.py` | 3b T2, T7 |
| §8.2 `duoc_nhan` | đã có mã + test | `tram/han_muc/luat.py` | 3a-1 |
| §8.3 Trần lần chạy, cầu dao | đã có mã + test | `tram/phieu/cau_dao.py`, `tram/tho/so_khe.py` | 3a-1; 3a-2 T8 |
| §9.1 `tho.yaml`, `them-khe`/`bot-khe`, `tat-khe`/`bat-khe` | đã có mã + test | `tram/tho/{cau_hinh,cau_hinh_chay,lenh_khe,lenh}.py` | 3a-1; 3a-2 T5, T20 |
| §9.1 Cài máy B: user, sudoers, LaunchDaemon `vn.tram.tho` | đã có mã, chờ cổng chạy thật (S2, S6). (16/10) 3c Task 4: `thuc_hien` bỏ qua lỗi `launchctl bootout`/`pkill` kể cả khi chạy qua `sudo` (`tram/chu/cai_dat.py`). (17/10) `cai-dat-tho` có sổ journal (đuôi dở cắt có bằng chứng, khoá cài/gỡ); user và nhà là hai bước; sudoers `tram-kiem` không NOPASSWD root (D22); cài hồ sơ Seatbelt `tram-kiem` cho cả hai cơ chế. `tram chu go-cai-dat-tho`: chỉ gỡ thứ sổ ghi `da_tao`, nhà là bước riêng (`--xoa-nha`), chờ `dong-y` | `tram/chu/{cai_dat_tho,lenh_tho}.py`; (17/10) `tram/chu/{cai_dat_kiem,so_cai_tho,go_cai_dat_tho,tai_nguyen,nhat_ky}.py` | 3a-2 T15; 3c r47 T1, T6, T8, 3C-D6a |
| §9.2 Ghép Mac từ xa: `cap-ma`, `/api/ghep-may`, `dang-ky` | đã có mã, chờ cổng chạy thật (#5, S6, S7) | `tram/phieu/ma_ghep.py`, `tram/api/ghep.py`, `tram/chu/cap_ma.py`, `tram/tho/{lenh_dang_ky,ke_hoach_dk,thuc_hien_dk,launchd_tho,token_may}.py` | 3b T1, T6, T9–11 |
| §9.3 `tram tho kiem` | đã có mã + test; các mục chờ cổng báo vàng. (17/10) Mục hạn mức khe Codex đọc dưới principal của khe sau khi xác minh UID thực; không thu hồi được → ĐỎ. `codex login status` vẫn chạy dưới tài khoản quản lý (`bs-863.17`) | `tram/tho/{kiem_may,kiem_cong,kiem_3b,do_may}.py` | 3a-2 T11; 3b T4, T12 |
| §10, §10.1 Sự kiện, `trang_thai_khe`, `/api/noi-bo/phieu` | đã có mã + test | `tram/phieu/{trang_thai,su_kien_chay}.py`, `tram/api/noi_bo.py` | 3a-1 |

### Lệch so với spec khi code

- §8.1 (3a-2 T1): trước khi S1 chốt thang đo, bộ đọc **không** đọc `utilization` (`thang=None`). Mọi cửa sổ Claude vì thế là "chưa biết". Khe vẫn nhận việc theo luật 3 của §8.2 (`tram/han_muc/claude.py`).
- §8.2: ngưỡng ngừng phía thợ cố định 90% (`NGUONG_NGUNG` trong `tram/tho/mot_lan.py`), không đọc `han_muc.ngung` của trạm. Trạm vẫn tự áp luật 1 khi cấp phiếu.
- §6.4: chưa chốt §14 nên mặc định `cong_bo.phuong_an = None`. Khi đó `/api/tho/da-push` trả 503 `chua-chot-phuong-an` và trạm không công bố ref nào.
- §7.1 (3a-2 G12): thợ không nghe `bead.dong` trực tiếp. Thợ hỏi trạm qua `POST /api/tho/da-dong` cho các worktree đang có, rồi mới dọn (`tram/tho/don_dep.py`).
- §7.4, §10 (3a-2 G11): `bao.bi.ly_do` có thêm `nhanh-bi-day-ngoai-luong` và `loi-may-tho`.
- §7.6, §17.1 (3a-2 T19): `VongKhe` so `han_giu` với đồng hồ thật của máy thợ và có watchdog lease, nên phiếu hết lease thì dừng cứng. Helper test `tests/tho_chay_gia.py::dung_may` phải truyền đồng hồ giả, nếu không 8 test treo. Mã trong `tram/` không đổi.
- §9.2 (3b T14, G4 review đợt 3): `tram tho dang-ky` từ chối ngay (`ValueError`) khi máy đã có `tho.yaml` hoặc service thợ, trước khi đổi mã ghép. Lệnh không chạy lại để sửa cấu hình cũ. Plist chỉ được dựng sẵn, chưa `bootstrap` cho tới khi qua S2/S6/S7.
- §9.1 (3a-2 rủi ro e): `tram tho them-khe` ghi lại `tho.yaml`, nên chú thích viết tay bị mất. Kế hoạch in rõ việc này trước khi hỏi `dong-y`.

Các hợp đồng mới khác (G2–G35 của 3a-2, G1–G19 của 3b) xem mục "Cần sửa spec sau" của hai plan đó.

### Cổng còn treo

| Cổng | Việc | Bead |
|---|---|---|
| S1–S4, S8 | Claude headless: `rate_limit_event`, Keychain dưới launchd, hai `CLAUDE_CONFIG_DIR`, cờ quyền, `PreCompact` | `bs-8eh.3` |
| S6, §14, H9 | Chọn cơ chế cách ly; quyền Git chung (G20); Keychain dưới sandbox (G34, G35); `tram-kiem` | `bs-8eh.4` |
| S7, §14 | Repo GitHub nháp, quyền push `tram/luot/*`, CAS, push treo, mất phản hồi | `bs-8eh.5` |
| S5, Q15 | Codex thật, allowlist endpoint OpenAI | `bs-8eh.6` |
| §9.2 (#5) | `tram tho dang-ky` thật trên Mac từ xa, bootstrap sau cổng | `bs-8eh.8` |
| G3 (17/10) | Đo trên macOS thật: cây `sudo`/`use_pty`, `kill -1`, Seatbelt dưới `sudo -u`, định dạng `launchctl print` (G3.3 có `sudo launchctl procinfo` do Đại ca tự gõ, D52) — kịch bản ở plan 3c Task 9 | `bs-8eh.4` |
| G5 (17/10) | Quota Codex dưới principal thật: UID khe, `CODEX_HOME` của khe, không dùng auth của quản lý, nhịp tiếp tục, log không lộ token | `bs-8eh.6`, `bs-8eh.4` |
| §15 mục 3 | Một bead `code` trên `B/claude-1` và một bước `qc` trên `B/claude-2` trong repo nháp | `bs-8eh.7` |

## Đồng bộ quyết định D1–D16 sau review đợt 4

Nguồn có thẩm quyền: [quyết định 15/10](../quyet-dinh/2026-10-15-chot-dot-4.md); không sửa quyết định. Những câu “chưa chốt” bên trên là lịch sử nếu đã có Dn thay thế:

- D1 chọn HR Codex bản sao trên B, sau Task 0; D2 chọn S1 sơ bộ → S6 → S1–S4 dưới principal; D3 thử user riêng mỗi khe trước, giữ nhánh sandbox dự phòng.
- D4 chọn công bố lai, chính thức sau S7. Snapshot có hai adapter nhưng chỉ chọn một nguồn toàn cục; **chưa có mã phối hợp lai trên cùng trạm**. Task 3c R3 bổ sung phần thiếu; không đánh đồng “có cả hai adapter” với “đã hỗ trợ D4”. **Cập nhật 16/10:** R3 đã ghép (`NguonLai`, `cong_bo.phuong_an: lai`, D34); D4 chỉ chính thức khi S7 đạt.
- D6 máy A chưa có Tailscale; D7 giữ memory đã cài; D8 chờ QC đạt đối với bàn giao code, spike giữ kiểm-lại đạt; D9/D10 không bỏ escalation máy móc/không cờ nguồn; D11 restart ngay sau 1b-4 T4 hoàn chỉnh.
- D12 đèn từ hook máy A: đã có plan 2e, chưa có mã/hook chạy thật. D13 không tự chọn S1–S8 của bảng điểm; D14 lọc mọi dự án/30 ngày mặc định; D15 cả hai loại tin PR. Mã snapshot chưa có các bổ sung 2d/2e này. (16/10: 2d/2e đã có mã, không đổi gì ở phần 3.)
- D16: cổng ADR không còn chờ adapter/nguồn mới. Chỉ decision `blocks` đã đóng; callback ADR giữ False. Các hàng `bs-8eh.11` chờ chọn nguồn bên trên được thay bằng D16 đã chốt.

“Đã có mã + test” chỉ là có module và test trong gói; số pass là lời bàn giao, không phải kết quả review độc lập. Root helper/hoàn tác 3c còn blocker R1/R2; không nâng trạng thái chạy thật dựa vào patch áp được hoặc fixture. Xem `../../REVIEW-CODEX.md` và sổ tay đã sửa đường cài dịch vụ.

