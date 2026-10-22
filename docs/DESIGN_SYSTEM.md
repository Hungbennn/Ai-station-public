# DESIGN_SYSTEM — luật giao diện của Ben Station (Trạm điều phối)
<!-- Đọc TRƯỚC khi chạm bất kỳ màn hình nào. -->

Project: `ben-station`
Status: `ACTIVE`
Cập nhật: `2026-10-17`

## Mục đích và sở hữu
Sở hữu: luật giao diện dùng chung của dashboard (`frontend/`) — token, component dùng chung, luật CSP cho mã
giao diện, quy trình thêm giao diện mới, ghi chú Văn phòng 3D.
Không sở hữu: hành vi từng màn và API (spec 2 trong `docs/specs/`, xem [FEATURE_SPEC.md](FEATURE_SPEC.md)),
CSP phía máy chủ (cơ chế ở [ARCHITECTURE.md](ARCHITECTURE.md), ADR-0008), bố cục chi tiết từng trang (mockup).

> Dựng từ code `frontend/` ngày 2026-10-17. **Mockup đã duyệt thắng code**: code lệch mockup thì báo Đại ca,
> không tự chọn bên. Docs này không chép code và không chép cả file CSS — chỉ tên token, vai trò, luật.

## Luật số một: giao diện mới phải có mockup Đại ca duyệt trước
- Màn mới, khối mới, hay đổi bố cục lớn: **dựng mockup trước, Đại ca duyệt, rồi mới viết plan và code**
  (`AGENT_RULES.md` mục "Phải hỏi trước"; lối đọc "Giao diện" ở `docs/AGENTS.md`).
- Mockup đã duyệt nằm ở `docs/mockup/2026-10-15-giao-dien/` (mở: `index.html`; ảnh chụp `anh-*.png`):
  - **D20** (15/10): khung sidebar, Văn phòng, Công việc, Đội ngũ AI, Phê duyệt.
  - **D33** (15/10): Tổng quan, Cài đặt.
  - **D39** (16/10): Ký ức, Usage & chi phí.
  - Nguồn quyết định: `docs/quyet-dinh/2026-10-15-chot-dot-4.md`. Mọi trang trong thư mục này đã duyệt.
- Phần bản thật có mà mockup không vẽ (D36): giữ bố cục cũ, **chỉ áp token và lớp CSS của mockup**. Không tự tạo kiểu mới.
- Cố ý không làm: chế độ tối (D38), trang Phân luồng (D18). Giao diện chỉ có nền sáng (`color-scheme: light`).

## Nguồn màu duy nhất
- Token khai **một chỗ**: khối `:root` trong `frontend/src/kieu/nen.css`, khớp `:root` của `style.css` trong mockup.
  Thêm hay đổi màu = đổi ở đó (và ở mockup), không rải ở file khác.
- Nhóm token (xem tên cụ thể trong file):
  - Nền: `--nen`, `--nen-2`, `--nen-3`, `--the` (thẻ), `--nen-hover`, `--nen-may`, `--nen-huy-hieu`.
  - Viền: `--vien`, `--vien-dam`.
  - Chữ: `--chu`, `--chu-2`, `--chu-phu`.
  - Màu nhấn thương hiệu (nâu đất): `--nhan`, `--nhan-dam`, `--nhan-nhat`.
  - Màu trạng thái: `--xanh` (ổn), `--vang` (chú ý), `--do` (lỗi, nguy hiểm), `--tim` (mất kết nối), `--xam` (tắt).
  - Cảnh báo: `--nen-canh-bao`, `--vien-canh-bao`, `--chu-canh-bao`. Estop: `--nen-estop`, `--vien-estop`,
    `--nen-bang-estop`, `--chu-bang-estop`. Khối lệnh CLI nền tối: `--nen-lenh`, `--chu-lenh`.
  - Bo góc `--r`. Phông: `--sans`, `--mono`.
- **Khoảng cách và cỡ chữ không có token**: viết px thẳng theo mockup, chỉ `--r` là token (suy từ code, chưa xác nhận
  đó là ý đồ).
- Thực tế code chưa sạch: các file trong `frontend/src/kieu/` còn nhiều mã hex viết thẳng (chip trạng thái trong
  `chung.css`, bóng đổ, màn Văn phòng). Không có test cưỡng chế "cấm hardcode màu" (suy từ code, chưa xác nhận).
  Luật cho code mới: màu dùng token; màu chưa có token thì thêm token ở `nen.css`, không viết hex mới.
