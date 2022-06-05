from browser import document, html, bind
from teacher_add_options import subjects, classes

# Append the subjects options!
for i in subjects:
    elem = html.OPTION(f"{subjects[i]}")
    elem.attrs["id"] = f"subject_{i}"
    elem.attrs["value"] = i
    document['subject'] <= elem

cls_none = html.OPTION("-----")
cls_none.attrs['id'] = f"cls_None"
cls_none.attrs['value'] = ''
document['class_teacher_of'] <= cls_none

# Append the class options!
for i in classes:
    for j in classes[i]:
        elem = html.OPTION(f"{i} - {j}")
        elem.attrs["id"] = f"cls_{i.lower()}-{j.lower()}"
        elem.attrs["value"] = f"{i}-{j}"
        document['class_teacher_of'] <= elem