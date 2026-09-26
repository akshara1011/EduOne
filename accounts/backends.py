"""
Authentication backends for ErVeda.
Allows students to log in using either their username or email address (case-insensitive).
"""

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

UserModel = get_user_model()


class EmailOrUsernameModelBackend(ModelBackend):
    """
    Authentication backend that allows students to sign in with:
    1. Exact or case-insensitive username
    2. Exact or case-insensitive email address
    Automatically handles leading/trailing whitespace.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)

        if not username or not password:
            return None

        clean_identifier = str(username).strip()

        # Query user by username OR email (case-insensitive)
        candidates = UserModel.objects.filter(
            Q(username__iexact=clean_identifier) | Q(email__iexact=clean_identifier)
        )

        for user in candidates:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user

        return None
