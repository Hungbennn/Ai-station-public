#!/bin/bash
# Giữ liền điều phối fixture/receipt/dọn; helper danh tính và giám sát đã tách ở cong-cu/.
# G3.11 giai đoạn 1: Đại ca chạy một lần trong Terminal.app, gõ dong-y; không cần mật khẩu.
# Chỉ đo dữ liệu giả; không cài daemon, không mở S6. Nguồn khởi chạy: Terminal của Đại ca.
# Mỗi lệnh 15 s, mỗi ca 60 s, đo 900 s + dự phòng dọn 90 s. Bash xử lý tín hiệu sau lệnh đang chờ.
# Ghi biên nhận trước lệnh ghi. Gỡ đúng nhãn rồi mới xoá dữ liệu; không kill theo tên.
# Mã: 0 ứng viên; 1 không kết luận; 2 không chạy; 3 dọn chưa rõ; 4 lọt; 130/142/143 ngắt.
# G3_GIA chỉ dành cho test lệnh giả, tuyệt đối không dùng khi đo thật.
set -u
D=$(cd "$(dirname "$0")" && pwd); REPO=$(cd "$D/../.." && pwd)
if [ -n "${G3_GIA:-}" ]; then
  B=$G3_GIA; SUDO=$B/sudo; LCTL=$B/launchctl; ID=$B/id; PS=$B/ps; PY=$G3_PY
  GOC=$B/goc; OUT=$B/out; NHA_TOI=$B/home; DEM=0; HAN_TONG=${G3_HAN_TONG:-120}
else
  [ -t 0 ] || { echo 'Không chạy: cần Terminal tương tác của Đại ca'; exit 2; }
  [ "${TERM_PROGRAM:-}" = Apple_Terminal ] || { echo 'Không chạy: cần Terminal.app'; exit 2; }
  if [ "${1:-}" != --trong-han ]; then
    read -r -p 'G3.11: thử nhãn launchd và canary giả, có dọn. Gõ dong-y để chạy: ' OK
    [ "$OK" = dong-y ] || { echo 'Không chạy'; exit 2; }; export G3_DONG_Y=dong-y
  fi
  [ "${G3_DONG_Y:-}" = dong-y ] || exit 2
  SUDO=/usr/bin/sudo; LCTL=/bin/launchctl; ID=/usr/bin/id; PS=/bin/ps; PY="${G3_PY:-$REPO/.venv/bin/python}"
  GOC=/Users/Shared/tram-kiem; OUT=$HOME/.tram/g3; NHA_TOI=$HOME; DEM=1; HAN_TONG=900
fi
[ "${1:-}" = --trong-han ] || exec /usr/bin/perl "$REPO/cong-cu/g3-giam-sat.pl" \
  "$HAN_TONG" 90 /bin/bash "$0" --trong-han
umask 077
LAN=$(date +%Y%m%d%H%M%S)-$$-$RANDOM; NHAN="vn.tram.g3r.$LAN"
mkdir -p "$OUT" && chmod 700 "$OUT" || exit 2
KHOA="$OUT/g3b.khoa"
mkdir "$KHOA" 2>/dev/null || { echo 'Không chạy: đang có lần đo khác hoặc khoá sót'; exit 2; }
P="$OUT/g3r-$LAN"; RC="$P.receipt"; : > "$RC" || exit 3
if [ -z "${G3_GIA:-}" ]; then exec > >(tee "$P.log") 2>&1
else : > "$P.log"; fi # sandbox Codex chặn /dev/fd; test nhận log qua stdout/stderr.
exec 4>&1
TKC=("$SUDO" -n -H -u tram-kiem)
W="$GOC/g3r-$LAN"; C="$NHA_TOI/tram-canary-$LAN"
E="${G3_GIA:-/Users/Shared}/g3r-$LAN.exec"
HET_CA=$((SECONDS + 60)); UIDK=; TOI=; DA_TK=0; KHONG_RO=0; DON_OK=0; DOC_NGOAI='?'; DOC_TRONG='?'
RECEIPT_LOI=0; LOT=0; CHUA_TOI=0; DANG_DON=0; HET_DON=0; HET_TONG=$HAN_TONG
. "$D/g3-rao-ho-so-probe.sh" --thu-vien
trap 'don >&4 2>&4' EXIT
tin_hieu
dung() { echo "KHÔNG KẾT LUẬN: $*"; exit 1; }

