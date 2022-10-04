#!/usr/bin/env python3

import os
import sys
import socket
import ctypes
import json
import platform
from collections import defaultdict
from types import SimpleNamespace

"""
Ripped from header files:
    ifaddrs.h
    netdb.h

example:
    echo '#include <ifaddrs.h>' | cc -E -dD -xc - > ifaddrs.h
"""

uname = platform.uname()
plat = f"{uname.system}+{uname.machine}"

if plat == "Linux+x86_64":
    try:
        glibc_version = os.confstr("CS_GNU_LIBC_VERSION")
    except ValueError:
        sys.exit(f"{plat} currently only works for glibc")
    if not glibc_version.startswith("glibc"):
        sys.exit(f"{plat} currently only works for glibc")

    # NOTE: THE BELOW HEADER INFO WAS SCRAPED FROM:
    #   Ubuntu 20.04
    #   Linux 4.19
    #   glibc 2.31
    #   arch x86_64

    "define NI_MAXHOST 1025"
    NI_MAXHOST = 1025
    "define NI_NUMERICHOST 1"
    NI_NUMERICHOST = 1
    "define NI_NAMEREQD 8"
    NI_NAMEREQD = 8

    "typedef unsigned short int sa_family_t;"
    sa_family_t = ctypes.c_ushort

    "typedef uint16_t in_port_t;"
    in_port_t = ctypes.c_uint16

    """
    typedef unsigned int __socklen_t;
    typedef __socklen_t socklen_t;
    """
    socklen_t = ctypes.c_uint

    class StructSockaddr (ctypes.Structure):
        """
        struct sockaddr {
          sa_family_t sa_family;
          char sa_data[14];
        };
        """
        _fields_ = [
            ("sa_family", sa_family_t),
            ("sa_data", ctypes.c_char * 14),
        ]

    class StructInAddr (ctypes.Structure):
        """
        typedef uint32_t in_addr_t;
        struct in_addr {
          in_addr_t s_addr;
        };
        """
        _fields_ = [
            ("s_addr", ctypes.c_uint32),
        ]

    class StructSockaddrIn (ctypes.Structure):
        """
        struct sockaddr_in {
          sa_family_t sin_family;
          in_port_t sin_port;
          struct in_addr sin_addr;


          unsigned char sin_zero[sizeof (struct sockaddr)
            - (sizeof (unsigned short int))
            - sizeof (in_port_t)
            - sizeof (struct in_addr)];
        };
        """
        _fields_ = [
            ("sin_family", sa_family_t),
            ("sin_port", in_port_t),
            ("sin_addr", StructInAddr),
            ("sin_zero", ctypes.c_ubyte * (ctypes.sizeof(StructSockaddr) - ctypes.sizeof(ctypes.c_ushort) - ctypes.sizeof(in_port_t) - ctypes.sizeof(StructInAddr))),
        ]

    """
    struct in6_addr {
      union {
        uint8_t __u6_addr8[16];
        uint16_t __u6_addr16[8];
        uint32_t __u6_addr32[4];
      } __in6_u;
    };
    """

    class UnionIn6U (ctypes.Union):
        _fields_ = [
            ("__u6_addr8", ctypes.c_uint8 * 16),
            ("__u6_addr16", ctypes.c_uint16 * 8),
            ("__u6_addr32", ctypes.c_uint32 * 4),
        ]

    class StructIn6Addr (ctypes.Structure):
        _fields_ = [
            ("__in6_u", UnionIn6U),
        ]

    class StructSockaddrIn6 (ctypes.Structure):
        """
        struct sockaddr_in6 {
          sa_family_t sin6_family;
          in_port_t sin6_port;
          uint32_t sin6_flowinfo;
          struct in6_addr sin6_addr;
          uint32_t sin6_scope_id;
        };
        """
        _fields_ = [
            ("sin6_family", sa_family_t),
            ("sin6_port", in_port_t),
            ("sin6_flowinfo", ctypes.c_uint32),
            ("sin6_addr", StructIn6Addr),
            ("sin6_scope_id", ctypes.c_uint32),
        ]


    """
    struct ifaddrs {
      struct ifaddrs *ifa_next;

      char *ifa_name;
      unsigned int ifa_flags;

      struct sockaddr *ifa_addr;
      struct sockaddr *ifa_netmask;
      union {
        struct sockaddr *ifu_broadaddr;
        struct sockaddr *ifu_dstaddr;
      } ifa_ifu;
      void *ifa_data;
    };
    """
    class UnionIfaIfu (ctypes.Union):
        _fields_ = [
            ("ifu_broadaddr", ctypes.POINTER(StructSockaddr)),
            ("ifu_dstaddr", ctypes.POINTER(StructSockaddr)),
        ]

    class StructIfAddrs (ctypes.Structure):
        @property
        def ifa_dstaddr (self):
            return self.ifa_ifu.ifu_dstaddr
    StructIfAddrs._fields_ = [
        ("ifa_next", ctypes.POINTER(StructIfAddrs)),
        ("ifa_name", ctypes.c_char_p),
        ("ifa_flags", ctypes.c_uint),
        ("ifa_addr", ctypes.POINTER(StructSockaddr)),
        ("ifa_netmask", ctypes.POINTER(StructSockaddr)),
        ("ifa_ifu", UnionIfaIfu),
        ("ifa_data", ctypes.c_void_p),
    ]

