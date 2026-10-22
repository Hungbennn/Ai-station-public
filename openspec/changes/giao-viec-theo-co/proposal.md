# Giao việc theo cỡ

Đã chốt 20/10/2026 · Bead: `bs-2bd.7` · bản nháp gốc: `ea8a2da`.
Chưa triển khai. [Plan TDD](../../../docs/plans/2026-10-21-giao-viec-theo-co.md)
đã được review độc lập trên HEAD `51ec56f`; xem [REVIEW-PLAN-1.md](REVIEW-PLAN-1.md).

## Why

Đại ca muốn việc nhỏ làm gọn, việc khó dùng model phù hợp và kiểm kỹ:
“đừng dùng dao mổ trâu giết gà”. Một lần chấm cỡ dùng chung cho model và quy
trình. Nguồn: yêu cầu và quyết định của Đại ca trong chat 20/10/2026.

## What Changes

- Đếm file, nhóm mã, tiêu chí; nguy hiểm luôn lớn, thiếu dữ liệu ít nhất vừa.
  Không gọi LLM để chấm.
- Nhỏ → Sonnet/code thẳng; vừa → Opus/plan ngắn; lớn → Opus/plan đầy đủ,
  review chéo tối đa 3 vòng. Giữ test, kiểm lại cách ly và QC khác khe.
- Đại ca chỉ nâng cỡ bằng nhãn Beads làm sàn; không thêm UI/mockup hay API cỡ.
- Lưu cỡ/model/quy trình theo lượt; ngưỡng trong cấu hình dự án để chỉnh sau
  khi có số liệu. Thiếu khe đúng model thì chờ.

[QUYET-DINH.md](QUYET-DINH.md): QĐ1=A, QĐ2=A, QĐ3=A, QĐ4=C, QĐ5=A.

## Capabilities

### New Capabilities

- `giao-viec-theo-co`: chấm cỡ, chọn model/quy trình, nâng bằng nhãn, lịch sử lượt.

### Modified Capabilities

Không sửa capability đã archive. Phần luật plan/QC cần đồng bộ trước khi bật
nhánh gọn được chỉ rõ trong [design.md](design.md).

## Impact

Vùng dự kiến: `tram/giao_viec/`, `tram/phieu/`, `tram/su_kien/`,
`tram/cau_hinh/`, `tram/tho/`, `tram/chay_cli/`, `vai/`.
Giữ cách ly và công tắc hiện hành; nếu triển khai cần đổi cấu trúc DB thì trình
riêng theo kill list. Không tự bật chạy thật hay nới quyền.

Nền đội ngũ thợ đã có trên HEAD dùng để review plan. Không quyết định lại
cách cài, đăng nhập, quyền Git hay số khe.
Phụ thuộc chạy thật `bs-2bd.2` không được coi đã xong chỉ vì spec đã chốt.

## Ngoài phạm vi

Giao diện, API riêng, cài thợ, đổi chấm cột,
tự merge/deploy, dự báo token, tự học ngưỡng hay xếp hạng chất lượng model.
