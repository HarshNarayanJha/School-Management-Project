from browser import document, html
from student_edit_options import genders, admission_categories, social_categories, classes

# Append the gender options!
for i in genders:
    elem = html.OPTION(f"{i[1]}")
    elem.attrs["id"] = f"gender_{i[1].lower()}"
    elem.attrs["value"] = i[1]
    document['gender'] <= elem

# Append the admission_categories options!
for i in admission_categories:
    elem = html.OPTION(f"{i[1]}")
    elem.attrs["id"] = f"admission_category_{i[1].lower()}"
    elem.attrs["value"] = i[1]
    document['admission_category'] <= elem

# Append the social_categories options!
for i in social_categories:
    elem = html.OPTION(f"{i[1]}")
    elem.attrs["id"] = f"social_category_{i[1].lower()}"
    elem.attrs["value"] = i[1]
    document['social_category'] <= elem

# Append the class options!
for i in classes:
    elem = html.OPTION(f"{i[1]}")
    elem.attrs["id"] = f"cls_{i[1].lower()}"
    elem.attrs["value"] = i[1]
    document['cls'] <= elem