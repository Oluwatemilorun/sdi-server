from django.db import models

from .Project import Project


class User (models.Model) :
	first_name = models.CharField(max_length=50)
	middle_name = models.CharField(max_length=50)
	last_name = models.CharField(max_length=50)
	registration_number = models.CharField(max_length=11, unique=True)
	level = models.PositiveIntegerField()
	faculty = models.CharField(max_length=100, default='earth and mineral science')
	department = models.CharField(max_length=100, default='remote sensing and gis')

	projects = models.ManyToManyField(Project) # reference the projects created by user

	is_active = models.BooleanField(default=True)

	def __str__(self) :
		return "User infomation for {}".format(self.registration_number)
