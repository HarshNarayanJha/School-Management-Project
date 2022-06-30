"""exam URL Configuration"""

from django.urls import path
from . import views

app_name = 'exams'
urlpatterns = [
    path('', views.home, name='home'),
    path('exams/', views.exams, name='exams'),
    path('exams/add/', views.exam_add, name='exam-add'),
    path('exams/type/add/', views.exam_type_add, name='exam-type-add'),
    path('exams/set/add/', views.exam_set_add, name='exam-set-add'),
    path('exams/<int:exmid>/', views.exam_detail, name='exam-detail'),
    path('exams/<int:exmid>/edit/', views.exam_edit, name='exam-edit'),

    path('exams/result/calculate/', views.exam_calculate_result, name='exam-calculate-result'),
]
