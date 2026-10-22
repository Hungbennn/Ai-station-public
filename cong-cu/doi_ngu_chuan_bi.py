"""Chuẩn bị runtime/kho/cấu hình B; chỉ người vận hành gọi sau duyệt."""
import os
import re
from pathlib import Path

from doi_ngu_io import Dung, ghi_yaml

REPO = Path("/Users/dai-ca/Developer/Ben Station")
RUNTIME = Path("/Users/Shared/tram-tho-code")
TRAM = RUNTIME / ".venv/bin/tram"
PYTHON = "/usr/local/tram/toolchains/python/3.12.15-20261009/bin/python3.12"
THO = Path("/Users/tram-tho")
CAU_HINH = Path("/Users/dai-ca/.tram/cau-hinh.yaml")
PLIST = Path("/Library/LaunchDaemons/vn.tram.tho.plist")


def lenh_tho(*args):
    return ["sudo", "-H", "-u", "tram-tho", str(TRAM), "tho", *args]


def can_tat(c):
    r = c.goi("dich-vu-tho", ["launchctl", "print", "system/vn.tram.tho"], check=False, han=30)
    if r.returncode == 0 or "Could not find service" not in r.stderr:
        raise Dung("tho-chua-xac-nhan-da-dung")
    r = c.goi("disable", ["launchctl", "print-disabled", "system"], han=30)
    if not re.search(r'"vn\.tram\.tho"\s*=>\s*(true|disabled)\b', r.stdout):  # macOS 15 in "disabled"
        raise Dung("tho-chua-disable")


def chuan_bi(c):
    import yaml
    can_tat(c)
    raw_gv = yaml.safe_load(CAU_HINH.read_text()) or {}
    if raw_gv.get("giao_viec", {}).get("bat", False):
        raise Dung("giao-viec-dang-bat")
    c.goi("sao-luu-su-kien", [str(REPO / ".venv/bin/tram"), "chu", "sao-luu"])
    if RUNTIME.exists():
        raise Dung("runtime-da-co-doi-soat-truoc-khi-cai-lai")
    RUNTIME.mkdir(mode=0o700)
    c.goi("clone-runtime", ["git", "clone", "--no-local", "--no-hardlinks", str(REPO), str(RUNTIME)])
    script = "import sys; from pathlib import Path; sys.path.insert(0, sys.argv[1]); "
    script += "from tram.tho.deps_b import cap_deps_b; cap_deps_b(Path(sys.argv[1]))"
    c.goi("deps-root", [PYTHON, "-I", "-c", script, str(RUNTIME)])
    TRAM.write_text(f"#!{RUNTIME}/.venv/bin/python\nimport sys\nsys.path.insert(0, {str(RUNTIME)!r})\n"
                    "from tram.cli import main\nsys.exit(main())\n")
    TRAM.chmod(0o755)
    env = {**os.environ, "TRAM_REPO": str(RUNTIME), "UV_PYTHON_DOWNLOADS": "never"}
    c.goi("cai-chi-tho", [str(REPO / ".venv/bin/tram"), "chu", "cai-dat-tho", "--co-che", "user",
        "--khe", "claude-1=tram-khe1", "--khe", "claude-2=tram-khe2", "--chi-tho", "--giu-tat", "--dong-y"], env=env)
    for user in ("tram-tho", "tram-khe1", "tram-khe2"):
        c.goi("chan-nha-dai-ca", ["chmod", "+a", f"user:{user} deny list,search", "/Users/dai-ca"], han=30)
    for n in (1, 2):
        user = f"tram-khe{n}"
        c.goi("thu-muc-claude", ["sudo", "-u", user, "mkdir", "-p", f"/Users/{user}/claude"], han=30)
        c.goi("quyen-nha-khe", ["sudo", "chmod", "700", f"/Users/{user}"], han=30)
        c.goi("quyen-claude", ["sudo", "chmod", "700", f"/Users/{user}/claude"], han=30)
        c.goi("quan-ly-di-qua", ["sudo", "chmod", "+a", "user:tram-tho allow search", f"/Users/{user}"], han=30)
        c.goi("claude-khong-acl", ["sudo", "-u", user, "chmod", "-N", f"/Users/{user}/claude"], han=30)
    for rel in (".tram", ".tram/log", "tram", "tram/kho", "tram/worktrees", ".tram/hang-doi/B"):
        c.goi("thu-muc-tho", ["sudo", "-u", "tram-tho", "mkdir", "-p", str(THO / rel)], han=30)
    for rel in ("", ".tram"):
        c.goi("kin-nha-quan-ly", ["sudo", "chmod", "700", str(THO / rel)], han=30)
    for n in (1, 2):
        user = f"tram-khe{n}"
        for rel in ("", ".tram", ".tram/hang-doi", ".tram/hang-doi/B", "tram", "tram/worktrees"):
            c.goi("di-qua", ["sudo", "chmod", "+a", f"user:{user} allow search", str(THO / rel)], han=30)
        q = THO / f".tram/hang-doi/B/claude-{n}"
        c.goi("hang-doi-khe", ["sudo", "-u", "tram-tho", "mkdir", "-p", str(q)], han=30)
        c.goi("kin-hang-doi", ["sudo", "chmod", "700", str(q)], han=30)
        c.goi("quyen-hang-doi", ["sudo", "chmod", "+a", f"user:{user} allow list,search", str(q)], han=30)
    raw = {"may_id": "B", "tram_api": "http://127.0.0.1:7700", "chay": {"day": "kho-tho",
        "path": f"{RUNTIME}/.venv/bin:/opt/homebrew/bin:/usr/bin:/bin", "thu_muc_tram": "/Users/dai-ca/.tram"},
        "khe": [{"ten": f"claude-{n}", "cli": "claude", "principal": f"user:tram-khe{n}",
        "thu_muc_cau_hinh": f"/Users/tram-khe{n}/claude", "ten_goi_nho": f"Tho Claude {n}",
        "vai_uu_tien": ["spec", "coder"] if n == 1 else ["qc"]} for n in (1, 2)]}
    p = c.goc / "tho-ung-vien.yaml"
    ghi_yaml(p, raw)
    c.goi("ung-vien", ["sudo", "install", "-o", "tram-tho", "-m", "600", str(p), str(THO / ".tram/tho-ung-vien.yaml")])
    da = RUNTIME / "du-an/ben-station.yaml"
    raw = yaml.safe_load(da.read_text())
    raw["duong_dan"] = str(THO / "tram/kho/ben-station")
    raw["moi_truong_kiem"]["file"] = str(RUNTIME / "du-an/ben-station.env.testing")
    ghi_yaml(da, raw)
    da.chmod(0o644)
    c.goi("runtime-chi-doc", ["find", str(RUNTIME), "(", "-type", "d", "-o", "-type", "f", ")",
                             "-exec", "chmod", "go-w", "{}", "+"])
    RUNTIME.chmod(0o755)
    c.ghi("chuan-bi", "XONG-GIU-TAT")


