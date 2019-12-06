import csv
import codecs


def import_profiles_from_csv(file_upload):
    file = file_upload.read().decode('utf-8').splitlines()
    csv_data = csv.reader(file)
    for profile in csv_data:
        print(profile)
