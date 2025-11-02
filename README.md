<!--suppress HtmlDeprecatedAttribute-->
<div align="center">
   <h1>🎯 NFSClient</h1>

</div>

<hr />

<div align="center">

[💼 Purpose](#purpose)

</div>

<hr />

# Purpose

A Python package providing a NFSv3 client.

# Usage

Display exported filesystems:
```
from nfsclient import Portmap, Mount

host = "10.1.2.3"
with Portmap(host) as portmap:
    port = portmap.getport(Mount)

with Mount(host, port) as mount:
    print(mount.export())
```
