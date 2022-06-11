import random
import numpy as np
import pandas as pd
from pandas.api.types import CategoricalDtype

from core.constants import CLASSES_NUMBER_MAP
"""
Some utility functions with multiple usages
"""

import datetime
from students.models import Student
from core.models import Class

def get_invalid_value_message(value_name: str, value: str, line_no: int, uid: str, expected_vals: "list[str]") -> str:
    """
    Returns the formatted message template for invalid value while parsing students data!
    """
    msg = f"Invalid {value_name} <span class=\"font-weight-bold\">{value}</span>\
            on line <span class=\"text-primary\">{line_no}</span>\
            of UID <span class=\"text-secondary\">{uid}</span>.\
            Should be one of {expected_vals}"
    return msg

def get_uid_warning(uid: str) -> str:
    """
    Returns the templated message for the warning of existing `UID`,
    while creating a `Student`
    """
    uid_href = f"/students/{uid}/#:~:text={uid}"

    msg = f"Student with UID <a class=\"alert-link text-secondary font-weight-medium text-decoration-none\"\
            href=\"{uid_href}\" target=\"_blank\">{uid}</a> already exists.. maybe you mistyped!"
    return msg

def get_roll_warning(roll: str, uid: str, cls: str) -> str:
    """
    Returns the templated message for the warning for duplicate `Roll No.` in the same `Class`,
    while creating a `Student`
    """
    roll_href = f"/students/{uid}/#:~:text={uid}"

    msg = f"A student bearing Roll No. <a class=\"alert-link text-secondary font-weight-medium text-decoration-none\"\
            href=\"{roll_href}\" target=\"_blank\">{roll}</a> already exists\
            in the Class <span class=\"text-primary font-weight-medium\">{cls}</span>. maybe you mistyped!"

    return msg

def get_create_success_message(name: str, uid: str) -> str:
    """
    Returns the templated message for successfully creating a `Student`
    """
    msg = f"Student <span class=\"text-primary font-weight-medium\">{name}</span> with\
            UID <span class=\"text-secondary font-weight-medium\">{uid}</span>\
            was successfully created."

    return msg

def get_update_success_message(name: str) -> str:
    """
    Returns the templated message for successfully creating a `Student`
    """
    msg = f"Student <span class=\"text-primary font-weight-medium\">{name}</span>\
            was successfully updated."

    return msg

def get_birthdays() -> "list[Student]":
    """
    Returns the list of all students who have their Birthday today
    """
    today = datetime.date.today()
    birthdays: list[Student] = Student.objects.filter(dob__day=today.day, dob__month=today.month)
    return birthdays

def prepare_dark_mode(request, context: dict) -> dict:
    """
    Takes the request and its context as parameter and modifies it for the dark mode setting
    and returns it
    """
    dark_mode_cookie = request.COOKIES.get("halfmoon_preferredMode") == "dark-mode"
    if dark_mode_cookie: context['dark_mode'] = 'dark-mode'

    return context

def format_students_data(data: pd.DataFrame) -> pd.DataFrame:
    """
    Author: Abjijeet Sir

    Formats the Students Excel file obtained from the UBI portal
    """
    COLUMNS_TO_DROP = ["Unnamed: 0", "Unnamed: 2", "Unnamed: 7", "Unnamed: 9", "Unnamed: 13",
                        "Unnamed: 26", "Unnamed: 27", "Unnamed: 30"]
    COLUMN_RENAME_MAP = {
        "Unnamed: 1": "SN", "Unnamed: 3": "Student_Code", "Unnamed: 4": "Admission_Year",
        "Unnamed: 5": "Admn_No", "Unnamed: 6": "Student_Name", "Unnamed: 8": "Class",
        "Unnamed: 10": "Section", "Unnamed: 11": "Fathers_Name", "Unnamed: 12": "Mothers_Name",
        "Unnamed: 14": "Gender", "Unnamed: 15": "DOB", "Unnamed: 16": "Admn_Category",
        "Unnamed: 17": "Category", "Unnamed: 18": "Minority", "Unnamed: 19": "Mobile_No",
        "Unnamed: 20": "Email_ID", "Unnamed: 21": "Blood_Group", "Unnamed: 22": "Aadhar",
        "Unnamed: 23": "Student_Status", "Unnamed: 24": "TC_Issued", "Unnamed: 25": "Admission_Flag",
        "Unnamed: 28": "BPL", "Unnamed: 29": "Physically_Disabled", "Unnamed: 31": "Sibbling",
        "Unnamed: 32": "SGC", "Unnamed: 33":"RTE", "Unnamed: 34": "KVS_Ward"
    }

    # To match the field names on the Model
    NEW_COLUMN_RENAME_MAP = {
        "Unnamed: 1": "SN", "Unnamed: 3": "uid", "Unnamed: 4": "admission_year",
        "Unnamed: 5": "admission_number", "Unnamed: 6": "student_name", "Unnamed: 8": "cls",
        "Unnamed: 10": "section", "Unnamed: 11": "fathers_name", "Unnamed: 12": "mothers_name",
        "Unnamed: 14": "gender", "Unnamed: 15": "dob", "Unnamed: 16": "admission_category",
        "Unnamed: 17": "social_category", "Unnamed: 18": "minority", "Unnamed: 19": "phone_number",
        "Unnamed: 20": "email", "Unnamed: 21": "blood_group", "Unnamed: 22": "aadhar_number",
        "Unnamed: 23": "student_status", "Unnamed: 24": "tc_issued", "Unnamed: 25": "admission_flag",
        "Unnamed: 28": "bpl", "Unnamed: 29": "physically_disabled", "Unnamed: 31": "sibbling",
        "Unnamed: 32": "single_girl_child", "Unnamed: 33":"rte", "Unnamed: 34": "kvs_ward"
    }

    data = data.iloc[7:,:35]
    data.drop(COLUMNS_TO_DROP, axis=1, inplace=True)
    data = data.rename(columns=NEW_COLUMN_RENAME_MAP)

    data['dob'] = pd.to_datetime(data['dob'], format="%d/%m/%Y")
    data.fillna("", inplace=True)

    data = data[data.student_status != 'Deactive']
    data = data[data.tc_issued != 'YES']

    data = data.iloc[:,1:]

    # Complex   sorting   algorithm...
    def sort_key(series: pd.Series):
        if series.name == 'cls':
            cls_nums = []
            for x in series.values:
                cls_nums.append(CLASSES_NUMBER_MAP[x] if x in CLASSES_NUMBER_MAP else CLASSES_NUMBER_MAP[x.split(" - ")[0]])

            return pd.Series(cls_nums)

        else:
            return series

    data.sort_values(by=['cls', 'section', 'student_name'], inplace=True, key=sort_key)

    data.index = np.arange(1, data.shape[0] + 1)
    return data