from django.db import models

from .Practical import Practical

class Staff (models.Model):
    last_name = models.CharField(max_Length=50)
    first_name = models.CharField(max_Length=50)
    course_title = models.CharField(max_Length=10)
    
    practicals = models.ManyToManyField(Practical)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return "Practical Created by {}".format(self.last_name)