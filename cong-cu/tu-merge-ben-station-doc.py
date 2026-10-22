#!/usr/bin/env python3
"""Thu thập chẩn đoán sổ tay; chỉ đọc repo/GitHub, chỉ ghi một log tạm 0600."""
import argparse
import datetime
import json
import os
from pathlib import Path
import subprocess
import tempfile

REPO = "Hungbennn/ben-station"
GOC = Path(__file__).resolve().parents[1]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--github-doc", action="store_true", help="Gọi GitHub chỉ đọc bằng gh đã đăng nhập")
    p.add_argument("--pr", type=int, help="Số PR thử để đọc thêm; cần --github-doc")
    a = p.parse_args()
    if a.pr is not None and (a.pr <= 0 or not a.github_doc):
        p.error("--pr cần số dương và --github-doc")
    fd, log = tempfile.mkstemp(prefix="ben-station-tu-merge-", suffix=".log")
    loi = []
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        def ghi(nhan, dl):
            dong = nhan + ": " + json.dumps(dl, ensure_ascii=False, sort_keys=True)
            print(dong)
            f.write(dong + "\n")
            f.flush()

        def chay(nhan, argv, *, ma_duoc=(0,)):
            try:
                r = subprocess.run(argv, cwd=GOC, capture_output=True, text=True, timeout=60,
                                   env={**os.environ, "GIT_TERMINAL_PROMPT": "0",
                                        "GH_PROMPT_DISABLED": "1", "GH_NO_UPDATE_NOTIFIER": "1"})
                if r.returncode in ma_duoc:
                    return r.stdout
                ghi(nhan, {"ma_loi": r.returncode, "goi_y": "Kiểm quyền đọc/cú pháp; chưa kết luận cổng đạt"})
            except (OSError, subprocess.TimeoutExpired) as e:
                ghi(nhan, {"loi": type(e).__name__})
            loi.append(nhan)
            return None

        def git(*args):
            return chay("git " + args[0], ["git", "-c", "core.hooksPath=/dev/null", *args])

        ghi("Giờ", datetime.datetime.now(datetime.timezone.utc).isoformat())
        ghi("Phạm vi", "Chỉ đọc; không sudo, launchctl, TRAM_HOME, token, fetch hoặc thay cấu hình")
        ghi("HEAD của bản sổ tay", (git("rev-parse", "HEAD") or "").strip())
        ghi("Nhánh", (git("branch", "--show-current") or "").strip())
        for ten in ("origin", "github"):
            url = git("remote", "get-url", ten)
            ghi("Remote " + ten, {"dung_repo_GitHub": bool(url and url.strip() in (
                f"https://github.com/{REPO}", f"https://github.com/{REPO}.git",
                f"git@github.com:{REPO}.git", f"ssh://git@github.com/{REPO}.git"))})
        wf = GOC / ".github/workflows"
        ghi("Workflow trong checkout", sorted(x.name for x in wf.glob("*") if x.suffix in (".yml", ".yaml")))
        ghi("Cấu hình ben-station có trong checkout", (GOC / "du-an/ben-station.yaml").is_file())
        if a.github_doc:
            def doc(nhan, args, loc):
                raw = chay(nhan, ["gh", *args], ma_duoc=(0, 1, 8) if nhan == "Checks PR" else (0,))
                if raw is not None:
                    try:
                        ghi(nhan, loc(json.loads(raw)))
                    except (ValueError, TypeError, KeyError, AttributeError):
                        ghi(nhan, "Dữ liệu không đúng dạng; không in đầu ra thô")
                        loi.append(nhan)

            doc("Bảo vệ main", ["api", "--method", "GET", f"repos/{REPO}/branches/main/protection"],
                lambda d: {k: d.get(k) for k in (
                    "required_status_checks", "enforce_admins", "required_pull_request_reviews")})
            doc("Luật hiệu lực main", ["api", "--method", "GET", "--paginate", "--slurp",
                                      f"repos/{REPO}/rules/branches/main"],
                lambda pages: [[r["type"] for r in page] for page in pages])
            if a.pr:
                doc("PR", ["pr", "view", str(a.pr), "--repo", REPO, "--json",
                           "headRefOid,baseRefName,isDraft,mergeable,mergeStateStatus"],
                    lambda d: {k: d[k] for k in (
                        "headRefOid", "baseRefName", "isDraft", "mergeable", "mergeStateStatus")})
                doc("Checks PR", ["pr", "checks", str(a.pr), "--repo", REPO, "--required",
                                  "--json", "name,bucket"], lambda d: [
                                      {"name": c["name"], "bucket": c["bucket"]} for c in d])
        ghi("Chưa đo", "Uq, kho kiểm thật, quyền deploy, bản đang chạy, rollback, passkey và R0–R5")
        ghi("Kết quả thu thập", {"loi": loi, "cho_phep_bat": False})
    print("Gửi Bé file log này (không cần gửi token/mật khẩu): " + log)
    return 2 if loi else 0


if __name__ == "__main__":
    raise SystemExit(main())
