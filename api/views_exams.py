from django.http import HttpRequest
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from exam.models import Exam, Result, Marks
from core.models import Subject
from core.serializers import SubjectSerializer
from exam.serializers import ExamSerializer, ResultSerializer, MarkSerializer

from school_management import settings

# Exams API views
@api_view(['GET', 'POST'])
def all_exams(request: HttpRequest) -> Response:
    """
    endpoint: `api/v1/exams/`\n
    HTTP Methods:\n
        - GET: returns all exams
        - POST: creates a new exam with POST data
    """
    if request.method == 'GET':
        limit = int(request.GET.get('limit', settings.API_STUDENTS_PER_PAGE))
        offset = int(request.GET.get('offset', 0))

        exams = Exam.objects.all()[offset:offset + limit] # don't use +1 here for the stop value!
        serializer = ExamSerializer(exams, many=True)

        next_path = f"http://{request.get_host()}{request.path}?limit={limit}&offset={offset + limit}"
        prev_path = f"http://{request.get_host()}{request.path}?limit={limit}&offset={offset - limit}"

        data = {}
        data['count'] = exams.count()
        data['next'] = next_path if offset + limit < Exam.objects.all().count() else None
        data['previous'] = prev_path if offset > 0 else None

        for exm in serializer.data:
            exm['url'] = f"http://{request.get_host()}{request.path}{exm['id']}" + "/"
            # weird method name ;) ??
            exm.move_to_end('url', last=False)

            del exm['results']

            # for res in exm['results']:
            #     res['url'] = f"http://{request.get_host()}{'/api/v1/results/'}{res['id']}" + "/"
            #     res.move_to_end('url', last=False)

            #     for mrk in res['marks']:
            #         mrk['url'] = f"http://{request.get_host()}{'/api/v1/marks/'}{mrk['id']}" + "/"
            #         mrk.move_to_end('url', last=False)

        data['exams'] = serializer.data
        return Response(data)

    if request.method == "POST":
        serializer = ExamSerializer(data=request.data)
        if serializer.is_valid(): 
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def exam(request: HttpRequest, exmid: str) -> Response:
    """
    endpoint: `api/v1/exams/{exmid}/`\n
    HTTP Methods:\n
        - GET: returns an `Exam` with `exmid`
    """
    try:
        exm = Exam.objects.get(id=exmid)
    except ObjectDoesNotExist:
        data = {
            'status': 404,
            'exmid': exmid,
            'message': f'Exam with id {exmid} was not found!',
        }

        return Response(data, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ExamSerializer(exm)
        for res in serializer.data['results']:
            res['url'] = f"http://{request.get_host()}{'/api/v1/results/'}{res['id']}" + "/"
            res.move_to_end('url', last=False)

            for mrk in res['marks']:
                mrk['url'] = f"http://{request.get_host()}{'/api/v1/marks/'}{mrk['id']}" + "/"
                mrk.move_to_end('url', last=False)
        return Response(serializer.data)

# Result API views
@api_view(['GET', 'POST'])
def all_results(request: HttpRequest) -> Response:
    """
    endpoint: `api/v1/results/`\n
    HTTP Methods:\n
        - GET: returns all results
        - POST: creates a new result with POST data
    """
    if request.method == 'GET':
        limit = int(request.GET.get('limit', settings.API_STUDENTS_PER_PAGE))
        offset = int(request.GET.get('offset', 0))

        results = Result.objects.all()[offset:offset + limit] # don't use +1 here for the stop value!
        serializer = ResultSerializer(results, many=True)

        next_path = f"http://{request.get_host()}{request.path}?limit={limit}&offset={offset + limit}"
        prev_path = f"http://{request.get_host()}{request.path}?limit={limit}&offset={offset - limit}"

        data = {}
        data['count'] = results.count()
        data['next'] = next_path if offset + limit < Result.objects.all().count() else None
        data['previous'] = prev_path if offset > 0 else None

        for res in serializer.data:
            res['url'] = f"http://{request.get_host()}{request.path}{res['id']}" + "/"
            # weird method name ;) ??
            res.move_to_end('url', last=False)

            del res['marks']

            # for mrk in res['marks']:
            #     mrk['url'] = f"http://{request.get_host()}{'/api/v1/marks/'}{res['id']}" + "/"
            #     mrk.move_to_end('url', last=False)

        data['results'] = serializer.data
        return Response(data)

    if request.method == "POST":
        serializer = ResultSerializer(data=request.data)
        if serializer.is_valid(): 
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def result(request: HttpRequest, resid: str) -> Response:
    """
    endpoint: `api/v1/results/{resid}/`\n
    HTTP Methods:\n
        - GET: returns an `Result` with `resid`
    """
    try:
        res = Result.objects.get(id=resid)
    except ObjectDoesNotExist:
        data = {
            'status': 404,
            'resid': resid,
            'message': f'Result with id {resid} was not found!',
        }

        return Response(data, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ResultSerializer(res)
        for mrk in serializer.data['marks']:
                mrk['url'] = f"http://{request.get_host()}{'/api/v1/marks/'}{mrk['id']}" + "/"
                mrk.move_to_end('url', last=False)
        return Response(serializer.data)

# Marks API views
@api_view(['GET', 'POST'])
def all_marks(request: HttpRequest) -> Response:
    """
    endpoint: `api/v1/marks/`\n
    HTTP Methods:\n
        - GET: returns all Marks
        - POST: creates a new Mark with POST data
    """
    if request.method == 'GET':
        limit = int(request.GET.get('limit', settings.API_STUDENTS_PER_PAGE))
        offset = int(request.GET.get('offset', 0))

        marks = Marks.objects.all()[offset:offset + limit] # don't use +1 here for the stop value!
        serializer = MarkSerializer(marks, many=True)

        next_path = f"http://{request.get_host()}{request.path}?limit={limit}&offset={offset + limit}"
        prev_path = f"http://{request.get_host()}{request.path}?limit={limit}&offset={offset - limit}"

        data = {}
        data['count'] = marks.count()
        data['next'] = next_path if offset + limit < Marks.objects.all().count() else None
        data['previous'] = prev_path if offset > 0 else None

        for mrk in serializer.data:
            mrk['url'] = f"http://{request.get_host()}{request.path}{mrk['id']}" + "/"
            # weird method name ;) ??
            mrk.move_to_end('url', last=False)

        data['marks'] = serializer.data
        return Response(data)

    if request.method == "POST":
        serializer = MarkSerializer(data=request.data)
        if serializer.is_valid(): 
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def mark(request: HttpRequest, mrkid: str) -> Response:
    """
    endpoint: `api/v1/marks/{mrkid}/`\n
    HTTP Methods:\n
        - GET: returns an `Mark` with `mrkid`
    """
    try:
        mrk = Marks.objects.get(id=mrkid)
    except ObjectDoesNotExist:
        data = {
            'status': 404,
            'mrkid': mrkid,
            'message': f'Mark with id {mrkid} was not found!',
        }

        return Response(data, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = MarkSerializer(mrk)
        return Response(serializer.data)

# Subjects API views
@api_view(['GET', 'POST'])
def all_subjects(request: HttpRequest) -> Response:
    """
    endpoint: `api/v1/subjects/`\n
    HTTP Methods:\n
        - GET: returns all subjects
        - POST: creates a new subject with POST data
    """
    if request.method == 'GET':
        limit = int(request.GET.get('limit', settings.API_STUDENTS_PER_PAGE))
        offset = int(request.GET.get('offset', 0))

        subjects = Subject.objects.all()[offset:offset + limit] # don't use +1 here for the stop value!
        serializer = SubjectSerializer(subjects, many=True)

        next_path = f"http://{request.get_host()}{request.path}?limit={limit}&offset={offset + limit}"
        prev_path = f"http://{request.get_host()}{request.path}?limit={limit}&offset={offset - limit}"

        data = {}
        data['count'] = subjects.count()
        data['next'] = next_path if offset + limit < Result.objects.all().count() else None
        data['previous'] = prev_path if offset > 0 else None

        for sub in serializer.data:
            sub['url'] = f"http://{request.get_host()}{request.path}{sub['subject_code']}" + "/"
            # weird method name ;) ??
            sub.move_to_end('url', last=False)

        data['subjects'] = serializer.data
        return Response(data)

    if request.method == "POST":
        serializer = SubjectSerializer(data=request.data)
        if serializer.is_valid(): 
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def subject(request: HttpRequest, subname: str) -> Response:
    """
    endpoint: `api/v1/subjects/{subname}/`\n
    HTTP Methods:\n
        - GET: returns an `Subject` with `subname`
    """
    try:
        sub = Subject.objects.get(subject_name=subname)
    except ObjectDoesNotExist:
        data = {
            'status': 404,
            'subname': subname,
            'message': f'Subject with name {subname} was not found!',
        }

        return Response(data, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = SubjectSerializer(sub)
        return Response(serializer.data)