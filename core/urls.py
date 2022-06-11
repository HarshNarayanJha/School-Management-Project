"""core URL Configuration"""

from django.urls import path
from . import views

app_name = "core"
urlpatterns = [
    path('', views.home, name='home'),
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
    path('debug/create/schools/', views.debug_create_schools, name='debug-schools-create'),
    path('debug/create/subjects/', views.debug_create_subjects, name='debug-subjects-create'),
    # path('debug/create/classes/', views.debug_create_classes, name='debug-classes-create'),
    path('debug/create/teachers/', views.debug_create_teachers, name='debug-teachers-create'),
    path('debug/create/admins/', views.debug_create_admins, name='debug-admins-create'),
]

urlpatterns += teacher_urlpatterns
urlpatterns += auth_urlpatterns
urlpatterns += debug_urlpatterns