- Màu trong cảnh 3D phải là hex trong JS (three không đọc biến CSS): bảng đồ vật ở `frontend/src/van_phong/hien_thi.js`,
  màu nhân vật theo khe ở `frontend/src/mau_khe.js` (băm tên khe nên thêm khe mới không đổi màu khe cũ).

## Nút
Lớp ở `frontend/src/kieu/chung.css`:
- `.nut` — nút thường (viền). `.nut.chinh` — nút chính (nền màu nhấn). `.nut.nguy` — việc nguy hiểm (chữ đỏ).
  `.nut:disabled` — mờ, không bấm được.
- `.nhom-nut` — nhóm nút chọn một (bộ lọc, khoảng thời gian), mục đang chọn là `.chon`.
- `.hang-nut` — hàng nút tự xuống dòng.
- Việc **dừng khẩn cấp (estop)**: nút trên thanh trên; bật có hộp xác nhận của trình duyệt, khi bật có `BangEstop`
  đỏ dưới thanh trên; chỉ Đại ca bấm được.
- Thao tác khó đảo ngược hiện đang dùng hộp xác nhận (`HopKhe` bật/tắt khe, `HopViSao` lý do kéo thẻ); giữ cách đó cho thao tác tương tự.
- **TẠM DỪNG tự merge / tự deploy** (mockup `docs/mockup/2026-10-18-tu-merge-tu-deploy/`, D101): `.nut-estop.vang` — cùng hình
  nút Estop, màu vàng; toàn trạm ở thanh trên cạnh Estop, khi bật có `BangTamDung` vàng; của dự án ở đầu trang Tự động.
  Công tắc bật/tắt: `CongTac` (`role="switch"`, lớp `.cong-tac`); bật và tắt đều hỏi lại bằng hộp xác nhận như estop.

## Phản hồi sau khi ghi
- Mọi thao tác ghi đi qua `frontend/src/api.js`: `ghi()` gắn `X-Tram: 1`; `thanGhi()` gắn `ma_thao_tac` (để thử lại không
  tạo trùng) và `expected_version`. Hiện chỉ `api.js` gọi `fetch`; đừng gọi ở chỗ khác.
- Thành công: tải lại dữ liệu hoặc để luồng SSE (`/api/luong`) cập nhật trang; không tự sửa tay trạng thái hiển thị.
- Lỗi: hiện **ngay tại chỗ thao tác** bằng chữ có `role="alert"` (lớp `.loi`, `.canh-bao`); lỗi chung của khung hiện ở
  `.loi-chung` trong `KhungChinh.vue`. Giữ ô nhập để Đại ca sửa và gửi lại.
- Khoá nút ghi khi: đang gửi; chưa xác minh được danh tính (`trangThai.la_dai_ca`); dự án chỉ quét thử (`bat_ghi: false`,
  hiện chip "chỉ quét thử", D37). Khoá ở giao diện chỉ là tiện, **quyền thật do máy chủ giữ** (ADR-0004): máy chủ
  vẫn từ chối (403/422) dù nút bị mở.

## Nhãn trạng thái
- Chip = lớp `.chip` + lớp màu. **Trạng thái do máy chủ suy; giao diện chỉ đổi sang chữ và màu**, không tự suy ra nghiệp vụ.
- Khe/nhân vật: `.tt-lam`, `.tt-ranh`, `.tt-can_nguoi`, `.tt-loi`, `.tt-tat`, `.tt-cau_dao`, `.tt-mat_ket_noi`.
  PR trạm: `.pr-mo`, `.pr-da_merge`, `.pr-khong_xac_minh`. Chấm trạng thái nhỏ: `.cham` + `xanh`/`do`/`xam`.
- Chưa biết thì ghi thật: `null` → "chưa chốt", không kiểm được → "không rõ". **Không đoán**, không hiện số giả.
- Hạn mức hiện bằng `ThanhHanMuc` (xanh còn nhiều, vàng thấp, đỏ hết).
- Bí mật không bao giờ hiện giá trị: Keychain chỉ "có / chưa có / không kiểm được"; Telegram `chat_id` chỉ "có / chưa có".

## Bố cục trang
- Khung: sidebar 272 px (`ThanhBen`) + cột chính gồm `ThanhTren` (ô tìm ⌘K, viên đồng bộ, estop), băng estop, rồi `.trang`.
  Dưới 900 px còn một cột.
- Mỗi trang mở bằng `DauTrang` (tiêu đề, một câu mô tả, công cụ ở slot bên phải), rồi các khối `.the` (thẻ),
  tiêu đề nhóm `h2.muc` kèm số đếm.
