from browser import document, html, bind
from students_filter_options import is_filter, request_get, classes, sections, genders
from students_filter_options import user_is_cls_teacher

filter_form_reset = document["filter_form_reset"]

if bool(is_filter):
    document['filter_collapse'].attrs['open'] = ""
    del filter_form_reset.attrs["disabled"]
    filter_form_reset.classList.remove("disabled")

stu_per_page_select = document['students_per_page']
stu_per_page_10 = document['stu_per_page_10']

stu_per_page = request_get.get('students_per_page', 10)
opt = document[f"stu_per_page_{stu_per_page}"]

opt.attrs["selected"] = ""

if not user_is_cls_teacher:
    # Append the class options!
    cls_none = html.OPTION("-----")
    cls_none.attrs["id"] = f"students_filter_cls_None"
    cls_none.attrs["value"] = ''
    document['students_filter_cls'] <= cls_none

    for i in classes:
        elem = html.OPTION(f"{i[1]}")
        elem.attrs["id"] = f"students_filter_cls_{i[1].lower()}"
        elem.attrs["value"] = i[1]
        document['students_filter_cls'] <= elem

    # pre-select the correct option!
    filter_cls = request_get.get('students_filter_cls', None)
    filter_cls = filter_cls.lower() if filter_cls else None

    cls_opt = document[f"students_filter_cls_{filter_cls}"]
    cls_opt.attrs["selected"] = ""

# Append the sections options
    def set_up_sections(current_cls):
        global filter_sec, sec_opt

        sec_none = html.OPTION("-----")
        sec_none.attrs["id"] = f"students_filter_section_None"
        sec_none.attrs["value"] = ''
        document['students_filter_section'] <= sec_none
        if current_cls:
            sects = sections[current_cls.upper()]
        else:
            sects = max(sections.values(), key=lambda m: len(m))
        for i in sects:
            elem = html.OPTION(f"{i}")
            elem.attrs["id"] = f"students_filter_section_{i.lower()}"
            elem.attrs["value"] = i
            document['students_filter_section'] <= elem

        # pre-select the correct option
        filter_sec = request_get.get('students_filter_section', None)
        filter_sec = filter_sec.lower() if filter_sec else None

        sec_opt = document[f"students_filter_section_{filter_sec}"]
        sec_opt.attrs["selected"] = ""

    set_up_sections(filter_cls)

    @bind(document['students_filter_cls'], 'change')
    def on_cls_change(ev):
        document['students_filter_section'].clear()
        set_up_sections(ev.target.value)

# Append the gender options!
gender_none = html.OPTION("-----")
gender_none.attrs["id"] = f"students_filter_gender_None"
gender_none.attrs["value"] = ''
document['students_filter_gender'] <= gender_none

for i in genders:
    elem = html.OPTION(f"{i[1]}")
    elem.attrs["id"] = f"students_filter_gender_{i[1].lower()}"
    elem.attrs["value"] = i[1]
    document['students_filter_gender'] <= elem

# pre-select the correct option!
filter_gender = request_get.get('students_filter_gender', None)
filter_gender = filter_gender.lower() if filter_gender else None

gender_opt = document[f"students_filter_gender_{filter_gender}"]
gender_opt.attrs["selected"] = ""
    