# R0: không sudo hay lệnh ghi fixture nào trước khi có khoá và bảng tiến trình sạch.
echo "G3.11 — lần $LAN; nguồn khởi chạy: Terminal của Đại ca (Terminal.app)"
echo 'Giữ giao_viec.bat=false, S6 đóng; không có lượt kiểm khác chạy đồng thời.'
TOI=$(han "$ID" -u); UIDK=$(han "$ID" -u tram-kiem)
[ "$TOI" = 501 ] && [ "$UIDK" = 503 ] || dung 'giai đoạn này cần đúng UID Đại ca 501 / tram-kiem 503'
bang || dung 'không đọc được ps (sandbox Codex có thể chặn; Claude kiểm ngoài sandbox)'
if [ -s "$P-ps.txt" ]; then cat "$P-ps.txt"; dung 'tram-kiem có tiến trình lạ — không giết'; fi
[ -x "$PY" ] || dung "thiếu Python của repo: $PY"
if [ -z "${G3_GIA:-}" ]; then
  han /usr/bin/sw_vers -buildVersion || dung 'không đọc được build macOS'
  han /usr/bin/git -C "$REPO" rev-parse HEAD || dung 'không đọc được SHA'
  han /usr/bin/id || dung 'không đọc được danh tính người chạy'
  han "$PY" -I -c '# G3R ho-so
import hashlib, sys
from pathlib import Path
from tram.giao_viec.cong_that import ho_so_cai
from tram.tho.quyen_kiem import HO_SO_KIEM, MANIFEST_KIEM
ho_so_cai(Path(sys.argv[1]))
for p in (HO_SO_KIEM, MANIFEST_KIEM):
    print(p, hashlib.sha256(p.read_bytes()).hexdigest())' "$GOC" || dung 'hồ sơ/manifest cài không hợp lệ'
else
  echo 'TEST GIẢ: bỏ đọc hồ sơ hệ thống; argv vẫn dựng bằng boc_luot thật'
fi
DA_TK=1
[ "$(han "${TKC[@]}" /usr/bin/id -u)" = "$UIDK" ] || dung 'đối chứng UID người gửi không phải 503'
echo "người gửi ngoài hồ sơ: UID=$UIDK; ASID ghi từ chính lệnh gửi khi đo thật"
[ -n "${G3_GIA:-}" ] || han "${TKC[@]}" /usr/bin/id || dung 'không đọc được nhóm người gửi'

MIENS="gui/$TOI user/$TOI gui/$UIDK user/$UIDK system"
tao_dir toi "$C" 755; tao_dir toi "$E" 755
tao_dir tk "$W" 755; tao_dir tk "$W.nha" 700
viet tk "$W.nha/tmp" "${TKC[@]}" /bin/mkdir -m 700 "$W.nha/tmp" || dung 'không tạo TMP'
viet toi "$E/out-$TOI" /bin/mkdir -m 700 "$E/out-$TOI" || dung 'không tạo đầu ra 501'
viet tk "$W/out-$UIDK" "${TKC[@]}" /bin/mkdir -m 700 "$W/out-$UIDK" || dung 'không tạo đầu ra 503'
viet toi "$E/probe.sh" /bin/cp "$D/g3-rao-ho-so-probe.sh" "$E/probe.sh" || dung 'không chép probe'
viet toi "$E/probe.sh" /bin/chmod 555 "$E/probe.sh" || dung 'không đặt quyền probe'
viet toi "$E/lenh.py" /bin/cp "$REPO/cong-cu/g3-lenh.py" "$E/lenh.py" || dung 'không chép wrapper đo'
viet toi "$E/lenh.py" /bin/chmod 444 "$E/lenh.py" || dung 'không siết wrapper đo'
viet toi "$C/data" "$PY" -I -c 'import os,sys; open(sys.argv[1],"x").write(os.urandom(32).hex())' \
  "$C/data" || dung 'không tạo canary'