- Chi tiết một bead mở ở **ngăn bên** (`NganBen`), không sang trang mới.
- Trạng thái rỗng: `.cot-rong`. Chỗ chờ chốt thiết kế: `.cho-chot`. Bị chặn quyền (vd Cài đặt khi không phải Đại ca): `.the-chan`.
- Tôn trọng `prefers-reduced-motion` (đã tắt chuyển động trong `nen.css`).

## Bảng
- `.bang` trong `.bang-cuon` (cuộn ngang khi hẹp). Số căn đều (`tabular-nums`).
- Số lớn viết gọn ("4,20 tr"), rê chuột hiện số đầy đủ (D39) — `BangUsage`. Bảng dài cuộn dọc, đầu bảng dính.
- Giờ luôn theo múi giờ Việt Nam: dùng `gioVN` (`src/luat.js`) và `src/dinh_dang.js`, không tự định dạng giờ.

## Form
- Ô nhập bọc `.truong` (nhãn trên, ô dưới); ô chọn/ô chữ dùng kiểu mặc định trong `chung.css` (`.o`, `select`, `textarea`).
- Hộp nhập/xác nhận dùng `.nen-mo` + `.hop`. Có vòng focus nhìn thấy (`:focus-visible`).
- Ô ghi chú, trả lời, chốt đã có sẵn: `OChot`, `OTraLoi`, `OGhiNho`, `OGiaoViec`. Trình duyệt **không** kiểm quyền thay máy chủ.
- Nội dung bead, ký ức, bàn giao là **dữ liệu không tin cậy**: chỉ hiện bằng chữ (`{{ }}`), xem luật CSP bên dưới.

## Điều hướng
- Hash router (`#/…`) trong `frontend/src/tuyen.js`; menu sidebar **9 mục** ở `frontend/src/menu.js`: Tổng quan (trang mở
  đầu, D17), Dự án, Văn phòng, Công việc, Đội ngũ AI, Ký ức, Usage & chi phí, Phê duyệt (có badge đếm), Cài đặt.
- **Đường dẫn trong `tuyen.js` và `menu.js` phải khớp.** Màn mới phải đi tới được từ thanh bên (hoặc từ một màn đã có);
  route có mà không ai vào được là lỗi (`AGENT_RULES.md` §13).
- Ký ức giữ `/nho` (link cũ từ máy A, Telegram), `/ky-uc` là bí danh (D38).
- Tab trình duyệt đặt tên "(n) <trang> · Ben Station" khi có n việc chờ Phê duyệt. Ô tìm ⌘K tìm phía trình duyệt (D38).
- Văn phòng 3D nạp lười (xem mục Văn phòng 3D).

## Chữ và ngôn ngữ
- Tiếng Việt, gọi người dùng "Đại ca". Giải nghĩa thuật ngữ bằng lời thường — Đại ca không phải lập trình viên.
- Tên đối ngoại: "Ben Station · Trạm điều phối"; thẻ người dùng "Đại ca · Chủ trạm" (D20). Không có danh tính Đại ca → thẻ "Chỉ đọc".
- Phông **tự host** (D35, giấy phép OFL): Be Vietnam Pro 400–800 cho chữ; JetBrains Mono 400/500 cho mã bead, lệnh, giờ, id
  (lớp `.mono`). File trong `frontend/src/assets/fonts/`. Không dùng phông từ CDN.
- Cỡ chữ gốc 15 px. Lệnh CLI gợi ý hiện bằng `LenhCli` (chỉ chép chữ, không chạy gì).

## Luật CSP cho mã giao diện
Máy chủ gửi CSP chặt trên mọi phản hồi (`tram/api/bao_mat.py`): `default-src 'none'`; script, style, connect, font chỉ
`'self'`; ảnh `'self'` và `data:`; không khung nhúng. Hệ quả cho code giao diện:
- **Không `style="…"` tĩnh** trong `.vue` (Vue gộp khối tĩnh thành chuỗi HTML nên CSP chặn). Style động `:style` thì được
  (đặt qua CSSOM). Dùng lớp CSS trong `src/kieu/`.
- **Không chèn HTML thô**: cấm `v-html`, `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write`. Icon vẽ bằng
  `<path>` (`BieuTuong`, `bieu_tuong.js`).
- **Không URL ngoài** trong mã nguồn; ngoại lệ duy nhất là link `https://github.com/…` (PR), lọc thêm bằng `laLinkAnToan`.
- **Không `eval`, `new Function`, `WebAssembly.instantiate`**, không `<script>`/`<style>` nội tuyến, không thuộc tính `on…=` trong `dist/index.html`.
- **Không nhúng font thành `data:`** (CSP `font-src 'self'`): `vite.config.js` đặt `assetsInlineLimit: 0`.
- Component `.vue` biên dịch sẵn lúc build (bản Vue chỉ-runtime), nên không cần `unsafe-eval`.
- Kiểm bằng hai cổng (đo lại khi đổi): `npm run kiem` = test node + `kiem-an-toan.mjs` (quét `src/`: HTML thô, style tĩnh,
  URL ngoài); `npm run build && npm run kiem-dist` (quét `dist/`: eval, inline, font ngoài, và **three không nằm trong gói chính**).
