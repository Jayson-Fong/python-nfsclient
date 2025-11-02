<!--suppress HtmlDeprecatedAttribute-->
<div align="center">
   <h1>📂 NFSClient</h1>

</div>

<hr />

<div align="center">

[💼 Purpose](#purpose)

</div>

<hr />

# Purpose

A generic, open source client for Linux NFSv3 file systems. The client is operating system and application independent,
implemented in Python and supporting Python versions 3.8 and later.

This package is a fork of [pyNfsClient](https://pypi.org/project/pyNfsClient/), updated to provide a more Pythonic API
and broader support across operating systems and network configurations, such as support for:
- Support for IPv6
- Falling back to non-privileged source ports on permission errors (see [RFC 2623](https://datatracker.ietf.org/doc/html/rfc2623#section-2.1))

# Installation

This package generally requires no dependencies. However, as the `xdrlib` module was removed from the Python standard 
library starting in Python version 3.13, [xdrlib3](https://pypi.org/project/xdrlib3/) is required for these later 
versions (see [PEP 594](https://peps.python.org/pep-0594/)).

You can install the latest development version from GitHub:

```shell
python3 -m pip install git+https://github.com/Jayson-Fong/python-nfsclient.git
```

# Usage

This package's latest development versions and examples are available on 
[GitHub](https://github.com/Jayson-Fong/python-nfsclient).

While this package's API largely resembles [pyNfsClient](https://pypi.org/project/pyNfsClient/), certain deviations
allow for cleaner usage while using more Pythonic naming conventions. For example, to display exported filesystems:

```
from nfsclient import Portmap, Mount

host = "10.1.2.3"
with Portmap(host) as portmap:
    port = portmap.getport(Mount)

with Mount(host, port) as mount:
    print(mount.export())
```
