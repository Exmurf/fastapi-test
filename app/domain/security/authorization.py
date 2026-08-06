from enum import Enum

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

class Permission(str, Enum):
    PRODUCT_READ_OWN = "product:read:own"
    PRODUCT_READ_ALL = "product:read:all"


ROLE_PERMISSIONS: dict[
    UserRole,
    set[Permission],
] = {
    UserRole.USER: {
        Permission.PRODUCT_READ_OWN,
    },
    UserRole.ADMIN: {
        Permission.PRODUCT_READ_ALL,
        Permission.PRODUCT_READ_OWN,
    },
}

def has_permission(
        role: UserRole,
        permission: Permission,
) -> bool:
    return permission in ROLE_PERMISSIONS.get(
        role,
        set(),
    )