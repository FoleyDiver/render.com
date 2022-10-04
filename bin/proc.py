import os
import datetime
from types import SimpleNamespace


clk_tck = os.sysconf("SC_CLK_TCK")
uptime = float(open("/proc/uptime", mode="rt").read().split()[0])


def kernel_uptime ():
    with open("/proc/uptime", mode="rt") as fp:
        return float(fp.read().split()[0])


def get_stat (pid):
    with open(f"/proc/{pid}/stat", mode="rt") as fp:
        data = fp.read()
    rest = data.partition(") ")[2].split()
    starttime = float(rest[22-3]) / clk_tck
    ppid = int(rest[4-3])
    return SimpleNamespace(
        ppid=ppid,
        starttime=starttime,
    )


def cmdline (pid):
    with open(f"/proc/{pid}/cmdline", mode="rt") as fp:
        cmdline = fp.read()
    if cmdline.endswith("\x00"):
        cmdline = cmdline[:-1]
    return cmdline.replace("\x00", " ")


def get_statm (pid):
    with open(f"/proc/{pid}/statm") as fp:
        _, rss, shared, *_ = map(float, fp.read().split())
    return SimpleNamespace(
        rss=rss * 4,
        shared=shared * 4,
        private=(rss - shared) * 4,
    )


def iter_procs ():
    for pid_str in os.listdir("/proc"):
        if not pid_str.isdigit():
            continue
        pid = int(pid_str)
        try:
            cmd = cmdline(pid) or ""
            statm = get_statm(pid)
            proc_stat = get_stat(pid)
        except (FileNotFoundError, NotADirectoryError):
            continue
        yield SimpleNamespace(
            pid=pid,
            cmd=cmd,
            statm=statm,
            stat=proc_stat,
        )


def ch3 (seconds):
    days, seconds = divmod(int(seconds), 86400)
    td = datetime.timedelta(seconds=seconds)
    if days:
        return f"{days} day{' ' if days == 1 else 's'} {td!s:>8}"
    else:
        return str(td).lstrip("0:") or "0"


def display (proc):
    return {
        "pid": proc.pid,
        "private": f"{proc.statm.private / 1024:.1f}",
        "shared": f"{proc.statm.shared / 1024:.1f}",
        "rss": f"{proc.statm.rss / 1024:.1f}",
        "runtime": ch3(uptime - proc.stat.starttime),
        "cmd": proc.cmd[:80],
    }
