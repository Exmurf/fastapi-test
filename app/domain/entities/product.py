from dataclasses import dataclass

@dataclass
class Product:
    id: int | None
    public_id: str | None
    owner_id: int
    name: str
    price: float
    stock: int