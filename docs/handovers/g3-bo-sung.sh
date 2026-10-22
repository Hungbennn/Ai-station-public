#!/bin/bash
# G3 bổ sung cho 3C-D7 (G3.8–G3.10), bản RÚT GỌN (D117). Đại ca chạy trong Terminal.app, gõ `dong-y` khi được hỏi:
#   bash "/Users/dai-ca/Developer/Ben Station/docs/handovers/g3-bo-sung.sh"
# Theo mẫu `.handover/g3/g3-do.sh` (đã chạy đạt 18/10): mỗi lệnh có hạn (perl alarm), lệnh dưới tram-kiem qua mảng
# TKC; cả lần chạy dưới HẠN TỔNG (perl alarm trên chính tiến trình này → SIGALRM → dọn). Tiền điều kiện: tram-kiem
# KHÔNG có tiến trình ngoài danh sách Apple D157 → mọi tiến trình tram-kiem khác về sau là của lần đo, nên
# dọn bằng `kill -KILL -1` DƯỚI tram-kiem (G3.5) chỉ trúng tài khoản dành riêng cho lần đo; có tiến trình → in, DỪNG,
# không giết. Mỗi bước đo phải đạt rõ ràng, không thì DỪNG trước lệnh ghi launchd tiếp theo. tram-kiem ghi được vào miền Đại ca →
# dừng ngay, mã 4 (D66). Không kết luận "launchd từ chối": chỉ ỨNG VIÊN; chữ lỗi do Em + Codex phân loại sau.
# G3.10 (sau đo 18/10 tối): CHỦ miền nạp/in/gỡ plist /usr/bin/true vào gui/$TOI, KHÔNG sudo, thư mục mktemp 0700
# riêng của chủ miền; ghi biên nhận TRƯỚC bootstrap. Không đạt → G3.9 KHÔNG KẾT LUẬN. tram-kiem bootstrap user/$UIDK
# chỉ ghi nhận mã (đã đo 5); nếu mã 0 thì vẫn phải kiểm bộ đọc trên ảnh có job / sau gỡ trước G3.9 thử ghi.
# Mã: 0 ứng viên; 1 dừng/không kết luận; 2 không chạy; 3 dọn chưa xác nhận; 4 ghi được vào miền Đại ca; 130/142/143
# bị ngắt/hết hạn tổng (đã dọn). G3_GIA=<thư mục>: CHỈ cho test (lệnh giả trong thư mục đó).
# Độc quyền (R4-03): khoá `$OUT/g3b.khoa` (mkdir nguyên tử) lấy TRƯỚC ảnh tram-kiem ban đầu, giữ tới hết dọn; đã có →
# mã 2, không sudo/kill gì. Chỉ chạy khi trạm chưa bật giao việc (`giao_viec.bat: false`) — trạm cũng dùng tram-kiem.
# GIỚI HẠN ĐÃ BIẾT (R4-02): bash chỉ chạy trap ALRM/INT/TERM khi lệnh đang chờ kết thúc; lệnh tự bỏ qua SIGALRM thì
# không hạn nào cắt được nó, và phần dọn không có trần riêng. Đại ca ngồi trước Terminal: quá ~20 phút chưa xong thì
# ĐÓNG cửa sổ Terminal và báo Em (HUP → dọn; dọn treo thì khoá còn → lần sau tự dừng, Em kiểm tay).
set -u
D=$(cd "$(dirname "$0")" && pwd); REPO=$(cd "$D/../.." && pwd)
if [ -n "${G3_GIA:-}" ]; then
  B=$G3_GIA; SUDO=$B/sudo; LCTL=$B/launchctl; PS=$B/ps; ID=$B/id; PY=$G3_PY; GOC=$B/goc; OUT=$B/out
  CHO=0; DEM=0; HAN_TONG=${G3_HAN_TONG:-120}; NC_TEN=root; BAN_GIA=${G3_BAN:-}; TAM_TOI=$B
