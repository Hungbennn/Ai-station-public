# Quyết định chủ dự án ("Đại ca") chốt sáng 13/10/2026

Trả lời danh sách câu hỏi gộp ở `docs/handovers/2026-10-13-sang-sau-dem-chay.md` §4. Các quyết định này **chưa** được ghi vào spec — spec còn để dạng "câu hỏi" hoặc "đề xuất".

Câu 1–4 và 6–20: **theo đề xuất**. Câu 5: **chưa duyệt**. Câu 21: tạm giữ các con số đang ghi trong spec làm mặc định.

| # | Quyết định |
|---|---|
| 1 | Beads từ xa: làm spike trên **bản sao** HR Codex trước; chuyển DB thật sang máy B chỉ sau khi Đại ca duyệt kết luận spike. |
| 2 | Remote git: **GitHub ngay** — trạm đăng nhập `gh`, nhánh chính bật branch protection, thợ chỉ push `tram/*`; sửa Q15 của kiến trúc thêm `github.com` (git + gh) vào danh sách gọi ra ngoài. |
| 3 | Cách ly: tạo **user macOS riêng cho thợ** trước khi bật phần 3; Mac thợ từ xa là thiết bị **gắn tag** Tailscale. |
| 4 | Chạy thử 4a đầu tiên trên **repo nháp** với 3 bug nhỏ, sau đó mới tới HR Codex. |
| 5 | **Chưa duyệt**: đăng nhập Tailscale trên B, spike S1–S4 (`claude -p` thật), cài Ollama + bge-m3, mã Đại ca trên máy A. (9router đã bỏ — không dùng nữa.) |
| 6 | Một decision đã đóng **chốt mọi loại hàng rào** (giữ như mã 1a hiện tại). |
| 7 | Nút Chốt (spec 2 §12 C1): gỡ mọi nhãn cột + đưa decision đã đóng vào prompt chấm (vai `cham-cot` phiên bản 2). |
| 8 | Một bead **một nhãn `cot:*`**; khối chèn `AGENTS.md`/`CLAUDE.md` tách đoạn phiên tay / agent trạm (spec 2 §12 C5). |
| 9 | Bộ chấm 1a **bỏ qua epic**. |
| 10 | Bộ chấm 1a **bỏ qua bead đang có phiếu hiệu lực**, kèm luật chấm lại khi phiếu kết thúc (thay quyết định 12/10 "bead đang làm vẫn chấm"). |
| 11 | Nút **Trả lời escalation** có trong lát 2a. |
| 12 | **Telegram** có trong lát 2a. |
| 13 | Mỗi phiếu tối đa **3 lần chạy CLI** trong ngân sách (thay "mỗi bước một lần chạy" của bàn giao 12/10). |
| 14 | Tắt khe / estop khi đang làm: **dừng mềm**. |
| 15 | Khe đã chạy mà không đọc được hạn mức: **chạy tiếp, cảnh báo vàng**. |
| 16 | Feature cha: trạm nhắc, **Đại ca tự đóng**; ngân sách bead **bắt đầu lại** sau khi Đại ca trả lời escalation hoặc trả về. |
| 17 | QC chéo giữa hai khe cùng model Claude: **chấp nhận**, không chờ khe Codex. |
| 18 | Memory: `/vai/*` chỉ qua thăng cấp hoặc Đại ca ghi tay; ký ức Đại ca không bị agent ghi đè; lọc bằng `pham_vi IN (tập mở rộng)` thay "mảng tổ tiên". |
| 19 | Thăng cấp ký ức **tự động, chờ 7 ngày** trước khi vào recall. |
| 20 | `tu_khoa_khach` tuỳ chọn; phiên Claude trên máy A **chỉ đọc** memory. |
| 21 | Con số: giữ mặc định trong spec, chỉnh sau. |

## Ghi chú 15/10/2026 — #5 đã mở một phần

Văn bản quyết định ở trên giữ nguyên. Sau 13/10, Đại ca đã cho phép riêng một số việc thuộc #5 (Em điều phối ghi lại theo hội thoại với Đại ca, đối chiếu máy B ngày 15/10). Spec và plan nào còn ghi "#5 chưa duyệt" thì đọc theo bảng này.

| Việc | Trạng thái 15/10 | Ghi chú |
|---|---|---|
| Cài Ollama + bge-m3 trên máy B | **Đã cho phép, đã cài** | Lệnh `ollama` có trên máy B. |
| Bật dịch vụ `vn.tram.bao-tin` và `vn.tram.nho` | **Đã cho phép, đang chạy** | LaunchAgent trong `~/Library/LaunchAgents`. Chưa cài `vn.tram.api`, `vn.tram.quet`, `vn.tram.sao-luu`. Chưa có LaunchDaemon `vn.tram.*` nào. |
| Dùng API key Anthropic cho chấm cột và memory | **Đã cho phép** | Key nằm trong Keychain máy B, mục `tram-anthropic-api-key`. Bước nào plan ghi phải báo ước tính chi phí trước (vd 0+1a Task 14 Step 1) thì vẫn báo đúng bước đó. |
| Đăng nhập Tailscale trên máy B | **Đã xong** | Bead `bs-g28.9` đã đóng. Tailscale trên máy A: chưa rõ. Các bước `tailscale serve` (2a T26, 1b-2 T10) chưa làm. |
| Tải gói `mcp==1.30.0`, `@tresjs/core@5.9.1`, `three@0.186.1` | **Đã cho phép, đã tải** | — |
| Spike S1–S8 gọi CLI thật (Claude, Codex) | **Chưa duyệt** | — |
| Tạo user macOS, sudoers (S6) | **Chưa duyệt** | — |
| Repo GitHub (S7) | **Chưa duyệt** | — |
| Mã Đại ca trên máy A (1b-2 T10 bước 2) | **Chưa duyệt** | — |
| Bật giao việc (`giao_viec.bat: true`) | **Chưa duyệt** | — |
| Mọi bước tốn quota | **Chưa duyệt** | — |
| Spike beads từ xa (0+1a Task 0, #1) | Chưa có ghi nhận cho phép chạy | Cách làm đã chốt ở #1. Điều kiện Tailscale máy B đã có. Hỏi Đại ca trước khi chạy. |

Thứ tự vẫn là "code xong hết rồi mới gom chạy thật". Lịch chạy và các cổng xem [sổ tay giai đoạn chạy thật](../handovers/2026-10-15-so-tay-chay-that.md).