viet toi "$C/data" /bin/chmod 644 "$C/data" || dung 'không đặt quyền canary'
viet toi "$E/data" /bin/cp "$C/data" "$E/data" || dung 'không tạo canary DAC ngoài nhà'
viet toi "$E/data" /bin/chmod 644 "$E/data" || dung 'không chmod canary ngoài nhà'
if [ -z "${G3_GIA:-}" ]; then
  han /bin/ls -lde "$NHA_TOI" "$C" "$C/data" "$E/probe.sh"
  # Kiểm quyền thực kể cả ACL trên probe và toàn bộ chuỗi cha, dưới UID 503.
  p="$E/probe.sh"
  while :; do
    acl=$(han /bin/ls -lde "$p") || dung 'không ghi được quyền/ACL chuỗi cha'
    printf '%s\n' "$acl"
    [ "$(printf '%s\n' "$acl" | wc -l | tr -d ' ')" = 1 ] || dung 'chuỗi probe có ACL cần đối soát'
    if [ "$p" = /Users/Shared ]; then
      # %Lp bỏ bit sticky (đo 19/10: 0:777) — so cả chế độ bát phân đầy đủ.
      [ "$(han /usr/bin/stat -f '%u:%p' "$p")" = 0:41777 ] || dung 'Shared thiếu sticky/root'
      m=1 # Sticky bảo vệ entry E do 501 sở hữu; không tin thư mục con ghi được bởi 503.
    else han "${TKC[@]}" /bin/test -w "$p"; m=$?; fi
    [ "$m" = 1 ] || dung "503 ghi được/không kiểm được probe hoặc chuỗi cha: $p"
    [ "$p" != / ] || break; p=$(dirname "$p")
  done
  for p in "$E" "$W"; do
    han "${TKC[@]}" /bin/test -x "$p" || dung "503 không traverse được $p"
  done
  han /bin/test -w "$W/out-$UIDK"; [ $? = 1 ] || dung '501 ghi được đầu ra 503'
  han "${TKC[@]}" /bin/test -w "$E/out-$TOI"; [ $? = 1 ] || dung '503 ghi được đầu ra 501'
  han "${TKC[@]}" /bin/test -w "$W/out-$UIDK" || dung '503 không ghi được đầu ra của mình'
  han /bin/test -w "$E/out-$TOI" || dung '501 không ghi được đầu ra của mình'
  han /bin/ls -lde "$E/out-$TOI" "$W/out-$UIDK" > "$P-output-permissions.txt" || dung 'lỗi quyền đầu ra'
  [ "$(wc -l < "$P-output-permissions.txt" | tr -d ' ')" = 2 ] || dung 'đầu ra có ACL ngoài dự tính'
  cat "$P-output-permissions.txt"
  han "$PY" -I -c 'import os,stat,sys
for p,u in zip(sys.argv[1::2],sys.argv[2::2]):
    s=os.lstat(p)
    assert stat.S_ISDIR(s.st_mode) and s.st_uid==int(u) and stat.S_IMODE(s.st_mode)==0o700' \
    "$E/out-$TOI" "$TOI" "$W/out-$UIDK" "$UIDK" || dung 'đầu ra sai chủ/quyền'
fi
viet tk "$W/launchctl-copy" "${TKC[@]}" /bin/cp "$LCTL" "$W/launchctl-copy" || dung 'không chép launchctl'
viet tk "$W/launchctl-copy" "${TKC[@]}" /bin/chmod 755 "$W/launchctl-copy" || dung 'không chmod bản chép'
han "${TKC[@]}" /usr/bin/cmp -s "$LCTL" "$W/launchctl-copy" || dung 'bản chép khác byte'
viet tk "$W/positive.sh" "${TKC[@]}" /bin/cp "$E/probe.sh" "$W/positive.sh" || dung 'thiếu chương trình dương'
viet tk "$W/positive.sh" "${TKC[@]}" /bin/chmod 755 "$W/positive.sh" || dung 'không chmod đối chứng'
han /bin/cat "$C/data" | viet tk "$W/expected" "${TKC[@]}" /usr/bin/tee "$W/expected" >/dev/null \
  || dung 'thiếu dấu canary trong lượt'
printf g3r | viet tk "$W/local" "${TKC[@]}" /usr/bin/tee "$W/local" >/dev/null || dung 'thiếu file dương'
viet tk "$W/link" "${TKC[@]}" /bin/ln -s "$C/data" "$W/link" || dung 'không tạo symlink canary'

