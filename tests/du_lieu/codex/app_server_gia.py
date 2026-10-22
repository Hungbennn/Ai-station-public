"""`codex app-server` GIẢ — CHỈ DÙNG TRONG TEST (chạy bằng sys.executable). Mỗi dòng stdin một JSON; ghi lại mọi
tin nhận được + CODEX_HOME vào file $GHI (không có $GHI thì không ghi). CHE_DO: ok | loi | treo | dong | dai (một
dòng 2 MiB không xuống dòng) | lo (lỗi mang nguyên văn $LO, kèm in $LO ra stderr). Hình dạng tin theo hiểu biết hiện
tại — chờ spike S5."""
import json
import os
import sys
import time
from pathlib import Path

MAU = json.loads((Path(__file__).parent / "app_server_rate_limits.json").read_text(encoding="utf-8"))
che_do, ghi = os.environ.get("CHE_DO", "ok"), Path(os.environ.get("GHI", os.devnull))
nhan = [{"CODEX_HOME": os.environ.get("CODEX_HOME")}]
if os.environ.get("GHI_ENV"):                       # test bs-78r.10: env + argv thật mà app-server nhận
    Path(os.environ["GHI_ENV"]).write_text(json.dumps({"env": dict(os.environ), "argv": sys.argv}))


def tra(tin):
    print(json.dumps(tin), flush=True)


for dong in sys.stdin:
    tin = json.loads(dong)
    nhan.append(tin)
    ghi.write_text(json.dumps(nhan))
    if tin.get("method") == "initialize":
        if che_do == "dong":
            sys.exit(0)
        tra({"method": "thong-bao/khac", "params": {}})
        print("dòng rác không phải json", flush=True)
        tra({"id": 0, "result": {"userAgent": "gia/0"}})
        if che_do == "treo":
            time.sleep(60)
        if che_do == "dai":
            sys.stdout.write("x" * (2 << 20))
            sys.stdout.flush()
            time.sleep(60)
    elif tin.get("method") == "account/rateLimits/read":
        if che_do == "lo":
            print(os.environ.get("LO", ""), file=sys.stderr, flush=True)
            tra({"id": 1, "error": {"code": 401, "message": os.environ.get("LO", "")}})
        else:
            tra({"id": 1, "error": {"code": -32600, "message": "chưa đăng nhập"}} if che_do == "loi"
                else {"id": 1, "result": MAU["plus"]})
