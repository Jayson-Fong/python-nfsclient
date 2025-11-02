import logging
import struct
from dataclasses import dataclass

from ..auth import AuthenticationFlavor, NoAuthentication
from ..const import MOUNT_PROGRAM, MOUNT_V3, MNT3_OK, MOUNTSTAT3, MNT3ERR_NOTSUPP
from ..pack import nfs_pro_v3Unpacker
from ._generic import Program

logger = logging.getLogger(__package__)


@dataclass(slots=True)
class MountMessage:
    status: int
    message: str


class Mount(Program):
    program = MOUNT_PROGRAM
    program_version = MOUNT_V3

    def __init__(self, *args, auth: AuthenticationFlavor = NoAuthentication, **kwargs):
        super().__init__(*args, **kwargs)
        self.path = None
        self.auth: AuthenticationFlavor = auth

    def null(self, auth=None):
        logger.debug("Mount NULL on %s" % self.host)
        self.request(
            self.program, self.program_version, 0, auth=auth if auth else self.auth
        )

        return MountMessage(MNT3_OK, MOUNTSTAT3[MNT3_OK])

    def mnt(self, path, auth=None):
        data = struct.pack("!L", len(path))
        data += path.encode()
        data += b"\x00" * ((4 - len(path) % 4) % 4)

        logger.debug("Do mount on %s" % path)
        data = self.request(
            self.program,
            self.program_version,
            1,
            data=data,
            auth=auth if auth else self.auth,
        )

        unpacker = nfs_pro_v3Unpacker(data)
        res = unpacker.unpack_mountres3()
        if res["status"] == MNT3_OK:
            self.path = path
        return res

    def umnt(self, auth=None):
        if not self.path:
            logger.warning("No path mounted, cannot process umount.")
            return {"status": MNT3ERR_NOTSUPP, "message": MOUNTSTAT3[MNT3ERR_NOTSUPP]}
        data = struct.pack("!L", len(self.path))
        data += self.path.encode()
        data += b"\x00" * ((4 - len(self.path) % 4) % 4)

        logger.debug("Do umount on %s" % self.path)
        self.request(
            self.program,
            self.program_version,
            3,
            data=data,
            auth=auth if auth else self.auth,
        )

        return MountMessage(MNT3_OK, MOUNTSTAT3[MNT3_OK])

    def export(self):
        logger.debug("Get mount export on %s" % self.host)
        export = self.request(self.program, self.program_version, 5)

        unpacker = nfs_pro_v3Unpacker(export)
        return unpacker.unpack_exports()


__all__ = ["Mount"]
