from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Student, Teacher


def home(request: HttpRequest):
    return render(request, 'students_home.html', context={})

def students(request: HttpRequest):
    all_students = Student.objects.all().order_by('cls', 'roll')
    page = request.GET.get('page',1)
    paginator = Paginator(all_students,10)
    try:
        students = paginator.page(page)
    except PageNotAnInteger:
        students = paginator.page(1)
    except EmptyPage:
        students = paginator.page(paginator.num_pages)
    context = {
        'students': students,
    }
    return render(request, 'students.html', context=context)