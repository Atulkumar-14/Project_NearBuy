import uuid
from sqlalchemy.types import TypeDecorator, BINARY


class GUID(TypeDecorator):
    """
    Platform-independent GUID/UUID type.

    Stores UUID as 16-byte BINARY in SQLite and returns Python uuid.UUID objects.
    """

    impl = BINARY(16)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return value.bytes
        try:
            return uuid.UUID(str(value)).bytes
        except Exception:
            raise ValueError("Invalid UUID value provided")

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        return uuid.UUID(bytes=value)