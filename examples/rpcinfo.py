import argparse
import sys
from typing import Tuple, List, Dict, Any

from nfsclient import (
    Portmap,
)


def get_programs(host: str) -> List[Dict[str, Any]]:
    with Portmap(host) as portmap:
        return portmap.dump()


PROGRAM_HEADER: str = "Program"
VERSION_HEADER: str = "Version"
PROTOCOL_HEADER: str = "Protocol"
PORT_HEADER: str = "Port"


def _get_column_length(programs: List[Dict[str, Any]]) -> Tuple[int, int, int, int]:
    program_len: int = len(PROGRAM_HEADER)
    version_len: int = len(VERSION_HEADER)
    protocol_len: int = len(PROTOCOL_HEADER)
    port_len: int = len(PORT_HEADER)

    for program in programs:
        program_len = max(len(str(program["program"])), program_len)
        version_len = max(len(str(program["version"])), version_len)
        protocol_len = max(len(str(program["protocol"])), protocol_len)
        port_len = max(len(str(program["port"])), port_len)

    return program_len, version_len, protocol_len, port_len


def display_programs(programs: List[Dict[str, Any]]):
    program_len, version_len, protocol_len, port_len = _get_column_length(programs)

    print(
        PROGRAM_HEADER.ljust(program_len),
        VERSION_HEADER.ljust(version_len),
        PROTOCOL_HEADER.ljust(protocol_len),
        PORT_HEADER.ljust(port_len),
        sep="\t",
        file=sys.stderr,
    )
    for program in sorted(programs, key=lambda x: x["program"]):
        print(
            str(program["program"]).ljust(program_len),
            str(program["version"]).ljust(version_len),
            str(program["protocol"]).ljust(protocol_len),
            str(program["port"]).ljust(port_len),
            sep="\t",
            file=sys.stderr,
        )


def cli():
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="RPC Portmapper Dump"
    )
    parser.add_argument("--host", type=str, help="Host", required=True)

    args: argparse.Namespace = parser.parse_args()
    programs: List[Dict[str, Any]] = get_programs(args.host)
    display_programs(programs)


if __name__ == "__main__":
    cli()
