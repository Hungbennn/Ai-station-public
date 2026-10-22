#!/usr/bin/perl
# Giám sát hữu hạn độc lập. Chỉ gửi tín hiệu PID con đang sở hữu (chưa wait/reap).
use strict;
use warnings;
use POSIX qw(WNOHANG SIGINT SIGTERM SIGHUP SIGALRM SIG_BLOCK SIG_SETMASK sigprocmask);
use Time::HiRes qw(time sleep);
my ($do, $don) = splice @ARGV, 0, 2;
die "han\n" unless $do =~ /^\d+$/ && $don =~ /^\d+$/ && @ARGV;
$SIG{CHLD}='DEFAULT';
my $pid = fork(); die "fork\n" unless defined $pid;
if (!$pid) {
    $SIG{$_}='DEFAULT' for qw(INT TERM HUP ALRM);
    exec @ARGV; die "exec\n";
}
my $owned=1;
$SIG{$_} = sub { kill $_[0], $pid if $owned; } for qw(INT TERM HUP ALRM);
my $signals=POSIX::SigSet->new(SIGINT,SIGTERM,SIGHUP,SIGALRM);
sub cho {
    my ($flags)=@_; my $old=POSIX::SigSet->new();
    sigprocmask(SIG_BLOCK,$signals,$old) or die "block\n";
    my $r=waitpid($pid,$flags); my $status=$?;
    $owned=0 if $r==$pid || $r<0;
    sigprocmask(SIG_SETMASK,$old) or die "unblock\n";
    return ($r,$status);
}
my $het = time + $do; my $gui = 0;
while (1) {
    my ($r,$status) = cho(WNOHANG);
    if ($r == $pid) {
        if ($status & 127) { warn "Shell đo bị signal; giữ khoá/receipt, đối soát trước lần sau.\n"; }
        exit(($status & 127) ? 128+($status & 127) : $status >> 8);
    }
    die "wait\n" if $r < 0;
    if (!$gui && time >= $het) { kill 'ALRM', $pid; $gui=1; }
    if (time >= $het + $don) {
        warn "Hết ngân sách dọn; giữ khoá/receipt, phục hồi theo đúng lần chạy.\n";
        kill 'KILL', $pid; cho(0); exit 3;
    }
    sleep 0.1;
}
