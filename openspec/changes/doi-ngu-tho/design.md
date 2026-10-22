# Thiết kế: dùng phần sẵn có, mở hai khe theo từng bước

Status: `REVIEW`; QĐ1–QĐ4 = A, QĐ5 = B đã chốt. Bằng chứng S2 đỏ 21/10 và QĐ2 sửa ở QUYET-DINH.md; chưa có S2 xanh.

## 1. Đối chiếu bối cảnh và mã

Hai bản bối cảnh nói “10 chỗ chặn”; bảng thực tế có 11 hàng do tách bước bật G7.
Giữ đủ cả 11, không bỏ hàng để khớp số:

| Chỗ chặn | Căn cứ mã tại `19a86c0` | Cách giải / bằng chứng |
|---|---|---|
| Khe 2 | `tram/tho/cau_hinh.py`, `tram/chu/nhom_rieng.py` | User/nhóm riêng, không nhập nhóm staff; Task 1, R1 |
| Cài từng phần | `tram/chu/lenh_tho.py`, `cai_dat_tho.py`, `cai_dat_kiem.py` | `--chi-tho --giu-tat`; không gọi phần kiểm; sổ cài cũ vẫn giữ; Task 1 |
| Đăng ký B | `tram/tho/ke_hoach_dk.py`, `lenh_khe.py`, `tram/chu/cap_ma.py` | Lệnh `dang-ky-b` riêng, không sửa luồng từ xa, không dùng `cap-ma` đã đóng; Task 2 |
| Token máy nền | `tram/tho/lenh_chay.py`, `tram/phieu/may.py` | Pipe vào file 0600 quản lý trên B, đọc trong daemon; lỗi giữ tắt, không tự xoay token; Task 4, R2 |
| Hai đăng nhập Claude | `tram/tho/kiem_cong.py`, `tram/chay_cli/lenh_claude.py`, `principal.py` | setup-token đúng user; wrapper mở file và truyền FD sau sudo; QĐ2, R2 |
| S1/S4/S8 | `tram/han_muc/claude.py`, `tram/chay_cli/bo_cli.py`, `lenh_claude.py` | Không đoán quota; đo headless/quyền/hook bằng CLI thật có ngân sách; R4 |
| S6 khe | `tram/tho/principal_khe.py`, `chuan_bi.py`, `bao.py` | Không trao Git metadata; quản lý chốt commit, settings chỉ đọc; Task 5–7, R4 |
| G5 đúng phạm vi | `tram/tho/vong_khe.py`, `tram/han_muc/claude.py` | Đo nhịp/thu hồi/API/DB cho Claude, không kéo Codex app-server vào; R4/R7 |
| S7 kho/remote | `tram/tho/worktree.py`, `day.py`, `tram/giao_viec/kho_kiem_tao.py` | Alias origin được đối chiếu; kho kiểm chia sẻ chỉ đọc; B dùng kho-tho; R3 |
| Ben Station trước | `tram/tho/kiem_may.py`, `kiem_cong.py`, `tram/giao_viec/noi_that.py` | Lọc kiểm tường minh; giới hạn dự án phía cấp việc, giữ mọi bead đủ điều kiện; Task 3/8 |
| Bật G7 | `tram/cau_hinh/giao_viec.py`, `tram/giao_viec/bo.py`, `du-an/ben-station.yaml` | Đồng bộ checkout API, mở mọi việc đủ điều kiện của ben-station, nạp lại API, đối chiếu nhịp; R6/R7 |

`docs/CURRENT_STATE.md` và `DEPLOY.md` còn các dòng “API/G4 chưa chạy”; không dùng
chúng phủ nhận cập nhật tối 20/10 và lời Đại ca. Không sửa các tài liệu sở hữu
trạng thái trong phiên này. Bản sổ tay bối cảnh còn ghi “reboot chưa đo”; log tối
20/10 đã xác nhận Uq tự lên, nên nợ reboot của **Uq** đã hết. Reboot của **thợ**
vẫn phải đo riêng.

## 2. Token file dưới đúng UID (QĐ2-A sửa 21/10)

Quyết định/bằng chứng do [QĐ2](QUYET-DINH.md) sở hữu; ngoại lệ kiến trúc ở
[ADR-0009](../../../docs/decisions/ADR-0009-quyen-khe-b.md). Plan bổ sung 21/10 thắng
phần token/Keychain trong Task 4/9 và R2/R4/R5 của plan 20/10; phần khác giữ nguyên.

