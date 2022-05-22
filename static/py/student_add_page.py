from browser import document, html, bind
from student_add_options import genders, admission_categories, social_categories, classes

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
    elem.attrs["id"] = f"social_category_{i[0].lower()}"
    elem.attrs["value"] = i[0]
    document['social_category'] <= elem

# Append the class options!
for i in classes:
    elem = html.OPTION(f"{i}")
    elem.attrs["id"] = f"cls_{i.lower()}"
    elem.attrs["value"] = i
    document['cls'] <= elem

def set_up_sections(current_cls):
    sects = classes[current_cls.upper()]
    for i in sects:
        elem = html.OPTION(f"{i}")
        elem.attrs["id"] = f"section_{i.lower()}"
        elem.attrs["value"] = i
        document['section'] <= elem

set_up_sections(document['cls'].value)

@bind(document['cls'], 'change')
def on_cls_change(ev):
    document['section'].clear()
    set_up_sections(ev.target.value)