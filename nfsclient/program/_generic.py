import abc
from typing import TypedDict, Optional, NotRequired, Union

from .._types import SupportsLenAndGetItem
from ..rpc import RPC


class Program(RPC, abc.ABC):

    program: int
    program_version: int


class RPCInitializationArguments(TypedDict, total=False):
    timeout: NotRequired[Optional[float]]
    client_port: NotRequired[Optional[Union[SupportsLenAndGetItem[int], int]]]
    bind_attempts: NotRequired[int]
    use_privileged_port: NotRequired[bool]
    unprivileged_fallback: NotRequired[bool]


__all__ = ("Program", "RPCInitializationArguments")
