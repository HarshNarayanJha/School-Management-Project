from browser import document, html, bind
from exam_add_options import classes, exam_names, sections

# Append the class options!
for i in exam_names:
    elem = html.OPTION(f"{i[1]}")
    elem.attrs["id"] = f"exam_{i[0].lower()}"
    elem.attrs["value"] = i[0]
    document['exam_name'] <= elem

# Append the class options!
for i in classes:
    elem = html.OPTION(f"{i[1]}")
    elem.attrs["id"] = f"cls_{i[0].lower()}"
    elem.attrs["value"] = i[0]
    document['cls'] <= elem

# Append the sections options!
def set_up_sections(current_cls):
    sects = sections[current_cls.upper()]
    for i in sects:
        elem = html.OPTION(f"{i}")
        elem.attrs["id"] = f"cls_section_{i.lower()}"
        elem.attrs["value"] = i
        document['section'] <= elem

set_up_sections(classes[0][1])

@bind(document['cls'], 'change')
def on_cls_change(ev):
    document['section'].clear()
    set_up_sections(ev.target.value)