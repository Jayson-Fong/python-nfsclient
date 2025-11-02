import argparse
import sys
import warnings
from typing import Tuple, Optional

from nfsclient import (
    Portmap,
    Mount,
    NFSv3,
    MNT3_OK,
    NFS3_OK,
)
from nfsclient.auth import SystemAuthenticationFlavor


def read_file(
    host: str, mount_path: str, file_path: str, chunk_size: int = 1024
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
        buffer = bytearray()

        last_data = nfs.read(file_handle, offset=0, chunk_count=chunk_size)
        if not last_data["status"] == NFS3_OK:
            return None, last_data["status"]

        buffer += last_data["resok"]["data"]
        while not last_data["resok"]["eof"]:
            last_data = nfs.read(
                file_handle, offset=len(buffer), chunk_count=chunk_size
            )
            if not last_data["status"] == NFS3_OK:
                return bytes(buffer), last_data["status"]

            buffer += last_data["resok"]["data"]

        return bytes(buffer), NFS3_OK


def cli():
    parser = argparse.ArgumentParser(description="NFSv3 File Reader")
    parser.add_argument("--host", type=str, help="NFS Server Host", required=True)
    parser.add_argument(
        "--mount-path", type=str, help="NFS Server Mount Path", required=True
    )
    parser.add_argument("--file-path", type=str, help="File Path", required=True)
    parser.add_argument("--output-path", type=str, help="Output Path", required=True)

    args = parser.parse_args()
    data, status = read_file(args.host, args.mount_path, args.file_path)

    if data is None:
        sys.exit(f"Failed to read file. Status code: {status}")

    if status != NFS3_OK:
        warnings.warn(f"Failed to read file chunk. Status code: {status}")

    with open(args.output_path, "wb") as file:
        file.write(data)


if __name__ == "__main__":
    cli()
