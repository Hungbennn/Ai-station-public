import subprocess
from datetime import datetime, timezone

import pytest

from git_gia import MOI_TRUONG, git, ghi, tao_repo
from tram.chay_cli.bo_cli import BO_CLI, BoCLI
from tram.chay_cli.codex.bo import BoCodex, lenh_codex
from tram.chay_cli.giao_dien import ChayCLI
from tram.han_muc.nguon import NguonHanMuc


def test_lenh_codex_sandbox_ghi_worktree_khong_mang_khong_hoi(tmp_path):
    argv = lenh_codex(worktree=tmp_path / "wt", ghi_them=[tmp_path / "phieu"], codex="/opt/bin/codex")
    assert argv == ["/opt/bin/codex", "exec", "--json", "--cd", str(tmp_path / "wt"), "--sandbox", "workspace-write",
                    "-c", 'approval_policy="never"', "-c", "sandbox_workspace_write.network_access=false",
                    "--add-dir", str(tmp_path / "phieu"), "-"]
    assert not any("danger" in a or "bypass" in a or "full-auto" in a for a in argv)
    for sai in ({"worktree": "wt", "ghi_them": []}, {"worktree": tmp_path, "ghi_them": ["/"]},
                {"worktree": tmp_path, "ghi_them": [tmp_path / ".." / "x"]}):
        with pytest.raises(ValueError):
            lenh_codex(**sai)


def test_bo_codex_khong_mo_git_chung(tmp_path):
    kho = tao_repo(tmp_path / "kho")
    ghi(kho, {"a.txt": "1"})
    git(kho, "worktree", "add", "-q", "-b", "tram/hr-1", str(tmp_path / "wt"))
    bo = BoCodex(codex="/opt/bin/codex", chay=lambda a, **k: subprocess.run(a, **k, env=MOI_TRUONG))
    argv = bo.lenh(worktree=tmp_path / "wt", thu_muc_phieu=tmp_path / "phieu", vai="coder", lenh_cho_phep=["x *"])
    them = [argv[i + 1] for i, a in enumerate(argv) if a == "--add-dir"]
    assert them == [str(tmp_path / "phieu")]
    assert str((kho / ".git").resolve()) not in them


def test_dang_ky_vao_bo_cli_cua_vong_tho(tmp_path, monkeypatch):
    bo = BO_CLI["codex"]
    assert isinstance(bo, BoCLI) and isinstance(bo, BoCodex) and bo.cli == "codex" and bo.bien_thu_muc == "CODEX_HOME"
    assert bo.chu_ky_han_muc_ranh_giay == 300
    assert isinstance(bo.tao_chay(), ChayCLI) and isinstance(bo.tao_nguon(), NguonHanMuc)
    khong = BoCodex(codex=str(tmp_path / "khong-co-codex"))
    assert khong.doc_han_muc_ranh("C/codex-1", tmp_path, bay_gio=datetime.now(timezone.utc), principal=None,
                                  path="/usr/bin") is None
    from dataclasses import replace
    from types import SimpleNamespace
    import threading
    from tho_chay_gia import dung_may, lay_phieu
    from tram.tho.chuan_bi import chuan_bi
    from tram.tho.mot_lan import chay_mot_lan
    from tram.chay_cli.giao_dien import KetQuaChay
    from tram.tho.principal import BIEN_GIU
    from tram.tho.cau_hinh_chay import doc_cau_hinh_chay
    assert "CODEX_HOME" in BIEN_GIU
    assert doc_cau_hinh_chay({"nho_url": "https://may-b.tail.ts.net/nho/mcp"}).nho_url.endswith("/nho/mcp")
    m = dung_may(tmp_path / "worker", monkeypatch, [])
    k, so, hop, tt = lay_phieu(m)
    pc = chuan_bi(m.nc, k, so, hop, tt)
    pc.k = replace(pc.k, cli="codex")
    m.nc.tao_cli = None
    captured = {}
    def chay(argv, **kw):
        captured.update(argv=argv, **kw)
        return KetQuaChay(0, True, False, False, False, token_ra=11)
    def factory(boc, **kw):
        captured["factory"] = (boc, kw)
        return SimpleNamespace(chay=chay)
    monkeypatch.setattr(bo, "tao_chay", factory)
    result = chay_mot_lan(pc, m.nc, threading.Event())
    assert result.token_ra == 11 and captured["argv"][0] == "codex"
    assert "CODEX_HOME" in captured["env"] and "CLAUDE_CONFIG_DIR" not in captured["env"]
    # B bọc thêm lớp token Claude (21/10); với codex argv phải y như principal.boc — so kết quả, không so danh tính hàm.
    assert captured["factory"][0](["codex", "exec"]) == pc.principal.boc(["codex", "exec"])
    assert captured["factory"][1]["kill"] == pc.principal.kill_nhom
    assert captured["factory"][1]["tran_token_ra"] == pc.p.ngan_sach.token_ra
