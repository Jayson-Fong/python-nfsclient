import logging
import random
import socket
import struct
import time
from typing import Optional, Union, Iterable

from . import auth as _auth
from ._types import SupportsLenAndGetItem
from .error import RPCProtocolError

logger = logging.getLogger(__package__)


class RPC:
    connections = list()

    def __init__(
        self,
        host,
        port,
        timeout: Optional[float] = 6000.0,
        client_port: Optional[Union[SupportsLenAndGetItem[int], int]] = range(500, 1024),
        bind_attempts: int = 32,
        use_privileged_port: bool = True,
        unprivileged_fallback: bool = True,
    ):
        self.host = host
        self.port = port
        self.timeout: Optional[float] = timeout
        self.bind_attempts: int = bind_attempts
        self.use_privileged_port: bool = use_privileged_port
        self.unprivileged_fallback: bool = unprivileged_fallback
        self.client = None

        if not isinstance(client_port, Iterable):
            client_port = [client_port]

        self.client_port: SupportsLenAndGetItem[int] = client_port

    def request(
        self,
        program,
        program_version,
        procedure,
        data=None,
        message_type=0,
        version=2,
        auth: _auth.AuthenticationFlavor = _auth.NoAuthentication,
    ) -> bytes:
        rpc_xid = int(time.time())
        rpc_message_type = message_type  # 0=call
        rpc_rpc_version = version
        rpc_program = program
        rpc_program_version = program_version
        rpc_procedure = procedure
        rpc_verifier_flavor = 0  # AUTH_NULL
        rpc_verifier_length = 0

        proto = struct.pack(
            # Remote Procedure Call
            "!LLLLLL",
            rpc_xid,
            rpc_message_type,
            rpc_rpc_version,
            rpc_program,
            rpc_program_version,
            rpc_procedure,
        )

        proto += auth.pack()

        proto += struct.pack(
            "!LL",
            rpc_verifier_flavor,
            rpc_verifier_length,
        )

        if data is not None:
            proto += data

        rpc_fragment_header = 0x80000000 + len(proto)

        proto = struct.pack("!L", rpc_fragment_header) + proto

        try:
            self.client.send(proto)

            last_fragment = False
            data = bytearray()

            while not last_fragment:
                response = self.recv()

                last_fragment = struct.unpack("!L", response[:4])[0] & 0x80000000 != 0

                data += response[4:]

            rpc = data[:24]
            (
                rpc_XID,
                rpc_Message_Type,
                rpc_Reply_State,
                rpc_Verifier_Flavor,
                rpc_Verifier_Length,
                rpc_Accept_State,
            ) = struct.unpack("!LLLLLL", rpc)

            if rpc_Message_Type != 1 or rpc_Reply_State != 0 or rpc_Accept_State != 0:
                raise Exception("RPC protocol error")

            data = data[24:]
        except Exception as e:
            logger.exception(e)

        return data

    def connect(self) -> None:
        # This may raise an exception if the host is unresolvable or the port is
        # invalid, but if that's the case, we can't fix it anyway, so let it error!
        address_info = socket.getaddrinfo(
            self.host, self.port, socket.AF_UNSPEC, socket.SOCK_STREAM
        )

        # noinspection SpellCheckingInspection
        for family, socktype, proto, canonname, sockaddr in address_info:
            self.client = socket.socket(family, socktype, proto)
            self.client.settimeout(self.timeout)

            if self.use_privileged_port:
                for _ in range(self.bind_attempts):
                    random_port: int = random.choice(self.client_port)

                    try:
                        self.client.bind(("", random_port))
                        break
                    except PermissionError:
                        logger.debug(
                            "Encountered permission error binding to port %d. Restricting to ports above 1023.",
                            random_port
                        )

                        if not self.unprivileged_fallback:
                            raise
                    except socket.error as e:
                        if e.errno == 98:
                            logger.debug("Port %d occupied", random_port)

                        logger.exception("Failed binding to port %d", random_port)
                        continue

            self.client.connect(sockaddr)
            RPC.connections.append(self)

    def disconnect(self) -> None:
        self.client.close()
        logger.debug("Port %s released" % self.client_port)

    @classmethod
    def disconnect_all(cls) -> None:
        counter = 0
        for item in cls.connections:
            try:
                item.client.close()
                counter += 1
            except:
                pass
        logger.debug("Disconnect all connecting rpc sockets, amount: %d" % counter)

    def recv(self) -> Optional[bytes]:
        rpc_response_size: bytes = bytearray()

        try:
            while len(rpc_response_size) != 4:
                rpc_response_size = self.client.recv(4)

            if len(rpc_response_size) != 4:
                raise RPCProtocolError(
                    "incorrect recv response size: %d" % len(rpc_response_size)
                )
            response_size: int = struct.unpack("!L", rpc_response_size)[0] & 0x7FFFFFFF

            rpc_response: bytes = rpc_response_size
            while len(rpc_response) < response_size:
                rpc_response = rpc_response + self.client.recv(
                    response_size - len(rpc_response) + 4
                )

            return rpc_response
        except Exception as e:
            logger.exception(e)

        return None

    def __enter__(self) -> "RPC":
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.disconnect()
