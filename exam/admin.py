from django.contrib import admin

from students.models import Student

from .models import Exam, Result, Marks
from .forms import ResultsInlineFormSet
import nested_admin

class MarksInline(nested_admin.NestedTabularInline):
    model = Marks
    extra = 0
    
    # Makes the Marks inline collapsable
    classes = ["collapse"]

class ResultsInline(nested_admin.NestedTabularInline):
    model = Result
    formset = ResultsInlineFormSet
    inlines = [MarksInline]

    # readonly_fields = ("student",)

    # We don't want the teacher to accidently sort Results up and down 
    # (therefore ruining the order of roll no.)
    is_sortable = False

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        # formset.request = request
        formset.obj = obj
        return formset

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
    # As minimum no. of slots = total_no of students in class...

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

class ExamAdmin(nested_admin.NestedModelAdmin):
    list_display = ("name", "session", "cls")
    list_filter = ("name", "session", "cls")
    search_fields = ("name", "session", "cls")

    fieldsets = (
        ("Exam Info", {'fields': ("name", "session", "cls")}),
    )

    inlines = [ResultsInline]

    def get_inline_instances(self, request, obj=None):
        # If this Exam instance is not saved yet, add no result inlines...
        if obj is None:
            return []
        
        return super().get_inline_instances(request, obj)

admin.site.register(Exam, ExamAdmin)
# These aren't registered in production
# Can be registered for debugging...
# admin.site.register(Result)
# admin.site.register(Marks)