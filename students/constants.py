# Class
CLASSES = (
            ("I","I"),("II","II"),("III","III"),("IV","IV"),("V","V"),("VI","VI"),("VII","VII"),
            ("VIII","VIII"),("IX","IX"),("X","X"),("XI","XI"),("XII","XII")
        )

CLASSES_NUMBER_MAP = {
    "I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7, "VIII": 8,
    "IX": 9, "X": 10, 'XI': 11, "XII": 12,
}

# Subjects
# mapping of Class with collection of different subject options
# classwise subject options
SUBJECTS_OPTIONAL_OUT_OF: "dict[str, tuple[tuple[str]]]" = {
    'IX': (("HIN", "SANS"),),
    'X': (("HIN", "SANS"),),
    'XI': (("HIN", "SANS", "CS"), ("MATH", "BIO"),),
    'XII': (("HIN", "SANS", "CS"), ("MATH", "BIO"),),
}

##################################
# Various User Groups

class ExamAdminGroup:
    LOGIN_NAME = "Exam Admin"
    GROUP_NAME = "Exam Admins"
    PASSWORD = "123456"

    def __str__(self) -> str:
        return self.GROUP_NAME

class TeacherGroup:
    LOGIN_NAME = "Teacher"
    GROUP_NAME = "Teachers"
    PASSWORD = "123456"

    def __str__(self) -> str:
        return self.GROUP_NAME

# Mapping of Group to Permissions
# Permissions are in form <app_name>.{add,change,view,delete}_<model_name>
GROUPS = {
    ExamAdminGroup.GROUP_NAME: [
        "students.add_student",
        "students.change_student",
        "students.view_student",
        "students.delete_student",

        "students.add_teacher",
        "students.view_teacher",

        "exam.add_exam",
        "exam.change_exam",
        "exam.view_exam",
        "exam.delete_exam",

        "exam.add_result",
        "exam.change_result",
        "exam.view_result",
        "exam.delete_result",

        "exam.add_marks",
        "exam.change_marks",
        "exam.view_marks",
        "exam.delete_marks",
    ],
    TeacherGroup.GROUP_NAME: [
        "students.view_student",
        "students.view_teacher",

        "exam.add_exam",
        "exam.change_exam",
        "exam.view_exam",

        "exam.add_result",
        "exam.change_result",
        "exam.view_result",

        "exam.add_marks",
        "exam.change_marks",
        "exam.view_marks",
    ],
}