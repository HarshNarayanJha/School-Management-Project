from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from .models import Exam, EXAM_TYPES, Marks, Result, Subject

from students.models import Student, Class
# from students.models import SUBJECTS
from time import time

def home(request: HttpRequest):
    context = {}

    dark_mode_cookie = request.COOKIES.get("halfmoon_preferredMode") == "dark-mode"
    if dark_mode_cookie: context['dark_mode'] = 'dark-mode'

    return render(request, 'exam_home.html', context=context)

def exams(request: HttpRequest):

    def create_paginator(all_exams, page, per_page=10):
        paginator = Paginator(all_exams, per_page)
        try:
            exams = paginator.page(page)
        except PageNotAnInteger:
            exams = paginator.page(1)
        except EmptyPage:
            exams = paginator.page(paginator.num_pages)

        return paginator, exams

    page = request.GET.get('page', 1)
    is_filter = bool(request.GET.get('is_filter', False))

    exams_per_page = int(request.GET.get('exams_per_page', 10))
    exams_filter_name = request.GET.get('exams_filter_name', "").strip()
    exams_filter_session = request.GET.get('exams_filter_session', "").strip()
    exams_filter_cls = request.GET.get('exams_filter_cls', "").strip()

    if (exams_filter_name or exams_filter_session or exams_filter_cls) or (exams_per_page != 10):

        is_filter = True

        if exams_filter_cls:
            all_exams = Exam.objects.all().filter(exam_name__startswith=exams_filter_name, session__icontains=exams_filter_session, cls__cls=exams_filter_cls).order_by('session')
        else:
            all_exams = Exam.objects.all().filter(exam_name__startswith=exams_filter_name, session__icontains=exams_filter_session).order_by('session', 'cls')
    else:
        is_filter = False
        all_exams = Exam.objects.all().order_by('session', 'cls')

    paginator, exams = create_paginator(all_exams, page, exams_per_page)

    pagination_get_parameters = f"&exams_per_page={request.GET.get('exams_per_page', '')}"
    pagination_get_parameters += f"&exams_filter_name={request.GET.get('exams_filter_name', '')}"
    pagination_get_parameters += f"&exams_filter_session={request.GET.get('exams_filter_session', '')}"
    pagination_get_parameters += f"&exams_filter_cls={request.GET.get('exams_filter_cls', '')}"
    pagination_get_parameters += f"&is_filter={bool(request.GET.get('is_filter', False))}"

    context = {
        'exams': exams,
        'exam_types': list(EXAM_TYPES),
        'classes': list(Class.CLASSES),
        'num_all_exams': len(all_exams),
        'num_exams': len(exams),
        'is_filter': is_filter,
        'pagination_get_parameters': pagination_get_parameters,        
    }

    dark_mode_cookie = request.COOKIES.get("halfmoon_preferredMode") == "dark-mode"
    if dark_mode_cookie: context['dark_mode'] = 'dark-mode'

    return render(request, 'exams.html', context=context)

def exam_add(request: HttpRequest):
    # start_time = time()
    if request.method == "POST":
        
        _cls, _cls_created = Class.objects.get_or_create(cls=request.POST.get('cls'))
        new_exam: Exam = Exam.objects.create(exam_name=request.POST.get('exam_name'),
                                            session=request.POST.get('session'),
                                            cls=_cls)

        exam_students = Student.objects.filter(cls=new_exam.cls).order_by('roll')
        results: list[Result] = []
        marks_list: list[list[Marks]] = []

        # TODO: ~takes~ *took* a horibble 20 seconds for class 9th (69 students)
        # But now, I optimised it now it's around 1.5 secs :)
        for student in exam_students:
            # result: Result = new_exam.result_set.create(student=student)
            result: Result = Result(exam=new_exam, student=student)
            _marks = []
            for subject in student.get_subjects_opted():
                mark: Marks = Marks(result=result, subject=subject)
                _marks.append(mark)

            results.append(result)
            marks_list.append(_marks)

        # ex_time1 = time() - start_time
        Result.objects.bulk_create(results)
        results_created = new_exam.result_set.get_queryset()

        # NOTE: Had to reassign the results due to a solid reason
        # Result objects created by bulk_create don't have any pk (but they do, in SQL 3.35+ or something...)
        # as all the objects are created in only one query
        # having pk == None causes Mark creation to fail, giving the error
        # that the related object (Result) is not saved (but it is!)
        for mark_set, result in zip(marks_list, results_created):
            for mark in mark_set:
                mark.result = result

        # ex_time2 = time() - start_time
        # takes the longest amt. of time (around 1.5 secs for 69 students)
        for mark_set in marks_list:
            Marks.objects.bulk_create(mark_set)

        # ex_time3 = time() - start_time

        # print("Exam Creation time Time:", time() - start_time, ex_time1, ex_time2, ex_time3, "for exam id", new_exam.id)
        return redirect('exams:exam-detail', exmid=new_exam.id)

    context = {
        'exam_names': list(EXAM_TYPES) or [],
        'classes': list(Class.CLASSES) or []
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
        'subjects': list(Subject.SUBJECTS)
    }

    dark_mode_cookie = request.COOKIES.get("halfmoon_preferredMode") == "dark-mode"
    if dark_mode_cookie: context['dark_mode'] = 'dark-mode'

    return render(request, 'exam_detail.html', context=context)

def exam_edit(request: HttpRequest, exmid: int):
    exam = Exam.objects.get(pk=exmid)
    exam_students = Student.objects.filter(cls=exam.cls).order_by('roll')

    if request.method == "POST":

        # dict[SUBJECT_NAME, tuple(marks_list (in order of roll), max_marks)]
        subject_marks: dict[str, tuple[list[str], str]] = {}

        for key in request.POST.keys():
            if "mark_ob" in key:
                marks = request.POST.getlist(key)
                sub = key.split("_")[0]
                mark_mx = request.POST.get(f"{sub}_mark_mx")

                subject_marks[sub] = (marks, mark_mx)

        print(subject_marks)

        for sub in subject_marks:
            for stu, mark_ob in zip(exam_students, subject_marks[sub][0]):
                # print(sub, stu, mark_ob, subject_marks[sub][1])

                for result in exam.result_set.get_queryset():
                    if result.student.uid == stu.uid:
                        marks: list[Marks] = result.marks_set.get_queryset()

                        for mark in marks:
                            if mark.subject.subject_name == sub:
                                if mark_ob:
                                    mark.marks_ob = mark_ob
                                # mark.marks_mx = mark_mx

                        result.marks_set.get_queryset().bulk_update(marks, ['marks_ob'])#, 'marks_mx'])

        return redirect('exams:exam-detail', exmid=exmid)

    context = {
        'exam': exam,
        # 'students': exam_students,
        'subjects': list(Subject.SUBJECTS)
    }

    dark_mode_cookie = request.COOKIES.get("halfmoon_preferredMode") == "dark-mode"
    if dark_mode_cookie: context['dark_mode'] = 'dark-mode'

    return render(request, 'exam_edit.html', context=context)