elif plat == "Darwin+x86_64" or plat == "Darwin+arm64":

    # NOTE: THE BELOW HEADER INFO WAS SCRAPED FROM:
    #   MacOS 10.15.7
    #   Darwin 19.6.0
    #   arch x86_64
    # AND
    #   MacOS 11.5.2
    #   Darwin 20.6.0
    #   arch arm64
    # Both appeared to be the same

    "define NI_MAXHOST 1025"
    NI_MAXHOST = 1025
    "define NI_NUMERICHOST 0x00000002"
    NI_NUMERICHOST = 2

    "typedef __uint8_t sa_family_t;"
    sa_family_t = ctypes.c_uint8

    "typedef __uint16_t in_port_t;"
    in_port_t = ctypes.c_uint16

    """
    typedef __uint32_t __darwin_socklen_t;
    typedef __darwin_socklen_t socklen_t;
    """
    socklen_t = ctypes.c_uint32

    class StructSockaddr (ctypes.Structure):
        """
        struct sockaddr {
          __uint8_t sa_len;
          sa_family_t sa_family;
          char sa_data[14];
        };
        """
        _fields_ = [
            ("sa_len", ctypes.c_uint8),
            ("sa_family", sa_family_t),
            ("sa_data", ctypes.c_char * 14),
        ]

    class StructInAddr (ctypes.Structure):
        """
        typedef __uint32_t in_addr_t;
        struct in_addr {
          in_addr_t s_addr;
        };
        """
        _fields_ = [
            ("s_addr", ctypes.c_uint32),
        ]

    class StructSockaddrIn (ctypes.Structure):
        """
        struct sockaddr_in {
          __uint8_t sin_len;
          sa_family_t sin_family;
          in_port_t sin_port;
          struct in_addr sin_addr;
          char sin_zero[8];
        };
        """
        _fields_ = [
            ("sin_len", ctypes.c_uint8),
            ("sin_family", sa_family_t),
            ("sin_port", in_port_t),
            ("sin_addr", StructInAddr),
            ("sin_zero", ctypes.c_ubyte * 8),
        ]

    """
    struct in6_addr {
      union {
        uint8_t __u6_addr8[16];
        uint16_t __u6_addr16[8];
        uint32_t __u6_addr32[4];
      } __u6_addr;
    };
    """

    class UnionIn6U (ctypes.Union):
        _fields_ = [
            ("__u6_addr8", ctypes.c_uint8 * 16),
            ("__u6_addr16", ctypes.c_uint16 * 8),
            ("__u6_addr32", ctypes.c_uint32 * 4),
        ]

    class StructIn6Addr (ctypes.Structure):
        _fields_ = [
            ("__u6_addr", UnionIn6U),
        ]

    class StructSockaddrIn6 (ctypes.Structure):
        """
        struct sockaddr_in6 {
          __uint8_t sin6_len;
          sa_family_t sin6_family;
          in_port_t sin6_port;
          __uint32_t sin6_flowinfo;
          struct in6_addr sin6_addr;
          __uint32_t sin6_scope_id;
        };
        """
        _fields_ = [
            ("sin6_len", ctypes.c_uint8),
            ("sin6_family", sa_family_t),
            ("sin6_port", in_port_t),
            ("sin6_flowinfo", ctypes.c_uint32),
            ("sin6_addr", StructIn6Addr),
            ("sin6_scope_id", ctypes.c_uint32),
        ]


    class StructIfAddrs (ctypes.Structure):
        """
        struct ifaddrs {
         struct ifaddrs *ifa_next;
         char *ifa_name;
         unsigned int ifa_flags;
         struct sockaddr *ifa_addr;
         struct sockaddr *ifa_netmask;
         struct sockaddr *ifa_dstaddr;
         void *ifa_data;
        };
        """
    StructIfAddrs._fields_ = [
        ("ifa_next", ctypes.POINTER(StructIfAddrs)),
        ("ifa_name", ctypes.c_char_p),
        ("ifa_flags", ctypes.c_uint),
        ("ifa_addr", ctypes.POINTER(StructSockaddr)),
        ("ifa_netmask", ctypes.POINTER(StructSockaddr)),
        ("ifa_dstaddr", ctypes.POINTER(StructSockaddr)),
        ("ifa_data", ctypes.c_void_p),
    ]

