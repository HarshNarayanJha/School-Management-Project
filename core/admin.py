from django.contrib import admin
from django.contrib.auth.models import User
from django.utils.safestring import SafeString

from .models import Subject, ExamAdmin, Teacher, Class

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
                if i.user:
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

admin.site.register(Subject)
admin.site.register(Class)
admin.site.register(ExamAdmin)
admin.site.register(Teacher, TeacherAdmin)