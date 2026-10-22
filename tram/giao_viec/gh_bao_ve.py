"""QĐ1: classic branch protection + required checks do gh chọn, không phân loại CI tuỳ chọn."""
import json
from urllib.parse import quote

from tram.giao_viec.gh_tu_merge import REPO_RE


def bao_ve_dat(d):
    try:
        checks = d["required_status_checks"]
        nguon = checks["checks"]
        bypass = (d.get("required_pull_request_reviews") or {}).get("bypass_pull_request_allowances", {})
        return (checks["strict"] is True and d["enforce_admins"]["enabled"] is True
                and isinstance(nguon, list) and bool(nguon)
                and all(isinstance(x.get("context"), str) and bool(x["context"])
                        and type(x.get("app_id")) is int and x["app_id"] > 0 for x in nguon)
                and not any(bypass.get(k) for k in ("users", "teams", "apps")))
    except (KeyError, TypeError, AttributeError):
        return False


def cong_merge(chay, repo, pr):
    if not REPO_RE.fullmatch(repo):
        return "do"
    def doc(argv):
        ma, ra, _ = chay(["gh", *argv], None)
        if ma and not (argv[:2] == ["pr", "checks"] and ma in (1, 8)):
            raise ValueError("github-chua-cho-phep")
        return json.loads(ra)
    try:
        base = quote(pr.base, safe="")
        bv = doc(["api", "--method", "GET", f"repos/{repo}/branches/{base}/protection"])
        pages = doc(["api", "--method", "GET", "--paginate", "--slurp",
                     f"repos/{repo}/rules/branches/{base}"])
        if not isinstance(pages, list) or not pages or not all(isinstance(p, list) for p in pages):
            return "do"
        rules = [r for page in pages for r in page]
        if not bao_ve_dat(bv) or not isinstance(rules, list) or any(
                r.get("type") == "merge_queue" for r in rules):
            return "do"
        p = doc(["pr", "view", str(pr.so), "--repo", repo, "--json",
                 "headRefOid,isDraft,mergeable,mergeStateStatus"])
        if (p.get("headRefOid") != pr.head or p.get("isDraft") is not False
                or p.get("mergeable") != "MERGEABLE" or p.get("mergeStateStatus") not in ("CLEAN", "UNSTABLE")):
            return "do"
        checks = doc(["pr", "checks", str(pr.so), "--repo", repo, "--required", "--json", "bucket"])
        return "xanh" if isinstance(checks, list) and checks and all(
            c.get("bucket") in ("pass", "skipping") for c in checks) else "do"
    except (ValueError, KeyError, TypeError, AttributeError):
        return "loi"
