from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50)
    date = models.DateField()

    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.category}"
    
    def clean(self):
        if self.amount < 0:
            raise ValidationError("Amount cannot be negative")

    def save(self, *args, **kwargs):
        self.full_clean()  # triggers clean()
        super().save(*args, **kwargs)