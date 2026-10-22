# Proposal — Điều khiển tự động (phần giữ lại sau hợp nhất 20/10)

Bead: `bs-2bd.3`. Nguồn: D69–D151 ngày 18/10 và QĐ1–QĐ4 đã chốt ngày 20/10.
Trạng thái: **HỢP NHẤT**; giữ capability điều khiển. Chưa archive, chưa cấp quyền chạy thật.

## Why

Giữ các nút, lịch sử, passkey, tạm dừng và báo tin đã có; tránh hai bộ ADDED cho cùng hành vi merge/deploy.

## What Changes

- Giữ `dieu-khien-tu-dong`; hai nút điều kiện cột/hàng rào, CI trở thành khoá cứng theo QĐ1.
- Cửa người theo change `xac-thuc-passkey`, thay mô tả unix-socket cũ.
- Chuyển toàn bộ quyền sở hữu `tu-merge` và `tu-deploy` sang
  [change kế tiếp](../tu-merge-deploy/proposal.md).
- Giữ bản 18/10 để đối chiếu ở [merge lịch sử](lich-su-tu-merge.md) và
  [deploy lịch sử](lich-su-tu-deploy.md), ngoài cây `specs/`, không còn ADDED.
  Không xoá mã TM-1…TM-4 và không áp lại các plan đã triển khai.

## Capabilities

### New Capabilities
- `dieu-khien-tu-dong`: cài đặt bằng sự kiện, lịch sử, tạm dừng, các nút dashboard.

### Modified Capabilities
Không có spec đã archive.

## Impact

Plan tiếp nối: [2026-10-20-tu-merge-deploy](../../../docs/plans/2026-10-20-tu-merge-deploy.md).
Archive change này chỉ nhập `dieu-khien-tu-dong`; change mới nhập `tu-merge` và `tu-deploy`.
QĐ1 thay nút bỏ CI/D94; QĐ2 thay chọn HEAD theo D125; QĐ3 thay design D-6 chạy bằng tài khoản trạm;
QĐ4 bổ sung bản nền và thử đường lui. Các chốt 18/10 khác vẫn giữ như bảng hợp nhất trong plan.
