import random
from django.shortcuts import redirect, render
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseForbidden, HttpResponseNotFound, HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from django.contrib import auth
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required, permission_required

import uuid
import pandas as pd

from .models import Student, Teacher, Class
from exam.models import Subject
from exam.constants import SUBJECTS, CLASS_SUBJECTS

from .constants import CLASSES, CLASSES_NUMBER_MAP, SUBJECTS_OPTIONAL_OUT_OF
from .constants import TeacherGroup, ExamAdminGroup

from school_management import settings

from .utils import get_invalid_value_message, get_create_success_message, get_roll_warning, get_uid_warning,\
                    get_update_success_message, get_birthdays, format_students_data, prepare_dark_mode

@login_required
def home(request: HttpRequest):

    context = {
        'birthdays': get_birthdays(),
    }

    context = prepare_dark_mode(request, context)
    return render(request, 'students_home.html', context=context)

def login(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect('students:home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        login_as = request.POST.get('login-as')

        if (login_as == TeacherGroup.LOGIN_NAME):
            teacher = Teacher.objects.filter(user__username=username)
            if not teacher.exists():
                messages.warning(request, f"No Teacher with username {username} was found. Please check that you are logging in with correct Login Type and the username and password are correct.", extra_tags='danger')
                return redirect('students:login')

            user = teacher[0].user
            _user = auth.authenticate(username=username, password=password)
            if not user == _user:
                messages.warning(request, f"The username or the password is incorrect. Try again", extra_tags='danger')
                return redirect('students:login')

            auth.login(request, user, backend=settings.AUTHENTICATION_BACKENDS[0])

        elif (login_as == ExamAdminGroup.LOGIN_NAME):
            # Handle ExamAdmin Login....
            messages.info(request, f"logging in ExamAdmin {username} Not implemented", extra_tags='primary')
        else:
            messages.error(f"Wrong Login As {login_as}", extra_tags='danger')
            return redirect('students:login')

        return redirect('students:home')

    context = {
        'login_as_types': [
            TeacherGroup.LOGIN_NAME,
            ExamAdminGroup.LOGIN_NAME,
        ]
    }

    context = prepare_dark_mode(request, context)
    return render(request, 'auth/login.html', context=context)

@login_required
def logout(request: HttpRequest):
    auth.logout(request)
    return redirect('students:home')

@login_required
def debug(request: HttpRequest):
    context = {}

    context = prepare_dark_mode(request, context)
    return render(request, 'utils/debug.html', context=context)

@login_required
@permission_required('exam.add_subject', raise_exception=True)
def debug_create_subjects(request: HttpRequest):
    subject_objs = []
    for subject in Subject.SUBJECTS:
        if not Subject.objects.filter(subject_name=subject[0]).exists():
            subject_objs.append(Subject(subject_name=subject[0]))

    Subject.objects.bulk_create(subject_objs)

    return redirect('students:debug')

@login_required
@permission_required('students.add_class', raise_exception=True)
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

@login_required
@permission_required('exam.delete_student', raise_exception=True)
def debug_delete_students(request: HttpRequest):
    Student.objects.all().delete()
    return redirect("students:debug")

@login_required
@permission_required('students.view_student', raise_exception=True)
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

    initial_all_students = Student.objects.all()
    if request.user.is_class_teacher():
        initial_all_students = Student.objects.filter(cls__cls=request.user.teacher.teacher_of_class.cls,
                                                        cls__section=request.user.teacher.teacher_of_class.section)

        if (students_filter_cls and students_filter_cls != request.user.teacher.teacher_of_class.cls) \
            or students_filter_section and students_filter_section != request.user.teacher.teacher_of_class.section:

            msg = f"You are not authorised to view the Students of class {students_filter_cls} and section {students_filter_section}"
            return HttpResponseForbidden(msg)

    if (students_filter_name or students_filter_uid or \
        students_filter_phone or students_filter_aadhar or \
        students_filter_mother or students_filter_father or \
        students_filter_cls or students_filter_section or students_filter_gender) or (students_per_page != 10):

        is_filter = True

        if students_filter_cls:
            all_students = initial_all_students.filter(
                                    student_name__icontains=students_filter_name,
                                    uid__icontains=students_filter_uid,
                                    phone_number__icontains=students_filter_phone,
                                    aadhar_number__icontains=students_filter_aadhar,
                                    mothers_name__icontains=students_filter_mother,
                                    fathers_name__icontains=students_filter_father,
                                    cls__cls=students_filter_cls,
                                    cls__section__icontains=students_filter_section,
                                    gender__icontains=students_filter_gender)

        else:
            all_students = initial_all_students.filter(
                                    student_name__icontains=students_filter_name,
                                    uid__icontains=students_filter_uid,
                                    phone_number__icontains=students_filter_phone,
                                    aadhar_number__icontains=students_filter_aadhar,
                                    mothers_name__icontains=students_filter_mother,
                                    fathers_name__icontains=students_filter_father,
                                    cls__section__icontains=students_filter_section,
                                    gender__icontains=students_filter_gender)
    else:
        is_filter = False
        all_students = initial_all_students

    paginator, students = create_paginator(all_students, page, students_per_page)

    # URI's GET request filter params
    pagination_get_parameters = f"&students_per_page={request.GET.get('students_per_page', '')}"
    pagination_get_parameters += f"&students_filter_name={request.GET.get('students_filter_name', '')}"
    pagination_get_parameters += f"&students_filter_uid={request.GET.get('students_filter_uid', '')}"
    pagination_get_parameters += f"&students_filter_phone={request.GET.get('students_filter_phone', '')}"
    pagination_get_parameters += f"&students_filter_aadhar={request.GET.get('students_filter_aadhar', '')}"
    pagination_get_parameters += f"&students_filter_mother={request.GET.get('students_filter_mother', '')}"
    pagination_get_parameters += f"&students_filter_father={request.GET.get('students_filter_father', '')}"
    if not request.user.is_class_teacher:
        pagination_get_parameters += f"&students_filter_cls={request.GET.get('students_filter_cls', '')}"
        pagination_get_parameters += f"&students_filter_section={request.GET.get('students_filter_section', '')}"
    pagination_get_parameters += f"&students_filter_gender={request.GET.get('students_filter_gender', '')}"
    pagination_get_parameters += f"&is_filter={bool(request.GET.get('is_filter', False))}"

    context = {
        'students': students,
        'num_all_students': len(all_students),
        'num_students': len(students),
        'is_filter': is_filter,
        'classes': CLASSES or [],
        'sections': Class.get_classwise_sections(),
        'genders': Student.GENDERS or [],
        'pagination_get_parameters': pagination_get_parameters,
    }

    context = prepare_dark_mode(request, context)
    return render(request, 'students.html', context=context)

@login_required
@permission_required('students.add_student', raise_exception=True)
def student_add(request: HttpRequest):

    if request.method == "POST":
        _cls, _cls_created = Class.objects.get_or_create(cls=request.POST.get('cls'), section=request.POST.get('section'))
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
        'classes': Class.get_classwise_sections()
    }

    context = prepare_dark_mode(request, context)
    return render(request, 'student_add.html', context=context)

@login_required
@permission_required('students.view_student', raise_exception=True)
def student_detail(request: HttpRequest, uid: str):

    try:
        stu: Student = Student.objects.get(uid=uid)
        if request.user.is_class_teacher():
            if stu.cls != request.user.teacher.teacher_of_class:
                return HttpResponseForbidden("This student is not of your class")
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

@login_required
@permission_required('students.change_student', raise_exception=True)
def student_edit(request: HttpRequest, uid: str):
    stu: Student = Student.objects.get(uid=uid)

    if request.method == "POST":
        _cls = Class.objects.get(cls=request.POST.get('cls'), section=request.POST.get('section'))
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
        'classes': Class.get_classwise_sections()
    }

    context = prepare_dark_mode(request, context)
    return render(request, 'student_edit.html', context=context)