else
  [ -t 0 ] || { echo "Không chạy: cần Terminal tương tác (Đại ca gõ dong-y)"; exit 2; }
  if [ "${1:-}" != --trong-han ]; then
    read -r -p "G3.8–G3.10: kill -1 dưới tram-kiem + launchctl ghi bởi chủ miền và tram-kiem (nhãn thử). Gõ dong-y để chạy: " OK
    [ "$OK" = dong-y ] || { echo "Không chạy."; exit 2; }
    export G3_DONG_Y=dong-y
  fi
  [ "${G3_DONG_Y:-}" = dong-y ] || { echo "Không chạy."; exit 2; }
  SUDO=/usr/bin/sudo; LCTL=/bin/launchctl; PS=/bin/ps; ID=/usr/bin/id; PY="$REPO/.venv/bin/python"
  GOC=/Users/Shared/tram-kiem; OUT=$HOME/.tram/g3; CHO=10; DEM=1; HAN_TONG=900; NC_TEN=tram-kiem; BAN_GIA=
  TAM_TOI=${TMPDIR:-/tmp}
fi
# Hạn tổng: chạy lại chính kịch bản dưới perl alarm (alarm còn hiệu lực qua exec; SIGALRM → trap → dọn có hạn).
[ "${1:-}" = --trong-han ] || exec /usr/bin/perl -e 'alarm shift; exec @ARGV or die "exec: $!"' "$HAN_TONG" \
  /bin/bash "$0" --trong-han
LAN=$(date +%Y%m%d%H%M%S)-$$
mkdir -p "$OUT" && chmod 700 "$OUT" || exit 2
P="$OUT/g3b-$LAN"; RC="$P.receipt"; : > "$RC"
exec > >(tee "$P.log") 2>&1
exec 4>&1      # bash 3.2 chạy trap trong redirect của lệnh đang dở: dọn ghi thẳng fd 4
han() { local s=$1; shift; /usr/bin/perl -e 'alarm shift; exec @ARGV or die "exec: $!"' "$s" "$@"; }
TKC=("$SUDO" -n -H -u tram-kiem)
W="$GOC/g3b-$LAN"; NHAN="vn.tram.g3b.$LAN"; TOI=$(/usr/bin/id -u)
GUI_KHONG="Could not print domain: 125: Domain does not support specified action"
muc() { echo; echo "=== $* ==="; }
ghi() { echo "$*" >> "$RC" || { echo "DỪNG: không ghi được biên nhận"; exit 1; }; }
dem() { awk -v n="$2" 'index($0, n) {c++} END {print c+0}' "$1"; }
inmien() { # inmien <tk|toi> <miền> <tệp>: mã của print, tệp = stdout+stderr
  if [ "$1" = tk ]; then han 30 "${TKC[@]}" "$LCTL" print "$2" > "$3" 2>&1
  else han 30 "$LCTL" print "$2" > "$3" 2>&1; fi
}
# D157: nguồn chung với trạm; executable do nhân trả, không đọc comm/argv.
BANG='import sys
from tram.kiem.ngoai_le_uid import con_uid, duong_nhan, chup_nhan
from tram.kiem.bang_tien_trinh import mot_nhan
try:
    ds = chup_nhan()
    con = con_uid(int(sys.argv[1]), lambda: ds, ten="tram-kiem")
except (OSError, ValueError) as e:
    print(e, file=sys.stderr)
    sys.exit(1)
paths = {}
for t in con:
    if mot_nhan(t.pid) != t:
        sys.exit(1)
    path = duong_nhan(t.pid)
    if mot_nhan(t.pid) != t:
        sys.exit(1)
    paths[t.pid] = "/bin/sleep" if path == "/bin/sleep" else "khac"
with open(sys.argv[2], "w") as f:
    for t in ds:
        print(t.pid, t.ppid, t.uid, t.ruid, paths.get(t.pid, "khac"), file=f)
for t in con:
    print(t.pid, t.ppid, t.uid, t.ruid, paths[t.pid])'
bang() {
  han 10 "$PY" -I -c "$BANG" "$UIDK" "$1.bang" > "$1" 2> "$1.err" || return 1
  [ ! -s "$1.err" ]
}
XET='import sys
from tram.giao_viec.ban_chep import LoiBanChep
from tram.giao_viec.launchd_kiem import MOC_USER, xet_user
moc = MOC_USER.get(sys.argv[2])
if moc is None:
    sys.exit(f"chưa có mốc launchd cho macOS {sys.argv[2]}")
try:
    xet_user("".join(open(p, encoding="utf-8", errors="replace").read() for p in sys.argv[3:]), int(sys.argv[1]), moc)
