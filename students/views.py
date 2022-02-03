from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.files.storage import FileSystemStorage
import uuid
import csv

from .models import Student, Teacher

def home(request: HttpRequest):
    return render(request, 'students_home.html', context={})

def students(request: HttpRequest):
    all_students = Student.objects.all().order_by('cls', 'roll')
    page = request.GET.get('page', 1)
    paginator = Paginator(all_students, 10)
    try:
        students = paginator.page(page)
    except PageNotAnInteger:
        students = paginator.page(1)
    except EmptyPage:
        students = paginator.page(paginator.num_pages)

    context = {
        'students': students,
    }
    return render(request, 'students.html', context=context)

def students_upload(request: HttpRequest):
    
    if request.method == 'POST' and request.FILES['students-file-input']:
        uploaded_file = request.FILES['students-file-input']
        fs = FileSystemStorage()
        filename = fs.save(str(uuid.uuid4())+".csv", uploaded_file)
        f = open(filename,"r")
        csvreader = csv.reader(f)
        students_list = []
        duplicate_students_list = []

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

    return render(request, 'students_upload.html', context={"students_added": students_list, "students_not_added": duplicate_students_list})