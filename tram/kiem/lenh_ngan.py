"""Lệnh hệ thống NGẮN có hạn TUYỆT ĐỐI (lát P1). `subprocess.run(timeout=…)` khi quá hạn gọi `kill()` rồi `wait()`
không hạn — nếu `kill()` bị từ chối (tiến trình là `sudo` chạy root) thì `Popen.__exit__` còn `wait()` trần, treo
mãi. Ở đây quá hạn → thử kill, đóng ống, KHÔNG chờ, trả mã None; đối tượng bỏ lại được `subprocess` tự gặt về sau.
Chỉ dùng cho `ps` (`cay_tien_trinh`) và `sudo -n -u … /bin/kill` (`Principal.kill_nhom`)."""
import subprocess


def chay_ngan(argv: list[str], *, timeout: float, doc: bool = False) -> tuple[int | None, bytes]:
    p = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE if doc else subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, start_new_session=True)
    try:
        ra, _ = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        try:
            p.kill()
        except OSError:
            pass
        if p.stdout is not None:
            p.stdout.close()
        return None, b""
    return p.returncode, ra or b""
