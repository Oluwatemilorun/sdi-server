from django.urls import path

from . import views

urlpatterns = [
	path('users', views.users.get_users, name='get_users')
]
