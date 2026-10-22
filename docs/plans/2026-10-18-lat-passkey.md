# Lát passkey — Implementation Plan

> **Review độc lập vòng 3/3: ĐẠT ở mức plan.** Kết luận và bổ sung cuối file thắng ghi chú lịch sử.
> Reviewer vòng 3 chỉ đọc mã và sửa tài liệu, không chạy code/test, áp thử hay gọi mạng.
> Số đo vòng 1/2 là của tác giả trong các phiên trước, không chứng nhận bản bổ sung vòng 3 hoặc cổng OS/browser.
> Quyền áp thử/hoàn nguyên được nhắc bên dưới chỉ thuộc các phiên viết plan trước, không cấp quyền cho phiên review này.

> **Bản sửa sau review Codex vòng 1 (18/10/2026).** Đọc mục **Phản hồi review Codex vòng 1** cuối file.
> Phiên sửa được Đại ca cho áp mã tạm để kiểm chứng, rồi hoàn nguyên; không commit/merge.
> Các số 81 khối/70 file và GREEN trong Tasks 1–12 là lịch sử trước review. Kết quả đo mới ở cuối file,
> không dùng số cũ để chứng nhận bản sửa hoặc cổng OS/browser.

> **For agentic workers:** dùng skill `ai-skills:executing-plans`, thực hiện lần lượt các task và đọc spec trước mã.
> **KHÔNG COMMIT**, kể cả sau GREEN. Lệnh trực tiếp của Đại ca trong phiên này thắng hướng dẫn commit của skill và PLAN-CHUNG.

**Goal:** Cửa ghi dashboard N/P/R theo D137–D155, đăng ký/phiên/thiết bị/khôi phục có kiểm WebAuthn thật,
không cho token máy mở quyền người; cung cấp điểm nối thay `can_kenh_that` cho TM/TC.

**Architecture:** `tram/passkey/` giữ kho xác thực riêng và các giao dịch cấp/thu hồi quyền; `tram/api/` kiểm
login, CSRF và mức thao tác trước nghiệp vụ. Giữ ledger nghiệp vụ hiện có; thêm ràng buộc băm mã/nội dung.
Outbox cùng giao dịch với quản lý thiết bị, vòng Telegram hiện có đọc nó. Browser dùng WebAuthn gốc, modal và trang thiết bị theo D150.

**Tech Stack:** Python 3.12, FastAPI, SQLite, `webauthn==3.0.1`, Vue 3, `navigator.credentials`, pytest 8.4.2,
`node --test`; `cryptography`/`cbor2` đã cài dùng để dựng authenticator giả trong test. Không npm mới.

**Spec:** [change xac-thuc-passkey](../../openspec/changes/xac-thuc-passkey/specs/cua-ghi-passkey/spec.md),
[design, bảng 23 tuyến](../../openspec/changes/xac-thuc-passkey/design.md),
[D137–D150](../quyet-dinh/2026-10-18-passkey.md),
[mockup chín màn đã duyệt D150](../mockup/2026-10-18-passkey/README.md).

**Nền gốc:** `135bca9` của worktree `spec/xac-thuc-passkey`; chưa có TM-1…TC. Bản vá bên dưới là chuỗi áp lên
nền này; phiên sửa áp trên HEAD `067215e` (chỉ thêm review docs), không phải patch vào cây đã ghép TM. Mọi file nguồn chỉ được áp **tạm** để kiểm chứng rồi hoàn nguyên;
đầu ra phiên viết plan chỉ là change, file plan này và `KET-QUA-CODEX.md`. Chưa triển khai, chưa mở cổng thật.

## Global Constraints

- **Kill list §2 mục 1 — cửa danh tính:** sửa `tram/api/bao_mat.py`, nối cửa ghi mới. **Cần Đại ca duyệt plan
  trước triển khai chính thức.** Quyền áp thử offline/hoàn nguyên trong phiên này do lời giao việc cho phép.
  Cũng chạm mục 2 (CLI cấp mã, cảnh báo), mục 4 (kho xác thực mới), mục 8 (cổng thật); không tự chạy cổng.
- **D152 đã duyệt kho xác thực riêng (kill list mục 4).** Không đổi cấu trúc DB nghiệp vụ. Không sửa `su-kien.db`, kho phiếu hay LanceDB. Cần kho riêng
  `TRAM_HOME/passkey.db`: public key/counter, phiên băm, mã băm, challenge dùng một lần, thu hồi và outbox phải
  giao dịch nguyên tử và sống qua restart; không nhét credential vào nhật ký sự kiện chỉ ghi thêm.
- Migration dùng **nguyên cơ chế** `tram/su_kien/phien_ban.py::nang_cap`: `BEGIN IMMEDIATE`, đọc lại phiên bản,
  sao lưu qua kết nối thứ hai trước nâng, SQL rời trong giao dịch, rollback khi lỗi, từ chối kho mới hơn mã.
  Kho mới có `user_version=1`, `BUOC` riêng, backup riêng `sao-luu-passkey/`; không sửa default `BUOC` của kho sự kiện.
  Task 9 bổ sung vào schema **chưa phát hành** của task 2; triển khai đủ chuỗi trước lần mở kho thật đầu tiên.
  Nếu đã mở kho thật v1 của bản trung gian thì phải viết migration v2 được review, không chỉ sửa `CREATE TABLE`.
- Quyền file theo `mo_ket_noi`/`mo_an_toan`: SQLite 0600, kiểm chủ/symlink/hardlink/chuỗi cha; bản sao cùng chuẩn.
  Thư mục, ACL, quyền đọc cookie/TTY/CLI thật là phần cổng, không suy ra từ mode của DB.
- **D146:** Đại ca dùng hồ sơ trình duyệt dashboard riêng, không cấp quyền điều khiển hồ sơ đó cho agent.
  Profile riêng không tự cách ly tiến trình cùng UID. **D153:** đo thấy agent còn với tới hồ sơ dashboard/lệnh
  khôi phục vẫn mở cửa theo quyết định Đại ca, ghi rủi ro vào sổ tay; dự án thật xét riêng khi bật.
  Không gọi đây là đã cách ly hoặc dùng HttpOnly làm bằng chứng ngăn agent.
- N/P/R giữ login Tailscale, `X-Tram: 1`, Origin đúng HTTPS; Host lạ vẫn 421. D143 đòi login khớp ở mỗi yêu cầu.
  Chỉ đúng một login cấu hình được khởi tạo thành chủ; cấu hình nhiều login đóng, không tự cấp nhiều chủ.
- Cookie `__Host-tram-phien`: **HttpOnly, Secure, SameSite=Strict, Path=/, không Domain, Max-Age=28800**;
  hạn tuyệt đối 8 giờ, không sliding, R không gia hạn. Private key không rời authenticator.
- Challenge 120 giây, mã đăng ký/mời 600 giây, mã ≥128 bit (mã CLI dùng 32 byte ngẫu nhiên); mã sai tối đa
  5/600 giây **tổng theo người**, chặt hơn chia theo địa chỉ nguồn và không tin `X-Forwarded-For` giả.
  Trần 20 challenge đang sống/người. Verifier bắt UP/UV, RP/Origin/challenge/counter/chữ ký; không tự viết crypto.
- R gắn băm `{POST, đường đích thực, toàn bộ thân gồm ma_thao_tac}` + người + phiên. Retry cùng quyền không
  sinh thao tác khác; mọi consumer TM/TC vẫn phải dùng ledger idempotency như mục **Ghép với TM/TC**.
- **D147:** ghi ký ức tay và gửi phiếu yêu cầu là N, vẫn khoá trước đăng ký. **D148:** server chặn thu hồi cuối.
  **D149:** giữ tin đêm trong outbox, **gom gửi buổi sáng khi hết giờ yên lặng cấu hình**. D154 chốt **23:00–07:00** (Asia/Ho_Chi_Minh);
  Đại ca tự bật `telegram.gio_yen_lang` trong cấu hình, agent không sửa cấu hình thật; giữ mọi ID/loại/giờ.
  Không dùng `BoChongOn.nhan` hiện có cho tin passkey vì nó bỏ tin mới trong giờ yên lặng.
- Không argv/log/URL/storage/sự kiện/Telegram chứa mã, cookie, assertion, attestation; CLI chỉ TTY, `dong-y`,
  chờ tối đa 120 giây. TTY chống nhầm, không chứng thực con người; quyền OS là cổng bắt buộc của CLI cứu hộ.
- Cả hai ceremony dùng API 3.0.1 đã đọc từ `.venv/lib/python3.12/site-packages/webauthn/`.
  `credential_current_sign_count=0` không bỏ kiểm chữ ký: thư viện cho 0→0 nhưng vẫn kiểm challenge, RP, Origin, UP/UV;
  khi một counter >0 thì counter mới phải lớn hơn counter cũ. Không tự sửa counter để né từ chối.
- Frontend chỉ gọi `fetch` trong `api.js`, không npm mới, không HTML thô/style nội tuyến/URL ngoài.
  Modal dùng `<dialog>` cho focus/ Escape/ trả focus, chỉ mở từ hành động người bấm, không từ polling.
- Tất cả test Python đi qua `tests/chan_host/chay.sh`; số dòng chặn mới phải **0**. Không pytest trần, mạng,
  tải gói, Keychain, Beads ghi, push/merge/commit, hệ thống thật hoặc `~/.tram` thật.
- File `tram/` ≤120 dòng, dòng ≤120 ký tự. Không bỏ kiểm `expected_version`, `expected_commit`, `bat_ghi`,
  khoá/Estop/QC hay điều kiện nghiệp vụ sau xác thực. Không coi test offline là bằng chứng Touch ID/cách ly thật.

## Bằng chứng dependency và môi trường

`pyproject.toml` đã ghim `webauthn==3.0.1` ở HEAD. `uv.lock` ghi wheel phát hành **2026-09-25T16:18:36.405Z**;
đối chiếu ngày viết **2026-10-18**, 23 ngày (>14). Nguồn bản phát hành trong lockfile là PyPI; phiên này không gọi mạng.
Đã đọc `__init__.py`, cả hai hàm sinh options và cả hai verifier trong package cài sẵn, không suy API từ bản khác.

| Gói | Phiên bản lockfile |
|---|---|
| webauthn | 3.0.1 |
| cbor2 | 6.1.5 |
| cryptography | 50.0.2 |
| pyasn1 | 0.6.4 |
| pyasn1-modules | 0.4.2 |
| pyopenssl | 26.4.0 |

Runner đầu tiên bị sandbox chặn cache `/Users/dai-ca/.cache/uv`; đổi cache `/tmp` thì thiếu wheel pygments offline.
Để kiểm được, chỉ sao chép pytest và các thư viện test **đã có ở checkout chính**, cùng `frontend/node_modules`
đã có, vào môi trường tạm của worktree; không tải/cài thêm dependency sản phẩm. Chạy runner với:

```bash
UV_NO_SYNC=1 UV_CACHE_DIR=/tmp/passkey-uv-cache tests/chan_host/chay.sh -q
```

Không dùng số `CURRENT_STATE.md` làm N₀. Cả bộ bị OS sandbox chặn; số đo cụ thể ở cuối plan.
Người điều phối phải chạy lại baseline và cả bộ trên môi trường cho phép trước khi duyệt triển khai.

## Bảng G

| G | Bảo đảm | Task / bằng chứng | Cổng còn lại |
|---|---|---|---|
| G1 | Verifier thật, chữ ký test thật, UV/RP/Origin/counter/challenge | 1, 3; test WebAuthn + race | Touch ID/Windows |
| G2 | Kho riêng, migration/rollback/kho mới hơn; băm mã/phiên | 2, 3, 9 | quyền/backup thật |
| G3 | Đúng người và vai, login khớp, cookie 8h tuyệt đối | 3, 4; đồng hồ tiêm, cookie flags | browser thật |
| G4 | Đủ 23 tuyến, N/P/M; `/tra-loi` luôn P; tuyến lạ đóng | 4; inventory OpenAPI + ma trận cửa | rà lại khi ghép |
| G5 | R ràng buộc đúng thao tác, không kéo dài phiên | 3, 9; sai binding, hết hạn, retry | consumer TM/TC |
| G6 | D141/D144 CLI TTY, dong-y, mã 10 phút, khôi phục hết quyền | 3, 5 | UID/TTY/CLI thật |
| G7 | D148 thu hồi cuối bị chặn, phiên/mã con bị thu hồi | 3; giao dịch khoá ghi | thu hồi thiết bị thật |
| G8 | D142/D149 outbox nguyên tử, đêm gom sáng, restart/retry đủ ID | 6; Telegram giả | Telegram thật |
| G9 | Token máy không bật khe mới/khe đã tắt qua đăng ký | 5, 11; test máy/phiếu | principal thật |
| G10 | Chưa mở cấp mã ghép qua HTTP; CLI cũ đóng theo D155 | 12 | đường vận hành ghép máy |
| G11 | D150: điều hướng, đăng ký, modal, thiết bị, chip, khoá trước đăng ký | 7, 8, 10; node/build | CSP/bố cục/focus |
| G12 | Sai mã/nội dung 409, xác thực lỗi không ghi nghiệp vụ, no-store cả lỗi | 4, 9, 11 | ghép ledger TM/TC |
| G13 | D146 hồ sơ riêng; D153 chấp nhận rủi ro còn truy cập | cổng đo A/B + ghi rủi ro | Không tuyên bố cách ly OS đạt |

## Phạm vi và đường dữ liệu

- Mã nghiệp vụ đang có giữ nguyên; cửa người đổi ở dependency chung, hook `/dieu-phoi/nhip` giữ cửa token riêng.
- Kho xác thực: `nguoi`, `khoa`, `ma`, `phien`, `hoi`, `quyen`, `tin`, `sai`, `thao_tac`.
  `tin` là outbox an ninh, không chứa nội dung nghiệp vụ; các bảng quyền có khoá người/phiên/credential.
  `thao_tac` mới chỉ giữ người + mã + băm, **không thay bảng kết quả nghiệp vụ**.
- Không có tiến trình mới: vòng `tram-bao-tin` hiện có đọc outbox trước cả nhánh khởi tạo mốc.
  Gửi ngoài khoá DB, tối đa 20 dòng/bản tin, timeout 10 giây của adapter Telegram; crash sau gửi trước đánh dấu
  có thể trùng cùng ID. Thu hồi vẫn hiệu lực ngay dù báo tin chưa gửi.
- Phản hồi đăng ký không tự mở phiên: sau đăng ký cần assertion đăng nhập để nhận cookie (hai ceremony rõ ràng).
- Trong lát này, lời “mã/QR” của D142 chọn **mã dùng một lần**, hiển thị chỉ trong bộ nhớ trang. QR dùng điện thoại
  để xác thực vẫn do browser cung cấp; không tự vẽ QR WebAuthn, không tải thư viện QR.
- **D155:** đóng `tram chu cap-ma <may_id>` cũ và chưa mở `/api/passkey/ghep-ma` (404 kể cả có phiên).
  Nút dashboard và endpoint cấp mã có chống lặp cùng giao dịch kho phiếu thuộc lát sau, cần mockup duyệt.
  Không nhầm với `tram chu passkey cap-ma` (bootstrap D141); không đổi API đổi mã `/api/ghep-may`.

## Thứ tự thực hiện và cách đọc mã

Làm 1→12 rồi áp đầy đủ **Task 13 — bản GREEN đã sửa qua vòng 2** và test trong **Phản hồi review Codex vòng 2** trước tích hợp. Bổ sung test vòng 3 ở cuối file. Không phát hành schema trung gian. Mỗi task: đọc Scenario → áp test nguyên văn → chạy RED → áp mã → chạy GREEN → không commit.
Ở Task 13, áp cả test vòng 1 và vòng 2 **trước** bản toàn file GREEN; không áp GREEN rồi đòi test vòng 2 đỏ.
RED của từng phiên sửa trong các bảng là lịch sử trên bản trước sửa của phiên đó, không phải tất cả đều tái hiện
trên chuỗi cuối này. Riêng endpoint ghép máy đã là 404 ở Task 4: test đóng endpoint Task 12 xanh sẵn;
test CLI cũ mới là RED cần bản vá Task 12. Các test coverage xanh sẵn không được báo là RED đã đo.
File mới là toàn bộ nội dung; file đã có là unified diff. Mỗi hunk đã được dựng trên HEAD + các task trước nó.
Các test helper là mã chạy test, không được đưa vào `tram/` hay thêm cửa bỏ xác thực cho sản phẩm.
Task 11 chuyển tiền điều kiện test nghiệp vụ sang phiên/cho phép khe thực; **không override dependency bảo mật**.

## Ma trận tuyến dùng để nghiệm thu

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

Không gắn P lên POST chỉ đọc `/xem`; token máy M giữ các kiểm riêng hiện có. R chưa có trong 23 tuyến HEAD,
được thêm ở quản lý passkey và nối các hành vi TM/TC theo mục ghép.

## Task 1: Verifier WebAuthn và authenticator giả ký thật

**Scenario:** Kiểm WebAuthn đầy đủ trước khi mở quyền; Windows có đường xác nhận phù hợp.

**Files:**

- `tram/passkey/__init__.py`
- `tram/passkey/webauthn.py`
- `tests/passkey_gia.py`
- `tests/test_passkey_webauthn.py`

**Interfaces:** tuy_chon(rp, login, nguoi: bytes, challenge: bytes, ids, tao) → dict; dang_ky(...) → VerifiedRegistration; dang_nhap(..., public_key, dem) → VerifiedAuthentication; lỗi TuChoi cố định.

- [ ] **Step 1 — áp test và helper test nguyên văn:**

### `tests/passkey_gia.py`

```python
"""Authenticator offline: private key chỉ nằm trong test, chữ ký ES256 thật."""
import hashlib
import json
import os

import cbor2
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from webauthn.helpers import bytes_to_base64url as b64


class KhoaGia:
    def __init__(self):
        self.khoa = ec.generate_private_key(ec.SECP256R1())
        self.id = os.urandom(32)

    def tra(self, challenge, *, dang_ky=False, rp='b.test', origin='https://b.test', uv=True, up=True, dem=0):
        client = json.dumps({'type': 'webauthn.create' if dang_ky else 'webauthn.get',
                             'challenge': b64(challenge), 'origin': origin}).encode()
        auth = hashlib.sha256(rp.encode()).digest() + bytes([(1 if up else 0) | (4 if uv else 0) | (64 if dang_ky else 0)])
        auth += dem.to_bytes(4, 'big')
        if dang_ky:
            pub = self.khoa.public_key().public_numbers()
            cose = cbor2.dumps({1: 2, 3: -7, -1: 1, -2: pub.x.to_bytes(32, 'big'), -3: pub.y.to_bytes(32, 'big')})
            auth += bytes(16) + len(self.id).to_bytes(2, 'big') + self.id + cose
            # packed self-attestation có chữ ký thật, không chứng thư/thiết bị thật.
            sig = self.khoa.sign(auth + hashlib.sha256(client).digest(), ec.ECDSA(hashes.SHA256()))
            response = {'attestationObject': b64(cbor2.dumps(
                {'fmt': 'packed', 'authData': auth, 'attStmt': {'alg': -7, 'sig': sig}}))}
        else:
            sig = self.khoa.sign(auth + hashlib.sha256(client).digest(), ec.ECDSA(hashes.SHA256()))
            response = {'authenticatorData': b64(auth), 'signature': b64(sig), 'userHandle': None}
        return {'id': b64(self.id), 'rawId': b64(self.id), 'type': 'public-key',
                'response': {**response, 'clientDataJSON': b64(client)}}
```

### `tests/test_passkey_webauthn.py`

```python
import json
import pytest
from passkey_gia import KhoaGia
from tram.passkey.webauthn import dang_ky, dang_nhap, tuy_chon, TuChoi


def test_verifier_that_va_uv_bat_buoc():
    k, c = KhoaGia(), b'c' * 32
    opt = tuy_chon('b.test', 'chu', b'u' * 32, c, [], True)
    assert opt['authenticatorSelection']['userVerification'] == 'required'
    r = dang_ky(k.tra(c, dang_ky=True), c, 'b.test')
    assert r.credential_id == k.id
    a = dang_nhap(k.tra(c), c, 'b.test', r.credential_public_key, 0)
    assert a.user_verified and a.new_sign_count == 0
    assert tuy_chon('b.test', 'chu', b'u'*32, c, [k.id], False)['userVerification'] == 'required'


@pytest.mark.parametrize('loi', ['uv', 'origin', 'rp', 'challenge', 'chu_ky', 'dem'])
def test_tu_choi_bang_chung_sai(loi):
    k, c = KhoaGia(), b'c' * 32
    r = dang_ky(k.tra(c, dang_ky=True), c, 'b.test')
    kw = {'uv': False} if loi == 'uv' else {loi: 'gia'} if loi in ('rp', 'origin') else {}
    a = k.tra(b'x'*32 if loi == 'challenge' else c, **kw)
    if loi == 'chu_ky':
        a['response']['signature'] = 'AAAA'
    with pytest.raises(TuChoi, match='Chưa xác nhận') as e:
        dang_nhap(a, c, 'b.test', r.credential_public_key, 1 if loi == 'dem' else 0)
    assert 'gia' not in str(e.value)


def test_dang_ky_khong_uv():
    k, c = KhoaGia(), b'c'*32
    with pytest.raises(TuChoi):
        dang_ky(k.tra(c, dang_ky=True, uv=False), c, 'b.test')
```

- [ ] **Step 2 — RED:**

```bash
UV_NO_SYNC=1 UV_CACHE_DIR=/tmp/passkey-uv-cache tests/chan_host/chay.sh -q tests/test_passkey_webauthn.py
```

**Bằng chứng đã chạy:** 8 passed; RED: ModuleNotFoundError: tram.passkey.webauthn

- [ ] **Step 3 — áp mã nguyên văn:**

### `tram/passkey/__init__.py`

```python
"""Cửa người bằng passkey; không chứa private key."""
```

### `tram/passkey/webauthn.py`

```python
"""Adapter py_webauthn 3.0.1; lỗi không mang dữ liệu ceremony."""
import json
from webauthn import (generate_registration_options, generate_authentication_options,
                      verify_registration_response, verify_authentication_response, options_to_json)
from webauthn.helpers.structs import (AuthenticatorSelectionCriteria, PublicKeyCredentialDescriptor,
                                     UserVerificationRequirement)


class TuChoi(ValueError):
    pass


def tuy_chon(rp, login, nguoi, challenge, ids, tao):
    chung = dict(rp_id=rp, challenge=challenge, timeout=120000)
    ds = [PublicKeyCredentialDescriptor(id=i) for i in ids]
    if tao:
        opt = generate_registration_options(**chung, rp_name='Trạm', user_name=login, user_id=nguoi,
            exclude_credentials=ds, authenticator_selection=AuthenticatorSelectionCriteria(
                user_verification=UserVerificationRequirement.REQUIRED))
    else:
        opt = generate_authentication_options(**chung, allow_credentials=ds,
                                             user_verification=UserVerificationRequirement.REQUIRED)
    return json.loads(options_to_json(opt))


def dang_ky(credential, challenge, rp):
    try:
        return verify_registration_response(credential=credential, expected_challenge=challenge,
            expected_rp_id=rp, expected_origin=f'https://{rp}', require_user_presence=True,
            require_user_verification=True)
    except Exception:
        raise TuChoi('Chưa xác nhận — thử lại') from None


def dang_nhap(credential, challenge, rp, public_key, dem):
    try:
        return verify_authentication_response(credential=credential, expected_challenge=challenge,
            expected_rp_id=rp, expected_origin=f'https://{rp}', credential_public_key=public_key,
            credential_current_sign_count=dem, require_user_verification=True)
    except Exception:
        raise TuChoi('Chưa xác nhận — thử lại') from None
```

- [ ] **Step 4 — GREEN:**

```bash
UV_NO_SYNC=1 UV_CACHE_DIR=/tmp/passkey-uv-cache tests/chan_host/chay.sh -q tests/test_passkey_webauthn.py
```

Chạy thêm tập tích hợp ở mục kiểm chứng cuối; không cộng các lượt lặp thành số test mới.

- [ ] **Step 5 — dừng ở cây làm việc, KHÔNG commit.** Người điều phối review diff và bằng chứng.

## Task 2: Kho xác thực riêng và mã một lần

**Scenario:** Đăng ký đầu tiên bằng mã một lần; khôi phục toàn bộ quyền cũ.

**Files:**

- `tram/passkey/luoc_do.py`
- `tram/passkey/kho.py`
- `tests/test_passkey_kho.py`

**Interfaces:** mo_kho(Path) → context SQLite; giao_dich(db); nguoi(db, login); cap_ma(db, u, luc, khoi_phuc=False, nguon=None); phien(db,u,cookie,luc). Hàm ghi nhận giao dịch người gọi, không tự mở kho hệ thật.

- [ ] **Step 1 — áp test và helper test nguyên văn:**

### `tests/test_passkey_kho.py`

```python
import sqlite3
import pytest
from tram.passkey.kho import mo_kho, giao_dich, nguoi, cap_ma, bam, TuChoi
from tram.su_kien.phien_ban import LoiPhienBan


def test_ma_chi_luu_bam_va_khoi_phuc(tmp_path):
    p = tmp_path/'passkey.db'
    with mo_kho(p) as db, giao_dich(db):
        u = nguoi(db, 'chu')
        m = cap_ma(db, u, 100, False)
        assert db.execute('select bam,han from ma').fetchone()[:] == (bam(m), 700)
        m2 = cap_ma(db, u, 101, True)
        assert db.execute('select count(*) from ma').fetchone()[0] == 1
        assert db.execute('select loai from tin').fetchone()[0] == 'khoi-phuc'
        assert m != m2
    assert m.encode() not in p.read_bytes()
    with mo_kho(p) as db:
        assert nguoi(db, 'chu')['id'] == u['id']
        with pytest.raises(TuChoi):
            nguoi(db, 'khac')


def test_migration_va_rollback(tmp_path):
    p = tmp_path/'passkey.db'
    with mo_kho(p) as db:
        assert db.execute('pragma user_version').fetchone()[0] == 1
        with pytest.raises(RuntimeError), giao_dich(db):
            nguoi(db, 'chu')
            raise RuntimeError()
        assert db.execute('select count(*) from nguoi').fetchone()[0] == 0
        db.execute('pragma user_version=2')
    with pytest.raises(LoiPhienBan):
        with mo_kho(p):
            pass
```

- [ ] **Step 2 — RED:**

```bash
UV_NO_SYNC=1 UV_CACHE_DIR=/tmp/passkey-uv-cache tests/chan_host/chay.sh -q tests/test_passkey_kho.py
```

**Bằng chứng đã chạy:** 2 passed; RED: ModuleNotFoundError: tram.passkey.kho

- [ ] **Step 3 — áp mã nguyên văn:**

### `tram/passkey/luoc_do.py`

```python
"""Kho riêng: không đổi su-kien.db, số phiên bản riêng qua cùng cơ chế migration."""
BUOC = {1: (
    'CREATE TABLE nguoi(id BLOB PRIMARY KEY, login TEXT UNIQUE NOT NULL, vai TEXT NOT NULL, bat INT NOT NULL)',
    'CREATE TABLE khoa(id BLOB PRIMARY KEY, nguoi BLOB NOT NULL, public BLOB NOT NULL, dem INT NOT NULL, '
    'ten TEXT NOT NULL, tao REAL NOT NULL, dung REAL, thu REAL)',
    'CREATE TABLE ma(bam TEXT PRIMARY KEY, nguoi BLOB NOT NULL, nguon BLOB, han REAL NOT NULL)',
    'CREATE TABLE phien(bam TEXT PRIMARY KEY, nguoi BLOB NOT NULL, khoa BLOB NOT NULL, '
    'login TEXT NOT NULL, han REAL NOT NULL)',
    'CREATE TABLE hoi(id TEXT PRIMARY KEY, nguoi BLOB NOT NULL, challenge BLOB NOT NULL, '
    'loai TEXT NOT NULL, rang TEXT NOT NULL, phien TEXT NOT NULL, ma TEXT NOT NULL, han REAL NOT NULL)',
    'CREATE TABLE quyen(id TEXT PRIMARY KEY, nguoi BLOB NOT NULL, phien TEXT NOT NULL, '
    'rang TEXT NOT NULL, han REAL NOT NULL, dung INT NOT NULL DEFAULT 0)',
    'CREATE TABLE tin(id INTEGER PRIMARY KEY, loai TEXT NOT NULL, luc REAL NOT NULL, gui INT NOT NULL DEFAULT 0)',
    'CREATE TABLE sai(nguoi BLOB PRIMARY KEY, dem INT NOT NULL, han REAL NOT NULL)',
)}
```

### `tram/passkey/kho.py`

```python
"""Kho passkey riêng tư; giao dịch ngắn, gọi WebAuthn cục bộ trong khoá ghi."""
import hashlib
import secrets
import sqlite3
from contextlib import contextmanager

from tram.passkey.luoc_do import BUOC
from tram.passkey.webauthn import TuChoi
from tram.su_kien.ket_noi import mo_ket_noi
from tram.su_kien.phien_ban import nang_cap


def bam(s):
    return hashlib.sha256(s.encode()).hexdigest()


@contextmanager
def mo_kho(path):
    db = mo_ket_noi(path)
    try:
        nang_cap(db, thu_muc_sao_luu=path.parent/'sao-luu-passkey', buoc=BUOC, moi=1)
        db.row_factory = sqlite3.Row
        yield db
    finally:
        db.close()


@contextmanager
def giao_dich(db):
    db.execute('BEGIN IMMEDIATE')
    try:
        yield
        db.commit()
    except BaseException:
        db.rollback()
        raise


def nguoi(db, login):
    u = db.execute('SELECT * FROM nguoi WHERE login=?', (login,)).fetchone()
    if u is None and not db.execute('SELECT 1 FROM nguoi').fetchone():
        db.execute('INSERT INTO nguoi VALUES(?,?,?,1)', (secrets.token_bytes(32), login, 'chu'))
        u = db.execute('SELECT * FROM nguoi WHERE login=?', (login,)).fetchone()
    if u is None or not u['bat'] or u['vai'] != 'chu':
        raise TuChoi('Không có quyền')
    return u


def cap_ma(db, u, luc, khoi_phuc=False, nguon=None):
    if khoi_phuc:
        db.execute('UPDATE khoa SET thu=? WHERE nguoi=? AND thu IS NULL', (luc, u['id']))
        for bang in ('phien', 'hoi', 'quyen', 'sai'):
            db.execute(f'DELETE FROM {bang} WHERE nguoi=?', (u['id'],))
        db.execute('INSERT INTO tin(loai,luc) VALUES(?,?)', ('khoi-phuc', luc))
    db.execute('DELETE FROM ma WHERE nguoi=?', (u['id'],))
    ma = secrets.token_urlsafe(32)
    db.execute('INSERT INTO ma VALUES(?,?,?,?)', (bam(ma), u['id'], nguon, luc+600))
    return ma


def phien(db, u, cookie, luc):
    p = db.execute('SELECT p.* FROM phien p JOIN khoa k ON k.id=p.khoa '
                   'WHERE p.bam=? AND p.nguoi=? AND p.login=? AND p.han>? AND k.thu IS NULL',
                   (bam(cookie), u['id'], u['login'], luc)).fetchone()
    if p is None:
        raise TuChoi('Cần phiên passkey')
    return p


def cac_khoa(db, u):
    return db.execute('SELECT * FROM khoa WHERE nguoi=? AND thu IS NULL ORDER BY tao', (u['id'],)).fetchall()
```

- [ ] **Step 4 — GREEN:**

```bash
UV_NO_SYNC=1 UV_CACHE_DIR=/tmp/passkey-uv-cache tests/chan_host/chay.sh -q tests/test_passkey_kho.py
```

Chạy thêm tập tích hợp ở mục kiểm chứng cuối; không cộng các lượt lặp thành số test mới.

- [ ] **Step 5 — dừng ở cây làm việc, KHÔNG commit.** Người điều phối review diff và bằng chứng.

## Task 3: Ceremony, phiên, quyền R, thêm/thu hồi/khôi phục

**Scenario:** Phiên tám giờ; D140; đăng ký; race mã; D148; mất hết thiết bị.

**Files:**

- `tram/passkey/nghi_le.py`
- `tram/passkey/thiet_bi.py`
- `tram/passkey/dich_vu.py`
- `tests/test_passkey_dich_vu.py`

**Interfaces:** DichVu(path, login, rp, dong_ho=time.time). bat_dau(loai, cookie="", rang="", ma="") → {id,publicKey}; ket_thuc(id, credential, ten) → đăng ký/cookie/quyen. can_phien(cookie), trang_thai(cookie), moi(cookie,quyen,rang=...), thu_hoi(cookie,quyen,target,rang=...).

- [ ] **Step 1 — áp test và helper test nguyên văn:**

### `tests/test_passkey_dich_vu.py`

```python
import concurrent.futures
import pytest
from passkey_gia import KhoaGia
from webauthn.helpers import base64url_to_bytes
from tram.passkey.dich_vu import DichVu
from tram.passkey.kho import mo_kho, giao_dich, nguoi, cap_ma, cac_khoa, TuChoi


@pytest.fixture
def dv(tmp_path):
    clock = [100.0]
    d = DichVu(tmp_path/'passkey.db', 'chu', 'b.test', lambda: clock[0])
    d.clock = clock
    return d


def them(d, ma=None):
    k = KhoaGia()
    if ma is None:
        ma = d.cap_ma()
    o = d.bat_dau('dang-ky', ma=ma)
    d.ket_thuc(o['id'], k.tra(base64url_to_bytes(o['publicKey']['challenge']), dang_ky=True), ten='Máy A')
    return k


def login(d, k, loai='phien', cookie='', rang=''):
    o = d.bat_dau(loai, cookie=cookie, rang=rang)
    return d.ket_thuc(o['id'], k.tra(base64url_to_bytes(o['publicKey']['challenge'])))


def test_phien_8_gio_va_login_thu_hoi(dv):
    k = them(dv)
    c = login(dv, k)['cookie']
    dv.clock[0] += 28799
    assert dv.trang_thai(c)['con_giay'] == 1
    dv.clock[0] += 1
    assert dv.trang_thai(c)['con_giay'] == 0
    with pytest.raises(TuChoi):
        dv.can_phien(c)
    with pytest.raises(TuChoi):
        DichVu(dv.path, 'khac', dv.rp).trang_thai(c)
    dv.cap_ma(khoi_phuc=True)
    assert dv.trang_thai(c)['thiet_bi'] == []


def test_r_gan_payload_khong_gia_han_va_chan_cuoi(dv):
    k = them(dv)
    c = login(dv, k)['cookie']
    dv.clock[0] += 99
    q = login(dv, k, 'r', c, 'thu:1')['quyen']
    with pytest.raises(TuChoi):
        dv.thu_hoi(c, q, 'khac', rang='thu:2')
    with pytest.raises(TuChoi, match='cuối'):
        dv.thu_hoi(c, q, dv.trang_thai(c)['thiet_bi'][0]['id'], rang='thu:1')
    assert dv.trang_thai(c)['con_giay'] == 28701
    k2 = them(dv)
    c2 = login(dv, k2)['cookie']
    target = dv.trang_thai(c)['thiet_bi'][1]['id']
    q = login(dv, k, 'r', c, 'thu:2')['quyen']
    dv.thu_hoi(c, q, target, rang='thu:2')
    with pytest.raises(TuChoi):
        dv.can_phien(c2)


def test_replay_race_ma_va_challenge(dv):
    ma = dv.cap_ma()
    ks = [KhoaGia(), KhoaGia()]
    os = [dv.bat_dau('dang-ky', ma=ma) for _ in ks]
    def go(i):
        try:
            return dv.ket_thuc(os[i]['id'], ks[i].tra(
                base64url_to_bytes(os[i]['publicKey']['challenge']), dang_ky=True))
        except TuChoi:
            return None
    with concurrent.futures.ThreadPoolExecutor() as pool:
        results = list(pool.map(go, range(2)))
    assert sum(r is not None for r in results) == 1
    assert len(dv.trang_thai('')['thiet_bi']) == 1
    assert go(0) is None and go(1) is None


def test_han_ma_challenge_va_rate_limit(dv):
    ma = dv.cap_ma()
    dv.clock[0] += 599
    o = dv.bat_dau('dang-ky', ma=ma)
    dv.clock[0] += 1
    with pytest.raises(TuChoi):
        dv.ket_thuc(o['id'], KhoaGia().tra(base64url_to_bytes(o['publicKey']['challenge']), dang_ky=True))
    for _ in range(5):
        with pytest.raises(TuChoi):
            dv.bat_dau('dang-ky', ma='sai')
    with pytest.raises(TuChoi, match='Quá nhiều'):
        dv.bat_dau('dang-ky', ma=ma)


def test_khoi_phuc_huy_het_va_tin_ben(dv):
    k = them(dv)
    c = login(dv, k)['cookie']
    q = login(dv, k, 'r', c, 'them')['quyen']
    ma = dv.moi(c, q, rang='them')['ma']
    o = dv.bat_dau('dang-ky', ma=ma)
    moi = dv.cap_ma(khoi_phuc=True)
    with pytest.raises(TuChoi):
        dv.ket_thuc(o['id'], KhoaGia().tra(base64url_to_bytes(o['publicKey']['challenge']), dang_ky=True))
    with pytest.raises(TuChoi):
        dv.can_phien(c)
    with mo_kho(dv.path) as db:
        assert db.execute('select count(*) from tin').fetchone()[0] == 2
    them(dv, moi)


def test_r_het_han_va_retry_khong_cap_ma_lan_hai(dv):
    k = them(dv)
    c = login(dv,k)['cookie']
    q = login(dv,k,'r',c,'them-het')['quyen']
    dv.clock[0] += 120
    with pytest.raises(TuChoi):
        dv.moi(c,q,rang='them-het')
    q = login(dv,k,'r',c,'them-cung-ma')['quyen']
    m = dv.moi(c,q,rang='them-cung-ma')
    q2 = login(dv,k,'r',c,'them-cung-ma')['quyen']
    assert q2 == q
    assert dv.moi(c,q2,rang='them-cung-ma') == m


def test_khoa_nguoi_va_vai_khong_cho_phien(dv):
    k = them(dv); c = login(dv,k)['cookie']
    with mo_kho(dv.path) as db,giao_dich(db):
        db.execute("UPDATE nguoi SET vai='xem'")
    with pytest.raises(TuChoi):
        dv.can_phien(c)
    with mo_kho(dv.path) as db,giao_dich(db):
        db.execute("UPDATE nguoi SET vai='chu',bat=0")
    with pytest.raises(TuChoi):
        dv.can_phien(c)
```

