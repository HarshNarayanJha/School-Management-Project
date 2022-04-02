from django.http import HttpRequest, HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from school_management import settings

from .views_students import all_students, students_bulk, all_classes, student, class_
from .views_exams import all_exams, exam, all_results, result, all_marks, mark, all_subjects, subject

def home(request: HttpRequest) -> HttpResponse:
    return HttpResponse("This is API home.")