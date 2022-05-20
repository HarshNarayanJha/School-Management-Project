from browser import document, bind
from exam_edit_options import subjects
from random import randint

autofill_but = document['autofill_dummy_data']
dummy_data = {}

def generate_dummy_data():
    global dummy_data
    for sub, sub_display in subjects:
        dummy_data[f"{sub}_mark_ob"] = randint(0, 40)
        dummy_data[f"{sub}_mark_mx"] = 40

generate_dummy_data()

# print(dummy_data)

@bind(autofill_but, 'click')
def autofill_dummy_data(ev):
    print("Autofilling exam marks...")

    for input in document.select(".form-control"):
        for field in dummy_data:
            if input.attrs['id'] == field and not 'readonly' in input.attrs:
                input.attrs["value"] = dummy_data[field]

        generate_dummy_data()