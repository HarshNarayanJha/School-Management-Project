from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect, render
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages

from core.models import Class
from core.constants import CLASSES
from .models import Exam, Marks, Result
from students.models import Student
from students.utils import prepare_dark_mode
from .constants import EXAM_TYPES
from core.constants import SUBJECTS

@login_required
def home(request: HttpRequest):
    context = {}
    context = prepare_dark_mode(request, context)
    return render(request, 'exam_home.html', context=context)

@login_required
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

    # Filter Params
    exams_per_page = int(request.GET.get('exams_per_page', 10))
    exams_filter_name = request.GET.get('exams_filter_name', "").strip()
    exams_filter_session = request.GET.get('exams_filter_session', "").strip()
    exams_filter_cls = request.GET.get('exams_filter_cls', "").strip()
    exams_filter_section = request.GET.get('exams_filter_section', "").strip()

    initial_all_exams = Exam.objects.all()
    if request.user.get_school():
        initial_all_exams = initial_all_exams.filter(cls__school=request.user.get_school())

    if request.user.is_class_teacher():
        initial_all_exams = Exam.objects.filter(cls=request.user.teacher.teacher_of_class)

        if (exams_filter_cls and exams_filter_cls != request.user.teacher.teacher_of_class.cls) \
            or exams_filter_section and exams_filter_section != request.user.teacher.teacher_of_class.section:

            msg = f"You are not authorised to view the Exams of class {exams_filter_cls} and section {exams_filter_section}"
            return HttpResponseForbidden(msg)

    if (exams_filter_name or exams_filter_session or \
                exams_filter_cls or exams_filter_section) or (exams_per_page != 10):

        is_filter = True

        if exams_filter_cls:
            all_exams = initial_all_exams.filter(
                                exam_name__icontains=exams_filter_name,
                                session__icontains=exams_filter_session,
                                cls__cls=exams_filter_cls,
                                cls__section__icontains=exams_filter_section)
        else:
            all_exams = initial_all_exams.filter(
                                exam_name__startswith=exams_filter_name,
                                session__icontains=exams_filter_session)
    else:
        is_filter = False
        all_exams = initial_all_exams

    paginator, page_exams = create_paginator(all_exams, page, exams_per_page)

    # URI's GET request filter params
    pagination_get_parameters = f"&exams_per_page={request.GET.get('exams_per_page', '')}"
    pagination_get_parameters += f"&exams_filter_name={request.GET.get('exams_filter_name', '')}"
    pagination_get_parameters += f"&exams_filter_session={request.GET.get('exams_filter_session', '')}"
    if not request.user.is_class_teacher:
        pagination_get_parameters += f"&exams_filter_cls={request.GET.get('exams_filter_cls', '')}"
        pagination_get_parameters += f"&exams_filter_section={request.GET.get('exams_filter_section', '')}"
    pagination_get_parameters += f"&is_filter={bool(request.GET.get('is_filter', False))}"

    if request.user.get_school():
        classes = Class.get_schoolwise_classes_sections([request.user.get_school().school_code])
    elif request.user.is_superuser:
        classes = Class.get_schoolwise_classes_sections(None)
    else:
        raise Exception("User hasn't any school and is not super user!")

    context = {
        'exams': page_exams,
        'exam_types': list(EXAM_TYPES),
        'classes': classes,
        'num_all_exams': len(all_exams),
        'num_exams': len(page_exams),
        'is_filter': is_filter,
        'pagination_get_parameters': pagination_get_parameters,        
    }

    context = prepare_dark_mode(request, context)
    return render(request, 'exams.html', context=context)

