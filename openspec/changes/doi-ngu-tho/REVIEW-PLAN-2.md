# Review vòng 2 — đội ngũ thợ

20/10/2026 · nhánh `spec/doi-ngu-tho` · HEAD `b5ad194`.
Đọc CHUNG.md, tài liệu vận hành/kiến trúc, toàn change, REVIEW-PLAN-1, plan và mã thật của các luồng liên quan.
QĐ1–QĐ4=A, QĐ5=B giữ nguyên. Theo yêu cầu phiên này, chỉ giữ plan/change/báo cáo;
không hoàn nguyên tài liệu như quy trình cũ trong CHUNG.md, không sửa mã của worktree.

## C1/C2 đã giải thế nào

**C1 — cổng cha riêng cho từng phiếu/lượt/khe.** Task 6 tạo worktree detached và thư mục phiếu trong
một cha 0700 do quản lý sở hữu. Chỉ mở quyền search sau khi chuẩn bị xong. Đóng bằng `chmod -N`
trên cha, xác nhận UID sạch rồi xoá cây/registration Git của đúng lượt; B không gọi đường thu
`lenh_trao_quyen(..., thu=True)` cũ. Không gỡ từng ACL, không chmod/chown file UID khe.

ACL kế thừa cho quản lý đọc/dọn file mới kể cả umask 077. Nếu khe gỡ ACL hoặc dọn không được thì
cổng đóng, giữ phiếu, dừng khe; không nuốt lỗi hay tăng quyền. Cùng phiếu restart giữ bản sửa và
thư viện, không reset/giải nén/cấp ACL lại. Tắt daemon đóng cổng nhưng giữ cây; dừng mềm giữ WIP
trước dọn. Phiếu cũ bị nhịp từ chối sau restart cũng được dọn trước xoá sổ. Đổi code→QC/khe dùng cây mới.
Chỉ thêm một dấu hoàn tất chuẩn bị trong cha quản lý giữ, không thêm registry/quy trình thu từng entry.

**C2 — dùng đúng bundle root đã có cho Uq.** Task 6 tái dùng `deps_root.doc_root/doc_bundle` và
`quan_kiem.cap_deps.cap_deps`: khớp bốn file nguồn, runtime/ABI, hash và giới hạn archive; helper
Python ghim `-I`, hạn 300 giây, giải nén `.venv` và `frontend/node_modules` riêng từng lượt.
Không sửa Uq/policy, không dùng venv/cache nhà hungle, không tải gói. Thiếu/sai bundle hoặc đích không
trống thì không chạy CLI. Task 9 dùng cùng bundle cho runtime quản lý, tạo entrypoint `tram` cục bộ.
Task 6–7 đặt `TRAM_KIEM_DA_CHUAN_BI=1` sau sudo cho cả CLI và kiểm sau xong, tránh bị mất cờ hoặc quay về uv.
Uq vẫn chuẩn bị và kiểm độc lập trong lượt của Uq.

## Phát hiện và sửa, nặng → nhẹ

| Mức | Phát hiện | Đã sửa |
|---|---|---|
| Chặn | C1 không chỉ là entry cấp/thu lệch: chuẩn bị lại cùng phiếu gọi `_don`, commit rồi reset về cha; nhánh nhịp từ chối phiếu cũ còn xoá sổ trước dọn. | Task 6 giữ cây đã sẵn sàng; nối nhánh phiếu cũ vào dọn, chỉ xoá sổ khi thành công. Test Git thật tái hiện mất bản sửa, đổi code→QC, dừng mềm/WIP, tắt daemon, lỗi UID/dọn và retry chuẩn bị dở. |
| Quan trọng | Phép thử chmod trong tmp phát hiện `user:501` không được macOS dịch sang UUID. | Đổi sang `pwd.getpwuid(UID chủ worktree).pw_name`; kiểm lại cú pháp ACL trên tmp và hồi quy quyền. Không nhầm UID người điều khiển S6 với chủ cây. |
| Quan trọng | File của UID khe không tự đọc/dọn được bằng quyền chủ quản lý; prompt `.tram/goi-2.md` tạo sau phải đọc được. | ACL kế thừa riêng cho quản lý theo UID chủ worktree; `.tram` chỉ kế thừa đọc. Test cấu trúc quyền + lỗi PermissionError; S6 bổ sung file/thư mục umask 077, kiểm chủ file, quản lý đọc/xoá và quyền cũ bị chặn. |
| Quan trọng | Worktree có thư viện vẫn chưa đủ nếu runner không nhận cờ sau đổi principal; runtime dùng uv sync vẫn phụ thuộc cache cũ. | Wrapper ở cả hai chỗ chạy; runtime dùng bundle root và entrypoint riêng. Kiểm thật đủ 6 lệnh offline và `uv run --offline --no-sync … tram --help`. |
| Quan trọng | Quyền runtime phụ thuộc umask lúc clone; script S6 tính ACL từ hungle không đọc được thư mục phiếu 700 của manager. | Runtime giữ 700 lúc chuẩn bị, bỏ ghi group/other rồi mới mở đọc. S6 gọi helper quyền bằng UID quản lý; ACL quản lý lấy từ UID chủ worktree, không từ người điều khiển script. |
| Vừa | B đổi cấu trúc cây nhưng bộ dọn bead đóng cũ vẫn quét dạng dự án/nhánh; test cũ báo cáo còn tự commit hoặc nhìn đường cũ nên có thể che lỗi. | B bỏ quét cũ, dọn theo lượt; test kiểm cây thật và dùng đúng cờ báo qua quản lý. Máy từ xa giữ luồng cũ và test riêng. |
| Nhỏ | Bản vá thêm nhánh cleanup làm `vong_khe.py` vượt trần; định dạng khối diff có thể mất dòng context trống. | Đưa dọn phiếu cũ vào module mồ côi hiện có; tất cả file ≤120 dòng. Áp lại từng diff từ plan và so byte, không chỉ kiểm AST. |

