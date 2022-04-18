from unicodedata import name
from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.

#Custom User model
class User(AbstractUser):
    email = models.EmailField(verbose_name="email", max_length=255, unique=True)
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def _str_(self):
        return f"{self.username} Profile"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


#Store model
class Store(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=50, null=True)
    city = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=50)
    state = models.CharField(max_length=100)
    latitude = models.CharField(max_length=20)
    longitude = models.CharField(max_length=20)
    # class Meta:
    #     unique_together = ("name", "address")

    def _str_(self):
        return f"{self.username}"

