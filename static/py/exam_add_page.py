from browser import document, html, bind
from exam_add_options import classes, exam_names
from exam_add_options import user_is_class_teacher, user_class_teacher_cls, user_class_teacher_section, user_school_code

# Append the class options!
for i, name in exam_names:
    elem = html.OPTION(f"{name}")
    elem.attrs["id"] = f"exam_{i}"
    elem.attrs["value"] = i
    document['exam_name'] <= elem

if not user_is_class_teacher:
    # Append the class options!
    for i in classes[user_school_code]:
        elem = html.OPTION(f"{i}")
        elem.attrs["id"] = f"cls_{i.lower()}"
        elem.attrs["value"] = i
        document['cls'] <= elem

    # Append the sections options!
    def set_up_sections(current_cls):
        sects = classes[user_school_code][current_cls.upper()]
        for i in sects:
            elem = html.OPTION(f"{i}")
            elem.attrs["id"] = f"cls_section_{i.lower()}"
            elem.attrs["value"] = i
            document['section'] <= elem

    set_up_sections(list(classes[user_school_code].keys())[0])

    @bind(document['cls'], 'change')
    def on_cls_change(ev):
        document['section'].clear()
        set_up_sections(ev.target.value)
else:
    elem = html.OPTION(f"{user_class_teacher_cls}")
    elem.attrs["id"] = f"cls_{user_class_teacher_cls.lower()}"
    elem.attrs["value"] = user_class_teacher_cls
    document['cls'] <= elem

    elem = html.OPTION(f"{user_class_teacher_section}")
    elem.attrs["id"] = f"cls_section_{user_class_teacher_section.lower()}"
    elem.attrs["value"] = user_class_teacher_section
    document['section'] <= elem