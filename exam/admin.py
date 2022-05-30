from django.contrib import admin
from django.http import HttpRequest

from students.models import Student, Class
from .models import Exam, Result, Marks, Subject, ExamAdmin
from .forms import ResultsInlineFormSet
import nested_admin

class MarksInline(nested_admin.NestedTabularInline):
    model = Marks
    extra = 0
    
    # Makes the Marks inline collapsable
    classes = ["collapse"]

    can_delete = False

    # Restrict the `subject` dropdown in the Marks inline to only those subjects
    # which are in this class

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "subject":
            exam_obj = Exam.objects.get(id=request.resolver_match.kwargs['object_id'])

            kwargs["limit_choices_to"] = {'class': exam_obj.cls}

        return super().formfield_for_choice_field(db_field, request, **kwargs)

    def has_change_permission(self, request, obj: Exam=None):
        if request.user.is_class_teacher():
            if obj is not None:
                if hasattr(obj, "exam"):
                    if obj.exam.edited_by_class_teacher:
                        return False
                    else:
                        return True
                elif hasattr(obj, "result"):
                    if obj.result.exam.edited_by_class_teacher:
                        return False
                    else:
                        return True
            else:
                return False
        else:
            return True

class ResultsInline(nested_admin.NestedTabularInline):
    model = Result
    formset = ResultsInlineFormSet
    inlines = [MarksInline]

    can_delete = False

    # NOTE #1:
    # Probably want this, but the issue with this is that
    # not yet saved Result instances will have a - (dash) inplace of student name...
    # readonly_fields = ("student",)

    # We don't want the teacher to accidently sort Results up and down 
    # (therefore ruining the order of roll no.)
    is_sortable = False

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        # formset.request = request
        formset.obj = obj
        return formset

    # Restrict the `student` dropdown in the Result inline to only those students 
    # who are in this class

    # Be we would ultimately want the `student` field to be readonly
    # as it is pre-populated, See NOTE #1 above
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        exam_obj = Exam.objects.get(id=request.resolver_match.kwargs['object_id'])
        if db_field.name == "student":
            kwargs["queryset"] = Student.objects.filter(cls=exam_obj.cls)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    #  We want the Results in the order of student's roll number, no matter the entry order
    def get_queryset(self, request):
        return super().get_queryset(request).order_by("student__roll")

    # Defines how many 'extra' (or initial) result slots we get when creating (or editing an exam instance)
    def get_extra(self, request, obj=None, **kwargs):
        # If exam is not saved yet, we do not need any...
        if obj is None:
            return 0

        exam = Exam.objects.get(pk=obj.id)
        total = Student.objects.filter(cls=exam.cls).count()
        done = exam.result_set.get_queryset().count()

        # Return extra slots as (total_students_in_class - students_saved_in_exam)
        return total - done

    ## Enabling this method causes an error to raise when saving
    # Don't know why ???
    # As minimum no. of slots (should=) total_no of students in class...

    # def get_min_num(self, request, obj=None, **kwargs):
    #     if obj is None:
    #         return super().get_min_num(request, obj, **kwargs)
    #     else:
    #         cls = Exam.objects.get(pk=obj.id).cls
    #         total = Student.objects.filter(cls=cls).count()
    #         return total

    # Maximum slots = total no. of students in class
    def get_max_num(self, request, obj=None, **kwargs):

        cls = Exam.objects.get(pk=obj.id).cls
        total = Student.objects.filter(cls=cls).count()

        return total

    def has_change_permission(self, request, obj: Exam=None):
        if request.user.is_class_teacher():
            if obj is not None:
                if hasattr(obj, "exam"):
                    if obj.exam.edited_by_class_teacher:
                        return False
                    else:
                        return True
                else:
                    if obj.edited_by_class_teacher:
                        return False
                    else:
                        return True
            else:
                return False
        else:
            return True

class ExamAdmin_(nested_admin.NestedModelAdmin):
    list_display = ("__str__", "session", "cls")
    list_filter = ("exam_name", "session", "cls")
    search_fields = ("exam_name", "session", "cls")

    fieldsets = (
        ("Exam Info", {'fields': ("exam_name", "session", "cls")}),
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_class_teacher():
            return super().formfield_for_foreignkey(db_field, request, **kwargs)
            
        cls = request.user.teacher.teacher_of_class
        if db_field.name == "cls":
            kwargs["queryset"] = Class.objects.filter(cls=cls.cls, section=cls.section)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_changeform_initial_data(self, request):
        if request.user.is_class_teacher():
            return {'cls': request.user.teacher.teacher_of_class}

    inlines = [ResultsInline]

    def get_inline_instances(self, request, obj=None):
        # If this Exam instance is not saved yet, add no result inlines...
        if obj is None:
            return []
        
        return super().get_inline_instances(request, obj)

    def has_change_permission(self, request, obj: Exam=None):
        if not request.user.is_class_teacher(): return True
        if obj is None: return False
        if obj.edited_by_class_teacher: return False

        return True

# This is the Admin class of the class Exam
admin.site.register(Exam, ExamAdmin_)
admin.site.register(Subject)
# This is the 'user/real' ExamAdmin
admin.site.register(ExamAdmin)
# These aren't registered in production
# Can be registered for debugging...
# admin.site.register(Result)
# admin.site.register(Marks)