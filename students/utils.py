"""
Some utility functions with multiple usages
"""

import datetime
from students.models import Student


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

def get_birthdays():
        today = datetime.date.today()
        birthdays: list[Student] = Student.objects.filter(dob__day=today.day, dob__month=today.month)
        return birthdays