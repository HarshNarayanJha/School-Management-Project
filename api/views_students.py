from functools import partial
from django.http import HttpRequest
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from students.models import Student, Class
from students.serializers import StudentSerializer, ClassSerializer

from school_management import settings

# Students API views
@api_view(['GET', 'POST'])
def all_students(request: HttpRequest) -> Response:
    """
    endpoint: `api/v1/students/`\n
    HTTP Methods:\n
        - GET: returns all students
        - POST: creates a new student with POST data (no bulk creation!)
    """
    if request.method == 'GET':
        limit = int(request.GET.get('limit', settings.API_STUDENTS_PER_PAGE))
        offset = int(request.GET.get('offset', 0))

        students = Student.objects.all()[offset:offset + limit] # don't use +1 here for the stop value!
        serializer = StudentSerializer(students, many=True)

        next_path = f"http://{request.get_host()}{request.path}?limit={limit}&offset={offset + limit}"
        prev_path = f"http://{request.get_host()}{request.path}?limit={limit}&offset={offset - limit}"

        data = {}
        data['count'] = students.count()
        data['next'] = next_path if offset + limit < Student.objects.all().count() else None
        data['previous'] = prev_path if offset > 0 else None

        for stu in serializer.data:
            stu['url'] = f"http://{request.get_host()}{request.path}{stu['uid']}" + "/"
            # weird method name ;) ??
            stu.move_to_end('url', last=False)

        data['students'] = serializer.data
        return Response(data)

    if request.method == "POST":
        serializer = StudentSerializer(data=request.data)
        if serializer.is_valid(): 
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def students_bulk(request: HttpRequest) -> Response:
    """
    endpoint: `api/v1/students/bulk/`\n
    HTTP Methods:\n
        - POST: creates `Student` in bulk with passed students POST data list
    """

    if request.method == "POST":
        if not isinstance(request.data, list):
            return Response({'status': 400, 'message': f'expected a list, got a {type(request.data)}'}, status=status.HTTP_400_BAD_REQUEST)

        stu_serializers_ok: list[StudentSerializer] = []
        stu_serializers_errors: list[StudentSerializer] = []

        for student in request.data:
            serializer = StudentSerializer(data=student, bulk=True)
            if serializer.is_valid():
                stu_serializers_ok.append(serializer)
                serializer.save()
            else:
                stu_serializers_errors.append(serializer)

        # NOTE: responses = {
        #   'created': [list of {student data} sucessfully created],
        #   'updated': [list of {student data} sucessfully updated],
        #   'failed': [list of {'uid': the failed student's passed uid or None, 'errors': {'field': error in that field}}]
        # }
        responses = {
            "created:": [stu.data for stu in stu_serializers_ok if not stu.bulk],
            "updated": [stu.data for stu in stu_serializers_ok if stu.bulk],
            "failed": []
        }
        for failed in stu_serializers_errors:
            responses["failed"].append({'uid': failed.data['uid'] if 'uid' in failed.data else None, 'errors': failed.errors})

        return Response(responses, status=status.HTTP_201_CREATED)

@api_view(['GET', 'PATCH'])
def student(request: HttpRequest, uid: str) -> Response:
    """
    endpoint: `api/v1/students/{uid}/`\n
    HTTP Methods:\n
        - GET: returns a `Student` with `uid`
        - PATCH: updates the `Student` with POST data
    """
    try:
        stu = Student.objects.get(uid=uid)
    except ObjectDoesNotExist:
        data = {
            'status': 404,
            'uid': uid,
            'message': f'Student with UID {uid} was not found!',
        }

        return Response(data, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = StudentSerializer(instance=stu)
        return Response(serializer.data)

    if request.method == 'PATCH':
        serializer = StudentSerializer(instance=stu, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_206_PARTIAL_CONTENT)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
# Class
def all_classes(request: HttpRequest) -> Response:
    """
    endpoint: `api/v1/classes/`\n
    HTTP Methods:\n
        - GET: returns all classes
        - POST: creates a new class with POST data
    """
    if request.method == 'GET':
        limit = int(request.GET.get('limit', settings.API_STUDENTS_PER_PAGE))
        offset = int(request.GET.get('offset', 0))

        classes = Class.objects.all()[offset:offset + limit] # don't use +1 here for the stop value!
        serializer = ClassSerializer(classes, many=True)

        next_path = f"http://{request.get_host()}{request.path}?limit={limit}&offset={offset + limit}"
        prev_path = f"http://{request.get_host()}{request.path}?limit={limit}&offset={offset - limit}"

        data = {}
        data['count'] = classes.count()
        data['next'] = next_path if offset + limit < Class.objects.all().count() else None
        data['previous'] = prev_path if offset > 0 else None

        for cls in serializer.data:
            cls['url'] = f"http://{request.get_host()}{request.path}{cls['cls']}" + "/"
            # weird method name ;) ??
            cls.move_to_end('url', last=False)

        data['classes'] = serializer.data
        return Response(data)

    if request.method == "POST":
        serializer = ClassSerializer(data=request.data)
        if serializer.is_valid(): 
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PATCH'])
def class_(request: HttpRequest, cls: str) -> Response:
    """
    endpoint: `api/v1/classes/{cls}/`\n
    HTTP Methods:\n
        - GET: returns an `Class` with `cls`
        - PATCH: updates the `Class` with PATCH data
    """
    try:
        cls_ins = Class.objects.get(cls=cls)
    except ObjectDoesNotExist:
        data = {
            'status': 404,
            'class': cls,
            'message': f'Class {cls} was not found!',
        }

        return Response(data, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ClassSerializer(instance=cls_ins)
        return Response(serializer.data)

    if request.method == "PATCH":
        serializer = ClassSerializer(instance=cls_ins, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
