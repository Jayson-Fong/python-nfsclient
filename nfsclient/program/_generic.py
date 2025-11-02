import abc

from ..rpc import RPC


class Program(RPC, abc.ABC):

    program: int
    program_version: int


__all__ = ("Program",)
