from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.core.exceptions import ObjectDoesNotExist

from .models import Exam, EXAM_TYPES, Marks, Result

from students.models import SUBJECTS, Student, CLASSES
from time import time

def home(request: HttpRequest):
    context = {}

    dark_mode_cookie = request.COOKIES.get("halfmoon_preferredMode") == "dark-mode"
    if dark_mode_cookie: context['dark_mode'] = 'dark-mode'

    return render(request, 'exam_home.html', context=context)

def exams(request: HttpRequest):
    exam = Exam.objects.all()

    context = {
        'exams': exam,
    }

    dark_mode_cookie = request.COOKIES.get("halfmoon_preferredMode") == "dark-mode"
    if dark_mode_cookie: context['dark_mode'] = 'dark-mode'

    return render(request, 'exams.html', context=context)

def exam_add(request: HttpRequest):
    start_time = time()
    if request.method == "POST":
        
        new_exam: Exam = Exam.objects.create(exam_name=request.POST.get('exam_name'),
                                            session=request.POST.get('session'),
                                            cls=request.POST.get('cls'))

        # TODO: takes a horibble 6 seconds for class 12th
        for student in Student.objects.filter(cls=new_exam.cls).order_by('roll'):
            result: Result = new_exam.result_set.create(student=student)
            for subject, subject_display in SUBJECTS:
                mark: Marks = result.marks_set.create(subject=subject)

        ex_time = time() - start_time
        print("Exam Add Time:", ex_time)
        return redirect('exams:exams')

    context = {
        'exam_names': list(EXAM_TYPES) or [],
        'classes': list(CLASSES) or []
    }

    dark_mode_cookie = request.COOKIES.get("halfmoon_preferredMode") == "dark-mode"
    if dark_mode_cookie: context['dark_mode'] = 'dark-mode'

    return render(request, 'exam_add.html', context=context)

def exam_detail(request: HttpRequest, exmid: int):

    try:
        exam = Exam.objects.get(pk=exmid)
    except ObjectDoesNotExist:
        context = {
            'message_404': f'Exam you are looking for was <span class="text-danger">not found</span>!'
        }
        dark_mode_cookie = request.COOKIES.get("halfmoon_preferredMode") == "dark-mode"
        if dark_mode_cookie: context['dark_mode'] = 'dark-mode'

        return render(request, '404.html', context=context)

    # exam_students = Student.objects.filter(cls=exam.cls)

    context = {
        'exam': exam,
        # 'students': exam_students,
        'subjects': list(SUBJECTS)
    }

    dark_mode_cookie = request.COOKIES.get("halfmoon_preferredMode") == "dark-mode"
    if dark_mode_cookie: context['dark_mode'] = 'dark-mode'

    return render(request, 'exam_detail.html', context=context)

def exam_edit(request: HttpRequest, exmid: int):
    exam = Exam.objects.get(pk=exmid)
    exam_students = Student.objects.filter(cls=exam.cls)

    if request.method == "POST":
        print("\n\n-------------------------------------\n")
        print(request.POST)
        print()
        print(list(request.POST.values()))
        print("\n-------------------------------------\n\n")

        # dict[SUBJECT_CODE, marks_list]
        subject_marks = {}

        for key, value in request.POST.items():
            # print(key, value)
            if "mark" in key:
                sub = key.split("_")[0]

                subject_marks[sub] = value

        # print(subject_marks)

        return redirect('exams:exam-edit', exmid=exmid)

    context = {
        'exam': exam,
        'students': exam_students,
        'subjects': list(SUBJECTS)
    }

    dark_mode_cookie = request.COOKIES.get("halfmoon_preferredMode") == "dark-mode"
    if dark_mode_cookie: context['dark_mode'] = 'dark-mode'

    return render(request, 'exam_edit.html', context=context)