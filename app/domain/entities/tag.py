from dataclasses import dataclass


@dataclass
class Tag:
    id: int | None
    public_id: str | None
    name: str
