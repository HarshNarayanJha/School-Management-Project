from django.shortcuts import redirect, render
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from django.contrib import messages
from django.urls import reverse

import uuid
import pandas as pd

from .models import Student, Teacher, Class
from exam.models import Subject, CLASS_SUBJECTS

from .utils import get_invalid_value_message, get_create_success_message, get_roll_warning, get_uid_warning,\
                    get_update_success_message, get_birthdays, format_students_data, prepare_dark_mode

def home(request: HttpRequest):

    context = {
        'birthdays': get_birthdays(),
    }

    context = prepare_dark_mode(request, context)
    return render(request, 'students_home.html', context=context)

def debug(request: HttpRequest):
    context = {}

    context = prepare_dark_mode(request, context)
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

def debug_delete_students(request: HttpRequest):
    Student.objects.all().delete()
    return redirect("students:debug")

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

    # Filter Params
    students_per_page = int(request.GET.get('students_per_page', 10) or 10)
    students_filter_name = request.GET.get('students_filter_name', "").strip()
    students_filter_uid = request.GET.get('students_filter_uid', "").strip()
    students_filter_phone = request.GET.get('students_filter_phone', "").strip()
    students_filter_aadhar = request.GET.get('students_filter_aadhar', "").strip()
    students_filter_mother = request.GET.get('students_filter_mother', "").strip()
    students_filter_father = request.GET.get('students_filter_father', "").strip()
    students_filter_cls = request.GET.get('students_filter_cls', "").strip()
    students_filter_section = request.GET.get('students_filter_section', "").strip()
    students_filter_gender = request.GET.get('students_filter_gender', "").strip()

    if (students_filter_name or students_filter_uid or \
        students_filter_phone or students_filter_aadhar or \
        students_filter_mother or students_filter_father or \
        students_filter_cls or students_filter_section or students_filter_gender) or (students_per_page != 10):

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
                                    cls__section__icontains=students_filter_section,
                                    gender__icontains=students_filter_gender).order_by('roll')

        else:
            all_students = Student.objects.all().filter(
                                    student_name__icontains=students_filter_name,
                                    uid__icontains=students_filter_uid,
                                    phone_number__icontains=students_filter_phone,
                                    aadhar_number__icontains=students_filter_aadhar,
                                    mothers_name__icontains=students_filter_mother,
                                    fathers_name__icontains=students_filter_father,
                                    cls__section__icontains=students_filter_section,
                                    gender__icontains=students_filter_gender).order_by('cls', 'cls__section', 'roll')
    else:
        is_filter = False
        all_students = Student.objects.all().order_by('cls', 'roll')

    paginator, students = create_paginator(all_students, page, students_per_page)

    # URI's GET request filter params
    pagination_get_parameters = f"&students_per_page={request.GET.get('students_per_page', '')}"
    pagination_get_parameters += f"&students_filter_name={request.GET.get('students_filter_name', '')}"
    pagination_get_parameters += f"&students_filter_uid={request.GET.get('students_filter_uid', '')}"
    pagination_get_parameters += f"&students_filter_phone={request.GET.get('students_filter_phone', '')}"
    pagination_get_parameters += f"&students_filter_aadhar={request.GET.get('students_filter_aadhar', '')}"
    pagination_get_parameters += f"&students_filter_mother={request.GET.get('students_filter_mother', '')}"
    pagination_get_parameters += f"&students_filter_father={request.GET.get('students_filter_father', '')}"
    pagination_get_parameters += f"&students_filter_cls={request.GET.get('students_filter_cls', '')}"
    pagination_get_parameters += f"&students_filter_section={request.GET.get('students_filter_section', '')}"
    pagination_get_parameters += f"&students_filter_gender={request.GET.get('students_filter_gender', '')}"
    pagination_get_parameters += f"&is_filter={bool(request.GET.get('is_filter', False))}"

    context = {
        'students': students,
        'num_all_students': len(all_students),
        'num_students': len(students),
        'is_filter': is_filter,
        'classes': Class.CLASSES or [],
        'sections': Class.get_classwise_sections(),
        'genders': Student.GENDERS or [],
        'pagination_get_parameters': pagination_get_parameters,
    }

    context = prepare_dark_mode(request, context)
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

    context = prepare_dark_mode(request, context)
    return render(request, 'student_add.html', context=context)

