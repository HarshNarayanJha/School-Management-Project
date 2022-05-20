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

# Teachers
TEACHERS_GROUP_NAME = "Teachers"
TEACHER_USER_DEFAULT_PASSWORD = "123456"
# Mapping of Group to Permissions
# Permissions are searched for using `icontains` lookup, 
# so `mark` will catch all of the add, view, delete, and change perms
GROUPS = {
    TEACHERS_GROUP_NAME: ["view user", 
                          "add exam", "change exam", "view exam", 
                          "mark", "result",
                          "add student", "change student", "view student",
                          "view teacher"],
}