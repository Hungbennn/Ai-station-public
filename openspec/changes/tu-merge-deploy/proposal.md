# Proposal — Tự merge, tự deploy dự án con

Bead: `bs-2bd.3`. Trạng thái: **QĐ1–QĐ4 ĐÃ CHỐT; plan 20/10 đã viết để review, chưa code/chạy thật**.
Nguồn: mục tiêu Đại ca chốt 17/10; yêu cầu trực tiếp trong chat 20/10/2026:
trạm tự merge + tự deploy, gọn, dùng GitHub/launchd/macOS; Uq + Seatbelt đã cài chính thức, lượt thật đạt.
Yêu cầu này cho phép viết spec và plan; không cấp quyền code, bật công tắc hay chạy thật.

## Why

Việc đủ kiểm cần đi từ PR tới bản chạy thật mà không chờ Đại ca bấm merge.
Trạm vẫn phải biết đang đưa bản nào lên, khi nào cần dừng và quay lại bản nào nếu lỗi.

## What Changes

- Thay điểm dừng #2 bằng tự merge có điều kiện, riêng từng dự án, mặc định tắt.
  Giữ duyệt spec (#1), hỏi khi bí/bất đồng (#3), duyệt thao tác nguy hiểm ngoài phạm vi được cấp (#4).
- “Kiểm đạt” là kết quả của bộ quản lý kiểm Uq + Seatbelt cho đúng lượt và commit,
  cộng QC khác khe; không lấy lời agent hay một lần G4 đạt làm bằng chứng cho mọi PR.
- **[QĐ1 đã chốt A]** GitHub giữ kiểm bắt buộc và yêu cầu nhánh cập nhật; trạm không dựng lại
  bảng kết luận của mọi job CI, không có nút bỏ CI cho tự merge.
- **[QĐ2 đã chốt A]** Deploy bản merge đã xác minh và kiểm lại đạt tại chính commit đó,
  không đọc HEAD đang di động để chọn mã sẽ chạy.
- **[QĐ3 đã chốt A]** Mỗi dự án giữ ba thao tác deploy/kiểm hoạt động/rollback;
  dùng đường triển khai có sẵn, quyền riêng của dự án, không chạy mã dự án bằng tài khoản giữ bí mật trạm.
- **[QĐ4 đã chốt A]** Chỉ bật deploy khi có bản ổn định để quay lại. Lỗi đã rõ → tự rollback;
  kết quả không rõ hoặc rollback hỏng → dừng dự án, báo Đại ca.
- Dùng cửa passkey, sự kiện, nút dừng và báo tin hiện có; không thêm hệ thống duyệt hay sổ kiểm thủ công.

## Capabilities

### New Capabilities

- `tu-merge`: điều kiện, bằng chứng, GitHub, xác minh sau merge và đối soát khi mất phản hồi.
- `tu-deploy`: đích theo dự án, bản phát hành cố định, kiểm hoạt động, rollback và phục hồi sau gián đoạn.

### Modified Capabilities

Không có spec đã archive: `openspec/specs/` hiện chỉ có `.gitkeep`.
Hai capability trên dùng `ADDED Requirements` theo quy ước OpenSpec.

## Đối chiếu nguồn và phạm vi thay thế

| Nguồn đã đọc | Kết luận cho plan này |
| --- | --- |
| [Q6, §5.7 kiến trúc](../../../docs/specs/2026-10-12-tram-dieu-phoi-kien-truc.md), [spec 4 §6.7](../../../docs/specs/2026-10-13-phan-4-giao-viec.md), [ADR-0007](../../../docs/decisions/ADR-0007-tram-giu-quyen-day.md) | Định nghĩa điểm dừng #2 và bằng chứng gắn commit. Thay người thực hiện merge theo QĐ đã chốt; giữ quyền công bố của trạm và xác minh trước đóng bead. |
| [AGENT_RULES §11](../../../docs/AGENT_RULES.md), [PROJECT](../../../docs/PROJECT.md), [ARCHITECTURE](../../../docs/ARCHITECTURE.md) | Còn ghi “chưa hiệu lực/Đại ca merge”. Spec nháp không tự sửa luật chạy thật. |
| [gh.py](../../../tram/giao_viec/gh.py), [gh_tu_merge.py](../../../tram/giao_viec/gh_tu_merge.py) tại `86aaf74` | Khác mô tả “cấm merge ~dòng 21”: đã cho merge theo đúng dạng ràng buộc đầu PR; không phải bằng chứng đã được bật chạy thật. |
| [Change cũ](../tu-merge-tu-deploy/proposal.md), [D69–D151](../../../docs/quyet-dinh/2026-10-18-tu-merge-tu-deploy.md) | Đã có spec, plan và mã TM. Bản này cập nhật hành vi theo yêu cầu 20/10, không coi repo là chưa có tính năng. |
| D69, D72–D92, D95–D124, D126–D130 | Giữ mặc định tắt, QC/kiểm lại bắt buộc, spec do Đại ca duyệt, hàng rào dữ liệu, ba lệnh, ba lần hỏng, báo tin và các nút hiện có. QĐ1 chỉ thay phần CI trong D70–D71/D93; QĐ2 thu hẹp “mới nhất” trong D97. |
| D94, D125; design cũ D-6 | Đổi có đánh dấu tương ứng QĐ1, QĐ2, QĐ3; QĐ4 thêm điều kiện đường lui lần đầu. QĐ1–QĐ4 đã chốt thay đúng phần ghi rõ; các phần khác giữ nguyên. |
| [Passkey](../xac-thuc-passkey/specs/cua-ghi-passkey/spec.md) D135–D155 | Thắng mô tả `unix-socket` cũ ở phần cửa người. Dùng xác thực hiện có, không dựng thêm cửa. |
| [Bàn giao G4, cập nhật 11:53 và chiều 20/10](../../../docs/handovers/2026-10-20-g4-chay-that-dat.md) | Uq đã cài chính thức, lượt thật đạt; kiểm khởi động lại còn riêng. Các dòng cũ trong CURRENT_STATE/DEPLOY về chưa có `tram-kiem`, chưa đạt G4 đã lạc hậu. Phiên này không đo lại OS. |

**Đã hợp nhất 20/10:** change này là nguồn duy nhất cho delta `tu-merge`/`tu-deploy`.
Change cũ chỉ còn `dieu-khien-tu-dong`; hai spec 18/10 chuyển thành `lich-su-tu-merge.md` và
`lich-su-tu-deploy.md` ngoài cây `specs/`, không còn ADDED. Lý do: tránh archive trùng capability.
Plan [20/10](../../../docs/plans/2026-10-20-tu-merge-deploy.md) ghi bảng giữ/bỏ và mã TDD tiếp nối.

## Impact

- Chạm kill list §2: mục 5 merge/deploy, 7 công tắc, 8 chạy thật;
  ranh giới mục 1–3 và 6 liên quan cửa người, bí mật, Uq và dịch vụ cần được giữ.
  Không cấp cho agent quyền sửa các vùng này trong phiên spec.
- Vùng áp mã trong plan: `tram/giao_viec/`, `tram/tu_dong/`, `tram/deploy/`,
  cửa passkey, báo tin và màn Tự động hiện có. Không mặc định cần package, bảng DB hay dịch vụ mới.
- Sau duyệt và kiểm chứng, tài liệu sở hữu cần thống nhất: ADR-0007, AGENT_RULES §11, PROJECT,
  PRODUCT_ARCHITECTURE, ARCHITECTURE, FEATURE_SPEC, DEPLOY và sổ tay cổng. Không sửa chúng trong bản giao này.
- Điều kiện mở thật: thử repo nháp theo cổng được Đại ca cho phép, rồi bật từng dự án.
  G4 đạt không thay cho kiểm GitHub, deploy/rollback và passkey của dự án đích.

## Ngoài phạm vi

Phiên plan chỉ sửa tài liệu; không mã sản phẩm, cấu hình thật, commit, Beads hay push. Không tự deploy chính ben-station,
không tự cài/gỡ dịch vụ, tạo user, cấp bí mật, migrate hoặc xoá/khôi phục dữ liệu.
Không agent tự cập nhật việc, nhiều môi trường, merge queue, tự sửa xung đột, giao diện mới hay nền deploy mới.
Lệnh cụ thể của HR Codex chưa được cung cấp: dự án đó chưa đủ điều kiện bật deploy.

## Quyết định và nghiệm thu

[Bốn quyết định](QUYET-DINH.md) là nguồn duy nhất cho lựa chọn đã chốt.
[Design](design.md) chỉ ghi ranh giới và tích hợp; [tasks](tasks.md) chỉ là mốc nghiệm thu, không chép mã của plan.
