"""Ép model/effort trước spawn; stream chỉ xác nhận model, effort lưu theo yêu cầu."""
import re


def models(raw):
    if not isinstance(raw, (list, tuple)) or any(x not in ("sonnet", "opus") for x in raw):
        raise ValueError("models chỉ nhận danh sách sonnet/opus")
    return tuple(dict.fromkeys(raw))


def lenh_model(argv, cli, ho_tro, co):
    if co is None:
        return argv
    model = co["model"]
    if cli != "claude" or model not in ho_tro:
        raise ValueError("Không ép được model yêu cầu")
    return [*argv, "--model", model] + (["--effort", co["effort"]] if "effort" in co else [])


def dung_model(co, kq):
    if co is None:
        return True
    return bool(not kq.model_lech and kq.co_assistant and kq.mo_hinh and re.fullmatch(
        r"claude-" + re.escape(co["model"]) + r"-[0-9]+(?:-[0-9]+)*(?:\[1m\])?", kq.mo_hinh))
