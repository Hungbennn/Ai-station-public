# Chuẩn cài đặt

Project: `ben-station`
Status: `ACTIVE`
Cập nhật: `2026-10-21`

## Mục đích và sở hữu
Sở hữu: chuẩn viết code, nơi đặt giá trị (hardcode hay cấu hình), cách code giữ bí mật, quy tắc dữ liệu,
mã định danh, quy ước kho mã, và **luật đã trả giá** (kèm sự cố thật).
Không sở hữu: luật hành xử của agent, lệnh cấm, bảng kiểm chứng (`AGENT_RULES.md` §11, §13, §14) · ranh giới
module và luồng dữ liệu (`ARCHITECTURE.md`) · trình tự làm một task (`DEVELOPMENT_PLAYBOOK.md`) · luật giao
diện (`DESIGN_SYSTEM.md`) · cài dịch vụ và tên mục Keychain (`DEPLOY.md`).

## Mục tiêu kỹ thuật
- Đọc được trong một lần nhìn: file nhỏ, tên tiếng Việt, mỗi file một việc.
- Mọi hành vi có test chạy offline; không test nào chạm máy thật.
- Hỏng thì đóng (cổng đóng, từ chối), không hỏng thì mở.
- Bí mật không đi qua chỗ nào agent hay log nhìn thấy được.

## Ngăn xếp
Nguồn sự thật là file khai báo, không phải bảng này: `pyproject.toml`, `uv.lock`, `frontend/package.json`.
- **Python ≥ 3.12, `uv`**. Thư viện chính: FastAPI, Uvicorn, LanceDB, MCP SDK, Anthropic SDK, Pydantic, PyYAML.
  Test: pytest 8. Lệnh `tram` = `tram.cli:main`.
- **Frontend:** Vue 3, vue-router (chế độ hash), TresJS + three.js, Vite. Không có thư viện test: test là
  `node --test` trên file `frontend/tests/*.test.mjs`.
- Phiên bản ghi **chính xác** (không `^`) cho phần lớn gói. Thêm gói phải hỏi trước (`AGENT_RULES.md` §11).

## Kiểu code
- **File ≤ 120 dòng, dòng ≤ 120 ký tự Unicode** trong `tram/` — `tests/test_do_dai_ma.py` cưỡng chế; không có
  ngoại lệ file, ngoại lệ dòng gắn với nguyên văn dòng và ghi lý do trong test. File Vue/JS lớn nhất 129 dòng
  (`frontend/src/trang/CongViec.vue`, chưa có test). Sắp vượt thì tách theo việc, không nén chữ vào một dòng.
- **Tên tiếng Việt không dấu**, `snake_case` cho hàm/biến/module, `PascalCase` cho lớp, `HOA_CO_GACH` cho hằng
  (ví dụ `NHAN_QUET`, `KEYCHAIN_NHO`). Chú thích và thông báo cho người đọc viết tiếng Việt có dấu.
- **TDD.** Viết test trước, chạy thấy đỏ đúng lý do, viết mã, chạy thấy xanh, rồi kiểm theo cỡ ở PLAYBOOK §1. Plan trong
  `docs/plans/` dùng dạng theo cỡ ở `DEVELOPMENT_PLAYBOOK.md` §1; chỉ nhánh lớn/cũ cần test và mã nguyên văn.
- **Test không chạm máy thật.** Mỗi test có `TRAM_HOME` tạm (`tests/conftest.py`). Hệ ngoài thay bằng bản giả
  `tests/*_gia.py` (ví dụ `tests/bd_gia.py`, `tests/gh_gia.py`, `tests/git_gia.py`, `tests/cli_gia.py`). Tiến trình
  thật trong test chỉ là `python -c` hay `/bin/sleep` của chính user chạy test, tự thu hồi đúng PID mình tạo.
- **Thông báo lỗi không chép** argv, đường dẫn, stdout/stderr hay chữ do tiến trình con gửi về (review Codex
  đợt 6, Q06; ghi trong Global Constraints của các plan từ đợt 6).
- **Frontend:** cấm chèn HTML thô (`v-html`, `innerHTML`…), cấm `style="…"` tĩnh trong `.vue`, cấm URL ngoài
  (trừ link GitHub); bundle không cần `eval` hay `unsafe-inline`. `frontend/kiem-an-toan.mjs` và
  `frontend/kiem-dist.mjs` cưỡng chế các luật này.