`tram-tho` chỉ đọc token máy B trong nhà lấy từ passwd của UID (không tin HOME/TRAM_HOME).
Mọi caller đã có cấu hình truyền `tren_may_b`; đăng ký B dùng file ngay cả trước tho.yaml.
`nhan-token --may-b` là bootstrap tường minh, máy từ xa giữ Keychain. File lỗi/thiếu không
fallback Keychain. Writer kiểm dạng, dùng dirfd + O_NOFOLLOW trên từng thành phần,
đúng chủ/mode, file thường một hardlink; tmp độc quyền 0600, fsync rồi replace cùng thư mục.
Lỗi trước rename giữ token cũ, không ghi đè đích lạ; không sao lưu giá trị bí mật sang file khác.

Mỗi khe giữ `claude/oauth-token`. Helper Python stdlib trong runtime tin cậy chạy `-I`
**bên trong** principal, kiểm UID từ passwd, chủ/mode/loại file và không credential file.
Helper dựng env từ allowlist sẵn có, tự đặt HOME/CLAUDE_CONFIG_DIR theo UID và số FD;
không nhận đường token/CLI tuỳ ý, exec `/opt/homebrew/bin/claude`. `BIEN_GIU` không thêm
OAuth. Khe từ xa, Codex và lệnh kiểm không đi qua helper token. Auth status, do_nen và
Claude chạy phiếu trên B dùng cùng helper; `san_sang_b` thừa hưởng phép auth mới.

Khảo sát tĩnh CLI 2.1.227 cài tại `/opt/homebrew/bin/claude` (không chạy CLI): hàm nhúng
`HEu` parseInt số FD, đọc `/dev/fd/N`, trim, tối đa 65536 byte và cache; `tA` ưu tiên token
env thường trước FD. `Lgs` có nhánh ghi `/home/claude/.claude/remote/.oauth_token` khi
`CLAUDE_CODE_REMOTE` bật. Wrapper loại biến này cùng các biến auth ngoài allowlist.
SHA256 binary: `7432511ba3be818e01f23f6eef8630d214a8b618451e188c3c7d61a987eef6c7`.
Đây xác nhận đường đọc trong binary, không chứng minh OAuth hợp lệ, auth status hay
headless dưới launchd. S2 kiểm lại phiên bản/hash, FD thực, auth/headless và không lưu thêm credential.

Sổ tay dùng setup-token tương tác chỉ tại Terminal.app, getpass không echo (từ chối khi
không có ô ẩn), stdin vào helper ghi dưới UID khe. Bỏ ACL cũ ở thư mục Claude rồi siết 0700;
file mới 0600. Mode POSIX không chứng minh ACL macOS: S6 bắt buộc đối chứng bằng owner,
thử mở/đóng không đọc nội dung dưới UID quản lý/khe kia và khe→token máy. Chỉ Permission
denied/Operation not permitted là đạt; thiếu đích/lệnh/timeout không kết luận.
Sudoers ALL đang có vẫn cho quản lý đổi UID; giới hạn này phải được chốt theo QĐ2,
không lấy S6 trực tiếp thay phép chống sudo.

Thiếu cấu hình/token/auth: in câu hằng, thoát sạch trước nhận phiếu, không tự xoay token.
Không thêm dependency/daemon. R5 đo reboot không mở khoá; chỉ khi có bằng chứng mới giải
được nợ `bs-2bd.11`. Hết hạn/thu hồi cần setup-token lại có chủ ý, không tự fallback.

Runtime thợ tách khỏi nhà hungle: clone mã đã ghép vào
`/Users/Shared/tram-tho-code`, cấp bundle root đã cài bằng `cap_deps_b` với Python ghim
trong `tram/kiem/toolchain.py`; không gọi uv sync/cache hoặc tải mạng. Tạo entrypoint `tram`
trỏ bản runtime này; giữ thư mục 700 trong lúc chuẩn bị, bỏ ghi của group/other rồi mới mở đọc 755. Hungle giữ quyền ghi runtime; manager/khe chỉ
đọc/chạy. Cấu hình dự án bản runtime trỏ kho thợ và file môi trường test không
bí mật trong runtime. Không cho thợ đi qua nhà hungle để đọc venv/cache cũ.
CLI Claude phải cài ở vị trí dùng chung, đích symlink cũng đọc được; thiếu thì
dừng để chuẩn bị bản cài chính thức, không mở lại nhà Đại ca.

## 3. Cài và đăng ký

Thêm hai cờ vào trình cài cũ: `--chi-tho` không đọc/cài phần tram-kiem;
`--giu-tat` không chạy launchctl. Trình cài vẫn đối soát sổ đã có trước khi
đụng user/nhóm/sudoers/plist. Trước khi cài phải xác nhận daemon thợ đang vắng
và disable; cờ giữ tắt không phải phép tự dừng daemon đang làm việc.