except LoiBanChep as e:
    print(e)
    sys.exit(1)
print("sạch")'
xet() { han 60 "$PY" -I -c "$XET" "$UIDK" "$BAN" "$@"; }

UIDK=; DA_TK=0; SP=; WT=; PROC_LOI=0; KQ=1; NGAT=; CO_KHOA=0; KHOA="$OUT/g3b.khoa"; NL='
'
mkdir "$KHOA" 2>/dev/null || { echo "Không chạy: đang có lần đo khác hoặc khoá sót từ lần trước ($KHOA — xoá tay nếu chắc"\
  "không còn lần nào chạy)"; exit 2; }
CO_KHOA=1      # khoá của CHÍNH lần này: lấy trước ảnh tram-kiem ban đầu, gỡ ở cuối dọn khi DỌN: XONG
_don() {
  trap '' INT TERM ALRM HUP; local ok=1 loai nhan mien ai i n bn
  muc "Dọn (biên nhận $RC)"
  if [ "$DA_TK" != 1 ]; then echo "chưa chạy gì dưới tram-kiem — không có gì để dọn"; echo "DỌN: XONG"; go_khoa; return; fi
  # Đọc biên nhận MỘT lần; đọc lỗi = không biết đã tạo gì → chưa xác nhận (R4-04). Xét dòng trong bộ nhớ, không grep.
  if bn=$(cat "$RC"); then :; else echo "CHƯA XÁC NHẬN: không đọc được biên nhận $RC"; ok=0; bn=; fi
  while read -r loai nhan mien ai; do
    [ "$loai" = huy ] && han 30 "${TKC[@]}" "$LCTL" remove "$nhan" > /dev/null 2>&1
    [ "$loai" = khongro ] && { echo "CHƯA XÁC NHẬN: không biết job $nhan ở miền nào"; ok=0; }
    [ "$loai" = nap ] || continue
    if [ "$ai" = tk ]; then han 30 "${TKC[@]}" "$LCTL" bootout "$mien/$nhan" > /dev/null 2>&1
    else han 30 "$LCTL" bootout "$mien/$nhan" > /dev/null 2>&1; fi
    if inmien "$ai" "$mien" "$P-don.txt" && [ "$(dem "$P-don.txt" "$nhan")" = 0 ]; then echo "đã gỡ $nhan khỏi $mien"
    else echo "CHƯA XÁC NHẬN gỡ $nhan khỏi $mien"; ok=0; fi
  done <<< "$bn"
  if [ -n "$WT" ]; then
    case "$NL$bn$NL" in *"${NL}co thumuc-toi $WT$NL"*)
      han 20 /bin/rm -rf "$WT"
      if [ ! -e "$WT" ] && [ ! -L "$WT" ]; then echo "thư mục chủ miền $WT: không còn"
      else echo "CHƯA XÁC NHẬN: thư mục chủ miền $WT còn"; ok=0; fi;;
    *) echo "CHƯA XÁC NHẬN: thiếu biên nhận thư mục chủ miền $WT — không xoá"; ok=0;; esac
  fi
  case "$NL$bn$NL" in *"${NL}co thumuc$NL"*) han 30 "${TKC[@]}" /bin/rm -rf "$W";; esac
  case "$NL$bn$NL" in *"${NL}y-dinh thumuc$NL"*)   # chỉ xoá khi biên nhận chứng minh của lần này; luôn kiểm lại
    han 20 "${TKC[@]}" /bin/test -e "$W" -o -L "$W"; i=$?
    if [ "$i" = 1 ]; then echo "thư mục $W: không còn"
    else echo "CHƯA XÁC NHẬN: thư mục $W còn/không kiểm được"; ok=0; fi;;
  esac
  [ "$ok" = 1 ] || [ -n "$bn" ] || { han 20 "${TKC[@]}" /bin/test -e "$W" -o -L "$W"; [ $? = 1 ] || \
    echo "(thư mục $W còn — không xoá vì không đọc được biên nhận)"; }
  han 20 "${TKC[@]}" /bin/kill -KILL -1 2>/dev/null       # tài khoản dành riêng, đã chứng minh trống lúc bắt đầu
  [ -n "$SP" ] && wait "$SP" 2>/dev/null
  for i in 1 2 3 4 5; do sleep "$DEM"
    if bang "$P-don-ps.txt"; then n=$(wc -l < "$P-don-ps.txt" | tr -d ' ')
      echo "lần $i: $n tiến trình uid/ruid tram-kiem"
      [ "$n" = 0 ] || ok=0
    else echo "lần $i: KHÔNG ĐỌC ĐƯỢC bảng tiến trình"; ok=0; fi
  done
  [ "$PROC_LOI" = 1 ] && { echo "CHƯA XÁC NHẬN: procinfo lỗi/quá hạn — không biết hậu duệ root của sudo đã hết"; ok=0; }
  if [ "$ok" = 1 ]; then echo "DỌN: XONG"; go_khoa
  else echo "DỌN: CHƯA XÁC NHẬN — giữ cổng đóng, báo Em, không chạy lại (giữ khoá $KHOA tới khi Em kiểm tay)"
    exit 3; fi
}
go_khoa() { [ "$CO_KHOA" = 1 ] && { rmdir "$KHOA" || echo "không gỡ được khoá $KHOA — xoá tay"; }; CO_KHOA=0; }
trap '_don >&4 2>&4' EXIT
trap 'echo "bị ngắt (INT)" >&4; exit 130' INT
trap 'echo "bị ngắt (TERM)" >&4; exit 143' TERM
trap 'echo "HẠN TỔNG ${HAN_TONG}s hết" >&4; exit 142' ALRM
trap 'echo "mất Terminal (HUP)" >&4; exit 129' HUP
dung() { echo "DỪNG: $*"; exit 1; }

