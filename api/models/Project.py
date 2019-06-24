from django.db import models

class Project (models.Model) :
	name = models.CharField(max_length=150)
	description = models.CharField(max_length=220)
	start_date = models.DateField()

	# owner = models.ForeignKey(User.User, on_delete=models.CASCADE) # reference the owner (user field) of this project


	def __str__(self) :
		return "Project infomation for {}".format(self.name)