Không còn phát hiện chặn code sau lượt rà cuối. Không thêm dependency, daemon, schema, root sudo hay quyền Git cho khe.

## Kiểm chứng

Tất cả mã thử nằm tại `/private/tmp/doi-v2-hz3elsn_/`, ngoài cây mã worktree.
Không gọi Claude/Keychain/sudo/launchd thật; không mạng, commit, bd, push hay merge.

- **RED:** 6 lỗi hành vi C1/C2 trước vá; thêm 3 ca đỏ khi lùi riêng mã cũ (ACL quản lý, phiếu cũ,
  runtime root). Fixture QC đã có `vai=qc` trước ghi nhận RED. Log `red.txt`, `additional-red.txt`.
- **Áp plan:** 45 khối Create/Modify, 51 tệp khác nhau; mọi diff qua `git apply --check` rồi áp,
  AST hợp lệ, nội dung bằng từng byte với bản đã chạy. Bản áp sạch cuối: `final4/`.
- **Hồi quy cuối từ bản áp sạch:** **236 passed, 4 deselected**, gồm toàn bộ test mới, luồng thợ,
  API/cài đặt, ngân sách/quota/cầu dao, dependency G4, trần dòng/vòng import. Log `logs/final4.txt`.
- **Bundle root thật:** digest `4ed173d9a6ed5409fe58fc00fd6ed76e7e83786801f1624d2c58874a909bad0b`.
  Bản sao sạch `offline/` được cấp thư viện bằng helper mới; chạy đủ sáu lệnh mặc định trong
  `du-an/ben-station.yaml`: Python **52 + 29 + 7 passed**; frontend **155 passed**, kiểm an toàn,
  build và kiểm dist đạt. Log `logs/offline-1.txt` đến `offline-6.txt`. Không dùng thư viện nhà hungle.
- **Runtime:** entrypoint sinh theo R1 chạy được với `uv run --offline --no-sync --project … tram --help`;
  cache trỏ tmp, không cài gói. Log `logs/runtime-entry.txt`. Đây là UID reviewer, không phải daemon thật.
- **Cú pháp ACL macOS trong tmp:** UID số bị từ chối; tên tra từ UID chủ cây và toàn bộ lệnh cấp ACL
  mới đều chạy đạt. Test này dùng `nobody` trên cây giả, không đổi UID/không sudo; chưa thay phép đo hai khe thật.
- **Giới hạn sandbox:** thử toàn suite với `--maxfail=40` → **175 passed, 40 failed**, dừng trong nhóm
  thu hồi tiến trình. HEAD chưa vá chạy đối chứng sáu ca (bản chép, bốn ca đã loại, vòng thợ đầy đủ)
  → **6 failed**. Đo riêng `chup_nhan()` bằng Python ghim → `PermissionError [Errno 1] sysctl`.
  Không tính các lỗi này vào verdict; không sửa timeout/test để giả xanh, không tuyên bố toàn suite xanh.
- Mọi lượt qua `tests/chan_host/chay.sh`, **0 dòng chặn mới**. Nhóm cuối ghi **16 điểm mù Python con**:
  helper `-I` cố ý không nạp PYTHONPATH/audithook và fixture cũ. Giữ nguyên ghi nhận này;
  runner không là sandbox tuyệt đối. Git push của fixture đều được giả lập.
- `DO_NOT_TRACK=1 OPENSPEC_TELEMETRY=0 openspec validate doi-ngu-tho --strict` → **valid**;
  binary có sẵn **1.11.0**, không tải bản pin 1.14.0. `git diff --check` sạch.

Skill review giúp rà lại toàn luồng, quyền và đường lỗi; skill kiểm chứng buộc áp lại mã nguyên văn,
đo RED→GREEN, chạy dependency thật và tách lỗi sandbox khỏi lỗi plan.

## Giới hạn trước chạy thật

Phép thử ACL của hai UID, Claude/Keychain/daemon và S7 chưa chạy trong phiên này. Plan đã giữ R4/S6
và R7 để đo file UID khe, đóng quyền, đổi code→QC, retry/dừng mềm và đủ lệnh kiểm dưới hai khe thật.
Đây là cổng vận hành sau code/QC/ghép, không phải chặn thiết kế C1/C2 còn bỏ ngỏ.
Giữ HR, tự merge/deploy tắt; QĐ5-B mở mọi việc đủ điều kiện của ben-station sau các cổng.
Không cho phép chạy sổ tay, mở estop/cổng, bật giao hoặc archive từ báo cáo này.

**ĐẠT để code — C1/C2 đã giải, mã/test nguyên văn khớp mã thật; các cổng chạy thật vẫn giữ nguyên.**
