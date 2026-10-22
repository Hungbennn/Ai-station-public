"""Toolchain kiểm ghim theo bản máy B; đổi pin phải cài lại hồ sơ/manifest và đo G4."""

PYTHON = '/usr/local/tram/toolchains/python/3.12.15-20261009'
UV = '/opt/homebrew/Cellar/uv/0.13.0'
GIT = '/opt/homebrew/Cellar/git/2.56.0_1'
NODE = '/opt/homebrew/Cellar/node/26.5.0'
# Homebrew dời npm khỏi Cellar; bin/npm của Node ghim là symlink vào đây (đo máy B 19/10 21:50).
NPM = '/opt/homebrew/lib/node_modules/npm'
PHU_THUOC = (
    '/opt/homebrew/Cellar/pcre2/10.49',
    '/opt/homebrew/Cellar/json-c/0.19',
    '/opt/homebrew/Cellar/libunistring/1.4.2',
    '/opt/homebrew/Cellar/gettext/1.0',
    '/opt/homebrew/Cellar/fmt/12.2.0',
    '/opt/homebrew/Cellar/ada-url/3.4.4',
    '/opt/homebrew/Cellar/brotli/1.2.0',
    '/opt/homebrew/Cellar/c-ares/1.34.8',
    '/opt/homebrew/Cellar/hdrhistogram_c/0.11.10',
    '/opt/homebrew/Cellar/icu4c@78/78.3',
    '/opt/homebrew/Cellar/libffi/3.7.1',
    '/opt/homebrew/Cellar/libnghttp2/1.69.0',
    '/opt/homebrew/Cellar/libnghttp3/1.17.0',
    '/opt/homebrew/Cellar/ca-certificates/2026-07-16',
    '/opt/homebrew/Cellar/openssl@3/3.6.3',
    '/opt/homebrew/Cellar/libngtcp2/1.24.0',
    '/opt/homebrew/Cellar/libuv/1.52.1',
    '/opt/homebrew/Cellar/llhttp/9.4.2',
    '/opt/homebrew/Cellar/simdutf/9.0.0',
    '/opt/homebrew/Cellar/merve/1.2.2_1',
    '/opt/homebrew/Cellar/nbytes/0.1.4',
    '/opt/homebrew/Cellar/simdjson/4.6.4',
    '/opt/homebrew/Cellar/readline/8.3.3',
    '/opt/homebrew/Cellar/sqlite/3.53.3',
    '/opt/homebrew/Cellar/uvwasi/0.0.23',
    '/opt/homebrew/Cellar/lz4/1.10.0',
    '/opt/homebrew/Cellar/xz/5.8.3',
    '/opt/homebrew/Cellar/zstd/1.5.7_1',
    NPM,
)
PREFIX = (PYTHON, UV, GIT, NODE)
PATH_KIEM = ':'.join(f'{p}/bin' for p in PREFIX) + ':/usr/bin:/bin:/usr/sbin:/sbin'
HE_THONG = ('/bin', '/usr/bin', '/usr/lib', '/usr/libexec', '/usr/share', '/System/Library',
             '/System/Cryptexes/OS/usr/lib', '/System/Volumes/Preboot/Cryptexes/OS/usr/lib',
             '/System/Cryptexes/OS/System/Library/dyld',
             '/System/Volumes/Preboot/Cryptexes/OS/System/Library/dyld', '/private/var/db/timezone')
LITERAL = ('/dev/null', '/dev/zero', '/dev/random', '/dev/urandom', '/private/etc/localtime',
           '/dev/fd')


def manifest() -> dict:
    return {'python': PYTHON, 'prefix': list((*PREFIX, *PHU_THUOC)),
            'he_thong': list(HE_THONG), 'literal': list(LITERAL)}


def bien_kiem(nha: str) -> dict[str, str]:
    return {'PATH': PATH_KIEM, 'UV_PYTHON': f'{PYTHON}/bin/python3.12', 'UV_PYTHON_DOWNLOADS': 'never',
            'UV_OFFLINE': '1', 'PYTHONDONTWRITEBYTECODE': '1',
            'UV_CACHE_DIR': f'{nha}/.cache/uv', 'UV_TOOL_DIR': f'{nha}/.local/uv',
            'XDG_CONFIG_HOME': f'{nha}/.config', 'XDG_CACHE_HOME': f'{nha}/.cache',
            'NPM_CONFIG_CACHE': f'{nha}/.cache/npm', 'NPM_CONFIG_USERCONFIG': f'{nha}/.npmrc'}
