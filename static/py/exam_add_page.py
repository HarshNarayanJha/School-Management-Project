from browser import document, html
from exam_add_options import classes, exam_names

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