from django.db import models

class Practical (models.Model):
    name = models.CharField(max_length = 150)
    decription = models.CharField(max_length = 150)
    start_date = models.DateField()
    due_date = models.DateField()
    date_created = models.DateTimeField(auto_now_add=True)
    

    def __str__(self) :
        return "Practical session information for {}".format(self.name)