muc "Chuẩn bị"
date; echo "lần $LAN"
[ -x "$PY" ] || dung "không có python của repo ($PY)"
UIDK=$(han 10 "$ID" -u tram-kiem)
case "$UIDK" in ''|*[!0-9]*) dung "UID tram-kiem không phải số";; esac
{ [ "$UIDK" -ne 0 ] && [ "$UIDK" -ne "$TOI" ]; } || dung "UID tram-kiem = 0 hoặc = UID vận hành"
bang "$P-tk-dau.txt" || dung "không đọc được bảng tiến trình"
if [ -s "$P-tk-dau.txt" ]; then cat "$P-tk-dau.txt"
  dung "tram-kiem đang có tiến trình (danh sách trên) — không giết; Đại ca dừng chúng hoặc báo Em rồi chạy lại"; fi
DA_TK=1
han 10 "${TKC[@]}" /usr/bin/true || dung "sudo -n -u tram-kiem không chạy được"
han 60 "$PY" -I -c "import sys; from tram.giao_viec.ngu_canh_kiem import ngu_canh_hien_hanh as n
c = n(sys.argv[1]); print(repr(c)); print(c.ban)" "$NC_TEN" > "$P-ngu-canh.txt" 2>&1 || dung "không đọc được ngữ cảnh"
cat "$P-ngu-canh.txt"; BAN=${BAN_GIA:-$(tail -n 1 "$P-ngu-canh.txt")}
inmien tk "user/$UIDK" "$P-truoc-user.txt" || dung "print user/$UIDK lỗi trước khi ghi"
inmien toi "gui/$TOI" "$P-truoc-gui.txt" || dung "print gui/$TOI lỗi trước khi ghi"
[ "$(dem "$P-truoc-user.txt" "$NHAN")$(dem "$P-truoc-gui.txt" "$NHAN")" = 00 ] || dung "nhãn $NHAN đã tồn tại"
ghi "y-dinh thumuc"
trap 'NGAT=${NGAT:-INT}' INT; trap 'NGAT=${NGAT:-TERM}' TERM   # mkdir + ghi kết quả không bị cắt giữa chừng
han 20 "${TKC[@]}" /bin/mkdir -m 700 "$W"; M=$?; [ "$M" = 0 ] && ghi "co thumuc"
trap 'echo "bị ngắt (INT)" >&4; exit 130' INT; trap 'echo "bị ngắt (TERM)" >&4; exit 143' TERM
[ -n "$NGAT" ] && kill -s "$NGAT" $$
[ "$M" = 0 ] || dung "không tạo được thư mục MỚI $W (đã có, symlink có sẵn, hoặc lỗi) — không đụng"
for k in user login gui; do
  printf '%s\n' '<?xml version="1.0" encoding="UTF-8"?>' \
    "<plist version=\"1.0\"><dict><key>Label</key><string>$NHAN.$k</string>" \
    '<key>ProgramArguments</key><array><string>/usr/bin/true</string></array></dict></plist>' \
    | han 20 "${TKC[@]}" /usr/bin/tee "$W/$k.plist" > /dev/null || dung "không ghi được $W/$k.plist"