- [ ] **Step 2 — RED:**

```bash
UV_NO_SYNC=1 UV_CACHE_DIR=/tmp/passkey-uv-cache tests/chan_host/chay.sh -q tests/test_passkey_dich_vu.py
```

**Bằng chứng đã chạy:** 7 passed; RED đầu: ModuleNotFoundError: tram.passkey.dich_vu; test bổ sung retry R từng đỏ AssertionError q2 != q rồi xanh. Sai contract test moi trả dict đã sửa thành lấy ["ma"], không thay kỳ vọng hành vi.

- [ ] **Step 3 — áp mã nguyên văn:**

### `tram/passkey/nghi_le.py`

```python
"""Ceremony nguyên tử: mã/challenge dùng một lần, UV do thư viện kiểm."""
import secrets
from tram.passkey.kho import bam, cac_khoa, phien, TuChoi
from tram.passkey.webauthn import dang_ky, dang_nhap, tuy_chon
from webauthn.helpers import base64url_to_bytes


def bat_dau(db, u, rp, luc, loai, cookie, rang, ma):
    if loai not in ('dang-ky', 'phien', 'r') or len(rang) > 128:
        raise TuChoi('Yêu cầu không hợp lệ')
    han, mh, ph = luc+120, '', ''
    if loai == 'dang-ky':
        sai = db.execute('SELECT * FROM sai WHERE nguoi=?', (u['id'],)).fetchone()
        if sai and sai['han'] > luc and sai['dem'] >= 5:
            raise TuChoi('Quá nhiều lần — thử lại sau')
        m = db.execute('SELECT * FROM ma WHERE bam=? AND nguoi=? AND han>?', (bam(ma), u['id'], luc)).fetchone()
        if m is None:
            dem, het = (sai['dem']+1, sai['han']) if sai and sai['han'] > luc else (1, luc+600)
            db.execute('INSERT OR REPLACE INTO sai VALUES(?,?,?)', (u['id'], dem, het))
            db.commit()  # giữ lần sai dù giao dịch ngoài từ chối; chưa có thay đổi nào khác
            raise TuChoi('Mã không hợp lệ hoặc hết hạn')
        mh, han = m['bam'], min(han, m['han'])
    elif not cac_khoa(db, u):
        raise TuChoi('Cần đăng ký passkey')
    elif loai == 'r':
        ph = phien(db, u, cookie, luc)['bam']
        if not rang:
            raise TuChoi('Thiếu thao tác')
    cid, challenge = secrets.token_urlsafe(32), secrets.token_bytes(32)
    db.execute('DELETE FROM hoi WHERE han<=?', (luc,))
    if db.execute('SELECT count(*) FROM hoi WHERE nguoi=?', (u['id'],)).fetchone()[0] >= 20:
        raise TuChoi('Quá nhiều lần — thử lại sau')
    db.execute('INSERT INTO hoi VALUES(?,?,?,?,?,?,?,?)',
               (cid, u['id'], challenge, loai, rang, ph, mh, han))
    return {'id': cid, 'publicKey': tuy_chon(rp, u['login'], u['id'], challenge,
            [k['id'] for k in cac_khoa(db, u)], loai == 'dang-ky')}


def ket_thuc(db, u, rp, luc, cid, credential, ten):
    h = db.execute('SELECT * FROM hoi WHERE id=? AND nguoi=? AND han>?', (cid, u['id'], luc)).fetchone()
    if h is None:
        raise TuChoi('Chưa xác nhận — thử lại')
    if h['loai'] == 'dang-ky':
        m = db.execute('SELECT * FROM ma WHERE bam=? AND nguoi=? AND han>?',
                       (h['ma'], u['id'], luc)).fetchone()
        if m is None:
            raise TuChoi('Mã không hợp lệ hoặc hết hạn')
        r = dang_ky(credential, h['challenge'], rp)
        if db.execute('SELECT 1 FROM khoa WHERE id=?', (r.credential_id,)).fetchone():
            raise TuChoi('Passkey đã có')
        db.execute('INSERT INTO khoa VALUES(?,?,?,?,?,?,NULL,NULL)',
                   (r.credential_id, u['id'], r.credential_public_key, r.sign_count, ten[:80], luc))
        db.execute('DELETE FROM ma WHERE bam=?', (h['ma'],))
        db.execute('INSERT INTO tin(loai,luc) VALUES(?,?)', ('them', luc))
        out = {'da_dang_ky': True}
    else:
        try:
            kid = base64url_to_bytes(credential['id'])
        except Exception:
            raise TuChoi('Chưa xác nhận — thử lại') from None
        k = db.execute('SELECT * FROM khoa WHERE id=? AND nguoi=? AND thu IS NULL', (kid, u['id'])).fetchone()
        if k is None:
            raise TuChoi('Chưa xác nhận — thử lại')
        r = dang_nhap(credential, h['challenge'], rp, k['public'], k['dem'])
        handle = credential.get('response', {}).get('userHandle')
        if handle is not None and base64url_to_bytes(handle) != u['id']:
            raise TuChoi('Chưa xác nhận — thử lại')
        db.execute('UPDATE khoa SET dem=?,dung=? WHERE id=?', (r.new_sign_count, luc, kid))
        token = secrets.token_urlsafe(32)
        if h['loai'] == 'phien':
            db.execute('INSERT INTO phien VALUES(?,?,?,?,?)', (bam(token), u['id'], kid, u['login'], luc+28800))
            out = {'cookie': token, 'han': luc+28800}
        else:
            p = db.execute('SELECT p.* FROM phien p JOIN khoa k ON p.khoa=k.id WHERE p.bam=? '
                           'AND p.han>? AND k.thu IS NULL', (h['phien'], luc)).fetchone()
            if p is None:
                raise TuChoi('Cần phiên passkey')
            cu = db.execute('SELECT * FROM quyen WHERE nguoi=? AND phien=? AND rang=?',
                            (u['id'], h['phien'], h['rang'])).fetchone()
            if cu:
                token = cu['id']
                if not cu['dung']:
                    db.execute('UPDATE quyen SET han=? WHERE id=?', (min(luc+120, p['han']), token))
            else:
                db.execute('INSERT INTO quyen VALUES(?,?,?,?,?,0)',
                           (token, u['id'], h['phien'], h['rang'], min(luc+120, p['han'])))
            out = {'quyen': token}
    db.execute('DELETE FROM hoi WHERE id=?', (cid,))
    return out
```

### `tram/passkey/thiet_bi.py`

```python
"""R chỉ dành đúng một thao tác; retry cùng thao tác không sinh quyền mới."""
import hashlib
import hmac
from webauthn.helpers import base64url_to_bytes
from tram.passkey.kho import bam, cac_khoa, phien, TuChoi


def can_r(db, u, cookie, qid, rang, luc):
    p = phien(db, u, cookie, luc)
    q = db.execute('SELECT * FROM quyen WHERE id=? AND nguoi=? AND phien=? AND rang=?',
                   (qid, u['id'], p['bam'], rang)).fetchone()
    if q is None or (not q['dung'] and q['han'] <= luc):
        raise TuChoi('Cần chạm lại cho thao tác này')
    return p, q


def moi(db, u, cookie, qid, rang, luc):
    p, q = can_r(db, u, cookie, qid, rang, luc)
    ma = hmac.new(cookie.encode(), qid.encode(), hashlib.sha256).hexdigest()
    if not q['dung']:
        db.execute('DELETE FROM ma WHERE nguoi=?', (u['id'],))
        db.execute('INSERT INTO ma VALUES(?,?,?,?)', (bam(ma), u['id'], p['khoa'], luc+600))
        db.execute('UPDATE quyen SET dung=1 WHERE id=?', (qid,))
    else:
        m = db.execute('SELECT 1 FROM ma WHERE bam=? AND han>?', (bam(ma), luc)).fetchone()
        if m is None:
            raise TuChoi('Mã đã dùng hoặc hết hạn — tạo yêu cầu mới')
    return {'ma': ma}


def thu_hoi(db, u, cookie, qid, target, rang, luc):
    _, q = can_r(db, u, cookie, qid, rang, luc)
    if q['dung']:
        return {'da_thu_hoi': True}
    try:
        kid = base64url_to_bytes(target)
    except Exception:
        raise TuChoi('Thiết bị không hợp lệ') from None
    ks = cac_khoa(db, u)
    if len(ks) <= 1:
        raise TuChoi('Không thể thu hồi passkey cuối cùng — khôi phục tại máy B')
    if kid not in [k['id'] for k in ks]:
        raise TuChoi('Thiết bị không hợp lệ')
    db.execute('UPDATE khoa SET thu=? WHERE id=?', (luc, kid))
    db.execute('DELETE FROM quyen WHERE phien IN (SELECT bam FROM phien WHERE khoa=?)', (kid,))
    db.execute('DELETE FROM hoi WHERE phien IN (SELECT bam FROM phien WHERE khoa=?)', (kid,))
    db.execute('DELETE FROM phien WHERE khoa=?', (kid,))
    db.execute('DELETE FROM ma WHERE nguon=?', (kid,))
    db.execute('UPDATE quyen SET dung=1 WHERE id=?', (qid,))
    db.execute('INSERT INTO tin(loai,luc) VALUES(?,?)', ('thu-hoi', luc))
    return {'da_thu_hoi': True}
```

### `tram/passkey/dich_vu.py`

```python
"""Một kết nối/giao dịch mỗi lời gọi; không giữ kết nối xuyên luồng."""
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from collections.abc import Callable
from webauthn.helpers import bytes_to_base64url
from tram.passkey import nghi_le, thiet_bi
from tram.passkey.kho import mo_kho, giao_dich, nguoi, cap_ma, cac_khoa, phien, TuChoi


@dataclass
class DichVu:
    path: Path
    login: str
    rp: str
    dong_ho: Callable = time.time

    @contextmanager
    def mo(self):
        with mo_kho(self.path) as db, giao_dich(db):
            yield db, nguoi(db, self.login), self.dong_ho()

    def cap_ma(self, khoi_phuc=False):
        with self.mo() as (db, u, luc):
            return cap_ma(db, u, luc, khoi_phuc)

    def bat_dau(self, loai, *, cookie='', rang='', ma=''):
        with self.mo() as (db, u, luc):
            return nghi_le.bat_dau(db, u, self.rp, luc, loai, cookie, rang, ma)

    def ket_thuc(self, cid, credential, ten='Thiết bị'):
        with self.mo() as (db, u, luc):
            return nghi_le.ket_thuc(db, u, self.rp, luc, cid, credential, ten)

    def can_phien(self, cookie):
        with self.mo() as (db, u, luc):
            return dict(phien(db, u, cookie, luc))

    def trang_thai(self, cookie):
        with self.mo() as (db, u, luc):
            try:
                con = max(0, int(phien(db, u, cookie, luc)['han']-luc))
            except TuChoi:
                con = 0
            return {'con_giay': con, 'cho_gui': db.execute('SELECT count(*) FROM tin WHERE gui=0').fetchone()[0],
                    'thiet_bi': [{'id': bytes_to_base64url(k['id']), 'ten': k['ten'], 'tao': k['tao'],
                                 'dung': k['dung']} for k in cac_khoa(db, u)]}

    def moi(self, cookie, quyen, *, rang):
        with self.mo() as (db, u, luc):
            return thiet_bi.moi(db, u, cookie, quyen, rang, luc)

    def thu_hoi(self, cookie, quyen, target, *, rang):
        with self.mo() as (db, u, luc):
            return thiet_bi.thu_hoi(db, u, cookie, quyen, target, rang, luc)
```

- [ ] **Step 4 — GREEN:**

```bash
UV_NO_SYNC=1 UV_CACHE_DIR=/tmp/passkey-uv-cache tests/chan_host/chay.sh -q tests/test_passkey_dich_vu.py
```

Chạy thêm tập tích hợp ở mục kiểm chứng cuối; không cộng các lượt lặp thành số test mới.

- [ ] **Step 5 — dừng ở cây làm việc, KHÔNG commit.** Người điều phối review diff và bằng chứng.

## Task 4: Cửa người và toàn bộ 23 tuyến HEAD

**Scenario:** Người/quyền; D143; N/P; trước đăng ký; cookie; cửa máy không bị buộc Touch ID.

**Files:**

- `tram/passkey/chinh_sach.py`
- `tram/api/passkey_phu_thuoc.py`
- `tram/api/passkey.py`
- `tram/api/bao_mat.py`
- `tram/api/dieu_phoi.py`
- `tram/api/app.py`
- `tests/test_passkey_api.py`
- `tests/test_passkey_cua.py`

**Interfaces:** dich_vu(Request) → DichVu theo cấu hình và login đã kiểm; can_phien_passkey(Request); can_ghi(Request); luon_cham_lai(Request) async. /api/passkey/trang-thai GET; /api/passkey/{viec} POST: bat-dau, ket-thuc, moi, thu-hoi. Yeu_cau_danh_tinh giữ hợp đồng cũ cho hook M.

- [ ] **Step 1 — áp test và helper test nguyên văn:**

### `tests/test_passkey_api.py`

```python
import pytest
from api_gia import tao_app_gia, DAI_CA, MAY_B, LOGIN
from asgi_gia import goi
from tram.passkey.chinh_sach import TUYEN, rang_buoc
from tram.passkey.dich_vu import DichVu
from passkey_gia import KhoaGia
from webauthn.helpers import base64url_to_bytes


def test_du_23_tuyen_head(tmp_path):
    app, _ = tao_app_gia(tmp_path, {})
    ds = {p for p, methods in app.openapi()['paths'].items() if 'post' in methods and '/passkey/' not in p}
    assert ds == set(TUYEN) and len(ds) == 23


@pytest.mark.parametrize('path,muc', list(TUYEN.items()))
def test_tuyen_ghi_truoc_dang_ky(tmp_path, path, muc):
    app, _ = tao_app_gia(tmp_path, {})
    path = path.replace('{du_an}', 'x').replace('{bead_id}', 'x').replace('{may_id}', 'x').replace('{ten}', 'x')
    r = goi(app, 'POST', path, json_body={}, headers=DAI_CA)
    if muc in ('N', 'P') and path not in ('/api/chu/estop', '/api/feature/yeu-cau/xem'):
        assert r.status == 403
    else:
        assert r.status != 200  # payload trống / máy thiếu token, không có side effect


def test_cookie_va_login_sai(tmp_path):
    app, _ = tao_app_gia(tmp_path, {})
    dv = DichVu(tmp_path/'pk.db', LOGIN, MAY_B)
    app.state.passkey_path = dv.path
    k = KhoaGia()
    def post(path, body, headers=DAI_CA):
        return goi(app, 'POST', '/api/passkey/'+path, json_body=body, headers=headers)
    o = post('bat-dau', {'loai':'dang-ky', 'ma':dv.cap_ma()}).json()
    a = k.tra(base64url_to_bytes(o['publicKey']['challenge']), dang_ky=True, rp=MAY_B, origin='https://'+MAY_B)
    assert post('ket-thuc', {'id':o['id'], 'credential':a, 'ten':'A'}).status == 200
    o = post('bat-dau', {'loai':'phien'}).json()
    a = k.tra(base64url_to_bytes(o['publicKey']['challenge']), rp=MAY_B, origin='https://'+MAY_B)
    r = post('ket-thuc', {'id':o['id'], 'credential':a})
    ck = r.headers['set-cookie']
    for flag in ('HttpOnly', 'Secure', 'SameSite=strict', 'Max-Age=28800', 'Path=/'):
        assert flag in ck
    assert 'Domain' not in ck and 'cookie' not in r.json()
    assert r.headers['cache-control'] == 'no-store'
    h = {**DAI_CA, 'Cookie':ck.split(';')[0]}
    assert goi(app,'GET','/api/passkey/trang-thai',headers=h).json()['con_giay'] > 0
    assert post('bat-dau',{'loai':'phien'}, {**h,'Tailscale-User-Login':'khac'}).status == 403
    assert post('bat-dau',{'loai':'phien'}, {**h,'Origin':'https://gia'}).status == 403
    assert post('bat-dau',{'loai':'phien'}, {**h,'Host':'gia'}).status == 421
    bad = post('ket-thuc', {'id': 'marker-secret', 'credential':{}})
    assert 'marker-secret' not in bad.body.decode()


def test_rang_buoc_khong_doi_payload():
    a = rang_buoc('/api/x', {'ma_thao_tac':'a','x':1})
    assert a == rang_buoc('/api/x', {'x':1,'ma_thao_tac':'a'})
    assert a != rang_buoc('/api/x', {'x':2,'ma_thao_tac':'a'})
    assert a != rang_buoc('/api/y', {'x':1,'ma_thao_tac':'a'})


def test_get_trinh_duyet_khong_co_origin(tmp_path):
    app, _ = tao_app_gia(tmp_path,{})
    r = goi(app,'GET','/api/passkey/trang-thai',headers={'Tailscale-User-Login':LOGIN})
    assert r.status == 200
    assert r.headers['cache-control'] == 'no-store'
```

### `tests/test_passkey_cua.py`

```python
import pytest
from types import SimpleNamespace
from fastapi import FastAPI, Depends, Request
from api_gia import tao_pt, DAI_CA, LOGIN, MAY_B
from asgi_gia import goi
from passkey_gia import KhoaGia
from webauthn.helpers import base64url_to_bytes
from tram.api.bao_mat import yeu_cau_ghi
from tram.passkey.chinh_sach import TUYEN
from tram.passkey.dich_vu import DichVu


@pytest.mark.parametrize('path,muc', [(p,m) for p,m in TUYEN.items() if m in ('N','P')])
def test_moi_tuyen_n_p_thieu_dung_het_phien(tmp_path,path,muc):
    app = FastAPI()
    app.state.pt = tao_pt(tmp_path,{})
    app.state.passkey_path = tmp_path/'pk.db'
    calls = []
    @app.post(path,dependencies=[Depends(yeu_cau_ghi)])
    def ghi():
        calls.append(1)
        return {'da_ghi':True}
    url = path.replace('{du_an}','x').replace('{bead_id}','x').replace('{may_id}','x').replace('{ten}','x')
    dv = DichVu(app.state.passkey_path,LOGIN,MAY_B)
    k = KhoaGia()
    o = dv.bat_dau('dang-ky',ma=dv.cap_ma())
    dv.ket_thuc(o['id'],k.tra(base64url_to_bytes(o['publicKey']['challenge']),
                             dang_ky=True,rp=MAY_B,origin='https://'+MAY_B))
    r = goi(app,'POST',url,headers=DAI_CA,json_body={})
    assert r.status == (403 if muc == 'P' else 200)
    assert len(calls) == (0 if muc == 'P' else 1)
    o = dv.bat_dau('phien')
    c = dv.ket_thuc(o['id'],k.tra(base64url_to_bytes(o['publicKey']['challenge']),
                                rp=MAY_B,origin='https://'+MAY_B))['cookie']
    hs = {**DAI_CA,'Cookie':'__Host-tram-phien='+c}
    assert goi(app,'POST',url,headers=hs,json_body={}).status == 200
    before = len(calls)
    for headers in ({}, {**hs,'Tailscale-User-Login':'gia'}, {**hs,'Origin':'https://gia'},
                    {**hs,'X-Tram':'0'}):
        assert goi(app,'POST',url,headers=headers,json_body={}).status == 403
    assert len(calls) == before
    from tram.passkey.kho import mo_kho,giao_dich
    with mo_kho(dv.path) as db,giao_dich(db):
        db.execute('UPDATE phien SET han=0')
    assert goi(app,'POST',url,headers=hs,json_body={}).status == (403 if muc == 'P' else 200)


def test_ghi_la_dong_mac_dinh(tmp_path):
    app=FastAPI(); app.state.pt=tao_pt(tmp_path,{})
    @app.post('/api/la',dependencies=[Depends(yeu_cau_ghi)])
    def ghi():
        pytest.fail('không chạy nghiệp vụ')
    assert goi(app,'POST','/api/la',headers=DAI_CA,json_body={}).status == 403
```

- [ ] **Step 2 — RED:**

```bash
UV_NO_SYNC=1 UV_CACHE_DIR=/tmp/passkey-uv-cache tests/chan_host/chay.sh -q tests/test_passkey_api.py tests/test_passkey_cua.py
```

**Bằng chứng đã chạy:** 27 passed ở API + 16 passed ở ma trận; RED: ModuleNotFoundError: tram.passkey.chinh_sach. Bổ sung GET không Origin: 1 failed (403 != 200) → GREEN. Inventory dùng app.openapi() vì FastAPI bản cài giữ router lồng; sửa bộ đọc test từ app.routes rỗng, không bỏ inventory.

- [ ] **Step 3 — áp mã nguyên văn:**

### `tram/passkey/chinh_sach.py`

```python
"""Danh mục đóng: route mới phải khai mức; TM/TC nối bằng phụ thuộc tường minh."""
import hashlib
import json

TUYEN = {
    '/api/bead/{du_an}/{bead_id}/cot': 'N',
    '/api/bead/{du_an}/{bead_id}/chot': 'P',
    '/api/bead/{du_an}/{bead_id}/thu-lai': 'N',
    '/api/phe-duyet/{du_an}/{bead_id}/duyet': 'P',
    '/api/phe-duyet/{du_an}/{bead_id}/tra-ve': 'N',
    '/api/phe-duyet/{du_an}/{bead_id}/tra-loi': 'P',
    '/api/chu/estop': 'N',
    '/api/chu/tiep-tuc': 'P',
    '/api/khe/{may_id}/{ten}/tat': 'N',
    '/api/khe/{may_id}/{ten}/bat': 'P',
    '/api/khe/{may_id}/{ten}/cau-dao-dong': 'P',
    '/api/nho/xoa': 'P',
    '/api/nho/ghi': 'N',
    '/api/feature/yeu-cau/xem': 'N',
    '/api/feature/yeu-cau': 'N',
    '/api/dieu-phoi/nhip': 'M',
    '/api/ghep-may': 'M',
    '/api/tho/dang-ky': 'M',
    '/api/tho/nhip': 'M',
    '/api/tho/bao': 'M',
    '/api/tho/su-kien': 'M',
    '/api/tho/da-push': 'M',
    '/api/tho/da-dong': 'M',
}


def rang_buoc(path, than):
    if not isinstance(than, dict) or not isinstance(than.get('ma_thao_tac'), str) or not than['ma_thao_tac']:
        raise ValueError('Thiếu mã thao tác')
    noi_dung = json.dumps(['POST', path, than], sort_keys=True, ensure_ascii=False, separators=(',', ':'))
    return hashlib.sha256(noi_dung.encode()).hexdigest()
```

### `tram/api/passkey_phu_thuoc.py`

```python
"""Cửa người TCP; danh tính mạng là điều kiện phụ, không phải bằng chứng chạm."""
from fastapi import HTTPException, Request
from tram.api.bao_mat import kiem_ghi, HEADER_DANH_TINH
from tram.duong_dan import tram_home
from tram.passkey.chinh_sach import TUYEN, rang_buoc
from tram.passkey.dich_vu import DichVu
from tram.passkey.kho import TuChoi
from tram.passkey.thiet_bi import can_r

COOKIE = '__Host-tram-phien'


def dich_vu(request: Request):
    ch = request.app.state.pt.cau_hinh
    hs = request.headers.getlist(HEADER_DANH_TINH)
    if len(hs) != 1 or len(ch.dai_ca_logins) != 1 or hs[0] != ch.dai_ca_logins[0]:
        raise HTTPException(403, 'Danh tính không hợp lệ')
    headers = dict(request.headers)
    if request.method == "GET":
        headers = {**headers, "origin": f"https://{ch.ten_may_b}", "x-tram": "1"}
    loi = kiem_ghi(headers, ch)
    if loi:
        raise HTTPException(403, loi)
    return DichVu(getattr(request.app.state, 'passkey_path', tram_home()/'passkey.db'), hs[0], ch.ten_may_b)


def cookie(request):
    return request.cookies.get(COOKIE, '')


def can_phien_passkey(request: Request):
    try:
        return dich_vu(request).can_phien(cookie(request))
    except TuChoi:
        raise HTTPException(403, 'Cần phiên passkey') from None


def can_ghi(request: Request):
    dv = dich_vu(request)
    path = request.scope['route'].path
    muc = TUYEN.get(path)
    if muc not in ('N', 'P'):
        raise HTTPException(403, 'Tuyến chưa được cấp quyền người')
    if path in ('/api/chu/estop', '/api/feature/yeu-cau/xem'):
        return
    try:
        if muc == 'P':
            dv.can_phien(cookie(request))
        elif not dv.trang_thai(cookie(request))['thiet_bi']:
            raise TuChoi('Cần đăng ký passkey')
    except TuChoi as e:
        raise HTTPException(403, str(e)) from None


async def luon_cham_lai(request: Request):
    """TM/TC: cùng mã/nội dung cho retry; ledger nghiệp vụ vẫn phải chống thực thi lần hai."""
    dv = dich_vu(request)
    try:
        rang = rang_buoc(request.url.path, await request.json())
        with dv.mo() as (db, u, luc):
            _, q = can_r(db, u, cookie(request), request.headers.get('x-tram-xac-nhan', ''), rang, luc)
            db.execute('UPDATE quyen SET dung=1 WHERE id=?', (q['id'],))
            return {'nguoi': u['id'].hex(), 'rang': rang, 'lap_lai': bool(q['dung'])}
    except (TuChoi, ValueError):
        raise HTTPException(403, 'Cần chạm lại cho thao tác này') from None
```

### `tram/api/passkey.py`

```python
"""Giao thức WebAuthn: không đưa lỗi schema/thư viện và dữ liệu ceremony ra log."""
import json
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from tram.api.passkey_phu_thuoc import COOKIE, cookie, dich_vu
from tram.passkey.chinh_sach import rang_buoc
from tram.passkey.kho import TuChoi

router = APIRouter()


async def than_kin(request):
    raw = b''
    async for chunk in request.stream():
        raw += chunk
        if len(raw) > 65536:
            raise HTTPException(413, 'Yêu cầu quá lớn')
    try:
        b = json.loads(raw)
        if not isinstance(b, dict):
            raise ValueError()
        return b
    except (ValueError, UnicodeError):
        raise HTTPException(422, 'Yêu cầu không hợp lệ') from None


def tra(b):
    r = JSONResponse({k:v for k,v in b.items() if k != 'cookie'}, headers={'Cache-Control':'no-store'})
    if 'cookie' in b:
        r.set_cookie(COOKIE, b['cookie'], max_age=28800, path='/', secure=True, httponly=True, samesite='strict')
    return r


@router.get('/api/passkey/trang-thai')
def trang_thai(request: Request):
    return tra(dich_vu(request).trang_thai(cookie(request)))


@router.post('/api/passkey/{viec}')
async def ghi(viec: str, request: Request):
    dv = dich_vu(request)
    b = await than_kin(request)
    try:
        if viec == 'bat-dau':
            loai = b['loai']
            rang = rang_buoc(b['duong'], b['than']) if loai == 'r' else ''
            out = dv.bat_dau(loai, cookie=cookie(request), ma=b.get('ma',''), rang=rang)
        elif viec == 'ket-thuc':
            out = dv.ket_thuc(b['id'], b['credential'], b.get('ten','Thiết bị'))
        elif viec in ('moi', 'thu-hoi'):
            than = b['than']
            rang = rang_buoc('/api/passkey/'+viec, than)
            if viec == 'moi':
                out = dv.moi(cookie(request), b['quyen'], rang=rang)
            else:
                out = dv.thu_hoi(cookie(request), b['quyen'], than['id'], rang=rang)
        else:
            raise HTTPException(404, 'Không có thao tác')
        return tra(out)
    except TuChoi as e:
        return JSONResponse({'loi':str(e)}, status_code=429 if str(e).startswith('Quá nhiều') else 403,
                            headers={'Cache-Control':'no-store'})
    except (KeyError, TypeError, ValueError, AttributeError):
        return JSONResponse({'loi':'Yêu cầu không hợp lệ'}, status_code=422, headers={'Cache-Control':'no-store'})
```

### `tram/api/bao_mat.py`

```diff
--- a/tram/api/bao_mat.py
+++ b/tram/api/bao_mat.py
@@ -40,7 +40,7 @@
     return {k.lower(): v for k, v in request.headers.items()}


-def yeu_cau_ghi(request: Request) -> None:
+def yeu_cau_danh_tinh(request: Request) -> None:
     if not kenh_hop_le(request):
         raise HTTPException(status_code=403, detail="API ghi chỉ nhận qua kênh đã xác thực (cach_ly.kenh_ghi)")
     if len(request.headers.getlist(HEADER_DANH_TINH)) > 1:
@@ -48,6 +48,11 @@
     loi = kiem_ghi(_header(request), request.app.state.pt.cau_hinh)
     if loi:
         raise HTTPException(status_code=403, detail=loi)
+
+
+def yeu_cau_ghi(request: Request) -> None:
+    from tram.api.passkey_phu_thuoc import can_ghi
+    can_ghi(request)


 def la_dai_ca_yeu_cau(request: Request) -> bool:
```

### `tram/api/dieu_phoi.py`

```diff
--- a/tram/api/dieu_phoi.py
+++ b/tram/api/dieu_phoi.py
@@ -2,7 +2,7 @@
 `dieu_phoi.nhip` của dự án `_tram`. ĐƯỜNG GHI HẸP: chỉ ghi đúng loại sự kiện này; không chạm beads, phiếu, khe, memory.

 Kiểm theo thứ tự, rẻ trước: kênh ghi (`cach_ly.kenh_ghi`, 403) → tần suất (429) → danh tính Tailscale + `X-Tram` +
-`Origin` (`yeu_cau_ghi` y hệt API ghi dashboard, 403) → mã điều phối (`Authorization: Bearer`, so sha256 với
+`Origin` (`yeu_cau_danh_tinh` y hệt API ghi dashboard, 403) → mã điều phối (`Authorization: Bearer`, so sha256 với
 `dieu_phoi_ma_sha256` — mã RIÊNG theo D24, không phải mã Đại ca; header Tailscale giả được từ TCP localhost, mã thì
 không; 401) → thân ≤ 512 byte (413) đúng lược đồ (422). Mã điều phối KHÔNG mở route nào khác: API ghi dashboard bỏ
 qua `Authorization`; memory service chỉ so với `ma_dai_ca_sha256`. Thông báo lỗi không chứa mã.
@@ -18,7 +18,7 @@
 from fastapi.concurrency import run_in_threadpool
 from pydantic import BaseModel, ConfigDict, Field, ValidationError

-from tram.api.bao_mat import yeu_cau_ghi
+from tram.api.bao_mat import yeu_cau_danh_tinh
 from tram.api.kenh_ghi import kenh_hop_le
 from tram.chu.ma_dieu_phoi import doc_bam
 from tram.suy.dieu_phoi import DU_AN_HE, LOAI, TAC_NHAN, can_ghi
@@ -104,7 +104,7 @@
         raise HTTPException(403, "API ghi chỉ nhận qua kênh đã xác thực (cach_ly.kenh_ghi)")
     if not gioi_han(request).cho_phep():
         raise HTTPException(429, "Quá nhiều nhịp — thử lại sau")
-    yeu_cau_ghi(request)
+    yeu_cau_danh_tinh(request)
     await run_in_threadpool(kiem_ma_dieu_phoi, request)
     than = await doc_than(request)
     return {"ghi": await run_in_threadpool(ghi_nhip, request.app.state.pt, than)}
```

### `tram/api/app.py`

```diff
--- a/tram/api/app.py
+++ b/tram/api/app.py
@@ -6,6 +6,7 @@
 from tram.api import doi_ngu, ghep, luong, noi_bo, tho, tho_them, tuyen_chu, tuyen_doc, tuyen_ghi, tuyen_nho, usage
 from tram.api import cai_dat, tong_quan, tuyen_yeu_cau, van_phong
 from tram.api.bao_mat import them_header_an_toan
+from tram.api.passkey import router as passkey_router
 from tram.api.phu_thuoc import PhuThuocApi
 from tram.api.tuyen_giao import router as tuyen_giao
 from tram.beads.bd import KhongThayBead, LoiBd
@@ -17,6 +18,7 @@
           LoiNhoKhach: 503}
 CAC_TUYEN = (tuyen_doc.router, tuyen_ghi.router, tuyen_chu.router, tuyen_nho.router, luong.router, tho.router,
              noi_bo.router, doi_ngu.router, usage.router, tho_them.router, ghep.router)
+CAC_TUYEN += (passkey_router,)
 CAC_TUYEN += (tuyen_giao,)                     # 4a-2: GET /api/giao-viec
 CAC_TUYEN += (van_phong.router,)               # 2c: GET /api/van-phong
 CAC_TUYEN += (cai_dat.router,)                 # 2f: GET /api/cai-dat, /api/san-sang (chỉ Đại ca)
```

- [ ] **Step 4 — GREEN:**

```bash
UV_NO_SYNC=1 UV_CACHE_DIR=/tmp/passkey-uv-cache tests/chan_host/chay.sh -q tests/test_passkey_api.py tests/test_passkey_cua.py
```

Chạy thêm tập tích hợp ở mục kiểm chứng cuối; không cộng các lượt lặp thành số test mới.

- [ ] **Step 5 — dừng ở cây làm việc, KHÔNG commit.** Người điều phối review diff và bằng chứng.

## Task 5: CLI bootstrap/khôi phục và tách quyền bật khe

**Scenario:** D141/D144 CLI; đăng ký khe không bật lại trái phép.

**Files:**

- `tram/chu/passkey.py`
- `tram/cli.py`
- `tram/phieu/khe.py`
- `tests/test_passkey_cli.py`
- `tests/test_passkey_khe.py`

**Interfaces:** tram chu passkey cap-ma / khoi-phuc: không tham số mã hoặc --yes; thuc_hien(dv,khoi_phuc,vao,ra,doi=select.select) tiêm TTY test. khe_dang_bat chỉ nhìn khe.bat/khe.tat.

- [ ] **Step 1 — áp test và helper test nguyên văn:**

### `tests/test_passkey_cli.py`

```python
import io
from types import SimpleNamespace
from tram.chu.passkey import thuc_hien
from tram.cli import tao_parser


class TTY(io.StringIO):
    def isatty(self):
        return True


def test_dong_y_va_khong_redirect():
    goi = []
    dv = SimpleNamespace(cap_ma=lambda **kw: goi.append(kw) or 'MA-BI-MAT')
    doi = lambda *a: ([1], [], [])
    for vao, ra, expected in [(TTY('khong\n'), TTY(), 1), (TTY('dong-y\n'), io.StringIO(), 1),
                              (io.StringIO('dong-y\n'), TTY(), 1), (TTY('dong-y\n'), TTY(), 0)]:
        assert thuc_hien(dv, True, vao, ra, doi=doi) == expected
        assert ('MA-BI-MAT' in ra.getvalue()) == (expected == 0)
    assert goi == [{'khoi_phuc': True}]


def test_parser_khong_nhan_ma_argv():
    import pytest
    p = tao_parser()
    for cmd in ('cap-ma','khoi-phuc'):
        assert p.parse_args(['chu','passkey',cmd]).viec_passkey == cmd
        with pytest.raises(SystemExit):
            p.parse_args(['chu','passkey',cmd,'--yes'])
    assert thuc_hien(None,False,TTY('dong-y\n'),TTY(),doi=lambda *a:([],[],[])) == 1
```

### `tests/test_passkey_khe.py`

