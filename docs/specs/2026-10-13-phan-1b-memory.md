# Phần 1b — Memory chung nhiều dự án

Status: `ĐÃ DUYỆT` — Đại ca duyệt trên chat 13/10/2026 (trước đó: nháp Em viết đêm 13/10/2026; qua ba vòng review của Fable và một vòng review độc lập của Codex; Đại ca đã trả lời câu hỏi 13/10 — §13)
Ngày: 2026-10-13 (sửa lần 2 cùng ngày: [quyết định 13/10](../quyet-dinh/2026-10-13-tra-loi-cau-hoi-gop.md) và [phản hồi review Codex](../handovers/2026-10-13-phan-hoi-review-codex.md); sửa lần 3 cùng ngày: khớp mã lát 1b-1 đã merge — mục "Cần sửa spec sau" và các giả định lệch chữ/hợp đồng mới của [plan 1b-1](../plans/2026-10-13-lat-1b-1-memory.md), gồm quyết định G3, G9, G13 Đại ca chốt 13/10; không đổi phạm vi đã duyệt)
Kiến trúc tổng: [2026-10-12-tram-dieu-phoi-kien-truc.md](2026-10-12-tram-dieu-phoi-kien-truc.md) (Q4, Q5, Q8, Q15, §5.1 lớp 5, **§5.4**, §6 dòng memory crewAI, §10 dòng crewAI)
Phần dùng kết quả: 1a (bài học khi chấm cột), phần 4 (lớp 5 của gói ngữ cảnh), phiên Claude/Codex trên máy thợ và máy A (qua MCP)

## 1. Mục tiêu

Bài học và quyết định không mất giữa các phiên và các CLI: một khe làm bead dự án X nhận đúng **năm ký ức liên quan** về X, về vai của nó và về cách làm chung — và **không bao giờ** thấy ký ức nghiệp vụ của dự án khác.

**Ví dụ đầu–cuối.** Đại ca chốt câu hỏi của bead `hr-12` trên dashboard: "Hoa hồng tính trên giá sau giảm giá" → sự kiện `cot.da_chot` → memory service tách thành ký ức "HR Codex: hoa hồng sale tính trên giá sau giảm giá (Đại ca chốt 13/10)", luật cứng thấy chữ "hoa hồng"… không phải số tiền nhưng nguồn là `da_chot` → ghi vào `/du-an/hr-codex/nghiep-vu` → tuần sau phần 4 dựng gói cho bead `hr-40` "Hiện hoa hồng tạm tính" → `nho_lai` trả ký ức này trong ba ký ức dự án → coder không hỏi lại.

## 2. Tiêu chí thành công

Ngưỡng mặc định đã chốt tại #21/§13; vẫn cần đo và nghiệm thu, không suy kết quả từ review tĩnh.

| # | Tiêu chí | Ngưỡng |
|---|---|---|
| M1 | Lời gọi recall/ghi của bead dự án X đọc hoặc ghi ký ức ngoài vùng cấp `[/du-an/X, /vai/<vai>, /chung]`, trên bộ test rò rỉ | **0** |
| M2 | Lời gọi thiếu vùng cấp, vùng cấp sai dạng, mã phiếu sai hoặc thiếu, hoặc phiên tay thiếu/sai mã Đại ca được chấp nhận | **0** (từ chối 100%). Phiếu đã bị thu hồi: còn dùng được **tối đa 30 giây** theo ngoại lệ cache §9.2, sau đó từ chối 100% — test riêng trước, trong và sau cửa sổ này |
| M3 | Bản ghi có vector giả/băm khi embedder lỗi; recall trả bản ghi khác model hiện hành | **0** |
| M4 | Ký ức có tên khách, số tiền, tên module nằm ngoài `/du-an/<ten>/nghiep-vu`, trên bộ mẫu | **0** |
| M5 | Recall trên bộ 20 truy vấn mẫu: ký ức Đại ca đánh dấu "đúng" có trong 3 ký ức nhóm dự án trả về | ≥ 80% |
| M6 | Độ trễ recall trên máy B (p95, kho ≤ 10.000 ký ức, **gồm** embed truy vấn qua Ollama) | ≤ 800 ms |
| M7a | Hai bản `tram nho chay` chạy cùng lúc | **0** (khoá `flock`) |
| M7b | Mã ngoài `tram/nho/` import `lancedb` | **0** (test quét mã) |

## 3. Lát triển khai