@login_required
@permission_required('exam.add_exam', raise_exception=True)
def exam_add(request: HttpRequest):

    if request.method == "POST":
        _cls: Class = Class.objects.get(cls=request.POST.get('cls'), section=request.POST.get('section'), school=request.user.get_school())
        if request.user.is_class_teacher():
            if request.user.teacher.teacher_of_class != _cls:
                return HttpResponseForbidden(f"You are not authorized to create Exam for class {_cls}")

        new_exam: Exam = Exam.objects.create(exam_name=request.POST.get('exam_name'),
                                            session=request.POST.get('session'),
                                            cls=_cls)

        exam_students = Student.objects.filter(cls=new_exam.cls).order_by('roll')
        results: list[Result] = []
        marks_list: list[list[Marks]] = []

        # DID: ~takes~ *took* a horibble 20 seconds for class 9th (69 students)
        # But now, I optimised it now it's around 1.5 secs :)
        # But still heavy!
        # return redirect("exam:exam-add")
        for student in exam_students:
            result: Result = Result(exam=new_exam, student=student)
            _marks = []
            for subject in _cls.cls_subjects.all():
                mark: Marks = Marks(result=result, subject=subject)
                _marks.append(mark)

            results.append(result)
            marks_list.append(_marks)

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

        # takes the longest amt. of time (around 1.5 secs for 69 students)
        for mark_set in marks_list:
            Marks.objects.bulk_create(mark_set)

        return redirect('exams:exam-edit', exmid=new_exam.id)

    context = {
        'exam_names': list(EXAM_TYPES) or [],
        'classes': Class.get_schoolwise_classes_sections([request.user.get_school()]),
    }

    context = prepare_dark_mode(request, context)

    return render(request, 'exam_add.html', context=context)

@login_required
@permission_required('exam.view_exam', raise_exception=True)
def exam_detail(request: HttpRequest, exmid: int):
    try:
        exam: Exam = Exam.objects.get(pk=exmid)
        if request.user.get_school():
            if request.user.get_school() != exam.cls.school:
                return HttpResponseForbidden(f"You are not authorized to view Exam for school {exam.cls.school}")

        if request.user.is_class_teacher():
            if request.user.teacher.teacher_of_class != exam.cls:
                return HttpResponseForbidden(f"You are not authorized to view Exam for class {exam.cls}")

    except ObjectDoesNotExist:
        context = {
            'message_404': f'Exam you are looking for was <span class="text-danger">not found</span>!'
        }
        dark_mode_cookie = request.COOKIES.get("halfmoon_preferredMode") == "dark-mode"
        if dark_mode_cookie: context['dark_mode'] = 'dark-mode'

        return render(request, '404.html', context=context)

    context = {
        'exam': exam,
        'subjects': list(SUBJECTS)
    }

    context = prepare_dark_mode(request, context)
    return render(request, 'exam_detail.html', context=context)

@login_required
@permission_required('exam.change_exam', raise_exception=True)
@permission_required('exam.change_result', raise_exception=True)
@permission_required('exam.change_marks', raise_exception=True)
def exam_edit(request: HttpRequest, exmid: int):
    exam: Exam = Exam.objects.get(pk=exmid)

    if request.user.get_school():
        if exam.cls.school != request.user.get_school():
            return HttpResponseForbidden(f"You are not authorized to edit Exam for school {exam.cls.school}")

    if request.user.is_class_teacher():
        if exam.edited_by_class_teacher:
            messages.error(request, f"Dear {request.user.teacher.teacher_name}, you have already edited the exam once. Class Teachers can edit exam only once.", extra_tags='danger')
            return redirect('exam:exam-detail', exmid=exmid)

        if request.user.teacher.teacher_of_class != exam.cls:
            return HttpResponseForbidden(f"You are not authorized to create Exam for class {exam.cls}")

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

        # print(subject_marks)

        # TODO: Takes too much time!
        for sub in subject_marks:
            for stu, mark_ob in zip(exam_students, subject_marks[sub][0]):
                # print(sub, stu, mark_ob, subject_marks[sub][1])

                for result in exam.result_set.get_queryset():
                    if result.student.uid == stu.uid:
                        marks: list[Marks] = result.marks_set.get_queryset()

                        for mark in marks:
                            if mark.subject.subject_name == sub:
                                mark.marks_ob = mark_ob or None
                                # mark.marks_mx = mark_mx

                        result.marks_set.get_queryset().bulk_update(marks, ['marks_ob'])#, 'marks_mx'])

        if request.user.is_class_teacher():
            exam.edited_by_class_teacher = True
            exam.save()
        return redirect('exams:exam-detail', exmid=exmid)

    context = {
        'exam': exam,
        'subjects': list(SUBJECTS)
    }

    context = prepare_dark_mode(request, context)
    return render(request, 'exam_edit.html', context=context)