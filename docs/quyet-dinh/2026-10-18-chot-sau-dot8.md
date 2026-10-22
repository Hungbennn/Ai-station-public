# Chốt sau đợt 8 (code V2 + V3) — 18/10/2026

Đại ca trả lời "Theo đề xuất của em" cho 8 câu hỏi gộp từ plan V2b, V2c, V3 và Codex review gộp vòng 3
(`.handover/review-codex-plan/REVIEW-CODEX-dot8-vong3.md` mục 5). Mỗi quyết định dưới đây là đúng đề xuất đã trình.

| # | Câu hỏi | Đại ca chọn |
|---|---|---|
| D54 | Kiểm cách ly khe từ tài khoản trạm (`tram chu kiem-cach-ly --principal`) luôn đỏ khi trạm không được chạy thay khe không mật khẩu | **Không cấp thêm quyền cho tài khoản trạm.** Hai phép kiểm "API Duyệt giả danh" và "kết nối DB" của khe chuyển sang `tram tho kiem` dưới tài khoản quản lý thợ (bead riêng). G5 chưa đạt tới khi hai phép đó chạy được dưới đúng principal. |
| D55 | Dọn toàn UID khe ở mỗi mốc (khởi động khe, đầu phiếu, sau mỗi lần chạy) | **Đồng ý.** Luật vận hành: dừng `tram tho chay` trước khi đăng nhập tay dưới tài khoản khe hay chạy `tram tho kiem`. Không làm công tắc "khe tạm nghỉ" ở lát này. |
| D56 | Hạn gọi Anthropic | **120 giây mỗi lời gọi, SDK không tự thử lại**; lỗi để lượt quét sau (~2 phút). Trần 2 lời gọi đồng thời mỗi tiến trình. Đo lại khi chạy thật. |
| D57 | Hạn cài memory (`tram chu cai-dat --nho`) | **brew 30 phút, bật Ollama 1 phút, tải bge-m3 60 phút**; quá hạn thì dừng, không báo "Đã cài". |
| D58 | Hai route không ai gọi: `GET /api/su-kien/gan-day`, `POST /api/phieu/kiem` | **Bỏ cả hai** (V3-6, V3-7). Thay phần tương ứng của spec 2 và spec 4. |
| D59 | Endpoint thử "mạng ra ngoài máy" ở G4 | **Máy A trong Tailscale mở tạm một cổng nghe trong lúc kiểm, tắt ngay sau.** Mở endpoint và từng kịch bản vẫn xin quyền riêng lúc tới G4. Chưa có endpoint thì hàng đó ghi "chưa đo", G4 chưa đạt phần mạng ngoài. |
| D60 | Ctrl-C/SIGTERM khi lệnh nghiệm thu đang dò danh tính hoặc thu hồi | **Chạy nốt bước đó** (dò ≤ ~25 s, thu hồi ≤ ~40 s) rồi mới dừng với mã 143/130. SIGKILL không có cam kết dọn; dấu khoá cổng còn, Đại ca kiểm tay. |
| D61 | Chạy test không qua bộ chặn | **Có làm bước nhỏ** để pytest từ chối chạy khi không qua `tests/chan_host/chay.sh` (bead riêng). Tới lúc đó luật vẫn là luôn chạy qua runner. |

## Giữ nguyên, không hỏi lại

Theo Codex vòng 3: S6 tổng luôn đỏ tới biên bản G4; thư mục chứa hồ sơ Seatbelt phải do root giữ từ `/`; đổi `TRAM_HOME`
hay thư mục kiểm thì cài lại hồ sơ; chụp bảng tiến trình 0,25 s là thông số hiệu năng đo lại ở G3; `tram tho dang-ky`
chỉ kiểm phiên bản, kiểm đăng nhập ở `tram tho kiem`; migration cho kho memory chưa làm ở lát này.

## Phạm vi

Không cấp quyền chạy thật. Các cổng G3–G7 vẫn trình kịch bản cụ thể cho Đại ca duyệt từng bước.

## Chốt thêm 18/10 — plan V4 và 3C-D7 (Đại ca: "Đồng ý như đề xuất của em")

| # | Câu hỏi | Đại ca chọn |
|---|---|---|
| D62 | V4-1: thông tin để thử "giả danh Đại ca" (login Tailscale, địa chỉ máy B, DB nghiệp vụ) lấy ở đâu | **(a) Trạm đưa cho máy thợ qua route thợ có khoá máy** (`GET /api/tho/kiem-am`), lấy từ chính cấu hình trạm dùng để kiểm lệnh ghi. Không bắt Đại ca gõ tay vào `tho.yaml`. |
| D63 | V4-1: dòng `[CHUYỂN]` ở `tram chu kiem-cach-ly` cho mục khe | **Không tính là lỗi**, không vào mã thoát; chỉ nhắc kiểm bằng `tram tho kiem`. |
| D64 | V4-1: phạm vi kiểm API/DB của khe | **Lát này chỉ kiểm khe khi thợ ở máy B** (`tram_api` loopback); thợ ở máy khác báo ĐỎ "không kết luận", không tự đổi địa chỉ. |
| D65 | 3C-D7: quan sát miền `login/<session>` (là phiên GUI của người vận hành) | **Hướng A: không quan sát miền này.** Mỗi bản macOS (`ProductBuildVersion`) phải có bằng chứng G3.9 rằng tram-kiem bị cấm cài job vào phiên người vận hành; chưa có thì bộ đọc báo lỗi, cổng đóng. |
| D66 | Chạy G3.8–G3.10 | **Cho chạy**; kịch bản cụ thể vẫn trình Đại ca trước khi chạy. Ghi được vào miền của Đại ca ở G3.9 → dừng S6. |
| D67 | tram-kiem (ngoài hồ sơ) đọc được danh sách dịch vụ của phiên người vận hành | **Tạm chấp nhận**; bead riêng xét đổi cách chạy tách phiên sau S2. |
| D68 | macOS tự nạp dịch vụ `com.apple.*` vào miền `user/<uid>` của tram-kiem | **Cho đưa vào mốc, chỉ đúng các nhãn đã đo** trên máy thật cho bản macOS đó. |
