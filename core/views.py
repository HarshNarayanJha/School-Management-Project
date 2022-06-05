from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.contrib import auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required

from .constants import CLASSES, SUBJECTS, TeacherGroup, CLASS_SUBJECTS, ExamAdminGroup
from .models import ExamAdmin, Subject, Teacher, Class

from school_management import settings
from students.utils import get_birthdays, prepare_dark_mode

@login_required
def home(request: HttpRequest):

    context = {}

    context = prepare_dark_mode(request, context)
    return render(request, 'home.html', context=context)

def login(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        login_as = request.POST.get('login-as')

        if (login_as == TeacherGroup.LOGIN_NAME):
            teacher = Teacher.objects.filter(user__username=username)
            if not teacher.exists():
                messages.warning(request, f"No Teacher with username {username} was found. Please check that you are logging in with correct Login Type and the username and password are correct.", extra_tags='danger')
                return redirect('core:login')

            user = teacher[0].user
            _user = auth.authenticate(username=username, password=password)
            print(user, _user)
            if not user == _user:
                messages.warning(request, f"The username or the password is incorrect. Try again", extra_tags='danger')
                return redirect('core:login')

            auth.login(request, user, backend=settings.AUTHENTICATION_BACKENDS[0])

        elif (login_as == ExamAdminGroup.LOGIN_NAME):
            # Handle ExamAdmin Login....
            exam_admin = ExamAdmin.objects.filter(user__username=username)
            if not exam_admin.exists():
                messages.warning(request, f"No ExamAdmin with username {username} was found. Please check that you are logging in with correct Login Type and the username and password are correct.", extra_tags='danger')
                return redirect('core:login')

            user = exam_admin[0].user
            _user = auth.authenticate(username=username, password=password)
            if not user == _user:
                messages.warning(request, f"The username or the password is incorrect. Try again", extra_tags='danger')
                return redirect('core:login')

            auth.login(request, user, backend=settings.AUTHENTICATION_BACKENDS[0])
        else:
            messages.error(f"Wrong Login As {login_as}", extra_tags='danger')
            return redirect('core:login')

        return redirect('core:home')

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
    return redirect('core:home')

@login_required
def debug(request: HttpRequest):
    context = {}

    context = prepare_dark_mode(request, context)
    return render(request, 'utils/debug.html', context=context)

@login_required
@permission_required('core.add_subject', raise_exception=True)
def debug_create_subjects(request: HttpRequest):
    subject_objs = []
    for subject in SUBJECTS:
        if not Subject.objects.filter(subject_name=subject[0]).exists():
            subject_objs.append(Subject(subject_name=subject[0]))

    Subject.objects.bulk_create(subject_objs)

    return redirect('core:debug')

@login_required
@permission_required('core.add_class', raise_exception=True)
def debug_create_classes(request: HttpRequest):
    cls_objs = []
    for cls in CLASSES:
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
    
    return redirect('core:debug')

@permission_required('core.view_teacher', raise_exception=True)
def teachers(request: HttpRequest):
    all_teachers = Teacher.objects.all()

    context = {
        'teachers': all_teachers,
    }

    context = prepare_dark_mode(request, context)
    return render(request, 'teachers/teachers.html', context=context)

@login_required
@permission_required('core.add_teacher', raise_exception=True)
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
            return redirect('core:teacher-add')

        if is_class_teacher:
            if same_cls_teacher.count() > 0:
                # One Class(and section) may have only 1 (or 2 ???) Class Teachers....
                messages.warning(request, f"Class Teacher of class {request.POST.get('cls_teacher_of')} already exists ({cls.class_teacher})", extra_tags="danger")
                return redirect('core:teacher-add')

        new_teacher: Teacher = Teacher.objects.create(
                                teacher_name=teacher_name,
                                user_name=username,
                                salary=salary,
                                subject=Subject.objects.get(subject_name=subject),
                                teacher_of_class=cls
                            )

        messages.success(request, f"Teacher {new_teacher} successfully created", extra_tags='success')
        return redirect("core:home")

    context = {
        'subjects': dict(SUBJECTS),
        'classes': Class.get_classwise_sections()
    }

    context = prepare_dark_mode(request, context)
    return render(request, 'teachers/teacher_add.html', context=context)

def teacher_detail(request: HttpRequest, tid: int):
    pass

def teacher_edit(request: HttpRequest, tid: int):
    pass
