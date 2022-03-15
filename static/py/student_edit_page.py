from browser import document, html
from student_edit_options import (genders, admission_categories, social_categories, classes,
                                gender, admission_category, social_category, cls)

# Append the gender options!
for i in genders:
    elem = html.OPTION(f"{i[1]}")
    elem.attrs["id"] = f"gender_{i[0].lower()}"
    elem.attrs["value"] = i[0]
    document['gender'] <= elem

    # pre-select the correct option!
    if i[0] == gender: elem.attrs["selected"] = ""

# Append the admission_categories options!
for i in admission_categories:
    elem = html.OPTION(f"{i[1]}")
    elem.attrs["id"] = f"admission_category_{i[0].lower()}"
    elem.attrs["value"] = i[0]
    document['admission_category'] <= elem

    # pre-select the correct option!
    if i[0] == admission_category: elem.attrs["selected"] = ""

# Append the social_categories (a type `dict`) options!
for i in social_categories.items():
    elem = html.OPTION(f"{i[1]}")
    elem.attrs["id"] = f"social_category_{i[0].lower()}"
    elem.attrs["value"] = i[0]
    document['social_category'] <= elem

    # pre-select the correct option!
    if i[0] == social_category: elem.attrs["selected"] = ""

# Append the class options!
for i in classes:
    elem = html.OPTION(f"{i[1]}")
    elem.attrs["id"] = f"cls_{i[0].lower()}"
    elem.attrs["value"] = i[0]
    document['cls'] <= elem

    # pre-select the correct option!
    if i[0] == cls: elem.attrs["selected"] = ""