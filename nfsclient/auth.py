import socket
import struct
import time
from abc import abstractmethod
from typing import Final, Optional, List


class AuthenticationFlavor:
    flavor: int

    def pack_header(self, body_length: int) -> bytes:
        return struct.pack("!LL", self.flavor, body_length)

    @abstractmethod
    def pack(self) -> bytes:
        raise NotImplementedError


class NoneAuthenticationFlavor(AuthenticationFlavor):
    flavor: Final[int] = 0

    def pack(self) -> bytes:
        return self.pack_header(0)


NO_AUTHENTICATION: AuthenticationFlavor = NoneAuthenticationFlavor()


class SystemAuthenticationFlavor(AuthenticationFlavor):
    __slots__ = ("machine_name", "uid", "gid", "gids", "stamp")

    flavor: Final[int] = 1

    def __init__(
        self,
        machine_name: Optional[str] = None,
        uid: int = 0,
        gid: int = 0,
        gids: Optional[List[str]] = None,
        stamp: Optional[int] = None,
    ):
        self.machine_name: str = machine_name or socket.gethostname()
        self.uid: int = uid
        self.gid: int = gid
        self.gids: List[str] = gids or []
        self.stamp: Optional[int] = stamp

    def pack_stamp(self) -> bytes:
        stamp: int = int(time.time()) if self.stamp is None else self.stamp
        return struct.pack("!L", stamp & 0xFFFF)

    def pack_machine_name(self) -> bytes:
        packed: bytes = bytearray()

        packed += struct.pack("!L", len(self.machine_name))
        packed += self.machine_name.encode()
        packed += b"\x00" * ((4 - len(self.machine_name) % 4) % 4)

        return packed

    def pack_ids(self) -> bytes:
        return struct.pack(
            "!LL",
            self.uid,
            self.gid,
        )

    def pack_gids(self) -> bytes:
        if len(self.gids) == 1 and self.gids[0] == 0:
            return struct.pack("!L", 0)

        packed: bytes = bytearray(struct.pack("!L", len(self.gids)))
        for aux_gid in self.gids:
            packed += struct.pack("!L", aux_gid)

        return packed

    def pack(self) -> bytes:
        packed: bytes = bytearray()

        packed += self.pack_stamp()
        packed += self.pack_machine_name()
        packed += self.pack_ids()
        packed += self.pack_gids()

        return self.pack_header(len(packed)) + packed


__all__ = (
    "AuthenticationFlavor",
    "NoneAuthenticationFlavor",
    "SystemAuthenticationFlavor",
    "NO_AUTHENTICATION",
)
