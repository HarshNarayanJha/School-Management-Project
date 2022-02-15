from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from .models import Exam
from students.models import Student

def home(request: HttpRequest):
    return render(request, 'exam_home.html', context={})

def exams(request: HttpRequest):
    exam = Exam.objects.all()

    context = {
        'exams': exam,
    }
    return render(request, 'exams.html', context=context)