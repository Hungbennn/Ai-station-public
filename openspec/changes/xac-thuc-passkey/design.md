# Design — Xác thực passkey

## Context

Đọc mã tại HEAD `135bca9`. Cửa hiện tại: `tram/api/bao_mat.py` kiểm kênh, một header login trong
`dai_ca_logins`, `X-Tram: 1`, Origin máy B; `tram/api/kenh_ghi.py` phân biệt header/socket. Cấu hình
`tram/cau_hinh/tram.py` chưa có người/quyền/passkey. `tram/api/app.py` đăng ký router; `van_phong.py`
đăng ký thêm `dieu_phoi.router`. `tram/bao_tin/` đọc sự kiện, gom tin, gửi lại sau lỗi.

D135–D150 là hướng mới, chưa phải hành vi đã build. `ARCHITECTURE.md`, từ vựng kênh ghi trong
`PRODUCT_ARCHITECTURE.md`, ADR-0004 và hai change mẫu vẫn mô tả socket. Khi triển khai phải cập nhật phần bị thay,
không diễn giải rằng các nguồn cũ đã đồng ý passkey. D87 trong change tự động còn cho Tiếp tục: nguồn mới loại ngoại lệ đó.

## Goals / Non-Goals

Một cửa ghi thống nhất, quyết định bằng hành vi thực chứ không bằng nhãn nút; xác nhận người dùng cho D138,
không bắt chạm mọi lần ghi (D137). Chuẩn bị dữ liệu người/quyền nhưng chỉ một chủ trạm (D136).
Không biến cookie thành bằng chứng có người ngồi trước máy ở mọi yêu cầu; không thay cách ly OS bằng passkey.

## Decisions

### D-1. Ba mức và trạng thái chưa đăng ký (D137–D140)

- **N**: không cần chạm; vẫn kiểm danh tính, quyền, Origin, X-Tram và luật nghiệp vụ.
- **P**: nguy hiểm, cần phiên passkey còn hạn; chưa có phiên thì chạm để mở phiên.
- **R**: nguy hiểm, luôn có xác nhận mới gắn đúng thao tác, dù phiên còn hạn (D140).
- **M**: giao thức máy riêng, không yêu cầu thợ chạm sinh trắc; không được dùng credential máy để mở cửa người.
- **B**: bootstrap/khôi phục theo mã một lần, không phải ngoại lệ ghi nghiệp vụ.

Khi người chưa có passkey hoạt động, mọi ghi dashboard N/P/R bị chặn trừ TẠM DỪNG và bật Estop;
B vẫn hoạt động để đăng ký. M giữ luồng riêng nhưng không được tạo đường vòng vào P/R.
Sau đăng ký, N không cần phiên 8 giờ; P cần phiên; R cần xác nhận mới. Mất phiên không làm mất khả năng dừng.

### D-2. Bảng toàn bộ tuyến POST/PUT/PATCH/DELETE hiện có (D138)

Rà tất cả file `tram/api/*.py`: **23 tuyến POST**, không có PUT/PATCH/DELETE. Hai POST chỉ đọc được giữ trong bảng
để không bỏ sót. “P qua cấp quyền” nghĩa là người chạm khi cấp quyền, máy chỉ đổi quyền đó một lần đúng mục đích.

