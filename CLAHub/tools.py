from people import models
from CLAHub.base_settings import BASE_DIR
from PIL import Image, ExifTags, ImageOps
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile

import csv
import os
import sys


def import_profiles_from_csv(file_upload):
    file = file_upload.read().decode('utf-8').splitlines()
    csv_data = csv.reader(file)
    data = [profile for profile in csv_data]
    columns = {
        'picture': 0,
        'village': 1,
        'name': 2
    }

    check = check_csv(data, columns)
    if check == 'missing_data_error':
        return check
    elif check == 'village_spelling_error':
        return check
    elif check.startswith('missing_file_error'):
        return check

    else:
        for profile in data:
            picture = os.path.join(BASE_DIR, 'uploads\import', profile[columns['picture']])
            villages = models.Person.villages
            village = ([item[0] for item in villages if item[1] == profile[columns['village']]][0])
            new_profile = models.Person(
                village=village,
                name=profile[columns['name']],
                # need to insert CLAHubs install dir before the filename
                picture=picture,
                last_modified_by='Batch importer'
            )
            new_profile.save()


            # todo clean up imports folder
            # todo write instructions into template
            # todo add other if conditions: if encoding error
            # todo write tests
        return len(data)


def check_csv(csv_data, columns):
    for profile in csv_data:
        for column in csv_data:
            if '' in column:
                return 'missing_data_error'
        # csv file has the value, not the key to villages. Need to loop though and find the
        # key that matches the value
        try:
            villages = models.Person.villages
            village = ([item[0] for item in villages if item[1] == profile[columns['village']]][0])
        except IndexError:
            return 'village_spelling_error'

        pic_exists = os.path.exists(os.path.join(BASE_DIR, 'uploads\import', profile[columns['picture']]))
        if not pic_exists:
            return 'missing_file_error%s' % (profile[columns['picture']],)

    return 'ok'

def compress_picture(picture, compressed_size):
    im = Image.open(picture)
    # get correct orientation
    im = ImageOps.exif_transpose(im)

    output = BytesIO()
    im.thumbnail(compressed_size)
    im.save(output, format='JPEG', quality=90)
    output.seek(0)
    picture = InMemoryUploadedFile(output, 'PictureField',
                                        "%s.jpg" % picture.name.split('.')[0],
                                        'image/jpeg',
                                        sys.getsizeof(output), None)
    return picture