done

muc "G3.8 — trạng thái ổn định của user/$UIDK (kill -1 dưới tram-kiem rồi print; KHÔNG chỉ đọc). Mọi bước phải đạt."
han 20 "${TKC[@]}" /bin/kill -KILL -1 2>/dev/null; sleep "$CHO"
bang "$P-ps-truoc.txt" || dung "G3.8: không đọc được bảng tiến trình (trước)"
for n in 2 3; do
  han 30 "${TKC[@]}" "$LCTL" print "user/$UIDK" > "$P-user-$n.out" 2> "$P-user-$n.err" || dung "G3.8: print user-$n lỗi"
  echo "user-$n → 0"; sleep "$CHO"
done
han 30 "${TKC[@]}" "$LCTL" print "gui/$UIDK" > "$P-gui.out" 2> "$P-gui.err"; M=$?; echo "gui → $M"
[ "$M" = 125 ] && [ "$(cat "$P-gui.out" "$P-gui.err")" = "$GUI_KHONG" ] || dung "G3.8: print gui/$UIDK khác dạng đã đo"
: > "$P-ps-sau.txt" || dung "G3.8: không ghi được bảng tổng ps-sau"; N=0
for i in 1 2 3 4 5 6 7 8 9 10; do sleep "$DEM"
  bang "$P-ps-lan.txt" || dung "G3.8: không đọc được bảng tiến trình (lượt $i)"
  n=$(wc -l < "$P-ps-lan.txt" | tr -d ' '); case "$n" in ''|*[!0-9]*) dung "G3.8: không đếm được lượt $i";; esac
  N=$((N + n)); cat "$P-ps-lan.txt" >> "$P-ps-sau.txt" || dung "G3.8: không ghi được bảng tổng ps-sau"
done
echo "ps-sau: $N dòng"     # đếm từ từng lượt đã đọc được, không từ tệp tổng (R4-04)
[ "$N" = 0 ] || dung "G3.8: print sinh tiến trình dưới tram-kiem (rủi ro 4 — cổng đóng giả), ghi nhận rồi dừng"
for n in 2 3; do
  R=$(xet "$P-user-$n.out" "$P-user-$n.err"); M=$?; echo "xet_user user-$n: $R"
  [ "$M" = 0 ] || dung "G3.8: bộ đọc không xác nhận sạch user-$n"
done

muc "G3.9 — ASID (D52: hỏi MẬT KHẨU cho sudo launchctl procinfo, chỉ đọc)"
han 90 "${TKC[@]}" /bin/sleep 60 & SP=$!; sleep 1
bang "$P-ps-sleep.txt" || dung "không đọc được bảng tiến trình"
LA=$(awk -v p="$SP" -v u="$UIDK" '{cha[$1]=$2} $3 == u && $4 == u && $5 ~ /sleep$/ {la[$1]=1}
  END {for (i in la) if (i == p || cha[i] == p || cha[cha[i]] == p) print i}' "$P-ps-sleep.txt.bang")
case "$LA" in ''|*[!0-9]*) dung "không thấy đúng một sleep của tram-kiem dưới sudo $SP";; esac
PROC_LOI=1     # đặt TRƯỚC lệnh: trap có thể thoát trước khi shell nhận/xét mã trả về
han 60 "$SUDO" "$LCTL" procinfo "$LA" > "$P-procinfo.txt" 2>&1; M=$?; echo "procinfo → $M"
[ "$M" = 0 ] || dung "procinfo mã $M — không dùng ASID"
PROC_LOI=0     # chỉ xoá dấu chưa xác nhận sau khi đã xét mã 0; ngắt trước đây giữ mã dọn 3
han 10 "${TKC[@]}" /bin/kill -KILL "$LA"; wait "$SP" 2>/dev/null; SP=
bang "$P-ps-sleep.txt" || dung "không đọc được bảng tiến trình sau khi dừng sleep"
[ -s "$P-ps-sleep.txt" ] && dung "còn tiến trình tram-kiem sau khi dừng sleep"
ASID=$(awk '/^audit info$/ {a=1; next} a && /^\tsession id = [0-9]+$/ {print $4; exit}' "$P-procinfo.txt")
HANDLE=$(awk '/^\thandle = [0-9]+$/ {print $3; exit}' "$P-truoc-gui.txt")
echo "asid(procinfo)=${ASID:-?} handle(gui/$TOI)=${HANDLE:-?}"
{ [ -n "$ASID" ] && [ "$ASID" = "$HANDLE" ]; } || dung "ASID không xác minh được (procinfo ≠ handle gui/$TOI)"

