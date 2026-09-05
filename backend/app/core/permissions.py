"""
Role -> feature permission matrix, directly encoding Tables 9.1 and 9.2
of the HEFIN Phase 0 spec. Kept as plain data so it's easy to audit and
extend without touching route logic.
"""

from app.models.user import UserRole

# feature -> set of roles allowed to use it
PERMISSIONS: dict[str, set[UserRole]] = {
    "ai_chat": {
        UserRole.PATIENT,
        UserRole.DOCTOR,
        UserRole.HOSPITAL,
        UserRole.RESEARCHER,
        UserRole.NGO,
        UserRole.ADMIN,
    },
    "upload_reports": {UserRole.PATIENT, UserRole.DOCTOR, UserRole.HOSPITAL},
    "patient_timeline": {UserRole.PATIENT, UserRole.DOCTOR, UserRole.HOSPITAL},
    "research_search": {UserRole.RESEARCHER, UserRole.NGO, UserRole.ADMIN},
    "user_management": {UserRole.ADMIN},
}


def has_permission(role: UserRole, feature: str) -> bool:
    return role in PERMISSIONS.get(feature, set())


class PermissionDenied(Exception):
    pass


def require_permission(role: UserRole, feature: str) -> None:
    if not has_permission(role, feature):
        raise PermissionDenied(f"Role '{role}' cannot access '{feature}'")