| Tuyến (đều POST) | File trong `tram/api/` | Mức | Cách xếp / điều kiện |
| --- | --- | --- | --- |
| `/api/bead/{du_an}/{bead_id}/cot` | `tuyen_ghi.py` | N | Kéo cột, D138 miễn chạm; không cho payload biến thành chốt |
| `/api/bead/{du_an}/{bead_id}/chot` | `tuyen_ghi.py` | P | Tạo và đóng decision, nhóm 2 |
| `/api/bead/{du_an}/{bead_id}/thu-lai` | `tuyen_ghi.py` | N | Thử lại, D138 miễn chạm |
| `/api/phe-duyet/{du_an}/{bead_id}/duyet` | `tuyen_ghi.py` | P | Duyệt spec, đóng feature và duyệt đóng thường, nhóm 2 |
| `/api/phe-duyet/{du_an}/{bead_id}/tra-ve` | `tuyen_ghi.py` | N | Trả về, kể cả spec |
| `/api/phe-duyet/{du_an}/{bead_id}/tra-loi` | `tuyen_ghi.py` | P | Mã hiện tại đóng decision/escalation; KHÔNG phải trả lời thường |
| `/api/chu/estop` | `tuyen_chu.py` | N | Bật dừng khẩn, được cả trước đăng ký |
| `/api/chu/tiep-tuc` | `tuyen_chu.py` | P | Tắt Estop, nhóm 3 |
| `/api/khe/{may_id}/{ten}/tat` | `doi_ngu.py` | N | Tắt khe |
| `/api/khe/{may_id}/{ten}/bat` | `doi_ngu.py` | P | Bật lại khe, nhóm 3 |
| `/api/khe/{may_id}/{ten}/cau-dao-dong` | `doi_ngu.py` | P | Đóng cầu dao để khe chạy lại, nhóm 3 |
| `/api/nho/xoa` | `tuyen_nho.py` | P | Xoá ký ức, nhóm 3 |
| `/api/nho/ghi` | `tuyen_nho.py` | N | Ghi ký ức tay không cần chạm; D147, vẫn khoá trước đăng ký |
| `/api/feature/yeu-cau/xem` | `tuyen_yeu_cau.py` | N (đọc) | POST xem trước, không ghi; vẫn kiểm quyền hiện có |
| `/api/feature/yeu-cau` | `tuyen_yeu_cau.py` | N | Gửi phiếu yêu cầu không cần chạm; D147, vẫn khoá trước đăng ký |
| `/api/dieu-phoi/nhip` | `dieu_phoi.py` | M | Mã điều phối riêng + danh tính/CSRF; chỉ sự kiện nhịp, không quyền dashboard |
| `/api/ghep-may` | `ghep.py` | M / P qua cấp quyền | Đổi mã ghép máy; mã chỉ được cấp sau quyền ghép nhóm 3, không nhận mã đăng ký passkey |
| `/api/tho/dang-ky` | `tho.py` | M / P nếu bật | Token máy đăng ký thông tin; không được tự bật lại khe qua đổi thông tin |
| `/api/tho/nhip` | `tho.py` | M | Token máy, phạm vi máy/phiếu/lượt; không quyền chủ |
| `/api/tho/bao` | `tho.py` | M | Báo cáo, đề nghị theo TC; không đóng decision thay chủ |
| `/api/tho/su-kien` | `tho.py` | M | Danh sách loại sự kiện giới hạn; không sự kiện cấp quyền người |
| `/api/tho/da-push` | `tho_them.py` | M | Công bố theo bằng chứng; không duyệt hay deploy tay |
| `/api/tho/da-dong` | `tho_them.py` | M (đọc) | Chỉ tra sự kiện đã đóng để thợ dọn; không đóng bead |

`noi_bo.py` chỉ có GET dùng token nội bộ, không tuyến ghi. Các router đọc còn lại không có POST/PUT/PATCH/DELETE.
`/api/dieu-phoi/nhip` được gắn gián tiếp qua `van_phong.router`, không được bỏ sót khi tách `yeu_cau_ghi`.

**Lỗ đường vòng cần nghiệm thu:** `tram/phieu/khe.py::dang_ky_khe` hiện ghi `khe.dang_ky` khi đổi thông tin,
`khe_dang_bat` coi sự kiện đó là bật. Khi triển khai phải tách đăng ký thông tin khỏi quyền bật; token máy không
được tự bật khe đã tắt hoặc cấp khe mới chạy khi chưa được chủ cho phép. Không chỉ thêm passkey ở nút `/bat`.
Việc ghép máy cũng phải rà CLI cấp mã: không để một lối cấp mã không bảo vệ mở vòng qua dashboard.

### D-3. Các hành vi sẽ có trong change song song (D138, D140)

Tên URL của TM/TC do plan của chúng sở hữu; dưới đây là hợp đồng theo hành vi, không khẳng định đã có route tại HEAD.