```python
from datetime import datetime, timezone
from tram.phieu.kho import KhoPhieu
from tram.phieu.khe import dang_ky_khe, khe_dang_bat, bat_tat_khe


def test_dang_ky_khong_cap_quyen_bat(tmp_path):
    kho = KhoPhieu(tmp_path/'sk.db')
    luc = datetime.now(timezone.utc)
    k = {'ten':'k1','cli':'claude','ten_goi_nho':'Khe','vai_uu_tien':['code']}
    try:
        with kho.giao_dich():
            dang_ky_khe(kho,'B',[k],luc=luc)
        assert not khe_dang_bat(kho,'B/k1')
        with kho.giao_dich():
            bat_tat_khe(kho,'B/k1',bat=True,vi_sao='',tac_nhan='dai-ca',luc=luc)
        assert khe_dang_bat(kho,'B/k1')
        with kho.giao_dich():
            bat_tat_khe(kho,'B/k1',bat=False,vi_sao='',tac_nhan='dai-ca',luc=luc)
            dang_ky_khe(kho,'B',[{**k,'ten_goi_nho':'Mới'}],luc=luc)
        assert not khe_dang_bat(kho,'B/k1')
    finally:
        kho.close()
```

- [ ] **Step 2 — RED:**

```bash
UV_NO_SYNC=1 UV_CACHE_DIR=/tmp/passkey-uv-cache tests/chan_host/chay.sh -q tests/test_passkey_cli.py tests/test_passkey_khe.py
```

**Bằng chứng đã chạy:** 3 passed; RED: ModuleNotFoundError: tram.chu.passkey. Test khe mới yêu cầu False; fixture cho phép chạy phải ghi khe.bat rõ ràng ở task 11.

- [ ] **Step 3 — áp mã nguyên văn:**

### `tram/chu/passkey.py`

```python
"""CLI cứu hộ chỉ ở Terminal của chủ trạm; TTY không thay cách ly quyền OS."""
import select
import sys
from tram.cau_hinh.tram import nap_cau_hinh_tram
from tram.duong_dan import tram_home
from tram.passkey.dich_vu import DichVu


def thuc_hien(dv, khoi_phuc, vao, ra, *, doi=select.select):
    if not vao.isatty() or not ra.isatty():
        return 1
    ra.write('Sẽ thu hồi mọi passkey, phiên và mã cũ.\n' if khoi_phuc else 'Sẽ cấp mã mới, huỷ mã cũ.\n')
    ra.write('Gõ dong-y trong 120 giây: ')
    ra.flush()
    if not doi([vao], [], [], 120)[0] or vao.readline(32).strip() != 'dong-y':
        ra.write('Chưa đổi gì.\n')
        return 1
    ma = dv.cap_ma(khoi_phuc=khoi_phuc)
    ra.write('Mã đăng ký dùng một lần, hạn 10 phút:\n'+ma+'\n')
    ra.flush()
    return 0


def chay(args):
    try:
        ch = nap_cau_hinh_tram()
        if len(ch.dai_ca_logins) != 1 or not ch.ten_may_b:
            raise ValueError()
        dv = DichVu(tram_home()/'passkey.db', ch.dai_ca_logins[0], ch.ten_may_b)
        return thuc_hien(dv, args.viec_passkey == 'khoi-phuc', sys.stdin, sys.stdout)
    except Exception:
        print('Không hoàn tất. Kiểm trạng thái trước khi cấp mã lại.', file=sys.stderr)
        return 2


def them_lenh(chu):
    nhom = chu.add_parser('passkey', help='Mã đăng ký và khôi phục passkey tại máy B')
    sub = nhom.add_subparsers(dest='viec_passkey', required=True)
    for ten in ('cap-ma', 'khoi-phuc'):
        sub.add_parser(ten).set_defaults(ham=chay)
```

### `tram/cli.py`

```diff
--- a/tram/cli.py
+++ b/tram/cli.py
@@ -74,6 +74,8 @@
     q.set_defaults(ham=_quet)

     chu = sub.add_parser("chu", help="Lệnh trạm chủ").add_subparsers(dest="lenh_chu", required=True)
+    from tram.chu.passkey import them_lenh as them_passkey
+    them_passkey(chu)
     e = chu.add_parser("estop", help="Dừng khẩn cấp mọi lượt quét")
     e.add_argument("--ly-do", default="Đại ca bấm estop")
     e.set_defaults(ham=_estop)
```

### `tram/phieu/khe.py`

```diff
--- a/tram/phieu/khe.py
+++ b/tram/phieu/khe.py
@@ -6,7 +6,7 @@
 from tram.cau_hinh.tram import CauHinhThoTram
 from tram.phieu.kho import DU_AN_TRAM, KhoPhieu, chuoi_gio

-LOAI_BAT_TAT = ("khe.dang_ky", "khe.bat", "khe.tat")
+LOAI_BAT_TAT = ("khe.bat", "khe.tat")
 LOAI_KET_NOI = ("khe.ket_noi", "khe.mat_ket_noi")


@@ -33,13 +33,13 @@


 def khe_dang_bat(kho: KhoPhieu, khe_id: str) -> bool:
-    """Điều kiện 1: sự kiện mới nhất trong `khe.dang_ky|bat|tat` — `khe.tat` → tắt; hai loại kia → bật."""
+    """Điều kiện 1: chỉ sự kiện cấp quyền `khe.bat`; đăng ký thông tin không cấp quyền chạy."""
     x = su_kien_khe(kho, khe_id, LOAI_BAT_TAT)
-    return x is not None and x[1] != "khe.tat"
+    return x is not None and x[1] == "khe.bat"


 def dang_ky_khe(kho: KhoPhieu, may_id: str, khe: list[dict], *, luc: datetime) -> list[str]:
-    """Trong giao dịch. Ghi `khe.dang_ky` cho khe mới hoặc đổi thông tin (coi như bật). Trả các khe_id."""
+    """Trong giao dịch. Ghi `khe.dang_ky` cho khe mới hoặc đổi thông tin (không cấp quyền bật). Trả các khe_id."""
     ra = []
     for k in khe:
         khe_id = f"{may_id}/{k['ten']}"
```

- [ ] **Step 4 — GREEN:**

```bash
UV_NO_SYNC=1 UV_CACHE_DIR=/tmp/passkey-uv-cache tests/chan_host/chay.sh -q tests/test_passkey_cli.py tests/test_passkey_khe.py
```

Chạy thêm tập tích hợp ở mục kiểm chứng cuối; không cộng các lượt lặp thành số test mới.

- [ ] **Step 5 — dừng ở cây làm việc, KHÔNG commit.** Người điều phối review diff và bằng chứng.

## Task 6: Outbox thiết bị: đêm gom sáng, không mất tin

**Scenario:** Bí mật không vào báo tin; nhiều thay đổi; Telegram lỗi; D149 restart.

**Files:**

- `tram/bao_tin/passkey.py`
- `tram/bao_tin/vong.py`
- `tests/test_passkey_bao_tin.py`

**Interfaces:** gui_cho(path, gio_yen_lang, luc, gui) → số sự kiện đã đánh dấu gửi; NguCanhBaoTin.passkey_path nối production, None giữ test không dùng outbox. Không đổi thứ tự tham số bắt buộc.

- [ ] **Step 1 — áp test và helper test nguyên văn:**

### `tests/test_passkey_bao_tin.py`

```python
from datetime import datetime, timezone
from tram.passkey.kho import mo_kho, giao_dich, nguoi, cap_ma
from tram.bao_tin.passkey import gui_cho
from tram.bao_tin.telegram import LoiTelegram


def test_dem_gom_sang_retry_restart(tmp_path):
    p = tmp_path/'pk.db'
    with mo_kho(p) as db, giao_dich(db):
        for loai in ('them','thu-hoi','khoi-phuc'):
            db.execute('INSERT INTO tin(loai,luc) VALUES(?,?)',(loai,100))
    dem = datetime(2026,10,18,16,tzinfo=timezone.utc)  # 23h VN
    sang = datetime(2026,10,19,0,tzinfo=timezone.utc)  # 7h VN
    da_gui = []
    assert gui_cho(p,'23:00-07:00',dem,da_gui.append) == 0
    assert not da_gui
    def hong(t):
        raise LoiTelegram('marker-secret')
    assert gui_cho(p,'23:00-07:00',sang,hong) == 0
    assert gui_cho(p,'23:00-07:00',sang,da_gui.append) == 3
    assert len(da_gui) == 1
    for loai in ('Thêm thiết bị','Thu hồi thiết bị','Khôi phục thiết bị'):
        assert loai in da_gui[0]
    assert gui_cho(p,None,sang,da_gui.append) == 0
    assert 'marker-secret' not in da_gui[0]


def test_lan_dau_vong_bao_tin_van_doc_outbox(tmp_path):
    from types import SimpleNamespace
    from tram.bao_tin.vong import NguCanhBaoTin, mot_vong
    p = tmp_path/'pk.db'
    with mo_kho(p) as db, giao_dich(db):
        cap_ma(db,nguoi(db,'chu'),100,True)
    gui = []
    nc = NguCanhBaoTin(SimpleNamespace(id_moi_nhat=lambda:0),None,gui.append,tmp_path/'bao',passkey_path=p)
    mot_vong(nc)
    assert len(gui) == 1
```

- [ ] **Step 2 — RED:**

```bash
UV_NO_SYNC=1 UV_CACHE_DIR=/tmp/passkey-uv-cache tests/chan_host/chay.sh -q tests/test_passkey_bao_tin.py
```

**Bằng chứng đã chạy:** 2 passed; RED: ModuleNotFoundError: tram.bao_tin.passkey

- [ ] **Step 3 — áp mã nguyên văn:**

### `tram/bao_tin/passkey.py`

```python
"""D142/D149: hàng chờ bền riêng, giữ đủ ID và gom sau giờ yên lặng."""
from datetime import datetime, timezone
from tram.bao_tin.chong_on import trong_gio_yen_lang
from tram.bao_tin.telegram import LoiTelegram
from tram.passkey.kho import mo_kho, giao_dich

TEN = {'them':'Thêm thiết bị', 'thu-hoi':'Thu hồi thiết bị', 'khoi-phuc':'Khôi phục thiết bị'}


def gui_cho(path, gio_yen_lang, luc, gui):
    if path is None or not path.exists() or trong_gio_yen_lang(gio_yen_lang,luc):
        return 0
    with mo_kho(path) as db:
        ds = db.execute('SELECT id,loai,luc FROM tin WHERE gui=0 ORDER BY id LIMIT 20').fetchall()
    if not ds:
        return 0
    noi_dung = ['[tram] Thiết bị passkey:']
    for t in ds:
        gio = datetime.fromtimestamp(t['luc'],timezone.utc).isoformat(timespec='seconds')
        noi_dung.append(f"#{t['id']} · {TEN.get(t['loai'], 'Thay đổi thiết bị')} · {gio}")
    try:
        gui('\n'.join(noi_dung))  # dùng adapter Telegram hiện có, hạn 10 giây; không giữ khoá DB khi gửi
    except LoiTelegram:
        return 0
    with mo_kho(path) as db, giao_dich(db):
        db.executemany('UPDATE tin SET gui=1 WHERE id=?', [(t['id'],) for t in ds])
    return len(ds)  # crash sau gửi trước đánh dấu: có thể trùng cùng ID, không mất tin
```

### `tram/bao_tin/vong.py`

```diff
--- a/tram/bao_tin/vong.py
+++ b/tram/bao_tin/vong.py
@@ -26,6 +26,7 @@
     tao_bd: Callable[[str], object]
     gui: Callable[[str], None]
     thu_muc: Path
+    passkey_path: Path | None = None
     gio_yen_lang: str | None = None
     dashboard_url: str | None = None
     bay_gio: Callable[[], datetime] = _bay_gio_utc
@@ -42,6 +43,8 @@


 def mot_vong(nc: NguCanhBaoTin) -> int:
+    from tram.bao_tin.passkey import gui_cho
+    gui_cho(nc.passkey_path, nc.gio_yen_lang, nc.bay_gio(), nc.gui)
     p_moc = nc.thu_muc / "moc.json"
     moc = doc_json(p_moc, None)
     if moc is None:
@@ -99,4 +102,5 @@
         return None
     return NguCanhBaoTin(kho=mo_kho(), tao_bd=lambda ten: Bd(nap_du_an(ten).duong_dan),
                          gui=lambda vb: gui_telegram(token, ch.telegram.chat_id, vb), thu_muc=tram_home() / "bao-tin",
-                         gio_yen_lang=ch.telegram.gio_yen_lang, dashboard_url=ch.dashboard_url)
+                         gio_yen_lang=ch.telegram.gio_yen_lang, dashboard_url=ch.dashboard_url,
+                         passkey_path=tram_home() / 'passkey.db')
```

- [ ] **Step 4 — GREEN:**

```bash
UV_NO_SYNC=1 UV_CACHE_DIR=/tmp/passkey-uv-cache tests/chan_host/chay.sh -q tests/test_passkey_bao_tin.py
```

Chạy thêm tập tích hợp ở mục kiểm chứng cuối; không cộng các lượt lặp thành số test mới.

- [ ] **Step 5 — dừng ở cây làm việc, KHÔNG commit.** Người điều phối review diff và bằng chứng.

## Task 7: Bridge navigator.credentials và transport trong api.js

**Scenario:** Windows/USB/QR browser; huỷ; dữ liệu không vào storage/URL.

**Files:**

- `frontend/src/passkey.js`
- `frontend/tests/passkey.test.mjs`
- `frontend/src/api.js`

**Interfaces:** doc64/ghi64/tuyChon/phanHoi; nghiLe(loai,them,deps) → phản hồi; datHoi(fn); quanLy(viec,than); guiPasskey ở api.js, goiPasskey alias. Injection deps chỉ cho test node, browser luôn dùng navigator.credentials.

- [ ] **Step 1 — áp test và helper test nguyên văn:**

### `frontend/tests/passkey.test.mjs`

```javascript
import test from 'node:test'
import assert from 'node:assert/strict'
import { doc64, ghi64, tuyChon, phanHoi, hienPhien, nghiLe, datHoi } from '../src/passkey.js'

test('base64url và options chuyển đúng BufferSource, giữ UV', () => {
  const v = new Uint8Array([0, 127, 255])
  assert.deepEqual(new Uint8Array(doc64(ghi64(v))), v)
  const r = tuyChon({ challenge: ghi64(v), user: { id: ghi64(v) },
    allowCredentials: [{ id: ghi64(v) }], authenticatorSelection: { userVerification: 'required' } })
  assert.ok(r.challenge instanceof ArrayBuffer)
  assert.ok(r.user.id instanceof ArrayBuffer)
  assert.equal(r.authenticatorSelection.userVerification, 'required')
})
test('serialize cả assertion và registration, không private key', () => {
  const b = new Uint8Array([1, 2]).buffer
  const r = phanHoi({id:'AQI',rawId:b,type:'public-key',response:{clientDataJSON:b,signature:b,
    authenticatorData:b,userHandle:null}})
  assert.equal(r.response.signature,'AQI')
  assert.equal(r.response.userHandle,null)
  assert.equal(phanHoi({id:'AQI',rawId:b,type:'public-key',response:{clientDataJSON:b,
    attestationObject:b}}).response.attestationObject,'AQI')
})
test('thời gian từ server và trước đăng ký', () => {
  assert.equal(hienPhien({thiet_bi:[],con_giay:0}), 'Chưa có passkey')
  assert.equal(hienPhien({thiet_bi:[{}],con_giay:3600}), 'Đã xác nhận, còn 60 phút')
})
test('hủy trước ceremony không gọi fetch/authenticator', async () => {
  datHoi(async () => false)
  await assert.rejects(nghiLe('phien', {}, {goi: () => assert.fail('không gọi mạng')}), /huỷ/)
})
test('ceremony dùng API có sẵn, không tự ghi nghiệp vụ', async () => {
  datHoi(async () => true)
  const calls = []
  const b = new Uint8Array([1, 2]).buffer
  const goi = async (p, body) => {
    calls.push([p,body]); return calls.length === 1 ? {id:'hoi',publicKey:{challenge:'AQI'}} : {han:100}
  }
  const credentials = {get: async o => {
    assert.ok(o.publicKey.challenge instanceof ArrayBuffer)
    return {id:'AQI',rawId:b,type:'public-key',response:{clientDataJSON:b,signature:b,authenticatorData:b}}
  }}
  assert.deepEqual(await nghiLe('phien',{}, {goi,credentials}),{han:100})
  assert.equal(calls.length,2)
})
```

- [ ] **Step 2 — RED:**

```bash
cd frontend && node --test tests/passkey.test.mjs
```

**Bằng chứng đã chạy:** 5 node passed; RED: ERR_MODULE_NOT_FOUND frontend/src/passkey.js

- [ ] **Step 3 — áp mã nguyên văn:**

### `frontend/src/passkey.js`

```javascript
import { guiPasskey } from './api.js'
// Không ghi mã, cookie hay ceremony vào storage, URL hoặc console.
let hoi = async () => { throw new Error('Chưa mở được hộp xác nhận') }
export function datHoi(fn) { hoi = fn }
export function doc64(s) {
  return Uint8Array.from(atob(s.replace(/-/g, '+').replace(/_/g, '/')), c => c.charCodeAt(0)).buffer
}
export function ghi64(b) {
  return btoa(String.fromCharCode(...new Uint8Array(b))).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')
}
export function tuyChon(o) {
  const r = { ...o, challenge: doc64(o.challenge) }
  if (o.user) r.user = { ...o.user, id: doc64(o.user.id) }
  for (const k of ['allowCredentials', 'excludeCredentials']) {
    if (o[k]) r[k] = o[k].map(c => ({ ...c, id: doc64(c.id) }))
  }
  return r
}
export function phanHoi(c) {
  const response = {}
  for (const k of ['clientDataJSON', 'attestationObject', 'authenticatorData', 'signature', 'userHandle']) {
    if (c.response[k] !== undefined) response[k] = c.response[k] === null ? null : ghi64(c.response[k])
  }
  return { id: c.id, rawId: ghi64(c.rawId), type: c.type, response }
}
export const goiPasskey = guiPasskey
export async function nghiLe(loai, them = {}, deps = {}) {
  if (!await hoi({ loai, duong: them.duong, than: them.than })) throw new Error('Đã huỷ xác nhận')
  const goi = deps.goi || goiPasskey
  const credentials = deps.credentials || globalThis.navigator?.credentials
  if (!credentials) throw new Error('Trình duyệt chưa hỗ trợ passkey; dùng browser hoặc thiết bị khác')
  const o = await goi('bat-dau', { loai, ...them })
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), 120000)
  try {
    const method = loai === 'dang-ky' ? 'create' : 'get'
    const c = await credentials[method]({ publicKey: tuyChon(o.publicKey), signal: controller.signal })
    if (!c) throw new Error('Đã huỷ')
    return await goi('ket-thuc', { id: o.id, credential: phanHoi(c), ten: them.ten })
  } catch {
    throw new Error('Chưa xác nhận — thử lại. Đại ca có thể chọn thiết bị khác trong hộp trình duyệt.')
  } finally { clearTimeout(timer) }
}
export async function quanLy(viec, than) {
  const tt = await goiPasskey('trang-thai')
  if (!tt.con_giay) await nghiLe('phien')
  const { quyen } = await nghiLe('r', { duong: '/api/passkey/' + viec, than })
  return goiPasskey(viec, { than, quyen })
}
export function hienPhien(tt) {
  if (!tt?.thiet_bi.length) return 'Chưa có passkey'
  return tt.con_giay > 0 ? `Đã xác nhận, còn ${Math.ceil(tt.con_giay / 60)} phút` : 'Cần xác nhận passkey'
}
```

### `frontend/src/api.js`

```diff
--- a/frontend/src/api.js
+++ b/frontend/src/api.js
@@ -33,3 +33,17 @@
     body: JSON.stringify(than),
   }))
 }
+
+export async function guiPasskey(path, body) {
+  const controller = new AbortController()
+  const timer = setTimeout(() => controller.abort(), 15000)
+  try {
+    const r = await fetch('/api/passkey/' + path, { method: body ? 'POST' : 'GET',
+      credentials: 'same-origin', cache: 'no-store', signal: controller.signal,
+      headers: { 'Content-Type': 'application/json', 'X-Tram': '1' },
+      body: body ? JSON.stringify(body) : undefined })
+    const b = await r.json()
+    if (!r.ok) throw new Error(b.loi || b.detail || 'Chưa xác nhận — thử lại')
+    return b
+  } finally { clearTimeout(timer) }
+}
```

- [ ] **Step 4 — GREEN:**

```bash
cd frontend && node --test tests/passkey.test.mjs
```

Chạy thêm tập tích hợp ở mục kiểm chứng cuối; không cộng các lượt lặp thành số test mới.

- [ ] **Step 5 — dừng ở cây làm việc, KHÔNG commit.** Người điều phối review diff và bằng chứng.

## Task 8: Trang thiết bị và modal theo D150

**Scenario:** Đăng ký lần đầu; thiết bị; thu hồi; cửa sổ xác nhận; còn thời gian phiên.

**Files:**

- `frontend/src/api.js`
- `frontend/src/tuyen.js`
- `frontend/src/KhungChinh.vue`
- `frontend/src/thanh/ThanhBen.vue`
- `frontend/src/thanh/ThanhTren.vue`
- `frontend/src/thanh/HopPasskey.vue`
- `frontend/src/thanh/ChipPasskey.vue`
- `frontend/src/trang/ThietBi.vue`
- `frontend/tests/passkey-noi.test.mjs`

**Interfaces:** ThietBi.vue ở /tai-khoan/thiet-bi; HopPasskey cài datHoi và dùng dialog; ChipPasskey đọc thời gian server. ghi() chỉ đăng nhập rồi thử lại đúng request khi nhận 403 Cần phiên passkey; không retry lỗi khác.

- [ ] **Step 1 — áp test và helper test nguyên văn:**

### `frontend/tests/passkey-noi.test.mjs`

```javascript
import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { ghi } from '../src/api.js'
import { datHoi } from '../src/passkey.js'

test('ghi P chỉ xin xác nhận khi cửa phiên từ chối, huỷ không retry', async () => {
  const old = globalThis.fetch
  let calls = 0
  globalThis.fetch = async () => { calls++; return {ok:false,status:403,
    json: async () => ({detail:'Cần phiên passkey'})} }
  datHoi(async () => false)
  try { await assert.rejects(ghi('/api/chu/tiep-tuc',{ma_thao_tac:'m'}), /huỷ/); assert.equal(calls,1) }
  finally { globalThis.fetch = old }
})
test('thiết bị đi từ thẻ chủ và chip, không thêm menu chính', () => {
  const read = p => readFileSync(new URL('../src/'+p, import.meta.url),'utf8')
  assert.match(read('tuyen.js'), /tai-khoan\/thiet-bi/)
  assert.match(read('thanh/ThanhBen.vue'), /tai-khoan\/thiet-bi/)
  assert.match(read('thanh/ThanhTren.vue'), /ChipPasskey/)
  assert.match(read('KhungChinh.vue'), /HopPasskey/)
  assert.match(read('trang/ThietBi.vue'), /tram chu passkey khoi-phuc/)
  assert.match(read('trang/ThietBi.vue'), /length <= 1/)
})
```

- [ ] **Step 2 — RED:**

```bash
cd frontend && node --test tests/passkey-noi.test.mjs
```

**Bằng chứng đã chạy:** 2 node mới passed; npm run kiem tại bước này: 109 passed. RED: không khớp /huỷ/ (vẫn lỗi Cần phiên passkey), chưa có route thiết bị. Build/kiem-dist xanh.

- [ ] **Step 3 — áp mã nguyên văn:**

### `frontend/src/api.js`

```diff
--- a/frontend/src/api.js
+++ b/frontend/src/api.js
@@ -27,11 +27,17 @@
 }

 export async function ghi(duongDan, than) {
-  return xuLy(await fetch(duongDan, {
+  const gui = async () => xuLy(await fetch(duongDan, {
     method: 'POST',
     headers: { 'Content-Type': 'application/json', 'X-Tram': '1' },
     body: JSON.stringify(than),
   }))
+  try { return await gui() } catch (e) {
+    if (e.status !== 403 || e.message !== 'Cần phiên passkey') throw e
+    const { nghiLe } = await import('./passkey.js')
+    await nghiLe('phien')
+    return gui()
+  }
 }

 export async function guiPasskey(path, body) {
```

### `frontend/src/tuyen.js`

```diff
--- a/frontend/src/tuyen.js
+++ b/frontend/src/tuyen.js
@@ -19,5 +19,6 @@
   { path: '/usage', component: Usage },
   { path: '/phe-duyet', component: PheDuyet },
   { path: '/cai-dat', component: CaiDat },
+  { path: '/tai-khoan/thiet-bi', component: () => import('./trang/ThietBi.vue') },
   { path: '/:khac(.*)*', redirect: '/tong-quan' },
 ]
```

### `frontend/src/KhungChinh.vue`

```diff
--- a/frontend/src/KhungChinh.vue
+++ b/frontend/src/KhungChinh.vue
@@ -5,6 +5,7 @@
 import { kho, moLuong, taiSoPheDuyet, taiTrangThai, theoDoiTab } from './kho.js'
 import { tieuDeTab } from './luat.js'
 import { tenTrang } from './menu.js'
+import HopPasskey from './thanh/HopPasskey.vue'
 import BangEstop from './thanh/BangEstop.vue'
 import ThanhBen from './thanh/ThanhBen.vue'
 import ThanhTren from './thanh/ThanhTren.vue'
@@ -19,6 +20,7 @@
 </script>

 <template>
+  <HopPasskey />
   <ThanhBen />
   <div class="khung">
     <ThanhTren :estop="estop" />
```

### `frontend/src/thanh/ThanhBen.vue`

```diff
--- a/frontend/src/thanh/ThanhBen.vue
+++ b/frontend/src/thanh/ThanhBen.vue
@@ -29,11 +29,11 @@
       <div class="may-tram mono">
         <span class="cham xanh" />{{ cucBo ? 'Máy trạm cục bộ' : 'Máy trạm' }}<b>{{ may }}</b>
       </div>
-      <div class="nguoi-dung">
+      <router-link class="nguoi-dung" to="/tai-khoan/thiet-bi">
         <div class="avatar" :class="{ 'chi-doc': !laDaiCa }" aria-hidden="true">{{ laDaiCa ? 'ĐC' : '?' }}</div>
         <div v-if="laDaiCa"><strong>Đại ca</strong><span class="mono">Chủ trạm</span></div>
         <div v-else><strong>Chỉ đọc</strong><span>không có danh tính Đại ca</span></div>
-      </div>
+      </router-link>
     </div>
   </aside>
 </template>
```

### `frontend/src/thanh/ThanhTren.vue`

```diff
--- a/frontend/src/thanh/ThanhTren.vue
+++ b/frontend/src/thanh/ThanhTren.vue
@@ -3,6 +3,7 @@
 import { gioPhut } from '../dinh_dang.js'
 import { kho } from '../kho.js'
 import BieuTuong from './BieuTuong.vue'
+import ChipPasskey from './ChipPasskey.vue'
 import OTim from './OTim.vue'

 // Thanh trên (mockup index.html `.thanh-tren`): ô tìm ⌘K, viên đồng bộ (quét cuối mới nhất của mọi dự án; mất luồng
@@ -20,6 +21,7 @@
   <header class="thanh-tren">
     <OTim />
     <div class="tt-phai">
+      <ChipPasskey v-if="tt?.la_dai_ca" />
       <span class="vien-tt mono" role="status">
         <span class="cham" :class="kho.matKetNoi ? 'do' : 'xanh'" />
         {{ kho.matKetNoi ? 'Mất kết nối · đang thử lại' : `Đồng bộ · quét cuối ${quetCuoi}` }}</span>
```

### `frontend/src/thanh/HopPasskey.vue`

```vue
<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { datHoi } from '../passkey.js'
const hop = ref(null), yeuCau = ref(null)
let traLoi = null, nutCu = null
function dong(ok) {
  hop.value?.close()
  const tra = traLoi; traLoi = null; yeuCau.value = null
  nutCu?.focus(); tra?.(ok)
}
onMounted(() => datHoi(async yc => {
  if (traLoi) return false
  nutCu = document.activeElement
  yeuCau.value = yc
  const ket = new Promise(resolve => { traLoi = resolve })
  await nextTick(); hop.value.showModal()
  return ket
}))
onUnmounted(() => { dong(false); datHoi(async () => false) })
</script>
<template>
  <dialog ref="hop" class="pk-hop the" aria-labelledby="pk-tieu-de" @cancel.prevent="dong(false)">
    <h2 id="pk-tieu-de">Chạm Touch ID để xác nhận</h2>
    <p v-if="yeuCau?.loai === 'r'">Thao tác này luôn cần chạm lại, kể cả khi phiên còn hạn.</p>
    <p v-else-if="yeuCau?.loai === 'dang-ky'">Tạo passkey cho Đại ca trên thiết bị này.</p>
    <p v-else>Cho phép thao tác nguy hiểm trên trình duyệt này trong 8 giờ.</p>
    <div v-if="yeuCau?.loai === 'r'" class="pk-tom-tat">
      {{ yeuCau.duong.endsWith('/thu-hoi') ? 'Thu hồi thiết bị đã chọn và các phiên của nó.' :
         yeuCau.duong.endsWith('/moi') ? 'Cấp mã một lần để thêm thiết bị.' : 'Xác nhận thay đổi vừa chọn.' }}
    </div>
    <p>Trên Windows: dùng Windows Hello hoặc khoá USB có xác minh người dùng.</p>
    <p>Để dùng điện thoại, chọn “Thiết bị khác” trong hộp của trình duyệt rồi quét QR ở đó.</p>
    <div class="hang-nut">
      <button class="nut" autofocus @click="dong(false)">Huỷ</button>
      <button class="nut chinh" @click="dong(true)">Tiếp tục xác nhận</button>
    </div>
  </dialog>
</template>
<style scoped>
.pk-hop { max-width: 620px; padding: 30px; border: 1px solid var(--vien); border-radius: 16px; }
.pk-hop::backdrop { background: color-mix(in srgb, var(--chu) 40%, transparent); }
.pk-tom-tat { padding: 14px; background: var(--nen-3); border-radius: 8px; }
.hang-nut { display: flex; justify-content: end; gap: 10px; margin-top: 20px; }
</style>
```

### `frontend/src/thanh/ChipPasskey.vue`

```vue
<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { goiPasskey, hienPhien } from '../passkey.js'
const tt = ref(null), loi = ref(false)
let timer
async function tai() {
  try { tt.value = await goiPasskey('trang-thai'); loi.value = false }
  catch { tt.value = null; loi.value = true }
}
onMounted(() => { tai(); timer = setInterval(tai, 60000); window.addEventListener('focus', tai) })
onUnmounted(() => { clearInterval(timer); window.removeEventListener('focus', tai) })
</script>
<template>
  <router-link class="vien-tt" to="/tai-khoan/thiet-bi" role="status">
    {{ loi ? 'Chưa đọc được phiên' : hienPhien(tt) }}
  </router-link>
</template>
```

### `frontend/src/trang/ThietBi.vue`

```vue
<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { goiPasskey, nghiLe, quanLy, hienPhien } from '../passkey.js'
const tt = ref(null), ma = ref(''), ten = ref(''), moi = ref(''), loi = ref(''), ban = ref(false)
let hanMa
const gio = t => t ? new Date(t * 1000).toLocaleString('vi-VN', { timeZone: 'Asia/Ho_Chi_Minh' }) : 'Chưa dùng'
async function tai() { tt.value = await goiPasskey('trang-thai') }
async function lam(fn) {
  if (ban.value) return
  ban.value = true; loi.value = ''
  try { await fn(); await tai() } catch (e) { loi.value = e.message }
  finally { ban.value = false }
}
async function dangKy() {
  const code = ma.value; ma.value = ''
  await lam(() => nghiLe('dang-ky', { ma: code, ten: ten.value }))
}
async function them() {
  await lam(async () => {
    moi.value = ''
    const r = await quanLy('moi', { ma_thao_tac: crypto.randomUUID() })
    moi.value = r.ma
    clearTimeout(hanMa); hanMa = setTimeout(() => { moi.value = '' }, 600000)
  })
}
async function thu(k) {
  await lam(() => quanLy('thu-hoi', { id: k.id, ma_thao_tac: crypto.randomUUID() }))
}
onMounted(() => lam(async () => {}))
onUnmounted(() => { ma.value = ''; moi.value = ''; clearTimeout(hanMa) })
</script>
<template>
  <div class="dau-trang"><div><div class="duong-dan">Đại ca / Thiết bị đã đăng ký</div>
    <h1>Thiết bị</h1><p>Cửa ghi dashboard bằng passkey</p></div></div>
  <p v-if="loi" role="alert" class="loi-chung">{{ loi }}</p>
  <section class="the pk-bao">
    <strong>{{ hienPhien(tt) }}</strong>
    <p v-if="tt && !tt.thiet_bi.length">Chưa có passkey: chỉ TẠM DỪNG và Estop. Đăng ký bên dưới để mở cửa ghi.</p>
    <p>Thêm hoặc thu hồi luôn cần chạm lại. Tin ban đêm được gom gửi buổi sáng.</p>
    <p v-if="tt?.cho_gui">Cảnh báo đang chờ gửi: {{ tt.cho_gui }}</p>
    <button v-if="tt?.thiet_bi.length && !tt.con_giay" class="nut" :disabled="ban"
      @click="lam(() => nghiLe('phien'))">Xác nhận phiên 8 giờ</button>
  </section>
  <section v-if="tt?.thiet_bi.length" class="the">
    <div class="pk-hang"><h2>Thiết bị đã đăng ký <span class="chip">{{ tt.thiet_bi.length }}</span></h2>
      <button class="nut chinh" :disabled="ban" @click="them">Thêm thiết bị</button></div>
    <div class="bang-cuon"><table class="bang"><thead><tr><th>Tên gợi nhớ</th><th>Đăng ký</th>
      <th>Dùng gần nhất</th><th>Thao tác</th></tr></thead><tbody>
      <tr v-for="k in tt.thiet_bi" :key="k.id"><td>{{ k.ten }}</td><td>{{ gio(k.tao) }}</td><td>{{ gio(k.dung) }}</td>
        <td><button class="nut nguy" :disabled="ban || tt.thiet_bi.length <= 1" @click="thu(k)">Thu hồi</button></td>
      </tr></tbody></table></div>
    <p>Một passkey đồng bộ có thể dùng trên nhiều máy; thu hồi sẽ mất quyền trên mọi bản sao cùng passkey.</p>
    <p v-if="tt.thiet_bi.length <= 1">Không thể thu hồi passkey cuối ở đây; dùng khôi phục trên máy B.</p>
  </section>
  <section v-if="moi" class="the pk-bao" aria-live="polite"><h2>Mã mời thiết bị</h2>
    <code class="pk-lenh">{{ moi }}</code><p>Dùng một lần, hết hạn 10 phút. Nhập ở trang Thiết bị trên máy mới.</p>
    <p>Không gửi vào chat, chụp ảnh hay lưu mã. QR xác thực bằng điện thoại do trình duyệt cung cấp.</p>
    <button class="nut" @click="moi = ''">Ẩn mã</button></section>
  <div class="pk-luoi">
    <section class="the"><span class="pk-buoc">BƯỚC 1 · TẠI MÁY B</span><h2>Lấy mã đăng ký</h2>
      <p>Đại ca mở Terminal trên máy B, chạy lệnh rồi làm theo hướng dẫn.</p>
      <code class="pk-lenh">tram chu passkey cap-ma</code><p>Mã dùng một lần, hết hạn 10 phút.</p></section>
    <form class="the" @submit.prevent="dangKy"><span class="pk-buoc">BƯỚC 2 · TRÊN THIẾT BỊ NÀY</span>
      <h2>Đăng ký cho Đại ca</h2><p>Thiết bị cần dùng đúng tài khoản Tailscale của Đại ca.</p>
      <label class="pk-truong">Mã từ máy B hoặc thiết bị cũ<input v-model="ma" type="password"
        autocomplete="off" required :disabled="ban"></label>
      <label class="pk-truong">Tên gợi nhớ<input v-model="ten" maxlength="80" required :disabled="ban"></label>
      <button class="nut chinh" :disabled="ban">Tạo passkey</button></form>
  </div>
  <section class="the"><h2>Mất hết thiết bị hoặc nghi bị lộ?</h2>
    <p>Đại ca mở Terminal trên máy B. Gõ dong-y sẽ thu hồi mọi passkey, phiên, mã cũ.</p>
    <code class="pk-lenh">tram chu passkey khoi-phuc</code></section>
</template>
<style scoped>
.the { padding: 26px; margin-bottom: 18px; }
.pk-luoi { display: grid; grid-template-columns: 1fr 1.1fr; gap: 18px; }
.pk-truong { display: flex; flex-direction: column; gap: 7px; margin: 16px 0; }
.pk-truong input { padding: 12px; border: 1px solid var(--vien); border-radius: 8px; font: inherit; }
.pk-lenh { display: block; padding: 14px; background: var(--nen-lenh); color: var(--chu-lenh); border-radius: 8px; overflow-wrap: anywhere; }
.pk-hang { display: flex; justify-content: space-between; gap: 16px; align-items: center; }
.pk-bao { background: var(--nen-canh-bao); }
.bang-cuon { overflow-x: auto; }
@media (max-width: 1100px) { .pk-luoi { grid-template-columns: 1fr; } }
</style>
```

