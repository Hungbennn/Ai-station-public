"""Dựng một máy thợ chạy THẬT vòng `tram tho chay` với CLI GIẢ (tests/cli_gia.py) và tram-api trong bộ nhớ (CHỈ DÙNG
TRONG TEST): principal giả chạy cùng user (không sudo), remote Git là repo bare cục bộ, không gọi Claude/mạng."""
import json
import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

from cong_bo_gia import dung_ba_kho
from git_gia import ghi, git
from khach_gia import khach_asgi
from phieu_gia import de_xuat, khoa
from tho_api_gia import tao_tram
from tram.cau_hinh.cong_bo import CauHinhCongBo
from tram.chay_cli.claude import ChayClaude
from tram.cong_bo.nguon import NguonKhoTho
from tram.duong_dan import goc_repo
from tram.tho.cau_hinh import CauHinhTho, KheCauHinh
from tram.tho.cau_hinh_chay import CauHinhChay
from tram.tho.mo_coi import kill_cuc_bo
from tram.tho.ngu_canh import NguCanhTho
from tram.tho.lenh_token_khe import lenh_token_khe
from tram.tho.tep_token import ghi as ghi_token

GOC = Path(__file__).resolve().parents[1]
CLI = str(Path(__file__).parent / "cli_gia.py")
LENH_KIEM = "python3 kiem_ok.py"
FILE_BG = "docs/handovers/2026-10-13-hr-1.md"


@dataclass
class PrincipalGia:
    kb: Path
    user: str | None = None

    def boc(self, argv):
        token = lenh_token_khe("chay")
        for i in range(len(argv)):
            if argv[i:i + len(token)] == token:
                argv = [*argv[:i], sys.executable, str(Path(__file__).with_name("claude_token_gia.py")),
                        str(self.kb.parent / "token-gia/claude/oauth-token"), *argv[i + len(token):]]
                break
        dau = ["/usr/bin/env", f"PYTHONPATH={GOC}", "GIT_CONFIG_GLOBAL=/dev/null", "GIT_CONFIG_NOSYSTEM=1",
               f"CLI_GIA_KICH_BAN={self.kb}"]
        return dau + ([sys.executable, CLI, *argv[1:]] if argv[0] == "claude" else argv)

    def kill_nhom(self, pgid, sig):
        kill_cuc_bo(pgid, sig)


def tram_bao(*args) -> dict:
    """Bước kịch bản: agent gọi `tram bao …` trong phiên."""
    return {"chay": [sys.executable, "-c", "import sys; from tram.cli import main; sys.exit(main(sys.argv[1:]))",
                     "bao", *args]}


def khoi_bg(tieu_chi: str, dat: bool = True) -> str:
    k = {"phien_ban": 1, "loai": "chinh-thuc", "luot": 0, "file_ban_giao": FILE_BG, "nhanh": "", "commit": None,
         "doi_chieu_nghiem_thu": [{"tieu_chi": tieu_chi, "dat": dat, "bang_chung": "kiem_ok.py pass"}],
         "lenh_kiem": [], "quyet_dinh": [], "huong_da_bo": [], "vuong_mac": [], "buoc_tiep": [], "cau_hoi_mo": [],
         "thay_doi_vung_nhay_cam": []}
    return f"# Bàn giao\n\n<!-- ban-giao -->\n{json.dumps(k, ensure_ascii=False)}\n<!-- ban-giao -->\n"


@dataclass
class MayGia:
    t: object
    b: object
    nc: NguCanhTho
    kb: Path


