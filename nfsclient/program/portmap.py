import inspect
import struct
from typing import Union, Optional, overload, Type, Unpack

from ..const import PORTMAP_PROGRAM, PORTMAP_VERSION, PORTMAP_PORT
from ._generic import Program, RPCInitializationArguments


class Portmap(Program):
    program = PORTMAP_PROGRAM  # Portmap
    program_version = PORTMAP_VERSION
    port = PORTMAP_PORT

    def __init__(self, host: str, **kwargs: Unpack[RPCInitializationArguments]):
        super().__init__(host=host, port=Portmap.port, **kwargs)

    def null(self):
        self.request(self.program, self.program_version, 0)
        return True

    def dump(self):
        proto = struct.pack("!LL", self.program_version, 4)

        portmap = self.request(self.program, self.program_version, 4, data=proto)

        rpc_map_entries = list()

        if len(portmap) <= 4:  # portmap_Value_Follows + one portmap_Map_entry
            return rpc_map_entries

        portmap_value_follows = portmap[0:4]
        portmap_map_entries = portmap[4:]

        while portmap_value_follows == b"\x00\x00\x00\x01":
            (program, version, protocol, port) = struct.unpack(
                "!LLLL", portmap_map_entries[:16]
            )
            portmap_map_entries = portmap_map_entries[16:]

            if protocol == 0x06:
                protocol = "tcp"
            elif protocol == 0x11:
                protocol = "udp"
            else:
                protocol = "unknown".format(protocol)

            _ = {
                "program": program,
                "version": version,
                "protocol": protocol,
                "port": port,
            }
            if _ not in rpc_map_entries:
                rpc_map_entries.append(_)

            portmap_value_follows = portmap_map_entries[0:4]
            portmap_map_entries = portmap_map_entries[4:]

        return rpc_map_entries

    @overload
    def getport(
        self,
        getport_program: Union[Program, Type[Program]],
        getport_program_version: None = None,
        getport_protocol: int = 6,
    ) -> int: ...

    @overload
    def getport(
        self,
        getport_program: int,
        getport_program_version: int,
        getport_protocol: int = 6,
    ) -> int: ...

    def getport(
        self,
        getport_program: Union[Program, Type[Program], int],
        getport_program_version: Optional[int] = None,
        getport_protocol: int = 6,
    ):
        if isinstance(getport_program, Program) or (
            inspect.isclass(getport_program) and issubclass(getport_program, Program)
        ):
            getport_program_version = getport_program.program_version
            getport_program = getport_program.program
        elif getport_program_version is None:
            raise ValueError("getport_program_version must be specified")

        # RPC
        program = 100000  # Portmap
        program_version = 2
        procedure = 3  # GetPort

        # GetPort
        getport_port = 0

        proto = struct.pack(
            "!LLLL",
            getport_program,
            getport_program_version,
            getport_protocol,
            getport_port,
        )

        getport = self.request(program, program_version, procedure, data=proto)

        (port,) = struct.unpack("!L", getport)
        return port
