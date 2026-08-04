from dataclasses import dataclass

@dataclass
class User:
    id: int | None
    public_id: str | None
    email: str
    password_hash: str
    is_active: bool = True