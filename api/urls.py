from django.urls import path

from . import views

urlpatterns = [
	path('users', views.users.get_users, name='get_users'),
	path('staffs', views.staffs.get_staffs, name= 'get_staffs'),
]
