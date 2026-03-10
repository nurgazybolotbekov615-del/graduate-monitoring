# from django.db import models


# class Student(models.Model):

#     STATUS_CHOICES = [
#         ('work', 'Трудоустроен'),
#         ('study', 'Учится'),
#         ('army', 'Армия'),
#         ('unemployed', 'Безработный')
#     ]

#     name = models.CharField(max_length=200)
#     group = models.CharField(max_length=50)
#     graduation_year = models.IntegerField()
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES)

#     city = models.CharField(max_length=100, blank=True, null=True)

#     def __str__(self):
#         return self.name
from django.db import models

class Student(models.Model):

    name = models.CharField(max_length=200)
    group = models.CharField(max_length=100)
    status = models.CharField(max_length=50)
    graduation_year = models.IntegerField()
    city = models.CharField(max_length=100)

    def __str__(self):
        return self.name