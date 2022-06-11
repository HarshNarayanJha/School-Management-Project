from django.contrib import admin
from django.contrib.auth.models import User
from django.utils.safestring import SafeString
from exam.models import Exam

from students.models import Student

from .models import Subject, ExamAdmin, Teacher, Class, School

class ExamAdminAdmin(admin.ModelAdmin):
    list_display = ("admin_name", "user_name", "school_code")
    ordering = ("school__school_code", "admin_name",)
    list_filter = ("school__school_code",)
    search_fields = ("admin_name", "user_name")

    def school_code(self, ad):
        return ad.school.school_code

    def get_deleted_objects(self, objs, request):
        deleted_objects, model_count, perms_needed, protected =  super().get_deleted_objects(objs, request)
        objs = list(objs)
        users_deleted = 0

        for i in objs:
            users_deleted += 1
            if isinstance(i, ExamAdmin):
                if i.user:
                    objs.append(i.user)
                    deleted_objects.append(SafeString(f'User: <a href="/admin/auth/user/{i.user.id}/">{i.user}</a>'))
                    model_count['users'] = users_deleted

        return (deleted_objects, model_count, perms_needed, protected)

class TeacherAdmin(admin.ModelAdmin):
    list_display = ("teacher_name", "school_code", "subject", "teacher_of_class", "salary")
    ordering = ("school__school_code", "teacher_of_class",)
    list_filter = ("school__school_code", "teacher_of_class", "subject")
    search_fields = ("teacher_name", "user_name", "subject__subject_name")


    def school_code(self, tea):
        return tea.school.school_code

    def get_deleted_objects(self, objs, request):
        deleted_objects, model_count, perms_needed, protected =  super().get_deleted_objects(objs, request)
        objs = list(objs)
        users_deleted = 0

        for i in objs:
            users_deleted += 1
            if isinstance(i, Teacher):
                if i.user:
                    objs.append(i.user)
                    deleted_objects.append(SafeString(f'User: <a href="/admin/auth/user/{i.user.id}/">{i.user}</a>'))
                    model_count['users'] = users_deleted

        return (deleted_objects, model_count, perms_needed, protected)

class ClassAdmin(admin.ModelAdmin):
    list_display = ("__str__", "school_code", "cls", "section", "stream")
    ordering = ("school__school_code", "cls", "section")
    list_filter = ("school__school_code", "cls", "section")
    search_fields = ("cls", "stream", "section")

    def school_code(self, cls):
        return cls.school.school_code

class SchoolAdmin(admin.ModelAdmin):
    list_display = ("school_code", "school_name", "city")
    ordering = ("school_code",)
    list_filter = ("city", )
    search_fields = ("school_code", "school_name", "school_name_short", "city")

def is_class_teacher(user):
    """
    Returns if the User is a class_teacher or not
    use `user.teacher.teacher_of_class` to access the class
    """
    if hasattr(user, "teacher"):
        return True if user.teacher.teacher_of_class else False
    return False

def is_examadmin(user):
    """
    Returns if the User is a examadmin or not
    """
    if hasattr(user, "examadmin"):
        return True
    return False

def user_type(user):
    """
    Returns the type of the user\n
    One of `["Teacher", "ExamAdmin"...]` or `"Superuser"`
    """
    if user.is_superuser:
        return "Superuser"
    elif user.is_class_teacher():
        return f"Class Teacher of {user.teacher.teacher_of_class}"
    elif not user.is_class_teacher() and hasattr(user, "teacher"):
        return f"Teacher of {user.teacher.subject}"
    elif user.is_examadmin():
        return f"Exam Admin"
    else:
        return "???"

def get_school(user):
    """
    Returns the School associated with the user, if in anyway, or None
    """
    if user.is_superuser: return None
    elif hasattr(user, "teacher"): return user.teacher.school
    elif user.is_examadmin(): return user.examadmin.school
    else: return None

def get_display_name(user):
    """
    Returns the appropriate name for the user_type
    - For Teacher, `user.teacher.teacher_name`
    - For ExamAdmin, `user.examadmin.admin_name`
    - Anything else, `user.username`
    """
    if hasattr(user, "teacher"):
        if user.teacher:
            return user.teacher.teacher_name
    elif hasattr(user, "examadmin"):
        if user.examadmin:
            return user.examadmin.admin_name

    return user.username

User.add_to_class('is_class_teacher', is_class_teacher)
User.add_to_class('is_examadmin', is_examadmin)
User.add_to_class('user_type', user_type)
User.add_to_class('get_display_name', get_display_name)
User.add_to_class('get_school', get_school)

def get_students(school):
    """
    Returns all the Students of the passed school
    """
    return Student.objects.filter(school__pk=school.pk)

def get_exams(school):
    """
    Returns all the Exams of the passed school
    """
    return Exam.objects.filter(school__pk=school.pk)

School.add_to_class('get_students', get_students)
School.add_to_class('get_exams', get_exams)

admin.site.register(School, SchoolAdmin)
admin.site.register(Class, ClassAdmin)
admin.site.register(Subject)
admin.site.register(ExamAdmin, ExamAdminAdmin)
admin.site.register(Teacher, TeacherAdmin)