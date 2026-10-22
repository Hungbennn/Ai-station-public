"""CHỈ TEST: thay UID/exec bằng bản giả, giữ mở file kín và truyền FD của wrapper thật."""
import os
import sys
from pathlib import Path

from tram.tho.claude_token import CLI, FD_ENV, chay


def exec_gia(cli, argv, env):
    assert cli == CLI
    # Biến của fixture, không có đường tiêm tương ứng trong điểm vào sản phẩm.
    env |= {k: os.environ[k] for k in ("PYTHONPATH", "CLI_GIA_KICH_BAN", "GIT_CONFIG_GLOBAL", "GIT_CONFIG_NOSYSTEM")}
    os.execve(sys.executable, [sys.executable, __file__, "--cli", *argv[1:]], env)


if __name__ == "__main__":
    if sys.argv[1] == "--cli":
        fd = int(os.environ.pop(FD_ENV))
        assert os.read(fd, 4097) == b"oauth-gia-lap"
        os.close(fd)
        sys.argv = [str(Path(__file__).with_name("cli_gia.py")), *sys.argv[2:]]
        from cli_gia import main
        raise SystemExit(main())
    p = Path(sys.argv[1])
    chay(sys.argv[2:], kiem_token=lambda: p, exec_cli=exec_gia)
