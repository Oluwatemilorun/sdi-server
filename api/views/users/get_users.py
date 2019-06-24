from django.http import HttpResponse

from api.models import User

def get_users(request) :
	return HttpResponse('All users')
	