- [ ] **Step 4 — GREEN:**

```bash
cd frontend && node --test tests/passkey-noi.test.mjs
```

Chạy thêm tập tích hợp ở mục kiểm chứng cuối; không cộng các lượt lặp thành số test mới.

- [ ] **Step 5 — dừng ở cây làm việc, KHÔNG commit.** Người điều phối review diff và bằng chứng.

## Task 9: Ràng buộc mã/nội dung và no-store cho cả lỗi

**Scenario:** Idempotency; cùng mã khác payload 409; không cache mã/phiên.

**Files:**

- `tram/passkey/luoc_do.py`
- `tram/api/bao_mat.py`
- `tram/api/passkey_phu_thuoc.py`
- `tram/passkey/thao_tac.py`
- `tests/test_passkey_rang.py`

**Interfaces:** rang_ma(db,u,path,than) chỉ lưu băm. yeu_cau_ghi chuyển async để rang_yeu_cau đọc body. API feature giữ ledger SoNhan/digest/envelope hiện có; không bọc lỗi 409 của nó bằng schema khác. luon_cham_lai chỉ xác minh proof R; consumer phải giữ ledger như mục ghép.

- [ ] **Step 1 — áp test và helper test nguyên văn:**

### `tests/test_passkey_rang.py`

```python
import pytest
from fastapi import FastAPI, Depends
from api_gia import tao_pt, DAI_CA, LOGIN, MAY_B
from asgi_gia import goi
from tram.api.bao_mat import yeu_cau_ghi
from tram.passkey.dich_vu import DichVu
from passkey_gia import KhoaGia
from webauthn.helpers import base64url_to_bytes


def test_cung_ma_khac_payload_409(tmp_path):
    app = FastAPI(); app.state.pt = tao_pt(tmp_path,{})
    app.state.passkey_path = tmp_path/'pk.db'
    calls = []
    @app.post('/api/nho/ghi',dependencies=[Depends(yeu_cau_ghi)])
    def ghi():
        calls.append(1)
        return {'ok':True}
    dv = DichVu(app.state.passkey_path, LOGIN, MAY_B)
    k = KhoaGia(); o = dv.bat_dau('dang-ky',ma=dv.cap_ma())
    dv.ket_thuc(o['id'],k.tra(base64url_to_bytes(o['publicKey']['challenge']),
                             dang_ky=True,rp=MAY_B,origin='https://'+MAY_B))
    body = {'ma_thao_tac':'m','noi_dung':'mot'}
    assert goi(app,'POST','/api/nho/ghi',headers=DAI_CA,json_body=body).status == 200
    assert goi(app,'POST','/api/nho/ghi',headers=DAI_CA,json_body={**body,'noi_dung':'hai'}).status == 409
    assert len(calls) == 1


def test_loi_xac_thuc_khong_cache(tmp_path):
    from api_gia import tao_app_gia
    app,_ = tao_app_gia(tmp_path,{})
    r = goi(app,'POST','/api/passkey/bat-dau',json_body={'ma':'marker'})
    assert r.status == 403 and r.headers['cache-control'] == 'no-store'
```

- [ ] **Step 2 — RED:**

```bash
UV_NO_SYNC=1 UV_CACHE_DIR=/tmp/passkey-uv-cache tests/chan_host/chay.sh -q tests/test_passkey_rang.py
```

**Bằng chứng đã chạy:** 2 passed; RED thật: cùng mã khác payload trả 200, và KeyError: cache-control ở phản hồi 403.

- [ ] **Step 3 — áp mã nguyên văn:**

### `tram/passkey/luoc_do.py`

```diff
--- a/tram/passkey/luoc_do.py
+++ b/tram/passkey/luoc_do.py
@@ -11,5 +11,6 @@
     'CREATE TABLE quyen(id TEXT PRIMARY KEY, nguoi BLOB NOT NULL, phien TEXT NOT NULL, '
     'rang TEXT NOT NULL, han REAL NOT NULL, dung INT NOT NULL DEFAULT 0)',
     'CREATE TABLE tin(id INTEGER PRIMARY KEY, loai TEXT NOT NULL, luc REAL NOT NULL, gui INT NOT NULL DEFAULT 0)',
+    'CREATE TABLE thao_tac(ma TEXT PRIMARY KEY, nguoi BLOB NOT NULL, bam TEXT NOT NULL)',
     'CREATE TABLE sai(nguoi BLOB PRIMARY KEY, dem INT NOT NULL, han REAL NOT NULL)',
 )}
```

### `tram/api/bao_mat.py`

```diff
--- a/tram/api/bao_mat.py
+++ b/tram/api/bao_mat.py
@@ -50,9 +50,10 @@
         raise HTTPException(status_code=403, detail=loi)


-def yeu_cau_ghi(request: Request) -> None:
-    from tram.api.passkey_phu_thuoc import can_ghi
+async def yeu_cau_ghi(request: Request) -> None:
+    from tram.api.passkey_phu_thuoc import can_ghi, rang_yeu_cau
     can_ghi(request)
+    await rang_yeu_cau(request)


 def la_dai_ca_yeu_cau(request: Request) -> bool:
@@ -83,7 +84,11 @@
         async def gui(m):
             nonlocal da_gui
             if m["type"] == "http.response.start":
-                da_gui, m = True, {**m, "headers": [*m.get("headers", []), *HEADER_AN_TOAN]}
+                hs = [*m.get("headers", []), *HEADER_AN_TOAN]
+                if scope["path"].startswith("/api/passkey/") or scope["path"] == "/":
+                    hs = [(k, v) for k, v in hs if k.lower() != b"cache-control"]
+                    hs.append((b"cache-control", b"no-store"))
+                da_gui, m = True, {**m, "headers": hs}
             await send(m)

         host = dict(scope["headers"]).get(b"host", b"").decode("latin-1").lower()
```

### `tram/api/passkey_phu_thuoc.py`

```diff
--- a/tram/api/passkey_phu_thuoc.py
+++ b/tram/api/passkey_phu_thuoc.py
@@ -59,7 +59,28 @@
         rang = rang_buoc(request.url.path, await request.json())
         with dv.mo() as (db, u, luc):
             _, q = can_r(db, u, cookie(request), request.headers.get('x-tram-xac-nhan', ''), rang, luc)
-            db.execute('UPDATE quyen SET dung=1 WHERE id=?', (q['id'],))
             return {'nguoi': u['id'].hex(), 'rang': rang, 'lap_lai': bool(q['dung'])}
     except (TuChoi, ValueError):
         raise HTTPException(403, 'Cần chạm lại cho thao tác này') from None
+
+
+async def rang_yeu_cau(request: Request):
+    import json
+    from tram.passkey.thao_tac import rang_ma, XungDotMa
+    if request.scope['route'].path in ('/api/feature/yeu-cau/xem', '/api/feature/yeu-cau'):
+        return
+    raw = await request.body()
+    if len(raw) > 65536:
+        raise HTTPException(413, 'Yêu cầu quá lớn')
+    try:
+        than = json.loads(raw)
+        if not isinstance(than, dict):
+            raise ValueError()
+        with dich_vu(request).mo() as (db, u, _):
+            rang_ma(db, u, request.url.path, than)
+    except XungDotMa:
+        raise HTTPException(409, 'Mã thao tác đã dùng cho nội dung khác') from None
+    except TuChoi:
+        raise HTTPException(403, 'Không có quyền') from None
+    except ValueError:
+        raise HTTPException(422, 'Yêu cầu không hợp lệ') from None
```

### `tram/passkey/thao_tac.py`

```python
"""Buộc mã thao tác với người + tuyến + payload; kết quả vẫn do ledger nghiệp vụ giữ."""
import hashlib
import json
from tram.passkey.kho import TuChoi


class XungDotMa(ValueError):
    pass


def rang_ma(db, u, path, than):
    ma = than.get('ma_thao_tac') or than.get('ma_yeu_cau')
    if not ma:  # schema nghiệp vụ sẽ báo thiếu mã; riêng POST đọc không cần mã
        return
    if not isinstance(ma,str) or len(ma) > 128:
        raise ValueError('Mã thao tác không hợp lệ')
    digest = hashlib.sha256(json.dumps([path,than],sort_keys=True,ensure_ascii=False,
                                      separators=(',',':')).encode()).hexdigest()
    cu = db.execute('SELECT * FROM thao_tac WHERE ma=?',(ma,)).fetchone()
    if cu:
        if cu['nguoi'] != u['id']:
            raise TuChoi('Không có quyền')
        if cu['bam'] != digest:
            raise XungDotMa('Mã thao tác đã dùng cho nội dung khác')
    else:
        db.execute('INSERT INTO thao_tac VALUES(?,?,?)',(ma,u['id'],digest))
```

- [ ] **Step 4 — GREEN:**

```bash
UV_NO_SYNC=1 UV_CACHE_DIR=/tmp/passkey-uv-cache tests/chan_host/chay.sh -q tests/test_passkey_rang.py
```

Chạy thêm tập tích hợp ở mục kiểm chứng cuối; không cộng các lượt lặp thành số test mới.

- [ ] **Step 5 — dừng ở cây làm việc, KHÔNG commit.** Người điều phối review diff và bằng chứng.

## Task 10: Khoá UI trước đăng ký, giữ đường dừng

**Scenario:** Chưa có passkey chỉ dừng; N không cần phiên sau đăng ký.

**Files:**

- `frontend/src/trang/DoiNgu.vue`
- `frontend/src/trang/NganBen.vue`
- `frontend/src/trang/PheDuyet.vue`
- `frontend/src/trang/CongViec.vue`
- `frontend/src/trang/KyUc.vue`
- `frontend/src/trang/ThietBi.vue`
- `frontend/src/thanh/TheBead.vue`
- `frontend/src/thanh/ThanhTren.vue`
- `frontend/src/thanh/ChipPasskey.vue`
- `frontend/src/KhungChinh.vue`
- `frontend/src/quyen_passkey.js`
- `frontend/tests/passkey-quyen.test.mjs`

**Interfaces:** quyenPasskey.tt, capNhat(tt), duocGhi(trangThai): danh tính + đã có credential. Các component ghi dùng hàm này; thanh Estop vẫn cho bật dừng, khoá Tiếp tục khi chưa đăng ký. Không biến hết phiên thành khoá N.

- [ ] **Step 1 — áp test và helper test nguyên văn:**

### `frontend/tests/passkey-quyen.test.mjs`

```javascript
import test from 'node:test'
import assert from 'node:assert/strict'
import { quyenPasskey, duocGhi, capNhat } from '../src/quyen_passkey.js'

test('chưa có passkey khóa ghi, lỗi đọc cũng khóa, hết phiên vẫn cho N', () => {
  capNhat(null)
  assert.equal(duocGhi({la_dai_ca:true}), false)
  capNhat({thiet_bi:[],con_giay:0})
  assert.equal(duocGhi({la_dai_ca:true}), false)
  capNhat({thiet_bi:[{}],con_giay:0})
  assert.equal(duocGhi({la_dai_ca:true}), true)
  assert.equal(duocGhi({la_dai_ca:false}), false)
  assert.equal(duocGhi(null), false)
  capNhat(null)
})
```

- [ ] **Step 2 — RED:**

```bash
cd frontend && node --test tests/passkey-quyen.test.mjs
```

**Bằng chứng đã chạy:** 1 node mới passed; npm run kiem: 110 passed. RED: ERR_MODULE_NOT_FOUND quyen_passkey.js.

- [ ] **Step 3 — áp mã nguyên văn:**

### `frontend/src/trang/DoiNgu.vue`

```diff
--- a/frontend/src/trang/DoiNgu.vue
+++ b/frontend/src/trang/DoiNgu.vue
@@ -2,6 +2,7 @@
 import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
 import '../kieu/doi-ngu.css'
 import { doc } from '../api.js'
+import { duocGhi } from '../quyen_passkey.js'
 import { kho } from '../kho.js'
 import { SO_NGAY_BANG_DIEM, dinhDangSo, duongDanDoiNgu, oTiLe } from '../luat_doi_ngu.js'
 import DauTrang from '../thanh/DauTrang.vue'
@@ -16,7 +17,7 @@
 const duAn = ref('')                      // D14: bảng điểm lọc theo dự án + số ngày; mặc định mọi dự án, 30 ngày
 const soNgay = ref(30)
 const dsDuAn = ref([])
-const laDaiCa = computed(() => Boolean(kho.trangThai && kho.trangThai.la_dai_ca))
+const laDaiCa = computed(() => duocGhi(kho.trangThai))
 let hen = null

 async function tai() {
```

### `frontend/src/trang/NganBen.vue`

```diff
--- a/frontend/src/trang/NganBen.vue
+++ b/frontend/src/trang/NganBen.vue
@@ -3,6 +3,7 @@
 // Bàn giao, Bộ giao việc giữ bố cục cũ, chỉ áp lớp mới (D36). Dự án chỉ quét thử: khoá nút ghi (D37).
 import { computed, ref, watch } from 'vue'
 import { doc, ghi, thanGhi } from '../api.js'
+import { duocGhi } from '../quyen_passkey.js'
 import { kho } from '../kho.js'
 import { CHU_CHI_QUET_THU, gioVN, laLinkAnToan } from '../luat.js'
 import { chipCot, uuTien, viTriThe } from '../luat_cong_viec.js'
@@ -16,7 +17,7 @@
 const ct = ref(null)
 const loi = ref('')
 const duongDan = () => `${encodeURIComponent(props.the.du_an)}/${encodeURIComponent(props.the.id)}`
-const laDaiCa = computed(() => Boolean(kho.trangThai && kho.trangThai.la_dai_ca))
+const laDaiCa = computed(() => duocGhi(kho.trangThai))
 const cauHoi = computed(() => (ct.value && ct.value.cham_gan_nhat ? ct.value.cham_gan_nhat.cau_hoi : []))

 async function tai() {
```

### `frontend/src/trang/PheDuyet.vue`

```diff
--- a/frontend/src/trang/PheDuyet.vue
+++ b/frontend/src/trang/PheDuyet.vue
@@ -1,6 +1,7 @@
 <script setup>
 import { computed, onMounted, ref, watch } from 'vue'
 import { doc } from '../api.js'
+import { duocGhi } from '../quyen_passkey.js'
 import { kho, taiSoPheDuyet } from '../kho.js'
 import { TEN_PHE_DUYET, duAnChiQuetThu, nhomPheDuyet } from '../luat.js'
 import { khoaMuc } from '../luat_doi_ngu.js'
@@ -22,7 +23,7 @@
 const loiDoc = ref({})
 const chiQuetThu = ref(new Set())          // dự án `bat_ghi: false` (D37)
 const nhom = computed(() => nhomPheDuyet(ds.value))
-const laDaiCa = computed(() => Boolean(kho.trangThai && kho.trangThai.la_dai_ca))
+const laDaiCa = computed(() => duocGhi(kho.trangThai))
 const khoaCua = (m) => khoaThaoTac(laDaiCa.value, chiQuetThu.value.has(m.du_an))

 async function tai() {
```

### `frontend/src/trang/CongViec.vue`

```diff
--- a/frontend/src/trang/CongViec.vue
+++ b/frontend/src/trang/CongViec.vue
@@ -5,6 +5,7 @@
 import { useRoute } from 'vue-router'
 import { doc, ghi, thanGhi } from '../api.js'
 import { ganGiaoViec } from '../giao_viec.js'
+import { duocGhi } from '../quyen_passkey.js'
 import { kho } from '../kho.js'
 import { TEN_HANG, choPhepKeo, duAnChiQuetThu, nhomTheoHang } from '../luat.js'
 import { COT, MO_TA_TRANG, dongKhe } from '../luat_cong_viec.js'
@@ -27,7 +28,7 @@
 const chon = ref(null)
 const nhom = computed(() => nhomTheoHang(dsThe.value))
 const chiQuetThu = computed(() => duAnChiQuetThu(dsDuAn.value))     // D37: bat_ghi false → chỉ quét thử
-const laDaiCa = computed(() => Boolean(kho.trangThai?.la_dai_ca))
+const laDaiCa = computed(() => duocGhi(kho.trangThai))
 const rong = computed(() => `Không có bead${duAn.value ? ` của ${duAn.value}` : ''}`)
 const tenChon = (d) => `${d.ten}${d.bat_ghi === false ? ' (chỉ quét thử)' : ''}`
 const thuocTinh = (t) => ({ the: t, khe: dongKhe(t, dsKhe.value), chiQuetThu: chiQuetThu.value.has(t.du_an) })
```

### `frontend/src/trang/KyUc.vue`

```diff
--- a/frontend/src/trang/KyUc.vue
+++ b/frontend/src/trang/KyUc.vue
@@ -1,6 +1,7 @@
 <script setup>
 import { computed, onMounted, ref, watch } from 'vue'
 import { doc } from '../api.js'
+import { duocGhi } from '../quyen_passkey.js'
 import { kho } from '../kho.js'
 import { locKyUc, tongPhamVi } from '../nho.js'
 import BieuTuong from '../thanh/BieuTuong.vue'
@@ -22,7 +23,7 @@
 const bao = ref('')
 const chan = ref(0)                // 403 | 503 → thẻ chặn thay cả lưới
 const loi = ref('')
-const laDaiCa = computed(() => Boolean(kho.trangThai && kho.trangThai.la_dai_ca))
+const laDaiCa = computed(() => duocGhi(kho.trangThai))
 const duAn = computed(() => (kho.trangThai ? kho.trangThai.du_an.map((d) => d.ten) : []))
 const hien = computed(() => locKyUc(ds.value, tim.value))
 const tatCa = computed(() => tongPhamVi(cacPhamVi.value))
```

### `frontend/src/trang/ThietBi.vue`

```diff
--- a/frontend/src/trang/ThietBi.vue
+++ b/frontend/src/trang/ThietBi.vue
@@ -1,10 +1,11 @@
 <script setup>
 import { ref, onMounted, onUnmounted } from 'vue'
+import { capNhat } from '../quyen_passkey.js'
 import { goiPasskey, nghiLe, quanLy, hienPhien } from '../passkey.js'
 const tt = ref(null), ma = ref(''), ten = ref(''), moi = ref(''), loi = ref(''), ban = ref(false)
 let hanMa
 const gio = t => t ? new Date(t * 1000).toLocaleString('vi-VN', { timeZone: 'Asia/Ho_Chi_Minh' }) : 'Chưa dùng'
-async function tai() { tt.value = await goiPasskey('trang-thai') }
+async function tai() { tt.value = await goiPasskey('trang-thai'); capNhat(tt.value) }
 async function lam(fn) {
   if (ban.value) return
   ban.value = true; loi.value = ''
```

### `frontend/src/thanh/TheBead.vue`

```diff
--- a/frontend/src/thanh/TheBead.vue
+++ b/frontend/src/thanh/TheBead.vue
@@ -2,6 +2,7 @@
 // Thẻ bead (mockup trang.js theBead, anh-cong-viec.png); chip của bản cũ giữ theo khảo sát §1.3 + D37.
 import { computed } from 'vue'
 import { chipThe, uuTien } from '../luat_cong_viec.js'
+import { duocGhi } from '../quyen_passkey.js'
 import { kho } from '../kho.js'

 const props = defineProps({
@@ -11,7 +12,7 @@
 })
 const emit = defineEmits(['mo', 'keo'])
 const chip = computed(() => chipThe(props.the, props.chiQuetThu))
-const keoDuoc = computed(() => props.the.keo_duoc && !props.chiQuetThu && Boolean(kho.trangThai?.la_dai_ca))
+const keoDuoc = computed(() => props.the.keo_duoc && !props.chiQuetThu && duocGhi(kho.trangThai))

 function batDauKeo(e) {
   if (!keoDuoc.value) { e.preventDefault(); return }
```

### `frontend/src/thanh/ThanhTren.vue`

```diff
--- a/frontend/src/thanh/ThanhTren.vue
+++ b/frontend/src/thanh/ThanhTren.vue
@@ -1,6 +1,7 @@
 <script setup>
 import { computed } from 'vue'
 import { gioPhut } from '../dinh_dang.js'
+import { duocGhi } from '../quyen_passkey.js'
 import { kho } from '../kho.js'
 import BieuTuong from './BieuTuong.vue'
 import ChipPasskey from './ChipPasskey.vue'
@@ -14,7 +15,7 @@
   const ds = (tt.value ? tt.value.du_an : []).map((d) => d.quet_cuoi).filter(Boolean).sort()
   return ds.length ? gioPhut(ds[ds.length - 1]) : 'chưa quét'
 })
-const khoa = computed(() => !tt.value || !tt.value.la_dai_ca || props.estop.dangGui.value)
+const khoa = computed(() => !tt.value || !tt.value.la_dai_ca || (tt.value.estop && !duocGhi(tt.value)) || props.estop.dangGui.value)
 </script>

 <template>
```

### `frontend/src/thanh/ChipPasskey.vue`

```diff
--- a/frontend/src/thanh/ChipPasskey.vue
+++ b/frontend/src/thanh/ChipPasskey.vue
@@ -1,10 +1,12 @@
 <script setup>
 import { ref, onMounted, onUnmounted } from 'vue'
+import { capNhat } from '../quyen_passkey.js'
 import { goiPasskey, hienPhien } from '../passkey.js'
 const tt = ref(null), loi = ref(false)
 let timer
 async function tai() {
-  try { tt.value = await goiPasskey('trang-thai'); loi.value = false }
+  capNhat(null)
+  try { tt.value = await goiPasskey('trang-thai'); loi.value = false; capNhat(tt.value) }
   catch { tt.value = null; loi.value = true }
 }
 onMounted(() => { tai(); timer = setInterval(tai, 60000); window.addEventListener('focus', tai) })
```

### `frontend/src/KhungChinh.vue`

```diff
--- a/frontend/src/KhungChinh.vue
+++ b/frontend/src/KhungChinh.vue
@@ -1,6 +1,7 @@
 <script setup>
 import { computed, onMounted, watch } from 'vue'
 import { useRoute } from 'vue-router'
+import { duocGhi, quyenPasskey } from './quyen_passkey.js'
 import { dungEstop } from './estop.js'
 import { kho, moLuong, taiSoPheDuyet, taiTrangThai, theoDoiTab } from './kho.js'
 import { tieuDeTab } from './luat.js'
@@ -13,7 +14,7 @@
 // Khung mockup (index.html): sidebar | thanh trên + băng estop + trang. Tiêu đề tab "<trang> · Ben Station".
 const route = useRoute()
 const estop = dungEstop()
-const khoa = computed(() => !(kho.trangThai && kho.trangThai.la_dai_ca) || estop.dangGui.value)
+const khoa = computed(() => !duocGhi(kho.trangThai) || estop.dangGui.value)
 onMounted(() => { taiTrangThai(); taiSoPheDuyet(); moLuong(); theoDoiTab() })
 watch([() => route.path, () => kho.soPheDuyet],
   () => { document.title = tieuDeTab(kho.soPheDuyet, tenTrang(route.path)) }, { immediate: true })
@@ -27,6 +28,10 @@
     <BangEstop v-if="kho.trangThai && kho.trangThai.estop" :khoa="khoa" @tiep-tuc="estop.bam(false)" />
     <p v-if="estop.thongBao.value" class="loi-chung" role="alert">{{ estop.thongBao.value }}</p>
     <p v-if="kho.loi" class="loi-chung" role="alert">{{ kho.loi }}</p>
+    <p v-if="kho.trangThai?.la_dai_ca && !quyenPasskey.tt?.thiet_bi.length" class="loi-chung" role="status">
+      Chưa có passkey hoặc chưa đọc được trạng thái: chỉ TẠM DỪNG và Estop.
+      <router-link to="/tai-khoan/thiet-bi">Đăng ký thiết bị</router-link>
+    </p>
     <main class="trang"><router-view /></main>
   </div>
 </template>
```

### `frontend/src/quyen_passkey.js`

```javascript
import { reactive } from 'vue'
export const quyenPasskey = reactive({ tt: null })
export function capNhat(tt) { quyenPasskey.tt = tt }
export function duocGhi(trangThai) {
  return Boolean(trangThai?.la_dai_ca && quyenPasskey.tt?.thiet_bi.length)
}
```

- [ ] **Step 4 — GREEN:**

```bash
cd frontend && node --test tests/passkey-quyen.test.mjs
```

Chạy thêm tập tích hợp ở mục kiểm chứng cuối; không cộng các lượt lặp thành số test mới.

- [ ] **Step 5 — dừng ở cây làm việc, KHÔNG commit.** Người điều phối review diff và bằng chứng.

## Task 11: Chuyển tiền điều kiện test nghiệp vụ sang quyền thật

**Scenario:** Giữ luật nghiệp vụ và cửa máy khi đổi xác thực.

**Files:**

- `tests/api_gia.py`
- `tests/asgi_gia.py`
- `tests/test_api_doi_ngu.py`
- `tests/test_api_ghi.py`
- `tests/test_api_nho.py`
- `tests/passkey_phien_gia.py`
- `tests/test_passkey_api.py`
- `tests/test_passkey_rang.py`
- `tests/tho_api_gia.py`
- `tests/test_api_van_phong.py`
- `tests/test_api_yeu_cau_tu_choi.py`
- `tests/giao_viec_gia.py`
- `tests/test_khe_cau_dao.py`
- `tests/test_trang_thai_khe.py`
- `tests/test_nhip_tim.py`
- `tests/test_cap_phieu.py`
- `tests/test_truong_2f.py`
- `tests/test_suy_doi_ngu.py`
- `tests/test_suy_nhan_vat.py`
- `tests/khe_duyet_gia.py`

**Interfaces:** dang_nhap_app(app,path) đăng ký/assertion thật của fixture, cookie_test chỉ ở tests/asgi_gia.py như cookie jar browser. tao_app_gia(co_passkey=False) dành test cửa trống. dang_ky_va_duyet chỉ dùng fixture nghiệp vụ đã có chấp thuận chủ; test cửa máy vẫn gọi hàm sản phẩm trực tiếp.

- [ ] **Step 1 — áp test và helper test nguyên văn:**

### `tests/api_gia.py`

```diff
--- a/tests/api_gia.py
+++ b/tests/api_gia.py
@@ -27,6 +27,10 @@
     )


-def tao_app_gia(tmp_path: Path, bds: dict[str, BdGia], **kw):
+def tao_app_gia(tmp_path: Path, bds: dict[str, BdGia], *, co_passkey=True, **kw):
     pt = tao_pt(tmp_path, bds, **kw)
-    return tao_app(pt), pt
+    app = tao_app(pt)
+    if co_passkey:
+        from passkey_phien_gia import dang_nhap_app
+        dang_nhap_app(app, tmp_path / "pk-test.db")
+    return app, pt
```

### `tests/asgi_gia.py`

```diff
--- a/tests/asgi_gia.py
+++ b/tests/asgi_gia.py
@@ -18,6 +18,8 @@
     path, _, query = duong_dan.partition("?")
     body = b"" if json_body is None else _json.dumps(json_body, ensure_ascii=False).encode()
     hdr = {"host": "127.0.0.1:7700"}
+    if (ck := getattr(getattr(app, "state", None), "cookie_test", None)):
+        hdr["cookie"] = ck
     if json_body is not None:
         hdr["content-type"] = "application/json"
     hdr.update({k.lower(): v for k, v in (headers or {}).items()})
```

### `tests/test_api_doi_ngu.py`

```diff
--- a/tests/test_api_doi_ngu.py
+++ b/tests/test_api_doi_ngu.py
@@ -25,7 +25,8 @@
     kho.close()
     pt = replace(tao_pt(tmp_path, {}), mo_kho_phieu=(lambda: KhoPhieu(db)) if kho_phieu else None,
                  dong_ho=lambda: LUC, **kw)
-    return tao_app(pt)
+    from passkey_phien_gia import dang_nhap_app
+    return dang_nhap_app(tao_app(pt), tmp_path / "pk-test.db")


 def _than(**kw):
```

### `tests/test_api_ghi.py`

```diff
--- a/tests/test_api_ghi.py
+++ b/tests/test_api_ghi.py
@@ -42,13 +42,13 @@
     app, _, _ = _app(tmp_path, bead("hr-1", labels=["cot:ai-lam"]),
                      bead("hr-2", labels=["cot:cho-review", "cho-duyet-spec"]))
     cot = "/api/bead/hr/hr-1/cot"
-    r = goi(app, "POST", cot, json_body=_than(cot="can-chot", expected_version="2026-10-12T00:00:00Z"), headers=DAI_CA)
+    r = goi(app, "POST", cot, json_body=_than(ma_thao_tac="loi-api-001", cot="can-chot", expected_version="2026-10-12T00:00:00Z"), headers=DAI_CA)
     assert r.status == 409 and "đã đổi" in r.json()["loi"]
-    assert goi(app, "POST", cot, json_body=_than(cot="cho-review"), headers=DAI_CA).status == 422
-    assert goi(app, "POST", cot, json_body=_than(cot="can-chot", la="x"), headers=DAI_CA).status == 422
-    assert goi(app, "POST", "/api/bead/khong/hr-1/cot", json_body=_than(cot="can-chot"), headers=DAI_CA).status == 404
-    assert goi(app, "POST", "/api/bead/hr/hr-99/cot", json_body=_than(cot="can-chot"), headers=DAI_CA).status == 404
-    assert goi(app, "POST", "/api/phe-duyet/hr/hr-2/duyet", json_body=_than(), headers=DAI_CA).status == 422
+    assert goi(app, "POST", cot, json_body=_than(ma_thao_tac="loi-api-002", cot="cho-review"), headers=DAI_CA).status == 422
+    assert goi(app, "POST", cot, json_body=_than(ma_thao_tac="loi-api-003", cot="can-chot", la="x"), headers=DAI_CA).status == 422
+    assert goi(app, "POST", "/api/bead/khong/hr-1/cot", json_body=_than(ma_thao_tac="loi-api-004", cot="can-chot"), headers=DAI_CA).status == 404
+    assert goi(app, "POST", "/api/bead/hr/hr-99/cot", json_body=_than(ma_thao_tac="loi-api-005", cot="can-chot"), headers=DAI_CA).status == 404
+    assert goi(app, "POST", "/api/phe-duyet/hr/hr-2/duyet", json_body=_than(ma_thao_tac="loi-api-cuoi"), headers=DAI_CA).status == 422


 def test_chot_tra_ve_tra_loi_thu_lai(tmp_path):
```

### `tests/test_api_nho.py`

```diff
--- a/tests/test_api_nho.py
+++ b/tests/test_api_nho.py
@@ -76,7 +76,7 @@
 def test_ghi_kiem_du_an_gui_ma_va_bao_ly_do_tu_choi(tmp_path):
     kq = {"id": "m-g", "pham_vi": "/chung", "xoa": [], "lap_lai": False}
     app, pt = _app(tmp_path, **{"/ghi": kq})
-    r = goi(app, "POST", "/api/nho/ghi", json_body=_than(noi_dung="x", pham_vi="/du-an/khac/cach-lam"), headers=DAI_CA)
+    r = goi(app, "POST", "/api/nho/ghi", json_body=_than(noi_dung="x", pham_vi="/du-an/khac/cach-lam", ma_thao_tac="ma-nho-la-01"), headers=DAI_CA)
     assert r.status == 404 and pt.nho.goi_ == []
     r = goi(app, "POST", "/api/nho/ghi", json_body=_than(noi_dung="Chạy test", pham_vi="/chung", nhan=["test"]),
             headers=DAI_CA)
```

### `tests/passkey_phien_gia.py`

```python
"""Cookie jar của client test nghiệp vụ: đăng ký + assertion thật, không override cửa bảo mật."""
from passkey_gia import KhoaGia
from tram.passkey.dich_vu import DichVu
from webauthn.helpers import base64url_to_bytes


def dang_nhap_app(app, path):
    ch = app.state.pt.cau_hinh
    app.state.passkey_path = path
    dv = DichVu(path,ch.dai_ca_logins[0],ch.ten_may_b)
    k = KhoaGia()
    o = dv.bat_dau('dang-ky',ma=dv.cap_ma())
    dv.ket_thuc(o['id'],k.tra(base64url_to_bytes(o['publicKey']['challenge']),dang_ky=True,
                             rp=ch.ten_may_b,origin='https://'+ch.ten_may_b))
    o = dv.bat_dau('phien')
    c = dv.ket_thuc(o['id'],k.tra(base64url_to_bytes(o['publicKey']['challenge']),
                                rp=ch.ten_may_b,origin='https://'+ch.ten_may_b))['cookie']
    app.state.cookie_test = '__Host-tram-phien='+c
    return app
```

### `tests/test_passkey_api.py`

```diff
--- a/tests/test_passkey_api.py
+++ b/tests/test_passkey_api.py
@@ -8,14 +8,14 @@


 def test_du_23_tuyen_head(tmp_path):
-    app, _ = tao_app_gia(tmp_path, {})
+    app, _ = tao_app_gia(tmp_path, {}, co_passkey=False)
     ds = {p for p, methods in app.openapi()['paths'].items() if 'post' in methods and '/passkey/' not in p}
     assert ds == set(TUYEN) and len(ds) == 23


 @pytest.mark.parametrize('path,muc', list(TUYEN.items()))
 def test_tuyen_ghi_truoc_dang_ky(tmp_path, path, muc):
-    app, _ = tao_app_gia(tmp_path, {})
+    app, _ = tao_app_gia(tmp_path, {}, co_passkey=False)
     path = path.replace('{du_an}', 'x').replace('{bead_id}', 'x').replace('{may_id}', 'x').replace('{ten}', 'x')
     r = goi(app, 'POST', path, json_body={}, headers=DAI_CA)
     if muc in ('N', 'P') and path not in ('/api/chu/estop', '/api/feature/yeu-cau/xem'):
@@ -25,7 +25,7 @@


 def test_cookie_va_login_sai(tmp_path):
-    app, _ = tao_app_gia(tmp_path, {})
+    app, _ = tao_app_gia(tmp_path, {}, co_passkey=False)
     dv = DichVu(tmp_path/'pk.db', LOGIN, MAY_B)
     app.state.passkey_path = dv.path
     k = KhoaGia()
@@ -59,7 +59,7 @@


 def test_get_trinh_duyet_khong_co_origin(tmp_path):
-    app, _ = tao_app_gia(tmp_path,{})
+    app, _ = tao_app_gia(tmp_path,{}, co_passkey=False)
     r = goi(app,'GET','/api/passkey/trang-thai',headers={'Tailscale-User-Login':LOGIN})
     assert r.status == 200
     assert r.headers['cache-control'] == 'no-store'
```

### `tests/test_passkey_rang.py`

```diff
--- a/tests/test_passkey_rang.py
+++ b/tests/test_passkey_rang.py
@@ -28,6 +28,6 @@

 def test_loi_xac_thuc_khong_cache(tmp_path):
     from api_gia import tao_app_gia
-    app,_ = tao_app_gia(tmp_path,{})
+    app,_ = tao_app_gia(tmp_path,{}, co_passkey=False)
     r = goi(app,'POST','/api/passkey/bat-dau',json_body={'ma':'marker'})
     assert r.status == 403 and r.headers['cache-control'] == 'no-store'
```

### `tests/tho_api_gia.py`

```diff
--- a/tests/tho_api_gia.py
+++ b/tests/tho_api_gia.py
@@ -41,4 +41,11 @@
     t = TramGia(tao_app(pt), pt, token, gio)
     if dang_ky:
         assert t.goi("POST", "/api/tho/dang-ky", json_body={"may_id": "B", "khe": KHE}).status == 200
+        from tram.phieu.khe import bat_tat_khe
+        from contextlib import closing
+        with closing(t.kho()) as kho:
+            with kho.giao_dich():
+                for k in KHE:
+                    bat_tat_khe(kho, 'B/'+k['ten'], bat=True, vi_sao='fixture đã được chủ duyệt',
+                                tac_nhan='dai-ca', luc=BAT_DAU)
     return t
```

### `tests/test_api_van_phong.py`

