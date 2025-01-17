from django.contrib.auth import get_user_model
from django.contrib.auth.backends import RemoteUserBackend

from shibboleth.app_settings import CREATE_UNKNOWN_USER


class ShibbolethRemoteUserBackend(RemoteUserBackend):
    """
    This backend is to be used in conjunction with the ``RemoteUserMiddleware``
    found in the middleware module of this package, and is used when the server
    is handling authentication outside of Django.

    By default, the ``authenticate`` method creates ``User`` objects for
    usernames that don't already exist in the database.  Subclasses can disable
    this behavior by setting the ``create_unknown_user`` attribute to
    ``False``.
    """

    def authenticate(self, request, remote_user, shib_meta):
        """
        The username passed as ``remote_user`` is considered trusted.  This
        method simply returns the ``User`` object with the given username,
        creating a new ``User`` object if ``create_unknown_user`` is ``True``.

        Returns None if ``create_unknown_user`` is ``False`` and a ``User``
        object with the given username is not found in the database.
        """
        if not remote_user:
            return
        User = get_user_model()
        username = self.clean_username(remote_user)
        field_names = [x.name for x in User._meta.get_fields()]
        shib_user_params = dict([(k, shib_meta[k]) for k in field_names if k in shib_meta])

        # Note that this could be accomplished in one try-except clause, but
        # instead we use get_or_create when creating unknown users since it has
        # built-in safeguards for multiple threads.
        if CREATE_UNKNOWN_USER:
            user, created = User.objects.get_or_create(username=username, defaults=shib_user_params)

            if created:
                """
                @note: setting password for user needs on initial creation of user instead of after auth.login() of middleware.
                because get_session_auth_hash() returns the salted_hmac value of salt and password.
                If it remains after the auth.login() it will return a different auth_hash
                than what's stored in session "request.session[HASH_SESSION_KEY]".
                Also we don't need to update the user's password everytime he logs in.
                """
                user.set_unusable_password()
                user.save()
                user = self.configure_user(user)
        else:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return
        # After receiving a valid user, we update the the user attributes according to the shibboleth
        # parameters. Otherwise the parameters (like mail address, sure_name or last_name) will always
        # be the initial values from the first login. Only save user object if there are any changes.
        if not min([getattr(user, k) == v for k, v in shib_user_params.items()]):
            user.__dict__.update(**shib_user_params)
            user.save()
        return user if self.user_can_authenticate(user) else None