def kho(c):
    import yaml
    can_tat(c)
    def remote(ten):
        r = c.goi("doc-remote", ["git", "-C", str(REPO), "remote", "get-url", ten], check=False, han=30)
        return r.stdout.strip() if r.returncode == 0 else None
    github, origin = remote("github"), remote("origin")
    if github not in ("git@github.com:Hungbennn/ben-station.git", "https://github.com/Hungbennn/ben-station.git"):
        raise Dung("github-chua-khop")
    if origin not in (None, github):
        raise Dung("origin-khac-github")
    if origin is None:
        c.goi("them-origin", ["git", "-C", str(REPO), "remote", "add", "origin", github], han=30)
    nguon = Path("/Users/Shared/tram-nguon/ben-station")
    link = Path("/Users/dai-ca/.tram/kho-kiem/ben-station")
    dich = THO / "tram/kho/ben-station"
    # Nhà tram-tho là 700 sau chuan-bi: hungle không stat được dich, phải kiểm dưới quyền tram-tho.
    co_dich = c.goi("co-kho-tho", ["sudo", "-u", "tram-tho", "test", "-e", str(dich)], check=False, han=30)
    if co_dich.returncode not in (0, 1):
        raise Dung("khong-kiem-duoc-kho-tho")
    if nguon.exists() or link.exists() or link.is_symlink() or co_dich.returncode == 0:
        raise Dung("kho-da-co-can-doi-soat-khong-ghi-de")
    nguon.parent.mkdir(mode=0o700, exist_ok=True)
    c.goi("clone-nguon", ["git", "clone", "--no-checkout", "--config", "core.hooksPath=/dev/null", github, str(nguon)])
    link.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    link.symlink_to(nguon)
    c.goi("nguon-di-qua", ["chmod", "+a", "user:tram-tho allow search", str(nguon.parent)], han=30)
    c.goi("nguon-doc", ["find", str(nguon), "(", "-type", "d", "-o", "-type", "f", ")", "-exec", "chmod", "+a",
        "user:tram-tho allow read,execute,readattr,readsecurity,file_inherit,directory_inherit", "{}", "+"])
    for safe in (nguon, nguon / ".git"):
        c.goi("git-doc-nguon", ["sudo", "-H", "-u", "tram-tho", "git", "config", "--global", "--add",
                               "safe.directory", str(safe)], han=30)
    c.goi("clone-tho", ["sudo", "-u", "tram-tho", "git", "-c", f"safe.directory={nguon}/.git", "clone",
        "--no-local", "--no-hardlinks", "--config", "core.hooksPath=/dev/null", str(nguon), str(dich)])
    dong_bo_nguon(c, dich)
    for p in (THO, THO / "tram", THO / "tram/kho"):
        c.goi("tram-di-qua", ["sudo", "chmod", "+a", "user:hungle allow search", str(p)], han=30)
    c.goi("tram-doc-kho", ["sudo", "find", str(dich), "(", "-type", "d", "-o", "-type", "f", ")", "-exec", "chmod", "+a",
        "user:hungle allow read,execute,readattr,readsecurity,file_inherit,directory_inherit", "{}", "+"])
    raw = yaml.safe_load(CAU_HINH.read_text()) or {}
    if raw.get("giao_viec", {}).get("bat", False):
        raise Dung("giao-viec-dang-bat")
    cb = raw.setdefault("cong_bo", {})
    cb["phuong_an"] = "lai"
    cb.setdefault("kho_tho", {})["B"] = str(THO / "tram/kho")
    ghi_yaml(CAU_HINH, raw)


def dong_bo_nguon(c, dich):
    # Nguồn --no-checkout chỉ fetch origin/*; refs/heads/main của nó không tự tiến.
    c.goi("refspec-nguon", ["sudo", "-H", "-u", "tram-tho", "git", "-C", str(dich), "config", "--replace-all",
                           "remote.origin.fetch", "+refs/remotes/origin/*:refs/remotes/origin/*"], han=30)
    c.goi("fetch-nguon", ["sudo", "-H", "-u", "tram-tho", "git", "-C", str(dich), "fetch", "origin"])
