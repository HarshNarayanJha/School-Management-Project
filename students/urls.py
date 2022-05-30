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

teacher_urlpatterns = [
    path('teachers/', views.teachers, name='teachers'),
    path('teachers/add/', views.teacher_add, name='teacher-add'),
    path('teachers/<int:tid>/', views.teacher_detail, name='teacher-detail'),
    path('teachers/<int:tid>/edit/', views.teacher_edit, name='teacher-edit'),
    # path('teachers/upload/bulk/', views.students_upload, name='students-upload'),
]

auth_urlpatterns = [
    path('accounts/login/', views.login, name='login'),
    path('accounts/logout/', views.logout, name='logout'),
]

debug_urlpatterns = [
    path('debug/', views.debug, name='debug'),
    path('debug/create/subjects/', views.debug_create_subjects, name='debug-subjects-create'),
    path('debug/create/classes/', views.debug_create_classes, name='debug-classes-create'),
    path('debug/delete/students/', views.debug_delete_students, name='debug-students-delete'),
]

urlpatterns += teacher_urlpatterns
urlpatterns += auth_urlpatterns
urlpatterns += debug_urlpatterns
