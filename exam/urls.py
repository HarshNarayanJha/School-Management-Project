"""exam URL Configuration"""

from django.urls import path
from . import views

app_name = 'exam'
urlpatterns = [
    path('', views.home, name='home'),
    path('exams/', views.exams, name='exams'),
]
