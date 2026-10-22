# Design — Agent tự cập nhật việc trong Beads (qua trạm)

## Context

Vì sao làm: `proposal.md` — Why. Hành vi phải có: hai file trong `specs/`. Các câu hỏi mở của bản nháp đầu đã chốt ở
**D102–D111** (bảng cuối file). Ở đây chỉ nói **đề nghị đi đường nào, lưu ở
đâu, ghi lúc nào, an toàn ra sao**. Mã nguyên văn ở plan TDD trong `docs/plans/`, viết sau khi Đại ca duyệt change này.

Hiện trạng (đọc từ `main` `1d0f174`):

- **Đường báo của agent.** Agent chạy dưới principal thực thi, **không mạng, không credential**. Nó gọi `tram bao`
  (`tram/tho/bao.py`) — chỉ ghi một dòng JSON vào hàng đợi `$TRAM_HANG_DOI`. Tiến trình quản lý thợ đọc hàng đợi
  (`tram/tho/hang_doi.py`), **bỏ mọi mã agent tự ghi** (`khe_id`, `giao_id`, `luot`, `request_id`), gắn phiếu đang
  chạy, sinh `request_id` tất định theo vị trí dòng, đưa vào hộp thư bền (`tram/tho/hop_thu.py`) rồi gọi
  `POST /api/tho/bao` bằng token máy. Quyền vai `coder` cho `Bash(tram bao:*)`, cấm `Bash(bd:*)` (`vai/quyen/coder.json`).
- **Trạm nhận báo** (`tram/phieu/bao.py` `nhan_bao`): trong **một** giao dịch SQLite — `request_id` đã có → trả kết quả
  cũ hoặc 409; thẻ chắn lượt (`KhoPhieu.kiem_the_chan`) → 409 `luot-cu` + `tho.tu_choi`; ghi sự kiện `bao.<loại>`. Loại
  hiện có: `moc`, `can_hoi`, `bi`, `xong`, `het_han_muc`. Estop **không** chặn báo.
- **Bí và cần hỏi đã tạo escalation:** `bao.bi {ly_do: agent}` → escalation `agent-bi`; `bao.can_hoi` → `agent-can-hoi`
  hoặc `can-thao-tac-nguy-hiem` (`tram/giao_viec/xu_ly_viec.py`, `escalation.py`). Escalation là bead `decision` nhãn
  `tram:escalation`, chặn bead gốc, có dấu `<!-- ma_thao_tac: esc-… -->` để đối soát. Lý do của agent được chép vào mô
  tả escalation (gộp khoảng trắng, cắt 2.000 ký tự) — **chưa qua bộ quét bí mật** (xem Risks).
- **Vòng tick** (`tram/giao_viec/tick.py`): pha `vong_nhanh` (không Git, mục tiêu ≤ 3 phút, dừng khi estop) và pha
  `vong_git` (kiểm lại, QC, cột 3). Không gọi Beads/Git khi giữ khoá SQLite.
- **Ghi Beads:** chỉ trạm, qua `tram/beads/bd.py` (`--actor tram/*`), hạn 120 giây mỗi lệnh. Nội dung đi qua argv
  (`-d`, `--append-notes`).
- **Bộ chấm cột** đọc tiêu đề, mô tả, tiêu chí, design — **không đọc ghi chú** (`Bead.van_ban`). `doc_khoi_ban_giao`
  đọc khối `<!-- ban-giao -->` **cuối cùng** trong ghi chú của bead.
- **Thao tác ghi dashboard:** `yeu_cau_ghi` (`tram/api/bao_mat.py`) + `chay_thao_tac` (`tram/thao_tac/chay.py`, bảng
  `thao_tac`, mã thao tác, `expected_version`); bật/tắt khe lưu bằng sự kiện (`tram/thao_tac/khe.py`). Kênh ghi
  `header` hiện hành là **tạm**.
- **Change song song** `tu-merge-tu-deploy` (nhánh `spec/tu-merge-tu-deploy`) lưu cài đặt tự động theo dự án bằng sự
  kiện trong `su_kien` (D-4 của nó) và dùng chung trang cài đặt dự án. Change này đi cùng kiểu đó.

## Goals / Non-Goals

