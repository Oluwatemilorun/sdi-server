from django.db import models

class Project (models.Model) :
	name = models.CharField(max_length=150)
	description = models.CharField(max_length=220)
	start_date = models.DateField()
	date_created = models.DateTimeField(auto_now_add=True)
	date_modified = models.DateTimeField(auto_now = True)
	semester = models.CharField(max_Length=10) # To easily categorise easy semester

	# owner = models.ForeignKey(User.User, on_delete=models.CASCADE) # reference the owner (user field) of this project


	def __str__(self) :
		return "Project infomation for {}".format(self.name)