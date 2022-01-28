# KV School Management
 Project for school management  (students, exams, results etc...) for Kendriya Vidyalaya using Django in Python

# Usage
You can start using the project by cloning the repo, then installing requirements by running
```
pip install -r requirements.txt
```

After that is done, run
```
python manage.py runserver
```
to run the development sever. Visit [`http://127.0.0.1:8000/`](http://127.0.0.1:8000/) in your browser or click the link in the terminal output to open the website.

# Demo Database
You can use a [demo database](https://github.com/HarshNarayanJha/Python/raw/master/db.sqlite3) that I have been using through development...
It contains some sample students, teachers and Exams set-up.
The superuser login credentials are

```
username: HarshNJ
password: 123456
```

# Apps
This project currently contains two apps
1. `students`
    
    This app manages student and teacher related systems.
    The `Student` model and the `Tecaher` models define database fields for respective roles.
    It also does admin site modification for `Student` model to show student's marks and results for various exam in the student detail page.
2. `exam`
    
    This app contains exam, results, and marks related systems.
    The `Exam` model, which is a `ForeignKey` to `Result` model, which is in turn a `ForeignKey` to `Marks` model.
    This allows each `Exam` to have multiple `Results` (associated with a `Student`) and each `Result` to have multiple `Marks` for each subject.

    ## `Exam` model
    ```python
    class Exam(models.Model):
        name = models.CharField("Exam Name", max_length=50)
        session = models.CharField("Exam Session", max_length=10)
        cls = models.IntegerField("Exam of Class")

        def __str__(self) -> str:
            return f"{self.name} ({self.session}) Class {self.cls}"
    ```
     - name of exam
     - session of the exam
     - class whose exam this is

    Let's say if multiple classes simuleneously have same exam, then the class tecahers of each class have to create a separate exam model instance for their class.
    
    ## `Result` model
    ```python
    class Result(models.Model):
        student = models.ForeignKey(to=Student, on_delete=models.CASCADE)

        exam = models.ForeignKey(to=Exam, null=True, on_delete=models.CASCADE)

        def __str__(self) -> str:
            return f"{self.student.full_name} (Roll: {self.student.roll})"
    ```
     - student whose result this is
     - exam this result is associated with

    When an exam is created and saved, the result inlines are automatically generated for ecah student in that class. Students are also sorted in the order of thier roll no.

    ## `Marks` model
    ```python
    class Marks(models.Model):

        subject = models.CharField("Subject", max_length=20, choices=SUBJECTS)
        marks_ob = models.IntegerField("Marks Obtained")
        marks_mx = models.IntegerField("Maximum Marks")

        result = models.ForeignKey(to=Result, null=True, on_delete=models.CASCADE)

        def __str__(self) -> str:
            return f"{self.subject}: {self.marks_ob} / {self.marks_mx}"
    ```
     - subject whose marks this is
     - marks_obtained
     - maximum_marks
     - result this mark is associated with

    Each result instance can have multiple marks, sutaible for multiple subjects.

I have also used the [django-nested-admin](https://pypi.org/project/django-nested-admin/) library to make nested inlines for marks (as each exam consists of multiple results and each result consists of mutiple marks, but nested inlines aren't natively supported by django) in the admin site.