`dang-ky-b --tep <ứng-viên>` chạy dưới tram-tho; xác minh B/loopback/hai user
riêng, chỉ nhận CLI Claude. Không phụ thuộc việc plist đang tồn tại.
Đọc token hiện có → ping kiểm `may_id` → POST toàn bộ hai khe → thay tho.yaml
nguyên tử. Cấu hình cũ được sao lưu kín trước thay; không có bí mật trong YAML.
HTTP đã nhận nhưng mất phản hồi: retry cùng nội dung, `dang_ky_khe` đã idempotent.
HTTP và filesystem không là một giao dịch: nếu POST xong mà ghi file hỏng,
thẻ có thể đã hiện; daemon vẫn tắt, retry sẽ hoàn tất cấu hình. Không giả vờ rollback
được API, không bật khe đang có, không tự cấp token lại.

Token máy lần đầu dùng `cap-token-may B --dong-y` nối trực tiếp `nhan-token`,
chỉ sau sao lưu và xác nhận B không có phiếu hiệu lực. Cấp lại vô hiệu token cũ,
nên không chạy lại bước đó để chữa mọi lỗi. CLI ghép từ xa `cap-ma` đã đóng;
không mở lại hoặc lách passkey.

## 4. Quyền repo: giảm việc phải cho phép

QĐ3-A giữ user riêng và ACL của macOS. Cây mã của từng phiếu có quyền sửa;
gốc worktree chỉ cho thêm mục, không cho xoá mọi con. `.git` và `.tram` được
loại khỏi lệnh cấp ACL; `.git` có deny ghi/xoá, gốc worktree giữ chủ quản lý.
Kho chung, metadata/index/objects/refs không cấp ghi cho khe. Settings/MCP của
phiếu chỉ đọc; chỉ file `hang-doi.jsonl` được append. Không mở quyền cả
`/Users/dai-ca`, `~/.tram`, `.git` hoặc dùng `safe.directory=*`.

Trên B, `tram bao` chỉ dựng báo cáo và append hàng đợi, commit để null. Mốc tạm
giữ trong sổ phiếu, chưa công bố. Sau CLI thoát và `don_khe` chứng minh sạch,
quản lý chốt WIP, tự điền SHA/nhánh/lượt. Phần kiểm lại/QC/công bố không đổi.
Mã báo cáo từ khe dù có SHA cũng không được tin; kết thúc mềm gắn lại SHA vào
bàn giao tạm. Luồng máy từ xa giữ hành vi hiện tại.

**C1 — không thu ACL từng file:** mỗi `(giao_id, luot, khe_id)` có một thư mục cha 0700 do
quản lý giữ; bên trong là worktree detached và thư mục phiếu. Khe chỉ có `search` trên cha,
không sửa/đổi tên cha. Sau chuẩn bị đầy đủ mới mở cổng cha. Kết thúc đóng cổng bằng `chmod -N`
trên đúng cha quản lý sở hữu, xác nhận UID sạch rồi xoá cây và registration Git của đúng lượt.
Không dùng `lenh_trao_quyen(..., thu=True)` cho B; máy từ xa giữ đường cũ.

Cùng phiếu restart giữ cây/bản sửa, không reset HEAD hay thêm ACL/giải nén lần nữa. Dấu `san-sang`
ở cha chỉ phân biệt chuẩn bị đầy đủ với dở dang, không phải chứng nhận an toàn. Chuẩn bị dở →
đóng/dọn trước retry. Tắt daemon giữ cây và phiếu nhưng đóng cổng. Phiếu cũ sau restart bị từ chối
cũng phải dọn trước xoá sổ. Code→QC hay đổi khe dùng cây khác ở đúng SHA cha của phiếu.

File mới vẫn thuộc UID khe. ACL kế thừa cấp quản lý đọc/ghi/dọn, kể cả file do khe tạo với umask 077;
không giả định quản lý có quyền chmod/chown file đó. Nếu khe cố ý gỡ ACL hoặc dọn lỗi, cổng giữ đóng,
phiếu giữ để đối soát và khe dừng, không dùng sudo root. Dừng mềm chốt/giữ WIP theo cơ chế cũ trước dọn.
`.git`/`.tram` không nhận quyền ghi kế thừa của khe; `.tram` cho đọc prompt mới ở lần CLI tiếp theo.

