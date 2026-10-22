# Proposal — Agent tự cập nhật việc trong Beads (qua trạm)

Bead: `bs-2bd.5` · Nguồn ý Đại ca: quyết định **D81–D86** (thảo luận 18/10/2026, kết thúc bằng "Đủ rồi, viết spec
đi") — [`docs/quyet-dinh/2026-10-18-agent-tu-cap-nhat-viec.md`](../../../docs/quyet-dinh/2026-10-18-agent-tu-cap-nhat-viec.md);
mục tiêu "cho agent tự cập nhật việc" Đại ca nói ngày 17/10 (ADR-0001 mục Hệ quả, `PRODUCT_ARCHITECTURE.md` mục
"Mục tiêu đã chốt, chưa hiệu lực"). Tách riêng khỏi tự merge/tự deploy theo D80. Câu hỏi mở của bản nháp đầu đã được Đại ca chốt: **D102–D111** (cùng file,
mục "Chốt câu hỏi mở…", 18/10/2026).

Trạng thái: **bản nháp chờ Đại ca duyệt**. Khi được duyệt và code xong, change này **thay một phần ADR-0001**: câu
"Agent thợ không gọi `bd`, chỉ báo qua `tram bao`" được nới thành "agent gửi **ba loại đề nghị** qua `tram bao`; trạm
kiểm rồi trạm ghi". Phần còn lại của ADR-0001 giữ nguyên: **trạm vẫn là bên DUY NHẤT ghi Beads**, agent vẫn không có
quyền `bd`, mọi lần ghi có mã thao tác bền và chỉ ghi khi `bat_ghi: true`. Tới lúc đó luật hiện hành giữ nguyên.

## Why

Hôm nay agent làm xong một việc chỉ báo được "xong", "bí" hay "cần hỏi"; mọi thứ agent nhận ra giữa chừng (đang làm tới
đâu, phát hiện thêm lỗi khác, bị kẹt vì đâu) không vào được Beads, nên Đại ca phải mở log hay hỏi lại. Đại ca muốn
agent **tự ghi lại việc của mình** — nhưng không được tự đóng việc, không sửa việc khác, và không để chữ của agent mở
thêm quyền (INV-002).

## What Changes

- **Ba loại đề nghị, không hơn** (D81, D102): (1) ghi **tiến độ** vào đúng việc của phiếu mình; (2) đề nghị **việc mới** phát
  hiện ra, liên kết với việc gốc; (3) báo **bị chặn**/cần Đại ca kèm lý do — dùng đúng `tram bao --bi`/`--can-hoi` sẵn có; việc "Bí: …"
  vẫn luôn tạo, nút con chỉ quyết có ghi thêm dòng "bị chặn" vào việc đang làm (D102). Agent **không** đóng việc, **không** sửa mô
  tả, ưu tiên, nhãn hay cột, **không** đụng việc khác.
- **Đường ghi qua trạm** (D82): agent gửi đề nghị bằng `tram bao` → tiến trình quản lý thợ gắn phiếu và gửi tới API thợ
  bằng token máy → trạm kiểm (đúng việc của phiếu, đúng số lượt, đúng loại, không bí mật, không quá dài, không ký tự
  điều khiển) → **trạm ghi**. Agent vẫn bị cấm `bd`.
- **Việc mới** (D83): nhãn "do agent tạo" + liên kết việc gốc; **không tự giao** — bộ chấm cột xếp như mọi việc (chạm
  hàng rào → cột "cần Đại ca chốt"); **tối đa 5 việc mới mỗi phiếu**. Agent chọn loại (bug/task/chore) và tiêu chí
  nghiệm thu, **không** chọn ưu tiên — mặc định P2 (D104).
- **Khi nào ghi** (D84): tiến độ và "bị chặn" ghi **ngay** trong lúc agent làm; việc mới ghi **cuối lượt, sau khi kiểm
  lại và QC đạt**; lượt không đạt → bỏ đề nghị việc mới; phiếu viết spec không được đề nghị việc mới, phiếu spike
  được, ghi sau khi kiểm tài liệu đạt (D103).
- **Giới hạn chữ** (D106): tiến độ 1.000 ký tự, lý do bị chặn 2.000, tiêu đề 200, mô tả 4.000, tiêu chí 2.000; **tối
  đa 20 dòng tiến độ mỗi phiếu**.
- **Bật/tắt** (D85): mỗi dự án **một nút, mặc định TẮT**, kèm **3 nút con** (tiến độ / việc mới / bị chặn); chỉnh trên
  dashboard (bật nút dự án hỏi xác nhận một lần — D108; ba nút con bật sẵn — D105), chung màn cài đặt với tự merge/tự deploy (mockup do agent khác gộp vào
  [`docs/mockup/2026-10-18-tu-merge-tu-deploy/`](../../../docs/mockup/2026-10-18-tu-merge-tu-deploy/)).
- **Báo Đại ca** (D86): Telegram khi "bị chặn" và khi có việc mới (**gộp một tin mỗi lượt**); tiến độ chỉ hiện trên
  dashboard.
- Luôn giữ: dự án `bat_ghi: false` thì **không ghi gì** (INV-005); estop bật thì **không ghi**, đề nghị được giữ lại và ghi sau khi tắt estop
  (INV-004, D107); nội dung đề
  nghị là **dữ liệu không tin cậy**, không bí mật nào được ghi (INV-001, INV-002).
- **BREAKING (luật):** ADR-0001 bị thay một phần như trên; vai `coder`/`qc` có thêm hướng dẫn gửi đề nghị (quyền vai
  không đổi — `tram bao` vốn được phép, `bd` vẫn cấm).

## Capabilities

### New Capabilities
- `de-nghi-viec-cua-agent`: agent đề nghị gì được, trạm nhận, kiểm (phạm vi phiếu, số lượt, bộ lọc nội dung), ghi vào
  Beads khi nào và thế nào; việc mới do agent tạo; khoá ghi, estop, chống ghi trùng.
- `cong-tac-de-nghi-viec`: nút theo dự án và ba nút con, chỉnh trên dashboard qua cửa ghi, lưu bền; báo Telegram và
  hiện tiến độ trên dashboard.

### Modified Capabilities
- (không có — `openspec/specs/` còn rỗng. Luật "trạm là bên duy nhất ghi Beads, agent chỉ báo" nằm ở ADR-0001, spec 4
  §5.4, §9, §11 — Tầng 3. Khi archive, hai capability trên thắng các chỗ đó ở vùng chúng phủ.)

## Impact

- **Kill list (`AGENT_RULES.md` §2) bị chạm:**
  - mục 2 *bộ quét bí mật* — dùng lại `tram/nho/bi_mat.py` để lọc đề nghị (có thể phải tách hàm dùng chung);
  - mục 7 *công tắc lớn* — công tắc mới theo dự án, cạnh `bat_ghi`; đọc `bat_ghi` (`tram/cau_hinh/bat_ghi.py`) ở mọi
    đường ghi mới;
  - mục 1 *cửa danh tính* — đường ghi cài đặt từ dashboard đi qua `yeu_cau_ghi` (`tram/api/bao_mat.py`), kênh `header`
    còn tạm — theo D87/D110 nút không bật được cho tới khi cửa ghi chuyển `unix-socket`;
  - **cửa API thợ** (`tram/api/tho.py`, `tram/phieu/bao.py`, xác thực token máy) — thêm hai loại báo;
  - **ghi Beads** (`tram/beads/bd.py`) — thêm tạo việc có liên kết, ghi chú do agent đề nghị; ghi Beads thật không đảo
    ngược trong 1 giờ;
  - mục 8 *chạy thật* — kịch bản trên repo nháp cần một cổng trong sổ tay.
  **Không** đổi cấu trúc DB (mục 4): đề nghị và cài đặt lưu bằng sự kiện trong bảng `su_kien` và bảng `thao_tac`,
  `bao_tho` đã có.
- Code: `tram/tho/` (`tram bao`, hàng đợi), `tram/phieu/bao.py`, `tram/api/` (tuyến đọc/ghi cài đặt), `tram/giao_viec/`
  (bước ghi đề nghị trong vòng tick, gói ngữ cảnh lớp 2), `tram/beads/bd.py`, `tram/thao_tac/`, `tram/bao_tin/` (loại tin
  mới), `vai/coder.md`, `vai/qc.md`, `frontend/` (theo mockup chung).
- Tài liệu cập nhật khi xong: ADR mới thay một phần ADR-0001; `PRODUCT_ARCHITECTURE.md` (ma trận ai ghi Beads, bỏ dòng
  "mục tiêu chưa hiệu lực"); `ARCHITECTURE.md` (luồng dữ liệu "agent làm"); `MODULES.md`; `FEATURE_SPEC.md`.
- Hệ ngoài: Beads (`bd create`, `bd update --append-notes`, `bd dep add --type discovered-from` — đã thử trên kho tạm theo D109, chạy được với `bd 1.2.2`, xem `design.md` D-5),
  Telegram (loại tin mới, không nội dung nghiệp vụ).

## Ngoài phạm vi

- Agent **đóng việc**: vẫn chỉ trạm đóng sau khi xác minh code đã gộp (D81, spec 4 §6.5).
- Agent **sửa mô tả, ưu tiên, nhãn, cột** của bất kỳ việc nào, hay **ghi vào việc khác** việc của phiếu mình (D81).
- Agent có quyền `bd` trực tiếp (D82, INV-002).
- **Tự giao ngay** việc do agent tạo, hay luật cột riêng cho chúng — bộ chấm cột xếp như mọi việc (D83).
- Đổi cách chấm cột, kiểm lại, QC, escalation: change này chỉ **đọc** kết quả của chúng.
- Đọc Beads của dự án khác, đề nghị cho repo trạm (`bs-…`).
- Lỗ có sẵn "lý do bí chưa quét bí mật" (INV-001): sửa riêng ở bead `bs-2bd.1.27` (D111), không thuộc change này.
- Giao diện: không làm mockup ở đây; mockup chung do agent khác gộp, Đại ca duyệt trước khi plan/code UI.

## Câu hỏi mở

Không còn. Mười hai câu của bản nháp đầu đã chốt ở D102–D111; bảng đối chiếu ở cuối [`design.md`](design.md#đã-chốt-d102d111).
