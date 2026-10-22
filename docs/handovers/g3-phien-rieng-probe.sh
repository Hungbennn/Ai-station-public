#!/bin/sh
# Chương trình đo cố định của G3.12, được chép vào chỗ chỉ chủ cài đặt ghi được trước khi launchd chạy.
# Cha giữ lá sudo sống; chính lá báo PID rồi submit. Job báo getuid/geteuid, tạo tệp độc quyền, không theo link.
# Không chạy mã dự án, không Seatbelt. Mọi tiến trình tự hết hạn; không xoá chương trình khi nhãn con còn.
exec /usr/bin/perl -x "$0" "$@"
#!perl
use strict;
use warnings;
use POSIX qw(getuid geteuid getgid getegid);
use Fcntl qw(O_WRONLY O_CREAT O_EXCL O_NOFOLLOW);
my ($role, $run, $label, $w, $toi, $tk, $sudo, $lc, $ps, $driver) = @ARGV;
$driver //= $toi; # Giữ lời gọi probe job cũ để kiểm tệp độc quyền.
die "doi so\n" unless (@ARGV == 9 || @ARGV == 10) && $role =~ /^(driver|leaf|job)$/
    && $run =~ /^[a-zA-Z0-9-]+$/ && $label =~ /^vn\.tram\.g3p\.[a-zA-Z0-9.-]+$/
    && $toi =~ /^\d+$/ && $tk =~ /^\d+$/ && $driver =~ /^\d+$/;
%ENV = (PATH => '/usr/bin:/bin:/usr/sbin:/sbin', LC_ALL => 'C');
# Cha riêng 0700 chặn người khác đọc; 0644 giúp chủ thư mục đọc được chứng cứ nếu job bất ngờ là root.
umask 022;
alarm 45;
sub ghi {
    my ($path, $text) = @_;
    sysopen(my $f, $path, O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW, 0644) or die "tao doc quyen: $!\n";
    print {$f} $text or die "ghi: $!\n";
    close($f) or die "dong: $!\n";
}
my $dir = getuid() == $tk ? "$w/tk" : getuid() == $driver && $driver != $toi ? "$w/uq" : "$w/toi";
# PID do chính Perl đang sống báo, không dùng PID sudo hay monitor. lstart được đối chiếu trước/sau procinfo.
open(my $p, '-|', $ps, '-p', $$, '-o', 'lstart=') or die "ps\n";
my $born = do { local $/; <$p> };
close($p) or die "ps loi\n";
$born =~ s/^\s+|\s+$//g;
$born =~ s/\s+/ /g;
ghi("$dir/$role.txt", join(' ', $run, $role, $$, getuid(), geteuid(), getgid(), getegid()) . "\n$born\n");
ghi("$dir/$role.groups", join(',', $(, $)) . "\n");
# Context từ chính actor, output nhỏ không lưu environment/services của người khác.
my $context='';
for my $what ('manageruid', 'managername') {
    open(my $f, '-|', $lc, $what) or die "context\n";
    my $line=<$f> // ''; close($f) or die "context failed\n";
    $line=substr($line,0,120); $line =~ s/[^\x20-\x7e]/?/g;
    $context .= "$what=$line\n";
}
ghi("$dir/$role.context", $context);
if ($role eq 'driver') {
    die "uid cha\n" unless getuid() == $driver && geteuid() == $driver;
    my $pid = fork(); die "fork\n" unless defined $pid;
    if (!$pid) { exec $sudo, '-n', '-H', '-u', 'tram-kiem', $0, 'leaf', @ARGV[1..$#ARGV]; die "sudo\n"; }
    waitpid($pid, 0);
    ghi("$dir/driver-exit.txt", (($? >> 8) || ($? & 127)) . "\n");
    sleep 20; # Giữ cha tới bootout để đo cùng thời điểm với lá, kể cả sudo lỗi.
} elsif ($role eq 'leaf') {
    die "uid la\n" unless getuid() == $tk && geteuid() == $tk;
    # Người đo đối chiếu chính lá sống trước khi cho phép thao tác launchd.
    until (-f "$dir/leaf.go" && !-l "$dir/leaf.go") { select undef, undef, undef, 0.1; }
    for my $target ("gui/$toi", "user/$driver", "user/$tk") {
        my $pid=open(my $f, '-|'); die "fork print\n" unless defined $pid;
        if (!$pid) { open STDERR, '>', '/dev/null'; alarm 3; exec $lc, 'print', $target; die "exec print\n"; }
        my $first=<$f> // ''; while (<$f>) {} close $f; my $status=$?;
        $first=substr($first,0,120); $first =~ s/[^\x20-\x7e]/?/g;
        my $key=$target; $key =~ s{/}{-}g;
        ghi("$dir/target-$key.txt", "actor_uid=".getuid()." target=$target exit=".($status>>8).
            " signal=".($status&127)." first=$first\n");
    }
    ghi("$dir/submit.intent", "$run submit $label.submit\n");
    pipe(my $rd, my $wr) or die "pipe\n";
    my $pid = fork(); die "fork\n" unless defined $pid;
    if (!$pid) {
        close $rd; open STDERR, '>&', $wr or die "stderr\n"; close $wr;
        open STDOUT, '>', '/dev/null' or die "stdout\n";
        alarm 15;
        exec $lc, 'submit', '-l', "$label.submit", '--', $0, 'job', @ARGV[1..$#ARGV]; die "exec\n";
    }
    close $wr; ghi("$dir/submit.pid", "$pid\n");
    my $err = ''; while (read($rd, my $buf, 1024)) { $err .= $buf if length($err) < 512; }
    close $rd; waitpid($pid, 0); my $rc = $?;
    $err = substr($err, 0, 512); $err =~ s/[^\x20-\x7e\n]/?/g;
    ghi("$dir/submit.err", $err);
    ghi("$dir/submit.status", 'exit=' . ($rc >> 8) . ' signal=' . ($rc & 127) . "\n");
    ghi("$dir/submit.phase", "returned\n");
    ghi("$dir/submit.txt", (($rc >> 8) || ($rc & 127)) . "\n");
    sleep 20;
} else {
    sleep 20; # Thành công cũng giữ sống, tránh launchd tự bật lại trước khi người đo đối chiếu/gỡ.
}
exit 0;
