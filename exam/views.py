from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
import uuid
import csv
from students.models import Student
# Create your views here.

def home(request: HttpRequest):
    return render(request, 'exam_home.html', context={})

def studentUpload(request: HttpRequest):
    if request.method == 'POST' and request.FILES['file']:  
        myfile = request.FILES['file']
        fs = FileSystemStorage()
        filename = fs.save(str(uuid.uuid4())+".csv", myfile)
        f = open(filename,"r")
        csvreader = csv.reader(f)
        students_list = []
        #skip header
        next(csvreader)
        for d in csvreader:
            s = Student(school_code=d[0],student_name=d[1],fathers_name=d[2],mothers_name=d[3],admission_category=d[4],
            social_category=d[5],uid=d[6],cls=d[7],roll=d[8],gender=d[9],dob=d[10],doa=d[11],aadhar_number=d[12],phone_number=d[13])
            students_list.append(s)
        f.close()
        fs.delete(filename)
        Student.objects.bulk_create(students_list)
        #['school_code','student_name','fathers_name','mothers_name','admission_category',
        #'social_category','uid','cls','roll','gender','dob','doa','aadhar_number','phone_number'])
    return render(request, 'students_upload.html', context={"data":students_list})