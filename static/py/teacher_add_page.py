from browser import document, html, bind
from teacher_add_options import subjects, classes

# Append the subjects options!
for i in subjects:
    elem = html.OPTION(f"{i[1]}")
    elem.attrs["id"] = f"subject_{i[0].lower()}"
    elem.attrs["value"] = i[0]
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