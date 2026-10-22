"""QĐ1: dữ liệu gh giả, không mạng, không chạy CLI thật."""
import json
from copy import deepcopy
from types import SimpleNamespace

import pytest

from tram.giao_viec.gh_bao_ve import cong_merge

H = "a" * 40
P = SimpleNamespace(so=1, head=H, base="main")
BV = {"required_status_checks": {"strict": True, "checks": [{"context": "test", "app_id": 1}]},
      "enforce_admins": {"enabled": True}, "required_pull_request_reviews":
      {"bypass_pull_request_allowances": {"users": [], "teams": [], "apps": []}}}
PR = {"headRefOid": H, "isDraft": False, "mergeable": "MERGEABLE", "mergeStateStatus": "CLEAN"}


def gia(bv=None, pr=None, checks=None, rules=None, fail=False):
    calls = []
    def run(argv, dau_vao):
        calls.append(argv)
        if fail:
            return 1, "secret", "secret"
        if "checks" in argv:
            d = [{"bucket": "pass"}] if checks is None else checks
        elif "view" in argv:
            d = PR if pr is None else pr
        elif argv[-1].endswith("/protection"):
            d = BV if bv is None else bv
        else:
            d = [[] if rules is None else rules]
        return 0, json.dumps(d), ""
    return run, calls


def test_optional_fail_does_not_block():
    run, calls = gia(pr={**PR, "mergeStateStatus": "UNSTABLE"})
    assert cong_merge(run, "owner/repo", P) == "xanh"
    assert any("--required" in a for a in calls)
    assert all("statusCheckRollup" not in " ".join(a) for a in calls)


@pytest.mark.parametrize("change", ["strict", "empty", "source", "admin", "bypass"])
def test_missing_protection_blocks(change):
    b = deepcopy(BV)
    if change == "strict":
        b["required_status_checks"]["strict"] = False
    if change == "empty":
        b["required_status_checks"]["checks"] = []
    if change == "source":
        b["required_status_checks"]["checks"][0]["app_id"] = -1
    if change == "admin":
        b["enforce_admins"]["enabled"] = False
    if change == "bypass":
        b["required_pull_request_reviews"]["bypass_pull_request_allowances"]["users"] = [{"id": 1}]
    assert cong_merge(gia(bv=b)[0], "owner/repo", P) == "do"


@pytest.mark.parametrize("kw", [
    {"fail": True}, {"checks": []}, {"checks": [{"bucket": "pending"}]},
    {"rules": [{"type": "merge_queue"}]}, {"pr": {**PR, "isDraft": True}},
    {"pr": {**PR, "headRefOid": "b" * 40}}, {"pr": {**PR, "mergeable": "CONFLICTING"}},
    {"pr": {**PR, "mergeStateStatus": "BEHIND"}}, {"pr": {**PR, "mergeStateStatus": "UNKNOWN"}},
])
def test_closed_when_uncertain(kw):
    assert cong_merge(gia(**kw)[0], "owner/repo", P) != "xanh"


def test_merge_queue_on_next_page_blocks():
    base, _ = gia()
    def run(argv, dau_vao):
        if "/rules/branches/" in argv[-1]:
            pages = [[], [{"type": "merge_queue"}]]
            data = pages if "--paginate" in argv and "--slurp" in argv else pages[0]
            return 0, json.dumps(data), ""
        return base(argv, dau_vao)
    assert cong_merge(run, "owner/repo", P) != "xanh"
