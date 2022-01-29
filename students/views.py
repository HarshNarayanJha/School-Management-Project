from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

from .models import Student, Teacher


def home(request: HttpRequest):
    return render(request, 'students_home.html', context={})

def students(request: HttpRequest):
    all_students = Student.objects.all().order_by('cls', 'roll')
    context = {
        'students': all_students,
    }
    return render(request, 'students.html', context=context)