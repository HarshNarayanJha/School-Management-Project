from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

# Create your views here.

def home(request: HttpRequest):
    return render(request, 'exam_home.html', context={})