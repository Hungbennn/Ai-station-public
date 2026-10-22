#!/bin/bash
# Giữ chung vòng đời năm biến thể và dọn theo một receipt; probe/giám sát tách riêng.
# G3.12 — tách phiên, giai đoạn 2 M1. Đại ca chạy: bash docs/handovers/g3-phien-rieng.sh trong Terminal.app.
# Gõ dong-y; sudo -v hỏi mật khẩu một lần. Đo V1 gui, V2/V3 system/501, V4/V5 system/Uq, tắt/bật SessionCreate.
# Đo PID cha và lá do probe tự báo; submit job cố định báo UID thật, không touch. Không có hồ sơ Seatbelt.
# Root chỉ cài/gỡ đúng plist + chương trình lần này (trong /usr/local/tram, KHÔNG phải /Library/LaunchDaemons
# để sót cũng không tự nạp khi khởi động), bootstrap/bootout system và đọc procinfo. Lá dùng sudo -n.
# Mỗi lệnh tối đa 15s (sudo -v 60s), đo 30s + dọn 60s/ca, đo tổng 600s + dự phòng dọn 90s; trap dọn theo receipt trước lệnh ghi.
# SIGKILL/mất điện không bắt được: giữ receipt/khoá để phục hồi tay. Test dùng G3_GIA, không gọi host thật.
# Mã: 0 đo xong, 1 không kết luận, 2 không chạy, 3 dọn chưa xác nhận, 130/142/143 ngắt đã dọn.
set -u
export LC_ALL=C
D=$(cd "$(dirname "$0")" && pwd)
if [ -n "${G3_GIA:-}" ]; then
  B=$G3_GIA; OUT=$B/out; TMP=$B; ROOT=$B/root; CHO=0; TONG=${G3_HAN_TONG:-600}
  SUDO=$B/sudo; LCTL=$B/launchctl; PS=$B/ps; ID=$B/id; INSTALL=$B/install; RM=$B/rm; PLUTIL=$B/plutil
else
  [ -t 0 ] || { echo 'Không chạy: cần Terminal tương tác.'; exit 2; }
  if [ "${1:-}" != --trong-han ]; then
    read -r -p 'G3.12: cài/gỡ năm job đo; sudo root có mật khẩu. Gõ dong-y: ' OK
    [ "$OK" = dong-y ] || exit 2; export G3_DONG_Y=dong-y
  fi
  [ "${G3_DONG_Y:-}" = dong-y ] || exit 2
  OUT=$HOME/.tram/g3; TMP=/Users/Shared; ROOT=/usr/local/tram; CHO=1; TONG=600
  SUDO=/usr/bin/sudo; LCTL=/bin/launchctl; PS=/bin/ps; ID=/usr/bin/id
  INSTALL=/usr/bin/install; RM=/bin/rm; PLUTIL=/usr/bin/plutil
fi
[ "${1:-}" = --trong-han ] || exec /usr/bin/perl "$D/../../cong-cu/g3-giam-sat.pl" \
  "$TONG" 90 /bin/bash "$0" --trong-han