@login_required
@permission_required('students.add_student', raise_exception=True)
def students_upload(request: HttpRequest):
    
    new_students_list: list[Student] = []
    existing_students_list: list[Student] = []

    students_optional_subjects: dict[Student, list[Subject]] = {}
    
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
            optional_subjects = []

            # If it's a normal Class, it's good to go....
            if d['cls'] in dict(CLASSES).values():
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

                    optional_subjects.append(with_subject)

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

            optional_subject_objects: list[Subject] = []
            if cls.cls in SUBJECTS_OPTIONAL_OUT_OF:
                for opts in SUBJECTS_OPTIONAL_OUT_OF[cls.cls]:
                    optional_subjects.append(random.choice(opts))
            
            optional_subjects = list(set(optional_subjects))

            for subject in optional_subjects:
                sub, sub_created = Subject.objects.get_or_create(subject_name=subject)
                optional_subject_objects.append(sub)

            students_optional_subjects[s] = optional_subject_objects

            # If the student with the same UID already exists, don't add it to the bulk create list...
            # we add it to bulk update list
            if Student.objects.filter(uid=s.uid).exists():
                existing_students_list.append(s)
            else:
                new_students_list.append(s)

            last_cls = cls.cls
            last_sec = cls.section

            # print(roll, last_cls, last_sec)

        fs.delete(filename)

        Student.objects.bulk_create(new_students_list)
        for s, subs in students_optional_subjects.items():
            for sub in subs:
                s.optional_subjects_opted.through.objects.get_or_create(student=s, subject=sub)

        # TODO: fix bulk update
        # Student.objects.bulk_update(existing_students_list, fields=("student_name", "cls", "roll", "phone_number", "email", "aadhar_number"), batch_size=10)

    context = {
        "students_added": new_students_list,
        "students_not_added": existing_students_list
    }

    context = prepare_dark_mode(request, context)
    return render(request, 'students_upload.html', context=context)

