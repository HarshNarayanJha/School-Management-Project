from django import forms

from .models import Result, Exam
from students.models import Student

class ResultsInlineFormSet(forms.models.BaseInlineFormSet):
    model = Result

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self.obj is None when the model is not saved yet...
        if self.obj is None:
            return

        # get the currently editing Exam model instance
        exam = Exam.objects.get(pk=self.obj.id)

        # If the Exam instance has already some students saved, append them first to the self.initial
        # In the order of roll number
        self.initial: list = []
        for result in exam.result_set.get_queryset().order_by("student__roll"):
            self.initial.append({'student': result.student})

        # Prepare a list of already added students
        self.added_students: list = []
        for k in self.initial: self.added_students.append(k['student'])

        # For each student in that class...
        for student in Student.objects.filter(cls=exam.cls).order_by('roll'):
            # If the student is not already added...
            if student not in self.added_students:
                # Add it to self.initials
                self.initial.append({'student': student})