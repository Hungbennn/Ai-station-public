"""TC Task 6 (design D-5, D104, D109; review vòng 1 Q14): `BdDeNghi` — argv và stdin đúng như đã đo trên `bd 1.2.2`;
mô tả không nằm trong argv; không `-p`, `--parent`, `--claim`; mọi lệnh qua `chay_gioi_han` (nhóm tiến trình riêng, hạn
30 s, quá hạn thu hồi cả cây); lỗi chỉ mang lệnh con + mã thoát / loại lỗi; JSON `bd list` đã đo (liên kết
`discovered-from`) đọc được và không bị luật cứng 1a coi là chặn. Không chạy `bd` thật: runner giả, hoặc script giả
`bd-treo` (tên khác `bd` — bộ chặn host cấm spawn `bd`) chạy qua `chay_gioi_han` thật."""
import json
import os
import subprocess
import time

import pytest

from tram.beads.bd_de_nghi import HAN_BD, BdDeNghi, chay_bd_de_nghi
from tram.beads.doc_ds import doc_ds
from tram.beads.loi import LoiBd
from tram.cham_cot.luat_cung import bi_chan_boi
from tram.kiem.chay_gioi_han import chay_gioi_han
from tram.kiem.vong_doi import LoiThuHoi, kill_cuc_bo

# `bd list --json --all --limit 0` đã đo 18/10/2026 11:19 (design D-5), rút gọn hai việc.
DO_LIST = json.dumps([
    {"id": "thu-yt4", "title": "Viec goc", "description": "goc", "status": "open", "priority": 2,
     "issue_type": "task", "updated_at": "2026-10-18T11:19:41Z"},
    {"id": "thu-b0g", "title": "Viec moi do agent tao", "description": "moi", "status": "open", "priority": 2,
     "issue_type": "bug", "labels": ["tram:agent-tao"], "acceptance_criteria": "tieu chi 1",
     "created_by": "tram/de-nghi", "updated_at": "2026-10-18T11:19:42Z", "dependency_count": 0,
     "dependencies": [{"issue_id": "thu-b0g", "depends_on_id": "thu-yt4", "type": "discovered-from",
                       "created_at": "2026-10-18T11:19:42Z", "created_by": "tram/de-nghi", "metadata": "{}"}]}])
BD_TREO = """#!/bin/sh
printf '%s\\n' "$@" > "$TC_ARGV"
cat > "$TC_STDIN"
sleep 30 &
echo $! > "$TC_PID"
wait
"""


class Ghi:
    def __init__(self, ra="thu-b0g\n"):
        self.goi, self.ra = [], ra

    def __call__(self, args, dau_vao=None):
        self.goi.append((list(args), dau_vao))
        return self.ra


def test_tao_viec_moi_mo_ta_qua_stdin_khong_uu_tien():
    r, v = Ghi("ok\n"), Ghi()
    bd = BdDeNghi("/r/repo-nhap", runner=r, runner_vao=v)
    assert bd.tao_viec_moi("Cắt UTF-8 sai", loai="bug", mo_ta="MÔ TẢ BÍ\nviec_goc: rn-12", tieu_chi="- a\n- b") == \
        "thu-b0g"
    args, dau_vao = v.goi[0]
    assert args == ["-C", "/r/repo-nhap", "create", "Cắt UTF-8 sai", "-t", "bug", "-l", "tram:agent-tao",
                    "--body-file", "-", "--silent", "--actor", "tram/de-nghi", "--acceptance=- a\n- b"]
    assert dau_vao == "MÔ TẢ BÍ\nviec_goc: rn-12" and not any("MÔ TẢ" in a for a in args)
    assert not {"-p", "--priority", "--parent", "--claim", "-d"} & set(args)
    bd.tao_viec_moi("Không tiêu chí", loai="chore", mo_ta="m", tieu_chi="")
    assert not any(a.startswith("--acceptance") for a in v.goi[1][0])
    bd.lien_ket_phat_hien("thu-b0g", "thu-yt4")
    assert r.goi == [(["-C", "/r/repo-nhap", "dep", "add", "thu-b0g", "thu-yt4", "--type", "discovered-from",
                       "--actor", "tram/de-nghi"], None)]


@pytest.mark.parametrize("ra", ["", "a b\n", "Created issue thu-1 ok\n"])
def test_create_khong_tra_mot_ma_thi_loi(ra):
    with pytest.raises(LoiBd):
        BdDeNghi("/r", runner=Ghi(), runner_vao=Ghi(ra)).tao_viec_moi("t", loai="bug", mo_ta="m", tieu_chi="")


