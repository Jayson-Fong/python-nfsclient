import logging
import struct
from dataclasses import dataclass
from typing import Optional, Unpack

from ..auth import AuthenticationFlavor, NoAuthentication
from ..const import MOUNT_PROGRAM, MOUNT_V3, MNT3_OK, MOUNTSTAT3, MNT3ERR_NOTSUPP
from ..pack import NFSv3Unpacker
from ._generic import Program, RPCInitializationArguments

logger = logging.getLogger(__package__)


@dataclass(slots=True)
class MountMessage:
    status: int
    message: str


class Mount(Program):
    program = MOUNT_PROGRAM
    program_version = MOUNT_V3

    __slots__ = ("path", "auth")

    def __init__(
        self,
        host: str,
        port: int,
        auth: AuthenticationFlavor = NoAuthentication,
        **kwargs: Unpack[RPCInitializationArguments],
    ):
        super().__init__(host=host, port=port, **kwargs)
        self.path: Optional[str] = None
        self.auth: AuthenticationFlavor = auth

    def null(self, auth: Optional[AuthenticationFlavor] = None):
        logger.debug("Mount NULL on %s" , self.host)
        self.request(self.program, self.program_version, 0, auth=auth or self.auth)

        return MountMessage(MNT3_OK, MOUNTSTAT3[MNT3_OK])

    def mnt(self, path: str, auth: Optional[AuthenticationFlavor] = None):
        data = struct.pack("!L", len(path))
        data += path.encode()
        data += b"\x00" * ((4 - len(path) % 4) % 4)

        logger.debug("Do mount on %s", path)
        data = self.request(
            self.program,
            self.program_version,
            1,
            data=data,
            auth=auth or self.auth,
        )

        unpacker = NFSv3Unpacker(data)
        res = unpacker.unpack_mountres3()
        if res["status"] == MNT3_OK:
            self.path = path

        return res

    def umnt(self, auth: Optional[AuthenticationFlavor] = None):
        if self.path is None:
            logger.warning("No path mounted, cannot process umount.")
            return MountMessage(MNT3ERR_NOTSUPP, MOUNTSTAT3[MNT3ERR_NOTSUPP])

        data = struct.pack("!L", len(self.path))
        data += self.path.encode()
        data += b"\x00" * ((4 - len(self.path) % 4) % 4)

        logger.debug("Do umount on %s", self.path)
        self.request(
            self.program,
            self.program_version,
            3,
            data=data,
            auth=auth or self.auth,
        )

        return MountMessage(MNT3_OK, MOUNTSTAT3[MNT3_OK])

    def export(self):
        logger.debug("Get mount export on %s", self.host)
        export = self.request(self.program, self.program_version, 5)

        unpacker = NFSv3Unpacker(export)
        return unpacker.unpack_exports()


__all__ = ("Mount",)
