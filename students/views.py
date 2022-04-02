import re
from django.shortcuts import redirect, render
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from django.contrib import messages
from django.urls import reverse
import datetime
import uuid
import csv


from .models import Student, Teacher, Class
from exam.models import Subject, CLASS_SUBJECTS

from .utils import get_invalid_value_message, get_create_success_message, get_roll_warning, get_uid_warning,\
                    get_update_success_message, get_birthdays


def home(request: HttpRequest):

    context = {
        'birthdays': get_birthdays(),
    }

    dark_mode_cookie = request.COOKIES.get("halfmoon_preferredMode") == "dark-mode"
    if dark_mode_cookie: context['dark_mode'] = 'dark-mode'

    return render(request, 'students_home.html', context=context)

def debug(request: HttpRequest):
    context = {}

    dark_mode_cookie = request.COOKIES.get("halfmoon_preferredMode") == "dark-mode"
    if dark_mode_cookie: context['dark_mode'] = 'dark-mode'

    return render(request, 'utils/debug.html', context=context)

def debug_create_subjects(request: HttpRequest):
    subject_objs = []
    for subject in Subject.SUBJECTS:
        if not Subject.objects.filter(subject_name=subject[0]).exists():
            subject_objs.append(Subject(subject_name=subject[0]))

    Subject.objects.bulk_create(subject_objs)

    return redirect('students:debug')

def debug_create_classes(request: HttpRequest):
    cls_objs = []
    for cls in Class.CLASSES:
        if not Class.objects.filter(cls=cls[0]).exists():
            _cls: Class = Class.objects.create(cls=cls[0])

            _cls_subjects_raw: list[str] = CLASS_SUBJECTS[_cls.cls]
            cls_subjects: list[Subject] = []

            for _sub in _cls_subjects_raw:
                cls_subjects.append(Subject.objects.get_or_create(subject_name=_sub)[0])

            _cls.cls_subjects.set(cls_subjects)
            cls_objs.append(_cls)

    try:
        # This gives integrity error with `student_class.id`.
        # don't know why, but last class (12th) gets succesfully created, and all subjects assinged!
        Class.objects.bulk_create(cls_objs)
    except:
        print("H" + "o"*15 + ":Err" + "o"*15 + "r")
    
    return redirect('students:debug')

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
                                    cls__cls=students_filter_cls,
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
        'classes': Class.CLASSES or [],
        'genders': Student.GENDERS or [],
        'pagination_get_parameters': pagination_get_parameters,
    }

    dark_mode_cookie = request.COOKIES.get("halfmoon_preferredMode") == "dark-mode"
    if dark_mode_cookie: context['dark_mode'] = 'dark-mode'

    return render(request, 'students.html', context=context)

def student_add(request: HttpRequest):

    if request.method == "POST":
        _cls, _cls_created = Class.objects.get_or_create(cls=request.POST.get('cls'))
        same_cls_roll = Student.objects.filter(cls=_cls).filter(roll=request.POST.get('roll'))
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
                                        uid=request.POST.get("uid"), cls=_cls,
                                        roll=request.POST.get("roll"), gender=request.POST.get("gender"),
                                        dob=request.POST.get("dob"), doa=request.POST.get("doa"),
                                        aadhar_number=request.POST.get("aadhar_number"), phone_number=request.POST.get("phone_number"))

                messages.success(request, get_create_success_message(new_stu.student_name, new_stu.uid), extra_tags='success')
                return redirect("students:student-detail", uid=new_stu.uid)

            except IntegrityError as e:
                print(e)
                msg = get_uid_warning(request.POST.get('uid'))
                messages.warning(request, msg, extra_tags="danger")

    context = {
        'genders': list(Student.GENDERS),
        'admission_categories': list(Student.ADMISSION_CATEGORIES),
        'social_categories': list(Student.SOCIAL_CATEGORIES),
        'classes': Class.CLASSES
    }
    dark_mode_cookie = request.COOKIES.get("halfmoon_preferredMode") == "dark-mode"
    if dark_mode_cookie: context['dark_mode'] = 'dark-mode'

    return render(request, 'student_add.html', context=context)

def student_detail(request: HttpRequest, uid: str):

    try:
        stu: Student = Student.objects.get(uid=uid)
    except ObjectDoesNotExist:
        context = {
            'message_404': f'Student with UID <code class="code font-size-18 text-secondary">{uid}</code> was <span class="text-danger">not found</span>!'
        }
        dark_mode_cookie = request.COOKIES.get("halfmoon_preferredMode") == "dark-mode"
        if dark_mode_cookie: context['dark_mode'] = 'dark-mode'
        return render(request, '404.html', context=context)

    context = {
        'stu': stu,
        'social_category_display': dict(Student.SOCIAL_CATEGORIES)[stu.social_category],
    }

    dark_mode_cookie = request.COOKIES.get("halfmoon_preferredMode") == "dark-mode"
    if dark_mode_cookie: context['dark_mode'] = 'dark-mode'

    return render(request, 'student_detail.html', context=context)

