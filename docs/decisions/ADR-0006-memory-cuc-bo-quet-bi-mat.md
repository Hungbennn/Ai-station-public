# ADR-0006 — Memory cục bộ trên máy B, một nơi ghi, phạm vi do trạm cấp, quét bí mật trước khi nạp

**Trạng thái:** Chấp nhận (hồi tố) · 2026-10-17 — quyết định có từ trước, ghi lại từ code và quyết định đã chốt

**Bối cảnh**
Bài học mất giữa các phiên và giữa các CLI. Nhiều dự án dùng chung trạm, nên ký ức nghiệp vụ của dự án này không được
lọt sang dự án khác. Memory của crewAI có lỗi rò phạm vi; bàn giao của agent có thể chứa khoá hay token.

**Quyết định**
Một tiến trình ghi duy nhất `tram nho chay` (khoá file) mở LanceDB `~/.tram/nho/lancedb`; embed cục bộ bằng Ollama
bge-m3, tách/gộp bằng Claude API của trạm (Q8). Phạm vi do trạm cấp theo phiếu, LLM không chọn; lọc `pham_vi IN (tập)`,
cấm lọc tiền tố (#18); thiếu phạm vi thì từ chối. Thợ gọi MCP cổng 7710 bằng `ma_giao`; máy A chỉ đọc, bằng mã Đại ca
(#20, D42). Bàn giao có dấu hiệu bí mật (mẫu khoá/token, chuỗi entropy cao) bị bỏ cả: không gửi LLM, không lưu (D23).

**Vì sao**
Ngữ cảnh trung lập với CLI (Q4). Một nơi ghi tránh hỏng kho khi nhiều máy mở. Embed cục bộ để nội dung không ra ngoài
ngoài Claude API (Q8). Chặn hẳn thay vì che giữ INV-001; chấp nhận mất vài bàn giao do báo nhầm (D23).

**Phương án đã loại**
- Dùng nguyên memory crewAI (rò phạm vi, spec 1b §11); lọc "mảng tổ tiên" (#18); mở chung LanceDB từ nhiều máy.
- Embedder lỗi thì lùi về vector giả (bài học ruflo); che bí mật rồi vẫn lưu (D23).

**Hệ quả**
Memory phụ thuộc Ollama và Claude API trên B; lỗi thì báo to, không lùi. Cache phiếu 30 giây: CLI vừa bị thu hồi còn
dùng được tối đa 30 giây, chỉ trong dự án của nó (đã chấp nhận). Nguồn `cot.*` và agent tự ghi chưa qua bộ quét (D40,
để lát sau). Cổng 7710 chưa kiểm `Host` — Đại ca xếp vào việc vá (17/10).

**Nguồn**
[Spec kiến trúc](../specs/2026-10-12-tram-dieu-phoi-kien-truc.md) Q4, Q8, §5.4 · [spec 1b](../specs/2026-10-13-phan-1b-memory.md) §4, §6.1, §9, §11, §13 · #18–#20, D8, D23, D40, D42 ·
`tram/nho/khoa.py`, `tram/nho/bang.py`, `tram/nho/pham_vi.py`, `tram/nho/bi_mat.py`, `tram/nho/danh_tinh.py`, `tram/nho/embed.py`.
