from django.db import models
from django.contrib.auth.models import User
# Create your models here.

#A django model is practically a table
#could be articles, users etc.
#Must start with a capital letter
class Password(models.Model):
    #Foreign key is used to make many to one (or one to many relations)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owner")
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    logo = models.CharField(max_length=300)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ["-id"]