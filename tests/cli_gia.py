"""CLI GIẢ thay `claude -p` (CHỈ DÙNG TRONG TEST — không bao giờ gọi Claude thật). Đọc kịch bản JSON từ biến
`CLI_GIA_KICH_BAN`: danh sách bước `{"in": {...}}` (in một dòng JSON), `{"in_tho": "…"}`, `{"ngu": giây}`,
`{"ghi": [đường dẫn tương đối cwd, nội dung]}`, `{"chay": [argv…]}` (vd gọi `tram bao`), `{"con": giây}` (sinh tiến
trình cháu ngủ), `{"cho_dung": true}` (chờ thợ gửi tín hiệu dừng), `{"thoat": mã}`.
Ghi stdin nhận được vào `<cwd>/.tram/stdin-<n>.md` để test kiểm gói."""
import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path


def main() -> int:
    vao = sys.stdin.read()
    d = Path(".tram")
    d.mkdir(exist_ok=True)
    n = len(list(d.glob("stdin-*.md"))) + 1
    (d / f"stdin-{n}.md").write_text(vao, encoding="utf-8")
    (d / f"argv-{n}.json").write_text(json.dumps(sys.argv[1:]), encoding="utf-8")
    buoc = json.loads(Path(os.environ["CLI_GIA_KICH_BAN"]).read_text())
    if isinstance(buoc, dict):                                    # kịch bản theo lần chạy: {"1": [...], "2": [...]}
        buoc = buoc.get(str(n), buoc.get("mac_dinh", []))
    for b in buoc:
        if "in" in b:
            print(json.dumps(b["in"], ensure_ascii=False), flush=True)
        elif "in_tho" in b:
            print(b["in_tho"], flush=True)
        elif "ngu" in b:
            time.sleep(b["ngu"])
        elif "cho_dung" in b:
            threading.Event().wait()
        elif "ghi" in b:
            Path(b["ghi"][0]).parent.mkdir(parents=True, exist_ok=True)
            Path(b["ghi"][0]).write_text(b["ghi"][1], encoding="utf-8")
        elif "chay" in b:
            subprocess.run(b["chay"], check=False)
        elif "con" in b:
            subprocess.Popen([sys.executable, "-c", f"import time; time.sleep({b['con']})"])
        elif "thoat" in b:
            return b["thoat"]
    return 0


if __name__ == "__main__":
    sys.exit(main())
