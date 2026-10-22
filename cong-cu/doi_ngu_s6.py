"""Phép đo quyền có đối chứng; chạy từ hungle, lệnh thử nằm dưới đúng khe, không lưu bí mật."""
import json
import pwd
from pathlib import Path

import subprocess

from doi_ngu_io import Dung
from doi_ngu_chuan_bi import THO, TRAM, RUNTIME, can_tat


def boc_van_hanh(user, env):
    # Người vận hành (hungle) không có SETENV: đổi user không giữ env, truyền đúng biến qua env -i.
    return lambda argv: ["sudo", "-n", "-H", "-u", user, "/usr/bin/env", "-i",
                         *[f"{k}={v}" for k, v in env.items()], *argv]


def chay_van_hanh(argv, *, kill, timeout, **kw):
    # Không tách phiên: sudo -n cần vé tty của người vận hành (khoi_chay đặt start_new_session → rc 1).
    return subprocess.run(argv, timeout=timeout, **kw)


def s6(c):
    from tram.tho.cham_tham_do import cham
    can_tat(c)
    def q(ten, *argv, check=True):
        return c.goi(ten, ["sudo", "-H", "-u", "tram-tho", *map(str, argv)], check=check, han=60)
    tmp = Path(q("thu-muc-do", "mktemp", "-d", str(THO / "tram/s6.XXXXXX")).stdout.strip())
    if tmp.parent != THO / "tram" or not tmp.name.startswith("s6."):
        raise Dung("duong-do-sai")
    q("di-qua-do", "chmod", "755", tmp)
    repo = tmp / "repo"
    q("repo-do", "git", "init", "-q", repo)
    q("commit-do", "git", "-C", repo, "-c", "user.name=probe", "-c", "user.email=probe@localhost",
      "-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false", "commit", "--allow-empty", "-m", "probe")
    for n in (1, 2):
        gate = tmp / f"g{n}"
        q("cong-do", "mkdir", "-m", "700", gate)
        w, hd = gate / "cay", gate / "phieu/hang-doi.jsonl"
        q("worktree-do", "git", "-C", repo, "worktree", "add", "-q", "-b", f"tram/probe-{n}", w)
        q("goi-do", "mkdir", w / ".tram")
        q("hang-doi-do", "mkdir", "-m", "700", hd.parent)
        q("file-do", "touch", hd, hd.parent / "settings.json")
        q("di-qua-hang-doi", "chmod", "+a", f"user:tram-khe{n} allow list,search", hd.parent)
        script = "import sys, subprocess; from pathlib import Path; sys.path.insert(0, sys.argv[1]); "
        script += "from tram.tho.quyen_cay_b import trao_quyen_b; "
        script += "trao_quyen_b(Path(sys.argv[2]), Path(sys.argv[3]), user=sys.argv[4], chay=subprocess.run)"
        q("acl-do", RUNTIME / ".venv/bin/python", "-I", "-c", script, RUNTIME, w, hd, f"tram-khe{n}")
        q("cong-kin", "chmod", "700", gate)
        q("mo-cong", "chmod", "+a", f"user:tram-khe{n} allow search", gate)
    for n in (1, 2):
        gate = tmp / f"g{n}"
        user, w, hd = f"tram-khe{n}", gate / "cay", gate / "phieu/hang-doi.jsonl"
        def thu(ten, argv, dat):
            r = c.goi(f"{user}-{ten}", ["sudo", "-H", "-u", user, *map(str, argv)], check=False, han=30)
            loai = "ok" if dat else "ghi"
            if cham(loai, r.returncode, r.stdout.strip(), r.stderr)[0] != "dat":
                raise Dung(f"{user}-{ten}")
            return r
        r = thu("uid", ["id", "-u"], True)
        if int(r.stdout.strip()) != pwd.getpwnam(user).pw_uid:
            raise Dung("uid-khong-khop")
        thu("ghi-ma", ["touch", w / "duong.txt"], True)
        thu("append-bao", ["/bin/sh", "-c", 'printf x >> "$1"', "probe", hd], True)
        thu("git-config", ["touch", repo / ".git/config"], False)
        thu("git-objects", ["touch", repo / ".git/objects/khong-duoc"], False)
        thu("git-refs", ["touch", repo / ".git/refs/heads/khong-duoc"], False)
        thu("git-hooks", ["touch", repo / ".git/hooks/khong-duoc"], False)
        thu("doi-git-pointer", ["mv", w / ".git", w / "git-khac"], False)
        thu("settings", ["touch", hd.parent / "settings.json"], False)
        thu("hang-doi-khe-khac", ["cat", tmp / f"g{3-n}/phieu/hang-doi.jsonl"], False)
        thu("nha-dai-ca", ["ls", "/Users/dai-ca"], False)
        thu("cau-hinh-khe-khac", ["ls", f"/Users/tram-khe{3-n}/claude"], False)
    for n in (1, 2):
        gate, user = tmp / f"g{n}", f"tram-khe{n}"
        w = gate / "cay"
        def thu(ten, argv, dat):
            r = c.goi(ten, ["sudo", "-H", "-u", user, *map(str, argv)], check=False, han=30)
            if cham("ok" if dat else "ghi", r.returncode, r.stdout.strip(), r.stderr)[0] != "dat":
                raise Dung(ten)
        thu("file-uid-khe", ["/bin/sh", "-c", 'umask 077; mkdir "$1/d"; printf x > "$1/d/f"', "probe", w], True)
        uid = q("chu-file", "stat", "-f", "%u", w / "d/f").stdout.strip()
        if uid != str(pwd.getpwnam(user).pw_uid):
            raise Dung("file-khong-thuoc-khe")
        q("quan-ly-doc-file", "cat", w / "d/f")
        q("dong-cong", "chmod", "-N", gate)
        thu("quyen-cu-da-dong", ["cat", w / "d/f"], False)
        script = "import sys; from pathlib import Path; sys.path.insert(0, sys.argv[1]); "
        script += "from tram.tho.luot_b import xoa_cay; xoa_cay(Path(sys.argv[2]), Path(sys.argv[3]))"
        q("xoa-luot", RUNTIME / ".venv/bin/python", "-I", "-c", script, RUNTIME, gate, repo)
    from doi_ngu_token import kiem_token_s6
    kiem_token_s6(c)
    from tram.tho.khach import DichKiemAm
    from tram.tho.kiem_am import chay_tham_do, tham_do_api_db
    from tram.tho.principal import doc_principal
    # Token chỉ được đọc trong tiến trình tram-tho; stdout chỉ chứa đích thăm dò không bí mật.
    script = ("import sys, json; from dataclasses import asdict; sys.path.insert(0, sys.argv[1]); "
              "from tram.tho.khach import KhachTram, doc_token_may; "
              "k = KhachTram('http://127.0.0.1:7700', doc_token_may(tren_may_b=True) or ''); "
              "print(json.dumps(asdict(k.kiem_am())))")
    r = q('dich-kiem-am', RUNTIME / '.venv/bin/python', '-I', '-c', script, RUNTIME)
    d = DichKiemAm(**json.loads(r.stdout))
    for n in (1, 2):
        user = f"tram-khe{n}"
        pr = doc_principal(f"user:{user}")
        ds = tham_do_api_db(api="http://127.0.0.1:7700", dai_ca_login=d.dai_ca_login, may_b=d.may_b, db=list(d.db_nghiep_vu))
        moi = {"PATH": "/opt/homebrew/bin:/usr/bin:/bin", "LANG": "C.UTF-8"}
        kq = chay_tham_do(ds, boc=boc_van_hanh(user, moi), kill=pr.kill_nhom, env=moi, chay=chay_van_hanh)
        if not all(x.dat for x in kq):
            raise Dung("API-DB-chua-dat")
    c.ghi("S6", "DAT-PHEP-DO-QUYEN-CON-CAN-THU-HOI-R4")
    # Giữ thư mục đo để đối soát; chỉ rmdir/xoá sau khi Đại ca duyệt đúng đường, không quét theo tên.
