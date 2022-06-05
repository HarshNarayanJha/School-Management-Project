from browser import document, bind
from student_add_options import admission_categories, genders, social_categories, classes
from random import choice

autofill_but = document['autofill_dummy_data']

dummy_data = {}
dummy_data_opt = {}

def generate_dummy_data():
    global dummy_data, dummy_data_opt

    dummy_data = {
        "school_code": "1012",
        "student_name": choice(["Link", "Zelda"]),
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
        "social_category": choice(social_categories)[0],
        "cls": choice(list(classes.keys())),
        "gender": choice(genders)[0],
    }
    dummy_data_opt['section'] = choice(classes[dummy_data_opt['cls']])

generate_dummy_data()

@bind(autofill_but, 'click')
def autofill_dummy_data(ev):
    print("Autofilling...")

    for field in dummy_data:
        print(f"{field}: {dummy_data[field]}")
        document[field].attrs["value"] = dummy_data[field]

    for field in dummy_data_opt:
        print(f"{field}: {dummy_data_opt[field]}")
        document[f"{field}_{dummy_data_opt[field].lower()}"].attrs["selected"] = ""

    generate_dummy_data()