## Quy tắc kiến trúc
Chỉ phần cài đặt; ranh giới và hướng import ở `ARCHITECTURE.md` mục Luật module.
- **Gọi lệnh ngoài luôn có hạn.** Lệnh chạy rồi chờ đi qua các khối trong `tram/kiem/` (`vong_doi.py`,
  `chay_gioi_han.py`, `lenh_ngan.py`): có hạn tuyệt đối, thu hồi cả cây con. Không `subprocess.run` không
  `timeout` (suy từ plan P1, chưa xác nhận là luật chung). Spawn theo hợp đồng sở hữu (`tram/kiem/so_huu.py`): con
  vào danh sách chủ trước mọi lối ra, người gọi thu hồi trong `finally`.
- **Lệnh đổi máy thì liệt kê trước, chờ `dong-y`.** Mẫu `KeHoach` trong `tram/chu/cai_dat.py`: in file sẽ ghi,
  lệnh sẽ chạy, cảnh báo; chỉ thực hiện khi Đại ca gõ `dong-y`. Lệnh cài, gỡ, cấp mã mới đều theo mẫu này.
- **Gỡ chỉ gỡ thứ mình đã tạo.** Cài máy thợ ghi sổ (`tram/chu/so_cai_tho.py`) trước và sau mỗi bước; gỡ
  (`tram/chu/go_cai_dat_tho.py`) chỉ đụng mục sổ ghi đã tạo và còn đúng định danh (UID, sha256, inode). Dịch vụ
  trạm chủ: cài ghi biên nhận sha256 plist, gỡ chỉ theo biên nhận đó (`tram/chu/chung_cu_go.py`).
- **Công tắc lớn mặc định tắt**; đọc cấu hình thiếu khoá thì rơi về giá trị an toàn (tắt, chỉ đọc).
- **Đọc cấu hình chặt:** khoá lạ, sai kiểu, ngoài giới hạn thì báo lỗi, không đoán (`tram/cau_hinh/tram.py`).

## Chính sách hardcode
Thang quyết định ở `AGENT_RULES.md` §14. Bảng dưới chỉ ra **nơi cụ thể** trong repo này:

| Loại giá trị | Đặt ở | Ví dụ |
| --- | --- | --- |
| Hằng kỹ thuật, không ai chỉnh | hằng trong module | nhãn launchd `tram/chu/launchd.py`, cổng 7700 `tram/cli_dich_vu.py` |
| Khác theo máy, không bí mật | `~/.tram/cau-hinh.yaml` | đọc qua `tram/cau_hinh/` (khối nào: `DEPLOY.md`) |
| Khác theo dự án con | `du-an/<ten>.yaml` | `bat_ghi`, nhánh chính, hàng rào (`tram/cau_hinh/du_an.py`) |
| Máy thợ, không bí mật | `~/.tram/tho.yaml` của tài khoản quản lý thợ | `tram/tho/cau_hinh.py` |
| Đường dẫn gốc | biến môi trường `TRAM_HOME`, `TRAM_REPO` | `tram/duong_dan.py` |
| Bí mật | Keychain của tài khoản trạm, **chỉ** ở đó | tên mục là hằng `KEYCHAIN_*` trong code |
| Prompt và quyền theo vai | `vai/` | không nhúng prompt dài trong mã Python |

Giới hạn số (ngưỡng hạn mức, trần lượt chạy) có mặc định trong dataclass và khoảng hợp lệ `GIOI_HAN`
(`tram/cau_hinh/tram.py`); ngưỡng hạn mức thuộc kill list.

## Quy tắc bảo mật
Luật hành xử của agent với bí mật ở `AGENT_RULES.md` §14. Ở đây là cách **code** giữ chúng:
- Bí mật đọc từ Keychain lúc chạy; không đọc từ file, biến môi trường hay đối số.
- Đưa bí mật cho lệnh con qua **stdin**, không qua argv (`ps` thấy argv). Mẫu: `tao_token_nho` trong
  `tram/chu/cai_dat_nho.py`. Tạo xong thì kiểm lại có thật, vì lệnh `security -i` có thể trả 0 khi lệnh con lỗi.