**Goals:**
- Dùng lại tối đa đường báo đã có (hàng đợi, hộp thư bền, token máy, thẻ chắn, `request_id`) — không mở cửa mới.
- Một bộ lọc nội dung duy nhất, chạy ở trạm (quyết định) và chạy sớm ở `tram bao` (để agent biết lỗi ngay).
- Mọi lần ghi Beads có mã bền, đối soát được sau sự cố, không ghi hai lần.
- Không đổi cấu trúc DB, không ghi file trong repo trạm.

**Non-Goals:**
- Không đổi luật escalation, chấm cột, kiểm lại, QC, công bố, ngân sách.
- Không cho agent đọc Beads ngoài gói ngữ cảnh hiện có.
- Không chống trùng theo nội dung giữa việc mới và việc đã có (chỉ chống trùng theo mã đề nghị).

## Decisions

### D-1. Đường đề nghị: mở rộng `tram bao` và `POST /api/tho/bao`, không thêm API, không thêm trường bàn giao
- **Tiến độ:** `tram bao --tien-do "<chữ>"` → dòng hàng đợi `loai: tien_do` → `bao.tien_do`.
- **Việc mới:** `tram bao --viec-moi --tieu-de … --mo-ta … --loai bug|task|chore [--tieu-chi …]` → `loai: viec_moi`
  kèm khối `viec_moi {tieu_de, mo_ta, loai_viec, tieu_chi}` → `bao.viec_moi`.
- **Bị chặn:** **dùng đúng** `tram bao --bi "<lý do>"` và `tram bao --can-hoi …` đang có (xem D-6). Không thêm lệnh.

Vì sao: hai loại mới đi chung hàng đợi và hộp thư bền nên **giữ thứ tự** (tiến độ tới trước `xong`), dùng chung xác
thực token máy, kiểm thuộc máy, thẻ chắn lượt và bảng `bao_tho` cho `request_id` — tất cả trong **một** giao dịch đã
có. Tiến trình quản lý thợ vẫn bỏ mã do agent ghi, nên agent không chỉ được tới việc khác (spec "Đề nghị đi qua trạm").
Quyền vai không đổi: `tram bao` vốn được phép.

*Phương án loại:*
- **API riêng `POST /api/tho/de-nghi`:** lặp lại xác thực, thẻ chắn, idempotency; thêm một đường gửi trong hộp thư; không
  được gì hơn.
- **Trường `viec_moi[]` trong khối bàn giao:** chỉ tới trạm lúc `xong` (D84 cần tiến độ và bị chặn ngay, nên vẫn phải có
  đường API); đổi schema `BanGiao` (`extra=forbid`, `phien_ban: 1`) mà QC, memory và ghi chú cột 3 đang đọc; khối bàn
  giao bị chép nguyên vào ghi chú bead. Đề nghị từ phiếu QC cũng khó gắn.

### D-2. Mã đề nghị và chống ghi trùng
- `request_id` tất định theo vị trí dòng hàng đợi (đã có) giữ idempotency ở cửa HTTP (bảng `bao_tho`, 409 khi cùng mã
  khác nội dung).
- **Mã đề nghị** `dn-<20 hex>` = băm của `(du_an, giao_id, request_id)`, do trạm tính — agent không chọn được.
- Mỗi lần ghi Beads mang dấu `<!-- ma_thao_tac: dn-… -->` (dòng riêng, trạm viết): cuối dòng ghi chú tiến độ/bị chặn,
  cuối mô tả việc mới. Trước khi ghi, trạm **đối soát**: đã có dấu trong ghi chú của việc (hoặc việc mang nhãn
  `tram:agent-tao` có dấu trong mô tả) → chỉ ghi sự kiện `de_nghi.da_ghi`, không ghi Beads lần hai. Cùng kiểu với
  escalation (spec 4 §18).
- `de_nghi.da_ghi` ghi đúng một lần theo khoá `ma_de_nghi` (`ghi_mot_lan`).

### D-3. Bộ lọc nội dung — một hàm thuần, ba chỗ gọi
Thứ tự kiểm, dừng ở lỗi đầu tiên, trả mã lý do:
1. cấu trúc (loại, trường bắt buộc, trường lạ) → `cau-truc`; loại việc ngoài `bug|task|chore` → `loai-viec-sai`;
2. độ dài → `qua-dai`;
3. ký tự điều khiển: mọi ký tự nhóm Cc trừ xuống dòng và tab (tiêu đề cấm cả xuống dòng), và ký tự định dạng vô hình /
   đảo chiều chữ (U+200B–U+200F, U+202A–U+202E, U+2060–U+2069, U+FEFF) → `ky-tu-dieu-khien`;
