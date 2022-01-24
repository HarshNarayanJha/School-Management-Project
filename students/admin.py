from django.contrib import admin
from .models import Student, Teacher
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

    def get_max_num(self, request, obj=None, **kwargs):
        if obj is None:
            return 0
        
        return Result.objects.filter(student=obj).count()

class StudentAdmin(nested_admin.NestedModelAdmin):
    list_display = ("full_name","first_name", "last_name", "uid", "dob", "cls", "roll")
    ordering = ("cls",)
    list_filter = ("cls",)
    search_fields = ("first_name", "last_name", "uid", "dob")

    inlines = [ResultInline]

    def get_inline_instances(self, request, obj=None):
        # If this Student instance is not saved yet, add no result inlines...
        if obj is None:
            return []
        
        return super().get_inline_instances(request, obj)

class TeacherAdmin(admin.ModelAdmin):
    list_display = ("full_name","first_name", "last_name", "subject", "teacher_of_class")
    ordering = ("teacher_of_class",)
    list_filter = ("teacher_of_class", "subject")
    search_fields = ("first_name", "last_name", "subject")

admin.site.register(Student, StudentAdmin)
admin.site.register(Teacher, TeacherAdmin)