muc "G3.10 — đối chứng dương do CHỦ miền: plist cùng dạng nạp vào gui/$TOI, KHÔNG sudo"
# Hoãn tín hiệu qua mktemp + biên nhận để không mất đường dẫn cần dọn khi bị ngắt.
trap 'NGAT=${NGAT:-INT}' INT; trap 'NGAT=${NGAT:-TERM}' TERM
trap 'NGAT=${NGAT:-ALRM}' ALRM; trap 'NGAT=${NGAT:-HUP}' HUP
WT=$(han 10 /usr/bin/mktemp -d "$TAM_TOI/g3b-toi-$LAN.XXXXXX"); M=$?
[ "$M" = 0 ] && ghi "co thumuc-toi $WT"
trap 'echo "bị ngắt (INT)" >&4; exit 130' INT; trap 'echo "bị ngắt (TERM)" >&4; exit 143' TERM
trap 'echo "HẠN TỔNG ${HAN_TONG}s hết" >&4; exit 142' ALRM; trap 'echo "mất Terminal (HUP)" >&4; exit 129' HUP
[ -n "$NGAT" ] && kill -s "$NGAT" $$
[ "$M" = 0 ] || dung "không tạo được thư mục chủ miền — G3.9 KHÔNG KẾT LUẬN"
printf '%s\n' '<?xml version="1.0" encoding="UTF-8"?>' \
  "<plist version=\"1.0\"><dict><key>Label</key><string>$NHAN.toi</string>" \
  '<key>ProgramArguments</key><array><string>/usr/bin/true</string></array></dict></plist>' \
  > "$WT/toi.plist" || dung "không ghi được plist chủ miền — G3.9 KHÔNG KẾT LUẬN"
ghi "nap $NHAN.toi gui/$TOI toi"
han 30 "$LCTL" bootstrap "gui/$TOI" "$WT/toi.plist" > "$P-nap-toi.txt" 2>&1; MT=$?
inmien toi "gui/$TOI" "$P-toi-co-viec.txt"; IC=$?
han 30 "$LCTL" bootout "gui/$TOI/$NHAN.toi" > "$P-go-toi.txt" 2>&1; GT=$?
inmien toi "gui/$TOI" "$P-toi-sau-don.txt"; IS=$?
echo "chủ miền bootstrap → $MT; print → $IC, $IS; bootout → $GT"
[ "$MT$IC$GT$IS" = 0000 ] \
  && [ "$(dem "$P-toi-co-viec.txt" "$NHAN.toi")$(dem "$P-toi-sau-don.txt" "$NHAN.toi")" = 10 ] \
  || dung "đối chứng dương chủ miền không đạt — G3.9 KHÔNG KẾT LUẬN"
echo "đối chứng dương chủ miền: ĐẠT"

