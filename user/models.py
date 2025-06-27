from django.db import models

class Signup(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)

    def __str__(self):
        return f"{self.name, self.email, self.password}"

    class Meta:
        app_label = 'user'  # Ensures it's grouped under 'user'
        verbose_name = 'Account'  # Display name for a single record
        verbose_name_plural = 'Accounts'  # Display name for the list


