#!/bin/bash
# Giữ probe cố định và thư viện G3.11 cùng tệp để bản chép có một nguồn kiểm chứng.
# Phụ trợ G3.11: báo danh tính hoặc đọc dữ liệu giả; phần cuối do kịch bản chính nạp.
# Job chỉ chạy nhánh cố định; tệp chứng cứ tạo độc quyền trong đầu ra của đúng UID.
case "${1:-}" in
job)
  shift; exec /usr/bin/perl -e '$SIG{ALRM}="DEFAULT"; alarm 9; exec @ARGV or die "exec: $!"' \
    /bin/bash "$0" job-co-han "$@";;
job-co-han)
  trap 'exit 0' ALRM
  set -u; umask 077; LAN=$2; CA=$3; U=$(/usr/bin/id -u)
  case "$U" in 501) O=$4;; 503) O=$5;; *) exit 0;; esac
  ( set -C
    { printf 'RUN=%s CASE=%s PID=%s UID=%s RUID=%s GID=%s RGID=%s GROUPS=%s\n' "$LAN" "$CA" "$$" "$U" \
        "$(/usr/bin/id -ru)" "$(/usr/bin/id -g)" "$(/usr/bin/id -rg)" "$(/usr/bin/id -G | tr ' ' ',')"
      printf 'START=%s\n' "$(/bin/ps -p $$ -o lstart= | awk '{$1=$1; print}')"
    } > "$O/$CA.txt"
  ) 2>/dev/null
  /bin/sleep 5; exit 0;;
identity)
  printf 'UID=%s RUID=%s GID=%s RGID=%s GROUPS=%s\n' "$(/usr/bin/id -u)" "$(/usr/bin/id -ru)" \
    "$(/usr/bin/id -g)" "$(/usr/bin/id -rg)" "$(/usr/bin/id -G | tr ' ' ',')"; exit 0;;
read)
  C=$2; W=$3; local_ok=khong; content=khong; metadata=khong; listing=khong; link=khong
  [ "$(/bin/cat "$W/local" 2>/dev/null)" = g3r ] && local_ok=co
  /usr/bin/cmp -s "$C/data" "$W/expected" && content=co
  /usr/bin/stat "$C/data" >/dev/null 2>&1 && metadata=co
  /bin/ls "$C" >/dev/null 2>&1 && listing=co
  /usr/bin/cmp -s "$W/link" "$W/expected" && link=co
  external=khong
  [ -z "${4:-}" ] || { /usr/bin/cmp -s "$4/data" "$W/expected" && external=co; }
  echo "local=$local_ok content=$content stat=$metadata list=$listing link=$link external=$external"
  [ "$local_ok" = co ]; exit $?;;
esac