4. dấu dành riêng: `<!--`, `-->`, thẻ `du_lieu_khong_tin_cay` (không phân biệt hoa thường) → `dau-danh-rieng`. Lý do:
   trạm đọc khối `<!-- ban-giao -->` cuối cùng trong ghi chú, đối soát bằng dấu `<!-- ma_thao_tac -->`, và bọc dữ liệu
   không tin cậy bằng thẻ đó — agent không được giả chúng;
5. bộ quét bí mật `quet()` của `tram/nho/bi_mat.py` (D23) trên **mọi** trường chữ, bản gốc chưa cắt → `co-bi-mat`;
   sự kiện từ chối chỉ mang nhóm + số lượng.

Giới hạn độ dài (D106): tiến độ 1.000 ký tự; lý do bị chặn 2.000 (bằng mức cắt escalation hiện có); tiêu đề việc mới
1–200, một dòng; mô tả 1–4.000; tiêu chí ≤ 2.000.

Gọi ở: `tram bao` (agent thấy lỗi ngay, không ghi hàng đợi), hàng đợi phía thợ (agent có thể ghi thẳng file), và
`nhan_bao` của trạm — **chỉ chỗ này quyết định**. Dùng `quet()` sẵn có, không sửa luật quét; nếu phải tách nó ra module
dùng chung thì đó là chạm kill list mục 2, plan phải nêu.

Riêng **bị chặn**: báo bí/cần hỏi không thể bị từ chối (phiếu phải dừng được), nên lý do không qua bộ lọc được **thay**
bằng câu của trạm thay vì trả 422; lý do quá dài thì cắt và ghi "(đã cắt)".

### D-4. Nhận trong `nhan_bao`, ghi trong `vong_nhanh`
**Lúc nhận** (trong giao dịch sẵn có của `nhan_bao`, sau thẻ chắn): lọc (D-3) → loại phiếu (`spec` không được đề nghị
việc mới, D103) → đếm theo phiếu: việc mới ≥ 5 hoặc tiến độ ≥ 20 → `qua-gioi-han` (D83, D106) → ghi sự kiện `bao.tien_do` / `bao.viec_moi`
(đây là "đã nhận", mang `ma_de_nghi`). Nút tắt hay `bat_ghi: false` lúc nhận → vẫn ghi `bao.*` rồi ghi ngay
`de_nghi.bo {ly_do: tat|khoa-ghi}`; trả 200 `{da_nhan: true, se_ghi: false, ly_do}`. Lỗi lọc → 422 `{ly_do}` + sự kiện
`de_nghi.tu_choi` (không nội dung). 4xx là từ chối dứt khoát: hộp thư không gửi lại.

**Lúc ghi** — một bước mới trong `vong_nhanh` của vòng tick, **sau** điểm dừng estop của pha này (estop bật hoặc chạy
thử → không chạy; đề nghị nằm chờ và được ghi ở nhịp đầu tiên sau khi tắt estop — D107), mỗi dự án riêng:
1. Đọc lại nút và `bat_ghi` (`tram/cau_hinh/bat_ghi.py`) của dự án. Tắt/khoá → mọi đề nghị chờ của dự án thành
   `de_nghi.bo`.
2. **Tiến độ** chờ (có `bao.tien_do`, chưa `da_ghi`/`bo`) → `bd update <việc> --append-notes "<dòng>"`.
3. **Bị chặn**: escalation của `bao.bi {agent}` / `bao.can_hoi` đã có `escalation.tao` (luồng hiện có, cùng pha) và
   nút bị chặn bật → thêm dòng "bị chặn" vào ghi chú việc gốc, kèm mã escalation.
4. **Việc mới** chờ → theo D-7: lượt đã vào bằng chứng cột 3 → tạo việc; lượt không đạt → `de_nghi.bo`.
5. Sau mỗi lần ghi Beads thành công → `de_nghi.da_ghi {ma_de_nghi, loai, bead_id, bead_moi?}`.