```diff
--- a/tests/test_api_van_phong.py
+++ b/tests/test_api_van_phong.py
@@ -7,7 +7,7 @@
 from kho_phieu_gia import LUC, dat_phieu
 from tram.api.app import tao_app
 from tram.chu import estop
-from tram.phieu.khe import dang_ky_khe
+from tram.phieu.khe import dang_ky_khe, bat_tat_khe
 from tram.phieu.kho import KhoPhieu
 from tram.phieu.nhip_tim import ghi_nhip

@@ -20,6 +20,7 @@
     with kho.giao_dich():
         dang_ky_khe(kho, "B", [{"ten": "claude-1", "cli": "claude", "ten_goi_nho": "a@b.vn", "vai_uu_tien": ["coder"]}],
                     luc=LUC)
+        bat_tat_khe(kho, "B/claude-1", bat=True, vi_sao="fixture đã duyệt", tac_nhan="dai-ca", luc=LUC)
         ghi_nhip(kho, "B/claude-1", luc=LUC, giao_id=None, luot=None, buoc_tho="chay", han_muc=None)
     dat_phieu(kho, "B/claude-1", bead_id="hr-2", tieu_de="Sửa thuế")
     kho.close()
```

### `tests/test_api_yeu_cau_tu_choi.py`

```diff
--- a/tests/test_api_yeu_cau_tu_choi.py
+++ b/tests/test_api_yeu_cau_tu_choi.py
@@ -45,9 +45,6 @@
     app, pt, bd, mo = mo_app(tmp_path)
     thanyc = {**than(), "dau_xem": dau()}
     assert goi_tho(app, TAO, thanyc, DUNG, host="ke-la.example") == 421
-    app.state.kenh_ghi = "unix-socket"                       # qua TCP thẳng, không qua socket của tailscale serve
-    assert goi_tho(app, TAO, thanyc, DUNG) == 403
-    app.state.kenh_ghi = "header"
     pt.cau_hinh = type(pt.cau_hinh)(dai_ca_logins=(LOGIN,), ten_may_b=None)
     assert goi_tho(app, TAO, thanyc, DUNG) == 403
     kiem_khong_dong_vao(bd, mo)
@@ -84,3 +81,10 @@
     app, _, bd, mo = mo_app(tmp_path)
     assert goi_tho(app, TAO, {**than(), "dau_xem": dau(), **sua}, DUNG) == 422
     kiem_khong_dong_vao(bd, mo)
+
+
+def test_d147_xem_tren_tcp_khong_phu_thuoc_socket(tmp_path):
+    app, _, bd, _ = mo_app(tmp_path)
+    app.state.kenh_ghi = 'unix-socket'
+    assert goi_tho(app, XEM, than(), DUNG) == 200
+    assert bd.so_lan_tao() == 0
```

### `tests/giao_viec_gia.py`

```diff
--- a/tests/giao_viec_gia.py
+++ b/tests/giao_viec_gia.py
@@ -10,7 +10,7 @@
 from tram.cau_hinh.du_an_giao import CauHinhGiao
 from tram.cau_hinh.tram import CauHinhTram
 from tram.giao_viec.bo import BoGiaoViec
-from tram.phieu.khe import dang_ky_khe
+from tram.phieu.khe import dang_ky_khe, bat_tat_khe
 from tram.phieu.kho import KhoPhieu
 from tram.phieu.nhip_tim import ghi_nhip

@@ -51,6 +51,7 @@
         dang_ky_khe(kho, "B", [{"ten": t, "cli": "claude", "ten_goi_nho": t, "vai_uu_tien": list(v)} for t, v in khe],
                     luc=LUC)
         for t, _ in khe:
+            bat_tat_khe(kho, f"B/{t}", bat=True, vi_sao="fixture đã duyệt", tac_nhan="dai-ca", luc=LUC)
             ghi_nhip(kho, f"B/{t}", luc=LUC, giao_id=None, luot=None, buoc_tho="ranh", han_muc=None)
     bo = BoGiaoViec(cac_du_an=lambda: [da], tao_bd=lambda d: g, mo_kho=lambda: KhoPhieu(db), ch=CauHinhTram(),
                     dong_ho=lambda: gio[0], kho_git=lambda d: k.kho, boc=boc)
```

### `tests/test_khe_cau_dao.py`

```diff
--- a/tests/test_khe_cau_dao.py
+++ b/tests/test_khe_cau_dao.py
@@ -29,9 +29,9 @@
         return xet_sau_chay(kho, "B/claude-1", ket_thuc, reset_luc=None, han_muc=None, bay_gio=luc, ch=CH, nguong=NG)


-def test_dang_ky_la_bat_va_khong_ghi_lai_khi_khong_doi(tmp_path):
+def test_dang_ky_khong_cap_quyen_va_khong_ghi_lai_khi_khong_doi(tmp_path):
     kho = _kho(tmp_path)
-    assert khe_dang_bat(kho, "B/claude-1") and not khe_dang_bat(kho, "B/claude-9")
+    assert not khe_dang_bat(kho, "B/claude-1") and not khe_dang_bat(kho, "B/claude-9")
     with kho.giao_dich():
         assert dang_ky_khe(kho, "B", [K1], luc=LUC) == ["B/claude-1"]
         dang_ky_khe(kho, "B", [{**K1, "vai_uu_tien": ["qc"]}], luc=LUC)
```

### `tests/test_trang_thai_khe.py`

```diff
--- a/tests/test_trang_thai_khe.py
+++ b/tests/test_trang_thai_khe.py
@@ -17,6 +17,7 @@
         dang_ky_khe(kho, "B", [{"ten": t, "cli": "claude", "ten_goi_nho": f"Claude {t}", "vai_uu_tien": ["coder"]}
                                for t in TEN], luc=LUC)
         for t in TEN:
+            bat_tat_khe(kho, f"B/{t}", bat=True, vi_sao="fixture đã duyệt", tac_nhan="dai-ca", luc=LUC)
             if t != "mat":
                 ghi_nhip(kho, f"B/{t}", luc=LUC, giao_id=None, luot=None, buoc_tho="ranh", han_muc=None)
         ghi_nhip(kho, "B/mat", luc=LUC - timedelta(seconds=91), giao_id=None, luot=None, buoc_tho="ranh",
@@ -45,6 +46,8 @@
     with kho.giao_dich():
         dang_ky_khe(kho, "B", [{"ten": "a", "cli": "claude", "ten_goi_nho": "A", "vai_uu_tien": ["qc"]},
                                {"ten": "b", "cli": "claude", "ten_goi_nho": "B", "vai_uu_tien": ["qc"]}], luc=LUC)
+        for t in ("a", "b"):
+            bat_tat_khe(kho, f"B/{t}", bat=True, vi_sao="fixture đã duyệt", tac_nhan="dai-ca", luc=LUC)
         ghi_nhip(kho, "B/a", luc=LUC, giao_id=None, luot=None, buoc_tho="ranh", han_muc=None)
         kho.ghi_su_kien("hr-codex", "chay.xong", {"khe_id": "B/a", "ket_thuc": "loi_he"}, luc=LUC, bead_id="x")
         kho.ghi_su_kien("hr-codex", "chay.xong", {"khe_id": "B/a", "ket_thuc": "xong"}, luc=LUC, bead_id="x")
```

### `tests/test_nhip_tim.py`

```diff
--- a/tests/test_nhip_tim.py
+++ b/tests/test_nhip_tim.py
@@ -1,3 +1,4 @@
+from khe_duyet_gia import dang_ky_va_duyet
 from datetime import timedelta

 import pytest
@@ -25,7 +26,7 @@
 def kho(tmp_path):
     k = kho_tam(tmp_path)
     with k.giao_dich():
-        dang_ky_khe(k, "B", [{"ten": "claude-1", "cli": "claude", "ten_goi_nho": "1", "vai_uu_tien": ["coder"]}],
+        dang_ky_va_duyet(k, "B", [{"ten": "claude-1", "cli": "claude", "ten_goi_nho": "1", "vai_uu_tien": ["coder"]}],
                     luc=LUC)
     return k

```

### `tests/test_cap_phieu.py`

```diff
--- a/tests/test_cap_phieu.py
+++ b/tests/test_cap_phieu.py
@@ -1,3 +1,4 @@
+from khe_duyet_gia import dang_ky_va_duyet
 import json
 import threading
 from datetime import timedelta
@@ -20,7 +21,7 @@
 def _kho(tmp_path, *khe):
     kho = kho_tam(tmp_path)
     with kho.giao_dich():
-        dang_ky_khe(kho, "B", [{"ten": t, "cli": "claude", "ten_goi_nho": t, "vai_uu_tien": ["coder"]}
+        dang_ky_va_duyet(kho, "B", [{"ten": t, "cli": "claude", "ten_goi_nho": t, "vai_uu_tien": ["coder"]}
                                for t in khe or ("claude-1",)], luc=LUC)
     return kho

```

### `tests/test_truong_2f.py`

```diff
--- a/tests/test_truong_2f.py
+++ b/tests/test_truong_2f.py
@@ -1,3 +1,4 @@
+from khe_duyet_gia import dang_ky_va_duyet
 """Trường bổ sung lát 2f (khảo sát giao diện §1.10): T1 đội ngũ `ten`/`vi_sao_tat`, T2 `cau_dao_ngat`,
 T4 phê duyệt `cau_hoi`/`khe_id`/`buoc`/`bead_goc`, T6 `suc_khoe.muc`. Chỉ THÊM khoá, khoá cũ giữ nguyên."""
 from datetime import timedelta
@@ -20,7 +21,7 @@

 def _khe(kho, *ten, cli="claude"):
     with kho.giao_dich():
-        dang_ky_khe(kho, "B", [{"ten": t, "cli": cli, "ten_goi_nho": "x", "vai_uu_tien": ["coder"]} for t in ten],
+        dang_ky_va_duyet(kho, "B", [{"ten": t, "cli": cli, "ten_goi_nho": "x", "vai_uu_tien": ["coder"]} for t in ten],
                     luc=LUC)
         for t in ten:
             ghi_nhip(kho, f"B/{t}", luc=LUC, giao_id=None, luot=None, buoc_tho="ranh", han_muc=None)
```

### `tests/test_suy_doi_ngu.py`

```diff
--- a/tests/test_suy_doi_ngu.py
+++ b/tests/test_suy_doi_ngu.py
@@ -1,3 +1,4 @@
+from khe_duyet_gia import dang_ky_va_duyet
 from datetime import timedelta

 from kho_phieu_gia import LUC, dat_phieu, kho_tam
@@ -31,7 +32,7 @@
 def test_doi_ngu_the_khe_ten_goi_nho_khong_email_va_phien_ban(tmp_path):
     kho = kho_tam(tmp_path)
     with kho.giao_dich():
-        dang_ky_khe(kho, "B", [{"ten": "claude-1", "cli": "claude", "ten_goi_nho": "Claude 1", "vai_uu_tien": ["coder"]},
+        dang_ky_va_duyet(kho, "B", [{"ten": "claude-1", "cli": "claude", "ten_goi_nho": "Claude 1", "vai_uu_tien": ["coder"]},
                                {"ten": "claude-2", "cli": "claude", "ten_goi_nho": "a@b.vn", "vai_uu_tien": ["qc"]}],
                     luc=LUC)
         ghi_nhip(kho, "B/claude-1", luc=LUC, giao_id=None, luot=None, buoc_tho="chay",
```

### `tests/test_suy_nhan_vat.py`

```diff
--- a/tests/test_suy_nhan_vat.py
+++ b/tests/test_suy_nhan_vat.py
@@ -1,3 +1,4 @@
+from khe_duyet_gia import dang_ky_va_duyet
 from datetime import timedelta

 from kho_phieu_gia import LUC, dat_phieu, kho_tam
@@ -15,7 +16,7 @@

 def _khe(kho, may, *ten, cli="claude", ten_goi_nho="Claude"):
     with kho.giao_dich():
-        dang_ky_khe(kho, may, [{"ten": t, "cli": cli, "ten_goi_nho": ten_goi_nho, "vai_uu_tien": ["coder"]}
+        dang_ky_va_duyet(kho, may, [{"ten": t, "cli": cli, "ten_goi_nho": ten_goi_nho, "vai_uu_tien": ["coder"]}
                                for t in ten], luc=LUC)
         for t in ten:
             ghi_nhip(kho, f"{may}/{t}", luc=LUC, giao_id=None, luot=None, buoc_tho="ranh", han_muc=None)
@@ -36,7 +37,7 @@
     kho = kho_tam(tmp_path)
     _khe(kho, "B", "lam", "ranh", "tat", "dao", "la", ten_goi_nho="dai-ca@vi-du.vn")
     with kho.giao_dich():
-        dang_ky_khe(kho, "B", [{"ten": "mat", "cli": "codex", "ten_goi_nho": "x", "vai_uu_tien": ["qc"]}], luc=LUC)
+        dang_ky_va_duyet(kho, "B", [{"ten": "mat", "cli": "codex", "ten_goi_nho": "x", "vai_uu_tien": ["qc"]}], luc=LUC)
         ngat_cau_dao(kho, "B/dao", ly_do="het-han-muc", toi_luc=LUC + timedelta(hours=1), luc=LUC)
     dat_phieu(kho, "B/lam", bead_id="hr-1", tieu_de="Sửa \u202egiá", buoc="qc")
     cu = dat_phieu(kho, "B/tat", bead_id="hr-2")
```

### `tests/khe_duyet_gia.py`

```python
"""Tiền điều kiện test nghiệp vụ: chủ đã cấp quyền chạy; không dùng trong test cửa máy."""
from tram.phieu.khe import dang_ky_khe, bat_tat_khe


def dang_ky_va_duyet(kho, may, khe, *, luc):
    ids = dang_ky_khe(kho, may, khe, luc=luc)
    for kid in ids:
        bat_tat_khe(kho, kid, bat=True, vi_sao='fixture đã được chủ duyệt', tac_nhan='dai-ca', luc=luc)
    return ids
```

- [ ] **Step 2 — RED:**

```bash
UV_NO_SYNC=1 UV_CACHE_DIR=/tmp/passkey-uv-cache tests/chan_host/chay.sh -q tests/test_api_ghi.py tests/test_api_doi_ngu.py tests/test_api_nho.py tests/test_api_yeu_cau.py
```

**Bằng chứng đã chạy:** RED thật: 3 failed, 1 passed do API nghiệp vụ chưa đăng ký/không phiên. GREEN đầu 29 passed; mở rộng API phát hiện 7 lỗi tiền điều kiện khe/socket cũ, đã sửa. Nhóm 19 file liên quan đăng ký khe: từ 11 failed, 84 passed sang 95 passed. Không sửa assertion để cho agent tự bật khe.

- [ ] **Step 3 — áp mã nguyên văn:**

Task này chỉ sửa tiền điều kiện/helper test, không thay mã sản phẩm hay thêm bypass.

- [ ] **Step 4 — GREEN:**

```bash
UV_NO_SYNC=1 UV_CACHE_DIR=/tmp/passkey-uv-cache tests/chan_host/chay.sh -q tests/test_api_ghi.py tests/test_api_doi_ngu.py tests/test_api_nho.py tests/test_api_yeu_cau.py
```

Chạy thêm tập tích hợp ở mục kiểm chứng cuối; không cộng các lượt lặp thành số test mới.

- [ ] **Step 5 — dừng ở cây làm việc, KHÔNG commit.** Người điều phối review diff và bằng chứng.

## Task 12: Đóng đường cấp mã ghép máy không có P

**Scenario:** Ghép máy không vượt quyền cấp mã.

**Files:**

- `tram/chu/cap_ma.py`
- `tests/test_passkey_ghep.py`
- `tests/test_ghep_may.py`

**Interfaces:** CLI cũ trả 2, không cấp mã. `/api/passkey/ghep-ma` không có nhánh xử lý (404); D155 hoãn cấp mã qua dashboard. Bootstrap D141/D144 giữ nguyên.

- [ ] **Step 1 — áp test và helper test nguyên văn:**

### `tests/test_passkey_ghep.py`

```python
from types import SimpleNamespace
from tram.chu.cap_ma import _cap_ma
from api_gia import tao_app_gia, DAI_CA
from asgi_gia import goi


def test_cli_cu_khong_cap_ma_khong_co_phien(capsys):
    assert _cap_ma(SimpleNamespace(may_id='C')) == 2
    assert 'passkey' in capsys.readouterr().err


def test_endpoint_cap_ma_ghep_chua_mo(tmp_path):
    app, _ = tao_app_gia(tmp_path, {})
    r = goi(app, 'POST', '/api/passkey/ghep-ma', json_body={'may_id':'C'}, headers=DAI_CA)
    assert r.status == 404 and 'ma' not in r.json()
    assert r.headers['cache-control'] == 'no-store'
```

### `tests/test_ghep_may.py`

```diff
--- a/tests/test_ghep_may.py
+++ b/tests/test_ghep_may.py
@@ -32,10 +32,7 @@
         assert t.goi("POST", "/api/ghep-may", None, json_body=than).status == 422


-def test_cli_chu_cap_ma(tram_home_tam, capsys):
-    assert main(["chu", "cap-ma", "C"]) == 0
-    ra = capsys.readouterr().out
-    assert re.search(r"Mã ghép máy C: [0-9A-Z]{4}-[0-9A-Z]{4}-[0-9A-Z]{4}", ra) and "tram tho dang-ky" in ra
-    kho = mo_kho_phieu()
-    cap_token_may(kho, "D", luc=datetime.now(timezone.utc))
-    assert main(["chu", "cap-ma", "D"]) == 2 and "go-may" in capsys.readouterr().err
+def test_cli_chu_cap_ma_can_phien_passkey(tram_home_tam, capsys):
+    assert main(["chu", "cap-ma", "C"]) == 2
+    out = capsys.readouterr()
+    assert out.out == "" and "passkey" in out.err
```

- [ ] **Step 2 — RED:**

```bash
UV_NO_SYNC=1 UV_CACHE_DIR=/tmp/passkey-uv-cache tests/chan_host/chay.sh -q tests/test_passkey_ghep.py tests/test_ghep_may.py
```

**Bằng chứng lịch sử:** CLI cũ trả 0 thay vì 2. Bản vòng 2 yêu cầu endpoint vẫn đóng; RED trước sửa nhận 200 thay vì 404, GREEN trong bộ tích hợp mới ở cuối file.

- [ ] **Step 3 — áp mã nguyên văn:**

### `tram/chu/cap_ma.py`

```diff
--- a/tram/chu/cap_ma.py
+++ b/tram/chu/cap_ma.py
@@ -6,24 +6,8 @@


 def _cap_ma(args) -> int:
-    from tram.cau_hinh.tram import nap_cau_hinh_tram
-    from tram.phieu.kho import mo_kho_phieu
-    from tram.phieu.ma_ghep import cap_ma_ghep
-    from tram.tho.do_may import TAG_THO
-    try:
-        with closing(mo_kho_phieu()) as kho:
-            mg = cap_ma_ghep(kho, args.may_id, luc=datetime.now(timezone.utc))
-    except ValueError as e:
-        print(e, file=sys.stderr)
-        return 2
-    try:
-        may_b = nap_cau_hinh_tram().ten_may_b or "<máy B>.<tailnet>.ts.net"
-    except ValueError:
-        may_b = "<máy B>.<tailnet>.ts.net"
-    print(f"Mã ghép máy {mg.may_id}: {mg.ma} — dùng một lần, hết hạn {mg.het_luc} (UTC).")
-    print(f"Trên Mac thợ (thiết bị Tailscale gắn {TAG_THO}, tài khoản quản lý thợ):")
-    print(f"  tram tho dang-ky --tram-chu https://{may_b} --khe <ten>:<cli>:<vai,…>:<tên gợi nhớ>")
-    return 0
+    print("Đã đóng cấp mã ghép máy cũ; chờ luồng dashboard có passkey (D155).", file=sys.stderr)
+    return 2


 def them_lenh_cap_ma(chu) -> None:
```

- [ ] **Step 4 — GREEN:**

```bash
UV_NO_SYNC=1 UV_CACHE_DIR=/tmp/passkey-uv-cache tests/chan_host/chay.sh -q tests/test_passkey_ghep.py tests/test_ghep_may.py
```

Chạy thêm tập tích hợp ở mục kiểm chứng cuối; không cộng các lượt lặp thành số test mới.

- [ ] **Step 5 — dừng ở cây làm việc, KHÔNG commit.** Người điều phối review diff và bằng chứng.

## Ghép với TM/TC

Đã đọc bản TM-1 bằng `git show 874e7c4:docs/plans/2026-10-18-lat-tm-1-nen-cai-dat.md`.
Không sửa plan TM. `can_kenh_that` của bản đó cố ý chỉ cho **TẠM DỪNG** khi dùng `header`.
Lát này cung cấp cửa thay thế khi ghép: `can_phien_passkey` cho P và `luon_cham_lai` cho R (D140),
đồng thời vẫn kiểm danh tính Tailscale và CSRF bằng `dich_vu`.

1. Router TM đang có `Depends(yeu_cau_ghi)` phải được ghép có chủ đích: dependency này dùng danh sách đóng
   23 tuyến HEAD, nên sẽ từ chối tuyến TM mới. Dùng `Depends(dich_vu)` ở router, gắn kiểm P/R đúng từng thao tác
   và `rang_yeu_cau` cho thân có mã; bổ sung inventory kiểm đủ tuyến mới. Không bỏ toàn bộ bảo vệ router.
2. Hai tuyến tiếp tục và các thao tác bật/tắt tự merge, deploy thủ công cần P. Thay `can_kenh_that` ở những
   tuyến đó bằng `can_phien_passkey`. Tạm dừng vẫn dùng danh tính/CSRF và ledger, không bắt phiên/chạm.
3. Tuyến lưu cấu hình không gắn một mức cố định: server so cấu hình hiện tại với cấu hình mới đã validate.
   Bật tự deploy hoặc sửa một trong ba lệnh chạy dùng R; thay đổi còn lại theo bảng D140 dùng P.
   Nếu nhiều thay đổi, lấy mức cao nhất; không tin trường mức do browser gửi. Giữ `tu_api`,
   `luu_cai_dat_thao_tac`, kiểm phiên bản và các luật nghiệp vụ TM-1 hiện có.
4. R ký nhận **đường dẫn thực và toàn bộ thân** (gồm `ma_thao_tac`, phiên bản kỳ vọng, cấu hình/commit đích).
   Browser xin ceremony với đúng đường/thân đó; server tự tính lại bằng `rang_buoc`. Không băm riêng
   `than.cai_dat.model_dump()` rồi bỏ mã hoặc phiên bản khỏi ràng buộc.
5. `luon_cham_lai` trả người/băm/dấu lặp và chỉ kiểm bằng chứng; nó **không** thực thi hay ghi kết quả TM/TC.
   Consumer phải dùng ledger nghiệp vụ hiện có: xác thực phiên/login và mã/băm trước; nếu đã hoàn thành đúng
   yêu cầu thì trả kết quả đã lưu, không chạy lại và không buộc chạm mới. Với yêu cầu mới, kiểm R còn hạn rồi
   chạy trong cơ chế khoá/ledger của nghiệp vụ. Sau lỗi chưa hoàn thành, retry vẫn phải qua kiểm quyền.
   Không dùng bảng `thao_tac` của passkey thay bảng kết quả, không đánh dấu thành công trước side effect.
6. Khi ghép thêm test TM/TC: `header` không cookie từ chối tiếp tục/lưu; cookie đúng cho P; cookie đơn thuần
   từ chối R; chữ ký đúng nhưng khác đường/thân/mã từ chối; cùng mã khác nội dung 409; retry cùng yêu cầu trả
   kết quả một lần; hết phiên/thu hồi/login khác từ chối. Sau đó chạy lại inventory toàn bộ POST.

Các file dễ giao nhau: `tram/api/app.py`, `tram/api/bao_mat.py`, `frontend/src/api.js`, thanh trên,
`tram/bao_tin/vong.py`; adapter cấu hình cần đối chiếu mẫu TM-1 tại thời điểm ghép. Không chép hunk HEAD này
đè cây TM đã triển khai. Worker tự merge/deploy dùng quyền hệ thống đã thiết kế, không nhận cookie của người;
P/R bảo vệ quyết định bật/tiếp tục/cấu hình, không biến mỗi tick nền thành một lần Touch ID.

## Kiểm chứng đã chạy và lệnh chạy lại

Bằng chứng ngày 18/10/2026 trên mã áp thử của 12 task, sau đó hoàn nguyên. RED thực tế từng task ghi ngay
trong Step 2; các lần sửa thêm đã chạy lại tập tích hợp. Không cộng các lượt lặp thành tổng test mới.

| Đợt | Kết quả thực đo |
|---|---|
| Tập tích hợp API/passkey/Telegram/khe/ghép máy/kiến trúc | **321 passed, 13.14s**; 0 dòng chặn mới, 0 điểm mù, 31 push giả lập |
| Frontend `npm run kiem` | **110 passed**; quét 140 file |
| Frontend `npm run build` và `npm run kiem-dist` | đạt; còn cảnh báo chunk >500 kB của build |
| Cả bộ với `--maxfail=1` | **1 failed, 131 passed**; không được gọi là cả bộ xanh |
| Cùng ca lỗi trên bản sao sạch HEAD | **1 failed** với cùng lỗi dọn tiến trình |

Lệnh tái lập tập tích hợp (tự chọn file, không phụ thuộc danh sách nằm trong `/tmp` phiên viết plan):

```bash
UV_NO_SYNC=1 UV_CACHE_DIR=/tmp/passkey-uv-cache .venv/bin/python - <<'PY'
import os
import subprocess
from pathlib import Path
files = set()
for pattern in ['test_api_*.py', 'test_passkey_*.py', 'test_bao_tin*.py', 'test_do_dai_ma.py',
                'test_vong_import.py', 'test_ghep_may.py', 'test_ma_ghep.py', 'test_khe_2b.py',
                'test_khe_cau_dao.py', 'test_khe_codex.py', 'test_trang_thai_khe.py',
                'test_chon_khe.py', 'test_thao_tac_khe.py']:
    files.update(str(p) for p in Path('tests').glob(pattern))
files.update(str(p) for p in Path('tests').glob('test*.py')
             if 'dang_ky_khe(' in p.read_text() or 'dang_ky_va_duyet(' in p.read_text())
raise SystemExit(subprocess.run(['tests/chan_host/chay.sh', '-q', *sorted(files)], env=os.environ).returncode)
PY
cd frontend && npm run kiem && npm run build && npm run kiem-dist
```

Cả bộ dừng ở `tests/test_ban_chep.py::test_ban_chep_dung_commit_co_repo_git_khong_bi_export_ignore_giau`:
`LoiBanChep` vì không xác nhận được dọn tiến trình. Ca này cũng thất bại trên **HEAD chưa áp plan** ở thư mục tạm.
Đo riêng `/bin/ps`, `/usr/sbin/sysctl kern.osrelease` trả `Operation not permitted`; bind `127.0.0.1:0`
trả `PermissionError: [Errno 1]`. Không nới sandbox, không coi đây là ca đã đạt.
Một đợt mở rộng còn có ca `test_khe_tan_du` sai số lượt gọi khi dọn tiến trình; cần người điều phối chạy lại
cả file này ngoài sandbox, chưa đủ bằng chứng quy hoàn toàn lỗi đó cho OS.

Người điều phối chạy baseline trên HEAD sạch rồi áp plan và chạy **toàn bộ**:

```bash
tests/chan_host/chay.sh -q
cd frontend && npm run kiem && npm run build && npm run kiem-dist
```

Các lệnh OS/cổng dưới đây chưa chạy; test chữ ký giả không thay thế chúng.

## Cổng cho Đại ca — chưa đạt

Mỗi kịch bản cần Đại ca cho phép riêng theo luật cổng chạy thật; không thực hiện khi đang viết plan.
Ghi thời điểm, SHA, phiên bản OS/browser/Tailscale, kết quả và ảnh không chứa mã/cookie vào sổ tay cổng.

### Cổng 1 — duyệt cửa danh tính và chuẩn bị đường lui

- Kho `passkey.db` đã được duyệt theo D152; các phần cửa danh tính vẫn review plan trước triển khai. Chạy lại cả bộ ngoài sandbox.
- Đo quyền DB, backup, WAL và thư mục cha: principal agent A/B không đọc/ghi được. Không khôi phục kho
  xác thực cũ cùng backup nghiệp vụ để làm sống lại phiên/credential đã thu hồi. Nếu buộc phục hồi kho xác thực,
  đóng cửa ghi, dùng quy trình khôi phục thu hồi toàn bộ quyền rồi đăng ký mới trước mở lại.
- Ghi cấu hình trước đổi và cách dừng API/khôi phục bản trước; không bật công tắc giao việc/deploy trong cổng này.

### Cổng 2 — HTTPS qua Tailscale tới TCP và đăng ký máy A

- Kiểm `tailscale version`, `tailscale serve --help`, `tailscale serve status` trên máy B trước chọn cú pháp.
  Dự kiến `tailscale serve --bg http://127.0.0.1:7700` **chỉ sau duyệt và xác nhận help của bản cài**;
  không Funnel. API chỉ bind loopback; tên HTTPS phải khớp `ten_may_b` dùng làm RP/Origin.
- Cấu hình kênh TCP/header đúng adapter hiện có; đo request thực qua proxy có đúng một login Tailscale.
  Không coi header là bằng chứng người: request localhost giả header thiếu phiên vẫn phải thất bại ở P/R.
- Trên Terminal chủ máy B chạy `tram chu passkey cap-ma`, nhập đúng `dong-y`; mã chỉ hiện tại TTY,
  không argv/history/log. Trên **hồ sơ dashboard riêng máy A**, nhập mã, đăng ký bằng Touch ID rồi đăng nhập.
  Kiểm cookie HttpOnly/Secure/SameSite=Strict, không Domain, hạn tuyệt đối 8 giờ, đúng login.
- Sai mã, mã dùng lại, hết 10 phút, hủy Touch ID không mở phiên. Sau 8 giờ P bị từ chối; chạm R không gia hạn.

### Cổng 3 — đo cửa P/R và rủi ro quyền agent A/B (D146/D153)

- Liệt kê principal/quyền thật của từng agent. Dashboard profile không được đưa vào công cụ browser của agent.
  Đo khả năng đọc cookie/profile/DB, điều khiển browser, gọi TTY/CLI cứu hộ; không ghi giá trị bí mật vào bằng chứng.
- Từ cả A và B: giả header, dùng token máy, gọi trực tiếp P; gọi R thiếu chữ ký hoặc chữ ký cho nội dung khác.
  Tất cả bị từ chối, số side effect nghiệp vụ không đổi. Dùng cookie hết hạn/thu hồi/login khác cũng bị chặn.
- Đặc biệt kiểm cấp mã ghép HTTP/CLI cũ đã đóng; đo khả năng agent gọi bootstrap/khôi phục, không mặc định đã chặn.
  Nếu cùng UID vẫn đọc cookie hoặc gọi CLI chủ được thì ghi rõ rủi ro còn lại theo **D153**,
  **vẫn mở cửa theo quyết định Đại ca**, không tự thêm sudo/principal mới; từng dự án thật xét riêng khi bật.
- N ký ức tay/phiếu yêu cầu dùng được sau đăng ký mà không chạm; trước đăng ký bị khoá. Tạm dừng vẫn dùng được.

### Cổng 4 — thiết bị, khôi phục, báo tin và giao diện

- Đi đủ chín màn mockup D150 ở 1440×1000 và 390×844, trên bản dist với CSP thật; kiểm bàn phím, focus,
  Escape, trả focus, lỗi đọc được, không polling nào bật hộp chạm. Trước đăng ký chỉ thao tác dừng được mở.
- Thêm thiết bị bằng mã một lần sau R; thử Touch ID, Windows Hello và điện thoại/USB theo khả năng thực tế.
  QR xác thực do browser quản lý. Hủy thao tác không ghi; thu hồi làm mất phiên của thiết bị ngay;
  passkey cuối cùng bị chặn cả UI lẫn API.
- `tram chu passkey khoi-phuc` tại Terminal chủ: hỏi `dong-y`, thu hồi hết credential/phiên/mã/quyền cũ,
  cấp mã mới; đo và ghi khả năng agent gọi lệnh theo D153. Đăng ký lại trên A rồi đo lại cửa P/R.
- Tạo sự kiện thêm/thu hồi/khôi phục trong giờ yên lặng: Telegram **không gửi ngay**. Restart vòng báo tin;
  buổi sáng hết giờ yên lặng nhận đủ ID/loại/thời điểm trong tin gom. Lỗi mạng giữ outbox để thử lại;
  không có mã, cookie hay nội dung nghiệp vụ trong tin. Thu hồi không chờ Telegram thành công.

**Bằng chứng lịch sử trước review, không phải phép đo bản sửa:** đã áp tuần tự **81 khối mã/diff** của plan lên bản sao HEAD sạch;
**70 file kết quả khớp từng byte** với cây đã kiểm thử. `openspec validate xac-thuc-passkey --strict` đạt.

## Câu hỏi cho Đại ca

Không còn câu hỏi quyết định trong lát này: D152 duyệt kho riêng; D153 chấp nhận rủi ro hồ sơ/khôi phục;
D154 23:00–07:00 do Đại ca tự bật cấu hình; D155 đóng CLI cấp mã ghép cũ, nút dashboard làm sau.
Nguồn mới đọc trực tiếp từ `/Users/dai-ca/Developer/Ben Station/docs/quyet-dinh/2026-10-18-passkey.md`;
không merge main, không sửa bản quyết định trong worktree. Các bước chạy thật vẫn theo cổng được cho phép riêng.

## Ghi chú triển khai — review vòng 1

Giữ phần nhận xét ban đầu để truy nguyên. **Task 13 và bảng Phản hồi review Codex vòng 1 bên dưới thắng
các câu “chưa chạy/chưa có GREEN” của phụ lục lịch sử này.** Không dùng kiểm offline thay cổng thật.

### V1-Q1 — import của màn Phê duyệt

Đã bổ sung hunk import `duocGhi` ngay trong Task 10. Trước sửa, computed gọi tên chưa khai báo;
build Vite và test regex không bảo đảm phát hiện lỗi khi render danh sách. Khi được phép kiểm runtime,
mở màn có ít nhất một mục phê duyệt dưới CSP thật, kiểm console và nút trước/sau đăng ký.

### V1-Q2 — chuyển test socket sang hợp đồng passkey

Sau Task 11, áp diff này vào `tests/test_kenh_ghi.py`. Giữ nguyên test transport socket và hook M;
chỉ thay test cửa P vì D135 đã thay tiêu chí cấp quyền. Gửi cookie tường minh cho cả app lẫn wrapper
`KenhUnix`: cookie jar của `asgi_gia.goi` không tìm thấy `app.state` qua wrapper.

```diff
--- a/tests/test_kenh_ghi.py
+++ b/tests/test_kenh_ghi.py
@@ -20,13 +20,17 @@
     assert goi(app, "POST", DUYET, json_body={}, headers=DAI_CA).status != 403      # qua kênh, tới kiểm dự án/thân


-def test_unix_socket_tcp_bi_chan_ke_ca_header_dung(tmp_path):
+def test_p_can_passkey_tren_ca_tcp_va_socket(tmp_path):
     app, _ = tao_app_gia(tmp_path, {})
     app.state.kenh_ghi = "unix-socket"
-    r = goi(app, "POST", DUYET, json_body={}, headers=DAI_CA)
-    assert r.status == 403 and "kênh" in r.json()["detail"]
-    assert goi(KenhUnix(app), "POST", DUYET, json_body={}, headers=DAI_CA).status != 403
-    assert goi(KenhUnix(app), "POST", DUYET, json_body={}).status == 403              # qua socket vẫn cần danh tính
+    dung = {**DAI_CA, "Cookie": app.state.cookie_test}
+    thieu = {**DAI_CA, "Cookie": ""}
+    for client in (app, KenhUnix(app)):
+        r = goi(client, "POST", DUYET, json_body={}, headers=thieu)
+        assert r.status == 403 and r.json()["detail"] == "Cần phiên passkey"
+        assert goi(client, "POST", DUYET, json_body={}, headers=dung).status == 422
+        r = goi(client, "POST", DUYET, json_body={}, headers={"Cookie": app.state.cookie_test})
+        assert r.status == 403


 def test_chay_hai_cong_that_qua_unix_socket():
```

RED suy luận trước đổi test: test cũ đòi 403/kênh nhưng cookie fixture Task 11 qua cửa P và thân rỗng
đến validation 422. Sau đổi, dự kiến cả hai transport cần cookie + danh tính; thân rỗng không ghi nghiệp vụ.
Lệnh kiểm cho pha code: `tests/chan_host/chay.sh -q tests/test_kenh_ghi.py tests/test_api_dieu_phoi.py`.
Test transport thật có thể vẫn bị sandbox chặn; phân biệt với test ASGI trong bộ nhớ ở trên.

### V1-Q3 / V1-Q4 — test tái hiện còn cần bản GREEN

Thêm nguyên file `tests/test_passkey_review_v1.py` sau Task 12, trước khi công nhận tích hợp.
Không mock verifier, phiên hay quyền R. Test Estop chỉ tiêm lỗi ở kho xác thực; kho nghiệp vụ và file
Estop vẫn dùng fixture tạm thật của repo. Không được bỏ assertion để đạt GREEN.

### `tests/test_passkey_review_v1.py`

