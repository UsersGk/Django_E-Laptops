from django.db import models


class Customer(models.Model):
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=20)
    password = models.CharField(max_length=25)
    confirm = models.CharField(max_length=25)

    def register(self):
        self.save()

    # def __str__(self):
    #     return self.name
    def isExist(self):
        if Customer.objects.filter(email=self.email):
            return True
        else:
            return False