# Danh sách D157 và bộ đọc bảng từ g3-bo-sung.sh; xuống dòng để không vượt 120 ký tự.
APPLE_TU_BAT='/usr/sbin/distnoted|/usr/libexec/trustd|/usr/libexec/secd|/usr/libexec/pkd|/usr/libexec/lsd'
APPLE_TU_BAT+='|/usr/libexec/containermanagerd'
MD='/System/Library/Frameworks/CoreServices.framework/Frameworks/Metadata.framework/Versions/A/Support'
APPLE_TU_BAT+="|$MD/mdworker_shared|$MD/mdbulkimport"
CS='/System/Library/Frameworks/CoreServices.framework/Versions/A/Frameworks/CarbonCore.framework/Versions/A'
APPLE_TU_BAT+="|$CS/XPCServices/csnameddatad.xpc/Contents/MacOS/csnameddatad"
NF='/System/Library/Frameworks/NetFS.framework/Versions/A/XPCServices'
APPLE_TU_BAT+="|$NF/PlugInLibraryService.xpc/Contents/MacOS/PlugInLibraryService"
APPLE_TU_BAT+='|/System/Library/Frameworks/Contacts.framework/Support/contactsd'   # D161: đo 19/10 12:49
bang() {
  han "$PS" -A -o pid=,ppid=,uid=,ruid=,comm= > "$P-ps.bang" 2> "$P-ps.err" || return 1
  [ ! -s "$P-ps.err" ] || return 1
  awk -v u="$UIDK" -v me="$$" -v toi="$TOI" -v ds="$APPLE_TU_BAT" '
    BEGIN {n=split(ds,a,"|"); for(i=1;i<=n;i++) apple[a[i]]=1}
    !/^ *[0-9]+ +[0-9]+ +[0-9]+ +[0-9]+ +[^ ]/ {hong=1}
    $1==me && $3==toi && $4==toi {thay=1}
    ($3==u || $4==u) && !($2==1 && $3==u && $4==u && ($5 in apple)) {print}
    END {exit(hong || !thay)}' "$P-ps.bang" > "$P-ps.txt"
}
han() { # Từng lệnh tối đa 15 s; từng ca kể cả quan sát/dọn tối đa 60 s.
  local s=15 con=$((HET_CA - SECONDS)) tong=$((HET_TONG - SECONDS))
  if [ "$DANG_DON" = 1 ]; then con=$((HET_DON - SECONDS))
  else [ "$tong" -ge "$con" ] || con=$tong; fi
  [ "$con" -gt 0 ] || return 124
  [ "$con" -ge "$s" ] || s=$con
  /usr/bin/perl -e '$SIG{ALRM}="DEFAULT"; alarm shift; exec @ARGV or die "exec: $!"' "$s" "$@"
}
ghi() {
  printf '%s\n' "$*" >> "$RC" || {
    RECEIPT_LOI=1; echo 'KHÔNG KẾT LUẬN: receipt không ghi được'; exit 3;
  }
}
viet() { local ai=$1 p=$2; shift 2; ghi "write|$p|$ai"; han "$@"; }
tin_hieu() {
  trap 'echo "bị ngắt (INT)" >&4; exit 130' INT
  trap 'echo "bị ngắt (TERM)" >&4; exit 143' TERM
  trap 'echo "mất Terminal (HUP)" >&4; exit 143' HUP
  trap 'echo "bị ngắt/hết hạn (ALRM)" >&4; exit 142' ALRM
}
tao_dir() {
  local ai=$1 p=$2 mode=$3 m; NGAT=
  ghi "intent|$p|$ai"
  trap 'NGAT=130' INT; trap 'NGAT=143' TERM; trap 'NGAT=143' HUP; trap 'NGAT=142' ALRM
  if [ "$ai" = tk ]; then han "${TKC[@]}" /bin/mkdir -m "$mode" "$p"; m=$?
  else han /bin/mkdir -m "$mode" "$p"; m=$?; fi
  if [ "$m" = 0 ]; then
    ghi "path|$p|$ai"
    local identity
    if [ "$ai" = tk ]; then identity=$(han "${TKC[@]}" /usr/bin/stat -f '%u:%i' "$p")
    else identity=$(han /usr/bin/stat -f '%u:%i' "$p"); fi
    [ -n "$identity" ] || dung 'không ghi được định danh thư mục'
    ghi "inode|$p|$identity"
  fi
  tin_hieu; [ -z "$NGAT" ] || exit "$NGAT"
  [ "$m" = 0 ] || dung "không tạo được thư mục mới $p"
}
tim() { # Chỉ print service riêng; phân biệt miền vắng, không có service và lỗi quan sát.
  local label=$1 domain canonical m pid live u ruid start x result; MIEN=; DOC_OK=1
  case "$label" in "$NHAN."*) :;; *) DOC_OK=0; return 1;; esac
  case "$label" in *[!a-zA-Z0-9.-]*) DOC_OK=0; return 1;; esac
  for domain in ${MIENS:-"gui/$TOI user/$TOI gui/$UIDK user/$UIDK system"}; do
    han "$LCTL" print "$domain/$label" > "$P-print.tmp" 2>&1; m=$?
    if [ "$m" = 0 ]; then
      canonical=$(awk 'NR==1 {print $1;exit}' "$P-print.tmp"); canonical=${canonical%/"$label"}
      case "$canonical" in gui/[0-9]*|user/[0-9]*|login/[0-9]*|system) :;; *) DOC_OK=0; continue;; esac
      case " $MIEN " in *" $canonical "*) continue;; esac
      domain=$canonical; MIEN="$MIEN $domain"; echo "$label: thấy định nghĩa ở $domain"; ghi "seen|$label|$domain"
      case "$label" in "$NHAN.m3-"*)
        LOT=1; result="$P-${label#"$NHAN."}.result"
        if [ ! -f "$result" ] || /usr/bin/grep -q '^khong/' "$result"; then
          printf 'co/?|UID=?\n' > "$result"
        fi;; esac
      pid=$(awk '$1=="pid" && $2=="=" && $3~/^[0-9]+$/ {print $3; exit}' "$P-print.tmp")
      if [ -n "$pid" ] && [ "$pid" != 0 ]; then
        live=$(han "$PS" -p "$pid" -o pid=,ppid=,uid=,ruid=,lstart= 2> "$P-pid.err"); m=$?
        if [ -s "$P-pid.err" ]; then DOC_OK=0
        elif [ "$m" = 0 ] && [ -n "$live" ]; then
          read -r pid x u ruid start <<< "$live"; start=$(echo "$start" | awk '{$1=$1; print}')
          case "$u/$ruid" in "$TOI/$TOI"|"$UIDK/$UIDK") ghi "pid|$label|$pid $u $start";;
            *) echo 'UID/RUID job bất thường'; KHONG_RO=1; DOC_OK=0;; esac
        elif [ "$m" != 1 ]; then DOC_OK=0; fi
      fi
    elif [ "$m" = 113 ] && /usr/bin/grep -Eq 'Could not find (specified )?service|Could not find domain' "$P-print.tmp"; then :
    elif [ "$m" = 125 ] && /usr/bin/grep -q 'Domain does not support specified action' "$P-print.tmp"; then
      echo "$domain: miền vắng"
    else echo "$label: không đọc được $domain (mã $m)"; DOC_OK=0; fi
  done
  : > "$P-print.tmp"   # không giữ đầu ra thô của launchd
}
pid_da_het() {
  local label=$1 k n data pid u start live m
  while IFS='|' read -r k n data; do
    [ "$k" = pid ] && [ "$n" = "$label" ] || continue
    read -r pid u start <<< "$data"
    live=$(han "$PS" -p "$pid" -o pid=,ppid=,uid=,ruid=,lstart= 2> "$P-pid.err"); m=$?
    [ ! -s "$P-pid.err" ] || return 1
    [ "$m" != 1 ] || continue
    [ "$m" = 0 ] && [ -n "$live" ] || return 1
    # So thế hệ bằng PID + thời điểm sinh; PID đã được dùng lại không phải probe cũ.
    echo "$live" | awk -v p="$pid" -v s="$start" '
      $1==p {for(i=1;i<=4;i++) $i=""; sub(/^ +/,""); alive=($0==s)}
      END {exit !alive}' && return 1
  done < "$RC"
  return 0
}
don_nhan() {
  local label=$1 i domain sach=0 ok=1
  ghi "clean|$label|no"
  for i in 1 2 3 4 5; do
    han /bin/sleep "$DEM"; tim "$label"
    if [ "$DOC_OK" = 1 ] && [ -z "$MIEN" ] && pid_da_het "$label"; then sach=$((sach+1))
    else sach=0; fi
    go_nhan "$label" || ok=0
  done
  [ "$ok" = 1 ] && [ "$sach" -ge 2 ] || return 1
  ghi "clean|$label|yes"; return 0
}
go_nhan() {
  local label=$1 domain ok=1
  for domain in $MIEN; do
    ghi "bootout|$label|$domain"
    case "$domain" in
      "gui/$TOI"|"user/$TOI") han "$LCTL" bootout "$domain/$label" >/dev/null 2>&1;;
      "gui/$UIDK"|"user/$UIDK") han "${TKC[@]}" "$LCTL" bootout "$domain/$label" >/dev/null 2>&1;;
      login/*) han "$LCTL" bootout "$domain/$label" >/dev/null 2>&1 \
        || han "${TKC[@]}" "$LCTL" bootout "$domain/$label" >/dev/null 2>&1 || ok=0;;
      *) echo "không có quyền gỡ $domain/$label"; ok=0;;
    esac
  done
  return $((1-ok))
}
danh_tinh_job() {
  local ca=$1 i file text u pid ruid start live; JOB_UID='?'; JOB_CHAY=khong
  for i in 1 2 3; do
    for u in "$TOI" "$UIDK"; do
      if [ "$u" = "$TOI" ]; then file="$E/out-$TOI/$ca.txt"; text=$(han /bin/cat "$file" 2>/dev/null)
      else file="$W/out-$UIDK/$ca.txt"; text=$(han "${TKC[@]}" /bin/cat "$file" 2>/dev/null); fi
      [ -n "$text" ] || continue
      # Run-ID/ca đúng; PID và thế hệ đối chiếu khi probe còn sống.
      [[ "$text" = "RUN=$LAN CASE=$ca PID="* ]] || return 1
      pid=$(printf '%s\n' "$text" | sed -n 's/.* PID=\([0-9]*\) UID=.*/\1/p')
      ruid=$(printf '%s\n' "$text" | sed -n 's/.* RUID=\([0-9]*\) GID=.*/\1/p')
      [[ "$text" = *" UID=$u RUID=$u "* ]] || return 1
      [ "$ruid" = "$u" ] && [ -n "$pid" ] || return 1
      start=$(printf '%s\n' "$text" | sed -n 's/^START=//p')
      live=$(han "$PS" -p "$pid" -o pid=,ppid=,uid=,ruid=,lstart=) || return 1
      echo "$live" | awk -v p="$pid" -v u="$u" -v s="$start" '
        $1==p && $3==u && $4==u {for(i=1;i<=4;i++) $i=""; sub(/^ +/,""); ok=($0==s)}
        END {exit !ok}' || return 1
      ghi "pid|$NHAN.$ca|$pid $u $start"
      JOB_UID=$u; JOB_CHAY=co; echo "$ca: $text"; return 0
    done
    han /bin/sleep "$DEM"
  done
  return 1
}
bang_cuoi() {
  local k label x ca result don
  echo 'Ca | Job được nhận/chạy? | UID? | Dọn xác nhận?'
  while IFS='|' read -r k label x; do
    [ "$k" = job ] || continue; ca=${label#"$NHAN."}; result='?/??|UID=?'; don=khong
    [ ! -f "$P-$ca.result" ] || result=$(cat "$P-$ca.result")
    [ "$(awk -F'|' -v n="$label" '$1=="clean" && $2==n {s=$3} END {print s}' "$RC")" = yes ] \
      && [ "$DON_OK" = 1 ] && don=co
    echo "$ca | $result | $don"
  done < "$RC"
  echo "ĐỌC NHÀ ĐẠI CA: ngoài hồ sơ $DOC_NGOAI, trong hồ sơ $DOC_TRONG"
}
don() {
  local code=$? bn k p ai i m round sach=0 ok=1 nl=$'\n'; trap - EXIT; trap '' INT TERM HUP ALRM
  DANG_DON=1; HET_DON=$((SECONDS + 60))
  echo "Dọn theo receipt: $RC"; HET_CA=$((SECONDS + 60))
  if ! bn=$(cat "$RC"); then ok=0; bn=; fi
  [ "$RECEIPT_LOI" = 0 ] || ok=0
  # mkdir có thể đã tạo rồi bị ngắt trước mã 0: intent thiếu path không được coi là sạch.
  while IFS='|' read -r k p ai; do
    [ "$k" = intent ] || continue
    case "$nl$bn$nl" in *"${nl}path|$p|$ai${nl}"*) continue;; esac
    if [ "$ai" = tk ]; then han "${TKC[@]}" /bin/test -e "$p" -o -L "$p"; m=$?
    else han /bin/test -e "$p" -o -L "$p"; m=$?; fi
    [ "$m" = 1 ] || { echo "CHƯA XÁC NHẬN intent $p — không xoá mù"; ok=0; }
  done <<< "$bn"
  if [ "$DA_TK" = 1 ]; then
    # Năm vòng CHUNG, không chờ 5 s nhân số nhãn. Chỉ xoá khi hai vòng cuối không job/PID cũ.
    for i in 1 2 3 4 5; do
      round=1; han /bin/sleep "$DEM"
      while IFS='|' read -r k p ai; do
        [ "$k" = job ] || continue
        tim "$p"
        if [ "$DOC_OK" = 1 ] && [ -z "$MIEN" ] && pid_da_het "$p"; then ghi "clean|$p|yes"
        else round=0; ghi "clean|$p|no"; go_nhan "$p" || ok=0; fi
      done <<< "$bn"
      if bang; then echo "lần $i: $(wc -l < "$P-ps.txt" | tr -d ' ') tiến trình ngoài D157"
        [ ! -s "$P-ps.txt" ] || ok=0
      else echo "lần $i: KHÔNG ĐỌC ĐƯỢC ps"; ok=0; fi
      if [ "$round" = 1 ]; then sach=$((sach+1)); else sach=0; fi
    done
    [ "$sach" -ge 2 ] && [ "$KHONG_RO" = 0 ] || ok=0
  fi
  if [ "$ok" = 1 ]; then
    while IFS='|' read -r k p ai; do
      [ "$k" = path ] || continue
      case "$p" in "$C"|"$E"|"$W"|"$W.nha") :;; *) ok=0; continue;; esac
      local expected actual
      expected=$(awk -F'|' -v p="$p" '$1=="inode" && $2==p {print $3;exit}' "$RC")
      if [ "$ai" = tk ]; then actual=$(han "${TKC[@]}" /usr/bin/stat -f '%u:%i' "$p")
      else actual=$(han /usr/bin/stat -f '%u:%i' "$p"); fi
      [ -n "$expected" ] && [ "$expected" = "$actual" ] && [ ! -L "$p" ] || { ok=0; continue; }
      ghi "delete|$p|$ai"
      if [ "$ai" = tk ]; then han "${TKC[@]}" /bin/rm -rf "$p"
        han "${TKC[@]}" /bin/test -e "$p" -o -L "$p"; [ $? = 1 ] || ok=0
      else han /bin/rm -rf "$p"; [ ! -e "$p" ] && [ ! -L "$p" ] || ok=0; fi
    done <<< "$bn"
  fi
  [ "$code" != 3 ] || [ "$ok" != 1 ] || code=1
  [ "$LOT" = 0 ] || code=4
  DON_OK=$ok; bang_cuoi
  if [ "$ok" = 1 ]; then echo 'DỌN: XONG'; rmdir "$KHOA" || { ok=0; code=3; }
  else echo 'DỌN: CHƯA XÁC NHẬN — giữ khoá, probe và receipt'; code=3; fi
  if [ "$code" = 0 ] && [ "$ok" = 1 ]; then echo 'RÀO LAUNCHD ỨNG VIÊN ĐẠT'
  elif [ "$LOT" = 1 ]; then echo 'LỌT'
  else echo 'KHÔNG KẾT LUẬN'; fi
  exit "$code"
}
