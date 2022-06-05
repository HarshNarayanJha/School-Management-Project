from django.contrib import admin
from django.contrib.auth.models import User

from .models import Student
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

admin.site.register(Student, StudentAdmin)