- Không in, không log bí mật, kể cả nhánh lỗi. Token máy chỉ lưu dạng sha256 (`tram/tho/token_may.py`).
- Nội dung bead, bàn giao, ký ức là **dữ liệu không tin cậy**: hiển thị bằng text, bọc trước khi đưa vào prompt,
  không ghi nguyên văn vào log.
- Mọi phản hồi HTTP có CSP chặt và kiểm `Host`; API ghi luôn kiểm danh tính (`tram/api/bao_mat.py`). Test API ghi
  phải có ca **thiếu** và **giả** danh tính.
- Memory lọc phạm vi bằng khớp chính xác, cấm lọc tiền tố; quét bí mật trước khi ghi (`tram/nho/bi_mat.py`).
- Kho SQLite qua `mo_an_toan.py`: tạo với mode 600; siết file có quyền nhóm/người khác về 600 trước khi mở.
  Bản sao qua `ban_sao.py`: file độc quyền 600, thư mục đích 700. `siet_quyen.py` chỉ sửa mục còn bit 0077;
  giữ mục đã kín, bỏ qua `hang-doi/`, `sandbox/`, symlink, file hardlink và mục khác chủ. Không bảo đảm toàn cây
  đúng 700/600 hay ACL đã sạch; `tram_home()` không ép quyền. Cách chạy: `DEPLOY.md` mục 3.

## Quy tắc dữ liệu
Sở hữu dữ liệu và kho nào ai ghi: `PRODUCT_ARCHITECTURE.md`, `ARCHITECTURE.md` mục Hợp đồng chung.
- Kho sự kiện chỉ **ghi thêm**; trạng thái hiển thị tính lúc đọc. Không sửa, không xoá dòng sự kiện.
- Thao tác ghi mang ID để thử lại không tạo trùng.
- Lược đồ DB: hiện trạng ở `ARCHITECTURE.md` mục Hợp đồng chung. Đổi lược đồ thuộc kill list.
- Ghi file trạng thái nguyên tử: ghi file tạm cạnh đích rồi `os.replace` (ví dụ `tram/nho/bao_tri.py`).
- Thời gian lưu dạng ISO; giờ bảo trì tính theo giờ Việt Nam (`GIO_VN` trong `tram/nho/bao_tri.py`).
- Sao lưu kho sự kiện dùng API online backup (`tram/su_kien/sao_luu.py`), không chép file DB đang mở; hạn chụp
  kiểm giữa các bước backup (`ban_sao.py`), không bao trùm ghi/fsync. Không suy rộng sang sao lưu memory.

## Mã định danh
| Thứ | Dạng | Ví dụ |
| --- | --- | --- |
| Việc của repo trạm | `bs-<mã>`, con `bs-<mã>.<n>` | `bs-2bd`, `bs-863.18` |
| Nhánh công bố của trạm | `tram/<bead>` | |
| Nhánh làm việc + worktree | `<phạm vi>/<việc>`, không dấu; worktree `.worktrees/<tên>` | `p1/code`, `docs/khung-docs` |
| Dịch vụ launchd | `vn.tram.<tên>` | `vn.tram.nho` |
| Mục Keychain | `tram-<tên>` | danh sách ở `DEPLOY.md` |
| Khe thợ | `<máy>/<cli>-<n>` | `B/claude-1` |
| Change OpenSpec | kebab-case không dấu | quy ước `OPENSPEC.md` |
| Plan, spec, bàn giao | `YYYY-MM-DD-<chu-de>.md` | `docs/plans/2026-10-17-lat-v2-va-sau-review-dot7.md` |
| Quyết định | `D<số>` (cũ, `docs/quyet-dinh/`), `ADR-XXXX` (mới, `docs/decisions/`) | D53, ADR-0005 |

## Kho mã
- Nhánh chính `main`. Mỗi việc một worktree `.worktrees/<tên>` tạo từ `main`; không làm thẳng trên `main`.
- Commit: `<loại>(<phạm vi>): <mô tả tiếng Việt>` — loại `feat`, `fix`, `docs`, `plan`; ghép là `merge: …`.
  Ghi lát và finding trong ngoặc cuối, ví dụ `(lát 3c, P1 H2)`. Dòng ghi công cuối là model đã viết.