# Teachers Area! No Student allowed!
def teachers(request: HttpRequest):
    pass

@login_required
@permission_required('students.add_teacher', raise_exception=True)
def teacher_add(request: HttpRequest):

    if request.method == "POST":
        print(request.POST)
        teacher_name = request.POST.get('teachers_name')
        username = request.POST.get('username')
        # password = request.POST.get('password')
        # password_rep = request.POST.get('password_repeat')
        salary = request.POST.get('salary')
        subject = request.POST.get('subject')

        is_class_teacher, cls = False, None
        if request.POST.get('class_teacher_of'):
            is_class_teacher = True
            _cls, _section = request.POST.get('class_teacher_of').split("-")
            cls, cls_created = Class.objects.get_or_create(cls=_cls, section=_section)
            same_cls_teacher = Teacher.objects.filter(teacher_of_class=cls)

        same_username = Teacher.objects.filter(user__username=username)

        if same_username.exists():
            # Sorry teacher, you have to pick another username...
            messages.warning(request, f"Username {username} already used! Pick another username.", extra_tags='danger')
            return redirect('students:teacher-add')

        if is_class_teacher:
            if same_cls_teacher.count() > 0:
                # One Class(and section) may have only 1 (or 2 ???) Class Teachers....
                messages.warning(request, f"Class Teacher of class {request.POST.get('cls_teacher_of')} already exists ({cls.class_teacher})", extra_tags="danger")
                return redirect('students:teacher-add')

        new_teacher: Teacher = Teacher.objects.create(
                                teacher_name=teacher_name,
                                user_name=username,
                                salary=salary,
                                subject=Subject.objects.get(subject_name=subject),
                                teacher_of_class=cls
                            )

        messages.success(request, f"Teacher {new_teacher} successfully created", extra_tags='success')
        return redirect("students:home")

    context = {
        'genders': list(Student.GENDERS),
        'admission_categories': list(Student.ADMISSION_CATEGORIES),
        'social_categories': list(Student.SOCIAL_CATEGORIES),
        'subjects': SUBJECTS,
        'classes': Class.get_classwise_sections()
    }

    context = prepare_dark_mode(request, context)
    return render(request, 'teachers/teacher_add.html', context=context)

def teacher_detail(request: HttpRequest):
    pass

def teacher_edit(request: HttpRequest):
    pass