@pytest.mark.parametrize("tieu_de", ["-p0", "  --help", " "])
def test_tieu_de_co_the_thanh_co_bi_chan(tieu_de):
    v = Ghi()
    with pytest.raises(ValueError):
        BdDeNghi("/r", runner=Ghi(), runner_vao=v).tao_viec_moi(tieu_de, loai="bug", mo_ta="m", tieu_chi="")
    assert v.goi == []


def test_moi_lenh_qua_runner_so_huu_loi_chi_mang_ma_thoat():
    """Q14 + review vòng 1 (stderr có thể vọng lại tiêu đề / mô tả / đường dẫn): lỗi chỉ có lệnh con + mã thoát."""
    goi = []

    def gia(argv, **kw):
        goi.append((argv, kw))
        return subprocess.CompletedProcess(argv, 1, "", "TIÊU ĐỀ AGENT mô tả lỗi Dolt /r")
    with pytest.raises(LoiBd) as e:
        chay_bd_de_nghi(["-C", "/r", "create", "TIÊU ĐỀ AGENT", "-t", "bug"], "mô tả", chay=gia)
    assert str(e.value) == "bd create lỗi 1"
    argv, kw = goi[0]
    assert argv[:4] == ["bd", "-C", "/r", "create"] and kw["kill"] is kill_cuc_bo and kw["timeout"] == HAN_BD == 30
    assert (kw["input"], kw["capture_output"], kw["text"]) == ("mô tả", True, True)
    for loi in (subprocess.TimeoutExpired(["bd"], 30), LoiThuHoi("bd"), OSError("['bd']: không khởi chạy được")):
        with pytest.raises(LoiBd) as e:
            chay_bd_de_nghi(["-C", "/r", "dep", "add", "TIÊU ĐỀ", "b"], chay=lambda a, **kw: (_ for _ in ()).throw(loi))
        assert str(e.value) == f"Không chạy được bd dep: {type(loi).__name__}" and e.value.__cause__ is None
    bd = BdDeNghi("/r")
    assert bd._runner is chay_bd_de_nghi and bd._vao is chay_bd_de_nghi


def _con_song(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


def test_qua_han_thu_hoi_ca_nhom_tien_trinh(tmp_path, monkeypatch):
    """Q14 — hợp đồng ở mức lệnh giả: `bd` sinh tiến trình con treo, giữ ống ra → quá hạn: `LoiBd`, cả nhóm bị thu hồi
    (cháu `sleep` chết), không chờ 30 s; mô tả chỉ đi qua stdin, không nằm trong argv."""
    gia = tmp_path / "bd-treo"
    gia.write_text(BD_TREO)
    gia.chmod(0o755)
    for k in ("ARGV", "STDIN", "PID"):
        monkeypatch.setenv(f"TC_{k}", str(tmp_path / k.lower()))
    bat_dau = time.monotonic()
    with pytest.raises(LoiBd, match="^Không chạy được bd create: TimeoutExpired$"):
        chay_bd_de_nghi(["-C", "/r", "create", "Tiêu đề", "--body-file", "-"], "MÔ TẢ BÍ", han=1.0,
                        chay=lambda argv, **kw: chay_gioi_han([str(gia), *argv[1:]], **kw))
    assert time.monotonic() - bat_dau < 10
    pid, het = int((tmp_path / "pid").read_text()), time.monotonic() + 5
    while _con_song(pid) and time.monotonic() < het:
        time.sleep(0.05)
    assert not _con_song(pid)
    assert (tmp_path / "stdin").read_text() == "MÔ TẢ BÍ" and "MÔ TẢ" not in (tmp_path / "argv").read_text()


def test_json_da_do_doc_duoc_va_discovered_from_khong_chan():
    ds = doc_ds(DO_LIST)
    theo_id = {b.id: b for b in ds}
    moi = theo_id["thu-b0g"]
    assert [(p.depends_on_id, p.loai) for p in moi.phu_thuoc] == [("thu-yt4", "discovered-from")]
    assert moi.priority == 2 and moi.labels == ("tram:agent-tao",) and moi.assignee == "" and moi.parent == ""
    assert bi_chan_boi(moi, theo_id) == () and bi_chan_boi(theo_id["thu-yt4"], theo_id) == ()