| Hành vi | Mức | Nhóm D138 |
| --- | --- | --- |
| Bật/tắt/chỉnh tự merge, các điều kiện | P | 1 |
| Bật tự deploy | R | 1 + D140 |
| Tắt/chỉnh tự deploy ngoài ba lệnh | P | 1 |
| Sửa bất kỳ lệnh deploy / kiểm còn sống / lùi | R | 1 + D140 |
| Deploy tay ở Dự án hoặc Phê duyệt | P | 1, cùng chính sách |
| Tiếp tục sau tạm dừng dự án/toàn trạm | P | 1 |
| Công tắc agent tự cập nhật việc và ba nút con | P | 1 |
| TẠM DỪNG dự án/toàn trạm | N | Ngoại lệ dừng |
| Bật lại máy thợ, cấp quyền ghép máy mới | P | 3 |
| Thêm/thu hồi thiết bị passkey | R | 4 + D140 |
| Trả lời câu hỏi thường không đóng decision | N | Miễn chạm; hiện chưa có tuyến riêng |

Tắt tự động vẫn theo xác nhận thường D128 và phiên P; TẠM DỪNG là đường dừng không cần chạm.
Nếu một yêu cầu sửa nhiều trường, áp mức cao nhất. Loại decision lấy từ máy chủ; không tin `loai=thuong` do client gửi.
Vòng tự merge tự chạy không dùng phiên người (D122); passkey chỉ bảo vệ lệnh/cài đặt do người gửi.

### D-4. Người, credential và phiên (D136, D139, D143)

Đề xuất mô hình tối thiểu, không xây bộ quản trị công ty: `nguoi` có ID ổn định, tên hiển thị, login Tailscale duy nhất,
vai `chu`, trạng thái; quyền ánh xạ phía máy chủ theo hành vi. Một người có nhiều credential; mỗi credential có
ID, public key, người sở hữu, tên gợi nhớ, thời điểm thêm/dùng/thu hồi, bộ đếm và thông tin cần kiểm xác thực.
Tên thiết bị chỉ là tên gợi nhớ, không chứng minh phần cứng; passkey đồng bộ có thể dùng trên nhiều thiết bị.
Danh sách ban đầu chỉ Đại ca. Không tự biến mọi mục `dai_ca_logins` thành một chủ; cấu hình mơ hồ thì đóng cửa ghi.

Phiên server lưu băm mã phiên ngẫu nhiên, người/credential nguồn, login, lúc xác nhận, hết hạn, trạng thái thu hồi.
Cookie đề xuất `__Host-tram-phien`, Path=/, không Domain, HttpOnly, Secure, SameSite=Strict, Max-Age=28800.
Hạn tuyệt đối 8 giờ từ xác nhận mở phiên, không gia hạn ngầm theo hoạt động; xác nhận R không kéo dài phiên cũ.
Đăng nhập lại có thể tạo phiên mới. Không localStorage. Máy chủ so login hiện tại với người, phiên và credential ở
mọi yêu cầu P/R; thiếu, trùng header, khác login hoặc người bị khoá → 403. Sai vai/quyền cũng 403 dù chữ ký đúng.

Kho xác thực thuộc tài khoản trạm, dùng kho riêng tư theo cơ chế mở kho an toàn và migration/sao lưu hiện có;
chốt schema trong plan, không nhét cookie/mã bootstrap/assertion vào `su_kien` hay `thao_tac`.
Private key nằm ở authenticator, server chỉ giữ public key. Mã một lần/phiên chỉ lưu băm và metadata tối thiểu.
Các thay đổi thiết bị và tin cần gửi được ghi nguyên tử để khởi động lại không mất cảnh báo.

### D-5. Xác nhận mới gắn thao tác (D140)

