from enum import Enum

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

class Permission(str, Enum):
    PRODUCT_READ_OWN = "product:read:own"
    PRODUCT_READ_ALL = "product:read:all"

    PRODUCT_UPDATE_OWN = "product:update:own"
    PRODUCT_UPDATE_ALL = "product:update:all"

    PRODUCT_DELETE_OWN = "product:delete:own"
    PRODUCT_DELETE_ALL = "product:delete:all"

    PROFILE_READ_OWN = "profile:read:own"
    PROFILE_READ_ALL = "profile:read:all"

    PROFILE_UPDATE_OWN = "profile:update:own"
    PROFILE_UPDATE_ALL = "profile:update:all"

    ANALYTICS_READ_OWN = "analytics:read:own"
    ANALYTICS_READ_ALL = "analytics:read:all"

ROLE_PERMISSIONS: dict[
    UserRole,
    set[Permission],
] = {
    UserRole.USER: {
        Permission.PRODUCT_READ_OWN,
        Permission.PRODUCT_UPDATE_OWN,
        Permission.PRODUCT_DELETE_OWN,

        Permission.PROFILE_READ_OWN,
        Permission.PROFILE_UPDATE_OWN,

        Permission.ANALYTICS_READ_OWN,
    },

    UserRole.ADMIN: {
        Permission.PRODUCT_READ_OWN,
        Permission.PRODUCT_READ_ALL,
        Permission.PRODUCT_UPDATE_OWN,
        Permission.PRODUCT_UPDATE_ALL,
        Permission.PRODUCT_DELETE_OWN,
        Permission.PRODUCT_DELETE_ALL,

        Permission.PROFILE_READ_OWN,
        Permission.PROFILE_READ_ALL,
        Permission.PROFILE_UPDATE_OWN,
        Permission.PROFILE_UPDATE_ALL,

        Permission.ANALYTICS_READ_OWN,
        Permission.ANALYTICS_READ_ALL,
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