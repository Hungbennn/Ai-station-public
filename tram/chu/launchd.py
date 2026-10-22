import plistlib
from pathlib import Path

NHAN_QUET = "vn.tram.quet"
NHAN_API = "vn.tram.api"
NHAN_BAO_TIN = "vn.tram.bao-tin"
NHAN_SAO_LUU = "vn.tram.sao-luu"
NHAN_NHO = "vn.tram.nho"          # memory service (spec 1b §9, §15) — chỉ cài qua `tram chu cai-dat --nho`
# launchd không có ~/.local/bin (nơi `bd` nằm trên máy B) — ghép thêm ở đầu PATH.
PATH_HE_THONG = "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"


def _chung(nhan: str, lenh: list[str], *, uv: str, repo: Path, log: Path) -> dict:
    return {
        "Label": nhan,
        "ProgramArguments": [uv, "run", "--project", str(repo), "tram", *lenh],
        "WorkingDirectory": str(repo),
        "StandardOutPath": str(log),
        "StandardErrorPath": str(log),
        "EnvironmentVariables": {"PATH": f"{Path.home() / '.local/bin'}:{PATH_HE_THONG}"},
    }


def tao_plist(*, uv: str, repo: Path, log: Path, chu_ky_giay: int = 120) -> bytes:
    return plistlib.dumps({**_chung(NHAN_QUET, ["quet", "--ghi"], uv=uv, repo=repo, log=log),
                           "StartInterval": chu_ky_giay, "RunAtLoad": True})


def tao_plist_thuong_truc(nhan: str, lenh: list[str], *, uv: str, repo: Path, log: Path) -> bytes:
    """Dịch vụ chạy liên tục; thoát mã 0 (vd chưa cấu hình Telegram) thì launchd không bật lại."""
    return plistlib.dumps({**_chung(nhan, lenh, uv=uv, repo=repo, log=log),
                           "RunAtLoad": True, "KeepAlive": {"SuccessfulExit": False}})


def tao_plist_hang_ngay(nhan: str, lenh: list[str], *, uv: str, repo: Path, log: Path,
                        gio: int = 3, phut: int = 15) -> bytes:
    return plistlib.dumps({**_chung(nhan, lenh, uv=uv, repo=repo, log=log),
                           "StartCalendarInterval": {"Hour": gio, "Minute": phut}})
