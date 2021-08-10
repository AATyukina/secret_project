from django.db import models
from .managers import SecretManager


class Secret(models.Model):
    uuid = models.CharField(max_length=32)
    secret = models.TextField()
    access_key = models.CharField(
        primary_key=True,
        max_length=128
    )
    secret_created_date = models.DateTimeField(
        auto_now_add=True
    )

    # define custom manager for this model
    objects = SecretManager()

    def __str__(self) -> str:
        return f"[{self.__class__.__name__}] {self.access_key} {self.secret_created_date}"
