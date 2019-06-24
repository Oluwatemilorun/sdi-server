from django.http import HttpResponse

def get_single_users(request) :
	return HttpResponse('All users')
	