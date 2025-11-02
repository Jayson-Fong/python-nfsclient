class NFSClientError(Exception):
    pass


class NFSFileNotFoundError(NFSClientError, FileNotFoundError):
    pass


class NFSPermissionError(NFSClientError, PermissionError):
    pass


class RPCProtocolError(NFSClientError):
    pass


__all__ = ("NFSClientError", "NFSFileNotFoundError", "NFSPermissionError", "RPCProtocolError")
