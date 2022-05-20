from browser import document, html, bind
from exam_filter_options import is_filter, request_get, exam_types, classes, sections

filter_form_reset = document["filter_form_reset"]

if is_filter:
    document['filter_collapse'].attrs['open'] = ""
    del filter_form_reset.attrs["disabled"]
    filter_form_reset.classList.remove("disabled")

exm_per_page_select = document['exams_per_page']
exm_per_page_10 = document['exm_per_page_10']

exm_per_page = request_get.get('exams_per_page', 10)
opt = document[f"exm_per_page_{exm_per_page}"]

opt.attrs["selected"] = ""
#-----------------------------------
# Append the exam type options!
exm_none = html.OPTION("-----")
exm_none.attrs["id"] = f"exams_filter_name_None"
exm_none.attrs["value"] = ''
document['exams_filter_name'] <= exm_none

for i in exam_types:
    elem = html.OPTION(f"{i[1]}")
    elem.attrs["id"] = f"exams_filter_name_{i[0].lower()}"
    elem.attrs["value"] = i[0]
    document['exams_filter_name'] <= elem

# pre-select the correct option!
filter_name = request_get.get('exams_filter_name', None)
filter_name = filter_name.lower() if filter_name else None

name_opt = document[f"exams_filter_name_{filter_name}"]
name_opt.attrs["selected"] = ""
#------------------------------------
# Append the class options!
cls_none = html.OPTION("-----")
cls_none.attrs["id"] = f"exams_filter_cls_None"
cls_none.attrs["value"] = ''
document['exams_filter_cls'] <= cls_none

for i in classes:
    elem = html.OPTION(f"{i[1]}")
    elem.attrs["id"] = f"exams_filter_cls_{i[1].lower()}"
    elem.attrs["value"] = i[1]
    document['exams_filter_cls'] <= elem

# pre-select the correct option!
filter_cls = request_get.get('exams_filter_cls', None)
filter_cls = filter_cls.lower() if filter_cls else None

cls_opt = document[f"exams_filter_cls_{filter_cls}"]
cls_opt.attrs["selected"] = ""
#----------------------------------

# Append the sections options!
def set_up_sections(current_cls):
    sec_none = html.OPTION("-----")
    sec_none.attrs["id"] = f"exams_filter_section_None"
    sec_none.attrs["value"] = ''
    document['exams_filter_section'] <= sec_none
    if current_cls:
        sects = sections[current_cls.upper()]
    else:
        sects = max(sections.values(), key=lambda m: len(m))
    for i in sects:
        elem = html.OPTION(f"{i}")
        elem.attrs["id"] = f"exams_filter_section_{i.lower()}"
        elem.attrs["value"] = i
        document['exams_filter_section'] <= elem

    # pre-select the correct option
    filter_sec = request_get.get('exams_filter_section', None)
    filter_sec = filter_sec.lower() if filter_sec else None

    sec_opt = document[f"exams_filter_section_{filter_sec}"]
    sec_opt.attrs["selected"] = ""

set_up_sections(filter_cls)

@bind(document['exams_filter_cls'], 'change')
def on_cls_change(ev):
    document['exams_filter_section'].clear()
    set_up_sections(ev.target.value)