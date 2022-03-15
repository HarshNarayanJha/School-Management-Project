"""exam URL Configuration"""

from django.urls import path
from . import views

app_name = 'exams'
urlpatterns = [
    path('', views.home, name='home'),
    path('exams/', views.exams, name='exams'),
    path('exams/add/', views.exam_add, name='exam-add'),
    path('exams/<int:exmid>/', views.exam_detail, name='exam-detail'),
    path('exams/<int:exmid>/edit/', views.exam_edit, name='exam-edit'),
]
