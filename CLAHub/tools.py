from people import models
from CLAHub.base_settings import BASE_DIR

import csv
import os


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
        return 'missing_data'
    else:
        villages = models.Person.villages
        for profile in data:
            # csv file has the value, not the key to villages. Need to loop though and find the
            # key that matches the value
            village = ([item[0] for item in villages if item[1] == profile[columns['village']]][0])
            new_profile = models.Person(
                village=village,
                name=profile[columns['name']],
                # need to insert CLAHubs install dir before the filename
                picture=os.path.join(BASE_DIR, 'uploads\import', profile[columns['picture']]),
                last_modified_by='Batch importer'
            )
            new_profile.save()
        return len(data)



def data_missing(csv_data):
    for profile in csv_data:
        for column in csv_data:
            if '' in column:
                return True