Vì sao `vong_nhanh`: không cần Git, không bị kiểm lại 15 phút chặn, đã dừng khi estop — tiến độ và bị chặn tới Beads
trong một nhịp tick (mặc định 2 phút), đúng "ghi ngay" của D84. Đề nghị lưu **bằng sự kiện**: bảng `cong_viec_cho` chỉ
cho một dòng mỗi phiếu (`giao_id UNIQUE`) nên không dùng; trạng thái "chờ" tính lúc đọc từ `bao.*` chưa có
`de_nghi.da_ghi`/`de_nghi.bo` — giống cách `bao.can_hoi` chờ `escalation.tao`. Không đổi cấu trúc DB.

### D-5. Ghi vào Beads ra sao
- Actor `tram/de-nghi`.
- **Dòng ghi chú:** `[tram/de-nghi · tiến độ · <khe> · lượt <n>] <chữ đã lọc>` (bị chặn: `· bị chặn ·` và
  `(escalation <id>)`), rồi dòng dấu mã. Ghi chú không vào bộ chấm cột nên chữ agent không đổi được cột.
- **Việc mới:** `bd create "<tiêu đề>" -t <loai> -l tram:agent-tao --body-file - [--acceptance <tiêu chí>]` (mô tả do
  trạm dựng, đưa qua stdin để không nằm trong argv)
  — mô tả mở đầu bằng dòng của trạm `Do agent tạo khi làm <gốc> (khe <k>, lượt <n>)` và `viec_goc: <gốc>`, sau đó chữ
  của agent, cuối là dấu mã. **Không** `-p` (ưu tiên mặc định P2 của Beads — D104; đã đo: việc tạo không có `-p` mang `"priority": 2`), **không** `--parent`, không
  nhãn cột, không `--claim`. Sau đó `bd dep add <mới> <gốc> --type discovered-from` (việc mới "phát hiện từ" gốc; không
  phải `blocks`, nên luật cứng 1a không coi là chặn).
- **Đã thử `discovered-from` trên kho Beads tạm (D109), 18/10/2026 11:19 giờ VN**, `bd version 1.2.2 (6c124203e)`, thư
  mục mới dưới scratchpad (`git init` + `bd init --non-interactive --skip-agents --skip-hooks -p thu`, embedded Dolt),
  đã xoá sau khi đo; không đụng kho Beads nào khác. Kết quả nguyên văn:
  - `bd dep add --help`: `-t, --type string  Dependency type (blocks|tracks|related|parent-child|discovered-from|until|caused-by|validates|relates-to|supersedes) (default "blocks")`
  - `bd create "Viec goc" -t task -d "goc" --silent --actor tram/thu` → `thu-yt4`;
    `bd create "Viec moi do agent tao" -t bug -d "moi" -l tram:agent-tao --acceptance "tieu chi 1" --silent --actor tram/de-nghi` → `thu-b0g`
  - `bd dep add thu-b0g thu-yt4 --type discovered-from --actor tram/de-nghi` →
    `✓ Added dependency: thu-b0g (Viec moi do agent tao) depends on thu-yt4 (Viec goc) (discovered-from)`, mã thoát 0
  - `bd show thu-b0g --json` (mảng một phần tử): `"status": "open"`, `"priority": 2`, `"issue_type": "bug"`,
    `"labels": ["tram:agent-tao"]`, `"acceptance_criteria": "tieu chi 1"`, `"created_by": "tram/de-nghi"`,
    `"dependencies": [{"id": "thu-yt4", …, "dependency_type": "discovered-from"}]`, `"dependency_count": 1`
  - `bd list --json --all --limit 0`, việc `thu-b0g`: `"dependencies": [{"issue_id": "thu-b0g", "depends_on_id": "thu-yt4",
    "type": "discovered-from", "created_at": "2026-10-18T11:19:42Z", "created_by": "tram/de-nghi", "metadata": "{}"}]`
    (lưu ý: trong `bd list` trường `dependency_count` của `thu-b0g` là `0`, khác `bd show` là `1` — trạm chỉ đọc
    mảng `dependencies`, không dựa vào `dependency_count`)
  - `bd ready --json --limit 0` → `['thu-b0g', 'thu-yt4']`: liên kết `discovered-from` **không chặn** cả hai việc
  - chạy lại đúng lệnh `dep add` → lại báo `✓ Added dependency …`, mã thoát 0, nhưng `bd list` vẫn chỉ **1** liên kết:
    lặp không tạo trùng, nhưng trạm vẫn tự kiểm liên kết đã có (giống `blocks`, spike 13/10)
  - `bd create --help`: có `--body-file string  Read description from file (use - for stdin)`; `bd update` có
    `--body-file` cho mô tả nhưng **không** có lựa chọn file/stdin cho `--append-notes`.
  Kết luận: dùng `discovered-from`; luật cứng 1a (`LOAI_CHAN = "blocks"`) không coi nó là chặn; `Bead` (`tram/beads/mo_hinh.py`) hiện đọc
  `dependencies[].type` nên đọc được loại mới. Vẫn ghi dòng `viec_goc:` trong mô tả để Đại ca đọc bằng mắt.
