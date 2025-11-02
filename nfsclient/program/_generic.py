import abc
from typing import TypedDict, Optional, Union

from .._types import SupportsLenAndGetItem
from ..rpc import RPC

try:
    from typing import NotRequired

    use_nr: bool = True
except ImportError:
    try:
        from typing_extensions import NotRequired

        use_nr: bool = True
    except ImportError:
        NotRequired = None
        use_nr: bool = False


class Program(RPC, abc.ABC):
    program: int
    program_version: int


if use_nr:

    class RPCInitializationArguments(TypedDict, total=False):
        timeout: NotRequired[Optional[float]]
        client_port: NotRequired[Optional[Union[SupportsLenAndGetItem[int], int]]]
        bind_attempts: NotRequired[int]
        use_privileged_port: NotRequired[bool]
        unprivileged_fallback: NotRequired[bool]

else:

    class RPCInitializationArguments(TypedDict, total=False):
        timeout: Optional[float]
        client_port: Optional[Union[SupportsLenAndGetItem[int], int]]
        bind_attempts: int
        use_privileged_port: bool
        unprivileged_fallback: bool


__all__ = ("Program", "RPCInitializationArguments")