BOC='import sys
from pathlib import Path
from tram.giao_viec.principal_kiem import tu_cach_ly
a = tu_cach_ly("user:tram-kiem").boc_luot(Path(sys.argv[1]))(sys.argv[2:])
sys.stdout.buffer.write(b"\0".join(s.encode() for s in a) + b"\0")'
trong() { # Không tự ghép lệnh sandbox. Đọc argv NUL từ boc_luot, rồi chạy nguyên mảng.
  local x; local a=()
  han "$PY" -I -c "$BOC" "$W" "$@" > "$P-argv.tmp" || return 125
  while IFS= read -r -d '' x; do a+=("$x"); done < "$P-argv.tmp"
  [ "${#a[@]}" -gt 0 ] || return 125
  [ -z "${G3_GIA:-}" ] || a[0]=$SUDO
  printf 'boc_luot argv: '; printf '%q ' "${a[@]}"; echo
  han "${a[@]}"
}
plist() {
  # plistlib thoát XML cho đường dẫn; fixture RunAtLoad, không KeepAlive.
  han "$PY" -I -c 'import plistlib,sys
print(plistlib.dumps({"Label":sys.argv[1], "RunAtLoad":True,
    "ProgramArguments":sys.argv[2:]}).decode(),end="")' "$NHAN.$1" "$E/probe.sh" job "$LAN" "$1" \
    "$E/out-$TOI" "$W/out-$UIDK"
}
do_lenh() { # prefix thuộc LUOT 503, hoặc E 501 cho đối chứng chủ miền.
  local ai=$1 prefix=$2; shift 2
  if [ -n "${G3_GIA:-}" ]; then
    case "$ai" in trong) trong "$@";; chu) han "$@";; *) han "${TKC[@]}" "$@";; esac
  else
    case "$ai" in
      trong) trong /usr/bin/python3 -I "$E/lenh.py" "$prefix" "$@";;
      chu) han /usr/bin/python3 -I "$E/lenh.py" "$prefix" "$@";;
      *) han "${TKC[@]}" /usr/bin/python3 -I "$E/lenh.py" "$prefix" "$@";;
    esac
  fi
}
command_info() {
  local che=$1 prefix=$2 ca=$3 ASID
  if [ -z "${G3_GIA:-}" ]; then
    if [ "$che" = chu ]; then han /bin/cat "$prefix.actor" > "$P-$ca.actor"
    else han "${TKC[@]}" /bin/cat "$prefix.actor" > "$P-$ca.actor"; fi
    if [ "$che" = chu ]; then han /bin/cat "$prefix.status" > "$P-$ca.status"
    else han "${TKC[@]}" /bin/cat "$prefix.status" > "$P-$ca.status"; fi
    cat "$P-$ca.actor" "$P-$ca.status"
    han "$PY" -I -c 'import json,sys
a=json.load(open(sys.argv[1])); assert a["pid"]>0 and a["born"] and a["uid"]==a["euid"]==int(sys.argv[2])' \
      "$P-$ca.actor" "$([ "$che" = chu ] && echo "$TOI" || echo "$UIDK")" || CHUA_TOI=1
    ASID=$(han "$PY" -I -c 'import json,sys; a=json.load(open(sys.argv[1])); print(a["asid"] or "")' "$P-$ca.actor")
    case "$ASID" in ''|*[!0-9]*) CHUA_TOI=1;; *)
      case " $MIENS " in *" login/$ASID "*) :;; *) MIENS="$MIENS login/$ASID";; esac;; esac
    # Không dùng mã 137 suy ra signal: status là waitstatus thật; thiếu/signal/timeout không chấm đạt.
    han "$PY" -I -c 'import json,sys