- Mô tả việc mới đi qua stdin (`--body-file -`). Dòng ghi chú tiến độ/bị chặn vẫn phải qua argv (`--append-notes` không
  nhận file) như các lần ghi hiện có; đã qua bộ quét bí mật nhưng vẫn là nội dung nghiệp vụ, tối đa 2.000 ký tự.

### D-6. "Bị chặn" là báo bí/cần hỏi sẵn có; nút con chỉ quyết dòng ghi chú
Đại ca mô tả loại (3) là "báo bị chặn/cần Đại ca kèm lý do" (D81) — đúng là `tram bao --bi` và `--can-hoi` hôm nay. Tạo
loại thứ tư song song sẽ có hai khái niệm "bị chặn" (một cái dừng phiếu, một cái không). Vì vậy:
- Escalation (điểm dừng #3, spec 4 §9) **luôn** được tạo như hôm nay — nó là luật an toàn, không thuộc nút.
- Nút con "bị chặn" bật → thêm dòng "bị chặn" kèm lý do đã lọc vào **chính việc đó**; lý do cũng được lọc trước khi vào
  escalation.
- Telegram: dùng **tin escalation hiện có** (đúng một tin mỗi lần báo, spec `cong-tac-de-nghi-viec`); không thêm tin.
Đại ca chốt đúng như vậy (D102).

### D-7. Cổng cho việc mới
- **Lượt trong bằng chứng:** khi có `bead.vao_cot_3` của việc, các lượt được ghi là: lượt `code` có `giao_id_code` /
  `luot_code` trong bộ bằng chứng, và lượt `qc` có `qc.ket_qua = dat` với `commit_qc` = `commit_ban_giao`. Spike: lượt
  `code` của spike (kiểm tài liệu đạt, không QC).
- **Lượt không đạt** (bỏ ngay khi biết): phiếu kết thúc khác `xong`; `bao.xong` không hợp lệ; `kiem.lai` của đúng
  `giao_id` + lượt không đạt; QC sau lần kiểm đó `tra_ve` / `khong_cong_nhan`; với lượt QC: `qc.ket_qua` khác `dat`;
  việc gốc bị đóng khi đề nghị còn chờ.
- Đọc từ sự kiện như `buoc_ke_tiep` (spec 4 §6.6) — hàm thuần, test từng dòng.
- Việc mới ghi **sau** `bead.vao_cot_3` (không chen vào luồng cột 3 ở `vong_git`); thứ tự tạo theo thứ tự nhận.
- Đề nghị bỏ không được "cứu" lại; agent ở lượt sau đề nghị lại nếu còn đúng (D103). Phiếu `spec` không được đề nghị
  việc mới; spike được, ghi sau khi kiểm tài liệu đạt (D103).

### D-8. Lưu nút bằng sự kiện, chỉnh qua cửa ghi sẵn có
- Mỗi lần đổi ghi sự kiện `tu_cap_nhat.cai_dat` (cột `du_an` = tên dự án) mang **toàn bộ** trạng thái sau khi đổi
  `{bat, tien_do, viec_moi, bi_chan, ma_thao_tac}`; giá trị hiện hành = sự kiện mới nhất; `expected_version` = id sự
  kiện đó; chưa có sự kiện = mặc định (nút dự án tắt, ba nút con bật — D105). Lịch sử "ai đổi gì" tính lúc đọc. Cùng kiểu D-4 của change
  `tu-merge-tu-deploy`; nếu change đó đổi cách lưu khi duyệt thì change này đổi theo.
- Đường ghi: tuyến mới dưới `yeu_cau_ghi` + `chay_thao_tac` (mã thao tác, 409 khi màn hình cũ). Bật nút dự án khi
  `bat_ghi: false` → 422. Dashboard hỏi xác nhận một lần khi bật nút dự án (D108). **Cửa ghi còn `header`** → máy chủ
  từ chối mọi yêu cầu bật/chỉnh nút, dashboard khoá kèm giải thích, cho tới khi chuyển `unix-socket` (D87, D110); tắt nút
  dự án vẫn nhận (thao tác làm an toàn hơn, cùng tinh thần "chỉ cho TẠM DỪNG" của D87). Không ghi `du-an/*.yaml` (Đại ca vẫn sửa tay file đó; `bat_ghi` vẫn chỉ sửa tay).
- Gói ngữ cảnh lớp 2 (`tram/giao_viec/goi.py`, `vai/coder.md`, `vai/qc.md`) chỉ chèn hướng dẫn cho loại **đang bật lúc
  cấp phiếu**. Đây chỉ là hướng dẫn; quyết định thật là kiểm lúc nhận và lúc ghi.

### D-9. Báo tin và dashboard
- Loại tin mới `viec_moi_agent` ("việc mới do agent tạo") từ một sự kiện tổng `de_nghi.dot_ghi {bead_goc, bead_moi[]}`
  ghi sau khi tạo xong cả đợt của một lần vào cột 3 → một tin, chỉ tên dự án, số lượng, mã việc, link
  (`tram/bao_tin/tin.py` luật sẵn có). Chống ồn, gộp 5 phút, giờ yên lặng giữ nguyên.
- Dashboard đọc tiến độ từ sự kiện `de_nghi.da_ghi` loại `tien_do` (không phân tích ghi chú Beads); hiện ở việc tương
  ứng và nút trên trang cài đặt chung — theo mockup chung, chưa làm UI trước khi Đại ca duyệt.

### D-10. Sự kiện mới
| Loại | Dữ liệu | Ai ghi |
| --- | --- | --- |
| `bao.tien_do` | `{giao_id, luot, ma_de_nghi, noi_dung, request_id}` | tram-api (nhận) |
| `bao.viec_moi` | `{giao_id, luot, ma_de_nghi, viec_moi: {tieu_de, mo_ta, loai_viec, tieu_chi}, request_id}` | tram-api |
| `de_nghi.tu_choi` | `{giao_id, luot, loai, ly_do, nhom?}` — không nội dung | tram-api |
| `de_nghi.bo` | `{ma_de_nghi, loai, ly_do: tat \| khoa-ghi \| luot-khong-dat \| viec-da-dong}` | tram-api / tick |
| `de_nghi.da_ghi` | `{ma_de_nghi, loai, bead_id, bead_moi?, escalation_id?}` | tick |
| `de_nghi.dot_ghi` | `{bead_goc, bead_moi[]}` | tick |
| `de_nghi.loi_ghi` | `{ma_de_nghi, loai, ma_loi}` — không nội dung, không stderr | tick |
| `tu_cap_nhat.cai_dat` | `{bat, tien_do, viec_moi, bi_chan, ma_thao_tac}` | tram-api (dashboard) |

## Tích hợp ngoài — bốn câu của `AGENT_RULES.md` §15

| Tích hợp | Timeout, ai áp | Hỏng thì Đại ca thấy gì | Retry có an toàn | Log có lọt bí mật / nội dung bead |
| --- | --- | --- | --- | --- |
| **Beads `bd`** (`create`, `update --append-notes`, `dep add`, `list`) | 120 giây mỗi lệnh, `chay_bd` áp | Đề nghị ở trạng thái "chờ ghi" trên dashboard, kèm lần lỗi cuối (`de_nghi.loi_ghi` chỉ mã lỗi, không nội dung); một dự án lỗi không chặn dự án khác (luật tick sẵn có); nhịp sau thử lại | **Có**: mã đề nghị + dấu trong Beads, đối soát trước khi tạo/ghi (D-2); `dep add` lặp được nhưng trạm tự kiểm liên kết đã có trước | Không bí mật (đã quét trước khi lưu). `LoiBd` chỉ mang 4 tham số đầu (không có nội dung) + 500 ký tự stderr — không đưa vào Telegram. Nội dung nằm trong argv lúc chạy `bd` (như ghi chú hiện có) — xem D-5 |
| **Telegram** (loại tin mới) | như `tram/bao_tin/` hiện có | Không nhận tin; tin xếp lại vòng sau (luật chống ồn sẵn có); dashboard vẫn hiện | **Có**: khoá chống lặp 1 giờ theo `(loại, dự án, mã)` | Tin chỉ có tên dự án, số lượng, mã việc, link — không tiêu đề, mô tả hay lý do của agent |

## Vùng kill list bị chạm

| Mục `AGENT_RULES.md` §2 | Chạm thế nào |
| --- | --- |
| Cửa API thợ (token máy — mục 2 `tram/tho/token_may.py` là gốc) | Thêm hai loại vào `ThanBao` / `nhan_bao` (`tram/phieu/bao.py`), hàng đợi `tram/tho/hang_doi.py`, `tram bao`. **Không** đổi xác thực token máy |
| Mục 2 — bộ quét bí mật | Gọi `quet()` của `tram/nho/bi_mat.py` cho đề nghị; có thể phải tách ra chỗ dùng chung |
| Ghi Beads (không đảo ngược trong 1 giờ) | `tram/beads/bd.py` thêm tạo việc có liên kết `discovered-from`; ghi chú do agent đề nghị |
| Mục 7 — công tắc lớn | Công tắc mới theo dự án; mọi đường ghi mới đọc `bat_ghi` |
| Mục 1 — cửa danh tính | Tuyến ghi cài đặt mới dùng `yeu_cau_ghi`; kênh `header` còn tạm → không bật được nút (D110). Không sửa `bao_mat.py`/`kenh_ghi.py` |
| Mục 8 — chạy thật | Kịch bản trên repo nháp, một cổng mới trong sổ tay |

Không chạm: cấu trúc DB (mục 4), cách ly (mục 3), đẩy/merge/deploy (mục 5), dịch vụ launchd (mục 6).

## Risks / Trade-offs

- **[Chữ lan qua việc mới]** Agent A tạo việc mới có chỉ dẫn độc; bộ chấm xếp cột 1; agent B nhận và làm theo. →
  Việc mới chỉ ghi sau kiểm lại + QC đạt; tối đa 5/phiếu; nhãn `tram:agent-tao` để Đại ca lọc; nội dung luôn bọc dữ liệu
  không tin cậy khi vào prompt; quyền và lệnh của phiếu do mã quyết (INV-002); việc chạm hàng rào vào cột 2; nút mặc định
  tắt. Rủi ro còn lại: việc vô hại về hàng rào nhưng sai mục đích vẫn có thể được làm — Đại ca chấp nhận theo D83.
- **[Bộ quét bỏ sót]** Bí mật viết tự do có thể lọt vào Beads; `.beads/` của dự án con có thể theo git lên GitHub. →
  Quét bốn nhóm (D23), nút mặc định tắt, tiến độ ngắn. Không bảo đảm tuyệt đối (giống memory, D23).
- **[Bộ quét báo nhầm]** Đề nghị hợp lệ bị từ chối. → Agent thấy lỗi ngay ở `tram bao`; chấp nhận như D23.
- **[Lỗ có sẵn, ngoài change này]** Lý do bí/cần hỏi hôm nay vào escalation mà **không quét bí mật** — lệch INV-001.
  Change này lọc khi nút bị chặn bật; sửa riêng để luôn lọc ở bead `bs-2bd.1.27` (P1, D111).
- **[Ghi chú phình]** Agent lặp có thể ghi nhiều dòng tiến độ. → Tối đa 20 dòng mỗi phiếu, 1.000 ký tự mỗi dòng (D106).
- **[`bd` đổi bản]** `discovered-from` đã đo trên `bd 1.2.2` (D-5); bản khác có thể đổi tên loại hay dạng JSON. →
  Plan có test với JSON đã đo; giữ dòng `viec_goc:` trong mô tả làm dấu phụ.
- **[Không có giao dịch chung Beads/SQLite]** Crash giữa `bd` và sự kiện. → Đối soát bằng dấu mã (D-2); cùng giới hạn
  đã chấp nhận ở ADR-0001.
- **[Đề nghị trễ]** Tiến độ tới Beads sau tối đa một nhịp tick, có thể sau khi phiếu đã xong. → Chấp nhận; lượt đã được
  kiểm lúc nhận.
- **[Kênh ghi tạm]** Tiến trình khác trên máy B giả được header để bật nút. → Không bật được nút khi cửa ghi còn `header`
  (D87, D110).

## Migration Plan

1. Code theo plan TDD; nút mặc định tắt nên triển khai không đổi hành vi của dự án nào.
2. ~~Spike `bd dep add --type discovered-from` trên kho tạm~~ — đã làm 18/10 theo D109, kết quả ở D-5.
3. Chạy thật trên repo nháp (cổng mới trong sổ tay): bật nút dự án, lần lượt từng nút con; kiểm từng Scenario cần máy
   thật (ghi Beads thật, tin Telegram thật).
4. **Lùi:** tắt nút dự án trên dashboard — đề nghị sau đó bị bỏ, không ghi. Gỡ code: sự kiện cũ vô hại; việc do agent
   tạo vẫn là việc bình thường mang nhãn `tram:agent-tao`.
5. Khi code xong và cổng đạt: viết ADR mới (số kế tiếp lúc đó) **thay một phần ADR-0001** — "trạm vẫn là bên duy nhất
   ghi Beads; agent gửi ba loại đề nghị qua `tram bao`, trạm kiểm rồi ghi"; ADR-0001 ghi `Superseded một phần by
   ADR-XXXX`. Cập nhật `PRODUCT_ARCHITECTURE.md` (ma trận nguồn sự thật, bỏ mục tiêu chưa hiệu lực), `ARCHITECTURE.md`,
   `MODULES.md`, `FEATURE_SPEC.md`.

## Đã chốt (D102–D111)

Mười hai câu hỏi mở của bản nháp đầu, Đại ca chốt ngày 18/10/2026 — đều theo đề xuất của Em
([quyết định](../../../docs/quyet-dinh/2026-10-18-agent-tu-cap-nhat-viec.md), mục "Chốt câu hỏi mở…").

| Câu cũ | D | Chốt | Ghi ở |
| --- | --- | --- | --- |
| 1. "Bị chặn" | D102 | Dùng `tram bao --bi/--can-hoi` sẵn có; việc "Bí: …" luôn tạo; nút con chỉ quyết dòng "bị chặn" | D-6; spec "Bị chặn ghi ngay…" |
| 2, 3. Lượt không đạt; spec/spike | D103 | Lượt không đạt → bỏ; phiếu spec không đề nghị việc mới; spike được, sau kiểm tài liệu | D-7; spec "Việc mới chỉ ghi sau…" |
| 4. Agent chọn gì | D104 | Loại + tiêu chí; không chọn ưu tiên (P2) | D-5; spec "Việc mới mang dấu…" |
| 5. Nút con | D105 | Bật sẵn; nút dự án mặc định tắt | D-8; spec "Một nút theo dự án…" |
| 6, 7. Giới hạn chữ, số dòng | D106 | 1.000 / 2.000 / 200 / 4.000 / 2.000 ký tự; 20 dòng tiến độ mỗi phiếu | D-3, D-4; spec "Lọc nội dung…", "Tối đa hai mươi dòng…" |
| 8. Estop | D107 | Giữ lại, ghi sau khi tắt estop | D-4; spec "Estop dừng mọi lần ghi" |
| 9. Xác nhận | D108 | Hỏi xác nhận một lần khi bật nút dự án | D-8; spec "Bật nút dự án cần xác nhận" |
| 10. Thử `bd` | D109 | Cho thử trên kho Beads tạm — đã làm, kết quả nguyên văn ở D-5 | D-5 |
| 11. Kênh `header` | D110 | Theo D87: không bật được nút tới khi có `unix-socket` | D-8; spec "Cửa ghi còn tạm…" |
| 12. Lỗ quét lý do "bí" | D111 | Sửa riêng, bead `bs-2bd.1.27` (P1) | Risks |

Câu hỏi mở còn lại: không có.