```python
from api_gia import DAI_CA, LOGIN, MAY_B, tao_app_gia
from asgi_gia import goi
from passkey_gia import KhoaGia
from webauthn.helpers import base64url_to_bytes, bytes_to_base64url
from tram.chu import estop
from tram.passkey.dich_vu import DichVu


def test_quan_ly_cung_ma_khac_thiet_bi_phai_409(tmp_path):
    app, _ = tao_app_gia(tmp_path, {}, co_passkey=False)
    app.state.passkey_path = tmp_path / 'pk.db'
    dv = DichVu(app.state.passkey_path, LOGIN, MAY_B)
    keys = [KhoaGia(), KhoaGia(), KhoaGia()]
    for k in keys:
        o = dv.bat_dau('dang-ky', ma=dv.cap_ma())
        dv.ket_thuc(o['id'], k.tra(base64url_to_bytes(o['publicKey']['challenge']),
                    dang_ky=True, rp=MAY_B, origin='https://' + MAY_B))
    o = dv.bat_dau('phien')
    c = dv.ket_thuc(o['id'], keys[0].tra(base64url_to_bytes(o['publicKey']['challenge']),
                    rp=MAY_B, origin='https://' + MAY_B))['cookie']
    hs = {**DAI_CA, 'Cookie': '__Host-tram-phien=' + c}

    def post(viec, body):
        return goi(app, 'POST', '/api/passkey/' + viec, json_body=body, headers=hs)

    def xac_nhan(than):
        r = post('bat-dau', {'loai': 'r', 'duong': '/api/passkey/thu-hoi', 'than': than})
        assert r.status == 200
        o = r.json()
        r = post('ket-thuc', {'id': o['id'], 'credential': keys[0].tra(
            base64url_to_bytes(o['publicKey']['challenge']), rp=MAY_B, origin='https://' + MAY_B)})
        assert r.status == 200
        return r.json()['quyen']

    a = {'ma_thao_tac': 'review-cung-ma-01', 'id': bytes_to_base64url(keys[1].id)}
    b = {**a, 'id': bytes_to_base64url(keys[2].id)}
    qa, qb = xac_nhan(a), xac_nhan(b)
    assert post('thu-hoi', {'than': a, 'quyen': qa}).status == 200
    assert post('thu-hoi', {'than': a, 'quyen': qa}).status == 200
    assert post('thu-hoi', {'than': b, 'quyen': qb}).status == 409
    assert len(dv.trang_thai(c)['thiet_bi']) == 2


def test_estop_khong_can_mo_kho_passkey(tmp_path, monkeypatch):
    app, _ = tao_app_gia(tmp_path, {}, co_passkey=False)

    def kho_hong(self):
        raise AssertionError('Estop không được phụ thuộc kho passkey')

    monkeypatch.setattr(DichVu, 'mo', kho_hong)
    r = goi(app, 'POST', '/api/chu/estop', headers=DAI_CA,
            json_body={'ma_thao_tac': 'review-estop-01', 'expected_version': '', 'ly_do': 'Dừng'})
    assert r.status == 200
    assert estop.dang_bat()

    r2 = goi(app, 'POST', '/api/chu/estop', headers=DAI_CA,
             json_body={'ma_thao_tac': 'review-estop-01', 'expected_version': '', 'ly_do': 'Dừng'})
    assert r2.status == 200 and r2.json()['lap_lai'] is True
    for hs in ({}, {**DAI_CA, 'Origin':'https://gia'}, {**DAI_CA,'X-Tram':'0'}):
        assert goi(app,'POST','/api/chu/estop',headers=hs,
                   json_body={'ma_thao_tac':'review-estop-02','expected_version':'','ly_do':'Dừng'}).status == 403
```

RED suy luận Q3: API quản lý không gọi `rang_ma`; hai R hợp lệ có cùng mã nhưng khác target tạo hai
`rang`, đều được thu hồi (200), còn một credential thay vì hai. Cần kiểm mã/người/nội dung trong cùng
giao dịch với kiểm R và ghi quản lý, trả 409 trước lần ghi thứ hai; không chỉ thêm kiểm ở browser.
Phải bổ sung cả ca cùng mã/nội dung từ phiên mới không tạo mã mời mới hoặc lặp tác dụng.

RED suy luận Q4: `can_ghi` miễn Estop nhưng `yeu_cau_ghi` tiếp tục gọi `rang_yeu_cau`, hàm này mở
`dv.mo()` trước nghiệp vụ. Cần giữ đường dừng không phụ thuộc kho passkey, đồng thời giữ chống lặp của
`tram/thao_tac/estop.py` và kiểm danh tính/CSRF. Bản sửa phải nói rõ ngoại lệ băm payload ở đường dừng;
không xoá toàn bộ kiểm chống lặp của các tuyến khác.

Lệnh cho pha code sau khi có bản sửa: `tests/chan_host/chay.sh -q tests/test_passkey_review_v1.py`.
Vòng review này không chạy lệnh và không đưa ra số passed/failed.


## Phản hồi review Codex vòng 1

Nhận Q1–Q7, N1–N2. Task 13 bên dưới là mã cuối thay thế trọn các file đã tạo ở task trước;
không cherry-pick riêng test hay bỏ phần sửa mã. Kho đang ở schema **chưa phát hành**; bảng `ket_qua`
được thêm vào v1 cùng chuỗi plan, không áp lên kho v1 đã chạy thật.

| Mục | Bản sửa và bằng chứng mới |
|---|---|
| V1-Q1 | Giữ import Task 10; test Vue compile + SSR danh sách decision không rỗng: bỏ import gây `ReferenceError: duocGhi is not defined`, giữ import render được. Browser CSP thật còn ở cổng. |
| V1-Q2 | Sửa hunk thiếu context; test cũ RED `422 == 403`, test P mới GREEN trên TCP/Unix wrapper ASGI; không đánh đồng với bind transport thật. |
| V1-Q3 | `quan_ly` kiểm R, ràng buộc người/mã/nội dung, kết quả và side effect trong cùng `BEGIN IMMEDIATE`; RED nhận 200 thay 409; GREEN xung đột, retry, phiên mới, mã đã dùng, từ chối không giữ mã. |
| V1-Q4 | Estop bỏ riêng ledger băm của passkey; vẫn gọi kiểm login/CSRF, ledger `bat_estop_thao_tac` giữ chống lặp. RED `Estop không được phụ thuộc kho passkey`; GREEN kho hỏng + retry + sai Origin/danh tính/X-Tram. |
| V1-Q5 | Middleware ASGI đọc trước typed body, trần 64 KiB/hạn tổng 5s; SQLite/verifier chạy threadpool, mỗi thread tự mở/đóng kho. RED thiếu middleware và `SQLite/verifier chặn event loop`; GREEN body quá lớn/chậm, kho SQLite bị khoá, request khác tiến triển, huỷ client rồi retry không nhân đôi. |
| V1-Q6 | Snapshot thân trước await, mô tả hành động/đích riêng; modal chỉ nhận chuỗi cho phép, không nhận toàn payload/mã. Hai đích khác nhau + huỷ cả P/R đã kiểm; RED `hienThi` undefined, GREEN. |
| V1-Q7 | Bổ sung migration lỗi giữa SQL + backup/version/schema, race cùng assertion login/R, challenge hết đúng 120s khi mã còn hạn, UP=0, đổi mã passkey qua route ghép thật, marker qua đăng ký/lỗi/schema/Telegram/log/sự kiện, P thiếu cookie ở bảy route thật. RED fixture thiếu `up`; sửa fixture cho cờ UP độc lập, các ca hành vi vốn đúng xanh ngay được ghi đúng là bổ sung coverage. |
| V1-N1 | Tiêu đề Thiết bị riêng, menu vẫn chín mục; RED `Ben Station != Thiết bị`, GREEN. |
| V1-N2 | Tách số lịch sử và phép đo phiên sửa; đã kiểm áp tuần tự lại trước bàn giao. Kiểm tài liệu RED `AssertionError: D152`; GREEN khi đủ D152–D155, mục phản hồi và bỏ câu hỏi đã chốt. |

### Hợp đồng bổ sung

- Kết quả mời bền chỉ lưu trạng thái **đã cấp**, không lưu mã rõ. Phản hồi đầu trả mã; retry cùng mã/nội dung
  (kể cả phiên/R mới, sau mã dùng hoặc hết hạn) trả `{da_cap: true, ma: null}` và không sinh/hủy mã khác.
  Nếu mất phản hồi đầu, UI báo đã cấp và Đại ca bấm Thêm thiết bị để tạo **yêu cầu mới**. UUID cũ giữ trong RAM
  qua lỗi truyền tải đến khi có kết quả; không tự tạo UUID mới khi bấm lại sau mất phản hồi. Reload mất RAM
  là yêu cầu mới của người dùng, không tuyên bố phục hồi mã qua reload. Thu hồi retry trả kết quả cũ.
- Không giữ mã của yêu cầu R sai: kiểm R và ledger nằm cùng giao dịch, lỗi rollback cả hai. R/phiên bị thu hồi
  vẫn từ chối retry; có kết quả trong ledger không phải quyền bỏ xác thực. Không ghi assertion/cookie/mã vào ledger.
- Hạn body chỉ bao pha nhận HTTP. Không timeout rồi “bỏ mặc” giao dịch: SQLite có busy timeout 10s mỗi lần chờ;
  đây không phải hạn tuyệt đối 10s của cả lời gọi. `mo_ket_noi` còn thử WAL tối đa 100 lần, nghỉ 0,1s giữa lần;
  migration có hạn backup riêng 60s, không bao thời gian ghi/fsync. Không hứa HTTP/CLI kết thúc trong 10s.
  thread hoàn tất/rollback và đóng kết nối. Ngắt client có thể không ngắt thread đang commit; kết quả quản lý
  được commit nguyên tử với side effect nên retry đối soát ledger. Không retry tự động một lệnh ghi.
  Ledger nghiệp vụ hiện có vẫn bắt buộc cho TM/TC; giới hạn này không hứa hủy thao tác khi browser đóng.
- Estop miễn **chỉ** bảng băm passkey: cùng mã dùng kết quả của ledger nghiệp vụ sẵn có, không mở passkey.db;
  không áp quy tắc 409 payload mới lên Estop vì ưu tiên đường dừng. Danh tính/Origin/X-Tram vẫn bắt buộc.
- `ghi(duong, than, hienThi?)`, `quanLy(viec, than, hienThi)` nhận mô tả `{hanhDong,dich}` chụp từ cùng đích
  đang gửi. Caller TM/TC phải truyền tên dự án/thiết bị cụ thể từ snapshot; fallback route hiện tại hiển thị
  loại hành động và mã đích. Modal dùng interpolation Vue, giới hạn 100/300 ký tự; không render HTML.
- D154: không hardcode giờ vào sản phẩm. Test dùng `23:00-07:00`; cấu hình thật đang tắt, Đại ca tự đặt
  `telegram.gio_yen_lang: "23:00-07:00"` ở `~/.tram/cau-hinh.yaml`. Phiên này không đọc/ghi file đó.

## Task 13: Sửa sau review vòng 1 và kiểm chuỗi plan

**Files:** các file có tiêu đề mã nguyên văn bên dưới; Q1 ở Task 10, Q2 ở phụ lục; không sửa kho nghiệp vụ.
**Interfaces:** giữ API task trước; thêm `DichVu.quan_ly(cookie, quyen, viec, than)`, middleware `GioiHanThan`,
metadata hiển thị riêng và kết quả mời retry như hợp đồng trên. Không dependency mới.

- [ ] **Step 1 — TEST:** áp các file test bên dưới và test Q3/Q4 ở phụ lục; Q7 cần helper `up` của Task 1.
- [ ] **Step 2 — RED:** chạy lệnh dưới trước phần mã GREEN; lỗi quan sát thật ở bảng phản hồi, không đòi mọi
  ca coverage mới phải đỏ khi hành vi hiện có đã đúng. Test Q1 tự thử bản bỏ import và bản đầy đủ.

```bash
UV_NO_SYNC=1 UV_CACHE_DIR=/tmp/passkey-uv-cache tests/chan_host/chay.sh -q tests/test_passkey_review_v1.py tests/test_passkey_http_v1.py tests/test_passkey_bo_sung_v1.py
node --test frontend/tests/passkey-review-v1.test.mjs frontend/tests/passkey-phe-duyet-runtime.test.mjs
```

### `tests/test_passkey_http_v1.py`

```python
import asyncio
import json
import threading
from fastapi import Request
from api_gia import tao_app_gia, DAI_CA
from tram.api.passkey import ghi
from tram.passkey.dich_vu import DichVu


def test_body_som_va_han_tuyet_doi(tmp_path):
    from tram.api.passkey_http import GioiHanThan
    async def run():
        reached = []
        async def endpoint(scope, receive, send):
            reached.append(True)
        app = GioiHanThan(endpoint, han=0.02)
        for chunks, expected in [([b'x'*40000, b'x'*40000], 413), ([b'x', None], 408)]:
            sent = []
            async def receive():
                b = chunks.pop(0)
                if b is None:
                    await asyncio.sleep(.1)
                return {'type':'http.request', 'body':b or b'', 'more_body':bool(chunks)}
            async def send(m): sent.append(m)
            await app({'type':'http','method':'POST','path':'/api/passkey/bat-dau'}, receive, send)
            assert sent[0]['status'] == expected
        assert reached == []
    asyncio.run(co_han(run()))


def test_ceremony_khong_chan_event_loop(tmp_path, monkeypatch):
    app, _ = tao_app_gia(tmp_path, {}, co_passkey=False)
    entered, released = threading.Event(), threading.Event()
    def busy(self, *args, **kwargs):
        entered.set()
        assert released.wait(1), 'SQLite/verifier chặn event loop'
        return {'id':'ok'}
    monkeypatch.setattr(DichVu, 'bat_dau', busy)
    async def run():
        scope = {'type':'http','method':'POST','path':'/api/passkey/bat-dau','app':app,
                 'headers':[(k.lower().encode(),v.encode()) for k,v in DAI_CA.items()]}
        async def receive():
            return {'type':'http.request','body':json.dumps({'loai':'phien'}).encode()}
        task = asyncio.create_task(ghi('bat-dau', Request(scope, receive)))
        try:
            await cho_event(entered, task)
            released.set()
            assert (await asyncio.wait_for(task, 2)).status_code == 200
        finally:
            released.set()
            if not task.done(): task.cancel()
            await asyncio.gather(task, return_exceptions=True)
    asyncio.run(co_han(run()))


def test_kho_sqlite_ban_request_khac_van_tien_trien(tmp_path):
    from tram.passkey.kho import mo_kho
    app,_=tao_app_gia(tmp_path,{})
    async def run():
        scope={'type':'http','method':'POST','path':'/api/passkey/bat-dau','app':app,
               'headers':[(k.lower().encode(),v.encode()) for k,v in DAI_CA.items()]}
        async def receive():
            return {'type':'http.request','body':b'{"loai":"phien"}'}
        with mo_kho(app.state.passkey_path) as db:
            db.execute('BEGIN IMMEDIATE')
            task=asyncio.create_task(ghi('bat-dau',Request(scope,receive)))
            await asyncio.sleep(.03)
            assert not task.done()
            db.rollback()
        assert (await asyncio.wait_for(task,1)).status_code == 200
    asyncio.run(co_han(run()))


def test_ngat_client_khong_nhan_doi_giao_dich(tmp_path, monkeypatch):
    from test_passkey_dich_vu import them, login
    from tram.passkey.chinh_sach import rang_buoc
    from tram.passkey.kho import mo_kho
    d=DichVu(tmp_path/'cancel.db','chu','b.test')
    k=them(d); c=login(d,k)['cookie']; body={'ma_thao_tac':'cancel-01'}
    q=login(d,k,'r',c,rang_buoc('/api/passkey/moi',body))['quyen']
    entered, released, finished = threading.Event(), threading.Event(), threading.Event()
    original=DichVu.quan_ly
    def slow(self,*args):
        entered.set()
        assert released.wait(1)
        try: return original(self,*args)
        finally: finished.set()
    monkeypatch.setattr(DichVu,'quan_ly',slow)
    async def run():
        from starlette.concurrency import run_in_threadpool
        task=asyncio.create_task(run_in_threadpool(d.quan_ly,c,q,'moi',body))
        try:
            await cho_event(entered, task)
            task.cancel()
        finally:
            released.set()
            if not task.done(): task.cancel()
            await asyncio.gather(task, return_exceptions=True)
        async with asyncio.timeout(2):
            while not finished.is_set(): await asyncio.sleep(.001)
    asyncio.run(co_han(run()))
    assert d.quan_ly(c,q,'moi',body) == {'da_cap':True,'ma':None}
    with mo_kho(d.path) as db:
        assert db.execute('select count(*) from ket_qua').fetchone()[0] == 1
        assert db.execute('select count(*) from ma').fetchone()[0] == 1


async def co_han(coro):
    async with asyncio.timeout(3):
        return await coro


async def cho_event(event, task):
    async with asyncio.timeout(1):
        while not event.is_set():
            if task.done():
                await task
                raise AssertionError('Task kết thúc trước khi vào worker')
            await asyncio.sleep(.001)
```

### `tests/test_passkey_bo_sung_v1.py`

```python
import concurrent.futures
import sqlite3
import pytest
from test_passkey_dich_vu import dv, them, login
from passkey_gia import KhoaGia
from tram.passkey.kho import mo_kho, TuChoi
from tram.su_kien.phien_ban import nang_cap, LoiPhienBan
from webauthn.helpers import base64url_to_bytes
from api_gia import tao_app_gia, DAI_CA, LOGIN, MAY_B
from asgi_gia import goi


def test_migration_loi_giu_schema_version_va_backup(tmp_path):
    p = tmp_path/'pk.db'
    with mo_kho(p) as db:
        before = db.execute('SELECT sql FROM sqlite_master ORDER BY name').fetchall()
        with pytest.raises(LoiPhienBan):
            nang_cap(db, thu_muc_sao_luu=tmp_path/'backup', moi=2,
                     buoc={2:('CREATE TABLE tam(id INT)', 'INVALID SQL')})
        assert db.execute('pragma user_version').fetchone()[0] == 1
        assert db.execute('SELECT sql FROM sqlite_master ORDER BY name').fetchall() == before
    backups = list((tmp_path/'backup').glob('*.db'))
    assert len(backups) == 1
    with sqlite3.connect(backups[0]) as db:
        assert db.execute('pragma user_version').fetchone()[0] == 1
        assert not db.execute("SELECT 1 FROM sqlite_master WHERE name='tam'").fetchone()


@pytest.mark.parametrize('loai', ['phien', 'r'])
def test_cung_assertion_dong_thoi_chi_mot_quyen(dv, loai):
    k = them(dv)
    c = login(dv,k)['cookie']
    o = dv.bat_dau(loai, cookie=c, rang='target')
    assertion = k.tra(base64url_to_bytes(o['publicKey']['challenge']))
    def go(_):
        try: return dv.ket_thuc(o['id'], assertion)
        except TuChoi: return None
    with concurrent.futures.ThreadPoolExecutor(2) as pool:
        results = list(pool.map(go, range(2)))
    assert sum(r is not None for r in results) == 1


def test_challenge_het_120_khi_ma_con_han(dv):
    m = dv.cap_ma()
    o = dv.bat_dau('dang-ky', ma=m)
    dv.clock[0] += 120
    with pytest.raises(TuChoi):
        dv.ket_thuc(o['id'], KhoaGia().tra(base64url_to_bytes(o['publicKey']['challenge']), dang_ky=True))
    assert dv.bat_dau('dang-ky', ma=m)['id'] != o['id']


@pytest.mark.parametrize('dang_ky', [True, False])
def test_up_0_khong_cap_quyen(dv, dang_ky):
    k = KhoaGia() if dang_ky else them(dv)
    o = dv.bat_dau('dang-ky',ma=dv.cap_ma()) if dang_ky else dv.bat_dau('phien')
    with pytest.raises(TuChoi):
        dv.ket_thuc(o['id'], k.tra(base64url_to_bytes(o['publicKey']['challenge']), dang_ky=dang_ky, up=False))


def test_ma_passkey_khong_doi_token_http(tmp_path):
    from tram.passkey.dich_vu import DichVu
    from tram.phieu.kho import KhoPhieu
    app, pt = tao_app_gia(tmp_path, {})
    pt.mo_kho_phieu = lambda: KhoPhieu(tmp_path/'phieu.db')
    ma = DichVu(app.state.passkey_path, LOGIN, MAY_B).cap_ma()
    r = goi(app,'POST','/api/ghep-may',json_body={'ma':ma})
    assert r.status == 403 and 'token' not in r.json()


@pytest.mark.parametrize('path,extra', [
    ('/api/bead/hr/hr-1/chot', {'tra_loi':['đồng ý']}),
    ('/api/phe-duyet/hr/hr-1/duyet', {}),
    ('/api/phe-duyet/hr/hr-1/tra-loi', {'tra_loi':'đồng ý'}),
    ('/api/chu/tiep-tuc', {}),
    ('/api/khe/B/main/bat', {}),
    ('/api/khe/B/main/cau-dao-dong', {}),
    ('/api/nho/xoa', {'id':'x'}),
])
def test_route_p_that_thieu_cookie_khong_ghi(tmp_path, monkeypatch, path, extra):
    app, pt = tao_app_gia(tmp_path,{})
    calls=[]
    def forbidden(*args, **kwargs):
        calls.append(1)
        pytest.fail('Không được mở kho nghiệp vụ')
    for name in ('mo_kho','mo_kho_tt','mo_kho_phieu','tao_bd'):
        monkeypatch.setattr(pt,name,forbidden)
    from tram.api.than import ThanGhi, ThanChot, ThanDuyet, ThanTraLoi, ThanNhoXoa
    from tram.api.doi_ngu import ThanKhe
    cls={'chot':ThanChot,'duyet':ThanDuyet,'tra-loi':ThanTraLoi,'xoa':ThanNhoXoa,'bat':ThanKhe}
    body={'ma_thao_tac':'v1-p-001','expected_version':'', **extra}
    cls.get(path.rsplit('/',1)[-1],ThanGhi).model_validate(body)
    r=goi(app,'POST',path,headers={**DAI_CA,'Cookie':''},json_body=body)
    assert r.status == 403 and r.json()['detail'] == 'Cần phiên passkey'
    assert calls == []


def test_moi_retry_phien_moi_khong_huy_ma_cu(dv):
    from tram.passkey.chinh_sach import rang_buoc
    from tram.passkey.thao_tac import XungDotMa
    k=them(dv)
    than={'ma_thao_tac':'moi-01'}
    rang=rang_buoc('/api/passkey/moi',than)
    c=login(dv,k)['cookie']; q=login(dv,k,'r',c,rang)['quyen']
    first=dv.quan_ly(c,q,'moi',than)
    c2=login(dv,k)['cookie']; q2=login(dv,k,'r',c2,rang)['quyen']
    assert dv.quan_ly(c2,q2,'moi',than) == {'da_cap':True,'ma':None}
    them(dv,first['ma'])
    assert dv.quan_ly(c2,q2,'moi',than) == {'da_cap':True,'ma':None}
    with mo_kho(dv.path) as db:
        assert db.execute('select count(*) from ket_qua').fetchone()[0] == 1
        assert db.execute('select count(*) from ma').fetchone()[0] == 0
    changed={**than,'khac':True}
    q3=login(dv,k,'r',c2,rang_buoc('/api/passkey/moi',changed))['quyen']
    with pytest.raises(XungDotMa): dv.quan_ly(c2,q3,'moi',changed)


def test_quan_ly_bi_tu_choi_khong_giu_ma(dv):
    from tram.passkey.chinh_sach import rang_buoc
    k=them(dv); c=login(dv,k)['cookie']
    body={'ma_thao_tac':'moi-02'}
    with pytest.raises(TuChoi): dv.quan_ly(c,'gia','moi',body)
    with mo_kho(dv.path) as db:
        assert db.execute('select count(*) from thao_tac').fetchone()[0] == 0
        assert db.execute('select count(*) from ket_qua').fetchone()[0] == 0


def test_marker_khong_ro_qua_loi_su_kien_telegram(tmp_path, caplog, capsys):
    from datetime import datetime, timezone
    from tram.passkey.dich_vu import DichVu
    from tram.bao_tin.passkey import gui_cho
    app, pt=tao_app_gia(tmp_path,{},co_passkey=False)
    app.state.passkey_path=tmp_path/'pk.db'
    d=DichVu(app.state.passkey_path,LOGIN,MAY_B)
    marker='V1-PRIVATE-MARKER-7f2a'
    ma=d.cap_ma()
    k=KhoaGia()
    o=d.bat_dau('dang-ky',ma=ma)
    cred=k.tra(base64url_to_bytes(o['publicKey']['challenge']),dang_ky=True,rp=MAY_B,origin='https://'+MAY_B)
    r=goi(app,'POST','/api/passkey/ket-thuc',headers=DAI_CA,
          json_body={'id':o['id'],'credential':cred,'ten':marker})
    assert r.status == 200
    # Nhánh schema và verifier; credential ID hợp lệ để lỗi đi tới verifier thật.
    o = d.bat_dau('phien')
    bad = k.tra(base64url_to_bytes(o['publicKey']['challenge']), rp=MAY_B, origin='https://'+MAY_B)
    bad['response']['signature'] = marker
    for body in ({'credential':marker}, {'id':o['id'], 'credential':bad}):
        r=goi(app,'POST','/api/passkey/ket-thuc',headers=DAI_CA,json_body=body)
        assert r.status in (403,422) and marker not in r.body.decode()
    sent=[]
    assert gui_cho(d.path,None,datetime.now(timezone.utc),sent.append) == 1
    with mo_kho(d.path) as db:
        events=repr([tuple(row) for row in db.execute('select * from tin')])
    out=capsys.readouterr()
    assert marker not in caplog.text+out.out+out.err+events+repr(sent)
    assert ma not in caplog.text+out.out+out.err+events+repr(sent)
    from contextlib import closing
    with closing(pt.mo_kho()) as kho:
        assert marker not in repr(kho.gan_day('_tram',None,100))
```

### `frontend/tests/passkey-review-v1.test.mjs`

```javascript
import test from 'node:test'
import assert from 'node:assert/strict'
import { datHoi, nghiLe } from '../src/passkey.js'
import { tenTrang, MENU } from '../src/menu.js'

test('N1: tiêu đề Thiết bị giữ menu chín mục', () => {
  assert.equal(tenTrang('/tai-khoan/thiet-bi'), 'Thiết bị')
  assert.equal(MENU.length, 9)
})
test('Q6: modal chỉ nhận mô tả đích, huỷ không chạy ceremony', async () => {
  const seen = []
  datHoi(async q => { seen.push(q); return false })
  for (const id of ['usb-a', 'usb-b']) {
    await assert.rejects(nghiLe('r', {
      duong: '/api/passkey/thu-hoi', than: {id, ma_thao_tac:'secret-marker'},
      hienThi: {hanhDong:'Thu hồi thiết bị', dich:id},
    }), /huỷ/)
  }
  assert.deepEqual(seen.map(q => q.hienThi.dich), ['usb-a', 'usb-b'])
  assert.ok(!JSON.stringify(seen).includes('secret-marker'))
})

test('Q6: P hết phiên hiển thị đúng hai đích, huỷ không gửi lại', async () => {
  const { ghi } = await import('../src/api.js')
  const old = globalThis.fetch, sent = [], seen = []
  globalThis.fetch = async (path, args) => {
    sent.push([path,JSON.parse(args.body)])
    return {ok:false,status:403,json:async()=>({detail:'Cần phiên passkey'})}
  }
  datHoi(async q => { seen.push(q); return false })
  try {
    for (const id of ['hr-1','hr-2']) {
      await assert.rejects(ghi('/api/phe-duyet/hr/'+id+'/duyet', {ma_thao_tac:id}), /huỷ/)
    }
    assert.deepEqual(seen.map(q=>q.hienThi.dich), ['phe-duyet / hr / hr-1','phe-duyet / hr / hr-2'])
    assert.ok(seen.every(q=>q.hienThi.hanhDong === 'Duyệt việc'))
    assert.equal(sent.length,2)
  } finally { globalThis.fetch = old }
})
```

### `frontend/tests/passkey-phe-duyet-runtime.test.mjs`

```javascript
import test from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { createSSRApp } from 'vue'
import { renderToString } from '@vue/server-renderer'
import { parse, compileScript } from '@vue/compiler-sfc'

// Chạy computed và template Vue thật; chỉ thay IO và component con bằng fixture.
async function render(source) {
  source = source.replace("const ds = ref([])", "const ds = ref([{loai:'decision',du_an:'hr',id:'hr-1'}])")
  source = source.replace(/import ([A-Za-z]+) from '[^']+\.vue'/g,
    "const $1 = { template: '<span>Thẻ phê duyệt</span>' }")
  source = source.replace(/import '[^']+\.css'\n/g, '')
  source = source.replace("import { kho, taiSoPheDuyet } from '../kho.js'",
    "const kho = {trangThai:{la_dai_ca:true,passkey:{thiet_bi:[{}]}}}; const taiSoPheDuyet = () => {}")
  const { descriptor } = parse(source)
  let code = compileScript(descriptor, {id:'runtime-test',inlineTemplate:true}).content
  code = code.replace(/from (['"])(.*?)\1/g, (all, q, name) => {
    const url = name.startsWith('.') ? new URL('../src/trang/' + name, import.meta.url).href : import.meta.resolve(name)
    return `from '${url}'`
  })
  const { default: component } = await import('data:text/javascript;base64,' + Buffer.from(code).toString('base64'))
  return renderToString(createSSRApp(component))
}
test('Q1: template danh sách không rỗng đánh giá khoaCua', async () => {
  const src = await readFile(new URL('../src/trang/PheDuyet.vue', import.meta.url),'utf8')
  await assert.rejects(render(src.replace("import { duocGhi } from '../quyen_passkey.js'",'')), /duocGhi/)
  assert.match(await render(src), /Thẻ phê duyệt/)
})
```

- [ ] **Step 3 — GREEN:** thay **toàn bộ** các file dưới bằng mã nguyên văn.

### `tram/passkey/luoc_do.py`

```python
"""Kho riêng: không đổi su-kien.db, số phiên bản riêng qua cùng cơ chế migration."""
BUOC = {1: (
    'CREATE TABLE nguoi(id BLOB PRIMARY KEY, login TEXT UNIQUE NOT NULL, vai TEXT NOT NULL, bat INT NOT NULL)',
    'CREATE TABLE khoa(id BLOB PRIMARY KEY, nguoi BLOB NOT NULL, public BLOB NOT NULL, dem INT NOT NULL, '
    'ten TEXT NOT NULL, tao REAL NOT NULL, dung REAL, thu REAL)',
    'CREATE TABLE ma(bam TEXT PRIMARY KEY, nguoi BLOB NOT NULL, nguon BLOB, han REAL NOT NULL)',
    'CREATE TABLE phien(bam TEXT PRIMARY KEY, nguoi BLOB NOT NULL, khoa BLOB NOT NULL, '
    'login TEXT NOT NULL, han REAL NOT NULL)',
    'CREATE TABLE hoi(id TEXT PRIMARY KEY, nguoi BLOB NOT NULL, challenge BLOB NOT NULL, '
    'loai TEXT NOT NULL, rang TEXT NOT NULL, phien TEXT NOT NULL, ma TEXT NOT NULL, han REAL NOT NULL)',
    'CREATE TABLE quyen(id TEXT PRIMARY KEY, nguoi BLOB NOT NULL, phien TEXT NOT NULL, '
    'rang TEXT NOT NULL, han REAL NOT NULL, dung INT NOT NULL DEFAULT 0)',
    'CREATE TABLE tin(id INTEGER PRIMARY KEY, loai TEXT NOT NULL, luc REAL NOT NULL, gui INT NOT NULL DEFAULT 0)',
    'CREATE TABLE thao_tac(ma TEXT PRIMARY KEY, nguoi BLOB NOT NULL, bam TEXT NOT NULL)',
    'CREATE TABLE ket_qua(ma TEXT PRIMARY KEY, nguoi BLOB NOT NULL, rang TEXT NOT NULL, loai TEXT NOT NULL)',
    'CREATE TABLE sai(nguoi BLOB PRIMARY KEY, dem INT NOT NULL, han REAL NOT NULL)',
)}
```

### `tram/passkey/dich_vu.py`

```python
"""Một kết nối/giao dịch mỗi lời gọi; không giữ kết nối xuyên luồng."""
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from collections.abc import Callable
from webauthn.helpers import bytes_to_base64url
from tram.passkey import nghi_le, thiet_bi
from tram.passkey.kho import mo_kho, giao_dich, nguoi, cap_ma, cac_khoa, phien, TuChoi


@dataclass
class DichVu:
    path: Path
    login: str
    rp: str
    dong_ho: Callable = time.time

    @contextmanager
    def mo(self):
        with mo_kho(self.path) as db, giao_dich(db):
            yield db, nguoi(db, self.login), self.dong_ho()

    def cap_ma(self, khoi_phuc=False):
        with self.mo() as (db, u, luc):
            return cap_ma(db, u, luc, khoi_phuc)

    def bat_dau(self, loai, *, cookie='', rang='', ma=''):
        with self.mo() as (db, u, luc):
            return nghi_le.bat_dau(db, u, self.rp, luc, loai, cookie, rang, ma)

    def ket_thuc(self, cid, credential, ten='Thiết bị'):
        with self.mo() as (db, u, luc):
            return nghi_le.ket_thuc(db, u, self.rp, luc, cid, credential, ten)

    def can_phien(self, cookie):
        with self.mo() as (db, u, luc):
            return dict(phien(db, u, cookie, luc))

    def trang_thai(self, cookie):
        with self.mo() as (db, u, luc):
            try:
                con = max(0, int(phien(db, u, cookie, luc)['han']-luc))
            except TuChoi:
                con = 0
            return {'con_giay': con, 'cho_gui': db.execute('SELECT count(*) FROM tin WHERE gui=0').fetchone()[0],
                    'thiet_bi': [{'id': bytes_to_base64url(k['id']), 'ten': k['ten'], 'tao': k['tao'],
                                 'dung': k['dung']} for k in cac_khoa(db, u)]}

    def moi(self, cookie, quyen, *, rang):
        with self.mo() as (db, u, luc):
            return thiet_bi.moi(db, u, cookie, quyen, rang, luc)

    def thu_hoi(self, cookie, quyen, target, *, rang):
        with self.mo() as (db, u, luc):
            return thiet_bi.thu_hoi(db, u, cookie, quyen, target, rang, luc)

    def quan_ly(self, cookie, quyen, viec, than):
        from tram.passkey.quan_ly import thuc_hien
        with self.mo() as (db, u, luc):
            return thuc_hien(db, u, cookie, quyen, viec, than, luc)
```

### `tram/passkey/quan_ly.py`

```python
"""Kết quả bền theo người/mã; không lưu mã mời rõ, không cấp lại khi mất phản hồi."""
from tram.passkey import thiet_bi
from tram.passkey.chinh_sach import rang_buoc
from tram.passkey.thao_tac import rang_ma


def thuc_hien(db, u, cookie, quyen, viec, than, luc):
    ma = than.get('ma_thao_tac')
    if not isinstance(ma, str) or not ma or len(ma) > 128:
        raise ValueError('Thiếu mã thao tác')
    path = '/api/passkey/' + viec
    rang = rang_buoc(path, than)
    thiet_bi.can_r(db, u, cookie, quyen, rang, luc)
    rang_ma(db, u, path, than)
    cu = db.execute('SELECT * FROM ket_qua WHERE ma=? AND nguoi=?', (ma, u['id'])).fetchone()
    if cu:
        if viec == 'thu-hoi':
            return {'da_thu_hoi': True}
        # Mã chỉ hiện ở phản hồi đầu. Retry trả kết quả đã cấp, kể cả mã đã dùng/hết hạn.
        return {'da_cap': True, 'ma': None}
    if viec == 'moi':
        out = thiet_bi.moi(db, u, cookie, quyen, rang, luc)
    else:
        out = thiet_bi.thu_hoi(db, u, cookie, quyen, than['id'], rang, luc)
    db.execute('INSERT INTO ket_qua VALUES(?,?,?,?)', (ma, u['id'], rang, viec))
    return out
```

### `tram/api/passkey.py`