R1 dùng kho/worktree mới, không tự chuyển/xoá cây cũ. R4 thử ghi, rename, symlink `.git`, metadata,
settings, khe khác, file UID khe và thu quyền qua cổng. Một phép lọt là S6 đỏ; chmod thoát 0 không
thay phép kiểm quyền thực tế. R7 đo đổi code→QC và restart/dừng mềm bằng cả hai UID thật.

**C2 — dùng thư viện root sẵn có:** chọn đúng một manifest trong
`/usr/local/tram/deps/ben-station/<digest>/manifest.json` khớp hash `uv.lock`, `pyproject.toml`,
`frontend/package-lock.json`, `frontend/package.json`. Dùng `deps_root.doc_root/doc_bundle` và
`quan_kiem.cap_deps.cap_deps` hiện có, không sửa Uq hay policy của Uq. Helper Python ghim `-I`
chỉ chạy stdlib/mã runtime tin cậy dưới quản lý, có hạn 300 giây; không import/chạy mã worktree.
Helper kiểm runtime/ABI, nguồn không symlink, đích trống, hash/giới hạn archive rồi giải nén
`python-site.tar`/`node-modules.tar` vào `.venv` và `frontend/node_modules` riêng từng lượt.
Không tạo cache chung, không dùng nhà hungle, không tải gói. Runtime quản lý cũng dùng bundle này.

Thiếu bundle, lock/runtime đổi, archive hỏng hoặc đích đã có → không mở cổng/không chạy CLI.
Retry cùng phiếu giữ dependency riêng đã cấp; phiếu mới nhận bản sạch, không dùng lại bản khe trước đã sửa.
Wrapper đặt `TRAM_KIEM_DA_CHUAN_BI=1` **sau sudo** cho CLI và các lệnh kiểm sau xong; runner dùng
`.venv/bin/python` ghim, không quay về uv. Uq vẫn tự tạo lượt kiểm riêng và xác minh lại độc lập.

Phép đo S6 của sổ tay chạy từ hungle để có đối chứng đích thật, còn thao tác
thử chạy dưới từng UID khe. Bộ `tho kiem` cũ có đối chứng Keychain/đường riêng
của hungle từ tram-tho, có thể không kết luận khi quyền đã siết đúng; không
đổi đỏ thành xanh bằng cách bỏ đối chứng. Phép đo mới dùng cùng bộ chấm lỗi
`cham_tham_do`, không coi thiếu lệnh/timeout/đích thiếu là bị chặn.

## 5. Repo nguồn và đường trả commit

Giữ repo làm việc của Đại ca. Kiểm URL `github` đúng `Hungbennn/ben-station`;
`origin` thiếu thì thêm alias cùng URL, khác thì dừng. Không in URL thô vì
URL có thể chứa credential. Repo thợ chỉ clone qua đường cục bộ.

Kho kiểm không checkout đặt tại `/Users/Shared/tram-nguon/ben-station`, do
hungle sở hữu; đường `~/.tram/kho-kiem/ben-station` là symlink do hungle tạo tới
nó. Đây là cùng một kho: luồng `git_kiem.fetch` sẵn có cập nhật origin/main;
không có mirror thứ hai phải tự nhớ cập nhật. Kho thợ phải fetch
`refs/remotes/origin/*` của nguồn sang `refs/remotes/origin/*` của mình; fetch `refs/heads/*` mặc định
chỉ nhận nhánh main cũ của kho không checkout. Chỉ `tram-tho` có ACL đọc/search
nguồn, không quyền ghi; hai khe không được đọc nguồn trực tiếp. Kho chứa mã
riêng tư nhưng không chứa token/file môi trường thật. Nếu kho kiểm đã có thì
dừng để chọn chuyển kho trong kịch bản riêng, không xoá/ghi đè tự động.

Kho thợ `/Users/tram-tho/tram/kho/ben-station` do tram-tho giữ, origin trỏ nguồn
cục bộ. Trạm đọc kho thợ để nhận `tram/luot/<bead>/<luot>`; `cong_bo: lai`,
`kho_tho.B: /Users/tram-tho/tram/kho`. Agent không push. Commit được xác minh
theo SHA/lượt và kiểm lại như trước. Việc tạo PR/push sau này vẫn là cổng S7/G7,
không nằm trong quyền thực hiện của phiên soạn này.

## 6. Phạm vi việc và giao diện

