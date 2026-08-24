from enum import StrEnum


class ProjectRole(StrEnum):
    """Supported project member roles with strict server-side hierarchy."""

    OWNER = "OWNER"
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"
    VIEWER = "VIEWER"


class Permission(StrEnum):
    """Granular platform permissions."""

    # Project Operations
    PROJECT_VIEW = "project:view"
    PROJECT_EDIT = "project:edit"
    PROJECT_DELETE = "project:delete"
    PROJECT_ARCHIVE = "project:archive"

    # Member & Role Operations
    MEMBER_INVITE = "member:invite"
    MEMBER_REMOVE = "member:remove"
    MEMBER_ROLE_CHANGE = "member:role_change"

    # Task Operations
    TASK_CREATE = "task:create"
    TASK_EDIT = "task:edit"
    TASK_DELETE = "task:delete"
    TASK_ASSIGN = "task:assign"

    # Comment Operations
    COMMENT_CREATE = "comment:create"
    COMMENT_DELETE = "comment:delete"


# Explicit Role -> Permission Set mapping (Single source of authorization truth)
ROLE_PERMISSIONS: dict[ProjectRole, set[Permission]] = {
    ProjectRole.OWNER: {
        Permission.PROJECT_VIEW,
        Permission.PROJECT_EDIT,
        Permission.PROJECT_DELETE,
        Permission.PROJECT_ARCHIVE,
        Permission.MEMBER_INVITE,
        Permission.MEMBER_REMOVE,
        Permission.MEMBER_ROLE_CHANGE,
        Permission.TASK_CREATE,
        Permission.TASK_EDIT,
        Permission.TASK_DELETE,
        Permission.TASK_ASSIGN,
        Permission.COMMENT_CREATE,
        Permission.COMMENT_DELETE,
    },
    ProjectRole.ADMIN: {
        Permission.PROJECT_VIEW,
        Permission.PROJECT_EDIT,
        Permission.PROJECT_ARCHIVE,
        Permission.MEMBER_INVITE,
        Permission.MEMBER_REMOVE,
        Permission.TASK_CREATE,
        Permission.TASK_EDIT,
        Permission.TASK_DELETE,
        Permission.TASK_ASSIGN,
        Permission.COMMENT_CREATE,
        Permission.COMMENT_DELETE,
    },
    ProjectRole.MEMBER: {
        Permission.PROJECT_VIEW,
        Permission.TASK_CREATE,
        Permission.TASK_EDIT,
        Permission.TASK_ASSIGN,
        Permission.COMMENT_CREATE,
    },
    ProjectRole.VIEWER: {
        Permission.PROJECT_VIEW,
    },
}

# Numeric hierarchy weights for role comparison
ROLE_HIERARCHY: dict[ProjectRole, int] = {
    ProjectRole.OWNER: 40,
    ProjectRole.ADMIN: 30,
    ProjectRole.MEMBER: 20,
    ProjectRole.VIEWER: 10,
}


def has_permission(role: ProjectRole, permission: Permission) -> bool:
    """Check whether a given project role has the requested permission."""
    return permission in ROLE_PERMISSIONS.get(role, set())


def is_role_higher_or_equal(user_role: ProjectRole, target_role: ProjectRole) -> bool:
    """Check whether user_role is equal to or higher than target_role."""
    return ROLE_HIERARCHY.get(user_role, 0) >= ROLE_HIERARCHY.get(target_role, 0)
