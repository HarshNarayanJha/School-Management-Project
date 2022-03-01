from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from .models import Exam
from students.models import Student

def home(request: HttpRequest):
    context = {}

    dark_mode_cookie = request.COOKIES.get("halfmoon_preferredMode") == "dark-mode"
    if dark_mode_cookie: context['dark_mode'] = 'dark-mode'

    return render(request, 'exam_home.html', context=context)

def exams(request: HttpRequest):
    exam = Exam.objects.all()

    context = {
        'exams': exam,
    }

    dark_mode_cookie = request.COOKIES.get("halfmoon_preferredMode") == "dark-mode"
    if dark_mode_cookie: context['dark_mode'] = 'dark-mode'

    return render(request, 'exams.html', context=context)