s=json.load(open(sys.argv[1])); assert not s["signal"] and not s["timeout"]' "$P-$ca.status" || CHUA_TOI=1
  fi
}
thu() { # ca, ngoài/trong/chủ miền, binary, subcommand, miền bootstrap
  local ca=$1 che=$2 bin=$3 sub=$4 domain=${5:-} m accepted=khong seen=0 identity=0; shift 5
  local label="$NHAN.$ca"; local a=(); local bat=$SECONDS; HET_CA=$((SECONDS + 60))
  if [ "$sub" = submit ]; then
    a=("$bin" submit -l "$label" -- "$E/probe.sh" job "$LAN" "$ca" "$E/out-$TOI" "$W/out-$UIDK")
  else
    if [ "$che" = chu ]; then # launchd đòi plist của miền gui do chính chủ miền sở hữu
      plist "$ca" | viet toi "$C/$ca.plist" /usr/bin/tee "$C/$ca.plist" >/dev/null || dung 'không dựng plist'
      a=("$bin" bootstrap "$domain" "$C/$ca.plist")
    else
      plist "$ca" | viet tk "$W/$ca.plist" "${TKC[@]}" /usr/bin/tee "$W/$ca.plist" >/dev/null \
        || dung 'không dựng được plist'
      viet tk "$W/$ca.plist" "${TKC[@]}" /bin/chmod 644 "$W/$ca.plist" || dung 'không chmod plist'
      a=("$bin" bootstrap "$domain" "$W/$ca.plist")
    fi
  fi
  ghi "evidence|$E/out-$TOI/$ca.txt|toi"; ghi "evidence|$W/out-$UIDK/$ca.txt|tk"
  ghi "job|$label|$che"
  local prefix="$W/$ca.command"; [ "$che" != chu ] || prefix="$E/$ca.command"
  ghi "command|$prefix|$che"
  do_lenh "$che" "$prefix" "${a[@]}" > "$P-$ca.out" 2> "$P-$ca.err"; m=$?
  command_info "$che" "$prefix" "$ca"
  printf "%s: actor_uid=%s observer_uid=%s elapsed=%ss shell_rc=%s (signal xem waitstatus)\n" "$ca" "$([ "$che" = chu ] && echo "$TOI" || echo "$UIDK")" "$TOI" "$((SECONDS-bat))" "$m"
  echo "$ca: mã $m; stderr (tối đa 240 byte): $(head -c 240 "$P-$ca.err" | LC_ALL=C tr -cd '\11\12\15\40-\176')"
  tim "$label"; [ -z "$MIEN" ] || seen=1
  [ "$m" != 0 ] && [ "$seen" = 0 ] || accepted=co
  JOB_UID='?'; JOB_CHAY=khong
  if [ "$accepted" = co ]; then danh_tinh_job "$ca" && identity=1; fi
  printf '%s/%s|UID=%s\n' "$accepted" "$JOB_CHAY" "$JOB_UID" > "$P-$ca.result"
  [ "$m" != 0 ] || [ "$seen" = 1 ] || KHONG_RO=1
  if [ "$che" = trong ] && [ "$accepted" = co ]; then LOT=1; echo "LỌT: $ca"; exit 4; fi
  [ "$DOC_OK" = 1 ] || dung 'không quan sát đủ các miền context'
  don_nhan "$label" || { echo 'dọn nhãn chưa xác nhận'; exit 3; }
  [ "$LOT" = 0 ] || { echo "LỌT: thấy nhãn trong lúc dọn $ca"; exit 4; }
  [ "$m" != 124 ] && [ "$m" != 142 ] || dung "hết hạn ca $ca"
  if [ "$che" = nen ]; then
    echo "$ca: bootstrap ngoài hồ sơ mã $m (rào OS nền); không tính riêng cho Seatbelt"
  elif [ "$che" != trong ]; then
    [ "$m" = 0 ] && [ "$seen" = 1 ] && [ "$identity" = 1 ] || {
      CHUA_TOI=1; echo "đối chứng $ca không tái hiện"; return 1; }
  elif [ "$bin" = "$W/launchctl-copy" ]; then
    # Cần dấu đã tới subcommand; exec/plist hỏng hoặc chỉ có mã 5 không phải bằng chứng rào.
    /usr/bin/grep -Eiq "^($sub failed:|launchctl: $sub failed:)" "$P-$ca.err" \
      && ! /usr/bin/grep -Eiq 'exec|not found|usage:|plist|No such file|Invalid' "$P-$ca.err" \
      && [ "$m" != 126 ] && [ "$m" != 127 ] || { CHUA_TOI=1; echo "$ca: CHƯA CHẮC bản chép tới subcommand"; }
  fi
}

# M2 và M3 dùng cùng byte; lỗi dụng cụ không ngăn canary sau khi dọn xác nhận.
M3_SAN=1
thu m2-original ngoai "$LCTL" submit '' || M3_SAN=0
HET_CA=$((SECONDS + 60)); bat=$SECONDS
if [ -z "${G3_GIA:-}" ]; then
  for f in "$LCTL" "$W/launchctl-copy"; do
    han /usr/bin/shasum -a 256 "$f"
    han /bin/ls -ldeO@ "$f"
    han /usr/bin/codesign -dv --verbose=2 "$f" 2>&1 | head -c 2000
  done > "$P-copy-metadata.txt" 2>&1
fi
do_lenh ngoai "$W/copy-help.command" "$W/launchctl-copy" help > "$P-copy-help.out" 2> "$P-copy-help.err"; m=$?
echo "copy-help: elapsed=$((SECONDS-bat))s shell_rc=$m; signal xem waitstatus"
command_info ngoai "$W/copy-help.command" copy-help
if [ "$m" = 0 ]; then
  thu m2-copy ngoai "$W/launchctl-copy" submit '' || M3_SAN=0