Máy chủ tạo challenge ngẫu nhiên, dùng một lần, thời hạn đề xuất 2 phút; ràng buộc người, phiên, loại thao tác,
đích, băm payload và `ma_thao_tac`. Xác minh bằng `webauthn`: RP ID cố định là tên DNS máy B,
Origin chính xác `https://<ten_may_b>`, challenge, credential owner, chữ ký, user presence và user verification
bắt buộc. Không suy RP/Origin từ Host client. Không tự viết kiểm mật mã; cách xử lý bộ đếm passkey đồng bộ chốt theo
thư viện ở plan, không coi bộ đếm bằng 0 là tự động hợp lệ cho mọi thứ.

R cấp quyền đúng một thao tác, không phải cờ “đã chạm gần đây” dùng được cho mọi lệnh. Thành công xác nhận chưa có
nghĩa nghiệp vụ đã chạy; vẫn kiểm phiên bản, khoá ghi, Estop và cổng của nghiệp vụ sát lúc thực thi.
Huỷ, quá hạn, sai Origin/RP, chữ ký sai, thiếu UV → không ghi. Không tự bật hộp sinh trắc từ poll; chỉ sau chủ bấm.

### D-6. CLI, mã một lần, thêm thiết bị (D141–D144)

**Giao diện CLI đề xuất — chưa tồn tại:** `tram chu passkey cap-ma` và `tram chu passkey khoi-phuc`.
Chỉ chạy trên B trong Terminal.app của tài khoản trạm được bảo vệ khỏi agent. Không cung cấp endpoint HTTP gọi
hai lệnh này. CLI in kế hoạch, yêu cầu `dong-y` từ TTY (khôi phục bắt buộc D144); không cờ `--yes`, không nhận
mã hay xác nhận qua argv. TTY là chống nhầm, KHÔNG phải bằng chứng người: quyền OS phải ngăn agent gọi hoặc đọc kết quả.

Mã mới có ít nhất 128 bit ngẫu nhiên, gắn người/login + mục đích đăng ký, hạn tuyệt đối 10 phút.
In đúng một lần trực tiếp ra TTY, không redirect ra file/log, không đưa vào argv, URL query, clipboard tự động,
sự kiện hoặc Telegram. Trang nhập gửi trong body qua HTTPS, `no-store`, không tự lưu ô nhập. Cấp mã mới huỷ mã cũ
cùng mục đích/người. Giới hạn đề xuất 5 lần mã sai mỗi 10 phút/người và nguồn, lỗi chung không lộ mã hay tài khoản.

Nhập mã chỉ lấy challenge đăng ký, không cấp quyền ghi. Ghi credential và tiêu thụ mã nguyên tử sau ceremony
đăng ký có UV hợp lệ; hai trình duyệt tranh cùng mã chỉ một thành công. Challenge giữ hạn không vượt hạn mã.
Thất bại/huỷ không tự ghi credential; mã vẫn hết đúng hạn, không kéo dài khi xin challenge.

Thiết bị cũ bấm Thêm → xác nhận R → mã/QR mời một lần cùng luật 10 phút → trình duyệt mới vào HTTPS đúng login,
nhập mã và đăng ký passkey bằng UV. QR mời là vật mang bí mật; bản thật dựng cục bộ, không dịch vụ QR ngoài;
không query chứa mã hoặc access log. Cách đóng gói QR chốt ở plan, không thêm npm (D145).
QR mời này khác QR của trình duyệt để dùng điện thoại xác thực WebAuthn. Mã từ B vẫn thêm được thiết bị khi đã có key.

Thu hồi lẻ cần R bằng credential đang hoạt động, thu hồi phiên mở bởi credential đó và mã mời chưa dùng do nó cấp.
D148: không cho thu hồi credential cuối trên web; hướng dẫn dùng khôi phục tại B để không tự khoá mình.
Khôi phục `dong-y`: nguyên tử thu hồi toàn bộ credential, phiên, challenge, mã mời/mã cũ của người; cấp mã mới
10 phút; ghi cảnh báo Telegram. Không chạy lại công việc/tự tiếp tục Estop hay tạm dừng.

### D-7. Đường mạng, tích hợp và đường lui (D135, D145)

