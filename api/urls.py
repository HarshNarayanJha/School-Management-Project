"""api URL Configuration"""

from django.urls import path
from . import views

app_name = 'api'
urlpatterns = [
    path('', views.home, name='home'),
    path('students/', views.all_students, name='students'),
    path('students/<int:uid>/', views.student, name='student-detail'),
    path('students/bulk/', views.students_bulk, name='students-bulk'),

    path('exams/', views.all_exams, name='exams'),
    path('exams/<int:exmid>/', views.exam, name='exam-detail'),

    path('results/', views.all_results, name='results'),
    path('results/<int:resid>/', views.result, name='result-detail'),

    path('marks/', views.all_marks, name='marks'),
    path('marks/<int:mrkid>/', views.mark, name='mark-detail'),

    path('classes/', views.all_classes, name='classes'),
    path('classes/<str:cls>/', views.class_, name='class-detail'),

    path('subjects/', views.all_subjects, name='subjects'),
    path('subjects/<str:subname>/', views.subject, name='subject-detail'),
]
