EXAM_TYPES = (
    ("PT-1", "Periodic Test - 1"),
    ("T-1", "Term - 1 Examination"),
    ("PT-2", "Periodic Test - 2"),
    ("T-2", "Term - 2 Examination"),
)

SUBJECTS = (("ENG", "English"),
                ("HIN", "Hindi"),
                ("SANS", "Sanskrit"),
                ("MATH", "Mathematics"),
                ("EVS", "Environmental Studies"),
                ("SCI", "Science"),
                ("SST", "Social Science"),

                ("PHY", "Physics"),
                ("CHEM", "Chemistry"),
                ("BIO", "Biology"),

                ("CS", "Computer Science"),
                ("PHE", "Physical Education"),
            )

# (Default) Mapping of Classes to Subjects
CLASS_SUBJECTS: "dict[str: 'list[str]']" = {
    "I": ("ENG", "HIN", "MATH", "EVS"),
    "II": ("ENG", "HIN", "MATH", "EVS"),
    "III": ("ENG", "HIN", "MATH", "EVS"),
    "IV": ("ENG", "HIN", "MATH", "EVS"),
    "V": ("ENG", "HIN", "MATH", "EVS"),

    "VI": ("ENG", "HIN", "SANS", "MATH", "SCI", "SST"),
    "VII": ("ENG", "HIN", "SANS", "MATH", "SCI", "SST"),
    "VIII": ("ENG", "HIN", "SANS", "MATH", "SCI", "SST"),

    "IX": ("ENG", "HIN", "SANS", "MATH", "SCI", "SST"),
    "X": ("ENG", "HIN", "SANS", "MATH", "SCI", "SST"),
    "XI": ("ENG", "HIN", "SANS", "CS", "MATH", "PHY", "CHEM", "BIO", "PHE"),
    "XII": ("ENG", "HIN", "SANS", "CS", "MATH", "PHY", "CHEM", "BIO", "PHE"),
}