Trình duyệt → HTTPS Tailscale Serve → `http://127.0.0.1:7700` tram-api. Chỉ loopback, không nghe mọi interface,
không Funnel. Lệnh chuyển Serve cụ thể chỉ ghi trong kịch bản chạy thật sau khi đối chiếu phiên bản app; phiên này
không chạy. Giữ Host, CSP, Origin, X-Tram; không coi header hay IP là bằng chứng chạm. Tuyến chưa phân loại đóng mặc định.

| Hệ ngoài | Hạn / ai áp (đề xuất khi chưa có D) | Hỏng thì Đại ca thấy | Retry và bí mật |
| --- | --- | --- | --- |
| WebAuthn trình duyệt + verifier | UI 120 giây; server challenge 2 phút tuyệt đối | “Chưa xác nhận — thử lại”, giữ nội dung nghiệp vụ | Challenge mới; không log assertion, clientData hay attestation |
| Tailscale Serve | Client HTTP 15 giây; không tự đổi cấu hình | “Không nối được trạm”, không coi đã ghi thành công | Đối soát rồi cùng mã thao tác; không echo header/cookie |
| Telegram | 10 giây/lần như `telegram.py`; vòng gửi 15 giây | Trạng thái “Cảnh báo đang chờ gửi” | Lưu hàng chờ bền, gửi lại; không hoàn tác thu hồi; chỉ ID sự kiện/loại/giờ/link sạch |
| CLI tại B | Chờ xác nhận tối đa 2 phút rồi huỷ | “Chưa đổi gì” nếu chưa commit; sau commit mất mã thì cấp mã mới | Không tự retry khôi phục, không log stdout có mã |

D145: plan ghim đúng một bản `webauthn` đã ra ≥14 ngày tính lúc chọn, ghi ngày phát hành và khoá phụ thuộc
`cbor2`, `cryptography`, `pyasn1`, `pyOpenSSL`; không tự nêu phiên bản chưa kiểm. Browser dùng API có sẵn,
không dependency npm mới. Cho tải ở D145 không vượt lệnh cấm mạng riêng của phiên bàn giao này.

Chuyển đổi: sao lưu → triển khai cửa mới mặc định đóng → đổi Serve sang TCP → đăng ký A → thử âm A/B →
chỉ sau cổng mới mở các nút. Lỗi thì giữ TẠM DỪNG/Estop và chỉ đọc, không quay lại header cho thao tác nguy hiểm.
Khôi phục bản DB cũ không được làm sống lại phiên/mã/passkey đã thu hồi: quy trình phục hồi buộc vô hiệu phiên/mã,
đối soát danh sách thu hồi hoặc khôi phục danh tính bằng CLI trước mở ghi.

## Phương án đã loại

- **Unix socket sau app Tailscale:** G29 đo app Serve trả 502; không dùng điều kiện socket để mở nút mới.
- **WhoIs địa chỉ tailnet:** xác định máy/người mạng, không xác định người hay agent trên cùng máy đang bấm;
  tiến trình A có thể mang cùng danh tính. Sau proxy còn phải tin nguồn địa chỉ. Không thay passkey bằng WhoIs.
- **Chỉ tin header localhost:** giả được; không giải quyết A/B. Header chỉ là điều kiện phụ để khớp D143.
- **Chạm mọi lần ghi:** trái D137. **Phiên cho cả quản lý key và sửa lệnh:** trái D140.
- **Token ghi dài hạn cho agent:** không chứng minh chủ có mặt, không cấp trong change này.

## Risks / Trade-offs

- **Cookie 8 giờ (D139):** tiến trình cùng tài khoản có thể đọc kho cookie hoặc điều khiển browser đã đăng nhập.
  HttpOnly ngăn JS đọc cookie, không ngăn tiến trình OS cùng tài khoản. P có thể bị lạm dụng trong phiên bị đánh cắp;
  R vẫn cần UV mới nhưng không chống người bị lừa xác nhận. Không tuyên bố chặn tuyệt đối agent A cùng tài khoản.
- **CLI cứu hộ:** nếu agent B chạy cùng tài khoản trạm, nó có thể cấp mã/khôi phục; `dong-y` không phải hàng rào bảo mật.
  Cổng A/B phải ghi rõ UID, quyền đọc cookie/DB/TTY/CLI; chưa cách ly đủ thì chưa đạt mục tiêu D135.