- Git bỏ qua: `.handover/` (gói review, công cụ QC), `.worktrees/`, dữ liệu Dolt trong `.beads/`.
- Không có CI. Kiểm chứng chạy tay theo `AGENT_RULES.md` §13.

## Vận hành agent trên máy thật — luật cứng đã trả giá
Danh sách lệnh cấm ở `AGENT_RULES.md` §11; bảng kiểm chứng ở §13. Mục này giữ **chuyện thật** để không ai
"dọn" các luật đó vì tưởng thừa. Nguồn: `docs/handovers/2026-10-17-ban-giao-phien.md` §5.

**1. Không chạy thật lệnh lịch hay dịch vụ, và không giết tiến trình theo tên — kể cả trong "chạy thử".**
- Sự cố 16/10/2026: một subagent viết plan 3c chạy kịch bản cài cron **dưới chính user `hungle`** của Đại ca.
  `crontab -` treo 120 giây rồi bị giết. Cùng subagent đó dùng `pkill -f` một lần.
- Vì sao nguy: lịch cài dưới user vận hành sẽ chạy lại mãi sau khi agent đã thoát; `pkill -f` giết luôn
  pytest hay dịch vụ của agent khác chạy song song trên cùng máy.
- Đã xử lý: kiểm lại máy (`crontab` trống, `atq` trống, không job launchd lạ). Luật cấm đưa vào
  `.handover/qc/huong-dan-code.md`, memory và `AGENT_RULES.md` §11. Mã harness S6 có chốt `xac_minh_uid`
  (`tram/kiem/danh_tinh.py`) từ chối chạy kịch bản lịch dưới user vận hành.
- Cách kiểm: test dùng bộ chạy giả; bộ test chạy với PATH chặn host, nhật ký chặn phải rỗng (`AGENT_RULES.md` §13).

**2. Subagent commit từng phần, không dồn tới cuối.**
- Sự cố trong phiên 13–17/10/2026: lỗi **429** (hết hạn mức sử dụng) làm **4 subagent dừng giữa chừng**;
  phần chưa commit có nguy cơ mất.
- Vì sao: hạn mức hết bất kỳ lúc nào, agent không kịp viết bàn giao.
- Cách làm: prompt subagent dặn commit sau mỗi bước xanh (bản dở dùng tiêu đề `wip:`), và dừng viết bàn
  giao khi ngữ cảnh gần 600k token (`DEVELOPMENT_PLAYBOOK.md`).

**3. Việc chạm macOS hay CLI ngoài: đo thật và tra cách người khác làm TRƯỚC khi viết plan.**
- Sự cố 21/10/2026 (chạy thật đội ngũ thợ, R4): plan + 3 vòng review offline chọn "đăng nhập Claude trong Keychain
  user riêng". Trong daemon launchd, Keychain mặc định là `System.keychain`, keychain user khoá (36, *User interaction
  is not allowed*) vì mở khoá gắn phiên Terminal → S2 đỏ, phải đổi sang token file. Đây là chuyện quen của dịch vụ nền
  trên macOS và tài liệu Claude Code headless (`setup-token`); spike S1–S4 (`bs-8eh.3`) chưa chạy trước khi code.
- Cách làm: trước plan, chạy vài phép đo nhỏ trên máy thật (đúng ngữ cảnh: launchd/user/phiên) và tra cách các dự án
  công khai giải cùng bài; đề review phải hỏi "người khác làm thế nào, đã đo ở ngữ cảnh thật chưa".

**4. Test của công cụ chạy thật dùng đầu ra THẬT chụp từ máy B, không tự viết mẫu.**
- Sự cố 21/10/2026: `can_tat` chỉ nhận `"vn.tram.tho" => true` (mẫu tự viết theo macOS cũ); macOS 15.6.1 in
  `=> disabled` — repo đã có mẫu thật trong `tests/du_lieu/launchd/`. Cùng đợt: công cụ tự chặn nhà `hungle`/`tram-tho`
  ở R1 rồi chính nó vấp `EACCES` ở R2/R3 (cwd `~`, `Path.exists()` dưới `hungle`) — test giả không có user/quyền thật.
- Cách làm: mẫu đầu ra lệnh hệ thống lấy từ máy thật vào `tests/du_lieu/`; công cụ chạy dưới user khác đặt cwd `/` và
  mọi kiểm đường trong nhà user khác chạy dưới chính user đó.
