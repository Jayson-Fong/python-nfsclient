import argparse
from typing import Tuple, Optional

from nfsclient import (
    Portmap,
    Mount,
    NFSv3,
    MNT3_OK,
    NFS3_OK,
)
from nfsclient.auth import SystemAuthenticationFlavor


def read_dir(
    host: str, mount_path: str, file_path: str
) -> Tuple[Optional[bytes], int]:
    with Portmap(host) as portmap:
        mount_port = portmap.getport(Mount)
        nfs_port = portmap.getport(NFSv3)

    auth = SystemAuthenticationFlavor()
    with Mount(host, mount_port, auth=auth) as mount:
        mount_response = mount.mnt(mount_path)
        if mount_response["status"] != MNT3_OK:
            return None, mount_response["status"]

        root_file_handle = mount_response["mountinfo"]["fhandle"]

    with NFSv3(host, nfs_port, auth=auth) as nfs:
        lookup_response = nfs.lookup(root_file_handle, file_path)
        if lookup_response["status"] != NFS3_OK:
            return None, lookup_response["status"]

        file_handle = lookup_response["resok"]["object"]["data"]
        return nfs.readdir(file_handle)


def cli():
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="NFSv3 Read Directorys"
    )
    parser.add_argument("--host", type=str, help="NFS Server Host", required=True)
    parser.add_argument(
        "--mount-path", type=str, help="NFS Server Mount Path", required=True
    )
    parser.add_argument("--file-path", type=str, help="File Path", required=True)

    args: argparse.Namespace = parser.parse_args()
    data = read_dir(args.host, args.mount_path, args.file_path)
    print(data)


if __name__ == "__main__":
    cli()
