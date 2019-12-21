from people import models
from CLAHub.base_settings import BASE_DIR
from PIL import Image, ImageOps
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile

import csv
import os
import sys
import logging

logger = logging.getLogger('debug')


def import_profiles_from_csv(file_upload):
    logger.info('import_profiles_from_csv initiated')
    if type(file_upload) == str:
        file = open(file_upload)
    else:
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
        logger.error('No data imported, data seems to be blank or missing')
        return check
    elif check == 'village_spelling_error':
        logger.error('No data imported, village mentioned is not an option')
        return check
    elif check.startswith('missing_file_error'):
        logger.error('No data imported, %s not found in import folder'
                     % check.lstrip('missing_file_error'))
        return check

    else:
        logger.info('All data cleared for import')
        for i, profile in enumerate(data, 1):
            picture = os.path.join(BASE_DIR, 'uploads', 'import', profile[columns['picture']])
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
            logger.info('Saved profile %s of %s' % (i, len(data)))
            # todo clean up imports folder
            # todo write instructions into template
            # todo add other if conditions: if encoding error
            # todo write tests
        logger.info('import_profiles_from_csv_finished %s profiles created\n\n' % len(data))
        return len(data)


def check_csv(csv_data, columns):
    logger.info('Checking integrity of .csv file')
    logger.debug('%s rows of data in .csv' % len(csv_data))
    for i, profile in enumerate(csv_data, 1):
        logger.debug('checking row %s' % i)
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
        pic_path = os.path.join(BASE_DIR, 'uploads', 'import', profile[columns['picture']])
        pic_exists = os.path.exists(pic_path)
        if not pic_exists:
            return 'missing_file_error%s' % profile[columns['picture']]
        logger.debug('Filename: %s\n' % pic_path)
        logger.debug('Name: %s\n' % profile[columns['name']])
        logger.debug('village: %s\n' % profile[columns['village']])
        logger.debug('Row %s ok\n' % i)

    return 'ok'


def compress_picture(picture, compressed_size):
    # If the image has already been processed don't compress again.
    # This avoids adding duplicate images to the file system
    if check_picture_already_imported(picture):
        return None
    # todo It's possible this could misbehave if a file has the same name and the user intends
    # to upload it. An uncompressed image would go through. If it went into a different upload folder
    # it wouldn't clash with the name previously.

    try:
        im = Image.open(picture)
    except IOError:
        logger.error('An invalid image was submitted')
        return None
    logger.info('Compressing picture, target size %sx%s' % (compressed_size[0], compressed_size[1]))
    # get correct orientation
    # PIL has an error, skip operation if error arises
    try:
        im = ImageOps.exif_transpose(im)
    except TypeError:
        logging.error('PIL error - image not rotated')
        pass

    output = BytesIO()
    im.thumbnail(compressed_size)
    im.save(output, format='JPEG', quality=90)
    output.seek(0)
    picture = InMemoryUploadedFile(output, 'PictureField',
                                        "%s.jpg" % picture.name.split('.')[0],
                                        'image/jpeg',
                                        sys.getsizeof(output), None)
    size = sys.getsizeof(output)/1000000
    logger.info('Picture compressed to %s Mb\n' % size)
    return picture


def check_picture_already_imported(picture):
    # look in CE and people uploads for files user has already uploaded
    imported_files = list_all_files('uploads/CultureEventFiles') \
                     + list_all_files('uploads/people/profile_pictures')
    if os.path.basename(str(picture)) in imported_files:
        return True


def list_all_files(path):
    # create a list of all file names recursively in a directory
    list_of_file = os.listdir(path)
    all_files = list()
    for entry in list_of_file:
        full_path = os.path.join(path, entry)
        if os.path.isdir(full_path):
            all_files = all_files + list_all_files(full_path)
        else:
            all_files.append(full_path)
    all_files = [os.path.basename(file) for file in all_files]

    return all_files
