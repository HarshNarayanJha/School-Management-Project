from browser import document, bind
from student_edit_options import admission_categories, genders, social_categories, classes
from random import choice

autofill_but = document['autofill_dummy_data']
dummy_data = {
    "school_code": "1012",
    "student_name": "Link",
    "fathers_name": "Unknown",
    "mothers_name": "Unknown",
    "uid": "8888888888888888",
    "roll": str(choice(list(range(0, 50)))),
    "dob": "1986-03-21",
    "doa": "2011-06-16",
    "aadhar_number": "111111111111",
    "phone_number": "9999999999",
}

dummy_data_opt = {
    "admission_category": choice(admission_categories)[0],
    "social_category": choice(social_categories)[1],
    "cls": choice(classes)[0],
    "gender": choice(genders)[0],
}

@bind(autofill_but, 'click')
def autofill_dummy_data(ev):
    print("Autofilling...")

    for field in dummy_data:
        document[field].attrs["value"] = dummy_data[field]
        print(f"{field}: {dummy_data[field]}")

    for field in dummy_data_opt:
        document[f"{field}_{dummy_data_opt[field].lower()}"].attrs["selected"] = ""
        print(f"{field}: {dummy_data_opt[field]}")