else
  M3_SAN=0; CHUA_TOI=1
  echo 'copy-help: lỗi thực thi; không quy SIGKILL cho Seatbelt; giữ metadata trước dọn'
  if [ -z "${G3_GIA:-}" ]; then
    pid=$(han "$PY" -I -c 'import json,sys; print(json.load(open(sys.argv[1]))["pid"])' "$P-copy-help.actor")
    case "$pid" in ''|*[!0-9]*) echo 'không có PID để lấy chẩn đoán OS';;
      *) begin=$(han "$PY" -I -c 'import json,sys; print(json.load(open(sys.argv[1]))["wall_start"])' "$P-copy-help.actor")
        end=$(han "$PY" -I -c 'import json,sys; print(json.load(open(sys.argv[1]))["wall_end"])' "$P-copy-help.status")
        han /usr/bin/log show --start "$begin" --end "$end" --style compact --predicate "processID == $pid" \
        2>&1 | head -c 2048 > "$P-copy-help-os.txt"
        echo 'Chẩn đoán OS giới hạn đúng PID/khoảng thực thi; có thể không chứa termination reason.';; esac
  fi
fi
# Bootstrap có đối chứng chủ miền riêng; nền OS không phải kết quả Seatbelt.
thu owner chu "$LCTL" bootstrap "gui/$TOI" || M3_SAN=0
thu baseline-gui nen "$LCTL" bootstrap "gui/$TOI"
thu baseline-user nen "$LCTL" bootstrap "user/$UIDK"
HET_CA=$((SECONDS + 60))
trong "$W/positive.sh" identity > "$P-positive.txt" 2>&1 || dung 'đối chứng dương trong LUOT không chạy'
cat "$P-positive.txt"
/usr/bin/grep -q "^UID=$UIDK RUID=$UIDK " "$P-positive.txt" || dung 'danh tính trong hồ sơ sai'
if [ "$M3_SAN" = 1 ]; then
  # Exec thành công trong chính hồ sơ + đối chứng nhận job ngoài hồ sơ + lỗi thao tác + không có nhãn.
  do_lenh trong "$W/copy-help-in.command" "$W/launchctl-copy" help > "$P-copy-help-in.out" 2> "$P-copy-help-in.err" || CHUA_TOI=1
  command_info trong "$W/copy-help-in.command" copy-help-in
  han "${TKC[@]}" /usr/bin/cmp -s "$LCTL" "$W/launchctl-copy" || dung 'binary/digest thay đổi sau đối chứng'
  for loai in original copy; do
    bin=$LCTL; [ "$loai" != copy ] || bin="$W/launchctl-copy"
    thu "m3-$loai-submit" trong "$bin" submit ''
    thu "m3-$loai-gui" trong "$bin" bootstrap "gui/$TOI"
    thu "m3-$loai-user" trong "$bin" bootstrap "user/$UIDK"
  done
else echo 'M3: CHƯA ĐO — đối chứng thực thi/submit chưa hợp lệ'; fi
# Canary đọc được là ghi nhận lỗ hiện hành; không đánh trượt rào launchd.
HET_CA=$((SECONDS + 60))
han "${TKC[@]}" /bin/bash "$E/probe.sh" read "$C" "$W" "$E" > "$P-read-out.txt" 2>&1 \
  || dung 'đối chứng file trong LUOT ngoài hồ sơ lỗi'
trong /bin/bash "$W/positive.sh" read "$C" "$W" "$E" > "$P-read-in.txt" 2>&1 \
  || dung 'đối chứng file trong LUOT trong hồ sơ lỗi'
for c in out in; do cat "$P-read-$c.txt"; done
DOC_NGOAI=không; DOC_TRONG=không
/usr/bin/grep -q 'content=co' "$P-read-out.txt" && DOC_NGOAI=có
/usr/bin/grep -q 'content=co' "$P-read-in.txt" && DOC_TRONG=có
echo "Canary độc lập: ngoài=$DOC_NGOAI trong=$DOC_TRONG; DAC có thể đã chặn ngoài hồ sơ"
[ "$CHUA_TOI" = 0 ] || dung 'bản chép launchctl chưa chắc tới subcommand — xem phase/waitstatus, chưa kết luận rào'
exit 0
