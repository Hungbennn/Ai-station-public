"""ACL chỉ cấp một lần trên cây mới; thu quyền ở cổng cha, không chmod file UID khe."""
import pwd
from pathlib import Path
from tram.tho.principal import USER_RE

QUYEN_CAY = 'read,write,append,execute,delete,readattr,readextattr,readsecurity'
QUYEN_THU_MUC = 'list,search,add_file,add_subdirectory,readattr,readextattr,readsecurity'
QUAN_LY = 'read,write,append,execute,delete,delete_child,readattr,writeattr,readextattr,writeextattr,readsecurity'


def lenh_quyen_b(wt: Path, hang_doi: Path, *, user: str) -> list[list[str]]:
    if not USER_RE.fullmatch(user):
        raise ValueError('Tên principal không hợp lệ')
    if not (wt / '.git').is_file() or (wt / '.git').is_symlink():
        raise ValueError('Cần worktree do quản lý tạo')
    def acl(p, quyen, who=user):
        return ['/bin/chmod', '+a', f'user:{who} allow {quyen}', str(p)]
    ds = [['/bin/chmod', '700', str(wt)], ['/bin/chmod', '700', str(hang_doi.parent)],
          acl(hang_doi.parent, 'list,search,readattr,readsecurity'),
          acl(wt, QUYEN_THU_MUC),
          ['/bin/chmod', '+a', f'user:{user} deny write,append,delete,writeattr,writeextattr,writesecurity,chown',
           str(wt / '.git')]]
    # Kế thừa cho file mới kể cả umask 077. Quản lý đọc/ghi/dọn được file UID khe;
    # chủ file cố ý gỡ ACL thì thất bại đóng, không mở sudo root để cưỡng ép.
    for who, quyen in ((pwd.getpwuid(wt.stat().st_uid).pw_name, QUAN_LY), (user, QUYEN_CAY)):
        ds.append(['/usr/bin/find', str(wt), '-mindepth', '1', '(', '-path', str(wt / '.git'), '-o', '-path',
                   str(wt / '.tram'), ')', '-prune', '-o', '(', '-type', 'd', '-o', '-type', 'f', ')',
                   '-exec', '/bin/chmod', '+a', f'user:{who} allow {quyen},file_inherit,directory_inherit', '{}', '+'])
        ds.append(acl(wt, f'{quyen},only_inherit,file_inherit,directory_inherit', who))
    # .tram và .git không thể bị thay tên: root không cấp delete_child, .tram không cấp delete.
    ds += [acl(wt / '.tram', 'read,execute,readattr,readsecurity,file_inherit,directory_inherit'),
           acl(hang_doi, 'read,append,readattr,readsecurity')]
    for p in [*(wt / '.tram').glob('goi*.md'), *(hang_doi.parent / n for n in ('settings.json', 'mcp.json'))]:
        if p.is_file():
            ds.append(acl(p, 'read,readattr,readsecurity'))
    return ds


def trao_quyen_b(wt, hang_doi, *, user, chay):
    for argv in lenh_quyen_b(wt, hang_doi, user=user):
        chay(argv, check=True, capture_output=True, timeout=30)