```python
"""Giao thức WebAuthn: không đưa lỗi schema/thư viện và dữ liệu ceremony ra log."""
import json
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from tram.api.passkey_phu_thuoc import COOKIE, cookie, dich_vu
from tram.passkey.chinh_sach import rang_buoc
from tram.passkey.kho import TuChoi
from tram.passkey.thao_tac import XungDotMa
from starlette.concurrency import run_in_threadpool

router = APIRouter()


async def than_kin(request):
    raw = b''
    async for chunk in request.stream():
        raw += chunk
        if len(raw) > 65536:
            raise HTTPException(413, 'Yêu cầu quá lớn')
    try:
        b = json.loads(raw)
        if not isinstance(b, dict):
            raise ValueError()
        return b
    except (ValueError, UnicodeError):
        raise HTTPException(422, 'Yêu cầu không hợp lệ') from None


def tra(b):
    r = JSONResponse({k:v for k,v in b.items() if k != 'cookie'}, headers={'Cache-Control':'no-store'})
    if 'cookie' in b:
        r.set_cookie(COOKIE, b['cookie'], max_age=28800, path='/', secure=True, httponly=True, samesite='strict')
    return r


@router.get('/api/passkey/trang-thai')
def trang_thai(request: Request):
    return tra(dich_vu(request).trang_thai(cookie(request)))


@router.post('/api/passkey/{viec}')
async def ghi(viec: str, request: Request):
    dv = dich_vu(request)
    b = await than_kin(request)
    return await run_in_threadpool(thuc_hien, viec, request, dv, b)


def thuc_hien(viec, request, dv, b):
    try:
        if viec == 'bat-dau':
            loai = b['loai']
            rang = rang_buoc(b['duong'], b['than']) if loai == 'r' else ''
            out = dv.bat_dau(loai, cookie=cookie(request), ma=b.get('ma',''), rang=rang)
        elif viec == 'ket-thuc':
            out = dv.ket_thuc(b['id'], b['credential'], b.get('ten','Thiết bị'))
        elif viec in ('moi', 'thu-hoi'):
            than = b['than']
            out = dv.quan_ly(cookie(request), b['quyen'], viec, than)
        else:
            raise HTTPException(404, 'Không có thao tác')
        return tra(out)
    except XungDotMa:
        return JSONResponse({'loi':'Mã thao tác đã dùng cho nội dung khác'}, status_code=409,
                            headers={'Cache-Control':'no-store'})
    except TuChoi as e:
        return JSONResponse({'loi':str(e)}, status_code=429 if str(e).startswith('Quá nhiều') else 403,
                            headers={'Cache-Control':'no-store'})
    except (KeyError, TypeError, ValueError, AttributeError):
        return JSONResponse({'loi':'Yêu cầu không hợp lệ'}, status_code=422, headers={'Cache-Control':'no-store'})
```

### `tram/api/passkey_phu_thuoc.py`

```python
"""Cửa người TCP; danh tính mạng là điều kiện phụ, không phải bằng chứng chạm."""
from fastapi import HTTPException, Request
from tram.api.bao_mat import kiem_ghi, HEADER_DANH_TINH
from tram.duong_dan import tram_home
from tram.passkey.chinh_sach import TUYEN, rang_buoc
from tram.passkey.dich_vu import DichVu
from tram.passkey.kho import TuChoi
from tram.passkey.thiet_bi import can_r

COOKIE = '__Host-tram-phien'


def dich_vu(request: Request):
    ch = request.app.state.pt.cau_hinh
    hs = request.headers.getlist(HEADER_DANH_TINH)
    if len(hs) != 1 or len(ch.dai_ca_logins) != 1 or hs[0] != ch.dai_ca_logins[0]:
        raise HTTPException(403, 'Danh tính không hợp lệ')
    headers = dict(request.headers)
    if request.method == "GET":
        headers = {**headers, "origin": f"https://{ch.ten_may_b}", "x-tram": "1"}
    loi = kiem_ghi(headers, ch)
    if loi:
        raise HTTPException(403, loi)
    return DichVu(getattr(request.app.state, 'passkey_path', tram_home()/'passkey.db'), hs[0], ch.ten_may_b)


def cookie(request):
    return request.cookies.get(COOKIE, '')


def can_phien_passkey(request: Request):
    try:
        return dich_vu(request).can_phien(cookie(request))
    except TuChoi:
        raise HTTPException(403, 'Cần phiên passkey') from None


def can_ghi(request: Request):
    dv = dich_vu(request)
    path = request.scope['route'].path
    muc = TUYEN.get(path)
    if muc not in ('N', 'P'):
        raise HTTPException(403, 'Tuyến chưa được cấp quyền người')
    if path in ('/api/chu/estop', '/api/feature/yeu-cau/xem'):
        return
    try:
        if muc == 'P':
            dv.can_phien(cookie(request))
        elif not dv.trang_thai(cookie(request))['thiet_bi']:
            raise TuChoi('Cần đăng ký passkey')
    except TuChoi as e:
        raise HTTPException(403, str(e)) from None


async def luon_cham_lai(request: Request):
    """TM/TC: cùng mã/nội dung cho retry; ledger nghiệp vụ vẫn phải chống thực thi lần hai."""
    than = await request.json()
    from starlette.concurrency import run_in_threadpool
    return await run_in_threadpool(kiem_r, request, than)


def kiem_r(request, than):
    dv = dich_vu(request)
    try:
        rang = rang_buoc(request.url.path, than)
        with dv.mo() as (db, u, luc):
            _, q = can_r(db, u, cookie(request), request.headers.get('x-tram-xac-nhan', ''), rang, luc)
            return {'nguoi': u['id'].hex(), 'rang': rang, 'lap_lai': bool(q['dung'])}
    except (TuChoi, ValueError):
        raise HTTPException(403, 'Cần chạm lại cho thao tác này') from None


async def rang_yeu_cau(request: Request):
    import json
    from tram.passkey.thao_tac import rang_ma, XungDotMa
    if request.scope['route'].path in ('/api/chu/estop', '/api/feature/yeu-cau/xem', '/api/feature/yeu-cau'):
        return
    raw = await request.body()
    from tram.api.passkey_http import han_than
    limit = han_than(request.url.path)
    if limit is not None and len(raw) > limit:
        raise HTTPException(413, 'Yêu cầu quá lớn')
    from starlette.concurrency import run_in_threadpool
    await run_in_threadpool(kiem_rang, request, raw)


def kiem_rang(request, raw):
    import json
    from tram.passkey.thao_tac import rang_ma, XungDotMa
    try:
        than = json.loads(raw)
        if not isinstance(than, dict):
            raise ValueError()
        with dich_vu(request).mo() as (db, u, _):
            rang_ma(db, u, request.url.path, than)
    except XungDotMa:
        raise HTTPException(409, 'Mã thao tác đã dùng cho nội dung khác') from None
    except TuChoi:
        raise HTTPException(403, 'Không có quyền') from None
    except ValueError:
        raise HTTPException(422, 'Yêu cầu không hợp lệ') from None
```

### `tram/api/passkey_http.py`

```python
"""Chặn thân POST trước FastAPI parse: hạn theo tuyến và hạn tổng 5 giây."""
import re
import anyio
from tram.passkey.chinh_sach import TUYEN
from fastapi.responses import JSONResponse


def han_than(path):
    if path.startswith('/api/passkey/'):
        return 65536
    if path.startswith('/api/feature/'):
        return None
    for route, muc in TUYEN.items():
        pattern = re.sub(r'\{[^}]+\}', '[^/]+', route)
        if muc in ('N', 'P') and re.fullmatch(pattern, path):
            return 1024 * 1024 if route.endswith('/chot') else 65536
    return None


class GioiHanThan:
    def __init__(self, app, han=5):
        self.app, self.han = app, han

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http' or scope['method'] != 'POST':
            return await self.app(scope, receive, send)
        limit = han_than(scope.get('path', ''))
        if limit is None:
            return await self.app(scope, receive, send)
        raw = bytearray()
        try:
            with anyio.fail_after(self.han):
                while True:
                    m = await receive()
                    if m['type'] == 'http.disconnect':
                        return
                    chunk = m.get('body', b'')
                    if len(raw) + len(chunk) > limit:
                        return await self.loi(413, scope, receive, send)
                    raw.extend(chunk)
                    if not m.get('more_body', False):
                        break
        except TimeoutError:
            return await self.loi(408, scope, receive, send)
        body = bytes(raw)
        delivered = False

        async def nhan():
            nonlocal delivered
            if delivered:
                return await receive()
            delivered = True
            return {'type':'http.request', 'body':body, 'more_body':False}

        await self.app(scope, nhan, send)

    async def loi(self, status, scope, receive, send):
        await JSONResponse({'loi':'Thân yêu cầu quá lớn hoặc nhận quá hạn'}, status_code=status,
                           headers={'Cache-Control':'no-store'})(scope, receive, send)
```

### `tram/api/bao_mat.py`

```python
"""Danh tính Tailscale + chống CSRF cho API ghi; header an toàn + kiểm Host cho mọi phản hồi (spec 2 §4 mục 2, 3, 6).

Lát 2a tin header `Tailscale-User-Login` do `tailscale serve` gắn. Header này giả được bởi mọi tiến trình
cục bộ gọi thẳng 127.0.0.1 (spec §4 mục 2b) — chấp nhận ở 2a vì chưa có thợ chạy trên B; phải thay trước 3a.
Hành vi header thật kiểm ở Task 26 (chờ #5).
"""
from collections.abc import Mapping

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from tram.api.kenh_ghi import kenh_hop_le
from tram.cau_hinh.tram import CauHinhTram

HEADER_DANH_TINH = "tailscale-user-login"
CSP = ("default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; "
       "font-src 'self'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'")
HEADER_AN_TOAN = [(b"content-security-policy", CSP.encode()), (b"x-content-type-options", b"nosniff"),
                  (b"referrer-policy", b"no-referrer"), (b"x-frame-options", b"DENY")]


def la_dai_ca(headers: Mapping[str, str], ch: CauHinhTram) -> bool:
    login = (headers.get(HEADER_DANH_TINH) or "").strip()
    return bool(login) and login in ch.dai_ca_logins


def kiem_ghi(headers: Mapping[str, str], ch: CauHinhTram) -> str | None:
    if not la_dai_ca(headers, ch):
        return "Chỉ đọc: yêu cầu không mang danh tính Đại ca (Tailscale-User-Login)"
    if headers.get("x-tram") != "1":
        return "Thiếu header X-Tram: 1"
    if not ch.ten_may_b:
        return "Chưa cấu hình ten_may_b trong ~/.tram/cau-hinh.yaml — từ chối mọi thao tác ghi"
    if headers.get("origin") != f"https://{ch.ten_may_b}":
        return "Origin không khớp máy B"
    return None


def _header(request) -> dict[str, str]:
    return {k.lower(): v for k, v in request.headers.items()}


def yeu_cau_danh_tinh(request: Request) -> None:
    if not kenh_hop_le(request):
        raise HTTPException(status_code=403, detail="API ghi chỉ nhận qua kênh đã xác thực (cach_ly.kenh_ghi)")
    if len(request.headers.getlist(HEADER_DANH_TINH)) > 1:
        raise HTTPException(status_code=403, detail="Nhiều header danh tính — từ chối")
    loi = kiem_ghi(_header(request), request.app.state.pt.cau_hinh)
    if loi:
        raise HTTPException(status_code=403, detail=loi)


async def yeu_cau_ghi(request: Request) -> None:
    from tram.api.passkey_phu_thuoc import can_ghi, rang_yeu_cau
    from starlette.concurrency import run_in_threadpool
    await run_in_threadpool(can_ghi, request)
    await rang_yeu_cau(request)


def la_dai_ca_yeu_cau(request: Request) -> bool:
    return (kenh_hop_le(request) and len(request.headers.getlist(HEADER_DANH_TINH)) == 1
            and la_dai_ca(_header(request), request.app.state.pt.cau_hinh))


def host_hop_le(ch: CauHinhTram, cong: int) -> frozenset[str]:
    """Host trình duyệt được dùng: localhost (cổng tram-api) và tên máy B qua `tailscale serve` (Task 26 bước 7.4)."""
    ds = {f"127.0.0.1:{cong}", f"localhost:{cong}"}
    if ch.ten_may_b:
        ds |= {ch.ten_may_b.lower(), f"{ch.ten_may_b.lower()}:443"}
    return frozenset(ds)


class GiuaAnToan:
    """ASGI thuần: Host lạ → 421 (chống DNS rebinding đọc API); mọi phản hồi mang CSP chặt + header an toàn."""

    def __init__(self, app, *, host: frozenset[str]):
        self.app, self.host = app, host

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        da_gui = False

        async def gui(m):
            nonlocal da_gui
            if m["type"] == "http.response.start":
                hs = [*m.get("headers", []), *HEADER_AN_TOAN]
                if scope["path"].startswith("/api/passkey/") or scope["path"] == "/":
                    hs = [(k, v) for k, v in hs if k.lower() != b"cache-control"]
                    hs.append((b"cache-control", b"no-store"))
                da_gui, m = True, {**m, "headers": hs}
            await send(m)

        host = dict(scope["headers"]).get(b"host", b"").decode("latin-1").lower()
        if host not in self.host:
            return await JSONResponse({"loi": "Host không hợp lệ"}, status_code=421)(scope, receive, gui)
        try:
            await self.app(scope, receive, gui)
        except Exception:
            # ServerErrorMiddleware (ngoài cùng) gửi 500 trần không header; tự gửi trước để có CSP.
            # Ném lại vẫn đúng: nó thấy phản hồi đã bắt đầu nên không gửi lần hai, chỉ ném tiếp cho uvicorn ghi log.
            if not da_gui:
                await JSONResponse({"loi": "Lỗi máy chủ"}, status_code=500)(scope, receive, gui)
            raise


def them_header_an_toan(app: FastAPI, ch: CauHinhTram, *, cong: int) -> None:
    app.add_middleware(GiuaAnToan, host=host_hop_le(ch, cong))
```

### `tram/api/app.py`

```python
"""tram-api (spec 2 §3, §7). Chỉ chạy qua `tram api` — nghe 127.0.0.1 (tram/cli_dich_vu.py)."""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from tram.api import doi_ngu, ghep, luong, noi_bo, tho, tho_them, tuyen_chu, tuyen_doc, tuyen_ghi, tuyen_nho, usage
from tram.api import cai_dat, tong_quan, tuyen_yeu_cau, van_phong
from tram.api.bao_mat import them_header_an_toan
from tram.api.passkey import router as passkey_router
from tram.api.phu_thuoc import PhuThuocApi
from tram.api.tuyen_giao import router as tuyen_giao
from tram.beads.bd import KhongThayBead, LoiBd
from tram.nho.khach import LoiNhoKhach
from tram.suy.lam_sach import lam_sach
from tram.thao_tac.loi import ChuaHoTro, KhongHopLe, KhongThay, XungDot

MA_LOI = {XungDot: 409, KhongHopLe: 422, ChuaHoTro: 501, KhongThay: 404, KhongThayBead: 404, LoiBd: 502,
          LoiNhoKhach: 503}
CAC_TUYEN = (tuyen_doc.router, tuyen_ghi.router, tuyen_chu.router, tuyen_nho.router, luong.router, tho.router,
             noi_bo.router, doi_ngu.router, usage.router, tho_them.router, ghep.router)
CAC_TUYEN += (passkey_router,)
CAC_TUYEN += (tuyen_giao,)                     # 4a-2: GET /api/giao-viec
CAC_TUYEN += (van_phong.router,)               # 2c: GET /api/van-phong
CAC_TUYEN += (cai_dat.router,)                 # 2f: GET /api/cai-dat, /api/san-sang (chỉ Đại ca)
CAC_TUYEN += (tong_quan.router,)               # 2f: GET /api/tong-quan
CAC_TUYEN += (tuyen_yeu_cau.router,)           # 4d: POST /api/feature/yeu-cau[/xem] — máy A gửi, B tạo feature


def _xu_ly(ma: int):
    async def xu_ly(request: Request, loi: Exception) -> JSONResponse:
        return JSONResponse({"loi": lam_sach(str(loi), 500)}, status_code=ma)
    return xu_ly


def tao_app(pt: PhuThuocApi, *, cong: int = 7700) -> FastAPI:
    app = FastAPI(title="tram-api", docs_url=None, redoc_url=None, openapi_url=None)
    app.state.pt = pt
    from tram.api.passkey_http import GioiHanThan
    app.add_middleware(GioiHanThan)
    them_header_an_toan(app, pt.cau_hinh, cong=cong)          # CSP + Host (spec 2 §4 mục 6)
    for loai, ma in MA_LOI.items():
        app.add_exception_handler(loai, _xu_ly(ma))
    for r in CAC_TUYEN:
        app.include_router(r)
    if pt.thu_muc_tinh is not None:      # mount sau cùng: /api/* khớp trước
        app.mount("/", StaticFiles(directory=pt.thu_muc_tinh, html=True), name="tinh")
    return app
```

### `frontend/src/api.js`

```javascript
// Gọi tram-api. POST ghi gắn X-Tram (chống CSRF — spec §4 mục 3) và ma_thao_tac + expected_version (§12.3).
export function taoMaThaoTac() {
  return crypto.randomUUID()
}

export function thanGhi(noiDung, version, ma = taoMaThaoTac()) {
  return { ...noiDung, ma_thao_tac: ma, expected_version: version ?? '' }
}

async function xuLy(r) {
  let than = {}
  try {
    than = await r.json()
  } catch {
    than = {}
  }
  if (!r.ok) {
    const loi = new Error(than.loi || (typeof than.detail === 'string' ? than.detail : `Lỗi HTTP ${r.status}`))
    loi.status = r.status
    throw loi
  }
  return than
}

export async function doc(duongDan) {
  return xuLy(await fetch(duongDan, { headers: { Accept: 'application/json' } }))
}

export async function ghi(duongDan, than, hienThi) {
  than = structuredClone(than)
  hienThi = structuredClone(hienThi || moTaGhi(duongDan, than))
  const gui = async () => xuLy(await fetch(duongDan, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-Tram': '1' },
    body: JSON.stringify(than),
  }))
  try { return await gui() } catch (e) {
    if (e.status !== 403 || e.message !== 'Cần phiên passkey') throw e
    const { nghiLe } = await import('./passkey.js')
    await nghiLe('phien', { hienThi })
    return gui()
  }
}

export async function guiPasskey(path, body) {
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), 15000)
  try {
    const r = await fetch('/api/passkey/' + path, { method: body ? 'POST' : 'GET',
      credentials: 'same-origin', cache: 'no-store', signal: controller.signal,
      headers: { 'Content-Type': 'application/json', 'X-Tram': '1' },
      body: body ? JSON.stringify(body) : undefined })
    const b = await r.json()
    if (!r.ok) {
      const e = new Error(b.loi || b.detail || 'Chưa xác nhận — thử lại')
      e.status = r.status
      throw e
    }
    return b
  } finally { clearTimeout(timer) }
}

export function moTaGhi(duong, than = {}) {
  const ten = { chot: 'Chốt việc', duyet: 'Duyệt việc', 'tra-loi': 'Trả lời quyết định',
    'tiep-tuc': 'Tiếp tục trạm', bat: 'Bật khe', 'cau-dao-dong': 'Đóng cầu dao',
    xoa: 'Xoá ký ức', deploy: 'Deploy', 'tu-deploy': 'Bật tự deploy',
    'lenh-deploy': 'Sửa lệnh deploy' }
  const parts = String(duong).split('/').filter(Boolean)
  if (duong === '/api/nho/xoa') {
    return { hanhDong: 'Xoá ký ức', dich: `Ký ức ${String(than.id || '').slice(0, 64)}` }
  }
  return { hanhDong: ten[parts.at(-1)] || 'Xác nhận thay đổi', dich: parts.slice(1, -1).join(' / ') || 'Trạm' }
}
```

### `frontend/src/passkey.js`

```javascript
import { guiPasskey } from './api.js'
// Không ghi mã, cookie hay ceremony vào storage, URL hoặc console.
let hoi = async () => { throw new Error('Chưa mở được hộp xác nhận') }
export function datHoi(fn) { hoi = fn }
export function doc64(s) {
  return Uint8Array.from(atob(s.replace(/-/g, '+').replace(/_/g, '/')), c => c.charCodeAt(0)).buffer
}
export function ghi64(b) {
  return btoa(String.fromCharCode(...new Uint8Array(b))).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')
}
export function tuyChon(o) {
  const r = { ...o, challenge: doc64(o.challenge) }
  if (o.user) r.user = { ...o.user, id: doc64(o.user.id) }
  for (const k of ['allowCredentials', 'excludeCredentials']) {
    if (o[k]) r[k] = o[k].map(c => ({ ...c, id: doc64(c.id) }))
  }
  return r
}
export function phanHoi(c) {
  const response = {}
  for (const k of ['clientDataJSON', 'attestationObject', 'authenticatorData', 'signature', 'userHandle']) {
    if (c.response[k] !== undefined) response[k] = c.response[k] === null ? null : ghi64(c.response[k])
  }
  return { id: c.id, rawId: ghi64(c.rawId), type: c.type, response }
}
export const goiPasskey = guiPasskey
export async function nghiLe(loai, them = {}, deps = {}) {
  them = structuredClone(them)
  const hienThi = Object.freeze({
    hanhDong: String(them.hienThi?.hanhDong || 'Xác nhận thao tác').slice(0, 100),
    dich: String(them.hienThi?.dich || them.duong || 'Phiên trình duyệt này').slice(0, 300),
  })
  if (!await hoi({ loai, hienThi })) throw new Error('Đã huỷ xác nhận')
  const goi = deps.goi || goiPasskey
  const credentials = deps.credentials || globalThis.navigator?.credentials
  if (!credentials) throw new Error('Trình duyệt chưa hỗ trợ passkey; dùng browser hoặc thiết bị khác')
  const o = await goi('bat-dau', { loai, ...them })
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), 120000)
  try {
    const method = loai === 'dang-ky' ? 'create' : 'get'
    const c = await credentials[method]({ publicKey: tuyChon(o.publicKey), signal: controller.signal })
    if (!c) throw new Error('Đã huỷ')
    return await goi('ket-thuc', { id: o.id, credential: phanHoi(c), ten: them.ten })
  } catch {
    throw new Error('Chưa xác nhận — thử lại. Đại ca có thể chọn thiết bị khác trong hộp trình duyệt.')
  } finally { clearTimeout(timer) }
}
let dangCho = null
export function boQuanLy() { dangCho = null }
export async function quanLy(viec, than, hienThi) {
  const key = JSON.stringify([viec, than])
  if (!dangCho || dangCho.key !== key) {
    dangCho = { key, than: structuredClone(than), hienThi: structuredClone(hienThi), quyen: null }
  }
  const cho = dangCho
  const gui = () => goiPasskey(viec, { than: cho.than, quyen: cho.quyen })
  if (cho.quyen) {
    try {
      const out = await gui()
      if (dangCho === cho) boQuanLy()
      return out
    } catch (e) {
      if (e.status !== 403 || !['Cần phiên passkey', 'Cần chạm lại cho thao tác này'].includes(e.message)) throw e
      cho.quyen = null
    }
  }
  const tt = await goiPasskey('trang-thai')
  if (!tt.con_giay) await nghiLe('phien', { hienThi: cho.hienThi })
  const { quyen } = await nghiLe('r', { duong: '/api/passkey/' + viec, than: cho.than, hienThi: cho.hienThi })
  cho.quyen = quyen
  const out = await gui()
  if (dangCho === cho) boQuanLy()
  return out
}
export function hienPhien(tt) {
  if (!tt?.thiet_bi.length) return 'Chưa có passkey'
  return tt.con_giay > 0 ? `Đã xác nhận, còn ${Math.ceil(tt.con_giay / 60)} phút` : 'Cần xác nhận passkey'
}
```

### `frontend/src/menu.js`

```javascript
// Menu sidebar 9 mục theo mockup (app.js MENU, D20). Phân luồng đã bỏ (D18). Ký ức giữ đường /nho, /ky-uc là bí danh
// (D38) — menu trỏ /ky-uc như mockup. Đường dẫn ở đây phải khớp tuyen.js.
export const MENU = [
  { ma: 'tong-quan', ten: 'Tổng quan', duong: '/tong-quan' },
  { ma: 'du-an', ten: 'Dự án', duong: '/du-an' },
  { ma: 'van-phong', ten: 'Văn phòng', duong: '/van-phong' },
  { ma: 'cong-viec', ten: 'Công việc', duong: '/cong-viec' },
  { ma: 'doi-ngu', ten: 'Đội ngũ AI', duong: '/doi-ngu' },
  { ma: 'ky-uc', ten: 'Ký ức', duong: '/ky-uc' },
  { ma: 'usage', ten: 'Usage & chi phí', duong: '/usage' },
  { ma: 'phe-duyet', ten: 'Phê duyệt', duong: '/phe-duyet', dem: true },
  { ma: 'cai-dat', ten: 'Cài đặt', duong: '/cai-dat' },
]
const BI_DANH = { '/nho': '/ky-uc', '/': '/tong-quan' }

// Mục menu của một đường dẫn (bỏ query); đường lạ → null.
export function mucCua(duong) {
  const p = String(duong || '/').split('?')[0].replace(/\/+$/, '') || '/'
  const goc = BI_DANH[p] ?? p
  return MENU.find((m) => goc === m.duong || goc.startsWith(`${m.duong}/`)) ?? null
}

export function tenTrang(duong) {
  if (String(duong).split('?')[0].replace(/\/+$/, '') === '/tai-khoan/thiet-bi') return 'Thiết bị'
  return mucCua(duong)?.ten ?? 'Ben Station'
}
```

### `frontend/src/thanh/HopPasskey.vue`

```vue
<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { datHoi } from '../passkey.js'
const hop = ref(null), yeuCau = ref(null)
let traLoi = null, nutCu = null
function dong(ok) {
  hop.value?.close()
  const tra = traLoi; traLoi = null; yeuCau.value = null
  nutCu?.focus(); tra?.(ok)
}
onMounted(() => datHoi(async yc => {
  if (traLoi) return false
  nutCu = document.activeElement
  yeuCau.value = yc
  const ket = new Promise(resolve => { traLoi = resolve })
  await nextTick(); hop.value.showModal()
  return ket
}))
onUnmounted(() => { dong(false); datHoi(async () => false) })
</script>
<template>
  <dialog ref="hop" class="pk-hop the" aria-labelledby="pk-tieu-de" @cancel.prevent="dong(false)">
    <h2 id="pk-tieu-de">Chạm Touch ID để xác nhận</h2>
    <p v-if="yeuCau?.loai === 'r'">Thao tác này luôn cần chạm lại, kể cả khi phiên còn hạn.</p>
    <p v-else-if="yeuCau?.loai === 'dang-ky'">Tạo passkey cho Đại ca trên thiết bị này.</p>
    <p v-else>Cho phép thao tác nguy hiểm trên trình duyệt này trong 8 giờ.</p>
    <div v-if="yeuCau" class="pk-tom-tat">
      <strong>{{ yeuCau.hienThi.hanhDong }}</strong>
      <p>{{ yeuCau.hienThi.dich }}</p>
    </div>
    <p>Trên Windows: dùng Windows Hello hoặc khoá USB có xác minh người dùng.</p>
    <p>Để dùng điện thoại, chọn “Thiết bị khác” trong hộp của trình duyệt rồi quét QR ở đó.</p>
    <div class="hang-nut">
      <button class="nut" autofocus @click="dong(false)">Huỷ</button>
      <button class="nut chinh" @click="dong(true)">Tiếp tục xác nhận</button>
    </div>
  </dialog>
</template>
<style scoped>
.pk-hop { max-width: 620px; padding: 30px; border: 1px solid var(--vien); border-radius: 16px; }
.pk-hop::backdrop { background: color-mix(in srgb, var(--chu) 40%, transparent); }
.pk-tom-tat { padding: 14px; background: var(--nen-3); border-radius: 8px; }
.hang-nut { display: flex; justify-content: end; gap: 10px; margin-top: 20px; }
</style>
```

### `frontend/src/trang/ThietBi.vue`

```vue
<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { capNhat } from '../quyen_passkey.js'
import { goiPasskey, nghiLe, quanLy, boQuanLy, hienPhien } from '../passkey.js'
const tt = ref(null), ma = ref(''), ten = ref(''), moi = ref(''), loi = ref(''), ban = ref(false)
let hanMa, yeuCauMoi = null, yeuCauThu = null
const gio = t => t ? new Date(t * 1000).toLocaleString('vi-VN', { timeZone: 'Asia/Ho_Chi_Minh' }) : 'Chưa dùng'
async function tai() { tt.value = await goiPasskey('trang-thai'); capNhat(tt.value) }
async function lam(fn) {
  if (ban.value) return
  ban.value = true; loi.value = ''
  try { await fn(); await tai() } catch (e) { loi.value = e.message }
  finally { ban.value = false }
}
async function dangKy() {
  const code = ma.value; ma.value = ''
  await lam(() => nghiLe('dang-ky', { ma: code, ten: ten.value }))
}
async function them() {
  await lam(async () => {
    moi.value = ''
    yeuCauMoi ||= { ma_thao_tac: crypto.randomUUID() }
    const r = await quanLy('moi', yeuCauMoi, { hanhDong: 'Thêm thiết bị', dich: 'Tài khoản Đại ca' })
    yeuCauMoi = null
    if (!r.ma) throw new Error('Yêu cầu đã cấp mã. Nếu mất mã, bấm Thêm thiết bị để tạo yêu cầu mới.')
    moi.value = r.ma
    clearTimeout(hanMa); hanMa = setTimeout(() => { moi.value = '' }, 600000)
  })
}
async function thu(k) {
  await lam(async () => {
    if (yeuCauThu?.id !== k.id) yeuCauThu = { id: k.id, ma_thao_tac: crypto.randomUUID() }
    await quanLy('thu-hoi', yeuCauThu,
      { hanhDong: 'Thu hồi thiết bị và các phiên của nó', dich: `${k.ten} (${k.id})` })
    yeuCauThu = null
  })
}
onMounted(() => lam(async () => {}))
onUnmounted(() => { boQuanLy(); yeuCauMoi = null; yeuCauThu = null; ma.value = ''; moi.value = ''; clearTimeout(hanMa) })
</script>
<template>
  <div class="dau-trang"><div><div class="duong-dan">Đại ca / Thiết bị đã đăng ký</div>
    <h1>Thiết bị</h1><p>Cửa ghi dashboard bằng passkey</p></div></div>
  <p v-if="loi" role="alert" class="loi-chung">{{ loi }}</p>
  <section class="the pk-bao">
    <strong>{{ hienPhien(tt) }}</strong>
    <p v-if="tt && !tt.thiet_bi.length">Chưa có passkey: chỉ TẠM DỪNG và Estop. Đăng ký bên dưới để mở cửa ghi.</p>
    <p>Thêm hoặc thu hồi luôn cần chạm lại. Tin ban đêm được gom gửi buổi sáng.</p>
    <p v-if="tt?.cho_gui">Cảnh báo đang chờ gửi: {{ tt.cho_gui }}</p>
    <button v-if="tt?.thiet_bi.length && !tt.con_giay" class="nut" :disabled="ban"
      @click="lam(() => nghiLe('phien'))">Xác nhận phiên 8 giờ</button>
  </section>
  <section v-if="tt?.thiet_bi.length" class="the">
    <div class="pk-hang"><h2>Thiết bị đã đăng ký <span class="chip">{{ tt.thiet_bi.length }}</span></h2>
      <button class="nut chinh" :disabled="ban" @click="them">Thêm thiết bị</button></div>
    <div class="bang-cuon"><table class="bang"><thead><tr><th>Tên gợi nhớ</th><th>Đăng ký</th>
      <th>Dùng gần nhất</th><th>Thao tác</th></tr></thead><tbody>
      <tr v-for="k in tt.thiet_bi" :key="k.id"><td>{{ k.ten }}</td><td>{{ gio(k.tao) }}</td><td>{{ gio(k.dung) }}</td>
        <td><button class="nut nguy" :disabled="ban || tt.thiet_bi.length <= 1" @click="thu(k)">Thu hồi</button></td>
      </tr></tbody></table></div>
    <p>Một passkey đồng bộ có thể dùng trên nhiều máy; thu hồi sẽ mất quyền trên mọi bản sao cùng passkey.</p>
    <p v-if="tt.thiet_bi.length <= 1">Không thể thu hồi passkey cuối ở đây; dùng khôi phục trên máy B.</p>
  </section>
  <section v-if="moi" class="the pk-bao" aria-live="polite"><h2>Mã mời thiết bị</h2>
    <code class="pk-lenh">{{ moi }}</code><p>Dùng một lần, hết hạn 10 phút. Nhập ở trang Thiết bị trên máy mới.</p>
    <p>Không gửi vào chat, chụp ảnh hay lưu mã. QR xác thực bằng điện thoại do trình duyệt cung cấp.</p>
    <button class="nut" @click="moi = ''">Ẩn mã</button></section>
  <div class="pk-luoi">
    <section class="the"><span class="pk-buoc">BƯỚC 1 · TẠI MÁY B</span><h2>Lấy mã đăng ký</h2>
      <p>Đại ca mở Terminal trên máy B, chạy lệnh rồi làm theo hướng dẫn.</p>
      <code class="pk-lenh">tram chu passkey cap-ma</code><p>Mã dùng một lần, hết hạn 10 phút.</p></section>
    <form class="the" @submit.prevent="dangKy"><span class="pk-buoc">BƯỚC 2 · TRÊN THIẾT BỊ NÀY</span>
      <h2>Đăng ký cho Đại ca</h2><p>Thiết bị cần dùng đúng tài khoản Tailscale của Đại ca.</p>
      <label class="pk-truong">Mã từ máy B hoặc thiết bị cũ<input v-model="ma" type="password"
        autocomplete="off" required :disabled="ban"></label>
      <label class="pk-truong">Tên gợi nhớ<input v-model="ten" maxlength="80" required :disabled="ban"></label>
      <button class="nut chinh" :disabled="ban">Tạo passkey</button></form>
  </div>
  <section class="the"><h2>Mất hết thiết bị hoặc nghi bị lộ?</h2>
    <p>Đại ca mở Terminal trên máy B. Gõ dong-y sẽ thu hồi mọi passkey, phiên, mã cũ.</p>
    <code class="pk-lenh">tram chu passkey khoi-phuc</code></section>
</template>
<style scoped>
.the { padding: 26px; margin-bottom: 18px; }
.pk-luoi { display: grid; grid-template-columns: 1fr 1.1fr; gap: 18px; }
.pk-truong { display: flex; flex-direction: column; gap: 7px; margin: 16px 0; }
.pk-truong input { padding: 12px; border: 1px solid var(--vien); border-radius: 8px; font: inherit; }
.pk-lenh { display: block; padding: 14px; background: var(--nen-lenh); color: var(--chu-lenh); border-radius: 8px; overflow-wrap: anywhere; }
.pk-hang { display: flex; justify-content: space-between; gap: 16px; align-items: center; }
.pk-bao { background: var(--nen-canh-bao); }
.bang-cuon { overflow-x: auto; }
@media (max-width: 1100px) { .pk-luoi { grid-template-columns: 1fr; } }
</style>
```

- [ ] **Step 4 — kiểm lại toàn chuỗi**, gồm test cửa socket đã bị bỏ sót:

```bash
UV_NO_SYNC=1 UV_CACHE_DIR=/tmp/passkey-uv-cache tests/chan_host/chay.sh -q tests/test_passkey*.py tests/test_kenh_ghi.py tests/test_api_dieu_phoi.py
cd frontend && npm run kiem && npm run build && npm run kiem-dist
```

- [ ] **Step 5 — không commit.** Trong phiên **viết/kiểm plan bằng mã tạm**, hoàn nguyên đúng file thử của phiên;
  chỉ giữ tài liệu được giao. Trong phiên **triển khai sản phẩm theo plan**, giữ mã và test đã triển khai để QC,
  không hoàn nguyên chúng theo ghi chép phiên viết plan. Không merge main hoặc ghi Beads trong phiên review này.

## Kiểm chứng phiên sửa vòng 1 — 18/10/2026

- HEAD đầu phiên `067215e`, cây sạch. Không merge main; chỉ đọc quyết định D152–D155 tại checkout chính.
- Áp lại trên bản xuất HEAD sạch: **100 khối mã/diff, 79 file**, mọi diff qua `git apply --check`, kết quả
  khớp từng byte với cây kiểm thử. Hunk Q2 đã sửa để áp được. Các con số 81/70 ở trên chỉ là lịch sử.
- Python tích hợp: **226 passed, 1 deselected**, gồm `tests/test_passkey*.py`, `tests/test_api*.py` và
  `tests/test_kenh_ghi.py -k 'not chay_hai_cong_that_qua_unix_socket'`. Ca loại ra cần bind socket thật.
  Bộ bổ sung Q7 sau siết schema payload/marker verifier: **17 passed**. Nhật ký chặn mọi lượt: **0 dòng mới**.
- Frontend: **114 passed, 0 failed**; `npm run kiem`, `npm run build`, `npm run kiem-dist` đạt. Còn cảnh báo
  chunk 3D lớn và dynamic import đã có static import; không phải lỗi build. SSR Q1 thử cả lỗi thiếu import
  và render được sau sửa; chưa thay kiểm browser/CSP/focus/bố cục thật.
- Toàn repo: đã chạy runner rồi chủ động ngắt sau lỗi môi trường lặp; **133 passed, 29 failed**, kết thúc
  `KeyboardInterrupt` sau 181.26s. Không gọi lượt này là toàn bộ xanh, không cộng số này vào 226.
  Các lỗi báo `LoiBanChep: không xác nhận thu hồi cây tiến trình`. Ca đại diện
  `test_cay_bi_doi_sau_khi_chep_thi_moi_truong_khong_ra_ngoai` tái hiện nguyên lỗi trên HEAD sau hoàn nguyên.
