from django.contrib import admin
from django.contrib.auth.models import User
from django.utils.safestring import SafeString

from .models import Student, Teacher, Class
from exam.models import Result, Marks

import nested_admin

class MarksInline(nested_admin.NestedTabularInline):
    model = Marks
    extra = 0

class ResultInline(nested_admin.NestedStackedInline):
    model = Result
    extra = 0
    can_delete = False

    readonly_fields = ("exam",)
    inlines = [MarksInline]

    # The maximium number of results to be shown in a student's page
    # is **safely** equal to the no. of results of that student
    def get_max_num(self, request, obj=None, **kwargs):
        if obj is None:
            return 0
        
        return Result.objects.filter(student=obj).count()

class StudentAdmin(nested_admin.NestedModelAdmin):
    list_display = ("student_name", "uid", "dob", "cls", "roll")
    ordering = ("cls","roll")
    list_filter = ("cls",)
    search_fields = ("student_name", "uid", "dob")

    inlines = [ResultInline]

    def get_inline_instances(self, request, obj=None):
        # If this Student instance is not saved yet, add no result inlines...
        if obj is None:
            return []
        
        return super().get_inline_instances(request, obj)

class TeacherAdmin(admin.ModelAdmin):
    list_display = ("teacher_name", "subject", "teacher_of_class")
    ordering = ("teacher_of_class",)
    list_filter = ("teacher_of_class", "subject")
    search_fields = ("first_name", "last_name", "subject")

    def get_deleted_objects(self, objs, request):
        deleted_objects, model_count, perms_needed, protected =  super().get_deleted_objects(objs, request)
        objs = list(objs)
        users_deleted = 0

        for i in objs:
            users_deleted += 1
            if isinstance(i, Teacher):
                objs.append(i.user)
                deleted_objects.append(SafeString(f'User: <a href="/admin/auth/user/{i.user.id}/">{i.user}</a>'))
                model_count['users'] = users_deleted

        return (deleted_objects, model_count, perms_needed, protected)

def is_class_teacher(user):
    """
    Returns if the User is a class_teacher or not
    use `user.teacher.teacher_of_class` to access the class
    """
    if hasattr(user, "teacher"):
        return True if user.teacher.teacher_of_class else False
    return False

def is_exam_admin(user):
    """
    Returns if the User is a exam_admin or not
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
    elif user.is_exam_admin():
        return f"Exam Admin"
    else:
        return "Unknown"

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
User.add_to_class('is_exam_admin', is_exam_admin)
User.add_to_class('user_type', user_type)
User.add_to_class('get_display_name', get_display_name)

admin.site.register(Student, StudentAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Class)