- **Credential đồng bộ:** thu hồi một credential có thể thu hồi nhiều bản sao cùng key. Danh sách “Thiết bị” phải giải
  thích điều này; không hứa thu hồi một chiếc máy vật lý trong khi vẫn giữ bản sao cùng credential.
- **Tin Telegram:** `chong_on.py` hiện gom theo loại/dự án/bead, có thể nuốt các lần thêm key gần nhau. Cần ID sự kiện
  bảo mật riêng, không gộp mất lần; gửi thất bại không làm key bị thu hồi hoạt động trở lại. Không hứa exactly-once
  qua Telegram khi timeout sau khi bên kia nhận; có thể trùng tin, cùng ID để nhận ra.
- **Dừng không chạm:** agent giả được header localhost có thể gây dừng; chấp nhận ưu tiên dừng an toàn theo D135,
  không cho dùng cùng ngoại lệ để Tiếp tục.
- **D146:** dashboard dùng hồ sơ trình duyệt riêng, agent không được điều khiển hồ sơ đó. Đây là luật vận hành,
  không phải bằng chứng cách ly OS; cổng phải đo quyền đọc cookie và điều khiển browser từ agent thật trên A/B.
- **D147:** ghi ký ức tay và gửi phiếu yêu cầu là N; vẫn kiểm danh tính và khoá trước đăng ký.

## Bản đồ tác động khi triển khai

`tram/api/bao_mat.py`, `kenh_ghi.py`: tách cửa mạng/danh tính, quyền người, P/R, M. Các router ở bảng D-2 và router
TM/TC áp chính sách theo hành vi; `tram/cau_hinh/tram.py` ánh xạ người/login; `tram/chu/` CLI mã/khôi phục;
kho xác thực mới theo cơ chế `tram/su_kien/`; `tram/phieu/khe.py`, cấp mã ghép máy chặn đường vòng;
`tram/bao_tin/{nguon,tin,chong_on,vong}.py` gửi đủ cảnh báo; `frontend/src/api.js`, thanh trên, trang thiết bị,
hộp xác nhận theo mockup. Đây là phạm vi plan sau, không file code tạo trong change.

Dữ liệu nghiệp vụ vẫn thuộc kho cũ; passkey chỉ quyết có cho gọi thao tác. Không cấp quyền shell/deploy từ chữ decision,
không bỏ `bat_ghi`, expected_version, expected_commit, idempotency hoặc luật kiểm lại/QC.

## Những điểm đã chốt D146–D150

- D146: hồ sơ trình duyệt dashboard riêng; không cho agent điều khiển. Cổng A/B kiểm thực tế quyền cookie,
  trình duyệt, CLI cứu hộ; nếu vẫn truy cập được thì cổng chưa đạt, không coi profile riêng là hàng rào OS.
- D147: hai tuyến ghi ký ức tay/gửi phiếu yêu cầu là N, vẫn khoá trước đăng ký.
- D148: server từ chối thu hồi passkey cuối trên web, kể cả gọi thẳng API; UI chỉ đường khôi phục tại B.
- D149: sự kiện thêm/thu hồi/khôi phục trong giờ yên lặng được giữ bền và **gom gửi buổi sáng** (khi hết giờ
  yên lặng cấu hình). Bản gom giữ đủ từng ID, loại, thời điểm; không gộp mất lần. Ngoài giờ yên lặng gửi ở vòng kế.
  Telegram lỗi giữ hàng chờ qua restart và retry, không hoàn tác thu hồi; timeout có thể gây gửi trùng cùng ID.
- D150: chín màn mockup đã duyệt 18/10; dòng DRAFT còn trong README là chữ cũ, không mở lại bước duyệt.

Plan: [2026-10-18-lat-passkey.md](../../../docs/plans/2026-10-18-lat-passkey.md).
Các tham số kỹ thuật (challenge 2 phút, giới hạn mã sai) là lựa chọn triển khai cần review trong plan.
