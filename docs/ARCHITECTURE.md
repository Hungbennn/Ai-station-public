# ARCHITECTURE — bản đồ hệ thống

Project: `ben-station`
Status: `ACTIVE`
Cập nhật: `2026-10-20`

## Mục đích và sở hữu
Sở hữu: tầng, luật module, hợp đồng chung, luồng dữ liệu, ràng buộc.
Không sở hữu: bản đồ package, tích hợp ngoài, bộ test (`MODULES.md`, Tầng 2); từ vựng và bất biến (`PRODUCT_ARCHITECTURE.md`), quyết định (`decisions/`), cài dịch vụ (`DEPLOY.md`).

> Đây là **bản đồ**, không phải mô tả từng hàm. Muốn biết code chạy thế nào: đọc code.
> Dựng từ code ngày 2026-10-17 (`main` `d2a74a9`) và spec kiến trúc đã duyệt. Chỗ chỉ suy từ code có dấu.

Một kho mã: gói Python `tram` (3.12, `uv`; FastAPI, SQLite, LanceDB, MCP) và một trang web Vue 3 (`frontend/`).
Chạy trên **máy B** (Mac mini 24/7: trạm chủ, kiêm thợ) dưới launchd; **máy A** (Mac làm việc của Đại ca)
gửi phiếu yêu cầu và xem dashboard qua Tailscale. Việc nằm ở Beads của từng dự án, trạm là bên ghi
([ADR-0001](decisions/ADR-0001-beads-nguon-viec-tram-ghi.md)).

## Tầng
| Tầng | Trách nhiệm | Thư mục |
| --- | --- | --- |
| Điểm vào | lệnh `tram …`, dịch vụ launchd | `tram/cli.py`, `tram/cli_*.py`, `tram/*/lenh*.py` |
| HTTP | tram-api: đọc cho dashboard, ghi có xác thực, API thợ, API nội bộ | `tram/api/` |
| Thao tác, suy, nghiệp vụ | xem [MODULES.md](MODULES.md) | `tram/thao_tac/`, `tram/suy/`, các package còn lại |
| Nền | đường dẫn, Keychain, kho sự kiện, cấu hình, client `bd`, LLM, chạy CLI, schema bàn giao | `tram/duong_dan.py`, `tram/keychain.py`, `tram/su_kien/`, `tram/cau_hinh/`, `tram/beads/`, `tram/llm/`, `tram/chay_cli/`, `tram/ban_giao/` |
| Giao diện | SPA hash-router; trang, thành phần, văn phòng 3D | `frontend/src/` |
| Ngoài gói | prompt và quyền theo vai; skill và hook máy A; cấu hình dự án | `vai/`, `ky-nang/`, `may-a/`, `du-an/` |

## Luật module
- Danh sách package: `ls tram/`; mỗi package sở hữu gì: [MODULES.md](MODULES.md). Không có test kiến trúc cưỡng chế ranh giới.
- Có vòng import ở cấp package, chạy được nhờ import module con và import trễ trong hàm — chi tiết và luật thêm import ở [MODULES.md](MODULES.md).
- Chỉ trạm chủ ghi kho sự kiện SQLite và LanceDB; mỗi kho một nơi mở ghi
  ([ADR-0002](decisions/ADR-0002-sqlite-nhat-ky-su-kien.md), [ADR-0006](decisions/ADR-0006-memory-cuc-bo-quet-bi-mat.md)).

## Hợp đồng chung
- **Đường dẫn:** mọi dữ liệu dưới `TRAM_HOME` (mặc định `~/.tram`); repo trạm theo `TRAM_REPO`. Nguồn: `tram/duong_dan.py`.
- **HTTP:** tram-api nghe `127.0.0.1:7700`; `tailscale serve` đưa ra tailnet. Danh sách router: `tram/api/app.py`.
  Lỗi nghiệp vụ → mã HTTP qua bảng `MA_LOI` cùng file. Mọi phản hồi có CSP chặt và kiểm `Host` (`tram/api/bao_mat.py`).
- **Đọc** dashboard không cần đăng nhập — cố ý. **Ghi** qua `yeu_cau_ghi`: kênh hợp lệ + `Tailscale-User-Login`
  thuộc `dai_ca_logins` + `X-Tram: 1` + `Origin` máy B ([ADR-0004](decisions/ADR-0004-danh-tinh-tailscale-kenh-ghi.md)).
  Kênh `header` hiện hành là **tạm**: header giả được từ localhost; chuyển `unix-socket` trước khi giao việc thật.
- **Cửa riêng:** API thợ dùng token máy (so sha256) và ghép máy bằng mã một lần
  ([ADR-0003](decisions/ADR-0003-phieu-khe-token-may.md)); API nội bộ dùng token nội bộ; hook điều phối máy A dùng mã
  riêng; memory 7710 dùng mã giao của phiếu hoặc mã Đại ca (`tram/nho/danh_tinh.py`).