else:
    sys.exit(f"Unsupported platform: {plat}")


"""
int getifaddrs(struct ifaddrs **ifap);
void freeifaddrs(struct ifaddrs *ifa);
int getnameinfo(const struct sockaddr *addr, socklen_t addrlen, char *host, socklen_t hostlen, char *serv, socklen_t servlen, int flags);
const char *gai_strerror(int errcode);
"""

libc = ctypes.CDLL(None, use_errno=True)
libc.getifaddrs.argtypes = [ctypes.POINTER(ctypes.POINTER(StructIfAddrs))]
libc.freeifaddrs.argtypes = [ctypes.POINTER(StructIfAddrs)]
libc.getnameinfo.argtypes = [ctypes.POINTER(StructSockaddr), socklen_t, ctypes.c_char_p, socklen_t, ctypes.c_char_p, socklen_t, ctypes.c_int]
libc.gai_strerror.argtypes = [ctypes.c_int]
libc.gai_strerror.restype = ctypes.c_char_p

families = {
    socket.AF_INET: SimpleNamespace(
        name="ipv4",
        struct=StructSockaddrIn,
        addrlen=ctypes.sizeof(StructSockaddrIn),
    ),
    socket.AF_INET6: SimpleNamespace(
        name="ipv6",
        struct=StructSockaddrIn6,
        addrlen=ctypes.sizeof(StructSockaddrIn6),
    ),
}

def sockaddr2text (sockaddr, fam=None):
    if not sockaddr:
        return None
    if not fam:
        fam = families.get(sockaddr.contents.sa_family)
    if not fam:
        return None
    addr_text = ctypes.create_string_buffer(NI_MAXHOST)
    error = libc.getnameinfo(sockaddr, fam.addrlen, ctypes.cast(addr_text, ctypes.POINTER(ctypes.c_char)), ctypes.sizeof(addr_text), None, 0, NI_NUMERICHOST)
    if error:
        #print(f"{ifa_name} {famname} getnameinfo error: {libc.gai_strerror(error).decode('latin-1')}", file=sys.stderr)
        #raise socket.gaierror(error)
        raise Exception(f"getnameinfo error: {libc.gai_strerror(error).decode('latin-1')}")
    return addr_text.value.decode("latin-1")


def main (arg0, argv):

    # parse args
    opts = {
        "ipv4": {"4", "ip4"},
        "ipv6": {"6", "ip6"},
        "name": {"n"},
        "json": {"j"},
    }
    opts = {v: k for k, vv in opts.items() for v in [k, *vv]}
    args = SimpleNamespace(ipv4=True, ipv6=False, name=False, json=False)
    for arg in argv:
        orig_arg = arg
        b = True
        if arg.startswith("--"):
            arg = arg[2:]
            if arg.startswith("no-"):
                arg = arg[3:]
                b = False
            opt = opts.get(arg)
            if opt:
                setattr(args, opt, b)
            else:
                return f"Unrecognized arg {orig_arg!a}"
        elif arg.startswith("-"):
            for short_arg in arg[1:]:
                opt = opts.get(short_arg)
                if opt:
                    setattr(args, opt, b)
                else:
                    return f"Unrecognized short arg {short_arg!a} (in {orig_arg!a})"
        else:
            return f"Unrecognized short arg {short_arg!a} (in {orig_arg!a})"

    ifaddrs = ctypes.POINTER(StructIfAddrs)()
    if libc.getifaddrs(ctypes.byref(ifaddrs)):
        return f"getifaddrs error: errno={ctypes.get_errno()}"
    try:
        ifa_addrs = defaultdict(lambda: dict(ipv4=None, ipv6=None))
        ifa = ifaddrs
        while ifa:
            ifa_name = ifa.contents.ifa_name.decode("latin-1")
            fam = families.get(ifa.contents.ifa_addr.contents.sa_family)
            if fam:
                ifa_addrs[ifa_name][fam.name] = {
                    "address": sockaddr2text(ifa.contents.ifa_addr, fam),
                    "broadcast": sockaddr2text(ifa.contents.ifa_dstaddr),
                    "netmask": sockaddr2text(ifa.contents.ifa_netmask),
                }
            ifa = ifa.contents.ifa_next
    finally:
        libc.freeifaddrs(ifaddrs)

    for ifa_name, addrs in ifa_addrs.items():
        if args.json:
            print(json.dumps(dict(interface=ifa_name, **addrs), indent=2))
        else:
            for family_name, addr in addrs.items():
                if not addr:
                    continue
                if getattr(args, family_name):
                    line = addr["address"]
                    if args.name:
                        line = f"{ifa_name}: {line}"
                    print(line)

if __name__ == "__main__":
    try:
        c = main(sys.argv[0], sys.argv[1:])
    except (KeyboardInterrupt, BrokenPipeError):
        sys.stderr.close()
        raise
    if c:
        sys.exit(c)