def dung_may(tmp_path, monkeypatch, kich_ban, *, so_lan=3, phut=90, buoc="code") -> MayGia:
    b = dung_ba_kho(tmp_path, monkeypatch)
    nguon = b.remote.parent / "nguon"
    b.cha = ghi(nguon, {"kiem_ok.py": "print('ok')\n"}, "thêm lệnh kiểm")
    git(nguon, "push", "-q", str(b.remote), "HEAD:refs/heads/main")
    repo = tmp_path / "repo"
    (repo / "du-an").mkdir(parents=True)
    shutil.copytree(goc_repo() / "vai" / "quyen", repo / "vai" / "quyen")
    (tmp_path / "env.testing").write_text("APP_ENV=testing\n")
    (repo / "du-an" / "hr-codex.yaml").write_text(
        f"ten: hr-codex\nduong_dan: /x\nlenh_cho_phep: ['{LENH_KIEM}']\n"
        f"moi_truong_kiem: {{file: {tmp_path / 'env.testing'}, dich: .env.testing}}\n")
    monkeypatch.setenv("TRAM_REPO", str(repo))
    t = tao_tram(tmp_path)
    t.pt.cac_du_an = lambda: ["hr-codex"]  # D89: GET cấu hình dự án thật trong trạm ASGI giả
    da_cap = []

    def chon(khe_id, hm):                      # đứng thay phần 4: đúng MỘT phiếu cho bead hr-1
        if da_cap:
            return None
        da_cap.append(khe_id)
        return de_xuat("hr-1", buoc=buoc, cha=b.cha, khoa_chong_trung=khoa("hr-1", b.cha),
                       lenh_kiem=[LENH_KIEM] if buoc == "code" else [], lenh_cho_phep=[LENH_KIEM],
                       ngan_sach={"so_lan_chay": so_lan, "phut": phut, "token_ra": 200000})
    t.pt.chon_phieu = chon
    t.app.state.cong_bo = (CauHinhCongBo("kho-tho", thoi_gian_cho_giay=30), NguonKhoTho({"B": b.tho.parent}),
                           lambda du_an: b.tram)
    kb = tmp_path / "kb.json"
    kb.write_text(json.dumps(kich_ban, ensure_ascii=False))
    home_token = tmp_path / "token-gia"
    home_token.mkdir(mode=0o700)
    ghi_token(home_token / "claude/oauth-token", "oauth-gia-lap")
    k = KheCauHinh("claude-1", "claude", "user:gia", tmp_path / "cfg1", "Claude 1", ("coder",))
    ch = CauHinhTho("B", "http://127.0.0.1:7700", (k,), CauHinhChay(day="kho-tho", han_chot_dung_mem_phut=1,
                                                                      path=os.environ["PATH"]))
    nc = NguCanhTho(ch, khach_asgi(t.app, t.token["B"]), goc=tmp_path / "tho-home", goc_kho=b.tho.parent,
                    goc_wt=tmp_path / "worktrees", principal_cua=lambda k, wt, ten: PrincipalGia(kb),
                    tao_cli=ChayClaude, chu_ky_nhip=0.2, cho_doc=0.05, cho_xong=5, cho_thu_lai=0.05,
                    don_uid=lambda pr: None,     # dọn theo UID của khe: GIẢ, không kill -1 thật (test_don_uid)
                    dong_ho=lambda: t.gio[0])    # đồng hồ thợ = đồng hồ trạm giả (han_giu do trạm cấp)
    return MayGia(t, b, nc, kb)


def lay_phieu(m: MayGia, nhan_luc: str | None = None):
    """Xin phiếu như nhịp tim rảnh; trả (khe, sổ khe, hộp thư, trạng thái phiếu). `nhan_luc` mặc định = bây giờ."""
    from tram.tho.hop_thu import HopThu
    from tram.tho.so_khe import SoKhe, TrangThaiPhieu, gio_utc
    p = m.t.goi("POST", "/api/tho/nhip", json_body={"khe_id": "B/claude-1", "buoc_tho": "ranh"}).json()["phieu"]
    so = SoKhe("B", "claude-1", m.nc.goc)
    return m.nc.ch.khe[0], so, HopThu(so.goc), TrangThaiPhieu(phieu=p, nhan_luc=nhan_luc or gio_utc(m.nc.dong_ho()))