- **Sự kiện:** chỉ ghi thêm; trạng thái hiển thị tính lúc đọc (`tram/suy/`). Thao tác ghi mang ID để thử lại
  không tạo trùng (`tram/thao_tac/`).
- **Lượt (fencing):** mọi báo cáo của thợ mang số lượt; lượt cũ bị từ chối (`tram/phieu/`).
- **Lược đồ DB:** bảng tạo bằng `CREATE … IF NOT EXISTS`. `su-kien.db` có số phiên bản cấu trúc
  (`PRAGMA user_version`, `tram/su_kien/phien_ban.py`): cần nâng thì giữ khoá ghi, sao lưu nếu đã có bảng rồi
  áp trong một giao dịch; kho mới hơn mã thì từ chối mở. `nhat-ky.db` của memory và LanceDB chưa có số phiên bản.
  Nguồn: `tram/su_kien/ket_noi.py`, `tram/phieu/luoc_do.py`, `tram/nho/bang.py`.
- **Nội dung bead và bàn giao là dữ liệu không tin cậy** khi đưa vào prompt.

## Luồng dữ liệu chính
1. **Chấm cột:** `vn.tram.quet` (mỗi 120 giây) → `bd` đọc bead đổi → luật cứng → Claude API → ghi nhãn cột
   (chỉ dự án `bat_ghi: true`) + sự kiện.
2. **Feature A → B:** skill trên máy A gửi phiếu → `POST /api/feature/yeu-cau` → B tạo bead feature, chống trùng
   theo mã yêu cầu → khe spec viết spec + plan → Đại ca duyệt trên dashboard → trạm tạo bead con.
3. **Giao việc:** tick → chọn khe (hạn mức, vai, người QC khác người code) → cấp phiếu (tăng lượt, giữ ngân sách)
   → thợ chạy CLI trong worktree dưới principal không bí mật → bàn giao → trạm **kiểm lại** tại SHA dưới
   `tram-kiem` trong Seatbelt ([ADR-0005](decisions/ADR-0005-kiem-lai-cach-ly.md)) → QC khác khe → công bố
   `tram/<bead>` + mở PR ([ADR-0007](decisions/ADR-0007-tram-giu-quyen-day.md)) → Đại ca merge → trạm xác minh merge, đóng bead.
4. **Memory:** CLI thợ gọi MCP 7710 → vùng do phiếu cấp, LLM không chọn → quét bí mật → embed bge-m3 (Ollama)
   → LanceDB `~/.tram/nho/lancedb`.
5. **Báo tin:** `vn.tram.bao-tin` đọc sự kiện → tin ngắn Telegram, không chứa nội dung nghiệp vụ.

Dashboard: SPA build ra `dist/`, tram-api phục vụ tĩnh cùng gốc ([ADR-0008](decisions/ADR-0008-dashboard-spa-csp.md)).

## Ràng buộc quan trọng (đổi là HIGH BLAST RADIUS)
Bất biến nghiệp vụ INV-001…INV-006 (bí mật, quyền, cổng, estop, khoá ghi, QC khác khe) thuộc `PRODUCT_ARCHITECTURE.md`. Ở đây chỉ
ghi cơ chế kỹ thuật đang giữ chúng:
- Bí mật trạm chỉ ở Keychain tài khoản trạm; khe không giữ credential trạm/GitHub/khe khác.
  Khe Claude B dùng phiên riêng trong Keychain user khe theo QĐ2-A ([ADR-0009](decisions/ADR-0009-quyen-khe-b.md)).
  B gửi bản sửa qua hàng đợi; quản lý chốt SHA sau thu hồi sạch, rồi giữ luồng kiểm lại/QC hiện có (QĐ3-A).
- Kiểm lại lỗi → cổng đóng, dấu `~/.tram/kiem-lai.dong` chặn lượt kế (`tram/giao_viec/kiem_lai.py`).
- Estop là file `~/.tram/estop` (`tram/chu/estop.py`); vòng quét, tick giao việc, cấp phiếu và thợ đều kiểm nó.
- Công tắc mặc định tắt: `giao_viec.bat`, `cong_bo.phuong_an`; dự án mới sinh ra với `bat_ghi: false`.
- Agent thợ được vào mạng — cố ý. Khe sandbox chung để mặc định cho phép (suy từ code, chưa xác nhận).
- Memory: gốc phạm vi do trạm cấp; lọc khớp chính xác, cấm lọc tiền tố.

Bản đồ package, bảng tích hợp ngoài (timeout, hỏng thì sao) và bộ test: [MODULES.md](MODULES.md) — đọc khi task chạm package hay tích hợp đó.
