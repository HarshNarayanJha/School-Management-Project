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

<!-- # Demo Database
You can use a [demo database](https://github.com/HarshNarayanJha/Python/raw/master/db.sqlite3) that I have been using through development...
It contains some sample students, teachers and Exams set-up.
The superuser login credentials are

```
username: HarshNJ
password: 123456
``` -->

# Apps
This project currently contains 3 apps
1. `students`
    
    This app manages student and teacher related systems.
    The `Student` model and the `Teacher` models define database fields for respective roles.
    It also does admin site modification for `Student` model to show student's marks and results for various exam in the student detail page using inline admin.
    It also defines the `Class` model

    ## `Class` model
    ```python
    class Class(models.Model):
        cls = models.CharField(verbose_name="Class", max_length=4, blank=False, null=False, choices=CLASSES)
        section = models.CharField(verbose_name="Section", max_length=1, blank=True, null=True)
        cls_subjects = models.ManyToManyField(to='exam.Subject', verbose_name="Subjects of the Class")
        stream = models.CharField("Stream", max_length=10, null=True, blank=True)
    ```
     - the class text (I, II, ..., XI, XII)
     - the section (A, B, C, ...)
     - NOTE: let's say class 12th has three sections, A, B, and C, then there will be 3 instances of `Class`, each having `cls` as "XII" but different sections (A, B, and C)
     - the `stream` of the class, if > 11th (XI)
2. `exam`
    
    This app contains exam related systems such as exam, results, marks and subjects.
    The `Exam` model, which is a `ForeignKey` to `Result` model, which is in turn a `ForeignKey` to `Marks` model.
    This allows each `Exam` to have multiple `Results` (associated with a `Student`) and each `Result` to have multiple `Marks` for each subject.

    ## `Exam` model
    ```python
    class Exam(models.Model):
        exam_name = models.CharField("Exam Name", max_length=50, choices=EXAM_TYPES)
        session_regex = RegexValidator(r'^20\d{2}-20\d{2}$', "should be in the format 20XX-20XX")
        session = models.CharField("Exam Session", max_length=10, validators=[session_regex])
        cls = models.ForeignKey(to=Class, verbose_name="Class", on_delete=models.CASCADE, blank=False, null=False)
        edited_by_class_teacher = models.BooleanField("Edited by Class Teacher", default=False, editable=False)
    ```
     - name of exam (choices)
     - session of the exam
     - class whose exam this is (see `Class`)
     - a bool `edited_by_class_teacher` which is set to `True` once the class teachers fills in the marks, which then disallows the class teacher to re-edit the marks, thus locking the entry.
    
    ## `Result` model
    ```python
    class Result(models.Model):
        exam = models.ForeignKey(to=Exam, null=True, on_delete=models.CASCADE)
        student = models.ForeignKey(to=Student, on_delete=models.CASCADE)
    ```
     - student whose result this is
     - exam this result is associated with

    When an exam is created and saved, the result inlines are automatically generated for each student in the class of the exam.

    ## `Marks` model
    ```python
    class Marks(models.Model):
        subject = models.ForeignKey(to="Subject", verbose_name="Subject", on_delete=models.CASCADE)
        marks_ob = models.IntegerField("Marks Obtained", null=True, blank=True)
        result = models.ForeignKey(to=Result, null=True, on_delete=models.CASCADE)
    ```
     - subject whose marks this is
     - marks_obtained
     - result this mark is associated with

    ## `Subject` model
    ```python
    class Subject(models.Model):
        subject_name = models.CharField(max_length=20, blank=False, null=False, choices=SUBJECTS, unique=True)

    ```

    Each result instance can have multiple marks, sutaible for multiple subjects. But it's worth noting the only those subject marks are generated with exam which subjects are in that class (the exam's class). Also, the subjects which a student hasn't opted for, are grayed out (readonly, not disabled, otherwise the fields won't be POSTED!)

    It also defines the `ExamAdmin` class

    ## `ExamAdmin` model
    ```python
    class ExamAdmin(models.Model):
        admin_name = models.CharField("Exam Admin's Name", max_length=30, null=False)
        user_name = models.CharField("User Name", max_length=150, unique=True)
        user = models.OneToOneField(to=User, on_delete=models.CASCADE, editable=False, null=True)
    ```

    `ExamAdmin` is a special user type who can re-edit any exam, and can control the various parts of exam system.

3. `api`

    This is the app that implements the API interface of the various models. Each app implements a `serializers.py` for each representable model. It contains the Serializer definitions for the models to convert them to APIs.