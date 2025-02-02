from django.db import models
from django.contrib.auth.models import User

class Registration(models.Model):
    idno = models.IntegerField(primary_key=True)
    lastname = models.CharField(max_length=80)
    firstname = models.CharField(max_length=80)
    middlename = models.CharField(max_length=80)
    course = models.CharField(max_length=80)
    level = models.IntegerField()
    email = models.EmailField(max_length=80)
    username = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.idno}, {self.username}, {self.firstname}, {self.lastname}"


    



