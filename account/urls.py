from django.urls import path
from . import views

app_name = 'account'

urlpatterns = [
	path('', views.account, name='account'),
	path('login/', views.login_view, name='login'),
	path('logout/', views.logout_view, name='logout'),
	path('status/', views.auth_status, name='status'),
]