muc "G3.10 — ghi nhận tram-kiem bootstrap user/$UIDK (không phải điều kiện phải nạp được)"
ghi "nap $NHAN.user user/$UIDK tk"
han 30 "${TKC[@]}" "$LCTL" bootstrap "user/$UIDK" "$W/user.plist" > "$P-nap-user.txt" 2>&1; MU=$?
echo "tram-kiem bootstrap user/$UIDK → $MU"
if [ "$MU" = 0 ]; then
  echo "tram-kiem nạp được user/$UIDK — khác lần đo 18/10 (mã 5); kiểm bộ đọc rồi gỡ"
  inmien tk "user/$UIDK" "$P-user-co-viec.txt"; IU=$?
  han 30 "${TKC[@]}" "$LCTL" bootout "user/$UIDK/$NHAN.user" > "$P-go-user.txt" 2>&1; GU=$?
  inmien tk "user/$UIDK" "$P-user-sau-don.txt"; IS=$?
  XC=$(xet "$P-user-co-viec.txt"); MC=$?; XS=$(xet "$P-user-sau-don.txt"); MS=$?
  echo "print → $IU, $IS; bootout → $GU; bộ đọc ảnh có job: $XC; bộ đọc sau gỡ: $XS"
  MONG="user/$UIDK: 1 dịch vụ launchd ngoài mốc — tram-kiem có job (C01 hàng 20)"
  [ "$IU$GU$IS$MC$MS" = 00010 ] && [ "$XC" = "$MONG" ] \
    && [ "$XS" = sạch ] && [ "$(dem "$P-user-co-viec.txt" "$NHAN.user")$(dem "$P-user-sau-don.txt" "$NHAN.user")" = 10 ] \
    || dung "kiểm bộ đọc user/$UIDK không đạt — G3.9 KHÔNG KẾT LUẬN"
else echo "tram-kiem không nạp được job vào miền của chính nó (đo $MU) — ghi nhận và đi tiếp"; fi

muc "G3.9 — tram-kiem thử ghi vào miền của Đại ca (login/$ASID, gui/$TOI); ghi được ở bước nào thì DỪNG ngay"
thu() { # thu <tên> <miền đích>: nạp rồi quan sát gui/$TOI ngay
  ghi "nap $NHAN.$1 gui/$TOI toi"
  han 30 "${TKC[@]}" "$LCTL" bootstrap "$2" "$W/$1.plist" > "$P-g39-$1.txt" 2>&1; M=$?; echo "$1 → $M"
  [ "$M" = 0 ] && { echo "G3.9: GHI ĐƯỢC VÀO MIỀN CỦA ĐẠI CA ($1) — DỪNG S6, báo Em"; KQ=4; exit 4; }
  inmien toi "gui/$TOI" "$P-g39-sau-$1.txt" || dung "G3.9: KHÔNG KẾT LUẬN (print gui/$TOI lỗi)"
  [ "$(dem "$P-g39-sau-$1.txt" "$NHAN")" = 0 ] || { echo "G3.9: GHI ĐƯỢC VÀO MIỀN CỦA ĐẠI CA (thấy nhãn) — DỪNG S6"
    KQ=4; exit 4; }
}
thu login "login/$ASID"; thu gui "gui/$TOI"
ghi "nap $NHAN.submit user/$UIDK tk"; ghi "nap $NHAN.submit gui/$TOI toi"; ghi "huy $NHAN.submit"
han 30 "${TKC[@]}" "$LCTL" submit -l "$NHAN.submit" -- /usr/bin/true > "$P-g39-submit.txt" 2>&1; MS=$?
inmien toi "gui/$TOI" "$P-g39-mien-toi.txt"; IT=$?; inmien tk "user/$UIDK" "$P-g39-mien-tk.txt"; IK=$?
OT=$(dem "$P-g39-mien-toi.txt" "$NHAN"); SK=$(dem "$P-g39-mien-tk.txt" "$NHAN.submit")
LK=$(dem "$P-g39-mien-tk.txt" "$NHAN.")
echo "submit → $MS; print gui/$TOI → $IT (nhãn: $OT); print user/$UIDK → $IK (submit: $SK, mọi nhãn: $LK)"
[ "$IT" = 0 ] && [ "$OT" != 0 ] && { echo "G3.9: GHI ĐƯỢC VÀO MIỀN CỦA ĐẠI CA (submit) — DỪNG S6"; KQ=4; exit 4; }
[ "$MS" = 0 ] && [ "$IK$SK" != 01 ] && ghi "khongro $NHAN.submit"
if [ "$IT$IK$MS" = 000 ] && [ "$SK$LK" = 11 ]; then
  echo "G3.9: ỨNG VIÊN ĐẠT — Em + Codex phân loại chữ lỗi trong $P-g39-login.txt, $P-g39-gui.txt"; KQ=0
else echo "G3.9: KHÔNG KẾT LUẬN (print lỗi, submit không thành công hoặc không thấy đúng một chỗ)"; fi
exit "$KQ"
