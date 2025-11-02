import argparse
import sys
from typing import List, TYPE_CHECKING

from nfsclient import Mount, Portmap


if TYPE_CHECKING:
    from nfsclient.rtypes import ExportNode


def get_exports(host: str) -> List["ExportNode"]:
    with Portmap(host) as portmap:
        port: int = portmap.getport(Mount)

    with Mount(host, port) as mount:
        return mount.export()


PATH_HEADER: str = "Exported Path"


def display_exports(exports: List["ExportNode"]) -> None:
    if not exports:
        sys.exit("No exports found")

    # Decoding here is needed as our backslash replacement might add
    # additional characters. This can cause our user to misinterpret our output.
    longest_name: int = max(
        [len(export.ex_dir.decode(errors="backslashreplace")) for export in exports]
    )
    longest_name = max(longest_name, len(PATH_HEADER))

    print(PATH_HEADER.ljust(longest_name), "Exported Groups", sep="\t", file=sys.stderr)
    for export in exports:
        exported_groups: str = ",".join(
            [
                group.gr_name.decode(errors="backslashreplace")
                for group in export.ex_groups
            ]
        )
        print(
            export.ex_dir.decode(errors="backslashreplace").ljust(longest_name),
            exported_groups,
            sep="\t",
        )


def cli() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="NFSv3 Export Lister"
    )
    parser.add_argument("--host", type=str, help="NFS Server Host", required=True)

    args: argparse.Namespace = parser.parse_args()
    exports: List["ExportNode"] = get_exports(args.host)

    display_exports(exports)


if __name__ == "__main__":
    cli()
