"""students URL Configuration"""

from django.urls import path
from . import views

app_name = "students"
urlpatterns = [
    path('', views.home, name='home'),
    path('students/', views.students, name='students'),
    path('students/add/', views.student_add, name='student-add'),
    path('students/<str:uid>/', views.student_detail, name='student-detail'),
    path('students/<str:uid>/edit/', views.student_edit, name='student-edit'),
    path('students/upload/bulk/', views.students_upload, name='students-upload'),
]

debug_urlpatterns = [
    path('debug/delete/students/', views.debug_delete_students, name='debug-students-delete'),
]

urlpatterns += debug_urlpatterns