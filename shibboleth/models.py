from django.db import models


class AllowedUser(models.Model):
    username = models.CharField(max_length=10)
    groups = models.ManyToManyField(Group, blank=True)
    is_superuser = models.BooleanField(default=False)

    def __str__(self):
        return self.username