from django.db import models


class AllowedGroup(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class AllowedUser(models.Model):
    username = models.CharField(max_length=10)
    groups = models.ManyToManyField(AllowedGroup, blank=True)
    is_staff = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    def __str__(self):
        return self.username