| Lát | Nội dung | Chạy được khi |
|---|---|---|
| **1b-1** | Memory service (tiến trình riêng), lưu LanceDB, embedder Ollama `bge-m3`, vùng cấp + lọc, recall có chấm điểm, ghi có gộp; nạp ký ức từ sự kiện của 1a và 2a; HTTP nội bộ `/nho-lai` (1a dùng thay cho "5 sự kiện `cot.dai_ca_sua` gần nhất"; phần 4 lớp 5 dùng từ 4c) và `/xoa` (xoá mềm theo id, kèm lệnh `tram nho xoa` — §9.1, §9.5) | 1a và **2a** chạy (cần `KhoSuKien.sau_id()`, sự kiện `cot.da_chot`, `cot.tra_ve`, `vi_sao`); chỉ cần `tram-nho-token` — **không** cần phần 3, không gọi API phiếu; Ollama + bge-m3 (#5 — **chưa duyệt**); spike N1 |
| *(adapter nguồn của phần 3/4)* | Nạp bàn giao (`kiem.lai` + `bao.xong`), `escalation.dong`, `spec.tra_ve` | chỉ bật khi phần 3 có kho phiếu + `tram-noi-bo-token` và phần 4 tương ứng đã triển khai. **Ghi chú 16/10, D8, D10 (lát 1b-4, đã có mã):** nguồn bật cùng mã, không cờ (D10); sự kiện chỉ có khi phần 4 chạy. Không cần `tram-noi-bo-token`: `vai` lấy từ sự kiện `giao.nhan` trong kho sự kiện, memory không gọi mạng |
| **1b-2** | MCP HTTP cho CLI trên máy thợ (theo phiếu) và phiên tay trên máy A (chỉ đọc — #20) | phần 3a có kho phiếu + `ma_giao` + `tram-noi-bo-token`; spike N2. Trước 1b-2, thợ **không** cấu hình MCP memory và không truyền URL giả; pipeline vẫn chạy lớp 1–4 |
| **1b-3** | Thăng cấp lên `/chung` và `/vai/*`; màn xem/xoá/ghi tay ký ức trên dashboard (phần 2 thêm `/api/nho/*`) | 1b-1 chạy ổn ≥ 1 tuần |

## 4. Phạm vi và vùng cấp (thực hiện §5.4 kiến trúc)

**Phạm vi** của một ký ức là đúng **một** trong bốn dạng:

```
/du-an/<ten>/nghiep-vu    luật nghiệp vụ, quyết định của Đại ca, tên khách, số tiền, module
/du-an/<ten>/cach-lam     cách làm việc trong repo này (lệnh test, bẫy, quy ước)
/vai/<vai>                bài học theo vai (coder, qc, spec, cham-cot, dieu-phoi…) — chỉ qua thăng cấp hoặc Đại ca ghi tay
/chung                    bài học cách-làm đúng ở ≥ 2 dự án — qua thăng cấp hoặc Đại ca ghi tay (#18)
```

**Vùng cấp** là danh sách phần tử trạm chủ cấp cho một lời gọi. Mỗi phần tử phải là một trong: `/du-an/<ten>`, `/du-an/<ten>/nghiep-vu`, `/du-an/<ten>/cach-lam`, `/vai/<vai>`, `/chung` — `<ten>` và `<vai>` khớp `[a-z0-9-]+`. Phần tử khác (`/`, `/du-an`, `/vai`, rỗng) → **từ chối cả lời gọi** (M2). Vùng cấp rỗng hoặc thiếu → từ chối; không có "tìm toàn kho".

**Lọc** (so khớp chính xác, cấm so tiền tố chuỗi): trạm **mở rộng** vùng cấp thành tập phạm vi đầy đủ — `/du-an/X` → `{/du-an/X/nghiep-vu, /du-an/X/cach-lam}`, các dạng khác giữ nguyên — rồi lọc `pham_vi IN (tập đó)`. Ví dụ `/du-an/hr` không bao giờ khớp `/du-an/hr-codex/cach-lam`. Đây là cách làm đúng ý "so khớp chính xác" của §5.4 mà không cần mảng tổ tiên (§13 câu 7).

**Ai cấp vùng — LLM không bao giờ chọn:**

| Người gọi | Vùng cấp | Nguồn |
|---|---|---|
| Bộ chấm cột 1a, dự án X | `[/du-an/X, /vai/cham-cot, /chung]` | mã 1a |
| Phần 4 dựng gói cho bead dự án X, vai V | `[/du-an/X, /vai/V, /chung]` | phiếu giao |
| CLI trên máy thợ (1b-2) | như phiếu giao đang giữ | memory service tra phiếu qua `giao_id` + `ma_giao` (§9.2) |
| Phiên tay của Đại ca trên máy A (1b-2) | `[/du-an/X, /vai/dieu-phoi, /chung]`, **chỉ đọc** | header tĩnh `X-Tram-Du-An: X` theo thư mục dự án (§9.3, câu 10) + mã Đại ca |

## 5. Mô hình ký ức

```json
{
  "id": "m-01J…",
  "noi_dung": "Test PHP chạy bằng `php artisan test --filter <Ten>`; không dùng phpunit trực tiếp vì thiếu bootstrap.",
  "pham_vi": "/du-an/hr-codex/cach-lam",
  "nhan": ["test", "php"],
  "quan_trong": 0.6,
  "nguon": [{"loai": "ban_giao", "du_an": "hr-codex", "bead_id": "hr-6xe1", "su_kien_id": 812}],
  "nguon_dai_ca": false,
  "hieu_luc_tu": "2026-10-13T02:00:00Z",
  "tao_luc": "2026-10-13T02:00:00Z", "dung_luc": null, "so_lan_dung": 0,
  "mo_hinh_embed": "bge-m3@<digest>", "so_chieu": 1024, "vector": [ … ],
  "da_xoa": false
}
```

- `nguon` bắt buộc. `nguon.loai` ∈ `da_chot | dai_ca_sua | tra_ve | dai_ca_ghi | ban_giao | agent | thang_cap`. Nguồn `ban_giao`, `agent` có thêm `vai` (lấy từ phiếu) để thăng cấp biết "cùng vai".
- `hieu_luc_tu` (ISO): ký ức thăng cấp = `tao_luc + 7 ngày`, nguồn khác = `tao_luc`. Recall chỉ xét `hieu_luc_tu ≤ bay_gio`.
- `tao_luc` của ký ức tách từ một sự kiện = **giờ của sự kiện nguồn**, không phải giờ nạp — nạp lại lịch sử không làm ký ức cũ thành "mới" ở bước chấm độ mới (§7). Bản do gộp soạn lại lấy `tao_luc` = lúc gộp (§6.3). (Chốt ở plan 1b-1 Task 19, không có trong bản duyệt 13/10 — Đại ca xác nhận cùng bản sửa này.)
- `nguon_dai_ca = true` khi mọi nguồn thuộc `da_chot | dai_ca_sua | tra_ve | dai_ca_ghi` — ký ức "của Đại ca", được bảo vệ khi gộp (§6.3).
- `quan_trong` ∈ [0, 1]: bước tách đặt, có **sàn tất định** theo nguồn: `da_chot`, `dai_ca_ghi` ≥ 0,8; `dai_ca_sua`, `tra_ve` ≥ 0,6.
- **Ghi chú 16/10 (1b-4):** trần ngược lại cho chữ do agent viết: ký ức mà **mọi** nguồn là `ban_giao` hoặc `agent` có `quan_trong` ≤ **0,6**, để chữ của agent không tự xếp ngang chữ của Đại ca (`TRAN_NGUON_AGENT` trong `tram/nho/mo_hinh.py`). Prompt tách phiên bản 2 (`vai/nho-tach.md`) phân biệt chữ Đại ca với bàn giao của agent.
- `mo_hinh_embed` gồm tên + digest model (`bge-m3@<digest>`, digest lấy từ `GET /api/tags` của Ollama) để đổi bản `bge-m3` thì phát hiện được. Vector **tự chuẩn hoá L2** trước khi lưu.
- Xoá là **xoá mềm** (`da_xoa = true`, sự kiện `nho.xoa`). Xoá cứng chỉ bằng lệnh riêng của Đại ca (1b-3).

## 6. Ghi ký ức

### 6.1 Nguồn và gốc

| Nguồn | Sự kiện | Gốc ghi (trạm quyết) |
|---|---|---|
| Đại ca sửa cột (1a, 2a) | `cot.dai_ca_sua` — có `vi_sao` (dashboard ghi): tách bằng LLM như thường; không có `vi_sao` (sửa qua `bd`, 1a phát hiện): **không gọi LLM**, ký ức dựng tất định = `"<tieu_de>": hệ xếp <cot_he>, Đại ca chuyển <cot_moi>. Lý do hệ: <ly_do_he>`, nhánh `cach-lam`, `quan_trong` sàn 0,6 — để 1a không mất bài học khi chuyển sang recall | `/du-an/X` |
| Đại ca trả lời escalation (4a) | `escalation.dong {tra_loi}` | `/du-an/X` (luôn `nghiep-vu`, `nguon.loai = da_chot`, sàn 0,8) |
| Đại ca trả về spec (4b) | `spec.tra_ve {gop_y}` (`nguon.loai = tra_ve`) | `/du-an/X` |
| Đại ca chốt câu hỏi (2a) | `cot.da_chot {decision_id, cau_hoi[], tra_loi[], adr?}` | `/du-an/X` (luôn `nghiep-vu`) |
| Đại ca trả về (2a) | `cot.tra_ve {gop_y}` | `/du-an/X` |
| Bàn giao chính thức đã qua kiểm của phần 4 | theo D8: code thường kích hoạt bởi `qc.ket_qua {ket_luan: "dat"}` rồi tìm `kiem.lai` đạt tương ứng; spike không QC kích hoạt bởi `kiem.lai {giao_id, dat: true}`; từ lần kiểm đó tra ngược `bao.xong` cùng `giao_id` lấy khối bàn giao: `quyet_dinh`, `huong_da_bo`, `vuong_mac`; ~~`vai` lấy từ `GET /api/noi-bo/phieu/{giao_id}` (trả cả khi phiếu đã hết hiệu lực)~~ `vai` lấy từ sự kiện `giao.nhan` cùng `giao_id` (16/10, D8 và 1b-4 G3: không gọi mạng từ memory) | `/du-an/X` |
| Agent tự ghi (1b-2) | công cụ MCP `ghi_nho(noi_dung, nhan?)` | `/du-an/X` của phiếu |
| Thăng cấp (1b-3) | §8 | `/chung` hoặc `/vai/<vai>` |
| Đại ca ghi tay (1b-3) | dashboard | bất kỳ phạm vi, Đại ca chọn |

> **Ghi chú 16/10, D8, D23 (lát 1b-4, đã có mã** `tram/nho/{cac_nguon,nguon_ban_giao,nguon_giao_viec,bi_mat}.py`**):**
>
> - **Bàn giao (D8, chặt hơn chữ spec gốc).** Bead thường kích hoạt bởi `qc.ket_qua {ket_luan: "dat", commit_code}` của lượt QC tương ứng, rồi tra ngược `kiem.lai` đạt cùng bead có `commit = commit_code` (ghi trước nó), rồi `bao.xong` cùng `giao_id` và lượt. `kiem.lai` đạt một mình chưa đủ. Phiếu spike (không QC) nhận ra bằng `kiem.lai {dat: true, ket_qua: []}` và giữ điều kiện `kiem.lai` đạt. Mọi tra ngược trong cùng dự án + bead. Không nạp bàn giao `tam`, QC trả về, hay `khong_cong_nhan`.
> - **Một bàn giao một lần.** Chống trùng chỉ xét QC nằm sau chính lần kiểm lại đó, nên một chu kỳ mới sau `cot.tra_ve` có phiếu mới giữ nguyên SHA vẫn có bàn giao mới.
> - **Nội dung.** Chỉ ba trường `quyet_dinh`, `huong_da_bo`, `vuong_mac`; mỗi danh sách tối đa 8 mục, mỗi mục tối đa 400 ký tự. Nguồn `ban_giao` không bao giờ là nguồn Đại ca; gốc ghi do trạm đặt.
> - **Escalation (D9).** `escalation.dong` chỉ lấy `tra_loi` (nguồn `da_chot`, luôn `nghiep-vu`, sàn 0,8) và `ly_do` do trạm đặt; **không** lấy câu hỏi gốc (do agent viết). `tra_loi` rỗng thì bỏ. `spec.tra_ve` lấy `gop_y` (nguồn `tra_ve`, sàn 0,6).
> - **Không cờ bật tắt** (D10). Điểm vào duy nhất là `doc_nguon`; vòng nạp, `la_nguon` và `tram nho thu` đều dùng nó.
> - **Chưa nạp:** bàn giao của phiếu `qc` và phiếu `spec` (D43, để sau).
> - **Chưa quét bí mật:** nguồn 1b-1/1b-2 (`cot.*`, `nho.agent_ghi`) chưa qua bộ quét (D40, để lát sau).

Không nạp bàn giao `tam`. Memory service đọc sự kiện mới bằng **vòng lặp trong tiến trình `tram nho chay`** (không phải job launchd riêng), mỗi 2 phút, mốc riêng `moc_nho` (id sự kiện cuối đã xử lý — cần `KhoSuKien.sau_id()` của spec phần 2 §12).

### 6.2 Các bước (tất định trước, LLM sau — Q5)

Trước mỗi lượt: gọi thử Ollama; chết → không làm gì, sự kiện `nho.loi_embedder`, mốc không tiến (không đốt token tách rồi làm lại).

**Lỗi làm đứng vòng nạp** (khác lỗi của riêng một sự kiện):
- Embedder lỗi (trước lượt hoặc ở bước 4) và **lỗi Claude API** (mạng, 5xx, khoá sai — khác "hết lượt guardrail" ở bước 1) → dừng cả lượt, không ghi gì, mốc không tiến, lượt sau (2 phút) thử lại.
- Báo **một lần mỗi đợt lỗi**: `nho.loi_embedder` hoặc `nho.loi_llm {su_kien_id, loi}`, ghi vào `du_an` + `bead_id` của **sự kiện nguồn đang kẹt** (thao tác dở trước, rồi sự kiện nguồn đầu tiên sau mốc) — không ghi vào `_tram`, vì dashboard chỉ liệt kê dự án trong `du-an/*.yaml`. Không có sự kiện nguồn nào đang chờ thì chỉ ghi log.
- Còn lỗi hay không đọc từ bảng sự kiện: còn lỗi khi `nho.loi_<loai>` mới hơn `nho.phuc_hoi` cùng loại. Không giữ cờ trong bộ nhớ, nên khởi động lại giữa đợt lỗi không ghi lặp.
- Sự kiện nguồn của dự án đó xử lý xong (áp dụng hoặc bỏ) → `nho.phuc_hoi {loai: "llm" | "embedder"}`.
- Hai lỗi này hiện ở "Hệ cần xem" trên dashboard và báo Telegram như trạm lỗi tới khi có `nho.phuc_hoi` cùng loại (spec phần 2 §5, §6).
- **Ghi chú 16/10 (1b-4 G14):** lỗi khoá SQLite (`sqlite3.OperationalError`) khi tra ngược kho sự kiện **không** phải sự kiện độc: vòng nạp ném lại lỗi, mốc không tiến, lượt sau thử lại; sự kiện không bị bỏ (`tram/nho/vong.py`).

**Sự kiện "độc"** — một sự kiện hỏng không được chặn cả hàng đợi:
- `du_an` không đúng dạng tên dự án (`[a-z0-9-]+`) → không phải sự kiện nguồn, mốc tiến.
- Dữ liệu sai kiểu (ví dụ `cau_hoi` không phải mảng), `du-an/<ten>.yaml` hỏng hoặc sai khoá, vùng cấp sai → `nho.loi_tach {su_kien_id, loi}`, **bỏ** sự kiện, mốc tiến. Trong lúc yaml của một dự án hỏng, sự kiện nguồn của dự án đó bị bỏ, có `nho.loi_tach` để biết.

**Chính sách bí mật (D23, 16/10; lát 1b-4, `tram/nho/bi_mat.py`)** — "quét để chặn":
- Nguồn phần 3/4 (`ban_giao`, `da_chot` từ escalation, `tra_ve` từ spec) được quét trên **mọi trường chữ gốc, chưa cắt**, TRƯỚC khi gửi LLM, embed hay lưu.
- Bốn nhóm dấu hiệu: `khoa_da_biet` (tiền tố khoá đã biết, token bot Telegram, JWT…), `khoa_rieng` (khối khoá riêng), `gan_gia_tri` (gán giá trị nhạy cảm như `password=`, chuỗi kết nối có mật khẩu, dòng `.env`), `entropy_cao` (chuỗi dài ≥ 32 ký tự có entropy trên 4,2 bit/ký tự, hoặc trên 3,0 nếu thuần hex; SHA 40/64 ký tự, UUID, đường dẫn không tính).
- Có dấu hiệu → bỏ **cả nguồn**: không gửi LLM, không lưu, ghi sự kiện `nho.bo_bi_mat {su_kien_id, loai_nguon, nhom: {<nhóm>: <số>}}` (xem §9.4) **không kèm đoạn khớp hay vị trí**, mốc tiến, **không thử lại**. `tram nho thu` bỏ y hệt và chỉ in nhóm + số lượng.
- Chấp nhận báo nhầm và mất nguồn đó. Bộ quét dùng biểu thức chính quy hữu hạn: **không** bắt được mọi bí mật viết tự do, và không tuyên bố ngược lại.

1. **Tách** (LLM; bỏ qua với `ghi_nho` và Đại ca ghi tay): từ một sự kiện, sinh 0–3 ký ức ngắn, tự đứng được. Schema đầu ra: `[{noi_dung, nhanh: "nghiep-vu"|"cach-lam", nhan[], quan_trong, co_ten_rieng: bool}]`. Guardrail + thử lại tối đa 3 lần như 1a. Nội dung sự kiện bọc `<du_lieu_khong_tin_cay>`. Hết lượt hoặc model từ chối → sự kiện `nho.loi_tach {su_kien_id, loi}`, **bỏ** sự kiện đó, mốc tiến.
2. **Đặt phạm vi** (tất định): `pham_vi = <gốc §6.1> + "/" + nhanh`. LLM chỉ chọn `nghiep-vu`/`cach-lam` — không bao giờ chọn gốc. Nguồn `da_chot` luôn `nghiep-vu`. `ghi_nho` không có bước tách: nhánh do bước 3 quyết (chạm → `nghiep-vu`, không → `cach-lam`).
3. **Luật cứng nghiệp vụ** (tất định, sau LLM, ghi đè LLM) → ép về `/du-an/<ten>/nghiep-vu` khi ký ức chứa:
   - **số tiền**: regex trên văn bản chuẩn hoá NFC, chữ thường: `\d[\d.,\s]*\s?(đ|₫|vnđ|vnd|usd|triệu|tr|tỷ|tỉ|nghìn|ngàn|k)(?!\w)` hoặc `\$\s?\d` — `(?!\w)` sau đơn vị (không dùng `\b` vì `₫` không phải chữ) để "3 điểm", "2 đường", "10 địa chỉ" không khớp; chấp nhận báo nhầm ("2 nghìn dòng"); plan chốt ≥ 10 ca test gồm "3 điểm kiểm" (không khớp) và "100₫", "10k" (khớp);
   - **tên module**: khớp **trọn từ, phân biệt hoa thường** với danh sách `module` mới trong `du-an/<ten>.yaml`, hoặc dạng `Modules/<Ten>` / `<Ten>Controller` (tránh "plan", "book" tiếng Anh thường);
   - **tên khách**: khớp danh sách `tu_khoa_khach` trong `du-an/<ten>.yaml` (Đại ca điền, có thể trống) **hoặc** `co_ten_rieng = true`.
   Phạm vi đích **không** thuộc `/du-an/*` (Đại ca ghi tay vào `/vai/*`, `/chung`; thăng cấp) mà chạm luật (xét với danh sách của **mọi** dự án đã `them`) → **từ chối**, sự kiện `nho.tu_choi {ly_do}`, dashboard báo.
4. **Embed** bằng `bge-m3` qua Ollama `127.0.0.1:11434`, chuẩn hoá L2. Lỗi giữa chừng → dừng cả lượt, sự kiện `nho.loi_embedder` (một lần mỗi đợt lỗi — xem trên), không ghi gì, mốc không tiến. Không bao giờ lùi về vector giả/băm (M3).
5. **Gộp** (§6.3) — chỉ trong **cùng `pham_vi`**.
6. **Ghi**, sự kiện `nho.ghi {id, pham_vi, nguon}`.

### 6.3 Gộp

- Ứng viên: tối đa **3** ký ức cùng `pham_vi`, chưa xoá, cùng `mo_hinh_embed`, cosine với ký ức mới ≥ **0,85**, cao nhất trước. Không có → ghi mới. Một sự kiện tách ra nhiều ký ức: bản cũ đã bị `gop`/`thay` ở ký ức trước **không** còn là ứng viên của ký ức sau (không sinh bản trùng). Bước gộp tự lọc lại ứng viên theo `pham_vi` và `da_xoa`, không tin bên gọi.
- Đầu ra LLM gộp sai schema (thiếu quyết định cho một ứng viên, sai kiểu) → thử lại; hết 3 lượt **hoặc model từ chối** thì coi mọi ứng viên là `giu_ca_hai`: ghi ký ức mới, giữ nguyên bản cũ. Khác bước tách (§6.2 bước 1): lỗi ở bước gộp không bỏ sự kiện.
- LLM quyết cho từng ứng viên: `giu_ca_hai | gop | thay`.
  - `thay`: xoá mềm bản cũ, ghi bản mới.
  - `gop`: xoá mềm bản cũ, ghi bản LLM soạn lại; `nguon` = hợp hai bên, `quan_trong` = max, `tao_luc` = bây giờ.
  - Sự kiện `nho.gop {cu[], moi}`.
- **Bảo vệ ký ức của Đại ca** (#18, tất định, ghi đè LLM): ký ức `nguon_dai_ca = true` chỉ bị `thay`/`gop` bởi ký ức mới cũng có `nguon_dai_ca = true`; với mọi nguồn khác (`ban_giao`, `agent`, `thang_cap`) chỉ được `giu_ca_hai`.
- **Kiểm lại nội dung cuối** (Q11 của review): mọi văn bản do `gop`/`thay`/thăng cấp tạo ra phải qua lại kiểm schema, giới hạn độ dài và **luật cứng nghiệp vụ** (§6.2 bước 3) trên **nội dung cuối**, rồi **embed lại nội dung cuối** trước khi ghi — vector luôn biểu diễn đúng văn bản đã lưu. LLM không được sửa `pham_vi`, `nguon`, `nguon_dai_ca`, `hieu_luc_tu`, `id` hay metadata quyền; các trường này tính tất định. Lỗi ở bất kỳ bước nào giữ nguyên các bản cũ.
- **Giới hạn của luật cứng:** bộ nhận diện tên/số tiền/module không bảo đảm "không bao giờ rò nghiệp vụ" — nghiệp vụ không có tên khách, số tiền hay tên module vẫn có thể bị xếp `cach-lam`. M4 là kết quả trên bộ mẫu; bộ mẫu M4 phải có các ca đối kháng loại này. Đây là rủi ro còn lại của #19 (thăng cấp tự động) để Đại ca biết.

### 6.4 Chống lặp và khôi phục sau sự cố (Q13 của review)

Một tiến trình ghi không tự có giao dịch xuyên LanceDB và SQLite. Hợp đồng:

- **Đơn vị xử lý = một sự kiện nguồn**, có ID thao tác bền `(su_kien_id, phien_ban_pipeline)`.
- Trước khi áp dụng: lưu **kết quả tách** (danh sách ký ức dự kiến với **ID ký ức ổn định** suy từ ID thao tác + số thứ tự) vào nhật ký thao tác `~/.tram/nho/nhat-ky.db` (SQLite của memory service).
- Áp dụng từng ký ức **idempotent theo ID ký ức**: ghi đã có thì bỏ qua; gộp/thay đã xoá mềm bản cũ thì không xoá lần hai.
- Chỉ **tiến mốc** `moc_nho` sau khi mọi ký ức của sự kiện đã áp dụng xong và nhật ký đánh dấu hoàn tất.
- Khởi động lại: đọc nhật ký, **đối soát** thao tác dở với LanceDB (bản ghi theo ID có chưa, bản cũ đã xoá mềm chưa) rồi làm tiếp; không cần giao dịch phân tán nhưng phải đối soát được.
- Embed lỗi **trước** khi áp dụng → giữ nguyên kho cho sự kiện đó, mốc không tiến; sự kiện trước đã hoàn tất không bị hoàn tác. Một ký ức lỗi trong sự kiện ba ký ức → cả sự kiện chưa hoàn tất, làm lại từ nhật ký.
- Recall, gộp, thăng cấp, ghi thống kê `dung_luc` và dọn phiên bản LanceDB được **tuần tự hoá** trong tiến trình ghi.
- **Sao lưu** gồm cả thư mục LanceDB, nhật ký thao tác và `moc_nho` tại cùng một điểm (dừng ghi trong lúc chụp); khôi phục từ bản sao lưu phải nhất quán giữa ba thứ. Cách làm (1b-1):
  - **Lịch và nơi lưu.** Mỗi ngày một lần sau 03:00 giờ VN, trong `tram nho chay`: `optimize` (§9.4) rồi chụp, trong lúc giữ khoá kho, `lancedb/` và bản sao trực tuyến `nhat-ky.db` (chứa `moc_nho`) vào `~/.tram/sao-luu/nho-<UTC>/`. Giữ 14 bản.
  - **Bản dở và lặp lại.** Bản đang chụp mang tên `.dang-chup-*`, không bao giờ mang tên `nho-*`; bản dở của lần bị cắt ngang được dọn ở lần chụp sau. Ngày bảo trì gần nhất lưu ở `~/.tram/nho/bao-tri-cuoi` (ngoài nhật ký, vì khôi phục quay ngược nhật ký), nên khởi động lại trong ngày không chụp lần hai.
  - **Khôi phục.** `tram nho khoi-phuc <bản>` chỉ chạy khi dịch vụ đã dừng (khoá `flock` rảnh). Trước khi đổi chỗ, kiểm bản sao: `nhat-ky.db` qua `PRAGMA quick_check` (mở chỉ đọc) và có đủ bảng; bảng ký ức LanceDB mở được. Bản hỏng → từ chối, kho hiện tại không đổi. Kho hiện tại chuyển sang `~/.tram/nho/truoc-khoi-phuc-<UTC>/`, không xoá.
- Ca kiểm: crash ở từng bước (xoá mềm, ghi mới, sự kiện, mốc); phát lại hai lần không đổi số bản; MCP `ghi_nho` trong lúc dọn phiên bản/sao lưu; lỗi một ký ức trong sự kiện ba ký ức.

## 7. Recall

`nho_lai(truy_van, vung_cap, *, nhom={"du-an": 3, "vai": 1, "chung": 1}, bay_gio=None)`

1. Kiểm vùng cấp (§4); mở rộng thành tập phạm vi.
2. **Lọc trước, lấy ứng viên riêng từng nhóm** (Q12 của review): với **từng nhóm** có hạn mức (`du-an`, `vai`, `chung`), lọc `da_xoa = false`, `hieu_luc_tu ≤ bay_gio`, `mo_hinh_embed` = model hiện hành, `pham_vi IN (tập của nhóm đó)`, rồi lấy tối đa **50** ứng viên theo cosine **trong chính nhóm đó**. (Lấy 50 chung cho cả vùng có thể toàn ký ức dự án, làm mất hết ứng viên vai/chung trước bước chia nhóm.)
3. Chấm: `diem = 0,5 · nghia + 0,3 · moi + 0,2 · quan_trong`, với `nghia = max(0, cosine)` (vector đã chuẩn hoá L2), `moi = 0,5 ^ (số ngày thực từ tao_luc tới bay_gio / 30)`. `bay_gio` tiêm được để test tất định. **Độ mới tính từ `tao_luc`**, không từ `dung_luc` — tránh vòng tự củng cố (ký ức hay được recall luôn "mới").
4. Chọn trong từng nhóm: sắp `diem` giảm dần (hoà → `tao_luc` mới hơn → `id`), lấy tối đa 3/1/1. Nhóm thiếu thì **không** bù bằng nhóm khác. Đầu ra tối đa năm ký ức, không bảo đảm đủ năm khi kho chưa đủ. Đây là xếp hạng trong tập ứng viên, không phải top tuyệt đối theo điểm tổng hợp toàn kho. Đo lại M6 với cách lấy ứng viên này.
5. Cập nhật `dung_luc`, `so_lan_dung` (chỉ để thống kê trên dashboard) — **gom** cập nhật, ghi tối đa mỗi 10 phút một lần cho cả kho (tránh tạo quá nhiều phiên bản LanceDB).

**Đầu ra cho gói ngữ cảnh (lớp 5)** và cho 1a: chỉ `{id, noi_dung, pham_vi}` — **không** trả `nguon` (tránh lộ tên dự án/bead khác qua `/chung`, `/vai`). `nguon` chỉ hiện trên dashboard của Đại ca. Người gọi bọc mỗi ký ức trong `<du_lieu_khong_tin_cay>`.

**1a dùng thế nào** (sửa ở 1a khi bật 1b-1): `bai_hoc_gan_day()` đổi sang `nho_lai(<tiêu đề + mô tả bead>, [/du-an/X, /vai/cham-cot, /chung])`, timeout 2 giây; `noi_dung()` của prompt chấm bọc mục bài học bằng `<du_lieu_khong_tin_cay>` và đổi tiêu đề thành "Bài học và quyết định đã ghi nhớ"; sự kiện `cham_cot.ket_qua` ghi `nguon_bai_hoc: "nho" | "su_kien"`. Memory service chưa cài (chưa có Keychain `tram-nho-token` → không gọi HTTP), tắt, lỗi, trả dữ liệu sai dạng, hoặc quá 2 giây → 1a lùi về 5 sự kiện `cot.dai_ca_sua` gần nhất (bỏ hẳn recall vector — không phải dùng vector giả). **Mọi** lỗi của bước recall đều lùi, không làm hỏng lượt chấm. 2 giây là **hạn tổng** của cả lời gọi, gồm đọc thân phản hồi: server trả nhỏ giọt không kéo dài được lời gọi. Còn hở: server treo ngay ở phần header chỉ bị chặn bởi timeout từng lần nhận dữ liệu.

## 8. Thăng cấp (1b-3)

- Chạy mỗi ngày trong `tram nho chay`. Cặp ứng viên: ký ức `/du-an/A/cach-lam` và `/du-an/B/cach-lam` (A ≠ B) cosine ≥ 0,85.
- Bỏ qua cặp đã có ký ức thăng cấp với `nguon` chứa cả hai id, **kể cả bản đã xoá mềm** — Đại ca xoá thì không tạo lại.
- **Đích do trạm tính** (tất định): cả hai ký ức gốc có `nguon.vai` giống nhau → `/vai/<vai>`; khác hoặc thiếu → `/chung`. LLM chỉ soạn nội dung tổng quát (bỏ chi tiết riêng dự án). Hệ quả: `/vai/cham-cot` (vùng của 1a) chỉ có ký ức Đại ca ghi tay, vì `cot.dai_ca_sua` không mang vai. Chạy **lại luật cứng nghiệp vụ với danh sách `module` và `tu_khoa_khach` của mọi dự án đã `them`** — chạm thì không thăng cấp.
- Ký ức mới đi qua gộp trong phạm vi đích; `nguon` = hai phần tử `{loai: "thang_cap", id_goc, du_an}` (không chép `nguon` của bản gốc) → `nguon_dai_ca` luôn `false`; "cặp đã thăng cấp" kiểm bằng `id_goc`. Ký ức đang chờ tự có hiệu lực (7 ngày, #19) chỉ được `giu_ca_hai` với ký ức đang hiệu lực (không làm `/chung` mất ký ức 7 ngày). Sự kiện `nho.thang_cap`. Hai ký ức gốc giữ nguyên.
- Ký ức thăng cấp có `hieu_luc_tu = tao_luc + 7 ngày`: **chờ 7 ngày rồi tự có hiệu lực** (#19) — trong 7 ngày không vào recall, hiện trên dashboard để Đại ca xem và xoá nếu muốn. Không có bước duyệt bắt buộc; hết 7 ngày mà chưa bị xoá thì tự vào recall. Thời gian chờ không tự phát hiện rò rỉ nghiệp vụ (xem giới hạn ở §6.3).
- Chỉ `cach-lam` được thăng cấp; **không bao giờ** thăng cấp `nghiep-vu`. Phép so khớp chéo dự án này chỉ chạy trong memory service, không lộ qua MCP hay HTTP.

## 9. Thành phần, giao diện, xác thực

```
Máy B
  tram nho chay   (tiến trình duy nhất mở kho LanceDB ~/.tram/nho/; flock ~/.tram/nho/.khoa)
    ├─ vòng nạp sự kiện mỗi 2 phút (§6), thăng cấp mỗi ngày (§8), dọn phiên bản LanceDB + sao lưu mỗi đêm (§6.4)
    ├─ HTTP nội bộ 127.0.0.1:7710: /nho-lai, /xoa (1b-1); /ghi (1b-3)  (§9.1)
    └─ MCP HTTP 127.0.0.1:7710/mcp: nho_lai(truy_van), ghi_nho(noi_dung, nhan?)  (§9.2, §9.3)
  Ollama 127.0.0.1:11434 + bge-m3
```

### 9.1 HTTP nội bộ

Yêu cầu header `Authorization: Bearer <tram-nho-token>` (Keychain dịch vụ `tram-nho-token`, tạo khi cài). Chỉ tram-api, bộ chấm 1a và lệnh `tram` của Đại ca đọc token này; **không bao giờ** đưa vào môi trường CLI của khe. Người gọi truyền vùng cấp tường minh; memory service vẫn kiểm dạng (§4).

- **Hợp đồng (1b-1, Đại ca chốt 13/10):**
  - `POST /nho-lai {truy_van: 1–4000 ký tự, vung_cap: 1–10 phần tử}` → `200 {ky_uc: [{id, noi_dung, pham_vi}]}`, luôn chia nhóm 3/1/1, không nhận tham số `nhom` qua HTTP.
  - `POST /xoa {id}` → `200 {da_xoa: bool}` (xoá mềm, sự kiện `nho.xoa`).
  - Lỗi:
    - `401 {detail}` khi thiếu hoặc sai token. Token được kiểm trước mọi kiểm thân và so hằng thời gian.
    - `503 {loi: "embedder: …"}` khi embedder chưa sẵn sàng.
    - `404 {loi}` khi không có `id`.
    - `422` có hai dạng thân: `{loi}` khi vùng cấp sai dạng (service tự kiểm), `{detail}` khi thân sai kiểu hoặc độ dài. Người gọi coi cả hai là "từ chối", không dựa vào tên trường.
  - Không có trang tài liệu API.
  - `/ghi` (Đại ca ghi tay) để **1b-3**, cùng màn dashboard.
- **Token** `tram-nho-token`:
  - Tạo bằng `secrets.token_hex(32)` khi cài, đưa vào Keychain qua **stdin** của `security -i`.
  - Không bao giờ nằm trong đối số dòng lệnh hay biến môi trường (`ps`, `ps eww` thấy được); không in ra, không ghi file.
  - Mã chạy thật chỉ đọc token từ Keychain. Lệnh kiểm M1/M2 dùng `tram nho tim --vung-cap` (§9.5), không dùng `curl` kèm token.
- **Vòng đời tiến trình:**
  - Bản thứ hai `tram nho chay` (M7a) in thông báo rồi thoát mã 0.
  - Không khởi động được (thiếu khoá API, kho sai số chiều…) → in lý do, thoát mã 0. launchd `KeepAlive {SuccessfulExit: false}` nhờ vậy không bật lại vô hạn.
  - Nhận SIGTERM (launchd dừng): dừng vòng nạp (chờ tối đa 10 giây, dưới hạn SIGKILL của launchd; bị cắt giữa chừng thì nhật ký làm tiếp ở lần chạy sau — §6.4), ghi nốt thống kê dùng, nhả khoá, thoát 0.

### 9.2 MCP cho CLI trên máy thợ (1b-2)

- **Công cụ MCP không nhận tham số phạm vi.** Header `X-Tram-Giao-Id` + `X-Tram-Ma-Giao` (từ biến môi trường `TRAM_GIAO_ID`, `TRAM_MA_GIAO` của phiếu — spec phần 3 §4, §7.2). Memory service hỏi tram-api `GET /api/noi-bo/phieu/{giao_id}` (Bearer **token nội bộ** `tram-noi-bo-token` — spec phần 3 §10; khác `tram-nho-token` là token để người khác gọi memory service) → nhận `{du_an, vai, ma_giao, con_hieu_luc}`, so `ma_giao` bằng phép so hằng thời gian, cache 30 giây. Sai/thiếu/hết hiệu lực → từ chối (M2).
- `ghi_nho` luôn ghi gốc `/du-an/X` của phiếu; nhánh do luật cứng quyết (§6.2 bước 2); không bao giờ `/vai`, `/chung`.
- URL MCP = biến môi trường `TRAM_NHO_URL` do thợ đặt theo máy (máy B: `http://127.0.0.1:7710/mcp`; Mac thợ từ xa: `https://<may-b>.<tailnet>.ts.net/nho/mcp`); `ma_giao` là bằng chứng ở cả hai đường. Cấu hình MCP trong `claude`/`codex` của máy thợ do `tram tho dang-ky` ghi (URL và header lấy từ biến môi trường — spike N2), có hiện diff và chờ `dong-y` (Q15).
- Cache phiếu 30 giây: CLI vừa bị thu hồi vẫn đọc/ghi được tối đa 30 giây, chỉ trong vùng dự án của chính nó — chấp nhận; M2 ghi rõ ngoại lệ này. Thu hồi **token máy** (spec phần 3 §5.1) vô hiệu mọi `ma_giao` của máy đó ngay khi cache hết hạn.
- `ma_giao` là credential: che trong log, thông báo lỗi và mọi thứ hiện trên dashboard.

### 9.3 MCP cho phiên tay của Đại ca trên máy A (1b-2)

- Đi qua `tailscale serve` (đường `/nho` → 7710). Header danh tính Tailscale **không đủ**: `tailscale serve` chuyển về `127.0.0.1`, nên tiến trình cục bộ trên máy B (agent của khe thợ — kể cả khi chạy dưới principal khác, vì TCP localhost không mang danh tính) giả được header (cùng lỗ với dashboard — spec phần 2 §12 C8). Phiên tay phải mang thêm `Authorization: Bearer <mã Đại ca>` — mã ngẫu nhiên Đại ca tạo, lưu Keychain **máy A**, đưa vào cấu hình MCP qua biến môi trường `TRAM_DAI_CA_MA` (không nằm trong repo); memory service giữ bản băm của mã: Đại ca chạy `tram chu dat-ma-dai-ca` trên máy B, nhập mã một lần, trạm lưu `sha256` vào `~/.tram/cau-hinh.yaml` — chỉ là băm nên tiến trình nào đọc được cũng vô dụng.
- Vùng cấp từ header tĩnh `X-Tram-Du-An` theo thư mục dự án trên máy A. ~~Hai cách (§13 câu 10): `.mcp.json` commit trong repo dự án (do `tram du-an them` chèn, có diff chờ `dong-y`; lộ URL tailnet của máy B trong repo), hoặc `claude mcp add --scope local` chạy trên máy A (không vào repo; Đại ca chạy một lệnh mỗi dự án).~~ **Đã chốt 16/10 (D42):** dùng `claude mcp add --scope local` chạy trên máy A, một lệnh cho mỗi dự án. **Không** ghi `.mcp.json` vào repo, nên không lộ địa chỉ tailnet của máy B trong repo, và `tram du-an them` không chèn `.mcp.json`. Sổ tay chạy thật ghi sẵn lệnh; nội dung cấu hình sinh bằng `cau_hinh_phien_tay()` trong `tram/nho/cau_hinh_mcp.py` (đã có mã, chỉ sinh, không ghi). Việc Claude Code có mở rộng `${TRAM_DAI_CA_MA}` trong `url`/`headers` hay không vẫn là spike N2 phía client, chưa chạy.
- **Ghi chú 16/10 (2e, D24):** mã điều phối của hook máy A (`tram-dieu-phoi-ma`, trạm giữ `dieu_phoi_ma_sha256`) là bí mật **khác**, memory service không nhận nó: chỉ so với `ma_dai_ca_sha256`. Phạm vi mã Đại ca không đổi. `tram chu dat-ma-dieu-phoi` từ chối mã trùng mã Đại ca; chiều ngược (`dat-ma-dai-ca` chặn trùng mã điều phối) chưa có mã.
- **Chỉ `nho_lai`** ở 1b-2. Đại ca ghi tay qua dashboard (1b-3).

### 9.4 Sự kiện, phụ thuộc, model

**Sự kiện** (bảng `su_kien` phần 0, `tac_nhan = "tram/nho"`, `du_an` = dự án của ký ức hoặc của sự kiện nguồn):

| Sự kiện | Dữ liệu | Lát |
|---|---|---|
| `nho.ghi` | `{id, pham_vi, nguon}` | 1b-1 |
| `nho.gop` | `{cu[], moi}` | 1b-1 |
| `nho.xoa` | `{id, pham_vi}` | 1b-1 |
| `nho.loi_tach` | `{su_kien_id, loi}` — hết lượt guardrail, model từ chối, sự kiện độc (§6.2) | 1b-1 |
| `nho.loi_embedder`, `nho.loi_llm` | `{su_kien_id, loi}` — một lần mỗi đợt lỗi, `du_an` + `bead_id` của sự kiện nguồn đang kẹt (§6.2) | 1b-1 |
| `nho.phuc_hoi` | `{loai: "llm" \| "embedder"}` — cùng `du_an` + `bead_id` với lỗi đã báo | 1b-1 |
| `nho.bo_bi_mat` | `{su_kien_id, loai_nguon: "ban_giao" \| "da_chot" \| "tra_ve", nhom: {<nhóm>: <số>}}` — nguồn bị bỏ vì có dấu hiệu bí mật (D23, §6.2); không đoạn khớp, không vị trí; `du_an` + `bead_id` của sự kiện nguồn. Dashboard (2f, D39) dựng câu mô tả từ mẫu cố định | 1b-4 |
| `nho.tu_choi` | `{ly_do}` | 1b-3 |
| `nho.thang_cap` | | 1b-3 |

**Phụ thuộc mới:** `lancedb` (Apache-2.0), SDK `mcp` chính thức (MIT) cho MCP HTTP; Ollama gọi bằng `urllib`. Khoá phiên bản chính xác ở plan. Phần phỏng theo crewAI (MIT) — chấm điểm, `MemorySlice` — giữ ghi chú bản quyền đầu file và trong `NOTICE` (kiến trúc §6).

**LLM cho tách/gộp/thăng cấp:** Claude qua API key của trạm chủ (Q8). Em đề xuất `claude-haiku-5-5` (rẻ); plan xác nhận id model qua skill `claude-api` và đánh giá trên bộ mẫu M4/M5.

**LanceDB** (`lancedb==0.40.0`): `table.update()` tạo phiên bản mới mỗi lần → memory service chạy `Table.optimize(cleanup_older_than=1 ngày)` mỗi đêm (vừa gộp file vừa xoá phiên bản cũ). Spike N1: `compact_files` + `cleanup_old_versions` đã deprecated và cần gói `pylance`, nên không dùng; giữ 1 ngày phiên bản vì 0 phá người đọc đang mở. Sao lưu hằng ngày: §6.4.

### 9.5 Lệnh `tram nho` (1b-1)

`chay` (tiến trình dịch vụ); `tim "<truy vấn>" (--du-an X [--vai <vai>] | --vung-cap '<JSON>')` — `--vung-cap` gửi thô để kiểm M1/M2; `xoa <id>`; `thu [--du-an] [--tu-id] [--gioi-han 20]` (tách thử, không ghi, có gọi Claude API); `dat-moc --hien-tai` (đặt `moc_nho` = sự kiện mới nhất — "chỉ nạp từ bây giờ"; mốc không lùi); `khoi-phuc <bản> [--dong-y]`; `do-tre [--so-ban 10000] [--so-lan 200]` (đo M6). Lệnh đọc/ghi ký ức đi qua service (một tiến trình ghi); `dat-moc`, `khoi-phuc` đụng thư mục kho nên chỉ chạy khi dịch vụ dừng (khoá `flock` rảnh).

## 10. Thay đổi cần ở phần khác

| Phần | Thay đổi |
|---|---|
| 1a | `bai_hoc_gan_day` → `nho_lai` có timeout + lùi (§7); bọc mục bài học trong `<du_lieu_khong_tin_cay>`; `nguon_bai_hoc` trong sự kiện. Prompt `vai/cham-cot.md`: phiên bản 2 là của plan 2a (mục "Quyết định đã chốt", spec phần 2 §12 C1); 1b-1 nâng lên phiên bản 3 |
| 2 (spec §12) | `cot.da_chot` mang `{decision_id, cau_hoi[], tra_loi[], adr?}`; `cot.dai_ca_sua` mang `vi_sao`; `cot.tra_ve` mang `gop_y`; `KhoSuKien.sau_id()`; 1b-3 thêm `/api/nho/*` (xem, xoá, ghi tay; xem/xoá ký ức thăng cấp đang chờ tự có hiệu lực — #19) |
| 3 | phiếu có `ma_giao`; tram-api có `GET /api/noi-bo/phieu/{giao_id}` trả cả khi phiếu hết hiệu lực (đều đã thêm vào spec phần 3) |
| 4 (kiểm lại) | phát `kiem.lai {giao_id, dat}` (đã có trong spec phần 4 §6.2) |
| 4 | dựng lớp 5 bằng `nho_lai` với vùng cấp của phiếu |
| `tram du-an them` | chèn `.mcp.json` có `X-Tram-Du-An` (1b-2); `tram du-an go` gỡ — ký ức của dự án giữ nguyên (xoá cần Đại ca) |

## 11. Bài học từ crewAI (đã đọc mã, kiến trúc §10) — cách 1b tránh

| Lỗi rò ở crewAI | 1b |
|---|---|
| Lọc phạm vi bằng `LIKE` tiền tố | `pham_vi IN (tập mở rộng từ vùng cấp)`, so khớp chính xác (§4) |
| Deep recall dùng phạm vi LLM gợi ý | vùng cấp chỉ do trạm cấp; LLM chỉ chọn `nghiep-vu`/`cach-lam` khi **ghi**, không bao giờ chọn gốc |
| Gộp ký ức không giới hạn gốc | gộp chỉ trong cùng `pham_vi` (§6.3) |
| Xoá theo phạm vi kèm `/` xoá lan | xoá theo `id`; xoá theo phạm vi chỉ khi khớp chính xác, cần Đại ca (1b-3) |
| Embedder lỗi lùi về vector băm (ruflo) | dừng, báo lỗi to (§6.2 bước 4) |

## 12. Chi tiết kỹ thuật đã duyệt cùng spec (13/10)

1. **Ba lát**; 1b-1 chưa cần MCP.
2. **Memory service là tiến trình riêng** (`tram nho chay`, cổng 7710), không nhét vào tram-api — tram-api khởi động lại không khoá kho, đúng "một tiến trình ghi".
3. **Nửa đời độ mới 30 ngày, tính từ `tao_luc`**; ứng viên 50; nhóm 3/1/1 không bù chéo; gộp ≥ 0,85, tối đa 3 ứng viên.
4. **Model tách/gộp `claude-haiku-5-5`**, đổi nếu bộ mẫu không đạt.
5. **Hai khoá mới trong `du-an/<ten>.yaml`**: `module` (HR Codex lấy từ `boi_canh` hiện có) và `tu_khoa_khach` (Đại ca điền nếu muốn). Phát hiện tên khách không tất định hoàn toàn — M4 đo trên bộ mẫu.
6. **Bảo vệ ký ức của Đại ca** khỏi gộp/thay bởi agent (§6.3).
7. **Xoá mềm** mặc định.
8. **1a lùi về cách cũ khi memory service tắt** (§7) — bỏ hẳn recall vector, không giả vector.
9. **Recall chỉ trả `{id, noi_dung, pham_vi}`** cho agent; `nguon` chỉ Đại ca xem.
10. **Phiên tay của Đại ca chỉ đọc** ở 1b-2.
11. **M6 nới lên 800 ms** vì gồm embed truy vấn qua Ollama; **M5 đo trên 20 truy vấn**, xét nhóm dự án.

## 13. Quyết định đã chốt 13/10 (thay mục câu hỏi)

| Câu cũ | Quyết định | Ghi ở |
|---|---|---|
| 1 | `/vai/*` chỉ nhận ký ức qua thăng cấp hoặc Đại ca ghi tay; hệ quả `/vai/cham-cot` của 1a chỉ có ký ức Đại ca ghi tay (#18) | §4, §8 |
| 2 | Thăng cấp **tự động, chờ 7 ngày** rồi tự có hiệu lực (#19) | §8 |
| 3 | Ký ức của Đại ca **không bị agent gộp/thay** (#18) | §6.3 |
| 4 | `tu_khoa_khach` **tuỳ chọn**, để trống vẫn chạy (#20) | §6.2 |
| 5 | Ngưỡng nửa đời 30 ngày, cosine 0,85, nhóm 3/1/1, M5 80% trên 20 truy vấn, M6 800 ms: **giữ làm mặc định** (#21), vẫn cần đo | §2, §7 |
| 6 | Cài Ollama + bge-m3 và dịch vụ `vn.tram.nho`: **chưa duyệt** (#5) | §15 |
| 7 | Lọc bằng `pham_vi IN (tập mở rộng)`, bỏ "mảng tổ tiên" (#18); kiến trúc §5.4 đã đổi chữ | §4 |
| 8 | Phiên Claude trên máy A **chỉ đọc** memory (#20); Đại ca ghi tay qua dashboard (1b-3) | §9.3 |
| 9 | Tạo mã Đại ca trên máy A: **chưa duyệt** (#5) | §9.3 |
| 10 | Cấu hình MCP phiên tay (`.mcp.json` trong repo hay `claude mcp add --scope local`): ~~**chưa chốt** — thuộc phần việc 1b-2 đang bị giữ bởi #5; không tự chọn thay Đại ca~~ **Đã chốt 16/10 (D42): `claude mcp add --scope local` trên máy A, không `.mcp.json` trong repo** | §9.3 |

**Việc tay của Đại ca vẫn chờ (#5):** cài Ollama + bge-m3; đăng nhập Tailscale trên máy B (điều kiện spike N2); tạo mã Đại ca trên máy A (chỉ khi làm 1b-2).

> **Ghi chú 15/10/2026** (không đổi bảng và đoạn trên): câu 6 đã được Đại ca cho phép riêng. Ollama + bge-m3 đã cài, `vn.tram.nho` đang chạy trên máy B (LaunchAgent), API key Anthropic cho memory nằm ở Keychain `tram-anthropic-api-key`. Tailscale máy B đã đăng nhập. Câu 9 (mã Đại ca trên máy A) vẫn **chưa duyệt**; câu 10 vẫn chưa chốt. Bảng đầy đủ: [quyết định 13/10, mục "Ghi chú 15/10"](../quyet-dinh/2026-10-13-tra-loi-cau-hoi-gop.md).

**Đề xuất kỹ thuật mới (từ review Codex) cần Đại ca biết khi duyệt spec:** kiểm lại nội dung cuối sau gộp và embed lại (§6.3); lấy ứng viên recall riêng từng nhóm (§7); đơn vị xử lý một sự kiện nguồn với ID thao tác bền và nhật ký thao tác (§6.4).

## 14. Spike trước khi viết plan

| # | Spike | Vì sao |
|---|---|---|
| N1 | LanceDB bản khoá ở plan: prefilter `where("pham_vi IN (...)")` + vector search, `update`/`compact_files`/`cleanup_old_versions`, độ trễ trên máy B với 10.000 bản ghi 1024 chiều — **xong 13/10** (kết quả ở plan 1b-1; dùng `optimize` thay hai hàm cũ — §9.4) | §7, M6 |
| N2 | Claude Code `.mcp.json` / `claude mcp add` hỗ trợ header lấy từ biến môi trường cho MCP HTTP; Codex tương đương; `tailscale serve` phục vụ hai đường (`/` → 7700, `/nho` → 7710) và gắn header danh tính cho MCP từ Claude desktop | §9.2, §9.3 |

## 15. Cài đặt (cần Đại ca cho phép — Q15)

`tram chu cai-dat --nho` thêm (liệt kê trước, chờ `dong-y`): cài Ollama (Homebrew), tải `bge-m3`, dịch vụ launchd `vn.tram.nho`, thư mục `~/.tram/nho/`, Keychain `tram-nho-token`; từ 1b-2, memory service đọc thêm `tram-noi-bo-token` (do `tram chu cai-dat` của phần 3 tạo; 1b-1 không cần). 1b-2 thêm lệnh `tram chu dat-ma-dai-ca`. Ollama chỉ nghe `127.0.0.1`.

Cách làm ở 1b-1 (Đại ca chốt G13 ngày 13/10):
- **Cờ riêng** `tram chu cai-dat --nho`; `tram chu cai-dat` không cờ giữ nguyên như cũ.
- **Các bước, liệt kê trước rồi chờ `dong-y`:** ghi plist `vn.tram.nho`; tạo `tram-nho-token` nếu chưa có (bước này chạy trước các lệnh); tạo `~/.tram/nho` và `~/.tram/log`; `brew install ollama` và `brew services start ollama` nếu chưa có Ollama; `ollama pull bge-m3`; `launchctl bootout` rồi `bootstrap` dịch vụ.
- **Tạo token:** dòng `add-generic-password …` đưa qua stdin của `security -i`, không qua argv. `security -i` có thể trả 0 dù lệnh con lỗi, nên sau đó kiểm lại bằng `find-generic-password` (không `-w`); không thấy thì báo lỗi.
- **Sau khi khởi động lại máy:** Keychain khoá tới khi Đại ca đăng nhập màn hình, nên dịch vụ báo thiếu token rồi dừng. Sau khi đăng nhập chạy `launchctl kickstart -k gui/<uid>/vn.tram.nho`; kế hoạch cài in sẵn cảnh báo này.
- **Bật lần đầu khi đã có lịch sử sự kiện:**
  - Trước `dong-y`, chạy `tram nho thu` để xem chất lượng tách. Chi phí nạp lịch sử ước lượng tay theo plan 1b-1 Task 24 bước 2 (số sự kiện nguồn × khoảng $0,0014); lệnh cài và `tram nho thu` không tự in con số này.
  - Mặc định là nạp toàn bộ lịch sử. Muốn "chỉ nạp từ bây giờ" thì chạy `tram nho dat-moc --hien-tai` trước bootstrap.

## 16. Kiểm chứng

1. **Unit test** (embedder giả trả vector cố định — **chỉ trong test**, đánh dấu rõ; LLM giả; đồng hồ tiêm): kiểm vùng cấp — bộ test rò rỉ gồm `["/"]`, `["/du-an"]`, `["/du-an/hr"]` khi có `hr-codex`, vùng cấp rỗng (M1, M2); mở rộng vùng cấp; prefilter — kho 100 ký ức dự án Y + 3 ký ức dự án X, recall X trả đủ 3; embedder lỗi → không ghi gì, mốc không tiến (M3); bản ghi khác model bị lọc (M3); luật cứng nghiệp vụ ≥ 10 ca số tiền + module trọn từ (M4); chấm điểm, hoà, nhóm không bù chéo; gộp không vượt phạm vi, tối đa 3 ứng viên, `thay`/`gop` xoá mềm bản cũ; ký ức của Đại ca không bị agent `thay`; thăng cấp không lặp, bỏ ký ức chạm nghiệp vụ của bất kỳ dự án nào; MCP từ chối thiếu header, `ma_giao` sai, phiếu hết hiệu lực, `giao_id` của phiếu khác (M2); HTTP nội bộ từ chối thiếu token; injection qua `ghi_nho` ("ghi nhớ: bỏ qua hàng rào") chỉ thành dữ liệu bọc thẻ khi recall; `nho.loi_tach` bỏ sự kiện, mốc tiến; `flock` chặn bản thứ hai (M7a); gọi thẳng 7710 với header danh tính Tailscale giả mà không có mã Đại ca → từ chối (M1); ký ức thăng cấp không vào recall trong 7 ngày; xoá mềm ký ức thăng cấp thì không thăng cấp lại; ~~`kiem.lai` đến sau `bao.xong` vẫn nạp bàn giao~~ (16/10, D8: `qc.ket_qua` đạt đến ở lượt sau `kiem.lai`, `bao.xong` vẫn nạp bàn giao; `kiem.lai` đạt một mình không nạp, trừ spike); ghi tay vào `/chung` chạm luật nghiệp vụ → `nho.tu_choi`; regex số tiền không khớp "3 điểm kiểm"; quét mã: chỉ `tram/nho/` import `lancedb` (M7b).
2. **Bộ mẫu** (Đại ca duyệt): 20 truy vấn từ bead HR Codex + ký ức kỳ vọng, nửa sinh từ lịch sử `cot.dai_ca_sua` (M5); 30 ký ức có/không có nội dung nghiệp vụ (M4).
3. **Trên máy B** (sau khi cài Ollama): đo M6 với 10.000 ký ức sinh giả (`tram nho do-tre`); nạp lịch sử sự kiện thật của 1a (chế độ thử, `tram nho thu`) và Đại ca đọc 20 ký ức đầu; kiểm M1/M2 bằng `tram nho tim --vung-cap` (§9.5).

## 17. Ngoài phạm vi

Memory riêng của từng CLI (`CLAUDE.md` cá nhân, memory của Claude Code) — không đồng bộ; embedding qua dịch vụ ngoài; tìm toàn văn trên mã nguồn (việc của gitnexus); chia sẻ ký ức giữa nhiều trạm chủ; embed lại khi đổi model (lệnh `tram nho embed-lai` để sau, M3 đã chặn trộn).

## 18. Đồng bộ review implementation plan 13/10/2026 — đã được Đại ca chấp nhận

Mục này ghi thay đổi kỹ thuật của review tĩnh hai plan 1b-3 và 1b-2; **không đổi #18, #19, #20, #21**, không mở #5/N2/S6 và không xác nhận test hay triển khai. Các G của đợt 1–2 đã được Đại ca chấp nhận theo `../handovers/2026-10-13-phan-hoi-review-codex-dot12.md`; không mở lại việc duyệt. Những gate cài/chạy thật riêng vẫn giữ nguyên. Thứ tự code: **3a-1 → 1b-3 → 2b → 4a-1 → 1b-2**; số test khởi điểm mỗi lát đo sau tất cả lát trước.

### 18.1 Ghi, xoá, bảo trì và replay (1b-3)

- `/ghi` nội bộ dùng Bearer `tram-nho-token`; nhận `{noi_dung, pham_vi, nhan, ma_thao_tac}`. Nội dung 1–600 ký tự, tối đa 5 nhãn 1–30 ký tự, mã 8–64 ký tự `[A-Za-z0-9-]`. Trả `{id, pham_vi, xoa, lap_lai}`. Cùng mã cùng nội dung đã chuẩn hoá/phạm vi/nhãn trả kết quả trước; cùng mã khác payload → **409**, không gọi embed/LLM và không ghi lại. HTTP `/api/nho/ghi` giữ cùng nghĩa 409. Nội dung vi phạm luật →422; dependency chưa sẵn sàng →503.
- `/danh-sach` nội bộ nhận phạm vi đủ hoặc null, `cho_hieu_luc`, `gioi_han` 1–1000; trả ký ức chưa xoá, tổng và đếm theo phạm vi, mới nhất trước, không vector. `/api/nho` giới hạn 200; đọc ký ức và nguồn cần danh tính Đại ca. **Timeline bead công khai phải che nội dung sự kiện `nho.*`; SSE chỉ phát metadata, không thêm `du_lieu` hay `nguon`.** Không thay quyền đọc bead khác.
- Thăng cấp chạy trong bảo trì đêm trước sao lưu, tối đa 10 cặp/đêm; luật cứng áp trên hai bản gốc và đầu ra cuối; sổ cặp giữ dấu từ chối/bỏ/xoá cứng. Gộp với bản đang chờ giữ thời gian chờ mới 7 ngày. Sau khi chọn cặp, giữ `khoa_gop` rồi kiểm lại bản gốc chưa xoá và cặp chưa được ghi nhận; bản stale bị bỏ, không gọi LLM.
- `/xoa`, `/ghi`, vòng nạp và từng cặp thăng cấp cùng dùng `khoa_gop`; thứ tự khoá là `khoa_gop → kho.khoa`. Recall không chờ LLM. **Dọn + sao lưu LanceDB và nhật ký giữ `khoa_gop`** để không chụp kho trước ghi nhưng nhật ký đã hoàn tất sau ghi. Sự kiện `nho.thang_cap` phát từ kế hoạch bền trong đường `ap_dung`, kể cả replay sau crash ngay sau tạo nhật ký; kiểm trùng theo khóa trong SQLite, không giới hạn ở 500 sự kiện gần nhất.
- `tram nho xoa-pham-vi` xoá mềm đúng phạm vi đủ, liệt kê/hỏi trước; `tram nho xoa-cung` chỉ chạy khi dịch vụ dừng, chỉ hàng đã xoá mềm, từ chối khi có thao tác dở. Nhật ký chỉ rút nội dung/vector/nhãn/nguồn của **bước sinh đúng ID**, giữ kết quả id/phạm vi, fingerprint yêu cầu và dấu đã xong. Kế hoạch chỉ tham chiếu ID trong danh sách `xoa` không bị xoá. Retry mã cũ không hồi sinh ký ức đã xoá cứng. Bản sao lưu cũ tồn tại tới kỳ xoay vòng; đây không phải cam kết xoá an toàn mọi dấu vết vật lý hoặc dữ liệu nguồn ban đầu.

Sự kiện bổ sung (producer `tram/nho`, consumer màn Ký ức; sự kiện nguồn MCP còn được vòng nạp đọc):

| Loại | Dữ liệu | `du_an` |
|---|---|---|
| `nho.thang_cap` | `{id, pham_vi, id_goc: [a,b], du_an: [A,B], hieu_luc_tu}` | `_tram` |
| `nho.tu_choi` | `{ly_do, nguon: "thang_cap", id_goc: [a,b]}` hoặc `{ly_do, nguon: "dai_ca_ghi", pham_vi}` | `_tram` cho `/vai/*`, `/chung`; dự án với phạm vi dự án |
| `nho.xoa_cung` | `{id, pham_vi}` | dự án của ký ức, hoặc `_tram` |
| `nho.agent_ghi` | `{noi_dung, nhan, giao_id, vai}`; `bead_id=null`, `tac_nhan="tram/nho"` | dự án của phiếu |

### 18.2 MCP, retry và giới hạn (1b-2)

- `/mcp` stateless HTTP, JSON, xác thực trước SDK. Giữ hai công cụ không có tham số phạm vi. Phiếu lấy vùng từ trạm; phiên tay mã Đại ca + dự án đã đăng ký chỉ đọc. Header Tailscale không phải bằng chứng. `ghi_nho` vẫn có thể xuất hiện trong tools/list của phiên tay nhưng thực thi phải từ chối. Cache phiếu tối đa 30 giây từ lúc bắt đầu hỏi; thiếu trường hợp đồng nội bộ →503, không cache lỗi.
- `ghi_nho` chỉ thêm sự kiện nguồn bền; vòng nạp chạy **theo nhịp danh nghĩa 2 phút**, không hứa có hiệu lực trong 2 phút khi backlog/LLM/dependency lỗi. Nhận sự kiện chưa có nghĩa đã có ký ức recall.
- Tối đa **20 bài học khác nhau/phiếu**. Đếm và thêm sự kiện nằm trong một khoá của memory service singleton (`flock` ngăn tiến trình thứ hai). Retry cùng nội dung sau che mã/cắt khoảng trắng và cùng danh sách nhãn có thứ tự trong cùng phiếu trả nhận cũ, không thêm sự kiện/quota, kể cả sau restart. Hai phiếu khác nhau độc lập. Quyền của phiếu vẫn kiểm trước retry; không thêm `request_id`/tham số phạm vi vào công cụ.
- Nguồn agent: `{loai: "agent", du_an, bead_id: null, su_kien_id, vai}`; luật cứng quyết nhánh, không LLM tách, bảo vệ ký ức Đại ca như #18. Hạn chế nhận diện tên riêng chưa nằm trong cấu hình vẫn là rủi ro M4 đã biết, không đổi quyết định `tu_khoa_khach` tuỳ chọn.
- `tram chu cai-dat --nho` tạo `tram-noi-bo-token` nếu chưa có, giữ cách stdin Keychain; mã Đại ca lưu `ma_dai_ca_sha256`, đọc mỗi lời gọi. Phương án cài cấu hình MCP phiên tay (§13 câu 10) vẫn chưa chốt. SDK dự kiến `mcp==1.30.0` chưa được review này kiểm chứng; phải kiểm bề mặt API/khoá dependency ở Task 9, N2 và cổng chạy thật vẫn đóng.

### 18.3 Mốc main eb97f87 và các consumer đợt 3 (review 14/10)

1b-1/1b-3 và 1b-2 Task 1–8 đã có mã trong snapshot. Task 9 SDK/endpoint MCP chưa có; không coi `UngDungNho` riêng lẻ là endpoint hoạt động. 3a-2/3b chỉ cấu hình MCP sau khi Task 9 đã ghép và N2 được xác minh. 4c dùng HTTP nội bộ `nho_lai_http`, không cấp `tram-nho-token` cho thợ, không đổi nhóm 3/1/1, không lùi sang recall toàn kho.

Bộ test Task 8 phải tự cấp fixture dự án và hash, không đọc cấu hình HR Codex hay mã Đại ca thật. Mẫu sửa nằm trong plan 1b-2; gói review này không sửa `tests/`.

Các thay đổi phạm vi chính xác, bảo vệ ký ức Đại ca, thăng cấp tự động sau 7 ngày, cache thu hồi tối đa 30 giây và quota 20 bài học khác nhau/phiếu từ diff lần 1 được giữ. Cache là ngoại lệ đã chốt cho memory, **không** dùng làm thời gian ân hạn cho publish/lease/PR. Claim M6/N1/test của người bàn giao chưa được review này chạy lại.

## Trạng thái triển khai (15/10/2026)

Đối chiếu với mã trên `main` (1c5f507, 1987 test pass). Embedder và LLM trong test đều là bản giả. Theo D7 và sổ tay, Ollama + bge-m3 cùng dịch vụ nhớ đã có; chưa có sự kiện nguồn để nạp. M1/M2/recall được bên bàn giao ghi nhận đã kiểm; M4/M5 làm khi có sự kiện thật. Review offline không xác minh runtime.

**Cập nhật 16/10/2026:** đối chiếu lại với `main` `f5b1fdb` (2242 test Python pass). Lát 1b-4 (Task 0–4) đã ghép; Task 5 mới làm Step 1–2 (kho sự kiện máy B trống, mốc `moc_nho` chưa có; `vn.tram.nho` đã kickstart lại không lỗi — D11). Hàng đổi có nhãn "(16/10)".

| Mục spec | Trạng thái | Nơi trong mã | Plan/Task |
|---|---|---|---|
| §4 Phạm vi, vùng cấp, lọc `pham_vi IN` | đã có mã + test | `tram/nho/pham_vi.py`, `kho.py` | 1b-1 |
| §5 Mô hình ký ức, xoá mềm | đã có mã + test | `tram/nho/mo_hinh.py`, `kho.py` | 1b-1 |
| §6.1 Nguồn từ 1a/2a (`cot.dai_ca_sua`, `cot.da_chot`, `cot.tra_ve`) | đã có mã + test; chờ cổng chạy thật (#5) | `tram/nho/nguon.py`, `vong.py` | 1b-1 |
| §6.1 Nguồn phần 3/4 (bàn giao sau QC đạt — D8, `escalation.dong`, `spec.tra_ve`) | (16/10) đã có mã + test, có quét bí mật (D23); chờ cổng chạy thật (sự kiện phần 4 thật; 1b-4 Task 5 Step 3–4). Chưa nạp bàn giao phiếu `qc`/`spec` (D43) | `tram/nho/{cac_nguon,nguon_ban_giao,nguon_giao_viec,bi_mat}.py`, `vong.py`, `loi_nap.py`, `thu.py` | 1b-4 T0–T4 |
| §6.1 Agent tự ghi qua `ghi_nho` | đã có mã + test; chờ cổng chạy thật (N2, phát phiếu thật) | `tram/nho/cong_cu.py`, `nguon.py` | 1b-2 T4, T7 |
| §6.2 Tách, luật cứng nghiệp vụ, embed, lỗi đứng, sự kiện độc | đã có mã + test; chờ cổng chạy thật (#5). (16/10) thêm: chính sách bí mật D23, trần `quan_trong` 0,6 cho chữ agent, lỗi khoá SQLite không bỏ sự kiện | `tram/nho/{tach,luat,khach,embed,llm,loi_nap,vong,bi_mat}.py` | 1b-1; 1b-4 |
| §6.3 Gộp, bảo vệ ký ức Đại ca | đã có mã + test | `tram/nho/gop.py`, `ke_hoach.py` | 1b-1 |
| §6.4 Nhật ký thao tác, đối soát, sao lưu, khôi phục | đã có mã + test | `tram/nho/{nhat_ky,ap_dung,sao_luu,bao_tri}.py`, `lenh_kho.py` | 1b-1 |
| §7 Recall 3/1/1; 1a dùng recall, lùi về sự kiện | đã có mã + test | `tram/nho/{nho_lai,cham_diem}.py`, `tram/nho/khach.py`, `tram/cham_cot/cham.py` | 1b-1 |
| §8 Thăng cấp, chờ 7 ngày | đã có mã + test; chờ cổng chạy thật (1b-1 chạy ổn ≥ 1 tuần) | `tram/nho/{thang_cap,vong_thang_cap,ke_hoach_thang_cap,soan_thang_cap,luat_chung}.py` | 1b-3 |
| §9.1 HTTP nội bộ `/nho-lai`, `/xoa`, `/ghi`, `/danh-sach` | đã có mã + test | `tram/nho/dich_vu.py`, `dich_vu_ghi.py` | 1b-1; 1b-3 |
| §9.2 MCP cho CLI trên máy thợ | đã có mã + test; chờ cổng chạy thật (N2; dịch vụ phải khởi động lại mới có `/mcp`) | `tram/nho/{may_chu_mcp,ung_dung,danh_tinh,tra_phieu}.py`, `tram/tho/mcp_tho.py` | 1b-2 T1–2, T8–9; 3b T5 |
| §9.3 MCP phiên tay: mã Đại ca, chỉ đọc | đã có mã + test; chờ cổng chạy thật (#5) | `tram/nho/{danh_tinh,ma_dai_ca}.py` | 1b-2 T2–3 |
| §9.3 Cấu hình MCP phiên tay trên máy A | (16/10) **đã chốt D42**: `claude mcp add --scope local` chạy tay trên máy A cho từng dự án, không `.mcp.json` trong repo. Mã chỉ sinh cấu hình (`cau_hinh_phien_tay()`); không có lệnh tự ghi, và không cần | `tram/nho/cau_hinh_mcp.py` | 1b-2 T6 |
| §9.4 Sự kiện `nho.*`, phụ thuộc `lancedb`, `mcp` | đã có mã + test; (16/10) thêm `nho.bo_bi_mat` | `tram/nho/{ap_dung,bi_mat,vong}.py`, `pyproject.toml` | 1b-1; 1b-2 T9; 1b-4 T0, T4 |
| §9.5 Lệnh `tram nho` | đã có mã + test | `tram/nho/{lenh,lenh_kho,lenh_xoa}.py` | 1b-1; 1b-3 |
| §10 Màn Ký ức, `/api/nho/*` | đã có mã + test | `tram/api/tuyen_nho.py`, `frontend/src/trang/KyUc.vue`, `nho.js` | 1b-3 |
| §10 `tram du-an them` chèn `.mcp.json` | (16/10) **bỏ theo D42**: không chèn `.mcp.json` vào repo, nên không làm | — | — |
| §10 Phần 4 lớp 5 dùng `nho_lai` | đã có mã, chờ cổng chạy thật; mặc định tắt (`phu_thuoc_4c.memory`) | `tram/giao_viec/lop_5.py`, `noi_4c.py` | 4c T3, T8 |
| §15 `tram chu cai-dat --nho`, `dat-ma-dai-ca`, `tram-noi-bo-token` | đã có mã + test; chờ cổng chạy thật (#5) | `tram/chu/cai_dat_nho.py`, `tram/nho/ma_dai_ca.py` | 1b-1; 1b-2 T3, T5 |

### Lệch so với spec khi code

- ~~§6.1: phần 4 (4a-1, 4b) đã phát `kiem.lai`, `escalation.dong`, `spec.tra_ve`, nhưng vòng nạp chưa đọc các sự kiện này. Bài học từ bàn giao, từ câu trả lời escalation và từ góp ý trả về spec **chưa** thành ký ức.~~ **Hết lệch từ 16/10** (1b-4): vòng nạp đọc ba nguồn qua `doc_nguon`. Vẫn lệch chữ spec gốc ở một chỗ có chủ ý: bàn giao code thường chờ `qc.ket_qua` đạt (D8), chặt hơn "`kiem.lai` đạt" của chữ gốc.
- §9.4, §18.2: SDK đã chốt là `mcp==1.30.0` (Đại ca cho tải 14/10). `uv.lock` thêm 19 gói chứ không phải 18 như G13; gói dư là `pywin32`, chỉ dành cho Windows và không cài trên macOS. Bề mặt API của SDK đã kiểm ở 1b-2 T9.
- §18.1 (1b-3 T11): nhãn là một phần của payload `/ghi`. Gửi lại cùng `ma_thao_tac` mà khác `nhan` thì trả 409.
- §9.2: dịch vụ `vn.tram.nho` đang chạy trên máy B vẫn là mã cũ, nên chưa phục vụ `/mcp` cho tới khi khởi động lại (`launchctl kickstart`). (16/10: đã kickstart sau khi ghép 1b-4 Task 4 theo D11, dịch vụ chạy lại không lỗi; việc kiểm `/mcp` vẫn thuộc N2.)

### Cổng còn treo

| Cổng | Việc | Bead |
|---|---|---|
| #5, §15 | Cài Ollama + bge-m3, bật `vn.tram.nho`, chạy thật 1b-1; đo M5, M6 | `bs-hpc.5` |
| N2, §9.2–9.3 | Kiểm `/mcp` trên máy B và máy A, `tailscale serve` đường `/nho`, mã Đại ca trên A (1b-2 T10) | `bs-8eh.1` |
| §3 hàng 1b-3 | Chạy thật thăng cấp và màn Ký ức, sau khi 1b-1 chạy ổn ≥ 1 tuần (1b-3 T14) | `bs-8eh.2` |
| ~~§13 câu 10~~ | ~~Chọn cách cấu hình MCP phiên tay~~ — **đã chốt 16/10 (D42)**: `claude mcp add --scope local`; bead `bs-urj.5` đã đóng | `bs-urj.5` |
| 1b-4 Task 5 Step 3–4 | `tram nho thu` (tốn API) và nạp thật khi đã có sự kiện phần 4 thật; đếm `nho.bo_bi_mat` theo nhóm | — |
| §16 mục 2 | Bộ mẫu M4 (30 ký ức) và M5 (20 truy vấn) do Đại ca duyệt | — |

> **Ghi chú 15/10/2026:** ở hàng "#5, §15", việc cài Ollama + bge-m3 và bật `vn.tram.nho` đã xong. Còn lại là chạy thật 1b-1 (M4, M5, M6, các bước còn lại của 1b-1 T24). Hàng §13 câu 10 nay có bead `bs-urj.5`; hàng §16 mục 2 có bead `bs-8eh.12`. Với hàng N2: 1b-2 T10 bước 1 chỉ kickstart `vn.tram.api` khi dịch vụ này đang chạy, nhưng ngày 15/10 `vn.tram.api` **chưa được cài** trên máy B (chỉ có `vn.tram.bao-tin`, `vn.tram.nho`). Đường tra phiếu bằng `tram-noi-bo-token` chỉ dùng được sau khi `tram chu cai-dat` (2a T26) cài `vn.tram.api`.

## Đồng bộ D8–D11 — thay điều kiện §6.1 và §16.1

- D8: bàn giao code thường chỉ thành nguồn sau `qc.ket_qua` đạt của lượt QC tương ứng và kiểm lại đạt; `kiem.lai` đạt một mình chưa đủ. Spike không QC giữ cửa `kiem.lai` đạt. Không nạp bàn giao tạm. Đây là thay đổi đã chốt, chặt hơn chữ §6.1 cũ.
- D9 nạp mọi escalation theo spec, không tự loại lý do máy móc; D10 không cờ nguồn; D11 restart dịch vụ ngay sau ghép Task 4 hoàn chỉnh, trước producer phần 4 chạy. D7 giữ dịch vụ hiện hữu.
- Adapter 1b-4 chưa có trong mã snapshot. Vai từ `giao.nhan` là đề xuất thay nguồn HTTP cũ (G3), không gọi mạng từ memory. G4/G9/G20 còn chờ chốt kỹ thuật; nguồn agent không tự thành nguồn Đại ca.
- §16.1 phải kiểm kiểm-lại đến sau báo-xong, QC đến sau kiểm-lại, QC trả về không nạp, hai phiếu có cùng SHA vẫn không làm mất bàn giao mới, lỗi schema không rò nội dung. R3 về bí mật trong văn bản hợp lệ còn chặn; wrapper prompt không thay kiểm bí mật.

- **Cập nhật 16/10 (D23, D42, D43):** adapter 1b-4 đã có mã (xem "Trạng thái triển khai"). R3 về bí mật đã giải bằng bộ quét D23 (§6.2); wrapper prompt vẫn không thay kiểm bí mật. D42 chốt cách cấu hình MCP phiên tay (§9.3, §13 câu 10). D43: bàn giao phiếu `qc`/`spec` để sau.
