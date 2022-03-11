from django.shortcuts import redirect, render
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from django.contrib import messages
from django.urls import reverse
import uuid
import csv

from .models import Student, Teacher, CLASSES
from .utils import get_create_success_message, get_roll_warning, get_uid_warning, get_update_success_message


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
    is_filter = bool(request.GET.get('is_filter', False))

    students_per_page = int(request.GET.get('students_per_page', 10) or 10)
    students_filter_name = request.GET.get('students_filter_name', "").strip()
    students_filter_uid = request.GET.get('students_filter_uid', "").strip()
    students_filter_phone = request.GET.get('students_filter_phone', "").strip()
    students_filter_aadhar = request.GET.get('students_filter_aadhar', "").strip()
    students_filter_mother = request.GET.get('students_filter_mother', "").strip()
    students_filter_father = request.GET.get('students_filter_father', "").strip()
    students_filter_cls = request.GET.get('students_filter_cls', "").strip()
    students_filter_gender = request.GET.get('students_filter_gender', "").strip()

    if (students_filter_name or students_filter_uid or \
        students_filter_phone or students_filter_aadhar or \
        students_filter_mother or students_filter_father or \
        students_filter_cls or students_filter_gender) or (students_per_page != 10):

        is_filter = True

        if students_filter_cls:
            all_students = Student.objects.all().filter(
                                    student_name__icontains=students_filter_name,
                                    uid__icontains=students_filter_uid,
                                    phone_number__icontains=students_filter_phone,
                                    aadhar_number__icontains=students_filter_aadhar,
                                    mothers_name__icontains=students_filter_mother,
                                    fathers_name__icontains=students_filter_father,
                                    cls=students_filter_cls,
                                    gender__icontains=students_filter_gender).order_by('roll')

        else:
            all_students = Student.objects.all().filter(
                                    student_name__icontains=students_filter_name,
                                    uid__icontains=students_filter_uid,
                                    phone_number__icontains=students_filter_phone,
                                    aadhar_number__icontains=students_filter_aadhar,
                                    mothers_name__icontains=students_filter_mother,
                                    fathers_name__icontains=students_filter_father,
                                    gender__icontains=students_filter_gender).order_by('cls', 'roll')
    else:
        is_filter = False
        all_students = Student.objects.all().order_by('cls', 'roll')

    paginator, students = create_paginator(all_students, page, students_per_page)

    pagination_get_parameters = f"&students_per_page={request.GET.get('students_per_page', '')}"
    pagination_get_parameters += f"&students_filter_name={request.GET.get('students_filter_name', '')}"
    pagination_get_parameters += f"&students_filter_uid={request.GET.get('students_filter_uid', '')}"
    pagination_get_parameters += f"&students_filter_phone={request.GET.get('students_filter_phone', '')}"
    pagination_get_parameters += f"&students_filter_aadhar={request.GET.get('students_filter_aadhar', '')}"
    pagination_get_parameters += f"&students_filter_mother={request.GET.get('students_filter_mother', '')}"
    pagination_get_parameters += f"&students_filter_father={request.GET.get('students_filter_father', '')}"
    pagination_get_parameters += f"&students_filter_cls={request.GET.get('students_filter_cls', '')}"
    pagination_get_parameters += f"&students_filter_gender={request.GET.get('students_filter_gender', '')}"
    pagination_get_parameters += f"&is_filter={bool(request.GET.get('is_filter', False))}"

    context = {
        'students': students,
        'num_all_students': len(all_students),
        'num_students': len(students),
        'is_filter': is_filter,
        'classes': CLASSES or [],
        'genders': Student.GENDERS or [],
        'pagination_get_parameters': pagination_get_parameters,
    }

    dark_mode_cookie = request.COOKIES.get("halfmoon_preferredMode") == "dark-mode"
    if dark_mode_cookie: context['dark_mode'] = 'dark-mode'

    return render(request, 'students.html', context=context)