def student_edit(request: HttpRequest, uid: str):
    stu: Student = Student.objects.get(uid=uid)

    if request.method == "POST":
        _cls = Class.objects.get(cls=request.POST.get('cls'))
        same_cls_roll = Student.objects.filter(cls=_cls).filter(roll=request.POST.get('roll'))
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
                if field == "cls":
                    setattr(stu, field, _cls)
                else:
                    setattr(stu, field, value)

            stu.save()
            messages.success(request, get_update_success_message(stu.student_name), extra_tags='success')

            return redirect('students:student-detail', uid=uid)

    context = {
        'stu': stu,
        'genders': list(Student.GENDERS),
        'admission_categories': list(Student.ADMISSION_CATEGORIES),
        'social_categories': dict(Student.SOCIAL_CATEGORIES),
        'classes': Class.CLASSES
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
        filename = fs.save(str(uuid.uuid4()) + ".csv", uploaded_file)
        f = open(filename, "r")
        csvreader = csv.reader(f)

        # skip header
        next(csvreader)

        line_no = 2

        for d in csvreader:
            # Class check
            if d[7] not in dict(Class.CLASSES):
                msg = get_invalid_value_message("Class", d[7], line_no, d[6], list(dict(Class.CLASSES)))
                messages.error(request, msg, extra_tags="danger")
                print(f"Invalid Class {d[7]} on line {line_no} of UID {d[6]}")
                return redirect("students:students-upload")

            cls, cls_created = Class.objects.get_or_create(cls=d[7])

            # Gender check
            if d[9] not in dict(Student.GENDERS):
                msg = get_invalid_value_message("Gender", d[9], line_no, d[6], list(dict(Student.GENDERS)))
                messages.error(request, msg, extra_tags="danger")
                print(f"Invalid Gender {d[9]} on line {line_no} of UID {d[6]}")
                return redirect("students:students-upload")

            # Social Cat and Addmission Cat check
            if d[4] not in dict(Student.ADMISSION_CATEGORIES):
                msg = get_invalid_value_message("Admission Category", d[4], line_no, d[6], list(dict(Student.ADMISSION_CATEGORIES)))
                messages.error(request, msg, extra_tags="danger")
                print(f"Invalid Admission Category {d[4]} on line {line_no} of UID {d[6]}")
                return redirect("students:students-upload")

            if d[5] not in dict(Student.SOCIAL_CATEGORIES).values():
                msg = get_invalid_value_message("Social Category", d[5], line_no, d[6], list(dict(Student.SOCIAL_CATEGORIES)))
                messages.error(request, msg, extra_tags="danger")
                print(f"Invalid Social Category {d[5]} on line {line_no} of UID {d[6]}")
                return redirect("students:students-upload")

            # Here I'm just flipping the key's and values of Student.SOCIAL_CATEGORIES
            _social_categories = []
            for cat in Student.SOCIAL_CATEGORIES:
                _social_categories.append(tuple(sorted(cat, reverse=True)))
            _social_categories = tuple(_social_categories)

            # To get the key from the value :) reverse sense!
            social_cat = dict(_social_categories)[d[5]]

            s = Student(school_code=d[0], student_name=d[1], fathers_name=d[2], mothers_name=d[3], admission_category=d[4],
            social_category=social_cat, uid=d[6], cls=cls, roll=d[8], gender=d[9], dob=d[10], doa=d[11], aadhar_number=d[12], phone_number=d[13])

            # If the student with the same UID already exists, don't add it to the bulk create list...
            if Student.objects.filter(uid=s.uid).exists():
                duplicate_students_list.append(s)
            else:
                students_list.append(s)

        f.close()
        fs.delete(filename)

        Student.objects.bulk_create(students_list)
        line_no += 1
        print(line_no)
        #['school_code','student_name','fathers_name','mothers_name','admission_category',
        #'social_category','uid','cls','roll','gender','dob','doa','aadhar_number','phone_number'])

    context = {
        "students_added": students_list,
        "students_not_added": duplicate_students_list
    }

    dark_mode_cookie = request.COOKIES.get("halfmoon_preferredMode") == "dark-mode"
    if dark_mode_cookie: context['dark_mode'] = 'dark-mode'

    return render(request, 'students_upload.html', context=context)