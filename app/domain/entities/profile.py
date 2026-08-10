from dataclasses import dataclass

@dataclass
class Profile:
    id: int | None
    user_id: int
    first_name: str | None
    last_name: str | None
    bio: str | None