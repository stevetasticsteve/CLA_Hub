from people import models

import csv


def import_profiles_from_csv(file_upload):
    file = file_upload.read().decode('utf-8').splitlines()
    csv_data = csv.reader(file)
    data = [profile for profile in csv_data]
    columns = {
        'picture': 0,
        'village': 1,
        'name': 2
    }
    if data_missing(data):
        return False
    else:
        for profile in data:
            new_profile = models.Person(
                village=columns['village'],
                name=columns['name'],
                picture=columns['picture'],
                last_modified_by='Batch importer'
            )
            new_profile.save()
            return True



def data_missing(csv_data):
    for profile in csv_data:
        for column in csv_data:
            if '' in column:
                return True