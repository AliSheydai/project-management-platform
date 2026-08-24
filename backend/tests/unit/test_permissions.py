from app.core.permissions import (
    Permission,
    ProjectRole,
    has_permission,
    is_role_higher_or_equal,
)


def test_project_roles_and_permissions_matrix() -> None:
    """Test that all roles have strictly defined permission sets."""
    # OWNER has full privileges
    assert has_permission(ProjectRole.OWNER, Permission.PROJECT_DELETE) is True
    assert has_permission(ProjectRole.OWNER, Permission.MEMBER_ROLE_CHANGE) is True
    assert has_permission(ProjectRole.OWNER, Permission.PROJECT_EDIT) is True
    assert has_permission(ProjectRole.OWNER, Permission.TASK_CREATE) is True

    # ADMIN has manage privileges but cannot delete project or change roles
    assert has_permission(ProjectRole.ADMIN, Permission.PROJECT_EDIT) is True
    assert has_permission(ProjectRole.ADMIN, Permission.MEMBER_INVITE) is True
    assert has_permission(ProjectRole.ADMIN, Permission.TASK_DELETE) is True
    assert has_permission(ProjectRole.ADMIN, Permission.PROJECT_DELETE) is False
    assert has_permission(ProjectRole.ADMIN, Permission.MEMBER_ROLE_CHANGE) is False

    # MEMBER can create/edit tasks and comment, cannot edit project or invite
    assert has_permission(ProjectRole.MEMBER, Permission.PROJECT_VIEW) is True
    assert has_permission(ProjectRole.MEMBER, Permission.TASK_CREATE) is True
    assert has_permission(ProjectRole.MEMBER, Permission.COMMENT_CREATE) is True
    assert has_permission(ProjectRole.MEMBER, Permission.PROJECT_EDIT) is False
    assert has_permission(ProjectRole.MEMBER, Permission.MEMBER_INVITE) is False
    assert has_permission(ProjectRole.MEMBER, Permission.TASK_DELETE) is False

    # VIEWER has read-only access
    assert has_permission(ProjectRole.VIEWER, Permission.PROJECT_VIEW) is True
    assert has_permission(ProjectRole.VIEWER, Permission.TASK_CREATE) is False
    assert has_permission(ProjectRole.VIEWER, Permission.COMMENT_CREATE) is False
    assert has_permission(ProjectRole.VIEWER, Permission.PROJECT_EDIT) is False


def test_role_hierarchy_ranking() -> None:
    """Test hierarchical ranking of project roles."""
    # OWNER >= all
    assert is_role_higher_or_equal(ProjectRole.OWNER, ProjectRole.OWNER) is True
    assert is_role_higher_or_equal(ProjectRole.OWNER, ProjectRole.ADMIN) is True
    assert is_role_higher_or_equal(ProjectRole.OWNER, ProjectRole.MEMBER) is True
    assert is_role_higher_or_equal(ProjectRole.OWNER, ProjectRole.VIEWER) is True

    # ADMIN >= ADMIN, MEMBER, VIEWER
    assert is_role_higher_or_equal(ProjectRole.ADMIN, ProjectRole.OWNER) is False
    assert is_role_higher_or_equal(ProjectRole.ADMIN, ProjectRole.ADMIN) is True
    assert is_role_higher_or_equal(ProjectRole.ADMIN, ProjectRole.MEMBER) is True
    assert is_role_higher_or_equal(ProjectRole.ADMIN, ProjectRole.VIEWER) is True

    # MEMBER >= MEMBER, VIEWER
    assert is_role_higher_or_equal(ProjectRole.MEMBER, ProjectRole.ADMIN) is False
    assert is_role_higher_or_equal(ProjectRole.MEMBER, ProjectRole.MEMBER) is True
    assert is_role_higher_or_equal(ProjectRole.MEMBER, ProjectRole.VIEWER) is True

    # VIEWER >= VIEWER only
    assert is_role_higher_or_equal(ProjectRole.VIEWER, ProjectRole.MEMBER) is False
    assert is_role_higher_or_equal(ProjectRole.VIEWER, ProjectRole.VIEWER) is True