def student_add(request: HttpRequest):

    if request.method == "POST":
        same_cls_roll = Student.objects.filter(cls=request.POST.get('cls')).filter(roll=request.POST.get('roll'))
        same_uid = Student.objects.filter(uid=request.POST.get('uid'))

        if same_cls_roll.exists():
            # A student in that class with the same roll exists....
            msg = get_roll_warning(request.POST.get('roll'), same_cls_roll[0].uid, request.POST.get('cls'))
            messages.warning(request, msg, extra_tags="danger")

            if same_uid.exists():
                msg = get_uid_warning(request.POST.get('uid'))
                messages.warning(request, msg, extra_tags="danger")
        
        else:
            try:
                new_stu: Student = Student.objects.create(school_code=request.POST.get("school_code"),
                                        student_name=request.POST.get("student_name"),
                                        fathers_name=request.POST.get("fathers_name"),
                                        mothers_name=request.POST.get("mothers_name"),
                                        admission_category=request.POST.get("admission_category"),
                                        social_category=request.POST.get("social_category"),
                                        uid=request.POST.get("uid"), cls=request.POST.get("cls"),
                                        roll=request.POST.get("roll"), gender=request.POST.get("gender"),
                                        dob=request.POST.get("dob"), doa=request.POST.get("doa"),
                                        aadhar_number=request.POST.get("aadhar_number"), phone_number=request.POST.get("phone_number"))

                messages.success(request, get_create_success_message(new_stu.student_name, new_stu.uid), extra_tags='success')
                return redirect("students:student-detail", uid=new_stu.uid)

            except IntegrityError as e:
                print(e)
                # uid_href = "{"+"url 'students:student-detail' uid={}".format(request.POST.get('uid')) + "}"
                # uid_href = f"/students/{request.POST.get('uid')}/#:~:text={request.POST.get('uid')}"

                # msg = f"Student with UID <a class=\"alert-link font-weight-bolder text-decoration-none\"\
                #         href=\"{uid_href}\" target=\"_blank\">{request.POST.get('uid')}</a> already exists.. maybe you mistyped!"

                msg = get_uid_warning(request.POST.get('uid'))
                messages.warning(request, msg, extra_tags="danger")

    context = {
        'genders': list(Student.GENDERS),
        'admission_categories': list(Student.ADMISSION_CATEGORIES),
        'social_categories': list(Student.SOCIAL_CATEGORIES),
        'classes': CLASSES
    }
    dark_mode_cookie = request.COOKIES.get("halfmoon_preferredMode") == "dark-mode"
    if dark_mode_cookie: context['dark_mode'] = 'dark-mode'

    return render(request, 'student_add.html', context=context)

def student_detail(request: HttpRequest, uid: str):

    try:
        stu = Student.objects.get(uid=uid)
    except ObjectDoesNotExist:
        context = {
            'message_404': f'Student with UID <code class="code font-size-18 text-secondary">{uid}</code> was <span class="text-danger">not found</span>!'
        }
        dark_mode_cookie = request.COOKIES.get("halfmoon_preferredMode") == "dark-mode"
        if dark_mode_cookie: context['dark_mode'] = 'dark-mode'
        return render(request, '404.html', context=context)

    context = {
        'stu': stu
    }

    dark_mode_cookie = request.COOKIES.get("halfmoon_preferredMode") == "dark-mode"
    if dark_mode_cookie: context['dark_mode'] = 'dark-mode'

    return render(request, 'student_detail.html', context=context)

def student_edit(request: HttpRequest, uid: str):
    stu: Student = Student.objects.get(uid=uid)

    if request.method == "POST":
        same_cls_roll = Student.objects.filter(cls=request.POST.get('cls')).filter(roll=request.POST.get('roll'))
        same_cls_roll = same_cls_roll.exclude(uid=stu.uid)

        if same_cls_roll.exists():
            # A student in that class with the same roll exists....
            msg = get_roll_warning(request.POST.get('roll'), same_cls_roll[0].uid, request.POST.get('cls'))
            messages.warning(request, msg, extra_tags="danger")

        else:
            # complete mess, this doesn't work!!!
            # stu.student_name = request.POST.get('student_name')
            # stu.fathers_name = request.POST.get('fathers_name')
            # stu.mothers_name = request.POST.get('mothers_name')
            # stu.dob = request.POST.get('dob')
            # stu.gender = request.POST.get('gender')
            # stu.aadhar_number = request.POST.get('aadhar_number')
            # stu.phone_number = request.POST.get('phone_number')
            # stu.school_code = request.POST.get('school_code')
            # stu.uid = request.POST.get('uid')
            # stu.admission_category = request.POST.get('admission_category')
            # stu.social_category = request.POST.get('social_category')
            # stu.doa = request.POST.get('doa')
            # stu.cls = request.POST.get('cls')
            # stu.roll = request.POST.get('roll')

            for field, value in request.POST.items():
                setattr(stu, field, value)

            stu.save()
            messages.success(request, get_update_success_message(stu.student_name), extra_tags='success')

            return redirect('students:student-detail', uid=uid)

    context = {
        'stu': stu,
        'genders': list(Student.GENDERS),
        'admission_categories': list(Student.ADMISSION_CATEGORIES),
        'social_categories': list(Student.SOCIAL_CATEGORIES),
        'classes': CLASSES
    }

    dark_mode_cookie = request.COOKIES.get("halfmoon_preferredMode") == "dark-mode"
    if dark_mode_cookie: context['dark_mode'] = 'dark-mode'

    return render(request, 'student_edit.html', context=context)

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