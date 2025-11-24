from __future__ import annotations


class ProfileError(Exception):
    """Profile domain/application errors."""
    pass


class ProfileNotFoundError(ProfileError):
    """Profile not found."""
    pass
