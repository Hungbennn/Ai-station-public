from tram.duong_dan import bay_gio, tram_home


def _co():
    return tram_home() / "estop"


def bat(ly_do: str) -> None:
    _co().write_text(f"{bay_gio()} {ly_do}\n", encoding="utf-8")


def tat() -> None:
    _co().unlink(missing_ok=True)


def dang_bat() -> bool:
    return _co().exists()
