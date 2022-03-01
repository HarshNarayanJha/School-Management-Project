from django.shortcuts import redirect, render
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.files.storage import FileSystemStorage
import uuid
import csv

from .models import Student, Teacher

def home(request: HttpRequest):

    context = {}

    dark_mode_cookie = request.COOKIES.get("halfmoon_preferredMode") == "dark-mode"
    if dark_mode_cookie: context['dark_mode'] = 'dark-mode'

    return render(request, 'students_home.html', context=context)

def students(request: HttpRequest):

    def create_paginator(all_students, page, per_page=10):
        paginator = Paginator(all_students, per_page)
        try:
            students = paginator.page(page)
        except PageNotAnInteger:
            students = paginator.page(1)
        except EmptyPage:
            students = paginator.page(paginator.num_pages)

        return paginator, students

    page = request.GET.get('page', 1)
    is_filter = request.GET.get('is_filter', False)

    students_per_page = int(request.GET.get('students_per_page', 10) or 10)
    students_filter_name = request.GET.get('students_filter_name', "").strip()
    students_filter_uid = request.GET.get('students_filter_uid', "").strip()
    students_filter_phone = request.GET.get('students_filter_phone', "").strip()
    students_filter_aadhar = request.GET.get('students_filter_aadhar', "").strip()

    if students_per_page != 10:
        is_filter = True

    if students_filter_name or students_filter_uid or students_filter_phone or students_filter_aadhar:
        is_filter = True

        all_students = Student.objects.all().filter(
                                student_name__icontains=students_filter_name,
                                uid__icontains=students_filter_uid,
                                phone_number__icontains=students_filter_phone,
                                aadhar_number__icontains=students_filter_aadhar).order_by('cls', 'roll')
    else:
        all_students = Student.objects.all().order_by('cls', 'roll')

    paginator, students = create_paginator(all_students, page, students_per_page)

    pagination_get_parameters = f"&is_filter={request.GET.get('is_filter', False)}"
    pagination_get_parameters += f"&students_per_page={request.GET.get('students_per_page', '')}"
    pagination_get_parameters += f"&students_filter_name={request.GET.get('students_filter_name', '')}"
    pagination_get_parameters += f"&students_filter_uid={request.GET.get('students_filter_uid', '')}"
    pagination_get_parameters += f"&students_filter_phone={request.GET.get('students_filter_phone', '')}"
    pagination_get_parameters += f"&students_filter_aadhar={request.GET.get('students_filter_aadhar', '')}"

    context = {
        'students': students,
        'is_filter': is_filter,
        'pagination_get_parameters': pagination_get_parameters,
    }

    dark_mode_cookie = request.COOKIES.get("halfmoon_preferredMode") == "dark-mode"
    if dark_mode_cookie: context['dark_mode'] = 'dark-mode'

    return render(request, 'students.html', context=context)

def student_detail(request: HttpRequest, uid: str):
    stu = Student.objects.get(uid=uid)

    context = {
        'stu': stu
    }

    dark_mode_cookie = request.COOKIES.get("halfmoon_preferredMode") == "dark-mode"
    if dark_mode_cookie: context['dark_mode'] = 'dark-mode'

    return render(request, 'student_detail.html', context=context)

def student_edit(request: HttpRequest, uid: str):

    context = {}
    dark_mode_cookie = request.COOKIES.get("halfmoon_preferredMode") == "dark-mode"
    if dark_mode_cookie: context['dark_mode'] = 'dark-mode'

    return HttpResponse(f"edit {uid}")

def students_upload(request: HttpRequest):

    students_list = []
    duplicate_students_list = []
    
    if request.method == 'POST' and request.FILES['students-file-input']:
        uploaded_file = request.FILES['students-file-input']
        fs = FileSystemStorage()
        filename = fs.save(str(uuid.uuid4())+".csv", uploaded_file)
        f = open(filename,"r")
        csvreader = csv.reader(f)

        # skip header
        next(csvreader)

        for d in csvreader:
            s = Student(school_code=d[0], student_name=d[1], fathers_name=d[2], mothers_name=d[3], admission_category=d[4],
            social_category=d[5], uid=d[6], cls=d[7], roll=d[8], gender=d[9], dob=d[10], doa=d[11], aadhar_number=d[12], phone_number=d[13])

            # If the student with the same UID already exists, don't add it to the bulk create list...
            if Student.objects.filter(uid=s.uid).exists():
                duplicate_students_list.append(s)
            else:
                students_list.append(s)

        f.close()
        fs.delete(filename)

        Student.objects.bulk_create(students_list)
        #['school_code','student_name','fathers_name','mothers_name','admission_category',
        #'social_category','uid','cls','roll','gender','dob','doa','aadhar_number','phone_number'])

    context = {
        "students_added": students_list,
        "students_not_added": duplicate_students_list
    }

    dark_mode_cookie = request.COOKIES.get("halfmoon_preferredMode") == "dark-mode"
    if dark_mode_cookie: context['dark_mode'] = 'dark-mode'

    return render(request, 'students_upload.html', context=context)