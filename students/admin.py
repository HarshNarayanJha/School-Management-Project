from django.contrib import admin
from django.contrib.auth.models import User

from .models import Student
from exam.models import Result, Marks

import nested_admin

class MarksInline(nested_admin.NestedTabularInline):
    model = Marks
    extra = 0
    can_delete = False
    classes = ["collapse"]

class ResultInline(nested_admin.NestedStackedInline):
    model = Result
    extra = 0
    can_delete = False
    is_sortable = False

    readonly_fields = ("exam",)
    inlines = [MarksInline]

    # The maximium number of results to be shown in a student's page
    # is **safely** equal to the no. of results of that student
    def get_max_num(self, request, obj=None, **kwargs):
        if obj is None:
            return 0
        
        return Result.objects.filter(student=obj).count()

class StudentAdmin(nested_admin.NestedModelAdmin):
    list_display = ("student_name", "school_code", "uid", "dob", "cls", "roll", "gender", "phone_number")
    ordering = ("school__school_code", "cls", "roll", "student_name")
    list_filter = ("school__school_code", "gender", "cls")
    search_fields = ("student_name", "uid", "dob", "phone_number")

    def school_code(self, stu):
        return stu.school.school_code

    inlines = [ResultInline]

    def get_inline_instances(self, request, obj=None):
        # If this Student instance is not saved yet, add no result inlines...
        if obj is None:
            return []
        
        return super().get_inline_instances(request, obj)

admin.site.register(Student, StudentAdmin)