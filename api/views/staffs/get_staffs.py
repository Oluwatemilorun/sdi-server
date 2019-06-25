from django.http import HttpResponse

from api.models import Staff

def get_staffs(request):
    return HttpResponse('All staffs')	
	