- Sandbox đo trực tiếp: `ps -axo pid,ppid,command` → `operation not permitted`; `sysctl kern.proc.all` →
  `Operation not permitted`; socket mới bind `127.0.0.1:0` → `PermissionError [Errno 1]`.
  Trên HEAD, ca transport `test_chay_hai_cong_that_qua_unix_socket` thất bại vì uvicorn không bind được,
  rồi không thấy socket. Hai ca baseline đại diện: **2 failed**, 0 dòng chặn mới; không sửa test để né sandbox.
- Còn phải đo trên môi trường cho phép: toàn repo đầy đủ; browser thật dưới CSP, Touch ID/USB/Windows Hello;
  proxy Tailscale; quyền OS/cookie/CLI và ghi rủi ro D153; Telegram thật và cấu hình D154 do Đại ca tự bật.
- `openspec validate xac-thuc-passkey --strict` đạt; kiểm tài liệu D152–D155/câu hỏi đạt; `git diff --check`
  sạch. Mã áp thử đã hoàn nguyên về HEAD, file mới ngoài plan/spec/báo cáo đã xoá. Không commit/merge/push.

### Architecture checkpoint

Kho quyền vẫn riêng, thêm một bảng kết quả cùng giao dịch; không tiến trình hay dependency mới.
Threadpool là ranh giới HTTP → đồng bộ, mỗi lời gọi tự đóng kết nối; body bị giới hạn trước typed route.
Estop giữ ledger nghiệp vụ riêng, không phụ thuộc kho quyền. Metadata modal không mang payload bí mật.
Rủi ro OS cùng UID vẫn còn theo D153, không tự mở rộng quyền token máy hoặc thay principal trong lát này.

## Phản hồi review Codex vòng 2

Nguồn review: `/Users/dai-ca/Developer/Ben Station/.handover/review-codex-plan/REVIEW-CODEX-passkey-vong2.md`.
Nguồn D152–D155: **chỉ đọc** `/Users/dai-ca/Developer/Ben Station/docs/quyet-dinh/2026-10-18-passkey.md`;
không merge main, không chép đè file quyết định trong worktree. HEAD đầu phiên `6090bef`, cây sạch.
Mục này thay trạng thái CHƯA ĐẠT của báo cáo cũ ở phạm vi sửa lỗi offline; chưa thay review độc lập vòng sau.

| Mục | RED thật | Bản sửa và GREEN |
|---|---|---|
| V2-Q1 | `413 == 422` với 20 × 4.000 ký tự; cả ASCII, tiếng Việt và JSON escape ký tự ngoài BMP bị chặn. | `han_than` dùng chung ở middleware và dependency; kiểm payload thật tới `bat_ghi: false`, biên đúng hạn/quá 1 byte và chậm trên app thật. |
| V2-Q2 | Test reviewer cho thấy retry thêm dòng `ma_ghep`, huỷ dòng cũ. Test phạm vi D155 nhận `200 == 404`. | Bỏ endpoint cấp mã khỏi lát, không tạo module `passkey_ghep.py`; thử cùng/khác đích trả 404, bảng mã và số sự kiện không đổi. CLI cũ vẫn đóng. Không tuyên bố đã làm ledger ghép máy. |
| V2-Q3 | Bridge `2 !== 1` lần hỏi R; thực thi `thu(k)` thật hai lần cho UUID và quyền khác nhau. | Giữ một yêu cầu đang chờ trong RAM, gồm snapshot thân/đích/UUID/quyền. Cùng yêu cầu thử quyền cũ trước; chỉ lỗi hết phiên/quyền mới xác nhận lại. Test Vue runtime, đổi đích, hết phiên và lỗi nghiệp vụ xanh. |
| V2-Q4 | Bỏ sửa metadata: nhận `['nho','nho']` thay hai ID ký ức. | Áp nguyên sửa reviewer ở Task 13; test hai ID, huỷ không gửi lại, không lộ marker mã thao tác xanh. |
| V2-N1 | Tiêm lỗi threadpool trước `entered`: `TimeoutError` và `Task exception was never retrieved`. | Kiểm task đã kết thúc trong vòng chờ có hạn, `finally` giải phóng event và thu task; test nhận đúng ValueError gốc. Các ca async có hạn ngoài cùng. |
| V2-N2 | Kiểm tài liệu: `AssertionError: Thiếu phản hồi/số đo vòng 2`. | Header và mục này phân biệt lịch sử, số đo phiên sửa, cổng chưa đo; kiểm D152–D155/câu hỏi xanh. |

### Hợp đồng phạm vi dung lượng (V2-Q1)

- Cửa mới `/api/passkey/*`: 65.536 byte, 5 giây tổng trước parse. `than_kin` giữ cùng trần.
- Tuyến N/P trong `TUYEN`, trừ hai tuyến feature: 65.536 byte; riêng `/api/bead/{du_an}/{bead_id}/chot`
  là 1.048.576 byte. `ThanChot` cho 80.000 ký tự; JSON escape ngoài BMP tốn tối đa 12 byte/ký tự
  (960.000 byte), còn chỗ cho envelope. Các thân N/P còn lại tối đa 4.000 ký tự chính (<48.000 byte
  khi escape), cộng metadata có giới hạn. Hạn HTTP tính cả whitespace; không cam kết nhận whitespace vô hạn.
- Hai tuyến feature và cửa M/thợ **không thuộc middleware nhận body mới**. `phieu` được kiểm khối 32 KiB
  ở `doc_phieu`; bàn giao được kiểm 64 KiB ở `kiem_cau_truc`. Envelope `ThanBao.loi_ban_giao` có chuỗi
  không giới hạn độ dài, nên không suy ra trần toàn request từ trần khối bàn giao. Giữ hợp đồng hiện có;
  không áp một trần mới lên giao thức thợ/phiếu trong lát passkey và không tuyên bố chúng đã có hạn HTTP.
- Test app thật gửi phiếu và báo thợ hợp lệ với JSON >64 KiB (whitespace hợp lệ), đi đến nghiệp vụ:
  phiếu tạo đúng một lần, báo thợ trả `luot-cu`. Không mock xác thực/schema để vượt cửa.
- Middleware vẫn chặn sớm trước FastAPI ở các cửa nó sở hữu; `rang_yeu_cau` dùng cùng hàm chọn hạn,
  không còn trần 64 KiB thứ hai trên tuyến chốt. Biên và timeout không dựa Content-Length tin từ client.

### Vòng đời yêu cầu UI (V2-Q3)

Một yêu cầu đang chờ kết quả nằm trong RAM; cùng thao tác/thân dùng lại quyền, không mở modal trước retry.
Mất mạng hoặc phản hồi không xác định giữ yêu cầu. Server trả thành công thì xoá; đổi đích/nội dung là yêu cầu
mới. Component giữ UUID thu hồi qua lỗi, xoá sau thành công, và xoá yêu cầu/quyền khi unmount. Không storage.
403 nghiệp vụ (ví dụ passkey cuối) không tự mở ceremony; chỉ `Cần phiên passkey` hoặc `Cần chạm lại cho thao tác này`
cho phép xin quyền mới. Phiên mới vẫn giữ UUID/thân để server ledger trả kết quả cũ, không tạo lại tác dụng.
Test browser giả chỉ kiểm giao thức client; test SQLite/HTTP vòng 1 tiếp tục kiểm ledger thật.

### TDD cho bản sửa vòng 2

**Files:** các bản toàn file cuối Task 13 đã chứa GREEN Q1/Q3/Q4/N1; Task 12 đã bỏ cấp mã HTTP Q2.
Thêm năm file test nguyên văn dưới đây. Không triển khai mã trung gian Task 1–12 ra máy thật.
**Interfaces:** `han_than(path) -> int | None`; `quanLy(viec, than, hienThi)` giữ quyền theo snapshot;
`boQuanLy()` xoá RAM khi rời màn; endpoint `ghep-ma` đóng. Không đổi schema kho nghiệp vụ.

- [ ] Áp test dưới đây lên mã trước sửa để tái hiện các RED trong bảng; N1 dùng hạn bảo vệ 0,2 giây
  để lỗi của chính test không treo runner. Test tài liệu dùng script cuối mục.
- [ ] Áp bản GREEN nguyên văn Task 12/13 trong file này. Không tạo `tram/api/passkey_ghep.py`.
- [ ] Chạy Python qua runner và frontend như lệnh cuối mục; không commit.

### `tests/test_passkey_review_v2.py`

```python
import json
from contextlib import closing

from api_gia import DAI_CA, tao_app_gia
from asgi_gia import goi
from tram.api.than import ThanChot
from tram.phieu.kho import KhoPhieu


def test_chot_than_hop_le_lon_van_den_kiem_bat_ghi(tmp_path):
    app, pt = tao_app_gia(tmp_path, {})
    pt.cac_du_an = lambda: ['hr']
    pt.bat_ghi = lambda _: False
    body = {'ma_thao_tac': 'v2-chot-001', 'expected_version': '',
            'tra_loi': ['a' * 4000 for _ in range(20)]}
    ThanChot.model_validate(body)
    assert len(json.dumps(body).encode()) > 65536
    r = goi(app, 'POST', '/api/bead/hr/hr-1/chot', headers=DAI_CA, json_body=body)
    assert r.status == 422
    assert 'bat_ghi: false' in r.json()['loi']


def test_cap_ma_ghep_dong_ke_ca_co_phien_va_retry(tmp_path):
    app, pt = tao_app_gia(tmp_path, {})
    pt.mo_kho_phieu = lambda: KhoPhieu(tmp_path / 'ghep-v2.db')
    with closing(pt.mo_kho_phieu()) as kho:
        from tram.phieu.ma_ghep import LUOC_DO_GHEP
        kho.db.executescript(LUOC_DO_GHEP)
        before = kho.db.execute('SELECT * FROM ma_ghep').fetchall()
        events = kho.db.execute("SELECT count(*) FROM su_kien").fetchone()[0]
    for may in ('C2', 'C2', 'D2'):
        r = goi(app, 'POST', '/api/passkey/ghep-ma', headers=DAI_CA,
                json_body={'may_id': may, 'ma_thao_tac': 'v2-ghep-001'})
        assert r.status == 404
        assert 'ma' not in r.json()
    with closing(pt.mo_kho_phieu()) as kho:
        assert kho.db.execute('SELECT * FROM ma_ghep').fetchall() == before
        assert kho.db.execute("SELECT count(*) FROM su_kien").fetchone()[0] == events
```

### `tests/test_passkey_body_v2.py`

```python
import asyncio
import json
import pytest
from api_gia import DAI_CA, tao_app_gia
from asgi_gia import goi
from tram.api.than import ThanChot


def raw_app(app, raw, *, slow=False):
    async def wrapped(scope, receive, send):
        scope = {**scope, 'headers': [*scope['headers'], (b'content-type', b'application/json')]}
        async def nhan():
            if slow:
                await asyncio.sleep(.05)
            return {'type':'http.request', 'body':raw, 'more_body':False}
        await app(scope, nhan, send)
    wrapped.state = getattr(app, 'state', None)
    return wrapped


@pytest.mark.parametrize('char,escaped', [('a',False), ('ệ',False), ('😀',True)])
def test_chot_max_schema_qua_ca_hai_lop(tmp_path, char, escaped):
    app, pt = tao_app_gia(tmp_path,{})
    pt.cac_du_an=lambda:['hr']; pt.bat_ghi=lambda _:False
    body={'ma_thao_tac':'v2-chot-max','expected_version':'','tra_loi':[char*4000]*20}
    ThanChot.model_validate(body)
    raw=json.dumps(body,ensure_ascii=escaped).encode()
    assert 65536 < len(raw) < 1024*1024
    r=goi(raw_app(app,raw),'POST','/api/bead/hr/hr-1/chot',headers=DAI_CA)
    assert r.status == 422 and 'bat_ghi: false' in r.json()['loi']


@pytest.mark.parametrize('path,limit',[('/api/passkey/bat-dau',65536),('/api/bead/hr/hr-1/chot',1048576)])
def test_han_tren_app_truoc_parse(tmp_path,path,limit):
    app,_=tao_app_gia(tmp_path,{})
    assert goi(raw_app(app,b' '*limit),'POST',path,headers=DAI_CA).status == 422
    r=goi(raw_app(app,b' '*(limit+1)),'POST',path,headers=DAI_CA)
    assert r.status == 413 and r.headers['cache-control']=='no-store'
    from tram.api.passkey_http import GioiHanThan
    limited=GioiHanThan(app,han=.01)
    assert goi(raw_app(limited,b'{}',slow=True),'POST',path,headers=DAI_CA).status == 408


def test_phieu_hop_le_tren_64k_khong_bi_chan(tmp_path):
    from api_yeu_cau_gia import mo_app, than, XEM, TAO, dau
    app,_,bd,_=mo_app(tmp_path)
    for path,body in [(XEM,than()),(TAO,{**than(),'dau_xem':dau()})]:
        raw=json.dumps(body).encode()+b' '*70000
        r=goi(raw_app(app,raw),'POST',path,headers=DAI_CA)
        assert r.status == (200 if path==XEM else 201)
    assert bd.so_lan_tao()==1


def test_bao_tho_hop_le_tren_64k(tmp_path):
    from tho_api_gia import tao_tram
    from tram.phieu.bao import ThanBao
    t=tao_tram(tmp_path)
    # moc không có ban_giao, chuỗi giao_id hợp lệ nhưng không tồn tại: cửa nghiệp vụ 409.
    body={'khe_id':'B/claude-1','giao_id':'khong-co','luot':1,'loai':'moc','request_id':'body-v2-001'}
    ThanBao.model_validate(body)
    raw=json.dumps(body).encode()+b' '*70000
    r=goi(raw_app(t.app,raw),'POST','/api/tho/bao',headers={'Authorization':'Bearer '+t.token['B']})
    assert r.status == 409 and r.json() == {'ly_do':'luot-cu'}
```

### `tests/test_passkey_cho_v2.py`

```python
import asyncio
import pytest
from test_passkey_http_v1 import test_ngat_client_khong_nhan_doi_giao_dich as chay_ngat


def test_threadpool_loi_truoc_entered_khong_treo(tmp_path, monkeypatch):
    import starlette.concurrency
    async def hong(*args):
        raise ValueError('threadpool chưa khởi động')
    monkeypatch.setattr(starlette.concurrency, 'run_in_threadpool', hong)
    run = asyncio.run
    monkeypatch.setattr(asyncio, 'run', lambda coro: run(asyncio.wait_for(coro, .2)))
    with pytest.raises(ValueError, match='threadpool chưa khởi động'):
        chay_ngat(tmp_path, monkeypatch)
```

### `frontend/tests/passkey-review-v2.test.mjs`

```javascript
import test from 'node:test'
import assert from 'node:assert/strict'
import { ghi } from '../src/api.js'
import { datHoi, quanLy } from '../src/passkey.js'

test('V2-Q3: retry kết quả mời đã mất không bắt chạm R lần hai', async () => {
  const oldFetch = globalThis.fetch
  const oldNavigator = Object.getOwnPropertyDescriptor(globalThis, 'navigator')
  const b = new Uint8Array([1, 2]).buffer
  const seen = [], writes = []
  datHoi(async q => { seen.push(q); return true })
  Object.defineProperty(globalThis, 'navigator', { configurable: true, value: {
    credentials: { get: async () => ({ id: 'AQI', rawId: b, type: 'public-key',
      response: { clientDataJSON: b, authenticatorData: b, signature: b } }) },
  } })
  globalThis.fetch = async (path, args) => {
    const body = args.body ? JSON.parse(args.body) : null
    let result
    if (path.endsWith('/trang-thai')) result = {con_giay: 3600, thiet_bi: [{}]}
    else if (path.endsWith('/bat-dau')) result = {id: 'hoi', publicKey: {challenge: 'AQI'}}
    else if (path.endsWith('/ket-thuc')) result = {quyen: 'quyen-test'}
    else if (path.endsWith('/moi')) {
      writes.push(body)
      if (writes.length === 1) throw new TypeError('Mất phản hồi sau commit giả lập')
      result = {da_cap: true, ma: null}
    } else assert.fail('Tuyến ngoài kịch bản')
    return {ok: true, status: 200, json: async () => result}
  }
  try {
    const body = {ma_thao_tac: 'v2-moi-001'}
    const display = {hanhDong: 'Thêm thiết bị', dich: 'Tài khoản Đại ca'}
    await assert.rejects(quanLy('moi', body, display), /Mất phản hồi/)
    assert.deepEqual(await quanLy('moi', body, display), {da_cap: true, ma: null})
    assert.deepEqual(writes[0], writes[1])
    assert.equal(seen.filter(q => q.loai === 'r').length, 1)
  } finally {
    globalThis.fetch = oldFetch
    if (oldNavigator) Object.defineProperty(globalThis, 'navigator', oldNavigator)
    else delete globalThis.navigator
    datHoi(async () => false)
  }
})

test('V2-Q4: xoá ký ức hiển thị đúng ID, huỷ không gửi lại', async () => {
  const oldFetch = globalThis.fetch, seen = [], sent = []
  globalThis.fetch = async (path, args) => {
    sent.push(JSON.parse(args.body))
    return {ok: false, status: 403, json: async () => ({detail: 'Cần phiên passkey'})}
  }
  datHoi(async q => { seen.push(q); return false })
  try {
    for (const id of ['ky-uc-a', 'ky-uc-b']) {
      await assert.rejects(ghi('/api/nho/xoa', {
        id, ma_thao_tac: 'marker-private', expected_version: '',
      }), /huỷ/)
    }
    assert.deepEqual(seen.map(q => q.hienThi.dich), ['Ký ức ky-uc-a', 'Ký ức ky-uc-b'])
    assert.ok(seen.every(q => q.hienThi.hanhDong === 'Xoá ký ức'))
    assert.ok(!JSON.stringify(seen).includes('marker-private'))
    assert.equal(sent.length, 2)
  } finally {
    globalThis.fetch = oldFetch
    datHoi(async () => false)
  }
})

test('V2-Q3: quyền hết hạn mới xin lại; lỗi nghiệp vụ không hỏi R thêm', async () => {
  const { boQuanLy } = await import('../src/passkey.js')
  const oldFetch = globalThis.fetch, oldNav = Object.getOwnPropertyDescriptor(globalThis, 'navigator')
  const b = new Uint8Array([1,2]).buffer, seen = [], writes = []
  let round = 0
  datHoi(async q => {seen.push(q); return true})
  Object.defineProperty(globalThis,'navigator',{configurable:true,value:{credentials:{
    get:async()=>({id:'AQI',rawId:b,type:'public-key',response:{clientDataJSON:b,authenticatorData:b,signature:b}}),
  }}})
  globalThis.fetch = async(path,args) => {
    const body = args.body && JSON.parse(args.body)
    let result, status = 200
    if(path.endsWith('trang-thai')) result = {con_giay:round ? 0 : 300,thiet_bi:[{}]}
    else if(path.endsWith('bat-dau')) result = {id:'hoi',publicKey:{challenge:'AQI'}}
    else if(path.endsWith('ket-thuc')) result = {quyen:'q-' + seen.length}
    else if(path.endsWith('thu-hoi')) {
      writes.push(body); round++
      if(round===1) throw new TypeError('Mất mạng')
      if(round===2) { status=403; result={loi:'Cần phiên passkey'} }
      else if(round===3) result={da_thu_hoi:true}
      else { status=403; result={loi:'Không thể thu hồi passkey cuối cùng — khôi phục tại máy B'} }
    } else assert.fail(path)
    return {ok:status===200,status,json:async()=>result}
  }
  try {
    const body={id:'a',ma_thao_tac:'expiry-001'}, display={hanhDong:'Thu hồi',dich:'Máy A'}
    await assert.rejects(quanLy('thu-hoi',body,display),/Mất mạng/)
    assert.deepEqual(await quanLy('thu-hoi',body,display),{da_thu_hoi:true})
    assert.deepEqual(writes[0],writes[1])
    assert.deepEqual(writes[0].than,writes[2].than)
    assert.deepEqual(seen.map(q=>q.loai),['r','phien','r'])
    await assert.rejects(quanLy('thu-hoi',{id:'b',ma_thao_tac:'expiry-002'},display),/cuối cùng/)
    const count=seen.length
    await assert.rejects(quanLy('thu-hoi',{id:'b',ma_thao_tac:'expiry-002'},display),/cuối cùng/)
    assert.equal(seen.length,count)
  } finally {
    boQuanLy(); globalThis.fetch=oldFetch
    if(oldNav) Object.defineProperty(globalThis,'navigator',oldNav)
    else delete globalThis.navigator
    datHoi(async()=>false)
  }
})
```

### `frontend/tests/passkey-thu-runtime.test.mjs`

```javascript
import test from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { parse, compileScript } from '@vue/compiler-sfc'
import { createRenderer } from 'vue'
import { datHoi } from '../src/passkey.js'

test('V2-Q3: thu(k) hai lần sau mất phản hồi giữ UUID và R; đổi đích tạo mới', async () => {
  const source = await readFile(new URL('../src/trang/ThietBi.vue', import.meta.url), 'utf8')
  const { descriptor } = parse(source)
  let code = compileScript(descriptor, { id: 'thu-runtime' }).content
  code = code.replace(/from (['"])(.*?)\1/g, (all, q, name) =>
    `from '${name.startsWith('.') ? new URL('../src/trang/' + name, import.meta.url).href : import.meta.resolve(name)}'`)
  const { default: component } = await import('data:text/javascript;base64,' + Buffer.from(code).toString('base64'))
  const oldFetch = globalThis.fetch, oldNav = Object.getOwnPropertyDescriptor(globalThis, 'navigator')
  const b = new Uint8Array([1, 2]).buffer, writes = [], seen = []
  datHoi(async q => { seen.push(q); return true })
  Object.defineProperty(globalThis, 'navigator', { configurable: true, value: { credentials: {
    get: async () => ({id:'AQI',rawId:b,type:'public-key',response:{clientDataJSON:b,authenticatorData:b,signature:b}}),
  } } })
  globalThis.fetch = async (path, args) => {
    const body = args.body && JSON.parse(args.body)
    let result
    if (path.endsWith('trang-thai')) result = {con_giay:3600,thiet_bi:[{id:'a'},{id:'b'}]}
    else if (path.endsWith('bat-dau')) result = {id:'hoi',publicKey:{challenge:'AQI'}}
    else if (path.endsWith('ket-thuc')) result = {quyen:'q-' + seen.length}
    else if (path.endsWith('thu-hoi')) {
      writes.push(body)
      if (writes.length === 1) throw new TypeError('Mất phản hồi sau commit')
      result = {da_thu_hoi:true}
    } else assert.fail(path)
    return {ok:true,status:200,json:async()=>result}
  }
  let vm
  const setup = component.setup
  component.setup = (props, ctx) => { vm = setup(props, ctx); return vm }
  component.render = () => null
  const renderer = createRenderer({ createComment:()=>({}), insert:()=>{}, remove:()=>{}, parentNode:()=>null,
    nextSibling:()=>null })
  const app = renderer.createApp(component)
  try {
    app.mount({})
    await new Promise(resolve => setImmediate(resolve))
    await vm.thu({id:'a',ten:'Máy A'})
    await vm.thu({id:'a',ten:'Máy A'})
    assert.deepEqual(writes[0], writes[1])
    assert.equal(seen.filter(q=>q.loai==='r').length, 1)
    await vm.thu({id:'b',ten:'Máy B'})
    assert.notEqual(writes[2].than.ma_thao_tac, writes[0].than.ma_thao_tac)
    assert.equal(writes[2].than.id, 'b')
  } finally {
    app.unmount(); globalThis.fetch = oldFetch
    if (oldNav) Object.defineProperty(globalThis,'navigator',oldNav)
    else delete globalThis.navigator
    datHoi(async()=>false)
  }
})
```

### Kiểm tài liệu N2 và quyết định đã chốt

Chạy từ gốc worktree bằng `python3`; mã này chỉ đọc plan, không là test sản phẩm:

```python
from pathlib import Path
p=Path('docs/plans/2026-10-18-lat-passkey.md').read_text()
assert '## Phản hồi review Codex vòng 2' in p, 'Thiếu phản hồi/số đo vòng 2'
assert 'Review vòng 2: CHƯA ĐẠT' not in p[:1000], 'Header còn chứng nhận bản trước sửa'
q=p.split('## Câu hỏi cho Đại ca',1)[1].split('\n## ',1)[0]
assert 'Không còn câu hỏi quyết định' in q
for d in range(152,156): assert f'D{d}' in q
assert 'ps' in p and 'sysctl' in p and 'PermissionError' in p
print('N2/D152–D155: PASS')
```

### Lệnh kiểm và phạm vi bằng chứng phiên sửa vòng 2

```bash
UV_NO_SYNC=1 UV_CACHE_DIR=/tmp/passkey-uv-cache tests/chan_host/chay.sh -q tests/test_passkey*.py tests/test_api*.py tests/test_kenh_ghi.py tests/test_ghep_may.py tests/test_do_dai_ma.py -k 'not chay_hai_cong_that_qua_unix_socket'
cd frontend && npm run kiem && npm run build && npm run kiem-dist
```

- Baseline chọn lọc trên HEAD trước áp: **18 passed** (`test_api_ghi`, `test_api_yeu_cau`, `test_ghep_may`),
  0 dòng chặn mới. Không lấy số baseline toàn repo của phiên trước làm số đo phiên này.
- Bản cuối: **242 passed, 1 deselected** (ca socket thật), **0 dòng chặn mới**, 0 điểm mù, 12 push giả lập,
  không push thật. Gồm toàn bộ test passkey, API, cửa ghi, ghép máy và trần độ dài mã.
- Frontend bản cuối: **118 passed, 0 failed**, `npm run kiem`, build và `kiem-dist` đạt. Cảnh báo chunk 3D lớn
  và dynamic/static import vẫn còn; không thay bằng chứng browser/CSP runtime.
- Đã xuất HEAD vào thư mục tạm và áp lại toàn chuỗi **103 khối / 83 file**: mọi diff qua `git apply --check`,
  mọi file kết quả khớp từng byte với cây vừa kiểm. Một lượt tích hợp ban đầu thiếu hunk test socket vòng 1
  trả 422 thay 403; sau áp đúng hunk đã có trong plan thì xanh. Không sửa sản phẩm để né test này.
- Toàn repo chạy `tests/chan_host/chay.sh -q --maxfail=3`: **131 passed, 3 failed**, dừng sau ba lỗi
  `LoiBanChep: không xác nhận thu hồi cây tiến trình` ở `test_ban_chep.py`; **0 dòng chặn mới**.
  Không gọi đây là toàn bộ xanh. Cần chạy đủ bộ trên môi trường cho phép trước triển khai.
- Đo sandbox trong phiên này: `ps -axo pid,ppid,command` → `operation not permitted`;
  `sysctl kern.proc.all` → `Operation not permitted`; bind socket mới `127.0.0.1:0` →
  `PermissionError [Errno 1] Operation not permitted`. Không xin vượt sandbox.
- Ca `test_chay_hai_cong_that_qua_unix_socket` chạy riêng trên mã áp thử: **1 failed, 1 warning**,
  uvicorn không bind được, không có socket. Không đổi assertion hay đánh dấu skip để gọi xanh.
- Sau hoàn nguyên mã thử về HEAD, chạy lại hai ca đại diện bản chép + socket: **2 failed, 1 warning**,
  cùng lỗi thu hồi cây tiến trình và bind localhost; **0 dòng chặn mới**. Đây là bằng chứng baseline
  tái hiện hạn chế sandbox, không phải bỏ qua hồi quy.
- Q4 được rollback riêng phần mô tả ID để đo RED rồi khôi phục bản reviewer, không chỉ chạy xanh một lần.
  N2 có phép kiểm tài liệu RED/GREEN thật; không gán “test sản phẩm” cho kiểm Markdown.
- Chưa đo: Touch ID/Windows Hello/USB/QR thật, HTTPS Tailscale/cookie, browser với CSP/focus/bố cục,
  quyền DB/profile/TTY/CLI và Telegram thật. D153 chấp nhận rủi ro còn truy cập nhưng không chứng nhận cách ly;
  D154 vẫn do Đại ca tự bật 23:00–07:00. Không đổi cấu hình thật, không commit/merge/push/ghi Beads.

- Hoàn nguyên tất cả mã/test áp thử; chỉ giữ plan, một scenario spec theo D155 và `KET-QUA-CODEX.md`.
  OpenSpec strict, kiểm tài liệu quyết định và `git diff --check` đạt. Không commit.

### Architecture checkpoint vòng 2

Không thêm dependency, tiến trình hay schema nghiệp vụ. Hạn HTTP mới chỉ thuộc cửa passkey/dashboard,
không áp ngầm lên giao thức thợ và phiếu. Đóng cấp mã ghép HTTP tránh giao dịch nửa chừng xuyên hai kho;
endpoint cùng nút dashboard thuộc lát sau theo D155. Client giữ một yêu cầu/quyền trong RAM, xoá khi rời màn.
Rủi ro cùng UID giữ nguyên theo D153. Test chữ ký giả/ASGI và Vue runtime không chứng minh cổng OS/browser.

## Kết luận review Codex vòng 3/3 — CUỐI

**KẾT LUẬN: ĐẠT** — ở mức plan triển khai, không phải chứng nhận code đã triển khai hoặc cổng đã mở.
Đã đối chiếu V2-Q1…Q4, N1, N2 với mã nguyên văn cuối Task 13, spec và mã nền thực tế trong worktree.
Không còn phát hiện Chặn/Quan trọng chưa xử lý trong phạm vi lát này. Báo cáo chi tiết:
`REVIEW-CODEX-passkey-vong3.md` ở gốc worktree. Không dùng tổng số test chưa xác minh làm lỗi plan.

### Chỉnh cuối và thứ tự nghiệm thu

- V2-Q1: trần 1 MiB cho chốt, 64 KiB cho các cửa dashboard còn lại và passkey; feature/M không bị áp
  trần mới. `ThanChot` thật và test JSON ngoài BMP kiểm cả middleware lẫn dependency. Đây là giới hạn
  theo tuyến, không phải chỉ giới hạn giao thức passkey, cũng không phải giới hạn HTTP toàn app.
- V2-Q2: endpoint cấp mã ghép không có nhánh xử lý; CLI cũ đóng. Không còn thiếu ledger ghép máy trong
  phạm vi này; D155 và scenario spec đã đưa cả nút lẫn endpoint sang lát sau.
- V2-Q3/Q4: giữ snapshot/UUID/quyền trong RAM để retry, chỉ xin lại khi phiên/quyền không hợp lệ;
  `thu(k)` được thực thi trong test Vue, mô tả xoá ký ức lấy ID từ snapshot thân.
- V2-N1/N2: chờ event có hạn, nhận lỗi task gốc và giải phóng event trong `finally`; tách rõ số đo tác giả
  với suy luận reviewer. Hạn asyncio chỉ có hiệu lực khi event loop nhường; không phải cách ngắt IO đồng bộ.
- Đã làm rõ TDD của bản hợp nhất và bước hoàn nguyên chỉ dành mã thử lúc viết plan. Không yêu cầu dựng lại
  endpoint ghép lỗi chỉ để có RED. Không thực hiện lệnh, test hoặc hoàn nguyên sản phẩm trong vòng review này.

### Bổ sung coverage vòng 3 — thu hồi mã con và retry sau hạn R

**Files:** thêm nguyên file `tests/test_passkey_review_v3.py` dưới đây khi triển khai; phiên review chỉ ghi
khối mã vào plan. **Không có thay đổi mã sản phẩm mới**: GREEN đã nằm ở `thiet_bi.py` Task 3 và `quan_ly.py`
Task 13. Đây là test bổ sung cho hành vi hiện có, dự đoán xanh ngay; không báo đã đo RED/GREEN.

Test dùng SQLite tạm, chữ ký thật của `KhoaGia`, đồng hồ tiêm và mở lại dịch vụ; không mock verifier,
`can_r`, thu hồi hay ledger. Nó bổ sung bằng chứng backend cho test retry browser vốn thay fetch.

### `tests/test_passkey_review_v3.py`

```python
import pytest
from webauthn.helpers import base64url_to_bytes, bytes_to_base64url
from passkey_gia import KhoaGia
from test_passkey_dich_vu import dv, them, login
from tram.passkey.chinh_sach import rang_buoc
from tram.passkey.dich_vu import DichVu
from tram.passkey.kho import mo_kho, TuChoi


def anh_quan_ly(d):
    with mo_kho(d.path) as db:
        return {bang: [tuple(row) for row in db.execute(f'SELECT * FROM {bang} ORDER BY 1')]
                for bang in ('ma', 'tin', 'ket_qua', 'thao_tac')}


def test_retry_da_commit_sau_120_giay_va_mo_lai_dich_vu(dv):
    k = them(dv)
    c = login(dv, k)['cookie']
    body = {'ma_thao_tac': 'v3-moi-da-commit'}
    rang = rang_buoc('/api/passkey/moi', body)
    q = login(dv, k, 'r', c, rang)['quyen']
    assert dv.quan_ly(c, q, 'moi', body)['ma']
    # Quyền chưa dùng khác phải hết hạn; không được lấy ngoại lệ retry làm quyền ghi mới.
    other = {'ma_thao_tac': 'v3-moi-chua-ghi'}
    q2 = login(dv, k, 'r', c, rang_buoc('/api/passkey/moi', other))['quyen']
    before = anh_quan_ly(dv)
    dv.clock[0] += 120
    reopened = DichVu(dv.path, dv.login, dv.rp, dv.dong_ho)
    assert reopened.quan_ly(c, q, 'moi', body) == {'da_cap': True, 'ma': None}
    with pytest.raises(TuChoi):
        reopened.quan_ly(c, q2, 'moi', other)
    assert anh_quan_ly(reopened) == before
    # Hết phiên tuyệt đối vẫn từ chối, dù ledger còn kết quả đã commit.
    dv.clock[0] += 28800
    with pytest.raises(TuChoi):
        reopened.quan_ly(c, q, 'moi', body)
    assert anh_quan_ly(reopened) == before


def test_thu_hoi_huy_ma_con_ca_khi_da_xin_challenge(dv):
    a, b = them(dv), them(dv)
    ca, cb = login(dv, a)['cookie'], login(dv, b)['cookie']
    invite = {'ma_thao_tac': 'v3-moi-tu-b'}
    qb = login(dv, b, 'r', cb, rang_buoc('/api/passkey/moi', invite))['quyen']
    ma = dv.quan_ly(cb, qb, 'moi', invite)['ma']
    pending = dv.bat_dau('dang-ky', ma=ma)
    third = KhoaGia()
    body = {'ma_thao_tac': 'v3-thu-hoi-b', 'id': bytes_to_base64url(b.id)}
    qa = login(dv, a, 'r', ca, rang_buoc('/api/passkey/thu-hoi', body))['quyen']
    assert dv.quan_ly(ca, qa, 'thu-hoi', body) == {'da_thu_hoi': True}
    before = anh_quan_ly(dv)
    reopened = DichVu(dv.path, dv.login, dv.rp, dv.dong_ho)
    with pytest.raises(TuChoi):
        reopened.ket_thuc(pending['id'], third.tra(
            base64url_to_bytes(pending['publicKey']['challenge']), dang_ky=True))
    with pytest.raises(TuChoi):
        reopened.can_phien(cb)
    with pytest.raises(TuChoi):
        reopened.quan_ly(cb, qb, 'moi', invite)
    with pytest.raises(TuChoi):
        login(reopened, b)
    assert reopened.can_phien(ca)
    assert [k['id'] for k in reopened.trang_thai(ca)['thiet_bi']] == [bytes_to_base64url(a.id)]
    assert anh_quan_ly(reopened) == before
    assert before['ma'] == []
    assert len(before['ket_qua']) == 2
    assert [row[1] for row in before['tin']] == ['them', 'them', 'thu-hoi']
```

Khi triển khai, chạy `tests/chan_host/chay.sh -q tests/test_passkey_review_v3.py` rồi các tập kiểm hiện có
và cả bộ theo §13. Reviewer vòng 3 **không chạy** lệnh này. Sau mỗi assertion từ chối, dữ liệu quản lý không
đổi; test không lấy việc có exception đơn thuần làm bằng chứng không phát sinh tác dụng.

### Cổng còn giữ nguyên

Cổng 1–4 ở trên vẫn bắt buộc: toàn bộ test ở môi trường được phép, HTTPS/cookie, Touch ID/Windows/USB/QR,
browser/CSP/focus/bố cục, quyền OS/TTY/CLI, Telegram và phục hồi backup. D153 giữ quyết định chấp nhận rủi ro;
D154 do Đại ca tự bật; D155 không mở lại CLI ghép. Không có câu hỏi quyết định mới cho Đại ca.

**KẾT LUẬN CUỐI PLAN: ĐẠT (review tĩnh vòng 3/3; chưa chứng nhận triển khai hoặc cổng OS).**