umask 077
LAN=$(date +%Y%m%d%H%M%S)-$$; mkdir -p "$OUT" && chmod 700 "$OUT" || exit 2
KHOA=$OUT/g3b.khoa
mkdir "$KHOA" 2>/dev/null || { echo "Không chạy: khoá đang có $KHOA"; exit 2; }
P=$OUT/g3p-$LAN; RC=$P.receipt; : > "$RC" || exit 3
printf 'fifo %s\n' "$P.fifo" >> "$RC"
/usr/bin/mkfifo "$P.fifo" || exit 3
tee "$P.log" < "$P.fifo" &
exec > "$P.fifo" 2>&1
exec 4>&1
echo "G3.12 lần $LAN; receipt $RC; log $P.log; S6 đóng."
HET=$((SECONDS + 30)); ACTIVE=0; CA=; W=; W_CO=0; PROG=; PLIST=; N=; MIEN=; ROOT_CO=0; NAP=0
MIENS=; PIDS=; UNKNOWN=0; KET=; KKL=0; UIDK=; TOI=; UQ=; DU=; DO=toi; CO_DON=0; BAD_UID=0; W_ID=; PROG_ID=; PLIST_ID=; PLIST_SHA=
ghi() { printf '%s\n' "$*" >> "$RC" || { echo 'Không ghi được receipt'; exit 3; }; }
han() {
  local s=$((HET - SECONDS)); [ "$s" -gt 0 ] || return 124
  [ "$s" -le 15 ] || s=15
  /usr/bin/perl -e '$SIG{ALRM}="DEFAULT"; alarm shift; exec @ARGV or die "exec"' "$s" "$@"
}
uq() { han "$SUDO" -n -H -u tram-quan-kiem "$@"; }
tk() { han "$SUDO" -n -H -u tram-kiem "$@"; }
root() { han "$SUDO" -n "$@"; }
dung() { echo "DỪNG: $*"; exit 1; }
# D157: chỉ bỏ đúng chương trình Apple, ppid=1 và uid=ruid=tram-kiem, không bỏ theo tên ngắn.
APPLE='/usr/sbin/distnoted|/usr/libexec/trustd|/usr/libexec/secd|/usr/libexec/pkd|/usr/libexec/lsd|'
APPLE+='/usr/libexec/containermanagerd|/System/Library/Frameworks/CoreServices.framework/Frameworks/'
APPLE+='Metadata.framework/Versions/A/Support/mdworker_shared|/System/Library/Frameworks/CoreServices.framework/'
APPLE+='Frameworks/Metadata.framework/Versions/A/Support/mdbulkimport|/System/Library/Frameworks/'
APPLE+='CoreServices.framework/Versions/A/Frameworks/CarbonCore.framework/Versions/A/XPCServices/'
APPLE+='csnameddatad.xpc/Contents/MacOS/csnameddatad|/System/Library/Frameworks/NetFS.framework/Versions/A/'
APPLE+='XPCServices/PlugInLibraryService.xpc/Contents/MacOS/PlugInLibraryService'
APPLE+='|/System/Library/Frameworks/Contacts.framework/Support/contactsd'   # D161: đo 19/10 12:49
bang() {
  han "$PS" -A -o pid=,ppid=,uid=,ruid=,comm= > "$P.ps" 2> "$P.err" || return 1
  [ ! -s "$P.err" ] || return 1
  awk -v u="$UIDK" -v uq="$UQ" -v toi="$TOI" -v me="$$" -v ds="$APPLE" '
    BEGIN {n=split(ds,a,"|"); for(i=1;i<=n;i++) apple[a[i]]=1}
    !/^ *[0-9]+ +[0-9]+ +[0-9]+ +[0-9]+ +[^ ]/ {hong=1}
    $1==me && $3==toi && $4==toi {thay=1}
    (($3==u || $4==u) && !($2==1 && $3==u && $4==u && ($5 in apple))) || $3==uq || $4==uq {print}
    END {exit(hong || !thay)}' "$P.ps" > "$P.tk"
}
inmien() { # Không sudo root khi đọc system. Miền 503 dùng quyền của chính 503.
  case "$1" in gui/"$UQ"*|user/"$UQ"*) uq "$LCTL" print "$1";;
    gui/"$UIDK"*|user/"$UIDK"*) tk "$LCTL" print "$1";;
    *) han "$LCTL" print "$1";; esac
}
mien() {
  local m=$1 r; CANON=$m
  inmien "$m" 2>&1 | awk 'NR==1 {print;next} $1=="handle" && $2=="=" {print}
    $1=="services" && $2=="=" && $3=="{" {s=1}
    s {print} s && $1=="}" {s=0}' > "$P.domain"
  r=${PIPESTATUS[0]}; TRANG=khongro # Không lưu environment hay đối số của job ngoài lần đo.
  if [ "$r" = 0 ] && awk -v m="$m" '
    NR==1 && $2=="=" && $3=="{" {d=($1==m); a=(m~/^login\// && $1~/^gui\/[0-9]+$/)}
    a && $1=="handle" && $2=="=" && $3==substr(m,7) {d=1}
    $1=="services" && $2=="=" && $3=="{" {s=1;next}
    s && $1=="}" {s=0;c=1}
    END {exit !(d && c)}' "$P.domain"; then
    TRANG=docduoc; CANON=$(awk 'NR==1 {print $1;exit}' "$P.domain")
  elif [ "$r" = 125 ] && rgia 'Domain does not support specified action' "$P.domain"; then TRANG=vang
  elif [ "$r" = 113 ] && rgia '^Could not print domain: 113: Could not find specified service$' \
    "$P.domain"; then TRANG=vang
  elif rgia 'Could not find domain' "$P.domain"; then TRANG=vang
  elif rgia 'Permission denied\|Operation not permitted' "$P.domain"; then TRANG=cam; fi
  echo "$CA $m ($CANON): $TRANG (print=$r)"; han /bin/cat "$P.domain" >> "$P.domains"
  [ "$TRANG" != cam ] || echo 'không quyền quan sát miền'
}
rgia() { /usr/bin/grep -q "$1" "$2"; }
co() { # gui/user chia sẻ endpoint; chỉ services mới là định nghĩa job của miền.
  awk -v n="$1" '$1=="services" && $2=="=" && $3=="{" {s=1;next}
    s && $1=="}" {s=0} s && NF==3 && $3==n {co=1} END {exit !co}' "$P.domain"
}
go() {
  ghi "go $1/$2"
  case "$1" in system) root "$LCTL" bootout "$1/$2";;
    gui/"$UQ"|user/"$UQ") uq "$LCTL" bootout "$1/$2";;
    gui/"$UIDK"|user/"$UIDK") tk "$LCTL" bootout "$1/$2";;
    login/*) han "$LCTL" bootout "$1/$2" || tk "$LCTL" bootout "$1/$2";;
    *) han "$LCTL" bootout "$1/$2";; esac > "$P.bootout" 2>&1
}
don() {
  [ "$ACTIVE" = 1 ] || return 0
  local i m ok=0 hong n pid sach=0; HET=$((SECONDS + 60)); CO_DON=1
  han /bin/cat "$RC" > "$P.receipt-doc" || { CO_DON=2; return 1; }
  if [ "$NAP" = 1 ]; then
    rgia "nap $N " "$P.receipt-doc" || { CO_DON=2; return 1; }
    # Ngắt ngay sau bootstrap có thể chưa kịp đo. Thu PID/ASID trước khi gỡ để không bỏ miền login mới.
    if [ -z "$PIDS" ]; then
      do_pid driver "$DO" "$DU" || UNKNOWN=1
      if ! do_pid leaf tk "$UIDK"; then
        DX=$(doc "$W/$DO/driver-exit.txt" 2>/dev/null) || DX='?'
        case "$DX" in ''|*[!0-9]*|0) UNKNOWN=1;; esac
      fi
      if doc "$W/toi/job.txt" >/dev/null 2>&1; then do_pid job toi "$TOI" || UNKNOWN=1
      elif doc "$W/tk/job.txt" >/dev/null 2>&1; then do_pid job tk "$UIDK" || UNKNOWN=1
      elif doc "$W/uq/job.txt" >/dev/null 2>&1; then do_pid job uq "$UQ" || UNKNOWN=1; fi
      [ "$BAD_UID" = 0 ] || UNKNOWN=1
    fi
  fi
  # Dừng con trước cha; giữ chương trình khi bất kỳ miền/PID nào chưa rõ. Lặp hữu hạn nếu job được nạp lại.
  for i in 1 2 3; do
    hong=0
    for m in $MIENS; do
      mien "$m"
      case "$TRANG" in docduoc) [ "$NAP" = 1 ] && co "$N.submit" && go "$m" "$N.submit";;
        vang) :;; *) hong=1;; esac
    done
    [ "$NAP" = 0 ] || go "$MIEN" "$N"
    sleep "$CHO"
    for m in $MIENS; do
      mien "$m"
      case "$TRANG" in docduoc) { co "$N" || co "$N.submit"; } && hong=1;;
        vang) :;; *) hong=1;; esac
    done
    [ "$UNKNOWN" = 0 ] || hong=1
    [ "$hong" = 0 ] && { ok=1; break; }
  done
  # Lá sudo có thể ở phiên/nhóm riêng; chờ probe tự hết hạn (≤45 s), tối đa
  # 40 lần đọc; cần 2 lần liên tiếp sạch. Hết lượt vẫn còn → chưa xác nhận.
  for i in $(seq 1 40); do
    sleep "$CHO"; hong=0
    if bang; then
      n=$(wc -l < "$P.tk" | tr -d ' '); echo "$CA dọn lần $i: $n tiến trình 503/Uq ngoài D157"
      [ "$n" = 0 ] || hong=1
    else echo "$CA không đọc được bảng tiến trình khi dọn"; hong=1; fi
    # Cả cha/job UID 501 cũng phải hết, không chỉ tài khoản kiểm.
    for pid in $PIDS; do
      if awk -v p="$pid" '$1==p {co=1} END {exit !co}' "$P.ps"; then
        born=$(awk -F'|' -v p="$pid" '$1=="birth" && $2==p {print $3;exit}' "$RC")
        live=$(han "$PS" -p "$pid" -o lstart=); r=$?; live=$(printf '%s\n' "$live" | xargs)
        [ "$r" = 0 ] && [ -n "$born" ] && [ -n "$live" ] && [ "$born" != "$live" ] || hong=1
      fi
    done
    if [ "$hong" = 0 ]; then sach=$((sach + 1)); else sach=0; fi
    [ "$sach" -lt 2 ] || break
  done
  [ "$sach" -ge 2 ] || ok=0
  for m in $MIENS; do
    mien "$m"
    case "$TRANG" in docduoc) { co "$N" || co "$N.submit"; } && ok=0;; vang) :;; *) ok=0;; esac
  done
  if [ "$ok" = 1 ] && [ "$W_CO" = 1 ]; then
    [ ! -L "$W" ] && [ -n "$W_ID" ] && [ "$(han /usr/bin/stat -f '%u:%i' "$W")" = "$W_ID" ] || ok=0
  fi
  if [ "$ok" = 1 ] && [ "$ROOT_CO" = 1 ]; then
    [ ! -L "$PROG" ] && [ -n "$PROG_ID" ] \
      && [ "$(han /usr/bin/stat -f '%u:%i' "$PROG")" = "$PROG_ID" ] || ok=0
    if [ -e "$PLIST" ] || [ -L "$PLIST" ]; then
      [ ! -L "$PLIST" ] && [ -n "$PLIST_ID" ] \
        && [ "$(han /usr/bin/stat -f '%u:%i' "$PLIST")" = "$PLIST_ID" ] \
        && [ "$(han /usr/bin/shasum -a 256 "$PLIST")" = "$PLIST_SHA" ] || ok=0
    fi
  fi
  if [ "$ok" = 1 ] && [ "$ROOT_CO" = 1 ]; then
    ghi "xoa $PLIST"; root "$RM" -f "$PLIST" || ok=0
    ghi "xoa $PROG"; root "$RM" -rf "$PROG" || ok=0
    [ ! -e "$PLIST" ] && [ ! -L "$PLIST" ] && [ ! -e "$PROG" ] && [ ! -L "$PROG" ] || ok=0
  fi
  if [ "$ok" = 1 ] && [ "$W_CO" = 1 ]; then
    for owner in tk uq; do
      ghi "don-noidung $W/$owner"
      "$owner" /usr/bin/perl -MFile::Path=remove_tree -e \
        'remove_tree($ARGV[0], {keep_root=>1,error=>\my $e}); exit(@$e ? 1 : 0)' "$W/$owner" || ok=0
      [ "$ok" = 1 ] || break
      ghi "go-thumuc $W/$owner"
      han /bin/rmdir "$W/$owner" || ok=0
      [ ! -e "$W/$owner" ] && [ ! -L "$W/$owner" ] || ok=0
    done
    [ "$ok" = 0 ] || { ghi "xoa $W"; han /bin/rm -rf "$W" || ok=0; }
  fi
  CO_DON=0
  [ "$ok" = 1 ] || { CO_DON=2; echo "$CA | $KE_THUA | $NOI; UID=$JOB_UID | CHƯA XÁC NHẬN"; return 1; }
  echo "$CA | $KE_THUA | $NOI; UID=$JOB_UID | XÁC NHẬN"; ACTIVE=0; return 0
}
ketthuc() {
  local ma=$?; HET=$((SECONDS+90)); trap '' INT TERM HUP ALRM; trap - EXIT
  if [ "$CO_DON" = 2 ] || ! don; then echo "DỌN: CHƯA XÁC NHẬN; giữ khoá, receipt $RC"; exit 3; fi
  han /bin/rm -f "$P.fifo" || exit 3
  rmdir "$KHOA" || exit 3
  echo "DỌN: XONG; receipt $RC"; exit "$ma"
}
trap 'ketthuc >&4 2>&4' EXIT
tin() { trap 'exit 130' INT; trap 'exit 143' TERM; trap 'exit 143' HUP; trap 'exit 142' ALRM; }
tin
UQ=$(han "$ID" -u tram-quan-kiem) || dung 'thiếu tram-quan-kiem — chạy bộ cài riêng g3-tai-khoan.py; không tự tạo'
case "$UQ" in ''|*[!0-9]*|0|501|503) dung 'UID tram-quan-kiem không hợp lệ';; esac
GQ=$(han "$ID" -g tram-quan-kiem); NQ=$(han "$ID" -gn tram-quan-kiem)
[ "$NQ" = tram-quan-kiem ] && [ "$GQ" != 0 ] && [ "$GQ" != 20 ] || dung 'tram-quan-kiem cần nhóm riêng'
# Đo 19/10 (24G90): mọi user cục bộ tự có 12 everyone, 61 localaccounts và qua nhóm lồng 701 sharepoint.group.1
# (lồng everyone), 100 _lpoperator (lồng localaccounts) — nền OS, không gỡ theo từng user. Cấm mọi nhóm khác (staff…).
for g in $(han "$ID" -G tram-quan-kiem); do
  case "$g" in "$GQ"|12|61|701|100) :;; *) dung "tram-quan-kiem có nhóm phụ ngoài dự kiến ($g)";; esac
done
TOI=$(han "$ID" -u); UIDK=$(han "$ID" -u tram-kiem); TEN=$(han "$ID" -un)
case "$TOI:$UIDK" in *[!0-9:]*|:*|*:) dung 'UID không phải số';; esac
[ "$TOI" = 501 ] && [ "$UIDK" = 503 ] || dung 'UID bất thường; phép đo dành cho 501/503'
bang || dung 'không đọc được bảng tiến trình'
[ ! -s "$P.tk" ] || { cat "$P.tk"; dung '503/Uq có tiến trình lạ — không giết'; }
HET=$((SECONDS + 75)); /usr/bin/perl -e 'alarm 60; exec @ARGV or die "exec"' "$SUDO" -v || dung 'sudo -v lỗi/hết 60s'
mien "gui/$TOI"; [ "$TRANG" = docduoc ] || dung 'không đọc được gui'
HANDLE=$(awk '$1=="handle" && $2=="=" && $3~/^[0-9]+$/ {print $3;exit}' "$P.domain")
[ -n "$HANDLE" ] || dung 'không có handle gui/501'
if [ -z "${G3_GIA:-}" ]; then
  han /usr/bin/sw_vers -buildVersion
  han /usr/bin/git -C "$D/../.." rev-parse HEAD
  han /usr/bin/shasum -a 256 "$0" "$D/g3-phien-rieng-probe.sh"
fi
if [ -z "${G3_GIA:-}" ]; then
  # Không root-install/rm qua symlink hay cha ghi được bởi principal không root.
  han /usr/bin/perl -e '
    use strict; use warnings;
    for my $p (@ARGV) {
      while (1) {
        my @s=lstat($p); die "cha khong tin\n" unless @s && -d _ && !-l _ && $s[4]==0 && !($s[2]&0022);
        last if $p eq "/"; $p =~ s{/[^/]+$}{}; $p="/" if $p eq "";
      }
    }' "$ROOT" || dung 'chuỗi cha ROOT không tin cậy'
  for base in "$ROOT" /usr/local /usr /; do
    txt=$(han /bin/ls -lde "$base") || dung 'không kiểm được ACL ROOT'
    [ "$(printf '%s\n' "$txt" | wc -l | tr -d ' ')" = 1 ] || dung 'ROOT có ACL; cần đối soát'
  done
  [ "$(han /usr/bin/stat -f '%u:%p' "$TMP")" = 0:41777 ] || dung 'Shared thiếu sticky/root'
fi
echo 'Biến thể | ASID lá có bằng ASID GUI 501? | Miền submit; UID job | Dọn xác nhận?'
doc() { case "$1" in */uq/*) uq /bin/cat "$1";; */tk/*) tk /bin/cat "$1";; *) han /bin/cat "$1";; esac; }
do_pid() {
  local role=$1 uid=$3 f=$W/$2/$1.txt txt run loai pid ru eu gid egid born truoc sau danh
  txt=$(doc "$f" 2>/dev/null) || return 1
  read -r run loai pid ru eu gid egid <<< "$txt"
  case "$pid:$ru:$eu:$gid:$egid" in *[!0-9:]*|:*|*:) return 1;; esac
  [ "$run" = "$LAN" ] && [ "$loai" = "$role" ] || return 1
  PIDS="$PIDS $pid"; born=$(printf '%s\n' "$txt" | sed -n '2p')
  ghi "pid $role $pid $ru $eu"; ghi "birth|$pid|$born"
  [ "$role" != job ] || JOB_UID=$ru
  if [ "$ru" != "$uid" ] || [ "$eu" != "$uid" ]; then echo 'UID bất thường từ probe'; BAD_UID=1; fi
  if [ "$uid" = "$UQ" ] && { [ "$gid" != "$GQ" ] || [ "$egid" != "$GQ" ]; }; then
    echo "$CA $role: nhóm Uq không đúng nhóm riêng đã kiểm"; BAD_UID=1
  fi
  born=$(printf '%s\n' "$txt" | sed -n '2p')
  truoc=$(han "$PS" -p "$pid" -o lstart= | xargs) || return 1
  danh=$(han "$PS" -p "$pid" -o uid=,ruid=,gid= | xargs) || return 1
  [ "$born" = "$truoc" ] && [ "$danh" = "$eu $ru $egid" ] || return 1
  root "$LCTL" procinfo "$pid" > "$P.$CA.$role.procinfo" 2>&1; local r=$?
  sau=$(han "$PS" -p "$pid" -o lstart= | xargs) || return 1
  [ "$born" = "$sau" ] && [ "$r" = 0 ] || return 1
  ASID=$(awk '/^audit info$/ {a=1;next} a && $1=="session" && $2=="id" {print $4;exit}' \
    "$P.$CA.$role.procinfo")
  case "$ASID" in ''|*[!0-9]*) return 1;; esac
  case " $MIENS " in *" login/$ASID "*) :;; *) MIENS="$MIENS login/$ASID";; esac
  echo "$CA actor_uid=$uid observer_uid=$TOI $role: PID=$pid uid/gid=$ru/$gid euid/egid=$eu/$egid ASID=$ASID; sinh=$born"
}
for CA in v1 v2 v3 v4 v5; do
  HAN_CA=$((SECONDS + 60)); HET=$((SECONDS + 30)); ACTIVE=1
  N=vn.tram.g3p.$LAN.$CA; W=$TMP/g3p-$LAN-$CA; MIEN=system; [ "$CA" != v1 ] || MIEN=gui/$TOI
  PROG=$ROOT/$N.d; PLIST=$ROOT/$N.plist; ROOT_CO=0; NAP=0; UNKNOWN=0; PIDS=; W_CO=0; BAD_UID=0; W_ID=; PROG_ID=; PLIST_ID=; PLIST_SHA=
  DU=$TOI; DT=$TEN; DO=toi
  case "$CA" in v4|v5) DU=$UQ; DT=tram-quan-kiem; DO=uq;; esac
  KE_THUA='KHÔNG KẾT LUẬN'; NOI='KHÔNG KẾT LUẬN'; JOB_UID='?'
  MIENS="gui/$TOI user/$TOI gui/$UIDK user/$UIDK gui/$UQ user/$UQ system"
  ghi "tao $W"; NGAT=
  trap 'NGAT=130' INT; trap 'NGAT=143' TERM HUP; trap 'NGAT=142' ALRM
  han /bin/mkdir -m 733 "$W"; R=$?; [ "$R" != 0 ] || W_CO=1
  tin; [ -z "$NGAT" ] || exit "$NGAT"
  [ "$R" = 0 ] || dung 'không tạo được thư mục mới — không xoá đường đã có'
  W_ID=$(han /usr/bin/stat -f '%u:%i' "$W") || dung 'không định danh W'
  ghi "inode $W $W_ID"
  ghi "tao $W/tk"; tk /bin/mkdir -m 700 "$W/tk" || dung 'sudo -n không tạo được đầu ra kiểm'
  ghi "tao $W/uq"; uq /bin/mkdir -m 700 "$W/uq" || dung 'không tạo đầu ra Uq'
  han /bin/chmod 711 "$W" || dung 'không siết được thư mục'
  han /bin/mkdir -m 700 "$W/toi" || dung 'không tạo được đầu ra chủ'
  if [ "$CA" = v1 ]; then PROG=$W/prog; PLIST=$W/$N.plist
    ghi "tao $PROG"; han /bin/mkdir -m 755 "$PROG" || dung 'không tạo được chương trình'
  else
    [ ! -e "$PLIST" ] && [ ! -L "$PLIST" ] && [ ! -e "$PROG" ] && [ ! -L "$PROG" ] || dung 'đường root đã có'
    ghi "cai $PROG"; ROOT_CO=1
    root "$INSTALL" -d -o root -g wheel -m 0755 "$PROG" || dung 'install thư mục lỗi'
  fi
  PROG_ID=$(han /usr/bin/stat -f '%u:%i' "$PROG") || dung 'không định danh chương trình'
  ghi "inode $PROG $PROG_ID"
  ghi "cai $PROG/probe"
  if [ "$CA" = v1 ]; then han "$INSTALL" -m 0555 "$D/g3-phien-rieng-probe.sh" "$PROG/probe"
  else root "$INSTALL" -o root -g wheel -m 0555 "$D/g3-phien-rieng-probe.sh" "$PROG/probe"; fi || dung 'install probe'
  # plist được soạn trong OUT 0700, không cho lá thay trước khi root install.
  F=$P.$CA.plist; ghi "soan $F"
  printf '%s\n' '<plist version="1.0"><dict>' "<key>Label</key><string>$N</string>" \
    '<key>RunAtLoad</key><true/><key>ProgramArguments</key><array>' > "$F"
  for a in "$PROG/probe" driver "$LAN" "$N" "$W" "$TOI" "$UIDK" "$SUDO" "$LCTL" "$PS" "$DU"; do
    printf '<string>%s</string>\n' "$a" >> "$F"
  done
  echo '</array>' >> "$F"
  [ "$CA" = v1 ] || printf '<key>UserName</key><string>%s</string>\n' "$DT" >> "$F"
  case "$CA" in v4|v5) echo '<key>GroupName</key><string>tram-quan-kiem</string>' >> "$F";; esac
  case "$CA" in v3|v5) echo '<key>SessionCreate</key><true/>' >> "$F";; esac
  echo '</dict></plist>' >> "$F"
  han "$PLUTIL" -lint "$F" || dung 'plist lỗi'
  ghi "cai $PLIST"
  if [ "$CA" = v1 ]; then han "$INSTALL" -m 0644 "$F" "$PLIST"
  else root "$INSTALL" -o root -g wheel -m 0644 "$F" "$PLIST"; fi || dung 'install plist'
  PLIST_ID=$(han /usr/bin/stat -f '%u:%i' "$PLIST") || dung 'không định danh plist'
  PLIST_SHA=$(han /usr/bin/shasum -a 256 "$PLIST") || dung 'không băm plist'
  ghi "inode $PLIST $PLIST_ID"; ghi "digest $PLIST_SHA"
  ghi "submit $N.submit $MIENS"; ghi "nap $N $MIEN $PLIST"; NAP=1
  if [ "$CA" = v1 ]; then han "$LCTL" bootstrap "$MIEN" "$PLIST"
  else root "$LCTL" bootstrap system "$PLIST"; fi || dung 'bootstrap lỗi'
  # Đồng bộ sẵn sàng bằng tệp độc quyền; thiếu driver/leaf ghi phase cụ thể.
  for i in $(seq 1 40); do
    if doc "$W/tk/leaf.txt" >/dev/null 2>&1; then break; fi
    sleep "$CHO"
  done
  if do_pid driver "$DO" "$DU" && do_pid leaf tk "$UIDK"; then
    ghi "cho-phep $W/tk/leaf.go"
    printf '%s\n' "$LAN" | tk /usr/bin/tee "$W/tk/leaf.go" >/dev/null || dung 'không đồng bộ lá'
  else echo "$CA phase=ready: driver/leaf chưa sẵn sàng (sudo -n/PAM)"; fi
  for i in $(seq 1 20); do
    MS=$(doc "$W/tk/submit.txt" 2>/dev/null) || MS='?'
    if [ "$MS" != '?' ]; then break; fi
    sleep "$CHO"
  done
  DAT=1; LA_ASID=
  if [ "$MS" = '?' ]; then
    DX=$(doc "$W/$DO/driver-exit.txt" 2>/dev/null) || DX='?'
    echo "$CA sudo -n/PAM hoặc khởi chạy chưa đạt (driver-exit=$DX); không xem là submit bị rào"
  fi
  do_pid driver "$DO" "$DU" || { echo "$CA phase=driver: không đối chiếu được danh tính/ASID"; DAT=0; UNKNOWN=1; }
  if do_pid leaf tk "$UIDK"; then LA_ASID=$ASID; else echo "$CA phase=leaf: thiếu/lỗi danh tính"; DAT=0
    [ "$MS" = '?' ] || UNKNOWN=1; fi
  echo "$CA submit → $MS"
  ST=$(doc "$W/tk/submit.status" 2>/dev/null) || ST=
  PH=$(doc "$W/tk/submit.phase" 2>/dev/null) || PH=
  echo "$CA phase=$PH status=$ST actor_uid=$UIDK observer_uid=$TOI"
  if doc "$W/toi/job.txt" > "$P.job" 2>/dev/null; then JOB_UID=$TOI; do_pid job toi "$TOI" || { DAT=0; UNKNOWN=1; }
  elif doc "$W/tk/job.txt" > "$P.job" 2>/dev/null; then JOB_UID=$UIDK; do_pid job tk "$UIDK" || { DAT=0; UNKNOWN=1; }
  elif doc "$W/uq/job.txt" > "$P.job" 2>/dev/null; then JOB_UID=$UQ; do_pid job uq "$UQ" || { DAT=0; UNKNOWN=1; }
  else JOB_UID=khong-ap-dung; fi
  [ "$BAD_UID" = 0 ] || dung 'UID bất thường — dừng phép đo'
  NOI=; VUOT=0; THAY=0
  MIENS=$(printf '%s\n' $MIENS | sort -u | xargs)
  for m in $MIENS; do
    mien "$m"
    case "$TRANG" in docduoc) if co "$N.submit"; then
      THAY=1; case ",$NOI," in *",$CANON,"*) :;; *) NOI="${NOI:+$NOI,}$CANON";; esac; inmien "$m/$N.submit" >/dev/null 2>&1 || DAT=0
      case "$m:$CANON" in gui/"$TOI":*|user/"$TOI":*|*:gui/"$TOI"|*:user/"$TOI") VUOT=1;; esac
    else echo "$CA $m: không có service $N.submit"; fi;; vang) :;; *) DAT=0;; esac
  done
  [ "$MS" != 0 ] || [ "$THAY" = 1 ] || UNKNOWN=1
  if [ "$THAY" = 1 ]; then
    [ "$MS" = 0 ] && [ "$PH" = returned ] && [ "$ST" = 'exit=0 signal=0' ] || DAT=0
    [ "$JOB_UID" != khong-ap-dung ] || { DAT=0; echo "$CA: đã nhận/chưa chạy"; }
  else
    ERR=$(doc "$W/tk/submit.err" 2>/dev/null) || ERR=
    ST=$(doc "$W/tk/submit.status" 2>/dev/null) || ST=
    PH=$(doc "$W/tk/submit.phase" 2>/dev/null) || PH=
    echo "$CA phase=$PH status=$ST stderr=${ERR:0:512}"
    if [ "$PH" = returned ] && [ "$MS" != 0 ] && [[ "$ST" = exit=*\ signal=0 ]] \
      && printf '%s' "$ERR" | /usr/bin/grep -Eiq 'submit failed:.*(Operation not permitted|Permission denied)'; then
      NOI='TỪ CHỐI HỢP LỆ'; JOB_UID=khong-ap-dung
    else NOI='KHÔNG KẾT LUẬN'; DAT=0; fi
  fi
  for target in "gui-$TOI" "user-$DU" "user-$UIDK"; do
    doc "$W/tk/target-$target.txt" > "$P.$CA.target-$target.txt" 2>/dev/null || { DAT=0; echo "$CA phase=target-$target: thiếu bằng chứng actor"; }
    [ ! -s "$P.$CA.target-$target.txt" ] || cat "$P.$CA.target-$target.txt"
  done
  for role in driver leaf job; do
    owner=$DO; [ "$role" != leaf ] || owner=tk
    if [ "$role" = job ]; then
      case "$JOB_UID" in "$TOI") owner=toi;; "$UIDK") owner=tk;; "$UQ") owner=uq;; *) continue;; esac
    fi
    doc "$W/$owner/$role.groups" > "$P.$CA.$role.groups" 2>/dev/null || DAT=0
    doc "$W/$owner/$role.context" > "$P.$CA.$role.context" 2>/dev/null || DAT=0
  done
  if [ -n "$LA_ASID" ]; then
    KE_THUA=KHÔNG; [ "$LA_ASID" != "$HANDLE" ] || KE_THUA=CÓ
  fi
  don || exit 3
  case "$CA" in v4|v5)
    [ "$DAT" != 1 ] || [ "$KE_THUA" != KHÔNG ] || [ "$VUOT" != 0 ] || KET="$KET $CA";; esac
  # Biến thể chưa kết luận không chặn biến thể sau (submit bị từ chối ở V3 vẫn cần xem bảng).
  [ "$JOB_UID" != '?' ] || { echo "$CA: KHÔNG KẾT LUẬN — job chưa báo danh tính"; KKL=1; continue; }
  [ "$DAT" = 1 ] || { echo "$CA: KHÔNG KẾT LUẬN — không đối chiếu được probe/ASID"; KKL=1; continue; }
done
echo "Ứng viên thiết kế:${KET:- không có}; Uq/system; cần đo Seatbelt/G4 riêng, S6 vẫn đóng."
echo 'CHƯA ĐO: M3/canary qua bộ quản lý Uq sản phẩm, G4 IPC/XPC, daemon nhiều lượt, logout/reboot.'
[ "$KKL" = 0 ] || exit 1
exit 0
