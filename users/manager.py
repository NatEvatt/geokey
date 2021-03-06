from django.contrib.auth.models import BaseUserManager
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, display_name, password=None, **extra_fields):
        """
        Creates a new user in the data base
        """
        if not email:
            raise ValueError('The given email must be set')
        if not display_name:
            raise ValueError('The given display name must be set')

        now = timezone.now()
        email = UserManager.normalize_email(email)

        user = self.model(email=email, display_name=display_name,
                          is_active=True, last_login=now, date_joined=now,
                          **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, display_name, password, **extra_fields):
        user = self.create_user(email, display_name, password=password,
                                **extra_fields)
        user.is_superuser = True
        user.save()
        return user

    def get_by_natural_key(self, username):
        """
        Returns the user identified by email. Overwrites parent method to
        make user names not case-sensitive.
        """
        return self.get(email__iexact=username)
