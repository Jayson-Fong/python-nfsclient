from typing import Protocol, TypeVar

_T_co = TypeVar("_T_co", covariant=True)


class SupportsLenAndGetItem(Protocol[_T_co]):
    def __len__(self) -> int: ...
    def __getitem__(self, k: int, /) -> _T_co: ...


__all__ = ("SupportsLenAndGetItem",)
