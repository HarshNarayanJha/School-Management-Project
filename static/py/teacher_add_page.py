from browser import document, html, bind
from teacher_add_options import schools, subjects, classes

# Append the subjects options!
for i in subjects:
    elem = html.OPTION(f"{subjects[i]}")
    elem.attrs["id"] = f"subject_{i}"
    elem.attrs["value"] = i
    document['subject'] <= elem

# Append the School options
for code, name in schools:
    elem = html.OPTION(f"{name}")
    elem.attrs["id"] = f"school_{code}"
    elem.attrs["value"] = f"{code}"
    document['school'] <= elem

@bind(document['school'], 'change')
def on_school_change(ev):
    document['class_teacher_of'].clear()
    generate_classes(ev.target.value)

def generate_classes(school):

    cls_none = html.OPTION("-----")
    cls_none.attrs['id'] = f"cls_None"
    cls_none.attrs['value'] = ''
    document['class_teacher_of'] <= cls_none

    # Append the class options!
    for i in classes[school]:
        for j in classes[school][i]:
            elem = html.OPTION(f"{i} - {j}")
            elem.attrs["id"] = f"cls_{i.lower()}-{j.lower()}"
            elem.attrs["value"] = f"{i}-{j}"
            document['class_teacher_of'] <= elem

generate_classes(document['school'].value)