- Hai cổng này **không thay** việc mở giao diện trên trình duyệt dưới CSP thật (`tests/chay_thu_giao_dien.py`,
  `AGENT_RULES.md` §13): console không được có lỗi CSP.

## Văn phòng 3D (TresJS / three)
- Dùng `@tresjs/core` + `three`, **khoá đúng phiên bản** trong `frontend/package.json` (không dùng `^`). Thẻ `Tres*` là phần tử của
  renderer TresJS, không phải component Vue — đã cấu hình ở `vite.config.js`.
- Trang `/van-phong` **nạp lười**; three chỉ nằm trong chunk lười đó (gói chính nhẹ, `kiem-dist` chặn nếu lọt vào gói chính).
- Cảnh isometric camera trực giao, mỗi dự án đã thêm là một phòng cộng các phòng cố định; nhân vật là khối hình học theo khe
  (`src/van_phong/`). Cảnh dựng bằng three thuần gắn qua `<primitive>`.
- Nhãn, biển phòng, bong bóng việc là **lớp HTML phủ lên canvas** (`LopNhan`), nhãn là `<button>` thật để dùng bàn phím.
- Luôn có **bản danh sách** (`DanhSachVanPhong`) cho bàn phím, trình đọc màn hình và máy không có WebGL.
- Tùy chọn "Giảm chuyển động" nhớ trong `localStorage`: chỉ là tiện ích riêng của từng máy, bọc `try/catch`, không lưu trạng thái nghiệp vụ.
- Trạng thái nhân vật/phòng do máy chủ suy (`/api/van-phong`); trang chỉ vẽ.

## Thành phần dùng chung
Tên và vai trò (code ở `frontend/src/thanh/`; tìm trước khi tự viết cái mới):
| Thành phần | Vai trò |
| --- | --- |
| `DauTrang` | đầu trang chuẩn (tiêu đề, mô tả, công cụ) |
| `ThanhBen`, `ThanhTren`, `BangEstop`, `OTim` | khung: sidebar, thanh trên, băng estop, ô tìm ⌘K |
| `TheBead`, `TheKhe`, `TheKyUc` | thẻ bead, thẻ khe/máy thợ, thẻ một ký ức |
| `Chibi`, `ThanhHanMuc`, `BieuTuong` | nhân vật chibi theo khe, thanh hạn mức, icon |
| `OChot`, `OTraLoi`, `OGhiNho`, `OGiaoViec` | ô thao tác của Đại ca trong ngăn bên |
| `HopKhe`, `HopViSao` | hộp xác nhận (bật/tắt khe, lý do kéo thẻ) |
| `DongThoiGian`, `SuKienNho` | dòng thời gian bead, sự kiện ký ức |
| `BangUsage`, `usage/BieuDoUsage` | bảng và biểu đồ usage |
| `LenhCli` | lệnh CLI gợi ý + nút sao chép |
| `BangTamDung`, `tu_dong/CongTac` | băng vàng TẠM DỪNG toàn trạm; công tắc `role="switch"` |
| `tu_dong/*` | khối trang Tự động `#/du-an/<ten>`: sẵn sàng deploy, chờ Đại ca, lịch sử, cài đặt, ngăn lịch sử đổi |
| `cai_dat/*`, `phe_duyet/*`, `tong_quan/*`, `usage/*` | khối riêng từng trang; dùng lại lớp chung ở `chung.css` |

## Khi cần thứ chưa có ở đây
1. Tìm trong bảng trên và `frontend/src/kieu/chung.css` trước. Có thì dùng.
2. Chưa có và thuộc giao diện mới: **dừng, dựng mockup, chờ Đại ca duyệt** (luật số một). Chưa viết plan hay code.
3. Đã duyệt: thêm token ở `nen.css`, lớp dùng chung ở `chung.css` (hoặc file trang trong `src/kieu/`), thành phần ở `src/thanh/`.
   Chạy `npm run kiem && npm run build && npm run kiem-dist`, mở trình duyệt dưới CSP thật.
4. Cập nhật mục tương ứng trong file này (tên + vai trò, không chép code) và, nếu đổi luật CSP, báo Đại ca (cửa danh tính và CSP là vùng nhạy cảm).