def student_detail(request: HttpRequest, uid: str):

    try:
        stu: Student = Student.objects.get(uid=uid)
    except ObjectDoesNotExist:
        context = {
            'message_404': f'Student with UID <code class="code font-size-18 text-secondary">{uid}</code> was <span class="text-danger">not found</span>!'
        }

        context = prepare_dark_mode(request, context)
        return render(request, '404.html', context=context)

    context = {
        'stu': stu,
        'social_category_display': dict(Student.SOCIAL_CATEGORIES)[stu.social_category],
    }

    context = prepare_dark_mode(request, context)
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

    context = prepare_dark_mode(request, context)
    return render(request, 'student_edit.html', context=context)

def students_upload(request: HttpRequest):
    
    new_students_list: list[Student] = []
    existing_students_list: list[Student] = []

    students_extra_subjects: dict[Student, list[Subject]] = {}
    
    if request.method == 'POST' and request.FILES['students-file-input']:
        uploaded_file = request.FILES['students-file-input']
        fs = FileSystemStorage()
        filename = fs.save(f"{uuid.uuid4()}.csv", uploaded_file)

        data = pd.read_excel(filename)
        data = format_students_data(data)
        dt = data.to_dict("index")

        roll = 0
        last_cls, last_sec = "", ""

        for d in dt.values():
            # print(d)
            extra_subjects = []

            # If it's a normal Class, it's good to go....
            if d['cls'] in dict(Class.CLASSES).values():
                cls, cls_created = Class.objects.get_or_create(cls=d['cls'], section=d['section'])

            # Oh no! those scary-n-weird class names :(
            else:
                # XI - Science with Computer Sc./I.P.
                # XI - Science without Computer Sc./I.P.
                # XII - Commerce with I.P. Electives
                # XII - Commerce without I.P. Electives

                # But easy handling!
                cls_number, subject_part = d['cls'].split(" - ")

                if ' with ' in subject_part:
                    stream, with_subject = subject_part.split(" with ")
                    # Just a Temporary mapping!
                    if with_subject == "Computer Sc./I.P.":
                        with_subject = "CS"
                    elif with_subject == "I.P. Electives":
                        with_subject = "PHE"

                    extra_subjects.append(with_subject)

                elif ' without ' in subject_part:
                    stream, without_subject = subject_part.split(" without ")

                # Create the Class XI and XIIth way!
                cls, cls_created = Class.objects.get_or_create(cls=cls_number, section=d['section'], stream=stream)

            rev_social_catergories = {v: k for k, v in dict(Student.SOCIAL_CATEGORIES).items()}
            social_cat = dict(rev_social_catergories)[d['social_category']]

            rev_minorities = {v: k for k, v in dict(Student.MINORITIES).items()}
            minority = dict(rev_minorities)[d['minority']]

            s = Student()
            for attr, val in d.items():
                if attr == 'cls':
                    setattr(s, attr, cls)
                elif attr == 'social_category':
                    setattr(s, attr, social_cat)
                elif attr == 'minority':
                    setattr(s, attr, minority)
                else:
                    setattr(s, attr, val)

            # Roll No. stuff
            if not last_cls: last_cls = cls.cls
            if not last_sec: last_sec = cls.section

            if cls.cls != last_cls: roll = 1
            elif cls.section != last_sec: roll = 1
            else: roll += 1

            setattr(s, 'roll', roll)
            # TODO: Get School Code perfectly
            setattr(s, 'school_code', '1819')

            extra_subject_objects: list[Subject] = []
            for subject in extra_subjects:
                sub, sub_created = Subject.objects.get_or_create(subject_name=subject)
                extra_subject_objects.append(sub)

            students_extra_subjects[s] = extra_subject_objects

            # If the student with the same UID already exists, don't add it to the bulk create list...
            # we add it to bulk update list
            if Student.objects.filter(uid=s.uid).exists():
                existing_students_list.append(s)
            else:
                new_students_list.append(s)

            last_cls = cls.cls
            last_sec = cls.section

        fs.delete(filename)

        Student.objects.bulk_create(new_students_list)
        for s, subs in students_extra_subjects.items():
            for sub in subs:
                s.extra_subjects_opted.through.objects.get_or_create(student=s, subject=sub)

        Student.objects.bulk_update(existing_students_list, fields=("student_name", "cls", "roll", "phone_number", "email", "aadhar_number"), batch_size=10)

    context = {
        "students_added": new_students_list,
        "students_not_added": existing_students_list
    }

    context = prepare_dark_mode(request, context)
    return render(request, 'students_upload.html', context=context)