`giao_viec.du_an` là danh sách dự án cho phép tuỳ chọn, không thay `bat_ghi`.
Ben-station đã có `bat_ghi: true` trên main để nhận yêu cầu máy A, độc lập với giao việc.
Sổ tay tắt giao chỉ tắt `giao_viec.bat`, không ghi lại YAML dự án; bật giao có thể đảm bảo `bat_ghi: true`.
`con_phieu_b()` lấy kho từ `tram.duong_dan.tram_home()` (theo `TRAM_HOME`), mở SQLite chỉ đọc.
Cấu hình đợt này là `[ben-station]`; QĐ5-B không có danh sách bead. Thiếu khoá giữ tương thích.
Nguồn `cac_du_an` dùng chung cho tick, chọn trước claim và `con_hop_le` trước cấp; nạp lại API khi đổi.
Giữ ngân sách bead/phiếu, số lần chạy, trần giờ/ngày, quota và cầu dao sẵn có. HR, TM/TC/tự deploy vẫn tắt.

`tho kiem --du-an ben-station` chỉ thu hẹp kiểm repo; không giảm kiểm user,
auth, API/DB, UID hay thu hồi. Tên không ở API bị từ chối. GET Đội ngũ lấy thẻ
từ sự kiện đăng ký: thẻ hiện và trạng thái tắt là đúng. `bat:true` của GET không
phải công tắc giao việc; không dùng query `du_an` của màn hình làm hàng rào.

## 7. Tích hợp ngoài (§15)

| Tích hợp | Hạn / nơi áp | Đại ca thấy khi hỏng | Retry / bí mật |
|---|---|---|---|
| Claude auth tương tác | Đại ca chủ động kết thúc; không chạy trong vòng nền | Terminal của đúng user | Không thu stdout, không tee/script/xtrace; không tự login lại |
| Claude auth status | 30 giây qua runner đang có | “Chưa xác nhận đăng nhập nền” | Không in JSON danh tính; không bật khe |
| Claude headless | ngân sách phiếu; phép thử R4 2 phút | mục S đỏ; thu hồi trước bước tiếp | Có thể tốn lượt; không tự lặp, không lưu prompt thô |
| Token B / Keychain từ xa | B: file cục bộ giới hạn 4096 byte, helper sổ tay 30 giây; Keychain xa giữ hạn cũ | “Chưa xác nhận kho token” | Không tự xoay; stdin/FD, không giá trị trong argv/log |
| API thợ | 10 giây/lời gọi | HTTP hoặc mã lỗi cố định | Đăng ký retry cùng nội dung; không log body/header |
| Git | 60 giây thao tác ngắn, clone/fetch 600 giây | bước repo thất bại | Giữ kho đã có, không xoá; không in URL/output thô |
| sudo/cài/launchctl | 30 giây mỗi lệnh sau xác thực sudo | bước + mã thoát + đường log | Không vô hiệu lỗi, không bootstrap lần hai khi trạng thái không rõ |
| ACL / kiểm UID | lệnh 30 giây, thăm dò qua P1 | S6 đỏ / không kết luận | Không coi timeout là bị chặn; Apple không bị dọn nhầm |

Không thêm registry dịch vụ Apple. Tận dụng bộ lọc Apple/UID và cơ chế thu hồi
đã sửa trong ngày 20/10; không sửa Uq, không giết theo tên. Đích kiểm có thật,
quyền CLI, token file/ACL và reboot cần bằng chứng macOS; test giả chỉ kiểm luồng.

## 8. Đường lui và điều kiện hoàn tất

Tắt `giao_viec.bat`, nạp lại API; tắt hai khe để dừng mềm, đối soát phiếu và
UID; rồi bootout/disable đúng thợ. Giữ Uq chạy. Giữ repo/commit/log để đối soát,
không tự restore DB sau khi đã phát phiếu, không xoá user/Keychain.
Hỏng ở bước nào chỉ retry bước đó sau đối soát. Không tự mở estop/cổng kiểm.

Đạt là hai khe thật, hai tài khoản, có nhịp; mọi việc đủ điều kiện được xét theo QĐ5-B;
ít nhất một chuỗi bằng chứng đi hết kiểm lại và
QC khác khe; S1–S4/S6/S7/S8 có bằng chứng đúng phạm vi. S2 không đạt thì toàn
bộ vận hành vẫn chờ dù spec/plan và test offline đã xong.

## 9. Review vòng 2

C1/C2 đã có mã/test nguyên văn ở Task 6–7 và điều chỉnh sổ tay ở Task 9; không còn là phần bỏ ngỏ.
Kết quả, giới hạn sandbox và kết luận để code: [REVIEW-CODEX.md](../../../REVIEW-CODEX.md).
Đây không phải xác nhận OS: S2/S3/S4/S6/S7/S8 và R7 vẫn bắt buộc sau code/QC/ghép.
